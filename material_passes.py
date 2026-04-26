"""
material_passes.py — World-class surface material rendering passes.

Each MaterialPass models the optical behavior of a distinct surface material:
the subsurface scattering of skin, the iridescent vane structure of feathers,
the layered sheen of fur, the tesselated reflectance of scales, and the
woven microgeometry of fabric.

All passes operate on a pycairo ImageSurface (ARGB32/BGRA) and accept an
optional subject mask (H×W float32) to restrict their effect to the painted
subject.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.ndimage import gaussian_filter


# ─────────────────────────────────────────────────────────────────────────────
# Shared parameters + abstract base
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MaterialParams:
    """Shared parameters for all material passes."""
    opacity:         float                    = 0.35
    subject_mask:    Optional[np.ndarray]     = None   # H×W float32 [0,1]
    direction_field: Optional[np.ndarray]     = None   # H×W×2 float32


class MaterialPass(ABC):
    """Abstract base for surface material rendering passes."""

    def __init__(self, params: Optional[MaterialParams] = None):
        self.params = params or MaterialParams()

    def _get_buf(self, surface) -> np.ndarray:
        W = surface.get_width()
        H = surface.get_height()
        return np.frombuffer(surface.get_data(),
                             dtype=np.uint8).reshape((H, W, 4)).copy()

    def _put_buf(self, surface, buf: np.ndarray) -> None:
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

    def _mask(self, H: int, W: int) -> np.ndarray:
        if self.params.subject_mask is not None:
            m = np.asarray(self.params.subject_mask, dtype=np.float32)
            if m.shape != (H, W):
                from scipy.ndimage import zoom
                m = zoom(m, (H / m.shape[0], W / m.shape[1]))
            return np.clip(m, 0.0, 1.0)
        return np.ones((H, W), dtype=np.float32)

    @abstractmethod
    def apply(self, surface, **kwargs) -> None:
        """Apply material pass in-place to a pycairo ImageSurface."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# SkinPass — subsurface scattering + pore micro-texture
# ─────────────────────────────────────────────────────────────────────────────

