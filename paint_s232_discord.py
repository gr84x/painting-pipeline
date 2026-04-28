"""
paint_s232_discord.py -- Session 232 Discord painting.

Subject: A solitary woman seated on a fog-shrouded canal jetty at pre-dawn,
         viewed from slightly above and behind, wrapped in grey-blue wool.
         Fernand Khnopff frozen reverie mode (143rd).
"""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
from stroke_engine import Painter

W, H = 520, 720
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "s232_khnopff_canal_reverie.png")


def _blend(arr, col, strength):
    return arr * (1.0 - strength) + np.array(col, dtype=np.float32) * strength


def _rect(arr, x0, y0, x1, y1, color, opacity=1.0):
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(arr.shape[1], x1), min(arr.shape[0], y1)
    for y in range(y0, y1):
        for x in range(x0, x1):
            arr[y, x] = _blend(arr[y, x], color, opacity)


def _ellipse(arr, cx, cy, rx, ry, color, opacity=1.0, feather=0.15):
    h, w = arr.shape[:2]
    for dy in range(-int(ry * 1.2), int(ry * 1.2) + 1):
        for dx in range(-int(rx * 1.2), int(rx * 1.2) + 1):
            px, py = cx + dx, cy + dy
            if 0 <= px < w and 0 <= py < h:
                d = math.sqrt((dx / max(rx, 1)) ** 2 + (dy / max(ry, 1)) ** 2)
                if d <= 1.0 + feather:
                    alpha = max(0.0, min(1.0, (1.0 + feather - d) / feather))
                    arr[py, px] = _blend(arr[py, px], color, alpha * opacity)


def _line(arr, x0, y0, x1, y1, color, width=1, opacity=1.0):
    h, w = arr.shape[:2]
    dx = abs(x1 - x0); sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0); sy = 1 if y0 < y1 else -1
    err = dx + dy
    cx, cy = x0, y0
    while True:
        for bx in range(-width, width + 1):
            for by in range(-width, width + 1):
                px2, py2 = cx + bx, cy + by
                if 0 <= px2 < w and 0 <= py2 < h:
                    arr[py2, px2] = _blend(arr[py2, px2], color, opacity)
        if cx == x1 and cy == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; cx += sx
        if e2 <= dx:
            err += dx; cy += sy


def _vgrad(arr, y0, y1, c0, c1):
    """Vertical gradient blend between two colors."""
    for y in range(max(0, y0), min(arr.shape[0], y1)):
        t = (y - y0) / max(y1 - y0, 1)
        col = np.array(c0, dtype=np.float32) * (1 - t) + np.array(c1, dtype=np.float32) * t
        arr[y, :] = _blend(arr[y, :], col, 1.0)


