"""
paint_s256_kollwitz_grieving_mother.py -- Session 256

"Grieving Mother, Candlelight" -- after Käthe Kollwitz

Image Description
-----------------
Subject & Composition
    A single woman -- a grieving mother -- occupies the left three-quarters of
    the canvas, viewed from a three-quarter angle, slightly to her right. She
    is seated, hunched forward, her head bowed and turned away from the viewer
    so only the back of her head and left cheekbone are visible. Her hands are
    clasped tightly together in her lap, pressed into her thighs. The composition
    is deliberately asymmetric and compressed: the figure fills the frame from
    below the knees to just above the crown of her head, with only a narrow
    margin of dark space at the top and right.

The Figure
    The woman is in her fifties -- working-class, heavy-set, dressed in a dark
    coarse wool dress. Her hands are thick and rope-veined, the knuckles pale
    where they press together. The back of her neck is visible above the collar:
    creased, shadowed, carrying the weight of her posture. A single candle
    burns below the frame at the lower-left, throwing its light upward onto
    the left side of her face and neck -- the only warm illumination in the
    composition. Her visible cheekbone and jaw are lit by this raking upward
    light; the right side of her face is in total shadow. The emotional state
    is one of silent, crushing grief -- not weeping, which is active; this is
    the stillness after weeping, the aftermath of loss held motionless in the
    body. The posture says everything: she has not moved in an hour.

The Environment
    The background is pure charcoal darkness -- no specific room, no furniture
    identifiable, just the compressed tonal field that Kollwitz uses to press
    her figures forward. In the lower-left foreground there is the faint circular
    glow of a candle halo, warm amber, slightly smeared by the charcoal medium.
    Immediately behind the figure's right shoulder, a vague darker mass suggests
    a wall or the back of a chair -- not defined, just present. The boundary
    between figure and ground is achieved by value contrast only: the lit side
    of the figure reads against the dark background, the shadow side disappears
    into it and is only recoverable by the slight shift of texture between
    figure and void.

Technique & Palette
    Käthe Kollwitz Charcoal Compression mode -- session 256, 167th distinct mode.

    Stage 1, DARK TONAL COMPRESSION: dark_power=1.60. Power-law luminance
    compression pushes the entire tonal range toward the dark half of the scale,
    simulating charcoal's impossibility of achieving pure white except by
    erasure. The result is that the few pale passages -- the lit cheekbone,
    the pale candle glow, the knuckles -- read with explosive luminosity against
    the compressed dark mass surrounding them.

    Stage 2, DIRECTIONAL CHARCOAL SMEAR: smear_angle_deg=52, smear_sigma_along=5.5,
    smear_sigma_across=0.55, smear_strength=0.60. The directional sweep is set at
    52 degrees to simulate the diagonal arm motion of Kollwitz's broad charcoal
    marks across the paper. The anisotropic blur is elongated along the smear
    axis and narrow perpendicular to it, creating the characteristic gesture
    directionality in the dark mid-tones of the figure's dress and background.

    Stage 3, HIGHLIGHT LIFT: lift_density=0.012, lift_radius=2.8,
    lift_strength=0.25. Sparse Gaussian-blurred lift zones simulate kneaded-
    eraser removal of charcoal at the lit cheekbone, the candle halo, and the
    pale knuckle highlights. The lift is strongest where the canvas is darkest
    (1-lum weighting), ensuring the eraser reveals near-paper tone in the deep
    shadows and adds only subtle brightening to already-pale areas.

    Edge Temperature improvement: contrast_strength=0.12, gradient_zone_px=3.5.
    At the boundary between the warm candle light zone (hue ~orange) and the
    cool-dark shadow zone (hue ~blue-grey), bidirectional temperature contrast
    is applied: the warm candle side is pushed slightly warmer (R+, B-) and
    the cool shadow side slightly cooler (R-, B+), intensifying the temperature
    opposition that gives the candle light its specific warmth against the
    surrounding cold dark.

    Palette: charcoal black (0.08/0.07/0.06) -- compressed dark (0.22/0.18/0.15)
    -- graphite mid (0.38/0.32/0.27) -- warm mid (0.52/0.45/0.36) --
    lifted grey (0.72/0.65/0.55) -- candle warm (0.82/0.58/0.22) --
    lit flesh (0.76/0.62/0.48) -- near-white lift (0.88/0.83/0.76) --
    warm shadow flesh (0.42/0.34/0.28)

Mood & Intent
    This painting is about weight. Not the dramatic weight of an operatic grief,
    but the specific physical weight that enters the body when it has run out of
    movement -- when there is nothing left to do but sit. Kollwitz painted this
    category of stillness more than any other artist: the moment after the soldier
    is already dead, after the letter has been read, after all the protesting has
    been done and the situation has not changed. The candle is the only specific
    thing in this darkness, and it illuminates only the back of a head that is
    turned away. The viewer is not permitted to see the face directly -- is kept
    outside of the grief, a witness rather than a participant. The intention is
    not to generate sympathy but recognition: the viewer knows this posture. They
    have sat in it themselves, or will.
"""

