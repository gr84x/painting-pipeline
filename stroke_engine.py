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


def make_cold_press_texture(w: int, h: int) -> np.ndarray:
    """
    Returns a (H, W) float32 array in [0.68, 1.0] representing cold-press
    watercolor paper texture.

    Cold-press (NOT) watercolor paper has a distinct character compared to
    woven linen canvas:

    1. **Large irregular tooth** — the paper surface has a rough, random grain
       formed by pressing the wet pulp sheet into a felt (the 'cold press').
       Two scales: coarse bumps (2–5mm) and medium mid-grain.

    2. **Horizontal laid lines** — the wire mesh of the papermaking mould
       leaves faint horizontal parallel striations spaced ~1mm apart.
       These are subtle but visible when paint pools in the valleys.

    3. **Chain lines** — thicker vertical wires are spaced every ~25mm,
       creating a barely perceptible vertical grid of slightly lower relief.

    Unlike linen, the cold-press surface absorbs water non-uniformly —
    higher areas resist first washes while low areas trap pigment.  This is
    the source of the characteristic blooms and cauliflowers of watercolor.

    The watercolor pipeline uses this texture in `tone_ground()` so the paper
    surface shows through in the untouched highlight areas.
    """
    tex = np.zeros((h, w), dtype=np.float32)
    inv_w, inv_h = 1.0 / w, 1.0 / h

    # ── Stage 1: Coarse irregular grain ──────────────────────────────────────
    # Two overlapping Perlin octave bands for paper bumps.
    for y in range(h):
        for x in range(w):
            coarse = pnoise2(x * inv_w * 18, y * inv_h * 18,
                             octaves=3, persistence=0.55)
            medium = pnoise2(x * inv_w * 55, y * inv_h * 55,
                             octaves=2, persistence=0.45)
            tex[y, x] = coarse * 0.55 + medium * 0.45

    # Normalise Perlin output to [0, 1]
    lo, hi = tex.min(), tex.max()
    tex = (tex - lo) / (hi - lo + 1e-8)

    # ── Stage 2: Horizontal laid lines ────────────────────────────────────────
    # Spaced ~1mm at 96 dpi ≈ every 3.8 pixels.  Subtle — only a 3% darkening
    # in the laid-line valleys so they appear as faint ribbing under wash.
    laid_period = max(3, round(h * 0.0035))          # ~0.35 % of canvas height
    ys = np.arange(h)
    laid = 0.03 * (0.5 - 0.5 * np.cos(2 * math.pi * ys / laid_period))
    tex -= laid[:, np.newaxis]                        # slight dip in laid valleys

    # ── Stage 3: Chain lines ──────────────────────────────────────────────────
    # Much wider spacing (~25mm at 96 dpi ≈ every 94px) and very faint (1%).
    chain_period = max(60, round(w * 0.12))
    xs = np.arange(w)
    chain = 0.01 * (0.5 - 0.5 * np.cos(2 * math.pi * xs / chain_period))
    tex -= chain[np.newaxis, :]

    # Re-normalise to [0.68, 1.0] — same range as linen texture
    lo, hi = tex.min(), tex.max()
    tex = (tex - lo) / (hi - lo + 1e-8)
    return (0.68 + 0.32 * tex).astype(np.float32)


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


