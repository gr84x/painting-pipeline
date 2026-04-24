"""
paint_mona_lisa_s155.py -- Session 155 portrait painting.

Warm-start from mona_lisa_s154.png (Bartolomeo Veneto accumulated canvas),
then applies session 155 additions.

Session 155 additions:
  - melozzo_da_forli                     -- NEW (session 155)
                                           Melozzo da Forlì (1438-1494),
                                           Umbrian-Roman Renaissance.
                                           Supreme master of di sotto in su
                                           perspective and overhead zenith light.
                                           His fragmentary Angel Musicians in
                                           the Vatican Pinacoteca are the
                                           definitive example of forms modelled
                                           by light descending from directly
                                           overhead -- luminous ivory tops,
                                           warm-umber under-surfaces.

  SESSION 155 MAIN PASS -- melozzo_zenith_radiance_pass:

                                           Thirty-sixth distinct mode:
                                           VERTICAL OVERHEAD ZENITH LIGHT --
                                           TOP-OF-FORM WARM LIFT AND
                                           UNDER-SURFACE COOL SHADOW DEEPENING.

                                           Vertical position map: y_frac =
                                           row/(H-1); zenith_wt = 1-y_frac
                                           [peaks at TOP = overhead]; under_wt
                                           = y_frac [peaks at BOTTOM].
                                           Midtone gate: smooth bump [0.28,
                                           0.75].  Zenith-lit: R+, G+ by
                                           zenith_wt x midgate.  Under-surface:
                                           B+, R- by under_wt x midgate.
                                           OPPOSITE polarity from atmospheric_
                                           depth_gradient_pass (which warms the
                                           foreground/bottom and cools the
                                           background/top -- aerial perspective
                                           vs. this pass's overhead light).

  SESSION 155 ARTISTIC IMPROVEMENT -- warm_ambient_occlusion_pass:

                                           THIRTY-SEVENTH DISTINCT MODE:
                                           LOCAL LUMINANCE CONCAVITY WARM-AMBER
                                           INFILL (AMBIENT INTER-REFLECTION).

                                           Wide Gaussian blur (sigma=10) of
                                           luminance -> local_mean.  Concavity =
                                           clip(local_mean - luma, 0, 0.25).
                                           Normalise: occ_norm = concavity/0.25.
                                           Shadow gate: smooth bump [0.10, 0.42].
                                           weight = occ_norm x shad_gate.
                                           R+warm_r, G+warm_g in concave zones.
                                           Simulates warm indirect reflected light
                                           in eye sockets, nostril wings, ear
                                           canals -- the ambient inter-reflection
                                           that makes old master portrait recesses
                                           glow warmly rather than go dead black.

Warm-start base: mona_lisa_s154.png
Applies: s154 accumulated base + s155 (Melozzo zenith radiance -- NEW)
                                   + s155 (Warm ambient occlusion -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S154_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s154.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s154.png"),
    "C:/Source/painting-pipeline/mona_lisa_s154.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s153.png"),
    "C:/Source/painting-pipeline/mona_lisa_s153.png",
]

base_path = None
for c in S154_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S154_CANDIDATES)
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
    print("Session 155 warm-start from accumulated canvas", flush=True)
    print("Applying: Melozzo da Forli zenith radiance (155 -- NEW)", flush=True)
    print("Applying: Warm ambient occlusion infill (155 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 155 (NEW): Melozzo zenith radiance pass ----------------------
    # Thirty-sixth distinct mode: VERTICAL OVERHEAD ZENITH LIGHT.
    #
    # The Mona Lisa is lit from the upper left (sfumato convention) but the
    # portrait prompt also implies a generally diffused overhead light that
    # warms the top of the forehead and crown while the underside of the chin
    # and the lap area receive slightly cooler ambient light.  This pass
    # reinforces that overhead quality gently.
    #
    # mid_lo=0.28, mid_hi=0.75: midtone gate -- excludes near-black shadows
    #   (garment, background void) and near-white specular highlights (which
    #   should not shift further warm).
    # warm_r=0.028, warm_g=0.014: subtle warm lift at top -- forehead, crown,
    #   background sky above the horizon.
    # cool_b=0.024, cool_r=0.012: subtle cool shadow at bottom -- lap, lower
    #   background, underside of the gauze wrap.
    # zenith_strength=0.55: moderate -- the overhead light is gentle, not harsh.
    # opacity=0.22: gentle on the 38th accumulated layer.
    print("Melozzo zenith radiance pass (session 155 -- NEW)...", flush=True)
    p.melozzo_zenith_radiance_pass(
        mid_lo          = 0.28,
        mid_hi          = 0.75,
        warm_r          = 0.028,
        warm_g          = 0.014,
        cool_b          = 0.024,
        cool_r          = 0.012,
        zenith_strength = 0.55,
        opacity         = 0.22,
    )

    # -- Session 155 (NEW): Warm ambient occlusion pass -----------------------
    # Thirty-seventh distinct mode: LOCAL LUMINANCE CONCAVITY WARM-AMBER INFILL.
    #
    # The portrait prompt describes rich modelling of eye sockets, nostrils,
    # and the hands folded in the lap.  All these concave areas receive warm
    # reflected light in great old master portraits.  This pass identifies
    # pixels darker than their local neighbourhood and applies a gentle warm
    # amber infill -- simulating the inter-reflection between warm surrounding
    # surfaces (warm ochre skin, warm fabric) into the recessed shadow zones.
    #
    # occ_radius=10.0: neighbourhood radius -- captures the extent of warm
    #   ambient light in the surrounding area.
    # occ_max=0.25: depth clamped so only moderate recessions are treated;
    #   prevents over-warming in the absolute darkest voids (dress, background).
    # shad_lo=0.10, shad_hi=0.42: shadow gate -- active in the dark-midtone
    #   zone where reflected light is most perceptible.
    # warm_r=0.035, warm_g=0.018: gentle warm amber -- enough to give life
    #   to shadow recesses without shifting overall colour balance.
    # opacity=0.18: very gentle -- this is the 39th accumulated layer.
    print("Warm ambient occlusion pass (session 155 artistic improvement -- NEW)...", flush=True)
    p.warm_ambient_occlusion_pass(
        occ_radius = 10.0,
        occ_max    = 0.25,
        shad_lo    = 0.10,
        shad_hi    = 0.42,
        warm_r     = 0.035,
        warm_g     = 0.018,
        opacity    = 0.18,
    )

    # -- Carry-forward passes from session 154 --------------------------------

    # Bartolomeo Veneto jewel brocade (from s154 -- carry forward)
    print("Bartolomeo Veneto jewel brocade pass (session 154 carry-forward)...", flush=True)
    p.bartolomeo_veneto_jewel_brocade_pass(
        blue_lo       = 0.05,
        blue_hi       = 0.55,
        gold_lo       = 0.44,
        gold_hi       = 0.86,
        blue_deepen   = 0.10,
        gold_deepen   = 0.12,
        pole_strength = 0.55,
        opacity       = 0.20,
    )

    # Iridescent glaze (from s154 -- carry forward)
    print("Iridescent glaze pass (session 154 carry-forward)...", flush=True)
    p.iridescent_glaze_pass(
        mid_lo           = 0.30,
        mid_hi           = 0.73,
        warm_r           = 0.026,
        warm_g           = 0.012,
        cool_b           = 0.022,
        cool_r           = 0.012,
        shimmer_strength = 0.42,
        opacity          = 0.14,
    )

    # Furini moonlit sfumato (from s153 -- carry forward)
    print("Furini moonlit sfumato pass (session 153 carry-forward)...", flush=True)
    p.furini_moonlit_sfumato_pass(
        hi_lo          = 0.55,
        hi_hi          = 0.90,
        cool_b         = 0.022,
        cool_r         = 0.012,
        cool_g         = 0.005,
        cool_strength  = 0.50,
        opacity        = 0.20,
    )

    # Translucent fabric (from s153 -- carry forward)
    print("Translucent fabric pass (session 153 carry-forward)...", flush=True)
    p.translucent_fabric_pass(
        fab_lo         = 0.32,
        fab_hi         = 0.70,
        fabric_r       = 0.10,
        fabric_g       = 0.14,
        fabric_b       = 0.11,
        fabric_opacity = 0.10,
        edge_factor    = 0.45,
        opacity        = 0.16,
    )

    # Gaudenzio warm devotion (from s152 -- carry forward)
    print("Gaudenzio warm devotion pass (session 152 carry-forward)...", flush=True)
    p.gaudenzio_warm_devotion_pass(
        shad_lo        = 0.05,
        shad_hi        = 0.40,
        warm_r         = 0.028,
        warm_g         = 0.016,
        warm_b         = 0.007,
        warm_strength  = 0.48,
        opacity        = 0.20,
    )

    # Atmospheric depth gradient (from s152 -- carry forward)
    print("Atmospheric depth gradient pass (session 152 carry-forward)...", flush=True)
    p.atmospheric_depth_gradient_pass(
        atm_warm_r   = 0.018,
        atm_warm_g   = 0.010,
        atm_cool_b   = 0.020,
        atm_cool_r   = 0.009,
        luma_lo      = 0.12,
        opacity      = 0.20,
    )

    # Ter Brugghen raking amber (from s151 -- carry forward)
    print("Ter Brugghen raking amber pass (session 151 carry-forward)...", flush=True)
    p.ter_brugghen_raking_amber_pass(
        mid_lo         = 0.24,
        mid_hi         = 0.74,
        warm_r         = 0.034,
        warm_g         = 0.016,
        cool_b         = 0.026,
        cool_r         = 0.012,
        ridge_strength = 0.50,
        opacity        = 0.18,
    )

    # Adaptive local contrast (from s151 -- carry forward)
    print("Adaptive local contrast pass (session 151 carry-forward)...", flush=True)
    p.adaptive_local_contrast_pass(
        block_size     = 80,
        p_lo           = 0.06,
        p_hi           = 0.94,
        contrast_lo    = 0.22,
        contrast_hi    = 0.78,
        stretch_amount = 0.26,
        opacity        = 0.14,
    )

    # Beccafumi nacreous glow (from s150 -- carry forward)
    print("Beccafumi nacreous glow pass (session 150 carry-forward)...", flush=True)
    p.beccafumi_nacreous_glow_pass(
        sigma_bloom   = 3.5,
        glow_lo       = 0.30,
        glow_hi       = 0.75,
        glow_warm_r   = 0.038,
        glow_warm_g   = 0.022,
        glow_cool_b   = 0.028,
        glow_cool_r   = 0.013,
        glow_strength = 0.48,
        opacity       = 0.22,
    )

    # Penumbra softening (from s150 -- carry forward)
    print("Penumbra softening pass (session 150 carry-forward)...", flush=True)
    p.penumbra_softening_pass(
        pen_lo        = 0.20,
        pen_hi        = 0.50,
        pen_sigma     = 1.8,
        soften_amount = 0.38,
        opacity       = 0.20,
    )

    # Romanino Brescian impasto (from s149 -- carry forward)
    print("Romanino Brescian impasto pass (session 149 carry-forward)...", flush=True)
    p.romanino_brescian_impasto_pass(
        sigma          = 1.2,
        relief_scale   = 13.0,
        impasto_warm_r = 0.040,
        impasto_warm_g = 0.020,
        shadow_b       = 0.025,
        shadow_r       = 0.011,
        opacity        = 0.20,
    )

    # Highlight velatura (from s149 -- carry forward)
    print("Highlight velatura pass (session 149 carry-forward)...", flush=True)
    p.highlight_velatura_pass(
        vel_lo          = 0.60,
        vel_hi          = 0.90,
        glaze_r         = 0.88,
        glaze_g         = 0.70,
        glaze_b         = 0.32,
        vel_amount      = 0.07,
        contrast_amount = 0.04,
        sigma           = 0.8,
        opacity         = 0.14,
    )

    # Bordone parabolic warmth (from s148 -- carry forward)
    print("Bordone parabolic midtone warmth pass (session 148 carry-forward)...", flush=True)
    p.bordone_venetian_warmth_pass(
        deepen_amount = 0.05,
        warm_r        = 0.012,
        warm_g        = 0.007,
        opacity       = 0.14,
    )

    # Luminous ground (from s148 -- carry forward)
    print("Luminous ground imprimatura pass (session 148 carry-forward)...", flush=True)
    p.luminous_ground_pass(
        ground_r      = 0.48,
        ground_g      = 0.35,
        ground_b      = 0.20,
        ground_hi     = 0.32,
        ground_amount = 0.10,
        gamma_ground  = 2.0,
        opacity       = 0.14,
    )

    # Sodoma Sienese dreamveil (from s147 -- carry forward)
    print("Sodoma Sienese dreamveil pass (session 147 carry-forward)...", flush=True)
    p.sodoma_sienese_dreamveil_pass(
        warm_lo      = 0.38,
        warm_hi      = 0.72,
        warm_r       = 0.014,
        warm_g       = 0.007,
        sat_lo       = 0.48,
        sat_hi       = 0.78,
        sat_lift     = 0.035,
        veil_sigma   = 2.2,
        veil_amount  = 0.045,
        sky_lo       = 0.82,
        sky_b        = 0.010,
        opacity      = 0.12,
    )

    # Specular clarity (from s147 -- carry forward)
    print("Specular clarity pass (session 147 carry-forward)...", flush=True)
    p.specular_clarity_pass(
        clarity_lo   = 0.72,
        sigma        = 1.0,
        usm_amount   = 0.09,
        cool_lo      = 0.85,
        cool_b       = 0.009,
        cool_r       = 0.007,
        opacity      = 0.11,
    )

    # Gossaert pearl-crystalline (from s146 -- carry forward)
    print("Gossaert pearl-crystalline pass (session 146 carry-forward)...", flush=True)
    p.gossaert_pearl_crystalline_pass(
        shadow_hi       = 0.36,
        highlight_lo    = 0.70,
        pearl_cool_b    = 0.025,
        pearl_desat     = 0.07,
        shadow_warm_r   = 0.016,
        shadow_warm_b   = 0.012,
        mid_sat_boost   = 0.030,
        crystal_sigma   = 2.0,
        crystal_amount  = 0.05,
        opacity         = 0.12,
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
        shadow_tint     = 0.020,
        penumbra_chroma = 0.040,
        opacity         = 0.10,
    )

    # Cambiaso geometric planes (from s145 -- carry forward)
    print("Cambiaso geometric planes pass (session 145 carry-forward)...", flush=True)
    p.cambiaso_geometric_planes_pass(
        sigma_coarse   = 22.0,
        sigma_medium   = 5.0,
        flatten_amount = 0.38,
        edge_boost     = 0.14,
        sigma_edge     = 2.0,
        terra_r        = 0.68,
        terra_g        = 0.45,
        terra_b        = 0.18,
        terra_lo       = 0.08,
        terra_hi       = 0.38,
        terra_amount   = 0.036,
        opacity        = 0.06,
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
        cool_amount   = 0.025,
        sat_dampen    = 0.04,
        opacity       = 0.07,
    )

    # Magnasco nervous brilliance (from s143 -- carry forward)
    print("Magnasco nervous brilliance pass (session 143 carry-forward)...", flush=True)
    p.magnasco_nervous_brilliance_pass(
        hf_sigma      = 3.0,
        scatter_px    = 2,
        bright_thresh = 0.04,
        dark_gate_lo  = 0.08,
        dark_gate_hi  = 0.55,
        warm_tint     = 0.035,
        opacity       = 0.06,
    )

    # Focal vignette (from s142 -- carry forward)
    print("Focal vignette pass (session 142 carry-forward)...", flush=True)
    p.focal_vignette_pass(
        focal_x           = 0.50,
        focal_y           = 0.35,
        vignette_strength = 0.22,
        vignette_power    = 2.2,
        cool_shift        = 0.014,
        opacity           = 0.20,
    )

    # Glazing depth pass (from session 141 -- carry forward)
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.055,
        warm_g      = 0.018,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.06,
    )

    # Velatura: warm amber unifying glaze (carry forward)
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.026)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.46, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s155.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
