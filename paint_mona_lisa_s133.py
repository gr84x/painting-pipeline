"""
paint_mona_lisa_s133.py -- Session 133 portrait painting.

Warm-start from mona_lisa_s132.png (latest accumulated canvas),
then applies session 133 additions.

Session 133 additions:
  - jacopo_bassano                      -- NEW (session 133)
                                           Jacopo Bassano
                                           (Jacopo da Ponte,
                                           c. 1510–1592), Italian
                                           (Venetian, Bassano del
                                           Grappa).  Master of rustic
                                           pastoral subjects, dramatic
                                           artificial light, and
                                           vigorous impasto handling.
                                           Built compositions from a
                                           deep warm umber ground with
                                           warm copper-amber firelight
                                           erupting from darkness.
                                           El Greco likely trained in
                                           his workshop.

  SESSION 133 ARTISTIC IMPROVEMENT -- bassano_pastoral_glow_pass:

                                           New pass encoding Bassano's
                                           firelight quality via the
                                           eleventh distinct processing
                                           mode in the pipeline:
                                           ANISOTROPIC DIFFUSION
                                           (Perona-Malik filter).

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

                                           This pass introduces the
                                           eleventh distinct mode:
                                           ANISOTROPIC DIFFUSION.

                                           Physical model: PDE
                                           ∂I/∂t = div(c(|∇I|)·∇I)
                                           c(s) = exp(-(s/K)²)

                                           Low gradient → c ≈ 1.0
                                             → diffuses freely
                                             → creates smooth tonal
                                               pools in flat areas
                                           High gradient → c ≈ 0.0
                                             → diffusion halted
                                             → edges preserved exactly

                                           Result: smooth luminous
                                           light zones, firm
                                           chiaroscuro edges.
                                           Then: FIRELIGHT WARMTH
                                           BOOST on bright pixels —
                                           warm copper-amber tint
                                           proportional to luminance,
                                           simulating torch/candlelight.

  SESSION 133 ARTISTIC IMPROVEMENT #2 -- shadow_temperature_relief_pass:

                                           New general utility pass
                                           that independently modulates
                                           the color temperature of
                                           shadow and highlight zones:
                                           warm amber in shadows
                                           (inhabited warmth, reflected
                                           light), cool blue-grey in
                                           bright highlights (diffused
                                           sky/daylight quality).
                                           Both zones have smooth
                                           sigmoid transitions to
                                           avoid visible boundaries.

Warm-start base: mona_lisa_s132.png
Applies: s132 accumulated base + s133 (Bassano anisotropic diffusion -- NEW)
                                 + shadow temperature relief (NEW improvement)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# ── Locate warm-start base ─────────────────────────────────────────────────────
S132_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s132.png"),
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s132.png"
    ),
    "/c/Source/painting-pipeline/mona_lisa_s132.png",
    "C:/Source/painting-pipeline/mona_lisa_s132.png",
]

base_path = None
for c in S132_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s132.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S132_CANDIDATES)
    )

print(f"Loading session-132 base: {base_path}", flush=True)


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
    Apply session 133 passes on top of the session-132 accumulated canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 133 warm-start from mona_lisa_s132.png", flush=True)
    print("Applying: accumulated s132 base + Jacopo Bassano (133 -- NEW)", flush=True)
    print("       + shadow_temperature_relief_pass (NEW improvement)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # ── Session 133 (NEW): Jacopo Bassano anisotropic diffusion pass ──────────
    # Perona-Malik anisotropic diffusion: iteratively smooth flat tonal areas
    # while preserving edges via the conductance function c(s) = exp(-(s/K)²).
    # Creates smooth luminous 'tonal pools' in the lights and shadows, with firm
    # chiaroscuro boundaries preserved exactly.  Followed by a firelight warmth
    # boost on bright pixels — copper-amber proportional to luminance.
    # Eleventh distinct processing mode in the pipeline.
    print("Jacopo Bassano anisotropic diffusion pass (session 133 -- NEW)...", flush=True)
    p.bassano_pastoral_glow_pass(
        n_iter           = 14,
        K                = 0.07,
        gamma            = 0.10,
        firelight_warm   = 0.22,
        firelight_thresh = 0.45,
        opacity          = 0.30,
    )

    # ── Session 133 artistic improvement: shadow temperature relief ────────────
    # Independently modulates shadow and highlight color temperature:
    # shadows receive warm amber (inhabited warmth of reflected light),
    # highlights receive subtle cool blue (sky/diffused daylight quality).
    # Smooth sigmoid transitions at both thresholds prevent visible seams.
    print("Shadow temperature relief pass (session 133 -- NEW improvement)...", flush=True)
    p.shadow_temperature_relief_pass(
        shadow_thresh   = 0.34,
        shadow_warm_r   = 0.04,
        shadow_warm_g   = 0.012,
        light_cool_b    = 0.025,
        light_thresh    = 0.72,
        transition_zone = 0.18,
        opacity         = 0.38,
    )

    # ── Finishing passes ───────────────────────────────────────────────────────

    # Velatura: Bassano often unified his canvases with a thin warm amber-copper
    # glaze that intensified the firelight quality and deepened the dark ground.
    print("Velatura warm glaze (Bassano firelight unification)...", flush=True)
    p.velatura_pass(midtone_tint=(0.82, 0.60, 0.28), midtone_opacity=0.09)

    # Vignette and crackle
    print("Finishing (vignette + crackle)...", flush=True)
    p.finish(vignette=0.52, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s133.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
