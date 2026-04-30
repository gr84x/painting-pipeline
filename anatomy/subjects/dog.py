"""
Dog head anatomy — frontal face (shepherd / upright-ear type).

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
Bounding ellipse: ear tips to chin (ny), ear-to-ear (nx).

Proportions represent a medium-sized domestic dog with upright ears
(German Shepherd, Husky, Malinois). Floppy-ear breeds can be approximated
by adjusting the ear landmark positions and reducing ear flow zone weight.
The muzzle is moderate length — shorter than a wolf, longer than a cat.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("left_eye",          nx=-0.28, ny=-0.10),
    Landmark("right_eye",         nx=+0.28, ny=-0.10),
    Landmark("left_brow",         nx=-0.28, ny=-0.22),
    Landmark("right_brow",        nx=+0.28, ny=-0.22),
    Landmark("nose_bridge",       nx= 0.00, ny=+0.12),
    Landmark("nose_pad",          nx= 0.00, ny=+0.30),
    Landmark("left_nostril",      nx=-0.08, ny=+0.28),
    Landmark("right_nostril",     nx=+0.08, ny=+0.28),
    Landmark("mouth_centre",      nx= 0.00, ny=+0.48),
    Landmark("left_mouth_corner", nx=-0.18, ny=+0.46),
    Landmark("right_mouth_corner",nx=+0.18, ny=+0.46),
    Landmark("chin",              nx= 0.00, ny=+0.72),
    Landmark("forehead",          nx= 0.00, ny=-0.45),
    Landmark("left_ear_base",     nx=-0.52, ny=-0.38),
    Landmark("left_ear_tip",      nx=-0.56, ny=-0.82),
    Landmark("right_ear_base",    nx=+0.52, ny=-0.38),
    Landmark("right_ear_tip",     nx=+0.56, ny=-0.82),
    Landmark("left_cheekbone",    nx=-0.42, ny=+0.05),
    Landmark("right_cheekbone",   nx=+0.42, ny=+0.05),
]

FEATURE_ZONES = [
    FeatureZone("left_eye",  "left_eye",  radius_nx=0.22, radius_ny=0.13,
                error_weight=7.0, stroke_size_scale=0.55, jitter_scale=0.60, wet_blend_scale=0.55),
    FeatureZone("right_eye", "right_eye", radius_nx=0.22, radius_ny=0.13,
                error_weight=7.0, stroke_size_scale=0.55, jitter_scale=0.60, wet_blend_scale=0.55),
    FeatureZone("nose_pad",  "nose_pad",  radius_nx=0.16, radius_ny=0.12,
                error_weight=5.0, stroke_size_scale=0.55, jitter_scale=0.60),
    FeatureZone("mouth",     "mouth_centre", radius_nx=0.28, radius_ny=0.14,
                error_weight=3.5, stroke_size_scale=0.65, jitter_scale=0.70),
    FeatureZone("left_ear",  "left_ear_tip",  radius_nx=0.14, radius_ny=0.26,
                error_weight=2.0, stroke_size_scale=0.75),
    FeatureZone("right_ear", "right_ear_tip", radius_nx=0.14, radius_ny=0.26,
                error_weight=2.0, stroke_size_scale=0.75),
]

FLOW_ZONES = [
    FlowZone("forehead", "diagonal",
             {"nx_factor": 0.12, "ny_factor": 1.0, "anchor_nx": 0.00, "anchor_ny": -0.45},
             weight_sigma_nx=0.60, weight_sigma_ny=0.25),
    FlowZone("left_eye_socket", "orbital",
             {"orbit_anchor": "left_eye", "orbit_nx": -0.28, "orbit_ny": -0.10},
             weight_sigma_nx=0.20, weight_sigma_ny=0.16),
    FlowZone("right_eye_socket", "orbital",
             {"orbit_anchor": "right_eye", "orbit_nx": +0.28, "orbit_ny": -0.10},
             weight_sigma_nx=0.20, weight_sigma_ny=0.16),
    FlowZone("muzzle", "diagonal",
             {"nx_factor": 0.05, "ny_factor": 0.95, "anchor_nx": 0.00, "anchor_ny": +0.22},
             weight_sigma_nx=0.22, weight_sigma_ny=0.22),
    FlowZone("left_cheek", "diagonal",
             {"nx_factor": -0.40, "ny_factor": 0.85, "anchor_nx": -0.38, "anchor_ny": +0.10},
             weight_sigma_nx=0.30, weight_sigma_ny=0.30),
    FlowZone("right_cheek", "diagonal",
             {"nx_factor": +0.40, "ny_factor": 0.85, "anchor_nx": +0.38, "anchor_ny": +0.10},
             weight_sigma_nx=0.30, weight_sigma_ny=0.30),
    FlowZone("left_ear", "fixed",
             {"radians": math.pi * 0.52, "anchor_nx": -0.54, "anchor_ny": -0.60},
             weight_sigma_nx=0.14, weight_sigma_ny=0.24),
    FlowZone("right_ear", "fixed",
             {"radians": math.pi * 0.48, "anchor_nx": +0.54, "anchor_ny": -0.60},
             weight_sigma_nx=0.14, weight_sigma_ny=0.24),
]

PROPORTIONS = {
    "muzzle_length_fraction":  0.32,
    "eye_diameter_fraction":   0.18,
    "ear_height_fraction":     0.44,
    "interocular_distance_nx": 0.56,
    "aspect_ratio":            0.88,
}

DOG = SubjectAnatomy(
    subject_id="dog",
    display_name="Dog (Frontal, Upright Ears)",
    landmarks=LANDMARKS,
    feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES,
    proportions=PROPORTIONS,
)
