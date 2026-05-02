"""Session 284 -- George Grosz (195th mode)
grosz_neue_sachlichkeit_pass + paint_chromatic_shadow_shift_pass

Subject & Composition:
    "Weimar Night -- Berlin Industrial District, 1923" -- a compressed, harsh
    cityscape of a Berlin industrial quarter at night, viewed from street level.
    Three tall factory chimneys rise against a sodium-lit sky. An angular
    tenement block with harsh lit windows fills the right. A solitary lamplit
    cobblestone street recedes into the distance. The composition is vertical
    and claustrophobic in the New Objectivity mode.

The Figure:
    No single human figure is present, but the built environment reads as a
    social figure: the chimneys are the workers, the tenement is the cramped
    existence of the proletariat, the empty street is the midnight of the
    Weimar Republic.

The Environment:
    SKY: A thick, poisonous-orange sodium glow from below meets a sickly
    grey-green overcast above. The sky has no stars, no open space -- it is
    a lid pressing down on the city. Wisps of industrial smoke drift across
    the orange zone.

    CHIMNEYS AND FACTORY: Three brick chimneys rise from mid-left to center,
    their tops cut off by the frame. The factory wall below them is a nearly
    flat dark mass with a few small lit windows -- rectangles of acid yellow
    light. The factory is rendered in flat, graphic masses consistent with
    Grosz's poster-like spatial treatment.

    STREET: The cobblestone street cuts diagonally from the lower-left to a
    vanishing point at mid-center. The cobblestones are dark, wet, reflecting
    the single streetlamp's orange cone. The perspective is compressed, the
    recession exaggerated, consistent with New Objectivity's flattened spatial
    tension.

    TENEMENT BLOCK: A tenement block on the right has sharp, angular windows --
    some lit (acid yellow-white), most dark. The facade is rendered with Grosz's
    flat-zone technique: minimal tonal variation within the wall plane.

Technique & Palette:
    George Grosz's Neue Sachlichkeit mode. Palette: near-black for heavy contour
    shadows; acid yellow-green for the sickly sodium sky glow; cadmium vermillion
    accents at the chimney tops and lit windows; prussian blue for the deepest
    night shadows; warm ochre-buff for the street surface. The grosz_neue_
    sachlichkeit_pass enforces directional cast shadows from upper-left, flat
    interior zones, acid colour push in green-dominant areas, and gamma-expanded
    mid-tones.

Mood & Intent:
    The image is meant to convey the oppressive weight of industrialism and the
    dehumanising architecture of poverty -- a Marxist reading of urban space
    rendered with aesthetic precision. The viewer should feel claustrophobia,
    a sense of being watched (by the lit windows), and the particular Grosz
    quality of social anger transmuted into aesthetic severity. The absence of
    figures is itself political: the city has become a machine, the workers
    absorbed into its mechanical rhythm. The palette -- acid, sickly, lit from
    below -- models the moral atmosphere of the Weimar period.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stroke_engine import Painter

# ── Canvas dimensions ────────────────────────────────────────────────────────
W, H = 1040, 1440   # portrait -- Grosz's vertical, claustrophobic format
SEED = 284

# ── Reference: procedural Weimar Berlin industrial night scene ────────────────

def build_reference() -> np.ndarray:
    """Construct a compressed Berlin industrial district night reference."""
    rng = np.random.default_rng(SEED)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    ys = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    xs = np.linspace(0.0, 1.0, W, dtype=np.float32)[None, :]

    # ── Sky (upper 40%) ───────────────────────────────────────────────────────
    sky_zone_bottom = 0.40
    sky_z = ys < sky_zone_bottom

    # Sodium glow base: sickly green-orange gradient
    sky_r = np.clip(0.36 + ys * 0.55 * (sky_zone_bottom - ys) / (sky_zone_bottom ** 2 + 0.01), 0.0, 1.0)
    sky_g = np.clip(0.28 + ys * 0.45 * (sky_zone_bottom - ys) / (sky_zone_bottom ** 2 + 0.01), 0.0, 1.0)
    sky_b = np.clip(0.06 + ys * 0.10, 0.0, 1.0)

    # Upper sky: grey-green overcast oppressive lid
    upper_fade = np.clip((sky_zone_bottom * 0.4 - ys) / (sky_zone_bottom * 0.4 + 0.01), 0.0, 1.0)
    sky_r = np.clip(sky_r * (1 - upper_fade) + 0.22 * upper_fade, 0.0, 1.0)
    sky_g = np.clip(sky_g * (1 - upper_fade) + 0.26 * upper_fade, 0.0, 1.0)
    sky_b = np.clip(sky_b * (1 - upper_fade) + 0.14 * upper_fade, 0.0, 1.0)

    # Industrial smoke wisps
    smoke_rng = np.random.default_rng(SEED + 1)
    from scipy.ndimage import gaussian_filter as gf
    smoke_noise = smoke_rng.random((H, W)).astype(np.float32)
    smoke_base = gf(smoke_noise, sigma=[8, 30])
    smoke_mask = np.clip(smoke_base - 0.58, 0.0, 1.0) * sky_z.astype(np.float32)
    smoke_mask = smoke_mask.astype(np.float32)
    sky_r = np.clip(sky_r + smoke_mask * 0.10, 0.0, 1.0)
    sky_g = np.clip(sky_g + smoke_mask * 0.10, 0.0, 1.0)
    sky_b = np.clip(sky_b + smoke_mask * 0.08, 0.0, 1.0)

    ref[:, :, 0] = np.where(sky_z, sky_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(sky_z, sky_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(sky_z, sky_b, ref[:, :, 2])

    # ── Factory building with chimneys (left 60%) ─────────────────────────────
    factory_top_y  = int(0.25 * H)
    factory_bot_y  = int(0.72 * H)
    factory_left_x = 0
    factory_right_x = int(0.60 * W)

    # Factory wall: flat dark ochre-grey with slight texture
    fact_noise = gf(np.random.default_rng(SEED + 2).random((H, W)).astype(np.float32), sigma=3)
    fact_r = np.clip(0.22 + fact_noise * 0.08, 0.0, 1.0)
    fact_g = np.clip(0.20 + fact_noise * 0.06, 0.0, 1.0)
    fact_b = np.clip(0.14 + fact_noise * 0.04, 0.0, 1.0)

    fact_zone = (
        (ys >= factory_top_y / H) & (ys < factory_bot_y / H) &
        (xs >= factory_left_x / W) & (xs < factory_right_x / W)
    )
    ref[:, :, 0] = np.where(fact_zone, fact_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(fact_zone, fact_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(fact_zone, fact_b, ref[:, :, 2])

    # Factory windows: acid yellow rectangles
    for (wy0, wy1, wx0, wx1) in [
        (0.32, 0.36, 0.08, 0.14), (0.32, 0.36, 0.20, 0.26),
        (0.32, 0.36, 0.32, 0.38), (0.32, 0.36, 0.44, 0.50),
        (0.42, 0.46, 0.10, 0.16), (0.42, 0.46, 0.28, 0.34),
        (0.52, 0.56, 0.06, 0.12), (0.52, 0.56, 0.38, 0.44),
        (0.62, 0.66, 0.16, 0.22), (0.62, 0.66, 0.46, 0.52),
    ]:
        ry0, ry1 = int(wy0 * H), int(wy1 * H)
        rx0, rx1 = int(wx0 * W), int(wx1 * W)
        ref[ry0:ry1, rx0:rx1, 0] = 0.82
        ref[ry0:ry1, rx0:rx1, 1] = 0.86
        ref[ry0:ry1, rx0:rx1, 2] = 0.12

    # Three chimneys: dark cylinders rising from factory
    for (cx_frac, cy_top, cy_bot, cw) in [
        (0.12, 0.04, 0.35, 0.040),
        (0.28, 0.06, 0.30, 0.036),
        (0.44, 0.09, 0.33, 0.030),
    ]:
        cx0 = int((cx_frac - cw / 2) * W)
        cx1 = int((cx_frac + cw / 2) * W)
        cy0 = int(cy_top * H)
        cy1 = int(cy_bot * H)
        cx0, cx1 = max(0, cx0), min(W, cx1)
        cy0, cy1 = max(0, cy0), min(H, cy1)
        # Chimney colour: dark red-brick
        ref[cy0:cy1, cx0:cx1, 0] = 0.28
        ref[cy0:cy1, cx0:cx1, 1] = 0.16
        ref[cy0:cy1, cx0:cx1, 2] = 0.10
        # Chimney cap glow: red-orange at top
        cap_h = max(2, int(0.02 * H))
        ref[cy0:cy0 + cap_h, cx0:cx1, 0] = 0.78
        ref[cy0:cy0 + cap_h, cx0:cx1, 1] = 0.22
        ref[cy0:cy0 + cap_h, cx0:cx1, 2] = 0.06

    # ── Tenement block (right 40%) ────────────────────────────────────────────
    ten_top_y   = int(0.18 * H)
    ten_bot_y   = int(0.78 * H)
    ten_left_x  = int(0.58 * W)
    ten_right_x = W

    ten_noise = gf(np.random.default_rng(SEED + 3).random((H, W)).astype(np.float32), sigma=4)
    ten_r = np.clip(0.30 + ten_noise * 0.10, 0.0, 1.0)
    ten_g = np.clip(0.26 + ten_noise * 0.08, 0.0, 1.0)
    ten_b = np.clip(0.20 + ten_noise * 0.06, 0.0, 1.0)

    ten_zone = (
        (ys >= ten_top_y / H) & (ys < ten_bot_y / H) &
        (xs >= ten_left_x / W) & (xs < 1.0)
    )
    ref[:, :, 0] = np.where(ten_zone, ten_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(ten_zone, ten_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(ten_zone, ten_b, ref[:, :, 2])

    # Tenement windows (mostly dark, some lit)
    for row_i, (wy0f, wy1f) in enumerate(
        [(0.22, 0.26), (0.30, 0.34), (0.38, 0.42), (0.46, 0.50),
         (0.54, 0.58), (0.62, 0.66), (0.70, 0.74)]
    ):
        for col_i, (wx0f, wx1f) in enumerate(
            [(0.62, 0.67), (0.70, 0.75), (0.78, 0.83), (0.86, 0.91)]
        ):
            ry0, ry1 = int(wy0f * H), int(wy1f * H)
            rx0, rx1 = int(wx0f * W), int(wx1f * W)
            # Only some windows lit (deterministic selection)
            lit = ((row_i * 4 + col_i) % 5) in {0, 2}
            if lit:
                ref[ry0:ry1, rx0:rx1, 0] = 0.78
                ref[ry0:ry1, rx0:rx1, 1] = 0.82
                ref[ry0:ry1, rx0:rx1, 2] = 0.10
            else:
                ref[ry0:ry1, rx0:rx1, 0] = 0.06
                ref[ry0:ry1, rx0:rx1, 1] = 0.05
                ref[ry0:ry1, rx0:rx1, 2] = 0.04

    # ── Street (lower ~30%) ───────────────────────────────────────────────────
    street_top_y = int(0.70 * H)
    street_bot_y = H

    # Cobblestone street: dark, wet, with reflected sodium glow
    st_noise = gf(np.random.default_rng(SEED + 4).random((H, W)).astype(np.float32), sigma=2)
    cobble = gf(np.random.default_rng(SEED + 5).random((H, W)).astype(np.float32), sigma=5)
    cobble = np.clip(cobble - 0.42, 0.0, 1.0)

    # Base street colour: very dark warm grey
    st_r = np.clip(0.14 + st_noise * 0.10 + cobble * 0.08, 0.0, 1.0)
    st_g = np.clip(0.12 + st_noise * 0.08 + cobble * 0.06, 0.0, 1.0)
    st_b = np.clip(0.08 + st_noise * 0.06 + cobble * 0.04, 0.0, 1.0)

    # Streetlamp cone: a sodium yellow-orange cone at mid-x, pointing downward
    lamp_x = 0.35
    lamp_y_start = 0.72
    lamp_sigma_x = 0.10
    lamp_dist_x = _xs = np.abs(xs - lamp_x)
    lamp_dist_y = np.clip(ys - lamp_y_start, 0.0, 1.0)
    lamp_cone = np.exp(-0.5 * (lamp_dist_x / (lamp_sigma_x + lamp_dist_y * 0.20)) ** 2)
    lamp_cone = lamp_cone * np.clip(lamp_dist_y * 4.0, 0.0, 1.0)
    lamp_cone = lamp_cone.astype(np.float32)

    st_r = np.clip(st_r + lamp_cone * 0.52, 0.0, 1.0)
    st_g = np.clip(st_g + lamp_cone * 0.44, 0.0, 1.0)
    st_b = np.clip(st_b + lamp_cone * 0.04, 0.0, 1.0)

    street_zone = ys >= (street_top_y / H)
    ref[:, :, 0] = np.where(street_zone, st_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(street_zone, st_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(street_zone, st_b, ref[:, :, 2])

    # Streetlamp post
    lp_x0 = int((lamp_x - 0.008) * W)
    lp_x1 = int((lamp_x + 0.008) * W)
    lp_y0 = int(0.62 * H)
    lp_y1 = int(0.95 * H)
    ref[lp_y0:lp_y1, lp_x0:lp_x1, 0] = 0.18
    ref[lp_y0:lp_y1, lp_x0:lp_x1, 1] = 0.16
    ref[lp_y0:lp_y1, lp_x0:lp_x1, 2] = 0.12

    # Streetlamp globe
    lg_cx = int(lamp_x * W)
    lg_cy = int(0.62 * H)
    lg_r  = int(0.018 * W)
    Y, X = np.ogrid[:H, :W]
    dist = np.sqrt((X - lg_cx) ** 2 + (Y - lg_cy) ** 2)
    globe_mask = dist < lg_r
    ref[globe_mask, 0] = 0.94
    ref[globe_mask, 1] = 0.90
    ref[globe_mask, 2] = 0.52

    # Horizon / ground plane transition
    ground_top = int(0.68 * H)
    ground_bot = int(0.72 * H)
    for row in range(ground_top, ground_bot):
        t = (row - ground_top) / max(ground_bot - ground_top - 1, 1)
        ref[row, :, 0] = np.clip(ref[row, :, 0] * (1 - t) + 0.08 * t, 0.0, 1.0)
        ref[row, :, 1] = np.clip(ref[row, :, 1] * (1 - t) + 0.06 * t, 0.0, 1.0)
        ref[row, :, 2] = np.clip(ref[row, :, 2] * (1 - t) + 0.04 * t, 0.0, 1.0)

    ref = np.clip(ref, 0.0, 1.0)
    return ref


# ── Build reference ───────────────────────────────────────────────────────────
print("Building procedural reference...")
ref = build_reference()

ref_uint8 = (ref * 255).astype(np.uint8)
Image.fromarray(ref_uint8).save("s284_reference.png")
print("Reference saved: s284_reference.png")

# ── Painting pipeline ─────────────────────────────────────────────────────────
print("Initialising painter...")
p = Painter(W, H, seed=SEED)

ref_u8 = (ref * 255).astype(np.uint8)

# Ground: warm raw umber (Grosz's toned support)
print("Tone ground...")
p.tone_ground(color=(0.36, 0.28, 0.18), texture_strength=0.020)

# Underpainting: establish tonal structure
print("Underpainting...")
p.underpainting(ref_u8, stroke_size=52, n_strokes=240, dry_amount=0.62)

# Block in: broad masses
print("Block in (broad)...")
p.block_in(ref_u8, stroke_size=30, n_strokes=440, dry_amount=0.52)
print("Block in (medium)...")
p.block_in(ref_u8, stroke_size=18, n_strokes=480, dry_amount=0.48)

# Build form: modelling
print("Build form (medium)...")
p.build_form(ref_u8, stroke_size=11, n_strokes=520, dry_amount=0.44)
print("Build form (fine)...")
p.build_form(ref_u8, stroke_size=5,  n_strokes=420, dry_amount=0.38)

# Place lights: highlights and accents
print("Place lights...")
p.place_lights(ref_u8, stroke_size=4, n_strokes=280)

# ── s284 improvement: Chromatic Shadow Shift (first HSV pass) ────────────────
print("Chromatic Shadow Shift (s284 improvement)...")
p.paint_chromatic_shadow_shift_pass(
    shadow_thresh=0.38,
    shadow_range=0.15,
    shadow_hue_shift=25.0,
    highlight_thresh=0.72,
    highlight_range=0.14,
    highlight_hue_shift=10.0,
    shift_strength=0.78,
    opacity=0.70,
)

# ── s284 artist pass: Grosz Neue Sachlichkeit (195th mode) ───────────────────
print("Grosz Neue Sachlichkeit (195th mode)...")
p.grosz_neue_sachlichkeit_pass(
    gradient_sigma=1.3,
    shadow_darken=0.58,
    zone_sigma=5.0,
    flat_strength=0.26,
    acid_strength=0.24,
    acid_r=0.78,
    acid_g=0.84,
    acid_b=0.14,
    dark_push_r=0.10,
    dark_push_g=0.08,
    dark_push_b=0.16,
    dark_push_strength=0.20,
    gamma_value=0.82,
    opacity=0.80,
)

# ── s283 improvement: Form Curvature Tint (depth enhancement) ────────────────
print("Form Curvature Tint (s283 improvement)...")
p.paint_form_curvature_tint_pass(
    smooth_sigma=7.0,
    convex_r=0.82,
    convex_g=0.76,
    convex_b=0.38,
    convex_strength=0.14,
    concave_r=0.18,
    concave_g=0.20,
    concave_b=0.44,
    concave_strength=0.12,
    curvature_sigma=2.0,
    curvature_percentile=80.0,
    opacity=0.68,
)

# ── Final output ──────────────────────────────────────────────────────────────
output_path = "s284_weimar_night.png"
p.save(output_path)
print(f"Saved: {output_path}")
