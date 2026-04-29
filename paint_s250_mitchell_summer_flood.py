"""
paint_s250_mitchell_summer_flood.py -- Session 250

"Summer Flood, Hudson Valley" -- after Joan Mitchell

Image Description
-----------------
Subject & Composition
    An all-over abstraction in landscape memory, the image Mitchell called a
    "remembered landscape": not the Hudson Valley literally seen, but the
    physical sensation of standing at its edge in midsummer after rain, when
    the river has risen and the fields gone silver-green and the sky pressed
    low with water. No horizon line. No depth cue. The canvas is organised
    from lower-left to upper-right in a diagonal surge of energy, with a zone
    of relative stillness in the lower right and a dense knot of mark
    activity in the upper centre-left.

The Figure (the marks themselves)
    No human figure. The marks ARE the subject. Large circular arc sweeps in
    cobalt and deep violet in the upper field -- arm-arc gestures that follow
    the curve of the shoulder -- surging from lower right to upper left as if
    recording the upward drive of floodwater. Against them: short rapid yellow
    and cadmium marks that cut horizontally, the intensity of summer light
    broken into incident. A zone of viridian and sap green in the lower left
    that sits heavily, like waterlogged fields pressed to the ground. Raw white
    strokes scattered through the centre: the silver glare of water surface.
    A single dark mass in the lower right -- dense near-black and burnt umber
    -- anchoring the composition against the surge: a stand of trees, a
    mud bank, the weight of earth against the flood.

    The marks have emotional states: the blue arcs are urgent, the green mass
    is patient and heavy, the white glare is indifferent, the black anchor is
    still.

The Environment
    No environment outside the marks. The canvas ground is warm off-white
    linen. It shows through in the sparse zones as the breathing space that
    Mitchell always preserved -- the lung of the composition. The background
    does not recede but holds the marks at the surface. All space is flat but
    all space is active: even the unpainted areas carry the memory of the
    marks around them.

Technique & Palette
    Joan Mitchell Gestural Arc mode -- session 250, 161st distinct mode.

    Stage 1, LARGE CIRCULAR ARC GESTURAL MARKS: 30 arc marks are scattered
    across the canvas, each a circular arc segment at a random radius
    (0.18 to 0.52 * min_dim) and arc span (0.6 to 2.1 radians). Each mark
    is rendered by computing minimum distance to the nearest arc point and
    applying a brightness shift within mark_width = 4.5 pixels. The result
    is a field of curved gestural marks that trace the arm-arc movement of
    the painter at full extension, a fundamentally different mark geometry
    from the straight-segment rasters of Basquiat (s249) or the calligraphic
    mega-strokes of Kline (s119).

    Stage 2, WET-SPREAD DIRECTIONAL COLOUR BLEED: In highly saturated zones
    (sat > 0.28), an anisotropic Gaussian blur [sigma_lo=1.4, sigma_hi=3.0]
    simulates wet paint spreading laterally from the mark into adjacent
    ground. The saturation acts as the bleed gate -- only the most intensely
    coloured pixels spread into their neighbours, creating the soft boundary
    between a cobalt arc and the off-white ground that characterises Mitchell's
    wet-into-wet technique.

    Stage 3, MARK DENSITY SATURATION RHYTHM: The arc density field (counting
    arc-mark passes within mark_width of each pixel) drives a saturation
    modulation: dense zones receive +0.24 saturation boost, sparse zones
    receive -0.12 reduction. This creates the characteristic dense-sparse
    alternation of Mitchell's all-over composition -- the breathing rhythm
    between full impasto and bare linen.

    Paint Chromatic Underdark improvement (session 250): The deep near-black
    mass in the lower right receives hue enrichment toward deep indigo-violet
    (dark_hue=0.70), weighted by existing saturation, so even the darkest
    areas carry a hint of deep chromatic life rather than deadening to flat
    black. Shadow clarity lift (clarity_amount=0.20) preserves the texture
    of the dark mark field.

    Palette: Cobalt blue (0.14/0.36/0.72) -- Viridian-deep green (0.22/0.54/0.28) --
    Cadmium yellow (0.92/0.84/0.18) -- Cadmium red-orange (0.82/0.26/0.18) --
    Titanium white/off-linen (0.90/0.88/0.84) -- Near-black (0.14/0.12/0.10) --
    Deep violet (0.68/0.30/0.64) -- Cerulean (0.62/0.80/0.88) --
    Burnt sienna (0.72/0.38/0.22) -- Yellow-green (0.38/0.64/0.30)

Mood & Intent
    Mitchell said: "I carry my landscapes around with me." This painting
    intends the quality of carried landscape -- not a view but a sensation,
    not a document but a physical residue. The surge of blue arcs from lower
    right to upper left is the body's memory of standing at the river's edge
    as the water rose. The green mass is the weight of saturated earth. The
    yellow cuts are the way summer light comes through rain.

    The viewer should feel the physical sensation of being inside weather --
    not watching it but standing inside it -- and the particular emotional
    state Mitchell sought in her paintings: the exhilaration of the body's
    response to natural scale and force.

    Paint with patience and practice, like a true artist.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "s250_mitchell_summer_flood.png"
)
W, H = 600, 780   # portrait format -- 10:13 proportion


def build_reference() -> np.ndarray:
    """
    Synthetic reference for "Summer Flood, Hudson Valley".

    Zone organisation (inspired by Mitchell's all-over abstraction):
      - Off-white linen ground: entire canvas
      - Cobalt/violet upper-left mass: large surging field
      - Viridian green lower-left zone: heavy, waterlogged
      - Yellow/cadmium incident marks: horizontal cuts in the mid-register
      - Raw white glare: centre silver
      - Near-black anchor: lower-right dense mass
      - Cerulean secondary blue: upper-right open field
    """
    rng = np.random.default_rng(250)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Off-white linen ground ────────────────────────────────────────────
    ground = np.array([0.90, 0.88, 0.82])
    for ch in range(3):
        ref[:, :, ch] = ground[ch]
    # Gentle noise for linen texture
    noise = gaussian_filter(
        rng.random((H, W)).astype(np.float32) - 0.5, sigma=6.0
    ) * 0.028
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + noise, 0.0, 1.0)

    def _apply_zone(mask, colour, strength=1.0):
        for ch in range(3):
            ref[:, :, ch] = np.clip(
                ref[:, :, ch] * (1.0 - mask * strength) +
                colour[ch] * mask * strength, 0.0, 1.0
            )

    # ── Cobalt/violet surging field: upper-left to upper-centre ──────────
    # Diagonal gradient: strongest in upper-left, fading toward lower-right
    cobalt_field = np.clip(
        (0.85 - ys) * 1.8 * (0.70 - xs) * 2.0, 0.0, 1.0
    ).astype(np.float32)
    cobalt_field = gaussian_filter(cobalt_field, sigma=40.0)
    cobalt_field = np.clip(cobalt_field * 2.2, 0.0, 0.88)
    cobalt = np.array([0.14, 0.36, 0.72])
    _apply_zone(cobalt_field, cobalt, strength=0.92)

    # Deep violet mixed into upper-left corner
    violet_field = np.clip(
        (0.55 - ys) * 3.0 * (0.45 - xs) * 3.5, 0.0, 1.0
    ).astype(np.float32)
    violet_field = gaussian_filter(violet_field, sigma=30.0)
    violet_field = np.clip(violet_field * 1.8, 0.0, 0.60)
    violet = np.array([0.56, 0.22, 0.62])
    _apply_zone(violet_field, violet, strength=0.72)

    # ── Viridian green: lower-left heavy mass ─────────────────────────────
    green_field = np.clip(
        (ys - 0.52) * 3.2 * (0.55 - xs) * 2.8, 0.0, 1.0
    ).astype(np.float32)
    green_field = gaussian_filter(green_field, sigma=35.0)
    green_field = np.clip(green_field * 1.9, 0.0, 0.80)
    viridian = np.array([0.22, 0.54, 0.28])
    _apply_zone(green_field, viridian, strength=0.88)

    # Yellow-green edge of the green field
    ygreen_field = np.clip(
        (ys - 0.65) * 3.5 * (0.40 - xs) * 3.0 + 0.1, 0.0, 1.0
    ).astype(np.float32)
    ygreen_field = gaussian_filter(ygreen_field, sigma=22.0)
    ygreen_field = np.clip(ygreen_field * 1.4, 0.0, 0.50)
    ygreen = np.array([0.38, 0.64, 0.30])
    _apply_zone(ygreen_field, ygreen, strength=0.60)

    # ── Cadmium yellow horizontal cuts: mid-register ──────────────────────
    # Several horizontal bands of varying density
    yellow = np.array([0.92, 0.84, 0.18])
    for y_centre in [0.34, 0.42, 0.50, 0.58]:
        band_w = float(rng.uniform(0.02, 0.05))
        x_start = float(rng.uniform(0.10, 0.35))
        x_end   = float(rng.uniform(0.55, 0.88))
        band = (
            (np.abs(ys - y_centre) < band_w) &
            (xs >= x_start) & (xs <= x_end)
        ).astype(np.float32)
        band = gaussian_filter(band, sigma=5.0)
        band = np.clip(band * 8.0, 0.0, 0.80) * float(rng.uniform(0.45, 0.85))
        _apply_zone(band, yellow, strength=0.90)

    # Cadmium red-orange incident mark
    cad_red = np.array([0.82, 0.26, 0.18])
    red_band = (
        (np.abs(ys - 0.46) < 0.016) &
        (xs >= 0.52) & (xs <= 0.76)
    ).astype(np.float32)
    red_band = gaussian_filter(red_band, sigma=4.0)
    red_band = np.clip(red_band * 10.0, 0.0, 0.70)
    _apply_zone(red_band, cad_red, strength=0.85)

    # ── Silver-white glare centre ─────────────────────────────────────────
    glare = np.exp(
        -((xs - 0.50) ** 2) / (2 * 0.08 ** 2) -
        ((ys - 0.44) ** 2) / (2 * 0.10 ** 2)
    ).astype(np.float32)
    glare = np.clip(glare * 0.75, 0.0, 0.65)
    white = np.array([0.94, 0.92, 0.90])
    _apply_zone(glare, white, strength=0.80)

    # ── Near-black anchor: lower-right ────────────────────────────────────
    black_field = np.clip(
        (ys - 0.58) * 3.0 * (xs - 0.58) * 2.8, 0.0, 1.0
    ).astype(np.float32)
    black_field = gaussian_filter(black_field, sigma=28.0)
    black_field = np.clip(black_field * 2.0, 0.0, 0.82)
    near_black = np.array([0.14, 0.12, 0.10])
    _apply_zone(black_field, near_black, strength=0.92)

    # Burnt sienna at the near-black boundary
    sienna_field = np.clip(
        (ys - 0.62) * 3.5 * (xs - 0.52) * 3.0 * (0.92 - ys) * 2.5, 0.0, 1.0
    ).astype(np.float32)
    sienna_field = gaussian_filter(sienna_field, sigma=18.0)
    sienna_field = np.clip(sienna_field * 2.5, 0.0, 0.45)
    sienna = np.array([0.72, 0.38, 0.22])
    _apply_zone(sienna_field, sienna, strength=0.65)

    # ── Cerulean upper-right open field ──────────────────────────────────
    cerulean_field = np.clip(
        (0.45 - ys) * 2.5 * (xs - 0.62) * 2.2, 0.0, 1.0
    ).astype(np.float32)
    cerulean_field = gaussian_filter(cerulean_field, sigma=32.0)
    cerulean_field = np.clip(cerulean_field * 1.8, 0.0, 0.55)
    cerulean = np.array([0.62, 0.80, 0.88])
    _apply_zone(cerulean_field, cerulean, strength=0.72)

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'Summer Flood, Hudson Valley' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=250)

    # Ground: warm off-white linen
    p.tone_ground((0.90, 0.86, 0.74), texture_strength=0.016)

    # Underpainting: establish the broad colour fields
    p.underpainting(ref_pil, stroke_size=90)

    # Block in: major colour zones -- cobalt surge, green mass, yellow cuts
    p.block_in(ref_pil, stroke_size=32)

    # Build form: tighten the colour zones and define density contrasts
    p.build_form(ref_pil, stroke_size=16)

    # Place lights: silver glare and yellow incident light
    p.place_lights(ref_pil, stroke_size=8)

    # ── MITCHELL GESTURAL ARC -- session 250, 161st distinct mode ────────

    # First pass: primary arc field -- large, sweeping, diagonal surge
    p.mitchell_gestural_arc_pass(
        n_arcs=30,
        arc_radius_lo=0.18,
        arc_radius_hi=0.52,
        arc_span_lo=0.60,
        arc_span_hi=2.10,
        mark_width=4.5,
        brightness_shift=0.22,
        dark_frac=0.38,
        wet_sat_thresh=0.26,
        wet_sigma_lo=1.4,
        wet_sigma_hi=3.2,
        wet_strength=0.34,
        density_boost=0.24,
        density_reduce=0.12,
        opacity=0.82,
        seed=250,
    )

    # Second pass: finer arc field -- shorter, more fragmented incident marks
    p.mitchell_gestural_arc_pass(
        n_arcs=18,
        arc_radius_lo=0.08,
        arc_radius_hi=0.24,
        arc_span_lo=0.40,
        arc_span_hi=1.20,
        mark_width=2.8,
        brightness_shift=0.14,
        dark_frac=0.50,
        wet_sat_thresh=0.35,
        wet_sigma_lo=0.8,
        wet_sigma_hi=2.0,
        wet_strength=0.22,
        density_boost=0.16,
        density_reduce=0.08,
        opacity=0.45,
        seed=500,
    )

    # ── PAINT CHROMATIC UNDERDARK -- session 250 improvement ─────────────
    # Enrich the near-black anchor zone with deep indigo-violet
    p.paint_chromatic_underdark_pass(
        shadow_thresh=0.30,
        shadow_fade=0.14,
        dark_hue=0.70,
        dark_strength=0.40,
        clarity_sigma=1.6,
        clarity_amount=0.20,
        opacity=0.50,
    )

    # Final vignette: darken edges slightly to focus the surge
    p.focal_vignette_pass(vignette_strength=0.26, opacity=0.40)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
