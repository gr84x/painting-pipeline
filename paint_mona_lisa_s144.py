"""
paint_mona_lisa_s144.py -- Session 144 portrait painting.

Warm-start from mona_lisa_s143.png (latest accumulated canvas),
then applies session 144 additions.

Session 144 additions:
  - guardi                              -- NEW (session 144)
                                           Francesco Guardi
                                           (1712–1793),
                                           Venetian Atmospheric Veduta.
                                           Last great vedutista of the
                                           Venetian Republic and one of
                                           the first proto-Impressionists
                                           in European painting.  Where
                                           Canaletto counted every brick,
                                           Guardi painted Venice as a
                                           shimmer of light on water —
                                           forms perpetually dissolving
                                           into the cool silver-grey
                                           lagoon atmosphere.

  SESSION 144 ARTISTIC IMPROVEMENT -- guardi_atmospheric_shimmer_pass:

                                           New pass encoding Guardi's
                                           defining technical quality as
                                           the TWENTY-SECOND distinct
                                           processing mode in the
                                           pipeline:
                                           COHERENT MULTI-OFFSET HF
                                           TREMBLING with cool
                                           atmospheric tint.

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
                                           s136 Moretto -- CIE L*a*b*
                                             perceptual colour sculpting
                                           s137 Parmigianino -- luma-
                                             chroma decoupled filtering
                                           s138 Giorgione -- luminance-
                                             zoned dual-temperature
                                             sculpting
                                           s139 Palma Vecchio --
                                             Gaussian-gated luminance-
                                             zone warm bloom
                                           s140 Cossa -- gem-zone
                                             chroma boost + USM clarity
                                           s141 Crivelli -- specular
                                             power-curve gold-leaf
                                             gilding
                                           s142 Filippino -- saturation-
                                             gated hue rotation
                                           s143 Magnasco -- spatial-
                                             scatter HF luminance
                                             revival

                                           This pass introduces the
                                           TWENTY-SECOND distinct mode:
                                           COHERENT MULTI-OFFSET HF
                                           TREMBLING with cool
                                           atmospheric tint.

                                           Algorithm:
                                           (1) Per-channel decompose:
                                               LF = Gaussian(ch, sigma)
                                               HF = ch - LF
                                           (2) Build trembled HF by
                                               averaging n_trembles
                                               shifted copies of HF at
                                               ±tremble_px offsets
                                               (deterministic seed 144)
                                           (3) Reconstruct trembled:
                                               clip(LF + trembled_HF)
                                           (4) Cool atmospheric tint
                                               in luminance zone
                                               [cool_lo, cool_hi]:
                                               smooth bump gate × blend
                                               toward cool_r/g/b
                                           (5) Saturation damping in
                                               same zone: lerp toward
                                               luminance grey
                                           (6) Composite at opacity

                                           Distinct from s143 Magnasco
                                           (extracts BRIGHT PEAKS only,
                                           scatters at random discrete
                                           offsets, dark-zone gated):
                                           Guardi processes the FULL
                                           bidirectional HF component
                                           through coherent averaging —
                                           no thresholding, no darkness
                                           gate, no warm tint; the
                                           result is uniform surface
                                           trembling, not selective
                                           highlight scattering.

                                           Distinct from s123 Rosa
                                           (smooth continuous vector
                                           field warps ENTIRE image):
                                           Guardi preserves the LF
                                           structure exactly and only
                                           redistributes HF detail.

Warm-start base: mona_lisa_s143.png
Applies: s143 accumulated base + s144 (Guardi atmospheric shimmer -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S143_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s143.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s143.png"),
    "C:/Source/painting-pipeline/mona_lisa_s143.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s135.png"),
    "C:/Source/painting-pipeline/mona_lisa_s135.png",
]

base_path = None
for c in S143_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S143_CANDIDATES)
    )

print(f"Loading warm-start base: {base_path}", flush=True)


# -- Utilities ----------------------------------------------------------------

def make_figure_mask() -> np.ndarray:
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
    print("=" * 68, flush=True)
    print("Session 144 warm-start from accumulated canvas", flush=True)
    print("Applying: Guardi atmospheric shimmer (144 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 144 (NEW): Guardi atmospheric shimmer pass -------------------
    # Twenty-second distinct mode: COHERENT MULTI-OFFSET HF TREMBLING.
    # Applied at gentle opacity (0.25) to preserve the Leonardo sfumato
    # accumulated across prior sessions.  The Guardi pass introduces three
    # complementary qualities to the Mona Lisa portrait:
    #
    # 1. Trembling surface: the fine-detail layer acquires a fractured,
    #    shimmering quality that gives the painted surface micro-scale
    #    vitality without disrupting the large-scale sfumato depth.
    #    This is especially perceptible in the landscape background where
    #    the rocky terrain and atmospheric haze benefit from Guardi's
    #    dissolving-form quality — the distant rocks appear to tremble
    #    slightly between solidity and atmosphere.
    #
    # 2. Cool atmospheric tint: the mid-luminance zones receive a very
    #    gentle push toward cool grey-silver.  For the Mona Lisa, this
    #    reinforces the cool sfumato atmosphere in the background distance
    #    while barely touching the warm flesh tones of the figure (which
    #    sit at the higher luminance end of the portrait and are partially
    #    outside the atmospheric zone's cool_hi ceiling of 0.72).
    #
    # 3. Saturation damping: slight reduction in mid-tonal saturation
    #    reinforces the atmospheric depth illusion in the landscape
    #    distance.
    #
    # Parameters chosen conservatively for the accumulated Leonardo canvas:
    # shimmer_sigma=2.0: slightly larger than default to work at canvas
    #   resolution without picking up JPEG/noise artifacts.
    # n_trembles=5: moderate; enough trembling character without over-
    #   softening the accumulated sfumato depth.
    # tremble_px=2: conservative; 2px offset preserves portrait legibility.
    # cool_lo=0.28, cool_hi=0.72: targets the mid-tonal atmosphere zone;
    #   the portrait's warm highlights (above 0.72) are left untouched.
    # cool_amount=0.045: very gentle — just enough to push background
    #   atmosphere toward the cool Venetian grey without visibly cooling
    #   the face.
    # sat_dampen=0.08: subtle — reduces distant atmospheric saturation
    #   without visibly affecting the foreground figure.
    print("Guardi atmospheric shimmer pass (session 144 -- NEW)...", flush=True)
    p.guardi_atmospheric_shimmer_pass(
        shimmer_sigma = 2.0,
        n_trembles    = 5,
        tremble_px    = 2,
        cool_r        = 0.72,
        cool_g        = 0.74,
        cool_b        = 0.78,
        cool_lo       = 0.28,
        cool_hi       = 0.72,
        cool_amount   = 0.045,
        sat_dampen    = 0.08,
        opacity       = 0.25,
    )

    # -- Carry-forward passes from session 143 --------------------------------

    # Magnasco nervous brilliance (from s143 -- carry forward)
    print("Magnasco nervous brilliance pass (session 143 carry-forward)...", flush=True)
    p.magnasco_nervous_brilliance_pass(
        hf_sigma      = 3.0,
        scatter_px    = 2,
        bright_thresh = 0.04,
        dark_gate_lo  = 0.08,
        dark_gate_hi  = 0.55,
        warm_tint     = 0.04,
        opacity       = 0.18,
    )

    # Focal vignette (from s142 -- carry forward)
    print("Focal vignette pass (session 142 carry-forward)...", flush=True)
    p.focal_vignette_pass(
        focal_x           = 0.50,
        focal_y           = 0.35,
        vignette_strength = 0.25,
        vignette_power    = 2.2,
        cool_shift        = 0.018,
        opacity           = 0.35,
    )

    # Glazing depth pass (from session 141 -- carry forward)
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.07,
        warm_g      = 0.025,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.14,
    )

    # Velatura: warm amber unifying glaze
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.04)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.48, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s144.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
