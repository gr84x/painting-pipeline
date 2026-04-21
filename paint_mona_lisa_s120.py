"""
paint_mona_lisa_s120.py -- Session 120 portrait painting.

Warm-start from mona_lisa_s101.png (the latest available base canvas),
then applies sessions 102–120 additions cumulatively.

Session 120 additions:
  - lotto                                    -- NEW (session 120)
                                               Lorenzo Lotto
                                               (c. 1480–1556/57), Italian
                                               (Venetian, later Bergamask).
                                               One of the most psychologically
                                               intense and formally eccentric
                                               portraitists of the Italian
                                               Renaissance.  Where Titian's
                                               sitters project serene authority,
                                               Lotto's appear caught mid-thought:
                                               restless, searching, inward.
                                               The Portrait of Andrea Odoni
                                               (1527, Hampton Court) is almost
                                               disquieting — a collector
                                               surrounded by antique fragments,
                                               gaze turned inward with
                                               self-absorbed intensity.  Lotto
                                               moved restlessly between Venice,
                                               Bergamo, and the Marche, never
                                               settling into a single courtly
                                               idiom — which accounts for the
                                               psychological edge and chromatic
                                               eccentricity that distinguish
                                               him from his more celebrated
                                               Venetian contemporaries.  His
                                               palette makes unexpected colour
                                               contrasts: vivid grass-green
                                               against mauve, cool grey-blue
                                               against warm ochre, acidic
                                               yellow-green in shadow zones.

  SESSION 120 ARTISTIC IMPROVEMENT -- lotto_restless_vivacity_pass:

                                               New pass encoding Lotto's
                                               defining chromatic quality:
                                               the multi-scale chromatic
                                               vibration field.

                                               A noise field is built from
                                               Gaussian-smoothed random noise
                                               at three spatial scales:
                                                 fine   (σ × 0.32) — stroke-
                                                        level pigment variation
                                                 medium (σ × 1.00) — single
                                                        glaze layer variation
                                                 coarse (σ × 2.40) — imprimatura
                                                        breathing through
                                               Weighted combination (0.50 fine
                                               + 0.35 medium + 0.15 coarse)
                                               produces a smooth, spatially
                                               non-uniform field in [-1, 1].

                                               Applied in the mid-tone zone
                                               via a sin²-bell mask with
                                               amplitude vibration_str (≈ 0.010),
                                               the field adds a spatially
                                               varying warm/cool shift at each
                                               pixel.  Some areas read slightly
                                               warmer; others slightly cooler.
                                               This models the optical complexity
                                               of Venetian multi-glaze technique:
                                               each spatial scale represents one
                                               layer of the glazing stack, and
                                               their combination creates the
                                               chromatic 'singing quality' that
                                               Lotto's flesh is known for.

                                               Unlike the uniform single-frequency
                                               effects of previous sessions —
                                               sin-window (s116 arc), sin²-window
                                               (s117 ground warmth), Gaussian-
                                               peaked (s118 moonveil), anisotropic
                                               streak (s119 silk sheen) — the
                                               multi-scale field captures the full
                                               spatial frequency content of oil
                                               glazing over canvas texture.  It is
                                               a more realistic model of the warm-
                                               cool variation that makes painted
                                               skin look alive rather than
                                               uniformly tinted.

Warm-start base: mona_lisa_s101.png
Applies: s102 (Tissot), s103 (Dolci), s104 (Giordano), s105 (Guercino),
         s106 (Ribera + atmospheric_depth), s107 (Boltraffio pearled sfumato),
         s108 (Moroni silver presence), s109 (Strozzi amber impasto),
         s110 (Sassoferrato pure devotion),
         s111 (Orazio Gentileschi silver daylight),
         s112 (Jacob Jordaens earthy vitality),
         s113 (Guido Cagnacci rose flesh),
         s114 (Francesco Furini melancholic sfumato),
         s115 (Lavinia Fontana jewel costume),
         s116 (Andrea Solario pellucid amber),
         s117 (Pietro Perugino Umbrian serenity),
         s118 (Giovanni Gerolamo Savoldo silver moonveil),
         s119 (Pompeo Batoni anisotropic silk sheen),
         s120 (Lorenzo Lotto chromatic vibration -- NEW)
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
    Apply sessions 102–120 passes on top of the session-101 base canvas.

    Returns the output PNG path.
    """
    print("=" * 68, flush=True)
    print("Session 120 warm-start from mona_lisa_s101.png", flush=True)
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
    print("          Andrea Solario pellucid amber (116) +", flush=True)
    print("          Pietro Perugino Umbrian serenity (117) +", flush=True)
    print("          Giovanni Gerolamo Savoldo silver moonveil (118) +", flush=True)
    print("          Pompeo Batoni anisotropic silk sheen (119) +", flush=True)
    print("          Lorenzo Lotto chromatic vibration (120 -- NEW)", flush=True)
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

    # ── Session 106: Jusepe de Ribera gritty tenebrism pass ──────────────────
    print("Ribera gritty tenebrism pass (session 106)...", flush=True)
    p.ribera_gritty_tenebrism_pass(
        shadow_hi        = 0.22,
        shadow_warm_r    = 0.015,
        shadow_warm_g    = 0.006,
        grain_strength   = 0.020,
        penumbra_lo      = 0.22,
        penumbra_hi      = 0.45,
        penumbra_grain   = 0.018,
        light_cx         = 0.15,
        light_cy         = 0.08,
        light_radius     = 0.70,
        amber_r          = 0.028,
        amber_g          = 0.012,
        blur_radius      = 3.5,
        opacity          = 0.12,
    )

    # ── Session 106 IMPROVED: atmospheric_depth_pass with foreground_warmth ──
    print("Atmospheric depth pass (s106 improvement -- foreground_warmth=0.08)...", flush=True)
    p.atmospheric_depth_pass(
        haze_color             = (0.68, 0.74, 0.84),
        desaturation           = 0.62,
        lightening             = 0.46,
        depth_gamma            = 1.6,
        background_only        = True,
        horizon_glow_band      = 0.12,
        horizon_y_frac         = 0.55,
        horizon_band_sigma     = 0.06,
        zenith_luminance_boost = 0.06,
        zenith_band_sigma      = 0.10,
        foreground_warmth      = 0.08,
        foreground_band_sigma  = 0.18,
    )

    # ── Session 107: Giovanni Antonio Boltraffio pearled sfumato pass ─────────
    print("Boltraffio pearled sfumato pass (session 107)...", flush=True)
    p.boltraffio_pearled_sfumato_pass(
        pearl_lo          = 0.72,
        pearl_r           = 0.010,
        pearl_g           = 0.015,
        pearl_b           = 0.022,
        shadow_hi         = 0.28,
        shadow_b          = 0.018,
        shadow_g          = 0.006,
        shadow_r          = 0.004,
        flesh_lo          = 0.40,
        flesh_hi          = 0.72,
        clarity_sigma     = 0.8,
        clarity_strength  = 0.14,
        blur_radius       = 4.0,
        opacity           = 0.32,
    )

    # ── Session 108: Giovanni Battista Moroni silver presence pass ────────────
    print("Moroni silver presence pass (session 108)...", flush=True)
    p.moroni_silver_presence_pass(
        hi_lo         = 0.70,
        silver_r      = 0.006,
        silver_g      = 0.010,
        silver_b      = 0.016,
        shadow_hi     = 0.35,
        warm_r        = 0.016,
        warm_g        = 0.008,
        warm_b        = 0.005,
        mid_lo        = 0.35,
        mid_hi        = 0.70,
        mid_gamma_lo  = 0.95,
        mid_gamma_hi  = 1.05,
        blur_radius   = 3.5,
        opacity       = 0.34,
    )

    # ── Session 109: Bernardo Strozzi amber impasto pass ─────────────────────
    print("Strozzi amber impasto pass (session 109)...", flush=True)
    p.strozzi_amber_impasto_pass(
        shadow_hi    = 0.36,
        amber_r      = 0.028,
        amber_g      = 0.014,
        amber_b      = 0.020,
        hi_lo        = 0.74,
        cream_r      = 0.012,
        cream_g      = 0.008,
        cream_b      = 0.010,
        hi_boost     = 1.035,
        mid_lo       = 0.36,
        mid_hi       = 0.74,
        rose_r       = 0.014,
        rose_b       = 0.007,
        blur_radius  = 4.0,
        opacity      = 0.38,
    )

    # ── Session 110: Sassoferrato pure devotion pass ──────────────────────────
    print("Sassoferrato pure devotion pass (session 110)...", flush=True)
    p.sassoferrato_pure_devotion_pass(
        ultra_thresh  = 0.04,
        ultra_b_lift  = 0.022,
        ultra_r_damp  = 0.016,
        pearl_lo      = 0.76,
        pearl_b_lift  = 0.010,
        pearl_r_damp  = 0.007,
        shadow_hi     = 0.30,
        shadow_b_lift = 0.016,
        shadow_r_damp = 0.008,
        blur_radius   = 3.5,
        opacity       = 0.30,
    )

    # ── Session 111: Orazio Gentileschi silver daylight pass ─────────────────
    print("Orazio Gentileschi silver daylight pass (session 111)...", flush=True)
    p.orazio_silver_daylight_pass(
        hi_lo          = 0.68,
        silver_r_damp  = 0.010,
        silver_b_lift  = 0.016,
        mid_lo         = 0.32,
        mid_hi         = 0.68,
        chroma_lift    = 0.018,
        shadow_hi      = 0.34,
        cool_r_damp    = 0.008,
        cool_b_lift    = 0.012,
        blur_radius    = 3.0,
        opacity        = 0.30,
    )

    # ── Session 112: Jacob Jordaens earthy vitality pass ─────────────────────
    print("Jordaens earthy vitality pass (session 112)...", flush=True)
    p.jordaens_earthy_vitality_pass(
        hi_lo        = 0.72,
        cream_r      = 0.014,
        cream_g      = 0.007,
        mid_lo       = 0.28,
        mid_hi       = 0.72,
        ruddy_r      = 0.024,
        ruddy_g      = 0.010,
        ruddy_b      = 0.009,
        shadow_hi    = 0.38,
        ochre_r      = 0.020,
        ochre_g      = 0.010,
        blur_radius  = 4.0,
        opacity      = 0.34,
    )

    # ── Session 113: Guido Cagnacci rose flesh pass ───────────────────────────
    print("Guido Cagnacci rose flesh pass (session 113)...", flush=True)
    p.cagnacci_rose_flesh_pass(
        hi_lo        = 0.70,
        rose_r_lift  = 0.010,
        rose_b_damp  = 0.005,
        mid_lo       = 0.34,
        mid_hi       = 0.70,
        peach_r      = 0.016,
        peach_g      = 0.006,
        peach_b      = 0.008,
        shadow_hi    = 0.34,
        warm_r       = 0.014,
        warm_g       = 0.006,
        blur_radius  = 3.5,
        opacity      = 0.32,
    )

    # ── Session 114: Francesco Furini melancholic sfumato pass ───────────────
    print("Francesco Furini melancholic sfumato pass (session 114)...", flush=True)
    p.furini_melancholic_sfumato_pass(
        hi_lo          = 0.68,
        ivory_r        = 0.010,
        ivory_g        = 0.007,
        ivory_b        = 0.003,
        penumbra_lo    = 0.28,
        penumbra_hi    = 0.60,
        lavender_b     = 0.015,
        lavender_r     = 0.007,
        shadow_hi      = 0.24,
        shadow_b       = 0.008,
        shadow_r       = 0.010,
        smooth_sigma   = 2.2,
        smooth_lo      = 0.28,
        smooth_hi      = 0.76,
        smooth_str     = 0.40,
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
        opacity      = 0.26,
    )

    # ── Session 116: Andrea Solario pellucid amber pass ───────────────────────
    print("Andrea Solario pellucid amber pass (session 116)...", flush=True)
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

    # ── Session 117: Pietro Perugino Umbrian serenity pass ────────────────────
    print("Pietro Perugino Umbrian serenity pass (session 117)...", flush=True)
    p.perugino_serene_grace_pass(
        ground_lo    = 0.30,
        ground_hi    = 0.75,
        ground_r     = 0.013,
        ground_g     = 0.006,
        hi_lo        = 0.70,
        ivory_r      = 0.010,
        ivory_g      = 0.006,
        ivory_b      = 0.003,
        shadow_hi    = 0.35,
        warm_r       = 0.013,
        warm_g       = 0.006,
        blur_radius  = 4.0,
        opacity      = 0.30,
    )

    # ── Session 118: Giovanni Gerolamo Savoldo silver moonveil pass ───────────
    print("Giovanni Gerolamo Savoldo silver moonveil pass (session 118)...", flush=True)
    p.savoldo_silver_veil_pass(
        penumbra_lo  = 0.28,
        penumbra_hi  = 0.62,
        silver_r     = 0.010,
        silver_b     = 0.022,
        hi_lo        = 0.70,
        ivory_r      = 0.012,
        ivory_g      = 0.007,
        shadow_hi    = 0.32,
        warm_r       = 0.012,
        warm_g       = 0.005,
        blur_radius  = 4.0,
        opacity      = 0.28,
    )

    # ── Session 119: Pompeo Batoni anisotropic silk-sheen pass ────────────────
    print("Pompeo Batoni anisotropic silk-sheen pass (session 119)...", flush=True)
    p.batoni_silk_sheen_pass(
        streak_angle   = 45.0,
        streak_width   = 4.0,
        streak_spacing = 11.0,
        silk_lo        = 0.48,
        streak_r       = 0.032,
        streak_g       = 0.022,
        streak_b       = 0.008,
        blur_along     = 12.0,
        blur_across    = 1.5,
        opacity        = 0.26,
    )

    # ── SESSION 120: Lorenzo Lotto multi-scale chromatic vibration pass (NEW) ─
    # The vibration pass encodes Lotto's defining chromatic quality:
    #
    # A noise field composed of Gaussian-smoothed random noise at three spatial
    # scales is applied in the mid-tone zone.  Fine grain (σ × 0.32) captures
    # stroke-level pigment variation; medium (σ × 1) models the glaze layer;
    # coarse (σ × 2.4) models the imprimatura breathing through.  Weighted
    # combination (0.50 fine + 0.35 medium + 0.15 coarse) creates a smooth,
    # non-uniform field that adds ± vibration_str warm/cool variation at each
    # pixel.  The result: some areas read slightly warmer, others slightly
    # cooler — the chromatic 'singing quality' of Lotto's flesh.
    #
    # Three stages:
    # 1. Warm vivacity lift in highlights (lum > 0.68): R + 0.013, G + 0.007,
    #    B - 0.004 — warm rose-ivory, neither cool pearl nor neutral ivory.
    # 2. Cool eccentric shadow accent (lum < 0.36): B + 0.011, G - 0.004.
    #    Lotto's darks carry cool blue-grey — distinguishing him from the warm-
    #    dark Giorgionesque tradition and adding psychological searching quality.
    # 3. Multi-scale vibration field in mid-tones: ± 0.009 warm/cool variation.
    print("Lorenzo Lotto multi-scale chromatic vibration pass (session 120 -- NEW)...", flush=True)
    p.lotto_restless_vivacity_pass(
        hi_lo          = 0.68,
        vivacity_r     = 0.013,
        vivacity_g     = 0.007,
        vivacity_b     = 0.004,
        shadow_hi      = 0.36,
        shadow_cool_b  = 0.011,
        shadow_warm_g  = 0.004,
        mid_lo         = 0.36,
        mid_hi         = 0.68,
        vibration_str  = 0.009,
        noise_scale    = 28.0,
        blur_radius    = 4.0,
        opacity        = 0.30,
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

    # Final glaze — warm Venetian golden unifier (Lotto's chromatic ground)
    print("Final glaze (warm Venetian golden for Lotto ground warmth)...", flush=True)
    p.glaze((0.60, 0.48, 0.22), opacity=0.016)

    # Vignette and crackle
    print("Finishing (vignette + crackle)...", flush=True)
    p.finish(vignette=0.52, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s120.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
