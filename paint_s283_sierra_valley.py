"""paint_s283_sierra_valley.py -- Session 283: Albert Bierstadt (194th mode)

Subject & Composition:
    A dramatic Sierra Nevada valley at late afternoon -- the classic Bierstadt
    subject. Viewed from a slightly elevated vantage on the valley's southern
    rim, looking northwest. The composition is organized in deep recession:
    richly textured rocky foreground with gold-and-umber meadow grasses in
    the immediate near zone; a great dark pine forest occupying the valley
    floor in the middle distance; and beyond the forest, a still mountain lake
    with glassy water reflecting the brilliant sky. The background is dominated
    by a sequence of mountain ranges retreating into atmospheric haze -- the
    nearest peaks warm amber in the late light, the farthest a cool blue-grey
    barely distinguishable from the sky. Cathedral spires of rock rise at
    left; a long snowfield catches the warm gold on the right.

The Figure: [no figure -- landscape subject]

The Environment:
    Sierra Nevada, California. Late October, approximately 4:30 PM. A weather
    system is partially clearing from the west: heavy storm clouds dominate the
    upper sky (dark ultramarine-grey), but a gap has opened near the horizon,
    and through that gap streams intense afternoon sunlight -- its rays rendered
    visible by the moisture-laden air and residual haze from the recent storm.
    The crepuscular rays fan downward-right toward the valley, illuminating the
    lake and the amber meadow in theatrical golden pools of light. The temperature
    is cool; the air crystalline after the rain, which intensifies all colors. The
    lake is absolutely still -- no wind has reached the valley floor. The pine
    forest is dark and densely shadowed. Far snowfields glow brilliant white
    where the sun catches them.

Technique & Palette:
    Albert Bierstadt's mature Rocky Mountain / Sierra Nevada method:
    - Sky: deep ultramarine zenith darkening to dramatic storm cloud grey,
      then opening to warm cream-gold near the horizon gap
    - Crepuscular rays in warm amber-gold, fanning from the upper-center gap
    - Mountains: warm sienna/amber for near ridges, cool blue-grey for far ranges
    - Forest: black-green silhouettes
    - Lake: cool blue mirror of the sky
    - Foreground: rich umber-sienna earth tones, golden meadow grass

Mood & Intent:
    The American Sublime -- Bierstadt's defining emotional register. The scene
    should inspire awe: the smallness of human scale against the grandeur of the
    mountains, the miracle of the light breaking through the storm, the sense
    that nature is here not indifferent but actively theatrical -- performing
    for the viewer. The painting should make the viewer feel simultaneously
    humbled and exalted. The specific mood is "numinous gladness" -- the
    uplift of witnessing something transcendently beautiful in nature.

New in s283:
    - bierstadt_luminous_glory_pass (194th mode): luminous horizon uplift with
      inverted sky gradient, cool ultramarine zenith, warm amber middle-distance
      theatrical haze (triple-gated), warm umber foreground shadow enrichment
    - paint_crepuscular_ray_pass (improvement): content-detected source point,
      polar coordinate transformation, angular cosine lobe ray synthesis,
      multiplicative falloff × luminance gate composite
"""

import os
import sys
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

W, H = 1440, 1040   # landscape -- wide panoramic valley

# ── Procedural reference image (landscape, no figures) ───────────────────────

