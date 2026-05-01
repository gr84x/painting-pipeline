"""paint_s281_pine_forest.py -- Session 281: Ivan Shishkin (192nd mode)

Subject & Composition:
    A dense Russian pine forest interior, late afternoon in early autumn.
    The viewer stands inside a cathedral of towering pine trunks, looking
    slightly upward toward a clearing where a shaft of warm golden light
    descends between two massive foreground trees. The composition is
    symmetrical but not rigid: the two dominant trunks frame the central
    light shaft, with a receding colonnade of smaller trunks behind them.
    The eye travels from the warm-lit foreground floor, up through the
    dark mid-zone of the trunks, into the golden light shaft, and then
    to the bright canopy beyond.

The Forest:
    Mature Scots pines (Pinus sylvestris), each 30-40 meters tall,
    with thick plated amber-brown bark on the sun-facing side and
    cool gray-green lichen on the shadow side. The two foreground
    trunks are massive -- nearly a meter in diameter -- and their bark
    is rendered in detail: vertical ridges, horizontal shadow bands,
    warm ochre highlights, cool gray recesses. Behind them, five or
    six additional trunks recede into the forest haze, becoming
    progressively cooler, grayer, and less distinct. The canopy is
    dense and dark above, with a bright warm opening at the top center
    where the light shaft originates. The forest floor is covered in
    dry pine needles and sand: warm ochre-brown with dappled shadow
    patterns. A small patch of scrubby undergrowth fills the
    lower-right corner.

The Environment:
    Deep Vyatka Province forest, late September, 4 PM. The light is
    golden and low-angled, creating long warm shadows and brilliant
    amber highlights on the right-facing bark surfaces. The air carries
    a cool, resinous moisture; the distant trunks dissolve into a
    blue-green atmospheric haze. The forest floor is dry and slightly
    sandy underfoot. No human presence. The scale of the trees makes
    the space feel vast and ancient. The light shaft is the compositional
    fulcrum -- everything else is organized around its diagonal warmth.

Technique & Palette:
    Ivan Shishkin's method: meticulous bark texture on foreground trunks,
    dappled canopy light mosaic in the upper zone, warm ochre on the
    forest floor, and cool blue-green atmospheric recession in the
    background. Palette: deep forest shadow green, sunlit mid-canopy
    green, warm amber bark, dark umber bark shadow, golden afternoon
    light, raw umber forest floor, cool haze blue-gray, sandy warm path.

Mood & Intent:
    The grandeur and solitude of the Russian forest. The painting should
    convey the specific physical sensation of standing inside a mature
    pine forest -- the scale, the filtered light, the resinous scent
    made visible through color. The viewer should feel the age and
    weight of the trees, the quiet authority of the natural world.
    Shishkin wanted viewers to know the forest as well as he did --
    not as decoration, but as a specific, material, living reality.

New in s281:
    - shishkin_forest_density_pass (192nd mode): vertical bark anisotropy,
      local variance dappling, shadow floor warmth, desaturation haze
    - paint_shadow_temperature_pass (improvement): highlight temperature
      sampling, opposing shadow chromatic push, dual-zone temperature dialogue
"""

import os
import sys
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

W, H = 1440, 1040   # landscape -- wide forest panorama

# ── Procedural reference image (landscape, no figures) ───────────────────────

