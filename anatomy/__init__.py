"""
Anatomy database for the painting pipeline.

Usage
-----
from anatomy import subjects, PlacedAnatomy, build_feature_weight_map

fox_anatomy = subjects.get("fox")
placed = PlacedAnatomy(anatomy=fox_anatomy, cx=head_cx, cy=head_cy, rx=hrx, ry=hry)
weight_map = build_feature_weight_map(placed, canvas_w=W, canvas_h=H)

# Apply to painter before painting passes begin
painter._comp_map = weight_map
"""
from .schema import (
    Landmark,
    FeatureZone,
    FlowZone,
    SubjectAnatomy,
    PlacedAnatomy,
)
from .feature_weights import build_feature_weight_map, build_combined_weight_map, combine_with_composition_map
from .flow_fields import build_anatomy_flow_field
from . import subjects
from . import hybrid

__all__ = [
    "Landmark",
    "FeatureZone",
    "FlowZone",
    "SubjectAnatomy",
    "PlacedAnatomy",
    "build_feature_weight_map",
    "build_combined_weight_map",
    "combine_with_composition_map",
    "build_anatomy_flow_field",
    "subjects",
    "hybrid",
]
