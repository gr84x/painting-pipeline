"""
run_riley_ancient_olive.py — Session 195 (Discord painting)

"The Geometry of the Old Olive"

Painting description:
  A single ancient olive tree, seen from ground level looking up and slightly
  right — the viewer is crouching beside the enormous roots. The massive
  twisted trunk splits into three great limbs that reach upward and outward,
  their silver-grey bark patterned with deep spiral furrows. The tree is in
  full summer leaf: masses of silver-green foliage shimmer against a blazing
  afternoon sky. The emotional state of the tree: profound patience — centuries
  of endurance made visible in the tortured, beautiful form of the trunk.

  Environment: a rocky Mediterranean hillside at midday — parched ochre
  limestone ground, dry grasses, distant blue sea haze through a gap in the
  foliage. Sky: intense cobalt blue, bleached white near the horizon. The
  boundary between foliage and sky is crisp and vibrating.

Technique: Bridget Riley Op Art wave pass (riley_op_art_wave_pass, 106th mode).
  The olive's tonal structure drives sinusoidal wave frequency: dark twisted bark
  vibrates at high frequency; bright sky breathes slowly and wide. Two-pass wave
  field — primary sepia/white waves encode tonal structure; secondary interference
  pass adds fine moiré ripple in the darkest bark zones.

Palette: warm sepia umber (#2B1A0A) against aged white (#F5EFE0) — monochromatic,
  as if a Mediterranean photograph has been re-encoded into pure frequency.

Mood: timeless, meditative, mathematically beautiful. Ancient organic form
  translated into absolute geometric order. The paradox of stillness vibrating.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "riley_ancient_olive.png"
)
W, H = 800, 1000   # portrait — tall to capture trunk-to-canopy sweep


def build_reference() -> np.ndarray:
    """
    Synthetic reference encoding the tonal structure of the olive tree scene.

    Tonal regions (used purely for luminance → wave frequency mapping):
      - Sky: bright cobalt blue → high luminance → slow, wide waves
      - Foliage masses: medium-light silver-green → moderate frequency
      - Major trunk and limbs: very dark twisted forms → tight, dense vibration
      - Ground: warm mid-tone limestone → moderate-slow waves
      - Root system: near-black at base → maximum frequency

    The reference is NEVER rendered directly — it only drives freq modulation.
    """
    rng = np.random.default_rng(195_2)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Sky: bright cobalt — upper 45% of canvas ─────────────────────────────
    sky_horizon = 0.45
    sky_t = np.clip(ys / sky_horizon, 0.0, 1.0)
    sky_lum = 0.88 - 0.18 * sky_t    # near-white at top, cobalt grey near horizon
    ref[:, :, 0] = sky_lum
    ref[:, :, 1] = sky_lum
    ref[:, :, 2] = sky_lum

    # ── Ground: warm limestone — lower 30% ────────────────────────────────────
    ground_start = 0.72
    ground_t = np.clip((ys - ground_start) / (1.0 - ground_start), 0.0, 1.0)
    ground_lum = 0.55 + 0.10 * (1.0 - ground_t)
    ref[:, :, 0] = np.where(ys > ground_start, ground_lum, ref[:, :, 0])
    ref[:, :, 1] = np.where(ys > ground_start, ground_lum * 0.95, ref[:, :, 1])
    ref[:, :, 2] = np.where(ys > ground_start, ground_lum * 0.88, ref[:, :, 2])

    # ── Foliage masses: medium-light in mid-zone ──────────────────────────────
    # Three major foliage clouds at upper left, upper right, upper centre
    for (fcx, fcy, frx, fry) in [
        (0.30, 0.22, 0.22, 0.28),   # left canopy mass
        (0.62, 0.18, 0.25, 0.22),   # right canopy mass
        (0.48, 0.32, 0.18, 0.20),   # centre-top canopy bridge
    ]:
        dist = _np.sqrt(((xs - fcx) / frx) ** 2 + ((ys - fcy) / fry) ** 2)
        foliage_mask = np.clip(1.0 - dist, 0.0, 1.0) ** 0.6
        foliage_lum = 0.68 + rng.random((H, W)).astype(np.float32) * 0.08
        ref[:, :, 0] = ref[:, :, 0] * (1 - foliage_mask) + foliage_lum * foliage_mask
        ref[:, :, 1] = ref[:, :, 1] * (1 - foliage_mask) + foliage_lum * 0.98 * foliage_mask
        ref[:, :, 2] = ref[:, :, 2] * (1 - foliage_mask) + foliage_lum * 0.90 * foliage_mask

    # ── Main trunk: very dark, twisted — centre of canvas ─────────────────────
    # Primary trunk: lower centre
    trunk_cx = 0.48
    trunk_top_y = 0.38
    trunk_bot_y = 0.72
    trunk_half_w_bot = 0.08
    trunk_half_w_top = 0.04

    for row_idx in range(H):
        y_frac = row_idx / float(H)
        if trunk_top_y <= y_frac <= trunk_bot_y:
            t = (y_frac - trunk_top_y) / (trunk_bot_y - trunk_top_y)
            half_w = trunk_half_w_top + (trunk_half_w_bot - trunk_half_w_top) * t
            # Slight sinuous taper (twist of trunk)
            cx_here = trunk_cx + 0.03 * np.sin(t * np.pi * 3.5)
            col_l = int(np.clip((cx_here - half_w) * W, 0, W - 1))
            col_r = int(np.clip((cx_here + half_w) * W, 0, W - 1))
            trunk_lum = 0.08 + rng.random(col_r - col_l + 1) * 0.06
            ref[row_idx, col_l:col_r + 1, 0] = trunk_lum
            ref[row_idx, col_l:col_r + 1, 1] = trunk_lum * 0.96
            ref[row_idx, col_l:col_r + 1, 2] = trunk_lum * 0.92

    # ── Three major limbs radiating from split point ──────────────────────────
    split_y = 0.40
    split_x = 0.49
    limb_specs = [
        (split_x - 0.02, split_y, 0.18, 0.18, 0.035),  # left limb
        (split_x + 0.02, split_y, 0.72, 0.10, 0.030),  # right limb
        (split_x,        split_y, 0.50, 0.22, 0.025),  # centre limb
    ]
    for (lx, ly, target_x, target_y, lw) in limb_specs:
        n_segs = 20
        for si in range(n_segs):
            t0 = si / float(n_segs)
            t1 = (si + 1) / float(n_segs)
            x0 = lx + (target_x - lx) * t0
            y0 = ly + (target_y - ly) * t0
            x1 = lx + (target_x - lx) * t1
            y1 = ly + (target_y - ly) * t1
            # Draw as thick ellipse patch
            cx = (x0 + x1) / 2.0
            cy = (y0 + y1) / 2.0
            limb_dist = np.sqrt(((xs - cx) / lw) ** 2 + ((ys - cy) / (lw * 0.4)) ** 2)
            limb_mask = np.clip(1.0 - limb_dist, 0.0, 1.0) ** 1.2
            limb_lum = 0.10 + rng.random((H, W)).astype(np.float32) * 0.05
            ref[:, :, 0] = ref[:, :, 0] * (1 - limb_mask) + limb_lum * limb_mask
            ref[:, :, 1] = ref[:, :, 1] * (1 - limb_mask) + limb_lum * 0.96 * limb_mask
            ref[:, :, 2] = ref[:, :, 2] * (1 - limb_mask) + limb_lum * 0.92 * limb_mask

    # ── Root flare: near-black at very base ───────────────────────────────────
    root_zone = np.clip((ys - 0.68) / 0.08, 0.0, 1.0)
    root_x_mask = np.clip(1.0 - np.abs(xs - trunk_cx) / 0.14, 0.0, 1.0)
    root_mask = root_zone * root_x_mask ** 0.5
    root_lum = 0.06
    ref[:, :, 0] = ref[:, :, 0] * (1 - root_mask) + root_lum * root_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - root_mask) + root_lum * root_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - root_mask) + root_lum * root_mask

    return np.clip(ref, 0.0, 1.0)


# numpy alias used inside the function
import numpy as _np


def main() -> str:
    """Paint 'The Geometry of the Old Olive' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H)

    # ── Ground: aged white — warm, slightly yellowed parchment ground ──────────
    p.tone_ground((0.96, 0.93, 0.87), texture_strength=0.0)

    # ── Primary Riley wave pass: sepia/ivory — 100 waves, strong freq mod ─────
    # Sepia: rgb(43, 26, 10) / 255 ≈ (0.169, 0.102, 0.039)
    # Aged white: rgb(245, 239, 224) / 255 ≈ (0.961, 0.937, 0.878)
    p.riley_op_art_wave_pass(
        ref_pil,
        n_waves=110,
        base_amplitude=13.0,
        freq_modulation=0.90,
        base_frequency=0.009,
        color_a=(0.169, 0.102, 0.039),   # warm sepia umber
        color_b=(0.961, 0.937, 0.878),   # aged ivory white
        opacity=0.92,
        seed=195,
    )

    # ── Second pass: fine interference moiré in dark (bark) zones ─────────────
    # Uses tighter base frequency, less amplitude — adds density to dark regions
    p.riley_op_art_wave_pass(
        ref_pil,
        n_waves=30,
        base_amplitude=5.5,
        freq_modulation=0.55,
        base_frequency=0.022,
        color_a=(0.12, 0.07, 0.02),      # deeper shadow sepia
        color_b=(0.94, 0.91, 0.84),      # lighter ground tone
        opacity=0.22,
        seed=7777,
    )

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
