"""paint_s280_taos_portrait.py -- Session 280: Nicolai Fechin (191st mode)

Subject & Composition:
    A Taos Pueblo elder woman seated in three-quarter view, her gaze turned
    slightly toward the viewer, commanding and still. She is positioned at
    center-left, her figure filling the upper two-thirds of the canvas. Her
    hands rest in her lap, fingers slightly curled -- strong, work-worn hands.
    The pose is dignified and self-contained.

The Figure:
    An older woman, perhaps 65-70. Deep-set eyes, weathered bronze skin, high
    cheekbones. She wears traditional Taos Pueblo clothing: a dark woven manta
    (dress) with geometric border patterns in red-ochre and black. A turquoise
    and silver necklace rests at her collarbone. Her hair is pulled back simply.
    Her expression: composed dignity, quiet strength, a life fully lived. The
    eyes hold a kind reserve -- watchful, warm, private.

The Environment:
    Interior of an adobe room in warm late-afternoon light. A single high window
    off-frame to the upper left casts a shaft of golden light across the figure.
    The background is loosely suggested: warm umber adobe wall, a hint of a
    blanket or pot at the edge. The floor is bare earth. The space is intimate,
    close -- the figure is almost architectural in the frame.

Technique & Palette:
    Nicolai Fechin's method: tight academic rendering at the face and hands
    (Repin's influence), loose gestural impasto in the background and clothing,
    palette knife scraping in the highlight zones of the face and necklace.
    Palette: burnt sienna ground, raw sienna midtones, warm ochre lights,
    Payne gray-blue in the shadow and background, deep umber darks,
    vermilion accent at the lips.

Mood & Intent:
    Dignity of age. The painting honors the subject with the same attentiveness
    and craft that Fechin brought to his Taos portraits. The viewer should feel
    the weight of time, the quiet power of the figure, the warmth of the adobe
    light -- and the painter's profound respect.

New in s280:
    - fechin_gestural_impasto_pass (191st mode): turbulent velocity field,
      palette knife scraping, focal academic sharpening, earth midtone
    - paint_lost_found_edges_pass (improvement): found/lost edge system,
      sharpening at focal edges, softening at peripheral edges
"""

import os
import sys
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

W, H = 1040, 1440   # portrait

from scene_schema import (
    Scene, Character, Camera, LightRig, Style, Medium, Period,
    PaletteHint, Vec3, Pose, SkinTone, Expression, Environment, EnvType
)
from blender_bridge import scene_to_painting

scene = Scene(
    subjects=[Character(
        pose       = Pose.SEATED,
        skin_tone  = SkinTone.BROWN,
        expression = Expression.STERN,
    )],
    camera    = Camera(
        position = Vec3(-0.08, -1.15, 1.22),
        target   = Vec3(0.0,  0.0,   1.10),
        fov      = 24,
    ),
    lighting  = LightRig.rembrandt(),
    environment = Environment(type=EnvType.INTERIOR),
    style     = Style(
        medium  = Medium.OIL,
        period  = Period.REALIST,
        palette = PaletteHint.WARM_EARTH,
    ),
    width  = W,
    height = H,
    title  = "taos_portrait",
)

print("Rendering Blender reference scene...")
ref_path = scene_to_painting(scene, "s280_taos_portrait_ref.png", verbose=True)
ref = np.array(Image.open(ref_path)).astype(np.uint8)
if ref.shape[2] == 4:
    ref = ref[:, :, :3]
# Ensure correct canvas size
if ref.shape[:2] != (H, W):
    ref_img = Image.fromarray(ref).resize((W, H), Image.LANCZOS)
    ref = np.array(ref_img).astype(np.uint8)
print(f"Reference loaded: {ref.shape}")

# ── Anatomy weight map ────────────────────────────────────────────────────────
from anatomy import subjects as anatomy_subjects, PlacedAnatomy, build_combined_weight_map

placed = [
    PlacedAnatomy(
        anatomy = anatomy_subjects.get("human_portrait"),
        cx      = 510,    # slightly left of center
        cy      = 480,    # upper third of canvas (face)
        rx      = 175,
        ry      = 210,
    )
]
weight_map = build_combined_weight_map(placed, canvas_w=W, canvas_h=H)

# ── Painter setup ─────────────────────────────────────────────────────────────
from stroke_engine import Painter

p = Painter(W, H, seed=280)
if weight_map is not None:
    p._comp_map = weight_map

# Warm burnt-sienna ground (Fechin's preferred academic ground)
p.tone_ground((0.58, 0.42, 0.26), texture_strength=0.025)

# ── Structural passes ─────────────────────────────────────────────────────────
print("Underpainting...")
p.underpainting(ref, stroke_size=52, n_strokes=260)
p.underpainting(ref, stroke_size=44, n_strokes=220)

print("Block-in (broad masses)...")
p.block_in(ref, stroke_size=32, n_strokes=480)
p.block_in(ref, stroke_size=20, n_strokes=500)

print("Build form (modelling)...")
p.build_form(ref, stroke_size=12, n_strokes=540)
p.build_form(ref, stroke_size=6,  n_strokes=420)

print("Lights and accents...")
p.place_lights(ref, stroke_size=4, n_strokes=300)

# ── Artist passes ─────────────────────────────────────────────────────────────
print("Fechin gestural impasto (191st mode)...")
p.fechin_gestural_impasto_pass(
    velocity_freq1   = 0.018,
    velocity_freq2   = 0.011,
    velocity_freq3   = 0.027,
    aniso_long       = 9,
    aniso_short      = 2,
    aniso_strength   = 0.42,
    scrape_threshold = 0.64,
    scrape_width     = 12,
    scrape_strength  = 0.52,
    sharp_sigma      = 1.0,
    sharp_strength   = 0.72,
    focal_power      = 2.2,
    earth_center     = 0.44,
    earth_sigma      = 0.17,
    earth_strength   = 0.30,
    sienna_r         = 0.72,
    sienna_g         = 0.38,
    sienna_b         = 0.12,
    seed             = 280,
    opacity          = 0.90,
)

print("Lost and found edges (s280 improvement)...")
p.paint_lost_found_edges_pass(
    found_threshold  = 0.32,
    lost_threshold   = 0.16,
    sharp_sigma      = 1.1,
    sharp_strength   = 0.82,
    lost_sigma       = 2.2,
    lost_strength    = 0.50,
    focal_percentile = 78.0,
    focal_power      = 1.6,
    edge_percentile  = 95.0,
    opacity          = 0.92,
)

# ── Save ──────────────────────────────────────────────────────────────────────
OUT = os.path.join(REPO, "s280_taos_portrait.png")
p.save(OUT)
print(f"Saved: {OUT}")