import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import cairo
from PIL import Image
from stroke_engine import Painter, mix_paint

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "s256_kollwitz_grieving_mother.png")

W, H = 720, 960   # portrait -- charcoal study proportions
RNG = random.Random(256)


# ─── Colour constants ──────────────────────────────────────────────────────────

CHARCOAL_BLACK   = (0.08, 0.07, 0.06)
COMPRESSED_DARK  = (0.22, 0.18, 0.15)
GRAPHITE_MID     = (0.38, 0.32, 0.27)
WARM_MID         = (0.52, 0.45, 0.36)
LIFTED_GREY      = (0.72, 0.65, 0.55)
CANDLE_WARM      = (0.82, 0.58, 0.22)
LIT_FLESH        = (0.76, 0.62, 0.48)
NEAR_WHITE_LIFT  = (0.88, 0.83, 0.76)
WARM_SHADOW_FLESH = (0.42, 0.34, 0.28)
DRESS_DARK       = (0.16, 0.13, 0.11)
NECK_WARM        = (0.68, 0.52, 0.40)


def build_reference(w: int, h: int) -> Image.Image:
    """
    Build a procedural reference image:
    - Deep charcoal background across full canvas
    - Figure silhouette (hunched, seated woman) in left 3/4
    - Candle glow in lower-left
    - Lit cheekbone / back of head in upper-left third
    - Clasped hands in lower-center
    """
    arr = np.zeros((h, w, 3), dtype=np.float32)

    # Background -- near-black charcoal field
    arr[:, :, :] = [0.10, 0.08, 0.07]

    # Slight darker void at right side (behind shadow of figure)
    arr[:, int(w * 0.72):, :] *= 0.7

    # Figure silhouette region -- overall body mass
    # Head center: ~20% from left, ~20% from top
    # Shoulders: ~18-55% from left, ~28-35% from top
    # Torso/dress: ~10-62% from left, ~28-88% from top
    # Clasped hands: ~22-48% from left, ~68-82% from top

    # Body mass (dark dress)
    for row in range(h):
        fy = row / h
        if 0.28 <= fy <= 0.98:
            # Dress silhouette -- hunched, wider at bottom
            width_frac = 0.08 + (fy - 0.28) * 0.30   # widens downward
            cx = 0.28 + (fy - 0.28) * 0.02            # slight rightward drift
            left = max(0, int((cx - width_frac / 2) * w))
            right = min(w, int((cx + width_frac / 2) * w))
            # Dress colour -- very dark warm-grey
            arr[row, left:right, :] = [0.18, 0.14, 0.11]

    # Upper back / neck -- slightly lighter
    for row in range(int(h * 0.28), int(h * 0.45)):
        fy = row / h
        cx = 0.24
        half_w = 0.065
        left = max(0, int((cx - half_w) * w))
        right = min(w, int((cx + half_w) * w))
        arr[row, left:right, :] = [0.28, 0.22, 0.17]

    # Visible neck (lit by candle from below-left)
    neck_rows = range(int(h * 0.30), int(h * 0.40))
    neck_cols = range(int(w * 0.17), int(w * 0.26))
    for row in neck_rows:
        for col in neck_cols:
            dist_from_lit_side = (col / w - 0.17) / 0.09   # 0=lit, 1=shadow
            brightness = NECK_WARM[0] * (1.0 - dist_from_lit_side * 0.6)
            r = max(0, min(1, brightness))
            g = max(0, min(1, NECK_WARM[1] * (1.0 - dist_from_lit_side * 0.5)))
            b = max(0, min(1, NECK_WARM[2] * (1.0 - dist_from_lit_side * 0.4)))
            arr[row, col, :] = [r, g, b]

    # Head mass -- back of head and left profile
    head_cy = int(h * 0.19)
    head_cx = int(w * 0.24)
    head_rx = int(w * 0.09)
    head_ry = int(h * 0.10)
    for row in range(max(0, head_cy - head_ry), min(h, head_cy + head_ry)):
        for col in range(max(0, head_cx - head_rx), min(w, head_cx + head_rx)):
            ex = ((col - head_cx) / head_rx) ** 2
            ey = ((row - head_cy) / head_ry) ** 2
            if ex + ey < 1.0:
                # Hair -- very dark
                arr[row, col, :] = [0.13, 0.10, 0.08]

    # Left cheekbone/jaw -- lit by candle from lower-left (upward raking light)
    cheek_cy = int(h * 0.24)
    cheek_cx = int(w * 0.18)
    cheek_rx = int(w * 0.06)
    cheek_ry = int(h * 0.05)
    for row in range(max(0, cheek_cy - cheek_ry), min(h, cheek_cy + cheek_ry)):
        for col in range(max(0, cheek_cx - cheek_rx), min(w, cheek_cx + cheek_rx)):
            ex = ((col - cheek_cx) / cheek_rx) ** 2
            ey = ((row - cheek_cy) / cheek_ry) ** 2
            if ex + ey < 1.0:
                falloff = 1.0 - math.sqrt(ex + ey)
                r = LIT_FLESH[0] * falloff + WARM_SHADOW_FLESH[0] * (1 - falloff)
                g = LIT_FLESH[1] * falloff + WARM_SHADOW_FLESH[1] * (1 - falloff)
                b = LIT_FLESH[2] * falloff + WARM_SHADOW_FLESH[2] * (1 - falloff)
                arr[row, col, :] = [r, g, b]

    # Clasped hands -- pale knuckles
    hands_cy = int(h * 0.74)
    hands_cx = int(w * 0.30)
    hands_rx = int(w * 0.10)
    hands_ry = int(h * 0.06)
    for row in range(max(0, hands_cy - hands_ry), min(h, hands_cy + hands_ry)):
        for col in range(max(0, hands_cx - hands_rx), min(w, hands_cx + hands_rx)):
            ex = ((col - hands_cx) / hands_rx) ** 2
            ey = ((row - hands_cy) / hands_ry) ** 2
            if ex + ey < 1.0:
                falloff = 1.0 - math.sqrt(ex + ey)
                # Hands lit from below-left by candle
                r = NEAR_WHITE_LIFT[0] * falloff * 0.7 + WARM_MID[0] * (1 - falloff * 0.7)
                g = NEAR_WHITE_LIFT[1] * falloff * 0.6 + WARM_MID[1] * (1 - falloff * 0.6)
                b = NEAR_WHITE_LIFT[2] * falloff * 0.5 + WARM_MID[2] * (1 - falloff * 0.5)
                arr[row, col, :] = [r, g, b]

    # Candle glow -- lower-left, warm amber circle
    candle_cy = int(h * 0.90)
    candle_cx = int(w * 0.10)
    candle_radius = int(w * 0.10)
    for row in range(max(0, candle_cy - candle_radius), min(h, candle_cy + candle_radius)):
        for col in range(max(0, candle_cx - candle_radius), min(w, candle_cx + candle_radius)):
            dist = math.sqrt((row - candle_cy) ** 2 + (col - candle_cx) ** 2) / candle_radius
            if dist < 1.0:
                falloff = (1.0 - dist) ** 2
                r = 0.10 + CANDLE_WARM[0] * falloff * 0.85
                g = 0.08 + CANDLE_WARM[1] * falloff * 0.65
                b = 0.07 + CANDLE_WARM[2] * falloff * 0.40
                # Blend with existing (dress may overlap candle glow)
                existing = arr[row, col, :].copy()
                arr[row, col, :] = [
                    min(1.0, existing[0] * (1 - falloff * 0.8) + r * falloff * 0.8),
                    min(1.0, existing[1] * (1 - falloff * 0.8) + g * falloff * 0.8),
                    min(1.0, existing[2] * (1 - falloff * 0.8) + b * falloff * 0.8),
                ]

    # Upward candle light wash on lower figure (warm gradient from bottom-left)
    for row in range(h):
        for col in range(int(w * 0.45)):
            fy = row / h
            fx = col / w
            # Distance from candle position
            dist = math.sqrt((fy - 0.90) ** 2 + (fx - 0.10) ** 2)
            warm_falloff = max(0, 1.0 - dist / 0.70)
            if warm_falloff > 0.01:
                arr[row, col, 0] = min(1.0, arr[row, col, 0] + warm_falloff * 0.12)
                arr[row, col, 1] = min(1.0, arr[row, col, 1] + warm_falloff * 0.07)
                # No blue boost -- candle is warm

    # Convert to uint8 PIL image
    arr_uint8 = np.clip(arr * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(arr_uint8, "RGB")


def main():
    print("Session 256 -- Grieving Mother, Candlelight (after Käthe Kollwitz)")
    print(f"Canvas: {W}×{H}")
    print()

    ref = build_reference(W, H)
    print("Reference built.")

    p = Painter(W, H)

    # Ground -- very dark, almost black charcoal field on buff paper
    # (charcoal drawings start with the paper as the lightest value,
    # but our pipeline starts with a tone ground -- use a dark ground
    # to simulate a heavily worked charcoal surface)
    print("Toning ground...")
    p.tone_ground(COMPRESSED_DARK, texture_strength=0.04)

    # Block in the dark masses
    print("Blocking in dark masses...")
    p.block_in(ref, stroke_size=40, n_strokes=120)

    # Build form -- second pass for tonal differentiation
    print("Building form...")
    p.build_form(ref, stroke_size=18, n_strokes=80)

    # Place key lights -- the lit cheekbone, candle halo, knuckles
    print("Placing lights...")
    p.place_lights(ref, stroke_size=8, n_strokes=50)

    # ── Kollwitz pass ──────────────────────────────────────────────────────────
    print("Applying Kollwitz Charcoal Compression pass...")
    p.kollwitz_charcoal_compression_pass(
        dark_power=1.60,
        smear_angle_deg=52.0,
        smear_sigma_along=5.5,
        smear_sigma_across=0.55,
        smear_strength=0.60,
        lift_density=0.012,
        lift_radius=2.8,
        lift_strength=0.25,
        opacity=0.85,
        seed=256,
    )

    # ── Edge Temperature improvement ────────────────────────────────────────────
    print("Applying Edge Temperature pass...")
    p.paint_edge_temperature_pass(
        warm_hue_center=0.07,    # orange-amber (candle)
        warm_hue_width=0.16,
        cool_hue_center=0.62,    # blue-grey (shadow void)
        cool_hue_width=0.22,
        gradient_zone_px=3.5,
        contrast_strength=0.12,
        opacity=0.65,
    )

    # ── Tonal key (from s255) -- push to low-key for Kollwitz ─────────────────
    print("Applying Tonal Key pass...")
    p.paint_tonal_key_pass(
        target_key=0.32,        # very low-key -- Kollwitz presses into darkness
        key_strength=3.8,
        dither_amplitude=0.005,
        opacity=0.60,
    )

    # Final contour weight (from s254 improvement)
    print("Applying Contour Weight pass...")
    p.paint_contour_weight_pass(
        contour_threshold=0.06,
        contour_strength=0.55,
        max_weight=0.85,
        weight_exponent=1.4,
        taper_strength=0.25,
        opacity=0.50,
    )

    # Save
    print(f"Saving to {OUTPUT_PATH}...")
    p.save(OUTPUT_PATH)
    print("Done.")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
