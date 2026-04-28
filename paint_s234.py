"""paint_s234.py -- Session 234: The Fisherman's Vigil (Ryder Moonlit Sea)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter

W, H = 540, 700


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
    rng = np.random.RandomState(234)

    horizon_y = int(H * 0.42)
    moon_y    = int(H * 0.25)
    moon_x    = int(W * 0.42)

    # Sky: dark indigo-black gradient with amber-warm horizon glow
    for y in range(horizon_y):
        sky_t = y / max(horizon_y, 1)
        if sky_t < 0.35:
            sky_col = np.array([0.04, 0.04, 0.08], dtype=np.float32)
        elif sky_t < 0.65:
            t = (sky_t - 0.35) / 0.30
            sky_col = _blend(
                np.array([0.04, 0.04, 0.08], dtype=np.float32),
                [0.08, 0.07, 0.16], t)
        else:
            t = (sky_t - 0.65) / 0.35
            sky_col = _blend(
                np.array([0.08, 0.07, 0.16], dtype=np.float32),
                [0.34, 0.28, 0.14], t)
        ref[y, :] = sky_col

    # Torn cloud wisps near horizon
    for _ in range(6):
        cy = int(rng.uniform(horizon_y - int(H * 0.16), horizon_y - int(H * 0.04)))
        cx = int(rng.uniform(int(W * 0.05), int(W * 0.85)))
        clen = int(rng.uniform(int(W * 0.10), int(W * 0.28)))
        ch = int(rng.uniform(int(H * 0.006), int(H * 0.018)))
        c_lum = rng.uniform(0.22, 0.44)
        c_col = [c_lum * 1.0, c_lum * 0.82, c_lum * 0.42]
        for dx in range(clen):
            px = cx + dx
            if 0 <= px < W:
                for dy_c in range(-ch, ch + 1):
                    py = cy + dy_c
                    if 0 <= py < H:
                        edge_fade = max(0.0, 1.0 - abs(dy_c) / max(ch, 1))
                        long_fade = max(0.0, min(1.0,
                            min(dx / (clen * 0.25 + 1), (clen - dx) / (clen * 0.25 + 1))))
                        alpha = edge_fade * long_fade * 0.55
                        ref[py, px] = _blend(ref[py, px], c_col, alpha)

    # Moon: diffuse amber-cream glow (warm, not cold like Kuindzhi)
    moon_r = int(W * 0.030)
    for r_mult, bright, alpha in [
        (6.0, [0.20, 0.18, 0.10], 0.25),
        (4.0, [0.36, 0.30, 0.14], 0.38),
        (2.5, [0.58, 0.50, 0.24], 0.50),
        (1.5, [0.76, 0.68, 0.40], 0.70),
        (1.0, [0.88, 0.82, 0.56], 1.00),
    ]:
        _ellipse(ref, moon_x, moon_y,
                 int(moon_r * r_mult), int(moon_r * r_mult),
                 bright, opacity=alpha, feather=0.55 if r_mult > 2.0 else 0.22)
    _ellipse(ref, moon_x, moon_y,
             int(moon_r * 0.5), int(moon_r * 0.5),
             [0.94, 0.90, 0.70], opacity=1.0, feather=0.15)

    # Sea: near-black with rolling dark swells
    for y in range(horizon_y, H):
        depth_t = (y - horizon_y) / max(H - horizon_y, 1)
        base_col = [
            max(0.0, 0.05 - depth_t * 0.02),
            max(0.0, 0.04 - depth_t * 0.015),
            max(0.0, 0.07 - depth_t * 0.025),
        ]
        ref[y, :] = base_col

    # Dark wave crests with warm amber moonlight touch
    for _ in range(18):
        wy = int(rng.uniform(horizon_y + int(H * 0.04), H - int(H * 0.08)))
        wx = int(rng.uniform(0, W - int(W * 0.15)))
        wlen = int(rng.uniform(int(W * 0.08), int(W * 0.25)))
        w_lum = rng.uniform(0.08, 0.18)
        w_col = [w_lum * 0.92, w_lum * 0.80, w_lum * 0.42]
        for i in range(wlen):
            px = wx + i
            if 0 <= px < W:
                undulate = int(math.sin(i * 0.12 + wx * 0.05) * 2)
                py = wy + undulate
                if 0 <= py < H:
                    ref[py, px] = _blend(ref[py, px], w_col, 0.60)

    # Moon reflection on water: soft amber column
    refl_cx = moon_x
    refl_w = int(W * 0.06)
    for y in range(horizon_y, H):
        depth_t = (y - horizon_y) / max(H - horizon_y, 1)
        depth_fade = max(0.0, 1.0 - depth_t * 0.85)
        for dx in range(-refl_w * 2, refl_w * 2 + 1):
            rx2 = refl_cx + dx
            if 0 <= rx2 < W:
                ripple = math.sin(y * 0.18 + abs(dx) * 0.35) * int(W * 0.005)
                eff_dx = abs(dx + ripple)
                streak_gate = max(0.0, 1.0 - eff_dx / (refl_w + 1e-6)) ** 2.0
                streak_lum = streak_gate * depth_fade
                if streak_lum > 0.01:
                    r_col = [0.72 * streak_lum, 0.60 * streak_lum, 0.28 * streak_lum]
                    ref[y, rx2] = _blend(ref[y, rx2], r_col, min(1.0, streak_lum * 1.4))

    # Boat: dark hull silhouette
    boat_cy = int(H * 0.62)
    boat_cx = int(W * 0.55)
    hull_w  = int(W * 0.22)
    hull_h  = int(H * 0.055)
    for dx in range(-hull_w, hull_w + 1):
        taper = 1.0 - (dx / max(hull_w, 1)) ** 2
        local_h = max(1, int(hull_h * taper))
        for dy in range(-local_h // 2, local_h // 2 + 1):
            py = boat_cy + dy
            px = boat_cx + dx
            if 0 <= px < W and 0 <= py < H:
                ref[py, px] = np.array([0.05, 0.04, 0.06], dtype=np.float32)

    # Mast
    mast_x = boat_cx - int(W * 0.02)
    mast_bot = boat_cy - hull_h // 2
    mast_top = int(H * 0.10)
    for y in range(mast_top, mast_bot + 1):
        if 0 <= mast_x < W and 0 <= y < H:
            ref[y, mast_x] = np.array([0.06, 0.05, 0.07], dtype=np.float32)
            if 0 <= mast_x + 1 < W:
                ref[y, mast_x + 1] = np.array([0.06, 0.05, 0.07], dtype=np.float32)

    # Boom
    boom_y = mast_top + int((mast_bot - mast_top) * 0.55)
    boom_len = int(W * 0.12)
    for ddx in range(-4, boom_len + 4):
        px = mast_x + ddx
        if 0 <= px < W and 0 <= boom_y < H:
            ref[boom_y, px] = np.array([0.06, 0.05, 0.07], dtype=np.float32)

    # Furled sail mass
    sail_cx = mast_x + boom_len // 3
    sail_w = int(W * 0.06)
    sail_h = int(H * 0.05)
    for dy in range(-sail_h // 2, sail_h // 2 + 1):
        for ddx in range(-sail_w // 2, sail_w // 2 + 1):
            px = sail_cx + ddx
            py = boom_y + dy
            if 0 <= px < W and 0 <= py < H:
                ref[py, px] = np.array([0.07, 0.06, 0.08], dtype=np.float32)

    # Fisherman: solitary silhouette at bow, hunched
    fig_x = boat_cx - int(W * 0.09)
    fig_y_bot = boat_cy - hull_h // 2
    fig_h = int(H * 0.09)
    for dy in range(-fig_h, 4):
        py = fig_y_bot + dy
        taper_t = abs(dy) / max(fig_h, 1)
        body_w = max(2, int(int(W * 0.018) * (0.5 + taper_t * 0.5)))
        for ddx in range(-body_w, body_w + 1):
            px = fig_x + ddx
            if 0 <= px < W and 0 <= py < H:
                ref[py, px] = np.array([0.04, 0.04, 0.06], dtype=np.float32)
    _ellipse(ref, fig_x, fig_y_bot - fig_h - int(H * 0.012),
             int(W * 0.012), int(H * 0.018),
             [0.05, 0.04, 0.06], opacity=1.0, feather=0.15)

    img = Image.fromarray(
        (np.clip(ref, 0.0, 1.0) * 255).astype(np.uint8), "RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=1.0))
    return img


def paint() -> str:
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s234_ryder_fishermans_vigil.png")
    print("Building reference...")
    ref = make_reference()
    print("Initialising Painter...")
    p = Painter(W, H, seed=234)
    print("Toning ground (warm dark umber imprimatura)...")
    p.tone_ground((0.14, 0.11, 0.08), texture_strength=0.04)
    print("Underpainting...")
    p.underpainting(ref, stroke_size=55, n_strokes=140)
    print("Block-in (broad)...")
    p.block_in(ref, stroke_size=36, n_strokes=260)
    print("Block-in (medium)...")
    p.block_in(ref, stroke_size=20, n_strokes=360)
    print("Build form...")
    p.build_form(ref, stroke_size=11, n_strokes=440)
    print("Build form (fine)...")
    p.build_form(ref, stroke_size=5, n_strokes=320)
    print("Place lights...")
    p.place_lights(ref, stroke_size=3, n_strokes=220)
    print("Ryder Moonlit Sea (145th mode)...")
    p.ryder_moonlit_sea_pass(
        dark_thresh=0.34,
        dark_power=1.90,
        dark_crush=0.45,
        light_thresh=0.62,
        light_power=1.60,
        light_lift=0.28,
        amber_center=0.40,
        amber_width=0.26,
        amber_r=0.15,
        amber_g=0.06,
        amber_b=0.10,
        amber_str=0.78,
        dissolution_sigma=2.50,
        dissolution_blend=0.25,
        opacity=0.88,
    )
    print("Paint Varnish Depth (session 234 improvement)...")
    p.paint_varnish_depth_pass(
        sat_center=0.44,
        sat_width=0.28,
        sat_boost=0.32,
        sheen_thresh=0.74,
        sheen_sigma=3.8,
        sheen_strength=0.055,
        opacity=0.68,
        seed=234,
    )
    print("Diffuse boundary...")
    p.diffuse_boundary_pass(low_grad=0.03, high_grad=0.22,
                            sigma=0.8, strength=0.30, opacity=0.40)
    print("Glaze (amber-umber)...")
    p.glaze((0.32, 0.24, 0.10), opacity=0.05)
    print("Vignette...")
    p.canvas.vignette(strength=0.60)
    p.canvas.save(out_path)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint()
    print("Done:", result)
