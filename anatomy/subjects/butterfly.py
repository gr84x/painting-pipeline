"""
Butterfly / moth anatomy — dorsal view (wings spread, symmetrical).

Two variants:
  "butterfly" — diurnal, often vivid colour bands; clubbed antennae
  "moth"      — often cryptic/muted pattern; feathered antennae; hindwing visible

Normalized space: nx ∈ [-1, +1] left→right, ny ∈ [-1, +1] top→bottom.
The bounding ellipse spans full wing tip-to-tip (nx) and forewing tip to
hindwing trailing edge (ny), with the body at centre (nx≈0, ny≈0).

Wings are the entire painting subject. Venation radiates from the wing
attachment points. Wing cell patterns (eyespots, bands, borders) are the
highest-priority features. The body is narrow and often partially obscured.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy


def _build(subject_id, display_name, eyespot_weight=6.0, body_weight=3.5):
    landmarks = [
        # Body
        Landmark("head",                   nx= 0.00, ny=-0.08),
        Landmark("thorax",                 nx= 0.00, ny= 0.00),
        Landmark("abdomen_tip",            nx= 0.00, ny=+0.35),
        # Antennae
        Landmark("left_antenna_tip",       nx=-0.18, ny=-0.55),
        Landmark("right_antenna_tip",      nx=+0.18, ny=-0.55),
        # Forewing attachment
        Landmark("fw_left_attachment",     nx=-0.08, ny=-0.10),
        Landmark("fw_right_attachment",    nx=+0.08, ny=-0.10),
        # Forewing tips
        Landmark("fw_left_apex",           nx=-0.88, ny=-0.52),
        Landmark("fw_right_apex",          nx=+0.88, ny=-0.52),
        # Forewing trailing edge
        Landmark("fw_left_trailing",       nx=-0.55, ny=+0.18),
        Landmark("fw_right_trailing",      nx=+0.55, ny=+0.18),
        # Hindwing
        Landmark("hw_left_apex",           nx=-0.72, ny=+0.52),
        Landmark("hw_right_apex",          nx=+0.72, ny=+0.52),
        Landmark("hw_left_tail",           nx=-0.35, ny=+0.82),   # swallowtail extension
        Landmark("hw_right_tail",          nx=+0.35, ny=+0.82),
        # Eyespots (common in many species — hindwing focus)
        Landmark("left_eyespot",           nx=-0.45, ny=+0.42),
        Landmark("right_eyespot",          nx=+0.45, ny=+0.42),
        # Wing margin band
        Landmark("fw_left_margin_mid",     nx=-0.78, ny=-0.22),
        Landmark("fw_right_margin_mid",    nx=+0.78, ny=-0.22),
    ]

    feature_zones = [
        # Eyespots — iridescent bull's-eye patterns are the focal feature
        FeatureZone("left_eyespot",   "left_eyespot",        radius_nx=0.20, radius_ny=0.18,
                    error_weight=eyespot_weight, stroke_size_scale=0.48, jitter_scale=0.50, wet_blend_scale=0.48),
        FeatureZone("right_eyespot",  "right_eyespot",       radius_nx=0.20, radius_ny=0.18,
                    error_weight=eyespot_weight, stroke_size_scale=0.48, jitter_scale=0.50, wet_blend_scale=0.48),
        # Wing margin bands — contrasting colour edges
        FeatureZone("fw_left_margin", "fw_left_margin_mid",  radius_nx=0.14, radius_ny=0.52,
                    error_weight=3.5, stroke_size_scale=0.55),
        FeatureZone("fw_right_margin","fw_right_margin_mid", radius_nx=0.14, radius_ny=0.52,
                    error_weight=3.5, stroke_size_scale=0.55),
        # Body — detailed texture (scales, legs, proboscis)
        FeatureZone("body",           "thorax",               radius_nx=0.12, radius_ny=0.42,
                    error_weight=body_weight, stroke_size_scale=0.52),
        # Antennae
        FeatureZone("antennae",       "left_antenna_tip",    radius_nx=0.24, radius_ny=0.30,
                    error_weight=2.0, stroke_size_scale=0.44),
        # Wing surface — the broad colour field
        FeatureZone("fw_left_field",  "fw_left_attachment",  radius_nx=0.52, radius_ny=0.45,
                    error_weight=2.0, stroke_size_scale=0.65),
        FeatureZone("fw_right_field", "fw_right_attachment", radius_nx=0.52, radius_ny=0.45,
                    error_weight=2.0, stroke_size_scale=0.65),
    ]

    flow_zones = [
        # Forewing — veins radiate from attachment outward to apex and trailing edge
        FlowZone("fw_left_radial", "diagonal",
                 {"nx_factor": -0.75, "ny_factor": -0.55, "anchor_nx": -0.08, "anchor_ny": -0.08},
                 weight_sigma_nx=0.48, weight_sigma_ny=0.45),
        FlowZone("fw_right_radial", "diagonal",
                 {"nx_factor": +0.75, "ny_factor": -0.55, "anchor_nx": +0.08, "anchor_ny": -0.08},
                 weight_sigma_nx=0.48, weight_sigma_ny=0.45),
        # Hindwing — veins radiate from attachment downward
        FlowZone("hw_left_radial", "diagonal",
                 {"nx_factor": -0.55, "ny_factor": 0.75, "anchor_nx": -0.10, "anchor_ny": +0.12},
                 weight_sigma_nx=0.40, weight_sigma_ny=0.45),
        FlowZone("hw_right_radial", "diagonal",
                 {"nx_factor": +0.55, "ny_factor": 0.75, "anchor_nx": +0.10, "anchor_ny": +0.12},
                 weight_sigma_nx=0.40, weight_sigma_ny=0.45),
        # Wing margins — strokes run along the wing edge
        FlowZone("fw_left_margin_flow", "orbital",
                 {"orbit_anchor": "fw_left_attachment", "orbit_nx": -0.08, "orbit_ny": -0.10},
                 weight_sigma_nx=0.80, weight_sigma_ny=0.55),
        # Body — vertical strokes along the body axis
        FlowZone("body", "fixed",
                 {"radians": math.pi / 2, "anchor_nx": 0.00, "anchor_ny": +0.12},
                 weight_sigma_nx=0.10, weight_sigma_ny=0.48),
    ]

    return SubjectAnatomy(
        subject_id=subject_id,
        display_name=display_name,
        landmarks=landmarks,
        feature_zones=feature_zones,
        flow_zones=flow_zones,
        proportions={
            "forewing_fraction":    0.60,
            "hindwing_fraction":    0.40,
            "wingspan_to_body":     5.0,
            "aspect_ratio":         1.15,
        },
    )


BUTTERFLY = _build("butterfly", "Butterfly (Dorsal, Wings Spread)", eyespot_weight=6.5)
MOTH      = _build("moth",      "Moth (Dorsal, Wings Spread)",      eyespot_weight=5.0, body_weight=4.0)
