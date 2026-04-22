"""
paint_mona_lisa_s136.py -- Session 136 portrait painting.

Warm-start from mona_lisa_s135.png (latest accumulated canvas),
then applies session 136 additions.

Session 136 additions:
  - parmigianino                        -- NEW (session 136)
                                           Francesco Mazzola (Parmigianino,
                                           1503–1540), Italian (Parma).
                                           The supreme Mannerist master of
                                           porcelain-perfect skin.  His
                                           flesh surfaces read as polished
                                           pearl — ultra-smooth, with no
                                           visible brushwork — built from
                                           successive glazes that cool
                                           toward silver in the half-tones.
                                           Extreme figure elongation
                                           (Madonna with the Long Neck)
                                           embodies refined Mannerist grace.

  SESSION 136 ARTISTIC IMPROVEMENT -- penumbra_cool_tint_pass:

                                           New pass applying a cool
                                           BLUE-LAVENDER TINT specifically
                                           in the penumbra / midtone zone
                                           (luminance ~0.15–0.52), leaving
                                           deep shadows and bright highlights
                                           untouched.  Encodes the warm/cool
                                           split exploited by Parmigianino
                                           and Leonardo: warm-lit highlights
                                           + cool scattered-skylight half-
                                           tones give skin simultaneous
                                           warmth and translucent depth.

  SESSION 136 MAIN PASS -- parmigianino_pearl_refinement_pass:

                                           New pass encoding Parmigianino's
                                           mercury-cool pearl skin via the
                                           FOURTEENTH distinct processing
                                           mode in the pipeline:
                                           LUMINANCE-CHROMINANCE DECOUPLED
                                           FILTERING (perceptual luma/chroma
                                           split with independent Gaussian
                                           chroma smoothing and luma USM,
                                           plus optional cool-pearl tint).

                                           Previous processing modes:
                                           s123 Rosa   -- spatial
                                             displacement (turbulent
                                             flow warping)
                                           s124 Stanzione -- frequency-
                                             band decomposition
                                             (Laplacian pyramid)
                                           s125 Albani -- vertical
                                             spatial gradient
                                             (chromatic aerial
                                             perspective)
                                           s126 Bartolommeo -- edge-
                                             map-driven modulation
                                             (Sobel form ridges)
                                           s127 Cantarini -- spectral
                                             channel-selective diffusion
                                           s128 Carpaccio -- local
                                             variance std map spatial
                                             adaptation
                                           s129 Piazzetta -- global
                                             histogram percentile
                                             tonal sculpting
                                           s130 Sebastiano -- image
                                             structure tensor
                                             coherence-driven
                                             form smoothing
                                           s131 Rosso -- hue-selective
                                             chromatic tension mapping
                                             (HSV space)
                                           s132 Dosso -- illumination-
                                             reflectance decomposition
                                             (Retinex/log domain)
                                           s133 Bassano -- anisotropic
                                             diffusion (Perona-Malik)
                                           s134 Cuyp -- luminance-
                                             adaptive spatial frequency
                                             attenuation (CSF)
                                           s135 Cranach -- chromaticity/
                                             luminance decomposition
                                             (mean-grey axis)

                                           This pass introduces the
                                           FOURTEENTH distinct mode:
                                           LUMINANCE-CHROMINANCE
                                           DECOUPLED FILTERING.

                                           Algorithm:
                                           (1) Luma = 0.299R + 0.587G
                                               + 0.114B  (perceptual,
                                               unlike Cranach's mean-grey)
                                           (2) Chroma residuals:
                                               Cr = R-Luma, Cg = G-Luma,
                                               Cb = B-Luma
                                           (3) Gaussian-smooth each chroma
                                               channel (sigma_chroma)
                                               → smooth colour zones
                                           (4) USM on Luma
                                               (sigma_luma, usm_amount)
                                               → crisp tonal structure
                                           (5) Optional cool tint:
                                               Cb += cool_tint
                                           (6) Reconstruct + composite

Warm-start base: mona_lisa_s135.png
Applies: s135 accumulated base + s136 (Parmigianino luma-chroma + penumbra -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# ── Locate warm-start base ─────────────────────────────────────────────────────
S135_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s135.png"),
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s135.png"
    ),
    "/c/Source/painting-pipeline/mona_lisa_s135.png",
    "C:/Source/painting-pipeline/mona_lisa_s135.png",
]

base_path = None
for c in S135_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s135.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S135_CANDIDATES)
    )

print(f"Loading session-135 base: {base_path}", flush=True)


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
    Apply session 136 passes on top of the session-135 accumulated canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 136 warm-start from mona_lisa_s135.png", flush=True)
    print("Applying: accumulated s135 base + Parmigianino (136 -- NEW)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # ── Session 136 artistic improvement: penumbra cool tint pass ─────────────
    # Zone-targeted cool tint in the penumbra/midtone band (lum 0.15–0.52).
    # Deep shadows and bright highlights are unaffected; only the transitional
    # half-tone penumbra receives a blue-lavender shift — encoding the warm/cool
    # split characteristic of sfumato portraiture: warm-lit highlight zones,
    # cool ambient-scattered penumbra, deep warm umber shadows.
    print("Penumbra cool tint pass (session 136 artistic improvement)...", flush=True)
    p.penumbra_cool_tint_pass(
        shadow_lo  = 0.15,
        shadow_hi  = 0.52,
        transition = 0.10,
        blue_lift  = 0.055,
        red_drop   = 0.018,
        opacity    = 0.28,
    )

    # ── Session 136 (NEW): Parmigianino pearl refinement pass ─────────────────
    # Luminance-chrominance decoupled filtering: decomposes each pixel into
    # perceptual luma (0.299R+0.587G+0.114B) and chroma residuals (R-L, G-L,
    # B-L), applies DIFFERENT filters to each channel — Gaussian smoothing to
    # chroma (smooth colour pools), USM to luma (precise tonal structure) —
    # then adds a subtle cool-pearl tint to the blue chroma residual.
    # Fourteenth distinct processing mode in the pipeline.
    print("Parmigianino pearl refinement pass (session 136 -- NEW)...", flush=True)
    p.parmigianino_pearl_refinement_pass(
        sigma_chroma = 2.2,
        sigma_luma   = 0.9,
        usm_amount   = 0.42,
        cool_tint    = 0.022,
        opacity      = 0.32,
    )

    # ── Finishing passes ───────────────────────────────────────────────────────

    # Velatura: Parmigianino unified his Parma panels with a warm amber-ivory
    # glaze that gave his portraits their characteristic pearl luminosity.
    print("Velatura warm amber-ivory glaze (Parmigianino Parma panel)...", flush=True)
    p.velatura_pass(midtone_tint=(0.82, 0.72, 0.50), midtone_opacity=0.06)

    # Vignette and crackle
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.50, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s136.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
