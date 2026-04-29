"""paint_s244.py -- Session 244: The Tarot Reader (Max Beckmann Black Armature, 155th mode)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
from stroke_engine import Painter

W, H = 520, 700

# Beckmann palette
SALMON_ORANGE    = (0.82, 0.42, 0.28)
ACID_GREEN       = (0.62, 0.72, 0.22)
COLD_BLUE_VIOLET = (0.14, 0.28, 0.56)
BRICK_RED        = (0.60, 0.14, 0.16)
DEEP_TEAL        = (0.24, 0.44, 0.40)
NEAR_BLACK       = (0.06, 0.05, 0.04)
ZINC_WHITE       = (0.92, 0.90, 0.88)
RAW_UMBER        = (0.54, 0.34, 0.22)
ACID_FLESH       = (0.72, 0.76, 0.38)
CANDLE_YELLOW    = (0.96, 0.82, 0.24)
CURTAIN_RED      = (0.58, 0.12, 0.14)
DARK_UMBER       = (0.22, 0.14, 0.08)
CARD_IVORY       = (0.86, 0.82, 0.62)
TABLE_BROWN      = (0.38, 0.26, 0.14)


def _blend(arr, col, strength):
    s = max(0.0, min(1.0, float(strength)))
    return arr * (1.0 - s) + np.array(col, dtype=np.float32) * s


def _ellipse(arr, cx, cy, rx, ry, color, opacity=1.0, feather=0.14):
    h, w = arr.shape[:2]
    rx, ry = max(rx, 1.0), max(ry, 1.0)
    for dy in range(-int(ry * 1.3), int(ry * 1.3) + 1):
        for dx in range(-int(rx * 1.3), int(rx * 1.3) + 1):
            px, py = int(cx + dx), int(cy + dy)
            if 0 <= px < w and 0 <= py < h:
                d = (dx / rx) ** 2 + (dy / ry) ** 2
                if d <= (1.0 + feather) ** 2:
                    a = max(0.0, min(1.0, (1.0 + feather - math.sqrt(d)) / (feather + 1e-6)))
                    arr[py, px] = _blend(arr[py, px], color, a * opacity)


def _rect(arr, x0, y0, x1, y1, color, opacity=1.0):
    h, w = arr.shape[:2]
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(w, int(x1)), min(h, int(y1))
    if x1 > x0 and y1 > y0:
        arr[y0:y1, x0:x1] = _blend(arr[y0:y1, x0:x1], color, opacity)


def _line(arr, x0, y0, x1, y1, color, thickness=1, opacity=0.90):
    steps = max(abs(int(x1 - x0)), abs(int(y1 - y0)), 1)
    for i in range(steps + 1):
        t = i / steps
        x = int(x0 + t * (x1 - x0))
        y = int(y0 + t * (y1 - y0))
        h, w = arr.shape[:2]
        for ty in range(-thickness, thickness + 1):
            for tx in range(-thickness, thickness + 1):
                if tx * tx + ty * ty <= thickness * thickness:
                    px, py = x + tx, y + ty
                    if 0 <= px < w and 0 <= py < h:
                        arr[py, px] = _blend(arr[py, px], color, opacity)


def _gradient_row(arr, y0, y1, col_top, col_bot):
    h, w = arr.shape[:2]
    y0i, y1i = max(0, int(y0)), min(h, int(y1))
    span = max(y1i - y0i, 1)
    for y in range(y0i, y1i):
        t = (y - y0i) / span
        c = np.array(col_top, dtype=np.float32) * (1.0 - t) + np.array(col_bot, dtype=np.float32) * t
        arr[y, :] = _blend(arr[y, :], c, 1.0)


def _poly_fill(arr, pts, color, opacity=1.0):
    """Fill a convex polygon by scanline."""
    h, w = arr.shape[:2]
    if len(pts) < 3:
        return
    min_y = max(0, int(min(p[1] for p in pts)))
    max_y = min(h - 1, int(max(p[1] for p in pts)))
    for y in range(min_y, max_y + 1):
        xs = []
        n = len(pts)
        for i in range(n):
            x0_, y0_ = pts[i]
            x1_, y1_ = pts[(i + 1) % n]
            if (y0_ <= y < y1_) or (y1_ <= y < y0_):
                if abs(y1_ - y0_) > 0:
                    t = (y - y0_) / (y1_ - y0_)
                    xs.append(x0_ + t * (x1_ - x0_))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            x_left  = max(0, int(xs[k]))
            x_right = min(w, int(xs[k + 1]) + 1)
            arr[y, x_left:x_right] = _blend(arr[y, x_left:x_right], color, opacity)


def build_scene(w, h):
    arr = np.zeros((h, w, 3), dtype=np.float32)

    # ── Background: near-black walls with compressed depth ──────────────────
    _gradient_row(arr, 0, h * 0.55, NEAR_BLACK, DARK_UMBER)
    _gradient_row(arr, int(h * 0.55), h, DARK_UMBER, NEAR_BLACK)

    # ── Brick-red curtain: right wall, top to mid ───────────────────────────
    _rect(arr, w * 0.60, 0, w, h * 0.52, CURTAIN_RED, 0.88)
    # curtain folds: dark vertical bands
    for cx in [w * 0.68, w * 0.76, w * 0.86]:
        _rect(arr, cx, 0, cx + 6, h * 0.52, NEAR_BLACK, 0.60)

    # ── Rope: hanging from upper-left corner (Beckmann motif) ───────────────
    _line(arr, w * 0.08, 0, w * 0.14, h * 0.30, DARK_UMBER, thickness=2, opacity=0.85)
    _line(arr, w * 0.14, h * 0.30, w * 0.10, h * 0.42, DARK_UMBER, thickness=2, opacity=0.80)

    # ── Table surface: salmon-orange slab, lower third ──────────────────────
    _rect(arr, 0, h * 0.58, w, h, TABLE_BROWN, 0.95)
    _rect(arr, 0, h * 0.58, w, h * 0.62, SALMON_ORANGE, 0.70)  # lit table edge

    # ── Tarot cards on the table ─────────────────────────────────────────────
    card_data = [
        (w * 0.22, h * 0.62, w * 0.10, h * 0.07, 15),
        (w * 0.38, h * 0.63, w * 0.10, h * 0.07, -8),
        (w * 0.54, h * 0.61, w * 0.10, h * 0.07, 12),
        (w * 0.70, h * 0.64, w * 0.10, h * 0.07, -5),
        (w * 0.15, h * 0.68, w * 0.09, h * 0.06, 20),
        (w * 0.46, h * 0.69, w * 0.09, h * 0.06, -15),
        (w * 0.62, h * 0.67, w * 0.09, h * 0.06, 7),
    ]
    for (cx, cy, cw, ch_, ang) in card_data:
        _rect(arr, cx - cw/2, cy - ch_/2, cx + cw/2, cy + ch_/2, CARD_IVORY, 0.88)
        _rect(arr, cx - cw/2 + 2, cy - ch_/2 + 2, cx + cw/2 - 2, cy + ch_/2 - 2, COLD_BLUE_VIOLET, 0.45)
        _line(arr, cx - cw/2, cy, cx + cw/2, cy, NEAR_BLACK, thickness=1, opacity=0.50)

    # ── Candlestick: right of figure ─────────────────────────────────────────
    _rect(arr, w * 0.76, h * 0.52, w * 0.79, h * 0.60, RAW_UMBER, 0.95)
    _rect(arr, w * 0.74, h * 0.59, w * 0.81, h * 0.62, RAW_UMBER, 0.90)
    # candle flame
    _ellipse(arr, w * 0.775, h * 0.495, 8, 16, CANDLE_YELLOW, opacity=0.95, feather=0.30)
    _ellipse(arr, w * 0.775, h * 0.490, 4, 8, ZINC_WHITE, opacity=0.85, feather=0.25)
    # candle light pool on wall/table
    _ellipse(arr, w * 0.78, h * 0.53, 90, 60, CANDLE_YELLOW, opacity=0.12, feather=0.80)
    _ellipse(arr, w * 0.78, h * 0.56, 70, 40, CANDLE_YELLOW, opacity=0.10, feather=0.80)

    # ── Symbolic fish on wooden plate: lower-left (Beckmann motif) ──────────
    _ellipse(arr, w * 0.10, h * 0.76, 40, 16, RAW_UMBER, opacity=0.92, feather=0.20)
    _ellipse(arr, w * 0.10, h * 0.76, 30, 10, ACID_GREEN, opacity=0.75, feather=0.18)  # fish body
    # tail fin
    _poly_fill(arr, [
        (int(w * 0.10 - 30), int(h * 0.76)),
        (int(w * 0.10 - 42), int(h * 0.76 - 12)),
        (int(w * 0.10 - 42), int(h * 0.76 + 12)),
    ], ACID_GREEN, 0.70)
    _ellipse(arr, w * 0.12, h * 0.756, 4, 4, NEAR_BLACK, opacity=0.80, feather=0.10)  # eye

    # ── Figure body: teal-and-black striped dress, torso centre ─────────────
    torso_cx, torso_top, torso_bot = w * 0.44, h * 0.30, h * 0.60
    # dress base
    _poly_fill(arr, [
        (int(w * 0.22), int(torso_bot)),
        (int(w * 0.66), int(torso_bot)),
        (int(w * 0.60), int(torso_top)),
        (int(w * 0.28), int(torso_top)),
    ], DEEP_TEAL, 0.95)
    # dress stripes
    stripe_colors = [NEAR_BLACK, DEEP_TEAL]
    for i, sx in enumerate(np.linspace(w * 0.22, w * 0.62, 10)):
        _rect(arr, sx, torso_top, sx + 10, torso_bot, stripe_colors[i % 2], 0.60)

    # ── Arms: spread wide over the table ────────────────────────────────────
    # Left arm (reaching left-down toward cards)
    _poly_fill(arr, [
        (int(w * 0.28), int(h * 0.46)),
        (int(w * 0.22), int(h * 0.50)),
        (int(w * 0.08), int(h * 0.62)),
        (int(w * 0.16), int(h * 0.64)),
        (int(w * 0.30), int(h * 0.52)),
    ], ACID_FLESH, 0.90)
    # Right arm (raised slightly, gesturing upward-right)
    _poly_fill(arr, [
        (int(w * 0.60), int(h * 0.46)),
        (int(w * 0.66), int(h * 0.44)),
        (int(w * 0.80), int(h * 0.54)),
        (int(w * 0.76), int(h * 0.56)),
        (int(w * 0.62), int(h * 0.50)),
    ], ACID_FLESH, 0.90)

    # ── Left hand flat on table ──────────────────────────────────────────────
    _ellipse(arr, w * 0.12, h * 0.63, 22, 10, ACID_FLESH, opacity=0.92, feather=0.18)
    # fingers
    for fx, fy in [(0.06, 0.61), (0.09, 0.59), (0.14, 0.60), (0.18, 0.62)]:
        _ellipse(arr, w * fx, h * fy, 8, 5, ACID_FLESH, opacity=0.85, feather=0.15)

    # ── Right hand upward-gesturing ──────────────────────────────────────────
    _ellipse(arr, w * 0.78, h * 0.54, 18, 10, ACID_FLESH, opacity=0.88, feather=0.18)
    for fx, fy in [(0.80, 0.51), (0.82, 0.52), (0.84, 0.54), (0.83, 0.56)]:
        _ellipse(arr, w * fx, h * fy, 6, 4, ACID_FLESH, opacity=0.80, feather=0.15)

    # ── Neck ─────────────────────────────────────────────────────────────────
    _rect(arr, w * 0.40, h * 0.22, w * 0.50, h * 0.32, ACID_FLESH, 0.92)

    # ── Head: slightly tilted, direct confrontational gaze ───────────────────
    head_cx, head_cy = w * 0.44, h * 0.16
    _ellipse(arr, head_cx, head_cy, 54, 62, ACID_FLESH, opacity=0.95, feather=0.12)

    # Hair: blunt-cut dark bob
    _ellipse(arr, head_cx, head_cy - 18, 56, 32, NEAR_BLACK, opacity=0.96, feather=0.10)
    _rect(arr, head_cx - 54, head_cy - 26, head_cx + 54, head_cy - 6, NEAR_BLACK, 0.95)
    # side hair blocks
    _rect(arr, head_cx - 56, head_cy - 20, head_cx - 38, head_cy + 34, NEAR_BLACK, 0.92)
    _rect(arr, head_cx + 38, head_cy - 20, head_cx + 56, head_cy + 34, NEAR_BLACK, 0.92)

    # Eyes: wide, staring, outlined in black
    for ex, ey in [(head_cx - 20, head_cy + 4), (head_cx + 20, head_cy + 4)]:
        _ellipse(arr, ex, ey, 14, 9, ZINC_WHITE, opacity=0.95, feather=0.12)
        _ellipse(arr, ex + 2, ey, 7, 7, COLD_BLUE_VIOLET, opacity=0.92, feather=0.10)
        _ellipse(arr, ex + 3, ey, 4, 4, NEAR_BLACK, opacity=0.98, feather=0.08)
        _ellipse(arr, ex + 5, ey - 2, 2, 2, ZINC_WHITE, opacity=0.80, feather=0.10)
        # heavy black lids
        _line(arr, ex - 13, ey - 5, ex + 13, ey - 5, NEAR_BLACK, thickness=2, opacity=0.90)
        _line(arr, ex - 12, ey + 4, ex + 12, ey + 4, NEAR_BLACK, thickness=2, opacity=0.80)

    # Nose
    _line(arr, head_cx - 4, head_cy + 10, head_cx - 7, head_cy + 22, DARK_UMBER, thickness=2, opacity=0.75)
    _line(arr, head_cx - 7, head_cy + 22, head_cx + 7, head_cy + 22, DARK_UMBER, thickness=2, opacity=0.70)

    # Mouth: set, slightly downturned
    _line(arr, head_cx - 16, head_cy + 30, head_cx + 14, head_cy + 31, BRICK_RED, thickness=3, opacity=0.88)
    _line(arr, head_cx - 16, head_cy + 30, head_cx - 20, head_cy + 36, DARK_UMBER, thickness=2, opacity=0.70)

    # Cheekbone: flush of cold light from candle
    _ellipse(arr, head_cx + 24, head_cy + 14, 18, 12, CANDLE_YELLOW, opacity=0.20, feather=0.60)

    # ── Strong black outline (armature) — key contours ───────────────────────
    # Head outline
    for r_off in range(3):
        _ellipse(arr, head_cx, head_cy, 54 + r_off, 62 + r_off, NEAR_BLACK, opacity=0.08, feather=0.50)
    # Torso outline
    _line(arr, w * 0.28, torso_top, w * 0.22, torso_bot, NEAR_BLACK, thickness=3, opacity=0.85)
    _line(arr, w * 0.60, torso_top, w * 0.66, torso_bot, NEAR_BLACK, thickness=3, opacity=0.85)
    _line(arr, w * 0.22, torso_bot, w * 0.66, torso_bot, NEAR_BLACK, thickness=2, opacity=0.70)
    # Table edge
    _line(arr, 0, h * 0.59, w, h * 0.59, NEAR_BLACK, thickness=4, opacity=0.85)

    # ── Dark compressed background figure: left ──────────────────────────────
    _ellipse(arr, w * 0.12, h * 0.26, 26, 30, DARK_UMBER, opacity=0.70, feather=0.20)
    _rect(arr, w * 0.04, h * 0.30, w * 0.22, h * 0.50, DARK_UMBER, 0.55)

    return arr


def main():
    print("Session 244 — The Tarot Reader (Max Beckmann Black Armature)")
    print("Canvas:", W, "×", H)

    ref = build_scene(W, H)
    ref_img = Image.fromarray((np.clip(ref, 0, 1) * 255).astype(np.uint8), "RGB")

    p = Painter(W, H)
    print("  1. Tone ground — dark umber near-black")
    p.tone_ground((0.20, 0.18, 0.14), texture_strength=0.04)

    print("  2. Underpainting — block in major masses")
    p.underpainting(ref_img, stroke_size=46)

    print("  3. Block in — primary colour planes")
    p.block_in(ref_img, stroke_size=28, n_strokes=420)

    print("  4. Build form — secondary modelling")
    p.build_form(ref_img, stroke_size=14, n_strokes=320)

    print("  5. Place lights — highlights and candle glow")
    p.place_lights(ref_img, stroke_size=6, n_strokes=180)

    print("  6. Beckmann Black Armature pass (155th mode)")
    p.beckmann_black_armature_pass(
        armature_thresh=0.10,
        armature_snap=0.85,
        compress_str=0.20,
        compress_mid=0.46,
        palette_str=0.42,
        palette_radius=60.0,
        opacity=0.84,
    )

    print("  7. Paint Aerial Perspective pass (session 244 improvement)")
    p.paint_aerial_perspective_pass(
        fine_sigma=1.0,
        coarse_sigma=14.0,
        depth_str=0.40,
        haze_r=0.78,
        haze_g=0.80,
        haze_b=0.88,
        haze_strength=0.22,
        desat_str=0.28,
        opacity=0.60,
    )

    print("  8. Final sheen pass")
    p.canvas.sheen_pass()

    out_path = "s244_beckmann_tarot_reader.png"
    p.save(out_path)
    print(f"  Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    main()
