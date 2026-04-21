"""
paint_mona_lisa_s116.py -- Session 116 portrait painting.

Warm-start from mona_lisa_s101.png (the latest available base canvas),
then applies sessions 102–116 additions cumulatively.

Session 116 additions:
  - andrea_solario                           -- NEW (session 116)
                                               Andrea Solario
                                               (c. 1460–1524), Italian
                                               Lombard Leonardesque /
                                               Venetian-Influenced
                                               Milanese Renaissance.
                                               Absorbed Leonardo's
                                               sfumato technique during
                                               the master's Milanese
                                               years; fused Lombard
                                               amber warmth with
                                               Venetian cool shadow
                                               sensibility.  Perhaps
                                               the most pellucid
                                               practitioner of
                                               Leonardesque sfumato
                                               outside Leonardo himself.
                                               Famous for the Madonna
                                               with Green Cushion
                                               (Louvre) and Salome —
                                               paintings whose flesh
                                               glows with a warm
                                               amber-honey luminosity
                                               unlike any other Lombard
                                               painter.  His Venetian
                                               training gave his shadows
                                               a cool blue-violet
                                               atmospheric quality
                                               absent from purely
                                               Florentine or Bolognese
                                               work.

  SESSION 116 ARTISTIC IMPROVEMENT -- solario_pellucid_amber_pass:

                                               New pass encoding three
                                               defining Solario qualities:
                                               (1) Pellucid amber
                                               highlight — warm amber-
                                               honey lift at peak flesh
                                               (lum > 0.62): R + amber_r,
                                               G + amber_g, B - amber_b.
                                               Warmer than Boltraffio's
                                               pearl, more amber than
                                               Furini's ivory — the
                                               honey-gold quality of
                                               glazed Lombard flesh;
                                               (2) Cool violet shadow —
                                               raised-cosine blue-violet
                                               undertone in deep shadow
                                               (lum < 0.32): B + violet_b,
                                               G + violet_g, R - violet_r.
                                               Venetian atmospheric
                                               shadow quality; prevents
                                               purely warm-dark shadow;
                                               (3) Chromatic arc mid-
                                               tone warmth — sin-window
                                               warmth pulse in penumbra
                                               [0.32, 0.62]: R + arc_r *
                                               sin_window.  The sin-
                                               window peaks at the centre
                                               of the penumbra and fades
                                               toward both extremes —
                                               a smooth, physically
                                               motivated amber gradient
                                               modelling the continuously-
                                               varying colour temperature
                                               of Solario's flesh.  This
                                               is the session 116
                                               improvement: chromatic arc
                                               mid-tone warmth, more
                                               sophisticated than previous
                                               passes that handled
                                               highlights and shadows
                                               independently without
                                               modelling the transition
                                               zone.

Warm-start base: mona_lisa_s101.png
Applies: s102 (Tissot), s103 (Dolci), s104 (Giordano), s105 (Guercino),
         s106 (Ribera + foreground_warmth), s107 (Boltraffio pearled sfumato),
         s108 (Moroni silver presence), s109 (Strozzi amber impasto),
         s110 (Sassoferrato pure devotion),
         s111 (Orazio Gentileschi silver daylight),
         s112 (Jacob Jordaens earthy vitality),
         s113 (Guido Cagnacci rose flesh),
         s114 (Francesco Furini melancholic sfumato),
         s115 (Lavinia Fontana jewel costume),
         s116 (Andrea Solario pellucid amber -- NEW)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image, ImageFilter
from stroke_engine import Painter
from scipy.ndimage import gaussian_filter
import numpy as np

W, H = 780, 1080

# ── Locate warm-start base ────────────────────────────────────────────────────
S101_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s101.png"),
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s101.png"
    ),
    "/c/Source/painting-pipeline/mona_lisa_s101.png",
    "C:/Source/painting-pipeline/mona_lisa_s101.png",
]

base_path = None
for c in S101_CANDIDATES:
    c_abs = os.path.abspath(c)
    if os.path.exists(c_abs):
        base_path = c_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s101.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S101_CANDIDATES)
    )

print(f"Loading session-101 base: {base_path}", flush=True)


# ── Utilities ─────────────────────────────────────────────────────────────────

def make_figure_mask() -> np.ndarray:
    """
    Elliptical figure mask for the Mona Lisa composition.
    Returns float32 array in [0, 1], 1 = figure, 0 = background.
    """
    mask = np.zeros((H, W), dtype=np.float32)
    cx, cy = W * 0.50, H * 0.46
    rx, ry = W * 0.38, H * 0.50
    y_idx, x_idx = np.ogrid[:H, :W]
    dist = ((x_idx - cx) / rx) ** 2 + ((y_idx - cy) / ry) ** 2
    mask[dist <= 1.0] = 1.0
    mask = gaussian_filter(mask, sigma=30)
    if mask.max() > 0:
        mask = mask / mask.max()
    return mask


def make_reference() -> Image.Image:
    """
    Build a simple warm-toned reference image for passes that need one.
    Returns a PIL Image in RGB mode.
    """
    ref = Image.new("RGB", (W, H), (178, 140, 100))
    return ref


def load_png_into_painter(p: Painter, path: str) -> None:
    """Load a PNG file into the Painter's cairo surface."""
    img = Image.open(path).convert("RGBA").resize((W, H), Image.LANCZOS)
    import cairo
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surface)
    import array as arr
    img_data = img.tobytes("raw", "BGRA")
    src = cairo.ImageSurface.create_for_data(
        arr.array("B", img_data), cairo.FORMAT_ARGB32, W, H
    )
    ctx.set_source_surface(src, 0, 0)
    ctx.paint()
    p.canvas.surface.get_data()[:] = surface.get_data()[:]


