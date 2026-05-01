"""paint_s282_frozen_river_dawn.py -- Session 282: Alexei Savrasov (193rd mode)

Subject & Composition:
    A wide Russian river in late February, seen from the high bank at dawn.
    The river stretches from the lower-left to the upper-right, still mostly
    frozen -- a broad blue-white expanse of ice -- with dark open water channels
    beginning to appear at the edges where the current runs fastest. The horizon
    is ruled by a pale, slightly violet-grey overcast sky: the unmistakable
    Savrasov grey of Russian late-winter light. The viewpoint is from the high
    left bank, looking across the river toward the far bank, where a village
    church with a white bell tower stands against the sky. Three or four bare
    willow trees lean over the near bank at the right, their intricate branch
    networks silhouetted against the pale sky and ice.

The River:
    The ice surface dominates the lower two-thirds of the image. It is not
    uniform: the central channel shows the most active surface -- mottled
    blue-white with faint grey cracks and pressure ridges running diagonally.
    Where the ice approaches the near bank, it is darkened by trapped debris
    and the shadow of the willows. At the far left, an open water channel
    about 20 meters wide runs along the far bank -- the first sign of thaw.
    This water is a deep, slightly greenish-black, reflecting the pale sky in
    broken patches. The near bank is snow-covered -- warm cream-yellow where
    the early morning light catches it, cool blue-grey in the shadow.

The Environment:
    Central Russia, the Volga or Oka watershed region, late February, 7 AM.
    Temperature just below freezing. The air is still and damp; a faint mist
    rises from the open water channel. The light is diffuse, directionless --
    the sun not yet risen above the cloud layer, but the sky is brightening
    from the east (right side). The willow trees are bare and black against
    the sky. In the far distance, across the ice, a treeline of dark conifers
    marks the far horizon. The village church's bell tower is the only
    vertical accent in the flat landscape. Two or three rooks circle
    silently above the far bank treeline.

Technique & Palette:
    Alexei Savrasov's method: horizontal atmospheric layering in the sky,
    the specific cool-grey of late-winter Russian light, bare branches sharp
    and precise against the pale sky, warm straw-ochre in the snow-covered
    lower banks. The palette is muted -- near-neutral -- with the warm ochre
    of the snow and the slight violet of the sky as the only color notes.
    The whole painting breathes the specific mood of early spring longing
    that made Savrasov the father of Russian lyrical landscape.

Mood & Intent:
    The melancholic promise of approaching spring -- the river is still frozen,
    the trees still bare, but the cracks in the ice and the open water channel
    speak of change to come. The painting should convey the specific Russian
    emotion of 'vesna' (spring longing) -- the season not yet arrived but
    already palpable in the quality of the light. The viewer should feel the
    silence, the cold, the vast flatness of the Russian river landscape, and
    in that silence, the stirring of something new.

New in s282:
    - savrasov_lyrical_mist_pass (193rd mode): horizontal atmospheric mist
      banding, mid-luminance cool-grey bell gate, vertical-gradient bare-branch
      sharpening, lower-zone × saturation warm ochre horizon
    - paint_contre_jour_rim_pass (improvement): warm rim at dark/light
      boundaries, cool halation on bright side of contre-jour edges,
      gradient-magnitude-weighted spatial mask
"""

import os
import sys
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

W, H = 1440, 1040   # landscape -- wide river panorama

# ── Procedural reference image (landscape, no figures) ───────────────────────

