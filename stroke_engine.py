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
from art_utils import Composition

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
        # Composition weight map: (H, W) float32 — relative stroke placement bias.
        # Built via _build_composition_map() and stored here so _place_strokes()
        # picks it up automatically without requiring every call site to pass it.
        self._comp_map: Optional[np.ndarray] = None

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

    def dappled_light_pass(
            self,
            reference:          "Union[np.ndarray, Image.Image]",
            n_pools:            int   = 38,
            pool_radius:        float = 0.065,
            light_color:        Color = (1.00, 0.97, 0.82),
            shadow_color:       Color = (0.62, 0.58, 0.80),
            light_intensity:    float = 0.28,
            shadow_intensity:   float = 0.14,
            scatter_jitter:     float = 0.18,
            lum_gate:           float = 0.30,
            blur_sigma:         float = 3.5,
    ):
        """
        Dappled light pass — inspired by Joaquín Sorolla's luminismo.

        Sorolla's outdoor paintings are defined by broken pools of Mediterranean
        sunlight scattered across figures, fabric, and water.  Direct sunlight
        filters through leaves (or reflects off water) to create irregular,
        overlapping patches of warm brilliance surrounded by cool violet shadow.

        This pass simulates that effect entirely in the painted pixel buffer:

        1. **Pool placement** — ``n_pools`` elliptical masks are placed pseudo-
           randomly across the canvas, biased toward mid-luminance areas (the
           brightly-lit regions where the effect is most readable).

        2. **Warm light dabs** — inside each pool the canvas is nudged toward
           ``light_color`` (warm golden-white) proportional to ``light_intensity``.
           The shift is strongest at the pool centre and falls off with a Gaussian
           envelope, so each patch is softer at its perimeter — imitating the
           penumbral edge of filtered sunlight.

        3. **Cool violet shadow fringe** — immediately outside each pool the
           complement effect kicks in: the shadow side is shifted toward
           ``shadow_color`` (cool violet / blue) at ``shadow_intensity``.
           This simultaneous contrast is the defining Sorolla move: warm light
           makes the adjacent shadow *cooler and more violet* by comparison.

        4. **Specular impasto dot** — at each pool's brightest point a single
           very bright near-white dab (radius ≈ pool_radius × 0.12) marks the
           direct specular highlight.  In Sorolla's technique these dots are
           painted last with a heavily loaded brush.

        The pass works in float32 pixel space for accuracy, then writes back to
        the Cairo ARGB32 surface — exactly like ``pigment_granulation_pass``.

        Parameters
        ----------
        reference        : Reference image for luminance-biased placement.
        n_pools          : Number of light pools to scatter.
        pool_radius      : Pool radius as a fraction of canvas width (0.03–0.12).
        light_color      : Warm sunlight colour to push into pool centres.
        shadow_color     : Cool shadow/violet colour for pool fringes.
        light_intensity  : Maximum lightening strength inside each pool (0–1).
        shadow_intensity : Maximum shadow fringe shift (0–1).
        scatter_jitter   : Fraction of canvas added as uniform random noise to
                           pool positions beyond the luminance-biased grid.
        lum_gate         : Only place pools over pixels above this luminance —
                           avoids scattering light into already-dark shadow areas.
        blur_sigma       : Gaussian sigma (px) for pool envelope softening.
        """
        print(f"Dappled light pass  (n_pools={n_pools}  "
              f"radius={pool_radius:.3f}  intensity={light_intensity:.2f})…")

        ref = self._prep(reference)
        h, w = self.h, self.w
        rng  = random.Random(42)           # deterministic within a painting session

        # ── Read current canvas ───────────────────────────────────────────────
        buf  = np.frombuffer(self.canvas.surface.get_data(),
                             dtype=np.uint8).reshape(h, w, 4).copy()
        carr = buf[:, :, [2, 1, 0]].astype(np.float32) / 255.0   # BGR→RGB

        # ── Reference luminance for placement bias ────────────────────────────
        ref_lum = (0.299 * ref[:, :, 0] +
                   0.587 * ref[:, :, 1] +
                   0.114 * ref[:, :, 2])

        # Build a candidate set: pixels above lum_gate
        bright_ys, bright_xs = np.where(ref_lum > lum_gate)
        if bright_ys.size == 0:
            bright_ys, bright_xs = np.where(ref_lum >= 0)   # fallback: anywhere

        # Pixel radius
        radius_px = max(6, int(pool_radius * w))

        # Accumulator for light and shadow shifts — summed, then applied once
        light_acc  = np.zeros((h, w), dtype=np.float32)   # +lightening
        shadow_acc = np.zeros((h, w), dtype=np.float32)   # +shadow fringe

        ys_f = np.arange(h, dtype=np.float32)
        xs_f = np.arange(w, dtype=np.float32)

        for _ in range(n_pools):
            # Sample a candidate pixel, biased toward bright areas
            idx = rng.randrange(len(bright_ys))
            cy  = int(bright_ys[idx] + rng.uniform(-scatter_jitter * h,
                                                     scatter_jitter * h))
            cx  = int(bright_xs[idx] + rng.uniform(-scatter_jitter * w,
                                                     scatter_jitter * w))
            cy  = max(0, min(h - 1, cy))
            cx  = max(0, min(w - 1, cx))

            # Elliptical Gaussian pool envelope (slight aspect-ratio variation)
            rx  = radius_px * rng.uniform(0.75, 1.25)
            ry  = radius_px * rng.uniform(0.75, 1.25)

            # Distance grid — vectorised
            dy  = (ys_f[:, np.newaxis] - cy) / max(ry, 1)
            dx  = (xs_f[np.newaxis, :] - cx) / max(rx, 1)
            d2  = dx * dx + dy * dy

            # Gaussian core: peaks at the pool centre (d2=0)
            gauss  = np.exp(-d2 * 1.8).astype(np.float32)

            # Shadow fringe: annular region just outside the core
            fringe = np.exp(-((d2 - 1.0) ** 2) * 2.5).astype(np.float32)
            fringe = np.where(d2 > 0.6, fringe, 0.0).astype(np.float32)

            light_acc  += gauss  * rng.uniform(0.65, 1.0)
            shadow_acc += fringe * rng.uniform(0.50, 1.0)

        # Normalise accumulators so overlapping pools don't over-saturate
        max_l = light_acc.max()
        max_s = shadow_acc.max()
        if max_l > 0:
            light_acc  /= max_l
        if max_s > 0:
            shadow_acc /= max_s

        # Optional Gaussian blur to soften pool boundaries
        if blur_sigma > 0:
            light_acc  = ndimage.gaussian_filter(light_acc,  sigma=blur_sigma)
            shadow_acc = ndimage.gaussian_filter(shadow_acc, sigma=blur_sigma)

        light_acc  = light_acc.clip(0, 1)
        shadow_acc = shadow_acc.clip(0, 1)

        # ── Warm light shift ──────────────────────────────────────────────────
        lc = np.array(light_color,  dtype=np.float32)
        sc = np.array(shadow_color, dtype=np.float32)

        out = carr.copy()
        for c in range(3):
            # Blend each pixel toward light_color proportional to pool presence
            out[:, :, c] = (carr[:, :, c]
                            + (lc[c] - carr[:, :, c]) * light_acc  * light_intensity
                            + (sc[c] - carr[:, :, c]) * shadow_acc * shadow_intensity)
        out = out.clip(0.0, 1.0)

        # ── Specular impasto dot at each pool centre ──────────────────────────
        # A single very bright near-white dab at the pool core — the small
        # loaded-brush impasto mark that catches the eye in Sorolla's work.
        # Only placed when light is actually being applied (intensity > 0).
        if light_intensity > 0:
            spec_r = max(2, int(radius_px * 0.12))
            spec_c = np.array([1.00, 0.98, 0.90], dtype=np.float32)
            ys_g, xs_g = np.ogrid[:h, :w]
            for _ in range(min(n_pools, 12)):   # only the first 12 pools get specular dots
                idx = rng.randrange(len(bright_ys))
                cy  = int(bright_ys[idx])
                cx  = int(bright_xs[idx])
                dg  = (ys_g - cy) ** 2 + (xs_g - cx) ** 2
                within = dg <= spec_r ** 2
                for c in range(3):
                    out[:, :, c] = np.where(within,
                                            out[:, :, c] * 0.25 + spec_c[c] * 0.75,
                                            out[:, :, c])

        out = out.clip(0.0, 1.0)

        # ── Write back to Cairo surface ───────────────────────────────────────
        buf[:, :, 2] = np.clip(out[:, :, 0] * 255, 0, 255).astype(np.uint8)  # R→G2
        buf[:, :, 1] = np.clip(out[:, :, 1] * 255, 0, 255).astype(np.uint8)  # G→G1
        buf[:, :, 0] = np.clip(out[:, :, 2] * 255, 0, 255).astype(np.uint8)  # B→G0
        buf[:, :, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print("  Dappled light complete.")

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

    # ── Composition helpers ───────────────────────────────────────────────────

    def _build_composition_map(self,
                               focal_xy: tuple = None,
                               strength: float = 0.6) -> np.ndarray:
        """
        Build a composition weight map with soft peaks at rule-of-thirds and
        golden-ratio intersections, plus a focal point boost.

        Returns a (H, W) float32 array where values > 1.0 attract strokes and
        values < 1.0 repel them.  Mean is normalised to 1.0 so the map is a
        relative bias, not an absolute scale.

        Parameters
        ----------
        focal_xy : (x, y) normalised focal point.  If provided, an extra
                   stronger Gaussian is added at that position.
        strength : 0 = no bias (returns uniform 1.0); 1 = full bias.
        """
        w, h = self.w, self.h
        cmap = np.ones((h, w), dtype=np.float32)

        if strength < 1e-6:
            return cmap

        comp   = Composition(w, h)
        thirds = comp.thirds()
        golden = comp.golden()
        sigma  = min(w, h) * 0.12

        # Rule-of-thirds intersections: (x1,y1), (x1,y2), (x2,y1), (x2,y2)
        thirds_pts = [
            (thirds['x1'], thirds['y1']),
            (thirds['x1'], thirds['y2']),
            (thirds['x2'], thirds['y1']),
            (thirds['x2'], thirds['y2']),
        ]
        # Golden-ratio intersection: single point
        golden_pts = [(golden['x'], golden['y'])]

        ys, xs = np.ogrid[:h, :w]

        for px, py in thirds_pts + golden_pts:
            bump = np.exp(-((xs - px) ** 2 + (ys - py) ** 2) / (2.0 * sigma ** 2))
            cmap += bump.astype(np.float32)

        # Optional focal-point boost — stronger, tighter Gaussian
        if focal_xy is not None:
            fx = focal_xy[0] * w
            fy = focal_xy[1] * h
            sigma_f = min(w, h) * 0.08
            focal_bump = 1.5 * np.exp(
                -((xs - fx) ** 2 + (ys - fy) ** 2) / (2.0 * sigma_f ** 2)
            )
            cmap += focal_bump.astype(np.float32)

        # Lerp between uniform 1.0 and the biased map according to strength
        cmap = 1.0 + (cmap - 1.0) * strength

        # Normalise so the mean is 1.0 — preserves overall stroke density
        mean = cmap.mean()
        if mean > 1e-9:
            cmap /= mean

        # Clip: never suppress strokes entirely; never over-concentrate
        cmap = np.clip(cmap, 0.5, 3.0)
        return cmap.astype(np.float32)

    def _derive_focal_xy(self) -> tuple:
        """
        Derive the focal point as normalised (x, y) from the figure mask.

        Uses the centroid of the top 40% of the figure mask, which typically
        captures the head and upper-chest region.  Falls back to (0.50, 0.35)
        when no figure mask is loaded.
        """
        if self._figure_mask is None:
            return (0.50, 0.35)

        h, w = self._figure_mask.shape[:2]

        # Resize mask to canvas dimensions if needed
        if h != self.h or w != self.w:
            from PIL import Image as _PILImg
            m_img = _PILImg.fromarray((self._figure_mask * 255).astype(np.uint8))
            m_img = m_img.resize((self.w, self.h), _PILImg.NEAREST)
            mask = np.array(m_img, dtype=np.float32) / 255.0
            h, w = self.h, self.w
        else:
            mask = self._figure_mask

        # Crop to the top 40% of the canvas — head / upper-chest zone
        crop_h = int(h * 0.40)
        top_mask = mask[:crop_h, :]

        ys_nz, xs_nz = np.nonzero(top_mask > 0.5)
        if ys_nz.size == 0:
            # No figure pixels in the top region — fall back to default
            return (0.50, 0.35)

        cx = float(xs_nz.mean()) / w
        cy = float(ys_nz.mean()) / h
        return (cx, cy)

    # ── Atmospheric passes ────────────────────────────────────────────────────

    def _atmosphere_fog_pass(self,
                             atmosphere: float,
                             fog_color:  tuple = (0.85, 0.88, 0.92)):
        """
        Apply atmospheric haze to background pixels only.

        atmosphere : 0.0 = clear, 1.0 = heavy fog.
        fog_color  : RGB (float) of the haze colour.  Default is a cool
                     atmospheric blue-grey reminiscent of aerial perspective.

        Only modifies pixels outside the figure mask.  If no mask is set,
        the haze is applied uniformly (background-only behaviour is preserved
        wherever a mask exists).
        """
        if atmosphere < 0.01:
            return

        print(f"  Atmosphere fog pass  (atmosphere={atmosphere:.2f}  "
              f"fog={fog_color})")

        h, w = self.h, self.w
        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(h, w, 4).copy()
        # Cairo ARGB32 stores pixels as BGRA in memory
        R = buf[:, :, 2].astype(np.float32) / 255.0
        G = buf[:, :, 1].astype(np.float32) / 255.0
        B = buf[:, :, 0].astype(np.float32) / 255.0

        # Background mask: 1.0 where no figure, 0.0 over figure
        if self._figure_mask is not None:
            fig = self._figure_mask
            if fig.shape != (h, w):
                from PIL import Image as _PILImg
                m_img = _PILImg.fromarray((fig * 255).astype(np.uint8))
                fig = np.array(m_img.resize((w, h), _PILImg.NEAREST),
                               dtype=np.float32) / 255.0
            bg_mask = 1.0 - fig
        else:
            bg_mask = np.ones((h, w), dtype=np.float32)

        # Blend coefficient: atmosphere * bg_mask, scaled to 0.7 max
        t = np.clip(atmosphere * bg_mask * 0.7, 0.0, 1.0)

        fr, fg, fb = fog_color

        # Slight Gaussian blur in background only — depth-of-field haze
        if atmosphere > 0.05:
            sigma = atmosphere * 2.5
            R_blurred = ndimage.gaussian_filter(R, sigma=sigma)
            G_blurred = ndimage.gaussian_filter(G, sigma=sigma)
            B_blurred = ndimage.gaussian_filter(B, sigma=sigma)
            # Only use blurred values in background region
            R = R + bg_mask * (R_blurred - R)
            G = G + bg_mask * (G_blurred - G)
            B = B + bg_mask * (B_blurred - B)

        # Blend toward fog colour in background
        R_out = R * (1.0 - t) + fr * t
        G_out = G * (1.0 - t) + fg * t
        B_out = B * (1.0 - t) + fb * t

        # Write back (BGRA layout)
        buf[:, :, 2] = np.clip(R_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(G_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip(B_out * 255, 0, 255).astype(np.uint8)

        surface_data = self.canvas.surface.get_data()
        surface_buf  = np.frombuffer(surface_data, dtype=np.uint8).reshape(h, w, 4)
        surface_buf[:] = buf

    def background_environment_pass(self,
                                     ref:         np.ndarray,
                                     env_type:    str,
                                     description: str   = "",
                                     atmosphere:  float = 0.0):
        """
        Paint an environment-specific background behind the figure.

        Strokes are placed only in the background region (outside the figure
        mask).  If no figure mask is loaded the pass has no effect.

        Parameters
        ----------
        ref         : Reference image array (H, W, 3/4 uint8).
        env_type    : One of 'INTERIOR', 'EXTERIOR', 'LANDSCAPE', 'ABSTRACT'.
        description : Optional scene description (not used by current branches
                      but available for future narrative-driven colour sampling).
        atmosphere  : 0.0 = clear, 1.0 = heavy fog.  Passed to
                      _atmosphere_fog_pass() after painting.
        """
        if self._figure_mask is None:
            return

        print(f"  Background environment pass  (env_type={env_type}  "
              f"atmosphere={atmosphere:.2f})")

        ref_arr = self._prep(ref)
        h, w    = self.h, self.w
        bg_mask = 1.0 - self._figure_mask

        rarr = ref_arr[:, :, :3].astype(np.float32) / 255.0

        if env_type == "INTERIOR":
            # Warm, enclosed space: architectural recession lines + floor gradient
            # + ambient warm light on one side.

            # Large atmospheric strokes in warm shadow tones
            self._place_strokes(
                ref_arr,
                stroke_size  = 75,
                n_strokes    = 40,
                opacity      = 0.30,
                wet_blend    = 0.10,
                jitter_amt   = 0.025,
                curvature    = 0.02,
                tip          = BrushTip(BrushTip.FLAT),
                stroke_mask  = bg_mask,
            )

            # Floor plane suggestion — horizontal gradient darkening at bottom third.
            # We paint opaque dark strokes across the lower background region.
            floor_mask = bg_mask.copy()
            floor_y0 = int(h * 0.65)
            floor_mask[:floor_y0, :] = 0.0   # only active below 65% height

            buf = np.frombuffer(self.canvas.surface.get_data(),
                                dtype=np.uint8).reshape(h, w, 4).copy()
            for row in range(floor_y0, h):
                # Darkening ramp: 0 at floor_y0, max at bottom
                t_floor = (row - floor_y0) / max(1, h - floor_y0)
                darken  = t_floor * 0.18
                for ch, bgra_idx in ((0, 2), (1, 1), (2, 0)):
                    col_arr = buf[row, :, bgra_idx].astype(np.float32) / 255.0
                    col_arr = np.clip(col_arr * (1.0 - darken * bg_mask[row, :]),
                                      0.0, 1.0)
                    buf[row, :, bgra_idx] = (col_arr * 255).astype(np.uint8)
            surface_data = self.canvas.surface.get_data()
            surface_buf  = np.frombuffer(surface_data,
                                         dtype=np.uint8).reshape(h, w, 4)
            surface_buf[:] = buf

            # Warm ambient light on left side — lighter strokes on the left
            left_mask = bg_mask.copy()
            left_mask[:, w//2:] = 0.0    # left half only
            self._place_strokes(
                ref_arr,
                stroke_size  = 85,
                n_strokes    = 20,
                opacity      = 0.25,
                wet_blend    = 0.12,
                jitter_amt   = 0.020,
                curvature    = 0.03,
                tip          = BrushTip(BrushTip.FLAT),
                stroke_mask  = left_mask,
                override_color = (0.78, 0.64, 0.45),   # warm amber ambient
            )

        elif env_type in ("EXTERIOR", "LANDSCAPE"):
            # Sky / horizon / ground three-zone treatment.

            sky_mask    = bg_mask.copy()
            horizon_mask = bg_mask.copy()
            ground_mask  = bg_mask.copy()

            sky_y1     = int(h * 0.45)
            horizon_y0 = int(h * 0.40)
            horizon_y1 = int(h * 0.55)
            ground_y0  = int(h * 0.55)

            sky_mask[sky_y1:, :]     = 0.0
            horizon_mask[:horizon_y0, :] = 0.0
            horizon_mask[horizon_y1:, :] = 0.0
            ground_mask[:ground_y0, :]   = 0.0

            # Sky: broad horizontal strokes, light airy tones
            sky_color = (0.62, 0.76, 0.88)   # pale blue sky
            self._place_strokes(
                ref_arr,
                stroke_size   = 90,
                n_strokes     = 10,
                opacity       = 0.35,
                wet_blend     = 0.14,
                jitter_amt    = 0.018,
                curvature     = 0.01,
                tip           = BrushTip(BrushTip.FLAT),
                stroke_mask   = sky_mask,
                override_color = sky_color,
            )

            # Horizon: atmospheric haze blending sky into ground
            horizon_color = (0.72, 0.74, 0.70)   # neutral mid-tone haze
            self._place_strokes(
                ref_arr,
                stroke_size   = 80,
                n_strokes     = 6,
                opacity       = 0.30,
                wet_blend     = 0.16,
                jitter_amt    = 0.020,
                curvature     = 0.01,
                tip           = BrushTip(BrushTip.FLAT),
                stroke_mask   = horizon_mask,
                override_color = horizon_color,
            )

            # Ground: darker, warmer strokes
            ground_color = (0.42, 0.38, 0.28)   # earth tone
            self._place_strokes(
                ref_arr,
                stroke_size   = 80,
                n_strokes     = 8,
                opacity       = 0.38,
                wet_blend     = 0.12,
                jitter_amt    = 0.022,
                curvature     = 0.02,
                tip           = BrushTip(BrushTip.FLAT),
                stroke_mask   = ground_mask,
                override_color = ground_color,
            )

            # LANDSCAPE only: atmospheric mid-tone suggesting distant hills
            if env_type == "LANDSCAPE":
                hill_mask = bg_mask.copy()
                hill_y0 = int(h * 0.40)
                hill_y1 = int(h * 0.50)
                hill_mask[:hill_y0, :] = 0.0
                hill_mask[hill_y1:, :] = 0.0
                hill_color = (0.48, 0.56, 0.50)   # cool atmospheric hill green
                self._place_strokes(
                    ref_arr,
                    stroke_size   = 70,
                    n_strokes     = 5,
                    opacity       = 0.40,
                    wet_blend     = 0.14,
                    jitter_amt    = 0.025,
                    curvature     = 0.04,
                    tip           = BrushTip(BrushTip.FLAT),
                    stroke_mask   = hill_mask,
                    override_color = hill_color,
                )

        else:
            # ABSTRACT / fallback: large atmospheric strokes, no theme.
            self._place_strokes(
                ref_arr,
                stroke_size = 60,
                n_strokes   = 60,
                opacity     = 0.40,
                wet_blend   = 0.10,
                jitter_amt  = 0.020,
                curvature   = 0.04,
                tip         = BrushTip(BrushTip.FLAT),
                stroke_mask = bg_mask,
            )

        # Apply atmospheric fog on top of the painted background
        if atmosphere > 0.01:
            self._atmosphere_fog_pass(atmosphere)

    def _place_strokes(self,
                       ref:              np.ndarray,
                       stroke_size:      float,
                       n_strokes:        int,
                       opacity:          float,
                       wet_blend:        float,
                       jitter_amt:       float,
                       curvature:        float,
                       tip:              BrushTip,
                       stroke_mask:      Optional[np.ndarray] = None,
                       override_color:   Optional[Color]      = None,
                       composition_map:  Optional[np.ndarray] = None):
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

        composition_map — optional (H, W) float32 weight array.  When
            provided, multiplied into the error map after region masking so
            stroke placement is biased toward compositionally significant areas
            (rule-of-thirds / golden-ratio intersections, focal point).  A
            value of 1.0 is neutral; values > 1.0 attract strokes; values
            < 1.0 repel strokes.  If None and self._comp_map is set, that
            stored map is used automatically.
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

        # Composition map — bias stroke placement toward significant anchor areas.
        # Falls back to self._comp_map if no per-call map is given.
        _cmap = composition_map if composition_map is not None else self._comp_map
        if _cmap is not None:
            err = err * _cmap

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

    def venetian_glaze_pass(self,
                            reference:       Union[np.ndarray, Image.Image],
                            n_glaze_layers:  int   = 6,
                            glaze_warmth:    float = 0.55,
                            shadow_depth:    float = 0.72,
                            impasto_strokes: int   = 400,
                            impasto_size:    float = 7.0,
                            impasto_opacity: float = 0.85):
        """
        Venetian glaze pass — inspired by Titian's colorist technique.

        Titian built his paintings through accumulating transparent warm glazes
        over a white underpaint.  The layered structure produces flesh tones of
        extraordinary luminosity: light penetrates the transparent colour layers,
        reflects off the white ground beneath, and returns through the glazes —
        a visual analog of subsurface light scattering in real skin.

        The pass has three stages:

          1. Transparent shadow glazes: warm red-umber glaze layers are applied
             to all areas darker than a luminance threshold.  Shadow areas deepen
             with warm umber rather than cool grey — the Venetian principle that
             shadows are warm, not cold.  Multiple thin layers accumulate to
             produce depth without opacity.

          2. Mid-tone colour enrichment: short gestural strokes are applied with
             the Venetian vermilion-gold palette, with moderate wet_blend.  These
             represent Titian's active wet-into-wet working method where colours
             are pushed and pulled across the wet surface before each layer dries.

          3. Impasto highlights: thick, directional highlight strokes in near-
             white to warm ivory are placed only at the highest luminance peaks
             (lum > 0.70).  These represent the loaded-brush impasto that gives
             Titian's surfaces their three-dimensional, relief-like quality.
             Titian's impasto reads as physically built-up paint even in
             reproduction — light catches the edges of thick strokes.

        Parameters
        ----------
        reference       : PIL Image or ndarray — painted base to glaze over.
        n_glaze_layers  : Number of transparent shadow glaze passes.
                          6–9 gives the characteristic Venetian depth; fewer
                          looks too thin, more can muddy the shadows.
        glaze_warmth    : Warmth of the shadow glaze (0 = neutral umber,
                          1 = full warm vermilion).  Titian's glazes are
                          distinctly warm — a value of 0.5–0.65 is authentic.
        shadow_depth    : Luminance threshold below which shadow glazing
                          is applied (0 = only deepest shadows, 1 = everywhere).
                          0.65–0.80 is appropriate; too high flattens lit areas.
        impasto_strokes : Number of loaded highlight strokes for the impasto
                          stage.  300–600 for a half-length portrait.
        impasto_size    : Mean brush radius for impasto strokes (pixels).
                          Titian's impasto is bold — 6–12px is appropriate.
        impasto_opacity : Opacity of impasto strokes.  High (0.80–0.95) so the
                          highlights are physically opaque, as in real impasto.
        """
        print(f"Venetian glaze pass  ({n_glaze_layers} glaze layers  "
              f"warmth={glaze_warmth:.2f}  impasto={impasto_strokes} strokes)…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        lum = (0.299 * rarr[:, :, 0] + 0.587 * rarr[:, :, 1] + 0.114 * rarr[:, :, 2])

        # ── Stage 1: Transparent warm shadow glazes ───────────────────────────
        # Titian's signature move: warm umber deepens shadows while preserving
        # their transparency.  Each glaze is a thin wash of warm-red tone,
        # masked to shadow regions.  The accumulated effect produces the
        # characteristic "glowing dark" of Venetian painting.
        warm_shadow_a = (0.55, 0.28, 0.12)   # warm red-umber base
        warm_shadow_b = (0.72, 0.40, 0.18)   # vermilion-shifted warm glaze
        ctx = self.canvas.ctx

        shadow_mask = np.clip((shadow_depth - lum) / max(shadow_depth, 0.01), 0.0, 1.0)
        if self._figure_mask is not None:
            shadow_mask = shadow_mask * self._figure_mask

        for i in range(n_glaze_layers):
            t = (i + 1) / n_glaze_layers
            # Alternate between warm umber and vermilion across layers —
            # Titian interleaved pigment types for chromatic complexity
            glaze_col = tuple(
                warm_shadow_a[c] * (1 - glaze_warmth) + warm_shadow_b[c] * glaze_warmth
                for c in range(3)
            )

            # Build glaze layer: current canvas colour shifted toward glaze_col
            # in shadow regions, at very low per-layer opacity (accumulates)
            per_layer_opacity = 0.055 * (0.7 + 0.3 * t)   # slightly heavier in later layers

            # ARGB32 premultiplied — shadow mask controls where glaze lands
            glaze_arr = np.zeros((h, w, 4), dtype=np.uint8)
            alpha_map = shadow_mask * per_layer_opacity
            premul = np.stack([
                alpha_map * glaze_col[2],  # B premul
                alpha_map * glaze_col[1],  # G premul
                alpha_map * glaze_col[0],  # R premul
            ], axis=2)
            glaze_arr[:, :, :3] = np.clip(premul * 255, 0, 255).astype(np.uint8)
            glaze_arr[:, :, 3]  = np.clip(alpha_map * 255, 0, 255).astype(np.uint8)

            glaze_surf = cairo.ImageSurface.create_for_data(
                bytearray(glaze_arr.tobytes()), cairo.FORMAT_ARGB32, w, h)
            ctx.set_source_surface(glaze_surf, 0, 0)
            ctx.paint()

        # ── Stage 2: Gestural mid-tone enrichment strokes ─────────────────────
        # Short, directional strokes in the Venetian vermilion-gold register are
        # pushed across mid-tone areas.  This represents Titian's wet-into-wet
        # working where colours are physically merged on the surface.
        venetian_palette = [
            (0.84, 0.28, 0.18),   # vermilion
            (0.76, 0.52, 0.18),   # Naples yellow-gold
            (0.90, 0.80, 0.60),   # warm ivory
            (0.60, 0.18, 0.14),   # deep red lake
        ]
        n_midtone_strokes = 300
        rng = self._rng_py

        for _ in range(n_midtone_strokes):
            # Sample position from mid-tone region (lum 0.30–0.65)
            attempts = 0
            cx_s = rng.randint(0, w - 1)
            cy_s = rng.randint(0, h - 1)
            while attempts < 8:
                tx = rng.randint(0, w - 1)
                ty = rng.randint(0, h - 1)
                if 0.28 < lum[ty, tx] < 0.68:
                    cx_s, cy_s = tx, ty
                    break
                attempts += 1

            col = venetian_palette[rng.randint(0, len(venetian_palette) - 1)]
            # Sample underlying colour for wet_blend mix
            ref_col = tuple(float(rarr[cy_s, cx_s, c]) for c in range(3))
            blended = tuple(
                math.sqrt(0.35 * col[c] ** 2 + 0.65 * ref_col[c] ** 2)
                for c in range(3)
            )
            sz = max(3.0, impasto_size * rng.uniform(0.6, 1.1))
            angle = rng.uniform(0, math.pi)
            length = sz * rng.uniform(2.0, 4.5)
            pts = stroke_path((cx_s, cy_s), angle, length, 0.06, 8)
            widths = [sz * w_v for w_v in width_profile(len(pts), tip_frac=0.28)]

            self.canvas.apply_stroke(
                pts, widths, blended,
                tip=BrushTip(BrushTip.FILBERT),
                opacity=0.28,
                wet_blend=0.72,
                jitter_amt=0.022,
                rng=rng,
                region_mask=self._figure_mask,
            )

        # ── Stage 3: Loaded impasto highlights ────────────────────────────────
        # Titian's impasto is a physical presence — thick ridges of lead white
        # and pale yellow that catch directional light.  Applied only at
        # luminance peaks so they read as genuine specular highlights.
        highlight_lum_thresh = 0.68
        highlight_palette = [
            (0.96, 0.92, 0.78),   # near-white ivory — lead white
            (0.94, 0.87, 0.62),   # warm Naples yellow-white
            (0.98, 0.95, 0.84),   # cool pale highlight
        ]

        highlight_mask = np.clip((lum - highlight_lum_thresh) / (1.0 - highlight_lum_thresh),
                                 0.0, 1.0)
        if self._figure_mask is not None:
            highlight_mask = highlight_mask * self._figure_mask

        placed = 0
        attempts_total = 0
        while placed < impasto_strokes and attempts_total < impasto_strokes * 8:
            attempts_total += 1
            tx = rng.randint(0, w - 1)
            ty = rng.randint(0, h - 1)
            if highlight_mask[ty, tx] < rng.uniform(0.1, 0.9):
                continue

            col = highlight_palette[rng.randint(0, len(highlight_palette) - 1)]
            # Mix with reference colour — impasto sits on top but is not fully opaque
            ref_col = tuple(float(rarr[ty, tx, c]) for c in range(3))
            mixed = tuple(
                math.sqrt(impasto_opacity * col[c] ** 2 + (1 - impasto_opacity) * ref_col[c] ** 2)
                for c in range(3)
            )
            sz = max(2.5, impasto_size * rng.uniform(0.5, 1.4))
            # Impasto strokes are short and fat — directional brush loads
            angle = rng.uniform(0, math.pi)
            length = sz * rng.uniform(1.5, 3.0)
            pts = stroke_path((tx, ty), angle, length, 0.04, 6)
            widths = [sz * w_v for w_v in width_profile(len(pts), tip_frac=0.22)]

            self.canvas.apply_stroke(
                pts, widths, mixed,
                tip=BrushTip(BrushTip.FLAT),
                opacity=impasto_opacity * 0.95,
                wet_blend=0.28,    # low wet_blend — impasto stays crisp
                jitter_amt=0.012,
                rng=rng,
                region_mask=self._figure_mask,
            )
            placed += 1

        print(f"  Venetian glaze complete  ({n_glaze_layers} glazes, "
              f"{n_midtone_strokes} mid-tone strokes, {placed} impasto highlights)")

    def subsurface_glow_pass(self,
                             reference:     Union[np.ndarray, Image.Image],
                             glow_color:    Color = (0.90, 0.42, 0.24),
                             glow_strength: float = 0.18,
                             blur_sigma:    float = 10.0,
                             edge_falloff:  float = 0.55):
        """
        Subsurface scattering glow — simulates light transmission through thin skin.

        In real human skin, light does not simply bounce off the surface —
        it penetrates a millimetre or two, scatters through the translucent
        dermis, and exits at a slightly different point, tinted by the
        haemoglobin and melanin in the tissue.  The result is a warm reddish
        glow at the edges of the figure silhouette (where the skin is thin and
        the light path through tissue is short) and at anatomical thin-skin
        areas (ear lobes, nose tip, inner corners of the eye).

        Titian achieved this effect through red-lake glazes over white underpaint.
        The transparent red-lake layer selectively absorbs blue and green,
        transmitting warm red-orange light from the ground beneath.  The
        visual result is flesh that glows warm from within rather than reflecting
        cold light from the surface.

        Implementation
        --------------
        1. Detect edge/silhouette zone from the figure mask (or luminance
           gradient if no mask is available).  The glow is strongest where
           the figure boundary is thin and light can penetrate.
        2. Blur this zone outward (Gaussian) so the glow halos around the edge
           rather than sitting exactly on it.
        3. Tint the glow with a warm red-orange (haemoglobin scattering colour)
           and composite at low opacity over the existing painting.

        The pass should always be applied before final glazing so the glow
        is unified under the ambient glaze.

        Parameters
        ----------
        reference     : PIL Image or ndarray — used to detect edge zones.
        glow_color    : RGB tint of the scattered light.  (0.90, 0.42, 0.24)
                        is warm vermilion-orange — correct for pale skin.
                        Darker or more melanated skin should use a deeper,
                        more umber-red: e.g. (0.70, 0.28, 0.14).
        glow_strength : Maximum opacity of the glow composite.  0.10–0.25
                        is subtle and naturalistic; >0.35 looks artificial.
        blur_sigma    : Gaussian spread of the glow in pixels.  Larger values
                        create a broader, softer halo.  8–14px for a portrait
                        at 780×1080.
        edge_falloff  : How strongly to weight the glow toward true silhouette
                        edges vs. internal form-transition edges.  1.0 = figure
                        silhouette only; 0.0 = all luminance gradient edges.
                        0.5 gives a natural blend.
        """
        print(f"Subsurface glow pass  (glow={glow_color}  "
              f"strength={glow_strength:.2f}  sigma={blur_sigma:.1f})…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        lum = (0.299 * rarr[:, :, 0] + 0.587 * rarr[:, :, 1] + 0.114 * rarr[:, :, 2])

        # ── Build glow zone mask ──────────────────────────────────────────────
        # Primary source: figure silhouette edge (where mask transitions 0→1)
        if self._figure_mask is not None:
            # Detect silhouette edge via Sobel on the binary figure mask
            sil_gx = ndimage.sobel(self._figure_mask, axis=1).astype(np.float32)
            sil_gy = ndimage.sobel(self._figure_mask, axis=0).astype(np.float32)
            silhouette_edge = np.sqrt(sil_gx ** 2 + sil_gy ** 2)
            if silhouette_edge.max() > 1e-9:
                silhouette_edge /= silhouette_edge.max()
        else:
            silhouette_edge = np.zeros((h, w), dtype=np.float32)

        # Secondary source: luminance gradient (internal form transitions)
        lum_gx = ndimage.sobel(lum, axis=1).astype(np.float32)
        lum_gy = ndimage.sobel(lum, axis=0).astype(np.float32)
        lum_edge = np.sqrt(lum_gx ** 2 + lum_gy ** 2)
        if lum_edge.max() > 1e-9:
            lum_edge /= lum_edge.max()

        # Blend silhouette and luminance edges according to edge_falloff
        glow_zone = silhouette_edge * edge_falloff + lum_edge * (1.0 - edge_falloff)
        if glow_zone.max() > 1e-9:
            glow_zone /= glow_zone.max()

        # Blur outward so the glow halos around the edge
        glow_zone = ndimage.gaussian_filter(glow_zone.astype(np.float32), sigma=blur_sigma)
        glow_zone = np.clip(glow_zone * 3.5, 0.0, 1.0)

        # Restrict glow to figure interior and immediate edge only
        if self._figure_mask is not None:
            # Allow glow to extend slightly beyond figure boundary (halo effect)
            dilated_mask = ndimage.gaussian_filter(
                self._figure_mask.astype(np.float32), sigma=blur_sigma * 0.4)
            dilated_mask = np.clip(dilated_mask * 2.5, 0.0, 1.0)
            glow_zone = glow_zone * dilated_mask

        # ── Composite warm glow over current painting ─────────────────────────
        # ARGB32 premultiplied — Cairo compositing handles the alpha correctly
        ctx = self.canvas.ctx

        alpha_map = glow_zone * glow_strength
        alpha_3ch = alpha_map[:, :, np.newaxis]
        premul_rgb = np.array(glow_color)[np.newaxis, np.newaxis, :] * alpha_3ch

        glow_rgba = np.zeros((h, w, 4), dtype=np.uint8)
        glow_rgba[:, :, 0] = np.clip(premul_rgb[:, :, 2] * 255, 0, 255).astype(np.uint8)  # B premul
        glow_rgba[:, :, 1] = np.clip(premul_rgb[:, :, 1] * 255, 0, 255).astype(np.uint8)  # G premul
        glow_rgba[:, :, 2] = np.clip(premul_rgb[:, :, 0] * 255, 0, 255).astype(np.uint8)  # R premul
        glow_rgba[:, :, 3] = np.clip(alpha_map * 255, 0, 255).astype(np.uint8)             # A

        glow_surf = cairo.ImageSurface.create_for_data(
            bytearray(glow_rgba.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(glow_surf, 0, 0)
        ctx.paint()

        print(f"  Subsurface glow complete  "
              f"(peak alpha={glow_strength:.2f}  blur={blur_sigma:.1f}px)")

    # ─────────────────────────────────────────────────────────────────────────
    # Fauvist mosaic pass — Henri Matisse / Les Fauves (session 16)
    # ─────────────────────────────────────────────────────────────────────────

    def fauvist_mosaic_pass(self,
                            reference:         Union[np.ndarray, Image.Image],
                            n_zones:           int   = 8,
                            saturation_boost:  float = 1.70,
                            lum_flatten:       float = 0.55,
                            contour_thickness: float = 2.5,
                            contour_opacity:   float = 0.92,
                            n_zone_strokes:    int   = 0,
                            complement_shadow: bool  = True,
                            shadow_threshold:  float = 0.38):
        """
        Fauvist mosaic technique — inspired by Henri Matisse and Les Fauves.

        Fauvism (1905–1908) was the first European movement to declare that
        colour need not represent reality.  Matisse placed pure cadmium red
        where there was a green shadow, pure cerulean blue where there was a
        brown wall — not because he mis-observed, but because the emotional
        truth of the colour chord mattered more than accurate hue transcription.
        The result is a flat, tile-like mosaic of saturated zones, separated
        by coloured (not black) contour lines.

        This pass implements the three stages of Matisse's Fauvist technique:

          Stage 1 — Hue liberation:
            Quantize the reference image to N colour zones using PIL palette
            reduction.  For each zone, extract the dominant hue, then REPLACE
            it with the nearest hue from the Fauvist palette (pure primaries and
            secondaries at maximum saturation).  The palette is not neutral —
            every zone is forced toward full chromatic intensity.

          Stage 2 — Luminance suppression:
            Matisse flattened chiaroscuro: forms are indicated by hue contrast,
            not by light/shadow gradients.  The luminance channel is compressed
            toward mid-value by `lum_flatten` (0 = no suppression, 1 = all
            zones at uniform mid-grey value).  Shadow areas are particularly
            affected: instead of darkening toward brown/black, they receive
            the COMPLEMENTARY colour (orange for blue zones, green for red
            zones), making the shadow zone as vivid as the lit zone.

          Stage 3 — Coloured contour lines:
            Sobel-detect zone boundaries, then draw contour strokes in a
            saturated colour (not black) — Matisse used vermilion, deep green,
            and ultramarine as his contour colours.  The coloured outline is
            what gives Fauvist works their stained-glass quality.

        Parameters
        ----------
        reference         : PIL Image or ndarray reference for colour sampling.
        n_zones           : Number of flat colour zones (6–12 typical).
        saturation_boost  : HSV saturation multiplier applied to every zone
                           colour before painting.  1.60–1.90 gives vivid Fauvist
                           saturation; values above 2.0 clip excessively.
        lum_flatten       : Fraction by which luminance variation is suppressed
                           toward mid-value (0.50).  0 = no flattening (natural
                           contrast retained); 0.55 = moderate Fauvist flatness;
                           1.0 = all zones at exactly v=0.50.
        contour_thickness : Width of coloured contour strokes in pixels.
        contour_opacity   : Opacity of contour strokes (0–1).
        n_zone_strokes    : Loaded-brush strokes to apply per zone for texture.
                           0 = auto-compute from canvas area.
        complement_shadow : If True, shadow zones receive their complementary
                           hue rather than a darkened version of the local hue.
                           This is the defining Fauvist technique.
        shadow_threshold  : Reference luminance below which a pixel is
                           classified as a shadow zone (0–1).
        """
        print(f"Fauvist mosaic pass  (zones={n_zones}  sat_boost={saturation_boost:.2f}"
              f"  lum_flatten={lum_flatten:.2f})…")

        ref  = self._prep(reference)
        rarr = ref[:, :, :3].astype(np.float32) / 255.0
        h, w = ref.shape[:2]

        # ── Stage 1: Hue quantization and liberation ──────────────────────────
        # Convert reference to PIL and quantize to N zones using median-cut.
        ref_pil   = Image.fromarray(ref[:, :, :3])
        quantized = ref_pil.quantize(colors=n_zones, method=Image.Quantize.MEDIANCUT)
        zone_idx  = np.array(quantized, dtype=np.int32)   # (H, W) zone indices

        # Matisse Fauvist palette — pure, maximum-saturation hues.
        # These are the raw pigments he squeezed directly from tube onto canvas.
        fauvist_hues = [
            0.00,   # cadmium red
            0.08,   # cadmium orange
            0.15,   # cadmium yellow
            0.38,   # viridian green
            0.57,   # cerulean / cobalt blue
            0.75,   # ultramarine blue-violet
            0.85,   # violet-rose / magenta
            0.92,   # rose madder
        ]

        # For each zone, determine representative hue from reference,
        # then assign the nearest Fauvist hue at maximum saturation.
        n_z = n_zones
        zone_colors = {}
        for z in range(n_z):
            mask = zone_idx == z
            if mask.sum() < 1:
                zone_colors[z] = (0.60, 0.20, 0.15)  # fallback red
                continue
            # Mean reference colour for this zone
            mean_rgb = rarr[mask].mean(axis=0)
            mean_h, mean_s, mean_v = colorsys.rgb_to_hsv(*mean_rgb)

            # Apply luminance suppression toward 0.50
            suppressed_v = mean_v + (0.50 - mean_v) * lum_flatten

            # Complement shadow: if this zone is in shadow, rotate hue by 180°
            is_shadow_zone = mean_v < shadow_threshold
            if complement_shadow and is_shadow_zone:
                target_hue = (mean_h + 0.5) % 1.0
            else:
                # Snap to nearest Fauvist hue
                dists = [min(abs(mean_h - fh), 1.0 - abs(mean_h - fh))
                         for fh in fauvist_hues]
                target_hue = fauvist_hues[int(np.argmin(dists))]

            # Apply saturation boost (cap at 1.0)
            target_sat = min(1.0, max(0.35, mean_s) * saturation_boost)
            zone_colors[z] = colorsys.hsv_to_rgb(target_hue, target_sat,
                                                  suppressed_v)

        # ── Stage 2: Flat zone fill via loaded-brush strokes ──────────────────
        # Matisse covered each zone in confident flat loaded-brush patches.
        # Stroke count auto-scales with canvas size if n_zone_strokes == 0.
        total_strokes = n_zone_strokes if n_zone_strokes > 0 else max(
            1200, int(w * h / 480))
        strokes_per_zone = max(80, total_strokes // max(1, n_z))

        print(f"  Zone fill  ({n_z} zones  ~{strokes_per_zone} strokes each)…")

        tip_flat  = BrushTip(BrushTip.FLAT, bristle_noise=0.05)
        base_size = max(6, int(min(w, h) / 65))   # ~1.5% of smaller dimension

        for z in range(n_z):
            mask = (zone_idx == z).astype(np.float32)
            if mask.sum() < 4:
                continue

            # Combine zone mask with figure mask for figure zones
            region = mask
            if self._figure_mask is not None:
                region = region  # allow both figure and background zones

            # Error map: paint where reference zone colour differs most from canvas
            cbuf = np.frombuffer(self.canvas.surface.get_data(),
                                 dtype=np.uint8).reshape(h, w, 4).copy()
            carr = cbuf[:, :, [2, 1, 0]].astype(np.float32) / 255.0
            zt   = np.array(zone_colors[z], dtype=np.float32)
            err  = np.mean(np.abs(carr - zt[np.newaxis, np.newaxis, :]), axis=2)
            prob = (err * mask)
            total_p = prob.sum()
            if total_p < 1e-9:
                continue
            prob = prob / total_p

            positions = self.rng.choice(
                h * w, size=strokes_per_zone, p=prob.flatten(), replace=True)

            zc = zone_colors[z]
            for pos in positions:
                py, px = int(pos // w), int(pos % w)
                margin = max(base_size + 2, 4)
                px = int(np.clip(px, margin, w - margin))
                py = int(np.clip(py, margin, h - margin))

                # Short confident flat strokes — Matisse's direct loaded-brush mark
                stroke_size = float(base_size) * self._rng_py.uniform(0.7, 1.8)
                angle = self._rng_py.uniform(0, math.pi)
                L     = stroke_size * self._rng_py.uniform(1.2, 3.0)
                pts   = stroke_path((float(px), float(py)), angle, L,
                                    curve=0.0, n=max(2, int(L / 4)))
                ws    = [stroke_size] * len(pts)
                self.canvas.apply_stroke(
                    pts, ws, zc, tip_flat,
                    opacity=0.88, wet_blend=0.04,
                    jitter_amt=0.018, rng=self._rng_py,
                    region_mask=region,
                )

        # ── Stage 3: Coloured contour lines ───────────────────────────────────
        # Detect zone boundaries via Sobel on the quantized zone index map.
        # Draw coloured (not black) contour strokes — the stained-glass signature.
        print(f"  Coloured contour lines  (thickness={contour_thickness:.1f}px)…")

        # Boundary map from zone index discontinuities
        zf   = zone_idx.astype(np.float32)
        bx   = ndimage.sobel(zf, axis=1).astype(np.float32)
        by   = ndimage.sobel(zf, axis=0).astype(np.float32)
        bmag = np.sqrt(bx ** 2 + by ** 2)
        if bmag.max() > 1e-9:
            bmag /= bmag.max()

        # Contour angle map (perpendicular to gradient = along the boundary)
        bangles = np.arctan2(by, bx) + math.pi / 2.0

        # Contour colour: rich ultramarine blue-green — Matisse's preferred outline
        contour_color = (0.06, 0.28, 0.55)   # deep ultramarine

        # Place contour strokes along high-magnitude boundary pixels
        boundary_prob = (bmag ** 1.5).flatten()
        bp_total = boundary_prob.sum()
        if bp_total > 1e-9:
            boundary_prob /= bp_total
            n_contour = max(500, int(w * h / 700))
            positions = self.rng.choice(h * w, size=n_contour,
                                        p=boundary_prob, replace=True)
            tip_c = BrushTip(BrushTip.FLAT, bristle_noise=0.0)
            margin = max(3, int(contour_thickness * 2))

            for pos in positions:
                py, px = int(pos // w), int(pos % w)
                px = max(margin, min(w - margin, px))
                py = max(margin, min(h - margin, py))
                a  = float(bangles[py, px])
                L  = self._rng_py.uniform(6.0, 18.0)
                start = (px - math.cos(a) * L * 0.5,
                         py - math.sin(a) * L * 0.5)
                n_pts = max(3, int(L / 4))
                pts   = stroke_path(start, a, L, curve=0.0, n=n_pts)
                ws    = [contour_thickness] * len(pts)
                self.canvas.apply_stroke(
                    pts, ws, contour_color, tip_c,
                    opacity=contour_opacity, wet_blend=0.0,
                    jitter_amt=0.006, rng=self._rng_py,
                )

        print(f"  Fauvist mosaic complete")

    # ─────────────────────────────────────────────────────────────────────────
    # Chroma zone pass — tonal chroma management (session 16 random improvement)
    # ─────────────────────────────────────────────────────────────────────────

    def chroma_zone_pass(self,
                         light_suppress:  float = 0.55,
                         shadow_suppress: float = 0.40,
                         midtone_boost:   float = 1.20,
                         light_thresh:    float = 0.72,
                         shadow_thresh:   float = 0.30):
        """
        Tonal chroma management — inspired by Vermeer's luminance-saturation control.

        The Old Masters — Vermeer especially — understood that chromatic intensity
        (saturation) should vary across the luminance range in a specific, non-obvious
        way:

          • Highest lights → warm white, nearly neutral (low saturation).  Pure
            white light bleaches colour; the highest highlight on a red dress is
            almost white, not red.

          • Deep shadows → cool neutral (low saturation).  Pigment in the deepest
            shadows is absorbed by darkness; a saturated blue-black is less
            convincing than a near-neutral dark grey with a faint cool cast.

          • Mid-tones → maximum saturation.  This is where colour lives.  The
            'local colour' of a surface — its true red, blue, or green — is most
            legible in the mid-tone zone, where it is neither bleached by light
            nor absorbed by shadow.

        This pass reads the current canvas buffer, performs per-pixel HSV analysis,
        and applies three targeted adjustments:

          1. **Light zone suppression**: pixels above `light_thresh` luminance have
             their saturation multiplied by `light_suppress` (< 1.0), driving
             highlights toward warm white.

          2. **Shadow zone suppression**: pixels below `shadow_thresh` luminance have
             their saturation multiplied by `shadow_suppress` (< 1.0), driving
             deep shadows toward cool neutral.

          3. **Mid-tone boost**: pixels between the two thresholds have their
             saturation multiplied by `midtone_boost` (> 1.0), enriching the
             zone where colour is most expressive.

        All changes are vectorised via numpy and written back in a single Cairo
        surface operation — no stroke-by-stroke overhead.

        This pass should be called AFTER the main painting passes and BEFORE the
        final glaze and finish(), so that colour temperature of the glaze is applied
        on top of correctly managed saturation zones.

        Parameters
        ----------
        light_suppress  : Saturation multiplier for highlight pixels (< 1.0).
                         0.40–0.65 gives the warm-neutral highlight typical of
                         Vermeer and Dutch masters.
        shadow_suppress : Saturation multiplier for shadow pixels (< 1.0).
                         0.30–0.55 gives cool near-neutral darks.
        midtone_boost   : Saturation multiplier for mid-tone pixels (> 1.0).
                         1.15–1.35 enriches the local-colour zone without clipping.
        light_thresh    : Luminance threshold above which pixels are 'highlight'
                         zone (0–1).  0.68–0.75 is appropriate for oil painting.
        shadow_thresh   : Luminance threshold below which pixels are 'shadow'
                         zone (0–1).  0.25–0.35 is appropriate for oil painting.
        """
        print(f"Chroma zone pass  (light_suppress={light_suppress:.2f}"
              f"  shadow_suppress={shadow_suppress:.2f}"
              f"  midtone_boost={midtone_boost:.2f})…")

        h, w = self.h, self.w
        ctx  = self.canvas.ctx

        # Read current canvas (Cairo BGRA layout)
        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(h, w, 4).copy()
        # Extract RGB float in [0, 1]
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0

        # Vectorised RGB → HSV
        # Luminance (value in HSV = max of RGB channels)
        v_ch = np.maximum(np.maximum(r_ch, g_ch), b_ch)
        mn   = np.minimum(np.minimum(r_ch, g_ch), b_ch)
        span = v_ch - mn

        # Saturation = span / v  (0 where v is 0)
        with np.errstate(divide='ignore', invalid='ignore'):
            s_ch = np.where(v_ch > 1e-9, span / v_ch, 0.0)

        # Hue (0–1 range)
        with np.errstate(divide='ignore', invalid='ignore'):
            h_ch = np.zeros_like(v_ch)
            # Red is max
            m = (v_ch == r_ch) & (span > 1e-9)
            h_ch[m] = ((g_ch[m] - b_ch[m]) / span[m]) % 6.0
            # Green is max
            m = (v_ch == g_ch) & (span > 1e-9)
            h_ch[m] = (b_ch[m] - r_ch[m]) / span[m] + 2.0
            # Blue is max
            m = (v_ch == b_ch) & (span > 1e-9)
            h_ch[m] = (r_ch[m] - g_ch[m]) / span[m] + 4.0
        h_ch = (h_ch / 6.0) % 1.0   # normalise to [0, 1]

        # ── Apply tonal chroma adjustments ───────────────────────────────────
        lum = v_ch  # use V channel as luminance proxy

        # Light zone: bleach toward neutral warm white
        light_mask   = lum >= light_thresh
        s_ch[light_mask] = np.clip(s_ch[light_mask] * light_suppress, 0.0, 1.0)

        # Shadow zone: cool near-neutral darks
        shadow_mask  = lum <= shadow_thresh
        s_ch[shadow_mask] = np.clip(s_ch[shadow_mask] * shadow_suppress, 0.0, 1.0)

        # Mid-tone zone: enrich local colour
        mid_mask = (~light_mask) & (~shadow_mask)
        s_ch[mid_mask] = np.clip(s_ch[mid_mask] * midtone_boost, 0.0, 1.0)

        # ── Vectorised HSV → RGB ─────────────────────────────────────────────
        # Uses the standard HSV→RGB sector formula, fully vectorised.
        h6   = h_ch * 6.0
        i    = np.floor(h6).astype(np.int32) % 6
        f    = h6 - np.floor(h6)
        p    = v_ch * (1.0 - s_ch)
        q    = v_ch * (1.0 - f * s_ch)
        t    = v_ch * (1.0 - (1.0 - f) * s_ch)

        r_out = np.select(
            [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
            [v_ch,   q,      p,      p,      t,      v_ch],  0.0)
        g_out = np.select(
            [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
            [t,      v_ch,   v_ch,   q,      p,      p],     0.0)
        b_out = np.select(
            [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
            [p,      p,      t,      v_ch,   v_ch,   q],     0.0)

        # Clamp and write back to Cairo BGRA buffer
        buf[:, :, 2] = np.clip(r_out * 255, 0, 255).astype(np.uint8)  # R → BGRA[2]
        buf[:, :, 1] = np.clip(g_out * 255, 0, 255).astype(np.uint8)  # G → BGRA[1]
        buf[:, :, 0] = np.clip(b_out * 255, 0, 255).astype(np.uint8)  # B → BGRA[0]
        buf[:, :, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(tmp, 0, 0)
        ctx.paint()

        print(f"  Chroma zone pass complete  "
              f"(light zone: {light_mask.sum()} px  "
              f"shadow zone: {shadow_mask.sum()} px  "
              f"mid-tone: {mid_mask.sum()} px)")

    # ─────────────────────────────────────────────────────────────────────────
    # Oval mask pass — Amedeo Modigliani / Primitivist portrait (session 17)
    # ─────────────────────────────────────────────────────────────────────────

    def oval_mask_pass(self,
                       reference:        Union[np.ndarray, Image.Image],
                       flesh_color:      Color = (0.84, 0.62, 0.38),
                       shadow_color:     Color = (0.68, 0.44, 0.24),
                       outline_color:    Color = (0.10, 0.07, 0.06),
                       outline_thickness: float = 2.5,
                       outline_opacity:  float = 0.88,
                       neck_elongation:  float = 0.18,
                       flesh_flatten:    float = 0.55,
                       flesh_tint:       float = 0.30):
        """
        Primitivist mask pass — inspired by Amedeo Modigliani.

        Modigliani's faces are derived from two primary sources: African ritual
        masks (long oval form, almond eye cavities) and Cycladic marble idols
        (featureless, archaic simplification).  His portrait technique reduces
        the human face to its essential geometry:

          1. An oval — smooth, unbroken, elongated about 30% beyond anatomical
             proportion.  One continuous contour line defines the whole face.

          2. Flat warm-ochre flesh fill — minimal modelling.  The only shadow
             colour is raw sienna or blue-grey, placed only beneath the chin
             and at the eye sockets.  No chiaroscuro: form is stated by the
             contour alone.

          3. Almond eyes — solid ellipses of cobalt blue or grey-mauve.  No
             pupils in the early work; tiny iris slits in the later portraits.
             The eye is a shape, not a window.

          4. Elongated neck — longer than the face itself, a single unbroken
             column.  This is the most visually distinctive Modigliani marker.

        Implementation
        --------------
        1. Detect face region from figure mask (upper figure region) or
           luminance analysis if no mask is available.

        2. Within the face ellipse: compress luminance variation toward a
           neutral mid-value (``flesh_flatten`` controls strength).  This
           simulates the near-total suppression of chiaroscuro Modigliani used.

        3. Tint the flattened face zone toward warm ochre (``flesh_tint``
           controls strength — 0 = unchanged, 1 = fully ochre).

        4. Draw a smooth oval contour around the detected face region using
           Cairo arc operations.  The oval is slightly taller than the detected
           face (elongation factor), giving the mask-like silhouette.

        5. Elongate the neck: extend the face contour downward by
           ``neck_elongation`` as a fraction of the face height.

        Parameters
        ----------
        reference         : PIL Image or ndarray — used for luminance analysis.
        flesh_color       : RGB of the warm ochre flesh fill target.
        shadow_color      : RGB of the raw sienna shadow placed at chin/eyes.
        outline_color     : RGB of the near-black oval contour line.
        outline_thickness : Width of the contour line in pixels.
        outline_opacity   : Alpha of the contour composite.
        neck_elongation   : Neck extension as fraction of face height (0.18 =
                            18%).  Modigliani's necks are about 0.3–0.45 of the
                            face height but 0.18–0.25 is enough in the pipeline.
        flesh_flatten     : Strength of luminance compression in the face zone
                            (0 = no change, 1 = fully flat mid-value).
        flesh_tint        : Strength of ochre tint overlay (0 = no tint,
                            1 = full replacement with flesh_color).

        Notes
        -----
        Famous works to study:
          *Jeanne Hébuterne with a Hat* (1918) — definitive oval, tilted neck.
          *Nu couché* (1917) — the mask face on a reclining nude.
          *Portrait of Lunia Czechowska* (1918) — severe elongation, cobalt eyes.
        """
        print(f"Oval mask pass  (flatten={flesh_flatten:.2f}  tint={flesh_tint:.2f}  "
              f"neck={neck_elongation:.2f})…")

        ref  = self._prep(reference)
        h, w = ref.shape[:2]

        # ── Locate face ellipse centre from figure mask ───────────────────────
        # If a figure mask is available, the face is in the upper ~40% of the
        # figure bounding box.  Without a mask, fall back to the upper-centre
        # of the canvas where a portrait subject would typically sit.
        if self._figure_mask is not None:
            rows   = np.any(self._figure_mask > 0.5, axis=1)
            cols   = np.any(self._figure_mask > 0.5, axis=0)
            if rows.any() and cols.any():
                r0, r1 = int(np.argmax(rows)), int(h - 1 - np.argmax(rows[::-1]))
                c0, c1 = int(np.argmax(cols)), int(w - 1 - np.argmax(cols[::-1]))
                # Face is upper 40% of figure height
                face_top    = r0
                face_bottom = r0 + int((r1 - r0) * 0.42)
                face_cx     = (c0 + c1) // 2
                face_cy     = (face_top + face_bottom) // 2
                face_ry     = max(20, (face_bottom - face_top) // 2)
                face_rx     = max(14, int(face_ry * 0.62))   # oval is taller than wide
            else:
                face_cx, face_cy = w // 2, h // 3
                face_ry = h // 6
                face_rx = int(face_ry * 0.62)
        else:
            face_cx, face_cy = w // 2, h // 3
            face_ry = h // 6
            face_rx = int(face_ry * 0.62)

        # ── Stage 1: Flatten and tint face zone ──────────────────────────────
        # Read current canvas pixel values
        ctx  = self.canvas.ctx
        surf = self.canvas.surface
        buf  = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()

        # Build face ellipse mask (soft-edged)
        yy, xx = np.ogrid[:h, :w]
        dist_sq = ((xx - face_cx) / max(face_rx, 1)) ** 2 + \
                  ((yy - face_cy) / max(face_ry, 1)) ** 2
        # Feather: 1.0 at centre, 0.0 outside the ellipse, smooth transition
        face_zone = np.clip(1.5 - dist_sq, 0.0, 1.0).astype(np.float32)

        # Current canvas RGB (Cairo BGRA: [B, G, R, A])
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0

        lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch
        mid_lum = float(np.median(lum[face_zone > 0.5])) if (face_zone > 0.5).any() else 0.55

        # Compress luminance variation toward mid-value within face zone
        # New lum = lerp(lum, mid_lum, flesh_flatten * face_zone)
        blend_w = flesh_flatten * face_zone
        flat_r  = r_ch * (1.0 - blend_w) + mid_lum * blend_w
        flat_g  = g_ch * (1.0 - blend_w) + mid_lum * blend_w
        flat_b  = b_ch * (1.0 - blend_w) + mid_lum * blend_w

        # Tint face zone toward warm ochre flesh colour
        fr, fg, fb = flesh_color
        tint_w = flesh_tint * face_zone
        final_r = flat_r * (1.0 - tint_w) + fr * tint_w
        final_g = flat_g * (1.0 - tint_w) + fg * tint_w
        final_b = flat_b * (1.0 - tint_w) + fb * tint_w

        # Write back into buffer (BGRA order)
        buf[:, :, 2] = np.clip(final_r * 255, 0, 255).astype(np.uint8)  # R
        buf[:, :, 1] = np.clip(final_g * 255, 0, 255).astype(np.uint8)  # G
        buf[:, :, 0] = np.clip(final_b * 255, 0, 255).astype(np.uint8)  # B
        buf[:, :, 3] = 255

        tmp_surf = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(tmp_surf, 0, 0)
        ctx.paint()

        # ── Stage 2: Draw oval contour and neck line ──────────────────────────
        # Modigliani's contour is a single continuous near-black line around the
        # face oval.  The neck is two near-parallel lines extending downward from
        # the chin point, separated by roughly the chin width.
        neck_length = int(face_ry * neck_elongation * 2.0)
        or_, og, ob = outline_color

        ctx.save()
        ctx.set_source_rgba(or_, og, ob, outline_opacity)
        ctx.set_line_width(outline_thickness)

        # Face oval (slightly taller than detected: *1.05 elongation factor)
        oval_ry = face_ry * 1.05
        oval_rx = face_rx
        ctx.arc(face_cx, face_cy, 1.0, 0, 2 * math.pi)  # unit circle → scaled
        ctx.new_path()
        ctx.save()
        ctx.translate(face_cx, face_cy)
        ctx.scale(oval_rx, oval_ry)
        ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
        ctx.restore()
        ctx.stroke()

        # Neck column: two vertical lines from chin down by neck_length
        chin_y   = face_cy + int(oval_ry)
        neck_w   = max(4, int(face_rx * 0.38))   # neck width fraction of face

        ctx.move_to(face_cx - neck_w, chin_y)
        ctx.line_to(face_cx - neck_w, chin_y + neck_length)
        ctx.stroke()

        ctx.move_to(face_cx + neck_w, chin_y)
        ctx.line_to(face_cx + neck_w, chin_y + neck_length)
        ctx.stroke()

        ctx.restore()

        print(f"  Oval mask pass complete  "
              f"(face_cx={face_cx}, face_cy={face_cy}  "
              f"rx={face_rx}, ry={face_ry}  neck={neck_length}px)")

    # ─────────────────────────────────────────────────────────────────────────
    # Warm-cool boundary pass — session 17 random artistic improvement
    # ─────────────────────────────────────────────────────────────────────────

    def warm_cool_boundary_pass(self,
                                strength:    float = 0.14,
                                edge_thresh: float = 0.08,
                                blur_sigma:  float = 1.8,
                                warm_push:   Color = (0.12, 0.02, -0.06),
                                cool_push:   Color = (-0.06, 0.01, 0.10)):
        """
        Warm-cool boundary vibration — universally applicable tonal refinement.

        Painters from Delacroix through Cézanne, the Impressionists, and
        Modigliani discovered that boundaries between colour areas appear more
        perceptually vivid when warm and cool tones are juxtaposed across the
        edge.  This is simultaneous contrast (Chevreul, 1839): each colour
        intensifies the apparent contrast of its neighbour across an edge by
        shifting the viewer's perception slightly toward the complementary.

        In practice this means:
          - The warm side of a boundary (more red/yellow) gets a micro-push
            toward warm (boost R slightly, damp B).
          - The cool side (more blue/green) gets a micro-push toward cool
            (boost B slightly, damp R).

        The visual result is that boundaries feel "inhabited" — alive and
        subtly vibrating — rather than static.  This is particularly important
        in portrait painting where the face-to-background edge is the central
        perceptual event.

        Unlike folk_retablo_pass() boundary_vibration (which uses explicit
        warm/cool strokes at zone edges), this pass operates directly on the
        canvas pixel buffer using vectorised numpy operations — fast, globally
        applied, and style-agnostic.  It is useful after any style pass that
        tends to produce flat or dead-looking boundaries.

        Implementation
        --------------
        1. Read the current canvas buffer as float32 RGB.
        2. Compute a Sobel edge-magnitude map.
        3. Threshold: pixels above ``edge_thresh`` are boundary pixels.
        4. For each boundary pixel, classify as "warm side" or "cool side"
           by comparing local R+G (warm channels) vs B+G (cool channels).
           A simple warm/cool score = (R - B) in the blurred reference.
        5. Apply ``warm_push`` delta to warm-side boundary pixels and
           ``cool_push`` delta to cool-side boundary pixels, weighted by
           edge magnitude and ``strength``.
        6. Composite back to the Cairo surface.

        Parameters
        ----------
        strength    : Overall intensity of the temperature push.  0.10–0.18
                      is subtle and naturalistic; >0.25 reads as artificial.
        edge_thresh : Minimum normalised edge magnitude to receive the push.
                      0.06–0.12 is a good range.
        blur_sigma  : Gaussian blur applied to the edge map before thresholding,
                      so isolated noise pixels don't fire.  1.5–2.5 is good.
        warm_push   : RGB delta applied to the warm side of each boundary.
                      Positive R, small positive G, negative B = red-orange push.
        cool_push   : RGB delta applied to the cool side.
                      Negative R, small positive G, positive B = blue-violet push.

        Notes
        -----
        This pass should be called AFTER the main style passes and BEFORE the
        final glaze/vignette.  It is particularly effective after:
          - oval_mask_pass() — to make the face-background boundary vibrate
          - fauvist_mosaic_pass() — to micro-push zone boundaries even further
          - flat_plane_pass() — to animate Manet's flat value-plane edges
        """
        print(f"Warm-cool boundary pass  (strength={strength:.2f}  "
              f"thresh={edge_thresh:.2f}  sigma={blur_sigma:.1f})…")

        surf = self.canvas.surface
        h, w = surf.get_height(), surf.get_width()

        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()

        # Current canvas RGB (Cairo BGRA: [B, G, R, A])
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0

        # ── Edge detection ───────────────────────────────────────────────────
        lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch
        gx  = ndimage.sobel(lum, axis=1).astype(np.float32)
        gy  = ndimage.sobel(lum, axis=0).astype(np.float32)
        edge_mag = np.sqrt(gx ** 2 + gy ** 2)
        if edge_mag.max() > 1e-9:
            edge_mag /= edge_mag.max()

        # Smooth to reduce noise
        edge_mag = ndimage.gaussian_filter(edge_mag, sigma=blur_sigma)
        if edge_mag.max() > 1e-9:
            edge_mag /= edge_mag.max()

        # ── Warm / cool classification ───────────────────────────────────────
        # warm_score > 0 → warm side (reddish), < 0 → cool side (bluish)
        warm_score = r_ch - b_ch

        # Apply a slight blur so that classification reflects local neighbourhood,
        # not just the single edge pixel (which may be a neutral transition colour).
        warm_score = ndimage.gaussian_filter(warm_score, sigma=blur_sigma * 1.5)

        warm_side = warm_score > 0.0
        cool_side = ~warm_side

        # ── Build delta maps ─────────────────────────────────────────────────
        # Weight by edge magnitude * strength so only true boundaries are affected.
        edge_weight = np.clip(edge_mag, 0.0, 1.0) * strength

        # Only apply where edge is above threshold
        active = edge_mag > edge_thresh

        dr = np.zeros((h, w), dtype=np.float32)
        dg = np.zeros((h, w), dtype=np.float32)
        db = np.zeros((h, w), dtype=np.float32)

        # Warm-side pixels get the warm push
        wp = active & warm_side
        dr[wp] += warm_push[0] * edge_weight[wp]
        dg[wp] += warm_push[1] * edge_weight[wp]
        db[wp] += warm_push[2] * edge_weight[wp]

        # Cool-side pixels get the cool push
        cp = active & cool_side
        dr[cp] += cool_push[0] * edge_weight[cp]
        dg[cp] += cool_push[1] * edge_weight[cp]
        db[cp] += cool_push[2] * edge_weight[cp]

        # ── Apply deltas to canvas buffer ────────────────────────────────────
        buf[:, :, 2] = np.clip((r_ch + dr) * 255, 0, 255).astype(np.uint8)  # R
        buf[:, :, 1] = np.clip((g_ch + dg) * 255, 0, 255).astype(np.uint8)  # G
        buf[:, :, 0] = np.clip((b_ch + db) * 255, 0, 255).astype(np.uint8)  # B
        buf[:, :, 3] = 255

        ctx = self.canvas.ctx
        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(tmp, 0, 0)
        ctx.paint()

        n_active = int(active.sum())
        n_warm   = int((active & warm_side).sum())
        n_cool   = int((active & cool_side).sum())
        print(f"  Warm-cool boundary pass complete  "
              f"(active={n_active}px  warm={n_warm}  cool={n_cool})")

    def glazed_panel_pass(self,
                          reference:       Union[np.ndarray, Image.Image],
                          n_glaze_layers:  int   = 8,
                          glaze_opacity:   float = 0.07,
                          shadow_warmth:   float = 0.28,
                          highlight_cool:  float = 0.12,
                          shadow_thresh:   float = 0.38,
                          highlight_thresh: float = 0.72,
                          panel_bloom:     float = 0.08):
        """
        Flemish panel painting glaze technique — inspired by Jan van Eyck.

        Van Eyck's revolutionary contribution was the systematic use of
        transparent oil glazes stacked over a chalk-white gesso panel ground.
        Unlike tempera (which is opaque and cannot be glazed), oil paint can be
        diluted to near-transparency.  Each glaze layer adds colour depth while
        allowing light to penetrate to the brilliant white ground below and
        reflect back upward through all layers — creating a luminosity that no
        opaque paint technique can replicate.

        The key physics: light entering a glazed oil painting travels through
        N transparent films of varying colour, strikes the white ground, and
        returns through the same films.  Shadow areas accumulate more amber-
        umber glaze (warm deep shadows); highlights retain the cool brilliance
        of the nearly-bare white ground.  This warm-shadow / cool-highlight
        reversal is the defining quality of Flemish panel luminosity and the
        opposite of the warm-light / cool-shadow convention used in outdoor
        Impressionism.

        Implementation
        --------------
        1. Read current canvas buffer as float32 RGB.
        2. Build a per-pixel luminance map from the reference.
        3. Shadow zones (lum < shadow_thresh): accumulate thin warm amber-umber
           glaze layers — each layer is composited at very low opacity so the
           effect builds gradually without over-darkening.
        4. Highlight zones (lum > highlight_thresh): apply a faint cool-neutral
           tint toward the chalk-white panel ground — the highlights are not
           pushed warm; they stay cool and bright.
        5. Mid-tone zones receive balanced warm/cool glazes for tonal unity.
        6. Panel bloom: a very slight radial luminance boost centred on the
           brightest highlight zone, simulating how light diffuses slightly in
           the topmost oil glaze film.

        Parameters
        ----------
        reference        : PIL Image or numpy array — original scene reference
                           used to compute the luminance guidance map.
        n_glaze_layers   : Number of simulated transparent glaze layers to
                           accumulate.  8–12 is realistic for a Flemish portrait.
        glaze_opacity    : Per-layer opacity.  0.05–0.10 keeps each layer
                           physically thin.  n_layers × opacity = total shadow depth.
        shadow_warmth    : Warmth of the shadow glaze (R-channel boost, B-damp).
                           0.20–0.35 gives the characteristic warm Flemish shadow.
        highlight_cool   : Cool pull applied to highlights.  0.08–0.15 gives
                           the chalk-grey Flemish highlight quality.
        shadow_thresh    : Luminance below which shadow glaze is applied (0–1).
        highlight_thresh : Luminance above which highlight cool is applied (0–1).
        panel_bloom      : Opacity of the panel bloom diffusion (0.05–0.12).

        Notes
        -----
        This pass must be called AFTER the main form-building passes and BEFORE
        the final glaze / vignette calls.  It is designed for EARLY_NETHERLANDISH
        period but the luminosity effect is beneficial for any period using a
        light ground (BAROQUE, RENAISSANCE).
        """
        print(f"Glazed panel pass  (n_layers={n_glaze_layers}  "
              f"opacity={glaze_opacity:.3f}  shadow_warmth={shadow_warmth:.2f})…")

        surf = self.canvas.surface
        h, w = surf.get_height(), surf.get_width()

        # ── Build luminance guidance map from reference ───────────────────────
        ref_arr = self._prep(reference)   # (H, W, 3) uint8
        ref_f   = ref_arr.astype(np.float32) / 255.0
        lum_ref = (0.299 * ref_f[:, :, 0]
                   + 0.587 * ref_f[:, :, 1]
                   + 0.114 * ref_f[:, :, 2])   # (H, W) in [0, 1]

        # Resize lum_ref to canvas size if needed
        if lum_ref.shape != (h, w):
            from PIL import Image as _PILImg
            lum_pil = _PILImg.fromarray((lum_ref * 255).astype(np.uint8), "L")
            lum_pil = lum_pil.resize((w, h), _PILImg.BILINEAR)
            lum_ref = np.array(lum_pil).astype(np.float32) / 255.0

        # ── Read canvas buffer ────────────────────────────────────────────────
        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0

        # ── Shadow zone glaze accumulation ────────────────────────────────────
        # Warm amber-umber glaze: boost R slightly, slightly reduce B.
        # Multiple thin layers simulate the stacked transparent film effect.
        shadow_mask = np.clip((shadow_thresh - lum_ref) / shadow_thresh, 0.0, 1.0)
        # Slightly blur the mask for smooth zone transitions
        shadow_mask = ndimage.gaussian_filter(shadow_mask.astype(np.float32), sigma=2.0)

        glaze_r_boost =  shadow_warmth * 0.55
        glaze_b_damp  = -shadow_warmth * 0.35
        glaze_g_boost =  shadow_warmth * 0.08

        for _ in range(n_glaze_layers):
            alpha = glaze_opacity * shadow_mask
            r_ch = np.clip(r_ch + alpha * glaze_r_boost, 0.0, 1.0)
            g_ch = np.clip(g_ch + alpha * glaze_g_boost, 0.0, 1.0)
            b_ch = np.clip(b_ch + alpha * glaze_b_damp,  0.0, 1.0)

        # ── Highlight zone cool pull ──────────────────────────────────────────
        # Chalk-white gesso reflects slightly cool — the highest lights retain
        # a slight blue-grey neutral quality (not the warm highlights of Italian oil).
        highlight_mask = np.clip((lum_ref - highlight_thresh) / (1.0 - highlight_thresh),
                                 0.0, 1.0)
        highlight_mask = ndimage.gaussian_filter(highlight_mask.astype(np.float32), sigma=1.5)

        cool_r_damp  = -highlight_cool * 0.30
        cool_b_boost =  highlight_cool * 0.25
        cool_g_boost =  highlight_cool * 0.05

        r_ch = np.clip(r_ch + highlight_mask * cool_r_damp,  0.0, 1.0)
        g_ch = np.clip(g_ch + highlight_mask * cool_g_boost, 0.0, 1.0)
        b_ch = np.clip(b_ch + highlight_mask * cool_b_boost, 0.0, 1.0)

        # ── Panel bloom — diffuse luminance spread at brightest highlight ─────
        # The outermost oil glaze film creates a slight scattering halo around
        # specular highlights, visible in close inspection of van Eyck's panels
        # (e.g. the pearls in the Arnolfini Portrait).
        if panel_bloom > 0.001:
            bright_zone = np.clip((lum_ref - 0.85) / 0.15, 0.0, 1.0).astype(np.float32)
            bloom = ndimage.gaussian_filter(bright_zone, sigma=4.0)
            if bloom.max() > 1e-9:
                bloom = bloom / bloom.max() * panel_bloom
            r_ch = np.clip(r_ch + bloom, 0.0, 1.0)
            g_ch = np.clip(g_ch + bloom * 0.92, 0.0, 1.0)
            b_ch = np.clip(b_ch + bloom * 0.82, 0.0, 1.0)

        # ── Write back to canvas ──────────────────────────────────────────────
        buf[:, :, 2] = np.clip(r_ch * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(g_ch * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip(b_ch * 255, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255

        ctx = self.canvas.ctx
        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(tmp, 0, 0)
        ctx.paint()

        shadow_px    = int((shadow_mask > 0.1).sum())
        highlight_px = int((highlight_mask > 0.1).sum())
        print(f"  Glazed panel pass complete  "
              f"(shadow_px={shadow_px}  highlight_px={highlight_px}  "
              f"layers={n_glaze_layers})")

    def micro_detail_pass(self,
                          strength:       float = 0.22,
                          fine_sigma:     float = 0.8,
                          coarse_sigma:   float = 3.5,
                          edge_thresh:    float = 0.06,
                          light_boost:    float = 0.18,
                          shadow_deepen:  float = 0.14,
                          figure_only:    bool  = True):
        """
        Flemish micro-detail enhancement — inspired by Jan van Eyck's
        hyper-precise rendering of individual hairs, fabric threads, and
        gemstone reflections.

        Van Eyck painted at a level of detail that remained unmatched until
        photography: individual hairs are painted one by one, fabric weave
        threads are rendered at near-microscopic scale, reflections in pearls
        and polished metal show tiny accurate mirror images of the room.
        This was possible partly because of the slow-drying oil medium
        (allowing fine rework) and partly because of his extraordinary
        patience and technique.

        The micro-detail pass enhances fine-scale edge contrast across the
        entire canvas — brightening the light side of every fine edge and
        deepening the shadow side.  This is equivalent to an unsharp-mask
        but physically motivated: it simulates the way a thin specular
        oil film produces micro-highlights along texture ridges.

        Implementation
        --------------
        1. Read the current canvas RGB buffer.
        2. Compute a fine-scale luminance gradient (tight Sobel with small sigma).
        3. Subtract a coarse-scale gradient to isolate only the finest edges
           (high-pass filtering in the spatial frequency domain).
        4. For each fine edge pixel:
             - The light side (gradient pointing toward bright area) receives
               a small brightness boost (``light_boost``).
             - The shadow side receives a small darkening (``shadow_deepen``).
        5. Apply ``strength`` weighting and ``edge_thresh`` threshold so that
           only genuine fine edges are processed, not noise or flat areas.
        6. If ``figure_only`` and a figure mask exists, restrict the pass to
           the figure region (fabric, skin, hair).

        Parameters
        ----------
        strength      : Overall intensity multiplier.  0.15–0.25 is subtle
                        and naturalistic; >0.35 looks sharpened.
        fine_sigma    : Gaussian blur sigma for the fine edge detection.
                        0.5–1.0 captures hair-scale detail.
        coarse_sigma  : Gaussian blur sigma for the coarse subtracted layer.
                        3.0–5.0 removes broad gradients, isolating micro-detail.
        edge_thresh   : Minimum edge magnitude (fine-scale, normalised) to
                        receive the micro-detail enhancement.  0.04–0.08 is good.
        light_boost   : Brightness boost applied to the light side of fine edges.
                        Simulates specular oil film micro-highlights.
        shadow_deepen : Darkening applied to the shadow side of fine edges.
                        Simulates the tiny shadow grooves of fabric weave.
        figure_only   : If True and a figure mask is loaded, restrict the pass
                        to the figure region only.  This prevents excessive
                        sharpening of background elements.

        Notes
        -----
        This pass should be called AFTER glazed_panel_pass() and BEFORE the
        final vignette.  It is designed for EARLY_NETHERLANDISH period but
        benefits any period with visible micro-texture (BAROQUE, VENETIAN_RENAISSANCE,
        MANNERIST).  Keep strength below 0.30 to avoid an over-sharpened look.
        """
        print(f"Micro-detail pass  (strength={strength:.2f}  "
              f"fine_sigma={fine_sigma:.1f}  coarse_sigma={coarse_sigma:.1f})…")

        surf = self.canvas.surface
        h, w = surf.get_height(), surf.get_width()

        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0

        lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch

        # ── Fine-scale edge detection ─────────────────────────────────────────
        # Blur at fine scale, then compute Sobel gradient.
        lum_fine   = ndimage.gaussian_filter(lum, sigma=fine_sigma)
        gx_fine    = ndimage.sobel(lum_fine, axis=1).astype(np.float32)
        gy_fine    = ndimage.sobel(lum_fine, axis=0).astype(np.float32)
        mag_fine   = np.sqrt(gx_fine ** 2 + gy_fine ** 2)

        # ── Coarse-scale edge detection to subtract ───────────────────────────
        # Removing the coarse gradient isolates only micro-scale edges.
        lum_coarse = ndimage.gaussian_filter(lum, sigma=coarse_sigma)
        gx_coarse  = ndimage.sobel(lum_coarse, axis=1).astype(np.float32)
        gy_coarse  = ndimage.sobel(lum_coarse, axis=0).astype(np.float32)
        mag_coarse = np.sqrt(gx_coarse ** 2 + gy_coarse ** 2)

        # High-pass: fine edges minus coarse edges
        mag_micro = np.clip(mag_fine - mag_coarse * 0.5, 0.0, None)
        if mag_micro.max() > 1e-9:
            mag_micro = mag_micro / mag_micro.max()

        # ── Build enhancement weight map ──────────────────────────────────────
        active     = mag_micro > edge_thresh
        edge_wt    = np.clip(mag_micro, 0.0, 1.0) * strength

        # Apply figure mask if requested
        if figure_only and self._figure_mask is not None:
            active  = active & (self._figure_mask > 0.1)
            edge_wt = edge_wt * self._figure_mask

        # ── Gradient direction for light/shadow side classification ───────────
        # The gradient vector points from dark → bright.
        # Light side: move in gradient direction → more luminance nearby → boost.
        # Shadow side: move against gradient direction → less luminance → deepen.
        # Approximate: use local luminance relative to neighbourhood mean.
        lum_mean = ndimage.uniform_filter(lum, size=5)
        light_side = (lum > lum_mean) & active
        shadow_side = (lum <= lum_mean) & active

        # ── Apply enhancement ─────────────────────────────────────────────────
        boost_map  = light_boost  * edge_wt
        deepen_map = shadow_deepen * edge_wt

        r_ch = np.clip(r_ch + light_side * boost_map  - shadow_side * deepen_map, 0.0, 1.0)
        g_ch = np.clip(g_ch + light_side * boost_map * 0.95 - shadow_side * deepen_map * 0.95, 0.0, 1.0)
        b_ch = np.clip(b_ch + light_side * boost_map * 0.88 - shadow_side * deepen_map * 0.90, 0.0, 1.0)

        # ── Write back to canvas ──────────────────────────────────────────────
        buf[:, :, 2] = np.clip(r_ch * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(g_ch * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip(b_ch * 255, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255

        ctx = self.canvas.ctx
        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(tmp, 0, 0)
        ctx.paint()

        n_boosted  = int(light_side.sum())
        n_deepened = int(shadow_side.sum())
        print(f"  Micro-detail pass complete  "
              f"(light_side={n_boosted}px  shadow_side={n_deepened}px)")

    # ──────────────────────────────────────────────────────────────────────────
    # chiaroscuro_focus_pass — Artemisia Gentileschi / Caravaggesque spotlight
    # ──────────────────────────────────────────────────────────────────────────

    def chiaroscuro_focus_pass(self,
                               light_center:      Tuple[float, float] = (0.35, 0.30),
                               light_radius:      float = 0.38,
                               falloff_sharpness: float = 2.5,
                               shadow_strength:   float = 0.72,
                               shadow_color:      Color = (0.28, 0.18, 0.08),
                               light_warmth:      float = 0.12,
                               light_boost:       float = 0.06,
                               figure_only:       bool  = False):
        """
        Caravaggesque spotlight effect inspired by Artemisia Gentileschi.

        Gentileschi used a tightly focused single light source to pool warm
        ivory light in one zone while the rest of the composition fell into
        deep, velvety warm shadow.  Unlike Rembrandt's rough impasto highlights,
        her lit surfaces are smooth and seamless — built from careful blending
        rather than thick paint application.

        This pass simulates the directional falloff of her characteristic
        single-candle or directed-window lighting:

        1. Each pixel receives a light weight = exp(-d^p / r^p) where d is the
           distance from light_center (in normalised canvas coords), p =
           falloff_sharpness, and r = light_radius.  This creates a Gaussian-
           like pool for p≈2 or a harder-edged lantern at p>3.
        2. Shadow zone (weight < 0.5): progressively blend toward shadow_color.
           The blend amount is proportional to (1 - weight)^1.5, keeping the
           mid-tone transition smooth.
        3. Light zone (weight > 0.5): apply a subtle warm shift (light_warmth)
           and a small luminance boost (light_boost) to emphasise the pool.

        Parameters
        ----------
        light_center      : (cx, cy) in normalised [0,1] canvas coordinates.
                            (0,0) = top-left; (1,1) = bottom-right.
                            Default (0.35, 0.30) — upper-left source, Gentileschi
                            convention matching Caravaggio's typical arrangement.
        light_radius      : Radius of the light pool in normalised coords.
                            0.25 = very tight spot; 0.50 = broad soft fill.
        falloff_sharpness : Exponent p of the falloff curve.  2.0 = Gaussian
                            (soft); 3.5+ = lantern-like (hard edge).
        shadow_strength   : Maximum darkening factor in the shadow zone.
                            0.60 = moderate shadow; 0.85 = near-black void.
        shadow_color      : Target colour in the deepest shadow zone.
                            Warm umber default matches Gentileschi's dark grounds.
        light_warmth      : Red-channel boost in the light zone.  Simulates the
                            warm amber tint of candlelight / northern window.
        light_boost       : Overall luminance boost in the lit zone.
        figure_only       : If True and a figure mask is loaded, restrict shadow
                            darkening to the figure; leave the background as-is.
                            Default False — Gentileschi darkens backgrounds too.

        Notes
        -----
        Call AFTER block_in() / build_form() and BEFORE the final glaze.
        Combine with impasto_texture_pass() on the lit highlights for a more
        Caravaggesque texture in the specular peaks, or omit for Gentileschi's
        characteristic smooth luminosity.
        """
        print(f"Chiaroscuro focus pass  (center={light_center}  "
              f"radius={light_radius:.2f}  strength={shadow_strength:.2f})…")

        surf = self.canvas.surface
        h, w = surf.get_height(), surf.get_width()

        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0

        # ── Build distance field from light_center ─────────────────────────────
        cx_px = light_center[0] * w
        cy_px = light_center[1] * h
        # Normalised distance — use canvas diagonal as reference so radius is scale-invariant
        diag = math.sqrt(w * w + h * h)

        ys = np.arange(h, dtype=np.float32)
        xs = np.arange(w, dtype=np.float32)
        xx, yy = np.meshgrid(xs, ys)
        dist_px = np.sqrt((xx - cx_px) ** 2 + (yy - cy_px) ** 2)
        dist_n  = dist_px / diag   # normalised distance

        # ── Light weight map ───────────────────────────────────────────────────
        # Soft exponential falloff: weight = exp(-(d/r)^p)
        p       = max(1.0, falloff_sharpness)
        r_n     = max(1e-6, light_radius)
        wt      = np.exp(- (dist_n / r_n) ** p)   # shape (h, w), range [0, 1]

        # ── Shadow zone blend ─────────────────────────────────────────────────
        # blend_amount: how much to push toward shadow_color (stronger away from light)
        blend_amount = np.clip((1.0 - wt) ** 1.5 * shadow_strength, 0.0, 1.0)

        sc_r, sc_g, sc_b = shadow_color
        r_new = r_ch * (1.0 - blend_amount) + sc_r * blend_amount
        g_new = g_ch * (1.0 - blend_amount) + sc_g * blend_amount
        b_new = b_ch * (1.0 - blend_amount) + sc_b * blend_amount

        # ── Light zone warm boost ──────────────────────────────────────────────
        # Only applied where wt > 0.5 — the illuminated pool
        lit_mask = wt > 0.5
        lit_wt   = np.clip((wt - 0.5) * 2.0, 0.0, 1.0)   # 0→1 in the lit zone

        r_new = np.clip(r_new + lit_mask * lit_wt * (light_warmth + light_boost), 0.0, 1.0)
        g_new = np.clip(g_new + lit_mask * lit_wt * light_boost * 0.85,           0.0, 1.0)
        b_new = np.clip(b_new + lit_mask * lit_wt * light_boost * 0.65,           0.0, 1.0)

        # ── Apply figure mask restriction ──────────────────────────────────────
        if figure_only and self._figure_mask is not None:
            fm = self._figure_mask
            r_new = r_ch * (1.0 - fm) + r_new * fm
            g_new = g_ch * (1.0 - fm) + g_new * fm
            b_new = b_ch * (1.0 - fm) + b_new * fm

        # ── Write back ─────────────────────────────────────────────────────────
        buf[:, :, 2] = np.clip(r_new * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(g_new * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip(b_new * 255, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255

        ctx = self.canvas.ctx
        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(tmp, 0, 0)
        ctx.paint()

        n_lit    = int(lit_mask.sum())
        n_shadow = int((~lit_mask).sum())
        print(f"  Chiaroscuro focus pass complete  "
              f"(lit_zone={n_lit}px  shadow_zone={n_shadow}px)")

    # ──────────────────────────────────────────────────────────────────────────
    # highlight_bloom_pass — luminous glow around specular highlights
    # ──────────────────────────────────────────────────────────────────────────

    def highlight_bloom_pass(self,
                             threshold:     float = 0.78,
                             bloom_sigma:   float = 8.0,
                             bloom_opacity: float = 0.22,
                             bloom_color:   Optional[Color] = None,
                             multi_scale:   bool  = True,
                             figure_only:   bool  = False):
        """
        Subtle photographic bloom around the brightest specular highlights.

        In real optical systems — the human eye, early photographic lenses,
        and oil-painted varnish surfaces — very bright highlights scatter light
        into the surrounding area.  This creates a soft luminous halo, sometimes
        called 'halation', where the specular peak bleeds into the adjacent mid-tone.

        Classical portrait painters were aware of this effect: Leonardo described
        how the eye cannot focus on extreme brightness without perceiving a soft
        surrounding glow.  Gentileschi's smooth highlights on forehead and
        cheekbones appear to radiate light rather than simply reflect it — partly
        a painting convention and partly a faithful rendering of what the eye sees.

        Implementation
        --------------
        1. Read the current canvas buffer and compute luminance.
        2. Extract a highlight mask: pixels where luminance >= threshold.
        3. Multiply the RGB of masked pixels by the mask weight to get the
           'raw bloom source'.
        4. Apply Gaussian blur at bloom_sigma (and optionally at 2× and 4× for a
           multi-scale glow that has a tight inner core and a soft outer halo).
        5. Blend the blurred bloom glow back onto the canvas using a soft-light
           compositing formula: result = canvas + glow × bloom_opacity.
        6. Apply optional bloom_color tint (default: slightly warmer than the
           original highlight, simulating the warm chromatic aberration of light
           scattering through oil or glass).

        Parameters
        ----------
        threshold    : Luminance threshold above which a pixel contributes to the
                       bloom source.  0.75–0.85 isolates only the specular peaks.
        bloom_sigma  : Gaussian blur sigma for the bloom halo.  5–10 = tight,
                       elegant; 15–25 = broader, more romantic glow.
        bloom_opacity: Blend weight of the glow layer.  0.10–0.20 = subtle and
                       photographic; 0.30+ = impressionistic light flare.
        bloom_color  : Optional (R,G,B) tint applied to the glow layer.  None =
                       use the native highlight colour (no tint).  A very slight
                       warm tint (0.02, 0.0, -0.01) simulates candlelight.
        multi_scale  : If True, add a tighter inner glow (sigma/2) at half opacity
                       and a broader outer halo (sigma*2) at quarter opacity, giving
                       the characteristic three-layer bloom of optical systems.
        figure_only  : If True and a figure mask is loaded, restrict the bloom to
                       the figure region only.

        Notes
        -----
        Call AFTER all painting passes and BEFORE the final vignette / crackle.
        This is the last image-enhancement step before finishing, so it should
        see the near-final colour values.  Keep bloom_opacity low (0.12–0.22) for
        realism; higher values become painterly or impressionistic.
        """
        print(f"Highlight bloom pass  (threshold={threshold:.2f}  "
              f"sigma={bloom_sigma:.1f}  opacity={bloom_opacity:.2f})…")

        surf = self.canvas.surface
        h, w = surf.get_height(), surf.get_width()

        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0

        lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch

        # ── Build highlight source mask ────────────────────────────────────────
        # Weight ramps smoothly from 0 at threshold to 1 at pure white.
        hi_wt = np.clip((lum - threshold) / max(1.0 - threshold, 1e-6), 0.0, 1.0)

        if figure_only and self._figure_mask is not None:
            hi_wt = hi_wt * self._figure_mask

        # ── Bloom source: highlight-coloured, weighted ─────────────────────────
        bloom_r = r_ch * hi_wt
        bloom_g = g_ch * hi_wt
        bloom_b = b_ch * hi_wt

        # ── Blur the bloom source — optionally at multiple scales ──────────────
        sigma = max(0.5, bloom_sigma)

        def _blur_channel(ch: np.ndarray, s: float) -> np.ndarray:
            return ndimage.gaussian_filter(ch, sigma=s)

        glow_r = _blur_channel(bloom_r, sigma)
        glow_g = _blur_channel(bloom_g, sigma)
        glow_b = _blur_channel(bloom_b, sigma)

        if multi_scale:
            # Inner tight glow (sigma/2) at 50% weight
            ir = _blur_channel(bloom_r, sigma * 0.5)
            ig = _blur_channel(bloom_g, sigma * 0.5)
            ib = _blur_channel(bloom_b, sigma * 0.5)
            glow_r = glow_r + ir * 0.50
            glow_g = glow_g + ig * 0.50
            glow_b = glow_b + ib * 0.50
            # Outer broad halo (sigma*2) at 25% weight
            or_ = _blur_channel(bloom_r, sigma * 2.0)
            og  = _blur_channel(bloom_g, sigma * 2.0)
            ob  = _blur_channel(bloom_b, sigma * 2.0)
            glow_r = glow_r + or_ * 0.25
            glow_g = glow_g + og  * 0.25
            glow_b = glow_b + ob  * 0.25

        # ── Apply optional colour tint ─────────────────────────────────────────
        if bloom_color is not None:
            bc_r, bc_g, bc_b = bloom_color
            # Tint the glow layer: blend toward tint color weighted by glow intensity
            glow_lum = (glow_r + glow_g + glow_b) / 3.0
            glow_r = glow_r * (1.0 - 0.35) + bc_r * glow_lum * 0.35
            glow_g = glow_g * (1.0 - 0.35) + bc_g * glow_lum * 0.35
            glow_b = glow_b * (1.0 - 0.35) + bc_b * glow_lum * 0.35

        # ── Composite: additive blend clamped ─────────────────────────────────
        r_out = np.clip(r_ch + glow_r * bloom_opacity, 0.0, 1.0)
        g_out = np.clip(g_ch + glow_g * bloom_opacity, 0.0, 1.0)
        b_out = np.clip(b_ch + glow_b * bloom_opacity, 0.0, 1.0)

        # ── Write back ─────────────────────────────────────────────────────────
        buf[:, :, 2] = np.clip(r_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(g_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip(b_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255

        ctx = self.canvas.ctx
        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(tmp, 0, 0)
        ctx.paint()

        n_bloomed = int((hi_wt > 0.01).sum())
        print(f"  Highlight bloom pass complete  (bloom_source={n_bloomed}px)")

    def art_deco_facet_pass(self,
                            reference,
                            n_zones:           int   = 5,
                            smooth_sigma:      float = 3.5,
                            boundary_contrast: float = 0.28,
                            metallic_sheen:    float = 0.22,
                            saturation_boost:  float = 1.18,
                            sheen_color:       Optional[Color] = None,
                            figure_only:       bool  = False):
        """
        Art Deco faceted surface technique inspired by Tamara de Lempicka.

        De Lempicka painted flesh and drapery as a series of smooth, clearly
        bounded tonal facets — influenced equally by Ingres' polished surfaces
        and Léger's Cubist geometry.  Each facet is a discrete, nearly flat
        plane of colour.  The boundary between adjacent facets is sharpened
        to a crisp, slightly darker edge.  The overall surface reads as
        lacquered or enamelled — metal, not skin.

        The technique differs from Manet's flat_plane_pass in that:
        (a) de Lempicka's zones are smoothed *within* but contrasted *between* —
            a distinct polished-metal quality rather than Manet's chalky flatness;
        (b) a metallic sheen highlight (cool silver-cream) is placed at the top
            of each bright zone boundary, simulating the specular ridge of a
            curved reflective surface;
        (c) shadow zones receive a saturation boost toward the dominant hue —
            de Lempicka's shadows are rich and chromatic, never muddy grey.

        Implementation
        --------------
        1. Read canvas buffer; compute luminance map.
        2. Quantize luminance into n_zones tonal bands.
        3. Within each zone, apply Gaussian smoothing (sigma=smooth_sigma) to
           suppress micro-variation (the intra-zone polish).
        4. Detect zone boundaries with Sobel; build a boundary weight map.
        5. At boundaries: push toward darker tone on shadow side, lighter cool
           sheen (sheen_color) on highlight side — boundary_contrast controls
           the strength of this edge sharpening.
        6. Boost saturation in mid-tone and shadow zones (metallic surfaces
           desaturate in direct light, saturate in shadow).
        7. Composite back onto canvas; optionally figure-only.

        Parameters
        ----------
        n_zones           : Number of tonal quantization bands.  3 = very broad
                            cubist planes; 6 = finely faceted, almost smooth.
        smooth_sigma      : Gaussian sigma for intra-zone smoothing.  Higher =
                            more polished, less textured surfaces.
        boundary_contrast : Strength of boundary sharpening.  0.0 = no effect;
                            0.4 = very dramatic edge sharpening.
        metallic_sheen    : Opacity of the cool silver highlight placed at the
                            top (light side) of each boundary.
        saturation_boost  : HSV saturation multiplier applied to shadow and
                            mid-tone zones.  > 1.0 = richer shadow colour.
        sheen_color       : RGB of the metallic sheen highlight.  Default is
                            a cool silver-cream (0.90, 0.88, 0.86).
        figure_only       : If True and a figure mask is loaded, restrict the
                            pass to the figure region only.
        """
        print(f"Art Deco facet pass  (zones={n_zones}  sigma={smooth_sigma:.1f}  "
              f"contrast={boundary_contrast:.2f}  sheen={metallic_sheen:.2f})…")

        if sheen_color is None:
            sheen_color = (0.90, 0.88, 0.86)   # cool silver-cream

        surf = self.canvas.surface
        h, w = surf.get_height(), surf.get_width()

        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0

        lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch

        # ── Figure mask ────────────────────────────────────────────────────────
        fig_mask = self._figure_mask if (figure_only and self._figure_mask is not None) \
                   else np.ones((h, w), dtype=np.float32)

        # ── Stage 1: Tonal zone quantization ──────────────────────────────────
        zone_idx = np.floor(np.clip(lum, 0.0, 1.0 - 1e-6) * n_zones).astype(np.int32)

        # ── Stage 2: Per-zone Gaussian smoothing (intra-zone polish) ──────────
        r_smooth = ndimage.gaussian_filter(r_ch, sigma=smooth_sigma)
        g_smooth = ndimage.gaussian_filter(g_ch, sigma=smooth_sigma)
        b_smooth = ndimage.gaussian_filter(b_ch, sigma=smooth_sigma)

        # Blend toward smoothed version within each zone (intra-zone polish)
        # The zone index keeps boundary transitions from bleeding across zones.
        smooth_weight = 0.65   # 65% toward smoothed — keeps paint-feel from disappearing
        r_out = r_ch * (1.0 - smooth_weight) + r_smooth * smooth_weight
        g_out = g_ch * (1.0 - smooth_weight) + g_smooth * smooth_weight
        b_out = b_ch * (1.0 - smooth_weight) + b_smooth * smooth_weight

        # ── Stage 3: Zone boundary detection ──────────────────────────────────
        # Sobel on the quantized zone index map — picks up tonal boundaries.
        zone_float = zone_idx.astype(np.float32)
        sobel_x = ndimage.sobel(zone_float, axis=1)
        sobel_y = ndimage.sobel(zone_float, axis=0)
        boundary = np.sqrt(sobel_x**2 + sobel_y**2)
        # Normalise boundary to [0, 1]
        b_max = boundary.max()
        if b_max > 1e-6:
            boundary = boundary / b_max

        # ── Stage 4: Boundary sharpening ──────────────────────────────────────
        # Shadow side of each boundary: push slightly darker (warm umber)
        # Light side: add cool silver sheen
        # The Sobel gradient direction distinguishes warm from cool side:
        # positive gradient = transitioning to lighter zone (light side here)
        grad_dir = np.sign(sobel_y + sobel_x)   # rough light/shadow discriminator

        # Boundary weight: how strongly to apply sharpening at each pixel
        bwt = np.clip(boundary * boundary_contrast, 0.0, 1.0) * fig_mask

        # Shadow-side darkening (where gradient direction indicates shadow approach)
        shadow_side = np.clip(grad_dir * -1.0, 0.0, 1.0)   # pixels on shadow side
        r_out = r_out - bwt * shadow_side * 0.18
        g_out = g_out - bwt * shadow_side * 0.14
        b_out = b_out - bwt * shadow_side * 0.10

        # Light-side metallic sheen (cool silver-cream highlight at boundary ridge)
        light_side = np.clip(grad_dir, 0.0, 1.0)   # pixels on light side
        sheen_wt = bwt * light_side * metallic_sheen
        r_out = r_out + (sheen_color[0] - r_out) * sheen_wt
        g_out = g_out + (sheen_color[1] - g_out) * sheen_wt
        b_out = b_out + (sheen_color[2] - b_out) * sheen_wt

        # ── Stage 5: Shadow/midtone saturation boost ──────────────────────────
        # De Lempicka's shadows are richly coloured, never grey.
        # Convert to HSV, boost S in dark and mid-tone zones.
        r_vec = r_out.ravel()
        g_vec = g_out.ravel()
        b_vec = b_out.ravel()

        import colorsys as _cs
        r_new = r_vec.copy()
        g_new = g_vec.copy()
        b_new = b_vec.copy()

        lum_out = 0.299 * r_out + 0.587 * g_out + 0.114 * b_out
        # Apply saturation boost only to mid-tone and shadow pixels
        boost_mask = (lum_out < 0.72).ravel()
        for i in np.where(boost_mask)[0]:
            rv, gv, bv = float(r_vec[i]), float(g_vec[i]), float(b_vec[i])
            hh, ss, vv = _cs.rgb_to_hsv(rv, gv, bv)
            ss = min(1.0, ss * saturation_boost)
            rr, gg, bb = _cs.hsv_to_rgb(hh, ss, vv)
            r_new[i], g_new[i], b_new[i] = rr, gg, bb

        r_out = r_new.reshape(h, w)
        g_out = g_new.reshape(h, w)
        b_out = b_new.reshape(h, w)

        # ── Clamp and write back ───────────────────────────────────────────────
        buf[:, :, 2] = np.clip(r_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(g_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip(b_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255

        ctx = self.canvas.ctx
        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(tmp, 0, 0)
        ctx.paint()

        n_boundary_px = int((boundary > 0.1).sum())
        print(f"  Art Deco facet pass complete  "
              f"(boundary={n_boundary_px}px  zones={n_zones})")

    def velatura_pass(self,
                      midtone_tint:       Color = (0.62, 0.52, 0.32),
                      shadow_tint:        Optional[Color] = None,
                      midtone_opacity:    float = 0.10,
                      shadow_opacity:     float = 0.06,
                      midtone_lo:         float = 0.28,
                      midtone_hi:         float = 0.72,
                      lum_preserve:       bool  = True,
                      figure_only:        bool  = False):
        """
        Italian Old Master velatura (glazed midtone enrichment) technique.

        Velatura — from the Italian for 'veil' — is a technique in which a thin,
        semi-transparent coloured glaze is applied selectively over the midtone
        zones of a painting.  Unlike an overall unifying glaze (which shifts the
        entire surface), velatura is zone-selective: it enriches the mid-value
        range where local colour is most expressive while leaving highlights
        (which should stay cool-neutral) and deep shadows (which should stay
        warm-dark) relatively undisturbed.

        The technique was described by Cennini and practiced by Leonardo, Titian,
        and the Flemish masters.  In portraits it creates the sensation that flesh
        has an inner warmth — as if blood moves beneath the surface.  In landscape
        it deepens the colour complexity of middle-distance zones.

        This pass differs from the Painter.glaze() method in three ways:
        (a) It is zone-selective (midtone only), not uniform;
        (b) An optional complementary shadow tint can be applied to shadow zones
            simultaneously, creating optical depth from the warm/cool pairing;
        (c) Luminance preservation: the tint shifts hue and saturation but does
            not change the value, keeping the tonal structure intact.

        Implementation
        --------------
        1. Read canvas buffer; compute luminance.
        2. Build a soft midtone mask: 1.0 at the midtone centre, falling off to
           0.0 at shadow_lo and highlight_hi boundaries (triangle falloff).
        3. Blend each midtone pixel toward midtone_tint weighted by mask ×
           midtone_opacity.  If lum_preserve=True, adjust the tinted result to
           match the original luminance (hue/chroma shift only).
        4. If shadow_tint is given, build a complementary shadow mask and apply
           the same blend logic to shadow-zone pixels.
        5. Composite result back onto canvas; optionally figure-only.

        Parameters
        ----------
        midtone_tint    : Warm or cool tint colour for the midtone zone.  Default
                          (0.62, 0.52, 0.32) = warm amber — typical Leonardo/Titian.
                          A cool blue-grey (0.42, 0.50, 0.58) works for austere
                          Northern European portraits.
        shadow_tint     : Optional tint for shadow zone.  None = no shadow tint.
                          A warm umber (0.35, 0.24, 0.10) deepens shadows richly.
        midtone_opacity : Blend strength toward midtone_tint.  0.05–0.15 = subtle
                          and authentic; > 0.25 = strongly coloured, painterly.
        shadow_opacity  : Blend strength toward shadow_tint (if given).
        midtone_lo      : Lower luminance boundary of the midtone zone.
        midtone_hi      : Upper luminance boundary of the midtone zone.
        lum_preserve    : If True, adjust tinted result to maintain original
                          luminance so the pass is purely a hue/chroma enrichment.
        figure_only     : If True and a figure mask is loaded, restrict the pass
                          to the figure region only.

        Notes
        -----
        Call AFTER main painting passes (underpainting, block_in, build_form,
        place_lights) and BEFORE the final glaze and finish.  Velatura is an
        intermediate enrichment step, not a finishing varnish.
        """
        print(f"Velatura pass  (midtone_tint={midtone_tint}  "
              f"opacity={midtone_opacity:.2f}  lum_preserve={lum_preserve})…")

        surf = self.canvas.surface
        h, w = surf.get_height(), surf.get_width()

        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0

        lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch

        # ── Figure mask ────────────────────────────────────────────────────────
        fig_mask = self._figure_mask if (figure_only and self._figure_mask is not None) \
                   else np.ones((h, w), dtype=np.float32)

        # ── Build midtone mask (triangle falloff) ─────────────────────────────
        mid_center = (midtone_lo + midtone_hi) * 0.5
        mid_half   = (midtone_hi - midtone_lo) * 0.5
        # Linear ramp from 0 at edges to 1 at center of midtone zone
        mid_mask = np.clip(1.0 - np.abs(lum - mid_center) / max(mid_half, 1e-6),
                           0.0, 1.0) * fig_mask

        # ── Apply midtone tint ─────────────────────────────────────────────────
        mt_r, mt_g, mt_b = midtone_tint
        blend_wt = mid_mask * midtone_opacity

        r_out = r_ch + (mt_r - r_ch) * blend_wt
        g_out = g_ch + (mt_g - g_ch) * blend_wt
        b_out = b_ch + (mt_b - b_ch) * blend_wt

        # ── Luminance preservation ─────────────────────────────────────────────
        if lum_preserve:
            lum_out = 0.299 * r_out + 0.587 * g_out + 0.114 * b_out
            # Scale RGB uniformly so lum_out matches original lum
            # Avoid divide-by-zero in near-black areas
            scale = np.where(lum_out > 1e-4, lum / (lum_out + 1e-6), 1.0)
            scale = np.clip(scale, 0.0, 3.0)   # guard against runaway in pure black
            r_out = np.clip(r_out * scale, 0.0, 1.0)
            g_out = np.clip(g_out * scale, 0.0, 1.0)
            b_out = np.clip(b_out * scale, 0.0, 1.0)

        # ── Optional shadow tint ───────────────────────────────────────────────
        if shadow_tint is not None:
            st_r, st_g, st_b = shadow_tint
            # Shadow mask: pixels below midtone_lo, falling off to 0 at midtone_lo
            shad_mask = np.clip(1.0 - lum / max(midtone_lo, 1e-6),
                                0.0, 1.0) * fig_mask
            s_wt = shad_mask * shadow_opacity

            r_out = r_out + (st_r - r_out) * s_wt
            g_out = g_out + (st_g - g_out) * s_wt
            b_out = b_out + (st_b - b_out) * s_wt

            if lum_preserve:
                lum_out2 = 0.299 * r_out + 0.587 * g_out + 0.114 * b_out
                scale2 = np.where(lum_out2 > 1e-4, lum / (lum_out2 + 1e-6), 1.0)
                scale2 = np.clip(scale2, 0.0, 3.0)
                r_out = np.clip(r_out * scale2, 0.0, 1.0)
                g_out = np.clip(g_out * scale2, 0.0, 1.0)
                b_out = np.clip(b_out * scale2, 0.0, 1.0)

        # ── Write back ─────────────────────────────────────────────────────────
        buf[:, :, 2] = np.clip(r_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(g_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip(b_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255

        ctx = self.canvas.ctx
        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(tmp, 0, 0)
        ctx.paint()

        n_midtone_px = int((mid_mask > 0.05).sum())
        print(f"  Velatura pass complete  (midtone_zone={n_midtone_px}px  "
              f"lo={midtone_lo:.2f}  hi={midtone_hi:.2f})")

    def chromatic_shadow_pass(self,
                              shadow_threshold: float = 0.42,
                              strength:         float = 0.22,
                              shadow_tint:      Optional[Color] = None,
                              lum_preserve:     bool  = True,
                              figure_only:      bool  = False):
        """
        Chromatic shadow pass — inspired by Eugène Delacroix's key colour discovery.

        Delacroix's journal records his pivotal observation: shadows are not simply
        dark versions of the lit colour — they contain the chromatic COMPLEMENT of
        the dominant light.  Under warm (yellowish) light, shadows trend toward
        violet-blue; under cool (bluish) studio light, shadows trend toward warm
        amber-orange.  This is the foundational insight that separates Delacroix
        from the academic tradition and anticipates Impressionism by 30 years.

        This pass identifies shadow zones (luminance < shadow_threshold) and adds a
        subtle complementary tint to each pixel in proportion to its darkness.  The
        luminance is optionally preserved (hue/chroma shift only, not brightness) so
        the pass cannot lighten or darken the painting — only enrich the colour depth
        of shadow passages.

        Implementation
        --------------
        1. Read the current canvas buffer as float32 RGB.
        2. Compute per-pixel luminance.
        3. Build a shadow weight: shadow_wt = max(0, (threshold − lum) / threshold)^1.5
           — ramps from 0 at the threshold boundary to maximum at luminance = 0.
        4. Compute the per-pixel complement colour:
               complement = (1 − r, 1 − g, 1 − b)   [spectral complement]
           If shadow_tint is provided, use that as the fixed tint colour instead.
        5. Blend toward the complement by shadow_wt × strength × 0.5:
               r_out = r + blend × (tint_r − r)
        6. If lum_preserve: rescale each output pixel to match the original luminance,
           keeping all brightness intact — only hue and saturation shift.
        7. Apply optional figure_only masking.

        Parameters
        ----------
        shadow_threshold : Luminance below which a pixel is 'in shadow'.
                          0.42 captures the lower half of the tonal range.
                          Lower (0.30) → stronger effect; higher (0.55) → includes
                          mid-tones.
        strength         : Maximum blend fraction toward the complement colour.
                          0.15–0.25 = subtle, photographic (Impressionist level).
                          0.30–0.45 = strong, expressive (late Delacroix).
        shadow_tint      : Optional fixed (R,G,B) shadow tint.  Use when the dominant
                          light colour is known, e.g. (0.30, 0.25, 0.70) for violet
                          shadows under warm candlelight.  None = per-pixel complement.
        lum_preserve     : If True (default), rescale each shadow pixel to its
                          original luminance after blending (chrominance-only shift).
                          If False, the complement blend may lighten dark pixels.
        figure_only      : If True and a figure mask is loaded, restrict the chromatic
                          shift to the figure region only.

        Notes
        -----
        Call AFTER block_in() and build_form() but BEFORE the final glaze, so the
        chromatic shift is gently softened by the glaze layer on top.

        Delacroix used this empirically; Chevreul formulated it as the law of
        simultaneous contrast (1839); Seurat operationalised it as Divisionism;
        Monet made it the entire subject of his serial paintings (Haystacks,
        Rouen Cathedral series).
        """
        print(f"Chromatic shadow pass  (threshold={shadow_threshold:.2f}  "
              f"strength={strength:.2f}  lum_preserve={lum_preserve})…")

        surf = self.canvas.surface
        h, w = surf.get_height(), surf.get_width()

        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
        # Cairo FORMAT_ARGB32 byte order: index 0=B, 1=G, 2=R, 3=A
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0

        lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch

        # ── Shadow weight: strongest in deepest darks, fades to 0 at threshold ──
        # Power 1.5 concentrates the effect in the true shadow zones and avoids
        # contaminating the mid-tone range where the effect would look muddy.
        shadow_wt = np.clip(
            (shadow_threshold - lum) / max(shadow_threshold, 1e-6), 0.0, 1.0
        ) ** 1.5

        # ── Optional figure mask ──────────────────────────────────────────────
        if figure_only and self._figure_mask is not None:
            shadow_wt = shadow_wt * self._figure_mask

        # ── Target tint per pixel ─────────────────────────────────────────────
        if shadow_tint is not None:
            # Fixed shadow tint: the painter knows the dominant light colour
            tint_r = np.full_like(r_ch, float(shadow_tint[0]))
            tint_g = np.full_like(g_ch, float(shadow_tint[1]))
            tint_b = np.full_like(b_ch, float(shadow_tint[2]))
        else:
            # Per-pixel spectral complement: each shadow pixel drifts toward
            # its chromatic opposite.  Warm shadow pixels → cooler tint;
            # cool shadow pixels → warmer tint.  Exactly Delacroix's observation.
            tint_r = 1.0 - r_ch
            tint_g = 1.0 - g_ch
            tint_b = 1.0 - b_ch

        # ── Blend toward tint in proportion to shadow weight ──────────────────
        # Factor of 0.5 dampens the blend to a gentle chromatic enrichment rather
        # than a jarring hue inversion.  Delacroix's effect is felt, not seen.
        blend = shadow_wt * strength * 0.5
        r_out = r_ch + blend * (tint_r - r_ch)
        g_out = g_ch + blend * (tint_g - g_ch)
        b_out = b_ch + blend * (tint_b - b_ch)

        # ── Luminance preservation ────────────────────────────────────────────
        # Rescale each pixel so the output luminance matches the input.
        # This ensures chromatic_shadow_pass is a pure hue/saturation adjustment —
        # it cannot brighten or darken the painting, only enrich shadow colour.
        if lum_preserve:
            out_lum = 0.299 * r_out + 0.587 * g_out + 0.114 * b_out
            # Where the shadow_wt is near-zero, scale ≈ 1.0 (no change).
            # Clamp scale to [0.5, 2.0] to prevent numerical explosion near black.
            scale = np.where(
                out_lum > 1e-6,
                np.clip(lum / (out_lum + 1e-8), 0.5, 2.0),
                1.0
            )
            r_out = np.clip(r_out * scale, 0.0, 1.0)
            g_out = np.clip(g_out * scale, 0.0, 1.0)
            b_out = np.clip(b_out * scale, 0.0, 1.0)
        else:
            r_out = np.clip(r_out, 0.0, 1.0)
            g_out = np.clip(g_out, 0.0, 1.0)
            b_out = np.clip(b_out, 0.0, 1.0)

        # ── Write back to canvas surface ──────────────────────────────────────
        buf[:, :, 0] = np.clip(b_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(g_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 2] = np.clip(r_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255

        ctx = self.canvas.ctx
        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(tmp, 0, 0)
        ctx.paint()

        n_shadow = int((shadow_wt > 0.01).sum())
        print(f"  Chromatic shadow pass complete  (shadow_pixels={n_shadow})")

    def scumble_pass(self,
                     opacity:        float = 0.18,
                     drag_distance:  int   = 14,
                     n_drags:        int   = 420,
                     dry_factor:     float = 0.72,
                     angle_jitter:   float = 0.45,
                     figure_only:    bool  = False):
        """
        Dry-brush scumbling: semi-opaque paint dragged sideways over a dry surface.

        Scumbling is the counterpart of glazing.  Where glazing applies a
        transparent dark layer to deepen shadows (working from dark to light),
        scumbling drags a lighter, semi-opaque colour across a darker dry surface
        (working from dark toward light).  It is the technique that gives the
        chalky, slightly broken surface quality distinctive of:

          - Rembrandt's face passages: warm ivory dragged over darker flesh
          - Vuillard's Intimiste canvases: matte distemper dragged over board
          - Hals and Sargent's spontaneous dry-brush drapery marks
          - The granular mid-tones of Baroque costume painting

        Physics model
        -------------
        A loaded but dry brush touches the raised texture peaks of the canvas
        and skips the valleys.  The result is a broken field: the drag direction
        is visible, and the underlying colour shows through in gaps.  Because the
        paint is thick and dry (not wet-on-wet), the drag does not blend -- it
        deposits as a hatched, semi-transparent mark.

        Implementation
        --------------
        1. Read the current canvas into a float32 RGB buffer.
        2. For each of n_drags scumble strokes:
           a. Choose a random origin and direction (with angle_jitter variation
              around a dominant near-horizontal direction -- scumbling is usually
              a sideways arm movement).
           b. Sample the canvas colour along the drag path; compute a lightened
              version (mix toward white/cream to simulate the dry lighter pigment).
           c. Weight the deposit by the linen-texture elevation at each pixel:
              deposit only where the texture is above its median (peaks only).
              This creates the characteristic broken, granular quality.
           d. Apply at reduced opacity (dry_factor x opacity) so the underlying
              paint shows through the gaps.
        3. Write the modified buffer back to the Cairo surface.

        Parameters
        ----------
        opacity       : Global blend weight of the scumble layer.  0.10-0.20 =
                        subtle chalky patina; 0.25-0.35 = pronounced dry-brush.
        drag_distance : Length of each scumble drag stroke in pixels.  Short
                        (8-12px) = fine chalk-dust texture; longer (20-30px) =
                        visible directional marks.
        n_drags       : Number of individual drag strokes.  400-600 gives even
                        coverage; 800+ creates a strong directional texture.
        dry_factor    : How dry the paint is -- controls how strongly the texture
                        elevation gates the deposit.  1.0 = deposits only on peaks
                        (most broken / granular); 0.5 = deposits more evenly.
        angle_jitter  : Variation in drag angle (radians).  0.3 = mostly horizontal
                        with slight variation; 1.2 = multi-directional hatching.
        figure_only   : If True and a figure mask is loaded, restrict scumbling
                        to the figure region only.

        Usage examples
        --------------
        Vuillard matte chalky surface::
            scumble_pass(opacity=0.14, n_drags=600, dry_factor=0.85, drag_distance=10)
        Baroque portrait flesh::
            scumble_pass(opacity=0.10, n_drags=300, dry_factor=0.65, drag_distance=18,
                         figure_only=True)
        Sargent spontaneous drapery::
            scumble_pass(opacity=0.22, n_drags=480, drag_distance=22, dry_factor=0.55,
                         angle_jitter=0.80)
        """
        print(f"Scumble pass  (opacity={opacity:.2f}  drags={n_drags}"
              f"  drag_dist={drag_distance}px  dry={dry_factor:.2f})...")

        surf = self.canvas.surface
        h, w = surf.get_height(), surf.get_width()

        # Read current canvas
        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0

        # Linen texture as deposit gate
        if hasattr(self.canvas, 'texture') and self.canvas.texture is not None:
            tex = self.canvas.texture
        else:
            tex = make_linen_texture(w, h)

        tex_median = float(np.median(tex))
        tex_norm = np.clip((tex - tex_median) / max(tex.max() - tex_median, 1e-6),
                           0.0, 1.0)

        # Figure mask gating
        if figure_only and self._figure_mask is not None:
            region = self._figure_mask
        else:
            region = np.ones((h, w), dtype=np.float32)

        # Scumble accumulation buffers
        acc_r = np.zeros((h, w), dtype=np.float32)
        acc_g = np.zeros((h, w), dtype=np.float32)
        acc_b = np.zeros((h, w), dtype=np.float32)
        acc_w = np.zeros((h, w), dtype=np.float32)

        rng = self.rng

        for _ in range(n_drags):
            ox = int(rng.uniform(0, w))
            oy = int(rng.uniform(0, h))

            # Near-horizontal drag with angle_jitter spread
            angle = float(rng.uniform(-angle_jitter, angle_jitter))

            cos_a, sin_a = math.cos(angle), math.sin(angle)

            # Sample canvas colour at origin; scumble lightens toward warm cream
            cr = float(np.clip(r_ch[oy, ox], 0.0, 1.0))
            cg = float(np.clip(g_ch[oy, ox], 0.0, 1.0))
            cb = float(np.clip(b_ch[oy, ox], 0.0, 1.0))

            cream_r, cream_g, cream_b = 0.94, 0.89, 0.78
            scumble_r = cr * 0.62 + cream_r * 0.38
            scumble_g = cg * 0.62 + cream_g * 0.38
            scumble_b = cb * 0.62 + cream_b * 0.38

            for s in range(drag_distance):
                px = int(ox + s * cos_a)
                py = int(oy + s * sin_a)

                if px < 0 or px >= w or py < 0 or py >= h:
                    break

                # Bell taper: full weight in middle, fades at both ends
                t = s / max(drag_distance - 1, 1)
                taper = math.sin(t * math.pi)

                # Texture gate: deposit strength rises with texture elevation
                tex_gate = tex_norm[py, px] ** dry_factor

                reg = float(region[py, px])
                if reg < 0.01:
                    continue

                wt = taper * tex_gate * reg * opacity
                if wt < 1e-6:
                    continue

                acc_r[py, px] += scumble_r * wt
                acc_g[py, px] += scumble_g * wt
                acc_b[py, px] += scumble_b * wt
                acc_w[py, px] += wt

        # Composite scumble over current canvas
        wt_clamp = np.clip(acc_w, 0.0, 1.0)
        safe_w = np.where(acc_w > 1e-6, acc_w, 1.0)

        mean_r = acc_r / safe_w
        mean_g = acc_g / safe_w
        mean_b = acc_b / safe_w

        r_out = np.clip(r_ch * (1.0 - wt_clamp) + mean_r * wt_clamp, 0.0, 1.0)
        g_out = np.clip(g_ch * (1.0 - wt_clamp) + mean_g * wt_clamp, 0.0, 1.0)
        b_out = np.clip(b_ch * (1.0 - wt_clamp) + mean_b * wt_clamp, 0.0, 1.0)

        # Write back to Cairo surface
        buf[:, :, 2] = np.clip(r_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(g_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip(b_out * 255, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255

        ctx = self.canvas.ctx
        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        ctx.set_source_surface(tmp, 0, 0)
        ctx.paint()

        n_active = int((acc_w > 0.01).sum())
        print(f"  Scumble pass complete  (active_pixels={n_active})")

    def intimiste_pattern_pass(
        self,
        palette:         List[Color],
        tile_size:       int   = 28,
        n_motif_strokes: int   = 600,
        opacity:         float = 0.32,
        pattern_type:    str   = "diamond",
        figure_only:     bool  = False,
        rng_seed:        Optional[int] = None,
    ):
        """
        Vuillard-inspired Intimiste pattern pass — seeds background regions
        with a soft repeating textile motif so figure and environment share
        the same pictorial plane.

        Édouard Vuillard's hallmark is the dissolution of boundary between
        person and setting: a woman's blouse echoes the wallpaper behind
        her; a tablecloth merges with the floor.  This creates the sensation
        that figure and ground are woven from the same fabric — literally,
        since he often painted on cardboard laid on a patterned surface and
        let the support colour read through.

        This pass replicates that effect by stamping small repeating
        textile-motif strokes (diamond lattice, floral rosette, or fine
        cross-hatch) across the background, using colours drawn from the
        same palette as the figure.  The strokes are rendered at low opacity
        so the underlying paint is visible through them, creating the warm,
        layered richness of aged fabric rather than wallpaper paste.

        Implementation
        --------------
        1. Read the current canvas buffer and compute luminance.
        2. Build a background mask: use figure_mask if available, otherwise
           threshold low-chroma pixels as background.
        3. Generate tile anchor positions across the canvas in a regular grid
           offset slightly by Perlin noise (the irregularity of handmade
           textiles vs mechanical printing).
        4. For each anchor in the background mask, stamp a small motif stroke
           in a randomly selected palette colour at the given opacity.
        5. Composite using alpha blending so the underlying paint shows through.

        Pattern types
        -------------
        'diamond'  : Diagonal lattice — repeating ◆ grid, warm and domestic.
                     Most characteristic of late-19th-century French wallpaper.
        'rosette'  : Small floral blossoms — circle with radial petals.
                     Evokes the dense floral fabrics in Vuillard's interiors.
        'crosshatch': Fine parallel cross-hatching — fabric weave texture.
                     Subtler; reads as cloth rather than wallpaper.

        Parameters
        ----------
        palette          : List of (R,G,B) colours to draw from.  Pass the
                           artist's ArtStyle.palette for authentic palette harmony.
        tile_size        : Spacing in pixels between motif anchors.  Smaller =
                           denser, more wallpaper-like.  Larger = looser textile.
        n_motif_strokes  : Total number of individual motif marks to stamp.
                           600–1200 for a full 800×1000 canvas.
        opacity          : Blend weight of each motif stroke.  0.20–0.35 = warm
                           textile shimmer; 0.50+ = dominant pattern.
        pattern_type     : One of 'diamond', 'rosette', 'crosshatch'.
        figure_only      : If True, apply pattern to figure region instead of
                           background (unusual but useful for costume detailing).
        rng_seed         : Optional seed for reproducibility.

        Notes
        -----
        Call AFTER block_in() / build_form() but BEFORE glaze() and vignette().
        The pass adds warmth and pictorial flatness — calling it after glazing
        risks competing with the unifying glaze tone.
        """
        print(f"Intimiste pattern pass  (type={pattern_type!r}  "
              f"tile_size={tile_size}  opacity={opacity:.2f}  "
              f"strokes={n_motif_strokes})…")

        rng = random.Random(rng_seed)
        np_rng = np.random.default_rng(rng_seed)

        surf = self.canvas.surface
        h, w = surf.get_height(), surf.get_width()

        buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
        b_ch = buf[:, :, 0].astype(np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(np.float32) / 255.0
        r_ch = buf[:, :, 2].astype(np.float32) / 255.0

        # ── Build background mask ─────────────────────────────────────────────
        if self._figure_mask is not None and not figure_only:
            # Background is where figure mask is near zero
            bg_mask = (1.0 - self._figure_mask).astype(np.float32)
            # Feather the transition zone slightly
            bg_mask = ndimage.gaussian_filter(bg_mask, sigma=6.0)
            bg_mask = np.clip(bg_mask, 0.0, 1.0)
        elif self._figure_mask is not None and figure_only:
            bg_mask = self._figure_mask.astype(np.float32)
        else:
            # No figure mask — use chroma saturation as a proxy:
            # Low-saturation areas are likely background
            lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch
            # Treat pixels within 15% of mean luminance as background
            mean_lum = float(lum.mean())
            bg_mask = np.where(np.abs(lum - mean_lum) < 0.15, 1.0, 0.4).astype(np.float32)

        # ── Build candidate anchor grid with Perlin jitter ────────────────────
        anchors = []
        inv_w, inv_h = 1.0 / max(w, 1), 1.0 / max(h, 1)
        for gy in range(tile_size // 2, h, tile_size):
            for gx in range(tile_size // 2, w, tile_size):
                # Perlin noise jitter so the grid reads as hand-woven, not printed
                jit_x = pnoise2(gx * inv_w * 8.0, gy * inv_h * 8.0, octaves=2) * tile_size * 0.4
                jit_y = pnoise2(gx * inv_w * 8.0 + 100, gy * inv_h * 8.0 + 100, octaves=2) * tile_size * 0.4
                ax = int(gx + jit_x)
                ay = int(gy + jit_y)
                if 0 <= ax < w and 0 <= ay < h:
                    weight = float(bg_mask[ay, ax])
                    if weight > 0.1:
                        anchors.append((ax, ay, weight))

        if not anchors:
            print("  Intimiste pattern pass: no background anchors found — skipping.")
            return

        # Normalise weights to a probability distribution
        weights = np.array([a[2] for a in anchors], dtype=np.float64)
        weights /= weights.sum()

        chosen_idx = np_rng.choice(len(anchors), size=min(n_motif_strokes, len(anchors)),
                                   replace=True, p=weights)

        # ── Stamp motifs via cairo ────────────────────────────────────────────
        ctx = self.canvas.ctx
        ctx.save()

        for idx in chosen_idx:
            ax, ay, wt = anchors[idx]
            col = rng.choice(palette)
            cr, cg, cb = jitter(col, amount=0.04, rng=rng)
            alpha_base = opacity * (0.7 + 0.3 * wt)     # weaker near figure edges
            # Add a tiny per-mark size variation for the handmade textile feel
            s_factor = 0.7 + rng.uniform(0, 0.6)
            s = max(2, int(tile_size * 0.28 * s_factor))

            ctx.set_source_rgba(cr, cg, cb, alpha_base)

            if pattern_type == "diamond":
                # Rotated square (◆) — classic 19th-century French wallpaper motif
                ctx.move_to(ax,     ay - s)   # top
                ctx.line_to(ax + s, ay)       # right
                ctx.line_to(ax,     ay + s)   # bottom
                ctx.line_to(ax - s, ay)       # left
                ctx.close_path()
                ctx.set_line_width(max(1.0, s * 0.18))
                ctx.stroke()

            elif pattern_type == "rosette":
                # Small floral blossoms — circle with 6 tiny petal dabs
                petal_r = max(1.0, s * 0.30)
                for petal in range(6):
                    angle = math.pi / 3 * petal
                    px = ax + math.cos(angle) * s * 0.55
                    py = ay + math.sin(angle) * s * 0.55
                    ctx.arc(px, py, petal_r, 0, 2 * math.pi)
                    ctx.fill()
                # Centre dot
                ctx.arc(ax, ay, max(1.0, s * 0.18), 0, 2 * math.pi)
                ctx.fill()

            else:  # crosshatch
                # Fine crossed lines — fabric weave texture
                lw = max(0.8, s * 0.12)
                ctx.set_line_width(lw)
                half = s * 0.6
                ctx.move_to(ax - half, ay)
                ctx.line_to(ax + half, ay)
                ctx.stroke()
                ctx.move_to(ax, ay - half)
                ctx.line_to(ax, ay + half)
                ctx.stroke()

        ctx.restore()

        n_painted = len(chosen_idx)
        print(f"  Intimiste pattern pass complete  ({n_painted} motif marks, "
              f"type={pattern_type!r})")

    # ─────────────────────────────────────────────────────────────────────────
    # radiance_bloom_pass — Raphael High Renaissance inner luminosity
    # ─────────────────────────────────────────────────────────────────────────

    def radiance_bloom_pass(self,
                            reference,
                            glow_radius:   float = 14.0,
                            glow_opacity:  float = 0.18,
                            glow_tint:     Color = (0.78, 0.62, 0.36),
                            lum_lo:        float = 0.42,
                            lum_hi:        float = 0.74,
                            sharpness:     float = 2.0,
                            figure_only:   bool  = False):
        """
        Raphael-inspired warm radiance bloom in the lit midtone zone.

        Raphael's figures appear to *emit* warm light rather than merely reflect
        it.  Unlike specular highlight bloom (which targets the very brightest
        pixels), this pass targets the warm midtone-to-highlight transition zone
        (lum in [lum_lo, lum_hi]) — the "radiant amber band" that is the
        defining quality of Raphael's flesh rendering.

        The effect is achieved by:
          1. Building a triangle-falloff midtone mask: pixels exactly at the
             midpoint of [lum_lo, lum_hi] have weight 1.0; values at the edges
             of the range have weight 0.0. This isolates the glowing penumbra
             zone without touching deep shadows or pure highlights.
          2. Applying a wide Gaussian blur (glow_radius) to this mask so the
             warm tint blooms softly outward into adjacent tones.
          3. Blending the glow_tint colour into canvas pixels proportional to
             the blurred mask weight × glow_opacity, preserving luminance so
             the pass warms the hue/chroma without lightening or darkening
             the tonal structure.

        Unlike highlight_bloom_pass (which adds luminance), radiance_bloom_pass
        is a *chromatic* operation — it shifts warmth within the midtone range
        rather than brightening it.  This matches Raphael's technique: his
        midtones are not brighter than they should be, but they are distinctly
        *warmer* (amber-gold) compared to the cooler highlights above and the
        transparent umber shadows below.

        Parameters
        ----------
        reference   : PIL Image — used only to extract the luminance map; the
                      bloom is computed from the *current canvas*, not reference.
        glow_radius : Gaussian blur sigma for the radiance spread (pixels).
                      10–16 = realistic penumbra; 20+ = glowing halo effect.
        glow_opacity: Blend weight of the warm glow layer.  0.12–0.20 = subtle
                      Raphael-like radiance; 0.25+ = stronger warm glow.
        glow_tint   : (R,G,B) target colour for the warm glow zone.  Default is
                      warm amber-gold — Raphael's characteristic midtone colour.
        lum_lo      : Lower luminance boundary of the midtone radiance zone.
        lum_hi      : Upper luminance boundary of the midtone radiance zone.
        sharpness   : Triangle falloff exponent.  1.0 = linear; 2.0 = quadratic
                      (peakier, concentrates glow closer to the midpoint).
        figure_only : If True and a figure mask is loaded, restrict glow to the
                      figure region only (avoids warming background/landscape).

        Notes
        -----
        Call AFTER build_form() / place_lights() and BEFORE the final glaze and
        finish().  Effective on HIGH_RENAISSANCE, VENETIAN_RENAISSANCE, and any
        portrait where warm inner luminosity is desired.
        """
        import numpy as np
        from scipy.ndimage import gaussian_filter

        print(f"  Radiance bloom pass  (radius={glow_radius:.1f}  "
              f"opacity={glow_opacity:.2f}  lum=[{lum_lo:.2f},{lum_hi:.2f}])")

        # ── Read current canvas ARGB32 (premultiplied) ────────────────────────
        buf  = np.frombuffer(self.canvas.surface.get_data(),
                             dtype=np.uint8).reshape(self.h, self.w, 4).copy()
        # ARGB32: channels = B, G, R, A (little-endian BGRA on most platforms)
        B = buf[:, :, 0].astype(np.float32) / 255.0
        G = buf[:, :, 1].astype(np.float32) / 255.0
        R = buf[:, :, 2].astype(np.float32) / 255.0

        # ── Luminance map ────────────────────────────────────────────────────
        lum = 0.299 * R + 0.587 * G + 0.114 * B   # (h, w)

        # ── Triangle-falloff midtone mask ────────────────────────────────────
        mid   = (lum_lo + lum_hi) * 0.5
        span  = (lum_hi - lum_lo) * 0.5 + 1e-9
        dist  = np.abs(lum - mid) / span            # 0 at midpoint, 1 at edges
        mask  = np.clip(1.0 - dist, 0.0, 1.0) ** sharpness   # (h, w)
        mask  = np.where((lum >= lum_lo) & (lum <= lum_hi), mask, 0.0)

        # ── Apply figure mask if requested ───────────────────────────────────
        if figure_only and self._figure_mask is not None:
            fm   = self._figure_mask
            if fm.shape != (self.h, self.w):
                from PIL import Image as _PILImg
                fm = np.array(
                    _PILImg.fromarray((fm * 255).astype(np.uint8)).resize(
                        (self.w, self.h), _PILImg.BILINEAR)) / 255.0
            mask = mask * fm

        # ── Blur mask to create soft radiant spread ──────────────────────────
        blurred = gaussian_filter(mask, sigma=glow_radius)
        blurred = np.clip(blurred / (blurred.max() + 1e-9), 0.0, 1.0) * mask.max()

        # ── Blend warm tint toward canvas pixels (lum-preserve) ──────────────
        tr, tg, tb = glow_tint
        weight = blurred * glow_opacity   # (H, W) per-pixel blend weight

        # Shift toward glow_tint while preserving luminance
        new_R = R + (tr - R) * weight
        new_G = G + (tg - G) * weight
        new_B = B + (tb - B) * weight

        # Luminance preservation: rescale so lum is unchanged
        new_lum = 0.299 * new_R + 0.587 * new_G + 0.114 * new_B
        safe    = np.where(new_lum > 1e-6, lum / new_lum, 1.0)
        new_R   = np.clip(new_R * safe, 0.0, 1.0)
        new_G   = np.clip(new_G * safe, 0.0, 1.0)
        new_B   = np.clip(new_B * safe, 0.0, 1.0)

        # ── Write back to ARGB32 (BGRA layout) ────────────────────────────────
        buf[:, :, 0] = np.clip(new_B * 255.0, 0, 255).astype(np.uint8)  # B
        buf[:, :, 1] = np.clip(new_G * 255.0, 0, 255).astype(np.uint8)  # G
        buf[:, :, 2] = np.clip(new_R * 255.0, 0, 255).astype(np.uint8)  # R
        buf[:, :, 3] = 255                                                 # A

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

    # ─────────────────────────────────────────────────────────────────────────
    # reflected_light_pass — classical shadow bounce illumination
    # ─────────────────────────────────────────────────────────────────────────

    def reflected_light_pass(self,
                             warm_bounce_color: Color = (0.72, 0.52, 0.28),
                             cool_bounce_color: Color = (0.45, 0.55, 0.72),
                             warm_strength:     float = 0.14,
                             cool_strength:     float = 0.08,
                             shadow_threshold:  float = 0.40,
                             warm_y_split:      float = 0.50,
                             figure_only:       bool  = False):
        """
        Classical reflected-light shadow enrichment.

        The fundamental principle of classical painting — codified by Leonardo,
        practised by Raphael, Rubens, Vermeer, and every Academy-trained painter
        thereafter — is that *shadows contain reflected light*.  A shadow area
        is never purely dark: it receives indirect light bounced from surrounding
        surfaces.  In a standard portrait setup:

          - The lower shadow zones (facing the warm ground plane, ochre-red
            imprimatura, warm fabrics) receive a *warm* bounce:
            deep amber-sienna reflected up from below.
          - The upper shadow zones (facing the cool open sky) receive a *cool*
            bounce: blue-violet sky light filtering down from above.

        Without reflected light, shadows read as flat, dead, and painterly-wrong.
        With reflected light, even the darkest shadow passage has chromatic life
        and the painting appears to breathe.

        Implementation
        --------------
        1. Read the canvas buffer and compute luminance.
        2. Build a shadow mask: pixels where luminance < shadow_threshold.
        3. Compute a vertical gradient weight: pixels in the lower half of the
           canvas (y > warm_y_split × H) receive warm_bounce_color; pixels in
           the upper half receive cool_bounce_color.
        4. Blend the bounce color into shadow pixels at the corresponding
           strength, with luminance preservation so the tonal structure is
           unchanged — only the chromatic quality of the shadow shifts.

        This is a style-agnostic improvement: it benefits RENAISSANCE,
        HIGH_RENAISSANCE, BAROQUE, VENETIAN_RENAISSANCE, and any period where
        traditional oil-painting technique is appropriate.  It was validated as
        the session-23 random artistic improvement.

        Parameters
        ----------
        warm_bounce_color : (R,G,B) warm reflected light colour — the bounce
                            from warm ground / imprimatura / fabric below.
                            Default: warm amber-sienna.
        cool_bounce_color : (R,G,B) cool reflected light colour — sky bounce
                            from above.  Default: cool blue-violet.
        warm_strength     : Blend weight for warm bounce (lower shadows).
                            0.08–0.15 = classical subtlety; 0.20+ = vivid.
        cool_strength     : Blend weight for cool bounce (upper shadows).
                            Typically slightly weaker than warm (sky is less
                            intense than ground-plane bounce indoors).
        shadow_threshold  : Luminance below which a pixel is treated as
                            shadow and receives bounce light.  0.35–0.45.
        warm_y_split      : Normalised Y coordinate (0=top, 1=bottom) dividing
                            warm-bounce zone (below) from cool-bounce (above).
                            Default 0.50 = canvas midpoint.
        figure_only       : If True and a figure mask is loaded, restrict bounce
                            to the figure region (avoids warming background).

        Notes
        -----
        Call AFTER build_form() and before place_lights() or the final glaze,
        so the warm/cool shadow enrichment is visible but can be slightly
        modulated by subsequent highlights and glazes.
        """
        import numpy as np

        print(f"  Reflected light pass  (warm={warm_strength:.2f}  "
              f"cool={cool_strength:.2f}  shadow_thresh={shadow_threshold:.2f})")

        # ── Read current canvas ARGB32 ─────────────────────────────────────
        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(np.float32) / 255.0
        G = buf[:, :, 1].astype(np.float32) / 255.0
        R = buf[:, :, 2].astype(np.float32) / 255.0

        # ── Luminance and shadow mask ──────────────────────────────────────
        lum  = 0.299 * R + 0.587 * G + 0.114 * B
        # Shadow weight: 1.0 deep in shadow, 0.0 at threshold edge
        shad = np.clip((shadow_threshold - lum) / (shadow_threshold + 1e-9),
                       0.0, 1.0)   # (h, w)

        # ── Figure mask ────────────────────────────────────────────────────
        if figure_only and self._figure_mask is not None:
            fm = self._figure_mask
            if fm.shape != (self.h, self.w):
                from PIL import Image as _PILImg
                fm = np.array(
                    _PILImg.fromarray((fm * 255).astype(np.uint8)).resize(
                        (self.w, self.h), _PILImg.BILINEAR)) / 255.0
            shad = shad * fm

        # ── Vertical bounce gradient ───────────────────────────────────────
        ys   = np.arange(self.h, dtype=np.float32).reshape(-1, 1) / self.h  # (h,1)
        # warm_weight: 0 at top, 1 at bottom (below warm_y_split → warm)
        warm_w = np.clip((ys - warm_y_split) / (1.0 - warm_y_split + 1e-9),
                         0.0, 1.0)   # (H, 1) broadcast to (H, W)
        cool_w = np.clip((warm_y_split - ys) / (warm_y_split + 1e-9),
                         0.0, 1.0)   # (H, 1)

        # ── Apply warm bounce to lower shadows ─────────────────────────────
        wr, wg, wb = warm_bounce_color
        w_alpha    = shad * warm_w * warm_strength

        new_R = R + (wr - R) * w_alpha
        new_G = G + (wg - G) * w_alpha
        new_B = B + (wb - B) * w_alpha

        # ── Apply cool bounce to upper shadows ─────────────────────────────
        cr, cg, cb = cool_bounce_color
        c_alpha    = shad * cool_w * cool_strength

        new_R = new_R + (cr - new_R) * c_alpha
        new_G = new_G + (cg - new_G) * c_alpha
        new_B = new_B + (cb - new_B) * c_alpha

        # ── Luminance preservation ─────────────────────────────────────────
        new_lum = 0.299 * new_R + 0.587 * new_G + 0.114 * new_B
        safe    = np.where(new_lum > 1e-6, lum / new_lum, 1.0)
        new_R   = np.clip(new_R * safe, 0.0, 1.0)
        new_G   = np.clip(new_G * safe, 0.0, 1.0)
        new_B   = np.clip(new_B * safe, 0.0, 1.0)

        # ── Write back to ARGB32 (BGRA layout) ────────────────────────────────
        buf[:, :, 0] = np.clip(new_B * 255.0, 0, 255).astype(np.uint8)  # B
        buf[:, :, 1] = np.clip(new_G * 255.0, 0, 255).astype(np.uint8)  # G
        buf[:, :, 2] = np.clip(new_R * 255.0, 0, 255).astype(np.uint8)  # R
        buf[:, :, 3] = 255                                                 # A

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

    # ─────────────────────────────────────────────────────────────────────────
    # luminous_fabric_pass — Zurbarán hyper-real white cloth technique
    # ─────────────────────────────────────────────────────────────────────────

    def luminous_fabric_pass(self,
                             reference,
                             white_lum_threshold: float = 0.62,
                             white_sat_threshold:  float = 0.22,
                             fold_contrast:        float = 0.55,
                             void_darken:          float = 0.72,
                             found_edge_strength:  float = 0.60,
                             figure_only:          bool  = False):
        """
        Zurbarán hyper-real white fabric technique.

        Zurbarán's defining achievement was the sculptural rendering of white
        cloth — monk habits, linen tunics, altar cloths — emerging from near-
        absolute darkness with almost photographic precision.  Every fold of
        white fabric is a self-contained study in value: brilliant lit peak,
        warm ochre mid-shadow, deep umber at the fold recess.  The edge between
        white cloth and void background is the sharpest, most *found* edge in
        17th-century painting.

        Three operations:
        1. **Fabric fold micro-contrast** — Fine Sobel within white/ivory zones
           brightens lit fold sides and darkens shadow sides.
        2. **Void deepening** — Background zones are darkened toward absolute black.
        3. **Found-edge sharpening** — Contrast at the fabric-void boundary is
           steepened to produce Zurbarán's razor-sharp silhouettes.

        Parameters
        ----------
        reference          : PIL Image — scene reference for fabric detection.
        white_lum_threshold: Luminance above which a pixel is potentially fabric.
        white_sat_threshold: HSV saturation below which a bright pixel is cloth.
        fold_contrast      : Strength of fold micro-contrast enhancement (0–1).
        void_darken        : Blend weight toward pure black for background zones.
        found_edge_strength: Strength of fabric-void boundary contrast boost.
        figure_only        : Restrict fabric detection to figure region if True.
        """
        import numpy as np
        from PIL import Image as _PILImg
        from scipy.ndimage import gaussian_filter, sobel as _sobel

        print(f"  Luminous fabric pass  "
              f"(fold_contrast={fold_contrast:.2f}  "
              f"void_darken={void_darken:.2f}  "
              f"found_edge={found_edge_strength:.2f})")

        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(self.h, self.w, 4).copy()
        B_c = buf[:, :, 0].astype(np.float32) / 255.0
        G_c = buf[:, :, 1].astype(np.float32) / 255.0
        R_c = buf[:, :, 2].astype(np.float32) / 255.0
        lum_c = 0.299 * R_c + 0.587 * G_c + 0.114 * B_c

        # Build fabric and void masks from reference
        ref_np = np.array(reference.convert("RGB"), dtype=np.float32) / 255.0
        ref_r, ref_g, ref_b = ref_np[:, :, 0], ref_np[:, :, 1], ref_np[:, :, 2]
        ref_lum = 0.299 * ref_r + 0.587 * ref_g + 0.114 * ref_b
        cmax = np.maximum(np.maximum(ref_r, ref_g), ref_b)
        cmin = np.minimum(np.minimum(ref_r, ref_g), ref_b)
        ref_sat = np.where(cmax > 1e-6, (cmax - cmin) / (cmax + 1e-9), 0.0)
        fabric_mask = (
            (ref_lum >= white_lum_threshold) & (ref_sat <= white_sat_threshold)
        ).astype(np.float32)
        if figure_only and self._figure_mask is not None:
            fm = self._figure_mask
            if fm.shape != (self.h, self.w):
                fm = np.array(
                    _PILImg.fromarray((fm * 255).astype(np.uint8)).resize(
                        (self.w, self.h), _PILImg.BILINEAR)) / 255.0
            fabric_mask = fabric_mask * fm
        void_mask = (ref_lum < 0.30).astype(np.float32)

        # Fold micro-contrast: Sobel on canvas luminance, apply within fabric zone
        smooth_lum = gaussian_filter(lum_c, sigma=0.8)
        gx = _sobel(smooth_lum, axis=1)
        gy = _sobel(smooth_lum, axis=0)
        edge_mag   = np.sqrt(gx ** 2 + gy ** 2)
        edge_norm  = np.clip(edge_mag / (edge_mag.max() + 1e-8), 0.0, 1.0)
        grad_sign  = np.sign(gx + gy)
        fold_delta = grad_sign * edge_norm * fold_contrast * 0.18 * fabric_mask
        new_R = np.clip(R_c + fold_delta,        0.0, 1.0)
        new_G = np.clip(G_c + fold_delta * 0.88, 0.0, 1.0)
        new_B = np.clip(B_c + fold_delta * 0.62, 0.0, 1.0)

        # Void deepening
        vd_alpha = void_mask * void_darken
        new_R = new_R * (1.0 - vd_alpha)
        new_G = new_G * (1.0 - vd_alpha)
        new_B = new_B * (1.0 - vd_alpha)

        # Found-edge sharpening at fabric-void boundary
        boundary_fabric = gaussian_filter(fabric_mask, sigma=1.5)
        boundary_void   = gaussian_filter(void_mask,   sigma=1.5)
        boundary_zone   = np.minimum(boundary_fabric, boundary_void)
        fabric_side = boundary_zone * (fabric_mask > 0.5).astype(float)
        void_side   = boundary_zone * (void_mask   > 0.5).astype(float)
        boost = found_edge_strength * 0.12
        new_R = np.clip(new_R + fabric_side * boost - void_side * boost * 1.5, 0.0, 1.0)
        new_G = np.clip(new_G + fabric_side * boost - void_side * boost * 1.5, 0.0, 1.0)
        new_B = np.clip(new_B + fabric_side * boost - void_side * boost * 1.5, 0.0, 1.0)

        buf[:, :, 0] = np.clip(new_B * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(new_G * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 2] = np.clip(new_R * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255
        _tmp_fab = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(_tmp_fab, 0, 0)
        self.canvas.ctx.paint()

    # ─────────────────────────────────────────────────────────────────────────
    # edge_lost_and_found_pass — classical edge quality control (session-24 random)
    # ─────────────────────────────────────────────────────────────────────────

    def edge_lost_and_found_pass(self,
                                  focal_xy:        tuple = (0.50, 0.30),
                                  found_radius:    float = 0.28,
                                  found_sharpness: float = 0.50,
                                  lost_blur:       float = 1.8,
                                  strength:        float = 0.35,
                                  figure_only:     bool  = False):
        """
        Classical edge quality control — "lost and found" edges.

        Every skilled portrait painter distinguishes two edge types:

        - **Found edges** — sharp, crisp, advance visually.  At the focal point:
          the lit side of the face, the highest-contrast detail the eye goes to
          first.
        - **Lost edges** — soft, dissolved, recede.  At the turning of a form
          into shadow, in peripheral areas, in atmospheric distance.

        Without this distinction all edges appear equally important and the
        painting reads as flat and mechanical.  This pass:

        1. Computes a cosine-falloff "found weight" from the focal point.
        2. Applies unsharp masking to the found zone.
        3. Applies Gaussian softening to the lost zone.
        4. Blends the result into the canvas at ``strength``.

        Useful for any portrait period.  Validated as the session-24 random
        artistic improvement.

        Parameters
        ----------
        focal_xy       : (x, y) normalised focal point (0,0=top-left).
                         Default (0.50, 0.30) = upper-centre portrait face.
        found_radius   : Normalised radius within which edges are sharpened.
        found_sharpness: Unsharp mask strength in found zone (0–1).
        lost_blur      : Gaussian sigma (pixels) for lost zone softening.
        strength       : Overall blend weight (0 = no effect, 1 = full).
        figure_only    : Restrict found-zone sharpening to figure if True.
        """
        import numpy as np
        from PIL import Image as _PILImg
        from scipy.ndimage import gaussian_filter

        print(f"  Edge lost-and-found pass  "
              f"(focal={focal_xy}  found_r={found_radius:.2f}  "
              f"sharpness={found_sharpness:.2f}  lost_blur={lost_blur:.1f}  "
              f"strength={strength:.2f})")

        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(self.h, self.w, 4).copy()
        B_lf = buf[:, :, 0].astype(np.float32) / 255.0
        G_lf = buf[:, :, 1].astype(np.float32) / 255.0
        R_lf = buf[:, :, 2].astype(np.float32) / 255.0

        # Radial found-weight: cosine falloff from focal point
        fx, fy = focal_xy
        ys, xs = np.ogrid[:self.h, :self.w]
        dist_norm = np.sqrt(
            ((xs / self.w) - fx) ** 2 + ((ys / self.h) - fy) ** 2
        ) / (found_radius + 1e-9)
        found_wt = np.clip(
            0.5 * (1.0 + np.cos(np.pi * np.minimum(dist_norm, 1.0))),
            0.0, 1.0).astype(np.float32)
        lost_wt = 1.0 - found_wt

        if figure_only and self._figure_mask is not None:
            fm = self._figure_mask
            if fm.shape != (self.h, self.w):
                fm = np.array(
                    _PILImg.fromarray((fm * 255).astype(np.uint8)).resize(
                        (self.w, self.h), _PILImg.BILINEAR)) / 255.0
            found_wt = found_wt * fm

        # Unsharp mask for found zone
        um_sigma = max(0.8, lost_blur * 0.45)
        R_blur = gaussian_filter(R_lf, sigma=um_sigma)
        G_blur = gaussian_filter(G_lf, sigma=um_sigma)
        B_blur = gaussian_filter(B_lf, sigma=um_sigma)
        sharp_R = np.clip(R_lf + found_sharpness * found_wt * (R_lf - R_blur), 0.0, 1.0)
        sharp_G = np.clip(G_lf + found_sharpness * found_wt * (G_lf - G_blur), 0.0, 1.0)
        sharp_B = np.clip(B_lf + found_sharpness * found_wt * (B_lf - B_blur), 0.0, 1.0)

        # Gaussian softening for lost zone
        R_soft = gaussian_filter(sharp_R, sigma=lost_blur)
        G_soft = gaussian_filter(sharp_G, sigma=lost_blur)
        B_soft = gaussian_filter(sharp_B, sigma=lost_blur)
        result_R = sharp_R * (1.0 - lost_wt) + R_soft * lost_wt
        result_G = sharp_G * (1.0 - lost_wt) + G_soft * lost_wt
        result_B = sharp_B * (1.0 - lost_wt) + B_soft * lost_wt

        # Blend result into canvas
        final_R = np.clip(R_lf * (1.0 - strength) + result_R * strength, 0.0, 1.0)
        final_G = np.clip(G_lf * (1.0 - strength) + result_G * strength, 0.0, 1.0)
        final_B = np.clip(B_lf * (1.0 - strength) + result_B * strength, 0.0, 1.0)

        buf[:, :, 0] = np.clip(final_B * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(final_G * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 2] = np.clip(final_R * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255
        _tmp_lf = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(_tmp_lf, 0, 0)
        self.canvas.ctx.paint()

    # ─────────────────────────────────────────────────────────────────────────
    # porcelain_skin_pass — Ingres / Neoclassical smooth flesh technique
    # ─────────────────────────────────────────────────────────────────────────

    def porcelain_skin_pass(self,
                             smooth_strength:  float = 0.65,
                             highlight_cool:   float = 0.08,
                             blush_opacity:    float = 0.10,
                             highlight_thresh: float = 0.75,
                             blush_lo:         float = 0.42,
                             blush_hi:         float = 0.68,
                             smooth_sigma:     float = 2.5,
                             figure_only:      bool  = True):
        """
        Ingres / Neoclassical porcelain skin technique.

        Ingres was obsessed with an impossibly smooth, seamless skin surface —
        often described as "ivory" or "porcelain" by contemporary critics.  He
        achieved it through meticulous wet-into-wet blending of closely-valued
        flesh tones until all trace of brushwork vanished.  Two chromatic
        qualities define his flesh:

        1. **Cool pearl highlight** — the highest-lum flesh zone receives a
           barely perceptible shift toward silver-white (cool blue-white tint).
           This creates the illusion of a smooth, translucent surface catching
           diffuse light, unlike the warm-tinted highlights of most oil painters.

        2. **Warm rose blush** — flesh midtones (moderate luminance) carry a
           gentle rose warmth: a slight boost to the red channel that gives the
           face life without making it look sun-burnt.

        The pass also performs weighted Gaussian smoothing of the flesh zone to
        suppress any residual brushstroke micro-texture, then restores shadow
        edges at full contrast so the smooth flesh reads against a defined form.

        Style-agnostic: benefits NEOCLASSICAL, ACADEMIC, and any portrait period
        where the artist sought an idealised, polished skin surface.

        Parameters
        ----------
        smooth_strength  : Blend weight for Gaussian smoothing in flesh zones
                           (0 = no smoothing, 1 = full replacement with smooth).
        highlight_cool   : Strength of the cool-pearl tint applied at bright
                           flesh highlights (lum > highlight_thresh).
        blush_opacity    : Intensity of the warm rose blush in flesh midtones.
        highlight_thresh : Luminance threshold above which the cool tint is applied.
        blush_lo / hi    : Luminance range for the rose blush zone.
        smooth_sigma     : Gaussian blur sigma (pixels) for flesh smoothing.
        figure_only      : Restrict all effects to the figure mask region.
        """
        import numpy as np
        from scipy.ndimage import gaussian_filter
        from PIL import Image as _PILImg

        print(f"  Porcelain skin pass  "
              f"(smooth={smooth_strength:.2f}  cool={highlight_cool:.2f}  "
              f"blush={blush_opacity:.2f}  sigma={smooth_sigma:.1f})")

        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(self.h, self.w, 4).copy()
        # Cairo ARGB32 is stored BGRA
        B_ps = buf[:, :, 0].astype(np.float32) / 255.0
        G_ps = buf[:, :, 1].astype(np.float32) / 255.0
        R_ps = buf[:, :, 2].astype(np.float32) / 255.0

        # ── Luminance ────────────────────────────────────────────────────────
        lum_ps = 0.299 * R_ps + 0.587 * G_ps + 0.114 * B_ps

        # ── Flesh zone detection ──────────────────────────────────────────────
        # Warm pixels (R noticeably exceeds B), mid-to-high luminance.
        # The warmth criterion avoids smoothing blue/green drapery or dark hair.
        flesh_mask = (
            (R_ps > B_ps + 0.06) &
            (lum_ps > 0.28) &
            (lum_ps < 0.92)
        ).astype(np.float32)

        # Optionally restrict to figure region
        if figure_only and self._figure_mask is not None:
            fm = self._figure_mask
            if fm.shape != (self.h, self.w):
                fm = np.array(
                    _PILImg.fromarray((fm * 255).astype(np.uint8)).resize(
                        (self.w, self.h), _PILImg.BILINEAR)) / 255.0
            flesh_mask = flesh_mask * fm

        # ── Stage 1: Weighted Gaussian smoothing of flesh zones ───────────────
        # Smooth the full canvas, then composite the smoothed version back onto
        # the original canvas only in the flesh zone.  This removes brushstroke
        # micro-texture from skin without touching drapery or background.
        R_smooth = gaussian_filter(R_ps, sigma=smooth_sigma)
        G_smooth = gaussian_filter(G_ps, sigma=smooth_sigma)
        B_smooth = gaussian_filter(B_ps, sigma=smooth_sigma)

        blend = flesh_mask * smooth_strength
        R_out = R_ps * (1.0 - blend) + R_smooth * blend
        G_out = G_ps * (1.0 - blend) + G_smooth * blend
        B_out = B_ps * (1.0 - blend) + B_smooth * blend

        # ── Stage 2: Cool pearl highlight tint ───────────────────────────────
        # In the brightest flesh zone, shift toward silver-white (0.96, 0.96, 1.0).
        # This is the defining Ingres quality: porcelain-cool on the highest light.
        highlight_zone = flesh_mask * np.clip(
            (lum_ps - highlight_thresh) / (1.0 - highlight_thresh + 1e-8),
            0.0, 1.0
        ) * highlight_cool
        # Pearl tint is slightly cool: R and G stay, B lifts a little
        R_out = np.clip(R_out - highlight_zone * 0.02, 0.0, 1.0)
        G_out = np.clip(G_out - highlight_zone * 0.01, 0.0, 1.0)
        B_out = np.clip(B_out + highlight_zone * 0.06, 0.0, 1.0)

        # ── Stage 3: Rose blush in midtone flesh ─────────────────────────────
        # A gentle warm-rose boost in the flesh midtone range gives the face
        # the flushed, living warmth that separates an Ingres portrait from a
        # cold academic study.  Blush_opacity ≤ 0.12 keeps it subtle.
        blush_zone_wt = np.clip(
            1.0 - 2.0 * np.abs(lum_ps - 0.5 * (blush_lo + blush_hi))
            / (blush_hi - blush_lo + 1e-8),
            0.0, 1.0
        )
        blush_zone = flesh_mask * blush_zone_wt * blush_opacity
        R_out = np.clip(R_out + blush_zone * 0.045, 0.0, 1.0)
        G_out = np.clip(G_out + blush_zone * 0.012, 0.0, 1.0)

        # ── Write back ───────────────────────────────────────────────────────
        buf[:, :, 0] = np.clip(B_out * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(G_out * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 2] = np.clip(R_out * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255
        _tmp_ps = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(_tmp_ps, 0, 0)
        self.canvas.ctx.paint()

    # ─────────────────────────────────────────────────────────────────────────
    # tonal_compression_pass — academic value range management
    # Session-25 random artistic improvement
    # ─────────────────────────────────────────────────────────────────────────

    def tonal_compression_pass(self,
                                shadow_lift:        float = 0.04,
                                highlight_compress: float = 0.96,
                                midtone_contrast:   float = 0.06,
                                midtone_lo:         float = 0.30,
                                midtone_hi:         float = 0.70,
                                figure_only:        bool  = False):
        """
        Academic tonal range management — compression toward a refined value structure.

        Academic salon painters from David and Ingres through Bouguereau and
        Gérôme carefully managed their tonal range to create what critics called
        a "velvety" or "enamel-like" surface quality.  The key technique:

        - **No crushed blacks** — the deepest darks are lifted very slightly off
          pure black (a value of about 0.03–0.06 rather than 0.0).  This ensures
          that form structure survives in shadow passages: you can read the contour
          of a hand even in its darkest shadow.  Pure black loses information.

        - **No blown highlights** — the brightest lights are held just below pure
          white (about 0.94–0.97 rather than 1.0).  This avoids the "poster" look
          of completely lost highlights and preserves delicate surface modelling on
          forehead, collar, and satin drapery.

        - **S-curve midtone contrast** — a subtle lift of contrast in the midtone
          region (roughly 0.30–0.70 lum) creates a slight S-curve response that
          makes the tonal transitions feel richer and more intentional.  The effect
          is the same as dodging the light midtones and burning the dark midtones —
          standard darkroom practice in the 20th-century analogue of academic
          technique.

        The result is the characteristic academic tonal quality: luminous but never
        glaring, deep but never empty, with a feeling of controlled, considered
        illumination across the entire canvas.

        Parameters
        ----------
        shadow_lift        : Amount to lift the deepest shadows (0 = no change,
                             0.06 = lift 0→0.06; typical: 0.03–0.06).
        highlight_compress : Ceiling for highlights (1.0 = no compress,
                             0.95 = compress down; typical: 0.93–0.97).
        midtone_contrast   : Strength of the midtone S-curve lift (0 = none,
                             0.08 = moderate; typical: 0.03–0.10).
        midtone_lo / hi    : Luminance bounds of the midtone region for S-curve.
        figure_only        : Restrict to figure mask region if True.
        """
        import numpy as np
        from PIL import Image as _PILImg

        print(f"  Tonal compression pass  "
              f"(shadow_lift={shadow_lift:.3f}  "
              f"hi_compress={highlight_compress:.3f}  "
              f"midtone_contrast={midtone_contrast:.3f})")

        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(self.h, self.w, 4).copy()
        B_tc = buf[:, :, 0].astype(np.float32) / 255.0
        G_tc = buf[:, :, 1].astype(np.float32) / 255.0
        R_tc = buf[:, :, 2].astype(np.float32) / 255.0

        # ── Compute per-channel luminance-like scaling ────────────────────────
        # We apply the tonal mapping to each channel proportionally, preserving
        # chroma (hue and saturation) while shifting the lightness curve.
        lum_tc = 0.299 * R_tc + 0.587 * G_tc + 0.114 * B_tc
        lum_safe = np.maximum(lum_tc, 1e-8)

        # ── Stage 1: Shadow lift ──────────────────────────────────────────────
        # Remap: lum_new = lum * (1 - shadow_lift) + shadow_lift
        # Applied as a luminance scale so all channels shift equally.
        lum_lifted = lum_tc * (1.0 - shadow_lift) + shadow_lift
        scale_lift = lum_lifted / lum_safe
        R_out = np.clip(R_tc * scale_lift, 0.0, 1.0)
        G_out = np.clip(G_tc * scale_lift, 0.0, 1.0)
        B_out = np.clip(B_tc * scale_lift, 0.0, 1.0)

        # ── Stage 2: Highlight compression ───────────────────────────────────
        # Remap: lum_new = min(lum, highlight_compress)
        # Pixels brighter than the ceiling are proportionally scaled down.
        lum_after_lift = 0.299 * R_out + 0.587 * G_out + 0.114 * B_out
        lum_safe2 = np.maximum(lum_after_lift, 1e-8)
        lum_compressed = np.minimum(lum_after_lift, highlight_compress)
        scale_compress = lum_compressed / lum_safe2
        R_out = np.clip(R_out * scale_compress, 0.0, 1.0)
        G_out = np.clip(G_out * scale_compress, 0.0, 1.0)
        B_out = np.clip(B_out * scale_compress, 0.0, 1.0)

        # ── Stage 3: Midtone S-curve contrast ────────────────────────────────
        # Build a smooth triangle-peak contrast boost: peaked at the midpoint
        # of [midtone_lo, midtone_hi], falling to zero at the boundaries.
        # Pixels in the lower half of the midtone range are darkened slightly;
        # pixels in the upper half are brightened — the classic S-curve shape.
        if midtone_contrast > 0.0:
            lum_mid = 0.299 * R_out + 0.587 * G_out + 0.114 * B_out
            mid_center = 0.5 * (midtone_lo + midtone_hi)
            # Smooth triangle weight inside [midtone_lo, midtone_hi]
            mid_wt = np.clip(
                1.0 - np.abs(lum_mid - mid_center) / (0.5 * (midtone_hi - midtone_lo) + 1e-8),
                0.0, 1.0
            )
            # S-curve direction: above center → lift, below center → deepen
            s_direction = np.sign(lum_mid - mid_center)
            # Magnitude: proportional to distance from center × window weight
            s_boost = s_direction * np.abs(lum_mid - mid_center) / (mid_center + 1e-8) \
                      * mid_wt * midtone_contrast

            lum_safe3 = np.maximum(lum_mid, 1e-8)
            lum_scurve = np.clip(lum_mid + s_boost, 0.0, 1.0)
            scale_scurve = lum_scurve / lum_safe3
            R_out = np.clip(R_out * scale_scurve, 0.0, 1.0)
            G_out = np.clip(G_out * scale_scurve, 0.0, 1.0)
            B_out = np.clip(B_out * scale_scurve, 0.0, 1.0)

        # ── Apply figure_only masking if requested ────────────────────────────
        if figure_only and self._figure_mask is not None:
            fm = self._figure_mask
            from PIL import Image as _PILImg2
            if fm.shape != (self.h, self.w):
                fm = np.array(
                    _PILImg2.fromarray((fm * 255).astype(np.uint8)).resize(
                        (self.w, self.h), _PILImg2.BILINEAR)) / 255.0
            R_out = R_tc * (1.0 - fm) + R_out * fm
            G_out = G_tc * (1.0 - fm) + G_out * fm
            B_out = B_tc * (1.0 - fm) + B_out * fm

        # ── Write back ───────────────────────────────────────────────────────
        buf[:, :, 0] = np.clip(B_out * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(G_out * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 2] = np.clip(R_out * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255
        _tmp_tc = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(_tmp_tc, 0, 0)
        self.canvas.ctx.paint()

    def candlelight_pass(
            self,
            candle_x:       float = 0.50,
            candle_y:       float = 0.55,
            radius:         float = 0.55,
            candle_color:   Color = (0.92, 0.62, 0.18),
            dark_color:     Color = (0.04, 0.02, 0.01),
            warmth_peak:    float = 0.55,
            void_crush:     float = 0.88,
            falloff_power:  float = 2.2,
            figure_only:    bool  = False,
    ):
        """
        Candlelight pass — inspired by Georges de La Tour's nocturnal paintings.

        La Tour's defining achievement is the single concealed candle as sole light
        source.  His nocturnes are built on three interlocking principles:

        1. **Warm radial gradient** — a concentrated amber-orange glow emanates from
           the candle position, falling off gradually across the picture plane.  Unlike
           Caravaggio's sudden chiaroscuro cut, La Tour's light transition is long and
           tender — warmth persists into the mid-shadow before the void takes over.

        2. **Absolute void** — beyond the light's reach the canvas approaches
           near-black.  There is no reflected ambient light, no secondary source,
           no horizon.  The darkness is total and meditative.

        3. **Warm colour push** — all lit surfaces are shifted toward the candle
           color (amber-orange).  La Tour's flesh in candlelight is not ivory-white
           but a deep warm amber-rust, and his drapery loses its local colour in
           favour of the universal amber tint.

        This pass simulates all three effects in pixel space:

        * **Radial distance mask** — for each pixel, normalised distance from
          (candle_x, candle_y) is computed in canvas-diagonal units and raised to
          ``falloff_power`` to create the characteristic La Tour gradient shape
          (power > 2 keeps the bright core tight; power < 2 spreads light wider).

        * **Warmth blend** — in the bright zone (distance < radius × 0.6) the
          canvas RGB is nudged toward ``candle_color`` by ``warmth_peak × (1-t)``
          where ``t`` is the normalised distance.  This warms lit flesh and cloth.

        * **Void crush** — in the shadow zone (distance > radius × 0.5) the canvas
          is blended toward ``dark_color`` (near-black) by ``void_crush × t``.
          The transition is smooth: both effects overlap in the mid-shadow band,
          creating La Tour's characteristic amber-to-black gradient.

        The pass respects the figure mask if ``figure_only=True``, restricting the
        effect to the painted figure — useful if the background has already been
        taken to near-black by a preceding dark_void_pass or vignette.

        Parameters
        ----------
        candle_x, candle_y : Normalised canvas position (0-1) of the candle.
                             (0.5, 0.5) is dead centre.  La Tour often places the
                             candle slightly below centre (0.5, 0.55–0.65).
        radius             : Light falloff radius as a fraction of the canvas
                             diagonal.  0.45–0.65 gives a realistic candlelit pool.
        candle_color       : RGB colour of the warm candlelight (amber-orange).
        dark_color         : RGB colour of the absolute void darkness (near-black).
        warmth_peak        : Maximum warm colour push in the bright zone (0–1).
                             0.40–0.65 is typical; lower = cooler candle.
        void_crush         : Maximum darkness push in the shadow zone (0–1).
                             0.75–0.95 produces La Tour's near-black void.
        falloff_power      : Exponent controlling the shape of the radial falloff.
                             2.0 = quadratic (wide, soft); 3.0 = cubic (tighter core).
        figure_only        : Restrict effect to the figure mask if True.
        """
        print(f"  Candlelight pass  "
              f"(candle=({candle_x:.2f},{candle_y:.2f})  "
              f"radius={radius:.2f}  "
              f"warmth={warmth_peak:.2f}  void_crush={void_crush:.2f})")

        import numpy as np

        h, w = self.h, self.w

        # ── Build normalised distance map from candle position ────────────────
        # Distance is measured in canvas-diagonal units so the radius parameter
        # is resolution-independent.
        diag = math.sqrt(w * w + h * h)
        ys = np.arange(h, dtype=np.float32) / h          # 0 … 1 top→bottom
        xs = np.arange(w, dtype=np.float32) / w          # 0 … 1 left→right
        xg, yg = np.meshgrid(xs, ys)                     # (h, w)
        dx = (xg - candle_x) * w / diag
        dy = (yg - candle_y) * h / diag
        dist_raw = np.sqrt(dx * dx + dy * dy)            # 0 … ~1, candle=0

        # Normalise so radius maps to 1.0
        dist_norm = np.clip(dist_raw / max(radius, 1e-6), 0.0, 1.0)

        # Apply falloff power — tighter bright core, longer shadow tail
        t = dist_norm ** falloff_power                   # 0=candle, 1=void

        # ── Read current canvas into float32 RGB ─────────────────────────────
        buf = np.frombuffer(self.canvas.surface.get_data(),
                            dtype=np.uint8).reshape(h, w, 4).copy()
        # Cairo ARGB32: channel order in memory is B G R A
        R = buf[:, :, 2].astype(np.float32) / 255.0
        G = buf[:, :, 1].astype(np.float32) / 255.0
        B = buf[:, :, 0].astype(np.float32) / 255.0

        # ── Stage 1: Warm colour push toward candle_color ────────────────────
        # The warmth blend is strongest at t=0 (candle) and zero at t=1 (void).
        # We use a smooth curve: warmth_weight = warmth_peak * (1 - t)^2
        # so the warm push falls off quadratically — a slow, tender gradient.
        warmth_weight = warmth_peak * np.clip((1.0 - t) ** 2, 0.0, 1.0)
        cr, cg, cb = candle_color
        R_out = R + (cr - R) * warmth_weight
        G_out = G + (cg - G) * warmth_weight
        B_out = B + (cb - B) * warmth_weight

        # ── Stage 2: Void crush toward dark_color ────────────────────────────
        # The darkness blend is zero at t=0 and void_crush at t=1.
        # We use a smooth curve: crush_weight = void_crush * t^2
        # so the void creeps in gradually — the mid-shadow band stays warm.
        crush_weight = void_crush * np.clip(t ** 2, 0.0, 1.0)
        dr, dg, db = dark_color
        R_out = R_out + (dr - R_out) * crush_weight
        G_out = G_out + (dg - G_out) * crush_weight
        B_out = B_out + (db - B_out) * crush_weight

        R_out = np.clip(R_out, 0.0, 1.0)
        G_out = np.clip(G_out, 0.0, 1.0)
        B_out = np.clip(B_out, 0.0, 1.0)

        # ── Apply figure_only masking if requested ────────────────────────────
        if figure_only and self._figure_mask is not None:
            from PIL import Image as _PILImg
            fm = self._figure_mask
            if fm.shape != (h, w):
                fm = np.array(
                    _PILImg.fromarray((fm * 255).astype(np.uint8)).resize(
                        (w, h), _PILImg.BILINEAR)) / 255.0
            R_out = R * (1.0 - fm) + R_out * fm
            G_out = G * (1.0 - fm) + G_out * fm
            B_out = B * (1.0 - fm) + B_out * fm

        # ── Write back to Cairo surface ───────────────────────────────────────
        buf[:, :, 2] = np.clip(R_out * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip(G_out * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip(B_out * 255.0, 0, 255).astype(np.uint8)
        buf[:, :, 3] = 255
        _tmp_cl = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        self.canvas.ctx.set_source_surface(_tmp_cl, 0, 0)
        self.canvas.ctx.paint()

    def verdaccio_pass(
            self,
            strength:        float = 0.18,
            shadow_thresh:   float = 0.42,
            shadow_width:    float = 0.28,
            green_shift:     float = 0.55,
            figure_only:     bool  = True,
    ):
        """
        Verdaccio underpainting pass — Renaissance shadow-cooling technique.

        Verdaccio (Italian: *greenish-grey*) is the cool grey-green underpaint
        used by Leonardo, Raphael, and the Flemish masters beneath flesh tones.
        It is a mixture of terre verte (green earth), ivory black, and white,
        applied as the value-construction layer over which warm flesh glazes are
        later laid.  Where the flesh glazes are thinner — in the shadows — the
        cool grey-green shows through, creating the characteristic luminous cool
        cast of Renaissance shadow flesh.  This is why Mona Lisa's shadow side
        reads as cool blue-green rather than the warm ochre of the lit side.

        This pass simulates the optical result of a verdaccio ground that was
        never fully covered by subsequent flesh:

        * **Shadow identification** — a luminance map of the current canvas
          identifies pixels below ``shadow_thresh``.  A smooth ramp of width
          ``shadow_width`` transitions from full effect (deep shadow) to zero
          effect (highlight).

        * **Hue rotation toward verdaccio** — in-shadow pixels have their hue
          gently rotated toward the cool grey-green of terre verte (HSV hue
          ≈ 0.30–0.38).  The ``green_shift`` parameter controls the fraction of
          hue rotation applied (0 = no shift; 1 = full verdaccio tint).
          Saturation is mildly boosted in mid-shadow to match the slight
          colouration of actual terre verte (which is more green than grey).

        * **Chroma desaturation in deep shadow** — where luminance drops below
          ``shadow_thresh × 0.55``, saturation is gently reduced.  This prevents
          the verdaccio from looking artificially green in the deepest shadows
          where the underpaint would actually be near-black.

        * **Figure-only masking** — when ``figure_only=True`` (default), the
          effect is restricted to the figure mask so the background landscape
          is not affected.

        Placement in the pipeline
        -------------------------
        Call AFTER ``build_form()`` and ``atmospheric_depth_pass()`` but BEFORE
        the first ``sfumato_veil_pass()`` and any glazing.  The verdaccio sits
        below the glaze layers; the subsequent warm amber glaze re-warms the
        highlights while the cool verdaccio persists in the shadow half.

        Parameters
        ----------
        strength       : Overall blend weight toward the verdaccio tint (0–1).
                         0.12–0.22 is the typical visible range — beyond 0.30
                         the green becomes too obvious against warm flesh glazes.
        shadow_thresh  : Luminance (0–1) below which the verdaccio is applied.
                         0.38–0.46 targets shadow flesh without touching mid-tones.
        shadow_width   : Width of the smooth transition ramp from shadow to light.
                         Wider ramp = gentler transition; narrower = hard edge.
        green_shift    : Fraction of hue rotated toward terre-verte green (0–1).
                         0.40–0.65 is historically accurate; above 0.75 reads
                         as obvious green paint rather than subtle cool shadow.
        figure_only    : Apply only to the figure region if True (recommended).
        """
        print(f"  Verdaccio pass  "
              f"(strength={strength:.2f}  shadow_thresh={shadow_thresh:.2f}  "
              f"green_shift={green_shift:.2f}  figure_only={figure_only})")

        import colorsys as _cs
        import numpy as _np

        h, w = self.h, self.w

        # ── Read current canvas into float32 RGB ──────────────────────────────
        buf = _np.frombuffer(self.canvas.surface.get_data(), dtype=_np.uint8)
        buf = buf.reshape((h, w, 4)).copy()

        R = buf[:, :, 2].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        B = buf[:, :, 0].astype(_np.float32) / 255.0

        # ── Luminance map (perceptual weights) ────────────────────────────────
        lum = 0.2126 * R + 0.7152 * G + 0.0722 * B

        # Shadow mask: smooth ramp from 1.0 (deep shadow) to 0.0 (highlight)
        # Ramp: 1.0 for lum ≤ (shadow_thresh - shadow_width/2)
        #        linear fall-off to 0.0 at lum = shadow_thresh + shadow_width/2
        lo = shadow_thresh - shadow_width * 0.5
        hi = shadow_thresh + shadow_width * 0.5
        shadow_mask = _np.clip((hi - lum) / (hi - lo + 1e-8), 0.0, 1.0)

        # ── Apply figure-only masking ─────────────────────────────────────────
        if figure_only and self._figure_mask is not None:
            from PIL import Image as _PILImg
            fm = self._figure_mask
            if fm.shape != (h, w):
                fm = _np.array(
                    _PILImg.fromarray((fm * 255).astype(_np.uint8)).resize(
                        (w, h), _PILImg.BILINEAR)) / 255.0
            shadow_mask = shadow_mask * fm

        # ── Per-pixel hue rotation toward terre verte ─────────────────────────
        # Terre verte HSV hue ≈ 0.33 (greenish-grey).
        # We vectorise by processing unique quantised hue buckets for speed.
        TARGET_HUE = 0.33
        TARGET_SAT_BOOST = 0.08   # slight saturation increase in mid-shadow

        R_out = R.copy()
        G_out = G.copy()
        B_out = B.copy()

        # Flatten for vectorised HSV conversion
        r_flat = R.ravel()
        g_flat = G.ravel()
        b_flat = B.ravel()
        mask_flat = shadow_mask.ravel()
        lum_flat  = lum.ravel()

        r_new = r_flat.copy()
        g_new = g_flat.copy()
        b_new = b_flat.copy()

        # Only process pixels where shadow_mask > 0.005 (skip highlights)
        active = mask_flat > 0.005
        if active.any():
            ra = r_flat[active]
            ga = g_flat[active]
            ba = b_flat[active]
            ma = mask_flat[active]
            la = lum_flat[active]

            # Convert to HSV in vectorised fashion via a small loop over blocks
            block_size = 4096
            n = ra.shape[0]
            h_arr = _np.zeros(n, dtype=_np.float32)
            s_arr = _np.zeros(n, dtype=_np.float32)
            v_arr = _np.zeros(n, dtype=_np.float32)

            for start in range(0, n, block_size):
                end = min(start + block_size, n)
                for i in range(start, end):
                    hh, ss, vv = _cs.rgb_to_hsv(float(ra[i]), float(ga[i]), float(ba[i]))
                    h_arr[i] = hh
                    s_arr[i] = ss
                    v_arr[i] = vv

            # Hue rotation toward TARGET_HUE
            # The rotation is weighted by green_shift * shadow_mask
            hue_blend = green_shift * ma
            # Shortest-path hue interpolation
            dh = TARGET_HUE - h_arr
            # Wrap to [-0.5, 0.5]
            dh = (dh + 0.5) % 1.0 - 0.5
            h_new = h_arr + dh * hue_blend

            # Saturation: slight boost in mid-shadow, slight cut in deep shadow
            deep_shadow = _np.clip((shadow_thresh * 0.55 - la) /
                                   (shadow_thresh * 0.55 + 1e-8), 0.0, 1.0)
            mid_shadow  = ma * (1.0 - deep_shadow)
            s_new = _np.clip(s_arr + TARGET_SAT_BOOST * mid_shadow * green_shift
                             - 0.10 * deep_shadow * ma, 0.0, 1.0)

            # Convert back to RGB
            r_a_new = _np.zeros(n, dtype=_np.float32)
            g_a_new = _np.zeros(n, dtype=_np.float32)
            b_a_new = _np.zeros(n, dtype=_np.float32)

            for start in range(0, n, block_size):
                end = min(start + block_size, n)
                for i in range(start, end):
                    rr, gg, bb = _cs.hsv_to_rgb(float(h_new[i] % 1.0),
                                                 float(s_new[i]), float(v_arr[i]))
                    r_a_new[i] = rr
                    g_a_new[i] = gg
                    b_a_new[i] = bb

            # Blend: verdaccio weighted by strength × shadow_mask
            blend_w = strength * ma
            r_new[active] = ra * (1.0 - blend_w) + r_a_new * blend_w
            g_new[active] = ga * (1.0 - blend_w) + g_a_new * blend_w
            b_new[active] = ba * (1.0 - blend_w) + b_a_new * blend_w

        R_out = r_new.reshape(h, w)
        G_out = g_new.reshape(h, w)
        B_out = b_new.reshape(h, w)

        # ── Write back ────────────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(R_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(G_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(B_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255
        _tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, w, h)
        self.canvas.ctx.set_source_surface(_tmp, 0, 0)
        self.canvas.ctx.paint()
        n_active = int(active.sum()) if active.any() else 0
        print(f"    Verdaccio complete  (shadow_pixels={n_active})")

    def dry_granulation_pass(
            self,
            palette:      List[Color],
            n_marks:      int   = 1800,
            mark_size:    float = 4.5,
            opacity:      float = 0.18,
            hue_spread:   float = 0.04,
            value_spread: float = 0.06,
            figure_only:  bool  = False,
            rng_seed:     Optional[int] = None,
    ):
        """
        Dry granulation pass — inspired by Jean-Baptiste-Siméon Chardin's
        powdery, granular surface technique.

        Chardin built his surfaces through tiny overlapping dry-brush marks of
        subtly varied related colours — what Diderot described as 'pastel without
        a stylus'.  Rather than wet-blending pigments into a smooth gradient, he
        juxtaposed closely related hues (ochre-grey, blue-grey, rose-grey) in the
        same shadow passage, relying on optical mixing at viewing distance to
        resolve them into a unified, luminous tone.

        This pass simulates that granular optical surface by stamping small
        directional marks sampled from a provided palette — each mark varied
        slightly in hue and value from its neighbours.  The effect is additive
        optical mixing: no single mark dominates, but their aggregate creates
        the characteristic Chardin texture — simultaneously powdery and rich.

        Implementation
        --------------
        1. Build a luminance map of the current canvas.
        2. For each of ``n_marks`` sampled positions (uniform random over the
           canvas or figure region):
           a. Sample a base colour from ``palette``.
           b. Apply small random hue perturbation (±``hue_spread``) and value
              perturbation (±``value_spread``) in HSV space.
           c. Stamp a small rectangular mark (``mark_size`` × ``mark_size`` px)
              rotated by a random angle drawn from a Gaussian (mean=0, σ=35°)
              to simulate the natural directional variation of dry-brush marks.
           d. Composite the mark at ``opacity`` using standard alpha blending.
        3. The mark density is uniform across the canvas — Chardin's hallmark
           is that every passage (shadows, highlights, background) receives the
           same intimate attention.

        Parameters
        ----------
        palette       : List of (R,G,B) base colours to sample from.  Use
                        the artist's ``ArtStyle.palette`` for authentic harmony.
                        Chardin's palette should include warm greys, ochres, and
                        soft whites — avoid saturated colours.
        n_marks       : Number of individual dry-brush marks to stamp.
                        1500–2500 for a full 780×1080 canvas; fewer = coarser grain.
        mark_size     : Width of each stamp mark in pixels (height = 1.8 × width
                        to simulate the elongated brush mark).  3–6px is typical.
        opacity       : Composite weight of each mark.  0.12–0.22 preserves the
                        underlying paint; 0.30+ begins to overpower it.
        hue_spread    : Maximum ±hue variation from the base colour (HSV units).
                        0.03–0.06 creates varied-but-related marks; above 0.10
                        reads as random colour noise rather than optical mixing.
        value_spread  : Maximum ±value variation.  0.04–0.08 gives the powdery
                        light–dark variation within a single tone zone.
        figure_only   : If True, restrict marks to the figure mask.
        rng_seed      : Optional seed for reproducibility.
        """
        print(f"  Dry granulation pass  "
              f"(marks={n_marks}  mark_size={mark_size:.1f}  "
              f"opacity={opacity:.2f}  figure_only={figure_only})")

        import colorsys as _cs
        import numpy as _np

        rng = random.Random(rng_seed)
        h, w = self.h, self.w

        # ── Build candidate pixel pool ────────────────────────────────────────
        if figure_only and self._figure_mask is not None:
            from PIL import Image as _PILImg
            fm = self._figure_mask
            if fm.shape != (h, w):
                fm = _np.array(
                    _PILImg.fromarray((fm * 255).astype(_np.uint8)).resize(
                        (w, h), _PILImg.BILINEAR)) / 255.0
            ys, xs = _np.where(fm > 0.15)
        else:
            ys, xs = _np.mgrid[0:h:1, 0:w:1]
            ys = ys.ravel()
            xs = xs.ravel()

        n_candidates = len(ys)
        if n_candidates == 0:
            print("    No active pixels — skipping dry granulation")
            return

        mh = int(mark_size * 1.8)
        mw = int(mark_size)

        n_placed = 0
        for _ in range(n_marks):
            # Random position from candidate pool
            idx = rng.randint(0, n_candidates - 1)
            cy = int(ys[idx])
            cx = int(xs[idx])

            # Sample and perturb colour
            base = rng.choice(palette)
            bh, bs, bv = _cs.rgb_to_hsv(*base)
            bh = (bh + rng.uniform(-hue_spread, hue_spread)) % 1.0
            bv = max(0.0, min(1.0, bv + rng.uniform(-value_spread, value_spread)))
            cr, cg, cb = _cs.hsv_to_rgb(bh, bs, bv)

            # Random rotation angle (Gaussian, σ=35°)
            # Use rng.gauss; clamp to ±80°
            angle = max(-80.0, min(80.0, rng.gauss(0, 35.0)))
            angle_r = math.radians(angle)
            cos_a = math.cos(angle_r)
            sin_a = math.sin(angle_r)

            # Rasterise rotated rectangle mark
            half_h = mh / 2.0
            half_w = mw / 2.0
            for ry in range(-int(half_h) - 1, int(half_h) + 2):
                for rx in range(-int(half_w) - 1, int(half_w) + 2):
                    # Inverse rotate to check if inside unrotated rectangle
                    local_x =  rx * cos_a + ry * sin_a
                    local_y = -rx * sin_a + ry * cos_a
                    if abs(local_x) <= half_w and abs(local_y) <= half_h:
                        px = cx + rx
                        py = cy + ry
                        if 0 <= px < w and 0 <= py < h:
                            self.canvas.ctx.set_source_rgba(cr, cg, cb, opacity)
                            self.canvas.ctx.rectangle(px, py, 1, 1)
                            self.canvas.ctx.fill()
            n_placed += 1

        print(f"    Dry granulation complete  (marks_placed={n_placed})")

    def palette_knife_pass(
            self,
            palette:        List[Color],
            n_strokes:      int   = 600,
            min_length:     float = 18.0,
            max_length:     float = 60.0,
            thickness:      float = 8.0,
            opacity:        float = 0.72,
            edge_ridge:     float = 0.18,
            angle_spread:   float = 45.0,
            value_contrast: float = 0.18,
            figure_only:    bool  = False,
            rng_seed:       Optional[int] = None,
    ):
        """
        Palette knife pass — inspired by Gustave Courbet's thick impasto technique.

        Courbet frequently applied paint with flexible steel palette knives rather
        than brushes, producing a distinctive surface character:

        1. **Flat colour planes** — the knife deposits a uniform layer of paint
           in a single directional stroke.  Within each stroke the colour is nearly
           constant (unlike a brush stroke whose opacity tapers at both ends).

        2. **Clean hard edges** — the knife's straight steel edge leaves a crisp
           boundary along the sides of each stroke, unlike the feathered edge of a
           bristle brush.  Tonal transitions between planes are abrupt.

        3. **Edge ridges** — paint accumulates in a thin ridge at the terminus and
           sides of each knife stroke, creating a subtle 3D relief.  This is
           simulated here by painting a narrow darker-value border around each stroke.

        4. **Directional drag texture** — the knife moves in a single direction,
           leaving a faint linear grain along the stroke axis.

        This pass operates over the existing canvas state, building the mid-tone and
        shadow passages characteristic of Courbet's dark-ground realism.  Call it
        after ``tone_ground()`` and ``underpainting()`` but before ``place_lights()``.

        Implementation
        --------------
        For each stroke:
        1. Choose a random position (within the figure mask if ``figure_only``).
        2. Sample a colour from ``palette`` and shift its value by ±``value_contrast``
           (simulating the tonal variation between adjacent knife planes).
        3. Draw a filled rectangle of size ``length × thickness`` at a random angle
           drawn uniformly from ±``angle_spread`` degrees.
        4. Optionally draw a thin darker border (``edge_ridge`` opacity) around the
           rectangle to simulate the paint ridge.

        Parameters
        ----------
        palette        : List of (R,G,B) base colours to sample from.  Use the
                         artist's ``ArtStyle.palette`` for authentic harmony.
                         Courbet's palette should be dark earth tones.
        n_strokes      : Number of knife strokes.  400–800 for a full 780×1080
                         canvas gives the characteristic Courbet plane density.
        min_length     : Minimum stroke length in pixels.
        max_length     : Maximum stroke length in pixels.
        thickness      : Knife width in pixels (height of the stroke rectangle).
        opacity        : Fill opacity of each stroke.  0.65–0.80 keeps underlying
                         ground visible in the gaps between strokes.
        edge_ridge     : Opacity of the edge-ridge border.  0.10–0.25 gives a
                         subtle physical relief suggestion without overdoing it.
        angle_spread   : ±degrees from horizontal for stroke direction.  45° gives
                         the varied-but-mostly-horizontal feel of Courbet's large
                         outdoor compositions.
        value_contrast : ±value shift applied to each stroke's base colour in HSV.
                         0.12–0.22 creates the tonal plane separation that defines
                         Courbet's form-building without palette-knife flatness.
        figure_only    : If True, restrict strokes to the figure mask region.
        rng_seed       : Optional seed for reproducibility.
        """
        print(f"  Palette knife pass  "
              f"(strokes={n_strokes}  thickness={thickness:.1f}  "
              f"opacity={opacity:.2f}  figure_only={figure_only})")

        import colorsys as _cs
        import numpy as _np

        rng = random.Random(rng_seed)
        h, w = self.h, self.w

        # ── Build candidate pixel pool ────────────────────────────────────────
        if figure_only and self._figure_mask is not None:
            from PIL import Image as _PILImg
            fm = self._figure_mask
            if fm.shape != (h, w):
                fm = _np.array(
                    _PILImg.fromarray((fm * 255).astype(_np.uint8)).resize(
                        (w, h), _PILImg.BILINEAR)) / 255.0
            ys, xs = _np.where(fm > 0.15)
        else:
            ys, xs = _np.mgrid[0:h:1, 0:w:1]
            ys = ys.ravel()
            xs = xs.ravel()

        n_candidates = len(ys)
        if n_candidates == 0:
            print("    No active pixels — skipping palette knife pass")
            return

        half_t = thickness / 2.0
        n_placed = 0

        for _ in range(n_strokes):
            # Random anchor position
            idx = rng.randint(0, n_candidates - 1)
            cy = int(ys[idx])
            cx = int(xs[idx])

            # Stroke geometry: length and angle
            length = rng.uniform(min_length, max_length)
            angle_deg = rng.uniform(-angle_spread, angle_spread)
            angle_r = math.radians(angle_deg)
            cos_a = math.cos(angle_r)
            sin_a = math.sin(angle_r)

            half_l = length / 2.0

            # Sample and perturb colour (value shift for tonal plane separation)
            base = rng.choice(palette)
            bh, bs, bv = _cs.rgb_to_hsv(*base)
            bv = max(0.0, min(1.0, bv + rng.uniform(-value_contrast, value_contrast)))
            cr, cg, cb = _cs.hsv_to_rgb(bh, bs, bv)

            # ── Draw filled knife stroke (rotated rectangle) ──────────────────
            # Scan bounding box of the rotated rectangle
            corners_l = [-half_l, half_l, half_l, -half_l]
            corners_t = [-half_t, -half_t, half_t, half_t]
            px_corners = [cx + cl * cos_a - ct * sin_a for cl, ct in zip(corners_l, corners_t)]
            py_corners = [cy + cl * sin_a + ct * cos_a for cl, ct in zip(corners_l, corners_t)]

            bx0 = max(0, int(min(px_corners)) - 1)
            bx1 = min(w - 1, int(max(px_corners)) + 2)
            by0 = max(0, int(min(py_corners)) - 1)
            by1 = min(h - 1, int(max(py_corners)) + 2)

            self.canvas.ctx.set_source_rgba(cr, cg, cb, opacity)
            for py in range(by0, by1 + 1):
                for px in range(bx0, bx1 + 1):
                    # Transform to stroke-local coordinates (inverse rotate)
                    dx = px - cx
                    dy = py - cy
                    local_l =  dx * cos_a + dy * sin_a
                    local_t = -dx * sin_a + dy * cos_a
                    if abs(local_l) <= half_l and abs(local_t) <= half_t:
                        self.canvas.ctx.rectangle(px, py, 1, 1)
            self.canvas.ctx.fill()

            # ── Edge ridge: thin darker border around the knife stroke ────────
            if edge_ridge > 0.0:
                ridge_r = max(0.0, cr - 0.15)
                ridge_g = max(0.0, cg - 0.15)
                ridge_b = max(0.0, cb - 0.15)
                self.canvas.ctx.set_source_rgba(ridge_r, ridge_g, ridge_b, edge_ridge)
                ridge_margin = 1.5
                for py in range(by0, by1 + 1):
                    for px in range(bx0, bx1 + 1):
                        dx = px - cx
                        dy = py - cy
                        local_l =  dx * cos_a + dy * sin_a
                        local_t = -dx * sin_a + dy * cos_a
                        in_outer = (abs(local_l) <= half_l + ridge_margin and
                                    abs(local_t) <= half_t + ridge_margin)
                        in_inner = (abs(local_l) <= half_l - 0.5 and
                                    abs(local_t) <= half_t - 0.5)
                        if in_outer and not in_inner:
                            self.canvas.ctx.rectangle(px, py, 1, 1)
                self.canvas.ctx.fill()

            n_placed += 1

        print(f"    Palette knife complete  (strokes_placed={n_placed})")

    # academic_skin_pass — Bouguereau porcelain-smooth flesh technique
    # ─────────────────────────────────────────────────────────────────────────
    def academic_skin_pass(
            self,
            reference:      Union[np.ndarray, Image.Image],
            n_passes:       int   = 4,
            strokes_per_pass: int = 600,
            stroke_size:    float = 3.5,
            wet_blend:      float = 0.88,
            opacity:        float = 0.38,
            skin_thresh_low: float = 0.38,
            skin_thresh_high: float = 0.88,
            jitter_amt:     float = 0.008,
            rng_seed:       Optional[int] = None,
    ):
        """
        Academic skin pass — inspired by William-Adolphe Bouguereau's porcelain-smooth
        flesh technique.

        Bouguereau built his characteristically seamless flesh through many sessions of
        imperceptibly fine brushwork.  Each session laid down tiny, carefully graduated
        strokes that were immediately blended with a dry soft brush before the paint set.
        After multiple sessions — each at a slightly different stroke angle — all trace of
        individual marks was erased, leaving a surface of extraordinary smoothness that
        critics described as "wax" or "porcelain."

        This pass simulates that quality:

        1. **Skin detection**: only skin-toned pixels in the reference are targeted —
           regions where luminance is in the mid-to-high range and the hue is in the
           warm flesh band (red-orange-yellow).  This keeps the pass from touching
           hair, clothing, or the background.

        2. **Multi-pass micro-blending**: ``n_passes`` passes of tiny strokes are applied.
           Each pass uses a slightly different angle offset so the directionality of no
           single pass dominates.  Within each pass, strokes are placed with very high
           ``wet_blend`` (default 0.88) so each mark is nearly fully blended with the
           paint already on the canvas beneath it — the stroke deposits colour without
           leaving a discrete edge.

        3. **Graduated colour sampling**: the colour for each stroke is sampled from the
           reference at the stroke's anchor point, then perturbed by a tiny jitter
           (default ±0.008).  At this jitter level the perceptual variation is below the
           threshold of the human eye but above zero, preventing the mechanical
           uniformity of a flat digital fill.

        4. **Angle variation per pass**: each of the ``n_passes`` passes rotates the
           stroke angle distribution by ``180° / n_passes``.  The cumulative effect is
           that strokes cross each other at many angles, producing the isotropic surface
           quality of true Academic blending — no single brush direction can be seen.

        Call this pass AFTER ``build_form()`` and BEFORE ``place_lights()``.
        The pass concentrates on the figure area (if a figure mask is set) and within
        that area on skin-toned regions detected from the reference.  Follow with
        ``glazed_panel_pass()`` at low opacity to add Bouguereau's characteristic warm
        golden depth without disturbing the smooth surface.

        Parameters
        ----------
        reference        : The colour reference image — used both to detect skin regions
                           and to sample stroke colours.
        n_passes         : Number of blending passes.  Each adds a further layer of
                           imperceptible smoothing.  4–6 passes approximate a single
                           Bouguereau glazing session; 8–12 approach his full multi-day
                           technique.
        strokes_per_pass : Number of strokes per pass.  600–1000 covers a 780×1080 face
                           region with dense micro-marks.
        stroke_size      : Stroke radius in pixels.  2–4px gives Bouguereau's finest
                           filbert-tip quality.  Values above 6 produce a visible, more
                           Sargent-like mark.
        wet_blend        : Blending strength.  0.85–0.92 for true porcelain smoothness.
                           Values below 0.70 leave a visible brushstroke texture.
        opacity          : Per-stroke opacity.  0.30–0.45 allows many passes to build up
                           without any single pass dominating the surface.
        skin_thresh_low  : Minimum luminance for a pixel to be considered skin.  Default
                           0.38 excludes deep shadow regions (which do not benefit from
                           the smooth blending pass).
        skin_thresh_high : Maximum luminance for a pixel to be considered skin.  Default
                           0.88 excludes specular highlights (which should remain crisp
                           after ``place_lights()``).
        jitter_amt       : Per-stroke colour jitter.  0.005–0.012 is the sweet spot for
                           organic variation below the threshold of perception.
        rng_seed         : Optional seed for reproducibility.
        """
        print(f"  Academic skin pass  "
              f"(n_passes={n_passes}  strokes/pass={strokes_per_pass}  "
              f"size={stroke_size:.1f}  wet_blend={wet_blend:.2f})")

        import colorsys as _cs
        import numpy as _np

        rng   = random.Random(rng_seed)
        ref   = self._prep(reference)           # → uint8 (H, W, 4)
        h, w  = self.h, self.w

        # ── Normalize to float32 [0, 1] and resize if necessary ──────────────
        # _prep() returns uint8 (H, W, 4); we always need float32 (H, W, 3)
        # in [0, 1] for luminance computation and skin detection thresholds.
        if ref.shape[:2] != (h, w):
            from PIL import Image as _PILImg
            ref_img = _PILImg.fromarray(ref[:, :, :3].astype(_np.uint8), "RGB")
            ref = _np.array(ref_img.resize((w, h), _PILImg.BILINEAR)).astype(_np.float32) / 255.0
        else:
            ref = ref[:, :, :3].astype(_np.float32) / 255.0

        # ── Build skin mask: warm-hue + mid-luminance pixels ─────────────────
        # Luminance (perceptual): 0.299 R + 0.587 G + 0.114 B
        lum = (0.299 * ref[:, :, 0] +
               0.587 * ref[:, :, 1] +
               0.114 * ref[:, :, 2])

        # Warm skin hue: red channel dominant, green secondary, blue minimal.
        # This detects orange-yellow-red flesh without picking up foliage or sky.
        warm_hue = (ref[:, :, 0] > ref[:, :, 2] + 0.06) & \
                   (ref[:, :, 0] > ref[:, :, 1] - 0.10)

        skin_mask = (
            warm_hue &
            (lum >= skin_thresh_low) &
            (lum <= skin_thresh_high)
        )

        # Intersect with figure mask if available
        if self._figure_mask is not None:
            fm = self._figure_mask
            if fm.shape != (h, w):
                from PIL import Image as _PILImg
                fm = _np.array(
                    _PILImg.fromarray((fm * 255).astype(_np.uint8)).resize(
                        (w, h), _PILImg.BILINEAR)) / 255.0
            skin_mask = skin_mask & (fm > 0.15)

        ys, xs = _np.where(skin_mask)
        n_candidates = len(ys)
        if n_candidates == 0:
            print("    No skin pixels detected — skipping academic_skin_pass")
            return

        print(f"    Skin region: {n_candidates} pixels  "
              f"({100.0 * n_candidates / (h * w):.1f}% of canvas)")

        total_placed = 0

        for pass_idx in range(n_passes):
            # Each pass rotates the angle distribution to erase directionality
            angle_offset = pass_idx * (180.0 / n_passes)
            pass_placed  = 0

            for _ in range(strokes_per_pass):
                idx = rng.randint(0, n_candidates - 1)
                cy  = int(ys[idx])
                cx  = int(xs[idx])

                # Sample colour from reference at this location
                r_s = float(ref[cy, cx, 0])
                g_s = float(ref[cy, cx, 1])
                b_s = float(ref[cy, cx, 2])
                # Tiny perceptual jitter — organic but sub-threshold
                r_s = max(0.0, min(1.0, r_s + rng.uniform(-jitter_amt, jitter_amt)))
                g_s = max(0.0, min(1.0, g_s + rng.uniform(-jitter_amt, jitter_amt)))
                b_s = max(0.0, min(1.0, b_s + rng.uniform(-jitter_amt, jitter_amt)))

                # Stroke angle: small spread around the per-pass base angle
                angle_deg = angle_offset + rng.uniform(-22.0, 22.0)
                angle_r   = math.radians(angle_deg)

                # Stroke length: short — these are micro-blending marks, not form strokes
                length = rng.uniform(stroke_size * 1.8, stroke_size * 4.5)

                # Place the stroke using the canvas's apply_stroke infrastructure
                # Build a two-point path along the stroke direction
                dx = math.cos(angle_r) * length * 0.5
                dy = math.sin(angle_r) * length * 0.5
                pts = [(cx - dx, cy - dy), (cx + dx, cy + dy)]

                n_pts = len(pts)
                widths = [stroke_size * 0.9, stroke_size * 0.9]  # uniform width — filbert flat

                self.canvas.apply_stroke(
                    pts     = pts,
                    widths  = widths,
                    color   = (r_s, g_s, b_s),
                    tip     = BrushTip(BrushTip.FILBERT),
                    opacity = opacity,
                    wet_blend = wet_blend,
                )
                pass_placed += 1

            total_placed += pass_placed
            # Partial dry between passes: settles slightly but stays workable.
            # This prevents consecutive passes from becoming a single merged wash.
            self.canvas.dry(amount=0.18)

        print(f"    Academic skin complete  "
              f"(total_strokes={total_placed}  passes={n_passes})")

    # ─────────────────────────────────────────────────────────────────────────
    # north_light_diffusion_pass — Mary Cassatt's north-window indoor daylight
    # ─────────────────────────────────────────────────────────────────────────

    def north_light_diffusion_pass(
            self,
            light_side:            str   = "left",
            cool_highlight_color:  Color = (0.72, 0.80, 0.92),
            warm_shadow_color:     Color = (0.88, 0.70, 0.42),
            cool_strength:         float = 0.10,
            warm_strength:         float = 0.08,
            gradient_sharpness:    float = 2.0,
            blend_opacity:         float = 0.30,
    ):
        """
        Simulates Mary Cassatt's characteristic north-window indoor daylight.

        Unlike the dramatic single-source chiaroscuro of Baroque painting or the
        outdoor broken-colour sunlight of Impressionism, Cassatt's indoor north-
        window light has three qualities that distinguish it:

        1. **Diffused and even**: the sky is the light source, not the sun.
           There is no hard terminator between light and shadow — the transition
           is gradual and soft across the whole form.

        2. **Cool on the lit side**: indirect sky light is perceptually cooler
           (blue-grey) than daylight.  The lit side of flesh and fabric carries
           a cool, silvery quality rather than the warm golden tone of sunlight.

        3. **Warm in the shadow**: interior shadows receive reflected warm light
           bouncing from walls, floors, and warm-coloured furniture.  Cassatt's
           shadow areas are never cold or dead — they glow with amber warmth.

        Implementation
        --------------
        A smooth horizontal (or vertical) gradient divides the canvas into a
        lit half and a shadow half.  The gradient uses a raised-cosine profile
        so the transition is natural rather than mechanical:

          - Lit pixels receive a cool blue-grey tint (``cool_highlight_color``)
            blended at ``cool_strength``.
          - Shadow pixels receive a warm amber tint (``warm_shadow_color``)
            blended at ``warm_strength``.
          - In the transition zone both influences are present, weighted by the
            gradient: no hard edge anywhere on the canvas.

        Luminance is preserved throughout: only the chromatic quality of the
        surface changes, not its tonal structure.

        Call AFTER ``build_form()`` and BEFORE ``place_lights()`` or the final
        glaze.  The pass complements ``reflected_light_pass()`` — they can be
        used together, with this pass setting the broad cool/warm temperature
        split and ``reflected_light_pass()`` adding fine shadow chromatics.

        Parameters
        ----------
        light_side            : Which side the north window is on.
                                "left", "right", "top", or "bottom".
        cool_highlight_color  : (R,G,B) for the lit-side cool tint.
                                Default: pale blue-grey (north sky quality).
        warm_shadow_color     : (R,G,B) for the shadow-side warm tint.
                                Default: warm amber (wall/floor bounce).
        cool_strength         : Blend weight for the cool highlight tint.
                                0.06–0.12 = subtle Cassatt quality; 0.20+ = very blue.
        warm_strength         : Blend weight for the warm shadow tint.
                                Slightly weaker than cool by default — the warm
                                bounce is gentler than the sky's influence on the lit.
        gradient_sharpness    : Controls how quickly the gradient transitions.
                                1.0 = linear; 2.0 = S-curve; 3.0+ = more abrupt.
                                Cassatt's diffused north light suits 1.8–2.5.
        blend_opacity         : Global opacity of the entire pass.  Allows the
                                pass to be stacked multiple times at low opacity
                                for a more gradual build (Cassatt's pastel technique).

        Notes
        -----
        Inspired by: "In the Loge" (1878), "The Child's Bath" (1893),
        "Little Girl in a Blue Armchair" (1878).
        Validated as this session's random artistic improvement pass.
        """
        import numpy as _np

        print(f"  North-light diffusion pass  "
              f"(side={light_side}  cool={cool_strength:.2f}  "
              f"warm={warm_strength:.2f}  opacity={blend_opacity:.2f})")

        # ── Read current canvas ARGB32 (BGRA byte order in pycairo) ──────────
        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        R = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.299 * R + 0.587 * G + 0.114 * B

        # ── Build the light-to-shadow gradient (0 = full shadow, 1 = full lit) ─
        # Raised cosine profile: smooth S-curve between 0 and 1.
        h, w = self.h, self.w
        if light_side == "left":
            axis = _np.linspace(0.0, 1.0, w, dtype=_np.float32)[_np.newaxis, :]
        elif light_side == "right":
            axis = _np.linspace(1.0, 0.0, w, dtype=_np.float32)[_np.newaxis, :]
        elif light_side == "top":
            axis = _np.linspace(0.0, 1.0, h, dtype=_np.float32)[:, _np.newaxis]
        else:   # "bottom"
            axis = _np.linspace(1.0, 0.0, h, dtype=_np.float32)[:, _np.newaxis]

        # Smooth S-curve via raised cosine raised to gradient_sharpness power
        # Value = 1.0 at the lit side; 0.0 at the shadow side.
        lit_weight  = (0.5 - 0.5 * _np.cos(_np.pi * axis)) ** gradient_sharpness
        shad_weight = 1.0 - lit_weight   # complement

        # Broadcast to (H, W) — both arrays are already (1, W) or (H, 1)
        # _np broadcasting handles the expansion automatically.
        lit_weight  = lit_weight  * _np.ones((h, w), dtype=_np.float32)
        shad_weight = shad_weight * _np.ones((h, w), dtype=_np.float32)

        # ── Apply cool tint on the lit side ───────────────────────────────────
        cr, cg, cb = cool_highlight_color
        cool_alpha  = lit_weight * cool_strength * blend_opacity
        new_R = R + (cr - R) * cool_alpha
        new_G = G + (cg - G) * cool_alpha
        new_B = B + (cb - B) * cool_alpha

        # ── Apply warm tint on the shadow side ────────────────────────────────
        wr, wg, wb = warm_shadow_color
        warm_alpha  = shad_weight * warm_strength * blend_opacity
        new_R = new_R + (wr - new_R) * warm_alpha
        new_G = new_G + (wg - new_G) * warm_alpha
        new_B = new_B + (wb - new_B) * warm_alpha

        # ── Luminance preservation — chromatic shift only, tonal structure kept ─
        new_lum = 0.299 * new_R + 0.587 * new_G + 0.114 * new_B
        safe    = _np.where(new_lum > 1e-6, lum / new_lum, 1.0)
        new_R   = _np.clip(new_R * safe, 0.0, 1.0)
        new_G   = _np.clip(new_G * safe, 0.0, 1.0)
        new_B   = _np.clip(new_B * safe, 0.0, 1.0)

        # ── Write back to ARGB32 surface (BGRA layout) ───────────────────────
        buf[:, :, 0] = _np.clip(new_B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 2] = _np.clip(new_R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"    North-light diffusion complete")

    # ─────────────────────────────────────────────────────────────────────────
    # bruegel_panorama_pass — Flemish aerial perspective
    # ─────────────────────────────────────────────────────────────────────────

    def bruegel_panorama_pass(
        self,
        *,
        haze_color:        Tuple[float, float, float] = (0.72, 0.78, 0.88),
        horizon_fraction:  float = 0.65,
        near_fraction:     float = 0.25,
        haze_opacity:      float = 0.55,
        desaturation:      float = 0.70,
        lightening:        float = 0.30,
        blend_mode:        str   = "normal",
    ) -> None:
        """
        Systematic aerial-perspective haze inspired by Pieter Bruegel the Elder.

        Bruegel was the first Northern European painter to apply Leonardo's
        atmospheric recession theory consistently across a whole canvas.  The
        result is a three-zone depth system that gives his panoramic landscapes
        their sensation of vast inhabited space:

          Foreground  (bottom near_fraction of the canvas)
              Warm, fully saturated earth tones — no haze applied.

          Middle-ground  (between near_fraction and horizon_fraction)
              Gradual cool temperature shift; moderate desaturation; faint
              blue-grey overlay blended in at rising opacity.

          Far-ground  (top, above horizon_fraction from bottom)
              Full desaturation toward near-monochrome; maximum blue-grey
              haze overlay at haze_opacity; atmospheric lightening lifts darks.

        Parameters
        ----------
        haze_color       : (R, G, B) in [0, 1] — atmospheric haze colour.
                           Bruegel's distance is cool blue-grey; winter scenes
                           use a paler, greyer variant.
        horizon_fraction : fraction of canvas height (from bottom) where the far
                           haze reaches full strength.  Default 0.65 places the
                           horizon in the upper third — Bruegel's high vantage.
        near_fraction    : fraction of canvas height (from bottom) that is
                           pure foreground — no haze applied here.  Default 0.25.
        haze_opacity     : maximum opacity of the haze overlay at full distance.
        desaturation     : fraction by which to desaturate at full depth (0 = none,
                           1 = full greyscale).
        lightening       : fraction by which to lighten dark pixels at full depth,
                           simulating the luminous pale horizon sky bleeding into
                           far-distance land masses.
        blend_mode       : 'normal' (alpha composite) or 'screen' (lighter effect).

        Notes
        -----
        The pass reads the current canvas pixel buffer, computes per-pixel
        depth weight from vertical position, then writes the modified buffer
        back to the cairo surface.  It is composable: apply after tone_ground()
        and build_form() passes but before final glaze.
        """
        import numpy as _np

        buf = _np.frombuffer(
            self.canvas.surface.get_data(), dtype=_np.uint8
        ).reshape((self.h, self.w, 4)).copy()

        # BGRA → float RGB
        R = buf[:, :, 2].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        B = buf[:, :, 0].astype(_np.float32) / 255.0

        # ── Depth weight: 0.0 at foreground base, 1.0 at far horizon ──────────
        # y=0 is the top of the canvas (far distance in a high-horizon scene).
        # Bruegel's foreground is at the bottom (y_norm = 1); far at top (0).
        y_norm = _np.arange(self.h, dtype=_np.float32)[:, _np.newaxis] / self.h
        # y_norm: 0 = top (far), 1 = bottom (near)
        near_start  = 1.0 - near_fraction        # depth starts above this y_norm
        horiz_start = 1.0 - horizon_fraction      # full haze at and above this y_norm

        # depth_w = 0 in foreground, ramps linearly to 1 at horizon and beyond
        depth_w = _np.clip(
            (near_start - y_norm) / (near_start - horiz_start + 1e-9), 0.0, 1.0
        )
        depth_w = depth_w * _np.ones((self.h, self.w), dtype=_np.float32)

        # ── Desaturation toward grey ───────────────────────────────────────────
        lum = 0.299 * R + 0.587 * G + 0.114 * B
        desat_amount = depth_w * desaturation
        R = R + (lum - R) * desat_amount
        G = G + (lum - G) * desat_amount
        B = B + (lum - B) * desat_amount

        # ── Atmospheric lightening — lifts dark values at distance ────────────
        lighten_amount = depth_w * lightening
        R = R + (1.0 - R) * lighten_amount * (1.0 - R)
        G = G + (1.0 - G) * lighten_amount * (1.0 - G)
        B = B + (1.0 - B) * lighten_amount * (1.0 - B)

        # ── Haze colour overlay ───────────────────────────────────────────────
        hr, hg, hb = haze_color
        alpha = depth_w * haze_opacity
        if blend_mode == "screen":
            R = 1.0 - (1.0 - R) * (1.0 - hr * alpha)
            G = 1.0 - (1.0 - G) * (1.0 - hg * alpha)
            B = 1.0 - (1.0 - B) * (1.0 - hb * alpha)
        else:
            R = R + (hr - R) * alpha
            G = G + (hg - G) * alpha
            B = B + (hb - B) * alpha

        # ── Write back to ARGB32 surface (BGRA layout) ───────────────────────
        buf[:, :, 2] = _np.clip(R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"    Bruegel panorama pass complete (haze={haze_color})")

    # ─────────────────────────────────────────────────────────────────────────
    # zorn_tricolor_pass — Anders Zorn's warm limited-palette skin technique
    # ─────────────────────────────────────────────────────────────────────────

    def zorn_tricolor_pass(
            self,
            ochre_warmth:       float = 0.08,
            vermillion_accent:  float = 0.12,
            shadow_warmth:      float = 0.06,
            midtone_low:        float = 0.28,
            midtone_high:       float = 0.75,
            blend_opacity:      float = 0.40,
    ):
        """
        Simulates Anders Zorn's characteristic warm limited-palette skin technique.

        Zorn famously restricted himself to four pigments: yellow ochre, ivory black,
        vermillion, and lead white.  Because there is no blue, green, or purple in this
        set, all flesh rendering must be achieved through warm mixtures — the entire tonal
        range of skin is negotiated between ochre-light, ochre-dark, and vermillion accent.
        The result is a distinctive warmth that permeates every value: highlights are
        cream-ochre rather than cool silver; midtones are pure warm yellow-brown; shadows
        glow with warm ivory-black rather than receding into cool grey.

        This pass imposes that quality on the current canvas by shifting three tonal zones:

        1. **Shadow zone** (luminance < ``midtone_low``): a gentle warm brown cast is
           applied — replicating the warmth of ivory black as opposed to the cool blue-grey
           of lamp black or carbon black.  Dark areas gain a subtle amber-brown undertone
           without lightening.

        2. **Midtone zone** (``midtone_low`` ≤ lum ≤ ``midtone_high``): the largest tonal
           zone is shifted toward Zorn's yellow ochre (0.82, 0.62, 0.18).  The strength is
           proportional to how close each pixel is to the mid-point of the range, so the
           effect peaks at the exact midtone and fades smoothly toward both the light and
           shadow boundaries.  This gives skin its characteristic warm amber quality at
           the form-turning transitions.

        3. **Warm-accent zone** (pixels where red channel dominates and saturation is
           high): the vermillion accent boost increases the saturation of already-warm
           reddish pixels — targeting the lips, cheekbone flush, ear helices, and nostril
           wings where Zorn typically placed his brightest red.  This is achieved by a
           small positive red-channel bias that does NOT lighten the pixel overall.

        All three effects are modulated by ``blend_opacity`` so the pass can be called
        multiple times at low opacity to build the effect gradually, mirroring Zorn's
        actual layering practice.

        The pass is tonal-structure-neutral: luminance is preserved throughout, so
        the tonal hierarchy established by ``build_form()`` is not disrupted — only the
        chromatic quality of each tonal zone is shifted.

        Call AFTER ``build_form()`` and BEFORE ``place_lights()``.  Follow with the
        warm amber ``glaze()`` at opacity 0.05–0.08 to unify the palette.

        Parameters
        ----------
        ochre_warmth       : Blend weight for the midtone ochre shift.
                             0.06–0.10 gives a subtle Zorn quality; 0.15+ is more pronounced.
        vermillion_accent  : Saturation boost for warm-red skin accents.
                             0.08–0.14 targets lips and cheeks without bleeding into neutrals.
        shadow_warmth      : Warm brown cast applied to dark areas.
                             0.04–0.08 replicates ivory black's warmth without lightening.
        midtone_low        : Lower luminance boundary of the midtone zone.
                             0.25–0.35 typical for flesh midtones.
        midtone_high       : Upper luminance boundary of the midtone zone.
                             0.70–0.80 typical (excludes near-white specular highlights).
        blend_opacity      : Global opacity of the pass.  0.35–0.50 for a single confident
                             pass; 0.20–0.30 when stacking multiple calls.

        Notes
        -----
        Inspired by: "Omnibus" (1895), "Hugo Lindqvist" (1895), "Dagmar" (1911).
        This session's random artistic improvement — the Zorn palette limitation as a
        computational painting pass.
        """
        import numpy as _np

        print(f"  Zorn tricolor pass  "
              f"(ochre={ochre_warmth:.2f}  vermillion={vermillion_accent:.2f}  "
              f"shadow={shadow_warmth:.2f}  opacity={blend_opacity:.2f})")

        # ── Read current canvas ARGB32 (BGRA byte order in pycairo) ──────────
        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        R = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Perceptual luminance ──────────────────────────────────────────────
        lum = 0.299 * R + 0.587 * G + 0.114 * B

        # ── Zone 1: Shadow warm cast — ivory-black warmth ────────────────────
        # Pixels below midtone_low receive a warm brown cast toward
        # (0.38, 0.28, 0.14) — the colour of ochre+ivory-black shadow.
        # The effect is strongest at lum=0 and fades linearly to zero at midtone_low.
        ivory_warm_r, ivory_warm_g, ivory_warm_b = 0.38, 0.28, 0.14
        shadow_t = _np.clip(1.0 - lum / (midtone_low + 1e-6), 0.0, 1.0)
        shadow_alpha = shadow_t * shadow_warmth * blend_opacity

        new_R = R + (ivory_warm_r - R) * shadow_alpha
        new_G = G + (ivory_warm_g - G) * shadow_alpha
        new_B = B + (ivory_warm_b - B) * shadow_alpha

        # ── Zone 2: Midtone ochre shift ───────────────────────────────────────
        # Pixels in [midtone_low, midtone_high] shift toward Zorn's yellow ochre
        # (0.82, 0.62, 0.18).  The effect is bell-shaped: maximum at the midpoint,
        # zero at both boundaries.
        ochre_r, ochre_g, ochre_b = 0.82, 0.62, 0.18
        mid_center = (midtone_low + midtone_high) * 0.5
        mid_half   = (midtone_high - midtone_low) * 0.5 + 1e-6
        # Raised cosine bell: 1 at the midpoint, 0 at the boundaries
        in_range   = ((lum >= midtone_low) & (lum <= midtone_high)).astype(_np.float32)
        bell       = (1.0 - _np.cos(_np.pi * (lum - midtone_low) / (midtone_high - midtone_low + 1e-6))) * 0.5
        mid_alpha  = bell * in_range * ochre_warmth * blend_opacity

        new_R = new_R + (ochre_r - new_R) * mid_alpha
        new_G = new_G + (ochre_g - new_G) * mid_alpha
        new_B = new_B + (ochre_b - new_B) * mid_alpha

        # ── Zone 3: Vermillion accent — warm-red saturation boost ────────────
        # Pixels where red dominates significantly over blue AND green
        # (i.e. already reddish skin accents) receive a small red channel boost.
        # This does not lighten the pixel — only the hue shifts warmer.
        warm_red_mask = (
            (R > G + 0.08) &
            (R > B + 0.14) &
            (lum >= midtone_low * 0.8) &
            (lum <= midtone_high)
        ).astype(_np.float32)
        # Boost red, desaturate blue slightly to keep luminance stable
        red_boost   = warm_red_mask * vermillion_accent * blend_opacity
        new_R = _np.clip(new_R + red_boost * 0.5, 0.0, 1.0)
        new_B = _np.clip(new_B - red_boost * 0.2, 0.0, 1.0)

        # ── Luminance preservation: tonal structure must not be altered ───────
        new_lum = 0.299 * new_R + 0.587 * new_G + 0.114 * new_B
        safe    = _np.where(new_lum > 1e-6, lum / new_lum, 1.0)
        new_R   = _np.clip(new_R * safe, 0.0, 1.0)
        new_G   = _np.clip(new_G * safe, 0.0, 1.0)
        new_B   = _np.clip(new_B * safe, 0.0, 1.0)

        # ── Write back to ARGB32 surface (BGRA layout) ───────────────────────
        buf[:, :, 0] = _np.clip(new_B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 2] = _np.clip(new_R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"    Zorn tricolor pass complete")

    # ─────────────────────────────────────────────────────────────────────────
    # morisot_plein_air_pass — Berthe Morisot's high-key impressionist light
    # ─────────────────────────────────────────────────────────────────────────

    def morisot_plein_air_pass(
            self,
            shadow_violet:      Color = (0.72, 0.68, 0.90),  # blue-violet shadow target
            luminosity_lift:    float = 0.10,                 # shadow brightness boost
            shadow_threshold:   float = 0.42,                 # lum below = shadow zone
            highlight_cream:    Color = (0.96, 0.93, 0.86),  # warm cream for highlights
            highlight_threshold: float = 0.76,                # lum above = highlight zone
            chroma_strength:    float = 0.18,                 # shadow hue-shift strength
            blend_opacity:      float = 0.45,
    ):
        """
        Simulates Berthe Morisot's characteristic high-key impressionist technique.

        Morisot's paintings share two defining qualities that distinguish her from her
        contemporaries: **colored shadows** and **elevated luminosity range**.  Where
        Rembrandt's shadows are warm umber, Zorn's are warm ivory-black, and Caravaggio's
        are pure void, Morisot's shadows are blue-violet or lavender — chromatic passages
        that contain as much color as the lights, only cooler.  This keeps her tonal range
        compressed into the upper half of the luminance scale, giving every canvas an
        airy, light-filled quality regardless of subject matter.

        This pass imposes that quality through two simultaneous corrections:

        1. **Shadow chroma correction** (luminance < ``shadow_threshold``):
           Dark areas are shifted toward ``shadow_violet`` — a blue-violet color
           that replicates the cool reflected sky light Morisot perceived in outdoor
           and north-lit interior settings.  The shift is proportional to how dark the
           pixel is, so the deepest shadows receive the strongest hue rotation while
           midtones blend smoothly out.  Luminance is also gently lifted by
           ``luminosity_lift`` to keep her characteristic high-key quality.

        2. **Highlight cream tint** (luminance > ``highlight_threshold``):
           The brightest areas receive a subtle warm cream bias — Morisot's highlights
           are never a brilliant blue-white but rather a luminous warm ivory, consistent
           with diffuse northern daylight reflecting off pale skin and white fabric.

        Both corrections are gated by ``blend_opacity`` so the pass can be called
        at lower strength multiple times, mirroring her layered wet-into-wet method.

        The pass is luminance-structure-neutral: unlike a simple colorize operation,
        the shadow shift targets only the chromatic component — the tonal hierarchy
        established by ``build_form()`` is preserved; only the color of each tonal
        zone is moved toward Morisot's characteristic palette.

        Call AFTER ``build_form()`` and BEFORE ``place_lights()``.  No final glaze
        is needed — Morisot's surface should remain fresh, not unified by a warm film.

        Parameters
        ----------
        shadow_violet      : RGB target color for the shadow zone.
                             Default (0.72, 0.68, 0.90) is a muted blue-violet.
                             Shift toward (0.60, 0.60, 0.92) for cooler, bluer shadows.
        luminosity_lift    : How much to lift shadow luminance toward the midtones.
                             0.06–0.12 gives Morisot's characteristic high-key quality.
                             0.0 shifts hue only without brightening.
        shadow_threshold   : Luminance boundary separating shadow from midtone zones.
                             0.38–0.45 typical for impressionist shadow treatment.
        highlight_cream    : RGB target color for the highlight zone.
                             Default (0.96, 0.93, 0.86) is warm ivory — not blue-white.
        highlight_threshold: Luminance above which the cream tint is applied.
                             0.72–0.80 avoids touching midtones.
        chroma_strength    : Blend weight for the shadow-to-violet hue shift.
                             0.12–0.22 gives visible but tasteful color in shadows.
        blend_opacity      : Global opacity of the entire pass.  0.40–0.55 for a single
                             confident pass; 0.20–0.30 when stacking multiple calls.

        Notes
        -----
        Inspired by: "The Cradle" (1872), "Summer's Day" (1879),
        "Woman at Her Toilette" (1879), "The Harbor at Lorient" (1869).
        This session's random artistic improvement — Morisot's colorful-shadow
        approach as a computational painting pass.
        """
        import numpy as _np

        print(f"  Morisot plein-air pass  "
              f"(chroma={chroma_strength:.2f}  lift={luminosity_lift:.2f}  "
              f"opacity={blend_opacity:.2f})")

        # ── Read current canvas ARGB32 (BGRA byte order in pycairo) ──────────
        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        R = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Perceptual luminance ──────────────────────────────────────────────
        lum = 0.299 * R + 0.587 * G + 0.114 * B

        # ── Zone 1: Shadow chroma shift toward blue-violet ───────────────────
        # Dark pixels (lum < shadow_threshold) are blended toward shadow_violet.
        # The blend weight is highest at lum=0 and fades to 0 at shadow_threshold.
        sv_r, sv_g, sv_b = shadow_violet
        shadow_t = _np.clip(1.0 - lum / (shadow_threshold + 1e-6), 0.0, 1.0)
        # Smoothstep: slow start, fast middle, slow end — avoids hard boundary
        shadow_t = shadow_t * shadow_t * (3.0 - 2.0 * shadow_t)
        shadow_alpha = shadow_t * chroma_strength * blend_opacity

        new_R = R + (sv_r - R) * shadow_alpha
        new_G = G + (sv_g - G) * shadow_alpha
        new_B = B + (sv_b - B) * shadow_alpha

        # ── Luminosity lift in shadow zone ────────────────────────────────────
        # Gently raise shadow luminance toward midtone — Morisot's shadows are
        # never the near-black void of Caravaggio or Rembrandt.
        if luminosity_lift > 0.0:
            lift_alpha = shadow_t * luminosity_lift * blend_opacity
            new_R = _np.clip(new_R + lift_alpha, 0.0, 1.0)
            new_G = _np.clip(new_G + lift_alpha, 0.0, 1.0)
            new_B = _np.clip(new_B + lift_alpha, 0.0, 1.0)

        # ── Zone 2: Highlight cream tint ──────────────────────────────────────
        # Bright areas (lum > highlight_threshold) receive a subtle warm cream bias.
        # Morisot's highlights read as warm ivory, not brilliant cool white.
        hc_r, hc_g, hc_b = highlight_cream
        hi_t = _np.clip(
            (lum - highlight_threshold) / (1.0 - highlight_threshold + 1e-6),
            0.0, 1.0,
        )
        hi_t = hi_t * hi_t  # quadratic ease — effect strongest at peak luminance
        hi_alpha = hi_t * 0.30 * blend_opacity  # cream tint is subtle; never overwhelm

        new_R = _np.clip(new_R + (hc_r - new_R) * hi_alpha, 0.0, 1.0)
        new_G = _np.clip(new_G + (hc_g - new_G) * hi_alpha, 0.0, 1.0)
        new_B = _np.clip(new_B + (hc_b - new_B) * hi_alpha, 0.0, 1.0)

        # ── Write back to ARGB32 surface (BGRA layout) ───────────────────────
        buf[:, :, 0] = _np.clip(new_B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 2] = _np.clip(new_R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"    Morisot plein-air pass complete")
