"""paint_s229.py -- Session 229: The Fox Kit at the Forest Edge (Redon Luminous Reverie)."""
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
    rng = np.random.RandomState(229)

    # ── Background: deep twilight forest interior ──
    # Sky glow behind treeline -- violet to indigo gradient from top
    for y in range(H):
        for x in range(W):
            yt = y / H
            xt = x / W
            # Twilight gradient: pale violet at top, deep indigo at mid, dark at bottom
            sky_t = max(0.0, 1.0 - yt * 1.8)
            ground_t = max(0.0, yt - 0.55) / 0.45
            sky_col = _blend(
                np.array([0.38, 0.28, 0.62], dtype=np.float32),
                [0.68, 0.52, 0.82], sky_t * 0.7)
            ref[y, x] = _blend(sky_col, [0.08, 0.06, 0.12], ground_t * 0.85)

    # ── Background forest: dark tree trunks, left and right ──
    # Left tree cluster
    for tx in [int(W * 0.04), int(W * 0.12), int(W * 0.20)]:
        tw = int(W * 0.018 + rng.uniform(0, W * 0.008))
        for y in range(int(H * 0.05), H):
            for x in range(max(0, tx - tw), min(W, tx + tw)):
                depth = (y - H * 0.05) / (H * 0.95)
                bark = np.array([0.06, 0.04, 0.08], dtype=np.float32)
                ref[y, x] = _blend(ref[y, x], bark, 0.88 + depth * 0.08)

    # Right tree cluster
    for tx in [int(W * 0.82), int(W * 0.88), int(W * 0.95)]:
        tw = int(W * 0.016 + rng.uniform(0, W * 0.008))
        for y in range(int(H * 0.08), H):
            for x in range(max(0, tx - tw), min(W, tx + tw)):
                depth = (y - H * 0.08) / (H * 0.92)
                bark = np.array([0.05, 0.04, 0.07], dtype=np.float32)
                ref[y, x] = _blend(ref[y, x], bark, 0.86 + depth * 0.08)

    # ── Forest floor: mossy, damp, deep violet-green ──
    gy = int(H * 0.72)
    for y in range(gy, H):
        for x in range(W):
            td = (y - gy) / max(H - gy, 1)
            # Mossy green floor darkening toward deep forest
            mx = (rng.uniform() * 0.04)
            col = np.array([0.06 + mx, 0.10 + mx * 0.6, 0.06 + mx * 0.3],
                           dtype=np.float32) * (1.0 - td * 0.5)
            ref[y, x] = _blend(ref[y, x], col, 0.92)

    # Forest floor detail: scattered leaves and roots
    for _ in range(120):
        lx = int(rng.uniform(0, W))
        ly = int(rng.uniform(gy + 10, H))
        lr = int(rng.uniform(2, 8))
        lc = [rng.uniform(0.06, 0.18), rng.uniform(0.08, 0.14), rng.uniform(0.04, 0.10)]
        _ellipse(ref, lx, ly, lr, int(lr * 0.5), lc, opacity=rng.uniform(0.4, 0.8))

    # ── Central clearing: luminous violet mist patch ──
    # The forest opens slightly -- distant glowing violet mist
    mx, my = int(W * 0.50), int(H * 0.45)
    for y in range(int(H * 0.25), int(H * 0.65)):
        for x in range(int(W * 0.22), int(W * 0.78)):
            dist = math.sqrt(((x - mx) / (W * 0.28)) ** 2
                             + ((y - my) / (H * 0.20)) ** 2)
            glow = max(0.0, 1.0 - dist) ** 1.6
            mist_col = np.array([0.54, 0.40, 0.76], dtype=np.float32)
            ref[y, x] = _blend(ref[y, x], mist_col, glow * 0.55)

    # ── Luminous wildflowers in foreground: Redon-style phosphorescent blooms ──
    flower_specs = [
        (int(W * 0.18), int(H * 0.62), (0.82, 0.32, 0.68), 14, 10),   # magenta
        (int(W * 0.30), int(H * 0.67), (0.62, 0.30, 0.88), 12, 9),    # deep violet
        (int(W * 0.68), int(H * 0.64), (0.88, 0.52, 0.76), 13, 10),   # rose-pink
        (int(W * 0.78), int(H * 0.70), (0.48, 0.38, 0.92), 11, 8),    # indigo-blue
        (int(W * 0.42), int(H * 0.73), (0.94, 0.72, 0.34), 10, 7),    # amber-gold
        (int(W * 0.58), int(H * 0.76), (0.72, 0.88, 0.52), 9, 7),     # sage-green
    ]
    for fx, fy, fc, frx, fry in flower_specs:
        # Petal outer bloom -- soft haze
        _ellipse(ref, fx, fy, int(frx * 1.8), int(fry * 1.8), fc,
                 opacity=0.22, feather=0.40)
        # Main petal cluster
        _ellipse(ref, fx, fy, frx, fry, fc, opacity=0.88, feather=0.20)
        # Bright centre
        _ellipse(ref, fx, fy, int(frx * 0.35), int(fry * 0.35),
                 [min(1.0, fc[0] * 1.25), min(1.0, fc[1] * 1.15),
                  min(1.0, fc[2] * 0.85)],
                 opacity=0.92, feather=0.30)
        # Tiny white-cream highlight
        _ellipse(ref, fx - int(frx * 0.1), fy - int(fry * 0.15),
                 int(frx * 0.12), int(fry * 0.12),
                 [0.96, 0.92, 0.86], opacity=0.70, feather=0.20)

    # ── Tall grass stems ──
    for _ in range(45):
        gsx = int(rng.uniform(W * 0.05, W * 0.95))
        gsy = int(rng.uniform(H * 0.68, H * 0.85))
        gsh = int(rng.uniform(H * 0.06, H * 0.16))
        gc = [rng.uniform(0.08, 0.20), rng.uniform(0.12, 0.28), rng.uniform(0.06, 0.16)]
        for step in range(gsh):
            sy = gsy - step
            sx = gsx + int(math.sin(step * 0.18 + gsx * 0.1) * 3)
            if 0 <= sy < H and 0 <= sx < W:
                ref[sy, sx] = _blend(ref[sy, sx], gc, 0.72)

    # ── Fox kit: young fox, sitting, looking toward the glowing mist ──
    fox_cx = int(W * 0.48)
    fox_cy = int(H * 0.70)

    # Body -- warm burnt-orange with ochre lit side, dark shadow side
    for y in range(int(H * 0.60), int(H * 0.78)):
        for x in range(int(W * 0.38), int(W * 0.60)):
            bx2 = (x - fox_cx) / (W * 0.10)
            by2 = (y - fox_cy) / (H * 0.09)
            d = bx2 * bx2 + by2 * by2
            if d <= 1.0:
                # Light from forest glow (centre-right, slightly warm)
                lit = max(0.0, -bx2 * 0.5 + 0.4)
                dark = np.array([0.34, 0.14, 0.06], dtype=np.float32)
                bright = np.array([0.88, 0.52, 0.18], dtype=np.float32)
                col = _blend(dark, bright, min(1.0, lit))
                fade = max(0.0, 1.0 - (d - 0.82) / 0.18) if d > 0.82 else 1.0
                ref[y, x] = _blend(ref[y, x], col, fade * 0.94)

    # Chest / underside -- cream-white
    for y in range(int(H * 0.65), int(H * 0.77)):
        for x in range(int(W * 0.42), int(W * 0.54)):
            cbx = (x - fox_cx) / (W * 0.055)
            cby = (y - fox_cy * 1.02) / (H * 0.06)
            cd = cbx * cbx + cby * cby
            if cd <= 1.0:
                fade = max(0.0, 1.0 - (cd - 0.75) / 0.25) if cd > 0.75 else 1.0
                ref[y, x] = _blend(ref[y, x], [0.92, 0.86, 0.76], fade * 0.72)

    # Hind legs/haunches -- sitting pose
    for side in [-1, 1]:
        hx = fox_cx + side * int(W * 0.07)
        hy = int(H * 0.755)
        for dy in range(-int(H * 0.038), int(H * 0.038) + 1):
            for dx in range(-int(W * 0.032), int(W * 0.032) + 1):
                px2, py2 = hx + dx, hy + dy
                if 0 <= px2 < W and 0 <= py2 < H:
                    d2 = (dx / (W * 0.030)) ** 2 + (dy / (H * 0.035)) ** 2
                    if d2 <= 1.0:
                        col = np.array([0.44, 0.18, 0.08], dtype=np.float32)
                        fade2 = max(0.0, 1.0 - (d2 - 0.78) / 0.22) if d2 > 0.78 else 1.0
                        ref[py2, px2] = _blend(ref[py2, px2], col, fade2 * 0.86)

    # Tail -- full and bushy, curled behind/below on right
    tx0, ty0 = fox_cx + int(W * 0.06), int(H * 0.73)
    for t in range(50):
        t_f = t / 49.0
        tang = t_f * 2.2
        tr = int(W * 0.08) * t_f
        tpx = tx0 + int(tr * math.cos(tang + 0.8))
        tpy = ty0 + int(tr * math.sin(tang + 0.8) * 0.7)
        tr_ell = int(W * 0.025 * (1.0 - t_f * 0.35))
        # Tip: white tip for fox tail
        tip_t = max(0.0, t_f - 0.80) / 0.20
        body_col = [0.80, 0.42, 0.12]
        tip_col = [0.92, 0.88, 0.82]
        tc = [body_col[i] * (1 - tip_t) + tip_col[i] * tip_t for i in range(3)]
        _ellipse(ref, tpx, tpy, tr_ell, tr_ell, tc,
                 opacity=0.86 - t_f * 0.18, feather=0.25)

    # Front paws -- small, tucked under body
    for px2 in [fox_cx - int(W * 0.042), fox_cx + int(W * 0.015)]:
        py2 = int(H * 0.778)
        _ellipse(ref, px2, py2, int(W * 0.022), int(H * 0.012),
                 [0.80, 0.38, 0.12], opacity=0.88, feather=0.25)
        _ellipse(ref, px2, py2 + int(H * 0.004), int(W * 0.015), int(H * 0.007),
                 [0.88, 0.52, 0.22], opacity=0.65, feather=0.20)

    # Head -- turned toward clearing glow (slight left profile)
    hx2, hy2 = fox_cx - int(W * 0.018), int(H * 0.555)
    hrx, hry = int(W * 0.066), int(H * 0.072)
    for dy in range(-hry - 4, hry + 4):
        for dx in range(-hrx - 4, hrx + 4):
            px2, py2 = hx2 + dx, hy2 + dy
            if 0 <= px2 < W and 0 <= py2 < H:
                hd = (dx / max(hrx, 1)) ** 2 + (dy / max(hry, 1)) ** 2
                if hd <= 1.08:
                    lit = max(0.0, min(1.0, (-dx / hrx * 0.6 + 0.45)))
                    dark_h = np.array([0.38, 0.14, 0.06], dtype=np.float32)
                    bright_h = np.array([0.86, 0.54, 0.22], dtype=np.float32)
                    col = _blend(dark_h, bright_h, lit)
                    fade = max(0.0, 1.0 - (hd - 0.86) / 0.22) if hd > 0.86 else 1.0
                    ref[py2, px2] = _blend(ref[py2, px2], col, fade * 0.94)

    # Muzzle / snout
    mux, muy = hx2 - int(hrx * 0.55), hy2 + int(hry * 0.16)
    _ellipse(ref, mux, muy, int(hrx * 0.40), int(hry * 0.30),
             [0.84, 0.50, 0.20], opacity=0.90, feather=0.22)
    _ellipse(ref, mux, muy + int(hry * 0.08), int(hrx * 0.22), int(hry * 0.14),
             [0.90, 0.72, 0.52], opacity=0.75, feather=0.22)

    # Nose -- small dark with violet glow from mist
    _ellipse(ref, mux - int(hrx * 0.08), muy - int(hry * 0.04),
             int(hrx * 0.10), int(hry * 0.07),
             [0.18, 0.10, 0.14], opacity=0.92, feather=0.15)

    # Eyes -- large, wide, reflecting the clearing's violet glow
    for ex_off, ey_off in [(-int(hrx * 0.30), -int(hry * 0.12)),
                            (int(hrx * 0.10), -int(hry * 0.14))]:
        ex2, ey2 = hx2 + ex_off, hy2 + ey_off
        # Eye socket -- dark
        _ellipse(ref, ex2, ey2, int(hrx * 0.18), int(hry * 0.13),
                 [0.06, 0.04, 0.08], opacity=0.92, feather=0.15)
        # Iris -- amber-gold with violet reflection (Redon characteristic)
        _ellipse(ref, ex2, ey2, int(hrx * 0.14), int(hry * 0.10),
                 [0.74, 0.52, 0.14], opacity=0.85, feather=0.18)
        # Pupil
        _ellipse(ref, ex2, ey2, int(hrx * 0.06), int(hry * 0.08),
                 [0.04, 0.02, 0.06], opacity=0.96, feather=0.12)
        # Specular highlight -- reflects clearing glow (violet-white)
        _ellipse(ref, ex2 - int(hrx * 0.04), ey2 - int(hry * 0.03),
                 int(hrx * 0.04), int(hry * 0.03),
                 [0.88, 0.82, 0.96], opacity=0.85, feather=0.15)

    # Ears -- upright, alert
    for ear_dx, ear_dy, ear_ang in [(-int(hrx * 0.30), -int(hry * 0.72), -0.3),
                                    (int(hrx * 0.22), -int(hry * 0.68), 0.2)]:
        eax, eay = hx2 + ear_dx, hy2 + ear_dy
        _ellipse(ref, eax, eay, int(hrx * 0.22), int(hry * 0.40),
                 [0.72, 0.30, 0.10], opacity=0.90, feather=0.22)
        _ellipse(ref, eax + int(hrx * 0.02), eay + int(hry * 0.05),
                 int(hrx * 0.10), int(hry * 0.22),
                 [0.90, 0.50, 0.40], opacity=0.70, feather=0.25)

    # Whiskers
    for wdir in [-1, 1]:
        for wi in range(3):
            wx0 = mux - int(hrx * 0.05)
            wy0 = muy - int(hry * 0.04) + wi * int(hry * 0.06) - int(hry * 0.06)
            wlen = int(W * 0.08)
            wend_x = wx0 + wdir * wlen
            wend_y = wy0 + wi * 2 - 2
            for t in range(20):
                t_f = t / 19.0
                wx2 = int(wx0 + t_f * (wend_x - wx0))
                wy2 = int(wy0 + t_f * (wend_y - wy0))
                if 0 <= wx2 < W and 0 <= wy2 < H:
                    ref[wy2, wx2] = _blend(ref[wy2, wx2], [0.88, 0.84, 0.80], 0.65)

    # ── Luminous spore-motes: drifting through clearing like Redon noirs dreamscape ──
    for _ in range(60):
        smx = int(rng.uniform(W * 0.20, W * 0.80))
        smy = int(rng.uniform(H * 0.28, H * 0.65))
        sr = rng.uniform(0.6, 1.0)
        col = [
            rng.uniform(0.60, 0.96),
            rng.uniform(0.50, 0.86),
            rng.uniform(0.72, 0.98)
        ]
        fade = max(0.0, 1.0 - abs(smx / W - 0.50) * 2.5)
        if 0 <= smy < H and 0 <= smx < W:
            ref[smy, smx] = _blend(ref[smy, smx], col, sr * fade * 0.80)

    img = Image.fromarray(
        (np.clip(ref, 0.0, 1.0) * 255).astype(np.uint8), "RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=1.2))
    return img


def paint() -> str:
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s229_redon_fox_kit.png")
    print("Building reference...")
    ref = make_reference()
    print("Initialising Painter...")
    p = Painter(W, H, seed=229)
    print("Toning ground (deep violet imprimatura)...")
    p.tone_ground((0.18, 0.12, 0.28), texture_strength=0.05)
    print("Underpainting...")
    p.underpainting(ref, stroke_size=52, n_strokes=180)
    print("Block-in...")
    p.block_in(ref, stroke_size=34, n_strokes=320)
    print("Block-in (tighter)...")
    p.block_in(ref, stroke_size=20, n_strokes=420)
    print("Build form...")
    p.build_form(ref, stroke_size=11, n_strokes=550)
    print("Build form (fine)...")
    p.build_form(ref, stroke_size=5, n_strokes=420)
    print("Place lights...")
    p.place_lights(ref, stroke_size=3, n_strokes=300)
    print("Redon Luminous Reverie (140th mode)...")
    p.redon_luminous_reverie_pass(
        shadow_thresh=0.32,
        violet_lift=0.07,
        phosphor_boost=0.40,
        dream_sigma=1.6,
        shimmer_thresh=0.80,
        shimmer_str=0.10,
        opacity=0.78,
    )
    print("Impasto Relief (session 229 improvement)...")
    p.impasto_relief_pass(
        light_angle=2.36,
        relief_scale=0.10,
        thickness_gate=0.28,
        relief_sigma=1.0,
        opacity=0.52,
    )
    print("Diffuse boundary...")
    p.diffuse_boundary_pass(low_grad=0.04, high_grad=0.22,
                            sigma=0.8, strength=0.38, opacity=0.48)
    print("Glaze (violet-rose)...")
    p.glaze((0.38, 0.20, 0.52), opacity=0.05)
    print("Vignette...")
    p.canvas.vignette(strength=0.55)
    p.canvas.save(out_path)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint()
    print("Done:", result)
