"""paint_s237.py -- Session 237: The Raven's Vigil (Rouault Stained Glass, 148th mode)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter

W, H = 520, 720


def _blend(arr, col, strength):
    return arr * (1 - strength) + np.array(col, dtype=np.float32) * strength


def _ellipse(arr, cx, cy, rx, ry, color, opacity=1.0, feather=0.08):
    h, w = arr.shape[:2]
    for dy in range(-int(ry * 1.12), int(ry * 1.12) + 1):
        for dx in range(-int(rx * 1.12), int(rx * 1.12) + 1):
            px, py = cx + dx, cy + dy
            if 0 <= px < w and 0 <= py < h:
                d = (dx / max(rx, 1)) ** 2 + (dy / max(ry, 1)) ** 2
                if d <= (1.0 + feather) ** 2:
                    alpha = max(0.0, min(1.0, (1.0 + feather - math.sqrt(d)) / feather))
                    arr[py, px] = _blend(arr[py, px], color, alpha * opacity)


def make_reference():
    ref = np.zeros((H, W, 3), dtype=np.float32)
    rng = np.random.RandomState(237)

    # ── Sky: deep prussian blue-grey, turbulent winter light ──
    for y in range(H):
        for x in range(W):
            yt = y / H
            xt = x / W
            # Cold dark sky -- prussian blue-grey gradient, lighter at horizon
            sky_t = max(0.0, 1.0 - yt * 1.6)
            base_sky = np.array([0.08, 0.12, 0.28], dtype=np.float32)
            bright_sky = np.array([0.18, 0.24, 0.42], dtype=np.float32)
            ref[y, x] = _blend(base_sky, bright_sky, sky_t * 0.5)

    # Horizon glow -- crimson amber streak (cold amber light, left side)
    for y in range(int(H * 0.55), int(H * 0.72)):
        for x in range(int(W * 0.0), int(W * 0.55)):
            yt = (y - H * 0.55) / (H * 0.17)
            xt = x / (W * 0.55)
            # Bell-curve glow
            bell = math.exp(-0.5 * ((yt - 0.35) / 0.22) ** 2)
            xbell = max(0.0, 1.0 - xt * 0.6)
            intensity = bell * xbell * 0.65
            glow_col = np.array([0.58, 0.22, 0.06], dtype=np.float32)
            ref[y, x] = _blend(ref[y, x], glow_col, intensity)

    # Torn cloud forms -- dark blueish grey masses
    cloud_specs = [
        (int(W * 0.25), int(H * 0.10), int(W * 0.22), int(H * 0.08), (0.22, 0.24, 0.38), 0.68),
        (int(W * 0.72), int(H * 0.08), int(W * 0.18), int(H * 0.06), (0.20, 0.22, 0.36), 0.60),
        (int(W * 0.50), int(H * 0.20), int(W * 0.28), int(H * 0.07), (0.15, 0.18, 0.32), 0.55),
        (int(W * 0.10), int(H * 0.25), int(W * 0.14), int(H * 0.05), (0.18, 0.20, 0.34), 0.50),
        (int(W * 0.82), int(H * 0.30), int(W * 0.16), int(H * 0.06), (0.14, 0.16, 0.30), 0.52),
    ]
    for cx, cy, rx, ry, col, op in cloud_specs:
        _ellipse(ref, cx, cy, rx, ry, list(col), opacity=op, feather=0.40)

    # ── Stone wall: horizontal, rough, mossy ──
    wall_top = int(H * 0.56)
    wall_bot = int(H * 0.75)

    # Wall base: raw umber grey stone
    for y in range(wall_top, wall_bot):
        for x in range(W):
            yt = (y - wall_top) / (wall_bot - wall_top)
            noise_x = rng.uniform(-0.015, 0.015)
            dark_t = 0.32 + yt * 0.18
            col = np.array([dark_t + noise_x, dark_t * 0.95 + noise_x * 0.8,
                             dark_t * 0.82 + noise_x * 0.5], dtype=np.float32)
            ref[y, x] = _blend(ref[y, x], col, 0.94)

    # Stone blocks: defined horizontal courses
    for course in range(3):
        cy = wall_top + int((wall_bot - wall_top) * (0.2 + course * 0.28))
        mortar_col = [0.16, 0.14, 0.12]
        for x in range(W):
            for dy in range(-1, 2):
                py = cy + dy
                if wall_top <= py < wall_bot:
                    ref[py, x] = _blend(ref[py, x], mortar_col, 0.72)

    # Vertical mortar joints (offset per course)
    for course in range(4):
        offset_x = int(W * (0.12 + course * 0.08)) % int(W * 0.25)
        joint_spacing = int(W * 0.15) + int(rng.uniform(0, W * 0.06))
        course_y_start = wall_top + int((wall_bot - wall_top) * course * 0.27)
        course_y_end = min(wall_bot, course_y_start + int((wall_bot - wall_top) * 0.30))
        x = offset_x
        while x < W:
            for y in range(course_y_start, course_y_end):
                ref[y, x] = _blend(ref[y, x], [0.14, 0.12, 0.10], 0.65)
                if x + 1 < W:
                    ref[y, x + 1] = _blend(ref[y, x + 1], [0.14, 0.12, 0.10], 0.40)
            x += joint_spacing + int(rng.uniform(0, joint_spacing * 0.3))

    # Lichen patches: emerald green and pale gold on stone
    lichen_specs = [
        (int(W * 0.12), int(H * 0.63), int(W * 0.04), int(H * 0.02), [0.14, 0.38, 0.18], 0.75),
        (int(W * 0.22), int(H * 0.66), int(W * 0.03), int(H * 0.015), [0.18, 0.42, 0.16], 0.72),
        (int(W * 0.78), int(H * 0.62), int(W * 0.04), int(H * 0.018), [0.12, 0.36, 0.20], 0.78),
        (int(W * 0.88), int(H * 0.65), int(W * 0.03), int(H * 0.014), [0.60, 0.54, 0.16], 0.65),
        (int(W * 0.08), int(H * 0.69), int(W * 0.025), int(H * 0.012), [0.52, 0.50, 0.14], 0.62),
        (int(W * 0.92), int(H * 0.70), int(W * 0.03), int(H * 0.014), [0.16, 0.40, 0.18], 0.70),
    ]
    for lx, ly, lrx, lry, lc, lo in lichen_specs:
        if wall_top <= ly < wall_bot:
            _ellipse(ref, lx, ly, lrx, lry, lc, opacity=lo, feather=0.35)

    # Wall top edge: darker capping stones, slight snow dusting
    cap_y = wall_top
    for x in range(W):
        noise = rng.uniform(-0.01, 0.01)
        cap_col = [0.42 + noise, 0.40 + noise, 0.36 + noise]
        ref[cap_y, x] = _blend(ref[cap_y, x], cap_col, 0.85)
        # Snow dusting on top edge
        if rng.uniform() > 0.45:
            ref[cap_y - 1, x] = _blend(ref[cap_y - 1, x], [0.78, 0.80, 0.82], 0.65)

    # ── Foreground: dead winter grasses, snow-dusted ground ──
    fg_start = wall_bot
    for y in range(fg_start, H):
        yt = (y - fg_start) / max(H - fg_start, 1)
        for x in range(W):
            # Dark cold ground: raw umber + grey
            dark_t = 0.12 + yt * 0.04
            noise = rng.uniform(-0.008, 0.008)
            col = [dark_t * 0.88 + noise, dark_t * 0.78 + noise * 0.7,
                   dark_t * 0.62 + noise * 0.5]
            ref[y, x] = _blend(ref[y, x], col, 0.92)

    # Snow patches on foreground ground
    for _ in range(25):
        sx = int(rng.uniform(0, W))
        sy = int(rng.uniform(fg_start + 5, H - 5))
        srx = int(rng.uniform(int(W * 0.02), int(W * 0.06)))
        sry = int(rng.uniform(int(H * 0.01), int(H * 0.02)))
        snow_col = [0.72, 0.74, 0.78]
        _ellipse(ref, sx, sy, srx, sry, snow_col, opacity=rng.uniform(0.45, 0.75), feather=0.30)

    # Dead grass stems in foreground
    for _ in range(65):
        gx = int(rng.uniform(int(W * 0.02), int(W * 0.98)))
        gy_bot = int(rng.uniform(fg_start + 2, H - 3))
        gh = int(rng.uniform(int(H * 0.04), int(H * 0.10)))
        gc = [rng.uniform(0.24, 0.38), rng.uniform(0.20, 0.30), rng.uniform(0.10, 0.18)]
        for step in range(gh):
            sy = gy_bot - step
            sx = gx + int(math.sin(step * 0.22 + gx * 0.08) * 2)
            if 0 <= sy < H and 0 <= sx < W:
                ref[sy, sx] = _blend(ref[sy, sx], gc, 0.68)

    # ── Background: bare tree silhouettes at horizon ──
    tree_y_base = int(H * 0.56)
    for tx in [int(W * 0.05), int(W * 0.14), int(W * 0.86), int(W * 0.94)]:
        tw = int(W * 0.006 + rng.uniform(0, W * 0.004))
        th = int(H * 0.22 + rng.uniform(0, H * 0.06))
        for y in range(tree_y_base - th, tree_y_base):
            for x in range(max(0, tx - tw), min(W, tx + tw)):
                if 0 <= y < H:
                    depth = (tree_y_base - y) / th
                    tc = np.array([0.08, 0.08, 0.12], dtype=np.float32) * (1 - depth * 0.15)
                    ref[y, x] = _blend(ref[y, x], tc, 0.88 + depth * 0.08)
        # Branch stubs
        for branch in range(3):
            blen = int(rng.uniform(W * 0.04, W * 0.08))
            bdir = rng.choice([-1, 1])
            by_start = tree_y_base - int(th * rng.uniform(0.4, 0.85))
            for bl in range(blen):
                bx = tx + bdir * bl
                by = by_start - int(bl * rng.uniform(0.1, 0.3))
                if 0 <= bx < W and 0 <= by < H:
                    ref[by, bx] = _blend(ref[by, bx], [0.06, 0.06, 0.10], 0.88)

    # ── Raven: large, perched on wall, facing left, head turning toward viewer ──
    # Positioned upper-centre, occupying the wall top edge zone
    raven_cx = int(W * 0.50)
    raven_cy = int(H * 0.46)   # body centre

    # Body -- near-black with deep cobalt iridescence on lit surfaces
    for y in range(int(H * 0.36), int(H * 0.58)):
        for x in range(int(W * 0.36), int(W * 0.64)):
            bx2 = (x - raven_cx) / (W * 0.125)
            by2 = (y - raven_cy) / (H * 0.105)
            d = bx2 * bx2 + by2 * by2
            if d <= 1.0:
                # Light from upper-left (cold winter sky); slight iridescence
                lit = max(0.0, min(1.0, (-bx2 * 0.55 - by2 * 0.45 + 0.35)))
                dark_col = np.array([0.04, 0.04, 0.06], dtype=np.float32)
                # Iridescent highlights: deep cobalt-blue-green
                irid_col = np.array([0.08, 0.16, 0.36], dtype=np.float32)
                col = _blend(dark_col, irid_col, min(1.0, lit * 1.8))
                fade = max(0.0, 1.0 - (d - 0.82) / 0.18) if d > 0.82 else 1.0
                ref[y, x] = _blend(ref[y, x], col, fade * 0.96)

    # Breast/belly: slightly paler underside, subtle warm cast
    for y in range(int(H * 0.46), int(H * 0.57)):
        for x in range(int(W * 0.43), int(W * 0.58)):
            cbx = (x - raven_cx) / (W * 0.075)
            cby = (y - (raven_cy + H * 0.05)) / (H * 0.055)
            cd = cbx * cbx + cby * cby
            if cd <= 1.0:
                fade = max(0.0, 1.0 - (cd - 0.72) / 0.28) if cd > 0.72 else 1.0
                ref[y, x] = _blend(ref[y, x], [0.06, 0.06, 0.09], fade * 0.55)

    # Right wing (slightly raised, catching cold sky light -- more iridescent)
    wing_cx = int(W * 0.60)
    wing_cy = int(H * 0.445)
    for dy in range(-int(H * 0.080), int(H * 0.080) + 1):
        for dx in range(-int(W * 0.095), int(W * 0.095) + 1):
            px, py = wing_cx + dx, wing_cy + dy
            if 0 <= px < W and 0 <= py < H:
                wd = (dx / (W * 0.085)) ** 2 + (dy / (H * 0.070)) ** 2
                if wd <= 1.08:
                    # Wing raised to right and up: more sky light = more iridescence
                    lit = max(0.0, min(1.0, (dx / (W * 0.085)) * 0.5 + 0.4))
                    dark_w = np.array([0.04, 0.04, 0.06], dtype=np.float32)
                    irid_w = np.array([0.06, 0.18, 0.38], dtype=np.float32)
                    col = _blend(dark_w, irid_w, min(1.0, lit * 2.2))
                    fade = max(0.0, 1.0 - (wd - 0.82) / 0.26) if wd > 0.82 else 1.0
                    ref[py, px] = _blend(ref[py, px], col, fade * 0.94)

    # Primary flight feathers (right wing, visible below wing mass)
    for fi, fang in enumerate([-0.18, -0.08, 0.04, 0.14]):
        flen = int(W * 0.05) + int(rng.uniform(0, W * 0.02))
        for ft in range(flen):
            ft_f = ft / flen
            fpx = wing_cx + int(ft * math.cos(fang + 0.8) * 1.1)
            fpy = wing_cy + int(ft * math.sin(fang + 0.8) * 0.65)
            if 0 <= fpx < W and 0 <= fpy < H:
                irid = max(0.0, ft_f * 0.6)
                ref[fpy, fpx] = _blend(ref[fpy, fpx], [0.04 + irid * 0.04,
                                                         0.05 + irid * 0.12,
                                                         0.08 + irid * 0.28], 0.90)

    # Left wing (tucked, mostly hidden behind body)
    for dy in range(-int(H * 0.068), int(H * 0.068) + 1):
        for dx in range(-int(W * 0.072), int(W * 0.072) + 1):
            px, py = (raven_cx - int(W * 0.055)) + dx, wing_cy + int(H * 0.01) + dy
            if 0 <= px < W and 0 <= py < H:
                wd = (dx / (W * 0.065)) ** 2 + (dy / (H * 0.060)) ** 2
                if wd <= 1.0:
                    fade = max(0.0, 1.0 - (wd - 0.80) / 0.20) if wd > 0.80 else 1.0
                    ref[py, px] = _blend(ref[py, px], [0.04, 0.04, 0.06], fade * 0.88)

    # Tail: long, wedge-shaped, extending down below body
    tail_cx = raven_cx + int(W * 0.04)
    tail_cy = int(H * 0.56)
    for dy in range(0, int(H * 0.065)):
        tw_half = max(2, int((1.0 - dy / (H * 0.065)) * W * 0.055))
        for dx in range(-tw_half, tw_half + 1):
            px, py = tail_cx + dx, tail_cy + dy
            if 0 <= px < W and 0 <= py < H:
                irid = max(0.0, (1.0 - dy / (H * 0.065)) * 0.3)
                ref[py, px] = _blend(ref[py, px], [0.04, 0.04 + irid * 0.08,
                                                     0.06 + irid * 0.22], 0.92)

    # Legs and talons: gripping the stone wall top edge
    for leg_x, leg_y_top, leg_y_bot in [
        (raven_cx - int(W * 0.045), int(H * 0.55), int(H * 0.575)),
        (raven_cx + int(W * 0.020), int(H * 0.55), int(H * 0.575)),
    ]:
        for y in range(leg_y_top, leg_y_bot):
            for dx in range(-1, 2):
                px = leg_x + dx
                if 0 <= px < W and 0 <= y < H:
                    ref[y, px] = _blend(ref[y, px], [0.08, 0.08, 0.10], 0.85)
        # Toes gripping wall
        for talon_dir in [-2, -1, 1, 2]:
            for tl in range(int(W * 0.028)):
                tx = leg_x + int(talon_dir * tl * 0.85)
                ty = leg_y_bot + int(tl * 0.12)
                if 0 <= tx < W and 0 <= ty < H:
                    ref[ty, tx] = _blend(ref[ty, tx], [0.06, 0.06, 0.08], 0.88)

    # Head: turning back/toward viewer (three-quarter view, facing slightly left)
    head_cx = raven_cx - int(W * 0.025)
    head_cy = int(H * 0.335)
    head_rx = int(W * 0.060)
    head_ry = int(H * 0.058)

    for dy in range(-head_ry - 4, head_ry + 4):
        for dx in range(-head_rx - 4, head_rx + 4):
            px, py = head_cx + dx, head_cy + dy
            if 0 <= px < W and 0 <= py < H:
                hd = (dx / max(head_rx, 1)) ** 2 + (dy / max(head_ry, 1)) ** 2
                if hd <= 1.08:
                    lit = max(0.0, min(1.0, (-dx / head_rx * 0.45 - dy / head_ry * 0.30 + 0.30)))
                    irid_h = min(1.0, lit * 2.0)
                    dark_h = np.array([0.04, 0.04, 0.06], dtype=np.float32)
                    irid_col_h = np.array([0.06, 0.14, 0.32], dtype=np.float32)
                    col = _blend(dark_h, irid_col_h, irid_h)
                    fade = max(0.0, 1.0 - (hd - 0.85) / 0.23) if hd > 0.85 else 1.0
                    ref[py, px] = _blend(ref[py, px], col, fade * 0.96)

    # Beak: large, powerful, curved -- dark grey with ivory at cutting edge
    beak_tip_x = head_cx - int(head_rx * 0.95)
    beak_tip_y = head_cy + int(head_ry * 0.05)
    beak_base_x = head_cx - int(head_rx * 0.12)
    beak_base_y = head_cy - int(head_ry * 0.12)
    for bt in range(24):
        bt_f = bt / 23.0
        bpx = int(beak_base_x + bt_f * (beak_tip_x - beak_base_x))
        bpy = int(beak_base_y + bt_f * (beak_tip_y - beak_base_y))
        bwidth = max(1, int((1.0 - bt_f) * head_rx * 0.28))
        for bdy in range(-bwidth, bwidth + 1):
            bfy = bpy + bdy
            if 0 <= bpx < W and 0 <= bfy < H:
                beak_col = [0.10, 0.10, 0.12] if bt_f < 0.85 else [0.72, 0.70, 0.58]
                ref[bfy, bpx] = _blend(ref[bfy, bpx], beak_col, 0.92)

    # Lower mandible
    for bt in range(18):
        bt_f = bt / 17.0
        bpx = int(beak_base_x - int(head_rx * 0.05) + bt_f * (beak_tip_x - beak_base_x + int(head_rx * 0.05)))
        bpy = int((beak_base_y + int(head_ry * 0.10)) + bt_f * (beak_tip_y - beak_base_y - int(head_ry * 0.08)))
        if 0 <= bpx < W and 0 <= bpy < H:
            ref[bpy, bpx] = _blend(ref[bpy, bpx], [0.08, 0.08, 0.10], 0.88)

    # Eye: startling amber-gold, wide, intelligent
    eye_x = head_cx - int(head_rx * 0.26)
    eye_y = head_cy - int(head_ry * 0.10)
    # Eye socket (dark surround)
    _ellipse(ref, eye_x, eye_y, int(head_rx * 0.22), int(head_ry * 0.18),
             [0.04, 0.04, 0.06], opacity=0.96, feather=0.14)
    # Iris: brilliant amber-gold (Rouault jewel colour)
    _ellipse(ref, eye_x, eye_y, int(head_rx * 0.17), int(head_ry * 0.14),
             [0.84, 0.54, 0.08], opacity=0.92, feather=0.16)
    # Pupil: deep near-black
    _ellipse(ref, eye_x, eye_y, int(head_rx * 0.09), int(head_ry * 0.09),
             [0.04, 0.02, 0.04], opacity=0.98, feather=0.12)
    # Specular highlight: cold sky reflection
    _ellipse(ref, eye_x - int(head_rx * 0.04), eye_y - int(head_ry * 0.04),
             int(head_rx * 0.04), int(head_ry * 0.03),
             [0.72, 0.76, 0.86], opacity=0.88, feather=0.14)

    # Nostril/nare area near beak base
    _ellipse(ref, beak_base_x - int(head_rx * 0.04), beak_base_y + int(head_ry * 0.04),
             int(head_rx * 0.04), int(head_ry * 0.03),
             [0.06, 0.06, 0.08], opacity=0.70, feather=0.22)

    return Image.fromarray(
        (np.clip(ref, 0.0, 1.0) * 255).astype(np.uint8), "RGB")


def paint() -> str:
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s237_rouault_raven.png")
    print("Building reference...")
    ref = make_reference()
    print("Initialising Painter...")
    p = Painter(W, H, seed=237)
    print("Toning ground (near-black imprimatura)...")
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
    print("Underpainting...")
    p.underpainting(ref, stroke_size=54, n_strokes=160)
    print("Block-in...")
    p.block_in(ref, stroke_size=36, n_strokes=290)
    print("Block-in (tighter)...")
    p.block_in(ref, stroke_size=22, n_strokes=380)
    print("Build form...")
    p.build_form(ref, stroke_size=12, n_strokes=500)
    print("Build form (fine)...")
    p.build_form(ref, stroke_size=6, n_strokes=380)
    print("Place lights...")
    p.place_lights(ref, stroke_size=3, n_strokes=280)
    print("Rouault Stained Glass (148th mode)...")
    p.rouault_stained_glass_pass(
        contour_thresh=0.16,
        contour_depth=0.68,
        contour_power=1.6,
        lead_cool=0.07,
        jewel_boost=0.52,
        opacity=0.80,
    )
    print("Paint Scumble (session 237 improvement)...")
    p.paint_scumble_pass(
        bristle_sigma=0.70,
        bristle_thresh=0.62,
        scumble_lift=0.12,
        cool_tint=0.05,
        lum_gate_low=0.28,
        lum_gate_high=0.82,
        opacity=0.44,
        seed=237,
    )
    print("Diffuse boundary...")
    p.diffuse_boundary_pass(low_grad=0.04, high_grad=0.22,
                            sigma=0.8, strength=0.38, opacity=0.46)
    print("Glaze (prussian blue-grey)...")
    p.glaze((0.04, 0.06, 0.14), opacity=0.05)
    print("Vignette...")
    p.canvas.vignette(strength=0.50)
    p.canvas.save(out_path)
    print(f"  Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint()
    print("Done:", result)
