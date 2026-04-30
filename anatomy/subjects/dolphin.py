"""
Dolphin head anatomy — side profile (bottlenose type).

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
nx=-1 = rostrum tip, nx=+1 = back of head / blowhole area.

Dolphins have a distinctive melon (forehead bulge), a long beak-like rostrum,
a permanent "smile" formed by the jaw line, and a small eye set mid-head.
Skin is smooth and seamless — flow follows body contour with no texture breaks.
The rostrum-to-melon boundary and the gape line are the key form landmarks.
"""
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("eye",             nx=-0.05, ny=-0.05),
    Landmark("rostrum_tip",     nx=-0.88, ny=+0.08),
    Landmark("gape",            nx=-0.35, ny=+0.14),    # the "smile" corner
    Landmark("upper_jaw_mid",   nx=-0.60, ny=+0.02),
    Landmark("lower_jaw_mid",   nx=-0.60, ny=+0.16),
    Landmark("melon",           nx=+0.12, ny=-0.28),    # the distinctive forehead
    Landmark("melon_peak",      nx=+0.08, ny=-0.40),
    Landmark("blowhole",        nx=+0.32, ny=-0.48),
    Landmark("nape",            nx=+0.55, ny=-0.20),
    Landmark("throat",          nx=+0.10, ny=+0.42),
    Landmark("chin",            nx=-0.45, ny=+0.28),
]

FEATURE_ZONES = [
    FeatureZone("eye",          "eye",          radius_nx=0.14, radius_ny=0.12,
                error_weight=9.0, stroke_size_scale=0.46, jitter_scale=0.50, wet_blend_scale=0.46),
    FeatureZone("gape",         "gape",         radius_nx=0.35, radius_ny=0.12,
                error_weight=4.5, stroke_size_scale=0.55),    # the "smile" line
    FeatureZone("melon",        "melon_peak",   radius_nx=0.35, radius_ny=0.25,
                error_weight=4.0, stroke_size_scale=0.58),    # melon curvature defines the species
    FeatureZone("blowhole",     "blowhole",     radius_nx=0.14, radius_ny=0.10,
                error_weight=3.0, stroke_size_scale=0.52),
    FeatureZone("rostrum",      "upper_jaw_mid",radius_nx=0.45, radius_ny=0.12,
                error_weight=3.5, stroke_size_scale=0.55),
]

FLOW_ZONES = [
    FlowZone("eye_socket", "orbital",
             {"orbit_anchor": "eye", "orbit_nx": -0.05, "orbit_ny": -0.05},
             weight_sigma_nx=0.14, weight_sigma_ny=0.13),
    # Melon — dome-shaped; strokes follow the curved surface contour
    FlowZone("melon", "orbital",
             {"orbit_anchor": "melon", "orbit_nx": +0.12, "orbit_ny": -0.28},
             weight_sigma_nx=0.35, weight_sigma_ny=0.30),
    # Rostrum — long horizontal strokes along the beak
    FlowZone("rostrum", "fixed",
             {"radians": 0.03, "anchor_nx": -0.55, "anchor_ny": +0.06},
             weight_sigma_nx=0.40, weight_sigma_ny=0.14),
    # Body — smooth horizontal strokes following body contour
    FlowZone("body_upper", "fixed",
             {"radians": 0.06, "anchor_nx": +0.20, "anchor_ny": -0.20},
             weight_sigma_nx=0.50, weight_sigma_ny=0.25),
    FlowZone("body_lower", "fixed",
             {"radians": -0.04, "anchor_nx": +0.15, "anchor_ny": +0.28},
             weight_sigma_nx=0.50, weight_sigma_ny=0.22),
]

PROPORTIONS = {
    "rostrum_length_fraction": 0.55,
    "melon_height_fraction":   0.32,
    "eye_diameter_fraction":   0.10,
    "aspect_ratio":            1.80,
}

DOLPHIN = SubjectAnatomy(
    subject_id="dolphin",
    display_name="Dolphin (Side Profile)",
    landmarks=LANDMARKS, feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES, proportions=PROPORTIONS,
)
