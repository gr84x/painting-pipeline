"""
Bear head anatomy — frontal or slight 3/4 face (brown / black bear type).

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
Bounding ellipse: top of skull to chin (ny), ear-to-ear (nx).

Bears have a very broad, domed skull, a moderately long muzzle that is
distinctly lighter in colour, small round ears set wide apart at the top
of the skull, and relatively small eyes. The muzzle colour contrast and
texture are important painting features. The forehead is wide and domed.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    Landmark("left_eye",          nx=-0.24, ny=-0.05),
    Landmark("right_eye",         nx=+0.24, ny=-0.05),
    Landmark("nose_pad",          nx= 0.00, ny=+0.38),
    Landmark("left_nostril",      nx=-0.10, ny=+0.34),
    Landmark("right_nostril",     nx=+0.10, ny=+0.34),
    Landmark("muzzle_centre",     nx= 0.00, ny=+0.28),
    Landmark("upper_lip",         nx= 0.00, ny=+0.50),
    Landmark("mouth_corner_left", nx=-0.20, ny=+0.48),
    Landmark("mouth_corner_right",nx=+0.20, ny=+0.48),
    Landmark("chin",              nx= 0.00, ny=+0.72),
    Landmark("forehead",          nx= 0.00, ny=-0.38),
    Landmark("crown",             nx= 0.00, ny=-0.65),
    Landmark("left_ear",          nx=-0.62, ny=-0.58),
    Landmark("right_ear",         nx=+0.62, ny=-0.58),
    Landmark("left_cheek",        nx=-0.48, ny=+0.18),
    Landmark("right_cheek",       nx=+0.48, ny=+0.18),
    # Muzzle boundary — the pale patch around the nose
    Landmark("muzzle_edge_left",  nx=-0.35, ny=+0.18),
    Landmark("muzzle_edge_right", nx=+0.35, ny=+0.18),
]

FEATURE_ZONES = [
    FeatureZone("left_eye",   "left_eye",   radius_nx=0.18, radius_ny=0.12,
                error_weight=7.0, stroke_size_scale=0.55, jitter_scale=0.60, wet_blend_scale=0.55),
    FeatureZone("right_eye",  "right_eye",  radius_nx=0.18, radius_ny=0.12,
                error_weight=7.0, stroke_size_scale=0.55, jitter_scale=0.60, wet_blend_scale=0.55),
    FeatureZone("nose_pad",   "nose_pad",   radius_nx=0.18, radius_ny=0.14,
                error_weight=6.0, stroke_size_scale=0.52, jitter_scale=0.58),
    # Muzzle pale patch — the colour boundary here is a key likeness feature
    FeatureZone("muzzle",     "muzzle_centre", radius_nx=0.40, radius_ny=0.28,
                error_weight=3.5, stroke_size_scale=0.68),
    FeatureZone("mouth",      "upper_lip",     radius_nx=0.28, radius_ny=0.14,
                error_weight=3.0, stroke_size_scale=0.65),
    # Bear ears are small and round, set as colour spots
    FeatureZone("left_ear",   "left_ear",   radius_nx=0.16, radius_ny=0.12,
                error_weight=2.0, stroke_size_scale=0.72),
    FeatureZone("right_ear",  "right_ear",  radius_nx=0.16, radius_ny=0.12,
                error_weight=2.0, stroke_size_scale=0.72),
]

FLOW_ZONES = [
    # Broad domed forehead — strokes radiate outward from crown
    FlowZone("forehead", "diagonal",
             {"nx_factor": 0.14, "ny_factor": 1.0, "anchor_nx": 0.00, "anchor_ny": -0.42},
             weight_sigma_nx=0.65, weight_sigma_ny=0.28),
    FlowZone("left_eye_socket", "orbital",
             {"orbit_anchor": "left_eye", "orbit_nx": -0.24, "orbit_ny": -0.05},
             weight_sigma_nx=0.20, weight_sigma_ny=0.16),
    FlowZone("right_eye_socket", "orbital",
             {"orbit_anchor": "right_eye", "orbit_nx": +0.24, "orbit_ny": -0.05},
             weight_sigma_nx=0.20, weight_sigma_ny=0.16),
    # Cheeks — broad, strokes fan outward and downward
    FlowZone("left_cheek", "diagonal",
             {"nx_factor": -0.42, "ny_factor": 0.85, "anchor_nx": -0.42, "anchor_ny": +0.20},
             weight_sigma_nx=0.35, weight_sigma_ny=0.32),
    FlowZone("right_cheek", "diagonal",
             {"nx_factor": +0.42, "ny_factor": 0.85, "anchor_nx": +0.42, "anchor_ny": +0.20},
             weight_sigma_nx=0.35, weight_sigma_ny=0.32),
    # Muzzle — strokes run downward, following guard-hair direction
    FlowZone("muzzle", "diagonal",
             {"nx_factor": 0.06, "ny_factor": 0.94, "anchor_nx": 0.00, "anchor_ny": +0.32},
             weight_sigma_nx=0.38, weight_sigma_ny=0.24),
    # Ears — small, circular; strokes orbit the ear base
    FlowZone("left_ear", "orbital",
             {"orbit_anchor": "left_ear", "orbit_nx": -0.62, "orbit_ny": -0.58},
             weight_sigma_nx=0.14, weight_sigma_ny=0.14),
    FlowZone("right_ear", "orbital",
             {"orbit_anchor": "right_ear", "orbit_nx": +0.62, "orbit_ny": -0.58},
             weight_sigma_nx=0.14, weight_sigma_ny=0.14),
]

PROPORTIONS = {
    "muzzle_length_fraction":  0.35,
    "eye_diameter_fraction":   0.10,   # small eyes relative to massive skull
    "ear_diameter_fraction":   0.12,   # small, round ears
    "interocular_distance_nx": 0.48,
    "muzzle_width_fraction":   0.70,   # broad muzzle
    "aspect_ratio":            1.05,   # slightly wider than tall
}

BEAR = SubjectAnatomy(
    subject_id="bear",
    display_name="Bear (Frontal)",
    landmarks=LANDMARKS,
    feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES,
    proportions=PROPORTIONS,
)
