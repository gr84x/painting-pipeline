"""
Octopus and squid anatomy — frontal / 3/4 view.

Two variants registered:
  "octopus" — rounded mantle, eight radiating arms, W-shaped pupil
  "squid"   — elongated torpedo mantle, two longer tentacles, slit pupil

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
The bounding ellipse spans the full arm/tentacle spread (nx) and mantle
tip to tentacle tips (ny), with the eyes and beak at centre-upper region.

These are among the most painterly subjects for texture: chromatophores
create rapid colour patterns; papillae create surface topography; iridophores
produce iridescent shimmer. The skin texture itself is the feature.

Flow zones radiate from the mantle centre outward along arm directions —
unlike fur subjects, the "texture flow" follows radial geometry.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy


# ── Octopus ───────────────────────────────────────────────────────────────────

OCTOPUS_LANDMARKS = [
    # Eyes — distinctive W-shaped (or horizontal bar) pupil; set on sides of head
    Landmark("left_eye",         nx=-0.32, ny=-0.18),
    Landmark("right_eye",        nx=+0.32, ny=-0.18),
    # Beak — hidden between arms at centre
    Landmark("beak",             nx= 0.00, ny=+0.05),
    # Mantle (body above the arms)
    Landmark("mantle_top",       nx= 0.00, ny=-0.72),
    Landmark("mantle_left",      nx=-0.35, ny=-0.45),
    Landmark("mantle_right",     nx=+0.35, ny=-0.45),
    Landmark("mantle_centre",    nx= 0.00, ny=-0.38),
    Landmark("web_centre",       nx= 0.00, ny=+0.08),   # interarm webbing
    # Arms (8) — approximate directions in radial layout
    Landmark("arm_1_tip",  nx=-0.80, ny=-0.25),
    Landmark("arm_2_tip",  nx=-0.90, ny=+0.15),
    Landmark("arm_3_tip",  nx=-0.75, ny=+0.55),
    Landmark("arm_4_tip",  nx=-0.35, ny=+0.85),
    Landmark("arm_5_tip",  nx=+0.35, ny=+0.85),
    Landmark("arm_6_tip",  nx=+0.75, ny=+0.55),
    Landmark("arm_7_tip",  nx=+0.90, ny=+0.15),
    Landmark("arm_8_tip",  nx=+0.80, ny=-0.25),
    # Sucker bands (texture reference)
    Landmark("arm_sucker_zone",  nx=+0.00, ny=+0.48),
]

OCTOPUS_FEATURE_ZONES = [
    # Eyes are the emotional core — W-pupil is a highly distinctive feature
    FeatureZone("left_eye",   "left_eye",   radius_nx=0.22, radius_ny=0.16,
                error_weight=9.0, stroke_size_scale=0.44, jitter_scale=0.48, wet_blend_scale=0.44),
    FeatureZone("right_eye",  "right_eye",  radius_nx=0.22, radius_ny=0.16,
                error_weight=9.0, stroke_size_scale=0.44, jitter_scale=0.48, wet_blend_scale=0.44),
    FeatureZone("beak",       "beak",       radius_nx=0.14, radius_ny=0.12,
                error_weight=5.5, stroke_size_scale=0.50),
    # Mantle — the main body; chromatophore patterns make this a priority
    FeatureZone("mantle",     "mantle_centre", radius_nx=0.40, radius_ny=0.42,
                error_weight=4.0, stroke_size_scale=0.58),
    # Sucker texture along arms
    FeatureZone("sucker_texture","arm_sucker_zone", radius_nx=0.65, radius_ny=0.28,
                error_weight=3.0, stroke_size_scale=0.52),
    # Webbing — thin interarm membrane
    FeatureZone("web",        "web_centre", radius_nx=0.45, radius_ny=0.18,
                error_weight=2.5, stroke_size_scale=0.60),
]

OCTOPUS_FLOW_ZONES = [
    # Mantle — dome-shaped strokes following the mantle surface curvature
    FlowZone("mantle", "orbital",
             {"orbit_anchor": "mantle_centre", "orbit_nx": 0.00, "orbit_ny": -0.38},
             weight_sigma_nx=0.42, weight_sigma_ny=0.42),
    # Left eye socket
    FlowZone("left_eye_socket", "orbital",
             {"orbit_anchor": "left_eye", "orbit_nx": -0.32, "orbit_ny": -0.18},
             weight_sigma_nx=0.20, weight_sigma_ny=0.18),
    # Right eye socket
    FlowZone("right_eye_socket", "orbital",
             {"orbit_anchor": "right_eye", "orbit_nx": +0.32, "orbit_ny": -0.18},
             weight_sigma_nx=0.20, weight_sigma_ny=0.18),
    # Arms — strokes radiate from beak outward along each arm direction
    FlowZone("arms_left", "diagonal",
             {"nx_factor": -0.72, "ny_factor": 0.55, "anchor_nx": -0.45, "anchor_ny": +0.38},
             weight_sigma_nx=0.40, weight_sigma_ny=0.40),
    FlowZone("arms_right", "diagonal",
             {"nx_factor": +0.72, "ny_factor": 0.55, "anchor_nx": +0.45, "anchor_ny": +0.38},
             weight_sigma_nx=0.40, weight_sigma_ny=0.40),
    FlowZone("arms_lower", "diagonal",
             {"nx_factor": 0.04, "ny_factor": 0.95, "anchor_nx": 0.00, "anchor_ny": +0.68},
             weight_sigma_nx=0.40, weight_sigma_ny=0.22),
]

OCTOPUS = SubjectAnatomy(
    subject_id="octopus",
    display_name="Octopus (Frontal / 3/4)",
    landmarks=OCTOPUS_LANDMARKS,
    feature_zones=OCTOPUS_FEATURE_ZONES,
    flow_zones=OCTOPUS_FLOW_ZONES,
    proportions={
        "mantle_fraction":    0.40,   # mantle = 40% of total spread
        "arm_count":          8,
        "eye_diameter_fraction": 0.18,
        "aspect_ratio":       0.95,
    },
)


# ── Squid ─────────────────────────────────────────────────────────────────────

SQUID_LANDMARKS = [
    Landmark("left_eye",          nx=-0.28, ny=+0.12),
    Landmark("right_eye",         nx=+0.28, ny=+0.12),
    Landmark("beak",              nx= 0.00, ny=+0.25),
    Landmark("mantle_tip",        nx= 0.00, ny=-0.88),   # pointed posterior
    Landmark("mantle_top",        nx= 0.00, ny=-0.55),
    Landmark("mantle_left",       nx=-0.28, ny=-0.20),
    Landmark("mantle_right",      nx=+0.28, ny=-0.20),
    Landmark("mantle_centre",     nx= 0.00, ny=-0.10),
    Landmark("fin_left_tip",      nx=-0.45, ny=-0.60),   # lateral fins
    Landmark("fin_right_tip",     nx=+0.45, ny=-0.60),
    # 8 shorter arms + 2 long tentacles
    Landmark("arm_cluster_left",  nx=-0.42, ny=+0.48),
    Landmark("arm_cluster_right", nx=+0.42, ny=+0.48),
    Landmark("tentacle_left_tip", nx=-0.65, ny=+0.90),
    Landmark("tentacle_right_tip",nx=+0.65, ny=+0.90),
    Landmark("tentacle_club_left",nx=-0.55, ny=+0.78),  # sucker-bearing club
    Landmark("tentacle_club_right",nx=+0.55,ny=+0.78),
]

SQUID_FEATURE_ZONES = [
    FeatureZone("left_eye",   "left_eye",   radius_nx=0.20, radius_ny=0.16,
                error_weight=9.0, stroke_size_scale=0.46, jitter_scale=0.50, wet_blend_scale=0.46),
    FeatureZone("right_eye",  "right_eye",  radius_nx=0.20, radius_ny=0.16,
                error_weight=9.0, stroke_size_scale=0.46, jitter_scale=0.50, wet_blend_scale=0.46),
    FeatureZone("beak",       "beak",       radius_nx=0.14, radius_ny=0.12,
                error_weight=5.0, stroke_size_scale=0.50),
    FeatureZone("mantle",     "mantle_centre", radius_nx=0.32, radius_ny=0.55,
                error_weight=3.5, stroke_size_scale=0.60),   # iridescent torpedo body
    FeatureZone("fins",       "fin_left_tip",  radius_nx=0.28, radius_ny=0.22,
                error_weight=2.5, stroke_size_scale=0.65),
    FeatureZone("tentacle_clubs","tentacle_club_left", radius_nx=0.22, radius_ny=0.16,
                error_weight=3.0, stroke_size_scale=0.52),   # sucker clubs are distinctive
]

SQUID_FLOW_ZONES = [
    # Mantle — elongated torpedo; strokes run longitudinally (head to tip)
    FlowZone("mantle", "diagonal",
             {"nx_factor": 0.04, "ny_factor": -0.98, "anchor_nx": 0.00, "anchor_ny": -0.35},
             weight_sigma_nx=0.30, weight_sigma_ny=0.55),
    FlowZone("left_eye_socket", "orbital",
             {"orbit_anchor": "left_eye", "orbit_nx": -0.28, "orbit_ny": +0.12},
             weight_sigma_nx=0.18, weight_sigma_ny=0.16),
    FlowZone("right_eye_socket", "orbital",
             {"orbit_anchor": "right_eye", "orbit_nx": +0.28, "orbit_ny": +0.12},
             weight_sigma_nx=0.18, weight_sigma_ny=0.16),
    # Fins — diagonal strokes following fin surface
    FlowZone("fins_left", "diagonal",
             {"nx_factor": -0.55, "ny_factor": -0.65, "anchor_nx": -0.38, "anchor_ny": -0.58},
             weight_sigma_nx=0.22, weight_sigma_ny=0.20),
    FlowZone("fins_right", "diagonal",
             {"nx_factor": +0.55, "ny_factor": -0.65, "anchor_nx": +0.38, "anchor_ny": -0.58},
             weight_sigma_nx=0.22, weight_sigma_ny=0.20),
    # Arms and tentacles — radiate downward from beak
    FlowZone("tentacles", "diagonal",
             {"nx_factor": 0.08, "ny_factor": 0.95, "anchor_nx": 0.00, "anchor_ny": +0.60},
             weight_sigma_nx=0.48, weight_sigma_ny=0.30),
]

SQUID = SubjectAnatomy(
    subject_id="squid",
    display_name="Squid (Frontal / 3/4)",
    landmarks=SQUID_LANDMARKS,
    feature_zones=SQUID_FEATURE_ZONES,
    flow_zones=SQUID_FLOW_ZONES,
    proportions={
        "mantle_fraction":       0.60,   # mantle = 60% of length
        "arm_count":             8,
        "tentacle_count":        2,
        "tentacle_length_ratio": 2.0,    # tentacles ~2× arm length
        "aspect_ratio":          0.50,   # tall, narrow torpedo
    },
)
