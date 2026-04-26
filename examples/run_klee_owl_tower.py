"""
run_klee_owl_tower.py — Session 190

Paints a Paul Klee-inspired scene: a Great Horned Owl perched atop a slender
Bauhaus watchtower at dusk, rendered in Klee's polyphonic cell-grid technique.
The warm ochre/cobalt palette, mosaic cell architecture, and amber ground bleed
evoke 'Fire in the Evening' (1929) and 'Ad Parnassum' (1932).

Session 190 pass used:
  klee_magic_square_pass  (101st distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "klee_owl_tower.png")
W, H = 780, 1060


def build_reference() -> np.ndarray:
    """
    Programmatic colour-field reference for the Klee owl-and-tower dusk scene.

    Zones (top -> bottom):
      - Deep cobalt-indigo sky, banding into warm saffron near horizon
      - Slender Bauhaus watchtower, centre, rising from lower third
      - Great Horned Owl perched on tower parapet, upper-centre
      - Low geometric rooftop mosaic, lower background
      - Stone parapet foreground band
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0, 1, H)[:, None]
    xs = np.linspace(0, 1, W)[None, :]
    rng = np.random.default_rng(190)

    # ── Sky: dusk gradient — cobalt top fading through rose to saffron horizon
    sky_t = np.clip(ys / 0.72, 0.0, 1.0)  # 0=top, 1=horizon band
    # Top cobalt-indigo
    sky_r = 0.14 + 0.38 * sky_t
    sky_g = 0.18 + 0.28 * sky_t
    sky_b = 0.52 - 0.18 * sky_t
    # Horizon saffron burst
    horiz_y = 0.68
    horiz_gate = np.exp(-((ys - horiz_y) ** 2) / (2 * 0.045 ** 2)).astype(np.float32)
    sky_r = np.clip(sky_r + 0.48 * horiz_gate, 0.0, 1.0)
    sky_g = np.clip(sky_g + 0.28 * horiz_gate, 0.0, 1.0)
    sky_b = np.clip(sky_b - 0.10 * horiz_gate, 0.0, 1.0)

    ref[:, :, 0] = sky_r
    ref[:, :, 1] = sky_g
    ref[:, :, 2] = sky_b

    # ── Geometric rooftop landscape: mosaic of low rectangular buildings
    ground_mask = np.clip((ys - 0.70) / 0.06, 0.0, 1.0).astype(np.float32)
    # Warm ochre base with colour block variation
    ground_noise = gaussian_filter(rng.uniform(0, 1, (H, W)).astype(np.float32), sigma=18)
    gr_r = 0.62 + 0.18 * ground_noise
    gr_g = 0.50 + 0.14 * ground_noise
    gr_b = 0.22 + 0.08 * ground_noise
    ref[:, :, 0] = ref[:, :, 0] * (1 - ground_mask) + np.clip(gr_r, 0, 1) * ground_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - ground_mask) + np.clip(gr_g, 0, 1) * ground_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - ground_mask) + np.clip(gr_b, 0, 1) * ground_mask

    # ── Watchtower: slender rectangular Bauhaus column, centre
    tower_cx = 0.50
    tower_w  = 0.055
    tower_top = 0.22
    tower_bot = 0.90
    tower_mask = np.zeros((H, W), dtype=np.float32)
    # Main shaft
    shaft_x = (np.abs(xs - tower_cx) < tower_w * 0.5).astype(np.float32)
    shaft_y = np.clip((ys - tower_top) / 0.02, 0.0, 1.0) * np.clip((tower_bot - ys) / 0.02, 0.0, 1.0)
    tower_mask = np.clip(shaft_x * shaft_y, 0.0, 1.0).astype(np.float32)
    # Wider parapet at top of tower
    parapet_y = tower_top + 0.04
    parapet_mask = (
        (np.abs(xs - tower_cx) < tower_w * 0.9) *
        np.clip((ys - (parapet_y - 0.03)) / 0.01, 0.0, 1.0) *
        np.clip((parapet_y - ys) / 0.005, 0.0, 1.0)
    ).astype(np.float32)
    tower_mask = np.maximum(tower_mask, parapet_mask)
    # Tower colour: warm terracotta with cobalt window accents
    tower_r = 0.72 + 0.10 * (1 - ys)
    tower_g = 0.52 + 0.08 * (1 - ys)
    tower_b = 0.28 + 0.04 * (1 - ys)
    # Small cobalt windows
    window_noise = gaussian_filter(rng.uniform(0, 1, (H, W)).astype(np.float32), sigma=1.5)
    window_gate = np.clip((window_noise - 0.85) * 10, 0.0, 1.0) * tower_mask * np.clip((ys - 0.30) / 0.05, 0.0, 1.0)
    tower_r = np.clip(tower_r - 0.40 * window_gate, 0.0, 1.0)
    tower_g = np.clip(tower_g - 0.20 * window_gate, 0.0, 1.0)
    tower_b = np.clip(tower_b + 0.30 * window_gate, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1 - tower_mask) + tower_r * tower_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - tower_mask) + tower_g * tower_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - tower_mask) + tower_b * tower_mask

    # ── Great Horned Owl: compact rounded body on parapet
    owl_cx, owl_cy = 0.50, 0.22
    # Body: rounded triangle form
    owl_body = np.clip(
        1.0 - np.sqrt(((xs - owl_cx) / 0.10) ** 2 + ((ys - owl_cy) / 0.11) ** 2),
        0.0, 1.0
    ).astype(np.float32) ** 1.4
    # Head: rounder circle above body
    head_cy = owl_cy - 0.085
    owl_head = np.clip(
        1.0 - np.sqrt(((xs - owl_cx) / 0.065) ** 2 + ((ys - head_cy) / 0.055) ** 2),
        0.0, 1.0
    ).astype(np.float32) ** 1.6
    # Ear tufts: two small pointed ellipses at top of head
    tuft_l = np.clip(
        1.0 - np.sqrt(((xs - (owl_cx - 0.028)) / 0.012) ** 2 + ((ys - (head_cy - 0.05)) / 0.028) ** 2),
        0.0, 1.0
    ).astype(np.float32) ** 1.8
    tuft_r = np.clip(
        1.0 - np.sqrt(((xs - (owl_cx + 0.028)) / 0.012) ** 2 + ((ys - (head_cy - 0.05)) / 0.028) ** 2),
        0.0, 1.0
    ).astype(np.float32) ** 1.8
    # Spread wings: two flat ellipses angling downward from body sides
    wing_l = np.clip(
        1.0 - np.sqrt(((xs - (owl_cx - 0.15)) / 0.12) ** 2 + ((ys - (owl_cy + 0.02)) / 0.048) ** 2),
        0.0, 1.0
    ).astype(np.float32) ** 1.3
    wing_r = np.clip(
        1.0 - np.sqrt(((xs - (owl_cx + 0.15)) / 0.12) ** 2 + ((ys - (owl_cy + 0.02)) / 0.048) ** 2),
        0.0, 1.0
    ).astype(np.float32) ** 1.3
    owl_mask = np.maximum(
        np.maximum(np.maximum(owl_body, owl_head), np.maximum(tuft_l, tuft_r)),
        np.maximum(wing_l, wing_r)
    )
    # Owl feather colours: warm amber-ochre bands with dark umber chevrons
    feather_noise = gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), sigma=3.5)
    owl_r = np.clip(0.72 + 0.16 * feather_noise, 0.0, 1.0)
    owl_g = np.clip(0.58 + 0.12 * feather_noise, 0.0, 1.0)
    owl_b = np.clip(0.24 + 0.06 * feather_noise, 0.0, 1.0)
    # Dark chevron stripes: umber bands across body
    stripe_noise = gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), sigma=1.2)
    stripe_gate = np.clip(np.abs(stripe_noise) - 1.5, 0.0, 1.0) * owl_mask
    owl_r = np.clip(owl_r - 0.45 * stripe_gate, 0.0, 1.0)
    owl_g = np.clip(owl_g - 0.40 * stripe_gate, 0.0, 1.0)
    owl_b = np.clip(owl_b - 0.18 * stripe_gate, 0.0, 1.0)
    # Facial disc: pale cream circle around the face
    disc_mask = np.clip(
        1.0 - np.sqrt(((xs - owl_cx) / 0.052) ** 2 + ((ys - head_cy) / 0.044) ** 2),
        0.0, 1.0
    ).astype(np.float32) ** 2.0
    owl_r = np.clip(owl_r + 0.16 * disc_mask * owl_mask, 0.0, 1.0)
    owl_g = np.clip(owl_g + 0.14 * disc_mask * owl_mask, 0.0, 1.0)
    owl_b = np.clip(owl_b + 0.10 * disc_mask * owl_mask, 0.0, 1.0)
    # Large golden eyes: two concentric circles, deep cobalt iris with gold ring
    for eye_dx in (-0.022, 0.022):
        eye_cx2 = owl_cx + eye_dx
        eye_cy2 = head_cy + 0.003
        eye_dist = np.sqrt(((xs - eye_cx2) / 0.018) ** 2 + ((ys - eye_cy2) / 0.016) ** 2)
        # Iris: cobalt blue
        iris_gate = np.clip(1.0 - eye_dist, 0.0, 1.0) ** 1.5
        owl_r = np.clip(owl_r - 0.30 * iris_gate * owl_mask, 0.0, 1.0)
        owl_g = np.clip(owl_g - 0.10 * iris_gate * owl_mask, 0.0, 1.0)
        owl_b = np.clip(owl_b + 0.35 * iris_gate * owl_mask, 0.0, 1.0)
        # Gold ring around iris
        ring_gate = np.clip(1.2 - eye_dist, 0.0, 1.0) ** 3 * np.clip(eye_dist - 0.6, 0.0, 1.0)
        owl_r = np.clip(owl_r + 0.55 * ring_gate * owl_mask, 0.0, 1.0)
        owl_g = np.clip(owl_g + 0.42 * ring_gate * owl_mask, 0.0, 1.0)
        owl_b = np.clip(owl_b - 0.10 * ring_gate * owl_mask, 0.0, 1.0)
        # Pupil: black centre
        pupil_gate = np.clip(0.4 - eye_dist, 0.0, 1.0) ** 2
        owl_r = np.clip(owl_r - 0.60 * pupil_gate * owl_mask, 0.0, 1.0)
        owl_g = np.clip(owl_g - 0.55 * pupil_gate * owl_mask, 0.0, 1.0)
        owl_b = np.clip(owl_b - 0.20 * pupil_gate * owl_mask, 0.0, 1.0)

    ref[:, :, 0] = ref[:, :, 0] * (1 - owl_mask * 0.95) + np.clip(owl_r, 0, 1) * owl_mask * 0.95
    ref[:, :, 1] = ref[:, :, 1] * (1 - owl_mask * 0.95) + np.clip(owl_g, 0, 1) * owl_mask * 0.95
    ref[:, :, 2] = ref[:, :, 2] * (1 - owl_mask * 0.95) + np.clip(owl_b, 0, 1) * owl_mask * 0.95

    # ── Foreground parapet: warm stone band at bottom
    fore_mask = np.clip((ys - 0.88) / 0.04, 0.0, 1.0).astype(np.float32)
    fore_r = np.clip(0.68 + 0.08 * (1 - xs), 0.0, 1.0)
    fore_g = np.clip(0.58 + 0.06 * (1 - xs), 0.0, 1.0)
    fore_b = np.clip(0.36 + 0.04 * (1 - xs), 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1 - fore_mask) + fore_r * fore_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - fore_mask) + fore_g * fore_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - fore_mask) + fore_b * fore_mask

    return np.clip(ref, 0.0, 1.0).astype(np.float32)