def build_reference(width: int, height: int, seed: int = 282) -> np.ndarray:
    """Build a frozen river at dawn reference -- Savrasov late-winter palette."""
    rng = np.random.default_rng(seed)

    img = np.zeros((height, width, 3), dtype=np.float32)

    Yn, Xn = np.mgrid[0:height, 0:width].astype(np.float32)
    Yn = Yn / (height - 1)
    Xn = Xn / (width  - 1)

    # ── Sky (top 42%) ────────────────────────────────────────────────────────
    # Savrasov grey: pale, slightly violet, luminous overcast
    # Zenith: warm pale grey; Horizon: slightly cooler, near-white
    sky_top    = np.array([0.72, 0.70, 0.68], dtype=np.float32)  # warm-grey zenith
    sky_horizon= np.array([0.82, 0.82, 0.84], dtype=np.float32)  # pale near-white horizon

    sky_zone = 0.42
    sky_mask = np.clip(1.0 - Yn / sky_zone, 0.0, 1.0)
    sky_blend = sky_mask ** 1.3  # weight for zenith tone
    sky_horizon_blend = sky_mask ** 0.4  # weight for horizon tone (broader near horizon)

    for c in range(3):
        img[:, :, c] += (sky_top[c] * sky_blend +
                         sky_horizon[c] * (sky_horizon_blend - sky_blend)) * sky_mask

    # Subtle horizontal mist bands in sky (3 layers)
    for i, (y_center, width_band, brightness, hue_shift) in enumerate([
        (0.32, 0.04, 0.05, np.array([ 0.01,  0.00, -0.01])),
        (0.36, 0.03, 0.04, np.array([-0.01,  0.00,  0.02])),
        (0.40, 0.02, 0.06, np.array([ 0.02, -0.01,  0.00])),
    ]):
        band_mask = np.clip(1.0 - np.abs(Yn - y_center) / width_band, 0.0, 1.0) * sky_mask
        for c in range(3):
            img[:, :, c] += band_mask * (brightness + hue_shift[c]) * 0.5

    # ── River / ice (middle zone 25% to 85%) ────────────────────────────────
    river_top = 0.40
    river_bottom = 0.88

    # The river runs diagonally -- near bank is bottom-left, far bank upper-right
    # Ice surface base: blue-white mottled
    ice_base   = np.array([0.76, 0.80, 0.86], dtype=np.float32)  # blue-white ice
    ice_shadow = np.array([0.54, 0.60, 0.68], dtype=np.float32)  # shadow zone on ice

    river_mask = np.clip(
        (Yn - river_top) / max(river_bottom - river_top, 0.01), 0.0, 1.0
    ) * np.clip(1.0 - (Yn - river_bottom) / 0.05, 0.0, 1.0)

    # Ice mottling: diagonal pressure ridges
    ridge_noise = rng.uniform(-0.06, 0.06, (height, width)).astype(np.float32)
    ice_value = np.clip(0.80 + ridge_noise * river_mask, 0.0, 1.0).astype(np.float32)

    for c in range(3):
        ice_col = ice_base[c] * (1.0 - 0.3 * (1.0 - ice_value))
        img[:, :, c] += ice_col * river_mask * 0.85

    # Ice cracks: a few thin dark diagonal lines
    for angle, offset in [(0.42, 0.30), (0.38, 0.55), (0.46, 0.70)]:
        crack = np.abs(Xn - (Yn * angle + offset))
        crack_mask = np.clip(1.0 - crack / 0.004, 0.0, 1.0) ** 3 * river_mask
        for c in range(3):
            img[:, :, c] -= crack_mask * 0.15

    # Open water channel at far-left edge (dark, reflecting sky)
    open_water_x = 0.08
    open_water_w = 0.06
    water_mask = np.clip(1.0 - np.abs(Xn - open_water_x) / open_water_w, 0.0, 1.0)
    water_mask = water_mask * river_mask * np.clip((Yn - 0.38) / 0.10, 0.0, 1.0)
    water_col = np.array([0.22, 0.28, 0.32], dtype=np.float32)  # dark greenish-black water
    for c in range(3):
        img[:, :, c] = img[:, :, c] * (1.0 - water_mask * 0.85) + water_col[c] * water_mask

    # Mist over open water
    mist_mask = np.clip((1.0 - np.abs(Xn - open_water_x) / (open_water_w * 2.5)), 0.0, 1.0)
    mist_mask = mist_mask * np.clip((Yn - 0.38) / 0.10, 0.0, 1.0) * np.clip(1.0 - (Yn - 0.55) / 0.15, 0.0, 1.0)
    mist_col  = np.array([0.78, 0.80, 0.82], dtype=np.float32)
    for c in range(3):
        img[:, :, c] = np.clip(img[:, :, c] + mist_col[c] * mist_mask * 0.22, 0.0, 1.0)

    # ── Near bank (snow-covered, bottom 15%) ────────────────────────────────
    bank_zone = 0.84
    bank_mask = np.clip((Yn - bank_zone) / (1.0 - bank_zone), 0.0, 1.0) ** 0.8

    snow_warm = np.array([0.86, 0.82, 0.68], dtype=np.float32)  # sunlit snow -- warm ochre
    snow_cool = np.array([0.70, 0.72, 0.78], dtype=np.float32)  # shadow snow -- cool blue

    # Right side of bank is in more shadow (under willows)
    shadow_x = np.clip((Xn - 0.55) / 0.45, 0.0, 1.0)
    for c in range(3):
        snow_col = snow_warm[c] * (1.0 - shadow_x) + snow_cool[c] * shadow_x
        img[:, :, c] = (img[:, :, c] * (1.0 - bank_mask * 0.90) +
                        snow_col * bank_mask * 0.90)

    # ── Distant far bank + village church (at horizon, ~40% height) ─────────
    # Treeline silhouette at horizon
    treeline_y = 0.41
    treeline_noise = rng.uniform(-0.02, 0.02, width).astype(np.float32)
    for x in range(width):
        tree_h = treeline_y + treeline_noise[x]
        # Dark conifer silhouette
        if 0.1 < Xn[0, x] < 0.55:
            for y in range(height):
                y_n = Yn[y, 0]
                if treeline_y + 0.01 > y_n > treeline_y - 0.04:
                    dist = abs(y_n - treeline_y) / 0.04
                    mask_v = max(0.0, 1.0 - dist) ** 2 * 0.6
                    for c in range(3):
                        img[y, x, c] = img[y, x, c] * (1.0 - mask_v) + 0.28 * mask_v

    # Church bell tower: right of center, at horizon
    church_x = 0.68
    church_w = 0.012
    church_base = 0.22
    church_top  = 0.39
    church_mask = (
        np.clip(1.0 - np.abs(Xn - church_x) / church_w, 0.0, 1.0) *
        np.clip((church_top - Yn) / max(church_top - church_base, 0.01), 0.0, 1.0) *
        np.clip((Yn - church_base) / 0.02, 0.0, 1.0)
    )
    church_col = np.array([0.90, 0.88, 0.84], dtype=np.float32)  # white church tower
    for c in range(3):
        img[:, :, c] = (img[:, :, c] * (1.0 - church_mask * 0.90) +
                        church_col[c] * church_mask)

    # Bell tower dome (slightly rounded top)
    dome_cx, dome_cy, dome_r = church_x, church_base - 0.02, 0.018
    dome_dist = np.sqrt((Xn - dome_cx)**2 + ((Yn - dome_cy) * 0.6)**2)
    dome_mask = np.clip(1.0 - dome_dist / dome_r, 0.0, 1.0) ** 2 * 0.70
    for c in range(3):
        img[:, :, c] = (img[:, :, c] * (1.0 - dome_mask) +
                        church_col[c] * dome_mask)

    # Cross atop dome
    cross_cx, cross_top_y = church_x, church_base - 0.04
    cross_mask = (
        np.clip(1.0 - np.abs(Xn - cross_cx) / 0.002, 0.0, 1.0) *
        np.clip(1.0 - np.abs(Yn - cross_top_y - 0.012) / 0.014, 0.0, 1.0)
    )
    cross_mask_h = (
        np.clip(1.0 - np.abs(Yn - cross_top_y - 0.015) / 0.002, 0.0, 1.0) *
        np.clip(1.0 - np.abs(Xn - cross_cx) / 0.008, 0.0, 1.0)
    )
    cross_mask = np.clip(cross_mask + cross_mask_h, 0.0, 1.0) * 0.60
    for c in range(3):
        img[:, :, c] = img[:, :, c] * (1.0 - cross_mask) + 0.22 * cross_mask

    # ── Willow trees (right bank, foreground) ────────────────────────────────
    # 3-4 bare willows leaning over the ice from the right edge
    willows = [
        (0.82, 0.55, 0.007, 0.15),   # x_base, lean, trunk_w, height_frac
        (0.89, 0.48, 0.006, 0.18),
        (0.94, 0.52, 0.005, 0.14),
        (0.76, 0.58, 0.006, 0.12),
    ]

    for wx, lean, tw, height_frac in willows:
        # Trunk: runs from bottom bank upward, leaning toward left (lean < 0.5 = lean left)
        trunk_top_x = wx - (0.5 - lean) * 0.25  # where trunk meets sky
        trunk_top_y = bank_zone - height_frac    # trunk top height

        for y in range(height):
            yn = Yn[y, 0]
            if yn < trunk_top_y or yn > bank_zone + 0.05:
                continue
            # Linear trunk position
            t = (bank_zone - yn) / max(bank_zone - trunk_top_y, 0.001)
            trunk_cx = wx + (trunk_top_x - wx) * t
            trunk_w_px = tw * (1.0 - t * 0.5)
            dist = np.abs(Xn[y] - trunk_cx)
            tmask = np.clip(1.0 - dist / max(trunk_w_px, 0.001), 0.0, 1.0) ** 1.5
            for c in range(3):
                img[y, :, c] = img[y, :, c] * (1.0 - tmask * 0.75) + 0.20 * tmask * 0.75

        # Branch clusters: random fan from top of trunk
        n_branches = rng.integers(8, 14)
        for _ in range(n_branches):
            bx0 = trunk_top_x + rng.uniform(-0.03, 0.03)
            by0 = trunk_top_y + rng.uniform(0.0, height_frac * 0.4)
            bx1 = bx0 + rng.uniform(-0.10, 0.06)
            by1 = by0 - rng.uniform(0.04, 0.12)
            bw  = rng.uniform(0.003, 0.006)

            # Draw branch as a narrow ellipse (approximated)
            bdx = Xn - bx0
            bdy = Yn - by0
            along  = bdx * (bx1 - bx0) + bdy * (by1 - by0)
            total_l = max(np.sqrt((bx1 - bx0)**2 + (by1 - by0)**2), 0.001)
            perp   = np.abs(bdx * (-(by1 - by0)) + bdy * (bx1 - bx0)) / total_l
            t_along = np.clip(along / (total_l**2), 0.0, 1.0)
            branch_mask = (np.clip(1.0 - perp / bw, 0.0, 1.0) ** 2 *
                           np.clip(t_along, 0.0, 1.0))

            for c in range(3):
                img[:, :, c] = (img[:, :, c] * (1.0 - branch_mask * 0.70) +
                                0.18 * branch_mask * 0.70)

    # ── Rooks in distant sky (small black specks above treeline) ─────────────
    n_rooks = rng.integers(5, 9)
    rook_xs = rng.uniform(0.20, 0.55, n_rooks).astype(np.float32)
    rook_ys = rng.uniform(0.25, 0.38, n_rooks).astype(np.float32)
    for rx, ry in zip(rook_xs, rook_ys):
        # Each rook is a tiny V-shape (two short diagonal lines)
        for wing_dx, wing_dy in [(-0.008, -0.003), (0.008, -0.003)]:
            wdist = np.sqrt((Xn - rx - wing_dx / 2)**2 + (Yn - ry - wing_dy / 2)**2)
            wmask = np.clip(1.0 - wdist / 0.004, 0.0, 1.0) ** 2 * 0.6
            for c in range(3):
                img[:, :, c] = img[:, :, c] * (1.0 - wmask) + 0.10 * wmask

    # ── Subtle texture noise ─────────────────────────────────────────────────
    noise = rng.uniform(-0.025, 0.025, (height, width, 3)).astype(np.float32)
    img = np.clip(img + noise, 0.0, 1.0)

    return (img * 255).astype(np.uint8)


