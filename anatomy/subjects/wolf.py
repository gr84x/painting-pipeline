"""
Wolf head anatomy — 3/4 profile view.

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
Bounding ellipse encompasses ears to chin (ny), snout tip to ruff (nx).

Wolves share the canid head structure with foxes but are proportionally
larger-skulled, with a longer and broader muzzle, smaller eyes relative
to skull size, and more prominent, upright ears. The ruff (neck fur) is
substantial and should be painted with outward-fanning strokes.
In 3/4 profile the snout angles to the viewer's left.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("near_eye",          nx=-0.24, ny=-0.12),
    Landmark("far_eye",           nx=+0.14, ny=-0.14),
    Landmark("nose_pad",          nx=-0.68, ny=+0.10),
    Landmark("left_nostril",      nx=-0.64, ny=+0.08),
    Landmark("right_nostril",     nx=-0.56, ny=+0.08),
    Landmark("muzzle_centre",     nx=-0.50, ny=+0.16),
    Landmark("mouth_corner",      nx=-0.38, ny=+0.32),
    Landmark("chin",              nx=-0.18, ny=+0.70),
    Landmark("forehead",          nx=+0.08, ny=-0.42),
    Landmark("left_ear_base",     nx=-0.30, ny=-0.55),
    Landmark("left_ear_tip",      nx=-0.34, ny=-0.90),
    Landmark("right_ear_base",    nx=+0.36, ny=-0.50),
    Landmark("right_ear_tip",     nx=+0.38, ny=-0.86),
    Landmark("cheekbone",         nx=-0.08, ny=+0.06),
    Landmark("ruff_left",         nx=-0.28, ny=+0.82),
    Landmark("ruff_right",        nx=+0.42, ny=+0.74),
]

FEATURE_ZONES = [
    FeatureZone("near_eye",  "near_eye",      radius_nx=0.20, radius_ny=0.14,
                error_weight=7.0, stroke_size_scale=0.55, jitter_scale=0.58, wet_blend_scale=0.52),
    FeatureZone("far_eye",   "far_eye",       radius_nx=0.15, radius_ny=0.11,
                error_weight=5.5, stroke_size_scale=0.58, jitter_scale=0.62, wet_blend_scale=0.56),
    FeatureZone("nose_pad",  "nose_pad",      radius_nx=0.16, radius_ny=0.12,
                error_weight=5.0, stroke_size_scale=0.52, jitter_scale=0.58),
    FeatureZone("muzzle",    "muzzle_centre", radius_nx=0.30, radius_ny=0.22,
                error_weight=3.5, stroke_size_scale=0.68, jitter_scale=0.72),
    FeatureZone("mouth",     "mouth_corner",  radius_nx=0.20, radius_ny=0.12,
                error_weight=2.5, stroke_size_scale=0.65),
    FeatureZone("left_ear",  "left_ear_tip",  radius_nx=0.14, radius_ny=0.24,
                error_weight=2.0, stroke_size_scale=0.72),
    FeatureZone("right_ear", "right_ear_tip", radius_nx=0.12, radius_ny=0.22,
                error_weight=1.8, stroke_size_scale=0.72),
]

FLOW_ZONES = [
    FlowZone("crown", "diagonal",
             {"nx_factor": 0.12, "ny_factor": -1.0, "anchor_nx": +0.08, "anchor_ny": -0.55},
             weight_sigma_nx=0.48, weight_sigma_ny=0.28),
    FlowZone("cheek", "diagonal",
             {"nx_factor": -0.40, "ny_factor": 0.88, "anchor_nx": -0.04, "anchor_ny": +0.10},
             weight_sigma_nx=0.40, weight_sigma_ny=0.38),
    FlowZone("near_eye_socket", "orbital",
             {"orbit_anchor": "near_eye", "orbit_nx": -0.24, "orbit_ny": -0.12},
             weight_sigma_nx=0.18, weight_sigma_ny=0.14),
    FlowZone("far_eye_socket", "orbital",
             {"orbit_anchor": "far_eye", "orbit_nx": +0.14, "orbit_ny": -0.14},
             weight_sigma_nx=0.14, weight_sigma_ny=0.12),
    FlowZone("muzzle", "diagonal",
             {"nx_factor": -0.05, "ny_factor": 0.08, "anchor_nx": -0.52, "anchor_ny": +0.12},
             weight_sigma_nx=0.30, weight_sigma_ny=0.20),
    FlowZone("left_ear", "fixed",
             {"radians": math.pi * 0.54, "anchor_nx": -0.32, "anchor_ny": -0.72},
             weight_sigma_nx=0.14, weight_sigma_ny=0.22),
    FlowZone("right_ear", "fixed",
             {"radians": math.pi * 0.47, "anchor_nx": +0.37, "anchor_ny": -0.68},
             weight_sigma_nx=0.14, weight_sigma_ny=0.22),
    FlowZone("ruff", "diagonal",
             {"nx_factor": 0.35, "ny_factor": 0.92, "anchor_nx": +0.05, "anchor_ny": +0.80},
             weight_sigma_nx=0.50, weight_sigma_ny=0.18),
]

PROPORTIONS = {
    "muzzle_length_fraction":  0.52,   # longer muzzle than fox
    "eye_diameter_fraction":   0.16,   # smaller eyes relative to skull
    "ear_height_fraction":     0.40,
    "interocular_distance_nx": 0.38,
    "aspect_ratio":            0.90,
}

WOLF = SubjectAnatomy(
    subject_id="wolf",
    display_name="Wolf (3/4 Profile)",
    landmarks=LANDMARKS,
    feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES,
    proportions=PROPORTIONS,
)
