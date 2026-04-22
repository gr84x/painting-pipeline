"""
paint_mona_lisa_s131.py -- Session 131 portrait painting.

Warm-start from mona_lisa_s130.png (latest accumulated canvas),
then applies session 131 addition.

Session 131 additions:
  - rosso_fiorentino                    -- NEW (session 131)
                                           Rosso Fiorentino
                                           (Giovanni Battista di Jacopo,
                                           1494–1540), Italian (Florentine).
                                           The most extreme of the Florentine
                                           Mannerists — close associate of
                                           Pontormo, but where Pontormo
                                           retreated inward, Rosso attacked
                                           outward.  Palette of acidic,
                                           dissonant colors: jaundiced
                                           yellows, cold bleached flesh,
                                           poison green-grey shadows.
                                           Angular, electrified compositions
                                           under existential stress.
                                           Refused harmonic color resolution.

  SESSION 131 ARTISTIC IMPROVEMENT -- rosso_chromatic_dissonance_pass:

                                           New pass encoding Rosso's
                                           defining quality: chromatic
                                           dissonance as expressive violence.

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

                                           This pass introduces the
                                           ninth distinct processing
                                           mode: HUE-SELECTIVE CHROMATIC
                                           TENSION MAPPING.

                                           Algorithm:
                                           (1) Convert RGB → HSV.
                                           (2) FLESH HUE TENSION:
                                             H ∈ [10°, 38°], S > 0.12 →
                                             rotate hue -hue_shift_flesh
                                             (toward acid lemon-yellow);
                                             reduce saturation by
                                             flesh_desat_amount.
                                           (3) SHADOW GREEN INJECTION:
                                             V < shadow_v_thresh →
                                             rotate hue +hue_shift_shadow
                                             (toward acid green-grey);
                                             slight S boost.
                                           (4) HIGHLIGHT ACID SHIFT:
                                             V > highlight_v_thresh,
                                             S > 0.08 →
                                             rotate hue +hue_shift_highlight
                                             (toward acid-yellow).
                                           (5) Convert HSV → RGB.
                                           (6) Composite at opacity.

Warm-start base: mona_lisa_s130.png
Applies: s130 accumulated base + s131 (Rosso chromatic dissonance -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# ── Locate warm-start base ─────────────────────────────────────────────────────
S130_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s130.png"),
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s130.png"
    ),
    "/c/Source/painting-pipeline/mona_lisa_s130.png",
    "C:/Source/painting-pipeline/mona_lisa_s130.png",
]

base_path = None
for c in S130_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s130.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S130_CANDIDATES)
    )

print(f"Loading session-130 base: {base_path}", flush=True)


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
    Apply session 131 pass on top of the session-130 accumulated canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 131 warm-start from mona_lisa_s130.png", flush=True)
    print("Applying: accumulated s130 base + Rosso Fiorentino (131 -- NEW)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # ── Session 131 (NEW): Rosso Fiorentino chromatic dissonance pass ──────────
    # Hue-selective chromatic tension mapping: flesh tones shift toward acid
    # lemon-yellow (bleached Mannerist skin); shadow regions receive poison-
    # green hue injection; highlights shift toward acid-yellow luminosity.
    # Ninth distinct processing mode in the pipeline.
    print("Rosso Fiorentino chromatic dissonance pass (session 131 -- NEW)...", flush=True)
    p.rosso_chromatic_dissonance_pass(
        hue_shift_flesh      = 8.0,
        flesh_desat_amount   = 0.08,
        hue_shift_shadow     = 14.0,
        shadow_v_thresh      = 0.46,
        hue_shift_highlight  = 7.0,
        highlight_v_thresh   = 0.72,
        opacity              = 0.26,
    )

    # ── Finishing passes ───────────────────────────────────────────────────────

    # No final glaze — Rosso refuses the harmonic unity a glaze would bring.
    # The chromatic tension must remain unresolved.

    # Vignette and crackle
    print("Finishing (vignette + crackle)...", flush=True)
    p.finish(vignette=0.54, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s131.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
