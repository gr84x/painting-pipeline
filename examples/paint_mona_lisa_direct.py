"""
paint_mona_lisa_direct.py — Renders the described portrait directly via the
stroke engine, bypassing Blender.

A synthetic reference image is constructed in numpy/PIL to approximate the
described scene composition, then the full Renaissance/sfumato pipeline is
applied to it.  The result demonstrates:
  - sfumato_veil_pass() with the new chroma_dampen improvement (session 14)
  - Renaissance warm-earth palette with maximum wet_blend

Composition:
  - Woman seated slightly right of centre, three-quarter pose
  - Face: oval, smooth, slightly upward ambiguous expression
  - Hair: dark, centre-parted, soft waves, dark veil
  - Dress: dark forest-green / blue-black
  - Background: dreamlike geological landscape, cool haze at distance
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter


W, H = 780, 1080


def make_reference() -> Image.Image:
    """
    Build a richly-coloured synthetic reference for the stroke engine.
    Values are saturated so the engine deposits strong, visible paint.
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # ── Background sky: medium blue-grey ─────────────────────────────────────
    sky = np.array([0.40, 0.46, 0.58])
    ref[:, :] = sky

    # ── Upper distant haze — slightly lighter cool blue ───────────────────────
    for y in range(H // 3):
        t = 1.0 - (y / (H / 3))
        ref[y] = ref[y] * (1.0 - t * 0.35) + np.array([0.60, 0.64, 0.72]) * t * 0.35

    # ── Mid-distance rocky terrain: deep olive / grey-green ───────────────────
    mid_y_l = int(H * 0.50)
    mid_y_r = int(H * 0.54)
    terrain = np.array([0.28, 0.34, 0.22])
    rock    = np.array([0.38, 0.36, 0.30])
    for x in range(W):
        hor = mid_y_l + int((mid_y_r - mid_y_l) * x / W)
        for y in range(hor, min(H, hor + int(H * 0.12))):
            t = (y - hor) / (H * 0.12)
            ref[y, x] = terrain * (1 - t) + rock * t

    # ── River / water: cool dark steel-blue ───────────────────────────────────
    ry = int(H * 0.47)
    rw = int(H * 0.018)
    rcx = int(W * 0.36)
    river_c = np.array([0.36, 0.44, 0.58])
    for y in range(ry - rw, ry + rw):
        if 0 <= y < H:
            for x in range(max(0, rcx - int(W * 0.12)), min(W, rcx + int(W * 0.10))):
                et = max(0.0, 1.0 - abs(y - ry) / rw)
                ref[y, x] = ref[y, x] * (1 - et * 0.65) + river_c * et * 0.65

    # ── Winding path on left ──────────────────────────────────────────────────
    path_c = np.array([0.52, 0.48, 0.36])
    for x in range(0, W // 2):
        pcx = int(W * 0.18 + (x / (W * 0.5)) * W * 0.10)
        pw  = max(3, int(W * 0.04))
        for y in range(mid_y_l - int(H * 0.07), mid_y_l + int(H * 0.05)):
            if 0 <= y < H and 0 <= pcx - pw <= x <= pcx + pw < W:
                pt = max(0.0, 1.0 - abs(x - pcx) / pw)
                ref[y, x] = ref[y, x] * (1 - pt * 0.55) + path_c * pt * 0.55

    # ── Foreground ground: warm dark earth ───────────────────────────────────
    fg_s  = int(H * 0.82)
    fg_c  = np.array([0.24, 0.20, 0.14])
    for y in range(fg_s, H):
        t = (y - fg_s) / (H - fg_s)
        ref[y] = ref[y] * (1 - t) + fg_c * t

    # ── Figure torso: dark forest-green dress ─────────────────────────────────
    fig_cx   = int(W * 0.54)
    torso_w  = int(W * 0.26)
    torso_top    = int(H * 0.34)
    torso_bottom = H - 30
    dress_l  = np.array([0.07, 0.22, 0.17])   # lit forest-green
    dress_s  = np.array([0.04, 0.08, 0.14])   # shadow blue-black

    for y in range(torso_top, torso_bottom):
        taper_t = (y - torso_top) / max(1, torso_bottom - torso_top)
        hw = int(torso_w * (0.68 + taper_t * 0.32))
        for x in range(max(0, fig_cx - hw), min(W, fig_cx + hw)):
            side_t = max(0.0, (x - fig_cx) / max(hw, 1))
            col = dress_l * (1 - side_t * 0.6) + dress_s * side_t * 0.6
            ref[y, x] = col

    # ── Gauze wrap: semi-transparent olive-green overlay on chest ────────────
    gauze_c = np.array([0.25, 0.34, 0.28])
    for y in range(int(H * 0.36), int(H * 0.50)):
        for x in range(fig_cx - int(torso_w * 0.75), fig_cx + int(torso_w * 0.55)):
            if 0 <= x < W:
                gm = 0.22 * max(0, 1 - abs(x - fig_cx) / (torso_w * 0.65))
                ref[y, x] = ref[y, x] * (1 - gm) + gauze_c * gm

    # ── Amber neckline trim ───────────────────────────────────────────────────
    neck_y = int(H * 0.39)
    trim_c = np.array([0.78, 0.54, 0.18])
    for y in range(neck_y - 3, neck_y + 5):
        if 0 <= y < H:
            for x in range(fig_cx - int(torso_w * 0.38), fig_cx + int(torso_w * 0.32)):
                if 0 <= x < W:
                    ref[y, x] = trim_c

    # ── Skin tones ───────────────────────────────────────────────────────────
    skin_light  = np.array([0.88, 0.74, 0.52])
    skin_shadow = np.array([0.46, 0.34, 0.22])

    # Neck
    neck_cx = fig_cx - int(W * 0.01)
    neck_hw = int(W * 0.052)
    for y in range(int(H * 0.27), int(H * 0.38)):
        for x in range(neck_cx - neck_hw, neck_cx + neck_hw):
            if 0 <= x < W:
                lt = max(0.0, 1 - abs(x - (neck_cx - neck_hw // 4)) / (neck_hw * 0.8))
                ref[y, x] = skin_shadow * (1 - lt) + skin_light * lt

    # ── Face ─────────────────────────────────────────────────────────────────
    face_cx = fig_cx - int(W * 0.02)
    face_cy = int(H * 0.195)
    face_rx = int(W * 0.122)
    face_ry = int(W * 0.162)

    for y in range(face_cy - face_ry - 8, face_cy + face_ry + 8):
        for x in range(face_cx - face_rx - 8, face_cx + face_rx + 8):
            if 0 <= y < H and 0 <= x < W:
                dx = (x - face_cx) / face_rx
                dy = (y - face_cy) / face_ry
                d  = dx * dx + dy * dy
                if d <= 1.04:
                    # Light from upper-left
                    nl = max(0.0, min(1.0, (-0.65 * dx - 0.55 * dy) * 1.4 + 0.28))
                    col = skin_shadow * (1 - nl) + skin_light * nl
                    fade = max(0.0, 1.0 - (d - 0.86) / 0.18) if d > 0.86 else 1.0
                    ref[y, x] = ref[y, x] * (1 - fade) + col * fade

    # ── Hair: dark warm brown ─────────────────────────────────────────────────
    hair_c  = np.array([0.20, 0.12, 0.06])
    hair_s  = np.array([0.06, 0.04, 0.01])
    for y in range(face_cy - face_ry - 5, face_cy + int(face_ry * 0.60)):
        for x in range(face_cx - face_rx - int(W * 0.07),
                       face_cx + face_rx + int(W * 0.06)):
            if 0 <= y < H and 0 <= x < W:
                fdx = (x - face_cx) / face_rx
                fdy = (y - face_cy) / face_ry
                face_d = fdx * fdx + fdy * fdy
                outer_d = ((x - face_cx) / (face_rx + W * 0.07))**2 + \
                          ((y - face_cy) / (face_ry + W * 0.02))**2
                if outer_d <= 1.05 and face_d >= 0.88:
                    ht = max(0.0, (x - face_cx) / (face_rx + W * 0.01))
                    ref[y, x] = hair_c * (1 - ht * 0.45) + hair_s * ht * 0.45

    # ── Veil: near-black over hair ────────────────────────────────────────────
    veil_c = np.array([0.08, 0.06, 0.09])
    for y in range(face_cy - face_ry, face_cy + int(face_ry * 0.38)):
        for x in range(face_cx - face_rx - int(W * 0.03),
                       face_cx + face_rx + int(W * 0.02)):
            if 0 <= y < H and 0 <= x < W:
                fdx = (x - face_cx) / face_rx
                fdy = (y - face_cy) / face_ry
                if fdx * fdx + fdy * fdy >= 0.90:
                    ref[y, x] = veil_c

    # ── Eyes: dark heavy-lidded ────────────────────────────────────────────────
    eye_sep = int(face_rx * 0.46)
    eye_y   = face_cy - int(face_ry * 0.07)
    eye_rx  = int(face_rx * 0.21)
    eye_ry  = int(face_ry * 0.11)
    iris_c  = np.array([0.12, 0.10, 0.08])

    for ex in [face_cx - eye_sep, face_cx + eye_sep]:
        for dy_e in range(-eye_ry - 1, eye_ry + 2):
            for dx_e in range(-eye_rx - 1, eye_rx + 2):
                ey = eye_y + dy_e
                ex2 = ex + dx_e
                if 0 <= ey < H and 0 <= ex2 < W:
                    de = (dx_e / eye_rx)**2 + (dy_e / eye_ry)**2
                    if de <= 1.0:
                        fade_e = max(0.0, 1.0 - de * 0.5)
                        ref[ey, ex2] = ref[ey, ex2] * (1 - fade_e) + iris_c * fade_e

    # ── Lips: closed, warm rose ────────────────────────────────────────────────
    lip_cx = face_cx + int(face_rx * 0.04)
    lip_cy = face_cy + int(face_ry * 0.47)
    lip_c  = np.array([0.64, 0.38, 0.28])

    for dy_l in range(-int(face_ry * 0.052), int(face_ry * 0.052) + 1):
        for dx_l in range(-int(face_rx * 0.27), int(face_rx * 0.27) + 1):
            lx = lip_cx + dx_l
            ly = lip_cy + dy_l
            if 0 <= ly < H and 0 <= lx < W:
                bow = abs(dx_l) / (face_rx * 0.25)
                lry = face_ry * 0.048 * (1.0 + 0.18 * bow * bow)
                dl  = (dx_l / (face_rx * 0.26))**2 + (dy_l / lry)**2
                if dl <= 1.0:
                    fade_l = max(0.0, 1.0 - dl * 0.55)
                    ref[ly, lx] = ref[ly, lx] * (1 - fade_l) + lip_c * fade_l

    # ── Hands: folded in lower centre ─────────────────────────────────────────
    hand_cx = fig_cx - int(W * 0.04)
    hand_cy = int(H * 0.73)
    hrx     = int(face_rx * 0.68)
    hry     = int(face_ry * 0.36)
    for dy_h in range(-hry, hry + 1):
        for dx_h in range(-hrx, hrx + 1):
            hx = hand_cx + dx_h
            hy = hand_cy + dy_h
            if 0 <= hy < H and 0 <= hx < W:
                dh = (dx_h / hrx)**2 + (dy_h / hry)**2
                if dh <= 1.0:
                    nl = max(0.0, min(1.0, 0.55 - dx_h / (hrx * 1.8)))
                    col = skin_shadow * (1 - nl) + skin_light * nl
                    fd  = max(0.0, 1.0 - (dh - 0.78) / 0.22) if dh > 0.78 else 1.0
                    ref[hy, hx] = ref[hy, hx] * (1 - fd) + col * fd

    # Apply gentle blur to smooth transitions
    img = Image.fromarray((np.clip(ref, 0, 1) * 255).astype(np.uint8), "RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=2.8))
    return img


def paint() -> str:
    print("Building synthetic reference…")
    ref = make_reference()
    ref.save(os.path.join(os.path.dirname(__file__), '..', 'mona_lisa_ref.png'))

    W_r, H_r = ref.size
    print(f"  Reference: {W_r}×{H_r}")

    print("Initialising Painter…")
    p = Painter(W_r, H_r)

    # ── Leonardo ochre ground ──────────────────────────────────────────────────
    print("Toning ground (warm ochre)…")
    p.tone_ground((0.52, 0.44, 0.28), texture_strength=0.06)

    # ── Build up the painting in multiple passes ───────────────────────────────
    print("Underpainting…")
    p.underpainting(ref, stroke_size=52, n_strokes=280)

    print("Block in…")
    p.block_in(ref, stroke_size=38, n_strokes=500)

    print("Block in (tighter)…")
    p.block_in(ref, stroke_size=22, n_strokes=700)

    print("Build form…")
    p.build_form(ref, stroke_size=14, n_strokes=1000)

    print("Build form (fine)…")
    p.build_form(ref, stroke_size=7, n_strokes=700)

    print("Place lights…")
    p.place_lights(ref, stroke_size=5, n_strokes=600)

    # Save before post-processing to verify the base painting
    p.save(os.path.join(os.path.dirname(__file__), '..', 'mona_lisa_base.png'))

    # ── Sfumato veil — improved with chroma_dampen (session 14) ───────────────
    # Subtle settings: 7 veils, low opacity, so the painting reads through clearly.
    # chroma_dampen=0.22 gives the warm grey-amber edge quality of the Mona Lisa
    # under X-ray — slightly desaturated at form transitions.
    print("Sfumato veil pass (chroma_dampen improvement)…")
    p.sfumato_veil_pass(
        ref,
        n_veils       = 7,
        blur_radius   = 8.0,
        warmth        = 0.28,
        veil_opacity  = 0.05,
        edge_only     = True,
        chroma_dampen = 0.22,
    )

    # ── Warm amber unifying glaze (Leonardo's characteristic tone) ─────────────
    print("Final glaze…")
    p.glaze((0.62, 0.44, 0.14), opacity=0.06)

    # ── Finish: vignette + crackle ────────────────────────────────────────────
    print("Finishing…")
    p.finish(vignette=0.45, crackle=True)

    out_path = os.path.join(os.path.dirname(__file__), '..', 'mona_lisa_final.png')
    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint()
    print("Done:", result)
