"""
Horse head anatomy — side profile view.

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
In side profile: nx=-1 = poll (top of skull), nx=+1 = nostril tip.
ny=-1 = top of head, ny=+1 = bottom of jaw.

The horse face is highly elongated — the longest muzzle-to-cranium ratio
of any common painting subject. In true side profile, only one eye is
visible. The eye sits high and far back on the skull. The nostril is large
and expressive. The mouth is set far forward. The ear is upright and
mobile. Forelock hair flows from the poll down the face.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    # Side profile: one eye visible, set high and back
    Landmark("eye",               nx=-0.38, ny=-0.22),
    Landmark("eye_orbit_upper",   nx=-0.38, ny=-0.32),
    # Ear
    Landmark("ear_base",          nx=-0.55, ny=-0.62),
    Landmark("ear_tip",           nx=-0.52, ny=-0.90),
    # Nose and mouth (forward = positive nx in side view)
    Landmark("nostril",           nx=+0.68, ny=+0.10),
    Landmark("nostril_upper",     nx=+0.70, ny=+0.02),
    Landmark("upper_lip",         nx=+0.58, ny=+0.32),
    Landmark("lower_lip",         nx=+0.52, ny=+0.42),
    Landmark("mouth_corner",      nx=+0.30, ny=+0.38),
    # Skull landmarks
    Landmark("poll",              nx=-0.72, ny=-0.50),
    Landmark("forehead",          nx=-0.20, ny=-0.35),
    Landmark("facial_crest",      nx=+0.20, ny=-0.05),   # bony ridge down face
    Landmark("cheek",             nx=-0.08, ny=+0.15),
    Landmark("jaw_angle",         nx=-0.30, ny=+0.55),
    Landmark("chin",              nx=+0.40, ny=+0.62),
    # Forelock insertion
    Landmark("forelock",          nx=-0.55, ny=-0.72),
]

FEATURE_ZONES = [
    # The eye is the emotional centrepiece of a horse portrait
    FeatureZone("eye",      "eye",      radius_nx=0.16, radius_ny=0.12,
                error_weight=8.0, stroke_size_scale=0.48, jitter_scale=0.55, wet_blend_scale=0.48),
    FeatureZone("nostril",  "nostril",  radius_nx=0.14, radius_ny=0.14,
                error_weight=5.5, stroke_size_scale=0.55, jitter_scale=0.60),
    FeatureZone("mouth",    "upper_lip",radius_nx=0.22, radius_ny=0.16,
                error_weight=3.5, stroke_size_scale=0.65, jitter_scale=0.70),
    FeatureZone("ear",      "ear_tip",  radius_nx=0.12, radius_ny=0.20,
                error_weight=2.5, stroke_size_scale=0.70),
    # Facial crest — bony ridge catches light; important for likeness
    FeatureZone("facial_crest", "facial_crest", radius_nx=0.55, radius_ny=0.10,
                error_weight=2.0, stroke_size_scale=0.75),
]

FLOW_ZONES = [
    # Forehead / frontal bone — strokes run roughly horizontal (poll to nose)
    FlowZone("forehead", "fixed",
             {"radians": 0.0, "anchor_nx": -0.20, "anchor_ny": -0.35},
             weight_sigma_nx=0.45, weight_sigma_ny=0.28),
    # Forelock — hair falls downward from poll
    FlowZone("forelock", "diagonal",
             {"nx_factor": 0.15, "ny_factor": 0.95, "anchor_nx": -0.52, "anchor_ny": -0.55},
             weight_sigma_nx=0.16, weight_sigma_ny=0.30),
    # Eye socket — strokes orbit the eye
    FlowZone("eye_socket", "orbital",
             {"orbit_anchor": "eye", "orbit_nx": -0.38, "orbit_ny": -0.22},
             weight_sigma_nx=0.16, weight_sigma_ny=0.14),
    # Cheek / masseter — strokes follow the jaw curve downward
    FlowZone("cheek", "diagonal",
             {"nx_factor": 0.10, "ny_factor": 0.92, "anchor_nx": -0.05, "anchor_ny": +0.18},
             weight_sigma_nx=0.42, weight_sigma_ny=0.35),
    # Nose / muzzle — strokes run roughly horizontal toward nostril
    FlowZone("muzzle", "fixed",
             {"radians": 0.04, "anchor_nx": +0.48, "anchor_ny": +0.10},
             weight_sigma_nx=0.28, weight_sigma_ny=0.22),
    # Ear — vertical strokes up into the ear
    FlowZone("ear", "fixed",
             {"radians": math.pi * 0.52, "anchor_nx": -0.53, "anchor_ny": -0.76},
             weight_sigma_nx=0.12, weight_sigma_ny=0.20),
    # Jaw / throat — strokes curve under the jaw toward the throat
    FlowZone("jaw", "diagonal",
             {"nx_factor": -0.25, "ny_factor": 0.90, "anchor_nx": -0.20, "anchor_ny": +0.55},
             weight_sigma_nx=0.38, weight_sigma_ny=0.22),
]

PROPORTIONS = {
    "muzzle_length_fraction":     0.72,   # very long face
    "eye_diameter_fraction":      0.12,
    "ear_height_fraction":        0.30,
    "skull_to_muzzle_ratio":      0.40,   # skull is 40% of total head length
    "nostril_diameter_fraction":  0.10,
    "aspect_ratio":               2.20,   # very elongated (width > height in side view)
}

HORSE = SubjectAnatomy(
    subject_id="horse",
    display_name="Horse (Side Profile)",
    landmarks=LANDMARKS,
    feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES,
    proportions=PROPORTIONS,
)
