"""
run_kline_urban_testament.py — Session 208

Paints a Franz Kline-inspired abstraction: 'Urban Testament' — the steel
skeleton of a New York elevated railway bridge reduced to monumental black
calligraphic gestures on raw white ground.

The composition references Kline's landmark 'Chief' (1950) and 'Mahoning'
(1956): a dominant horizontal girder beam sweeps the full canvas width at
mid-height, crossed by two diagonal tension cables, all rendered as massive
house-painter's-brush slashes.  The raw white canvas breathes between the
marks, as active as the black.

Session 208 pass used:
  kline_gestural_slash_pass  (119th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "kline_urban_testament.png"
)
W, H = 900, 720   # landscape — Kline's preferred horizontal sweep proportions


def build_reference() -> np.ndarray:
    """
    Synthetic structural reference for the Kline bridge-girder abstraction.

    Zones:
      - Near-white ground filling the entire canvas
      - One dominant horizontal girder: thick dark band at ~45% canvas height
      - Two diagonal tension struts: upper-left to lower-right, and upper-right
        to lower-left
      - Four vertical rivet columns at canvas quarter-points
    """
    rng = np.random.default_rng(208)
    ref = np.ones((H, W, 3), dtype=np.float32) * 0.92  # raw white ground

    xs = np.linspace(0.0, 1.0, W)[np.newaxis, :]
    ys = np.linspace(0.0, 1.0, H)[:, np.newaxis]

    def add_dark_band(mask, strength=1.0):
        """Blend a structural dark element into the reference."""
        dark = np.array([0.05, 0.04, 0.04], dtype=np.float32)
        for c in range(3):
            ref[:, :, c] = ref[:, :, c] * (1.0 - mask * strength) + dark[c] * mask * strength

    # ── Main horizontal girder: thick, slightly angled ────────────────────────
    girder_y      = 0.44     # centre of girder
    girder_height = 0.075    # half-thickness
    # Slight angle: left side slightly higher
    girder_centre = girder_y + (xs - 0.5) * 0.04
    girder_dist   = np.abs(ys - girder_centre) / girder_height
    girder_mask   = np.clip(1.0 - girder_dist, 0.0, 1.0) ** 0.5
    # Random noise to simulate rough brushwork
    girder_noise  = rng.uniform(0.85, 1.0, (H, W)).astype(np.float32)
    add_dark_band(girder_mask * girder_noise, strength=0.95)

    # ── Diagonal tension strut: upper-left to lower-right ────────────────────
    diag1_slope    = 1.30   # rise/run
    diag1_origin_y = 0.12  # top-left intercept
    diag1_centre   = diag1_origin_y + xs * diag1_slope
    diag1_width    = 0.035
    diag1_dist     = np.abs(ys - diag1_centre) / diag1_width
    diag1_mask     = np.clip(1.0 - diag1_dist, 0.0, 1.0) ** 0.6
    diag1_noise    = rng.uniform(0.80, 1.0, (H, W)).astype(np.float32)
    add_dark_band(diag1_mask * diag1_noise, strength=0.90)

    # ── Diagonal counter-strut: upper-right to lower-left ────────────────────
    diag2_slope    = -1.10
    diag2_origin_y = 0.14 + 1.0 * (-diag2_slope)   # so it starts at right edge
    diag2_centre   = diag2_origin_y + xs * diag2_slope
    diag2_width    = 0.030
    diag2_dist     = np.abs(ys - diag2_centre) / diag2_width
    diag2_mask     = np.clip(1.0 - diag2_dist, 0.0, 1.0) ** 0.7
    diag2_noise    = rng.uniform(0.80, 1.0, (H, W)).astype(np.float32)
    add_dark_band(diag2_mask * diag2_noise, strength=0.88)

    # ── Vertical rivet columns at quarter-points ──────────────────────────────
    for qx in [0.25, 0.50, 0.75]:
        col_width  = 0.016
        col_dist   = np.abs(xs - qx) / col_width
        col_mask   = np.clip(1.0 - col_dist, 0.0, 1.0) ** 0.8
        col_noise  = rng.uniform(0.75, 1.0, (H, W)).astype(np.float32)
        add_dark_band(col_mask * col_noise, strength=0.85)

    # ── Soft ground texture: linen weave feel ────────────────────────────────
    linen = rng.uniform(-0.025, 0.025, (H, W)).astype(np.float32)
    for c in range(3):
        ref[:, :, c] = np.clip(ref[:, :, c] + linen, 0.0, 1.0)

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint the Kline urban-testament and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H)

    # ── Ground: raw white cream — Kline often painted on raw canvas ───────────
    p.tone_ground((0.92, 0.91, 0.88), texture_strength=0.08)

    # ── Structural underpainting: lay in tonal mass of the bridge forms ───────
    p.underpainting(ref_pil, stroke_size=40, dry_amount=0.85)

    # ── Block-in: broad dark zones establish the primary masses ──────────────
    p.block_in(ref_pil, stroke_size=28, dry_amount=0.55)

    # ── Kline signature pass: gestural calligraphic sweeps ───────────────────
    p.kline_gestural_slash_pass(
        n_strokes=20,
        width_scale=0.07,
        bleed_sigma=4.5,
        opacity=0.94,
        stroke_color=(0.04, 0.04, 0.05),
        angle_noise=0.20,
        seed=208,
    )

    # ── Second pass: tighter, finer gestural corrections ─────────────────────
    p.kline_gestural_slash_pass(
        n_strokes=10,
        width_scale=0.03,
        bleed_sigma=2.0,
        opacity=0.70,
        stroke_color=(0.06, 0.05, 0.05),
        angle_noise=0.12,
        seed=42,
    )

    # ── Canvas grain: evokes the woven texture of raw stretched canvas ────────
    p.canvas_grain_pass(noise_scale=1.2, opacity=0.12)

    # ── Minimal glaze: near-white veil to knock back any muddy marks ──────────
    p.glaze((0.94, 0.93, 0.90), opacity=0.08)

    # ── Finish ────────────────────────────────────────────────────────────────
    p.finish()

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
