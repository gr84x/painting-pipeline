"""
paint_mona_lisa_s135.py -- Session 135 portrait painting.

Warm-start from mona_lisa_s134.png (latest accumulated canvas),
then applies session 135 additions.

Session 135 additions:
  - lucas_cranach                       -- NEW (session 135)
                                           Lucas Cranach the Elder
                                           (1472-1553), German (Saxony).
                                           Court painter to the Saxon
                                           Electors and close friend of
                                           Martin Luther.  His panel
                                           surfaces exhibit enamel-like
                                           chromatic purity: each colour
                                           zone reads at maximum
                                           saturation for its luminance
                                           level, with no grey
                                           contamination from atmospheric
                                           blending.  Gothic linear
                                           clarity fused with Renaissance
                                           figuration.

  SESSION 135 ARTISTIC IMPROVEMENT -- highlight_crystalline_pass:

                                           New pass applying
                                           LUMINANCE-GATED UNSHARP
                                           MASKING to bright highlight
                                           zones only.  Inspired by
                                           Van Eyck's lead-white
                                           specular touches -- crystalline
                                           precision in the brightest
                                           surface accents, contrasted
                                           with the soft atmospheric
                                           treatment of shadows.

  SESSION 135 MAIN PASS -- cranach_enamel_clarity_pass:

                                           New pass encoding Cranach's
                                           enamel-flat colour purity via
                                           the THIRTEENTH distinct
                                           processing mode in the
                                           pipeline:
                                           CHROMATICITY/LUMINANCE
                                           DECOMPOSITION (mean-achromatic
                                           separation with chromatic
                                           boost and spatial chroma
                                           pooling).

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

                                           This pass introduces the
                                           THIRTEENTH distinct mode:
                                           CHROMATICITY/LUMINANCE
                                           DECOMPOSITION.

                                           Algorithm:
                                           (1) grey = (R+G+B)/3
                                           (2) cr = R-grey, cg = G-grey,
                                               cb = B-grey
                                               (cr+cg+cb = 0 identically)
                                           (3) Boost chroma:
                                               cr *= (1+chroma_boost)
                                           (4) Optional spatial pooling
                                               of chroma only
                                               (sigma_pool approx 1.8px)
                                           (5) Reconstruct:
                                               R_out = grey + cr_final
                                           (6) Composite at opacity

Warm-start base: mona_lisa_s134.png
Applies: s134 accumulated base + s135 (Cranach chromaticity + crystalline -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# ── Locate warm-start base ─────────────────────────────────────────────────────
S134_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s134.png"),
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s134.png"
    ),
    "/c/Source/painting-pipeline/mona_lisa_s134.png",
    "C:/Source/painting-pipeline/mona_lisa_s134.png",
]

base_path = None
for c in S134_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s134.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S134_CANDIDATES)
    )

print(f"Loading session-134 base: {base_path}", flush=True)


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
    Apply session 135 passes on top of the session-134 accumulated canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 135 warm-start from mona_lisa_s134.png", flush=True)
    print("Applying: accumulated s134 base + Lucas Cranach (135 -- NEW)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # ── Session 135 (NEW): Cranach enamel clarity pass ────────────────────────
    # Chromaticity/luminance decomposition: separates each pixel into its
    # achromatic grey component and chromatic deviation (R-grey, G-grey, B-grey,
    # where cr+cg+cb = 0 identically), boosts the chromatic deviation, and
    # applies mild spatial pooling to the chroma layer only -- grey structure
    # remains untouched.  Replicates Cranach's enamel-flat colour purity: each
    # pigment zone reaches maximum chroma without grey contamination.
    # Thirteenth distinct processing mode in the pipeline.
    print("Lucas Cranach enamel clarity pass (session 135 -- NEW)...", flush=True)
    p.cranach_enamel_clarity_pass(
        chroma_boost = 0.32,
        sigma_pool   = 2.0,
        pool_weight  = 0.28,
        opacity      = 0.30,
    )

    # ── Session 135 artistic improvement: highlight crystalline pass ──────────
    # Luminance-gated unsharp masking: applies USM sharpening only in the
    # bright highlight zone (luminance > lum_thresh), making specular accents
    # on skin, fabric sheen, and background elements read with crystalline
    # precision -- the complementary operation to the dissolving passes elsewhere.
    print("Highlight crystalline pass (session 135 artistic improvement)...", flush=True)
    p.highlight_crystalline_pass(
        lum_thresh  = 0.70,
        usm_sigma   = 1.4,
        usm_amount  = 0.50,
        transition  = 0.16,
        opacity     = 0.32,
    )

    # ── Finishing passes ───────────────────────────────────────────────────────

    # Velatura: Cranach unified his panels with a thin warm glaze that gave
    # his Saxon court portraits their characteristic golden warmth.
    print("Velatura warm amber glaze (Cranach Saxon panel unification)...", flush=True)
    p.velatura_pass(midtone_tint=(0.86, 0.70, 0.36), midtone_opacity=0.07)

    # Vignette and crackle
    print("Finishing (vignette + crackle)...", flush=True)
    p.finish(vignette=0.52, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s135.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
