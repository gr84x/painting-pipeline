"""
Deer head anatomy — 3/4 profile view (doe / without antlers).

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
Bounding ellipse: ear tips to chin (ny), snout to far ear (nx).

Deer have a long, tapered muzzle, very large liquid eyes set wide on the
skull, and large ears that extend well beyond the skull width. The eyes
are the dominant feature and carry the characteristic gentle expression.
The nose is broad and dark. In 3/4 profile, the near ear is prominent.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("near_eye",          nx=-0.18, ny=-0.18),
    Landmark("far_eye",           nx=+0.30, ny=-0.20),
    Landmark("nose_pad",          nx=-0.55, ny=+0.28),
    Landmark("left_nostril",      nx=-0.52, ny=+0.24),
    Landmark("right_nostril",     nx=-0.44, ny=+0.24),
    Landmark("muzzle_centre",     nx=-0.40, ny=+0.22),
    Landmark("upper_lip",         nx=-0.38, ny=+0.40),
    Landmark("mouth_corner",      nx=-0.28, ny=+0.42),
    Landmark("chin",              nx=-0.14, ny=+0.72),
    Landmark("forehead",          nx=+0.12, ny=-0.38),
    Landmark("near_ear_base",     nx=-0.32, ny=-0.52),
    Landmark("near_ear_tip",      nx=-0.42, ny=-0.92),
    Landmark("far_ear_base",      nx=+0.42, ny=-0.48),
    Landmark("far_ear_tip",       nx=+0.55, ny=-0.88),
    Landmark("cheek",             nx=+0.05, ny=+0.08),
    Landmark("throat",            nx=+0.10, ny=+0.80),
]

FEATURE_ZONES = [
    FeatureZone("near_eye",   "near_eye",      radius_nx=0.22, radius_ny=0.16,
                error_weight=8.0, stroke_size_scale=0.50, jitter_scale=0.55, wet_blend_scale=0.50),
    FeatureZone("far_eye",    "far_eye",        radius_nx=0.18, radius_ny=0.13,
                error_weight=6.5, stroke_size_scale=0.54, jitter_scale=0.58, wet_blend_scale=0.52),
    FeatureZone("nose",       "nose_pad",        radius_nx=0.18, radius_ny=0.14,
                error_weight=5.0, stroke_size_scale=0.58, jitter_scale=0.62),
    FeatureZone("muzzle",     "muzzle_centre",   radius_nx=0.28, radius_ny=0.22,
                error_weight=3.0, stroke_size_scale=0.68),
    FeatureZone("mouth",      "mouth_corner",    radius_nx=0.20, radius_ny=0.12,
                error_weight=2.5, stroke_size_scale=0.68),
    FeatureZone("near_ear",   "near_ear_tip",    radius_nx=0.16, radius_ny=0.28,
                error_weight=2.5, stroke_size_scale=0.68),
    FeatureZone("far_ear",    "far_ear_tip",     radius_nx=0.14, radius_ny=0.26,
                error_weight=2.0, stroke_size_scale=0.72),
]

FLOW_ZONES = [
    FlowZone("forehead", "diagonal",
             {"nx_factor": 0.10, "ny_factor": -0.95, "anchor_nx": +0.12, "anchor_ny": -0.38},
             weight_sigma_nx=0.48, weight_sigma_ny=0.25),
    FlowZone("near_eye_socket", "orbital",
             {"orbit_anchor": "near_eye", "orbit_nx": -0.18, "orbit_ny": -0.18},
             weight_sigma_nx=0.20, weight_sigma_ny=0.16),
    FlowZone("far_eye_socket", "orbital",
             {"orbit_anchor": "far_eye", "orbit_nx": +0.30, "orbit_ny": -0.20},
             weight_sigma_nx=0.16, weight_sigma_ny=0.14),
    FlowZone("cheek", "diagonal",
             {"nx_factor": -0.35, "ny_factor": 0.90, "anchor_nx": +0.06, "anchor_ny": +0.12},
             weight_sigma_nx=0.40, weight_sigma_ny=0.36),
    FlowZone("muzzle", "diagonal",
             {"nx_factor": -0.06, "ny_factor": 0.12, "anchor_nx": -0.42, "anchor_ny": +0.20},
             weight_sigma_nx=0.26, weight_sigma_ny=0.20),
    FlowZone("near_ear", "fixed",
             {"radians": math.pi * 0.55, "anchor_nx": -0.37, "anchor_ny": -0.72},
             weight_sigma_nx=0.16, weight_sigma_ny=0.28),
    FlowZone("far_ear", "fixed",
             {"radians": math.pi * 0.46, "anchor_nx": +0.48, "anchor_ny": -0.68},
             weight_sigma_nx=0.14, weight_sigma_ny=0.26),
    FlowZone("throat", "diagonal",
             {"nx_factor": 0.15, "ny_factor": 0.95, "anchor_nx": +0.10, "anchor_ny": +0.78},
             weight_sigma_nx=0.42, weight_sigma_ny=0.18),
]

PROPORTIONS = {
    "muzzle_length_fraction":  0.48,
    "eye_diameter_fraction":   0.22,   # large, liquid eyes
    "ear_height_fraction":     0.42,
    "interocular_distance_nx": 0.48,
    "aspect_ratio":            0.85,
}

DEER = SubjectAnatomy(
    subject_id="deer",
    display_name="Deer / Doe (3/4 Profile)",
    landmarks=LANDMARKS,
    feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES,
    proportions=PROPORTIONS,
)
