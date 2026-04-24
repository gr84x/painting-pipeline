"""
paint_mona_lisa_s151.py -- Session 151 portrait painting.

Warm-start from mona_lisa_s150.png (latest accumulated canvas),
then applies session 151 additions.

Session 151 additions:
  - gaudenzio_ferrari                   -- NEW (session 151)
                                           Gaudenzio Ferrari (c. 1477–1546),
                                           Piedmontese Devotional Luminism.
                                           Supreme master of warm inner light:
                                           his figures are lit from within by
                                           amber-gold devotional warmth that
                                           floods the shadow zone — where
                                           Leonardo leaves shadows cool and
                                           remote, Ferrari makes them glow.
                                           Lombard-Leonardesque synthesis of
                                           sfumato depth and vivid emotional
                                           directness.

  SESSION 151 MAIN PASS -- gaudenzio_warm_devotion_pass:

                                           Thirty-first distinct mode:
                                           SHADOW-ZONE WARM AMBER LUMINOSITY
                                           SCUMBLE.

                                           Computes luminance, defines shadow/
                                           penumbra gate (smooth bump in
                                           [shad_lo=0.05, shad_hi=0.42])
                                           targeting the transitional zone
                                           between shadow and mid-tone.
                                           Applies warm amber tint (R+, G+)
                                           with slight blue reduction (B−)
                                           weighted by gate × warm_strength.
                                           The effect is a gentle amber scumble
                                           in the shadows — not a highlight
                                           bloom, but Ferrari's characteristic
                                           devotional inner light made visible
                                           in the darkest passages.

  SESSION 151 ARTISTIC IMPROVEMENT -- atmospheric_depth_gradient_pass:

                                           LUMINANCE-WEIGHTED VERTICAL CHROMATIC
                                           TEMPERATURE GRADIENT.

                                           Applies Leonardo's atmospheric
                                           perspective across the full canvas
                                           height: warm ochre push strengthens
                                           at the lower canvas (foreground /
                                           figure base), cool blue-grey push
                                           strengthens at the upper canvas
                                           (sky / distant landscape horizon).
                                           Gated by luminance to exclude deep
                                           shadow voids.  Simulates the warm-
                                           to-cool depth recession visible in
                                           the Mona Lisa landscape background.

Warm-start base: mona_lisa_s150.png
Applies: s150 accumulated base + s151 (Gaudenzio warm devotion -- NEW)
                                  + s151 (Atmospheric depth gradient -- NEW)
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
    print("Applying: Gaudenzio warm devotion shadow glow (151 -- NEW)", flush=True)
    print("Applying: Atmospheric depth gradient (151 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 151 (NEW): Gaudenzio warm devotion pass ----------------------
    # Thirty-first distinct mode: SHADOW-ZONE WARM AMBER LUMINOSITY SCUMBLE.
    #
    # Design intent for the accumulated Leonardo/Venetian/Sienese canvas:
    #
    # After 31 prior passes the canvas has extraordinary tonal depth,
    # nacreous iridescence (Beccafumi), warm Venetian color, and physical
    # impasto texture.  The shadow zones, while deep and warm from
    # luminous_ground, can still benefit from Gaudenzio Ferrari's
    # distinctive treatment: a subtle amber scumble that makes the shadows
    # feel inhabited by inner devotional warmth rather than external
    # illumination.  This is distinct from highlight bloom (which targets
    # lit zones) and distinct from nacreous glow (which targets midtones
    # with a signed difference).
    #
    # shad_lo=0.05, shad_hi=0.40: shadow/penumbra gate — targets the
    #   transitional zone between deep shadow and mid-tone flesh.
    # warm_r=0.032, warm_g=0.018: gentle amber tint — less saturated
    #   than default since the canvas already has warm richness.
    # warm_b=0.008: slight blue reduction — reinforces amber warmth.
    # warm_strength=0.50: moderate gate scale on the rich canvas.
    # opacity=0.26: subtle, additive to 30 prior passes.
    print("Gaudenzio warm devotion pass (session 151 -- NEW)...", flush=True)
    p.gaudenzio_warm_devotion_pass(
        shad_lo        = 0.05,
        shad_hi        = 0.40,
        warm_r         = 0.032,
        warm_g         = 0.018,
        warm_b         = 0.008,
        warm_strength  = 0.50,
        opacity        = 0.26,
    )

    # -- Session 151 (NEW): Atmospheric depth gradient pass -------------------
    # Artistic improvement: LUMINANCE-WEIGHTED VERTICAL CHROMATIC TEMPERATURE
    # GRADIENT — Leonardo's atmospheric perspective.
    #
    # Design intent:
    # The Mona Lisa's landscape background (upper canvas: distant terrain,
    # winding paths, atmospheric haze) should read cooler and more blue-grey
    # than the foreground figure (lower canvas: hands, dress, warm flesh).
    # After 30 passes this vertical temperature gradient is already present
    # implicitly, but this pass reinforces it explicitly: warm amber push
    # at the lower canvas, cool blue-grey push at the upper canvas.
    #
    # The effect is subtle — strengthening what is already there rather than
    # imposing a new character.  On the accumulated warm-toned canvas the
    # atmospheric recession should feel like a natural consequence of depth.
    #
    # atm_warm_r=0.020, atm_warm_g=0.012: gentle warm push at figure base.
    # atm_cool_b=0.022, atm_cool_r=0.010: gentle cool push at sky/horizon.
    # luma_lo=0.12: exclude deepest shadow voids from the colour push.
    # opacity=0.24: very subtle — the 31st layer must be a whisper.
    print("Atmospheric depth gradient pass (session 151 artistic improvement -- NEW)...", flush=True)
    p.atmospheric_depth_gradient_pass(
        atm_warm_r   = 0.020,
        atm_warm_g   = 0.012,
        atm_cool_b   = 0.022,
        atm_cool_r   = 0.010,
        luma_lo      = 0.12,
        opacity      = 0.24,
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
