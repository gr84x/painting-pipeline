"""paint_s280_discord_flamenca.py -- Final Discord image for Session 280

Subject & Composition:
    A Spanish flamenco dancer at the peak of a rapid vuelta (turn), viewed from
    low three-quarter angle looking slightly upward. She fills the canvas from
    knee-height to the upper edge, spinning clockwise so we see primarily her
    left side and the beginning of her face turning back toward us in profile.
    Arms in arabesque: left arm curved above her head reaching toward the upper
    right, right arm sweeping out below at mid-height, gathering the dress hem
    slightly. Her crimson dress billows in a wide arc behind her -- a comet-tail
    of spinning silk frozen at the moment of maximum extension.

The Figure:
    A woman in her early 50s: powerful, precise, absolute. Dark auburn hair in a
    tight bun with wisps escaping at the temples. Brown skin glistening with the
    heat of exertion. Her spine is straight as a column; her bearing is
    architectural. Fitted black silk bodice with red embroidery at the collar.
    The deep crimson skirt with black ruffle has become a full revolving plane
    of fabric. Her left hand is open, fingers extended and slightly curved in the
    classic flamenco mano. Expression: contained, fierce, inward -- the audience
    does not exist for her. She has disappeared entirely into the music.

The Environment:
    A small stone-vaulted tablao in Seville. The ceiling is a dark barrel vault of
    rough whitewashed brick, lit from below by thick beeswax candles in iron holders
    mounted to the side walls. The walls are warm amber-plaster in the candle zones,
    cooling to shadow-gray at the vault. The floor: deep-worn chestnut floorboards
    reflecting faint candle-gold. In the far background center (very dark): the
    barely discernible silhouette of a seated guitarist, his head bowed over the
    instrument. Foreground: the dancer's shadow sprawls dramatically across the
    warm boards, longer than she is tall.

Technique & Palette:
    Nicolai Fechin's method (191st mode): the face, hands, and bodice rendered with
    Repin-academic precision; the spinning dress in loose slashing strokes at varied
    angles; the stone vault and background dissolve into atmospheric mist. Palette
    knife scraping on the brightest crimson folds -- horizontal bright streaks where
    the knife passes expose the warm ground. Lost edges at the spinning dress
    periphery; found edges at the face and the foreground floor boards.
    Palette: deep crimson, near-black, warm amber-gold, burnt sienna, Payne gray-blue.

Mood & Intent:
    Contained passion. The paradox at the heart of flamenco: absolute emotional
    intensity controlled and expressed through absolute technical precision. The
    painting should communicate heat, weight, sound, privacy. The viewer should feel
    the candle-heat, hear the heels on wood, and understand that they are witnessing
    something not meant to be witnessed -- a private communion between a human being
    and their art.
"""

import os
import sys
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

W, H = 1040, 1440

from scene_schema import (
    Scene, Character, Camera, LightRig, Style, Medium, Period,
    PaletteHint, Vec3, Pose, SkinTone, Expression, Environment, EnvType
)
from blender_bridge import scene_to_painting

# Single standing dancer figure, lit from below-left (candle position)
scene = Scene(
    subjects=[Character(
        pose       = Pose.STANDING,
        skin_tone  = SkinTone.BROWN,
        expression = Expression.STERN,
    )],
    camera    = Camera(
        position = Vec3(0.15, -1.20, 0.95),
        target   = Vec3(0.0,  0.0,   1.15),
        fov      = 26,
    ),
    lighting  = LightRig.rembrandt(),
    environment = Environment(type=EnvType.INTERIOR),
    style     = Style(
        medium  = Medium.OIL,
        period  = Period.SPANISH_BAROQUE,
        palette = PaletteHint.WARM_EARTH,
    ),
    width  = W,
    height = H,
    title  = "flamenca_taos",
)

print("Rendering Blender reference for flamenca...")
ref_path = scene_to_painting(scene, "s280_discord_flamenca_ref.png", verbose=True)
ref = np.array(Image.open(ref_path)).astype(np.uint8)
if ref.shape[2] == 4:
    ref = ref[:, :, :3]
if ref.shape[:2] != (H, W):
    ref_img = Image.fromarray(ref).resize((W, H), Image.LANCZOS)
    ref = np.array(ref_img).astype(np.uint8)
print(f"Reference loaded: {ref.shape}")

from anatomy import subjects as anatomy_subjects, PlacedAnatomy, build_combined_weight_map

# Full body standing figure -- face in upper portion
placed = [
    PlacedAnatomy(
        anatomy = anatomy_subjects.get("human_portrait"),
        cx      = 490,   # slightly left of center
        cy      = 350,   # upper quarter (face zone)
        rx      = 160,
        ry      = 190,
    )
]
weight_map = build_combined_weight_map(placed, canvas_w=W, canvas_h=H)

from stroke_engine import Painter

p = Painter(W, H, seed=280)
if weight_map is not None:
    p._comp_map = weight_map

# Deep warm umber ground -- the tablao floor and walls
p.tone_ground((0.45, 0.22, 0.08), texture_strength=0.030)

print("Underpainting...")
p.underpainting(ref, stroke_size=54, n_strokes=260)
p.underpainting(ref, stroke_size=46, n_strokes=240)

print("Block-in...")
p.block_in(ref, stroke_size=34, n_strokes=500)
p.block_in(ref, stroke_size=22, n_strokes=520)

print("Build form...")
p.build_form(ref, stroke_size=13, n_strokes=560)
p.build_form(ref, stroke_size=6,  n_strokes=440)

print("Lights...")
p.place_lights(ref, stroke_size=4, n_strokes=320)

print("Fechin gestural impasto (191st mode)...")
p.fechin_gestural_impasto_pass(
    velocity_freq1   = 0.016,
    velocity_freq2   = 0.012,
    velocity_freq3   = 0.030,
    aniso_long       = 10,
    aniso_short      = 2,
    aniso_strength   = 0.45,
    scrape_threshold = 0.60,
    scrape_width     = 14,
    scrape_strength  = 0.58,
    sharp_sigma      = 0.9,
    sharp_strength   = 0.78,
    focal_power      = 2.2,
    earth_center     = 0.42,
    earth_sigma      = 0.18,
    earth_strength   = 0.32,
    sienna_r         = 0.72,
    sienna_g         = 0.38,
    sienna_b         = 0.12,
    seed             = 2801,
    opacity          = 0.92,
)

print("Lost and found edges (s280 improvement)...")
p.paint_lost_found_edges_pass(
    found_threshold  = 0.30,
    lost_threshold   = 0.15,
    sharp_sigma      = 1.0,
    sharp_strength   = 0.88,
    lost_sigma       = 2.4,
    lost_strength    = 0.52,
    focal_percentile = 76.0,
    focal_power      = 1.8,
    edge_percentile  = 95.0,
    opacity          = 0.90,
)

print("Surface grain (s279 improvement)...")
p.paint_surface_grain_pass(
    grain_strength     = 0.055,
    coverage_radius    = 4,
    coverage_boost     = 2.8,
    linen_r            = 0.72,
    linen_g            = 0.55,
    linen_b            = 0.32,
    grain_sigma_fine   = 0.8,
    grain_sigma_coarse = 2.0,
    seed               = 2802,
    opacity            = 0.85,
)

OUT = os.path.join(REPO, "s280_discord_flamenca.png")
p.save(OUT)
print(f"Saved: {OUT}")
