"""
Owl head anatomy — frontal face (great horned / barn owl type).

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
Bounding ellipse: ear tufts / crown to chin (ny), face disc edge to edge (nx).

Owls are unique among painting subjects: the facial disc is a concave
parabolic reflector for sound, and it defines the entire compositional
structure of the head. Eyes are enormous, perfectly forward-facing, and
immobile — the iris and pupil are the painting's focal point. The beak
is short and hooked, often partly hidden in facial feathers. Feathers
radiate outward from the beak/eye centre in concentric arcs.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    # Eyes — huge, forward-facing, dominant
    Landmark("left_eye",          nx=-0.28, ny=-0.05),
    Landmark("right_eye",         nx=+0.28, ny=-0.05),
    Landmark("left_iris_centre",  nx=-0.28, ny=-0.05),
    Landmark("right_iris_centre", nx=+0.28, ny=-0.05),
    # Beak (short, hooked)
    Landmark("beak_tip",          nx= 0.00, ny=+0.22),
    Landmark("beak_base",         nx= 0.00, ny=+0.10),
    Landmark("left_beak_corner",  nx=-0.06, ny=+0.14),
    Landmark("right_beak_corner", nx=+0.06, ny=+0.14),
    # Facial disc edge — the radiating boundary
    Landmark("disc_top",          nx= 0.00, ny=-0.62),
    Landmark("disc_left",         nx=-0.88, ny=+0.05),
    Landmark("disc_right",        nx=+0.88, ny=+0.05),
    Landmark("disc_bottom",       nx= 0.00, ny=+0.70),
    # Ear tufts (great horned owl; absent in barn owl)
    Landmark("left_ear_tuft",     nx=-0.28, ny=-0.80),
    Landmark("right_ear_tuft",    nx=+0.28, ny=-0.80),
    # Crown
    Landmark("crown",             nx= 0.00, ny=-0.68),
    Landmark("chin",              nx= 0.00, ny=+0.62),
]

FEATURE_ZONES = [
    # Eyes are everything in an owl portrait
    FeatureZone("left_eye",   "left_eye",  radius_nx=0.28, radius_ny=0.22,
                error_weight=9.0, stroke_size_scale=0.45, jitter_scale=0.50, wet_blend_scale=0.45),
    FeatureZone("right_eye",  "right_eye", radius_nx=0.28, radius_ny=0.22,
                error_weight=9.0, stroke_size_scale=0.45, jitter_scale=0.50, wet_blend_scale=0.45),
    # Beak — small but high-contrast and structurally important
    FeatureZone("beak",       "beak_tip",  radius_nx=0.14, radius_ny=0.14,
                error_weight=5.0, stroke_size_scale=0.52, jitter_scale=0.58),
    # Facial disc boundary — the radiating feather pattern
    FeatureZone("disc_edge_left",  "disc_left",  radius_nx=0.18, radius_ny=0.55,
                error_weight=2.5, stroke_size_scale=0.72),
    FeatureZone("disc_edge_right", "disc_right", radius_nx=0.18, radius_ny=0.55,
                error_weight=2.5, stroke_size_scale=0.72),
    # Ear tufts — silhouette-defining
    FeatureZone("left_ear_tuft",  "left_ear_tuft",  radius_nx=0.16, radius_ny=0.18,
                error_weight=2.0, stroke_size_scale=0.68),
    FeatureZone("right_ear_tuft", "right_ear_tuft", radius_nx=0.16, radius_ny=0.18,
                error_weight=2.0, stroke_size_scale=0.68),
]

FLOW_ZONES = [
    # Facial disc — feathers radiate outward from beak/eye centre
    # Modelled as orbital around the face centre
    FlowZone("disc_left_upper", "orbital",
             {"orbit_anchor": "beak_base", "orbit_nx": 0.00, "orbit_ny": +0.10},
             weight_sigma_nx=0.55, weight_sigma_ny=0.55),
    # Left eye socket — feathers orbit the eye tightly
    FlowZone("left_eye_socket", "orbital",
             {"orbit_anchor": "left_eye", "orbit_nx": -0.28, "orbit_ny": -0.05},
             weight_sigma_nx=0.24, weight_sigma_ny=0.22),
    # Right eye socket
    FlowZone("right_eye_socket", "orbital",
             {"orbit_anchor": "right_eye", "orbit_nx": +0.28, "orbit_ny": -0.05},
             weight_sigma_nx=0.24, weight_sigma_ny=0.22),
    # Crown — feathers lie flat, running rearward
    FlowZone("crown", "diagonal",
             {"nx_factor": 0.10, "ny_factor": -0.98, "anchor_nx": 0.00, "anchor_ny": -0.65},
             weight_sigma_nx=0.42, weight_sigma_ny=0.18),
    # Ear tufts — vertical strokes
    FlowZone("left_ear_tuft", "fixed",
             {"radians": math.pi * 0.52, "anchor_nx": -0.28, "anchor_ny": -0.80},
             weight_sigma_nx=0.12, weight_sigma_ny=0.16),
    FlowZone("right_ear_tuft", "fixed",
             {"radians": math.pi * 0.48, "anchor_nx": +0.28, "anchor_ny": -0.80},
             weight_sigma_nx=0.12, weight_sigma_ny=0.16),
    # Chin / throat — feathers point downward
    FlowZone("chin", "diagonal",
             {"nx_factor": 0.08, "ny_factor": 0.95, "anchor_nx": 0.00, "anchor_ny": +0.60},
             weight_sigma_nx=0.40, weight_sigma_ny=0.18),
]

PROPORTIONS = {
    "eye_diameter_fraction":      0.32,   # enormous eyes
    "interocular_distance_nx":    0.56,
    "beak_length_fraction":       0.15,   # short beak
    "facial_disc_diameter_nx":    1.80,   # disc extends beyond skull
    "ear_tuft_height_fraction":   0.20,
    "aspect_ratio":               0.92,
}

OWL = SubjectAnatomy(
    subject_id="owl",
    display_name="Owl (Frontal)",
    landmarks=LANDMARKS,
    feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES,
    proportions=PROPORTIONS,
)
