"""Session 284 -- Oskar Kokoschka (195th mode)
kokoschka_vibrating_surface_pass + paint_chromatic_shadow_shift_pass

Subject & Composition:
    "Storm Over the Aegean" -- a panoramic coastal landscape viewed from an
    elevated rocky promontory above the Aegean Sea at the approach of a
    violent storm. The composition is divided into three horizontal zones:
    a turbulent sky occupying the upper half, dark churning sea below, and
    a rocky cliff face cutting across the left edge.

The Environment:
    SKY: Storm clouds mass in dark charcoal-violet layers. The horizon glows
    with an electric orange-amber light where the sun is still visible beneath
    the cloud base, throwing vivid warm light under the dark anvil above. The
    upper sky is deep Prussian violet-black. Cumulus masses build in the
    mid-sky, their undersides caught in the warm horizon light (crimson-orange)
    while their tops are dark steel-grey.

    SEA: The Aegean lies dark and churning below. Near the horizon the water
    reflects the warm orange glow in broken patches. Mid-sea: deep blue-green
    with whitecap ridges, horizontal smears of foam tracking the wind
    direction. Foreground water: near-black troughs between cresting waves.
    Two distant silhouetted sailing vessels are visible at mid-distance,
    their sails nearly vertical against the storm sky.

    CLIFF: A rocky promontory in burnt ochre and deep sienna occupies the
    left third of the canvas from mid-height to bottom. The cliff face is
    broken with diagonal fault lines and pools of dark shadow in the crevices.
    A few wind-bent scrub trees cling to the upper edge of the cliff.

Technique & Palette:
    Kokoschka's Austrian Expressionist mode. Palette: Prussian blue-violet
    for sky and deep water; cadmium orange-amber for the horizon glow;
    burnt ochre and raw sienna for the cliff; viridian and cobalt for
    mid-sea water; vivid cobalt edge accents at all form boundaries;
    warm amber inner glow throughout mid-tone zones.

Mood & Intent:
    The painting channels Kokoschka's "cosmic viewpoint" -- the sensation
    of observing the meeting of opposing forces (sky and sea, calm and storm,
    warmth and cold) from a position of elevated witness. The viewer should
    feel the energy and charge of the moment before the storm breaks: the
    heavy silence, the electric anticipation, the vast indifferent power
    of the natural world. The vivid chromatic edge accentuation creates
    intensity without aggression; the inner amber glow at the cliff and
    horizon introduces warmth and vitality into the turbulent scene.
    The painting intends to leave the viewer with a sense of awe, alertness,
    and the particular Austrian Expressionist feeling of the sublime as
    something both terrifying and beautiful.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stroke_engine import Painter

# ── Canvas dimensions ────────────────────────────────────────────────────────
W, H = 1440, 1040
SEED = 284

# ── Reference: procedural Aegean storm scene ─────────────────────────────────

def build_reference() -> np.ndarray:
    """Construct a vivid expressionist coastal storm reference."""
    rng = np.random.default_rng(SEED)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    ys = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]   # (H,1)
    xs = np.linspace(0.0, 1.0, W, dtype=np.float32)[None, :]   # (1,W)

    horizon_y = 0.50     # sea/sky boundary as fraction of H
    horizon_row = int(horizon_y * H)

    # ── Sky ──────────────────────────────────────────────────────────────────
    # upper sky: deep prussian violet-black
    sky_r = np.clip(0.08 + ys * 0.18, 0.0, 1.0)
    sky_g = np.clip(0.06 + ys * 0.14, 0.0, 1.0)
    sky_b = np.clip(0.28 + ys * 0.14, 0.0, 1.0)

    # horizon glow: orange-amber band at 85-100% of sky zone (y near horizon_y)
    glow_center = 0.92   # fraction within sky (0=top, 1=horizon)
    glow_y = glow_center * horizon_y
    glow_sigma = 0.07
    glow_dist = np.abs(ys - glow_y)
    glow_weight = np.exp(-0.5 * (glow_dist / glow_sigma) ** 2).astype(np.float32)
    glow_weight = glow_weight * (ys < horizon_y).astype(np.float32)

    sky_r = np.clip(sky_r + glow_weight * 0.82, 0.0, 1.0)
    sky_g = np.clip(sky_g + glow_weight * 0.42, 0.0, 1.0)
    sky_b = np.clip(sky_b - glow_weight * 0.12, 0.0, 1.0)

    # Storm cloud masses (perlin-like turbulence via stacked noise)
    def fbm_noise(shape, octaves=5, seed=0):
        rng2 = np.random.default_rng(seed)
        out = np.zeros(shape, dtype=np.float32)
        amp, freq = 1.0, 1.0
        for _ in range(octaves):
            noise = rng2.random(shape).astype(np.float32)
            from scipy.ndimage import gaussian_filter as gf
            smooth_sigma = max(1, int(min(shape) / (freq * 8)))
            out += amp * gf(noise, sigma=smooth_sigma)
            amp *= 0.5
            freq *= 2.0
        out -= out.min()
        out /= max(out.max(), 1e-6)
        return out

    cloud_noise = fbm_noise((H, W), octaves=5, seed=SEED + 10)

    # cloud band: occupies y = 0.10..0.85 of sky zone
    cloud_lo = int(0.10 * horizon_row)
    cloud_hi = int(0.85 * horizon_row)
    cloud_ys = np.zeros((H, 1), dtype=np.float32)
    for row in range(cloud_lo, cloud_hi):
        t = (row - cloud_lo) / max(cloud_hi - cloud_lo - 1, 1)
        cloud_ys[row] = np.sin(np.pi * t) * 0.85

    cloud_mask = cloud_noise * cloud_ys.reshape(H, 1)
    cloud_mask = np.clip(cloud_mask - 0.25, 0.0, 1.0) * (ys < horizon_y)
    cloud_mask = cloud_mask.astype(np.float32)

    # clouds: dark charcoal on top, warm orange-red on underside
    cloud_r = cloud_mask * (0.38 + glow_weight * 0.52)
    cloud_g = cloud_mask * (0.22 + glow_weight * 0.18)
    cloud_b = cloud_mask * (0.28 - glow_weight * 0.18)

    sky_r = np.clip(sky_r * (1 - cloud_mask * 0.65) + cloud_r, 0.0, 1.0)
    sky_g = np.clip(sky_g * (1 - cloud_mask * 0.65) + cloud_g, 0.0, 1.0)
    sky_b = np.clip(sky_b * (1 - cloud_mask * 0.65) + cloud_b, 0.0, 1.0)

    # write sky zone
    sky_zone = ys < horizon_y
    ref[:, :, 0] = np.where(sky_zone, sky_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(sky_zone, sky_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(sky_zone, sky_b, ref[:, :, 2])

    # ── Sea ──────────────────────────────────────────────────────────────────
    # normalised depth within sea zone (0=horizon, 1=bottom)
    sea_t = np.clip((ys - horizon_y) / (1.0 - horizon_y), 0.0, 1.0)

    # base sea colour: dark cobalt-green deepening toward near-black at bottom
    sea_r = np.clip(0.18 - sea_t * 0.14, 0.0, 1.0)
    sea_g = np.clip(0.28 - sea_t * 0.16, 0.0, 1.0)
    sea_b = np.clip(0.42 - sea_t * 0.22, 0.0, 1.0)

    # horizon glow reflection in near-horizon water
    reflect_sigma = 0.04
    reflect_dist = np.abs(ys - horizon_y)
    reflect_weight = np.exp(-0.5 * (reflect_dist / reflect_sigma) ** 2).astype(np.float32)
    reflect_weight = reflect_weight * (ys >= horizon_y)
    sea_r = np.clip(sea_r + reflect_weight * 0.70, 0.0, 1.0)
    sea_g = np.clip(sea_g + reflect_weight * 0.28, 0.0, 1.0)
    sea_b = np.clip(sea_b - reflect_weight * 0.10, 0.0, 1.0)

    # whitecaps: horizontal band noise
    wave_noise = fbm_noise((H, W), octaves=4, seed=SEED + 20)
    wave_row_pattern = np.zeros((H, 1), dtype=np.float32)
    # bands of whitecaps at irregular intervals
    for band_y in [0.55, 0.62, 0.70, 0.80, 0.90]:
        bsig = 0.008
        dist = np.abs(ys - band_y)
        wave_row_pattern += np.exp(-0.5 * (dist / bsig) ** 2)
    whitecap_mask = np.clip(wave_noise * wave_row_pattern, 0.0, 1.0)
    whitecap_mask = np.clip(whitecap_mask - 0.55, 0.0, 1.0) * (ys >= horizon_y)
    whitecap_mask = whitecap_mask.astype(np.float32)

    sea_r = np.clip(sea_r + whitecap_mask * 0.68, 0.0, 1.0)
    sea_g = np.clip(sea_g + whitecap_mask * 0.70, 0.0, 1.0)
    sea_b = np.clip(sea_b + whitecap_mask * 0.72, 0.0, 1.0)

    sea_zone = ys >= horizon_y
    ref[:, :, 0] = np.where(sea_zone, sea_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(sea_zone, sea_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(sea_zone, sea_b, ref[:, :, 2])

    # ── Rocky cliff (left edge) ───────────────────────────────────────────────
    # cliff occupies x = 0..0.22 W, y = 0.38..1.0 H
    cliff_w_frac = 0.22
    cliff_top_y  = 0.38
    cliff_edge_x = int(cliff_w_frac * W)

    cliff_noise = fbm_noise((H, W), octaves=4, seed=SEED + 30)

    # distance from cliff edge (1 at left, 0 at cliff_edge_x)
    cliff_dist = np.clip(1.0 - xs / cliff_w_frac, 0.0, 1.0)
    cliff_top_fade = np.clip((ys - cliff_top_y) / 0.08, 0.0, 1.0)
    cliff_mask = (cliff_dist * cliff_top_fade).astype(np.float32)
    cliff_mask = np.clip(cliff_mask + cliff_noise * 0.15 - 0.05, 0.0, 1.0)
    cliff_mask = cliff_mask.astype(np.float32)

    # cliff colour: warm burnt ochre with dark shadow crevices
    cliff_r = np.clip(0.62 + cliff_noise * 0.22 - 0.08, 0.10, 0.84)
    cliff_g = np.clip(0.38 + cliff_noise * 0.16 - 0.06, 0.08, 0.58)
    cliff_b = np.clip(0.18 + cliff_noise * 0.10 - 0.04, 0.04, 0.32)

    # shadow crevices in the cliff face
    crv_noise = fbm_noise((H, W), octaves=6, seed=SEED + 40)
    crevice = np.clip(crv_noise - 0.60, 0.0, 1.0) * cliff_mask
    cliff_r = np.clip(cliff_r - crevice * 0.45, 0.0, 1.0)
    cliff_g = np.clip(cliff_g - crevice * 0.30, 0.0, 1.0)
    cliff_b = np.clip(cliff_b - crevice * 0.15, 0.0, 1.0)

    ref[:, :, 0] = np.clip(ref[:, :, 0] * (1 - cliff_mask) + cliff_r * cliff_mask, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] * (1 - cliff_mask) + cliff_g * cliff_mask, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] * (1 - cliff_mask) + cliff_b * cliff_mask, 0.0, 1.0)

    # ── Distant sailing vessels ───────────────────────────────────────────────
    # Two small triangular sail silhouettes at horizon level
    for (sx, sy, sw, sh_) in [(0.52, 0.44, 0.025, 0.06), (0.65, 0.46, 0.018, 0.045)]:
        cx = int(sx * W)
        cy = int(sy * H)
        hull_h = int(0.012 * H)
        sail_h = int(sh_ * H)
        sail_w = int(sw * W)

        # hull: dark rectangle
        hy0 = cy - hull_h // 2
        hy1 = cy + hull_h // 2
        hx0 = cx - sail_w // 2
        hx1 = cx + sail_w // 2
        hy0, hy1 = max(0, hy0), min(H, hy1)
        hx0, hx1 = max(0, hx0), min(W, hx1)
        ref[hy0:hy1, hx0:hx1, 0] = 0.08
        ref[hy0:hy1, hx0:hx1, 1] = 0.06
        ref[hy0:hy1, hx0:hx1, 2] = 0.10

        # sail: triangle (near-white leaning against the storm)
        for row_off in range(sail_h):
            row = cy - row_off
            if 0 <= row < H:
                frac = row_off / max(sail_h - 1, 1)
                sw_row = max(1, int(sail_w * (1.0 - frac * 0.7)))
                col0 = max(0, cx - sw_row // 2)
                col1 = min(W, cx + sw_row // 2)
                ref[row, col0:col1, 0] = np.clip(0.82 + rng.random() * 0.08, 0.0, 1.0)
                ref[row, col0:col1, 1] = np.clip(0.82 + rng.random() * 0.06, 0.0, 1.0)
                ref[row, col0:col1, 2] = np.clip(0.78 + rng.random() * 0.06, 0.0, 1.0)

    # ── Scrub trees on cliff edge ─────────────────────────────────────────────
    tree_y = int(cliff_top_y * H)
    for tx in [int(0.08 * W), int(0.14 * W), int(0.19 * W)]:
        for dy in range(-int(0.04 * H), 0):
            row = tree_y + dy
            if 0 <= row < H:
                spread = int(0.012 * W * (1.0 + dy / (0.04 * H + 1e-5)))
                col0 = max(0, tx - spread)
                col1 = min(W, tx + spread)
                ref[row, col0:col1, 0] = 0.12
                ref[row, col0:col1, 1] = 0.20
                ref[row, col0:col1, 2] = 0.10

    ref = np.clip(ref, 0.0, 1.0)
    return ref


# ── Build reference ───────────────────────────────────────────────────────────
print("Building procedural reference...")
ref = build_reference()

# Save reference preview
ref_uint8 = (ref * 255).astype(np.uint8)
Image.fromarray(ref_uint8).save("s284_reference.png")
print("Reference saved: s284_reference.png")

# ── Painting pipeline ─────────────────────────────────────────────────────────
print("Initialising painter...")
p = Painter(W, H, seed=SEED)

ref_u8 = (ref * 255).astype(np.uint8)   # uint8 for all engine methods

# Ground: deep violet-grey (Kokoschka's turbulent base)
print("Tone ground...")
p.tone_ground(color=(0.34, 0.28, 0.44), texture_strength=0.025)

# Underpainting: establish tonal structure
print("Underpainting...")
p.underpainting(ref_u8, stroke_size=52, n_strokes=260, dry_amount=0.65)

# Block in: broad masses
print("Block in (broad)...")
p.block_in(ref_u8, stroke_size=32, n_strokes=460, dry_amount=0.55)
print("Block in (medium)...")
p.block_in(ref_u8, stroke_size=20, n_strokes=500, dry_amount=0.50)

# Build form: modelling
print("Build form (medium)...")
p.build_form(ref_u8, stroke_size=12, n_strokes=540, dry_amount=0.45)
print("Build form (fine)...")
p.build_form(ref_u8, stroke_size=6,  n_strokes=440, dry_amount=0.40)

# Place lights: highlights and accents
print("Place lights...")
p.place_lights(ref_u8, stroke_size=4, n_strokes=300)

# ── s284 improvement: Chromatic Shadow Shift (first HSV pass) ────────────────
print("Chromatic Shadow Shift (s284 improvement)...")
p.paint_chromatic_shadow_shift_pass(
    shadow_thresh=0.40,
    shadow_range=0.16,
    shadow_hue_shift=30.0,
    highlight_thresh=0.70,
    highlight_range=0.14,
    highlight_hue_shift=14.0,
    shift_strength=0.82,
    opacity=0.72,
)

# ── s284 artist pass: Kokoschka Vibrating Surface (195th mode) ───────────────
print("Kokoschka Vibrating Surface (195th mode)...")
p.kokoschka_vibrating_surface_pass(
    gradient_sigma=1.1,
    edge_percentile=80.0,
    glow_lo=0.36,
    glow_hi=0.72,
    glow_r=0.94,
    glow_g=0.82,
    glow_b=0.52,
    glow_strength=0.26,
    edge_r=0.28,
    edge_g=0.50,
    edge_b=0.90,
    edge_strength=0.30,
    sat_boost=0.32,
    opacity=0.86,
)

# ── s283 improvement: Form Curvature Tint (depth enhancement) ────────────────
print("Form Curvature Tint (s283 improvement)...")
p.paint_form_curvature_tint_pass(
    smooth_sigma=8.0,
    convex_r=0.88,
    convex_g=0.70,
    convex_b=0.44,
    convex_strength=0.16,
    concave_r=0.22,
    concave_g=0.28,
    concave_b=0.56,
    concave_strength=0.14,
    curvature_sigma=2.0,
    curvature_percentile=80.0,
    opacity=0.70,
)

# ── Final output ──────────────────────────────────────────────────────────────
output_path = "s284_aegean_storm.png"
p.save(output_path)
print(f"Saved: {output_path}")
