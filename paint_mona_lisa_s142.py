"""
paint_mona_lisa_s142.py -- Session 142 portrait painting.

Warm-start from mona_lisa_s138.png (latest accumulated canvas),
then applies session 142 additions.

Session 142 additions:
  - filippino_lippi                     -- NEW (session 142)
                                           Filippino Lippi (c. 1457-1504),
                                           Florentine, Late Quattrocento.
                                           Son of Fra Filippo Lippi, pupil
                                           of Botticelli.  Uses COLOR AS
                                           TENSION: adjacent chromatic zones
                                           push against each other with a
                                           restless energy anticipating
                                           Mannerism.

  SESSION 142 ARTISTIC IMPROVEMENT -- focal_vignette_pass:

                                           New pass applying a radial
                                           darkening and subtle cool-edge
                                           shift outward from the focal
                                           centre (focal_x, focal_y).
                                           Concentrates viewer attention on
                                           the central subject -- the face
                                           and hands -- by reducing luminance
                                           toward the composition edges and
                                           adding a faint cool atmospheric
                                           blue shift at the periphery.
                                           Applicable across all period
                                           styles; particularly effective
                                           for Renaissance portraits.

  SESSION 142 MAIN PASS -- filippino_tension_pass:

                                           New pass encoding Filippino
                                           Lippi's defining chromatic
                                           quality as the TWENTIETH distinct
                                           processing mode in the pipeline:
                                           SATURATION-GATED HUE ROTATION.

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

                                           This pass introduces the
                                           TWENTIETH distinct mode:
                                           SATURATION-GATED HUE ROTATION.

                                           Algorithm:
                                           (1) Convert RGB to HSV
                                           (2) gate = clip(
                                               (S - sat_thresh) /
                                               (1 - sat_thresh), 0, 1
                                               ) ^ sat_power
                                           (3) H' = (H + hue_shift *
                                               gate) % 1.0
                                           (4) S' = clip(S * (1 +
                                               sat_boost * gate), 0, 1)
                                           (5) Convert back to RGB
                                           (6) Composite at opacity

                                           Distinct from s131 (Rosso
                                           Fiorentino) which rotates
                                           hue ONLY in specific hue
                                           angle ranges (flesh, shadow,
                                           highlight zones by luminance),
                                           because this mode applies a
                                           UNIVERSAL rotation scaled
                                           by saturation level: the
                                           more chromatic a pixel, the
                                           more its hue is pushed.

Warm-start base: mona_lisa_s138.png
Applies: s138 accumulated base + s142 (Filippino tension + focal vignette -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S138_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s138.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s138.png"),
    "C:/Source/painting-pipeline/mona_lisa_s138.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s135.png"),
    "C:/Source/painting-pipeline/mona_lisa_s135.png",
]

base_path = None
for c in S138_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S138_CANDIDATES)
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
    print("Session 142 warm-start from accumulated canvas", flush=True)
    print("Applying: Filippino tension + focal vignette (142 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 142 artistic improvement: focal vignette pass ----------------
    # Radial darkening and cool edge shift from the face outward.
    # Focal point slightly above centre to concentrate on the face/upper figure.
    # cool_shift=0.025 adds a faint atmospheric blue recession at edges --
    # matching the sfumato aerial perspective of the background landscape.
    print("Focal vignette pass (session 142 artistic improvement)...", flush=True)
    p.focal_vignette_pass(
        focal_x           = 0.50,
        focal_y           = 0.35,
        vignette_strength = 0.30,
        vignette_power    = 2.2,
        cool_shift        = 0.025,
        opacity           = 0.45,
    )

    # -- Session 142 (NEW): Filippino tension pass ----------------------------
    # Twentieth distinct mode: SATURATION-GATED HUE ROTATION.
    # Gentle push on the most chromatic zones -- the landscape greens and
    # the drapery accents -- creating subtle colour argument between adjacent
    # zones without disturbing the overall Leonardo sfumato harmony.
    # sat_thresh=0.22 leaves the desaturated skin tones and hazy background
    # untouched; only the vivid mid-saturation landscape and drapery zones
    # receive the hue rotation.  hue_shift=0.03 is subtle (10.8 degrees) --
    # enough to push greens slightly more yellow-green, drapery slightly
    # more complex, without jarring the sfumato atmosphere.
    print("Filippino tension pass (session 142 -- NEW)...", flush=True)
    p.filippino_tension_pass(
        sat_thresh = 0.22,
        sat_power  = 1.8,
        hue_shift  = 0.030,
        sat_boost  = 0.14,
        opacity    = 0.22,
    )

    # -- Finishing passes -----------------------------------------------------

    # Glazing depth pass (from session 141 -- carry forward) --
    # Warm mid-tone glazing echo for oil transparency depth.
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.08,
        warm_g      = 0.03,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.18,
    )

    # Velatura: warm amber unifying glaze -- Leonardo's amber imprimatura note
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.04)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.48, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s142.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
