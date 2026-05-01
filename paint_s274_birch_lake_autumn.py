"""
paint_s274_birch_lake_autumn.py -- Session 274

"Golden Birch Lake — Autumn Dusk"
in the manner of Isaak Levitan (Russian Lyrical Impressionism)

Image Description
-----------------
Subject & Composition
    A wide Russian landscape at dusk in the peak of autumn — canvas landscape
    format (1440 x 1040). The composition is organized in four horizontal
    bands: an overcast but luminous sky (upper 40%), a stand of golden birch
    trees with their reflections in still water (middle-right, 35%), the still
    lake surface itself (lower-left, 30%), and a dark fir-pine treeline on the
    far bank (a narrow band at 65–70% from top). The viewpoint is slightly
    elevated, looking slightly downward across the still water toward the birch
    grove. The golden birch mass is weighted to the right half of the canvas;
    the lake occupies the lower-left quarter. A narrow strip of autumn grass
    and soil runs along the near bank at the bottom edge.

The Subject
    No human or animal subject. The primary subject is the GOLDEN BIRCH GROVE:
    fifteen to twenty birch trees of varying heights, their slender white trunks
    marked with dark horizontal lenticels, their canopies full of autumn gold —
    deep ochre, amber, and warm yellow leaves at peak color. Several tallest
    birches rise above the treeline horizon, their upper crowns silhouetted
    against the pale warm sky. The trees are not regimented but natural — some
    leaning slightly, some close together, some apart. The trunks catch a last
    warm sidelight from the low sun to the right, creating a warm cream
    highlight along their right edges.

    On the left and far bank: a darker stand of conifer trees (fir and pine),
    nearly black-green, providing deep contrast against the golden birches and
    serving as a visual anchor for the left-hand weight of the composition.

    The emotional state of the scene is deeply melancholic and tender: the peak
    of golden autumn, the last day of warmth before the Russian winter closes in.
    The gold is intense, almost aching — beauty at maximum intensity, its very
    completeness a premonition of loss. Levitan painted this season repeatedly
    because it most completely expressed his temperament: joy and grief
    indistinguishable.

The Environment
    SKY (upper 40%): Overcast but luminous — not dark stormy grey but a
    pearlescent warm grey-buff, with diffuse light that seems to come from
    everywhere and nowhere. The sky is warmest near the horizon (right side,
    where a faint warm glow suggests the low autumn sun behind the cloud layer)
    and cools toward the zenith. The horizon on the right carries a narrow band
    of warm amber-ivory, the last direct light.

    BIRCH GROVE (35%, center-right): The golden birch canopy is the dominant
    warm mass of the image. The leaves are at peak autumn: dense ochre-gold
    with some amber-orange passages and occasional pale yellow. The canopy has
    depth, with trees further back reading slightly cooler and more atmospheric.
    Between the trunks, glimpses of the far bank and sky are visible as cool-grey
    vertical slots. The ground beneath the birches is covered with fallen leaves:
    a warm ochre-gold carpet that extends to the water's edge.

    FAR BANK — DARK CONIFERS (narrow band, 65–70%): A treeline of dark fir
    trees stretches across the canvas. Their near-black forms provide the darkest
    value in the scene and create a strong horizontal anchoring line.

    LAKE (lower 30%, primarily left): The still water surface mirrors and
    slightly darkens the scene above. Reflection shows: sky (warm grey), the
    dark conifer band, and the golden birch foliage. Very gentle horizontal
    wavering — not ripples, but the subtle distortion of truly still water.

    NEAR BANK (lower 5%): A strip of autumn grass and dark soil along the
    bottom edge, with accumulated fallen birch leaves in warm ochre-gold.

Technique & Palette
    Isaak Levitan Russian Lyrical Impressionism mode — session 274, 185th distinct mode.

    Pipeline:
    1. Procedural reference: sky gradient (warm horizon to cool overcast zenith),
       golden birch grove (right), dark conifer band, still lake reflection (left).
    2. tone_ground: warm buff-ochre (0.58, 0.52, 0.38) — toned linen ground.
    3. underpainting x2: establish tonal architecture.
    4. block_in x2: build sky, birch golden canopy, dark treeline, water surface.
    5. build_form x2: develop birch trunk detail, leaf texture, water reflection.
    6. place_lights: warm highlights on birch trunks, horizon amber glow.
    7. paint_edge_recession_pass (s274 improvement): soften peripheral edges
       while preserving crisp edges near the focal zone (birch trunks, key leaf
       passages).
    8. levitan_autumn_shimmer_pass (s274, 185th mode): diffuse golden warmth
       from birch foliage into adjacent sky and water zones.
    9. paint_aerial_perspective_pass: cool the far conifer band and upper sky.
    10. paint_chromatic_underdark_pass: deepen shadows under birches and in
        deep water with cool blue-violet.

    Full palette:
    golden-birch-ochre (0.82/0.68/0.28) -- amber-foliage (0.72/0.56/0.22) --
    warm-dark-umber (0.48/0.38/0.20) -- cool-water (0.24/0.34/0.45) --
    overcast-sky (0.72/0.70/0.60) -- warm-horizon (0.82/0.76/0.56) --
    pale-birch-trunk (0.78/0.74/0.62) -- dark-conifer (0.12/0.18/0.14) --
    autumn-grass (0.52/0.48/0.36) -- water-reflection (0.32/0.42/0.38)

Mood & Intent
    The painting intends LYRICAL MELANCHOLY AT THE PEAK OF AUTUMN. Levitan
    painted the Russian October not as documentation but as emotional equivalent:
    the intensity of the gold is inseparable from the knowledge that it will not
    last. The overcast sky presses gently downward; the still lake holds the gold
    like a mirror being slowly covered. The viewer should feel the peculiar Russian
    autumn emotion — what the writer Ivan Bunin called "the sadness of beautiful
    things" — not depression, but a profound tenderness for the transient. Quiet,
    intimate, and deeply felt: as if glimpsed through a window on a still October
    afternoon, before the first frost arrives.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stroke_engine import Painter

W, H = 1440, 1040
SEED = 274
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s274_birch_lake_autumn.png")


def build_reference() -> np.ndarray:
    """Build a procedural reference for the Levitan autumn birch lake scene.

    Returns uint8 (H, W, 3) in range 0-255.
    """
    rng = np.random.default_rng(SEED)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    sky_end_y      = int(H * 0.40)
    conifer_top_y  = int(H * 0.39)
    conifer_bot_y  = int(H * 0.52)
    water_start_y  = int(H * 0.50)
    bank_y         = int(H * 0.95)

    # ── Sky (upper 40%) ───────────────────────────────────────────────────────
    for y in range(sky_end_y + 5):
        t = y / float(sky_end_y)
        if t < 0.55:
            s = t / 0.55
            r = 0.62 + (0.72 - 0.62) * s
            g = 0.62 + (0.70 - 0.62) * s
            b = 0.66 + (0.62 - 0.66) * s
        else:
            s = (t - 0.55) / 0.45
            r = 0.72 + (0.86 - 0.72) * s
            g = 0.70 + (0.78 - 0.70) * s
            b = 0.62 + (0.52 - 0.62) * s

        xs = np.arange(W, dtype=np.float32) / float(W)
        warm_boost = xs * 0.06 * t
        noise = rng.uniform(-0.006, 0.006, W).astype(np.float32)
        ref[y, :, 0] = np.clip(r + warm_boost + noise, 0, 1)
        ref[y, :, 1] = np.clip(g + warm_boost * 0.7 + noise * 0.8, 0, 1)
        ref[y, :, 2] = np.clip(b - warm_boost * 0.3 + noise * 0.5, 0, 1)

    # ── Ground / mid area base (60%) ─────────────────────────────────────────
    for y in range(sky_end_y, H):
        t = (y - sky_end_y) / float(H - sky_end_y - 1)
        r = 0.30 + 0.15 * t + rng.uniform(-0.01, 0.01)
        g = 0.25 + 0.10 * t + rng.uniform(-0.01, 0.01)
        b = 0.14 + 0.05 * t + rng.uniform(-0.008, 0.008)
        ref[y, :, 0] = np.clip(r, 0, 1)
        ref[y, :, 1] = np.clip(g, 0, 1)
        ref[y, :, 2] = np.clip(b, 0, 1)

    # ── Water / lake surface (50%–95%) ───────────────────────────────────────
    for y in range(water_start_y, bank_y):
        t_water = (y - water_start_y) / float(bank_y - water_start_y)
        sky_reflect_y = int(sky_end_y * (1.0 - t_water * 0.5))
        sky_reflect_y = max(0, min(sky_end_y - 1, sky_reflect_y))

        for x in range(W):
            x_frac = x / float(W)
            in_lake = (x_frac < 0.62)
            if in_lake:
                sky_r = ref[sky_reflect_y, x, 0]
                sky_g = ref[sky_reflect_y, x, 1]
                sky_b = ref[sky_reflect_y, x, 2]
                water_r = sky_r * 0.78
                water_g = sky_g * 0.80
                water_b = sky_b * 0.88 + 0.04
                leaf_warm = max(0, t_water - 0.70) * 2.0
                water_r += leaf_warm * 0.12
                water_g += leaf_warm * 0.06
                wave = 0.004 * np.sin(x * 0.08 + y * 0.3)
                noise_w = rng.uniform(-0.005, 0.005)
                ref[y, x, 0] = float(np.clip(water_r + wave + noise_w, 0, 1))
                ref[y, x, 1] = float(np.clip(water_g + wave * 0.8 + noise_w, 0, 1))
                ref[y, x, 2] = float(np.clip(water_b + wave * 0.5 + noise_w, 0, 1))

    # ── Dark conifer treeline (far bank, 39%–55%) ─────────────────────────────
    conifer_rng = np.random.default_rng(SEED + 10)
    for y in range(conifer_top_y, conifer_bot_y):
        t = (y - conifer_top_y) / float(conifer_bot_y - conifer_top_y)
        for x in range(W):
            x_frac = x / float(W)
            conifer_strength = 0.85 + 0.15 * (1.0 - x_frac * 0.4)
            profile_val = (
                0.55
                + 0.2 * np.sin(x * 0.015 + 0.5)
                + 0.15 * np.sin(x * 0.04 + 1.2)
                + 0.1 * np.sin(x * 0.09 + 0.8)
            )
            in_conifer = (t < profile_val * conifer_strength)
            if in_conifer:
                depth = (1.0 - t / (profile_val * conifer_strength + 0.01))
                noise_c = conifer_rng.uniform(-0.015, 0.015)
                ref[y, x, 0] = float(np.clip(0.10 + depth * 0.06 + noise_c, 0, 1))
                ref[y, x, 1] = float(np.clip(0.16 + depth * 0.08 + noise_c, 0, 1))
                ref[y, x, 2] = float(np.clip(0.12 + depth * 0.05 + noise_c, 0, 1))

    # ── Golden birch grove (center-right, 39%–85%) ───────────────────────────
    birch_rng = np.random.default_rng(SEED + 20)

    trees = [
        (0.50, 0.06, 0.68, 4, 38),
        (0.58, 0.04, 0.68, 5, 44),
        (0.64, 0.08, 0.70, 4, 36),
        (0.70, 0.06, 0.70, 4, 40),
        (0.76, 0.10, 0.68, 4, 34),
        (0.52, 0.10, 0.72, 6, 50),
        (0.60, 0.07, 0.74, 7, 58),
        (0.67, 0.05, 0.76, 6, 52),
        (0.74, 0.08, 0.74, 6, 48),
        (0.80, 0.12, 0.72, 5, 42),
        (0.55, 0.08, 0.82, 8, 65),
        (0.63, 0.04, 0.84, 9, 72),
        (0.70, 0.06, 0.82, 8, 62),
        (0.77, 0.10, 0.80, 7, 58),
        (0.85, 0.14, 0.78, 7, 54),
        (0.92, 0.18, 0.76, 6, 46),
        (0.48, 0.15, 0.70, 5, 38),
        (0.88, 0.08, 0.74, 5, 40),
    ]

    for (cx_f, top_f, bot_f, trunk_w, canopy_r) in trees:
        cx    = int(cx_f * W)
        top_y = int(top_f * H)
        bot_y = int(bot_f * H)
        is_back = (cx_f < 0.55 and top_f < 0.12) or canopy_r < 44

        canopy_cy = top_y + int(canopy_r * 0.4)
        for dy in range(-canopy_r, canopy_r + 1):
            yy = canopy_cy + dy
            if yy < 0 or yy >= H:
                continue
            cr_x = int(canopy_r * np.sqrt(max(0, 1.0 - (dy / (canopy_r + 1)) ** 2)))
            for dx in range(-cr_x, cr_x + 1):
                xx = cx + dx
                if xx < 0 or xx >= W:
                    continue
                dist_norm = np.sqrt((dx / (canopy_r + 1)) ** 2 +
                                    (dy / (canopy_r * 0.8 + 1)) ** 2)
                if dist_norm > 1.0:
                    continue
                density = 1.0 - dist_norm ** 0.7
                if birch_rng.uniform() > density * 0.92:
                    continue
                hue_var = birch_rng.uniform(-0.06, 0.06)
                if is_back:
                    r = float(np.clip(0.70 + hue_var, 0, 1))
                    g = float(np.clip(0.58 + hue_var * 0.8, 0, 1))
                    b = float(np.clip(0.22 + hue_var * 0.3, 0, 1))
                else:
                    r = float(np.clip(0.82 + hue_var, 0, 1))
                    g = float(np.clip(0.68 + hue_var * 0.9, 0, 1))
                    b = float(np.clip(0.26 + hue_var * 0.2, 0, 1))
                if birch_rng.uniform() < 0.18:
                    r = float(np.clip(r + 0.08, 0, 1))
                    g = float(np.clip(g - 0.06, 0, 1))
                ref[yy, xx, 0] = r
                ref[yy, xx, 1] = g
                ref[yy, xx, 2] = b

        for y in range(max(top_y, conifer_bot_y - 5), bot_y):
            for dx in range(-trunk_w // 2, trunk_w // 2 + 1):
                xx = cx + dx
                if xx < 0 or xx >= W:
                    continue
                bark_var = birch_rng.uniform(-0.04, 0.04)
                is_lentic = (
                    (int(y * 0.35 + xx * 0.1) % 14 < 2) and
                    abs(dx) < trunk_w * 0.35
                )
                if is_lentic:
                    r = float(np.clip(0.22 + bark_var, 0, 1))
                    g = float(np.clip(0.20 + bark_var, 0, 1))
                    b = float(np.clip(0.18 + bark_var, 0, 1))
                else:
                    warm_side = max(0.0, dx / float(trunk_w + 1)) * 0.10
                    r = float(np.clip(0.76 + warm_side + bark_var, 0, 1))
                    g = float(np.clip(0.72 + warm_side * 0.7 + bark_var, 0, 1))
                    b = float(np.clip(0.60 + bark_var, 0, 1))
                ref[y, xx, 0] = r
                ref[y, xx, 1] = g
                ref[y, xx, 2] = b

        # Canopy reflection in water
        water_line_y = water_start_y
        for dy in range(-canopy_r, canopy_r + 1):
            src_y = canopy_cy + dy
            ref_y = water_line_y + (water_line_y - canopy_cy - dy)
            if ref_y < water_start_y or ref_y >= bank_y:
                continue
            if src_y < 0 or src_y >= H:
                continue
            cr_x = int(canopy_r * np.sqrt(max(0, 1.0 - (dy / (canopy_r + 1)) ** 2)))
            for dx in range(-cr_x, cr_x + 1):
                xx = cx + dx
                if xx < 0 or xx >= W or xx > int(W * 0.62) + 50:
                    continue
                if birch_rng.uniform() > 0.72:
                    continue
                orig_r = ref[src_y, min(xx, W-1), 0]
                orig_g = ref[src_y, min(xx, W-1), 1]
                orig_b = ref[src_y, min(xx, W-1), 2]
                ref[ref_y, xx, 0] = float(np.clip(orig_r * 0.76 + birch_rng.uniform(-0.02, 0.02), 0, 1))
                ref[ref_y, xx, 1] = float(np.clip(orig_g * 0.78 + birch_rng.uniform(-0.02, 0.02), 0, 1))
                ref[ref_y, xx, 2] = float(np.clip(orig_b * 0.84 + birch_rng.uniform(-0.01, 0.01), 0, 1))

    # ── Near bank — fallen leaves (bottom 5%) ────────────────────────────────
    leaf_rng = np.random.default_rng(SEED + 30)
    for y in range(bank_y, H):
        for x in range(W):
            t = (y - bank_y) / float(H - bank_y + 1)
            leaf_noise = leaf_rng.uniform(-0.04, 0.04)
            r = float(np.clip(0.52 + t * 0.12 + leaf_noise, 0, 1))
            g = float(np.clip(0.44 + t * 0.08 + leaf_noise * 0.8, 0, 1))
            b = float(np.clip(0.24 + t * 0.04 + leaf_noise * 0.5, 0, 1))
            if leaf_rng.uniform() < 0.22:
                r = float(np.clip(r + 0.20, 0, 1))
                g = float(np.clip(g + 0.12, 0, 1))
                b = float(np.clip(b - 0.04, 0, 1))
            ref[y, x, 0] = r
            ref[y, x, 1] = g
            ref[y, x, 2] = b

    return (np.clip(ref, 0, 1) * 255).astype(np.uint8)


def main():
    print(f"Session 274 -- Isaak Levitan Lyrical Impressionism -- Golden Birch Lake")
    print(f"Canvas: {W} x {H}")
    print()

    print("Building procedural reference...")
    ref = build_reference()
    print(f"  Reference: {ref.shape}, dtype={ref.dtype}, range=[{ref.min()},{ref.max()}]")

    print("Initialising Painter...")
    p = Painter(W, H, seed=SEED)

    print("Laying ground...")
    p.tone_ground((0.58, 0.52, 0.38), texture_strength=0.018)

    print("Underpainting (x2)...")
    p.underpainting(ref, stroke_size=54, n_strokes=220)
    p.underpainting(ref, stroke_size=38, n_strokes=250)

    print("Block-in (x2)...")
    p.block_in(ref, stroke_size=32, n_strokes=460)
    p.block_in(ref, stroke_size=20, n_strokes=490)

    print("Build form (x2)...")
    p.build_form(ref, stroke_size=12, n_strokes=510)
    p.build_form(ref, stroke_size=6,  n_strokes=400)

    print("Place lights...")
    p.place_lights(ref, stroke_size=4, n_strokes=280)

    print("Edge recession pass (s274 improvement)...")
    p.paint_edge_recession_pass(
        focal_cx=0.64,
        focal_cy=0.54,
        focal_radius=0.22,
        max_blur_sigma=2.8,
        edge_threshold=0.10,
        edge_sigma=1.4,
        opacity=0.68,
    )

    print("Levitan autumn shimmer pass (185th mode)...")
    p.levitan_autumn_shimmer_pass(
        warm_threshold=0.52,
        warmth_spread_min=0.14,
        warmth_sigma=44.0,
        tint_r_boost=0.055,
        tint_g_boost=0.028,
        tint_b_reduce=0.075,
        tint_max_opacity=0.52,
        luminance_floor=0.26,
        noise_seed=SEED,
    )

    print("Aerial perspective pass...")
    p.paint_aerial_perspective_pass()

    print("Chromatic underdark pass...")
    p.paint_chromatic_underdark_pass()

    print(f"Saving to {OUT}...")
    p.save(OUT)
    print("Done.")


if __name__ == "__main__":
    main()
