"""
run_agnes_martin_crane.py — Session 192

Paints an Agnes Martin-inspired scene: a solitary white crane standing in
shallow morning mist over still water, rendered in Martin's meditative
ruled-line technique with pale grey-blue wash and barely-there tonal banding.

The vast pale ground, horizontal meditation lines, and quiet palette evoke
'Night Sea' (1963) and 'Loving' (1999) — where the subject dissolves into
the surface and the surface becomes the subject.

Session 192 pass used:
  agnes_martin_meditation_lines_pass  (103rd distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agnes_martin_crane.png")
W, H = 800, 800   # Agnes Martin always worked square


def build_reference() -> np.ndarray:
    """
    Pale, near-empty reference for the Agnes Martin crane scene.

    Zones (top -> bottom):
      - Vast pale sky: bleached linen with barely-perceptible horizon band
      - Horizon mist: soft grey-blue atmospheric haze
      - Still water surface: mirror of the sky, slightly darker
      - Reed shadow band: faint vertical marks in lower foreground
      - Solitary white crane: standing centre-left, near horizon line
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0, 1, H)[:, None]
    xs = np.linspace(0, 1, W)[None, :]
    rng = np.random.default_rng(192)

    # ── Sky: pale bleached linen with barely-perceptible gradient ────────────
    # Near-white at top, very slightly warmer towards horizon
    sky_r = 0.92 + 0.04 * ys
    sky_g = 0.91 + 0.04 * ys
    sky_b = 0.90 + 0.04 * ys
    ref[:, :, 0] = sky_r
    ref[:, :, 1] = sky_g
    ref[:, :, 2] = sky_b

    # ── Horizon mist band: soft grey-blue (Martin's 'Night Sea' tone) ────────
    horiz_y = 0.54
    horiz_sigma = 0.055
    horiz_gate = np.exp(-((ys - horiz_y) ** 2) / (2 * horiz_sigma ** 2)).astype(np.float32)
    ref[:, :, 0] = np.clip(ref[:, :, 0] - 0.06 * horiz_gate, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] - 0.04 * horiz_gate, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + 0.03 * horiz_gate, 0.0, 1.0)

    # ── Water surface: below horizon line, mirror of sky, slightly cooler ────
    water_mask = np.clip((ys - 0.56) / 0.04, 0.0, 1.0).astype(np.float32)
    water_r = 0.84 + 0.06 * (1 - ys)
    water_g = 0.86 + 0.05 * (1 - ys)
    water_b = 0.90 + 0.04 * (1 - ys)
    # Barely-perceptible horizontal ripple in the water
    ripple = gaussian_filter(
        rng.uniform(0, 1, (H, W)).astype(np.float32), sigma=(0.8, 35.0)
    )
    water_r = np.clip(water_r + 0.018 * (ripple - 0.5), 0.0, 1.0)
    water_g = np.clip(water_g + 0.015 * (ripple - 0.5), 0.0, 1.0)
    water_b = np.clip(water_b + 0.010 * (ripple - 0.5), 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1 - water_mask) + water_r * water_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - water_mask) + water_g * water_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - water_mask) + water_b * water_mask

    # ── Reed shadow: faint vertical smears in lower third ────────────────────
    reed_mask = np.clip((ys - 0.72) / 0.08, 0.0, 1.0).astype(np.float32)
    reed_noise = gaussian_filter(
        rng.uniform(0, 1, (H, W)).astype(np.float32), sigma=(8.0, 0.9)
    )
    reed_gate = np.clip((reed_noise - 0.70) * 5.0, 0.0, 1.0) * reed_mask
    ref[:, :, 0] = np.clip(ref[:, :, 0] - 0.12 * reed_gate, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] - 0.10 * reed_gate, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] - 0.08 * reed_gate, 0.0, 1.0)

    # ── White crane: standing at horizon line, slightly left of centre ────────
    crane_cx = 0.40
    crane_cy = 0.52      # at horizon line

    # Body: elongated oval, tilted slightly
    body_ry = 0.042
    body_rx = 0.022
    body_dist = np.sqrt(
        ((xs - crane_cx) / body_rx) ** 2 +
        ((ys - crane_cy) / body_ry) ** 2
    )
    body_mask = np.clip(1.0 - body_dist, 0.0, 1.0).astype(np.float32) ** 2.0

    # Neck: narrow elongated oval rising from body
    neck_cx = crane_cx + 0.005
    neck_cy = crane_cy - 0.075
    neck_dist = np.sqrt(
        ((xs - neck_cx) / 0.010) ** 2 +
        ((ys - neck_cy) / 0.048) ** 2
    )
    neck_mask = np.clip(1.0 - neck_dist, 0.0, 1.0).astype(np.float32) ** 2.2

    # Head: small circle at top of neck
    head_cy = crane_cy - 0.126
    head_dist = np.sqrt(
        ((xs - neck_cx) / 0.016) ** 2 +
        ((ys - head_cy) / 0.014) ** 2
    )
    head_mask = np.clip(1.0 - head_dist, 0.0, 1.0).astype(np.float32) ** 2.0

    # Red crown: tiny ellipse on top of head (Sandhill/Whooping crane marker)
    crown_cy = head_cy - 0.017
    crown_dist = np.sqrt(
        ((xs - neck_cx) / 0.009) ** 2 +
        ((ys - crown_cy) / 0.008) ** 2
    )
    crown_mask = np.clip(1.0 - crown_dist, 0.0, 1.0).astype(np.float32) ** 2.0

    # Legs: two thin vertical lines descending below body into water
    for leg_x in (crane_cx - 0.007, crane_cx + 0.007):
        leg_dist = np.sqrt(
            ((xs - leg_x) / 0.004) ** 2 +
            ((ys - (crane_cy + 0.065)) / 0.048) ** 2
        )
        leg_mask = np.clip(1.0 - leg_dist, 0.0, 1.0).astype(np.float32) ** 3.0
        ref[:, :, 0] = np.clip(ref[:, :, 0] - 0.22 * leg_mask, 0.0, 1.0)
        ref[:, :, 1] = np.clip(ref[:, :, 1] - 0.20 * leg_mask, 0.0, 1.0)
        ref[:, :, 2] = np.clip(ref[:, :, 2] - 0.18 * leg_mask, 0.0, 1.0)

    # Combined crane mask
    crane_mask = np.maximum(
        np.maximum(body_mask, neck_mask), head_mask
    )

    # Crane colour: pure white with barely-perceptible grey shading on one side
    crane_r = np.clip(0.97 - 0.08 * (xs - crane_cx + 0.03), 0.86, 0.97)
    crane_g = np.clip(0.96 - 0.07 * (xs - crane_cx + 0.03), 0.86, 0.96)
    crane_b = np.clip(0.95 - 0.05 * (xs - crane_cx + 0.03), 0.87, 0.95)

    ref[:, :, 0] = ref[:, :, 0] * (1 - crane_mask) + crane_r * crane_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - crane_mask) + crane_g * crane_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - crane_mask) + crane_b * crane_mask

    # Red crown (painted last, over crane head)
    ref[:, :, 0] = np.clip(ref[:, :, 0] + 0.55 * crown_mask, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] - 0.20 * crown_mask, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] - 0.25 * crown_mask, 0.0, 1.0)

    return np.clip(ref, 0.0, 1.0).astype(np.float32)


