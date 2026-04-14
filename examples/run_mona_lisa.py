"""
run_mona_lisa.py — Full sfumato portrait in the style of Leonardo da Vinci.

Prompt summary
--------------
Half-length portrait of a woman, positioned slightly right of centre.
Three-quarter pose (body 45° right, head nearly full-face).
Hands folded in lap, lower-centre.

The face
  - Oval face, high smooth forehead, barely perceptible eyebrows
  - Dark heavy-lidded eyes gazing directly at viewer, calm awareness
  - Closed lips with corners turned very slightly upward — ambiguous,
    neither smile nor neutral: the essential quality
  - Skin: seamless ivory technique, warm light from upper left, no
    visible brushwork

Hair
  - Dark brown, centre part, soft waves, partially covered by a dark
    semi-transparent veil draped over the crown

Clothing
  - Dark forest-green / blue-black dress, thin amber trim at neckline
  - Semi-transparent gauze wrap over shoulder and chest

Background
  - Dreamlike geological wilderness — not realistic
  - Winding path / road snaking into distance on the left
  - Rocky craggy terrain, sparse vegetation
  - River or body of water suggested in middle distance
  - Left horizon sits subtly higher than right (uncanny quality)
  - Dissolves to cool atmospheric haze — sfumato recession

Technique
  - Sfumato throughout — no hard outlines, forms melt into each other
  - Palette: warm ochres / raw umbers / ivory / soft flesh for figure;
    cool grey-blues / muted greens / dusty lavenders for background
  - Foreground warm and low-key; cooling and lightening with depth
  - Glazing logic — thin transparent layers building luminous depth
  - Upper-left diffused light source, gentle transitions

Mood
  - Still, interior, quietly enigmatic
  - Inner life inaccessible — composed without joy or sorrow
  - Ancient, unpeopled landscape; subject outside ordinary time
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scene_schema import (
    Scene, Character, Camera, LightRig, Environment, Style, Light,
    Pose, PoseDetail, SkinTone, Expression, EnvType, Medium, Period,
    PaletteHint, HairStyle, Sex, AgeRange, Build, Vec3, Costume,
)
from blender_bridge import scene_to_painting

# ── Lighting ──────────────────────────────────────────────────────────────────
# Upper-left diffused key from Leonardo's convention.
# No fill — the shadow side falls into warm umber.
# Gentle ambient from a cool northern sky.
rig = LightRig(
    lights=[
        Light(
            position  = Vec3(-2.2, -1.0, 3.2),   # upper-left, close
            color     = (1.0, 0.96, 0.88),         # warm ivory — northern window
            intensity = 200,
            kind      = "AREA",
        ),
        Light(
            position  = Vec3(2.0, -0.5, 1.8),     # very gentle fill, right side
            color     = (0.70, 0.78, 0.92),         # cool blue-grey fill
            intensity = 18,
            kind      = "AREA",
        ),
    ],
    ambient_color    = (0.08, 0.07, 0.06),
    ambient_strength = 0.22,
)

# ── Subject ───────────────────────────────────────────────────────────────────
subject = Character(
    sex        = Sex.FEMALE,
    age        = AgeRange.YOUNG,
    build      = Build.AVERAGE,
    skin_tone  = SkinTone.LIGHT,
    hair_style = HairStyle.VEILED,
    hair_color = (0.15, 0.09, 0.04),      # very dark warm brown

    pose       = Pose.SEATED,
    pose_detail= PoseDetail(
        head_turn = -10.0,    # body 45° right, head nearly faces viewer
        head_nod  =  4.0,     # slight downward inclination — contemplative
        head_tilt =  2.0,     # minimal rightward tilt — relaxed composure
    ),
    expression = Expression.ENIGMATIC,    # the essential quality: ambiguous

    costume = Costume(
        top       = "dark forest-green dress with thin amber neckline trim",
        headwear  = "dark semi-transparent veil draped over crown of head",
        accessory = "semi-transparent gauze wrap over shoulder and chest",
        palette   = PaletteHint.DARK_EARTH,
        fabric_sim= True,
    ),

    # Positioned slightly right of centre
    position = Vec3(0.08, 0.0, 0.0),
    scale    = 1.0,
)

# ── Camera — half-length portrait framing ─────────────────────────────────────
# Slightly elevated, pulled back enough for hands to appear in lower frame.
camera = Camera(
    position = Vec3(-0.10, -1.35, 1.05),   # slightly left of centre, mid-height
    target   = Vec3( 0.04,  0.0,  1.18),   # look at face / upper chest zone
    fov      = 28,                          # portrait lens — reduces distortion
    dof_enabled    = False,                 # Leonardo had no shallow DOF; we don't either
)

# ── Environment — dreamlike geological wilderness ─────────────────────────────
# Cool atmospheric haze; left horizon subtly higher than right.
# The description is left and right sides of figure, receding into sfumato.
environment = Environment(
    type        = EnvType.EXTERIOR,
    description = (
        "Imaginary geological wilderness: winding road snaking into left-side "
        "distance; rocky craggy formations; sparse vegetation; river or water "
        "body in middle distance; left horizon sits slightly higher than right "
        "(uncanny, subtly disorienting quality); distant forms dissolve to cool "
        "blue-grey atmospheric haze; no people, no buildings — ancient and unpeopled"
    ),
    atmosphere   = 0.38,                   # significant sfumato haze in distance
    ground_color = (0.35, 0.38, 0.28),     # cool muted green-grey landscape floor
)

# ── Style — Leonardo High Renaissance with full sfumato ──────────────────────
# edge_softness ≥ 0.80 activates sfumato_veil_pass() in the standard pipeline.
# wet_blend 0.92 — Leonardo's technique has almost no visible brushwork.
style = Style(
    medium        = Medium.OIL,
    period        = Period.RENAISSANCE,
    palette       = PaletteHint.WARM_EARTH,
    edge_softness = 0.92,      # maximum sfumato — forms dissolve into smoke
    wet_blend     = 0.90,      # near-maximum: no brushwork visible on skin
    stroke_size_face = 5,      # very small strokes — microscopic sfumato touches
    stroke_size_bg   = 28,     # moderate background strokes for landscape
)

# ── Assemble scene ────────────────────────────────────────────────────────────
scene = Scene(
    subjects    = [subject],
    camera      = camera,
    lighting    = rig,
    environment = environment,
    style       = style,
    width       = 780,
    height      = 1080,
    title       = "mona_lisa_sfumato",
)

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    _out_dir = os.path.join(os.path.dirname(__file__), '..')
    out_path = os.path.join(_out_dir, "mona_lisa_sfumato.png")
    print("Starting Mona Lisa sfumato portrait pipeline…")
    print("  Subject  : Woman, enigmatic, veiled, three-quarter pose")
    print("  Style    : Period.RENAISSANCE, edge_softness=0.92, wet_blend=0.90")
    print("  Passes   : sfumato_veil_pass (9 veils, warm amber, edge-only)")
    print("  Output   :", out_path)
    print()
    result = scene_to_painting(scene, out_path, verbose=True)
    print()
    print("Done:", result)