def build_reference(width: int, height: int, seed: int = 283) -> np.ndarray:
    """Build a Sierra Nevada valley at late afternoon -- Bierstadt palette."""
    rng = np.random.default_rng(seed)

    img = np.zeros((height, width, 3), dtype=np.float32)

    Yn, Xn = np.mgrid[0:height, 0:width].astype(np.float32)
    Yn = Yn / (height - 1)
    Xn = Xn / (width  - 1)

    # ── Sky (top 38%) ────────────────────────────────────────────────────────
    sky_zone = 0.38

    # Zenith: deep ultramarine-grey storm clouds
    sky_zenith   = np.array([0.18, 0.20, 0.40], dtype=np.float32)
    sky_cloud_mid = np.array([0.36, 0.38, 0.48], dtype=np.float32)
    sky_horizon  = np.array([0.90, 0.88, 0.72], dtype=np.float32)  # warm cream at horizon gap

    sky_mask = np.clip(1.0 - Yn / sky_zone, 0.0, 1.0)
    sky_mask_soft = np.clip(1.0 - (Yn - sky_zone + 0.03) / 0.03, 0.0, 1.0)
    # Gradient: horizon (bottom of sky) is brightest
    t_sky = np.clip(Yn / sky_zone, 0.0, 1.0)  # 0 at zenith, 1 at horizon
    for c in range(3):
        img[:, :, c] += (sky_zenith[c] * (1.0 - t_sky) ** 1.5 +
                         sky_cloud_mid[c] * (1.0 - np.abs(t_sky - 0.5) * 2) * 0.8 +
                         sky_horizon[c] * t_sky ** 2.0
                         ) * sky_mask_soft

    # Storm cloud texture: darker patches in upper sky
    for i in range(8):
        cx = rng.uniform(0.0, 1.0)
        cy = rng.uniform(0.0, 0.28)
        rx, ry = rng.uniform(0.12, 0.28), rng.uniform(0.04, 0.10)
        cloud_dark = rng.uniform(0.06, 0.16)
        dist_cloud = np.sqrt(((Xn - cx) / rx)**2 + ((Yn - cy) / ry)**2)
        cloud_mask = np.clip(1.0 - dist_cloud, 0.0, 1.0) ** 2 * sky_mask_soft
        img[:, :, :] -= cloud_mask[:, :, np.newaxis] * cloud_dark

    # Golden ray shaft zone: warm glow in upper-center-right sky
    # The "gap" in the clouds where the sun breaks through
    gap_cx, gap_cy = 0.60, 0.22
    gap_rx, gap_ry = 0.18, 0.08
    gap_dist = np.sqrt(((Xn - gap_cx) / gap_rx)**2 + ((Yn - gap_cy) / gap_ry)**2)
    gap_mask = np.clip(1.0 - gap_dist, 0.0, 1.0) ** 1.5 * sky_mask_soft
    ray_glow = np.array([0.96, 0.82, 0.48], dtype=np.float32)
    for c in range(3):
        img[:, :, c] = np.clip(img[:, :, c] + ray_glow[c] * gap_mask * 0.45, 0.0, 1.0)

    img = np.clip(img, 0.0, 1.0)

    # ── Far mountains (38% to 52%) ───────────────────────────────────────────
    far_top = 0.36
    far_bot = 0.52

    # Multiple ranges with increasing warmth from farthest to nearest
    mountain_profiles = [
        # (bottom_y, height_frac, n_peaks, peak_height_var, color, snow_thresh)
        (0.44, 0.10, 5, 0.04,
         np.array([0.44, 0.48, 0.58]), 0.62),   # farthest -- cool blue-grey
        (0.46, 0.12, 4, 0.05,
         np.array([0.54, 0.46, 0.28]), 0.75),   # mid-distance -- warm amber
        (0.49, 0.14, 3, 0.06,
         np.array([0.30, 0.24, 0.16]), 0.85),   # near ridgeline -- dark umber
    ]

    for bot_y, h_frac, n_pk, var, color, snow_thresh in mountain_profiles:
        peak_xs = np.linspace(0.0, 1.0, n_pk + 2)[1:-1]
        peak_hs = bot_y - h_frac + rng.uniform(-var, var, n_pk).astype(np.float32)

        for ix, (px, ph) in enumerate(zip(peak_xs, peak_hs)):
            # Triangular mountain silhouette for each peak
            slope = rng.uniform(3.0, 6.0)
            dist_from_peak = np.abs(Xn - px)
            peak_mask = np.clip(1.0 - dist_from_peak * slope - (Yn - ph) / (bot_y - ph),
                                0.0, 1.0) * np.clip((Yn - ph) / max(bot_y - ph, 0.001), 0.0, 1.0)
            peak_mask = peak_mask ** 0.5
            for c in range(3):
                img[:, :, c] = img[:, :, c] * (1.0 - peak_mask * 0.92) + color[c] * peak_mask * 0.92

            # Snow on peaks (high luminance patches on upper portions of mountains)
            snow_mask = peak_mask * np.clip(1.0 - (Yn - ph) / (bot_y - ph + 0.02), 0.0, 1.0)
            snow_mask = np.clip(snow_mask * snow_thresh, 0.0, 1.0)
            snow_col = np.array([0.94, 0.92, 0.90], dtype=np.float32)
            snow_light = rng.uniform(0.0, 1.0, (height, width)).astype(np.float32)
            snow_light = np.clip(snow_light * 0.3 + 0.7, 0.0, 1.0)
            for c in range(3):
                img[:, :, c] = np.clip(img[:, :, c] + snow_col[c] * snow_mask * 0.60, 0.0, 1.0)

    # ── Valley forest (50% to 68%) ───────────────────────────────────────────
    forest_top = 0.50
    forest_bot = 0.68

    forest_mask = (np.clip((Yn - forest_top) / 0.04, 0.0, 1.0) *
                   np.clip((forest_bot - Yn) / 0.04, 0.0, 1.0))

    # Dark pine green with variation
    pine_dark  = np.array([0.08, 0.12, 0.06], dtype=np.float32)
    pine_mid   = np.array([0.14, 0.18, 0.10], dtype=np.float32)

    # Forest texture: irregular canopy silhouette
    canopy_noise = rng.uniform(-0.04, 0.04, (height, width)).astype(np.float32)
    canopy_factor = np.clip(canopy_noise * 8 + 0.5, 0.0, 1.0)[:, :, np.newaxis]
    forest_tone = pine_dark + (pine_mid - pine_dark) * canopy_factor

    for c in range(3):
        img[:, :, c] = img[:, :, c] * (1.0 - forest_mask * 0.92) + forest_tone[:, :, c] * forest_mask * 0.92

    # Golden meadow clearings in forest
    for _ in range(4):
        cx = rng.uniform(0.2, 0.8)
        cy = rng.uniform(forest_top + 0.02, forest_bot - 0.02)
        rx, ry = rng.uniform(0.05, 0.12), rng.uniform(0.015, 0.03)
        clearing_dist = np.sqrt(((Xn - cx) / rx)**2 + ((Yn - cy) / ry)**2)
        clearing_mask = np.clip(1.0 - clearing_dist, 0.0, 1.0) ** 1.5
        meadow_col = np.array([0.62, 0.56, 0.22], dtype=np.float32)
        for c in range(3):
            img[:, :, c] = img[:, :, c] * (1.0 - clearing_mask * 0.80) + meadow_col[c] * clearing_mask * 0.80

    # ── Mountain lake (67% to 76%) ───────────────────────────────────────────
    lake_top = 0.67
    lake_bot = 0.76
    lake_mask = (np.clip((Yn - lake_top) / 0.015, 0.0, 1.0) *
                 np.clip((lake_bot - Yn) / 0.015, 0.0, 1.0))

    # Lake color: reflection of sky -- cool blue-grey with horizontal distortions
    lake_base = np.array([0.40, 0.50, 0.62], dtype=np.float32)
    # Subtle horizontal reflection ripples
    ripple_noise = np.sin(Yn * 800 + rng.uniform(0, 2*np.pi)) * 0.015
    lake_bright = np.clip(lake_base + ripple_noise[:, :, np.newaxis] * 0.5, 0.0, 1.0)

    # Reflections of sky rays in water (horizontal streaks of gold)
    reflection_y = np.clip(1.0 - (Yn - lake_top) / (lake_bot - lake_top), 0.0, 1.0)
    ray_reflect = gap_mask * reflection_y  # mirror the sky gap
    for c in range(3):
        img[:, :, c] = (img[:, :, c] * (1.0 - lake_mask * 0.94) +
                        (lake_bright[:, :, c] + ray_glow[c] * ray_reflect * 0.20) * lake_mask * 0.94)

    img = np.clip(img, 0.0, 1.0)

    # ── Foreground (76% to 100%) ─────────────────────────────────────────────
    fg_top = 0.76
    fg_mask = np.clip((Yn - fg_top) / 0.06, 0.0, 1.0)

    # Warm umber-sienna base
    fg_dark  = np.array([0.38, 0.24, 0.12], dtype=np.float32)
    fg_light = np.array([0.60, 0.50, 0.28], dtype=np.float32)

    fg_noise = rng.uniform(0.0, 1.0, (height, width)).astype(np.float32)
    fg_tone  = fg_dark + (fg_light - fg_dark) * fg_noise[:, :, np.newaxis]

    for c in range(3):
        img[:, :, c] = img[:, :, c] * (1.0 - fg_mask * 0.88) + fg_tone[:, :, c] * fg_mask * 0.88

    # Rocky outcroppings in foreground
    for _ in range(6):
        rx_c = rng.uniform(0.05, 0.95)
        ry_c = rng.uniform(fg_top + 0.04, 0.94)
        rock_rx = rng.uniform(0.04, 0.10)
        rock_ry = rng.uniform(0.02, 0.05)
        rock_dist = np.sqrt(((Xn - rx_c) / rock_rx)**2 + ((Yn - ry_c) / rock_ry)**2)
        rock_mask = np.clip(1.0 - rock_dist, 0.0, 1.0) ** 2
        rock_col = np.array([0.50, 0.42, 0.30], dtype=np.float32)
        rock_lit = np.clip(rock_col + rng.uniform(-0.06, 0.10, 3).astype(np.float32), 0.0, 1.0)
        for c in range(3):
            img[:, :, c] = img[:, :, c] * (1.0 - rock_mask * 0.80) + rock_lit[c] * rock_mask * 0.80

    # Golden grass patches in lower foreground
    for _ in range(12):
        gx = rng.uniform(0.02, 0.98)
        gy = rng.uniform(fg_top + 0.03, 0.98)
        grass_mask_r = np.clip(1.0 - np.abs(Xn - gx) / rng.uniform(0.03, 0.08), 0.0, 1.0)
        grass_mask_y = np.clip(1.0 - np.abs(Yn - gy) / rng.uniform(0.015, 0.04), 0.0, 1.0)
        grass_mask   = grass_mask_r * grass_mask_y * fg_mask
        grass_col = np.array([0.72, 0.64, 0.24], dtype=np.float32)
        for c in range(3):
            img[:, :, c] = np.clip(img[:, :, c] + grass_col[c] * grass_mask * 0.40, 0.0, 1.0)

    # ── Atmospheric haze overlay ──────────────────────────────────────────────
    # Fade mountain zones slightly with distance haze
    haze_mask = np.clip(1.0 - Yn * 2.0, 0.0, 0.30)  # stronger near top
    haze_col  = np.array([0.78, 0.80, 0.88], dtype=np.float32)
    for c in range(3):
        img[:, :, c] = np.clip(img[:, :, c] + haze_col[c] * haze_mask * 0.15, 0.0, 1.0)

    # ── Subtle noise ──────────────────────────────────────────────────────────
    noise = rng.uniform(-0.02, 0.02, (height, width, 3)).astype(np.float32)
    img = np.clip(img + noise, 0.0, 1.0)

    return (img * 255).astype(np.uint8)


