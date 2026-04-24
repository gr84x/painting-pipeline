"""
paint_mona_lisa_s156.py -- Session 156 portrait painting.

Warm-start from mona_lisa_s155.png (Melozzo da Forlì accumulated canvas),
then applies session 156 additions.

Session 156 additions:
  - gentile_da_fabriano                  -- NEW (session 156)
                                           Gentile da Fabriano (c. 1370–1427),
                                           International Gothic.
                                           Supreme master of gold-ground
                                           tempera on panel; Adoration of the
                                           Magi (1423) the defining monument
                                           of courtly Gothic opulence.
                                           Tooled/punched gold halos, flat
                                           jewel-tone pigment zones, crisp
                                           Gothic contour, verdaccio flesh.

  SESSION 156 MAIN PASS -- gentile_da_fabriano_gold_tooling_pass:

                                           THIRTY-EIGHTH DISTINCT MODE:
                                           LUMINANCE-RIDGE WARM GOLD SHIMMER
                                           TINTING.

                                           Isotropic Sobel gradient magnitude
                                           x high-luminance gate [0.60, 0.95]
                                           x ridge_strength=0.70.
                                           Apply warm gold tint to lit ridges:
                                           R+gold_r=0.070, G+gold_g=0.045,
                                           B-gold_b=0.020 (blue reduction
                                           deepens gold chroma).
                                           Composite at opacity=0.28.
                                           Simulates the catchlight sparkle of
                                           physically punched/tooled gold-ground
                                           halos and brocade surfaces under
                                           raking light.

  SESSION 156 ARTISTIC IMPROVEMENT -- chromatic_fringe_pass:

                                           THIRTY-NINTH DISTINCT MODE:
                                           PRISMATIC EDGE CHROMATIC FRINGE.

                                           Sobel gx, gy -> gradient magnitude
                                           -> norm_mag.  Edge gate: smooth bump
                                           in [0.08, 0.80] of norm_mag (excludes
                                           noise and specular clips).
                                           Bright-side gate = clip(gx_norm,0,1)
                                           x edge_gate.  Dark-side gate =
                                           clip(-gx_norm,0,1) x edge_gate.
                                           Warm fringe on bright side:
                                           R+0.045, G+0.018.  Cool fringe on
                                           dark side: B+0.040, R-0.016.
                                           Composite at opacity=0.18.
                                           Simulates prismatic dispersion of
                                           light refracted through stacked oil
                                           glaze layers at lit/shadow transitions
                                           -- iridescent micro-halo of aged
                                           Renaissance panel paintings.

Warm-start base: mona_lisa_s155.png
Applies: s155 accumulated base + s156 (Gentile da Fabriano gold tooling -- NEW)
                                   + s156 (Chromatic fringe -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S155_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s155.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s155.png"),
    "C:/Source/painting-pipeline/mona_lisa_s155.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s154.png"),
    "C:/Source/painting-pipeline/mona_lisa_s154.png",
]

base_path = None
for c in S155_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S155_CANDIDATES)
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
    print("Session 156 warm-start from accumulated canvas", flush=True)
    print("Applying: Gentile da Fabriano gold tooling (156 -- NEW)", flush=True)
    print("Applying: Chromatic fringe pass (156 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 156 (NEW): Gentile da Fabriano gold tooling pass -------------
    # Thirty-eighth distinct mode: LUMINANCE-RIDGE WARM GOLD SHIMMER TINTING.
    #
    # The Mona Lisa's sfumato surfaces carry thousands of micro-ridges in the
    # glazed flesh zones — orbital bone, nasal bridge, cheekbone, knuckle —
    # where the light catches raised paint edges.  This pass adds the warm
    # gold shimmer of tooled gold-ground halos to those same lit ridges,
    # deepening the jewel-like luminous quality of the portrait's face zone.
    #
    # hi_lo=0.60, hi_hi=0.95: active on the upper mid-tone and highlight zone;
    #   suppressed in shadow (where no gold catchlight exists) and in the
    #   full specular clip (which already reads as bright).
    # gold_r=0.050, gold_g=0.032: warm amber-gold tint — restrained to avoid
    #   a visible gold overlay effect; the goal is a subtle richening.
    # gold_b=0.015: blue reduction deepens gold chroma away from white-light
    #   neutral into warm gold territory.
    # ridge_strength=0.65: scale factor; slightly reduced from pass default
    #   to prevent over-warming the already richly glazed portrait.
    # opacity=0.22: light composite on the 40th accumulated layer.
    print("Gentile da Fabriano gold tooling pass (session 156 -- NEW)...", flush=True)
    p.gentile_da_fabriano_gold_tooling_pass(
        hi_lo          = 0.60,
        hi_hi          = 0.95,
        gold_r         = 0.050,
        gold_g         = 0.032,
        gold_b         = 0.015,
        ridge_strength = 0.65,
        opacity        = 0.22,
    )

    # -- Session 156 (NEW): Chromatic fringe pass -----------------------------
    # Thirty-ninth distinct mode: PRISMATIC EDGE CHROMATIC FRINGE.
    #
    # The Mona Lisa's sfumato edges — the hairline dissolving into the dark
    # ground, the shoulder line against the background, the subtle contour of
    # the gauze wrap — are the precise locations where multilayer oil glazing
    # creates prismatic iridescence.  This pass adds the warm fringe on the
    # lit side of each edge and the cool fringe on the shadow side, simulating
    # the spectral dispersion visible in aged Renaissance panel paintings.
    #
    # edge_lo=0.10, edge_hi=0.78: edge gate excludes noise (< 0.10) and fully
    #   saturated specular transitions (> 0.78); active on real structural edges.
    # fringe_warm_r=0.035, fringe_warm_g=0.014: gentle warm tint on lit side;
    #   restrained to keep the sfumato quality — the fringe should not harden
    #   the portrait's deliberately soft edges.
    # fringe_cool_b=0.030, fringe_cool_r=0.012: gentle cool-violet on shadow
    #   side; reinforces the warm/cool edge transition without creating a
    #   visible halo.
    # opacity=0.15: very gentle composite on the 41st accumulated layer.
    print("Chromatic fringe pass (session 156 artistic improvement -- NEW)...", flush=True)
    p.chromatic_fringe_pass(
        edge_lo        = 0.10,
        edge_hi        = 0.78,
        fringe_warm_r  = 0.035,
        fringe_warm_g  = 0.014,
        fringe_cool_b  = 0.030,
        fringe_cool_r  = 0.012,
        opacity        = 0.15,
    )

    # -- Carry-forward passes from session 155 --------------------------------

    # Melozzo zenith radiance (from s155 -- carry forward)
    print("Melozzo zenith radiance pass (session 155 carry-forward)...", flush=True)
    p.melozzo_zenith_radiance_pass(
        mid_lo          = 0.28,
        mid_hi          = 0.75,
        warm_r          = 0.026,
        warm_g          = 0.013,
        cool_b          = 0.022,
        cool_r          = 0.011,
        zenith_strength = 0.52,
        opacity         = 0.20,
    )

    # Warm ambient occlusion (from s155 -- carry forward)
    print("Warm ambient occlusion pass (session 155 carry-forward)...", flush=True)
    p.warm_ambient_occlusion_pass(
        occ_radius = 10.0,
        occ_max    = 0.25,
        shad_lo    = 0.10,
        shad_hi    = 0.42,
        warm_r     = 0.030,
        warm_g     = 0.016,
        opacity    = 0.16,
    )

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
        opacity       = 0.18,
    )

    # Iridescent glaze (from s154 -- carry forward)
    print("Iridescent glaze pass (session 154 carry-forward)...", flush=True)
    p.iridescent_glaze_pass(
        mid_lo           = 0.30,
        mid_hi           = 0.73,
        warm_r           = 0.024,
        warm_g           = 0.011,
        cool_b           = 0.020,
        cool_r           = 0.011,
        shimmer_strength = 0.40,
        opacity          = 0.12,
    )

    # Furini moonlit sfumato (from s153 -- carry forward)
    print("Furini moonlit sfumato pass (session 153 carry-forward)...", flush=True)
    p.furini_moonlit_sfumato_pass(
        hi_lo          = 0.55,
        hi_hi          = 0.90,
        cool_b         = 0.020,
        cool_r         = 0.011,
        cool_g         = 0.005,
        cool_strength  = 0.48,
        opacity        = 0.18,
    )

    # Translucent fabric (from s153 -- carry forward)
    print("Translucent fabric pass (session 153 carry-forward)...", flush=True)
    p.translucent_fabric_pass(
        fab_lo         = 0.32,
        fab_hi         = 0.70,
        fabric_r       = 0.10,
        fabric_g       = 0.14,
        fabric_b       = 0.11,
        fabric_opacity = 0.09,
        edge_factor    = 0.42,
        opacity        = 0.14,
    )

    # Gaudenzio warm devotion (from s152 -- carry forward)
    print("Gaudenzio warm devotion pass (session 152 carry-forward)...", flush=True)
    p.gaudenzio_warm_devotion_pass(
        shad_lo        = 0.05,
        shad_hi        = 0.40,
        warm_r         = 0.026,
        warm_g         = 0.015,
        warm_b         = 0.006,
        warm_strength  = 0.46,
        opacity        = 0.18,
    )

    # Atmospheric depth gradient (from s152 -- carry forward)
    print("Atmospheric depth gradient pass (session 152 carry-forward)...", flush=True)
    p.atmospheric_depth_gradient_pass(
        atm_warm_r   = 0.016,
        atm_warm_g   = 0.009,
        atm_cool_b   = 0.018,
        atm_cool_r   = 0.008,
        luma_lo      = 0.12,
        opacity      = 0.18,
    )

    # Ter Brugghen raking amber (from s151 -- carry forward)
    print("Ter Brugghen raking amber pass (session 151 carry-forward)...", flush=True)
    p.ter_brugghen_raking_amber_pass(
        mid_lo         = 0.24,
        mid_hi         = 0.74,
        warm_r         = 0.032,
        warm_g         = 0.015,
        cool_b         = 0.024,
        cool_r         = 0.011,
        ridge_strength = 0.48,
        opacity        = 0.16,
    )

    # Adaptive local contrast (from s151 -- carry forward)
    print("Adaptive local contrast pass (session 151 carry-forward)...", flush=True)
    p.adaptive_local_contrast_pass(
        block_size     = 80,
        p_lo           = 0.06,
        p_hi           = 0.94,
        contrast_lo    = 0.22,
        contrast_hi    = 0.78,
        stretch_amount = 0.24,
        opacity        = 0.12,
    )

    # Beccafumi nacreous glow (from s150 -- carry forward)
    print("Beccafumi nacreous glow pass (session 150 carry-forward)...", flush=True)
    p.beccafumi_nacreous_glow_pass(
        sigma_bloom   = 3.5,
        glow_lo       = 0.30,
        glow_hi       = 0.75,
        glow_warm_r   = 0.036,
        glow_warm_g   = 0.020,
        glow_cool_b   = 0.026,
        glow_cool_r   = 0.012,
        glow_strength = 0.46,
        opacity       = 0.20,
    )

    # Penumbra softening (from s150 -- carry forward)
    print("Penumbra softening pass (session 150 carry-forward)...", flush=True)
    p.penumbra_softening_pass(
        pen_lo        = 0.20,
        pen_hi        = 0.50,
        pen_sigma     = 1.8,
        soften_amount = 0.36,
        opacity       = 0.18,
    )

    # Romanino Brescian impasto (from s149 -- carry forward)
    print("Romanino Brescian impasto pass (session 149 carry-forward)...", flush=True)
    p.romanino_brescian_impasto_pass(
        sigma          = 1.2,
        relief_scale   = 13.0,
        impasto_warm_r = 0.038,
        impasto_warm_g = 0.019,
        shadow_b       = 0.023,
        shadow_r       = 0.010,
        opacity        = 0.18,
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
        opacity         = 0.12,
    )

    # Bordone parabolic warmth (from s148 -- carry forward)
    print("Bordone parabolic midtone warmth pass (session 148 carry-forward)...", flush=True)
    p.bordone_venetian_warmth_pass(
        deepen_amount = 0.05,
        warm_r        = 0.011,
        warm_g        = 0.006,
        opacity       = 0.12,
    )

    # Luminous ground (from s148 -- carry forward)
    print("Luminous ground imprimatura pass (session 148 carry-forward)...", flush=True)
    p.luminous_ground_pass(
        ground_r      = 0.48,
        ground_g      = 0.35,
        ground_b      = 0.20,
        ground_hi     = 0.32,
        ground_amount = 0.09,
        gamma_ground  = 2.0,
        opacity       = 0.12,
    )

    # Sodoma Sienese dreamveil (from s147 -- carry forward)
    print("Sodoma Sienese dreamveil pass (session 147 carry-forward)...", flush=True)
    p.sodoma_sienese_dreamveil_pass(
        warm_lo      = 0.38,
        warm_hi      = 0.72,
        warm_r       = 0.012,
        warm_g       = 0.006,
        sat_lo       = 0.48,
        sat_hi       = 0.78,
        sat_lift     = 0.030,
        veil_sigma   = 2.2,
        veil_amount  = 0.040,
        sky_lo       = 0.82,
        sky_b        = 0.009,
        opacity      = 0.10,
    )

    # Specular clarity (from s147 -- carry forward)
    print("Specular clarity pass (session 147 carry-forward)...", flush=True)
    p.specular_clarity_pass(
        clarity_lo   = 0.72,
        sigma        = 1.0,
        usm_amount   = 0.08,
        cool_lo      = 0.85,
        cool_b       = 0.008,
        cool_r       = 0.006,
        opacity      = 0.10,
    )

    # Gossaert pearl-crystalline (from s146 -- carry forward)
    print("Gossaert pearl-crystalline pass (session 146 carry-forward)...", flush=True)
    p.gossaert_pearl_crystalline_pass(
        shadow_hi       = 0.36,
        highlight_lo    = 0.70,
        pearl_cool_b    = 0.022,
        pearl_desat     = 0.06,
        shadow_warm_r   = 0.014,
        shadow_warm_b   = 0.011,
        mid_sat_boost   = 0.026,
        crystal_sigma   = 2.0,
        crystal_amount  = 0.04,
        opacity         = 0.10,
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
        shadow_tint     = 0.018,
        penumbra_chroma = 0.036,
        opacity         = 0.09,
    )

    # Cambiaso geometric planes (from s145 -- carry forward)
    print("Cambiaso geometric planes pass (session 145 carry-forward)...", flush=True)
    p.cambiaso_geometric_planes_pass(
        sigma_coarse   = 22.0,
        sigma_medium   = 5.0,
        flatten_amount = 0.36,
        edge_boost     = 0.13,
        sigma_edge     = 2.0,
        terra_r        = 0.68,
        terra_g        = 0.45,
        terra_b        = 0.18,
        terra_lo       = 0.08,
        terra_hi       = 0.38,
        terra_amount   = 0.032,
        opacity        = 0.05,
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
        cool_amount   = 0.022,
        sat_dampen    = 0.04,
        opacity       = 0.06,
    )

    # Magnasco nervous brilliance (from s143 -- carry forward)
    print("Magnasco nervous brilliance pass (session 143 carry-forward)...", flush=True)
    p.magnasco_nervous_brilliance_pass(
        hf_sigma      = 3.0,
        scatter_px    = 2,
        bright_thresh = 0.04,
        dark_gate_lo  = 0.08,
        dark_gate_hi  = 0.55,
        warm_tint     = 0.030,
        opacity       = 0.05,
    )

    # Focal vignette (from s142 -- carry forward)
    print("Focal vignette pass (session 142 carry-forward)...", flush=True)
    p.focal_vignette_pass(
        focal_x           = 0.50,
        focal_y           = 0.35,
        vignette_strength = 0.22,
        vignette_power    = 2.2,
        cool_shift        = 0.013,
        opacity           = 0.18,
    )

    # Glazing depth pass (from session 141 -- carry forward)
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.052,
        warm_g      = 0.017,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.05,
    )

    # Velatura: warm amber unifying glaze (carry forward)
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.024)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.46, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s156.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
