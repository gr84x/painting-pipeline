"""
paint_mona_session25.py — Enigmatic half-length portrait, session-25 technique.

Renders the Mona Lisa composition entirely in PIL/numpy — no scipy dependency —
using a multi-pass simulation of the NEOCLASSICAL / Leonardesque pipeline:

  1. Warm ochre ground
  2. Synthetic reference build (landscape + figure)
  3. Stroke-simulation via Gaussian blur chains and directional smear
  4. porcelain_skin_pass (PIL bilateral approximation)
  5. tonal_compression_pass (S-curve value mapping)
  6. sfumato_veil (repeated Gaussian + alpha blend)
  7. atmospheric_depth (distance-weighted desaturation)
  8. Amber unifying glaze
  9. Vignette + crackle finish

Output: mona_session25.png
"""

import math
import random
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

W, H = 780, 1080
rng = random.Random(42)


# ─────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────────

def arr_to_img(a: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8), "RGB")


def img_to_arr(img: Image.Image) -> np.ndarray:
    return np.array(img).astype(np.float32) / 255.0


def lum(arr):
    return 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]


def gaussian_blur_arr(arr, radius):
    img = arr_to_img(arr)
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
    return img_to_arr(blurred)


# ─────────────────────────────────────────────────────────────────────────────
# Reference image  (reuses the geometry from run_leonardesque_enigmatic.py)
# ─────────────────────────────────────────────────────────────────────────────

