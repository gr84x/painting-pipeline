"""
stroke_engine.py — Natural painting primitives.

Architecture
============
  PaintCanvas   — cairo surface + numpy wetness map + linen texture
  BrushTip      — tip shape mask (round, filbert, flat)
  Stroke        — tapered bezier path with pigment color
  mix_paint()   — subtractive (pigment) color mixing in sqrt-space
  Painter       — high-level layered painting API

Workflow
========
  p = Painter(800, 1000)
  p.tone_ground(TERRE_VERTE)
  p.underpainting(reference, stroke_size=55)
  p.block_in(reference,      stroke_size=38)
  p.build_form(reference,    stroke_size=16)
  p.place_lights(reference,  stroke_size=6)
  p.glaze(WARM_AMBER, opacity=0.10)
  p.save("out.png")
"""

import math, random, colorsys
from typing import List, Tuple, Optional, Union

import numpy as np
import cairo
from PIL import Image, ImageFilter
from scipy import ndimage
from noise import pnoise2

Color = Tuple[float, float, float]

# ─────────────────────────────────────────────────────────────────────────────
# Color mixing — subtractive (pigment) model
# ─────────────────────────────────────────────────────────────────────────────

def mix_paint(c1: Color, c2: Color, t: float) -> Color:
    """
    Subtractive pigment mixing via sqrt-space blend.
    Unlike linear RGB averaging (which gives muddy midpoints),
    this approximates how physical paint pigments combine.
    """
    t = max(0.0, min(1.0, t))
    return tuple(math.sqrt((1 - t) * c1[i] ** 2 + t * c2[i] ** 2)
                 for i in range(3))


def jitter(c: Color, amount: float = 0.035, rng=None) -> Color:
    """Organic per-stroke color variation."""
    r = rng or random
    return tuple(max(0.0, min(1.0, c[i] + r.uniform(-amount, amount)))
                 for i in range(3))


def complement(c: Color) -> Color:
    """
    Return the chromatic complement of a colour by rotating hue 180° in HSV.

    Seurat's divisionism relies on simultaneous contrast: placing a colour
    beside its complement makes both appear more vivid.  This gives the
    luminous shimmer that physical pigment mixing cannot achieve.

    Unlike a naive (1-r, 1-g, 1-b) inversion this preserves saturation and
    value, so the complement dot is the same 'brightness' as the primary.
    """
    h, s, v = colorsys.rgb_to_hsv(*c)
    h_comp = (h + 0.5) % 1.0
    return colorsys.hsv_to_rgb(h_comp, s, v)


def temp_shift(c: Color, warmth: float) -> Color:
    """
    Shift a colour toward warm (positive) or cool (negative).
    Warm: boost R, damp B.  Cool: boost B, damp R.
    Models the painter's warm-light / cool-shadow convention.
    """
    r, g, b = c
    if warmth > 0:
        return (min(1.0, r + warmth * 0.12),
                g,
                max(0.0, b - warmth * 0.08))
    else:
        w = -warmth
        return (max(0.0, r - w * 0.08),
                g,
                min(1.0, b + w * 0.12))


# ─────────────────────────────────────────────────────────────────────────────
# Canvas texture — linen grain via layered Perlin noise
# ─────────────────────────────────────────────────────────────────────────────

def make_linen_texture(w: int, h: int) -> np.ndarray:
    """
    Returns a (H, W) float32 array in [0.72, 1.0] representing linen weave.
    Two scales: coarse warp/weft threads + fine surface grain.
    """
    tex = np.zeros((h, w), dtype=np.float32)
    inv_w, inv_h = 1.0 / w, 1.0 / h
    for y in range(h):
        for x in range(w):
            # Coarse thread weave
            coarse = pnoise2(x * inv_w * 28, y * inv_h * 28,
                             octaves=2, persistence=0.5)
            # Fine surface grain
            fine = pnoise2(x * inv_w * 120, y * inv_h * 120,
                           octaves=3, persistence=0.4)
            tex[y, x] = coarse * 0.65 + fine * 0.35

    # Normalise to [0.72, 1.0]
    lo, hi = tex.min(), tex.max()
    tex = (tex - lo) / (hi - lo + 1e-8)
    return (0.72 + 0.28 * tex).astype(np.float32)


# ─────────────────────────────────────────────────────────────────────────────
# BrushTip — normalised alpha mask for stamp-style edge texture
# ─────────────────────────────────────────────────────────────────────────────

class BrushTip:
    ROUND   = "round"
    FILBERT = "filbert"     # rounded-corner flat — most versatile
    FLAT    = "flat"

    def __init__(self, kind: str = FILBERT, bristle_noise: float = 0.06):
        self.kind = kind
        self.bristle_noise = bristle_noise

    def edge_softness(self, t_along: float) -> float:
        """
        Edge opacity modifier as a function of position along stroke (0-1).
        Tapers both tips; filbert and round taper more than flat.
        """
        if self.kind == BrushTip.FLAT:
            # Flat brush: sharp sides, only tiny taper at very ends
            return math.sin(min(t_along, 1 - t_along) * math.pi / 0.15) \
                   if t_along < 0.15 or t_along > 0.85 else 1.0
        else:
            # Round / filbert: smooth bell
            return math.sin(t_along * math.pi)


# ─────────────────────────────────────────────────────────────────────────────
# Stroke geometry helpers
# ─────────────────────────────────────────────────────────────────────────────

