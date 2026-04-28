"""paint_s228.py — Session 228: The Blacksmith at the Apex (Boccioni Futurist style)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter

W, H = 520, 720


def _blend(arr, col, strength):
    return arr * (1 - strength) + np.array(col, dtype=np.float32) * strength


def _ellipse(arr, cx, cy, rx, ry, color, opacity=1.0, feather=0.08):
    """Paint a soft ellipse onto arr (float32 H×W×3)."""
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

    # ── Background: stone wall — cool dark grey, faintly warm upper-left ──
    for y in range(H):
        for x in range(W):
            wall = np.array([0.16, 0.13, 0.11], dtype=np.float32)
            # Warm upper-left (residual ambient light from exterior)
            warm = max(0.0, 1.0 - math.sqrt((x / W) ** 2 + (y / H) ** 2) * 1.6)
            ref[y, x] = _blend(wall, [0.26, 0.21, 0.15], warm * 0.25)

    # ── Stone floor — darker, faint checker pattern ──
    fy = int(H * 0.68)
    for y in range(fy, H):
        for x in range(W):
            tx = (x // 40) % 2
            ty = ((y - fy) // 40) % 2
            col = [0.11, 0.09, 0.08] if (tx + ty) % 2 == 0 else [0.08, 0.07, 0.06]
            depth = (y - fy) / max(H - fy, 1)
            ref[y, x] = np.array(col, dtype=np.float32) * (1.0 - depth * 0.30)

    # ── Forge glow — right side, orange-red bloom ──
    fx, fy2 = int(W * 0.88), int(H * 0.62)
    for y in range(H):
        for x in range(W):
            dist = math.sqrt(((x - fx) / (W * 0.38)) ** 2 + ((y - fy2) / (H * 0.28)) ** 2)
            forge_glow = max(0.0, 1.0 - dist)
            if forge_glow > 0:
                forge_col = np.array([0.90, 0.42, 0.08], dtype=np.float32)
                ref[y, x] = _blend(ref[y, x], forge_col, forge_glow ** 1.8 * 0.65)

    # ── Forge opening — bright orange-white hot coals ──
    _ellipse(ref, int(W * 0.87), int(H * 0.62), int(W * 0.065), int(H * 0.048),
             [0.96, 0.72, 0.28], opacity=0.95)
    _ellipse(ref, int(W * 0.87), int(H * 0.62), int(W * 0.032), int(H * 0.024),
             [1.0, 0.94, 0.78], opacity=0.90)

    # ── Anvil — dark iron silhouette, center-lower ──
    anx, any2 = int(W * 0.46), int(H * 0.70)
    # Anvil base
    for y in range(int(H * 0.70), int(H * 0.80)):
        for x in range(int(W * 0.30), int(W * 0.64)):
            t = (y - H * 0.70) / (H * 0.10)
            col = np.array([0.14, 0.12, 0.10], dtype=np.float32) * (1.0 - t * 0.3)
            ref[y, x] = _blend(ref[y, x], col, 0.92)
    # Anvil top face — lit by forge glow from right
    for y in range(int(H * 0.655), int(H * 0.70)):
        for x in range(int(W * 0.28), int(W * 0.66)):
            # Light from right
            lit = max(0.0, (x / W - 0.28) / 0.38)
            col = _blend(np.array([0.20, 0.16, 0.12], dtype=np.float32),
                         [0.48, 0.28, 0.10], lit * 0.55)
            ref[y, x] = _blend(ref[y, x], col, 0.92)
    # Anvil horn (right protrusion)
    for y in range(int(H * 0.655), int(H * 0.68)):
        for x in range(int(W * 0.64), int(W * 0.72)):
            taper = 1.0 - (x - W * 0.64) / (W * 0.08)
            if taper > 0:
                ref[y, x] = _blend(ref[y, x], [0.22, 0.18, 0.13], taper * 0.88)

    # ── Hot iron on anvil — glowing orange-white ──
    hix, hiy = int(W * 0.44), int(H * 0.655)
    _ellipse(ref, hix, hiy, int(W * 0.055), int(H * 0.018),
             [0.96, 0.62, 0.14], opacity=0.90)
    _ellipse(ref, hix, hiy, int(W * 0.028), int(H * 0.010),
             [1.0, 0.90, 0.55], opacity=0.85)

    # ── Blacksmith figure: leather apron + torso ──
    # Apron — dark leather, ochre-lit from forge
    bx, by_ap = int(W * 0.44), int(H * 0.52)
    for y in range(int(H * 0.46), int(H * 0.70)):
        hw = int(W * 0.115 * (1.0 + (y / H - 0.46) * 0.20))
        for x in range(max(0, bx - hw), min(W, bx + hw)):
            side = (x - bx) / max(hw, 1)
            # Forge light from right side
            lit = max(0.0, side * 0.6 + 0.3)
            ap_dark = np.array([0.20, 0.14, 0.08], dtype=np.float32)
            ap_lit  = np.array([0.44, 0.26, 0.10], dtype=np.float32)
            col = _blend(ap_dark, ap_lit, lit)
            aw  = max(0.0, 1.0 - abs(side) ** 1.4)
            ref[y, x] = _blend(ref[y, x], col, aw * 0.92)

    # Shirt — rolled sleeves, dull linen
    for y in range(int(H * 0.30), int(H * 0.48)):
        hw = int(W * 0.13)
        for x in range(max(0, bx - hw), min(W, bx + hw)):
            side = (x - bx) / max(hw, 1)
            lit = max(0.0, side * 0.4 + 0.35)
            sh_d = np.array([0.25, 0.20, 0.14], dtype=np.float32)
            sh_l = np.array([0.56, 0.46, 0.34], dtype=np.float32)
            col = _blend(sh_d, sh_l, lit)
            aw  = max(0.0, 1.0 - abs(side) ** 1.6)
            ref[y, x] = _blend(ref[y, x], col, aw * 0.90)

    # Left arm (lower, resting on anvil area)
    lax, lay = int(W * 0.34), int(H * 0.62)
    for t in range(20):
        t_f = t / 19.0
        ax2 = int(lax + t_f * W * 0.06)
        ay2 = int(lay - t_f * H * 0.06)
        _ellipse(ref, ax2, ay2, int(W * 0.028), int(H * 0.028),
                 [0.40, 0.26, 0.14], opacity=0.82)

    # Right arm — RAISED, hammer overhead (Futurist kinetic focus)
    # Upper arm: bx-ish up to the right
    rax0, ray0 = int(W * 0.50), int(H * 0.38)
    rax1, ray1 = int(W * 0.54), int(H * 0.18)
    for t in range(30):
        t_f = t / 29.0
        ax2 = int(rax0 + t_f * (rax1 - rax0))
        ay2 = int(ray0 + t_f * (ray1 - ray0))
        r_arm = int(W * 0.030 * (1.0 - t_f * 0.20))
        lit = max(0.0, t_f * 0.6 + 0.25)
        col = _blend(np.array([0.35, 0.22, 0.12], dtype=np.float32),
                     [0.72, 0.50, 0.28], lit)
        _ellipse(ref, ax2, ay2, r_arm, r_arm, col, opacity=0.88)

    # Forearm continues — wrist to hammer grip
    for t in range(20):
        t_f = t / 19.0
        ax2 = int(rax1 + t_f * (W * 0.04))
        ay2 = int(ray1 + t_f * (H * 0.04))
        _ellipse(ref, ax2, ay2, int(W * 0.022), int(W * 0.022),
                 [0.44, 0.28, 0.14], opacity=0.85)

    # ── Hammer — iron head, wooden handle ──
    # Handle: diagonal from grip down-left
    hx0, hy0 = int(W * 0.58), int(H * 0.13)   # head end
    hx1, hy1 = int(W * 0.54), int(H * 0.22)   # grip end
    for t in range(25):
        t_f = t / 24.0
        hpx = int(hx1 + t_f * (hx0 - hx1))
        hpy = int(hy1 + t_f * (hy0 - hy1))
        _ellipse(ref, hpx, hpy, int(W * 0.012), int(W * 0.012),
                 [0.42, 0.30, 0.16], opacity=0.90)
    # Hammer head — iron rectangle, wide
    hmx, hmy = int(W * 0.60), int(H * 0.105)
    for y in range(int(H * 0.075), int(H * 0.136)):
        for x in range(int(W * 0.545), int(W * 0.660)):
            # Lit on top, dark below; forge-orange on right face
            lit_top = max(0.0, 1.0 - (y - H * 0.075) / (H * 0.06) * 0.8)
            lit_right = max(0.0, (x - W * 0.545) / (W * 0.115))
            base = np.array([0.30, 0.27, 0.25], dtype=np.float32)
            col = _blend(base, [0.88, 0.68, 0.28], lit_right * 0.45)
            col = _blend(col, [0.65, 0.62, 0.60], lit_top * 0.30)
            ref[y, x] = _blend(ref[y, x], col, 0.94)

    # ── Head / neck ──
    sk_l = np.array([0.62, 0.42, 0.25], dtype=np.float32)
    sk_s = np.array([0.28, 0.17, 0.09], dtype=np.float32)
    nkx, nky = int(W * 0.44), int(H * 0.295)
    # Neck
    for y in range(int(H * 0.29), int(H * 0.32)):
        for x in range(nkx - int(W * 0.032), nkx + int(W * 0.032)):
            if 0 <= x < W:
                side = max(0.0, (x - nkx) / (W * 0.032))
                ref[y, x] = _blend(ref[y, x], _blend(sk_l, sk_s, side * 0.7), 0.90)
    # Head
    fax, fay = int(W * 0.44), int(H * 0.235)
    frx, fry = int(W * 0.075), int(H * 0.095)
    for y in range(fay - fry - 4, fay + fry + 4):
        for x in range(fax - frx - 4, fax + frx + 4):
            if 0 <= y < H and 0 <= x < W:
                dx2 = (x - fax) / max(frx, 1)
                dy2 = (y - fay) / max(fry, 1)
                d = dx2 * dx2 + dy2 * dy2
                if d <= 1.08:
                    lit = max(0.0, min(1.0, (dx2 * 0.5 - dy2 * 0.3) * 1.2 + 0.4))
                    col = _blend(sk_s, sk_l, lit)
                    fade = max(0.0, 1.0 - (d - 0.88) / 0.20) if d > 0.88 else 1.0
                    ref[y, x] = _blend(ref[y, x], col, fade * 0.94)
    # Short dark hair
    hair_c = np.array([0.10, 0.07, 0.04], dtype=np.float32)
    for y in range(fay - fry - 3, fay - int(fry * 0.1)):
        for x in range(fax - frx - int(W * 0.02), fax + frx + int(W * 0.02)):
            if 0 <= y < H and 0 <= x < W:
                fdx = (x - fax) / max(frx, 1)
                fdy = (y - fay) / max(fry, 1)
                fd  = fdx * fdx + fdy * fdy
                od  = ((x - fax) / (frx + W * 0.022)) ** 2 + ((y - fay) / (fry + W * 0.008)) ** 2
                if od <= 1.04 and fd >= 0.80:
                    ref[y, x] = hair_c
    # Eyes
    for ex in [fax - int(frx * 0.36), fax + int(frx * 0.18)]:
        ey2 = fay - int(fry * 0.04)
        for dy in range(-int(fry * 0.065), int(fry * 0.065) + 1):
            for dx in range(-int(frx * 0.14), int(frx * 0.14) + 1):
                px2, py2 = ex + dx, ey2 + dy
                if 0 <= px2 < W and 0 <= py2 < H:
                    de = (dx / max(frx * 0.13, 1)) ** 2 + (dy / max(fry * 0.058, 1)) ** 2
                    if de <= 1.0:
                        ref[py2, px2] = _blend(ref[py2, px2], [0.06, 0.04, 0.02],
                                               max(0, 1.0 - de * 0.5))

    # ── Hanging tools silhouetted on back wall ──
    # Tongs shape at upper-left
    for y in range(int(H * 0.10), int(H * 0.36)):
        for x in range(int(W * 0.06), int(W * 0.10)):
            if (x - W * 0.08) ** 2 < (W * 0.012) ** 2:
                ref[y, x] = _blend(ref[y, x], [0.07, 0.06, 0.05], 0.85)
    # Hammer silhouette at upper
    for y in range(int(H * 0.08), int(H * 0.15)):
        for x in range(int(W * 0.14), int(W * 0.22)):
            ref[y, x] = _blend(ref[y, x], [0.07, 0.06, 0.05], 0.75)

    # ── Spark scatter — tiny bright flecks near hot iron ──
    rng = np.random.RandomState(228)
    for _ in range(120):
        sx = int(rng.uniform(W * 0.25, W * 0.65))
        sy = int(rng.uniform(H * 0.55, H * 0.70))
        br = rng.uniform(0.70, 1.0)
        if 0 <= sy < H and 0 <= sx < W:
            ref[sy, sx] = [br, br * 0.72, br * 0.22]
    # Sparks flying up from hammer strike zone
    for _ in range(80):
        sx = int(rng.uniform(W * 0.35, W * 0.62))
        sy = int(rng.uniform(H * 0.28, H * 0.60))
        br = rng.uniform(0.65, 1.0) * max(0.0, 1.0 - (sy / H - 0.28) / 0.32)
        if br > 0.2 and 0 <= sy < H and 0 <= sx < W:
            ref[sy, sx] = [br * 0.95, br * 0.66, br * 0.18]

    # ── Smoke wisps at upper area ──
    for _ in range(40):
        smx = int(rng.uniform(W * 0.30, W * 0.70))
        smy = int(rng.uniform(0, int(H * 0.18)))
        ref[smy, smx] = _blend(ref[smy, smx], [0.22, 0.20, 0.18], rng.uniform(0.15, 0.35))

    img = Image.fromarray(
        (np.clip(ref, 0.0, 1.0) * 255).astype(np.uint8), "RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=1.8))
    return img


def paint() -> str:
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s228_boccioni_blacksmith.png")
    print("Building reference…")
    ref = make_reference()
    print("Initialising Painter…")
    p = Painter(W, H, seed=228)
    print("Toning ground…")
    p.tone_ground((0.18, 0.14, 0.08), texture_strength=0.06)
    print("Underpainting…")
    p.underpainting(ref, stroke_size=52, n_strokes=180)
    print("Block-in…")
    p.block_in(ref, stroke_size=34, n_strokes=320)
    print("Block-in (tighter)…")
    p.block_in(ref, stroke_size=20, n_strokes=420)
    print("Build form…")
    p.build_form(ref, stroke_size=11, n_strokes=550)
    print("Build form (fine)…")
    p.build_form(ref, stroke_size=5, n_strokes=420)
    print("Place lights…")
    p.place_lights(ref, stroke_size=3, n_strokes=300)
    print("Boccioni Futurist Motion (139th mode)…")
    p.boccioni_futurist_motion_pass(
        contour_thresh=0.030,
        force_strength=0.32,
        smear_distance=7,
        sat_boost=0.25,
        velocity_blur=2.2,
        opacity=0.80,
    )
    print("Chromatic Focal Pull (improvement)…")
    p.chromatic_focal_pull_pass(
        focal_x=0.44,
        focal_y=0.48,
        reach=0.52,
        warm_pull=0.10,
        cool_push=0.07,
        opacity=0.68,
    )
    print("Diffuse boundary…")
    p.diffuse_boundary_pass(low_grad=0.04, high_grad=0.24,
                            sigma=0.9, strength=0.42, opacity=0.50)
    print("Glaze…")
    p.glaze((0.55, 0.28, 0.06), opacity=0.06)
    print("Vignette…")
    p.canvas.vignette(strength=0.50)
    p.canvas.save(out_path)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint()
    print("Done:", result)
