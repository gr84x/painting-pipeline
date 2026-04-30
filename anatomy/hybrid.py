"""
Hybrid anatomy composition tools.

Allows combining, morphing, and modifying anatomy definitions to create
custom or fantastical creatures without defining them from scratch.

Core operations
---------------
blend_anatomies(sources)
    Weighted blend of two or more anatomies. Landmark positions are
    averaged by weight. Feature zones are merged (max error_weight wins).
    Flow zones are combined (all zones from all sources included, named
    by source to avoid collisions).

graft_zones(base, feature_grafts, flow_grafts)
    Surgical replacement: swap named feature or flow zones in a base
    anatomy with zones from another anatomy or a custom definition.

scale_feature_weights(source, scales)
    Multiply specific feature zone error_weights. Use to emphasise or
    de-emphasise individual features (e.g., make eyes owl-sized on a fox).

mirror_x(source)
    Flip the anatomy horizontally. Converts a left-facing 3/4 profile
    to a right-facing one by negating all nx coordinates.

add_landmarks(source, extras)
    Append additional landmarks without redefining the whole anatomy.
    Useful for creature-specific features (horns, extra eyes, tentacles).

Composition example — Griffin (eagle head, feline features):

    from anatomy import subjects
    from anatomy.hybrid import blend_anatomies, scale_feature_weights

    griffin = blend_anatomies(
        [(subjects.get("eagle"),  0.65),
         (subjects.get("lion"),   0.35)],
        subject_id="griffin",
        display_name="Griffin",
    )
"""
from __future__ import annotations
import math
import numpy as np
from dataclasses import replace
from .schema import (
    Landmark, FeatureZone, FlowZone, SubjectAnatomy,
)


# ── Blend ─────────────────────────────────────────────────────────────────────

def blend_anatomies(
    weighted_sources: list[tuple[SubjectAnatomy, float]],
    subject_id: str = "hybrid",
    display_name: str = "Hybrid Creature",
) -> SubjectAnatomy:
    """
    Create a new anatomy by blending two or more source anatomies.

    Landmark positions are weighted-averaged. Landmarks only present in
    one source are included at their original position (scaled by their
    source's weight, so they appear less prominently in the weight map).

    Feature zones: all zones from all sources are merged. Where names
    collide, the maximum error_weight wins and stroke_size/jitter/wet_blend
    are taken from the higher-weight zone. The merged zone is prefixed with
    the source subject_id to keep provenance clear.

    Flow zones: all zones are included, prefixed by source. The flow field
    builder blends them via weighted accumulation (weight_sigma controls
    spatial spread, so overlapping zones blend naturally).
    """
    if not weighted_sources:
        raise ValueError("At least one source required.")

    total_w = sum(w for _, w in weighted_sources)
    if total_w <= 0:
        raise ValueError("Total blend weight must be > 0.")
    norm_weights = [(a, w / total_w) for a, w in weighted_sources]

    # ── Landmarks ────────────────────────────────────────────────────────────
    landmark_map: dict[str, list[tuple[float, float, float]]] = {}  # name → [(nx,ny,weight)]
    for anat, w in norm_weights:
        for lm in anat.landmarks:
            landmark_map.setdefault(lm.name, []).append((lm.nx, lm.ny, w))

    blended_landmarks: list[Landmark] = []
    for name, entries in landmark_map.items():
        total = sum(e[2] for e in entries)
        nx = sum(e[0] * e[2] for e in entries) / total
        ny = sum(e[1] * e[2] for e in entries) / total
        blended_landmarks.append(Landmark(name=name, nx=nx, ny=ny))

    # ── Feature zones ─────────────────────────────────────────────────────────
    # Collect all zones; on name collision keep highest error_weight.
    fzone_map: dict[str, FeatureZone] = {}
    for anat, w in norm_weights:
        for fz in anat.feature_zones:
            key = fz.name
            if key not in fzone_map or fz.error_weight > fzone_map[key].error_weight:
                # Scale the weight by blend fraction so minority sources
                # contribute proportionally less emphasis
                scaled = _scale_fzone_weight(fz, w)
                fzone_map[key] = scaled
    blended_fzones = list(fzone_map.values())

    # ── Flow zones ────────────────────────────────────────────────────────────
    # Include all flow zones from all sources, disambiguating by source prefix.
    seen_flow: set[str] = set()
    blended_flow: list[FlowZone] = []
    for anat, w in norm_weights:
        for fz in anat.flow_zones:
            key = f"{anat.subject_id}__{fz.name}"
            if key not in seen_flow:
                seen_flow.add(key)
                # Reduce weight_sigma for minority contributors
                sigma_scale = math.sqrt(w)   # sqrt softens the reduction
                blended_flow.append(FlowZone(
                    name=key,
                    angle_type=fz.angle_type,
                    angle_params=fz.angle_params,
                    weight_sigma_nx=fz.weight_sigma_nx * sigma_scale,
                    weight_sigma_ny=fz.weight_sigma_ny * sigma_scale,
                ))

    # ── Proportions ───────────────────────────────────────────────────────────
    prop_map: dict[str, list[tuple[float, float]]] = {}
    for anat, w in norm_weights:
        for k, v in anat.proportions.items():
            prop_map.setdefault(k, []).append((v, w))
    blended_props = {
        k: sum(v * w for v, w in entries) / sum(w for _, w in entries)
        for k, entries in prop_map.items()
    }

    return SubjectAnatomy(
        subject_id=subject_id,
        display_name=display_name,
        landmarks=blended_landmarks,
        feature_zones=blended_fzones,
        flow_zones=blended_flow,
        proportions=blended_props,
    )


