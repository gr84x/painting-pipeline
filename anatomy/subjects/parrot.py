"""
Parrot head anatomy — frontal face (psittacine type: macaw, cockatoo, etc.).

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
Bounding ellipse: crest top to chin (ny), cheek patch to cheek patch (nx).

Parrots have a distinctively curved, powerful beak (both halves hook),
a round skull, and large intelligent eyes with prominent, bare periorbital
skin. Cheek patches are vibrant colour regions crucial to species identity.
Crests (cockatiels, cockatoos) extend above the skull and define silhouette.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("left_eye",          nx=-0.32, ny=-0.05),
    Landmark("right_eye",         nx=+0.32, ny=-0.05),
    Landmark("left_periorbital",  nx=-0.38, ny=-0.05),   # bare skin ring
    Landmark("right_periorbital", nx=+0.38, ny=-0.05),
    Landmark("upper_beak_tip",    nx= 0.00, ny=+0.32),
    Landmark("upper_beak_base",   nx= 0.00, ny=+0.10),
    Landmark("lower_beak_tip",    nx= 0.00, ny=+0.40),
    Landmark("cere",              nx= 0.00, ny=+0.08),
    Landmark("left_cheek_patch",  nx=-0.52, ny=+0.12),
    Landmark("right_cheek_patch", nx=+0.52, ny=+0.12),
    Landmark("crown",             nx= 0.00, ny=-0.50),
    Landmark("crest_base",        nx= 0.00, ny=-0.58),
    Landmark("crest_tip",         nx= 0.00, ny=-0.88),   # optional; present in cockatoos
    Landmark("chin",              nx= 0.00, ny=+0.58),
    Landmark("nape",              nx= 0.00, ny=-0.30),
]

FEATURE_ZONES = [
    FeatureZone("left_eye",         "left_eye",         radius_nx=0.24, radius_ny=0.18,
                error_weight=8.0, stroke_size_scale=0.50, jitter_scale=0.54, wet_blend_scale=0.50),
    FeatureZone("right_eye",        "right_eye",        radius_nx=0.24, radius_ny=0.18,
                error_weight=8.0, stroke_size_scale=0.50, jitter_scale=0.54, wet_blend_scale=0.50),
    FeatureZone("left_periorbital", "left_periorbital", radius_nx=0.22, radius_ny=0.14,
                error_weight=4.5, stroke_size_scale=0.58),   # bare skin — colour & texture
    FeatureZone("right_periorbital","right_periorbital", radius_nx=0.22, radius_ny=0.14,
                error_weight=4.5, stroke_size_scale=0.58),
    FeatureZone("beak",             "upper_beak_tip",   radius_nx=0.22, radius_ny=0.28,
                error_weight=6.0, stroke_size_scale=0.50, jitter_scale=0.56),
    FeatureZone("left_cheek_patch", "left_cheek_patch", radius_nx=0.28, radius_ny=0.22,
                error_weight=3.5, stroke_size_scale=0.62),
    FeatureZone("right_cheek_patch","right_cheek_patch",radius_nx=0.28, radius_ny=0.22,
                error_weight=3.5, stroke_size_scale=0.62),
    FeatureZone("crest",            "crest_tip",        radius_nx=0.30, radius_ny=0.22,
                error_weight=2.5, stroke_size_scale=0.65),
]

FLOW_ZONES = [
    FlowZone("crown", "diagonal",
             {"nx_factor": 0.08, "ny_factor": 1.0, "anchor_nx": 0.00, "anchor_ny": -0.48},
             weight_sigma_nx=0.50, weight_sigma_ny=0.22),
    FlowZone("crest", "diagonal",
             {"nx_factor": 0.06, "ny_factor": 0.98, "anchor_nx": 0.00, "anchor_ny": -0.75},
             weight_sigma_nx=0.24, weight_sigma_ny=0.18),
    FlowZone("left_eye_socket", "orbital",
             {"orbit_anchor": "left_eye", "orbit_nx": -0.32, "orbit_ny": -0.05},
             weight_sigma_nx=0.24, weight_sigma_ny=0.20),
    FlowZone("right_eye_socket", "orbital",
             {"orbit_anchor": "right_eye", "orbit_nx": +0.32, "orbit_ny": -0.05},
             weight_sigma_nx=0.24, weight_sigma_ny=0.20),
    FlowZone("left_cheek", "diagonal",
             {"nx_factor": -0.50, "ny_factor": 0.60, "anchor_nx": -0.46, "anchor_ny": +0.15},
             weight_sigma_nx=0.30, weight_sigma_ny=0.25),
    FlowZone("right_cheek", "diagonal",
             {"nx_factor": +0.50, "ny_factor": 0.60, "anchor_nx": +0.46, "anchor_ny": +0.15},
             weight_sigma_nx=0.30, weight_sigma_ny=0.25),
    FlowZone("chin", "diagonal",
             {"nx_factor": 0.05, "ny_factor": 0.95, "anchor_nx": 0.00, "anchor_ny": +0.55},
             weight_sigma_nx=0.35, weight_sigma_ny=0.16),
]

PROPORTIONS = {
    "beak_length_fraction":    0.38,
    "beak_depth_fraction":     0.28,   # deep, powerful beak
    "eye_diameter_fraction":   0.22,
    "cheek_patch_width_nx":    0.56,
    "aspect_ratio":            0.90,
}

PARROT = SubjectAnatomy(
    subject_id="parrot",
    display_name="Parrot (Frontal)",
    landmarks=LANDMARKS, feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES, proportions=PROPORTIONS,
)