def main():
    print("=== Paul Klee: Owl on the Tower at Dusk (Session 190) ===")
    print(f"Canvas: {W}x{H}")

    ref = build_reference()
    print("Reference built.")

    p = Painter(W, H)

    # Ground: warm buff — Klee's burlap/muslin base
    print("  tone_ground ...")
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.025)

    # Seed canvas with reference colour field
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

    # Light underpainting — Klee's thin transparent wash base
    print("  underpainting ...")
    p.underpainting(ref, stroke_size=40, n_strokes=35)

    # Build form with small delicate marks — Klee's miniaturist touch
    print("  build_form ...")
    p.build_form(ref, stroke_size=7, n_strokes=140)

    # Klee magic square pass — the defining polyphonic cell-grid effect
    print("  klee_magic_square_pass (101st mode) ...")
    p.klee_magic_square_pass(
        cell_size=16,
        harmony_strength=0.07,
        freq_x=0.75,
        freq_y=0.55,
        border_opacity=0.14,
        warm_shift=0.045,
        opacity=0.42,
    )

    # Canvas grain — matte fresco-like surface quality
    print("  canvas_grain_pass ...")
    p.canvas_grain_pass(
        noise_scale=1.0,
        noise_strength=0.012,
        sharpness=0.08,
        luma_lo=0.08,
        luma_hi=0.94,
        opacity=0.18,
    )

    # Edge definition — Klee's 'line as independent event'
    print("  edge_definition_pass ...")
    p.edge_definition_pass(
        edge_sigma=0.8,
        strength=0.28,
        soft_threshold=0.04,
        luma_lo=0.04,
        luma_hi=0.96,
        opacity=0.22,
    )

    # Warm amber glaze — the final amber veil unifying all cells
    print("  glaze ...")
    p.glaze((0.78, 0.62, 0.30), opacity=0.028)

    # Finish — very light vignette, no crackle (Klee's surfaces are smooth)
    print("  finish ...")
    p.finish(vignette=0.20, crackle=False)

    p.save(OUTPUT)
    print(f"\nSaved -> {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
