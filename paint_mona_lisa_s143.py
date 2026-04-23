"""
paint_mona_lisa_s143.py -- Session 143 portrait painting.

Warm-start from mona_lisa_s142.png (latest accumulated canvas),
then applies session 143 additions.

Session 143 additions:
  - magnasco                            -- NEW (session 143)
                                           Alessandro Magnasco
                                           (il Lissandrino, 1667-1749),
                                           Genoese Dark Baroque.
                                           Master of nervous flickering
                                           highlights on near-black grounds.
                                           Figures and landscapes emerge
                                           from near-total darkness via
                                           rapid impasto touches applied
                                           with fierce gestural energy —
                                           proto-Expressionist urgency
                                           two centuries before its time.

  SESSION 143 ARTISTIC IMPROVEMENT -- magnasco_nervous_brilliance_pass:

                                           New pass encoding Magnasco's
                                           defining technical quality as
                                           the TWENTY-FIRST distinct
                                           processing mode in the pipeline:
                                           SPATIAL-SCATTER HIGH-FREQUENCY
                                           LUMINANCE REVIVAL.

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

                                           This pass introduces the
                                           TWENTY-FIRST distinct mode:
                                           SPATIAL-SCATTER HIGH-FREQUENCY
                                           LUMINANCE REVIVAL.

                                           Algorithm:
                                           (1) Extract positive HF per
                                               channel:
                                               HF = clip(ch -
                                               Gaussian(ch, hf_sigma)
                                               - bright_thresh, 0, inf)
                                           (2) Compute n_copies=4
                                               randomly shifted versions
                                               of HF using np.roll at
                                               ±scatter_px pixel offsets
                                               (deterministic seed 143)
                                           (3) Average shifted copies
                                               → scattered highlight
                                               layer
                                           (4) Dark-zone gate:
                                               1 - clip((luma -
                                               dark_gate_lo) /
                                               (dark_gate_hi -
                                               dark_gate_lo), 0, 1)
                                           (5) Warm-tint R channel:
                                               R *= (1 + warm_tint)
                                           (6) Add scattered HF to
                                               original, composite at
                                               opacity * dark_gate

                                           Distinct from s123 Rosa
                                           (turbulent flow warps the
                                           ENTIRE image via a smooth
                                           continuous vector field)
                                           because this mode extracts
                                           only BRIGHT PEAKS from the
                                           HF component and scatters
                                           those isolated marks by
                                           discrete random pixel
                                           offsets — the base image
                                           structure is not warped.
                                           Distinct from s128 Carpaccio
                                           (local variance std-map
                                           continuously adapts stroke
                                           behaviour via a smooth
                                           spatial field) because this
                                           is a discrete-offset point
                                           scatter on thresholded
                                           luminance peaks.

Warm-start base: mona_lisa_s142.png
Applies: s142 accumulated base + s143 (Magnasco nervous brilliance -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S142_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s142.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s142.png"),
    "C:/Source/painting-pipeline/mona_lisa_s142.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s135.png"),
    "C:/Source/painting-pipeline/mona_lisa_s135.png",
]

base_path = None
for c in S142_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S142_CANDIDATES)
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
    print("Session 143 warm-start from accumulated canvas", flush=True)
    print("Applying: Magnasco nervous brilliance (143 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 143 (NEW): Magnasco nervous brilliance pass ------------------
    # Twenty-first distinct mode: SPATIAL-SCATTER HIGH-FREQUENCY LUMINANCE REVIVAL.
    # Applied at gentle opacity (0.28) -- the Mona Lisa already has excellent
    # sfumato depth from the accumulated sessions; Magnasco's scattered highlight
    # technique adds a very subtle surface vivacity in the mid-dark zones:
    # the landscape darkness and the deep shadow areas of the figure receive
    # faint warm amber flickers that are too subtle to disrupt the Leonardo
    # sfumato but add micro-scale surface energy, as if the paint surface has
    # a slight internal luminosity in its darker regions.
    # hf_sigma=3.0: slightly larger than default to match the larger canvas
    # resolution; extracts surface-level detail rather than micro-texture noise.
    # scatter_px=2: conservative scatter for a portrait -- preserves the
    # compositional serenity while adding the nervous quality at a micro-scale.
    # dark_gate_hi=0.55: only the darker half of the tonal range receives the
    # effect; the sfumato mid-tones and highlights are left untouched.
    # warm_tint=0.04: very gentle amber warming -- enough to create the
    # candlelight quality without disturbing the cool sfumato atmosphere.
    print("Magnasco nervous brilliance pass (session 143 -- NEW)...", flush=True)
    p.magnasco_nervous_brilliance_pass(
        hf_sigma      = 3.0,
        scatter_px    = 2,
        bright_thresh = 0.04,
        dark_gate_lo  = 0.08,
        dark_gate_hi  = 0.55,
        warm_tint     = 0.04,
        opacity       = 0.28,
    )

    # -- Carry-forward passes from session 142 --------------------------------

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

    out_path = os.path.join(out_dir, "mona_lisa_s143.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
