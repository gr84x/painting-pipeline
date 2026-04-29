"""
paint_s248_stael_harbor_agrigento.py -- Session 248

"Harbor at Agrigento, Dusk" -- after Nicolas de Stael

Image Description
-----------------
Subject & Composition
    Three fishing boats moored side by side at a Sicilian harbour quay, seen
    from dock level at a slight low angle, looking across the boats toward the
    open sea beyond the harbour mouth. The composition is wide and horizontal,
    divided into strong bands: burning cobalt-to-orange sky above, a
    simplified horizontal quay wall of ochre limestone in the middle, the
    dark sea-green water below — and the three boat hulls as the dominant
    vertical forms bisecting the horizon. A single tall mast rises from the
    centre boat, thin and dark, the only vertical element that crosses from
    the water zone into the sky.

The Figures (Boats)
    Left boat: a broad low wooden hull of burnt sienna-red, streaked with
    weathering and salt. Solid, heavy. Rounded at the bow. A short white-
    cream superstructure forward. Sitting low in the water: its own dark
    reflection stretches directly below it in the harbour.
    Centre boat: slightly larger. A weathered steel-blue hull — pale cobalt
    grey, the blue of Mediterranean shadow in the afternoon. Its cabin is
    cream-white, cube-like. A tall slim mast rises from the cabin roof, dark
    navy, reaching into the orange sky zone. The centre boat's hull is the
    compositional anchor.
    Right boat: a warm ochre-yellow hull — the yellow of Sicilian limestone
    and dry summer grass. Lower and flatter than its neighbours. No cabin
    visible, just the broad plane of its deck and hull.
    The boats are simplified geometric shapes — three strong rectangles of
    colour, each with its own palette, pressed together at the quay edge.
    Mood of the boats: patient, heavy, at rest; the industry of the day
    completed.

The Environment
    Sky: deep cobalt blue at the zenith, transitioning through indigo and rich
    violet to a burning band of cadmium-orange at the horizon. The transition
    is the sky at the exact moment before the sun disappears — the last full
    energy of dusk. The orange band is wide, maybe one-quarter of the sky zone.
    A faint warm blush of rose-gold near the horizon where sky meets water.
    Quay wall: a simple horizontal band of ochre Sicilian limestone — warm,
    slightly textured, the stone worn smooth by ropes and time. It forms a
    clean dividing line between the sky and the water at about one-third up
    from the bottom of the canvas.
    Water: the inner harbour water is dark sea-green, nearly still. It holds
    pale reflections of the cobalt sky above and warm streaks of orange from
    the dusk light. The reflections of the three boat hulls — red, blue,
    ochre — run as bold vertical bands down from the waterline.

Technique & Palette
    Nicolas de Stael Palette Knife Mosaic mode -- session 248, 159th distinct
    mode. Stage 1 TILE MEAN QUANTIZATION: the canvas is divided into
    rectangular tiles (24x32 pixels). Each tile becomes a single flat colour
    plane carrying its mean hue and value, flattening the scene into bold
    abstract planes in the manner of de Stael's 1952-1954 harbour work.
    Stage 2 INTRA-TILE KNIFE GRADIENT at 12 degrees: within each tile, a
    slight directional luminance gradient simulates the palette knife drag
    direction. Stage 3 TILE BOUNDARY GAP DARKENING: thin dark lines at tile
    boundaries simulate the trough left where the knife lifts between deposits.
    Paint Halation improvement: warm orange bloom from the bright sky band
    bleeds softly into the surrounding cobalt, simulating the dusk halation
    effect.

    Palette: Burnt sienna-orange (sky band, red hull) -- Cobalt blue (upper
    sky, blue hull, deep water) -- Raw ochre-yellow (quay stone, yellow hull,
    sunlight) -- Brick-red (left boat hull, harbour wall) -- Slate blue-grey
    (water, weathered hull) -- Cream-white (superstructure, bright sky) --
    Amber gold (dusk reflection, water) -- Deep sea-green (harbour depth)

Mood & Intent
    This painting attempts what de Stael achieved in his Mediterranean
    harbour paintings of 1953-1954: the reduction of a specific, luminous
    scene to its essential colour geometry. Not the boats as boats, but the
    boats as three coloured rectangles standing against the burning sky. The
    composition is about the relationship between those three colour planes
    and the horizontal bands of sky, stone, and water that contain them.

    The mood is the particular richness of a Mediterranean summer evening --
    the moment when the light has become so saturated with orange that every
    surface it touches becomes more intensely itself: the red hull redder,
    the blue hull more deeply blue, the ochre stone more golden. The harbour
    is emptying. The day's work is done. The water is still. The mast is
    the only vertical ambition left in the frame.

    The viewer should feel the fullness of colour -- not the sadness of the
    end of the day, but its completeness. De Stael was not a melancholy
    painter. He was a painter who believed that a single decisive colour block
    could contain everything that needed to be said.

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
    "s248_stael_harbor_agrigento.png"
)
W, H = 960, 720   # wide landscape — horizontal bands, Mediterranean proportion


def build_reference() -> np.ndarray:
    """
    Synthetic reference for "Harbor at Agrigento, Dusk".

    Tonal/colour zones (top to bottom):
      - Sky upper zone (0 to 0.38): deep cobalt blue
      - Sky lower / dusk band (0.38 to 0.55): burning cadmium orange to amber
      - Quay wall (0.55 to 0.62): ochre limestone band
      - Water / harbour (0.62 to 1.0): dark sea-green with reflections
      - Left boat hull (burnt red): columns roughly 0.08 to 0.32
      - Centre boat hull (blue-grey): columns roughly 0.37 to 0.62
      - Right boat hull (ochre-yellow): columns roughly 0.67 to 0.90
      - Boat reflections in water: same colours, blurred vertically below waterline
    """
    rng = np.random.default_rng(248)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys  = np.linspace(0.0, 1.0, H)[:, None]
    xs  = np.linspace(0.0, 1.0, W)[None, :]

    # ── Sky: cobalt upper zone ────────────────────────────────────────────────
    sky_top   = np.array([0.16, 0.22, 0.72])   # deep cobalt at zenith
    sky_mid   = np.array([0.24, 0.28, 0.60])   # slightly lighter cobalt
    horizon_y = 0.55   # top of quay wall

    sky_frac = np.clip(ys / horizon_y, 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = sky_top[ch] * (1.0 - sky_frac) + sky_mid[ch] * sky_frac

    # ── Dusk band: orange-amber near horizon (upper portion of horizon) ───────
    dusk_lo   = 0.30   # start of orange band (y fraction)
    dusk_hi   = 0.55   # end of orange band (top of quay)
    dusk_c    = np.array([0.92, 0.52, 0.14])   # rich cadmium orange
    blush_c   = np.array([0.88, 0.64, 0.36])   # softer amber-gold lower dusk

    dusk_mask = np.clip((ys - dusk_lo) / max(dusk_hi - dusk_lo, 0.01), 0.0, 1.0)
    dusk_mask = np.where(ys < dusk_hi, dusk_mask, 0.0)
    for ch in range(3):
        col = dusk_c[ch] * (1.0 - dusk_mask * 0.5) + blush_c[ch] * dusk_mask * 0.5
        ref[:, :, ch] = ref[:, :, ch] * (1.0 - dusk_mask) + col * dusk_mask

    # Slight noise in sky
    sky_n = gaussian_filter(rng.random((H, W)).astype(np.float32) - 0.5, sigma=20.0) * 0.025
    sky_zone = np.where(ys < horizon_y, 1.0, 0.0)
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + sky_n * sky_zone, 0.0, 1.0)

    # ── Quay wall: ochre limestone band ──────────────────────────────────────
    quay_lo  = 0.55
    quay_hi  = 0.63
    quay_c   = np.array([0.78, 0.66, 0.42])   # warm Sicilian limestone ochre
    quay_m   = np.clip((ys - quay_lo) / (quay_hi - quay_lo), 0.0, 1.0)
    quay_mask = np.where((ys >= quay_lo) & (ys < quay_hi), 1.0, 0.0)
    quay_noise = gaussian_filter(rng.random((H, W)).astype(np.float32) - 0.5, sigma=4.0) * 0.04
    for ch in range(3):
        ref[:, :, ch] = (ref[:, :, ch] * (1.0 - quay_mask) +
                        np.clip(quay_c[ch] + quay_noise, 0.0, 1.0) * quay_mask)

    # ── Water: dark sea-green with orange dusk reflection ────────────────────
    water_lo  = 0.63
    water_top = np.array([0.14, 0.26, 0.32])   # dark sea-green near surface
    water_dep = np.array([0.08, 0.14, 0.20])   # darker near-black deeper water
    water_f   = np.clip((ys - water_lo) / (1.0 - water_lo + 1e-7), 0.0, 1.0)
    water_mask = np.where(ys >= water_lo, 1.0, 0.0)
    for ch in range(3):
        wc = water_top[ch] * (1.0 - water_f) + water_dep[ch] * water_f
        ref[:, :, ch] = ref[:, :, ch] * (1.0 - water_mask) + wc * water_mask

    # Horizontal shimmer in water
    water_n = gaussian_filter(
        rng.random((H, W)).astype(np.float32) - 0.5, sigma=(2.0, 10.0)
    ) * 0.05
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + water_n * water_mask, 0.0, 1.0)

    # Orange sky reflection in water (a warm vertical band across water centre)
    refl_cx   = 0.50
    refl_w    = 0.50
    refl_mask = np.clip(1.0 - np.abs(xs - refl_cx) / (refl_w * 0.5), 0.0, 1.0) * water_mask
    orange_refl = np.array([0.52, 0.34, 0.10])
    for ch in range(3):
        ref[:, :, ch] = np.clip(
            ref[:, :, ch] + orange_refl[ch] * refl_mask * 0.25, 0.0, 1.0
        )

    # ── Left boat: burnt sienna-red hull ─────────────────────────────────────
    b1_xl  = 0.08
    b1_xr  = 0.30
    b1_yt  = 0.44   # hull top (above quay, sitting in water/quay zone)
    b1_yb  = 0.78   # hull bottom (in water)
    hull1_c = np.array([0.72, 0.28, 0.14])   # burnt sienna-red

    b1_mask_y = np.where((ys >= b1_yt) & (ys < b1_yb), 1.0, 0.0)
    b1_mask_x = np.where((xs >= b1_xl) & (xs < b1_xr), 1.0, 0.0)
    b1_mask   = b1_mask_y * b1_mask_x

    # Rounded bow: hull tapers at left end
    bow_taper = np.clip((xs - b1_xl) / 0.04, 0.0, 1.0) if True else 1.0
    bow_taper = np.clip((xs - b1_xl) / 0.04, 0.0, 1.0)
    b1_mask   = b1_mask * np.clip(bow_taper + 0.6, 0.0, 1.0)

    # Hull shadow: slightly darker lower two-thirds
    hull1_shadow = np.where(ys > (b1_yt + b1_yb) * 0.5, 0.12, 0.0) * b1_mask
    for ch in range(3):
        ref[:, :, ch] = (ref[:, :, ch] * (1.0 - b1_mask) +
                        np.clip(hull1_c[ch] - hull1_shadow, 0.0, 1.0) * b1_mask)

    # Left boat superstructure: cream-white box forward
    s1_xl = b1_xl + 0.02
    s1_xr = b1_xl + 0.11
    s1_yt = b1_yt - 0.04
    s1_yb = b1_yt + 0.03
    s1_mask = (np.where((ys >= s1_yt) & (ys < s1_yb), 1.0, 0.0) *
               np.where((xs >= s1_xl) & (xs < s1_xr), 1.0, 0.0))
    super1_c = np.array([0.90, 0.86, 0.76])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1.0 - s1_mask) + super1_c[ch] * s1_mask

    # ── Centre boat: weathered blue-grey hull ─────────────────────────────────
    b2_xl  = 0.35
    b2_xr  = 0.62
    b2_yt  = 0.43
    b2_yb  = 0.80
    hull2_c = np.array([0.36, 0.50, 0.68])   # steel blue-grey, worn cobalt

    b2_mask = (np.where((ys >= b2_yt) & (ys < b2_yb), 1.0, 0.0) *
               np.where((xs >= b2_xl) & (xs < b2_xr), 1.0, 0.0))

    hull2_shadow = np.where(ys > (b2_yt + b2_yb) * 0.5, 0.10, 0.0) * b2_mask
    for ch in range(3):
        ref[:, :, ch] = (ref[:, :, ch] * (1.0 - b2_mask) +
                        np.clip(hull2_c[ch] - hull2_shadow, 0.0, 1.0) * b2_mask)

    # Centre boat cabin: cream-white cube
    c2_xl = (b2_xl + b2_xr) * 0.5 - 0.06
    c2_xr = (b2_xl + b2_xr) * 0.5 + 0.06
    c2_yt = b2_yt - 0.06
    c2_yb = b2_yt + 0.02
    c2_mask = (np.where((ys >= c2_yt) & (ys < c2_yb), 1.0, 0.0) *
               np.where((xs >= c2_xl) & (xs < c2_xr), 1.0, 0.0))
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1.0 - c2_mask) + super1_c[ch] * c2_mask

    # Mast: thin dark vertical from cabin to sky
    mast_x  = (b2_xl + b2_xr) * 0.5 + 0.01
    mast_yt = 0.12
    mast_yb = c2_yt
    mast_w  = 0.004
    mast_mask = (np.where((ys >= mast_yt) & (ys < mast_yb), 1.0, 0.0) *
                 np.clip(1.0 - np.abs(xs - mast_x) / mast_w, 0.0, 1.0) ** 2.0)
    mast_c = np.array([0.10, 0.12, 0.18])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1.0 - mast_mask) + mast_c[ch] * mast_mask

    # ── Right boat: warm ochre-yellow hull ────────────────────────────────────
    b3_xl  = 0.66
    b3_xr  = 0.90
    b3_yt  = 0.46
    b3_yb  = 0.76
    hull3_c = np.array([0.84, 0.72, 0.28])   # raw ochre-yellow, warm limestone

    b3_mask = (np.where((ys >= b3_yt) & (ys < b3_yb), 1.0, 0.0) *
               np.where((xs >= b3_xl) & (xs < b3_xr), 1.0, 0.0))

    hull3_shadow = np.where(ys > (b3_yt + b3_yb) * 0.5, 0.09, 0.0) * b3_mask
    for ch in range(3):
        ref[:, :, ch] = (ref[:, :, ch] * (1.0 - b3_mask) +
                        np.clip(hull3_c[ch] - hull3_shadow, 0.0, 1.0) * b3_mask)

    # ── Hull reflections in water ─────────────────────────────────────────────
    for (hull_xl, hull_xr, hull_yb, hull_col, ref_strength) in [
        (b1_xl, b1_xr, b1_yb, hull1_c, 0.55),
        (b2_xl, b2_xr, b2_yb, hull2_c, 0.50),
        (b3_xl, b3_xr, b3_yb, hull3_c, 0.45),
    ]:
        refl_yt = hull_yb
        refl_yb = min(1.0, hull_yb + 0.16)
        rx_mask = np.where((xs >= hull_xl) & (xs < hull_xr), 1.0, 0.0)
        # Reflection fades with depth
        ry_frac = np.clip((ys - refl_yt) / max(refl_yb - refl_yt, 0.01), 0.0, 1.0)
        ry_fade = (1.0 - ry_frac) * ref_strength
        ry_mask = np.where((ys >= refl_yt) & (ys < refl_yb), ry_fade, 0.0)
        refl_overall = rx_mask * ry_mask
        for ch in range(3):
            ref[:, :, ch] = np.clip(
                ref[:, :, ch] * (1.0 - refl_overall * 0.7) +
                hull_col[ch] * refl_overall * 0.7,
                0.0, 1.0
            )

    # Apply slight vertical Gaussian blur to reflections in water (wavering)
    water_region_r = ref[int(H * 0.63):, :, 0]
    water_region_g = ref[int(H * 0.63):, :, 1]
    water_region_b = ref[int(H * 0.63):, :, 2]
    ref[int(H * 0.63):, :, 0] = gaussian_filter(water_region_r, sigma=(3.0, 1.5))
    ref[int(H * 0.63):, :, 1] = gaussian_filter(water_region_g, sigma=(3.0, 1.5))
    ref[int(H * 0.63):, :, 2] = gaussian_filter(water_region_b, sigma=(3.0, 1.5))

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'Harbor at Agrigento, Dusk' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=248)

    # Ground: warm burnt sienna-orange — the colour of Sicilian earth in late light
    p.tone_ground((0.82, 0.52, 0.20), texture_strength=0.020)

    # Underpainting: establish sky/water/quay/boat colour masses
    p.underpainting(ref_pil, stroke_size=80)

    # Block in: define the three boat hulls and horizontal bands
    p.block_in(ref_pil, stroke_size=32)

    # Build form: boat contours, mast, superstructure, quay edge
    p.build_form(ref_pil, stroke_size=16)

    # Lights: dusk light on cabin tops, orange reflections in water
    p.place_lights(ref_pil, stroke_size=7)

    # ── DE STAEL PALETTE KNIFE MOSAIC — session 248, 159th distinct mode ──────
    # First pass: bold tile quantization, strong knife texture, clear boundary gaps
    p.de_stael_palette_knife_mosaic_pass(
        tile_h=24,
        tile_w=32,
        knife_angle_deg=12.0,      # slight tilt, like a horizontal knife pass
        knife_texture_str=0.065,
        boundary_width=2,
        boundary_strength=0.20,
        opacity=0.88,
    )

    # Second pass: finer tiles to preserve boat/sky distinction within each zone
    p.de_stael_palette_knife_mosaic_pass(
        tile_h=12,
        tile_w=16,
        knife_angle_deg=168.0,     # nearly horizontal, opposed direction
        knife_texture_str=0.035,
        boundary_width=1,
        boundary_strength=0.10,
        opacity=0.40,
    )

    # ── PAINT HALATION — session 248 improvement ──────────────────────────────
    # Warm orange bloom from bright dusk sky band bleeds into surrounding cobalt
    p.paint_halation_pass(
        halation_thresh=0.72,
        halation_sigma=18.0,
        tint_r=1.00,
        tint_g=0.65,
        tint_b=0.22,
        bloom_strength=0.22,
        opacity=0.50,
    )

    # Final vignette: deepen the corners, focus on the boat forms
    p.focal_vignette_pass(vignette_strength=0.28, opacity=0.45)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
