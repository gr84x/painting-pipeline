"""
reference_builder.py — Synthetic reference image builder.

Builds H×W×3 float32 references in [0, 1] without external photos, using
hard-edged geometric primitives, direction-aware lighting, and distance fields.

Design intent
-------------
Hard geometric edges + multi-light shading produce high-contrast luma
boundaries that the stroke engine can reliably follow. The soft distance-field
approach (used in the s187 owl) produced weak placement signals; this builder
defaults to hard clip edges via ``soft_edges=0.0`` in ReferenceSpec.

Key outputs
-----------
build_portrait()     — head + shoulders, centered
build_creature()     — generic body + head (bird, animal)
build_subject_mask() — luminance-threshold mask (H×W float32)
build_direction_field() — tangent-to-luma-gradient field (H×W×2 float32)
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter


# ─────────────────────────────────────────────────────────────────────────────
# Primitive shape masks
# ─────────────────────────────────────────────────────────────────────────────

def ellipse_mask(H: int, W: int,
                 cy: float, cx: float,
                 ry: float, rx: float,
                 soft: float = 0.0) -> np.ndarray:
    """Filled ellipse. cy/cx are fractional [0,1]; ry/rx are pixel radii.

    soft=0 gives a hard binary edge; soft>0 blurs the boundary with that sigma.
    """
    ys = np.arange(H, dtype=np.float32)
    xs = np.arange(W, dtype=np.float32)
    YY, XX = np.meshgrid(ys, xs, indexing='ij')
    dist = np.sqrt(((YY - cy * H) / (ry + 1e-6)) ** 2 +
                   ((XX - cx * W) / (rx + 1e-6)) ** 2)
    if soft > 0.0:
        mask = np.clip(1.0 - dist, 0.0, 1.0).astype(np.float32)
        return np.clip(gaussian_filter(mask, sigma=soft), 0.0, 1.0)
    return (dist <= 1.0).astype(np.float32)


def rect_mask(H: int, W: int,
              y0: float, x0: float,
              y1: float, x1: float,
              soft: float = 0.0) -> np.ndarray:
    """Filled rectangle. All coordinates are fractional [0,1]."""
    ys = np.arange(H, dtype=np.float32) / H
    xs = np.arange(W, dtype=np.float32) / W
    YY, XX = np.meshgrid(ys, xs, indexing='ij')
    mask = ((YY >= y0) & (YY <= y1) & (XX >= x0) & (XX <= x1)).astype(np.float32)
    if soft > 0.0:
        mask = np.clip(gaussian_filter(mask, sigma=soft), 0.0, 1.0)
    return mask


def gradient_field(H: int, W: int,
                   direction: str = "top_to_bottom",
                   lo: float = 0.0, hi: float = 1.0) -> np.ndarray:
    """Linear or radial gradient field (H×W float32)."""
    if direction == "top_to_bottom":
        g = np.linspace(hi, lo, H, dtype=np.float32).reshape(-1, 1) * np.ones((1, W))
    elif direction == "bottom_to_top":
        g = np.linspace(lo, hi, H, dtype=np.float32).reshape(-1, 1) * np.ones((1, W))
    elif direction == "left_to_right":
        g = np.linspace(lo, hi, W, dtype=np.float32).reshape(1, -1) * np.ones((H, 1))
    elif direction == "radial":
        ys = (np.arange(H) / H - 0.5) * 2
        xs = (np.arange(W) / W - 0.5) * 2
        YY, XX = np.meshgrid(ys, xs, indexing='ij')
        g = np.clip(1.0 - np.sqrt(YY ** 2 + XX ** 2), 0.0, 1.0).astype(np.float32)
        g = g * (hi - lo) + lo
    else:
        raise ValueError(f"Unknown gradient direction: {direction!r}")
    return g.astype(np.float32)


# ─────────────────────────────────────────────────────────────────────────────
# Light rig
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LightSource:
    """Directional light for Lambertian shading of synthetic references."""
    direction: Tuple[float, float, float] = (0.6, -0.8, 0.5)
    color:     Tuple[float, float, float] = (1.0, 0.95, 0.85)
    intensity: float = 1.0

    def shade(self, normals: np.ndarray) -> np.ndarray:
        """Return H×W Lambertian shade factor given H×W×3 unit normal field."""
        dx, dy, dz = self.direction
        mag = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2) + 1e-8
        L = np.array([dx / mag, dy / mag, dz / mag], dtype=np.float32)
        return np.clip(normals @ L, 0.0, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# Reference specification
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ReferenceSpec:
    """Specification for a synthetic reference image."""
    H:             int   = 1080
    W:             int   = 780
    subject_frac:  float = 0.65   # fraction of short axis for primary subject
    bg_color:      Tuple[float, float, float] = (0.12, 0.10, 0.08)
    subject_color: Tuple[float, float, float] = (0.72, 0.55, 0.38)
    light_angle:   float = -0.6   # radians from horizontal
    ambient:       float = 0.18
    soft_edges:    float = 0.0    # 0 = hard; >0 = edge blur sigma


# ─────────────────────────────────────────────────────────────────────────────
# ReferenceBuilder
# ─────────────────────────────────────────────────────────────────────────────

class ReferenceBuilder:
    """
    Builds synthetic reference images without external photos.

    Hard geometric edges + multi-light shading produce clear luma boundaries
    that guide stroke placement reliably. Pass ``soft_edges=0.0`` (default) for
    maximum sharpness; increase it only when a soft atmospheric look is wanted.
    """

    def __init__(self, spec: Optional[ReferenceSpec] = None):
        self.spec = spec or ReferenceSpec()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sphere_normals(self, H: int, W: int,
                        cy: float, cx: float,
                        ry: float, rx: float) -> np.ndarray:
        """Approximate sphere normal field (H×W×3 float32, unit vectors)."""
        ys = np.arange(H, dtype=np.float32)
        xs = np.arange(W, dtype=np.float32)
        YY, XX = np.meshgrid(ys, xs, indexing='ij')
        ny = (YY - cy * H) / (ry + 1e-6)
        nx = (XX - cx * W) / (rx + 1e-6)
        r2 = np.clip(ny ** 2 + nx ** 2, 0.0, 1.0)
        nz = np.sqrt(np.clip(1.0 - r2, 0.0, 1.0))
        normals = np.stack([-ny, -nx, nz], axis=-1).astype(np.float32)
        mag = np.linalg.norm(normals, axis=-1, keepdims=True) + 1e-8
        return normals / mag

    def _key_light(self, angle: float, intensity: float = 0.85) -> LightSource:
        return LightSource(
            direction=(math.cos(angle), -0.3, 0.7),
            color=(1.0, 0.95, 0.85),
            intensity=intensity,
        )

    # ------------------------------------------------------------------
    # Public builders
    # ------------------------------------------------------------------

    def build_portrait(self) -> np.ndarray:
        """
        Portrait-orientation reference: head + shoulders, centered.

        Returns H×W×3 float32 in [0, 1] with hard-edged head ellipse and
        shoulder block — strong luma boundaries for stroke placement.
        """
        spec = self.spec
        H, W = spec.H, spec.W
        ref = np.zeros((H, W, 3), dtype=np.float32)

        # Background gradient (dark at bottom, lighter at top)
        bg = gradient_field(H, W, "top_to_bottom", lo=0.6, hi=1.0)
        for c in range(3):
            ref[:, :, c] = bg * spec.bg_color[c]

        # Head: upper-center ellipse
        head_cy = 0.35
        head_cx = 0.50
        head_ry = H * spec.subject_frac * 0.25
        head_rx = head_ry * 0.80

        normals = self._sphere_normals(H, W, head_cy, head_cx, head_ry, head_rx)
        shading = self._key_light(spec.light_angle).shade(normals)
        head_mask = ellipse_mask(H, W, head_cy, head_cx, head_ry, head_rx,
                                  soft=spec.soft_edges)

        for c, sc in enumerate(spec.subject_color):
            lit = sc * (shading + spec.ambient)
            ref[:, :, c] = ref[:, :, c] * (1 - head_mask) + lit * head_mask

        # Shoulders: lower rectangle
        shoulder_mask = rect_mask(H, W, 0.55, 0.15, 1.00, 0.85,
                                   soft=spec.soft_edges)
        shoulder_color = tuple(c * 0.60 for c in spec.subject_color)
        for c, sc in enumerate(shoulder_color):
            ref[:, :, c] = ref[:, :, c] * (1 - shoulder_mask) + sc * shoulder_mask

        return np.clip(ref, 0.0, 1.0).astype(np.float32)

    def build_creature(
        self,
        body_cy: float = 0.55,
        body_cx: float = 0.50,
        body_ry_frac: float = 0.28,
        body_rx_frac: float = 0.20,
        head_offset_y: float = -0.22,
        head_scale: float = 0.55,
    ) -> np.ndarray:
        """
        Generic creature reference: body ellipse + head ellipse.

        Returns H×W×3 float32 in [0, 1]. Works for birds, mammals, reptiles —
        adjust body_ry_frac / head_scale for the specific subject.
        """
        spec = self.spec
        H, W = spec.H, spec.W
        ref = np.zeros((H, W, 3), dtype=np.float32)

        # Background
        bg = gradient_field(H, W, "top_to_bottom", lo=0.3, hi=0.9)
        for c in range(3):
            ref[:, :, c] = bg * spec.bg_color[c]

        body_ry = H * body_ry_frac
        body_rx = W * body_rx_frac
        body_mask = ellipse_mask(H, W, body_cy, body_cx, body_ry, body_rx,
                                  soft=spec.soft_edges)
        normals  = self._sphere_normals(H, W, body_cy, body_cx, body_ry, body_rx)
        shading  = self._key_light(spec.light_angle, 0.80).shade(normals)

        for c, sc in enumerate(spec.subject_color):
            lit = sc * (shading + spec.ambient)
            ref[:, :, c] = ref[:, :, c] * (1 - body_mask) + lit * body_mask

        # Head
        head_cy = body_cy + head_offset_y
        head_ry = body_ry * head_scale
        head_rx = body_rx * head_scale
        head_mask   = ellipse_mask(H, W, head_cy, body_cx, head_ry, head_rx,
                                    soft=spec.soft_edges)
        head_normals = self._sphere_normals(H, W, head_cy, body_cx, head_ry, head_rx)
        head_shading = self._key_light(spec.light_angle, 0.85).shade(head_normals)
        head_color   = tuple(c * 0.90 for c in spec.subject_color)

        for c, sc in enumerate(head_color):
            lit = sc * (head_shading + spec.ambient)
            ref[:, :, c] = ref[:, :, c] * (1 - head_mask) + lit * head_mask

        return np.clip(ref, 0.0, 1.0).astype(np.float32)

    def build_subject_mask(self, reference: np.ndarray,
                            threshold: float = 0.30,
                            sigma: float = 2.0) -> np.ndarray:
        """
        Luminance-threshold binary mask from a reference image.

        Returns H×W float32 in [0, 1].
        """
        luma = (0.2126 * reference[:, :, 0] +
                0.7152 * reference[:, :, 1] +
                0.0722 * reference[:, :, 2])
        luma_s = gaussian_filter(luma, sigma=sigma)
        mask   = (luma_s > threshold).astype(np.float32)
        mask   = gaussian_filter(mask, sigma=sigma * 0.5)
        return np.clip(mask, 0.0, 1.0).astype(np.float32)

    def build_direction_field(self, reference: np.ndarray,
                               sigma: float = 3.0) -> np.ndarray:
        """
        Direction field tangent to the luma gradient of the reference.

        Returns H×W×2 float32 — [dy_tangent, dx_tangent] per pixel.
        A brush following this field paints *along* forms rather than across them.
        """
        luma   = (0.2126 * reference[:, :, 0] +
                  0.7152 * reference[:, :, 1] +
                  0.0722 * reference[:, :, 2])
        luma_s = gaussian_filter(luma, sigma=sigma)
        gy, gx = np.gradient(luma_s)
        # Tangent = rotate gradient 90°
        ty, tx = -gx, gy
        mag    = np.sqrt(ty ** 2 + tx ** 2) + 1e-8
        return np.stack([ty / mag, tx / mag], axis=-1).astype(np.float32)
