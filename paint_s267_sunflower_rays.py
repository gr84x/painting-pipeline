"""
paint_s267_sunflower_rays.py -- Session 267

"Three Sunflowers, Evening Sky" -- in the manner of Natalia Goncharova
(Russian Avant-Garde / Rayonism / Neo-Primitivism)

Image Description
-----------------
Subject & Composition
    Three giant sunflower heads stand against a deep cobalt-to-golden
    evening sky in a portrait-format composition (1040 × 1440). The tallest
    sunflower occupies the centre-upper canvas, its face turned directly
    toward the viewer. Two flanking sunflowers at slightly lower heights
    frame the central one -- the left flower faces three-quarters left, the
    right flower faces three-quarters right, as though the three are in
    active dialogue. The stems drive hard vertical lines from the base of
    the canvas upward, anchoring the composition against the dynamism of the
    Rayonist sky behind them. The viewer stands close, looking slightly
    upward at the central disc.

The Figure/Subject
    Each sunflower disc is rendered as a bold flat brown-black mass -- a
    large circular coin of compressed pigment at the head of each stem.
    Around each disc, 16-18 petals radiate outward as flat amber-gold
    lozenges, broad and blunt-tipped in the manner of Goncharova's bold
    Neo-Primitivist mark. The central sunflower (tallest) carries 18 petals,
    the flanking pair 16 each. The petals are in full summer abundance --
    heavy and full-faced, catching the warm evening light on their upper
    surfaces with a particularly vivid amber-gold, fading to ochre at the
    petal base where the disc shadow falls. Each stem carries two pairs of
    broad elliptical leaves -- dark, assertive, the flat-cut leaf mass of
    folk embroidery. The emotional state of the subject is vital and
    confrontational: these sunflowers face the viewer as icons face the
    worshipper, full-frontal and declarative, not picturesque.

The Environment
    The sky occupies the upper half of the canvas and the negative space
    between the sunflower heads -- a deep cobalt at the zenith, warming
    steadily through violet-blue at mid-height to warm amber-gold near the
    horizon. The Rayonist pass fractures this sky into crossing beams of
    directional light: the golden sunflower disc-light streaks diagonally
    across the cooler sky zones; cool blue-violet rays cross the warm amber
    horizon light; and at every crossing, a zone of chromatic interference
    where warm and cool rays mix in a spatially alternating shimmer. The
    ground zone at the canvas base is warm olive-sienna -- a summer garden
    floor, loose and textured, from which the thick stems rise. There is no
    middle distance; the composition pushes the sunflowers immediately
    forward, filling the picture plane.

Technique & Palette
    Natalia Goncharova Rayonist mode -- session 267, 178th distinct painting
    mode.

    Stage 1 (MULTI-ANGLE DIRECTIONAL STREAK SYNTHESIS, n_angles=4, sigma=26):
    The existing canvas colour is stretched simultaneously in 4 directions
    (0°, 45°, 90°, 135°) using 1D Gaussian blurs after rotation. The mean
    of all 4 directional blurs synthesises a multi-directional ray field --
    each bright source (sunflower disc, petal highlight, sky glow) emits
    crossing rays in the Rayonist tradition.

    Stage 2 (LUMINANCE-WEIGHTED STREAK OVERLAY, ray_strength=0.30):
    Bright areas generate stronger ray contributions. The golden disc (lum
    near 0.7) produces full-strength rays; the dark leaf masses (lum ~0.2)
    produce minimal ray extension. This models the Rayonist physical
    principle that light-source intensity governs ray emission strength.

    Stage 3 (CHROMATIC HUE SHIMMER, shimmer_angle=16°, shimmer_freq=0.05):
    In the crossing-ray interference zones (where the rayonist composite
    diverges from the original above shimmer_threshold=0.10), a spatially
    alternating hue rotation of ±16° creates the chromatic vibration of
    Goncharova's prismatic colour placement along crossing ray paths -- warm
    gold and cool violet alternating at the sub-compositional scale.

    Pipeline improvement s267 (PALETTE KNIFE RIDGE TEXTURE): Applied first
    to add gradient-following ridge texture to the sunflower petals and leaf
    masses -- ridges run transversely across petals (perpendicular to the
    petal-axis gradient), giving them the tactile impasto quality of
    Goncharova's loaded-brush Neo-Primitivist technique.

    Stage-by-stage pipeline:
    Ground: warm sienna-brown (0.30, 0.20, 0.10) -- summer earth
    Underpainting: sunflower mass geometry, sky-ground division
    Block-in (broad): sky cobalt mass, ground warm, sunflower discs
    Block-in (medium): petal masses, stem verticals, leaf pairs
    Build form (medium): petal form, disc edge, leaf detail
    Build form (fine): petal edge, disc centre ring, leaf vein suggestion
    Place lights: petal highlight catch, disc rim highlight, sky gradient
    Palette Knife Ridge (s267): gradient-following ridge texture on petals
    Goncharova Rayonist (267 178th mode): crossing light ray fracture
    Hue Zone Boundary (s266): reinforces petal/sky zone boundaries
    Granulation (s258): subtle surface pigment granularity

    Full palette:
    sunflower-gold (0.92/0.76/0.10) -- disc-brown (0.24/0.14/0.04) --
    stem-green (0.16/0.42/0.10) -- cobalt-blue (0.10/0.14/0.58) --
    amber-orange (0.86/0.44/0.06) -- violet (0.24/0.14/0.52) --
    horizon-gold (0.90/0.62/0.10) -- sienna-earth (0.58/0.38/0.14) --
    pale-cream (0.96/0.90/0.70) -- leaf-dark (0.10/0.28/0.08) --
    petal-ochre (0.70/0.48/0.06) -- ground-warm (0.30/0.20/0.10)

Mood & Intent
    The painting embodies Goncharova's Rayonist conviction that painting
    should render not objects but the LIGHT BETWEEN objects -- the dynamic
    electromagnetic exchange between illuminated surface and viewing eye.
    The sunflowers are not static botanical specimens but active emitters
    of golden evening light. Their warm disc faces and glowing petals
    generate crossing ray fields that fracture the cobalt sky into planes
    of warm and cool interference. The mood is vitalistic and declarative:
    the sunflowers radiate into the viewer's space with the same assertive
    frontality as the peasant icons and embroideries that Goncharova drew
    from in her Neo-Primitivist period. The viewer should leave with the
    sense of having perceived not three sunflowers but the LIGHT of three
    sunflowers -- the rays, not the objects.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "s267_sunflower_rays.png")

W, H = 1040, 1440   # portrait — tall sunflower composition


# ── Palette ────────────────────────────────────────────────────────────────────

COBALT_DEEP    = (0.08, 0.10, 0.56)
COBALT         = (0.12, 0.16, 0.62)
VIOLET_SKY     = (0.24, 0.14, 0.52)
AMBER_ORANGE   = (0.86, 0.44, 0.06)
HORIZON_GOLD   = (0.92, 0.66, 0.10)
PALE_CREAM     = (0.94, 0.88, 0.68)
SUNFLOWER_GOLD = (0.92, 0.76, 0.10)
PETAL_OCHRE    = (0.70, 0.48, 0.06)
DISC_BROWN     = (0.24, 0.14, 0.04)
DISC_DARK      = (0.14, 0.08, 0.02)
STEM_GREEN     = (0.16, 0.42, 0.10)
LEAF_DARK      = (0.10, 0.28, 0.08)
SIENNA_EARTH   = (0.58, 0.38, 0.14)
GROUND_WARM    = (0.30, 0.20, 0.10)
OLIVE_GREEN    = (0.36, 0.44, 0.12)


def lerp(a, b, t):
    t = max(0.0, min(1.0, float(t)))
    return tuple(float(a[i]) * (1.0 - t) + float(b[i]) * t for i in range(3))


def smooth(t):
    t = max(0.0, min(1.0, float(t)))
    return t * t * (3.0 - 2.0 * t)


def build_reference(w: int, h: int) -> Image.Image:
    """Build procedural reference for 'Three Sunflowers, Evening Sky'.

    Returns a PIL Image (uint8 RGB).

    Composition zones (as fraction of H):
      0.00-0.62  Sky — deep cobalt zenith to amber-gold horizon
      0.62-0.78  Upper ground / stem base zone
      0.78-1.00  Ground — warm sienna-olive floor
    Sunflowers overlapping sky and ground zones.
    """
    rng = np.random.RandomState(267)
    arr = np.zeros((h, w, 3), dtype=np.float32)

    # ── Zone 1: Sky (cobalt zenith → amber-gold horizon) ─────────────────────
    sky_bot = int(h * 0.62)
    for row in range(sky_bot):
        fy = row / max(sky_bot - 1, 1)
        if fy < 0.35:
            col = lerp(COBALT_DEEP, COBALT, smooth(fy / 0.35))
        elif fy < 0.65:
            col = lerp(COBALT, VIOLET_SKY, smooth((fy - 0.35) / 0.30))
        else:
            col = lerp(VIOLET_SKY, AMBER_ORANGE, smooth((fy - 0.65) / 0.35))
        noise = rng.normal(0, 0.008, w).astype(np.float32)
        arr[row, :, 0] = np.clip(col[0] + noise * 0.5, 0.0, 1.0)
        arr[row, :, 1] = np.clip(col[1] + noise * 0.4, 0.0, 1.0)
        arr[row, :, 2] = np.clip(col[2] + noise * 0.6, 0.0, 1.0)

    # Horizon glow band just below sky
    glow_top = int(sky_bot * 0.88)
    for row in range(glow_top, sky_bot):
        fy = (row - glow_top) / max(sky_bot - glow_top - 1, 1)
        glow = smooth(fy) * 0.28
        noise = rng.normal(0, 0.010, w).astype(np.float32)
        arr[row, :, 0] = np.clip(arr[row, :, 0] + glow * 0.95 + noise * 0.3, 0.0, 1.0)
        arr[row, :, 1] = np.clip(arr[row, :, 1] + glow * 0.52 + noise * 0.2, 0.0, 1.0)
        arr[row, :, 2] = np.clip(arr[row, :, 2] + glow * 0.04 + noise * 0.1, 0.0, 1.0)

    # ── Zone 2: Upper ground / stem base ─────────────────────────────────────
    ground_top = sky_bot
    ground_mid = int(h * 0.78)
    for row in range(ground_top, ground_mid):
        fy = (row - ground_top) / max(ground_mid - ground_top - 1, 1)
        col = lerp(OLIVE_GREEN, SIENNA_EARTH, smooth(fy))
        noise = rng.normal(0, 0.014, w).astype(np.float32)
        arr[row, :, 0] = np.clip(col[0] + noise * 0.8, 0.0, 1.0)
        arr[row, :, 1] = np.clip(col[1] + noise * 0.6, 0.0, 1.0)
        arr[row, :, 2] = np.clip(col[2] + noise * 0.5, 0.0, 1.0)

    # ── Zone 3: Ground floor ──────────────────────────────────────────────────
    for row in range(ground_mid, h):
        fy = (row - ground_mid) / max(h - ground_mid - 1, 1)
        col = lerp(SIENNA_EARTH, GROUND_WARM, smooth(fy))
        noise = rng.normal(0, 0.018, w).astype(np.float32)
        arr[row, :, 0] = np.clip(col[0] + noise * 1.0, 0.0, 1.0)
        arr[row, :, 1] = np.clip(col[1] + noise * 0.7, 0.0, 1.0)
        arr[row, :, 2] = np.clip(col[2] + noise * 0.6, 0.0, 1.0)

    # ── Sunflower helper functions ────────────────────────────────────────────

    def draw_stem(cx, top_y, bot_y, stem_w):
        for row in range(top_y, min(h, bot_y)):
            fy = (row - top_y) / max(bot_y - top_y - 1, 1)
            hw = max(2, int(stem_w * (1.0 + fy * 0.15)))
            noise_x = int(rng.normal(0, 0.5))
            for col in range(max(0, cx - hw + noise_x), min(w, cx + hw + noise_x)):
                dx = abs(col - cx) / max(hw, 1)
                blend = smooth(1.0 - dx) * 0.85 + 0.12
                sc = lerp(LEAF_DARK, STEM_GREEN, blend)
                n = rng.normal(0, 0.012)
                arr[row, col, 0] = np.clip(sc[0] + n, 0.0, 1.0)
                arr[row, col, 1] = np.clip(sc[1] + n * 0.8, 0.0, 1.0)
                arr[row, col, 2] = np.clip(sc[2] + n * 0.6, 0.0, 1.0)

    def draw_leaf(cx, cy, half_len, half_wid, angle_deg):
        cos_a = np.cos(np.radians(angle_deg))
        sin_a = np.sin(np.radians(angle_deg))
        row_lo = max(0, cy - int(half_len + half_wid))
        row_hi = min(h, cy + int(half_len + half_wid) + 1)
        col_lo = max(0, cx - int(half_len + half_wid))
        col_hi = min(w, cx + int(half_len + half_wid) + 1)
        for row in range(row_lo, row_hi):
            for col in range(col_lo, col_hi):
                dx = col - cx
                dy = row - cy
                dx_rot =  dx * cos_a + dy * sin_a
                dy_rot = -dx * sin_a + dy * cos_a
                inside = (dx_rot / max(half_len, 1))**2 + (dy_rot / max(half_wid, 1))**2
                if inside < 1.0:
                    blend = smooth(1.0 - inside) * 0.88
                    lc = lerp(LEAF_DARK, STEM_GREEN, blend)
                    n = rng.normal(0, 0.010)
                    arr[row, col, 0] = np.clip(lc[0] + n, 0.0, 1.0)
                    arr[row, col, 1] = np.clip(lc[1] + n * 0.8, 0.0, 1.0)
                    arr[row, col, 2] = np.clip(lc[2] + n * 0.6, 0.0, 1.0)

    def draw_petals(cx, cy, disc_r, petal_len, petal_wid, n_petals, rotation_offset=0.0):
        for i in range(n_petals):
            theta = i * 2.0 * np.pi / n_petals + rotation_offset
            pcx = cx + int((disc_r + petal_len * 0.5) * np.cos(theta))
            pcy = cy + int((disc_r + petal_len * 0.5) * np.sin(theta))
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)
            row_lo = max(0, pcy - petal_len - 2)
            row_hi = min(h, pcy + petal_len + 2)
            col_lo = max(0, pcx - petal_len - 2)
            col_hi = min(w, pcx + petal_len + 2)
            for row in range(row_lo, row_hi):
                for col in range(col_lo, col_hi):
                    dx = col - pcx
                    dy = row - pcy
                    # Rotate to petal axis frame
                    dx_rot =  dx * cos_t + dy * sin_t
                    dy_rot = -dx * sin_t + dy * cos_t
                    # Lozenge / rhombus petal shape
                    inside = (abs(dx_rot) / max(petal_len * 0.5, 1) +
                              abs(dy_rot) / max(petal_wid * 0.5, 1))
                    if inside < 1.0:
                        # Inner gradient: bright gold at tip, ochre at base
                        tip_frac = (dx_rot / max(petal_len * 0.5, 1) + 1.0) / 2.0
                        pc = lerp(PETAL_OCHRE, SUNFLOWER_GOLD, smooth(tip_frac))
                        blend = smooth(1.0 - inside)
                        edge_shadow = smooth(abs(dy_rot) / max(petal_wid * 0.5, 1))
                        shadow = lerp(pc, PETAL_OCHRE, edge_shadow * 0.35)
                        n = rng.normal(0, 0.012)
                        arr[row, col, 0] = np.clip(shadow[0] + n, 0.0, 1.0)
                        arr[row, col, 1] = np.clip(shadow[1] + n * 0.8, 0.0, 1.0)
                        arr[row, col, 2] = np.clip(shadow[2] + n * 0.5, 0.0, 1.0)

    def draw_disc(cx, cy, r):
        row_lo = max(0, cy - r - 1)
        row_hi = min(h, cy + r + 1)
        col_lo = max(0, cx - r - 1)
        col_hi = min(w, cx + r + 1)
        for row in range(row_lo, row_hi):
            for col in range(col_lo, col_hi):
                d2 = (col - cx)**2 + (row - cy)**2
                if d2 < r * r:
                    dist = np.sqrt(d2) / r
                    # Outer ring slightly lighter, centre dark
                    ring_bright = smooth(dist) * 0.30
                    dc = lerp(DISC_DARK, DISC_BROWN, ring_bright)
                    n = rng.normal(0, 0.010)
                    arr[row, col, 0] = np.clip(dc[0] + n, 0.0, 1.0)
                    arr[row, col, 1] = np.clip(dc[1] + n * 0.8, 0.0, 1.0)
                    arr[row, col, 2] = np.clip(dc[2] + n * 0.6, 0.0, 1.0)

    # ── Three sunflowers ──────────────────────────────────────────────────────
    # (head_cx_frac, head_cy_frac, disc_r, petal_len, petal_wid, n_petals,
    #  stem_top_frac, stem_cx_frac, stem_w)
    FLOWERS = [
        # Central — tallest, face-on
        (0.52, 0.17, 68, 88, 28, 18, 0.17, 0.52, 5,  0.0),
        # Left flanking
        (0.24, 0.36, 58, 76, 24, 16, 0.36, 0.24, 4,  0.18),
        # Right flanking
        (0.76, 0.27, 62, 82, 26, 16, 0.27, 0.76, 4, -0.12),
    ]

    for (cx_f, cy_f, disc_r, plen, pwid, n_pet,
         stem_top_f, scx_f, sw, rot) in FLOWERS:
        cx = int(w * cx_f)
        cy = int(h * cy_f)
        scx = int(w * scx_f)
        stem_top = int(h * stem_top_f)

        # Petals (draw first so disc covers their bases)
        draw_petals(cx, cy, disc_r, plen, pwid, n_pet, rotation_offset=rot)

        # Disc
        draw_disc(cx, cy, disc_r)

        # Stem (from head down to canvas bottom)
        draw_stem(scx, stem_top, h, sw)

        # Leaves: two pairs along stem
        leaf_y1 = stem_top + int((h - stem_top) * 0.25)
        leaf_y2 = stem_top + int((h - stem_top) * 0.52)
        leaf_len = max(30, int(w * 0.075))
        leaf_wid = max(12, int(w * 0.030))
        draw_leaf(scx - leaf_len - 4, leaf_y1, leaf_len, leaf_wid,  25)
        draw_leaf(scx + leaf_len + 4, leaf_y1, leaf_len, leaf_wid, -25)
        draw_leaf(scx - leaf_len - 3, leaf_y2, leaf_len - 4, leaf_wid - 2,  30)
        draw_leaf(scx + leaf_len + 3, leaf_y2, leaf_len - 4, leaf_wid - 2, -30)

    arr = np.clip(arr, 0.0, 1.0)
    return Image.fromarray((arr * 255).astype(np.uint8), "RGB")


def main():
    print("Session 267 -- Three Sunflowers, Evening Sky (after Natalia Goncharova)")
    print(f"Canvas: {W}x{H}")
    print()

    ref = build_reference(W, H)
    ref_uint8 = np.array(ref)
    print("Reference built.")

    p = Painter(W, H, seed=267)

    # ── Ground: warm sienna-brown — summer earth ──────────────────────────────
    print("Toning ground (warm sienna-brown)...")
    p.tone_ground((0.28, 0.18, 0.10), texture_strength=0.022)

    # ── Underpainting: sunflower mass geometry, sky-ground division ───────────
    print("Underpainting...")
    p.underpainting(ref_uint8, stroke_size=54, n_strokes=240)
    p.underpainting(ref_uint8, stroke_size=44, n_strokes=260)

    # ── Block-in: sky cobalt, ground warm, sunflower discs and petals ─────────
    print("Blocking in masses...")
    p.block_in(ref_uint8, stroke_size=34, n_strokes=500)
    p.block_in(ref_uint8, stroke_size=22, n_strokes=530)

    # ── Build form: petal form, disc edge, leaf masses ────────────────────────
    print("Building form...")
    p.build_form(ref_uint8, stroke_size=13, n_strokes=560)
    p.build_form(ref_uint8, stroke_size=7,  n_strokes=490)

    # ── Place lights: petal catch-light, disc rim, sky horizon glow ───────────
    print("Placing lights...")
    p.place_lights(ref_uint8, stroke_size=5, n_strokes=320)
    p.place_lights(ref_uint8, stroke_size=3, n_strokes=290)

    # ── Palette Knife Ridge (s267 improvement) ────────────────────────────────
    print("Applying Palette Knife Ridge pass (s267 improvement)...")
    p.paint_palette_knife_ridge_pass(
        ridge_freq=0.16,
        ridge_scale=0.048,
        ridge_sigma=9.0,
        lum_lo=0.20,
        lum_hi=0.80,
        noise_seed=267,
        opacity=0.60,
    )

    # ── Goncharova Rayonist (178th mode) ──────────────────────────────────────
    print("Applying Goncharova Rayonist pass (178th mode)...")
    p.goncharova_rayonist_pass(
        n_angles=4,
        ray_sigma=26.0,
        ray_strength=0.30,
        shimmer_angle=16.0,
        shimmer_freq=0.05,
        shimmer_threshold=0.10,
        noise_seed=267,
        opacity=0.72,
    )

    # ── Hue Zone Boundary (s266) — reinforce petal/sky zone boundaries ────────
    print("Applying Hue Zone Boundary pass (s266)...")
    p.paint_hue_zone_boundary_pass(
        variance_sigma=3.0,
        boundary_dark=0.50,
        interior_chroma=0.16,
        feather_sigma=1.5,
        sat_floor=0.12,
        noise_seed=267,
        opacity=0.60,
    )

    # ── Granulation (s258) — subtle canvas texture ────────────────────────────
    print("Applying Granulation pass...")
    p.paint_granulation_pass(
        granule_sigma=1.4,
        granule_scale=0.022,
        warm_shift=0.012,
        cool_shift=0.012,
        edge_sharpen=0.12,
        noise_seed=267,
        opacity=0.28,
    )

    # ── Save ──────────────────────────────────────────────────────────────────
    print(f"Saving to {OUTPUT_PATH}...")
    p.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
