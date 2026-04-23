"""
paint_mona_lisa_s148.py -- Session 148 portrait painting.

Warm-start from mona_lisa_s147.png (latest accumulated canvas),
then applies session 148 additions.

Session 148 additions:
  - paris_bordone                       -- NEW (session 148)
                                           Paris Bordone (1500-1571),
                                           Venetian Intimate Colorism.
                                           Trained briefly under Titian,
                                           Bordone absorbed the Venetian
                                           warm coloring tradition and
                                           Giorgione's atmospheric softness,
                                           then intensified both toward a
                                           more intimate, sensuous chromatic
                                           register.  His flesh radiates a
                                           characteristic amber-gold warmth
                                           in the midtones — achieved through
                                           the Venetian multi-glaze tradition.
                                           The warm umber imprimatura glows
                                           through thin dark passages as a
                                           warm amber undertone — the
                                           'luminous ground' phenomenon
                                           distinctive to Venetian painting.

  SESSION 148 MAIN PASS -- bordone_venetian_warmth_pass:

                                           Twenty-seventh distinct mode:
                                           PARABOLIC MIDTONE CHROMATIC
                                           DEEPENING.

                                           The parabolic gate
                                           w = 4 * luma * (1 - luma)
                                           peaks at luma=0.5 and zeros
                                           at both extremes — targeting
                                           only the midtone flesh zone.
                                           Two operations:
                                           (1) Chromatic deepening: each
                                               channel pushed away from
                                               per-pixel luma by
                                               deepen_amount * w;
                                           (2) Warm tint: R += warm_r*w,
                                               G += warm_g*w.
                                           Distinct from all 26 prior
                                           modes by the parabolic gate
                                           and simultaneous chroma
                                           deepening + warm tint.

  SESSION 148 ARTISTIC IMPROVEMENT -- luminous_ground_pass:

                                           CUBIC-FALLOFF IMPRIMATURA
                                           WARMTH IN DARK ZONES.

                                           Simulates warm umber
                                           imprimatura glowing through
                                           thin dark paint layers.
                                           Gate: (1 - luma/ground_hi)^gamma
                                           concentrates in darkest pixels.
                                           Blends toward warm ground color.
                                           Distinct from shadow_transparency
                                           (cool violet) — this injects warm
                                           amber ground warmth.

Warm-start base: mona_lisa_s147.png
Applies: s147 accumulated base + s148 (Bordone warmth -- NEW)
                                  + s148 (Luminous ground -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S147_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s147.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s147.png"),
    "C:/Source/painting-pipeline/mona_lisa_s147.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s146.png"),
    "C:/Source/painting-pipeline/mona_lisa_s146.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s145.png"),
    "C:/Source/painting-pipeline/mona_lisa_s145.png",
]

base_path = None
for c in S147_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S147_CANDIDATES)
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
    print("Session 148 warm-start from accumulated canvas", flush=True)
    print("Applying: Paris Bordone parabolic warmth (148 -- NEW)", flush=True)
    print("Applying: Luminous ground imprimatura glow (148 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 148 (NEW): Paris Bordone parabolic warmth pass ---------------
    # Twenty-seventh distinct mode: PARABOLIC MIDTONE CHROMATIC DEEPENING.
    #
    # Design intent for the accumulated Leonardo canvas:
    #
    # 1. Chromatic deepening: deepen_amount=0.08 — conservative on the
    #    accumulated canvas which already has 27 layers of processing.
    #    The parabolic gate ensures only midtone pixels are affected.
    #    The Mona Lisa's flesh midtones (luminance ~0.4-0.65) will gain
    #    slightly deeper, richer chromatic presence — Bordone's intimate
    #    Venetian quality without overriding Leonardo's sfumato.
    #
    # 2. Warm tint: warm_r=0.018, warm_g=0.010 — very subtle warm amber
    #    flush in the midtone zone.  The canvas already has Leonardo's
    #    amber warmth; Bordone adds Venetian chromatic intimacy.
    #
    # opacity=0.30: moderate; the effect is gentle but cumulatively
    # enriches the flesh midtones over the accumulated sfumato base.
    print("Bordone parabolic midtone warmth pass (session 148 -- NEW)...", flush=True)
    p.bordone_venetian_warmth_pass(
        deepen_amount = 0.08,
        warm_r        = 0.018,
        warm_g        = 0.010,
        opacity       = 0.30,
    )

    # -- Session 148 (NEW): Luminous ground pass -------------------------------
    # Artistic improvement: CUBIC-FALLOFF IMPRIMATURA WARMTH IN DARK ZONES.
    #
    # Design intent:
    # The Mona Lisa's dark background and deep shadow areas (under chin,
    # shadow side of costume, darkest landscape passages) should carry a
    # subtle warm umber glow — the imprimatura shining through thin paint.
    # ground_hi=0.32: targets pixels below luminance 0.32 (shadow zone).
    # ground_amount=0.14: gentle blend toward warm umber ground color.
    # gamma_ground=2.0: quadratic falloff — effect concentrated in darkest.
    # opacity=0.28: moderate; this is a unifying pass over dark shadows.
    print("Luminous ground imprimatura pass (session 148 artistic improvement -- NEW)...", flush=True)
    p.luminous_ground_pass(
        ground_r      = 0.48,
        ground_g      = 0.35,
        ground_b      = 0.20,
        ground_hi     = 0.32,
        ground_amount = 0.14,
        gamma_ground  = 2.0,
        opacity       = 0.28,
    )

    # -- Carry-forward passes from session 147 --------------------------------

    # Sodoma Sienese dreamveil (from s147 -- carry forward)
    print("Sodoma Sienese dreamveil pass (session 147 carry-forward)...", flush=True)
    p.sodoma_sienese_dreamveil_pass(
        warm_lo      = 0.38,
        warm_hi      = 0.72,
        warm_r       = 0.018,
        warm_g       = 0.010,
        sat_lo       = 0.48,
        sat_hi       = 0.78,
        sat_lift     = 0.04,
        veil_sigma   = 2.2,
        veil_amount  = 0.05,
        sky_lo       = 0.82,
        sky_b        = 0.013,
        opacity      = 0.22,
    )

    # Specular clarity (from s147 -- carry forward)
    print("Specular clarity pass (session 147 carry-forward)...", flush=True)
    p.specular_clarity_pass(
        clarity_lo   = 0.72,
        sigma        = 1.0,
        usm_amount   = 0.12,
        cool_lo      = 0.85,
        cool_b       = 0.012,
        cool_r       = 0.009,
        opacity      = 0.20,
    )

    # Gossaert pearl-crystalline (from s146 -- carry forward)
    print("Gossaert pearl-crystalline pass (session 146 carry-forward)...", flush=True)
    p.gossaert_pearl_crystalline_pass(
        shadow_hi       = 0.36,
        highlight_lo    = 0.70,
        pearl_cool_b    = 0.032,
        pearl_desat     = 0.10,
        shadow_warm_r   = 0.020,
        shadow_warm_b   = 0.016,
        mid_sat_boost   = 0.04,
        crystal_sigma   = 2.0,
        crystal_amount  = 0.07,
        opacity         = 0.22,
    )

    # Shadow transparency (from s146 -- carry forward)
    print("Shadow transparency pass (session 146 carry-forward)...", flush=True)
    p.shadow_transparency_pass(
        shadow_hi       = 0.38,
        penumbra_lo     = 0.28,
        penumbra_hi     = 0.55,
        violet_r        = 0.38,
        violet_g        = 0.30,
        violet_b        = 0.68,
        shadow_tint     = 0.025,
        penumbra_chroma = 0.05,
        opacity         = 0.18,
    )

    # Cambiaso geometric planes (from s145 -- carry forward)
    print("Cambiaso geometric planes pass (session 145 carry-forward)...", flush=True)
    p.cambiaso_geometric_planes_pass(
        sigma_coarse   = 22.0,
        sigma_medium   = 5.0,
        flatten_amount = 0.45,
        edge_boost     = 0.18,
        sigma_edge     = 2.0,
        terra_r        = 0.68,
        terra_g        = 0.45,
        terra_b        = 0.18,
        terra_lo       = 0.08,
        terra_hi       = 0.38,
        terra_amount   = 0.045,
        opacity        = 0.12,
    )

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
        cool_amount   = 0.032,
        sat_dampen    = 0.06,
        opacity       = 0.13,
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
        opacity       = 0.10,
    )

    # Focal vignette (from s142 -- carry forward)
    print("Focal vignette pass (session 142 carry-forward)...", flush=True)
    p.focal_vignette_pass(
        focal_x           = 0.50,
        focal_y           = 0.35,
        vignette_strength = 0.22,
        vignette_power    = 2.2,
        cool_shift        = 0.015,
        opacity           = 0.28,
    )

    # Glazing depth pass (from session 141 -- carry forward)
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.065,
        warm_g      = 0.022,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.10,
    )

    # Velatura: warm amber unifying glaze
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.04)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.48, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s148.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
