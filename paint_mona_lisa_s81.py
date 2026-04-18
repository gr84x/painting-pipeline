"""
paint_mona_lisa_s81.py -- Session 81 portrait painting.

Paints the Mona Lisa-inspired portrait using the full stroke-engine pipeline,
with session-81 additions:

  - chardin_granular_intimacy_pass()           -- NEW (session 81) Jean-Baptiste-
                                                  Siméon Chardin.  Granular optical
                                                  dab scatter, atmospheric muting
                                                  pull toward warm-gray center,
                                                  quiet luminance cap. Applied at
                                                  low opacity (0.34) after del Sarto
                                                  to restore the quiet intimacy that
                                                  accumulates chromatic warmth can
                                                  displace.

  - edge_lost_and_found_pass (improved)        -- NEW (session 81) gradient_selectivity
                                                  parameter. Gates found-zone sharpening
                                                  by luminance gradient magnitude,
                                                  preventing noise amplification in
                                                  smooth flesh passages while fully
                                                  sharpening actual form boundaries.
                                                  Applied at gradient_selectivity=0.65.

  Sessions 80 and earlier (retained):
  - andrea_del_sarto_golden_sfumato_pass()    -- (session 80) Andrea del Sarto
  - lotto_chromatic_anxiety_pass()             -- (session 79) Lorenzo Lotto
  - rigaud_velvet_drapery_pass()              -- (session 78) Hyacinthe Rigaud
  - poussin_classical_clarity_pass()          -- (session 77) Nicolas Poussin
  - steen_warm_vitality_pass()                -- (session 76) Jan Steen warm vitality
  - anguissola_intimacy_pass()                -- (session 73) Sofonisba Anguissola
  - cool_atmospheric_recession_pass()          -- (session 74) Aerial perspective
  - de_hooch_threshold_light_pass()           -- (session 75) Pieter de Hooch
  - watteau_crepuscular_reverie_pass()
  - correggio_golden_tenderness_pass()
  - luminous_haze_pass()
  - guido_reni_angelic_grace_pass()
  - highlight_bloom_pass()
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
  - canaletto_luminous_veduta_pass()
  - old_master_varnish_pass()
  - sfumato_thermal_gradient_pass()
  - sfumato_veil_pass()
  - weyden_angular_shadow_pass()
  - giorgione_tonal_poetry_pass()
  - aerial_perspective_pass()

Session 81 artistic character:
  The random artist inspiration for this session is Jean-Baptiste-Siméon Chardin
  (1699–1779), one of the greatest still-life and domestic genre painters in the
  Western tradition, and the supreme master of what Diderot called 'la magie de
  Chardin' — a magic he could not explain.

  Chardin worked in an era dominated by the decorative glitter of Rococo — Boucher's
  pink goddesses, Fragonard's theatrical roses — and represented something entirely
  different: the honest, patient study of ordinary objects and ordinary people under
  ordinary light.  His copper pots, his loaves of bread, his young students and
  kitchen maids are painted with a quiet authority that makes everything around them
  seem frivolous.

  His technique is unlike any of his contemporaries'.  Where the Rococo painters
  blended their pigment into smooth, appetising surfaces, Chardin applied small
  individual dabs of slightly varied colour side by side, leaving the retinal
  blending to happen in the eye rather than on the canvas.  The result is a warm,
  grainy, atmospheric quality — dusty but luminous, quiet but never dead.  Diderot
  described stepping back from a Chardin canvas and watching objects reconstitute
  themselves from apparent chaos: 'approach the picture and everything blurs and
  flattens out; step back and everything reconstitutes and comes back to life.'

  This is not Seurat's systematic divisionism — Chardin's dabs are random in
  placement, asymmetric in size, and deeply organic in colour variation.  The result
  reads as texture rather than colour theory.  His palette is deliberately muted:
  warm grays, ochres, olive greens, quiet ivory — the colours of aged linen and
  copper and kitchen walls.  No chromatic drama; the power comes from the
  accumulation of small, careful decisions.

  What does a Chardin-inspired pass do for the Mona Lisa portrait?

  The preceding sessions have built up a painting of considerable chromatic
  complexity: del Sarto's golden amber warmth (session 80), Lotto's cool
  psychological undertone (session 79), Poussin's classical clarity (session 77),
  Rigaud's velvet and silk (session 78), Steen's warm vitality (session 76).
  Each pass adds presence — but presence can become crowdedness.  Chardin's
  quality is the opposite: intimacy through restraint.  The chardin_granular_intimacy_pass()
  applies a quiet counter-pressure:

  1. The granular dab scatter redistributes existing colour into micro-touches,
     softening any remaining machine-smoothness without introducing new colour.
     The result is a surface that feels handled — as if the paint were applied by
     a patient hand rather than a process.

  2. The atmospheric muting pull draws slightly over-saturated passages back toward
     the warm-gray center of Chardin's palette.  This is not desaturation — it is
     the specific muted-ochre warmth of Chardin's world, which ensures the portrait's
     accumulated chromatic energy settles into coherence rather than vibrating loose.

  3. The luminance cap gently suppresses the highest specular peaks.  Chardin's
     paintings have no blazing highlights.  This passes on the quality of intimate
     candlelight rather than theatrical spotlight.

  Session-81 technical improvement — gradient_selectivity in edge_lost_and_found_pass():
  Prior sessions applied the found-zone sharpening uniformly to all pixels near the
  focal point.  This caused slight noise amplification in the smooth interior of
  well-blended flesh passages: the unsharp mask found and enhanced micro-variation
  (brush texture seams from earlier passes) that should have remained invisible.  The
  new gradient_selectivity=0.65 parameter gates the sharpening by the local luminance
  gradient — only pixels that lie on actual form boundaries (nose bridge, lip line,
  eye contour, highlighted cheekbone ridge) receive full sharpening.  The smooth
  interior of flesh passages is left undisturbed.  The result is a more surgically
  accurate edge quality: precisely found where the form demands it, entirely lost
  in the transitions between tones.
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
# (same composition as previous sessions -- identical portrait)
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

    # Landscape below sky
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

    # Rocky crags -- left side
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

    # Rocky crags -- right side
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
            # Dress width narrows toward the top (neckline)
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
                    # Dot product with light direction for shading
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
    # Eyes -- dark almond shapes
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
                # Bilobed upper lip shape
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
    """Run the full session-81 painting pipeline."""
    print("Session 81 -- Mona Lisa portrait")
    print("Random artist: Jean-Baptiste-Siméon Chardin (French Rococo / Intimism, 1699-1779)")
    print("New pass: chardin_granular_intimacy_pass()")
    print("  -- granular optical dab scatter + atmospheric muting + quiet luminance cap")
    print("Artistic improvement: edge_lost_and_found_pass(gradient_selectivity=0.65)")
    print("  -- gradient-gated found-zone sharpening; no noise amplification in smooth flesh")
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

    # Session 74: Cool atmospheric recession pass
    print("Cool atmospheric recession pass (session 74)...")
    p.cool_atmospheric_recession_pass(
        horizon_y       = 0.54,
        cool_strength   = 0.16,
        bright_lift     = 0.06,
        desaturate      = 0.42,
        blur_background = True,
        feather         = 0.12,
        opacity         = 0.64,
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

    # Subsurface scatter pass (session 64)
    print("Subsurface scatter pass (session 64)...")
    p.subsurface_scatter_pass(
        scatter_strength  = 0.10,
        scatter_radius    = 6.0,
        scatter_low       = 0.42,
        scatter_high      = 0.82,
        penumbra_warm     = 0.05,
        shadow_cool       = 0.03,
        opacity           = 0.42,
    )

    # Correggio golden tenderness pass (session 71)
    print("Correggio golden tenderness pass (session 71)...")
    p.correggio_golden_tenderness_pass(
        midtone_low   = 0.30,
        midtone_high  = 0.78,
        gold_lift     = 0.055,
        amber_shadow  = 0.045,
        face_cx       = 0.515,
        face_cy       = 0.210,
        face_rx       = 0.140,
        face_ry       = 0.190,
        glow_strength = 0.048,
        blur_radius   = 10.0,
        opacity       = 0.46,
    )

    # Guido Reni angelic grace pass (session 70)
    print("Guido Reni angelic grace pass (session 70)...")
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

    # Anguissola intimacy pass (session 73)
    print("Anguissola intimacy pass (session 73)...")
    p.anguissola_intimacy_pass(
        focus_cx         = 0.515,
        focus_cy         = 0.210,
        focus_radius     = 0.155,
        sharpen_strength = 0.70,
        eye_cx_offset    = 0.048,
        eye_cy_offset    = -0.018,
        eye_radius       = 0.032,
        lip_cy_offset    = 0.055,
        lip_rx           = 0.052,
        lip_ry           = 0.020,
        periphery_soften = 0.45,
        warm_ambient     = 0.018,
        opacity          = 0.52,
    )

    # Alma-Tadema marble luminance pass (session 65)
    print("Alma-Tadema marble luminance pass (session 65)...")
    p.alma_tadema_marble_luminance_pass(
        marble_warm_strength = 0.07,
        specular_cool_shift  = 0.05,
        specular_thresh      = 0.82,
        translucent_low      = 0.50,
        translucent_high     = 0.82,
        opacity              = 0.45,
    )

    # Mantegna sculptural form pass (session 67)
    print("Mantegna sculptural form pass (session 67)...")
    p.mantegna_sculptural_form_pass(
        highlight_lift = 0.09,
        shadow_deepen  = 0.07,
        edge_crisp     = 0.05,
        blur_radius    = 4.0,
        opacity        = 0.44,
    )

    # David neoclassical clarity pass (session 69)
    print("David neoclassical clarity pass (session 69)...")
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

    # Canaletto luminous veduta pass (session 63)
    print("Canaletto luminous veduta pass (session 63)...")
    p.canaletto_luminous_veduta_pass(
        sky_lift   = 0.08,
        stone_warm = 0.06,
        water_cool = 0.06,
        sky_band   = 0.52,
        opacity    = 0.52,
    )

    # Weyden angular shadow pass
    print("Weyden angular shadow pass...")
    p.weyden_angular_shadow_pass(
        shadow_thresh  = 0.36,
        light_thresh   = 0.62,
        edge_sharpen   = 0.38,
        shadow_cool    = 0.06,
        highlight_cool = 0.03,
        opacity        = 0.50,
    )

    # Sfumato thermal gradient pass (session 60)
    print("Sfumato thermal gradient pass (session 60)...")
    p.sfumato_thermal_gradient_pass(
        warm_strength      = 0.10,
        cool_strength      = 0.12,
        horizon_y          = 0.52,
        gradient_width     = 0.28,
        edge_soften_radius = 8,
        opacity            = 0.62,
    )

    # Sfumato veil -- the defining Leonardo technique
    print("Sfumato veil pass...")
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

    # Translucent gauze pass (session 62)
    print("Translucent gauze pass (session 62)...")
    p.translucent_gauze_pass(
        zone_top        = 0.38,
        zone_bottom     = 0.58,
        opacity         = 0.26,
        cool_shift      = 0.04,
        weave_strength  = 0.010,
        blur_radius     = 6.0,
    )

    # Giorgione tonal poetry pass
    print("Giorgione tonal-poetry pass...")
    p.giorgione_tonal_poetry_pass(
        midtone_low          = 0.32,
        midtone_high         = 0.68,
        luminous_lift        = 0.06,
        warm_shadow_strength = 0.04,
        cool_edge_strength   = 0.04,
        opacity              = 0.48,
    )

    # Place final lights
    print("Place lights...")
    p.place_lights(ref, stroke_size=5, n_strokes=650)

    # Aerial perspective pass
    print("Aerial perspective pass...")
    p.aerial_perspective_pass(
        sky_band     = 0.58,
        fade_power   = 2.0,
        desaturation = 0.52,
        cool_push    = 0.11,
        haze_lift    = 0.06,
        opacity      = 0.70,
    )

    # Crystalline surface pass (session 68)
    print("Crystalline surface pass (session 68)...")
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

    # Highlight bloom pass (session 70)
    print("Highlight bloom pass (session 70)...")
    p.highlight_bloom_pass(
        threshold     = 0.76,
        bloom_sigma   = 12.0,
        bloom_opacity = 0.28,
        bloom_color   = (1.00, 0.97, 0.90),
        multi_scale   = True,
        figure_only   = False,
    )

    # Luminous haze pass (session 71)
    print("Luminous haze pass (session 71)...")
    p.luminous_haze_pass(
        haze_warmth    = 0.038,
        haze_opacity   = 0.10,
        haze_color     = (0.88, 0.76, 0.50),
        soften_radius  = 2.5,
        contrast_damp  = 0.055,
        shadow_lift    = 0.016,
        opacity        = 0.50,
    )

    # Watteau crepuscular reverie pass (session 72)
    print("Watteau crepuscular reverie pass (session 72)...")
    p.watteau_crepuscular_reverie_pass(
        amber_shift       = 0.032,
        shadow_lift       = 0.020,
        edge_soften       = 3.5,
        crepuscular_low   = 0.32,
        crepuscular_high  = 0.72,
        periphery_darken  = 0.055,
        opacity           = 0.44,
    )

    # De Hooch threshold light pass (session 75)
    print("De Hooch threshold light pass (session 75)...")
    p.de_hooch_threshold_light_pass(
        light_x       = 0.12,
        light_width   = 0.55,
        light_falloff = 0.60,
        warm_color    = (0.78, 0.58, 0.28),
        cool_color    = (0.36, 0.46, 0.58),
        warm_strength = 0.20,
        cool_strength = 0.14,
        doorway_y     = 0.28,
        doorway_h     = 0.50,
        doorway_w     = 0.16,
        doorway_x     = 0.84,
        opacity       = 0.38,
    )

    # Skin zone temperature pass (session 67)
    print("Skin zone temperature pass (session 67)...")
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

    # Warm/cool form duality pass (session 66)
    print("Warm/cool form duality pass (session 66)...")
    p.warm_cool_form_duality_pass(
        warm_strength    = 0.06,
        cool_strength    = 0.06,
        midtone          = 0.48,
        transition_width = 0.18,
        blur_radius      = 7.0,
        opacity          = 0.52,
    )

    # Jan Steen warm vitality pass (session 76)
    print("Jan Steen warm vitality pass (session 76)...")
    p.steen_warm_vitality_pass(
        face_cx          = 0.515,
        face_cy          = 0.210,
        face_rx          = 0.140,
        face_ry          = 0.195,
        amber_lift       = 0.048,
        rose_flush       = 0.034,
        shadow_warmth    = 0.032,
        shadow_thresh    = 0.36,
        highlight_thresh = 0.72,
        blur_radius      = 9.0,
        opacity          = 0.52,
    )

    # Poussin classical clarity pass (session 77)
    print("Poussin classical clarity pass (session 77)...")
    p.poussin_classical_clarity_pass(
        shadow_cool      = 0.06,
        midtone_lift     = 0.04,
        saturation_cap   = 0.82,
        highlight_ivory  = 0.04,
        opacity          = 0.35,
    )

    # Rigaud velvet drapery pass (session 78)
    print("Rigaud velvet drapery pass (session 78)...")
    p.rigaud_velvet_drapery_pass(
        velvet_thresh  = 0.30,
        velvet_dark    = 0.10,
        velvet_warm_r  = 0.06,
        velvet_warm_g  = 0.03,
        silk_thresh    = 0.68,
        silk_cool_b    = 0.08,
        silk_cool_r    = 0.03,
        blur_radius    = 6.0,
        opacity        = 0.48,
    )

    # Lotto chromatic anxiety pass (session 79)
    print("Lotto chromatic anxiety pass (session 79)...")
    p.lotto_chromatic_anxiety_pass(
        flesh_mid_lo     = 0.40,
        flesh_mid_hi     = 0.75,
        cool_b_boost     = 0.07,
        cool_r_reduce    = 0.04,
        eye_left_cx      = 0.468,
        eye_left_cy      = 0.198,
        eye_right_cx     = 0.562,
        eye_right_cy     = 0.198,
        eye_rx           = 0.060,
        eye_ry           = 0.038,
        eye_contrast     = 0.10,
        eye_cool_b       = 0.04,
        eye_cool_r       = 0.025,
        bg_mid_lo        = 0.28,
        bg_mid_hi        = 0.68,
        bg_green_lift    = 0.045,
        bg_blue_lift     = 0.028,
        blur_radius      = 4.5,
        opacity          = 0.46,
    )

    # Session 80: Andrea del Sarto golden sfumato pass
    print("Andrea del Sarto golden sfumato pass (session 80)...")
    p.andrea_del_sarto_golden_sfumato_pass(
        flesh_mid_lo    = 0.45,
        flesh_mid_hi    = 0.78,
        gold_r_boost    = 0.050,
        gold_g_boost    = 0.028,
        sfumato_blur    = 5.5,
        edge_grad_lo    = 0.06,
        edge_grad_hi    = 0.22,
        harmony_sat_cap = 0.85,
        harmony_pull    = 0.055,
        blur_radius     = 5.0,
        opacity         = 0.46,
    )

    # Session 81 NEW: Chardin granular intimacy pass
    # Applied after del Sarto's golden warmth to introduce Chardin's quiet
    # counter-pressure: the patient granular texture that restores intimacy after
    # the accumulation of successive warm chromatic layers.  The granular dab
    # scatter redistributes existing colour into micro-touches (sampling pixel
    # neighbourhoods with random offsets, then light Gaussian smoothing so the
    # dabs merge at their edges -- not isolated dots, but individual touches that
    # cohere).  The atmospheric muting pull draws slightly over-saturated passages
    # toward Chardin's warm-gray center.  The luminance cap gently suppresses
    # specular peaks to the restrained warm-ivory register.
    # Opacity 0.34 -- Chardin's intimacy is accumulative; never intrusive.
    print("Chardin granular intimacy pass (session 81 NEW)...")
    p.chardin_granular_intimacy_pass(
        dab_radius     = 3.5,
        dab_density    = 0.52,
        mute_strength  = 0.18,
        lum_cap        = 0.88,
        lum_cap_str    = 0.26,
        warm_gray_r    = 0.70,
        warm_gray_g    = 0.66,
        warm_gray_b    = 0.55,
        opacity        = 0.34,
        rng_seed       = 81,
    )

    # Session 81 IMPROVED: edge_lost_and_found_pass with gradient_selectivity
    # gradient_selectivity=0.65 gates the found-zone sharpening by local luminance
    # gradient magnitude.  Only pixels on actual form boundaries (nose bridge, lip
    # line, eye contour, cheekbone ridge) receive the full unsharp-mask sharpening.
    # Smooth interior flesh passages are left undisturbed, eliminating the subtle
    # noise amplification that was visible in sessions 24–80 (the unsharp mask
    # found and enhanced brush-texture seams from earlier passes in the smooth
    # midtone flesh).  The lost zone (periphery) remains unchanged -- full
    # Gaussian softening as before.
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

    out_path = os.path.join(out_dir, "mona_lisa_s81.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
