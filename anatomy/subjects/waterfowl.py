"""
Waterfowl head anatomy — side profile (duck / mallard type).

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
In side profile: nx=-1 = bill tip, nx=+1 = nape. ny=-1 = crown, ny=+1 = chin.

Ducks have a flat-topped bill (lamellate, with a nail at the tip), a smooth
rounded head, an eye set high, and an iridescent speculum patch on the wing.
In portrait the head is the subject. The iridescent head (mallard drake) or
streaked brown pattern (hen) defines the colour challenge. The bill colour and
nail are important identifying features; the eye has a sharp, alert quality.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("eye",          nx=-0.05, ny=-0.20),
    Landmark("bill_tip",     nx=-0.82, ny=+0.12),
    Landmark("bill_nail",    nx=-0.78, ny=+0.08),    # hard tip of bill
    Landmark("bill_base",    nx=-0.22, ny=+0.08),
    Landmark("bill_centre",  nx=-0.52, ny=+0.08),
    Landmark("nostril",      nx=-0.48, ny=-0.02),
    Landmark("gape",         nx=-0.25, ny=+0.16),
    Landmark("crown",        nx=+0.05, ny=-0.55),
    Landmark("nape",         nx=+0.55, ny=-0.22),
    Landmark("chin",         nx=-0.20, ny=+0.30),
    Landmark("throat",       nx=+0.08, ny=+0.50),
    Landmark("neck_ring",    nx=+0.18, ny=+0.62),    # white neck ring (drake)
    Landmark("cheek",        nx=+0.10, ny=+0.02),
]

FEATURE_ZONES = [
    FeatureZone("eye",       "eye",       radius_nx=0.14, radius_ny=0.12,
                error_weight=9.0, stroke_size_scale=0.46, jitter_scale=0.50, wet_blend_scale=0.46),
    FeatureZone("bill",      "bill_centre",radius_nx=0.42, radius_ny=0.12,
                error_weight=4.5, stroke_size_scale=0.55, jitter_scale=0.60),
    FeatureZone("bill_nail", "bill_nail", radius_nx=0.10, radius_ny=0.10,
                error_weight=4.0, stroke_size_scale=0.44),
    # Iridescent head — the green/purple shift is the signature feature of a drake
    FeatureZone("head_iridescence", "cheek", radius_nx=0.65, radius_ny=0.48,
                error_weight=3.0, stroke_size_scale=0.60),
    FeatureZone("neck_ring", "neck_ring", radius_nx=0.40, radius_ny=0.12,
                error_weight=3.5, stroke_size_scale=0.55),   # white collar boundary
    FeatureZone("crown",     "crown",     radius_nx=0.38, radius_ny=0.28,
                error_weight=2.5, stroke_size_scale=0.65),
]

FLOW_ZONES = [
    FlowZone("crown", "diagonal",
             {"nx_factor": 0.50, "ny_factor": -0.15, "anchor_nx": +0.05, "anchor_ny": -0.50},
             weight_sigma_nx=0.40, weight_sigma_ny=0.25),
    FlowZone("eye_socket", "orbital",
             {"orbit_anchor": "eye", "orbit_nx": -0.05, "orbit_ny": -0.20},
             weight_sigma_nx=0.15, weight_sigma_ny=0.13),
    # Bill — flat horizontal strokes along the lamellate surface
    FlowZone("bill", "fixed",
             {"radians": 0.04, "anchor_nx": -0.50, "anchor_ny": +0.08},
             weight_sigma_nx=0.44, weight_sigma_ny=0.10),
    FlowZone("cheek", "diagonal",
             {"nx_factor": 0.55, "ny_factor": 0.15, "anchor_nx": +0.10, "anchor_ny": 0.00},
             weight_sigma_nx=0.38, weight_sigma_ny=0.30),
    FlowZone("throat", "diagonal",
             {"nx_factor": -0.04, "ny_factor": 0.98, "anchor_nx": +0.06, "anchor_ny": +0.46},
             weight_sigma_nx=0.28, weight_sigma_ny=0.22),
    FlowZone("nape", "diagonal",
             {"nx_factor": 0.38, "ny_factor": 0.42, "anchor_nx": +0.48, "anchor_ny": -0.18},
             weight_sigma_nx=0.22, weight_sigma_ny=0.24),
]

PROPORTIONS = {
    "bill_length_fraction":   0.55,
    "bill_width_fraction":    0.18,   # broad, flat
    "eye_diameter_fraction":  0.12,
    "aspect_ratio":           1.40,
}

WATERFOWL = SubjectAnatomy(
    subject_id="waterfowl",
    display_name="Waterfowl / Duck (Side Profile)",
    landmarks=LANDMARKS, feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES, proportions=PROPORTIONS,
)
