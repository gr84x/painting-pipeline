"""
Heron / crane head anatomy — side profile (great blue heron / grey heron type).

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
In side profile: nx=-1 = bill tip (forward), nx=+1 = nape/crest (rear).
ny=-1 = crown plumes, ny=+1 = chin/throat.

Herons have an extremely long, dagger-shaped bill (longer than the head),
a distinctive black stripe running from the eye to long head plumes at the
nape, and a long sinuous neck. The bill tip is often a contrasting colour.
The yellow/orange iris is striking. Crown is flat with long nuptial plumes.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("eye",              nx=-0.05, ny=-0.15),
    Landmark("eye_stripe_front", nx=-0.25, ny=-0.18),   # black loral stripe
    Landmark("eye_stripe_rear",  nx=+0.28, ny=-0.20),
    Landmark("bill_tip",         nx=-0.88, ny=+0.05),
    Landmark("bill_base_upper",  nx=-0.15, ny=-0.05),
    Landmark("bill_base_lower",  nx=-0.15, ny=+0.08),
    Landmark("nare",             nx=-0.50, ny=-0.03),
    Landmark("crown",            nx=+0.05, ny=-0.55),
    Landmark("nape_plume_base",  nx=+0.38, ny=-0.30),
    Landmark("nape_plume_tip",   nx=+0.62, ny=-0.60),   # the trailing plumes
    Landmark("chin",             nx=-0.20, ny=+0.35),
    Landmark("throat",           nx=+0.05, ny=+0.55),
    Landmark("neck_front",       nx=-0.10, ny=+0.72),
]

FEATURE_ZONES = [
    FeatureZone("eye",          "eye",           radius_nx=0.14, radius_ny=0.10,
                error_weight=9.0, stroke_size_scale=0.45, jitter_scale=0.50, wet_blend_scale=0.45),
    FeatureZone("eye_stripe",   "eye_stripe_front", radius_nx=0.38, radius_ny=0.08,
                error_weight=4.5, stroke_size_scale=0.55),   # bold black stripe
    FeatureZone("bill",         "bill_tip",       radius_nx=0.60, radius_ny=0.08,
                error_weight=5.0, stroke_size_scale=0.48, jitter_scale=0.58),
    FeatureZone("bill_tip_colour","bill_tip",     radius_nx=0.12, radius_ny=0.10,
                error_weight=4.0, stroke_size_scale=0.42),   # contrasting colour
    FeatureZone("nape_plumes",  "nape_plume_tip", radius_nx=0.28, radius_ny=0.30,
                error_weight=3.0, stroke_size_scale=0.58),
    FeatureZone("crown",        "crown",          radius_nx=0.30, radius_ny=0.20,
                error_weight=2.5, stroke_size_scale=0.62),
]

FLOW_ZONES = [
    FlowZone("eye_socket", "orbital",
             {"orbit_anchor": "eye", "orbit_nx": -0.05, "orbit_ny": -0.15},
             weight_sigma_nx=0.14, weight_sigma_ny=0.12),
    # Black eye stripe — strokes run along the stripe (horizontal in profile)
    FlowZone("eye_stripe", "fixed",
             {"radians": 0.0, "anchor_nx": 0.00, "anchor_ny": -0.18},
             weight_sigma_nx=0.40, weight_sigma_ny=0.08),
    # Bill — long horizontal strokes along the bill length
    FlowZone("bill", "fixed",
             {"radians": 0.02, "anchor_nx": -0.50, "anchor_ny": +0.01},
             weight_sigma_nx=0.48, weight_sigma_ny=0.10),
    # Crown — flat feathers lying rearward
    FlowZone("crown", "diagonal",
             {"nx_factor": 0.55, "ny_factor": -0.10, "anchor_nx": +0.05, "anchor_ny": -0.50},
             weight_sigma_nx=0.35, weight_sigma_ny=0.20),
    # Nape plumes — stream backward and downward
    FlowZone("nape_plumes", "diagonal",
             {"nx_factor": 0.40, "ny_factor": 0.65, "anchor_nx": +0.50, "anchor_ny": -0.45},
             weight_sigma_nx=0.22, weight_sigma_ny=0.30),
    # Throat — feathers point downward into neck
    FlowZone("throat", "diagonal",
             {"nx_factor": -0.04, "ny_factor": 0.99, "anchor_nx": +0.00, "anchor_ny": +0.55},
             weight_sigma_nx=0.28, weight_sigma_ny=0.22),
]

PROPORTIONS = {
    "bill_length_fraction":    0.88,   # bill longer than head
    "eye_diameter_fraction":   0.12,
    "neck_length_multiplier":  2.50,   # very long neck
    "aspect_ratio":            2.10,   # very elongated in profile
}

HERON = SubjectAnatomy(
    subject_id="heron",
    display_name="Heron / Crane (Side Profile)",
    landmarks=LANDMARKS, feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES, proportions=PROPORTIONS,
)