def build_reference(width: int, height: int, seed: int = 281) -> np.ndarray:
    """Build a pine forest interior reference image."""
    rng = np.random.default_rng(seed)

    img = np.zeros((height, width, 3), dtype=np.float32)

    # Normalized coordinate grids
    Yn, Xn = np.mgrid[0:height, 0:width].astype(np.float32)
    Yn = Yn / (height - 1)
    Xn = Xn / (width  - 1)

    # ── Base atmosphere ──────────────────────────────────────────────────────
    # Canopy/sky at top (warm golden): top 18%
    sky_color   = np.array([0.80, 0.70, 0.40], dtype=np.float32)
    # Deep forest shadow middle zone
    forest_color = np.array([0.20, 0.25, 0.14], dtype=np.float32)
    # Forest floor (warm ochre): bottom 22%
    floor_color  = np.array([0.54, 0.38, 0.18], dtype=np.float32)

    sky_w   = np.clip(1.0 - Yn / 0.18, 0.0, 1.0) ** 1.8
    floor_w = np.clip((Yn - 0.78) / 0.22, 0.0, 1.0) ** 1.5
    forest_w = np.clip(1.0 - sky_w - floor_w, 0.0, 1.0)

    for c in range(3):
        img[:, :, c] = (sky_color[c]    * sky_w   +
                        forest_color[c] * forest_w +
                        floor_color[c]  * floor_w)

    # ── Tree trunks ──────────────────────────────────────────────────────────
    # (x_norm, half_width_norm, depth_scale)
    # depth_scale: 1.0 = foreground, 0.5 = background
    trunks = [
        (0.03,  0.022, 0.60),   # far left edge
        (0.14,  0.040, 0.90),   # large left foreground
        (0.26,  0.028, 0.65),   # mid-left
        (0.38,  0.050, 1.00),   # massive left-center foreground
        (0.56,  0.048, 1.00),   # massive right-center foreground
        (0.68,  0.030, 0.70),   # mid-right
        (0.80,  0.038, 0.80),   # right foreground
        (0.92,  0.024, 0.55),   # far right background
        (0.46,  0.018, 0.50),   # thin center background
    ]

    for tx, tw, depth in trunks:
        # Soft trunk mask: Gaussian profile
        dist = np.abs(Xn - tx) / (tw + 1e-6)
        trunk_mask = np.clip(1.0 - dist, 0.0, 1.0) ** 2   # (H, W)

        # Bark value varies: lit on right side (light from upper right)
        # Light comes from upper-right at ~60% across canvas
        light_x = 0.60
        dx_to_light = light_x - tx
        # Right-facing surfaces lit, left-facing in shadow
        side_factor = np.clip(0.5 + (Xn - tx) / (tw * 2.5), 0.0, 1.0)

        bark_dark   = np.array([0.20, 0.15, 0.09], dtype=np.float32) * depth
        bark_bright = np.array([0.55, 0.40, 0.22], dtype=np.float32) * depth

        # Slightly warmer toward top (sky light), darker in dense middle
        sky_reflect = np.clip(1.0 - Yn / 0.25, 0.0, 1.0) * 0.12
        floor_reflect = np.clip((Yn - 0.80) / 0.20, 0.0, 1.0) * 0.10

        for c in range(3):
            bark_col = (bark_dark[c] * (1 - side_factor) +
                        bark_bright[c] * side_factor)
            bark_col = bark_col + sky_reflect * 0.08
            bark_col = bark_col + floor_reflect * 0.05
            img[:, :, c] = (img[:, :, c] * (1.0 - trunk_mask * 0.80) +
                            bark_col       * trunk_mask * 0.80)

    # ── Central light shaft ──────────────────────────────────────────────────
    # Diagonal shaft from upper-right, angled down-left
    # Center x shifts: at top it's at ~0.62, at bottom it's ~0.50
    shaft_cx = 0.62 - (Yn - 0.0) * 0.18
    shaft_w  = 0.065
    shaft_dist = np.abs(Xn - shaft_cx) / shaft_w
    shaft_mask = np.clip(1.0 - shaft_dist, 0.0, 1.0) ** 2
    shaft_fade = np.clip(1.0 - Yn / 0.65, 0.0, 1.0) * np.clip(1.0 - Yn / 0.10, 0.0, 1.0) ** 0
    shaft_fade = np.clip(1.0 - Yn / 0.65, 0.0, 1.0)
    shaft_color = np.array([0.92, 0.84, 0.58], dtype=np.float32)
    shaft_strength = shaft_mask * shaft_fade * 0.40

    for c in range(3):
        img[:, :, c] = np.clip(img[:, :, c] + shaft_color[c] * shaft_strength,
                               0.0, 1.0)

    # ── Dappled light patches on forest floor ────────────────────────────────
    floor_zone = np.clip((Yn - 0.72) / 0.28, 0.0, 1.0)  # only in bottom zone
    n_patches = 12
    patch_xs  = rng.uniform(0.10, 0.90, n_patches).astype(np.float32)
    patch_ys  = rng.uniform(0.75, 0.95, n_patches).astype(np.float32)
    patch_rs  = rng.uniform(0.03, 0.08, n_patches).astype(np.float32)
    patch_color = np.array([0.80, 0.68, 0.42], dtype=np.float32)
    for i in range(n_patches):
        pd = np.sqrt((Xn - patch_xs[i])**2 + (Yn - patch_ys[i])**2)
        pm = np.clip(1.0 - pd / patch_rs[i], 0.0, 1.0) ** 2
        pm = pm * floor_zone * 0.35
        for c in range(3):
            img[:, :, c] = np.clip(img[:, :, c] + patch_color[c] * pm, 0.0, 1.0)

    # ── Subtle noise for texture ─────────────────────────────────────────────
    noise = rng.uniform(-0.03, 0.03, (height, width, 3)).astype(np.float32)
    img = np.clip(img + noise, 0.0, 1.0)

    return (img * 255).astype(np.uint8)


