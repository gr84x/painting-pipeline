"""
Songbird head anatomy — 3/4 profile (passerine / perching bird type).

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
Bounding ellipse: crown to chin (ny), bill tip to back of head (nx).

Represents small perching birds: robin, sparrow, finch, warbler, thrush.
The head is roughly spherical. The bill is short, conical, and pointed.
The eye is a perfect dark sphere, usually with a pale eye-ring. Feathers
follow distinct tracts — crown, cheek, throat, nape — each with their own
growth direction. Plumage colour boundaries (e.g. red breast / brown back)
are major features and should receive precise stroke placement.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy

LANDMARKS = [
    # Eye — single visible eye in 3/4 profile
    Landmark("eye",              nx=-0.12, ny=-0.10),
    Landmark("eye_ring",         nx=-0.12, ny=-0.10),
    # Bill (short, conical; tip points toward viewer's left)
    Landmark("bill_tip",         nx=-0.68, ny=+0.18),
    Landmark("bill_base_upper",  nx=-0.22, ny=+0.08),
    Landmark("bill_base_lower",  nx=-0.22, ny=+0.16),
    Landmark("gape",             nx=-0.24, ny=+0.14),  # corner of mouth
    # Skull
    Landmark("crown",            nx=+0.10, ny=-0.62),
    Landmark("nape",             nx=+0.55, ny=-0.20),
    Landmark("forehead",         nx=-0.02, ny=-0.42),
    # Face regions
    Landmark("lore",             nx=-0.18, ny=-0.02),  # between eye and bill
    Landmark("cheek",            nx=+0.12, ny=+0.10),
    Landmark("throat",           nx=-0.10, ny=+0.40),
    Landmark("chin",             nx=-0.18, ny=+0.30),
    Landmark("breast_upper",     nx=+0.02, ny=+0.65),
]

FEATURE_ZONES = [
    # The eye is tiny but absolutely critical for a lifelike bird painting
    FeatureZone("eye",          "eye",          radius_nx=0.18, radius_ny=0.16,
                error_weight=9.0, stroke_size_scale=0.40, jitter_scale=0.50, wet_blend_scale=0.42),
    # Bill — small but structurally defining
    FeatureZone("bill",         "bill_tip",     radius_nx=0.30, radius_ny=0.12,
                error_weight=5.5, stroke_size_scale=0.50, jitter_scale=0.58),
    FeatureZone("gape",         "gape",         radius_nx=0.12, radius_ny=0.08,
                error_weight=4.0, stroke_size_scale=0.48, jitter_scale=0.55),
    # Crown — colour patch (often distinct species marker)
    FeatureZone("crown_patch",  "crown",        radius_nx=0.35, radius_ny=0.28,
                error_weight=3.0, stroke_size_scale=0.60),
    # Throat — often strongly coloured (red breast, yellow throat, etc.)
    FeatureZone("throat",       "throat",       radius_nx=0.28, radius_ny=0.24,
                error_weight=3.0, stroke_size_scale=0.62),
    # Cheek patch — important for species identification
    FeatureZone("cheek_patch",  "cheek",        radius_nx=0.26, radius_ny=0.20,
                error_weight=2.5, stroke_size_scale=0.65),
]

FLOW_ZONES = [
    # Crown feathers — lie flat, stream rearward toward nape
    FlowZone("crown", "diagonal",
             {"nx_factor": 0.55, "ny_factor": -0.30, "anchor_nx": +0.12, "anchor_ny": -0.52},
             weight_sigma_nx=0.35, weight_sigma_ny=0.28),
    # Forehead — feathers slope toward bill
    FlowZone("forehead", "diagonal",
             {"nx_factor": -0.40, "ny_factor": 0.50, "anchor_nx": -0.05, "anchor_ny": -0.35},
             weight_sigma_nx=0.22, weight_sigma_ny=0.22),
    # Eye region — feathers orbit the eye (the eye-ring pattern)
    FlowZone("eye_socket", "orbital",
             {"orbit_anchor": "eye", "orbit_nx": -0.12, "orbit_ny": -0.10},
             weight_sigma_nx=0.18, weight_sigma_ny=0.16),
    # Cheek — feathers fan backward from lore
    FlowZone("cheek", "diagonal",
             {"nx_factor": 0.60, "ny_factor": 0.25, "anchor_nx": +0.10, "anchor_ny": +0.08},
             weight_sigma_nx=0.30, weight_sigma_ny=0.25),
    # Throat — feathers point straight downward
    FlowZone("throat", "diagonal",
             {"nx_factor": -0.05, "ny_factor": 0.98, "anchor_nx": -0.08, "anchor_ny": +0.38},
             weight_sigma_nx=0.26, weight_sigma_ny=0.24),
    # Nape — feathers lie rearward and downward
    FlowZone("nape", "diagonal",
             {"nx_factor": 0.45, "ny_factor": 0.50, "anchor_nx": +0.48, "anchor_ny": -0.15},
             weight_sigma_nx=0.22, weight_sigma_ny=0.28),
]

PROPORTIONS = {
    "bill_length_fraction":    0.30,   # bill = ~30% of head length
    "eye_diameter_fraction":   0.18,
    "skull_roundness":         0.90,   # nearly spherical
    "aspect_ratio":            0.85,   # slightly taller than wide in profile
}

SONGBIRD = SubjectAnatomy(
    subject_id="songbird",
    display_name="Songbird / Passerine (3/4 Profile)",
    landmarks=LANDMARKS,
    feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES,
    proportions=PROPORTIONS,
)
