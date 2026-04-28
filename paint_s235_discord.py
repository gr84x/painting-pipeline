"""
Session 235 painting: 'Fox at the Edge of the Dark Pines'
Nolde Incandescent Surge mode (146th distinct mode).

Subject: A solitary red fox seated motionless on a lichen-crusted granite boulder
at the edge of a North Sea dune meadow, late October at dusk. Low three-quarter
angle, the fox centered and slightly below eye level, gazing directly at the viewer.
The background: silhouetted coastal pines against a turbulent sky torn open at the
horizon with smoldering incandescent amber. The fox's thick winter coat burns
orange-crimson in the Nolde chromatic surge.
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
from PIL import Image

W, H = 520, 720
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "s235_nolde_fox_dark_pines.png")


# ─────────────────────────────────────────────────────────────────────────────
# Reference construction helpers
# ─────────────────────────────────────────────────────────────────────────────

def _clamp(arr):
    return np.clip(arr, 0.0, 1.0)


def _ellipse_mask(img_h, img_w, cy, cx, ry, rx):
    """Return float mask: 1 inside ellipse, 0 outside."""
    yy, xx = np.mgrid[0:img_h, 0:img_w]
    return (((yy - cy) / ry) ** 2 + ((xx - cx) / rx) ** 2 <= 1.0).astype(np.float32)


def _soft_mask(hard_mask, sigma=3.0):
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(hard_mask.astype(np.float32), sigma)


def make_reference():
    """Build float32 RGB reference array (H, W, 3) for the fox scene."""
    rng = np.random.default_rng(235)
    img = np.zeros((H, W, 3), dtype=np.float32)

    # ─────────────────────────────────────────────────────────────────────────
    # Zone 1: Sky (rows 0 → H*0.42)
    # Top: near-black storm-purple → mid: bruised deep violet-purple
    # Bottom band: smoldering amber-orange tear at horizon
    # ─────────────────────────────────────────────────────────────────────────
    sky_bottom = int(H * 0.42)
    amber_band_top = int(H * 0.32)

    for y in range(sky_bottom):
        t = y / sky_bottom
        if y < amber_band_top:
            # upper sky: near-black storm purple at top → bruised violet-purple
            tt = y / amber_band_top
            r = 0.06 + tt * 0.10
            g = 0.04 + tt * 0.04
            b = 0.12 + tt * 0.14
            img[y, :] = [r, g, b]
        else:
            # amber horizon band: bruised purple transitions to incandescent amber
            at = (y - amber_band_top) / (sky_bottom - amber_band_top)
            # left side: deeper orange; right side: more amber-gold
            for x in range(W):
                xt = x / W
                amber_r = 0.68 + at * 0.20 + xt * 0.05
                amber_g = 0.28 + at * 0.22 + xt * 0.08
                amber_b = 0.04 + at * 0.06
                img[y, x] = _clamp(np.array([amber_r, amber_g, amber_b]))

    # Add some subtle cloud streaks in the upper sky
    for _ in range(8):
        cy = rng.integers(10, amber_band_top - 5)
        cx = rng.integers(20, W - 20)
        cw = rng.integers(40, 110)
        for dy in range(-4, 5):
            for dx in range(-cw // 2, cw // 2):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < amber_band_top and 0 <= nx < W:
                    fade = (1.0 - abs(dy) / 5.0) * (1.0 - abs(2 * dx / cw))
                    # darker cloud streak
                    img[ny, nx] = _clamp(img[ny, nx] * (1.0 - fade * 0.25))

    # ─────────────────────────────────────────────────────────────────────────
    # Zone 2: Pine forest silhouette band (rows H*0.28 → H*0.56)
    # Irregular dark jagged treetops against the amber/purple sky
    # ─────────────────────────────────────────────────────────────────────────
    pine_top_base = int(H * 0.30)
    pine_bottom = int(H * 0.56)

    # Build irregular pine-top silhouette line
    pine_line = np.zeros(W, dtype=np.float32)
    # Base pine horizon
    for x in range(W):
        # gentle undulation
        xt = x / W
        base_y = int(H * (0.31 + 0.04 * np.sin(xt * np.pi * 3.5)
                          + 0.02 * np.sin(xt * np.pi * 7.8)))
        pine_line[x] = base_y

    # Add individual pine tree spikes
    n_trees = 24
    tree_x = rng.integers(0, W, n_trees)
    tree_height = rng.integers(int(H * 0.06), int(H * 0.14), n_trees)
    tree_width = rng.integers(14, 36, n_trees)
    for i in range(n_trees):
        tx = tree_x[i]
        th = tree_height[i]
        tw = tree_width[i]
        tip_y = pine_line[min(tx, W-1)] - th
        for dx in range(-tw // 2, tw // 2 + 1):
            nx = tx + dx
            if 0 <= nx < W:
                # taper: width at this height proportional to distance from tip
                half_w_at_base = tw // 2
                half_w_now = int(half_w_at_base * abs(dx) / max(tw // 2, 1))
                notch_y = tip_y + int(th * (abs(dx) / max(tw // 2, 1)) ** 0.7)
                pine_line[nx] = min(pine_line[nx], notch_y)

    # Paint pine silhouettes
    for x in range(W):
        top_y = max(0, int(pine_line[x]))
        for y in range(top_y, pine_bottom):
            t_depth = (y - top_y) / max(pine_bottom - top_y, 1)
            # Near-black at top, very slightly dark forest-green in lower trunk zone
            r = 0.04 + t_depth * 0.03
            g = 0.05 + t_depth * 0.04
            b = 0.05 + t_depth * 0.02
            img[y, x] = [r, g, b]

    # ─────────────────────────────────────────────────────────────────────────
    # Zone 3: Ground / dune meadow (rows H*0.50 → H)
    # Dark olive-ochre ground, rough grass tufts, boulders
    # ─────────────────────────────────────────────────────────────────────────
    ground_top = int(H * 0.50)

    for y in range(ground_top, H):
        t = (y - ground_top) / (H - ground_top)
        for x in range(W):
            xt = x / W
            # Dark umber ground with slight warm ochre tinge
            r = 0.12 + t * 0.05 + rng.uniform(-0.01, 0.01)
            g = 0.09 + t * 0.04 + rng.uniform(-0.008, 0.008)
            b = 0.05 + t * 0.02
            img[y, x] = _clamp(np.array([r, g, b]))

    # Dry grass tufts in foreground
    n_tufts = 180
    tuft_y = rng.integers(int(H * 0.62), H - 4, n_tufts)
    tuft_x = rng.integers(5, W - 5, n_tufts)
    tuft_height = rng.integers(8, 28, n_tufts)
    for i in range(n_tufts):
        ty, tx = tuft_y[i], tuft_x[i]
        th = tuft_height[i]
        # Ochre-yellow grass blade
        r_tuft = rng.uniform(0.38, 0.55)
        g_tuft = rng.uniform(0.28, 0.40)
        b_tuft = rng.uniform(0.04, 0.10)
        for dy in range(th):
            nx = tx + rng.integers(-2, 3)
            ny = ty - dy
            if 0 <= ny < H and 0 <= nx < W:
                fade = 1.0 - dy / th
                img[ny, nx] = _clamp(np.array([r_tuft * fade, g_tuft * fade, b_tuft * fade]))

    # ─────────────────────────────────────────────────────────────────────────
    # Zone 4: Granite boulder (central, y: H*0.48 → H*0.80)
    # Dark grey-brown with lichen patches (pale ochre/white)
    # ─────────────────────────────────────────────────────────────────────────
    boulder_cy = int(H * 0.68)
    boulder_cx = int(W * 0.50)
    boulder_ry = int(H * 0.19)
    boulder_rx = int(W * 0.30)

    boulder_mask = _ellipse_mask(H, W, boulder_cy, boulder_cx, boulder_ry, boulder_rx)

    for y in range(H):
        for x in range(W):
            if boulder_mask[y, x] > 0.5:
                # Granite base: dark grey-brown
                dist_from_top = (y - (boulder_cy - boulder_ry)) / (2 * boulder_ry)
                shadow = 1.0 - 0.35 * (dist_from_top ** 0.5)
                r = (0.22 + rng.uniform(-0.02, 0.02)) * shadow
                g = (0.20 + rng.uniform(-0.02, 0.02)) * shadow
                b = (0.18 + rng.uniform(-0.02, 0.02)) * shadow
                img[y, x] = _clamp(np.array([r, g, b]))

    # Lichen patches on boulder (pale ochre/ivory)
    n_lichen = 55
    for _ in range(n_lichen):
        ly = rng.integers(boulder_cy - boulder_ry + 5, boulder_cy + int(boulder_ry * 0.6))
        lx = rng.integers(boulder_cx - boulder_rx + 10, boulder_cx + boulder_rx - 10)
        if boulder_mask[ly, lx] > 0.5:
            lr = int(rng.integers(3, 9))
            r_lic = rng.uniform(0.52, 0.72)
            g_lic = rng.uniform(0.48, 0.65)
            b_lic = rng.uniform(0.25, 0.38)
            for dy in range(-lr, lr + 1):
                for dx in range(-lr, lr + 1):
                    ny, nx = ly + dy, lx + dx
                    if (dy**2 + dx**2) <= lr**2 and 0 <= ny < H and 0 <= nx < W:
                        if boulder_mask[ny, nx] > 0.4:
                            fade = 1.0 - (dy**2 + dx**2) / (lr**2 + 0.1)
                            img[ny, nx] = _clamp(img[ny, nx] * (1 - fade * 0.6)
                                                 + np.array([r_lic, g_lic, b_lic]) * fade * 0.6)

    # ─────────────────────────────────────────────────────────────────────────
    # Zone 5: The Fox (y: H*0.16 → H*0.72, centered)
    # Thick orange-crimson winter coat, white chest, amber eyes, black ear tips
    # ─────────────────────────────────────────────────────────────────────────
    fox_cy = int(H * 0.44)   # body center
    fox_cx = int(W * 0.50)

    # Fox body: large oval
    body_ry = int(H * 0.18)
    body_rx = int(W * 0.18)
    body_mask = _ellipse_mask(H, W, fox_cy, fox_cx, body_ry, body_rx)

    # Fox head: slightly smaller oval, above body
    head_cy = int(H * 0.24)
    head_cx = int(W * 0.50)
    head_ry = int(H * 0.09)
    head_rx = int(W * 0.10)
    head_mask = _ellipse_mask(H, W, head_cy, head_cx, head_ry, head_rx)

    # Fox neck: connects head to body
    neck_cy = int(H * 0.335)
    neck_cx = int(W * 0.50)
    neck_ry = int(H * 0.07)
    neck_rx = int(W * 0.07)
    neck_mask = _ellipse_mask(H, W, neck_cy, neck_cx, neck_ry, neck_rx)

    # Fox tail: large curved oval, lower right
    tail_cy = int(H * 0.62)
    tail_cx = int(W * 0.62)
    tail_ry = int(H * 0.10)
    tail_rx = int(W * 0.18)
    tail_mask = _ellipse_mask(H, W, tail_cy, tail_cx, tail_ry, tail_rx)

    fox_mask = _clamp(body_mask + head_mask + neck_mask + tail_mask)

    for y in range(H):
        for x in range(W):
            if fox_mask[y, x] > 0.1:
                blend = fox_mask[y, x]
                yt = y / H
                xt = x / W

                # Base fur color: vivid orange-crimson
                # Lit areas (upper, facing viewer): bright orange
                # Shadowed areas (lower, sides): deep crimson-red
                lum_factor = 1.0 - 0.5 * ((yt - 0.3) / 0.4) ** 2
                r_fur = 0.82 + rng.uniform(-0.04, 0.04)
                g_fur = 0.32 + lum_factor * 0.15 + rng.uniform(-0.03, 0.03)
                b_fur = 0.04 + rng.uniform(-0.01, 0.02)

                # Chest patch: creamy white (lower front of body)
                chest_y_thresh = fox_cy + int(body_ry * 0.1)
                chest_x_range = (fox_cx - int(body_rx * 0.35), fox_cx + int(body_rx * 0.35))
                if (y > chest_y_thresh - int(H * 0.02) and
                        chest_x_range[0] < x < chest_x_range[1] and
                        body_mask[y, x] > 0.5):
                    chest_blend = min(1.0, (y - (chest_y_thresh - int(H*0.02))) / (H * 0.05))
                    r_fur = r_fur * (1 - chest_blend * 0.5) + 0.90 * chest_blend * 0.5
                    g_fur = g_fur * (1 - chest_blend * 0.5) + 0.85 * chest_blend * 0.5
                    b_fur = b_fur * (1 - chest_blend * 0.5) + 0.72 * chest_blend * 0.5

                # Tail tip: white
                tail_dist = ((y - tail_cy) ** 2 / tail_ry ** 2
                             + (x - (tail_cx + tail_rx - 10)) ** 2 / (tail_rx * 0.3) ** 2)
                if tail_mask[y, x] > 0.5 and tail_dist < 0.4:
                    white_blend = (0.4 - tail_dist) / 0.4
                    r_fur = r_fur * (1 - white_blend) + 0.88 * white_blend
                    g_fur = g_fur * (1 - white_blend) + 0.84 * white_blend
                    b_fur = b_fur * (1 - white_blend) + 0.78 * white_blend

                fur_color = _clamp(np.array([r_fur, g_fur, b_fur]))
                img[y, x] = _clamp(img[y, x] * (1 - blend) + fur_color * blend)

    # Muzzle: slightly pointed, darker red-brown at nose
    muzzle_cy = int(H * 0.235)
    muzzle_cx = int(W * 0.50)
    muzzle_ry = int(H * 0.038)
    muzzle_rx = int(W * 0.055)
    muzzle_mask = _ellipse_mask(H, W, muzzle_cy, muzzle_cx, muzzle_ry, muzzle_rx)
    for y in range(H):
        for x in range(W):
            if muzzle_mask[y, x] > 0.5:
                blend = muzzle_mask[y, x]
                img[y, x] = _clamp(img[y, x] * (1 - blend * 0.5)
                                   + np.array([0.60, 0.28, 0.06]) * blend * 0.5)

    # Nose: small dark spot
    nose_cy = int(H * 0.218)
    nose_cx = int(W * 0.50)
    for dy in range(-5, 6):
        for dx in range(-7, 8):
            ny, nx = nose_cy + dy, nose_cx + dx
            if 0 <= ny < H and 0 <= nx < W:
                if dy**2 / 25 + dx**2 / 49 < 1.0:
                    img[ny, nx] = np.array([0.10, 0.08, 0.07])

    # Eyes: amber gold with dark pupil
    for eye_cx_offset in [-int(W * 0.045), int(W * 0.045)]:
        eye_cy = int(H * 0.226)
        eye_cx = int(W * 0.50) + eye_cx_offset
        for dy in range(-7, 8):
            for dx in range(-8, 9):
                ny, nx = eye_cy + dy, eye_cx + dx
                if 0 <= ny < H and 0 <= nx < W:
                    dist2 = dy**2 / 49 + dx**2 / 64
                    if dist2 < 1.0:
                        # Amber iris
                        img[ny, nx] = np.array([0.75, 0.52, 0.08])
                    if dist2 < 0.35:
                        # Dark slit pupil
                        img[ny, nx] = np.array([0.08, 0.06, 0.04])
                    if dy == -3 and abs(dx) <= 2:
                        # Highlight catch-light
                        img[ny, nx] = np.array([0.92, 0.90, 0.85])

    # Ears: two upright triangular ear shapes
    for ear_sign in [-1, 1]:
        ear_base_y = int(H * 0.195)
        ear_tip_y = int(H * 0.140)
        ear_cx = int(W * 0.50) + ear_sign * int(W * 0.065)
        ear_w = int(W * 0.045)
        for y in range(ear_tip_y, ear_base_y):
            t_ear = (y - ear_tip_y) / max(ear_base_y - ear_tip_y, 1)
            half_w = int(t_ear * ear_w)
            for dx in range(-half_w, half_w + 1):
                nx = ear_cx + dx
                ny = y
                if 0 <= ny < H and 0 <= nx < W:
                    # Orange fur ear
                    img[ny, nx] = _clamp(np.array([0.78, 0.30, 0.05])
                                         + rng.uniform(-0.02, 0.02, 3).astype(np.float32))
        # Black ear tip
        for y in range(ear_tip_y, ear_tip_y + int((ear_base_y - ear_tip_y) * 0.40)):
            t_ear = (y - ear_tip_y) / max(ear_base_y - ear_tip_y, 1)
            half_w = max(1, int(t_ear * ear_w) - 1)
            for dx in range(-half_w + 1, half_w):
                nx = ear_cx + dx
                if 0 <= y < H and 0 <= nx < W:
                    img[y, nx] = np.array([0.08, 0.06, 0.05])

    # ─────────────────────────────────────────────────────────────────────────
    # Final: smooth/blend with soft gaussian at medium sigma
    # ─────────────────────────────────────────────────────────────────────────
    from scipy.ndimage import gaussian_filter
    for c in range(3):
        img[:, :, c] = gaussian_filter(img[:, :, c], sigma=1.2)

    return _clamp(img)


# ─────────────────────────────────────────────────────────────────────────────
# Painting pipeline
# ─────────────────────────────────────────────────────────────────────────────

def _reinforce_key_elements(p, ref):
    """Directly composite fox and amber horizon at higher fidelity."""
    import cairo
    import numpy as _np

    surface = p.canvas.surface
    orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4)).copy()

    # Convert reference to uint8 BGRA
    ref_bgra = _np.zeros((H, W, 4), dtype=_np.uint8)
    ref_bgra[:, :, 2] = (ref[:, :, 0] * 255).clip(0, 255).astype(_np.uint8)
    ref_bgra[:, :, 1] = (ref[:, :, 1] * 255).clip(0, 255).astype(_np.uint8)
    ref_bgra[:, :, 0] = (ref[:, :, 2] * 255).clip(0, 255).astype(_np.uint8)
    ref_bgra[:, :, 3] = 255

    # Fox zone (rows H*0.12 to H*0.75) — blend reference strongly
    y0 = int(H * 0.12)
    y1 = int(H * 0.75)
    alpha = 0.55
    blend_zone = orig.copy()
    blend_zone[y0:y1] = (orig[y0:y1].astype(_np.float32) * (1 - alpha)
                         + ref_bgra[y0:y1].astype(_np.float32) * alpha).clip(0, 255).astype(_np.uint8)

    # Amber horizon (rows H*0.30 to H*0.44) — push vivid amber strongly
    y0h = int(H * 0.30)
    y1h = int(H * 0.44)
    alpha_h = 0.70
    blend_zone[y0h:y1h] = (blend_zone[y0h:y1h].astype(_np.float32) * (1 - alpha_h)
                            + ref_bgra[y0h:y1h].astype(_np.float32) * alpha_h).clip(0, 255).astype(_np.uint8)

    surface.get_data()[:] = blend_zone.tobytes()
    surface.mark_dirty()


def paint():
    from stroke_engine import Painter

    print(f"Painting session 235: Fox at the Edge of the Dark Pines ({W}x{H})")
    ref = make_reference()
    p = Painter(W, H, seed=235)

    # ── Ground: raw umber dark imprimatura ────────────────────────────────────
    p.tone_ground((0.12, 0.06, 0.02), texture_strength=0.04)
    print("  tone_ground done")

    # ── Underpainting from reference ──────────────────────────────────────────
    p.underpainting(ref, stroke_size=60, n_strokes=150)
    print("  underpainting done")

    # ── Block-in layers ───────────────────────────────────────────────────────
    p.block_in(ref, stroke_size=40, n_strokes=300)
    print("  block_in 1 done")
    p.block_in(ref, stroke_size=24, n_strokes=420)
    print("  block_in 2 done")

    # ── Build form ────────────────────────────────────────────────────────────
    p.build_form(ref, stroke_size=12, n_strokes=520)
    print("  build_form 1 done")
    p.build_form(ref, stroke_size=6, n_strokes=400)
    print("  build_form fine done")

    # ── Reinforce fox and horizon key elements ────────────────────────────────
    _reinforce_key_elements(p, ref)
    print("  key elements reinforced")

    # ── Nolde Incandescent Surge pass (146th mode) ────────────────────────────
    p.nolde_incandescent_surge_pass(
        shadow_ceil=0.28,
        shadow_power=1.90,
        shadow_r_push=0.11,
        shadow_b_drop=0.07,
        mid_center=0.50,
        mid_width=0.21,
        surge_boost=0.72,
        bloom_chroma_min=0.20,
        bloom_lum_min=0.35,
        bloom_sigma=3.80,
        bloom_warm_r=0.07,
        bloom_warm_g=0.035,
        bloom_warm_b=0.01,
        opacity=0.86,
    )
    print("  nolde_incandescent_surge_pass done")

    # ── Pigment Granulation pass (improvement) ────────────────────────────────
    p.paint_pigment_granulation_pass(
        coarse_sigma=5.50,
        fine_sigma=1.10,
        coarse_weight=0.58,
        fine_weight=0.42,
        chroma_min=0.08,
        granule_depth=0.06,
        valley_r_push=0.022,
        valley_g_push=0.010,
        opacity=0.48,
    )
    print("  paint_pigment_granulation_pass done")

    # ── Warm-cool contrast: deepen pines, warm fox ────────────────────────────
    p.warm_cool_zone_pass(
        warm_threshold=0.62,
        cool_threshold=0.22,
        warm_r_lift=0.04,
        warm_b_drop=0.03,
        cool_b_lift=0.05,
        cool_r_drop=0.03,
    )
    print("  warm_cool_zone_pass done")

    # ── Chromatic vignette: darken corners to push focus to fox ──────────────
    p.chromatic_vignette_pass()
    print("  chromatic_vignette_pass done")

    # ── Glaze: warm raw umber unifying tint ───────────────────────────────────
    p.glaze((0.12, 0.06, 0.02), opacity=0.05)
    print("  glaze done")

    # ── Vignette: edge darkening ──────────────────────────────────────────────
    p.canvas.vignette(strength=0.42)
    print("  vignette done")

    # ── Save ──────────────────────────────────────────────────────────────────
    p.canvas.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    out = paint()
    img = Image.open(out)
    print(f"Image size: {img.size}, mode: {img.mode}")
    arr = np.array(img)
    print(f"Pixel range: [{arr.min()}, {arr.max()}]")
    print("Done.")
