"""
run_leger_diver_underwater.py — Session 196

"The Diver" — after Fernand Léger

Image Description
─────────────────
Subject & Composition
    A single deep-sea diver seen from directly below, suspended at mid-depth,
    arms spread wide and legs slightly parted — a cruciform silhouette filling
    nearly the entire canvas. The viewer looks straight up from the seafloor.
    The diver occupies the center of the frame, head tilted downward, looking
    back at the viewer through a circular porthole visor.

The Figure
    The diver wears a vintage hard-hat diving suit — cylindrical brass helmet
    with four bolted porthole windows, corrugated rubber shoulder joints,
    canvas torso, thick rubberized gloves, and lead-soled boots. Every part of
    the suit is tubular and mechanical — the limbs are literal cylinders, the
    helmet a sphere on a cylinder neck-ring, the gloves barrel-shaped. The suit
    is rendered in cobalt blue shadow with cool grey highlights; the brass
    helmet glows chrome yellow. A single air hose spirals upward from the left
    shoulder, curling out of frame.
    Emotional state: weightless awe — suspended between worlds, neither
    belonging to the surface nor the deep, utterly at peace in the machine
    that keeps them alive.

The Environment
    Deep water surrounds the figure in bands of cobalt blue deepening to near-
    black at the edges. A shaft of golden sunlight descends from the upper-left
    corner, fragmenting into four geometric wedge-beams as it passes through
    the surface. The seafloor is implied rather than shown — a suggestion of
    grey silt and a single coral column (forest green, cylindrical) at lower-
    right. The water surface is visible at the very top as a shimmering
    horizontal stripe of chrome yellow and white — a flat graphic band, not a
    realistic rendering. Air bubbles rise in perfect white circles from the
    helmet's exhaust valve, forming a loose diagonal trail from center toward
    upper-right.

Technique & Palette
    Léger Tubist Contour Pass (leger_tubist_contour_pass, 107th distinct mode).
    Thick black outlines define every object boundary — helmet, suit segments,
    sunbeam edges, coral, bubble circles. Inside each outlined region: flat
    areas of primary colour, quantized to the Léger palette.
    Palette: cobalt blue (water / suit shadow), chrome yellow (sunbeam /
    helmet brass), cadmium red (suit accent / logo patch on shoulder),
    forest green (coral), cool grey (suit midtone / seafloor haze),
    near-black (outlines / deep water edges), off-white (bubbles / highlight
    on helmet glass).

Mood & Intent
    Heroic solitude. The mechanical body in the organic abyss. Léger believed
    the machine and the human were becoming one — here that merger is literal:
    the diver exists only by virtue of their machine-suit, rendered in the same
    geometric language as the surrounding industrial sea. The viewer is invited
    not to pity but to admire — this figure is master of their environment,
    floating with the stillness of a gyroscope. The emotion to carry away:
    quiet pride in human ingenuity, wonder at the alien beauty of the deep,
    and the paradox of life inside a machine.

Session 196 pass used:
    leger_tubist_contour_pass  (107th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "leger_diver_underwater.png"
)
W, H = 800, 900   # portrait — emphasises vertical suspension of the diver


def build_reference() -> np.ndarray:
    """
    Synthetic tonal reference encoding the underwater diver scene.

    Used only for its colour/luminance structure — the Tubist Contour pass
    needs real pictorial variation so it can detect edges and quantize regions.

    Tonal zones:
      - Deep blue water: medium-dark cobalt across most of frame
      - Sunlight shaft: bright chrome-yellow wedge from upper-left
      - Surface shimmer: bright horizontal band at very top
      - Diver figure: mid-tone central cruciform shape
        - Helmet: bright chrome-yellow sphere
        - Suit body: blue-grey cylinder
        - Gloves / boots: darker accent
        - Air hose: thin curved orange-red line
      - Coral column: forest-green cylinder, lower-right
      - Air bubbles: small bright circles trailing upper-right
      - Seafloor haze: slightly lighter grey at bottom strip
    """
    rng = np.random.default_rng(196)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Deep water background: cobalt blue gradient ───────────────────────────
    depth_t = np.clip(ys / 1.0, 0.0, 1.0)
    blue_r = 0.04 + 0.08 * (1.0 - depth_t)
    blue_g = 0.12 + 0.14 * (1.0 - depth_t)
    blue_b = 0.55 + 0.28 * (1.0 - depth_t)
    ref[:, :, 0] = blue_r
    ref[:, :, 1] = blue_g
    ref[:, :, 2] = blue_b

    # ── Surface shimmer: bright band at top (y < 0.06) ───────────────────────
    surf_t = np.clip(1.0 - ys / 0.06, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] + surf_t * (0.88 - ref[:, :, 0])
    ref[:, :, 1] = ref[:, :, 1] + surf_t * (0.80 - ref[:, :, 1])
    ref[:, :, 2] = ref[:, :, 2] + surf_t * (0.12 - ref[:, :, 2])

    # ── Sunlight shaft: bright wedge from upper-left ──────────────────────────
    # Four geometric wedge-beams: narrow triangles from top-left corner
    beam_origins = [(0.05, 0.0), (0.18, 0.0), (0.28, 0.0), (0.38, 0.0)]
    beam_angles = [0.45, 0.52, 0.58, 0.65]   # x-position at y=1.0 (spread)
    for (bx0, by0), ba in zip(beam_origins, beam_angles):
        # Triangle: apex at (bx0, by0), base width spreading to ba at bottom
        beam_cx = bx0 + (ba - bx0) * ys          # centre x at each row
        beam_hw = 0.012 + 0.04 * ys               # half-width growing with depth
        beam_dist = np.abs(xs - beam_cx) / (beam_hw + 1e-6)
        beam_mask = np.clip(1.0 - beam_dist, 0.0, 1.0) ** 1.5
        beam_mask = beam_mask * np.clip(1.0 - ys / 0.75, 0.0, 1.0)  # fade with depth
        ref[:, :, 0] = ref[:, :, 0] + beam_mask * (0.90 - ref[:, :, 0]) * 0.85
        ref[:, :, 1] = ref[:, :, 1] + beam_mask * (0.78 - ref[:, :, 1]) * 0.85
        ref[:, :, 2] = ref[:, :, 2] + beam_mask * (0.08 - ref[:, :, 2]) * 0.85

    # ── Diver: cruciform figure at center ────────────────────────────────────
    diver_cx = 0.50
    diver_cy = 0.48

    # Helmet: bright chrome-yellow sphere at top of figure
    helm_cx = diver_cx
    helm_cy = diver_cy - 0.14
    helm_r = 0.065
    helm_dist = np.sqrt(((xs - helm_cx) / helm_r) ** 2 + ((ys - helm_cy) / helm_r) ** 2)
    helm_mask = np.clip(1.0 - helm_dist, 0.0, 1.0) ** 0.7
    ref[:, :, 0] = ref[:, :, 0] * (1 - helm_mask) + 0.90 * helm_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - helm_mask) + 0.78 * helm_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - helm_mask) + 0.05 * helm_mask

    # Torso: grey-blue cylinder
    torso_half_w = 0.06
    torso_top = diver_cy - 0.08
    torso_bot = diver_cy + 0.16
    torso_mask_x = np.clip(1.0 - np.abs(xs - diver_cx) / torso_half_w, 0.0, 1.0)
    torso_mask_y = np.where((ys >= torso_top) & (ys <= torso_bot), 1.0, 0.0)
    torso_mask = (torso_mask_x ** 0.8) * torso_mask_y
    ref[:, :, 0] = ref[:, :, 0] * (1 - torso_mask) + 0.22 * torso_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - torso_mask) + 0.30 * torso_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - torso_mask) + 0.58 * torso_mask

    # Left arm: horizontal cylinder extending left
    arm_l_cx = diver_cx - 0.18
    arm_l_cy = diver_cy + 0.04
    arm_l_w = 0.18
    arm_l_h = 0.035
    arm_l_dist = (((xs - arm_l_cx) / arm_l_w) ** 2 + ((ys - arm_l_cy) / arm_l_h) ** 2)
    arm_l_mask = np.clip(1.0 - arm_l_dist ** 0.5, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1 - arm_l_mask) + 0.20 * arm_l_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - arm_l_mask) + 0.28 * arm_l_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - arm_l_mask) + 0.55 * arm_l_mask

    # Right arm: horizontal cylinder extending right
    arm_r_cx = diver_cx + 0.18
    arm_r_cy = diver_cy + 0.04
    arm_r_dist = (((xs - arm_r_cx) / arm_l_w) ** 2 + ((ys - arm_r_cy) / arm_l_h) ** 2)
    arm_r_mask = np.clip(1.0 - arm_r_dist ** 0.5, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1 - arm_r_mask) + 0.20 * arm_r_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - arm_r_mask) + 0.28 * arm_r_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - arm_r_mask) + 0.55 * arm_r_mask

    # Left leg: slightly spread cylinder going lower-left
    leg_l_cx = diver_cx - 0.08
    leg_l_cy = diver_cy + 0.28
    leg_l_w = 0.04
    leg_l_h = 0.16
    leg_l_dist = (((xs - leg_l_cx) / leg_l_w) ** 2 + ((ys - leg_l_cy) / leg_l_h) ** 2)
    leg_l_mask = np.clip(1.0 - leg_l_dist ** 0.5, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1 - leg_l_mask) + 0.18 * leg_l_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - leg_l_mask) + 0.26 * leg_l_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - leg_l_mask) + 0.52 * leg_l_mask

    # Right leg
    leg_r_cx = diver_cx + 0.08
    leg_r_cy = diver_cy + 0.28
    leg_r_dist = (((xs - leg_r_cx) / leg_l_w) ** 2 + ((ys - leg_r_cy) / leg_l_h) ** 2)
    leg_r_mask = np.clip(1.0 - leg_r_dist ** 0.5, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1 - leg_r_mask) + 0.18 * leg_r_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - leg_r_mask) + 0.26 * leg_r_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - leg_r_mask) + 0.52 * leg_r_mask

    # Lead boots: darker accent at bottom of legs
    for (bx, by) in [(leg_l_cx, leg_l_cy + 0.13), (leg_r_cx, leg_r_cy + 0.13)]:
        boot_dist = np.sqrt(((xs - bx) / 0.05) ** 2 + ((ys - by) / 0.04) ** 2)
        boot_mask = np.clip(1.0 - boot_dist, 0.0, 1.0) ** 0.8
        ref[:, :, 0] = ref[:, :, 0] * (1 - boot_mask) + 0.10 * boot_mask
        ref[:, :, 1] = ref[:, :, 1] * (1 - boot_mask) + 0.10 * boot_mask
        ref[:, :, 2] = ref[:, :, 2] * (1 - boot_mask) + 0.12 * boot_mask

    # Red shoulder logo patch
    patch_cx = diver_cx - 0.03
    patch_cy = diver_cy - 0.04
    patch_dist = np.sqrt(((xs - patch_cx) / 0.025) ** 2 + ((ys - patch_cy) / 0.018) ** 2)
    patch_mask = np.clip(1.0 - patch_dist, 0.0, 1.0) ** 0.9
    ref[:, :, 0] = ref[:, :, 0] * (1 - patch_mask) + 0.82 * patch_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - patch_mask) + 0.10 * patch_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - patch_mask) + 0.08 * patch_mask

    # Air hose: curved orange tube from left shoulder, spiraling up-left
    hose_cx_left = diver_cx - 0.06
    hose_cy_start = diver_cy - 0.06
    n_hose = 40
    for hi in range(n_hose):
        t = hi / float(n_hose)
        hx = hose_cx_left - 0.22 * t + 0.08 * np.sin(t * np.pi * 4)
        hy = hose_cy_start - 0.30 * t
        if hy < 0.0:
            break
        hose_dist = np.sqrt(((xs - hx) / 0.012) ** 2 + ((ys - hy) / 0.010) ** 2)
        hose_mask = np.clip(1.0 - hose_dist, 0.0, 1.0) ** 1.2
        ref[:, :, 0] = ref[:, :, 0] * (1 - hose_mask) + 0.85 * hose_mask
        ref[:, :, 1] = ref[:, :, 1] * (1 - hose_mask) + 0.38 * hose_mask
        ref[:, :, 2] = ref[:, :, 2] * (1 - hose_mask) + 0.05 * hose_mask

    # ── Coral column: forest green cylinder at lower-right ────────────────────
    coral_cx = 0.80
    coral_cy = 0.82
    coral_hw = 0.038
    coral_ht = 0.25
    coral_x_mask = np.clip(1.0 - np.abs(xs - coral_cx) / coral_hw, 0.0, 1.0)
    coral_y_mask = np.where(ys >= coral_cy - coral_ht, 1.0, 0.0)
    coral_mask = (coral_x_mask ** 0.8) * coral_y_mask
    ref[:, :, 0] = ref[:, :, 0] * (1 - coral_mask) + 0.10 * coral_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - coral_mask) + 0.42 * coral_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - coral_mask) + 0.18 * coral_mask

    # Coral cap: rounded top
    coral_cap_dist = np.sqrt(
        ((xs - coral_cx) / 0.055) ** 2 + ((ys - (coral_cy - coral_ht)) / 0.04) ** 2
    )
    coral_cap_mask = np.clip(1.0 - coral_cap_dist, 0.0, 1.0) ** 0.9
    ref[:, :, 0] = ref[:, :, 0] * (1 - coral_cap_mask) + 0.10 * coral_cap_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - coral_cap_mask) + 0.48 * coral_cap_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - coral_cap_mask) + 0.20 * coral_cap_mask

    # ── Air bubbles: white circles trailing upper-right ───────────────────────
    bubble_positions = [
        (diver_cx + 0.02, helm_cy + 0.03, 0.018),
        (diver_cx + 0.05, helm_cy - 0.04, 0.014),
        (diver_cx + 0.09, helm_cy - 0.11, 0.011),
        (diver_cx + 0.13, helm_cy - 0.17, 0.016),
        (diver_cx + 0.16, helm_cy - 0.25, 0.010),
        (diver_cx + 0.20, helm_cy - 0.32, 0.013),
    ]
    for (bx, by, br) in bubble_positions:
        if by < 0.0:
            continue
        bub_dist = np.sqrt(((xs - bx) / br) ** 2 + ((ys - by) / br) ** 2)
        bub_shell = np.clip(
            (1.0 - np.abs(bub_dist - 0.65) / 0.35), 0.0, 1.0
        ) ** 1.5
        ref[:, :, 0] = ref[:, :, 0] * (1 - bub_shell) + 0.92 * bub_shell
        ref[:, :, 1] = ref[:, :, 1] * (1 - bub_shell) + 0.92 * bub_shell
        ref[:, :, 2] = ref[:, :, 2] * (1 - bub_shell) + 0.94 * bub_shell

    # ── Seafloor haze: lighter grey-blue at very bottom ───────────────────────
    floor_t = np.clip((ys - 0.88) / 0.12, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] + floor_t * (0.38 - ref[:, :, 0]) * 0.50
    ref[:, :, 1] = ref[:, :, 1] + floor_t * (0.40 - ref[:, :, 1]) * 0.50
    ref[:, :, 2] = ref[:, :, 2] + floor_t * (0.44 - ref[:, :, 2]) * 0.50

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'The Diver' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=196)

    # ── Ground: deep ocean off-white — slightly blue-tinted ───────────────────
    p.tone_ground((0.88, 0.90, 0.94), texture_strength=0.02)

    # ── Underpainting: lay in broad tonal masses from reference ───────────────
    p.underpainting(ref_pil, stroke_size=42)
    p.block_in(ref_pil, stroke_size=26)

    # ── Léger Tubist Contour pass: THE signature effect ───────────────────────
    # Primary pass — strong primary-palette snap, thick outlines
    p.leger_tubist_contour_pass(
        contour_thickness=5,
        contour_threshold=0.15,
        flat_fill_strength=0.70,
        primary_shift=0.65,
        contour_strength=0.92,
        opacity=0.88,
        seed=196,
    )

    # ── Second Léger pass: slightly tighter threshold to refine inner edges ───
    # Catches subtle interior details (helmet rivets, suit pleats, bubble rims)
    p.leger_tubist_contour_pass(
        contour_thickness=3,
        contour_threshold=0.28,
        flat_fill_strength=0.40,
        primary_shift=0.35,
        contour_strength=0.85,
        opacity=0.42,
        seed=196,
    )

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
