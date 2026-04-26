"""
run_beksinski_crow_angel.py — Session 189

Paints a Beksiński-inspired scene: a solitary crow perched on the outstretched
arm of a crumbling stone angel in a forgotten graveyard, at the last moment of
dusk. Renders the signature Beksiński atmosphere — ashen void, ember warmth
bleeding through the deepest shadows, obsessive micro-texture.

Session 189 passes used:
  beksinski_dystopian_atmosphere_pass  (99th distinct mode)
  imprimatura_reveal_pass              (100th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beksinski_crow_angel.png")
W, H = 800, 1060


def build_reference() -> np.ndarray:
    """
    Programmatic colour-field reference for the crow-and-angel graveyard scene.

    Zones (top → bottom):
      - Heavy cloud sky, near-black, with sickly amber glow at the horizon
      - Skeletal tree silhouettes, upper 60%
      - Stone angel torso and outstretched arm, centre-left
      - Crow silhouette perched on the arm, upper-left area
      - Foreground plinth, dead leaves, frost
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0, 1, H)[:, None]
    xs = np.linspace(0, 1, W)[None, :]

    # ── Sky: heavy ashen clouds with amber band at horizon ─────────────────
    horizon_y = 0.58
    sky_pos = np.clip(ys / horizon_y, 0.0, 1.0)

    # Upper sky: mid-value ash-grey (Beksiński's oppressive clouds)
    sky_r = 0.32 + 0.14 * (1.0 - sky_pos)
    sky_g = 0.26 + 0.12 * (1.0 - sky_pos)
    sky_b = 0.24 + 0.14 * (1.0 - sky_pos)

    # Horizon amber glow: very wide, very bright — the primary light source
    horiz_gate = np.exp(-((ys - horizon_y) ** 2) / (2 * 0.035 ** 2)).astype(np.float32)
    horiz_gate = np.clip(horiz_gate, 0.0, 1.0)
    sky_r = sky_r + 0.62 * horiz_gate
    sky_g = sky_g + 0.36 * horiz_gate
    sky_b = sky_b + 0.06 * horiz_gate

    # Cloud texture: large-scale noise
    rng = np.random.default_rng(42)
    noise = rng.standard_normal((H, W)).astype(np.float32)
    cloud_texture = gaussian_filter(noise, sigma=28) * 0.05
    sky_r = np.clip(sky_r + cloud_texture, 0.0, 1.0)
    sky_g = np.clip(sky_g + cloud_texture * 0.7, 0.0, 1.0)
    sky_b = np.clip(sky_b + cloud_texture * 0.5, 0.0, 1.0)

    ref[:, :, 0] = sky_r
    ref[:, :, 1] = sky_g
    ref[:, :, 2] = sky_b

    # ── Ground / earth below horizon ──────────────────────────────────────
    ground_mask = np.clip((ys - horizon_y) / 0.08, 0.0, 1.0).astype(np.float32)
    ground_r = 0.20 + 0.08 * (1.0 - xs)
    ground_g = 0.14 + 0.05 * (1.0 - xs)
    ground_b = 0.09 + 0.03 * (1.0 - xs)
    ref[:, :, 0] = ref[:, :, 0] * (1.0 - ground_mask) + ground_r * ground_mask
    ref[:, :, 1] = ref[:, :, 1] * (1.0 - ground_mask) + ground_g * ground_mask
    ref[:, :, 2] = ref[:, :, 2] * (1.0 - ground_mask) + ground_b * ground_mask

    # ── Skeletal trees: spidery dark silhouettes ──────────────────────────
    # Several vertical trunks with slight sway, upper 80% of frame
    tree_mask = np.zeros((H, W), dtype=np.float32)
    tree_defs = [
        # (x-center, x-width, y-max, y-min-taper)
        (0.08, 0.012, 1.0, 0.05),
        (0.18, 0.010, 0.95, 0.04),
        (0.78, 0.013, 1.0, 0.05),
        (0.88, 0.011, 0.97, 0.04),
        (0.94, 0.009, 0.90, 0.06),
        (0.03, 0.008, 0.85, 0.08),
    ]
    for tx, tw, ty_max, ty_min in tree_defs:
        # Trunk: narrow Gaussian column
        trunk = np.exp(-((xs - tx) ** 2) / (2 * tw ** 2)).astype(np.float32)
        # Taper: narrower at top
        taper = np.clip((ty_max - ys) / (ty_max - ty_min), 0.0, 1.0).astype(np.float32)
        trunk = trunk * taper
        tree_mask = np.maximum(tree_mask, trunk)

    # Branch spray: random thin horizontal diagonals near upper tree zones
    branch_noise = gaussian_filter(rng.uniform(0, 1, (H, W)).astype(np.float32), sigma=0.3)
    branch_zone = np.clip(1.0 - ys / 0.70, 0.0, 1.0) * np.clip(np.abs(xs - 0.5) - 0.15, 0.0, 1.0)
    branch_mask = np.clip((branch_noise - 0.985) * 40.0, 0.0, 1.0).astype(np.float32) * branch_zone
    tree_mask = np.minimum(tree_mask + branch_mask * 0.4, 1.0)

    tree_r = 0.06 * (1.0 - tree_mask)
    tree_g = 0.05 * (1.0 - tree_mask)
    tree_b = 0.04 * (1.0 - tree_mask)
    blend_t = np.clip(tree_mask * 1.4, 0.0, 1.0)
    ref[:, :, 0] = ref[:, :, 0] * (1.0 - blend_t) + tree_r * blend_t
    ref[:, :, 1] = ref[:, :, 1] * (1.0 - blend_t) + tree_g * blend_t
    ref[:, :, 2] = ref[:, :, 2] * (1.0 - blend_t) + tree_b * blend_t

    # ── Stone angel: weathered grey form, centre-right, from mid to bottom ─
    # Body mass: tall ellipse
    angel_cx, angel_cy = 0.54, 0.62
    angel_rx, angel_ry = 0.16, 0.34
    angel_body = np.clip(
        1.0 - np.sqrt(((xs - angel_cx) / angel_rx) ** 2 + ((ys - angel_cy) / angel_ry) ** 2),
        0.0, 1.0,
    ).astype(np.float32) ** 1.4

    # Head: slightly above body centre, small ellipse
    head_cx, head_cy = 0.52, 0.30
    head_r = 0.10
    angel_head = np.clip(
        1.0 - np.sqrt(((xs - head_cx) / head_r) ** 2 + ((ys - head_cy) / (head_r * 1.2)) ** 2),
        0.0, 1.0,
    ).astype(np.float32) ** 1.6

    # Outstretched left arm: horizontal ellipse extending toward left
    arm_cx, arm_cy = 0.32, 0.47
    arm_rx, arm_ry = 0.24, 0.055
    angel_arm = np.clip(
        1.0 - np.sqrt(((xs - arm_cx) / arm_rx) ** 2 + ((ys - arm_cy) / arm_ry) ** 2),
        0.0, 1.0,
    ).astype(np.float32) ** 1.2

    angel_mask = np.maximum(np.maximum(angel_body, angel_head), angel_arm)

    # Angel colour: cold ash stone with warm imprimatura glow in shadow areas
    angel_luma = np.clip(0.55 + 0.30 * (1.0 - ys) + 0.10 * xs, 0.0, 1.0).astype(np.float32)
    stone_r = 0.55 + 0.28 * angel_luma
    stone_g = 0.50 + 0.26 * angel_luma
    stone_b = 0.46 + 0.18 * angel_luma

    # Add moss patches: greenish-grey in shadow areas
    moss_noise = gaussian_filter(rng.uniform(0, 1, (H, W)).astype(np.float32), sigma=4)
    moss_gate = np.clip((moss_noise - 0.58) * 5.0, 0.0, 1.0) * angel_mask
    stone_r = stone_r - 0.06 * moss_gate
    stone_g = stone_g + 0.04 * moss_gate
    stone_b = stone_b - 0.02 * moss_gate

    # Fissures: thin darker lines across the stone
    fissure_noise = gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), sigma=0.6)
    fissure_gate = np.clip(np.abs(fissure_noise) - 2.4, 0.0, 1.0) * angel_mask
    stone_r = stone_r - 0.12 * fissure_gate
    stone_g = stone_g - 0.10 * fissure_gate
    stone_b = stone_b - 0.08 * fissure_gate

    ref[:, :, 0] = ref[:, :, 0] * (1.0 - angel_mask * 0.9) + np.clip(stone_r, 0.0, 1.0) * angel_mask * 0.9
    ref[:, :, 1] = ref[:, :, 1] * (1.0 - angel_mask * 0.9) + np.clip(stone_g, 0.0, 1.0) * angel_mask * 0.9
    ref[:, :, 2] = ref[:, :, 2] * (1.0 - angel_mask * 0.9) + np.clip(stone_b, 0.0, 1.0) * angel_mask * 0.9

    # ── Crow: near-black silhouette with iridescent blue-blue sheen ────────
    # Perched on the arm, upper-left region
    crow_cx, crow_cy = 0.24, 0.44
    crow_rx, crow_ry = 0.075, 0.055
    crow_body = np.clip(
        1.0 - np.sqrt(((xs - crow_cx) / crow_rx) ** 2 + ((ys - crow_cy) / crow_ry) ** 2),
        0.0, 1.0,
    ).astype(np.float32) ** 1.5

    # Wing: half-spread, slightly above and to the left
    wing_cx, wing_cy = 0.17, 0.41
    wing_rx, wing_ry = 0.11, 0.038
    wing_angle_mask = np.clip(1.0 - ((xs - wing_cx) / wing_rx) ** 2 - ((ys - wing_cy - 0.02 * (xs - wing_cx)) / wing_ry) ** 2, 0.0, 1.0).astype(np.float32) ** 1.3

    # Head: small circle above body
    chead_cx, chead_cy = 0.26, 0.40
    chead_r = 0.028
    crow_head = np.clip(
        1.0 - np.sqrt(((xs - chead_cx) / chead_r) ** 2 + ((ys - chead_cy) / chead_r) ** 2),
        0.0, 1.0,
    ).astype(np.float32) ** 1.8

    crow_mask = np.maximum(np.maximum(crow_body, wing_angle_mask), crow_head)

    # Crow colour: near-black with iridescent blue-violet sheen on catching light
    sheen_direction = np.clip(-(xs - 0.24) * 2.5, 0.0, 1.0).astype(np.float32)  # left-side sheen
    crow_r = 0.04 + 0.06 * sheen_direction
    crow_g = 0.04 + 0.08 * sheen_direction
    crow_b = 0.05 + 0.18 * sheen_direction

    # Amber eye glint: tiny warm point
    eye_cx, eye_cy = 0.268, 0.393
    eye_dist = np.sqrt(((xs - eye_cx) / 0.008) ** 2 + ((ys - eye_cy) / 0.006) ** 2)
    eye_gate = np.clip(1.0 - eye_dist, 0.0, 1.0).astype(np.float32) ** 2
    crow_r = crow_r + 0.70 * eye_gate
    crow_g = crow_g + 0.35 * eye_gate
    crow_b = crow_b + 0.02 * eye_gate

    ref[:, :, 0] = ref[:, :, 0] * (1.0 - crow_mask) + np.clip(crow_r, 0.0, 1.0) * crow_mask
    ref[:, :, 1] = ref[:, :, 1] * (1.0 - crow_mask) + np.clip(crow_g, 0.0, 1.0) * crow_mask
    ref[:, :, 2] = ref[:, :, 2] * (1.0 - crow_mask) + np.clip(crow_b, 0.0, 1.0) * crow_mask

    # ── Foreground plinth and ground ──────────────────────────────────────
    plinth_top = 0.90
    plinth_mask = np.clip((ys - plinth_top) / 0.06, 0.0, 1.0).astype(np.float32)
    plinth_r = 0.22 + 0.06 * (1.0 - xs)
    plinth_g = 0.18 + 0.04 * (1.0 - xs)
    plinth_b = 0.14 + 0.02 * (1.0 - xs)

    # Frost crystals: sparse bright points on plinth
    frost_noise = rng.uniform(0, 1, (H, W)).astype(np.float32)
    frost_gate = np.clip((frost_noise - 0.992) * 200, 0.0, 1.0) * plinth_mask
    plinth_r = plinth_r + 0.60 * frost_gate
    plinth_g = plinth_g + 0.62 * frost_gate
    plinth_b = plinth_b + 0.65 * frost_gate

    # Dead leaf scatter: warm brown flecks
    leaf_noise = gaussian_filter(rng.uniform(0, 1, (H, W)).astype(np.float32), sigma=1.2)
    leaf_gate = np.clip((leaf_noise - 0.74) * 6, 0.0, 1.0) * plinth_mask
    plinth_r = plinth_r + 0.20 * leaf_gate
    plinth_g = plinth_g + 0.08 * leaf_gate
    plinth_b = plinth_b + 0.00 * leaf_gate

    ref[:, :, 0] = ref[:, :, 0] * (1.0 - plinth_mask * 0.85) + np.clip(plinth_r, 0.0, 1.0) * plinth_mask * 0.85
    ref[:, :, 1] = ref[:, :, 1] * (1.0 - plinth_mask * 0.85) + np.clip(plinth_g, 0.0, 1.0) * plinth_mask * 0.85
    ref[:, :, 2] = ref[:, :, 2] * (1.0 - plinth_mask * 0.85) + np.clip(plinth_b, 0.0, 1.0) * plinth_mask * 0.85

    # Ensure readable tonal range — Beksiński passes will darken shadows
    ref = 0.12 + 0.88 * ref

    return np.clip(ref, 0.0, 1.0).astype(np.float32)


