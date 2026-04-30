"""
Rabbit head anatomy — frontal or slight 3/4 face.

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
Bounding ellipse: ear tips to chin (ny), ear-to-ear (nx).

Rabbits have a very compact round skull, extremely long upright ears,
a short divided upper lip (the characteristic cleft), a prominent twitching
nose, and eyes set wide on the skull. The ears dominate the overall silhouette
and contain important colour transitions (pink interior, fur-covered exterior).
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("left_eye",          nx=-0.38, ny=+0.10),  # set low and wide
    Landmark("right_eye",         nx=+0.38, ny=+0.10),
    Landmark("nose",              nx= 0.00, ny=+0.42),
    Landmark("left_nostril",      nx=-0.06, ny=+0.40),
    Landmark("right_nostril",     nx=+0.06, ny=+0.40),
    Landmark("upper_lip_left",    nx=-0.08, ny=+0.52),  # cleft lip
    Landmark("upper_lip_right",   nx=+0.08, ny=+0.52),
    Landmark("mouth_centre",      nx= 0.00, ny=+0.56),
    Landmark("chin",              nx= 0.00, ny=+0.72),
    Landmark("forehead",          nx= 0.00, ny=-0.05),  # short forehead
    Landmark("left_ear_base",     nx=-0.28, ny=-0.08),
    Landmark("left_ear_mid",      nx=-0.30, ny=-0.52),
    Landmark("left_ear_tip",      nx=-0.28, ny=-0.88),
    Landmark("right_ear_base",    nx=+0.28, ny=-0.08),
    Landmark("right_ear_mid",     nx=+0.30, ny=-0.52),
    Landmark("right_ear_tip",     nx=+0.28, ny=-0.88),
    Landmark("left_cheek",        nx=-0.44, ny=+0.35),
    Landmark("right_cheek",       nx=+0.44, ny=+0.35),
]

FEATURE_ZONES = [
    FeatureZone("left_eye",  "left_eye",  radius_nx=0.18, radius_ny=0.14,
                error_weight=7.5, stroke_size_scale=0.52, jitter_scale=0.58, wet_blend_scale=0.52),
    FeatureZone("right_eye", "right_eye", radius_nx=0.18, radius_ny=0.14,
                error_weight=7.5, stroke_size_scale=0.52, jitter_scale=0.58, wet_blend_scale=0.52),
    FeatureZone("nose",      "nose",       radius_nx=0.14, radius_ny=0.12,
                error_weight=5.5, stroke_size_scale=0.52, jitter_scale=0.58),
    # Cleft upper lip — distinctive feature, high detail priority
    FeatureZone("upper_lip", "mouth_centre", radius_nx=0.20, radius_ny=0.12,
                error_weight=4.5, stroke_size_scale=0.58, jitter_scale=0.62),
    # Ear interiors have strong colour contrast and texture
    FeatureZone("left_ear_interior",  "left_ear_mid",  radius_nx=0.12, radius_ny=0.30,
                error_weight=3.0, stroke_size_scale=0.65),
    FeatureZone("right_ear_interior", "right_ear_mid", radius_nx=0.12, radius_ny=0.30,
                error_weight=3.0, stroke_size_scale=0.65),
    FeatureZone("left_cheek_fur",  "left_cheek",  radius_nx=0.22, radius_ny=0.18,
                error_weight=1.8),
    FeatureZone("right_cheek_fur", "right_cheek", radius_nx=0.22, radius_ny=0.18,
                error_weight=1.8),
]

FLOW_ZONES = [
    FlowZone("forehead", "diagonal",
             {"nx_factor": 0.06, "ny_factor": 1.0, "anchor_nx": 0.00, "anchor_ny": -0.05},
             weight_sigma_nx=0.40, weight_sigma_ny=0.14),
    FlowZone("left_eye_socket", "orbital",
             {"orbit_anchor": "left_eye", "orbit_nx": -0.38, "orbit_ny": +0.10},
             weight_sigma_nx=0.18, weight_sigma_ny=0.16),
    FlowZone("right_eye_socket", "orbital",
             {"orbit_anchor": "right_eye", "orbit_nx": +0.38, "orbit_ny": +0.10},
             weight_sigma_nx=0.18, weight_sigma_ny=0.16),
    # Cheeks — fur fans outward from nose
    FlowZone("left_cheek", "diagonal",
             {"nx_factor": -0.50, "ny_factor": 0.70, "anchor_nx": -0.38, "anchor_ny": +0.30},
             weight_sigma_nx=0.28, weight_sigma_ny=0.28),
    FlowZone("right_cheek", "diagonal",
             {"nx_factor": +0.50, "ny_factor": 0.70, "anchor_nx": +0.38, "anchor_ny": +0.30},
             weight_sigma_nx=0.28, weight_sigma_ny=0.28),
    # Nose area — short downward strokes
    FlowZone("nose_area", "diagonal",
             {"nx_factor": 0.04, "ny_factor": 0.96, "anchor_nx": 0.00, "anchor_ny": +0.44},
             weight_sigma_nx=0.18, weight_sigma_ny=0.16),
    # Ear exteriors — long vertical strokes following ear height
    FlowZone("left_ear", "fixed",
             {"radians": math.pi * 0.51, "anchor_nx": -0.29, "anchor_ny": -0.48},
             weight_sigma_nx=0.14, weight_sigma_ny=0.40),
    FlowZone("right_ear", "fixed",
             {"radians": math.pi * 0.49, "anchor_nx": +0.29, "anchor_ny": -0.48},
             weight_sigma_nx=0.14, weight_sigma_ny=0.40),
]

PROPORTIONS = {
    "muzzle_length_fraction":  0.15,
    "eye_diameter_fraction":   0.20,
    "ear_height_fraction":     0.80,   # ears are very tall
    "ear_width_fraction":      0.12,
    "interocular_distance_nx": 0.76,   # eyes set very wide
    "aspect_ratio":            0.70,   # tall due to ears
}

RABBIT = SubjectAnatomy(
    subject_id="rabbit",
    display_name="Rabbit (Frontal)",
    landmarks=LANDMARKS,
    feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES,
    proportions=PROPORTIONS,
)
