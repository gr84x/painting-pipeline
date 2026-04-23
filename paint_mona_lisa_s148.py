"""
paint_mona_lisa_s148.py -- Session 148 portrait painting.

Warm-start from mona_lisa_s147.png (latest accumulated canvas),
then applies session 148 additions.

Session 148 additions:
  - paris_bordone                       -- NEW (session 148)
                                           Paris Bordone (1500–1571),
                                           Venetian Renaissance.
                                           Born in Treviso, trained briefly
                                           under Titian in Venice, absorbing
                                           the master's rich chromatic
                                           approach and amber-warm palette.
                                           His portraits have an intimate
                                           warmth — flesh saturated with
                                           amber and rose, shadows remaining
                                           richly coloured and transparent
                                           rather than neutrally grey.
                                           The famous 'Fisherman Delivering
                                           the Ring to the Doge' (1534)
                                           shows complex figural command;
                                           his half-length portraits reveal
                                           the intimate colourism most
                                           purely: warm ground glowing
                                           through thin flesh passages,
                                           amber-gold bloom in midtones,
                                           and chromatically deep shadows.

  SESSION 148 MAIN PASS -- bordone_venetian_warmth_pass:

                                           Twenty-seventh distinct mode:
                                           VENETIAN INTIMATE WARMTH
                                           SATURATION + AMBER-GOLD FLESH
                                           BLOOM + CHROMATIC SHADOW DEPTH.

                                           Three sequential operations:
                                           (1) Chromatic saturation boost
                                               in [sat_lo=0.32, sat_hi=0.70]
                                               — moves RGB away from mean
                                               luma by sat_boost, enriching
                                               Venetian chromatic intensity
                                               in flesh and mid-values;
                                           (2) Amber-gold flesh bloom gate
                                               at [bloom_lo=0.42, bloom_hi=0.72]
                                               — adds warm_r/warm_g in
                                               characteristic Bordone flesh
                                               range, injecting amber-gold
                                               warmth distinct from Leonardo's
                                               cooler sfumato;
                                           (3) Shadow chromatic depth at
                                               luma < shadow_hi=0.30 — adds
                                               warm umber tint to keep shadows
                                               chromatically warm and
                                               transparent rather than grey.

                                           Distinct from all 26 prior modes:
                                           pure CHROMATIC RICHNESS axis
                                           (saturation, warmth, shadow
                                           colour) with no edge softening,
                                           no LF blending, no spatial gating.

  SESSION 148 ARTISTIC IMPROVEMENT -- luminous_ground_pass:

                                           Twenty-eighth distinct mode:
                                           WARM GROUND LUMINOSITY RECOVERY
                                           + AMBIENT LOW-VALUE UPLIFT.

                                           Simulates the warm Venetian
                                           ground (ochre/sienna) glowing
                                           through dark paint passages —
                                           the luminous transparency in
                                           near-black shadow zones that
                                           characterises Old Master oil
                                           technique.  Quadratic gate
                                           (strongest at near-black) injects
                                           warm ground_r/ground_g, then
                                           adds subtle sat_lift in the
                                           recovered zone for chromatic
                                           depth rather than mere warming.

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
    print("Applying: Paris Bordone Venetian warmth (148 -- NEW)", flush=True)
    print("Applying: Luminous ground recovery (148 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 148 (NEW): Bordone Venetian warmth pass ----------------------
    # Twenty-seventh distinct mode: VENETIAN INTIMATE WARMTH SATURATION
    # + AMBER-GOLD FLESH BLOOM + CHROMATIC SHADOW DEPTH.
    #
    # Design intent for the accumulated Leonardo canvas:
    #
    # 1. Chromatic saturation boost: The accumulated canvas has 27 layers of
    #    processing.  The sfumato approach intentionally desaturates the flesh
    #    toward warm grey-tan.  Bordone's Venetian colourism adds chromatic
    #    richness back — not garishly, but with the quiet saturation depth of
    #    a Titianesque palette.  sat_boost=0.06 is conservative; the canvas
    #    already has accumulated warmth.
    #
    # 2. Amber-gold flesh bloom: The accumulated portrait has warm amber glaze
    #    from many prior passes.  Bordone's specific quality is a richer amber-
    #    gold in the flesh midtone zone [0.44, 0.70].  warm_r=0.020, warm_g=0.010
    #    are gentle — this is a refinement of existing warmth, not a new colour.
    #
    # 3. Shadow chromatic depth: shadow_hi=0.28 targets only the near-black zone.
    #    shadow_r=0.014, shadow_g=0.006 — very subtle warm umber in deep shadows,
    #    simulating the Venetian ground's warmth showing through transparent paint.
    #
    # opacity=0.26: moderate; respectful of the 27-pass accumulated surface.
    print("Bordone Venetian warmth pass (session 148 -- NEW)...", flush=True)
    p.bordone_venetian_warmth_pass(
        sat_lo    = 0.32,
        sat_hi    = 0.70,
        sat_boost = 0.06,
        bloom_lo  = 0.44,
        bloom_hi  = 0.70,
        warm_r    = 0.020,
        warm_g    = 0.010,
        shadow_hi = 0.28,
        shadow_r  = 0.014,
        shadow_g  = 0.006,
        opacity   = 0.26,
    )

    # -- Session 148 (NEW): Luminous ground pass ------------------------------
    # Artistic improvement: twenty-eighth distinct mode.
    # WARM GROUND LUMINOSITY RECOVERY + AMBIENT LOW-VALUE UPLIFT.
    #
    # Design intent:
    # The accumulated canvas has deep shadows from many vignette, chiaroscuro,
    # and dark-ground passes.  The Venetian tradition's warm ground glowing
    # through thin paint gives shadows a luminous transparency rather than
    # opaque flatness.  This pass targets the near-black zone (luma < 0.30)
    # with a quadratic gate (strongest at absolute black) and injects warm
    # ground warmth (ground_r=0.020, ground_g=0.010) plus a sat_lift=0.03
    # that enriches the chromatic content of the recovered shadow zone.
    #
    # ground_hi=0.30: targets only the darkest shadows (avoiding midtones)
    # ground_r=0.020, ground_g=0.010: very subtle warm amber ground glow
    # sat_lift=0.03: gentle chromatic enrichment in recovered zone
    # opacity=0.22: low; this is a barely perceptible refinement
    print("Luminous ground pass (session 148 artistic improvement -- NEW)...", flush=True)
    p.luminous_ground_pass(
        ground_hi = 0.30,
        ground_r  = 0.020,
        ground_g  = 0.010,
        ground_b  = 0.000,
        sat_lift  = 0.03,
        opacity   = 0.22,
    )

    # -- Carry-forward passes from session 147 --------------------------------

    # Sodoma Sienese dreamveil (from s147 -- carry forward)
    print("Sodoma Sienese dreamveil pass (session 147 carry-forward)...", flush=True)
    p.sodoma_sienese_dreamveil_pass(
        warm_lo      = 0.38,
        warm_hi      = 0.72,
        warm_r       = 0.022,
        warm_g       = 0.012,
        sat_lo       = 0.48,
        sat_hi       = 0.78,
        sat_lift     = 0.05,
        veil_sigma   = 2.2,
        veil_amount  = 0.06,
        sky_lo       = 0.82,
        sky_b        = 0.016,
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
        cool_r       = 0.008,
        opacity      = 0.20,
    )

    # Gossaert pearl-crystalline (from s146 -- carry forward)
    print("Gossaert pearl-crystalline pass (session 146 carry-forward)...", flush=True)
    p.gossaert_pearl_crystalline_pass(
        shadow_hi       = 0.36,
        highlight_lo    = 0.70,
        pearl_cool_b    = 0.04,
        pearl_desat     = 0.12,
        shadow_warm_r   = 0.025,
        shadow_warm_b   = 0.020,
        mid_sat_boost   = 0.05,
        crystal_sigma   = 2.0,
        crystal_amount  = 0.08,
        opacity         = 0.25,
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
        shadow_tint     = 0.03,
        penumbra_chroma = 0.06,
        opacity         = 0.18,
    )

    # Cambiaso geometric planes (from s145 -- carry forward)
    print("Cambiaso geometric planes pass (session 145 carry-forward)...", flush=True)
    p.cambiaso_geometric_planes_pass(
        sigma_coarse   = 22.0,
        sigma_medium   = 5.0,
        flatten_amount = 0.50,
        edge_boost     = 0.22,
        sigma_edge     = 2.0,
        terra_r        = 0.68,
        terra_g        = 0.45,
        terra_b        = 0.18,
        terra_lo       = 0.08,
        terra_hi       = 0.38,
        terra_amount   = 0.055,
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
        cool_amount   = 0.035,
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
        vignette_strength = 0.25,
        vignette_power    = 2.2,
        cool_shift        = 0.018,
        opacity           = 0.28,
    )

    # Glazing depth pass (from session 141 -- carry forward)
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.07,
        warm_g      = 0.025,
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
