"""
paint_mona_lisa_s134.py -- Session 134 portrait painting.

Warm-start from mona_lisa_s133.png (latest accumulated canvas),
then applies session 134 additions.

Session 134 additions:
  - aelbert_cuyp                        -- NEW (session 134)
                                           Aelbert Cuyp
                                           (1620–1691), Dutch
                                           (Dordrecht).  Supreme master
                                           of golden-hour atmospheric
                                           light — the "Dutch Claude"
                                           who brought Mediterranean
                                           warmth into Dutch pastoral
                                           landscape painting.  His
                                           amber-gold luminosity
                                           dissolves fine spatial detail
                                           in brilliantly lit zones,
                                           encoding a perceptual truth
                                           now measured as the luminance-
                                           dependent Contrast Sensitivity
                                           Function.

  SESSION 134 ARTISTIC IMPROVEMENT -- cuyp_golden_hour_pass:

                                           New pass encoding Cuyp's
                                           golden-hour light quality via
                                           the TWELFTH distinct
                                           processing mode in the
                                           pipeline:
                                           LUMINANCE-ADAPTIVE SPATIAL
                                           FREQUENCY ATTENUATION
                                           (Contrast Sensitivity Function
                                           simulation).

                                           Previous processing modes:
                                           s123 Rosa   — spatial
                                             displacement (turbulent
                                             flow warping)
                                           s124 Stanzione — frequency-
                                             band decomposition
                                             (Laplacian pyramid)
                                           s125 Albani — vertical
                                             spatial gradient
                                             (chromatic aerial
                                             perspective)
                                           s126 Bartolommeo — edge-
                                             map-driven modulation
                                             (Sobel form ridges)
                                           s127 Cantarini — spectral
                                             channel-selective diffusion
                                           s128 Carpaccio — local
                                             variance std map spatial
                                             adaptation
                                           s129 Piazzetta — global
                                             histogram percentile
                                             tonal sculpting
                                           s130 Sebastiano — image
                                             structure tensor
                                             coherence-driven
                                             form smoothing
                                           s131 Rosso — hue-selective
                                             chromatic tension mapping
                                           s132 Dosso — illumination-
                                             reflectance decomposition
                                             (Retinex)
                                           s133 Bassano — anisotropic
                                             diffusion (Perona-Malik)

                                           This pass introduces the
                                           TWELFTH distinct mode:
                                           LUMINANCE-ADAPTIVE SPATIAL
                                           FREQUENCY ATTENUATION.

                                           Perceptual model:
                                           The human Contrast Sensitivity
                                           Function (CSF) is modulated
                                           by background luminance.  At
                                           high background luminance,
                                           sensitivity to high spatial
                                           frequencies (fine texture,
                                           sharp edge detail) falls
                                           sharply — "luminance masking."
                                           In Cuyp's brightly lit zones,
                                           fine detail genuinely dissolves
                                           into the golden luminous field.

                                           Algorithm:
                                           (1) L = 0.299R + 0.587G +
                                               0.114B
                                           (2) GOLDEN WARMTH SHIFT:
                                               R += gold_warm_r × L²
                                               G += gold_warm_g × L²
                                               B -= gold_cool_b × L²
                                               (quadratic: only bright
                                               pixels get full shift)
                                           (3) SPATIALLY-VARYING BLUR:
                                               σ(x,y) = σ_base +
                                               σ_scale × L²
                                               Approximated by blending
                                               N pre-computed Gaussian
                                               levels proportionally
                                               to L²
                                           (4) COMPOSITE at opacity

                                           Unlike anisotropic diffusion
                                           (s133), which PRESERVES edges,
                                           this mode DELIBERATELY
                                           DISSOLVES fine detail
                                           proportionally to luminance —
                                           a fundamentally different
                                           physical model.

Warm-start base: mona_lisa_s133.png
Applies: s133 accumulated base + s134 (Cuyp CSF golden-hour -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# ── Locate warm-start base ─────────────────────────────────────────────────────
S133_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s133.png"),
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s133.png"
    ),
    "/c/Source/painting-pipeline/mona_lisa_s133.png",
    "C:/Source/painting-pipeline/mona_lisa_s133.png",
]

base_path = None
for c in S133_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s133.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S133_CANDIDATES)
    )

print(f"Loading session-133 base: {base_path}", flush=True)


# ── Utilities ──────────────────────────────────────────────────────────────────

def make_figure_mask() -> np.ndarray:
    """Elliptical figure mask for the Mona Lisa composition."""
    mask = np.zeros((H, W), dtype=np.float32)
    cx, cy = W * 0.50, H * 0.46
    rx, ry = W * 0.38, H * 0.46
    y_idx, x_idx = np.ogrid[:H, :W]
    ellipse = ((x_idx - cx) / rx) ** 2 + ((y_idx - cy) / ry) ** 2
    mask[ellipse <= 1.0] = 1.0
    from scipy.ndimage import gaussian_filter
    mask = gaussian_filter(mask, sigma=30)
    return np.clip(mask, 0.0, 1.0)


def load_png_into_painter(p: Painter, path: str) -> None:
    """Load a PNG file into the Painter's cairo surface."""
    img = Image.open(path).convert("RGBA").resize((W, H), Image.LANCZOS)
    import cairo
    import array as arr
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surface)
    img_data = img.tobytes("raw", "BGRA")
    src = cairo.ImageSurface.create_for_data(
        arr.array("B", img_data), cairo.FORMAT_ARGB32, W, H
    )
    ctx.set_source_surface(src, 0, 0)
    ctx.paint()
    p.canvas.surface.get_data()[:] = surface.get_data()[:]
    p.canvas.surface.mark_dirty()


def paint(out_dir: str = ".") -> str:
    """
    Apply session 134 passes on top of the session-133 accumulated canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 134 warm-start from mona_lisa_s133.png", flush=True)
    print("Applying: accumulated s133 base + Aelbert Cuyp (134 -- NEW)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # ── Session 134 (NEW): Aelbert Cuyp golden-hour CSF pass ──────────────────
    # Luminance-adaptive spatial frequency attenuation: bright pixels receive a
    # progressively stronger Gaussian blur (proportional to L²), dissolving fine
    # spatial detail in luminous zones into the golden atmosphere — a direct
    # simulation of the human CSF luminance-masking effect that Cuyp encoded
    # two centuries before it was formally measured.  The warm golden shift
    # (R += gold_warm_r × L², B -= gold_cool_b × L²) simultaneously infuses
    # bright zones with the amber-gold warmth of late-afternoon Dutch sunlight.
    # Twelfth distinct processing mode in the pipeline.
    print("Aelbert Cuyp golden-hour CSF pass (session 134 -- NEW)...", flush=True)
    p.cuyp_golden_hour_pass(
        gold_warm_r   = 0.16,
        gold_warm_g   = 0.07,
        gold_cool_b   = 0.09,
        sigma_base    = 0.8,
        sigma_scale   = 5.5,
        n_blur_levels = 4,
        opacity       = 0.32,
    )

    # ── Finishing passes ───────────────────────────────────────────────────────

    # Velatura: Cuyp unified his canvases with a thin amber-gold glaze that
    # deepened the warm luminosity and gave all tones the quality of being
    # seen through a golden afternoon atmosphere.
    print("Velatura warm amber-gold glaze (Cuyp afternoon unification)...", flush=True)
    p.velatura_pass(midtone_tint=(0.88, 0.72, 0.38), midtone_opacity=0.08)

    # Vignette and crackle
    print("Finishing (vignette + crackle)...", flush=True)
    p.finish(vignette=0.52, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s134.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
