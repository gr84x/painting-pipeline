"""
paint_mona_lisa_s129.py -- Session 129 portrait painting.

Warm-start from mona_lisa_s128.png (latest accumulated canvas),
then applies session 129 addition.

Session 129 additions:
  - piazzetta                                -- NEW (session 129)
                                               Giovanni Battista Piazzetta
                                               (1682–1754), Italian (Venetian).
                                               The great independent master of
                                               Venetian Baroque Tenebrism —
                                               velvet near-black shadow warmth
                                               with glowing impasto amber
                                               highlights.  A slow, deliberate
                                               painter who worked in the
                                               opposite direction from Tiepolo:
                                               not toward airy luminosity but
                                               into warm candlelit darkness.

  SESSION 129 ARTISTIC IMPROVEMENT -- piazzetta_velvet_shadow_pass:

                                               New pass encoding Piazzetta's
                                               two defining technical poles:
                                               velvet shadow warmth and
                                               impasto amber highlight lift.

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

                                               This pass introduces the
                                               seventh distinct processing
                                               mode: GLOBAL HISTOGRAM
                                               PERCENTILE ANALYSIS.

                                               Algorithm:
                                               (1) Compute luminance for
                                               every pixel (BT.601).
                                               (2) Argsort the flat array
                                               to produce a rank-order
                                               percentile map in [0,1].
                                               (3) Shadow zone (rank <
                                               shadow_percentile): warm
                                               umber deepening (R+, B-).
                                               (4) Highlight zone (rank >
                                               highlight_percentile): warm
                                               amber lift (R+, G+).
                                               (5) Midtone: unchanged.

Warm-start base: mona_lisa_s128.png
Applies: s128 accumulated base + s129 (Piazzetta velvet shadow -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# ── Locate warm-start base ─────────────────────────────────────────────────────
S128_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s128.png"),
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s128.png"
    ),
    "/c/Source/painting-pipeline/mona_lisa_s128.png",
    "C:/Source/painting-pipeline/mona_lisa_s128.png",
]

base_path = None
for c in S128_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s128.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S128_CANDIDATES)
    )

print(f"Loading session-128 base: {base_path}", flush=True)


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
    Apply session 129 pass on top of the session-128 accumulated canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 129 warm-start from mona_lisa_s128.png", flush=True)
    print("Applying: accumulated s128 base + Piazzetta (129 -- NEW)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # ── Session 129 (NEW): Piazzetta velvet shadow pass ────────────────────────
    # Global histogram percentile analysis: velvet shadow warming in the darkest
    # percentile zone, warm amber impasto lift in the brightest percentile zone.
    print("Piazzetta velvet shadow pass (session 129 -- NEW)...", flush=True)
    p.piazzetta_velvet_shadow_pass(
        shadow_percentile   = 0.22,
        highlight_percentile= 0.82,
        shadow_warm_r       = 0.020,
        shadow_warm_b       = 0.024,
        highlight_warm_r    = 0.034,
        highlight_warm_g    = 0.013,
        opacity             = 0.33,
    )

    # ── Finishing passes ───────────────────────────────────────────────────────

    # Final glaze — warm amber-umber (Piazzetta's candlelit unifying tone)
    print("Final glaze (warm amber-umber for Piazzetta)...", flush=True)
    p.glaze((0.52, 0.40, 0.25), opacity=0.007)

    # Vignette and crackle
    print("Finishing (vignette + crackle)...", flush=True)
    p.finish(vignette=0.54, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s129.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
