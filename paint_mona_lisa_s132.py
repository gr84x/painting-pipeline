"""
paint_mona_lisa_s132.py -- Session 132 portrait painting.

Warm-start from mona_lisa_s131.png (latest accumulated canvas),
then applies session 132 addition.

Session 132 additions:
  - dosso_dossi                         -- NEW (session 132)
                                           Dosso Dossi
                                           (Giovanni di Niccolò de Lutteri,
                                           c. 1490–1542), Italian (Ferrarese).
                                           Court painter of Ferrara under
                                           Alfonso I d'Este.  Absorbed the
                                           Giorgionesque sfumato and chromatic
                                           vision of Venetian colorism, fused
                                           with Ferrarese jewel-like intensity
                                           and poetic mythological imagination.
                                           Palette has a distinctive inner
                                           luminosity — warm amber-gold light
                                           seems to emanate from the ground
                                           itself.  Circe (c.1514) and Melissa
                                           (c.1520) are defining works.

  SESSION 132 ARTISTIC IMPROVEMENT -- dosso_luminance_reflectance_pass:

                                           New pass encoding Dosso's inner
                                           luminosity via the tenth distinct
                                           processing mode in the pipeline:
                                           ILLUMINATION-REFLECTANCE
                                           DECOMPOSITION (Retinex-inspired).

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

                                           This pass introduces the tenth
                                           distinct processing mode:
                                           ILLUMINATION-REFLECTANCE
                                           DECOMPOSITION.

                                           Physical model: L = I × R
                                             (illumination × reflectance)
                                           In log space:
                                             log(L) = log(I) + log(R)

                                           (1) ILLUMINATION ESTIMATION:
                                             I = Gaussian_blur(log(L))
                                             Sigma ≈ 60px — captures
                                             large-scale light distribution
                                             while leaving local color
                                             in reflectance.
                                           (2) REFLECTANCE EXTRACTION:
                                             R = L / (I + ε)
                                             Intrinsic local color,
                                             freed from global light.
                                           (3) REFLECTANCE SAT BOOST:
                                             Boost saturation in R by
                                             sat_boost — produces Dosso's
                                             jewel-like local color
                                             intensity without altering
                                             the overall tonal key.
                                           (4) ILLUMINATION WARMTH TINT:
                                             Shift I toward amber (+R, +G)
                                             — the pervasive Ferrarese
                                             golden ground warmth that
                                             unifies the canvas.
                                           (5) RECONSTRUCTION:
                                             result = I_warm × R_boosted
                                             Composite at opacity.

Warm-start base: mona_lisa_s131.png
Applies: s131 accumulated base + s132 (Dosso illumination-reflectance -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# ── Locate warm-start base ─────────────────────────────────────────────────────
S131_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s131.png"),
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s131.png"
    ),
    "/c/Source/painting-pipeline/mona_lisa_s131.png",
    "C:/Source/painting-pipeline/mona_lisa_s131.png",
]

base_path = None
for c in S131_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s131.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S131_CANDIDATES)
    )

print(f"Loading session-131 base: {base_path}", flush=True)


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
    # Notify cairo that surface was modified directly.
    # Without mark_dirty(), subsequent cairo context operations may read stale data.
    p.canvas.surface.mark_dirty()


def paint(out_dir: str = ".") -> str:
    """
    Apply session 132 pass on top of the session-131 accumulated canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 132 warm-start from mona_lisa_s131.png", flush=True)
    print("Applying: accumulated s131 base + Dosso Dossi (132 -- NEW)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # ── Session 132 (NEW): Dosso Dossi illumination-reflectance pass ──────────
    # Illumination-reflectance decomposition (Retinex): separate the image into
    # its large-scale illumination envelope (Gaussian blur in log space) and
    # intrinsic local reflectance.  Boost reflectance saturation for jewel-like
    # color intensity; tint illumination with warm amber for the Ferrarese golden
    # ground.  Tenth distinct processing mode in the pipeline.
    print("Dosso Dossi illumination-reflectance pass (session 132 -- NEW)...", flush=True)
    p.dosso_luminance_reflectance_pass(
        sigma_illum   = 60.0,
        sat_boost     = 0.22,
        illum_warm_r  = 0.06,
        illum_warm_g  = 0.02,
        opacity       = 0.34,
    )

    # ── Finishing passes ───────────────────────────────────────────────────────

    # Velatura: a thin semi-transparent warm glaze — Dosso often unified his
    # panels with a warm amber veil that deepened the jewel quality.
    print("Velatura warm glaze (Dosso Dossi unifying amber veil)...", flush=True)
    p.velatura_pass(opacity=0.10)

    # Vignette and crackle
    print("Finishing (vignette + crackle)...", flush=True)
    p.finish(vignette=0.52, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s132.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
