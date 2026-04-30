"""
Sea turtle anatomy — dorsal / slight 3/4 overhead view.

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
The bounding ellipse spans the full carapace (shell) width and length.
The head extends slightly forward (negative ny) from the shell.

The carapace scute pattern is the dominant visual feature — the geometric
arrangement of large central scutes (vertebrals + costals) surrounded by
smaller marginal scutes creates the signature texture. The head is small
relative to the shell. Flippers are paddle-shaped and powerful.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    # Head (protruding from shell front)
    Landmark("head_centre",       nx= 0.00, ny=-0.72),
    Landmark("left_eye",          nx=-0.12, ny=-0.76),
    Landmark("right_eye",         nx=+0.12, ny=-0.76),
    Landmark("mouth",             nx= 0.00, ny=-0.82),
    Landmark("nostril",           nx= 0.00, ny=-0.80),
    Landmark("head_rear",         nx= 0.00, ny=-0.65),
    # Carapace (shell) landmarks
    Landmark("nuchal_scute",      nx= 0.00, ny=-0.60),   # front-centre shell
    Landmark("vertebral_1",       nx= 0.00, ny=-0.42),
    Landmark("vertebral_3",       nx= 0.00, ny= 0.00),   # midpoint
    Landmark("vertebral_5",       nx= 0.00, ny=+0.42),
    Landmark("pygal_scute",       nx= 0.00, ny=+0.62),   # rear-centre
    Landmark("left_costal_1",     nx=-0.32, ny=-0.35),
    Landmark("right_costal_1",    nx=+0.32, ny=-0.35),
    Landmark("left_costal_3",     nx=-0.42, ny=+0.20),
    Landmark("right_costal_3",    nx=+0.42, ny=+0.20),
    Landmark("left_marginal",     nx=-0.65, ny= 0.00),
    Landmark("right_marginal",    nx=+0.65, ny= 0.00),
    # Flippers
    Landmark("front_left_flipper", nx=-0.80, ny=-0.38),
    Landmark("front_right_flipper",nx=+0.80, ny=-0.38),
    Landmark("rear_left_flipper",  nx=-0.60, ny=+0.62),
    Landmark("rear_right_flipper", nx=+0.60, ny=+0.62),
]

FEATURE_ZONES = [
    # Eyes — tiny but critical
    FeatureZone("left_eye",    "left_eye",     radius_nx=0.10, radius_ny=0.08,
                error_weight=9.0, stroke_size_scale=0.40, jitter_scale=0.48, wet_blend_scale=0.42),
    FeatureZone("right_eye",   "right_eye",    radius_nx=0.10, radius_ny=0.08,
                error_weight=9.0, stroke_size_scale=0.40, jitter_scale=0.48, wet_blend_scale=0.42),
    FeatureZone("head",        "head_centre",  radius_nx=0.20, radius_ny=0.16,
                error_weight=5.0, stroke_size_scale=0.50),
    # Scute pattern — the visual signature; each scute boundary is important
    FeatureZone("vertebral_scutes", "vertebral_3", radius_nx=0.20, radius_ny=0.60,
                error_weight=4.0, stroke_size_scale=0.58),
    FeatureZone("left_costal_scutes","left_costal_3", radius_nx=0.28, radius_ny=0.42,
                error_weight=3.5, stroke_size_scale=0.60),
    FeatureZone("right_costal_scutes","right_costal_3",radius_nx=0.28, radius_ny=0.42,
                error_weight=3.5, stroke_size_scale=0.60),
    FeatureZone("marginal_scutes","left_marginal",radius_nx=0.18, radius_ny=0.65,
                error_weight=2.5, stroke_size_scale=0.65),
    FeatureZone("flippers",    "front_left_flipper", radius_nx=0.22, radius_ny=0.20,
                error_weight=2.0, stroke_size_scale=0.70),
]

FLOW_ZONES = [
    FlowZone("left_eye_socket", "orbital",
             {"orbit_anchor": "left_eye", "orbit_nx": -0.12, "orbit_ny": -0.76},
             weight_sigma_nx=0.10, weight_sigma_ny=0.09),
    FlowZone("right_eye_socket", "orbital",
             {"orbit_anchor": "right_eye", "orbit_nx": +0.12, "orbit_ny": -0.76},
             weight_sigma_nx=0.10, weight_sigma_ny=0.09),
    # Shell scutes — strokes follow scute boundaries (roughly radial from centre)
    FlowZone("shell_upper_left", "diagonal",
             {"nx_factor": -0.45, "ny_factor": -0.60, "anchor_nx": -0.22, "anchor_ny": -0.25},
             weight_sigma_nx=0.30, weight_sigma_ny=0.35),
    FlowZone("shell_upper_right", "diagonal",
             {"nx_factor": +0.45, "ny_factor": -0.60, "anchor_nx": +0.22, "anchor_ny": -0.25},
             weight_sigma_nx=0.30, weight_sigma_ny=0.35),
    FlowZone("shell_lower_left", "diagonal",
             {"nx_factor": -0.45, "ny_factor": 0.60, "anchor_nx": -0.28, "anchor_ny": +0.25},
             weight_sigma_nx=0.30, weight_sigma_ny=0.35),
    FlowZone("shell_lower_right", "diagonal",
             {"nx_factor": +0.45, "ny_factor": 0.60, "anchor_nx": +0.28, "anchor_ny": +0.25},
             weight_sigma_nx=0.30, weight_sigma_ny=0.35),
    # Vertebral centre — strokes run along spine axis
    FlowZone("vertebral_axis", "fixed",
             {"radians": math.pi / 2, "anchor_nx": 0.00, "anchor_ny": 0.00},
             weight_sigma_nx=0.16, weight_sigma_ny=0.65),
    # Front flippers — strokes follow flipper length
    FlowZone("front_flippers", "diagonal",
             {"nx_factor": -0.80, "ny_factor": -0.45, "anchor_nx": -0.65, "anchor_ny": -0.38},
             weight_sigma_nx=0.20, weight_sigma_ny=0.18),
]

PROPORTIONS = {
    "head_to_shell_ratio":     0.25,
    "shell_aspect_ratio":      0.75,   # slightly longer than wide
    "flipper_span_fraction":   1.60,   # flippers extend beyond shell width
    "scute_count_vertebral":   5,
    "scute_count_costal":      4,
}

SEA_TURTLE = SubjectAnatomy(
    subject_id="sea_turtle",
    display_name="Sea Turtle (Dorsal View)",
    landmarks=LANDMARKS, feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES, proportions=PROPORTIONS,
)
