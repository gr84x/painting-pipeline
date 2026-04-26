"""
run_aivazovsky_storm_skiff.py — Session 199

"Skiff in the Trough" — after Ivan Aivazovsky

Image Description
─────────────────
Subject & Composition
    A solitary wooden fishing skiff viewed from a low angle just above the
    waterline, plunging through the trough between two enormous Atlantic
    storm waves.  The boat occupies the lower-left third of the frame,
    angled steeply downward at roughly 25° as it descends into the trough.
    The perspective is intimate and vertiginous — the viewer is nearly at
    wave level, in the water beside the boat.

The Figure
    No human figure — the boat is the subject.  A weathered, dark-hulled
    wooden skiff, perhaps twelve feet long, its bow pressing downward into
    the trough.  The hull is dark umber: paint peeling in long strips,
    exposing raw timber beneath.  A single tattered sail, half-furled,
    whips to the right in the wind.  A coil of heavy rope lies in the
    stern.  The mast tilts severely to port under gale force.  No crew
    visible — either swept away or huddled below the gunwale.  The boat
    carries the emotional weight: abandonment, courage, survival.

The Environment
    Two massive wave walls bracket the composition.  The left wave rears up
    like a cliff — a vertical wall of deep navy-indigo water, its crest
    beginning to curl at the upper-left, backlit by pale golden storm light
    so the thin tip is translucent jade-green before dissolving into white
    spray.  The right wave is seen in cross-section: trough face blue-black,
    impenetrable; its upper shoulder curves away to the right.  The horizon
    is a compressed razor of pale silver-gold light, visible only in a
    narrow gap between the two wave masses at upper-centre.  Sky above is
    storm grey — deep charcoal with a bruised violet cast, clouds boiling.
    A fine scatter of sea spray hangs across the entire upper half.

Technique & Palette
    Ivan Aivazovsky's Russian Romantic marine technique: wide confident
    horizontal brushwork for wave architecture, loaded-brush horizontal
    drags, atmospheric depth for distant haze.  Aivazovsky Marine Luminance
    pass (110th distinct mode) as the primary effect: jade crest
    translucency, navy trough deepening, amber-gold horizon radiance band.
    Thin viridian glaze unifies the ocean.

    Palette: deep navy indigo, stormy blue-grey, translucent jade-viridian,
    silver-pale horizon gold, near-black storm cloud, foam white, weathered
    umber boat hull, tattered ochre-grey sail.

Mood & Intent
    The storm does not know the boat exists.  The waves are not malevolent —
    they simply are.  The boat, absurdly small, absurdly present, continues.
    The narrow strip of horizon light is not hope exactly — it is just the
    truth that beyond the wave there is more sky.  The viewer is left with
    the cold exhilaration of standing at the edge of something vast and
    indifferent and surviving it, for now.

Session 199 pass used:
    aivazovsky_marine_luminance_pass  (110th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "aivazovsky_storm_skiff.png"
)
W, H = 900, 1100   # portrait — emphasises the towering wave walls


def build_reference() -> np.ndarray:
    """
    Synthetic tonal reference encoding the storm seascape scene.

    Tonal zones:
      - Sky (upper fifth): deep charcoal-violet storm cloud
      - Horizon band: compressed silver-gold radiance strip
      - Left wave wall (main): navy-indigo vertical mass, backlit jade crest
      - Right wave shoulder (foreground right): dark cross-section
      - Wave trough (lower centre): turbulent green-grey churned water
      - Wooden skiff: dark umber hull + tattered sail, lower-left
      - Sea spray: fine bright scatter across upper half
    """
    rng = np.random.default_rng(199)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Sky: deep storm charcoal-violet ──────────────────────────────────────
    sky_bound = 0.18
    sky_base  = np.array([0.12, 0.10, 0.16])   # dark charcoal-violet
    sky_mid   = np.array([0.16, 0.14, 0.20])   # slightly lighter mid
    sky_frac  = np.clip(ys / sky_bound, 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = sky_base[ch] * (1 - sky_frac) + sky_mid[ch] * sky_frac

    # ── Horizon radiance band: silver-gold, compressed strip ──────────────────
    hor_centre = 0.22   # narrow strip just below sky
    hor_width  = 0.025
    hor_color  = np.array([0.82, 0.76, 0.52])
    hor_glow   = np.exp(-0.5 * ((ys - hor_centre) / hor_width) ** 2)
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - hor_glow) + hor_color[ch] * hor_glow

    # ── Main water mass: deep navy-indigo base ─────────────────────────────────
    water_start = 0.20
    water_frac  = np.clip((ys - water_start) / (1.0 - water_start), 0.0, 1.0)
    water_top   = np.array([0.12, 0.20, 0.40])   # mid-water blue
    water_deep  = np.array([0.06, 0.10, 0.26])   # deep trough navy
    for ch in range(3):
        ref[:, :, ch] = np.where(
            ys > water_start,
            water_top[ch] * (1 - water_frac) + water_deep[ch] * water_frac,
            ref[:, :, ch]
        )

    # ── Left wave wall: tall vertical navy mass, lower-left to upper-left ────
    # The wave is centred around x=0.30, spanning upper-left to lower-centre
    wave_cx  = 0.28
    wave_top_y = 0.22   # wave crest at 22% from top
    wave_bot_y = 0.88   # wave foot at 88% from top
    wave_hw  = 0.18     # half-width at base

    # Wave shape: a parabolic bulge, wider at base
    wave_t = np.clip((ys - wave_top_y) / (wave_bot_y - wave_top_y), 0.0, 1.0)
    wave_half = wave_hw * (0.3 + 0.7 * wave_t)   # narrows toward top
    wave_edge = wave_cx + wave_half
    wave_dist = np.abs(xs - wave_cx) / (wave_half + 0.001)
    wave_dist = np.where(ys >= wave_top_y, wave_dist, 999.0)
    wave_mask = np.clip(1.0 - wave_dist ** 0.60, 0.0, 1.0)

    # Wave face colour: deep navy on shadow side, greener toward centre
    wave_r = 0.08; wave_g = 0.18; wave_b = 0.42
    for ch, wc in enumerate([wave_r, wave_g, wave_b]):
        ref[:, :, ch] = ref[:, :, ch] * (1 - wave_mask) + wc * wave_mask

    # Backlit jade crest at top of wave
    crest_band = np.exp(-0.5 * ((ys - wave_top_y) / 0.04) ** 2)
    crest_mask = crest_band * wave_mask * np.where(xs < wave_cx + wave_half * 0.8, 1.0, 0.0)
    crest_color = np.array([0.18, 0.52, 0.40])   # translucent jade
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - crest_mask * 0.80) + crest_color[ch] * crest_mask * 0.80

    # ── Right wave shoulder: dark cross-section on right side ─────────────────
    rwave_x  = 0.72
    rwave_hw = 0.28
    rwave_top_y = 0.30
    rwave_frac = np.clip((xs - rwave_x) / rwave_hw, 0.0, 1.0)
    rwave_vert  = np.clip((ys - rwave_top_y) / 0.70, 0.0, 1.0)
    rwave_mask  = rwave_frac * rwave_vert
    rwave_col   = np.array([0.04, 0.08, 0.20])   # near-black blue-black
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - rwave_mask) + rwave_col[ch] * rwave_mask

    # ── Wave trough: turbulent green-grey churned water ───────────────────────
    trough_y = 0.78
    trough_col = np.array([0.14, 0.28, 0.32])   # murky green-grey
    trough_band = np.exp(-0.5 * ((ys - trough_y) / 0.12) ** 2)
    trough_zone = trough_band * np.clip(1.0 - wave_mask - rwave_mask, 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - trough_zone * 0.6) + trough_col[ch] * trough_zone * 0.6

    # Add turbulence texture to trough
    noise = rng.random((H, W)).astype(np.float32) - 0.5
    from scipy.ndimage import gaussian_filter
    noise_smooth = gaussian_filter(noise, sigma=4.0)
    trough_texture = trough_zone * noise_smooth * 0.15
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + trough_texture, 0.0, 1.0)

    # ── Wooden skiff hull: dark umber, angled downward at lower-left ──────────
    # Hull: elongated ellipse tilted at -25 degrees
    hull_cx = 0.28
    hull_cy = 0.82
    hull_angle = -25.0 * math.pi / 180.0
    cos_a = math.cos(hull_angle)
    sin_a = math.sin(hull_angle)
    hull_hw = 0.18   # half-length
    hull_hh = 0.028  # half-height

    # Rotate coordinates
    dx_hull = xs - hull_cx
    dy_hull = ys - hull_cy
    rx_hull =  dx_hull * cos_a + dy_hull * sin_a
    ry_hull = -dx_hull * sin_a + dy_hull * cos_a
    hull_dist = np.sqrt((rx_hull / hull_hw) ** 2 + (ry_hull / hull_hh) ** 2)
    hull_mask = np.clip(1.0 - hull_dist ** 0.70, 0.0, 1.0)

    # Dark umber hull
    hull_col = np.array([0.20, 0.10, 0.04])   # weathered umber
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - hull_mask) + hull_col[ch] * hull_mask

    # Hull highlight on upper edge (wet wood catching light)
    hull_top_mask = hull_mask * np.clip((ry_hull + hull_hh * 0.5) / (hull_hh * 0.6), 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + hull_top_mask * 0.12, 0.0, 1.0)

    # ── Mast: dark vertical line tilted to port ───────────────────────────────
    mast_base_x = hull_cx - 0.02
    mast_base_y = hull_cy - hull_hh * 2.0
    mast_top_x  = mast_base_x - 0.04   # tilts left
    mast_top_y  = mast_base_y - 0.30
    for mi in range(80):
        mt = mi / 80.0
        mx = mast_base_x + (mast_top_x - mast_base_x) * mt
        my = mast_base_y + (mast_top_y - mast_base_y) * mt
        mast_dist = np.sqrt(((xs - mx) / 0.004) ** 2 + ((ys - my) / 0.004) ** 2)
        mast_seg_mask = np.clip(1.0 - mast_dist, 0.0, 1.0) ** 2 * 0.90
        for ch in range(3):
            ref[:, :, ch] -= mast_seg_mask * ref[:, :, ch] * 0.85

    # ── Tattered sail: ochre-grey, blowing right ──────────────────────────────
    sail_cx = mast_top_x + 0.06
    sail_cy = mast_top_y + 0.10
    sail_hw = 0.09
    sail_hh = 0.07
    sail_dist = np.sqrt(((xs - sail_cx) / sail_hw) ** 2 + ((ys - sail_cy) / sail_hh) ** 2)
    sail_mask = np.clip(1.0 - sail_dist ** 0.65, 0.0, 1.0) * 0.75
    sail_col  = np.array([0.72, 0.64, 0.44])   # dirty ochre-grey canvas
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - sail_mask) + sail_col[ch] * sail_mask

    # ── Sea spray: fine bright scatter in upper half ───────────────────────────
    spray_noise = rng.random((H, W)).astype(np.float32)
    spray_mask  = np.where(spray_noise > 0.93, spray_noise, 0.0)
    spray_vert  = np.clip(1.0 - ys * 3.0, 0.0, 1.0)   # stronger at top
    spray_alpha = spray_mask * spray_vert * 0.55
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + spray_alpha * 0.88, 0.0, 1.0)

    # ── Foam: white at wave crest edges ──────────────────────────────────────
    foam_col   = np.array([0.92, 0.93, 0.95])
    foam_mask  = crest_mask * np.where(rng.random((H, W)) > 0.60, 1.0, 0.0)
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - foam_mask * 0.75) + foam_col[ch] * foam_mask * 0.75

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'Skiff in the Trough' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=199)

    # ── Ground: warm ochre-umber — Aivazovsky's characteristic toned ground ──
    p.tone_ground((0.42, 0.36, 0.22), texture_strength=0.020)

    # ── Underpainting: dark wave masses and sky ───────────────────────────────
    p.underpainting(ref_pil, stroke_size=58)

    # ── Block in: broad horizontal wave architecture ──────────────────────────
    p.block_in(ref_pil, stroke_size=30)

    # ── Build form: wave surface structure ────────────────────────────────────
    p.build_form(ref_pil, stroke_size=14)

    # ── Lights: lead-white foam peaks and horizon radiance ───────────────────
    p.place_lights(ref_pil, stroke_size=7)

    # ── Aivazovsky Marine Luminance — THE signature effect ───────────────────
    # Primary pass: full marine luminance with horizon radiance
    p.aivazovsky_marine_luminance_pass(
        horizon_y=0.22,
        wave_frequency=9.0,
        wave_amplitude=0.06,
        crest_jade=(0.16, 0.50, 0.38),
        trough_navy=(0.05, 0.12, 0.30),
        crest_strength=0.72,
        trough_strength=0.58,
        horizon_glow=(0.84, 0.76, 0.46),
        horizon_glow_width=0.06,
        horizon_glow_strength=0.65,
        foam_strength=0.52,
        opacity=0.82,
        seed=199,
    )

    # Second pass: deeper trough darkening, lower frequency for large wave form
    p.aivazovsky_marine_luminance_pass(
        horizon_y=0.22,
        wave_frequency=3.5,
        crest_jade=(0.20, 0.54, 0.44),
        trough_navy=(0.04, 0.09, 0.22),
        crest_strength=0.45,
        trough_strength=0.70,
        horizon_glow=(0.88, 0.80, 0.52),
        horizon_glow_width=0.03,
        horizon_glow_strength=0.45,
        foam_strength=0.25,
        opacity=0.40,
        seed=1990,
    )

    # ── Atmospheric depth: haze the far wave wall ─────────────────────────────
    p.atmospheric_depth_pass(
        haze_color=(0.32, 0.40, 0.56),
        desaturation=0.30,
        lightening=0.22,
        depth_gamma=1.4,
        background_only=False,
    )

    # ── Meso detail: sharpen the hull and wave crest edges ────────────────────
    p.meso_detail_pass(strength=0.28, opacity=0.22)

    # ── Glazing: thin viridian to unify the ocean ─────────────────────────────
    p.glaze((0.10, 0.30, 0.22), opacity=0.08)

    # ── Vignette: pull focus to the skiff and the horizon light ──────────────
    p.focal_vignette_pass(vignette_strength=0.28, opacity=0.50)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
