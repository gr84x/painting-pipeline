"""
paint_s266_birch_forest.py -- Session 266

"Birch Forest at Dusk, Lake Ruovesi" -- in the manner of Akseli Gallen-Kallela

Image Description
-----------------
Subject & Composition
    A Finnish birch forest stands in late October at the edge of Lake Ruovesi
    in Häme, Finland — the same lake at whose shores Gallen-Kallela built his
    studio Kalela in 1895. Six birch trunks of varying heights occupy the lower
    two-thirds of the canvas as vertical white sentinels, evenly distributed
    across the width. The viewer stands at the lake's edge, looking into the
    forest interior; the lake is a narrow band of dark water in the middle
    distance, visible between and beneath the birch crowns. Above the treeline:
    a Finnish dusk sky — deep cobalt at the zenith, graduating through raw
    ultramarine to a band of brilliant burnt orange above the horizon. The
    composition is landscape-oriented (wide), emphasising the horizontal
    spread of the Finnish forest landscape and the long, flat horizon typical
    of Finnish lake country.

The Figure
    No human subject. The six birch trunks are the compositional "figures" —
    tall, vertical, each one a distinct white form against the dark forest
    interior. The trees vary: the leftmost is the tallest and most massive,
    its base flaring slightly at the ground; two thinner saplings cluster near
    the left-centre; the central dominant trunk rises toward the top edge; two
    further birches frame the right half. Each trunk carries the characteristic
    dark oval node markings of Betula pendula — small horizontal black lenticels
    scattered at irregular intervals up the white bark. The emotional state of
    the subject is ancient and indifferent: these trees predate memory, have
    stood through a hundred Finnish winters, and will stand through a hundred
    more. Their stillness is total.

The Environment
    The Finnish forest interior at dusk: between the birch trunks lies a zone
    of dark shadow — the spruce and pine understorey that grows behind the
    birch fringe, almost impenetrable to the eye, painted as a flat deep forest-
    green / dark umber field. The forest floor is covered in leaf litter:
    fallen birch leaves in brilliant burnt ochre, golden yellow, and warm russet,
    gathered at the base of each trunk in a sweep of autumn colour. The narrow
    lake band gleams in the middle distance — deep blue-black, nearly opaque,
    with a single horizontal streak of reflected burnt orange from the dusk sky.
    The sky occupies the upper 30% of the canvas: from the zenith a deep saturated
    cobalt, warming through ultramarine toward a pure orange-crimson at the
    horizon line behind the birch crowns. The birch crowns themselves — a delicate
    tracery of fine branches against the sky — are suggested rather than detailed,
    their leaf mass already diminished to autumn sparseness. Temperature: below
    freezing tonight for the first time this year. The air is absolutely still.

Technique & Palette
    Akseli Gallen-Kallela Enamel Cloisonne mode — session 266, 177th distinct
    painting mode.

    Stage 1 CIRCULAR-HUE ZONE FLATTENING (flat_sigma=5.0, zone_blend=0.60):
    The circular Gaussian averaging of hue in sin/cos space resolves the subtle
    within-zone hue variation of the painted birch bark, autumn leaves, and sky
    gradient into unified colour areas — the birch trunks become a pure cream-
    white without hint of warm or cool bias; the sky cobalt becomes a single
    assertive hue; the forest dark resolves into a single deep green-black.
    This is the Japanese woodblock flatness that Gallen-Kallela absorbed in
    Paris and applied to the Finnish forest subject.

    Stage 2 BOLD CONTOUR DARKENING (contour_strength=0.75, contour_sigma=0.8):
    The Sobel magnitude computed from the flattened canvas detects the boundaries
    between the white birch trunks and the dark forest interior, between the sky
    zones and the treeline silhouette, between the lake band and the forest floor.
    Darkening at contour_strength=0.75 produces bold outlines in the tradition
    of Gallen-Kallela's "Symposium" and "Aino" paintings — not soft atmospheric
    edges but assertive, architectural partition lines.

    Stage 3 DECORATIVE PALETTE SATURATION PUNCH (sat_boost=0.25, sat_floor=0.12):
    The saturation amplification pushes the cobalt sky toward pure lapis, the
    burnt orange leaves toward the vivid crimson-ochre of Gallen-Kallela's
    decorative palette, and the forest green toward a deep jewel-tone. The result
    reads not as landscape painting but as landscape decoration — the view through
    a stained-glass window at a Finnish forest.

    Hue Zone Boundary improvement (s266): variance_sigma=3.5, boundary_dark=0.60,
    interior_chroma=0.20. Applied after the Gallen-Kallela mode to reinforce zone
    boundaries via circular hue variance detection — the hue-based boundary
    detection finds colour zone edges that luminance-based Sobel misses (e.g., the
    cobalt-to-orange sky transition, the white trunk against the green forest).

    Stage-by-stage pipeline:
    Ground: dark umber (0.22, 0.16, 0.09) — Finnish forest floor warmth
    Underpainting: birch trunk geometry, sky-treeline boundary, lake band
    Block-in (broad): sky cobalt mass, forest dark mass, birch trunks, lake
    Block-in (medium): sky gradient zones, leaf litter colour, trunk nodes
    Build form (medium): trunk form, forest depth, leaf texture
    Build form (fine): trunk node detail, leaf edge, sky horizon gradient
    Place lights: sky horizon glow, lake reflection streak, leaf highlights
    Hue Zone Boundary (s266): circular hue variance — zone interior chroma lift
    Gallen-Kallela Enamel Cloisonne (s266 177th mode): zone flatten + contour + sat
    Flat Zone (s263): secondary zone unification with warm ground reveal
    Atmospheric Recession (s259): minimal — Finnish landscape is flat, not deep

    Full palette:
    birch-white (0.94/0.92/0.88) -- trunk-node (0.12/0.10/0.08) --
    burnt-orange (0.82/0.40/0.08) -- cobalt (0.18/0.26/0.72) --
    forest-green (0.14/0.32/0.14) -- golden-ochre (0.68/0.52/0.12) --
    lake-dark (0.06/0.08/0.18) -- horizon-crimson (0.80/0.22/0.06) --
    leaf-russet (0.62/0.28/0.08) -- sky-ultramarine (0.12/0.18/0.60) --
    bark-shadow (0.28/0.24/0.20) -- ground-umber (0.22/0.16/0.09)

Mood & Intent
    The painting aims for the quality Gallen-Kallela described as "Finnish
    gravitas" — the particular weight of the Finnish forest landscape, its
    resistance to sentimentality, its refusal to be merely picturesque. The
    birch trees are not charming; they are ancient and vertical. The dusk
    sky is not romantic; it is a fact of the October latitude. The lake does
    not beckon; it reflects, and what it reflects is the fire of the dying
    day. The viewer should leave with the sense of having looked through a
    window — not into a painted fiction but into a real category of place:
    the Finnish lakeside forest at the end of October, which is neither tragic
    nor beautiful in the ordinary sense, but simply true.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "s266_birch_forest.png")

W, H = 1440, 1040   # landscape — Finnish forest panorama


# ── Palette ────────────────────────────────────────────────────────────────────

BIRCH_WHITE     = (0.94, 0.92, 0.88)
TRUNK_NODE      = (0.12, 0.10, 0.08)
BURNT_ORANGE    = (0.82, 0.40, 0.08)
COBALT          = (0.18, 0.26, 0.72)
FOREST_GREEN    = (0.12, 0.28, 0.12)
GOLDEN_OCHRE    = (0.68, 0.52, 0.12)
LAKE_DARK       = (0.06, 0.08, 0.20)
HORIZON_CRIMSON = (0.82, 0.24, 0.06)
LEAF_RUSSET     = (0.62, 0.28, 0.08)
SKY_ULTRAMARINE = (0.14, 0.20, 0.62)
BARK_SHADOW     = (0.28, 0.24, 0.20)
GROUND_UMBER    = (0.20, 0.14, 0.08)
SKY_COBALT_DEEP = (0.10, 0.14, 0.60)
LEAF_GOLD       = (0.78, 0.60, 0.08)


def lerp(a, b, t):
    t = max(0.0, min(1.0, float(t)))
    return tuple(float(a[i]) * (1.0 - t) + float(b[i]) * t for i in range(3))


def smooth(t):
    t = max(0.0, min(1.0, float(t)))
    return t * t * (3.0 - 2.0 * t)


def build_reference(w: int, h: int) -> Image.Image:
    """Build procedural reference for 'Birch Forest at Dusk, Lake Ruovesi'.

    Returns a PIL Image (uint8 RGB).

    Composition zones (as fraction of H):
      0.00-0.30  Sky — cobalt zenith to burnt-orange horizon
      0.30-0.38  Treeline silhouette and sky-forest transition
      0.38-0.46  Lake band — dark water with single orange reflection streak
      0.46-0.72  Forest interior — dark spruce/pine with birch trunk bases
      0.72-1.00  Forest floor — autumn leaf litter, warm umber ground
    """
    rng = np.random.RandomState(266)
    arr = np.zeros((h, w, 3), dtype=np.float32)

    # Zone boundaries (pixels)
    sky_bot     = int(h * 0.30)
    treeline_bot = int(h * 0.38)
    lake_bot    = int(h * 0.46)
    forest_bot  = int(h * 0.72)
    floor_bot   = h

    xs = np.arange(w, dtype=np.float32) / max(w - 1, 1)
    ys = np.arange(h, dtype=np.float32) / max(h - 1, 1)

    # ── Zone 1: Sky (cobalt zenith → burnt orange horizon) ───────────────────
    for row in range(sky_bot):
        fy = row / max(sky_bot - 1, 1)   # 0 = zenith, 1 = horizon
        # Deep cobalt at zenith, warming to burnt orange at horizon
        if fy < 0.5:
            col = lerp(SKY_COBALT_DEEP, COBALT, smooth(fy / 0.5))
        else:
            col = lerp(COBALT, BURNT_ORANGE, smooth((fy - 0.5) / 0.5))
        # Near horizon: blend in crimson
        if fy > 0.78:
            col = lerp(col, HORIZON_CRIMSON, smooth((fy - 0.78) / 0.22))
        noise = rng.normal(0, 0.008, w).astype(np.float32)
        arr[row, :, 0] = np.clip(col[0] + noise * 0.6, 0.0, 1.0)
        arr[row, :, 1] = np.clip(col[1] + noise * 0.5, 0.0, 1.0)
        arr[row, :, 2] = np.clip(col[2] + noise * 0.8, 0.0, 1.0)

    # ── Zone 2: Treeline silhouette ───────────────────────────────────────────
    # Jagged treeline: alternating spruce peaks and birch crowns
    treeline_y = np.zeros(w, dtype=np.int32)
    base_y = sky_bot
    for col in range(w):
        fx = col / max(w - 1, 1)
        # Periodic jagged treeline with noise
        spikes = (
            0.3 * np.sin(fx * 14.0 * np.pi) +
            0.15 * np.sin(fx * 27.0 * np.pi + 0.7) +
            0.08 * np.sin(fx * 51.0 * np.pi + 1.3)
        )
        treeline_y[col] = base_y + int((spikes + rng.normal(0, 0.018)) * (treeline_bot - base_y) * 0.6)
        treeline_y[col] = max(base_y - int((treeline_bot - base_y) * 0.3),
                              min(treeline_bot, treeline_y[col]))

    for row in range(sky_bot - int((treeline_bot - sky_bot) * 0.3), treeline_bot):
        for col in range(w):
            if row >= treeline_y[col]:
                t = (row - treeline_y[col]) / max(treeline_bot - treeline_y[col], 1)
                dark = lerp(FOREST_GREEN, TRUNK_NODE, smooth(t))
                arr[row, col, 0] = np.clip(dark[0] + rng.normal(0, 0.006), 0.0, 1.0)
                arr[row, col, 1] = np.clip(dark[1] + rng.normal(0, 0.005), 0.0, 1.0)
                arr[row, col, 2] = np.clip(dark[2] + rng.normal(0, 0.007), 0.0, 1.0)

    # ── Zone 3: Lake band ─────────────────────────────────────────────────────
    for row in range(treeline_bot, lake_bot):
        fy = (row - treeline_bot) / max(lake_bot - treeline_bot - 1, 1)
        base = lerp(TRUNK_NODE, LAKE_DARK, smooth(fy))
        noise = rng.normal(0, 0.010, w).astype(np.float32)
        arr[row, :, 0] = np.clip(base[0] + noise * 0.5, 0.0, 1.0)
        arr[row, :, 1] = np.clip(base[1] + noise * 0.4, 0.0, 1.0)
        arr[row, :, 2] = np.clip(base[2] + noise * 0.7, 0.0, 1.0)

    # Orange sky reflection streak in lake: narrow horizontal band
    streak_y = treeline_bot + int((lake_bot - treeline_bot) * 0.40)
    streak_h = max(2, int((lake_bot - treeline_bot) * 0.22))
    for row in range(streak_y, min(lake_bot, streak_y + streak_h)):
        fy = (row - streak_y) / max(streak_h - 1, 1)
        str_bright = smooth(1.0 - abs(2 * fy - 1.0)) * 0.45
        noise = rng.normal(0, 0.015, w).astype(np.float32)
        arr[row, :, 0] = np.clip(arr[row, :, 0] + str_bright * 0.90 + noise * 0.5, 0.0, 1.0)
        arr[row, :, 1] = np.clip(arr[row, :, 1] + str_bright * 0.38 + noise * 0.3, 0.0, 1.0)
        arr[row, :, 2] = np.clip(arr[row, :, 2] + str_bright * 0.04 + noise * 0.2, 0.0, 1.0)

    # ── Zone 4: Forest interior ───────────────────────────────────────────────
    for row in range(lake_bot, forest_bot):
        fy = (row - lake_bot) / max(forest_bot - lake_bot - 1, 1)
        base = lerp(TRUNK_NODE, GROUND_UMBER, smooth(fy * 0.6))
        noise = rng.normal(0, 0.012, w).astype(np.float32)
        arr[row, :, 0] = np.clip(base[0] + noise * 0.8, 0.0, 1.0)
        arr[row, :, 1] = np.clip(base[1] + noise * 0.6, 0.0, 1.0)
        arr[row, :, 2] = np.clip(base[2] + noise * 0.5, 0.0, 1.0)

    # Forest green substorey (spruce shadows)
    for row in range(lake_bot, lake_bot + int((forest_bot - lake_bot) * 0.55)):
        fy = (row - lake_bot) / max(int((forest_bot - lake_bot) * 0.55) - 1, 1)
        green_val = smooth(1.0 - fy) * 0.24
        for col in range(w):
            fx = col / max(w - 1, 1)
            # Dark green patches alternating across forest zone
            patch = (np.sin(fx * 7.0 * np.pi + 0.4) + 1.0) / 2.0
            blend = green_val * patch * 0.75
            arr[row, col, 0] = np.clip(arr[row, col, 0] * (1.0 - blend) + FOREST_GREEN[0] * blend, 0.0, 1.0)
            arr[row, col, 1] = np.clip(arr[row, col, 1] * (1.0 - blend) + FOREST_GREEN[1] * blend, 0.0, 1.0)
            arr[row, col, 2] = np.clip(arr[row, col, 2] * (1.0 - blend) + FOREST_GREEN[2] * blend, 0.0, 1.0)

    # ── Zone 5: Forest floor (leaf litter) ───────────────────────────────────
    for row in range(forest_bot, floor_bot):
        fy = (row - forest_bot) / max(floor_bot - forest_bot - 1, 1)
        base = lerp(LEAF_RUSSET, GROUND_UMBER, smooth(fy * 0.7))
        noise = rng.normal(0, 0.018, w).astype(np.float32)
        arr[row, :, 0] = np.clip(base[0] + noise * 1.0, 0.0, 1.0)
        arr[row, :, 1] = np.clip(base[1] + noise * 0.7, 0.0, 1.0)
        arr[row, :, 2] = np.clip(base[2] + noise * 0.5, 0.0, 1.0)

    # Scattered leaf-gold patches on floor
    for row in range(forest_bot, floor_bot):
        for col in range(w):
            fx = col / max(w - 1, 1)
            fy = (row - forest_bot) / max(floor_bot - forest_bot - 1, 1)
            leaf = (np.sin(fx * 19.0 * np.pi + 1.1) * np.sin(fy * 11.0 * np.pi + 0.3) + 1.0) / 2.0
            lf = leaf * 0.38 * (1.0 - fy * 0.5)
            arr[row, col, 0] = np.clip(arr[row, col, 0] * (1.0 - lf) + LEAF_GOLD[0] * lf, 0.0, 1.0)
            arr[row, col, 1] = np.clip(arr[row, col, 1] * (1.0 - lf) + LEAF_GOLD[1] * lf, 0.0, 1.0)
            arr[row, col, 2] = np.clip(arr[row, col, 2] * (1.0 - lf) + LEAF_GOLD[2] * lf, 0.0, 1.0)

    # ── Birch trunks ──────────────────────────────────────────────────────────
    # Six birch trunks at varying x positions and heights
    TRUNKS = [
        # (cx_frac, base_frac, top_frac, half_w_frac, lean_deg)
        (0.08, 1.00, 0.04, 0.013,  0.5),   # leftmost — tall, thick
        (0.20, 1.00, 0.10, 0.009, -0.3),   # second — medium
        (0.33, 1.00, 0.06, 0.011,  0.2),   # central-left
        (0.50, 1.00, 0.02, 0.014,  0.0),   # central dominant
        (0.68, 1.00, 0.12, 0.008,  0.4),   # right-centre
        (0.86, 1.00, 0.15, 0.009, -0.2),   # rightmost
    ]

    for (cx_f, base_f, top_f, hw_f, lean) in TRUNKS:
        cx    = int(w * cx_f)
        top_y = int(h * top_f)
        bot_y = int(h * base_f)
        hw    = max(3, int(w * hw_f))

        for row in range(top_y, min(h, bot_y)):
            fy = (row - top_y) / max(bot_y - top_y - 1, 1)
            lean_offset = int(lean * fy * 8)
            # Trunk widens slightly near base (flare)
            hw_row = max(2, int(hw * (1.0 + fy * 0.35)))
            col_centre = cx + lean_offset

            for col in range(max(0, col_centre - hw_row),
                             min(w, col_centre + hw_row)):
                dx = abs(col - col_centre) / max(hw_row, 1)
                # Bark: bright on face, darker at edges
                bright = smooth(1.0 - dx) * 0.85 + 0.12
                bark = lerp(BARK_SHADOW, BIRCH_WHITE, bright)
                # Dark node markings at irregular intervals
                is_node = (int(fy * 22.0 + cx_f * 7.0) % 3 == 0) and fy > 0.08
                if is_node and abs(col - col_centre) < max(1, hw_row - 2):
                    node_t = max(0.0, 1.0 - abs(fy * 22.0 + cx_f * 7.0 - int(fy * 22.0 + cx_f * 7.0)) * 8.0)
                    bark = lerp(bark, TRUNK_NODE, node_t * 0.85)
                n = rng.normal(0, 0.010)
                arr[row, col, 0] = np.clip(bark[0] + n, 0.0, 1.0)
                arr[row, col, 1] = np.clip(bark[1] + n * 0.9, 0.0, 1.0)
                arr[row, col, 2] = np.clip(bark[2] + n * 0.8, 0.0, 1.0)

    # Leaf litter at base of each trunk (warm ochre scatter)
    for (cx_f, base_f, top_f, hw_f, lean) in TRUNKS:
        cx = int(w * cx_f)
        base_y = int(h * base_f)
        scatter_top = int(h * max(base_f - 0.10, 0.65))
        scatter_r = int(w * 0.05)
        for row in range(scatter_top, min(h, base_y)):
            fy = (row - scatter_top) / max(base_y - scatter_top - 1, 1)
            for col in range(max(0, cx - scatter_r), min(w, cx + scatter_r)):
                dx = (col - cx) / max(scatter_r, 1)
                blend = smooth(1.0 - np.sqrt(dx * dx)) * smooth(fy) * 0.45
                arr[row, col, 0] = np.clip(arr[row, col, 0] * (1.0 - blend) + GOLDEN_OCHRE[0] * blend, 0.0, 1.0)
                arr[row, col, 1] = np.clip(arr[row, col, 1] * (1.0 - blend) + GOLDEN_OCHRE[1] * blend, 0.0, 1.0)
                arr[row, col, 2] = np.clip(arr[row, col, 2] * (1.0 - blend) + GOLDEN_OCHRE[2] * blend, 0.0, 1.0)

    arr = np.clip(arr, 0.0, 1.0)
    return Image.fromarray((arr * 255).astype(np.uint8), "RGB")


def main():
    print("Session 266 -- Birch Forest at Dusk, Lake Ruovesi (after Akseli Gallen-Kallela)")
    print(f"Canvas: {W}x{H}")
    print()

    ref = build_reference(W, H)
    ref_uint8 = np.array(ref)
    print("Reference built.")

    p = Painter(W, H, seed=266)

    # ── Ground: dark umber — Finnish forest floor ─────────────────────────────
    print("Toning ground (dark umber)...")
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.018)

    # ── Underpainting: birch trunk geometry, sky-treeline, lake band ──────────
    print("Underpainting...")
    p.underpainting(ref_uint8, stroke_size=52, n_strokes=230)
    p.underpainting(ref_uint8, stroke_size=42, n_strokes=250)

    # ── Block-in: sky cobalt, forest dark, birch trunks, lake ────────────────
    print("Blocking in masses...")
    p.block_in(ref_uint8, stroke_size=32, n_strokes=480)
    p.block_in(ref_uint8, stroke_size=20, n_strokes=520)

    # ── Build form: trunk form, forest depth, leaf texture ────────────────────
    print("Building form...")
    p.build_form(ref_uint8, stroke_size=12, n_strokes=540)
    p.build_form(ref_uint8, stroke_size=6,  n_strokes=480)

    # ── Place lights: sky horizon glow, lake reflection, leaf highlights ───────
    print("Placing lights...")
    p.place_lights(ref_uint8, stroke_size=5, n_strokes=320)
    p.place_lights(ref_uint8, stroke_size=3, n_strokes=280)

    # ── Hue Zone Boundary (s266 improvement) ─────────────────────────────────
    print("Applying Hue Zone Boundary pass (s266 improvement)...")
    p.paint_hue_zone_boundary_pass(
        variance_sigma=3.5,
        boundary_dark=0.60,
        interior_chroma=0.20,
        feather_sigma=1.5,
        sat_floor=0.10,
        noise_seed=266,
        opacity=0.72,
    )

    # ── Gallen-Kallela Enamel Cloisonne (177th mode) ─────────────────────────
    print("Applying Gallen-Kallela Enamel Cloisonne pass (177th mode)...")
    p.gallen_kallela_enamel_cloisonne_pass(
        flat_sigma=5.0,
        zone_blend=0.60,
        contour_strength=0.75,
        contour_sigma=0.8,
        sat_boost=0.25,
        sat_floor=0.12,
        sat_ceil=0.90,
        noise_seed=266,
        opacity=0.80,
    )

    # ── Flat Zone (s263) — secondary zone unification ─────────────────────────
    print("Applying Flat Zone pass...")
    p.paint_flat_zone_pass(
        zone_radius=4,
        preserve_edges=0.78,
        ground_r=0.22,
        ground_g=0.16,
        ground_b=0.09,
        ground_strength=0.06,
        edge_sigma=1.2,
        noise_seed=266,
        opacity=0.45,
    )

    # ── Atmospheric Recession (s259) — minimal, flat horizon ─────────────────
    print("Applying Atmospheric Recession pass...")
    p.paint_atmospheric_recession_pass(
        recession_direction="top",
        haze_lift=0.03,
        desaturation=0.10,
        cool_shift_r=0.01,
        cool_shift_g=0.00,
        cool_shift_b=0.04,
        near_fraction=0.15,
        far_fraction=0.70,
        opacity=0.25,
    )

    # ── Granulation (s258) — subtle birch bark texture ────────────────────────
    print("Applying Granulation pass...")
    p.paint_granulation_pass(
        granule_sigma=1.2,
        granule_scale=0.024,
        warm_shift=0.015,
        cool_shift=0.015,
        edge_sharpen=0.15,
        noise_seed=266,
        opacity=0.30,
    )

    # ── Save ──────────────────────────────────────────────────────────────────
    print(f"Saving to {OUTPUT_PATH}...")
    p.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
