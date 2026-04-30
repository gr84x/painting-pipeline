"""
Raven / crow head anatomy — 3/4 profile (corvid type).

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
Bounding ellipse: crown to chin (ny), bill tip to nape (nx).

Corvids have a large domed skull (reflecting high intelligence), a straight
strong bill with a slight hook at the tip, bristle feathers at the bill base
(nasal tufts), and a glossy iridescent plumage that shifts between black,
blue, purple, and green depending on light angle. Capturing this iridescence
is the central painting challenge. The eye is dark, intelligent, and alert.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("eye",              nx=-0.10, ny=-0.12),
    Landmark("bill_tip",         nx=-0.62, ny=+0.12),
    Landmark("bill_base_upper",  nx=-0.18, ny=-0.02),
    Landmark("bill_base_lower",  nx=-0.18, ny=+0.10),
    Landmark("nasal_tuft",       nx=-0.28, ny=-0.04),   # bristle feathers at bill base
    Landmark("gape",             nx=-0.22, ny=+0.12),
    Landmark("crown",            nx=+0.05, ny=-0.55),   # large domed skull
    Landmark("nape",             nx=+0.48, ny=-0.20),
    Landmark("throat",           nx=-0.08, ny=+0.42),
    Landmark("chin",             nx=-0.18, ny=+0.30),
    Landmark("ear_region",       nx=+0.18, ny=-0.05),
    Landmark("cheek",            nx=+0.10, ny=+0.15),
]

FEATURE_ZONES = [
    FeatureZone("eye",         "eye",         radius_nx=0.18, radius_ny=0.14,
                error_weight=9.0, stroke_size_scale=0.45, jitter_scale=0.50, wet_blend_scale=0.45),
    FeatureZone("bill",        "bill_tip",    radius_nx=0.34, radius_ny=0.12,
                error_weight=5.0, stroke_size_scale=0.52, jitter_scale=0.58),
    FeatureZone("nasal_tuft",  "nasal_tuft",  radius_nx=0.16, radius_ny=0.10,
                error_weight=3.5, stroke_size_scale=0.52),   # bristly texture
    # Iridescent zones — capture the colour shift (prioritise these areas)
    FeatureZone("crown_iridescence", "crown", radius_nx=0.45, radius_ny=0.28,
                error_weight=3.0, stroke_size_scale=0.60),
    FeatureZone("cheek_iridescence", "cheek", radius_nx=0.38, radius_ny=0.28,
                error_weight=2.5, stroke_size_scale=0.62),
    FeatureZone("throat_iridescence","throat",radius_nx=0.30, radius_ny=0.22,
                error_weight=2.5, stroke_size_scale=0.62),
]

FLOW_ZONES = [
    FlowZone("crown", "diagonal",
             {"nx_factor": 0.42, "ny_factor": -0.28, "anchor_nx": +0.05, "anchor_ny": -0.48},
             weight_sigma_nx=0.45, weight_sigma_ny=0.28),
    FlowZone("eye_socket", "orbital",
             {"orbit_anchor": "eye", "orbit_nx": -0.10, "orbit_ny": -0.12},
             weight_sigma_nx=0.18, weight_sigma_ny=0.15),
    FlowZone("bill_region", "diagonal",
             {"nx_factor": -0.68, "ny_factor": 0.15, "anchor_nx": -0.35, "anchor_ny": +0.04},
             weight_sigma_nx=0.24, weight_sigma_ny=0.14),
    FlowZone("cheek", "diagonal",
             {"nx_factor": 0.55, "ny_factor": 0.25, "anchor_nx": +0.12, "anchor_ny": +0.10},
             weight_sigma_nx=0.38, weight_sigma_ny=0.28),
    FlowZone("throat", "diagonal",
             {"nx_factor": -0.05, "ny_factor": 0.98, "anchor_nx": -0.06, "anchor_ny": +0.38},
             weight_sigma_nx=0.28, weight_sigma_ny=0.22),
    FlowZone("nape", "diagonal",
             {"nx_factor": 0.38, "ny_factor": 0.40, "anchor_nx": +0.45, "anchor_ny": -0.18},
             weight_sigma_nx=0.22, weight_sigma_ny=0.24),
]

PROPORTIONS = {
    "bill_length_fraction": 0.40,
    "skull_dome_fraction":  0.65,   # large braincase
    "eye_diameter_fraction":0.18,
    "aspect_ratio":         0.84,
}

RAVEN = SubjectAnatomy(
    subject_id="raven",
    display_name="Raven / Crow (3/4 Profile)",
    landmarks=LANDMARKS, feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES, proportions=PROPORTIONS,
)