print("Building procedural Sierra Nevada reference...")
ref = build_reference(W, H, seed=283)
if ref.shape[2] == 4:
    ref = ref[:, :, :3]
print(f"Reference built: {ref.shape}")

# ── Painter setup ─────────────────────────────────────────────────────────────
from stroke_engine import Painter

p = Painter(W, H, seed=283)

# Warm amber-ochre ground -- Bierstadt's toned canvas
p.tone_ground((0.62, 0.58, 0.42), texture_strength=0.022)

# ── Structural passes ─────────────────────────────────────────────────────────
print("Underpainting...")
p.underpainting(ref, stroke_size=54, n_strokes=260)
p.underpainting(ref, stroke_size=44, n_strokes=250)

print("Block-in (broad masses)...")
p.block_in(ref, stroke_size=34, n_strokes=500)
p.block_in(ref, stroke_size=22, n_strokes=530)

print("Build form (modelling)...")
p.build_form(ref, stroke_size=12, n_strokes=560)
p.build_form(ref, stroke_size=6,  n_strokes=470)

print("Lights and accents...")
p.place_lights(ref, stroke_size=4, n_strokes=320)

# ── Artist passes ─────────────────────────────────────────────────────────────
print("Bierstadt luminous glory (194th mode)...")
p.bierstadt_luminous_glory_pass(
    sky_zone            = 0.38,
    sky_bright_lo       = 0.52,
    horizon_r           = 0.92,
    horizon_g           = 0.88,
    horizon_b           = 0.68,
    horizon_strength    = 0.36,
    zenith_fraction     = 0.16,
    zenith_dark_thresh  = 0.44,
    zenith_r            = 0.14,
    zenith_g            = 0.18,
    zenith_b            = 0.42,
    zenith_strength     = 0.40,
    mid_lo              = 0.38,
    mid_hi              = 0.76,
    mid_sat_thresh      = 0.52,
    mid_zone_lo         = 0.32,
    mid_zone_hi         = 0.70,
    amber_r             = 0.94,
    amber_g             = 0.74,
    amber_b             = 0.28,
    amber_strength      = 0.30,
    lower_zone          = 0.74,
    lower_dark_thresh   = 0.36,
    umber_r             = 0.44,
    umber_g             = 0.28,
    umber_b             = 0.12,
    umber_strength      = 0.32,
    opacity             = 0.90,
)

