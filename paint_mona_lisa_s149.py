"""
paint_mona_lisa_s149.py -- Session 149 portrait painting.

Warm-start from mona_lisa_s148.png (latest accumulated canvas),
then applies session 149 additions.

Session 149 additions:
  - romanino                            -- NEW (session 149)
                                           Girolamo Romanino (c.1484–1562),
                                           Brescian Venetian Impasto.
                                           The most physically expressive
                                           painter of the Brescian school —
                                           trained in Venice under Giorgione
                                           and early Titian, then returned
                                           to Brescia where he developed a
                                           bold impasto technique unique in
                                           Italian Renaissance painting.
                                           Loaded brushstrokes build visible
                                           ridges that catch raking light.

  SESSION 149 MAIN PASS -- romanino_brescian_impasto_pass:

                                           Twenty-ninth distinct mode:
                                           HEIGHT-FIELD OBLIQUE-LIGHT
                                           IMPASTO SIMULATION.

                                           Computes smoothed luma height
                                           field (Gaussian sigma=1.0),
                                           extracts spatial gradient via
                                           np.gradient, then simulates
                                           upper-left oblique lighting:
                                           light = −(gx + gy) × relief_scale.
                                           Lit ridges (gate_high) → warm
                                           ochre R/G boost.
                                           Shadowed valleys (gate_shadow) →
                                           cool B boost, slight R reduction.
                                           Asymmetric warm/cool relief on
                                           every brushstroke ridge.

  SESSION 149 ARTISTIC IMPROVEMENT -- highlight_velatura_pass:

                                           TRANSPARENT OIL-GLAZE VEIL IN
                                           UPPER-MIDTONE / HIGHLIGHT ZONE.

                                           Smooth bump gate in [0.58, 0.92]
                                           blends toward warm amber glaze
                                           (R=0.88, G=0.68, B=0.28) at
                                           vel_amount=0.12, then applies
                                           local contrast softening via
                                           Gaussian within the gate zone,
                                           simulating the optical depth of
                                           a transparent velatura.
                                           Distinct from existing velatura_pass
                                           (midtone zone [0.28, 0.72]):
                                           this targets the upper highlight
                                           zone for added luminous depth.

Warm-start base: mona_lisa_s148.png
Applies: s148 accumulated base + s149 (Romanino impasto -- NEW)
                                  + s149 (Highlight velatura -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S148_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s148.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s148.png"),
    "C:/Source/painting-pipeline/mona_lisa_s148.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s147.png"),
    "C:/Source/painting-pipeline/mona_lisa_s147.png",
]

base_path = None
for c in S148_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S148_CANDIDATES)
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
    print("Session 149 warm-start from accumulated canvas", flush=True)
    print("Applying: Romanino oblique-light impasto (149 -- NEW)", flush=True)
    print("Applying: Highlight velatura glaze veil (149 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 149 (NEW): Romanino Brescian impasto pass --------------------
    # Twenty-ninth distinct mode: HEIGHT-FIELD OBLIQUE-LIGHT IMPASTO SIMULATION.
    #
    # Design intent for the accumulated Leonardo/Venetian canvas:
    #
    # The accumulated canvas (28 passes) has rich tonal depth and warm Venetian
    # color but lacks the physical, tactile quality of impasto paint surface.
    # Romanino's pass adds a subtle three-dimensional relief to every brushstroke
    # texture in the image: raised ridges catch warm ochre light from the upper
    # left, recessed valleys take on cool blue recession.
    #
    # sigma=1.2: slightly wider than default to match the macro-scale
    #   brushstroke texture of the accumulated canvas rather than pixel-level
    #   noise. Smooth height field emphasises structural brushwork.
    # relief_scale=14.0: modest scale on the accumulated multi-layer canvas
    #   to avoid over-emphasising texture that was built up subtly. The canvas
    #   is already rich; this adds physical depth without dominance.
    # impasto_warm_r=0.045, impasto_warm_g=0.022: warm ochre on lit ridges —
    #   Romanino's characteristic warm sienna-ochre paint catching light.
    # shadow_b=0.028, shadow_r=0.012: cool blue recession in shadowed valleys —
    #   Venetian influence: cool atmospheric air pools in paint valleys.
    # opacity=0.30: moderate. The relief is felt rather than announced.
    print("Romanino Brescian impasto pass (session 149 -- NEW)...", flush=True)
    p.romanino_brescian_impasto_pass(
        sigma          = 1.2,
        relief_scale   = 14.0,
        impasto_warm_r = 0.045,
        impasto_warm_g = 0.022,
        shadow_b       = 0.028,
        shadow_r       = 0.012,
        opacity        = 0.30,
    )

    # -- Session 149 (NEW): Highlight velatura pass ----------------------------
    # Artistic improvement: TRANSPARENT OIL-GLAZE VEIL IN HIGHLIGHT ZONE.
    #
    # Design intent:
    # The Mona Lisa's upper-midtone and highlight zones (the luminous forehead,
    # the lit cheek, the pearl-white veil, the sky highlights in the landscape)
    # are bright but can benefit from the optical depth of a warm amber velatura.
    # This pass adds the illusion of a transparent oil glaze tinting the bright
    # passages with a warm amber-gold that enriches their luminosity without
    # dulling them.
    #
    # vel_lo=0.60, vel_hi=0.90: targets the upper-midtone / highlight zone.
    #   The smooth bump gate peaks at luma=0.75 — catching the face highlights
    #   and the bright landscape sky without touching the deep midtones
    #   (already handled by Sodoma and Bordone passes).
    # vel_amount=0.08: conservative — this is a layer over 28 prior passes,
    #   each of which has contributed its own warmth. The velatura adds
    #   luminous depth rather than adding more warmth.
    # contrast_amount=0.05: very gentle contrast softening — smooths micro-
    #   transitions in the bright flesh zone, giving the skin its seamless
    #   velatura quality without dulling the sfumato edge work.
    # glaze_r=0.88, glaze_g=0.70, glaze_b=0.32: slightly cooler amber than
    #   default to complement the existing warm layers without over-yellowing.
    # opacity=0.22: subtle. The velatura is a finishing veil.
    print("Highlight velatura pass (session 149 artistic improvement -- NEW)...", flush=True)
    p.highlight_velatura_pass(
        vel_lo          = 0.60,
        vel_hi          = 0.90,
        glaze_r         = 0.88,
        glaze_g         = 0.70,
        glaze_b         = 0.32,
        vel_amount      = 0.08,
        contrast_amount = 0.05,
        sigma           = 0.8,
        opacity         = 0.22,
    )

    # -- Carry-forward passes from session 148 --------------------------------

    # Bordone parabolic warmth (from s148 -- carry forward)
    print("Bordone parabolic midtone warmth pass (session 148 carry-forward)...", flush=True)
    p.bordone_venetian_warmth_pass(
        deepen_amount = 0.06,
        warm_r        = 0.014,
        warm_g        = 0.008,
        opacity       = 0.22,
    )

    # Luminous ground (from s148 -- carry forward)
    print("Luminous ground imprimatura pass (session 148 carry-forward)...", flush=True)
    p.luminous_ground_pass(
        ground_r      = 0.48,
        ground_g      = 0.35,
        ground_b      = 0.20,
        ground_hi     = 0.32,
        ground_amount = 0.12,
        gamma_ground  = 2.0,
        opacity       = 0.22,
    )

    # Sodoma Sienese dreamveil (from s147 -- carry forward)
    print("Sodoma Sienese dreamveil pass (session 147 carry-forward)...", flush=True)
    p.sodoma_sienese_dreamveil_pass(
        warm_lo      = 0.38,
        warm_hi      = 0.72,
        warm_r       = 0.016,
        warm_g       = 0.008,
        sat_lo       = 0.48,
        sat_hi       = 0.78,
        sat_lift     = 0.04,
        veil_sigma   = 2.2,
        veil_amount  = 0.05,
        sky_lo       = 0.82,
        sky_b        = 0.012,
        opacity      = 0.20,
    )

    # Specular clarity (from s147 -- carry forward)
    print("Specular clarity pass (session 147 carry-forward)...", flush=True)
    p.specular_clarity_pass(
        clarity_lo   = 0.72,
        sigma        = 1.0,
        usm_amount   = 0.10,
        cool_lo      = 0.85,
        cool_b       = 0.010,
        cool_r       = 0.008,
        opacity      = 0.18,
    )

    # Gossaert pearl-crystalline (from s146 -- carry forward)
    print("Gossaert pearl-crystalline pass (session 146 carry-forward)...", flush=True)
    p.gossaert_pearl_crystalline_pass(
        shadow_hi       = 0.36,
        highlight_lo    = 0.70,
        pearl_cool_b    = 0.028,
        pearl_desat     = 0.08,
        shadow_warm_r   = 0.018,
        shadow_warm_b   = 0.014,
        mid_sat_boost   = 0.035,
        crystal_sigma   = 2.0,
        crystal_amount  = 0.06,
        opacity         = 0.20,
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
        shadow_tint     = 0.022,
        penumbra_chroma = 0.045,
        opacity         = 0.16,
    )

    # Cambiaso geometric planes (from s145 -- carry forward)
    print("Cambiaso geometric planes pass (session 145 carry-forward)...", flush=True)
    p.cambiaso_geometric_planes_pass(
        sigma_coarse   = 22.0,
        sigma_medium   = 5.0,
        flatten_amount = 0.40,
        edge_boost     = 0.16,
        sigma_edge     = 2.0,
        terra_r        = 0.68,
        terra_g        = 0.45,
        terra_b        = 0.18,
        terra_lo       = 0.08,
        terra_hi       = 0.38,
        terra_amount   = 0.040,
        opacity        = 0.10,
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
        cool_amount   = 0.028,
        sat_dampen    = 0.05,
        opacity       = 0.11,
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
        opacity       = 0.09,
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
        warm_r      = 0.060,
        warm_g      = 0.020,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.09,
    )

    # Velatura: warm amber unifying glaze (carry forward)
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.035)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.48, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s149.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
