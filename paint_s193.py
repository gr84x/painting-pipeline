"""
paint_s193.py — Session 193 final painting

Subject: A red British telephone booth (K6) in heavy rain, painted in
Yayoi Kusama's obsessive all-over dot style — dots radiating from multiple
centres consume every surface: rain, stones, sky, and booth alike.

Technique: kusama_infinity_dot_pass (104th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from scipy.ndimage import gaussian_filter
from stroke_engine import Painter

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s193_kusama_red_booth.png")
W, H = 800, 1000   # portrait — emphasises height of the booth and stormy sky


def build_reference() -> np.ndarray:
    """
    Reference image: red telephone booth in heavy rainstorm at dusk.

    Zones:
      - Turbulent blue-grey storm sky (upper 55%)
      - Distant city buildings dissolving into mist (upper middle)
      - Sodium streetlamp glow far down the street
      - Central red K6 booth, low three-quarter angle
      - Wet cobblestone foreground with reflections
      - Rain streaks diagonally across the full canvas
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0, 1, H)[:, None]
    xs = np.linspace(0, 1, W)[None, :]
    rng = np.random.default_rng(193)

    # ── Storm sky: deep bruised Prussian blue-grey ────────────────────────────
    sky_r = 0.14 + 0.08 * ys
    sky_g = 0.16 + 0.10 * ys
    sky_b = 0.26 + 0.14 * ys
    ref[:, :, 0] = sky_r
    ref[:, :, 1] = sky_g
    ref[:, :, 2] = sky_b

    # ── Storm cloud turbulence: dark swirling masses ──────────────────────────
    cloud_noise = gaussian_filter(
        rng.standard_normal((H, W)).astype(np.float32), sigma=(30, 50)
    )
    cloud_noise = (cloud_noise - cloud_noise.min()) / (cloud_noise.max() - cloud_noise.min())
    sky_mask = np.clip(1.0 - ys / 0.55, 0.0, 1.0).astype(np.float32)
    cloud_dark = 0.06 * cloud_noise * sky_mask
    ref[:, :, 0] = np.clip(ref[:, :, 0] - cloud_dark, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] - cloud_dark, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] - cloud_dark * 0.6, 0.0, 1.0)

    # ── Distant buildings: faint ghostly terraced facades dissolving in mist ──
    bld_mask = np.clip((ys - 0.38) / 0.10, 0.0, 1.0).astype(np.float32)  # below 38%
    bld_mask *= np.clip(1.0 - (ys - 0.50) / 0.06, 0.0, 1.0)              # above 50%
    bld_noise = gaussian_filter(
        rng.standard_normal((H, W)).astype(np.float32), sigma=(4, 2)
    )
    bld_gate = np.clip(bld_noise * 0.5 + 0.4, 0.0, 1.0) * bld_mask
    ref[:, :, 0] = np.clip(ref[:, :, 0] + 0.10 * bld_gate, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + 0.10 * bld_gate, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + 0.08 * bld_gate, 0.0, 1.0)

    # ── Sodium streetlamp glow: warm gold far down the right side ────────────
    lamp_cx, lamp_cy = 0.78, 0.48
    lamp_dist = np.sqrt(
        ((xs - lamp_cx) / 0.10) ** 2 + ((ys - lamp_cy) / 0.08) ** 2
    )
    lamp_glow = np.clip(1.0 - lamp_dist, 0.0, 1.0) ** 1.2
    lamp_glow = gaussian_filter(lamp_glow.astype(np.float32), sigma=12)
    ref[:, :, 0] = np.clip(ref[:, :, 0] + 0.35 * lamp_glow, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + 0.22 * lamp_glow, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + 0.04 * lamp_glow, 0.0, 1.0)

    # ── Wet cobblestone ground: dark, reflective ──────────────────────────────
    ground_mask = np.clip((ys - 0.62) / 0.06, 0.0, 1.0).astype(np.float32)
    gnd_r = 0.10 + 0.04 * (1 - ys)
    gnd_g = 0.11 + 0.04 * (1 - ys)
    gnd_b = 0.15 + 0.05 * (1 - ys)
    # Cobblestone texture: grid-like noise
    cob_noise = gaussian_filter(
        rng.uniform(0, 1, (H, W)).astype(np.float32), sigma=(0.5, 0.5)
    )
    cob_grid_y = 0.5 + 0.5 * np.sin(ys * H / 18.0 * np.pi)
    cob_grid_x = 0.5 + 0.5 * np.cos(xs * W / 28.0 * np.pi)
    cob_texture = (cob_grid_y * cob_grid_x * cob_noise * 0.06).astype(np.float32)
    gnd_r = np.clip(gnd_r + cob_texture, 0.0, 1.0)
    gnd_g = np.clip(gnd_g + cob_texture, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1 - ground_mask) + gnd_r * ground_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - ground_mask) + gnd_g * ground_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - ground_mask) + gnd_b * ground_mask

    # ── Red booth reflection in puddles: amber-red shimmer on the ground ──────
    puddle_cx, puddle_cy = 0.42, 0.84
    puddle_dist = np.sqrt(
        ((xs - puddle_cx) / 0.18) ** 2 + ((ys - puddle_cy) / 0.08) ** 2
    )
    puddle_mask = np.clip(1.0 - puddle_dist, 0.0, 1.0) ** 1.4
    puddle_mask = gaussian_filter(puddle_mask.astype(np.float32), sigma=5) * ground_mask
    ref[:, :, 0] = np.clip(ref[:, :, 0] + 0.28 * puddle_mask, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + 0.04 * puddle_mask, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] - 0.04 * puddle_mask, 0.0, 1.0)

    # ── Telephone booth: central, occupying 55–62% vertical ───────────────────
    # Booth outer rectangle
    booth_x0, booth_x1 = 0.28, 0.58   # left/right fraction of width
    booth_y0, booth_y1 = 0.25, 0.88   # top/bottom fraction of height

    bx0p, bx1p = int(booth_x0 * W), int(booth_x1 * W)
    by0p, by1p = int(booth_y0 * H), int(booth_y1 * H)

    # Frame/body: vivid cadmium red
    booth_x_mask = np.clip(
        np.minimum((xs - booth_x0) / 0.015, (booth_x1 - xs) / 0.015), 0.0, 1.0
    ).astype(np.float32)
    booth_y_mask = np.clip(
        np.minimum((ys - booth_y0) / 0.012, (booth_y1 - ys) / 0.012), 0.0, 1.0
    ).astype(np.float32)
    booth_frame = np.minimum(booth_x_mask, booth_y_mask)

    # Fill interior of booth: dark with interior glow
    interior_x = np.clip((xs - (booth_x0 + 0.02)) / 0.01, 0.0, 1.0) * \
                 np.clip(((booth_x1 - 0.02) - xs) / 0.01, 0.0, 1.0)
    interior_y = np.clip((ys - (booth_y0 + 0.015)) / 0.01, 0.0, 1.0) * \
                 np.clip(((booth_y1 - 0.015) - ys) / 0.01, 0.0, 1.0)
    interior_mask = np.minimum(interior_x, interior_y).astype(np.float32)

    # Interior: dark blue-grey with warm amber glow from top
    interior_glow = np.clip(1.0 - (ys - booth_y0) / (booth_y1 - booth_y0), 0.0, 1.0) ** 2
    int_r = 0.22 + 0.40 * interior_glow
    int_g = 0.18 + 0.22 * interior_glow
    int_b = 0.14 + 0.06 * interior_glow

    # Paint interior
    ref[:, :, 0] = ref[:, :, 0] * (1 - interior_mask) + int_r * interior_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - interior_mask) + int_g * interior_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - interior_mask) + int_b * interior_mask

    # Paint red frame over interior
    booth_red_r = 0.85
    booth_red_g = 0.06
    booth_red_b = 0.05
    # Frame edges
    ref[:, :, 0] = np.clip(
        ref[:, :, 0] * (1 - booth_frame) + booth_red_r * booth_frame, 0.0, 1.0
    )
    ref[:, :, 1] = np.clip(
        ref[:, :, 1] * (1 - booth_frame) + booth_red_g * booth_frame, 0.0, 1.0
    )
    ref[:, :, 2] = np.clip(
        ref[:, :, 2] * (1 - booth_frame) + booth_red_b * booth_frame, 0.0, 1.0
    )

    # Booth crown: arched top panel, solid red slightly brighter
    crown_y0, crown_y1 = booth_y0 - 0.04, booth_y0 + 0.015
    crown_mask = np.clip(
        np.minimum((xs - booth_x0) / 0.008, (booth_x1 - xs) / 0.008), 0.0, 1.0
    ) * np.clip(
        np.minimum((ys - crown_y0) / 0.008, (crown_y1 - ys) / 0.008), 0.0, 1.0
    )
    ref[:, :, 0] = np.clip(ref[:, :, 0] + 0.10 * crown_mask, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] - 0.02 * crown_mask, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] - 0.02 * crown_mask, 0.0, 1.0)

    # Window glazing bars: thin horizontal and vertical dark lines within booth
    n_panes_v = 4   # 4 panes per tall window
    win_x0, win_x1 = booth_x0 + 0.025, booth_x1 - 0.025
    win_y0, win_y1 = booth_y0 + 0.04, booth_y0 + 0.65 * (booth_y1 - booth_y0)
    # Vertical center bar
    cbar_dist = np.abs(xs - 0.430) / 0.008
    cbar_mask = np.clip(1.0 - cbar_dist, 0.0, 1.0) * interior_mask
    ref[:, :, 0] = np.clip(ref[:, :, 0] + 0.50 * cbar_mask, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + 0.02 * cbar_mask, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + 0.02 * cbar_mask, 0.0, 1.0)
    # Horizontal glazing bars
    for k in range(1, n_panes_v):
        hy = win_y0 + k * (win_y1 - win_y0) / n_panes_v
        hbar_dist = np.abs(ys - hy) / 0.006
        hbar_mask = np.clip(1.0 - hbar_dist, 0.0, 1.0) * interior_mask
        ref[:, :, 0] = np.clip(ref[:, :, 0] + 0.50 * hbar_mask, 0.0, 1.0)
        ref[:, :, 1] = np.clip(ref[:, :, 1] + 0.02 * hbar_mask, 0.0, 1.0)
        ref[:, :, 2] = np.clip(ref[:, :, 2] + 0.02 * hbar_mask, 0.0, 1.0)

    # Interior lamp: bright warm point at top centre
    lamp2_cx, lamp2_cy = 0.430, booth_y0 + 0.04
    lamp2_dist = np.sqrt(
        ((xs - lamp2_cx) / 0.04) ** 2 + ((ys - lamp2_cy) / 0.03) ** 2
    )
    lamp2_glow = np.clip(1.0 - lamp2_dist, 0.0, 1.0) ** 1.5
    lamp2_glow = gaussian_filter(lamp2_glow.astype(np.float32), sigma=8) * interior_mask
    ref[:, :, 0] = np.clip(ref[:, :, 0] + 0.60 * lamp2_glow, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + 0.40 * lamp2_glow, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + 0.10 * lamp2_glow, 0.0, 1.0)

    # ── Rain streaks: diagonal near-white lines ────────────────────────────────
    # Simulated by anisotropic noise field elongated diagonally
    rain_noise = rng.standard_normal((H, W)).astype(np.float32)
    # Shift noise diagonally to simulate right-to-left rain
    from scipy.ndimage import affine_transform
    angle_rad = -0.38   # ~22 degrees left lean
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
    matrix = np.array([[cos_a, sin_a], [-sin_a, cos_a]])
    rain_noise = affine_transform(rain_noise, matrix, offset=[H * 0.1, 0],
                                  mode='wrap')
    # Elongate vertically (rain streaks are tall and narrow)
    rain_streaks = gaussian_filter(rain_noise, sigma=(12, 0.3))
    rain_streaks = np.clip((rain_streaks - rain_streaks.mean()) / rain_streaks.std(), -2.5, 2.5)
    rain_gate = np.clip((rain_streaks - 1.5) * 3.0, 0.0, 1.0).astype(np.float32)
    rain_opacity = 0.22
    ref[:, :, 0] = np.clip(ref[:, :, 0] + rain_opacity * rain_gate, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + rain_opacity * rain_gate, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + rain_opacity * rain_gate * 0.85, 0.0, 1.0)

    return np.clip(ref, 0.0, 1.0).astype(np.float32)