class SkinPass(MaterialPass):
    """
    Skin surface material.

    1. Subsurface scattering (SSS): red-channel warm bleed through thin skin.
       Approximated by blurring the red channel significantly more than green/blue
       then compositing back — the classic translucency look at ear rims,
       nostrils, and lit cheeks.
    2. Pore micro-texture: a fine Gaussian-filtered noise field that kills the
       plastic smoothness of a uniform render without adding photographic grain.
    """

    def __init__(self, params: Optional[MaterialParams] = None,
                 sss_radius: float = 8.0,
                 sss_strength: float = 0.18,
                 pore_scale: float = 1.5,
                 pore_strength: float = 0.04):
        super().__init__(params)
        self.sss_radius = sss_radius
        self.sss_strength = sss_strength
        self.pore_scale = pore_scale
        self.pore_strength = pore_strength

    def apply(self, surface, **kwargs) -> None:
        buf = self._get_buf(surface)
        H, W = buf.shape[:2]
        mask = self._mask(H, W)
        op = float(self.params.opacity)

        b = buf[:, :, 0].astype(np.float32) / 255.0
        g = buf[:, :, 1].astype(np.float32) / 255.0
        r = buf[:, :, 2].astype(np.float32) / 255.0

        # SSS: differential blur by channel
        r_sss = r + (gaussian_filter(r, self.sss_radius) - r) * self.sss_strength
        g_sss = g + (gaussian_filter(g, self.sss_radius * 0.5) - g) * self.sss_strength * 0.4
        b_sss = b + (gaussian_filter(b, self.sss_radius * 0.3) - b) * self.sss_strength * 0.15

        # Pore micro-texture
        rng   = np.random.default_rng(42)
        noise = rng.standard_normal((H, W)).astype(np.float32)
        noise = gaussian_filter(noise, sigma=self.pore_scale)
        noise = noise / (noise.std() + 1e-8) * self.pore_strength

        r_out = np.clip(r_sss + noise * 0.6, 0.0, 1.0)
        g_out = np.clip(g_sss + noise * 0.4, 0.0, 1.0)
        b_out = np.clip(b_sss + noise * 0.2, 0.0, 1.0)

        blend = op * mask
        buf[:, :, 2] = np.clip((r * (1 - blend) + r_out * blend) * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip((g * (1 - blend) + g_out * blend) * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip((b * (1 - blend) + b_out * blend) * 255, 0, 255).astype(np.uint8)
        self._put_buf(surface, buf)
        print("    Skin material pass complete (SSS + pore texture).")


# ─────────────────────────────────────────────────────────────────────────────
# FeatherPass — vane structure + barbule iridescence
# ─────────────────────────────────────────────────────────────────────────────

class FeatherPass(MaterialPass):
    """
    Feather surface material.

    1. Vane/barb structure: anisotropic blur — sharp across the vane, soft along
       it — giving the characteristic linear texture of feather filaments.
    2. Barbule iridescence: thin-film interference causes hue shifts at ridges.
       Approximated by a hue-rotation field scaled by luma gradient magnitude.
    """

    def __init__(self, params: Optional[MaterialParams] = None,
                 vane_sigma_along: float = 3.0,
                 vane_sigma_across: float = 0.5,
                 iridescence_strength: float = 0.06):
        super().__init__(params)
        self.vane_sigma_along = vane_sigma_along
        self.vane_sigma_across = vane_sigma_across
        self.iridescence_strength = iridescence_strength

    def apply(self, surface, **kwargs) -> None:
        buf = self._get_buf(surface)
        H, W = buf.shape[:2]
        mask = self._mask(H, W)
        op = float(self.params.opacity)

        b = buf[:, :, 0].astype(np.float32) / 255.0
        g = buf[:, :, 1].astype(np.float32) / 255.0
        r = buf[:, :, 2].astype(np.float32) / 255.0

        # Anisotropic blur approximation — [row_sigma, col_sigma]
        s_a, s_c = self.vane_sigma_along, self.vane_sigma_across
        r_along = gaussian_filter(r, sigma=[s_a, s_c])
        g_along = gaussian_filter(g, sigma=[s_a, s_c])
        b_along = gaussian_filter(b, sigma=[s_a, s_c])

        # Iridescence: hue shift proportional to luma gradient magnitude
        luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
        gy, gx = np.gradient(luma)
        grad_mag  = np.sqrt(gx ** 2 + gy ** 2)
        hue_shift = np.tanh(grad_mag * 8.0) * self.iridescence_strength

        r_irid = np.clip(r_along - hue_shift * 0.5, 0.0, 1.0)
        g_irid = np.clip(g_along + hue_shift * 0.3, 0.0, 1.0)
        b_irid = np.clip(b_along + hue_shift * 0.8, 0.0, 1.0)

        blend = op * mask
        buf[:, :, 2] = np.clip((r * (1 - blend) + r_irid * blend) * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip((g * (1 - blend) + g_irid * blend) * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip((b * (1 - blend) + b_irid * blend) * 255, 0, 255).astype(np.uint8)
        self._put_buf(surface, buf)
        print("    Feather material pass complete (vane structure + iridescence).")


# ─────────────────────────────────────────────────────────────────────────────
# FurPass — undercoat + topcoat striations + silhouette fringe
# ─────────────────────────────────────────────────────────────────────────────

class FurPass(MaterialPass):
    """
    Fur surface material.

    Three optical layers of mammalian fur:
    1. Undercoat: dense, fine, matte base — coarse anisotropic blur.
    2. Topcoat: longer guard-hair striations — band-pass detail along pelage dir.
    3. Fringe: back-lit rim light at silhouette edges via mask-edge gradient halo.
    """

    def __init__(self, params: Optional[MaterialParams] = None,
                 undercoat_sigma: float = 4.0,
                 topcoat_strength: float = 0.12,
                 fringe_strength: float = 0.18,
                 fringe_sigma: float = 3.0):
        super().__init__(params)
        self.undercoat_sigma = undercoat_sigma
        self.topcoat_strength = topcoat_strength
        self.fringe_strength = fringe_strength
        self.fringe_sigma = fringe_sigma

    def apply(self, surface, **kwargs) -> None:
        buf = self._get_buf(surface)
        H, W = buf.shape[:2]
        mask = self._mask(H, W)
        op = float(self.params.opacity)

        b = buf[:, :, 0].astype(np.float32) / 255.0
        g = buf[:, :, 1].astype(np.float32) / 255.0
        r = buf[:, :, 2].astype(np.float32) / 255.0

        # Undercoat: directional smooth
        r_under = gaussian_filter(r, self.undercoat_sigma)
        g_under = gaussian_filter(g, self.undercoat_sigma)
        b_under = gaussian_filter(b, self.undercoat_sigma * 0.8)

        # Topcoat: band-pass striations
        striation = (gaussian_filter(r, 0.8) - gaussian_filter(r, 3.0)) * self.topcoat_strength
        r_top = np.clip(r_under + striation,        0.0, 1.0)
        g_top = np.clip(g_under + striation * 0.6,  0.0, 1.0)
        b_top = np.clip(b_under + striation * 0.3,  0.0, 1.0)

        # Fringe: rim glow at mask silhouette edge
        mask_blurred = gaussian_filter(mask, sigma=self.fringe_sigma)
        fringe = np.clip(mask - mask_blurred, 0.0, 1.0) * self.fringe_strength

        r_out = np.clip(r_top + fringe * 0.9, 0.0, 1.0)
        g_out = np.clip(g_top + fringe * 0.8, 0.0, 1.0)
        b_out = np.clip(b_top + fringe * 0.6, 0.0, 1.0)

        blend = op * mask
        buf[:, :, 2] = np.clip((r * (1 - blend) + r_out * blend) * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip((g * (1 - blend) + g_out * blend) * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip((b * (1 - blend) + b_out * blend) * 255, 0, 255).astype(np.uint8)
        self._put_buf(surface, buf)
        print("    Fur material pass complete (undercoat + topcoat + fringe).")


# ─────────────────────────────────────────────────────────────────────────────
# ScalesPass — tessellated facets + specular glint + iridescence
# ─────────────────────────────────────────────────────────────────────────────

class ScalesPass(MaterialPass):
    """
    Scales / reptile surface material.

    1. Tessellation shadow: darker lower edge per scale — sine wave at scale_period.
    2. Specular glint: narrow bright band on the upper face of each scale.
    3. Iridescent overlay: structural color via hue-phase oscillation field.
    """

    def __init__(self, params: Optional[MaterialParams] = None,
                 scale_period: float = 12.0,
                 shadow_depth: float = 0.12,
                 specular_width: float = 0.08,
                 iridescence: float = 0.04):
        super().__init__(params)
        self.scale_period = scale_period
        self.shadow_depth = shadow_depth
        self.specular_width = specular_width
        self.iridescence = iridescence

    def apply(self, surface, **kwargs) -> None:
        buf = self._get_buf(surface)
        H, W = buf.shape[:2]
        mask = self._mask(H, W)
        op = float(self.params.opacity)

        b = buf[:, :, 0].astype(np.float32) / 255.0
        g = buf[:, :, 1].astype(np.float32) / 255.0
        r = buf[:, :, 2].astype(np.float32) / 255.0

        ys = np.arange(H, dtype=np.float32).reshape(-1, 1) * np.ones((1, W))
        xs = np.arange(W, dtype=np.float32).reshape(1, -1) * np.ones((H, 1))
        phase = (ys / self.scale_period + xs / self.scale_period * 0.5) * 2 * np.pi
        wave = np.sin(phase).astype(np.float32)

        shadow   = np.clip(-wave, 0.0, 1.0) * self.shadow_depth
        specular = np.clip(wave - (1.0 - self.specular_width * 2),
                           0.0, 1.0) * (1.0 / (self.specular_width + 1e-6))
        specular = np.clip(specular, 0.0, 1.0) * 0.25
        hue_mod  = np.sin(phase + np.pi / 2).astype(np.float32) * self.iridescence

        r_out = np.clip(r - shadow + specular + hue_mod * (-0.3), 0.0, 1.0)
        g_out = np.clip(g - shadow * 0.8 + specular + hue_mod * 0.5, 0.0, 1.0)
        b_out = np.clip(b - shadow * 0.6 + specular + hue_mod * 0.9, 0.0, 1.0)

        blend = op * mask
        buf[:, :, 2] = np.clip((r * (1 - blend) + r_out * blend) * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip((g * (1 - blend) + g_out * blend) * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip((b * (1 - blend) + b_out * blend) * 255, 0, 255).astype(np.uint8)
        self._put_buf(surface, buf)
        print("    Scales material pass complete (tessellation + specular + iridescence).")


# ─────────────────────────────────────────────────────────────────────────────
# FabricPass — weave microgeometry + directional sheen
# ─────────────────────────────────────────────────────────────────────────────

class FabricPass(MaterialPass):
    """
    Fabric surface material.

    1. Weave microgeometry: crossed sine grid at thread scale — grid pattern
       of woven cloth visible at close range.
    2. Thread shadow: narrow dark valley between adjacent threads.
    3. Directional sheen: highlight lobe aligned with the weave direction,
       characteristic of silk and satin.
    """

    def __init__(self, params: Optional[MaterialParams] = None,
                 thread_period: float = 4.0,
                 sheen_strength: float = 0.12,
                 weave_shadow: float = 0.06):
        super().__init__(params)
        self.thread_period = thread_period
        self.sheen_strength = sheen_strength
        self.weave_shadow = weave_shadow

    def apply(self, surface, **kwargs) -> None:
        buf = self._get_buf(surface)
        H, W = buf.shape[:2]
        mask = self._mask(H, W)
        op = float(self.params.opacity)

        b = buf[:, :, 0].astype(np.float32) / 255.0
        g = buf[:, :, 1].astype(np.float32) / 255.0
        r = buf[:, :, 2].astype(np.float32) / 255.0

        ys = np.arange(H, dtype=np.float32).reshape(-1, 1) * np.ones((1, W))
        xs = np.arange(W, dtype=np.float32).reshape(1, -1) * np.ones((H, 1))
        p = self.thread_period
        weave = (np.sin(ys / p * 2 * np.pi) + np.sin(xs / p * 2 * np.pi)) * 0.5

        shadow_field = np.clip(-weave, 0.0, 1.0).astype(np.float32) * self.weave_shadow
        sheen_field  = np.clip( weave, 0.0, 1.0).astype(np.float32) * self.sheen_strength

        r_out = np.clip(r - shadow_field + sheen_field * 0.85, 0.0, 1.0)
        g_out = np.clip(g - shadow_field + sheen_field * 0.90, 0.0, 1.0)
        b_out = np.clip(b - shadow_field + sheen_field * 1.00, 0.0, 1.0)

        blend = op * mask
        buf[:, :, 2] = np.clip((r * (1 - blend) + r_out * blend) * 255, 0, 255).astype(np.uint8)
        buf[:, :, 1] = np.clip((g * (1 - blend) + g_out * blend) * 255, 0, 255).astype(np.uint8)
        buf[:, :, 0] = np.clip((b * (1 - blend) + b_out * blend) * 255, 0, 255).astype(np.uint8)
        self._put_buf(surface, buf)
        print("    Fabric material pass complete (weave + sheen).")


# ─────────────────────────────────────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────────────────────────────────────

_MATERIAL_PASSES = {
    "skin":    SkinPass,
    "feather": FeatherPass,
    "fur":     FurPass,
    "scales":  ScalesPass,
    "fabric":  FabricPass,
}


def get_material_pass(name: str, params: Optional[MaterialParams] = None,
                      **kwargs) -> MaterialPass:
    """
    Instantiate a MaterialPass by name.

    Parameters
    ----------
    name   : 'skin' | 'feather' | 'fur' | 'scales' | 'fabric'
    params : shared MaterialParams
    kwargs : extra keyword arguments forwarded to the subclass __init__
    """
    if name not in _MATERIAL_PASSES:
        raise ValueError(
            f"Unknown material pass {name!r}. Available: {sorted(_MATERIAL_PASSES)}"
        )
    return _MATERIAL_PASSES[name](params=params, **kwargs)
