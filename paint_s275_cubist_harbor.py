"""
paint_s275_cubist_harbor.py -- Session 275

"Cadaques Harbor at Dawn -- in the manner of Pablo Picasso (Analytic Cubism)"

Image Description
-----------------
Subject & Composition
    A Mediterranean harbor viewed from a terrace above -- Cadaques, Catalonia,
    Spain, the village where Pablo Picasso worked in the summer of 1910 during
    the defining period of Analytic Cubism. Canvas landscape format (1440 x 1040).
    The composition organizes three horizontal bands that interpenetrate as Cubist
    planes: an upper zone of pale dawn sky with warm ochre-gold at the horizon;
    a middle zone of stacked white cubic houses climbing the steep cliff face,
    their irregular rooflines and shadowed walls forming naturally geometric
    architecture; and a lower zone of deep blue-grey harbor water with the dark
    silhouettes of three fishing boats (llauts) at rest. The viewpoint is from a
    terrace at approximately 60% height -- we look slightly downward through the
    white village toward the harbor below.

The Subject
    The architecture of Cadaques is the primary subject -- the same whitewashed
    cubic houses that Picasso saw from his rented house in summer 1910, the same
    geometric cliff-face village that gave him a visual grammar of stacked planes.
    The buildings range from near-white in full sun (pale cream, warm ochre) to
    deep umber-brown in shadow (north-facing walls, under-eaves), with cool
    blue-grey in the recessed doorway voids and window openings. Their forms are
    clean cubes and rectangles, stacked and offset, with occasional angled party
    walls creating diagonal transitions between the horizontal and vertical grid.
    The architecture's natural geometry IS the point: Picasso did not impose
    Cubism on Cadaques -- Cadaques already was Cubism.

    Three harbor boats (llauts, traditional Catalan fishing boats) sit motionless
    on the barely-disturbed water. Their hulls are dark umber-black; their masts
    are thin dark verticals cutting across the reflected sky.

The Environment
    SKY (upper 22%): Dawn, approximately 20 minutes after sunrise. Pale blue-grey
    at the zenith, transitioning to warm ochre-gold at the horizon. The sky has
    the luminous haze of early morning Mediterranean air: not pure blue but a
    slightly milky, atmospheric blue-grey.

    CLIFF FACE AND ARCHITECTURE (middle 52%): The white cubic houses occupy the
    full width of the canvas, stacked three to four stories high on the steep
    cliff. Full-sun faces (south and east) are pale cream-ochre. Shadow faces
    are cool umber-grey. Windows and doorways are deep blue-black voids. Stone
    retaining walls are raw umber. The whole cliff-face reads as an irregular
    stacked grid of light and dark rectangles -- a naturally-occurring Cubist
    tessellation.

    HARBOR WATER (lower 26%): Deep blue-grey, almost still at dawn. Dark umber-
    black boat hulls with thin dark masts. The cliff base meets the water as a
    hard, clean line -- stone quay, no beach.

Technique & Palette
    Pablo Picasso Analytic Cubism mode -- session 275, 186th distinct mode.

    Pipeline:
    1. Procedural reference: dawn sky gradient, stacked cubic architecture,
       harbor water, boat silhouettes.
    2. tone_ground: warm ochre-umber (0.42, 0.35, 0.18).
    3. underpainting x2: establish tonal architecture.
    4. block_in x2: build sky zone, architecture masses, harbor water.
    5. build_form x2: develop architectural surface, window voids, boat forms.
    6. place_lights: dawn sky warmth, sun-lit wall faces, mast highlights.
    7. paint_impasto_ridge_lighting_pass (s275 improvement): directional raking
       light from upper-left on all paint ridges.
    8. picasso_cubist_fragmentation_pass (s275, 186th mode): angular Voronoi
       facet decomposition with Analytic Cubism restricted palette.
    9. paint_aerial_perspective_pass: cool atmospheric recession in distance.

    Palette (Analytic Cubism restricted):
    ochre (0.72/0.60/0.30) -- warm grey (0.58/0.56/0.52) --
    raw umber (0.35/0.27/0.15) -- pale cream (0.88/0.84/0.72) --
    dark umber (0.14/0.11/0.08) -- muted ochre-grey (0.48/0.42/0.28)

Mood & Intent
    The painting is a historical reimagination: Picasso in Cadaques, summer 1910,
    seeing the village through the accumulated analysis of months of Cubist work.
    By now the village has ceased to be merely white houses stacked on a cliff --
    it has become a grammar of planes, a visual system. The harbor water is the
    most coherent zone, the least analyzed -- it remains the still, reflective
    surface that anchors the chaotic analysis above.
    The viewer should walk away with a sense of STRUCTURED PERCEPTION -- the
    realization that visual field, when attended to analytically, is already a
    Cubist painting. Cadaques was not a subject that Picasso imposed Cubism upon:
    it was a pre-existing Cubist composition waiting to be recognized.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stroke_engine import Painter

W, H = 1440, 1040
SEED = 275
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s275_cubist_harbor.png")


def build_reference() -> np.ndarray:
    """Build a procedural reference for the Cadaques harbor Cubist landscape."""
    rng = np.random.default_rng(SEED)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    sky_bottom  = int(H * 0.22)
    arch_bottom = int(H * 0.74)
    water_top   = arch_bottom

    # ── Sky gradient ──────────────────────────────────────────────────────────
    for y in range(sky_bottom):
        t = y / float(sky_bottom - 1)
        if t < 0.6:
            s = t / 0.6
            r = 0.58 + (0.68 - 0.58) * s
            g = 0.62 + (0.68 - 0.62) * s
            b = 0.70 + (0.66 - 0.70) * s
        else:
            s = (t - 0.6) / 0.4
            r = 0.68 + (0.88 - 0.68) * s
            g = 0.68 + (0.80 - 0.68) * s
            b = 0.66 + (0.42 - 0.66) * s
        noise = rng.uniform(-0.006, 0.006, W).astype(np.float32)
        ref[y, :, 0] = np.clip(r + noise, 0, 1)
        ref[y, :, 1] = np.clip(g + noise * 0.8, 0, 1)
        ref[y, :, 2] = np.clip(b + noise * 0.5, 0, 1)

    # ── Architecture zone base ────────────────────────────────────────────────
    for y in range(sky_bottom, arch_bottom):
        t = (y - sky_bottom) / float(arch_bottom - sky_bottom - 1)
        r = 0.68 - 0.08 * t + rng.uniform(-0.02, 0.02)
        g = 0.62 - 0.08 * t + rng.uniform(-0.015, 0.015)
        b = 0.42 - 0.06 * t + rng.uniform(-0.010, 0.010)
        ref[y, :, 0] = np.clip(r, 0, 1)
        ref[y, :, 1] = np.clip(g, 0, 1)
        ref[y, :, 2] = np.clip(b, 0, 1)

    # ── Building blocks ───────────────────────────────────────────────────────
    arch_rng = np.random.default_rng(SEED + 10)

    def paint_row(y_top, y_bot, buildings):
        for (x_frac, w_frac, btype) in buildings:
            x_s = int(x_frac * W)
            x_e = min(W, int((x_frac + w_frac) * W))
            yt  = y_top + arch_rng.integers(0, 10)
            yb  = y_bot - arch_rng.integers(0, 8)
            if btype == 'lit':
                rv, gv, bv = 0.84, 0.77, 0.56
            elif btype == 'shadow':
                rv, gv, bv = 0.36, 0.32, 0.22
            else:
                rv, gv, bv = 0.60, 0.54, 0.38
            for y in range(max(0, yt), min(H, yb)):
                n = arch_rng.uniform(-0.018, 0.018)
                ref[y, x_s:x_e, 0] = np.clip(rv + n, 0, 1)
                ref[y, x_s:x_e, 1] = np.clip(gv + n * 0.8, 0, 1)
                ref[y, x_s:x_e, 2] = np.clip(bv + n * 0.6, 0, 1)

    arch_h  = arch_bottom - sky_bottom
    paint_row(
        sky_bottom + int(arch_h * 0.00),
        sky_bottom + int(arch_h * 0.28),
        [(0.00, 0.10, 'lit'), (0.10, 0.08, 'shadow'), (0.18, 0.12, 'lit'),
         (0.30, 0.09, 'mid'), (0.39, 0.11, 'lit'),    (0.50, 0.08, 'shadow'),
         (0.58, 0.12, 'lit'), (0.70, 0.09, 'mid'),    (0.79, 0.11, 'lit'),
         (0.90, 0.10, 'shadow')],
    )
    paint_row(
        sky_bottom + int(arch_h * 0.24),
        sky_bottom + int(arch_h * 0.58),
        [(0.00, 0.11, 'shadow'), (0.11, 0.13, 'lit'),    (0.24, 0.09, 'shadow'),
         (0.33, 0.14, 'lit'),    (0.47, 0.10, 'mid'),    (0.57, 0.13, 'lit'),
         (0.70, 0.09, 'shadow'), (0.79, 0.12, 'lit'),    (0.91, 0.09, 'shadow')],
    )
    paint_row(
        sky_bottom + int(arch_h * 0.54),
        arch_bottom,
        [(0.00, 0.16, 'shadow'), (0.16, 0.18, 'lit'),    (0.34, 0.12, 'mid'),
         (0.46, 0.16, 'lit'),    (0.62, 0.14, 'shadow'), (0.76, 0.14, 'lit'),
         (0.90, 0.10, 'mid')],
    )

    # ── Windows and doorways ──────────────────────────────────────────────────
    win_rng = np.random.default_rng(SEED + 20)
    for _ in range(140):
        y_c = win_rng.integers(sky_bottom + 5, arch_bottom - 5)
        x_c = win_rng.integers(5, W - 5)
        wh  = win_rng.integers(6, 18)
        ww  = win_rng.integers(5, 14)
        y_s = max(sky_bottom, y_c - wh // 2)
        y_e = min(arch_bottom, y_c + wh // 2)
        x_s = max(0, x_c - ww // 2)
        x_e = min(W, x_c + ww // 2)
        ref[y_s:y_e, x_s:x_e, 0] = np.clip(0.10 + win_rng.uniform(-0.03, 0.03), 0, 1)
        ref[y_s:y_e, x_s:x_e, 1] = np.clip(0.12 + win_rng.uniform(-0.03, 0.03), 0, 1)
        ref[y_s:y_e, x_s:x_e, 2] = np.clip(0.20 + win_rng.uniform(-0.03, 0.03), 0, 1)

    # ── Harbor water ──────────────────────────────────────────────────────────
    for y in range(water_top, H):
        t = (y - water_top) / float(H - water_top)
        r = 0.28 - 0.06 * t + rng.uniform(-0.012, 0.012)
        g = 0.34 - 0.06 * t + rng.uniform(-0.012, 0.012)
        b = 0.48 - 0.06 * t + rng.uniform(-0.008, 0.008)
        ref[y, :, 0] = np.clip(r, 0, 1)
        ref[y, :, 1] = np.clip(g, 0, 1)
        ref[y, :, 2] = np.clip(b, 0, 1)

    # Reflected architecture in water
    reflect_h = int((H - water_top) * 0.40)
    for y in range(water_top, water_top + reflect_h):
        src_y = arch_bottom - (y - water_top) - 1
        src_y = max(0, min(H - 1, src_y))
        t_b   = (y - water_top) / float(reflect_h + 1)
        ref[y, :, 0] = ref[y, :, 0] * 0.68 + ref[src_y, :, 0] * 0.32 * (1 - t_b * 0.5)
        ref[y, :, 1] = ref[y, :, 1] * 0.68 + ref[src_y, :, 1] * 0.32 * (1 - t_b * 0.5)
        ref[y, :, 2] = ref[y, :, 2] * 0.68 + ref[src_y, :, 2] * 0.32 * (1 - t_b * 0.5)

    # ── Fishing boats ─────────────────────────────────────────────────────────
    boat_rng = np.random.default_rng(SEED + 30)
    boats = [
        (0.22, 0.80, 0.08, 12, True),
        (0.52, 0.82, 0.10, 14, True),
        (0.78, 0.79, 0.07, 11, True),
    ]
    for (cx_f, yw_f, bw_f, bh, has_mast) in boats:
        cx = int(cx_f * W)
        yw = int(yw_f * H)
        hw = int(bw_f * W)
        for dy in range(bh):
            t_hull = dy / float(bh)
            half_w = int(hw * 0.5 * (1 - t_hull * 0.4))
            yr = yw + dy
            if yr >= H:
                continue
            xs = max(0, cx - half_w)
            xe = min(W, cx + half_w)
            ref[yr, xs:xe, 0] = np.clip(0.14 + boat_rng.uniform(-0.02, 0.02), 0, 1)
            ref[yr, xs:xe, 1] = np.clip(0.12 + boat_rng.uniform(-0.02, 0.02), 0, 1)
            ref[yr, xs:xe, 2] = np.clip(0.10 + boat_rng.uniform(-0.02, 0.02), 0, 1)
        if has_mast:
            mast_h = boat_rng.integers(40, 65)
            mx = cx + boat_rng.integers(-4, 4)
            for dy in range(-mast_h, 0):
                ym = yw + dy
                for dx in range(2):
                    xi = mx + dx
                    if 0 <= ym < H and 0 <= xi < W:
                        ref[ym, xi] = [0.16, 0.14, 0.12]

    return (np.clip(ref, 0, 1) * 255).astype(np.uint8)


def main():
    print("Session 275 -- Pablo Picasso Analytic Cubism -- Cadaques Harbor at Dawn")
    print(f"Canvas: {W} x {H}")
    print()

    print("Building procedural reference...")
    ref = build_reference()
    print(f"  Reference: {ref.shape}, dtype={ref.dtype}, range=[{ref.min()},{ref.max()}]")

    print("Initialising Painter...")
    p = Painter(W, H, seed=SEED)

    print("Laying ground...")
    p.tone_ground((0.42, 0.35, 0.18), texture_strength=0.022)

    print("Underpainting (x2)...")
    p.underpainting(ref, stroke_size=52, n_strokes=240)
    p.underpainting(ref, stroke_size=36, n_strokes=260)

    print("Block-in (x2)...")
    p.block_in(ref, stroke_size=30, n_strokes=480)
    p.block_in(ref, stroke_size=20, n_strokes=500)

    print("Build form (x2)...")
    p.build_form(ref, stroke_size=12, n_strokes=520)
    p.build_form(ref, stroke_size=6,  n_strokes=430)

    print("Place lights...")
    p.place_lights(ref, stroke_size=4, n_strokes=300)

    print("Impasto ridge lighting pass (s275 improvement)...")
    p.paint_impasto_ridge_lighting_pass(
        light_angle_deg=225.0,
        ridge_strength=0.58,
        highlight_lift=0.13,
        shadow_drop=0.09,
        gradient_sigma=1.3,
        min_gradient=0.045,
        ridge_warmth=0.03,
        opacity=0.58,
    )

    print("Picasso Cubist fragmentation pass (186th mode)...")
    p.picasso_cubist_fragmentation_pass(
        n_facets=300,
        displacement_sigma=30.0,
        displacement_scale=150.0,
        tonal_variance=0.060,
        palette_shift=0.20,
        edge_darkness=0.48,
        edge_width=2,
        noise_seed=SEED,
        opacity=0.76,
    )

    print("Aerial perspective pass...")
    p.paint_aerial_perspective_pass()

    print(f"Saving to {OUT}...")
    p.save(OUT)
    print("Done.")


if __name__ == "__main__":
    main()
