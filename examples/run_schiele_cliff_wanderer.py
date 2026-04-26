"""
run_schiele_cliff_wanderer.py — Session 194

Paints an Egon Schiele-inspired 'Cliff Wanderer' scene: a solitary hooded
figure standing at the edge of a rocky cliff, seen from slightly below,
looking out across a stormy sea at dusk.  The figure's dark cloak billows
against a sky transitioning from burnt orange near the horizon to deep
violet-grey overhead.  The sea below is dark indigo with angular white
wave crests.  The rocky cliff edge shows angular geological facets.

The angular contour treatment, sparse flesh-toned washes, and diagonal
shadow hatching directly evoke Schiele's characteristic draftsmanship —
his raw, defiant line quality and the psychological isolation of figures
floating in undefined space.

Session 194 pass used:
  schiele_angular_contour_pass  (105th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "schiele_cliff_wanderer.png"
)
W, H = 720, 1000   # tall portrait — Schiele's preferred figural proportions


def build_reference() -> np.ndarray:
    """
    Synthetic reference for the Schiele cliff-wanderer scene.

    Zones:
      - Burnt orange to violet-grey sky gradient (upper two-thirds)
      - Dark indigo-black sea (lower quarter)
      - Angular rocky cliff edge (lower left and right)
      - Solitary hooded figure silhouette (centre, slightly above mid-height)
      - Billowing cloak extending left and downward from figure
    """
    rng = np.random.default_rng(194)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Sky: burnt orange at horizon, violet-grey overhead ────────────────────
    # Horizon sits at ~65% down the canvas (sea occupies bottom 35%)
    horizon_y = 0.65
    sky_mask = ys < horizon_y
    # t = 0 at top, 1 at horizon
    t_sky = np.clip(ys / horizon_y, 0.0, 1.0)
    sky_r = 0.18 + 0.62 * t_sky ** 1.6   # dark violet → burnt orange
    sky_g = 0.10 + 0.28 * t_sky ** 2.2
    sky_b = 0.22 + 0.12 * t_sky - 0.08 * t_sky ** 2

    # Add subtle cloud texture via noise
    noise_y = rng.standard_normal((H, 1)) * 0.03
    noise_x = rng.standard_normal((1, W)) * 0.03
    sky_r = np.clip(sky_r + noise_y + noise_x, 0.0, 1.0)
    sky_g = np.clip(sky_g + noise_y * 0.5, 0.0, 1.0)
    sky_b = np.clip(sky_b + noise_x * 0.5, 0.0, 1.0)

    ref[:, :, 0] = sky_r
    ref[:, :, 1] = sky_g
    ref[:, :, 2] = sky_b

    # ── Sea: dark indigo-black, lower 35% ─────────────────────────────────────
    sea_t = np.clip((ys - horizon_y) / (1.0 - horizon_y), 0.0, 1.0)
    sea_r = 0.04 + 0.06 * (1.0 - sea_t)
    sea_g = 0.06 + 0.08 * (1.0 - sea_t)
    sea_b = 0.18 + 0.16 * (1.0 - sea_t)
    sea_mask = ys >= horizon_y
    ref[:, :, 0] = np.where(sea_mask, sea_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(sea_mask, sea_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(sea_mask, sea_b, ref[:, :, 2])

    # Angular wave crests: bright near-white streaks in the sea zone
    n_waves = 12
    for wi in range(n_waves):
        wave_y = horizon_y + 0.04 + wi * (1.0 - horizon_y - 0.04) / n_waves
        wave_y += rng.uniform(-0.015, 0.015)
        wave_thickness = rng.uniform(0.003, 0.007)
        wave_crest = np.exp(-((ys - wave_y) ** 2) / (2 * wave_thickness ** 2))
        # Angular x-modulation for wave crests
        x_offset = rng.uniform(-0.1, 0.1)
        wave_x_mod = np.clip(
            0.5 + 0.5 * np.cos(8.0 * np.pi * (xs - x_offset)), 0.0, 1.0
        )
        crest_intensity = wave_crest * wave_x_mod * 0.55
        ref[:, :, 0] = np.clip(ref[:, :, 0] + crest_intensity * 0.80, 0.0, 1.0)
        ref[:, :, 1] = np.clip(ref[:, :, 1] + crest_intensity * 0.82, 0.0, 1.0)
        ref[:, :, 2] = np.clip(ref[:, :, 2] + crest_intensity * 0.88, 0.0, 1.0)

    # ── Rocky cliff: angular dark shapes at lower edges ──────────────────────
    cliff_height = 0.22   # cliff top at 22% from bottom (y = 0.78)
    # Left cliff
    left_cliff_x = 0.28
    left_cliff_slope = 1.8   # steep
    left_cliff = np.clip(
        1.0 - (xs - left_cliff_x) * left_cliff_slope - (ys - (1.0 - cliff_height)) * 2.0,
        0.0, 1.0
    )
    # Right cliff
    right_cliff_x = 0.72
    right_cliff = np.clip(
        1.0 + (xs - right_cliff_x) * left_cliff_slope - (ys - (1.0 - cliff_height)) * 2.0,
        0.0, 1.0
    )
    cliff_combined = np.clip(left_cliff + right_cliff, 0.0, 1.0)
    cliff_r = 0.15 + 0.06 * rng.random((H, W))
    cliff_g = 0.12 + 0.05 * rng.random((H, W))
    cliff_b = 0.08 + 0.04 * rng.random((H, W))
    ref[:, :, 0] = ref[:, :, 0] * (1 - cliff_combined) + cliff_r * cliff_combined
    ref[:, :, 1] = ref[:, :, 1] * (1 - cliff_combined) + cliff_g * cliff_combined
    ref[:, :, 2] = ref[:, :, 2] * (1 - cliff_combined) + cliff_b * cliff_combined

    # ── Figure silhouette: hooded cloaked form at centre ──────────────────────
    fig_cx = 0.50
    fig_cy = 0.52   # vertical centre of figure

    # Head and hood: ellipse
    head_rx, head_ry = 0.045, 0.055
    head_dist = np.sqrt(
        ((xs - fig_cx) / head_rx) ** 2 + ((ys - (fig_cy - 0.12)) / head_ry) ** 2
    )
    head_mask = np.clip(1.0 - head_dist, 0.0, 1.0) ** 1.5

    # Torso: tall narrow rectangle with slight taper
    torso_w = 0.09
    torso_top = fig_cy - 0.07
    torso_bot = fig_cy + 0.20
    torso_mask = np.where(
        (xs > fig_cx - torso_w / 2) & (xs < fig_cx + torso_w / 2)
        & (ys > torso_top) & (ys < torso_bot),
        1.0, 0.0,
    )

    # Billowing cloak: large irregular shape extending left and down
    cloak_cx = fig_cx - 0.06
    cloak_cy = fig_cy + 0.10
    cloak_rx, cloak_ry = 0.18, 0.20
    cloak_dist = np.sqrt(
        ((xs - cloak_cx) / cloak_rx) ** 2 + ((ys - cloak_cy) / cloak_ry) ** 2
    )
    cloak_mask = np.clip(1.0 - cloak_dist, 0.0, 1.0) ** 0.8

    # Combine figure parts
    figure_mask = np.clip(head_mask + torso_mask + cloak_mask, 0.0, 1.0)
    figure_mask = np.clip(figure_mask ** 0.5, 0.0, 1.0)

    # Figure is near-black with slight warm undertone (dark cloak)
    fig_r = 0.08 + 0.04 * figure_mask
    fig_g = 0.06 + 0.03 * figure_mask
    fig_b = 0.04 + 0.02 * figure_mask
    ref[:, :, 0] = ref[:, :, 0] * (1 - figure_mask) + fig_r * figure_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - figure_mask) + fig_g * figure_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - figure_mask) + fig_b * figure_mask

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint the Schiele cliff-wanderer and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H)

    # ── Ground: warm cream, slight texture — unprimed paper feel ───────────────
    p.tone_ground((0.87, 0.84, 0.79), texture_strength=0.06)

    # ── Foundational underpainting: lay in tonal structure ────────────────────
    p.underpainting(ref_pil, stroke_size=22, dry_amount=0.88)
    p.block_in(ref_pil, stroke_size=14, dry_amount=0.60)

    # ── Schiele signature pass: angular contours, flesh wash, shadow hatching ──
    p.schiele_angular_contour_pass(
        ref_pil,
        edge_threshold=0.13,
        contour_weight=3.0,
        flesh_wash_opacity=0.15,
        hatch_opacity=0.20,
        n_hatch_lines=55,
        hatch_shadow_thresh=0.38,
        contour_color=(0.05, 0.03, 0.02),
        flesh_color=(0.82, 0.60, 0.44),
        opacity=0.82,
    )

    # ── Second contour pass: lighter, catches finer details ───────────────────
    p.schiele_angular_contour_pass(
        ref_pil,
        edge_threshold=0.22,
        contour_weight=1.8,
        flesh_wash_opacity=0.08,
        hatch_opacity=0.10,
        n_hatch_lines=30,
        hatch_shadow_thresh=0.30,
        contour_color=(0.08, 0.04, 0.02),
        flesh_color=(0.88, 0.68, 0.52),
        opacity=0.55,
        seed=99,
    )

    # ── Canvas grain: paper texture evokes Schiele's raw paper surface ────────
    p.canvas_grain_pass(noise_scale=1.5, opacity=0.18)

    # ── Final glaze: cool blue-grey veil over sea and sky ─────────────────────
    p.glaze((0.24, 0.26, 0.38), opacity=0.10)

    # ── Finish: vignette draws eye to the solitary figure ─────────────────────
    p.finish()

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
