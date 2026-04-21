"""
paint_mona_lisa_s91.py -- Session 91 portrait painting.

Paints the Mona Lisa-inspired portrait using the full stroke-engine pipeline,
with session-91 additions:

  - franz_marc_prismatic_vitality_pass()             -- NEW (session 91) Franz Marc.
                                                       Three-stage Der Blaue Reiter
                                                       symbolic colour technique:
                                                       (1) symbolic colour intensification
                                                       -- blue-dominant pixels pushed
                                                       toward ultramarine (spiritual
                                                       elevation); warm yellow-dominant
                                                       brights receive cadmium warmth
                                                       push; red mid-darks deepened into
                                                       warm crimson; (2) prismatic form
                                                       bloom -- high-chroma boundaries
                                                       receive a soft Gaussian colour
                                                       aureole, producing stained-glass
                                                       luminosity; (3) prismatic clarity
                                                       lift -- mid-tone saturated zones
                                                       boosted toward their dominant hue.

  - cool_atmospheric_recession_pass
    (warm_ground_glow=0.12)                          -- SESSION 91 ARTISTIC IMPROVEMENT.
                                                       Warm amber glow near the base of
                                                       the recession zone: Renaissance and
                                                       Venetian landscape tradition in
                                                       which the terrain just above the
                                                       horizon glows with warm reflected
                                                       ground-light before the cool aerial
                                                       blue-grey takes over at altitude.
                                                       Bell-curve profiled, peaking at
                                                       ~8% above the per-column horizon,
                                                       adding R↑/G↑/B↓ warmth that fades
                                                       smoothly into the cool zone above.

  Sessions 90 and earlier (retained):
  - hodler_parallelism_pass()                        -- (session 90) Ferdinand Hodler
  - atmospheric_depth_pass (horizon_glow_band=0.15)  -- (session 90 improved)
  - spilliaert_vertiginous_void_pass()               -- (session 89) Léon Spilliaert
  - sfumato_veil_pass (chroma_gate=0.42)             -- (session 89 improved)
  - redon_luminous_reverie_pass()                    -- (session 88) Odilon Redon
  - luminous_haze_pass (spectral_dispersion=0.28)    -- (session 88 improved)
  - whistler_tonal_harmony_pass()                    -- (session 87)
  - cool_atmospheric_recession_pass
    (lateral_horizon_asymmetry=+0.06)                -- (session 87 improved)
  - carriera_pastel_glow_pass()                      -- (session 86)
  - signorelli_sculptural_vigour_pass()              -- (session 85)
  - perugino_serene_grace_pass()                     -- (session 84)
  - fra_filippo_lippi_tenerezza_pass()               -- (session 83)
  - highlight_bloom_pass (chromatic_bloom=True)      -- (session 83 improved)
  - gericault_romantic_turbulence_pass()             -- (session 82)
  - sfumato_veil_pass (shadow_warm_recovery)         -- (session 82 improved)
  - chardin_granular_intimacy_pass()                 -- (session 81)
  - edge_lost_and_found_pass (gradient_selectivity)  -- (session 81 improved)
  - andrea_del_sarto_golden_sfumato_pass()           -- (session 80)
  - lotto_chromatic_anxiety_pass()                   -- (session 79)
  - rigaud_velvet_drapery_pass()                     -- (session 78)
  - poussin_classical_clarity_pass()                 -- (session 77)
  - steen_warm_vitality_pass()                       -- (session 76)
  - de_hooch_threshold_light_pass()                  -- (session 75)
  - anguissola_intimacy_pass()                       -- (session 73)
  - cool_atmospheric_recession_pass()                -- (session 74)
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

Session 91 artistic character:
  The random artist for this session is Franz Marc (1880-1916), co-founder of
  Der Blaue Reiter (The Blue Rider) — the Munich-based German Expressionist
  movement that made colour itself the carrier of spiritual meaning.  Marc's
  central conviction was that blue carries spirituality, yellow gentleness,
  and red violence — not as symbols attached from outside, but as inherent
  properties of the colours themselves.

  Marc's contribution to the accumulated portrait is prismatic vitality.
  After twenty sessions, the composition is tonally rich, sfumato-dissolved,
  and atmospherically recessive.  What Marc adds is a clarification of the
  colour-temperature zones: the deep ultramarine of the background recession
  is pushed slightly further toward pure spiritual blue; the warm ivory-amber
  passages of the figure's lit skin and the horizon glow are warmed toward
  Marc's cadmium yellow; the shadow passages of the dress receive a barely
  perceptible deepening into warm crimson.  The prismatic form bloom adds the
  subtle stained-glass luminosity Marc's pure colour planes are famous for —
  a soft aureole at the boundary between the cool landscape and the warm figure,
  where his spiritual blue meets the earthly ochre of the Mona Lisa's garments.

  Applied at opacity 0.28 and with conservative push values, the effect is
  very gentle — a slight spiritual intensification of colour temperature
  contrast, not a transformation of the portrait's sfumato character.  Marc
  himself saw his colour as a spiritual overtone resonating beneath the
  visible surface of things; at this opacity his pass does precisely that.

  The session 91 artistic improvement — warm_ground_glow in
  cool_atmospheric_recession_pass() — resolves a subtle inadequacy in the
  existing atmospheric pipeline.  The prior formulation applied cool haze
  uniformly above the horizon, treating the near-horizon terrain as the
  onset of the cool zone.  But in Renaissance painting — and visually in the
  Mona Lisa itself — the terrain just above the horizon is not the coolest
  area; it is specifically warm.  The cool aerial blue-grey dominates at
  altitude, but at the horizon the ground reflects warm golden light back into
  the lower atmosphere, creating the characteristic warm/cool oscillation that
  gives the Mona Lisa background its atmospheric richness.  warm_ground_glow
  adds a bell-curve warm amber push centred ~8% above the horizon that
  gracefully transitions into the cool zone above, physically motivated by
  the Venetian observation that ground-reflected light warms the base of the
  atmosphere.
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
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # Sky / upper background: pale blue-grey, lightening toward the top
    sky_top    = np.array([0.72, 0.74, 0.78])
    sky_bottom = np.array([0.42, 0.48, 0.58])
    sky_band   = int(H * 0.62)
    for y in range(sky_band):
        t = y / sky_band
        ref[y, :] = sky_top * (1 - t) + sky_bottom * t

    # Landscape below sky -- left side sits higher than right (Mona Lisa asymmetry)
    def horizon_y(x: int) -> int:
        t = x / W
        return int(H * (0.50 + t * 0.06))

    for x in range(W):
        hy = horizon_y(x)
        for y in range(hy, H):
            t = (y - hy) / (H - hy)
            far  = np.array([0.28, 0.30, 0.24])
            near = np.array([0.18, 0.14, 0.09])
            ref[y, x] = far * (1 - t) + near * t

    # Rocky crags -- left side (more prominent, higher placement)
    crag_c  = np.array([0.35, 0.33, 0.28])
    crag_sh = np.array([0.18, 0.17, 0.14])
    rock_formations = [
        (int(W * 0.10), int(H * 0.42), int(W * 0.07), int(H * 0.06)),
        (int(W * 0.22), int(H * 0.39), int(W * 0.06), int(H * 0.08)),
        (int(W * 0.08), int(H * 0.37), int(W * 0.05), int(H * 0.05)),
    ]
    for cx, cy, rx, ry in rock_formations:
        for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
            for x in range(max(0, cx - rx), min(W, cx + rx + 1)):
                dx = (x - cx) / rx
                dy = (y - cy) / ry
                d = dx * dx + dy * dy
                if d <= 1.05:
                    shade = max(0, -dx * 0.5)
                    c = crag_c * (1 - shade * 0.5) + crag_sh * shade * 0.5
                    fade = max(0.0, 1.0 - (d - 0.82) / 0.23) if d > 0.82 else 1.0
                    ref[y, x] = ref[y, x] * (1 - fade) + c * fade

    # Rocky crags -- right side (lower, more distant)
    right_crags = [
        (int(W * 0.82), int(H * 0.50), int(W * 0.08), int(H * 0.05)),
        (int(W * 0.92), int(H * 0.47), int(W * 0.07), int(H * 0.06)),
    ]
    crag_r = np.array([0.38, 0.36, 0.30])
    for cx, cy, rx, ry in right_crags:
        for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
            for x in range(max(0, cx - rx), min(W, cx + rx + 1)):
                dx = (x - cx) / rx
                dy = (y - cy) / ry
                d = dx * dx + dy * dy
                if d <= 1.05:
                    fade = max(0.0, 1.0 - (d - 0.82) / 0.23) if d > 0.82 else 1.0
                    ref[y, x] = ref[y, x] * (1 - fade) + crag_r * fade

    # Winding path on left
    path_c = np.array([0.50, 0.46, 0.34])
    for seg in range(40):
        t = seg / 40.0
        px = int(W * (0.04 + t * 0.18 + 0.06 * math.sin(t * math.pi * 2.5)))
        py = int(H * (0.76 - t * 0.28))
        pw = max(3, int(W * 0.028 * (1 - t * 0.55)))
        for dy in range(-pw, pw + 1):
            for dx in range(-pw, pw + 1):
                fy, fx = py + dy, px + dx
                if 0 <= fy < H and 0 <= fx < W:
                    d_path = math.sqrt(dx * dx + dy * dy) / pw
                    if d_path <= 1.0:
                        fm = max(0.0, 1.0 - d_path * 0.8) * 0.6
                        ref[fy, fx] = ref[fy, fx] * (1 - fm) + path_c * fm

    # River / water in mid-distance
    river_y  = int(H * 0.46)
    river_h  = int(H * 0.022)
    river_xL = int(W * 0.25)
    river_xR = int(W * 0.44)
    river_c  = np.array([0.42, 0.52, 0.64])
    for y in range(river_y - river_h, river_y + river_h):
        if 0 <= y < H:
            for x in range(river_xL, river_xR):
                if 0 <= x < W:
                    et = max(0.0, 1.0 - abs(y - river_y) / river_h)
                    ref[y, x] = ref[y, x] * (1 - et * 0.62) + river_c * et * 0.62

    # Sparse vegetation
    veg_c = np.array([0.22, 0.28, 0.16])
    for veg in [
        (int(W * 0.16), int(H * 0.55), int(W * 0.03), int(H * 0.04)),
        (int(W * 0.30), int(H * 0.57), int(W * 0.02), int(H * 0.03)),
        (int(W * 0.85), int(H * 0.56), int(W * 0.03), int(H * 0.04)),
    ]:
        cx, cy, rx, ry = veg
        for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
            for x in range(max(0, cx - rx), min(W, cx + rx + 1)):
                dx = (x - cx) / rx
                dy = (y - cy) / ry
                d = dx * dx + dy * dy
                if d <= 1.0:
                    fade = max(0.0, 1.0 - (d - 0.75) / 0.25) if d > 0.75 else 1.0
                    ref[y, x] = ref[y, x] * (1 - fade * 0.7) + veg_c * fade * 0.7

    # -------------------------------------------------------------------------
    # Figure: dark dress (forest-green / blue-black) occupying lower 2/3
    # -------------------------------------------------------------------------
    dress_c = np.array([0.10, 0.13, 0.10])   # dark forest-green dress
    for y in range(int(H * 0.38), H):
        for x in range(int(W * 0.16), int(W * 0.84)):
            t_body = max(0.0, min(1.0, (y - H * 0.38) / (H * 0.28)))
            half_w = int(W * (0.24 + 0.10 * t_body))
            cx = W // 2
            if abs(x - cx) <= half_w:
                dist_edge = (half_w - abs(x - cx)) / half_w
                fade = min(1.0, dist_edge * 4.0)
                ref[y, x] = ref[y, x] * (1 - fade) + dress_c * fade

    # Neckline trim -- thin warm gold
    neck_y   = int(H * 0.40)
    neck_c   = np.array([0.72, 0.60, 0.28])
    for y in range(neck_y - 4, neck_y + 5):
        for x in range(int(W * 0.33), int(W * 0.67)):
            if 0 <= y < H and 0 <= x < W:
                ref[y, x] = ref[y, x] * 0.4 + neck_c * 0.6

    # -------------------------------------------------------------------------
    # Skin: face, neck, hands
    # -------------------------------------------------------------------------
    skin_hi   = np.array([0.88, 0.76, 0.58])   # lit highlight
    skin_mid  = np.array([0.76, 0.60, 0.42])   # warm midtone
    skin_shad = np.array([0.52, 0.38, 0.24])   # warm shadow

    def paint_skin_ellipse(cx, cy, rx, ry, lit_dir=(0.35, -0.70)):
        """Fill an ellipse with skin, shaded from lit_dir."""
        for y in range(max(0, cy - ry - 4), min(H, cy + ry + 5)):
            for x in range(max(0, cx - rx - 4), min(W, cx + rx + 5)):
                dx = (x - cx) / rx
                dy = (y - cy) / ry
                d = dx * dx + dy * dy
                if d <= 1.08:
                    shade = max(0.0, min(1.0, dx * lit_dir[0] + dy * lit_dir[1]))
                    c = skin_hi * (1 - shade) * 0.5 + skin_mid * 0.5 + skin_shad * shade * 0.5
                    fade = max(0.0, 1.0 - (d - 0.85) / 0.23) if d > 0.85 else 1.0
                    ref[y, x] = ref[y, x] * (1 - fade) + np.clip(c, 0, 1) * fade

    # Face
    face_cx = W // 2 + 8
    face_cy = int(H * 0.215)
    face_rx = int(W * 0.125)
    face_ry = int(H * 0.168)
    paint_skin_ellipse(face_cx, face_cy, face_rx, face_ry)

    # Neck
    neck_cx = W // 2 + 5
    neck_top = int(H * 0.370)
    neck_bot = int(H * 0.415)
    neck_rx  = int(W * 0.048)
    for y in range(neck_top, neck_bot):
        for x in range(neck_cx - neck_rx, neck_cx + neck_rx):
            if 0 <= x < W:
                ref[y, x] = skin_mid

    # Hands in lower center
    hand_cx = W // 2
    hand_cy = int(H * 0.78)
    hand_rx = int(W * 0.15)
    hand_ry = int(H * 0.06)
    paint_skin_ellipse(hand_cx, hand_cy, hand_rx, hand_ry, lit_dir=(0.2, -0.5))

    # -------------------------------------------------------------------------
    # Dark veil / hair
    # -------------------------------------------------------------------------
    hair_c   = np.array([0.14, 0.11, 0.08])
    hair_mid = np.array([0.22, 0.18, 0.12])

    # Central parting -- hair falls on both sides
    hair_top = face_cy - face_ry - 8
    for side in [-1, 1]:
        for seg in range(30):
            t = seg / 30.0
            hx = face_cx + side * int(face_rx * (0.3 + t * 0.7))
            hy = hair_top + int(face_ry * t * 1.5)
            for dy in range(-18, 19):
                for dx in range(-12, 13):
                    fy, fx = hy + dy, hx + dx
                    if 0 <= fy < H and 0 <= fx < W:
                        d = math.sqrt(dx * dx * 0.6 + dy * dy)
                        if d < 16:
                            fade = max(0.0, 1.0 - d / 16.0) * 0.80
                            ref[fy, fx] = ref[fy, fx] * (1 - fade) + hair_c * fade

    # Dark translucent veil draped over crown
    veil_y = hair_top - 12
    for y in range(max(0, veil_y - 20), min(H, face_cy + face_ry // 2)):
        for x in range(int(W * 0.25), int(W * 0.75)):
            if 0 <= y < H:
                dist_top = max(0, y - veil_y) / (face_ry * 0.6)
                veil_str = max(0.0, 1.0 - dist_top) * 0.55
                ref[y, x] = ref[y, x] * (1 - veil_str) + hair_mid * veil_str

    # Translucent gauze wrap over shoulder
    gauze_c = np.array([0.64, 0.58, 0.48])
    for y in range(int(H * 0.40), int(H * 0.72)):
        for x in range(int(W * 0.20), int(W * 0.52)):
            dy_f = (y - H * 0.40) / (H * 0.32)
            dx_f = (x - W * 0.20) / (W * 0.32)
            fade = max(0.0, 1.0 - (dy_f + dx_f) * 0.7) * 0.38
            ref[y, x] = ref[y, x] * (1 - fade) + gauze_c * fade

    # -------------------------------------------------------------------------
    # Facial features (subtle)
    # -------------------------------------------------------------------------
    eye_c = np.array([0.12, 0.10, 0.08])
    for eye_ox, eye_oy in [(-int(W * 0.048), -int(H * 0.022)),
                            (+int(W * 0.048), -int(H * 0.022))]:
        ex, ey = face_cx + eye_ox, face_cy + eye_oy
        for dy in range(-9, 10):
            for dx in range(-22, 23):
                if 0 <= ey + dy < H and 0 <= ex + dx < W:
                    d = (dx / 18.0) ** 2 + (dy / 7.0) ** 2
                    if d <= 1.0:
                        fade = max(0.0, 1.0 - d) * 0.85
                        ref[ey + dy, ex + dx] = (
                            ref[ey + dy, ex + dx] * (1 - fade) + eye_c * fade
                        )

    # Lips -- small, softly curved, slightly warm rose
    lip_c = np.array([0.74, 0.50, 0.40])
    lip_cx, lip_cy = face_cx + 2, face_cy + int(face_ry * 0.52)
    for dy in range(-9, 10):
        for dx in range(-22, 23):
            if 0 <= lip_cy + dy < H and 0 <= lip_cx + dx < W:
                d = (dx / 16.0) ** 2 + (dy / 6.5) ** 2
                if d <= 1.0:
                    fade = max(0.0, 1.0 - d) * 0.68
                    ref[lip_cy + dy, lip_cx + dx] = (
                        ref[lip_cy + dy, lip_cx + dx] * (1 - fade) + lip_c * fade
                    )

    # Convert to PIL and apply strong Gaussian blur to smooth reference
    ref_uint8 = np.clip(ref * 255, 0, 255).astype(np.uint8)
    ref_img   = Image.fromarray(ref_uint8)
    ref_img   = ref_img.filter(ImageFilter.GaussianBlur(radius=18))
    return ref_img


# -------------------------------------------------------------------------
# Figure mask (binary silhouette)
# -------------------------------------------------------------------------

def make_figure_mask() -> np.ndarray:
    """
    Returns a float32 (H, W) mask: 1.0 = figure, 0.0 = background.
    Covers the figure from collar to bottom of frame.
    """
    mask = np.zeros((H, W), dtype=np.float32)

    # Face ellipse
    face_cx = W // 2 + 8
    face_cy = int(H * 0.215)
    face_rx = int(W * 0.138)
    face_ry = int(H * 0.185)
    for y in range(max(0, face_cy - face_ry - 10), min(H, face_cy + face_ry + 10)):
        for x in range(max(0, face_cx - face_rx - 10), min(W, face_cx + face_rx + 10)):
            dx = (x - face_cx) / face_rx
            dy = (y - face_cy) / face_ry
            if dx * dx + dy * dy <= 1.1:
                mask[y, x] = 1.0

    # Body (trapezoid widening toward bottom)
    for y in range(int(H * 0.36), H):
        t = (y - H * 0.36) / (H - H * 0.36)
        hw = int(W * (0.20 + 0.14 * t))
        cx = W // 2
        x0 = max(0, cx - hw)
        x1 = min(W, cx + hw)
        mask[y, x0:x1] = 1.0

    # Smooth the mask boundary
    from scipy.ndimage import gaussian_filter
    mask = np.clip(gaussian_filter(mask, sigma=12.0), 0.0, 1.0)
    return mask


def paint(out_dir: str = ".") -> str:
    """Run the full session-91 painting pipeline."""
    print("Session 91 -- Mona Lisa portrait")
    print("Random artist: Franz Marc (German Expressionism / Der Blaue Reiter, 1880-1916)")
    print("New pass: franz_marc_prismatic_vitality_pass()")
    print("  -- symbolic colour intensification: blue->ultramarine, bright warm->cadmium")
    print("  --   yellow, red mid-darks->warm crimson")
    print("  -- prismatic form bloom: stained-glass luminous aureole at colour boundaries")
    print("  -- prismatic clarity lift: mid-tone saturation boost for unmixed-pigment vibrancy")
    print()
    print("Session 91 artistic improvement: warm_ground_glow in cool_atmospheric_recession_pass()")
    print("  Renaissance landscape tradition: terrain just above horizon glows with warm")
    print("  amber ground-reflected light before cool aerial blue-grey takes over above.")
    print("  Bell-curve warm push centred ~8% above the horizon, fading smoothly upward.")
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

    # SESSION 91 IMPROVED: Cool atmospheric recession with warm_ground_glow + lateral asymmetry
    print("Cool atmospheric recession pass (s74+s87+s91 -- lateral_horizon_asymmetry=+0.06, "
          "warm_ground_glow=0.12)...")
    p.cool_atmospheric_recession_pass(
        horizon_y                 = 0.54,
        cool_strength             = 0.16,
        bright_lift               = 0.06,
        desaturate                = 0.42,
        blur_background           = 0.8,
        feather                   = 0.12,
        opacity                   = 0.64,
        lateral_horizon_asymmetry = 0.06,
        warm_ground_glow          = 0.12,   # SESSION 91: warm amber near horizon
    )

    # Session 90: Atmospheric depth pass with horizon_glow_band
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

    # Vigée Le Brun pearlescent grace pass (session 64)
    print("Vigee Le Brun pearlescent grace pass (session 64)...")
    p.vigee_le_brun_pearlescent_grace_pass(
        rose_bloom_strength = 0.07,
        pearl_highlight     = 0.06,
        shadow_warmth       = 0.04,
        midtone_low         = 0.45,
        midtone_high        = 0.82,
        opacity             = 0.46,
    )

    # Session 65: Subsurface scatter pass
    print("Subsurface scatter pass (session 65)...")
    p.subsurface_scatter_pass(
        scatter_strength = 0.10,
        scatter_radius   = 4.0,
        scatter_low      = 0.42,
        scatter_high     = 0.82,
        penumbra_warm    = 0.04,
        opacity          = 0.18,
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
        facet_scale     = 0.03,
        shimmer_amount  = 0.04,
        cold_highlight  = 0.03,
        opacity         = 0.18,
    )

    # Session 68: Translucent gauze pass
    print("Translucent gauze pass (session 68)...")
    p.translucent_gauze_pass(
        gauze_opacity   = 0.52,
        warm_undertone  = 0.04,
        cool_shadow     = 0.03,
        thread_scale    = 0.008,
        opacity         = 0.26,
    )

    # Correggio golden tenderness pass (session 69)
    print("Correggio golden tenderness pass (session 69)...")
    p.correggio_golden_tenderness_pass(
        gold_warmth      = 0.06,
        sfumato_softness = 0.04,
        shadow_depth     = 0.05,
        opacity          = 0.38,
    )

    # Warm-cool form duality pass (session 70)
    print("Warm-cool form duality pass (session 70)...")
    p.warm_cool_form_duality_pass(
        warm_shift  = 0.04,
        cool_shift  = 0.04,
        opacity     = 0.38,
    )

    # Mantegna sculptural form pass (session 70)
    print("Mantegna sculptural form pass (session 70)...")
    p.mantegna_sculptural_form_pass(
        shadow_cool_b  = 0.04,
        light_warm_r   = 0.04,
        contour_darken = 0.06,
        opacity        = 0.30,
    )

    # Skin zone temperature pass (session 71)
    print("Skin zone temperature pass (session 71)...")
    p.skin_zone_temperature_pass(
        forehead_cool   = 0.022,
        cheek_warm      = 0.028,
        chin_neutral    = 0.010,
        temple_cool     = 0.018,
        opacity         = 0.38,
    )

    # David neoclassical clarity pass (session 72)
    print("David neoclassical clarity pass (session 72)...")
    p.david_neoclassical_clarity_pass(
        contour_strength  = 0.08,
        midtone_flatten   = 0.05,
        highlight_clarify = 0.04,
        opacity           = 0.30,
    )

    # Guido Reni angelic grace pass (session 73)
    print("Guido Reni angelic grace pass (session 73)...")
    p.guido_reni_angelic_grace_pass(
        pearl_lift     = 0.06,
        shadow_deepen  = 0.05,
        opacity        = 0.34,
    )

    # Session 74: Cool atmospheric recession base (ALSO IMPROVED in s87 and s91)
    # (already called above as the session 91 version with warm_ground_glow)

    # Session 75: de Hooch threshold light pass
    print("de Hooch threshold light pass (session 75)...")
    p.de_hooch_threshold_light_pass(
        light_x        = 0.12,
        light_width    = 0.48,
        light_falloff  = 0.52,
        warm_strength  = 0.06,
        cool_shadow    = 0.04,
        opacity        = 0.32,
    )

    # Session 76: Steen warm vitality pass
    print("Steen warm vitality pass (session 76)...")
    p.steen_warm_vitality_pass(
        flush_strength  = 0.05,
        amber_glow      = 0.04,
        opacity         = 0.30,
    )

    # Session 77: Poussin classical clarity pass
    print("Poussin classical clarity pass (session 77)...")
    p.poussin_classical_clarity_pass(
        clarity_strength  = 0.06,
        contour_amount    = 0.04,
        opacity           = 0.28,
    )

    # Session 78: Rigaud velvet drapery pass
    print("Rigaud velvet drapery pass (session 78)...")
    p.rigaud_velvet_drapery_pass(
        velvet_depth   = 0.08,
        sheen_lift     = 0.06,
        opacity        = 0.32,
    )

    # Session 79: Lotto chromatic anxiety pass
    print("Lotto chromatic anxiety pass (session 79)...")
    p.lotto_chromatic_anxiety_pass(
        anxiety_strength  = 0.06,
        cool_shadow_push  = 0.04,
        opacity           = 0.28,
    )

    # Session 80: Andrea del Sarto golden sfumato pass
    print("Andrea del Sarto golden sfumato pass (session 80)...")
    p.andrea_del_sarto_golden_sfumato_pass(
        golden_warmth   = 0.05,
        sfumato_blend   = 0.06,
        opacity         = 0.34,
    )

    # Session 81: Chardin granular intimacy pass
    print("Chardin granular intimacy pass (session 81)...")
    p.chardin_granular_intimacy_pass(
        grain_scale    = 0.008,
        grain_strength = 0.04,
        muted_warmth   = 0.03,
        opacity        = 0.28,
    )

    # Session 82: Géricault romantic turbulence pass
    print("Gericault romantic turbulence pass (session 82)...")
    p.gericault_romantic_turbulence_pass(
        turbulence_strength = 0.06,
        shadow_depth        = 0.05,
        opacity             = 0.28,
    )

    # Session 83: Fra Filippo Lippi tenerezza pass
    print("Fra Filippo Lippi tenerezza pass (session 83)...")
    p.fra_filippo_lippi_tenerezza_pass(
        tenderness_lift  = 0.06,
        rose_blush       = 0.04,
        opacity          = 0.30,
    )

    # Session 83 IMPROVED: Highlight bloom with chromatic bloom
    print("Highlight bloom pass (session 83 improved -- chromatic_bloom=True)...")
    p.highlight_bloom_pass(
        bloom_strength  = 0.08,
        bloom_radius    = 3.5,
        bloom_thresh    = 0.82,
        chromatic_bloom = True,
        opacity         = 0.30,
    )

    # Session 84: Perugino serene grace pass
    print("Perugino serene grace pass (session 84)...")
    p.perugino_serene_grace_pass(
        serenity_lift  = 0.06,
        sky_blue_push  = 0.05,
        opacity        = 0.30,
    )

    # Session 85: Signorelli sculptural vigour pass
    print("Signorelli sculptural vigour pass (session 85)...")
    p.signorelli_sculptural_vigour_pass(
        contour_sigma     = 1.2,
        contour_amount    = 0.40,
        contour_thresh    = 0.04,
        shadow_lo         = 0.10,
        shadow_hi         = 0.42,
        shadow_warm_r     = 0.024,
        shadow_deep_b     = 0.014,
        shadow_deep_g     = 0.006,
        sat_boost_amount  = 0.18,
        sat_boost_thresh  = 0.22,
        sat_boost_lo      = 0.30,
        sat_boost_hi      = 0.78,
        blur_radius       = 6.0,
        opacity           = 0.34,
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

    # ── SESSION 91: Franz Marc prismatic vitality pass (NEW) ──────────────────
    # Franz Marc (1880–1916) — German Expressionist / Der Blaue Reiter.
    # Three operations: symbolic colour intensification, prismatic form bloom,
    # prismatic clarity lift.  Applied at low opacity to add spiritual colour
    # temperature contrast without overwhelming the sfumato character.
    print("Franz Marc prismatic vitality pass (session 91 -- NEW)...")
    p.franz_marc_prismatic_vitality_pass(
        blue_push          = 0.14,   # gentle ultramarine lift on background blues
        yellow_push        = 0.10,   # warm golden push on bright ivory highlights
        red_deepen         = 0.08,   # subtle crimson deepening in warm shadow masses
        bloom_thresh       = 0.42,   # activate bloom only on well-saturated areas
        bloom_sigma        = 3.0,
        bloom_strength     = 0.12,   # soft luminous aureole at colour boundaries
        sat_boost_lo       = 0.32,
        sat_boost_hi       = 0.74,
        sat_boost_amount   = 0.18,
        sat_boost_thresh   = 0.16,
        blur_radius        = 3.5,
        opacity            = 0.28,   # gentle: Marc's spirit as an undertone
    )

    # Session 88 IMPROVED: Luminous haze pass with spectral dispersion
    print("Luminous haze pass (session 88 improved -- spectral_dispersion=0.28)...")
    p.luminous_haze_pass(
        soften_radius       = 1.8,
        haze_warmth         = 0.04,
        haze_cool           = 0.02,
        background_only     = True,
        spectral_dispersion = 0.28,
        opacity             = 0.42,
    )

    # Session 89 IMPROVED: Sfumato veil with chroma_gate
    print("Sfumato veil pass (session 89 improved -- chroma_gate=0.42)...")
    p.sfumato_veil_pass(
        veil_strength  = 0.28,
        veil_radius    = 2.5,
        shadow_low     = 0.22,
        shadow_high    = 0.52,
        chroma_gate    = 0.42,
        opacity        = 0.46,
    )

    # Session 73: Anguissola intimacy pass
    print("Anguissola intimacy pass (session 73)...")
    p.anguissola_intimacy_pass(
        warmth_strength  = 0.05,
        softness         = 0.04,
        opacity          = 0.30,
    )

    # Claude Lorrain golden light pass
    print("Claude Lorrain golden light pass...")
    p.claude_lorrain_golden_light_pass(
        gold_strength  = 0.06,
        sky_haze       = 0.04,
        opacity        = 0.32,
    )

    # Watteau crepuscular reverie pass
    print("Watteau crepuscular reverie pass...")
    p.watteau_crepuscular_reverie_pass(
        dusk_warmth   = 0.04,
        shadow_cool   = 0.03,
        opacity       = 0.28,
    )

    # Session 81 IMPROVED: edge_lost_and_found_pass with gradient_selectivity
    print("Edge lost-and-found pass (session 81 improved -- gradient_selectivity=0.65)...")
    p.edge_lost_and_found_pass(
        focal_xy             = (0.515, 0.195),
        found_radius         = 0.28,
        found_sharpness      = 0.48,
        lost_blur            = 2.0,
        strength             = 0.34,
        figure_only          = True,
        gradient_selectivity = 0.65,
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

    out_path = os.path.join(out_dir, "mona_lisa_s91.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
