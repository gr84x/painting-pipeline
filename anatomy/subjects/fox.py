"""
Fox head anatomy — 3/4 profile view (snout angled toward viewer's left).

Normalized coordinate system: nx ∈ [-1, +1] left→right (from viewer),
ny ∈ [-1, +1] top→bottom. The bounding ellipse encompasses the full head
from ear tips (-1) to chin (+1), and from snout tip (-1) to ruff (+1).

Fox-specific proportions:
  - Muzzle is elongated, occupying roughly 40% of head width in 3/4 view
  - Eyes are large relative to head, set high and forward
  - Ears are tall (roughly 35–40% of head height), widely spaced
  - Nose pad (wet nose) is small, dark, at the very tip of the snout
  - In 3/4 profile: near eye (viewer's left) appears larger and rounder;
    far eye (viewer's right) is partially foreshortened

Flow zones encode how fur lies across the fox's head — always following
the direction of hair growth, which painters must replicate with brushwork.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy


# ── Landmarks ─────────────────────────────────────────────────────────────────
# Coordinates calibrated to the session reference fox:
#   head centre = (fox_cx - 0.018*W, fox_cy - 0.145*H)
#   head rx = 0.066*W, head ry = 0.072*H
# nx/ny are relative to this head bounding ellipse.

LANDMARKS = [
    # Eyes — 3/4 profile: near eye is left, far eye is right
    Landmark("near_eye",         nx=-0.28, ny=-0.14),  # viewer's left, larger
    Landmark("far_eye",          nx=+0.12, ny=-0.16),  # viewer's right, foreshortened
    # Pupils / iris centres (used for orbital flow zones)
    Landmark("near_eye_pupil",   nx=-0.28, ny=-0.14),
    Landmark("far_eye_pupil",    nx=+0.12, ny=-0.16),
    # Ears — tall, upright, angled outward
    Landmark("left_ear_base",    nx=-0.28, ny=-0.60),
    Landmark("left_ear_tip",     nx=-0.32, ny=-0.92),
    Landmark("right_ear_base",   nx=+0.30, ny=-0.55),
    Landmark("right_ear_tip",    nx=+0.34, ny=-0.88),
    # Snout / muzzle — extends to viewer's left in 3/4 view
    Landmark("muzzle_centre",    nx=-0.52, ny=+0.14),
    Landmark("nose_pad",         nx=-0.62, ny=+0.08),  # wet nose tip
    Landmark("left_nostril",     nx=-0.58, ny=+0.12),
    Landmark("right_nostril",    nx=-0.50, ny=+0.12),
    # Mouth
    Landmark("mouth_corner",     nx=-0.42, ny=+0.30),
    Landmark("lower_lip",        nx=-0.48, ny=+0.38),
    # Jaw and skull
    Landmark("chin",             nx=-0.20, ny=+0.68),
    Landmark("jaw_line",         nx=+0.20, ny=+0.52),
    # Forehead / crown
    Landmark("forehead",         nx=+0.05, ny=-0.40),
    Landmark("crown",            nx=+0.05, ny=-0.70),
    # Cheekbone
    Landmark("cheekbone",        nx=-0.10, ny=+0.05),
    # Ruff / neck connection
    Landmark("ruff_left",        nx=-0.30, ny=+0.80),
    Landmark("ruff_right",       nx=+0.40, ny=+0.72),
]


# ── Feature zones ─────────────────────────────────────────────────────────────

FEATURE_ZONES = [
    # Near eye — highest priority; this is the focal point of a fox portrait
    FeatureZone(
        name="near_eye",
        anchor="near_eye",
        radius_nx=0.22, radius_ny=0.16,
        error_weight=7.0,
        stroke_size_scale=0.50,
        jitter_scale=0.55,
        wet_blend_scale=0.50,
    ),
    # Far eye — slightly lower weight due to foreshortening
    FeatureZone(
        name="far_eye",
        anchor="far_eye",
        radius_nx=0.16, radius_ny=0.12,
        error_weight=5.5,
        stroke_size_scale=0.55,
        jitter_scale=0.60,
        wet_blend_scale=0.55,
    ),
    # Nose pad — small, high-contrast; important for likeness
    FeatureZone(
        name="nose_pad",
        anchor="nose_pad",
        radius_nx=0.14, radius_ny=0.10,
        error_weight=5.0,
        stroke_size_scale=0.50,
        jitter_scale=0.55,
    ),
    # Muzzle — wider zone; fur texture and lip line
    FeatureZone(
        name="muzzle",
        anchor="muzzle_centre",
        radius_nx=0.28, radius_ny=0.20,
        error_weight=3.5,
        stroke_size_scale=0.70,
        jitter_scale=0.70,
    ),
    # Mouth corner — subtle but important for expression
    FeatureZone(
        name="mouth",
        anchor="mouth_corner",
        radius_nx=0.20, radius_ny=0.12,
        error_weight=3.0,
        stroke_size_scale=0.65,
        jitter_scale=0.70,
    ),
    # Ear interiors — colour and texture contrast with outer fur
    FeatureZone(
        name="left_ear",
        anchor="left_ear_tip",
        radius_nx=0.16, radius_ny=0.24,
        error_weight=2.5,
        stroke_size_scale=0.75,
    ),
    FeatureZone(
        name="right_ear",
        anchor="right_ear_tip",
        radius_nx=0.14, radius_ny=0.22,
        error_weight=2.0,
        stroke_size_scale=0.75,
    ),
]


# ── Flow zones ────────────────────────────────────────────────────────────────
# Fur on a fox grows in very specific directions. Strokes that follow growth
# direction produce convincing fur texture even at coarse brush sizes.
# Zones named for the anatomical region and dominant fur direction.

FLOW_ZONES = [
    # Crown / forehead — fur grows rearward and downward from brow
    FlowZone(
        name="crown",
        angle_type="diagonal",
        angle_params={"nx_factor": 0.15, "ny_factor": -1.0,
                      "anchor_nx": +0.05, "anchor_ny": -0.55},
        weight_sigma_nx=0.45, weight_sigma_ny=0.28,
    ),
    # Cheek — fur fans outward and downward from eye toward jaw
    FlowZone(
        name="cheek",
        angle_type="diagonal",
        angle_params={"nx_factor": -0.45, "ny_factor": 0.85,
                      "anchor_nx": -0.05, "anchor_ny": +0.10},
        weight_sigma_nx=0.38, weight_sigma_ny=0.35,
    ),
    # Near eye socket — strokes orbit the visible eye
    FlowZone(
        name="near_eye_socket",
        angle_type="orbital",
        angle_params={"orbit_anchor": "near_eye",
                      "orbit_nx": -0.28, "orbit_ny": -0.14},
        weight_sigma_nx=0.18, weight_sigma_ny=0.14,
    ),
    # Far eye socket
    FlowZone(
        name="far_eye_socket",
        angle_type="orbital",
        angle_params={"orbit_anchor": "far_eye",
                      "orbit_nx": +0.12, "orbit_ny": -0.16},
        weight_sigma_nx=0.14, weight_sigma_ny=0.12,
    ),
    # Muzzle — fur runs horizontally along the snout toward the nose
    FlowZone(
        name="muzzle",
        angle_type="diagonal",
        angle_params={"nx_factor": -0.05, "ny_factor": 0.10,
                      "anchor_nx": -0.50, "anchor_ny": +0.12},
        weight_sigma_nx=0.28, weight_sigma_ny=0.18,
    ),
    # Left ear — vertical strokes, following the ear's upright shape
    FlowZone(
        name="left_ear",
        angle_type="fixed",
        angle_params={"radians": math.pi * 0.55,   # slightly tilted vertical
                      "anchor_nx": -0.30, "anchor_ny": -0.76},
        weight_sigma_nx=0.14, weight_sigma_ny=0.22,
    ),
    # Right ear
    FlowZone(
        name="right_ear",
        angle_type="fixed",
        angle_params={"radians": math.pi * 0.48,
                      "anchor_nx": +0.32, "anchor_ny": -0.72},
        weight_sigma_nx=0.14, weight_sigma_ny=0.22,
    ),
    # Chin / lower jaw — fur grows downward into the ruff
    FlowZone(
        name="chin_ruff",
        angle_type="diagonal",
        angle_params={"nx_factor": 0.20, "ny_factor": 0.90,
                      "anchor_nx": -0.10, "anchor_ny": +0.60},
        weight_sigma_nx=0.40, weight_sigma_ny=0.25,
    ),
]


# ── Proportions ───────────────────────────────────────────────────────────────

PROPORTIONS = {
    # Muzzle length relative to total head height
    "muzzle_length_fraction":     0.42,
    # Eye diameter relative to head width (fox eyes are large)
    "eye_diameter_fraction":      0.20,
    # Ear height relative to head height
    "ear_height_fraction":        0.38,
    # Interocular distance in 3/4 view (compressed vs frontal)
    "interocular_distance_nx":    0.40,
    # Nose pad diameter relative to muzzle width
    "nose_pad_fraction":          0.18,
    # Head width / head height ratio
    "aspect_ratio":               0.92,
}


# ── Assembly ──────────────────────────────────────────────────────────────────

FOX = SubjectAnatomy(
    subject_id="fox",
    display_name="Fox (3/4 Profile)",
    landmarks=LANDMARKS,
    feature_zones=FEATURE_ZONES,
    flow_zones=FLOW_ZONES,
    proportions=PROPORTIONS,
)
