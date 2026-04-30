"""
Raptor head anatomy — 3/4 profile (hawk / eagle / falcon type).

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
Bounding ellipse: crown to chin (ny), snout tip to nape (nx).

Raptors share a distinctive hooked beak (the cere + culmen), a supraorbital
ridge that creates the characteristic fierce brow line, and forward-facing
eyes with exceptional acuity. The beak is strongly laterally compressed.
Feathers on the face lie flat, following tight tracts around beak and eye.
In 3/4 profile the cere (soft beak base) and nare are visible and painterly.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("near_eye",         nx=-0.20, ny=-0.15),
    Landmark("far_eye",          nx=+0.18, ny=-0.18),
    Landmark("supraorbital_ridge_near", nx=-0.20, ny=-0.28),  # the fierce brow
    Landmark("supraorbital_ridge_far",  nx=+0.18, ny=-0.30),
    Landmark("cere",             nx=-0.52, ny=+0.02),   # soft beak base
    Landmark("nare",             nx=-0.48, ny=-0.02),   # nostril in cere
    Landmark("beak_tip",         nx=-0.72, ny=+0.18),   # hooked tip
    Landmark("beak_upper_ridge", nx=-0.60, ny=-0.05),
    Landmark("beak_lower",       nx=-0.58, ny=+0.22),
    Landmark("gape",             nx=-0.38, ny=+0.20),
    Landmark("crown",            nx=+0.08, ny=-0.62),
    Landmark("nape",             nx=+0.55, ny=-0.25),
    Landmark("chin_throat",      nx=-0.14, ny=+0.45),
    Landmark("ear_coverts",      nx=+0.25, ny=-0.05),   # feathers covering ear
    Landmark("cheek",            nx=+0.05, ny=+0.12),
]

FEATURE_ZONES = [
    FeatureZone("near_eye",  "near_eye",          radius_nx=0.20, radius_ny=0.14,
                error_weight=8.0, stroke_size_scale=0.48, jitter_scale=0.52, wet_blend_scale=0.48),
    FeatureZone("far_eye",   "far_eye",            radius_nx=0.16, radius_ny=0.11,
                error_weight=6.5, stroke_size_scale=0.52, jitter_scale=0.56, wet_blend_scale=0.52),
    FeatureZone("supraorbital_ridge", "supraorbital_ridge_near", radius_nx=0.30, radius_ny=0.08,
                error_weight=4.0, stroke_size_scale=0.58),   # the fierce brow is distinctive
    FeatureZone("beak",      "beak_tip",           radius_nx=0.30, radius_ny=0.18,
                error_weight=5.5, stroke_size_scale=0.50, jitter_scale=0.58),
    FeatureZone("cere",      "cere",               radius_nx=0.16, radius_ny=0.10,
                error_weight=4.0, stroke_size_scale=0.55),   # colour and texture of cere
    FeatureZone("nare",      "nare",               radius_nx=0.10, radius_ny=0.08,
                error_weight=3.5, stroke_size_scale=0.48),
    FeatureZone("ear_coverts","ear_coverts",        radius_nx=0.28, radius_ny=0.22,
                error_weight=2.0, stroke_size_scale=0.70),
]

FLOW_ZONES = [
    FlowZone("crown", "diagonal",
             {"nx_factor": 0.45, "ny_factor": -0.35, "anchor_nx": +0.08, "anchor_ny": -0.55},
             weight_sigma_nx=0.38, weight_sigma_ny=0.24),
    FlowZone("near_eye_socket", "orbital",
             {"orbit_anchor": "near_eye", "orbit_nx": -0.20, "orbit_ny": -0.15},
             weight_sigma_nx=0.20, weight_sigma_ny=0.16),
    FlowZone("far_eye_socket", "orbital",
             {"orbit_anchor": "far_eye", "orbit_nx": +0.18, "orbit_ny": -0.18},
             weight_sigma_nx=0.16, weight_sigma_ny=0.13),
    # Beak — feathers fan toward the cere
    FlowZone("beak_region", "diagonal",
             {"nx_factor": -0.70, "ny_factor": 0.20, "anchor_nx": -0.48, "anchor_ny": +0.06},
             weight_sigma_nx=0.26, weight_sigma_ny=0.20),
    # Cheek / ear coverts — feathers stream rearward
    FlowZone("cheek", "diagonal",
             {"nx_factor": 0.62, "ny_factor": 0.20, "anchor_nx": +0.08, "anchor_ny": +0.05},
             weight_sigma_nx=0.35, weight_sigma_ny=0.28),
    # Throat — feathers point straight down
    FlowZone("throat", "diagonal",
             {"nx_factor": -0.06, "ny_factor": 0.98, "anchor_nx": -0.10, "anchor_ny": +0.40},
             weight_sigma_nx=0.28, weight_sigma_ny=0.22),
    FlowZone("nape", "diagonal",
             {"nx_factor": 0.40, "ny_factor": 0.45, "anchor_nx": +0.48, "anchor_ny": -0.20},
             weight_sigma_nx=0.22, weight_sigma_ny=0.25),
]

PROPORTIONS = {
    "beak_length_fraction":    0.42,
    "eye_diameter_fraction":   0.20,
    "beak_depth_fraction":     0.18,   # strongly laterally compressed
    "aspect_ratio":            0.82,
}

RAPTOR = SubjectAnatomy(
    subject_id="raptor",
    display_name="Raptor / Eagle / Hawk (3/4 Profile)",
    landmarks=LANDMARKS, feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES, proportions=PROPORTIONS,
)
