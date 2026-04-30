"""
Core data types for the anatomy database.

All coordinates are in normalized subject space:
  nx ∈ [-1, +1]  — left edge to right edge of the bounding ellipse
  ny ∈ [-1, +1]  — top edge to bottom edge of the bounding ellipse
  (0, 0) = center of the bounding ellipse

Flow zones describe stroke *direction* (how the brush moves across a region).
Feature zones describe stroke *density* (where the error map is upweighted).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Landmark:
    """A named anatomical point in normalized subject space."""
    name: str
    nx: float
    ny: float


@dataclass(frozen=True)
class FeatureZone:
    """
    A perceptually important region that should attract disproportionately
    more strokes. The weight map contributes a Gaussian bump centred on
    *anchor*, decaying to 1.0 at the zone boundary.

    error_weight    — peak multiplier for the error map at the anchor point.
                      Eyes: 5–7. Nose/mouth: 3–5. Fur texture zones: 1.5–2.
    stroke_size_scale — override stroke size for dedicated feature passes.
                        < 1.0 = finer brush in this zone.
    jitter_scale    — < 1.0 = tighter colour fidelity in this zone.
    wet_blend_scale — < 1.0 = less blending, crisper edges in this zone.
    """
    name: str
    anchor: str        # name of the Landmark at this zone's centre
    radius_nx: float   # half-width in normalized units
    radius_ny: float   # half-height in normalized units
    error_weight: float
    stroke_size_scale: float = 1.0
    jitter_scale: float = 1.0
    wet_blend_scale: float = 1.0


@dataclass(frozen=True)
class FlowZone:
    """
    A region with a defined stroke direction, blended smoothly with
    neighbouring zones.

    angle_type — one of:
        "fixed"             : constant angle (angle_params["radians"])
        "diagonal"          : arctan2(nx_factor, ny_factor) per pixel
        "orbital"           : tangent to an ellipse around a landmark
                              (angle_params["orbit_anchor"])
        "gradient_fallback" : use the reference image gradient (no params)

    weight_sigma_nx, weight_sigma_ny — Gaussian falloff for zone blending
        in normalized space. Larger = softer boundary with neighbours.
    """
    name: str
    angle_type: str
    angle_params: dict
    weight_sigma_nx: float = 0.35
    weight_sigma_ny: float = 0.35


@dataclass
class SubjectAnatomy:
    """
    Full anatomy definition for one subject type, expressed in normalized
    [-1, 1] space relative to the subject's bounding ellipse.
    """
    subject_id: str
    display_name: str
    landmarks: list[Landmark]
    feature_zones: list[FeatureZone]
    flow_zones: list[FlowZone]
    # Species-level proportional constants (informational; used by make_reference)
    proportions: dict[str, float] = field(default_factory=dict)

    def landmark(self, name: str) -> Optional[Landmark]:
        for lm in self.landmarks:
            if lm.name == name:
                return lm
        return None


@dataclass
class PlacedAnatomy:
    """
    A SubjectAnatomy anchored to pixel coordinates on a specific canvas.

    The normalized-to-pixel transform is:
        px = cx + nx * rx
        py = cy + ny * ry
    """
    anatomy: SubjectAnatomy
    cx: float   # bounding ellipse centre x (pixels)
    cy: float   # bounding ellipse centre y (pixels)
    rx: float   # bounding ellipse half-width (pixels)
    ry: float   # bounding ellipse half-height (pixels)

    def to_pixels(self, nx: float, ny: float) -> tuple[float, float]:
        return self.cx + nx * self.rx, self.cy + ny * self.ry

    def to_normalized(self, px: float, py: float) -> tuple[float, float]:
        return (
            (px - self.cx) / (self.rx + 1e-6),
            (py - self.cy) / (self.ry + 1e-6),
        )
