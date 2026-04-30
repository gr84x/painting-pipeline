"""
paint_s269_garden_sochi.py -- Session 269

"Garden at Sochi, Dusk" -- in the manner of Arshile Gorky
(Armenian-American Biomorphic Abstraction / Abstract Expressionism)

Image Description
-----------------
Subject & Composition
    A garden landscape at dusk, viewed from an oblique elevated angle -- a wide
    composition (1440 × 1040) inspired by Arshile Gorky's Garden in Sochi series
    (c.1940-41), his group of semi-abstract paintings derived from memories of his
    father's garden in the Van province of historic Armenia. The composition is
    divided into three biomorphic zones: a warm amber-gold sky occupying the upper
    half, biomorphic viridian-to-umber plant masses anchoring the lower-left and
    right, and a luminous ochre mid-ground where the late afternoon sun falls on
    the earth between masses. Scattered crimson and rose accent shapes -- abstracted
    poppy and flower memories -- pulse through the middle plane. No horizon is
    named. The forms are organic, rounded, and irregular, with boundaries that
    shift between hard contour and soft bleed depending on the saturation and
    the thinness of the paint layer above.

The Subject
    The subject is not a scene but a memory of abundant organic life: the feel of
    a Mediterranean garden in late afternoon heat, the weight of dark viridian
    vegetation against warm ochre earth, the flicker of red flower colour against
    green and gold. Three primary biomorphic masses dominate: (Left) a dense
    dark viridian form -- trees, hedgerow, old stone under root -- occupying the
    lower-left quarter, its interior deep and cool, its boundary luminous where
    the afternoon sun catches the leaf edges. (Center-lower) a quieter earth
    form in sienna and umber, warm and grounded, from which accent shapes emerge.
    (Right) a lighter, more atmospheric mass -- dappled, partly dissolved in
    the warm light, partly lost in warm amber ground. The mood of the subject
    is warm, unhurried, and melancholic -- the garden holds the memory of
    childhood summer, vast and specific at once. No human presence, but the
    feeling of a place made by human hands over generations.

The Environment
    Upper sky zone (top 45%): warm amber-gold fading toward pale luminous cream
    at the zenith -- the sky just before dusk, when the light turns golden and
    the shadows begin to lengthen. The sky has a luminous core in the center-right
    (the sun not yet set) that bleeds outward into warm cream, then into the
    cooler ochre-grey of the upper atmosphere.
    Mid-ground (40-65%): the richly painted zone. Warm ochre earth in the center,
    cut through by three crimson/burgundy accent shapes (abstracted poppies).
    The earth is warm and tactile -- burnt sienna overlaid with ochre, the ground
    showing through the thin paint layers. This is the zone of maximum colour
    complexity, where viridian, crimson, ochre, and amber coexist in thin
    transparent washes.
    Vegetation masses (lower left, lower right): deep viridian to dark umber.
    Interior of masses is deep and cool; boundaries are luminous, warm, slightly
    blurred -- the thinned paint has bled slightly along the canvas grain at the
    form/ground boundary.
    Deep lower zone (below 75%): dark earth, umber-to-sienna, where the base of
    the vegetation masses meets the ground plane. The warmest, darkest zone --
    the root-zone of the garden.

Technique & Palette
    Gorky Biomorphic Abstraction mode -- session 269, 180th distinct mode.

    Pipeline:
    1. Procedural reference: amber sky with luminous center-right, viridian
       biomorphic masses left and right, crimson accent shapes, warm ochre earth.
    2. tone_ground: warm cream-ochre (0.92, 0.88, 0.76) -- Gorky's ground
       always shows through the thin paint layers.
    3. underpainting x2: establish the biomorphic masses and sky structure.
    4. block_in x2 (broad and medium): main tonal zones, sky vs earth vs masses.
    5. build_form x2 (medium and fine): organic interior of masses, luminous
       mid-ground, accent shapes.
    6. place_lights: afternoon light catches on foliage edges and earth.
    7. paint_chromatic_vibration_pass (s269 improvement): simultaneous contrast
       vibration at warm-cool boundaries (viridian/crimson, ochre/umber).
    8. gorky_biomorphic_fluid_pass (269, 180th mode): saturation-guided fluid
       washes, dark umber contour lines, warm ground re-exposure, paint bleed.
    9. paint_shadow_bleed_pass: atmospheric shadow bleeding in deep forms.
    10. paint_granulation_pass: organic pigment scatter on the canvas surface.

    Full palette:
    warm-cream (0.92/0.88/0.76) -- deep-viridian (0.14/0.36/0.22) --
    crimson (0.72/0.16/0.18) -- ochre-amber (0.68/0.44/0.10) --
    dark-umber (0.30/0.16/0.08) -- burnt-sienna (0.52/0.32/0.12) --
    yellow-gold (0.82/0.72/0.40) -- dark-indigo (0.18/0.22/0.38) --
    rose-crimson (0.60/0.22/0.28)

Mood & Intent
    The image is intended to convey WARM ORGANIC ABUNDANCE and the melancholy
    sweetness of the remembered garden -- a place that no longer exists except
    in memory and paint. The biomorphic forms should feel alive with organic
    energy while remaining fully abstract: the viewer should sense plant, earth,
    light, and flower without being able to name any specific thing. The
    crimson accents pulse against the viridian masses like remembered flashes of
    colour. The warm cream ground shows through every layer, giving the painting
    its luminous, breathing quality. The viewer should feel the weight of summer
    afternoon light -- unhurried, golden, and already tinged with the melancholy
    of impermanence. This is the feeling of Gorky's Garden in Sochi: a paradise
    of memory, painted with total technical control and total emotional freedom.
"""

