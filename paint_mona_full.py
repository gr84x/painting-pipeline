"""
paint_mona_full.py — Full stroke-engine portrait using PIL-based scipy stub.

scipy.ndimage hangs on import in this environment (ndimage._filters DLL issue).
We pre-stub sys.modules['scipy.ndimage'] with PIL-backed implementations BEFORE
importing stroke_engine, so the full Painter pipeline becomes available.

This produces the enigmatic half-length Leonardesque portrait using the
session-25 leonardesque example script pipeline.
"""

import sys
import types
import numpy as np
from PIL import Image, ImageFilter


# ─────────────────────────────────────────────────────────────────────────────
# scipy.ndimage stub — PIL-backed replacements
# Must be installed in sys.modules BEFORE stroke_engine is imported
# ─────────────────────────────────────────────────────────────────────────────

def _pil_gaussian_filter(arr, sigma=1.0, **kwargs):
    """Drop-in for scipy.ndimage.gaussian_filter using PIL.GaussianBlur."""
    radius = float(sigma)
    arr = np.asarray(arr, dtype=np.float32)
    if arr.ndim == 2:
        img = Image.fromarray(
            np.clip(arr * 255, 0, 255).astype(np.uint8), 'L')
        blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
        return np.array(blurred).astype(np.float32) / 255.0
    elif arr.ndim == 3:
        result = np.zeros_like(arr)
        for c in range(arr.shape[2]):
            ch = np.clip(arr[:, :, c] * 255, 0, 255).astype(np.uint8)
            img = Image.fromarray(ch, 'L')
            blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
            result[:, :, c] = np.array(blurred).astype(np.float32) / 255.0
        return result
    return arr


def _pil_sobel(arr, axis=0, **kwargs):
    """Drop-in for scipy.ndimage.sobel — edge detection via PIL FIND_EDGES."""
    arr = np.asarray(arr, dtype=np.float32)
    if arr.ndim == 2:
        img = Image.fromarray(
            np.clip(arr * 255, 0, 255).astype(np.uint8), 'L')
        edges = img.filter(ImageFilter.FIND_EDGES)
        out = np.array(edges).astype(np.float32) / 255.0
        if axis == 0:
            return out * (0.5 if arr.mean() > 0 else 1.0)
        else:
            return out * 0.5
    return np.zeros_like(arr)


def _passthrough(arr, **kwargs):
    return np.asarray(arr, dtype=np.float32)


def _uniform_filter(arr, size=3, **kwargs):
    """Drop-in for scipy.ndimage.uniform_filter using PIL box blur."""
    arr = np.asarray(arr, dtype=np.float32)
    radius = size / 2.0
    if arr.ndim == 2:
        img = Image.fromarray(
            np.clip(arr * 255, 0, 255).astype(np.uint8), 'L')
        blurred = img.filter(ImageFilter.BoxBlur(int(radius)))
        return np.array(blurred).astype(np.float32) / 255.0
    elif arr.ndim == 3:
        result = np.zeros_like(arr)
        for c in range(arr.shape[2]):
            ch = np.clip(arr[:, :, c] * 255, 0, 255).astype(np.uint8)
            img = Image.fromarray(ch, 'L')
            blurred = img.filter(ImageFilter.BoxBlur(int(radius)))
            result[:, :, c] = np.array(blurred).astype(np.float32) / 255.0
        return result
    return arr


def _label(arr, **kwargs):
    """Minimal scipy.ndimage.label stub — return array + count."""
    # Simple thresholded labelling: mark non-zero regions with 1
    mask = (np.asarray(arr) != 0).astype(np.int32)
    return mask, int(mask.max())


def _generic_filter(arr, function, size=3, **kwargs):
    """Drop-in for generic_filter — just return identity."""
    return np.asarray(arr, dtype=np.float32)


def _sum_labels(arr, labels=None, index=None):
    return 0.0


# Build the stub module
_ndimage = types.ModuleType('scipy.ndimage')
_ndimage.gaussian_filter  = _pil_gaussian_filter
_ndimage.sobel            = _pil_sobel
_ndimage.uniform_filter   = _uniform_filter
_ndimage.label            = _label
_ndimage.generic_filter   = _generic_filter
_ndimage.sum_labels       = _sum_labels
_ndimage.binary_dilation  = lambda a, **kw: a.astype(bool)
_ndimage.binary_erosion   = lambda a, **kw: a.astype(bool)
_ndimage.distance_transform_edt = lambda a: np.zeros_like(a, dtype=float)
_ndimage.convolve         = lambda a, w, **kw: a

# The from-import forms (e.g. `from scipy.ndimage import gaussian_filter`) also
# check sys.modules, so installing the stub is sufficient.
sys.modules['scipy.ndimage'] = _ndimage

# Also stub scipy.ndimage._nd_image, ._filters, etc. to prevent any DLL load
for _submod in ('_nd_image', '_filters', '_interpolation', '_morphology',
                '_measurements', '_fourier'):
    sys.modules[f'scipy.ndimage.{_submod}'] = _ndimage


# ─────────────────────────────────────────────────────────────────────────────
# Now stroke_engine can be imported without hanging
# ─────────────────────────────────────────────────────────────────────────────

print("Loading stroke engine (scipy.ndimage stub active)…")
import os
sys.path.insert(0, os.path.dirname(__file__))

