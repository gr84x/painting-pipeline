"""
paint_mona_lisa_s145.py -- Session 145 portrait painting.

Warm-start from mona_lisa_s144.png (latest accumulated canvas),
then applies session 145 additions.

Session 145 additions:
  - cambiaso                            -- NEW (session 145)
                                           Luca Cambiaso
                                           (1527–1585),
                                           Genoese Mannerism /
                                           Ligurian Mannerism.
                                           The leading painter of
                                           Genoa in the sixteenth
                                           century and the first
                                           Western artist to
                                           systematically resolve
                                           the human figure into
                                           simplified geometric
                                           volumes — cubes,
                                           cylinders, and cones.
                                           His cubic figure drawings
                                           anticipate analytical
                                           Cubism by three centuries.
                                           In his finished paintings,
                                           broad flat tonal planes
                                           are separated by crisp
                                           boundaries; warm
                                           terracotta-ochre grounds
                                           glow through shadow zones.

  SESSION 145 ARTISTIC IMPROVEMENT -- cambiaso_geometric_planes_pass:

                                           New pass encoding Cambiaso's
                                           defining technical quality as
                                           the TWENTY-THIRD distinct
                                           processing mode in the
                                           pipeline:
                                           COARSE-ZONE TONAL FLATTENING
                                           WITH BOUNDARY CLARIFICATION.

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
                                           s144 Guardi -- coherent
                                             multi-offset HF trembling
                                             with cool atmospheric tint

                                           This pass introduces the
                                           TWENTY-THIRD distinct mode:
                                           COARSE-ZONE TONAL FLATTENING
                                           WITH BOUNDARY CLARIFICATION.

                                           Algorithm:
                                           (1) Per-channel two-scale
                                               Gaussian decomposition:
                                               coarse=Gaussian(ch,20)
                                               medium=Gaussian(ch,4)
                                           (2) Within-zone flattening:
                                               residual = ch - medium
                                               flat = medium + residual
                                                       * (1 - flatten)
                                           (3) Zone boundary detection:
                                               coarse_luma = weighted avg
                                               boundary = norm(|Sobel|)
                                           (4) Boundary clarification:
                                               usm = coarse - blur(coarse)
                                               enh = flat + boost*usm*bnd
                                           (5) Terracotta tint in
                                               shadow zone [0.12, 0.42]:
                                               smooth bump gate × blend
                                               toward ochre (0.68,0.45,0.18)
                                           (6) Composite at opacity

                                           Distinct from s144 Guardi
                                           (redistributes HF spatially):
                                           Cambiaso SUPPRESSES fine
                                           detail, moving pixels toward
                                           zone mean — planes flatten
                                           rather than tremble.

                                           Distinct from s126 Bartolommeo
                                           (fine-edge modulation):
                                           Cambiaso operates only at
                                           COARSE-ZONE boundaries, not
                                           fine-detail edges.

Warm-start base: mona_lisa_s144.png
Applies: s144 accumulated base + s145 (Cambiaso geometric planes -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S144_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s144.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s144.png"),
    "C:/Source/painting-pipeline/mona_lisa_s144.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s143.png"),
    "C:/Source/painting-pipeline/mona_lisa_s143.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s135.png"),
    "C:/Source/painting-pipeline/mona_lisa_s135.png",
]

base_path = None
for c in S144_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S144_CANDIDATES)
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
    print("Session 145 warm-start from accumulated canvas", flush=True)
    print("Applying: Cambiaso geometric planes (145 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 145 (NEW): Cambiaso geometric planes pass --------------------
    # Twenty-third distinct mode: COARSE-ZONE TONAL FLATTENING.
    # Applied at moderate opacity (0.28) to preserve the accumulated Leonardo
    # sfumato without over-flattening the deep tonal gradations of the portrait.
    #
    # The Cambiaso pass contributes three complementary qualities to the canvas:
    #
    # 1. Planar coherence: broad tonal zones within the face, landscape, and
    #    drapery read more clearly as distinct geometric planes.  The sigma_coarse
    #    of 22.0 (slightly enlarged for the 780×1080 canvas) ensures the zones
    #    are genuinely broad — forehead, cheek, jaw, and neck each resolve into
    #    their own coherent luminance plane rather than a continuous gradient.
    #    flatten_amount=0.50 is conservative: we suppress half the within-zone
    #    variation, leaving the sfumato depth intact while clarifying the planes.
    #
    # 2. Boundary clarification: at the transitions between planes (forehead-to-
    #    cheek, light-side-to-shadow-side, figure-to-landscape edge), the Sobel-
    #    gated USM signal provides a gentle sharpening that reinforces the sense
    #    of geometric form without introducing hard outlines incompatible with
    #    Leonardo's sfumato.  edge_boost=0.22 is gentle.
    #
    # 3. Terracotta shadow warmth: in the dark zones of the portrait — the deep
    #    sfumato shadow under the jaw, the deep shadow of the landscape distance,
    #    the dark drapery — the ochre terracotta tint glows through, providing
    #    a warm ambient that subtly distinguishes this canvas from the cool
    #    atmospheric Guardi treatment of s144.  The net effect is a delicate
    #    interplay: Guardi's cool atmospheric shimmer in the mid-tones, Cambiaso's
    #    warm terracotta in the deeper shadows.
    #
    # Parameters chosen for the accumulated Leonardo canvas:
    # sigma_coarse=22.0: slightly larger than default to work at full canvas
    #   resolution; ensures zones span entire face regions.
    # sigma_medium=5.0: larger medium sigma for the high-res canvas.
    # flatten_amount=0.50: conservative; preserves sfumato depth.
    # edge_boost=0.22: gentle; compatible with sfumato's blurred edges.
    # terra_lo=0.08, terra_hi=0.38: targets the deep shadow zone of the
    #   portrait; the sfumato mid-tones (above 0.38) are left untouched.
    # terra_amount=0.055: very gentle tint — ochre warmth in shadows only.
    # opacity=0.28: moderate; respects the accumulated surface.
    print("Cambiaso geometric planes pass (session 145 -- NEW)...", flush=True)
    p.cambiaso_geometric_planes_pass(
        sigma_coarse   = 22.0,
        sigma_medium   = 5.0,
        flatten_amount = 0.50,
        edge_boost     = 0.22,
        sigma_edge     = 2.0,
        terra_r        = 0.68,
        terra_g        = 0.45,
        terra_b        = 0.18,
        terra_lo       = 0.08,
        terra_hi       = 0.38,
        terra_amount   = 0.055,
        opacity        = 0.28,
    )

    # -- Carry-forward passes from session 144 --------------------------------

    # Guardi atmospheric shimmer (from s144 -- carry forward)
    print("Guardi atmospheric shimmer pass (session 144 carry-forward)...", flush=True)
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
        opacity       = 0.20,
    )

    # Magnasco nervous brilliance (from s143 -- carry forward)
    print("Magnasco nervous brilliance pass (session 143 carry-forward)...", flush=True)
    p.magnasco_nervous_brilliance_pass(
        hf_sigma      = 3.0,
        scatter_px    = 2,
        bright_thresh = 0.04,
        dark_gate_lo  = 0.08,
        dark_gate_hi  = 0.55,
        warm_tint     = 0.04,
        opacity       = 0.15,
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

    out_path = os.path.join(out_dir, "mona_lisa_s145.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
