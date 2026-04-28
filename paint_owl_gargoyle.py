"""
paint_owl_gargoyle.py — Session 208 painting task

Paints 'The Watcher' — a great horned owl perched on a gothic stone gargoyle
at night, viewed from below-left, in Munch-influenced expressionist atmospheric
style with Rembrandt chiaroscuro.

Passes used:
  underpainting, block_in, build_form, place_lights
  munch_anxiety_swirl_pass  (atmospheric nocturnal sky energy)
  kline_gestural_slash_pass (structural edge tension in the stonework)
  glaze, finish
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "owl_gargoyle_watcher.png")
W, H = 800, 1080   # tall portrait — gives room for owl above, city below


def build_reference() -> np.ndarray:
    """
    Synthetic reference for the owl-on-gargoyle nocturne.

    Zones (top to bottom):
      - Deep Prussian blue sky (upper half), luminous grey-white near moon (upper right)
      - Faint cirrus wisps in sky
      - Cathedral stone parapet (lower right diagonal)
      - Gargoyle form (centre-right, mid-canvas)
      - Owl silhouette and plumage detail (upper-centre, largest element)
      - City lights far below (lower quarter, indistinct amber haze)
      - Fog wisps rising (lower third)
    """
    rng = np.random.default_rng(208)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    xs = np.linspace(0.0, 1.0, W)[np.newaxis, :]
    ys = np.linspace(0.0, 1.0, H)[:, np.newaxis]

    # ── Sky: Prussian blue lit by moon, visible mid-range brightness ─────────
    # Moon light source is upper-right: brightest at (0.88, 0.06)
    moon_x, moon_y = 0.88, 0.06
    moon_dist = np.sqrt((xs - moon_x) ** 2 + (ys - moon_y) ** 2)
    moon_glow = np.clip(1.0 - moon_dist / 0.70, 0.0, 1.0) ** 1.4

    # Sky: mid-tone blue (0.12 base so it reads clearly through painting)
    sky_r = 0.12 + 0.34 * moon_glow + 0.04 * (1.0 - ys)
    sky_g = 0.14 + 0.30 * moon_glow + 0.03 * (1.0 - ys)
    sky_b = 0.32 + 0.40 * moon_glow + 0.08 * (1.0 - ys)

    ref[:, :, 0] = np.clip(sky_r, 0.0, 1.0)
    ref[:, :, 1] = np.clip(sky_g, 0.0, 1.0)
    ref[:, :, 2] = np.clip(sky_b, 0.0, 1.0)

    # ── Faint cirrus wisps ────────────────────────────────────────────────────
    for _ in range(7):
        wisp_y = rng.uniform(0.05, 0.30)
        wisp_x = rng.uniform(0.1, 0.9)
        wisp_len = rng.uniform(0.25, 0.55)
        wisp_h = rng.uniform(0.012, 0.025)
        wisp_angle = rng.uniform(-0.15, 0.15)
        # Parameterised along wisp
        t = np.linspace(0.0, 1.0, 80)
        for ti in t:
            wx = wisp_x + (ti - 0.5) * wisp_len
            wy = wisp_y + (ti - 0.5) * wisp_len * wisp_angle
            d = np.sqrt(((xs - wx) / wisp_len) ** 2 + ((ys - wy) / wisp_h) ** 2)
            intensity = np.exp(-d ** 2 * 6.0) * 0.12 * np.sin(np.pi * ti)
            ref[:, :, 0] = np.clip(ref[:, :, 0] + intensity * 0.78, 0.0, 1.0)
            ref[:, :, 1] = np.clip(ref[:, :, 1] + intensity * 0.82, 0.0, 1.0)
            ref[:, :, 2] = np.clip(ref[:, :, 2] + intensity * 0.88, 0.0, 1.0)

    # ── Stone parapet: diagonal band lower-right ──────────────────────────────
    parapet_left_y  = 0.78
    parapet_right_y = 0.62
    parapet_slope   = (parapet_right_y - parapet_left_y)
    parapet_y_mid   = parapet_left_y + xs * parapet_slope
    parapet_thick   = 0.055
    parapet_dist    = np.abs(ys - parapet_y_mid) / parapet_thick
    parapet_mask    = np.clip(1.0 - parapet_dist ** 0.6, 0.0, 1.0)
    # Stone: mid blue-grey, moonlit top edge bright
    stone_r = 0.28 + 0.22 * moon_glow
    stone_g = 0.28 + 0.18 * moon_glow
    stone_b = 0.34 + 0.20 * moon_glow
    ref[:, :, 0] = ref[:, :, 0] * (1 - parapet_mask) + np.clip(stone_r, 0.0, 1.0) * parapet_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - parapet_mask) + np.clip(stone_g, 0.0, 1.0) * parapet_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - parapet_mask) + np.clip(stone_b, 0.0, 1.0) * parapet_mask

    # Stone below parapet: dark mid-tone, not black
    below_parapet = (ys > parapet_y_mid + parapet_thick * 0.5)
    dark_r = np.clip(0.14 + 0.08 * moon_glow, 0.0, 1.0)
    dark_g = np.clip(0.12 + 0.06 * moon_glow, 0.0, 1.0)
    dark_b = np.clip(0.18 + 0.10 * moon_glow, 0.0, 1.0)
    ref[:, :, 0] = np.where(below_parapet, dark_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(below_parapet, dark_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(below_parapet, dark_b, ref[:, :, 2])

    # ── City lights: warm amber haze in lowest quarter ────────────────────────
    city_zone = np.clip((ys - 0.80) / 0.20, 0.0, 1.0)
    city_r = 0.35 * city_zone
    city_g = 0.22 * city_zone
    city_b = 0.06 * city_zone
    # Add random light pinpoints
    n_lights = 140
    for _ in range(n_lights):
        lx = rng.uniform(0.0, 1.0)
        ly = rng.uniform(0.82, 1.0)
        ld = np.sqrt(((xs - lx) / 0.025) ** 2 + ((ys - ly) / 0.015) ** 2)
        lint = np.exp(-ld ** 2) * rng.uniform(0.3, 0.9)
        city_r = np.clip(city_r + lint * 0.90, 0.0, 1.0)
        city_g = np.clip(city_g + lint * 0.55, 0.0, 1.0)
        city_b = np.clip(city_b + lint * 0.10, 0.0, 1.0)

    city_mask = city_zone
    ref[:, :, 0] = ref[:, :, 0] * (1 - city_mask * 0.85) + city_r * city_mask * 0.85
    ref[:, :, 1] = ref[:, :, 1] * (1 - city_mask * 0.85) + city_g * city_mask * 0.85
    ref[:, :, 2] = ref[:, :, 2] * (1 - city_mask * 0.85) + city_b * city_mask * 0.85

    # ── Fog wisps rising from city ────────────────────────────────────────────
    fog_y_start = 0.70
    fog_mask = np.clip((fog_y_start - ys + 0.15) / 0.18, 0.0, 1.0) * 0.35
    fog_noise = rng.uniform(0.0, 1.0, (H, W)).astype(np.float32)
    fog_actual = fog_mask * (0.4 + 0.6 * fog_noise)
    ref[:, :, 0] = np.clip(ref[:, :, 0] + fog_actual * 0.22, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + fog_actual * 0.22, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + fog_actual * 0.28, 0.0, 1.0)

    # ── Gargoyle: dark stone form, centre-right, projecting outward ──────────
    # Gargoyle body: elongated dark mass from parapet at (0.62, 0.64) forward-left
    gar_cx, gar_cy = 0.54, 0.58
    gar_rx, gar_ry = 0.11, 0.10
    gar_dist = np.sqrt(((xs - gar_cx) / gar_rx) ** 2 + ((ys - gar_cy) / gar_ry) ** 2)
    gar_body  = np.clip(1.0 - gar_dist, 0.0, 1.0) ** 0.7
    # Gargoyle neck and head (forward protrusion)
    gneck_cx, gneck_cy = 0.48, 0.52
    gneck_rx, gneck_ry = 0.06, 0.07
    gneck_dist = np.sqrt(((xs - gneck_cx) / gneck_rx) ** 2 + ((ys - gneck_cy) / gneck_ry) ** 2)
    gneck_mask = np.clip(1.0 - gneck_dist, 0.0, 1.0) ** 0.8
    gar_mask = np.clip(gar_body + gneck_mask, 0.0, 1.0)
    # Stone edge-lit by moonlight (upper-right face of gargoyle slightly brighter)
    gar_light = np.clip(1.0 - moon_dist / 1.2, 0.0, 1.0) * 0.25
    gar_r = 0.14 + gar_light
    gar_g = 0.14 + gar_light * 0.85
    gar_b = 0.18 + gar_light * 0.70
    ref[:, :, 0] = ref[:, :, 0] * (1 - gar_mask) + np.clip(gar_r, 0.0, 1.0) * gar_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - gar_mask) + np.clip(gar_g, 0.0, 1.0) * gar_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - gar_mask) + np.clip(gar_b, 0.0, 1.0) * gar_mask

    # ── Owl: main subject, upper-centre ──────────────────────────────────────
    owl_cx, owl_cy = 0.46, 0.32   # owl body centre
    owl_body_rx, owl_body_ry = 0.16, 0.22
    # Body: ellipse
    body_dist = np.sqrt(
        ((xs - owl_cx) / owl_body_rx) ** 2 + ((ys - owl_cy) / owl_body_ry) ** 2
    )
    body_mask = np.clip(1.0 - body_dist, 0.0, 1.0) ** 0.6

    # Head: slightly separate ellipse above body
    head_cx, head_cy = 0.46, 0.16
    head_rx, head_ry = 0.12, 0.11
    head_dist = np.sqrt(
        ((xs - head_cx) / head_rx) ** 2 + ((ys - head_cy) / head_ry) ** 2
    )
    head_mask = np.clip(1.0 - head_dist, 0.0, 1.0) ** 0.6

    # Ear tufts: two narrow dark spikes above head
    for tuft_x in [0.39, 0.53]:
        tuft_cx, tuft_cy = tuft_x, 0.07
        tuft_dist = np.sqrt(
            ((xs - tuft_cx) / 0.025) ** 2 + ((ys - tuft_cy) / 0.055) ** 2
        )
        tuft_mask = np.clip(1.0 - tuft_dist, 0.0, 1.0) ** 0.8
        head_mask = np.clip(head_mask + tuft_mask, 0.0, 1.0)

    # Combined owl silhouette
    owl_mask = np.clip(body_mask + head_mask, 0.0, 1.0)

    # Owl plumage: warm barred brown-amber breast, darker back
    breast_y = owl_cy
    breast_mask = owl_mask * np.clip((ys - (breast_y - 0.08)) / 0.20, 0.0, 1.0)
    # Barring: visible horizontal modulation
    bars = (np.sin(ys * H * 0.32) * 0.5 + 0.5) * 0.20 + 0.80
    breast_r = 0.70 * bars
    breast_g = 0.50 * bars
    breast_b = 0.24 * bars

    # Dark mantle (back/top): deep umber, clearly darker than breast
    mantle_mask = owl_mask * np.clip(1.0 - breast_mask / (owl_mask + 1e-6), 0.0, 1.0)
    mantle_r = 0.32
    mantle_g = 0.22
    mantle_b = 0.12

    # Moonlight edge: bright silver catch on owl's upper-right silhouette
    owl_moon_light = np.clip(1.0 - moon_dist / 0.80, 0.0, 1.0) * 0.42
    owl_r = (breast_r * breast_mask + mantle_r * mantle_mask) * owl_mask + owl_moon_light * owl_mask
    owl_g = (breast_g * breast_mask + mantle_g * mantle_mask) * owl_mask + owl_moon_light * 0.92 * owl_mask
    owl_b = (breast_b * breast_mask + mantle_b * mantle_mask) * owl_mask + owl_moon_light * 0.80 * owl_mask

    ref[:, :, 0] = ref[:, :, 0] * (1 - owl_mask) + np.clip(owl_r, 0.0, 1.0) * owl_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - owl_mask) + np.clip(owl_g, 0.0, 1.0) * owl_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - owl_mask) + np.clip(owl_b, 0.0, 1.0) * owl_mask

    # ── Owl eyes: large golden irises ────────────────────────────────────────
    for eye_x, eye_y in [(0.41, 0.18), (0.51, 0.18)]:
        eye_dist = np.sqrt(((xs - eye_x) / 0.038) ** 2 + ((ys - eye_y) / 0.042) ** 2)
        iris_mask = np.clip(1.0 - eye_dist, 0.0, 1.0) ** 0.6
        pupil_dist = np.sqrt(((xs - eye_x) / 0.016) ** 2 + ((ys - eye_y) / 0.018) ** 2)
        pupil_mask = np.clip(1.0 - pupil_dist, 0.0, 1.0) ** 0.7
        # Iris: burnished gold
        ref[:, :, 0] = ref[:, :, 0] * (1 - iris_mask) + (0.82 * iris_mask)
        ref[:, :, 1] = ref[:, :, 1] * (1 - iris_mask) + (0.62 * iris_mask)
        ref[:, :, 2] = ref[:, :, 2] * (1 - iris_mask) + (0.04 * iris_mask)
        # Pupil: near-black
        ref[:, :, 0] = ref[:, :, 0] * (1 - pupil_mask) + (0.04 * pupil_mask)
        ref[:, :, 1] = ref[:, :, 1] * (1 - pupil_mask) + (0.03 * pupil_mask)
        ref[:, :, 2] = ref[:, :, 2] * (1 - pupil_mask) + (0.02 * pupil_mask)
        # Eye specular catch light (moonlight)
        catch_dist = np.sqrt(((xs - (eye_x + 0.012)) / 0.008) ** 2 + ((ys - (eye_y - 0.010)) / 0.009) ** 2)
        catch_mask = np.clip(1.0 - catch_dist, 0.0, 1.0) ** 0.5
        ref[:, :, 0] = np.clip(ref[:, :, 0] + catch_mask * 0.92, 0.0, 1.0)
        ref[:, :, 1] = np.clip(ref[:, :, 1] + catch_mask * 0.94, 0.0, 1.0)
        ref[:, :, 2] = np.clip(ref[:, :, 2] + catch_mask * 0.95, 0.0, 1.0)

    # ── Facial disc: rust-orange ring around eyes ─────────────────────────────
    disc_cx, disc_cy = 0.46, 0.19
    disc_rx, disc_ry = 0.14, 0.13
    disc_dist = np.sqrt(((xs - disc_cx) / disc_rx) ** 2 + ((ys - disc_cy) / disc_ry) ** 2)
    disc_ring = np.clip(1.0 - np.abs(disc_dist - 0.60) / 0.22, 0.0, 1.0) ** 1.5 * owl_mask
    ref[:, :, 0] = np.clip(ref[:, :, 0] + disc_ring * 0.38, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + disc_ring * 0.18, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] - disc_ring * 0.06, 0.0, 1.0)

    # ── Throat: pale ivory-white disc ────────────────────────────────────────
    throat_cx, throat_cy = 0.46, 0.25
    throat_dist = np.sqrt(((xs - throat_cx) / 0.055) ** 2 + ((ys - throat_cy) / 0.045) ** 2)
    throat_mask = np.clip(1.0 - throat_dist, 0.0, 1.0) ** 0.9 * owl_mask
    ref[:, :, 0] = ref[:, :, 0] * (1 - throat_mask) + 0.90 * throat_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - throat_mask) + 0.88 * throat_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - throat_mask) + 0.82 * throat_mask

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint The Watcher and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=208)

    # ── Ground: dark indigo-blue — Rembrandt-dark but lets warm tones read ────
    p.tone_ground((0.12, 0.12, 0.20), texture_strength=0.04)

    # ── Underpainting: establish tonal structure ──────────────────────────────
    p.underpainting(ref_pil, stroke_size=50, dry_amount=0.82)

    # ── Block-in: primary chromatic zones ────────────────────────────────────
    p.block_in(ref_pil, stroke_size=26, dry_amount=0.58)

    # ── Build form: mid-scale feather and stone detail ────────────────────────
    p.build_form(ref_pil, stroke_size=11, dry_amount=0.40)

    # ── Munch swirl: very subtle, bg-only — adds nocturnal sky atmosphere ─────
    p.munch_anxiety_swirl_pass(
        n_swirl_strokes=80,
        swirl_amplitude=0.18,
        swirl_frequency=3.0,
        color_intensity=0.28,
        bg_only=True,
        stroke_opacity=0.10,
        stroke_size=8.0,
    )

    # ── Place lights: moonlit impasto highlights on owl and parapet ───────────
    p.place_lights(ref_pil, stroke_size=5, n_strokes=500)

    # ── Final glaze: cool blue veil for nocturnal unity ───────────────────────
    p.glaze((0.06, 0.08, 0.18), opacity=0.09)

    # ── Finish ────────────────────────────────────────────────────────────────
    p.finish()

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