def make_reference() -> np.ndarray:
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # Sky gradient: blue-grey, slightly warmer near horizon
    sky_top = np.array([0.52, 0.58, 0.70])
    sky_hor = np.array([0.64, 0.67, 0.72])
    for y in range(H):
        t = min(1.0, y / (H * 0.55))
        ref[y] = sky_top * (1 - t) + sky_hor * t

    # Haze band near horizon — left slightly higher (uncanny mismatch)
    for x in range(W):
        hor_l = int(H * 0.38)
        hor_r = int(H * 0.42)
        hor_y = hor_l + int((hor_r - hor_l) * x / W)
        haze = np.array([0.76, 0.80, 0.86])
        for y in range(max(0, hor_y - 28), min(H, hor_y + 18)):
            band_t = max(0.0, 1.0 - abs(y - hor_y) / 28.0) ** 1.4
            ref[y, x] = ref[y, x] * (1 - band_t * 0.55) + haze * band_t * 0.55

    # Rocky mid-distance terrain
    terrain = np.array([0.30, 0.35, 0.24])
    rock    = np.array([0.42, 0.40, 0.32])
    for x in range(W):
        hor_l = int(H * 0.41)
        hor_r = int(H * 0.46)
        hor_y = hor_l + int((hor_r - hor_l) * x / W)
        for y in range(hor_y, min(H, hor_y + int(H * 0.14))):
            t = (y - hor_y) / (H * 0.14)
            ref[y, x] = terrain * (1 - t) + rock * t

    # River — cool steel-blue in left middle distance
    river_y  = int(H * 0.46)
    river_hw = int(H * 0.020)
    river_cx = int(W * 0.33)
    river_w  = int(W * 0.24)
    river_c  = np.array([0.38, 0.46, 0.60])
    for y in range(river_y - river_hw, river_y + river_hw):
        if 0 <= y < H:
            for x in range(max(0, river_cx - river_w), min(W, river_cx + river_w)):
                et = max(0.0, 1.0 - abs(y - river_y) / river_hw)
                ref[y, x] = ref[y, x] * (1 - et * 0.62) + river_c * et * 0.62

    # Winding road / path on left side
    path_c = np.array([0.55, 0.50, 0.38])
    for frac in range(0, W // 2):
        x = frac
        pcx = int(W * 0.14 + (frac / (W * 0.48)) ** 1.4 * W * 0.11
                  + math.sin(frac / (W * 0.12)) * W * 0.025)
        pw = max(3, int(W * 0.038 * (1.0 - frac / (W * 0.50)) + 4))
        mid_y_l = int(H * 0.43)
        for y in range(mid_y_l - int(H * 0.06), mid_y_l + int(H * 0.04)):
            if 0 <= y < H:
                dist = abs(x - pcx)
                if dist <= pw and 0 <= x < W:
                    pt = max(0.0, 1.0 - dist / pw)
                    ref[y, x] = ref[y, x] * (1 - pt * 0.50) + path_c * pt * 0.50

    # Foreground dark earth
    fg_start = int(H * 0.80)
    fg_c     = np.array([0.24, 0.20, 0.14])
    for y in range(fg_start, H):
        t = (y - fg_start) / (H - fg_start)
        ref[y] = ref[y] * (1 - t * 0.8) + fg_c * t * 0.8

    # Parapet / ledge at very bottom
    parapet_top = int(H * 0.89)
    parapet_c   = np.array([0.18, 0.15, 0.10])
    for y in range(parapet_top, H):
        t = (y - parapet_top) / (H - parapet_top)
        ref[y] = ref[y] * (1 - t * 0.65) + parapet_c * t * 0.65

    # Figure: dark forest-green / blue-black dress
    fig_cx    = int(W * 0.545)
    torso_w   = int(W * 0.255)
    torso_top = int(H * 0.340)
    torso_btm = H - 20
    dress_lit = np.array([0.08, 0.23, 0.17])
    dress_shd = np.array([0.03, 0.07, 0.13])
    for y in range(torso_top, torso_btm):
        taper = (y - torso_top) / max(1, torso_btm - torso_top)
        hw = int(torso_w * (0.66 + taper * 0.34))
        for x in range(max(0, fig_cx - hw), min(W, fig_cx + hw)):
            st = max(0.0, (x - fig_cx) / max(hw, 1))
            col = dress_lit * (1 - st * 0.65) + dress_shd * st * 0.65
            ref[y, x] = col

    # Gauze wrap
    gauze_c = np.array([0.26, 0.35, 0.28])
    for y in range(int(H * 0.360), int(H * 0.510)):
        for x in range(fig_cx - int(torso_w * 0.78), fig_cx + int(torso_w * 0.52)):
            if 0 <= x < W:
                gm = 0.20 * max(0.0, 1.0 - abs(x - fig_cx) / (torso_w * 0.62))
                ref[y, x] = ref[y, x] * (1 - gm) + gauze_c * gm

    # Amber neckline trim
    neck_y  = int(H * 0.393)
    trim_c  = np.array([0.80, 0.56, 0.18])
    trim_hw = int(torso_w * 0.37)
    for y in range(neck_y - 3, neck_y + 6):
        if 0 <= y < H:
            for x in range(fig_cx - trim_hw, fig_cx + int(torso_w * 0.30)):
                if 0 <= x < W:
                    ref[y, x] = trim_c

    # Skin
    skin_lit = np.array([0.90, 0.76, 0.53])
    skin_shd = np.array([0.48, 0.34, 0.22])

    # Neck
    neck_cx = fig_cx - int(W * 0.008)
    neck_hw = int(W * 0.053)
    for y in range(int(H * 0.275), int(H * 0.385)):
        for x in range(neck_cx - neck_hw, neck_cx + neck_hw):
            if 0 <= x < W:
                lt = max(0.0, 1.0 - abs(x - (neck_cx - neck_hw // 4)) / (neck_hw * 0.80))
                ref[y, x] = skin_shd * (1 - lt) + skin_lit * lt

    # Face — oval, upper-left lighting
    face_cx = fig_cx - int(W * 0.018)
    face_cy = int(H * 0.197)
    face_rx = int(W * 0.124)
    face_ry = int(W * 0.164)
    for y in range(face_cy - face_ry - 10, face_cy + face_ry + 10):
        for x in range(face_cx - face_rx - 10, face_cx + face_rx + 10):
            if 0 <= y < H and 0 <= x < W:
                dx = (x - face_cx) / face_rx
                dy = (y - face_cy) / face_ry
                d  = dx * dx + dy * dy
                if d <= 1.06:
                    nl  = max(0.0, min(1.0, (-0.68 * dx - 0.52 * dy) * 1.45 + 0.28))
                    col = skin_shd * (1 - nl) + skin_lit * nl
                    fade = (max(0.0, 1.0 - (d - 0.84) / 0.22) if d > 0.84 else 1.0)
                    ref[y, x] = ref[y, x] * (1 - fade) + col * fade

    # Hair
    hair_lit = np.array([0.22, 0.13, 0.06])
    hair_shd = np.array([0.06, 0.04, 0.01])
    hair_side_x = int(W * 0.082)
    hair_btm    = face_cy + int(face_ry * 1.05)
    for y in range(face_cy - face_ry - 14, hair_btm):
        for x in range(face_cx - face_rx - hair_side_x,
                       face_cx + face_rx + int(W * 0.062)):
            if 0 <= y < H and 0 <= x < W:
                fdx = (x - face_cx) / face_rx
                fdy = (y - face_cy) / face_ry
                face_d = fdx * fdx + fdy * fdy
                wave = 0.03 * math.sin((y - face_cy) / (face_ry * 0.28))
                outer_rx = face_rx + hair_side_x
                outer_ry = face_ry + int(face_ry * 0.18)
                outer_d  = ((x - face_cx) / outer_rx + wave) ** 2 + \
                           ((y - face_cy) / outer_ry) ** 2
                if outer_d <= 1.05 and face_d >= 0.84:
                    ht  = max(0.0, (x - face_cx) / (face_rx + int(W * 0.012)))
                    col = hair_lit * (1 - ht * 0.55) + hair_shd * ht * 0.55
                    ref[y, x] = col

    # Dark veil over crown
    veil_c = np.array([0.07, 0.05, 0.08])
    for y in range(face_cy - face_ry - 12, face_cy + int(face_ry * 0.52)):
        for x in range(face_cx - face_rx - int(W * 0.036),
                       face_cx + face_rx + int(W * 0.024)):
            if 0 <= y < H and 0 <= x < W:
                fdx = (x - face_cx) / face_rx
                fdy = (y - face_cy) / face_ry
                if fdx * fdx + fdy * fdy >= 0.86:
                    ref[y, x] = veil_c

    # Eyes
    eye_sep = int(face_rx * 0.46)
    eye_y   = face_cy - int(face_ry * 0.065)
    eye_rx  = int(face_rx * 0.30)
    eye_ry  = int(face_ry * 0.148)
    iris_c  = np.array([0.08, 0.06, 0.04])
    sclera  = np.array([0.84, 0.77, 0.64])
    lid_shd = np.array([0.06, 0.04, 0.02])
    for ex in [face_cx - eye_sep, face_cx + eye_sep]:
        for dy_e in range(-eye_ry - 3, eye_ry + 4):
            for dx_e in range(-eye_rx - 3, eye_rx + 4):
                ey  = eye_y + dy_e
                ex2 = ex + dx_e
                if 0 <= ey < H and 0 <= ex2 < W:
                    de_full = (dx_e / eye_rx) ** 2 + (dy_e / eye_ry) ** 2
                    de_iris = (dx_e / (eye_rx * 0.50)) ** 2 + \
                              (dy_e / (eye_ry * 0.52)) ** 2
                    if de_full <= 1.0:
                        if de_iris <= 1.0:
                            ref[ey, ex2] = iris_c
                        else:
                            t = min(1.0, (de_full - 0.45) / 0.55)
                            ref[ey, ex2] = sclera * (1 - t * 0.5) + iris_c * t * 0.5
                lid_dy = dy_e + eye_ry - 2
                if (0 <= lid_dy <= 4
                        and abs(dx_e) <= eye_rx
                        and 0 <= eye_y - eye_ry + lid_dy < H
                        and 0 <= ex + dx_e < W):
                    ref[eye_y - eye_ry + lid_dy, ex + dx_e] = lid_shd

    # Lips — ambiguous subtle curve
    lip_cx = face_cx + int(face_rx * 0.030)
    lip_cy = face_cy + int(face_ry * 0.470)
    lip_c  = np.array([0.72, 0.34, 0.22])
    for dy_l in range(-int(face_ry * 0.072), int(face_ry * 0.072) + 1):
        for dx_l in range(-int(face_rx * 0.32), int(face_rx * 0.32) + 1):
            lx = lip_cx + dx_l
            ly = lip_cy + dy_l
            if 0 <= ly < H and 0 <= lx < W:
                bow    = abs(dx_l) / (face_rx * 0.26)
                lry    = face_ry * (0.048 + 0.016 * bow * bow)
                corner = 0.015 * bow * bow
                dl = (dx_l / (face_rx * 0.268)) ** 2 + \
                     ((dy_l + corner * face_ry) / lry) ** 2
                if dl <= 1.0:
                    fade_l = max(0.0, 1.0 - dl * 0.55)
                    ref[ly, lx] = ref[ly, lx] * (1 - fade_l) + lip_c * fade_l

    # Hands — folded in lower centre
    hand_cx = fig_cx - int(W * 0.042)
    hand_cy = int(H * 0.735)
    hrx = int(face_rx * 0.70)
    hry = int(face_ry * 0.37)
    for dy_h in range(-hry, hry + 1):
        for dx_h in range(-hrx, hrx + 1):
            hx = hand_cx + dx_h
            hy = hand_cy + dy_h
            if 0 <= hy < H and 0 <= hx < W:
                dh = (dx_h / hrx) ** 2 + (dy_h / hry) ** 2
                if dh <= 1.0:
                    nl  = max(0.0, min(1.0, 0.54 - dx_h / (hrx * 1.75)))
                    col = skin_shd * (1 - nl) + skin_lit * nl
                    fd  = (max(0.0, 1.0 - (dh - 0.76) / 0.24) if dh > 0.76 else 1.0)
                    ref[hy, hx] = ref[hy, hx] * (1 - fd) + col * fd

    return np.clip(ref, 0, 1)


# ─────────────────────────────────────────────────────────────────────────────
# Painting passes — PIL-only implementations
# ─────────────────────────────────────────────────────────────────────────────

def warm_ground_tint(canvas: np.ndarray, ground: tuple, strength: float) -> np.ndarray:
    """Apply a warm ochre imprimatura over the canvas."""
    g = np.array(ground, dtype=np.float32)
    return canvas * (1 - strength) + g * strength


def stroke_blur_pass(canvas: np.ndarray, ref: np.ndarray,
                     radius: float, opacity: float, n_passes: int = 3) -> np.ndarray:
    """
    Simulate broad stroke layering: blend blurred reference into canvas.
    Models the block_in / underpainting passes.
    """
    result = canvas.copy()
    for i in range(n_passes):
        r = radius * (1.0 - i * 0.25)
        blurred = gaussian_blur_arr(ref, r)
        result = result * (1 - opacity) + blurred * opacity
        opacity *= 0.70   # subsequent passes weaker
    return result


def build_form_pass(canvas: np.ndarray, ref: np.ndarray,
                    radius: float = 3.0, opacity: float = 0.45) -> np.ndarray:
    """
    Build form with finer passes: blend sharp reference details.
    """
    # Two-scale: coarse then fine
    coarse = gaussian_blur_arr(ref, radius * 2.0)
    fine   = gaussian_blur_arr(ref, radius * 0.8)
    result = canvas * (1 - opacity * 0.6) + coarse * opacity * 0.6
    result = result * (1 - opacity * 0.4) + fine * opacity * 0.4
    return np.clip(result, 0, 1)


def atmospheric_depth_pass(canvas: np.ndarray, haze_color=(0.72, 0.77, 0.86),
                            desaturation=0.65, lightening=0.45,
                            horizon_y=0.40) -> np.ndarray:
    """
    Aerial perspective: upper-half background fades to cool haze.
    Linear blend based on vertical position.
    """
    result = canvas.copy()
    haze = np.array(haze_color, dtype=np.float32)
    for y in range(H):
        # Above horizon: strong haze. Below: none.
        hy = int(H * horizon_y)
        if y < hy:
            depth = (hy - y) / hy
            wt = depth * 0.72
            result[y] = result[y] * (1 - wt) + haze * wt
    return np.clip(result, 0, 1)


def porcelain_skin_pass(canvas: np.ndarray,
                         smooth_strength=0.60,
                         highlight_cool=0.07,
                         blush_opacity=0.10,
                         highlight_thresh=0.74,
                         blush_lo=0.40,
                         blush_hi=0.68,
                         smooth_radius=2.2) -> np.ndarray:
    """
    Ingres porcelain skin pass — PIL-based approximation.
    Smooth warm flesh zones; cool pearl at highlights; rose blush in midtones.
    """
    result = canvas.copy()
    R, G, B = result[:, :, 0], result[:, :, 1], result[:, :, 2]
    lum_arr = 0.299 * R + 0.587 * G + 0.114 * B

    # Flesh zone: warm (R > B + 0.06), mid-to-high luminance
    flesh_mask = (
        (R > B + 0.06) &
        (lum_arr > 0.28) &
        (lum_arr < 0.92)
    ).astype(np.float32)

    # Smooth
    smooth = gaussian_blur_arr(canvas, smooth_radius)
    blend  = flesh_mask[:, :, np.newaxis] * smooth_strength
    result = canvas * (1.0 - blend) + smooth * blend

    # Re-extract after smoothing
    R2, G2, B2 = result[:, :, 0], result[:, :, 1], result[:, :, 2]
    lum2 = 0.299 * R2 + 0.587 * G2 + 0.114 * B2

    # Cool pearl tint at highlights
    hl_zone = flesh_mask * np.clip(
        (lum2 - highlight_thresh) / (1.0 - highlight_thresh + 1e-8), 0, 1
    ) * highlight_cool
    result[:, :, 0] = np.clip(R2 - hl_zone * 0.02, 0, 1)
    result[:, :, 1] = np.clip(G2 - hl_zone * 0.01, 0, 1)
    result[:, :, 2] = np.clip(B2 + hl_zone * 0.06, 0, 1)

    # Rose blush in midtones
    mid_center = 0.5 * (blush_lo + blush_hi)
    blush_wt = np.clip(
        1.0 - 2.0 * np.abs(lum2 - mid_center) / (blush_hi - blush_lo + 1e-8),
        0, 1
    )
    blush_zone = flesh_mask * blush_wt * blush_opacity
    result[:, :, 0] = np.clip(result[:, :, 0] + blush_zone * 0.045, 0, 1)
    result[:, :, 1] = np.clip(result[:, :, 1] + blush_zone * 0.012, 0, 1)

    return np.clip(result, 0, 1)


def tonal_compression_pass(canvas: np.ndarray,
                            shadow_lift=0.04,
                            highlight_compress=0.96,
                            midtone_contrast=0.06,
                            midtone_lo=0.30,
                            midtone_hi=0.70) -> np.ndarray:
    """
    Academic tonal compression: lift shadows, compress highlights, S-curve midtones.
    """
    result = canvas.copy()
    lum_arr = np.maximum(
        0.299 * result[:, :, 0] + 0.587 * result[:, :, 1] + 0.114 * result[:, :, 2],
        1e-8
    )[:, :, np.newaxis]

    # Shadow lift
    lum_lifted = lum_arr * (1 - shadow_lift) + shadow_lift
    result = np.clip(result * (lum_lifted / lum_arr), 0, 1)

    # Highlight compress
    lum2 = np.maximum(
        0.299 * result[:, :, 0] + 0.587 * result[:, :, 1] + 0.114 * result[:, :, 2],
        1e-8
    )[:, :, np.newaxis]
    lum2_comp = np.minimum(lum2, highlight_compress)
    result = np.clip(result * (lum2_comp / lum2), 0, 1)

    # S-curve midtone contrast
    if midtone_contrast > 0:
        lum3 = (
            0.299 * result[:, :, 0] + 0.587 * result[:, :, 1] + 0.114 * result[:, :, 2]
        )
        mid_center = 0.5 * (midtone_lo + midtone_hi)
        mid_wt = np.clip(
            1.0 - np.abs(lum3 - mid_center) / (0.5 * (midtone_hi - midtone_lo) + 1e-8),
            0, 1
        )
        s_dir    = np.sign(lum3 - mid_center)
        s_boost  = s_dir * np.abs(lum3 - mid_center) / (mid_center + 1e-8) \
                   * mid_wt * midtone_contrast
        lum3_safe = np.maximum(lum3, 1e-8)[:, :, np.newaxis]
        lum3_new  = np.clip(lum3 + s_boost, 0, 1)[:, :, np.newaxis]
        result = np.clip(result * (lum3_new / lum3_safe), 0, 1)

    return result


def sfumato_veil_pass(canvas: np.ndarray, n_veils=5, blur_radius=8.0,
                       veil_opacity=0.038, warmth=0.28,
                       chroma_dampen=0.18) -> np.ndarray:
    """
    Multi-layer Gaussian sfumato veil with warm amber tint.
    Each veil slightly shifts toward warm grey-amber while softening edges.
    """
    result = canvas.copy()
    # Warm amber veil colour (desaturated)
    veil_r = 0.62 + warmth * 0.08
    veil_g = 0.56 + warmth * 0.04
    veil_b = 0.44 - warmth * 0.04

    for _ in range(n_veils):
        blurred = gaussian_blur_arr(result, blur_radius)
        # Blend blurred + warm tint
        warm_tint = np.array([veil_r, veil_g, veil_b], dtype=np.float32)
        blurred_tinted = blurred * (1 - chroma_dampen) + warm_tint * chroma_dampen
        result = result * (1 - veil_opacity) + blurred_tinted * veil_opacity

    return np.clip(result, 0, 1)


def warm_cool_boundary_pass(canvas: np.ndarray, strength=0.12) -> np.ndarray:
    """Simultaneous contrast edge vibration: warm-side brighter, cool-side cooler."""
    from PIL import ImageFilter as IF
    img = arr_to_img(canvas)
    # Edge detection via PIL
    edges = img.filter(IF.FIND_EDGES)
    edges_arr = np.array(edges).astype(np.float32) / 255.0
    edge_lum = 0.299 * edges_arr[:, :, 0] + 0.587 * edges_arr[:, :, 1] + \
               0.114 * edges_arr[:, :, 2]
    edge_mask = np.clip(edge_lum, 0, 1)[:, :, np.newaxis] * strength

    R, G, B = canvas[:, :, 0], canvas[:, :, 1], canvas[:, :, 2]
    warm_side = (R > B).astype(np.float32)[:, :, np.newaxis]
    cool_side = 1.0 - warm_side

    result = canvas.copy()
    # Warm sides: boost R, damp B
    result[:, :, 0] = np.clip(R + edge_mask[:, :, 0] * warm_side[:, :, 0] * 0.06, 0, 1)
    result[:, :, 2] = np.clip(B - edge_mask[:, :, 0] * warm_side[:, :, 0] * 0.04, 0, 1)
    # Cool sides: boost B, damp R
    result[:, :, 2] = np.clip(result[:, :, 2] + edge_mask[:, :, 0] * cool_side[:, :, 0] * 0.06, 0, 1)
    result[:, :, 0] = np.clip(result[:, :, 0] - edge_mask[:, :, 0] * cool_side[:, :, 0] * 0.04, 0, 1)
    return np.clip(result, 0, 1)


def amber_glaze(canvas: np.ndarray, color=(0.62, 0.44, 0.14), opacity=0.050) -> np.ndarray:
    glaze = np.array(color, dtype=np.float32)
    return np.clip(canvas * (1 - opacity) + glaze * opacity, 0, 1)


def vignette(canvas: np.ndarray, strength=0.48) -> np.ndarray:
    ys, xs = np.ogrid[:H, :W]
    cx, cy = W / 2.0, H / 2.0
    dist = np.sqrt(((xs - cx) / (W * 0.55)) ** 2 + ((ys - cy) / (H * 0.55)) ** 2)
    vig = np.clip(1.0 - dist ** 2 * strength, 0, 1)[:, :, np.newaxis]
    return np.clip(canvas * vig, 0, 1)


def crackle_pass(canvas: np.ndarray, strength=0.022) -> np.ndarray:
    """Simulate aged crackle varnish: dark fine cracks in a random network."""
    # Use random noise to create crack-like texture
    rs = np.random.RandomState(99)
    noise = rs.random((H, W)).astype(np.float32)
    # Hard threshold creates a sparse network
    cracks = (noise > (1.0 - strength * 0.35)).astype(np.float32) * 0.28
    result = np.clip(canvas - cracks[:, :, np.newaxis] * 0.04, 0, 1)
    return result


def subsurface_glow(canvas: np.ndarray, glow_color=(0.88, 0.40, 0.22),
                     strength=0.10, radius=9.0) -> np.ndarray:
    """Translucent skin edge glow — warm R at silhouette."""
    blurred = gaussian_blur_arr(canvas, radius)
    glow = np.array(glow_color, dtype=np.float32)
    # Only apply at skin-tone edges (R-dominant)
    R = canvas[:, :, 0]
    B = canvas[:, :, 2]
    lum_arr = 0.299 * R + 0.587 * canvas[:, :, 1] + 0.114 * B
    skin_zone = ((R > B + 0.04) & (lum_arr > 0.25) & (lum_arr < 0.88)).astype(np.float32)
    glow_layer = np.clip(blurred * (1 - strength) + glow * strength, 0, 1)
    blend = skin_zone[:, :, np.newaxis] * strength * 0.5
    return np.clip(canvas * (1 - blend) + glow_layer * blend, 0, 1)


def place_lights(canvas: np.ndarray, ref: np.ndarray,
                 n_lights=40, radius=4.0) -> np.ndarray:
    """
    Place specular highlight dabs at the brightest reference pixels.
    """
    result = canvas.copy()
    ref_lum = 0.299 * ref[:, :, 0] + 0.587 * ref[:, :, 1] + 0.114 * ref[:, :, 2]
    # Find top n_lights brightest pixels
    flat_idx = np.argsort(ref_lum.ravel())[-n_lights * 8:]
    ys, xs = np.unravel_index(flat_idx, (H, W))
    highlight = np.array([0.96, 0.93, 0.84], dtype=np.float32)

    img = arr_to_img(result)
    draw = ImageDraw.Draw(img, 'RGBA')
    sampled = rng.sample(list(zip(ys.tolist(), xs.tolist())), min(n_lights, len(ys)))
    for (y, x) in sampled:
        r = rng.uniform(radius * 0.6, radius * 1.4)
        alpha = int(rng.uniform(60, 130))
        col_r = int(np.clip(highlight[0] * 255, 0, 255))
        col_g = int(np.clip(highlight[1] * 255, 0, 255))
        col_b = int(np.clip(highlight[2] * 255, 0, 255))
        draw.ellipse([(x - r, y - r), (x + r, y + r)],
                     fill=(col_r, col_g, col_b, alpha))

    result = img_to_arr(img.convert("RGB"))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Main orchestration
# ─────────────────────────────────────────────────────────────────────────────

def layered_unsharp_pass(canvas: np.ndarray, ref: np.ndarray,
                          detail_radius: float = 1.2,
                          detail_strength: float = 0.45) -> np.ndarray:
    """
    Blend sharp reference detail back over the canvas (forms a detail layer).
    Simulates the Flemish micro-detail pass — crisp edges drawn on top.
    """
    # High-pass from reference: original minus blur
    blurred = gaussian_blur_arr(ref, detail_radius * 2.5)
    high_pass = np.clip(ref - blurred + 0.5, 0, 1)
    # Add half-strength detail back to canvas
    result = np.clip(canvas + (high_pass - 0.5) * detail_strength, 0, 1)
    return result


def edge_preserve_blend(canvas: np.ndarray, ref: np.ndarray, opacity: float = 0.72,
                         edge_threshold: float = 0.08) -> np.ndarray:
    """
    Blend reference into canvas, but weight by inverse-edge-strength so sharp
    edges in the reference are composited more strongly.
    """
    from PIL import ImageFilter as IF
    img_r = arr_to_img(ref)
    edges = img_r.filter(IF.FIND_EDGES)
    edge_arr = np.array(edges).astype(np.float32) / 255.0
    edge_lum = np.clip(
        0.299 * edge_arr[:, :, 0] + 0.587 * edge_arr[:, :, 1] + 0.114 * edge_arr[:, :, 2],
        0, 1
    )
    # Strong edges get full reference; smooth areas get gentle blend
    edge_weight = np.clip(edge_lum / (edge_threshold + 0.001), 0, 1)[:, :, np.newaxis]
    blend_weight = opacity * (0.4 + 0.6 * edge_weight)
    return np.clip(canvas * (1 - blend_weight) + ref * blend_weight, 0, 1)


def oil_texture_pass(canvas: np.ndarray, strength: float = 0.06) -> np.ndarray:
    """
    Simulate oil paint surface texture: emboss + linen grain overlay.
    Uses PIL emboss filter to create directional paint ridges.
    """
    from PIL import ImageFilter as IF, ImageEnhance
    img = arr_to_img(canvas)
    # Emboss gives surface relief
    embossed = img.filter(IF.EMBOSS)
    emb_arr = np.array(embossed).astype(np.float32) / 255.0
    # High-pass: emboss is mean-grey; centre at 0.5
    texture = (emb_arr - 0.5) * strength
    return np.clip(canvas + texture, 0, 1)


def saturation_boost(canvas: np.ndarray, factor: float = 1.20) -> np.ndarray:
    """Boost saturation for richer, more painted colours."""
    from PIL import ImageEnhance
    img = arr_to_img(canvas)
    enhanced = ImageEnhance.Color(img).enhance(factor)
    return img_to_arr(enhanced)


def contrast_boost(canvas: np.ndarray, factor: float = 1.15) -> np.ndarray:
    """Increase contrast slightly for oil-paint depth."""
    from PIL import ImageEnhance
    img = arr_to_img(canvas)
    enhanced = ImageEnhance.Contrast(img).enhance(factor)
    return img_to_arr(enhanced)


def background_sfumato(canvas: np.ndarray, ref: np.ndarray,
                        horizon_y: float = 0.45,
                        blur_radius: float = 5.0,
                        strength: float = 0.55) -> np.ndarray:
    """
    Apply sfumato ONLY to the background (above horizon and to the sides of figure).
    Preserves figure clarity while giving landscape the atmospheric haze.
    """
    # Figure center and rough boundaries
    fig_cx    = int(W * 0.545)
    torso_w   = int(W * 0.30)
    torso_top = int(H * 0.310)

    # Build a background mask: 1.0 in background, 0.0 in figure region
    ys, xs = np.ogrid[:H, :W]
    fig_dist_x = np.abs(xs - fig_cx).astype(np.float32) / torso_w
    fig_dist_y = np.maximum((ys - torso_top).astype(np.float32) / (H - torso_top), 0.0)
    # Inside figure: fig_dist_x < 1 and below torso_top
    in_figure = ((fig_dist_x < 1.0) & (ys >= torso_top)).astype(np.float32)
    # Soft boundary
    bg_mask = np.clip(1.0 - in_figure, 0, 1)

    # Blur background
    blurred = gaussian_blur_arr(canvas, blur_radius)
    blend = bg_mask[:, :, np.newaxis] * strength
    return np.clip(canvas * (1 - blend) + blurred * blend, 0, 1)


def paint(out_path: str = "mona_session25.png") -> str:
    print("Building synthetic reference…")
    ref = make_reference()
    # Very mild blur for colour transition smoothing
    ref_smooth = gaussian_blur_arr(ref, 1.4)

    print("Phase 1 — Warm ochre ground…")
    canvas = warm_ground_tint(np.ones((H, W, 3), dtype=np.float32),
                               (0.75, 0.68, 0.52), strength=0.95)

    print("Phase 2 — Underpainting (grisaille value structure)…")
    # Build in layers: broad → medium → fine → near-sharp
    broad   = gaussian_blur_arr(ref_smooth, 18.0)
    medium  = gaussian_blur_arr(ref_smooth,  7.0)
    fine    = gaussian_blur_arr(ref_smooth,  3.0)
    sharper = gaussian_blur_arr(ref_smooth,  1.2)

    # Layered build toward sharpness — weighted progressive blend
    canvas = canvas * 0.15 + broad * 0.85
    canvas = canvas * 0.25 + medium * 0.75
    canvas = canvas * 0.35 + fine * 0.65
    canvas = canvas * 0.45 + sharper * 0.55
    canvas = canvas * 0.55 + ref_smooth * 0.45

    print("Phase 3 — Build form with edge emphasis…")
    canvas = edge_preserve_blend(canvas, ref_smooth, opacity=0.52,
                                  edge_threshold=0.05)
    # Final crisp composite: mostly the smoothed reference
    canvas = canvas * 0.50 + ref_smooth * 0.50

    print("Phase 4 — Saturation and contrast for oil depth…")
    canvas = saturation_boost(canvas, factor=1.18)
    canvas = contrast_boost(canvas, factor=1.12)

    print("Phase 5 — Atmospheric depth in background…")
    canvas = atmospheric_depth_pass(canvas, horizon_y=0.44)

    print("Phase 6 — Porcelain skin pass (Ingres / session-25)…")
    canvas = porcelain_skin_pass(canvas,
                                  smooth_strength=0.42,
                                  highlight_cool=0.07,
                                  blush_opacity=0.09,
                                  smooth_radius=1.5)

    print("Phase 7 — Tonal compression (session-25 random improvement)…")
    canvas = tonal_compression_pass(canvas,
                                     shadow_lift=0.03,
                                     highlight_compress=0.97,
                                     midtone_contrast=0.06)

    print("Phase 8 — Background sfumato (preserve figure clarity)…")
    canvas = background_sfumato(canvas, ref, horizon_y=0.44,
                                 blur_radius=4.5, strength=0.48)

    print("Phase 9 — Edge sfumato veils (atmospheric haze)…")
    canvas = sfumato_veil_pass(canvas, n_veils=2, blur_radius=6.0,
                                veil_opacity=0.022, warmth=0.26, chroma_dampen=0.12)
    canvas = sfumato_veil_pass(canvas, n_veils=2, blur_radius=3.5,
                                veil_opacity=0.018, warmth=0.22, chroma_dampen=0.14)

    print("Phase 10 — Oil paint surface texture…")
    canvas = oil_texture_pass(canvas, strength=0.05)

    print("Phase 11 — Detail layer (sharp features over sfumato)…")
    canvas = layered_unsharp_pass(canvas, ref_smooth,
                                   detail_radius=0.8, detail_strength=0.28)

    print("Phase 12 — Warm-cool boundary vibration…")
    canvas = warm_cool_boundary_pass(canvas, strength=0.09)

    print("Phase 13 — Subsurface skin glow…")
    canvas = subsurface_glow(canvas, strength=0.09, radius=6.5)

    print("Phase 14 — Specular lights…")
    canvas = place_lights(canvas, ref, n_lights=70, radius=2.8)

    print("Phase 15 — Amber unifying glaze…")
    canvas = amber_glaze(canvas, color=(0.62, 0.44, 0.14), opacity=0.040)

    print("Phase 16 — Vignette + crackle finish…")
    canvas = vignette(canvas, strength=0.42)
    canvas = crackle_pass(canvas, strength=0.008)

    img = arr_to_img(canvas)
    img.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "mona_session25.png"
    paint(out)
