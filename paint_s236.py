"""paint_s236.py -- Session 236: The Lighthouse at the Threshold (Kupka Orphic Fugue)."""
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
    for dy in range(-int(ry * 1.15), int(ry * 1.15) + 1):
        for dx in range(-int(rx * 1.15), int(rx * 1.15) + 1):
            px, py = cx + dx, cy + dy
            if 0 <= px < w and 0 <= py < h:
                d = (dx / max(rx, 1)) ** 2 + (dy / max(ry, 1)) ** 2
                if d <= (1.0 + feather) ** 2:
                    alpha = max(0.0, min(1.0,
                        (1.0 + feather - math.sqrt(d)) / feather))
                    arr[py, px] = _blend(arr[py, px], color, alpha * opacity)


def make_reference():
    ref = np.zeros((H, W, 3), dtype=np.float32)
    rng = np.random.RandomState(236)

    # ── Sky: banded dusk -- five pure color planes (Kupka vertical planes) ──
    # From top: near-black midnight → prussian blue → cerulean → cadmium red → amber
    sky_bands = [
        (0.00, 0.18, (0.04, 0.04, 0.12)),   # near-black midnight
        (0.18, 0.36, (0.04, 0.16, 0.55)),   # prussian blue
        (0.36, 0.52, (0.10, 0.38, 0.72)),   # cerulean
        (0.52, 0.65, (0.72, 0.14, 0.08)),   # cadmium red horizon
        (0.65, 0.74, (0.96, 0.72, 0.06)),   # chrome amber glow
    ]
    for y in range(H):
        yt = y / H
        for x in range(W):
            col = np.array([0.04, 0.04, 0.12], dtype=np.float32)
            for y0, y1, band_col in sky_bands:
                if y0 <= yt < y1:
                    # Hard-edge between bands (Kupka's pure planes)
                    band_t = (yt - y0) / (y1 - y0)
                    # Slightly soften band edge (10% blend zone at boundary)
                    prev_col = np.array([0.04, 0.04, 0.12], dtype=np.float32)
                    for py0, py1, pc in sky_bands:
                        if py1 == y0:
                            prev_col = np.array(pc, dtype=np.float32)
                    edge_blend = min(1.0, band_t * 8.0)
                    col = prev_col * (1 - edge_blend) + np.array(band_col, dtype=np.float32) * edge_blend
                    break
            ref[y, x] = col

    # ── Sea: below horizon (y > 0.74H) ──
    horizon_y = int(H * 0.74)
    for y in range(horizon_y, H):
        td = (y - horizon_y) / (H - horizon_y)
        for x in range(W):
            # Dark prussian sea with amber reflection band from lighthouse
            sea_col = np.array([0.04, 0.12, 0.42], dtype=np.float32)
            sea_col = sea_col * (1.0 - td * 0.6)  # darken toward foreground
            ref[y, x] = sea_col

    # ── Amber reflection streak from lighthouse lamp on water ──
    lamp_x = int(W * 0.58)  # lighthouse x position
    lamp_y = int(H * 0.28)  # lamp height
    for y in range(horizon_y, H):
        yt = (y - horizon_y) / (H - horizon_y)
        for dx in range(-int(W * 0.10), int(W * 0.10) + 1):
            px = lamp_x + dx
            if 0 <= px < W:
                # Reflection: narrower near horizon, widens toward foreground
                streak_width = W * 0.012 + dx * 0.0 + yt * W * 0.06
                streak_gate = max(0.0, 1.0 - abs(dx) / streak_width) ** 1.8
                if streak_gate > 0.01:
                    amber_col = np.array([0.92, 0.68, 0.08], dtype=np.float32)
                    ref[y, px] = _blend(ref[y, px], amber_col,
                                        streak_gate * 0.55 * (1 - yt * 0.6))

    # ── Foreground: volcanic basalt rocks -- near-black with wet glints ──
    rock_y = int(H * 0.82)
    for y in range(rock_y, H):
        td = (y - rock_y) / (H - rock_y)
        for x in range(W):
            # Near-black with slight blue-grey sheen
            rock_base = np.array([0.06, 0.06, 0.09], dtype=np.float32)
            noise = rng.uniform(-0.02, 0.02, 3).astype(np.float32)
            ref[y, x] = np.clip(rock_base + noise, 0, 1)

    # Rock surface texture: irregular dark boulders
    for _ in range(18):
        rx_c = int(rng.uniform(0, W))
        ry_c = int(rng.uniform(rock_y + 10, H - 5))
        rx_r = int(rng.uniform(15, 55))
        ry_r = int(rng.uniform(8, 22))
        col = [rng.uniform(0.04, 0.10), rng.uniform(0.04, 0.10),
               rng.uniform(0.06, 0.13)]
        _ellipse(ref, rx_c, ry_c, rx_r, ry_r, col,
                 opacity=rng.uniform(0.6, 0.9), feather=0.25)

    # Wet rock glints (amber/white reflections from the amber sky)
    for _ in range(22):
        gx = int(rng.uniform(W * 0.10, W * 0.90))
        gy = int(rng.uniform(rock_y + 5, H - 8))
        gcol = [rng.uniform(0.55, 0.85), rng.uniform(0.45, 0.70),
                rng.uniform(0.05, 0.20)]
        _ellipse(ref, gx, gy, int(rng.uniform(3, 10)), int(rng.uniform(1, 3)),
                 gcol, opacity=rng.uniform(0.30, 0.65), feather=0.35)

    # ── Lighthouse tower -- white cylindrical shaft ──
    lh_cx = lamp_x
    lh_base_y = int(H * 0.82)   # base at rock line
    lh_top_y  = int(H * 0.30)   # top (lamp room level)
    lh_width_base = int(W * 0.038)
    lh_width_top  = int(W * 0.028)

    for y in range(lh_top_y, lh_base_y):
        ty = (y - lh_top_y) / (lh_base_y - lh_top_y)
        half_w = int(lh_width_top + (lh_width_base - lh_width_top) * ty)
        for dx in range(-half_w - 1, half_w + 2):
            px = lh_cx + dx
            if 0 <= px < W:
                # Light side (left, facing sky glow) vs shadow side (right)
                lit = max(0.0, 1.0 - dx / max(half_w, 1) * 0.55)
                edge_fade = max(0.0, 1.0 - (abs(dx) / max(half_w, 1) - 0.80) / 0.20) \
                            if abs(dx) > half_w * 0.80 else 1.0
                bright_col = np.array([0.94, 0.90, 0.84], dtype=np.float32)
                shadow_col = np.array([0.52, 0.50, 0.58], dtype=np.float32)
                col = _blend(shadow_col, bright_col, lit * 0.82)
                ref[y, px] = _blend(ref[y, px], col, edge_fade * 0.96)

    # Lighthouse bands (horizontal paint bands every ~12% height)
    for band_frac in [0.20, 0.40, 0.60, 0.78]:
        band_y = int(lh_top_y + (lh_base_y - lh_top_y) * band_frac)
        ty = band_frac
        half_w = int(lh_width_top + (lh_width_base - lh_width_top) * ty)
        for dy2 in range(-2, 3):
            for dx in range(-half_w - 1, half_w + 2):
                px, py2 = lh_cx + dx, band_y + dy2
                if 0 <= px < W and 0 <= py2 < H:
                    ref[py2, px] = _blend(ref[py2, px],
                                         [0.72, 0.68, 0.74], 0.55)

    # ── Lamp room (lantern gallery) ──
    lamp_room_y = int(H * 0.305)
    lamp_room_r = int(W * 0.042)
    lamp_room_ry = int(H * 0.022)

    # Gallery railing
    _ellipse(ref, lh_cx, lamp_room_y + lamp_room_ry + 4,
             lamp_room_r + 6, 5,
             [0.22, 0.22, 0.26], opacity=0.88, feather=0.20)

    # Lantern housing -- dark metal cage
    _ellipse(ref, lh_cx, lamp_room_y,
             lamp_room_r, lamp_room_ry,
             [0.18, 0.18, 0.22], opacity=0.90, feather=0.15)

    # ── Lamp: warm gold-amber light source ──
    lamp_core_x, lamp_core_y = lh_cx, int(H * 0.283)

    # Outer corona -- large warm halo
    for r_halo in [32, 22, 14, 8, 4]:
        alpha = 0.08 + (32 - r_halo) * 0.015
        halo_col = [min(1.0, 0.92 + (32 - r_halo) * 0.003),
                    0.72 - (32 - r_halo) * 0.012,
                    0.04]
        _ellipse(ref, lamp_core_x, lamp_core_y, r_halo, r_halo,
                 halo_col, opacity=alpha, feather=0.35)

    # Bright core
    _ellipse(ref, lamp_core_x, lamp_core_y, 6, 6,
             [1.0, 0.90, 0.42], opacity=0.96, feather=0.25)
    _ellipse(ref, lamp_core_x, lamp_core_y, 3, 3,
             [1.0, 0.96, 0.80], opacity=1.0, feather=0.15)

    # ── Lighthouse beam -- diagonal ray upper-left ──
    beam_start_x, beam_start_y = lamp_core_x, lamp_core_y
    beam_angle = -2.3   # radians, upper-left
    beam_len = int(W * 1.1)
    for step in range(beam_len):
        t = step / beam_len
        bx = int(beam_start_x + step * math.cos(beam_angle))
        by = int(beam_start_y + step * math.sin(beam_angle))
        if not (0 <= bx < W and 0 <= by < H):
            break
        beam_width = 2 + int(t * 12)
        beam_bright = max(0.0, 0.55 * (1 - t ** 0.6))
        for dw in range(-beam_width, beam_width + 1):
            px = bx + dw
            if 0 <= px < W:
                fade = max(0.0, 1.0 - abs(dw) / max(beam_width, 1)) ** 1.4
                ref[by, px] = _blend(ref[by, px],
                                     [0.96, 0.88, 0.52],
                                     fade * beam_bright)

    # ── Distant shore / sea rocks (mid-ground silhouettes) ──
    shore_y = int(H * 0.76)
    for _ in range(6):
        rx_c = int(rng.uniform(0, W))
        ry_c = shore_y + int(rng.uniform(-8, 8))
        _ellipse(ref, rx_c, ry_c, int(rng.uniform(25, 65)),
                 int(rng.uniform(6, 16)),
                 [0.04, 0.04, 0.06], opacity=rng.uniform(0.55, 0.80),
                 feather=0.35)

    # ── Stars (above the cerulean band) ──
    for _ in range(55):
        sx = int(rng.uniform(0, W))
        sy = int(rng.uniform(0, H * 0.35))
        sr = rng.uniform(0.8, 1.4)
        scol = [rng.uniform(0.82, 1.0), rng.uniform(0.78, 0.96),
                rng.uniform(0.62, 0.88)]
        fade = max(0.0, 1.0 - abs(sx / W - 0.5) * 1.8)
        if 0 <= sy < H and 0 <= sx < W:
            ref[sy, sx] = _blend(ref[sy, sx], scol, sr * fade * 0.85)

    img = Image.fromarray(
        (np.clip(ref, 0.0, 1.0) * 255).astype(np.uint8), "RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    return img


def paint() -> str:
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s236_kupka_lighthouse.png")
    print("Building reference...")
    ref = make_reference()
    print("Initialising Painter...")
    p = Painter(W, H, seed=236)
    print("Toning ground (near-black prussian imprimatura)...")
    p.tone_ground((0.04, 0.05, 0.14), texture_strength=0.04)
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
    print("Kupka Orphic Fugue (147th mode)...")
    p.kupka_orphic_fugue_pass(
        hue_amplitude=0.14,
        hue_period_frac=0.26,
        hue_phase=0.0,
        centroid_thresh=0.60,
        chroma_boost=0.32,
        mid_lum_center=0.50,
        mid_lum_width=0.22,
        opacity=0.86,
    )
    print("Paint Medium Pooling (session 236 improvement)...")
    p.paint_medium_pooling_pass(
        pool_size=5,
        pool_depth=0.042,
        pool_sat_lift=0.13,
        pool_thresh=0.032,
        pool_power=0.72,
        opacity=0.58,
    )
    print("Diffuse boundary...")
    p.diffuse_boundary_pass(low_grad=0.04, high_grad=0.20,
                            sigma=0.8, strength=0.35, opacity=0.45)
    print("Glaze (prussian blue night)...")
    p.glaze((0.02, 0.06, 0.16), opacity=0.04)
    print("Vignette...")
    p.canvas.vignette(strength=0.48)
    p.canvas.save(out_path)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint()
    print("Done:", result)