def main():
    print("=== Agnes Martin: Crane at Morning (Session 192) ===")
    print(f"Canvas: {W}x{H}")

    ref = build_reference()
    print("Reference built.")

    p = Painter(W, H)

    # Ground: bleached linen — Agnes Martin's unprimed canvas
    print("  tone_ground ...")
    p.tone_ground((0.95, 0.93, 0.90), texture_strength=0.008)

    # Seed canvas lightly from reference colour field
    print("  seeding canvas from reference ...")
    import numpy as _np
    _W, _H = p.canvas.w, p.canvas.h
    _buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((_H, _W, 4)).copy()
    _ref_u8 = (_np.clip(ref, 0.0, 1.0) * 255).astype(_np.uint8)
    _seed_op = 0.85
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

    # Very light underpainting — Martin's washes are gossamer-thin
    print("  underpainting ...")
    p.underpainting(ref, stroke_size=60, n_strokes=20)

    # Agnes Martin meditation lines — the defining pass
    print("  agnes_martin_meditation_lines_pass (103rd mode) ...")
    p.agnes_martin_meditation_lines_pass(
        n_lines=320,
        tremor_sigma=1.2,
        breathe_freq=2.5,
        line_opacity=0.52,
        wash_color=(0.84, 0.88, 0.92),
        wash_opacity=0.10,
        tone_drift=0.030,
        opacity=0.68,
    )

    # Canvas grain — very subtle linen texture
    print("  canvas_grain_pass ...")
    p.canvas_grain_pass(
        noise_scale=1.0,
        noise_strength=0.006,
        sharpness=0.04,
        luma_lo=0.10,
        luma_hi=0.98,
        opacity=0.12,
    )

    # Cool blue-grey atmospheric glaze — Martin's 'pale veil' finish
    print("  glaze ...")
    p.glaze((0.80, 0.84, 0.90), opacity=0.018)

    # Finish — minimal vignette
    print("  finish ...")
    p.finish(vignette=0.10, crackle=False)

    p.save(OUTPUT)
    print(f"\nSaved -> {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
