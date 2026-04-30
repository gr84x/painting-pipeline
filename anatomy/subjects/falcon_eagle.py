"""
Falcon and eagle anatomy — distinct variants of raptor.

Both share the raptor base (hooked beak, supraorbital ridge, forward-facing
eyes) but differ in key ways:

  Falcon: smaller, pointed wings (not relevant for head portrait), notched
    tomial tooth on upper mandible, longer more tapered beak, dark malar
    stripe (the "moustache"), faster more angular silhouette.

  Eagle: massive beak (deeper, more prominently hooked), very heavy brow,
    larger head, powerful broad-based cere, often feathered up to cere base.
    Bald eagle has the white head + yellow cere + yellow beak — high contrast.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy


# ── Falcon (3/4 profile) ──────────────────────────────────────────────────────

FALCON = SubjectAnatomy(
    subject_id="falcon",
    display_name="Falcon (3/4 Profile)",
    landmarks=[
        Landmark("near_eye",         nx=-0.18, ny=-0.18),
        Landmark("far_eye",          nx=+0.20, ny=-0.20),
        Landmark("supraorbital_ridge",nx=-0.18,ny=-0.30),
        Landmark("cere",             nx=-0.48, ny=+0.02),
        Landmark("tomial_tooth",     nx=-0.58, ny=+0.08),   # the notch unique to falcons
        Landmark("beak_tip",         nx=-0.68, ny=+0.20),
        Landmark("nare",             nx=-0.44, ny=-0.04),
        Landmark("malar_stripe_top", nx=-0.25, ny=-0.05),   # the "moustache" stripe
        Landmark("malar_stripe_base",nx=-0.22, ny=+0.25),
        Landmark("gape",             nx=-0.35, ny=+0.22),
        Landmark("crown",            nx=+0.06, ny=-0.60),
        Landmark("nape",             nx=+0.52, ny=-0.22),
        Landmark("chin",             nx=-0.12, ny=+0.45),
        Landmark("ear_coverts",      nx=+0.22, ny=-0.08),
    ],
    feature_zones=[
        FeatureZone("near_eye",       "near_eye",         radius_nx=0.18, radius_ny=0.13,
                    error_weight=8.0, stroke_size_scale=0.48, jitter_scale=0.52, wet_blend_scale=0.48),
        FeatureZone("far_eye",        "far_eye",          radius_nx=0.14, radius_ny=0.10,
                    error_weight=6.5, stroke_size_scale=0.52, jitter_scale=0.56),
        FeatureZone("malar_stripe",   "malar_stripe_top", radius_nx=0.10, radius_ny=0.22,
                    error_weight=5.5, stroke_size_scale=0.48),    # THE defining falcon feature
        FeatureZone("beak",           "beak_tip",         radius_nx=0.28, radius_ny=0.20,
                    error_weight=5.0, stroke_size_scale=0.50, jitter_scale=0.58),
        FeatureZone("tomial_tooth",   "tomial_tooth",     radius_nx=0.12, radius_ny=0.10,
                    error_weight=4.0, stroke_size_scale=0.45),
        FeatureZone("cere",           "cere",             radius_nx=0.14, radius_ny=0.10,
                    error_weight=3.5, stroke_size_scale=0.52),
        FeatureZone("supraorbital",   "supraorbital_ridge",radius_nx=0.26,radius_ny=0.08,
                    error_weight=3.5, stroke_size_scale=0.55),
    ],
    flow_zones=[
        FlowZone("crown", "diagonal",
                 {"nx_factor": 0.42, "ny_factor": -0.32, "anchor_nx": +0.06, "anchor_ny": -0.52},
                 weight_sigma_nx=0.38, weight_sigma_ny=0.24),
        FlowZone("near_eye_socket", "orbital",
                 {"orbit_anchor": "near_eye", "orbit_nx": -0.18, "orbit_ny": -0.18},
                 weight_sigma_nx=0.18, weight_sigma_ny=0.15),
        FlowZone("far_eye_socket", "orbital",
                 {"orbit_anchor": "far_eye", "orbit_nx": +0.20, "orbit_ny": -0.20},
                 weight_sigma_nx=0.14, weight_sigma_ny=0.12),
        # Malar stripe — strokes run vertically along the stripe
        FlowZone("malar_stripe", "fixed",
                 {"radians": math.pi * 0.50, "anchor_nx": -0.23, "anchor_ny": +0.10},
                 weight_sigma_nx=0.10, weight_sigma_ny=0.24),
        FlowZone("beak_feathers", "diagonal",
                 {"nx_factor": -0.65, "ny_factor": 0.22, "anchor_nx": -0.42, "anchor_ny": +0.06},
                 weight_sigma_nx=0.24, weight_sigma_ny=0.20),
        FlowZone("cheek", "diagonal",
                 {"nx_factor": 0.58, "ny_factor": 0.22, "anchor_nx": +0.10, "anchor_ny": +0.04},
                 weight_sigma_nx=0.35, weight_sigma_ny=0.28),
        FlowZone("throat", "diagonal",
                 {"nx_factor": -0.06, "ny_factor": 0.98, "anchor_nx": -0.08, "anchor_ny": +0.38},
                 weight_sigma_nx=0.26, weight_sigma_ny=0.20),
    ],
    proportions={"beak_length_fraction": 0.38, "beak_depth_fraction": 0.14,
                 "eye_diameter_fraction": 0.20, "aspect_ratio": 0.80},
)


# ── Eagle (3/4 profile — bald eagle / golden eagle) ──────────────────────────

EAGLE = SubjectAnatomy(
    subject_id="eagle",
    display_name="Eagle (3/4 Profile)",
    landmarks=[
        Landmark("near_eye",          nx=-0.16, ny=-0.16),
        Landmark("far_eye",           nx=+0.18, ny=-0.18),
        Landmark("supraorbital_heavy",nx=-0.16, ny=-0.32),   # massive brow overhang
        Landmark("cere_base",         nx=-0.35, ny=-0.02),
        Landmark("cere_nostril",      nx=-0.40, ny=-0.08),
        Landmark("beak_culmen",       nx=-0.55, ny=-0.08),   # ridge of upper beak
        Landmark("beak_tip",          nx=-0.72, ny=+0.24),   # dramatically hooked
        Landmark("gape",              nx=-0.30, ny=+0.20),
        Landmark("lower_mandible",    nx=-0.50, ny=+0.28),
        Landmark("crown",             nx=+0.06, ny=-0.62),
        Landmark("nape",              nx=+0.52, ny=-0.25),
        Landmark("chin_white",        nx=-0.14, ny=+0.42),   # white head (bald eagle)
        Landmark("ear_coverts",       nx=+0.22, ny=-0.10),
        Landmark("cheek",             nx=+0.06, ny=+0.10),
    ],
    feature_zones=[
        FeatureZone("near_eye",        "near_eye",           radius_nx=0.18, radius_ny=0.14,
                    error_weight=8.5, stroke_size_scale=0.48, jitter_scale=0.52, wet_blend_scale=0.48),
        FeatureZone("far_eye",         "far_eye",            radius_nx=0.15, radius_ny=0.11,
                    error_weight=7.0, stroke_size_scale=0.52, jitter_scale=0.56),
        # The heavy supraorbital brow is as important as the eye itself
        FeatureZone("supraorbital",    "supraorbital_heavy", radius_nx=0.32, radius_ny=0.10,
                    error_weight=5.0, stroke_size_scale=0.52),
        FeatureZone("beak",            "beak_tip",           radius_nx=0.35, radius_ny=0.24,
                    error_weight=6.0, stroke_size_scale=0.48, jitter_scale=0.54),
        FeatureZone("cere",            "cere_base",          radius_nx=0.18, radius_ny=0.12,
                    error_weight=4.5, stroke_size_scale=0.50),
        FeatureZone("white_head",      "crown",              radius_nx=0.55, radius_ny=0.45,
                    error_weight=3.5, stroke_size_scale=0.60),   # bald eagle white plumage
        FeatureZone("ear_coverts",     "ear_coverts",        radius_nx=0.28, radius_ny=0.24,
                    error_weight=2.0, stroke_size_scale=0.70),
    ],
    flow_zones=[
        FlowZone("crown", "diagonal",
                 {"nx_factor": 0.40, "ny_factor": -0.35, "anchor_nx": +0.06, "anchor_ny": -0.55},
                 weight_sigma_nx=0.40, weight_sigma_ny=0.26),
        FlowZone("near_eye_socket", "orbital",
                 {"orbit_anchor": "near_eye", "orbit_nx": -0.16, "orbit_ny": -0.16},
                 weight_sigma_nx=0.20, weight_sigma_ny=0.16),
        FlowZone("far_eye_socket", "orbital",
                 {"orbit_anchor": "far_eye", "orbit_nx": +0.18, "orbit_ny": -0.18},
                 weight_sigma_nx=0.16, weight_sigma_ny=0.14),
        FlowZone("beak_region", "diagonal",
                 {"nx_factor": -0.68, "ny_factor": 0.25, "anchor_nx": -0.48, "anchor_ny": +0.06},
                 weight_sigma_nx=0.28, weight_sigma_ny=0.24),
        FlowZone("cheek", "diagonal",
                 {"nx_factor": 0.60, "ny_factor": 0.20, "anchor_nx": +0.08, "anchor_ny": +0.06},
                 weight_sigma_nx=0.38, weight_sigma_ny=0.30),
        FlowZone("throat", "diagonal",
                 {"nx_factor": -0.05, "ny_factor": 0.98, "anchor_nx": -0.10, "anchor_ny": +0.38},
                 weight_sigma_nx=0.28, weight_sigma_ny=0.22),
        FlowZone("nape", "diagonal",
                 {"nx_factor": 0.38, "ny_factor": 0.42, "anchor_nx": +0.46, "anchor_ny": -0.20},
                 weight_sigma_nx=0.22, weight_sigma_ny=0.25),
    ],
    proportions={"beak_length_fraction": 0.46, "beak_depth_fraction": 0.24,
                 "eye_diameter_fraction": 0.20, "aspect_ratio": 0.82},
)
