"""
paint_mona_lisa_s158.py -- Session 158 portrait painting.

Warm-start from mona_lisa_s157.png (Giampietrino accumulated canvas),
then applies session 158 additions.

Session 158 additions:
  - jean_baptiste_greuze                 -- NEW (session 158)
                                           Jean-Baptiste Greuze (1725–1805),
                                           French Sentimentalist.
                                           Master of the 'tête d'expression' —
                                           sentimental expression heads of young
                                           women rendered with extraordinary
                                           emotional immediacy.  His signature:
                                           WARM ROSE-CARNATION mid-flesh flush
                                           paired with a COOL-PEARL DEWY shimmer
                                           at specular peaks — making his
                                           subjects read as warm living flesh
                                           capped by a moist, luminous surface.

  SESSION 158 MAIN PASS -- greuze_sentimental_carnation_pass:

                                           FORTY-SECOND DISTINCT MODE:
                                           SENTIMENTAL CARNATION GLOW —
                                           WARM ROSE-FLESH + COOL DEWY
                                           PEARL SHIMMER.

                                           Carnation gate [0.38, 0.80]:
                                           R+carn_r, G+carn_g, B-carn_b
                                           — rose-carnation push in the
                                           mid-flesh zone (distinct from
                                           amber: R+G+ direction vs
                                           rose: R+ G+small B-).
                                           Dewy shimmer gate [0.82, 1.0]:
                                           B+dew_b, R-dew_r — cool-pearl
                                           moisture at specular peaks.
                                           Composite at opacity=0.28.

  SESSION 158 ARTISTIC IMPROVEMENT -- edge_sfumato_dissolution_pass:

                                           FORTY-THIRD DISTINCT MODE:
                                           GRADIENT-SELECTIVE EDGE
                                           DISSOLUTION — SFUMATO AT
                                           FORM BOUNDARIES.

                                           Per-channel Sobel gradient
                                           magnitude → grad_norm →
                                           edge_wt = grad_norm^power
                                           × edge_strength.  Full-canvas
                                           Gaussian blur (sigma=2.5).
                                           Per-pixel blend: orig×(1-wt)
                                           + blurred×wt.  Composite at
                                           opacity=0.35.  Distinct from
                                           penumbra_softening_pass (that
                                           uses luma gate × Sobel; this
                                           uses ONLY gradient magnitude).

Warm-start base: mona_lisa_s157.png
Applies: s157 accumulated base + s158 (Greuze sentimental carnation -- NEW)
                                   + s158 (Edge sfumato dissolution -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S157_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s157.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s157.png"),
    "C:/Source/painting-pipeline/mona_lisa_s157.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s156.png"),
    "C:/Source/painting-pipeline/mona_lisa_s156.png",
]

base_path = None
for c in S157_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S157_CANDIDATES)
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
    print("Session 158 warm-start from accumulated canvas", flush=True)
    print("Applying: Greuze sentimental carnation (158 -- NEW)", flush=True)
    print("Applying: Edge sfumato dissolution pass (158 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 158 (NEW): Greuze sentimental carnation pass -----------------
    # Forty-second distinct mode: SENTIMENTAL CARNATION GLOW.
    #
    # Greuze's flesh lives in two registers: a warm rose-carnation zone in the
    # mid-flesh [0.38–0.80] and a cool-pearl dewy shimmer at the specular peak
    # [0.82–1.0].  The Mona Lisa's flesh tones — the warm ivory brow, the lit
    # cheekbone — fall squarely in the carnation gate.  The specular highlights
    # on the forehead and the glistening specular point in the eyes fall in the
    # dewy shimmer gate.  This pass enriches the mid-flesh with a subtle rose
    # warmth (more French, more sentimental than the amber-honey of the Venetian
    # painters) and adds a cool moisture to the specular peaks.
    #
    # carn_lo=0.42, carn_hi=0.78: slightly tightened from default to focus on
    #   the Mona Lisa's warm ivory flesh mid-tone; avoids pushing the background
    #   landscape or shadow tones into rose.
    # carn_r=0.032, carn_g=0.008, carn_b=0.014: restrained carnation — enough
    #   to introduce Greuze's characteristic warmth without visibly pinking the
    #   flesh in a way inconsistent with the cool sfumato of Leonardo's model.
    # dew_lo=0.84, dew_hi=1.00: dewy shimmer in the uppermost specular zone.
    # dew_b=0.022, dew_r=0.009: very gentle pearl shimmer — the dewy quality
    #   is a whisper, not a highlight; it should read as moisture, not paint.
    # opacity=0.28: light composite on the 44th accumulated layer.
    print("Greuze sentimental carnation pass (session 158 -- NEW)...", flush=True)
    p.greuze_sentimental_carnation_pass(
        carn_lo = 0.42,
        carn_hi = 0.78,
        carn_r  = 0.032,
        carn_g  = 0.008,
        carn_b  = 0.014,
        dew_lo  = 0.84,
        dew_hi  = 1.00,
        dew_b   = 0.022,
        dew_r   = 0.009,
        opacity = 0.28,
    )

    # -- Session 158 (NEW): Edge sfumato dissolution pass ---------------------
    # Forty-third distinct mode: GRADIENT-SELECTIVE EDGE DISSOLUTION.
    #
    # The Mona Lisa is the supreme demonstration of sfumato-as-edge-phenomenon:
    # the famous ambiguity of the smile arises precisely because Leonardo
    # dissolved the lip corners into the surrounding flesh, making it impossible
    # to read the expression with certainty.  This pass applies that principle
    # computationally: wherever the image has a high gradient (a sharp transition),
    # the pass dissolves it into the surrounding tone.  Smooth areas — the open
    # skin of the brow, the undifferentiated landscape distance — are left entirely
    # unchanged.  Only the boundaries between forms are softened.
    #
    # grad_threshold=0.08: dissolves moderate gradient boundaries as well as sharp
    #   ones, consistent with Leonardo's thorough sfumato application.
    # edge_power=1.8: slightly supra-linear falloff — concentrates dissolution at
    #   the sharpest edges while leaving low-gradient transitions nearly untouched.
    # edge_strength=0.62: at the sharpest boundary zones, 62% blend toward the
    #   Gaussian-blurred image; enough to dissolve the contour without destroying
    #   the underlying form.
    # blur_sigma=2.2: relatively narrow Gaussian — the dissolution is local to the
    #   edge zone rather than a wide atmospheric blur.
    # opacity=0.35: moderate composite on the 45th accumulated layer.
    print("Edge sfumato dissolution pass (session 158 artistic improvement -- NEW)...", flush=True)
    p.edge_sfumato_dissolution_pass(
        grad_threshold = 0.08,
        edge_power     = 1.8,
        edge_strength  = 0.62,
        blur_sigma     = 2.2,
        opacity        = 0.35,
    )

    # -- Carry-forward passes from session 157 --------------------------------

    # Giampietrino warm devotion (from s157 -- carry forward)
    print("Giampietrino warm devotion pass (session 157 carry-forward)...", flush=True)
    p.giampietrino_warm_devotion_pass(
        hi_lo    = 0.56,
        hi_hi    = 0.86,
        warm_r   = 0.032,
        warm_g   = 0.018,
        shad_lo  = 0.06,
        shad_hi  = 0.40,
        cool_b   = 0.030,
        cool_r   = 0.013,
        opacity  = 0.20,
    )

    # Peripheral defocus (from s157 -- carry forward)
    print("Peripheral defocus pass (session 157 carry-forward)...", flush=True)
    p.peripheral_defocus_pass(
        inner_radius  = 0.42,
        blur_sigma    = 3.5,
        power         = 2.0,
        blur_strength = 0.50,
        opacity       = 0.25,
    )

    # Gentile da Fabriano gold tooling (from s156 -- carry forward)
    print("Gentile da Fabriano gold tooling pass (session 156 carry-forward)...", flush=True)
    p.gentile_da_fabriano_gold_tooling_pass(
        hi_lo          = 0.60,
        hi_hi          = 0.95,
        gold_r         = 0.028,
        gold_g         = 0.017,
        gold_b         = 0.008,
        ridge_strength = 0.48,
        opacity        = 0.12,
    )

    # Chromatic fringe (from s156 -- carry forward)
    print("Chromatic fringe pass (session 156 carry-forward)...", flush=True)
    p.chromatic_fringe_pass(
        edge_lo        = 0.10,
        edge_hi        = 0.78,
        fringe_warm_r  = 0.018,
        fringe_warm_g  = 0.007,
        fringe_cool_b  = 0.015,
        fringe_cool_r  = 0.006,
        opacity        = 0.08,
    )

    # Melozzo zenith radiance (from s155 -- carry forward)
    print("Melozzo zenith radiance pass (session 155 carry-forward)...", flush=True)
    p.melozzo_zenith_radiance_pass(
        mid_lo          = 0.28,
        mid_hi          = 0.75,
        warm_r          = 0.014,
        warm_g          = 0.007,
        cool_b          = 0.012,
        cool_r          = 0.005,
        zenith_strength = 0.38,
        opacity         = 0.11,
    )

    # Warm ambient occlusion (from s155 -- carry forward)
    print("Warm ambient occlusion pass (session 155 carry-forward)...", flush=True)
    p.warm_ambient_occlusion_pass(
        occ_radius = 10.0,
        occ_max    = 0.22,
        shad_lo    = 0.10,
        shad_hi    = 0.42,
        warm_r     = 0.018,
        warm_g     = 0.009,
        opacity    = 0.10,
    )

    # Bartolomeo Veneto jewel brocade (from s154 -- carry forward)
    print("Bartolomeo Veneto jewel brocade pass (session 154 carry-forward)...", flush=True)
    p.bartolomeo_veneto_jewel_brocade_pass(
        blue_lo       = 0.05,
        blue_hi       = 0.55,
        gold_lo       = 0.44,
        gold_hi       = 0.86,
        blue_deepen   = 0.06,
        gold_deepen   = 0.07,
        pole_strength = 0.40,
        opacity       = 0.11,
    )

    # Iridescent glaze (from s154 -- carry forward)
    print("Iridescent glaze pass (session 154 carry-forward)...", flush=True)
    p.iridescent_glaze_pass(
        mid_lo           = 0.30,
        mid_hi           = 0.73,
        warm_r           = 0.013,
        warm_g           = 0.006,
        cool_b           = 0.011,
        cool_r           = 0.005,
        shimmer_strength = 0.28,
        opacity          = 0.07,
    )

    # Furini moonlit sfumato (from s153 -- carry forward)
    print("Furini moonlit sfumato pass (session 153 carry-forward)...", flush=True)
    p.furini_moonlit_sfumato_pass(
        hi_lo          = 0.55,
        hi_hi          = 0.90,
        cool_b         = 0.011,
        cool_r         = 0.005,
        cool_g         = 0.002,
        cool_strength  = 0.35,
        opacity        = 0.10,
    )

    # Translucent fabric (from s153 -- carry forward)
    print("Translucent fabric pass (session 153 carry-forward)...", flush=True)
    p.translucent_fabric_pass(
        fab_lo         = 0.32,
        fab_hi         = 0.70,
        fabric_r       = 0.10,
        fabric_g       = 0.14,
        fabric_b       = 0.11,
        fabric_opacity = 0.06,
        edge_factor    = 0.38,
        opacity        = 0.08,
    )

    # Gaudenzio warm devotion (from s152 -- carry forward)
    print("Gaudenzio warm devotion pass (session 152 carry-forward)...", flush=True)
    p.gaudenzio_warm_devotion_pass(
        shad_lo        = 0.05,
        shad_hi        = 0.40,
        warm_r         = 0.014,
        warm_g         = 0.008,
        warm_b         = 0.003,
        warm_strength  = 0.30,
        opacity        = 0.10,
    )

    # Atmospheric depth gradient (from s152 -- carry forward)
    print("Atmospheric depth gradient pass (session 152 carry-forward)...", flush=True)
    p.atmospheric_depth_gradient_pass(
        atm_warm_r   = 0.009,
        atm_warm_g   = 0.005,
        atm_cool_b   = 0.010,
        atm_cool_r   = 0.004,
        luma_lo      = 0.12,
        opacity      = 0.10,
    )

    # Ter Brugghen raking amber (from s151 -- carry forward)
    print("Ter Brugghen raking amber pass (session 151 carry-forward)...", flush=True)
    p.ter_brugghen_raking_amber_pass(
        mid_lo         = 0.24,
        mid_hi         = 0.74,
        warm_r         = 0.018,
        warm_g         = 0.008,
        cool_b         = 0.013,
        cool_r         = 0.006,
        ridge_strength = 0.32,
        opacity        = 0.09,
    )

    # Adaptive local contrast (from s151 -- carry forward)
    print("Adaptive local contrast pass (session 151 carry-forward)...", flush=True)
    p.adaptive_local_contrast_pass(
        block_size     = 80,
        p_lo           = 0.06,
        p_hi           = 0.94,
        contrast_lo    = 0.22,
        contrast_hi    = 0.78,
        stretch_amount = 0.14,
        opacity        = 0.07,
    )

    # Beccafumi nacreous glow (from s150 -- carry forward)
    print("Beccafumi nacreous glow pass (session 150 carry-forward)...", flush=True)
    p.beccafumi_nacreous_glow_pass(
        sigma_bloom   = 3.5,
        glow_lo       = 0.30,
        glow_hi       = 0.75,
        glow_warm_r   = 0.020,
        glow_warm_g   = 0.010,
        glow_cool_b   = 0.015,
        glow_cool_r   = 0.007,
        glow_strength = 0.30,
        opacity       = 0.12,
    )

    # Penumbra softening (from s150 -- carry forward)
    print("Penumbra softening pass (session 150 carry-forward)...", flush=True)
    p.penumbra_softening_pass(
        pen_lo        = 0.20,
        pen_hi        = 0.50,
        pen_sigma     = 1.8,
        soften_amount = 0.22,
        opacity       = 0.10,
    )

    # Romanino Brescian impasto (from s149 -- carry forward)
    print("Romanino Brescian impasto pass (session 149 carry-forward)...", flush=True)
    p.romanino_brescian_impasto_pass(
        sigma          = 1.2,
        relief_scale   = 11.0,
        impasto_warm_r = 0.020,
        impasto_warm_g = 0.010,
        shadow_b       = 0.013,
        shadow_r       = 0.006,
        opacity        = 0.10,
    )

    # Highlight velatura (from s149 -- carry forward)
    print("Highlight velatura pass (session 149 carry-forward)...", flush=True)
    p.highlight_velatura_pass(
        vel_lo          = 0.60,
        vel_hi          = 0.90,
        glaze_r         = 0.88,
        glaze_g         = 0.70,
        glaze_b         = 0.32,
        vel_amount      = 0.04,
        contrast_amount = 0.02,
        sigma           = 0.8,
        opacity         = 0.07,
    )

    # Bordone parabolic warmth (from s148 -- carry forward)
    print("Bordone parabolic midtone warmth pass (session 148 carry-forward)...", flush=True)
    p.bordone_venetian_warmth_pass(
        deepen_amount = 0.03,
        warm_r        = 0.006,
        warm_g        = 0.003,
        opacity       = 0.07,
    )

    # Luminous ground (from s148 -- carry forward)
    print("Luminous ground imprimatura pass (session 148 carry-forward)...", flush=True)
    p.luminous_ground_pass(
        ground_r      = 0.48,
        ground_g      = 0.35,
        ground_b      = 0.20,
        ground_hi     = 0.32,
        ground_amount = 0.06,
        gamma_ground  = 2.0,
        opacity       = 0.07,
    )

    # Sodoma Sienese dreamveil (from s147 -- carry forward)
    print("Sodoma Sienese dreamveil pass (session 147 carry-forward)...", flush=True)
    p.sodoma_sienese_dreamveil_pass(
        warm_lo      = 0.38,
        warm_hi      = 0.72,
        warm_r       = 0.006,
        warm_g       = 0.003,
        sat_lo       = 0.48,
        sat_hi       = 0.78,
        sat_lift     = 0.018,
        veil_sigma   = 2.2,
        veil_amount  = 0.024,
        sky_lo       = 0.82,
        sky_b        = 0.005,
        opacity      = 0.06,
    )

    # Specular clarity (from s147 -- carry forward)
    print("Specular clarity pass (session 147 carry-forward)...", flush=True)
    p.specular_clarity_pass(
        clarity_lo   = 0.72,
        sigma        = 1.0,
        usm_amount   = 0.05,
        cool_lo      = 0.85,
        cool_b       = 0.005,
        cool_r       = 0.003,
        opacity      = 0.06,
    )

    # Gossaert pearl-crystalline (from s146 -- carry forward)
    print("Gossaert pearl-crystalline pass (session 146 carry-forward)...", flush=True)
    p.gossaert_pearl_crystalline_pass(
        shadow_hi       = 0.36,
        highlight_lo    = 0.70,
        pearl_cool_b    = 0.013,
        pearl_desat     = 0.03,
        shadow_warm_r   = 0.008,
        shadow_warm_b   = 0.006,
        mid_sat_boost   = 0.014,
        crystal_sigma   = 2.0,
        crystal_amount  = 0.02,
        opacity         = 0.06,
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
        shadow_tint     = 0.010,
        penumbra_chroma = 0.020,
        opacity         = 0.06,
    )

    # Cambiaso geometric planes (from s145 -- carry forward)
    print("Cambiaso geometric planes pass (session 145 carry-forward)...", flush=True)
    p.cambiaso_geometric_planes_pass(
        sigma_coarse   = 22.0,
        sigma_medium   = 5.0,
        flatten_amount = 0.22,
        edge_boost     = 0.08,
        sigma_edge     = 2.0,
        terra_r        = 0.68,
        terra_g        = 0.45,
        terra_b        = 0.18,
        terra_lo       = 0.08,
        terra_hi       = 0.38,
        terra_amount   = 0.018,
        opacity        = 0.03,
    )

    # Focal vignette (carry forward)
    print("Focal vignette pass (session 142 carry-forward)...", flush=True)
    p.focal_vignette_pass(
        focal_x           = 0.50,
        focal_y           = 0.35,
        vignette_strength = 0.16,
        vignette_power    = 2.2,
        cool_shift        = 0.008,
        opacity           = 0.11,
    )

    # Glazing depth pass (carry forward)
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.030,
        warm_g      = 0.010,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.03,
    )

    # Velatura: warm amber unifying glaze (carry forward)
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.016)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.44, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s158.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
