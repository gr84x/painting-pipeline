"""paint_s239.py -- Session 239: The Foundry Night (Dix Neue Sachlichkeit)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter

W, H = 520, 700


def _blend(arr, col, strength):
    return arr * (1.0 - strength) + np.array(col, dtype=np.float32) * strength


def _ellipse(arr, cx, cy, rx, ry, color, opacity=1.0, feather=0.10):
    h, w = arr.shape[:2]
    rx = max(rx, 1)
    ry = max(ry, 1)
    for dy in range(-int(ry * 1.15), int(ry * 1.15) + 1):
        for dx in range(-int(rx * 1.15), int(rx * 1.15) + 1):
            px, py = cx + dx, cy + dy
            if 0 <= px < w and 0 <= py < h:
                d = (dx / rx) ** 2 + (dy / ry) ** 2
                if d <= (1.0 + feather) ** 2:
                    alpha = max(0.0, min(1.0, (1.0 + feather - math.sqrt(d)) / (feather + 1e-6)))
                    arr[py, px] = _blend(arr[py, px], color, alpha * opacity)


def _rect(arr, x0, y0, x1, y1, color, opacity=1.0):
    h, w = arr.shape[:2]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    arr[y0:y1, x0:x1] = _blend(arr[y0:y1, x0:x1], color, opacity)


def _line(arr, x0, y0, x1, y1, color, thickness=1, opacity=0.85):
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
    ref = np.zeros((H, W, 3), dtype=np.float32)
    rng = np.random.RandomState(239)

    # ── Background: foundry interior — near-black walls, dark industrial space ──
    for y in range(H):
        for x in range(W):
            yt = y / H
            xt = x / W
            # Base: near-black space with slight warm cast from furnace
            furnace_x, furnace_y = 0.82, 0.88
            fdist = math.sqrt((xt - furnace_x) ** 2 + (yt - furnace_y) ** 2)
            furnace_glow = max(0.0, 1.0 - fdist * 1.6) ** 2.0
            base = np.array([0.06, 0.05, 0.04], dtype=np.float32)
            warm = np.array([0.52, 0.22, 0.06], dtype=np.float32)
            ref[y, x] = _blend(base, warm, furnace_glow * 0.70)

    # ── Furnace: lower-right — amber-orange radiant glow ──
    fx, fy = int(W * 0.78), int(H * 0.82)
    for y in range(max(0, int(H * 0.68)), H):
        for x in range(max(0, int(W * 0.60)), W):
            dx = x - fx
            dy = y - fy
            d = math.sqrt(dx * dx + dy * dy)
            glow = max(0.0, 1.0 - d / (W * 0.30)) ** 1.4
            col = np.array([0.92, 0.52, 0.12], dtype=np.float32)
            ref[y, x] = _blend(ref[y, x], col, glow * 0.88)

    # Furnace opening — bright core
    for r_step in range(40):
        r_f = r_step / 39.0
        r = int(W * 0.08 * (1.0 - r_f))
        bright = np.array([1.0, 0.78 * (1.0 - r_f * 0.4), 0.12 * (1.0 - r_f * 0.7)],
                          dtype=np.float32)
        _ellipse(ref, fx, fy, r, int(r * 0.65), bright, opacity=0.90 - r_f * 0.25)

    # ── Industrial beams: dark steel diagonal structure ──
    beam_color = [0.08, 0.07, 0.06]
    # Left diagonal beam, upper-left to mid
    _line(ref, int(W * 0.05), int(H * 0.02),
          int(W * 0.32), int(H * 0.45), beam_color, thickness=3, opacity=0.90)
    _line(ref, int(W * 0.12), int(H * 0.02),
          int(W * 0.38), int(H * 0.45), beam_color, thickness=2, opacity=0.80)
    # Right diagonal beam
    _line(ref, int(W * 0.96), int(H * 0.05),
          int(W * 0.70), int(H * 0.50), beam_color, thickness=3, opacity=0.88)
    # Horizontal beam upper
    _line(ref, int(W * 0.0), int(H * 0.20),
          int(W * 1.0), int(H * 0.20), beam_color, thickness=2, opacity=0.72)
    # Vertical pillar left
    _line(ref, int(W * 0.10), 0, int(W * 0.10), H, beam_color, thickness=4, opacity=0.82)

    # ── Smoke / haze: dark upper third with diffuse particles ──
    for _ in range(120):
        sx = int(rng.uniform(0, W))
        sy = int(rng.uniform(0, int(H * 0.35)))
        sr = int(rng.uniform(4, 16))
        sc = rng.uniform(0.07, 0.14)
        _ellipse(ref, sx, sy, sr, int(sr * 0.6),
                 [sc, sc * 0.92, sc * 0.84], opacity=rng.uniform(0.15, 0.35), feather=0.50)

    # ── Worker figure — foundry man, 3/4 front-left view, lit from furnace ──
    fig_cx = int(W * 0.42)
    fig_cy = int(H * 0.50)

    # --- Legs ---
    for side in [-1, 1]:
        lx = fig_cx + side * int(W * 0.055)
        # Thigh to knee
        _ellipse(ref, lx, int(H * 0.72), int(W * 0.038), int(H * 0.09),
                 [0.14, 0.10, 0.07], opacity=0.92, feather=0.18)
        # Lower leg
        _ellipse(ref, lx + side * int(W * 0.008), int(H * 0.84),
                 int(W * 0.030), int(H * 0.075),
                 [0.12, 0.09, 0.06], opacity=0.90, feather=0.18)
        # Boot
        _ellipse(ref, lx + side * int(W * 0.010), int(H * 0.92),
                 int(W * 0.038), int(H * 0.028),
                 [0.08, 0.06, 0.04], opacity=0.95, feather=0.14)

    # --- Torso: dark jacket with furnace-lit right side ──
    for y in range(int(H * 0.46), int(H * 0.72)):
        for x in range(int(W * 0.31), int(W * 0.56)):
            bx = (x - fig_cx) / (W * 0.125)
            by = (y - fig_cy) / (H * 0.13)
            d = bx * bx * 0.9 + by * by
            if d <= 1.0:
                # Furnace light from right-below
                lit = max(0.0, bx * 0.6 + 0.25)
                dark = np.array([0.12, 0.09, 0.06], dtype=np.float32)
                light = np.array([0.42, 0.22, 0.10], dtype=np.float32)
                col = _blend(dark, light, min(1.0, lit * 1.2))
                fade = max(0.0, 1.0 - (d - 0.80) / 0.20) if d > 0.80 else 1.0
                ref[y, x] = _blend(ref[y, x], col, fade * 0.94)

    # Jacket lapels / collar detail
    _ellipse(ref, fig_cx - int(W * 0.018), int(H * 0.475),
             int(W * 0.022), int(H * 0.028), [0.18, 0.12, 0.08], opacity=0.80, feather=0.22)
    _ellipse(ref, fig_cx + int(W * 0.014), int(H * 0.475),
             int(W * 0.018), int(H * 0.028), [0.14, 0.10, 0.07], opacity=0.80, feather=0.22)

    # --- Arms ---
    # Right arm (lit side, reaching toward furnace direction)
    for ay in range(int(H * 0.50), int(H * 0.70)):
        arm_t = (ay - H * 0.50) / (H * 0.20)
        ax_c = fig_cx + int(W * (0.12 + arm_t * 0.10))
        lit_r = 0.35 + arm_t * 0.30
        dark_a = np.array([0.14, 0.10, 0.07], dtype=np.float32)
        lit_a  = np.array([0.44, 0.24, 0.10], dtype=np.float32)
        col = _blend(dark_a, lit_a, min(1.0, lit_r))
        _ellipse(ref, ax_c, ay, int(W * 0.028), int(H * 0.016),
                 col, opacity=0.88, feather=0.20)

    # Left arm (shadow side)
    for ay in range(int(H * 0.50), int(H * 0.68)):
        arm_t = (ay - H * 0.50) / (H * 0.18)
        ax_c = fig_cx - int(W * (0.11 + arm_t * 0.04))
        _ellipse(ref, ax_c, ay, int(W * 0.026), int(H * 0.015),
                 [0.10, 0.08, 0.05], opacity=0.88, feather=0.18)

    # Right hand (reaching, splayed fingers toward furnace)
    hx_r, hy_r = fig_cx + int(W * 0.22), int(H * 0.69)
    _ellipse(ref, hx_r, hy_r, int(W * 0.032), int(H * 0.022),
             [0.62, 0.38, 0.20], opacity=0.88, feather=0.22)
    for fi in range(4):
        fx2 = hx_r + int(W * 0.016 * fi) - int(W * 0.024)
        fy2 = hy_r + int(H * 0.018 + fi * 2)
        _ellipse(ref, fx2, fy2, int(W * 0.008), int(H * 0.014),
                 [0.60, 0.36, 0.18], opacity=0.78, feather=0.25)

    # Left hand (hanging)
    hx_l, hy_l = fig_cx - int(W * 0.16), int(H * 0.68)
    _ellipse(ref, hx_l, hy_l, int(W * 0.026), int(H * 0.018),
             [0.30, 0.16, 0.08], opacity=0.82, feather=0.22)

    # --- Head ──
    hd_cx, hd_cy = fig_cx - int(W * 0.012), int(H * 0.365)
    hd_rx, hd_ry = int(W * 0.068), int(H * 0.080)

    # Head base: shadow side vs. furnace-lit side
    for dy in range(-hd_ry - 5, hd_ry + 5):
        for dx in range(-hd_rx - 5, hd_rx + 5):
            px, py = hd_cx + dx, hd_cy + dy
            if 0 <= px < W and 0 <= py < H:
                hd = (dx / hd_rx) ** 2 + (dy / hd_ry) ** 2
                if hd <= 1.10:
                    # Furnace (right-below) lighting
                    lit = max(0.0, min(1.0, dx / hd_rx * 0.55 + 0.35))
                    dark_h = np.array([0.28, 0.16, 0.08], dtype=np.float32)
                    lit_h  = np.array([0.78, 0.54, 0.30], dtype=np.float32)
                    col = _blend(dark_h, lit_h, lit)
                    fade = max(0.0, 1.0 - (hd - 0.86) / 0.24) if hd > 0.86 else 1.0
                    ref[py, px] = _blend(ref[py, px], col, fade * 0.95)

    # Brow ridge — harsh overhead shadow band
    for dy_br in range(int(hd_ry * 0.08), int(hd_ry * 0.24)):
        for dx_br in range(-int(hd_rx * 0.90), int(hd_rx * 0.90)):
            px, py = hd_cx + dx_br, hd_cy - int(hd_ry * 0.15) + dy_br
            if 0 <= px < W and 0 <= py < H:
                ref[py, px] = _blend(ref[py, px], [0.14, 0.08, 0.04], 0.45)

    # Eyes — deep-set, Dix's intense gaze
    for ex_off, ey_off in [(-int(hd_rx * 0.32), -int(hd_ry * 0.04)),
                            (int(hd_rx * 0.16), -int(hd_ry * 0.06))]:
        ex, ey = hd_cx + ex_off, hd_cy + ey_off
        _ellipse(ref, ex, ey, int(hd_rx * 0.20), int(hd_ry * 0.13),
                 [0.08, 0.05, 0.03], opacity=0.95, feather=0.12)
        _ellipse(ref, ex, ey, int(hd_rx * 0.13), int(hd_ry * 0.09),
                 [0.22, 0.14, 0.08], opacity=0.80, feather=0.18)
        _ellipse(ref, ex, ey, int(hd_rx * 0.05), int(hd_ry * 0.07),
                 [0.04, 0.02, 0.01], opacity=0.98, feather=0.10)
        _ellipse(ref, ex + int(hd_rx * 0.04), ey - int(hd_ry * 0.02),
                 int(hd_rx * 0.04), int(hd_ry * 0.03),
                 [0.82, 0.70, 0.52], opacity=0.72, feather=0.18)

    # Nose — angular, Dix-style prominent
    nsx, nsy = hd_cx - int(hd_rx * 0.08), hd_cy + int(hd_ry * 0.14)
    _ellipse(ref, nsx, nsy, int(hd_rx * 0.16), int(hd_ry * 0.14),
             [0.70, 0.44, 0.24], opacity=0.82, feather=0.22)
    _ellipse(ref, nsx - int(hd_rx * 0.14), nsy + int(hd_ry * 0.04),
             int(hd_rx * 0.08), int(hd_ry * 0.07),
             [0.14, 0.08, 0.04], opacity=0.75, feather=0.20)
    # Nose highlight (furnace-lit)
    _ellipse(ref, nsx + int(hd_rx * 0.04), nsy - int(hd_ry * 0.04),
             int(hd_rx * 0.07), int(hd_ry * 0.05),
             [0.88, 0.68, 0.40], opacity=0.65, feather=0.22)

    # Mouth — tight, grim line
    mx, my = hd_cx - int(hd_rx * 0.06), hd_cy + int(hd_ry * 0.34)
    _ellipse(ref, mx, my, int(hd_rx * 0.30), int(hd_ry * 0.06),
             [0.18, 0.10, 0.06], opacity=0.90, feather=0.18)
    _ellipse(ref, mx, my + int(hd_ry * 0.05), int(hd_rx * 0.22), int(hd_ry * 0.05),
             [0.50, 0.28, 0.14], opacity=0.60, feather=0.22)

    # Jaw / chin — angular, Dix's strong jaw
    _ellipse(ref, hd_cx, hd_cy + int(hd_ry * 0.76), int(hd_rx * 0.60), int(hd_ry * 0.18),
             [0.54, 0.30, 0.14], opacity=0.82, feather=0.22)
    # Jaw shadow left side
    _ellipse(ref, hd_cx - int(hd_rx * 0.50), hd_cy + int(hd_ry * 0.40),
             int(hd_rx * 0.28), int(hd_ry * 0.34),
             [0.12, 0.07, 0.04], opacity=0.68, feather=0.28)

    # --- Cap / flat cap — worker's cloth cap ──
    cap_cx, cap_cy = hd_cx - int(hd_rx * 0.04), hd_cy - int(hd_ry * 0.76)
    _ellipse(ref, cap_cx, cap_cy, int(hd_rx * 0.92), int(hd_ry * 0.32),
             [0.16, 0.12, 0.08], opacity=0.94, feather=0.16)
    # Cap peak
    _ellipse(ref, cap_cx - int(hd_rx * 0.68), cap_cy + int(hd_ry * 0.16),
             int(hd_rx * 0.38), int(hd_ry * 0.14),
             [0.12, 0.09, 0.06], opacity=0.92, feather=0.18)
    # Cap highlight on top
    _ellipse(ref, cap_cx + int(hd_rx * 0.08), cap_cy - int(hd_ry * 0.08),
             int(hd_rx * 0.28), int(hd_ry * 0.10),
             [0.48, 0.30, 0.14], opacity=0.55, feather=0.28)

    # Ear (right side, furnace lit)
    _ellipse(ref, hd_cx + int(hd_rx * 0.88), hd_cy + int(hd_ry * 0.04),
             int(hd_rx * 0.14), int(hd_ry * 0.22),
             [0.70, 0.44, 0.22], opacity=0.82, feather=0.22)

    # ── Ground / floor: concrete, lit orange from furnace ──
    for y in range(int(H * 0.90), H):
        for x in range(W):
            xt = x / W
            yt = (y - H * 0.90) / (H * 0.10)
            furnace_d = abs(xt - 0.82)
            glow = max(0.0, 1.0 - furnace_d * 2.0) * (1.0 - yt * 0.5)
            base = np.array([0.12, 0.09, 0.06], dtype=np.float32)
            warm = np.array([0.48, 0.26, 0.08], dtype=np.float32)
            ref[y, x] = _blend(base, warm, glow * 0.60)

    # Floor cracks / grime marks
    for _ in range(8):
        cx_ = int(rng.uniform(W * 0.1, W * 0.9))
        cy_ = int(rng.uniform(H * 0.91, H * 0.98))
        cl_ = int(rng.uniform(20, 60))
        _line(ref, cx_, cy_, cx_ + cl_, cy_ + int(rng.uniform(-3, 3)),
              [0.06, 0.04, 0.02], thickness=1, opacity=0.55)

    # ── Atmospheric embers / sparks drifting from furnace ──
    for _ in range(35):
        ex_ = int(rng.uniform(W * 0.55, W * 0.95))
        ey_ = int(rng.uniform(int(H * 0.40), int(H * 0.80)))
        er_ = rng.uniform(0.5, 2.0)
        fade_ = max(0.0, 1.0 - abs(ex_ / W - 0.80) * 3.0)
        col_e = [min(1.0, 0.88 + rng.uniform(-0.08, 0.08)),
                 min(1.0, 0.44 + rng.uniform(-0.12, 0.12)),
                 min(1.0, 0.08 + rng.uniform(0, 0.08))]
        if 0 <= ey_ < H and 0 <= ex_ < W:
            ref[ey_, ex_] = _blend(ref[ey_, ex_], col_e, er_ * fade_ * 0.80)

    img = Image.fromarray(
        (np.clip(ref, 0.0, 1.0) * 255).astype(np.uint8), "RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=1.0))
    return img


def paint() -> str:
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s239_dix_foundry_night.png")
    print("Building reference...")
    ref = make_reference()
    print("Initialising Painter...")
    p = Painter(W, H, seed=239)
    print("Toning ground (warm plaster)...")
    p.tone_ground((0.78, 0.70, 0.58), texture_strength=0.06)
    print("Underpainting...")
    p.underpainting(ref, stroke_size=54, n_strokes=160)
    print("Block-in...")
    p.block_in(ref, stroke_size=36, n_strokes=300)
    print("Block-in (tighter)...")
    p.block_in(ref, stroke_size=22, n_strokes=380)
    print("Build form...")
    p.build_form(ref, stroke_size=12, n_strokes=520)
    print("Build form (fine)...")
    p.build_form(ref, stroke_size=6, n_strokes=400)
    print("Place lights...")
    p.place_lights(ref, stroke_size=3, n_strokes=280)
    print("Dix Neue Sachlichkeit (150th mode)...")
    p.dix_neue_sachlichkeit_pass(
        compress_strength=0.42,
        midtone_gamma=1.8,
        surge_lo=0.28,
        surge_hi=0.66,
        saturation_surge=0.36,
        hi_thresh=0.80,
        hi_power=1.6,
        hi_crispness=0.52,
        opacity=0.78,
    )
    print("Paint Glaze Gradient (session 239 improvement)...")
    p.paint_glaze_gradient_pass(
        color=(0.52, 0.28, 0.06),
        axis='y',
        opacity_near=0.0,
        opacity_far=0.12,
        gamma=1.8,
        reverse=True,   # build from bottom (furnace glow area)
        blend_mode='multiply',
    )
    print("Diffuse boundary...")
    p.diffuse_boundary_pass(low_grad=0.05, high_grad=0.24,
                            sigma=0.8, strength=0.32, opacity=0.42)
    print("Glaze (warm umber)...")
    p.glaze((0.30, 0.16, 0.05), opacity=0.04)
    print("Vignette...")
    p.canvas.vignette(strength=0.60)
    p.canvas.save(out_path)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint()
    print("Done:", result)
