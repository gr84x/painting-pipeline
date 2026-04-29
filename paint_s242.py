"""paint_s242.py -- Session 242: The Lighthouse at Port de Saint-Tropez (Signac Divisionist Mosaic, 153rd mode)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
from stroke_engine import Painter

W, H = 520, 680

# ── Palette (Signac-inspired: pure complementary pairs, Mediterranean vibrancy) ──
DEEP_CERULEAN    = (0.18, 0.52, 0.82)   # Mediterranean harbour water
CHROME_YELLOW    = (0.92, 0.72, 0.22)   # sunlit sails and stone highlights
SEA_GREEN        = (0.28, 0.68, 0.52)   # shallow harbour shallows
VIVID_ORANGE     = (0.82, 0.38, 0.16)   # hull accents, complementary to blue
VIOLET_MAGENTA   = (0.64, 0.22, 0.62)   # shadow complement to yellow
COOL_SKY_WHITE   = (0.88, 0.92, 0.96)   # sky luminosity and cloud tops
LEMON_YELLOW     = (0.96, 0.90, 0.32)   # sun glare on water crests
DEEP_VIOLET      = (0.34, 0.22, 0.68)   # deepest water shadow
WARM_STONE       = (0.86, 0.76, 0.52)   # lighthouse and quay stone
TERRACOTTA       = (0.78, 0.42, 0.28)   # terracotta roof tiles
NEAR_WHITE       = (0.96, 0.96, 0.92)   # ground / sky near zenith
OLIVE_SHADOW     = (0.36, 0.44, 0.26)   # distant hill vegetation
RED_HULL         = (0.82, 0.22, 0.18)   # fishing boat hull 1
BLUE_HULL        = (0.24, 0.44, 0.76)   # fishing boat hull 2
ORANGE_HULL      = (0.88, 0.52, 0.18)   # fishing boat hull 3
MAST_BROWN       = (0.52, 0.38, 0.22)   # mast timber
LANTERN_GOLD     = (0.98, 0.88, 0.40)   # lighthouse lantern housing
HARBOUR_LIGHT    = (0.72, 0.82, 0.90)   # water shimmer


def _blend(arr, col, strength):
    s = max(0.0, min(1.0, float(strength)))
    return arr * (1.0 - s) + np.array(col, dtype=np.float32) * s


def _ellipse(arr, cx, cy, rx, ry, color, opacity=1.0, feather=0.14):
    h, w = arr.shape[:2]
    rx, ry = max(rx, 1.0), max(ry, 1.0)
    for dy in range(-int(ry * 1.25), int(ry * 1.25) + 1):
        for dx in range(-int(rx * 1.25), int(rx * 1.25) + 1):
            px, py = int(cx + dx), int(cy + dy)
            if 0 <= px < w and 0 <= py < h:
                d = (dx / rx) ** 2 + (dy / ry) ** 2
                if d <= (1.0 + feather) ** 2:
                    alpha = max(0.0, min(1.0, (1.0 + feather - math.sqrt(d)) / (feather + 1e-6)))
                    arr[py, px] = _blend(arr[py, px], color, alpha * opacity)


def _rect(arr, x0, y0, x1, y1, color, opacity=1.0):
    h, w = arr.shape[:2]
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(w, int(x1)), min(h, int(y1))
    if x1 > x0 and y1 > y0:
        arr[y0:y1, x0:x1] = _blend(arr[y0:y1, x0:x1], color, opacity)


def _line(arr, x0, y0, x1, y1, color, thickness=1, opacity=0.88):
    h, w = arr.shape[:2]
    steps = max(abs(int(x1) - int(x0)), abs(int(y1) - int(y0)), 1)
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


def _gradient_col(arr, y0, y1, col_top, col_bot):
    h, w = arr.shape[:2]
    y0i, y1i = max(0, int(y0)), min(h, int(y1))
    span = max(y1i - y0i, 1)
    for y in range(y0i, y1i):
        t = (y - y0i) / span
        c = np.array(col_top, dtype=np.float32) * (1.0 - t) + np.array(col_bot, dtype=np.float32) * t
        arr[y, :] = _blend(arr[y, :], c, 1.0)


def make_reference():
    ref = np.ones((H, W, 3), dtype=np.float32) * np.array(NEAR_WHITE, dtype=np.float32)
    rng = np.random.RandomState(242)

    # ── Sky: cool white near zenith, deepening cerulean below, warm horizon band ──
    sky_bottom = int(H * 0.38)
    _gradient_col(ref, 0, sky_bottom,
                  NEAR_WHITE,
                  DEEP_CERULEAN)

    # Cloud wisps in upper quarter
    for _ in range(8):
        cx = int(rng.uniform(30, W - 30))
        cy = int(rng.uniform(20, int(H * 0.18)))
        rw = int(rng.uniform(35, 85))
        rh = int(rng.uniform(10, 22))
        _ellipse(ref, cx, cy, rw, rh, COOL_SKY_WHITE, opacity=0.60, feather=0.50)

    # Warm yellow-orange horizon glow band
    h_band = int(H * 0.36)
    h_band2 = int(H * 0.40)
    for y in range(h_band, h_band2):
        t = (y - h_band) / max(h_band2 - h_band, 1)
        glow = 1.0 - abs(t - 0.5) * 2.5
        glow = max(0.0, glow)
        ref[y, :] = _blend(ref[y, :], CHROME_YELLOW, 0.28 * glow)
        ref[y, :] = _blend(ref[y, :], VIVID_ORANGE,  0.14 * glow)

    # ── Distant hillside: terracotta roofs + olive vegetation ────────────────
    hill_y0 = int(H * 0.30)
    hill_y1 = int(H * 0.42)
    # Olive hill mass on left
    for xi in range(0, int(W * 0.35)):
        hy = hill_y0 + int(8 * math.sin(xi * 0.06))
        _ellipse(ref, xi, hy + 12, 18, 22, OLIVE_SHADOW, opacity=0.45, feather=0.55)
    # Terracotta roofline right of hillside
    for xi in range(int(W * 0.28), int(W * 0.72), 18):
        ry = hill_y0 - 2 + int(6 * rng.uniform(-1, 1))
        rw_ = int(rng.uniform(14, 26))
        rh_ = int(rng.uniform(8, 16))
        _rect(ref, xi, ry, xi + rw_, ry + rh_, TERRACOTTA, opacity=rng.uniform(0.55, 0.78))
    # White house walls below roof
    for xi in range(int(W * 0.28), int(W * 0.72), 18):
        ry = hill_y0 + int(rng.uniform(4, 12))
        rw_ = int(rng.uniform(14, 24))
        rh_ = int(rng.uniform(10, 20))
        _rect(ref, xi, ry, xi + rw_, ry + rh_, WARM_STONE, opacity=rng.uniform(0.40, 0.62))

    # ── Harbour water: sea-green shallows → deep cerulean further out ─────────
    water_y0 = int(H * 0.39)
    _gradient_col(ref, water_y0, H,
                  COOL_SKY_WHITE,   # horizon reflection at water line
                  DEEP_VIOLET)      # deep violet-blue at canvas bottom

    # Sea-green in upper harbour (closer to quay / shallower)
    quay_bottom = int(H * 0.72)
    for y in range(water_y0, quay_bottom):
        t = (y - water_y0) / max(quay_bottom - water_y0, 1)
        green_amt = (1.0 - t) * 0.55
        ref[y, :] = _blend(ref[y, :], SEA_GREEN, green_amt)
        ref[y, :] = _blend(ref[y, :], DEEP_CERULEAN, t * 0.40)

    # Horizontal glinting shimmer bands on water
    for _ in range(32):
        sy  = int(rng.uniform(water_y0 + 10, quay_bottom))
        sx  = int(rng.uniform(0, W - 60))
        sw  = int(rng.uniform(18, 70))
        ref[sy:sy + 1, sx:sx + sw] = _blend(ref[sy:sy + 1, sx:sx + sw], HARBOUR_LIGHT, 0.42)
        ref[min(sy + 1, H - 1):min(sy + 2, H), sx:sx + sw] = _blend(
            ref[min(sy + 1, H - 1):min(sy + 2, H), sx:sx + sw], HARBOUR_LIGHT, 0.22)

    # Orange and lemon glare reflection from lighthouse/sky
    for _ in range(14):
        sy = int(rng.uniform(water_y0 + 5, water_y0 + 40))
        sx = int(rng.uniform(int(W * 0.52), int(W * 0.75)))
        sw = int(rng.uniform(12, 35))
        ref[sy:sy + 1, sx:sx + sw] = _blend(ref[sy:sy + 1, sx:sx + sw], LEMON_YELLOW, 0.35)

    # ── Stone quay (foreground, horizontal band) ─────────────────────────────
    quay_y0 = int(H * 0.68)
    quay_y1 = int(H * 0.74)
    _rect(ref, 0, quay_y0, W, quay_y1, WARM_STONE, opacity=0.85)
    # Quay shadow edge at bottom
    _rect(ref, 0, quay_y1, W, quay_y1 + 6, DEEP_VIOLET, opacity=0.45)
    # Stone texture: slightly varied rows
    for xi in range(0, W, 22):
        for yi in range(quay_y0, quay_y1, 6):
            ref[yi:yi + 1, xi:min(xi + 18, W)] = _blend(
                ref[yi:yi + 1, xi:min(xi + 18, W)],
                (WARM_STONE[0] * 0.85, WARM_STONE[1] * 0.85, WARM_STONE[2] * 0.85),
                0.30)

    # ── Lighthouse: central vertical tower, slightly right of centre ──────────
    lh_cx   = int(W * 0.60)
    lh_base_y = quay_y0
    lh_top_y  = int(H * 0.08)
    lh_w    = 28   # half-width

    # Tower body: warm white stone with slight taper
    for y in range(lh_top_y + 30, lh_base_y):
        taper = 1.0 - (lh_base_y - y) / max(lh_base_y - lh_top_y, 1) * 0.18
        hw = max(4, int(lh_w * taper))
        ref[y, lh_cx - hw:lh_cx + hw] = _blend(
            ref[y, lh_cx - hw:lh_cx + hw], WARM_STONE, 0.92)

    # Red stripe band on tower (lighthouse marking)
    stripe_y0 = int(H * 0.32)
    stripe_y1 = stripe_y0 + 18
    for y in range(stripe_y0, stripe_y1):
        taper = 1.0 - (lh_base_y - y) / max(lh_base_y - lh_top_y, 1) * 0.18
        hw = max(4, int(lh_w * taper))
        ref[y, lh_cx - hw:lh_cx + hw] = _blend(
            ref[y, lh_cx - hw:lh_cx + hw], RED_HULL, 0.78)

    # Lantern housing (gold, at top)
    lantern_y0 = lh_top_y + 8
    lantern_y1 = lh_top_y + 30
    _rect(ref, lh_cx - 16, lantern_y0, lh_cx + 16, lantern_y1, LANTERN_GOLD, opacity=0.90)
    # Lantern cap (dome shape)
    _ellipse(ref, lh_cx, lantern_y0, 18, 10, WARM_STONE, opacity=0.88, feather=0.20)
    # Balcony railing
    _rect(ref, lh_cx - 20, lantern_y1, lh_cx + 20, lantern_y1 + 5, WARM_STONE, opacity=0.85)

    # ── Three fishing boats moored at the quay ────────────────────────────────
    boats = [
        {"hull": RED_HULL,    "cx": int(W * 0.18), "w": 56, "h_boat": 22},
        {"hull": BLUE_HULL,   "cx": int(W * 0.38), "w": 64, "h_boat": 26},
        {"hull": ORANGE_HULL, "cx": int(W * 0.80), "w": 52, "h_boat": 20},
    ]
    boat_water_y = int(H * 0.67)

    for boat in boats:
        cx   = boat["cx"]
        bw   = boat["w"] // 2
        bh   = boat["h_boat"]
        by0  = boat_water_y - bh

        # Hull: ellipse slightly wider than tall, rounded bottom
        _ellipse(ref, cx, by0 + bh // 2, bw, bh // 2, boat["hull"], opacity=0.92, feather=0.12)
        # Upper hull/gunwale: thin band
        _rect(ref, cx - bw, by0, cx + bw, by0 + 6, WARM_STONE, opacity=0.72)
        # Mast
        mast_top_y  = by0 - int(rng.uniform(55, 80))
        mast_top_y  = max(int(H * 0.12), mast_top_y)
        _line(ref, cx, by0, cx, mast_top_y, MAST_BROWN, thickness=1, opacity=0.82)
        # Boom (horizontal)
        boom_len = int(rng.uniform(18, 28))
        _line(ref, cx, by0 + 8, cx + boom_len, by0 + 16, MAST_BROWN, thickness=1, opacity=0.68)
        # Hull reflection in water (simpler, lower, darker)
        ref_cy  = boat_water_y + bh // 2 + 4
        ref_col = (boat["hull"][0] * 0.50, boat["hull"][1] * 0.50, boat["hull"][2] * 0.60)
        _ellipse(ref, cx, ref_cy, bw + 4, bh // 3, ref_col, opacity=0.32, feather=0.55)

    # ── Foreground water (near bottom, below quay) ────────────────────────────
    bottom_water_y = quay_y1 + 6
    _gradient_col(ref, bottom_water_y, H,
                  DEEP_CERULEAN,
                  DEEP_VIOLET)
    # Foreground shimmer
    for _ in range(18):
        sy = int(rng.uniform(bottom_water_y + 5, H - 10))
        sx = int(rng.uniform(0, W - 50))
        sw = int(rng.uniform(25, 65))
        ref[sy:sy + 1, sx:sx + sw] = _blend(ref[sy:sy + 1, sx:sx + sw], HARBOUR_LIGHT, 0.32)

    return ref


def paint():
    print("Session 242: The Lighthouse at Port de Saint-Tropez (Signac Divisionist Mosaic, 153rd mode)")

    ref_arr = make_reference()
    ref = Image.fromarray((np.clip(ref_arr, 0, 1) * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=242)

    # High-key off-white ground (Signac worked on white-primed canvas for maximum colour luminosity)
    p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.03)

    # Underpainting — broad colour masses
    p.underpainting(ref, stroke_size=48, n_strokes=130)

    # Block in — two passes
    p.block_in(ref, stroke_size=28, n_strokes=190)
    p.block_in(ref, stroke_size=12, n_strokes=240)

    # Build form — medium then fine
    p.build_form(ref, stroke_size=7, n_strokes=280)
    p.build_form(ref, stroke_size=3, n_strokes=320)

    # Place lights — water shimmer, lighthouse lantern, chrome yellow sail glints
    p.place_lights(ref, stroke_size=2, n_strokes=140)

    # ── Session 242 new artistic pass: Signac Divisionist Mosaic (153rd mode) ──
    # Rectangular mosaic patches with complementary interleaving and Chevreul
    # simultaneous contrast boost at opposing-hue patch boundaries.
    p.signac_divisionist_mosaic_pass(
        patch_size=7,
        comp_mix=0.32,
        sat_boost=0.24,
        hue_thresh=75.0,
        blend_sigma=0.7,
        opacity=0.68,
    )

    # ── Session 242 artistic improvement: Color Bloom ────────────────────────
    # Saturated reds, blues, and yellows irradiate into adjacent areas.
    # Blue channel blooms slightly further (shorter wavelength diffraction).
    p.paint_color_bloom_pass(
        bloom_threshold=0.48,
        bloom_sigma=3.5,
        bloom_strength=0.24,
        chroma_shift=0.018,
        opacity=0.58,
    )

    # Diffuse boundary — smooth edges
    p.diffuse_boundary_pass(opacity=0.18)

    # Final glaze: thin cerulean wash for Mediterranean light unity
    p.glaze((0.18, 0.52, 0.82), opacity=0.08)

    # Warm yellow glaze for afternoon sun
    p.glaze((0.92, 0.72, 0.22), opacity=0.05)

    # Vignette — slightly darker corners to push eye toward harbour/lighthouse
    p.canvas.vignette(strength=0.18)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s242_signac_lighthouse_saint_tropez.png")
    p.canvas.save(out_path)
    print(f"Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    paint()