def main():
    print("=== Session 193: Red Booth in the Kusama Rain ===")
    print(f"Canvas: {W}x{H}")

    ref = build_reference()
    print("Reference built.")

    p = Painter(W, H)

    # Ground: very dark Prussian blue-grey — stormy night
    print("  tone_ground ...")
    p.tone_ground((0.12, 0.14, 0.22), texture_strength=0.003)

    # Seed canvas from reference
    print("  seeding canvas from reference ...")
    import numpy as _np
    _W, _H = p.canvas.w, p.canvas.h
    _buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((_H, _W, 4)).copy()
    _ref_u8 = (_np.clip(ref, 0.0, 1.0) * 255).astype(_np.uint8)
    _seed_op = 0.88
    _buf[:, :, 2] = _np.clip(
        _buf[:, :, 2] * (1 - _seed_op) + _ref_u8[:, :, 0] * _seed_op, 0, 255
    ).astype(_np.uint8)
    _buf[:, :, 1] = _np.clip(
        _buf[:, :, 1] * (1 - _seed_op) + _ref_u8[:, :, 1] * _seed_op, 0, 255
    ).astype(_np.uint8)
    _buf[:, :, 0] = _np.clip(
        _buf[:, :, 0] * (1 - _seed_op) + _ref_u8[:, :, 2] * _seed_op, 0, 255
    ).astype(_np.uint8)
    p.canvas.surface.get_data()[:] = _buf.tobytes()
    p.canvas.surface.mark_dirty()

    # Underpainting — lay in atmospheric masses
    print("  underpainting ...")
    p.underpainting(ref, stroke_size=60, n_strokes=20)

    # Block in — broad colour areas: red booth, dark sky, wet cobblestones
    print("  block_in ...")
    p.block_in(ref, stroke_size=32)

    # Build form — tighten the booth structure
    print("  build_form ...")
    p.build_form(ref, stroke_size=14)

    # ── Kusama infinity dots: the primary stylistic pass ──────────────────────
    # Large bold dots, Kusama palette cycling through the storm atmosphere
    print("  kusama_infinity_dot_pass (104th mode) — primary layer ...")
    STORM_DOT_PALETTE = [
        (0.10, 0.10, 0.22),   # deep Prussian blue-black (rain, sky)
        (0.82, 0.06, 0.06),   # cadmium red (booth, hot dots)
        (0.16, 0.20, 0.42),   # cobalt blue-grey (wet stones)
        (0.62, 0.06, 0.72),   # deep violet (shadow pulse)
        (0.82, 0.52, 0.08),   # amber gold (lamp glow)
        (0.86, 0.86, 0.92),   # near-white (rain streaks as dots)
    ]
    p.kusama_infinity_dot_pass(
        n_seeds=12,
        ring_step=40,
        dot_radius=16,
        dot_spacing=44,
        jitter_frac=0.20,
        palette=STORM_DOT_PALETTE,
        opacity=0.68,
    )

    # ── Secondary fine dot layer: smaller dots filling gaps ───────────────────
    print("  kusama_infinity_dot_pass — secondary fine layer ...")
    FINE_STORM_PALETTE = [
        (0.82, 0.06, 0.06),   # red
        (0.10, 0.10, 0.22),   # dark blue
        (0.96, 0.96, 0.96),   # white (rain)
        (0.82, 0.52, 0.08),   # amber
    ]
    p.kusama_infinity_dot_pass(
        n_seeds=8,
        ring_step=22,
        dot_radius=8,
        dot_spacing=24,
        jitter_frac=0.28,
        palette=FINE_STORM_PALETTE,
        opacity=0.38,
    )

    # Beksinski atmosphere pass — adds oppressive stormy depth to the sky zones
    print("  beksinski_dystopian_atmosphere_pass ...")
    p.beksinski_dystopian_atmosphere_pass(
        ash_pull=0.30,
        shadow_deepen=0.22,
        ember_glow=0.10,
        grain_strength=0.012,
        opacity=0.22,
    )

    # Canvas grain — subtle texture
    print("  canvas_grain_pass ...")
    p.canvas_grain_pass(
        noise_scale=1.0,
        noise_strength=0.008,
        sharpness=0.05,
        luma_lo=0.05,
        luma_hi=0.95,
        opacity=0.10,
    )

    # Cool blue glaze over everything — the rain-soaked atmosphere
    print("  glaze ...")
    p.glaze((0.14, 0.18, 0.32), opacity=0.06)

    # Finish
    print("  finish ...")
    p.finish(vignette=0.22, crackle=False)

    p.save(OUTPUT)
    print(f"\nSaved -> {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