def _scale_fzone_weight(fz: FeatureZone, weight: float) -> FeatureZone:
    """Return a FeatureZone with error_weight scaled by blend weight."""
    # Clamp to at least 1.0 (base weight) to avoid actively suppressing areas
    new_w = max(1.0, 1.0 + (fz.error_weight - 1.0) * weight)
    return FeatureZone(
        name=fz.name, anchor=fz.anchor,
        radius_nx=fz.radius_nx, radius_ny=fz.radius_ny,
        error_weight=new_w,
        stroke_size_scale=fz.stroke_size_scale,
        jitter_scale=fz.jitter_scale,
        wet_blend_scale=fz.wet_blend_scale,
    )


# ── Graft ─────────────────────────────────────────────────────────────────────

def graft_feature_zones(
    base: SubjectAnatomy,
    replacements: dict[str, FeatureZone] | None = None,
    additions: list[FeatureZone] | None = None,
    removals: set[str] | None = None,
) -> SubjectAnatomy:
    """
    Surgically modify feature zones on a base anatomy.

    replacements : map of zone_name → new FeatureZone (replaces existing)
    additions    : list of new FeatureZones to append
    removals     : set of zone names to delete
    """
    zones = list(base.feature_zones)
    if removals:
        zones = [z for z in zones if z.name not in removals]
    if replacements:
        zones = [replacements.get(z.name, z) for z in zones]
    if additions:
        zones = zones + list(additions)
    return _copy_anatomy(base, feature_zones=zones)


def graft_flow_zones(
    base: SubjectAnatomy,
    replacements: dict[str, FlowZone] | None = None,
    additions: list[FlowZone] | None = None,
    removals: set[str] | None = None,
) -> SubjectAnatomy:
    """Surgically modify flow zones on a base anatomy."""
    zones = list(base.flow_zones)
    if removals:
        zones = [z for z in zones if z.name not in removals]
    if replacements:
        zones = [replacements.get(z.name, z) for z in zones]
    if additions:
        zones = zones + list(additions)
    return _copy_anatomy(base, flow_zones=zones)


# ── Scale ─────────────────────────────────────────────────────────────────────