print("Crepuscular ray light shafts (s283 improvement)...")
p.paint_crepuscular_ray_pass(
    source_detect_sigma = 22.0,
    source_top_fraction = 0.55,
    n_rays              = 7,
    ray_sharpness       = 3.2,
    ray_angular_noise   = 0.24,
    ray_color_r         = 0.96,
    ray_color_g         = 0.80,
    ray_color_b         = 0.42,
    dist_falloff        = 1.2,
    ray_strength        = 0.18,
    lum_gate            = 0.26,
    noise_seed          = 283,
    opacity             = 0.82,
)

print("Depth atmosphere (aerial perspective)...")
p.paint_depth_atmosphere_pass(
    haze_color      = (0.78, 0.80, 0.90),
    depth_sigma     = 38.0,
    max_haze        = 0.20,
    vertical_weight = 0.65,
    contrast_weight = 0.35,
    contrast_radius = 6.0,
    noise_seed      = 283,
    opacity         = 0.55,
)

print("Contre-jour rim light (s282)...")
p.paint_contre_jour_rim_pass(
    bright_threshold   = 0.68,
    dark_threshold     = 0.38,
    gradient_sigma     = 1.4,
    rim_sigma          = 2.6,
    rim_strength       = 0.44,
    rim_r              = 0.94,
    rim_g              = 0.74,
    rim_b              = 0.24,
    cool_edge_strength = 0.24,
    cool_edge_r        = 0.52,
    cool_edge_g        = 0.60,
    cool_edge_b        = 0.80,
    edge_percentile    = 74.0,
    opacity            = 0.76,
)

print("Lost and found edges...")
p.paint_lost_found_edges_pass(
    found_threshold  = 0.26,
    lost_threshold   = 0.14,
    sharp_sigma      = 0.9,
    sharp_strength   = 0.65,
    lost_sigma       = 2.0,
    lost_strength    = 0.40,
    focal_percentile = 76.0,
    focal_power      = 1.2,
    edge_percentile  = 94.0,
    opacity          = 0.80,
)

# ── Save ──────────────────────────────────────────────────────────────────────
OUT = os.path.join(REPO, "s283_sierra_valley.png")
p.save(OUT)
print(f"Saved: {OUT}")
