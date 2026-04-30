"""
paint_s268_gorge_at_dawn.py -- Session 268

"Huangshan Gorge at Dawn" -- in the manner of Zao Wou-Ki
(Chinese-French Lyrical Abstraction / Abstract Expressionism)

Image Description
-----------------
Subject & Composition
    A deep mountain gorge at the moment of first dawn light -- the Huangshan
    (Yellow Mountains) of Anhui Province, evoked rather than depicted, in
    portrait format (1040 x 1440). The composition is centred on a luminous
    core of warm gold and apricot light that occupies the upper third of the
    canvas: sunrise breaking through morning mist above the gorge. The light
    source is not a disc or orb -- it is a zone of concentrated brilliance,
    the mountain mist acting as a diffuser, distributing the first sunlight
    across a large warm field. Radiating outward from this core, the canvas
    darkens in every direction: downward into the gorge shadow, sideways into
    the canyon walls, upward into the pre-dawn sky above the mist line.

The Subject
    The gorge itself exists as felt depth rather than depicted form. The
    canyon walls are not drawn -- they are present as dark blue-indigo zones
    at the left and right margins, their materiality established through dense
    calligraphic peripheral marks: long, looping, ink-dark strokes that orbit
    the luminous center at oblique tangential angles, the visual language of
    the Chinese brush tradition fused with Western gestural painting. In the
    lower half of the canvas, the gorge floor and cliff bases emerge from the
    deepest indigo-black: raw rock, the ink tradition\'s ground. Pine silhouettes
    at the left and right lower edges -- a few dark verticals, barely legible --
    anchor the composition to Chinese mountain landscape without narrative.
    The mood of the subject is one of CONCENTRATED STILLNESS: the gorge holds
    its breath at first light, vast and ancient. No human presence.

The Environment
    Foreground (lower third): deep blue-black and indigo void -- the gorge
    floor in pre-dawn shadow. Ink-dark and weighty. Surface: the texture of
    stone and deep water.
    Mid-field (central third): the transition zone -- warm amber-ochre and
    burnt sienna on the left canyon wall where the first light catches the
    rock face; cool cerulean and slate-grey on the right wall still in shadow;
    between them, a band of atmospheric mist, misty white dissolving into
    warm apricot. The colour temperature clash in this zone is extreme -- warm
    and cool meet at the canyon\'s axis.
    Background/Sky (upper third): the luminous center zone. Warm gold and
    apricot dissolve outward into pale misty white, then into the cool grey-
    blue of the pre-dawn upper atmosphere. No hard edge anywhere in this zone;
    everything dissolves into everything else.
    The depth of field is total: from the nearest rock face to the farthest
    peaks, the atmosphere blurs everything equally, creating a sense of
    limitless depth within a bounded frame.

Technique & Palette
    Zao Wou-Ki Lyrical Abstraction mode -- session 268, 179th distinct mode.

    Pipeline:
    1. Procedural reference: warm-gold luminous upper center, dark blue-
       indigo lower gorge, atmospheric transition zone with mist passages.
    2. tone_ground: deep warm indigo-black (0.08/0.06/0.18) -- the void
       ground of Chinese ink painting; darkness as starting condition.
    3. underpainting: structure the gorge depth -- dark below, light above.
    4. block_in (broad): the main tonal masses -- sky glow, gorge shadow,
       canyon walls.
    5. block_in (medium): refine the mist-band, the rock walls, the warm-cool
       boundary at the canyon axis.
    6. build_form (medium): model the gorge depth -- tonal modelling of the
       atmospheric recession.
    7. build_form (fine): rock texture, mist dissolution, pine silhouettes.
    8. place_lights: the luminous center highlight and warm catches on rock.
    9. paint_depth_atmosphere_pass (s268 improvement): aerial perspective --
       the blue-grey haze of atmospheric distance.
    10. zao_wou_ki_ink_atmosphere_pass (268, 179th mode): luminous center glow,
        dark peripheral vignette, dual thermal field, calligraphic marks.
    11. paint_granulation_pass: subtle atmospheric pigment scatter.
    12. paint_sfumato_contour_dissolution_pass: edge dissolution in the mist.

    Full palette:
    luminous-gold (0.98/0.88/0.42) -- blue-black void (0.04/0.06/0.16) --
    amber-ochre (0.88/0.54/0.12) -- indigo (0.14/0.22/0.52) --
    warm-apricot (0.96/0.72/0.30) -- cerulean (0.32/0.44/0.68) --
    burnt-sienna (0.60/0.36/0.14) -- misty-white (0.82/0.80/0.74) --
    slate-grey (0.22/0.28/0.40) -- deep-ground (0.08/0.06/0.18)

Mood & Intent
    The image is intended to convey PRIMORDIAL DEPTH AND FIRST LIGHT -- the
    sensation of standing at the edge of a mountain gorge in the seconds before
    sunrise fully breaks, when the landscape is still mostly dark but a warm
    radiance is already present in the upper atmosphere. The viewer should feel
    both the weight of the darkness below and the pull of the light above --
    the vertical tension of the gorge architecture, the horizontal dissolution
    of the mist. The calligraphic peripheral marks carry the energy of the
    Chinese ink tradition: the understanding that a mark is not a representation
    but an event, a gesture of the hand in the presence of the world. The
    painting should leave the viewer with a feeling of quiet awe at geological
    time and the transience of any particular moment of light.
"""

