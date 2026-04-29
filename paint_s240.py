"""paint_s240.py -- Session 240: The Regatta at Deauville (Dufy Chromatic Dissociation)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter

W, H = 520, 680

# ── Palette (Dufy-inspired) ──────────────────────────────────────────────────
CERULEAN      = (0.14, 0.52, 0.88)   # Mediterranean sea, sky
DEEP_COBALT   = (0.10, 0.28, 0.60)   # sea shadow, depth
NAPLES_YELLOW = (0.90, 0.84, 0.38)   # sunlit sand, sails in sun
VERMILLION    = (0.88, 0.28, 0.20)   # pennants, hull accent
VIRIDIAN      = (0.18, 0.60, 0.42)   # palm fronds, waterline
WHITE_SAIL    = (0.96, 0.96, 0.93)   # sails catching sun
VIOLET_SHADE  = (0.56, 0.22, 0.60)   # shadows on promenade
OCHRE_WARM    = (0.82, 0.64, 0.26)   # beach, awning warmth
NEAR_WHITE    = (0.95, 0.94, 0.90)   # paper/canvas ground
HULL_RED      = (0.78, 0.22, 0.16)   # racing hull
HULL_COBALT   = (0.12, 0.28, 0.68)   # second hull
HULL_GREEN    = (0.20, 0.52, 0.32)   # third hull
FIGURE_DARK   = (0.22, 0.18, 0.14)   # spectator silhouettes
SAND_WARM     = (0.88, 0.80, 0.58)   # beach foreground
MAST_DARK     = (0.16, 0.14, 0.12)   # mast/rigging
SKY_HAZE      = (0.72, 0.84, 0.94)   # pale sky horizon haze
PENNANT_GOLD  = (0.92, 0.76, 0.18)   # gold race pennants


def _blend(arr, col, strength):
    return arr * (1.0 - strength) + np.array(col, dtype=np.float32) * strength


def _ellipse(arr, cx, cy, rx, ry, color, opacity=1.0, feather=0.12):
    h, w = arr.shape[:2]
    rx, ry = max(rx, 1), max(ry, 1)
    for dy in range(-int(ry * 1.15), int(ry * 1.15) + 1):
        for dx in range(-int(rx * 1.15), int(rx * 1.15) + 1):
            px, py = cx + dx, cy + dy
            if 0 <= px < w and 0 <= py < h:
                d = (dx / rx) ** 2 + (dy / ry) ** 2
                if d <= (1.0 + feather) ** 2:
                    alpha = max(0.0, min(1.0, (1.0 + feather - math.sqrt(d)) / (feather + 1e-6)))
                    arr[py, px] = _blend(arr[py, px], color, alpha * opacity)


def _rect(arr, x0, y0, x1, y1, color, opacity=1.0):
    h, w = arr.shape[:2]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    arr[y0:y1, x0:x1] = _blend(arr[y0:y1, x0:x1], color, opacity)


def _line(arr, x0, y0, x1, y1, color, thickness=1, opacity=0.90):
    h, w = arr.shape[:2]
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        t = i / steps
        x = int(x0 + t * (x1 - x0))
        y = int(y0 + t * (y1 - y0))
        for ty in range(-thickness, thickness + 1):
            for tx in range(-thickness, thickness + 1):
                if tx * tx + ty * ty <= thickness * thickness:
                    px, py = x + tx, y + ty
                    if 0 <= px < w and 0 <= py < h:
                        arr[py, px] = _blend(arr[py, px], color, opacity)


def _triangle(arr, pts, color, opacity=0.92):
    """Fill a triangle defined by three (x, y) points."""
    h, w = arr.shape[:2]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = max(0, min(xs)), min(w - 1, max(xs))
    y0, y1 = max(0, min(ys)), min(h - 1, max(ys))
    (ax, ay), (bx, by), (cx, cy) = pts
    denom = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy) + 1e-9
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            w1 = ((by - cy) * (x - cx) + (cx - bx) * (y - cy)) / denom
            w2 = ((cy - ay) * (x - cx) + (ax - cx) * (y - cy)) / denom
            w3 = 1.0 - w1 - w2
            if w1 >= 0 and w2 >= 0 and w3 >= 0:
                arr[y, x] = _blend(arr[y, x], color, opacity)


def make_reference():
    ref = np.zeros((H, W, 3), dtype=np.float32)
    rng = np.random.RandomState(240)

    # ── Sky: cerulean blue graduating to pale haze at horizon ──
    horizon_y = int(H * 0.42)
    for y in range(horizon_y):
        t = y / max(horizon_y - 1, 1)
        # Deeper cerulean at top, paler haze toward horizon
        sky_col = np.array(CERULEAN, dtype=np.float32) * (1.0 - t * 0.45) + \
                  np.array(SKY_HAZE, dtype=np.float32) * t * 0.55
        ref[y, :] = sky_col

    # ── Sea: deep cerulean with cobalt shadow bands ──
    sea_y_top = horizon_y
    sea_y_bot = int(H * 0.68)
    for y in range(sea_y_top, sea_y_bot):
        t = (y - sea_y_top) / max(sea_y_bot - sea_y_top - 1, 1)
        sea_col = _blend(np.array(CERULEAN, dtype=np.float32),
                         DEEP_COBALT, t * 0.55)
        ref[y, :] = sea_col
        # Horizontal wave-shimmer bands in cerulean/cobalt
        for wave_x in range(0, W, 18 + rng.randint(0, 8)):
            band_w = 3 + rng.randint(0, 5)
            for bx in range(wave_x, min(wave_x + band_w, W)):
                ref[y, bx] = _blend(ref[y, bx], WHITE_SAIL, 0.18)

    # ── Beach / promenade foreground ──
    beach_y = sea_y_bot
    for y in range(beach_y, H):
        t = (y - beach_y) / max(H - beach_y - 1, 1)
        beach_col = _blend(np.array(SAND_WARM, dtype=np.float32),
                           OCHRE_WARM, t * 0.35)
        ref[y, :] = beach_col

    # ── Background coastline / cliffs (right side) ──
    cliff_x = int(W * 0.70)
    for y in range(int(H * 0.28), horizon_y):
        t = (y - int(H * 0.28)) / max(horizon_y - int(H * 0.28) - 1, 1)
        cliff_h = int((horizon_y - y) * 0.6)
        for x in range(cliff_x + int(t * W * 0.18), W):
            ref[y, x] = _blend(ref[y, x], (0.74, 0.78, 0.72), 0.55)

    # ── Sailboat 1 (left, closest): red hull ──
    # Hull
    b1x, b1y = int(W * 0.22), int(H * 0.52)
    _ellipse(ref, b1x, b1y + 14, 38, 10, HULL_RED, opacity=0.95)
    _ellipse(ref, b1x, b1y + 18, 40, 7, DEEP_COBALT, opacity=0.65)
    # Mast
    _line(ref, b1x, b1y + 10, b1x + 4, b1y - 105, MAST_DARK, thickness=1)
    # Main sail
    _triangle(ref, [(b1x + 4, b1y - 105), (b1x + 44, b1y + 6), (b1x + 4, b1y + 6)],
              WHITE_SAIL, opacity=0.93)
    # Jib
    _triangle(ref, [(b1x + 4, b1y - 90), (b1x - 32, b1y + 8), (b1x + 4, b1y + 8)],
              WHITE_SAIL, opacity=0.82)
    # Pennant
    _line(ref, b1x + 4, b1y - 105, b1x + 20, b1y - 97, VERMILLION, thickness=1)

    # ── Sailboat 2 (centre, receding): cobalt hull ──
    b2x, b2y = int(W * 0.50), int(H * 0.48)
    _ellipse(ref, b2x, b2y + 12, 30, 8, HULL_COBALT, opacity=0.90)
    _ellipse(ref, b2x, b2y + 16, 32, 5, DEEP_COBALT, opacity=0.55)
    _line(ref, b2x, b2y + 8, b2x + 3, b2y - 82, MAST_DARK, thickness=1)
    _triangle(ref, [(b2x + 3, b2y - 82), (b2x + 36, b2y + 6), (b2x + 3, b2y + 6)],
              WHITE_SAIL, opacity=0.90)
    _triangle(ref, [(b2x + 3, b2y - 70), (b2x - 24, b2y + 6), (b2x + 3, b2y + 6)],
              WHITE_SAIL, opacity=0.78)
    _line(ref, b2x + 3, b2y - 82, b2x + 16, b2y - 75, PENNANT_GOLD, thickness=1)

    # ── Sailboat 3 (far right, distant): green hull ──
    b3x, b3y = int(W * 0.72), int(H * 0.45)
    _ellipse(ref, b3x, b3y + 9, 22, 6, HULL_GREEN, opacity=0.85)
    _ellipse(ref, b3x, b3y + 13, 24, 4, DEEP_COBALT, opacity=0.50)
    _line(ref, b3x, b3y + 6, b3x + 2, b3y - 60, MAST_DARK, thickness=1)
    _triangle(ref, [(b3x + 2, b3y - 60), (b3x + 26, b3y + 5), (b3x + 2, b3y + 5)],
              WHITE_SAIL, opacity=0.88)
    _triangle(ref, [(b3x + 2, b3y - 52), (b3x - 18, b3y + 5), (b3x + 2, b3y + 5)],
              WHITE_SAIL, opacity=0.75)
    _line(ref, b3x + 2, b3y - 60, b3x + 12, b3y - 54, VERMILLION, thickness=1)

    # ── Palm tree (left foreground) ──
    palm_x, palm_y = int(W * 0.09), int(H * 0.82)
    # Trunk
    _line(ref, palm_x, palm_y, palm_x + 6, palm_y - 90, (0.28, 0.22, 0.14), thickness=3)
    # Fronds (five arching lines)
    for angle_deg in [-55, -30, -5, 20, 45]:
        rad = math.radians(angle_deg - 90)
        fx = palm_x + 6 + int(math.cos(rad) * 48)
        fy = (palm_y - 90) + int(math.sin(rad) * 48)
        _line(ref, palm_x + 6, palm_y - 90, fx, fy, VIRIDIAN, thickness=2, opacity=0.88)
        # Leaflet branches
        for frac in (0.4, 0.6, 0.8, 1.0):
            lx = palm_x + 6 + int(math.cos(rad) * 48 * frac)
            ly = (palm_y - 90) + int(math.sin(rad) * 48 * frac)
            perp = rad + math.pi / 2
            lex1 = lx + int(math.cos(perp) * 12)
            ley1 = ly + int(math.sin(perp) * 12)
            lex2 = lx - int(math.cos(perp) * 12)
            ley2 = ly - int(math.sin(perp) * 12)
            _line(ref, lx, ly, lex1, ley1, VIRIDIAN, thickness=1, opacity=0.70)
            _line(ref, lx, ly, lex2, ley2, VIRIDIAN, thickness=1, opacity=0.70)

    # ── Second palm (partially visible, right edge) ──
    palm2_x, palm2_y = int(W * 0.91), int(H * 0.78)
    _line(ref, palm2_x, palm2_y, palm2_x - 4, palm2_y - 75, (0.28, 0.22, 0.14), thickness=3)
    for angle_deg in [-135, -110, -85, -60]:
        rad = math.radians(angle_deg - 90)
        fx = palm2_x - 4 + int(math.cos(rad) * 42)
        fy = (palm2_y - 75) + int(math.sin(rad) * 42)
        _line(ref, palm2_x - 4, palm2_y - 75, fx, fy, VIRIDIAN, thickness=2, opacity=0.80)

    # ── Spectator figures on promenade ──
    fig_y_base = int(H * 0.72)
    for i, (fig_x, fig_h) in enumerate([
        (int(W * 0.18), 28),
        (int(W * 0.26), 26),
        (int(W * 0.32), 30),
        (int(W * 0.38), 24),
        (int(W * 0.60), 25),
        (int(W * 0.66), 29),
        (int(W * 0.74), 22),
        (int(W * 0.80), 26),
    ]):
        # Body
        fig_col = [FIGURE_DARK, HULL_RED, HULL_COBALT, VIRIDIAN][i % 4]
        _ellipse(ref, fig_x, fig_y_base, 5, fig_h // 2, fig_col, opacity=0.82)
        # Head
        _ellipse(ref, fig_x, fig_y_base - fig_h // 2 - 5, 4, 4,
                 (0.78, 0.60, 0.44), opacity=0.76)
        # Hat (parasol suggestion)
        if i % 3 == 0:
            _ellipse(ref, fig_x, fig_y_base - fig_h // 2 - 10, 8, 3,
                     [VERMILLION, PENNANT_GOLD, VIRIDIAN][i % 3], opacity=0.72)

    # ── Race pennants / bunting between masts ──
    # String of pennants across the middle sea zone
    pn_y = int(H * 0.44)
    colors_pn = [VERMILLION, PENNANT_GOLD, CERULEAN, VIRIDIAN, WHITE_SAIL, VERMILLION]
    for i in range(18):
        px_start = int(W * 0.08) + i * int(W * 0.05)
        py_start = pn_y + rng.randint(-4, 4)
        px_end   = px_start + int(W * 0.04)
        py_end   = py_start + rng.randint(-3, 3)
        pcol     = colors_pn[i % len(colors_pn)]
        # Small triangular pennant
        _triangle(ref,
                  [(px_start, py_start), (px_start + 8, py_start + 6),
                   (px_start, py_start + 12)],
                  pcol, opacity=0.85)
        _line(ref, px_end, py_end, px_end + 14, py_end - 2, (0.50, 0.44, 0.38),
              thickness=1, opacity=0.55)

    # ── Water reflections: vertical stripes of cerulean / white ──
    for _ in range(32):
        rx = rng.randint(0, W)
        ry = rng.randint(sea_y_top, sea_y_bot - 10)
        rh = rng.randint(4, 18)
        rw = rng.randint(1, 4)
        rcol = WHITE_SAIL if rng.rand() < 0.4 else CERULEAN
        _rect(ref, rx, ry, rx + rw, ry + rh, rcol, opacity=0.30)

    # ── Café parasols / awnings in foreground right ──
    para_cx = int(W * 0.78)
    para_cy = int(H * 0.76)
    _ellipse(ref, para_cx, para_cy, 32, 10, VERMILLION, opacity=0.80)
    _line(ref, para_cx, para_cy, para_cx, para_cy + 22, MAST_DARK, thickness=2)

    para_cx2 = int(W * 0.86)
    _ellipse(ref, para_cx2, para_cy - 4, 28, 9, NAPLES_YELLOW, opacity=0.80)
    _line(ref, para_cx2, para_cy - 4, para_cx2, para_cy + 18, MAST_DARK, thickness=2)

    return Image.fromarray(np.clip(ref * 255, 0, 255).astype(np.uint8), "RGB")


def paint():
    ref = make_reference()
    p = Painter(W, H, seed=240)

    # Near-white ground (Dufy's characteristic light primed canvas/paper)
    p.tone_ground((0.92, 0.92, 0.90), texture_strength=0.03)

    # Underpainting — large blocking strokes, sea + sky masses
    p.underpainting(ref, stroke_size=44, n_strokes=160, opacity=0.82)

    # Block in — two passes, broad then medium
    p.block_in(ref, stroke_size=28, n_strokes=220, opacity=0.76)
    p.block_in(ref, stroke_size=16, n_strokes=280, opacity=0.70)

    # Build form — medium then fine strokes
    p.build_form(ref, stroke_size=9, n_strokes=340, opacity=0.65)
    p.build_form(ref, stroke_size=4, n_strokes=420, opacity=0.60)

    # Place lights — crisp highlight touches (white sails, wave highlights)
    p.place_lights(ref, stroke_size=2, n_strokes=180, opacity=0.72)

    # ── Session 240 new artistic pass: Dufy Chromatic Dissociation (151st mode) ──
    p.dufy_chromatic_dissociation_pass(
        outline_sigma=1.4,
        outline_threshold=0.16,
        outline_darkness=0.68,
        chroma_dx=10,
        chroma_dy=7,
        saturation_lift=0.30,
        opacity=0.80,
    )

    # ── Session 240 artistic improvement: Sfumato Focus ──
    # Focus on the primary sailboat (boat 1) at left centre
    p.paint_sfumato_focus_pass(
        cx=0.24,
        cy=0.46,
        focus_radius=0.28,
        max_sigma=3.5,
        sat_falloff=0.22,
        transition_k=5.0,
        opacity=0.55,
    )

    # Diffuse boundary — soft edges between sea/sky and boat forms
    p.diffuse_boundary_pass(opacity=0.30)

    # Final glaze: thin cerulean wash to unify the Mediterranean light
    p.glaze((0.14, 0.52, 0.88), opacity=0.12)

    # Vignette
    p.vignette(strength=0.18)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s240_dufy_deauville_regatta.png")
    p.canvas.save(out_path)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    paint()
