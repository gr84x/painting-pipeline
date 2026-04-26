"""
run_kandinsky_resonance_field.py — Session 197

"Cellist in the Storm" — after Wassily Kandinsky

Image Description
─────────────────
Subject & Composition
    A solitary cellist seated on a wooden chair, viewed from a three-quarter
    angle slightly above and to the left.  She is mid-performance: bow drawn
    across the strings in a long, sweeping arc, head tilted toward the
    instrument, entirely surrendered to the music.  The figure occupies the
    lower centre of the canvas; the surrounding storm fills the upper two-thirds.

The Figure
    A woman in her 40s in a deep navy concert dress, hair pulled back but
    escaping in the wind.  The cello is amber-red — warm spruce and maple
    glowing against the dark sky.  Her left hand presses the strings,
    right arm sweeping the bow with controlled force.
    Emotional state: fierce concentration — eyes closed, lips slightly parted,
    technically precise yet utterly surrendered.  The bow-arm arc echoes the
    curve of the instrument; the two together form a closed loop of energy.

The Environment
    A thunderstorm at twilight.  The sky is ultramarine-violet above, cadmium
    yellow at the horizon where lightning fractures the band of light.  The
    cellist sits exposed on an open hill — no shelter, no audience, only wind
    and rain and the note she is drawing from the strings.
    Behind her: three jagged near-black lightning bolts that mirror the tension
    lines of the Kandinsky geometric vocabulary.  The foreground grass bends in
    hard wind; flat wedge shapes, yellow-green to emerald.  Rain falls in
    near-vertical near-black strokes from upper-left to lower-right.  The
    horizon is a hard geometric edge: flat ultramarine above, chrome yellow
    band below — the landscape itself obeys Kandinsky's colour theory.

Technique & Palette
    Kandinsky Geometric Resonance pass (kandinsky_geometric_resonance_pass,
    108th distinct mode).  Blue concentric circles float in the storm clouds
    (celestial depth, cello tone).  Yellow triangles advance from the grass
    (the music pushing upward, trumpet-call of sunlight).  Near-black tension
    lines from the lightning (structural force, dramatic counterpoint).
    Vermilion squares anchor the midground hills (earthbound drumbeat warmth).
    Violet arcs scatter through the rain (wavering uncertainty, dissolution
    into sensation).
    Palette: ultramarine blue, cadmium yellow, vermilion red, near-black,
    ivory white, emerald green, violet.

Mood & Intent
    Music and storm are the same force — pure energy translated into form.
    Kandinsky believed painting and music are identical in spiritual effect.
    This image argues that a cellist in a thunderstorm is not reckless but
    canonical: both forces obey the same laws of resonance, tension, and
    release.  The geometric overlay is not decorative — it reveals the hidden
    musical structure underneath weather.  The viewer carries away the
    paradox of stillness within chaos: the cellist is perfectly still at the
    eye of everything, the one fixed point around which the storm turns.

Session 197 pass used:
    kandinsky_geometric_resonance_pass  (108th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "kandinsky_cellist_storm.png"
)
W, H = 800, 1000   # portrait — cellist tall in frame, storm above


def build_reference() -> np.ndarray:
    """
    Synthetic tonal reference encoding the cellist-in-storm scene.

    Tonal zones:
      - Upper sky: ultramarine-violet gradient, deep blue-violet
      - Horizon band: bright cadmium yellow / chrome strip (lightning zone)
      - Lower sky / storm mid-level: darker ultramarine turbulence
      - Rain streaks: near-vertical dark lines across mid and upper canvas
      - Lightning: three jagged bright near-white bolts in sky
      - Grass foreground: wedge-shaped emerald-to-yellow-green bands
      - Cellist figure: mid-tone navy mass at lower centre
      - Cello instrument: warm amber-red body within figure
      - Chair: mid-grey rectangular mass beneath figure
      - Bow arm: diagonal bright stroke extending from figure
    """
    rng = np.random.default_rng(197)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Sky: ultramarine-violet gradient (top) to yellow (horizon) ──────────
    sky_top = np.array([0.08, 0.12, 0.52])   # deep ultramarine blue
    sky_mid = np.array([0.14, 0.08, 0.38])   # storm violet at mid-sky
    sky_hor = np.array([0.85, 0.72, 0.06])   # chrome yellow at horizon

    sky_frac = np.clip(ys / 0.62, 0.0, 1.0)   # 0 = top sky, 1 = horizon
    # top-to-mid blend
    t_mid = np.clip(sky_frac * 2.0, 0.0, 1.0)
    ref[:, :, 0] = sky_top[0] * (1 - t_mid) + sky_mid[0] * t_mid
    ref[:, :, 1] = sky_top[1] * (1 - t_mid) + sky_mid[1] * t_mid
    ref[:, :, 2] = sky_top[2] * (1 - t_mid) + sky_mid[2] * t_mid
    # mid-to-horizon blend
    t_hor = np.clip((sky_frac - 0.50) * 3.0, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1 - t_hor) + sky_hor[0] * t_hor
    ref[:, :, 1] = ref[:, :, 1] * (1 - t_hor) + sky_hor[1] * t_hor
    ref[:, :, 2] = ref[:, :, 2] * (1 - t_hor) + sky_hor[2] * t_hor

    # ── Horizon bright band (lightning zone: y ≈ 0.60–0.66) ─────────────────
    hor_dist = np.abs(ys - 0.63) / 0.035
    hor_glow = np.clip(1.0 - hor_dist, 0.0, 1.0) ** 1.2
    ref[:, :, 0] = ref[:, :, 0] + hor_glow * (0.92 - ref[:, :, 0]) * 0.80
    ref[:, :, 1] = ref[:, :, 1] + hor_glow * (0.84 - ref[:, :, 1]) * 0.80
    ref[:, :, 2] = ref[:, :, 2] + hor_glow * (0.04 - ref[:, :, 2]) * 0.80

    # ── Foreground grass (y > 0.66): emerald / yellow-green wedges ──────────
    grass_frac = np.clip((ys - 0.66) / 0.34, 0.0, 1.0)
    grass_r = 0.12 + 0.20 * grass_frac
    grass_g = 0.42 + 0.28 * (1.0 - grass_frac)
    grass_b = 0.08 + 0.06 * grass_frac
    ref[:, :, 0] = ref[:, :, 0] * (1 - grass_frac) + grass_r * grass_frac
    ref[:, :, 1] = ref[:, :, 1] * (1 - grass_frac) + grass_g * grass_frac
    ref[:, :, 2] = ref[:, :, 2] * (1 - grass_frac) + grass_b * grass_frac

    # Wind distortion in grass: lateral sine bends
    wind_amp = 0.015
    for band in range(8):
        band_y = 0.68 + band * 0.040
        band_h = 0.018
        band_t = np.clip(1.0 - np.abs(ys - band_y) / band_h, 0.0, 1.0) ** 0.8
        shift = wind_amp * np.sin(xs * 18.0 + band * 1.2)
        bright = 0.10 + 0.12 * (band % 2)
        ref[:, :, 1] = ref[:, :, 1] + band_t * (grass_g + bright - ref[:, :, 1]) * 0.35

    # ── Rain streaks: near-vertical dark lines ────────────────────────────────
    n_rain = 55
    for ri in range(n_rain):
        rx_start = rng.random()
        ry_start = rng.random() * 0.55     # rain falls in sky/horizon zone
        length = 0.08 + rng.random() * 0.18
        rx_end = rx_start + length * 0.12   # slight diagonal
        ry_end = ry_start + length
        if ry_end > 0.88:
            ry_end = 0.88
        # Linear mask along rain streak
        rain_dist = np.abs(xs - (rx_start + (rx_end - rx_start) * ys / max(ry_end - ry_start, 0.01))) / 0.005
        rain_y_mask = np.where((ys >= ry_start) & (ys <= ry_end), 1.0, 0.0)
        rain_mask = np.clip(1.0 - rain_dist, 0.0, 1.0) * rain_y_mask * 0.35
        ref[:, :, 0] = ref[:, :, 0] * (1 - rain_mask) + 0.06 * rain_mask
        ref[:, :, 1] = ref[:, :, 1] * (1 - rain_mask) + 0.06 * rain_mask
        ref[:, :, 2] = ref[:, :, 2] * (1 - rain_mask) + 0.10 * rain_mask

    # ── Lightning bolts: three jagged bright near-white/yellow forks ─────────
    lightning_specs = [
        # (x_top, y_top, x_bottom, y_bottom, jitter_scale, width)
        (0.24, 0.05, 0.19, 0.60, 0.025, 0.004),
        (0.61, 0.02, 0.65, 0.58, 0.018, 0.003),
        (0.82, 0.10, 0.78, 0.62, 0.020, 0.003),
    ]
    for (lx0, ly0, lx1, ly1, ljit, lw) in lightning_specs:
        n_seg = 12
        pts_x = np.linspace(lx0, lx1, n_seg)
        pts_y = np.linspace(ly0, ly1, n_seg)
        pts_x[1:-1] += rng.normal(0, ljit, n_seg - 2)
        for si in range(n_seg - 1):
            seg_dx = pts_x[si + 1] - pts_x[si]
            seg_dy = pts_y[si + 1] - pts_y[si]
            seg_len = max(np.sqrt(seg_dx ** 2 + seg_dy ** 2), 1e-6)
            t_seg = np.clip(
                (xs - pts_x[si]) / (seg_dx + 1e-9) +
                (ys - pts_y[si]) / (seg_dy + 1e-9),
                0.0, 1.0,
            )
            # Distance to segment
            cx = pts_x[si] + t_seg * seg_dx
            cy = pts_y[si] + t_seg * seg_dy
            bolt_dist = np.sqrt(((xs - cx) ** 2 + (ys - cy) ** 2)) / lw
            bolt_mask = np.clip(1.0 - bolt_dist, 0.0, 1.0) ** 1.5
            bolt_mask *= np.where((ys >= pts_y[si]) & (ys <= pts_y[si + 1]), 1.0, 0.0)
            ref[:, :, 0] = ref[:, :, 0] + bolt_mask * (0.96 - ref[:, :, 0]) * 0.88
            ref[:, :, 1] = ref[:, :, 1] + bolt_mask * (0.96 - ref[:, :, 1]) * 0.88
            ref[:, :, 2] = ref[:, :, 2] + bolt_mask * (0.80 - ref[:, :, 2]) * 0.88

    # ── Chair: mid-grey rectangle at lower centre ─────────────────────────────
    chair_cx = 0.50
    chair_cy_top = 0.82
    chair_cy_bot = 0.94
    chair_hw = 0.075
    chair_x_mask = np.clip(1.0 - np.abs(xs - chair_cx) / chair_hw, 0.0, 1.0)
    chair_y_mask = np.where((ys >= chair_cy_top) & (ys <= chair_cy_bot), 1.0, 0.0)
    chair_mask = (chair_x_mask ** 0.6) * chair_y_mask
    ref[:, :, 0] = ref[:, :, 0] * (1 - chair_mask) + 0.30 * chair_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - chair_mask) + 0.28 * chair_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - chair_mask) + 0.26 * chair_mask

    # ── Cellist figure: deep navy mass ────────────────────────────────────────
    fig_cx = 0.50
    fig_cy = 0.76
    fig_hw = 0.10
    fig_hh = 0.20
    fig_dist = np.sqrt(((xs - fig_cx) / fig_hw) ** 2 + ((ys - fig_cy) / fig_hh) ** 2)
    fig_mask = np.clip(1.0 - fig_dist ** 0.7, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1 - fig_mask) + 0.10 * fig_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - fig_mask) + 0.12 * fig_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - fig_mask) + 0.30 * fig_mask

    # Head: small sphere above body
    head_cy = fig_cy - 0.18
    head_r = 0.045
    head_dist = np.sqrt(((xs - fig_cx) / head_r) ** 2 + ((ys - head_cy) / head_r) ** 2)
    head_mask = np.clip(1.0 - head_dist, 0.0, 1.0) ** 0.8
    ref[:, :, 0] = ref[:, :, 0] * (1 - head_mask) + 0.68 * head_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - head_mask) + 0.52 * head_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - head_mask) + 0.38 * head_mask

    # ── Cello: warm amber-red body within figure ──────────────────────────────
    cello_cx = 0.47
    cello_cy = 0.73
    cello_hw = 0.045
    cello_hh = 0.115
    cello_dist = np.sqrt(((xs - cello_cx) / cello_hw) ** 2 + ((ys - cello_cy) / cello_hh) ** 2)
    cello_mask = np.clip(1.0 - cello_dist ** 0.75, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1 - cello_mask) + 0.72 * cello_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - cello_mask) + 0.32 * cello_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - cello_mask) + 0.08 * cello_mask

    # Cello scroll (scroll neck, top)
    neck_cx = cello_cx + 0.008
    neck_top = cello_cy - cello_hh - 0.06
    neck_dist = np.sqrt(((xs - neck_cx) / 0.010) ** 2 + ((ys - (neck_top + 0.03)) / 0.04) ** 2)
    neck_mask = np.clip(1.0 - neck_dist, 0.0, 1.0) ** 1.0
    ref[:, :, 0] = ref[:, :, 0] * (1 - neck_mask) + 0.60 * neck_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - neck_mask) + 0.28 * neck_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - neck_mask) + 0.06 * neck_mask

    # ── Bow arm: diagonal bright stroke, lower-right to upper-centre ─────────
    bow_x0 = 0.58
    bow_y0 = 0.80
    bow_x1 = 0.38
    bow_y1 = 0.62
    n_bow = 30
    for bi in range(n_bow):
        t = bi / float(n_bow)
        bx = bow_x0 + (bow_x1 - bow_x0) * t
        by = bow_y0 + (bow_y1 - bow_y0) * t
        bow_dist = np.sqrt(((xs - bx) / 0.008) ** 2 + ((ys - by) / 0.006) ** 2)
        bow_mask = np.clip(1.0 - bow_dist, 0.0, 1.0) ** 1.3
        ref[:, :, 0] = ref[:, :, 0] * (1 - bow_mask) + 0.65 * bow_mask
        ref[:, :, 1] = ref[:, :, 1] * (1 - bow_mask) + 0.58 * bow_mask
        ref[:, :, 2] = ref[:, :, 2] * (1 - bow_mask) + 0.40 * bow_mask

    # ── Dark cloud masses in upper sky ────────────────────────────────────────
    cloud_specs = [
        (0.18, 0.12, 0.20, 0.07),
        (0.70, 0.08, 0.18, 0.06),
        (0.42, 0.22, 0.22, 0.08),
        (0.85, 0.25, 0.14, 0.06),
    ]
    for (cx, cy, cw, ch) in cloud_specs:
        cdist = np.sqrt(((xs - cx) / cw) ** 2 + ((ys - cy) / ch) ** 2)
        cmask = np.clip(1.0 - cdist ** 0.65, 0.0, 1.0) * 0.55
        ref[:, :, 0] = ref[:, :, 0] * (1 - cmask) + 0.06 * cmask
        ref[:, :, 1] = ref[:, :, 1] * (1 - cmask) + 0.06 * cmask
        ref[:, :, 2] = ref[:, :, 2] * (1 - cmask) + 0.18 * cmask

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'Cellist in the Storm' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=197)

    # ── Ground: off-white — Kandinsky wanted colour to radiate cleanly ───────
    p.tone_ground((0.92, 0.91, 0.87), texture_strength=0.02)

    # ── Underpainting: tonal structure from the storm scene ──────────────────
    p.underpainting(ref_pil, stroke_size=48)

    # ── Block in: broad colour masses ────────────────────────────────────────
    p.block_in(ref_pil, stroke_size=30)

    # ── Build form: directional strokes follow contours ──────────────────────
    p.build_form(ref_pil, stroke_size=14)

    # ── Kandinsky Geometric Resonance — THE signature effect ─────────────────
    # Primary pass: full geometric scatter with strong synesthetic palette
    p.kandinsky_geometric_resonance_pass(
        ref_pil,
        n_circles=22,
        n_triangles=18,
        n_tension_lines=28,
        n_squares=14,
        n_arcs=9,
        primitive_scale=1.10,
        synesthetic_strength=0.80,
        opacity=0.72,
        seed=197,
    )

    # ── Second resonance pass: smaller primitives, lower opacity, deeper structure
    p.kandinsky_geometric_resonance_pass(
        ref_pil,
        n_circles=12,
        n_triangles=10,
        n_tension_lines=16,
        n_squares=8,
        n_arcs=5,
        primitive_scale=0.65,
        synesthetic_strength=0.55,
        opacity=0.38,
        seed=1970,
    )

    # ── Vignette: draw focus inward to the cellist ───────────────────────────
    p.vignette_pass(strength=0.35)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
