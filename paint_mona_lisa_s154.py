"""
paint_mona_lisa_s154.py -- Session 154 portrait painting.

Warm-start from mona_lisa_s153.png (Francesco Furini accumulated canvas),
then applies session 154 additions.

Session 154 additions:
  - bartolomeo_veneto                    -- NEW (session 154)
                                           Bartolomeo Veneto (active c. 1502-1546),
                                           Lombardy-Venetian Jewel Realism.
                                           Portraitist of extraordinary precision
                                           and almost entirely mysterious biography.
                                           Fuses cool Lombard-Leonardesque flesh
                                           precision with Venetian jewel-tone
                                           brocade richness.  His palette splits
                                           between deep blue-violet fabric shadows
                                           (ultramarine brocade) and warm gold-amber
                                           fabric highlights (hammered gold brocade)
                                           -- a HUE-ANGULAR DUAL-POLE system.

  SESSION 154 MAIN PASS -- bartolomeo_veneto_jewel_brocade_pass:

                                           Thirty-fourth distinct mode:
                                           HUE-ANGULAR DUAL-POLE SATURATION
                                           DEEPENING.

                                           Two hue poles computed from RGB channel
                                           relationships (no HSV conversion):
                                           BLUE-VIOLET POLE: blue_proxy =
                                           clip(B - max(R,G), 0, 1); gated to
                                           shadow zone smooth bump [0.05, 0.55].
                                           GOLD-AMBER POLE: gold_proxy =
                                           clip(R-B, 0,1) * clip(G-B*0.5, 0,1);
                                           gated to highlight smooth bump [0.42, 0.88].
                                           Blue zone: R-, G-, B+.
                                           Gold zone: R+, G+, B-.
                                           Deepens brocade richness; leaves cool
                                           ivory flesh largely untouched.

  SESSION 154 ARTISTIC IMPROVEMENT -- iridescent_glaze_pass:

                                           FULL-GRADIENT ORIENTATION WARM/COOL
                                           IRIDESCENT SHIMMER IN PAINT TRANSITIONS.

                                           Computes full 2D gradient orientation
                                           via arctan2(gy, gx) (both Sobel axes)
                                           -- distinct from ter_brugghen horizontal-
                                           only Sobel.  warm_dir = clip(cos(theta),
                                           0, 1); cool_dir = clip(-cos(theta), 0, 1).
                                           Gated by midtone luma [0.28, 0.75] AND
                                           gradient magnitude (95th pct normalised).
                                           Warm tint (R+, G+) in warm-facing gradient
                                           zones; cool tint (B+, R-) in cool-facing.
                                           Simulates iridescent thin-film glaze
                                           quality across curved painted surfaces.

Warm-start base: mona_lisa_s153.png
Applies: s153 accumulated base + s154 (Bartolomeo Veneto jewel brocade -- NEW)
                                  + s154 (Iridescent glaze -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S153_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s153.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s153.png"),
    "C:/Source/painting-pipeline/mona_lisa_s153.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s152.png"),
    "C:/Source/painting-pipeline/mona_lisa_s152.png",
]

base_path = None
for c in S153_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S153_CANDIDATES)
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
    print("Session 154 warm-start from accumulated canvas", flush=True)
    print("Applying: Bartolomeo Veneto jewel brocade (154 -- NEW)", flush=True)
    print("Applying: Iridescent glaze shimmer (154 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 154 (NEW): Bartolomeo Veneto jewel brocade pass --------------
    # Thirty-fourth distinct mode: HUE-ANGULAR DUAL-POLE SATURATION DEEPENING.
    #
    # The Mona Lisa's dress is dark forest-green/blue-black with faint brocade
    # and a semi-transparent gauze wrap.  The blue-violet pole will deepen any
    # existing blue/violet fabric zones in the shadow regions.  The gold-amber
    # pole targets the warmer mid-to-highlight zones (landscape background,
    # skin highlights, amber glaze layers accumulated from prior sessions).
    #
    # blue_lo=0.05, blue_hi=0.55: shadow gate — matches the dark dress zones
    #   and deep umber shadows of the accumulated canvas.
    # gold_lo=0.44, gold_hi=0.86: highlight gate — targets the warm amber
    #   glaze and ochre flesh highlight zones.
    # blue_deepen=0.10: subtle — the dress is almost neutral black, so we
    #   enrich rather than saturate aggressively.
    # gold_deepen=0.12: moderate — deepens the brocade warmth in highlights.
    # pole_strength=0.55: moderate — preserves prior 35+ pass accumulation.
    # opacity=0.24: gentle on the 36th layer.
    print("Bartolomeo Veneto jewel brocade pass (session 154 -- NEW)...", flush=True)
    p.bartolomeo_veneto_jewel_brocade_pass(
        blue_lo       = 0.05,
        blue_hi       = 0.55,
        gold_lo       = 0.44,
        gold_hi       = 0.86,
        blue_deepen   = 0.10,
        gold_deepen   = 0.12,
        pole_strength = 0.55,
        opacity       = 0.24,
    )

    # -- Session 154 (NEW): Iridescent glaze pass -----------------------------
    # Artistic improvement: FULL-GRADIENT ORIENTATION WARM/COOL IRIDESCENT
    # SHIMMER IN PAINT TRANSITIONS.
    #
    # The Mona Lisa is painted with thin oil glazes over a warm imprimatura.
    # The curved surface of the face, hands, and distant landscape creates
    # a subtle orientation-dependent warm/cool shimmer in transition zones.
    # This pass simulates that quality across all gradient orientations.
    #
    # mid_lo=0.30, mid_hi=0.73: midtone gate — active in the modelled flesh
    #   and landscape transition zones, not in deepest shadow or pure highlight.
    # warm_r=0.030, warm_g=0.014: delicate warm shimmer in +x gradient zones.
    # cool_b=0.026, cool_r=0.014: delicate cool shimmer in -x gradient zones.
    # shimmer_strength=0.48: moderate — iridescent quality should be barely
    #   perceptible, not a strong directional bias.
    # opacity=0.16: very gentle — this is the 37th accumulated layer.
    print("Iridescent glaze pass (session 154 artistic improvement -- NEW)...", flush=True)
    p.iridescent_glaze_pass(
        mid_lo           = 0.30,
        mid_hi           = 0.73,
        warm_r           = 0.030,
        warm_g           = 0.014,
        cool_b           = 0.026,
        cool_r           = 0.014,
        shimmer_strength = 0.48,
        opacity          = 0.16,
    )

    # -- Carry-forward passes from session 153 --------------------------------

    # Furini moonlit sfumato (from s153 -- carry forward)
    print("Furini moonlit sfumato pass (session 153 carry-forward)...", flush=True)
    p.furini_moonlit_sfumato_pass(
        hi_lo          = 0.55,
        hi_hi          = 0.90,
        cool_b         = 0.025,
        cool_r         = 0.014,
        cool_g         = 0.006,
        cool_strength  = 0.55,
        opacity        = 0.22,
    )

    # Translucent fabric (from s153 -- carry forward)
    print("Translucent fabric pass (session 153 carry-forward)...", flush=True)
    p.translucent_fabric_pass(
        fab_lo         = 0.32,
        fab_hi         = 0.70,
        fabric_r       = 0.10,
        fabric_g       = 0.14,
        fabric_b       = 0.11,
        fabric_opacity = 0.12,
        edge_factor    = 0.45,
        opacity        = 0.18,
    )

    # Gaudenzio warm devotion (from s152 -- carry forward)
    print("Gaudenzio warm devotion pass (session 152 carry-forward)...", flush=True)
    p.gaudenzio_warm_devotion_pass(
        shad_lo        = 0.05,
        shad_hi        = 0.40,
        warm_r         = 0.032,
        warm_g         = 0.018,
        warm_b         = 0.008,
        warm_strength  = 0.50,
        opacity        = 0.24,
    )

    # Atmospheric depth gradient (from s152 -- carry forward)
    print("Atmospheric depth gradient pass (session 152 carry-forward)...", flush=True)
    p.atmospheric_depth_gradient_pass(
        atm_warm_r   = 0.020,
        atm_warm_g   = 0.012,
        atm_cool_b   = 0.022,
        atm_cool_r   = 0.010,
        luma_lo      = 0.12,
        opacity      = 0.22,
    )

    # Ter Brugghen raking amber (from s151 -- carry forward)
    print("Ter Brugghen raking amber pass (session 151 carry-forward)...", flush=True)
    p.ter_brugghen_raking_amber_pass(
        mid_lo         = 0.24,
        mid_hi         = 0.74,
        warm_r         = 0.038,
        warm_g         = 0.018,
        cool_b         = 0.030,
        cool_r         = 0.014,
        ridge_strength = 0.55,
        opacity        = 0.20,
    )

    # Adaptive local contrast (from s151 -- carry forward)
    print("Adaptive local contrast pass (session 151 carry-forward)...", flush=True)
    p.adaptive_local_contrast_pass(
        block_size     = 80,
        p_lo           = 0.06,
        p_hi           = 0.94,
        contrast_lo    = 0.22,
        contrast_hi    = 0.78,
        stretch_amount = 0.28,
        opacity        = 0.16,
    )

    # Beccafumi nacreous glow (from s150 -- carry forward)
    print("Beccafumi nacreous glow pass (session 150 carry-forward)...", flush=True)
    p.beccafumi_nacreous_glow_pass(
        sigma_bloom   = 3.5,
        glow_lo       = 0.30,
        glow_hi       = 0.75,
        glow_warm_r   = 0.042,
        glow_warm_g   = 0.024,
        glow_cool_b   = 0.030,
        glow_cool_r   = 0.014,
        glow_strength = 0.50,
        opacity       = 0.26,
    )

    # Penumbra softening (from s150 -- carry forward)
    print("Penumbra softening pass (session 150 carry-forward)...", flush=True)
    p.penumbra_softening_pass(
        pen_lo        = 0.20,
        pen_hi        = 0.50,
        pen_sigma     = 1.8,
        soften_amount = 0.40,
        opacity       = 0.22,
    )

    # Romanino Brescian impasto (from s149 -- carry forward)
    print("Romanino Brescian impasto pass (session 149 carry-forward)...", flush=True)
    p.romanino_brescian_impasto_pass(
        sigma          = 1.2,
        relief_scale   = 14.0,
        impasto_warm_r = 0.045,
        impasto_warm_g = 0.022,
        shadow_b       = 0.028,
        shadow_r       = 0.012,
        opacity        = 0.22,
    )

    # Highlight velatura (from s149 -- carry forward)
    print("Highlight velatura pass (session 149 carry-forward)...", flush=True)
    p.highlight_velatura_pass(
        vel_lo          = 0.60,
        vel_hi          = 0.90,
        glaze_r         = 0.88,
        glaze_g         = 0.70,
        glaze_b         = 0.32,
        vel_amount      = 0.08,
        contrast_amount = 0.05,
        sigma           = 0.8,
        opacity         = 0.16,
    )

    # Bordone parabolic warmth (from s148 -- carry forward)
    print("Bordone parabolic midtone warmth pass (session 148 carry-forward)...", flush=True)
    p.bordone_venetian_warmth_pass(
        deepen_amount = 0.06,
        warm_r        = 0.014,
        warm_g        = 0.008,
        opacity       = 0.16,
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
        opacity       = 0.16,
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
        opacity      = 0.14,
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
        opacity      = 0.13,
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
        opacity         = 0.14,
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
        opacity         = 0.11,
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
        opacity        = 0.07,
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
        opacity       = 0.08,
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
        opacity       = 0.07,
    )

    # Focal vignette (from s142 -- carry forward)
    print("Focal vignette pass (session 142 carry-forward)...", flush=True)
    p.focal_vignette_pass(
        focal_x           = 0.50,
        focal_y           = 0.35,
        vignette_strength = 0.22,
        vignette_power    = 2.2,
        cool_shift        = 0.015,
        opacity           = 0.22,
    )

    # Glazing depth pass (from session 141 -- carry forward)
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.060,
        warm_g      = 0.020,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.07,
    )

    # Velatura: warm amber unifying glaze (carry forward)
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.028)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.46, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s154.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