def anatomy_flow_field(w: int, h: int,
                       cx: float, cy: float,
                       rx: float, ry: float,
                       gradient_fallback: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Anatomy-aware stroke flow field for portrait faces.

    Unlike ``spherical_flow()`` which treats the face as a featureless sphere,
    this field encodes the **major anatomical planes** that trained portrait
    painters follow instinctively when building form:

      ┌─────────────────────────────────────────────────────────────────┐
      │  Forehead (ny < -0.45)                                          │
      │    → Near-horizontal strokes with a gentle outward spread.      │
      │      The forehead is a broad, near-flat plane; painters run      │
      │      strokes across it rather than up-down.                     │
      │  Brow ridge / upper cheek (ny ∈ [-0.45, -0.10])                │
      │    → Diagonal strokes curving outward from the nose bridge,      │
      │      following the supraorbital arc and zygoma.                 │
      │  Eye socket zone (|nx| < 0.55, ny ∈ [-0.35, 0.10])            │
      │    → Orbital circle tangent — strokes orbit the eye socket.     │
      │  Nose bridge / axis (|nx| < 0.22, ny ∈ [-0.15, 0.55])         │
      │    → Near-vertical strokes running down the nasal planes.        │
      │  Cheeks (|nx| > 0.25, ny ∈ [-0.10, 0.50])                     │
      │    → Diagonal strokes following the cheekbone toward the jaw.   │
      │  Philtrum / upper lip (ny ∈ [0.30, 0.60])                     │
      │    → Near-horizontal strokes, slightly converging at centre.    │
      │  Chin / mandible (ny > 0.55)                                   │
      │    → Downward-curving strokes following jaw contour outward.    │
      └─────────────────────────────────────────────────────────────────┘

    Parameters
    ----------
    w, h              : canvas dimensions.
    cx, cy            : face centre pixel coordinates.
    rx, ry            : face ellipse radii in pixels.
    gradient_fallback : optional pre-computed ``flow_field()`` array.
                        Used to blend in a gradient-driven direction for
                        pixels outside the face ellipse (d > 1.4).

    Returns
    -------
    (H, W) float32 ndarray of stroke angles in radians.
    """
    ys, xs = np.mgrid[0:h, 0:w]

    # Normalised face-relative coordinates in [-1, 1] space.
    nx = (xs - cx) / (rx + 1e-6)          # -1 = left ear, +1 = right ear
    ny = (ys - cy) / (ry + 1e-6)          # -1 = hairline, +1 = chin
    d  = np.sqrt(nx ** 2 + ny ** 2)       # distance from face centre, norm.

    # ── Zone angles (one per anatomical region) ───────────────────────────────

    # Forehead: near-horizontal, slight upward bow at centre, outward spread.
    ang_forehead = np.arctan2(nx * 0.18, np.ones_like(nx))

    # Brow / upper cheek: supraorbital arc; diagonal following cheekbone slope.
    ang_brow = np.arctan2(nx * 0.6, -np.ones_like(nx) * 0.3)

    # Eye socket orbit: strokes circle the socket like latitude lines on a small
    # sphere.  Tangent to the orbital ring = (-dy_orbit, dx_orbit) where
    # the orbit centre is at (0, -0.20) in normalised space.
    orb_dx = nx
    orb_dy = ny + 0.20
    ang_orbit = np.arctan2(orb_dx, -orb_dy)

    # Nose axis: near-vertical, slight inward lean toward centre line.
    ang_nose = np.arctan2(nx * 0.10, np.ones_like(nx) * 0.9)

    # Cheeks: diagonal toward jaw; steepens further from centre.
    ang_cheek = np.arctan2(
        np.sign(nx) * 0.55 + nx * 0.35,
        np.ones_like(ny) * 0.7 + ny * 0.20,
    )

    # Philtrum / lip: horizontal strokes with gentle convergence at midline.
    ang_lip = np.arctan2(nx * (-0.12), np.ones_like(nx))

    # Chin / mandible: downward-curving strokes that fan outward from the chin.
    ang_chin = np.arctan2(
        np.sign(nx) * 0.40 + nx * 0.30,
        np.ones_like(ny) * 0.85,
    )

    # ── Blend weights per zone (smooth, overlapping) ──────────────────────────

    def smooth_step(a: float, b: float, arr: np.ndarray) -> np.ndarray:
        """Smoothstep ramp 0→1 over the interval [a, b]."""
        t = np.clip((arr - a) / (b - a + 1e-9), 0.0, 1.0).astype(np.float32)
        return t * t * (3 - 2 * t)

    # ny-based zone weights (vertical anatomy)
    w_forehead = smooth_step(-0.55, -0.30, -ny)              # top: large weight
    w_brow     = (smooth_step(0.25, 0.55, -ny) *
                  smooth_step(0.35, 0.65, -ny + 0.2))        # upper face
    w_orbit    = (smooth_step(-0.05, 0.25, -ny) *
                  smooth_step(0.35, 0.10, np.abs(nx) - 0.1)) # eye zone (central)
    w_nose     = (smooth_step(-0.20, 0.05, ny) *
                  smooth_step(0.60, 0.25, ny) *
                  smooth_step(0.22, 0.0, np.abs(nx)))         # nose (centre)
    w_cheek    = (smooth_step(0.0, 0.30, ny) *
                  smooth_step(0.60, 0.35, ny) *
                  smooth_step(0.25, 0.55, np.abs(nx)))        # cheeks (sides)
    w_lip      = smooth_step(0.22, 0.45, ny)                  # lower-mid face
    w_chin     = smooth_step(0.50, 0.75, ny)                  # bottom

    # Stack and normalise (each pixel belongs partly to multiple zones).
    total = w_forehead + w_brow + w_orbit + w_nose + w_cheek + w_lip + w_chin + 1e-9

    # Weighted blend of angles using sin/cos to avoid wrap discontinuity.
    def _blend(weights_list, angles_list):
        sin_sum = np.zeros((h, w), dtype=np.float32)
        cos_sum = np.zeros((h, w), dtype=np.float32)
        for ww, aa in zip(weights_list, angles_list):
            sin_sum += ww * np.sin(aa)
            cos_sum += ww * np.cos(aa)
        return np.arctan2(sin_sum, cos_sum)

    blended = _blend(
        [w_forehead, w_brow, w_orbit, w_nose, w_cheek, w_lip, w_chin],
        [ang_forehead, ang_brow, ang_orbit, ang_nose, ang_cheek, ang_lip, ang_chin],
    )
    blended = blended / total  # normalise is implicitly in arctan2 result,
                                # but rescale influences for cleaner output
    blended = _blend(
        [w_forehead, w_brow, w_orbit, w_nose, w_cheek, w_lip, w_chin],
        [ang_forehead, ang_brow, ang_orbit, ang_nose, ang_cheek, ang_lip, ang_chin],
    )

    # ── Blend to fallback outside the face ellipse ────────────────────────────
    if gradient_fallback is not None:
        # Smooth transition: anatomy field fully active inside d < 0.9,
        # fades to gradient fallback between d = 0.9 and d = 1.4.
        inside  = np.clip(1.0 - (d - 0.90) / 0.50, 0.0, 1.0).astype(np.float32)
        outside = 1.0 - inside
        sin_b = inside * np.sin(blended) + outside * np.sin(gradient_fallback)
        cos_b = inside * np.cos(blended) + outside * np.cos(gradient_fallback)
        blended = np.arctan2(sin_b, cos_b).astype(np.float32)

    # Final smooth to remove any numerical noise from the zone blending.
    blended = ndimage.gaussian_filter(blended, sigma=3.5)
    return blended.astype(np.float32)


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

    def set_substrate(self, kind: str = "linen"):
        """
        Replace the canvas texture with the chosen substrate.

        Parameters
        ----------
        kind : str
            "linen"       — woven linen canvas (default; already set at init).
            "cold_press"  — cold-press watercolor paper with laid lines, chain
                            lines, and irregular paper tooth.  Use before the
                            watercolor_wash_pass() to get authentic paper grain
                            showing through untouched highlight areas.

        Why this matters
        ----------------
        The canvas texture modulates every `tone_ground()` call so the physical
        surface "shows through" the paint layer.  Linen weave on a watercolor
        painting looks wrong — the texture grid is too regular and too coarse.
        Cold-press paper has a distinctly different character: random coarse tooth
        plus faint horizontal laid lines from the paper mould wire.  Switching
        substrate before the watercolor passes ensures that the highlight areas
        (where no pigment is placed) display authentic paper surface rather than
        linen.
        """
        w, h = self.w, self.h
        if kind == "cold_press":
            print("  Stretching cold-press watercolor paper…")
            self.canvas.texture = make_cold_press_texture(w, h)
        else:
            print("  Weaving linen texture…")
            self.canvas.texture = make_linen_texture(w, h)

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

    def woodblock_pass(self,
                       reference:         Union[np.ndarray, Image.Image],
                       n_colors:          int   = 8,
                       bokashi_color:     Color = (0.15, 0.38, 0.72),
                       bokashi_strength:  float = 0.42,
                       bokashi_vertical:  bool  = True,
                       contour_weight:    float = 0.30,
                       contour_thickness: float = 2.5,
                       ink_color:         Color = (0.06, 0.04, 0.10)):
        """
        Ukiyo-e woodblock print technique — inspired by Katsushika Hokusai.

        Traditional ukiyo-e prints are built from three separate carved wood
        blocks printed in register:

          1. **Keyblock (Kento)** — the ink outline, printed in near-black or
             deep indigo.  Defines all major forms and figure silhouettes.
          2. **Colour blocks** — each flat colour region has its own block.
             The colours are pure, unshaded, with no tonal modelling.
          3. **Bokashi** — a soft graduated wash, produced by rubbing damp
             pigment from the edge of the block inward.  Typically Prussian
             blue in sky, water, and distant background areas.

        This pass replicates the full three-stage process:

          Stage 1 — Flat colour quantisation:
            The reference is reduced to ``n_colors`` dominant pigments via
            median-cut quantisation.  Each pixel is then painted with its
            nearest palette colour, creating the flat blocked-out regions
            characteristic of all ukiyo-e work.

          Stage 2 — Bokashi gradient:
            A soft directional gradient (default: Prussian blue, top → bottom,
            or left → right in landscape works) is overlaid at reduced opacity
            in the background zone, recreating the graduated atmospheric wash
            that makes Hokusai's skies and seas luminous.

          Stage 3 — Ink contour lines (keyblock):
            Thin dark strokes are placed along value boundaries (detected via
            Sobel gradient magnitude).  These mimic the carved contour lines
            that give ukiyo-e its distinctive graphic clarity.

        Parameters
        ----------
        reference         : Reference image (PIL Image or ndarray).
        n_colors          : Palette size for flat colour quantisation (6–12).
        bokashi_color     : Colour of the directional wash (default: Prussian blue).
        bokashi_strength  : Maximum opacity of the bokashi gradient (0–1).
                            0.30–0.50 reads as subtle; >0.60 reads as deep sky.
        bokashi_vertical  : True = top-to-bottom fade (sky); False = left-right.
        contour_weight    : Weight of contour detection in stroke placement
                            (0 = ignore value edges, 1 = contours only).
        contour_thickness : Width of ink keyblock lines in pixels.
        ink_color         : Colour of the keyblock outline strokes.

        Notes
        -----
        Unlike oil painting passes this method does NOT use the wetness map
        (ukiyo-e pigment is water-based and dries instantly).  wet_blend is
        forced to 0.0 throughout.

        Famous Hokusai works to study:
          *The Great Wave off Kanagawa* (c. 1831) — defining bokashi
          *Fine Wind, Clear Morning (Red Fuji)* (c. 1831) — flat colour + sky
          *The Dream of the Fisherman's Wife* (1814) — keyblock mastery
        """
        print(f"Woodblock pass  (n_colors={n_colors}  bokashi={bokashi_strength:.2f}"
              + f"  contour_w={contour_weight:.2f})…")

        ref  = self._prep(reference)
        h, w = ref.shape[:2]

        # ── Stage 1: Flat colour quantisation ────────────────────────────────
        # Reduce the reference to n_colors representative pigments and fill
        # each pixel with its nearest palette colour — no tonal blending.
        print("  Stage 1: flat colour quantisation…")
        pil_ref = Image.fromarray(ref[:, :, :3])

        # Quantise using PIL's median-cut algorithm to find dominant pigments.
        quantized_pil = pil_ref.quantize(colors=n_colors,
                                         method=Image.Quantize.MEDIANCUT,
                                         dither=Image.Dither.NONE)
        # Convert back to RGB so each pixel holds its palette colour.
        flat_rgb = np.array(quantized_pil.convert("RGB"), dtype=np.uint8)

        # Write the flat-colour image to the canvas surface.
        # Cairo stores BGRA; we build that directly.
        flat_bgra = np.dstack([flat_rgb[:, :, 2],   # B
                               flat_rgb[:, :, 1],   # G
                               flat_rgb[:, :, 0],   # R
                               np.full((h, w), 255, dtype=np.uint8)])
        flat_bytes = bytearray(flat_bgra.astype(np.uint8).tobytes())
        flat_surf  = cairo.ImageSurface.create_for_data(
            flat_bytes, cairo.FORMAT_ARGB32, w, h)
        self.canvas.ctx.set_source_surface(flat_surf, 0, 0)
        self.canvas.ctx.paint()

        # ── Stage 2: Bokashi gradient ──────────────────────────────────────────
        # Apply a soft directional colour wash over the background zone only.
        # In Hokusai's prints this is typically a graduated Prussian-blue sky
        # running from dark at the top to pale cream at the horizon.
        print("  Stage 2: bokashi gradient…")
        br, bg, bb = bokashi_color

        if bokashi_vertical:
            # Vertical: dark at top (y=0), fades to transparent at mid-canvas.
            grad = cairo.LinearGradient(0, 0, 0, h * 0.65)
        else:
            # Horizontal: left to right (e.g. for wave / water direction).
            grad = cairo.LinearGradient(0, 0, w * 0.65, 0)

        grad.add_color_stop_rgba(0.0, br, bg, bb, bokashi_strength)
        grad.add_color_stop_rgba(0.55, br, bg, bb, bokashi_strength * 0.25)
        grad.add_color_stop_rgba(1.0, br, bg, bb, 0.0)

        # Apply only in background zone if mask is available; otherwise full canvas.
        if self._figure_mask is not None:
            # Background is where figure_mask < 0.5.
            # Build a temporary mask surface to clip the gradient.
            bg_mask = (self._figure_mask < 0.5).astype(np.uint8) * 255
            mask_rgba = np.dstack([bg_mask, bg_mask, bg_mask,
                                   bg_mask]).astype(np.uint8)
            mask_bytes = bytearray(mask_rgba.tobytes())
            mask_surf  = cairo.ImageSurface.create_for_data(
                mask_bytes, cairo.FORMAT_ARGB32, w, h)

            # Paint gradient, then mask it by multiplying alpha with the bg mask.
            # Simpler approach: just fill, but skip figure pixels.
            # We'll use a full-canvas fill and let the very light opacity do the work
            # (the figure already has flat colour from Stage 1 which is opaque).
            self.canvas.ctx.rectangle(0, 0, w, h)
            self.canvas.ctx.set_source(grad)
            self.canvas.ctx.fill()
        else:
            self.canvas.ctx.rectangle(0, 0, w, h)
            self.canvas.ctx.set_source(grad)
            self.canvas.ctx.fill()

        # ── Stage 3: Ink contour lines (keyblock) ─────────────────────────────
        # Thin dark strokes placed along value boundaries, replicating the carved
        # contour lines that give ukiyo-e its graphic clarity.
        print("  Stage 3: ink keyblock contours…")
        rarr   = ref[:, :, :3].astype(np.float32) / 255.0
        lum    = (0.299 * rarr[:,:,0] + 0.587 * rarr[:,:,1]
                  + 0.114 * rarr[:,:,2]).astype(np.float32)
        gx     = ndimage.sobel(lum, axis=1)
        gy     = ndimage.sobel(lum, axis=0)
        # Contour strength map: strong at sharp value edges (lines / silhouettes).
        edge_mag = np.sqrt(gx**2 + gy**2).astype(np.float32)
        if edge_mag.max() > 1e-9:
            edge_mag /= edge_mag.max()

        # Smooth lightly so contour placement isn't hyper-jittery.
        edge_mag = ndimage.gaussian_filter(edge_mag, sigma=contour_thickness * 0.4)

        # Contour strokes respect figure mask if present.
        if self._figure_mask is not None:
            edge_mag = edge_mag * self._figure_mask

        prob = edge_mag.flatten() * contour_weight
        # Also add a small uniform component so every feature region can receive
        # contour lines even if its gradient is very soft (e.g. coloured areas
        # within the figure that share similar value to their neighbours).
        if self._figure_mask is not None:
            uniform = self._figure_mask.flatten() * (1.0 - contour_weight)
        else:
            uniform = np.ones(h * w, dtype=np.float32) * (1.0 - contour_weight)
        prob = prob + uniform
        total = prob.sum()
        if total < 1e-9:
            return
        prob /= total

        # Contour direction: tangent to the edge gradient (perpendicular to normal).
        contour_angles = np.arctan2(gx, -gy)     # follow the contour line direction
        contour_angles = ndimage.gaussian_filter(contour_angles, sigma=2.0)

        # Stroke count proportional to canvas area so large canvases get enough lines.
        n_contour = max(400, int(w * h / 600))

        tip_flat = BrushTip(BrushTip.FLAT, bristle_noise=0.0)
        positions = self._rng_py.choices(range(h * w),
                                          weights=prob.tolist(), k=n_contour)
        ir, ig, ib = ink_color
        margin = max(3, int(contour_thickness * 2))

        for pos in positions:
            py, px = int(pos // w), int(pos % w)
            px = max(margin, min(w - margin, px))
            py = max(margin, min(h - margin, py))

            a  = float(contour_angles[py, px])
            # Short crisp strokes — keyblock lines are typically 10–25px long.
            L  = self._rng_py.uniform(8.0, 22.0)
            start = (px - math.cos(a) * L * 0.5,
                     py - math.sin(a) * L * 0.5)
            n_pts = max(3, int(L / 4))
            pts   = stroke_path(start, a, L, curve=0.0, n=n_pts)
            ws    = [contour_thickness] * len(pts)

            self.canvas.apply_stroke(
                pts, ws, ink_color, tip_flat,
                opacity=0.94, wet_blend=0.0,
                jitter_amt=0.008, rng=self._rng_py,
                region_mask=self._figure_mask,
            )

    def watercolor_wash_pass(self,
                             reference:      Union[np.ndarray, Image.Image],
                             n_washes:       int   = 6,
                             wash_opacity:   float = 0.28,
                             drag_strokes:   int   = 180,
                             drag_size:      float = 22.0,
                             dark_strokes:   int   = 320,
                             dark_opacity:   float = 0.72,
                             paper_threshold: float = 0.82,
                             bloom_prob:     float = 0.18):
        """
        Transparent watercolour technique — inspired by John Singer Sargent.

        Watercolour is fundamentally different from oil: pigment is suspended
        in water and behaves according to the moisture state of the paper.
        There is no white paint — the highest lights are bare paper.  This
        pass replicates the four stages of Sargent's watercolour method:

          Stage 1 — Wet-into-wet foundation washes:
            Large, nearly-transparent sweeps of diluted pigment applied to
            pre-wetted paper.  Colours bleed and merge at their boundaries,
            producing the soft lost-edge quality of sky, water, and shadow
            masses.  Simulated via very large strokes with high wet_blend and
            low opacity.

          Stage 2 — 'Sargent drag' (dry-brush sparkle):
            A heavily-loaded flat brush dragged rapidly across the PEAKS of
            dry rough-surface paper.  The brush skips the hollows, leaving
            channels of bare cream paper that read as sparkling water,
            sunlit foliage, or sunlit stucco.
            Simulated by short, high-opacity flat strokes placed ONLY in
            mid-luminance areas (avoiding the very darkest shadows and the
            reserved bright lights), with a broken-edge quality from
            high bristle_noise in the BrushTip.

          Stage 3 — Hard-edge blooms:
            When a second wet stroke meets the drying edge of an earlier
            wash a backrun forms: the advancing waterfront pushes pigment
            outward, creating a hard 'cauliflower' edge.  Simulated by
            occasionally placing a narrow dark fringe stroke just outside
            a wash boundary (detected from the reference gradient).

          Stage 4 — Dark accent strokes (charged loaded brush):
            The final crisp darks are the last marks placed — a fully-loaded
            brush on dry paper leaves clean, transparent, high-intensity
            colour.  These are the marks that define shadow edges, figure
            outlines, and the deepest recesses.

        Paper preservation:
            Any pixel whose reference luminance exceeds *paper_threshold* is
            left as bare cream paper — NO pigment is placed there.  This is
            the most important rule of watercolour: you cannot paint light
            back once it is covered, so the artist plans and protects the
            white areas from the start.

        Parameters
        ----------
        reference        : PIL Image or ndarray — the target reference.
        n_washes         : Number of large wet-into-wet wash strokes.
                           6–10 is typical; more reads as overworked.
        wash_opacity     : Alpha of each wash stroke (keep low: 0.18–0.35).
        drag_strokes     : Number of 'Sargent drag' dry-brush strokes.
        drag_size        : Width of each drag stroke in pixels.
        dark_strokes     : Number of final dark-accent strokes.
        dark_opacity     : Opacity of dark accent strokes (0.55–0.85).
        paper_threshold  : Luminance above which pixels are left as bare paper.
        bloom_prob       : Probability (0–1) that a wash boundary gets a hard
                          bloom fringe stroke (cauliflower effect).

        Notes
        -----
        Sargent famously said that a watercolour should be finished before the
        first wash dries — speed is everything.  His *Muddy Alligators* (1917)
        and *Santa Maria della Salute* (1904) show a 'Sargent drag' sky
        applied in a single confident pass.

        Famous works to study:
          *Muddy Alligators* (1917) — wet-into-wet + loaded dark strokes.
          *Santa Maria della Salute* (1904) — 'drag' sky, hard blooms on water.
          *Boat Deck, Meteor* (1902) — reserve whites + dark accent calligraphy.
        """
        print(f"Watercolour wash pass  ({n_washes} washes  {drag_strokes} drag  "
              f"{dark_strokes} darks)…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        # ── Luminance map: used throughout for paper-preservation gating ─────────
        lum = (0.299 * rarr[:, :, 0] +
               0.587 * rarr[:, :, 1] +
               0.114 * rarr[:, :, 2])                        # (H, W) in [0, 1]

        # Paper-preservation mask: 0.0 where we must leave bare paper, 1.0 elsewhere.
        # Applied to stroke probability so no pigment lands on the lightest areas.
        paper_mask = (lum < paper_threshold).astype(np.float32)
        paper_mask = ndimage.gaussian_filter(paper_mask, sigma=3.5)  # feather the edge
        paper_mask = np.clip(paper_mask, 0.0, 1.0)

        # Also respect the figure mask if one is loaded.
        effective_mask = paper_mask
        if self._figure_mask is not None:
            effective_mask = paper_mask * self._figure_mask

        # ── Gradient for bloom detection ─────────────────────────────────────────
        gx = ndimage.sobel(lum, axis=1).astype(np.float32)
        gy = ndimage.sobel(lum, axis=0).astype(np.float32)
        grad_mag = np.sqrt(gx ** 2 + gy ** 2)
        if grad_mag.max() > 1e-9:
            grad_mag /= grad_mag.max()

        # ── Stage 1: Wet-into-wet foundation washes ──────────────────────────────
        # Large, very transparent, high-blending strokes that lay in the broad
        # colour and tonal masses.  The wetness allows colours to flow together
        # at their boundaries — this is the 'lost edge' quality of watercolour.
        print("  Stage 1: wet-into-wet washes…")
        tip_filbert = BrushTip(BrushTip.FILBERT, bristle_noise=0.04)

        # Sample from mid-dark regions (avoid bare-paper zones).
        wash_weight = (1.0 - lum) * effective_mask
        wash_total  = wash_weight.sum()
        if wash_total > 1e-9:
            wash_weight /= wash_total
            wash_positions = self.rng.choice(h * w, size=n_washes,
                                             p=wash_weight.flatten(), replace=True)
        else:
            wash_positions = self.rng.integers(0, h * w, size=n_washes)

        wash_stroke_size = min(w, h) * 0.18    # ~18% of the shorter canvas dimension

        for pos in wash_positions:
            py, px = int(pos // w), int(pos % w)
            margin = max(20, int(wash_stroke_size))
            px = int(np.clip(px, margin, w - margin))
            py = int(np.clip(py, margin, h - margin))

            # Colour: sample a patch and take the mean — washes are flat tones.
            pw = max(4, int(wash_stroke_size * 0.3))
            patch = rarr[max(0, py-pw):py+pw+1, max(0, px-pw):px+pw+1, :]
            col   = tuple(float(np.mean(patch[:, :, c])) for c in range(3))
            # Dilute toward white (water lightens pigment in wash state).
            col = tuple(min(1.0, v * 0.85 + 0.15) for v in col)
            col = jitter(col, 0.04, self._rng_py)

            a      = self._rng_py.uniform(0, 2 * math.pi)
            length = wash_stroke_size * self._rng_py.uniform(1.8, 3.5)
            start  = (px - math.cos(a) * length * 0.5,
                      py - math.sin(a) * length * 0.5)
            pts    = stroke_path(start, a, length,
                                 curve=self._rng_py.uniform(-0.08, 0.08),
                                 n=max(5, int(length / 14)))
            ws     = [wash_stroke_size * self._rng_py.uniform(1.0, 2.2)] * len(pts)

            self.canvas.apply_stroke(
                pts, ws, col, tip_filbert,
                opacity=wash_opacity,
                wet_blend=0.68,          # very high: washes bleed into each other
                jitter_amt=0.025,
                rng=self._rng_py,
                region_mask=effective_mask,
            )

            # ── Hard bloom (backrun / cauliflower edge) ───────────────────────
            # Occasionally add a narrow fringe of concentrated pigment along the
            # leading edge of the wash — this is the hard water-mark that forms
            # when a wet stroke dries.  Its colour is a darker, slightly shifted
            # version of the wash colour.
            if self._rng_py.random() < bloom_prob and len(pts) >= 2:
                # Bloom colour: darker, slightly cooler than the parent wash.
                b_col = tuple(max(0.0, v - self._rng_py.uniform(0.08, 0.18))
                              for v in col)
                # Bloom trace runs along the wash boundary: pick the last quarter
                # of the stroke path as the 'leading edge' and draw a thin line.
                split    = max(1, len(pts) * 3 // 4)
                b_pts    = pts[split:]
                b_ws     = [max(1.5, ws[0] * 0.12)] * len(b_pts)
                if len(b_pts) >= 2:
                    self.canvas.apply_stroke(
                        b_pts, b_ws, b_col,
                        BrushTip(BrushTip.FLAT, bristle_noise=0.0),
                        opacity=min(0.85, dark_opacity * 0.70),
                        wet_blend=0.0,       # hard bloom = no wet blending
                        jitter_amt=0.012,
                        rng=self._rng_py,
                        region_mask=effective_mask,
                    )

        # ── Stage 2: Sargent drag (dry-brush sparkle pass) ───────────────────────
        # A loaded flat brush drawn rapidly across the PEAKS of rough dry paper.
        # The bristles skip the hollow valleys of the paper grain, leaving thin
        # channels of bare cream paper that become sparkling light on water, etc.
        # We simulate this with short, fast flat-brush strokes using high bristle_noise
        # placed only in mid-luminance areas (not in the protected lights or the
        # deepest darks).
        print("  Stage 2: Sargent drag…")
        drag_tip = BrushTip(BrushTip.FLAT, bristle_noise=0.18)   # high bristle noise → broken coverage

        # Mid-luminance target: 0.35 ≤ lum < paper_threshold.
        # This is where sunlit texture is: not the deepest shadows, not the paper-white lights.
        drag_mask = ((lum >= 0.32) & (lum < paper_threshold)).astype(np.float32)
        if self._figure_mask is not None:
            drag_mask = drag_mask * self._figure_mask
        drag_weight = drag_mask * (lum - 0.32)     # favour brighter end of the range
        drag_total  = drag_weight.sum()

        if drag_total > 1e-9:
            drag_weight /= drag_total
            drag_positions = self.rng.choice(h * w, size=drag_strokes,
                                              p=drag_weight.flatten(), replace=True)

            for pos in drag_positions:
                py, px = int(pos // w), int(pos % w)
                margin = max(4, int(drag_size))
                px = int(np.clip(px, margin, w - margin))
                py = int(np.clip(py, margin, h - margin))

                # Sample lightened reference colour — drag picks up light pigment.
                col = tuple(float(rarr[py, px, c]) for c in range(3))
                col = tuple(min(1.0, v * 1.12) for v in col)   # slightly lighter
                col = jitter(col, 0.03, self._rng_py)

                # Direction: predominantly horizontal or a gentle diagonal —
                # Sargent worked with confident directional strokes, not random.
                base_angle = self._rng_py.choice([0.0, math.pi / 8, -math.pi / 8,
                                                   math.pi / 6, math.pi * 0.9])
                a      = base_angle + self._rng_py.uniform(-0.12, 0.12)
                length = drag_size * self._rng_py.uniform(2.5, 5.0)   # long confident stroke
                start  = (px - math.cos(a) * length * 0.5,
                          py - math.sin(a) * length * 0.5)
                pts    = stroke_path(start, a, length, curve=0.0,
                                     n=max(4, int(length / 8)))
                ws     = [drag_size * self._rng_py.uniform(0.8, 1.4)] * len(pts)

                self.canvas.apply_stroke(
                    pts, ws, col, drag_tip,
                    opacity=0.55,       # moderate — drag is not fully opaque
                    wet_blend=0.04,     # nearly dry surface — almost no blending
                    jitter_amt=0.025,
                    rng=self._rng_py,
                    region_mask=effective_mask,
                )

        # ── Stage 3: Dark accent strokes (loaded charged brush on dry paper) ─────
        # The final crisp darks are placed last on completely dry paper.  A
        # fully-loaded brush on dry paper gives transparent, luminous, clean
        # dark marks — much more vivid than overworking wet-into-wet.
        # These define shadow edges, cast shadows, and the deepest recesses.
        print("  Stage 3: dark accent strokes…")
        tip_round = BrushTip(BrushTip.ROUND, bristle_noise=0.02)

        dark_weight = (1.0 - lum) ** 2.5          # strongly prefer the darkest areas
        dark_weight *= effective_mask
        dark_weight += grad_mag * effective_mask * 0.4   # and value edges
        dark_weight  = dark_weight.flatten()
        dark_total   = dark_weight.sum()

        if dark_total > 1e-9:
            dark_weight /= dark_total
            dark_positions = self.rng.choice(h * w, size=dark_strokes,
                                              p=dark_weight, replace=True)

            angles = flow_field(rarr)   # strokes follow the colour contour
            dark_size = max(3.0, drag_size * 0.30)   # smaller, crisper than washes

            for pos in dark_positions:
                py, px = int(pos // w), int(pos % w)
                margin = max(4, int(dark_size * 2))
                px = int(np.clip(px, margin, w - margin))
                py = int(np.clip(py, margin, h - margin))

                col = tuple(float(rarr[py, px, c]) for c in range(3))
                # Darken the sampled colour — loaded pigment on dry paper is deep
                # and transparent.  The colour is rich, not muddy: multiply lightly.
                col = tuple(max(0.0, v * 0.75) for v in col)
                col = jitter(col, 0.02, self._rng_py)

                a      = float(angles[py, px]) + self._rng_py.uniform(-0.25, 0.25)
                length = dark_size * self._rng_py.uniform(2.0, 5.0)
                start  = (px - math.cos(a) * length * 0.5,
                          py - math.sin(a) * length * 0.5)
                pts    = stroke_path(start, a, length,
                                     curve=self._rng_py.uniform(-0.08, 0.08),
                                     n=max(3, int(length / 5)))
                ws     = [dark_size * self._rng_py.uniform(0.6, 1.2)] * len(pts)

                self.canvas.apply_stroke(
                    pts, ws, col, tip_round,
                    opacity=dark_opacity,
                    wet_blend=0.03,     # dry surface — no blending
                    jitter_amt=0.018,
                    rng=self._rng_py,
                    region_mask=effective_mask,
                )

    def flat_plane_pass(self,
                        reference:       Union[np.ndarray, Image.Image],
                        n_planes:        int   = 5,
                        strokes_per_plane: int = 500,
                        stroke_size:     float = 11.0,
                        plane_opacity:   float = 0.80,
                        border_strokes:  int   = 300,
                        border_size:     float = 4.0,
                        border_opacity:  float = 0.88,
                        black_color:     Color = (0.06, 0.05, 0.06),
                        wet_blend:       float = 0.12):
        """
        Flat value-plane pass — inspired by Édouard Manet.

        Manet's revolutionary technique broke with academic chiaroscuro by
        rendering forms as a small number of discrete tonal planes separated
        by visible (but not hard) boundaries.  Where a Renaissance painter
        would smoothly graduate from highlight to shadow through hundreds of
        nuanced mid-tones, Manet laid down 3–5 flat patches of colour and
        left the boundary visible.  Olympia (1863) looks like a playing card
        at arm's length — and that flatness is the radical act.

        Algorithm
        ---------
        1. **Value quantisation** — Convert the reference to luminance.
           Cluster pixels into ``n_planes`` tonal bands (darkest to lightest)
           using evenly-spaced luminance thresholds.

        2. **Flat stroke patches** — For each band, sample random pixels
           inside that band and paint broad, nearly-flat strokes using the
           reference colour at that pixel.  Very low wet_blend keeps each
           patch from bleeding into adjacent bands (the 'mosaic' quality).

        3. **Plane-boundary dark strokes** — Detect the luminance gradient
           (edges between planes) and lay short, bold dark strokes along
           those edges.  Manet's characteristic border mark: a loaded flat
           brush pulled swiftly along the shadow side of a form.  Black is
           used as a pure chromatic colour here, not a neutral shadow mixer.

        Parameters
        ----------
        reference        : PIL Image or ndarray
        n_planes         : Number of tonal value bands (4–6 gives best results).
                           Too many → approaches normal painting; too few →
                           posterised / woodblock feel.
        strokes_per_plane: Broad flat strokes per tonal band.
        stroke_size      : Width of the flat plane strokes in pixels.
        plane_opacity    : Opacity of each flat stroke (high = decisive, loaded).
        border_strokes   : Short dark strokes placed at plane boundaries.
        border_size      : Width of the dark border strokes.
        border_opacity   : Opacity of the border strokes (deliberately high —
                           Manet's borders are confident, not timid).
        black_color      : The rich black used for border and shadow strokes.
                           Manet used black as a chromatic value, not merely
                           shadow — so this is a warm-neutral near-black, not
                           (0, 0, 0).
        wet_blend        : Within-plane wet blending.  Keep very low (0.10–0.20)
                           so patches stay flat.  Manet's whole point is the
                           absence of smooth gradients between planes.
        """
        print(f"Flat plane pass  ({n_planes} planes  {strokes_per_plane} strokes/plane)…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        tip_flat  = BrushTip(BrushTip.FLAT)
        tip_round = BrushTip(BrushTip.ROUND)

        # ── 1. Luminance map and plane thresholds ─────────────────────────────
        # Manet's cool-biased palette: weight luminance toward the green channel
        # (standard photometric) but suppress the red channel slightly so warm
        # tones read a touch darker — matching his silvery cool half-tones.
        lum = (0.28 * rarr[:, :, 0] +
               0.60 * rarr[:, :, 1] +
               0.12 * rarr[:, :, 2]).astype(np.float32)

        thresholds = [i / n_planes for i in range(1, n_planes)]

        # ── 2. Flat stroke patches per tonal band ─────────────────────────────
        for plane_idx in range(n_planes):
            lo = 0.0          if plane_idx == 0            else thresholds[plane_idx - 1]
            hi = 1.001        if plane_idx == n_planes - 1 else thresholds[plane_idx]

            plane_mask_bool = (lum >= lo) & (lum < hi)
            candidate_ys, candidate_xs = np.where(plane_mask_bool)
            if len(candidate_ys) == 0:
                continue

            # Apply figure mask if available — prefer painting the figure first,
            # then background (matches Manet's process: figure block-in, then bg).
            if self._figure_mask is not None:
                fig_vals = self._figure_mask[candidate_ys, candidate_xs]
                # Prefer figure pixels (high mask weight) — sample with weighting
                probs = 0.3 + 0.7 * fig_vals
                probs = probs / probs.sum()
            else:
                probs = None

            # Per plane, lay strokes sampling broadly across that tonal band.
            n_here = min(strokes_per_plane, len(candidate_ys))
            chosen = self.rng.choice(len(candidate_ys), size=n_here,
                                         replace=len(candidate_ys) < n_here,
                                         p=probs)

            for idx in chosen:
                py, px = int(candidate_ys[idx]), int(candidate_xs[idx])
                col = tuple(float(rarr[py, px, c]) for c in range(3))

                # Manet's key: cool silver in mid-tones, not warm brown.
                # Slightly desaturate mid-tones and nudge them cool.
                t_plane = plane_idx / max(n_planes - 1, 1)   # 0=dark, 1=light
                is_midtone = 0.25 < t_plane < 0.75
                if is_midtone:
                    col = temp_shift(col, warmth=-0.4)

                col = jitter(col, 0.028, self._rng_py)

                # Stroke direction: roughly horizontal for the torso/background
                # (Manet's confident loaded flat-brush sweep), with slight
                # individual variation.  This produces the visible planar
                # quality — strokes have direction, not random noise.
                base_angle = 0.0   # horizontal (flat drag)
                if plane_idx < n_planes // 2:
                    # Darker planes: slightly diagonal toward lower-left —
                    # Manet's shadow-side strokes have a deliberate lean.
                    base_angle = math.radians(20.0)
                a = base_angle + self._rng_py.uniform(-0.35, 0.35)

                # Broad strokes: length 2.5–5× width for a 'loaded sweep' look
                length = stroke_size * self._rng_py.uniform(2.5, 5.0)
                start  = (px - math.cos(a) * length * 0.5,
                          py - math.sin(a) * length * 0.5)
                pts    = stroke_path(start, a, length,
                                     curve=self._rng_py.uniform(-0.04, 0.04),
                                     n=max(3, int(length / 6)))
                ws     = [stroke_size * self._rng_py.uniform(0.85, 1.15)] * len(pts)

                self.canvas.apply_stroke(
                    pts, ws, col, tip_flat,
                    opacity=plane_opacity * self._rng_py.uniform(0.85, 1.0),
                    wet_blend=wet_blend,
                    jitter_amt=0.018,
                    rng=self._rng_py,
                    region_mask=self._figure_mask,
                )

        # ── 3. Plane-boundary dark strokes ────────────────────────────────────
        # Detect luminance gradients — high gradient = boundary between planes.
        # Manet placed short, bold, dark strokes (often black) right at these
        # boundaries — the most distinctive mark of his style.
        grad_y = ndimage.sobel(lum, axis=0)
        grad_x = ndimage.sobel(lum, axis=1)
        grad_mag = np.hypot(grad_x, grad_y).astype(np.float32)
        grad_mag /= (grad_mag.max() + 1e-9)

        # Threshold: only paint at genuine plane boundaries
        boundary_mask = grad_mag > 0.18
        bys, bxs = np.where(boundary_mask)
        if len(bys) > 0:
            n_border = min(border_strokes, len(bys))
            b_chosen = self.rng.choice(len(bys), size=n_border, replace=False)

            for idx in b_chosen:
                py, px = int(bys[idx]), int(bxs[idx])

                # Dark colour: Manet's black — warm-neutral, not absolute.
                # In the lightest areas add a hint of the local colour so the
                # shadow stroke is 'coloured dark' rather than dead grey.
                if lum[py, px] > 0.65:
                    local = tuple(float(rarr[py, px, c]) for c in range(3))
                    # Darken local by blending with black 70:30
                    col = mix_paint(local, black_color, 0.70)
                else:
                    col = jitter(black_color, 0.015, self._rng_py)

                # Stroke direction: follow the gradient direction (perpendicular
                # to the edge, into the darker side) — matching how Manet's
                # loaded brush draws across the shadow side of a form boundary.
                gx = float(grad_x[py, px])
                gy = float(grad_y[py, px])
                mag = math.sqrt(gx * gx + gy * gy) or 1.0
                # Perpendicular to gradient = along the edge
                a = math.atan2(gx / mag, -(gy / mag))
                a += self._rng_py.uniform(-0.30, 0.30)

                length = border_size * self._rng_py.uniform(3.0, 7.0)
                start  = (px - math.cos(a) * length * 0.5,
                          py - math.sin(a) * length * 0.5)
                pts    = stroke_path(start, a, length, curve=0.0,
                                     n=max(2, int(length / 5)))
                ws     = [border_size * self._rng_py.uniform(0.8, 1.2)] * len(pts)

                self.canvas.apply_stroke(
                    pts, ws, col, tip_flat,
                    opacity=border_opacity * self._rng_py.uniform(0.75, 1.0),
                    wet_blend=0.04,     # very dry — Manet's dark accents don't bleed
                    jitter_amt=0.012,
                    rng=self._rng_py,
                    region_mask=None,   # border strokes cross figure/background boundary
                )

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

    def dark_void_pass(self,
                       reference:       Union[np.ndarray, Image.Image],
                       void_darkness:   float = 0.96,
                       n_strokes:       int   = 600,
                       stroke_size:     float = 16,
                       flesh_color:     Color = (0.68, 0.55, 0.35),
                       accent_color:    Color = (0.72, 0.18, 0.08),
                       accent_prob:     float = 0.08,
                       void_depth:      float = 0.80):
        """
        Pinturas Negras (Black Paintings) technique — inspired by Francisco Goya.

        Goya painted his Black Paintings directly onto the plaster walls of his
        Quinta del Sordo between 1819–1823, aged 73–75, deaf, and living in
        voluntary isolation.  *Saturn Devouring His Son*, *The Dog*, *Witches'
        Sabbath* — these works share a single visual strategy: near-black void
        surrounding barely-resolved figures.

        The technique:
          1. **Void ground** — the background is deepened to near-black by
             compositing a dark screen over background pixels. The figure is
             the only light source in a universe of darkness.
          2. **Crude figure strokes** — applied with a spatula and stiff brush;
             no wet blending, no refinement. Forms emerge from the dark only
             enough to be horrifying.  Ashen ochre and charred umber predominate.
          3. **Blood accent** — a single small intense stroke of blood-red or
             bone-white carries extraordinary weight against the surrounding void.
             Goya used this with surgical restraint.
          4. **Void encroachment** — dark strokes are placed even in figure areas
             near the edges, letting the void bleed into and consume the figure.
             This creates the sensation of figures dissolving rather than standing.

        Parameters
        ----------
        reference    : PIL Image or ndarray reference.
        void_darkness: Opacity of the black void overlay on background (0–1).
                       0.90–0.96 gives the characteristic impenetrable black.
        n_strokes    : Number of figure strokes.  Goya used fewer, larger marks
                       than conventional painters — 400–700 is appropriate.
        stroke_size  : Base width of strokes in pixels.  Keep large (12–20px) —
                       these are spatula marks, not fine brushwork.
        flesh_color  : Ashen ochre-grey used for figure flesh and mid-tones.
        accent_color : Blood red (or pale ash) used for the single hot accent.
        accent_prob  : Probability (0–1) that a stroke is placed in the accent
                       color rather than the flesh/umber range. Keep very low
                       (0.05–0.12) — Goya's restraint is part of the effect.
        void_depth   : Fraction of background pixels that receive additional
                       dark strokes (encroachment into the figure's territory).
        """
        print(f"Dark void pass  ({n_strokes} strokes  size={stroke_size:.0f}px"
              f"  void={void_darkness:.2f})…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        # ── Stage 1: Void the background ─────────────────────────────────────
        # Overlay pure near-black on all non-figure pixels.
        # This replicates Goya's black ground — the wall plaster was dark before
        # he began, and background areas received no light-valued paint at all.
        print("  Voiding background…")
        void_color = (0.02, 0.015, 0.008)   # near-black with a faint warm cast

        ctx = self.canvas.ctx
        if self._figure_mask is not None:
            # Background mask as a soft numpy field
            bg = np.clip(1.0 - self._figure_mask, 0.0, 1.0)
            # Read current canvas buffer
            buf = np.frombuffer(self.canvas.surface.get_data(),
                                dtype=np.uint8).reshape(h, w, 4).copy()
            carr = buf[:, :, [2, 1, 0]].astype(np.float32) / 255.0  # RGB

            # Blend toward void using the mask
            for c_idx, v in enumerate(void_color):
                src_ch = carr[:, :, c_idx]
                carr[:, :, c_idx] = src_ch * (1.0 - bg * void_darkness) + v * (bg * void_darkness)

            # Write back — Cairo BGRA
            buf[:, :, 2] = np.clip(carr[:, :, 0] * 255, 0, 255).astype(np.uint8)
            buf[:, :, 1] = np.clip(carr[:, :, 1] * 255, 0, 255).astype(np.uint8)
            buf[:, :, 0] = np.clip(carr[:, :, 2] * 255, 0, 255).astype(np.uint8)
            buf[:, :, 3] = 255
            tmp = cairo.ImageSurface.create_for_data(
                bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
            ctx.set_source_surface(tmp, 0, 0)
            ctx.paint()
        else:
            # No mask: darken the whole canvas (full-void approach)
            ctx.set_source_rgba(*void_color, void_darkness * 0.5)
            ctx.rectangle(0, 0, w, h)
            ctx.fill()

        # ── Stage 2: Crude figure strokes ────────────────────────────────────
        # Ashen, umber, and occasional blood-red strokes on the figure.
        # Error-driven sampling ensures strokes go where the reference differs
        # most from the dark canvas — i.e., where the figure should be.
        print(f"  Figure strokes ({n_strokes})…")

        cbuf = np.frombuffer(self.canvas.surface.get_data(),
                             dtype=np.uint8).reshape(h, w, 4).copy()
        carr = cbuf[:, :, [2, 1, 0]].astype(np.float32) / 255.0
        err  = np.mean(np.abs(carr - rarr), axis=2).astype(np.float32)
        err  = ndimage.gaussian_filter(err, sigma=stroke_size * 0.5)

        region = self._figure_mask
        if region is not None:
            err = err * region

        err_flat = err.flatten()
        total    = err_flat.sum()
        if total < 1e-9:
            prob = np.ones(h * w, dtype=np.float32) / (h * w)
        else:
            prob = err_flat / total

        positions = self.rng.choice(h * w, size=n_strokes, p=prob, replace=True)
        tip_flat  = BrushTip(BrushTip.FLAT, bristle_noise=0.25)  # crude, bristled
        self.canvas.dry(1.0)

        angles = flow_field(rarr)   # gradient-based angles

        for pos in positions:
            py, px = int(pos // w), int(pos % w)
            margin = max(int(stroke_size) + 2, 4)
            px = int(np.clip(px, margin, w - margin))
            py = int(np.clip(py, margin, h - margin))

            # Goya's colour choice: almost always ashen ochre/umber unless the
            # accent_prob dice roll fires.
            if self._rng_py.random() < accent_prob:
                col = accent_color
            else:
                # Reference-sampled colour crushed toward ashen flesh palette
                ref_col = tuple(float(rarr[py, px, c]) for c in range(3))
                # Lerp toward flesh_color (50/50): makes everything read more ashen
                col = mix_paint(ref_col, flesh_color, 0.55)

            col = jitter(col, 0.06, self._rng_py)

            a = float(angles[py, px]) + self._rng_py.uniform(-0.4, 0.4)  # crude angle jitter
            length = stroke_size * self._rng_py.uniform(1.5, 3.5)
            start  = (px - math.cos(a) * length * 0.5,
                      py - math.sin(a) * length * 0.5)
            pts = stroke_path(start, a, length,
                              curve=self._rng_py.uniform(-0.12, 0.12),
                              n=max(3, int(length / 4)))
            ws  = [stroke_size * self._rng_py.uniform(0.6, 1.3)] * len(pts)

            self.canvas.apply_stroke(pts, ws, col, tip_flat,
                                     opacity=self._rng_py.uniform(0.65, 0.92),
                                     wet_blend=0.08,   # near-zero blending — crude
                                     jitter_amt=0.05, rng=self._rng_py,
                                     region_mask=region)

        # ── Stage 3: Void encroachment ────────────────────────────────────────
        # Dark strokes placed near the figure's silhouette edge consume parts
        # of the figure, replicating how Goya's figures dissolve into blackness.
        if self._figure_mask is not None and void_depth > 0.0:
            print("  Void encroachment…")
            # Edge zone: where figure mask transitions from 1→0
            edge_zone = ndimage.gaussian_filter(self._figure_mask, sigma=stroke_size * 0.8)
            edge_zone = np.clip(self._figure_mask - edge_zone * 0.55, 0.0, 1.0)
            edge_zone *= void_depth

            edge_flat = edge_zone.flatten()
            total_e   = edge_flat.sum()
            if total_e > 1e-9:
                n_edge    = max(50, n_strokes // 5)
                prob_e    = edge_flat / total_e
                edge_pos  = self.rng.choice(h * w, size=n_edge, p=prob_e, replace=True)

                for pos in edge_pos:
                    py, px = int(pos // w), int(pos % w)
                    margin = max(int(stroke_size) + 2, 4)
                    px = int(np.clip(px, margin, w - margin))
                    py = int(np.clip(py, margin, h - margin))

                    # Very dark — almost void colour, with a faint umber warmth
                    col = jitter(void_color, 0.04, self._rng_py)
                    a   = self._rng_py.uniform(0, math.pi * 2)
                    length = stroke_size * self._rng_py.uniform(1.0, 2.0)
                    start  = (px - math.cos(a) * length * 0.5,
                              py - math.sin(a) * length * 0.5)
                    pts = stroke_path(start, a, length, curve=0.0,
                                      n=max(2, int(length / 6)))
                    ws  = [stroke_size * 0.7] * len(pts)

                    self.canvas.apply_stroke(pts, ws, col, tip_flat,
                                             opacity=self._rng_py.uniform(0.55, 0.85),
                                             wet_blend=0.05,
                                             jitter_amt=0.03, rng=self._rng_py,
                                             region_mask=None)  # allow crossing boundary

    def sfumato_veil_pass(self,
                          reference:     Union[np.ndarray, Image.Image],
                          n_veils:       int   = 7,
                          blur_radius:   float = 12.0,
                          warmth:        float = 0.35,
                          veil_opacity:  float = 0.08,
                          edge_only:     bool  = True,
                          chroma_dampen: float = 0.18):
        """
        Sfumato veil — improved Renaissance edge-softening technique.

        Named after Leonardo da Vinci's term 'sfumato' (from *sfumare*,
        'to evaporate like smoke'), this pass simulates the imperceptible
        transitions between light and shadow that are the hallmark of
        Leonardo's portrait technique.

        **Improvement over naive edge-softness:**
        Previous sessions approximated sfumato by reducing edge_softness in
        stroke_params.  This pass provides a physically motivated simulation:
        multiple thin, warm, blurred semi-transparent glazes are composited
        over the edge zone only, replicating how Leonardo built up sfumato
        through 30–40 imperceptible layers of oil glaze with fingertip
        blending.

        Technique:
          1. Detect the edge zone — where luminance gradient is above a
             threshold (form boundaries, transitions between light and shadow).
          2. Generate a blurred, warm-tinted version of the reference at
             each edge pixel.
          3. Composite n_veils thin copies at progressively larger blur
             radii, so the final result has a gentle gradient of haziness
             that increases away from the lit surface.

        The result: edges do not simply become soft (a smear) — they become
        *atmospheric*, as if seen through a thin curtain of warm smoke.
        Form is still readable; the boundary simply ceases to be findable.

        Parameters
        ----------
        reference    : PIL Image or ndarray — the reference to draw from.
        n_veils      : Number of glaze layers.  7–12 gives best results;
                       fewer looks too abrupt, more reads as out-of-focus.
        blur_radius  : Gaussian sigma for the initial blur, in pixels.
                       Final veil uses blur_radius * 2.0 (grows outward).
        warmth       : Warm tint strength (0 = neutral, 1 = full amber glaze).
                       Leonardo used a warm amber sfumato that shifts flesh
                       tones toward golden ochre at the edges.
        veil_opacity  : Alpha per veil layer.  Keep very low (0.04–0.12) —
                        the veils accumulate across n_veils layers.
        edge_only     : If True (default), veils are masked to the gradient
                        edge zone only — form interiors are not hazed, matching
                        Leonardo's selective sfumato. If False, applies globally.
        chroma_dampen : Chromatic desaturation at the edge zone (0 = no dampening,
                        1 = full greyscale).  Leonardo's sfumato zones are not
                        merely blurred — they are also slightly desaturated, as if
                        seen through thin warm smoke.  A value of 0.15–0.25 gives
                        the subtle grey-amber edge quality visible under X-ray at
                        the mouth corners of the Mona Lisa.  Applied per-veil so
                        outer veils are more desaturated than inner ones.

        Notes
        -----
        *Mona Lisa* (Louvre) shows sfumato most clearly at the corners of
        the mouth and eyes — precisely where expression is ambiguous.
        Leonardo never resolved these areas; the ambiguity is the technique.

        X-ray and infrared reflectography reveal up to 30 distinct glaze
        layers in the sfumato zones, each individually invisible.  The zones
        are also slightly desaturated relative to adjacent flesh areas — a
        quality missed by blur-only approximations.  chroma_dampen replicates
        this.
        """
        print(f"Sfumato veil pass  ({n_veils} veils  blur={blur_radius:.1f}px"
              f"  warmth={warmth:.2f}  chroma_dampen={chroma_dampen:.2f})…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        # ── Warm the reference toward amber (Leonardo's characteristic tone) ──
        # The sfumato is not a neutral grey haze but a warm golden one —
        # Leonardo used lead white + raw umber + a touch of red ochre in his glaze.
        amber = (0.80, 0.62, 0.35)
        warmed = np.zeros_like(rarr)
        for c in range(3):
            warmed[:, :, c] = rarr[:, :, c] * (1.0 - warmth) + amber[c] * warmth

        # ── Edge zone mask ────────────────────────────────────────────────────
        lum = (0.299 * rarr[:, :, 0] + 0.587 * rarr[:, :, 1] + 0.114 * rarr[:, :, 2])
        gx  = ndimage.sobel(lum, axis=1).astype(np.float32)
        gy  = ndimage.sobel(lum, axis=0).astype(np.float32)
        grad_mag = np.sqrt(gx ** 2 + gy ** 2)
        if grad_mag.max() > 1e-9:
            grad_mag /= grad_mag.max()

        if edge_only:
            # Expand the gradient edge zone with a Gaussian so the sfumato
            # covers a band around form boundaries, not just the 1-pixel edge.
            edge_mask = ndimage.gaussian_filter(
                grad_mag.astype(np.float32), sigma=blur_radius * 0.7)
            edge_mask = np.clip(edge_mask * 3.5, 0.0, 1.0)
            # Also apply figure mask if available
            if self._figure_mask is not None:
                edge_mask = edge_mask * self._figure_mask
        else:
            if self._figure_mask is not None:
                edge_mask = self._figure_mask.copy()
            else:
                edge_mask = np.ones((h, w), dtype=np.float32)

        # ── Multi-veil accumulation ───────────────────────────────────────────
        # Each veil: blur the warmed reference at a slightly larger radius,
        # weight by the edge mask, and composite at veil_opacity.
        ctx = self.canvas.ctx

        for i in range(n_veils):
            t = (i + 1) / n_veils                      # 0→1 across veil sequence
            sigma = blur_radius * (0.5 + t * 1.5)      # grows from small to large
            veil_warmth = warmth * (0.6 + 0.4 * t)     # warmer in outer veils

            # Re-warm each veil individually (outer veils are warmer / more golden)
            veil_ref = np.zeros_like(rarr)
            for c in range(3):
                veil_ref[:, :, c] = (rarr[:, :, c] * (1.0 - veil_warmth)
                                     + amber[c] * veil_warmth)

            # Chromatic dampening — outer veils are progressively desaturated so
            # the edge zone acquires a warm grey-amber quality (Leonardo's edges
            # under X-ray).  Desaturate by blending toward luminance-grey before
            # blurring so the effect is spatially coherent, not just an HSV shift.
            if chroma_dampen > 0.0:
                dampen_t = chroma_dampen * t   # ramps from 0 at first veil to full
                lum_veil = (0.299 * veil_ref[:, :, 0]
                            + 0.587 * veil_ref[:, :, 1]
                            + 0.114 * veil_ref[:, :, 2])
                for c in range(3):
                    veil_ref[:, :, c] = (veil_ref[:, :, c] * (1.0 - dampen_t)
                                         + lum_veil * dampen_t)

            # Gaussian blur to create the smoke effect
            blurred = np.stack([
                ndimage.gaussian_filter(veil_ref[:, :, c].astype(np.float32), sigma=sigma)
                for c in range(3)
            ], axis=2)

            # Composite: only where edge_mask is active
            alpha = edge_mask * veil_opacity            # (H, W) float

            # Build an ARGB32 Cairo surface for this veil.
            # IMPORTANT: Cairo's FORMAT_ARGB32 uses PREMULTIPLIED alpha.
            # Each channel must be multiplied by alpha before storing, or Cairo
            # will composite the raw (full-brightness) RGB values as if they were
            # already premultiplied, producing severe over-brightening at edges.
            alpha_3ch = alpha[:, :, np.newaxis]          # (H, W, 1) for broadcast
            premul_rgb = blurred * alpha_3ch              # (H, W, 3) premultiplied

            veil_rgba = np.zeros((h, w, 4), dtype=np.uint8)
            veil_rgba[:, :, 0] = np.clip(premul_rgb[:, :, 2] * 255, 0, 255).astype(np.uint8)  # B premul
            veil_rgba[:, :, 1] = np.clip(premul_rgb[:, :, 1] * 255, 0, 255).astype(np.uint8)  # G premul
            veil_rgba[:, :, 2] = np.clip(premul_rgb[:, :, 0] * 255, 0, 255).astype(np.uint8)  # R premul
            veil_rgba[:, :, 3] = np.clip(alpha * 255, 0, 255).astype(np.uint8)                 # A

            veil_surf = cairo.ImageSurface.create_for_data(
                bytearray(veil_rgba.tobytes()), cairo.FORMAT_ARGB32, w, h)
            ctx.set_source_surface(veil_surf, 0, 0)
            ctx.paint()   # alpha is premultiplied into R/G/B

        print(f"  Sfumato complete ({n_veils} veils accumulated).")

    def angular_contour_pass(self,
                             reference:           Union[np.ndarray, Image.Image],
                             n_flat_strokes:      int   = 800,
                             flat_stroke_size:    float = 10.0,
                             n_contour_strokes:   int   = 1600,
                             contour_thickness:   float = 2.8,
                             contour_color:       Color = (0.12, 0.07, 0.04),
                             flesh_desaturation:  float = 0.40,
                             flesh_green_shift:   float = 0.12,
                             accent_color:        Color = (0.70, 0.12, 0.04),
                             accent_prob:         float = 0.06):
        """
        Viennese Expressionist contour pass — inspired by Egon Schiele.

        Schiele's drawings and gouaches are immediately recognisable by their
        violent, fractured contour line.  He drew with a reed pen or fine brush
        and pressed hard at joints, knuckles, and collar-bones where the anatomy
        is most exposed — the line swells, then almost vanishes between significant
        points.  The interior of the figure is filled with flat, barely-modelled
        patches of pale, slightly sickly flesh (often pulled toward yellow-green
        rather than warm pink), against a near-bare paper void.

        This pass has three sub-stages:

          Stage 1 — Flat interior fill:
            The figure interior is painted with short, flat, low-wet-blend strokes
            in slightly desaturated, greenish-shifted flesh tones.  Two brightness
            zones: lighter (lit surfaces) and darker (shadowed planes).  Very little
            wet blending — patches stay distinct, like gouache on dry paper.

          Stage 2 — Angular contour lines:
            Sobel edge detection locates all structural boundaries (silhouette,
            limb separations, form edges).  Short (10–30px) line segments are
            placed along these edges, each deliberately offset in angle from its
            neighbour by a small random amount.  This creates the fractured,
            re-starting quality of Schiele's mark — the line breaks, skips, then
            re-attacks.  At points of high edge magnitude (strong boundaries, joints)
            strokes are wider and more opaque.  At low-magnitude edges the line
            thins and fades.

          Stage 3 — Sparse blood-red accent:
            A small number of strokes in a warm blood-red or deep sienna accent are
            placed at the highest-gradient edge points — replicating Schiele's
            precise use of a single vivid accent to intensify the most psychologically
            loaded part of the composition (usually a hand, face, or collar).

        Parameters
        ----------
        reference           : PIL Image or ndarray.
        n_flat_strokes      : Number of interior flat-fill strokes.
        flat_stroke_size    : Width of the flat interior fill strokes in pixels.
        n_contour_strokes   : Number of angular contour line segments.
        contour_thickness   : Base width of contour lines in pixels.
                              Actual width varies ±50% per stroke to simulate
                              pressure variation on the reed pen.
        contour_color       : Near-black warm ink colour used for contour lines.
                              Schiele's lines were warm dark sienna-black, not a
                              neutral grey or cold blue-black.
        flesh_desaturation  : Fraction [0–1] by which the reference colour is
                              pulled toward grey before placing interior strokes.
                              0.30–0.50 gives the characteristically pallid look.
        flesh_green_shift   : Amount by which the flesh mid-tones are shifted
                              toward green (Schiele's jaundiced shadow planes).
                              Applied only to mid-luminance pixels (0.35–0.65 lum).
        accent_color        : Blood-red or hot sienna used for accent strokes.
        accent_prob         : Probability that a high-edge-strength contour stroke
                              is placed in the accent colour rather than near-black.
                              Keep very low (0.04–0.08) — Schiele's restraint is key.

        Notes
        -----
        Schiele died of Spanish flu in 1918, aged 28.  His entire known output
        spans only eleven years (1907–1918), yet he produced around 3,000 works
        on paper and 330 oil paintings.  The contour line was his primary instrument
        — even his oils read as drawings with colour added.

        Famous works to study:
          *Self-Portrait with Physalis* (1912) — pure angular contour + pale fill.
          *Death and the Maiden* (1915) — two figures dissolving into each other;
            the contour line becomes an embrace and a fracture simultaneously.
          *Seated Couple* (1915) — two figures locked together; limb boundaries
            drawn with multiple overlapping angular short strokes.
        """
        print(f"Angular contour pass  ({n_flat_strokes} fill  {n_contour_strokes} contour"
              f"  thick={contour_thickness:.1f}px)…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        # ── Luminance map (used throughout) ───────────────────────────────────
        lum = (0.299 * rarr[:, :, 0] +
               0.587 * rarr[:, :, 1] +
               0.114 * rarr[:, :, 2]).astype(np.float32)

        # ── Stage 1: Flat interior fill ───────────────────────────────────────
        # Schiele's interiors are flat, dry, barely blended.  Split into two
        # tonal zones: lit (lum ≥ 0.45) and shadowed (lum < 0.45).  Each zone
        # gets flat strokes with desaturated, slightly green-shifted colour.
        print("  Stage 1: flat interior fill…")

        # Desaturation helper: pull colour toward grey, then optionally green-shift
        def _schiele_flesh(col: tuple, pix_lum: float) -> tuple:
            """Apply Schiele's characteristic flesh treatment to a sampled colour."""
            r, g, b = col
            # Desaturate: lerp toward luminance grey
            grey = pix_lum
            r = r * (1.0 - flesh_desaturation) + grey * flesh_desaturation
            g = g * (1.0 - flesh_desaturation) + grey * flesh_desaturation
            b = b * (1.0 - flesh_desaturation) + grey * flesh_desaturation
            # Green shift in mid-tones (the sickly shadow planes)
            if 0.30 < pix_lum < 0.65:
                g = min(1.0, g + flesh_green_shift * (1.0 - abs(pix_lum - 0.475) / 0.175))
                r = max(0.0, r - flesh_green_shift * 0.35)
            return (r, g, b)

        tip_flat = BrushTip(BrushTip.FLAT, bristle_noise=0.03)
        region = self._figure_mask

        # Build sampling distribution: error-weighted within figure mask
        cbuf = np.frombuffer(self.canvas.surface.get_data(),
                             dtype=np.uint8).reshape(h, w, 4).copy()
        carr = cbuf[:, :, [2, 1, 0]].astype(np.float32) / 255.0
        err  = np.mean(np.abs(carr - rarr), axis=2).astype(np.float32)
        err  = ndimage.gaussian_filter(err, sigma=flat_stroke_size * 0.4)
        if region is not None:
            err = err * region
        err_total = err.flatten().sum()
        if err_total < 1e-9:
            prob_flat = (region.flatten() if region is not None
                         else np.ones(h * w, dtype=np.float32) / (h * w))
        else:
            prob_flat = err.flatten() / err_total

        positions = self.rng.choice(h * w, size=n_flat_strokes, p=prob_flat, replace=True)
        angles_bg = flow_field(rarr)   # follow colour contours for flat patches

        for pos in positions:
            py, px = int(pos // w), int(pos % w)
            margin = max(5, int(flat_stroke_size * 1.5))
            px = int(np.clip(px, margin, w - margin))
            py = int(np.clip(py, margin, h - margin))

            col = tuple(float(rarr[py, px, c]) for c in range(3))
            col = _schiele_flesh(col, float(lum[py, px]))
            col = jitter(col, 0.022, self._rng_py)

            # Flat strokes follow the image gradient (contours), with wide
            # confident sweeps rather than following form curvature.
            a = float(angles_bg[py, px]) + self._rng_py.uniform(-0.35, 0.35)
            L = flat_stroke_size * self._rng_py.uniform(2.0, 4.5)
            start = (px - math.cos(a) * L * 0.5,
                     py - math.sin(a) * L * 0.5)
            pts = stroke_path(start, a, L, curve=0.0,
                               n=max(3, int(L / 6)))
            ws = [flat_stroke_size * self._rng_py.uniform(0.7, 1.3)] * len(pts)

            self.canvas.apply_stroke(
                pts, ws, col, tip_flat,
                opacity=0.76,
                wet_blend=0.04,       # near-dry — no blending between patches
                jitter_amt=0.018,
                rng=self._rng_py,
                region_mask=region,
            )

        # ── Stage 2: Angular contour lines ────────────────────────────────────
        # Detect edges in the reference to locate figure silhouettes, limb
        # separations, and major form boundaries.  Place short, angular line
        # segments along these boundaries.
        print("  Stage 2: angular contour lines…")

        gx = ndimage.sobel(lum, axis=1).astype(np.float32)
        gy = ndimage.sobel(lum, axis=0).astype(np.float32)
        edge_mag = np.sqrt(gx ** 2 + gy ** 2).astype(np.float32)
        if edge_mag.max() > 1e-9:
            edge_mag /= edge_mag.max()

        # Lightly smooth so contour strokes cluster around edges without
        # pixel-level jitter
        edge_mag_smooth = ndimage.gaussian_filter(edge_mag, sigma=contour_thickness * 0.5)

        # Sample heavily from strong edges + a small uniform base so even
        # soft inner-form edges receive some line work
        if region is not None:
            edge_weight = edge_mag_smooth * region + region * 0.08
        else:
            edge_weight = edge_mag_smooth + 0.04
        edge_total = edge_weight.flatten().sum()
        if edge_total < 1e-9:
            return
        edge_prob = edge_weight.flatten() / edge_total

        # Contour direction: tangent to the edge gradient (along the edge)
        contour_angles_map = np.arctan2(gx, -gy).astype(np.float32)
        contour_angles_map = ndimage.gaussian_filter(contour_angles_map, sigma=1.5)

        positions_c = self.rng.choice(h * w, size=n_contour_strokes,
                                       p=edge_prob, replace=True)

        tip_round = BrushTip(BrushTip.ROUND, bristle_noise=0.01)
        margin_c = max(3, int(contour_thickness * 2))

        for pos in positions_c:
            py, px = int(pos // w), int(pos % w)
            px = int(np.clip(px, margin_c, w - margin_c))
            py = int(np.clip(py, margin_c, h - margin_c))

            local_edge = float(edge_mag[py, px])

            # Schiele accent: rare blood-red at very strong boundary points
            if (local_edge > 0.55 and
                    self._rng_py.random() < accent_prob * local_edge * 2.0):
                stroke_col = jitter(accent_color, 0.015, self._rng_py)
            else:
                stroke_col = jitter(contour_color, 0.02, self._rng_py)

            # Angular break: the contour direction is the gradient tangent, but
            # Schiele's line re-starts at a slightly different angle rather than
            # flowing smoothly.  Add a per-stroke angular deviation sampled from
            # a bimodal distribution: usually small (±0.15 rad), occasionally
            # larger (±0.55 rad) to simulate a genuine break and re-attack.
            if self._rng_py.random() < 0.18:
                angle_jitter = self._rng_py.choice([-1, 1]) * self._rng_py.uniform(0.35, 0.65)
            else:
                angle_jitter = self._rng_py.uniform(-0.14, 0.14)
            a = float(contour_angles_map[py, px]) + angle_jitter

            # Line length scales with local edge strength: strong edges → longer
            # strokes (Schiele pressed hardest at joints and silhouette).
            L_min = contour_thickness * 3.5
            L_max = contour_thickness * 9.0
            L = L_min + (L_max - L_min) * min(1.0, local_edge * 1.4)
            L *= self._rng_py.uniform(0.7, 1.3)

            start = (px - math.cos(a) * L * 0.5,
                     py - math.sin(a) * L * 0.5)
            pts = stroke_path(start, a, L, curve=0.0,
                               n=max(2, int(L / 5)))

            # Pressure variation: strong at joints (high edge mag), faint between.
            thickness_here = (contour_thickness
                              * self._rng_py.uniform(0.55, 1.50)
                              * (0.6 + 0.8 * local_edge))
            ws = [thickness_here] * len(pts)

            # Opacity also scales with edge strength — Schiele's line disappears
            # on soft form transitions, punches through on silhouette/joint edges.
            opacity_here = 0.55 + 0.40 * min(1.0, local_edge * 1.5)

            self.canvas.apply_stroke(
                pts, ws, stroke_col, tip_round,
                opacity=opacity_here,
                wet_blend=0.0,   # dry — ink on paper does not blend
                jitter_amt=0.008,
                rng=self._rng_py,
                region_mask=None,  # contour lines cross the figure/bg boundary
            )

        print(f"  Angular contour complete ({n_flat_strokes} fill  "
              f"{n_contour_strokes} contour lines).")

    def cloisonne_pass(self,
                       reference:          Union[np.ndarray, Image.Image],
                       n_colors:           int   = 8,
                       contour_thickness:  float = 4.5,
                       contour_color:      Color = (0.06, 0.04, 0.10),
                       saturation_boost:   float = 1.40,
                       hue_exotic_shift:   float = 0.03,
                       zone_opacity:       float = 0.92,
                       contour_opacity:    float = 0.94,
                       n_zone_strokes:     int   = 1400):
        """
        Cloisonnism / Synthetism pass — inspired by Paul Gauguin.

        Gauguin's Cloisonnism (named for cloisonné enamel jewellery where
        metallic 'cloisons' separate vivid glass fields) renders the world as
        flat zones of saturated, anti-naturalistic colour enclosed in dark
        thick organic contour lines — like stained-glass leading.  Chiaroscuro
        modelling is abandoned in favour of colour-as-emotion.  In Tahiti
        (1891–1903) his palette became the most exotic in Western painting:
        hot cadmium orange, deep cerulean, rose-magenta, viridian, golden ochre.

        Algorithm
        ---------
        1. Quantize the reference to ``n_colors`` flat zones using PIL palette
           quantization.  Each zone is assigned its mean colour from the
           reference, then saturation-boosted and hue-drifted toward Gauguin's
           tropical register.
        2. Fill each colour zone with flat loaded-brush strokes — opaque,
           low-wet-blend, broad.  Strokes are sampled from within each zone's
           pixel mask so colour never crosses a zone boundary.
        3. Detect inter-zone boundaries with Sobel on the zone index map.
        4. Draw thick dark organic contour lines along all zone boundaries —
           the 'cloisonné leading' that gives the technique its graphic power.
           Gauguin used near-black Prussian blue-black, not pure black.

        Parameters
        ----------
        reference         : PIL Image or ndarray reference.
        n_colors          : Number of colour zones (6–10 is Gauguin's range).
        contour_thickness : Width of the dark boundary lines in pixels.
        contour_color     : Cloisonné line colour — near-black with blue-purple
                            warmth (Gauguin used Prussian blue-black, not raw black).
        saturation_boost  : HSV saturation multiplier applied to each zone's
                            mean colour.  > 1 pushes toward exotic intensity.
        hue_exotic_shift  : Fraction of the hue wheel to drift each zone colour.
                            Small positive values push toward warm-tropical.
        zone_opacity      : Opacity of flat zone fill strokes.
        contour_opacity   : Opacity of contour line strokes.
        n_zone_strokes    : Total flat-fill strokes across all colour zones.
        """
        print(f"Cloisonné pass  (n_colors={n_colors}  "
              f"contour={contour_thickness:.1f}px  boost={saturation_boost:.2f})…")

        ref  = self._prep(reference)
        h, w = ref.shape[:2]

        # ── Step 1: Palette quantization ─────────────────────────────────────
        # PIL quantize gives us an index image and a compact palette.
        ref_pil = Image.fromarray(ref[:, :, :3])
        quantized = ref_pil.quantize(colors=n_colors, method=0, dither=0)
        index_arr = np.array(quantized, dtype=np.int32)   # (H, W), values 0..n_colors-1

        # Extract the palette as (n_colors, 3) float array in [0, 1].
        raw_palette = quantized.getpalette()               # flat list R,G,B × 256
        zone_colors_rgb: List[Color] = []
        for zi in range(n_colors):
            r = raw_palette[zi * 3]     / 255.0
            g = raw_palette[zi * 3 + 1] / 255.0
            b = raw_palette[zi * 3 + 2] / 255.0
            zone_colors_rgb.append((r, g, b))

        # ── Step 2: Boost saturation and drift hue toward tropical palette ───
        def _gauguin_shift(c: Color) -> Color:
            """Boost saturation and apply exotic hue drift in HSV space."""
            h_hsv, s, v = colorsys.rgb_to_hsv(*c)
            # Drift hue toward warm-tropical (orange-red register)
            h_hsv = (h_hsv + hue_exotic_shift) % 1.0
            # Boost saturation — Gauguin's colours are never muddy
            s = min(1.0, s * saturation_boost)
            # Slight value push: very dark zones stay dark, but mid-tones
            # are pushed slightly lighter (paper under thin paint glows through)
            if 0.15 < v < 0.65:
                v = v * 0.85 + 0.15
            return colorsys.hsv_to_rgb(h_hsv, s, v)

        zone_colors_shifted = [_gauguin_shift(c) for c in zone_colors_rgb]

        # ── Step 3: Flat zone fill ────────────────────────────────────────────
        print("  Stage 1: flat colour zone fill…")
        rarr = ref[:, :, :3].astype(np.float32) / 255.0

        tip_flat = BrushTip(BrushTip.FLAT, bristle_noise=0.04)

        # Distribute strokes across zones proportional to zone area.
        zone_areas = np.array([float((index_arr == zi).sum())
                                for zi in range(n_colors)], dtype=np.float32)
        total_area = zone_areas.sum() + 1e-9
        zone_strokes_alloc = [
            max(20, int(n_zone_strokes * (zone_areas[zi] / total_area)))
            for zi in range(n_colors)
        ]

        for zi in range(n_colors):
            zone_mask = (index_arr == zi).astype(np.float32)  # (H, W)
            if zone_mask.sum() < 4:
                continue

            # Apply figure mask if set — prefer not to flood background with
            # garish tropical colour unless the reference has a figure there.
            effective_zone = zone_mask
            if self._figure_mask is not None:
                # Blend: full weight in figure zone, 0.6 weight in background zone
                bg_weight = 0.60 * (1.0 - self._figure_mask)
                effective_zone = zone_mask * (self._figure_mask + bg_weight)
                effective_zone = np.clip(effective_zone, 0.0, 1.0)

            zone_flat = effective_zone.flatten()
            zone_total = zone_flat.sum()
            if zone_total < 1e-9:
                continue
            zone_prob = zone_flat / zone_total

            col_base = zone_colors_shifted[zi]
            n_here   = zone_strokes_alloc[zi]

            positions = self.rng.choice(h * w, size=n_here, p=zone_prob, replace=True)

            stroke_size = max(6.0, min(w, h) * 0.018)   # ~1.8% canvas short side

            for pos in positions:
                py, px = int(pos // w), int(pos % w)
                margin = max(3, int(stroke_size))
                px = int(np.clip(px, margin, w - margin))
                py = int(np.clip(py, margin, h - margin))

                # Slight per-stroke jitter in hue/value to avoid perfectly flat blocks
                col = jitter(col_base, 0.022, self._rng_py)

                # Broadly horizontal strokes — Gauguin's zone fills are confident
                # lateral sweeps, not random marks
                a      = self._rng_py.uniform(-0.20, 0.20)   # near-horizontal
                length = stroke_size * self._rng_py.uniform(2.0, 4.5)
                start  = (px - math.cos(a) * length * 0.5,
                          py - math.sin(a) * length * 0.5)
                n_pts  = max(3, int(length / 7))
                pts    = stroke_path(start, a, length, curve=0.0, n=n_pts)
                ws     = [stroke_size * self._rng_py.uniform(0.85, 1.15)] * len(pts)

                self.canvas.apply_stroke(
                    pts, ws, col, tip_flat,
                    opacity=zone_opacity * self._rng_py.uniform(0.88, 1.0),
                    wet_blend=0.05,      # Synthetism: flat, not blended
                    jitter_amt=0.015,
                    rng=self._rng_py,
                    region_mask=zone_mask,   # hard zone boundary — no colour bleed
                )

        # ── Step 4: Cloisonné contour lines (zone boundaries) ────────────────
        # Sobel on the index map locates every transition between colour zones.
        # This is the 'cloisonné leading' — the dark line that gives the
        # technique its graphic, stained-glass quality.
        print("  Stage 2: cloisonné boundary lines…")

        idx_float = index_arr.astype(np.float32) / max(n_colors - 1, 1)
        gx = ndimage.sobel(idx_float, axis=1).astype(np.float32)
        gy = ndimage.sobel(idx_float, axis=0).astype(np.float32)
        edge_mag = np.sqrt(gx ** 2 + gy ** 2).astype(np.float32)
        if edge_mag.max() > 1e-9:
            edge_mag /= edge_mag.max()

        # Smooth slightly so contour strokes cluster neatly, not pixel-by-pixel
        edge_smooth = ndimage.gaussian_filter(edge_mag, sigma=contour_thickness * 0.45)

        # Sample contour positions heavily from boundary pixels
        boundary_weight = edge_smooth.flatten()
        boundary_total  = boundary_weight.sum()
        if boundary_total < 1e-9:
            print("  No zone boundaries detected — skipping contour stage.")
        else:
            boundary_weight /= boundary_total

            # Contour stroke count scales with canvas area
            n_contour = max(600, int(w * h / 500))
            positions_c = self.rng.choice(h * w, size=n_contour,
                                           p=boundary_weight, replace=True)

            # Contour direction: tangent to the zone edge (perpendicular to Sobel gradient)
            contour_angles = np.arctan2(gx, -gy).astype(np.float32)
            contour_angles = ndimage.gaussian_filter(contour_angles, sigma=1.8)

            tip_round = BrushTip(BrushTip.ROUND, bristle_noise=0.02)
            margin_c  = max(3, int(contour_thickness * 2))

            for pos in positions_c:
                py, px = int(pos // w), int(pos % w)
                px = int(np.clip(px, margin_c, w - margin_c))
                py = int(np.clip(py, margin_c, h - margin_c))

                local_edge = float(edge_mag[py, px])
                if local_edge < 0.05:
                    continue   # skip weak-boundary noise

                # Gauguin's cloisonné line: thick where the zone contrast is
                # highest, thinner across gentler transitions — the 'lead'
                # varies in weight like hand-drawn metalwork.
                thick = (contour_thickness
                         * self._rng_py.uniform(0.70, 1.35)
                         * (0.55 + 0.75 * min(1.0, local_edge * 1.5)))

                a = float(contour_angles[py, px])
                a += self._rng_py.uniform(-0.10, 0.10)   # organic wobble

                # Short strokes — the leading is a series of overlapping segments,
                # not a single continuous ruled line.
                L = thick * self._rng_py.uniform(4.0, 9.0)
                start = (px - math.cos(a) * L * 0.5,
                         py - math.sin(a) * L * 0.5)
                pts = stroke_path(start, a, L, curve=0.0,
                                   n=max(2, int(L / 5)))
                ws  = [thick] * len(pts)

                col = jitter(contour_color, 0.018, self._rng_py)

                self.canvas.apply_stroke(
                    pts, ws, col, tip_round,
                    opacity=contour_opacity * (0.72 + 0.28 * min(1.0, local_edge * 2)),
                    wet_blend=0.0,   # ink contour — never wet-blends
                    jitter_amt=0.010,
                    rng=self._rng_py,
                    region_mask=None,   # contour lines cross all boundaries
                )

        print(f"  Cloisonné complete ({n_colors} zones  contour={contour_thickness:.1f}px).")

    def pigment_granulation_pass(self,
                                 strength:   float = 0.42,
                                 lum_lo:     float = 0.08,
                                 lum_hi:     float = 0.82,
                                 tex_mean:   float = 0.84):
        """
        Watercolour pigment granulation — physical paper-tooth pigment settling.

        Certain watercolour pigments (ultramarine blue PB29, burnt sienna PR101,
        cobalt PB28, raw umber PBr7) have unusually large or heavy particles.
        As a freshly-applied wash dries, these particles settle by gravity and
        surface tension into the depressions ('hollows') of the paper tooth, while
        the water-soluble binder lifts them off the peaks.  The result is a
        speckled, tactile texture where:
          - **Paper hollows** (low texture value) = concentrated dark pigment
          - **Paper peaks** (high texture value) = diluted or absent pigment

        This is impossible to replicate by varying stroke size or opacity alone —
        it requires a direct pixel-level modulation of the painted surface using
        the same paper texture that drives the substrate rendering.

        The pass reads the current canvas buffer, computes per-pixel luminance,
        then applies the paper-texture map (self.canvas.texture) as a physical
        offset: hollows are darkened, peaks are lightened, by up to ``strength``.
        Only mid-luminance pixels (lum_lo … lum_hi) receive the effect — bare
        paper (very light) and deep darks are left untouched, matching how real
        granulating pigments are transparent in high-dilution zones.

        This improvement is applied *after* the wet-into-wet wash passes so that
        the granulation reads as a property of the dried pigment deposit, not an
        additional paint layer.

        Parameters
        ----------
        strength : Maximum luminance shift at full texture contrast (0–1).
                   0.35–0.50 gives a naturalistic granulation; above 0.60
                   looks like deliberate texture.
        lum_lo   : Lower luminance gate (shadows below this are untouched).
        lum_hi   : Upper luminance gate (lights above this are untouched — bare paper).
        tex_mean : Neutral texture value around which hollows and peaks are measured.
                   Should match the midpoint of the texture range (linen ~0.86,
                   cold-press paper ~0.84).
        """
        print(f"Pigment granulation pass  (strength={strength:.2f}  "
              f"lum=[{lum_lo:.2f}, {lum_hi:.2f}])…")

        h, w = self.h, self.w

        # ── Read current canvas ───────────────────────────────────────────────
        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(h, w, 4).copy()
        # Cairo BGRA → RGB float [0, 1]
        carr = buf[:, :, [2, 1, 0]].astype(np.float32) / 255.0

        # ── Paper texture (already generated for the substrate) ───────────────
        tex = self.canvas.texture   # (H, W) float32 in [0.68, 1.0]

        # ── Luminance map ─────────────────────────────────────────────────────
        lum = (0.299 * carr[:, :, 0] +
               0.587 * carr[:, :, 1] +
               0.114 * carr[:, :, 2]).astype(np.float32)

        # ── Granulation mask: only mid-luminance painted areas ────────────────
        gran_mask = ((lum > lum_lo) & (lum < lum_hi)).astype(np.float32)

        # Smooth the mask so the effect fades in at both luminance extremes
        gran_mask = ndimage.gaussian_filter(gran_mask, sigma=1.5)
        gran_mask = np.clip(gran_mask, 0.0, 1.0)

        # Apply figure mask if present: granulation is strongest on figure
        # surfaces (where pigment was actually applied) and weaker in the
        # bare-paper background.
        if self._figure_mask is not None:
            fig_weight = 0.40 + 0.60 * self._figure_mask   # bg gets 40% strength
            gran_mask  = gran_mask * fig_weight

        # ── Texture offset ────────────────────────────────────────────────────
        # tex values below tex_mean = hollow = more pigment → darker
        # tex values above tex_mean = peak   = less pigment → lighter
        # offset is negative in hollows (darken), positive on peaks (lighten)
        tex_offset = (tex - tex_mean) * strength   # (H, W) in [-strength*0.16, +strength*0.16]
        # Scale by mask so effect only appears in the painted mid-tone zone
        tex_offset = tex_offset * gran_mask         # (H, W)

        # ── Apply modulation to RGB channels ──────────────────────────────────
        # All three channels shift equally to preserve hue; only luminance changes.
        modified = np.zeros_like(carr)
        for c in range(3):
            modified[:, :, c] = np.clip(carr[:, :, c] + tex_offset, 0.0, 1.0)

        # ── Write back to Cairo surface (RGB → BGR for BGRA layout) ──────────
        buf[:, :, 2] = np.clip(modified[:, :, 0] * 255, 0, 255).astype(np.uint8)  # R
        buf[:, :, 1] = np.clip(modified[:, :, 1] * 255, 0, 255).astype(np.uint8)  # G
        buf[:, :, 0] = np.clip(modified[:, :, 2] * 255, 0, 255).astype(np.uint8)  # B
        buf[:, :, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print("  Granulation complete.")

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

    def color_field_pass(self,
                         reference:              Union[np.ndarray, Image.Image],
                         n_bands:                int   = 3,
                         n_washes:               int   = 14,
                         wash_opacity:           float = 0.16,
                         edge_blur_sigma:        float = 0.0,
                         figure_preserve:        float = 0.60,
                         chromatic_vibration:    float = 0.035,
                         band_hue_drift:         float = 0.018):
        """
        Color Field pass — inspired by Mark Rothko.

        Rothko's mature paintings from the 1950s–60s consist of two or three
        large horizontal rectangles of colour that appear to float against a
        dark absorbing ground.  The rectangles have no hard edge — their
        boundaries are built up over many (often 15–20) thin transparent washes
        applied wet-into-wet, so the colour seems to emerge from within the
        canvas rather than sitting on top of it.  The result is a luminous,
        breathing quality that no single opaque stroke can achieve.

        Key perceptual mechanisms Rothko exploited:

          1. **Simultaneous contrast** — adjacent bands are chosen from opposite
             ends of the warm/cool spectrum so each makes the other appear more
             intense than it actually is.

          2. **Dark absorbing void** — the ground and lower band are very dark,
             making upper lighter bands appear self-luminous by comparison.

          3. **Optical layering** — each wash is semi-transparent; the light
             shifts wavelength as it passes through each layer, bounces off the
             canvas, and passes back out through all the layers.  This creates
             a depth and warmth that cannot be replicated by flat opaque paint.

          4. **Chromatic vibration at the edge** — the boundary zone between two
             bands contains both colours at once, creating a narrow fringe that
             visually vibrates.  Rothko described this as "the breath of the
             painting."

        This pass:
          Stage 1 — Analyse the reference image.  Divide it into `n_bands`
                    horizontal strips and compute the mean colour of each strip,
                    biased toward the dominant hue of that zone.

          Stage 2 — Apply `n_washes` thin Cairo rectangle washes per band,
                    each wash slightly shifting hue/value so the accumulated
                    colour has depth and variation.  The band boundaries are
                    feathered using a per-row opacity falloff (Gaussian profile).

          Stage 3 — Chromatic vibration pass.  At each band boundary, composite
                    an additional thin wash of the complementary colour mixed
                    from both adjacent bands.  This brightens the boundary
                    perceptually while remaining physically thin.

          Stage 4 — If `figure_preserve` > 0, blend the painted color field with
                    the underlying canvas (which holds the standard oil underpainting
                    that blender_bridge runs before this pass), so the figure remains
                    recognisable as a warmth or luminosity within the field rather
                    than being completely erased.

        Parameters
        ----------
        reference           : PIL Image or ndarray.
        n_bands             : Number of horizontal color bands (Rothko typically
                              used 2–4; 3 is canonical).
        n_washes            : Washes applied per band.  More = more optical depth.
                              12–18 is the practical sweet spot.
        wash_opacity        : Opacity of each individual wash.  Cumulative effect
                              of `n_washes` washes is approximately
                              1 - (1 - wash_opacity)^n_washes.
        edge_blur_sigma     : Additional Gaussian blur applied to each band mask
                              beyond the intrinsic Gaussian falloff (pixels).
                              0 = rely only on the Gaussian profile; values of
                              20–60 create very soft dissolution.
        figure_preserve     : How much of the pre-existing canvas (typically the
                              oil underpainting) to blend back in [0–1].  0 = pure
                              color field erases the figure; 1 = color field has no
                              effect.  0.55–0.70 gives Rothko-like results where
                              you sense a form within the field without defining it.
        chromatic_vibration : Opacity of the boundary vibration wash.
                              0.03–0.06 gives a subtle shimmer; 0 disables it.
        band_hue_drift      : Per-wash hue rotation (HSV) applied cumulatively so
                              successive washes shift the band's colour slightly.
                              Models Rothko's deliberate hue shifts between layers.

        Notes
        -----
        Mark Rothko (1903–1970) was born Marcus Rothkowitz in Dvinsk, Latvia.
        He emigrated to the United States at age 10.  After years of surrealist
        influence he arrived at his signature "Multiform" and then pure Color
        Field style around 1950.  He rejected interpretation and said his
        paintings were about "basic human emotions — tragedy, ecstasy, doom."
        He insisted his works be hung close to the floor and experienced at
        close range so the viewer is enveloped rather than distanced.

        The Rothko Chapel in Houston (1971) contains 14 large paintings he
        made for the space.  He died by suicide on 25 February 1970, at 66,
        before the chapel opened.

        Famous works:
          *No. 61 (Rust and Blue)* (1953) — rust band over deep blue void.
          *Orange, Red, Yellow* (1961) — sold for $86.9M in 2012; warm chromatic field.
          *Black on Maroon* (1958) — Seagram mural; near-black dissolving geometry.
        """
        print(f"Color field pass  (n_bands={n_bands}  n_washes={n_washes}"
              f"  opacity/wash={wash_opacity:.2f})…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        # ── Stage 1: Sample dominant colour per horizontal strip ──────────────
        # Each band covers an equal fraction of image height.  Mean colour is
        # computed over all pixels in the strip (in float [0, 1] space).
        band_colors: List[Color] = []
        band_y_centers: List[float] = []
        for b in range(n_bands):
            y0 = int(b * h / n_bands)
            y1 = int((b + 1) * h / n_bands)
            strip = rarr[y0:y1, :, :]          # (strip_h, W, 3)
            mean_col = strip.reshape(-1, 3).mean(axis=0)
            band_colors.append((float(mean_col[0]),
                                 float(mean_col[1]),
                                 float(mean_col[2])))
            band_y_centers.append((y0 + y1) * 0.5)

        # ── Save pre-pass canvas snapshot for figure_preserve blending ────────
        # Read the current canvas into a float array so we can blend it back in
        # during Stage 4.  This captures whatever underpainting was run first.
        if figure_preserve > 0.0:
            pre_buf = np.frombuffer(self.canvas.surface.get_data(),
                                    dtype=np.uint8).reshape(h, w, 4).copy()
            # BGRA → RGB float
            pre_rgb = pre_buf[:, :, [2, 1, 0]].astype(np.float32) / 255.0
        else:
            pre_rgb = None

        # ── Stage 2: Band washes ──────────────────────────────────────────────
        # For each band, apply n_washes thin Cairo rectangle composites.
        # Opacity is modulated by a Gaussian weight that peaks at the band
        # centre and falls to ~5% at the adjacent band centres — creating the
        # feathered dissolution that defines Rothko's edge language.
        #
        # band_sigma: standard deviation of the Gaussian in image pixels.
        # For 3 bands across height H, each band is H/3 tall, so sigma ≈ H/6.
        band_sigma = h / (n_bands * 2.2)   # Gaussian half-width ≈ one half-band

        ys_all = np.arange(h, dtype=np.float32)

        for b, (base_col, cy_b) in enumerate(zip(band_colors, band_y_centers)):
            print(f"  Band {b+1}/{n_bands}: ({base_col[0]:.2f}, {base_col[1]:.2f},"
                  f" {base_col[2]:.2f})  cy={cy_b:.0f}px…")

            # Per-row Gaussian weight for this band
            gauss_weights = np.exp(-0.5 * ((ys_all - cy_b) / band_sigma) ** 2)

            if edge_blur_sigma > 0.0:
                gauss_weights = ndimage.gaussian_filter1d(
                    gauss_weights, sigma=edge_blur_sigma)
            gauss_weights = np.clip(gauss_weights, 0.0, 1.0)

            # Iterative hue-drift wash loop
            h_hsv, s_hsv, v_hsv = colorsys.rgb_to_hsv(*base_col)
            for wash_i in range(n_washes):
                # Cumulative hue drift — each wash shifted slightly
                h_drift = (h_hsv + wash_i * band_hue_drift) % 1.0
                # Value alternates slightly: even washes slightly lighter,
                # odd washes slightly darker — mimics the oscillation of a
                # loaded brush vs. a drawing-back stroke.
                v_drift = max(0.02, min(1.0,
                    v_hsv + 0.015 * math.sin(wash_i * 1.47)))
                wash_r, wash_g, wash_b = colorsys.hsv_to_rgb(h_drift, s_hsv, v_drift)
                wash_r = float(np.clip(wash_r + self._rng_py.uniform(-0.005, 0.005), 0, 1))
                wash_g = float(np.clip(wash_g + self._rng_py.uniform(-0.005, 0.005), 0, 1))
                wash_b = float(np.clip(wash_b + self._rng_py.uniform(-0.005, 0.005), 0, 1))

                # Draw a full-width rectangle at each row, with per-row alpha
                # = wash_opacity * gauss_weight[y].  Cairo's set_source_rgba
                # applies a single alpha; we vary by row by iterating over rows
                # in chunks or per-pixel.  For efficiency we batch by rounding
                # gauss_weights to 4-decimal precision and group consecutive rows.
                ctx = self.canvas.ctx
                for row_y in range(h):
                    row_alpha = wash_opacity * float(gauss_weights[row_y])
                    if row_alpha < 0.002:
                        continue
                    ctx.set_source_rgba(wash_r, wash_g, wash_b, row_alpha)
                    ctx.rectangle(0.0, float(row_y), float(w), 1.0)
                    ctx.fill()

        # ── Stage 3: Chromatic vibration at band boundaries ───────────────────
        # Between each pair of adjacent bands, compute a boundary colour as the
        # mean of the two bands, then shift it toward the complement of whichever
        # band dominates at the boundary.  Apply a narrow Gaussian wash.
        if chromatic_vibration > 0.0:
            print("  Chromatic vibration pass…")
            boundary_sigma = band_sigma * 0.22   # very narrow fringe

            for b in range(n_bands - 1):
                by = (band_y_centers[b] + band_y_centers[b + 1]) * 0.5
                col_a = band_colors[b]
                col_b = band_colors[b + 1]
                # Mean colour at the boundary
                mid_col = ((col_a[0] + col_b[0]) * 0.5,
                           (col_a[1] + col_b[1]) * 0.5,
                           (col_a[2] + col_b[2]) * 0.5)
                # Shift toward complement to create perceptual shimmer
                comp_col = complement(mid_col)
                vib_col  = mix_paint(mid_col, comp_col, 0.25)

                vib_gauss = np.exp(-0.5 * ((ys_all - by) / boundary_sigma) ** 2)
                vib_gauss = np.clip(vib_gauss, 0.0, 1.0)

                ctx = self.canvas.ctx
                for row_y in range(h):
                    row_alpha = chromatic_vibration * float(vib_gauss[row_y])
                    if row_alpha < 0.002:
                        continue
                    ctx.set_source_rgba(vib_col[0], vib_col[1], vib_col[2], row_alpha)
                    ctx.rectangle(0.0, float(row_y), float(w), 1.0)
                    ctx.fill()

        # ── Stage 4: Figure preserve — blend pre-pass canvas back in ─────────
        # Composite pre_rgb (the underpainting/reference pass canvas) at
        # `figure_preserve` opacity over the color field.  This lets the figure
        # remain recognisable as a luminous warmth within the field.
        if pre_rgb is not None and figure_preserve > 0.0:
            print(f"  Figure preserve blend  ({figure_preserve:.0%})…")
            ctx = self.canvas.ctx

            # Re-bake pre_rgb into a cairo surface and composite at figure_preserve
            pre_arr = np.zeros((h, w, 4), dtype=np.uint8)
            pre_arr[:, :, 2] = np.clip(pre_rgb[:, :, 0] * 255, 0, 255).astype(np.uint8)  # R→BGRA
            pre_arr[:, :, 1] = np.clip(pre_rgb[:, :, 1] * 255, 0, 255).astype(np.uint8)
            pre_arr[:, :, 0] = np.clip(pre_rgb[:, :, 2] * 255, 0, 255).astype(np.uint8)
            pre_arr[:, :, 3] = 255

            pre_surf = cairo.ImageSurface.create_for_data(
                bytearray(pre_arr.tobytes()), cairo.FORMAT_ARGB32, w, h)

            ctx.set_source_surface(pre_surf, 0, 0)
            ctx.paint_with_alpha(figure_preserve)

        # Dampen wetness after color field — the vast washes add significant wet
        # surface; let them dry partially before any subsequent stroke passes.
        self.canvas.wetness *= 0.30

    # ── El Greco Mannerist technique ──────────────────────────────────────────

    def elongation_distortion_pass(
            self,
            reference:          Union[np.ndarray, Image.Image],
            elongation_factor:  float = 0.15,
            figure_mask:        Optional[np.ndarray] = None,
            jewel_boost:        float = 1.30,
            inner_glow_radius:  float = 14.0,
            inner_glow_opacity: float = 0.22,
            glow_color:         Color = (0.88, 0.86, 0.80),
    ) -> None:
        """
        El Greco Mannerist elongation pass.

        Three-stage technique inspired by Domenikos Theotokopoulos (El Greco):

        Stage 1 — Figure elongation
            Reads the current canvas buffer.  In the figure region (defined by
            figure_mask or the whole canvas if None), compresses source rows
            over a larger destination range to vertically stretch forms.  The
            elongation is soft-weighted at top and bottom so faces and feet
            don't warp — only the torso and limbs receive maximum stretch.
            This mimics El Greco's characteristic spiritual lengthening where
            figures seem to aspire upward beyond anatomical possibility.

        Stage 2 — Jewel-tone saturation boost
            Converts the canvas buffer to HSV, multiplies saturation by
            `jewel_boost`, and writes back.  El Greco's palette is famous for
            its jewel-like intensity: vermilion, cerulean, lemon, viridian —
            colours that vibrate rather than harmonise.

        Stage 3 — Inner-glow on pale flesh
            Identifies canvas pixels whose luminance exceeds 0.72 (the pale
            silver-grey flesh zones that El Greco made self-luminous).  Applies
            a Gaussian soft bright halo radiating outward from those pixels,
            composited at `inner_glow_opacity`.  This creates the uncanny
            inner-lit quality unique to his flesh rendering.

        Parameters
        ----------
        reference       : reference image (PIL or ndarray) — used for luminance
                          masking of the inner-glow stage.
        elongation_factor : fractional vertical stretch to apply to the figure
                            region (0.15 = 15% taller, El Greco's typical range).
        figure_mask     : (H, W) float32 mask — 1.0 inside figure, 0.0 outside.
                          If None the whole canvas is treated as figure.
        jewel_boost     : HSV saturation multiplier (> 1 = more saturated).
        inner_glow_radius  : Gaussian blur sigma in pixels for glow spread.
        inner_glow_opacity : opacity at which the glow layer is composited.
        glow_color      : warm silver-grey colour of the inner glow.
        """
        from PIL import ImageFilter as _IF

        w, h = self.canvas.w, self.canvas.h

        # ── Stage 1: Figure elongation ────────────────────────────────────────
        # Read current canvas as BGRA uint8 array
        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(h, w, 4).copy()

        if figure_mask is not None:
            # Determine the vertical extent of the figure region
            mask_rows = figure_mask.max(axis=1)   # (H,) — row is in figure if > 0.5
            fig_rows  = np.where(mask_rows > 0.5)[0]
            if len(fig_rows) >= 4:
                y_top    = int(fig_rows[0])
                y_bottom = int(fig_rows[-1])
                fig_height = y_bottom - y_top

                # Source height we will compress into [y_top, y_bottom]:
                # We read from the figure region at a contracted sample spacing
                # so that the same content covers more pixels = elongation.
                src_height = max(1, round(fig_height / (1.0 + elongation_factor)))
                src_y_top  = y_top + (fig_height - src_height) // 2

                stretched = buf.copy()
                # Soft weight for elongation: zero at very top/bottom 15% of
                # figure, rising to 1.0 in the middle 70%.
                for dst_y in range(y_top, y_bottom + 1):
                    t = (dst_y - y_top) / max(fig_height, 1)
                    # Linear ramp in / ramp out at 15% top and bottom
                    blend = min(t / 0.15, 1.0, (1.0 - t) / 0.15)

                    # Source row: lerp between original row and the stretched row
                    src_t   = (dst_y - y_top) / max(fig_height, 1)
                    src_row = src_y_top + int(src_t * src_height)
                    src_row = max(0, min(h - 1, src_row))

                    # Blend the stretched row in according to mask weight and
                    # distance from figure centre.
                    row_mask = (figure_mask[dst_y, :] * blend)[:, np.newaxis]  # (W, 1)
                    stretched[dst_y] = (
                        buf[src_row] * row_mask + buf[dst_y] * (1.0 - row_mask)
                    ).astype(np.uint8)

                buf = stretched
        # else: no mask — elongation is subtle across the whole image by
        # slightly stretching the vertical centre portion.  Apply at half weight.
        else:
            centre_start = h // 5
            centre_end   = h - h // 5
            region_h     = centre_end - centre_start
            src_h        = max(1, round(region_h / (1.0 + elongation_factor * 0.5)))
            src_start    = centre_start + (region_h - src_h) // 2
            stretched    = buf.copy()
            for dst_y in range(centre_start, centre_end):
                t       = (dst_y - centre_start) / max(region_h, 1)
                blend   = min(t / 0.20, 1.0, (1.0 - t) / 0.20) * 0.55
                src_t   = t
                src_row = src_start + int(src_t * src_h)
                src_row = max(0, min(h - 1, src_row))
                stretched[dst_y] = (
                    buf[src_row] * blend + buf[dst_y] * (1.0 - blend)
                ).astype(np.uint8)
            buf = stretched

        # Write stretched buffer back to canvas
        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"  Elongation applied  (factor={elongation_factor:.0%})")

        # ── Stage 2: Jewel-tone saturation boost ──────────────────────────────
        # Read canvas back (may have been modified by stage 1 write)
        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(h, w, 4).copy()
        rgb = buf[:, :, [2, 1, 0]].astype(np.float32) / 255.0  # BGRA→RGB

        # Vectorised HSV saturation boost
        # Reshape to (H*W, 3) for colorsys-style computation
        flat = rgb.reshape(-1, 3)
        maxc = flat.max(axis=1)
        minc = flat.min(axis=1)
        span = maxc - minc  # saturation numerator

        # Boost saturation while keeping hue and value identical
        # For pixels already nearly grey (span < 0.02) — skip; no hue to boost.
        boosted = flat.copy()
        mask_sat = span > 0.02
        if mask_sat.any():
            # Compute scale factor: new_sat = min(1, old_sat * jewel_boost)
            # old_sat = span / maxc  (HSV definition)
            # new_span = old_sat * jewel_boost * maxc = span * jewel_boost
            # Clamp so no channel exceeds maxc.
            scale = np.where(mask_sat, np.minimum(jewel_boost, maxc / (span + 1e-8)), 1.0)
            # Grey point of the pixel: midpoint between min and max
            grey = ((flat - minc[:, None]) * scale[:, None] + minc[:, None])
            boosted[mask_sat] = np.clip(grey[mask_sat], 0, 1)

        rgb_boosted = boosted.reshape(h, w, 3)

        # Write back to canvas buffer
        buf[:, :, 2] = np.clip(rgb_boosted[:, :, 0] * 255, 0, 255).astype(np.uint8)  # R
        buf[:, :, 1] = np.clip(rgb_boosted[:, :, 1] * 255, 0, 255).astype(np.uint8)  # G
        buf[:, :, 0] = np.clip(rgb_boosted[:, :, 2] * 255, 0, 255).astype(np.uint8)  # B

        tmp2 = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        self.canvas.ctx.set_source_surface(tmp2, 0, 0)
        self.canvas.ctx.paint()

        print(f"  Jewel saturation boost applied  (×{jewel_boost:.2f})")

        # ── Stage 3: Inner glow on pale flesh zones ───────────────────────────
        # El Greco's flesh is silver-grey and appears self-luminous — not lit from
        # outside but radiating from within.  We simulate this by:
        #   1. Find canvas pixels where luminance > 0.72 (the pale silver zones)
        #   2. Build a grey-scale "seed" map from those pixels
        #   3. Gaussian-blur it to spread the glow outward
        #   4. Composite the glow at inner_glow_opacity using glow_color
        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(h, w, 4).copy()
        rgb_f = buf[:, :, [2, 1, 0]].astype(np.float32) / 255.0

        lum = 0.2126 * rgb_f[:, :, 0] + 0.7152 * rgb_f[:, :, 1] + 0.0722 * rgb_f[:, :, 2]
        pale_seed = np.clip((lum - 0.72) / 0.28, 0.0, 1.0).astype(np.float32)

        if pale_seed.max() > 0.01 and inner_glow_radius > 0.5 and inner_glow_opacity > 0.0:
            # Blur the seed to spread glow
            glow_map = ndimage.gaussian_filter(pale_seed, sigma=inner_glow_radius)
            glow_map = np.clip(glow_map / (glow_map.max() + 1e-8), 0.0, 1.0)

            gr, gg, gb = glow_color
            ctx = self.canvas.ctx
            for row_y in range(h):
                row_max = float(glow_map[row_y].max())
                if row_max < 0.005:
                    continue
                # Per-pixel would be too slow; use a per-row composite with the
                # row's average glow value as alpha — adequate for a soft glow.
                row_alpha = inner_glow_opacity * row_max
                ctx.set_source_rgba(gr, gg, gb, row_alpha)
                ctx.rectangle(0.0, float(row_y), float(w), 1.0)
                ctx.fill()

        print(f"  Inner glow applied  (radius={inner_glow_radius:.1f}px, "
              f"opacity={inner_glow_opacity:.0%})")

    # ── Impasto texture pass — physical thick-paint ridge simulation ──────────

    def impasto_texture_pass(
            self,
            light_angle:   float = 315.0,
            ridge_height:  float = 0.55,
            blur_sigma:    float = 1.4,
            highlight_opacity: float = 0.28,
            shadow_opacity:    float = 0.22,
    ) -> None:
        """
        Simulate the physical texture of thick impasto oil paint.

        Rembrandt, Van Gogh, and Velázquez all applied paint so thickly in
        their lit areas that the dried ridges of paint cast real shadows and
        catch directional light — giving the surface a three-dimensional,
        sculptural quality that photographs cannot fully capture.

        This pass approximates that texture by:

        Stage 1 — Local gradient detection
            Computes the Sobel gradient of the canvas luminance to identify
            stroke ridges.  Strong gradient = paint ridge boundary.

        Stage 2 — Directional ridge highlight
            Along the upwind side of each ridge (relative to `light_angle`),
            adds a thin bright white-cream highlight strip.  Real impasto ridges
            catch the light on their upper face.

        Stage 3 — Directional ridge shadow
            Along the downwind side of each ridge, adds a thin dark shadow
            strip.  Real ridges cast a micro-shadow on the canvas below.

        The combination of adjacent highlight + shadow creates the visual
        illusion of a three-dimensional paint surface without requiring a
        full normal map or 3D geometry.

        Parameters
        ----------
        light_angle     : direction light arrives from, in degrees clockwise
                          from north (0° = from top, 315° = upper-left,
                          the traditional studio north-light convention).
        ridge_height    : controls how pronounced the ridge effect is.
                          0 = off; 1 = very strong raised impasto.
        blur_sigma      : Gaussian blur applied to the gradient before
                          thresholding — wider sigma = softer, broader ridges.
        highlight_opacity : opacity of the bright ridge highlight.
        shadow_opacity    : opacity of the dark ridge shadow.
        """
        if ridge_height < 0.01:
            return

        w, h = self.canvas.w, self.canvas.h

        # ── Stage 1: Compute luminance gradient ───────────────────────────────
        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(h, w, 4).copy()
        rgb = buf[:, :, [2, 1, 0]].astype(np.float32) / 255.0
        lum = (0.2126 * rgb[:, :, 0] +
               0.7152 * rgb[:, :, 1] +
               0.0722 * rgb[:, :, 2])

        # Sobel x and y gradients
        gx = ndimage.sobel(lum, axis=1)
        gy = ndimage.sobel(lum, axis=0)

        if blur_sigma > 0.1:
            gx = ndimage.gaussian_filter(gx, sigma=blur_sigma)
            gy = ndimage.gaussian_filter(gy, sigma=blur_sigma)

        # Gradient magnitude — proxy for ridge height
        gmag = np.sqrt(gx ** 2 + gy ** 2)
        if gmag.max() < 1e-6:
            return   # uniform canvas — no ridges to enhance

        gmag = (gmag / gmag.max()).astype(np.float32)

        # ── Stage 2–3: Directional highlight and shadow ───────────────────────
        # Convert light_angle to a unit direction vector (light_dx, light_dy)
        # 0° = from top = (0, -1), 90° = from right = (1, 0), etc.
        angle_rad = math.radians(light_angle)
        # Light arrives FROM this direction; the highlight is on the surface
        # perpendicular facing INTO the light.
        # gy: gradient in Y (positive = brighter below), gx: gradient in X
        # Ridge faces light if dot(gradient_dir, light_dir) > 0
        light_dx = math.sin(angle_rad)    # component pointing right
        light_dy = -math.cos(angle_rad)   # component pointing down (image coords)

        # Normalise gradient direction map
        gnorm = gmag + 1e-8
        gdx = gx / gnorm
        gdy = gy / gnorm

        # Directional component: positive = facing light, negative = shadow
        directional = gdx * light_dx + gdy * light_dy  # in [-1, 1]

        highlight_map = np.clip( directional, 0.0, 1.0) * gmag * ridge_height
        shadow_map    = np.clip(-directional, 0.0, 1.0) * gmag * ridge_height

        ctx = self.canvas.ctx

        # Highlight: warm creamy white
        for row_y in range(h):
            row_max = float(highlight_map[row_y].max())
            if row_max < 0.005:
                continue
            row_alpha = highlight_opacity * row_max
            ctx.set_source_rgba(0.98, 0.96, 0.90, row_alpha)
            ctx.rectangle(0.0, float(row_y), float(w), 1.0)
            ctx.fill()

        # Shadow: cool dark (slightly blue-black to suggest indirect skylight)
        for row_y in range(h):
            row_max = float(shadow_map[row_y].max())
            if row_max < 0.005:
                continue
            row_alpha = shadow_opacity * row_max
            ctx.set_source_rgba(0.05, 0.06, 0.10, row_alpha)
            ctx.rectangle(0.0, float(row_y), float(w), 1.0)
            ctx.fill()

        print(f"  Impasto texture pass complete  "
              f"(angle={light_angle:.0f}°, ridge_height={ridge_height:.2f})")

    # ── Atmospheric depth pass — aerial perspective (Leonardo / Friedrich) ─────

    def atmospheric_depth_pass(
            self,
            haze_color:      Color = (0.72, 0.78, 0.88),  # cool blue-grey haze
            desaturation:    float = 0.65,                  # saturation loss at max depth
            lightening:      float = 0.50,                  # blend toward haze at max depth
            depth_gamma:     float = 1.6,                   # depth curve shape (>1 = effect
                                                            # concentrates near horizon)
            background_only: bool  = True,                  # apply only outside figure mask
    ) -> None:
        """
        Atmospheric depth (aerial perspective) pass.

        Leonardo da Vinci described this phenomenon in *Trattato della Pittura*
        (c. 1490–1510) as *prospettiva aerea* (aerial perspective): the
        atmosphere between the viewer and a distant object scatters and absorbs
        light so that distant surfaces appear progressively —

          1. **Lighter in value** — atmosphere adds a veil of bright sky to
             every distant surface.
          2. **Cooler / bluer** — Rayleigh scattering shifts the apparent colour
             of distant elements toward the blue of the sky.
          3. **Less saturated** — the atmosphere desaturates and blends all
             colours toward the ambient sky tone.
          4. **Lower contrast** — dark darks become less dark; lights become
             less light, as everything resolves toward the same atmospheric grey.

        This pass simulates the effect by reading the current canvas state and
        applying a depth-weighted blend: pixels near the top of the canvas
        (the far sky / distant landscape) receive the strongest atmospheric
        treatment; pixels at the bottom (foreground) are untouched.

        The depth gradient is purely positional (y-axis), which is physically
        correct for landscape paintings where the horizon is always above the
        foreground ground plane.

        Caspar David Friedrich applied aerial perspective with extraordinary
        systematic rigour: each of the three major zones (foreground, middle
        distance, far horizon / sky) is painted in its own atmospheric register,
        each noticeably cooler, lighter, and less saturated than the one below.
        The technique pre-dates photographic depth-of-field but achieves a
        similar sense of spatial recession through colour temperature alone.

        Parameters
        ----------
        haze_color      : The colour toward which distant pixels are blended.
                          Should match the ambient sky / horizon tone.
                          Default: pale blue-grey (0.72, 0.78, 0.88).
        desaturation    : How much to desaturate at maximum depth (0–1).
                          0 = no desaturation; 1 = full greyscale at the horizon.
                          Typical range 0.50–0.75.
        lightening      : How much to blend toward haze_color at maximum depth
                          (0–1).  0 = no atmospheric tinting; 1 = full haze.
                          Typical range 0.35–0.60.
        depth_gamma     : Shape of the depth falloff curve.  Values > 1.0
                          concentrate the atmospheric effect near the horizon;
                          values < 1.0 spread it further into the mid-ground.
                          1.6 (default) gives a convincing natural falloff.
        background_only : If True (default), apply only to the background zone
                          (pixels outside the figure mask).  The figure is left
                          untouched so portrait subjects retain their local colour.
                          Pass False to apply to the whole canvas (landscape-only
                          scenes with no figure mask).

        Notes
        -----
        Friedrich's *Wanderer above the Sea of Fog* (1818) demonstrates the
        three atmospheric zones almost diagrammatically: jet-black pine
        silhouettes at the very bottom; grey-green fog-draped ridges in the
        middle; a pale cerulean-white sky at the top.  Each zone is internally
        consistent and makes the next zone read correctly by contrast.

        Leonardo's own instructions in Trattato della Pittura:
          "Objects at a distance should be less dark and their outlines lost;
           the further you place them the lighter, bluer and more blurred."

        Applies to all landscape-heavy paintings:
        ROMANTIC (Turner, Friedrich), RENAISSANCE landscape bg (Leonardo),
        IMPRESSIONIST exterior (Monet, Pissarro), Ukiyo-e background sky.
        """
        print(f"Atmospheric depth pass  "
              f"(haze={haze_color}  desat={desaturation:.2f}"
              f"  lighten={lightening:.2f}  gamma={depth_gamma:.1f})…")

        w, h = self.canvas.w, self.canvas.h

        # ── Read current canvas buffer ──────────────────────────────────────────
        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(h, w, 4).copy()
        # Cairo stores BGRA; convert to float RGB [0, 1]
        rgb = buf[:, :, [2, 1, 0]].astype(np.float32) / 255.0  # (H, W, 3)

        hr, hg, hb = haze_color

        # ── Build spatial depth map ─────────────────────────────────────────────
        # y=0 is the TOP of the image (most distant / sky);
        # y=H-1 is the BOTTOM (foreground).
        # depth = 1 at the very top, 0 at the very bottom.
        ys = np.arange(h, dtype=np.float32)
        depth_linear = 1.0 - ys / max(h - 1, 1)              # (H,)
        depth        = depth_linear ** depth_gamma             # apply curve
        depth        = depth[:, np.newaxis]                    # (H, 1)  — broadcast over W

        # ── Background mask ─────────────────────────────────────────────────────
        if background_only and self._figure_mask is not None:
            # bg_weight[y, x] = 0 where figure is present, 1 in background.
            bg_weight = np.clip(1.0 - self._figure_mask, 0.0, 1.0)
        else:
            bg_weight = np.ones((h, w), dtype=np.float32)

        # Combined per-pixel effect weight: depth × background_weight
        # Both broadcast over the 3 colour channels.
        effect = (depth * bg_weight)[:, :, np.newaxis]       # (H, W, 1)

        # ── Stage 1: Desaturate toward luminance ─────────────────────────────────
        # Convert to per-pixel luminance (BT.601 weights) and lerp toward it.
        lum = (0.299 * rgb[:, :, 0] +
               0.587 * rgb[:, :, 1] +
               0.114 * rgb[:, :, 2])[:, :, np.newaxis]       # (H, W, 1)

        desaturation_weight = effect * desaturation
        rgb_desat = rgb * (1.0 - desaturation_weight) + lum * desaturation_weight

        # ── Stage 2: Haze blend toward haze_color ────────────────────────────────
        haze_vec = np.array([hr, hg, hb], dtype=np.float32)   # (3,)
        lightening_weight = effect * lightening
        rgb_final = rgb_desat * (1.0 - lightening_weight) + haze_vec * lightening_weight

        rgb_final = np.clip(rgb_final, 0.0, 1.0)

        # ── Write modified pixels back to Cairo surface ──────────────────────────
        # Build BGRA uint8 array: Cairo needs B, G, R, A channel order.
        # Alpha channel is preserved from the original buffer.
        out = np.zeros((h, w, 4), dtype=np.uint8)
        out[:, :, 0] = (rgb_final[:, :, 2] * 255).astype(np.uint8)   # B
        out[:, :, 1] = (rgb_final[:, :, 1] * 255).astype(np.uint8)   # G
        out[:, :, 2] = (rgb_final[:, :, 0] * 255).astype(np.uint8)   # R
        out[:, :, 3] = buf[:, :, 3]                                    # A (preserve)

        out_bytes = bytearray(out.tobytes())
        haze_surf = cairo.ImageSurface.create_for_data(
            out_bytes, cairo.FORMAT_ARGB32, w, h)
        self.canvas.ctx.set_source_surface(haze_surf, 0, 0)
        self.canvas.ctx.paint()

        print(f"  Atmospheric depth complete  "
              f"({h}×{w} canvas, gamma={depth_gamma:.1f})")

    def folk_retablo_pass(
            self,
            ref,
            n_levels:             int   = 4,
            saturation_boost:     float = 1.55,
            outline_thickness:    float = 2.5,
            outline_color:        Color = (0.05, 0.03, 0.02),
            outline_opacity:      float = 0.88,
            boundary_vibration:   bool  = True,
            vibration_width:      float = 1.8,
            vibration_opacity:    float = 0.28,
    ) -> None:
        """
        Folk retablo / ex-voto painting pass.

        Inspired by Frida Kahlo's technique — itself rooted in the Mexican
        retablo tradition of small devotional paintings on metal or masonite —
        this pass transforms the current canvas into a flat, zone-based,
        high-saturation rendering with heavy dark contour outlines at every
        colour boundary.

        Three-stage process
        -------------------
        **Stage 1 — Posterization and saturation boost.**
        Converts the canvas to HSV colour space and quantizes the Value channel
        into ``n_levels`` discrete levels.  The Saturation channel is multiplied
        by ``saturation_boost`` so every colour moves toward its maximum
        intensity.  This models Kahlo's preference for volcanic earth reds,
        deep jungle greens, and Aztec turquoise — none of which are naturalistic;
        all are emotionally driven.

        **Stage 2 — Boundary vibration (simultaneous contrast).**
        This is the key artistic improvement in this session: at every detected
        zone boundary the pass applies a thin warm/cool opposing accent stripe.
        On the side of the boundary closer to a warm tone (R > B), a cool blue-
        grey veil is applied; on the cool side, a warm amber veil is applied.
        This replicates the perceptual "hum" of Kahlo's figure-ground
        relationships — her jungle-green backgrounds read as more vivid because
        the warm figure edge pushes them cooler, and the skin reads as warmer
        because the cool foliage edge pushes it warmer.  Simultaneous contrast
        was first theorised by Chevreul (1839) and used systematically by Seurat,
        but Kahlo applied it intuitively in every work regardless of period.

        **Stage 3 — Contour outlines.**
        Sobel edge detection on the posterized result identifies all zone
        boundaries.  A thick dark (near-black umber) line is composited over
        every strong boundary at ``outline_opacity``.  This directly models the
        retablo craftsman's final step of reinforcing every object boundary with
        a loaded dark-paint contour.

        Parameters
        ----------
        ref               : PIL Image reference for local colour sampling.
        n_levels          : Posterization levels (3 = flat folk, 5 = more tonal).
        saturation_boost  : HSV saturation multiplier (> 1.0 intensifies colour).
                            Kahlo's palette is typically 1.4–1.7× natural saturation.
        outline_thickness : Pixel width of the dark contour strokes.
        outline_color     : RGB colour of the contour lines (near-black umber).
        outline_opacity   : Compositing opacity for the contour overlay (0–1).
        boundary_vibration: Enable simultaneous-contrast warm/cool accent stripes.
        vibration_width   : Width of the accent stripe on each side of a boundary.
        vibration_opacity : Opacity of the vibration stripe (subtle — 0.20–0.35).

        Notes
        -----
        This pass should run AFTER the standard form-building passes
        (underpainting, block_in, build_form) so it has fully rendered subject
        matter to posterize, and BEFORE place_lights() or any final glaze so the
        impasto highlights land on top of the flat zones.

        The ``boundary_vibration`` parameter implements the "random aspect
        improvement" for this session: simultaneous colour contrast at zone
        edges is a general technique that applies to any period with hard colour
        boundaries, including SYNTHETIST, REALIST, and UKIYO_E, but is most
        critical for SURREALIST / folk-art rendering.
        """
        print(f"Folk retablo pass  (levels={n_levels}  sat_boost={saturation_boost:.2f}"
              f"  outline_t={outline_thickness:.1f}  vibration={boundary_vibration})…")

        from PIL import Image as _PILImage
        import colorsys as _cs

        w, h = self.canvas.w, self.canvas.h

        # ── Read current canvas buffer ──────────────────────────────────────────
        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(h, w, 4).copy()
        # Cairo BGRA → float RGB (H, W, 3)
        rgb = buf[:, :, [2, 1, 0]].astype(np.float32) / 255.0

        # ── Stage 1: Posterize + saturation boost ──────────────────────────────
        # Vectorised HSV conversion via scipy/colorsys is slow for large arrays;
        # use a direct numpy approximation instead.

        # RGB → HSV (all in [0, 1])
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        v = np.maximum(np.maximum(r, g), b)                      # Value
        s_denom = np.where(v > 1e-6, v, 1e-6)
        s = (v - np.minimum(np.minimum(r, g), b)) / s_denom      # Saturation

        # Hue (0–6 scale; undefined for achromatic pixels)
        delta = v - np.minimum(np.minimum(r, g), b)
        safe_delta = np.where(delta > 1e-6, delta, 1e-6)
        hue = np.where(
            v == r, (g - b) / safe_delta % 6.0,
            np.where(v == g, (b - r) / safe_delta + 2.0,
                     (r - g) / safe_delta + 4.0)
        )
        hue = hue / 6.0   # normalise to [0, 1]

        # Posterize Value to n_levels discrete steps
        v_steps  = np.round(v * (n_levels - 1)) / (n_levels - 1)

        # Boost saturation; clip to [0, 1]
        s_boosted = np.clip(s * saturation_boost, 0.0, 1.0)

        # HSV → RGB reconstruction
        h6  = hue * 6.0
        hi  = np.floor(h6).astype(np.int32) % 6
        f   = h6 - np.floor(h6)
        p   = v_steps * (1.0 - s_boosted)
        q   = v_steps * (1.0 - s_boosted * f)
        t   = v_steps * (1.0 - s_boosted * (1.0 - f))

        r2 = np.select([hi == 0, hi == 1, hi == 2, hi == 3, hi == 4, hi == 5],
                       [v_steps, q,       p,       p,       t,       v_steps])
        g2 = np.select([hi == 0, hi == 1, hi == 2, hi == 3, hi == 4, hi == 5],
                       [t,       v_steps, v_steps, q,       p,       p])
        b2 = np.select([hi == 0, hi == 1, hi == 2, hi == 3, hi == 4, hi == 5],
                       [p,       p,       t,       v_steps, v_steps, q])

        rgb_post = np.stack([r2, g2, b2], axis=-1).astype(np.float32)
        rgb_post = np.clip(rgb_post, 0.0, 1.0)

        # ── Stage 2: Boundary vibration (simultaneous contrast) ────────────────
        # Detect zone boundaries on the posterized Value image.  Sobel gives a
        # gradient magnitude at every pixel; high magnitude = zone boundary.
        from scipy.ndimage import sobel as _sobel, uniform_filter as _uf
        v_map = v_steps.astype(np.float32)
        gx = _sobel(v_map, axis=1)
        gy = _sobel(v_map, axis=0)
        grad_mag = np.hypot(gx, gy)

        # Normalise gradient magnitude to [0, 1]
        g_max = grad_mag.max()
        if g_max > 1e-6:
            grad_norm = grad_mag / g_max
        else:
            grad_norm = grad_mag

        if boundary_vibration:
            # Determine warmth of each pixel: R-dominance means warm, B-dominance cool.
            warmth = rgb_post[:, :, 0] - rgb_post[:, :, 2]   # (H, W): + = warm, - = cool

            # Boundary zone: use a dilated version of the gradient so the accent
            # stripe has the specified pixel width.
            vib_w = max(1, int(round(vibration_width)))
            boundary_zone = _uf(grad_norm, size=vib_w * 2 + 1)
            boundary_zone = np.clip(boundary_zone / (boundary_zone.max() + 1e-6),
                                    0.0, 1.0)

            # Warm-side accent: cool blue-grey tint
            warm_accent  = np.array([0.60, 0.68, 0.85], dtype=np.float32)
            # Cool-side accent: warm amber tint
            cool_accent  = np.array([0.90, 0.68, 0.38], dtype=np.float32)

            # Select which accent applies at each pixel
            is_warm = (warmth > 0.0)[:, :, np.newaxis]
            accent  = np.where(is_warm, warm_accent, cool_accent)

            vib_weight = (boundary_zone * vibration_opacity)[:, :, np.newaxis]
            rgb_post   = rgb_post * (1.0 - vib_weight) + accent * vib_weight
            rgb_post   = np.clip(rgb_post, 0.0, 1.0)

        # ── Stage 3: Dark contour outlines ─────────────────────────────────────
        # Threshold the gradient at a moderate level to find only the strongest
        # zone boundaries.  Dilate to outline_thickness pixels, then composite
        # the dark outline_color at outline_opacity.
        outline_threshold = 0.30
        outline_mask = (grad_norm > outline_threshold).astype(np.float32)

        # Grow the outline to the requested thickness via uniform filter
        ot = max(1, int(round(outline_thickness)))
        outline_grown = _uf(outline_mask, size=ot * 2 + 1)
        outline_grown = np.clip(outline_grown / (outline_grown.max() + 1e-6),
                                0.0, 1.0)

        or_, og_, ob_ = outline_color
        outline_rgb = np.array([or_, og_, ob_], dtype=np.float32)
        ol_weight   = (outline_grown * outline_opacity)[:, :, np.newaxis]
        rgb_final   = rgb_post * (1.0 - ol_weight) + outline_rgb * ol_weight
        rgb_final   = np.clip(rgb_final, 0.0, 1.0)

        # ── Write back to Cairo surface ─────────────────────────────────────────
        out = np.zeros((h, w, 4), dtype=np.uint8)
        out[:, :, 0] = (rgb_final[:, :, 2] * 255).astype(np.uint8)   # B
        out[:, :, 1] = (rgb_final[:, :, 1] * 255).astype(np.uint8)   # G
        out[:, :, 2] = (rgb_final[:, :, 0] * 255).astype(np.uint8)   # R
        out[:, :, 3] = buf[:, :, 3]                                    # A preserve

        out_bytes = bytearray(out.tobytes())
        retablo_surf = cairo.ImageSurface.create_for_data(
            out_bytes, cairo.FORMAT_ARGB32, w, h)
        self.canvas.ctx.set_source_surface(retablo_surf, 0, 0)
        self.canvas.ctx.paint()

        # Final pass: place a handful of loaded thick strokes along the main
        # figure contours in the outline colour to reinforce the retablo outline.
        rng = random.Random(77)
        n_contour = int(outline_thickness * 200)
        for _ in range(n_contour):
            yw = rng.randint(0, h - 1)
            xw = rng.randint(0, w - 1)
            # Sample gradient at this point — only draw where there is a strong edge
            if rng.random() > float(grad_norm[yw, xw]):
                continue
            length = outline_thickness * 3.0
            angle  = math.atan2(float(gy[yw, xw] + 1e-9),
                                 float(gx[yw, xw] + 1e-9)) + math.pi / 2.0
            x2 = xw + length * math.cos(angle)
            y2 = yw + length * math.sin(angle)
            self.canvas.ctx.set_source_rgba(or_, og_, ob_, outline_opacity * 0.60)
            self.canvas.ctx.set_line_width(outline_thickness * 0.7)
            self.canvas.ctx.move_to(float(xw), float(yw))
            self.canvas.ctx.line_to(float(x2), float(y2))
            self.canvas.ctx.stroke()

        print(f"  Folk retablo pass complete  "
              f"({h}×{w}, {n_levels} levels, vib={'on' if boundary_vibration else 'off'})")

    def geometric_resonance_pass(self,
                                 reference:      Union[np.ndarray, Image.Image],
                                 n_circles:      int   = 12,
                                 n_triangles:    int   = 8,
                                 n_lines:        int   = 18,
                                 shape_opacity:  float = 0.18,
                                 min_radius:     float = 0.04,
                                 max_radius:     float = 0.18,
                                 line_thickness: float = 2.0,
                                 seed:           int   = 42):
        """
        Geometric Resonance Pass — inspired by Wassily Kandinsky.

        Kandinsky believed each geometric form carried an intrinsic emotional
        and acoustic resonance that could be used to compose a painting the way
        a musician composes a symphony.  In "Concerning the Spiritual in Art"
        (1911) and in his Bauhaus colour theory course he mapped:

          • Yellow / triangle  — sharp, advancing, trumpet-like energy
          • Blue   / circle    — receding, heavenly, cello-deep resonance
          • Red    / square    — earthbound, stable, drumbeat warmth
          • Black  / line      — tension, boundary, the silence after sound

        This pass scatters floating geometric primitives across the canvas:

          1. Circles in cool-blue resonance zones  (Kandinsky's "cosmic" form)
          2. Triangles in warm-yellow/orange zones  (his "active" pointing form)
          3. Radiating tension lines from focal points  (his "musical notations")

        Each primitive samples a harmonically-related colour from the region
        beneath it, then applies it at low opacity — the underlying painting
        remains legible.  The effect gives any composition an internally
        vibrating, musical quality as if solid form is dissolving into sensation.

        Parameters
        ----------
        reference     : PIL Image or ndarray used for colour sampling.
        n_circles     : Number of floating circles to overlay.
        n_triangles   : Number of floating triangles to overlay.
        n_lines       : Number of radiating tension lines to overlay.
        shape_opacity : Base alpha for each geometric primitive (0.05–0.35).
                        Keep low so underlying painting reads through.
        min_radius    : Smallest circle/triangle radius as fraction of canvas W.
        max_radius    : Largest circle/triangle radius as fraction of canvas W.
        line_thickness: Stroke width for tension lines, in pixels.
        seed          : Random seed for reproducible placement.
        """
        print(f"Geometric resonance pass  (circles={n_circles}, tri={n_triangles}, "
              f"lines={n_lines}, opacity={shape_opacity:.2f})…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = rarr.shape[:2]
        ctx  = self.canvas.ctx
        rng  = random.Random(seed)

        def _sample_region_color(cx: float, cy: float, radius: float) -> Color:
            """Sample the mean RGB of a disc region in the reference."""
            x0 = max(0, int(cx - radius))
            x1 = min(w, int(cx + radius) + 1)
            y0 = max(0, int(cy - radius))
            y1 = min(h, int(cy + radius) + 1)
            patch = rarr[y0:y1, x0:x1]
            if patch.size == 0:
                return (0.5, 0.5, 0.5)
            return (float(patch[:, :, 0].mean()),
                    float(patch[:, :, 1].mean()),
                    float(patch[:, :, 2].mean()))

        def _resonance_color(base: Color) -> Color:
            """
            Map a sampled base colour to its Kandinsky resonance complement.

            Cool blue zones → circle drawn in luminous warm yellow (advancing)
            Warm yellow zones → triangle drawn in deep ultramarine (contrasting)
            Neutral/grey zones → drawn in pure saturated version of dominant hue
            All colours are slightly over-saturated to read through the painting.
            """
            import colorsys as _cs
            h_hsv, s_hsv, v_hsv = _cs.rgb_to_hsv(*base)
            # Boost saturation so the resonance colour sings above the ground
            s_boosted = min(1.0, s_hsv * 1.6 + 0.2)
            # Rotate hue toward warm complement: cool hues → warm, warm → cool
            # (hue rotation is 0.5 = 180° = complementary)
            hue_complement = (h_hsv + 0.5) % 1.0
            r, g, b = _cs.hsv_to_rgb(hue_complement, s_boosted, min(1.0, v_hsv + 0.1))
            return (r, g, b)

        def _set_resonance_source(base: Color):
            r, g, b = _resonance_color(base)
            ctx.set_source_rgba(r, g, b, shape_opacity)

        # ── 1. Floating circles  (Kandinsky: cosmic / blue / receding) ─────────
        for _ in range(n_circles):
            cx = rng.uniform(0.0, float(w))
            cy = rng.uniform(0.0, float(h))
            r  = rng.uniform(min_radius * w, max_radius * w)
            base = _sample_region_color(cx, cy, r * 0.5)

            # Unfilled circle ring — resonance at the boundary only
            _set_resonance_source(base)
            ctx.set_line_width(max(1.0, r * 0.06))
            ctx.arc(cx, cy, r, 0, 2 * math.pi)
            ctx.stroke()

            # Optionally add a very faint interior fill for larger circles
            if r > min_radius * w * 2.5:
                r2, g2, b2 = _resonance_color(base)
                ctx.set_source_rgba(r2, g2, b2, shape_opacity * 0.25)
                ctx.arc(cx, cy, r, 0, 2 * math.pi)
                ctx.fill()

        # ── 2. Floating triangles  (Kandinsky: active / yellow / advancing) ───
        for _ in range(n_triangles):
            cx  = rng.uniform(0.05 * w, 0.95 * w)
            cy  = rng.uniform(0.05 * h, 0.95 * h)
            r   = rng.uniform(min_radius * w, max_radius * w * 0.80)
            # Random rotation so triangles point in varied directions
            angle_offset = rng.uniform(0, 2 * math.pi)
            base = _sample_region_color(cx, cy, r * 0.5)

            # Compute equilateral triangle vertices
            verts = []
            for k in range(3):
                a = angle_offset + k * (2 * math.pi / 3)
                verts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

            _set_resonance_source(base)
            ctx.set_line_width(max(1.0, r * 0.05))
            ctx.move_to(*verts[0])
            ctx.line_to(*verts[1])
            ctx.line_to(*verts[2])
            ctx.close_path()
            ctx.stroke()

        # ── 3. Radiating tension lines  (Kandinsky: the musical notation) ─────
        # Lines radiate outward from N focal points distributed across the canvas.
        # Each line samples the colour of the region it crosses and draws its
        # resonance complement, creating chromatic tension along its length.
        n_foci = max(2, n_lines // 5)
        foci   = [(rng.uniform(0.2 * w, 0.8 * w),
                   rng.uniform(0.2 * h, 0.8 * h))
                  for _ in range(n_foci)]

        lines_per_focus = max(1, n_lines // n_foci)
        for fx, fy in foci:
            for _ in range(lines_per_focus):
                angle    = rng.uniform(0, 2 * math.pi)
                length   = rng.uniform(0.06 * w, 0.35 * w)
                x2       = fx + length * math.cos(angle)
                y2       = fy + length * math.sin(angle)
                mid_x    = (fx + x2) / 2.0
                mid_y    = (fy + y2) / 2.0
                base     = _sample_region_color(mid_x, mid_y, line_thickness * 3)

                r_c, g_c, b_c = _resonance_color(base)
                ctx.set_source_rgba(r_c, g_c, b_c, shape_opacity * 0.75)
                ctx.set_line_width(line_thickness)
                ctx.move_to(fx, fy)
                ctx.line_to(x2, y2)
                ctx.stroke()

        print(f"  Geometric resonance complete  "
              f"({n_circles} circles, {n_triangles} triangles, {n_lines} lines)")
