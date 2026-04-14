"""
run_v20.py — Fix: no fill light (was flooding shadow cheek at 2.5:1 ratio vs 8:1 needed).
  - Single Rembrandt key at 280W, upper-left, tracks to face
  - Close camera from v19 (Y=-1.2, FOV=22°, target Z=1.10) so face fills ~45% frame
  - Head turn increased to -22° for a cleaner shadow triangle
  - Ambient kept very low (0.15 strength) — this provides enough lift on shadow side
    without adding a second light that would flatten the Rembrandt effect
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

# Single-light Rembrandt: key only. Ambient (0.006 effective at shadow) provides
# just enough lift to see shadow-side face structure without killing the drama.
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
    title  = "rembrandt_portrait_v1",
)

print("Starting rembrandt_v1 pipeline (single-light Rembrandt, close camera, -22° turn)…")
_out_dir = os.path.join(os.path.dirname(__file__), '..')
out = scene_to_painting(scene, os.path.join(_out_dir, 'rembrandt_portrait_v1.png'), verbose=True)
print("Done:", out)