import sys
import os
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)

from stroke_engine import Painter

W, H = 1440, 1040
SEED = 269
OUTPUT = os.path.join(REPO, "s269_garden_sochi.png")


def build_reference(w: int, h: int) -> np.ndarray:
    """
    Build a procedural reference for 'Garden at Sochi, Dusk'.
    No figures or animals -- procedural Python only.

    Architecture:
    - Upper zone (top 45%): warm amber-gold sky with luminous center-right
    - Mid-ground (40-65%): warm ochre earth, crimson accent shapes
    - Vegetation masses (lower left, lower right): deep viridian/umber biomorphic
    - Deep lower zone (75-100%): dark umber earth root-zone
    """
    ref = np.zeros((h, w, 3), dtype=np.float32)

    Y, X = np.mgrid[0:h, 0:w]
    y_n = Y.astype(np.float32) / float(h - 1)   # 0 = top, 1 = bottom
    x_n = X.astype(np.float32) / float(w - 1)   # 0 = left, 1 = right

    # ── Luminous sky center (center-right, upper zone) ────────────────────────
    glow_cx, glow_cy = 0.68, 0.22
    glow_dist = np.sqrt(((x_n - glow_cx) * 0.85) ** 2 +
                        ((y_n - glow_cy) * 1.20) ** 2).astype(np.float32)
    glow_field = np.exp(-glow_dist ** 2 / (2.0 * 0.22 ** 2)).astype(np.float32)

    # ── Sky zone (top 50%) ────────────────────────────────────────────────────
    sky_mask = np.clip(1.0 - y_n / 0.50, 0.0, 1.0).astype(np.float32)

    sky_r = (0.96 * glow_field + 0.84 * (1.0 - glow_field)) * sky_mask
    sky_g = (0.80 * glow_field + 0.68 * (1.0 - glow_field)) * sky_mask
    sky_b = (0.32 * glow_field + 0.38 * (1.0 - glow_field)) * sky_mask

    # ── Warm ochre earth mid-ground (38-72%) ──────────────────────────────────
    earth_lo, earth_hi = 0.38, 0.72
    earth_weight = np.clip(
        (y_n - earth_lo) / (earth_hi - earth_lo), 0.0, 1.0
    ) * np.clip(
        1.0 - (y_n - earth_hi) / 0.12, 0.0, 1.0
    )
    earth_weight = earth_weight.astype(np.float32)
    # Center opening in mid-ground (between the vegetation masses)
    center_opening = np.clip(1.0 - np.abs(x_n - 0.50) / 0.38, 0.0, 1.0).astype(np.float32)
    earth_weight *= center_opening

    earth_r = 0.72 * earth_weight
    earth_g = 0.50 * earth_weight
    earth_b = 0.18 * earth_weight

    # ── Left viridian vegetation mass ────────────────────────────────────────
    mass_l_params = [(0.18, 0.62, 0.22, 0.24), (0.10, 0.72, 0.16, 0.20),
                     (0.26, 0.55, 0.18, 0.18)]
    mass_left = np.zeros((h, w), dtype=np.float32)
    for cx_m, cy_m, rx_m, ry_m in mass_l_params:
        d = np.sqrt(((x_n - cx_m) / rx_m) ** 2 + ((y_n - cy_m) / ry_m) ** 2)
        mass_left += np.clip(1.0 - d, 0.0, 1.0).astype(np.float32)
    mass_left = np.clip(mass_left, 0.0, 1.0).astype(np.float32)

    vir_l_r = 0.14 * mass_left
    vir_l_g = 0.34 * mass_left
    vir_l_b = 0.20 * mass_left

    # ── Right viridian vegetation mass ───────────────────────────────────────
    mass_r_params = [(0.82, 0.60, 0.24, 0.22), (0.88, 0.70, 0.18, 0.20),
                     (0.76, 0.52, 0.18, 0.18)]
    mass_right = np.zeros((h, w), dtype=np.float32)
    for cx_m, cy_m, rx_m, ry_m in mass_r_params:
        d = np.sqrt(((x_n - cx_m) / rx_m) ** 2 + ((y_n - cy_m) / ry_m) ** 2)
        mass_right += np.clip(1.0 - d, 0.0, 1.0).astype(np.float32)
    mass_right = np.clip(mass_right, 0.0, 1.0).astype(np.float32)

    vir_r_r = 0.16 * mass_right
    vir_r_g = 0.38 * mass_right
    vir_r_b = 0.22 * mass_right

    # ── Crimson/burgundy accent shapes (3 flower masses) ─────────────────────
    acc_params = [
        (0.40, 0.50, 0.07),   # left-center poppy
        (0.58, 0.44, 0.06),   # center-right accent
        (0.28, 0.42, 0.05),   # left accent
        (0.52, 0.58, 0.06),   # lower center
    ]
    accents = np.zeros((h, w), dtype=np.float32)
    for cx_a, cy_a, r_a in acc_params:
        d = np.sqrt((x_n - cx_a) ** 2 + (y_n - cy_a) ** 2)
        accents += np.exp(-d ** 2 / (2.0 * r_a ** 2)).astype(np.float32)
    accents = np.clip(accents, 0.0, 1.0).astype(np.float32)

    acc_r_val = 0.74 * accents
    acc_g_val = 0.14 * accents
    acc_b_val = 0.16 * accents

    # ── Deep lower earth zone (below 70%) ─────────────────────────────────────
    deep_lo = 0.68
    deep_weight = np.clip((y_n - deep_lo) / (1.0 - deep_lo), 0.0, 1.0).astype(np.float32)
    deep_weight = (deep_weight ** 1.3).astype(np.float32)
    deep_r = 0.36 * deep_weight
    deep_g = 0.22 * deep_weight
    deep_b = 0.10 * deep_weight

    # ── Composite ─────────────────────────────────────────────────────────────
    veg_total = np.clip(mass_left + mass_right, 0.0, 1.0)
    veg_total_r = vir_l_r + vir_r_r
    veg_total_g = vir_l_g + vir_r_g
    veg_total_b = vir_l_b + vir_r_b

    R = np.clip(
        sky_r * (1.0 - veg_total) * (1.0 - accents)
        + earth_r * (1.0 - veg_total) * (1.0 - accents)
        + veg_total_r
        + acc_r_val
        + deep_r,
        0.0, 1.0
    ).astype(np.float32)

    G = np.clip(
        sky_g * (1.0 - veg_total) * (1.0 - accents)
        + earth_g * (1.0 - veg_total) * (1.0 - accents)
        + veg_total_g
        + acc_g_val
        + deep_g,
        0.0, 1.0
    ).astype(np.float32)

    B = np.clip(
        sky_b * (1.0 - veg_total) * (1.0 - accents)
        + earth_b * (1.0 - veg_total) * (1.0 - accents)
        + veg_total_b
        + acc_b_val
        + deep_b,
        0.0, 1.0
    ).astype(np.float32)

    ref[:, :, 0] = R
    ref[:, :, 1] = G
    ref[:, :, 2] = B

    return ref


