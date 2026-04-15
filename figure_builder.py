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
# Hand finger articulation
# ─────────────────────────────────────────────────────────────────────────────

def _hand_metaballs(builder: "MballBuilder", hand_pos, wrist_pos,
                    side: str = "l", curl: float = 0.0) -> None:
    """Add finger metaballs to *builder* for one hand.

    The palm is oriented from *wrist_pos* toward *hand_pos* (the knuckle line).
    Fingers fan out laterally from the palm axis.

    Parameters
    ----------
    builder   : MballBuilder to accumulate into
    hand_pos  : (x, y, z) world position of the knuckle centre
    wrist_pos : (x, y, z) world position of the wrist
    side      : 'l' or 'r' — controls which way the thumb splays
    curl      : 0.0 = open relaxed hand, 1.0 = closed fist
    """
    # ── Palm ──────────────────────────────────────────────────────────────────
    # Palm blob centred between wrist and knuckles.
    palm_ctr = _lerp3(wrist_pos, hand_pos, 0.55)
    builder.point(palm_ctr, 0.035, stiffness=2.0)

    # Derive palm local axes.
    # Forward axis: wrist → knuckles (finger extension direction).
    dx = hand_pos[0] - wrist_pos[0]
    dy = hand_pos[1] - wrist_pos[1]
    dz = hand_pos[2] - wrist_pos[2]
    length = math.sqrt(dx*dx + dy*dy + dz*dz) or 1e-9
    fwd = (dx / length, dy / length, dz / length)

    # Lateral axis: world Z cross fwd, normalised.
    # For left hand the thumb is medial (positive X side); right hand opposite.
    lat_raw = (fwd[1]*1.0 - fwd[2]*0.0,
               fwd[2]*0.0 - fwd[0]*1.0,
               fwd[0]*0.0 - fwd[1]*0.0)  # cross(fwd, world-Z=(0,0,1)) → right
    lat_len = math.sqrt(sum(v*v for v in lat_raw)) or 1e-9
    lat = tuple(v / lat_len for v in lat_raw)  # points right (positive X)

    # Finger offsets: [index, middle, ring, pinky] fan from centre
    # Spread = fraction of half-hand width along *lat* axis.
    # Positive = toward anatomical little finger; negative = toward index.
    finger_data = [
        # (lateral_frac, finger_length_frac, proximal_radius, distal_radius)
        (-0.28, 1.00, 0.014, 0.011),   # index
        (-0.09, 1.05, 0.015, 0.012),   # middle (longest)
        ( 0.10, 0.97, 0.014, 0.011),   # ring
        ( 0.29, 0.85, 0.012, 0.010),   # pinky
    ]
    # Palm half-width = ~0.040 m
    palm_hw = 0.040

    # Finger segment length from knuckles to tip (~55mm for index).
    finger_len_base = length * 0.80   # scale relative to palm length

    # curl bends the distal phalanx toward the palm.  At curl=1 the fingertip
    # reaches ~50% of the way back to the palm centre.
    for lat_frac, len_frac, r_prox, r_dist in finger_data:
        # Knuckle base: at hand_pos, shifted laterally.
        # Positive lat_frac → little-finger side; flip for right hand.
        lat_sign = 1.0 if side == "l" else -1.0
        knuckle = (
            hand_pos[0] + lat_sign * lat_frac * palm_hw * lat[0],
            hand_pos[1] + lat_sign * lat_frac * palm_hw * lat[1],
            hand_pos[2] + lat_sign * lat_frac * palm_hw * lat[2],
        )

        seg_len = finger_len_base * len_frac
        prox_len = seg_len * 0.55   # proximal phalanx is longer
        dist_len = seg_len * 0.45

        # Proximal phalanx: extends along fwd direction from knuckle.
        prox_tip = (
            knuckle[0] + fwd[0] * prox_len,
            knuckle[1] + fwd[1] * prox_len,
            knuckle[2] + fwd[2] * prox_len,
        )
        builder.segment(knuckle, prox_tip, r_prox, stiffness=1.8)

        # Distal phalanx: at curl=0 continues along fwd; at curl=1 bends back
        # toward the palm (curling finger direction = negative fwd + slight down).
        curl_dir = (
            fwd[0] * (1.0 - curl) - fwd[0] * curl,
            fwd[1] * (1.0 - curl) - fwd[1] * curl,
            fwd[2] * (1.0 - 2.0 * curl),   # fingertip drops toward palm
        )
        cd_len = math.sqrt(sum(v*v for v in curl_dir)) or 1e-9
        curl_dir = tuple(v / cd_len for v in curl_dir)

        dist_tip = (
            prox_tip[0] + curl_dir[0] * dist_len,
            prox_tip[1] + curl_dir[1] * dist_len,
            prox_tip[2] + curl_dir[2] * dist_len,
        )
        builder.segment(prox_tip, dist_tip, r_dist, stiffness=1.8)

    # ── Thumb ──────────────────────────────────────────────────────────────────
    # Thumb root: on the medial (index-finger) side of the palm, angled ~45°
    # away from the palm plane.  Medial = negative lat_sign * lat axis.
    thumb_sign = -1.0 if side == "l" else 1.0   # thumb on medial side
    thumb_root = (
        palm_ctr[0] + thumb_sign * 0.030 * lat[0],
        palm_ctr[1] + thumb_sign * 0.030 * lat[1],
        palm_ctr[2] + thumb_sign * 0.030 * lat[2],
    )
    # Thumb proximal: 45° off palm axis, angled laterally and forward.
    thumb_prox_dir = (
        fwd[0] * 0.707 + thumb_sign * lat[0] * 0.707,
        fwd[1] * 0.707 + thumb_sign * lat[1] * 0.707,
        fwd[2] * 0.707,
    )
    tpd_len = math.sqrt(sum(v*v for v in thumb_prox_dir)) or 1e-9
    thumb_prox_dir = tuple(v / tpd_len for v in thumb_prox_dir)

    thumb_prox_len = finger_len_base * 0.55
    thumb_mid = (
        thumb_root[0] + thumb_prox_dir[0] * thumb_prox_len,
        thumb_root[1] + thumb_prox_dir[1] * thumb_prox_len,
        thumb_root[2] + thumb_prox_dir[2] * thumb_prox_len,
    )
    builder.segment(thumb_root, thumb_mid, 0.016, stiffness=1.8)

    # Thumb distal: at curl=0 continues; at curl=1 curls toward index finger.
    thumb_dist_len = finger_len_base * 0.40
    thumb_dist_dir = (
        thumb_prox_dir[0] * (1.0 - curl * 0.5) + thumb_sign * lat[0] * curl * 0.5,
        thumb_prox_dir[1] * (1.0 - curl * 0.5) + thumb_sign * lat[1] * curl * 0.5,
        thumb_prox_dir[2] - curl * 0.4,
    )
    tdd_len = math.sqrt(sum(v*v for v in thumb_dist_dir)) or 1e-9
    thumb_dist_dir = tuple(v / tdd_len for v in thumb_dist_dir)

    thumb_tip = (
        thumb_mid[0] + thumb_dist_dir[0] * thumb_dist_len,
        thumb_mid[1] + thumb_dist_dir[1] * thumb_dist_len,
        thumb_mid[2] + thumb_dist_dir[2] * thumb_dist_len,
    )
    builder.segment(thumb_mid, thumb_tip, 0.014, stiffness=1.8)


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

    if pose_name == "CROUCHING":
        # Deep knee bend: knees at ~0.30, hips at ~0.55
        # Thighs angle forward-down, shins nearly vertical
        for side, sign in (("l", -1), ("r", 1)):
            hx_off = sign * 0.108
            hip    = (hx_off,  0.04,  0.55)
            knee   = (hx_off, -0.10,  0.30)   # forward and low
            ankle  = (hx_off, -0.05,  0.08)   # shins nearly vertical
            foot   = (hx_off, -0.12,  0.038)
            lm[f"hip_{side}"]   = hip
            lm[f"knee_{side}"]  = knee
            lm[f"ankle_{side}"] = ankle
            lm[f"foot_{side}"]  = foot

        # Torso: pelvis drops, spine compresses to stay above the lowered hips
        # Lift = proportional to how much the pelvis dropped (0.870 → 0.55)
        crouch_lift = 0.55 - 0.870   # −0.32
        for k in ["pelvis", "navel", "chest", "neck_base", "chin",
                  "head_ctr", "head_top"]:
            x, y, z = lm[k]
            lm[k] = (x, y + 0.04, z + crouch_lift)
        for k in ["sh_l", "sh_r"]:
            x, y, z = lm[k]
            lm[k] = (x, y + 0.04, z + crouch_lift)

        # Arms hang / brace forward on knees
        lm["elbow_l"] = (-0.130, -0.12, 0.55)
        lm["wrist_l"] = (-0.100, -0.20, 0.38)
        lm["hand_l"]  = (-0.090, -0.23, 0.32)
        lm["elbow_r"] = ( 0.130, -0.12, 0.55)
        lm["wrist_r"] = ( 0.100, -0.20, 0.38)
        lm["hand_r"]  = ( 0.090, -0.23, 0.32)

    elif pose_name == "WALKING":
        sx = 0.205   # half-shoulder width (matches _standing_landmarks)

        # Left leg forward, right leg back
        lm["ankle_l"] = (-0.085, -0.25, 0.082)
        lm["knee_l"]  = (-0.103, -0.12, 0.470)
        lm["hip_l"]   = (-0.108,  0.04, 0.870)
        lm["foot_l"]  = (-0.085, -0.34, 0.038)

        lm["ankle_r"] = ( 0.085,  0.20, 0.082)
        lm["knee_r"]  = ( 0.103,  0.10, 0.470)
        lm["hip_r"]   = ( 0.108, -0.04, 0.870)
        lm["foot_r"]  = ( 0.085,  0.12, 0.038)

        # Slight forward lean on torso
        for k in ["pelvis", "navel", "chest", "neck_base", "chin",
                  "head_ctr", "head_top"]:
            x, y, z = lm[k]
            lm[k] = (x, y - 0.03, z)
        lm["chest"] = (lm["chest"][0], -0.05, lm["chest"][2])

        # Counterswing arms: right arm forward when left leg forward
        lm["elbow_r"] = ( sx + 0.02, -0.05, 1.160)
        lm["wrist_r"] = ( sx - 0.02, -0.10, 0.895)
        lm["hand_r"]  = ( sx - 0.03, -0.12, 0.830)
        lm["elbow_l"] = (-sx - 0.02,  0.06, 1.160)
        lm["wrist_l"] = (-sx + 0.02,  0.10, 0.895)
        lm["hand_l"]  = (-sx + 0.03,  0.12, 0.830)

        for k in ["sh_l", "sh_r"]:
            x, y, z = lm[k]
            lm[k] = (x, y - 0.03, z)

    elif pose_name == "RUNNING":
        sx = 0.205

        # Left leg driving forward; right leg trailing behind
        lm["ankle_l"] = (-0.085, -0.40, 0.082)
        lm["knee_l"]  = (-0.103, -0.10, 0.650)   # knee lifted high
        lm["hip_l"]   = (-0.108,  0.04, 0.870)
        lm["foot_l"]  = (-0.085, -0.50, 0.038)

        lm["ankle_r"] = ( 0.085,  0.35, 0.082)
        lm["knee_r"]  = ( 0.103,  0.20, 0.420)   # trailing, bent back
        lm["hip_r"]   = ( 0.108, -0.04, 0.870)
        lm["foot_r"]  = ( 0.085,  0.45, 0.038)

        # Strong forward lean
        for k in ["pelvis", "navel", "chest", "neck_base", "chin",
                  "head_ctr", "head_top"]:
            x, y, z = lm[k]
            lm[k] = (x, y - 0.06, z)
        lm["chest"]   = (lm["chest"][0],   -0.12, lm["chest"][2])
        lm["head_ctr"] = (lm["head_ctr"][0], -0.08, lm["head_ctr"][2])

        for k in ["sh_l", "sh_r"]:
            x, y, z = lm[k]
            lm[k] = (x, y - 0.06, z)

        # Strong arm swing — elbows bent ~90°
        lm["elbow_r"] = ( sx + 0.02, -0.10, 1.220)
        lm["wrist_r"] = ( sx - 0.04, -0.18, 1.050)
        lm["hand_r"]  = ( sx - 0.06, -0.22, 0.990)
        lm["elbow_l"] = (-sx - 0.02,  0.10, 1.100)
        lm["wrist_l"] = (-sx + 0.02,  0.18, 0.940)
        lm["hand_l"]  = (-sx + 0.03,  0.22, 0.880)

    elif pose_name == "FIGHTING":
        sx = 0.205

        # Slight crouch: knees bent, spine compressed ~0.05
        fight_squat = -0.05
        for k in ["pelvis", "navel", "chest", "neck_base", "chin",
                  "head_ctr", "head_top"]:
            x, y, z = lm[k]
            lm[k] = (x, y, z + fight_squat)
        for k in ["sh_l", "sh_r"]:
            x, y, z = lm[k]
            lm[k] = (x, y, z + fight_squat)

        # Left foot back (weight on back foot), right foot forward + wider
        lm["ankle_l"] = (-0.085,  0.15, 0.082)
        lm["knee_l"]  = (-0.103,  0.06, 0.445)
        lm["hip_l"]   = (-0.108,  0.00, 0.820)
        lm["foot_l"]  = (-0.085,  0.08, 0.038)

        lm["ankle_r"] = ( 0.110, -0.14, 0.082)
        lm["knee_r"]  = ( 0.118, -0.06, 0.445)
        lm["hip_r"]   = ( 0.108,  0.00, 0.820)
        lm["foot_r"]  = ( 0.110, -0.22, 0.038)

        # Guard position: left (lead) hand forward at chin height, right at jaw
        chin_z = lm["chin"][2]
        lm["elbow_l"] = (-sx + 0.05, -0.12, chin_z - 0.05)
        lm["wrist_l"] = (-sx + 0.10, -0.22, chin_z + 0.01)
        lm["hand_l"]  = (-sx + 0.12, -0.28, chin_z + 0.00)

        jaw_z = chin_z - 0.04
        lm["elbow_r"] = ( sx - 0.08, -0.05, jaw_z)
        lm["wrist_r"] = ( sx - 0.12, -0.14, jaw_z + 0.01)
        lm["hand_r"]  = ( sx - 0.14, -0.18, jaw_z)

    elif pose_name == "FLYING":
        sx = 0.205

        # Arms spread wide, elbows at shoulder height, wrists angled upward
        sh_z_l = lm["sh_l"][2]
        sh_z_r = lm["sh_r"][2]

        lm["sh_l"] = (-0.28, 0.025, sh_z_l)
        lm["sh_r"] = ( 0.28, 0.025, sh_z_r)

        lm["elbow_l"] = (-0.42, 0.020, sh_z_l + 0.01)
        lm["wrist_l"] = (-0.54, 0.010, sh_z_l + 0.04)
        lm["hand_l"]  = (-0.60, 0.005, sh_z_l + 0.06)

        lm["elbow_r"] = ( 0.42, 0.020, sh_z_r + 0.01)
        lm["wrist_r"] = ( 0.54, 0.010, sh_z_r + 0.04)
        lm["hand_r"]  = ( 0.60, 0.005, sh_z_r + 0.06)

        # Tilt whole torso/spine forward progressively from pelvis to head
        spine_keys = ["pelvis", "navel", "chest", "neck_base", "chin",
                      "head_ctr", "head_top", "sh_l", "sh_r"]
        spine_y_offsets = [0.00, -0.02, -0.04, -0.06, -0.07, -0.08, -0.08,
                           -0.04, -0.04]
        for k, dy in zip(spine_keys, spine_y_offsets):
            x, y, z = lm[k]
            lm[k] = (x, y + dy, z)

        # Head lifted slightly
        x, y, z = lm["head_ctr"]
        lm["head_ctr"] = (x, y, z + 0.02)

        # Legs trailing slightly behind
        for side in ("l", "r"):
            sign = -1 if side == "l" else 1
            hx_off = sign * 0.108
            lm[f"ankle_{side}"] = (sign * 0.085, 0.12, 0.082)
            lm[f"knee_{side}"]  = (sign * 0.103, 0.06, 0.470)
            lm[f"hip_{side}"]   = (hx_off,       0.00, 0.870)
            lm[f"foot_{side}"]  = (sign * 0.085, 0.18, 0.038)

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
    _hand_metaballs(body, p("hand_l"), p("wrist_l"), side="l")

    # Right arm
    body.segment(p("sh_r"), p("elbow_r"), R["upper_arm"], taper=True)
    body.segment(p("elbow_r"), p("wrist_r"), R["forearm"], taper=True)
    _hand_metaballs(body, p("hand_r"), p("wrist_r"), side="r")

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
    face_code    = build_head_code(lm, pose_detail, getattr(character, 'morphology', None),
                                   expression=getattr(character, 'expression', None))
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
