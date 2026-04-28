"""paint_s230.py -- Session 230: The Empty Chair (Hammershøi Grey Interior)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
from stroke_engine import Painter

W, H = 520, 720
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "s230_hammershoi_empty_chair.png")


def _blend(arr, col, strength):
    """Linear blend toward a colour."""
    return arr * (1.0 - strength) + np.array(col, dtype=np.float32) * strength


def _rect(arr, x0, y0, x1, y1, color, opacity=1.0):
    """Fill an axis-aligned rectangle."""
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(arr.shape[1], x1), min(arr.shape[0], y1)
    for y in range(y0, y1):
        for x in range(x0, x1):
            arr[y, x] = _blend(arr[y, x], color, opacity)


def _ellipse(arr, cx, cy, rx, ry, color, opacity=1.0, feather=0.10):
    h, w = arr.shape[:2]
    for dy in range(-int(ry * 1.12), int(ry * 1.12) + 1):
        for dx in range(-int(rx * 1.12), int(rx * 1.12) + 1):
            px, py = cx + dx, cy + dy
            if 0 <= px < w and 0 <= py < h:
                d = math.sqrt((dx / max(rx, 1)) ** 2 + (dy / max(ry, 1)) ** 2)
                if d <= 1.0 + feather:
                    alpha = max(0.0, min(1.0, (1.0 + feather - d) / feather))
                    arr[py, px] = _blend(arr[py, px], color, alpha * opacity)


def make_reference():
    """
    Build a reference image: an empty rocking chair in a dim Hammershøi interior.

    Composition:
    - Left wall with tall north-facing window at upper-left pouring silver light
    - Far back wall: bare plaster, muted grey-ivory
    - Right wall merges into shadow
    - Floor: wide pale-pine boards, grain running left-right toward window light
    - Rocking chair: dark oak, centre-right, facing slightly left (away from viewer)
    - Very distant small framed picture on back wall (barely visible)
    - Deep charcoal shadow in right corner and ceiling corners
    """
    rng = np.random.RandomState(230)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # ── Base atmosphere: muted warm grey plaster room ──────────────────────────
    for y in range(H):
        for x in range(W):
            # Warm near-window (left), cool far-right
            x_t = x / W
            y_t = y / H
            base = np.array([0.72, 0.70, 0.67], dtype=np.float32)
            # Ceiling: slightly darker
            if y_t < 0.12:
                base = _blend(base, [0.58, 0.56, 0.54], (0.12 - y_t) / 0.12 * 0.4)
            # Upper left corner bright (window glow)
            corner_dist = math.sqrt((x_t ** 2) + (y_t ** 2)) * 0.6
            base = _blend(base, [0.88, 0.86, 0.82], max(0.0, 0.7 - corner_dist) * 0.45)
            # Right-side shadow
            right_shadow = max(0.0, x_t - 0.62) / 0.38
            base = _blend(base, [0.34, 0.33, 0.34], right_shadow ** 1.4 * 0.70)
            # Bottom corners: very dark
            bottom_corner = (max(0.0, y_t - 0.85) / 0.15) * (max(0.0, x_t - 0.60) / 0.40)
            base = _blend(base, [0.18, 0.17, 0.18], bottom_corner ** 0.8 * 0.80)
            ref[y, x] = base

    # ── Floor: wide pine boards with window-light reflections ─────────────────
    floor_y = int(H * 0.72)
    for y in range(floor_y, H):
        for x in range(W):
            x_t = x / W
            y_t_floor = (y - floor_y) / max(H - floor_y, 1)
            # Pine boards base: warm cream-grey
            board_idx = int(x / (W / 7))
            board_warm = 0.72 + (board_idx % 2) * 0.03
            board_col = np.array([board_warm, board_warm * 0.97, board_warm * 0.91],
                                 dtype=np.float32)
            # Window light pool on floor (left-centre reflection)
            wl_x = 0.28
            wl_dist = abs(x_t - wl_x) / 0.35
            window_pool = max(0.0, 1.0 - wl_dist ** 1.5) * max(0.0, 1.0 - y_t_floor * 2.5)
            board_col = _blend(board_col, [0.90, 0.89, 0.86], window_pool * 0.50)
            # Far-right floor in deep shadow
            right_sh = max(0.0, x_t - 0.65) / 0.35
            board_col = _blend(board_col, [0.24, 0.23, 0.22],
                               right_sh ** 1.2 * 0.75 + y_t_floor * 0.25)
            # Board grain lines (horizontal)
            grain_noise = rng.uniform(-0.018, 0.018)
            board_col = np.clip(board_col + grain_noise, 0.0, 1.0)
            ref[y, x] = board_col

    # ── Left wall section and tall window ──────────────────────────────────────
    # Window frame: from x=40..180, y=35..410
    wx0, wx1 = int(W * 0.08), int(W * 0.35)
    wy0, wy1 = int(H * 0.05), int(H * 0.57)
    # Window glass: luminous silver-white with soft gradient
    for y in range(wy0, wy1):
        for x in range(wx0, wx1):
            x_t = (x - wx0) / max(wx1 - wx0, 1)
            y_t = (y - wy0) / max(wy1 - wy0, 1)
            # Diffused sky light: brightest upper-left, softer lower-right
            brightness = 0.88 + (1.0 - x_t) * 0.06 + (1.0 - y_t) * 0.04
            # Slight warm tint near frame
            warmth = (1.0 - x_t) * 0.012
            ref[y, x] = np.array([brightness + warmth,
                                   brightness - 0.005,
                                   brightness - 0.022], dtype=np.float32)

    # Window frame (dark oak surround, thin)
    frame_w = int(W * 0.012)
    # Top bar
    for y in range(max(0, wy0 - frame_w), wy0 + 1):
        for x in range(max(0, wx0 - frame_w), min(W, wx1 + frame_w)):
            ref[y, x] = _blend(ref[y, x], [0.28, 0.25, 0.22], 0.88)
    # Bottom bar
    for y in range(wy1, min(H, wy1 + frame_w)):
        for x in range(max(0, wx0 - frame_w), min(W, wx1 + frame_w)):
            ref[y, x] = _blend(ref[y, x], [0.28, 0.25, 0.22], 0.88)
    # Left bar
    for y in range(max(0, wy0 - frame_w), min(H, wy1 + frame_w)):
        for x in range(max(0, wx0 - frame_w), wx0 + 1):
            ref[y, x] = _blend(ref[y, x], [0.28, 0.25, 0.22], 0.88)
    # Right bar
    for y in range(max(0, wy0 - frame_w), min(H, wy1 + frame_w)):
        for x in range(wx1, min(W, wx1 + frame_w)):
            ref[y, x] = _blend(ref[y, x], [0.28, 0.25, 0.22], 0.88)
    # Middle crossbar (horizontal)
    mid_y = (wy0 + wy1) // 2
    for y in range(mid_y - frame_w // 2, mid_y + frame_w // 2 + 1):
        for x in range(wx0, wx1):
            ref[y, x] = _blend(ref[y, x], [0.28, 0.25, 0.22], 0.85)

    # ── Skirting board along bottom of back wall ──────────────────────────────
    sk_y0, sk_y1 = int(H * 0.68), int(H * 0.72)
    for y in range(sk_y0, sk_y1):
        for x in range(0, W):
            ref[y, x] = _blend(ref[y, x], [0.44, 0.41, 0.38], 0.70)

    # ── Small framed picture on far back wall ──────────────────────────────────
    px0, px1 = int(W * 0.60), int(W * 0.76)
    py0, py1 = int(H * 0.22), int(H * 0.38)
    # Frame
    fw = int(W * 0.008)
    for y in range(py0, py1):
        for x in range(px0, px1):
            is_frame = (x < px0 + fw or x >= px1 - fw or
                        y < py0 + fw or y >= py1 - fw)
            if is_frame:
                ref[y, x] = _blend(ref[y, x], [0.32, 0.29, 0.25], 0.80)
            else:
                # Canvas interior: indistinct darker tones
                ref[y, x] = _blend(ref[y, x], [0.42, 0.40, 0.39], 0.65)

    # ── Rocking chair ──────────────────────────────────────────────────────────
    # Chair centre: x=310, seat baseline y=520
    cx = int(W * 0.60)
    seat_y = int(H * 0.72)

    chair_col      = np.array([0.32, 0.27, 0.21], dtype=np.float32)  # dark oak
    chair_lit      = np.array([0.48, 0.42, 0.34], dtype=np.float32)  # lit-side oak
    chair_hi       = np.array([0.60, 0.54, 0.44], dtype=np.float32)  # edge highlight
    chair_shadow   = np.array([0.18, 0.15, 0.12], dtype=np.float32)  # deep shadow

    # Seat: slightly tilted trapezoid (wider at front)
    seat_w_front = int(W * 0.135)
    seat_w_back  = int(W * 0.100)
    seat_depth   = int(H * 0.052)
    for dy in range(seat_depth):
        t = dy / max(seat_depth - 1, 1)
        seat_w = int(seat_w_back + (seat_w_front - seat_w_back) * t)
        for dx in range(-seat_w, seat_w + 1):
            px = cx + dx + int(W * 0.008 * t)
            py = seat_y - seat_depth + dy
            if 0 <= px < W and 0 <= py < H:
                # Light falls from upper-left: brighter on left half of seat
                lit_t = max(0.0, -dx / (seat_w + 1))
                col = _blend(chair_col, chair_lit, lit_t * 0.65)
                # Caning suggestion: fine crosshatch-like darkening
                if (dx + dy * 2) % 6 == 0:
                    col = _blend(col, chair_shadow, 0.25)
                # Worn centre (thinner caning)
                centre_worn = max(0.0, 1.0 - (abs(dx) / max(seat_w * 0.6, 1)) ** 2)
                col = _blend(col, [col[0] * 0.90, col[1] * 0.88, col[2] * 0.85],
                             centre_worn * 0.20)
                ref[py, px] = _blend(ref[py, px], col, 0.92)

    # Back legs (two vertical posts)
    for leg_dx in [-int(W * 0.080), int(W * 0.058)]:
        lx = cx + leg_dx
        for y in range(seat_y - seat_depth + 2, seat_y + int(H * 0.120)):
            if 0 <= lx < W and 0 <= y < H:
                dark_t = (y - seat_y) / (H * 0.120) if y > seat_y else 0.0
                col = _blend(chair_col, chair_shadow, dark_t * 0.50)
                ref[y, lx] = _blend(ref[y, lx], col, 0.88)
                if lx + 1 < W:
                    ref[y, lx + 1] = _blend(ref[y, lx + 1], col, 0.60)

    # Front legs (two vertical posts, slightly forward-angled)
    for leg_dx in [-int(W * 0.100), int(W * 0.080)]:
        for i in range(int(H * 0.110)):
            lx = cx + leg_dx + int(i * 0.03)
            ly = seat_y + i
            if 0 <= lx < W and 0 <= ly < H:
                ref[ly, lx] = _blend(ref[ly, lx], chair_col, 0.88)
                if lx + 1 < W:
                    ref[ly, lx + 1] = _blend(ref[ly, lx + 1], chair_col, 0.50)

    # Chair back (tall curved back with vertical spindles)
    back_y_top  = seat_y - seat_depth - int(H * 0.195)
    back_y_bot  = seat_y - seat_depth
    back_x_left = cx - int(W * 0.065)
    back_x_right = cx + int(W * 0.065)

    # Back uprights (outer rails)
    for rail_x in [back_x_left, back_x_right]:
        for y in range(back_y_top, back_y_bot):
            curvature = int(4 * math.sin(math.pi * (y - back_y_top) /
                                         max(back_y_bot - back_y_top, 1)))
            rx = rail_x + curvature
            if 0 <= rx < W and 0 <= y < H:
                lit_t = 1.0 if rail_x == back_x_left else 0.0
                col = _blend(chair_col, chair_lit, lit_t * 0.55)
                ref[y, rx] = _blend(ref[y, rx], col, 0.90)
                if rx + 1 < W:
                    ref[y, rx + 1] = _blend(ref[y, rx + 1], col, 0.55)

    # Spindles (thin vertical slats)
    for spindle_n in range(5):
        sp_x = back_x_left + int((back_x_right - back_x_left) *
                                  (spindle_n + 1) / 6)
        for y in range(back_y_top + int(H * 0.025), back_y_bot):
            if 0 <= sp_x < W and 0 <= y < H:
                ref[y, sp_x] = _blend(ref[y, sp_x], chair_col, 0.78)

    # Top crest rail (arched)
    for dx in range(back_x_left - 3, back_x_right + 4):
        arch = int(6 * (1.0 - ((dx - cx) / max(back_x_right - cx, 1)) ** 2))
        for dy in range(int(H * 0.022)):
            py = back_y_top + dy - arch
            if 0 <= dx < W and 0 <= py < H:
                col = chair_lit if dx < cx else chair_col
                ref[py, dx] = _blend(ref[py, dx], col, 0.88)

    # Rockers (curved base rails)
    rocker_y = seat_y + int(H * 0.078)
    for rocker_dx in [-int(W * 0.085), int(W * 0.075)]:
        for t_frac in range(200):
            t = t_frac / 199.0
            angle = math.pi * (0.25 + t * 0.50)
            rx_r  = int(W * 0.090)
            ry_r  = int(H * 0.048)
            rx = cx + rocker_dx + int(rx_r * (t - 0.5) * 2)
            ry = rocker_y - int(ry_r * math.sin(angle - math.pi / 2) * 0.6)
            if 0 <= rx < W and 0 <= ry < H:
                ref[ry, rx] = _blend(ref[ry, rx], chair_col, 0.82)
                if ry + 1 < H:
                    ref[ry + 1, rx] = _blend(ref[ry + 1, rx], chair_col, 0.45)

    # Chair shadow on floor (soft, angled toward lower-right)
    for i in range(80):
        shadow_x = cx - int(W * 0.040) + i * int(W * 0.0024)
        shadow_y = seat_y + int(H * 0.105) + i * int(H * 0.0016)
        shadow_r = max(2, int((80 - i) * W / 1400))
        _ellipse(ref, shadow_x, shadow_y, shadow_r, int(shadow_r * 0.30),
                 [0.22, 0.20, 0.20],
                 opacity=max(0.0, 0.45 - i * 0.005),
                 feather=0.30)

    # ── Final ambient dust motes in window light ───────────────────────────────
    for _ in range(18):
        mx = int(rng.uniform(wx0 + 5, wx1 + int(W * 0.10)))
        my = int(rng.uniform(wy0 + 10, floor_y - 10))
        if 0 <= mx < W and 0 <= my < H:
            ref[my, mx] = _blend(ref[my, mx], [0.96, 0.94, 0.90],
                                 rng.uniform(0.25, 0.55))

    return np.clip(ref, 0.0, 1.0)


def main():
    print("Session 230: The Empty Chair — Hammershøi Grey Interior")
    print(f"  Canvas: {W}×{H}")
    print(f"  Output: {OUT}")

    print("  Building reference...")
    ref_arr = make_reference()
    ref_img = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H)

    # Neutral grey imprimatura — Hammershøi's mid-grey ground
    print("  tone_ground (grey imprimatura)...")
    p.tone_ground((0.52, 0.51, 0.50), texture_strength=0.05)

    # Thin underpainting — structural skeleton
    print("  underpainting...")
    p.underpainting(ref_img, stroke_size=36, n_strokes=80)

    # First block-in: primary tonal zones
    print("  block_in (pass 1)...")
    p.block_in(ref_img, stroke_size=20, n_strokes=160)

    # Second block-in: finer placement
    print("  block_in (pass 2)...")
    p.block_in(ref_img, stroke_size=11, n_strokes=240)

    # Build form: interior volumes and floor planes
    print("  build_form (pass 1)...")
    p.build_form(ref_img, stroke_size=7, n_strokes=300)

    # Second form pass: chair detail
    print("  build_form (pass 2)...")
    p.build_form(ref_img, stroke_size=4, n_strokes=200)

    # Lights: window glass highlights and floor shimmer
    print("  place_lights...")
    p.place_lights(ref_img, stroke_size=3, n_strokes=120)

    # ── Hammershøi Grey Interior Pass (141st mode) ────────────────────────────
    print("  hammershoi_grey_interior_pass (141st mode)...")
    p.hammershoi_grey_interior_pass(
        grey_veil=0.58,
        window_lift=0.10,
        window_cool=0.065,
        stillness_sigma=1.8,
        stillness_str=0.45,
        opacity=0.72,
    )

    # ── Chromatic Memory Pass (improvement) ───────────────────────────────────
    print("  chromatic_memory_pass (improvement)...")
    p.chromatic_memory_pass(
        memory_radius=11,
        memory_pull=0.25,
        sat_threshold=0.20,
        opacity=0.65,
    )

    # ── Impasto relief — suggest slightly textured plaster walls ──────────────
    print("  impasto_relief_pass...")
    p.impasto_relief_pass(
        light_angle=2.50,
        relief_scale=0.07,
        thickness_gate=0.28,
        relief_sigma=1.0,
        opacity=0.40,
    )

    # Diffuse boundary — soft interior edges
    print("  diffuse_boundary_pass...")
    p.diffuse_boundary_pass(
        boundary_sigma=1.2,
        boundary_str=0.30,
        opacity=0.50,
    )

    # Glaze: very faint silver-grey unifying veil
    print("  glaze (silver-grey veil)...")
    p.glaze((0.68, 0.68, 0.66), opacity=0.07)

    # Vignette: deepen outer edges toward charcoal
    print("  vignette...")
    p.vignette(strength=0.42)

    print(f"  Saving to {OUT}...")
    p.save(OUT)
    print("  Done.")


if __name__ == "__main__":
    main()