import sys
import os
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)

from stroke_engine import Painter

W, H = 1040, 1440
SEED = 268
OUTPUT = os.path.join(REPO, "s268_gorge_at_dawn.png")


def build_reference(w: int, h: int) -> np.ndarray:
    """
    Build a procedural reference for 'Huangshan Gorge at Dawn'.
    No figures or animals -- procedural Python only.

    Architecture:
    - Upper zone (top 38%): warm luminous gold/apricot sky -- the sunrise glow
    - Transition zone (38-58%): atmospheric mist band -- misty white/amber
    - Mid zone (58-75%): canyon wall transition -- warm left, cool right
    - Lower zone (75-100%): deep gorge void -- blue-black indigo

    The reference uses radial gradients to create a luminous center in the
    upper-center region, with atmospheric recession into the peripheral zones.
    """
    ref = np.zeros((h, w, 3), dtype=np.float32)

    Y, X = np.mgrid[0:h, 0:w]
    y_n = Y.astype(np.float32) / float(h - 1)  # 0 = top, 1 = bottom
    x_n = X.astype(np.float32) / float(w - 1)  # 0 = left, 1 = right

    # ── Luminous center (upper-center) ────────────────────────────────────────
    cx, cy = 0.50, 0.28   # center of glow in normalized coords
    glow_dist = np.sqrt((x_n - cx) ** 2 + ((y_n - cy) * 1.3) ** 2)
    glow_field = np.exp(-glow_dist ** 2 / (2.0 * 0.18 ** 2)).astype(np.float32)

    # ── Sky gradient (top zone) ────────────────────────────────────────────────
    sky_mask = np.clip(1.0 - y_n / 0.55, 0.0, 1.0).astype(np.float32)

    # Sky colors: luminous gold center, pale misty white outward, cool grey at edges
    sky_r = (0.98 * glow_field + 0.82 * (1 - glow_field)) * sky_mask
    sky_g = (0.88 * glow_field + 0.80 * (1 - glow_field)) * sky_mask
    sky_b = (0.42 * glow_field + 0.74 * (1 - glow_field)) * sky_mask

    # ── Mist band (transition zone 38-62%) ────────────────────────────────────
    mist_lo, mist_hi = 0.35, 0.62
    mist_weight = np.clip(
        1.0 - np.abs(y_n - (mist_lo + mist_hi) / 2.0) / ((mist_hi - mist_lo) / 2.0),
        0.0, 1.0
    ).astype(np.float32)
    mist_weight *= np.clip(1.0 - glow_dist * 2.5, 0.0, 1.0).astype(np.float32)

    mist_r = 0.96 * mist_weight
    mist_g = 0.90 * mist_weight
    mist_b = 0.74 * mist_weight

    # ── Canyon walls (mid zone 55-80%) ────────────────────────────────────────
    wall_y_lo, wall_y_hi = 0.52, 0.80
    wall_weight = np.clip(
        (y_n - wall_y_lo) / (wall_y_hi - wall_y_lo), 0.0, 1.0
    ) * np.clip(
        1.0 - (y_n - wall_y_hi) / 0.08, 0.0, 1.0
    )
    wall_weight = wall_weight.astype(np.float32)

    # Left wall: warm amber-ochre (sun-lit)
    left_weight = (wall_weight * np.clip(1.0 - x_n / 0.45, 0.0, 1.0)).astype(np.float32)
    wall_r_l = 0.72 * left_weight
    wall_g_l = 0.44 * left_weight
    wall_b_l = 0.14 * left_weight

    # Right wall: cool cerulean-slate (shadow)
    right_weight = (wall_weight * np.clip((x_n - 0.55) / 0.45, 0.0, 1.0)).astype(np.float32)
    wall_r_r = 0.22 * right_weight
    wall_g_r = 0.34 * right_weight
    wall_b_r = 0.58 * right_weight

    # ── Deep gorge void (lower zone 72-100%) ──────────────────────────────────
    gorge_lo = 0.70
    gorge_weight = np.clip((y_n - gorge_lo) / (1.0 - gorge_lo), 0.0, 1.0).astype(np.float32)
    gorge_weight = gorge_weight ** 1.4  # deepen the fall-off
    gorge_r = 0.08 * gorge_weight
    gorge_g = 0.06 * gorge_weight
    gorge_b = 0.18 * gorge_weight

    # ── Pine silhouettes (lower edges) ────────────────────────────────────────
    # Left pine cluster
    pine_x_l = np.clip(1.0 - x_n / 0.18, 0.0, 1.0).astype(np.float32)
    pine_y_l = np.clip((y_n - 0.74) / 0.20, 0.0, 1.0).astype(np.float32)
    pine_left = (pine_x_l * pine_y_l * 0.85).astype(np.float32)

    # Right pine cluster
    pine_x_r = np.clip((x_n - 0.82) / 0.18, 0.0, 1.0).astype(np.float32)
    pine_y_r = np.clip((y_n - 0.76) / 0.18, 0.0, 1.0).astype(np.float32)
    pine_right = (pine_x_r * pine_y_r * 0.85).astype(np.float32)

    pine_mask = np.clip(pine_left + pine_right, 0.0, 1.0).astype(np.float32)
    pine_r = 0.06 * pine_mask
    pine_g = 0.08 * pine_mask
    pine_b = 0.12 * pine_mask

    # ── Composite all zones ────────────────────────────────────────────────────
    R = (sky_r + mist_r * (1 - sky_mask) * 0.8 +
         wall_r_l + wall_r_r + gorge_r + pine_r)
    G = (sky_g + mist_g * (1 - sky_mask) * 0.8 +
         wall_g_l + wall_g_r + gorge_g + pine_g)
    B = (sky_b + mist_b * (1 - sky_mask) * 0.8 +
         wall_b_l + wall_b_r + gorge_b + pine_b)

    ref[:, :, 0] = np.clip(R, 0.0, 1.0)
    ref[:, :, 1] = np.clip(G, 0.0, 1.0)
    ref[:, :, 2] = np.clip(B, 0.0, 1.0)

    return ref


