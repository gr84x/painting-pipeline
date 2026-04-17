"""
paint_mona_lisa_s70.py — Session 70 portrait painting.

Paints the Mona Lisa-inspired portrait using the full stroke-engine pipeline,
enhanced with session-70 additions:

  - guido_reni_angelic_grace_pass()   — NEW (session 70) Guido Reni
                                         Bolognese Baroque inspiration.
                                         Lifts the highlight region to
                                         Reni's alabaster pearl-white;
                                         injects warm rose into the cheek
                                         and lip zones; cools the deepest
                                         shadow passages toward violet-grey.

  - highlight_bloom_pass()            — NEW (session 70) artistic improvement.
                                         Simulates the soft luminous glow
                                         around bright highlights — the
                                         visual phenomenon that makes Reni's
                                         skin appear to emit its own gentle
                                         light.  Two Gaussian bloom operations:
                                         a tight inner bloom at the specular
                                         peak and a wide outer halo for the
                                         broader scattering envelope.

  Previous sessions (retained):
  - david_neoclassical_clarity_pass() — (session 69)
  - ground_tone_recession_pass()      — (session 69)
  - skin_zone_temperature_pass()      — (session 67)
  - mantegna_sculptural_form_pass()   — (session 67)
  - warm_cool_form_duality_pass()     — (session 66)
  - patinir_weltlandschaft_pass()     — (session 66)
  - crystalline_surface_pass()        — (session 65)
  - alma_tadema_marble_luminance_pass() — (session 65)
  - vigee_le_brun_pearlescent_grace_pass() — (session 64)
  - subsurface_scatter_pass()         — (session 64)
  - parmigianino_serpentine_elegance_pass() — (session 62)
  - translucent_gauze_pass()          — (session 62)
  - canaletto_luminous_veduta_pass()  — (session 63)
  - old_master_varnish_pass()         — (session 63)
  - sfumato_thermal_gradient_pass()   — (session 60)
  - sfumato_veil_pass()              — Leonardo edge dissolution
  - weyden_angular_shadow_pass()
  - giorgione_tonal_poetry_pass()
  - aerial_perspective_pass()

Session 70 artistic character:
  The random artist inspiration for this session is Guido Reni
  (1575–1642), the supreme master of the Bolognese Baroque ideal.

  Where Leonardo invented sfumato to dissolve edges into atmospheric smoke,
  and David trained to impose crisp rational contours, Reni sought something
  different: a beauty so refined it approaches the divine.  Trained in
  Annibale Carracci's Accademia degli Incamminati, Reni developed a technique
  of exquisite softness — not sfumato but silken, high-key blending that gives
  his figures an otherworldly luminosity.  His skin is built from thin,
  layered glazes over a warm ground, accumulating from rose-ivory midtones to
  alabaster pearl highlights that appear to radiate from within.  Shadows are
  kept cool and violet-grey, giving even the darkest passages a spiritual
  weightlessness.

  The Aurora ceiling fresco (1614, Casino Rospigliosi, Rome) is the fullest
  demonstration: Apollo's chariot crosses a cool dawn sky, preceded by the
  Hours, the whole procession swept by a warm-to-cool temperature gradient
  that encodes the movement of light across the day.  Reni painted this
  standing on scaffolding, working directly al fresco, and yet achieved
  the silken finish of his oil portraits.

  The guido_reni_angelic_grace_pass() applies his three defining operations:
  (1) pearl lift on the highlights — the faint cool luminosity that marks
  Reni's specular peak as alabaster rather than warm ivory;
  (2) rose injection in the cheek and lip zones — the warm pink midtone that
  reads as both lifelike warmth and idealised beauty;
  (3) violet-grey shadow cooling — the spiritual lightness that his darkest
  passages always retain.

  The session 70 artistic improvement is highlight_bloom_pass() — an encoding
  of the optical phenomenon that underlies Reni's light-emitting skin quality.
  In his paintings, the brightest areas appear to glow softly outward, as if
  light is scattering at the translucent surface.  This is physically real:
  subsurface scattering in thin-glaze oil painting causes bright passages to
  have a soft halo.  Reni enhanced this through repeated thin glazes that
  accumulate a luminous depth.  The highlight_bloom_pass() applies two
  Gaussian bloom operations — a tight inner bloom at the specular peak and a
  wide outer halo for the broader envelope — giving the portrait that quality
  of radiance that distinguishes Reni from every other Baroque painter.
"""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter

