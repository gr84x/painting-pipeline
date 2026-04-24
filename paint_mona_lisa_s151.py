"""
paint_mona_lisa_s151.py -- Session 151 portrait painting.

Warm-start from mona_lisa_s150.png (latest accumulated canvas),
then applies session 151 additions.

Session 151 additions:
  - ter_brugghen                        -- NEW (session 151)
                                           Hendrick ter Brugghen (1588–1629),
                                           Utrecht Caravaggism.
                                           Dutch master of warm raking sidelight —
                                           amber light catching every elevated
                                           surface ridge (nose bridge, cheekbone,
                                           finger knuckle, collar fold) while
                                           cool blue-grey infills the receding
                                           shadow faces of those same forms.
                                           Studied Caravaggio in Rome 1604–1614;
                                           brought tenebrism north with a warmer,
                                           more lyrical Dutch sensibility.

  SESSION 151 MAIN PASS -- ter_brugghen_raking_amber_pass:

                                           Thirty-first distinct mode:
                                           DIRECTIONAL HORIZONTAL SOBEL
                                           WARM-LIGHT RIDGE TINTING WITH
                                           COOL-SHADOW INFILL.

                                           Computes luminance, applies horizontal
                                           Sobel (scipy axis=1) to detect the
                                           left-to-right luminance gradient.
                                           Positive sobel → lit ridge face →
                                           warm amber tint (R+warm_r, G+warm_g).
                                           Negative sobel → shadow side of ridge →
                                           cool blue-grey tint (B+cool_b, R−cool_r).
                                           Gated to midtone zone [mid_lo=0.22,
                                           mid_hi=0.76] to confine the effect to
                                           form-bearing figure surfaces.

  SESSION 151 ARTISTIC IMPROVEMENT -- adaptive_local_contrast_pass:

                                           LOCAL-BLOCK PERCENTILE CONTRAST
                                           STRETCHING.

                                           Divides the image into overlapping
                                           local blocks (block_size=64).  For
                                           each block computes 5th and 95th
                                           percentile of each RGB channel.
                                           Interpolates percentile grids to
                                           full resolution (scipy.ndimage.zoom
                                           order=1).  Stretches each channel
                                           so the local [p5, p95] maps to [0, 1],
                                           gated to the midtone zone
                                           [contrast_lo=0.20, contrast_hi=0.80].
                                           Builds local form contrast in the
                                           manner of Renaissance painters who
                                           exaggerated modelling within individual
                                           form regions for distance readability.

Warm-start base: mona_lisa_s150.png
Applies: s150 accumulated base + s151 (ter Brugghen raking amber -- NEW)
                                  + s151 (Adaptive local contrast -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S150_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s150.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s150.png"),
    "C:/Source/painting-pipeline/mona_lisa_s150.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s149.png"),
    "C:/Source/painting-pipeline/mona_lisa_s149.png",
]

base_path = None
for c in S150_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S150_CANDIDATES)
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
    print("Session 151 warm-start from accumulated canvas", flush=True)
    print("Applying: Ter Brugghen raking amber sidelight (151 -- NEW)", flush=True)
    print("Applying: Adaptive local contrast stretching (151 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 151 (NEW): Ter Brugghen raking amber pass --------------------
    # Thirty-first distinct mode: DIRECTIONAL HORIZONTAL SOBEL WARM-LIGHT
    # RIDGE TINTING WITH COOL-SHADOW INFILL.
    #
    # Design intent for the accumulated canvas after 31 prior passes:
    #
    # The canvas has extraordinary sfumato depth, warm Venetian color, nacreous
    # iridescence (Beccafumi), and penumbra softening.  What it can still gain
    # from ter Brugghen is DIRECTIONAL FORM ARTICULATION: the raking sidelight
    # that makes every elevated surface catch amber warmth while every receding
    # face drops into cool blue-grey.  The horizontal Sobel encodes exactly this
    # directional preference — it finds the left-to-right luminance gradient and
    # maps positive gradient → lit amber ridge, negative → cool shadow infill.
    # This is the Utrecht Caravaggist contribution: making form readable through
    # directional warm/cool local contrast rather than global tonal hierarchy.
    #
    # mid_lo=0.24, mid_hi=0.74: target figure flesh/drapery midtones — avoids
    #   deep shadow voids and specular highlight peaks.
    # warm_r=0.038, warm_g=0.018: gentle warm amber on lit ridges — complements
    #   the existing Venetian warmth without over-yellowing.
    # cool_b=0.030, cool_r=0.014: gentle cool blue-grey on shadow sides —
    #   a quiet Utrecht Caravaggist shadow temperature shift.
    # ridge_strength=0.55: moderate on the rich accumulated canvas.
    # opacity=0.22: subtle directional pass — it is seventh-layer refinement.
    print("Ter Brugghen raking amber pass (session 151 -- NEW)...", flush=True)
    p.ter_brugghen_raking_amber_pass(
        mid_lo         = 0.24,
        mid_hi         = 0.74,
        warm_r         = 0.038,
        warm_g         = 0.018,
        cool_b         = 0.030,
        cool_r         = 0.014,
        ridge_strength = 0.55,
        opacity        = 0.22,
    )

    # -- Session 151 (NEW): Adaptive local contrast pass ----------------------
    # Artistic improvement: LOCAL-BLOCK PERCENTILE CONTRAST STRETCHING.
    #
    # Design intent:
    # The accumulated canvas has subtle tonal depth but the fine form modelling
    # within individual features — the curve of a cheek, the bridge of the nose,
    # the drape of fabric folds — can benefit from a local contrast lift that
    # makes these details read more clearly without disturbing the global sfumato
    # tonal design.  The local-block approach targets each region independently
    # so that the modelling within each face zone is stretched toward its own
    # local dynamic range, exactly as Renaissance painters exaggerated local
    # contrast for distant viewability.
    #
    # block_size=80: block covers roughly one facial feature (nose, eye, cheek)
    #   at the accumulated canvas resolution — captures local form scale.
    # p_lo=0.06, p_hi=0.94: 6th and 94th percentile — robust to outliers.
    # contrast_lo=0.22, contrast_hi=0.78: midtone zone gate — avoids deep
    #   shadows (already well-modelled) and specular highlights (already clear).
    # stretch_amount=0.28: gentle stretch — preserves the sfumato quality.
    # opacity=0.18: subtle finishing pass.
    print("Adaptive local contrast pass (session 151 artistic improvement -- NEW)...", flush=True)
    p.adaptive_local_contrast_pass(
        block_size     = 80,
        p_lo           = 0.06,
        p_hi           = 0.94,
        contrast_lo    = 0.22,
        contrast_hi    = 0.78,
        stretch_amount = 0.28,
        opacity        = 0.18,
    )

    # -- Carry-forward passes from session 150 --------------------------------

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
        opacity       = 0.28,
    )

    # Penumbra softening (from s150 -- carry forward)
    print("Penumbra softening pass (session 150 carry-forward)...", flush=True)
    p.penumbra_softening_pass(
        pen_lo        = 0.20,
        pen_hi        = 0.50,
        pen_sigma     = 1.8,
        soften_amount = 0.40,
        opacity       = 0.25,
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
        opacity        = 0.25,
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
        opacity         = 0.18,
    )

    # Bordone parabolic warmth (from s148 -- carry forward)
    print("Bordone parabolic midtone warmth pass (session 148 carry-forward)...", flush=True)
    p.bordone_venetian_warmth_pass(
        deepen_amount = 0.06,
        warm_r        = 0.014,
        warm_g        = 0.008,
        opacity       = 0.18,
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
        opacity       = 0.18,
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
        opacity      = 0.16,
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
        opacity      = 0.15,
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
        opacity         = 0.16,
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
        opacity         = 0.13,
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
        opacity        = 0.08,
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
        opacity       = 0.09,
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
        opacity       = 0.08,
    )

    # Focal vignette (from s142 -- carry forward)
    print("Focal vignette pass (session 142 carry-forward)...", flush=True)
    p.focal_vignette_pass(
        focal_x           = 0.50,
        focal_y           = 0.35,
        vignette_strength = 0.22,
        vignette_power    = 2.2,
        cool_shift        = 0.015,
        opacity           = 0.25,
    )

    # Glazing depth pass (from session 141 -- carry forward)
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.060,
        warm_g      = 0.020,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.08,
    )

    # Velatura: warm amber unifying glaze (carry forward)
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.030)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.48, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s151.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