from stroke_engine import Painter
from examples.run_leonardesque_enigmatic import make_reference, _make_face_ellipse_mask, W, H
print("Stroke engine loaded.")


# ─────────────────────────────────────────────────────────────────────────────
# Full painting orchestration (mirrors run_leonardesque_enigmatic.paint())
# with the session-25 additions woven in
# ─────────────────────────────────────────────────────────────────────────────

def paint(out_path: str = "mona_full.png") -> str:
    print("Building synthetic reference…")
    ref = make_reference()
    W_r, H_r = ref.size

    p = Painter(W_r, H_r)

    # ── Phase 1: Ground and grisaille ────────────────────────────────────────
    print("\nPhase 1 — Ground and grisaille")
    p.tone_ground((0.54, 0.45, 0.26), texture_strength=0.055)
    print("  Underpainting pass 1…")
    p.underpainting(ref, stroke_size=56, n_strokes=240)
    print("  Underpainting pass 2…")
    p.underpainting(ref, stroke_size=32, n_strokes=360)
    p.canvas.dry(amount=0.85)

    # ── Phase 2: Colour block-in ──────────────────────────────────────────────
    print("\nPhase 2 — Colour block-in")
    p.block_in(ref, stroke_size=40, n_strokes=460)
    p.block_in(ref, stroke_size=24, n_strokes=620)
    p.canvas.dry(amount=0.60)
    p.focused_pass(
        ref,
        region_mask=np.ones((H_r, W_r), dtype=np.float32),
        stroke_size=12, n_strokes=400,
        opacity=0.72, wet_blend=0.22, jitter_amt=0.030, curvature=0.08,
    )

    # ── Phase 3: Form building ────────────────────────────────────────────────
    print("\nPhase 3 — Build form")
    p.canvas.dry(amount=0.65)
    p.build_form(ref, stroke_size=9, n_strokes=880)
    p.build_form(ref, stroke_size=5, n_strokes=620)
    p.canvas.dry(amount=0.85)

    # ── Phase 4: Atmospheric depth ────────────────────────────────────────────
    print("\nPhase 4 — Atmospheric depth")
    p.atmospheric_depth_pass(
        haze_color=(0.72, 0.77, 0.86),
        desaturation=0.68,
        lightening=0.52,
        depth_gamma=1.8,
        background_only=True,
    )

    # ── Phase 5: Session-25 new passes ───────────────────────────────────────
    print("\nPhase 5 — Session-25: Porcelain skin (Ingres)")
    p.porcelain_skin_pass(
        smooth_strength=0.55,
        highlight_cool=0.07,
        blush_opacity=0.10,
        highlight_thresh=0.74,
        blush_lo=0.40,
        blush_hi=0.68,
        smooth_sigma=2.0,
        figure_only=False,   # stub gaussian works globally
    )

    print("\nPhase 6 — Session-25: Tonal compression (academic value range)")
    p.tonal_compression_pass(
        shadow_lift=0.04,
        highlight_compress=0.96,
        midtone_contrast=0.06,
    )

    # ── Phase 7: Sfumato in three sessions ───────────────────────────────────
    print("\nPhase 7 — Sfumato (three sessions)")
    p.sfumato_veil_pass(ref, n_veils=3, blur_radius=12.0, warmth=0.30,
                        veil_opacity=0.040, edge_only=True, chroma_dampen=0.18)
    p.canvas.dry(amount=0.65)
    p.sfumato_veil_pass(ref, n_veils=3, blur_radius=7.5, warmth=0.26,
                        veil_opacity=0.038, edge_only=True, chroma_dampen=0.20)
    p.canvas.dry(amount=0.60)
    p.sfumato_veil_pass(ref, n_veils=2, blur_radius=4.5, warmth=0.22,
                        veil_opacity=0.035, edge_only=True, chroma_dampen=0.22)
    p.canvas.dry(amount=0.70)

    # ── Phase 8: Glazing ──────────────────────────────────────────────────────
    print("\nPhase 8 — Glazing")
    p.warm_cool_boundary_pass(strength=0.12, edge_thresh=0.07, blur_sigma=1.6)
    p.subsurface_glow_pass(ref, glow_color=(0.88, 0.40, 0.22),
                           glow_strength=0.14, blur_sigma=9.0, edge_falloff=0.60)
    p.glazed_panel_pass(ref, n_glaze_layers=7, glaze_opacity=0.055,
                        shadow_warmth=0.28, highlight_cool=0.12,
                        shadow_thresh=0.36, highlight_thresh=0.74, panel_bloom=0.06)
    p.canvas.dry(amount=0.60)

    # ── Phase 9: Lights, detail, finish ──────────────────────────────────────
    print("\nPhase 9 — Lights, detail, finish")
    p.place_lights(ref, stroke_size=5, n_strokes=560)
    p.glaze((0.62, 0.44, 0.14), opacity=0.050)
    face_mask = _make_face_ellipse_mask(H_r, W_r)
    p.focused_pass(ref, region_mask=face_mask, stroke_size=4, n_strokes=860,
                   opacity=0.80, wet_blend=0.06, jitter_amt=0.015, curvature=0.05)
    p.finish(vignette=0.48, crackle=True)

    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "mona_full.png"
    paint(out)
