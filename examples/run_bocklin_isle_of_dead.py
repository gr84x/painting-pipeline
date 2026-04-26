"""
run_bocklin_isle_of_dead.py — Session 200

"Reverie at the Island Shore" — after Arnold Böcklin

Image Description
─────────────────
Subject & Composition
    A solitary island viewed from low water level, centred in the frame,
    approached from a silent black lake.  The island sits at exact
    horizontal centre, its reflection a near-perfect mirror in the calm
    dark water below.  The composition is rigidly symmetrical — Böcklin's
    characteristic enclosed world, complete and self-referential.
    Foreground: the still black water surface.  Middleground: a narrow
    wooden boat gliding toward the island, carrying a single white-shrouded
    figure standing in the stern.  Background: the rocky island rising
    steeply from the water, crowned by three tall black Italian cypresses
    pressing against a pale dusk sky.

The Figure
    A single standing figure in the boat, wrapped entirely in white linen
    shroud — no face visible, no gesture, no individuality.  The figure
    is small relative to the island, its whiteness the only bright element
    in a composition of deep shadow and cool atmosphere.  The posture is
    perfectly upright, a column of white light against the dark prow of
    the boat.  Emotional state: absolute stillness, acceptance, the quiet
    dignity of transition.  The figure carries no grief and no resistance —
    only presence, in passage.

The Environment
    The island: steep vertical rock faces carved from dark stone, draped
    in thick climbing ivy (deep green, almost black).  Narrow archways
    cut into the rock — entrances to vaulted funerary chambers, dark as
    ink within.  The three cypress trees rise like black flames above the
    stone, their narrow silhouettes pressing against the dusk sky.  At the
    island's base, pale marble balustrades and a small landing quay — cold
    white stone, worn smooth by water — catch the last light.  The sky
    is the transition between day and something else: a cool grey-violet
    dusk, neither night nor day.  Horizon is a pale gold-grey wash.
    Foreground water: perfectly still, mirror-smooth, reflecting the island
    in exact inversion — dark rock above, dark rock below.  The water's
    surface is not black but very deep blue-green, its darkness coming from
    depth, not shadow.

Technique & Palette
    Arnold Böcklin's German-Swiss Symbolist technique: smooth academic
    glazing on a cool grey-blue ground.  Bocklin Mythic Atmosphere pass
    (111th distinct mode) as the primary chromatic effect — tripartite
    luminance toning darkens shadows to blue-violet void, mists the
    atmospheric midtones to cool grey-blue recession, boosts the few
    highlights (white figure, marble balustrade) to jewel-bright clarity.
    Heavy peripheral vignette frames the image in near-black.

    Palette: near-black blue-violet water/shadow, cool blue-grey
    atmospheric mist, near-black cypress green, cold white marble, warm
    ochre-amber stone (very limited), pale gold-grey dusk sky, deep
    funerary arch darkness.

Mood & Intent
    The image speaks of threshold.  Not of death, precisely — of the
    moment just before arrival at an unknown shore.  Böcklin never
    explained the painting; he said it was intended "to produce such a
    stillness that one would be awed by a knock at the door."  The viewer
    is not a mourner, not a witness — they are in the boat.  The island
    is neither welcoming nor threatening.  It simply is.  The water does
    not move.  The cypresses do not bend.  The shrouded figure does not
    turn.  The viewer carries that stillness away.

Session 200 pass used:
    bocklin_mythic_atmosphere_pass  (111th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "bocklin_isle_of_dead.png"
)
W, H = 960, 1120   # portrait — emphasises the vertical cypresses and island height


def build_reference() -> np.ndarray:
    """
    Synthetic tonal reference for 'Reverie at the Island Shore'.

    Tonal zones:
      - Sky (upper fifth): cool grey-violet dusk with pale gold horizon band
      - Island rock mass (centre): dark stone with ivy draping
      - Three cypresses: near-black narrow silhouettes above island
      - Marble balustrade and quay: pale white at island waterline
      - Funerary arch entrances: near-black rectangular openings in rock
      - Water foreground (lower half): still, dark blue-green mirror
      - Island reflection in water: exact vertical inversion of island
      - Boat and white figure: narrow boat, small white column at stern
    """
    rng = np.random.default_rng(200)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Sky: cool grey-violet dusk ────────────────────────────────────────────
    sky_bound = 0.42    # sky occupies upper 42% (island is tall)
    sky_top   = np.array([0.30, 0.30, 0.40])   # cool grey-violet at top
    sky_mid   = np.array([0.46, 0.44, 0.52])   # lighter grey-violet toward horizon
    horizon_c = np.array([0.70, 0.66, 0.52])   # pale gold-grey at horizon line
    sky_frac  = np.clip(ys / sky_bound, 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = sky_top[ch] * (1 - sky_frac) + sky_mid[ch] * sky_frac

    # Horizon gold-grey wash just above the island/water line
    hor_y     = 0.42
    hor_w     = 0.04
    hor_glow  = np.exp(-0.5 * ((ys - hor_y) / hor_w) ** 2)
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - hor_glow * 0.6) + horizon_c[ch] * hor_glow * 0.6

    # ── Water: dark blue-green mirror (lower 58%) ─────────────────────────────
    water_start = 0.42
    water_top_c  = np.array([0.08, 0.12, 0.20])   # dark blue at waterline
    water_deep_c = np.array([0.03, 0.05, 0.10])   # near-black at bottom
    water_frac   = np.clip((ys - water_start) / (1.0 - water_start), 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = np.where(
            ys > water_start,
            water_top_c[ch] * (1 - water_frac) + water_deep_c[ch] * water_frac,
            ref[:, :, ch]
        )

    # ── Island rock mass: centred, occupies middle third of width ─────────────
    isle_cx   = 0.50
    isle_top_y = 0.10   # island peaks at 10% from top
    isle_bot_y = 0.42   # island base at waterline
    isle_hw   = 0.18    # half-width

    # Island silhouette: trapezoidal — narrower at top
    isle_frac = np.clip((ys - isle_top_y) / (isle_bot_y - isle_top_y), 0.0, 1.0)
    isle_half_w = isle_hw * (0.5 + 0.5 * isle_frac)   # wider at base
    isle_dist = np.abs(xs - isle_cx) / (isle_half_w + 0.001)
    isle_mask = np.clip(1.0 - isle_dist ** 1.5, 0.0, 1.0)
    isle_vert = np.where((ys >= isle_top_y) & (ys <= isle_bot_y), 1.0, 0.0)
    isle_mask = isle_mask * isle_vert

    # Dark stone with cold cast
    stone_col = np.array([0.12, 0.10, 0.14])   # dark warm-neutral stone
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - isle_mask) + stone_col[ch] * isle_mask

    # Ivy draping: darker organic patches on rock
    ivy_noise = rng.random((H, W)).astype(np.float32)
    ivy_smooth = gaussian_filter(ivy_noise, sigma=6.0)
    ivy_mask = np.clip((ivy_smooth - 0.5) * 3.0, 0.0, 1.0) * isle_mask
    ivy_col = np.array([0.05, 0.10, 0.05])   # near-black green ivy
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - ivy_mask * 0.7) + ivy_col[ch] * ivy_mask * 0.7

    # ── Marble balustrade and quay: pale white at island base ────────────────
    quay_y = isle_bot_y
    quay_band = np.exp(-0.5 * ((ys - quay_y) / 0.015) ** 2)
    quay_mask = quay_band * isle_mask
    marble_col = np.array([0.78, 0.78, 0.76])   # cold white marble
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - quay_mask * 0.85) + marble_col[ch] * quay_mask * 0.85

    # ── Funerary arch entrances: near-black rectangles in rock ───────────────
    arch_positions = [0.42, 0.50, 0.58]   # x positions of three arches
    arch_top_y  = 0.28
    arch_bot_y  = 0.40
    arch_hw     = 0.025
    for ax in arch_positions:
        adist = np.abs(xs - ax) / arch_hw
        avert = np.where((ys >= arch_top_y) & (ys <= arch_bot_y), 1.0, 0.0)
        arch_gate = np.clip(1.0 - adist ** 3, 0.0, 1.0) * avert
        arch_col  = np.array([0.02, 0.02, 0.02])   # void darkness
        for ch in range(3):
            ref[:, :, ch] = ref[:, :, ch] * (1 - arch_gate * 0.90) + arch_col[ch] * arch_gate * 0.90

    # ── Three cypresses: near-black narrow silhouettes ────────────────────────
    cypress_xs  = [0.42, 0.50, 0.58]
    cypress_tops = [0.04, 0.02, 0.04]   # centre cypress tallest
    cypress_bots = [isle_top_y + 0.06] * 3
    for cx_x, cy_top, cy_bot in zip(cypress_xs, cypress_tops, cypress_bots):
        cy_hw   = 0.018   # very narrow
        cy_frac = np.clip((ys - cy_top) / (cy_bot - cy_top + 0.001), 0.0, 1.0)
        cy_half = cy_hw * (0.3 + 0.7 * (1.0 - cy_frac))   # narrower at top
        cy_dist = np.abs(xs - cx_x) / (cy_half + 0.001)
        cy_vert = np.where((ys >= cy_top) & (ys <= cy_bot), 1.0, 0.0)
        cy_mask = np.clip(1.0 - cy_dist ** 1.5, 0.0, 1.0) * cy_vert
        cy_col  = np.array([0.04, 0.06, 0.04])   # near-black green-black
        for ch in range(3):
            ref[:, :, ch] = ref[:, :, ch] * (1 - cy_mask) + cy_col[ch] * cy_mask

    # ── Island reflection in water: exact vertical mirror ────────────────────
    # Mirror the island zone [isle_top_y, isle_bot_y] into [isle_bot_y, 2*isle_bot_y - isle_top_y]
    refl_start = isle_bot_y
    refl_end   = min(1.0, 2.0 * isle_bot_y - isle_top_y)
    isle_zone_rows = int(isle_top_y * H)
    isle_zone_end  = int(isle_bot_y * H)
    isle_slice = ref[isle_zone_rows:isle_zone_end, :, :]
    refl_slice = isle_slice[::-1, :, :] * 0.55   # mirror + darken 45%
    refl_start_row = int(refl_start * H)
    refl_end_row   = min(H, refl_start_row + refl_slice.shape[0])
    actual_rows    = refl_end_row - refl_start_row
    # Blend softly into water
    refl_rows = actual_rows
    refl_fade = np.linspace(0.80, 0.15, refl_rows, dtype=np.float32)[:, None, None]
    existing_water = ref[refl_start_row:refl_end_row, :, :]
    ref[refl_start_row:refl_end_row, :, :] = (
        existing_water * (1 - refl_fade) + refl_slice[:refl_rows] * refl_fade
    )

    # Add faint ripple texture to reflection
    ripple = rng.random((H, W)).astype(np.float32) - 0.5
    ripple_smooth = gaussian_filter(ripple, sigma=2.5) * 0.05
    refl_zone_mask = np.zeros((H, 1, 1), dtype=np.float32)
    refl_zone_mask[refl_start_row:refl_end_row] = 0.6
    for ch in range(3):
        ref[:, :, ch] = np.clip(
            ref[:, :, ch] + ripple_smooth * refl_zone_mask[:, :, 0], 0.0, 1.0
        )

    # ── Boat: narrow dark hull approaching island centre ──────────────────────
    boat_cx = 0.50
    boat_cy = 0.54   # just below waterline / in water zone
    boat_hw = 0.10
    boat_hh = 0.014
    # Slight angular taper: hull narrower at bow
    boat_dist = np.sqrt(
        ((xs - boat_cx) / boat_hw) ** 2 + ((ys - boat_cy) / boat_hh) ** 2
    )
    boat_mask = np.clip(1.0 - boat_dist ** 0.8, 0.0, 1.0)
    boat_col  = np.array([0.08, 0.06, 0.05])   # dark weathered hull
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - boat_mask) + boat_col[ch] * boat_mask

    # ── White-shrouded figure: small white column at boat stern ──────────────
    fig_cx = boat_cx + 0.04   # stern
    fig_cy = boat_cy - 0.04   # standing above the hull
    fig_hw = 0.012
    fig_hh = 0.045
    fig_dist = np.sqrt(
        ((xs - fig_cx) / fig_hw) ** 2 + ((ys - fig_cy) / fig_hh) ** 2
    )
    fig_mask = np.clip(1.0 - fig_dist ** 1.5, 0.0, 1.0)
    fig_col  = np.array([0.86, 0.86, 0.84])   # cold white linen shroud
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - fig_mask) + fig_col[ch] * fig_mask

    # ── Atmospheric haze: very faint blue-grey softening over midground ──────
    haze_y    = 0.42
    haze_band = np.exp(-0.5 * ((ys - haze_y) / 0.08) ** 2)
    haze_col  = np.array([0.48, 0.50, 0.60])   # cool atmospheric blue-grey
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - haze_band * 0.22) + haze_col[ch] * haze_band * 0.22

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'Reverie at the Island Shore' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=200)

    # ── Ground: cool grey-blue imprimatura — Böcklin's atmospheric base ───────
    p.tone_ground((0.26, 0.28, 0.36), texture_strength=0.015)

    # ── Underpainting: establish dark island, water, and sky masses ───────────
    p.underpainting(ref_pil, stroke_size=60)

    # ── Block in: tonal masses — dark island, pale sky, dark water ───────────
    p.block_in(ref_pil, stroke_size=28)

    # ── Build form: island rock texture, cypress silhouettes ─────────────────
    p.build_form(ref_pil, stroke_size=12)

    # ── Lights: marble quay, white figure, pale horizon strip ────────────────
    p.place_lights(ref_pil, stroke_size=5)

    # ── Böcklin Mythic Atmosphere — THE signature effect ─────────────────────
    # Primary pass: full tripartite toning + heavy peripheral vignette
    p.bocklin_mythic_atmosphere_pass(
        shadow_cool=0.48,
        shadow_threshold=0.28,
        mist_strength=0.35,
        mist_color=(0.36, 0.40, 0.54),
        highlight_threshold=0.65,
        jewel_boost=0.28,
        vignette_strength=0.62,
        vignette_power=2.2,
        opacity=0.75,
    )

    # Second pass: gentler, to refine atmosphere without blowing out the figure
    p.bocklin_mythic_atmosphere_pass(
        shadow_cool=0.30,
        shadow_threshold=0.22,
        mist_strength=0.18,
        mist_color=(0.40, 0.44, 0.58),
        highlight_threshold=0.72,
        jewel_boost=0.40,   # push white figure toward pure cold white
        vignette_strength=0.28,
        vignette_power=2.8,
        opacity=0.40,
    )

    # ── Atmospheric depth: push the island into cool atmospheric recession ────
    p.atmospheric_depth_pass(
        haze_color=(0.38, 0.42, 0.58),
        desaturation=0.28,
        lightening=0.15,
        depth_gamma=1.6,
        background_only=False,
    )

    # ── Meso detail: refine island rock texture and quay stonework ───────────
    p.meso_detail_pass(strength=0.22, opacity=0.18)

    # ── Glazing: cool blue-grey unifying atmospheric veil ────────────────────
    p.glaze((0.30, 0.34, 0.52), opacity=0.07)

    # ── Final vignette: deepen the peripheral darkness ───────────────────────
    p.focal_vignette_pass(vignette_strength=0.32, opacity=0.55)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
