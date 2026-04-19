"""
paint_mona_lisa_s91.py -- Session 91 portrait painting.

Paints the Mona Lisa-inspired portrait using the full stroke-engine pipeline,
with session-91 additions:

  - caillebotte_perspective_pass()                    -- NEW (session 91) Gustave Caillebotte.
                                                         Three-stage Parisian Realist technique:
                                                         (1) axis-aligned H/V edge sharpening --
                                                         unsharp masking along horizontal and
                                                         vertical axes independently reinforces
                                                         receding geometric lines (the landscape
                                                         crags, the horizon edge) without halos
                                                         on organic diagonal edges; (2) cobblestone
                                                         reflection lift -- in dark, desaturated
                                                         background zones, a cool blue-channel
                                                         boost simulates the faint sky reflection
                                                         in the dark rocky terrain, adding a trace
                                                         of atmospheric cool to the shadowed crags;
                                                         (3) cool ambient shift -- warm mid-tones
                                                         in the background landscape are nudged
                                                         toward cooler grey, countering the
                                                         accumulated warmth of the oil-painting
                                                         glaze chain and restoring the cool,
                                                         diffuse quality of Leonardo's distant
                                                         atmosphere.

  - Improved edge_lost_and_found_pass()               -- SESSION 91 ARTISTIC IMPROVEMENT.
    with soft_halo_strength=0.14                        Perioral sfumato halo: Leonardo's most
                                                         characteristic technical achievement in
                                                         the Mona Lisa is the way the mouth
                                                         corners dissolve into the surrounding
                                                         flesh -- a literal impossibility to
                                                         discern where the lip ends and the
                                                         cheek begins.  The existing
                                                         edge_lost_and_found_pass already applies
                                                         selective focus sharpening in the focal
                                                         zone; the new soft_halo_strength
                                                         parameter adds a very soft Gaussian halo
                                                         around lost edges at the periphery of
                                                         the focal zone, creating a gentle
                                                         luminous bloom that imitates the way
                                                         Leonardo's sfumato layers build up a
                                                         faint luminous aureole around dissolving
                                                         edge zones -- particularly visible in
                                                         the area between the nose shadow, upper
                                                         lip, and cheek.  This is the 'smile
                                                         problem' made visible: the edge is not
                                                         missing; it is replaced by a soft glow.

  Sessions 90 and earlier (retained):
  - hodler_parallelism_pass()                          -- (session 90) Ferdinand Hodler
  - atmospheric_depth_pass (horizon_glow_band=0.15)   -- (session 90 improved)
  - spilliaert_vertiginous_void_pass()                 -- (session 89) Leon Spilliaert
  - sfumato_veil_pass (chroma_gate=0.42)               -- (session 89 improved)
  - redon_luminous_reverie_pass()                      -- (session 88) Odilon Redon
  - luminous_haze_pass (spectral_dispersion=0.28)      -- (session 88 improved)
  - whistler_tonal_harmony_pass()                      -- (session 87)
  - cool_atmospheric_recession_pass
    (lateral_horizon_asymmetry=+0.06)                  -- (session 87 improved)
  - carriera_pastel_glow_pass()                        -- (session 86)
  - signorelli_sculptural_vigour_pass()                -- (session 85)
  - perugino_serene_grace_pass()                       -- (session 84)
  - fra_filippo_lippi_tenerezza_pass()                 -- (session 83)
  - highlight_bloom_pass (chromatic_bloom=True)        -- (session 83 improved)
  - gericault_romantic_turbulence_pass()               -- (session 82)
  - sfumato_veil_pass (shadow_warm_recovery)           -- (session 82 improved)
  - chardin_granular_intimacy_pass()                   -- (session 81)
  - edge_lost_and_found_pass (gradient_selectivity)    -- (session 81 improved)
  - andrea_del_sarto_golden_sfumato_pass()             -- (session 80)
  - lotto_chromatic_anxiety_pass()                     -- (session 79)
  - rigaud_velvet_drapery_pass()                       -- (session 78)
  - poussin_classical_clarity_pass()                   -- (session 77)
  - steen_warm_vitality_pass()                         -- (session 76)
  - de_hooch_threshold_light_pass()                    -- (session 75)
  - anguissola_intimacy_pass()                         -- (session 73)
  - cool_atmospheric_recession_pass()                  -- (session 74)
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
  The random artist for this session is Gustave Caillebotte (1848-1894), the
  Impressionist-Realist who brought a photographer's precision and an
  architect's spatial rigour to Parisian urban painting.  His visual language
  -- radical perspective foreshortening, cool grey Parisian overcast palette,
  and the cool reflection of sky in wet cobblestones -- contributes to this
  portrait through the caillebotte_perspective_pass().

  In the context of the accumulated Mona Lisa portrait, Caillebotte's
  contribution is atmospheric counter-pressure.  By session 90, twenty
  successive glazing passes have built up a warm, amber-saturated oil-
  painting quality across the entire canvas -- appropriate for Leonardo's
  figure and foreground, but somewhat at odds with his cool, atmospheric
  background landscape.  Leonardo's distant crags and sky genuinely ARE cool:
  they recede into blue-grey atmospheric haze, the sky above is a pale grey-
  blue, and the rocky terrain in the middle distance is desaturated and
  neutral.  Caillebotte's cool ambient shift and cobblestone reflection lift
  restore some of that coolness selectively in the background.

  The axis-aligned sharpening of the Caillebotte pass also sharpens the
  horizontal horizon line and the vertical silhouettes of the distant crags --
  making them read more clearly as solid forms within the atmospheric haze,
  which is exactly what Leonardo's background intends: firm geological mass
  rendered in cool atmospheric colour.

  The session 91 artistic improvement -- soft_halo_strength in
  edge_lost_and_found_pass() -- addresses one of the most distinctive and
  most-discussed features of the Mona Lisa: the ambiguous smile.  The corners
  of the mouth dissolve into surrounding flesh under Leonardo's sfumato in a
  way that makes it impossible to read the expression definitively.  In a
  rendered digital portrait this ambiguity is hard to encode; hard edges
  produce a fixed expression, and pure blurring produces formlessness.  The
  soft_halo_strength parameter adds a faint Gaussian luminous bloom around
  edges in the sfumato zone (outside the sharp focal ring) -- not erasing
  edges but surrounding them with a gentle light aureole that, at low
  strength, creates the perceptual effect of a form present-but-dissolving.
  This is optically closer to what Leonardo achieved through glazing than
  simple blurring: a faint luminous envelope around the edge, not the edge
  itself.
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
    ys, xs = np.ogrid[:H, :W]
    face_d = ((xs - face_cx) / face_rx) ** 2 + ((ys - face_cy) / face_ry) ** 2
    mask[face_d <= 1.15] = 1.0

    # Body / dress trapezoid
    body_top = int(H * 0.37)
    for y in range(body_top, H):
        t = (y - body_top) / (H - body_top)
        half_w = int(W * (0.22 + 0.12 * t))
        cx = W // 2
        x0 = max(0, cx - half_w)
        x1 = min(W, cx + half_w)
        mask[y, x0:x1] = 1.0

    # Gaussian feather
    from scipy.ndimage import gaussian_filter
    mask = gaussian_filter(mask, sigma=12.0)
    mask = np.clip(mask / mask.max(), 0.0, 1.0)
    return mask


# -------------------------------------------------------------------------
# Painting
# -------------------------------------------------------------------------

def paint(out_dir: str = ".") -> str:
    """Run the full session-91 painting pipeline."""
    print("Session 91 -- Mona Lisa portrait")
    print("Random artist: Gustave Caillebotte (French Impressionism / Urban Realism, 1848-1894)")
    print("New pass: caillebotte_perspective_pass()")
    print("  -- H/V axis-aligned edge sharpening: reinforce receding geometric lines in landscape")
    print("  -- cobblestone reflection lift: cool blue boost in dark desaturated crag zones")
    print("  -- cool ambient shift: neutralise warm mid-tones toward Parisian overcast grey")
    print()
    print("Session 91 artistic improvement: soft_halo_strength in edge_lost_and_found_pass()")
    print("  Perioral sfumato halo: a faint Gaussian luminous bloom around lost edges at the")
    print("  periphery of the focal zone simulates Leonardo's sfumato layers building a gentle")
    print("  luminous aureole around dissolving edge zones -- the mechanism behind the smile.")
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

    # SESSION 90: Atmospheric depth pass with horizon_glow_band (ARTISTIC IMPROVEMENT s90)
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

    # Session 71: Luminous haze pass -- SESSION 88 IMPROVEMENT: spectral_dispersion=0.28
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
        warm_strength = 0.06,
        cool_strength = 0.04,
        opacity       = 0.22,
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

    # Session 82 IMPROVED (s89): sfumato veil with shadow_warm_recovery AND chroma_gate.
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

    # ── SESSION 91: Caillebotte perspective pass (NEW) ────────────────────────
    # Gustave Caillebotte (1848-1894) -- Impressionism / Urban Realism.
    # Three operations: H/V edge sharpening, cobblestone reflection lift,
    # cool ambient shift.  In this portrait, the pass works primarily on the
    # background landscape: the horizontal horizon edge is reinforced, dark
    # rocky crags receive a cool sky-reflection lift, and accumulated warmth
    # in the mid-tone landscape is pulled toward atmospheric grey.
    # Applied at opacity=0.25 to preserve the warm portrait glazing chain
    # while restoring coolness to the distant background atmosphere.
    print("Caillebotte perspective pass (session 91 -- NEW)...")
    p.caillebotte_perspective_pass(
        perspective_strength  = 0.22,   # modest sharpening -- crisp horizon, not harsh
        cobblestone_boost     = 0.06,   # subtle cool lift in dark rocky crag zones
        cool_shift            = 0.04,   # gentle cool shift in warm mid-tones
        axis_sigma_h          = 1.4,    # slightly wider H-blur for softer horizontal lines
        axis_sigma_v          = 1.2,
        dark_lum_thresh       = 0.42,   # target dark rocky background zones
        dark_chroma_thresh    = 0.12,
        warm_lum_lo           = 0.32,
        warm_lum_hi           = 0.68,
        blur_radius           = 2.5,
        opacity               = 0.25,
    )

    # Session 81 IMPROVED (s91): edge_lost_and_found_pass with gradient_selectivity
    # -- SESSION 91 ARTISTIC IMPROVEMENT: soft_halo_strength=0.14 for perioral sfumato.
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

    out_path = os.path.join(out_dir, "mona_lisa_s91.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
