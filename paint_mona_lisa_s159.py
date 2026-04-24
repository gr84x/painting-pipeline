"""
paint_mona_lisa_s159.py -- Session 159 portrait painting.

Warm-start from mona_lisa_s158.png (accumulated canvas),
then applies session 159 additions.

Session 159 additions:
  - antonio_moro                          -- NEW (session 159)
                                           Antonio Moro (Anthonis Mor van Dashorst,
                                           c. 1519–c. 1575), Flemish-Spanish Court
                                           Renaissance.  Supreme court portraitist
                                           of Philip II of Spain, Mary Tudor, and
                                           the Habsburg aristocracy.  Trained under
                                           Jan van Scorel; brought to Spain under
                                           Cardinal Granvelle's patronage.
                                           Technical signature: HIGH-POLARITY TONAL
                                           CONTRAST — very dark umber grounds with
                                           very precise cool-silver highlights;
                                           extraordinary rendering of black velvet
                                           and silver metalwork; Flemish precision
                                           contour with Spanish court gravity.

  SESSION 159 MAIN PASS -- moro_regal_presence_pass:

                                           FORTY-FOURTH DISTINCT MODE:
                                           HIGH-POLARITY TONAL AMPLIFICATION —
                                           COURT PORTRAIT GRAVITY.

                                           (A) Shadow deepening gate [0, shadow_hi]:
                                           shadow_gate = clip((shadow_hi-luma)
                                           /shadow_hi, 0,1)^shadow_power;
                                           out_c = c*(1-shadow_deepen*shadow_gate).
                                           Darkens shadows toward near-black,
                                           amplifying the Flemish dark-ground
                                           convention.

                                           (B) Highlight crystallisation gate
                                           [highlight_lo, 1.0]:
                                           hi_gate = clip((luma-highlight_lo)
                                           /(1-highlight_lo),0,1)^highlight_power;
                                           B+silver_b*hi_gate; R-silver_r*hi_gate.
                                           Adds cool-silver to the brightest pixels
                                           as a monotonically increasing ramp (not
                                           a bump gate like Greuze or Furini).

                                           Composite at opacity=0.28.

  SESSION 159 ARTISTIC IMPROVEMENT -- skin_subsurface_scatter_pass:

                                           FORTY-FIFTH DISTINCT MODE:
                                           SKIN SUBSURFACE LIGHT SCATTERING —
                                           WARM-RED TRANSLUCENCY GLOW.

                                           Skin detection: (r>0.40) AND (r>g)
                                           AND (g>b) AND (r-b>0.10).
                                           Gaussian blur skin mask (sigma=10).
                                           Large-sigma Gaussian scatter spread
                                           (sigma=5.0) over full image.
                                           Warm-tint scattered: R*warm_boost,
                                           B*cool_damp.
                                           Blend: orig*(1-skin_mask*strength)
                                           + warm_spread*(skin_mask*strength).
                                           Composite at opacity=0.25.

Warm-start base: mona_lisa_s158.png
Applies: s158 accumulated base + s159 (Moro regal presence -- NEW)
                                   + s159 (Skin subsurface scatter -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S158_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s158.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s158.png"),
    "C:/Source/painting-pipeline/mona_lisa_s158.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s157.png"),
    "C:/Source/painting-pipeline/mona_lisa_s157.png",
]

base_path = None
for c in S158_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S158_CANDIDATES)
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
    print("Session 159 warm-start from accumulated canvas", flush=True)
    print("Applying: Moro regal presence (159 -- NEW)", flush=True)
    print("Applying: Skin subsurface scatter pass (159 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 159 (NEW): Moro regal presence pass --------------------------
    # Forty-fourth distinct mode: HIGH-POLARITY TONAL AMPLIFICATION.
    #
    # Antonio Moro's court portraits achieve their extraordinary gravity through
    # a deliberate high-polarity tonal system: near-black shadows (the dark umber
    # ground showing through the paint film) and precisely calibrated cool-silver
    # highlights.  Applied to the Mona Lisa, this pass deepens the shadow passages
    # — the fold of the veil, the shadow beneath the chin, the distant landscape
    # darks — while adding a cool crystalline quality to the brightest highlight
    # points: the specular on the brow, the highlights in the eyes.  The combined
    # effect is a subtle intensification of the overall tonal polarity, giving the
    # portrait the authoritative court gravity that Moro brought from Flanders to
    # the Spanish Habsburg court.
    #
    # shadow_hi=0.35: deepens shadows below luma 0.35 — the shadow passages of
    #   the Mona Lisa's face (eye sockets, under-chin shadow) and the darkest
    #   landscape elements are the primary targets.
    # shadow_power=1.6: slightly supra-linear — concentrates deepening at the very
    #   darkest pixels while leaving mid-tones largely unaffected.
    # shadow_deepen=0.14: moderate deepening — enough to add gravity without
    #   crushing the subtle shadow modelling that Leonardo built through sfumato.
    # highlight_lo=0.72: crystallises highlights above luma 0.72 — the bright
    #   specular points on the forehead and hands are the primary targets.
    # highlight_power=1.8: concentrates crystallisation at the very brightest points.
    # silver_b=0.016, silver_r=0.007: very restrained cool-silver — a whisper of
    #   Northern light on the peak specular, not a dramatic colour shift.
    # opacity=0.28: moderate composite on the 46th accumulated layer.
    print("Moro regal presence pass (session 159 -- NEW)...", flush=True)
    p.moro_regal_presence_pass(
        shadow_hi      = 0.35,
        shadow_power   = 1.6,
        shadow_deepen  = 0.14,
        highlight_lo   = 0.72,
        highlight_power= 1.8,
        silver_b       = 0.016,
        silver_r       = 0.007,
        opacity        = 0.28,
    )

    # -- Session 159 (NEW): Skin subsurface scatter pass ----------------------
    # Forty-fifth distinct mode: SKIN SUBSURFACE LIGHT SCATTERING.
    #
    # The Mona Lisa's flesh — the smooth brow, the lit cheekbone, the hands
    # folded in the lower third — has a quality of inner illumination that
    # distinguishes it from any painted surface that is merely reflecting light.
    # This quality, achieved by Leonardo through successive thin glazes over a warm
    # ground, is precisely the optical effect of subsurface scattering: light
    # entering the skin, dispersing within the vascularised dermis, and emerging
    # slightly reddened and softened.  This pass applies that principle to the
    # accumulated canvas: detecting warm flesh pixels, spreading the light
    # information spatially (simulating dermis dispersion), warming the spread
    # component (simulating spectral reddening), and blending it back at low
    # opacity to add the luminous inner warmth that Leonardo's glazes achieved.
    #
    # scatter_sigma=4.5: moderate spread — simulates ~4-5mm dermis penetration
    #   at 780px canvas width (each pixel roughly 0.5mm at A4 print scale).
    # scatter_strength=0.18: restrained blend — the effect should read as a
    #   subtle enhancement of the flesh's inner warmth, not a visible blur.
    # warm_boost=1.03: very gentle R lift — the spectral reddening in real
    #   subsurface scatter is subtle; this pass models it at low amplitude.
    # cool_damp=0.98: minimal B reduction — just enough to shift the scattered
    #   component very slightly toward warm-red without creating an obvious tint.
    # mask_sigma=12.0: wide mask sigma — ensures smooth flesh region boundaries
    #   so the scatter effect fades gradually into non-flesh areas.
    # opacity=0.25: light composite on the 47th accumulated layer.
    print("Skin subsurface scatter pass (session 159 artistic improvement -- NEW)...", flush=True)
    p.skin_subsurface_scatter_pass(
        scatter_sigma   = 4.5,
        scatter_strength= 0.18,
        warm_boost      = 1.03,
        cool_damp       = 0.98,
        mask_sigma      = 12.0,
        opacity         = 0.25,
    )

    # -- Carry-forward passes from session 158 --------------------------------

    # Greuze sentimental carnation (from s158 -- carry forward)
    print("Greuze sentimental carnation pass (session 158 carry-forward)...", flush=True)
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
        opacity = 0.22,
    )

    # Edge sfumato dissolution (from s158 -- carry forward)
    print("Edge sfumato dissolution pass (session 158 carry-forward)...", flush=True)
    p.edge_sfumato_dissolution_pass(
        grad_threshold = 0.08,
        edge_power     = 1.8,
        edge_strength  = 0.62,
        blur_sigma     = 2.2,
        opacity        = 0.28,
    )

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
        opacity  = 0.18,
    )

    # Peripheral defocus (from s157 -- carry forward)
    print("Peripheral defocus pass (session 157 carry-forward)...", flush=True)
    p.peripheral_defocus_pass(
        inner_radius  = 0.42,
        blur_sigma    = 3.5,
        power         = 2.0,
        blur_strength = 0.50,
        opacity       = 0.22,
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
        opacity        = 0.10,
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
        opacity        = 0.07,
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
        opacity         = 0.10,
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
        opacity    = 0.09,
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
        opacity       = 0.09,
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
        opacity          = 0.06,
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
        opacity        = 0.09,
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
        opacity        = 0.07,
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
        opacity        = 0.09,
    )

    # Atmospheric depth gradient (from s152 -- carry forward)
    print("Atmospheric depth gradient pass (session 152 carry-forward)...", flush=True)
    p.atmospheric_depth_gradient_pass(
        atm_warm_r   = 0.009,
        atm_warm_g   = 0.005,
        atm_cool_b   = 0.010,
        atm_cool_r   = 0.004,
        luma_lo      = 0.12,
        opacity      = 0.09,
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
        opacity        = 0.08,
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
        opacity        = 0.06,
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
        opacity       = 0.10,
    )

    # Penumbra softening (from s150 -- carry forward)
    print("Penumbra softening pass (session 150 carry-forward)...", flush=True)
    p.penumbra_softening_pass(
        pen_lo        = 0.20,
        pen_hi        = 0.50,
        pen_sigma     = 1.8,
        soften_amount = 0.22,
        opacity       = 0.09,
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
        opacity        = 0.09,
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
        opacity         = 0.06,
    )

    # Bordone parabolic warmth (from s148 -- carry forward)
    print("Bordone parabolic midtone warmth pass (session 148 carry-forward)...", flush=True)
    p.bordone_venetian_warmth_pass(
        deepen_amount = 0.03,
        warm_r        = 0.006,
        warm_g        = 0.003,
        opacity       = 0.06,
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
        opacity       = 0.06,
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
        opacity      = 0.05,
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
        opacity      = 0.05,
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
        opacity         = 0.05,
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
        opacity         = 0.05,
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
        opacity           = 0.10,
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
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.015)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.44, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s159.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
