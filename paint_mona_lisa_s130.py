"""
paint_mona_lisa_s130.py -- Session 130 portrait painting.

Warm-start from mona_lisa_s129.png (latest accumulated canvas),
then applies session 130 addition.

Session 130 additions:
  - sebastiano_del_piombo                -- NEW (session 130)
                                           Sebastiano del Piombo
                                           (1485–1547), Italian (Venetian-Roman).
                                           Trained under Bellini and Giorgione in
                                           Venice; moved to Rome in 1511 where he
                                           befriended Michelangelo — the only painter
                                           Michelangelo ever respected as an equal.
                                           Fused Venetian warmth and color richness
                                           with Michelangelesque monumental gravity
                                           and sculptural form weight.

  SESSION 130 ARTISTIC IMPROVEMENT -- sebastiano_sculptural_depth_pass:

                                           New pass encoding Sebastiano's defining
                                           fusion of Venetian surface blending and
                                           Roman sculptural form.

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

                                           This pass introduces the
                                           eighth distinct processing
                                           mode: IMAGE STRUCTURE TENSOR
                                           COHERENCE-DRIVEN FORM SMOOTHING.

                                           Algorithm:
                                           (1) Compute luminance (BT.601).
                                           (2) Sobel gradient: Gx, Gy.
                                           (3) Build 2×2 structure tensor J:
                                             J11 = Gaussian(Gx²),
                                             J12 = Gaussian(Gx·Gy),
                                             J22 = Gaussian(Gy²).
                                           (4) Eigenvalues λ1 ≥ λ2 of J:
                                             λ1 large, λ2≈0 → edge;
                                             λ1≈λ2≈0 → flat interior.
                                           (5) Coherence c =
                                             ((λ1−λ2)/(λ1+λ2+ε))^p.
                                           (6) Interpolate:
                                             result = orig·c +
                                             Gaussian_smooth·(1−c).
                                           (7) Warm Venetian tint on
                                             smooth fraction (R+).

Warm-start base: mona_lisa_s129.png
Applies: s129 accumulated base + s130 (Sebastiano sculptural depth -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# ── Locate warm-start base ─────────────────────────────────────────────────────
S129_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s129.png"),
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s129.png"
    ),
    "/c/Source/painting-pipeline/mona_lisa_s129.png",
    "C:/Source/painting-pipeline/mona_lisa_s129.png",
]

base_path = None
for c in S129_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s129.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S129_CANDIDATES)
    )

print(f"Loading session-129 base: {base_path}", flush=True)


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
    Apply session 130 pass on top of the session-129 accumulated canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 130 warm-start from mona_lisa_s129.png", flush=True)
    print("Applying: accumulated s129 base + Sebastiano del Piombo (130 -- NEW)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # ── Session 130 (NEW): Sebastiano sculptural depth pass ────────────────────
    # Image structure tensor coherence-driven form smoothing: interior planes of
    # the figure acquire deep, rounded sculptural presence; edges remain crisp.
    # The Venetian warm tint on the smooth fraction adds Sebastiano's amber richness.
    print("Sebastiano sculptural depth pass (session 130 -- NEW)...", flush=True)
    p.sebastiano_sculptural_depth_pass(
        integration_sigma   = 2.5,
        smooth_sigma        = 4.0,
        coherence_power     = 2.0,
        warm_tint_r         = 0.012,
        opacity             = 0.30,
    )

    # ── Finishing passes ───────────────────────────────────────────────────────

    # Final glaze — deep amber-umber (Sebastiano's rich Venetian-Roman unifying tone)
    print("Final glaze (deep amber-umber for Sebastiano)...", flush=True)
    p.glaze((0.52, 0.38, 0.20), opacity=0.006)

    # Vignette and crackle
    print("Finishing (vignette + crackle)...", flush=True)
    p.finish(vignette=0.54, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s130.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