def paint(out_dir: str = ".") -> str:
    """
    Apply sessions 102–116 passes on top of the session-101 base canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 116 warm-start from mona_lisa_s101.png", flush=True)
    print("Applying: Tissot(102) + Dolci(103) + Giordano(104) +", flush=True)
    print("          Guercino(105) + Ribera(106) + Boltraffio(107) +", flush=True)
    print("          Moroni silver presence (108) +", flush=True)
    print("          Strozzi amber impasto (109) +", flush=True)
    print("          Sassoferrato pure devotion (110) +", flush=True)
    print("          Orazio Gentileschi silver daylight (111) +", flush=True)
    print("          Jordaens earthy vitality (112) +", flush=True)
    print("          Guido Cagnacci rose flesh (113) +", flush=True)
    print("          Francesco Furini melancholic sfumato (114) +", flush=True)
    print("          Lavinia Fontana jewel costume (115) +", flush=True)
    print("          Andrea Solario pellucid amber (116 -- NEW)", flush=True)
    print("=" * 68, flush=True)
    print(flush=True)

    # Load session-101 base canvas
    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # Rebuild reference for passes that need it
    ref = make_reference()

    # ── Session 102: James Tissot fashionable gloss pass ─────────────────────
    print("Tissot fashionable gloss pass (session 102)...", flush=True)
    p.tissot_fashionable_gloss_pass(
        clarity_str    = 0.11,
        sheen_thresh   = 0.72,
        sheen_strength = 0.07,
        chroma_boost   = 0.06,
        mid_lo         = 0.28,
        mid_hi         = 0.72,
        highlight_cool = 0.04,
        blur_radius    = 4.0,
        opacity        = 0.27,
    )

    # ── Session 103: Carlo Dolci Florentine enamel pass ───────────────────────
    print("Dolci Florentine enamel pass (session 103)...", flush=True)
    p.dolci_florentine_enamel_pass(
        smooth_sigma      = 2.8,
        smooth_strength   = 0.55,
        flesh_lo          = 0.38,
        flesh_hi          = 0.84,
        shadow_lo         = 0.05,
        shadow_hi         = 0.32,
        shadow_depth_str  = 0.08,
        shadow_warm_r     = 0.040,
        shadow_warm_g     = 0.012,
        highlight_lo      = 0.80,
        highlight_lift    = 0.05,
        highlight_ivory_r = 0.018,
        highlight_ivory_g = 0.010,
        penumbra_lo       = 0.30,
        penumbra_hi       = 0.55,
        penumbra_amber_r  = 0.022,
        penumbra_amber_g  = 0.008,
        penumbra_amber_b  = 0.012,
        blur_radius       = 4.0,
        opacity           = 0.30,
    )

    # Session 103 IMPROVED: subsurface_scatter_pass with penumbra_warmth_depth
    print("Subsurface scatter pass (s92 improved, s103 penumbra_warmth_depth=0.07)...", flush=True)
    p.subsurface_scatter_pass(
        scatter_strength      = 0.14,
        scatter_radius        = 8.0,
        scatter_low           = 0.42,
        scatter_high          = 0.82,
        penumbra_warm         = 0.06,
        shadow_cool           = 0.04,
        shadow_pellucidity    = 0.05,
        penumbra_warmth_depth = 0.07,
        opacity               = 0.52,
    )

    # ── Session 104: Luca Giordano rapidità luminosa pass ────────────────────
    print("Giordano rapidità luminosa pass (session 104)...", flush=True)
    p.giordano_rapidita_luminosa_pass(
        aureole_cx      = 0.88,
        aureole_cy      = 0.06,
        aureole_radius  = 0.72,
        aureole_r       = 0.052,
        aureole_g       = 0.028,
        aureole_b       = 0.007,
        rim_strength    = 0.040,
        rim_sigma       = 3.0,
        shadow_hi       = 0.30,
        shadow_violet_b = 0.013,
        shadow_violet_r = 0.005,
        blur_radius     = 5.0,
        opacity         = 0.30,
    )

    # ── Session 105: il Guercino penumbra warmth pass ────────────────────────
    print("Guercino penumbra warmth pass (session 105)...", flush=True)
    p.guercino_penumbra_warmth_pass(
        penumbra_lo      = 0.28,
        penumbra_hi      = 0.62,
        amber_r          = 0.038,
        amber_g          = 0.018,
        amber_b          = 0.008,
        light_cx         = 0.18,
        light_cy         = 0.08,
        light_radius     = 0.85,
        directional_str  = 0.018,
        shadow_lo        = 0.05,
        shadow_hi        = 0.28,
        shadow_warm_r    = 0.022,
        shadow_warm_g    = 0.008,
        blur_radius      = 4.5,
        opacity          = 0.28,
    )

    # ── Session 105 IMPROVED: sfumato_veil_pass with penumbra_bloom ───────────
    print("Sfumato veil pass (s82 improved, s105 penumbra_bloom=0.06)...", flush=True)
    p.sfumato_veil_pass(
        reference               = ref,
        n_veils                 = 8,
        blur_radius             = 10.0,
        warmth                  = 0.32,
        veil_opacity            = 0.07,
        edge_only               = True,
        chroma_dampen           = 0.18,
        depth_gradient          = 0.06,
        shadow_warm_recovery    = 0.05,
        chroma_gate             = 0.12,
        highlight_ivory_lift    = 0.04,
        highlight_ivory_thresh  = 0.82,
        atmospheric_blue_shift  = 0.03,
        penumbra_bloom          = 0.06,
        penumbra_bloom_lo       = 0.30,
        penumbra_bloom_hi       = 0.60,
    )

    # ── Session 106: Jusepe de Ribera tenebrism pass ─────────────────────────
    print("Ribera tenebrism pass (session 106)...", flush=True)
    p.ribera_tenebrism_pass(
        shadow_lo        = 0.0,
        shadow_hi        = 0.30,
        void_black_r     = 0.014,
        void_black_g     = 0.006,
        highlight_lo     = 0.72,
        grit_strength    = 0.022,
        grit_sigma       = 1.2,
        warm_r           = 0.028,
        warm_g           = 0.010,
        blur_radius      = 4.0,
        opacity          = 0.28,
    )

    # ── Session 106 IMPROVED: foreground_warmth_pass ──────────────────────────
    print("Foreground warmth pass (s106 improved)...", flush=True)
    p.foreground_warmth_pass(
        warmth_r    = 0.045,
        warmth_g    = 0.018,
        warmth_b    = 0.005,
        depth_lo    = 0.55,
        depth_hi    = 1.00,
        blur_sigma  = 8.0,
        opacity     = 0.32,
    )

    # ── Session 107: Boltraffio pearled sfumato pass ───────────────────────────
    print("Boltraffio pearled sfumato pass (session 107)...", flush=True)
    p.boltraffio_pearled_sfumato_pass(
        hi_lo        = 0.72,
        pearl_r      = 0.006,
        pearl_g      = 0.008,
        pearl_b      = 0.014,
        penumbra_lo  = 0.30,
        penumbra_hi  = 0.68,
        cool_b       = 0.012,
        cool_r       = 0.006,
        shadow_hi    = 0.28,
        shadow_b     = 0.008,
        shadow_r     = 0.010,
        smooth_sigma = 2.0,
        smooth_lo    = 0.32,
        smooth_hi    = 0.80,
        smooth_str   = 0.42,
        blur_radius  = 3.5,
        opacity      = 0.28,
    )

    # ── Session 108: Moroni silver presence pass ───────────────────────────────
    print("Moroni silver presence pass (session 108)...", flush=True)
    p.moroni_silver_presence_pass(
        hi_lo        = 0.68,
        silver_r     = 0.004,
        silver_g     = 0.005,
        silver_b     = 0.010,
        shadow_hi    = 0.35,
        warm_r       = 0.018,
        warm_g       = 0.008,
        warm_b       = 0.003,
        mid_gamma    = 0.94,
        blur_radius  = 3.0,
        opacity      = 0.26,
    )

    # ── Session 109: Strozzi amber impasto pass ───────────────────────────────
    print("Strozzi amber impasto pass (session 109)...", flush=True)
    p.strozzi_amber_impasto_pass(
        impasto_thresh   = 0.70,
        impasto_r        = 0.030,
        impasto_g        = 0.016,
        impasto_b        = 0.005,
        chestnut_lo      = 0.22,
        chestnut_hi      = 0.52,
        chestnut_r       = 0.025,
        chestnut_g       = 0.010,
        chestnut_b       = 0.005,
        shadow_hi        = 0.22,
        amber_r          = 0.016,
        amber_g          = 0.007,
        smooth_lo        = 0.28,
        smooth_hi        = 0.75,
        smooth_str       = 0.42,
        blur_radius      = 3.5,
        opacity          = 0.30,
    )

    # ── Session 110: Sassoferrato pure devotion pass ───────────────────────────
    print("Sassoferrato pure devotion pass (session 110)...", flush=True)
    p.sassoferrato_pure_devotion_pass(
        ultramarine_lo   = 0.22,
        ultramarine_hi   = 0.55,
        ultra_b          = 0.022,
        ultra_g          = 0.005,
        ultra_r          = 0.006,
        porcelain_lo     = 0.68,
        porcelain_r      = 0.006,
        porcelain_g      = 0.004,
        porcelain_b      = 0.010,
        smooth_sigma     = 3.0,
        smooth_lo        = 0.30,
        smooth_hi        = 0.82,
        smooth_str       = 0.48,
        blur_radius      = 4.0,
        opacity          = 0.28,
    )

    # ── Session 111: Orazio Gentileschi silver daylight pass ──────────────────
    print("Orazio Gentileschi silver daylight pass (session 111)...", flush=True)
    p.orazio_gentileschi_silver_daylight_pass(
        hi_lo            = 0.70,
        silver_r         = 0.004,
        silver_g         = 0.005,
        silver_b         = 0.012,
        fabric_lo        = 0.30,
        fabric_hi        = 0.68,
        fabric_b         = 0.010,
        fabric_g         = 0.005,
        shadow_hi        = 0.28,
        shadow_cool_b    = 0.008,
        shadow_cool_r    = 0.006,
        smooth_sigma     = 2.5,
        smooth_lo        = 0.28,
        smooth_hi        = 0.78,
        smooth_str       = 0.40,
        blur_radius      = 3.5,
        opacity          = 0.26,
    )

    # ── Session 112: Jacob Jordaens earthy vitality pass ─────────────────────
    print("Jordaens earthy vitality pass (session 112)...", flush=True)
    p.jordaens_earthy_vitality_pass(
        hi_lo         = 0.72,
        cream_r       = 0.020,
        cream_g       = 0.012,
        cream_b       = 0.004,
        mid_lo        = 0.30,
        mid_hi        = 0.70,
        sienna_r      = 0.018,
        sienna_g      = 0.008,
        shadow_hi     = 0.28,
        amber_r       = 0.016,
        amber_g       = 0.007,
        blur_radius   = 3.5,
        opacity       = 0.28,
    )

    # ── Session 113: Guido Cagnacci rose flesh pass ───────────────────────────
    print("Guido Cagnacci rose flesh pass (session 113)...", flush=True)
    p.cagnacci_rose_flesh_pass(
        rose_lo       = 0.40,
        rose_hi       = 0.80,
        rose_r        = 0.022,
        rose_g        = 0.006,
        rose_b        = 0.010,
        hi_lo         = 0.75,
        ivory_r       = 0.012,
        ivory_g       = 0.006,
        shadow_hi     = 0.30,
        warm_r        = 0.014,
        warm_g        = 0.005,
        blur_radius   = 3.5,
        opacity       = 0.28,
    )

    # ── Session 114: Francesco Furini melancholic sfumato pass ───────────────
    print("Francesco Furini melancholic sfumato pass (session 114)...", flush=True)
    p.furini_melancholic_sfumato_pass(
        hi_lo          = 0.68,
        ivory_r        = 0.012,
        ivory_g        = 0.008,
        ivory_b        = 0.004,
        penumbra_lo    = 0.28,
        penumbra_hi    = 0.60,
        lavender_b     = 0.018,
        lavender_r     = 0.008,
        shadow_hi      = 0.26,
        shadow_b       = 0.010,
        shadow_r       = 0.012,
        smooth_sigma   = 2.2,
        smooth_lo      = 0.30,
        smooth_hi      = 0.78,
        smooth_str     = 0.45,
        blur_radius    = 3.5,
        opacity        = 0.30,
    )

    # ── Session 115: Lavinia Fontana jewel costume pass ───────────────────────
    print("Lavinia Fontana jewel costume pass (session 115)...", flush=True)
    p.fontana_jewel_costume_pass(
        hi_lo        = 0.70,
        ivory_r      = 0.012,
        ivory_g      = 0.007,
        ivory_b      = 0.002,
        costume_lo   = 0.18,
        costume_hi   = 0.46,
        crimson_r    = 0.018,
        crimson_g    = 0.003,
        crimson_b    = 0.006,
        shadow_hi    = 0.22,
        amber_r      = 0.012,
        amber_g      = 0.005,
        blur_radius  = 3.0,
        opacity      = 0.26,  # slightly reduced to make room for Solario
    )

    # ── SESSION 116: Andrea Solario pellucid amber pass (NEW) ─────────────────
    # The pellucid amber pass encodes Solario's three defining qualities:
    #
    # (1) Pellucid amber highlight — warm amber-honey lift at peak flesh
    #     (hi_lo=0.62).  After the accumulated Baroque and Italian passes,
    #     the highlight zone has a complex character: Boltraffio's cool pearl,
    #     Moroni's silver, Furini's warm ivory, Fontana's rose-ivory.  Solario's
    #     amber_r (0.016) adds a distinctly amber-honey warmth — warmer than any
    #     of the preceding highlight treatments, more golden and pellucid.
    #     The amber_b reduction (0.003) prevents the cumulative blue from ivory
    #     and pearl passes from neutralising the amber quality.
    #
    # (2) Cool violet shadow — raised-cosine blue-violet in zones below lum=0.32.
    #     After Furini's cool shadow (shadow_r reduction) and Fontana's amber
    #     counter-correction, Solario's violet_b (0.014) introduces the Venetian
    #     atmospheric shadow quality — a blue-violet coolness in the deepest zones
    #     that reads as spatial recession rather than mere darkness.  This is
    #     fundamentally different from the warm amber shadows of the Bolognese
    #     tradition (Guercino, Strozzi, Fontana) — it gives the shadow zones an
    #     atmospheric, recessive quality that matches Solario's landscape backgrounds.
    #
    # (3) Chromatic arc mid-tone warmth — sin-window pulse in [0.32, 0.62].
    #     arc_r (0.012) and arc_g (0.005) create a continuously-varying warmth
    #     gradient that peaks in the penumbra centre and fades toward both shadow
    #     and highlight extremes.  This is the session 116 improvement: a smooth,
    #     physically motivated transition zone that connects Solario's cool shadows
    #     and amber highlights through a warm amber penumbra — replicating the
    #     actual behaviour of semi-transparent amber oil glazes.
    print("Andrea Solario pellucid amber pass (session 116 -- NEW)...", flush=True)
    p.solario_pellucid_amber_pass(
        hi_lo        = 0.62,
        amber_r      = 0.016,
        amber_g      = 0.009,
        amber_b      = 0.003,
        shadow_hi    = 0.32,
        violet_b     = 0.014,
        violet_g     = 0.004,
        violet_r     = 0.005,
        arc_lo       = 0.32,
        arc_hi       = 0.62,
        arc_r        = 0.012,
        arc_g        = 0.005,
        blur_radius  = 3.5,
        opacity      = 0.30,
    )

    # ── Finishing passes ──────────────────────────────────────────────────────

    # Edge lost-and-found (s81 improved, s91)
    print("Edge lost-and-found pass (s81/s91)...", flush=True)
    p.edge_lost_and_found_pass(
        focal_xy             = (0.515, 0.195),
        found_radius         = 0.28,
        found_sharpness      = 0.48,
        lost_blur            = 2.0,
        strength             = 0.34,
        figure_only          = True,
        gradient_selectivity = 0.65,
        soft_halo_strength   = 0.14,
    )

    # Old-master varnish
    print("Old-master varnish pass (s63)...", flush=True)
    p.old_master_varnish_pass(
        amber_strength  = 0.12,
        edge_darken     = 0.10,
        highlight_desat = 0.06,
        opacity         = 0.28,
    )

    # Final glaze — warm amber reflecting Lombard-Leonardesque amber warmth
    print("Final glaze (warm amber for Lombard-Leonardesque pellucidity)...", flush=True)
    p.glaze((0.58, 0.44, 0.18), opacity=0.024)

    # Vignette and crackle
    print("Finishing (vignette + crackle)...", flush=True)
    p.finish(vignette=0.52, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s116.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