def scale_feature_weights(
    source: SubjectAnatomy,
    scales: dict[str, float],
) -> SubjectAnatomy:
    """
    Multiply the error_weight of named feature zones.

    scales: {zone_name: multiplier}
      > 1.0 — attract more strokes (emphasise this feature)
      < 1.0 — attract fewer strokes (de-emphasise)
      0.0   — effectively remove the weighting (reduce to base weight 1.0)

    Example — give a fox owl-sized eyes:
        from anatomy.hybrid import scale_feature_weights
        from anatomy import subjects
        mystical_fox = scale_feature_weights(
            subjects.get("fox"), {"near_eye": 2.5, "far_eye": 2.0}
        )
    """
    def _scale(fz: FeatureZone) -> FeatureZone:
        if fz.name not in scales:
            return fz
        m = scales[fz.name]
        new_w = max(1.0, 1.0 + (fz.error_weight - 1.0) * m)
        return FeatureZone(
            name=fz.name, anchor=fz.anchor,
            radius_nx=fz.radius_nx, radius_ny=fz.radius_ny,
            error_weight=new_w,
            stroke_size_scale=fz.stroke_size_scale,
            jitter_scale=fz.jitter_scale,
            wet_blend_scale=fz.wet_blend_scale,
        )
    return _copy_anatomy(source, feature_zones=[_scale(z) for z in source.feature_zones])


# ── Mirror ────────────────────────────────────────────────────────────────────

def mirror_x(source: SubjectAnatomy, new_id: str | None = None) -> SubjectAnatomy:
    """
    Flip the anatomy horizontally (negate all nx values).

    Converts a left-facing 3/4 profile to a right-facing one.
    Flow zone angle_params containing orbit_nx or anchor_nx are also mirrored.
    """
    def _mirror_lm(lm: Landmark) -> Landmark:
        return Landmark(name=lm.name, nx=-lm.nx, ny=lm.ny)

    def _mirror_fz(fz: FeatureZone) -> FeatureZone:
        return fz   # FeatureZone uses anchor landmark name — landmark already mirrored

    def _mirror_flow(fz: FlowZone) -> FlowZone:
        p = dict(fz.angle_params)
        if "orbit_nx" in p:
            p["orbit_nx"] = -p["orbit_nx"]
        if "anchor_nx" in p:
            p["anchor_nx"] = -p["anchor_nx"]
        if "nx_factor" in p:
            p["nx_factor"] = -p["nx_factor"]
        if fz.angle_type == "fixed" and "radians" in p:
            p["radians"] = math.pi - p["radians"]
        return FlowZone(name=fz.name, angle_type=fz.angle_type, angle_params=p,
                        weight_sigma_nx=fz.weight_sigma_nx, weight_sigma_ny=fz.weight_sigma_ny)

    sid = new_id or (source.subject_id + "_mirrored")
    return SubjectAnatomy(
        subject_id=sid,
        display_name=source.display_name + " (Mirrored)",
        landmarks=[_mirror_lm(lm) for lm in source.landmarks],
        feature_zones=[_mirror_fz(fz) for fz in source.feature_zones],
        flow_zones=[_mirror_flow(fz) for fz in source.flow_zones],
        proportions=dict(source.proportions),
    )


# ── Add landmarks ─────────────────────────────────────────────────────────────

def add_landmarks(
    source: SubjectAnatomy,
    extras: list[Landmark],
) -> SubjectAnatomy:
    """Append additional landmarks to an anatomy (e.g. horns, extra eyes)."""
    return _copy_anatomy(source, landmarks=list(source.landmarks) + list(extras))


# ── Internal helper ───────────────────────────────────────────────────────────

def _copy_anatomy(
    source: SubjectAnatomy,
    *,
    landmarks=None,
    feature_zones=None,
    flow_zones=None,
) -> SubjectAnatomy:
    return SubjectAnatomy(
        subject_id=source.subject_id,
        display_name=source.display_name,
        landmarks=landmarks if landmarks is not None else list(source.landmarks),
        feature_zones=feature_zones if feature_zones is not None else list(source.feature_zones),
        flow_zones=flow_zones if flow_zones is not None else list(source.flow_zones),
        proportions=dict(source.proportions),
    )
