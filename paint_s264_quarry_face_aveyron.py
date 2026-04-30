"""
paint_s264_quarry_face_aveyron.py -- Session 264

"Quarry Face at Nightfall, Aveyron" -- in the manner of Pierre Soulages

Image Description
-----------------
Subject & Composition
    A vertical basalt and schist quarry face, Conques-en-Rouergue, Aveyron,
    France -- the region where Pierre Soulages was born and from which his
    darkest instincts came. The stone wall fills nearly the entire canvas.
    The face is cut into a hillside; the ancient fracture planes of the rock
    run nearly horizontal, interrupted by irregular vertical joints. The
    viewpoint is direct -- face to face with the stone, as if standing a
    few metres from it, looking straight at it. There is no horizon line,
    no sky to speak of (a narrow sliver at the very top of the canvas), no
    middleground. The stone is the subject. The stone is everything.

The Figure (Environment)
    The basalt is nearly total darkness. The mineral is matte in its depths
    but at the horizontal fracture planes -- where the stone split along its
    ancient grain under geological pressure -- the polished inner faces catch
    the last raking light of dusk from the west. These fracture seams read as
    horizontal bands of warmth against the surrounding mineral dark: not bright,
    not dramatic, but present -- the way a single candle reads in a cathedral.
    There are approximately fourteen to eighteen clearly visible fracture bands
    across the stone face, varying in apparent width from a narrow seam to a
    broader shelf. The left side of each fracture is slightly brighter than the
    right, where shadow accumulates as the evening light departs. At the very
    top of the canvas -- barely 7% of the canvas height -- a narrow band of deep
    violet-indigo sky is visible above the quarry's cut rim. At the very bottom
    -- approximately 10% of the canvas -- a still pool of dark water at the
    quarry base mirrors the stone above: the fracture bands appear again,
    inverted, in the water, even fainter, rippled only by a breath of air. The
    stone surface between fractures carries micro-texture: fine parallel
    saw-marks from the original quarrying, natural inclusions of quartz catching
    occasional points of light, and at the finest scale, a grey lichen that
    registers only as the faintest variation in the near-black field. The
    rightmost 25% of the stone face falls more deeply into shadow.

Technique & Palette
    Soulages Outrenoir mode -- session 264, 175th distinct painting mode.

    Stage 1 ULTRA-BLACK DEEPENING (black_threshold=0.40, deepening_power=2.4):
    All pixels below luminance 0.40 are compressed by a power-law toward
    near-zero, creating the Soulages pigment depth -- the pure absorption of
    industrial-grade matte black acrylic. The basalt absorbs at 97%; what
    remains is the trace of fracture geometry, mineral inclusion, and tool mark.

    Stage 2 HORIZONTAL REFLECTIVE STRIPE FIELD (stripe_freq=24.0,
    stripe_strength=0.052, stripe_threshold=0.46):
    Within dark zones, sinusoidal horizontal luminance bands simulate the
    squeegee-drag marks of Soulages' tool: each horizontal sweep of the palette
    knife creates a ridge of slightly different reflectivity. These are not
    colour -- they are brightness, the physics of surface geometry.

    Stage 3 DARK-SIDE EDGE BLOOM (bloom_sigma=3.0, bloom_strength=0.065):
    At transitions from dark stone to lighter fracture seams, the dark side
    makes the light appear brighter than it is. The eye compensates. Soulages
    understood this -- that the deeper the black, the more luminous the adjacent
    seam of light appears. The bloom occurs FROM the dark side, lifting adjacent
    light pixels without touching the dark zone itself.

    Pipeline improvement s264 LUMINANCE EXCAVATION (dark_threshold=0.34,
    variance_sigma=5.0, texture_strength=0.10, lift_amount=0.030):
    Applied after the structural phases to excavate buried micro-texture from
    the dark zones -- the canvas grain, the stroke direction from underpainting,
    the pooling of pigment in slight depressions -- making each near-black zone
    carry the suggestion of internal complexity.

    Full palette:
    outrenoir-black (0.03/0.03/0.04) -- reflective-near-black (0.08/0.08/0.10)
    dark-schist (0.15/0.14/0.17) -- fracture-shadow (0.24/0.22/0.20)
    fracture-lit (0.42/0.38/0.32) -- fracture-warm (0.56/0.50/0.40)
    sky-violet (0.18/0.14/0.28) -- sky-near-black (0.06/0.05/0.10)
    water-mirror (0.04/0.04/0.06) -- quartz-inclusion (0.52/0.50/0.48)

Mood & Intent
    The viewer stands face-to-face with darkness. Not darkness as absence --
    darkness as material, as mineral, as geological time. The stone has been
    here for three hundred million years. The quarry face was cut within the
    last century. The fracture planes were opened two hundred million years ago
    by pressures the imagination cannot hold. Against this time scale, the
    painting is a meditation. The viewer should feel the specific quality of
    confronting something that does not need them: the stone is complete without
    observation, without witness. The few bands of light within the dark face
    are not warmth or invitation -- they are geometry, the record of ancient
    pressure, the signature of deep time. The intended emotional response is not
    awe but presence: the viewer and the stone in the same silence, in the same
    late light, in the same darkness that will outlast both.
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "s264_quarry_face_aveyron.png")

W, H = 1040, 1440   # portrait — vertical stone face


# ── Palette ────────────────────────────────────────────────────────────────────

OUTRENOIR_BLACK  = (0.03, 0.03, 0.04)
REFL_NEAR_BLACK  = (0.08, 0.08, 0.10)
DARK_SCHIST      = (0.14, 0.13, 0.16)
SCHIST_MID       = (0.20, 0.18, 0.22)
FRACTURE_SHADOW  = (0.24, 0.22, 0.20)
FRACTURE_LIT     = (0.42, 0.38, 0.32)
FRACTURE_WARM    = (0.56, 0.50, 0.40)
QUARTZ_INCL      = (0.52, 0.50, 0.48)
SKY_VIOLET       = (0.18, 0.14, 0.28)
SKY_NEAR_BLACK   = (0.06, 0.05, 0.10)
WATER_MIRROR     = (0.04, 0.04, 0.06)
WATER_REFLECT    = (0.10, 0.09, 0.12)


def lerp(a, b, t):
    t = max(0.0, min(1.0, float(t)))
    return tuple(float(a[i]) * (1.0 - t) + float(b[i]) * t for i in range(3))


def build_reference(w: int, h: int) -> np.ndarray:
    """Build procedural reference for 'Quarry Face at Nightfall, Aveyron'.

    Returns float32 RGB array, shape (H, W, 3), values in [0, 1].
    """
    rng = np.random.RandomState(264)
    ref = np.zeros((h, w, 3), dtype=np.float32)

    sky_rows   = int(h * 0.07)    # top 7% — narrow violet sky band
    water_rows = int(h * 0.10)    # bottom 10% — dark quarry pool
    stone_top  = sky_rows
    stone_bot  = h - water_rows

    xs = np.arange(w, dtype=np.float32) / max(w - 1, 1)  # [0, 1] horizontal
    ys = np.arange(h, dtype=np.float32) / max(h - 1, 1)  # [0, 1] vertical

    # ── Sky band: deep violet-indigo gradient ──────────────────────────────────
    for row in range(sky_rows):
        t = row / max(sky_rows - 1, 1)   # 0=top (violet), 1=stone edge (near-black)
        col = lerp(SKY_VIOLET, SKY_NEAR_BLACK, t ** 0.7)
        ref[row, :, 0] = col[0]
        ref[row, :, 1] = col[1]
        ref[row, :, 2] = col[2]

    # ── Stone face base: very dark, horizontally uniform ──────────────────────
    for row in range(stone_top, stone_bot):
        # Right side 25% falls more deeply into shadow
        left_base  = np.full(w, DARK_SCHIST[0], dtype=np.float32)
        left_base2 = np.full(w, DARK_SCHIST[1], dtype=np.float32)
        left_base3 = np.full(w, DARK_SCHIST[2], dtype=np.float32)

        # Shadow ramp across the right 30% of the image
        shadow_start = 0.70
        shadow_mask = np.clip((xs - shadow_start) / (1.0 - shadow_start), 0.0, 1.0)
        left_base  -= shadow_mask * 0.08
        left_base2 -= shadow_mask * 0.07
        left_base3 -= shadow_mask * 0.09

        # Subtle raking-light warmth on left 40%
        light_mask = np.clip((0.40 - xs) / 0.40, 0.0, 1.0) * 0.03
        left_base  += light_mask
        left_base2 += light_mask * 0.8
        left_base3 += light_mask * 0.6

        ref[row, :, 0] = np.clip(left_base, 0.0, 1.0)
        ref[row, :, 1] = np.clip(left_base2, 0.0, 1.0)
        ref[row, :, 2] = np.clip(left_base3, 0.0, 1.0)

    # ── Horizontal fracture planes ─────────────────────────────────────────────
    # Generate 16 fracture positions with varying vertical spacing
    rng_frac = np.random.RandomState(2640)
    n_frac = 16
    stone_height = stone_bot - stone_top
    # Distribute fractures with irregular spacing
    base_spacing = stone_height / (n_frac + 1)
    fracture_positions = []
    y = stone_top + base_spacing * 0.5
    for i in range(n_frac):
        jitter = rng_frac.uniform(-base_spacing * 0.25, base_spacing * 0.25)
        frac_y = int(y + jitter)
        if stone_top + 20 <= frac_y <= stone_bot - 20:
            fracture_positions.append(frac_y)
        y += base_spacing + rng_frac.uniform(-base_spacing * 0.1, base_spacing * 0.1)

    for fy in fracture_positions:
        # Fracture width: 3 to 9 pixels, varying
        fw = rng_frac.randint(2, 6)
        # Fracture brightness varies: left side brighter (raking light)
        for dy in range(-fw, fw + 1):
            row = fy + dy
            if not (stone_top <= row < stone_bot):
                continue
            # Gaussian falloff from fracture centre
            t_edge = 1.0 - abs(dy) / (fw + 1)
            # Left side: warm fracture light; right side: fracture shadow
            lit_r = np.linspace(FRACTURE_WARM[0], FRACTURE_SHADOW[0], w)
            lit_g = np.linspace(FRACTURE_WARM[1], FRACTURE_SHADOW[1], w)
            lit_b = np.linspace(FRACTURE_WARM[2], FRACTURE_SHADOW[2], w)

            # Shadow ramp kills fracture on the right
            shadow_mask = np.clip((xs - 0.70) / 0.30, 0.0, 1.0)
            lit_r = lit_r * (1.0 - shadow_mask * 0.6)
            lit_g = lit_g * (1.0 - shadow_mask * 0.6)
            lit_b = lit_b * (1.0 - shadow_mask * 0.6)

            blend = t_edge * 0.85
            ref[row, :, 0] = np.clip(
                ref[row, :, 0] * (1.0 - blend) + lit_r * blend, 0.0, 1.0)
            ref[row, :, 1] = np.clip(
                ref[row, :, 1] * (1.0 - blend) + lit_g * blend, 0.0, 1.0)
            ref[row, :, 2] = np.clip(
                ref[row, :, 2] * (1.0 - blend) + lit_b * blend, 0.0, 1.0)

    # ── Micro-texture: quartz inclusions and saw-marks ─────────────────────────
    # Fine horizontal saw-mark texture (very subtle, <2% variation)
    saw_noise = rng.normal(0, 0.008, (stone_bot - stone_top, 1)).astype(np.float32)
    saw_noise = np.broadcast_to(saw_noise, (stone_bot - stone_top, w)).copy()
    ref[stone_top:stone_bot, :, 0] = np.clip(
        ref[stone_top:stone_bot, :, 0] + saw_noise, 0.0, 1.0)
    ref[stone_top:stone_bot, :, 1] = np.clip(
        ref[stone_top:stone_bot, :, 1] + saw_noise * 0.9, 0.0, 1.0)
    ref[stone_top:stone_bot, :, 2] = np.clip(
        ref[stone_top:stone_bot, :, 2] + saw_noise * 0.8, 0.0, 1.0)

    # Random quartz inclusions (tiny bright specks, very sparse)
    n_quartz = 120
    qx = rng.randint(0, w, n_quartz)
    qy = rng.randint(stone_top, stone_bot, n_quartz)
    for i in range(n_quartz):
        r_, g_, b_ = QUARTZ_INCL
        ref[qy[i], qx[i], 0] = r_
        ref[qy[i], qx[i], 1] = g_
        ref[qy[i], qx[i], 2] = b_

    # ── Water reflection: inverted stone, darker ──────────────────────────────
    water_start = stone_bot
    water_end   = h
    water_h     = water_end - water_start

    # Take bottom portion of stone, flip vertically, darken
    source_rows = max(water_h, 1)
    stone_mirror_src = ref[stone_bot - source_rows:stone_bot, :, :].copy()
    stone_mirror     = stone_mirror_src[::-1, :, :] * 0.45

    # Add slight ripple variation to water
    ripple_noise = rng.normal(0, 0.005, (water_h, w)).astype(np.float32)
    stone_mirror[:, :, 0] = np.clip(stone_mirror[:, :, 0] + ripple_noise, 0.0, 1.0)
    stone_mirror[:, :, 1] = np.clip(stone_mirror[:, :, 1] + ripple_noise, 0.0, 1.0)
    stone_mirror[:, :, 2] = np.clip(stone_mirror[:, :, 2] + ripple_noise, 0.0, 1.0)

    # Apply to water band
    rows_to_fill = min(water_h, stone_mirror.shape[0])
    ref[water_start:water_start + rows_to_fill, :, :] = (
        stone_mirror[:rows_to_fill, :, :])

    # Water base: near-black at very bottom
    for row in range(water_start, water_end):
        t = (row - water_start) / max(water_h - 1, 1)
        darkening = 1.0 - t * 0.5
        ref[row, :, :] = np.clip(ref[row, :, :] * darkening, 0.0, 1.0)

    return np.clip(ref, 0.0, 1.0)


def main():
    print("Session 264 -- Quarry Face at Nightfall, Aveyron (after Pierre Soulages)")
    print(f"Canvas: {W}×{H}")
    print()

    ref_arr = build_reference(W, H)
    ref_uint8 = (ref_arr * 255).astype(np.uint8)
    print("Reference built.")

    p = Painter(W, H, seed=264)

    # ── Ground: outrenoir black ───────────────────────────────────────────────
    print("Toning ground (outrenoir black)...")
    p.tone_ground((0.04, 0.04, 0.05), texture_strength=0.010)

    # ── Underpainting: structural geometry of the stone face ──────────────────
    print("Underpainting...")
    p.underpainting(ref_uint8, stroke_size=56, n_strokes=240)
    p.underpainting(ref_uint8, stroke_size=46, n_strokes=260)

    # ── Block-in: dark zones, fracture bands, sky sliver ──────────────────────
    print("Blocking in masses...")
    p.block_in(ref_uint8, stroke_size=34, n_strokes=460)
    p.block_in(ref_uint8, stroke_size=22, n_strokes=480)

    # ── Build form: fracture depth, micro-texture variation ───────────────────
    print("Building form...")
    p.build_form(ref_uint8, stroke_size=13, n_strokes=520)
    p.build_form(ref_uint8, stroke_size=6,  n_strokes=440)

    # ── Place lights: fracture warmth, quartz glints, sky ────────────────────
    print("Placing lights...")
    p.place_lights(ref_uint8, stroke_size=4, n_strokes=300)
    p.place_lights(ref_uint8, stroke_size=3, n_strokes=280)

    # ── Luminance Excavation (s264 improvement) ───────────────────────────────
    print("Applying Luminance Excavation pass (s264 improvement)...")
    p.paint_luminance_excavation_pass(
        dark_threshold=0.34,
        variance_sigma=5.0,
        texture_strength=0.10,
        lift_amount=0.030,
        noise_seed=264,
        opacity=0.65,
    )

    # ── Soulages Outrenoir pass (175th mode) ──────────────────────────────────
    print("Applying Soulages Outrenoir pass (175th mode)...")
    p.soulages_outrenoir_pass(
        black_threshold=0.40,
        deepening_power=2.4,
        stripe_freq=24.0,
        stripe_strength=0.052,
        stripe_threshold=0.46,
        bloom_sigma=3.0,
        bloom_strength=0.065,
        noise_seed=264,
        opacity=0.82,
    )

    # ── Flat Zone pass (s263 improvement) ────────────────────────────────────
    print("Applying Flat Zone pass...")
    p.paint_flat_zone_pass(
        zone_radius=4,
        preserve_edges=0.85,
        ground_r=0.06,
        ground_g=0.06,
        ground_b=0.08,
        ground_strength=0.04,
        edge_sigma=1.2,
        noise_seed=264,
        opacity=0.50,
    )

    # ── Shadow Bleed (s257) ───────────────────────────────────────────────────
    print("Applying Shadow Bleed pass...")
    p.paint_shadow_bleed_pass(
        shadow_threshold=0.28,
        bright_threshold=0.55,
        bleed_sigma=8.0,
        reflect_strength=0.06,
        warm_r=0.42,
        warm_g=0.38,
        warm_b=0.30,
        opacity=0.25,
    )

    # ── Save ──────────────────────────────────────────────────────────────────
    print(f"Saving to {OUTPUT_PATH}...")
    p.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
