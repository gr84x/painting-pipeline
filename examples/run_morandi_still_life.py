"""
run_morandi_still_life.py — Session 188

Paints a Morandi-inspired interior scene: a seated figure in quiet repose,
sharing the atmosphere with bottles on a windowsill — all rendered in Morandi's
chalky, dust-muted palette through the two new Session 188 passes.

Session 188 passes used:
  morandi_tonal_unity_pass  (96th distinct mode)
  palette_proximity_pull_pass (97th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "morandi_still_life.png")
W, H = 780, 1040


def build_reference() -> np.ndarray:
    """
    Build a programmatic colour-field reference image representing the scene:
      - warm ochre-grey wall as background
      - soft window light from upper-left
      - figure occupying the vertical centre (warm flesh-sage zone)
      - a lower foreground zone in deep warm ochre-brown
      - a narrow windowsill zone on the right with subtle cool blues
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # Coordinate grids (0..1)
    ys = np.linspace(0, 1, H)[:, None]
    xs = np.linspace(0, 1, W)[None, :]

    # ── Background: dusty ochre-grey wall ──────────────────────────────────
    bg_r = 0.70 + 0.06 * (1.0 - ys)         # slightly lighter at top
    bg_g = 0.65 + 0.04 * (1.0 - ys)
    bg_b = 0.54 + 0.02 * (1.0 - ys)
    ref[:, :, 0] = bg_r
    ref[:, :, 1] = bg_g
    ref[:, :, 2] = bg_b

    # ── Window light gradient from upper-left ──────────────────────────────
    dist_ul = np.sqrt((ys * 0.8) ** 2 + (xs * 1.2) ** 2)
    window_strength = np.clip(1.0 - dist_ul * 0.9, 0.0, 1.0).astype(np.float32)
    ref[:, :, 0] += 0.08 * window_strength
    ref[:, :, 1] += 0.07 * window_strength
    ref[:, :, 2] += 0.04 * window_strength

    # ── Figure zone: warm ochre-flesh, centred ─────────────────────────────
    fig_cx, fig_cy = 0.42, 0.44
    fig_rx, fig_ry = 0.26, 0.38
    fig_mask = np.clip(
        1.0 - np.sqrt(((xs - fig_cx) / fig_rx) ** 2 + ((ys - fig_cy) / fig_ry) ** 2),
        0.0, 1.0
    ).astype(np.float32) ** 1.6

    fig_r = 0.75 * fig_mask
    fig_g = 0.63 * fig_mask
    fig_b = 0.50 * fig_mask
    ref[:, :, 0] = ref[:, :, 0] * (1.0 - fig_mask * 0.7) + fig_r
    ref[:, :, 1] = ref[:, :, 1] * (1.0 - fig_mask * 0.7) + fig_g
    ref[:, :, 2] = ref[:, :, 2] * (1.0 - fig_mask * 0.7) + fig_b

    # Head: slightly lighter and cooler
    head_cx, head_cy = 0.41, 0.20
    head_r = 0.18
    head_mask = np.clip(
        1.0 - np.sqrt(((xs - head_cx) / head_r) ** 2 + ((ys - head_cy) / (head_r * 1.1)) ** 2),
        0.0, 1.0
    ).astype(np.float32) ** 1.8
    ref[:, :, 0] = ref[:, :, 0] * (1.0 - head_mask * 0.5) + 0.78 * head_mask
    ref[:, :, 1] = ref[:, :, 1] * (1.0 - head_mask * 0.5) + 0.70 * head_mask
    ref[:, :, 2] = ref[:, :, 2] * (1.0 - head_mask * 0.5) + 0.62 * head_mask

    # ── Windowsill zone: right edge, cool blue-grey bottles ───────────────
    sill_x = np.clip((xs - 0.70) / 0.28, 0.0, 1.0).astype(np.float32)
    sill_vert = np.clip(
        np.minimum((ys - 0.12) / 0.10, (0.72 - ys) / 0.10), 0.0, 1.0
    ).astype(np.float32)
    sill_mask = sill_x * sill_vert
    ref[:, :, 0] = ref[:, :, 0] * (1.0 - sill_mask * 0.4) + 0.62 * sill_mask
    ref[:, :, 1] = ref[:, :, 1] * (1.0 - sill_mask * 0.4) + 0.64 * sill_mask
    ref[:, :, 2] = ref[:, :, 2] * (1.0 - sill_mask * 0.4) + 0.70 * sill_mask  # blue note

    # ── Foreground: warm ochre-brown floor/chair — kept lighter for Morandi ─
    fg_strength = np.clip((ys - 0.78) / 0.20, 0.0, 1.0).astype(np.float32)
    fg_r = 0.52 * fg_strength
    fg_g = 0.44 * fg_strength
    fg_b = 0.32 * fg_strength
    ref[:, :, 0] = ref[:, :, 0] * (1.0 - fg_strength * 0.40) + fg_r
    ref[:, :, 1] = ref[:, :, 1] * (1.0 - fg_strength * 0.40) + fg_g
    ref[:, :, 2] = ref[:, :, 2] * (1.0 - fg_strength * 0.40) + fg_b

    # Overall lift: Morandi's palette never goes below about 0.28
    ref = 0.28 + 0.72 * ref

    return np.clip(ref, 0.0, 1.0).astype(np.float32)


