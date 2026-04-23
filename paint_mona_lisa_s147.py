"""
paint_mona_lisa_s147.py -- Session 147 portrait painting.

Warm-start from mona_lisa_s146.png (latest accumulated canvas),
then applies session 147 additions.

Session 147 additions:
  - sodoma                              -- NEW (session 147)
                                           Sodoma (Giovanni Antonio Bazzi,
                                           1477–1549), Sienese Leonardesque.
                                           Born in Vercelli (Piedmont),
                                           trained in Lombardy where he
                                           encountered Leonardo's Milanese
                                           circle (Boltraffio, de Predis),
                                           absorbing the sfumato approach to
                                           flesh.  Settled in Siena by 1501,
                                           absorbing the city's deep tradition
                                           of warm golden grounds and luminous
                                           devotional tenderness.  Worked
                                           alongside Raphael at the Vatican
                                           Stanza della Segnatura (1508).
                                           His flesh has a characteristic
                                           amber-golden interior glow in
                                           the midtones — the Sienese ochre
                                           ground glowing through thin paint
                                           layers — combined with near-sfumato
                                           soft edge dissolution and a barely
                                           perceptible Sienese sky-blue whisper
                                           in the brightest highlights.

  SESSION 147 MAIN PASS -- sodoma_sienese_dreamveil_pass:

                                           Twenty-fifth distinct mode:
                                           WARM SIENESE MIDTONE GILDING
                                           + DREAMVEIL GLOBAL LF BLEND
                                           + SKY-BLUE HIGHLIGHT WHISPER.

                                           Three sequential operations:
                                           (1) Warm golden midtone gate
                                               in [warm_lo=0.38, warm_hi=0.72]
                                               boosts R and G in flesh
                                               midtones (Sienese warmth);
                                           (2) Saturation lift in upper
                                               midtones [0.48, 0.78] adds
                                               chromatic richness;
                                           (3) Dreamveil LF blend at
                                               veil_sigma=2.2 softens
                                               edges without full sfumato;
                                           (4) Sky-blue whisper at
                                               luma > 0.80 links brightest
                                               flesh to Sienese celestial blue.

                                           Distinct from all 24 prior modes:
                                           uniform LF dreamveil blend
                                           (not trembling Guardi, not zone-
                                           flattening Cambiaso, not stroke-
                                           level sfumato Leonardo).

  SESSION 147 ARTISTIC IMPROVEMENT -- specular_clarity_pass:

                                           Twenty-sixth distinct mode:
                                           BRIGHT-ZONE USM SHARPENING
                                           + VERY-BRIGHTEST COOL-PEARL PEAK.

                                           Refines specular highlights as
                                           focused point-source light — the
                                           forehead catch-light, nose ridge
                                           gleam, and hand highlights acquire
                                           micro-sharpening (USM at clarity_lo)
                                           and the very brightest peak receives
                                           a barely-perceptible cool-pearl cast
                                           (Vermeer specular quality), reducing
                                           R slightly and boosting B.

Warm-start base: mona_lisa_s146.png
Applies: s146 accumulated base + s147 (Sodoma dreamveil -- NEW)
                                  + s147 (Specular clarity -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
import numpy as np

W, H = 780, 1080

# -- Locate warm-start base ---------------------------------------------------
S146_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s146.png"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mona_lisa_s146.png"),
    "C:/Source/painting-pipeline/mona_lisa_s146.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s145.png"),
    "C:/Source/painting-pipeline/mona_lisa_s145.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s144.png"),
    "C:/Source/painting-pipeline/mona_lisa_s144.png",
]

base_path = None
for c in S146_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find warm-start base. Searched:\n" +
        "\n".join(f"  {c}" for c in S146_CANDIDATES)
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
    print("Session 147 warm-start from accumulated canvas", flush=True)
    print("Applying: Sodoma Sienese dreamveil (147 -- NEW)", flush=True)
    print("Applying: Specular clarity (147 -- NEW)", flush=True)
    print("=" * 68, flush=True)

    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # -- Session 147 (NEW): Sodoma Sienese dreamveil pass ---------------------
    # Twenty-fifth distinct mode: WARM SIENESE MIDTONE GILDING + DREAMVEIL
    # GLOBAL LF BLEND + SKY-BLUE HIGHLIGHT WHISPER.
    #
    # Design intent for the accumulated Leonardo canvas:
    #
    # 1. Golden midtone warmth: The accumulated canvas already has Leonardo's
    #    warm amber sfumato (from the many prior velatura and glazing passes).
    #    Sodoma's Sienese golden warmth is subtly different — it peaks in the
    #    midtone range [0.38, 0.72] with a gentle R+G boost rather than a
    #    broad amber glaze.  warm_r=0.022, warm_g=0.012 are conservative —
    #    the canvas already has warmth; we add Sienese golden specificity.
    #
    # 2. Saturation lift: sat_lift=0.05 in [0.48, 0.78] — very subtle.
    #    The sfumato portrait is intentionally desaturated in the midtones;
    #    Sodoma's Sienese tradition had slightly more chromatic richness in
    #    the flesh than Leonardo's purest sfumato.
    #
    # 3. Dreamveil LF blend: veil_sigma=2.2, veil_amount=0.06 — a very
    #    gentle global soft blend.  The accumulated canvas already has 25
    #    layers of processing; the dreamveil adds a unifying luminous softness
    #    without visibly blurring the portrait.
    #
    # 4. Sky-blue whisper: sky_lo=0.82, sky_b=0.016 — targets only the
    #    brightest catch-lights (forehead, nose ridge).  A barely perceptible
    #    Sienese sky-blue linking flesh to background.
    #
    # opacity=0.28: moderate; respectful of the 25-pass accumulated surface.
    print("Sodoma Sienese dreamveil pass (session 147 -- NEW)...", flush=True)
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
        opacity      = 0.28,
    )

    # -- Session 147 (NEW): Specular clarity pass -----------------------------
    # Artistic improvement: twenty-sixth distinct mode.
    # Refines specular highlights as focused point-source light — USM at
    # bright zone + barely-perceptible cool-pearl at very brightest peak.
    #
    # Design intent:
    # The accumulated canvas has excellent sfumato overall but the specular
    # highlights (forehead, nose ridge, lips, hands) may be slightly soft
    # from the repeated blending passes.  specular_clarity_pass adds micro-
    # sharpening only at bright pixels (clarity_lo=0.72) and a barely
    # perceptible cool-pearl at the very brightest peak (cool_lo=0.85),
    # giving the portrait the focused point-source quality of Old Master
    # window illumination.
    #
    # clarity_lo=0.72: targets bright pixels (forehead catch-light, nose)
    # usm_amount=0.14: gentle — the sfumato should not be disturbed broadly
    # cool_lo=0.85: only the absolute peak highlights
    # cool_b=0.014, cool_r=0.010: barely perceptible cool pearl
    # opacity=0.24: low; this is a subtle refinement
    print("Specular clarity pass (session 147 artistic improvement -- NEW)...", flush=True)
    p.specular_clarity_pass(
        clarity_lo   = 0.72,
        sigma        = 1.0,
        usm_amount   = 0.14,
        cool_lo      = 0.85,
        cool_b       = 0.014,
        cool_r       = 0.010,
        opacity      = 0.24,
    )

    # -- Carry-forward passes from session 146 --------------------------------

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
        opacity         = 0.30,
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
        opacity         = 0.22,
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
        opacity        = 0.15,
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
        cool_amount   = 0.040,
        sat_dampen    = 0.07,
        opacity       = 0.16,
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
        opacity       = 0.12,
    )

    # Focal vignette (from s142 -- carry forward)
    print("Focal vignette pass (session 142 carry-forward)...", flush=True)
    p.focal_vignette_pass(
        focal_x           = 0.50,
        focal_y           = 0.35,
        vignette_strength = 0.25,
        vignette_power    = 2.2,
        cool_shift        = 0.018,
        opacity           = 0.30,
    )

    # Glazing depth pass (from session 141 -- carry forward)
    print("Glazing depth pass (session 141 carry-forward)...", flush=True)
    p.glazing_depth_pass(
        glaze_sigma = 3.5,
        warm_r      = 0.07,
        warm_g      = 0.025,
        depth_low   = 0.28,
        depth_high  = 0.72,
        opacity     = 0.12,
    )

    # Velatura: warm amber unifying glaze
    print("Velatura warm amber glaze (Leonardo sfumato finish)...", flush=True)
    p.velatura_pass(midtone_tint=(0.80, 0.65, 0.38), midtone_opacity=0.04)

    # Vignette finish
    print("Finishing (vignette)...", flush=True)
    p.finish(vignette=0.48, crackle=False)

    out_path = os.path.join(out_dir, "mona_lisa_s147.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