def main() -> None:
    print("=" * 60)
    print("Session 268 -- Huangshan Gorge at Dawn")
    print("Artist: Zao Wou-Ki (Chinese-French Lyrical Abstraction)")
    print("Mode: 179th distinct mode -- zao_wou_ki_ink_atmosphere_pass")
    print("=" * 60)

    # ── Build reference ────────────────────────────────────────────────────────
    print("\nBuilding procedural reference...")
    ref_f = build_reference(W, H)
    # Painter methods expect uint8 reference (0-255); convert once here.
    ref = (np.clip(ref_f, 0.0, 1.0) * 255).astype(np.uint8)
    ref_img = Image.fromarray(ref, "RGB")

    ref_path = os.path.join(REPO, "s268_reference.png")
    ref_img.save(ref_path)
    print(f"Reference saved: {ref_path}")

    # ── Initialise painter ─────────────────────────────────────────────────────
    print("\nInitialising painter...")
    p = Painter(W, H, seed=SEED)

    # ── Ground: deep warm indigo-black ────────────────────────────────────────
    print("  tone_ground...")
    p.tone_ground((0.08, 0.06, 0.18), texture_strength=0.015)

    # ── Underpainting: establish gorge depth structure ─────────────────────────
    print("  underpainting (gorge structure)...")
    p.underpainting(ref, stroke_size=54, n_strokes=240)
    p.underpainting(ref, stroke_size=44, n_strokes=260)

    # ── Block in: main tonal masses ───────────────────────────────────────────
    print("  block_in (broad)...")
    p.block_in(ref, stroke_size=34, n_strokes=460)
    print("  block_in (medium)...")
    p.block_in(ref, stroke_size=20, n_strokes=500)

    # ── Build form: atmospheric recession ─────────────────────────────────────
    print("  build_form (medium)...")
    p.build_form(ref, stroke_size=12, n_strokes=540)
    print("  build_form (fine)...")
    p.build_form(ref, stroke_size=5, n_strokes=420)

    # ── Place lights: luminous center highlights ───────────────────────────────
    print("  place_lights...")
    p.place_lights(ref, stroke_size=4, n_strokes=300)

    # ── s268 improvement: Aerial perspective depth haze ───────────────────────
    print("  paint_depth_atmosphere_pass (s268 improvement)...")
    p.paint_depth_atmosphere_pass(
        haze_color=(0.76, 0.82, 0.92),
        depth_sigma=44.0,
        max_haze=0.30,
        vertical_weight=0.62,
        contrast_weight=0.38,
        opacity=0.72,
    )

    # ── 179th mode: Zao Wou-Ki Ink Atmosphere ─────────────────────────────────
    print("  zao_wou_ki_ink_atmosphere_pass (179th mode)...")
    p.zao_wou_ki_ink_atmosphere_pass(
        glow_sigma=0.20,
        glow_strength=0.28,
        vignette_strength=0.42,
        vignette_color=(0.04, 0.06, 0.14),
        warm_boost=0.18,
        cool_shift=0.15,
        ink_n_strokes=32,
        ink_length_frac=0.24,
        ink_width=3.0,
        ink_opacity=0.58,
        noise_seed=SEED,
        opacity=0.84,
    )

    # ── Supporting passes ──────────────────────────────────────────────────────
    print("  paint_granulation_pass...")
    p.paint_granulation_pass(
        granule_sigma=1.2,
        granule_scale=0.05,
        opacity=0.55,
    )

    print("  paint_sfumato_contour_dissolution_pass...")
    p.paint_sfumato_contour_dissolution_pass(
        blur_sigma=1.4,
        dissolve_strength=0.35,
        edge_threshold=0.05,
        opacity=0.60,
    )

    # ── Save output ────────────────────────────────────────────────────────────
    print(f"\nSaving output to {OUTPUT}...")
    p.save(OUTPUT)
    print(f"Output saved: {OUTPUT}")
    print("\nSession 268 complete.")


if __name__ == "__main__":
    main()
