"""
Human portrait anatomy — full frontal face.

Normalized coordinate system: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
The bounding ellipse encompasses the face from hairline (-1) to chin (+1)
and ear-to-ear (-1 to +1).

Landmark positions derived from classical canon of facial proportions
(Leonardo, Dürer, Loomis). Eyes sit at ny ≈ -0.12 (the "eye line" is
slightly above vertical center of the face). Nose base at ny ≈ +0.28.
Mouth at ny ≈ +0.45. Chin at ny ≈ +0.78.

Flow zones encode how a portrait painter's brush moves across each
anatomical plane — following form, not image edges.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy


# ── Landmarks ─────────────────────────────────────────────────────────────────

LANDMARKS = [
    # Eyes
    Landmark("left_eye",           nx=-0.30, ny=-0.12),
    Landmark("right_eye",          nx=+0.30, ny=-0.12),
    # Brows
    Landmark("left_brow_inner",    nx=-0.12, ny=-0.26),
    Landmark("left_brow_outer",    nx=-0.44, ny=-0.22),
    Landmark("right_brow_inner",   nx=+0.12, ny=-0.26),
    Landmark("right_brow_outer",   nx=+0.44, ny=-0.22),
    # Nose
    Landmark("nose_bridge",        nx= 0.00, ny=+0.04),
    Landmark("nose_tip",           nx= 0.00, ny=+0.22),
    Landmark("left_nostril",       nx=-0.12, ny=+0.28),
    Landmark("right_nostril",      nx=+0.12, ny=+0.28),
    # Mouth
    Landmark("upper_lip_centre",   nx= 0.00, ny=+0.42),
    Landmark("lower_lip_centre",   nx= 0.00, ny=+0.52),
    Landmark("left_mouth_corner",  nx=-0.22, ny=+0.47),
    Landmark("right_mouth_corner", nx=+0.22, ny=+0.47),
    # Jaw and skull
    Landmark("chin",               nx= 0.00, ny=+0.78),
    Landmark("left_jaw",           nx=-0.55, ny=+0.55),
    Landmark("right_jaw",          nx=+0.55, ny=+0.55),
    Landmark("forehead_centre",    nx= 0.00, ny=-0.55),
    Landmark("left_ear",           nx=-0.88, ny=+0.02),
    Landmark("right_ear",          nx=+0.88, ny=+0.02),
    # Cheekbones
    Landmark("left_cheekbone",     nx=-0.50, ny=+0.05),
    Landmark("right_cheekbone",    nx=+0.50, ny=+0.05),
]


# ── Feature zones ─────────────────────────────────────────────────────────────
# error_weight: how many times more strokes this zone should attract vs baseline.
# Eyes are highest priority — they define likeness above all other features.

FEATURE_ZONES = [
    FeatureZone(
        name="left_eye",
        anchor="left_eye",
        radius_nx=0.22, radius_ny=0.12,
        error_weight=7.0,
        stroke_size_scale=0.55,
        jitter_scale=0.60,
        wet_blend_scale=0.55,
    ),
    FeatureZone(
        name="right_eye",
        anchor="right_eye",
        radius_nx=0.22, radius_ny=0.12,
        error_weight=7.0,
        stroke_size_scale=0.55,
        jitter_scale=0.60,
        wet_blend_scale=0.55,
    ),
    FeatureZone(
        name="left_brow",
        anchor="left_brow_inner",
        radius_nx=0.28, radius_ny=0.08,
        error_weight=3.0,
        stroke_size_scale=0.70,
        jitter_scale=0.75,
    ),
    FeatureZone(
        name="right_brow",
        anchor="right_brow_inner",
        radius_nx=0.28, radius_ny=0.08,
        error_weight=3.0,
        stroke_size_scale=0.70,
        jitter_scale=0.75,
    ),
    FeatureZone(
        name="nose",
        anchor="nose_tip",
        radius_nx=0.20, radius_ny=0.18,
        error_weight=4.0,
        stroke_size_scale=0.70,
        jitter_scale=0.70,
    ),
    FeatureZone(
        name="mouth",
        anchor="upper_lip_centre",
        radius_nx=0.35, radius_ny=0.16,
        error_weight=5.0,
        stroke_size_scale=0.60,
        jitter_scale=0.65,
        wet_blend_scale=0.60,
    ),
]


# ── Flow zones ────────────────────────────────────────────────────────────────
# Each zone defines stroke direction for a facial plane.
# Follows the seven-zone approach in stroke_engine.anatomy_flow_field()
# but expressed as data so it can be inspected, extended, and overridden.

FLOW_ZONES = [
    # Forehead — near-horizontal with slight outward sweep from centre
    FlowZone(
        name="forehead",
        angle_type="diagonal",
        angle_params={"nx_factor": 0.18, "ny_factor": 1.0,
                      "anchor_nx": 0.00, "anchor_ny": -0.55},
        weight_sigma_nx=0.65, weight_sigma_ny=0.25,
    ),
    # Brow ridge / upper cheek — diagonal following supraorbital arc
    FlowZone(
        name="brow_ridge",
        angle_type="diagonal",
        angle_params={"nx_factor": 0.60, "ny_factor": -0.30,
                      "anchor_nx": 0.00, "anchor_ny": -0.22},
        weight_sigma_nx=0.55, weight_sigma_ny=0.18,
    ),
    # Left eye socket — strokes orbit around the eye
    FlowZone(
        name="left_eye_socket",
        angle_type="orbital",
        angle_params={"orbit_anchor": "left_eye",
                      "orbit_nx": -0.30, "orbit_ny": -0.12},
        weight_sigma_nx=0.20, weight_sigma_ny=0.16,
    ),
    # Right eye socket
    FlowZone(
        name="right_eye_socket",
        angle_type="orbital",
        angle_params={"orbit_anchor": "right_eye",
                      "orbit_nx": +0.30, "orbit_ny": -0.12},
        weight_sigma_nx=0.20, weight_sigma_ny=0.16,
    ),
    # Nose bridge — near-vertical, down the nasal planes
    FlowZone(
        name="nose_bridge",
        angle_type="diagonal",
        angle_params={"nx_factor": 0.10, "ny_factor": 0.90,
                      "anchor_nx": 0.00, "anchor_ny": +0.12},
        weight_sigma_nx=0.14, weight_sigma_ny=0.25,
    ),
    # Cheeks — diagonal toward jaw, following zygoma
    FlowZone(
        name="left_cheek",
        angle_type="diagonal",
        angle_params={"nx_factor": -0.55, "ny_factor": 0.70,
                      "anchor_nx": -0.42, "anchor_ny": +0.12},
        weight_sigma_nx=0.28, weight_sigma_ny=0.30,
    ),
    FlowZone(
        name="right_cheek",
        angle_type="diagonal",
        angle_params={"nx_factor": +0.55, "ny_factor": 0.70,
                      "anchor_nx": +0.42, "anchor_ny": +0.12},
        weight_sigma_nx=0.28, weight_sigma_ny=0.30,
    ),
    # Philtrum / lip — near-horizontal, converging at centre
    FlowZone(
        name="philtrum_lip",
        angle_type="diagonal",
        angle_params={"nx_factor": -0.12, "ny_factor": 1.0,
                      "anchor_nx": 0.00, "anchor_ny": +0.46},
        weight_sigma_nx=0.30, weight_sigma_ny=0.14,
    ),
    # Chin / mandible — downward-curving, fanning outward
    FlowZone(
        name="chin_mandible",
        angle_type="diagonal",
        angle_params={"nx_factor": 0.40, "ny_factor": 0.85,
                      "anchor_nx": 0.00, "anchor_ny": +0.70},
        weight_sigma_nx=0.45, weight_sigma_ny=0.20,
    ),
]


# ── Proportions ───────────────────────────────────────────────────────────────

PROPORTIONS = {
    "eye_width_fraction":          0.22,   # eye width / face width
    "interocular_distance_nx":     0.60,   # centre-to-centre in normalized x
    "nose_length_ny":              0.34,   # brow to nose tip in normalized y
    "mouth_width_fraction":        0.44,   # mouth width / face width
    "eye_to_mouth_ny":             0.59,   # eye line to mouth centre in normalized y
    "ear_height_fraction":         0.35,   # ear height / face height
}


# ── Assembly ──────────────────────────────────────────────────────────────────

HUMAN_PORTRAIT = SubjectAnatomy(
    subject_id="human_portrait",
    display_name="Human Portrait (Frontal)",
    landmarks=LANDMARKS,
    feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES,
    proportions=PROPORTIONS,
)
