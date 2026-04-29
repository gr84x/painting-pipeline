"""paint_s241.py -- Session 241: The Egret at Dusk (Frankenthaler Soak-Stain)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter

W, H = 520, 680

# ── Palette (Frankenthaler-inspired: luminous, transparent, lyrical) ─────────
EGRET_WHITE     = (0.96, 0.96, 0.93)   # near-white plumage with warm tint
CERULEAN        = (0.24, 0.52, 0.78)   # sky and upper water
ROSE_GOLD       = (0.86, 0.50, 0.38)   # horizon glow and water blush
WARM_OCHRE      = (0.88, 0.74, 0.32)   # sunlit horizon edge
SAGE_GREEN      = (0.44, 0.60, 0.42)   # distant reeds
DEEP_INDIGO     = (0.18, 0.24, 0.52)   # deep water shadow
LAVENDER_SHADOW = (0.66, 0.58, 0.78)   # plumage shadow side
NEAR_WHITE      = (0.94, 0.92, 0.86)   # raw canvas ground
BEAK_YELLOW     = (0.80, 0.70, 0.18)   # egret beak
EGRET_SHADOW    = (0.20, 0.26, 0.44)   # egret's reflection in water
WATER_SHIMMER   = (0.70, 0.82, 0.90)   # glassy water highlight
HORIZON_PINK    = (0.90, 0.68, 0.58)   # softest horizon blush
PALE_SKY        = (0.58, 0.74, 0.90)   # upper sky luminosity
REED_DARK       = (0.28, 0.34, 0.26)   # reed shadow


def _blend(arr, col, strength):
    s = max(0.0, min(1.0, strength))
    return arr * (1.0 - s) + np.array(col, dtype=np.float32) * s


def _ellipse(arr, cx, cy, rx, ry, color, opacity=1.0, feather=0.14):
    h, w = arr.shape[:2]
    rx, ry = max(rx, 1.0), max(ry, 1.0)
    for dy in range(-int(ry * 1.2), int(ry * 1.2) + 1):
        for dx in range(-int(rx * 1.2), int(rx * 1.2) + 1):
            px, py = int(cx + dx), int(cy + dy)
            if 0 <= px < w and 0 <= py < h:
                d = (dx / rx) ** 2 + (dy / ry) ** 2
                if d <= (1.0 + feather) ** 2:
                    alpha = max(0.0, min(1.0, (1.0 + feather - math.sqrt(d)) / (feather + 1e-6)))
                    arr[py, px] = _blend(arr[py, px], color, alpha * opacity)


def _rect(arr, x0, y0, x1, y1, color, opacity=1.0):
    h, w = arr.shape[:2]
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(w, int(x1)), min(h, int(y1))
    if x1 > x0 and y1 > y0:
        arr[y0:y1, x0:x1] = _blend(arr[y0:y1, x0:x1], color, opacity)


def _line(arr, x0, y0, x1, y1, color, thickness=1, opacity=0.88):
    h, w = arr.shape[:2]
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        t = i / steps
        x = int(x0 + t * (x1 - x0))
        y = int(y0 + t * (y1 - y0))
        for ty in range(-thickness, thickness + 1):
            for tx in range(-thickness, thickness + 1):
                if tx * tx + ty * ty <= thickness * thickness:
                    px, py = x + tx, y + ty
                    if 0 <= px < w and 0 <= py < h:
                        arr[py, px] = _blend(arr[py, px], color, opacity)


def make_reference():
    ref = np.ones((H, W, 3), dtype=np.float32) * np.array(NEAR_WHITE, dtype=np.float32)
    rng = np.random.RandomState(241)

    # ── Sky: pale cerulean at top, warming toward rose-gold at horizon ──────
    horizon_y = int(H * 0.40)
    for y in range(horizon_y):
        t = y / max(horizon_y - 1, 1)
        # Pale sky blue at top, rose-horizon blend lower
        sky_col = (np.array(PALE_SKY, dtype=np.float32) * (1.0 - t * 0.6) +
                   np.array(HORIZON_PINK, dtype=np.float32) * (t * 0.55) +
                   np.array(WARM_OCHRE, dtype=np.float32) * (t * 0.20))
        sky_col = np.clip(sky_col, 0.0, 1.0)
        ref[y, :] = sky_col

    # ── Horizon band: narrow warm rose-gold glow ─────────────────────────────
    h_band_y0 = int(H * 0.38)
    h_band_y1 = int(H * 0.43)
    for y in range(h_band_y0, h_band_y1):
        t = abs(y - (h_band_y0 + h_band_y1) / 2) / ((h_band_y1 - h_band_y0) / 2 + 1)
        glow = 1.0 - t * t
        ref[y, :] = _blend(ref[y, :], ROSE_GOLD, 0.45 * glow)
        ref[y, :] = _blend(ref[y, :], WARM_OCHRE, 0.25 * glow)

    # ── Water: cerulean reflecting sky, deepening toward indigo at bottom ───
    water_y = int(H * 0.42)
    for y in range(water_y, H):
        t = (y - water_y) / max(H - water_y - 1, 1)
        water_col = (np.array(CERULEAN, dtype=np.float32) * (1.0 - t * 0.55) +
                     np.array(DEEP_INDIGO, dtype=np.float32) * (t * 0.60))
        water_col = np.clip(water_col, 0.0, 1.0)
        ref[y, :] = water_col

    # ── Rose-gold reflection band in water (mirrors horizon) ─────────────────
    refl_y0 = int(H * 0.43)
    refl_y1 = int(H * 0.52)
    for y in range(refl_y0, refl_y1):
        t = abs(y - (refl_y0 + refl_y1) / 2) / ((refl_y1 - refl_y0) / 2 + 1)
        glow = (1.0 - t * t) * 0.55
        ref[y, :] = _blend(ref[y, :], ROSE_GOLD, glow)
        ref[y, :] = _blend(ref[y, :], HORIZON_PINK, glow * 0.60)

    # ── Water shimmer: horizontal glint bands ────────────────────────────────
    for _ in range(28):
        sy = int(rng.uniform(water_y + 10, H - 10))
        sx = int(rng.uniform(0, W - 40))
        sw = int(rng.uniform(20, 80))
        ref[sy:sy + 1, sx:sx + sw] = _blend(ref[sy:sy + 1, sx:sx + sw], WATER_SHIMMER, 0.35)

    # ── Distant reeds: right side, at horizon ────────────────────────────────
    reed_x0 = int(W * 0.65)
    for _ in range(22):
        rx = reed_x0 + int(rng.uniform(0, W - reed_x0 - 8))
        ry_base = int(H * 0.42)
        ry_top  = ry_base - int(rng.uniform(22, 58))
        rw      = int(rng.uniform(2, 5))
        # Thin vertical reed
        for ry in range(ry_top, ry_base):
            t = (ry - ry_top) / max(ry_base - ry_top, 1)
            for rx2 in range(rx, rx + rw):
                if 0 <= rx2 < W and 0 <= ry < H:
                    ref[ry, rx2] = _blend(ref[ry, rx2], SAGE_GREEN, 0.60 * (1.0 - t * 0.4))

    # Blurry reed mass for atmosphere
    for _ in range(8):
        rx = reed_x0 + int(rng.uniform(0, W - reed_x0 - 20))
        ry = int(H * 0.40)
        _ellipse(ref, rx, ry, int(rng.uniform(12, 28)), int(rng.uniform(18, 38)),
                 SAGE_GREEN, opacity=0.38, feather=0.55)

    # ── Egret body: tall bird slightly left-of-centre ────────────────────────
    body_cx = int(W * 0.40)
    body_cy = int(H * 0.60)

    # Main body mass: large white ellipse, elongated vertically
    _ellipse(ref, body_cx, body_cy, 38, 58, EGRET_WHITE, opacity=0.96, feather=0.12)
    # Slight lavender shadow on right flank
    _ellipse(ref, body_cx + 18, body_cy + 8, 22, 36, LAVENDER_SHADOW, opacity=0.30, feather=0.30)

    # Aigrette breeding plumes: trailing wisps from lower back
    for i in range(5):
        plume_x = body_cx - 12 + i * 6
        plume_y_top = body_cy + 20
        plume_y_bot = body_cy + 68 + i * 5
        plume_x_drift = body_cx - 30 + i * 8
        for frac in range(12):
            t = frac / 11.0
            px = int(plume_x + (plume_x_drift - plume_x) * t * t)
            py = int(plume_y_top + (plume_y_bot - plume_y_top) * t)
            _ellipse(ref, px, py, 3, 2, EGRET_WHITE, opacity=0.72 - t * 0.45, feather=0.60)

    # ── Neck: S-curve upward from body ───────────────────────────────────────
    # Neck follows an S: starts at top of body, curves right then left to head
    neck_pts = [
        (body_cx,      body_cy - 52),    # top of body
        (body_cx + 14, body_cy - 80),    # right curve (lower neck)
        (body_cx + 18, body_cy - 108),   # inflection
        (body_cx + 10, body_cy - 135),   # left curve (upper neck)
        (body_cx + 4,  body_cy - 160),   # head base
    ]
    for i in range(len(neck_pts) - 1):
        x0, y0 = neck_pts[i]
        x1, y1 = neck_pts[i + 1]
        steps = max(abs(x1 - x0), abs(y1 - y0), 1) * 3
        for j in range(steps):
            t = j / steps
            nx = int(x0 + (x1 - x0) * t)
            ny = int(y0 + (y1 - y0) * t)
            r = 6 - i         # thicker at base, thinner toward head
            r = max(r, 3)
            _ellipse(ref, nx, ny, r, r, EGRET_WHITE, opacity=0.90, feather=0.22)

    # ── Head: small ellipse at top of neck ───────────────────────────────────
    head_cx = body_cx + 4
    head_cy = body_cy - 165
    _ellipse(ref, head_cx, head_cy, 14, 12, EGRET_WHITE, opacity=0.95, feather=0.12)

    # ── Beak: long, pointed, angled downward toward water ────────────────────
    beak_x0 = head_cx + 8
    beak_y0 = head_cy + 4
    beak_x1 = head_cx + 38
    beak_y1 = head_cy + 28
    _line(ref, beak_x0, beak_y0, beak_x1, beak_y1, BEAK_YELLOW, thickness=2, opacity=0.92)
    # Dark tip
    _line(ref, beak_x1 - 6, beak_y1 - 4, beak_x1, beak_y1, REED_DARK, thickness=1, opacity=0.88)

    # ── Lore / eye: small yellow-green spot near eye ─────────────────────────
    _ellipse(ref, head_cx + 6, head_cy - 1, 3, 2, BEAK_YELLOW, opacity=0.82)
    _ellipse(ref, head_cx + 7, head_cy - 2, 1, 1, REED_DARK, opacity=0.90)

    # ── Legs: two grey-green legs into the water ─────────────────────────────
    leg_y_top  = body_cy + 54    # emerges from under body
    water_line = int(H * 0.76)   # where legs enter water

    # Left leg: straight into water
    leg_l_x = body_cx - 10
    _line(ref, leg_l_x, leg_y_top, leg_l_x, water_line, SAGE_GREEN, thickness=2, opacity=0.78)
    # Foot / toes
    _line(ref, leg_l_x, water_line, leg_l_x - 12, water_line + 4, SAGE_GREEN, thickness=1, opacity=0.68)
    _line(ref, leg_l_x, water_line, leg_l_x + 8, water_line + 4,  SAGE_GREEN, thickness=1, opacity=0.68)

    # Right leg: raised — upper leg extends forward, lower leg bent back
    leg_r_x_hip  = body_cx + 10
    leg_r_x_knee = body_cx + 32
    leg_r_y_knee = body_cy + 40
    _line(ref, leg_r_x_hip, leg_y_top, leg_r_x_knee, leg_r_y_knee, SAGE_GREEN, thickness=2, opacity=0.72)
    # Lower leg folds up toward body
    _line(ref, leg_r_x_knee, leg_r_y_knee, leg_r_x_knee + 6, leg_y_top - 4, SAGE_GREEN, thickness=1, opacity=0.65)

    # ── Egret shadow/reflection in water ─────────────────────────────────────
    shadow_cx = body_cx + 8
    shadow_cy = int(H * 0.82)
    # Distorted mirror: wider, shorter, darker
    _ellipse(ref, shadow_cx, shadow_cy, 42, 28, EGRET_SHADOW, opacity=0.38, feather=0.45)
    # Neck reflection (simpler, vertical streak)
    _line(ref, shadow_cx + 4, shadow_cy - 22, shadow_cx + 8, shadow_cy + 20,
          EGRET_SHADOW, thickness=3, opacity=0.28)

    # ── Ripple rings from the standing leg ───────────────────────────────────
    ripple_cx = leg_l_x
    ripple_cy = water_line
    for ring in range(3):
        r = 8 + ring * 14
        for angle in range(0, 360, 4):
            ax = ripple_cx + int(r * math.cos(math.radians(angle)))
            ay = ripple_cy + int(r * 0.35 * math.sin(math.radians(angle)))
            if 0 <= ax < W and 0 <= ay < H:
                fade = 0.22 - ring * 0.06
                ref[ay, ax] = _blend(ref[ay, ax], WATER_SHIMMER, fade)

    return ref


def paint():
    print("Session 241: The Egret at Dusk (Frankenthaler Soak-Stain, 152nd mode)")

    ref_arr = make_reference()
    ref = Image.fromarray((np.clip(ref_arr, 0, 1) * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=241)

    # Off-white raw canvas ground (Frankenthaler worked on unprimed cotton duck)
    p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.04)

    # Underpainting — establish broad colour masses
    p.underpainting(ref, stroke_size=50, n_strokes=140)

    # Block in — two passes, large then medium
    p.block_in(ref, stroke_size=30, n_strokes=200)
    p.block_in(ref, stroke_size=14, n_strokes=260)

    # Build form — medium then fine, for the egret structure
    p.build_form(ref, stroke_size=8, n_strokes=300)
    p.build_form(ref, stroke_size=4, n_strokes=360)

    # Place lights — white highlights on plumage and water shimmer
    p.place_lights(ref, stroke_size=2, n_strokes=160)

    # ── Session 241 new artistic pass: Frankenthaler Soak-Stain (152nd mode) ──
    # The sky and water become transparent, absorbed colour fields.
    # Multiple stain pours with soft, diffuse edges — no paint film, only light.
    p.frankenthaler_soak_stain_pass(
        n_stains=5,
        sigma_large=55.0,
        sigma_small=16.0,
        stain_alpha=0.46,
        absorption=0.60,
        cap_sigma=4.0,
        cap_threshold=0.04,
        seed=241,
        opacity=0.72,
    )

    # ── Session 241 artistic improvement: Lost-Found Edges ───────────────────
    # Sharpen the egret's body and beak (found edges), soften water/sky periphery (lost).
    p.paint_lost_found_edges_pass(
        found_sharpness=1.80,
        found_radius=1.0,
        lost_sigma=2.5,
        importance_k=5.5,
        cx=0.40,       # focal centre: the egret's body
        cy=0.60,
        focal_weight=0.50,
        opacity=0.60,
    )

    # Diffuse boundary — blend the stain zones smoothly at canvas edges
    p.diffuse_boundary_pass(opacity=0.22)

    # Final glaze: thin cerulean wash to unify the dusk light
    p.glaze((0.24, 0.52, 0.78), opacity=0.10)

    # Warm rose-gold glaze for dusk warmth
    p.glaze((0.86, 0.50, 0.38), opacity=0.06)

    # Vignette
    p.canvas.vignette(strength=0.20)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s241_frankenthaler_egret_dusk.png")
    p.canvas.save(out_path)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    paint()
