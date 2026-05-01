"""
paint_s271_nordic_fjord_dusk.py -- Session 271

"Trolljegeren's Pond -- Twilight Over a Norse Peat Bog" -- in the manner of Theodor Kittelsen
(Norwegian Romantic Realism / Folk Illustration)

Image Description
-----------------
Subject & Composition
    A small, near-circular peat bog pond set in open moorland at deep twilight.
    The canvas is wide landscape (1440 × 1040), framing a low horizon with the
    pond occupying the lower 40% of the image as a perfect still mirror. The sky
    fills the upper 60%, transitioning from a narrow band of amber-gold just above
    the silhouetted treeline to cool steel blue in the mid-sky to deep prussian
    blue-violet at the zenith. No sun is visible -- only the afterglow of a recently
    set sun remains. A single bright evening star emerges in the upper-right sky.
    The composition is rigorously horizontal: the treeline and pond edge both run
    near-parallel to the canvas edge, emphasizing the vast flatness of Norwegian
    moorland.

The Subject
    The pond is the central subject: a perfectly still body of dark water that
    mirrors the twilight sky above it. The reflection inverts the sky gradient --
    amber at the water's far edge (horizon reflection), steel blue in the pond
    center, deep violet near the near shore. The surface is absolutely still;
    there is not a ripple. A thin, wispy band of mist rises from the warm water
    into cooler air, hovering just above the pond surface, pale silver-white
    against the dark treeline beyond.

    Flanking the pond on both sides: silhouetted birch trees with pale trunks
    and dark branching crowns, their reflections also mirrored in the water
    below. The silhouettes are sharply cut against the pale sky -- the defining
    Kittelsen silhouette opposition. To the far left: a denser cluster of spruce
    trees, their conical profiles darkly massed. To the far right: a lone dead
    birch with bare upward-reaching branches. On the near shore: low heather and
    sedge tufts, dark and texturally rich, with the quality of cold moorland
    vegetation pressing toward the viewer.

    The emotional state of the scene is one of deep, listening stillness --
    the particular Norwegian quality of being utterly alone in the wilderness
    at the edge of night, when the daylight is fully gone but darkness has not
    yet taken complete hold. There is the latent sense that the landscape is
    aware of you. Kittelsen placed his trolls and spirits into exactly these
    moments.

The Environment
    Sky: amber-gold at the very horizon (R=0.85, G=0.68, B=0.38), transitioning
    upward through warm peach to cool steel blue (R=0.40, G=0.48, B=0.65) and
    finally to deep prussian blue-violet (R=0.08, G=0.10, B=0.28) at the zenith.
    The gradient is smooth and continuous, interrupted only by the dark treeline
    silhouette at the horizon.

    Foreground: dark peat-umber heather and sedge (nearly black, R=0.12, G=0.10,
    B=0.08), textured, rough, pressing close. The heather tufts are small rounded
    forms with fine branching detail.

    Background: dark spruce and birch silhouettes, near-black, sharply cut against
    the pale sky. The treeline is irregular -- varying heights, gap between clusters.

    Water: the pond mirrors sky but slightly darkened and slightly desaturated --
    still water absorbs more light than it reflects at steep angles. The mist
    band above the water is pale silver-grey (R=0.72, G=0.74, B=0.76).

    One bright star: a single point of near-white light in the upper-right sky,
    surrounded by a faint radial halo.

Technique & Palette
    Theodor Kittelsen Norwegian Romantic Realism mode -- session 271, 182nd distinct mode.

    Pipeline:
    1. Procedural reference: sky gradient, treeline silhouettes, mirrored pond,
       mist band, foreground heather.
    2. tone_ground: dark peat-umber (0.16, 0.14, 0.12).
    3. underpainting x2: establish large tonal masses -- dark earth, pale sky
       gradient, dark treeline, mirrored water.
    4. block_in x2: build atmospheric sky gradient, silhouetted tree masses,
       pond surface, mist band.
    5. build_form x2: refine birch trunk detail, heather texture, pond surface
       reflections, mist gradients.
    6. place_lights: evening star highlight, pale birch bark highlights,
       amber horizon glow.
    7. paint_reflected_light_pass (s271 improvement): inject ambient blue-violet
       sky bounce into shadow zones; warm ground bounce into near foreground shadows.
    8. kittelsen_nordic_mist_pass (271, 182nd mode): content-adaptive far-zone
       detection, atmospheric haze tint, silhouette edge hardening, dark blue-violet
       underlayer.
    9. paint_depth_atmosphere_pass: deepen the atmospheric perspective in far zones.
    10. paint_lost_found_edges_pass: soften mist zone edges, maintain hard silhouettes.

    Full palette:
    prussian-blue-violet (0.06/0.08/0.22) -- amber-gold (0.85/0.70/0.40) --
    pale-silver-grey (0.72/0.74/0.78) -- dark-umber (0.12/0.10/0.08) --
    cool-blue-grey (0.45/0.52/0.68) -- near-white (0.88/0.88/0.86) --
    forest-black (0.08/0.12/0.10) -- warm-rose-amber (0.80/0.55/0.35)

Mood & Intent
    The image intends NORDIC STILLNESS and THE WEIGHT OF DUSK. Kittelsen painted
    the Norwegian landscape at the moment when the rational world recedes and the
    folk world -- trolls, nisse, spirits of the bog and forest -- becomes plausible.
    This is that moment. The still water is too perfect, the silence too complete.
    The viewer is invited to pause at the edge of the pond and listen. The single
    evening star names the moment precisely: day has ended; night has not yet
    arrived; anything might walk out of the dark treeline.
"""

