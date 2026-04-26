"""
run_kusama_pumpkin_obliteration.py — Session 193

Paints a Yayoi Kusama-inspired 'Pumpkin Obliteration' scene: a single large
yellow pumpkin completely consumed by concentric rings of vivid polka dots
radiating outward from multiple explosion centres, dissolving the boundary
between figure and ground until only the dots remain — Kusama's 'Infinity Net'
doctrine applied to her most iconic subject.

The yellow ground, bold graphic dots, and obsessive all-over coverage evoke
'Pumpkin' (1994) and 'All the Eternal Love I Have for the Pumpkins' (2016).

Session 193 pass used:
  kusama_infinity_dot_pass  (104th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kusama_pumpkin_obliteration.png")
W, H = 800, 800   # square format — Kusama frequently worked square


def build_reference() -> np.ndarray:
    """
    Vivid reference for the Kusama pumpkin scene.

    Zones:
      - Sunshine yellow background — Kusama's characteristic warm ground
      - Central pumpkin: large globose form with distinct lobes, deep orange-gold
      - Pumpkin stem: dark khaki-green at top centre
      - Scattered shadow areas: hints of depth beneath the pumpkin
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0, 1, H)[:, None]
    xs = np.linspace(0, 1, W)[None, :]
    rng = np.random.default_rng(193)

    # ── Sunshine yellow background ────────────────────────────────────────────
    ref[:, :, 0] = 0.96
    ref[:, :, 1] = 0.88
    ref[:, :, 2] = 0.06

    # ── Pumpkin body: large globose form, centre-bottom ────────────────────────
    px, py = 0.50, 0.60   # pumpkin centre (x, y fraction)
    pr_x, pr_y = 0.30, 0.28   # horizontal and vertical radii

    # Base pumpkin shape: squash ellipse
    pumpkin_dist = np.sqrt(
        ((xs - px) / pr_x) ** 2 +
        ((ys - py) / pr_y) ** 2
    )
    pumpkin_mask = np.clip(1.0 - pumpkin_dist, 0.0, 1.0).astype(np.float32)
    pumpkin_mask = pumpkin_mask ** 0.8   # gentler falloff for rounder look

    # Pumpkin colour: warm cadmium orange-gold
    pump_r = 0.93 - 0.10 * np.abs(xs - px)
    pump_g = 0.62 - 0.08 * np.abs(ys - py) * 2.0
    pump_b = 0.04

    # ── Pumpkin lobes: N vertical sinusoidal ridges modulating brightness ──────
    n_lobes = 9
    lobe_freq = n_lobes * np.pi
    lobe_wave = 0.5 + 0.5 * np.cos(lobe_freq * (xs - px))  # peaks at lobe centres
    lobe_dark = 1.0 - 0.18 * (1.0 - lobe_wave)              # darken between lobes
    pump_r = np.clip(pump_r * lobe_dark, 0.0, 1.0)
    pump_g = np.clip(pump_g * lobe_dark, 0.0, 1.0)

    ref[:, :, 0] = ref[:, :, 0] * (1 - pumpkin_mask) + pump_r * pumpkin_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - pumpkin_mask) + pump_g * pumpkin_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - pumpkin_mask) + pump_b * pumpkin_mask

    # ── Pumpkin stem: dark green rectangle at top of pumpkin ──────────────────
    stem_cx, stem_cy = px, py - pr_y - 0.028
    stem_dist = np.sqrt(
        ((xs - stem_cx) / 0.022) ** 2 +
        ((ys - stem_cy) / 0.038) ** 2
    )
    stem_mask = np.clip(1.0 - stem_dist, 0.0, 1.0).astype(np.float32) ** 1.5
    ref[:, :, 0] = np.clip(ref[:, :, 0] - 0.52 * stem_mask, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] - 0.18 * stem_mask, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + 0.08 * stem_mask, 0.0, 1.0)

    # ── Pumpkin shadow: soft dark pool beneath ────────────────────────────────
    shad_cy = py + pr_y * 0.85
    shad_dist = np.sqrt(
        ((xs - px) / 0.32) ** 2 +
        ((ys - shad_cy) / 0.055) ** 2
    )
    shad_mask = np.clip(1.0 - shad_dist, 0.0, 1.0).astype(np.float32) ** 1.2
    shad_mask = gaussian_filter(shad_mask, sigma=6.0)
    ref[:, :, 0] = np.clip(ref[:, :, 0] - 0.28 * shad_mask, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] - 0.22 * shad_mask, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] - 0.04 * shad_mask, 0.0, 1.0)

    return np.clip(ref, 0.0, 1.0).astype(np.float32)


def main():
    print("=== Yayoi Kusama: Pumpkin Obliteration (Session 193) ===")
    print(f"Canvas: {W}x{H}")

    ref = build_reference()
    print("Reference built.")

    p = Painter(W, H)

    # Ground: brilliant white gesso — Kusama's obliteration ground
    print("  tone_ground ...")
    p.tone_ground((0.97, 0.97, 0.96), texture_strength=0.002)

    # Seed canvas from vivid reference colour field
    print("  seeding canvas from reference ...")
    import numpy as _np
    _W, _H = p.canvas.w, p.canvas.h
    _buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((_H, _W, 4)).copy()
    _ref_u8 = (_np.clip(ref, 0.0, 1.0) * 255).astype(_np.uint8)
    _seed_op = 0.90
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

    # Light underpainting — establish form before dots obliterate it
    print("  underpainting ...")
    p.underpainting(ref, stroke_size=55, n_strokes=18)

    # Block in broad colour areas
    print("  block_in ...")
    p.block_in(ref, stroke_size=28)

    # Kusama infinity dots — the defining obliteration pass
    print("  kusama_infinity_dot_pass (104th mode) ...")
    KUSAMA_PALETTE = [
        (0.06, 0.06, 0.06),   # jet black — Kusama's primary dot colour
        (0.92, 0.08, 0.08),   # vivid red
        (0.06, 0.12, 0.82),   # cobalt blue
        (0.62, 0.06, 0.78),   # deep violet
        (0.10, 0.70, 0.18),   # vivid green
        (0.96, 0.60, 0.06),   # cadmium orange
    ]
    p.kusama_infinity_dot_pass(
        n_seeds=11,
        ring_step=38,
        dot_radius=16,
        dot_spacing=42,
        jitter_frac=0.18,
        palette=KUSAMA_PALETTE,
        opacity=0.78,
    )

    # Second dot pass at smaller scale — Kusama layers dot densities
    print("  kusama_infinity_dot_pass (secondary fine layer) ...")
    FINE_PALETTE = [
        (0.06, 0.06, 0.06),   # black
        (0.98, 0.98, 0.98),   # white
        (0.92, 0.08, 0.08),   # red
    ]
    p.kusama_infinity_dot_pass(
        n_seeds=7,
        ring_step=20,
        dot_radius=7,
        dot_spacing=22,
        jitter_frac=0.25,
        palette=FINE_PALETTE,
        opacity=0.42,
    )

    # Finish — no vignette, no crackle — Kusama is hard-edged and graphic
    print("  finish ...")
    p.finish(vignette=0.04, crackle=False)

    p.save(OUTPUT)
    print(f"\nSaved -> {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
