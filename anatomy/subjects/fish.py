"""
Fish head / body anatomy — side profile.

Two variants registered:
  "fish_tropical"  — reef fish: tall body, short snout, vivid colour bands
  "fish_elongated" — trout / salmon / pike: streamlined, longer snout

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
In side profile: nx=-1 = mouth/lip, nx=+1 = tail end of head / operculum.
ny=-1 = dorsal surface, ny=+1 = ventral surface.

Key painting features:
  - Eye: single, round, prominent — highest weight
  - Lateral line: a sensory pore stripe running mid-body (species-specific)
  - Operculum (gill cover): the curved boundary behind the head
  - Scales: overlap in diagonal rows, creating the characteristic texture
  - Colour bands / spots: species identification marks
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy


# ── Shared landmark builder ───────────────────────────────────────────────────

def _fish_landmarks(snout_reach: float = 0.55) -> list:
    """snout_reach: how far nx=-1 extends (0.55 = short tropical, 0.72 = elongated)"""
    return [
        # Head
        Landmark("eye",               nx=-0.12, ny=-0.12),
        Landmark("pupil",             nx=-0.12, ny=-0.12),
        Landmark("mouth_upper_lip",   nx=-snout_reach, ny=+0.05),
        Landmark("mouth_lower_lip",   nx=-snout_reach, ny=+0.12),
        Landmark("snout_tip",         nx=-(snout_reach - 0.04), ny=0.00),
        Landmark("nare",              nx=-(snout_reach * 0.62), ny=-0.06),
        Landmark("operculum_top",     nx=+0.22, ny=-0.42),    # gill cover top
        Landmark("operculum_rear",    nx=+0.52, ny=-0.05),    # gill cover trailing edge
        Landmark("operculum_bottom",  nx=+0.30, ny=+0.40),
        # Body surface (head region)
        Landmark("dorsal_profile",    nx=+0.00, ny=-0.55),
        Landmark("ventral_profile",   nx=+0.00, ny=+0.55),
        Landmark("lateral_line_fore", nx=+0.10, ny=-0.08),    # lateral line starts here
        Landmark("lateral_line_mid",  nx=+0.40, ny=-0.05),
        # Colour band anchors
        Landmark("body_centre",       nx=+0.20, ny=+0.00),
        Landmark("chin",              nx=-0.35, ny=+0.32),
    ]


def _fish_feature_zones(eye_weight: float = 9.0) -> list:
    return [
        FeatureZone("eye",            "eye",              radius_nx=0.18, radius_ny=0.16,
                    error_weight=eye_weight, stroke_size_scale=0.44, jitter_scale=0.48, wet_blend_scale=0.44),
        FeatureZone("mouth",          "mouth_upper_lip",  radius_nx=0.20, radius_ny=0.14,
                    error_weight=5.0, stroke_size_scale=0.52, jitter_scale=0.58),
        FeatureZone("operculum",      "operculum_rear",   radius_nx=0.24, radius_ny=0.48,
                    error_weight=4.0, stroke_size_scale=0.55),    # gill cover boundary
        FeatureZone("lateral_line",   "lateral_line_mid", radius_nx=0.42, radius_ny=0.08,
                    error_weight=2.5, stroke_size_scale=0.58),
        FeatureZone("colour_band",    "body_centre",      radius_nx=0.50, radius_ny=0.60,
                    error_weight=2.0, stroke_size_scale=0.62),
    ]


def _fish_flow_zones() -> list:
    return [
        # Around eye — strokes orbit the eye
        FlowZone("eye_socket", "orbital",
                 {"orbit_anchor": "eye", "orbit_nx": -0.12, "orbit_ny": -0.12},
                 weight_sigma_nx=0.16, weight_sigma_ny=0.14),
        # Scales — overlap posteriorly; strokes run diagonally back and down
        FlowZone("scales_upper", "diagonal",
                 {"nx_factor": 0.70, "ny_factor": 0.35, "anchor_nx": +0.20, "anchor_ny": -0.25},
                 weight_sigma_nx=0.45, weight_sigma_ny=0.28),
        FlowZone("scales_lower", "diagonal",
                 {"nx_factor": 0.70, "ny_factor": -0.35, "anchor_nx": +0.20, "anchor_ny": +0.28},
                 weight_sigma_nx=0.45, weight_sigma_ny=0.28),
        # Operculum — curved strokes following the gill cover arc
        FlowZone("operculum", "orbital",
                 {"orbit_anchor": "eye", "orbit_nx": -0.12, "orbit_ny": -0.12},
                 weight_sigma_nx=0.30, weight_sigma_ny=0.50),
        # Snout — short strokes toward the mouth
        FlowZone("snout", "diagonal",
                 {"nx_factor": -0.80, "ny_factor": 0.10, "anchor_nx": -0.35, "anchor_ny": 0.00},
                 weight_sigma_nx=0.22, weight_sigma_ny=0.18),
    ]


FISH_TROPICAL = SubjectAnatomy(
    subject_id="fish_tropical",
    display_name="Fish — Tropical / Reef (Side Profile)",
    landmarks=_fish_landmarks(snout_reach=0.52),
    feature_zones=_fish_feature_zones(eye_weight=9.0),
    flow_zones=_fish_flow_zones(),
    proportions={
        "body_depth_fraction":   0.90,   # tall, deep body
        "snout_length_fraction": 0.22,
        "eye_diameter_fraction": 0.22,
        "aspect_ratio":          0.88,
    },
)

FISH_ELONGATED = SubjectAnatomy(
    subject_id="fish_elongated",
    display_name="Fish — Trout / Salmon / Pike (Side Profile)",
    landmarks=_fish_landmarks(snout_reach=0.68),
    feature_zones=_fish_feature_zones(eye_weight=8.5),
    flow_zones=_fish_flow_zones(),
    proportions={
        "body_depth_fraction":   0.40,   # streamlined, slender
        "snout_length_fraction": 0.42,
        "eye_diameter_fraction": 0.14,
        "aspect_ratio":          2.20,
    },
)