print("Building procedural pine forest reference...")
ref = build_reference(W, H, seed=281)
if ref.shape[2] == 4:
    ref = ref[:, :, :3]
print(f"Reference built: {ref.shape}")

# ── Painter setup ─────────────────────────────────────────────────────────────
from stroke_engine import Painter

p = Painter(W, H, seed=281)

# Warm forest-earth ground
p.tone_ground((0.42, 0.32, 0.18), texture_strength=0.020)

# ── Structural passes ─────────────────────────────────────────────────────────
print("Underpainting...")
p.underpainting(ref, stroke_size=54, n_strokes=260)
p.underpainting(ref, stroke_size=46, n_strokes=240)

print("Block-in (broad masses)...")
p.block_in(ref, stroke_size=34, n_strokes=480)
p.block_in(ref, stroke_size=22, n_strokes=510)

print("Build form (modelling)...")
p.build_form(ref, stroke_size=13, n_strokes=540)
p.build_form(ref, stroke_size=7,  n_strokes=460)

print("Lights and accents...")
p.place_lights(ref, stroke_size=4, n_strokes=300)

# ── Artist passes ─────────────────────────────────────────────────────────────
print("Shishkin forest density (192nd mode)...")
p.shishkin_forest_density_pass(
    bark_vlong       = 22,
    bark_vshort      = 2,
    bark_strength    = 0.38,
    dapple_sigma     = 4.5,
    dapple_threshold = 0.011,
    dapple_r         = 0.65,
    dapple_g         = 0.72,
    dapple_b         = 0.36,
    dapple_strength  = 0.30,
    floor_threshold  = 0.33,
    floor_softness   = 0.14,
    floor_r          = 0.52,
    floor_g          = 0.34,
    floor_b          = 0.14,
    floor_strength   = 0.32,
    haze_threshold   = 0.22,
    haze_sigma       = 2.5,
    haze_r           = 0.50,
    haze_g           = 0.58,
    haze_b           = 0.66,
    haze_strength    = 0.34,
    opacity          = 0.88,
)

print("Shadow temperature (s281 improvement)...")
p.paint_shadow_temperature_pass(
    highlight_percentile  = 86.0,
    shadow_threshold      = 0.34,
    shadow_softness       = 0.14,
    shadow_strength       = 0.30,
    highlight_reinforce   = 0.18,
    highlight_threshold   = 0.72,
    bias_scale            = 3.5,
    cool_shadow_color     = (0.28, 0.30, 0.50),
    warm_shadow_color     = (0.58, 0.40, 0.20),
    cool_highlight_color  = (0.72, 0.84, 0.92),
    warm_highlight_color  = (0.92, 0.82, 0.55),
    opacity               = 0.82,
)

print("Depth atmosphere (aerial perspective)...")
p.paint_depth_atmosphere_pass(
    haze_color      = (0.50, 0.58, 0.68),
    depth_sigma     = 38.0,
    max_haze        = 0.28,
    vertical_weight = 0.55,
    contrast_weight = 0.45,
    contrast_radius = 7.0,
    noise_seed      = 281,
    opacity         = 0.65,
)

print("Lost and found edges...")
p.paint_lost_found_edges_pass(
    found_threshold  = 0.30,
    lost_threshold   = 0.15,
    sharp_sigma      = 1.0,
    sharp_strength   = 0.75,
    lost_sigma       = 2.0,
    lost_strength    = 0.48,
    focal_percentile = 80.0,
    focal_power      = 1.4,
    edge_percentile  = 95.0,
    opacity          = 0.85,
)

# ── Save ──────────────────────────────────────────────────────────────────────
OUT = os.path.join(REPO, "s281_pine_forest.png")
p.save(OUT)
print(f"Saved: {OUT}")
