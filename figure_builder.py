"""
figure_builder.py — Human figure construction for Blender.

Generates Blender Python code (as a string) that builds a poseable human
figure using metaballs. Runs inside Blender's Python environment via
blender_bridge.py.

Design
------
  - 7.5-head realistic proportions (1.75 m standing)
  - segment() places metaball elements at even intervals along each limb
    so adjacent blobs always overlap and merge into a smooth surface
  - Separate hair metaball object with its own material
  - Principled BSDF skin with subsurface scatter

Coordinate system: Blender Z-up, Y-back. Origin = foot contact centre.
"""

from __future__ import annotations
import math
from typing import List, Tuple

from head_builder    import build_head_code
from costume_builder import build_costume_code

# ─────────────────────────────────────────────────────────────────────────────
# Canonical proportions  (metres, 1.75 m figure)
# ─────────────────────────────────────────────────────────────────────────────

H = 0.233   # one head unit

# Segment radii — governs thickness at that body region
R = {
    "head":      0.118,
    "jaw":       0.082,
    "neck":      0.038,
    "shoulder":  0.058,
    "chest":     0.130,
    "waist":     0.105,
    "pelvis":    0.118,
    "upper_arm": 0.044,
    "forearm":   0.036,
    "hand":      0.042,
    "thigh":     0.068,
    "shin":      0.048,
    "ankle":     0.032,
    "foot":      0.044,
}

# Spacing multiplier: elements placed every radius * SPACING along each segment
SPACING = 0.75   # tighter packing ensures small-radius limbs merge cleanly


# ─────────────────────────────────────────────────────────────────────────────
# Geometry helpers
# ─────────────────────────────────────────────────────────────────────────────

def _dist(a, b):
    return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))

def _lerp3(a, b, t):
    return tuple(a[i] + (b[i]-a[i])*t for i in range(3))

def _rotate(pt, pivot, deg, axis="z"):
    a = math.radians(deg)
    dx, dy, dz = pt[0]-pivot[0], pt[1]-pivot[1], pt[2]-pivot[2]
    if axis == "x":
        ny = dy*math.cos(a) - dz*math.sin(a)
        nz = dy*math.sin(a) + dz*math.cos(a)
        return (pivot[0]+dx, pivot[1]+ny, pivot[2]+nz)
    elif axis == "y":
        nx =  dx*math.cos(a) + dz*math.sin(a)
        nz = -dx*math.sin(a) + dz*math.cos(a)
        return (pivot[0]+nx, pivot[1]+dy, pivot[2]+nz)
    else:
        nx = dx*math.cos(a) - dy*math.sin(a)
        ny = dx*math.sin(a) + dy*math.cos(a)
        return (pivot[0]+nx, pivot[1]+ny, pivot[2]+dz)


# ─────────────────────────────────────────────────────────────────────────────
# Element accumulator
# ─────────────────────────────────────────────────────────────────────────────

class MballBuilder:
    """Accumulates metaball element specs: (x, y, z, radius, stiffness)."""

    def __init__(self):
        self.elements: List[Tuple] = []

    def point(self, pos, radius, stiffness=2.2):
        self.elements.append((*pos, radius, stiffness))

    def segment(self, a, b, radius, taper=False, stiffness=1.8):
        """
        Fill segment A→B with overlapping blobs.
        taper=True tapers radius toward B (for forearm, shin etc.).
        Spacing = radius * SPACING ensures adjacent blobs merge.
        """
        length = _dist(a, b)
        if length < 1e-6:
            self.point(a, radius, stiffness)
            return
        n = max(2, int(math.ceil(length / (radius * SPACING))))
        for i in range(n + 1):
            t = i / n
            pos = _lerp3(a, b, t)
            r = radius * (1.0 - 0.25*t) if taper else radius
            self.elements.append((*pos, r, stiffness))

    def to_code(self, obj_name: str, mat_name: str,
                resolution: float = 0.022) -> str:
        elems_repr = ",\n    ".join(
            f"({x:.4f},{y:.4f},{z:.4f},{r:.4f},{s:.1f})"
            for x, y, z, r, s in self.elements
        )
        return f"""
_mball_{obj_name} = bpy.data.metaballs.new('{obj_name}Mball')
_mball_{obj_name}.resolution        = {resolution}
_mball_{obj_name}.render_resolution = {resolution * 0.75:.4f}
_mball_{obj_name}.threshold         = 0.40
_mobj_{obj_name} = bpy.data.objects.new('{obj_name}', _mball_{obj_name})
bpy.context.collection.objects.link(_mobj_{obj_name})
_mobj_{obj_name}.data.materials.append({mat_name})
for _ex,_ey,_ez,_er,_es in [
    {elems_repr}
]:
    _el = _mball_{obj_name}.elements.new()
    _el.co = (_ex, _ey, _ez)
    _el.radius = _er
    _el.stiffness = _es
"""