def catmull_rom(pts: List[Tuple], steps: int = 6) -> List[Tuple]:
    """Smooth a point list with Catmull-Rom interpolation."""
    if len(pts) < 2:
        return pts
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[min(i + 2, n - 1)]
        for s in range(steps):
            t = s / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) +
                       (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) +
                       (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


def build_stroke_outline(pts: List[Tuple], widths: List[float]
                         ) -> Tuple[List[Tuple], List[Tuple]]:
    """
    Offset a centre-line into left / right boundary polygons.
    Returns (left_side, right_side) each as a list of (x, y).
    """
    left, right = [], []
    n = len(pts)
    for i in range(n):
        if i == 0:
            dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        elif i == n - 1:
            dx, dy = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
        else:
            dx, dy = pts[i+1][0] - pts[i-1][0], pts[i+1][1] - pts[i-1][1]

        mag = math.hypot(dx, dy) or 1e-6
        px, py = -dy / mag, dx / mag       # perpendicular (left normal)
        hw = widths[i] / 2.0
        left.append( (pts[i][0] + px * hw, pts[i][1] + py * hw))
        right.append((pts[i][0] - px * hw, pts[i][1] - py * hw))
    return left, right


def width_profile(n: int, tip_frac: float = 0.18) -> List[float]:
    """Bell-shaped width envelope: narrow at both tips, full in middle."""
    out = []
    for i in range(n):
        t = i / max(n - 1, 1)
        if t < tip_frac:
            v = t / tip_frac
        elif t > 1 - tip_frac:
            v = (1 - t) / tip_frac
        else:
            v = 1.0
        out.append(max(0.05, v))
    return out


def stroke_path(origin: Tuple, angle: float, length: float,
                curve: float = 0.0, n: int = 7) -> List[Tuple]:
    """
    Generate a gently curved centre-line.
    curve: radians of total arc over the stroke length.
    """
    pts = [origin]
    x, y = origin
    a = angle
    step = length / n
    da = curve / n
    for _ in range(n):
        a += da
        x += math.cos(a) * step
        y += math.sin(a) * step
        pts.append((x, y))
    return pts


# ─────────────────────────────────────────────────────────────────────────────
# PaintCanvas
# ─────────────────────────────────────────────────────────────────────────────

class PaintCanvas:
    """
    The painting surface.

    Cairo ImageSurface is the master pixel store.
    A numpy wetness map tracks which regions have fresh paint
    so wet-on-wet blending can be simulated.
    """

    def __init__(self, width: int, height: int):
        self.w, self.h = width, height
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx     = cairo.Context(self.surface)
        self.ctx.set_antialias(cairo.ANTIALIAS_BEST)

        # Wetness: 1.0 = fresh paint, decays between layers
        self.wetness = np.zeros((height, width), dtype=np.float32)

        # Linen texture (built once)
        print("  Weaving linen texture…")
        self.texture = make_linen_texture(width, height)

    # ── Ground ────────────────────────────────────────────────────────────────

    def tone(self, color: Color, texture_strength: float = 0.07):
        """
        Prime the canvas with a toned ground.
        The texture modulates the ground colour so the linen weave shows through.
        """
        r, g, b = color
        # Build BGRA array with texture variation
        tex = self.texture
        arr = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        arr[:, :, 0] = np.clip((b * (1 - texture_strength + texture_strength * tex)) * 255, 0, 255)
        arr[:, :, 1] = np.clip((g * (1 - texture_strength + texture_strength * tex)) * 255, 0, 255)
        arr[:, :, 2] = np.clip((r * (1 - texture_strength + texture_strength * tex)) * 255, 0, 255)
        arr[:, :, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(arr.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.ctx.set_source_surface(tmp, 0, 0)
        self.ctx.paint()
        self.wetness[:] = 0.0

    # ── Stroke application ────────────────────────────────────────────────────

    def _sample_color(self, x: int, y: int) -> Color:
        """Read canvas colour at pixel (x, y) — fast single-pixel read."""
        x = max(0, min(self.w - 1, x))
        y = max(0, min(self.h - 1, y))
        buf  = self.surface.get_data()
        off  = (y * self.w + x) * 4
        b, g, r, _ = buf[off], buf[off+1], buf[off+2], buf[off+3]
        return r / 255.0, g / 255.0, b / 255.0

    def apply_stroke(self,
                     pts:        List[Tuple],
                     widths:     List[float],
                     color:      Color,
                     tip:        BrushTip,
                     opacity:    float = 0.82,
                     wet_blend:  float = 0.22,
                     jitter_amt: float = 0.03,
                     rng=None,
                     region_mask: Optional[np.ndarray] = None):
        """
        Place one brush stroke on the canvas.

        The stroke is rendered as a series of tapered polygon segments.
        Wet-on-wet: at the stroke mid-point, the incoming colour is mixed
        with the canvas colour proportionally to local wetness.
        """
        if len(pts) < 2:
            return

        # Smooth centre-line (recompute widths to match new point count)
        pts = catmull_rom(pts, steps=5)
        # Widths were for the original pts; resample to match smoothed length
        orig_n = len(widths)
        new_n  = len(pts)
        if new_n != orig_n:
            widths = [widths[int(i * (orig_n - 1) / max(new_n - 1, 1))]
                      for i in range(new_n)]

        # ── Wet blending ─────────────────────────────────────────────────────
        mid   = pts[len(pts) // 2]
        mx, my = int(mid[0]), int(mid[1])
        canvas_col = self._sample_color(mx, my)
        wet_at = float(self.wetness[max(0, min(self.h-1, my)),
                                    max(0, min(self.w-1, mx))])
        blend_t = wet_blend * wet_at
        paint_col = mix_paint(color, canvas_col, blend_t)
        paint_col = jitter(paint_col, jitter_amt, rng)

        r, g, b = paint_col

        # ── Build outline ─────────────────────────────────────────────────────
        wp = width_profile(len(pts))
        scaled_widths = [wp[i] * widths[i] for i in range(len(pts))]
        left, right  = build_stroke_outline(pts, scaled_widths)

        # ── Draw tapered segments ─────────────────────────────────────────────
        n_seg = len(pts) - 1
        for i in range(n_seg):
            # Region mask: skip segment if its centre pixel is outside the
            # allowed region.  This is the hard guard against brush strokes
            # bleeding across the figure/background boundary.
            if region_mask is not None:
                seg_cx = int((pts[i][0] + pts[i+1][0]) * 0.5)
                seg_cy = int((pts[i][1] + pts[i+1][1]) * 0.5)
                seg_cx = max(0, min(self.w - 1, seg_cx))
                seg_cy = max(0, min(self.h - 1, seg_cy))
                if region_mask[seg_cy, seg_cx] < 0.5:
                    continue

            t_mid = (i + 0.5) / max(n_seg, 1)
            seg_alpha = opacity * tip.edge_softness(t_mid)
            seg_alpha = max(0.05, seg_alpha)

            i0, i1 = min(i, len(left)-1), min(i+1, len(left)-1)
            quad = [left[i0], left[i1], right[i1], right[i0]]

            self.ctx.move_to(*quad[0])
            for p in quad[1:]:
                self.ctx.line_to(*p)
            self.ctx.close_path()
            self.ctx.set_source_rgba(r, g, b, seg_alpha)
            self.ctx.fill()

        # ── Update wetness in bbox ────────────────────────────────────────────
        all_x = [int(p[0]) for p in left + right]
        all_y = [int(p[1]) for p in left + right]
        x0 = max(0,       min(all_x))
        x1 = min(self.w,  max(all_x) + 1)
        y0 = max(0,       min(all_y))
        y1 = min(self.h,  max(all_y) + 1)
        self.wetness[y0:y1, x0:x1] = np.minimum(
            1.0, self.wetness[y0:y1, x0:x1] + 0.35)

    # ── Post-processing ───────────────────────────────────────────────────────

    def dry(self, amount: float = 0.55):
        """Simulate paint drying between layers — reduces wetness."""
        self.wetness *= (1.0 - amount)

    def glaze(self, color: Color, opacity: float = 0.10):
        """Transparent colour wash over entire canvas (final warmth / tone)."""
        self.ctx.rectangle(0, 0, self.w, self.h)
        self.ctx.set_source_rgba(*color, opacity)
        self.ctx.fill()

    def vignette(self, strength: float = 0.55):
        grad = cairo.RadialGradient(
            self.w/2, self.h/2, min(self.w, self.h) * 0.30,
            self.w/2, self.h/2, max(self.w, self.h) * 0.78)
        grad.add_color_stop_rgba(0, 0, 0, 0, 0)
        grad.add_color_stop_rgba(1, 0, 0, 0, strength)
        self.ctx.rectangle(0, 0, self.w, self.h)
        self.ctx.set_source(grad)
        self.ctx.fill()

    def crackle(self, density: float = 0.028):
        """
        Simulate aged varnish crackle — a fine dark network across the surface.
        Adds enormous period authenticity.
        """
        buf = np.frombuffer(self.surface.get_data(), dtype=np.uint8).reshape(
            self.h, self.w, 4).copy()

        for y in range(0, self.h, 3):
            for x in range(0, self.w, 3):
                n = abs(pnoise2(x / 12.0, y / 12.0, octaves=5))
                if n > 0.44:
                    fade = min(1.0, (n - 0.44) / 0.06) * density
                    buf[y, x, :3] = np.clip(
                        buf[y, x, :3].astype(float) * (1 - fade), 0, 255).astype(np.uint8)

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.ctx.set_source_surface(tmp, 0, 0)
        self.ctx.paint()

    # ── Output ────────────────────────────────────────────────────────────────

    def to_pil(self) -> Image.Image:
        buf  = self.surface.get_data()
        arr  = np.frombuffer(buf, dtype=np.uint8).reshape(self.h, self.w, 4).copy()
        rgb  = arr[:, :, [2, 1, 0]]          # BGRA → RGB
        return Image.fromarray(rgb, "RGB")

    def save(self, path: str):
        self.to_pil().save(path)
        print(f"  Saved: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Flow field — stroke directions from image gradient
# ─────────────────────────────────────────────────────────────────────────────

def flow_field(img_arr: np.ndarray) -> np.ndarray:
    """
    Compute stroke direction angles (radians) from image gradient.
    Strokes run PERPENDICULAR to the gradient so they follow colour contours,
    which is how painters naturally work along the form.
    """
    if img_arr.ndim == 3:
        gray = (0.299 * img_arr[:,:,0] +
                0.587 * img_arr[:,:,1] +
                0.114 * img_arr[:,:,2]).astype(np.float32)
    else:
        gray = img_arr.astype(np.float32)

    # Sobel gradient
    gx = ndimage.sobel(gray, axis=1)
    gy = ndimage.sobel(gray, axis=0)

    # Perpendicular to gradient = follow colour contour
    angles = np.arctan2(gx, -gy)

    # Smooth the field so strokes don't jitter randomly
    angles = ndimage.gaussian_filter(angles, sigma=4.0)
    return angles


# ─────────────────────────────────────────────────────────────────────────────
# Region mask helpers
# ─────────────────────────────────────────────────────────────────────────────

def ellipse_mask(w: int, h: int,
                 cx: float, cy: float,
                 rx: float, ry: float,
                 feather: float = 0.25) -> np.ndarray:
    """
    Soft elliptical mask.  Values are 1 inside, fall to 0 at the feathered edge.
    cx, cy, rx, ry are in pixels.  feather: fraction of radius for soft edge.
    """
    ys, xs = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xs - cx) / (rx + 1e-6))**2 + ((ys - cy) / (ry + 1e-6))**2)
    inner = 1.0 - feather
    mask  = np.clip((1.0 - d) / feather, 0.0, 1.0)
    mask  = np.where(d < inner, 1.0, mask)
    return mask.astype(np.float32)


def spherical_flow(w: int, h: int,
                   cx: float, cy: float,
                   rx: float, ry: float) -> np.ndarray:
    """
    Flow field whose strokes follow the surface of a sphere centred at (cx, cy).
    Strokes are tangent to latitude circles — they curve around the face
    rather than following colour edges.

    This is what painters do: on a face they work 'around' the form,
    not in arbitrary directions dictated by the flat image.
    """
    ys, xs = np.mgrid[0:h, 0:w]
    # Normalised vector from centre
    dx = (xs - cx) / (rx + 1e-6)
    dy = (ys - cy) / (ry + 1e-6)
    # Tangent = perpendicular to radial = rotate 90°
    # At top of sphere: strokes go horizontal.
    # At sides: strokes go vertical.
    angles = np.arctan2(dx, -dy)          # tangent direction
    # Smooth so there are no discontinuities
    angles = ndimage.gaussian_filter(angles, sigma=6.0)
    return angles.astype(np.float32)


# ─────────────────────────────────────────────────────────────────────────────
# Painter — high-level layered API
# ─────────────────────────────────────────────────────────────────────────────

class Painter:
    """
    Thinks in painting layers, not geometric shapes.

    Each method corresponds to a real stage in oil painting practice.
    """

    def __init__(self, width: int, height: int):
        self.canvas = PaintCanvas(width, height)
        self.rng    = np.random.default_rng(7)
        self._rng_py = random.Random(7)
        self.w, self.h = width, height
        # Figure mask: (H, W) float32 — 1.0=figure, 0.0=background.
        # Set via set_figure_mask() before painting.
        self._figure_mask: Optional[np.ndarray] = None
        # Normal map: (H, W, 3) float32 in [-1, 1], world-space normals.
        # Set via set_normal_map() before toon passes.
        self._normal_map: Optional[np.ndarray] = None

    # ── Mask management ───────────────────────────────────────────────────────

    def set_figure_mask(self, mask_source):
        """
        Load the figure silhouette mask.

        mask_source — path to a grayscale PNG (white=figure, black=background),
                      a PIL Image, or a (H, W) numpy array.

        Once set, ALL stroke passes automatically constrain themselves to the
        figure region.  Background pixels are sealed first with
        seal_background() before any figure strokes are placed.
        """
        if isinstance(mask_source, str):
            from PIL import Image as _PILImage
            img = _PILImage.open(mask_source).convert("L").resize(
                (self.w, self.h), _PILImage.NEAREST)
            arr = np.array(img, dtype=np.float32) / 255.0
        elif isinstance(mask_source, np.ndarray):
            arr = mask_source.astype(np.float32)
            if arr.max() > 1.0:
                arr /= 255.0
        else:
            arr = np.array(mask_source.convert("L"), dtype=np.float32) / 255.0
        # Hard threshold: 1 = figure, 0 = background
        self._figure_mask = (arr > 0.5).astype(np.float32)

    def set_normal_map(self, source):
        """Load world-normal map (H, W, 3) float32 in [-1, 1] range.

        source — path to the normal PNG written by blender_bridge (encoded as
                 (N+1)/2 → RGB), a PIL Image, or a (H, W, 3) numpy array.

        Decodes the PNG encoding: pixel = (N + 1) / 2  →  N = pixel * 2 - 1.
        Result is stored as self._normal_map with shape (H, W, 3), dtype float32,
        values in [-1, 1], resized to match the painter dimensions.
        """
        if isinstance(source, str):
            from PIL import Image as _PILImage
            img = _PILImage.open(source).convert("RGB").resize(
                (self.w, self.h), _PILImage.BILINEAR)
            arr = np.array(img, dtype=np.float32) / 255.0
        elif isinstance(source, np.ndarray):
            arr = source.astype(np.float32)
            if arr.max() > 1.0:
                arr = arr / 255.0
        else:
            # PIL Image
            img = source.convert("RGB").resize((self.w, self.h))
            arr = np.array(img, dtype=np.float32) / 255.0

        # Decode from [0, 1] encoding to [-1, 1] world normals
        self._normal_map = arr * 2.0 - 1.0

    def toon_contour_mask(self, light_dir, shadow_thresh=0.10, contour_thresh=0.25):
        """Compute toon shading masks from the loaded normal map.

        Parameters
        ----------
        light_dir       : (3,) array-like — world-space light direction (normalised)
        shadow_thresh   : dot(N, L) threshold below which a pixel is in shadow
        contour_thresh  : |dot(N, camera)| threshold for silhouette/contour pixels

        Returns
        -------
        shadow_mask   : (H, W) float32 — 1.0 where dot(N, L) < shadow_thresh
        light_mask    : (H, W) float32 — 1.0 where dot(N, L) >= shadow_thresh
        contour_mask  : (H, W) float32 — 1.0 where |dot(N, camera)| < contour_thresh

        All masks have feathered edges via a small Gaussian blur so stroke
        placement transitions look painted rather than hard-cut.
        """
        if self._normal_map is None:
            h, w = self.h, self.w
            ones  = np.zeros((h, w), dtype=np.float32)
            return ones, np.ones((h, w), dtype=np.float32), ones

        N = self._normal_map  # (H, W, 3)

        # Normalise light direction
        L = np.array(light_dir, dtype=np.float32)
        L_len = np.sqrt((L * L).sum()) + 1e-9
        L = L / L_len

        # Dot product: N · L for each pixel
        NdotL = (N * L[np.newaxis, np.newaxis, :]).sum(axis=2)  # (H, W)

        # Camera direction: in Blender convention the camera looks along -Y.
        # The "camera normal" for contour detection is the view direction (0, -1, 0).
        cam_dir = np.array([0.0, -1.0, 0.0], dtype=np.float32)
        NdotC = np.abs((N * cam_dir[np.newaxis, np.newaxis, :]).sum(axis=2))

        # Binary masks with feathering (Gaussian blur for soft edges)
        shadow_raw   = (NdotL < shadow_thresh).astype(np.float32)
        contour_raw  = (NdotC < contour_thresh).astype(np.float32)

        shadow_mask  = ndimage.gaussian_filter(shadow_raw,  sigma=1.5).astype(np.float32)
        contour_mask = ndimage.gaussian_filter(contour_raw, sigma=1.0).astype(np.float32)
        light_mask   = 1.0 - shadow_mask

        # Clip to [0, 1] after blur
        shadow_mask  = np.clip(shadow_mask,  0.0, 1.0)
        light_mask   = np.clip(light_mask,   0.0, 1.0)
        contour_mask = np.clip(contour_mask, 0.0, 1.0)

        return shadow_mask, light_mask, contour_mask

    def toon_paint(self, reference, light_direction, shadow_color=(0.12, 0.08, 0.04),
                   light_color=(0.92, 0.80, 0.65), ink_color=(0.05, 0.03, 0.02),
                   n_strokes=800, stroke_size=8):
        """Cel-shading paint pass using the loaded normal map.

        Three sub-passes:
          1. Shadow region — flat dark strokes (shadow_color)
          2. Light region  — flat warm strokes (light_color)
          3. Contour lines — thin dark ink strokes (ink_color) along contour dir

        All passes respect self._figure_mask if set.
        Uses BrushTip.FLAT for solid coverage.

        Parameters
        ----------
        reference       : reference image (PIL Image or ndarray, not used for colour
                          — pass for error-map weighting within each region)
        light_direction : (3,) world-space light direction (normalised)
        shadow_color    : fixed RGB tuple for shadow strokes
        light_color     : fixed RGB tuple for lit-area strokes
        ink_color       : fixed RGB tuple for contour strokes
        n_strokes       : total strokes (split ~1/3 shadow, 1/3 light, 1/4 contour)
        stroke_size     : base stroke width in pixels
        """
        print(f"Toon paint pass ({n_strokes} strokes, size={stroke_size}px)…")
        ref = self._prep(reference)

        shadow_mask, light_mask, contour_mask = self.toon_contour_mask(light_direction)

        # Apply figure mask to all region masks
        if self._figure_mask is not None:
            shadow_mask  = shadow_mask  * self._figure_mask
            light_mask   = light_mask   * self._figure_mask
            contour_mask = contour_mask * self._figure_mask

        tip_flat = BrushTip(BrushTip.FLAT)

        # ── Shadow pass ───────────────────────────────────────────────────────
        shadow_n = n_strokes // 3
        if shadow_mask.sum() > 1.0:
            self._place_strokes(
                ref, stroke_size, shadow_n,
                opacity=0.95, wet_blend=0.04, jitter_amt=0.015,
                curvature=0.03, tip=tip_flat,
                stroke_mask=shadow_mask,
                override_color=shadow_color,
            )

        # ── Light pass ────────────────────────────────────────────────────────
        light_n = n_strokes // 3
        if light_mask.sum() > 1.0:
            self._place_strokes(
                ref, stroke_size, light_n,
                opacity=0.90, wet_blend=0.04, jitter_amt=0.015,
                curvature=0.03, tip=tip_flat,
                stroke_mask=light_mask,
                override_color=light_color,
            )

        # ── Contour / ink pass ────────────────────────────────────────────────
        # Thin strokes oriented along the contour (tangent to the silhouette
        # edge), giving the appearance of hand-drawn ink outlines.
        contour_n = n_strokes // 4
        if contour_mask.sum() > 1.0:
            self._place_strokes(
                ref, max(2, stroke_size // 3), contour_n,
                opacity=0.98, wet_blend=0.02, jitter_amt=0.008,
                curvature=0.05, tip=tip_flat,
                stroke_mask=contour_mask,
                override_color=ink_color,
            )

    def seal_background(self, reference):
        """
        Before any figure strokes, lock the background by copying reference
        pixels directly onto the canvas for every non-figure pixel.

        Why: error-driven stroke sampling would otherwise place large strokes
        near the figure/background boundary that carry figure colours into the
        dark background.  Sealing prevents this entirely — the background
        pixels are already 'correct' and carry no painterly error signal.

        Also applies a tiny linen-texture modulation so the background reads
        as painted rather than photographic.
        """
        if self._figure_mask is None:
            return

        print("  Sealing background…")
        ref = Painter._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32)   # 0-255 range

        bg = self._figure_mask < 0.5               # (H, W) bool

        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(self.h, self.w, 4).copy()

        tex = self.canvas.texture                  # (H, W) float32 in ~[0,1]
        strength = 0.06                            # subtle texture modulation
        mod = 1.0 - strength + strength * tex      # e.g. 0.94 … 1.00

        # Write reference colour into background pixels with texture modulation.
        # Cairo uses BGRA byte order.
        buf[bg, 2] = np.clip(rarr[bg, 0] * mod[bg], 0, 255).astype(np.uint8)  # R
        buf[bg, 1] = np.clip(rarr[bg, 1] * mod[bg], 0, 255).astype(np.uint8)  # G
        buf[bg, 0] = np.clip(rarr[bg, 2] * mod[bg], 0, 255).astype(np.uint8)  # B
        buf[bg, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

    def background_pass(self, reference, n_strokes: int = 60,
                        stroke_size: float = 55):
        """
        Optional atmospheric background strokes (placed ONLY in background).

        A small number of large, dark, loosely directional strokes give the
        background painterly texture without contaminating the figure region.
        Painted before any figure strokes.
        """
        if self._figure_mask is None:
            return

        print(f"  Background pass ({n_strokes} strokes  size={stroke_size:.0f}px)…")
        ref   = self._prep(reference)
        bg_mask = 1.0 - self._figure_mask          # (H, W): 1=bg, 0=figure
        self._place_strokes(ref, stroke_size, n_strokes,
                            opacity=0.55, wet_blend=0.08,
                            jitter_amt=0.015, curvature=0.05,
                            tip=BrushTip(BrushTip.FLAT),
                            stroke_mask=bg_mask)

    # ── Layer methods ─────────────────────────────────────────────────────────

    def tone_ground(self, color: Color, texture_strength: float = 0.07):
        """
        Step 1 — Toned ground.
        Eliminates the white canvas; sets the mid-tone temperature.
        Traditionally: raw umber, terre verte, or warm ochre.
        """
        print("Toning ground…")
        self.canvas.tone(color, texture_strength)

    def underpainting(self, reference: Union[np.ndarray, Image.Image],
                      stroke_size: float = 52,
                      n_strokes:   int   = 150):
        """
        Step 2 — Dead-colour underpainting.
        Value structure only, desaturated toward raw umber.
        Establishes light/dark composition before colour is introduced.
        """
        print(f"Underpainting  ({n_strokes} strokes  size={stroke_size:.0f}px)…")
        ref = self._prep(reference)
        gray_ref = self._to_value(ref, warm_tint=(0.42, 0.32, 0.18))
        self.canvas.dry(0.9)
        self._place_strokes(gray_ref, stroke_size, n_strokes,
                            opacity=0.60, wet_blend=0.12,
                            jitter_amt=0.02, curvature=0.04,
                            tip=BrushTip(BrushTip.FLAT),
                            stroke_mask=self._figure_mask)

    def block_in(self, reference: Union[np.ndarray, Image.Image],
                 stroke_size: float = 36,
                 n_strokes:   int   = 300):
        """
        Step 3 — Block-in.
        Large confident strokes establishing main colour masses.
        Painters work boldly here; no detail yet.
        """
        print(f"Blocking in    ({n_strokes} strokes  size={stroke_size:.0f}px)…")
        ref = self._prep(reference)
        self.canvas.dry(0.65)
        self._place_strokes(ref, stroke_size, n_strokes,
                            opacity=0.72, wet_blend=0.28,
                            jitter_amt=0.045, curvature=0.07,
                            tip=BrushTip(BrushTip.FILBERT),
                            stroke_mask=self._figure_mask)

    def build_form(self, reference: Union[np.ndarray, Image.Image],
                   stroke_size: float = 15,
                   n_strokes:   int   = 700):
        """
        Step 4 — Form building.
        Medium directional strokes that follow surface curvature.
        This is the most labour-intensive stage.
        Stroke direction follows image gradient contours (Hertzmann 1998).
        """
        print(f"Building form  ({n_strokes} strokes  size={stroke_size:.0f}px)…")
        ref = self._prep(reference)
        self.canvas.dry(0.55)
        self._place_strokes(ref, stroke_size, n_strokes,
                            opacity=0.78, wet_blend=0.22,
                            jitter_amt=0.038, curvature=0.10,
                            tip=BrushTip(BrushTip.FILBERT),
                            stroke_mask=self._figure_mask)

    def place_lights(self, reference: Union[np.ndarray, Image.Image],
                     stroke_size: float = 6,
                     n_strokes:   int   = 500):
        """
        Step 5 — Lights placed last (impasto highlights).
        Small, opaque, bright strokes concentrated in high-luminance areas.
        In oil painting these are always the FINAL marks — never painted over.
        """
        print(f"Placing lights ({n_strokes} strokes  size={stroke_size:.0f}px)…")
        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        lum  = (0.299*rarr[:,:,0] + 0.587*rarr[:,:,1] + 0.114*rarr[:,:,2])
        # Bias toward VERY bright regions only (impasto highlights on nose tip,
        # forehead, cheekbone).  Power=4.5 (was 2.2) ensures only true specular
        # peaks qualify — moderately-lit hair (~0.4–0.6 lum) gets near-zero weight
        # and won't receive bright white strokes.  Also gate by figure mask.
        weight = np.power(lum, 4.5)
        if self._figure_mask is not None:
            weight *= self._figure_mask
        weight /= weight.sum() + 1e-9

        angles = flow_field(rarr)
        h, w   = ref.shape[:2]

        positions = self.rng.choice(h * w, size=n_strokes,
                                    p=weight.flatten(), replace=True)
        tip = BrushTip(BrushTip.ROUND)

        self.canvas.dry(0.8)
        for pos in positions:
            py, px = int(pos // w), int(pos % w)
            margin = max(4, int(stroke_size * 2))
            px = int(np.clip(px, margin, w - margin))
            py = int(np.clip(py, margin, h - margin))

            col = tuple(float(rarr[py, px, c]) for c in range(3))
            col = tuple(min(1.0, v * 1.18) for v in col)  # impasto: brighter
            col = jitter(col, 0.025, self._rng_py)

            a = float(angles[py, px]) + self._rng_py.uniform(-0.2, 0.2)
            length = stroke_size * self._rng_py.uniform(1.3, 2.4)
            start = (px - math.cos(a)*length*0.5,
                     py - math.sin(a)*length*0.5)
            pts = stroke_path(start, a, length,
                              curve=self._rng_py.uniform(-0.04, 0.04),
                              n=max(3, int(length / 3)))
            ws  = [stroke_size * self._rng_py.uniform(0.7, 1.0)] * len(pts)

            self.canvas.apply_stroke(pts, ws, col, tip,
                                     opacity=0.88, wet_blend=0.08,
                                     jitter_amt=0.02, rng=self._rng_py,
                                     region_mask=self._figure_mask)

    def pointillist_pass(self,
                         reference:       Union[np.ndarray, Image.Image],
                         n_dots:          int   = 6000,
                         dot_size:        float = 4.0,
                         chromatic_split: bool  = True,
                         split_ratio:     float = 0.30,
                         split_radius:    float = 2.5):
        """
        Divisionist dot pass — Seurat / Signac pointillism technique.

        Inspired by Georges Seurat's *A Sunday on La Grande Jatte* (1884–86)
        and the discoveries of Hilma af Klint, who also explored pure-colour
        fields and spiritual resonance in pigment placement.

        Each placement samples the reference colour at that pixel and places a
        small round dot.  When chromatic_split=True an additional tiny dot of
        the **complementary colour** (hue-rotated 180°) is offset by
        split_radius×dot_size pixels.  This mirrors Seurat's use of
        simultaneous contrast (Chevreul's law): adjacent complementary dots
        intensify each other optically in the viewer's eye, creating a
        luminosity impossible with physically mixed paint.

        Parameters
        ----------
        reference       : PIL Image or ndarray reference to sample colour from.
        n_dots          : Total number of primary dots placed.
        dot_size        : Radius of each dot in pixels.
        chromatic_split : Enable the complementary-dot shimmer technique.
        split_ratio     : Opacity of the complementary dot (0–1).
                          0.25–0.40 gives subtle vibration; >0.50 is vivid.
        split_radius    : Offset of complementary dot as a multiple of dot_size.
                          Seurat kept dots very close (~1.5–3 radii apart).

        Notes
        -----
        Unlike the brush-stroke passes this method does NOT use wet-on-wet
        blending (wet_blend is forced to 0.0 per Seurat's dry-on-dry method).
        The canvas should be toned first; any underpainting is visible between
        the sparsely-placed dots, just as the gessoed linen showed through in
        La Grande Jatte.
        """
        print(f"Pointillist pass  ({n_dots} dots  size={dot_size:.1f}px"
              + (" + complement)" if chromatic_split else ")") + "…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        # Error-weighted sampling so dots concentrate where canvas diverges most
        # from the reference (same principle as _place_strokes but adapted for dots).
        cbuf = np.frombuffer(self.canvas.surface.get_data(),
                             dtype=np.uint8).reshape(h, w, 4).copy()
        carr = cbuf[:, :, [2, 1, 0]].astype(np.float32) / 255.0
        err  = np.mean(np.abs(carr - rarr), axis=2).astype(np.float32)
        # Mild smoothing so dot placement isn't hyper-concentrated at single pixels.
        err  = ndimage.gaussian_filter(err, sigma=dot_size * 0.6)

        # Mask to figure only when available; else paint everywhere.
        region = self._figure_mask
        if region is not None:
            err = err * region

        err_flat = err.flatten()
        total    = err_flat.sum()
        if total < 1e-9:
            # Fallback to uniform sampling if canvas already closely matches reference.
            prob = np.ones(h * w, dtype=np.float32) / (h * w)
            if region is not None:
                prob *= region.flatten()
                prob /= prob.sum() + 1e-9
        else:
            prob = err_flat / total

        positions = self.rng.choice(h * w, size=n_dots, p=prob, replace=True)

        tip_round = BrushTip(BrushTip.ROUND, bristle_noise=0.0)
        margin = max(int(dot_size) + 1, 3)

        for pos in positions:
            py, px = int(pos // w), int(pos % w)
            px = int(np.clip(px, margin, w - margin))
            py = int(np.clip(py, margin, h - margin))

            # Sample reference colour at this pixel.
            primary = tuple(float(rarr[py, px, c]) for c in range(3))
            primary = jitter(primary, 0.025, self._rng_py)

            # Place a tiny round dot: two-point stroke (centre → centre + 1px).
            # The degenerate stroke collapses to a circle thanks to round tip caps.
            pts = [(float(px), float(py)), (float(px) + 0.5, float(py))]
            ws  = [dot_size, dot_size]

            self.canvas.apply_stroke(
                pts, ws, primary, tip_round,
                opacity=0.92, wet_blend=0.0,    # zero wet blending — Seurat's method
                jitter_amt=0.018, rng=self._rng_py,
                region_mask=region,
            )

            # ── Complementary dot (divisionist shimmer) ───────────────────────
            if chromatic_split:
                comp_col = complement(primary)
                comp_col = jitter(comp_col, 0.02, self._rng_py)

                # Offset in a random direction so the complement dot doesn't
                # simply overlay the primary — Seurat kept them visually distinct.
                angle = self._rng_py.uniform(0, 2 * math.pi)
                offset = dot_size * split_radius
                cx = int(np.clip(px + math.cos(angle) * offset, margin, w - margin))
                cy = int(np.clip(py + math.sin(angle) * offset, margin, h - margin))

                # Check region mask at complement position too.
                if region is not None and region[cy, cx] < 0.5:
                    continue

                comp_pts = [(float(cx), float(cy)), (float(cx) + 0.5, float(cy))]
                comp_ws  = [dot_size * 0.70, dot_size * 0.70]   # slightly smaller

                self.canvas.apply_stroke(
                    comp_pts, comp_ws, comp_col, tip_round,
                    opacity=split_ratio, wet_blend=0.0,
                    jitter_amt=0.015, rng=self._rng_py,
                    region_mask=region,
                )

    def luminous_glow_pass(self,
                           reference:    Union[np.ndarray, Image.Image],
                           n_rings:      int   = 9,
                           max_radius:   float = 0.55,
                           core_color:   Color = (0.98, 0.94, 0.72),
                           haze_color:   Color = (0.50, 0.62, 0.80),
                           core_opacity: float = 0.22,
                           haze_opacity: float = 0.10):
        """
        Atmospheric luminosity pass — inspired by J.M.W. Turner.

        Turner's late work dissolves solid form into radiant light.  His vortex
        compositions place the light source at the centre of a whirlpool of
        colour: burning white-yellow at the core, fading through warm amber and
        cool blue-grey to near-darkness at the periphery.

        This pass locates the brightest region in the reference image (the
        'sun' or primary light source) and overlays a series of concentric,
        semi-transparent radial gradients — each ring slightly larger and
        cooler than the last.  The accumulation creates the luminous aureole
        that is impossible to achieve with a single flat brush stroke.

        Unlike the stroke passes this is a post-processing compositing step:
        it does NOT use the wetness map or figure mask, because atmospheric
        light halos cross all boundaries (figure, background, edge).  Call it
        LAST, just before any final vignette or crackle.

        Parameters
        ----------
        reference    : PIL Image or ndarray — used only to locate the brightest
                       pixel (the light source centre).
        n_rings      : Number of glow rings to stack.  More rings = smoother
                       aureole.  9–12 is a good range; too many reads as foggy.
        max_radius   : Radius of the outermost ring as a fraction of the shorter
                       canvas dimension (0.55 = half the canvas width).
        core_color   : RGB of the innermost glow (hottest — near white-yellow).
        haze_color   : RGB of the outermost ring (cool atmospheric blue-grey).
        core_opacity : Alpha of the first (innermost) ring per layer.
        haze_opacity : Alpha of the last (outermost) ring per layer.

        Notes
        -----
        Turner frequently painted with a near-white cream ground and built up
        transparent warm glazes from the centre outward.  The cool blue-grey at
        the edges reflects his study of Goethe's colour theory: warm colours
        advance (light), cool colours recede (shadow/atmosphere).

        Famous works to study:
          *Light and Colour (Goethe's Theory)* (1843) — purest vortex composition.
          *Snow Storm — Steam-Boat* (1842) — ship dissolving in white tornado.
          *The Fighting Temeraire* (1839) — sunset aureole across calm water.
        """
        print(f"Luminous glow pass  ({n_rings} rings  max_r={max_radius:.2f})…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        # ── Locate brightest point (light source centre) ──────────────────────
        # Luminance map: weight toward warm bright pixels (matches incandescent
        # light sources which are warm rather than blue-white).
        lum = (0.40 * rarr[:, :, 0] +   # boosted red weight — warm bias
               0.50 * rarr[:, :, 1] +   # green
               0.10 * rarr[:, :, 2])    # suppressed blue
        lum = ndimage.gaussian_filter(lum, sigma=max(3.0, min(w, h) * 0.02))
        flat_idx = int(np.argmax(lum))
        src_y    = flat_idx // w
        src_x    = flat_idx %  w

        # ── Ring geometry ─────────────────────────────────────────────────────
        short_side  = min(w, h)
        outer_r     = max_radius * short_side

        # Rings grow non-linearly (quadratic) so the core is dense and the halo
        # thins out gracefully toward the edges — matching Turner's actual light.
        ring_radii = [outer_r * ((i + 1) / n_rings) ** 1.6
                      for i in range(n_rings)]

        # ── Draw concentric radial gradients ─────────────────────────────────
        for i, r in enumerate(ring_radii):
            t = i / max(n_rings - 1, 1)           # 0.0 = innermost, 1.0 = outermost

            # Colour: lerp from core (warm) to haze (cool)
            rc = core_color[0] + (haze_color[0] - core_color[0]) * t
            gc = core_color[1] + (haze_color[1] - core_color[1]) * t
            bc = core_color[2] + (haze_color[2] - core_color[2]) * t

            # Opacity: lerp between core and haze opacities, then halve for each
            # successive ring so they don't simply overdrive brightness.
            ring_opacity = core_opacity + (haze_opacity - core_opacity) * t
            # Thin inner rings need higher opacity; outer rings accumulate via
            # multiple layers so they're kept light individually.
            ring_opacity *= max(0.30, 1.0 - t * 0.55)

            # Inner edge fully transparent → outer edge at ring_opacity (annular).
            # Using two concentric radial gradients stacked gives a true ring
            # rather than a filled disk, which better matches Turner's swirling
            # diffuse bands of colour.
            inner_r = r * 0.0 if i == 0 else ring_radii[i - 1] * 0.65

            grad = cairo.RadialGradient(
                src_x, src_y, inner_r,
                src_x, src_y, r,
            )
            grad.add_color_stop_rgba(0.0, rc, gc, bc, 0.0)            # centre → transparent
            grad.add_color_stop_rgba(0.45, rc, gc, bc, ring_opacity)  # peak opacity
            grad.add_color_stop_rgba(1.0, rc, gc, bc, 0.0)            # fade to transparent

            self.canvas.ctx.rectangle(0, 0, w, h)
            self.canvas.ctx.set_source(grad)
            self.canvas.ctx.fill()

        # ── Thin warm core bloom (Vermeer 'pearls' at the light source) ───────
        # A final very small, very opaque bright dot at the exact light centre
        # gives the pin-sharp 'sun disc' visible in Turner's works through haze.
        bloom_r = max(3.0, short_side * 0.012)
        bloom   = cairo.RadialGradient(src_x, src_y, 0, src_x, src_y, bloom_r)
        bloom.add_color_stop_rgba(0.0, 1.0, 0.97, 0.88, 0.55)
        bloom.add_color_stop_rgba(1.0, 1.0, 0.97, 0.88, 0.0)
        self.canvas.ctx.arc(src_x, src_y, bloom_r, 0, 2 * math.pi)
        self.canvas.ctx.set_source(bloom)
        self.canvas.ctx.fill()

    def focused_pass(self,
                     reference:   Union[np.ndarray, Image.Image],
                     region_mask: np.ndarray,
                     stroke_size: float = 8,
                     n_strokes:   int   = 600,
                     opacity:     float = 0.82,
                     wet_blend:   float = 0.12,
                     jitter_amt:  float = 0.025,
                     curvature:   float = 0.06,
                     form_angles: Optional[np.ndarray] = None):
        """
        High-density detail pass concentrated in a masked region.

        region_mask — (H, W) float32 array in [0, 1].
                      1.0 = stroke here, 0.0 = never stroke here.
        form_angles — optional pre-computed flow field (H, W) float32
                      in radians.  If None, derived from reference gradient.
                      Pass a spherical/radial field for faces so strokes
                      follow the curved surface rather than the flat image.

        This is how a portrait painter works: after the broad block-in,
        they move close to the canvas and place many small strokes on the
        face alone, with the brush following cheekbone curves and orbital
        contours rather than just colour edges.
        """
        label = f"Focused pass   ({n_strokes} strokes  size={stroke_size:.0f}px)"
        print(f"{label}…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        # Error map
        cbuf = np.frombuffer(self.canvas.surface.get_data(),
                             dtype=np.uint8).reshape(h, w, 4).copy()
        carr = cbuf[:, :, [2, 1, 0]].astype(np.float32) / 255.0
        err  = np.mean(np.abs(carr - rarr), axis=2).astype(np.float32)
        err  = ndimage.gaussian_filter(err, sigma=stroke_size * 0.3)

        # Reference luminance gradient — captures facial feature edges (nose
        # shadow, orbital rim, lip line) that error alone misses once the
        # block-in pass has covered the face in roughly-correct skin tone.
        lum_ref = (0.299 * rarr[:,:,0] + 0.587 * rarr[:,:,1]
                   + 0.114 * rarr[:,:,2]).astype(np.float32)
        gx = ndimage.sobel(lum_ref, axis=1).astype(np.float32)
        gy = ndimage.sobel(lum_ref, axis=0).astype(np.float32)
        grad_mag = np.sqrt(gx**2 + gy**2)
        if grad_mag.max() > 1e-9:
            grad_mag /= grad_mag.max()

        mask = np.clip(region_mask, 0, 1).astype(np.float32)

        # Intersect face/feature ellipse with the figure mask so focused_pass
        # strokes never land in the background.  Without this the ellipse extends
        # past the figure silhouette and strokes painted there (with pale skin
        # colours) appear as bright smears above/beside the head.
        if self._figure_mask is not None:
            mask = mask * self._figure_mask

        # Tripartite weight: raw error + gradient edges within mask + base mask coverage.
        # The gradient term pulls strokes toward nose/eye/lip feature boundaries.
        weight = err * 0.25 + (grad_mag * mask) * 0.45 + mask * 0.30
        weight = weight.flatten()
        weight /= weight.sum() + 1e-9

        angles = form_angles if form_angles is not None else flow_field(rarr)
        tip    = BrushTip(BrushTip.ROUND)

        # Local contrast lookup window (half-width in pixels)
        _contrast_hw = max(8, int(stroke_size * 1.5))
        _contrast_amp = 1.7   # push colours away from local mean

        self.canvas.dry(0.7)
        positions = self.rng.choice(h * w, size=n_strokes,
                                    p=weight, replace=True)
        lengths = stroke_size * self.rng.uniform(1.4, 2.8, n_strokes)

        for i, pos in enumerate(positions):
            py, px = int(pos // w), int(pos % w)
            margin = max(3, int(stroke_size * 1.5))
            px = int(np.clip(px, margin, w - margin))
            py = int(np.clip(py, margin, h - margin))

            col = tuple(float(rarr[py, px, c]) for c in range(3))

            # Local contrast enhancement within the masked region: shadows are
            # pushed darker, highlights brighter relative to the local mean.
            # Without this the face reads as a uniform pale blob because coarse
            # passes have already averaged out the subtle light/shadow gradient.
            if mask[py, px] > 0.4:
                hw = _contrast_hw
                patch = rarr[max(0, py-hw):py+hw+1,
                             max(0, px-hw):px+hw+1, :]
                pm = tuple(float(np.mean(patch[:, :, c])) for c in range(3))
                col = tuple(
                    max(0.0, min(1.0, pm[c] + (col[c] - pm[c]) * _contrast_amp))
                    for c in range(3)
                )

            col = jitter(col, jitter_amt, self._rng_py)

            a = float(angles[py, px]) + self._rng_py.uniform(-0.22, 0.22)
            L = lengths[i]
            start = (px - math.cos(a)*L*0.5, py - math.sin(a)*L*0.5)
            n_pts = max(4, int(L / 4))
            pts = stroke_path(start, a, L,
                              curve=self._rng_py.uniform(-curvature, curvature),
                              n=n_pts)
            ww = stroke_size * self._rng_py.uniform(0.55, 1.05)
            ws = [ww] * len(pts)

            # region_mask contains strokes within the face/feature ellipse
            self.canvas.apply_stroke(pts, ws, col, tip,
                                     opacity=opacity, wet_blend=wet_blend,
                                     jitter_amt=jitter_amt, rng=self._rng_py,
                                     region_mask=mask if mask is not None else None)

    def glaze(self, color: Color, opacity: float = 0.10):
        """
        Step 6 — Final glaze.
        Thin transparent wash over the whole painting.
        Warms or cools the overall tone; unifies the palette.
        """
        print(f"Glazing  colour={color}  opacity={opacity:.0%}…")
        self.canvas.dry(1.0)
        self.canvas.glaze(color, opacity)

    def finish(self, vignette: float = 0.50, crackle: bool = True):
        """
        Final post-processing: vignette + aged-varnish crackle.
        """
        print("Finishing…")
        self.canvas.vignette(vignette)
        if crackle:
            print("  Adding crackle…")
            self.canvas.crackle()

    def save(self, path: str):
        self.canvas.save(path)

    def show(self, viewer: str = "inkscape"):
        import tempfile, subprocess
        tmp = tempfile.mktemp(suffix=".png", prefix="painting_")
        self.canvas.save(tmp)
        inkscape = r"C:\Program Files\Inkscape\bin\inkscape.exe"
        subprocess.Popen([inkscape, tmp])
        return tmp

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _prep(img: Union[np.ndarray, Image.Image]) -> np.ndarray:
        """Ensure reference is a (H, W, 4) uint8 numpy array."""
        if isinstance(img, Image.Image):
            img = img.convert("RGBA")
            return np.array(img)
        if img.ndim == 3 and img.shape[2] == 3:
            return np.dstack([img,
                              np.full(img.shape[:2], 255, dtype=np.uint8)])
        return img.astype(np.uint8)

    @staticmethod
    def _to_value(ref: np.ndarray,
                  warm_tint: Color = (0.4, 0.32, 0.20)) -> np.ndarray:
        """
        Desaturate to luminosity and tint toward warm_tint.
        Used for the underpainting (dead-colour) layer.
        """
        f  = ref[:, :, :3].astype(np.float32) / 255.0
        lm = (0.299*f[:,:,0] + 0.587*f[:,:,1] + 0.114*f[:,:,2])
        wt = np.array(warm_tint, dtype=np.float32)
        out = np.zeros_like(f)
        for c in range(3):
            out[:, :, c] = np.clip(lm * 0.55 + wt[c] * 0.45, 0, 1)
        rgb  = (out * 255).astype(np.uint8)
        alph = ref[:, :, 3:4]
        return np.concatenate([rgb, alph], axis=2)

    def _place_strokes(self,
                       ref:            np.ndarray,
                       stroke_size:    float,
                       n_strokes:      int,
                       opacity:        float,
                       wet_blend:      float,
                       jitter_amt:     float,
                       curvature:      float,
                       tip:            BrushTip,
                       stroke_mask:    Optional[np.ndarray] = None,
                       override_color: Optional[Color]      = None):
        """
        Core stroke placement loop.
        Positions are sampled from the error map (canvas vs reference)
        so strokes are concentrated where most improvement is needed.

        stroke_mask    — optional (H, W) float32 in [0, 1].  When provided,
            stroke centres are ONLY sampled from within the mask region.
            The mask is eroded by the maximum stroke half-length so no
            stroke can reach across the boundary.  Each segment is then
            individually clipped at the mask boundary as a hard backstop.

            Pass self._figure_mask for figure strokes.
            Pass (1 - self._figure_mask) for background strokes.

        override_color — optional fixed RGB (float, float, float) in [0, 1].
            When set, ALL strokes use this colour instead of sampling from
            the reference.  Used by toon_paint() for flat cel-shading passes.
        """
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        # Canvas current state
        cbuf = np.frombuffer(self.canvas.surface.get_data(),
                             dtype=np.uint8).reshape(h, w, 4).copy()
        carr = cbuf[:, :, [2, 1, 0]].astype(np.float32) / 255.0

        # Error map — where canvas diverges from reference
        err = np.mean(np.abs(carr - rarr), axis=2).astype(np.float32)
        err = ndimage.gaussian_filter(err, sigma=stroke_size * 0.45)

        # Region masking ── erode so stroke centres stay well inside the region
        region_mask_for_draw = None
        if stroke_mask is not None:
            binary = (stroke_mask > 0.5)
            # Erode by max stroke half-reach so endpoints can't cross boundary
            erosion_r = max(1, int(stroke_size * 1.4))
            struct    = np.ones((erosion_r * 2 + 1, erosion_r * 2 + 1), dtype=bool)
            eroded    = ndimage.binary_erosion(binary, structure=struct)
            err = err * eroded.astype(np.float32)
            # Also store the (un-eroded) mask for per-segment clipping
            region_mask_for_draw = stroke_mask.astype(np.float32)

        err_flat = err.flatten()
        total = err_flat.sum()
        if total < 1e-9:
            return   # mask too small / nothing to paint
        prob = err_flat / total

        # Stroke direction field
        angles = flow_field(rarr)

        positions = self.rng.choice(h * w, size=n_strokes,
                                    p=prob, replace=True)
        lengths = stroke_size * self.rng.uniform(1.6, 3.2, n_strokes)

        for i, pos in enumerate(positions):
            py, px = int(pos // w), int(pos % w)
            margin = max(4, int(stroke_size * 1.8))
            px = int(np.clip(px, margin, w - margin))
            py = int(np.clip(py, margin, h - margin))

            # Use override_color for cel-shading passes; otherwise sample reference.
            if override_color is not None:
                col = jitter(override_color, jitter_amt, self._rng_py)
            else:
                col = tuple(float(rarr[py, px, c]) for c in range(3))
                col = jitter(col, jitter_amt, self._rng_py)

            a = float(angles[py, px]) + self._rng_py.uniform(-0.28, 0.28)
            L = lengths[i]
            start = (px - math.cos(a)*L*0.5, py - math.sin(a)*L*0.5)

            n_pts = max(4, int(L / 5))
            pts = stroke_path(start, a, L,
                              curve=self._rng_py.uniform(-curvature, curvature),
                              n=n_pts)
            w_val = stroke_size * self._rng_py.uniform(0.55, 1.15)
            ws    = [w_val] * len(pts)

            self.canvas.apply_stroke(pts, ws, col, tip,
                                     opacity=opacity,
                                     wet_blend=wet_blend,
                                     jitter_amt=jitter_amt,
                                     rng=self._rng_py,
                                     region_mask=region_mask_for_draw)