print("Building procedural frozen river reference...")
ref = build_reference(W, H, seed=282)
if ref.shape[2] == 4:
    ref = ref[:, :, :3]
print(f"Reference built: {ref.shape}")

# ── Painter setup ─────────────────────────────────────────────────────────────
from stroke_engine import Painter

p = Painter(W, H, seed=282)

# Pale warm-grey ground -- overcast late-winter light on canvas
p.tone_ground((0.68, 0.64, 0.56), texture_strength=0.018)

# ── Structural passes ─────────────────────────────────────────────────────────
print("Underpainting...")
p.underpainting(ref, stroke_size=52, n_strokes=250)
p.underpainting(ref, stroke_size=44, n_strokes=240)

print("Block-in (broad masses)...")
p.block_in(ref, stroke_size=32, n_strokes=490)
p.block_in(ref, stroke_size=20, n_strokes=520)

print("Build form (modelling)...")
p.build_form(ref, stroke_size=12, n_strokes=540)
p.build_form(ref, stroke_size=6,  n_strokes=460)

print("Lights and accents...")
p.place_lights(ref, stroke_size=4, n_strokes=310)

# ── Artist passes ─────────────────────────────────────────────────────────────
print("Savrasov lyrical mist (193rd mode)...")
p.savrasov_lyrical_mist_pass(
    mist_hwidth        = 42,
    mist_vwidth        = 2,
    mist_strength      = 0.32,
    mid_lo             = 0.38,
    mid_hi             = 0.70,
    mid_r              = 0.62,
    mid_g              = 0.67,
    mid_b              = 0.76,
    mid_strength       = 0.30,
    branch_sigma       = 1.2,
    branch_percentile  = 78.0,
    branch_sharp       = 0.58,
    branch_sharp_sigma = 0.8,
    horizon_zone       = 0.60,
    horizon_sat_thresh = 0.24,
    horizon_sat_sigma  = 3.5,
    horizon_r          = 0.74,
    horizon_g          = 0.68,
    horizon_b          = 0.44,
    horizon_strength   = 0.34,
    opacity            = 0.90,
)

