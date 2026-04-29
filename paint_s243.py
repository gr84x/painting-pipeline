"""paint_s243.py -- Session 243: Woman at the Cafe Corner, Berlin (Kirchner Die Brucke, 154th mode)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
from stroke_engine import Painter

W, H = 520, 700

ACID_YELLOW       = (0.88, 0.84, 0.08)
COBALT_BLUE       = (0.14, 0.26, 0.72)
CADMIUM_RED       = (0.82, 0.12, 0.14)
OLIVE_BLACK       = (0.12, 0.16, 0.08)
ACID_LIME         = (0.44, 0.68, 0.18)
VIVID_MAGENTA     = (0.70, 0.12, 0.56)
ZINC_WHITE        = (0.94, 0.92, 0.90)
NEAR_BLACK        = (0.08, 0.06, 0.05)
DARK_VIOLET       = (0.24, 0.10, 0.40)
TERRACOTTA        = (0.70, 0.36, 0.22)
WARM_AMBER        = (0.80, 0.52, 0.18)
DEEP_WALL         = (0.10, 0.13, 0.07)
ELECTRIC_YELLOW   = (0.98, 0.96, 0.16)
DRESS_STRIPE_DARK = (0.56, 0.62, 0.08)


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


def make_reference():
    """
    Reference: Woman at the Cafe Corner, Berlin
    A seated young woman in acid-yellow striped dress, three-quarters to viewer.
    Dark Berlin cafe interior. Harsh yellow gaslight upper-right. Small marble table.
    Acid lime flesh (Kirchner distortion). Heavy dark hair cut blunt below ears.
    Coffee cup. Background dark male figure partially visible. Dark panelled walls.
    """
    ref = np.ones((H, W, 3), dtype=np.float32) * np.array(DEEP_WALL, dtype=np.float32)
    rng = np.random.RandomState(243)

    # Background wall
    _gradient_row(ref, 0, H, (0.10, 0.13, 0.07), (0.16, 0.12, 0.06))
    _rect(ref, 0, 0, W // 3, H, NEAR_BLACK, opacity=0.40)
    for xi in range(0, W, 38):
        _line(ref, xi, 0, xi, H, NEAR_BLACK, thickness=1, opacity=0.35)
    chair_rail_y = int(H * 0.60)
    _rect(ref, 0, chair_rail_y, W, chair_rail_y + 6, (0.22, 0.18, 0.10), opacity=0.80)

    # Lamp light (upper right)
    lamp_cx, lamp_cy = int(W * 0.82), int(H * 0.05)
    _ellipse(ref, lamp_cx, lamp_cy + 30, 12, 8, ELECTRIC_YELLOW, opacity=0.95)
    _ellipse(ref, lamp_cx, lamp_cy + 22, 7, 7, ZINC_WHITE, opacity=0.95)
    for r in range(5, 220, 6):
        alpha = max(0.0, 0.55 - r / 280.0)
        spread = r * 0.68
        ell_cx = lamp_cx - int(r * 0.38)
        ell_cy = lamp_cy + 30 + int(r * 0.60)
        warm = _blend(np.array(WARM_AMBER, dtype=np.float32), ELECTRIC_YELLOW, max(0, 0.5 - r/200.0))
        _ellipse(ref, ell_cx, ell_cy, int(spread*0.6), int(spread*0.35), tuple(warm.tolist()), opacity=alpha*0.45, feather=0.6)

    # Table
    table_cx = int(W * 0.46)
    table_top = int(H * 0.72)
    table_rx, table_ry = 90, 26
    _ellipse(ref, table_cx, table_top, table_rx, table_ry, TERRACOTTA, opacity=0.90)
    _ellipse(ref, table_cx + 18, table_top - 4, 58, 16, WARM_AMBER, opacity=0.65)
    _ellipse(ref, table_cx, table_top + 8, table_rx, int(table_ry * 0.55), NEAR_BLACK, opacity=0.55)
    _line(ref, table_cx, table_top + table_ry, table_cx - 8, H, (0.18, 0.14, 0.08), thickness=3)

    cup_cx, cup_cy = int(W * 0.52), table_top - 14
    _ellipse(ref, cup_cx, cup_cy, 14, 9, ZINC_WHITE, opacity=0.92)
    _ellipse(ref, cup_cx + 10, cup_cy + 8, 16, 7, (0.16, 0.14, 0.10), opacity=0.50, feather=0.30)
    _ellipse(ref, cup_cx, cup_cy - 3, 9, 4, (0.18, 0.16, 0.14), opacity=0.70)

    # Background figure (cobalt-dark)
    bg_cx = int(W * 0.75)
    bg_shoulder_y = int(H * 0.30)
    _ellipse(ref, bg_cx, bg_shoulder_y - 52, 20, 25, (0.16, 0.20, 0.46), opacity=0.72, feather=0.25)
    _rect(ref, bg_cx - 22, bg_shoulder_y - 30, bg_cx + 22, bg_shoulder_y + 120, (0.12, 0.16, 0.38), opacity=0.60)
    _ellipse(ref, bg_cx, bg_shoulder_y + 5, 8, 12, (0.44, 0.48, 0.52), opacity=0.55, feather=0.3)

    # Woman figure
    fig_cx = int(W * 0.40)
    head_cx = fig_cx + 12
    head_cy = int(H * 0.22)

    # Neck
    neck_top = head_cy + 32
    neck_bot = int(H * 0.38)
    _rect(ref, head_cx - 10, neck_top, head_cx + 10, neck_bot, ACID_LIME, opacity=0.75)

    # Head: acid lime flesh
    _ellipse(ref, head_cx, head_cy, 46, 58, ACID_LIME, opacity=0.88)
    _ellipse(ref, head_cx - 14, head_cy + 6, 30, 48,
             _blend(np.array(COBALT_BLUE, dtype=np.float32), ACID_LIME, 0.28).tolist(), opacity=0.42, feather=0.30)
    _ellipse(ref, head_cx + 18, head_cy - 10, 16, 20, ZINC_WHITE, opacity=0.28, feather=0.45)

    # Hair
    _ellipse(ref, head_cx, head_cy - 30, 50, 28, NEAR_BLACK, opacity=0.88)
    _rect(ref, head_cx - 50, head_cy - 18, head_cx - 22, head_cy + 52, NEAR_BLACK, opacity=0.82)
    _rect(ref, head_cx + 22, head_cy - 16, head_cx + 52, head_cy + 52, NEAR_BLACK, opacity=0.82)
    _rect(ref, head_cx - 44, head_cy - 44, head_cx + 48, head_cy - 20, NEAR_BLACK, opacity=0.85)

    # Eyes
    for ex, ey in [(head_cx - 15, head_cy + 2), (head_cx + 12, head_cy + 2)]:
        _ellipse(ref, ex, ey, 9, 7, NEAR_BLACK, opacity=0.90)
        _ellipse(ref, ex, ey, 4, 4, (0.06, 0.05, 0.05), opacity=0.95)

    # Nose
    _line(ref, head_cx + 2, head_cy + 8, head_cx - 4, head_cy + 28, NEAR_BLACK, thickness=1, opacity=0.55)
    _ellipse(ref, head_cx - 6, head_cy + 28, 4, 3, NEAR_BLACK, opacity=0.42)

    # Mouth
    _ellipse(ref, head_cx + 2, head_cy + 42, 14, 5, CADMIUM_RED, opacity=0.72)
    _line(ref, head_cx - 10, head_cy + 42, head_cx + 14, head_cy + 42, NEAR_BLACK, thickness=1, opacity=0.60)

    # Ear
    _ellipse(ref, head_cx + 44, head_cy + 14, 8, 12, ACID_LIME, opacity=0.65)

    # Shoulders and torso (dress)
    torso_top = int(H * 0.38)
    torso_bot = int(H * 0.92)
    _ellipse(ref, fig_cx - 52, torso_top + 14, 52, 26, ACID_YELLOW, opacity=0.86)
    _ellipse(ref, fig_cx + 68, torso_top + 14, 36, 22, ACID_YELLOW, opacity=0.72)
    _rect(ref, fig_cx - 72, torso_top + 16, fig_cx + 88, torso_bot, ACID_YELLOW, opacity=0.88)

    # Dress stripes
    for offset in range(-400, 400, 28):
        sx0 = fig_cx - 72 + offset
        sx1 = sx0 + 14
        _rect(ref, sx0, torso_top + 16, sx1, torso_bot, DRESS_STRIPE_DARK, opacity=0.55)

    # Dress shadow zone
    _rect(ref, fig_cx - 72, torso_top, int(fig_cx - 10), torso_bot, DARK_VIOLET, opacity=0.36)

    # Collar V
    _line(ref, head_cx, neck_bot, fig_cx - 20, torso_top + 38, NEAR_BLACK, thickness=2, opacity=0.80)
    _line(ref, head_cx, neck_bot, fig_cx + 36, torso_top + 38, NEAR_BLACK, thickness=2, opacity=0.80)

    # Left arm (resting on table)
    arm_l_x0, arm_l_y0 = fig_cx - 62, torso_top + 50
    arm_l_x1, arm_l_y1 = fig_cx - 90, table_top - 10
    _line(ref, arm_l_x0, arm_l_y0, arm_l_x1, arm_l_y1, ACID_LIME, thickness=14, opacity=0.80)
    _line(ref, arm_l_x1, arm_l_y1, arm_l_x1 + 48, table_top - 6, ACID_LIME, thickness=10, opacity=0.80)
    _ellipse(ref, arm_l_x1 + 60, table_top - 8, 14, 8, ACID_LIME, opacity=0.78)

    # Right arm (holding cup)
    arm_r_x0, arm_r_y0 = fig_cx + 72, torso_top + 48
    _line(ref, arm_r_x0, arm_r_y0, cup_cx - 12, cup_cy + 10, ACID_LIME, thickness=12, opacity=0.78)
    _ellipse(ref, cup_cx - 8, cup_cy + 12, 12, 8, ACID_LIME, opacity=0.72)

    # Lap
    lap_y = int(H * 0.72)
    _ellipse(ref, fig_cx + 8, lap_y + 20, 90, 38, ACID_YELLOW, opacity=0.80)
    _ellipse(ref, fig_cx - 20, lap_y + 22, 60, 28, DARK_VIOLET, opacity=0.38, feather=0.30)

    # Floor
    _gradient_row(ref, int(H * 0.88), H, (0.18, 0.14, 0.08), (0.10, 0.08, 0.05))

    # Table shadow
    _ellipse(ref, table_cx + 8, H - 28, 70, 16, NEAR_BLACK, opacity=0.42, feather=0.35)

    # Figure shadow
    _ellipse(ref, fig_cx - 60, lap_y + 55, 55, 18, NEAR_BLACK, opacity=0.35, feather=0.40)

    # Red accent (colour key)
    _ellipse(ref, fig_cx + 16, torso_top + 32, 8, 7, CADMIUM_RED, opacity=0.62)

    noise = rng.uniform(-0.03, 0.03, ref.shape).astype(np.float32)
    ref = np.clip(ref + noise, 0.0, 1.0)
    return Image.fromarray((ref * 255).astype(np.uint8), "RGB")


def main():
    ref = make_reference()
    p = Painter(W, H, seed=243)

    p.tone_ground(DEEP_WALL, texture_strength=0.06)
    p.underpainting(ref, stroke_size=60, n_strokes=140)
    p.block_in(ref, stroke_size=42, n_strokes=260)
    p.block_in(ref, stroke_size=26, n_strokes=380)
    p.build_form(ref, stroke_size=16, n_strokes=480)
    p.build_form(ref, stroke_size=9, n_strokes=560)
    p.build_form(ref, stroke_size=5, n_strokes=460)
    p.place_lights(ref, stroke_size=3, n_strokes=300)
    p.place_lights(ref, stroke_size=2, n_strokes=200)

    # Imprimatura: warm amber ground in shadow zones
    p.paint_imprimatura_warmth_pass(
        warmth_gate=0.30, warmth_str=0.26,
        imprimatura_r=0.70, imprimatura_g=0.44, imprimatura_b=0.16,
        edge_warmth=0.14, edge_sigma=1.4, opacity=0.62)

    # Kirchner Die Brucke: chromatic dissonance + woodcut contour + polarization
    p.kirchner_brucke_expressionist_pass(
        hue_pull_str=0.58, contour_thresh=0.07, contour_dark=0.28,
        polarize_radius=8, polarize_str=0.30, opacity=0.82)

    # Additional detail
    p.build_form(ref, stroke_size=3, n_strokes=220)

    # Second Kirchner pass (consolidation)
    p.kirchner_brucke_expressionist_pass(
        hue_pull_str=0.28, contour_thresh=0.10, contour_dark=0.40,
        polarize_radius=5, polarize_str=0.16, opacity=0.38)

    # Second imprimatura (edge fringe reinforcement)
    p.paint_imprimatura_warmth_pass(
        warmth_gate=0.22, warmth_str=0.18,
        imprimatura_r=0.72, imprimatura_g=0.40, imprimatura_b=0.14,
        edge_warmth=0.18, edge_sigma=0.9, opacity=0.40)

    p.canvas.vignette(strength=0.62)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "s243_kirchner_cafe_woman.png")
    p.canvas.save(out_path)
    print(f"\nPainting saved: {out_path}")
    return out_path


if __name__ == "__main__":
    main()