# ─────────────────────────────────────────────────────────────────────────────
# Landmark computation
# ─────────────────────────────────────────────────────────────────────────────

def _standing_landmarks():
    """Return joint positions for a neutral standing figure."""
    sx = 0.205   # half-shoulder width
    hx = 0.108   # half-hip width
    kx = 0.103
    ax = 0.085

    lm = {
        # Spine
        "floor":      (0, 0, 0.000),
        "ankle_l":    (-ax, 0, 0.082), "ankle_r":    (ax, 0, 0.082),
        "knee_l":     (-kx, 0, 0.470), "knee_r":     (kx, 0, 0.470),
        "hip_l":      (-hx, 0, 0.870), "hip_r":      (hx, 0, 0.870),
        "pelvis":     (0, 0, 0.870),
        "navel":      (0, 0, 1.030),
        "chest":      (0, 0, 1.270),
        "neck_base":  (0, 0, 1.490),
        "chin":       (0, 0, 1.515),
        "head_ctr":   (0, 0, 1.625),
        "head_top":   (0, 0, 1.750),
        # Shoulders
        "sh_l":  (-sx, 0.025, 1.440), "sh_r":  (sx, 0.025, 1.440),
        # Left arm (hanging relaxed)
        "elbow_l": (-sx - 0.02, 0.020, 1.160),
        "wrist_l": (-sx + 0.02, 0.010, 0.895),
        "hand_l":  (-sx + 0.03, 0.005, 0.830),
        # Right arm
        "elbow_r": (sx + 0.02, 0.020, 1.160),
        "wrist_r": (sx - 0.02, 0.010, 0.895),
        "hand_r":  (sx - 0.03, 0.005, 0.830),
        # Feet
        "foot_l": (-ax, -0.100, 0.038),
        "foot_r": ( ax, -0.100, 0.038),
    }
    return lm


def compute_landmarks(pose_name: str, pose_detail) -> dict:
    lm = _standing_landmarks()

    if pose_name == "SEATED":
        seat_h    = 0.46
        thigh_len = 0.38   # horizontal thigh length (forward)
        shin_len  = 0.40   # vertical shin length (down)

        # Lower body: thighs go forward (Y-), shins drop straight down
        for side, sign in (("l", -1), ("r", 1)):
            hx_off = sign * 0.108
            hip    = (hx_off, 0,              seat_h)
            knee   = (hx_off, -thigh_len,     seat_h)        # same height, pushed forward
            ankle  = (hx_off, -thigh_len,     seat_h - shin_len)  # drops straight down
            foot   = (hx_off, -thigh_len - 0.08, seat_h - shin_len - 0.03)
            lm[f"hip_{side}"]   = hip
            lm[f"knee_{side}"]  = knee
            lm[f"ankle_{side}"] = ankle
            lm[f"foot_{side}"]  = foot

        # Upper body lifts to sit upright on seat
        lift = seat_h - 0.870
        for k in ["pelvis","navel","chest","neck_base","chin",
                  "head_ctr","head_top","sh_l","sh_r"]:
            x, y, z = lm[k]
            lm[k] = (x, y, z + lift)

        # Arms folded in lap
        lm["elbow_l"] = (-0.115, -0.100, seat_h + 0.18)
        lm["wrist_l"] = (-0.055, -0.200, seat_h + 0.03)
        lm["hand_l"]  = (-0.035, -0.225, seat_h - 0.02)
        lm["elbow_r"] = ( 0.115, -0.100, seat_h + 0.18)
        lm["wrist_r"] = ( 0.055, -0.200, seat_h + 0.03)
        lm["hand_r"]  = ( 0.035, -0.225, seat_h - 0.02)

    # Head rotation
    pivot = lm["neck_base"]
    turn  = getattr(pose_detail, "head_turn", 0.0)
    tilt  = getattr(pose_detail, "head_tilt", 0.0)
    nod   = getattr(pose_detail, "head_nod",  0.0)
    for key in ("chin", "head_ctr", "head_top"):
        p = lm[key]
        p = _rotate(p, pivot, turn, "z")
        p = _rotate(p, pivot, tilt, "y")
        p = _rotate(p, pivot, nod,  "x")
        lm[key] = p

    return lm