import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

from stroke_engine import Painter

# ── Canvas dimensions ────────────────────────────────────────────────────────
W, H = 1440, 1040
SEED = 271
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s271_nordic_fjord_dusk.png")


def build_reference(w: int, h: int) -> np.ndarray:
    """Build a procedural reference for the Norse peat bog at twilight.

    Returns uint8 (H, W, 3) -- pass directly to Painter methods.
    Establishes:
      - Sky: amber-gold horizon → steel blue → prussian violet zenith
      - Treeline silhouettes: dark shapes against pale sky
      - Pond: mirrored sky gradient in lower canvas
      - Mist band above pond surface
      - Foreground heather texture
      - Evening star
    """
    from scipy.ndimage import gaussian_filter

    arr = np.zeros((h, w, 3), dtype=np.float32)

    ys, xs = np.mgrid[0:h, 0:w]
    y_frac = ys.astype(np.float32) / float(h - 1)   # 0=top, 1=bottom
    x_frac = xs.astype(np.float32) / float(w - 1)

    # ── Sky zone: upper 58% of canvas ────────────────────────────────────────
    sky_horizon  = 0.58   # y_frac where horizon sits
    horizon_band = 0.06   # relative thickness of amber band above horizon

    # Sky y-fraction within sky zone: 0 = horizon, 1 = zenith
    sky_y = np.clip((sky_horizon - y_frac) / (sky_horizon + 1e-6), 0.0, 1.0).astype(np.float32)

    # Colour stops (from horizon to zenith):
    # [0.00] amber-gold    (0.85, 0.68, 0.38)
    # [0.18] warm peach    (0.68, 0.60, 0.55)
    # [0.40] steel blue    (0.40, 0.48, 0.65)
    # [1.00] prussian violet (0.08, 0.10, 0.28)

    def sky_color(t):
        t = float(np.clip(t, 0.0, 1.0))
        if t < 0.18:
            s = t / 0.18
            r = 0.85 + (0.68 - 0.85) * s
            g = 0.68 + (0.60 - 0.68) * s
            b = 0.38 + (0.55 - 0.38) * s
        elif t < 0.40:
            s = (t - 0.18) / (0.40 - 0.18)
            r = 0.68 + (0.40 - 0.68) * s
            g = 0.60 + (0.48 - 0.60) * s
            b = 0.55 + (0.65 - 0.55) * s
        else:
            s = (t - 0.40) / (1.00 - 0.40)
            r = 0.40 + (0.08 - 0.40) * s
            g = 0.48 + (0.10 - 0.48) * s
            b = 0.65 + (0.28 - 0.65) * s
        return np.clip(r, 0, 1), np.clip(g, 0, 1), np.clip(b, 0, 1)

    # Vectorized sky colour
    sky_r = np.zeros((h, w), dtype=np.float32)
    sky_g = np.zeros((h, w), dtype=np.float32)
    sky_b = np.zeros((h, w), dtype=np.float32)

    for i in range(h):
        t_row = float(sky_y[i, 0]) if i < h else 1.0
        sr, sg, sb = sky_color(t_row)
        sky_r[i, :] = sr
        sky_g[i, :] = sg
        sky_b[i, :] = sb

    # Set sky pixels
    sky_mask = (y_frac <= sky_horizon).astype(np.float32)
    arr[:, :, 0] = sky_r * sky_mask
    arr[:, :, 1] = sky_g * sky_mask
    arr[:, :, 2] = sky_b * sky_mask

    # ── Evening star (upper-right) ────────────────────────────────────────────
    star_y = int(h * 0.12)
    star_x = int(w * 0.78)
    star_sigma = 1.2
    star_halo_sigma = 4.0
    star_field = np.zeros((h, w), dtype=np.float32)
    if 0 <= star_y < h and 0 <= star_x < w:
        star_field[star_y, star_x] = 1.0
    star_core = gaussian_filter(star_field, sigma=star_sigma).astype(np.float32)
    star_halo = gaussian_filter(star_field, sigma=star_halo_sigma).astype(np.float32)
    star_composite = np.clip(star_core * 60.0 + star_halo * 4.0, 0.0, 1.0).astype(np.float32)
    # Apply only in sky zone
    star_r = star_composite * sky_mask
    arr[:, :, 0] = np.clip(arr[:, :, 0] + star_r * 0.96, 0.0, 1.0)
    arr[:, :, 1] = np.clip(arr[:, :, 1] + star_r * 0.96, 0.0, 1.0)
    arr[:, :, 2] = np.clip(arr[:, :, 2] + star_r * 1.00, 0.0, 1.0)

    # ── Treeline silhouettes ──────────────────────────────────────────────────
    # Silhouettes sit near the horizon: y_frac around sky_horizon ± 0.08
    # Built as procedural height profiles

    rng = np.random.default_rng(seed=271)
    treeline = np.zeros(w, dtype=np.float32)   # height above horizon (in y_frac units)

    # Spruce cluster left (x: 0.0 to 0.28)
    for xi in range(0, int(w * 0.28)):
        # Conic spruce profile -- jagged, irregular
        tree_phase = xi / float(w * 0.28)
        base_ht = 0.048 + 0.018 * np.sin(xi * 0.42) + rng.uniform(-0.006, 0.006)
        treeline[xi] = max(treeline[xi], base_ht)

    # Birch cluster left (x: 0.15 to 0.42) -- taller, narrower
    for xi in range(int(w * 0.15), int(w * 0.42)):
        jag = 0.035 + 0.022 * abs(np.sin(xi * 0.28)) + rng.uniform(0, 0.012)
        treeline[xi] = max(treeline[xi], jag)

    # Gap in center (x: 0.44 to 0.58) -- open sky
    for xi in range(int(w * 0.44), int(w * 0.58)):
        treeline[xi] = max(treeline[xi], 0.008 + rng.uniform(0, 0.006))

    # Birch cluster right (x: 0.60 to 0.80)
    for xi in range(int(w * 0.60), int(w * 0.80)):
        jag = 0.040 + 0.018 * abs(np.sin(xi * 0.35)) + rng.uniform(0, 0.010)
        treeline[xi] = max(treeline[xi], jag)

    # Lone dead birch far right (x: 0.86 to 0.94) -- thin, tall branches
    for xi in range(int(w * 0.86), int(w * 0.94)):
        ht = 0.060 * np.exp(-((xi / w - 0.90) ** 2) / (2 * 0.015 ** 2))
        treeline[xi] = max(treeline[xi], ht + rng.uniform(0, 0.008))

    # Smooth the treeline slightly
    treeline_smooth = gaussian_filter(treeline, sigma=1.5).astype(np.float32)

    # Paint treeline: pixels where y_frac > sky_horizon - treeline_smooth[x]
    # and y_frac <= sky_horizon + 0.04 (just below horizon)
    tree_top = sky_horizon - treeline_smooth  # top of tree at this x

    tree_color = np.array([0.09, 0.11, 0.09], dtype=np.float32)   # dark conifer green-black
    tree_mask_2d = np.zeros((h, w), dtype=np.float32)
    for xi in range(w):
        top_y = tree_top[xi]
        bot_y = sky_horizon + 0.005  # slightly below horizon
        col = np.clip((y_frac[:, xi] - top_y) / 0.003, 0.0, 1.0)
        below = np.clip((bot_y - y_frac[:, xi]) / 0.003, 0.0, 1.0)
        tree_mask_2d[:, xi] = col * below

    tree_mask_2d = np.clip(tree_mask_2d, 0.0, 1.0).astype(np.float32)
    tm = tree_mask_2d[:, :, np.newaxis]
    arr = arr * (1.0 - tm) + tree_color[np.newaxis, np.newaxis, :] * tm

    # ── Pond: lower 40% of canvas ─────────────────────────────────────────────
    pond_top = 0.60    # y_frac where pond begins
    pond_bot = 0.88    # y_frac where pond ends (near shore)

    # Pond is an elliptical shape, slightly wider than tall
    pond_cx = 0.50
    pond_cy = (pond_top + pond_bot) / 2.0
    pond_rx = 0.42    # half-width in x_frac
    pond_ry = (pond_bot - pond_top) / 2.0

    # Elliptical pond mask
    pond_dist = (((x_frac - pond_cx) / pond_rx) ** 2
                 + ((y_frac - pond_cy) / pond_ry) ** 2).astype(np.float32)
    pond_mask = np.clip(1.0 - (pond_dist - 0.80) / 0.20, 0.0, 1.0).astype(np.float32)

    # Mirror the sky gradient in the pond (flipped vertically)
    # Map pond y to reflected sky t: y_frac=pond_bot → t=0 (horizon), y_frac=pond_top → t=0.5
    pond_y_norm = np.clip((y_frac - pond_top) / (pond_bot - pond_top + 1e-6), 0.0, 1.0).astype(np.float32)
    pond_t = pond_y_norm * 0.50   # maps 0-1 to sky 0-0.5 (inverted reflection is horizon-first)

    pond_r = np.zeros((h, w), dtype=np.float32)
    pond_g = np.zeros((h, w), dtype=np.float32)
    pond_b = np.zeros((h, w), dtype=np.float32)

    for i in range(h):
        t_row = float(pond_t[i, 0])
        pr, pg, pb = sky_color(t_row)
        # Darken and desaturate slightly for water reflection
        lum_r = 0.299 * pr + 0.587 * pg + 0.114 * pb
        pr = lum_r + (pr - lum_r) * 0.75
        pg = lum_g = lum_r + (pg - lum_r) * 0.75
        pb = lum_b = lum_r + (pb - lum_r) * 0.75
        pr = np.clip(pr * 0.78, 0, 1)
        pg = np.clip(pg * 0.78, 0, 1)
        pb = np.clip(pb * 0.78, 0, 1)
        pond_r[i, :] = pr
        pond_g[i, :] = pg
        pond_b[i, :] = pb

    pm = pond_mask[:, :, np.newaxis]
    pond_rgb = np.stack([pond_r, pond_g, pond_b], axis=-1)
    arr = arr * (1.0 - pm) + pond_rgb * pm

    # ── Mist band above pond surface ──────────────────────────────────────────
    mist_center_y = pond_top - 0.015   # just above pond top
    mist_sigma_y = 0.018
    mist_strength = 0.32

    mist_row = np.exp(-((y_frac - mist_center_y) ** 2) / (2 * mist_sigma_y ** 2)).astype(np.float32)
    # Mist only where there is pond below (x-wise within pond width)
    mist_x_mask = np.clip(1.0 - ((x_frac - pond_cx) / (pond_rx * 1.1)) ** 8, 0.0, 1.0).astype(np.float32)
    mist_map = (mist_row * mist_x_mask * mist_strength).astype(np.float32)

    mist_color = np.array([0.72, 0.74, 0.76], dtype=np.float32)
    mist_m = mist_map[:, :, np.newaxis]
    arr = arr * (1.0 - mist_m) + mist_color[np.newaxis, np.newaxis, :] * mist_m

    # ── Foreground: dark heather/sedge strip ──────────────────────────────────
    fg_top = 0.86     # y_frac where foreground begins
    fg_alpha = np.clip((y_frac - fg_top) / (1.0 - fg_top + 1e-6), 0.0, 1.0).astype(np.float32)

    # Add procedural heather texture: fine noise bumps
    rng2 = np.random.default_rng(seed=2712)
    heather_noise = rng2.uniform(0.0, 1.0, (h, w)).astype(np.float32)
    heather_noise_smooth = gaussian_filter(heather_noise, sigma=2.5).astype(np.float32)
    heather_noise_fine   = gaussian_filter(heather_noise, sigma=0.8).astype(np.float32)
    # Dark base with slight variance for texture
    heather_r = np.clip(0.12 + heather_noise_smooth * 0.05 + heather_noise_fine * 0.02, 0.0, 1.0)
    heather_g = np.clip(0.10 + heather_noise_smooth * 0.04 + heather_noise_fine * 0.02, 0.0, 1.0)
    heather_b = np.clip(0.08 + heather_noise_smooth * 0.05 + heather_noise_fine * 0.02, 0.0, 1.0)

    fg_rgb = np.stack([heather_r, heather_g, heather_b], axis=-1).astype(np.float32)
    fg_m = fg_alpha[:, :, np.newaxis]
    arr = arr * (1.0 - fg_m) + fg_rgb * fg_m

    # ── Grassy/earth strip between pond and foreground ────────────────────────
    earth_y_center = (pond_bot + fg_top) / 2.0
    earth_sigma = 0.025
    earth_mask = np.exp(-((y_frac - earth_y_center) ** 2) / (2 * earth_sigma ** 2)).astype(np.float32)
    earth_mask = earth_mask * 0.6
    earth_color = np.array([0.14, 0.12, 0.10], dtype=np.float32)
    earth_m = earth_mask[:, :, np.newaxis]
    arr = arr * (1.0 - earth_m) + earth_color[np.newaxis, np.newaxis, :] * earth_m

    # ── Treeline reflection in pond ───────────────────────────────────────────
    # Mirror tree silhouette into the pond top
    tree_refl_mask = np.zeros((h, w), dtype=np.float32)
    for xi in range(w):
        top_y = tree_top[xi]
        ht = sky_horizon - top_y
        # Reflected tree: from pond_top to pond_top + ht (mirrored)
        refl_top = pond_top
        refl_bot = pond_top + ht * 0.8
        col = np.clip((y_frac[:, xi] - refl_top) / 0.003, 0.0, 1.0)
        below = np.clip((refl_bot - y_frac[:, xi]) / 0.003, 0.0, 1.0)
        tree_refl_mask[:, xi] = col * below * pond_mask[:, xi]

    tree_refl_mask = np.clip(tree_refl_mask, 0.0, 1.0).astype(np.float32)
    # Reflections are slightly lighter than the original (water reflection diffusion)
    tree_refl_color = np.array([0.11, 0.13, 0.14], dtype=np.float32)
    trm = tree_refl_mask[:, :, np.newaxis]
    arr = arr * (1.0 - trm) + tree_refl_color[np.newaxis, np.newaxis, :] * trm

    # ── Smooth the whole reference lightly ───────────────────────────────────
    arr[:, :, 0] = gaussian_filter(arr[:, :, 0], sigma=1.0).astype(np.float32)
    arr[:, :, 1] = gaussian_filter(arr[:, :, 1], sigma=1.0).astype(np.float32)
    arr[:, :, 2] = gaussian_filter(arr[:, :, 2], sigma=1.0).astype(np.float32)

    # ── Convert to uint8 ─────────────────────────────────────────────────────
    return (np.clip(arr, 0.0, 1.0) * 255).astype(np.uint8)


