"""
paint_mona_lisa_s127.py -- Session 127 portrait painting.

Warm-start from mona_lisa_s124.png (latest available accumulated canvas),
then applies session 127 addition.

Session 127 additions:
  - domenichino                              -- NEW (session 127)
                                               Domenico Zampieri
                                               'Il Domenichino'
                                               (1581–1641), Italian
                                               (Bolognese).
                                               Direct student of Annibale
                                               Carracci, trained alongside
                                               Albani and Guido Reni.
                                               Supreme classicist of the
                                               Bolognese school — painting
                                               as rational geometric beauty.
                                               His cerulean shadow zones
                                               and crystalline flat surfaces
                                               represent the intellectual
                                               apex of Carracci-reform
                                               classicism.

  SESSION 127 ARTISTIC IMPROVEMENT -- domenichino_cerulean_crystalline_pass:

                                               New pass encoding
                                               Domenichino's two defining
                                               technical qualities:
                                               cerulean shadow cooling
                                               and crystalline flat-zone
                                               clarity.

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

                                               This pass introduces the
                                               fifth distinct processing
                                               mode: LOCAL VARIANCE FIELD
                                               ANALYSIS.

                                               Algorithm:
                                               (1) Compute luminance
                                               variance in a sliding
                                               local window:
                                               var = E[lum²] - E[lum]²

                                               (2) Smooth the variance
                                               map with a Gaussian for
                                               soft zone boundaries.

                                               (3) LOW-VARIANCE zones
                                               (smooth flat areas) below
                                               shadow_limit: apply cerulean
                                               cooling — B up, R down.

                                               (4) HIGH-VARIANCE zones
                                               (textured areas): apply
                                               gentle unsharp masking
                                               for crystalline clarity.

Warm-start base: mona_lisa_s124.png
Applies: s124 accumulated base + s127 (Domenichino cerulean crystalline -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# ── Locate warm-start base ─────────────────────────────────────────────────────
S124_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s124.png"),
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s124.png"
    ),
    "/c/Source/painting-pipeline/mona_lisa_s124.png",
    "C:/Source/painting-pipeline/mona_lisa_s124.png",
]

base_path = None
for c in S124_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s124.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S124_CANDIDATES)
    )

print(f"Loading session-124 base: {base_path}", flush=True)


# ── Utilities ──────────────────────────────────────────────────────────────────

def make_figure_mask() -> np.ndarray:
    """
    Elliptical figure mask for the Mona Lisa composition.
    Returns float32 array in [0, 1], 1 = figure, 0 = background.
    """
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
    # Notify cairo that the surface was modified directly via the buffer.
    # Without this, subsequent cairo context operations (glaze, vignette)
    # may read stale data when no intermediate cairo draw calls were made.
    p.canvas.surface.mark_dirty()


def paint(out_dir: str = ".") -> str:
    """
    Apply session 127 pass on top of the session-124 accumulated canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 127 warm-start from mona_lisa_s124.png", flush=True)
    print("Applying: accumulated s124 base + Domenichino (127 -- NEW)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    # Load session-124 base canvas
    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # ── Session 127 (NEW): Domenichino cerulean crystalline pass ──────────────
    # Local-variance-field analysis: cerulean shadow cooling in smooth zones,
    # crystalline clarity (unsharp masking) in high-variance textured zones.
    print("Domenichino cerulean crystalline pass (session 127 -- NEW)…", flush=True)
    p.domenichino_cerulean_crystalline_pass(
        local_window        = 7,
        cerulean_threshold  = 0.005,
        cerulean_b          = 0.034,
        cerulean_g          = 0.009,
        cerulean_r          = 0.011,
        shadow_limit        = 0.52,
        clarity_threshold   = 0.008,
        clarity_strength    = 0.038,
        clarity_blur        = 2.0,
        blur_radius         = 3.0,
        opacity             = 0.32,
    )

    # ── Finishing passes ───────────────────────────────────────────────────────

    # Final glaze — warm neutral Bolognese (Domenichino's academic finish)
    print("Final glaze (warm Bolognese neutral for Domenichino)…", flush=True)
    p.glaze((0.58, 0.52, 0.40), opacity=0.006)

    # Vignette and crackle
    print("Finishing (vignette + crackle)…", flush=True)
    p.finish(vignette=0.52, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s127.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
