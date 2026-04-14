"""
run_v21.py — Fixes bright-hair / background bleed in paintings:
  - focused_pass now intersects face ellipse with figure mask (no background strokes)
  - place_lights uses lum^4.5 (was 2.2) — only true specular highlights, not hair
  - face_mask tightened to rx*1.0, ry*0.95 (was rx*1.25, ry*1.20)
  - All other settings from v20 (single Rembrandt key, close camera, -22° turn)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scene_schema import (
    Scene, Character, Camera, LightRig, Environment, Style, Light,
    Pose, PoseDetail, SkinTone, Expression, EnvType, Medium, Period,
    PaletteHint, Vec3
)
from blender_bridge import scene_to_painting

rig = LightRig.rembrandt()
rig.lights[0].intensity = 280

scene = Scene(
    subjects=[Character(
        pose        = Pose.SEATED,
        pose_detail = PoseDetail(head_turn=-22.0, head_nod=5.0),
        skin_tone   = SkinTone.LIGHT,
        expression  = Expression.ENIGMATIC,
        hair_color  = (0.18, 0.08, 0.02),
    )],
    camera = Camera(
        position = Vec3(-0.12, -1.2, 1.0),
        target   = Vec3(0,     0,    1.10),
        fov      = 22,
    ),
    lighting = rig,
    environment = Environment(
        type         = EnvType.INTERIOR,
        ground_color = (0.04, 0.03, 0.02),
    ),
    style = Style(
        medium  = Medium.OIL,
        period  = Period.RENAISSANCE,
        palette = PaletteHint.WARM_EARTH,
    ),
    width  = 780,
    height = 1080,
    title  = "mona_lisa_v21",
)

print("Starting v21 pipeline (focused_pass x figure_mask, tight face ellipse, selective highlights)...")
_out_dir = os.path.join(os.path.dirname(__file__), '..')
out = scene_to_painting(scene, os.path.join(_out_dir, 'mona_lisa_v21.png'), verbose=True)
print("Done:", out)
