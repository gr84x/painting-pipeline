"""
paint_mona_lisa_s138.py -- Session 138 portrait painting.

Warm-start from mona_lisa_s135.png (latest accumulated canvas),
then applies session 138 additions.

Session 138 additions:
  - giorgione                           -- NEW (session 138)
                                           Giorgio da Castelfranco (Giorgione,
                                           c. 1477-1510), Italian (Venetian).
                                           The founding master of Venetian poetic
                                           tonalism — 'poesia' painting.  His
                                           compositions emanate warm amber-golden
                                           radiance from the compositional centre,
                                           cooling and desaturating toward the
                                           margins.  Pioneered the atmospheric
                                           tonal approach that Titian inherited
                                           and transformed.  Only ~6 definitive
                                           attributions survive.

  SESSION 138 ARTISTIC IMPROVEMENT -- warm_shadow_lift_pass:

                                           New pass applying a subtle WARM AMBER
                                           LIFT specifically in the deepest shadow
                                           zones (luminance < 0.18), modelling
                                           how Renaissance oil painters avoided
                                           pure dead black in shadows.  Even the
                                           deepest painted shadows contain warm
                                           reflected ambient light — umber ground
                                           visible through thin shadow glazes.
                                           Complements penumbra_cool_tint_pass
                                           (which cools midtones) to create the
                                           full three-zone warm/cool model:
                                           warm highlights, cool penumbra, warm-
                                           amber deep shadows.

  SESSION 138 MAIN PASS -- giorgione_focal_warmth_pass:

                                           New pass encoding Giorgione's defining
                                           optical quality via the SIXTEENTH
                                           distinct processing mode in the
                                           pipeline: ELLIPTICAL FOCAL WARMTH
                                           SCULPTING.

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

                                           This pass introduces the
                                           SIXTEENTH distinct mode:
                                           ELLIPTICAL FOCAL WARMTH
                                           SCULPTING.

                                           Algorithm:
                                           (1) Normalised elliptical
                                               distance d from focal
                                               centre (cx, cy) with
                                               axes (rx, ry)
                                           (2) Gaussian warmth kernel:
                                               W = warm_peak *
                                               exp(-d^2 / 2*sigma^2)
                                           (3) Warm tint in focal zone:
                                               R += warm_r * W
                                               G += warm_g * W
                                           (4) Peripheral desaturation:
                                               for d > sat_radius, reduce
                                               saturation proportionally
                                               to (d - sat_radius) *
                                               sat_fade
                                           (5) Composite at opacity

                                           Geometrically distinct from
                                           all 15 prior modes:
                                           - Not mode 3 (vertical
                                             gradient only)
                                           - Not mode 12 (luminance-
                                             driven, not position)
                                           Uses 2D ELLIPTICAL GAUSSIAN
                                           kernel driving BOTH warmth
                                           AND saturation from focal pt.

Warm-start base: mona_lisa_s135.png
Applies: s135 accumulated base + s138 (Giorgione focal warmth + warm
         shadow lift -- NEW)
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
    Apply session 138 passes on top of the session-135 accumulated canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 138 warm-start from mona_lisa_s135.png", flush=True)
    print("Applying: accumulated s135 base + Giorgione (138 -- NEW)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # ── Session 138 artistic improvement: warm shadow lift pass ───────────────
    # Lifts deepest shadow zones (lum < 0.18) with a subtle warm amber tint,
    # modelling how Renaissance oil painters avoided pure dead black in shadows.
    # Complements penumbra_cool_tint_pass (session 137 improvement) to create
    # the full three-zone warm/cool model of sfumato portraiture.
    print("Warm shadow lift pass (session 138 artistic improvement)...", flush=True)
    p.warm_shadow_lift_pass(
        shadow_thresh = 0.18,
        transition    = 0.08,
        warm_r        = 0.040,
        warm_g        = 0.018,
        opacity       = 0.30,
    )

    # ── Session 138 (NEW): Giorgione tonal poetry pass ───────────────────────
    # Sixteenth distinct processing mode: LUMINANCE-ZONED DUAL-TEMPERATURE
    # SCULPTING.  Three luminance zones: (1) midtone warm luminous lift;
    # (2) shadow warm amber transition; (3) silhouette cool edge accent.
    # Models Giorgione's poesia: warm glowing interior, cool mysterious edge.
    print("Giorgione tonal poetry pass (session 138 -- NEW)...", flush=True)
    p.giorgione_tonal_poetry_pass(
        midtone_low          = 0.28,
        midtone_high         = 0.68,
        luminous_lift        = 0.08,
        warm_shadow_strength = 0.04,
        cool_edge_strength   = 0.03,
        figure_mask          = make_figure_mask(),
        opacity              = 0.30,
    )

    # ── Session 138 additional artistic pass: focal warmth radiance ──────────
    # Elliptical Gaussian warmth field centred on face region — complementary
    # spatial approach reinforcing the tonal poetry pass's warm focal quality.
    print("Giorgione focal warmth pass (session 138 artistic improvement)...", flush=True)
    p.giorgione_focal_warmth_pass(
        cx          = 0.50,
        cy          = 0.38,
        rx          = 0.60,
        ry          = 0.55,
        warm_peak   = 1.0,
        warm_r      = 0.10,
        warm_g      = 0.05,
        sigma       = 0.38,
        sat_radius  = 0.55,
        sat_fade    = 0.18,
        opacity     = 0.22,
    )

    # ── Finishing passes ───────────────────────────────────────────────────────

    # Velatura: Giorgione unified his panels with warm amber-golden glaze —
    # the 'inner glow' that gives Venetian tonalist paintings their warmth.
    print("Velatura warm amber-golden glaze (Giorgione Venetian tonalism)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.68, 0.42), midtone_opacity=0.05)

    # Vignette
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.50, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s138.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
