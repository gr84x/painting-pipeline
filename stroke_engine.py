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
                          reference:      Union[np.ndarray, Image.Image],
                          n_veils:        int   = 7,
                          blur_radius:    float = 12.0,
                          warmth:         float = 0.35,
                          veil_opacity:   float = 0.08,
                          edge_only:      bool  = True,
                          chroma_dampen:  float = 0.18,
                          depth_gradient: float = 0.0):
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
        depth_gradient : When > 0, intensifies the sfumato effect toward the
                         upper portion of the canvas (the distant background), and
                         reduces it toward the lower foreground.  This matches
                         Leonardo's actual technique: the landscape behind the Mona
                         Lisa — the rocky terrain and winding road that recede into
                         the far distance — is significantly more hazed than the
                         figure in the foreground.  The sfumato effect exists along
                         a vertical gradient of atmospheric depth, not uniformly.
                         At ``depth_gradient=1.0`` the top of the canvas receives
                         full veil_opacity while the bottom receives ~20% — a strong
                         but naturalistic atmospheric recession.  At 0.0 (default)
                         the behaviour is unchanged from prior sessions.

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

        The ``depth_gradient`` improvement (session 54): prior sessions applied
        sfumato uniformly across the canvas, which missed Leonardo's spatial
        logic — near-foreground forms are less hazed than distant ones.  The
        gradient weight corrects this by modulating veil opacity per-row.
        """
        print(f"Sfumato veil pass  ({n_veils} veils  blur={blur_radius:.1f}px"
              f"  warmth={warmth:.2f}  chroma_dampen={chroma_dampen:.2f}"
              f"  depth_gradient={depth_gradient:.2f})…")

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

        # ── Depth gradient weight (session 54 improvement) ───────────────────────
        # Build a (H, 1) vertical weight map: rows near the top (background /
        # distant landscape) receive more sfumato; rows near the bottom
        # (foreground) receive less.  This matches Leonardo's spatial logic:
        # the far landscape behind the Mona Lisa is far more hazed than the
        # figure in the foreground.  depth_gradient=0 disables this (uniform).
        if depth_gradient > 0.0:
            # ys: 1.0 at the top row (row 0), fading toward a minimum of
            # (1 - depth_gradient) at the bottom row.
            ys = np.linspace(1.0, 1.0 - depth_gradient, h, dtype=np.float32)
            depth_w = np.clip(ys, 0.01, 1.0)[:, np.newaxis]  # (H, 1)
        else:
            depth_w = 1.0   # scalar broadcast — no per-row adjustment

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

            # Composite: only where edge_mask is active; modulate by depth gradient
            # so distant (upper) regions receive stronger sfumato.
            alpha = edge_mask * veil_opacity * depth_w  # (H, W) float

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
    # piero_crystalline_pass — Piero della Francesca's cool mineral light
    # ─────────────────────────────────────────────────────────────────────────

    def piero_crystalline_pass(
            self,
            shadow_stone:        Color = (0.44, 0.46, 0.50),  # cool stone-grey shadow target
            highlight_silver:    Color = (0.93, 0.94, 0.96),  # cool silver-white highlight target
            shadow_threshold:    float = 0.42,                 # lum below = shadow zone
            highlight_threshold: float = 0.70,                 # lum above = highlight zone
            shadow_strength:     float = 0.22,                 # shadow shift blend weight
            highlight_strength:  float = 0.16,                 # highlight shift blend weight
            chroma_dampen:       float = 0.08,                 # midtone desaturation strength
            blend_opacity:       float = 0.45,
    ):
        """
        Simulates Piero della Francesca's characteristic cool, crystalline light.

        Piero's surfaces have a quality unlike any other painter of his era: the light
        that falls on his figures is diffuse, sourceless, and mineral — as if his
        subjects were carved from pale stone and placed under an even, cloudless sky.
        Where Leonardo dissolved edges in amber sfumato and Titian warmed flesh with
        golden glazes, Piero's illumination is cool and resolved.  Shadows drift toward
        pale stone-grey rather than warm umber; highlights are silver-white rather than
        cream; and the midtones carry a gentle desaturation that gives every surface a
        geometric, fresco-like austerity.

        This pass imposes that quality through three simultaneous corrections:

        1. **Shadow cooldown** (luminance < ``shadow_threshold``):
           Dark areas are shifted toward ``shadow_stone`` — a cool stone-grey that
           replicates the pale, unsentimental shadow quality visible in the Flagellation
           and the Resurrection.  Unlike Rembrandt or Caravaggio, Piero never lets a
           shadow become warm umber or dramatic near-black; his shadows are resolutely
           cool and contained.  The blend weight is highest at the darkest pixels and
           fades smoothly to zero at the threshold boundary.

        2. **Highlight silver tint** (luminance > ``highlight_threshold``):
           Bright areas receive a cool silver-white bias.  This is the opposite of
           Leonardo's amber highlight tint and Zorn's ivory-warm brightest mark: Piero's
           highest lights read as luminous pale stone — cool, not golden.

        3. **Midtone chroma dampen** (``shadow_threshold`` < lum < ``highlight_threshold``):
           Midtone pixels are gently blended toward their own luminance grey, reducing
           saturation in the mid-range.  This replicates the restrained, mineral palette
           of Piero's fresco work — colours in the midtone zone are present but muted,
           never the full saturation of a Venetian master.  The effect is proportional
           to distance from the shadow and highlight zones: pixels squarely in the
           midrange receive the strongest desaturation; pixels near the zone boundaries
           receive progressively less.

        Together these three corrections shift any base painting toward Piero's cool,
        geometric, crystalline aesthetic without altering the fundamental tonal structure
        established by ``build_form()``.

        Call AFTER ``build_form()`` and BEFORE ``place_lights()``.  Do NOT follow
        with ``sfumato_veil_pass()`` — Piero's edges are clear and resolved, not
        dissolved into atmospheric smoke.

        Parameters
        ----------
        shadow_stone        : RGB target for the shadow zone.
                              Default (0.44, 0.46, 0.50) is a cool neutral stone-grey.
                              Shift toward (0.38, 0.40, 0.46) for deeper, cooler shadows.
        highlight_silver    : RGB target for the highlight zone.
                              Default (0.93, 0.94, 0.96) is a pale cool silver-white.
                              Shift toward (0.88, 0.90, 0.94) for a slightly warmer silver.
        shadow_threshold    : Luminance boundary below which shadow cooldown engages.
                              0.38–0.45 covers deep shadows without touching midtones.
        highlight_threshold : Luminance boundary above which silver tint engages.
                              0.66–0.74 covers highlights without touching midtones.
        shadow_strength     : Blend weight for the shadow-to-stone-grey shift.
                              0.18–0.28 gives visible cool shadow without deadening form.
        highlight_strength  : Blend weight for the highlight-to-silver shift.
                              0.12–0.22 gives cool highlights without washing the form.
        chroma_dampen       : Strength of midtone desaturation.
                              0.06–0.12 gives Piero's characteristic muted midtone palette.
                              0.0 disables midtone desaturation entirely.
        blend_opacity       : Global opacity of the entire pass.  0.40–0.55 for a single
                              confident pass; 0.25–0.35 when stacking multiple calls.

        Notes
        -----
        Inspired by: "The Flagellation of Christ" (c. 1455),
        "The Resurrection" (c. 1463), "The Baptism of Christ" (c. 1448),
        "Portrait of Federico da Montefeltro" (c. 1472).
        This session's new artist addition — Piero della Francesca's cool mineral
        quality as a computational painting pass.
        """
        import numpy as _np

        print(f"  Piero crystalline pass  "
              f"(shadow={shadow_strength:.2f}  highlight={highlight_strength:.2f}  "
              f"chroma_dampen={chroma_dampen:.3f}  opacity={blend_opacity:.2f})")

        # ── Read current canvas ARGB32 (BGRA byte order in pycairo) ──────────
        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        R = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Perceptual luminance ──────────────────────────────────────────────
        lum = 0.299 * R + 0.587 * G + 0.114 * B

        # ── Zone 1: Shadow cooldown toward stone-grey ─────────────────────────
        # Dark pixels (lum < shadow_threshold) blend toward shadow_stone.
        # Smoothstep weighting: highest blend at lum=0, fades to zero at threshold.
        ss_r, ss_g, ss_b = shadow_stone
        shadow_t = _np.clip(1.0 - lum / (shadow_threshold + 1e-6), 0.0, 1.0)
        shadow_t = shadow_t * shadow_t * (3.0 - 2.0 * shadow_t)  # smoothstep
        shadow_alpha = shadow_t * shadow_strength * blend_opacity

        new_R = R + (ss_r - R) * shadow_alpha
        new_G = G + (ss_g - G) * shadow_alpha
        new_B = B + (ss_b - B) * shadow_alpha

        # ── Zone 2: Highlight silver tint ─────────────────────────────────────
        # Bright pixels (lum > highlight_threshold) blend toward highlight_silver.
        # Quadratic ease: effect strongest at peak luminance, fades toward threshold.
        hs_r, hs_g, hs_b = highlight_silver
        hi_t = _np.clip(
            (lum - highlight_threshold) / (1.0 - highlight_threshold + 1e-6),
            0.0, 1.0,
        )
        hi_t = hi_t * hi_t  # quadratic: strongest at peak brightness
        hi_alpha = hi_t * highlight_strength * blend_opacity

        new_R = _np.clip(new_R + (hs_r - new_R) * hi_alpha, 0.0, 1.0)
        new_G = _np.clip(new_G + (hs_g - new_G) * hi_alpha, 0.0, 1.0)
        new_B = _np.clip(new_B + (hs_b - new_B) * hi_alpha, 0.0, 1.0)

        # ── Zone 3: Midtone chroma dampen ─────────────────────────────────────
        # Pixels in the midtone range (shadow_threshold < lum < highlight_threshold)
        # are gently blended toward their own luminance grey.  This replicates
        # Piero's restrained midtone palette — colours are present but never saturated.
        if chroma_dampen > 0.0:
            # Midtone weight: highest at centre of midrange, zero at both zone edges.
            mid_low    = shadow_threshold
            mid_high   = highlight_threshold
            mid_centre = 0.5 * (mid_low + mid_high)
            mid_half   = 0.5 * (mid_high - mid_low) + 1e-6
            mid_t = _np.clip(1.0 - _np.abs(lum - mid_centre) / mid_half, 0.0, 1.0)
            mid_t = mid_t * mid_t  # quadratic — softer ramp into the midzone

            chroma_alpha = mid_t * chroma_dampen * blend_opacity
            new_lum = 0.299 * new_R + 0.587 * new_G + 0.114 * new_B
            new_R = _np.clip(new_R + (new_lum - new_R) * chroma_alpha, 0.0, 1.0)
            new_G = _np.clip(new_G + (new_lum - new_G) * chroma_alpha, 0.0, 1.0)
            new_B = _np.clip(new_B + (new_lum - new_B) * chroma_alpha, 0.0, 1.0)

        # ── Write back to ARGB32 surface (BGRA layout) ───────────────────────
        buf[:, :, 0] = _np.clip(new_B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 2] = _np.clip(new_R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"    Piero crystalline pass complete")

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

    # ──────────────────────────────────────────────────────────────────────────
    # Degas pastel pass
    # ──────────────────────────────────────────────────────────────────────────

    def degas_pastel_pass(
            self,
            shadow_grey:        Color = (0.30, 0.30, 0.42),  # deep blue-grey shadow target
            light_amber:        Color = (0.88, 0.72, 0.54),  # warm amber-orange highlight target
            shadow_threshold:   float = 0.40,                 # lum below = shadow zone
            light_threshold:    float = 0.68,                 # lum above = light zone
            shadow_strength:    float = 0.22,                 # shadow cooldown blend weight
            light_strength:     float = 0.18,                 # highlight warmup blend weight
            pastel_grain:       float = 0.04,                 # fine-grain pastel surface noise
            blend_opacity:      float = 0.50,
    ):
        """
        Simulates Edgar Degas' characteristic pastel-over-monotype technique.

        Degas built his pastels on a dark monotype ground — an oil-ink print pulled from
        a plate, leaving a tonal image with strong dark passages.  Onto that base he
        applied successive layers of pastel in directional hatching, each layer at a
        different angle, creating a surface where colours optically mix rather than
        physically blend.  The result is simultaneously structural (the monotype
        drawing holds the form) and colouristic (the pastel strokes create vibrating
        simultaneous contrast).

        This pass models that duality through three simultaneous operations:

        1. **Shadow cooldown** (luminance < ``shadow_threshold``):
           Dark areas are shifted toward ``shadow_grey`` — a deep blue-grey that
           replicates the cooled, inky darkness of the monotype ground showing through
           sparse pastel coverage.  The blend is luminance-weighted: the darkest pixels
           receive the strongest shift; the transition out of shadow is smooth.

        2. **Highlight warmup** (luminance > ``light_threshold``):
           Bright areas receive a warm amber-orange bias.  Degas' lit flesh in his ballet
           pictures is never a clean white but a warm, slightly dusty amber — the warmth
           of stage gaslight filtered through pale skin and gauze.

        3. **Pastel grain** (applied globally at low weight):
           A fine per-pixel luminance noise is added to simulate the physical texture of
           pastel pigment sitting in the tooth of the paper without fully filling it.
           Unlike photographic film grain (which is additive), pastel grain is
           bidirectional — some pixels lighten slightly, others darken — giving the
           surface a characteristic soft granularity rather than a smooth photographic
           finish.

        Together these three corrections shift any base painting toward Degas' cool-dark,
        warm-light, grain-surfaced aesthetic without altering the fundamental tonal
        structure established by ``build_form()``.

        Call AFTER ``build_form()`` and BEFORE ``place_lights()``.  The pass pairs well
        with ``dry_granulation_pass()`` for additional surface texture depth.

        Parameters
        ----------
        shadow_grey       : RGB target for the shadow zone.
                            Default (0.30, 0.30, 0.42) is a deep indigo-blue-grey.
                            Shift toward (0.22, 0.22, 0.30) for deeper, denser shadows.
        light_amber       : RGB target for the highlight zone.
                            Default (0.88, 0.72, 0.54) is a warm amber-orange.
                            Shift toward (0.96, 0.80, 0.60) for warmer stage-light effect.
        shadow_threshold  : Luminance boundary below which shadow cooldown engages.
                            0.36–0.44 covers deep shadow without touching midtones.
        light_threshold   : Luminance boundary above which highlight warmup engages.
                            0.64–0.72 covers highlights without touching midtones.
        shadow_strength   : Blend weight for the shadow-to-grey shift.
                            0.18–0.28 gives visible cool shadow without deadening the form.
        light_strength    : Blend weight for the highlight-to-amber shift.
                            0.14–0.24 gives warm highlights without over-saturating.
        pastel_grain      : Amplitude of the bidirectional per-pixel luminance noise.
                            0.03–0.06 gives Degas' characteristic soft-tooth surface.
                            0.0 disables grain entirely.
        blend_opacity     : Global opacity of the entire pass.  0.45–0.60 for a single
                            confident pass; 0.25–0.35 when stacking multiple calls.

        Notes
        -----
        Inspired by: "The Dance Class" (1874), "L'Absinthe" (1876),
        "Woman Bathing in a Shallow Tub" (1886), "Dancers in Blue" (1890).
        This session's new artist addition — Degas' pastel-over-monotype approach
        as a computational painting pass.
        """
        import numpy as _np

        print(f"  Degas pastel pass  "
              f"(shadow={shadow_strength:.2f}  light={light_strength:.2f}  "
              f"grain={pastel_grain:.3f}  opacity={blend_opacity:.2f})")

        # ── Read current canvas ARGB32 (BGRA byte order in pycairo) ──────────
        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        R = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Perceptual luminance ──────────────────────────────────────────────
        lum = 0.299 * R + 0.587 * G + 0.114 * B

        # ── Zone 1: Shadow cooldown toward blue-grey ─────────────────────────
        # Pixels darker than shadow_threshold shift toward shadow_grey.
        # Blend weight is highest at the darkest pixels and fades smoothly to zero
        # at the threshold boundary — no hard seam between shadow and midtone.
        sg_r, sg_g, sg_b = shadow_grey
        shadow_t = _np.clip(1.0 - lum / (shadow_threshold + 1e-6), 0.0, 1.0)
        # Smoothstep: prevents hard tonal boundary at the shadow/midtone transition
        shadow_t = shadow_t * shadow_t * (3.0 - 2.0 * shadow_t)
        shadow_alpha = shadow_t * shadow_strength * blend_opacity

        new_R = R + (sg_r - R) * shadow_alpha
        new_G = G + (sg_g - G) * shadow_alpha
        new_B = B + (sg_b - B) * shadow_alpha

        # ── Zone 2: Highlight warmup toward amber-orange ─────────────────────
        # Bright pixels (lum > light_threshold) blend toward light_amber.
        # Quadratic ease — strongest effect at peak luminance, fades toward threshold.
        la_r, la_g, la_b = light_amber
        light_t = _np.clip(
            (lum - light_threshold) / (1.0 - light_threshold + 1e-6),
            0.0, 1.0,
        )
        light_t = light_t * light_t  # quadratic: effect strongest at peak brightness
        light_alpha = light_t * light_strength * blend_opacity

        new_R = _np.clip(new_R + (la_r - new_R) * light_alpha, 0.0, 1.0)
        new_G = _np.clip(new_G + (la_g - new_G) * light_alpha, 0.0, 1.0)
        new_B = _np.clip(new_B + (la_b - new_B) * light_alpha, 0.0, 1.0)

        # ── Zone 3: Pastel grain — bidirectional luminance noise ──────────────
        # Simulates the physical texture of dry pastel pigment resting in the paper
        # tooth.  Unlike additive film grain, pastel grain is bidirectional: some
        # micro-areas receive more pigment (darker), some less (lighter).  The result
        # is a soft granularity rather than a smooth photographic surface.
        if pastel_grain > 0.0:
            rng = _np.random.default_rng(seed=42)  # deterministic for reproducibility
            grain = rng.uniform(-pastel_grain, pastel_grain,
                                size=(self.h, self.w)).astype(_np.float32)
            grain_alpha = blend_opacity * 0.60  # grain is applied at reduced opacity
            new_R = _np.clip(new_R + grain * grain_alpha, 0.0, 1.0)
            new_G = _np.clip(new_G + grain * grain_alpha, 0.0, 1.0)
            new_B = _np.clip(new_B + grain * grain_alpha, 0.0, 1.0)

        # ── Write back to ARGB32 surface (BGRA layout) ───────────────────────
        buf[:, :, 0] = _np.clip(new_B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 2] = _np.clip(new_R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"    Degas pastel pass complete")

    # ─────────────────────────────────────────────────────────────────────────
    # waterhouse_jewel_pass — Pre-Raphaelite wet-white-ground jewel saturation
    #
    # This is this session's random artistic improvement: simulating the unique
    # luminosity that results from the Pre-Raphaelite wet white ground method.
    # Unlike any prior pass, it operates by lifting midtone SATURATION selectively
    # (not luminance, not hue) in the zone where jewel colours live.  The white
    # ground reflects back through the paint, making colours appear more saturated
    # than they would on a dark or mid-tone priming.
    # ─────────────────────────────────────────────────────────────────────────

    def waterhouse_jewel_pass(
            self,
            jewel_boost:        float = 0.14,
            jewel_low:          float = 0.20,
            jewel_high:         float = 0.62,
            shadow_cool:        float = 0.10,
            shadow_threshold:   float = 0.32,
            shadow_width:       float = 0.12,
            highlight_warmth:   float = 0.06,
            highlight_threshold: float = 0.78,
            blend_opacity:      float = 0.45,
    ):
        """
        Simulates John William Waterhouse's Pre-Raphaelite wet white ground technique.

        The Pre-Raphaelite Brotherhood (and Waterhouse as their foremost late
        successor) applied paint onto a STILL-WET white lead priming.  This "wet
        white ground" method has a profound effect on colour:

        1. **Midtone jewel saturation** — Paint applied thinly or transparently over
           a wet white ground reads at higher saturation than the same paint on a
           toned or dark ground, because the white substrate reflects light back
           through the paint film rather than absorbing it.  This is the source of
           the characteristic jewel quality of Pre-Raphaelite colours — the sapphire
           blues, deep crimsons, and rich viridians of Waterhouse, Millais, and
           Holman Hunt glow from within.  The effect is strongest in the midtone
           range (lum 0.20–0.62) where pigments are applied in one or two thin layers
           rather than the thick impasto of the highlights.

        2. **Cool shadow passages** — Where the paint is thinnest (deep shadows, the
           penumbra between lit and unlit), the cool white ground shows through as a
           pale lavender-grey tint.  Waterhouse's shadow flesh has this quality:
           the halftone cools toward blue-grey before darkening, rather than shifting
           toward warm umber as it would on a mid-tone ground.

        3. **Warm ivory highlights** — The lit passages receive confident loaded-brush
           strokes that fully cover the ground; these are warm ivory (the natural
           mixing of white and ochre flesh pigment) rather than cool.  A gentle
           warmth pass in the highlight zone reinforces this.

        The pass imposes all three effects on the current canvas without disrupting
        the tonal structure established by ``build_form()``.

        This method is this session's **random artistic improvement**: no prior pass
        in the pipeline targeted midtone saturation independently of luminance or hue.
        All earlier chromatic adjustments (``zorn_tricolor_pass``, ``morisot_plein_air_pass``,
        ``degas_pastel_pass``) shifted *hue* or *luminance*; this is the first to lift
        *chroma* directly in HSV space within a luminance window — a technique applicable
        to any artist pipeline that benefits from increased colour richness.

        Parameters
        ----------
        jewel_boost        : Saturation increase in the jewel zone (0–0.30).
                             0.10–0.18 replicates Pre-Raphaelite richness without
                             artificiality; above 0.25 reads as oversaturated.
        jewel_low          : Lower luminance boundary of the jewel (midtone) zone.
                             0.18–0.25 is appropriate — below this, paint is too thick
                             to show white ground influence.
        jewel_high         : Upper luminance boundary of the jewel zone.
                             0.58–0.68 — above this, the highlight strokes are opaque
                             loaded paint (full cover) and the ground plays no role.
        shadow_cool        : Strength of the blue-grey cool shift in deep shadows.
                             0.08–0.14 recreates the lavender quality of Waterhouse's
                             shadow flesh without making the darks look cold.
        shadow_threshold   : Luminance below which shadow cooling is applied.
                             0.28–0.36 targets deep shadow without touching midtones.
        shadow_width       : Width of the smooth ramp from shadow to neutral.
                             0.10–0.16 creates a gentle transition without a hard seam.
        highlight_warmth   : Warm ivory tint applied to high-luminance pixels.
                             0.04–0.08 — the white-ground loaded strokes are warm,
                             not neutral; this reinforces that quality.
        highlight_threshold: Luminance above which warmth is applied (0.75–0.82).
        blend_opacity      : Global blend weight for all three effects.
                             0.40–0.55 for a full confident pass; 0.25–0.35 when
                             used on top of a non-white ground for a gentler effect.

        Notes
        -----
        Inspired by: "The Lady of Shalott" (1888, Tate), "Hylas and the Nymphs"
        (1896, Manchester), "Ophelia" (1894).
        Primary reference: Joyce Townsend, Tate Conservation, on Pre-Raphaelite
        wet white ground priming technique (Tate Papers, 2004).
        This session's random artistic improvement — midtone chroma lifting as an
        independent pipeline pass applicable across all white-ground painting styles.
        """
        import numpy as _np
        import colorsys as _cs

        print(f"  Waterhouse jewel pass  "
              f"(jewel_boost={jewel_boost:.2f}  shadow_cool={shadow_cool:.2f}  "
              f"highlight_warmth={highlight_warmth:.2f}  opacity={blend_opacity:.2f})")

        # ── Read current canvas ARGB32 (BGRA byte order in pycairo) ──────────
        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        R = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Perceptual luminance ──────────────────────────────────────────────
        lum = 0.299 * R + 0.587 * G + 0.114 * B

        # Pre-allocate output arrays (modified in-place per zone)
        new_R = R.copy()
        new_G = G.copy()
        new_B = B.copy()

        # ── Zone 1: Jewel saturation boost in the midtone range ──────────────
        # The white ground reflects through thin-to-moderate paint application
        # (midtone luminance), boosting apparent saturation.  We operate in HSV:
        # convert each pixel, increase S by jewel_boost, clamp, convert back.
        #
        # The boost is weighted by how deep the pixel sits inside the jewel window:
        # 0 at the window edges, peak at the midpoint.  This gives a smooth
        # saturation gradient rather than a hard-edged mask.
        jewel_mid   = (jewel_low + jewel_high) * 0.5
        jewel_range = (jewel_high - jewel_low) * 0.5 + 1e-6
        jewel_t     = _np.clip(1.0 - _np.abs(lum - jewel_mid) / jewel_range, 0.0, 1.0)
        # Smoothstep for softer transitions
        jewel_t     = jewel_t * jewel_t * (3.0 - 2.0 * jewel_t)

        # For each pixel in the jewel zone, boost saturation in HSV space.
        # Vectorised HSV conversion: max/min per pixel.
        Cmax  = _np.maximum(_np.maximum(R, G), B)
        Cmin  = _np.minimum(_np.minimum(R, G), B)
        delta = Cmax - Cmin + 1e-9

        # HSV S (saturation) = delta / Cmax  (0 when Cmax=0)
        S = _np.where(Cmax > 1e-6, delta / Cmax, 0.0)

        # Boost S proportional to jewel_t and jewel_boost, clamped to [0, 1]
        S_new = _np.clip(S + jewel_t * jewel_boost * blend_opacity, 0.0, 1.0)
        S_boost_ratio = _np.where(S > 1e-6, S_new / S, 1.0)

        # Apply saturation boost: distance from grey (Cmax) is scaled.
        # grey_R = R where saturation = 0, i.e., R == G == B == Cmax (the grey axis).
        grey_R = Cmax
        grey_G = Cmax
        grey_B = Cmax
        new_R = _np.clip(grey_R + (R - grey_R) * S_boost_ratio, 0.0, 1.0)
        new_G = _np.clip(grey_G + (G - grey_G) * S_boost_ratio, 0.0, 1.0)
        new_B = _np.clip(grey_B + (B - grey_B) * S_boost_ratio, 0.0, 1.0)

        # ── Zone 2: Shadow cooling toward lavender-blue ───────────────────────
        # In the shadow zone the white ground shows through as a pale cool tint
        # (the lead white of the priming, visible through very thin paint).
        # Target: (0.72, 0.72, 0.86) — pale blue-grey lavender.
        sc_r, sc_g, sc_b = 0.72, 0.72, 0.86
        lo = shadow_threshold - shadow_width * 0.5
        hi = shadow_threshold + shadow_width * 0.5
        # Smooth ramp: 1.0 in deep shadow, 0.0 above the ramp
        shadow_t = _np.clip((hi - lum) / (hi - lo + 1e-6), 0.0, 1.0)
        shadow_t = shadow_t * shadow_t * (3.0 - 2.0 * shadow_t)  # smoothstep
        shadow_alpha = shadow_t * shadow_cool * blend_opacity

        new_R = _np.clip(new_R + (sc_r - new_R) * shadow_alpha, 0.0, 1.0)
        new_G = _np.clip(new_G + (sc_g - new_G) * shadow_alpha, 0.0, 1.0)
        new_B = _np.clip(new_B + (sc_b - new_B) * shadow_alpha, 0.0, 1.0)

        # ── Zone 3: Highlight warm ivory tint ────────────────────────────────
        # Loaded opaque highlight strokes are warm ivory on a white ground —
        # not cool (the white ground is not showing through thick paint here).
        # Target: (0.94, 0.88, 0.72) — warm ivory.
        hi_r, hi_g, hi_b = 0.94, 0.88, 0.72
        light_t = _np.clip(
            (lum - highlight_threshold) / (1.0 - highlight_threshold + 1e-6),
            0.0, 1.0,
        )
        light_t = light_t * light_t  # quadratic ease — strongest at peak brightness
        light_alpha = light_t * highlight_warmth * blend_opacity

        new_R = _np.clip(new_R + (hi_r - new_R) * light_alpha, 0.0, 1.0)
        new_G = _np.clip(new_G + (hi_g - new_G) * light_alpha, 0.0, 1.0)
        new_B = _np.clip(new_B + (hi_b - new_B) * light_alpha, 0.0, 1.0)

        # ── Write back to ARGB32 surface (BGRA layout) ───────────────────────
        buf[:, :, 0] = _np.clip(new_B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 2] = _np.clip(new_R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        tmp = cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"    Waterhouse jewel pass complete")

    # moreau_gilded_pass — Symbolist encrusted gold-point surface technique
    #
    # This is this session's random artistic improvement: stochastic gold-point
    # scattering to simulate Gustave Moreau's distinctive "encrusted" surface
    # quality.  Unlike every prior pass, which modifies pixel values globally
    # or within luminance bands, this pass uses a STOCHASTIC POINT-SCATTER
    # strategy: a population of small, bright gold fragments is placed at
    # randomly sampled positions within the target luminance range, blending
    # into the underlying colour.  This creates a mosaic-like, irregular texture
    # that reads as "encrusted" — paint laid on as jewel fragments rather than
    # brushed as continuous tone.
    # ─────────────────────────────────────────────────────────────────────────

    def moreau_gilded_pass(
            self,
            gold_density:       float = 0.018,
            gold_low:           float = 0.42,
            gold_high:          float = 0.88,
            crimson_shadow:     float = 0.12,
            shadow_threshold:   float = 0.28,
            gold_tint:          tuple = (0.92, 0.76, 0.22),
            blend_opacity:      float = 0.52,
    ):
        """
        Simulates Gustave Moreau's Symbolist encrusted-gold surface technique.

        Moreau's mythological canvases are unlike any other 19th-century oil
        paintings in their surface quality: they accumulate thousands of tiny
        touches of gold and jewel-coloured paint until the canvas surface reads
        as a Byzantine reliquary rather than a stretched linen support.  His
        method draws on medieval manuscript illumination and Byzantine mosaic
        as much as on the Western oil painting tradition.

        This pass replicates three distinct aspects of that technique:

        1. **Stochastic gold-point scattering** — The defining Moreau effect.
           A proportion (``gold_density``) of pixels within the midtone-to-
           highlight luminance window (``gold_low``–``gold_high``) are randomly
           selected and tinted toward the gold colour (``gold_tint``).  The
           random selection creates an irregular, fragmented appearance: each
           "gold fragment" is a single pixel or small cluster, simulating a
           tiny brushstroke of gold paint laid individually on the surface.
           This stochastic approach is the core innovation of this pass and
           distinguishes it from all prior passes in the pipeline, which modify
           pixels deterministically (globally, by luminance band, or via
           convolution).  Stochastic pixel sampling produces the irregular,
           hand-placed quality of Moreau's encrusted technique; it cannot be
           replicated by a smooth per-pixel function.

        2. **Crimson shadow enrichment** — Moreau's darks are never dead black.
           The dark warm umber-crimson ground glows through thin shadow passages,
           giving his interiors a ruby warmth.  Pixels below ``shadow_threshold``
           are shifted toward a deep warm crimson, preventing the void
           backgrounds from reading as neutral or cool.

        3. **Warm gold atmospheric tint** — A gentle overall warm gold tint
           is blended across the full image at low opacity, simulating the
           characteristic amber-gold tonality of his varnished surfaces.  This
           is the atmospheric unifier of his palette and gives his paintings
           the feeling of being viewed through warm amber glass.

        Parameters
        ----------
        gold_density   : Fraction of eligible pixels receiving a gold touch.
                         0.010–0.025 replicates Moreau's density — enough to
                         read as "scattered" not "uniform"; above 0.035 the
                         effect starts to look like a solid gold overlay.
        gold_low       : Lower luminance boundary for gold scattering.
                         0.38–0.46 — gold fragments live in the upper-midtone
                         range where thin glaze over dark ground would catch
                         light without being the full highlight.
        gold_high      : Upper luminance boundary (0.82–0.92) — gold fragments
                         extend into the highlights but not the absolute peak
                         brightness, which Moreau reserved for near-white ivory.
        crimson_shadow : Strength of the warm crimson push in deep shadows.
                         0.08–0.16 — enough to warm the darks without making
                         them look like red paint (the ground glows through, it
                         does not dominate).
        shadow_threshold: Luminance below which shadow enrichment is applied.
                         0.22–0.32 — deep shadows only; midtones unaffected.
        gold_tint      : RGB tuple for the gold scatter colour (values 0–1).
                         (0.92, 0.76, 0.22) is burnished gold; (0.90, 0.82, 0.38)
                         is pale gold leaf; (0.88, 0.62, 0.12) is deep amber.
        blend_opacity  : Global blend weight for all three effects combined.
                         0.45–0.60 for a full-strength Moreau surface;
                         0.25–0.35 as a supplementary pass over another style.

        Notes
        -----
        Inspired by: "Salome Dancing Before Herod" (1876, Musée Gustave Moreau),
        "Jupiter and Semele" (1895, Musée Gustave Moreau), "The Apparition"
        (1876, Musée d'Orsay).
        Primary reference: Julius Kaplan, "The Art of Gustave Moreau: Theory,
        Style, and Content" (1982); Geneviève Lacambre, Musée Moreau catalogue.
        This session's random artistic improvement — stochastic pixel-scatter
        as a new pipeline primitive, enabling encrusted and mosaic surface
        effects not achievable by deterministic per-pixel transforms.
        """
        import numpy as _np

        print(f"  Moreau gilded pass  "
              f"(gold_density={gold_density:.3f}  crimson_shadow={crimson_shadow:.2f}  "
              f"blend_opacity={blend_opacity:.2f})")

        # ── Read current canvas ARGB32 (BGRA byte order in pycairo) ──────────
        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        R = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Perceptual luminance ──────────────────────────────────────────────
        lum = 0.299 * R + 0.587 * G + 0.114 * B

        new_R = R.copy()
        new_G = G.copy()
        new_B = B.copy()

        # ── Zone 1: Stochastic gold-point scattering ─────────────────────────
        # Identify pixels in the eligible luminance window.
        eligible = (lum >= gold_low) & (lum <= gold_high)
        eligible_indices = _np.argwhere(eligible)

        if eligible_indices.shape[0] > 0:
            # Sample a random subset of eligible pixels.
            rng = _np.random.default_rng(seed=42)   # deterministic seed for reproducibility
            n_total   = eligible_indices.shape[0]
            n_scatter = max(1, int(n_total * gold_density))
            chosen = rng.choice(n_total, size=n_scatter, replace=False)
            ys = eligible_indices[chosen, 0]
            xs = eligible_indices[chosen, 1]

            # Gold tint RGB components
            gt_r, gt_g, gt_b = float(gold_tint[0]), float(gold_tint[1]), float(gold_tint[2])

            # Blend each chosen pixel toward the gold tint at full blend_opacity.
            # (Each fragment is an individual "touch" — full-strength application
            # at that point, not a smooth global transition.)
            new_R[ys, xs] = _np.clip(
                new_R[ys, xs] * (1.0 - blend_opacity) + gt_r * blend_opacity, 0.0, 1.0)
            new_G[ys, xs] = _np.clip(
                new_G[ys, xs] * (1.0 - blend_opacity) + gt_g * blend_opacity, 0.0, 1.0)
            new_B[ys, xs] = _np.clip(
                new_B[ys, xs] * (1.0 - blend_opacity) + gt_b * blend_opacity, 0.0, 1.0)

        # ── Zone 2: Crimson shadow enrichment ────────────────────────────────
        # Warm the darkest pixels toward deep crimson — the ground glows through.
        # Target: (0.48, 0.10, 0.06) — deep warm crimson-ruby.
        cr_r, cr_g, cr_b = 0.48, 0.10, 0.06
        shadow_t = _np.clip(
            1.0 - (lum / (shadow_threshold + 1e-6)),
            0.0, 1.0,
        )
        shadow_t = shadow_t * shadow_t   # quadratic: strongest at absolute zero
        shadow_alpha = shadow_t * crimson_shadow * blend_opacity

        new_R = _np.clip(new_R + (cr_r - new_R) * shadow_alpha, 0.0, 1.0)
        new_G = _np.clip(new_G + (cr_g - new_G) * shadow_alpha, 0.0, 1.0)
        new_B = _np.clip(new_B + (cr_b - new_B) * shadow_alpha, 0.0, 1.0)

        # ── Zone 3: Warm gold atmospheric overall tint ───────────────────────
        # A gentle warm-gold atmospheric veil at very low opacity — simulates
        # the amber-varnish quality of Moreau's finished surfaces.
        # Applied as a global blend toward the gold tint at reduced strength.
        atm_strength = blend_opacity * 0.12   # 12 % of blend_opacity → subtle
        new_R = _np.clip(new_R + (float(gold_tint[0]) - new_R) * atm_strength, 0.0, 1.0)
        new_G = _np.clip(new_G + (float(gold_tint[1]) - new_G) * atm_strength, 0.0, 1.0)
        new_B = _np.clip(new_B + (float(gold_tint[2]) - new_B) * atm_strength, 0.0, 1.0)

        # ── Write back to ARGB32 surface (BGRA layout) ───────────────────────
        buf[:, :, 0] = _np.clip(new_B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 2] = _np.clip(new_R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        import cairo as _cairo
        tmp = _cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), _cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"    Moreau gilded pass complete  "
              f"(gold fragments placed: {n_scatter if eligible_indices.shape[0] > 0 else 0})")

    # ─────────────────────────────────────────────────────────────────────────
    # botticelli_linear_grace_pass — Florentine Renaissance tempera technique
    # ─────────────────────────────────────────────────────────────────────────

    def botticelli_linear_grace_pass(
            self,
            reference,
            hatch_density:   float = 0.022,
            hatch_length:    float = 12.0,
            hatch_opacity:   float = 0.55,
            gold_density:    float = 0.012,
            gold_tint:       tuple = (0.88, 0.72, 0.24),
            gold_opacity:    float = 0.70,
            luminosity_lift: float = 0.06,
    ):
        """
        Simulates Sandro Botticelli's Florentine tempera hatching technique.

        Botticelli's tempera-on-gesso method is the structural opposite of
        Leonardo's sfumato: form is built entirely through fine *parallel
        hatching* strokes laid from the contour inward, and through
        *chrysographic gold filaments* (fine shell-gold marks) scattered
        through hair, drapery highlights, and botanical detail.  No wet
        blending occurs — egg tempera dries in seconds.

        This pass replicates three distinct aspects of his technique:

        1. **Directional contour hatching** — Edge-gradient detection (Sobel)
           identifies the contour zones where Botticelli drew his defining
           lines.  Short parallel hatch-marks are drawn *along* the gradient
           direction at detected edges, simulating the fine parallel strokes
           he used to build tonal transitions in the absence of blending.
           Hatch marks are slightly darker than the local pixel, replicating
           the characteristic shadow-building of his tempera hatching.

        2. **Chrysographic gold filaments** — A stochastic scatter of bright
           gold-tinted marks in the upper-midtone to highlight luminance
           band replicates the shell-gold filaments he applied to hair, fabric
           folds, and botanical elements.  These are drawn as tiny horizontal
           dashes rather than single points, distinguishing them from the
           Moreau-style gold fragments (which are points).

        3. **Luminosity lift** — A global brightness boost simulates the pale
           white gesso ground showing through thin tempera washes.  Botticelli's
           panels glow with an internal light absent from dark-ground oil painting.
           The lift is applied as an additive blend toward white, strongest in the
           midtone and highlight zones where paint is thinnest.

        Parameters
        ----------
        reference      : PIL Image or ndarray — the reference to draw from.
        hatch_density  : Fraction of edge-zone pixels receiving hatch marks.
                         0.015–0.030: enough to read as fine hatching without
                         covering the underlying paint.
        hatch_length   : Length of each hatch mark in pixels (8–18).
                         Botticelli's marks were short, precise, and directional.
        hatch_opacity  : Opacity of hatch marks (0.35–0.70).
                         High enough to read as deliberate marks; low enough to
                         layer transparently like real tempera.
        gold_density   : Fraction of eligible midtone/highlight pixels receiving
                         a gold filament.  0.008–0.018 replicates the delicate
                         chrysographic density of his hair and drapery treatment.
        gold_tint      : RGB tuple for the chrysographic gold colour.
                         (0.88, 0.72, 0.24) is warm shell gold — slightly darker
                         and warmer than Moreau's burnished gold.
        gold_opacity   : Opacity of gold filaments (0.55–0.80).
        luminosity_lift: Global brightness additive for gesso-ground simulation.
                         0.04–0.08 is sufficient — the lift is subtle, not bleaching.

        Notes
        -----
        Inspired by: "Primavera" (c. 1477–82, Uffizi), "The Birth of Venus"
        (c. 1485, Uffizi), "Portrait of a Young Man" (c. 1480, National Gallery).
        Technical reference: Dunkerton, Foister, Gordon, Penny, "Giotto to
        Dürer: Early Renaissance Painting in the National Gallery" (1991);
        Skaug, "Punch Marks from Giotto to Fra Angelico" (1994).
        This session's randomly selected artistic improvement — sinuous contour
        hatching as a new pipeline primitive, enabling tempera and panel-painting
        surface effects not achievable by wet-blend or glaze-based passes.
        """
        import numpy as _np
        import cairo as _cairo
        from PIL import Image as _Img
        from scipy.ndimage import sobel as _sobel

        print(f"  Botticelli linear grace pass  "
              f"(hatch_density={hatch_density:.3f}  gold_density={gold_density:.3f}  "
              f"lift={luminosity_lift:.2f})")

        # ── Read reference and current canvas (BGRA) ─────────────────────────
        ref = self._prep(reference)
        rarr = ref[:, :, :3].astype(_np.float32) / 255.0   # (H, W, 3) RGB float

        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        R = buf[:, :, 2].astype(_np.float32) / 255.0

        # Perceptual luminance
        lum = 0.299 * R + 0.587 * G + 0.114 * B

        new_R = R.copy()
        new_G = G.copy()
        new_B = B.copy()

        # ── Zone 1: Directional contour hatching ─────────────────────────────
        # Compute gradient magnitude and direction via Sobel on reference lum.
        ref_lum = (0.299 * rarr[:, :, 0]
                   + 0.587 * rarr[:, :, 1]
                   + 0.114 * rarr[:, :, 2])
        gx = _sobel(ref_lum, axis=1)
        gy = _sobel(ref_lum, axis=0)
        grad_mag = _np.sqrt(gx**2 + gy**2)
        grad_mag /= (grad_mag.max() + 1e-8)

        # Edge zone: pixels above a gradient threshold
        edge_zone = grad_mag > 0.12
        edge_pixels = _np.argwhere(edge_zone)

        rng = _np.random.default_rng(seed=77)

        if edge_pixels.shape[0] > 0:
            n_hatch = max(1, int(edge_pixels.shape[0] * hatch_density))
            chosen_idx = rng.choice(edge_pixels.shape[0], size=n_hatch, replace=False)
            chosen = edge_pixels[chosen_idx]

            # Half-hatch-length for centering each mark
            hl = max(1, int(hatch_length / 2))

            for ys, xs in chosen:
                # Gradient direction at this point (tangent = perpendicular to gradient)
                gx_v = float(gx[ys, xs])
                gy_v = float(gy[ys, xs])
                norm = (gx_v**2 + gy_v**2) ** 0.5 + 1e-8
                # Tangent direction (parallel to contour edge)
                tx = -gy_v / norm
                ty =  gx_v / norm

                # Local darker tint — slightly below canvas colour
                local_r = float(new_R[ys, xs]) * 0.72
                local_g = float(new_G[ys, xs]) * 0.72
                local_b = float(new_B[ys, xs]) * 0.72

                # Draw hatch segment centered on pixel
                for step in range(-hl, hl + 1):
                    px = int(round(xs + tx * step))
                    py = int(round(ys + ty * step))
                    if 0 <= px < self.w and 0 <= py < self.h:
                        a = hatch_opacity
                        new_R[py, px] = new_R[py, px] * (1 - a) + local_r * a
                        new_G[py, px] = new_G[py, px] * (1 - a) + local_g * a
                        new_B[py, px] = new_B[py, px] * (1 - a) + local_b * a

        n_hatches = n_hatch if edge_pixels.shape[0] > 0 else 0

        # ── Zone 2: Chrysographic gold filaments ─────────────────────────────
        # Eligible: upper-midtone to highlight (0.45–0.88 luminance)
        gold_eligible = (lum >= 0.45) & (lum <= 0.88)
        gold_pixels = _np.argwhere(gold_eligible)

        n_gold = 0
        if gold_pixels.shape[0] > 0:
            n_gold = max(1, int(gold_pixels.shape[0] * gold_density))
            gold_chosen = rng.choice(gold_pixels.shape[0], size=n_gold, replace=False)
            chosen_gold = gold_pixels[gold_chosen]

            gr, gg, gb = float(gold_tint[0]), float(gold_tint[1]), float(gold_tint[2])
            filament_len = 5   # short horizontal dash simulating a pen filament

            for ys, xs in chosen_gold:
                for dx in range(-filament_len // 2, filament_len // 2 + 1):
                    px = xs + dx
                    if 0 <= px < self.w:
                        a = gold_opacity
                        new_R[ys, px] = _np.clip(new_R[ys, px] * (1 - a) + gr * a, 0, 1)
                        new_G[ys, px] = _np.clip(new_G[ys, px] * (1 - a) + gg * a, 0, 1)
                        new_B[ys, px] = _np.clip(new_B[ys, px] * (1 - a) + gb * a, 0, 1)

        # ── Zone 3: Luminosity lift (gesso-ground simulation) ─────────────────
        # Additive brightness boost — strongest in midtone/highlight areas where
        # the white gesso ground would show through thin tempera paint films.
        lift_weight = _np.clip(lum, 0.0, 1.0)   # scale lift by existing luminance
        new_R = _np.clip(new_R + luminosity_lift * lift_weight, 0.0, 1.0)
        new_G = _np.clip(new_G + luminosity_lift * lift_weight, 0.0, 1.0)
        new_B = _np.clip(new_B + luminosity_lift * lift_weight, 0.0, 1.0)

        # ── Write back to ARGB32 surface (BGRA) ──────────────────────────────
        buf[:, :, 0] = _np.clip(new_B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 2] = _np.clip(new_R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        tmp = _cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), _cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"    Botticelli pass complete  "
              f"(hatch marks: {n_hatches}  gold filaments: {n_gold})")

    # ─────────────────────────────────────────────────────────────────────────
    # tonal_envelope_pass — Portrait luminosity gradient improvement
    # ─────────────────────────────────────────────────────────────────────────

    def tonal_envelope_pass(
            self,
            center_x:     Optional[float] = None,
            center_y:     Optional[float] = None,
            radius:       Optional[float] = None,
            lift_strength: float = 0.10,
            lift_warmth:   float = 0.28,
            edge_darken:   float = 0.08,
            gamma:         float = 1.8,
    ):
        """
        Tonal envelope — radial portrait luminosity gradient.

        In traditional portraiture, master painters consciously managed the
        *tonal envelope* of the composition: the overall luminance distribution
        that guides the viewer's eye from the peripheral darkening at the
        canvas edges inward to the brightest zone around the sitter's face.
        This is distinct from the finish-pass vignette (which darkens edges
        mechanically) in that it *brightens the portrait center with warmth*
        rather than only darkening the corners, creating a three-dimensional
        sense of light gathering at the face.

        Leonardo, Raphael, and Botticelli all used this compositional
        luminosity management, though it operates at the level of the full
        composition rather than individual stroke placement.  The effect is
        most visible in Leonardo's "Lady with an Ermine" and Raphael's
        "Baldassare Castiglione" — both have a subtle inner glow around the
        face that cannot be explained by the depicted light source alone; it
        is a painterly fiction that makes the face appear self-luminous.

        This pass is the session's random artistic improvement: a new
        pipeline primitive for compositional luminosity management that
        operates globally on the canvas after all stroke passes are complete,
        simulating the final tonal adjustments that Renaissance masters made
        to unify the composition before varnishing.

        Implementation
        --------------
        1. Compute a radial weight map centered on (center_x, center_y)
           with sigmoid falloff at `radius` pixels.
        2. In the central zone: additive warm lift toward ivory (simulating
           the face-glow effect of reflected candlelight or window light
           gathering at the portrait center).
        3. At the periphery: slight cool darkening (enhancing depth and
           framing the figure without the mechanical look of a flat vignette).

        Parameters
        ----------
        center_x    : Horizontal centre of the luminosity envelope, as a
                      fraction of canvas width [0, 1].  Defaults to 0.50.
        center_y    : Vertical centre, as a fraction of canvas height [0, 1].
                      Defaults to 0.35 (typical portrait face position).
        radius      : Radius of the bright zone as a fraction of the shorter
                      canvas dimension.  Defaults to 0.42 — roughly the
                      inscribed circle within which a half-length portrait's
                      face and hands are contained.
        lift_strength: Maximum additive luminance in the centre zone.
                       0.06–0.14 gives a subtle perceptible glow without
                       bleaching the face.
        lift_warmth  : Fraction of the lift applied as a warm amber tint
                       (boosting R > G > B) rather than neutral white.
                       0.20–0.40: enough warmth to simulate the characteristic
                       amber of Renaissance candle/window light.
        edge_darken  : Maximum luminance subtraction at the canvas corners.
                       0.04–0.12: subtle framing, not a heavy vignette.
        gamma        : Exponent on the radial weight — higher values create a
                       sharper boundary between the bright centre and dark
                       periphery.  1.5–2.5 gives a natural-looking gradient.
        """
        import numpy as _np
        import cairo as _cairo

        cx = center_x if center_x is not None else 0.50
        cy = center_y if center_y is not None else 0.35
        r  = radius   if radius   is not None else 0.42

        print(f"  Tonal envelope pass  "
              f"(centre=({cx:.2f},{cy:.2f})  r={r:.2f}  "
              f"lift={lift_strength:.2f}  edge_darken={edge_darken:.2f})")

        # ── Read canvas BGRA ──────────────────────────────────────────────────
        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        R = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Build radial weight map ───────────────────────────────────────────
        # w=1.0 at center, 0.0 at radius, negative (edge darkening) beyond.
        y_idx = _np.arange(self.h, dtype=_np.float32)[:, None] / self.h
        x_idx = _np.arange(self.w, dtype=_np.float32)[None, :] / self.w

        short_side = min(self.w, self.h)
        # Elliptical distance (portrait-aware: slightly wider than tall)
        dx = (x_idx - cx) / (r * 1.15)
        dy = (y_idx - cy) / r
        dist = _np.sqrt(dx**2 + dy**2)

        # Central bright zone: dist < 1 → positive weight toward lift_strength
        bright_weight = _np.clip(1.0 - dist, 0.0, 1.0) ** gamma

        # Edge dark zone: dist > 1 → negative weight toward edge_darken
        dark_weight = _np.clip(dist - 1.0, 0.0, 1.0) ** (gamma * 0.7)

        # ── Apply central luminosity lift ─────────────────────────────────────
        # Warm ivory target: more red boost than green/blue.
        warm_r = lift_strength * (1.0 + lift_warmth * 0.40)
        warm_g = lift_strength * (1.0 - lift_warmth * 0.08)
        warm_b = lift_strength * (1.0 - lift_warmth * 0.35)

        new_R = _np.clip(R + bright_weight * warm_r, 0.0, 1.0)
        new_G = _np.clip(G + bright_weight * warm_g, 0.0, 1.0)
        new_B = _np.clip(B + bright_weight * warm_b, 0.0, 1.0)

        # ── Apply peripheral darkening ────────────────────────────────────────
        # Slight cool shift (blue channel preserved more than red) to give
        # the corners an atmospheric depth rather than flat grey.
        new_R = _np.clip(new_R - dark_weight * edge_darken * 1.10, 0.0, 1.0)
        new_G = _np.clip(new_G - dark_weight * edge_darken * 0.95, 0.0, 1.0)
        new_B = _np.clip(new_B - dark_weight * edge_darken * 0.70, 0.0, 1.0)

        # ── Write back ────────────────────────────────────────────────────────
        buf[:, :, 0] = _np.clip(new_B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 2] = _np.clip(new_R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        tmp = _cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), _cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print("    Tonal envelope pass complete")

    # ─────────────────────────────────────────────────────────────────────────
    # durer_engraving_pass — Albrecht Dürer Northern Renaissance graphic precision
    # ─────────────────────────────────────────────────────────────────────────

    def durer_engraving_pass(
            self,
            reference,
            hatch_density:    float = 0.030,
            hatch_length:     float = 10.0,
            hatch_opacity:    float = 0.45,
            cross_hatch:      bool  = True,
            shadow_threshold: float = 0.45,
            cool_shift:       float = 0.06,
    ):
        """
        Simulates Albrecht Dürer's engraving-influenced oil shadow technique.

        Dürer's oil paintings carry the unmistakable imprint of his years as
        a master engraver.  In engraving, tonal gradations are achieved through
        the *density* and *crossing angle* of fine parallel lines, not through
        smooth blending.  Dürer applied this graphic principle to oil painting:
        in his shadow zones, forms are built through thin, directional strokes
        that run parallel and cross-parallel (at ±45°), creating a systematic
        hatching that reads as both painted and drawn simultaneously.

        This pass replicates three aspects of his technique:

        1. **Cross-hatching in shadow zones** — In areas darker than
           ``shadow_threshold``, fine diagonal strokes are drawn at +45°
           (primary hatching) and, if ``cross_hatch=True``, a second pass at
           −45° (cross-hatching).  Line density and opacity scale with local
           darkness: the deepest shadows receive the most marks at the highest
           opacity; the upper shadow zone receives sparse, lighter marks.
           This graduated density replicates the engraving convention of
           building tonal depth through accumulating hatch lines.

        2. **Directional shadow parallel lines** — Unlike Botticelli's
           contour-following tangent marks, Dürer's hatching is consistently
           directional (±45° to the picture plane), independent of local
           surface curvature.  This is the signature quality that separates
           engraving-influenced oil from purely painterly oil technique.

        3. **Cool shadow shift** — Dürer's shadows have a cool blue-grey
           quality absent from Italian chiaroscuro.  A subtle cool tint
           (reducing R, preserving B) is applied in the shadow zone,
           simulating the cool transparent grey washes he laid into shadows
           before the hatching strokes.

        Parameters
        ----------
        reference       : PIL Image or ndarray — the reference image.
        hatch_density   : Fraction of shadow-zone pixels receiving a hatch
                          mark.  0.020–0.040 replicates Dürer's shadow density.
        hatch_length    : Length of each hatch stroke in pixels (6–14).
                          Dürer's marks in oil were slightly longer than
                          Botticelli's tempera hatching.
        hatch_opacity   : Base opacity of hatch marks (0.30–0.55).
                          Scales with local darkness — deepest shadows use
                          full hatch_opacity; lighter shadow zones use 0.5×.
        cross_hatch     : Whether to apply a second pass of −45° hatching
                          over the primary +45° layer.  True = full
                          cross-hatching (Dürer's standard shadow convention).
                          False = single-direction hatching (his lighter
                          shadow passages use single-direction only).
        shadow_threshold: Luminance below which hatching is applied (0–1).
                          0.45 captures shadow and dark-midtone zones without
                          intruding into the lit flesh areas.
        cool_shift      : Magnitude of the cool (blue-grey) shift applied in
                          shadow zones.  0.04–0.08 is perceptible but subtle —
                          the cool is an undertone, not a dominant hue.

        Notes
        -----
        Inspired by: "Self-Portrait at 28" (1500, Alte Pinakothek),
        "Portrait of Hieronymus Holzschuher" (1526, Gemäldegalerie Berlin),
        "Self-Portrait at 26" (1498, Prado).
        Technical reference: Panofsky, "The Life and Art of Albrecht Dürer"
        (1943); Koerner, "The Moment of Self-Portraiture in German Renaissance
        Art" (1993); NGA technical study of Dürer panel paintings.
        Randomly selected artistic discovery for session 34 — the Northern
        Renaissance's graphic precision as a distinct oil-painting paradigm,
        extending the hatching vocabulary beyond Botticelli's tempera-specific
        contour marks to a systematic cross-directional engraving logic.
        """
        import numpy as _np
        import cairo as _cairo
        from PIL import Image as _Img

        print(f"  Dürer engraving pass  "
              f"(hatch_density={hatch_density:.3f}  cross_hatch={cross_hatch}  "
              f"cool_shift={cool_shift:.2f})")

        # ── Read reference and current canvas (BGRA) ─────────────────────────
        ref = self._prep(reference)
        rarr = ref[:, :, :3].astype(_np.float32) / 255.0   # (H, W, 3) RGB float

        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        R = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.299 * R + 0.587 * G + 0.114 * B

        new_R = R.copy()
        new_G = G.copy()
        new_B = B.copy()

        # ── Zone 1: Cool shadow shift ─────────────────────────────────────────
        # Pixels below shadow_threshold get a cool (blue-grey) tint: reduce R
        # slightly, leave G neutral, preserve B.  The shift is proportional to
        # how far the pixel falls into the shadow zone.
        shadow_weight = _np.clip((shadow_threshold - lum) / shadow_threshold, 0.0, 1.0)
        new_R = _np.clip(new_R - shadow_weight * cool_shift * 1.20, 0.0, 1.0)
        new_G = _np.clip(new_G - shadow_weight * cool_shift * 0.60, 0.0, 1.0)
        new_B = _np.clip(new_B + shadow_weight * cool_shift * 0.35, 0.0, 1.0)

        # ── Zone 2: Directional cross-hatching in shadow zones ────────────────
        # Shadow pixels receive fine parallel lines at +45° and (if cross_hatch)
        # a second pass at −45°.  Opacity and density scale with local darkness.
        shadow_mask = lum < shadow_threshold
        shadow_pixels = _np.argwhere(shadow_mask)

        rng = _np.random.default_rng(seed=42)

        def _draw_hatch_pass(angle_deg: float, density: float, opacity_scale: float):
            """Draw a single directional hatch pass at angle_deg."""
            if shadow_pixels.shape[0] == 0:
                return 0
            n_marks = max(1, int(shadow_pixels.shape[0] * density))
            chosen_idx = rng.choice(shadow_pixels.shape[0], size=n_marks, replace=False)
            chosen = shadow_pixels[chosen_idx]

            import math as _math
            rad = _math.radians(angle_deg)
            dx = _math.cos(rad)
            dy = _math.sin(rad)
            hl = max(1, int(hatch_length / 2))

            for ys, xs in chosen:
                # Local darkness weight: deeper shadow → more opacity
                local_lum = float(lum[ys, xs])
                depth_weight = _np.clip(1.0 - local_lum / shadow_threshold, 0.0, 1.0)
                mark_opacity = hatch_opacity * opacity_scale * (0.50 + 0.50 * depth_weight)

                # Hatch colour: slightly darker and cooler than canvas pixel
                local_r = float(new_R[ys, xs]) * 0.68
                local_g = float(new_G[ys, xs]) * 0.72
                local_b = float(new_B[ys, xs]) * 0.78   # blue channel preserved more

                for step in range(-hl, hl + 1):
                    px = int(round(xs + dx * step))
                    py = int(round(ys + dy * step))
                    if 0 <= px < self.w and 0 <= py < self.h:
                        a = mark_opacity
                        new_R[py, px] = new_R[py, px] * (1 - a) + local_r * a
                        new_G[py, px] = new_G[py, px] * (1 - a) + local_g * a
                        new_B[py, px] = new_B[py, px] * (1 - a) + local_b * a

            return n_marks

        # Primary hatch at +45°
        n_primary = _draw_hatch_pass(45.0, hatch_density, 1.0)
        # Cross-hatch at −45° with slightly lower density and opacity
        n_cross = 0
        if cross_hatch:
            n_cross = _draw_hatch_pass(-45.0, hatch_density * 0.65, 0.75)

        # ── Write back to ARGB32 surface (BGRA) ──────────────────────────────
        buf[:, :, 0] = _np.clip(new_B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 2] = _np.clip(new_R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        tmp = _cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), _cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"    Dürer engraving pass complete  "
              f"(primary marks: {n_primary}  cross marks: {n_cross})")

    # ─────────────────────────────────────────────────────────────────────────
    # selective_focus_pass — Portrait depth-of-field softening (random improvement)
    # ─────────────────────────────────────────────────────────────────────────

    def selective_focus_pass(
            self,
            center_x:        float = 0.50,
            center_y:        float = 0.30,
            focus_radius:    float = 0.32,
            max_blur_radius: float = 4.0,
            desaturation:    float = 0.12,
            gamma:           float = 2.0,
    ):
        """
        Applies a radial selective-focus softening to peripheral areas.

        Portrait painters throughout history — from Leonardo to Vermeer to
        Sargent — kept the focal area (typically the sitter's face) rendered
        with maximum sharpness and clarity while allowing the peripheral zones
        (clothing, background, hands) to soften gradually.  This was partly
        intentional (directing the viewer's eye) and partly a natural consequence
        of working at close range: the artist's own eye focused on the face and
        rendered it with proportionally more attention and refinement.

        This pass replicates that quality computationally: pixels beyond the
        ``focus_radius`` ellipse are progressively blurred and desaturated,
        with both effects scaling quadratically with distance from the focal
        centre.  The blur is applied as a Gaussian convolution with a radius
        that grows from zero at the focus boundary to ``max_blur_radius`` at
        the canvas corners.  Desaturation reduces the chromatic intensity of
        peripheral areas, simulating the slightly less saturated peripheral
        vision of the painting eye and the tonal wash quality of loosely-
        rendered background passages.

        The pass is designed to be subtle: the default parameters produce a
        barely-perceptible improvement in visual hierarchy that does not read
        as an obvious photographic blur effect, but as the natural quality
        difference between a carefully wrought face and a broadly indicated
        background — the quality that separates a portrait by Dürer or Holbein
        from a merely competent likeness.

        Parameters
        ----------
        center_x       : Horizontal focus centre as fraction of canvas width.
        center_y       : Vertical focus centre as fraction of canvas height.
                         0.30 places the focus at typical portrait face height.
        focus_radius   : Radius of the sharp zone as a fraction of the shorter
                         canvas dimension.  0.28–0.36 covers the face and the
                         immediate surrounding area.
        max_blur_radius: Maximum Gaussian blur sigma at the canvas corners, in
                         pixels.  2.0–5.0: subtle without reading as digital
                         post-processing.
        desaturation   : Maximum chroma reduction in the peripheral zone (0–1).
                         0.08–0.18: enough to read as a looser passage without
                         draining the peripheral colour to grey.
        gamma          : Exponent on the radial transition — higher values
                         create a sharper focus boundary.  1.5–2.5.

        Notes
        -----
        Randomly selected artistic improvement for session 34 — a composable
        selective-focus primitive that benefits any portrait pipeline by
        replicating the natural attention-gradient of the human eye as it
        studies a sitter across a working distance.  Distinct from
        ``sfumato_veil_pass`` (which targets painted edges specifically) and
        ``atmospheric_depth_pass`` (which models distance-based aerial haze):
        this pass is compositionally focused, not optically motivated.
        """
        import numpy as _np
        import cairo as _cairo
        from scipy.ndimage import gaussian_filter as _gauss

        print(f"  Selective focus pass  "
              f"(centre=({center_x:.2f},{center_y:.2f})  r={focus_radius:.2f}  "
              f"max_blur={max_blur_radius:.1f}  desat={desaturation:.2f})")

        # ── Early exit: nothing to do when both effects are zero ──────────────
        if max_blur_radius <= 0.0 and desaturation <= 0.0:
            print(f"    Selective focus pass complete  (no-op — zero blur and desat)")
            return

        # ── Read canvas BGRA ──────────────────────────────────────────────────
        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(self.h, self.w, 4).copy()
        B = buf[:, :, 0].astype(_np.float32) / 255.0
        G = buf[:, :, 1].astype(_np.float32) / 255.0
        R = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Build radial distance map ─────────────────────────────────────────
        # 0 at focus centre, 1 at focus boundary, > 1 outside
        y_idx = _np.arange(self.h, dtype=_np.float32)[:, None] / self.h
        x_idx = _np.arange(self.w, dtype=_np.float32)[None, :] / self.w

        short = min(self.w, self.h)
        # Elliptical — slightly wider than tall for portrait proportions
        edx = (x_idx - center_x) / (focus_radius * 1.15)
        edy = (y_idx - center_y) / focus_radius
        dist = _np.sqrt(edx**2 + edy**2)

        # Peripheral weight: 0 inside focus, scales to 1 at corners
        outer = _np.clip(dist - 1.0, 0.0, None)
        # Normalise: maximum possible outer distance from focus boundary
        max_dist = _np.max(outer) + 1e-8
        w_periph = _np.clip(outer / max_dist, 0.0, 1.0) ** gamma   # (H, W)

        # ── Blur channel: progressive Gaussian on the full image, blend ───────
        # Rather than per-pixel blur (expensive), blur the full canvas at the
        # maximum radius and composite using the radial weight mask.
        # This is an efficient approximation of radially-varying blur.
        if max_blur_radius > 0.5:
            R_blurred = _gauss(R, sigma=max_blur_radius)
            G_blurred = _gauss(G, sigma=max_blur_radius)
            B_blurred = _gauss(B, sigma=max_blur_radius)
        else:
            R_blurred, G_blurred, B_blurred = R, G, B

        # Composite: sharp in focus zone, blurred in periphery
        new_R = R * (1.0 - w_periph) + R_blurred * w_periph
        new_G = G * (1.0 - w_periph) + G_blurred * w_periph
        new_B = B * (1.0 - w_periph) + B_blurred * w_periph

        # ── Desaturation: reduce chroma in periphery ──────────────────────────
        # Perceptual grey conversion, then lerp toward grey by desaturation × weight
        grey = 0.299 * new_R + 0.587 * new_G + 0.114 * new_B
        desat_w = w_periph * desaturation
        new_R = new_R * (1.0 - desat_w) + grey * desat_w
        new_G = new_G * (1.0 - desat_w) + grey * desat_w
        new_B = new_B * (1.0 - desat_w) + grey * desat_w

        # ── Write back ────────────────────────────────────────────────────────
        buf[:, :, 0] = _np.clip(new_B * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_G * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 2] = _np.clip(new_R * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = 255

        tmp = _cairo.ImageSurface.create_for_data(
            bytearray(buf.tobytes()), _cairo.FORMAT_ARGB32, self.w, self.h)
        self.canvas.ctx.set_source_surface(tmp, 0, 0)
        self.canvas.ctx.paint()

        print(f"    Selective focus pass complete  "
              f"(blur sigma={max_blur_radius:.1f}  desat={desaturation:.2f})")

    def hatching_pass(
            self,
            reference:       "Union[np.ndarray, Image.Image]",
            n_strokes:       int   = 2400,
            stroke_size:     int   = 3,
            angle_primary:   float = 45.0,
            angle_cross:     float = -45.0,
            cross_hatch:     bool  = True,
            shadow_thresh:   float = 0.45,
            dark_color:      Color = (0.28, 0.20, 0.12),
            light_color:     Color = (0.92, 0.88, 0.75),
            opacity_shadow:  float = 0.52,
            opacity_light:   float = 0.18,
            hatch_length:    float = 12.0,
            spacing_jitter:  float = 0.35,
    ):
        """
        Tempera hatching pass — inspired by Fra Angelico's Quattrocento technique.

        Egg-tempera dries almost instantly on the chalk-white gesso panel, which
        means the wet-into-wet blending exploited by oil painters is unavailable.
        Instead, Renaissance tempera painters built tonal form through *hatching*:
        extremely fine parallel strokes laid over a dry previous layer at a
        consistent angle.  Shadow regions received dense overlapping hatch layers;
        lit areas were left relatively sparse so the brilliant gesso ground
        could shine through between the strokes.

        This pass simulates that technique by scattering short, thin, directional
        line strokes across the canvas in two ways:

        1. **Shadow hatching** — In pixels darker than ``shadow_thresh`` the pass
           lays down strokes of ``dark_color`` at ``angle_primary`` (default 45°).
           Stroke density is proportional to darkness: fully shadowed regions
           receive the most strokes; mid-tones receive fewer; fully lit areas
           receive none.  This builds tonal depth through *accumulation*, not
           blending.

        2. **Cross-hatching** — When ``cross_hatch=True`` a second pass of strokes
           at ``angle_cross`` (default −45°, perpendicular to the first) is applied
           in the deepest shadow regions (lum < shadow_thresh × 0.55).  The
           diagonal cross-pattern replicates the "piani di colore" layering that
           Fra Angelico, Botticelli, and Perugino used to model the deepest shadow
           passages in flesh and drapery.

        3. **Light accent strokes** — In bright highlight pixels (lum > 0.82) a
           sparse scatter of slightly lighter strokes in ``light_color`` at the
           primary angle indicates the gesso ground asserting itself between hatch
           layers — the distinctive luminous quality of tempera that oil painting
           cannot replicate.

        The technique is relevant to any early tempera pipeline (Fra Angelico,
        Botticelli, Piero della Francesca, Ghirlandaio) and also to the chalk /
        silverpoint underdrawing stage used before oil painting in Dürer's and
        Holbein's Northern Renaissance technique.

        Parameters
        ----------
        reference       : Tonal reference — used to read pixel luminance for
                          stroke placement and density decisions.
        n_strokes       : Total number of hatch strokes to scatter.  2000–4000
                          is typical for a portrait; increase for denser shadow.
        stroke_size     : Stroke width in pixels.  2–4px for tempera fidelity;
                          broader strokes shift toward chalk or silverpoint feel.
        angle_primary   : Angle of primary hatch strokes in degrees.  45° is the
                          canonical Fra Angelico angle derived from his San Marco
                          frescoes; 30° or 60° are period-appropriate alternatives.
        angle_cross     : Angle of the cross-hatch layer (only used when
                          cross_hatch=True).  −45° is perpendicular to 45°.
        cross_hatch     : Whether to add the second diagonal layer in deep shadows.
        shadow_thresh   : Luminance threshold below which hatch strokes are placed.
                          0.45 puts the hatching in the shadow half of the tonal
                          range; increase toward 0.65 for softer, broader coverage.
        dark_color      : Hatch stroke colour for shadow region strokes.
                          Fra Angelico used raw sienna (0.28, 0.20, 0.12) for flesh
                          shadows and a cool grey-brown for drapery.
        light_color     : Hatch stroke colour for highlight accent strokes.
                          Pure lead-white (0.92, 0.88, 0.75) for gesso showing through.
        opacity_shadow  : Base opacity of shadow hatch strokes (0–1).
        opacity_light   : Opacity of light accent strokes (0–1).
        hatch_length    : Length of each hatch stroke in pixels.  8–16px for
                          tempera; longer strokes (~20px) read more like chalk.
        spacing_jitter  : Fraction of hatch_length added as random positional noise.
                          0.30–0.45: slight irregularity avoids mechanical regularity.

        Notes
        -----
        Randomly selected artistic improvement for this session — a composable
        tempera-hatching primitive that benefits any pre-oil pipeline (Quattrocento
        tempera, silverpoint underdrawing, chalk cartoon).  Distinct from
        ``build_form()`` (which uses free-flowing paint strokes following the image
        gradient) and ``angular_contour_pass()`` (which draws expressive contour
        outlines at figure boundaries): hatching_pass builds *interior tonal form*
        through systematic parallel marks, as Renaissance masters did on gesso.
        """
        import math as _math
        import random as _random
        import numpy as _np
        import cairo as _cairo

        print(f"  Hatching pass  (n={n_strokes}  angle={angle_primary:.0f}°  "
              f"cross={cross_hatch}  shadow_thresh={shadow_thresh:.2f})…")

        ref = self._prep(reference)
        h, w = self.h, self.w
        rng = _random.Random(7)   # deterministic seed

        # Pre-compute luminance map from reference for placement decisions.
        # _prep() returns a uint8 array (0–255); normalise to [0, 1] so that
        # shadow_thresh and light thresholds compare in the same scale.
        ref_f = ref[:, :, :3].astype(_np.float32) / 255.0
        lum = (0.299 * ref_f[:, :, 0]
             + 0.587 * ref_f[:, :, 1]
             + 0.114 * ref_f[:, :, 2])   # (H, W) float32 in [0, 1]

        def _draw_hatch(angle_deg: float, color: Color, opacity: float,
                        lum_min: float, lum_max: float, count: int):
            """
            Scatter ``count`` hatch strokes in pixels with luminance in
            [lum_min, lum_max].  Each stroke is a short, thin line at
            ``angle_deg`` degrees, placed randomly within qualifying pixels.
            """
            rad = _math.radians(angle_deg)
            cos_a = _math.cos(rad)
            sin_a = _math.sin(rad)

            # Build a list of candidate pixel indices in the lum band
            mask = (lum >= lum_min) & (lum <= lum_max)
            ys, xs = _np.where(mask)
            if len(ys) == 0:
                return

            ctx = self.canvas.ctx
            ctx.save()

            r_c, g_c, b_c = color

            for _ in range(count):
                # Sample a candidate pixel biased to the lum band
                idx = rng.randrange(len(ys))
                cy  = float(ys[idx]) + rng.uniform(-spacing_jitter * hatch_length,
                                                    spacing_jitter * hatch_length)
                cx  = float(xs[idx]) + rng.uniform(-spacing_jitter * hatch_length,
                                                    spacing_jitter * hatch_length)

                half = hatch_length * 0.5
                x0 = cx - cos_a * half
                y0 = cy - sin_a * half
                x1 = cx + cos_a * half
                y1 = cy + sin_a * half

                # Stroke-density scaling: darker → more opaque hatch strokes
                if lum_min < shadow_thresh:
                    # Map pixel luminance to opacity boost: darker = higher density
                    pix_lum = float(lum[
                        max(0, min(h - 1, int(cy))),
                        max(0, min(w - 1, int(cx)))
                    ])
                    density = _np.clip(1.0 - pix_lum / (shadow_thresh + 1e-6),
                                       0.0, 1.0)
                    eff_opacity = opacity * (0.35 + 0.65 * float(density))
                else:
                    eff_opacity = opacity

                ctx.set_source_rgba(r_c, g_c, b_c, eff_opacity)
                ctx.set_line_width(stroke_size)
                ctx.set_line_cap(_cairo.LINE_CAP_ROUND)
                ctx.move_to(x0, y0)
                ctx.line_to(x1, y1)
                ctx.stroke()

            ctx.restore()

        # ── Primary shadow hatching ───────────────────────────────────────────
        # Hatch density scales inversely with luminance within the shadow zone.
        # Darkest pixels get ~70% of total strokes; lighter shadow pixels get less.
        shadow_count = n_strokes
        _draw_hatch(angle_primary, dark_color, opacity_shadow,
                    0.0, shadow_thresh, shadow_count)

        # ── Cross-hatching in deepest shadows ────────────────────────────────
        if cross_hatch:
            deep_thresh = shadow_thresh * 0.55
            cross_count = n_strokes // 3
            _draw_hatch(angle_cross, dark_color, opacity_shadow * 0.75,
                        0.0, deep_thresh, cross_count)

        # ── Light accent strokes — gesso ground showing through ──────────────
        light_count = max(1, n_strokes // 8)
        _draw_hatch(angle_primary, light_color, opacity_light,
                    0.82, 1.0, light_count)

        print(f"    Hatching pass complete  "
              f"(shadow={shadow_count}  cross={n_strokes // 3 if cross_hatch else 0}  "
              f"light={light_count})")

    def holbein_jewel_glaze_pass(
            self,
            chroma_boost:      float = 0.30,
            jewel_lo:          float = 0.22,
            jewel_hi:          float = 0.72,
            shadow_cool_shift: float = 0.08,
            highlight_pale:    float = 0.14,
            shadow_desat:      float = 0.18,
            opacity:           float = 0.82,
    ):
        """
        Holbein jewel-glaze pass — inspired by Hans Holbein the Younger's technique.

        Holbein built his surfaces through thin, resin-rich oil glazes applied to a
        near-white ground, each glaze drying completely before the next was applied.
        Because he never used a warm amber varnish to unify the surface — as Leonardo,
        Raphael, and the Venetians did — each colour zone in a Holbein portrait retains
        its full chromatic identity: the crimson sleeve stays crimson, the smalt-blue
        doublet stays cold cobalt, the malachite green remains clear and mineral.  The
        result has a jewel-like, enamel quality: every colour appears to glow from
        within, as if lit by its own internal light rather than by a shared external
        source.

        This pass simulates that effect through three targeted per-pixel adjustments:

        1. **Jewel-zone chroma boost** — In the mid-luminance band (``jewel_lo`` to
           ``jewel_hi``, default 0.22–0.72) the pass boosts HSV saturation by
           ``chroma_boost`` (default 0.30).  This is the zone where local colour is
           most legible; boosting it replicates the jewel depth that Holbein achieved
           through repeated transparent glazes.  A smooth cosine ramp at both edges of
           the zone prevents hard saturation cliffs.

        2. **Shadow cooling and desaturation** — Pixels below ``jewel_lo`` have their
           saturation reduced by ``shadow_desat`` and their hue gently shifted toward
           the blue-grey end of the spectrum by ``shadow_cool_shift``.  Holbein's
           shadows are cool and restrained — never the warm chiaroscuro of Caravaggio —
           because his thin glazes lack the optical body to absorb light into drama.
           Desaturating the darks also ensures that the boosted mid-tones read as
           jewel-bright against a neutral shadow field.

        3. **Highlight paling** — Pixels above ``jewel_hi`` have their saturation
           reduced by ``highlight_pale`` and their value (lightness) pushed slightly
           toward an ivory-white, simulating the lead-white highlights Holbein applied
           last to seal the surface.  These near-white touches make the jewel mid-tones
           read as even richer by contrast.

        All operations are fully vectorised (NumPy) and applied to the raw Cairo surface
        buffer.  The result is blended back at ``opacity`` so the caller can control the
        overall strength of the effect.  The pass is safe to call multiple times —
        successive applications compound the jewel depth without clipping.

        Parameters
        ----------
        chroma_boost      : Saturation increase in the jewel zone (0–1 delta added to
                            HSV saturation, clamped to 1.0).  0.20–0.35 gives a
                            rich but believable jewel quality; higher values read as
                            illustration.
        jewel_lo          : Lower luminance boundary of the jewel zone (default 0.22).
                            Pixels below this are treated as deep shadow.
        jewel_hi          : Upper luminance boundary of the jewel zone (default 0.72).
                            Pixels above this are treated as highlight.
        shadow_cool_shift : Amount by which the hue of shadow pixels is shifted toward
                            the blue-grey cool direction (0–1, applied as a small
                            additive hue offset toward ~0.60 in HSV).
        highlight_pale    : Saturation reduction in the highlight zone (0–1 delta).
                            0.10–0.20 drives highlights toward ivory without fully
                            neutralising any remaining warm tint.
        shadow_desat      : Saturation reduction in the shadow zone (0–1 delta).
        opacity           : Blend weight of the adjusted layer over the original
                            canvas pixels (0 = no effect, 1 = full replacement).

        Notes
        -----
        Randomly selected artistic improvement for this session — a composable
        jewel-glaze primitive inspired by Holbein's unique palette strategy.  Distinct
        from ``chroma_zone_pass()`` (which only adjusts saturation globally), this pass
        also introduces directed warm/cool temperature shifts in the luminance extremes,
        replicating the specific chromatic personality of Northern Renaissance panel
        painting: brilliant mid-tone hues, cool restrained shadows, pale ivory lights.
        """
        import numpy as _np
        import colorsys as _colorsys

        print(f"  Holbein jewel-glaze pass  "
              f"(chroma_boost={chroma_boost:.2f}  "
              f"jewel=[{jewel_lo:.2f}–{jewel_hi:.2f}]  "
              f"opacity={opacity:.2f})…")

        h, w = self.h, self.w

        # ── Read current canvas (Cairo BGRA layout) ───────────────────────────
        buf = _np.frombuffer(self.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()   # keep original for the final opacity blend

        # Extract RGB float in [0, 1] — Cairo stores BGRA
        r_ch = buf[:, :, 2].astype(_np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(_np.float32) / 255.0
        b_ch = buf[:, :, 0].astype(_np.float32) / 255.0

        # ── Vectorised RGB → HSV ──────────────────────────────────────────────
        v_ch  = _np.maximum(_np.maximum(r_ch, g_ch), b_ch)   # value
        c_min = _np.minimum(_np.minimum(r_ch, g_ch), b_ch)   # chrominance range
        delta = v_ch - c_min

        # Saturation: s = delta / v (undefined when v=0 — keep s=0)
        s_ch = _np.where(v_ch > 1e-6, delta / (v_ch + 1e-6), 0.0)

        # Hue (in [0, 1] = [0°, 360°] / 360):
        #   When delta=0 the colour is achromatic — hue is undefined; set to 0.
        eps = 1e-6
        h_ch = _np.zeros_like(r_ch)

        r_max = (v_ch == r_ch) & (delta > eps)
        g_max = (v_ch == g_ch) & (delta > eps) & ~r_max
        b_max = ~r_max & ~g_max & (delta > eps)

        h_ch[r_max] = ((g_ch[r_max] - b_ch[r_max]) / delta[r_max]) % 6.0
        h_ch[g_max] = ((b_ch[g_max] - r_ch[g_max]) / delta[g_max]) + 2.0
        h_ch[b_max] = ((r_ch[b_max] - g_ch[b_max]) / delta[b_max]) + 4.0
        h_ch = h_ch / 6.0   # normalise to [0, 1]

        # ── Luminance (perceived brightness) for zone decisions ───────────────
        lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch   # (H, W) float32

        # ── Zone masks ────────────────────────────────────────────────────────
        in_shadow   = lum < jewel_lo
        in_highlight = lum > jewel_hi
        in_jewel    = ~in_shadow & ~in_highlight

        # Smooth cosine ramp at zone boundaries to avoid saturation cliffs.
        # Within the jewel zone, ramp from 0→1 over the lower 10% and 1→0 over
        # the upper 10% of the zone width.
        zone_width = jewel_hi - jewel_lo + eps
        ramp_w     = zone_width * 0.10   # transition width at each edge

        ramp_lo = _np.clip((lum - jewel_lo) / ramp_w, 0.0, 1.0)
        ramp_hi = _np.clip((jewel_hi - lum) / ramp_w, 0.0, 1.0)
        jewel_ramp = _np.where(in_jewel,
                               0.5 * (1.0 - _np.cos(_np.pi * _np.minimum(ramp_lo, ramp_hi))),
                               0.0)

        # ── Apply jewel-zone chroma boost ─────────────────────────────────────
        s_out = s_ch.copy()
        s_out = _np.where(in_jewel,
                          _np.clip(s_ch + chroma_boost * jewel_ramp, 0.0, 1.0),
                          s_out)

        # ── Shadow cooling + desaturation ─────────────────────────────────────
        # Shift hue toward blue (0.58 in [0,1] ≈ 210° — blue-grey / slate)
        hue_blue  = 0.58
        shadow_ramp = _np.clip((jewel_lo - lum) / (jewel_lo + eps), 0.0, 1.0)
        h_out = h_ch.copy()
        h_out = _np.where(
            in_shadow,
            h_ch + shadow_cool_shift * shadow_ramp * (hue_blue - h_ch),
            h_out,
        )
        s_out = _np.where(in_shadow,
                          _np.clip(s_ch - shadow_desat * shadow_ramp, 0.0, 1.0),
                          s_out)

        # ── Highlight paling ──────────────────────────────────────────────────
        # Drive highlights toward pale ivory by reducing saturation.
        # Also push value very slightly toward 1.0 (white-lead highlights).
        hi_ramp = _np.clip((lum - jewel_hi) / (1.0 - jewel_hi + eps), 0.0, 1.0)
        s_out = _np.where(in_highlight,
                          _np.clip(s_ch - highlight_pale * hi_ramp, 0.0, 1.0),
                          s_out)
        v_out = _np.where(in_highlight,
                          _np.clip(v_ch + 0.04 * hi_ramp, 0.0, 1.0),
                          v_ch)
        v_out = _np.where(in_jewel | in_shadow, v_ch, v_out)   # only highlights

        # ── Reconstruct RGB from adjusted HSV ─────────────────────────────────
        # HSV → RGB via sector-based formula (vectorised, no per-pixel loop)
        h6  = (h_out % 1.0) * 6.0           # [0, 6)
        hi_ = h6.astype(_np.int32) % 6      # sector index 0–5
        f   = h6 - hi_.astype(_np.float32)  # fractional part

        p   = v_out * (1.0 - s_out)
        q   = v_out * (1.0 - s_out * f)
        t_  = v_out * (1.0 - s_out * (1.0 - f))

        r_out = _np.zeros_like(r_ch)
        g_out = _np.zeros_like(g_ch)
        b_out = _np.zeros_like(b_ch)

        for sec, (rv, gv, bv) in enumerate(
            [(v_out, t_, p), (q, v_out, p), (p, v_out, t_),
             (p, q, v_out), (t_, p, v_out), (v_out, p, q)]
        ):
            mask = hi_ == sec
            r_out[mask] = rv[mask]
            g_out[mask] = gv[mask]
            b_out[mask] = bv[mask]

        # Achromatic pixels: copy value to all channels
        achromatic = delta < eps
        r_out[achromatic] = v_out[achromatic]
        g_out[achromatic] = v_out[achromatic]
        b_out[achromatic] = v_out[achromatic]

        # ── Blend adjusted layer back at `opacity` ───────────────────────────
        # Cairo BGRA: blue in [0], green in [1], red in [2], alpha in [3]
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        print(f"    Holbein jewel-glaze pass complete")

    def van_dyck_silver_drapery_pass(
            self,
            fabric_angle:     float = 30.0,
            shimmer_period:   float = 18.0,
            shimmer_strength: float = 0.08,
            silver_cool:      float = 0.12,
            ivory_boost:      float = 0.06,
            neutral_thresh:   float = 0.40,
            lum_lo:           float = 0.32,
            opacity:          float = 0.75,
    ):
        """
        Van Dyck silver-drapery pass — inspired by Anthony van Dyck's technique.

        Van Dyck's greatest technical achievement is his rendering of silk —
        particularly the shimmering, pearl-grey English court silks that appear
        in virtually every portrait from his London period (1632–1641).  He
        painted these with loaded, rapid strokes that follow the fall of the
        fabric, leaving thick bright ridges of pearl-grey alternating with cool
        shadow valleys.  The result has an almost liquid quality: the silk appears
        to shift and reflect as the viewer moves.

        Technically, this effect arises from two sources:
        1. **Woven-silk anisotropy** — warp and weft threads reflect light at
           slightly different angles, producing a subtle directional shimmer
           perpendicular to the fabric's main fold direction.
        2. **Temperature contrast** — van Dyck's highlights read warm ivory
           (lead-white tinted with naples yellow) while the shadow valleys cool
           toward a blue-grey (from the reddish-brown ground showing through thin
           grey paint).

        This pass simulates both effects through three per-pixel adjustments:

        1. **Directional shimmer** — A sinusoidal brightness modulation with
           period ``shimmer_period`` pixels is applied along the direction
           *perpendicular* to ``fabric_angle``.  Pixels in the candidate silk
           zone (luminance ≥ ``lum_lo`` and saturation ≤ ``neutral_thresh``) are
           brightened at shimmer peaks and slightly darkened at troughs,
           reproducing the alternating highlight-shadow structure of woven silk.

        2. **Silver cooling** — The silk zone is shifted toward cool blue-grey by
           reducing the red channel and boosting the blue channel proportionally
           to local luminance.  This replicates the way van Dyck's thin silver-grey
           paint allows the warm reddish-brown imprimatura to warm the shadow
           passages while highlights stay cool and metallic.

        3. **Ivory specular push** — In the brightest pixels of the silk zone
           (lum > 0.78) a gentle ivory-white boost is applied via a linear ramp,
           simulating the thick lead-white impasto van Dyck pressed onto the
           highest highlight ridges as a final loaded-brush stroke.

        All operations are fully vectorised (NumPy) and applied to the raw Cairo
        surface buffer.  The result is blended back at ``opacity`` so the caller
        can control overall effect strength.  The pass is composable — call it
        after ``block_in()`` to establish the silk structure, then after
        ``place_lights()`` to sharpen the final specular ridge.

        Parameters
        ----------
        fabric_angle     : Direction of the fabric's main fold flow, in degrees.
                           0° = horizontal folds, 90° = vertical, 30–45° typical
                           for draped court costume.  The shimmer is applied
                           *perpendicular* to this angle.
        shimmer_period   : Pixel period of the woven-silk shimmer (default 18px).
                           12–22px is perceptually realistic at portrait scale;
                           larger values produce smoother, more satin-like sheen.
        shimmer_strength : Amplitude of the brightness oscillation (0–1 delta,
                           default 0.08).  0.05–0.10 gives a subtle realistic
                           shimmer; higher values read as illustration.
        silver_cool      : Strength of the cool blue-grey shift in the silk zone
                           (0–1, default 0.12).  Applied as a luminance-scaled
                           reduction of R and boost of B.
        ivory_boost      : Strength of the ivory-white specular push in the
                           brightest highlights (lum > 0.78, default 0.06).
        neutral_thresh   : HSV saturation ceiling for silk-candidate pixels
                           (default 0.40).  Near-neutral grey-white pixels qualify;
                           strongly chromatic pixels (flesh, crimson, ultramarine)
                           are excluded from the silk zone.
        lum_lo           : Minimum luminance for silk-candidate pixels (default
                           0.32).  Deep shadows are excluded — only mid-to-bright
                           areas qualify as visible silk surface.
        opacity          : Blend weight of the adjusted layer over the original
                           canvas pixels (0 = no effect, 1 = full replacement).

        Notes
        -----
        Randomly selected artistic improvement for this session — a composable
        silk-shimmer primitive inspired by van Dyck's directional drapery
        technique.  Distinct from ``luminous_fabric_pass()`` (Zurbarán's hyper-
        real razor-sharp white cloth) and ``scumble_pass()`` (undirected dry-
        brush texture): this pass introduces *directional* periodicity that
        simulates the warp/weft anisotropy of woven silk, combined with the
        warm/cool temperature contrast specific to van Dyck's pearl-grey palette.
        """
        import numpy as _np

        print(f"  Van Dyck silver-drapery pass  "
              f"(fabric_angle={fabric_angle:.0f}°  "
              f"shimmer_period={shimmer_period:.0f}px  "
              f"opacity={opacity:.2f})…")

        h, w = self.h, self.w

        # ── Read current canvas (Cairo BGRA layout) ───────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Extract RGB float in [0, 1] — Cairo stores BGRA
        r_ch = buf[:, :, 2].astype(_np.float32) / 255.0
        g_ch = buf[:, :, 1].astype(_np.float32) / 255.0
        b_ch = buf[:, :, 0].astype(_np.float32) / 255.0

        # ── Luminance and saturation for zone decisions ───────────────────────
        lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch   # (H, W)

        v_ch  = _np.maximum(_np.maximum(r_ch, g_ch), b_ch)
        c_min = _np.minimum(_np.minimum(r_ch, g_ch), b_ch)
        delta = v_ch - c_min
        s_ch  = _np.where(v_ch > 1e-6, delta / (v_ch + 1e-6), 0.0)

        # Silk candidate mask: moderate-to-high luminance AND near-neutral colour.
        # Near-neutral = low saturation: grey, white, and pale silks qualify;
        # strongly chromatic areas (flesh, crimson, blue) are excluded.
        silk_mask = (lum >= lum_lo) & (s_ch <= neutral_thresh)

        # ── Coordinate grids for directional shimmer ──────────────────────────
        # Build per-pixel (y, x) arrays and project onto the direction
        # *perpendicular* to fabric_angle.  This gives each pixel a "fiber
        # position" value; the sinusoid along this axis creates the warp/weft
        # alternation that makes woven silk shimmer.
        ys_grid = _np.arange(h, dtype=_np.float32)[:, None] * _np.ones((1, w), dtype=_np.float32)
        xs_grid = _np.ones((h, 1), dtype=_np.float32) * _np.arange(w, dtype=_np.float32)[None, :]

        rad_perp   = _np.radians(fabric_angle + 90.0)   # perpendicular to fabric flow
        fiber_proj = xs_grid * _np.cos(rad_perp) + ys_grid * _np.sin(rad_perp)

        # Sinusoidal shimmer: peaks at +shimmer_strength, troughs at −shimmer_strength
        shimmer = shimmer_strength * _np.sin(
            2.0 * _np.pi * fiber_proj / (shimmer_period + 1e-6)
        )   # (H, W)  values in [−shimmer_strength, +shimmer_strength]

        # ── Apply shimmer to silk zone ────────────────────────────────────────
        # Brighten ridges (positive shimmer), slightly darken valleys (negative).
        # Apply equally to R, G; apply at ×0.50 to B so shimmer ridges warm
        # slightly (ivory ridge) and troughs cool slightly (no additional boost).
        r_out = _np.where(silk_mask, _np.clip(r_ch + shimmer,        0.0, 1.0), r_ch)
        g_out = _np.where(silk_mask, _np.clip(g_ch + shimmer,        0.0, 1.0), g_ch)
        b_out = _np.where(silk_mask, _np.clip(b_ch + shimmer * 0.50, 0.0, 1.0), b_ch)

        # ── Silver cooling — shift silk zone toward blue-grey ─────────────────
        # Reduce R, boost B, proportionally to how bright the pixel is within
        # the silk zone.  Brighter = more silver coolness (the paint is thinner
        # at highlights, so the imprimatura shows through less, making the
        # highlight cooler and more metallic).
        cool_scale = _np.clip((lum - lum_lo) / (1.0 - lum_lo + 1e-6), 0.0, 1.0)
        r_out = _np.where(silk_mask,
                          _np.clip(r_out - silver_cool * cool_scale, 0.0, 1.0),
                          r_out)
        b_out = _np.where(silk_mask,
                          _np.clip(b_out + silver_cool * cool_scale * 0.80, 0.0, 1.0),
                          b_out)

        # ── Ivory specular push in the brightest highlights ───────────────────
        # Van Dyck pressed thick lead-white (warm ivory) onto the highest
        # highlight ridges as a final loaded-brush stroke.  Simulate this by
        # boosting R and G (toward warm ivory) in pixels above lum=0.78.
        hi_thresh = 0.78
        hi_mask   = silk_mask & (lum > hi_thresh)
        hi_ramp   = _np.where(hi_mask,
                               _np.clip((lum - hi_thresh) / (1.0 - hi_thresh + 1e-6),
                                        0.0, 1.0),
                               0.0)
        r_out = _np.where(hi_mask,
                          _np.clip(r_out + ivory_boost * hi_ramp, 0.0, 1.0),
                          r_out)
        g_out = _np.where(hi_mask,
                          _np.clip(g_out + ivory_boost * hi_ramp * 0.85, 0.0, 1.0),
                          g_out)

        # ── Blend adjusted layer back at `opacity` ───────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        print(f"    Van Dyck silver-drapery pass complete")

    # ──────────────────────────────────────────────────────────────────────────
    # Rubens flesh-vitality pass
    # ──────────────────────────────────────────────────────────────────────────

    def rubens_flesh_vitality_pass(
            self,
            blush_strength:   float = 0.14,
            cream_strength:   float = 0.10,
            warm_shadow:      float = 0.06,
            blush_lo:         float = 0.28,
            blush_hi:         float = 0.68,
            highlight_thresh: float = 0.72,
            shadow_thresh:    float = 0.22,
            opacity:          float = 0.80,
    ):
        """
        Rubens flesh-vitality pass — inspired by Peter Paul Rubens' technique.

        Rubens' most celebrated achievement is his rendering of living flesh:
        warm, rosy, translucent, and unmistakably breathing.  He achieved this
        through three distinct chromatic strategies applied simultaneously:

        1. **Rosy blush in thin-skin zones** (mid-luminance band):
           Ears, nose tip, cheeks, lips, and knuckles — places where the skin is
           thin enough for blood vessels to show — received an extra glaze of
           vermilion or rose madder.  This is the flushed, vascular warmth that
           no cool-flesh palette can replicate.  Here we apply it as a
           luminance-gated R-channel boost that peaks in the mid-tone band
           (blush_lo..blush_hi) and falls to zero at the extremes.

        2. **Cream-ivory impasto at highlight peaks** (high-luminance band):
           Rubens pressed final highlights on with a palette knife — thick
           lead-white tinted with naples yellow, warm ivory rather than pure
           white.  This cream push (R + slight G) warms the brightest peaks
           away from dead-white, giving them the luminous quality of sunlit
           porcelain.

        3. **Warm brownish-red in deep shadows** (low-luminance band):
           Unlike Northern painters who let shadows go cool and grey, Rubens'
           shadows glow with brownish-red transmitted light, as though the
           figure were lit from within.  A subtle R boost and B reduction in
           the darkest zones reproduces this quality without lifting the overall
           shadow depth.

        All three adjustments are blended back at `opacity` so the original
        canvas reading is preserved beneath the tonal shift.

        Parameters
        ----------
        blush_strength   : peak strength of the rosy blush tint in mid-tones
        cream_strength   : ivory warmth pushed into highlight peaks
        warm_shadow      : brownish-red glow added to deep shadow pixels
        blush_lo         : lower luminance bound for the blush zone
        blush_hi         : upper luminance bound for the blush zone
        highlight_thresh : luminance above which cream push begins
        shadow_thresh    : luminance below which warm shadow begins
        opacity          : global blend weight of the entire adjustment layer
        """
        import numpy as _np

        print(f"  Rubens flesh-vitality pass  "
              f"(blush={blush_strength:.2f}  cream={cream_strength:.2f}  "
              f"warm_shadow={warm_shadow:.2f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Rubens flesh-vitality pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA channel order: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Luminance ────────────────────────────────────────────────────────
        lum = 0.299 * r_f + 0.587 * g_f + 0.114 * b_f

        # ── 1. Rosy blush — mid-luminance thin-skin zones ────────────────────
        # A sine ramp peaks at the centre of the blush band and fades to zero
        # at both boundaries, giving a smooth, anatomically convincing taper.
        blush_range = max(blush_hi - blush_lo, 1e-6)
        blush_t     = _np.clip((lum - blush_lo) / blush_range, 0.0, 1.0)
        blush_scale = _np.sin(_np.pi * blush_t)   # 0 at edges, 1 at centre
        blush_mask  = (lum >= blush_lo) & (lum <= blush_hi)

        r_out = _np.where(blush_mask,
                          _np.clip(r_f + blush_strength * blush_scale, 0.0, 1.0),
                          r_f)
        g_out = _np.where(blush_mask,
                          _np.clip(g_f - blush_strength * 0.30 * blush_scale, 0.0, 1.0),
                          g_f)
        b_out = _np.where(blush_mask,
                          _np.clip(b_f - blush_strength * 0.50 * blush_scale, 0.0, 1.0),
                          b_f)

        # ── 2. Cream-ivory push at highlight peaks ───────────────────────────
        # Ramp from zero at highlight_thresh to full at lum=1.0.
        hi_mask = lum > highlight_thresh
        hi_ramp = _np.where(hi_mask,
                            _np.clip((lum - highlight_thresh)
                                     / (1.0 - highlight_thresh + 1e-6), 0.0, 1.0),
                            0.0)
        r_out = _np.where(hi_mask,
                          _np.clip(r_out + cream_strength * hi_ramp, 0.0, 1.0),
                          r_out)
        g_out = _np.where(hi_mask,
                          _np.clip(g_out + cream_strength * 0.85 * hi_ramp, 0.0, 1.0),
                          g_out)
        # Blue is left unchanged at highlights — warm ivory keeps its warmth.

        # ── 3. Warm brownish-red undertone in deep shadows ───────────────────
        # Ramp from zero at shadow_thresh down to full at lum=0.
        sh_mask = lum < shadow_thresh
        sh_ramp = _np.where(sh_mask,
                            _np.clip((shadow_thresh - lum)
                                     / (shadow_thresh + 1e-6), 0.0, 1.0),
                            0.0)
        r_out = _np.where(sh_mask,
                          _np.clip(r_out + warm_shadow * sh_ramp, 0.0, 1.0),
                          r_out)
        b_out = _np.where(sh_mask,
                          _np.clip(b_out - warm_shadow * 0.70 * sh_ramp, 0.0, 1.0),
                          b_out)

        # ── Blend adjusted layer back at `opacity` ───────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        print(f"    Rubens flesh-vitality pass complete")

    # ─────────────────────────────────────────────────────────────────────────
    # Poussin classical-clarity pass — Nicolas Poussin / French Classicism
    # ─────────────────────────────────────────────────────────────────────────

    def poussin_classical_clarity_pass(
            self,
            shadow_cool:      float = 0.12,
            midtone_lift:     float = 0.06,
            saturation_cap:   float = 0.72,
            highlight_ivory:  float = 0.05,
            shadow_thresh:    float = 0.32,
            highlight_thresh: float = 0.72,
            midtone_lo:       float = 0.32,
            midtone_hi:       float = 0.68,
            opacity:          float = 0.80,
    ):
        """
        Poussin classical-clarity pass — inspired by Nicolas Poussin (1594–1665).

        Nicolas Poussin built his paintings on deliberate chromatic principles
        that distinguished his work from the warm Baroque tradition around him.
        While Rubens, Rembrandt, and Caravaggio all used warm, earthy shadows,
        Poussin's shadow areas carry a silvery blue-grey quality derived from
        his close study of classical marble sculpture in Rome.  This pass
        approximates three of his defining technical signatures:

        1. **Cool, silver-grey shadows** — Poussin's shadows read as though cast
           from marble rather than lit by warm transmitted firelight.  Here we
           apply a cool blue-grey push to the darkest luminance zone (boost B,
           damp R), whose strength ramps from maximum at lum=0 down to zero at
           ``shadow_thresh``.  The result is the characteristic silvery depth
           that separates Poussin from every warm-Baroque painter of his era.

        2. **Mid-tone clarification — opening the tonal structure** — Poussin
           organised his compositions into clear, readable tonal triads (lights,
           mid-tones, darks) with crisp transitions between them.  His mid-tones
           are deliberately lifted away from the shadow zone, giving the painting
           an architectural clarity — every zone is legible from across a room.
           A sine ramp peaks at the centre of the mid-tone band
           (``midtone_lo``..``midtone_hi``) and proportionally lifts all three
           channels (preserving hue while opening value).

        3. **Cool ivory highlights** — His highest lights have a subtle blue-ivory
           quality, influenced by the cool reflected light of marble and plaster
           casts, rather than the warm lead-white cream of Rubens or the pure
           cadmium white of Academic painting.  A linear ramp applies a slight
           B boost and mild R damp above ``highlight_thresh``.

        4. **Saturation discipline** — Poussin's palette is radiant but never
           garish.  No single colour dominates; every hue is placed in a tonal
           context that gives it value without allowing it to overwhelm the whole.
           This step caps HSV saturation at ``saturation_cap`` for any pixel
           whose saturation exceeds that value, reducing chroma toward achromatic
           while preserving hue and value.

        All four adjustments are blended back at ``opacity`` so the original
        canvas reading is preserved beneath the chromatic correction.

        Parameters
        ----------
        shadow_cool      : strength of the blue-grey cool push in deep shadows
        midtone_lift     : fractional luminance lift at the centre of the
                          mid-tone band (0 = no lift, 0.10 = 10% value gain)
        saturation_cap   : maximum HSV saturation allowed after the pass
                          (1.0 = no capping; 0.70 = cap vivid pixels to 70%)
        highlight_ivory  : strength of the cool ivory push at highlight peaks
        shadow_thresh    : luminance below which the shadow-cool push is applied
        highlight_thresh : luminance above which the highlight-ivory push begins
        midtone_lo       : lower luminance bound of the mid-tone clarification
        midtone_hi       : upper luminance bound of the mid-tone clarification
        opacity          : global blend weight of the entire adjustment layer
                          (0 = noop, 1 = full replacement)

        Notes
        -----
        Call this AFTER the main style passes and BEFORE the final glaze/finish.
        Particularly effective after block_in() and build_form() on a painting
        that reads as too warm or too Baroque — it corrects the tonal register
        toward Poussin's architectural classical clarity without removing the
        underlying paint structure.

        Famous works to study:
          *Et in Arcadia Ego* (c. 1637–1638, Louvre) — definitive azure/vermilion
          triad, cool marble-grey shadows, crystalline Arcadian light.
          *The Holy Family on the Steps* (1648, Cleveland) — exemplary mid-tone
          clarification: light, mid-tone, and shadow read as three distinct zones.
          *A Dance to the Music of Time* (c. 1634–36, Wallace Collection) — the
          cool silver-blue of the sky flows into the shadow sides of the figures.
        """
        import numpy as _np

        print(f"  Poussin classical-clarity pass  "
              f"(shadow_cool={shadow_cool:.2f}  midtone_lift={midtone_lift:.2f}  "
              f"sat_cap={saturation_cap:.2f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Poussin classical-clarity pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA channel order: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Luminance ────────────────────────────────────────────────────────
        lum = 0.299 * r_f + 0.587 * g_f + 0.114 * b_f

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── 1. Cool silver-grey push in deep shadows ─────────────────────────
        # Ramp from full at lum=0 down to zero at shadow_thresh.
        # Cool push: boost B, damp R — marble-shadow quality.
        sh_mask = lum < shadow_thresh
        sh_ramp = _np.where(sh_mask,
                            _np.clip((shadow_thresh - lum)
                                     / (shadow_thresh + 1e-6), 0.0, 1.0),
                            0.0)
        r_out = _np.where(sh_mask,
                          _np.clip(r_out - shadow_cool * 0.50 * sh_ramp, 0.0, 1.0),
                          r_out)
        b_out = _np.where(sh_mask,
                          _np.clip(b_out + shadow_cool * 0.60 * sh_ramp, 0.0, 1.0),
                          b_out)

        # ── 2. Mid-tone clarification — open the tonal structure ─────────────
        # A sine ramp peaks at the centre of the mid-tone band.
        # Lift all channels proportionally (preserves hue; opens value).
        mt_range = max(midtone_hi - midtone_lo, 1e-6)
        mt_t     = _np.clip((lum - midtone_lo) / mt_range, 0.0, 1.0)
        mt_scale = _np.sin(_np.pi * mt_t)   # 0 at band edges, 1 at centre
        mt_mask  = (lum >= midtone_lo) & (lum <= midtone_hi)

        lift = 1.0 + midtone_lift * mt_scale
        r_out = _np.where(mt_mask, _np.clip(r_out * lift, 0.0, 1.0), r_out)
        g_out = _np.where(mt_mask, _np.clip(g_out * lift, 0.0, 1.0), g_out)
        b_out = _np.where(mt_mask, _np.clip(b_out * lift, 0.0, 1.0), b_out)

        # ── 3. Cool ivory push at highlight peaks ────────────────────────────
        # Linear ramp from zero at highlight_thresh to full at lum=1.0.
        # Cool ivory: slight B boost, minor R damp (marble-reflected-light quality).
        hi_mask = lum > highlight_thresh
        hi_ramp = _np.where(hi_mask,
                            _np.clip((lum - highlight_thresh)
                                     / (1.0 - highlight_thresh + 1e-6), 0.0, 1.0),
                            0.0)
        r_out = _np.where(hi_mask,
                          _np.clip(r_out - highlight_ivory * 0.40 * hi_ramp, 0.0, 1.0),
                          r_out)
        b_out = _np.where(hi_mask,
                          _np.clip(b_out + highlight_ivory * 0.35 * hi_ramp, 0.0, 1.0),
                          b_out)

        # ── 4. Saturation discipline — cap over-vivid pixels ─────────────────
        # Vectorised HSV saturation capping.
        # For each pixel: sat = (max_c - min_c) / max_c.
        # If sat > saturation_cap, scale the non-max channels toward max_c
        # (reduce chroma without changing value or hue).
        max_c  = _np.maximum(_np.maximum(r_out, g_out), b_out)   # value
        min_c  = _np.minimum(_np.minimum(r_out, g_out), b_out)
        chroma = max_c - min_c

        sat  = _np.where(max_c > 1e-6, chroma / max_c, 0.0)
        over = sat > saturation_cap

        # Scale factor: new_chroma = max_c * saturation_cap → scale = new/old
        # Use safe_chroma to avoid a div-by-zero runtime warning from numpy's
        # vectorised evaluation (np.where evaluates both branches before selecting).
        new_chroma  = max_c * saturation_cap
        safe_chroma = _np.where(chroma > 1e-6, chroma, 1.0)
        scale = _np.where(over & (chroma > 1e-6), new_chroma / safe_chroma, 1.0)

        # Each channel: new_ch = max_c - (max_c - old_ch) * scale
        r_out = _np.where(over, _np.clip(max_c - (max_c - r_out) * scale, 0.0, 1.0), r_out)
        g_out = _np.where(over, _np.clip(max_c - (max_c - g_out) * scale, 0.0, 1.0), g_out)
        b_out = _np.where(over, _np.clip(max_c - (max_c - b_out) * scale, 0.0, 1.0), b_out)

        # ── Blend adjusted layer back at `opacity` ───────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        n_shadow    = int(sh_mask.sum())
        n_midtone   = int(mt_mask.sum())
        n_highlight = int(hi_mask.sum())
        n_over_sat  = int(over.sum())
        print(f"    Poussin classical-clarity pass complete  "
              f"(shadow={n_shadow}px  midtone={n_midtone}px  "
              f"highlight={n_highlight}px  sat-capped={n_over_sat}px)")

    # ─────────────────────────────────────────────────────────────────────────
    # Gainsborough feathery pass — Thomas Gainsborough / British Rococo Portrait
    # ─────────────────────────────────────────────────────────────────────────

    def gainsborough_feathery_pass(
            self,
            silver_strength:  float = 0.10,
            feather_spread:   float = 2.5,
            shimmer_strength: float = 0.04,
            shadow_haze:      float = 0.06,
            highlight_thresh: float = 0.68,
            midtone_lo:       float = 0.30,
            midtone_hi:       float = 0.72,
            shadow_thresh:    float = 0.35,
            opacity:          float = 0.78,
    ):
        """
        Gainsborough feathery pass — inspired by Thomas Gainsborough (1727–1788).

        Thomas Gainsborough was the supreme British portrait and landscape painter
        of the 18th century.  He worked in direct competition with Sir Joshua
        Reynolds — while Reynolds favoured warm academic flesh tones and grand
        classical gravity, Gainsborough's answer was silvery lightness: cool,
        feathery, alive with atmospheric breath.

        This pass approximates three of his defining technical signatures:

        1. **Cool silver-blue highlights** — Gainsborough's brightest lights lean
           toward a cool blue-white silver rather than warm ivory or cream.  He
           admired Van Dyck's pearl-grey silk passages and carried that quality
           into his flesh, drapery, and sky.  Here we apply a gentle B-channel
           boost and slight R damp above ``highlight_thresh``, ramping linearly
           to full strength at lum=1.0.

        2. **Feathery edge dissolution** — His most iconic quality.  Using
           long flexible brushes held at arm's length, each mark ended in a
           broken, tapered "feather" that dissolved into the surrounding paint
           before it dried.  We approximate this by detecting edge zones with a
           Sobel magnitude map, then applying a directional Gaussian blur along
           the edge gradient perpendicular (across the edge, not along it).
           The result is the characteristic soft dissolution of a figure's
           silhouette into its background — without losing the interior
           structure of the form.

        3. **Fluid midtone shimmer** — He applied paint in very thin, liquid
           layers that would almost run on the canvas.  In mid-tone areas this
           produces a subtle horizontal streaming quality — as if the paint
           is still in motion.  We simulate this with a stochastic horizontal
           scatter: for each mid-luminance pixel, a small random R/B offset is
           sampled from its neighbourhood along the horizontal axis, adding the
           optical sense of a fresh, fluid brushstroke that has not yet set.

        4. **Cool atmospheric background haze** — Gainsborough always united
           his sitter and landscape into one atmospheric world.  Shadow areas
           receive a subtle B boost and slight R damp, pushing them toward the
           cool blue-grey of an English cloudy sky.  This is most effective in
           the periphery of the composition where the background sits.

        All four adjustments are composited back at ``opacity`` so the original
        canvas reading is preserved beneath the tonal shifts.

        Parameters
        ----------
        silver_strength  : strength of the cool silver push in highlights
        feather_spread   : Gaussian sigma (pixels) for the edge feathering blur
        shimmer_strength : amplitude of the horizontal fluid shimmer in midtones
        shadow_haze      : strength of the cool atmospheric push in shadows
        highlight_thresh : luminance above which the silver push begins
        midtone_lo       : lower luminance bound of the shimmer zone
        midtone_hi       : upper luminance bound of the shimmer zone
        shadow_thresh    : luminance below which the atmospheric haze begins
        opacity          : global blend weight of the entire adjustment layer
                          (0 = noop, 1 = full replacement)

        Notes
        -----
        Call this AFTER the main style passes and BEFORE the final glaze/finish.
        Particularly effective on warm-fleshed portraits that need the cool
        British atmosphere added without removing the underlying painterly warmth.

        Famous works to study:
          *The Blue Boy* (c. 1770, Huntington Library) — his most celebrated
          portrait; the cool silver-blue of the suit reads against a warm
          autumnal landscape background, demonstrating his mastery of warm-cool
          simultaneous contrast.
          *Mrs. Richard Brinsley Sheridan* (1785–87, National Gallery of Art,
          Washington) — the feathery dissolution of her hair and dress into the
          landscape background is the quintessential Gainsborough edge quality.
          *The Morning Walk* (1785, National Gallery) — the cool silver of her
          dress and his coat unified with the sky through atmospheric feathering.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gauss

        print(f"  Gainsborough feathery pass  "
              f"(silver={silver_strength:.2f}  feather_spread={feather_spread:.1f}  "
              f"shimmer={shimmer_strength:.2f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Gainsborough feathery pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA channel order: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Luminance ────────────────────────────────────────────────────────
        lum = 0.299 * r_f + 0.587 * g_f + 0.114 * b_f

        # ── 1. Cool silver-blue push in highlights ───────────────────────────
        # Linear ramp from zero at highlight_thresh to full at lum=1.0.
        # Silver push: boost B, damp R — pearl-grey quality Gainsborough
        # learned from studying Van Dyck's silk passages.
        hi_mask = lum > highlight_thresh
        hi_ramp = _np.where(hi_mask,
                            _np.clip((lum - highlight_thresh)
                                     / (1.0 - highlight_thresh + 1e-6), 0.0, 1.0),
                            0.0)
        r_out = _np.where(hi_mask,
                          _np.clip(r_out - silver_strength * 0.45 * hi_ramp, 0.0, 1.0),
                          r_out)
        b_out = _np.where(hi_mask,
                          _np.clip(b_out + silver_strength * 0.55 * hi_ramp, 0.0, 1.0),
                          b_out)

        # ── 2. Feathery edge dissolution ──────────────────────────────────────
        # Detect edges via Sobel gradient magnitude, then apply a
        # cross-edge Gaussian blur proportional to edge strength.
        # The blur is applied independently per channel so colour at
        # the edge bleeds laterally — simulating the tapered "feather"
        # where the final stroke tip breaks and dissolves.
        if feather_spread > 0.1:
            # Luminance Sobel for edge detection
            sobel_x = _np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                                 dtype=_np.float32)
            sobel_y = _np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
                                 dtype=_np.float32)
            from scipy.ndimage import convolve as _conv
            gx = _conv(lum, sobel_x, mode='reflect')
            gy = _conv(lum, sobel_y, mode='reflect')
            edge_mag = _np.sqrt(gx * gx + gy * gy)
            edge_mag = _np.clip(edge_mag / (edge_mag.max() + 1e-6), 0.0, 1.0)

            # Blurred versions of each channel
            r_blurred = _gauss(r_out, sigma=feather_spread, mode='reflect')
            g_blurred = _gauss(g_out, sigma=feather_spread, mode='reflect')
            b_blurred = _gauss(b_out, sigma=feather_spread, mode='reflect')

            # Blend sharpened vs. blurred based on edge strength —
            # strong edges dissolve most; interior stays crisp.
            feather_w = _np.clip(edge_mag * 0.80, 0.0, 1.0)
            r_out = r_out * (1.0 - feather_w) + r_blurred * feather_w
            g_out = g_out * (1.0 - feather_w) + g_blurred * feather_w
            b_out = b_out * (1.0 - feather_w) + b_blurred * feather_w

        # ── 3. Fluid midtone shimmer ─────────────────────────────────────────
        # For each mid-luminance pixel, replace its R and B with a value
        # sampled from a small horizontal neighbourhood (±4px), weighted by
        # a random shift.  This mimics the optical streaming quality of very
        # thin, liquid oil paint that has not fully set — a horizontal
        # "aliveness" in the mid-tones.
        if shimmer_strength > 0.0:
            # Build shifted versions ±3px horizontally
            shift_l = _np.roll(r_f, -3, axis=1)   # left shift
            shift_r = _np.roll(r_f,  3, axis=1)   # right shift
            shift_bl = _np.roll(b_f, -3, axis=1)
            shift_br = _np.roll(b_f,  3, axis=1)

            # Random per-pixel blend weights in midtone zone
            rng_arr = _np.random.RandomState(42).uniform(
                0.0, shimmer_strength, size=(h, w)).astype(_np.float32)

            mt_mask = (lum >= midtone_lo) & (lum <= midtone_hi)
            mt_ramp = _np.zeros((h, w), dtype=_np.float32)
            mt_range = max(midtone_hi - midtone_lo, 1e-6)
            mt_t = _np.clip((lum - midtone_lo) / mt_range, 0.0, 1.0)
            mt_ramp = _np.where(mt_mask, _np.sin(_np.pi * mt_t), 0.0)

            # Blend the shifted samples in at shimmer weight
            shimmer_r = (shift_l + shift_r) * 0.5
            shimmer_b = (shift_bl + shift_br) * 0.5
            w_mt = rng_arr * mt_ramp
            r_out = _np.clip(r_out * (1.0 - w_mt) + shimmer_r * w_mt, 0.0, 1.0)
            b_out = _np.clip(b_out * (1.0 - w_mt) + shimmer_b * w_mt, 0.0, 1.0)

        # ── 4. Cool atmospheric haze in shadows ──────────────────────────────
        # Ramp from full at lum=0 down to zero at shadow_thresh.
        # Cool haze: boost B, damp R — English cloudy-sky quality in shadows.
        sh_mask = lum < shadow_thresh
        sh_ramp = _np.where(sh_mask,
                            _np.clip((shadow_thresh - lum)
                                     / (shadow_thresh + 1e-6), 0.0, 1.0),
                            0.0)
        r_out = _np.where(sh_mask,
                          _np.clip(r_out - shadow_haze * 0.50 * sh_ramp, 0.0, 1.0),
                          r_out)
        b_out = _np.where(sh_mask,
                          _np.clip(b_out + shadow_haze * 0.60 * sh_ramp, 0.0, 1.0),
                          b_out)

        # ── Blend adjusted layer back at `opacity` ───────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        n_highlight = int(hi_mask.sum())
        n_shadow    = int(sh_mask.sum())
        n_midtone   = int(mt_mask.sum()) if shimmer_strength > 0.0 else 0
        print(f"    Gainsborough feathery pass complete  "
              f"(highlight={n_highlight}px  midtone={n_midtone}px  "
              f"shadow={n_shadow}px)")

    # ─────────────────────────────────────────────────────────────────────────
    # homer_marine_clarity_pass — Winslow Homer American Realism / Marine
    # ─────────────────────────────────────────────────────────────────────────

    def homer_marine_clarity_pass(
        self,
        *,
        highlight_lift: float = 0.12,
        shadow_cool: float = 0.10,
        contrast_strength: float = 0.08,
        wash_luminosity: float = 0.06,
        highlight_thresh: float = 0.72,
        shadow_thresh: float = 0.35,
        opacity: float = 0.72,
    ) -> None:
        """
        Winslow Homer marine clarity pass (session 41 artist pass).

        Homer's Atlantic seascapes and genre paintings are defined by four
        qualities that this pass approximates:

        1. **Brilliant maritime highlight lift** — Near-white light striking
           wave crests, sails, and lit figure tops is pushed higher and
           slightly warmer (warm ivory, not the cool silver of Gainsborough).
           R and G channels lift proportionally in the brightest zone, giving
           the sensation of glittering Atlantic noon-sun.

        2. **Cool Prussian shadow** — Shadow zones receive a strong B boost
           and R damp, pushing them toward the deep slate-blue of the North
           Atlantic in overcast weather.  Homer's shadows are cold and deep —
           the opposite of Rembrandt's warm amber shadow glow.

        3. **Tonal contrast push** — Homer separated light from dark decisively
           (inspired by Japanese woodblock prints).  A gentle S-curve is applied
           to the luminance channel: values above the midpoint are lifted, values
           below are pushed down, increasing the tonal spread without clipping.

        4. **Transparent wash luminosity** — In the light and midtone zones,
           the paint is treated as though it were thin watercolour over a white
           ground: saturation is very slightly reduced (transparent pigment reads
           less saturated than opaque body colour) and luminance is lifted subtly
           to simulate the ground glowing through the pigment film.

        All four adjustments composite back at ``opacity`` over the original
        canvas, preserving the underlying painterly layer beneath.

        Parameters
        ----------
        highlight_lift     : strength of the warm ivory push in highlights
        shadow_cool        : strength of the cool Prussian push in shadows
        contrast_strength  : amplitude of the tonal S-curve contrast boost
        wash_luminosity    : luminance lift in the midtone / light zones
        highlight_thresh   : luminance above which the highlight lift begins
        shadow_thresh      : luminance below which the cool shadow push begins
        opacity            : global blend weight of the entire adjustment
                             (0 = noop, 1 = full replacement)

        Notes
        -----
        Call this AFTER the main style passes and BEFORE the final glaze/finish.
        Most effective on paintings with a near-white ground where the white
        support is already contributing luminosity through thin paint layers.

        Famous works to study:
          *Breezing Up (A Fair Wind)* (1876, National Gallery of Art) — his
          most beloved oil; the warm ivory of the sails against the cool
          blue-green sea is the definitive Homer warm-cool contrast.
          *The Life Line* (1884, Philadelphia Museum of Art) — the orange
          rescue line against stormy blue-grey sea; tonal clarity at its peak.
          *Fog Warning* (1885, MFA Boston) — a lone fisherman in a dory,
          fog-grey distance, the sea almost black in the near-field troughs.
        """
        import numpy as _np

        print(f"  Homer marine clarity pass  "
              f"(highlight_lift={highlight_lift:.2f}  shadow_cool={shadow_cool:.2f}  "
              f"contrast={contrast_strength:.2f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Homer marine clarity pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA channel order: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Luminance ─────────────────────────────────────────────────────────
        lum = 0.299 * r_f + 0.587 * g_f + 0.114 * b_f

        # ── 1. Brilliant maritime highlight lift ──────────────────────────────
        # Linear ramp from zero at highlight_thresh to full at lum=1.0.
        # Warm ivory push: lift R and G (warm white), slightly boost B less —
        # maritime noon light is warm, not the cool silver of northern European sky.
        hi_mask = lum > highlight_thresh
        hi_ramp = _np.where(hi_mask,
                            _np.clip((lum - highlight_thresh)
                                     / (1.0 - highlight_thresh + 1e-6), 0.0, 1.0),
                            0.0)
        r_out = _np.where(hi_mask,
                          _np.clip(r_out + highlight_lift * 0.55 * hi_ramp, 0.0, 1.0),
                          r_out)
        g_out = _np.where(hi_mask,
                          _np.clip(g_out + highlight_lift * 0.40 * hi_ramp, 0.0, 1.0),
                          g_out)
        b_out = _np.where(hi_mask,
                          _np.clip(b_out + highlight_lift * 0.15 * hi_ramp, 0.0, 1.0),
                          b_out)

        # ── 2. Cool Prussian shadow push ──────────────────────────────────────
        # Ramp from full at lum=0 down to zero at shadow_thresh.
        # Atlantic cold: strong B boost, damp R — the opposite of warm Baroque shadow.
        sh_mask = lum < shadow_thresh
        sh_ramp = _np.where(sh_mask,
                            _np.clip((shadow_thresh - lum)
                                     / (shadow_thresh + 1e-6), 0.0, 1.0),
                            0.0)
        r_out = _np.where(sh_mask,
                          _np.clip(r_out - shadow_cool * 0.55 * sh_ramp, 0.0, 1.0),
                          r_out)
        b_out = _np.where(sh_mask,
                          _np.clip(b_out + shadow_cool * 0.65 * sh_ramp, 0.0, 1.0),
                          b_out)

        # ── 3. Tonal contrast S-curve ─────────────────────────────────────────
        # Simple cubic S-curve centred at 0.5:
        #   lum_new = lum + contrast_strength * sin(pi * lum) * (lum - 0.5)
        # Pixels above 0.5 lift; pixels below 0.5 drop.
        # Applied to all channels proportionally (preserves hue).
        s_curve = contrast_strength * _np.sin(_np.pi * lum) * (lum - 0.5)
        r_out = _np.clip(r_out + s_curve, 0.0, 1.0)
        g_out = _np.clip(g_out + s_curve, 0.0, 1.0)
        b_out = _np.clip(b_out + s_curve, 0.0, 1.0)

        # ── 4. Transparent wash luminosity in midtones / lights ───────────────
        # For pixels above shadow_thresh (mid-to-bright zone), apply a small
        # luminance lift simulating thin transparent pigment over a white ground.
        # The lift is proportional to distance from shadow_thresh — darkest
        # midtones get the least lift; highlights already lifted in step 1.
        wash_zone = lum >= shadow_thresh
        wash_ramp = _np.where(wash_zone,
                              _np.clip((lum - shadow_thresh)
                                       / (1.0 - shadow_thresh + 1e-6) * 0.60,
                                       0.0, 1.0),
                              0.0)
        lift = wash_luminosity * wash_ramp
        r_out = _np.clip(r_out + lift, 0.0, 1.0)
        g_out = _np.clip(g_out + lift, 0.0, 1.0)
        b_out = _np.clip(b_out + lift, 0.0, 1.0)

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        n_highlight = int(hi_mask.sum())
        n_shadow    = int(sh_mask.sum())
        print(f"    Homer marine clarity pass complete  "
              f"(highlight={n_highlight}px  shadow={n_shadow}px)")

    # ─────────────────────────────────────────────────────────────────────────
    # fragonard_bravura_pass — session 42 artist pass
    # ─────────────────────────────────────────────────────────────────────────

    def fragonard_bravura_pass(
        self,
        *,
        warmth_strength: float = 0.08,
        highlight_bloom: float = 0.06,
        shadow_warm: float = 0.05,
        highlight_thresh: float = 0.65,
        shadow_thresh: float = 0.30,
        opacity: float = 0.70,
    ) -> None:
        """
        Jean-Honoré Fragonard bravura pass (session 42 artist pass).

        Fragonard's French Rococo canvases are defined by three tonal qualities
        that this pass approximates:

        1. **Warm highlight bloom** — In bright zones (lum > highlight_thresh),
           highlights are pushed toward a creamy warm tone rather than the cool
           silver of northern European painting.  R and G channels lift; B is
           gently boosted only slightly (warm cream, not cold white).  This
           gives the sensation of afternoon garden light striking silk and flesh
           rather than cold studio daylight.

        2. **Rosy peach midtone warmth** — In the middle zone
           (shadow_thresh ≤ lum ≤ highlight_thresh), a gentle warmth push
           toward peach-rose is applied: R lifts slightly, B is subtly damped.
           Fragonard's flesh tones are warm and rosy — not the cool ivory of
           Academic painting, not the amber of Rembrandt, but a light garden-
           afternoon peach.

        3. **Warm shadow damping** — In shadow zones (lum < shadow_thresh),
           any cool blue is gently damped and R is slightly boosted, keeping
           shadows in warm umber-brown territory.  Fragonard's shadows are warm
           throughout — the contrast in his work is light warm versus dark warm,
           never the warm-light/cool-shadow convention of Academic Realism.

        All three adjustments composite back at ``opacity`` over the original
        canvas, preserving the underlying painterly layer.

        Parameters
        ----------
        warmth_strength   : strength of the rose-peach push in midtones
        highlight_bloom   : extra warm-cream boost in highlight zones
        shadow_warm       : strength of the warm shadow damping (reduces B in darks)
        highlight_thresh  : luminance above which highlight bloom begins
        shadow_thresh     : luminance below which shadow warmth applies
        opacity           : global blend weight of the entire adjustment
                            (0 = noop, 1 = full replacement)

        Notes
        -----
        Call this AFTER the main style passes and BEFORE the final glaze/finish.
        Pairs well with a warm honey-amber glaze (0.88, 0.78, 0.62) applied after.

        Famous works to study:
          *The Swing* (1767, Wallace Collection, London) — the definitive
          Fragonard; the pink-silk dress and foliage are lit with warm cream-
          gold afternoon sun; shadows are warm leafy green-umber, never cool.
          *Young Girl Reading* (c. 1776, National Gallery of Art, Washington) —
          the yellow dress in warm afternoon light; a masterclass in warm
          highlight and warm shadow coexisting without any cool tone.
          *The Bathers* (c. 1765, Louvre) — luminous rose-cream flesh bathed in
          dappled warm light; the water shadows are warm olive, not cool blue.
        """
        import numpy as _np

        print(f"  Fragonard bravura pass  "
              f"(warmth={warmth_strength:.2f}  hi_bloom={highlight_bloom:.2f}  "
              f"shadow_warm={shadow_warm:.2f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Fragonard bravura pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA channel order: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Luminance ─────────────────────────────────────────────────────────
        lum = 0.299 * r_f + 0.587 * g_f + 0.114 * b_f

        # ── 1. Warm highlight bloom ───────────────────────────────────────────
        # Linear ramp from zero at highlight_thresh to full at lum=1.0.
        # Push toward warm cream: R lifts most, G lifts moderately, B lifts
        # just slightly — creamy warm, not silvery cool.
        hi_mask = lum > highlight_thresh
        hi_ramp = _np.where(hi_mask,
                            _np.clip((lum - highlight_thresh)
                                     / (1.0 - highlight_thresh + 1e-6), 0.0, 1.0),
                            0.0)
        r_out = _np.where(hi_mask,
                          _np.clip(r_out + highlight_bloom * 0.70 * hi_ramp, 0.0, 1.0),
                          r_out)
        g_out = _np.where(hi_mask,
                          _np.clip(g_out + highlight_bloom * 0.50 * hi_ramp, 0.0, 1.0),
                          g_out)
        b_out = _np.where(hi_mask,
                          _np.clip(b_out + highlight_bloom * 0.20 * hi_ramp, 0.0, 1.0),
                          b_out)

        # ── 2. Rosy peach midtone warmth ─────────────────────────────────────
        # The midtone band: shadow_thresh ≤ lum ≤ highlight_thresh.
        # Gently warm toward peach-rose: lift R, damp B slightly.
        mid_mask = (lum >= shadow_thresh) & (lum <= highlight_thresh)
        # Weight peaks at the centre of the midtone band, tapering to zero at edges.
        mid_centre = (shadow_thresh + highlight_thresh) * 0.5
        mid_half   = (highlight_thresh - shadow_thresh) * 0.5 + 1e-6
        mid_weight = _np.where(mid_mask,
                               1.0 - _np.abs(lum - mid_centre) / mid_half,
                               0.0)
        r_out = _np.where(mid_mask,
                          _np.clip(r_out + warmth_strength * 0.55 * mid_weight, 0.0, 1.0),
                          r_out)
        b_out = _np.where(mid_mask,
                          _np.clip(b_out - warmth_strength * 0.30 * mid_weight, 0.0, 1.0),
                          b_out)

        # ── 3. Warm shadow damping ────────────────────────────────────────────
        # In shadows (lum < shadow_thresh): slightly boost R, damp B.
        # This keeps Fragonard's shadows warm umber-brown rather than cool Prussian.
        sh_mask = lum < shadow_thresh
        sh_ramp = _np.where(sh_mask,
                            _np.clip((shadow_thresh - lum)
                                     / (shadow_thresh + 1e-6), 0.0, 1.0),
                            0.0)
        r_out = _np.where(sh_mask,
                          _np.clip(r_out + shadow_warm * 0.40 * sh_ramp, 0.0, 1.0),
                          r_out)
        b_out = _np.where(sh_mask,
                          _np.clip(b_out - shadow_warm * 0.45 * sh_ramp, 0.0, 1.0),
                          b_out)

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        n_highlight = int(hi_mask.sum())
        n_midtone   = int(mid_mask.sum())
        n_shadow    = int(sh_mask.sum())
        print(f"    Fragonard bravura pass complete  "
              f"(highlight={n_highlight}px  midtone={n_midtone}px  shadow={n_shadow}px)")

    # ─────────────────────────────────────────────────────────────────────────
    # renoir_luminous_warmth_pass — Pierre-Auguste Renoir artist pass
    # ─────────────────────────────────────────────────────────────────────────

    def renoir_luminous_warmth_pass(
        self,
        *,
        saturation_boost: float = 0.18,
        rose_warmth: float = 0.07,
        highlight_glow: float = 0.06,
        highlight_thresh: float = 0.62,
        shadow_thresh: float = 0.28,
        opacity: float = 0.72,
    ) -> None:
        """
        Pierre-Auguste Renoir luminous warmth pass (artist pass).

        Renoir's French Impressionist canvases are defined by three tonal qualities
        that this pass approximates:

        1. **Chromatic saturation boost** — Renoir's palette runs at maximum
           luminous intensity across all hue zones.  The saturation of every
           non-shadow pixel is lifted toward full chroma, giving the canvas its
           characteristic vivid, jewel-like quality.  The boost is strongest in
           the midtone band (shadows and near-white highlights are less affected
           to avoid cartoon-like oversaturation).

        2. **Rose-peach midtone warmth** — In the midtone band
           (shadow_thresh ≤ lum ≤ highlight_thresh), R is lifted and B is
           gently damped, pushing toward Renoir's signature warm rose-peach.
           He explicitly rejected the Impressionist convention of cool violet
           shadows; his darks remain warm throughout.

        3. **Luminous warm highlight glow** — In bright zones
           (lum > highlight_thresh), highlights are pushed toward a warm
           cream-gold tone: R and G lift, B lifts only slightly.  This replicates
           the characteristic Renoir bloom — warm afternoon sunlight striking
           white lace, pale skin, or gleaming hair — as opposed to the cool
           silver of Northern European painting.

        All three adjustments composite back at ``opacity`` over the original
        canvas, preserving the underlying painterly layer structure.

        Parameters
        ----------
        saturation_boost : how much saturation is lifted in mid-lum zones
                           (0 = no change, 1 = full saturation clamp at 1.0)
        rose_warmth      : strength of the rose-peach push in midtones
        highlight_glow   : warm-cream boost amplitude in highlight zones
        highlight_thresh : luminance above which highlight glow begins
        shadow_thresh    : luminance below which warm push tapers off
        opacity          : global blend weight of the entire adjustment
                           (0 = noop, 1 = full replacement)

        Notes
        -----
        Call this AFTER the main style passes (block_in, build_form) and
        BEFORE the final glaze/finish.  Pairs well with a warm peach-rose
        glaze (0.90, 0.72, 0.62) applied afterward.

        Famous works to study:
          *Dance at Le Moulin de la Galette* (1876, Musée d'Orsay) — dappled
          afternoon garden light; warm rose-cream skin dabs interleaved with
          cool blue-grey shadow strokes; saturation maximised throughout.
          *Luncheon of the Boating Party* (1880–1881, Phillips Collection) —
          the pink-cheeked faces and richly coloured drapery; warm golden light
          on every highlight; not a cool tone in the entire canvas.
          *Two Sisters (On the Terrace)* (1881, Art Institute of Chicago) —
          the warm spring green foliage and rose-peach flesh; highlights are
          cream-warm, shadows are warm ochre-umber; vivid chromatic punch.
        """
        import colorsys as _cs
        import numpy as _np

        print(f"  Renoir luminous warmth pass  "
              f"(sat_boost={saturation_boost:.2f}  warmth={rose_warmth:.2f}  "
              f"hi_glow={highlight_glow:.2f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Renoir luminous warmth pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA channel order: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Luminance ─────────────────────────────────────────────────────────
        lum = 0.299 * r_f + 0.587 * g_f + 0.114 * b_f

        # ── 1. Chromatic saturation boost ─────────────────────────────────────
        # Convert each pixel to HSV, lift S by saturation_boost, convert back.
        # The boost is weighted by a bell curve centred in the midtone band so
        # very dark shadows and near-white highlights are less affected.
        # We implement this with a fast vectorised HSV round-trip via colorsys
        # logic expressed as array operations (avoids slow per-pixel loops).

        # HSV conversion (vectorised):
        cmax = _np.maximum(_np.maximum(r_out, g_out), b_out)
        cmin = _np.minimum(_np.minimum(r_out, g_out), b_out)
        delta = cmax - cmin

        # Value (V) = cmax
        v_ch = cmax

        # Saturation (S) = delta / cmax  (0 when cmax == 0)
        s_ch = _np.where(cmax > 1e-6, delta / (cmax + 1e-6), 0.0)

        # Hue computation (6 segments)
        with _np.errstate(invalid='ignore', divide='ignore'):
            h_seg = _np.zeros_like(r_out)
            mask_r = (cmax == r_out) & (delta > 1e-6)
            mask_g = (cmax == g_out) & (delta > 1e-6)
            mask_b = (cmax == b_out) & (delta > 1e-6)
            h_seg = _np.where(
                mask_r,
                ((g_out - b_out) / (delta + 1e-6)) % 6.0,
                _np.where(
                    mask_g,
                    (b_out - r_out) / (delta + 1e-6) + 2.0,
                    _np.where(
                        mask_b,
                        (r_out - g_out) / (delta + 1e-6) + 4.0,
                        0.0)))
        h_ch = h_seg / 6.0  # normalise to [0, 1]

        # Saturation boost weight — peaks at the midtone centre, zero at extremes
        mid_centre = (shadow_thresh + highlight_thresh) * 0.5
        mid_half   = (highlight_thresh - shadow_thresh) * 0.5 + 1e-6
        sat_weight = _np.clip(1.0 - _np.abs(lum - mid_centre) / (mid_half * 1.4), 0.0, 1.0)
        s_new = _np.clip(s_ch + saturation_boost * sat_weight, 0.0, 1.0)

        # HSV → RGB back-conversion (vectorised)
        h6   = h_ch * 6.0
        i    = _np.floor(h6).astype(_np.int32) % 6
        f    = h6 - _np.floor(h6)
        p_v  = v_ch * (1.0 - s_new)
        q_v  = v_ch * (1.0 - s_new * f)
        t_v  = v_ch * (1.0 - s_new * (1.0 - f))

        r_sat = _np.select(
            [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
            [v_ch,   q_v,    p_v,    p_v,    t_v,    v_ch],
            default=r_out)
        g_sat = _np.select(
            [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
            [t_v,    v_ch,   v_ch,   q_v,    p_v,    p_v],
            default=g_out)
        b_sat = _np.select(
            [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
            [p_v,    p_v,    t_v,    v_ch,   v_ch,   q_v],
            default=b_out)

        # Where delta==0 (grey pixels), saturation boost has no effect — keep original
        grey_mask = delta < 1e-6
        r_out = _np.where(grey_mask, r_out, _np.clip(r_sat, 0.0, 1.0))
        g_out = _np.where(grey_mask, g_out, _np.clip(g_sat, 0.0, 1.0))
        b_out = _np.where(grey_mask, b_out, _np.clip(b_sat, 0.0, 1.0))

        # ── 2. Rose-peach midtone warmth ──────────────────────────────────────
        # In the midtone band: lift R toward rose-peach, damp B slightly.
        # Weight peaks at the midtone centre.
        mid_mask = (lum >= shadow_thresh) & (lum <= highlight_thresh)
        mid_w    = _np.where(mid_mask,
                             1.0 - _np.abs(lum - mid_centre) / (mid_half + 1e-6),
                             0.0)
        r_out = _np.where(mid_mask,
                          _np.clip(r_out + rose_warmth * 0.60 * mid_w, 0.0, 1.0),
                          r_out)
        b_out = _np.where(mid_mask,
                          _np.clip(b_out - rose_warmth * 0.28 * mid_w, 0.0, 1.0),
                          b_out)

        # Shadow zone: keep warm — gentle R lift, B damp to prevent cool invasion
        sh_mask = lum < shadow_thresh
        sh_ramp = _np.where(sh_mask,
                            _np.clip((shadow_thresh - lum) / (shadow_thresh + 1e-6),
                                     0.0, 1.0),
                            0.0)
        r_out = _np.where(sh_mask,
                          _np.clip(r_out + rose_warmth * 0.25 * sh_ramp, 0.0, 1.0),
                          r_out)
        b_out = _np.where(sh_mask,
                          _np.clip(b_out - rose_warmth * 0.35 * sh_ramp, 0.0, 1.0),
                          b_out)

        # ── 3. Luminous warm highlight glow ──────────────────────────────────
        # In bright zones: push toward warm cream-gold.
        # R lifts most, G moderately, B just slightly — warm cream, not cold silver.
        hi_mask = lum > highlight_thresh
        hi_ramp = _np.where(hi_mask,
                            _np.clip((lum - highlight_thresh)
                                     / (1.0 - highlight_thresh + 1e-6), 0.0, 1.0),
                            0.0)
        r_out = _np.where(hi_mask,
                          _np.clip(r_out + highlight_glow * 0.72 * hi_ramp, 0.0, 1.0),
                          r_out)
        g_out = _np.where(hi_mask,
                          _np.clip(g_out + highlight_glow * 0.48 * hi_ramp, 0.0, 1.0),
                          g_out)
        b_out = _np.where(hi_mask,
                          _np.clip(b_out + highlight_glow * 0.18 * hi_ramp, 0.0, 1.0),
                          b_out)

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        n_highlight = int(hi_mask.sum())
        n_midtone   = int(mid_mask.sum())
        n_shadow    = int(sh_mask.sum())
        print(f"    Renoir luminous warmth pass complete  "
              f"(highlight={n_highlight}px  midtone={n_midtone}px  shadow={n_shadow}px)")

    # ─────────────────────────────────────────────────────────────────────────
    # wet_on_wet_bleeding_pass — session 41 random improvement
    # ─────────────────────────────────────────────────────────────────────────

    def wet_on_wet_bleeding_pass(
        self,
        *,
        bleed_radius: float = 2.5,
        bleed_strength: float = 0.18,
        edge_sensitivity: float = 0.55,
        opacity: float = 0.65,
    ) -> None:
        """
        Wet-on-wet paint bleeding pass (session 41 random improvement).

        When oil paint is applied to a still-wet canvas, pigment migrates
        across colour boundaries — colours from adjacent zones partially
        invade each other, softening the boundary into a transitional blended
        strip while leaving the interior of each colour zone intact.  This is
        fundamentally different from the global blur of sfumato_veil_pass:
        bleeding is *localised to detected colour boundaries* and only mixes
        the colours that are physically adjacent.

        Algorithm
        ---------
        1. **Edge detection** — Sobel gradient magnitude on the luminance
           channel identifies zones of high colour change (boundary pixels).
        2. **Neighbourhood blend** — At each boundary pixel, the colour is
           replaced with a Gaussian-blurred version (radius = bleed_radius),
           simulating pigment spreading outward from the loaded brush.
        3. **Selective composition** — The blended result is composited back
           only in proportion to the local edge strength × bleed_strength,
           so the interior of each colour zone is untouched — only the
           boundary zone softens.
        4. **Final opacity** — The entire layer is blended at ``opacity``
           over the original so the effect is subtle and controllable.

        The result gives the canvas a "freshly painted, still-wet" quality:
        edges that were previously hard become softly transitional, as though
        a master's palette-knife has just laid adjacent colours wet-to-wet
        and the pigments are beginning to move into each other.

        Parameters
        ----------
        bleed_radius      : Gaussian sigma (pixels) for the cross-boundary spread
        bleed_strength    : how strongly the blurred colour replaces the
                            sharp edge colour (0 = no bleed, 1 = full replace)
        edge_sensitivity  : normalised threshold controlling which gradient
                            magnitudes register as boundaries (0.0 = very
                            sensitive / all edges bleed; 1.0 = only strongest
                            edges bleed)
        opacity           : global blend weight of the entire pass
                            (0 = noop, 1 = full replacement of original)

        Notes
        -----
        Best applied AFTER the main form-building passes (block_in, build_form)
        and BEFORE the final highlights (place_lights) — it softens the mid-
        range boundary edges without removing the fine highlight details added
        later.  Use low opacity (0.4–0.7) for a subtle living-paint quality;
        high opacity (0.9+) produces an overly blended academic-school effect.

        References
        ----------
        Observable in: Rubens alla-prima passages, Sargent's wet-paper
        watercolours, Zorn's fluid oil portraits — all artists who prized the
        chromatic liveliness of paint that had not yet dried.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gauss, convolve as _conv

        print(f"  Wet-on-wet bleeding pass  "
              f"(bleed_radius={bleed_radius:.1f}  strength={bleed_strength:.2f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Wet-on-wet bleeding pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Luminance for edge detection ──────────────────────────────────────
        lum = 0.299 * r_f + 0.587 * g_f + 0.114 * b_f

        # ── Sobel edge magnitude ──────────────────────────────────────────────
        sobel_x = _np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                             dtype=_np.float32)
        sobel_y = _np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
                             dtype=_np.float32)
        gx = _conv(lum, sobel_x, mode='reflect')
        gy = _conv(lum, sobel_y, mode='reflect')
        edge_mag = _np.sqrt(gx * gx + gy * gy)

        # Normalise to [0, 1]
        edge_max = edge_mag.max()
        if edge_max > 1e-6:
            edge_mag = edge_mag / edge_max
        else:
            # Flat canvas — nothing to bleed
            print(f"    Wet-on-wet bleeding pass complete (flat canvas — no edges detected)")
            return

        # Apply edge sensitivity threshold: only edges above the threshold
        # contribute; ramp from threshold to 1.0 for smooth roll-off.
        edge_weight = _np.clip(
            (edge_mag - (1.0 - edge_sensitivity)) / (edge_sensitivity + 1e-6),
            0.0, 1.0)

        # ── Gaussian-blurred versions of each channel ─────────────────────────
        # This is the "bled" colour — what adjacent pigments look like after
        # migrating across the boundary into the current pixel's zone.
        r_bleed = _gauss(r_f, sigma=bleed_radius, mode='reflect')
        g_bleed = _gauss(g_f, sigma=bleed_radius, mode='reflect')
        b_bleed = _gauss(b_f, sigma=bleed_radius, mode='reflect')

        # ── Selective blending at boundary zones ──────────────────────────────
        # w_bleed: how much of the blurred colour replaces the original,
        #          scaled by edge_weight and bleed_strength.
        w_bleed = _np.clip(edge_weight * bleed_strength, 0.0, 1.0)

        r_out = r_f * (1.0 - w_bleed) + r_bleed * w_bleed
        g_out = g_f * (1.0 - w_bleed) + g_bleed * w_bleed
        b_out = b_f * (1.0 - w_bleed) + b_bleed * w_bleed

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        n_edge = int((edge_weight > 0.01).sum())
        print(f"    Wet-on-wet bleeding pass complete  "
              f"(boundary pixels={n_edge}  bleed_radius={bleed_radius:.1f}px)")

    # ─────────────────────────────────────────────────────────────────────────
    # gentileschi_dramatic_flesh_pass — inspired by Artemisia Gentileschi
    # ─────────────────────────────────────────────────────────────────────────

    def gentileschi_dramatic_flesh_pass(
        self,
        *,
        shadow_deepen:    float = 0.20,
        shadow_warmth:    float = 0.12,
        penumbra_warmth:  float = 0.09,
        highlight_gold:   float = 0.10,
        shadow_thresh:    float = 0.30,
        highlight_thresh: float = 0.68,
        opacity:          float = 0.75,
    ) -> None:
        """
        Artemisia Gentileschi dramatic flesh pass (artist pass).

        Gentileschi inherited Caravaggio's tenebrism but departed from it in one
        defining way: her shadows are *warm*.  Where Caravaggio's void is cold —
        a near-black that has no temperature — Gentileschi's darks carry a deep
        umber-brown warmth absorbed from her dark ground and amber glazes.  This
        pass replicates that quality by operating separately on three tonal zones:

        1. **Shadow deepening** — In the darkest zone (lum < shadow_thresh), value
           is pulled further down toward deep shadow, but simultaneously warmed:
           R is lifted relative to G and B.  The result is warm umber-brown dark
           rather than cold near-black — the defining difference between Gentileschi's
           emotional tenebrism and Caravaggio's nihilistic void.

        2. **Penumbra warmth** — In the lower half of the midtone zone (shadow_thresh
           ≤ lum ≤ midtone centre), the colour is pushed toward a warm olive-amber.
           This is the *penumbra* — the zone of partial shadow — which Gentileschi
           glazed with warm amber to create an intermediate transition that reads as
           firelight absorbed into flesh.  It is distinct from both the warm golden
           highlight above it and the warm umber shadow below.

        3. **Candlelit highlight gold** — In the brightest zone (lum > highlight_thresh),
           highlights are warmed toward amber-gold: R lifts most, G moderately, B
           barely.  Gentileschi's highlights are not the cool silver of northern
           painting or the ivory of Academic painters — they carry the warm golden
           quality of single-source candlelight or torch illumination.

        All three adjustments are composited back at ``opacity`` over the original
        canvas, preserving the underlying layer structure.

        Parameters
        ----------
        shadow_deepen    : how strongly the dark zone is deepened (value pulled down)
        shadow_warmth    : warm umber push in the shadow zone (lifts R relative to G/B)
        penumbra_warmth  : olive-amber push in the lower midtone / penumbra zone
        highlight_gold   : warm amber-gold lift in the bright highlight zone
        shadow_thresh    : luminance boundary below which shadow adjustments apply
        highlight_thresh : luminance boundary above which highlight adjustments apply
        opacity          : global blend weight (0 = noop, 1 = full replacement)

        Notes
        -----
        Call this AFTER the main form-building passes (block_in, build_form) and
        BEFORE the final highlights (place_lights).  Pairs well with a warm
        amber-umber glaze (0.58, 0.38, 0.16) applied afterward.

        The penumbra zone (shadow_thresh to midtone centre) is where this pass
        does its most distinctive work — the olive-warm half-shadow is the
        quality most absent from generic tenebrism implementations and most
        characteristic of Gentileschi's specific style.

        Famous works to study:
          *Judith Slaying Holofernes* (c. 1614–1620, Uffizi) — the lit side of
          Judith's arm and chest gleam with warm golden impasto; her shadow side
          falls into deep warm umber, not cold black; the penumbra zone between
          them carries a warm olive-amber transition.
          *Self-Portrait as the Allegory of Painting* (c. 1638–1639, Royal
          Collection) — the lit face and arm show warm candlelit gold; the
          shadow half is warm umber-brown with visible amber glaze in the
          half-shadow.
        """
        import numpy as _np

        print(f"  Gentileschi dramatic flesh pass  "
              f"(shadow_deepen={shadow_deepen:.2f}  shadow_warmth={shadow_warmth:.2f}  "
              f"penumbra_warmth={penumbra_warmth:.2f}  highlight_gold={highlight_gold:.2f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Gentileschi dramatic flesh pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA channel order: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Luminance ─────────────────────────────────────────────────────────
        lum = 0.299 * r_f + 0.587 * g_f + 0.114 * b_f

        # ── Thresholds and zone midpoint ──────────────────────────────────────
        mid_centre = (shadow_thresh + highlight_thresh) * 0.5
        penumbra_top = mid_centre  # penumbra warmth applies from shadow_thresh to mid_centre

        # ── 1. Shadow zone: deepen and warm toward umber ──────────────────────
        # Pixels darker than shadow_thresh are pulled deeper (shadow_deepen) and
        # simultaneously warmed (shadow_warmth): R lifted, G/B damped.
        # The warm push is proportional to how deep into the shadow the pixel is,
        # so the darkest pixels get the most warmth (they need it most to escape
        # cold-black appearance).
        sh_mask = lum < shadow_thresh
        sh_ramp = _np.where(
            sh_mask,
            _np.clip((shadow_thresh - lum) / (shadow_thresh + 1e-6), 0.0, 1.0),
            0.0)  # peaks at lum=0, zero at lum=shadow_thresh

        # Deepen: pull all channels down proportionally
        deepen_factor = 1.0 - shadow_deepen * sh_ramp
        r_out = _np.where(sh_mask, r_out * deepen_factor, r_out)
        g_out = _np.where(sh_mask, g_out * deepen_factor, g_out)
        b_out = _np.where(sh_mask, b_out * deepen_factor, b_out)

        # Warm umber push: after deepening, lift R, damp B relative to mid
        # — turns the deepened tone from cold grey-black to warm umber-brown
        r_out = _np.where(sh_mask,
                          _np.clip(r_out + shadow_warmth * 0.70 * sh_ramp, 0.0, 1.0),
                          r_out)
        g_out = _np.where(sh_mask,
                          _np.clip(g_out + shadow_warmth * 0.20 * sh_ramp, 0.0, 1.0),
                          g_out)
        b_out = _np.where(sh_mask,
                          _np.clip(b_out - shadow_warmth * 0.30 * sh_ramp, 0.0, 1.0),
                          b_out)

        # ── 2. Penumbra zone: olive-amber warmth ──────────────────────────────
        # The lower midtone band (shadow_thresh to mid_centre) — where Gentileschi
        # applied warm amber glazes to create the characteristic olive-warm half-shadow.
        # This is the most distinctive quality of her flesh rendering.
        pen_mask = (lum >= shadow_thresh) & (lum < penumbra_top)
        pen_ramp = _np.where(
            pen_mask,
            # peaks midway between shadow_thresh and penumbra_top; zero at both ends
            1.0 - _np.abs(lum - (shadow_thresh + penumbra_top) * 0.5)
                  / ((penumbra_top - shadow_thresh) * 0.5 + 1e-6),
            0.0)
        pen_ramp = _np.clip(pen_ramp, 0.0, 1.0)

        # Olive-amber: R up (warm), G up slightly (olive), B down (remove cool)
        r_out = _np.where(pen_mask,
                          _np.clip(r_out + penumbra_warmth * 0.65 * pen_ramp, 0.0, 1.0),
                          r_out)
        g_out = _np.where(pen_mask,
                          _np.clip(g_out + penumbra_warmth * 0.30 * pen_ramp, 0.0, 1.0),
                          g_out)
        b_out = _np.where(pen_mask,
                          _np.clip(b_out - penumbra_warmth * 0.40 * pen_ramp, 0.0, 1.0),
                          b_out)

        # ── 3. Highlight zone: warm amber-gold lift ───────────────────────────
        # In bright zones above highlight_thresh, warm the highlights toward
        # amber-gold: R lifts most, G moderately, B barely.  Gentileschi's
        # highlights carry the colour of a single warm candle or torch — not
        # the cool silver of northern painting.
        hi_mask = lum > highlight_thresh
        hi_ramp = _np.where(
            hi_mask,
            _np.clip((lum - highlight_thresh) / (1.0 - highlight_thresh + 1e-6),
                     0.0, 1.0),
            0.0)  # zero at lum=highlight_thresh, peaks at lum=1.0

        r_out = _np.where(hi_mask,
                          _np.clip(r_out + highlight_gold * 0.80 * hi_ramp, 0.0, 1.0),
                          r_out)
        g_out = _np.where(hi_mask,
                          _np.clip(g_out + highlight_gold * 0.45 * hi_ramp, 0.0, 1.0),
                          g_out)
        b_out = _np.where(hi_mask,
                          _np.clip(b_out + highlight_gold * 0.08 * hi_ramp, 0.0, 1.0),
                          b_out)

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        n_shadow    = int(sh_mask.sum())
        n_penumbra  = int(pen_mask.sum())
        n_highlight = int(hi_mask.sum())
        print(f"    Gentileschi dramatic flesh pass complete  "
              f"(shadow={n_shadow}px  penumbra={n_penumbra}px  highlight={n_highlight}px)")

    # ─────────────────────────────────────────────────────────────────────────
    # munch_anxiety_swirl_pass — inspired by Edvard Munch
    # ─────────────────────────────────────────────────────────────────────────

    def munch_anxiety_swirl_pass(
        self,
        *,
        n_swirl_strokes:  int   = 320,
        swirl_amplitude:  float = 0.22,
        swirl_frequency:  float = 3.8,
        color_intensity:  float = 0.55,
        bg_only:          bool  = True,
        stroke_opacity:   float = 0.28,
        stroke_size:      float = 9.0,
    ) -> None:
        """
        Munch Anxiety Swirl Pass — Edvard Munch's sinuous background turbulence.

        Munch's defining compositional gesture is the undulating, serpentine
        brushstroke that spirals across the canvas in long curving arcs —
        most famously in "The Scream" (1893), where the entire sky and
        landscape becomes a single churning vortex of anxious energy.  This
        technique dissolves the distinction between figure and environment,
        making the external world an expression of an internal psychological
        state.

        Implementation strategy
        -----------------------
        The pass places a series of long sinusoidal stroke paths across the
        canvas.  Each path is a sine-wave trajectory with randomised phase,
        frequency, and amplitude, oriented at a shallow diagonal to suggest
        the rolling, fjord-scape undulations in Munch's oils.  The colour
        of each stroke is drawn from the Munch palette — blood reds, saffron
        yellows, prussian blues, sickly greens — with per-stroke jitter to
        introduce the characteristic raw, trembling quality of his surface.

        When bg_only=True (the default), strokes are suppressed wherever the
        figure mask is solid, confining the turbulence to the background and
        leaving the portrait subject as a calmer, mask-like presence within
        the swirling landscape.  This matches Munch's portrait practice:
        the sitter is simplified and steady while the world behind them writhes.

        Parameters
        ----------
        n_swirl_strokes : int
            Number of sinusoidal swirl paths to place.  320 produces dense
            coverage; reduce to 180–220 for a looser, more gestural reading.
        swirl_amplitude : float
            Amplitude of the sinusoidal wave as a fraction of canvas height.
            0.22 produces medium-depth undulation; raise to 0.35+ for extreme
            churning, lower to 0.10 for shallow ripples.
        swirl_frequency : float
            Number of complete wave cycles across the canvas width.  3.8
            gives roughly four undulations per stroke — the Munch characteristic
            rhythm.  Higher values produce tighter, more frantic coils.
        color_intensity : float
            Blend weight of the Munch palette colours into the existing canvas.
            0.55 is psychologically vivid without obliterating the underpainting.
            Raise toward 1.0 for maximum expressionist intensity.
        bg_only : bool
            If True, strokes are masked to the background only (suppressed
            where figure mask alpha > 0.5).  Recommended True for portraiture.
        stroke_opacity : float
            Per-stroke opacity in [0, 1].  Lower values (0.20–0.28) build up
            colour gradually as strokes cross; higher values (0.40+) create
            bold individual marks visible from across the room.
        stroke_size : float
            Base brush radius in pixels.  Munch's loaded-brush swirl marks
            are wider than most portrait passes — 9px is appropriate for a
            512×512 canvas; scale proportionally for larger outputs.

        Notes
        -----
        Call AFTER block_in() / build_form() and BEFORE glaze() and finish().
        Pair with a warm crimson-amber glaze (0.65, 0.30, 0.10) at opacity
        0.07–0.10 after this pass to unify the turbulent surface in fever warmth.
        """
        import math as _math
        import numpy as _np
        import cairo as _cairo

        print(f"  Munch anxiety swirl pass  "
              f"(n={n_swirl_strokes}  amp={swirl_amplitude:.2f}  "
              f"freq={swirl_frequency:.1f}  intensity={color_intensity:.2f})…")

        surf = self.canvas.surface
        W    = surf.get_width()
        H    = surf.get_height()

        # ── Munch characteristic palette ──────────────────────────────────────
        munch_colors = [
            (0.82, 0.28, 0.14),   # cadmium-red anxiety
            (0.88, 0.62, 0.18),   # saffron-amber atmospheric warmth
            (0.18, 0.32, 0.52),   # prussian-cobalt cold depth
            (0.42, 0.58, 0.38),   # sickly verdigris
            (0.62, 0.22, 0.35),   # crimson-violet psychic wound
        ]
        n_colors = len(munch_colors)

        # ── Figure mask for bg_only suppression ───────────────────────────────
        fig_mask = self._figure_mask   # (H, W) float32 in [0, 1] or None

        rng = _np.random.default_rng(seed=42)   # deterministic for reproducibility

        strokes_placed = 0
        for _ in range(n_swirl_strokes):
            # Starting y position distributed across full canvas height
            y0_frac = rng.uniform(0.0, 1.0)
            phase   = rng.uniform(0.0, 2.0 * _math.pi)
            # Diagonal angle — Munch's lines rarely run purely horizontal
            angle_deg = rng.uniform(-18.0, 18.0)
            cos_a = _math.cos(_math.radians(angle_deg))
            sin_a = _math.sin(_math.radians(angle_deg))

            # Choose colour with slight jitter
            base_col = munch_colors[rng.integers(0, n_colors)]
            jitter   = rng.uniform(-0.06, 0.06, size=3)
            col = tuple(float(_np.clip(c + j, 0.0, 1.0))
                        for c, j in zip(base_col, jitter))

            # Build sinusoidal path across the canvas
            n_pts   = 32
            pts     = []
            amp_px  = swirl_amplitude * H
            for i in range(n_pts):
                t  = i / (n_pts - 1)          # 0 → 1 across the stroke length
                # Base x progresses across canvas; y follows sine wave
                bx = t * W
                by = y0_frac * H + amp_px * _math.sin(
                    2.0 * _math.pi * swirl_frequency * t + phase
                )
                # Apply rotational tilt
                cx = bx * cos_a - (by - y0_frac * H) * sin_a
                cy = by * cos_a + (bx - 0) * sin_a * 0.08   # subtle rotation
                pts.append((cx, cy))

            # Check whether the stroke midpoint falls in background
            mid_x = int(_np.clip(pts[n_pts // 2][0], 0, W - 1))
            mid_y = int(_np.clip(pts[n_pts // 2][1], 0, H - 1))
            if bg_only and fig_mask is not None:
                if fig_mask[mid_y, mid_x] > 0.50:
                    continue   # Skip — this stroke would cover the figure

            # Draw the swirl path as a series of connected segments
            ctx = self.canvas.ctx
            ctx.save()

            # Scale opacity by color_intensity
            effective_opacity = stroke_opacity * color_intensity

            r_col, g_col, b_col = col
            ctx.set_source_rgba(r_col, g_col, b_col, effective_opacity)
            ctx.set_line_width(stroke_size)
            ctx.set_line_cap(_cairo.LINE_CAP_ROUND)
            ctx.set_line_join(_cairo.LINE_JOIN_ROUND)

            ctx.move_to(pts[0][0], pts[0][1])
            for px, py in pts[1:]:
                ctx.line_to(px, py)
            ctx.stroke()
            ctx.restore()

            strokes_placed += 1

        print(f"    Munch anxiety swirl pass complete  ({strokes_placed} swirl strokes placed)")

    # ─────────────────────────────────────────────────────────────────────────
    # hals_bravura_stroke_pass — inspired by Frans Hals
    # ─────────────────────────────────────────────────────────────────────────

    def hals_bravura_stroke_pass(
        self,
        reference:        Union[np.ndarray, Image.Image, None] = None,
        *,
        n_strokes:        int   = 480,
        stroke_size:      float = 8.0,
        opacity:          float = 0.62,
        angle_jitter_deg: float = 42.0,
        color_jitter:     float = 0.05,
        broken_tone:      bool  = True,
        figure_mask:      Optional[np.ndarray] = None,
    ) -> None:
        """
        Hals Bravura Stroke Pass — Frans Hals's alla prima broken-tone technique.

        Frans Hals (c. 1582–1666) was the first great master of the 'broken
        tone': adjacent strokes of slightly different value and colour
        temperature are set down directly on the canvas without blending, so
        the eye synthesises the tonal mixture from a normal reading distance.
        This anticipates Impressionist divided colour by two centuries and
        gives Hals's portraits their startling sense of psychological
        immediacy — as if the sitter were caught mid-thought.

        The improvement this pass introduces
        -------------------------------------
        No previous pass in this pipeline simulates 'broken tone' as a
        deliberate compositional strategy.  Existing passes blend colours
        through wet_blend or glaze layers.  This pass withholds blending
        entirely and instead places two value-contrasting strokes side-by-side,
        trusting the viewer's eye to resolve the optical mixture.  This is a
        distinct artistic capability not previously available in the pipeline.

        Implementation strategy
        -----------------------
        The pass samples n_strokes positions across the canvas, each time
        reading the reference colour at that location and applying a bold
        angular jitter (±angle_jitter_deg degrees) to the local flow-field
        direction.  Each stroke is short — approximately 2–3× its width — to
        match the compact, decisive mark Hals preferred.  Per-stroke colour
        jitter (color_jitter) ensures no two adjacent strokes are identical;
        the variation is the technique, not a flaw.

        When broken_tone=True (default), each primary stroke is accompanied
        by a slightly lighter or darker companion stroke offset roughly one
        brush-width perpendicular to the stroke direction.  The companion uses
        an inverted value delta (lighter companion for a shadow stroke, darker
        companion for a highlight stroke), creating the shimmering half-tone
        quality that distinguishes Hals from any smooth-blended technique.

        Parameters
        ----------
        reference : PIL Image, numpy array, or None
            Reference to sample colours from.  When None the current canvas
            buffer is used as reference — useful for a post-processing pass.
        n_strokes : int
            Number of bravura strokes.  480 gives good coverage on 512×512.
        stroke_size : float
            Base brush radius in pixels.  8.0 is the primary Hals mark.
        opacity : float
            Per-stroke opacity in [0, 1].  0.62 places marks confidently
            without fully obliterating the warm straw ground.
        angle_jitter_deg : float
            Maximum angular deviation from local flow direction in degrees.
            42.0 produces the spontaneous multi-directional quality of Hals.
            Do not reduce below 35 or the surface becomes too regular.
        color_jitter : float
            Per-stroke colour variation amplitude.  0.05 is faithful to
            Hals's subtle broken tone; raise toward 0.10 for more vibration.
        broken_tone : bool
            When True, each primary stroke is accompanied by a value-shifted
            companion stroke to simulate Hals's broken-tone technique.
        figure_mask : numpy array, optional
            Overrides self._figure_mask for stroke placement bias.

        Notes
        -----
        Call AFTER block_in() / build_form() and BEFORE any final glaze().
        No glazing pass is needed or recommended afterward — Hals finished
        directly, without a unifying glaze layer.
        Pair with tone_ground((0.78, 0.70, 0.52)) beforehand so the warm
        straw buff shows through in the half-tone areas.
        """
        print(f"  Hals bravura stroke pass  "
              f"(n={n_strokes}  size={stroke_size:.1f}  "
              f"opacity={opacity:.2f}  broken_tone={broken_tone})…")

        h, w = self.h, self.w

        # ── Reference: sample canvas buffer when none provided ────────────────
        if reference is not None:
            ref  = self._prep(reference)
            rarr = ref[:, :, :3].astype(np.float32) / 255.0
        else:
            # Use current canvas state as colour reference
            buf  = np.frombuffer(self.canvas.surface.get_data(),
                                 dtype=np.uint8).reshape(h, w, 4).copy()
            # Cairo stores BGRA; convert to RGB for consistency
            rarr = buf[:, :, [2, 1, 0]].astype(np.float32) / 255.0

        # ── Flow field: stroke angle follows colour contours ──────────────────
        angles = flow_field(rarr)

        # ── Effective region mask ──────────────────────────────────────────────
        effective_mask = figure_mask if figure_mask is not None else self._figure_mask

        # ── Sampling weight: uniform with modest figure bias ──────────────────
        # Hals painted background and figure with the same bravura approach,
        # so we do not mask to figure only — we merely weight figure pixels
        # slightly higher to concentrate detail where it matters.
        weight = np.ones((h, w), dtype=np.float32)
        if effective_mask is not None:
            weight = np.where(effective_mask > 0.5, 2.0, 1.0).astype(np.float32)
        weight_flat = weight.flatten()
        weight_flat /= weight_flat.sum() + 1e-9

        if n_strokes <= 0:
            print("    Hals bravura stroke pass skipped (n_strokes=0)")
            return

        positions = self.rng.choice(h * w, size=n_strokes,
                                    p=weight_flat, replace=True)

        tip              = BrushTip(BrushTip.FILBERT)
        angle_jitter_rad = math.radians(angle_jitter_deg)
        strokes_placed   = 0

        for pos in positions:
            py, px = int(pos // w), int(pos % w)
            margin = max(4, int(stroke_size * 2))
            px = int(np.clip(px, margin, w - margin))
            py = int(np.clip(py, margin, h - margin))

            # ── Colour from reference + per-stroke jitter ─────────────────────
            col = tuple(float(rarr[py, px, c]) for c in range(3))
            col = jitter(col, color_jitter, self._rng_py)

            # ── Stroke direction: flow field + bold angular jitter ────────────
            # Hals's bravura mark does not consistently follow the form contour;
            # it departs at a bold angle, creating the restless spontaneous energy
            # of his technique.  angle_jitter_rad applies a uniform random offset
            # of up to ±42° from the locally dominant colour-contour direction.
            a = (float(angles[py, px])
                 + self._rng_py.uniform(-angle_jitter_rad, angle_jitter_rad))

            # ── Short, decisive stroke: ~2–3× width in length ─────────────────
            length = stroke_size * self._rng_py.uniform(2.0, 3.2)
            start  = (px - math.cos(a) * length * 0.5,
                      py - math.sin(a) * length * 0.5)
            # Slight S-curve (curve parameter) for organic cursive quality
            curve = self._rng_py.uniform(-0.18, 0.18)
            pts   = stroke_path(start, a, length,
                                curve=curve,
                                n=max(3, int(length / 4)))
            ws    = [stroke_size * self._rng_py.uniform(0.75, 1.15)] * len(pts)

            self.canvas.apply_stroke(
                pts, ws, col, tip,
                opacity=opacity,
                wet_blend=0.10,        # alla prima: minimal wet blending
                jitter_amt=color_jitter * 0.5,
                rng=self._rng_py,
                region_mask=effective_mask,
            )
            strokes_placed += 1

            # ── Broken-tone companion stroke ───────────────────────────────────
            # Hals's defining innovation: a value-shifted companion stroke placed
            # perpendicular to the primary, one brush-width offset.  The companion
            # is lighter adjacent to a shadow stroke and darker adjacent to a
            # highlight stroke — the eye resolves the optical mixture into a
            # vibrant, living half-tone that no blended technique can replicate.
            if broken_tone:
                lum = 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]
                # Positive delta (lighter) for dark strokes; negative (darker) for lights
                value_delta = 0.12 if lum < 0.45 else -0.09
                comp_col = (
                    max(0.0, min(1.0, col[0] + value_delta)),
                    max(0.0, min(1.0, col[1] + value_delta * 0.88)),
                    max(0.0, min(1.0, col[2] + value_delta * 0.72)),
                )
                # Perpendicular offset — one brush-radius away from primary stroke
                perp_offset = stroke_size * 0.85
                perp_cos    = -math.sin(a)
                perp_sin    =  math.cos(a)
                comp_pts    = [
                    (px_ + perp_cos * perp_offset,
                     py_ + perp_sin * perp_offset)
                    for (px_, py_) in pts
                ]
                comp_ws = [wi * 0.75 for wi in ws]

                self.canvas.apply_stroke(
                    comp_pts, comp_ws, comp_col, tip,
                    opacity=opacity * 0.55,
                    wet_blend=0.06,
                    jitter_amt=color_jitter * 0.35,
                    rng=self._rng_py,
                    region_mask=effective_mask,
                )

        print(f"    Hals bravura stroke pass complete  "
              f"({strokes_placed} bravura strokes placed)")

    # ─────────────────────────────────────────────────────────────────────────
    # dali_paranoiac_critical_pass — inspired by Salvador Dali
    # ─────────────────────────────────────────────────────────────────────────

    def dali_paranoiac_critical_pass(
        self,
        *,
        chroma_shift:        int   = 3,
        shadow_ultramarine:  float = 0.18,
        highlight_warmth:    float = 0.06,
        shadow_thresh:       float = 0.28,
        highlight_thresh:    float = 0.78,
        figure_sharpen:      float = 0.38,
        bg_only_aberration:  bool  = True,
        opacity:             float = 0.82,
    ) -> None:
        """
        Dali Paranoiac-Critical Pass — Salvador Dali's hyper-realist surrealist technique.

        Salvador Dali (1904–1989) called his method the 'Paranoiac-Critical Method':
        by deliberately inducing a paranoid hallucinatory state, he trained himself
        to discover hidden double images within compositions — two or more distinct
        subjects occupying the same visual space, readable depending on the viewer's
        mental frame.  The painterly technique he applied to these visions was the
        precise opposite of psychological instability: obsessively photographic,
        with near-invisible brushwork and seamless enamel-like surfaces he called
        'hand-painted dream photographs.'

        This pass replicates four defining qualities of Dali's technique:

        1. **Ultramarine shadow deepening** — In the darkest tonal zone (lum <
           shadow_thresh), shadows are pushed toward deep ultramarine-violet rather
           than neutral black.  This is the Catalonian light signature: sunlit
           Mediterranean surfaces against cool ultramarine void — the same quality
           that appears in Velázquez's Catalan-influenced shadows, intensified by
           the brilliant overhead sun of the Empordà plain near Dali's home in
           Cadaqués.  The push is graduated: the deepest shadows get the most
           ultramarine, while the penumbra edge preserves a warm transition.

        2. **Catalan sunlight warmth** — In the brightest tonal zone (lum >
           highlight_thresh), lit surfaces are pushed toward warm amber-gold — the
           colour of Catalan sunlight on ochre stone.  This contrasts with the cool
           ultramarine shadows to produce the extreme tonal polarity that gives
           Dali's canvases their almost hallucinogenic vibrancy.

        3. **Chromatic prismatic aberration** — A subtle lateral offset of the R
           and B channels in background regions simulates the dreamlike out-of-phase
           quality of Dali's hyper-realist surfaces.  Real optics introduce small
           chromatic aberrations from lens dispersion; Dali's hyper-realist technique
           seems to replicate this on canvas, suggesting the image is a photograph
           of a dream rather than a painting from life.  When bg_only_aberration=True
           (default), this effect is restricted to regions outside the figure mask,
           preserving crisp foreground precision while the background shimmers.

        4. **Hyper-realist figure sharpening** — An unsharp-mask pass applied to
           figure regions reinforces the 'hand-painted photograph' quality.  Dali
           rendered his subjects with impossible photographic crispness — every pore,
           every hair, every reflected catch-light resolved with precision.  The
           figure_sharpen parameter controls the strength of this unsharp mask.

        Parameters
        ----------
        chroma_shift : int
            Lateral pixel offset for chromatic aberration.  3 gives a subtle
            prismatic fringe at edges; 0 disables aberration entirely.
        shadow_ultramarine : float
            Strength of the ultramarine push in the dark zone.  0.18 is faithful
            to Dali's deep shadow colour; raise toward 0.30 for stronger effect.
        highlight_warmth : float
            Strength of the amber-gold warmth in the bright zone.  0.06 is subtle.
        shadow_thresh : float
            Luminance below which shadow adjustments apply.
        highlight_thresh : float
            Luminance above which highlight adjustments apply.
        figure_sharpen : float
            Unsharp-mask strength applied to figure regions.  0.38 gives
            photographic crispness without artefacts.  0 disables sharpening.
        bg_only_aberration : bool
            When True, chromatic aberration is applied only to background
            regions (figure_mask < 0.5).  When False, applied everywhere.
        opacity : float
            Global blend weight for all adjustments.  0 = noop, 1 = full.

        Notes
        -----
        Call AFTER block_in() and build_form().  Pairs with a warm amber
        glaze (0.88, 0.78, 0.42) applied afterward for the final unifying
        Catalan sunlight quality.

        Famous works to study:
          *The Persistence of Memory* (1931, MoMA) — the melting watches sit
          on a table in a hyper-precisely rendered Catalonian cove; every
          sand grain, every reflective surface is resolved with photographic
          fidelity; the impossible (melting metal) gains its power from
          the photographic reality of everything around it.

          *Dream Caused by the Flight of a Bee* (1944, Thyssen-Bornemisza) —
          Gala floats in mid-air above a sunlit ledge; the tiger emerging
          from a pomegranate is rendered with the same obsessive precision
          as Gala's skin; deep ultramarine shadows define the spatial
          recession behind the brilliant warm-lit foreground.
        """
        import numpy as _np
        from scipy import ndimage as _ndimage

        print(f"  Dali paranoiac-critical pass  "
              f"(chroma_shift={chroma_shift}  "
              f"shadow_ultramarine={shadow_ultramarine:.2f}  "
              f"figure_sharpen={figure_sharpen:.2f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Dali paranoiac-critical pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA channel order: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Luminance ─────────────────────────────────────────────────────────
        lum = 0.299 * r_f + 0.587 * g_f + 0.114 * b_f

        # ── 1. Ultramarine shadow deepening ───────────────────────────────────
        # In the darkest tonal zone, push colour toward deep ultramarine-violet.
        # The ramp peaks at lum=0 (maximum adjustment on pure black) and falls
        # to zero at lum=shadow_thresh (no adjustment at the shadow boundary).
        sh_mask = lum < shadow_thresh
        sh_ramp = _np.where(
            sh_mask,
            _np.clip((shadow_thresh - lum) / (shadow_thresh + 1e-6), 0.0, 1.0),
            0.0)

        # Cool R and G down; lift B toward deep ultramarine
        r_out = _np.where(sh_mask,
                          _np.clip(r_out - shadow_ultramarine * 0.55 * sh_ramp,
                                   0.0, 1.0),
                          r_out)
        g_out = _np.where(sh_mask,
                          _np.clip(g_out - shadow_ultramarine * 0.42 * sh_ramp,
                                   0.0, 1.0),
                          g_out)
        b_out = _np.where(sh_mask,
                          _np.clip(b_out + shadow_ultramarine * 0.70 * sh_ramp,
                                   0.0, 1.0),
                          b_out)

        # ── 2. Catalan sunlight warmth in highlights ──────────────────────────
        # Push bright zones toward warm amber-gold — the colour of Catalan
        # sunlight on ochre stone and warm ivory flesh.  The ramp peaks at
        # lum=1.0 and falls to zero at lum=highlight_thresh.
        hi_mask = lum > highlight_thresh
        hi_ramp = _np.where(
            hi_mask,
            _np.clip((lum - highlight_thresh) / (1.0 - highlight_thresh + 1e-6),
                     0.0, 1.0),
            0.0)

        r_out = _np.where(hi_mask,
                          _np.clip(r_out + highlight_warmth * 0.80 * hi_ramp,
                                   0.0, 1.0),
                          r_out)
        g_out = _np.where(hi_mask,
                          _np.clip(g_out + highlight_warmth * 0.50 * hi_ramp,
                                   0.0, 1.0),
                          g_out)
        b_out = _np.where(hi_mask,
                          _np.clip(b_out - highlight_warmth * 0.25 * hi_ramp,
                                   0.0, 1.0),
                          b_out)

        # ── 3. Chromatic prismatic aberration ─────────────────────────────────
        # Shift R right and B left by chroma_shift pixels to simulate the
        # dreamlike out-of-phase quality of Dali's hyper-realist surfaces.
        # When bg_only_aberration=True, apply only to background regions so
        # the crisp foreground precision of his figure rendering is preserved.
        if chroma_shift > 0:
            if bg_only_aberration and self._figure_mask is not None:
                # Background: where figure_mask < 0.5; smooth the edge transition
                bg_mask_2d = (self._figure_mask < 0.5).astype(_np.float32)
                bg_mask_2d = _ndimage.gaussian_filter(
                    bg_mask_2d, sigma=float(chroma_shift))
            else:
                bg_mask_2d = _np.ones((h, w), dtype=_np.float32)

            # Lateral shift: R right (+col), B left (-col)
            r_aberrated = _np.roll(r_out, chroma_shift, axis=1)
            b_aberrated = _np.roll(b_out, -chroma_shift, axis=1)

            # Remove wrap-around artefacts at canvas edges
            r_aberrated[:, :chroma_shift] = r_out[:, :chroma_shift]
            b_aberrated[:, w - chroma_shift:] = b_out[:, w - chroma_shift:]

            # Blend aberrated channels into background area (60% blend weight)
            blend = bg_mask_2d * 0.60
            r_out = _np.clip(r_out * (1.0 - blend) + r_aberrated * blend, 0.0, 1.0)
            b_out = _np.clip(b_out * (1.0 - blend) + b_aberrated * blend, 0.0, 1.0)

        # ── 4. Hyper-realist figure sharpening ────────────────────────────────
        # Apply an unsharp mask to figure regions to achieve the 'hand-painted
        # photograph' precision of Dali's subject rendering.  The sigma is
        # adaptive (0.8% of the shorter canvas dimension) so it scales cleanly
        # across canvas sizes without requiring manual tuning.
        if figure_sharpen > 0.0 and self._figure_mask is not None:
            fig_mask = (self._figure_mask > 0.5).astype(_np.float32)
            sigma    = max(1.0, float(min(h, w)) * 0.008)

            for ch_arr in (r_out, g_out, b_out):
                blurred = _ndimage.gaussian_filter(ch_arr, sigma=sigma)
                unsharp = _np.clip(ch_arr + figure_sharpen * (ch_arr - blurred),
                                   0.0, 1.0)
                # In-place update restricted to figure pixels
                ch_arr[:, :] = ch_arr * (1.0 - fig_mask) + unsharp * fig_mask

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        n_shadow    = int(sh_mask.sum())
        n_highlight = int(hi_mask.sum())
        print(f"    Dali paranoiac-critical pass complete  "
              f"(shadow={n_shadow}px  highlight={n_highlight}px  "
              f"aberration={'on' if chroma_shift > 0 else 'off'})")

    # ─────────────────────────────────────────────────────────────────────────
    # hammershoi_grey_silence_pass — Vilhelm Hammershøi near-monochrome silence
    # ─────────────────────────────────────────────────────────────────────────

    def hammershoi_grey_silence_pass(
        self,
        desaturation:   float = 0.82,
        window_thresh:  float = 0.68,
        window_cool:    float = 0.08,
        shadow_thresh:  float = 0.35,
        shadow_cool:    float = 0.04,
        opacity:        float = 0.88,
    ) -> None:
        """
        Vilhelm Hammershøi's near-monochrome interior silence pass.

        Hammershøi's Copenhagen interiors are built from a single grey chord
        modulated across the canvas — almost all colour saturation stripped away,
        leaving only a ghost of hue.  What little colour survives is the
        differential between warm ivory (north window light) and cool blue-grey
        (shadowed wall and floor).  The net effect is a profound, held-breath
        silence — the room exists outside of ordinary time.

        Three-strategy pass:

        1. **Desaturation toward grey** — Each RGB channel is blended toward
           its perceptual luminance value at ``desaturation`` rate.  At 0.82,
           each channel retains only 18 % of its original colour deviation from
           grey.  The result reads as near-monochrome but is not a mechanical
           greyscale conversion — a ghost of the original hue survives.

        2. **Window-light cooling** — Bright pixels (``lum > window_thresh``)
           receive a cool blue-grey shift (B lift, R+G damp) simulating the
           diffuse north window daylight that illuminates all of Hammershøi's
           interiors.  The ramp peaks at the brightest pixels and fades to zero
           at the window threshold boundary.

        3. **Shadow cooling** — Dark pixels (``lum < shadow_thresh``) receive a
           further subtle blue-grey cool shift (B lift, R damp) simulating the
           cool reflected sky quality in shadowed room recesses.  Hammershøi
           never introduces warm bounce light in his shadows — they are simply
           cooler and darker versions of the wall tone.

        Parameters
        ----------
        desaturation : float
            Fraction of colour deviation from grey to remove (0 = no change,
            1 = full greyscale).  0.82 retains 18 % of original hue.
        window_thresh : float
            Luminance above which the window-light cooling applies.
        window_cool : float
            Strength of the cool blue-grey shift in lit zones.
        shadow_thresh : float
            Luminance below which the shadow cooling applies.
        shadow_cool : float
            Strength of the cool blue-grey shift in shadow zones.
        opacity : float
            Global blend weight for all adjustments.  0 = noop, 1 = full.

        Notes
        -----
        Call AFTER ``build_form()`` and BEFORE the final ``glaze()``.  Pairs
        with the cool grey unifying glaze ``(0.78, 0.77, 0.74)`` applied
        afterward.

        Famous works to study:
          *Dust Motes Dancing in Sunrays* (1900, Ordrupgaard) — shafts of
          north-window light fall across an otherwise silent grey interior;
          the drama is entirely tonal, not chromatic.

          *Interior, Strandgade 30* (1901, Statens Museum for Kunst) — a door
          stands open into a further room; the recession of grey-on-grey planes
          into depth is the complete subject; no narrative, no figure.
        """
        import numpy as _np

        print(f"  Hammershøi grey silence pass  "
              f"(desaturation={desaturation:.2f}  "
              f"window_cool={window_cool:.2f}  "
              f"shadow_cool={shadow_cool:.2f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Hammershøi grey silence pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA channel order: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Luminance ─────────────────────────────────────────────────────────
        lum = 0.299 * r_f + 0.587 * g_f + 0.114 * b_f

        # ── 1. Desaturation toward grey ────────────────────────────────────────
        # Blend each channel toward the luminance value.
        # At desaturation=0.82: output = 0.18 * channel + 0.82 * luminance.
        # The ghost of colour (18 %) prevents mechanical greyscale while
        # achieving the near-monochrome appearance of Hammershøi's palette.
        r_out = (1.0 - desaturation) * r_f + desaturation * lum
        g_out = (1.0 - desaturation) * g_f + desaturation * lum
        b_out = (1.0 - desaturation) * b_f + desaturation * lum

        # ── 2. Window-light cooling (bright zone) ─────────────────────────────
        # In the lightest tonal zone, push colour toward cool blue-grey to
        # simulate diffuse north window daylight.  The ramp peaks at lum=1.0
        # and falls to zero at lum=window_thresh.
        win_mask = lum > window_thresh
        win_ramp = _np.where(
            win_mask,
            _np.clip((lum - window_thresh) / (1.0 - window_thresh + 1e-6),
                     0.0, 1.0),
            0.0)

        # Cool R and G slightly; lift B toward blue-grey
        r_out = _np.clip(r_out - window_cool * 0.60 * win_ramp, 0.0, 1.0)
        g_out = _np.clip(g_out - window_cool * 0.30 * win_ramp, 0.0, 1.0)
        b_out = _np.clip(b_out + window_cool * 0.55 * win_ramp, 0.0, 1.0)

        # ── 3. Shadow cooling (dark zone) ─────────────────────────────────────
        # In the darkest tonal zone, add a further subtle cool blue-grey push
        # simulating the cool reflected sky quality in shadowed room recesses.
        # The ramp peaks at lum=0 and falls to zero at lum=shadow_thresh.
        sh_mask = lum < shadow_thresh
        sh_ramp = _np.where(
            sh_mask,
            _np.clip((shadow_thresh - lum) / (shadow_thresh + 1e-6), 0.0, 1.0),
            0.0)

        r_out = _np.clip(r_out - shadow_cool * 0.50 * sh_ramp, 0.0, 1.0)
        b_out = _np.clip(b_out + shadow_cool * 0.40 * sh_ramp, 0.0, 1.0)

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        n_win = int(win_mask.sum())
        n_sh  = int(sh_mask.sum())
        print(f"    Hammershøi grey silence pass complete  "
              f"(desaturated={h * w}px  window={n_win}px  shadow={n_sh}px)")

    # ─────────────────────────────────────────────────────────────────────────
    # horizon_mist_pass — graduated mid-ground atmospheric haze
    # ─────────────────────────────────────────────────────────────────────────

    def horizon_mist_pass(
        self,
        horizon_y:      float = 0.48,
        band_height:    float = 0.18,
        mist_color:     "Color" = (0.78, 0.80, 0.86),
        mist_strength:  float = 0.28,
        blur_sigma:     float = 2.5,
        opacity:        float = 0.72,
    ) -> None:
        """
        Graduated mid-ground atmospheric haze for landscape backgrounds.

        Renaissance portrait masters — Leonardo most famously in the Mona Lisa —
        placed their figures before imaginary geological landscapes that dissolve
        into cool atmospheric haze as they recede.  The transition from the
        warmly lit foreground to the pale blue-grey distant horizon is not
        linear: the most pronounced haze collects in the *mid-ground transition
        zone* — roughly at the horizon line — where near and far space meet.
        This band reads as a silvery veil of distance, thicker than the clear
        foreground but lighter than the distant sky.

        This pass targets that mid-ground zone.  It identifies a horizontal band
        centred on ``horizon_y`` (as a fraction of canvas height, measured from
        the top), applies a Gaussian-blurred cool mist overlay whose strength
        peaks at the band centre and fades to zero at its edges, then blends
        that mist over the canvas at ``opacity``.

        Unlike ``atmospheric_depth_pass`` (which applies globally across the
        full vertical range based on luminance thresholds) this pass acts only
        on the specified horizontal band.  It is therefore well-suited to
        portrait backgrounds where the foreground figure must remain unaffected
        but the mid-ground landscape recedes into haze.

        Strategies
        ----------
        1. **Band weighting** — A 1-D Gaussian weight function peaks at
           ``horizon_y`` and has half-power width ``band_height``.  The weight
           is broadcast across the full width of the canvas so the mist thins
           gradually above and below the horizon band.

        2. **Mist overlay** — ``mist_color`` (default cool silver-blue
           ``(0.78, 0.80, 0.86)``) is blended over the canvas at each pixel
           with a weight equal to ``band_weight × mist_strength``.  The colour
           choice models the characteristic pale blue-grey of atmosphere seen
           against a distant sky — slightly blue (cool scattered light), lighter
           than mid-tone (atmospheric translucency), with low saturation.

        3. **Edge softening** — The band boundary is Gaussian-smoothed
           (sigma = ``blur_sigma`` percent of canvas height) so the haze
           dissolves seamlessly into the clear foreground and clear sky above,
           avoiding any visible hard boundary at the band edges.

        Parameters
        ----------
        horizon_y : float
            Vertical centre of the haze band, as a fraction of canvas height
            (0 = top, 1 = bottom).  Default 0.48 places the band just below
            the canvas mid-line, typical for a half-length portrait.
        band_height : float
            Half-width of the haze band as a fraction of canvas height.  0.18
            gives a band spanning roughly the middle third of the canvas.
        mist_color : Color
            RGB colour of the atmospheric mist overlay.  Default (0.78, 0.80,
            0.86) is a cool silver-blue — characteristic of aerial perspective.
        mist_strength : float
            Peak opacity of the mist overlay at the band centre.  0.28 gives
            a visible but non-dominating haze; raise toward 0.50 for a strongly
            misty effect.
        blur_sigma : float
            Gaussian sigma for edge smoothing of the band weight, expressed as
            a fraction of canvas height (percent).  2.5 % gives smooth dissolve.
        opacity : float
            Global blend weight applied on top of the per-pixel mist weight.

        Notes
        -----
        Apply AFTER ``build_form()`` and atmospheric passes, BEFORE the final
        glaze.  Pairs naturally with ``atmospheric_depth_pass()`` for full
        landscape recession: ``atmospheric_depth_pass`` handles the overall
        value/saturation falloff with distance; ``horizon_mist_pass`` adds the
        specific mid-ground haze band that makes the transition read as deep
        natural space.
        """
        from scipy import ndimage as _ndimage
        import numpy as _np

        print(f"  Horizon mist pass  "
              f"(horizon_y={horizon_y:.2f}  band_height={band_height:.2f}  "
              f"mist_strength={mist_strength:.2f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Horizon mist pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA channel order: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── 1. Build 1-D band weight (Gaussian along Y) ────────────────────────
        # Peak at horizon_y, half-power radius = band_height.
        # sigma_px derived from band_height so the 1-sigma point is at the
        # band edge: sigma = band_height * h / 2 (converts fraction to pixels).
        sigma_band_px = max(1.0, band_height * h / 2.0)
        ys        = _np.arange(h, dtype=_np.float32)
        cy        = horizon_y * h
        band_1d   = _np.exp(-0.5 * ((ys - cy) / sigma_band_px) ** 2)

        # Apply additional Gaussian blur to soften band edges
        sigma_blur_px = max(1.0, blur_sigma / 100.0 * h)
        band_1d = _ndimage.gaussian_filter1d(band_1d, sigma=sigma_blur_px)

        # Clamp to [0, 1] after blur; broadcast to (H, W)
        band_1d  = _np.clip(band_1d, 0.0, 1.0)
        band_2d  = band_1d[:, _np.newaxis]   # shape (H, 1) → broadcast to (H, W)

        # Per-pixel blend weight: peak mist_strength at band centre
        weight = band_2d * mist_strength      # shape (H, W)

        # ── 2. Mist overlay blend ──────────────────────────────────────────────
        # Blend mist_color over the current pixel at the computed weight.
        # This is a standard screen-space opacity blend:
        #   out = (1 - weight) * src + weight * mist
        mr, mg, mb = mist_color

        r_out = _np.clip((1.0 - weight) * r_f + weight * mr, 0.0, 1.0)
        g_out = _np.clip((1.0 - weight) * g_f + weight * mg, 0.0, 1.0)
        b_out = _np.clip((1.0 - weight) * b_f + weight * mb, 0.0, 1.0)

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        peak_weight = float(weight.max())
        print(f"    Horizon mist pass complete  "
              f"(band_center_px={int(horizon_y * h)}  "
              f"peak_weight={peak_weight:.3f})")

    # ──────────────────────────────────────────────────────────────────────────
    # Session 50 — John Constable artist pass
    # ──────────────────────────────────────────────────────────────────────────

    def constable_cloud_sky_pass(
        self,
        sky_threshold:    float = 0.40,
        warm_top:         float = 0.16,
        cool_base:        float = 0.10,
        silver_strength:  float = 0.30,
        silver_density:   float = 0.04,
        opacity:          float = 0.72,
    ) -> None:
        """
        Build luminous English skies in the manner of John Constable.

        Constable's skies are the most technically studied element of his
        paintings.  He conducted hundreds of dedicated cloud studies from life,
        noting meteorological conditions on the verso.  His sky technique has
        three distinct registers:

        1. **Warm cream tops / cool grey undersides** — Cloud formations read
           as three-dimensional forms lit from above: the top surfaces catch
           warm direct light (cream-ivory); the undersides carry cool grey-blue
           shadow.  The overall sky tone is not a flat blue wash but a complex
           field of warm and cool passages in dialogue.

        2. **Luminous horizon** — The sky near the horizon is always lighter
           and cooler than the sky at the zenith, modelling the way atmospheric
           perspective reduces colour and value contrast near the far ground.
           This lift also provides luminosity beneath the clouds, pushing the
           sky reading as a genuine *light source* rather than a backdrop.

        3. **'Constable's snow'** — His signature impasto device: tiny dagger-
           touches of thick, undiluted white (sometimes pure lead white or
           flake white) scattered across lit cloud edges, water glints, and
           wet leaf surfaces.  These touches are not blended; they sit proud of
           the picture surface and catch raking light in a way that illusory
           white paint alone cannot.  In this pass they are simulated as sparse
           scattered bright-white pixels, slightly above the existing local tone.

        The pass operates only on the sky zone (``y < sky_threshold * h``),
        leaving the landscape below unmodified.  A soft cosine gradient feathers
        the sky-to-landscape transition so no hard band appears at the boundary.

        Strategies
        ----------
        1. **Sky gradient** — A 1-D cosine weight along Y (1.0 at top → 0.0 at
           ``sky_threshold``) modulates two simultaneous colour pushes: a warm
           cream push toward the zenith (``warm_top``) and a cool pale-blue push
           toward the horizon base of the sky zone (``cool_base``).

        2. **Silver sparkle** — A sparse binary mask (Bernoulli with probability
           ``silver_density``) restricted to the sky zone selects candidate
           pixels.  Only pixels already brighter than the local mean in their
           3×3 neighbourhood are promoted further toward (1.0, 1.0, 0.95) —
           Constable's impasto white — at strength ``silver_strength``.

        Parameters
        ----------
        sky_threshold : float
            Fraction of canvas height (from top) defining the sky zone.
            0.40 means the upper 40 % is treated as sky.
        warm_top : float
            Strength of the warm cream push (R lift, G lift, B damp) at the
            sky zenith.  0.16 gives a subtle creamy warmth without browning.
        cool_base : float
            Strength of the cool pale-blue push (B lift, R+G slight damp) at
            the base of the sky zone.  0.10 gives a gentle horizon luminosity.
        silver_strength : float
            How strongly selected pixels are pushed toward pure silver-white.
            0.30 gives convincing sparkle without over-brightening.
        silver_density : float
            Probability that any given sky pixel becomes a sparkle candidate
            before brightness-gating.  0.04 (4 %) gives a lively but not
            over-crowded scatter.
        opacity : float
            Global blend weight for the pass result over the original canvas.

        Notes
        -----
        Apply AFTER ``build_form()`` and before the final glaze.  Pairs well
        with ``atmospheric_depth_pass()`` for full landscape recession and
        ``horizon_mist_pass()`` for mid-ground haze.
        """
        import numpy as _np

        print(f"  Constable cloud sky pass  "
              f"(sky_threshold={sky_threshold:.2f}  warm_top={warm_top:.2f}  "
              f"cool_base={cool_base:.2f}  silver_strength={silver_strength:.2f}  "
              f"silver_density={silver_density:.3f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Constable cloud sky pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # Sky zone: rows 0 … sky_px-1 inclusive
        sky_px = max(1, int(sky_threshold * h))

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:sky_px, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:sky_px, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:sky_px, :, 2].astype(_np.float32) / 255.0

        # ── 1. Sky gradient — warm top → cool horizon base ───────────────────
        # cosine weight: 1.0 at row 0 (zenith), 0.0 at row sky_px-1 (horizon)
        ys         = _np.linspace(0.0, 1.0, sky_px, dtype=_np.float32)
        warm_w     = ((_np.cos(_np.pi * ys) + 1.0) * 0.5)[:, _np.newaxis]   # (sky_px, 1)
        cool_w     = (1.0 - warm_w)                                           # (sky_px, 1)

        # Warm top push: cream-ivory — lift R and G, slight B damp
        r_f = _np.clip(r_f + warm_w * warm_top * 0.90, 0.0, 1.0)
        g_f = _np.clip(g_f + warm_w * warm_top * 0.80, 0.0, 1.0)
        b_f = _np.clip(b_f - warm_w * warm_top * 0.15, 0.0, 1.0)

        # Cool base push: pale cerulean — lift B, slight R+G damp
        b_f = _np.clip(b_f + cool_w * cool_base * 1.10, 0.0, 1.0)
        r_f = _np.clip(r_f - cool_w * cool_base * 0.20, 0.0, 1.0)
        g_f = _np.clip(g_f - cool_w * cool_base * 0.10, 0.0, 1.0)

        # ── 2. Constable's silver sparkle ─────────────────────────────────────
        # Sparse bright-white impasto touches on already-lit sky pixels
        rng       = _np.random.default_rng(seed=42)
        candidate = rng.random(size=(sky_px, w), dtype=_np.float32) < silver_density

        # Brightness-gate: only promote pixels already locally bright
        lum       = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f
        bright    = lum > 0.55   # keep only pixels that are already in the light
        mask      = candidate & bright

        # Push selected pixels toward silver-white (1.0, 1.0, 0.95)
        r_f = _np.where(mask, _np.clip(r_f + silver_strength, 0.0, 1.0), r_f)
        g_f = _np.where(mask, _np.clip(g_f + silver_strength, 0.0, 1.0), g_f)
        b_f = _np.where(mask, _np.clip(b_f + silver_strength * 0.92, 0.0, 1.0), b_f)

        # ── Blend sky zone back at `opacity` ──────────────────────────────────
        buf[:sky_px, :, 2] = _np.clip(
            orig[:sky_px, :, 2] * (1.0 - opacity) + r_f * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:sky_px, :, 1] = _np.clip(
            orig[:sky_px, :, 1] * (1.0 - opacity) + g_f * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:sky_px, :, 0] = _np.clip(
            orig[:sky_px, :, 0] * (1.0 - opacity) + b_f * opacity * 255.0,
            0, 255).astype(_np.uint8)
        # Alpha and landscape zone unchanged
        buf[:sky_px, :, 3] = orig[:sky_px, :, 3]

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        sparkle_count = int(mask.sum())
        print(f"    Constable cloud sky pass complete  "
              f"(sky_px={sky_px}  sparkle_pixels={sparkle_count})")

    # ──────────────────────────────────────────────────────────────────────────
    # Session 50 — random improvement: chiaroscuro_modelling_pass
    # ──────────────────────────────────────────────────────────────────────────

    def chiaroscuro_modelling_pass(
        self,
        figure_mask:    "Optional[_np.ndarray]" = None,
        light_thresh:   float = 0.65,
        shadow_thresh:  float = 0.38,
        light_warmth:   float = 0.10,
        shadow_cool:    float = 0.08,
        shadow_deepen:  float = 0.07,
        opacity:        float = 0.68,
    ) -> None:
        """
        Enhance three-dimensional figure modelling via chiaroscuro warm/cool split.

        Chiaroscuro — Italian for 'light-dark' — is the classical technique of
        modelling solid form through a deliberate warm-to-cool tonal shift from
        the lit side to the shadow side of a figure.  It was perfected in the
        Italian Renaissance and then extended into its most extreme expression
        by Caravaggio (tenebrism) and Rembrandt (luminous impasto against deep
        shadow).  The physical basis is real: direct sunlight (or lamplight)
        is warm (high colour temperature ~3000–5500 K) while open-sky fill
        light and shadow is cool (high colour temperature ~7000–12000 K from
        scattered blue skylight).

        This pass implements the two-zone correction:

        **Light zone** (``luminance > light_thresh``) — Push toward warm ivory.
        Lift R and G slightly (toward cream), damp B slightly.  This enriches
        the sense that lit flesh is warm with blood and direct light.

        **Shadow zone** (``luminance < shadow_thresh``) — Deepen and cool
        shadows simultaneously.  Lower R+G (darker), lift B slightly (cooler).
        This prevents shadows from looking like mere grey mud and gives them
        the quality of atmospheric open-sky fill: cold, airy, and receding.

        The pass is most effective on portrait figures with a clear three-
        quarter lighting setup.  When ``figure_mask`` is provided the effect
        is spatially limited to the figure, preserving the background tone.

        Strategies
        ----------
        1. **Luminance gating** — Per-pixel luminance (BT.709 coefficients) is
           computed from the current canvas state.  Pixels are sorted into three
           zones: light, midtone (unchanged), and shadow.  A soft falloff is
           applied: the correction strength ramps from zero at the threshold to
           full at the zone extreme, avoiding a hard step.

        2. **Warm light push** — Light-zone R + G lift, B slight damp.  The
           asymmetric weighting (R > G > B) targets the ivory-amber of lit skin
           rather than a generic white push.

        3. **Cool shadow deepen** — Shadow-zone R + G damp (darkening), B lift
           (cooling).  The B lift is smaller than the R+G damp so the net effect
           is a *darker* cool, not a bright blue.

        4. **Mask compositing** — When ``figure_mask`` (float32 H×W in [0,1])
           is provided, adjustments are weighted by the mask: corrections are
           full-strength at mask=1 and zero at mask=0.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 array of shape ``(H, W)`` with values in [0, 1].  1 = fully
            inside figure, 0 = background.  If None, the pass operates on the
            full canvas.
        light_thresh : float
            Luminance threshold above which a pixel is considered 'in the
            light'.  0.65 catches highlights and upper mid-tones.
        shadow_thresh : float
            Luminance threshold below which a pixel is considered 'in shadow'.
            0.38 catches deep shadows and lower mid-tones.
        light_warmth : float
            Magnitude of the warm push on the lit side.  0.10 is noticeable
            but restrained — suitable for a Renaissance portrait.
        shadow_cool : float
            Magnitude of the B channel lift in shadow zones.  0.08 gives a
            cold-air quality without turning shadows blue.
        shadow_deepen : float
            Magnitude of the R+G channel damp in shadow zones.  0.07 darkens
            the shadows while the B lift adds coolness.
        opacity : float
            Global blend weight applied to the full adjusted layer.

        Notes
        -----
        Apply AFTER ``build_form()`` and ``sfumato_veil_pass()`` (if used),
        BEFORE the final glaze.  Pairs naturally with ``subsurface_glow_pass()``
        (warm sub-surface scatter in the lit zone amplifies the warm reading)
        and ``reflected_light_pass()`` (bounce light in shadow zones).
        """
        import numpy as _np

        print(f"  Chiaroscuro modelling pass  "
              f"(light_thresh={light_thresh:.2f}  shadow_thresh={shadow_thresh:.2f}  "
              f"light_warmth={light_warmth:.2f}  shadow_cool={shadow_cool:.2f}  "
              f"shadow_deepen={shadow_deepen:.2f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Chiaroscuro modelling pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Luminance (BT.709) ───────────────────────────────────────────────
        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f  # (H, W)

        # ── Soft zone weights ────────────────────────────────────────────────
        # light_w ramps 0→1 as lum rises from light_thresh to 1.0
        light_range = max(1e-6, 1.0 - light_thresh)
        light_w     = _np.clip((lum - light_thresh) / light_range, 0.0, 1.0)

        # shadow_w ramps 0→1 as lum falls from shadow_thresh to 0.0
        shadow_range = max(1e-6, shadow_thresh)
        shadow_w     = _np.clip(1.0 - lum / shadow_range, 0.0, 1.0)

        # ── Apply figure mask if provided ────────────────────────────────────
        if figure_mask is not None:
            fm   = _np.asarray(figure_mask, dtype=_np.float32)
            if fm.shape != (h, w):
                # resize mask to canvas dimensions if needed
                from scipy.ndimage import zoom as _zoom
                fm = _zoom(fm, (h / fm.shape[0], w / fm.shape[1]), order=1)
                fm = _np.clip(fm, 0.0, 1.0)
            light_w  = light_w  * fm
            shadow_w = shadow_w * fm

        # ── 1. Warm light push ───────────────────────────────────────────────
        r_out = _np.clip(r_f + light_w * light_warmth * 0.90, 0.0, 1.0)
        g_out = _np.clip(g_f + light_w * light_warmth * 0.70, 0.0, 1.0)
        b_out = _np.clip(b_f - light_w * light_warmth * 0.25, 0.0, 1.0)

        # ── 2. Cool shadow deepen ────────────────────────────────────────────
        r_out = _np.clip(r_out - shadow_w * shadow_deepen, 0.0, 1.0)
        g_out = _np.clip(g_out - shadow_w * shadow_deepen * 0.90, 0.0, 1.0)
        b_out = _np.clip(b_out + shadow_w * shadow_cool,   0.0, 1.0)

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]   # alpha unchanged

        # Write back to Cairo surface
        self.canvas.surface.get_data()[:] = buf.tobytes()

        light_count  = int((light_w  > 0.05).sum())
        shadow_count = int((shadow_w > 0.05).sum())
        print(f"    Chiaroscuro modelling pass complete  "
              f"(light_pixels={light_count}  shadow_pixels={shadow_count})")

    # ──────────────────────────────────────────────────────────────────────────
    # Session 51 — artist pass: bellini_sacred_light_pass
    # ──────────────────────────────────────────────────────────────────────────

    def bellini_sacred_light_pass(
        self,
        figure_mask:      "Optional[_np.ndarray]" = None,
        light_thresh:     float = 0.62,
        shadow_thresh:    float = 0.32,
        honey_warmth:     float = 0.12,
        lapis_cool:       float = 0.10,
        halo_thresh:      float = 0.82,
        halo_gold:        float = 0.06,
        opacity:          float = 0.70,
    ) -> None:
        """
        Apply the crystalline sacred luminosity of Giovanni Bellini's glazing technique.

        Bellini was the first Venetian master to fully exploit the transparency of
        oil paint as a glazing medium.  He adopted the Flemish technique (brought
        to Venice by Antonello da Messina c. 1475) and transformed it with an
        unmistakably Italian warm, golden quality.

        His sacred figures — Madonnas, saints, the enthroned Christ — glow with
        an interior warmth that is both technically and spiritually distinctive.
        The effect comes from three layered interactions:

        1. **Honey-amber glaze in the light zone** — Bellini applied a warm amber
           glaze (raw sienna diluted in oil) over the lit passages of flesh and drapery.
           This warm glaze over the cool white gesso reflector creates the characteristic
           ivory-gold quality of his lit flesh, distinct from both the cooler Flemish
           tradition and the more sfumatoed Florentine approach.

        2. **Lapis lazuli depth in shadows** — Deep shadow passages received thin
           transparent glazes of lapis lazuli or indigo, giving the shadows a cool
           blue-violet depth that recedes optically.  This warm light / cool shadow
           contrast generates the three-dimensional solidity that distinguishes his
           mature altarpieces from his earlier tempera work.

        3. **Golden halo zone in the brightest highlights** — The very brightest
           pixels — the lit crown of the head, the shoulder peak, the white of the
           eye, the knuckle highlight — receive a faint golden push toward warm
           ivory.  This simulates the slight warm lead-white highlight that Bellini
           applied as final impasto touches over the dried glaze layers, giving the
           highlights a warm, solid, material quality rather than cold specular glare.

        Strategies
        ----------
        1. **Luminance gating** — BT.709 luminance partitions pixels into three
           zones: light (``lum > light_thresh``), shadow (``lum < shadow_thresh``),
           and midtone (unchanged).  Soft ramps from the thresholds prevent banding.

        2. **Honey light push** — In the light zone: lift R and G toward warm amber,
           slight B damp.  Asymmetric weights (R 0.85, G 0.65, B −0.20) reproduce
           the warm-ivory quality of Bellini's flesh glazes — neither white nor gold,
           but the precise ivory-honey of his Madonnas.

        3. **Lapis shadow push** — In the shadow zone: lift B (lapis coolness),
           slight R damp.  The B lift is stronger than the R damp so the net result
           is a cool but not dark shadow — receding blue depth rather than black mud.

        4. **Golden halo zone** — Pixels with luminance above ``halo_thresh`` receive
           a further warm push: a gentle R + G lift (``halo_gold``) that turns the
           brightest white into warm ivory.  Keeps highlights from appearing cold.

        5. **Mask compositing** — When ``figure_mask`` is provided, all three
           corrections are weighted by the mask so the background is unaffected.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 array ``(H, W)`` in [0, 1].  1 = figure, 0 = background.
        light_thresh : float
            Luminance threshold for the light zone.  0.62 covers highlights and
            upper mid-tones without reaching into the deep midtone.
        shadow_thresh : float
            Luminance threshold below which a pixel is considered shadow.
            0.32 catches deep shadows and lower mid-tones.
        honey_warmth : float
            Magnitude of the warm honey push in the light zone.  0.12 gives a
            visible but restrained warm glow without yellowing.
        lapis_cool : float
            Magnitude of the blue (lapis) lift in shadow zones.  0.10 gives the
            cool receding quality of lapis shadow glazes.
        halo_thresh : float
            Luminance threshold above which the golden halo push applies.
            0.82 captures only the brightest highlights.
        halo_gold : float
            Strength of the warm ivory push on halo-zone pixels.  0.06 is subtle
            — a faint gold cast, not a yellow highlight.
        opacity : float
            Global blend weight for the pass result over the original canvas.

        Notes
        -----
        Apply AFTER ``build_form()`` and before the final glaze.  Pairs naturally
        with ``venetian_glaze_pass()`` (adds further warm oil depth), ``subsurface_
        glow_pass()`` (warm SSS reinforces the honey light zone), and
        ``sfumato_veil_pass()`` (if used — apply sfumato before this pass so the
        warm glow overlays the softened edges).
        """
        import numpy as _np

        print(f"  Bellini sacred light pass  "
              f"(light_thresh={light_thresh:.2f}  shadow_thresh={shadow_thresh:.2f}  "
              f"honey_warmth={honey_warmth:.2f}  lapis_cool={lapis_cool:.2f}  "
              f"halo_thresh={halo_thresh:.2f}  halo_gold={halo_gold:.2f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Bellini sacred light pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Luminance (BT.709) ───────────────────────────────────────────────
        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        # ── Soft zone weights ────────────────────────────────────────────────
        light_range = max(1e-6, 1.0 - light_thresh)
        light_w     = _np.clip((lum - light_thresh) / light_range, 0.0, 1.0)

        shadow_range = max(1e-6, shadow_thresh)
        shadow_w     = _np.clip(1.0 - lum / shadow_range, 0.0, 1.0)

        halo_range   = max(1e-6, 1.0 - halo_thresh)
        halo_w       = _np.clip((lum - halo_thresh) / halo_range, 0.0, 1.0)

        # ── Apply figure mask if provided ────────────────────────────────────
        if figure_mask is not None:
            fm = _np.asarray(figure_mask, dtype=_np.float32)
            if fm.shape != (h, w):
                from scipy.ndimage import zoom as _zoom
                fm = _zoom(fm, (h / fm.shape[0], w / fm.shape[1]), order=1)
                fm = _np.clip(fm, 0.0, 1.0)
            light_w  = light_w  * fm
            shadow_w = shadow_w * fm
            halo_w   = halo_w   * fm

        # ── 1. Honey-amber light push ─────────────────────────────────────────
        r_out = _np.clip(r_f + light_w * honey_warmth * 0.85, 0.0, 1.0)
        g_out = _np.clip(g_f + light_w * honey_warmth * 0.65, 0.0, 1.0)
        b_out = _np.clip(b_f - light_w * honey_warmth * 0.20, 0.0, 1.0)

        # ── 2. Lapis lazuli shadow push ───────────────────────────────────────
        r_out = _np.clip(r_out - shadow_w * lapis_cool * 0.35, 0.0, 1.0)
        g_out = _np.clip(g_out - shadow_w * lapis_cool * 0.10, 0.0, 1.0)
        b_out = _np.clip(b_out + shadow_w * lapis_cool * 1.00, 0.0, 1.0)

        # ── 3. Golden halo zone ───────────────────────────────────────────────
        r_out = _np.clip(r_out + halo_w * halo_gold * 1.00, 0.0, 1.0)
        g_out = _np.clip(g_out + halo_w * halo_gold * 0.80, 0.0, 1.0)
        # B unchanged in halo zone — keep highlights warm ivory, not white

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        light_count  = int((light_w  > 0.05).sum())
        shadow_count = int((shadow_w > 0.05).sum())
        halo_count   = int((halo_w   > 0.05).sum())
        print(f"    Bellini sacred light pass complete  "
              f"(light_px={light_count}  shadow_px={shadow_count}  halo_px={halo_count})")

    # ──────────────────────────────────────────────────────────────────────────
    # Session 51 — random improvement: penumbra_zone_pass
    # ──────────────────────────────────────────────────────────────────────────

    def penumbra_zone_pass(
        self,
        figure_mask:      "Optional[_np.ndarray]" = None,
        light_thresh:     float = 0.62,
        shadow_thresh:    float = 0.35,
        penumbra_warmth:  float = 0.08,
        penumbra_chroma:  float = 0.06,
        opacity:          float = 0.65,
    ) -> None:
        """
        Enrich the penumbra zone — the transition between lit and shadow flesh.

        The penumbra is the soft band of transitional tone between the directly lit
        surface of a face and the shadowed side.  In life this zone has a subtle
        but important warm-rosy quality: the blood vessels beneath the skin are
        most visible in this transitional zone where the surface curves away from
        the light, and where subsurface scattering is strongest.

        Classical painters understood this empirically.  Rubens called it the
        *"demitint"* (half-tone); his flesh glazes were warmest not in the full
        light but in this transitional zone.  Rembrandt's penumbra passages carry
        a warm amber-brown glow.  Titian's demi-tints are the most celebrated in
        Western painting: a warm peach-sienna passage that makes his flesh appear
        genuinely alive rather than painted.

        This pass targets exactly this zone — the luminance band between
        ``shadow_thresh`` and ``light_thresh`` — and applies a gentle warm blush
        (slight R and G lift) plus a modest chroma boost (saturation increase in
        the midtone) to make the transitional flesh more vivid and alive.

        Strategies
        ----------
        1. **Penumbra weight** — The weight function is a tent shape: 0 at both
           the light threshold and the shadow threshold, reaching maximum 1.0 at
           the midpoint of the two.  This ensures the correction is strongest in
           the true penumbra centre and fades smoothly to zero at both edges,
           avoiding any hard step at either boundary.

        2. **Warm blush** — A gentle R lift (``penumbra_warmth × 0.80``) and
           G lift (``× 0.45``) with no B change pushes toward warm peach-rose
           in the penumbra.  This reproduces the warm blood-flush visible in life
           at the light-to-shadow transition of the cheeks and temples.

        3. **Chroma boost** — The penumbra zone also receives a modest saturation
           increase: the RGB values are pushed away from their luminance (toward
           their chroma direction) by ``penumbra_chroma``.  This prevents the warm
           blush from looking washed-out and gives the transitional zone the
           vibrant living quality of Titian's demi-tints.

        4. **Mask compositing** — When ``figure_mask`` is provided, corrections are
           weighted by the mask, confining the blush to the figure and leaving the
           background neutral.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 array ``(H, W)`` in [0, 1].  1 = figure, 0 = background.
        light_thresh : float
            Upper luminance boundary of the penumbra zone.  Pixels above this
            are in the full light and receive no blush.  0.62 matches the default
            light zone threshold of chiaroscuro_modelling_pass().
        shadow_thresh : float
            Lower luminance boundary of the penumbra zone.  Pixels below this
            are in deep shadow and receive no blush.  0.35 catches the upper
            shadow fringe rather than the deep void.
        penumbra_warmth : float
            Magnitude of the warm blush R+G push in the penumbra zone.  0.08
            is subtly visible — a warm flush, not a paint-bucket fill.
        penumbra_chroma : float
            Magnitude of the chroma (saturation) boost in the penumbra.  0.06
            enriches the blush without over-saturating.
        opacity : float
            Global blend weight for the pass result over the original canvas.

        Notes
        -----
        Apply AFTER ``build_form()`` and ``chiaroscuro_modelling_pass()`` (if
        used) so the warm/cool split is already established before the penumbra
        enrichment is applied.  Pairs naturally with ``subsurface_glow_pass()``
        (warm SSS in the light zone extends into the penumbra) and
        ``reflected_light_pass()`` (the cool shadow bounce sets the dark boundary
        of the zone this pass enriches).
        """
        import numpy as _np

        print(f"  Penumbra zone pass  "
              f"(light_thresh={light_thresh:.2f}  shadow_thresh={shadow_thresh:.2f}  "
              f"penumbra_warmth={penumbra_warmth:.2f}  penumbra_chroma={penumbra_chroma:.2f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Penumbra zone pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Luminance (BT.709) ───────────────────────────────────────────────
        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        # ── Penumbra tent weight ──────────────────────────────────────────────
        # Tent: peaks at the midpoint of [shadow_thresh, light_thresh], 0 outside.
        mid = (light_thresh + shadow_thresh) * 0.5
        half_width = max(1e-6, (light_thresh - shadow_thresh) * 0.5)
        pen_w = _np.clip(1.0 - _np.abs(lum - mid) / half_width, 0.0, 1.0)

        # ── Apply figure mask if provided ────────────────────────────────────
        if figure_mask is not None:
            fm = _np.asarray(figure_mask, dtype=_np.float32)
            if fm.shape != (h, w):
                from scipy.ndimage import zoom as _zoom
                fm = _zoom(fm, (h / fm.shape[0], w / fm.shape[1]), order=1)
                fm = _np.clip(fm, 0.0, 1.0)
            pen_w = pen_w * fm

        # ── 1. Warm blush push ────────────────────────────────────────────────
        r_out = _np.clip(r_f + pen_w * penumbra_warmth * 0.80, 0.0, 1.0)
        g_out = _np.clip(g_f + pen_w * penumbra_warmth * 0.45, 0.0, 1.0)
        b_out = b_f.copy()   # B unchanged — a red-gold blush, not orange

        # ── 2. Chroma boost in penumbra zone ──────────────────────────────────
        # Push RGB away from their luminance toward their chroma direction.
        # delta = (r, g, b) − lum → normalize, then push outward
        lum3 = lum[:, :, _np.newaxis] if lum.ndim == 2 else lum
        rgb  = _np.stack([r_out, g_out, b_out], axis=-1)   # (H, W, 3)
        lum_s = lum[:, :, None]
        delta = rgb - lum_s   # colour deviation from grey (H, W, 3)
        chroma_push = pen_w[:, :, None] * penumbra_chroma
        rgb_boosted = _np.clip(rgb + delta * chroma_push, 0.0, 1.0)
        r_out, g_out, b_out = rgb_boosted[..., 0], rgb_boosted[..., 1], rgb_boosted[..., 2]

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        pen_count = int((pen_w > 0.05).sum())
        print(f"    Penumbra zone pass complete  (penumbra_pixels={pen_count})")

    # ──────────────────────────────────────────────────────────────────────────
    # Session 52 — new artist: Pontormo / FLORENTINE_MANNERIST
    # ──────────────────────────────────────────────────────────────────────────

    def pontormo_dissonance_pass(
        self,
        figure_mask:      "Optional[_np.ndarray]" = None,
        light_thresh:     float = 0.60,
        shadow_thresh:    float = 0.32,
        acid_lift:        float = 0.14,
        violet_push:      float = 0.12,
        midtone_chroma:   float = 0.10,
        opacity:          float = 0.68,
    ) -> None:
        """
        Apply Pontormo's signature chromatic dissonance to the canvas.

        Jacopo Pontormo (1494–1557) abandoned the warm harmonic colour systems
        of the High Renaissance in favour of a deliberately unsettling palette:
        acid chartreuse in the lights, cold violet-black in the shadows, and a
        competing tension of rose and chartreuse in the midtones that denies the
        viewer a comfortable resting point.  The effect is one of sustained
        chromatic anxiety — a visual correlate of the psychological intensity
        that characterises his greatest work, the Deposition from the Cross
        (Capponi Chapel, Florence, c.1525–28).

        This pass applies three distinct zone corrections:

        1. **Highlight zone** (``lum > light_thresh``): Pushes the lit passages
           toward acid lemon-yellow by lifting R strongly and G moderately while
           reducing B.  This produces the characteristic cold-warm paradox of
           Pontormo's lights — they are bright but not warm in the conventional
           ivory-to-gold sense; instead they carry the acid quality of a lemon
           or chartreuse that sits at the hot-cool boundary.

        2. **Shadow zone** (``lum < shadow_thresh``): Pushes the shadow
           passages toward cool violet-black by reducing R and boosting B
           significantly.  Pontormo's shadows are not warm Rembrandt umbers;
           they are cold, slightly purple-tinged near-blacks that make the
           surrounding acid colours appear even more dissonant by contrast.

        3. **Midtone zone**: Applies a spatially modulated chroma push: pixels
           in the left half of the canvas receive a rose-carmine pull (R boost,
           slight B push) while pixels in the right half receive a chartreuse
           pull (G boost, R moderate).  This creates the competing colour
           tension across the midtone band that reads as Pontormo's instinctive
           refusal to let any colour zone fully resolve into harmonic agreement
           with its neighbours.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 array ``(H, W)`` in [0, 1].  When provided, the correction
            is weighted by the mask so the dissonance is strongest on the figure
            and fades toward the neutral background.
        light_thresh : float
            Luminance boundary above which the acid-yellow highlight push is
            applied.  0.60 catches the upper midtone zone as well as the
            direct lights, giving a broad, assertive acid highlight zone.
        shadow_thresh : float
            Luminance boundary below which the violet-black shadow push is
            applied.  0.32 targets the core shadow without eating into the
            penumbra zone, which is left for the midtone correction.
        acid_lift : float
            Strength of the acid lemon-yellow highlight push.  0.14 is a
            visible, assertive lift — Pontormo's highlights are unmistakably
            acid, not subtle.
        violet_push : float
            Strength of the violet-black shadow push.  0.12 gives a clearly
            cooler, more purple shadow without becoming a digital chroma-key.
        midtone_chroma : float
            Strength of the spatial rose/chartreuse chroma pull in the midtone
            zone.  0.10 is a moderate pull — visible in the midtones without
            dominating the composition.
        opacity : float
            Global blend weight for the entire pass over the original canvas.

        Notes
        -----
        Apply AFTER ``build_form()`` and before final glaze.  Pairs with a cool
        grey ``glaze()`` (not warm amber) to reinforce the Mannerist palette.
        Do NOT combine with ``sfumato_veil_pass()`` — sfumato warms and softens;
        Pontormo's dissonance requires crisp, unsmoked colour zones.
        """
        import numpy as _np

        print(f"  Pontormo dissonance pass  "
              f"(light_thresh={light_thresh:.2f}  shadow_thresh={shadow_thresh:.2f}  "
              f"acid_lift={acid_lift:.2f}  violet_push={violet_push:.2f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Pontormo dissonance pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Luminance (BT.709) ───────────────────────────────────────────────
        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        # ── Zone weights ─────────────────────────────────────────────────────
        light_w  = _np.clip((lum - light_thresh) / (1.0 - light_thresh + 1e-6), 0.0, 1.0)
        shadow_w = _np.clip((shadow_thresh - lum) / (shadow_thresh + 1e-6), 0.0, 1.0)
        mid_w    = _np.clip(1.0 - light_w - shadow_w, 0.0, 1.0)

        # ── Spatial left/right split for midtone dissonance ──────────────────
        # xs: 0.0 at left edge, 1.0 at right edge — (H, W) broadcast
        xs = _np.linspace(0.0, 1.0, w, dtype=_np.float32)[_np.newaxis, :]  # (1, W)
        rose_w  = mid_w * _np.clip(0.55 - xs, 0.0, 1.0) * 2.0   # left → rose
        chart_w = mid_w * _np.clip(xs - 0.45, 0.0, 1.0) * 2.0   # right → chartreuse

        # ── Apply figure mask ────────────────────────────────────────────────
        if figure_mask is not None:
            fm = _np.asarray(figure_mask, dtype=_np.float32)
            if fm.shape != (h, w):
                from scipy.ndimage import zoom as _zoom
                fm = _zoom(fm, (h / fm.shape[0], w / fm.shape[1]), order=1)
                fm = _np.clip(fm, 0.0, 1.0)
            light_w  = light_w  * fm
            shadow_w = shadow_w * fm
            rose_w   = rose_w   * fm
            chart_w  = chart_w  * fm

        # ── 1. Acid lemon-yellow highlight push ───────────────────────────────
        # R up strong, G up moderate, B down — acid chartreuse-yellow
        r_out = _np.clip(r_f + light_w * acid_lift * 1.00, 0.0, 1.0)
        g_out = _np.clip(g_f + light_w * acid_lift * 0.75, 0.0, 1.0)
        b_out = _np.clip(b_f - light_w * acid_lift * 0.55, 0.0, 1.0)

        # ── 2. Violet-black shadow push ───────────────────────────────────────
        # R down, G slightly down, B up — cool violet-black
        r_out = _np.clip(r_out - shadow_w * violet_push * 0.90, 0.0, 1.0)
        g_out = _np.clip(g_out - shadow_w * violet_push * 0.30, 0.0, 1.0)
        b_out = _np.clip(b_out + shadow_w * violet_push * 0.60, 0.0, 1.0)

        # ── 3. Midtone spatial dissonance ─────────────────────────────────────
        # Left: rose-carmine pull (R up, slight B up)
        r_out = _np.clip(r_out + rose_w  * midtone_chroma * 0.80, 0.0, 1.0)
        b_out = _np.clip(b_out + rose_w  * midtone_chroma * 0.20, 0.0, 1.0)
        # Right: chartreuse pull (G up, R moderate up, B down)
        r_out = _np.clip(r_out + chart_w * midtone_chroma * 0.45, 0.0, 1.0)
        g_out = _np.clip(g_out + chart_w * midtone_chroma * 0.85, 0.0, 1.0)
        b_out = _np.clip(b_out - chart_w * midtone_chroma * 0.40, 0.0, 1.0)

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        light_count  = int((light_w  > 0.05).sum())
        shadow_count = int((shadow_w > 0.05).sum())
        mid_count    = int((mid_w    > 0.05).sum())
        print(f"    Pontormo dissonance pass complete  "
              f"(light_px={light_count}  shadow_px={shadow_count}  mid_px={mid_count})")

    # ──────────────────────────────────────────────────────────────────────────
    # Session 52 — random improvement: aerial_perspective_pass
    # ──────────────────────────────────────────────────────────────────────────

    def aerial_perspective_pass(
        self,
        sky_band:             float = 0.45,
        fade_power:           float = 2.2,
        desaturation:         float = 0.55,
        cool_push:            float = 0.10,
        haze_lift:            float = 0.06,
        opacity:              float = 0.72,
        warm_foreground_push: float = 0.0,
        fg_band:              float = 0.35,
    ) -> None:
        """
        Apply systematic aerial (atmospheric) perspective to the upper canvas zone.

        Aerial perspective — the optical phenomenon by which distant objects
        appear lighter, bluer, and less saturated than near objects — was first
        codified by Leonardo da Vinci in his notebooks and is visible in the
        Mona Lisa's famous hazy background landscape.  The principle derives from
        the physical reality that atmospheric particles (water vapour, dust,
        aerosols) scatter shorter wavelengths (blue) preferentially and absorb
        longer wavelengths (red, green), causing the following perceptual shifts
        with increasing distance:

        - **Desaturation**: colours lose their purity, converging toward neutral grey
        - **Cool push**: the residual hue drifts toward blue-grey (atmospheric blue)
        - **Value lift**: shadows lighten toward the atmospheric tone (near-white haze)
        - **Edge softening**: distant contours dissolve into the ambient atmosphere

        This pass applies a vertical weight gradient — maximum at the top of the
        canvas (sky and far horizon), fading to zero at ``sky_band * H`` — and
        applies three corrections weighted by that gradient:

        1. **Desaturation**: pixels are blended toward their BT.709 luminance
           (grey) by ``desaturation × weight``.  This models the loss of chroma
           that accumulates over distance as atmospheric particles scatter colour
           out of the light path.

        2. **Cool push**: the desaturated result is pushed further toward cool
           blue-grey by boosting B and reducing R in proportion to ``cool_push``
           and the atmospheric weight.  This models the preferential scattering
           of short-wavelength (blue) light, which tints the atmosphere itself
           blue and simultaneously removes the warm wavelengths from distant objects.

        3. **Haze lift**: the overall luminance in the atmospheric zone is raised
           by ``haze_lift × weight``.  In nature, the atmospheric column between
           the observer and a distant surface adds a veil of semi-luminous haze;
           even a dark distant mountain reads lighter than a nearby shadow of
           the same tonal value.

        Parameters
        ----------
        sky_band : float
            Fractional height from the top of the canvas over which the
            atmospheric effect is applied.  0.45 = upper 45% of the image.
            Below this line the weight fades to zero and the pass has no effect.
        fade_power : float
            Power exponent of the vertical weight gradient.  Higher values make
            the effect more concentrated at the very top (faster fade from the
            top edge).  2.2 gives a natural-looking quadratic falloff that
            matches the perceptual experience of aerial perspective.
        desaturation : float
            Maximum desaturation applied at the top of the canvas.  0.55 gives
            a clearly atmospheric haze in the far sky zone; 0.0 disables
            desaturation while allowing the cool push and haze lift alone.
        cool_push : float
            Maximum blue-grey push applied at the top.  0.10 is a gentle but
            clearly visible cool shift in the sky zone.
        haze_lift : float
            Maximum luminance lift applied at the top.  0.06 is a subtle veil
            of atmospheric light — visible in the distant sky but not washing
            out foreground tones (which receive near-zero weight).
        opacity : float
            Global blend weight for the pass result over the original canvas.
        warm_foreground_push : float
            **Improvement (session 59+):** When > 0, applies a complementary
            warm push to the lower foreground zone — the inverse of the cool
            atmospheric push applied to the sky.  This implements the complete
            atmospheric perspective principle: not only does distance make
            objects cooler and more desaturated, but proximity makes them
            comparatively warmer and more saturated.  Venetian painters —
            Titian, Tiepolo, Veronese — consistently exploited this contrast:
            foreground figures glow with warm ochre and vermilion while the
            background recedes into cool grey-blue haze.

            The warm push boosts R slightly and suppresses B slightly in the
            lower ``fg_band`` fraction of the canvas, weighted by a gradient
            that peaks at the bottom edge and fades to zero at ``fg_band * H``.
            At ``warm_foreground_push=0.08`` the foreground receives a subtle
            but perceptible warmth relative to the sky zone; at 0.15 the
            contrast is more theatrical (appropriate for Tiepolo or Rubens).
            Default 0.0 preserves the existing behaviour exactly.
        fg_band : float
            Fractional height from the bottom of the canvas over which the
            warm foreground push is applied.  0.35 = lower 35% of the image.
            Has no effect if ``warm_foreground_push`` is 0.

        Notes
        -----
        Apply AFTER ``build_form()`` and before ``place_lights()`` so the
        atmospheric haze is established before the final light accents are
        placed.  Pairs especially well with ``sfumato_veil_pass()`` (which
        softens edges) and ``tonal_envelope_pass()`` (which enriches the
        foreground figure separately from the receding background).  Do NOT
        apply to images with no landscape or sky zone — the effect has no
        meaning on flat-background portrait compositions.
        """
        import numpy as _np

        print(f"  Aerial perspective pass  "
              f"(sky_band={sky_band:.2f}  fade_power={fade_power:.2f}  "
              f"desaturation={desaturation:.2f}  cool_push={cool_push:.2f}  "
              f"haze_lift={haze_lift:.2f}  opacity={opacity:.2f}  "
              f"warm_fg={warm_foreground_push:.3f}) ...")

        if opacity <= 0.0:
            print("    Aerial perspective pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Vertical weight: 1.0 at top row, fading to 0 at sky_band * H ─────
        # ys: normalised position within the sky band [0 = top, 1 = bottom of band]
        sky_px = max(1, int(h * sky_band))
        ys = _np.linspace(0.0, 1.0, sky_px, dtype=_np.float32)   # (sky_px,)
        atm_weight_1d = _np.clip(1.0 - ys, 0.0, 1.0) ** fade_power  # (sky_px,)

        # Expand to full canvas height: zeros for rows below sky_band
        atm_w = _np.zeros((h,), dtype=_np.float32)
        atm_w[:sky_px] = atm_weight_1d
        atm_w = atm_w[:, _np.newaxis]   # (H, 1) — broadcast over W

        # ── 1. Desaturate toward luminance ────────────────────────────────────
        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f   # (H, W)
        desat = atm_w * desaturation   # (H, W)
        r_out = r_f * (1.0 - desat) + lum * desat
        g_out = g_f * (1.0 - desat) + lum * desat
        b_out = b_f * (1.0 - desat) + lum * desat

        # ── 2. Cool push: boost B, reduce R, toward atmospheric blue-grey ─────
        cool = atm_w * cool_push
        r_out = _np.clip(r_out - cool * 0.80, 0.0, 1.0)
        g_out = _np.clip(g_out - cool * 0.15, 0.0, 1.0)
        b_out = _np.clip(b_out + cool * 0.60, 0.0, 1.0)

        # ── 3. Haze lift: raise overall luminance in atmospheric zone ─────────
        haze = atm_w * haze_lift
        r_out = _np.clip(r_out + haze, 0.0, 1.0)
        g_out = _np.clip(g_out + haze, 0.0, 1.0)
        b_out = _np.clip(b_out + haze, 0.0, 1.0)

        # ── 4. Warm foreground push (session 59 improvement) ─────────────────
        # Applies the complementary half of atmospheric perspective: not only
        # does distance cool and desaturate, but proximity comparatively warms
        # and saturates.  Venetian masters (Titian, Tiepolo, Veronese) relied
        # on this contrast.  The gradient mirrors the sky band — maximum weight
        # at the bottom row, fading to zero at fg_band * H from the bottom.
        if warm_foreground_push > 0.0:
            fg_px = max(1, int(h * fg_band))
            # ys_fg: 0 at the bottom row, 1 at the top of the fg_band
            ys_fg = _np.linspace(0.0, 1.0, fg_px, dtype=_np.float32)
            fg_weight_1d = _np.clip(1.0 - ys_fg, 0.0, 1.0) ** fade_power
            fg_w = _np.zeros((h,), dtype=_np.float32)
            # fg_weight_1d[0] = bottom-most row of the fg_band → maps to h-1
            fg_w[h - fg_px:] = fg_weight_1d[::-1]
            fg_w = fg_w[:, _np.newaxis]   # (H, 1) — broadcast over W
            warm = fg_w * warm_foreground_push
            # Warm push: boost R, modest G, suppress B — Naples yellow / ochre push
            r_out = _np.clip(r_out + warm * 0.85, 0.0, 1.0)
            g_out = _np.clip(g_out + warm * 0.30, 0.0, 1.0)
            b_out = _np.clip(b_out - warm * 0.45, 0.0, 1.0)

        # ── Blend adjusted layer back at `opacity` ────────────────────────────
        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - opacity) + r_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - opacity) + g_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - opacity) + b_out * opacity * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        atm_count = int((atm_w.squeeze() > 0.05).sum() * w)
        print(f"    Aerial perspective pass complete  (affected_px~{atm_count})")

    # ──────────────────────────────────────────────────────────────────────────
    # Session 53 — new artist: Rogier van der Weyden / weyden_angular_shadow_pass
    # ──────────────────────────────────────────────────────────────────────────

    def weyden_angular_shadow_pass(
        self,
        figure_mask:      "Optional[_np.ndarray]" = None,
        shadow_thresh:    float = 0.38,
        light_thresh:     float = 0.60,
        edge_sharpen:     float = 0.55,
        shadow_cool:      float = 0.08,
        highlight_cool:   float = 0.04,
        opacity:          float = 0.70,
    ) -> None:
        """
        Apply Rogier van der Weyden's angular, geometric shadow modelling.

        Rogier van der Weyden (c. 1399/1400–1464) achieved emotional intensity
        through the precise geometry of light and shadow.  Unlike Leonardo's
        sfumato — which dissolves tonal transitions into imperceptible atmospheric
        haze — Weyden's shadows have clean, angular found edges that describe the
        geometry of folded drapery with almost architectural clarity.  A cloth fold
        passes from brilliantly lit surface to near-black shadow in a single,
        sharp step.  This gives his robes, mantles, and shrouds the quality of
        carved stone: every plane fully resolved, every edge intentional.

        His flesh is correspondingly pale — almost waxen — with cool blue-tinged
        shadows rather than the warm ambers of Rembrandt or the glowing umbers of
        Titian.  The coolness in the shadows reads as a kind of spiritual rigour:
        where Rubens's flesh glows with vitality, Weyden's flesh endures with
        austere, grief-stricken dignity.

        This pass applies three distinct operations:

        1. **Shadow zone cooling** (``lum < shadow_thresh``): Shadow pixels
           receive a slight cool-violet push — R is reduced and B is lifted
           by ``shadow_cool``.  This gives the characteristic Flemish cool-
           shadow quality that distinguishes Weyden from the warm Venetians.

        2. **Edge sharpening at the penumbra boundary**: The pixels in the
           narrow band around the shadow threshold are pushed toward their
           extreme (toward full shadow or full light, depending on which side
           of the boundary they fall).  This is a local contrast stretch at
           the transition zone only — replicating the effect of a found edge.
           The strength is controlled by ``edge_sharpen``.

        3. **Highlight cooling** (``lum > light_thresh``): The lit passages
           receive a subtle cool-ivory push — a slight B lift by
           ``highlight_cool``.  Weyden's lit flesh is not warm ivory (as in
           Titian or Rembrandt) but pale, slightly cool — almost the tonality
           of white linen rather than warm skin.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 array ``(H, W)`` in [0, 1].  1 = figure, 0 = background.
            When provided, all corrections are composited only within the figure.
        shadow_thresh : float
            Luminance boundary below which pixels are treated as shadow.
            Default 0.38 matches a slightly deeper shadow zone than the
            penumbra_zone_pass boundary, capturing the full Flemish shadow void.
        light_thresh : float
            Luminance boundary above which pixels are treated as lit.
            Default 0.60 — a broad, bright-lit zone for pale Flemish flesh.
        edge_sharpen : float
            Strength of the found-edge contrast push at the light-shadow boundary.
            0.0 = no sharpening (smooth transition preserved); 1.0 = maximum
            push (extreme jump from lit to shadow at each boundary pixel).
            Default 0.55 — strong but not posterised.
        shadow_cool : float
            Magnitude of the cool-violet push in shadow zones.  Reduces R,
            lifts B.  0.08 produces a subtle but clearly visible cool shift.
        highlight_cool : float
            Magnitude of the pale-ivory cool lift in fully lit zones.  Lifts
            B gently.  0.04 is a light correction — barely perceptible alone
            but collectively shifts the flesh tonality from warm to pale.
        opacity : float
            Global blend factor: 0 = no effect, 1 = full correction applied.

        Notes
        -----
        Apply AFTER ``build_form()`` and before ``glaze()`` so the geometric
        shadow structure is established before any warm unifying layer is applied
        (a warm glaze applied afterward will slightly mellow the coolness —
        exactly as Weyden's oak panel ground does in his originals).
        Pairs well with ``holbein_jewel_glaze_pass()`` for panel-painting finish
        and ``edge_lost_and_found_pass()`` for final edge refinement.
        """
        import numpy as _np

        print(f"  Weyden angular shadow pass  "
              f"(shadow_thresh={shadow_thresh:.2f}  light_thresh={light_thresh:.2f}  "
              f"edge_sharpen={edge_sharpen:.2f}  shadow_cool={shadow_cool:.2f}  "
              f"highlight_cool={highlight_cool:.2f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Weyden angular shadow pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f   # (H, W)

        # ── Figure mask weight ────────────────────────────────────────────────
        if figure_mask is not None:
            mask_w = _np.clip(
                _np.array(figure_mask, dtype=_np.float32), 0.0, 1.0
            )
            if mask_w.shape != (h, w):
                from PIL import Image as _Img
                mask_w = _np.array(
                    _Img.fromarray((mask_w * 255).astype(_np.uint8)).resize(
                        (w, h), _Img.BILINEAR
                    ), dtype=_np.float32
                ) / 255.0
        else:
            mask_w = _np.ones((h, w), dtype=_np.float32)

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── 1. Shadow zone cooling (lum < shadow_thresh) ─────────────────────
        # Push deep shadows toward cool violet: reduce R, lift B.
        shadow_zone = (lum < shadow_thresh).astype(_np.float32)
        r_out = _np.clip(r_out - shadow_zone * shadow_cool * 0.85, 0.0, 1.0)
        b_out = _np.clip(b_out + shadow_zone * shadow_cool * 0.70, 0.0, 1.0)

        # ── 2. Edge sharpening at the penumbra boundary ───────────────────────
        # The penumbra band is the zone between shadow_thresh and light_thresh.
        # Within this band, push each pixel toward whichever extreme (lit or
        # shadow) it is closest to — creating a sharper step at the boundary.
        penumbra_band = ((lum >= shadow_thresh) & (lum < light_thresh)).astype(
            _np.float32
        )
        # Normalised position within the band: 0 = deep shadow edge, 1 = light edge
        band_width = max(light_thresh - shadow_thresh, 1e-6)
        pos_in_band = _np.clip(
            (lum - shadow_thresh) / band_width, 0.0, 1.0
        )   # 0 near shadow, 1 near light

        # Pixels in the lower half of the band → push toward shadow (darken)
        # Pixels in the upper half of the band → push toward light (brighten)
        push_direction = (pos_in_band - 0.5) * 2.0   # [-1, +1]
        edge_correction = penumbra_band * edge_sharpen * push_direction * 0.15

        r_out = _np.clip(r_out + edge_correction, 0.0, 1.0)
        g_out = _np.clip(g_out + edge_correction * 0.85, 0.0, 1.0)
        b_out = _np.clip(b_out + edge_correction * 0.70, 0.0, 1.0)

        # ── 3. Highlight cooling (lum > light_thresh) ─────────────────────────
        # Weyden's lit flesh is cool pale ivory, not warm gold.  Lift B gently.
        light_zone = (lum >= light_thresh).astype(_np.float32)
        b_out = _np.clip(b_out + light_zone * highlight_cool, 0.0, 1.0)

        # ── Blend corrected layer back at `opacity`, weighted by mask ─────────
        blend = opacity * mask_w

        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - blend) + r_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - blend) + g_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - blend) + b_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        shadow_count    = int((shadow_zone > 0.5).sum())
        highlight_count = int((light_zone  > 0.5).sum())
        print(f"    Weyden angular shadow pass complete  "
              f"(shadow_px={shadow_count}  highlight_px={highlight_count})")

    # ──────────────────────────────────────────────────────────────────────────
    # Session 54 — new artist: Hans Memling / memling_jewel_light_pass
    # ──────────────────────────────────────────────────────────────────────────

    def memling_jewel_light_pass(
        self,
        figure_mask:         "Optional[_np.ndarray]" = None,
        highlight_thresh:    float = 0.72,
        midtone_low:         float = 0.32,
        midtone_high:        float = 0.58,
        jewel_strength:      float = 0.07,
        subsurface_strength: float = 0.055,
        opacity:             float = 0.72,
    ) -> None:
        """
        Apply Hans Memling's crystalline jewel-light luminosity to the canvas.

        Hans Memling (c. 1430/1440–1494) — trained in Rogier van der Weyden's
        Brussels workshop — transformed Early Netherlandish technique into a
        world of serene, jewel-like luminosity.  Where Weyden's shadows are
        tense and architectural, Memling's lights are warm and crystalline:
        the brightest highlight passages read as polished enamel — brilliant,
        cold, and luminous rather than simply pale.

        He achieved this through stacked transparent oil glazes on a chalk-
        white gesso ground.  Each glaze layer (lead white + pale ochre) was
        dried separately, so light could pass through the paint film, reflect
        from the white ground, and exit cooled and brightened.  The result:
        highlights that have interior depth rather than surface opaqueness.

        The other defining quality is the blue-green coolness in the shadow
        transitions of his flesh.  Unlike Rembrandt's warm amber shadows or
        Titian's glowing umbers, Memling's mid-tones carry a subtle blue-green
        undertone — the Flemish subsurface quality — that reads as translucent
        skin with light scattering through it before exiting.

        This pass applies two operations:

        1. **Jewel-highlight push** (``lum > highlight_thresh``): The brightest
           pixels are pushed toward cool pale ivory — R is gently reduced and
           B is lifted, making the highlights read as slightly cooler and more
           luminous than the warm mid-tones.  Unlike Rembrandt's warm golden
           highlights, Memling's lights are almost white with a faint blue
           quality, like the reflection from polished silver.  Controlled by
           ``jewel_strength``.

        2. **Subsurface mid-tone tint** (``midtone_low ≤ lum < midtone_high``):
           The shadow-transition zone receives a gentle blue-green push — G
           and B lifted slightly, R reduced fractionally.  This mimics the
           effect of light scattering through translucent skin and exiting
           slightly cooled and greenish.  Controlled by ``subsurface_strength``.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 array ``(H, W)`` in [0, 1].  1 = figure, 0 = background.
            When provided, corrections are applied only within the figure.
        highlight_thresh : float
            Luminance threshold above which pixels are treated as bright
            highlights.  Default 0.72 — a high value to target only the
            genuine enamel-bright specular zones, not the mid-tones.
        midtone_low : float
            Lower luminance bound for the subsurface mid-tone band.
            Default 0.32 — below this the shadows are too deep for the
            translucent effect.
        midtone_high : float
            Upper luminance bound for the subsurface mid-tone band.
            Default 0.58 — above this the flesh begins to be clearly lit.
        jewel_strength : float
            Magnitude of the cool ivory push in the highlight zone.  Lifts B,
            reduces R fractionally.  Default 0.07 — visible but not stark.
        subsurface_strength : float
            Magnitude of the blue-green push in the mid-tone shadow zone.
            Lifts G and B, reduces R slightly.  Default 0.055 — a subtle
            glowing coolness rather than an obvious colour shift.
        opacity : float
            Global blend factor: 0 = no effect, 1 = full correction.

        Notes
        -----
        Apply AFTER ``build_form()`` — the subsurface quality is a refinement
        of the modelled form, not a substitute for it.  Works well before a
        warm ``glaze()`` call: the warm glaze will slightly mellow the cool
        quality, exactly as Memling's final amber varnish does on his panels.
        Pairs naturally with ``weyden_angular_shadow_pass()`` (which cools the
        deepest shadows); Memling handled the highlights and mid-shadows,
        while the Weyden pass handles the dark shadow geometry.
        """
        import numpy as _np

        print(f"  Memling jewel-light pass  "
              f"(highlight_thresh={highlight_thresh:.2f}  "
              f"midtone_low={midtone_low:.2f}  midtone_high={midtone_high:.2f}  "
              f"jewel_strength={jewel_strength:.3f}  "
              f"subsurface_strength={subsurface_strength:.3f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Memling jewel-light pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f   # (H, W)

        # ── Figure mask weight ────────────────────────────────────────────────
        if figure_mask is not None:
            mask_w = _np.clip(
                _np.array(figure_mask, dtype=_np.float32), 0.0, 1.0
            )
            if mask_w.shape != (h, w):
                from PIL import Image as _Img
                mask_w = _np.array(
                    _Img.fromarray((mask_w * 255).astype(_np.uint8)).resize(
                        (w, h), _Img.BILINEAR
                    ), dtype=_np.float32
                ) / 255.0
        else:
            mask_w = _np.ones((h, w), dtype=_np.float32)

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── 1. Jewel highlight push (lum > highlight_thresh) ──────────────────
        # Lift the brightest zones toward cool ivory: B up, R slightly down.
        # Memling's highlights are not warm gold (Rembrandt) but cool enamel-
        # white — as if the light has been filtered through a thin silver mirror.
        highlight_zone = (lum > highlight_thresh).astype(_np.float32)
        # Scale the push by how far above the threshold the pixel is — the
        # very brightest pixels get the full push; pixels just above threshold
        # receive only a fractional correction.
        highlight_excess = _np.clip(
            (lum - highlight_thresh) / max(1.0 - highlight_thresh, 1e-6),
            0.0, 1.0
        )
        highlight_w = highlight_zone * highlight_excess
        b_out = _np.clip(b_out + highlight_w * jewel_strength,           0.0, 1.0)
        r_out = _np.clip(r_out - highlight_w * jewel_strength * 0.40,    0.0, 1.0)

        # ── 2. Subsurface mid-tone tint (midtone_low ≤ lum < midtone_high) ───
        # Lift G and B in the shadow-transition band, reduce R fractionally.
        # This mimics light scattering through translucent skin: wavelengths
        # in the blue-green range penetrate more shallowly and exit from the
        # surface adjacent to the entry point, giving the transition zones a
        # slightly cooler, glowing quality.
        midtone_zone = (
            (lum >= midtone_low) & (lum < midtone_high)
        ).astype(_np.float32)

        # Weight peaks in the middle of the mid-tone band — subtlest at edges,
        # strongest at the centre of the transition zone (most translucent area).
        band_width = max(midtone_high - midtone_low, 1e-6)
        band_pos   = _np.clip((lum - midtone_low) / band_width, 0.0, 1.0)
        # Triangular weighting: 0 at band edges, 1 at centre
        sub_weight = midtone_zone * (1.0 - _np.abs(band_pos * 2.0 - 1.0))

        g_out = _np.clip(g_out + sub_weight * subsurface_strength * 0.70, 0.0, 1.0)
        b_out = _np.clip(b_out + sub_weight * subsurface_strength,         0.0, 1.0)
        r_out = _np.clip(r_out - sub_weight * subsurface_strength * 0.30,  0.0, 1.0)

        # ── Blend corrected layer back at `opacity`, weighted by mask ─────────
        blend = opacity * mask_w

        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - blend) + r_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - blend) + g_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - blend) + b_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        highlight_count  = int((highlight_zone  > 0.5).sum())
        midtone_count    = int((midtone_zone    > 0.5).sum())
        print(f"    Memling jewel-light pass complete  "
              f"(highlight_px={highlight_count}  midtone_px={midtone_count})")

    # ──────────────────────────────────────────────────────────────────────────
    # Session 56 — new artist: Agnolo Bronzino / bronzino_enamel_skin_pass
    # ──────────────────────────────────────────────────────────────────────────

    def bronzino_enamel_skin_pass(
        self,
        figure_mask:          "Optional[_np.ndarray]" = None,
        midtone_low:          float = 0.35,
        midtone_high:         float = 0.72,
        compression_strength: float = 0.18,
        highlight_thresh:     float = 0.72,
        cool_strength:        float = 0.05,
        shadow_thresh:        float = 0.35,
        desaturate_strength:  float = 0.22,
        opacity:              float = 0.70,
    ) -> None:
        """
        Apply Agnolo Bronzino's enamel-smooth flesh quality to the canvas.

        Agnolo Bronzino (1503–1572) — court painter to Cosimo I de' Medici and
        the supreme Florentine Mannerist portraitist — achieved a surface quality
        unlike any other painter of his era.  Where Leonardo dissolved edges in
        sfumato smoke and Rembrandt built impasto mountains of light, Bronzino
        refined and refined until the flesh read as polished ivory: seamless,
        cool, and utterly opaque to the emotions beneath.

        The technical basis was patient oil layering on a prepared panel, with
        each layer dried and sanded before the next was applied.  The result:
        a surface without visible brushwork, without texture, without incident.
        Tonal transitions in the midtones are minimal — barely perceptible —
        and this near-flat quality in the flesh is paradoxically more unsettling
        than bold modelling: the face becomes a mask.

        His highlights are not warm gold (as in Rembrandt or Titian) but cool
        pale ivory — as if the brightest zones have been lightly touched with
        white lead mixed with a trace of cool grey rather than Naples yellow.
        His deepest shadows carry no warm amber undertone; they desaturate toward
        cool grey, draining vitality from the flesh and replacing it with a
        controlled, aristocratic neutrality.

        This pass applies three distinct operations:

        1. **Midtone compression** (``midtone_low ≤ lum ≤ midtone_high``):
           Each pixel in the midtone band is blended toward a locally smoothed
           (gaussian-filtered) version of itself.  This compresses the tonal
           micro-texture of the painted surface — the fine variation that reads
           as brushwork — toward a smooth, seamless average.  The blend strength
           is highest at the band centre and tapers to zero at the edges
           (triangular weighting).  Controlled by ``compression_strength``.

        2. **Cool highlight push** (``lum > highlight_thresh``): The brightest
           pixels are pushed toward cool pale ivory: B is lifted and R is
           reduced.  Unlike Memling's jewel-light (which targets a specific
           enamel brilliance) this is a subtler, more uniform cooling — the
           entire lit zone is shifted very slightly toward silver-white rather
           than warm gold.  Controlled by ``cool_strength``.

        3. **Shadow desaturation** (``lum < shadow_thresh``): Deep shadow
           pixels are mixed toward their luminance value (neutral grey).  This
           drains warm undertones from the dark zones — removing the amber and
           sienna that warm oil grounds tend to impart — and leaves the shadows
           cool, chromatic-neutral, and slightly lifeless.  The strength scales
           with shadow depth: deepest shadows receive the full desaturation;
           pixels at the shadow boundary receive a fractional push.  Controlled
           by ``desaturate_strength``.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 array ``(H, W)`` in [0, 1].  1 = figure, 0 = background.
            When provided, all corrections are applied only within the figure.
        midtone_low : float
            Lower luminance boundary of the midtone compression band.
            Default 0.35 — below this the pixel is in shadow territory.
        midtone_high : float
            Upper luminance boundary of the midtone compression band.
            Default 0.72 — above this the pixel transitions to highlight.
        compression_strength : float
            Maximum blend fraction toward the gaussian-smoothed neighbourhood.
            0.0 = no smoothing; 1.0 = fully replaces local texture with the
            neighbourhood average.  Default 0.18 — perceptible but not extreme.
        highlight_thresh : float
            Luminance threshold above which pixels receive the cool push.
            Default 0.72 — only genuinely bright highlight zones are affected.
        cool_strength : float
            Magnitude of the cool ivory push in highlight zones.  Lifts B,
            reduces R.  Default 0.05 — subtle; stacks well with other passes.
        shadow_thresh : float
            Luminance boundary below which pixels are desaturated.
            Default 0.35 — captures the lower-mid and deep shadow zones.
        desaturate_strength : float
            Maximum desaturation strength at the deepest shadows.  0.0 = no
            change; 1.0 = full grayscale in the darkest pixels.  Default 0.22.
        opacity : float
            Global blend factor: 0 = no effect applied, 1 = full correction.

        Notes
        -----
        Apply AFTER ``build_form()`` — the compression suppresses brushwork
        texture, not the modelled tonal structure.  Works well before the final
        ``glaze()`` call: a cool pale ivory glaze (as in Bronzino's catalog
        entry) will complement and extend the enamel quality introduced here.
        Pairs well with ``weyden_angular_shadow_pass()`` (for precise shadow
        geometry) and ``holbein_jewel_glaze_pass()`` (for panel-painting
        finish).  Does NOT pair well with ``sfumato_veil_pass()`` at high
        settings — sfumato and enamel are aesthetically opposed techniques.
        """
        import numpy as _np

        print(f"  Bronzino enamel-skin pass  "
              f"(midtone_low={midtone_low:.2f}  midtone_high={midtone_high:.2f}  "
              f"compression={compression_strength:.3f}  cool={cool_strength:.3f}  "
              f"desaturate={desaturate_strength:.3f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Bronzino enamel-skin pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f   # (H, W)

        # ── Figure mask weight ────────────────────────────────────────────────
        if figure_mask is not None:
            mask_w = _np.clip(
                _np.array(figure_mask, dtype=_np.float32), 0.0, 1.0
            )
            if mask_w.shape != (h, w):
                from PIL import Image as _Img
                mask_w = _np.array(
                    _Img.fromarray((mask_w * 255).astype(_np.uint8)).resize(
                        (w, h), _Img.BILINEAR
                    ), dtype=_np.float32
                ) / 255.0
        else:
            mask_w = _np.ones((h, w), dtype=_np.float32)

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── 1. Midtone compression (midtone_low ≤ lum ≤ midtone_high) ─────────
        # Blend each pixel in the midtone band toward a locally smoothed version.
        # The gaussian kernel produces a neighbourhood average that reflects the
        # broad colour mass rather than individual brushstroke variation — mixing
        # toward it compresses local tonal texture without affecting the overall
        # tonal structure of the painting.
        sigma = max(2.0, min(w, h) * 0.012)
        r_smooth = ndimage.gaussian_filter(r_f, sigma=sigma).astype(_np.float32)
        g_smooth = ndimage.gaussian_filter(g_f, sigma=sigma).astype(_np.float32)
        b_smooth = ndimage.gaussian_filter(b_f, sigma=sigma).astype(_np.float32)

        midtone_zone = (
            (lum >= midtone_low) & (lum <= midtone_high)
        ).astype(_np.float32)
        # Triangular weighting: 0 at band edges, 1 at centre
        band_width = max(midtone_high - midtone_low, 1e-6)
        band_pos   = _np.clip((lum - midtone_low) / band_width, 0.0, 1.0)
        mid_weight = midtone_zone * (1.0 - _np.abs(band_pos * 2.0 - 1.0))
        blend_w    = mid_weight * compression_strength

        r_out = r_out * (1.0 - blend_w) + r_smooth * blend_w
        g_out = g_out * (1.0 - blend_w) + g_smooth * blend_w
        b_out = b_out * (1.0 - blend_w) + b_smooth * blend_w

        # ── 2. Cool highlight push (lum > highlight_thresh) ───────────────────
        # Lift B, reduce R in the brightest zones — Bronzino's highlights read
        # as cool pale ivory, not the warm Naples yellow of Italian Renaissance
        # painting.  Scale by how far above the threshold the pixel sits.
        highlight_zone   = (lum > highlight_thresh).astype(_np.float32)
        highlight_excess = _np.clip(
            (lum - highlight_thresh) / max(1.0 - highlight_thresh, 1e-6),
            0.0, 1.0
        )
        hi_w = highlight_zone * highlight_excess * cool_strength
        b_out = _np.clip(b_out + hi_w,            0.0, 1.0)
        r_out = _np.clip(r_out - hi_w * 0.50,     0.0, 1.0)

        # ── 3. Shadow desaturation (lum < shadow_thresh) ─────────────────────
        # Mix deep shadow pixels toward their luminance value (grayscale).
        # This removes the warm amber undertone that oil grounds introduce,
        # leaving Bronzino's characteristic cool, chromatic-neutral shadows.
        # Strength scales with depth — deepest shadows receive full push.
        shadow_depth = _np.clip(
            (shadow_thresh - lum) / max(shadow_thresh, 1e-6), 0.0, 1.0
        )
        desat_w = shadow_depth * desaturate_strength
        r_out = _np.clip(r_out * (1.0 - desat_w) + lum * desat_w, 0.0, 1.0)
        g_out = _np.clip(g_out * (1.0 - desat_w) + lum * desat_w, 0.0, 1.0)
        b_out = _np.clip(b_out * (1.0 - desat_w) + lum * desat_w, 0.0, 1.0)

        # ── Blend corrected layer back at `opacity`, weighted by mask ─────────
        blend = opacity * mask_w

        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - blend) + r_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - blend) + g_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - blend) + b_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        midtone_count   = int((midtone_zone   > 0.5).sum())
        highlight_count = int((highlight_zone  > 0.5).sum())
        shadow_count    = int((shadow_depth    > 0.05).sum())
        print(f"    Bronzino enamel-skin pass complete  "
              f"(midtone_px={midtone_count}  highlight_px={highlight_count}  "
              f"shadow_px={shadow_count})")

    def tintoretto_dynamic_light_pass(
        self,
        figure_mask:         "Optional[_np.ndarray]" = None,
        contrast_strength:   float = 0.22,
        highlight_thresh:    float = 0.68,
        silver_strength:     float = 0.08,
        shadow_thresh:       float = 0.30,
        shadow_depth_push:   float = 0.18,
        opacity:             float = 0.75,
    ) -> None:
        """
        Apply Jacopo Tintoretto's silver lightning-highlight and dramatic void quality.

        Tintoretto (Jacopo Robusti, 1518–1594) — Il Furioso — transformed Venetian
        painting by combining the Venetian tradition of rich colourism with a
        Michelangelesque command of dramatic light.  Where his teacher Titian built
        luminosity through patient transparent glazing on warm ochre grounds,
        Tintoretto slashed silver-white impasto directly onto near-black grounds,
        creating a quality of light that reads less like warm sunlight and more like
        a sudden bolt of lightning cutting across absolute darkness.

        His technique in the Scuola Grande di San Rocco — the largest body of
        paintings by a single artist in any single building — represents the extreme
        development of this approach: figures emerge from near-absolute void, lit by
        cool, directional, electric-silver highlights rather than warm diffuse glow.
        The tonal range from darkest shadow to brightest highlight is among the widest
        in Italian Renaissance painting; the drama lives in that gap.

        This pass applies three layered operations:

        1. **Contrast amplification** (global): Expands the tonal range by darkening
           shadows and brightening highlights simultaneously.  Applies a mild S-curve
           to luminance — the midpoint is held, but both ends are pushed outward.
           This models the quality of Tintoretto's extreme ground-to-highlight range.
           Controlled by ``contrast_strength``.

        2. **Silver highlight push** (``lum > highlight_thresh``): The brightest
           pixels are cooled toward silver-white — B is lifted, R is slightly reduced.
           This is the inverse of Rembrandt or Titian warm gold highlights: Tintoretto's
           impasto peaks read as cool, metallic, almost electrically bright.  The effect
           scales with distance above the threshold (brightest pixels receive full push).
           Controlled by ``silver_strength``.

        3. **Shadow void deepening** (``lum < shadow_thresh``): Dark pixels are pulled
           further toward the near-black Venetian ground.  This widens the luminance gap
           between lit and unlit areas, reinforcing the drama of sudden emergence from
           darkness.  Strength scales with depth: deepest shadows receive the full push.
           Controlled by ``shadow_depth_push``.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 array ``(H, W)`` in [0, 1].  1 = figure, 0 = background.
            When provided, all corrections are confined to the figure region.
        contrast_strength : float
            Amplitude of the S-curve contrast expansion.  0 = no change; 0.22 = visible
            dramatic extension of tonal range.  Values > 0.40 will crush shadows and
            blow highlights; use with care.
        highlight_thresh : float
            Luminance above which the silver cool-push is applied.  Default 0.68.
            Only genuine impasto highlights should receive the silver treatment.
        silver_strength : float
            Magnitude of the silver push: B lifted, R reduced.  Default 0.08 — subtle
            but perceptible; stacks with contrast amplification to produce the
            characteristic electric-silver impasto quality.
        shadow_thresh : float
            Luminance below which shadow void deepening is applied.  Default 0.30.
        shadow_depth_push : float
            How strongly shadows are pushed toward absolute black.  0 = no change;
            1 = full push to zero.  Default 0.18.  Preserves the slight warm-brown
            undertone of Tintoretto's ground rather than crushing to pure black.
        opacity : float
            Global blend factor: 0 = no effect, 1 = full correction applied.

        Notes
        -----
        Apply AFTER ``build_form()`` — contrast amplification acts on the modelled
        tonal structure, not the unformed underpainting.  Works well before ``glaze()``
        with a deep amber Venetian glaze: the silver highlights read through the amber
        as a warm-then-cool flicker, reproducing the Tintoretto luminosity exactly.
        Pairs well with ``chiaroscuro_modelling_pass()`` (to establish the initial
        tonal drama) and ``reflected_light_pass()`` (the secondary silver reflection
        in shadow areas that Tintoretto used to animate his void backgrounds).
        Does NOT pair well with ``bronzino_enamel_skin_pass()`` — they are
        aesthetically opposite techniques (seamless surface vs. slashed impasto).
        """
        import numpy as _np

        print(f"  Tintoretto dynamic-light pass  "
              f"(contrast={contrast_strength:.3f}  silver={silver_strength:.3f}  "
              f"shadow_push={shadow_depth_push:.3f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Tintoretto dynamic-light pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Acquire raw BGRA buffer ───────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape(h, w, 4).copy()
        orig = buf.copy()

        # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f   # (H, W)

        # ── Figure mask weight ────────────────────────────────────────────────
        if figure_mask is not None:
            mask_w = _np.clip(
                _np.array(figure_mask, dtype=_np.float32), 0.0, 1.0
            )
            if mask_w.shape != (h, w):
                from PIL import Image as _Img
                mask_w = _np.array(
                    _Img.fromarray((mask_w * 255).astype(_np.uint8)).resize(
                        (w, h), _Img.BILINEAR
                    ), dtype=_np.float32
                ) / 255.0
        else:
            mask_w = _np.ones((h, w), dtype=_np.float32)

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── 1. Contrast amplification (S-curve centred at 0.5) ───────────────
        # A mild S-curve pushes darks darker and brights brighter simultaneously.
        # Implementation: lum_new = 0.5 + (lum - 0.5) * (1 + contrast_strength)
        # We compute a luminance delta and apply it proportionally to each channel
        # so that hue is preserved while the tonal range is expanded.
        if contrast_strength > 0.0:
            scale = 1.0 + contrast_strength
            lum_new = _np.clip(0.5 + (lum - 0.5) * scale, 0.0, 1.0)
            lum_safe = _np.where(lum > 1e-6, lum, 1e-6)
            ratio = lum_new / lum_safe
            # Clamp ratio so no channel exceeds [0, 1]
            ratio = _np.clip(ratio, 0.0, 1.0 / _np.maximum(
                _np.stack([r_out, g_out, b_out], axis=-1).max(axis=-1), 1e-6
            ))
            r_out = _np.clip(r_out * ratio, 0.0, 1.0)
            g_out = _np.clip(g_out * ratio, 0.0, 1.0)
            b_out = _np.clip(b_out * ratio, 0.0, 1.0)
            # Recompute luminance after contrast step for subsequent operations
            lum = 0.2126 * r_out + 0.7152 * g_out + 0.0722 * b_out

        # ── 2. Silver highlight push (lum > highlight_thresh) ────────────────
        # The brightest impasto ridges are cooled toward silver-white:
        # B is lifted, R is slightly reduced.  This is Tintoretto's cool electric
        # highlight — neither Rembrandt's warm amber glow nor Leonardo's sfumato.
        # Strength scales with excess luminance above the threshold.
        highlight_excess = _np.clip(
            (lum - highlight_thresh) / max(1.0 - highlight_thresh, 1e-6),
            0.0, 1.0
        )
        hi_w = highlight_excess * silver_strength
        b_out = _np.clip(b_out + hi_w,         0.0, 1.0)
        r_out = _np.clip(r_out - hi_w * 0.55,  0.0, 1.0)

        # ── 3. Shadow void deepening (lum < shadow_thresh) ───────────────────
        # Dark pixels are pulled further toward black — widening the tonal gap
        # between Tintoretto's lit impasto peaks and his near-black Venetian void.
        # Strength scales with how deep the shadow is (deepest = full push).
        shadow_depth = _np.clip(
            (shadow_thresh - lum) / max(shadow_thresh, 1e-6), 0.0, 1.0
        )
        push_w = shadow_depth * shadow_depth_push
        r_out  = _np.clip(r_out * (1.0 - push_w), 0.0, 1.0)
        g_out  = _np.clip(g_out * (1.0 - push_w), 0.0, 1.0)
        b_out  = _np.clip(b_out * (1.0 - push_w), 0.0, 1.0)

        # ── Blend corrected layer back at `opacity`, weighted by mask ─────────
        blend = opacity * mask_w

        buf[:, :, 2] = _np.clip(
            orig[:, :, 2] * (1.0 - blend) + r_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(
            orig[:, :, 1] * (1.0 - blend) + g_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(
            orig[:, :, 0] * (1.0 - blend) + b_out * blend * 255.0,
            0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        highlight_count = int((highlight_excess > 0.05).sum())
        shadow_count    = int((shadow_depth     > 0.05).sum())
        print(f"    Tintoretto dynamic-light pass complete  "
              f"(highlight_px={highlight_count}  shadow_px={shadow_count})")

    # ─────────────────────────────────────────────────────────────────────────
    # Giorgione — tonal poetry pass
    # ─────────────────────────────────────────────────────────────────────────

    def giorgione_tonal_poetry_pass(
        self,
        figure_mask:         "Optional[_np.ndarray]" = None,
        midtone_low:         float = 0.30,
        midtone_high:        float = 0.70,
        luminous_lift:       float = 0.12,
        warm_shadow_strength: float = 0.06,
        cool_edge_strength:  float = 0.05,
        opacity:             float = 0.70,
    ) -> None:
        """
        Apply Giorgione's tonal-poetry quality to the canvas.

        Giorgione (Giorgio Barbarelli da Castelfranco, c.1477–1510) — Venetian High
        Renaissance — invented 'tonalismo': building form entirely through pooled
        tone and colour rather than linear underdrawing.  His flesh appears to breathe
        from within because his midtones carry a mysterious inner luminosity — forms
        are neither crisp (Flemish) nor dissolved (sfumato) but softly, warmly
        present.  Landscape and atmosphere seep into the figure's peripheral silhouette,
        creating the warm-cool oscillation that binds figure to environment.

        This pass applies three distinct operations:

        1. **Luminous midtone lift** (midtone_low ≤ lum ≤ midtone_high): Brightens
           midtone pixels by a soft, lum-weighted amount, creating the characteristic
           inner glow.  Controlled by luminous_lift.

        2. **Warm amber shadow-transition push** (lum < midtone_high): At the
           shadow-to-midtone boundary, warms the tone toward Giorgione's raw-sienna
           earth palette by slightly elevating the red-channel relative to blue.
           Controlled by warm_shadow_strength.

        3. **Cool blue-green peripheral bleed** (figure_mask provided, mask < 0.4):
           At the figure's peripheral silhouette, bleeds a subtle cool blue-green
           tint inward — the landscape atmosphere seeping into the figure edge.
           Controlled by cool_edge_strength.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 array (H, W) in [0, 1]. 1 = figure interior, 0 = background.
            When provided, operation 3 is applied at the figure's soft edge zone
            (mask values 0.05–0.40).  If None, operation 3 is skipped.
        midtone_low : float
            Lower luminance boundary of the midtone zone in [0, 1].  Pixels with
            luminance below this are treated as shadows; only operation 2 applies
            at the shadow-midtone transition.  Default 0.30.
        midtone_high : float
            Upper luminance boundary of the midtone zone in [0, 1].  Pixels above
            this are highlights; operation 1 tapers off toward this threshold.
            Default 0.70.
        luminous_lift : float
            Magnitude of the midtone luminance lift in [0, 1].  0 = no inner glow;
            0.20+ produces a noticeably bright, almost Bellini-esque glow.
            Default 0.12 — subtle inner light.
        warm_shadow_strength : float
            Red-channel boost applied in the shadow-to-midtone transition zone.
            Warms the deep half-tones toward Giorgione's raw-sienna earth palette.
            Default 0.06.
        cool_edge_strength : float
            Blue-green tint added at the figure's peripheral mask edge (mask 0.05–0.40).
            Simulates the landscape atmosphere seeping into the silhouette.
            Default 0.05.
        opacity : float
            Global blend factor: 0 = no effect, 1 = full correction applied.
            The three operations are each independently blended at this opacity.

        Notes
        -----
        Apply AFTER build_form().  Works best before glaze(), which will warm and
        deepen the final surface over the tonal work this pass establishes.
        Pairs well with sfumato_veil_pass() (softens remaining hard edges further)
        and atmospheric_depth_pass() (extends the cool recessive logic into the
        background).
        Does NOT pair well with tintoretto_dynamic_light_pass() (which dramatically
        re-contrasts what this pass intentionally softens).
        """
        import numpy as _np

        print(f"  Giorgione tonal-poetry pass  "
              f"(luminous_lift={luminous_lift:.3f}  "
              f"warm_shadow={warm_shadow_strength:.3f}  "
              f"cool_edge={cool_edge_strength:.3f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Giorgione tonal-poetry pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Read canvas buffer ────────────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # Normalise to float [0, 1] — cairo surface is BGRA
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # Perceived luminance
        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        # When a figure_mask is provided, operations 1 and 2 are gated to figure
        # pixels — pixels where mask=0 (pure background) are not altered.
        # This matches the convention of every other artist-specific pass in this engine.
        if figure_mask is not None:
            mask_f  = figure_mask.astype(_np.float32)
            fig_w   = _np.clip(mask_f, 0.0, 1.0)   # [0, 1] spatial weight for ops 1 & 2
        else:
            mask_f  = None
            fig_w   = _np.ones((h, w), dtype=_np.float32)   # apply everywhere

        # ── Operation 1: luminous midtone lift ────────────────────────────────
        # Bell-shaped weight: peaks at midpoint of midtone_low..midtone_high,
        # falls to zero at either boundary.
        mid_centre = (midtone_low + midtone_high) * 0.5
        mid_half   = (midtone_high - midtone_low) * 0.5 + 1e-8
        in_mid     = (lum >= midtone_low) & (lum <= midtone_high)
        # Cosine bell: weight 1 at centre, 0 at edges of midtone zone
        bell       = _np.where(in_mid,
                               0.5 * (1.0 + _np.cos(
                                   _np.pi * (lum - mid_centre) / mid_half)),
                               0.0).astype(_np.float32)
        lift       = bell * luminous_lift * opacity * fig_w

        r_out = _np.clip(r_f + lift, 0.0, 1.0)
        g_out = _np.clip(g_f + lift * 0.92, 0.0, 1.0)   # slightly less green lift
        b_out = _np.clip(b_f + lift * 0.80, 0.0, 1.0)   # least blue lift — keeps warm

        # ── Operation 2: warm amber shadow-transition push ────────────────────
        # Target zone: shadow-to-midtone boundary (midtone_low ± half its span)
        shadow_zone_top = midtone_low + (midtone_high - midtone_low) * 0.25
        in_shadow_trans = (lum >= (midtone_low * 0.5)) & (lum <= shadow_zone_top)
        # Weight strongest at midtone_low, fading at either side
        shadow_bell     = _np.where(
            in_shadow_trans,
            _np.clip(1.0 - _np.abs(lum - midtone_low) / (shadow_zone_top - midtone_low * 0.5 + 1e-8), 0.0, 1.0),
            0.0).astype(_np.float32)
        warm_push       = shadow_bell * warm_shadow_strength * opacity * fig_w

        # Raise R slightly, pull B slightly — raw-sienna warmth in the half-tones
        r_out = _np.clip(r_out + warm_push,        0.0, 1.0)
        b_out = _np.clip(b_out - warm_push * 0.50, 0.0, 1.0)

        # ── Operation 3: cool blue-green peripheral bleed ─────────────────────
        if mask_f is not None:
            # Edge zone: mask values between 0.05 and 0.40 — soft peripheral silhouette
            in_edge = (mask_f >= 0.05) & (mask_f <= 0.40)
            # Weight inversely proportional to mask density — strongest at outer edge
            edge_w  = _np.where(in_edge,
                                (0.40 - mask_f) / 0.35,
                                0.0).astype(_np.float32)
            cool_push = edge_w * cool_edge_strength * opacity

            # Add blue-green at the peripheral edge — Giorgione's landscape seeping in
            b_out = _np.clip(b_out + cool_push * 1.20, 0.0, 1.0)
            g_out = _np.clip(g_out + cool_push * 0.80, 0.0, 1.0)
            r_out = _np.clip(r_out - cool_push * 0.40, 0.0, 1.0)

        # ── Write back ────────────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        midtone_px = int(in_mid.sum())
        print(f"    Giorgione tonal-poetry pass complete  "
              f"(midtone_px={midtone_px})")

    # ─────────────────────────────────────────────────────────────────────────
    # Veronese — luminous feast pass
    # ─────────────────────────────────────────────────────────────────────────

    def veronese_luminous_feast_pass(
        self,
        figure_mask:            "Optional[_np.ndarray]" = None,
        midtone_low:            float = 0.35,
        midtone_high:           float = 0.65,
        saturation_boost:       float = 0.14,
        cool_highlight_strength: float = 0.06,
        shadow_chroma_preserve: float = 0.08,
        opacity:                float = 0.72,
    ) -> None:
        """
        Apply Paolo Veronese's luminous colour quality to the canvas.

        Paolo Veronese (Paolo Caliari, 1528–1588) — Venetian Colorism — bathed his
        enormous feast-scene canvases in a clear, silvery, almost outdoor light that
        sets him apart from both Titian's warm-amber depth and Tintoretto's near-black
        void drama.  His palette is the most brilliantly saturated of the three great
        Venetians: rose-crimson draperies, clear warm-yellow fabric, and cool grey-green
        shadow tones read with festive, architectural clarity.  Unlike the tonal
        dissolvers (Leonardo, Giorgione), Veronese's forms stand confidently in light;
        his shadows remain colour-filled and relatively luminous, not collapsing toward
        black.

        This pass applies three distinct operations:

        1. **Mid-tone saturation boost** (midtone_low ≤ lum ≤ midtone_high): Increases
           colour saturation in the mid-luminance band using a bell-shaped weight.
           In HSV space: S is lifted toward 1.0.  This intensifies Veronese's brilliant
           fabric colours — rose, yellow-gold, grey-green — without blowing out
           highlights or muddying deep shadows.  Controlled by saturation_boost.

        2. **Cool silver-ivory highlight push** (lum > highlight_thresh=0.70): Adds a
           subtle B-channel and slight G-channel lift in the brightest lit pixels —
           pushing them toward Veronese's characteristic cool north-light ivory
           (not Titian's warm gold).  Controlled by cool_highlight_strength.

        3. **Shadow chroma preservation** (lum < shadow_thresh=0.30): In deep shadow
           zones, slightly boosts saturation (the same HSV logic as op 1 but applied
           to dark pixels).  Prevents shadows from collapsing toward grey, maintaining
           the colour-filled quality of Veronese's lit, airy shadow zones.
           Controlled by shadow_chroma_preserve.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 array (H, W) in [0, 1].  1 = figure interior, 0 = background.
            When provided, all three operations are gated to figure pixels — pure
            background pixels (mask=0) are not altered.  If None, the pass applies
            globally across the canvas.
        midtone_low : float
            Lower luminance boundary of the mid-tone saturation zone.  Pixels darker
            than this are treated as shadows (operation 3 applies instead).
            Default 0.35.
        midtone_high : float
            Upper luminance boundary of the mid-tone saturation zone.  Pixels brighter
            than this receive the cool highlight push (operation 2) instead.
            Default 0.65.
        saturation_boost : float
            Magnitude of the HSV saturation lift in the mid-tone band.  0 = no change;
            0.25+ produces visibly intense Fauvist-approaching colour.  Default 0.14 —
            noticeable vibrancy without cartoonish saturation.
        cool_highlight_strength : float
            Blue-green channel lift applied in the brightest pixels (lum > 0.70).
            Pushes highlights toward cool silver-ivory rather than warm gold.
            Default 0.06 — subtle but distinguishable from Titian's warm glaze.
        shadow_chroma_preserve : float
            HSV saturation lift applied in the deepest shadow zone (lum < 0.30).
            Prevents colour from draining completely in dark areas; keeps shadows
            luminous.  Default 0.08.
        opacity : float
            Global blend factor: 0 = no effect, 1 = full correction applied.
            All three operations are composited at this opacity.  Default 0.72.

        Notes
        -----
        Apply AFTER build_form() and BEFORE glaze().  The mid-tone saturation boost
        enhances the colours that the subsequent warm glaze will deepen — together they
        produce Veronese's characteristic rich-yet-luminous surface.
        Pairs well with penumbra_zone_pass() (warms the light-to-shadow transition)
        and sfumato_veil_pass() (if a softer sfumato variant of the portrait is desired,
        though Veronese himself used clear edges).
        Does NOT pair well with tintoretto_dynamic_light_pass() (which darkens shadows
        and contracts colour into near-black, opposite to Veronese's luminous intent).
        """
        import numpy as _np
        import colorsys as _colorsys

        print(f"  Veronese luminous-feast pass  "
              f"(sat_boost={saturation_boost:.3f}  "
              f"cool_hi={cool_highlight_strength:.3f}  "
              f"shadow_chroma={shadow_chroma_preserve:.3f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Veronese luminous-feast pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Read canvas buffer ────────────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # Normalise to float [0, 1] — cairo surface is BGRA
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # Perceived luminance
        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        # Spatial weight: figure_mask gating (same convention as all artist passes)
        if figure_mask is not None:
            fig_w = _np.clip(figure_mask.astype(_np.float32), 0.0, 1.0)
        else:
            fig_w = _np.ones((h, w), dtype=_np.float32)

        # ── Operation 1 & 3: saturation boost via HSV ────────────────────────
        # Bell weight for mid-tone zone (op 1)
        mid_centre = (midtone_low + midtone_high) * 0.5
        mid_half   = (midtone_high - midtone_low) * 0.5 + 1e-8
        in_mid     = (lum >= midtone_low) & (lum <= midtone_high)
        mid_bell   = _np.where(in_mid,
                               0.5 * (1.0 + _np.cos(
                                   _np.pi * (lum - mid_centre) / mid_half)),
                               0.0).astype(_np.float32)

        # Linear weight for shadow zone (op 3): strongest at lum=0, fades at shadow_thresh
        shadow_thresh = midtone_low
        in_shadow     = lum < shadow_thresh
        shadow_w      = _np.where(in_shadow,
                                  1.0 - lum / (shadow_thresh + 1e-8),
                                  0.0).astype(_np.float32)

        # Apply saturation boost pixel-by-pixel using vectorised HSV conversion.
        # For efficiency: compute max/min across RGB channels to get S and V in HSV.
        cmax   = _np.maximum(_np.maximum(r_f, g_f), b_f)
        cmin   = _np.minimum(_np.minimum(r_f, g_f), b_f)
        delta  = cmax - cmin + 1e-8   # avoid division by zero

        # HSV saturation = delta / cmax  (when cmax > 0)
        sat_orig = _np.where(cmax > 1e-6, delta / cmax, 0.0).astype(_np.float32)

        # Combined boost weight: mid-tone bell + shadow preservation
        mid_boost_w    = mid_bell   * saturation_boost       * fig_w
        shadow_boost_w = shadow_w   * shadow_chroma_preserve * fig_w

        sat_new = _np.clip(sat_orig
                           + mid_boost_w * opacity
                           + shadow_boost_w * opacity,
                           0.0, 1.0)

        # Scale RGB channels: to increase saturation in HSV, scale each channel
        # away from its grey (cmax) by the ratio of new S to old S.
        # If old S = 0 (grey pixel), no change can be made.
        nonzero_sat = sat_orig > 1e-4
        scale = _np.where(nonzero_sat, sat_new / sat_orig, 1.0).astype(_np.float32)
        # Clamp scale to avoid oversaturation artefacts
        scale = _np.clip(scale, 0.0, 2.5)

        # The neutral grey reference per-pixel is cmax (max channel = V in HSV).
        # Saturation boost shifts each channel: c_new = cmax + (c_old - cmax) * scale
        r_out = _np.clip(cmax + (r_f - cmax) * scale, 0.0, 1.0)
        g_out = _np.clip(cmax + (g_f - cmax) * scale, 0.0, 1.0)
        b_out = _np.clip(cmax + (b_f - cmax) * scale, 0.0, 1.0)

        # ── Operation 2: cool silver-ivory highlight push ─────────────────────
        highlight_thresh = midtone_high
        in_hi  = lum > highlight_thresh
        # Weight: linear ramp, strongest at lum=1, zero at highlight_thresh
        hi_w   = _np.where(in_hi,
                           (lum - highlight_thresh) / (1.0 - highlight_thresh + 1e-8),
                           0.0).astype(_np.float32)
        cool_push = hi_w * cool_highlight_strength * opacity * fig_w

        # Cool silver-ivory: slight B lift and G lift, slight R reduction
        b_out = _np.clip(b_out + cool_push * 1.10, 0.0, 1.0)
        g_out = _np.clip(g_out + cool_push * 0.55, 0.0, 1.0)
        r_out = _np.clip(r_out - cool_push * 0.20, 0.0, 1.0)

        # ── Write back ────────────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        midtone_px   = int(in_mid.sum())
        highlight_px = int(in_hi.sum())
        shadow_px    = int(in_shadow.sum())
        print(f"    Veronese luminous-feast pass complete  "
              f"(midtone_px={midtone_px}  highlight_px={highlight_px}  "
              f"shadow_px={shadow_px})")

    def murillo_vapor_pass(
        self,
        figure_mask:       "Optional[_np.ndarray]" = None,
        warmth_strength:   float = 0.18,
        bloom_radius:      int   = 12,
        shadow_warmth:     float = 0.10,
        highlight_glow:    float = 0.08,
        opacity:           float = 0.68,
    ) -> None:
        """
        Apply Bartolomé Esteban Murillo's 'estilo vaporoso' (vaporous style) to the canvas.

        Murillo (1617–1682) — Spanish Baroque — is distinguished from all other Spanish
        Baroque painters by his warm, diffused luminosity: the 'estilo vaporoso' that
        18th-century collectors named to describe the soft, glowing quality of his mature
        work.  Where Caravaggio and Zurbarán used cold, dramatic chiaroscuro and near-black
        voids, Murillo bathed every surface in warm amber-rose light that reads not as
        theatrical drama but as spiritual tenderness.  His Immaculate Conception (c.1678,
        Prado) seems literally to glow; his beggar boys are not grim but radiant.

        This pass applies three distinct operations that together produce the 'vaporous'
        quality:

        1. **Warm luminous bloom** (all luminance zones, strongest in midtones):
           A warm amber-rose bloom is diffused outward from highlighted areas using a
           Gaussian-blurred luminance kernel.  The bloom radiates warmth into the
           surrounding midtone zones — simulating how Murillo's light sources appear to
           warm the air around them, not merely illuminate surfaces.  Controlled by
           warmth_strength and bloom_radius.

        2. **Shadow warmth injection** (lum < 0.32):
           Deep shadow zones receive a warm amber-rose lift, preventing the cold collapse
           toward near-black that defines Caravaggio and Zurbarán.  Murillo's shadows
           retain colour — they read as warm dark amber, not cold black void.
           Controlled by shadow_warmth.

        3. **Pearl highlight push** (lum > 0.68):
           The very brightest pixels receive a slight warm ivory push — adding a tiny
           red-channel lift and modest green lift while leaving blue unchanged.  This
           produces the characteristic Murillo 'pearl' quality in lit skin: highlights
           that feel warm, creamy, and almost edible, contrasting with the cool silver
           of Veronese and the golden warmth of Titian.  Controlled by highlight_glow.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 (H, W) array in [0, 1].  1 = figure interior, 0 = background.
            When provided, all operations are gated to figure pixels — background
            pixels (mask=0) are left unchanged.  If None, applies globally.
        warmth_strength : float
            Magnitude of the warm bloom halo.  0 = no bloom; 0.30+ produces a
            visibly strong warm aureole around lit areas.  Default 0.18 — noticeable
            warmth without aureole artefacts.
        bloom_radius : int
            Gaussian blur radius (in pixels) for the warm bloom diffusion kernel.
            Larger values spread warmth over a wider halo; smaller values keep it close
            to the highlight zone.  Default 12 — appropriate for a 780×1080 canvas.
        shadow_warmth : float
            Warm amber-rose lift in the darkest shadow pixels (lum < 0.32).  Prevents
            dark zones from collapsing to near-black.  Default 0.10 — a perceptible
            warm amber quality in shadows without washing out the dark value.
        highlight_glow : float
            Warm ivory push applied to the brightest highlights (lum > 0.68).
            Lifts the red and green channels fractionally, producing the 'pearl' quality
            of Murillo's lit skin.  Default 0.08.
        opacity : float
            Global blend factor.  0 = no effect applied; 1 = full operations.
            Default 0.68 — strong but not overwhelming.

        Notes
        -----
        Apply AFTER build_form() and BEFORE the final glaze().  The warm bloom and
        shadow warmth operations work best when form is already fully established;
        applying them earlier can wash out the structural underpainting.

        Pairs naturally with:
        - sfumato_veil_pass(warmth=0.30) for a further warm-edge softening.
        - glaze(color=(0.68, 0.50, 0.34), opacity=0.06) — Murillo's characteristic
          amber-rose final glaze that deepens the warm harmony.

        Does NOT pair with:
        - tintoretto_dynamic_light_pass() — Tintoretto's cold near-black shadows
          directly oppose Murillo's warm shadow warmth.
        - veronese_luminous_feast_pass() with high saturation_boost — Veronese's
          cool-highlight push (B-channel) conflicts with Murillo's warm red-channel glow.
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Murillo vapor pass  "
              f"(warmth={warmth_strength:.3f}  bloom_r={bloom_radius}  "
              f"shadow_warmth={shadow_warmth:.3f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Murillo vapor pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Read canvas buffer ────────────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # Normalise to float [0, 1] — cairo surface is BGRA
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # Perceived luminance
        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        # Spatial gating weight from figure_mask
        if figure_mask is not None:
            fig_w = _np.clip(figure_mask.astype(_np.float32), 0.0, 1.0)
        else:
            fig_w = _np.ones((h, w), dtype=_np.float32)

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Operation 1: Warm luminous bloom ─────────────────────────────────
        # Build the bloom kernel: Gaussian-blurred luminance map.
        # We convert lum to PIL Image, apply GaussianBlur, convert back.
        lum_img = _Image.fromarray(
            _np.clip(lum * 255.0, 0, 255).astype(_np.uint8), mode="L"
        )
        bloom_img = lum_img.filter(
            _ImageFilter.GaussianBlur(radius=float(bloom_radius))
        )
        bloom_arr = _np.asarray(bloom_img, dtype=_np.float32) / 255.0

        # The bloom contribution: warm amber-rose — R:1.0, G:0.62, B:0.28
        bloom_weight = bloom_arr * warmth_strength * opacity * fig_w
        r_out = _np.clip(r_out + bloom_weight * 1.00, 0.0, 1.0)
        g_out = _np.clip(g_out + bloom_weight * 0.62, 0.0, 1.0)
        b_out = _np.clip(b_out + bloom_weight * 0.28, 0.0, 1.0)

        # ── Operation 2: Shadow warmth injection ─────────────────────────────
        shadow_thresh = 0.32
        in_shadow = lum < shadow_thresh
        shadow_w  = _np.where(in_shadow,
                              (1.0 - lum / (shadow_thresh + 1e-8)) * fig_w,
                              0.0).astype(_np.float32)
        warm_lift = shadow_w * shadow_warmth * opacity
        # Warm amber-rose shadow: +R, +slight G, minimal B
        r_out = _np.clip(r_out + warm_lift * 1.00, 0.0, 1.0)
        g_out = _np.clip(g_out + warm_lift * 0.55, 0.0, 1.0)
        b_out = _np.clip(b_out + warm_lift * 0.15, 0.0, 1.0)

        # ── Operation 3: Pearl highlight push ────────────────────────────────
        highlight_thresh = 0.68
        in_hi = lum > highlight_thresh
        hi_w  = _np.where(in_hi,
                          (lum - highlight_thresh) / (1.0 - highlight_thresh + 1e-8) * fig_w,
                          0.0).astype(_np.float32)
        pearl_push = hi_w * highlight_glow * opacity
        # Warm ivory pearl: strong R lift, moderate G lift, minimal B
        r_out = _np.clip(r_out + pearl_push * 1.00, 0.0, 1.0)
        g_out = _np.clip(g_out + pearl_push * 0.78, 0.0, 1.0)
        b_out = _np.clip(b_out + pearl_push * 0.38, 0.0, 1.0)

        # ── Write back ────────────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        bloom_px   = int((bloom_arr > 0.05).sum())
        shadow_px  = int(in_shadow.sum())
        hi_px      = int(in_hi.sum())
        print(f"    Murillo vapor pass complete  "
              f"(bloom_px={bloom_px}  shadow_px={shadow_px}  hi_px={hi_px})")

    # ──────────────────────────────────────────────────────────────────────────
    # Session 59 — new artist: Giovanni Battista Tiepolo / tiepolo_celestial_light_pass
    # ──────────────────────────────────────────────────────────────────────────

    def tiepolo_celestial_light_pass(
        self,
        figure_mask:       "Optional[_np.ndarray]" = None,
        azure_push:        float = 0.12,
        naples_glow:       float = 0.10,
        pearl_bloom:       float = 0.08,
        azure_band:        float = 0.50,
        bloom_radius:      int   = 18,
        opacity:           float = 0.70,
    ) -> None:
        """
        Apply Giovanni Battista Tiepolo's defining celestial light effect.

        Tiepolo (1696–1770) was the supreme master of the Venetian Rococo and
        the last great fresco painter of the Western tradition.  His signature
        visual quality — a vast luminous sky from which overhead celestial
        light descends onto figures below — depends on three simultaneous
        colour operations that this pass implements:

        1. **Azure sky push** (upper canvas zone): The upper ``azure_band``
           fraction of the canvas is pushed toward Tiepolo's characteristic
           brilliant azure-cerulean sky.  Unlike the muted grey-blue of
           ordinary atmospheric perspective, Tiepolo's skies are saturated
           and vibrant — a positive chromatic assertion, not merely a
           desaturated haze.  The push boosts B, reduces R, and very slightly
           lifts G in the sky zone, weighted by a gradient that is maximum at
           the top of the canvas and fades to zero at ``azure_band * H``.

        2. **Naples yellow warm glow** (figure zone): Within the figure_mask —
           or globally if none is provided — the lit tops of forms (pixels
           above the luminance midpoint) receive a warm Naples-yellow bloom.
           Tiepolo's flesh is modelled from a warm Naples yellow base:
           highlights lean warm-gold rather than the cool pearl of Ingres or
           the ivory of Leonardo.  The glow adds R and G in proportion to
           luminance, creating the self-luminous quality of his figures
           standing in direct overhead light.

        3. **Pearl-white zenith bloom**: The highest-luminance pixels (above
           0.75 lum) receive a brilliant near-white bloom — boosting all
           channels toward equal, pure white — simulating the dazzling zenith
           highlights on drapery, metallic armour, and upturned faces.
           Tiepolo's whites are not warm ivory (Rembrandt) nor cool silver
           (Velázquez) but a neutral brilliant pearl that reads as direct
           exposure to celestial light.

        Together these three operations recreate the distinctive quality of a
        Tiepolo fresco seen from below: figures in brilliant natural overhead
        light against a vivid azure sky, with both the sky and the figures
        appearing to radiate rather than merely reflect the light.

        Parameters
        ----------
        figure_mask : ndarray or None
            Float mask [0, 1] restricting the Naples-yellow glow to the
            figure zone.  If None, the glow applies globally.
        azure_push : float
            Strength of the azure-cerulean push in the sky zone.  0.12
            produces the clear, saturated Tiepolo sky; 0.0 disables it.
        naples_glow : float
            Strength of the Naples-yellow warm glow on lit figure surfaces.
        pearl_bloom : float
            Strength of the brilliant pearl-white bloom on the highest
            highlights.  Keep low (0.06–0.10) to avoid washing out.
        azure_band : float
            Fractional height from the top of the canvas over which the
            azure sky push is applied.  0.50 = upper half.
        bloom_radius : int
            Gaussian blur radius for the pearl bloom kernel, in pixels.
        opacity : float
            Global blend weight for the combined result over the original.

        Pairs with
        ----------
        - ``aerial_perspective_pass()`` — set ``warm_foreground_push > 0``
          to complement the azure sky with a warm foreground (the complete
          Tiepolo atmospheric contrast).
        - ``sfumato_veil_pass()`` — NOT recommended at high warmth values;
          sfumato's warm amber haze conflicts with the cool azure sky.
        - ``veronese_luminous_feast_pass()`` — Veronese's cool silver
          highlights share the same Venetian chromatic family as Tiepolo;
          the two passes may be sequenced for a combined Venetian luminosity.

        Does NOT pair with
        ------------------
        - ``murillo_vapor_pass()`` — Murillo's warm amber-rose glow
          opposes Tiepolo's brilliant azure-pearl light system.
        - ``tintoretto_dynamic_light_pass()`` — Tintoretto's near-black
          void ground conflicts with Tiepolo's pale, luminous imprimatura.
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Tiepolo celestial light pass  "
              f"(azure={azure_push:.3f}  naples={naples_glow:.3f}  "
              f"pearl={pearl_bloom:.3f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Tiepolo celestial light pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Read canvas buffer ────────────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # Normalise to float [0, 1] — cairo surface is BGRA
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # Perceived luminance (BT.709)
        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Operation 1: Azure sky push ───────────────────────────────────────
        # Vertical weight gradient — max at top row, fades to 0 at azure_band * H
        sky_px = max(1, int(h * azure_band))
        ys = _np.linspace(0.0, 1.0, sky_px, dtype=_np.float32)
        sky_w_1d = _np.clip(1.0 - ys, 0.0, 1.0) ** 2.0
        sky_w = _np.zeros((h,), dtype=_np.float32)
        sky_w[:sky_px] = sky_w_1d
        sky_w = sky_w[:, _np.newaxis]   # (H, 1) broadcast over W

        az = sky_w * azure_push * opacity
        # Azure-cerulean: boost B strongly, slight G lift, reduce R
        r_out = _np.clip(r_out - az * 0.60, 0.0, 1.0)
        g_out = _np.clip(g_out + az * 0.10, 0.0, 1.0)
        b_out = _np.clip(b_out + az * 0.85, 0.0, 1.0)

        # ── Operation 2: Naples yellow warm glow on figure highlights ─────────
        if figure_mask is not None:
            fig_w = _np.clip(figure_mask.astype(_np.float32), 0.0, 1.0)
        else:
            fig_w = _np.ones((h, w), dtype=_np.float32)

        # Target: mid-to-high luminance pixels in the figure zone
        midlit = _np.clip((lum - 0.35) / (0.65 + 1e-8), 0.0, 1.0) * fig_w
        naples = midlit * naples_glow * opacity
        # Naples yellow: R strong, G moderate, minimal B
        r_out = _np.clip(r_out + naples * 1.00, 0.0, 1.0)
        g_out = _np.clip(g_out + naples * 0.72, 0.0, 1.0)
        b_out = _np.clip(b_out + naples * 0.08, 0.0, 1.0)

        # ── Operation 3: Pearl-white bloom on highest highlights ──────────────
        # Build bloom from the brightest pixels via Gaussian blur
        lum_img = _Image.fromarray(
            _np.clip(lum * 255.0, 0, 255).astype(_np.uint8), mode="L"
        )
        bloom_img = lum_img.filter(
            _ImageFilter.GaussianBlur(radius=float(bloom_radius))
        )
        bloom_arr = _np.asarray(bloom_img, dtype=_np.float32) / 255.0

        # Gate bloom to the very bright highlights only
        highlight_gate = _np.clip((lum - 0.72) / (0.28 + 1e-8), 0.0, 1.0) * fig_w
        pearl = highlight_gate * bloom_arr * pearl_bloom * opacity
        # Pearl white: equal R, G, B push toward neutral brilliant white
        r_out = _np.clip(r_out + pearl * 1.00, 0.0, 1.0)
        g_out = _np.clip(g_out + pearl * 0.95, 0.0, 1.0)
        b_out = _np.clip(b_out + pearl * 0.88, 0.0, 1.0)

        # ── Write back ────────────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        sky_px_count   = int((sky_w.squeeze() > 0.05).sum() * w)
        naples_px      = int((midlit * fig_w > 0.05).sum())
        pearl_px       = int((highlight_gate > 0.05).sum())
        print(f"    Tiepolo celestial light pass complete  "
              f"(sky_px={sky_px_count}  naples_px={naples_px}  pearl_px={pearl_px})")

    def zurbaran_stark_devotion_pass(
        self,
        figure_mask:          "Optional[_np.ndarray]" = None,
        void_depth:           float = 0.22,
        crystalline_strength: float = 0.16,
        midtone_compression:  float = 0.12,
        opacity:              float = 0.72,
    ) -> None:
        """
        Apply Francisco de Zurbarán's 'stark devotion' tonal polarity to the canvas.

        Zurbarán (1598–1664) — Spanish Golden Age — is the supreme painter of austere
        monasticism.  Known as 'the painter of monks', he polarises his tonal range into
        cold, near-black voids and crystalline cold-white highlights with minimal midtone
        transition.  Where Murillo suffuses every shadow with warm amber-rose tenderness,
        Zurbarán's darkness is cold, silent, absent — a void from which forms emerge with
        sculptural clarity.  His white habits are rendered in pure cold-white light
        modelled by cool blue-grey shadows, reading as marble rather than fabric.

        This pass applies three distinct operations that together produce Zurbarán's
        devotional austerity:

        1. **Cold void deepening** (lum < 0.28):
           The darkest shadow zones are cooled and slightly desaturated, pushing them
           toward the near-black cold void that defines Zurbarán's backgrounds.  Unlike
           Murillo's warm shadow warmth (+R, +G), this operation withdraws warmth from
           dark regions: a small red-channel reduction and slight blue-channel lift
           creates cold darkness rather than warm amber shadow.  Controlled by void_depth.

        2. **Crystalline white drapery push** (lum > 0.70):
           The brightest highlight zones receive a cool-white crystalline push: a subtle
           blue-channel lift and slight green-channel lift with no red addition, producing
           the cold, almost alabaster quality of Zurbarán's white habits.  This is the
           polar opposite of Murillo's warm pearl highlight push.  Controlled by
           crystalline_strength.

        3. **Midtone compression** (0.28 < lum < 0.70):
           The midtone register is gently darkened — a slight overall luminance reduction
           that compresses the middle tones toward the dark end, accentuating the stark
           polarity between void-black and crystalline-white.  The near-zero midtone
           transition is what gives Zurbarán's work its devotional sharpness: forms do
           not graduate through grey; they are present or absent.  Controlled by
           midtone_compression.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 (H, W) array in [0, 1].  1 = figure interior, 0 = background.
            When provided, all operations are gated to figure pixels — background
            pixels (mask=0) are left unchanged.  If None, applies globally.
        void_depth : float
            Magnitude of the cold void deepening in shadows (lum < 0.28).  0 = no
            darkening; 0.30+ produces very deep cold near-black voids.  Default 0.22 —
            perceptible cold absence without losing all shadow detail.
        crystalline_strength : float
            Magnitude of the cool-white push in brightest highlights (lum > 0.70).
            0 = no change; 0.25+ produces visible blue-white alabaster quality.
            Default 0.16 — clear crystalline quality without colour cast.
        midtone_compression : float
            Darkening applied to the midtone register (0.28–0.70 lum).  Compresses
            mid-grey toward the dark end, accentuating tonal polarity.  Default 0.12 —
            perceptible compression without washing out midtone detail entirely.
        opacity : float
            Global blend factor.  0 = no effect; 1 = full operations.  Default 0.72.

        Notes
        -----
        Apply AFTER build_form() and BEFORE the final glaze().  The void deepening and
        crystalline push work best once form is fully established; applying earlier can
        collapse the structural underpainting.

        Pairs naturally with:
        - chiaroscuro_modelling_pass() for further tonal range extension
        - scumble_pass() over the white drapery zones for subtle fabric texture

        Does NOT pair with:
        - murillo_vapor_pass() — Murillo's warm shadow warmth directly opposes
          Zurbarán's cold void deepening; the two cancel each other out.
        - sfumato_veil_pass() — Zurbarán's crisp edges are incompatible with
          sfumato's deliberate edge dissolution.
        """
        import numpy as _np

        print(f"  Zurbarán stark devotion pass  "
              f"(void={void_depth:.3f}  crystal={crystalline_strength:.3f}  "
              f"compress={midtone_compression:.3f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Zurbarán stark devotion pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Read canvas buffer ────────────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # Normalise to float [0, 1] — cairo surface is BGRA
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # Perceived luminance
        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        # Spatial gating weight from figure_mask
        if figure_mask is not None:
            fig_w = _np.clip(figure_mask.astype(_np.float32), 0.0, 1.0)
        else:
            fig_w = _np.ones((h, w), dtype=_np.float32)

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Operation 1: Cold void deepening ─────────────────────────────────
        # In the darkest zones, withdraw warmth and add a fractional cool-blue lift.
        # This produces cold darkness — the silent void of a monastery interior.
        shadow_thresh = 0.28
        in_shadow = lum < shadow_thresh
        shadow_w  = _np.where(in_shadow,
                              (1.0 - lum / (shadow_thresh + 1e-8)) * fig_w,
                              0.0).astype(_np.float32)
        cold_pull = shadow_w * void_depth * opacity
        # Withdraw warmth (reduce R), add cold blue-black quality (slight +B)
        r_out = _np.clip(r_out - cold_pull * 0.80, 0.0, 1.0)
        g_out = _np.clip(g_out - cold_pull * 0.55, 0.0, 1.0)
        b_out = _np.clip(b_out - cold_pull * 0.20, 0.0, 1.0)

        # ── Operation 2: Crystalline white drapery push ───────────────────────
        # In the brightest zones, add a cool blue-white lift — marble/alabaster quality.
        # No red channel addition: keeps the whites cold, not warm like Murillo or Titian.
        hi_thresh = 0.70
        in_hi  = lum > hi_thresh
        hi_w   = _np.where(in_hi,
                           (lum - hi_thresh) / (1.0 - hi_thresh + 1e-8) * fig_w,
                           0.0).astype(_np.float32)
        crystal_push = hi_w * crystalline_strength * opacity
        # Cool alabaster: slight G lift, stronger B lift, no R addition
        r_out = _np.clip(r_out + crystal_push * 0.10, 0.0, 1.0)
        g_out = _np.clip(g_out + crystal_push * 0.55, 0.0, 1.0)
        b_out = _np.clip(b_out + crystal_push * 1.00, 0.0, 1.0)

        # ── Operation 3: Midtone compression ─────────────────────────────────
        # The midtone register (28–70% lum) is slightly darkened, compressing it
        # toward the dark end.  This accentuates the stark polarity between void and
        # crystalline highlight — the characteristic Zurbarán tonal binary.
        lo, hi = 0.28, 0.70
        in_mid = (lum >= lo) & (lum <= hi)
        # Weight peaks at 0.50 luminance, falls off toward both thresholds
        mid_w  = _np.where(in_mid,
                           (1.0 - _np.abs(lum - 0.49) / (0.21 + 1e-8)) * fig_w,
                           0.0).astype(_np.float32)
        mid_w  = _np.clip(mid_w, 0.0, 1.0)
        compress_pull = mid_w * midtone_compression * opacity
        # Uniform darkening across all channels — pure tonal compression, not a hue shift
        r_out = _np.clip(r_out - compress_pull * 0.90, 0.0, 1.0)
        g_out = _np.clip(g_out - compress_pull * 0.90, 0.0, 1.0)
        b_out = _np.clip(b_out - compress_pull * 0.90, 0.0, 1.0)

        # ── Write back ────────────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        void_px    = int(in_shadow.sum())
        crystal_px = int(in_hi.sum())
        mid_px     = int(in_mid.sum())
        print(f"    Zurbarán stark devotion pass complete  "
              f"(void_px={void_px}  crystal_px={crystal_px}  mid_px={mid_px})")

    def sfumato_thermal_gradient_pass(
        self,
        figure_mask:        "Optional[_np.ndarray]" = None,
        warm_strength:      float = 0.06,
        cool_strength:      float = 0.08,
        horizon_y:          float = 0.55,
        gradient_width:     float = 0.30,
        edge_soften_radius: int   = 8,
        opacity:            float = 0.55,
    ) -> None:
        """
        Apply Leonardo da Vinci's sfumato atmospheric thermal gradient to the canvas.

        This pass models the warm-to-cool color temperature depth gradient that Leonardo
        perfected in his landscape backgrounds — most visibly in the Mona Lisa and
        Virgin of the Rocks.  The technique is distinct from simple aerial perspective
        (which only adds blue atmospheric haze) in that it simultaneously:

        (a) Warms the lower-foreground zone with subtle ochre-earth tones, simulating
            the warm reflected light of the earth plane and near-ground atmosphere.
        (b) Cools the upper-distance zone with cool blue-grey, simulating atmospheric
            scattering of short-wavelength light at depth.
        (c) Softens edges in the transitional atmospheric zone (around the horizon
            line) using Gaussian blurring — the sfumato dissolution where forms lose
            their boundaries as they recede.

        This combination produces the dreamlike atmospheric depth of Leonardo's
        backgrounds: foreground earth feels grounded and warm; middle-distance forms
        begin to lose definition; the horizon and distance dissolve into a cool,
        luminous blue-grey haze that is neither sky nor land but a nameless atmospheric
        zone.  The effect is deliberately subtle — power lives in the accumulation of
        thin, nearly imperceptible layers.

        Three operations are applied:

        1. **Foreground warm zone** (canvas rows below horizon_y):
           A radial-weighted warm earth lift (soft ochre: +R, +G-dim, slight -B) is
           applied strongest at the very bottom of the canvas, fading to zero at the
           horizon line.  This warms the earth plane and the base of the figure as if
           light bounced upward from warm ground.

        2. **Distance cool zone** (canvas rows above horizon_y):
           A linear cool lift (atmospheric blue-grey: -R-dim, -G-dim, +B) is applied
           strongest at the top of the canvas, fading to zero at the horizon line.
           This simulates Rayleigh scattering — distant forms shift toward cool blue-grey.

        3. **Atmospheric edge dissolution** (transition zone around horizon_y):
           A Gaussian-blurred version of the original canvas is blended into the
           transition zone weighted by the horizon proximity.  This produces sfumato's
           characteristic edge dissolution where forms lose sharp boundaries as they
           recede into the atmospheric middle distance.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 (H, W) array in [0, 1].  1 = figure interior, 0 = background.
            When provided, the warm/cool gradient operations are gated to background
            pixels only — the figure is protected from the atmospheric gradient (the
            figure sits in front of the landscape, not within it).
            Edge dissolution applies to background only when mask is provided.
            If None, applies globally (useful for full-canvas landscape passes).
        warm_strength : float
            Magnitude of the warm earth lift in the foreground zone.  0 = no warming;
            0.12+ produces a visible warm ochre bloom at the canvas base.  Default 0.06
            — subtly warm without visibly tinting the lower figure region.
        cool_strength : float
            Magnitude of the cool blue-grey lift in the distance zone.  0 = no cooling;
            0.15+ produces a visible atmospheric haze at the canvas top.  Default 0.08
            — light atmospheric blue without an artificial sky colour cast.
        horizon_y : float
            Vertical position of the horizon line as a fraction of canvas height.
            0.0 = top of canvas; 1.0 = bottom.  Default 0.55 — slightly below centre,
            as in many three-quarter portrait compositions where the figure's shoulders
            align with the mid-canvas and the landscape extends above.
        gradient_width : float
            Width of the transition zone as a fraction of canvas height.  Larger values
            produce a wider, smoother gradient; smaller values sharpen the warm/cool
            boundary.  Default 0.30 — a broad, smooth atmospheric transition.
        edge_soften_radius : int
            Gaussian blur radius (pixels) for the atmospheric edge dissolution in the
            transition zone.  Larger values produce a wider sfumato dissolution.
            Default 8 — appropriate for a 780×1080 canvas.
        opacity : float
            Global blend factor.  0 = no effect; 1 = full operations.  Default 0.55.

        Notes
        -----
        Apply AFTER build_form() and artist-specific passes, BEFORE the final glaze().
        This pass is most effective on images that already have an established background
        landscape — applying it to a blank canvas produces the gradient with no structural
        content to dissolve.

        Pairs naturally with:
        - aerial_perspective_pass() for combined haze + thermal gradient
        - sfumato_veil_pass() for further figure-edge dissolution
        - glaze(color=(0.72, 0.78, 0.88), opacity=0.04) — cool blue glaze that
          unifies the distant zone with the figure's atmospheric context.

        Does NOT pair with:
        - pontormo_dissonance_pass() — the dissonant acid palette is incompatible
          with atmospheric naturalness.
        - fauvist_mosaic_pass() — fauvism rejects atmospheric depth entirely.
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Sfumato thermal gradient pass  "
              f"(warm={warm_strength:.3f}  cool={cool_strength:.3f}  "
              f"horizon_y={horizon_y:.2f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Sfumato thermal gradient pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Read canvas buffer ────────────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # Normalise to float [0, 1] — cairo surface is BGRA
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Build vertical gradient maps ──────────────────────────────────────
        # Row index as fraction of canvas height, 0 = top, 1 = bottom
        row_frac = _np.linspace(0.0, 1.0, h, dtype=_np.float32)[:, None]  # (H, 1)

        horizon_px    = horizon_y
        half_grad     = gradient_width / 2.0

        # Foreground warm weight: 1 at bottom, 0 at horizon, 0 above horizon
        warm_raw = (row_frac - horizon_px) / (1.0 - horizon_px + 1e-8)
        warm_raw = _np.clip(warm_raw, 0.0, 1.0)                           # (H, 1)
        warm_map = _np.broadcast_to(warm_raw, (h, w)).copy()              # (H, W)

        # Distance cool weight: 1 at top, 0 at horizon, 0 below horizon
        cool_raw = (horizon_px - row_frac) / (horizon_px + 1e-8)
        cool_raw = _np.clip(cool_raw, 0.0, 1.0)                           # (H, 1)
        cool_map = _np.broadcast_to(cool_raw, (h, w)).copy()              # (H, W)

        # Transition zone weight: peaks at horizon, falls off with gradient_width
        dist_to_horiz = _np.abs(row_frac - horizon_px)                    # (H, 1)
        trans_raw     = 1.0 - _np.clip(dist_to_horiz / (half_grad + 1e-8), 0.0, 1.0)
        trans_map     = _np.broadcast_to(trans_raw, (h, w)).copy()        # (H, W)

        # Spatial gating: if figure_mask provided, apply gradient to background only
        if figure_mask is not None:
            fig_w  = _np.clip(figure_mask.astype(_np.float32), 0.0, 1.0)
            bg_w   = 1.0 - fig_w
        else:
            bg_w   = _np.ones((h, w), dtype=_np.float32)

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Operation 1: Foreground warm earth lift ───────────────────────────
        # Soft warm ochre: strong R, moderate G, slight negative B
        # Weighted by luminance complement — darker areas receive proportionally less
        # (avoids tinting near-black shadow zones which should remain colour-neutral)
        lum   = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f
        lum_w = _np.clip(lum + 0.30, 0.0, 1.0)   # allow even mid-darks some warmth

        warm_contrib = warm_map * bg_w * lum_w * warm_strength * opacity
        r_out = _np.clip(r_out + warm_contrib * 1.00, 0.0, 1.0)
        g_out = _np.clip(g_out + warm_contrib * 0.62, 0.0, 1.0)
        b_out = _np.clip(b_out - warm_contrib * 0.18, 0.0, 1.0)

        # ── Operation 2: Distance cool atmospheric lift ───────────────────────
        # Cool blue-grey: slight R reduction, slight G reduction, stronger B addition
        cool_contrib = cool_map * bg_w * cool_strength * opacity
        r_out = _np.clip(r_out - cool_contrib * 0.30, 0.0, 1.0)
        g_out = _np.clip(g_out - cool_contrib * 0.10, 0.0, 1.0)
        b_out = _np.clip(b_out + cool_contrib * 1.00, 0.0, 1.0)

        # ── Operation 3: Atmospheric edge dissolution in transition zone ──────
        # Gaussian blur of the current (post-gradient) working buffer in transition zone
        # Blend blurred version into the output weighted by trans_map * bg_w
        r_work = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        g_work = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        b_work = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)

        # Build blurred versions of each channel
        def _blur_channel(arr_u8: "_np.ndarray") -> "_np.ndarray":
            img    = _Image.fromarray(arr_u8, mode="L")
            blurred = img.filter(_ImageFilter.GaussianBlur(radius=float(edge_soften_radius)))
            return _np.asarray(blurred, dtype=_np.float32) / 255.0

        r_blur = _blur_channel(r_work)
        g_blur = _blur_channel(g_work)
        b_blur = _blur_channel(b_work)

        # Blend factor: transition zone weight × background mask × opacity × 0.45
        # (0.45 keeps dissolution subtle — sfumato is never a hard blur)
        blend_w = trans_map * bg_w * opacity * 0.45

        r_out = r_out * (1.0 - blend_w) + r_blur * blend_w
        g_out = g_out * (1.0 - blend_w) + g_blur * blend_w
        b_out = b_out * (1.0 - blend_w) + b_blur * blend_w

        # ── Write back ────────────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        warm_px  = int((warm_map * bg_w > 0.05).sum())
        cool_px  = int((cool_map * bg_w > 0.05).sum())
        trans_px = int((trans_map * bg_w > 0.05).sum())
        print(f"    Sfumato thermal gradient pass complete  "
              f"(warm_px={warm_px}  cool_px={cool_px}  trans_px={trans_px})")

    # ──────────────────────────────────────────────────────────────────────────
    # Session 62 — new artist: Parmigianino / parmigianino_serpentine_elegance_pass
    # Session 62 — artistic improvement: translucent_gauze_pass
    # ──────────────────────────────────────────────────────────────────────────

    def parmigianino_serpentine_elegance_pass(
        self,
        figure_mask:        "Optional[_np.ndarray]" = None,
        porcelain_strength: float = 0.14,
        lavender_shadow:    float = 0.12,
        silver_highlight:   float = 0.10,
        opacity:            float = 0.72,
    ) -> None:
        """
        Apply Parmigianino's cool porcelain refinement to the canvas.

        Parmigianino (1503–1540) — Parma / Florentine Mannerism — achieved a
        distinctive aesthetic of cool, translucent elegance that stands apart from
        every other Italian tradition.  Where the Venetians built warm amber
        subsurface luminosity (Titian's 'colorito'), and Leonardo built warm
        atmospheric sfumato, Parmigianino built COOL REFINEMENT: flesh tones that
        read as translucent porcelain or alabaster, shadows that shift toward
        silver-lavender rather than warm umber, and highlights polished to cool
        silver-white rather than warm gold.

        This pass applies three operations that together produce the porcelain
        elegance of his mature portrait style:

        1. **Porcelain midlight push** (lum 0.52–0.82, 'the face zone'):
           Midlight zones are shifted toward cool ivory — raising R and G slightly
           while adding a disproportionately larger B raise.  This cools the flesh
           tones away from warm amber and toward translucent cool porcelain.
           The effect is strongest in the upper midlight range (lum ~0.70) and
           fades toward both the highlights (too bright for colour shift) and the
           shadow zone (handled separately).

        2. **Shadow lavender-silver cool** (lum < 0.42):
           Deep and mid-shadow zones receive a cool lavender-silver push: B raised,
           G raised slightly, R reduced slightly.  This converts the expected warm
           umber/brown of oil shadows into the silvery grey-lavender characteristic
           of Parmigianino's drapery and face shadows — as seen in 'Schiava Turca'
           (c.1530–32) where face shadows read as cool lavender-grey, not warm brown.

        3. **Highlight silver polish** (lum > 0.82):
           The brightest pixels receive a cool silver-white push — B raised modestly,
           R and G raised less — producing a cool polished highlight quality.  This
           is the opposite of the warm ivory pearl used in Murillo and Rubens: no red
           warmth is added.  The result is the almost metallic highlight quality
           visible in 'Self-Portrait in a Convex Mirror' where the back of the hand
           catches the light as if glazed ceramic.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 (H, W) in [0, 1].  When provided, all operations are gated to
            the figure zone.  Background is left unchanged.
        porcelain_strength : float
            Magnitude of the cool ivory midlight push.  0.10–0.18 gives a perceptible
            but refined porcelain quality; above 0.22 the effect becomes clinical.
        lavender_shadow : float
            Strength of the cool lavender push into shadow zones.  0.08–0.15 produces
            the characteristic Parma shadow coolness; above 0.20 reads as unnatural.
        silver_highlight : float
            Strength of the cool silver polish on the highest lights.  0.06–0.14 adds
            metallic sheen without over-brightening.
        opacity : float
            Global blend factor.  Default 0.72.

        Notes
        -----
        Apply AFTER build_form() and BEFORE glaze().

        Pairs naturally with:
        - sfumato_veil_pass(warmth=0.10, chroma_dampen=0.20) — the cool sfumato
          reinforces the porcelain quality without introducing warm amber haze.
        - glaze(color=(0.92, 0.88, 0.84), opacity=0.05) — the pale cool ivory
          final glaze ties the tones into the characteristic 'enamel' surface.

        Does NOT pair well with:
        - murillo_vapor_pass() — Murillo's warm amber bloom directly opposes
          the cool ivory characteristic of Parmigianino's flesh rendering.
        - tiepolo_celestial_light_pass() — Tiepolo's warm Naples-yellow sky push
          would overwhelm the cool silvery refinement.
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Parmigianino serpentine elegance pass  "
              f"(porcelain={porcelain_strength:.3f}  lavender={lavender_shadow:.3f}  "
              f"silver={silver_highlight:.3f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Parmigianino serpentine elegance pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Read canvas buffer ────────────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # Cairo surface: BGRA channel order
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        # Spatial gating
        if figure_mask is not None:
            fig_w = _np.clip(figure_mask.astype(_np.float32), 0.0, 1.0)
        else:
            fig_w = _np.ones((h, w), dtype=_np.float32)

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Operation 1: Porcelain midlight push ─────────────────────────────
        # Target zone: lum 0.52–0.82  (the midlight to upper-midlight face zone)
        # Bell-shaped weight: peaks at lum ~0.67, falls to 0 at each boundary.
        mid_lo, mid_hi = 0.52, 0.82
        in_mid = _np.clip((lum - mid_lo) / (mid_hi - mid_lo + 1e-8), 0.0, 1.0)
        # Symmetrical bell: multiply by its mirror to create a peak at centre
        in_mid_bell = in_mid * (1.0 - in_mid) * 4.0  # peaks at 1.0 at midpoint
        porcelain_w = in_mid_bell * fig_w * porcelain_strength * opacity
        # Cool ivory: R+moderate, G+moderate, B+strong  (net: shift toward cool white)
        r_out = _np.clip(r_out + porcelain_w * 0.60, 0.0, 1.0)
        g_out = _np.clip(g_out + porcelain_w * 0.70, 0.0, 1.0)
        b_out = _np.clip(b_out + porcelain_w * 1.00, 0.0, 1.0)

        # ── Operation 2: Shadow lavender-silver cool ─────────────────────────
        # Target zone: lum < 0.42  (mid-shadow to deep shadow)
        shadow_thresh = 0.42
        shadow_w = _np.clip(1.0 - lum / (shadow_thresh + 1e-8), 0.0, 1.0)
        shadow_w = shadow_w * fig_w * lavender_shadow * opacity
        # Lavender-silver: B raised most, G slight raise, R slight reduction
        r_out = _np.clip(r_out - shadow_w * 0.30, 0.0, 1.0)
        g_out = _np.clip(g_out + shadow_w * 0.20, 0.0, 1.0)
        b_out = _np.clip(b_out + shadow_w * 1.00, 0.0, 1.0)

        # ── Operation 3: Highlight silver polish ─────────────────────────────
        # Target zone: lum > 0.82
        hi_thresh = 0.82
        hi_w = _np.clip((lum - hi_thresh) / (1.0 - hi_thresh + 1e-8), 0.0, 1.0)
        hi_w = hi_w * fig_w * silver_highlight * opacity
        # Cool silver: B raised, G raised moderately, R raised least
        r_out = _np.clip(r_out + hi_w * 0.50, 0.0, 1.0)
        g_out = _np.clip(g_out + hi_w * 0.75, 0.0, 1.0)
        b_out = _np.clip(b_out + hi_w * 1.00, 0.0, 1.0)

        # ── Write back ────────────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        mid_px    = int((in_mid_bell * fig_w > 0.05).sum())
        shadow_px = int((shadow_w > 0.005).sum())
        hi_px     = int((hi_w > 0.005).sum())
        print(f"    Parmigianino serpentine elegance pass complete  "
              f"(midlight_px={mid_px}  shadow_px={shadow_px}  highlight_px={hi_px})")

    def translucent_gauze_pass(
        self,
        figure_mask:    "Optional[_np.ndarray]" = None,
        zone_top:       float = 0.42,
        zone_bottom:    float = 0.72,
        opacity:        float = 0.35,
        cool_shift:     float = 0.06,
        weave_strength: float = 0.018,
        blur_radius:    float = 4.0,
    ) -> None:
        """
        Simulate semi-transparent gauze or velo fabric over a defined canvas zone.

        The *velo* — a thin, semi-transparent gauze wrap — appears in Renaissance
        and Mannerist portraiture as a device to add a soft, airy layer between the
        viewer and the sitter's bodice or shoulders.  Notable examples include:

        - **Mona Lisa** (Leonardo, c.1503–19) — the fine gauze at the décolletage
          creates a soft edge between the dark dress and the bare neck, adding a
          layer of translucent material that softens the neckline.
        - **Parmigianino's 'Antea'** (c.1531–35) — a translucent shoulder wrap
          that drifts across the figure, simultaneously revealing and concealing
          the dark dress beneath.
        - **Raphael's 'La Velata'** (c.1515, Pitti Palace) — a tour de force of
          painted textile: a translucent veil that covers the sitter's torso,
          showing the fabric layers beneath through a thin shimmer of gauze.

        Technically, gauze transmits light with a slight scattering — the colours
        beneath become visible but are slightly washed-out and cooled by the thin
        white fibres.  This pass simulates that optical effect using three operations:

        1. **Translucent blend**: Within the gauze zone (zone_top → zone_bottom,
           expressed as fractions of canvas height), the canvas values are blended
           toward a near-white, slightly cool scattering tone — simulating the white
           woven fibres of the gauze absorbing and scattering the underlying colours.
           The blend weight is soft (Gaussian-weighted within the zone) so the gauze
           has natural vignette edges rather than a sharp mask boundary.

        2. **Cool temperature shift**: The scattering fibres of white gauze introduce
           a very slight cooling of the transmitted light (cool_shift).  This is the
           optical equivalent of seeing warm flesh through a white diffusing layer —
           the result is slightly cooler, as if a thin cool mist has been interposed.

        3. **Woven texture** (optional, weave_strength > 0): A very subtle horizontal
           sinusoidal pattern at pixel frequency is added at the gauze zone to suggest
           the warp/weft weave of fine cloth without reading as visible lines at normal
           viewing distance.  The frequency is set to approximate the weave of a fine
           linen gauze at approximately 1:10 canvas scale.

        Parameters
        ----------
        figure_mask : np.ndarray or None
            Float32 (H, W) in [0, 1].  When provided, the gauze effect is confined
            to the figure zone.  Background is unaffected.
        zone_top : float
            Top edge of the gauze zone as fraction of canvas height (0 = top, 1 = bottom).
            Default 0.42 — approximates the neckline of a half-length portrait.
        zone_bottom : float
            Bottom edge of the gauze zone.  Default 0.72 — covers the upper torso.
        opacity : float
            Strength of the translucent blend toward the gauze scattering tone.
            0.20 = barely perceptible veil; 0.50 = clearly visible gauze.
            Default 0.35 — a visible but delicate translucency.
        cool_shift : float
            Magnitude of the cool temperature shift in the gauze zone.
            Reduces R slightly, raises B slightly.  Default 0.06.
        weave_strength : float
            Amplitude of the woven texture pattern.  0 = no texture.  Default 0.018
            — a barely-perceptible structural hint at the weave.
        blur_radius : float
            Gaussian radius (pixels) for softening the zone mask edges, ensuring
            natural vignette transitions rather than hard-cut boundaries.
            Default 4.0.

        Notes
        -----
        Apply AFTER build_form() and sfumato passes, and BEFORE final glaze().
        The gauze effect should be one of the last surface treatments.

        Pairs naturally with:
        - sfumato_veil_pass() — adds atmospheric sfumato at the edges of the
          gauze zone, further dissolving the boundary between gauze and skin.
        - parmigianino_serpentine_elegance_pass() — Parmigianino painted the most
          famous gauze wraps in Italian Mannerism; this pass directly supports his
          aesthetic.
        - bronzino_enamel_skin_pass() — Bronzino's cool enamel skin pairs naturally
          with gauze, which similarly suppresses warm tones.

        Does NOT pair with:
        - impasto_texture_pass() on the gauze zone — impasto implies thick pigment,
          which is physically incompatible with transparent fabric.
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Translucent gauze pass  "
              f"(zone={zone_top:.2f}->{zone_bottom:.2f}  opacity={opacity:.2f}  "
              f"cool={cool_shift:.3f}  weave={weave_strength:.3f}) ...")

        if opacity <= 0.0:
            print(f"    Translucent gauze pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        # ── Read canvas buffer ────────────────────────────────────────────────
        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        # ── Build soft zone mask ──────────────────────────────────────────────
        # Row fractions 0 (top) → 1 (bottom)
        row_frac = _np.linspace(0.0, 1.0, h, dtype=_np.float32)[:, _np.newaxis]  # (H, 1)

        # Tent function: ramps up from zone_top, ramps down at zone_bottom
        rise = _np.clip((row_frac - zone_top)   / (max(zone_bottom - zone_top, 1e-8) * 0.25), 0.0, 1.0)
        fall = _np.clip((zone_bottom - row_frac) / (max(zone_bottom - zone_top, 1e-8) * 0.25), 0.0, 1.0)
        zone_raw = _np.minimum(rise, fall)                      # (H, 1) tent peak = 1.0 at centre

        # Broadcast to (H, W) and apply Gaussian softening at zone edges
        zone_2d = _np.broadcast_to(zone_raw, (h, w)).copy().astype(_np.float32)  # (H, W)
        zone_img   = _Image.fromarray(_np.clip(zone_2d * 255, 0, 255).astype(_np.uint8), mode="L")
        zone_blurred = _Image.fromarray(
            _np.asarray(zone_img.filter(_ImageFilter.GaussianBlur(radius=float(blur_radius))),
                        dtype=_np.uint8), mode="L")
        zone_mask = _np.asarray(zone_blurred, dtype=_np.float32) / 255.0  # (H, W)

        # Apply figure mask gating
        if figure_mask is not None:
            zone_mask = zone_mask * _np.clip(figure_mask.astype(_np.float32), 0.0, 1.0)

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Operation 1: Translucent scatter blend ────────────────────────────
        # Gauze scattering tone: near-white with very slight warm off-white cast
        # (white linen woven threads reflecting diffused interior light)
        scatter_r, scatter_g, scatter_b = 0.96, 0.94, 0.92
        blend_w = zone_mask * opacity
        r_out = r_out * (1.0 - blend_w) + scatter_r * blend_w
        g_out = g_out * (1.0 - blend_w) + scatter_g * blend_w
        b_out = b_out * (1.0 - blend_w) + scatter_b * blend_w

        # ── Operation 2: Cool temperature shift ──────────────────────────────
        # White gauze scatters more at shorter wavelengths — introduces a very
        # slight blue-shift (cool) relative to the warm skin underneath.
        cool_w = zone_mask * cool_shift
        r_out = _np.clip(r_out - cool_w * 0.60, 0.0, 1.0)
        g_out = _np.clip(g_out - cool_w * 0.10, 0.0, 1.0)
        b_out = _np.clip(b_out + cool_w * 0.80, 0.0, 1.0)

        # ── Operation 3: Woven texture ────────────────────────────────────────
        # Very fine sinusoidal modulation at warp/weft frequency — simulates
        # the rhythmic weave of fine linen.  Amplitude is tiny (weave_strength).
        if weave_strength > 0.0:
            # Horizontal warp threads: modulate along Y axis
            y_idx = _np.arange(h, dtype=_np.float32)[:, _np.newaxis]  # (H, 1)
            warp_freq = 8.0   # ~8px period for a fine weave at portrait scale
            warp = _np.sin(y_idx * 2.0 * _np.pi / warp_freq) * weave_strength
            warp_2d = _np.broadcast_to(warp, (h, w)).copy()  # (H, W)

            # Weave only appears in the gauze zone
            weave_contrib = warp_2d * zone_mask
            # Modulate value slightly (darken at warp threads, lighten at gaps)
            r_out = _np.clip(r_out + weave_contrib, 0.0, 1.0)
            g_out = _np.clip(g_out + weave_contrib, 0.0, 1.0)
            b_out = _np.clip(b_out + weave_contrib, 0.0, 1.0)

        # ── Write back ────────────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        gauze_px = int((zone_mask > 0.05).sum())
        print(f"    Translucent gauze pass complete  (gauze_px={gauze_px})")



    def corot_silver_veil_pass(
        self,
        figure_mask:       "Optional[_np.ndarray]" = None,
        desaturation:      float = 0.38,
        cool_shift:        float = 0.04,
        green_silver:      float = 0.22,
        edge_blur_radius:  int   = 5,
        opacity:           float = 0.60,
    ) -> None:
        """
        Apply Jean-Baptiste-Camille Corot's silver veil atmospheric effect.

        Corot (1796-1875), Barbizon School / Proto-Impressionism, developed a
        systematic atmospheric technique: an all-pervading tonal unity achieved by
        desaturating all colours toward a cool silver-grey register.  His greens are
        never richly saturated - they are muted, silvery, as if seen through morning
        mist.  Skies and foliage occupy the same tonal register; this tonal
        compression is the essence of his lyrical landscape vision.

        Four operations:
        1. Chromatic desaturation toward silver-grey (global)
        2. Cool temperature shift (subtle blue lift, red reduction)
        3. Green-to-silver conversion (foliage zones)
        4. Atmospheric edge dissolution (soft blur blend)
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Corot silver veil pass  "
              f"(desat={desaturation:.3f}  cool={cool_shift:.3f}  "
              f"green_silver={green_silver:.3f}  blur_r={edge_blur_radius}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Corot silver veil pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        if figure_mask is not None:
            bg_w = 1.0 - _np.clip(figure_mask.astype(_np.float32), 0.0, 1.0)
        else:
            bg_w = _np.ones((h, w), dtype=_np.float32)

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        desat_w = bg_w * desaturation * opacity
        r_out = r_out * (1.0 - desat_w) + lum * desat_w
        g_out = g_out * (1.0 - desat_w) + lum * desat_w
        b_out = b_out * (1.0 - desat_w) + lum * desat_w

        cool_w = bg_w * cool_shift * opacity
        r_out = _np.clip(r_out - cool_w * 0.60, 0.0, 1.0)
        g_out = _np.clip(g_out - cool_w * 0.15, 0.0, 1.0)
        b_out = _np.clip(b_out + cool_w * 1.00, 0.0, 1.0)

        green_dom  = (g_out > r_out) & (g_out > b_out)
        mid_lum    = (lum > 0.25) & (lum < 0.75)
        foliage_px = green_dom & mid_lum
        gs_w       = _np.where(foliage_px, bg_w * green_silver * opacity, 0.0).astype(_np.float32)
        r_out = r_out * (1.0 - gs_w) + lum * gs_w
        g_out = g_out * (1.0 - gs_w * 0.90) + lum * gs_w * 0.90
        b_out = b_out * (1.0 - gs_w) + (lum + 0.04) * gs_w

        r_out = _np.clip(r_out, 0.0, 1.0)
        g_out = _np.clip(g_out, 0.0, 1.0)
        b_out = _np.clip(b_out, 0.0, 1.0)

        r_u8 = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        g_u8 = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        b_u8 = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)

        def _blur_ch(arr):
            img = _Image.fromarray(arr, mode="L")
            return _np.asarray(
                img.filter(_ImageFilter.GaussianBlur(radius=float(edge_blur_radius))),
                dtype=_np.float32
            ) / 255.0

        r_blur = _blur_ch(r_u8)
        g_blur = _blur_ch(g_u8)
        b_blur = _blur_ch(b_u8)

        blur_w = bg_w * opacity * 0.22
        r_out = r_out * (1.0 - blur_w) + r_blur * blur_w
        g_out = g_out * (1.0 - blur_w) + g_blur * blur_w
        b_out = b_out * (1.0 - blur_w) + b_blur * blur_w

        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        foliage_px_count = int(foliage_px.sum())
        print(f"    Corot silver veil pass complete  "
              f"(foliage_px={foliage_px_count})")

    # ─────────────────────────────────────────────────────────────────────────
    # Session 63 — Canaletto luminous veduta pass
    # ─────────────────────────────────────────────────────────────────────────

    def canaletto_luminous_veduta_pass(
        self,
        sky_lift: float = 0.18,
        stone_warm: float = 0.14,
        water_cool: float = 0.12,
        sky_band: float = 0.38,
        opacity: float = 0.65,
    ) -> None:
        """
        Apply Canaletto's defining chromatic clarity: the three-register
        Venetian veduta palette.

        Three operations applied to distinct luminance/hue zones:

        1. **Sky cerulean lift** — the upper canvas (above sky_band) receives a
           blue-channel boost and slight desaturation toward cerulean.  Canaletto's
           skies are the clearest in the whole Western landscape tradition: no
           warm haze at the horizon, just saturated, direct Venetian blue.

        2. **Warm honey-stone push** — sunlit mid-tones (moderate luminance with
           warm R>G>B dominance) are pushed further toward warm ochre-honey.
           This is the warm masonry that fills the centre of every veduta —
           the Doge's Palace, the Procuratie, the Rialto stone.

        3. **Canal silver-blue pull** — cool mid-tones (B ≥ R, moderate luminance)
           are pulled further toward cool silver-blue.  This distinguishes the
           canal-water reflections from the stone architecture in every painting
           Canaletto made of the Grand Canal.

        Parameters
        ----------
        sky_lift      : strength of the cerulean blue push in the sky zone
        stone_warm    : strength of the warm ochre push in sunlit stone zones
        water_cool    : strength of the cool silver-blue pull in water/shadow zones
        sky_band      : canvas fraction (from top) treated as sky zone (0 = top)
        opacity       : overall pass blend weight
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Canaletto luminous veduta pass "
              f"(sky_lift={sky_lift:.3f} stone_warm={stone_warm:.3f} "
              f"water_cool={water_cool:.3f} opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Canaletto luminous veduta pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # cairo BGRA → float RGB
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── 1. Sky cerulean lift ──────────────────────────────────────────────
        sky_y = int(h * sky_band)
        sky_mask = _np.zeros((h, w), dtype=_np.float32)
        if sky_y > 0:
            # linear falloff: full at top row, zero at sky_y
            for yi in range(sky_y):
                sky_mask[yi, :] = 1.0 - yi / float(sky_y)

        sky_w = sky_mask * sky_lift * opacity
        # cerulean = boost B, slight boost G, restrain R
        r_out = _np.clip(r_out - sky_w * 0.30, 0.0, 1.0)
        g_out = _np.clip(g_out + sky_w * 0.12, 0.0, 1.0)
        b_out = _np.clip(b_out + sky_w * 0.85, 0.0, 1.0)

        # ── 2. Warm stone push (sunlit masonry) ───────────────────────────────
        # Pixels where R > G > B (warm hue) and mid-high luminance (sunlit)
        warm_dom  = (r_out > g_out) & (g_out > b_out * 1.08)
        sunlit    = (lum > 0.38) & (lum < 0.88)
        stone_px  = warm_dom & sunlit & (sky_mask < 0.25)   # below sky zone
        stone_w   = _np.where(stone_px, stone_warm * opacity, 0.0).astype(_np.float32)
        # warm ochre push: lift R, gentle G, suppress B
        r_out = _np.clip(r_out + stone_w * 0.70, 0.0, 1.0)
        g_out = _np.clip(g_out + stone_w * 0.30, 0.0, 1.0)
        b_out = _np.clip(b_out - stone_w * 0.40, 0.0, 1.0)

        # ── 3. Canal silver-blue pull (water and cool shadow) ─────────────────
        # Pixels where B ≥ R (cool hue) and moderate luminance (not deepest shadow)
        cool_dom  = b_out >= r_out
        water_lum = (lum > 0.20) & (lum < 0.72)
        water_px  = cool_dom & water_lum & (sky_mask < 0.25)
        water_w   = _np.where(water_px, water_cool * opacity, 0.0).astype(_np.float32)
        # silver-blue: slight desaturation + blue tint
        r_out = _np.clip(r_out * (1.0 - water_w * 0.35) + lum * water_w * 0.35
                         - water_w * 0.06, 0.0, 1.0)
        g_out = _np.clip(g_out * (1.0 - water_w * 0.20) + lum * water_w * 0.20, 0.0, 1.0)
        b_out = _np.clip(b_out + water_w * 0.18, 0.0, 1.0)

        # Write back (BGRA)
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        stone_count = int(stone_px.sum())
        water_count = int(water_px.sum())
        print(f"    Canaletto luminous veduta pass complete  "
              f"(stone_px={stone_count}  water_px={water_count})")

    # ─────────────────────────────────────────────────────────────────────────
    # Session 63 — Artistic improvement: old-master varnish patina pass
    # ─────────────────────────────────────────────────────────────────────────

    def old_master_varnish_pass(
        self,
        amber_strength: float = 0.18,
        edge_darken: float = 0.12,
        highlight_desat: float = 0.08,
        opacity: float = 0.55,
    ) -> None:
        """
        Simulate three centuries of aged amber varnish on an old master painting.

        Museum-quality old master paintings (Rembrandt, Vermeer, Titian, Leonardo)
        have accumulated multiple layers of natural resin varnish that has yellowed
        and darkened over centuries.  The visible effect is:

        1. **Amber tint** — a warm yellow-brown cast over the entire surface.
           The blue channel is most suppressed; red and green are gently boosted.
           This is the most immediately recognisable quality of a varnished old
           master: colours that were once cooler now read as warmer, and the
           overall key is slightly lower.

        2. **Edge oxidation darkening** — varnish on the edges and corners of a
           panel or canvas oxidizes faster than the centre (less UV exposure at
           margins, but more moisture ingress).  A radial darkening mask is applied
           with a cos² falloff that is strongest at the canvas border and zero
           toward the centre.  This subtly reinforces a vignette effect.

        3. **Highlight desaturation** — the brightest specular highlights on skin,
           drapery, and metalwork are slightly desaturated by the amber overlay.
           Where a freshly-painted Titian might have pure white highlights, a
           varnished Titian has warm ivory highlights.

        This pass is intentionally subtle at default opacity (0.55) — it should
        add the sense of age and museum authenticity without noticeably distorting
        colour relationships.  Use opacity=0.20–0.35 for a barely-perceptible
        museum patina; 0.55–0.75 for a heavily varnished look.

        Parameters
        ----------
        amber_strength   : strength of the warm amber tint (R+G↑, B↓)
        edge_darken      : strength of the edge/corner darkening vignette
        highlight_desat  : desaturation of the brightest highlights
        opacity          : overall pass blend weight
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Old-master varnish pass "
              f"(amber={amber_strength:.3f} edge_darken={edge_darken:.3f} "
              f"highlight_desat={highlight_desat:.3f} opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Old-master varnish pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # cairo BGRA → float RGB
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── 1. Amber tint (yellowed varnish) ──────────────────────────────────
        # Natural resin varnish yellows: suppresses B channel most, boosts R+G
        amb = amber_strength * opacity
        r_out = _np.clip(r_out + amb * 0.22, 0.0, 1.0)
        g_out = _np.clip(g_out + amb * 0.12, 0.0, 1.0)
        b_out = _np.clip(b_out - amb * 0.38, 0.0, 1.0)

        # ── 2. Edge oxidation darkening ───────────────────────────────────────
        # cos² radial falloff: 1.0 at border, 0.0 at centre
        ys = _np.linspace(-1.0, 1.0, h)[:, _np.newaxis]
        xs = _np.linspace(-1.0, 1.0, w)[_np.newaxis, :]
        r2 = _np.clip(ys ** 2 + xs ** 2, 0.0, None)
        edge_mask = _np.clip((r2 - 0.55) / 0.45, 0.0, 1.0).astype(_np.float32)
        edge_w = edge_mask * edge_darken * opacity
        r_out = _np.clip(r_out * (1.0 - edge_w), 0.0, 1.0)
        g_out = _np.clip(g_out * (1.0 - edge_w), 0.0, 1.0)
        b_out = _np.clip(b_out * (1.0 - edge_w), 0.0, 1.0)

        # ── 3. Highlight desaturation (amber wash dulls pure whites) ─────────
        bright_px = lum > 0.78
        desat_w   = _np.where(bright_px, highlight_desat * opacity, 0.0).astype(_np.float32)
        r_out = r_out * (1.0 - desat_w) + lum * desat_w
        g_out = g_out * (1.0 - desat_w) + lum * desat_w
        b_out = b_out * (1.0 - desat_w) + lum * desat_w
        # Re-apply a gentle amber tint to desaturated highlights
        r_out = _np.clip(r_out + desat_w * 0.04, 0.0, 1.0)
        b_out = _np.clip(b_out - desat_w * 0.06, 0.0, 1.0)

        # Write back (BGRA)
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        bright_count = int(bright_px.sum())
        print(f"    Old-master varnish pass complete  "
              f"(bright_px={bright_count})")

    # ─────────────────────────────────────────────────────────────────────────
    # Session 64 — New artist: Vigée Le Brun pearlescent grace pass
    # ─────────────────────────────────────────────────────────────────────────

    def vigee_le_brun_pearlescent_grace_pass(
        self,
        rose_bloom_strength: float = 0.10,
        pearl_highlight:     float = 0.06,
        shadow_warmth:       float = 0.04,
        midtone_low:         float = 0.48,
        midtone_high:        float = 0.82,
        opacity:             float = 0.65,
    ) -> None:
        """
        Apply Élisabeth Louise Vigée Le Brun's defining skin quality.

        Vigée Le Brun (1755–1842), court portraitist to Marie Antoinette and
        the European aristocracy, developed a skin-rendering technique unique
        among her contemporaries: a warm pearlescent iridescence that makes her
        sitters appear lit from within rather than merely lit from without.

        She worked from the midtone outward — establishing a warm rose-ivory
        foundation across the whole face, then modulating toward shadow and
        highlight from that pink centre.  The result is that even her deepest
        shadows retain rose-warm quality; and her highlights, rather than
        reaching warm ivory, attain a cool pearl iridescence — the slight
        blue-cool shimmer of nacre.

        Three operations:

        1. **Rose bloom in warm midtones** — pixels with luminance in
           [midtone_low, midtone_high] receive a warm rose-ivory push
           (R+ strongly, G+ modestly, B+ very slightly).  This is the primary
           characteristic: not the red-orange of SSS but the pink-ivory of
           18th-century French aristocratic skin.

        2. **Pearl highlight** — very bright pixels (lum > midtone_high)
           receive a slight cool pearl shift (B+ slight, R- slight), converting
           pure white specular highlights to the characteristic nacre quality.
           Pearl reflects slightly cool-blue — not the warm ivory of Raphael.

        3. **Shadow warmth injection** — deepest shadow pixels (lum < 0.30)
           receive a subtle warm rose-violet push.  Vigée Le Brun's shadows are
           never cold grey — they are warm, inhabited, alive.

        Parameters
        ----------
        rose_bloom_strength : warm rose push in the lit midtone zone
        pearl_highlight     : cool pearl shift in the brightest highlights
        shadow_warmth       : warm rose-violet push in the deepest shadows
        midtone_low         : lower luminance boundary of the midtone bloom zone
        midtone_high        : upper luminance boundary of the midtone bloom zone
        opacity             : overall blend weight
        """
        import numpy as _np

        print(f"  Vigée Le Brun pearlescent grace pass "
              f"(rose={rose_bloom_strength:.3f}  pearl={pearl_highlight:.3f}  "
              f"shadow_warm={shadow_warmth:.3f}  "
              f"lum=[{midtone_low:.2f},{midtone_high:.2f}]  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Vigée Le Brun pearlescent grace pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # cairo BGRA → float RGB
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── 1. Rose bloom in warm midtones ────────────────────────────────────
        # Tent mask peaking at the centre of [midtone_low, midtone_high]
        mid_c = (midtone_low + midtone_high) * 0.5
        mid_h = (midtone_high - midtone_low) * 0.5
        midtone_mask = _np.clip(1.0 - _np.abs(lum - mid_c) / max(mid_h, 1e-8),
                                0.0, 1.0)

        rose_w = midtone_mask * rose_bloom_strength * opacity
        r_out = _np.clip(r_out + rose_w * 0.85, 0.0, 1.0)   # strong pink-rose
        g_out = _np.clip(g_out + rose_w * 0.32, 0.0, 1.0)   # modest — keeps it rose not orange
        b_out = _np.clip(b_out + rose_w * 0.10, 0.0, 1.0)   # tiny — prevents pure red cast

        # ── 2. Pearl highlight ────────────────────────────────────────────────
        # Pixels above midtone_high receive the cool nacre shimmer
        pearl_mask = _np.clip(
            (lum - midtone_high) / max(1.0 - midtone_high, 1e-8), 0.0, 1.0)
        pearl_w = pearl_mask * pearl_highlight * opacity
        r_out = _np.clip(r_out - pearl_w * 0.30, 0.0, 1.0)   # slight R pull → cooler
        b_out = _np.clip(b_out + pearl_w * 0.40, 0.0, 1.0)   # slight B lift → pearl shimmer

        # ── 3. Shadow warmth injection ────────────────────────────────────────
        # Pixels below lum=0.30 — Vigée Le Brun shadows are rose-warm, not cold
        shadow_mask = _np.clip(1.0 - lum / 0.30, 0.0, 1.0)
        shadow_w = shadow_mask * shadow_warmth * opacity
        r_out = _np.clip(r_out + shadow_w * 0.55, 0.0, 1.0)   # warm rose
        g_out = _np.clip(g_out + shadow_w * 0.15, 0.0, 1.0)
        b_out = _np.clip(b_out + shadow_w * 0.25, 0.0, 1.0)   # slight violet cast

        # ── Write back (BGRA) ─────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        midtone_px = int((midtone_mask > 0.05).sum())
        print(f"    Vigée Le Brun pearlescent grace pass complete  "
              f"(midtone_px={midtone_px})")

    # ─────────────────────────────────────────────────────────────────────────
    # Session 64 — Artistic improvement: subsurface scatter pass
    # ─────────────────────────────────────────────────────────────────────────

    def subsurface_scatter_pass(
        self,
        scatter_strength:  float = 0.14,
        scatter_radius:    float = 8.0,
        scatter_low:       float = 0.42,
        scatter_high:      float = 0.82,
        penumbra_warm:     float = 0.06,
        shadow_cool:       float = 0.04,
        opacity:           float = 0.65,
    ) -> None:
        """
        Simulate subsurface light scattering through human skin.

        When light strikes skin, a significant fraction penetrates the epidermis
        and scatters through the layers beneath — dermis, subcutaneous fat,
        capillary beds — before re-emerging at the surface displaced a few
        millimetres from the entry point.  This scattering is strongly
        wavelength-dependent: long wavelengths (red, orange) penetrate deepest
        and scatter furthest; short wavelengths (blue, violet) are absorbed near
        the surface.

        The result is the warm red-orange inner glow that distinguishes real
        skin from any painted imitation — most visible in three zones:

        1. **Lit midtones** (luminance scatter_low–scatter_high): the lit-but-
           not-specular zone where scatter path length is greatest.  These pixels
           receive a diffuse warm red-orange bloom — R+ most, G+ modest, B-.
           The bloom is softened with a Gaussian (radius ~8px) because the
           scatter path is non-directional and covers a finite skin area.

        2. **Penumbra / shadow edge** (luminance 0.28–scatter_low): the zone
           where light entering from the adjacent lit surface has scattered
           sideways into the shadow edge — the warm "inner light" that curves
           around the terminator.  A subtler deep-red warmth without bloom.

        3. **Deep shadow cool recovery** (luminance < 0.28): subsurface scatter
           fails in the deepest shadows — no light penetrates here.  A slight
           cool push (R-, B+) reinforces shadow colour separation from the warm
           lit zones, increasing perceived luminosity by contrast.

        This pass should be applied *before* final glazing and artist-specific
        passes.  At default opacity (0.65) it is visibly present but natural.
        Use opacity=0.35–0.50 for a barely-perceptible glow; 0.80–1.0 for the
        jewel-like Bouguereau/Vigée Le Brun hyper-real effect.

        Parameters
        ----------
        scatter_strength  : peak red-orange scatter boost in lit midtones
        scatter_radius    : Gaussian blur radius of scatter bloom (pixels)
        scatter_low       : lower luminance boundary of the lit-midtone zone
        scatter_high      : upper luminance boundary (above = specular, not scatter)
        penumbra_warm     : warm push in the penumbra zone (0.28–scatter_low)
        shadow_cool       : cool push in deepest shadows (lum < 0.28)
        opacity           : overall blend weight
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Subsurface scatter pass "
              f"(scatter={scatter_strength:.3f}  radius={scatter_radius:.1f}  "
              f"lum=[{scatter_low:.2f},{scatter_high:.2f}]  "
              f"penumbra={penumbra_warm:.3f}  shadow_cool={shadow_cool:.3f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Subsurface scatter pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # cairo BGRA → float RGB
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── 1. Lit-midtone scatter bloom ──────────────────────────────────────
        # Build a ramp mask over the lit-midtone range
        scatter_range = max(scatter_high - scatter_low, 1e-8)
        scatter_raw = _np.clip((lum - scatter_low) / scatter_range, 0.0, 1.0)
        scatter_raw = _np.where(lum > scatter_high, 0.0, scatter_raw)  # clamp above specular

        # Soften with Gaussian to simulate the non-local scatter path length
        scatter_img = _Image.fromarray(
            _np.clip(scatter_raw * 255, 0, 255).astype(_np.uint8), mode="L")
        scatter_blurred = _np.asarray(
            scatter_img.filter(_ImageFilter.GaussianBlur(radius=float(scatter_radius))),
            dtype=_np.float32) / 255.0

        # Apply warm red-orange bloom (R >> G > 0 > B)
        s_w = scatter_blurred * scatter_strength * opacity
        r_out = _np.clip(r_out + s_w * 0.90, 0.0, 1.0)   # strong red
        g_out = _np.clip(g_out + s_w * 0.28, 0.0, 1.0)   # modest green (orange component)
        b_out = _np.clip(b_out - s_w * 0.45, 0.0, 1.0)   # damp blue

        # ── 2. Penumbra warmth ────────────────────────────────────────────────
        # Tent mask centred on the midpoint of [0.28, scatter_low]
        pen_lo  = 0.28
        pen_mid = (pen_lo + scatter_low) * 0.5
        pen_h   = max((scatter_low - pen_lo) * 0.5, 1e-8)
        penumbra_mask = _np.clip(
            1.0 - _np.abs(lum - pen_mid) / pen_h, 0.0, 1.0)

        p_w = penumbra_mask * penumbra_warm * opacity
        r_out = _np.clip(r_out + p_w * 0.70, 0.0, 1.0)   # deep red
        g_out = _np.clip(g_out + p_w * 0.15, 0.0, 1.0)
        b_out = _np.clip(b_out - p_w * 0.20, 0.0, 1.0)

        # ── 3. Deep shadow cool recovery ─────────────────────────────────────
        # Subsurface scatter fails in the deepest shadows
        shadow_mask = _np.clip(1.0 - lum / 0.28, 0.0, 1.0)
        sc_w = shadow_mask * shadow_cool * opacity
        r_out = _np.clip(r_out - sc_w * 0.50, 0.0, 1.0)
        b_out = _np.clip(b_out + sc_w * 0.60, 0.0, 1.0)

        # ── Write back (BGRA) ─────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        scatter_px = int((scatter_blurred > 0.05).sum())
        print(f"    Subsurface scatter pass complete  "
              f"(scatter_px={scatter_px})")

    # ─────────────────────────────────────────────────────────────────────────
    # Session 65 — Alma-Tadema marble luminance pass
    # ─────────────────────────────────────────────────────────────────────────

    def alma_tadema_marble_luminance_pass(
        self,
        marble_warm_strength: float = 0.08,
        specular_cool_shift:  float = 0.06,
        specular_thresh:      float = 0.86,
        translucent_low:      float = 0.52,
        translucent_high:     float = 0.86,
        opacity:              float = 0.60,
    ) -> None:
        """
        Apply Lawrence Alma-Tadema's characteristic marble luminance quality.

        Alma-Tadema (1836–1912), Dutch-British painter of ancient Greco-Roman
        scenes, became the foremost renderer of marble in the history of Western
        painting.  His marble is not a grey-white inert solid: it is a translucent
        material that absorbs light at the surface and radiates it from within,
        simultaneously warm in the body and cool at the sharpest specular peaks.

        Three mechanisms drive his marble luminosity:

        1. **Warm translucent body** — marble in the mid-luminance range
           (translucent_low–translucent_high) receives a warm cream-gold push
           (R+ strong, G+ moderate, B-).  Pentelic and Giallo Antico marble
           contain iron impurities that give the stone a warm cast when
           backlit or side-lit.  This is the "glow from within" quality — the
           opposite of the cold grey of plaster.

        2. **Cool crystalline specular** — very bright pixels above
           specular_thresh receive a slight cool shift (B+, R-).  This is
           the direct specular reflection off the polished marble surface.
           Polished marble acts as a near-perfect mirror for the coolest
           component of daylight (skylight, not sunlight), so the very
           brightest highlights are distinctly cooler than the warm marble body.
           The contrast between warm body and cool peak creates the crystalline
           quality that sets his marble apart from Bouguereau's ivory skin.

        3. **Shadow depth** — deep shadows (lum < translucent_low * 0.5)
           receive a slight warm ochre push.  Marble shadow is not neutral grey —
           the warm stone body colours the shadow from within.

        Parameters
        ----------
        marble_warm_strength : warm cream-gold push in the marble body zone
        specular_cool_shift  : cool (B+/R-) shift in the sharpest specular peaks
        specular_thresh      : luminance threshold above which specular cooling applies
        translucent_low      : lower luminance of the warm-body translucency zone
        translucent_high     : upper luminance of the warm-body zone (below specular peak)
        opacity              : overall blend weight
        """
        import numpy as _np

        print(f"  Alma-Tadema marble luminance pass "
              f"(marble_warm={marble_warm_strength:.3f}  "
              f"specular_cool={specular_cool_shift:.3f}  "
              f"specular_thresh={specular_thresh:.2f}  "
              f"lum=[{translucent_low:.2f},{translucent_high:.2f}]  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Alma-Tadema marble luminance pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # cairo BGRA → float RGB
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── 1. Warm translucent marble body ───────────────────────────────────
        # Tent mask peaking at centre of [translucent_low, translucent_high]
        mid_c = (translucent_low + translucent_high) * 0.5
        mid_h = (translucent_high - translucent_low) * 0.5
        body_mask = _np.clip(
            1.0 - _np.abs(lum - mid_c) / max(mid_h, 1e-8), 0.0, 1.0)

        warm_w = body_mask * marble_warm_strength * opacity
        r_out = _np.clip(r_out + warm_w * 0.80, 0.0, 1.0)   # cream-gold: strong R
        g_out = _np.clip(g_out + warm_w * 0.50, 0.0, 1.0)   # moderate G
        b_out = _np.clip(b_out - warm_w * 0.10, 0.0, 1.0)   # slight B suppression

        # ── 2. Cool crystalline specular ──────────────────────────────────────
        # Pixels above specular_thresh: direct specular from skylight — cool
        specular_mask = _np.clip(
            (lum - specular_thresh) / max(1.0 - specular_thresh, 1e-8), 0.0, 1.0)
        specular_w = specular_mask * specular_cool_shift * opacity
        r_out = _np.clip(r_out - specular_w * 0.40, 0.0, 1.0)  # R- → cooler
        b_out = _np.clip(b_out + specular_w * 0.50, 0.0, 1.0)  # B+ → pearl-crystal

        # ── 3. Shadow warm ochre depth ────────────────────────────────────────
        shadow_thresh = translucent_low * 0.5
        shadow_mask = _np.clip(1.0 - lum / max(shadow_thresh, 1e-8), 0.0, 1.0)
        shadow_w = shadow_mask * (marble_warm_strength * 0.4) * opacity
        r_out = _np.clip(r_out + shadow_w * 0.60, 0.0, 1.0)   # warm ochre
        g_out = _np.clip(g_out + shadow_w * 0.38, 0.0, 1.0)
        b_out = _np.clip(b_out - shadow_w * 0.08, 0.0, 1.0)

        # ── Write back (BGRA) ─────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        specular_px = int((specular_mask > 0.05).sum())
        body_px     = int((body_mask > 0.05).sum())
        print(f"    Alma-Tadema marble luminance pass complete  "
              f"(body_px={body_px}  specular_px={specular_px})")

    # ─────────────────────────────────────────────────────────────────────────
    # Session 65 — Artistic improvement: crystalline surface pass
    # ─────────────────────────────────────────────────────────────────────────

    def crystalline_surface_pass(
        self,
        specular_radius:    float = 2.5,
        specular_strength:  float = 0.12,
        specular_thresh:    float = 0.80,
        micro_cool_shift:   float = 0.04,
        halo_radius:        float = 6.0,
        halo_warmth:        float = 0.05,
        halo_thresh:        float = 0.70,
        opacity:            float = 0.55,
    ) -> None:
        """
        Simulate specular coherence on smooth, polished surfaces.

        Inspired by Lawrence Alma-Tadema's glass-like mastery of polished marble,
        this pass applies a universal surface-quality improvement to any painted
        image: it sharpens and concentrates the specular peaks while introducing
        the warm halo that real materials produce around a sharp specular — the
        zone where the surface is not quite bright enough for direct specular
        but is close enough to receive diffuse reflected light from the bright
        zone.

        Two complementary operations:

        1. **Specular peak concentration** — the very brightest pixels
           (above specular_thresh) are enhanced with a Gaussian-sharpened
           version of themselves.  The sharpened version is computed by
           subtracting a blurred version from the original (unsharp mask
           principle) and compositing the result.  A slight cool shift
           (micro_cool_shift) is applied to the peak: polished surfaces
           reflect the coolest component of the ambient light at their
           sharpest specular angle — the same principle as Alma-Tadema's
           marble peaks.

        2. **Specular halo warmth** — pixels in a surrounding zone
           (halo_thresh–specular_thresh) receive a slight warm push.  This
           is the diffuse component of the specular lobe — the zone adjacent
           to the mirror-like peak where light is scattered in a narrow cone.
           On warm materials (marble, ivory, skin), this halo has a warm
           cream-gold cast.  Adding this halo increases the perceptual "depth"
           of the specular peak by providing a warm-to-cool gradient: warm
           halo → neutral midtone → cool peak.

        This pass is universally applicable and should be placed near the end
        of the pipeline, after artist-specific skin and material passes and
        before the final varnish.

        Parameters
        ----------
        specular_radius   : Gaussian radius for the unsharp mask (pixels)
        specular_strength : peak enhancement strength
        specular_thresh   : luminance threshold for the specular zone
        micro_cool_shift  : cool (B+/R-) shift applied to the specular peak
        halo_radius       : Gaussian radius for the halo zone blending
        halo_warmth       : warm push in the halo zone (halo_thresh–specular_thresh)
        halo_thresh       : lower luminance boundary of the halo zone
        opacity           : overall blend weight
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Crystalline surface pass "
              f"(spec_r={specular_radius:.1f}  strength={specular_strength:.3f}  "
              f"thresh={specular_thresh:.2f}  cool={micro_cool_shift:.3f}  "
              f"halo_r={halo_radius:.1f}  halo_warm={halo_warmth:.3f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print(f"    Crystalline surface pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # cairo BGRA → float RGB
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── 1. Specular peak concentration (unsharp mask on bright zone) ──────
        # Build a blurred luminance map to identify the broad bright region
        lum_img = _Image.fromarray(
            _np.clip(lum * 255.0, 0, 255).astype(_np.uint8), "L")
        lum_blur = _np.array(
            lum_img.filter(_ImageFilter.GaussianBlur(radius=specular_radius)),
            dtype=_np.float32) / 255.0

        # Unsharp mask: detail = original - blurred
        lum_detail = lum - lum_blur

        # Specular zone mask — only pixels above threshold
        specular_mask = _np.clip(
            (lum - specular_thresh) / max(1.0 - specular_thresh, 1e-8), 0.0, 1.0)

        # Apply concentrated detail push to all channels
        spec_w = specular_mask * specular_strength * opacity
        detail_lift = lum_detail * spec_w
        r_out = _np.clip(r_out + detail_lift, 0.0, 1.0)
        g_out = _np.clip(g_out + detail_lift, 0.0, 1.0)
        b_out = _np.clip(b_out + detail_lift, 0.0, 1.0)

        # Cool shift on the sharpened peaks
        cool_w = specular_mask * micro_cool_shift * opacity
        r_out = _np.clip(r_out - cool_w * 0.35, 0.0, 1.0)
        b_out = _np.clip(b_out + cool_w * 0.45, 0.0, 1.0)

        # ── 2. Specular halo warmth ────────────────────────────────────────────
        # Halo zone: halo_thresh ≤ lum < specular_thresh
        halo_mask = _np.clip(
            (lum - halo_thresh) / max(specular_thresh - halo_thresh, 1e-8),
            0.0, 1.0) * (1.0 - specular_mask)

        # Blur the halo mask slightly for a smooth transition
        halo_img  = _Image.fromarray(
            _np.clip(halo_mask * 255.0, 0, 255).astype(_np.uint8), "L")
        halo_soft = _np.array(
            halo_img.filter(_ImageFilter.GaussianBlur(radius=halo_radius)),
            dtype=_np.float32) / 255.0

        halo_w = halo_soft * halo_warmth * opacity
        r_out = _np.clip(r_out + halo_w * 0.75, 0.0, 1.0)   # warm cream-gold
        g_out = _np.clip(g_out + halo_w * 0.48, 0.0, 1.0)
        b_out = _np.clip(b_out - halo_w * 0.06, 0.0, 1.0)

        # ── Write back (BGRA) ─────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        specular_px = int((specular_mask > 0.05).sum())
        halo_px     = int((halo_soft > 0.05).sum())
        print(f"    Crystalline surface pass complete  "
              f"(specular_px={specular_px}  halo_px={halo_px})")

    # ─────────────────────────────────────────────────────────────────────────
    # Patinir world-landscape atmospheric recession pass (session 66)
    # ─────────────────────────────────────────────────────────────────────────

    def patinir_weltlandschaft_pass(self,
                                    warm_foreground:  float = 0.10,
                                    green_midground:  float = 0.08,
                                    cool_distance:    float = 0.12,
                                    horizon_near:     float = 0.55,
                                    horizon_far:      float = 0.72,
                                    transition_blur:  float = 18.0,
                                    opacity:          float = 0.55) -> None:
        """
        Patinir Weltlandschaft three-zone atmospheric recession pass.

        Joachim Patinir (c. 1480–1524) established the 'world landscape'
        (Weltlandschaft) as an independent genre: vast panoramic terrain viewed
        from a high vantage point, with systematic colour recession across three
        distinct atmospheric zones.

        Zone 1 — Foreground (below horizon_near):
            Push toward warm sandy ochre.  Rocks and earth read as warm brown,
            sunlit and textured.  Geological crispness: no aerial softening.

        Zone 2 — Middle distance (horizon_near → horizon_far):
            Push toward muted olive-green.  Foliage, water, and terrain shift to
            the characteristic Patinir sage-green hue that separates foreground
            brown from distant blue.

        Zone 3 — Far distance (above horizon_far):
            Push toward pale cool blue-grey.  The far distance dissolves into
            sky-like aerial haze — Patinir's skies and distant mountains share
            the same pale cerulean tint.

        Transition between zones is Gaussian-blurred so the colour bands
        dissolve into one another rather than producing hard horizontal seams.

        Parameters
        ----------
        warm_foreground  : strength of warm ochre push in foreground zone
        green_midground  : strength of olive-green push in middle zone
        cool_distance    : strength of cool blue-grey push in far zone
        horizon_near     : canvas Y fraction where foreground ends (0=top, 1=bottom)
        horizon_far      : canvas Y fraction where middle zone ends
        transition_blur  : Gaussian radius (px) to soften zone boundaries
        opacity          : overall blend weight
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter
        from scipy import ndimage as _ndimage

        print(f"  Patinir Weltlandschaft pass "
              f"(warm={warm_foreground:.3f}  green={green_midground:.3f}  "
              f"cool={cool_distance:.3f}  hn={horizon_near:.2f}  "
              f"hf={horizon_far:.2f}  blur={transition_blur:.1f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Patinir Weltlandschaft pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # cairo BGRA → float RGB
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # Build per-pixel Y-fraction array (0=top, 1=bottom)
        y_frac = (_np.arange(h, dtype=_np.float32) / max(h - 1, 1))[:, _np.newaxis]
        y_frac = _np.broadcast_to(y_frac, (h, w)).copy()

        # ── Zone masks (soft-edged via Gaussian blur) ─────────────────────────
        # Foreground mask: peaks at bottom, falls off above horizon_near
        fg_raw = _np.clip((y_frac - horizon_near) / max(1.0 - horizon_near, 1e-8),
                          0.0, 1.0)
        fg_img  = _Image.fromarray(
            _np.clip(fg_raw * 255, 0, 255).astype(_np.uint8), "L")
        fg_mask = _np.array(
            fg_img.filter(_ImageFilter.GaussianBlur(radius=transition_blur)),
            dtype=_np.float32) / 255.0

        # Far-distance mask: peaks at top, falls off below horizon_far
        far_raw = _np.clip((horizon_far - y_frac) / max(horizon_far, 1e-8),
                           0.0, 1.0)
        far_img  = _Image.fromarray(
            _np.clip(far_raw * 255, 0, 255).astype(_np.uint8), "L")
        far_mask = _np.array(
            far_img.filter(_ImageFilter.GaussianBlur(radius=transition_blur)),
            dtype=_np.float32) / 255.0

        # Middle-ground mask: complement of the other two
        mid_mask = _np.clip(1.0 - fg_mask - far_mask, 0.0, 1.0)

        # ── Zone 1: Foreground warm ochre push ────────────────────────────────
        # Warm sandy ochre: R↑ G slight↑ B↓
        w1 = fg_mask * warm_foreground * opacity
        r_out = _np.clip(r_out + w1 * 0.72, 0.0, 1.0)
        g_out = _np.clip(g_out + w1 * 0.32, 0.0, 1.0)
        b_out = _np.clip(b_out - w1 * 0.28, 0.0, 1.0)

        # ── Zone 2: Middle-distance olive-green push ──────────────────────────
        # Muted olive green: G↑ R slight↑ B slight↓
        w2 = mid_mask * green_midground * opacity
        r_out = _np.clip(r_out + w2 * 0.12, 0.0, 1.0)
        g_out = _np.clip(g_out + w2 * 0.65, 0.0, 1.0)
        b_out = _np.clip(b_out - w2 * 0.10, 0.0, 1.0)

        # ── Zone 3: Far-distance cool blue-grey push ──────────────────────────
        # Pale cool blue-grey: B↑ R↓ G slight↑
        w3 = far_mask * cool_distance * opacity
        r_out = _np.clip(r_out - w3 * 0.30, 0.0, 1.0)
        g_out = _np.clip(g_out + w3 * 0.15, 0.0, 1.0)
        b_out = _np.clip(b_out + w3 * 0.55, 0.0, 1.0)

        # ── Write back (BGRA) ─────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        fg_px  = int((fg_mask  > 0.05).sum())
        mid_px = int((mid_mask > 0.05).sum())
        far_px = int((far_mask > 0.05).sum())
        print(f"    Patinir Weltlandschaft pass complete  "
              f"(fg_px={fg_px}  mid_px={mid_px}  far_px={far_px})")

    # ─────────────────────────────────────────────────────────────────────────
    # Warm/cool form duality pass — session 66 artistic improvement
    # ─────────────────────────────────────────────────────────────────────────

    def warm_cool_form_duality_pass(self,
                                    warm_strength:      float = 0.08,
                                    cool_strength:      float = 0.07,
                                    midtone:            float = 0.50,
                                    transition_width:   float = 0.18,
                                    blur_radius:        float = 6.0,
                                    opacity:            float = 0.55) -> None:
        """
        Warm-light / cool-shadow form duality pass.

        The single most universal principle of traditional oil painting technique:
        lit surfaces are warmer than shadow surfaces.  This emerges from the
        physical reality of outdoor light — the warm yellow sun heats the lit side
        while the cool blue sky fills the shadow — but virtually all portrait and
        figure painters apply it indoors too as a formal device for creating the
        sensation of rounded, three-dimensional form.

        Zorn, Sargent, Velázquez, and Rembrandt all employed this principle.
        Leonardo's warm amber glaze over the lit flesh and cooler deep-shadow
        umbers is essentially the same idea at a larger tonal scale.

        Algorithm
        ---------
        1. Compute per-pixel luminance.
        2. Lit zone (lum > midtone + transition_width/2):
             push toward warm — R↑, slight G↑, B↓.
        3. Shadow zone (lum < midtone - transition_width/2):
             push toward cool — R↓, B↑.
        4. Transition zone: blend linearly between warm and cool pushes.
        5. Apply Gaussian softening to the zone mask to avoid banding.

        This pass is placed after artist-specific colour passes but before the
        final varnish.  It acts as a tonal unifier that reinforces three-
        dimensionality without overriding any artist-specific colour decisions.

        Parameters
        ----------
        warm_strength    : warm push magnitude in lit zone (R+/B- scale)
        cool_strength    : cool push magnitude in shadow zone (B+/R- scale)
        midtone          : luminance pivot point (default 0.50)
        transition_width : width of the cross-fade zone around midtone
        blur_radius      : Gaussian radius (px) for mask softening
        opacity          : overall blend weight
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Warm/cool form duality pass "
              f"(warm={warm_strength:.3f}  cool={cool_strength:.3f}  "
              f"mid={midtone:.2f}  tw={transition_width:.2f}  "
              f"blur={blur_radius:.1f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Warm/cool form duality pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # cairo BGRA → float RGB
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Lit-zone mask: ramps from 0 at midtone to 1 in bright highlights ─
        half_tw = transition_width / 2.0
        lit_raw = _np.clip((lum - (midtone + half_tw)) / max(half_tw, 1e-8),
                           0.0, 1.0)
        lit_img  = _Image.fromarray(
            _np.clip(lit_raw * 255, 0, 255).astype(_np.uint8), "L")
        lit_mask = _np.array(
            lit_img.filter(_ImageFilter.GaussianBlur(radius=blur_radius)),
            dtype=_np.float32) / 255.0

        # ── Shadow-zone mask: ramps from 0 at midtone to 1 in deepest shadows ─
        shd_raw = _np.clip(((midtone - half_tw) - lum) / max(half_tw, 1e-8),
                           0.0, 1.0)
        shd_img  = _Image.fromarray(
            _np.clip(shd_raw * 255, 0, 255).astype(_np.uint8), "L")
        shd_mask = _np.array(
            shd_img.filter(_ImageFilter.GaussianBlur(radius=blur_radius)),
            dtype=_np.float32) / 255.0

        # ── Apply warm push in lit zone (R↑ G slight↑ B↓) ────────────────────
        lw = lit_mask * warm_strength * opacity
        r_out = _np.clip(r_out + lw * 0.80, 0.0, 1.0)
        g_out = _np.clip(g_out + lw * 0.25, 0.0, 1.0)
        b_out = _np.clip(b_out - lw * 0.35, 0.0, 1.0)

        # ── Apply cool push in shadow zone (R↓ B↑) ───────────────────────────
        sw = shd_mask * cool_strength * opacity
        r_out = _np.clip(r_out - sw * 0.40, 0.0, 1.0)
        b_out = _np.clip(b_out + sw * 0.55, 0.0, 1.0)

        # ── Write back (BGRA) ─────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        lit_px = int((lit_mask > 0.05).sum())
        shd_px = int((shd_mask > 0.05).sum())
        print(f"    Warm/cool form duality pass complete  "
              f"(lit_px={lit_px}  shadow_px={shd_px})")

    # ─────────────────────────────────────────────────────────────────────────
    # Mantegna sculptural form pass — session 67 artist pass
    # ─────────────────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────────────────
    # Claude Lorrain golden light pass — session 68 artistic improvement
    # ─────────────────────────────────────────────────────────────────────────

    def claude_lorrain_golden_light_pass(self,
                                         horizon_y:      float = 0.60,
                                         glow_spread:    float = 0.45,
                                         warmth:         float = 0.18,
                                         sky_cool:       float = 0.10,
                                         water_shimmer:  float = 0.08,
                                         opacity:        float = 0.55) -> None:
        """
        Claude Lorrain golden light pass.

        Claude Lorrain (1600–1682) was the supreme master of contre-jour landscape
        light: a low sun on the horizon floods the sky with warm amber-gold while
        the upper sky remains cool cerulean blue.  The same golden glow is mirrored
        in water below the horizon.  Distant forms dissolve in the atmospheric haze.

        This pass applies a vertical luminance gradient that:

        1.  Warms the lower sky and horizon band with amber-gold (R↑ G↑ B↓).
            The maximum warm shift is at horizon_y; it falls off with a Gaussian
            envelope of width glow_spread * image_height above and below.

        2.  Cools the upper sky region (above the horizon) with a gentle blue shift
            (R↓ B↑), reinforcing the temperature contrast that defines Lorrain's
            palette: warm horizon against cool zenith.

        3.  Adds a subtle shimmer on the lower portion of the image (water / earth
            below the horizon): a faint warm-gold lift that suggests reflected light.

        Parameters
        ----------
        horizon_y      : normalised Y position of the horizon (0=top, 1=bottom).
                         0.60 places the horizon in the lower third — typical Lorrain.
        glow_spread    : standard-deviation of the horizon glow in normalised Y units.
                         Larger values spread the warm glow further up the sky.
        warmth         : maximum warm shift magnitude at the horizon centre.
        sky_cool       : cool blue shift applied to upper sky above the glow.
        water_shimmer  : additional warm lift on water/earth below the horizon.
        opacity        : overall blend weight (0=no effect, 1=full replacement).
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Claude Lorrain golden light pass "
              f"(horizon_y={horizon_y:.2f}  spread={glow_spread:.2f}  "
              f"warmth={warmth:.3f}  sky_cool={sky_cool:.3f}  "
              f"shimmer={water_shimmer:.3f}  opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Claude Lorrain golden light pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()

        # cairo BGRA → float RGB
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Vertical coordinate (0=top, 1=bottom) ────────────────────────────
        ys = _np.linspace(0.0, 1.0, h, dtype=_np.float32)  # (H,)
        # Broadcast to (H, W)
        yy = _np.tile(ys[:, _np.newaxis], (1, w))           # (H, W)

        # ── 1. Horizon warm glow — Gaussian centred on horizon_y ─────────────
        # The glow is strongest at horizon_y and falls off symmetrically above/below.
        sigma = max(glow_spread, 0.05)
        horizon_glow = _np.exp(-0.5 * ((yy - horizon_y) / sigma) ** 2)  # (H, W)

        # Warm amber-gold: R↑ strongly, G↑ moderately, B↓ slightly
        w_factor = horizon_glow * warmth * opacity
        r_out = _np.clip(r_out + w_factor * 1.00, 0.0, 1.0)
        g_out = _np.clip(g_out + w_factor * 0.62, 0.0, 1.0)
        b_out = _np.clip(b_out - w_factor * 0.30, 0.0, 1.0)

        # ── 2. Upper sky cooling (above horizon) ─────────────────────────────
        # Linear ramp: maximum cool shift at the very top, zero at horizon_y
        sky_ramp = _np.clip((horizon_y - yy) / max(horizon_y, 0.01), 0.0, 1.0)
        c_factor = sky_ramp * sky_cool * opacity
        r_out = _np.clip(r_out - c_factor * 0.45, 0.0, 1.0)
        g_out = _np.clip(g_out - c_factor * 0.10, 0.0, 1.0)
        b_out = _np.clip(b_out + c_factor * 0.60, 0.0, 1.0)

        # ── 3. Water / earth shimmer below the horizon ───────────────────────
        # Gentle warm-gold lift on everything below horizon_y, attenuating with depth.
        water_ramp = _np.clip((yy - horizon_y) / max(1.0 - horizon_y, 0.01),
                              0.0, 1.0)
        # Soft sinusoidal: maximum shimmer just below horizon, fading to near-zero at bottom
        shimmer_mask = _np.sin(water_ramp * _np.pi * 0.5)
        s_factor = shimmer_mask * water_shimmer * opacity
        r_out = _np.clip(r_out + s_factor * 0.90, 0.0, 1.0)
        g_out = _np.clip(g_out + s_factor * 0.55, 0.0, 1.0)
        b_out = _np.clip(b_out - s_factor * 0.15, 0.0, 1.0)

        # ── Write back (BGRA) ─────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        # Alpha channel untouched
        buf[:, :, 3] = _np.frombuffer(self.canvas.surface.get_data(),
                                      dtype=_np.uint8).reshape((h, w, 4))[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        warm_px = int((horizon_glow > 0.10).sum())
        print(f"    Claude Lorrain golden light pass complete  "
              f"(warm_px={warm_px})")

    # ─────────────────────────────────────────────────────────────────────────

    def mantegna_sculptural_form_pass(self,
                                      highlight_lift:   float = 0.10,
                                      shadow_deepen:    float = 0.08,
                                      edge_crisp:       float = 0.06,
                                      blur_radius:      float = 4.0,
                                      opacity:          float = 0.50) -> None:
        """
        Mantegna sculptural form pass.

        Andrea Mantegna (1431–1506) rendered the human figure as if it were
        carved from cold stone or cast in bronze.  Where Leonardo dissolved
        forms into sfumato smoke, Mantegna engraved them into mineral clarity.

        This pass detects ridge-form geometry by computing a local luminance
        gradient magnitude map.  Pixels that sit at the peak of a bright ridge
        (high luminance, surrounded by falling-away shadow) receive a pale
        chalk-cool highlight lift — the characteristic Mantegna highlight on
        the brow bone, cheekbone arc, nose bridge, and chin.  Pixels that sit
        in shadow troughs flanking these ridges receive a mild further deepening.

        Additionally, a very light sharpening kernel is applied to high-contrast
        edges in the mid-luminance range, reinforcing the engraved, graphic
        quality of Mantegna's form language.

        Parameters
        ----------
        highlight_lift  : pale chalk highlight intensity on ridge peaks
        shadow_deepen   : additional depth in shadow troughs adjacent to ridges
        edge_crisp      : unsharp-mask strength for edge reinforcement
        blur_radius     : Gaussian radius (px) for ridge peak detection
        opacity         : overall blend weight
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Mantegna sculptural form pass "
              f"(hl={highlight_lift:.3f}  sd={shadow_deepen:.3f}  "
              f"ec={edge_crisp:.3f}  blur={blur_radius:.1f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Mantegna sculptural form pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # cairo BGRA → float RGB
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        lum = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Ridge peak detection ──────────────────────────────────────────────
        # Blur luminance to find local average; pixels brighter than blur-average
        # by a margin are ridge peaks.
        lum_uint8 = _np.clip(lum * 255, 0, 255).astype(_np.uint8)
        lum_img   = _Image.fromarray(lum_uint8, "L")
        lum_blur  = _np.array(
            lum_img.filter(_ImageFilter.GaussianBlur(radius=blur_radius)),
            dtype=_np.float32) / 255.0

        # Ridge peak: local brightness above blurred neighbour average
        ridge_raw = _np.clip((lum - lum_blur) / max(0.10, 1e-8), 0.0, 1.0)
        ridge_raw = ridge_raw * (lum > 0.40).astype(_np.float32)  # only lit areas

        # Shadow trough: local darkness below blurred neighbour average
        trough_raw = _np.clip((lum_blur - lum) / max(0.10, 1e-8), 0.0, 1.0)
        trough_raw = trough_raw * (lum < 0.60).astype(_np.float32)  # only shadow areas

        # ── Pale chalk-cool highlight on ridge peaks (R↑ G↑ B↑↑) ────────────
        # Mantegna's highlights are slightly cool — whiter-grey rather than warm ivory
        hl = ridge_raw * highlight_lift * opacity
        r_out = _np.clip(r_out + hl * 0.82, 0.0, 1.0)
        g_out = _np.clip(g_out + hl * 0.86, 0.0, 1.0)
        b_out = _np.clip(b_out + hl * 0.95, 0.0, 1.0)   # slightly bluer → cool chalk

        # ── Shadow trough deepening ───────────────────────────────────────────
        # Deepen shadows at the flanks of ridge-forms (warm umber deepening)
        sd = trough_raw * shadow_deepen * opacity
        r_out = _np.clip(r_out - sd * 0.40, 0.0, 1.0)
        g_out = _np.clip(g_out - sd * 0.50, 0.0, 1.0)
        b_out = _np.clip(b_out - sd * 0.60, 0.0, 1.0)

        # ── Edge crispening (unsharp-mask on mid-luminance) ───────────────────
        # Reinforces the engraved graphic quality of Mantegna's contour lines.
        # Applied only in the mid-luminance band (0.25–0.75) to avoid blowing
        # out highlights or crushing shadows.
        if edge_crisp > 0.0:
            for ch_out, ch_f in [(r_out, r_f), (g_out, g_f), (b_out, b_f)]:
                # Per-channel unsharp mask
                ch_uint8 = _np.clip(ch_f * 255, 0, 255).astype(_np.uint8)
                ch_img   = _Image.fromarray(ch_uint8, "L")
                ch_blur  = _np.array(
                    ch_img.filter(_ImageFilter.GaussianBlur(radius=2.0)),
                    dtype=_np.float32) / 255.0
                detail = ch_f - ch_blur
                mid_mask = 1.0 - _np.abs(lum - 0.50) / 0.25   # peaks at lum=0.50
                mid_mask = _np.clip(mid_mask, 0.0, 1.0)
                # write sharpened result back into ch_out in-place via +=
                ch_out += detail * edge_crisp * opacity * mid_mask
                _np.clip(ch_out, 0.0, 1.0, out=ch_out)

        # ── Write back (BGRA) ─────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        ridge_px  = int((ridge_raw  > 0.05).sum())
        trough_px = int((trough_raw > 0.05).sum())
        print(f"    Mantegna sculptural form pass complete  "
              f"(ridge_px={ridge_px}  trough_px={trough_px})")

    # ─────────────────────────────────────────────────────────────────────────
    # Skin zone temperature pass — session 67 artistic improvement
    # ─────────────────────────────────────────────────────────────────────────

    def skin_zone_temperature_pass(self,
                                   face_cx:         float = 0.50,
                                   face_cy:         float = 0.20,
                                   face_rx:         float = 0.13,
                                   face_ry:         float = 0.18,
                                   forehead_warm:   float = 0.04,
                                   temple_cool:     float = 0.03,
                                   nose_pink:       float = 0.04,
                                   lip_rose:        float = 0.03,
                                   jaw_cool:        float = 0.03,
                                   blur_radius:     float = 8.0,
                                   opacity:         float = 0.55) -> None:
        """
        Skin zone temperature pass — session 67 artistic improvement.

        Every human face is not a uniform colour field.  Traditional painters
        from Rubens to Sargent exploited the anatomical fact that different
        facial zones have different colour temperatures:

          Forehead / brow bone:
              Slightly warmer (golden-amber).  The skin is thickest here;
              the underlying blood vessels are closer to the surface across a
              wide area.  Great portrait painters subtly warm the forehead
              relative to the cheek plane.

          Temples / eye sockets:
              Slightly cooler (blue-grey).  The skin is thinner, the bone is
              close, and small surface veins show through.  Velázquez and
              Rembrandt both added a faint cool-blue-grey tone to the temple
              zone of their portrait sitters.

          Nose tip and alar wings:
              Slightly warmer-pink (rosacea zone).  Capillaries are dense
              here; the nose picks up warmth and pink even in pale skin.

          Lips and surrounding zone (oral zone):
              Rose-pink.  Lip mucosa is supplied by dense capillary networks.
              The skin around the mouth has a slight greenish-neutral undertone
              (the orbicularis oris muscle close to surface), but the lips
              themselves are distinctly rose.

          Chin and jaw plane:
              Slightly cooler (violet-grey).  The jaw plane faces away from
              the dominant overhead light source; it receives more cool skylight
              and the bone mass cools the overlying skin.

        Algorithm
        ---------
        1. Build normalised (x, y) coordinate maps relative to the face centre.
        2. Create five Gaussian-shaped region masks — one per zone above.
        3. Apply a targeted RGB colour push to each mask, with Gaussian blur
           to soften zone boundaries so the transition is imperceptible.
        4. Blend at the specified opacity so the effect reinforces rather
           than overrides the existing painting.

        Parameters
        ----------
        face_cx        : face centre X as fraction of canvas width
        face_cy        : face centre Y as fraction of canvas height
        face_rx        : face half-width as fraction of canvas width
        face_ry        : face half-height as fraction of canvas height
        forehead_warm  : golden-warm push strength on forehead / brow
        temple_cool    : cool blue-grey push strength on temples / eye sockets
        nose_pink      : warm-pink push strength on nose tip
        lip_rose       : rose push strength on the oral zone / lips
        jaw_cool       : cool violet-grey push strength on chin / jaw plane
        blur_radius    : Gaussian radius (px) for zone mask softening
        opacity        : overall blend weight
        """
        import numpy as _np
        from PIL import Image as _Image, ImageFilter as _ImageFilter

        print(f"  Skin zone temperature pass "
              f"(face_cx={face_cx:.2f}  face_cy={face_cy:.2f}  "
              f"rx={face_rx:.2f}  ry={face_ry:.2f}  "
              f"fwarm={forehead_warm:.3f}  tcool={temple_cool:.3f}  "
              f"npink={nose_pink:.3f}  lrose={lip_rose:.3f}  "
              f"jcool={jaw_cool:.3f}  blur={blur_radius:.1f}  "
              f"opacity={opacity:.2f}) ...")

        if opacity <= 0.0:
            print("    Skin zone temperature pass skipped (opacity=0)")
            return

        h, w = self.h, self.w

        buf  = _np.frombuffer(self.canvas.surface.get_data(),
                              dtype=_np.uint8).reshape((h, w, 4)).copy()
        orig = buf.copy()

        # cairo BGRA → float RGB
        b_f = buf[:, :, 0].astype(_np.float32) / 255.0
        g_f = buf[:, :, 1].astype(_np.float32) / 255.0
        r_f = buf[:, :, 2].astype(_np.float32) / 255.0

        r_out = r_f.copy()
        g_out = g_f.copy()
        b_out = b_f.copy()

        # ── Coordinate grids ──────────────────────────────────────────────────
        cx_px = int(face_cx * w)
        cy_px = int(face_cy * h)
        rx_px = max(1, int(face_rx * w))
        ry_px = max(1, int(face_ry * h))

        ys = (_np.arange(h, dtype=_np.float32) - cy_px) / ry_px
        xs = (_np.arange(w, dtype=_np.float32) - cx_px) / rx_px
        yy, xx = _np.meshgrid(ys, xs, indexing="ij")  # (H, W)

        # Elliptical face mask — only pixels inside the face ellipse get treated.
        face_dist = xx ** 2 + yy ** 2
        face_mask = _np.clip(1.0 - (face_dist - 0.70) / 0.30, 0.0, 1.0)

        def _zone_mask(x0: float, y0: float, sigma: float) -> _np.ndarray:
            """Gaussian blob centred at (x0, y0) in normalised face coords."""
            raw = _np.exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * sigma ** 2))
            raw = raw * face_mask
            img = _Image.fromarray(
                _np.clip(raw * 255, 0, 255).astype(_np.uint8), "L")
            blurred = _np.array(
                img.filter(_ImageFilter.GaussianBlur(radius=blur_radius)),
                dtype=_np.float32) / 255.0
            return blurred

        # ── Zone 1: Forehead — warm golden-amber (R↑ G↑ B- slight) ─────────
        # Centred at top of face ellipse (y ≈ -0.55 normalised)
        fh_mask = _zone_mask(0.0, -0.55, sigma=0.38)
        fw = fh_mask * forehead_warm * opacity
        r_out = _np.clip(r_out + fw * 0.85, 0.0, 1.0)
        g_out = _np.clip(g_out + fw * 0.48, 0.0, 1.0)
        b_out = _np.clip(b_out - fw * 0.18, 0.0, 1.0)

        # ── Zone 2: Temples / eye sockets — cool blue-grey (R↓ B↑) ─────────
        # Two lobes, left and right temple
        for temple_x in (-0.72, 0.72):
            t_mask = _zone_mask(temple_x, -0.10, sigma=0.28)
            tw = t_mask * temple_cool * opacity
            r_out = _np.clip(r_out - tw * 0.35, 0.0, 1.0)
            g_out = _np.clip(g_out - tw * 0.10, 0.0, 1.0)
            b_out = _np.clip(b_out + tw * 0.42, 0.0, 1.0)

        # ── Zone 3: Nose tip — warm pink (R↑ G slight↑ B slight↑) ──────────
        # Centred slightly below face centre (y ≈ +0.28 normalised)
        n_mask = _zone_mask(0.05, 0.28, sigma=0.14)
        nw = n_mask * nose_pink * opacity
        r_out = _np.clip(r_out + nw * 0.90, 0.0, 1.0)
        g_out = _np.clip(g_out + nw * 0.30, 0.0, 1.0)
        b_out = _np.clip(b_out + nw * 0.15, 0.0, 1.0)

        # ── Zone 4: Lips / oral zone — rose (R↑ G↓ slight B slight) ────────
        # Centred at y ≈ +0.50 normalised
        l_mask = _zone_mask(0.04, 0.50, sigma=0.18)
        lw = l_mask * lip_rose * opacity
        r_out = _np.clip(r_out + lw * 0.80, 0.0, 1.0)
        g_out = _np.clip(g_out - lw * 0.12, 0.0, 1.0)
        b_out = _np.clip(b_out + lw * 0.22, 0.0, 1.0)

        # ── Zone 5: Chin / jaw plane — cool violet-grey (R↓ slight B↑) ─────
        # Centred at y ≈ +0.82 normalised
        j_mask = _zone_mask(0.0, 0.82, sigma=0.30)
        jw = j_mask * jaw_cool * opacity
        r_out = _np.clip(r_out - jw * 0.30, 0.0, 1.0)
        g_out = _np.clip(g_out - jw * 0.12, 0.0, 1.0)
        b_out = _np.clip(b_out + jw * 0.38, 0.0, 1.0)

        # ── Write back (BGRA) ─────────────────────────────────────────────────
        buf[:, :, 2] = _np.clip(r_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b_out * 255.0, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]

        self.canvas.surface.get_data()[:] = buf.tobytes()

        active_px = int((face_mask > 0.05).sum())
        print(f"    Skin zone temperature pass complete  "
              f"(face_px={active_px})")