def make_reference():
    """
    Composition: Woman on canal jetty at pre-dawn fog.

    Scene layout (top to bottom):
    - Sky/fog zone (0..H*0.42): deep blue-grey fog, almost uniformly grey with
      subtle lighter band at fog horizon
    - Far bank (H*0.40..H*0.50): barely visible grey-green willow smear
    - Water surface (H*0.50..H*0.72): absolute mirror-still, slightly lighter
      grey than sky, with faint jetty reflection below
    - Jetty (H*0.55..H*1.0): grey weathered planks, near planks dark with moss
    - Figure: seated center-left, occupying H*0.30..H*0.68

    Figure anatomy:
    - Shawl/back: broad grey-blue draped mass
    - Head: partial right profile, pale, facing water (slightly right of center)
    - Hands: pale, in lap area
    """
    rng = np.random.RandomState(2320)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    fog_horizon = int(H * 0.44)
    water_start = int(H * 0.50)
    jetty_y     = int(H * 0.56)

    # ── Fog sky: near-uniform blue-grey, lightest at horizon ────────────────
    sky_top   = np.array([0.52, 0.53, 0.60], dtype=np.float32)
    sky_horiz = np.array([0.70, 0.72, 0.76], dtype=np.float32)
    for y in range(fog_horizon):
        t = y / fog_horizon
        row_col = sky_top * (1 - t) + sky_horiz * t
        ref[y, :] = row_col

    # Subtle horizontal fog striations — barely perceptible
    for _ in range(18):
        fy = rng.randint(0, fog_horizon)
        fw = rng.randint(W // 3, W)
        fx = rng.randint(0, W - fw)
        fv = rng.uniform(-0.03, 0.03)
        ref[fy, fx:fx+fw] = np.clip(ref[fy, fx:fx+fw] + fv, 0, 1)

    # ── Fog horizon glow band (H*0.38..H*0.48) ──────────────────────────────
    glow_s, glow_e = int(H * 0.38), int(H * 0.48)
    for y in range(glow_s, min(glow_e, H)):
        t = (y - glow_s) / max(glow_e - glow_s, 1)
        bell = math.exp(-0.5 * ((t - 0.5) / 0.22) ** 2)
        ref[y, :] = np.clip(ref[y, :] + bell * 0.06, 0, 1)

    # ── Far bank: barely-visible willow smear (H*0.40..H*0.52) ─────────────
    bank_s, bank_e = int(H * 0.40), int(H * 0.52)
    bank_col = np.array([0.55, 0.57, 0.58], dtype=np.float32)
    for y in range(bank_s, bank_e):
        t = (y - bank_s) / max(bank_e - bank_s, 1)
        opacity = 0.28 * math.exp(-0.5 * ((t - 0.5) / 0.25) ** 2)
        ref[y, :] = _blend(ref[y, :], bank_col, opacity)

    # Willow tree lumps
    for i in range(7):
        wx = rng.randint(0, W)
        wy = int(H * 0.43) + rng.randint(-8, 8)
        wrx, wry = rng.randint(25, 55), rng.randint(15, 35)
        wcol = np.array([0.50, 0.52, 0.54], dtype=np.float32)
        _ellipse(ref, wx, wy, wrx, wry, wcol, opacity=0.25, feather=0.30)

    # ── Water (H*0.50..H*0.72): flat steel-grey mirror ──────────────────────
    water_col_top = np.array([0.66, 0.68, 0.72], dtype=np.float32)
    water_col_bot = np.array([0.58, 0.60, 0.65], dtype=np.float32)
    water_end = int(H * 0.72)
    for y in range(water_start, min(water_end, H)):
        t = (y - water_start) / max(water_end - water_start, 1)
        row_col = water_col_top * (1 - t) + water_col_bot * t
        ref[y, :] = row_col
    # Faint reflection ripples
    for _ in range(12):
        ry2 = rng.randint(water_start + 5, water_end - 5)
        rx2 = rng.randint(20, W - 20)
        rw2 = rng.randint(40, 120)
        rv = rng.uniform(-0.025, 0.025)
        ref[ry2, max(0,rx2-rw2//2):min(W,rx2+rw2//2)] = np.clip(
            ref[ry2, max(0,rx2-rw2//2):min(W,rx2+rw2//2)] + rv, 0, 1)

    # ── Jetty: grey weathered planks (H*0.56..H) ────────────────────────────
    jetty_base = np.array([0.42, 0.43, 0.46], dtype=np.float32)
    jetty_dark = np.array([0.28, 0.30, 0.32], dtype=np.float32)
    for y in range(jetty_y, H):
        t = (y - jetty_y) / max(H - jetty_y, 1)
        row_col = jetty_base * (1 - t * 0.35) + jetty_dark * t * 0.35
        ref[y, :] = row_col

    # Jetty plank lines — horizontal, slightly irregular
    for i in range(8):
        py2 = jetty_y + i * ((H - jetty_y) // 8) + rng.randint(-3, 3)
        if 0 <= py2 < H:
            ref[py2, :] = np.clip(ref[py2, :] - 0.06, 0, 1)

    # Moss / lichen patches on jetty (dark, irregular)
    for _ in range(22):
        mx = rng.randint(0, W)
        my = rng.randint(jetty_y, H)
        mrx, mry = rng.randint(8, 25), rng.randint(4, 12)
        mcol = np.array([0.22, 0.26, 0.24], dtype=np.float32)
        _ellipse(ref, mx, my, mrx, mry, mcol, opacity=0.30, feather=0.35)

    # ── Figure: woman on jetty ───────────────────────────────────────────────
    # Seated center-left, occupying roughly x:150..370, y:200..480
    cx = int(W * 0.50)   # horizontal center of figure
    fig_top  = int(H * 0.27)   # top of head
    fig_bot  = int(H * 0.67)   # bottom of seated body

    # SHAWL BODY MASS: large draped grey-blue form
    shawl_col = np.array([0.52, 0.55, 0.64], dtype=np.float32)
    shawl_dark = np.array([0.36, 0.38, 0.46], dtype=np.float32)
    # Main body mass (back/shoulders)
    _ellipse(ref, cx, int(H*0.52), 100, 120, shawl_col, opacity=0.85, feather=0.18)
    # Shoulder hump (left - far shoulder)
    _ellipse(ref, cx - 60, int(H*0.44), 65, 50, shawl_col, opacity=0.80, feather=0.22)
    # Shoulder (right - near shoulder, slightly lower since back is turned)
    _ellipse(ref, cx + 55, int(H*0.46), 60, 45, shawl_col, opacity=0.75, feather=0.22)
    # Shawl shadows (lower part of back mass, where shawl gathers)
    _ellipse(ref, cx + 10, int(H*0.60), 85, 70, shawl_dark, opacity=0.50, feather=0.20)

    # SHAWL HOOD / HEAD WRAP: grey-blue fabric over head
    hood_col = np.array([0.56, 0.58, 0.68], dtype=np.float32)
    hood_dark = np.array([0.38, 0.40, 0.50], dtype=np.float32)
    # Hood main mass
    _ellipse(ref, cx + 15, int(H*0.38), 52, 48, hood_col, opacity=0.88, feather=0.15)
    # Hood shadow fold on right side
    _ellipse(ref, cx + 40, int(H*0.40), 28, 35, hood_dark, opacity=0.55, feather=0.20)

    # HEAD: pale face in right profile, slightly turned away
    # Only right cheek/jaw visible from this angle
    face_cx = cx + 28
    face_cy = int(H * 0.36)
    face_col = np.array([0.88, 0.84, 0.78], dtype=np.float32)  # warm ivory-pearl
    # Face oval (partially hidden by hood on left)
    _ellipse(ref, face_cx, face_cy, 28, 34, face_col, opacity=0.82, feather=0.18)
    # Cheekbone highlight
    _ellipse(ref, face_cx + 8, face_cy - 8, 12, 10,
             np.array([0.93, 0.90, 0.84], dtype=np.float32), opacity=0.65, feather=0.22)
    # Temple / forehead shadow
    _ellipse(ref, face_cx - 10, face_cy - 15, 18, 15,
             np.array([0.72, 0.68, 0.64], dtype=np.float32), opacity=0.50, feather=0.25)
    # Jaw line shadow
    _ellipse(ref, face_cx, face_cy + 22, 16, 12,
             np.array([0.70, 0.66, 0.62], dtype=np.float32), opacity=0.45, feather=0.25)
    # Neck
    _ellipse(ref, face_cx - 4, face_cy + 38, 12, 20,
             np.array([0.82, 0.78, 0.72], dtype=np.float32), opacity=0.60, feather=0.22)

    # HANDS: pale, in lap (barely visible, mostly covered by shawl)
    hands_cx = cx - 15
    hands_cy = int(H * 0.605)
    hand_col = np.array([0.86, 0.82, 0.76], dtype=np.float32)
    _ellipse(ref, hands_cx, hands_cy, 32, 16, hand_col, opacity=0.58, feather=0.22)
    _ellipse(ref, hands_cx + 18, hands_cy + 3, 20, 11,
             np.array([0.78, 0.74, 0.68], dtype=np.float32), opacity=0.42, feather=0.25)

    # ── Water reflection of figure (soft, distorted) ─────────────────────────
    refl_top = int(H * 0.62)
    refl_col = np.array([0.50, 0.52, 0.58], dtype=np.float32)
    _ellipse(ref, cx, refl_top + 40, 85, 55, refl_col, opacity=0.22, feather=0.35)
    _ellipse(ref, cx + 12, refl_top + 70, 50, 30, refl_col, opacity=0.15, feather=0.40)

    # ── Canal edge lines (jetty boards at bottom) ────────────────────────────
    # Dark water-jetty boundary line
    for x in range(W):
        jty = jetty_y + int(rng.uniform(-2, 2))
        if 0 <= jty < H:
            ref[jty, x] = np.clip(ref[jty, x] * 0.78, 0, 1)

    # Clip and convert
    ref = np.clip(ref, 0.0, 1.0)
    return Image.fromarray((ref * 255).astype(np.uint8), "RGB")


def paint() -> str:
    """Paint and save the Khnopff canal reverie."""
    print("Session 232 — Khnopff Frozen Reverie: building reference...")
    ref = make_reference()

    p = Painter(W, H)

    # Cool blue-grey Khnopff ground
    print("  tone_ground...")
    p.tone_ground((0.55, 0.56, 0.60), texture_strength=0.04)

    # Block in from reference
    print("  block_in...")
    p.block_in(ref, stroke_size=14, n_strokes=600)

    # Build form with medium-fine strokes
    print("  build_form...")
    p.build_form(ref, stroke_size=7, n_strokes=900)

    # Detail layer with fine strokes
    print("  detail strokes...")
    p.build_form(ref, stroke_size=4, n_strokes=500)

    # Midtone clarity — sharpen structural detail before mist
    print("  midtone_clarity_pass...")
    p.midtone_clarity_pass(
        clarity_center=0.55,
        clarity_width=0.20,
        sharpness=0.42,
        blur_sigma=1.2,
        opacity=0.55,
    )

    # Warm-cool zone separation — Academic light temperature
    print("  warm_cool_zone_pass...")
    p.warm_cool_zone_pass(
        warm_threshold=0.60,
        warm_ramp=0.18,
        warm_r_lift=0.025,
        warm_b_drop=0.015,
        cool_threshold=0.32,
        cool_ramp=0.20,
        cool_b_lift=0.035,
        cool_r_drop=0.018,
        cool_g_drop=0.006,
        opacity=0.65,
    )

    # KHNOPFF FROZEN REVERIE PASS — 143rd mode
    print("  khnopff_frozen_reverie_pass (143rd mode)...")
    p.khnopff_frozen_reverie_pass(
        desat_str=0.50,
        cool_shift=0.048,
        reverie_sigma=1.90,
        mist_str=0.55,
        bright_start=0.60,
        bright_range=0.22,
        pearl_b_boost=0.028,
        pearl_start=0.72,
        opacity=0.82,
    )

    # Final unifying cool grey glaze
    print("  glaze...")
    p.glaze((0.60, 0.62, 0.68), opacity=0.10)

    # Vignette — deepen edges for intimate mood
    print("  vignette...")
    p.canvas.vignette(strength=0.28)

    print(f"  saving to {OUT}...")
    p.save(OUT)
    print("  done.")
    return OUT


if __name__ == "__main__":
    paint()
