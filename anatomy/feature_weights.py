"""
Feature-weighted error map generation.

build_feature_weight_map() returns a (H, W) float32 array where
perceptually critical zones (eyes, nose, mouth) have values > 1.0.
When multiplied against the guided-filtered error map in _place_strokes(),
strokes cluster in feature zones proportionally to their error_weight.

The weight map is intended to be assigned to painter._comp_map (or
multiplied into it if an existing composition map is present).
"""
from __future__ import annotations
import numpy as np
from .schema import PlacedAnatomy


def build_feature_weight_map(
    placed: PlacedAnatomy,
    canvas_w: int,
    canvas_h: int,
    base_weight: float = 1.0,
    gaussian_sigma: float = 2.0,
) -> np.ndarray:
    """
    Build a (H, W) float32 weight map for a placed subject.

    Each FeatureZone contributes a Gaussian bump centred on its anchor
    landmark. The bump peaks at zone.error_weight and decays toward
    base_weight at approximately 1 normalized radius from the centre.

    gaussian_sigma — controls the sharpness of the bump falloff. Higher
                     values spread the emphasis over a wider area; lower
                     values concentrate it tightly on the feature centre.
                     Expressed in units of the zone radius (not pixels).

    Returns
    -------
    weight_map : (H, W) float32
        Values >= base_weight. Suitable for use as composition_map in
        _place_strokes(), or for direct assignment to painter._comp_map.
    """
    weights = np.full((canvas_h, canvas_w), base_weight, dtype=np.float32)

    ys = np.arange(canvas_h, dtype=np.float32)[:, np.newaxis]  # (H, 1)
    xs = np.arange(canvas_w, dtype=np.float32)[np.newaxis, :]  # (1, W)

    for zone in placed.anatomy.feature_zones:
        anchor = placed.anatomy.landmark(zone.anchor)
        if anchor is None:
            continue

        centre_px, centre_py = placed.to_pixels(anchor.nx, anchor.ny)
        rx_px = zone.radius_nx * placed.rx
        ry_px = zone.radius_ny * placed.ry

        if rx_px < 1e-3 or ry_px < 1e-3:
            continue

        # Normalized distance from zone centre (1.0 = at the zone boundary)
        dx_norm = (xs - centre_px) / rx_px
        dy_norm = (ys - centre_py) / ry_px
        d2 = dx_norm ** 2 + dy_norm ** 2

        # Gaussian bump: peak = zone.error_weight, falls to base_weight as d→∞
        excess = zone.error_weight - base_weight
        bump = base_weight + excess * np.exp(-d2 / (2.0 * gaussian_sigma ** 2))

        # Take the maximum so overlapping zones don't cancel each other
        weights = np.maximum(weights, bump.astype(np.float32))

    return weights


def build_combined_weight_map(
    placed_subjects: list[PlacedAnatomy],
    canvas_w: int,
    canvas_h: int,
    base_weight: float = 1.0,
    gaussian_sigma: float = 2.0,
) -> np.ndarray | None:
    """
    Build a single (H, W) float32 weight map from multiple placed subjects.

    Each subject's feature zones contribute Gaussian bumps. Where subjects
    overlap, the maximum weight wins (so one subject's eyes don't reduce
    emphasis on another's). Returns None if placed_subjects is empty,
    which signals the caller to skip setting painter._comp_map.

    This is the standard entry point for session scripts:

        ref, placed_subjects = make_reference()
        weight_map = build_combined_weight_map(placed_subjects, W, H)
        if weight_map is not None:
            painter._comp_map = weight_map
    """
    if not placed_subjects:
        return None

    combined = np.full((canvas_h, canvas_w), base_weight, dtype=np.float32)
    for placed in placed_subjects:
        subject_map = build_feature_weight_map(
            placed, canvas_w, canvas_h,
            base_weight=base_weight,
            gaussian_sigma=gaussian_sigma,
        )
        combined = np.maximum(combined, subject_map)
    return combined


def combine_with_composition_map(
    feature_map: np.ndarray,
    composition_map: np.ndarray | None,
) -> np.ndarray:
    """
    Multiply feature_map with an existing composition map (rule-of-thirds
    bias, etc.) so both influences are active simultaneously.

    If composition_map is None, returns feature_map unchanged.
    """
    if composition_map is None:
        return feature_map
    return (feature_map * composition_map).astype(np.float32)