def main():
    print(f"Session 271 -- Trolljegeren's Pond -- Twilight Over a Norse Peat Bog")
    print(f"Theodor Kittelsen Norwegian Romantic Realism -- 182nd distinct mode")
    print(f"Canvas: {W} x {H}")
    print()

    print("Building procedural reference...")
    ref = build_reference(W, H)
    print(f"  Reference shape: {ref.shape}, dtype: {ref.dtype}")

    print("Initialising Painter...")
    p = Painter(W, H, seed=SEED)

    # ── 1. Toned ground: dark peat-umber ─────────────────────────────────────
    print("  tone_ground (dark peat-umber 0.16/0.14/0.12)...")
    p.tone_ground((0.16, 0.14, 0.12), texture_strength=0.025)

    # ── 2. Underpainting x2 ──────────────────────────────────────────────────
    print("  underpainting pass 1 (large, stroke=54)...")
    p.underpainting(ref, stroke_size=54, n_strokes=230)
    print("  underpainting pass 2 (medium, stroke=34)...")
    p.underpainting(ref, stroke_size=34, n_strokes=260)

    # ── 3. Block in x2 ───────────────────────────────────────────────────────
    print("  block_in pass 1 (broad, stroke=34)...")
    p.block_in(ref, stroke_size=34, n_strokes=460)
    print("  block_in pass 2 (medium, stroke=20)...")
    p.block_in(ref, stroke_size=20, n_strokes=510)

    # ── 4. Build form x2 ─────────────────────────────────────────────────────
    print("  build_form pass 1 (medium, stroke=12)...")
    p.build_form(ref, stroke_size=12, n_strokes=490)
    print("  build_form pass 2 (fine, stroke=6)...")
    p.build_form(ref, stroke_size=6, n_strokes=420)

    # ── 5. Place lights ───────────────────────────────────────────────────────
    print("  place_lights (stroke=4)...")
    p.place_lights(ref, stroke_size=4, n_strokes=280)

    # ── 6. Reflected Light pass (s271 improvement) ────────────────────────────
    print("  paint_reflected_light_pass (s271 improvement)...")
    p.paint_reflected_light_pass(
        shadow_threshold=0.28,
        light_threshold=0.58,
        search_radius=45.0,
        reflect_strength=0.16,
        sky_cool=0.07,
        ground_warm=0.04,
        opacity=0.65,
    )

    # ── 7. Kittelsen Nordic Mist pass (182nd mode) ────────────────────────────
    print("  kittelsen_nordic_mist_pass (session 271, 182nd mode)...")
    p.kittelsen_nordic_mist_pass(
        variance_sigma=9.0,
        far_lum_low=0.36,
        far_lum_high=0.84,
        haze_r=0.58,
        haze_g=0.63,
        haze_b=0.76,
        haze_strength=0.28,
        silhouette_contrast=0.24,
        dark_violet_r=0.07,
        dark_violet_g=0.09,
        dark_violet_b=0.26,
        dark_strength=0.30,
        dark_threshold=0.20,
        opacity=0.76,
    )

    # ── 8. Depth atmosphere: deepen aerial perspective ────────────────────────
    print("  paint_depth_atmosphere_pass...")
    p.paint_depth_atmosphere_pass(
        haze_color=(0.55, 0.60, 0.74),
        depth_sigma=35.0,
        max_haze=0.24,
        vertical_weight=0.70,
        contrast_weight=0.30,
        opacity=0.55,
    )

    # ── 9. Lost and found edges: preserve silhouette, soften mist ────────────
    print("  paint_lost_found_edges_pass...")
    p.paint_lost_found_edges_pass()

    # ── 10. Chromatic vibration: subtle colour variation in sky ───────────────
    print("  paint_chromatic_vibration_pass (subtle sky variation)...")
    p.paint_chromatic_vibration_pass(
        vibration_sigma=10.0,
        vibration_strength=0.10,
        saturation_boost=0.06,
        opacity=0.40,
    )

    # ── 11. Save ──────────────────────────────────────────────────────────────
    print(f"  Saving to {OUT}...")
    p.save(OUT)
    print(f"Done. Output: {OUT}")
    return OUT


if __name__ == "__main__":
    main()