def main() -> None:
    print("=" * 60)
    print("Session 269 -- Garden at Sochi, Dusk")
    print("Artist: Arshile Gorky (Armenian-American Biomorphic Abstraction)")
    print("Mode: 180th distinct mode -- gorky_biomorphic_fluid_pass")
    print("=" * 60)

    # ── Build reference ────────────────────────────────────────────────────────
    print("\nBuilding procedural reference...")
    ref_f = build_reference(W, H)
    # Painter methods expect uint8 reference (0-255); convert once here.
    ref = (np.clip(ref_f, 0.0, 1.0) * 255).astype(np.uint8)
    ref_img = Image.fromarray(ref, "RGB")

    ref_path = os.path.join(REPO, "s269_reference.png")
    ref_img.save(ref_path)
    print(f"Reference saved: {ref_path}")

    # ── Initialise painter ─────────────────────────────────────────────────────
    print("\nInitialising painter...")
    p = Painter(W, H, seed=SEED)

    # ── Ground: warm cream-ochre (Gorky's characteristic ground) ──────────────
    print("  tone_ground...")
    p.tone_ground((0.92, 0.88, 0.76), texture_strength=0.018)

    # ── Underpainting: establish biomorphic mass structure ────────────────────
    print("  underpainting (mass structure)...")
    p.underpainting(ref, stroke_size=52, n_strokes=230)
    p.underpainting(ref, stroke_size=40, n_strokes=250)

    # ── Block in: main tonal zones ────────────────────────────────────────────
    print("  block_in (broad)...")
    p.block_in(ref, stroke_size=32, n_strokes=450)
    print("  block_in (medium)...")
    p.block_in(ref, stroke_size=18, n_strokes=490)

    # ── Build form: organic interior and mid-ground ───────────────────────────
    print("  build_form (medium)...")
    p.build_form(ref, stroke_size=11, n_strokes=520)
    print("  build_form (fine)...")
    p.build_form(ref, stroke_size=5, n_strokes=400)

    # ── Place lights: afternoon light on foliage edges and earth ──────────────
    print("  place_lights...")
    p.place_lights(ref, stroke_size=4, n_strokes=280)

    # ── s269 improvement: Chromatic Vibration ────────────────────────────────
    print("  paint_chromatic_vibration_pass (s269 improvement)...")
    p.paint_chromatic_vibration_pass(
        vibration_sigma=9.0,
        vibration_strength=0.20,
        boundary_threshold=0.045,
        saturation_boost=0.14,
        noise_seed=SEED,
        opacity=0.72,
    )

    # ── 180th mode: Gorky Biomorphic Fluid ────────────────────────────────────
    print("  gorky_biomorphic_fluid_pass (180th mode)...")
    p.gorky_biomorphic_fluid_pass(
        wash_sigma=7.0,
        wash_strength=0.22,
        contour_threshold=0.07,
        contour_opacity=0.28,
        contour_color=(0.12, 0.08, 0.06),
        bleed_sigma=1.9,
        bleed_opacity=0.20,
        ground_warmth=0.10,
        ground_color=(0.92, 0.82, 0.62),
        noise_seed=SEED,
        opacity=0.82,
    )

    # ── Supporting passes ──────────────────────────────────────────────────────
    print("  paint_shadow_bleed_pass...")
    p.paint_shadow_bleed_pass(
        bleed_sigma=6.0,
        shadow_threshold=0.30,
        opacity=0.55,
    )

    print("  paint_granulation_pass...")
    p.paint_granulation_pass(
        granule_sigma=1.0,
        granule_scale=0.04,
        opacity=0.50,
    )

    # ── Save output ────────────────────────────────────────────────────────────
    print(f"\nSaving output to {OUTPUT}...")
    p.save(OUTPUT)
    print(f"Output saved: {OUTPUT}")
    print("\nSession 269 complete.")


if __name__ == "__main__":
    main()
