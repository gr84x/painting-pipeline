"""
paint_mona_lisa_s64.py — Session 64 portrait painting.

Paints the Mona Lisa-inspired portrait using the full stroke-engine pipeline,
enhanced with session-64 additions:

  - vigee_le_brun_pearlescent_grace_pass()  — NEW (session 64) Vigée Le Brun
                                               skin technique: warm rose bloom
                                               in lit midtones, cool pearl shift
                                               in brightest highlights, warm
                                               rose-violet shadow warmth.
                                               Applied after build_form() to
                                               give the skin the characteristic
                                               pearlescent inner glow of her
                                               18th-century court portraiture.

  - subsurface_scatter_pass()               — NEW (session 64) physiologically
                                               accurate subsurface light
                                               scattering: red-orange Gaussian
                                               bloom in lit skin midtones,
                                               deep-red penumbra warmth at the
                                               terminator, cool recovery in the
                                               deepest shadows.  Applied before
                                               the Vigée Le Brun pass to
                                               establish the physical SSS layer
                                               beneath the artist's surface
                                               treatment.

  - parmigianino_serpentine_elegance_pass() — (session 62) cool porcelain skin,
                                               lavender shadows, silver highlights

  - translucent_gauze_pass()               — (session 62) Renaissance velo over
                                               neckline / chest zone

  - canaletto_luminous_veduta_pass()        — (session 63) cerulean sky lift,
                                               warm stone push, cool canal-silver

  - old_master_varnish_pass()              — (session 63) aged amber varnish
                                               amber tint, edge oxidation, highlight
                                               desaturation

  - sfumato_thermal_gradient_pass()         — (session 60) warm foreground /
                                               cool distance depth gradient

  - sfumato_veil_pass()                     — Leonardo edge dissolution

Session 64 artistic character:
  The random artist inspiration for this session is Élisabeth Louise Vigée Le
  Brun (1755–1842), whose pearlescent skin treatment introduces a layer of
  warm rose luminosity that enriches the SSS base.  The subsurface scatter pass
  establishes the physiologically accurate red-orange bloom in the lit midtone
  zone (the quality of blood and capillaries seen through translucent skin),
  then the Vigée Le Brun pass overlays her characteristic rose-ivory surface
  quality — slightly cooler and more delicate than raw SSS.  Together they
  create a skin that reads as both physically real (SSS depth) and aesthetically
  luminous (Vigée Le Brun surface) — the combination approaches the skin
  quality that made her female portraits uniquely radiant.

  As in session 63, canaletto_luminous_veduta_pass() articulates the
  background landscape, and old_master_varnish_pass() draws the entire image
  into a warm amber key as the final tonal unifier.
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
# (identical composition to s63 — same portrait, new passes applied)
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
                dx = (x - cx) / max(rx, 1)
                dy = (y - cy) / max(ry, 1)
                if dx * dx + dy * dy <= 1.0:
                    ref[y, x] = veg_c

    # ─────────────────────────────────────────────────────────────────────────
    # Figure
    # ─────────────────────────────────────────────────────────────────────────

    fig_cx  = int(W * 0.54)
    fig_top = int(H * 0.06)

    # ── Torso — dark forest-green / blue-black dress ──────────────────────────
    torso_top    = int(H * 0.36)
    torso_bottom = H - 10
    dress_lit    = np.array([0.05, 0.18, 0.14])
    dress_shadow = np.array([0.03, 0.06, 0.10])

    for y in range(torso_top, torso_bottom):
        taper   = (y - torso_top) / max(1, torso_bottom - torso_top)
        hw      = int(W * (0.14 + taper * 0.12))
        x_shift = int(W * 0.018)
        for x in range(max(0, fig_cx - hw - x_shift), min(W, fig_cx + hw)):
            side_t = (x - (fig_cx - x_shift)) / (hw * 2.0)
            col = dress_lit * (1 - side_t * 0.85) + dress_shadow * side_t * 0.85
            ref[y, x] = col

    # ── Gauze wrap — semi-transparent over chest ──────────────────────────────
    gauze_c = np.array([0.22, 0.30, 0.25])
    for y in range(int(H * 0.38), int(H * 0.52)):
        for x in range(fig_cx - int(W * 0.18), fig_cx + int(W * 0.13)):
            if 0 <= x < W:
                gm = 0.18 * max(0.0, 1 - abs(x - (fig_cx - int(W * 0.02))) / (W * 0.14))
                ref[y, x] = ref[y, x] * (1 - gm) + gauze_c * gm

    # ── Amber neckline trim ───────────────────────────────────────────────────
    neck_y = int(H * 0.405)
    trim_c = np.array([0.80, 0.56, 0.20])
    for y in range(neck_y - 3, neck_y + 7):
        if 0 <= y < H:
            for x in range(fig_cx - int(W * 0.09), fig_cx + int(W * 0.07)):
                if 0 <= x < W:
                    ref[y, x] = trim_c

    # ── Skin tones ────────────────────────────────────────────────────────────
    skin_light  = np.array([0.90, 0.78, 0.56])
    skin_shadow = np.array([0.48, 0.35, 0.22])

    # Neck
    neck_cx = fig_cx - int(W * 0.012)
    neck_hw = int(W * 0.055)
    for y in range(int(H * 0.28), int(H * 0.40)):
        for x in range(neck_cx - neck_hw, neck_cx + neck_hw):
            if 0 <= x < W:
                lt = max(0.0, 1 - abs(x - (neck_cx - neck_hw // 4)) / (neck_hw * 0.8))
                ref[y, x] = skin_shadow * (1 - lt) + skin_light * lt

    # ── Face ─────────────────────────────────────────────────────────────────
    face_cx = fig_cx - int(W * 0.015)
    face_cy = int(H * 0.196)
    face_rx = int(W * 0.125)
    face_ry = int(W * 0.168)

    for y in range(face_cy - face_ry - 10, face_cy + face_ry + 10):
        for x in range(face_cx - face_rx - 10, face_cx + face_rx + 10):
            if 0 <= y < H and 0 <= x < W:
                dx = (x - face_cx) / face_rx
                dy = (y - face_cy) / face_ry
                temple_factor = 1.0 + max(0.0, -dy) * 0.25
                d = (dx * temple_factor) ** 2 + dy * dy
                if d <= 1.06:
                    nl  = max(0.0, min(1.0, (-0.58 * dx - 0.52 * dy) * 1.45 + 0.30))
                    col = skin_shadow * (1 - nl) + skin_light * nl
                    fade = max(0.0, 1.0 - (d - 0.86) / 0.20) if d > 0.86 else 1.0
                    ref[y, x] = ref[y, x] * (1 - fade) + col * fade

    # ── Hair ─────────────────────────────────────────────────────────────────
    hair_c = np.array([0.18, 0.11, 0.05])
    hair_s = np.array([0.06, 0.04, 0.02])
    for y in range(face_cy - face_ry - 8, face_cy + int(face_ry * 0.70)):
        for x in range(face_cx - int(face_rx * 1.7), face_cx + int(face_rx * 1.6)):
            if 0 <= y < H and 0 <= x < W:
                fdx    = (x - face_cx) / face_rx
                fdy    = (y - face_cy) / face_ry
                face_d = fdx * fdx + fdy * fdy
                outer_d = ((x - face_cx) / (face_rx * 1.58)) ** 2 + \
                          ((y - face_cy) / (face_ry * 1.05)) ** 2
                if outer_d <= 1.05 and face_d >= 0.88:
                    ht = max(0.0, (x - face_cx) / (face_rx + W * 0.01))
                    ref[y, x] = hair_c * (1 - ht * 0.42) + hair_s * ht * 0.42

    # ── Veil ─────────────────────────────────────────────────────────────────
    veil_c = np.array([0.07, 0.05, 0.08])
    for y in range(face_cy - face_ry - 2, face_cy + int(face_ry * 0.32)):
        for x in range(face_cx - int(face_rx * 1.55), face_cx + int(face_rx * 1.45)):
            if 0 <= y < H and 0 <= x < W:
                fdx = (x - face_cx) / face_rx
                fdy = (y - face_cy) / face_ry
                if fdx * fdx + fdy * fdy >= 0.88:
                    ref[y, x] = veil_c * 0.85 + ref[y, x] * 0.15

    # ── Eyes ─────────────────────────────────────────────────────────────────
    eye_sep = int(face_rx * 0.44)
    eye_y   = face_cy - int(face_ry * 0.06)
    eye_rx  = int(face_rx * 0.22)
    eye_ry  = int(face_ry * 0.10)
    iris_c  = np.array([0.10, 0.08, 0.06])
    lid_c   = np.array([0.12, 0.09, 0.07])

    for ex in [face_cx - eye_sep, face_cx + eye_sep]:
        for dy_e in range(-eye_ry - 2, eye_ry + 3):
            for dx_e in range(-eye_rx - 2, eye_rx + 3):
                ey  = eye_y + dy_e
                ex2 = ex + dx_e
                if 0 <= ey < H and 0 <= ex2 < W:
                    de = (dx_e / eye_rx) ** 2 + (dy_e / eye_ry) ** 2
                    if de <= 1.05:
                        col    = lid_c if abs(dy_e) > eye_ry * 0.55 else iris_c
                        fade_e = max(0.0, 1.0 - de * 0.55)
                        ref[ey, ex2] = ref[ey, ex2] * (1 - fade_e) + col * fade_e

    # ── Nose ─────────────────────────────────────────────────────────────────
    nose_cx = face_cx + int(face_rx * 0.06)
    nose_cy = face_cy + int(face_ry * 0.26)
    nose_c  = np.array([0.54, 0.38, 0.26])
    for dy_n in range(-int(face_ry * 0.05), int(face_ry * 0.05) + 1):
        for dx_n in range(-int(face_rx * 0.12), int(face_rx * 0.12) + 1):
            nx, ny = nose_cx + dx_n, nose_cy + dy_n
            if 0 <= ny < H and 0 <= nx < W:
                dn = (dx_n / (face_rx * 0.11)) ** 2 + (dy_n / (face_ry * 0.045)) ** 2
                if dn <= 1.0:
                    ref[ny, nx] = ref[ny, nx] * 0.45 + nose_c * 0.55

    # ── Lips — closed, ambiguous corners (the Mona Lisa smile) ───────────────
    lip_cx = face_cx + int(face_rx * 0.05)
    lip_cy = face_cy + int(face_ry * 0.48)
    lip_c  = np.array([0.60, 0.36, 0.26])

    for dy_l in range(-int(face_ry * 0.055), int(face_ry * 0.058) + 1):
        for dx_l in range(-int(face_rx * 0.29), int(face_rx * 0.29) + 1):
            lx = lip_cx + dx_l
            ly = lip_cy + dy_l
            if 0 <= ly < H and 0 <= lx < W:
                bow = abs(dx_l) / max(1, face_rx * 0.26)
                lry = face_ry * 0.050 * (1.0 + 0.14 * bow ** 2)
                dl  = (dx_l / (face_rx * 0.27)) ** 2 + (dy_l / lry) ** 2
                if dl <= 1.0:
                    fade_l = max(0.0, 1.0 - dl * 0.60)
                    ref[ly, lx] = ref[ly, lx] * (1 - fade_l) + lip_c * fade_l

    # ── Chin shadow ───────────────────────────────────────────────────────────
    chin_cy = face_cy + int(face_ry * 0.82)
    chin_c  = np.array([0.44, 0.30, 0.18])
    for dy_c in range(-int(face_ry * 0.10), int(face_ry * 0.06) + 1):
        for dx_c in range(-int(face_rx * 0.44), int(face_rx * 0.44) + 1):
            cx2, cy2 = face_cx + dx_c, chin_cy + dy_c
            if 0 <= cy2 < H and 0 <= cx2 < W:
                dc = (dx_c / (face_rx * 0.43)) ** 2 + (dy_c / (face_ry * 0.09)) ** 2
                if dc <= 1.0:
                    ref[cy2, cx2] = ref[cy2, cx2] * 0.55 + chin_c * 0.45

    # ── Hands ─────────────────────────────────────────────────────────────────
    hand_cx = fig_cx - int(W * 0.038)
    hand_cy = int(H * 0.725)
    hrx     = int(face_rx * 0.70)
    hry     = int(face_ry * 0.35)
    for dy_h in range(-hry, hry + 1):
        for dx_h in range(-hrx, hrx + 1):
            hx = hand_cx + dx_h
            hy = hand_cy + dy_h
            if 0 <= hy < H and 0 <= hx < W:
                dh = (dx_h / hrx) ** 2 + (dy_h / hry) ** 2
                if dh <= 1.0:
                    nl  = max(0.0, min(1.0, 0.52 - dx_h / (hrx * 1.85)))
                    col = skin_shadow * (1 - nl) + skin_light * nl
                    fd  = max(0.0, 1.0 - (dh - 0.76) / 0.24) if dh > 0.76 else 1.0
                    ref[hy, hx] = ref[hy, hx] * (1 - fd) + col * fd

    img = Image.fromarray((np.clip(ref, 0, 1) * 255).astype(np.uint8), "RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=3.2))
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Painting pipeline
# ─────────────────────────────────────────────────────────────────────────────

def paint(out_dir: str = ".") -> str:
    print("Building synthetic reference…")
    ref = make_reference()
    ref_path = os.path.join(out_dir, "mona_lisa_s64_ref.png")
    ref.save(ref_path)
    print(f"  Reference saved: {ref_path}")

    print("Initialising Painter…")
    p = Painter(W, H)

    # ── Warm ochre imprimatura (Leonardo's ground) ────────────────────────────
    print("Toning ground (warm ochre imprimatura)…")
    p.tone_ground((0.54, 0.46, 0.28), texture_strength=0.05)

    # ── Underpainting — dead-colour value structure ───────────────────────────
    print("Underpainting…")
    p.underpainting(ref, stroke_size=55, n_strokes=300)

    # ── Block in — colour masses ──────────────────────────────────────────────
    print("Block in (large)…")
    p.block_in(ref, stroke_size=40, n_strokes=550)

    print("Block in (medium)…")
    p.block_in(ref, stroke_size=24, n_strokes=700)

    # ── Build form ────────────────────────────────────────────────────────────
    print("Build form…")
    p.build_form(ref, stroke_size=14, n_strokes=1100)

    print("Build form (fine)…")
    p.build_form(ref, stroke_size=7, n_strokes=800)

    # Save base checkpoint
    base_path = os.path.join(out_dir, "mona_lisa_s64_base.png")
    p.save(base_path)
    print(f"  Base painting saved: {base_path}")

    # ── Session 64: Subsurface scatter pass (artistic improvement) ────────────
    # Applied first, before any artist-specific skin pass.  This establishes the
    # physiologically accurate SSS layer — the red-orange Gaussian bloom in the
    # lit skin midtones that is the physical reality of light scattering through
    # skin.  scatter_radius=10 at portrait scale gives a soft, natural bloom that
    # covers a 10-pixel radius (~6mm at the painting's DPI) — realistic for
    # facial skin SSS path length.  opacity=0.48 is deliberately moderate: the
    # SSS effect should be present and warm the skin, but not dominate; the
    # Vigée Le Brun pass will layer its rose-ivory surface quality on top.
    print("Subsurface scatter pass (session 64)…")
    p.subsurface_scatter_pass(
        scatter_strength = 0.10,    # moderate red-orange bloom
        scatter_radius   = 10.0,    # soft, naturalistic scatter path
        scatter_low      = 0.42,
        scatter_high     = 0.82,
        penumbra_warm    = 0.05,    # warm the terminator edge
        shadow_cool      = 0.03,    # cool the deepest void
        opacity          = 0.48,
    )

    # ── Session 64: Vigée Le Brun pearlescent grace pass ─────────────────────
    # Applied after SSS.  The SSS pass has already established the physical
    # red-orange glow beneath the surface; this pass adds Vigée Le Brun's
    # distinctive surface treatment — the rose-ivory midtone warmth and the
    # cool pearl highlight quality.  rose_bloom_strength=0.08 is gentler than
    # the SSS scatter (which is the primary warming pass); this is the delicate
    # 18th-century court portrait overlay.  pearl_highlight=0.05 introduces
    # the nacre shimmer in the very brightest pixels.
    print("Vigée Le Brun pearlescent grace pass (session 64)…")
    p.vigee_le_brun_pearlescent_grace_pass(
        rose_bloom_strength = 0.08,   # delicate rose overlay
        pearl_highlight     = 0.05,   # subtle nacre shimmer
        shadow_warmth       = 0.03,   # warm rose-violet shadows
        midtone_low         = 0.45,
        midtone_high        = 0.82,
        opacity             = 0.60,
    )

    # ── Session 63: Canaletto luminous veduta pass ────────────────────────────
    print("Canaletto luminous veduta pass (session 63)…")
    p.canaletto_luminous_veduta_pass(
        sky_lift   = 0.14,
        stone_warm = 0.10,
        water_cool = 0.10,
        sky_band   = 0.50,
        opacity    = 0.58,
    )

    # ── Parmigianino serpentine elegance pass (session 62) ────────────────────
    print("Parmigianino serpentine elegance pass (session 62)…")
    p.parmigianino_serpentine_elegance_pass(
        porcelain_strength = 0.09,
        lavender_shadow    = 0.07,
        silver_highlight   = 0.06,
        opacity            = 0.52,
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

    out_path = os.path.join(out_dir, "mona_lisa_s64_final.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
    print("Done:", result)
