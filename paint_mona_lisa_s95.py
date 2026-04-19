"""
paint_mona_lisa_s95.py -- Session 95 portrait painting.

Paints the Mona Lisa-inspired portrait using the full stroke-engine pipeline,
with session-95 additions:

  - fabritius_contre_jour_pass()                         -- NEW (session 95) Carel Fabritius.
                                                           Three-stage contre-jour technique:
                                                           (1) Pale-ground warm lift -- in
                                                           background zones (lum > 0.52),
                                                           gently brighten toward pale buff
                                                           cream (R+0.028, G+0.025, B+0.015),
                                                           compressing tonal distance between
                                                           figure and field toward the pale
                                                           stone register of The Goldfinch;
                                                           (2) Contre-jour boundary dissolution
                                                           -- in mid-luminance zones (lum
                                                           0.42–0.66), introduce a subtle warm
                                                           luminous fringe (sigma 2.5 px,
                                                           halation_str=0.022), dissolving
                                                           figure/ground boundaries into
                                                           shared ambient light; (3) Straw-
                                                           gold surface register -- in upper
                                                           highlights (lum > 0.70), shift
                                                           toward pale straw-gold (R+0.018,
                                                           G+0.012, B-0.006), lighter and
                                                           more luminous than Rembrandt/Dou
                                                           amber -- the warmth of pale stone
                                                           in afternoon sunlight.

  - straw-gold surface register (straw_r=0.018)         -- SESSION 95 ARTISTIC IMPROVEMENT.
                                                           The straw_r / straw_g parameters
                                                           in fabritius_contre_jour_pass()
                                                           implement Fabritius's signature
                                                           pale straw-gold tonality -- the
                                                           quality most visible in The
                                                           Goldfinch (1654), where the warm
                                                           buff wall and the bird's tawny
                                                           plumage share the same ambient
                                                           light register.  Unlike Dou's
                                                           candle-amber (warm and intimate),
                                                           the straw-gold is lighter, more
                                                           luminous, more open.  It shifts
                                                           the highlight register from
                                                           warm-dark to warm-light: the
                                                           difference between a candle in
                                                           a dark niche and afternoon sun
                                                           on pale stone.  At straw_r=0.018
                                                           (opacity=0.36), the effect is
                                                           intentionally subtle -- a tonal
                                                           quality rather than a colour
                                                           statement.  It interacts with
                                                           the existing Gerrit Dou candle-
                                                           amber from session 94 to produce
                                                           a slightly cooler, more luminous
                                                           warmth in the accumulated surface
                                                           register: the difference between
                                                           a Leiden studio interior and a
                                                           Delft room in afternoon light.
                                                           Fabritius and Dou were working
                                                           in the same tradition at the same
                                                           moment -- Dou in Leiden, Fabritius
                                                           in Delft -- and both died in the
                                                           same decade.  The two passes in
                                                           combination evoke the full register
                                                           of mid-17th-century Dutch light.

  Sessions 94 and earlier (retained):
  - gerrit_dou_fijnschilder_pass()                       -- (session 94) Gerrit Dou
  - candle gradient point source (candle_gradient_str=0.038) -- (session 94 improved)
  - hugo_van_der_goes_expressive_depth_pass()            -- (session 93) Hugo van der Goes
  - impasto_texture_pass (ridge_warmth=0.28)             -- (session 93 improved)
  - antonello_pellucid_flesh_pass()                      -- (session 92) Antonello da Messina
  - Improved subsurface_scatter_pass (shadow_pellucidity=0.05) -- (session 92 improved)
  - caillebotte_perspective_pass()                       -- (session 91) Gustave Caillebotte
  - edge_lost_and_found_pass (soft_halo_strength=0.14)   -- (session 91 improved)
  - hodler_parallelism_pass()                            -- (session 90)
  - atmospheric_depth_pass (horizon_glow_band=0.15)      -- (session 90 improved)
  - spilliaert_vertiginous_void_pass()                   -- (session 89)
  - sfumato_veil_pass (chroma_gate=0.42)                 -- (session 89 improved)
  - redon_luminous_reverie_pass()                        -- (session 88)
  - luminous_haze_pass (spectral_dispersion=0.28)        -- (session 88 improved)
  - whistler_tonal_harmony_pass()                        -- (session 87)
  - cool_atmospheric_recession_pass
    (lateral_horizon_asymmetry=+0.06)                    -- (session 87 improved)
  - carriera_pastel_glow_pass()                          -- (session 86)
  - signorelli_sculptural_vigour_pass()                  -- (session 85)
  - perugino_serene_grace_pass()                         -- (session 84)
  - fra_filippo_lippi_tenerezza_pass()                   -- (session 83)
  - highlight_bloom_pass (chromatic_bloom=True)          -- (session 83 improved)
  - gericault_romantic_turbulence_pass()                 -- (session 82)
  - sfumato_veil_pass (shadow_warm_recovery)             -- (session 82 improved)
  - chardin_granular_intimacy_pass()                     -- (session 81)
  - edge_lost_and_found_pass (gradient_selectivity)      -- (session 81 improved)
  - andrea_del_sarto_golden_sfumato_pass()               -- (session 80)
  - lotto_chromatic_anxiety_pass()                       -- (session 79)
  - rigaud_velvet_drapery_pass()                         -- (session 78)
  - poussin_classical_clarity_pass()                     -- (session 77)
  - steen_warm_vitality_pass()                           -- (session 76)
  - de_hooch_threshold_light_pass()                      -- (session 75)
  - anguissola_intimacy_pass()                           -- (session 73)
  - cool_atmospheric_recession_pass()                    -- (session 74)
  - watteau_crepuscular_reverie_pass()
  - correggio_golden_tenderness_pass()
  - luminous_haze_pass()
  - guido_reni_angelic_grace_pass()
  - david_neoclassical_clarity_pass()
  - ground_tone_recession_pass()
  - skin_zone_temperature_pass()
  - mantegna_sculptural_form_pass()
  - warm_cool_form_duality_pass()
  - patinir_weltlandschaft_pass()
  - crystalline_surface_pass()
  - alma_tadema_marble_luminance_pass()
  - vigee_le_brun_pearlescent_grace_pass()
  - subsurface_scatter_pass()
  - parmigianino_serpentine_elegance_pass()
  - translucent_gauze_pass()
  - old_master_varnish_pass()

Session 95 artistic character:
  The random artist for this session is Carel Fabritius (1622–1654), Rembrandt's
  most gifted pupil and the direct ancestor of Vermeer.  He is the great reverser
  of the Dutch Golden Age: where Rembrandt placed light figures against dark
  grounds, Fabritius placed light figures against light grounds.

  Fabritius studied with Rembrandt in Amsterdam c. 1641–1643, absorbing his
  master's dramatic chiaroscuro and virtuoso brushwork.  But when he settled in
  Delft, he invented something entirely his own: the contre-jour technique, in
  which the figure shares the ambient light of its background rather than
  emerging from theatrical darkness.  His masterpiece The Goldfinch (1654,
  Mauritshuis) is a small trompe-l'oeil panel of such concentrated luminosity
  that it reads as a window rather than a painting — the finch's warm tawny
  plumage set against a pale buff stone wall, held apart only by the most
  delicate temperature differential.

  Fabritius died in the Delft Powder Magazine explosion on 12 October 1654 at
  the age of 32, destroying most of his studio and with it most of his work.
  Fewer than a dozen paintings are securely attributed to him.  He is one of the
  great might-have-beens of art history: had he lived, the Dutch Golden Age
  might have taken a very different direction, toward the luminous, light-flooded
  Delft tradition that Vermeer would develop in his wake.

  In the context of this Mona Lisa portrait, Fabritius contributes the
  contre-jour quality that has been missing from the accumulated passes: the
  sense that the figure exists in the same ambient light as the viewer, rather
  than performing within a staged interior.  By session 95, the portrait has
  accumulated warmth from Rembrandt, Gerrit Dou, Hugo van der Goes, and three
  dozen other Dutch and Flemish masters.  Fabritius's pale-ground warm lift and
  straw-gold surface register gently move the tonal register from dark-warm to
  light-warm — the shift from a Leiden studio candle to Delft afternoon sunlight.

  The session 95 artistic improvement — the straw-gold surface register — is the
  subtlest of any session to date.  At straw_r=0.018, it is less than half the
  strength of the session 94 candle gradient (candle_gradient_str=0.038).  But
  its action is different: where the candle gradient is a spatial warm field
  (more warmth near the upper-right source, cooler at a distance), the straw-gold
  register is a tonal quality (more straw warmth in the brightest highlights,
  fading to nothing in the shadows).  The two work together to give the
  accumulated surface a specificity that previously it lacked: a warm afternoon
  light from the upper right, filtered through the pale stone register of a Delft
  interior.
"""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter

W, H = 780, 1080


# -------------------------------------------------------------------------
# Reference image construction
# (same composition as all prior sessions -- identical portrait)
# -------------------------------------------------------------------------

def make_reference() -> Image.Image:
    """
    Construct a richly coloured synthetic reference encoding the described
    composition.  The reference is blurred before painting so the stroke engine
    works on smooth colour masses rather than hard-edged pixels.
    """
    ref = Image.new("RGB", (W, H), (110, 100, 72))
    px  = ref.load()

    def horizon_y(x: int) -> int:
        """Slight left-right horizon tilt: left side is 8 px higher."""
        return int(0.54 * H - 8 * (x / W - 0.5))

    # ── Background landscape ──────────────────────────────────────────────
    for y in range(H):
        for x in range(W):
            hy = horizon_y(x)
            if y < hy:
                # Sky / upper landscape -- cool blue-grey haze
                t = (hy - y) / max(hy, 1)
                r = int(130 + 60 * t)
                g = int(140 + 50 * t)
                b = int(155 + 60 * t)
            else:
                # Lower landscape -- warm earth tones
                t = (y - hy) / max(H - hy, 1)
                r = int(120 - 30 * t)
                g = int(110 - 25 * t)
                b = int(80  - 20 * t)
            px[x, y] = (
                min(255, max(0, r)),
                min(255, max(0, g)),
                min(255, max(0, b)),
            )

    # Winding path on the left side of background
    for y in range(int(0.52 * H), H):
        t    = (y - 0.52 * H) / (H * 0.48)
        cx   = int(0.18 * W + 0.10 * W * t)
        hw   = max(2, int(6 * (1 - t * 0.6)))
        for dx in range(-hw, hw + 1):
            xx = cx + dx
            if 0 <= xx < W:
                r, g, b = px[xx, y]
                px[xx, y] = (
                    min(255, r + 18),
                    min(255, g + 14),
                    min(255, b + 8),
                )

    # Rocky formation upper-right
    for y in range(int(0.30 * H), int(0.58 * H)):
        for x in range(int(0.62 * W), W):
            dx = (x - 0.62 * W) / (0.38 * W)
            dy = abs(y / H - 0.44)
            if dx * 0.7 + dy * 0.3 < 0.35:
                r, g, b = px[x, y]
                px[x, y] = (
                    min(255, r - 12),
                    min(255, g - 10),
                    min(255, b - 6),
                )

    # ── Figure -- dress (dark blue-green) ────────────────────────────────
    def in_torso(x, y):
        cx   = 0.515 * W
        top  = 0.38 * H
        bot  = H
        rx_t = 0.16 * W
        rx_b = 0.22 * W
        if y < top or y > bot:
            return False
        t  = (y - top) / (bot - top)
        rx = rx_t + (rx_b - rx_t) * t
        return abs(x - cx) <= rx

    for y in range(H):
        for x in range(W):
            if in_torso(x, y):
                # Dark forest-green dress
                r, g, b = px[x, y]
                t = (y - 0.38 * H) / max(H - 0.38 * H, 1)
                dr = int(38 + 10 * t)
                dg = int(52 + 12 * t)
                db = int(42 + 10 * t)
                px[x, y] = (
                    min(255, max(0, dr + r // 6)),
                    min(255, max(0, dg + g // 6)),
                    min(255, max(0, db + b // 6)),
                )

    # ── Face and neck ──────────────────────────────────────────────────────
    face_cx = 0.515 * W
    face_cy = 0.215 * H
    face_rx = 0.105 * W
    face_ry = 0.138 * H
    neck_top = 0.34  * H
    neck_bot = 0.42  * H
    neck_rx  = 0.055 * W

    for y in range(H):
        for x in range(W):
            # Face ellipse
            dx = (x - face_cx) / face_rx
            dy = (y - face_cy) / face_ry
            d2 = dx * dx + dy * dy
            if d2 <= 1.0:
                t   = 1.0 - d2
                fr  = int(192 + 28 * t)
                fg  = int(162 + 22 * t)
                fb  = int(118 + 14 * t)
                px[x, y] = (
                    min(255, fr),
                    min(255, fg),
                    min(255, fb),
                )
                continue
            # Neck
            if neck_top <= y <= neck_bot and abs(x - face_cx) <= neck_rx:
                nt = (y - neck_top) / (neck_bot - neck_top)
                nr = int(185 - 10 * nt)
                ng = int(155 - 12 * nt)
                nb = int(112 - 10 * nt)
                px[x, y] = (min(255, nr), min(255, ng), min(255, nb))

    # ── Hands ──────────────────────────────────────────────────────────────
    hands_cx  = 0.500 * W
    hands_cy  = 0.820 * H
    hands_rx  = 0.115 * W
    hands_ry  = 0.062 * H
    for y in range(H):
        for x in range(W):
            dx = (x - hands_cx) / hands_rx
            dy = (y - hands_cy) / hands_ry
            if dx * dx + dy * dy <= 1.0:
                t  = 1.0 - (dx * dx + dy * dy)
                hr = int(180 + 20 * t)
                hg = int(150 + 16 * t)
                hb = int(108 + 10 * t)
                px[x, y] = (min(255, hr), min(255, hg), min(255, hb))

    # ── Dark veil over hair ──────────────────────────────────────────────
    hair_cx = 0.515 * W
    hair_cy = 0.110 * H
    hair_rx = 0.155 * W
    hair_ry = 0.120 * H
    for y in range(H):
        for x in range(W):
            dx = (x - hair_cx) / hair_rx
            dy = (y - hair_cy) / hair_ry
            if dx * dx + dy * dy <= 1.0:
                r, g, b = px[x, y]
                t = dx * dx + dy * dy
                dark = int(28 + 14 * t)
                px[x, y] = (
                    max(0, r - dark - 12),
                    max(0, g - dark - 10),
                    max(0, b - dark - 8),
                )

    # Blur the reference so stroke engine sees smooth colour masses
    ref = ref.filter(ImageFilter.GaussianBlur(radius=6))
    return ref


def make_figure_mask() -> np.ndarray:
    """
    Return a float32 mask [H, W] in [0, 1] where 1 = figure, 0 = background.
    Figure is a soft-edged region covering the torso and head area.
    """
    mask = np.zeros((H, W), dtype=np.float32)
    cx   = 0.515 * W
    cy   = 0.50  * H
    rx   = 0.26  * W
    ry   = 0.50  * H
    ys, xs = np.ogrid[:H, :W]
    d2  = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2
    mask[d2 <= 1.0] = 1.0
    # Feather edges
    from scipy.ndimage import gaussian_filter
    mask = gaussian_filter(mask, sigma=18.0)
    mask = np.clip(mask / mask.max(), 0.0, 1.0)
    return mask


def paint(out_dir: str = ".") -> str:
    """Run the full session-95 painting pipeline."""
    print("Session 95 -- Mona Lisa portrait")
    print("Random artist: Carel Fabritius (Dutch Golden Age / Delft School, 1622-1654)")
    print("New pass: fabritius_contre_jour_pass()")
    print("  -- Pale-ground warm lift: background brightened toward pale buff cream (lum > 0.52)")
    print("  -- Contre-jour boundary dissolution: warm luminous fringe at figure/ground edges")
    print("  -- Straw-gold surface register: pale straw-gold tint in upper highlights (lum > 0.70)")
    print()
    print("Session 95 artistic improvement: straw-gold surface register in fabritius_contre_jour_pass()")
    print("  Pale straw-gold highlight tint: shifts accumulated warmth from Dou candle-amber")
    print("  to Fabritius afternoon-light -- lighter, more luminous, more open-air.")
    print("  The interplay between session-94 candle gradient and session-95 straw-gold")
    print("  creates the full mid-17th-century Dutch light register: warm point source (Dou)")
    print("  modulated by ambient pale ground (Fabritius).")
    print()

    ref = make_reference()
    p   = Painter(W, H)
    p.set_figure_mask(make_figure_mask())

    # Warm ochre imprimatura
    print("Toning ground (warm ochre imprimatura)...")
    p.tone_ground((0.54, 0.46, 0.28), texture_strength=0.05)

    # Broad underpainting -- establish major colour masses
    print("Underpainting...")
    p.underpainting(ref, stroke_size=55, n_strokes=300)

    # Block in -- first structural pass
    print("Block in (large)...")
    p.block_in(ref, stroke_size=40, n_strokes=550)

    # Session 69: Ground tone recession pass
    print("Ground tone recession pass (session 69)...")
    p.ground_tone_recession_pass(
        horizon_y       = 0.54,
        fg_warm_lift    = 0.032,
        bg_cool_lift    = 0.038,
        transition_band = 0.22,
        opacity         = 0.48,
    )

    # Build form -- mid-range detail passes
    print("Block in (medium)...")
    p.block_in(ref, stroke_size=24, n_strokes=700)
    print("Build form (large)...")
    p.build_form(ref, stroke_size=14, n_strokes=1100)
    print("Build form (detail)...")
    p.build_form(ref, stroke_size=7, n_strokes=800)

    # Session 93 ARTISTIC IMPROVEMENT: impasto_texture_pass with ridge_warmth
    print("Impasto texture pass (session 93 improved -- ridge_warmth=0.28)...")
    p.impasto_texture_pass(
        light_angle       = 315.0,
        ridge_height      = 0.42,
        blur_sigma        = 1.6,
        highlight_opacity = 0.22,
        shadow_opacity    = 0.18,
        ridge_warmth      = 0.28,
    )

    # Patinir weltlandschaft pass (session 66)
    print("Patinir weltlandschaft pass (session 66)...")
    p.patinir_weltlandschaft_pass(
        warm_foreground  = 0.06,
        green_midground  = 0.05,
        cool_distance    = 0.10,
        horizon_near     = 0.52,
        horizon_far      = 0.70,
        transition_blur  = 12.0,
        opacity          = 0.58,
    )

    # Session 74 IMPROVED (session 87): Cool atmospheric recession with lateral asymmetry
    print("Cool atmospheric recession pass (session 74, improved s87 -- lateral_horizon_asymmetry=+0.06)...")
    p.cool_atmospheric_recession_pass(
        horizon_y                 = 0.54,
        cool_strength             = 0.16,
        bright_lift               = 0.06,
        desaturate                = 0.42,
        blur_background           = 0.8,
        feather                   = 0.12,
        opacity                   = 0.64,
        lateral_horizon_asymmetry = 0.06,
    )

    # SESSION 90: Atmospheric depth pass with horizon_glow_band
    print("Atmospheric depth pass (session 90 -- horizon_glow_band=0.15)...")
    p.atmospheric_depth_pass(
        haze_color         = (0.72, 0.78, 0.88),
        desaturation       = 0.48,
        lightening         = 0.32,
        depth_gamma        = 1.6,
        background_only    = True,
        horizon_glow_band  = 0.15,
        horizon_y_frac     = 0.54,
        horizon_band_sigma = 0.08,
    )

    # Parmigianino serpentine elegance pass (session 62)
    print("Parmigianino serpentine elegance pass (session 62)...")
    p.parmigianino_serpentine_elegance_pass(
        porcelain_strength = 0.10,
        lavender_shadow    = 0.08,
        silver_highlight   = 0.06,
        opacity            = 0.36,
    )

    # Vigee Le Brun pearlescent grace pass (session 64)
    print("Vigee Le Brun pearlescent grace pass (session 64)...")
    p.vigee_le_brun_pearlescent_grace_pass(
        rose_bloom_strength = 0.07,
        pearl_highlight     = 0.06,
        shadow_warmth       = 0.04,
        midtone_low         = 0.45,
        midtone_high        = 0.82,
        opacity             = 0.46,
    )

    # Session 65: Subsurface scatter pass (s92 improved)
    print("Subsurface scatter pass (session 65, improved s92 -- shadow_pellucidity=0.05)...")
    p.subsurface_scatter_pass(
        scatter_strength   = 0.10,
        scatter_radius     = 4.0,
        scatter_low        = 0.42,
        scatter_high       = 0.82,
        penumbra_warm      = 0.04,
        shadow_pellucidity = 0.05,
        opacity            = 0.18,
    )

    # Session 66: Alma-Tadema marble luminance pass
    print("Alma-Tadema marble luminance pass (session 66)...")
    p.alma_tadema_marble_luminance_pass(
        marble_warm_strength = 0.05,
        specular_cool_shift  = 0.04,
        specular_thresh      = 0.86,
        translucent_low      = 0.52,
        translucent_high     = 0.86,
        opacity              = 0.22,
    )

    # Session 67: Crystalline surface pass
    print("Crystalline surface pass (session 67)...")
    p.crystalline_surface_pass(
        specular_radius   = 2.5,
        specular_strength = 0.05,
        specular_thresh   = 0.82,
        micro_cool_shift  = 0.03,
        halo_radius       = 6.0,
        halo_warmth       = 0.04,
        halo_thresh       = 0.72,
        opacity           = 0.18,
    )

    # Session 68: Mantegna sculptural form pass
    print("Mantegna sculptural form pass (session 68)...")
    p.mantegna_sculptural_form_pass(
        highlight_lift = 0.05,
        shadow_deepen  = 0.06,
        edge_crisp     = 0.05,
        blur_radius    = 4.0,
        opacity        = 0.28,
    )

    # Session 69: Warm-cool form duality pass
    print("Warm-cool form duality pass (session 69)...")
    p.warm_cool_form_duality_pass(
        warm_strength    = 0.06,
        cool_strength    = 0.08,
        opacity          = 0.30,
    )

    # Session 69: Skin zone temperature pass
    print("Skin zone temperature pass (session 69)...")
    p.skin_zone_temperature_pass(
        face_cx        = 0.515,
        face_cy        = 0.215,
        face_rx        = 0.13,
        face_ry        = 0.18,
        forehead_warm  = 0.03,
        temple_cool    = 0.03,
        nose_pink      = 0.04,
        lip_rose       = 0.03,
        jaw_cool       = 0.02,
        blur_radius    = 8.0,
        opacity        = 0.40,
    )

    # Session 70: Guido Reni angelic grace pass
    print("Guido Reni angelic grace pass (session 70)...")
    p.guido_reni_angelic_grace_pass(
        face_cx       = 0.515,
        face_cy       = 0.215,
        face_rx       = 0.20,
        face_ry       = 0.25,
        pearl_lift    = 0.06,
        pearl_cool    = 0.04,
        cheek_rose    = 0.04,
        lip_rose      = 0.04,
        shadow_violet = 0.03,
        blur_radius   = 8.0,
        opacity       = 0.28,
    )

    # Session 70: David neoclassical clarity pass
    print("David neoclassical clarity pass (session 70)...")
    p.david_neoclassical_clarity_pass(
        figure_cx      = 0.515,
        figure_top     = 0.02,
        figure_bottom  = 0.85,
        figure_rx      = 0.28,
        bg_cool_shift  = 0.05,
        contour_crisp  = 0.04,
        amber_glaze    = 0.03,
        blur_radius    = 6.0,
        opacity        = 0.24,
    )

    # Translucent gauze pass (session 62)
    print("Translucent gauze pass (session 62)...")
    p.translucent_gauze_pass(
        zone_top       = 0.40,
        zone_bottom    = 0.72,
        cool_shift     = 0.04,
        weave_strength = 0.014,
        blur_radius    = 4.0,
        opacity        = 0.28,
    )

    # Session 71: Correggio golden tenderness pass
    print("Correggio golden tenderness pass (session 71)...")
    p.correggio_golden_tenderness_pass(
        midtone_low  = 0.32,
        midtone_high = 0.78,
        gold_lift    = 0.06,
        amber_shadow = 0.04,
        face_cx      = 0.515,
        face_cy      = 0.215,
        face_rx      = 0.140,
        face_ry      = 0.190,
        glow_strength = 0.04,
        blur_radius  = 10.0,
        opacity      = 0.32,
    )

    # Session 71: Luminous haze pass (s88 improved: spectral_dispersion=0.28)
    print("Luminous haze pass (session 71, improved s88 -- spectral_dispersion=0.28)...")
    p.luminous_haze_pass(
        haze_color           = (0.72, 0.68, 0.56),
        haze_warmth          = 0.025,
        haze_opacity         = 0.08,
        soften_radius        = 3.0,
        contrast_damp        = 0.04,
        shadow_lift          = 0.012,
        spectral_dispersion  = 0.28,
        opacity              = 0.24,
    )

    # Session 72: Watteau crepuscular reverie pass
    print("Watteau crepuscular reverie pass (session 72)...")
    p.watteau_crepuscular_reverie_pass(
        amber_shift      = 0.05,
        shadow_lift      = 0.022,
        edge_soften      = 4.0,
        crepuscular_low  = 0.30,
        crepuscular_high = 0.70,
        periphery_darken = 0.06,
        opacity          = 0.30,
    )

    # Session 73: Anguissola intimacy pass
    print("Anguissola intimacy pass (session 73)...")
    p.anguissola_intimacy_pass(
        focus_cx          = 0.515,
        focus_cy          = 0.195,
        focus_radius      = 0.22,
        sharpen_strength  = 0.55,
        eye_cx_offset     = 0.062,
        eye_cy_offset     = -0.022,
        eye_radius        = 0.042,
        lip_cy_offset     = 0.088,
        lip_rx            = 0.055,
        lip_ry            = 0.025,
        periphery_soften  = 0.12,
        warm_ambient      = 0.020,
        opacity           = 0.40,
    )

    # Session 75: Pieter de Hooch threshold light pass
    print("De Hooch threshold light pass (session 75)...")
    p.de_hooch_threshold_light_pass(
        light_x       = 0.10,
        light_width   = 0.48,
        light_falloff = 0.52,
        warm_color    = (0.78, 0.58, 0.28),
        cool_color    = (0.36, 0.46, 0.58),
        opacity       = 0.28,
    )

    # Session 76: Steen warm vitality pass
    print("Steen warm vitality pass (session 76)...")
    p.steen_warm_vitality_pass(
        face_cx          = 0.515,
        face_cy          = 0.215,
        face_rx          = 0.155,
        face_ry          = 0.175,
        amber_lift       = 0.04,
        rose_flush       = 0.03,
        shadow_warmth    = 0.03,
        shadow_thresh    = 0.28,
        highlight_thresh = 0.72,
        blur_radius      = 8.0,
        opacity          = 0.28,
    )

    # Session 77: Poussin classical clarity pass
    print("Poussin classical clarity pass (session 77)...")
    p.poussin_classical_clarity_pass(
        shadow_cool       = 0.06,
        midtone_lift      = 0.04,
        saturation_cap    = 0.80,
        highlight_ivory   = 0.03,
        shadow_thresh     = 0.30,
        highlight_thresh  = 0.74,
        midtone_lo        = 0.30,
        midtone_hi        = 0.68,
        blur_radius       = 6.0,
        opacity           = 0.38,
    )

    # Session 78: Rigaud velvet drapery pass
    print("Rigaud velvet drapery pass (session 78)...")
    p.rigaud_velvet_drapery_pass(
        velvet_thresh   = 0.22,
        velvet_dark     = 0.06,
        velvet_warm_r   = 0.03,
        velvet_warm_g   = 0.01,
        silk_thresh     = 0.78,
        silk_cool_b     = 0.04,
        silk_cool_r     = 0.02,
        skin_r_lo       = 0.45, skin_r_hi = 0.92,
        skin_g_lo       = 0.28, skin_g_hi = 0.80,
        skin_b_hi       = 0.65,
        blur_radius     = 8.0,
        opacity         = 0.32,
    )

    # Session 79: Lotto chromatic anxiety pass
    print("Lotto chromatic anxiety pass (session 79)...")
    p.lotto_chromatic_anxiety_pass(
        flesh_mid_lo    = 0.42,
        flesh_mid_hi    = 0.78,
        cool_b_boost    = 0.018,
        cool_r_reduce   = 0.008,
        eye_left_cx     = 0.478,
        eye_left_cy     = 0.193,
        eye_right_cx    = 0.542,
        eye_right_cy    = 0.193,
        eye_rx          = 0.042,
        eye_ry          = 0.020,
        eye_contrast    = 0.12,
        eye_cool_b      = 0.015,
        eye_cool_r      = 0.008,
        bg_mid_lo       = 0.30,
        bg_mid_hi       = 0.68,
        bg_green_lift   = 0.010,
        bg_blue_lift    = 0.012,
        skin_r_lo       = 0.45, skin_r_hi = 0.92,
        skin_g_lo       = 0.28, skin_g_hi = 0.80,
        skin_b_hi       = 0.65,
        blur_radius     = 7.0,
        opacity         = 0.36,
    )

    # Session 80: Andrea del Sarto golden sfumato pass
    print("Andrea del Sarto golden sfumato pass (session 80)...")
    p.andrea_del_sarto_golden_sfumato_pass(
        flesh_mid_lo    = 0.42,
        flesh_mid_hi    = 0.78,
        gold_r_boost    = 0.022,
        gold_g_boost    = 0.012,
        sfumato_blur    = 2.5,
        edge_grad_lo    = 0.02,
        edge_grad_hi    = 0.10,
        harmony_sat_cap = 0.78,
        harmony_pull    = 0.08,
        skin_r_lo       = 0.45, skin_r_hi = 0.92,
        skin_g_lo       = 0.28, skin_g_hi = 0.80,
        skin_b_hi       = 0.65,
        blur_radius     = 7.0,
        opacity         = 0.40,
    )

    # Session 81: Chardin granular intimacy pass
    print("Chardin granular intimacy pass (session 81)...")
    p.chardin_granular_intimacy_pass(
        dab_radius    = 3.5,
        dab_density   = 0.55,
        mute_strength = 0.14,
        lum_cap       = 0.88,
        lum_cap_str   = 0.22,
        warm_gray_r   = 0.68,
        warm_gray_g   = 0.64,
        warm_gray_b   = 0.54,
        opacity       = 0.30,
        rng_seed      = 42,
    )

    # Session 82: Gericault romantic turbulence pass
    print("Gericault romantic turbulence pass (session 82)...")
    p.gericault_romantic_turbulence_pass(
        shadow_thresh      = 0.32,
        shadow_warm_r      = 0.12,
        shadow_warm_g      = 0.04,
        shadow_cool_b      = 0.10,
        turb_low           = 0.30,
        turb_high          = 0.68,
        turb_strength      = 0.042,
        turb_frequency     = 8.0,
        contrast_midpoint  = 0.48,
        contrast_gain      = 3.2,
        contrast_strength  = 0.10,
        opacity            = 0.36,
    )

    # Session 82 IMPROVED (s89): sfumato veil with shadow_warm_recovery AND chroma_gate
    print("Sfumato veil pass (session 82 improved -- shadow_warm_recovery + s89 chroma_gate=0.42)...")
    p.sfumato_veil_pass(
        reference            = ref,
        n_veils              = 4,
        veil_opacity         = 0.14,
        warmth               = 0.35,
        shadow_warm_recovery = 0.10,
        chroma_gate          = 0.42,
    )

    # Session 83: Fra Filippo Lippi tenerezza pass
    print("Fra Filippo Lippi tenerezza pass (session 83)...")
    p.fra_filippo_lippi_tenerezza_pass(
        flesh_mid_lo    = 0.42,
        flesh_mid_hi    = 0.80,
        rose_r_boost    = 0.038,
        rose_g_boost    = 0.014,
        rose_b_dampen   = 0.022,
        glow_thresh     = 0.74,
        glow_lift       = 0.030,
        glow_blur       = 8.0,
        bg_cool_shift   = 0.018,
        bg_desaturate   = 0.10,
        bg_thresh       = 0.44,
        blur_radius     = 6.0,
        opacity         = 0.34,
    )

    # Session 83 IMPROVED: highlight bloom with chromatic_bloom=True
    print("Highlight bloom pass (session 83 improved -- chromatic_bloom=True)...")
    p.highlight_bloom_pass(
        threshold       = 0.78,
        bloom_sigma     = 6.0,
        bloom_opacity   = 0.18,
        bloom_color     = (0.88, 0.80, 0.62),
        chromatic_bloom = True,
    )

    # Session 84: Perugino serene grace pass
    print("Perugino serene grace pass (session 84)...")
    p.perugino_serene_grace_pass(
        sky_band         = 0.52,
        sky_cool_b       = 0.045,
        sky_desaturate   = 0.24,
        sky_lift         = 0.032,
        shadow_thresh_lo = 0.18,
        shadow_thresh_hi = 0.44,
        shadow_cool_b    = 0.022,
        shadow_cool_r    = 0.010,
        shadow_violet_g  = 0.005,
        midtone_lo       = 0.40,
        midtone_hi       = 0.76,
        smooth_sigma     = 3.5,
        smooth_strength  = 0.14,
        blur_radius      = 7.0,
        opacity          = 0.32,
    )

    # Session 85: Signorelli sculptural vigour pass
    print("Signorelli sculptural vigour pass (session 85)...")
    p.signorelli_sculptural_vigour_pass(
        contour_sigma    = 1.2,
        contour_amount   = 0.48,
        contour_thresh   = 0.04,
        shadow_lo        = 0.10,
        shadow_hi        = 0.42,
        shadow_warm_r    = 0.025,
        shadow_deep_b    = 0.015,
        shadow_deep_g    = 0.006,
        sat_boost_amount = 0.18,
        sat_boost_thresh = 0.22,
        sat_boost_lo     = 0.30,
        sat_boost_hi     = 0.78,
        blur_radius      = 6.0,
        opacity          = 0.36,
    )

    # Session 86: Carriera pastel glow pass
    print("Carriera pastel glow pass (session 86)...")
    p.carriera_pastel_glow_pass(
        skin_brighten_lo   = 0.55,
        skin_brighten_hi   = 0.85,
        warm_pink_r        = 0.026,
        warm_pink_b        = 0.010,
        highlight_sigma    = 3.2,
        highlight_thresh   = 0.88,
        highlight_bloom    = 0.16,
        bg_cool_b          = 0.022,
        bg_cool_r          = 0.010,
        blur_radius        = 5.0,
        opacity            = 0.34,
    )

    # Session 87: Whistler tonal harmony pass
    print("Whistler tonal harmony pass (session 87)...")
    p.whistler_tonal_harmony_pass(
        key_center          = 0.48,
        key_strength        = 0.16,
        dominant_hue_r      = 0.56,
        dominant_hue_g      = 0.57,
        dominant_hue_b      = 0.62,
        hue_drift           = 0.10,
        dissolution_radius  = 0.62,
        dissolution_sigma   = 2.2,
        blur_radius         = 5.0,
        opacity             = 0.40,
    )

    # Session 88: Redon luminous reverie pass
    print("Redon luminous reverie pass (session 88)...")
    p.redon_luminous_reverie_pass(
        void_thresh      = 0.28,
        void_warm_r      = 0.016,
        void_cool_b      = 0.022,
        void_damp_g      = 0.008,
        bloom_thresh     = 0.30,
        bloom_sigma      = 4.5,
        bloom_strength   = 0.18,
        sat_boost_lo     = 0.36,
        sat_boost_hi     = 0.74,
        sat_boost_thresh = 0.16,
        sat_boost_amount = 0.18,
        blur_radius      = 6.0,
        opacity          = 0.42,
    )

    # Session 89: Spilliaert vertiginous void pass
    print("Spilliaert vertiginous void pass (session 89)...")
    p.spilliaert_vertiginous_void_pass(
        void_thresh       = 0.30,
        void_cool_b       = 0.028,
        void_damp_r       = 0.014,
        void_damp_g       = 0.008,
        pale_thresh       = 0.74,
        pale_grey_lift    = 0.016,
        pale_cool_b       = 0.010,
        vignette_strength = 0.16,
        vignette_radius   = 0.58,
        blur_radius       = 9.0,
        opacity           = 0.38,
    )

    # Session 90: Hodler parallelism pass
    print("Hodler parallelism pass (session 90)...")
    p.hodler_parallelism_pass(
        n_bands              = 7,
        band_hardness        = 0.45,
        contour_strength     = 0.22,
        contour_sigma        = 2.0,
        contour_thresh       = 0.05,
        chroma_clarity_lo    = 0.35,
        chroma_clarity_hi    = 0.72,
        chroma_clarity_boost = 0.14,
        chroma_min           = 0.10,
        blur_radius          = 2.5,
        opacity              = 0.30,
    )

    # Session 91: Caillebotte perspective pass
    print("Caillebotte perspective pass (session 91)...")
    p.caillebotte_perspective_pass(
        perspective_strength  = 0.22,
        cobblestone_boost     = 0.06,
        cool_shift            = 0.04,
        axis_sigma_h          = 1.4,
        axis_sigma_v          = 1.2,
        dark_lum_thresh       = 0.42,
        dark_chroma_thresh    = 0.12,
        warm_lum_lo           = 0.32,
        warm_lum_hi           = 0.68,
        blur_radius           = 2.5,
        opacity               = 0.25,
    )

    # Session 92: Antonello da Messina pellucid flesh pass
    print("Antonello da Messina pellucid flesh pass (session 92)...")
    p.antonello_pellucid_flesh_pass(
        shadow_cool_lo      = 0.18,
        shadow_cool_hi      = 0.46,
        shadow_green_lift   = 0.018,
        shadow_blue_lift    = 0.028,
        shadow_red_damp     = 0.010,
        highlight_lo        = 0.74,
        highlight_warm_r    = 0.022,
        highlight_warm_g    = 0.012,
        highlight_cool_b    = 0.008,
        penumbra_lo         = 0.44,
        penumbra_hi         = 0.58,
        penumbra_contrast   = 0.06,
        blur_radius         = 5.0,
        opacity             = 0.38,
    )

    # Session 93: Hugo van der Goes expressive depth pass
    print("Hugo van der Goes expressive depth pass (session 93)...")
    p.hugo_van_der_goes_expressive_depth_pass(
        shadow_lo           = 0.00,
        shadow_hi           = 0.35,
        shadow_amber_r      = 0.022,
        shadow_amber_b      = 0.015,
        midtone_lo          = 0.45,
        midtone_hi          = 0.68,
        midtone_earth_r     = 0.014,
        midtone_earth_g     = 0.007,
        midtone_earth_b     = 0.012,
        void_thresh         = 0.12,
        void_deepen         = 0.012,
        blur_radius         = 5.0,
        opacity             = 0.40,
    )

    # Session 94: Gerrit Dou fijnschilder pass
    print("Gerrit Dou fijnschilder pass (session 94)...")
    p.gerrit_dou_fijnschilder_pass(
        highlight_lo        = 0.62,
        highlight_hi        = 0.95,
        enamel_strength     = 0.55,
        candle_lo           = 0.72,
        candle_amber_r      = 0.022,
        candle_amber_g      = 0.010,
        candle_amber_b      = 0.008,
        candle_x            = 0.72,
        candle_y            = 0.12,
        candle_radius       = 0.65,
        candle_gradient_str = 0.038,
        blur_radius         = 4.0,
        opacity             = 0.38,
    )

    # ── SESSION 95: Carel Fabritius contre-jour pass (NEW) ───────────────────
    # Carel Fabritius (1622–1654) -- Dutch Golden Age / Delft School.
    # Three operations: pale-ground warm lift (background brightened to buff cream),
    # contre-jour boundary dissolution (warm luminous fringe at figure/ground edges),
    # and straw-gold surface register (session 95 artistic improvement --
    # pale straw-gold tint shifts highlights from Dou-amber to Fabritius cream).
    print("Carel Fabritius contre-jour pass (session 95 -- NEW)...")
    p.fabritius_contre_jour_pass(
        buff_lift       = 0.028,   # background warm-buff brightness lift
        buff_bg_lo      = 0.52,    # lower lum threshold for pale-ground brightening
        halation_lo     = 0.42,    # lower lum of contre-jour boundary zone
        halation_hi     = 0.66,    # upper lum of contre-jour boundary zone
        halation_sigma  = 2.5,     # Gaussian sigma for boundary fringe (pixels)
        halation_str    = 0.022,   # peak warm lift in contre-jour boundary zone
        straw_lo        = 0.70,    # lower lum for straw-gold highlight tint
        straw_r         = 0.018,   # SESSION 95 IMPROVEMENT: pale straw-gold R boost
        straw_g         = 0.012,   # G boost (cream, not amber)
        straw_b         = 0.006,   # B slight reduction (damp cool)
        blur_radius     = 3.5,
        opacity         = 0.36,
    )

    # Session 81 IMPROVED (s91): edge_lost_and_found_pass
    print("Edge lost-and-found pass (session 81 improved -- gradient_selectivity=0.65, s91 soft_halo_strength=0.14)...")
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

    # Session 63: Old-master varnish pass
    print("Old-master varnish pass (session 63)...")
    p.old_master_varnish_pass(
        amber_strength  = 0.12,
        edge_darken     = 0.10,
        highlight_desat = 0.06,
        opacity         = 0.28,
    )

    # Final glaze -- pale straw, lighter than session 94's amber
    # Fabritius: the unifying surface register is straw-cream, not deep amber
    print("Final glaze (pale straw cream -- Fabritius register)...")
    p.glaze((0.62, 0.50, 0.22), opacity=0.028)

    # Finish
    print("Finishing (vignette + crackle)...")
    p.finish(vignette=0.50, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s95.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