W, H = 780, 1080


# ─────────────────────────────────────────────────────────────────────────────
# Reference image construction
# (same composition as s69 — identical portrait, new passes applied)
# ─────────────────────────────────────────────────────────────────────────────

def make_reference() -> Image.Image:
    """
    Construct a richly coloured synthetic reference encoding the described
    composition.  The reference is blurred before painting so the stroke engine
    works on smooth colour masses rather than hard-edged pixels.
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # ── Sky / upper background: pale blue-grey, lightening toward the top ────
    sky_top    = np.array([0.72, 0.74, 0.78])
    sky_bottom = np.array([0.42, 0.48, 0.58])
    sky_band   = int(H * 0.62)
    for y in range(sky_band):
        t = y / sky_band
        ref[y, :] = sky_top * (1 - t) + sky_bottom * t

    # ── Landscape below sky ───────────────────────────────────────────────────
    def horizon_y(x: int) -> int:
        t = x / W
        return int(H * (0.52 + t * 0.04))   # left=52%, right=56%

    for x in range(W):
        hy = horizon_y(x)
        for y in range(hy, H):
            t = (y - hy) / (H - hy)
            far  = np.array([0.28, 0.30, 0.24])
            near = np.array([0.18, 0.14, 0.09])
            ref[y, x] = far * (1 - t) + near * t

    # ── Rocky crags — left side ───────────────────────────────────────────────
    crag_c  = np.array([0.35, 0.33, 0.28])
    crag_sh = np.array([0.18, 0.17, 0.14])
    rock_formations = [
        (int(W * 0.10), int(H * 0.45), int(W * 0.07), int(H * 0.06)),
        (int(W * 0.22), int(H * 0.42), int(W * 0.06), int(H * 0.08)),
        (int(W * 0.08), int(H * 0.40), int(W * 0.05), int(H * 0.05)),
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

    # ── Rocky crags — right side ──────────────────────────────────────────────
    right_crags = [
        (int(W * 0.82), int(H * 0.49), int(W * 0.08), int(H * 0.05)),
        (int(W * 0.92), int(H * 0.46), int(W * 0.07), int(H * 0.06)),
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

    # ── Winding path on left ──────────────────────────────────────────────────
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

    # ── River / water in mid-distance ─────────────────────────────────────────
    river_y  = int(H * 0.47)
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

    # ── Sparse vegetation ─────────────────────────────────────────────────────
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

    # ── Figure ground — warm dark lower half ─────────────────────────────────
    fg_top  = int(H * 0.56)
    fg_c    = np.array([0.16, 0.13, 0.10])
    for y in range(fg_top, H):
        t = (y - fg_top) / (H - fg_top)
        ref[y, int(W * 0.25):int(W * 0.75)] = (
            ref[y, int(W * 0.25):int(W * 0.75)] * (1 - t * 0.6)
            + fg_c * t * 0.6
        )

    # ── Dress — dark forest-green/blue-black torso ────────────────────────────
    dress_top  = int(H * 0.60)
    dress_cx   = int(W * 0.515)
    dress_rx   = int(W * 0.20)
    dress_c    = np.array([0.10, 0.14, 0.12])
    for y in range(dress_top, H):
        yr  = (y - dress_top) / (H - dress_top)
        rx_now = int(dress_rx * (1 + yr * 0.35))
        x0 = max(0, dress_cx - rx_now)
        x1 = min(W, dress_cx + rx_now)
        ref[y, x0:x1] = dress_c

    # ── Gauze wrap — semi-transparent across upper torso ─────────────────────
    gauze_top    = int(H * 0.58)
    gauze_bottom = int(H * 0.72)
    gauze_c      = np.array([0.50, 0.50, 0.44])
    for y in range(gauze_top, gauze_bottom):
        t = (y - gauze_top) / (gauze_bottom - gauze_top)
        alpha = 0.18 * (1 - abs(t - 0.5) * 1.5)
        x0 = int(W * (0.30 + t * 0.05))
        x1 = int(W * (0.72 - t * 0.03))
        if x0 < x1:
            ref[y, x0:x1] = ref[y, x0:x1] * (1 - alpha) + gauze_c * alpha

    # ── Neck ─────────────────────────────────────────────────────────────────
    neck_cx  = int(W * 0.515)
    neck_rx  = int(W * 0.042)
    neck_top = int(H * 0.365)
    neck_bot = int(H * 0.62)
    neck_c   = np.array([0.78, 0.64, 0.48])
    for y in range(neck_top, neck_bot):
        t = (y - neck_top) / (neck_bot - neck_top)
        rx_now = int(neck_rx * (1 + t * 0.25))
        x0 = max(0, neck_cx - rx_now)
        x1 = min(W, neck_cx + rx_now)
        ref[y, x0:x1] = neck_c

    # ── Face ─────────────────────────────────────────────────────────────────
    face_cx = int(W * 0.515)
    face_cy = int(H * 0.210)
    face_rx = int(W * 0.125)
    face_ry = int(H * 0.165)
    face_c  = np.array([0.82, 0.68, 0.52])
    for y in range(max(0, face_cy - face_ry), min(H, face_cy + face_ry + 1)):
        for x in range(max(0, face_cx - face_rx), min(W, face_cx + face_rx + 1)):
            dx = (x - face_cx) / face_rx
            dy = (y - face_cy) / face_ry
            d  = dx * dx + dy * dy
            if d <= 1.0:
                shade = max(0.0, dx * 0.18)
                c = face_c * (1 - shade) + np.array([0.62, 0.50, 0.36]) * shade
                fade = max(0.0, 1.0 - (d - 0.82) / 0.18) if d > 0.82 else 1.0
                ref[y, x] = ref[y, x] * (1 - fade) + c * fade

    # ── Veil over hair ────────────────────────────────────────────────────────
    veil_cx  = int(W * 0.515)
    veil_cy  = int(H * 0.105)
    veil_rx  = int(W * 0.16)
    veil_ry  = int(H * 0.10)
    veil_c   = np.array([0.14, 0.11, 0.10])
    for y in range(max(0, veil_cy - veil_ry), min(H, veil_cy + veil_ry + 1)):
        for x in range(max(0, veil_cx - veil_rx), min(W, veil_cx + veil_rx + 1)):
            dx = (x - veil_cx) / veil_rx
            dy = (y - veil_cy) / veil_ry
            d  = dx * dx + dy * dy
            if d <= 1.0:
                fade = 0.80
                ref[y, x] = ref[y, x] * (1 - fade) + veil_c * fade

    # ── Hair — dark brown, either side of face ────────────────────────────────
    hair_c = np.array([0.18, 0.13, 0.09])
    for side in (-1, 1):
        hx = face_cx + side * int(face_rx * 0.78)
        for y in range(int(H * 0.12), int(H * 0.40)):
            x0 = hx - int(W * 0.04)
            x1 = hx + int(W * 0.04)
            ref[y, max(0, x0):min(W, x1)] = hair_c

    # ── Eyes (simplified — dark irises) ───────────────────────────────────────
    for eye_x_frac in (0.468, 0.562):
        ex = int(W * eye_x_frac)
        ey = int(H * 0.198)
        for y in range(ey - 8, ey + 8):
            for x in range(ex - 12, ex + 12):
                if 0 <= y < H and 0 <= x < W:
                    d = math.sqrt(((x - ex) / 12) ** 2 + ((y - ey) / 8) ** 2)
                    if d <= 1.0:
                        ref[y, x] = np.array([0.10, 0.10, 0.11])

    # ── Hands — lower centre ──────────────────────────────────────────────────
    hands_c  = np.array([0.76, 0.62, 0.46])
    hands_cy = int(H * 0.835)
    hands_rx = int(W * 0.115)
    hands_ry = int(H * 0.052)
    for y in range(max(0, hands_cy - hands_ry), min(H, hands_cy + hands_ry + 1)):
        for x in range(max(0, int(W * 0.50) - hands_rx),
                       min(W, int(W * 0.50) + hands_rx)):
            dx = (x - int(W * 0.50)) / hands_rx
            dy = (y - hands_cy) / hands_ry
            d  = dx * dx + dy * dy
            if d <= 1.0:
                fade = max(0.0, 1.0 - (d - 0.78) / 0.22) if d > 0.78 else 1.0
                ref[y, x] = ref[y, x] * (1 - fade * 0.88) + hands_c * fade * 0.88

    # ── Final blur — smooth colour masses for stroke engine ───────────────────
    ref_uint8 = np.clip(ref * 255, 0, 255).astype(np.uint8)
    ref_img   = Image.fromarray(ref_uint8, "RGB")
    ref_img   = ref_img.filter(ImageFilter.GaussianBlur(radius=14))
    return ref_img


# ─────────────────────────────────────────────────────────────────────────────
# Main paint function
# ─────────────────────────────────────────────────────────────────────────────

def paint(out_dir: str = ".") -> str:
    """
    Execute the full session-70 painting pipeline and save the result.

    Returns the path to the saved PNG.
    """
    print("Session 70 — Mona Lisa portrait")
    print("Random artist: Guido Reni (Bolognese Baroque, 1575–1642)")
    print("Artistic improvement: highlight_bloom_pass()")
    print()

    ref = make_reference()
    p   = Painter(W, H)

    # ── Warm ochre imprimatura ────────────────────────────────────────────────
    print("Toning ground (warm ochre imprimatura)…")
    p.tone_ground((0.54, 0.46, 0.28), texture_strength=0.05)

    # ── Broad underpainting — establish major colour masses ───────────────────
    print("Underpainting…")
    p.underpainting(ref, stroke_size=55, n_strokes=300)

    # ── Block in — first structural pass ─────────────────────────────────────
    print("Block in (large)…")
    p.block_in(ref, stroke_size=40, n_strokes=550)

    # ── Session 69: Ground tone recession pass ────────────────────────────────
    print("Ground tone recession pass (session 69)…")
    p.ground_tone_recession_pass(
        horizon_y       = 0.54,
        fg_warm_lift    = 0.032,
        bg_cool_lift    = 0.038,
        transition_band = 0.22,
        opacity         = 0.48,
    )

    # ── Build form — mid-range detail passes ─────────────────────────────────
    print("Block in (medium)…")
    p.block_in(ref, stroke_size=24, n_strokes=700)
    print("Build form (large)…")
    p.build_form(ref, stroke_size=14, n_strokes=1100)
    print("Build form (detail)…")
    p.build_form(ref, stroke_size=7, n_strokes=800)

    # ── Patinir weltlandschaft pass (session 66) ──────────────────────────────
    print("Patinir weltlandschaft pass (session 66)…")
    p.patinir_weltlandschaft_pass(
        warm_foreground  = 0.06,
        green_midground  = 0.05,
        cool_distance    = 0.10,
        horizon_near     = 0.52,
        horizon_far      = 0.70,
        transition_blur  = 12.0,
        opacity          = 0.58,
    )

    # ── Parmigianino serpentine elegance pass (session 62) ────────────────────
    print("Parmigianino serpentine elegance pass (session 62)…")
    p.parmigianino_serpentine_elegance_pass(
        porcelain_strength = 0.10,
        lavender_shadow    = 0.08,
        silver_highlight   = 0.06,
        opacity            = 0.36,
    )

    # ── Vigée Le Brun pearlescent grace pass (session 64) ─────────────────────
    print("Vigée Le Brun pearlescent grace pass (session 64)…")
    p.vigee_le_brun_pearlescent_grace_pass(
        rose_bloom_strength = 0.07,
        pearl_highlight     = 0.06,
        shadow_warmth       = 0.04,
        midtone_low         = 0.45,
        midtone_high        = 0.82,
        opacity             = 0.46,
    )

    # ── Subsurface scatter pass (session 64) ──────────────────────────────────
    print("Subsurface scatter pass (session 64)…")
    p.subsurface_scatter_pass(
        scatter_strength  = 0.10,
        scatter_radius    = 6.0,
        scatter_low       = 0.42,
        scatter_high      = 0.82,
        penumbra_warm     = 0.05,
        shadow_cool       = 0.03,
        opacity           = 0.42,
    )

    # ── Session 70: Guido Reni angelic grace pass ─────────────────────────────
    # Applied after the warm skin passes and before the structural modelling
    # passes.  At this point the skin is warm and glowing from the subsurface
    # scatter and Vigée Le Brun passes; Reni's pass now:
    #   1. Lifts the highlight region to alabaster pearl-white — cooler and
    #      more luminous than the warm ivory produced by the previous passes.
    #   2. Injects rose into cheek and lip zones — the idealised warm-pink
    #      midtone that separates Reni from Leonardo's neutral warm ochre.
    #   3. Cools the shadow passages toward violet-grey — giving even the
    #      darkest areas the spiritual weightlessness of Bolognese Baroque.
    # opacity=0.50 — present but balanced against the accumulated warm tone.
    print("Guido Reni angelic grace pass (session 70)…")
    p.guido_reni_angelic_grace_pass(
        face_cx       = 0.515,
        face_cy       = 0.210,
        face_rx       = 0.125,
        face_ry       = 0.168,
        pearl_lift    = 0.07,
        pearl_cool    = 0.04,
        cheek_rose    = 0.045,
        lip_rose      = 0.055,
        shadow_violet = 0.042,
        blur_radius   = 9.0,
        opacity       = 0.50,
    )

    # ── Alma-Tadema marble luminance pass (session 65) ────────────────────────
    print("Alma-Tadema marble luminance pass (session 65)…")
    p.alma_tadema_marble_luminance_pass(
        marble_warm_strength = 0.07,
        specular_cool_shift  = 0.05,
        specular_thresh      = 0.82,
        translucent_low      = 0.50,
        translucent_high     = 0.82,
        opacity              = 0.45,
    )

    # ── Mantegna sculptural form pass (session 67) ────────────────────────────
    print("Mantegna sculptural form pass (session 67)…")
    p.mantegna_sculptural_form_pass(
        highlight_lift = 0.09,
        shadow_deepen  = 0.07,
        edge_crisp     = 0.05,
        blur_radius    = 4.0,
        opacity        = 0.44,
    )

    # ── Session 69: David neoclassical clarity pass ───────────────────────────
    print("David neoclassical clarity pass (session 69)…")
    p.david_neoclassical_clarity_pass(
        figure_cx      = 0.515,
        figure_top     = 0.02,
        figure_bottom  = 0.90,
        figure_rx      = 0.30,
        bg_cool_shift  = 0.058,
        contour_crisp  = 0.048,
        amber_glaze    = 0.038,
        blur_radius    = 7.0,
        opacity        = 0.46,
    )

    # ── Canaletto luminous veduta pass (session 63) ───────────────────────────
    print("Canaletto luminous veduta pass (session 63)…")
    p.canaletto_luminous_veduta_pass(
        sky_lift   = 0.08,
        stone_warm = 0.06,
        water_cool = 0.06,
        sky_band   = 0.52,
        opacity    = 0.52,
    )

    # ── Weyden angular shadow pass ────────────────────────────────────────────
    print("Weyden angular shadow pass…")
    p.weyden_angular_shadow_pass(
        shadow_thresh  = 0.36,
        light_thresh   = 0.62,
        edge_sharpen   = 0.38,
        shadow_cool    = 0.06,
        highlight_cool = 0.03,
        opacity        = 0.50,
    )

    # ── Sfumato thermal gradient pass (session 60) ────────────────────────────
    print("Sfumato thermal gradient pass (session 60)…")
    p.sfumato_thermal_gradient_pass(
        warm_strength      = 0.10,
        cool_strength      = 0.12,
        horizon_y          = 0.52,
        gradient_width     = 0.28,
        edge_soften_radius = 8,
        opacity            = 0.62,
    )

    # ── Sfumato veil — the defining Leonardo technique ────────────────────────
    print("Sfumato veil pass…")
    p.sfumato_veil_pass(
        ref,
        n_veils        = 9,
        blur_radius    = 10.0,
        warmth         = 0.26,
        veil_opacity   = 0.046,
        edge_only      = True,
        chroma_dampen  = 0.22,
        depth_gradient = 0.55,
    )

    # ── Translucent gauze pass (session 62) ───────────────────────────────────
    print("Translucent gauze pass (session 62)…")
    p.translucent_gauze_pass(
        zone_top        = 0.38,
        zone_bottom     = 0.58,
        opacity         = 0.26,
        cool_shift      = 0.04,
        weave_strength  = 0.010,
        blur_radius     = 6.0,
    )

    # ── Giorgione tonal poetry pass ───────────────────────────────────────────
    print("Giorgione tonal-poetry pass…")
    p.giorgione_tonal_poetry_pass(
        midtone_low          = 0.32,
        midtone_high         = 0.68,
        luminous_lift        = 0.06,
        warm_shadow_strength = 0.04,
        cool_edge_strength   = 0.04,
        opacity              = 0.48,
    )

    # ── Place final lights ────────────────────────────────────────────────────
    print("Place lights…")
    p.place_lights(ref, stroke_size=5, n_strokes=650)

    # ── Aerial perspective ────────────────────────────────────────────────────
    print("Aerial perspective pass…")
    p.aerial_perspective_pass(
        sky_band     = 0.58,
        fade_power   = 2.0,
        desaturation = 0.52,
        cool_push    = 0.11,
        haze_lift    = 0.06,
        opacity      = 0.70,
    )

    # ── Session 65: Crystalline surface pass ─────────────────────────────────
    print("Crystalline surface pass (session 65)…")
    p.crystalline_surface_pass(
        specular_radius   = 2.5,
        specular_strength = 0.10,
        specular_thresh   = 0.82,
        micro_cool_shift  = 0.04,
        halo_radius       = 7.0,
        halo_warmth       = 0.05,
        halo_thresh       = 0.68,
        opacity           = 0.50,
    )

    # ── Session 70: Highlight bloom pass (artistic improvement) ───────────────
    # Applied after the crystalline surface pass — at this point the specular
    # peaks are sharply defined; the bloom pass now wraps them in a soft
    # luminous halo, translating Reni's glazed-skin radiance from his oil
    # painting technique into our pipeline.
    # bloom_thresh=0.76 — targets only the genuine specular peaks, not the
    # broader midtone.  bloom_radius=12 / halo_radius=26 — inner tight bloom
    # + outer diffuse envelope.  opacity=0.52 — present but not dominant;
    # the sfumato should remain the primary edge-dissolving technique.
    print("Highlight bloom pass (session 70)…")
    p.highlight_bloom_pass(
        threshold     = 0.76,
        bloom_sigma   = 12.0,
        bloom_opacity = 0.28,
        bloom_color   = (1.00, 0.97, 0.90),   # very faint warm ivory tint
        multi_scale   = True,
        figure_only   = False,
    )

    # ── Session 67: Skin zone temperature pass ────────────────────────────────
    print("Skin zone temperature pass (session 67)…")
    p.skin_zone_temperature_pass(
        face_cx        = 0.515,
        face_cy        = 0.196,
        face_rx        = 0.125,
        face_ry        = 0.168,
        forehead_warm  = 0.035,
        temple_cool    = 0.028,
        nose_pink      = 0.038,
        lip_rose       = 0.030,
        jaw_cool       = 0.025,
        blur_radius    = 9.0,
        opacity        = 0.55,
    )

    # ── Session 66: Warm/cool form duality pass ───────────────────────────────
    print("Warm/cool form duality pass (session 66)…")
    p.warm_cool_form_duality_pass(
        warm_strength    = 0.06,
        cool_strength    = 0.06,
        midtone          = 0.48,
        transition_width = 0.18,
        blur_radius      = 7.0,
        opacity          = 0.52,
    )

    # ── Session 63: Old-master varnish pass ───────────────────────────────────
    print("Old-master varnish pass (session 63)…")
    p.old_master_varnish_pass(
        amber_strength  = 0.12,
        edge_darken     = 0.10,
        highlight_desat = 0.06,
        opacity         = 0.28,
    )

    # ── Final glaze — warm amber, very light ─────────────────────────────────
    print("Final glaze (warm amber)…")
    p.glaze((0.58, 0.44, 0.16), opacity=0.034)

    # ── Finish ────────────────────────────────────────────────────────────────
    print("Finishing (vignette + crackle)…")
    p.finish(vignette=0.50, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s70_final.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
    print("Done:", result)
