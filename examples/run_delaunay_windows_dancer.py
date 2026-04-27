"""
run_delaunay_windows_dancer.py — Session 207

"The Dancer at the Threshold of Colour" — after Robert Delaunay

Image Description
─────────────────
Subject & Composition
    A single female dancer, seen from below and slightly left, mid-leap at the
    centre of a Paris rooftop terrace at dusk.  She is caught at the apex of
    her jump — both feet off the ground, arms spread wide, her body arched back
    in a full arabesque.  The Eiffel Tower is partially visible as a dark
    geometric silhouette at the upper right, its iron lattice fragmenting into
    the colour field.  The canvas divides into four overlapping chromatic disk
    zones that correspond roughly to: sky (upper 45%), rooftop plane (lower
    35%), tower fragment (right 25%), and the dancer's kinetic aura (centre
    30%).  The disk fields do not respect these boundaries — they overlap and
    interfere, as Delaunay intended.

The Figure
    The dancer is young, twenties, dressed in a white costume that has become
    a light-gathering prism — where cobalt disk fields cross it, it is blue;
    where orange fields cross, it is warm amber; where fields overlap, it
    fragments into vivid secondary zones.  She is approximately 60% of the
    canvas height.  Her emotional state: pure exhilaration — not performed joy
    but the physiological reality of a body at the outer edge of what it can do.
    Her arms are not graceful; they are geometric struts, structural members of
    a compositional arc that completes the upper disk boundary.  Her face is
    turned upward and slightly left, absorbed in the act of motion.

The Environment
    The sky is not sky — it is a field of six overlapping Orphist disks: cobalt
    blue / vermilion orange, cadmium yellow / magenta-violet, emerald green /
    orange.  The disk centres are distributed by golden-angle spiral, placing
    one disk near the dancer's head (upper centre), one at the Eiffel Tower
    apex (upper right), one near the rooftop horizon (lower centre-left), and
    the remaining three at intermediate positions.  Where disks overlap, the
    simultaneous contrast is at its most intense: at the blue-orange boundary,
    the orange appears incandescent; the blue reads as pure void.  The rooftop
    beneath the dancer is a dark near-black ground — the original deep blue-black
    of Delaunay's primed canvas — punctuated by chimney pots whose cylindrical
    forms echo the disk geometry.  Horizon: no horizon.  Distance: colour.

Technique & Palette
    Robert Delaunay's Orphist / Simultaneist technique.  The primary effect is
    delaunay_orphist_disk_pass (118th distinct mode): seven disk centres
    distributed by golden-angle spiral, each assigned a complementary pair
    (cobalt-blue/vermilion-orange, cadmium-yellow/magenta-violet,
    emerald-green/orange).  Proximity-weighted ring-band fields from all seven
    disks are summed and normalised, producing simultaneous contrast at every
    disk boundary.  The ring_frequency is set to 5.0 — five concentric band
    cycles per unit distance — which creates visible, clearly-banded colour
    arcs rather than fine interference fringes.

    Palette: cobalt blue (0.05, 0.22, 0.78) — primary chromatic void; vermilion
    orange (0.92, 0.32, 0.05) — thermal complement; cadmium yellow (0.95, 0.84,
    0.06) — solar arc; emerald green (0.08, 0.62, 0.28) — cool secondary;
    magenta-violet (0.78, 0.10, 0.58) — dusk complement; near-white (0.95,
    0.95, 0.95) — optical peak at disk intersections; deep navy (0.10, 0.10,
    0.18) — grounding dark.

Mood & Intent
    Delaunay believed colour in motion was the modern equivalent of what music
    had always been: pure sensation without description.  This image attempts
    that equation.  The dancer is a pretext — a shape that gives the colour
    fields a human scale and a directional energy.  What the image is about is
    the moment when two complementary colours occupy adjacent zones and the eye
    cannot rest: the orange is more orange because the blue is beside it; the
    blue is more blue because the orange is beside it.  The viewer should come
    away feeling the visual vibration of simultaneous contrast as a physical
    sensation — a kind of optical heat.  Not joy.  Not beauty.  Chromatic energy.

Session 207 pass used:
    delaunay_orphist_disk_pass  (118th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "delaunay_windows_dancer.png"
)
W, H = 960, 1120


def build_reference() -> np.ndarray:
    """
    Synthetic reference for 'The Dancer at the Threshold of Colour'.

    Tonal zones:
      - Sky / upper disk field (upper 55%): deep blue-black to fragment
      - Rooftop plane (lower 45%): deep near-black with warm ground
      - Dancer figure (centre, ~60% canvas height): pale costume silhouette
      - Eiffel Tower fragment (upper right): dark geometric lattice
    """
    rng = np.random.default_rng(207)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    sky_frac = 0.55

    # ── Background: deep blue-black ground (Delaunay's dark canvas) ──────────
    bg_top    = np.array([0.06, 0.06, 0.15])
    bg_bottom = np.array([0.10, 0.08, 0.12])
    for ch in range(3):
        ref[:, :, ch] = bg_top[ch] * (1 - ys) + bg_bottom[ch] * ys

    # ── Faint chromatic disk pre-colouring (seed for the pass) ───────────────
    # Upper-left disk hint: cobalt blue
    d1_cx, d1_cy = 0.28, 0.20
    d1_r = np.sqrt((xs - d1_cx) ** 2 + (ys - d1_cy) ** 2)
    d1_mask = np.clip(1.0 - d1_r / 0.40, 0.0, 1.0) ** 1.4
    d1_col = np.array([0.06, 0.10, 0.38])
    for ch in range(3):
        ref[:, :, ch] += d1_col[ch] * d1_mask * 0.45

    # Upper-right disk hint: warm orange-amber (near tower)
    d2_cx, d2_cy = 0.76, 0.18
    d2_r = np.sqrt((xs - d2_cx) ** 2 + (ys - d2_cy) ** 2)
    d2_mask = np.clip(1.0 - d2_r / 0.38, 0.0, 1.0) ** 1.4
    d2_col = np.array([0.35, 0.18, 0.04])
    for ch in range(3):
        ref[:, :, ch] += d2_col[ch] * d2_mask * 0.40

    # Lower disk hint: emerald green
    d3_cx, d3_cy = 0.38, 0.72
    d3_r = np.sqrt((xs - d3_cx) ** 2 + (ys - d3_cy) ** 2)
    d3_mask = np.clip(1.0 - d3_r / 0.42, 0.0, 1.0) ** 1.4
    d3_col = np.array([0.04, 0.28, 0.12])
    for ch in range(3):
        ref[:, :, ch] += d3_col[ch] * d3_mask * 0.35

    # ── Eiffel Tower lattice (upper right): dark geometric struts ─────────────
    # Simplified: triangular converging form
    tower_cx = 0.82
    tower_top_y = 0.04
    tower_base_y = 0.50
    tower_half_w_at_base = 0.12
    # Linear taper: at row y, half-width = tower_half_w_at_base * (y - tower_top_y)
    for row_idx in range(H):
        y_norm = row_idx / float(H)
        if y_norm < tower_top_y or y_norm > tower_base_y:
            continue
        t_taper = (y_norm - tower_top_y) / (tower_base_y - tower_top_y)
        hw = tower_half_w_at_base * t_taper
        x_lo = tower_cx - hw
        x_hi = tower_cx + hw
        j_lo = max(0, int(x_lo * W))
        j_hi = min(W, int(x_hi * W))
        if j_hi > j_lo:
            for ch in range(3):
                ref[row_idx, j_lo:j_hi, ch] = np.clip(
                    ref[row_idx, j_lo:j_hi, ch] * 0.30, 0.0, 1.0
                )

    # Lattice noise — darkening streaks
    lattice_noise = rng.random((H, W)).astype(np.float32)
    lattice_blur  = gaussian_filter(lattice_noise, sigma=(1.5, 0.5))
    lattice_dark  = np.clip((lattice_blur - 0.62) * 4.0, 0.0, 0.18)
    tower_zone = np.clip(
        (1.0 - np.abs(xs - tower_cx) / 0.16) * np.clip((ys - tower_top_y) / 0.02, 0, 1) *
        np.clip(1.0 - (ys - tower_base_y) / 0.04, 0, 1),
        0.0, 1.0
    )
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] - lattice_dark * tower_zone * 0.5, 0.0, 1.0)

    # ── Dancer figure: pale costume silhouette (centre, leaping pose) ─────────
    # Torso
    torso_cx, torso_cy = 0.46, 0.52
    torso_w, torso_h = 0.055, 0.14
    torso_dist = np.sqrt(
        ((xs - torso_cx) / torso_w) ** 2 + ((ys - torso_cy) / torso_h) ** 2
    )
    torso_mask = np.clip(1.0 - torso_dist ** 2.0, 0.0, 1.0)

    # Head (tilted up and left)
    head_cx, head_cy = 0.43, 0.36
    head_w, head_h = 0.038, 0.052
    head_dist = np.sqrt(
        ((xs - head_cx) / head_w) ** 2 + ((ys - head_cy) / head_h) ** 2
    )
    head_mask = np.clip(1.0 - head_dist ** 2.0, 0.0, 1.0)

    # Arms spread wide (two ellipses)
    arm_l_cx, arm_l_cy = 0.28, 0.47
    arm_l_w, arm_l_h = 0.10, 0.025
    arm_l_dist = np.sqrt(
        ((xs - arm_l_cx) / arm_l_w) ** 2 + ((ys - arm_l_cy) / arm_l_h) ** 2
    )
    arm_l_mask = np.clip(1.0 - arm_l_dist ** 2.0, 0.0, 1.0)

    arm_r_cx, arm_r_cy = 0.64, 0.44
    arm_r_w, arm_r_h = 0.10, 0.025
    arm_r_dist = np.sqrt(
        ((xs - arm_r_cx) / arm_r_w) ** 2 + ((ys - arm_r_cy) / arm_r_h) ** 2
    )
    arm_r_mask = np.clip(1.0 - arm_r_dist ** 2.0, 0.0, 1.0)

    # Legs (arabesque — one leg extended back, one tucked)
    leg_ext_cx, leg_ext_cy = 0.50, 0.72
    leg_ext_w, leg_ext_h = 0.025, 0.12
    leg_ext_dist = np.sqrt(
        ((xs - leg_ext_cx) / leg_ext_w) ** 2 + ((ys - leg_ext_cy) / leg_ext_h) ** 2
    )
    leg_ext_mask = np.clip(1.0 - leg_ext_dist ** 2.2, 0.0, 1.0)

    leg_tuck_cx, leg_tuck_cy = 0.40, 0.68
    leg_tuck_w, leg_tuck_h = 0.035, 0.08
    leg_tuck_dist = np.sqrt(
        ((xs - leg_tuck_cx) / leg_tuck_w) ** 2 + ((ys - leg_tuck_cy) / leg_tuck_h) ** 2
    )
    leg_tuck_mask = np.clip(1.0 - leg_tuck_dist ** 2.2, 0.0, 1.0)

    # Composite figure mask
    fig_mask = np.clip(
        torso_mask + head_mask + arm_l_mask + arm_r_mask +
        leg_ext_mask + leg_tuck_mask,
        0.0, 1.0
    )

    costume_col = np.array([0.82, 0.82, 0.82])   # pale near-white costume
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - fig_mask * 0.78) + \
                        costume_col[ch] * fig_mask * 0.78

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'The Dancer at the Threshold of Colour' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=207)

    # ── Ground: deep blue-black — Orphist dark primed canvas ─────────────────
    p.tone_ground((0.12, 0.12, 0.20), texture_strength=0.008)

    # ── Underpainting: abstract mass, colour zone placement ───────────────────
    p.underpainting(ref_pil, stroke_size=58)

    # ── Block in: broad chromatic zones for disk fields ───────────────────────
    p.block_in(ref_pil, stroke_size=32)

    # ── Build form: figure volumes, tower lattice structure ───────────────────
    p.build_form(ref_pil, stroke_size=14)

    # ── Lights: optical peaks and white costume highlights ────────────────────
    p.place_lights(ref_pil, stroke_size=6)

    # ── Delaunay Orphist Disk Pass — PRIMARY chromatic field effect ───────────
    # Seven disks by golden-angle spiral, five complementary pairs cycling
    p.delaunay_orphist_disk_pass(
        n_disks=7,
        ring_frequency=5.0,
        disk_sigma=0.38,
        opacity=0.70,
    )

    # ── Second pass: tighter ring frequency, lower opacity — adds inner bands ─
    p.delaunay_orphist_disk_pass(
        n_disks=5,
        ring_frequency=9.0,
        disk_sigma=0.22,
        opacity=0.30,
        disk_centers=[
            (0.28, 0.22), (0.72, 0.20), (0.46, 0.52),
            (0.18, 0.68), (0.68, 0.72),
        ],
    )

    # ── Chromatic aberration: slight optical fringing at colour boundaries ────
    p.chromatic_aberration_pass(opacity=0.10)

    # ── Meso detail: surface energy on figure and tower ───────────────────────
    p.meso_detail_pass(strength=0.08, opacity=0.08)

    # ── Vignette: slight edge darkening to push the disk field forward ────────
    p.vignette_pass(opacity=0.18)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
