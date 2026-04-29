"""paint_s238.py -- Session 238: The Crystalline Harbor (Feininger Prism, 149th mode)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
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
                    alpha = max(0.0, min(1.0, (1.0 + feather - math.sqrt(d)) / feather))
                    arr[py, px] = _blend(arr[py, px], color, alpha * opacity)


def _line(arr, x0, y0, x1, y1, color, thickness=1, opacity=1.0):
    h, w = arr.shape[:2]
    dx, dy = x1 - x0, y1 - y0
    length = max(int(math.sqrt(dx * dx + dy * dy)), 1)
    for i in range(length + 1):
        t = i / length
        px = int(x0 + t * dx)
        py = int(y0 + t * dy)
        for tx in range(-thickness, thickness + 1):
            for ty in range(-thickness, thickness + 1):
                nx, ny = px + tx, py + ty
                if 0 <= nx < w and 0 <= ny < h:
                    arr[ny, nx] = _blend(arr[ny, nx], color, opacity)


def make_reference():
    ref = np.zeros((H, W, 3), dtype=np.float32)
    rng = np.random.RandomState(238)

    horizon_y = int(H * 0.50)

    # ── Sky: upper half -- cool prussian cobalt deepening upward ──
    for y in range(horizon_y):
        yt = y / horizon_y  # 0=top, 1=horizon
        for x in range(W):
            xt = x / W
            # Sky gradient: deep prussian cobalt at top, warm amber-ochre at horizon
            deep_sky   = np.array([0.10, 0.14, 0.36], dtype=np.float32)
            mid_sky    = np.array([0.22, 0.30, 0.50], dtype=np.float32)
            glow_sky   = np.array([0.62, 0.52, 0.28], dtype=np.float32)
            if yt < 0.55:
                t = yt / 0.55
                col = _blend(deep_sky, mid_sky, t)
            else:
                t = (yt - 0.55) / 0.45
                col = _blend(mid_sky, glow_sky, t)
            ref[y, x] = col

    # Horizon amber-gold glow band
    for y in range(int(H * 0.40), horizon_y):
        yt = (y - H * 0.40) / (horizon_y - H * 0.40)
        bell = math.exp(-0.5 * ((yt - 0.80) / 0.18) ** 2)
        glow = np.array([0.78, 0.60, 0.22], dtype=np.float32)
        for x in range(W):
            ref[y, x] = _blend(ref[y, x], glow, bell * 0.55)

    # Feininger angular cloud planes -- slate violet, cool grey, layered diagonals
    cloud_planes = [
        # (x_left, x_right, y_top, y_bot, color, opacity)
        (int(W * 0.00), int(W * 0.38), int(H * 0.04), int(H * 0.18),
         (0.28, 0.30, 0.48), 0.58),
        (int(W * 0.22), int(W * 0.68), int(H * 0.08), int(H * 0.20),
         (0.24, 0.26, 0.44), 0.52),
        (int(W * 0.55), int(W * 1.00), int(H * 0.02), int(H * 0.16),
         (0.26, 0.28, 0.46), 0.55),
        (int(W * 0.08), int(W * 0.52), int(H * 0.22), int(H * 0.30),
         (0.20, 0.24, 0.40), 0.45),
        (int(W * 0.46), int(W * 0.90), int(H * 0.24), int(H * 0.34),
         (0.18, 0.22, 0.38), 0.42),
        (int(W * 0.62), int(W * 1.00), int(H * 0.30), int(H * 0.40),
         (0.22, 0.26, 0.44), 0.38),
        (int(W * 0.00), int(W * 0.30), int(H * 0.28), int(H * 0.38),
         (0.20, 0.24, 0.42), 0.40),
    ]
    for xl, xr, yt_px, yb_px, col, op in cloud_planes:
        for y in range(yt_px, yb_px):
            yfrac = (y - yt_px) / max(yb_px - yt_px, 1)
            # Feathered top and bottom edges
            alpha = min(yfrac * 4.0, (1.0 - yfrac) * 4.0, 1.0)
            # Slight diagonal shear: left edge shifts upward
            x_shear = int((1.0 - yfrac) * W * 0.03)
            for x in range(max(0, xl + x_shear), min(W, xr + x_shear)):
                xfrac = (x - xl) / max(xr - xl, 1)
                xalpha = min(xfrac * 6.0, (1.0 - xfrac) * 6.0, 1.0)
                ref[y, x] = _blend(ref[y, x], list(col), op * alpha * xalpha)

    # ── Water: lower half -- pewter grey-green with angular facet reflections ──
    for y in range(horizon_y, H):
        yt = (y - horizon_y) / (H - horizon_y)
        for x in range(W):
            xt = x / W
            # Deep cold water -- slate grey-green darkens toward bottom
            surface_water = np.array([0.32, 0.38, 0.44], dtype=np.float32)
            deep_water    = np.array([0.10, 0.14, 0.22], dtype=np.float32)
            col = _blend(surface_water, deep_water, yt * 0.85)
            ref[y, x] = col

    # Horizon reflection band: amber glow mirrored into near-water surface
    for y in range(horizon_y, int(H * 0.58)):
        yt = (y - horizon_y) / (int(H * 0.58) - horizon_y)
        bell = math.exp(-0.5 * (yt / 0.35) ** 2)
        warm_refl = np.array([0.52, 0.44, 0.24], dtype=np.float32)
        for x in range(W):
            ref[y, x] = _blend(ref[y, x], warm_refl, bell * 0.45)

    # Angular water facet planes (Feininger geometric reflections)
    water_planes = [
        # x_left, x_right, y_top, y_bot, color, opacity
        (int(W * 0.05), int(W * 0.28), int(H * 0.52), int(H * 0.60),
         (0.38, 0.46, 0.52), 0.30),
        (int(W * 0.20), int(W * 0.48), int(H * 0.55), int(H * 0.64),
         (0.62, 0.54, 0.32), 0.25),
        (int(W * 0.55), int(W * 0.80), int(H * 0.52), int(H * 0.62),
         (0.36, 0.44, 0.52), 0.28),
        (int(W * 0.68), int(W * 0.96), int(H * 0.57), int(H * 0.66),
         (0.58, 0.50, 0.28), 0.22),
        (int(W * 0.10), int(W * 0.40), int(H * 0.64), int(H * 0.74),
         (0.24, 0.32, 0.42), 0.32),
        (int(W * 0.38), int(W * 0.70), int(H * 0.66), int(H * 0.76),
         (0.58, 0.48, 0.26), 0.20),
        (int(W * 0.60), int(W * 1.00), int(H * 0.68), int(H * 0.80),
         (0.22, 0.30, 0.40), 0.28),
        (int(W * 0.00), int(W * 0.25), int(H * 0.74), int(H * 0.86),
         (0.18, 0.26, 0.36), 0.30),
        (int(W * 0.30), int(W * 0.65), int(H * 0.78), int(H * 0.88),
         (0.28, 0.36, 0.44), 0.25),
    ]
    for xl, xr, yt_px, yb_px, col, op in water_planes:
        for y in range(yt_px, min(yb_px, H)):
            yfrac = (y - yt_px) / max(yb_px - yt_px, 1)
            alpha = min(yfrac * 5.0, (1.0 - yfrac) * 5.0, 1.0)
            # Slight diagonal shear to reinforce angular quality
            x_shear = int(yfrac * W * 0.04)
            for x in range(max(0, xl + x_shear), min(W, xr + x_shear)):
                xfrac = (x - xl) / max(xr - xl, 1)
                xalpha = min(xfrac * 5.0, (1.0 - xfrac) * 5.0, 1.0)
                ref[y, x] = _blend(ref[y, x], list(col), op * alpha * xalpha)

    # ── Sailboat: gaff-rigged sloop, 3/4 view, bow slightly right ──
    hull_cx = int(W * 0.50)
    hull_cy = horizon_y + int(H * 0.04)

    # Hull: warm ochre-cream, painted wood, slightly weathered
    hull_w = int(W * 0.14)
    hull_h = int(H * 0.06)
    for y in range(hull_cy - hull_h // 2, hull_cy + hull_h):
        yt = (y - (hull_cy - hull_h // 2)) / hull_h
        # Hull narrows toward bow (right) and slightly toward stern (left)
        width_scale = max(0.3, 1.0 - abs(yt - 0.35) * 0.6)
        hw = int(hull_w * width_scale)
        # Bow shear: right end slightly lower
        bow_offset = int(yt * hull_h * 0.12)
        for x in range(hull_cx - hw, hull_cx + hw):
            xfrac = (x - (hull_cx - hw)) / max(2 * hw, 1)
            d_ellipse = ((x - hull_cx) / max(hw, 1)) ** 2 + ((y - hull_cy) / max(hull_h * 0.5, 1)) ** 2
            if d_ellipse <= 1.08:
                # Hull color: warm ochre, slightly darker below waterline
                if y > hull_cy + hull_h * 0.3:
                    hull_col = [0.52, 0.40, 0.20]  # wet hull below waterline
                else:
                    hull_col = [0.70, 0.58, 0.34]  # warm ochre above
                fade = max(0.0, 1.0 - (d_ellipse - 0.82) / 0.26) if d_ellipse > 0.82 else 1.0
                ref[y, x] = _blend(ref[y, x], hull_col, fade * 0.94)

    # Hull deck top edge: a thin dark line
    for x in range(hull_cx - hull_w + 5, hull_cx + hull_w - 5):
        deck_y = hull_cy - hull_h // 2 + int((x - hull_cx) / (hull_w * 0.8) * hull_h * 0.04)
        if 0 <= deck_y < H:
            ref[deck_y, x] = _blend(ref[deck_y, x], [0.18, 0.16, 0.14], 0.88)

    # Cabin / deckhouse: small rectangular structure mid-hull
    cabin_cx = hull_cx - int(W * 0.02)
    cabin_cy = hull_cy - hull_h // 2 - int(H * 0.025)
    cabin_w = int(W * 0.050)
    cabin_h = int(H * 0.030)
    for y in range(cabin_cy, cabin_cy + cabin_h):
        for x in range(cabin_cx - cabin_w // 2, cabin_cx + cabin_w // 2):
            if 0 <= x < W and 0 <= y < H:
                yfrac = (y - cabin_cy) / max(cabin_h, 1)
                col = [0.62, 0.52, 0.30] if yfrac < 0.5 else [0.52, 0.42, 0.22]
                ref[y, x] = _blend(ref[y, x], col, 0.88)

    # ── Mast: tall, dark, slightly raked aft ──
    mast_base_x = hull_cx - int(W * 0.010)
    mast_base_y = hull_cy - hull_h // 2
    mast_height = int(H * 0.42)
    mast_top_x  = mast_base_x - int(W * 0.018)  # slight aft rake
    mast_top_y  = mast_base_y - mast_height
    _line(ref, mast_base_x, mast_base_y, mast_top_x, mast_top_y,
          [0.14, 0.13, 0.12], thickness=1, opacity=0.96)

    # ── Gaff spar: diagonal boom from mast top ──
    gaff_end_x = mast_top_x + int(W * 0.08)
    gaff_end_y = mast_top_y + int(H * 0.08)
    _line(ref, mast_top_x, mast_top_y, gaff_end_x, gaff_end_y,
          [0.16, 0.14, 0.12], thickness=1, opacity=0.90)

    # ── Boom: near-horizontal from mast base area ──
    boom_start_x = mast_base_x
    boom_start_y = mast_base_y - int(H * 0.008)
    boom_end_x = hull_cx + int(W * 0.10)
    boom_end_y = boom_start_y + int(H * 0.01)
    _line(ref, boom_start_x, boom_start_y, boom_end_x, boom_end_y,
          [0.16, 0.14, 0.12], thickness=1, opacity=0.85)

    # ── Mainsail (furled, rolled on boom) ──
    sail_cx = int((mast_base_x + boom_end_x) / 2)
    sail_cy = int((mast_base_y + boom_end_y) / 2) - int(H * 0.005)
    sail_rx = int((boom_end_x - mast_base_x) / 2 - W * 0.01)
    sail_ry = int(H * 0.012)
    _ellipse(ref, sail_cx, sail_cy, sail_rx, sail_ry,
             [0.78, 0.76, 0.66], opacity=0.82, feather=0.30)

    # ── Gaff sail (furled, on gaff) ──
    gsail_cx = int((mast_top_x + gaff_end_x) / 2)
    gsail_cy = int((mast_top_y + gaff_end_y) / 2)
    gsail_rx = int(W * 0.028)
    gsail_ry = int(H * 0.010)
    _ellipse(ref, gsail_cx, gsail_cy, gsail_rx, gsail_ry,
             [0.76, 0.74, 0.64], opacity=0.78, feather=0.30)

    # ── Stays and rigging: thin lines ──
    # Forestay: mast top to bow
    bow_x = hull_cx + hull_w - 5
    bow_y = hull_cy - hull_h // 4
    _line(ref, mast_top_x, mast_top_y, bow_x, bow_y,
          [0.18, 0.16, 0.14], thickness=0, opacity=0.65)

    # Backstay: mast top to stern
    stern_x = hull_cx - hull_w + 8
    stern_y = hull_cy - hull_h // 4
    _line(ref, mast_top_x, mast_top_y, stern_x, stern_y,
          [0.18, 0.16, 0.14], thickness=0, opacity=0.60)

    # Shrouds (port and starboard)
    for shroud_x_offset in [-int(W * 0.04), int(W * 0.04)]:
        shroud_x = hull_cx + shroud_x_offset
        shroud_y = hull_cy - int(hull_h * 0.3)
        shroud_top_x = mast_top_x + int(shroud_x_offset * 0.15)
        shroud_top_y = mast_top_y + int(mast_height * 0.25)
        _line(ref, shroud_top_x, shroud_top_y, shroud_x, shroud_y,
              [0.18, 0.16, 0.14], thickness=0, opacity=0.55)

    # ── Boat reflection in water ──
    refl_start = hull_cy + hull_h // 2
    refl_depth = int(H * 0.035)
    for dy in range(refl_depth):
        fade = 1.0 - dy / refl_depth
        ry = refl_start + dy
        if ry < H:
            for x in range(hull_cx - hull_w + 5, hull_cx + hull_w - 5):
                if 0 <= x < W:
                    hull_above = hull_cy + hull_h // 2 - 1
                    if 0 <= hull_above < H:
                        src_col = ref[hull_above, x]
                        # Slightly desaturate and cool the reflection
                        lum_r = float(0.299 * src_col[0] + 0.587 * src_col[1] + 0.114 * src_col[2])
                        refl_col = [
                            lum_r + (src_col[0] - lum_r) * 0.5,
                            lum_r + (src_col[1] - lum_r) * 0.5,
                            lum_r + (src_col[2] - lum_r) * 0.5 + 0.04,
                        ]
                        ref[ry, x] = _blend(ref[ry, x], refl_col, fade * 0.62)

    # Mast reflection
    refl_mast_depth = int(H * 0.06)
    for dy in range(refl_mast_depth):
        fade = (1.0 - dy / refl_mast_depth) * 0.55
        ry = refl_start + dy
        rx = mast_base_x + int(rng.uniform(-1, 2))
        if 0 <= ry < H and 0 <= rx < W:
            ref[ry, rx] = _blend(ref[ry, rx], [0.18, 0.16, 0.14], fade)

    # ── Atmospheric mist at horizon line ──
    mist_half = int(H * 0.018)
    for y in range(horizon_y - mist_half, horizon_y + mist_half):
        if 0 <= y < H:
            dist = abs(y - horizon_y) / mist_half
            mist_alpha = math.exp(-0.5 * (dist / 0.45) ** 2) * 0.52
            mist_col = [0.74, 0.72, 0.64]
            for x in range(W):
                ref[y, x] = _blend(ref[y, x], mist_col, mist_alpha)

    # ── Distant sail silhouettes on horizon (left and right) ──
    for sail_x, sail_h_scale in [(int(W * 0.12), 0.65), (int(W * 0.82), 0.55)]:
        sail_mast_y = horizon_y - int(H * 0.14 * sail_h_scale)
        sail_mast_x = sail_x
        sail_hull_y = horizon_y
        _line(ref, sail_mast_x, sail_mast_y, sail_mast_x, sail_hull_y,
              [0.18, 0.18, 0.22], thickness=0, opacity=0.50)
        # Small triangle sail
        for step in range(int(H * 0.12 * sail_h_scale)):
            yfrac = step / (H * 0.12 * sail_h_scale)
            sw = int(W * 0.025 * (1.0 - yfrac) * sail_h_scale)
            sy = sail_hull_y - step
            for dx in range(-2, sw):
                sx = sail_mast_x + dx
                if 0 <= sx < W and 0 <= sy < H:
                    ref[sy, sx] = _blend(ref[sy, sx], [0.64, 0.60, 0.50], 0.38)

    # ── Foreground ripple lines ──
    for rl in range(8):
        ry_base = int(H * (0.72 + rl * 0.032))
        if ry_base >= H:
            break
        ripple_col = [0.34, 0.40, 0.46] if rl % 2 == 0 else [0.58, 0.50, 0.28]
        for x in range(W):
            wave = math.sin(x * 0.04 + rl * 1.1) * 1.5
            ry = ry_base + int(wave)
            if 0 <= ry < H:
                ref[ry, x] = _blend(ref[ry, x], ripple_col, 0.28)

    return Image.fromarray(
        (np.clip(ref, 0.0, 1.0) * 255).astype(np.uint8), "RGB")


def paint() -> str:
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s238_feininger_harbor.png")
    print("Building reference...")
    ref = make_reference()
    print("Initialising Painter...")
    p = Painter(W, H, seed=238)
    print("Toning ground (misty slate imprimatura)...")
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.03)
    print("Underpainting...")
    p.underpainting(ref, stroke_size=52, n_strokes=150)
    print("Block-in...")
    p.block_in(ref, stroke_size=34, n_strokes=280)
    print("Block-in (tighter)...")
    p.block_in(ref, stroke_size=20, n_strokes=360)
    print("Build form...")
    p.build_form(ref, stroke_size=11, n_strokes=480)
    print("Build form (fine)...")
    p.build_form(ref, stroke_size=5, n_strokes=360)
    print("Place lights...")
    p.place_lights(ref, stroke_size=3, n_strokes=260)
    print("Feininger Crystalline Prism (149th mode)...")
    p.feininger_crystalline_prism_pass(
        facet_sigma=9.0,
        prism_cycles=3.0,
        chroma_tilt=0.11,
        lum_facet=0.065,
        opacity=0.74,
    )
    print("Paint Split Toning (session 238 improvement)...")
    p.paint_split_toning_pass(
        shadow_cool=0.060,
        highlight_warm=0.050,
        shadow_pivot=0.28,
        highlight_pivot=0.74,
        transition_width=0.16,
        opacity=0.50,
    )
    print("Diffuse boundary...")
    p.diffuse_boundary_pass(low_grad=0.04, high_grad=0.20,
                            sigma=0.7, strength=0.35, opacity=0.42)
    print("Glaze (misty cobalt wash)...")
    p.glaze((0.08, 0.10, 0.22), opacity=0.04)
    print("Vignette...")
    p.canvas.vignette(strength=0.44)
    p.canvas.save(out_path)
    print(f"  Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint()
    print("Done:", result)