print("Contre-jour rim light (s282 improvement)...")
p.paint_contre_jour_rim_pass(
    bright_threshold   = 0.68,
    dark_threshold     = 0.40,
    gradient_sigma     = 1.4,
    rim_sigma          = 2.8,
    rim_strength       = 0.48,
    rim_r              = 0.88,
    rim_g              = 0.62,
    rim_b              = 0.22,
    cool_edge_strength = 0.28,
    cool_edge_r        = 0.54,
    cool_edge_g        = 0.64,
    cool_edge_b        = 0.82,
    edge_percentile    = 72.0,
    opacity            = 0.78,
)

print("Shadow temperature (s281 improvement)...")
p.paint_shadow_temperature_pass(
    highlight_percentile  = 88.0,
    shadow_threshold      = 0.32,
    shadow_softness       = 0.16,
    shadow_strength       = 0.25,
    highlight_reinforce   = 0.14,
    highlight_threshold   = 0.74,
    bias_scale            = 3.0,
    cool_shadow_color     = (0.32, 0.36, 0.52),
    warm_shadow_color     = (0.54, 0.42, 0.22),
    cool_highlight_color  = (0.78, 0.86, 0.94),
    warm_highlight_color  = (0.92, 0.84, 0.58),
    opacity               = 0.78,
)

print("Depth atmosphere (aerial perspective)...")
p.paint_depth_atmosphere_pass(
    haze_color      = (0.74, 0.76, 0.82),
    depth_sigma     = 42.0,
    max_haze        = 0.22,
    vertical_weight = 0.60,
    contrast_weight = 0.40,
    contrast_radius = 6.0,
    noise_seed      = 282,
    opacity         = 0.55,
)

print("Lost and found edges...")
p.paint_lost_found_edges_pass(
    found_threshold  = 0.28,
    lost_threshold   = 0.14,
    sharp_sigma      = 0.9,
    sharp_strength   = 0.70,
    lost_sigma       = 2.2,
    lost_strength    = 0.44,
    focal_percentile = 78.0,
    focal_power      = 1.3,
    edge_percentile  = 94.0,
    opacity          = 0.82,
)

# ── Save ──────────────────────────────────────────────────────────────────────
OUT = os.path.join(REPO, "s282_frozen_river_dawn.png")
p.save(OUT)
print(f"Saved: {OUT}")
