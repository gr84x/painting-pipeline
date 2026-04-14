"""
run_cartoon_v1.py — First cartoon character through the painting pipeline.

Demonstrates CartoonMorphology.cartoon() preset:
  - Enlarged cranium (1.35x) for anime big-head proportions
  - Large, deep eye sockets (scale=1.60, depth=1.50)
  - Reduced nose (size=0.45, tip=0.40) — barely visible
  - Fuller lips (fullness=1.30)
  - Gentle jaw taper (0.20) for a slightly pointed chin
  - Slight face flatten (0.25) for a more 2D-feel profile

Lighting: Rembrandt key only (as in v20/v21) — dramatic shadows read
well on cartoon faces because the simplified geometry creates clean
shadow shapes rather than noisy surface detail.

Normal map is automatically rendered by blender_bridge and passed to
the stroke engine, making toon_paint() available for cel-shading passes.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scene_schema import (
    Scene, Character, Camera, LightRig, Environment, Style, Light,
    Pose, PoseDetail, SkinTone, Expression, EnvType, Medium, Period,
    PaletteHint, Vec3
)
from cartoon_morphology import CartoonMorphology
from blender_bridge import scene_to_painting

# Single Rembrandt key — same proven setup as v20/v21.
# Cartoon faces need the same 8:1 key:fill ratio; if anything, higher
# contrast reads better with simplified geometry.
rig = LightRig.rembrandt()
rig.lights[0].intensity = 280

# CartoonMorphology.cartoon() preset:
#   cranium_ratio=1.35, eye_scale=1.60, eye_depth=1.50, brow_ridge=0.70,
#   nose_size=0.45, nose_tip=0.40, lip_fullness=1.30, jaw_taper=0.20,
#   face_flat=0.25
morph = CartoonMorphology.cartoon()

scene = Scene(
    subjects=[Character(
        pose        = Pose.SEATED,
        pose_detail = PoseDetail(head_turn=-22.0, head_nod=5.0),
        skin_tone   = SkinTone.LIGHT,
        expression  = Expression.ENIGMATIC,
        hair_color  = (0.15, 0.06, 0.02),   # slightly darker than v21
        morphology  = morph,
    )],
    camera = Camera(
        # Pull back slightly (Y=-1.4) because the cranium is 35% bigger —
        # we want the full head in frame without losing the face-fill ratio.
        position = Vec3(-0.12, -1.4, 1.0),
        target   = Vec3(0,     0,    1.15),
        fov      = 24,
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
    title  = "cartoon_v1",
)

print("Starting cartoon_v1 pipeline (CartoonMorphology.cartoon(), Rembrandt key, normal-map pass)...")
_out_dir = os.path.join(os.path.dirname(__file__), '..')
out = scene_to_painting(scene, os.path.join(_out_dir, 'cartoon_v1.png'), verbose=True)
print("Done:", out)
