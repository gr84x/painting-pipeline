"""
paint_mona_lisa_s157.py -- Session 157 portrait painting.

Warm-start from mona_lisa_s156.png (Gentile da Fabriano accumulated canvas),
then applies session 157 additions.

Session 157 additions:
  - giampietrino                         -- NEW (session 157)
                                           Giampietrino (Giovanni Pietro
                                           Rizzoli, c. 1495–1540),
                                           Milanese Leonardesque.
                                           Direct pupil of Leonardo da Vinci
                                           in Milan; the most faithful studio
                                           transmitter of Leonardo's multi-
                                           layer oil-glazing method.
                                           Characteristic: warm honey-amber
                                           flesh highlights + cool violet-
                                           plum shadow resonance — the
                                           DUAL-TEMPERATURE FLESH MODEL.

  SESSION 157 MAIN PASS -- giampietrino_warm_devotion_pass:

                                           FORTIETH DISTINCT MODE:
                                           DUAL-ZONE LUMINANCE TINTING —
                                           WARM HIGHLIGHT AMBER + COOL
                                           SHADOW VIOLET.

                                           Highlight gate [0.55, 0.88]:
                                           R+warm_r=0.055, G+warm_g=0.030
                                           — warm honey-amber lift on lit
                                           flesh zones.  Shadow gate
                                           [0.05, 0.42]: B+cool_b=0.055,
                                           R-cool_r=0.022 — cool violet
                                           deepening in shadow recesses.
                                           Composite at opacity=0.30.

  SESSION 157 ARTISTIC IMPROVEMENT -- peripheral_defocus_pass:

                                           FORTY-FIRST DISTINCT MODE:
                                           RADIAL PERIPHERAL SOFTENING —
                                           SIMULATED DEPTH OF FIELD.

                                           Radial distance from canvas
                                           centre → defocus_wt map
                                           (inner_radius=0.38, power=1.8,
                                           blur_strength=0.55).  Full-
                                           canvas Gaussian blur sigma=4.0.
                                           Blend: out = orig*(1-wt) +
                                           blurred*wt.  Composite at
                                           opacity=0.40.  Distinct from
                                           focal_vignette_pass (that
                                           DARKENS; this BLURS).

Warm-start base: mona_lisa_s156.png
Applies: s156 accumulated base + s157 (Giampietrino warm devotion -- NEW)
                                   + s157 (Peripheral defocus -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S156_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s156.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s156.png"),
    "C:/Source/painting-pipeline/mona_lisa_s156.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s155.png"),
    "C:/Source/painting-pipeline/mona_lisa_s155.png",
]

base_path = None
for c in S156_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S156_CANDIDATES)
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
    print("Session 157 warm-start from accumulated canvas", flush=True)
    print("Applying: Giampietrino warm devotion (157 -- NEW)", flush=True)
    print("Applying: Peripheral defocus pass (157 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 157 (NEW): Giampietrino warm devotion pass -------------------
    # Fortieth distinct mode: DUAL-ZONE LUMINANCE TINTING.
    #
    # The Mona Lisa's flesh tones live in the upper mid-tone range [0.55-0.88]
    # — the warm ivory brow, the lit cheek, the warm knuckle surface.  The
    # shadow recesses — under the chin, the orbital socket, the neck below
    # the gauze wrap — fall in [0.05-0.42].  This pass simultaneously warms
    # the highlight zone with a honey-amber push and deepens the shadow zone
    # with a cool violet resonance, exactly replicating Giampietrino's
    # dual-temperature flesh model.
    #
    # hi_lo=0.56, hi_hi=0.86: tightly centred on the upper flesh mid-tone;
    #   avoids clipping into full highlights (already white) or cool mid-tones.
    # warm_r=0.040, warm_g=0.022: restrained warm amber — enough to enrich
    #   the flesh highlights without visibly shifting the white balance.
    # shad_lo=0.06, shad_hi=0.40: shadow gate; centred on the deep warm
    #   umber zone of the Mona Lisa's background and shadow flesh.
    # cool_b=0.038, cool_r=0.016: gentle violet shadow resonance.
    # opacity=0.26: light composite on the 42nd accumulated layer.
    print("Giampietrino warm devotion pass (session 157 -- NEW)...", flush=True)
    p.giampietrino_warm_devotion_pass(
        hi_lo    = 0.56,
        hi_hi    = 0.86,
        warm_r   = 0.040,
        warm_g   = 0.022,
        shad_lo  = 0.06,
        shad_hi  = 0.40,
        cool_b   = 0.038,
        cool_r   = 0.016,
        opacity  = 0.26,
    )

    # -- Session 157 (NEW): Peripheral defocus pass ---------------------------
    # Forty-first distinct mode: RADIAL PERIPHERAL SOFTENING.
    #
    # The Mona Lisa is the supreme portrait of the concentrated gaze: the face
    # and hands emerge from an atmospheric haze that softens everything beyond
    # the central figure.  This pass applies a radial spatial blur that
    # increases toward the canvas perimeter, sharpening the contrast between
    # the well-focused central figure zone and the softly dissolved background
    # landscape and shadow areas.  This is the opposite of vignetting — it
    # preserves luminance at the edges while introducing spatial dissolution.
    #
    # inner_radius=0.42: the sharp zone extends ~42% of the corner distance,
    #   keeping the face, hands, and upper torso sharply resolved.
    # blur_sigma=3.5: moderate peripheral Gaussian sigma — enough to soften
    #   the landscape background detail without obliterating it.
    # power=2.0: slightly sharper transition from sharp to soft than the
    #   pass default (1.8) — concentrates attention on the figure.
    # blur_strength=0.50: at the corners, 50% blend toward blurred image.
    # opacity=0.35: moderate composite on the 43rd accumulated layer.
    print("Peripheral defocus pass (session 157 artistic improvement -- NEW)...", flush=True)
    p.peripheral_defocus_pass(
        inner_radius  = 0.42,
        blur_sigma    = 3.5,
        power         = 2.0,
        blur_strength = 0.50,
        opacity       = 0.35,
    )

    # -- Carry-forward passes from session 156 --------------------------------

    # Gentile da Fabriano gold tooling (from s156 -- carry forward)
    print("Gentile da Fabriano gold tooling pass (session 156 carry-forward)...", flush=True)
    p.gentile_da_fabriano_gold_tooling_pass(
        hi_lo          = 0.60,
        hi_hi          = 0.95,
        gold_r         = 0.036,
        gold_g         = 0.022,
        gold_b         = 0.010,
        ridge_strength = 0.55,
        opacity        = 0.16,
    )

    # Chromatic fringe (from s156 -- carry forward)
    print("Chromatic fringe pass (session 156 carry-forward)...", flush=True)
    p.chromatic_fringe_pass(
        edge_lo        = 0.10,
        edge_hi        = 0.78,
        fringe_warm_r  = 0.022,
        fringe_warm_g  = 0.009,
        fringe_cool_b  = 0.019,
        fringe_cool_r  = 0.008,
        opacity        = 0.10,
    )

    # Melozzo zenith radiance (from s155 -- carry forward)
    print("Melozzo zenith radiance pass (session 155 carry-forward)...", flush=True)
    p.melozzo_zenith_radiance_pass(
        mid_lo          = 0.28,
        mid_hi          = 0.75,
        warm_r          = 0.018,
        warm_g          = 0.009,
        cool_b          = 0.015,
        cool_r          = 0.007,
        zenith_strength = 0.45,
        opacity         = 0.14,
    )

    # Warm ambient occlusion (from s155 -- carry forward)
    print("Warm ambient occlusion pass (session 155 carry-forward)...", flush=True)
    p.warm_ambient_occlusion_pass(
        occ_radius = 10.0,
        occ_max    = 0.25,
        shad_lo    = 0.10,
        shad_hi    = 0.42,
        warm_r     = 0.022,
        warm_g     = 0.011,
        opacity    = 0.12,
    )

    # Bartolomeo Veneto jewel brocade (from s154 -- carry forward)
    print("Bartolomeo Veneto jewel brocade pass (session 154 carry-forward)...", flush=True)
    p.bartolomeo_veneto_jewel_brocade_pass(
        blue_lo       = 0.05,
        blue_hi       = 0.55,
        gold_lo       = 0.44,
        gold_hi       = 0.86,
        blue_deepen   = 0.08,
        gold_deepen   = 0.09,
        pole_strength = 0.48,
        opacity       = 0.14,
    )

    # Iridescent glaze (from s154 -- carry forward)
    print("Iridescent glaze pass (session 154 carry-forward)...", flush=True)
    p.iridescent_glaze_pass(
        mid_lo           = 0.30,
        mid_hi           = 0.73,
        warm_r           = 0.016,
        warm_g           = 0.008,
        cool_b           = 0.014,
        cool_r           = 0.007,
        shimmer_strength = 0.35,
        opacity          = 0.09,
    )

    # Furini moonlit sfumato (from s153 -- carry forward)
    print("Furini moonlit sfumato pass (session 153 carry-forward)...", flush=True)
    p.furini_moonlit_sfumato_pass(
        hi_lo          = 0.55,
        hi_hi          = 0.90,
        cool_b         = 0.014,
        cool_r         = 0.007,
        cool_g         = 0.003,
        cool_strength  = 0.40,
        opacity        = 0.13,
    )

    # Translucent fabric (from s153 -- carry forward)
    print("Translucent fabric pass (session 153 carry-forward)...", flush=True)
    p.translucent_fabric_pass(
        fab_lo         = 0.32,
        fab_hi         = 0.70,
        fabric_r       = 0.10,
        fabric_g       = 0.14,
        fabric_b       = 0.11,
        fabric_opacity = 0.07,
        edge_factor    = 0.42,
        opacity        = 0.10,
    )

    # Gaudenzio warm devotion (from s152 -- carry forward)
    print("Gaudenzio warm devotion pass (session 152 carry-forward)...", flush=True)
    p.gaudenzio_warm_devotion_pass(
        shad_lo        = 0.05,
        shad_hi        = 0.40,
        warm_r         = 0.018,
        warm_g         = 0.010,
        warm_b         = 0.004,
        warm_strength  = 0.38,
        opacity        = 0.13,
    )

    # Atmospheric depth gradient (from s152 -- carry forward)
    print("Atmospheric depth gradient pass (session 152 carry-forward)...", flush=True)
    p.atmospheric_depth_gradient_pass(
        atm_warm_r   = 0.011,
        atm_warm_g   = 0.006,
        atm_cool_b   = 0.012,
        atm_cool_r   = 0.005,
        luma_lo      = 0.12,
        opacity      = 0.13,
    )

    # Ter Brugghen raking amber (from s151 -- carry forward)
    print("Ter Brugghen raking amber pass (session 151 carry-forward)...", flush=True)
    p.ter_brugghen_raking_amber_pass(
        mid_lo         = 0.24,
        mid_hi         = 0.74,
        warm_r         = 0.022,
        warm_g         = 0.010,
        cool_b         = 0.016,
        cool_r         = 0.007,
        ridge_strength = 0.40,
        opacity        = 0.12,
    )

    # Adaptive local contrast (from s151 -- carry forward)
    print("Adaptive local contrast pass (session 151 carry-forward)...", flush=True)
    p.adaptive_local_contrast_pass(
        block_size     = 80,
        p_lo           = 0.06,
        p_hi           = 0.94,
        contrast_lo    = 0.22,
        contrast_hi    = 0.78,
        stretch_amount = 0.18,
        opacity        = 0.09,
    )

    # Beccafumi nacreous glow (from s150 -- carry forward)
    print("Beccafumi nacreous glow pass (session 150 carry-forward)...", flush=True)
    p.beccafumi_nacreous_glow_pass(
        sigma_bloom   = 3.5,
        glow_lo       = 0.30,
        glow_hi       = 0.75,
        glow_warm_r   = 0.026,
        glow_warm_g   = 0.014,
        glow_cool_b   = 0.019,
        glow_cool_r   = 0.009,
        glow_strength = 0.38,
        opacity       = 0.15,
    )

    # Penumbra softening (from s150 -- carry forward)
    print("Penumbra softening pass (session 150 carry-forward)...", flush=True)
    p.penumbra_softening_pass(
        pen_lo        = 0.20,
        pen_hi        = 0.50,
        pen_sigma     = 1.8,
        soften_amount = 0.28,
        opacity       = 0.13,
    )

    # Romanino Brescian impasto (from s149 -- carry forward)
    print("Romanino Brescian impasto pass (session 149 carry-forward)...", flush=True)
    p.romanino_brescian_impasto_pass(
        sigma          = 1.2,
        relief_scale   = 11.0,
        impasto_warm_r = 0.026,
        impasto_warm_g = 0.013,
        shadow_b       = 0.016,
        shadow_r       = 0.007,
        opacity        = 0.13,
    )

    # Highlight velatura (from s149 -- carry forward)
    print("Highlight velatura pass (session 149 carry-forward)...", flush=True)
    p.highlight_velatura_pass(
        vel_lo          = 0.60,
        vel_hi          = 0.90,
        glaze_r         = 0.88,
        glaze_g         = 0.70,
        glaze_b         = 0.32,
        vel_amount      = 0.05,
        contrast_amount = 0.03,
        sigma           = 0.8,
        opacity         = 0.09,
    )

    # Bordone parabolic warmth (from s148 -- carry forward)
    print("Bordone parabolic midtone warmth pass (session 148 carry-forward)...", flush=True)
    p.bordone_venetian_warmth_pass(
        deepen_amount = 0.04,
        warm_r        = 0.008,
        warm_g        = 0.004,
        opacity       = 0.09,
    )

    # Luminous ground (from s148 -- carry forward)
    print("Luminous ground imprimatura pass (session 148 carry-forward)...", flush=True)
    p.luminous_ground_pass(
        ground_r      = 0.48,
        ground_g      = 0.35,
        ground_b      = 0.20,
        ground_hi     = 0.32,
        ground_amount = 0.07,
        gamma_ground  = 2.0,
        opacity       = 0.09,
    )

    # Sodoma Sienese dreamveil (from s147 -- carry forward)
    print("Sodoma Sienese dreamveil pass (session 147 carry-forward)...", flush=True)
    p.sodoma_sienese_dreamveil_pass(
        warm_lo      = 0.38,
        warm_hi      = 0.72,
        warm_r       = 0.008,
        warm_g       = 0.004,
        sat_lo       = 0.48,
        sat_hi       = 0.78,
        sat_lift     = 0.022,
        veil_sigma   = 2.2,
        veil_amount  = 0.030,
        sky_lo       = 0.82,
        sky_b        = 0.006,
        opacity      = 0.08,
    )

    # Specular clarity (from s147 -- carry forward)
    print("Specular clarity pass (session 147 carry-forward)...", flush=True)
    p.specular_clarity_pass(
        clarity_lo   = 0.72,
        sigma        = 1.0,
        usm_amount   = 0.06,
        cool_lo      = 0.85,
        cool_b       = 0.006,
        cool_r       = 0.004,
        opacity      = 0.08,
    )

    # Gossaert pearl-crystalline (from s146 -- carry forward)
    print("Gossaert pearl-crystalline pass (session 146 carry-forward)...", flush=True)
    p.gossaert_pearl_crystalline_pass(
        shadow_hi       = 0.36,
        highlight_lo    = 0.70,
        pearl_cool_b    = 0.016,
        pearl_desat     = 0.04,
        shadow_warm_r   = 0.010,
        shadow_warm_b   = 0.008,
        mid_sat_boost   = 0.018,
        crystal_sigma   = 2.0,
        crystal_amount  = 0.03,
        opacity         = 0.08,
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
        shadow_tint     = 0.013,
        penumbra_chroma = 0.026,
        opacity         = 0.07,
    )

    # Cambiaso geometric planes (from s145 -- carry forward)
    print("Cambiaso geometric planes pass (session 145 carry-forward)...", flush=True)
    p.cambiaso_geometric_planes_pass(
        sigma_coarse   = 22.0,
        sigma_medium   = 5.0,
        flatten_amount = 0.28,
        edge_boost     = 0.10,
        sigma_edge     = 2.0,
        terra_r        = 0.68,
        terra_g        = 0.45,
        terra_b        = 0.18,
        terra_lo       = 0.08,
        terra_hi       = 0.38,
        terra_amount   = 0.022,
        opacity        = 0.04,
    )

    # Focal vignette (carry forward)
    print("Focal vignette pass (session 142 carry-forward)...", flush=True)
    p.focal_vignette_pass(
        focal_x           = 0.50,
        focal_y           = 0.35,
        vignette_strength = 0.18,
        vignette_power    = 2.2,
        cool_shift        = 0.010,
        opacity           = 0.14,
    )

    # Glazing depth pass (carry forward)
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.038,
        warm_g      = 0.012,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.04,
    )

    # Velatura: warm amber unifying glaze (carry forward)
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.020)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.44, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s157.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