def main():
    print("=== Morandi Still-Life Interior (Session 188) ===")
    print(f"Canvas: {W}×{H}")

    ref = build_reference()
    print("Reference built.")

    p = Painter(W, H)

    # ── Ground: warm dusty ecru — Morandi's chalked ground ─────────────────
    print("  tone_ground ...")
    p.tone_ground((0.71, 0.67, 0.58), texture_strength=0.045)

    # ── Standard painting stages: light, sparse — Morandi's dry restraint ─
    print("  underpainting ...")
    p.underpainting(ref, stroke_size=60, n_strokes=80)

    print("  block_in ...")
    p.block_in(ref, stroke_size=42, n_strokes=120)

    # ── Morandi-specific passes (Session 188) ──────────────────────────────
    print("  morandi_tonal_unity_pass (96th mode) ...")
    p.morandi_tonal_unity_pass(
        ab_sigma=18.0,
        convergence_strength=0.65,
        luma_lo=0.05,
        luma_hi=0.95,
        opacity=0.70,
    )

    print("  palette_proximity_pull_pass (97th mode) ...")
    p.palette_proximity_pull_pass(
        pull_strength=0.28,
        luma_lo=0.04,
        luma_hi=0.96,
        opacity=0.42,
    )

    print("  build_form ...")
    p.build_form(ref, stroke_size=14, n_strokes=220)

    # ── Scumble: the chalky dry-brush Morandi surface ──────────────────────
    print("  scumble_pass ...")
    p.scumble_pass(
        opacity=0.18,
        n_drags=400,
        dry_factor=0.90,
        drag_distance=12,
    )

    # Second Morandi pass after build_form to re-unify colours
    print("  morandi_tonal_unity_pass (second pass) ...")
    p.morandi_tonal_unity_pass(
        ab_sigma=12.0,
        convergence_strength=0.45,
        luma_lo=0.06,
        luma_hi=0.94,
        opacity=0.40,
    )

    # ── Lights: very small, sparse, placed last ───────────────────────────
    print("  place_lights ...")
    p.place_lights(ref, stroke_size=5, n_strokes=200)

    # ── Final tonal glaze: faint warm ochre-grey unifier ──────────────────
    print("  glaze ...")
    p.glaze((0.70, 0.66, 0.56), opacity=0.038)

    # ── Finish ─────────────────────────────────────────────────────────────
    print("  finish ...")
    p.finish(vignette=0.28, crackle=False)

    p.save(OUTPUT)
    print(f"\nSaved → {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
