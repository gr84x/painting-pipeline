"""paint_s233.py -- Session 233: Moonlit Night on the Steppe (Kuindzhi Moonlit Radiance)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter

W, H = 560, 720


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
    rng = np.random.RandomState(233)

    # ── Sky: tiered nocturnal gradient ──
    # Top: near-black → deep indigo → cold grey corona → pale amber at horizon
    horizon_y = int(H * 0.38)   # horizon line
    moon_y    = int(H * 0.28)   # moon position above horizon
    moon_x    = int(W * 0.50)   # centred

    for y in range(H):
        for x in range(W):
            yt = y / H
            xt = x / W

            # Sky zone (above horizon)
            if y < horizon_y:
                sky_t = y / max(horizon_y, 1)          # 0 at top, 1 at horizon
                # Base sky gradient: near-black → deep indigo → pale near horizon
                if sky_t < 0.30:
                    sky_col = np.array([0.03, 0.03, 0.10], dtype=np.float32)
                elif sky_t < 0.60:
                    t = (sky_t - 0.30) / 0.30
                    sky_col = _blend(
                        np.array([0.03, 0.03, 0.10], dtype=np.float32),
                        [0.06, 0.08, 0.22], t)
                else:
                    t = (sky_t - 0.60) / 0.40
                    sky_col = _blend(
                        np.array([0.06, 0.08, 0.22], dtype=np.float32),
                        [0.24, 0.26, 0.34], t)
                ref[y, x] = sky_col

            # Earth/water zone (below horizon)
            else:
                # Base: near-black with slight blue tint for water
                depth = (y - horizon_y) / max(H - horizon_y, 1)
                base = np.array([0.04, 0.04, 0.08], dtype=np.float32)
                ref[y, x] = _blend(base, [0.02, 0.02, 0.05], depth * 0.5)

    # ── Moon: incandescent cold disc ──
    moon_radius = int(W * 0.038)
    # Moon corona / halo (several layers from outside in)
    for r_mult, bright, alpha in [
        (5.5, [0.22, 0.24, 0.28], 0.30),
        (3.8, [0.38, 0.40, 0.46], 0.45),
        (2.4, [0.62, 0.64, 0.66], 0.55),
        (1.5, [0.78, 0.80, 0.78], 0.70),
        (1.0, [0.94, 0.95, 0.88], 1.00),  # bright disc core
    ]:
        _ellipse(ref, moon_x, moon_y,
                 int(moon_radius * r_mult), int(moon_radius * r_mult),
                 bright, opacity=alpha, feather=0.45 if r_mult > 1.5 else 0.18)

    # Moon disc: cold cream-white centre with very slight warm core
    _ellipse(ref, moon_x, moon_y,
             int(moon_radius * 0.6), int(moon_radius * 0.6),
             [0.98, 0.97, 0.90], opacity=1.0, feather=0.12)

    # Atmospheric glow near horizon around the moon
    for y in range(max(0, moon_y - int(H * 0.14)), min(H, moon_y + int(H * 0.12))):
        for x in range(W):
            dist_x = abs(x - moon_x) / (W * 0.45)
            dist_y = abs(y - moon_y) / (H * 0.13)
            glow = max(0.0, 1.0 - dist_x - dist_y * 0.5) ** 1.8
            if glow > 0.02:
                ref[y, x] = _blend(ref[y, x], [0.26, 0.28, 0.32], glow * 0.55)

    # ── Stars: scattered faint points in upper sky ──
    for _ in range(80):
        sx = int(rng.uniform(0, W))
        sy = int(rng.uniform(0, int(H * 0.30)))
        sr = rng.uniform(0.4, 0.85)
        # Avoid area near moon
        if abs(sx - moon_x) < int(W * 0.20) and abs(sy - moon_y) < int(H * 0.15):
            continue
        star_lum = rng.uniform(0.40, 0.75)
        if 0 <= sy < H and 0 <= sx < W:
            ref[sy, sx] = _blend(ref[sy, sx],
                                 [star_lum * 0.90, star_lum * 0.92, star_lum * 1.0],
                                 sr * 0.80)

    # ── Distant far bank: flat near-black ribbon ──
    bank_y = horizon_y
    bank_h = int(H * 0.035)
    for y in range(bank_y, min(H, bank_y + bank_h)):
        for x in range(W):
            # Very slight undulation for organic silhouette
            wave = int(math.sin(x * 0.05) * 2 + math.sin(x * 0.12) * 1)
            if y > bank_y + wave:
                ref[y, x] = _blend(ref[y, x], [0.04, 0.04, 0.07], 0.95)

    # ── River surface: obsidian black with vertical moon reflection streak ──
    water_y = bank_y + bank_h
    for y in range(water_y, H):
        for x in range(W):
            # Base water: near-black deep
            ref[y, x] = np.array([0.04, 0.04, 0.08], dtype=np.float32)

    # Moon reflection on water: vertical column of cold silver-yellow
    refl_cx = moon_x
    refl_width = int(W * 0.055)
    for y in range(water_y, H):
        depth_t = (y - water_y) / max(H - water_y, 1)
        for dx in range(-refl_width * 2, refl_width * 2 + 1):
            rx2 = refl_cx + dx
            if 0 <= rx2 < W:
                # Core streak with oscillation (water ripples)
                ripple = math.sin(y * 0.22 + abs(dx) * 0.4) * int(W * 0.006)
                eff_dx = abs(dx + ripple)
                streak_gate = max(0.0, 1.0 - eff_dx / (refl_width + 1e-6)) ** 1.8
                # Fade with depth
                depth_fade = max(0.0, 1.0 - depth_t * 0.80)
                streak_lum = streak_gate * depth_fade
                if streak_lum > 0.01:
                    refl_col = [0.82 * streak_lum, 0.85 * streak_lum, 0.72 * streak_lum]
                    ref[y, rx2] = _blend(ref[y, rx2], refl_col, min(1.0, streak_lum * 1.2))

    # Subtle water shimmer (faint horizontal ripple lines)
    for _ in range(35):
        wy = int(rng.uniform(water_y + 10, H - 5))
        wlen = int(rng.uniform(W * 0.04, W * 0.14))
        wx = int(rng.uniform(0, W - wlen))
        w_lum = rng.uniform(0.06, 0.14)
        for i in range(wlen):
            if 0 <= wx + i < W:
                ref[wy, wx + i] = _blend(ref[wy, wx + i],
                                          [w_lum * 0.82, w_lum * 0.88, w_lum],
                                          0.55)

    # ── Foreground bank (near viewer): dark earth, dried grass, reeds ──
    fg_y = int(H * 0.82)
    for y in range(fg_y, H):
        for x in range(W):
            depth = (y - fg_y) / max(H - fg_y, 1)
            ref[y, x] = _blend(np.array([0.06, 0.05, 0.08], dtype=np.float32),
                                [0.03, 0.02, 0.04], depth * 0.6)

    # Dried grass: thin vertical stems at foreground bank
    for _ in range(90):
        gx = int(rng.uniform(0, W))
        gy = int(rng.uniform(fg_y, H - 8))
        gh = int(rng.uniform(int(H * 0.03), int(H * 0.09)))
        g_lum = rng.uniform(0.08, 0.20)
        # Vary color: some cool (near moon side) some warm
        g_col = [g_lum * 0.82, g_lum * 0.88, g_lum * (0.90 if gx > W//2 else 0.78)]
        for step in range(gh):
            sy = gy - step
            sx = gx + int(math.sin(step * 0.22 + gx * 0.08) * 1.5)
            if 0 <= sy < H and 0 <= sx < W:
                ref[sy, sx] = _blend(ref[sy, sx], g_col, 0.75)

    # Reeds: taller, at waterline
    for _ in range(25):
        rx2 = int(rng.uniform(int(W * 0.05), int(W * 0.95)))
        ry = int(rng.uniform(fg_y - int(H * 0.04), fg_y + int(H * 0.02)))
        rh = int(rng.uniform(int(H * 0.06), int(H * 0.14)))
        r_col = [0.06, 0.06, 0.08]
        for step in range(rh):
            sy = ry - step
            sx = rx2 + int(math.sin(step * 0.15 + rx2 * 0.05) * 2)
            if 0 <= sy < H and 0 <= sx < W:
                ref[sy, sx] = _blend(ref[sy, sx], r_col, 0.88)
        # Reed head: small dark oval at top
        _ellipse(ref, sx, sy,
                 int(W * 0.006), int(H * 0.012),
                 [0.08, 0.06, 0.07], opacity=0.90, feather=0.20)

    # ── Birch tree: right-centre, moonlit right side, dark left ──
    birch_x = int(W * 0.58)
    birch_bot = int(H * 0.84)
    birch_top = int(H * 0.04)
    trunk_w_max = int(W * 0.022)

    # Trunk: tapers from wide base to narrow crown
    for y in range(birch_top, birch_bot):
        trunk_t = (y - birch_top) / max(birch_bot - birch_top, 1)  # 0=top 1=bot
        tw = max(2, int(trunk_w_max * (0.25 + trunk_t * 0.75)))
        # Slight lean right as it goes up
        cx2 = birch_x + int((1.0 - trunk_t) * int(W * 0.018))
        for dx in range(-tw, tw + 1):
            px = cx2 + dx
            if 0 <= px < W:
                # Moonlight from left side of canvas (moon is centre), so right-trunk lit
                lit_side = dx / max(tw, 1)  # -1=left shadow, +1=right
                bark_bright = max(0.0, min(1.0, 0.38 + lit_side * 0.55))
                # Birch bark: pale cream where lit, dark charcoal where shadowed
                r_v = 0.72 * bark_bright + 0.06 * (1 - bark_bright)
                g_v = 0.74 * bark_bright + 0.05 * (1 - bark_bright)
                b_v = 0.68 * bark_bright + 0.10 * (1 - bark_bright)
                # Bark markings: dark horizontal lenticels
                lenticel = (math.sin(y * 0.55 + cx2 * 0.12) > 0.70)
                if lenticel:
                    r_v *= 0.45; g_v *= 0.45; b_v *= 0.42
                ref[y, px] = np.array([r_v, g_v, b_v], dtype=np.float32)

    # Major branches: three radiating upward-left from upper trunk
    branch_specs = [
        # (start_y_frac, end_dx_frac, end_dy_frac, width)
        (0.18, -0.18,  -0.10, 3),   # highest branch, sweeps far left
        (0.26, -0.12,  -0.08, 4),   # mid branch
        (0.35,  0.08,  -0.06, 3),   # lower branch, slight right
    ]
    for (sy_frac, edx_frac, edy_frac, bw) in branch_specs:
        bsy = int(birch_top + (birch_bot - birch_top) * sy_frac)
        bex = birch_x + int(edx_frac * W)
        bey = bsy + int(edy_frac * H)
        steps = 60
        for i in range(steps):
            t = i / steps
            bpx = int(birch_x + t * (bex - birch_x))
            bpy = int(bsy + t * (bey - bsy))
            for dbw in range(-bw, bw + 1):
                ppx = bpx + dbw
                if 0 <= ppx < W and 0 <= bpy < H:
                    # Branches are silhouette dark (some slight blue sky reflected)
                    branch_col = [0.06, 0.06, 0.10]
                    ref[bpy, ppx] = _blend(ref[bpy, ppx], branch_col, 0.92)
            # Fine sub-branches
            if i > 35 and i % 6 == 0:
                for sub in range(2):
                    sdir = (sub - 0.5) * 2
                    for si in range(18):
                        st2 = si / 17.0
                        spx = bpx + int(sdir * st2 * int(W * 0.055))
                        spy = bpy - int(st2 * int(H * 0.028))
                        if 0 <= spx < W and 0 <= spy < H:
                            ref[spy, spx] = _blend(ref[spy, spx], [0.05, 0.05, 0.09], 0.88)

    img = Image.fromarray(
        (np.clip(ref, 0.0, 1.0) * 255).astype(np.uint8), "RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    return img


def paint() -> str:
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s233_kuindzhi_moonlit_steppe.png")
    print("Building reference...")
    ref = make_reference()
    print("Initialising Painter...")
    p = Painter(W, H, seed=233)
    print("Toning ground (near-black nocturnal imprimatura)...")
    p.tone_ground((0.06, 0.06, 0.14), texture_strength=0.03)
    print("Underpainting...")
    p.underpainting(ref, stroke_size=58, n_strokes=160)
    print("Block-in...")
    p.block_in(ref, stroke_size=38, n_strokes=280)
    print("Block-in (tighter)...")
    p.block_in(ref, stroke_size=22, n_strokes=380)
    print("Build form...")
    p.build_form(ref, stroke_size=12, n_strokes=480)
    print("Build form (fine)...")
    p.build_form(ref, stroke_size=6, n_strokes=380)
    print("Place lights...")
    p.place_lights(ref, stroke_size=3, n_strokes=260)
    print("Kuindzhi Moonlit Radiance (144th mode)...")
    p.kuindzhi_moonlit_radiance_pass(
        halo_sigma=18.0,
        halo_strength=0.22,
        velvet_power=2.40,
        velvet_threshold=0.30,
        moon_cold_b_shift=0.12,
        moon_cold_r_drop=0.07,
        moon_threshold=0.65,
        shadow_b_push=0.07,
        shadow_threshold=0.20,
        streak_width=0.062,
        streak_strength=0.16,
        opacity=0.90,
    )
    print("Paint Gravity Drift (session 233 improvement)...")
    p.paint_gravity_drift_pass(
        drift_sigma_down=3.8,
        drift_sigma_up=0.7,
        thick_threshold=0.32,
        thick_power=1.50,
        drift_strength=0.50,
        opacity=0.55,
    )
    print("Diffuse boundary...")
    p.diffuse_boundary_pass(low_grad=0.03, high_grad=0.20,
                            sigma=0.7, strength=0.32, opacity=0.42)
    print("Glaze (cold indigo)...")
    p.glaze((0.12, 0.14, 0.28), opacity=0.04)
    print("Vignette...")
    p.canvas.vignette(strength=0.65)
    p.canvas.save(out_path)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint()
    print("Done:", result)
