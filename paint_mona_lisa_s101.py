"""
paint_mona_lisa_s101.py -- Session 101 portrait painting.

Paints the Mona Lisa-inspired portrait using the full stroke-engine pipeline,
with session-101 additions:

  - toulouse_lautrec                                        -- NEW (session 101)
                                                           Henri de Toulouse-Lautrec
                                                           (1864–1901),
                                                           Post-Impressionism /
                                                           Belle Époque.
                                                           Peinture à l'essence
                                                           -- oil diluted with
                                                           turpentine on raw
                                                           cardboard, producing
                                                           a dry, chalky, matte
                                                           surface quality quite
                                                           unlike traditional
                                                           oil glazing.  Three
                                                           defining effects:
                                                           (1) Matte surface
                                                           desaturation --
                                                           the cardboard-absorbed
                                                           ground kills the oil
                                                           sheen;
                                                           (2) Spidery diagonal
                                                           hatching in mid-tone /
                                                           shadow zones -- the
                                                           draughtsman's mark
                                                           survives in paint;
                                                           (3) Warm-cool graphic
                                                           separation -- warm
                                                           cardboard-ochre zones
                                                           oppose cool blue-grey
                                                           shadows in the flat,
                                                           Japonisme-influenced
                                                           graphic language.

  SESSION 101 ARTISTIC IMPROVEMENT -- graphic dryness against accumulated sheen:

                                                           After 100 sessions
                                                           of oil glazing, the
                                                           surface has acquired
                                                           a rich luminosity
                                                           that could tip into
                                                           sweetness.  Lautrec's
                                                           lesson is the
                                                           corrective: dryness,
                                                           graphic clarity, and
                                                           the psychological
                                                           directness of a
                                                           draughtsman who seizes
                                                           a character in a single
                                                           sustained observation.
                                                           The matte_str (0.11)
                                                           tones the glaze sheen
                                                           without destroying it;
                                                           the hatching adds
                                                           texture in the mid-tone
                                                           veil zones where 100
                                                           sessions of sfumato
                                                           have most dissolved
                                                           form; the warm-cool
                                                           separation recovers the
                                                           temperature contrast
                                                           that the accumulated
                                                           amber glazes have
                                                           compressed.

  Sessions 100 and earlier (retained):
  - masaccio_architectonic_mass_pass()                     -- (session 100) Masaccio
  - bonnard_chromatic_vibration_pass()                     -- (session 99) Pierre Bonnard
  - barocci_petal_flush_pass()                             -- (session 98) Federico Barocci
  - luini_leonardesque_glow_pass()                         -- (session 97) Bernardino Luini
  - sfumato_veil (highlight_ivory_lift=0.06)               -- (session 97 improved)
  - judith_leyster_joyful_light_pass()                     -- (session 96) Judith Leyster
  - fabritius_contre_jour_pass()                           -- (session 95) Carel Fabritius
  - gerrit_dou_fijnschilder_pass()                         -- (session 94) Gerrit Dou
  - candle gradient (candle_gradient_str=0.038)            -- (session 94 improved)
  - hugo_van_der_goes_expressive_depth_pass()              -- (session 93) Hugo van der Goes
  - impasto_texture_pass (ridge_warmth=0.28)               -- (session 93 improved)
  - antonello_pellucid_flesh_pass()                        -- (session 92) Antonello da Messina
  - subsurface_scatter_pass (shadow_pellucidity=0.05)      -- (session 92 improved)
  - caillebotte_perspective_pass()                         -- (session 91) Gustave Caillebotte
  - edge_lost_and_found_pass (soft_halo_strength=0.14)     -- (session 91 improved)
  - hodler_parallelism_pass()                              -- (session 90)
  - atmospheric_depth_pass (horizon_glow_band=0.15)        -- (session 90 improved)
  - spilliaert_vertiginous_void_pass()                     -- (session 89)
  - sfumato_veil_pass (chroma_gate=0.42)                   -- (session 89 improved)
  - redon_luminous_reverie_pass()                          -- (session 88)
  - luminous_haze_pass (spectral_dispersion=0.28)          -- (session 88 improved)
  - whistler_tonal_harmony_pass()                          -- (session 87)
  - cool_atmospheric_recession_pass
    (lateral_horizon_asymmetry=+0.06)                      -- (session 87 improved)
  - carriera_pastel_glow_pass()                            -- (session 86)
  - signorelli_sculptural_vigour_pass()                    -- (session 85)
  - perugino_serene_grace_pass()                           -- (session 84)
  - fra_filippo_lippi_tenerezza_pass()                     -- (session 83)
  - highlight_bloom_pass (chromatic_bloom=True)            -- (session 83 improved)
  - gericault_romantic_turbulence_pass()                   -- (session 82)
  - sfumato_veil_pass (shadow_warm_recovery)               -- (session 82 improved)
  - chardin_granular_intimacy_pass()                       -- (session 81)
  - edge_lost_and_found_pass (gradient_selectivity)        -- (session 81 improved)
  - andrea_del_sarto_golden_sfumato_pass()                 -- (session 80)
  - lotto_chromatic_anxiety_pass()                         -- (session 79)
  - rigaud_velvet_drapery_pass()                           -- (session 78)
  - poussin_classical_clarity_pass()                       -- (session 77)
  - steen_warm_vitality_pass()                             -- (session 76)
  - de_hooch_threshold_light_pass()                        -- (session 75)
  - anguissola_intimacy_pass()                             -- (session 73)
  - cool_atmospheric_recession_pass()                      -- (session 74)
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

Session 101 artistic character:

  The random artist for this session is Henri de Toulouse-Lautrec (1864–1901),
  an aristocrat by birth and a Parisian by vocation, who became the great
  chronicler of Montmartre's nocturnal theatre — the Moulin Rouge, the Divan
  Japonais, the café-concerts where Yvette Guilbert held court and Jane Avril
  danced.  His physical condition (dwarfism resulting from two childhood
  fractures, possibly exacerbated by a genetic disorder) confined him to a world
  that others moved through casually; he observed it instead with an attention
  so concentrated and patient that he captured psychological states in posture
  and gesture that academic painters, painting to flatter, never sought.

  His technique — peinture à l'essence — was invented as a workaround and became
  a style.  He needed a paint that dried fast (the cafés and brothels were not
  studios; he worked in short concentrated sessions), that could be carried and
  stored without the long tacky drying times of traditional oil, and that would
  allow him to draw with the brush rather than paint — to maintain the
  calligraphic, character-defining line that was his most powerful tool.  Thinning
  paint with turpentine until it flowed like ink and applying it to raw cardboard
  gave him all of this.  The cardboard, rather than a liability, became an
  aesthetic collaborator: its warm ochre tone read through every thin layer as
  a unifying mid-ground, and its absorbency meant that the paint dried immediately
  and lay flat, without the three-dimensional surface variation of impasto that
  would have complicated his graphic intentions.

  The influence of Japanese woodblock prints — which Lautrec collected, studied,
  and explicitly imitated in his lithographic poster work — is everywhere in his
  painting: flat colour zones separated by purposeful contours, figures pressing
  close to the picture plane, bold cropping borrowed from photography and ukiyo-e
  alike, and the radical simplification of background into tone rather than
  elaborated space.  These were also the qualities that made his work reproducible
  in lithography, the medium through which his images reached the widest audience
  and for which he is now perhaps best known.

  In the context of this portrait — accumulated over 100 sessions of sfumato,
  atmospheric glazing, and oil-richness — Lautrec's contribution is tonic: the
  dryness of the cardboard surface cuts against accumulated sheen, the hatching
  marks re-introduce the draughtsman's handwriting in the zones most dissolved by
  sfumato, and the warm-cool graphic separation recovers the temperature contrast
  that the amber glazes have gradually compressed.  The result should add
  psychological immediacy — the sense that the figure has been seized in a single
  sustained observation — to the atmospheric depth that the prior sessions have
  built.
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
# (identical composition to all prior sessions)
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
        t    = (y - top) / (bot - top)
        rx   = rx_t + (rx_b - rx_t) * t
        return abs(x - cx) <= rx

    for y in range(H):
        for x in range(W):
            if in_torso(x, y):
                px[x, y] = (28, 52, 45)

    # Neckline trim (amber-gold)
    neck_y = int(0.40 * H)
    neck_cx = int(0.515 * W)
    for y in range(neck_y - 4, neck_y + 4):
        for x in range(int(0.40 * W), int(0.63 * W)):
            if 0 <= x < W and 0 <= y < H:
                dist = abs(y - neck_y)
                if dist < 3:
                    px[x, y] = (160, 118, 52)

    # Semi-transparent gauze wrap over torso
    for y in range(int(0.38 * H), int(0.72 * H)):
        for x in range(int(0.35 * W), int(0.70 * W)):
            if in_torso(x, y):
                r, g, b = px[x, y]
                px[x, y] = (
                    min(255, r + 12),
                    min(255, g + 10),
                    min(255, b + 8),
                )

    # ── Face ──────────────────────────────────────────────────────────────
    face_cx = int(0.515 * W)
    face_cy = int(0.215 * H)
    face_rx = int(0.105 * W)
    face_ry = int(0.155 * H)

    def paint_skin_ellipse(cx, cy, rx, ry, lit_dir=(0.35, -0.70)):
        """Paint skin tone into an ellipse with simple directional shading."""
        for y in range(cy - ry - 2, cy + ry + 2):
            for x in range(cx - rx - 2, cx + rx + 2):
                if not (0 <= x < W and 0 <= y < H):
                    continue
                nx = (x - cx) / rx
                ny = (y - cy) / ry
                d  = math.sqrt(nx * nx + ny * ny)
                if d > 1.0:
                    continue
                # Diffuse shading
                dot    = nx * lit_dir[0] + ny * lit_dir[1]
                light  = 0.55 + 0.45 * max(dot, 0.0)
                falloff = max(0.0, 1.0 - d)
                # Base flesh tone: warm ivory
                base_r = 215
                base_g = 175
                base_b = 130
                r = int(base_r * light)
                g = int(base_g * light)
                b = int(base_b * light)
                # Soften into existing pixels at the ellipse edge
                alpha  = min(1.0, (1.0 - d) * 4.0)
                old_r, old_g, old_b = px[x, y]
                px[x, y] = (
                    min(255, max(0, int(old_r * (1 - alpha) + r * alpha))),
                    min(255, max(0, int(old_g * (1 - alpha) + g * alpha))),
                    min(255, max(0, int(old_b * (1 - alpha) + b * alpha))),
                )

    paint_skin_ellipse(face_cx, face_cy, face_rx, face_ry)

    # Neck
    paint_skin_ellipse(
        int(0.515 * W), int(0.355 * H),
        int(0.058 * W), int(0.085 * H),
        lit_dir=(0.30, -0.60),
    )

    # Décolletage
    paint_skin_ellipse(
        int(0.515 * W), int(0.42 * H),
        int(0.095 * W), int(0.052 * H),
        lit_dir=(0.28, -0.55),
    )

    # ── Hands (lower centre) ──────────────────────────────────────────────
    paint_skin_ellipse(
        int(0.48 * W), int(0.82 * H),
        int(0.082 * W), int(0.048 * H),
        lit_dir=(0.25, -0.50),
    )
    paint_skin_ellipse(
        int(0.53 * W), int(0.855 * H),
        int(0.080 * W), int(0.042 * H),
        lit_dir=(0.25, -0.50),
    )

    # ── Hair and veil ─────────────────────────────────────────────────────
    for y in range(int(0.08 * H), int(0.38 * H)):
        for x in range(int(0.35 * W), int(0.68 * W)):
            nx = (x - 0.515 * W) / (0.105 * W)
            ny = (y - 0.215 * H) / (0.155 * H)
            d  = math.sqrt(nx * nx + ny * ny)
            if d > 0.85 and d < 1.55:
                t = min(1.0, (d - 0.85) / 0.70)
                r, g, b = px[x, y]
                px[x, y] = (
                    int(r * (1 - t) + 52 * t),
                    int(g * (1 - t) + 42 * t),
                    int(b * (1 - t) + 28 * t),
                )

    # Translucent dark veil over crown
    for y in range(int(0.06 * H), int(0.18 * H)):
        for x in range(int(0.38 * W), int(0.65 * W)):
            r, g, b = px[x, y]
            px[x, y] = (
                int(r * 0.72 + 30 * 0.28),
                int(g * 0.72 + 24 * 0.28),
                int(b * 0.72 + 18 * 0.28),
            )

    return ref.filter(ImageFilter.GaussianBlur(radius=3))


def make_figure_mask() -> np.ndarray:
    """
    Return a float32 mask [H, W] in [0, 1] where 1 = figure, 0 = background.
    """
    mask = np.zeros((H, W), dtype=np.float32)
    cx   = 0.515 * W
    cy   = 0.50  * H
    rx   = 0.26  * W
    ry   = 0.50  * H
    ys, xs = np.ogrid[:H, :W]
    d2  = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2
    mask[d2 <= 1.0] = 1.0
    from scipy.ndimage import gaussian_filter
    mask = gaussian_filter(mask, sigma=18.0)
    mask = np.clip(mask / mask.max(), 0.0, 1.0)
    return mask


def paint(out_dir: str = ".") -> str:
    """Run the full session-101 painting pipeline."""
    print("Session 101 -- Mona Lisa portrait")
    print("Random artist: Henri de Toulouse-Lautrec (Post-Impressionism / Belle Époque, 1864–1901)")
    print("New pass: lautrec_essence_pass()")
    print("  -- Matte surface desaturation: turpentine-diluted 'essence' kills oil-glaze sheen")
    print("  -- Spidery diagonal hatching: draughtsman's mark in mid-tone / shadow zones")
    print("  -- Warm-cool graphic separation: cardboard-ochre warmth vs. cool blue-grey shadows")
    print()
    print("Session 101 artistic improvement: graphic dryness against accumulated sfumato sheen")
    print("  Lautrec's peinture à l'essence introduces tonic dryness to the 100-session oil surface.")
    print("  Matte desaturation tones the glaze; hatching re-draws form in dissolved zones;")
    print("  warm-cool separation recovers temperature contrast compressed by amber glazing.")
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
        opacity            = 0.55,
    )

    # Skin zone temperature pass (session 67)
    print("Skin zone temperature pass (session 67)...")
    p.skin_zone_temperature_pass(
        face_cx          = 0.515,
        face_cy          = 0.215,
        face_rx          = 0.160,
        face_ry          = 0.180,
        warm_r           = 0.04,
        warm_g           = 0.02,
        shadow_cool_b    = 0.03,
        shadow_thresh    = 0.35,
        opacity          = 0.52,
    )

    # Warm-cool form duality pass (session 68)
    print("Warm-cool form duality pass (session 68)...")
    p.warm_cool_form_duality_pass(
        warm_thresh  = 0.60,
        cool_thresh  = 0.35,
        warm_color   = (0.78, 0.58, 0.28),
        cool_color   = (0.36, 0.46, 0.58),
        opacity      = 0.28,
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

    # Session 82 IMPROVED (s89, s97): sfumato veil
    print("Sfumato veil pass (s82/s89 improved, s97 -- highlight_ivory_lift=0.06)...")
    p.sfumato_veil_pass(
        reference              = ref,
        n_veils                = 4,
        veil_opacity           = 0.14,
        warmth                 = 0.35,
        shadow_warm_recovery   = 0.10,
        chroma_gate            = 0.42,
        highlight_ivory_lift   = 0.06,
        highlight_ivory_thresh = 0.82,
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

    # Session 95: Carel Fabritius contre-jour pass
    print("Carel Fabritius contre-jour pass (session 95)...")
    p.fabritius_contre_jour_pass(
        shadow_threshold   = 0.32,
        cool_veil_strength = 0.048,
        cool_veil_b_boost  = 0.022,
        edge_sigma         = 1.8,
        edge_threshold     = 0.08,
        bloom_sigma        = 5.5,
        bloom_strength     = 0.055,
        mid_cool_lo        = 0.38,
        mid_cool_hi        = 0.65,
        mid_cool_strength  = 0.015,
        blur_radius        = 3.0,
        opacity            = 0.38,
    )

    # Session 96: Judith Leyster joyful light pass
    print("Judith Leyster joyful light pass (session 96)...")
    p.judith_leyster_joyful_light_pass(
        highlight_lo        = 0.65,
        highlight_amber_r   = 0.028,
        highlight_amber_g   = 0.012,
        highlight_amber_b   = 0.016,
        shadow_hi           = 0.28,
        shadow_warm_r       = 0.018,
        shadow_warm_g       = 0.010,
        shadow_warm_b       = 0.003,
        mid_lo              = 0.35,
        mid_hi              = 0.60,
        mid_amber_r         = 0.016,
        mid_amber_g         = 0.007,
        mid_amber_b         = 0.005,
        blur_radius         = 3.5,
        opacity             = 0.40,
    )

    # Session 97: Bernardino Luini leonardesque glow pass
    print("Bernardino Luini leonardesque glow pass (session 97)...")
    p.luini_leonardesque_glow_pass(
        highlight_lo        = 0.70,
        ivory_r             = 0.028,
        ivory_g             = 0.016,
        ivory_b             = 0.006,
        shadow_hi           = 0.32,
        shadow_violet_b     = 0.018,
        shadow_violet_g     = 0.006,
        shadow_violet_r     = 0.004,
        flesh_lo            = 0.40,
        flesh_hi            = 0.74,
        smooth_sigma        = 1.6,
        smooth_strength     = 0.50,
        blur_radius         = 4.0,
        opacity             = 0.38,
    )

    # Session 98: Federico Barocci petal flush pass
    print("Federico Barocci petal flush pass (session 98)...")
    p.barocci_petal_flush_pass(
        penumbra_lo             = 0.42,
        penumbra_hi             = 0.62,
        rose_r                  = 0.022,
        rose_g                  = 0.008,
        rose_b                  = 0.010,
        bianca_lo               = 0.58,
        bianca_hi               = 0.82,
        bianca_r                = 0.018,
        bianca_g                = 0.012,
        bianca_b                = 0.006,
        edge_dissolve_sigma     = 2.2,
        edge_dissolve_radius    = 0.72,
        edge_dissolve_strength  = 0.35,
        blur_radius             = 4.0,
        opacity                 = 0.38,
    )

    # Session 99: Pierre Bonnard chromatic vibration pass
    print("Pierre Bonnard chromatic vibration pass (session 99)...")
    p.bonnard_chromatic_vibration_pass(
        mid_lo            = 0.28,
        mid_hi            = 0.76,
        warm_amp          = 0.028,
        cool_amp          = 0.022,
        noise_scale       = 18.0,
        noise_octaves     = 4,
        noise_persistence = 0.50,
        blur_radius       = 3.5,
        opacity           = 0.36,
        rng_seed          = 99,
    )

    # Session 100: Masaccio architectonic mass pass
    print("Masaccio architectonic mass pass (session 100 -- CENTENNIAL)...")
    p.masaccio_architectonic_mass_pass(
        shadow_lo         = 0.05,
        shadow_hi         = 0.32,
        shadow_deepen     = 0.05,
        penumbra_lo       = 0.28,
        penumbra_hi       = 0.54,
        penumbra_contrast = 0.08,
        lit_lo            = 0.62,
        earth_r           = 0.018,
        earth_g           = 0.012,
        blur_radius       = 5.0,
        opacity           = 0.28,
    )

    # ── SESSION 101: Toulouse-Lautrec essence pass (NEW) ──────────────────────
    # Henri de Toulouse-Lautrec (1864–1901) -- Post-Impressionism / Belle Époque.
    # Peinture à l'essence: oil diluted with turpentine applied to raw cardboard.
    # Three stages:
    #   (1) Matte surface desaturation (matte_str=0.11): turpentine removes oil sheen
    #   (2) Spidery diagonal hatching (hatch_angle=44°, density=0.24): draughtsman's mark
    #       in mid-tone and shadow zones [lum 0.22–0.62]
    #   (3) Warm-cool graphic separation: mustard-amber in warm zones, blue-grey in cool zones
    # opacity=0.30: adds Lautrec's graphic character without overwhelming 100 sessions of sfumato
    print("Toulouse-Lautrec peinture à l'essence pass (session 101 -- NEW)...")
    p.lautrec_essence_pass(
        matte_str      = 0.11,    # mild desaturation — kills oil-glaze sheen
        hatch_angle    = 44.0,    # near-45° diagonal hatching
        hatch_density  = 0.24,    # sparse — texture not pattern
        hatch_darkness = 0.08,    # gentle darkening per hatch mark
        mid_lo         = 0.22,    # shadow / mid-tone zone bottom
        mid_hi         = 0.62,    # mid-tone zone top (below highlights)
        warm_boost     = 0.06,    # R-channel mustard-amber lift for warm pixels
        cool_boost     = 0.045,   # B-channel blue-grey lift for cool pixels
        blur_radius    = 3.5,     # smooth zone transitions
        opacity        = 0.30,    # adds graphic dryness, respects sfumato beneath
        rng_seed       = 101,     # reproducible hatch pattern
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

    # Final glaze -- warm amber, very light
    print("Final glaze (warm amber)...")
    p.glaze((0.58, 0.44, 0.16), opacity=0.034)

    # Finish
    print("Finishing (vignette + crackle)...")
    p.finish(vignette=0.50, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s101.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
