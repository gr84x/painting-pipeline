"""
run_pointillist_v1.py — Seurat-inspired divisionist portrait.

Technique
---------
Instead of continuous brush strokes this script uses pointillist_pass()
which places thousands of tiny pure-colour dots.  Each dot has a companion
complementary dot offset by ~2.5 dot-radii, implementing Seurat's
simultaneous-contrast principle: the viewer's eye optically mixes the dots
at a distance, producing luminosity that physical pigment mixing cannot match.

Style reference
---------------
  Georges Seurat — A Sunday on La Grande Jatte (1884–86)
  Palette:  warm yellows/oranges in sunlit zones;
            cerulean blue / violet in shadows
  Inspired by: Hilma af Klint's use of bold colour contrast zones
  (warm amber against deep blue, spirit and cosmos)

Pipeline
--------
  1. Tone the canvas pale (cream — canvas shows between dots)
  2. Light underpainting to establish value structure
  3. pointillist_pass() — primary + complementary dots (the key innovation)
  4. Second pointillist_pass() at slightly larger dot size for variety
  5. Soft vignette — no crackle (Seurat painted on fresh canvas)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scene_schema import (
    Scene, Character, Camera, LightRig, Environment, Style, Light,
    Pose, PoseDetail, SkinTone, Expression, EnvType, Medium, Period,
    PaletteHint, Vec3,
)
from blender_bridge import scene_to_painting

# ── Scene description ─────────────────────────────────────────────────────────
# Seurat painted figures in dappled outdoor sunlight — overcast or hazy light
# gives the soft, diffuse illumination his palette thrives in.

rig = LightRig.overcast()

scene = Scene(
    subjects=[Character(
        pose        = Pose.STANDING,
        pose_detail = PoseDetail(head_turn=-15.0, head_nod=3.0),
        skin_tone   = SkinTone.MEDIUM,
        expression  = Expression.PENSIVE,
        hair_color  = (0.15, 0.10, 0.05),
    )],
    camera = Camera(
        position = Vec3(-0.08, -1.4, 1.05),
        target   = Vec3(0,      0,   1.10),
        fov      = 28,
    ),
    lighting    = rig,
    environment = Environment(
        type         = EnvType.EXTERIOR,
        description  = "sunny park by a river, dappled light through trees",
        atmosphere   = 0.10,
        ground_color = (0.55, 0.62, 0.40),   # sunlit grass
    ),
    style = Style(
        medium  = Medium.OIL,
        period  = Period.POINTILLIST,
        palette = PaletteHint.JEWEL,
        # Override defaults for pointillist technique:
        #   very small strokes, minimal wet-blending, crisp dot edges
        stroke_size_face = 4,
        stroke_size_bg   = 5,
        wet_blend        = 0.02,
        edge_softness    = 0.10,
    ),
    width  = 780,
    height = 1080,
    title  = "pointillist_v1",
)

print("Starting pointillist_v1 pipeline (Seurat divisionism + Hilma af Klint colour zones)...")

_out_dir = os.path.join(os.path.dirname(__file__), '..')
out = scene_to_painting(scene, os.path.join(_out_dir, 'pointillist_v1.png'), verbose=True)
print("Done:", out)
