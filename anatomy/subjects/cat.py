"""
Cat head anatomy — frontal or slight 3/4 face.

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
Bounding ellipse: ear tips to chin (ny), ear-to-ear (nx).

Cats have a distinctively round skull, very short muzzle, and extremely
large eyes relative to head size — eyes are the dominant feature and
the primary focus for any cat portrait. The whisker pads are broad and
prominent. Ears are tall, triangular, and widely spaced.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("left_eye",          nx=-0.30, ny=-0.08),
    Landmark("right_eye",         nx=+0.30, ny=-0.08),
    Landmark("nose_tip",          nx= 0.00, ny=+0.22),
    Landmark("left_nostril",      nx=-0.06, ny=+0.20),
    Landmark("right_nostril",     nx=+0.06, ny=+0.20),
    Landmark("left_whisker_pad",  nx=-0.22, ny=+0.28),
    Landmark("right_whisker_pad", nx=+0.22, ny=+0.28),
    Landmark("mouth_centre",      nx= 0.00, ny=+0.36),
    Landmark("chin",              nx= 0.00, ny=+0.60),
    Landmark("forehead",          nx= 0.00, ny=-0.38),
    Landmark("left_ear_base",     nx=-0.50, ny=-0.42),
    Landmark("left_ear_tip",      nx=-0.52, ny=-0.88),
    Landmark("right_ear_base",    nx=+0.50, ny=-0.42),
    Landmark("right_ear_tip",     nx=+0.52, ny=-0.88),
    Landmark("left_cheek",        nx=-0.48, ny=+0.12),
    Landmark("right_cheek",       nx=+0.48, ny=+0.12),
]

FEATURE_ZONES = [
    # Cat eyes are proportionally the largest of any common subject
    FeatureZone("left_eye",         "left_eye",         radius_nx=0.26, radius_ny=0.16,
                error_weight=8.0, stroke_size_scale=0.50, jitter_scale=0.55, wet_blend_scale=0.50),
    FeatureZone("right_eye",        "right_eye",        radius_nx=0.26, radius_ny=0.16,
                error_weight=8.0, stroke_size_scale=0.50, jitter_scale=0.55, wet_blend_scale=0.50),
    FeatureZone("nose",             "nose_tip",         radius_nx=0.12, radius_ny=0.10,
                error_weight=4.5, stroke_size_scale=0.55, jitter_scale=0.60),
    FeatureZone("left_whisker_pad", "left_whisker_pad", radius_nx=0.20, radius_ny=0.14,
                error_weight=3.0, stroke_size_scale=0.65),
    FeatureZone("right_whisker_pad","right_whisker_pad",radius_nx=0.20, radius_ny=0.14,
                error_weight=3.0, stroke_size_scale=0.65),
    FeatureZone("mouth",            "mouth_centre",     radius_nx=0.22, radius_ny=0.10,
                error_weight=3.5, stroke_size_scale=0.60, jitter_scale=0.65),
    FeatureZone("left_ear",         "left_ear_tip",     radius_nx=0.14, radius_ny=0.28,
                error_weight=2.0, stroke_size_scale=0.70),
    FeatureZone("right_ear",        "right_ear_tip",    radius_nx=0.14, radius_ny=0.28,
                error_weight=2.0, stroke_size_scale=0.70),
]

FLOW_ZONES = [
    FlowZone("forehead", "diagonal",
             {"nx_factor": 0.08, "ny_factor": 1.0, "anchor_nx": 0.00, "anchor_ny": -0.38},
             weight_sigma_nx=0.55, weight_sigma_ny=0.22),
    FlowZone("left_eye_socket", "orbital",
             {"orbit_anchor": "left_eye", "orbit_nx": -0.30, "orbit_ny": -0.08},
             weight_sigma_nx=0.22, weight_sigma_ny=0.18),
    FlowZone("right_eye_socket", "orbital",
             {"orbit_anchor": "right_eye", "orbit_nx": +0.30, "orbit_ny": -0.08},
             weight_sigma_nx=0.22, weight_sigma_ny=0.18),
    # Whisker pads — fur radiates outward from nose
    FlowZone("left_whisker_region", "diagonal",
             {"nx_factor": -0.55, "ny_factor": 0.50, "anchor_nx": -0.20, "anchor_ny": +0.24},
             weight_sigma_nx=0.24, weight_sigma_ny=0.18),
    FlowZone("right_whisker_region", "diagonal",
             {"nx_factor": +0.55, "ny_factor": 0.50, "anchor_nx": +0.20, "anchor_ny": +0.24},
             weight_sigma_nx=0.24, weight_sigma_ny=0.18),
    FlowZone("left_cheek", "diagonal",
             {"nx_factor": -0.45, "ny_factor": 0.80, "anchor_nx": -0.42, "anchor_ny": +0.15},
             weight_sigma_nx=0.28, weight_sigma_ny=0.28),
    FlowZone("right_cheek", "diagonal",
             {"nx_factor": +0.45, "ny_factor": 0.80, "anchor_nx": +0.42, "anchor_ny": +0.15},
             weight_sigma_nx=0.28, weight_sigma_ny=0.28),
    FlowZone("left_ear", "fixed",
             {"radians": math.pi * 0.54, "anchor_nx": -0.51, "anchor_ny": -0.65},
             weight_sigma_nx=0.14, weight_sigma_ny=0.26),
    FlowZone("right_ear", "fixed",
             {"radians": math.pi * 0.46, "anchor_nx": +0.51, "anchor_ny": -0.65},
             weight_sigma_nx=0.14, weight_sigma_ny=0.26),
]

PROPORTIONS = {
    "muzzle_length_fraction":  0.18,
    "eye_diameter_fraction":   0.28,   # very large eyes
    "ear_height_fraction":     0.46,
    "interocular_distance_nx": 0.60,
    "aspect_ratio":            0.95,   # nearly circular skull
}

CAT = SubjectAnatomy(
    subject_id="cat",
    display_name="Cat (Frontal)",
    landmarks=LANDMARKS,
    feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES,
    proportions=PROPORTIONS,
)
