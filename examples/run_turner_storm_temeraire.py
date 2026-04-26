"""
run_turner_storm_temeraire.py — Session 203

"The Vortex Claims the Wounded Ship" — after J. M. W. Turner

Image Description
─────────────────
Subject & Composition
    A single three-masted first-rate sailing warship in the final moments of
    a catastrophic North Sea storm, viewed from low water level, slightly to
    port and roughly two hundred metres back.  The ship occupies the right
    half of the canvas, tilted fifteen degrees to starboard, its silhouette
    dissolving into the surrounding atmosphere at every edge.  The masts pierce
    the vortex sky; the lower hull is swallowed by black-green surge.  The
    composition is radially organised: a screaming tear of yellow-gold light
    bursts from the upper-centre-right sky — the Turner solar vortex, the eye
    of the storm's brief opening — and all energy radiates outward from it:
    waves, spray, rigging lines, torn sail edges.  The far left is impenetrable
    storm wall, dark blue-violet.

The Figure
    The ship is a Royal Navy first-rate of the 1840s, oak-black hull barely
    readable against the dark water.  The foremast leans at a dangerous angle;
    the mainmast is still vertical but the topsails are stripped to tatters by
    the gale, ribbons of pale canvas streaming to the left.  The bowsprit
    points skyward at a terrifying pitch.  No crew is visible — the ship is
    either abandoned or the crew has retreated below.  State: the vessel is
    present yet already becoming part of the storm — its outlines are not
    edges but gradients, already reabsorbed into the atmosphere Turner loved
    more than the things it contained.  Emotional state: sublime indifference.
    The ship neither struggles nor surrenders.  The ocean does not notice.

The Environment
    The sea is not water but energy in a visible state.  The lower two-thirds
    of the canvas are enormous wedge-shaped storm swells — dark grey-green
    walls shot through with silver-white foam crests that catch the vortex
    light.  The crests are the only firm edges in the painting.  In the
    foreground, churning white spume catches the yellow-gold vortex glow,
    creating the brightest passage in the lower half.  The sky is a single
    vast atmospheric field: the vortex light at upper-centre-right is near-
    white yellow-gold, radiating outward through chrome yellow and raw sienna
    into Payne's grey and then deep blue-violet at the far left and upper-left
    corners.  Rain streaks are visible as fine diagonal silver threads across
    the mid-sky zone.  Horizon: invisible — sea and sky fuse at the limit of
    the vortex's reach.  The transition zone between them is pure atmosphere.

Technique & Palette
    J. M. W. Turner's late Romantic / Proto-Impressionist technique.  The
    turner_vortex_luminance_pass (114th distinct mode) is the primary chromatic
    effect: the solar vortex at upper-centre-right radiates warm yellow-gold
    outward while the periphery receives progressive cool blue-violet atmospheric
    haze.  A luminance lift at the vortex core reproduces Turner's near-blinding
    solar intensity.  All edges are dissolved by wet-into-wet blending.

    Palette: near-white yellow-gold (solar vortex), chrome yellow, raw sienna,
    warm cream, storm grey-green (sea), Payne's grey, cool blue-violet (storm
    wall), silver-white (foam crests), dark oak-black (hull).

Mood & Intent
    The Burkean sublime: the terror that precedes awe when something vast and
    indifferent reveals itself.  Turner spent his life painting not the things
    that exist in atmosphere but the atmosphere itself — light, water, and air
    as a single unified field.  The ship is an excuse, not the subject.  The
    viewer should feel breathless, then afraid, then moved: the ocean is not
    hostile, it simply does not know you are there.  Turner's dying words were
    "The sun is God."  This image is about that.

Session 203 pass used:
    turner_vortex_luminance_pass  (114th distinct mode)
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
    os.path.dirname(os.path.abspath(__file__)), "turner_storm_temeraire.png"
)
W, H = 1080, 900


def build_reference() -> np.ndarray:
    """
    Synthetic reference for 'The Vortex Claims the Wounded Ship'.

    Tonal zones:
      - Vortex sky (upper 40%): warm yellow-gold at centre-right, cool storm grey at left
      - Sea (lower 60%): dark grey-green swells with white foam crests
      - Ship silhouette (right-centre): dark hull, dissolving masts
      - Vortex core: near-white luminance burst at upper-centre-right
      - Foreground spume: bright white-gold foam catching vortex light
    """
    rng = np.random.default_rng(203)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Vortex sky (upper 42% of canvas) ─────────────────────────────────────
    sky_frac = 0.42
    sky_mask_hard = (ys < sky_frac).astype(np.float32)
    sky_mask_soft = np.clip(1.0 - (ys - 0.0) / (sky_frac + 0.08), 0.0, 1.0)

    # Base sky: cool storm grey drifting to deep blue-violet at left
    base_sky = np.array([0.52, 0.54, 0.62])
    storm_wall_col = np.array([0.22, 0.22, 0.40])
    x_gradient = np.clip(xs / 0.60, 0.0, 1.0)   # 0=left (dark), 1=centre+right
    for ch in range(3):
        sky_col = storm_wall_col[ch] * (1 - x_gradient) + base_sky[ch] * x_gradient
        ref[:, :, ch] += sky_col * sky_mask_soft

    # ── Solar vortex glow (upper-centre-right sky) ────────────────────────────
    vortex_cx, vortex_cy = 0.62, 0.22
    vortex_r = 0.30
    vortex_dist = np.sqrt((xs - vortex_cx) ** 2 + (ys - vortex_cy) ** 2)
    # Warm yellow-gold inner glow
    vortex_glow = np.clip(1.0 - vortex_dist / vortex_r, 0.0, 1.0) ** 1.4
    vortex_col = np.array([0.97, 0.90, 0.55])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - vortex_glow * 0.72) + vortex_col[ch] * vortex_glow * 0.72

    # Near-white core burst (inner 35% of vortex radius)
    core_glow = np.clip(1.0 - vortex_dist / (vortex_r * 0.35), 0.0, 1.0) ** 2.0
    core_col = np.array([1.0, 0.97, 0.88])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - core_glow) + core_col[ch] * core_glow

    # Chrome yellow mid-ring transition
    mid_glow = np.clip(
        (1.0 - vortex_dist / (vortex_r * 0.70)) * (vortex_dist / (vortex_r * 0.30)),
        0.0, 1.0
    ) ** 1.2
    mid_col = np.array([0.90, 0.78, 0.35])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - mid_glow * 0.55) + mid_col[ch] * mid_glow * 0.55

    # ── Rain streaks in sky (fine diagonal silver threads) ────────────────────
    rain_noise = rng.random((H, W)).astype(np.float32)
    rain_smooth = gaussian_filter(rain_noise, sigma=(0.5, 4.0))   # elongated horizontally→diagonal
    rain_streaks = np.clip((rain_smooth - 0.70) * 15.0, 0.0, 1.0) * 0.18
    rain_col = np.array([0.80, 0.82, 0.88])
    for ch in range(3):
        ref[:, :, ch] = np.clip(
            ref[:, :, ch] * (1 - rain_streaks * sky_mask_soft) + rain_col[ch] * rain_streaks * sky_mask_soft,
            0.0, 1.0
        )

    # ── Storm sea (lower 60% of canvas) ──────────────────────────────────────
    sea_frac = 0.42
    sea_mask = np.clip((ys - sea_frac) / 0.08, 0.0, 1.0)

    # Base sea: dark grey-green
    sea_col_deep  = np.array([0.10, 0.14, 0.18])   # deep trough
    sea_col_mid   = np.array([0.20, 0.28, 0.32])   # mid swell
    # Lerp from mid at horizon to deep near viewer
    sea_depth_t = np.clip((ys - sea_frac) / (1.0 - sea_frac), 0.0, 1.0)
    for ch in range(3):
        sea_col = sea_col_mid[ch] * (1 - sea_depth_t) + sea_col_deep[ch] * sea_depth_t
        ref[:, :, ch] = ref[:, :, ch] * (1 - sea_mask) + sea_col * sea_mask

    # Wave swells: sinusoidal undulation with noise
    wave_base_freq = 3.5
    wave_noise = rng.random((H, W)).astype(np.float32)
    wave_smooth = gaussian_filter(wave_noise, sigma=8.0)
    wave_field = np.sin(
        xs * math.pi * wave_base_freq + wave_smooth * 1.8 + ys * math.pi * 1.2
    ) * 0.5 + 0.5   # [0, 1]
    # Wave peaks are lighter (grey-green)
    wave_peak = wave_field ** 2.8
    wave_peak_col = np.array([0.30, 0.38, 0.42])   # swell crest colour
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - wave_peak * sea_mask * 0.55) + \
                        wave_peak_col[ch] * wave_peak * sea_mask * 0.55

    # ── Foam crests: bright white-gold on wave peaks ──────────────────────────
    foam_threshold = 0.68
    foam_mask = np.clip((wave_field - foam_threshold) / (1.0 - foam_threshold), 0.0, 1.0)
    foam_mask = foam_mask ** 1.8 * sea_mask
    foam_col = np.array([0.95, 0.92, 0.80])   # warm silver-white
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - foam_mask * 0.90) + foam_col[ch] * foam_mask * 0.90

    # ── Foreground spume — bright churning foam at very bottom ────────────────
    spume_y = np.clip((ys - 0.78) / 0.18, 0.0, 1.0)
    spume_noise = rng.random((H, W)).astype(np.float32)
    spume_smooth = gaussian_filter(spume_noise, sigma=3.5)
    spume_mask = np.clip((spume_smooth - 0.40) * 2.5, 0.0, 1.0) * spume_y ** 0.7
    spume_col = np.array([0.98, 0.95, 0.85])   # near-white with warm vortex tint
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - spume_mask * 0.85) + spume_col[ch] * spume_mask * 0.85

    # ── Vortex reflection on sea (warm gold streak on water) ─────────────────
    refl_cx = vortex_cx
    refl_y_start = sea_frac + 0.08
    refl_width = 0.12
    refl_dist_x = np.abs(xs - refl_cx)
    refl_mask = np.clip(
        1.0 - refl_dist_x / (refl_width * (1.0 + (ys - refl_y_start) * 1.5)),
        0.0, 1.0
    ) ** 1.5 * np.clip((ys - refl_y_start) / 0.10, 0.0, 1.0) * sea_mask
    refl_col = np.array([0.72, 0.62, 0.28])   # warm amber reflection
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - refl_mask * 0.50) + refl_col[ch] * refl_mask * 0.50

    # ── Ship silhouette (right-centre, dissolving into atmosphere) ────────────
    ship_cx = 0.66
    ship_cy = sea_frac - 0.04   # sitting on the horizon
    ship_tilt = 0.15            # 15-degree tilt to starboard (right)

    # Hull: dark trapezoid shape, slightly wider at waterline
    hull_half_w = 0.085
    hull_half_h = 0.065
    hull_dist = np.sqrt(
        ((xs - ship_cx) / hull_half_w) ** 2 + ((ys - ship_cy) / hull_half_h) ** 2
    )
    hull_mask = np.clip(1.0 - hull_dist ** 1.6, 0.0, 1.0)
    hull_col = np.array([0.10, 0.10, 0.12])   # near-black oak hull
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - hull_mask * 0.80) + hull_col[ch] * hull_mask * 0.80

    # Hull waterline reflection: slight lighter band at waterline
    waterline_y = ship_cy + hull_half_h * 0.55
    waterline_mask = np.exp(
        -((ys - waterline_y) ** 2) / (0.008 ** 2)
    ) * np.clip(1.0 - np.abs(xs - ship_cx) / hull_half_w, 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + waterline_mask * 0.12, 0.0, 1.0)

    # Foremast: tilted line, dissolves into sky
    mast_base_x = ship_cx - 0.020
    mast_base_y = ship_cy - hull_half_h * 0.60
    mast_tip_x  = mast_base_x + ship_tilt * 0.18 + 0.015   # tilt + slight sway
    mast_tip_y  = mast_base_y - 0.30
    for mast_frac in np.linspace(0, 1, 80):
        mx = mast_base_x + (mast_tip_x - mast_base_x) * mast_frac
        my = mast_base_y + (mast_tip_y - mast_base_y) * mast_frac
        mdist = np.sqrt(((xs - mx) / 0.004) ** 2 + ((ys - my) / 0.004) ** 2)
        mmask = np.clip(1.0 - mdist ** 2.0, 0.0, 1.0) * (1 - mast_frac ** 1.5 * 0.65)
        mcol = np.array([0.15, 0.15, 0.18])
        for ch in range(3):
            ref[:, :, ch] = ref[:, :, ch] * (1 - mmask * 0.75) + mcol[ch] * mmask * 0.75

    # Mainmast: more vertical, slightly behind foremast
    main_base_x = ship_cx + 0.010
    main_base_y = mast_base_y
    main_tip_x  = main_base_x + ship_tilt * 0.08
    main_tip_y  = main_base_y - 0.36
    for mast_frac in np.linspace(0, 1, 90):
        mx = main_base_x + (main_tip_x - main_base_x) * mast_frac
        my = main_base_y + (main_tip_y - main_base_y) * mast_frac
        mdist = np.sqrt(((xs - mx) / 0.0035) ** 2 + ((ys - my) / 0.0035) ** 2)
        mmask = np.clip(1.0 - mdist ** 2.0, 0.0, 1.0) * (1 - mast_frac ** 1.8 * 0.70)
        mcol = np.array([0.14, 0.14, 0.16])
        for ch in range(3):
            ref[:, :, ch] = ref[:, :, ch] * (1 - mmask * 0.72) + mcol[ch] * mmask * 0.72

    # Shredded topsail: pale ghost ribbons streaming left from foremast top
    sail_cx = mast_tip_x - 0.02
    sail_cy = mast_tip_y + 0.04
    sail_noise = rng.random((H, W)).astype(np.float32)
    sail_smooth = gaussian_filter(sail_noise, sigma=(1.5, 6.0))
    sail_cloud = np.clip(sail_smooth - 0.55, 0.0, 1.0) * 8.0
    sail_x_gate = np.clip((ship_cx - xs) / 0.28 + 0.05, 0.0, 1.0) ** 0.8   # streams LEFT
    sail_y_gate = np.exp(-((ys - sail_cy) ** 2) / (0.028 ** 2))
    sail_mask = np.clip(sail_cloud * sail_x_gate * sail_y_gate, 0.0, 0.45)
    sail_col = np.array([0.88, 0.85, 0.78])   # pale weathered canvas
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - sail_mask) + sail_col[ch] * sail_mask

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'The Vortex Claims the Wounded Ship' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=203)

    # ── Ground: warm cream — Turner's white chalk ground ─────────────────────
    p.tone_ground((0.85, 0.80, 0.68), texture_strength=0.008)

    # ── Underpainting: broad atmospheric masses — sky, sea, vortex shape ─────
    p.underpainting(ref_pil, stroke_size=70)

    # ── Block in: sky zones, sea swells, ship mass, vortex glow area ─────────
    p.block_in(ref_pil, stroke_size=30)

    # ── Build form: wave forms, ship silhouette, foam crests ─────────────────
    p.build_form(ref_pil, stroke_size=14)

    # ── Lights: foam crest highlights, vortex core burst, sail ribbons ────────
    p.place_lights(ref_pil, stroke_size=6)

    # ── Turner Vortex Luminance — THE signature effect ────────────────────────
    # Primary pass: solar vortex at upper-centre-right, blue-violet storm wall
    p.turner_vortex_luminance_pass(
        vortex_x=0.62,
        vortex_y=0.22,
        vortex_radius=0.42,
        core_strength=0.60,
        haze_strength=0.50,
        lum_lift=0.20,
        vortex_color=(0.98, 0.92, 0.60),
        periphery_color=(0.28, 0.26, 0.46),
        opacity=0.76,
    )

    # Second pass: gentler second vortex pass to deepen the luminous core
    p.turner_vortex_luminance_pass(
        vortex_x=0.62,
        vortex_y=0.22,
        vortex_radius=0.20,
        core_strength=0.35,
        haze_strength=0.0,
        lum_lift=0.12,
        vortex_color=(1.0, 0.97, 0.82),
        periphery_color=(0.30, 0.28, 0.48),
        opacity=0.38,
    )

    # ── Atmospheric depth: deepen the blue-grey haze toward canvas edges ─────
    p.atmospheric_depth_pass(
        haze_color=(0.32, 0.30, 0.52),
        desaturation=0.35,
        lightening=0.20,
        depth_gamma=1.2,
        background_only=False,
        horizon_glow_band=0.0,
    )

    # ── Tonal compression: hold Turner's full tonal range — no crushed blacks,
    #    no blown whites — the atmosphere needs its full luminance field ────────
    p.tonal_compression_pass(shadow_lift=0.01, highlight_compress=0.98, midtone_contrast=0.03)

    # ── Meso detail: wave texture, foam structure, sail shred detail ──────────
    p.meso_detail_pass(strength=0.14, opacity=0.12)

    # ── Vignette: darken extreme corners to reinforce the vortex composition ──
    p.glaze((0.20, 0.18, 0.30), opacity=0.06)   # cool violet tint to deepen shadows

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