def main():
    print("=== Beksinski: The Crow and the Angel (Session 189) ===")
    print(f"Canvas: {W}×{H}")

    ref = build_reference()
    print("Reference built.")

    p = Painter(W, H)

    # ── Ground: warm mid-sienna — structural tonal base ──────────────────
    print("  tone_ground ...")
    p.tone_ground((0.52, 0.38, 0.22), texture_strength=0.055)

    # ── Underpainting: establish broad tonal masses ────────────────────────
    print("  underpainting ...")
    p.underpainting(ref, stroke_size=75, n_strokes=120)

    # ── Block-in: build readable image structure ───────────────────────────
    print("  block_in ...")
    p.block_in(ref, stroke_size=38, n_strokes=260)

    # ── Build form: small marks, detail accumulation ───────────────────────
    print("  build_form ...")
    p.build_form(ref, stroke_size=14, n_strokes=320)

    # ── Imprimatura reveal: warm sienna ground glowing through shadows ─────
    print("  imprimatura_reveal_pass (100th mode) ...")
    p.imprimatura_reveal_pass(
        ground_color=(0.38, 0.22, 0.10),
        reveal_strength=0.28,
        thin_paint_luma=0.45,
        opacity=0.28,
    )

    # ── Beksiński dystopian atmosphere: the defining aesthetic move ────────
    print("  beksinski_dystopian_atmosphere_pass (99th mode) ...")
    p.beksinski_dystopian_atmosphere_pass(
        ash_pull=0.25,
        shadow_deepen=0.18,
        ember_glow=0.18,
        grain_strength=0.016,
        opacity=0.35,
    )

    # ── Scumble: Beksiński's obsessive layered surface quality ─────────────
    print("  scumble_pass ...")
    p.scumble_pass(
        opacity=0.12,
        n_drags=300,
        dry_factor=0.90,
        drag_distance=10,
    )

    # ── Edge definition: tighten crow silhouette and angel contour ─────────
    print("  edge_definition_pass ...")
    p.edge_definition_pass(
        edge_sigma=0.7,
        strength=0.35,
        soft_threshold=0.05,
        luma_lo=0.05,
        luma_hi=0.92,
        opacity=0.28,
    )

    # ── Canvas grain: geological surface texture ───────────────────────────
    print("  canvas_grain_pass ...")
    p.canvas_grain_pass(
        noise_scale=1.0,
        noise_strength=0.018,
        sharpness=0.14,
        luma_lo=0.06,
        luma_hi=0.88,
        opacity=0.22,
    )

    # ── Final glaze: very faint amber warmth ──────────────────────────────
    print("  glaze ...")
    p.glaze((0.35, 0.22, 0.10), opacity=0.030)

    # ── Finish: moderate vignette, no crackle ─────────────────────────────
    print("  finish ...")
    p.finish(vignette=0.30, crackle=False)

    p.save(OUTPUT)
    print(f"\nSaved → {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
