"""
Anatomy-aware flow field generation.

build_anatomy_flow_field() is the generalized version of the existing
anatomy_flow_field() in stroke_engine.py. It accepts a PlacedAnatomy
and computes per-pixel stroke angles from the subject's FlowZone definitions,
blending zones smoothly and falling back to the image gradient field outside
the subject's bounding ellipse.

Angle convention matches stroke_engine: radians, 0 = rightward, π/2 = downward.
"""
from __future__ import annotations
import math
import numpy as np
from scipy.ndimage import gaussian_filter
from .schema import PlacedAnatomy, FlowZone


# ── Per-zone angle computation ────────────────────────────────────────────────

def _angle_fixed(nx: np.ndarray, ny: np.ndarray, params: dict) -> np.ndarray:
    return np.full_like(nx, params["radians"], dtype=np.float32)


def _angle_diagonal(nx: np.ndarray, ny: np.ndarray, params: dict) -> np.ndarray:
    """arctan2(nx_factor * nx, ny_factor) — strokes run diagonally across the form."""
    nxf = params.get("nx_factor", 1.0)
    nyf = params.get("ny_factor", 1.0)
    return np.arctan2(nxf * nx, nyf * np.ones_like(ny) * nyf).astype(np.float32)


def _angle_orbital(nx: np.ndarray, ny: np.ndarray, params: dict,
                   placed: PlacedAnatomy) -> np.ndarray:
    """Tangent to an ellipse centred on an anchor landmark — strokes orbit the feature."""
    anchor_name = params["orbit_anchor"]
    anchor = placed.anatomy.landmark(anchor_name)
    if anchor is None:
        return np.zeros_like(nx, dtype=np.float32)

    orb_nx = params.get("orbit_nx", anchor.nx)
    orb_ny = params.get("orbit_ny", anchor.ny)

    # Radial vector from orbit centre; tangent is perpendicular to it
    dx = nx - orb_nx
    dy = ny - orb_ny
    return np.arctan2(dx, -dy).astype(np.float32)


def _compute_zone_angle(zone: FlowZone, nx: np.ndarray, ny: np.ndarray,
                        placed: PlacedAnatomy) -> np.ndarray:
    t = zone.angle_type
    p = zone.angle_params
    if t == "fixed":
        return _angle_fixed(nx, ny, p)
    elif t == "diagonal":
        return _angle_diagonal(nx, ny, p)
    elif t == "orbital":
        return _angle_orbital(nx, ny, p, placed)
    elif t == "gradient_fallback":
        # Sentinel — handled in the main builder; return zeros as placeholder
        return np.zeros_like(nx, dtype=np.float32)
    else:
        raise ValueError(f"Unknown FlowZone angle_type: {t!r}")


# ── Zone blend weights ────────────────────────────────────────────────────────

def _zone_weight(zone: FlowZone, nx: np.ndarray, ny: np.ndarray,
                 placed: PlacedAnatomy) -> np.ndarray:
    """
    Gaussian weight field for a zone's blending contribution.
    The zone centre is defined by the orbit_anchor landmark (if orbital)
    or the zone's own anchor_nx / anchor_ny params.
    """
    p = zone.angle_params

    if zone.angle_type == "orbital" and "orbit_anchor" in p:
        anchor = placed.anatomy.landmark(p["orbit_anchor"])
        cnx = anchor.nx if anchor else 0.0
        cny = anchor.ny if anchor else 0.0
    else:
        cnx = p.get("anchor_nx", 0.0)
        cny = p.get("anchor_ny", 0.0)

    dx = (nx - cnx) / (zone.weight_sigma_nx + 1e-6)
    dy = (ny - cny) / (zone.weight_sigma_ny + 1e-6)
    return np.exp(-(dx ** 2 + dy ** 2) * 0.5).astype(np.float32)


# ── Main builder ──────────────────────────────────────────────────────────────

def build_anatomy_flow_field(
    canvas_w: int,
    canvas_h: int,
    placed: PlacedAnatomy,
    gradient_fallback: np.ndarray | None = None,
    smooth_sigma: float = 3.5,
    falloff_start: float = 0.85,
    falloff_end: float = 1.20,
) -> np.ndarray:
    """
    Build a (H, W) float32 flow field from a PlacedAnatomy definition.

    Each FlowZone contributes a Gaussian-weighted angle. Zones blend via
    sin/cos averaging to avoid wrap-around discontinuities. Outside the
    subject ellipse (d > falloff_start), the field blends smoothly into
    gradient_fallback. A final Gaussian smooth removes blending artefacts.

    Parameters
    ----------
    gradient_fallback : (H, W) float32 from flow_field(ref) in stroke_engine.
                        Used outside the anatomy ellipse. If None, defaults
                        to 0.0 (horizontal strokes) at the boundary.
    smooth_sigma      : Final smoothing in pixels; matches anatomy_flow_field().
    falloff_start     : Normalized ellipse distance at which blending begins.
    falloff_end       : Normalized distance at which anatomy field is fully off.

    Returns
    -------
    angles : (H, W) float32 in radians.
    """
    ys = np.arange(canvas_h, dtype=np.float32)[:, np.newaxis]
    xs = np.arange(canvas_w, dtype=np.float32)[np.newaxis, :]

    # Normalized coordinates relative to the placed anatomy's bounding ellipse
    nx = (xs - placed.cx) / (placed.rx + 1e-6)
    ny = (ys - placed.cy) / (placed.ry + 1e-6)
    d = np.sqrt(nx ** 2 + ny ** 2)

    # Blend all flow zones via weighted sin/cos accumulation
    sin_acc = np.zeros((canvas_h, canvas_w), dtype=np.float32)
    cos_acc = np.zeros((canvas_h, canvas_w), dtype=np.float32)
    weight_acc = np.zeros((canvas_h, canvas_w), dtype=np.float32)

    for zone in placed.anatomy.flow_zones:
        if zone.angle_type == "gradient_fallback":
            continue  # handled separately below
        a = _compute_zone_angle(zone, nx, ny, placed)
        w = _zone_weight(zone, nx, ny, placed)
        sin_acc += w * np.sin(a)
        cos_acc += w * np.cos(a)
        weight_acc += w

    # Normalize accumulated anatomy field
    denom = weight_acc + 1e-6
    anatomy_angles = np.arctan2(sin_acc / denom, cos_acc / denom).astype(np.float32)

    # Blend toward gradient_fallback outside the ellipse
    fallback = gradient_fallback if gradient_fallback is not None else np.zeros_like(anatomy_angles)

    # smoothstep blend: 0 inside ellipse, 1 outside
    t = np.clip((d - falloff_start) / (falloff_end - falloff_start + 1e-6), 0.0, 1.0)
    t = (t * t * (3.0 - 2.0 * t)).astype(np.float32)  # smoothstep

    # Blend in sin/cos space to avoid angle wrap artefacts
    sa = (1 - t) * np.sin(anatomy_angles) + t * np.sin(fallback)
    ca = (1 - t) * np.cos(anatomy_angles) + t * np.cos(fallback)
    angles = np.arctan2(sa, ca).astype(np.float32)

    # Final smooth to remove zone boundary noise
    if smooth_sigma > 0:
        angles = gaussian_filter(angles, sigma=smooth_sigma).astype(np.float32)

    return angles