# ─────────────────────────────────────────────────────────────────────────────
# Figure assembly
# ─────────────────────────────────────────────────────────────────────────────

def build_figure_code(character) -> str:
    pose_name   = character.pose.name
    pose_detail = character.pose_detail
    lm          = compute_landmarks(pose_name, pose_detail)

    skin_colors = {
        "FAIR":   (0.91, 0.78, 0.65), "LIGHT":  (0.87, 0.72, 0.57),
        "MEDIUM": (0.76, 0.57, 0.40), "OLIVE":  (0.67, 0.51, 0.33),
        "TAN":    (0.62, 0.45, 0.28), "BROWN":  (0.46, 0.29, 0.16),
        "DEEP":   (0.28, 0.17, 0.09),
    }
    sc = skin_colors.get(character.skin_tone.name, (0.76, 0.57, 0.40))
    hc = character.hair_color

    def p(k): return lm[k]
    def mid(a, b, t=0.5): return _lerp3(p(a), p(b), t)

    # ── Body builder ──────────────────────────────────────────────────────────
    body = MballBuilder()

    # Head & face: replaced by the mesh-based face from face_builder.
    # Keep only a small cranium blob so the hair and neck metaballs connect.
    # The jaw / face features are all removed — the mesh face handles them.

    # Neck
    body.segment(p("chin"), p("neck_base"), R["neck"])

    # Torso — spine line + bilateral chest volume
    body.segment(p("neck_base"), p("pelvis"), R["chest"])
    # Side chest bulge
    body.point((-0.090, p("chest")[1], p("chest")[2]), R["chest"] * 0.85)
    body.point(( 0.090, p("chest")[1], p("chest")[2]), R["chest"] * 0.85)
    # Waist pinch
    body.point(p("navel"), R["waist"])
    # Pelvis/hip width — extend forward to bridge torso→thigh junction
    body.point(p("hip_l"), R["pelvis"] * 0.80)
    body.point(p("hip_r"), R["pelvis"] * 0.80)
    # Bridge blobs at thigh root (same position as hip but pushed to thigh Y)
    body.point(_lerp3(p("hip_l"), p("knee_l"), 0.15), R["thigh"] * 1.1)
    body.point(_lerp3(p("hip_r"), p("knee_r"), 0.15), R["thigh"] * 1.1)

    # Shoulders
    body.segment(p("neck_base"), p("sh_l"), R["shoulder"])
    body.segment(p("neck_base"), p("sh_r"), R["shoulder"])

    # Left arm
    body.segment(p("sh_l"), p("elbow_l"), R["upper_arm"], taper=True)
    body.segment(p("elbow_l"), p("wrist_l"), R["forearm"], taper=True)
    body.point(p("hand_l"), R["hand"])

    # Right arm
    body.segment(p("sh_r"), p("elbow_r"), R["upper_arm"], taper=True)
    body.segment(p("elbow_r"), p("wrist_r"), R["forearm"], taper=True)
    body.point(p("hand_r"), R["hand"])

    # Left leg
    body.segment(p("hip_l"), p("knee_l"), R["thigh"], taper=True)
    body.segment(p("knee_l"), p("ankle_l"), R["shin"], taper=True)
    body.point(p("foot_l"), R["foot"])

    # Right leg
    body.segment(p("hip_r"), p("knee_r"), R["thigh"], taper=True)
    body.segment(p("knee_r"), p("ankle_r"), R["shin"], taper=True)
    body.point(p("foot_r"), R["foot"])

    # ── Hair builder ──────────────────────────────────────────────────────────
    # Renaissance centre-parted hair: falls behind and to the sides of the face.
    # Key constraints:
    #   - Side falls must be BEHIND the face (Y > face_front_Y) so they don't
    #     occlude the face from the camera at Y = -1.8.
    #   - Radii much smaller than head radius so hair doesn't dominate the frame.
    hair = MballBuilder()
    hc_pos = lm["head_ctr"]
    neck_z = lm["neck_base"][2]
    sh_z   = lm["sh_l"][2]
    HR     = R["head"]   # 0.118

    # Crown — compact, pushed well behind so it clears the forehead from camera view
    hair.point((hc_pos[0], hc_pos[1] + HR * 0.35, hc_pos[2] + HR * 0.75), 0.095)

    # Side falls: angled BEHIND the face (HR*0.22 = ~26mm behind face plane)
    # so the camera sees the face clearly with hair as dark flanking masses.
    # Radius 0.070 (59% of head) keeps them proportionate.
    for sx in (-1, 1):
        temple = (hc_pos[0] + sx * 0.095, hc_pos[1] + HR * 0.22, hc_pos[2] + HR * 0.40)
        jaw    = (hc_pos[0] + sx * 0.105, hc_pos[1] + HR * 0.18, hc_pos[2] - HR * 0.75)
        sh_lvl = (hc_pos[0] + sx * 0.095, hc_pos[1] + HR * 0.22, sh_z + 0.04)
        hair.segment(temple, jaw,    0.072)
        hair.segment(jaw,    sh_lvl, 0.058)

    # Back/nape volume — behind the head, smooth transition to shoulders
    hair.segment(
        (hc_pos[0], hc_pos[1] + HR * 0.90, hc_pos[2] + 0.02),
        (hc_pos[0], hc_pos[1] + HR * 0.55, neck_z + 0.03),
        0.082
    )

    body_code    = body.to_code("Figure",  "skin_mat", resolution=0.020)
    hair_code    = hair.to_code("Hair",    "hair_mat", resolution=0.025)
    face_code    = build_head_code(lm, pose_detail, getattr(character, 'morphology', None))
    costume_code = build_costume_code(lm, character.costume, pose_name)

    return f"""
# ═══════════════════════════════════════════════════════════════════
# Human figure — metaball body + mesh face + costume
# ═══════════════════════════════════════════════════════════════════

skin_mat = bpy.data.materials.new(name='Skin')
skin_mat.use_nodes = True
_skin_nt = skin_mat.node_tree
_skin_nt.nodes.clear()
_skin_out  = _skin_nt.nodes.new('ShaderNodeOutputMaterial')
_bsdf      = _skin_nt.nodes.new('ShaderNodeBsdfPrincipled')
_skin_out.location = (300, 0)
_bsdf.location     = (0, 0)
_bsdf.inputs['Base Color'].default_value = ({sc[0]:.4f},{sc[1]:.4f},{sc[2]:.4f},1.0)
_bsdf.inputs['Roughness'].default_value  = 0.52
if 'Subsurface Weight' in _bsdf.inputs:
    _bsdf.inputs['Subsurface Weight'].default_value = 0.12
if 'Subsurface Radius' in _bsdf.inputs:
    _bsdf.inputs['Subsurface Radius'].default_value = (0.85, 0.35, 0.22)
if 'Subsurface Scale' in _bsdf.inputs:
    _bsdf.inputs['Subsurface Scale'].default_value  = 0.05
_skin_nt.links.new(_bsdf.outputs['BSDF'], _skin_out.inputs['Surface'])

hair_mat = bpy.data.materials.new(name='Hair')
hair_mat.use_nodes = True
_hair_nt = hair_mat.node_tree
_hair_nt.nodes.clear()
_hair_out  = _hair_nt.nodes.new('ShaderNodeOutputMaterial')
_hbsdf     = _hair_nt.nodes.new('ShaderNodeBsdfPrincipled')
_hair_out.location = (300, 0)
_hbsdf.location    = (0, 0)
_hbsdf.inputs['Base Color'].default_value = ({hc[0]:.4f},{hc[1]:.4f},{hc[2]:.4f},1.0)
_hbsdf.inputs['Roughness'].default_value  = 0.80
_hair_nt.links.new(_hbsdf.outputs['BSDF'], _hair_out.inputs['Surface'])

{body_code}
{hair_code}
{face_code}
{costume_code}
"""


# ─────────────────────────────────────────────────────────────────────────────
# Standalone test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, 'C:/Users/4nick')
    from scene_schema import Character, Pose, PoseDetail, SkinTone
    ch = Character(
        pose=Pose.SEATED,
        pose_detail=PoseDetail(head_turn=-15.0, head_nod=5.0),
        skin_tone=SkinTone.LIGHT,
        hair_color=(0.22, 0.10, 0.04),
    )
    code = build_figure_code(ch)
    n_elems = code.count("_el.co")
    print(f"Generated {len(code)} chars, {n_elems} metaball elements. OK")
