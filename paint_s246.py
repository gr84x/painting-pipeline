"""paint_s246.py -- Session 246: Marché à Tunis (August Macke Luminous Planes, 157th mode)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
from stroke_engine import Painter

W, H = 500, 660

# Macke Tunisian palette
CADMIUM_YELLOW   = (0.95, 0.78, 0.20)   # noon sun, sand floor
COBALT_BLUE      = (0.14, 0.32, 0.76)   # shadow wall, djellaba shadow
VERMILION        = (0.92, 0.26, 0.10)   # hanging fabric, copper gleam
CERULEAN         = (0.28, 0.62, 0.88)   # sky glow, awning stripe
WARM_WHITE       = (0.98, 0.96, 0.90)   # blazing sunlit wall
TERRACOTTA       = (0.78, 0.42, 0.22)   # architecture, jars
ACID_GREEN       = (0.72, 0.86, 0.16)   # market silk, frond accent
DEEP_VIOLET      = (0.32, 0.14, 0.52)   # doorway shadow, deep shade
OCHRE            = (0.86, 0.68, 0.28)   # warm sand ground
BURNT_ORANGE     = (0.82, 0.48, 0.12)   # copper vessels, awning stripe
DJELLABA_LIGHT   = (0.96, 0.95, 0.91)   # woman's garment sunlit side
DJELLABA_SHADOW  = (0.24, 0.44, 0.72)   # woman's garment shadow folds
SKIN_TONE        = (0.86, 0.60, 0.38)   # exposed skin
DARK_HAIR        = (0.18, 0.12, 0.08)   # hair
ARCH_GLOW        = (0.98, 0.96, 0.86)   # desert light through distant arch
COPPER_ORANGE    = (0.82, 0.52, 0.14)   # copper bowl highlights
NEAR_BLACK       = (0.08, 0.06, 0.10)   # deepest darks


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


def _gradient_v(arr, y0, y1, col_top, col_bot, opacity=1.0):
    """Vertical gradient fill from y0 to y1."""
    h, w = arr.shape[:2]
    y0i, y1i = max(0, int(y0)), min(h, int(y1))
    span = max(y1i - y0i, 1)
    ct = np.array(col_top, dtype=np.float32)
    cb = np.array(col_bot, dtype=np.float32)
    for y in range(y0i, y1i):
        t = (y - y0i) / span
        c = ct * (1.0 - t) + cb * t
        arr[y, :] = _blend(arr[y, :], c, opacity)


def _gradient_h(arr, x0, x1, y0, y1, col_left, col_right, opacity=1.0):
    """Horizontal gradient fill within x0..x1, y0..y1."""
    h, w = arr.shape[:2]
    x0i = max(0, int(x0)); x1i = min(w, int(x1))
    y0i = max(0, int(y0)); y1i = min(h, int(y1))
    span = max(x1i - x0i, 1)
    cl = np.array(col_left, dtype=np.float32)
    cr = np.array(col_right, dtype=np.float32)
    for x in range(x0i, x1i):
        t = (x - x0i) / span
        c = cl * (1.0 - t) + cr * t
        arr[y0i:y1i, x] = _blend(arr[y0i:y1i, x], c, opacity)


def build_scene(w, h):
    arr = np.zeros((h, w, 3), dtype=np.float32)

    # ── Base: warm golden sand floor + terracotta wall background ─────────────
    _gradient_v(arr, 0, h * 0.55, TERRACOTTA, OCHRE, opacity=1.0)
    _gradient_v(arr, h * 0.55, h, OCHRE, CADMIUM_YELLOW, opacity=1.0)

    # ── Left wall in deep violet-blue shadow (flat colour plane) ──────────────
    _rect(arr, 0, 0, w * 0.22, h, COBALT_BLUE, opacity=0.95)
    # Inner edge of left shadow wall: slightly lighter
    _gradient_h(arr, w * 0.18, w * 0.26, 0, h, COBALT_BLUE, DEEP_VIOLET, opacity=0.70)

    # ── Right wall blazing in full noon sun (warm ivory) ──────────────────────
    _rect(arr, w * 0.78, 0, w, h, WARM_WHITE, opacity=0.92)
    # Shadow fade from right wall edge inward
    _gradient_h(arr, w * 0.68, w * 0.82, 0, h * 0.80, TERRACOTTA, WARM_WHITE, opacity=0.60)

    # ── Far background: stone arch framing desert glow ────────────────────────
    arch_cx = w * 0.50
    arch_cy = h * 0.46
    # Desert arch glow (near-white)
    _ellipse(arr, arch_cx, arch_cy, w * 0.14, h * 0.18,
             ARCH_GLOW, opacity=0.96, feather=0.20)
    # Arch stone surround (terracotta)
    for r_off in range(3):
        _ellipse(arr, arch_cx, arch_cy, w * 0.14 + r_off * 4, h * 0.18 + r_off * 3,
                 TERRACOTTA, opacity=0.22, feather=0.60)
    # Arch shadow interior
    _ellipse(arr, arch_cx, arch_cy + h * 0.08, w * 0.10, h * 0.12,
             DEEP_VIOLET, opacity=0.72, feather=0.18)

    # ── Awning: horizontal coloured bands across top of canvas ────────────────
    awning_bot = h * 0.20
    stripe_h   = awning_bot / 5
    awning_colors = [COBALT_BLUE, BURNT_ORANGE, COBALT_BLUE, BURNT_ORANGE, COBALT_BLUE]
    for i, ac in enumerate(awning_colors):
        _rect(arr, 0, i * stripe_h, w, (i + 1) * stripe_h, ac, opacity=0.90)
    # Awning bottom fringe (cerulean)
    _rect(arr, 0, awning_bot - stripe_h * 0.3, w, awning_bot, CERULEAN, opacity=0.70)

    # ── Shadow stripes on sand floor from awning slats ────────────────────────
    stripe_count = 6
    for i in range(stripe_count):
        sx = w * (i / stripe_count)
        sw = w * 0.04
        _rect(arr, sx, h * 0.55, sx + sw, h, DEEP_VIOLET, opacity=0.18)

    # ── Hanging market goods: vermilion fabric, yellow-green silk ─────────────
    # Large bolt of vermilion fabric left-centre
    _rect(arr, w * 0.28, awning_bot, w * 0.38, h * 0.55, VERMILION, opacity=0.88)
    # Yellow-green silk panel centre
    _rect(arr, w * 0.40, awning_bot, w * 0.47, h * 0.50, ACID_GREEN, opacity=0.82)
    # Smaller vermilion piece right of centre
    _rect(arr, w * 0.55, awning_bot, w * 0.62, h * 0.48, VERMILION, opacity=0.76)
    # Orange fabric strip far right hanging area
    _rect(arr, w * 0.70, awning_bot, w * 0.76, h * 0.45, BURNT_ORANGE, opacity=0.80)

    # ── Market stall right foreground: table + pots + copper + cloth ──────────
    table_top = h * 0.60
    table_bot = h * 0.68
    # Table surface (ochre/warm)
    _rect(arr, w * 0.65, table_top, w * 0.95, table_bot, OCHRE, opacity=0.88)
    # Table shadow underside
    _rect(arr, w * 0.65, table_bot, w * 0.95, table_bot + h * 0.02, DEEP_VIOLET, opacity=0.72)
    # Terracotta pots on table
    for i, pot_x in enumerate([w * 0.68, w * 0.75, w * 0.83, w * 0.90]):
        _ellipse(arr, pot_x, table_top - h * 0.04, w * 0.025, h * 0.055,
                 TERRACOTTA, opacity=0.90, feather=0.12)
        # Pot rim shadow
        _ellipse(arr, pot_x, table_top - h * 0.07, w * 0.025, h * 0.015,
                 DEEP_VIOLET, opacity=0.60, feather=0.25)
    # Copper bowl
    _ellipse(arr, w * 0.78, table_top - h * 0.03, w * 0.04, h * 0.035,
             COPPER_ORANGE, opacity=0.88, feather=0.14)
    _ellipse(arr, w * 0.78, table_top - h * 0.03, w * 0.025, h * 0.020,
             CADMIUM_YELLOW, opacity=0.70, feather=0.30)  # specular
    # Folded cloth (deep violet + burnt orange)
    _rect(arr, w * 0.66, h * 0.70, w * 0.78, h * 0.78, DEEP_VIOLET, opacity=0.84)
    _rect(arr, w * 0.78, h * 0.70, w * 0.90, h * 0.78, BURNT_ORANGE, opacity=0.80)

    # ── Woman in djellaba (from behind, slightly left of centre) ──────────────
    figure_cx = w * 0.42
    figure_cy = h * 0.68   # base of figure (ground contact)
    fig_head_y = h * 0.28  # top of head

    # Main djellaba body (flat near-white plane, sunlit back facing us)
    _ellipse(arr, figure_cx, figure_cy - h * 0.20, w * 0.12, h * 0.28,
             DJELLABA_LIGHT, opacity=0.94, feather=0.08)
    # Djellaba left shadow (deep blue, away from direct noon sun)
    _ellipse(arr, figure_cx - w * 0.06, figure_cy - h * 0.20, w * 0.055, h * 0.26,
             DJELLABA_SHADOW, opacity=0.78, feather=0.22)
    # Djellaba hem widening at base
    _ellipse(arr, figure_cx, figure_cy - h * 0.04, w * 0.10, h * 0.06,
             DJELLABA_LIGHT, opacity=0.90, feather=0.18)
    # Djellaba hem left shadow
    _ellipse(arr, figure_cx - w * 0.04, figure_cy - h * 0.04, w * 0.048, h * 0.055,
             DJELLABA_SHADOW, opacity=0.72, feather=0.26)

    # Shoulders
    for sx_off, sh_col, sh_op in [
        (-w * 0.10, DJELLABA_SHADOW, 0.86),   # left shoulder in shadow
        (w * 0.10, DJELLABA_LIGHT, 0.90),     # right shoulder in sun
    ]:
        _ellipse(arr, figure_cx + sx_off, figure_cy - h * 0.36, w * 0.06, h * 0.04,
                 sh_col, opacity=sh_op, feather=0.20)

    # Neck (exposed skin)
    _ellipse(arr, figure_cx, figure_cy - h * 0.42, w * 0.035, h * 0.045,
             SKIN_TONE, opacity=0.90, feather=0.16)

    # Head: simplified flat plane
    head_r_w = w * 0.075
    head_r_h = h * 0.075
    head_y   = figure_cy - h * 0.51
    # Head mass (skin/warm ochre)
    _ellipse(arr, figure_cx, head_y, head_r_w, head_r_h,
             SKIN_TONE, opacity=0.88, feather=0.10)
    # Hair (dark flat plane covering top+back of head)
    _ellipse(arr, figure_cx, head_y - head_r_h * 0.35, head_r_w * 1.1, head_r_h * 0.85,
             DARK_HAIR, opacity=0.92, feather=0.10)
    # Headscarf (terracotta-warm)
    _ellipse(arr, figure_cx + head_r_w * 0.2, head_y - head_r_h * 0.20,
             head_r_w * 0.80, head_r_h * 0.55, TERRACOTTA, opacity=0.78, feather=0.22)

    # Terracotta water jar at right hip
    jar_cx = figure_cx + w * 0.10
    jar_cy = figure_cy - h * 0.20
    _ellipse(arr, jar_cx, jar_cy, w * 0.045, h * 0.075,
             TERRACOTTA, opacity=0.92, feather=0.10)
    # Jar rim
    _ellipse(arr, jar_cx, jar_cy - h * 0.075, w * 0.020, h * 0.018,
             DEEP_VIOLET, opacity=0.80, feather=0.20)
    # Jar highlight
    _ellipse(arr, jar_cx - w * 0.010, jar_cy - h * 0.012, w * 0.012, h * 0.020,
             WARM_WHITE, opacity=0.65, feather=0.35)
    # Arm carrying jar
    _line(arr, int(figure_cx + w * 0.06), int(figure_cy - h * 0.28),
          int(jar_cx - w * 0.010), int(jar_cy - h * 0.055),
          SKIN_TONE, thickness=4, opacity=0.78)

    # ── Ground shadow of figure ────────────────────────────────────────────────
    _ellipse(arr, figure_cx + w * 0.03, figure_cy + h * 0.01, w * 0.10, h * 0.020,
             DEEP_VIOLET, opacity=0.50, feather=0.45)

    # ── Final unifying sand floor foreground tone ──────────────────────────────
    # Foreground strip is warm golden sand -- flat plane
    _rect(arr, 0, h * 0.85, w, h, OCHRE, opacity=0.60)
    _rect(arr, 0, h * 0.92, w, h, CADMIUM_YELLOW, opacity=0.45)

    return arr


def main():
    print("Session 246 -- Marché à Tunis (August Macke Luminous Planes, 157th mode)")
    print("Canvas:", W, "x", H)

    ref = build_scene(W, H)
    ref_img = Image.fromarray((np.clip(ref, 0, 1) * 255).astype(np.uint8), "RGB")

    p = Painter(W, H)
    print("  1. Tone ground -- warm golden ochre (Macke's sun-bleached ground)")
    p.tone_ground((0.82, 0.66, 0.28), texture_strength=0.03)

    print("  2. Underpainting -- block in major colour planes")
    p.underpainting(ref_img, stroke_size=55)

    print("  3. Block in -- primary flat colour zones")
    p.block_in(ref_img, stroke_size=32, n_strokes=460)

    print("  4. Build form -- secondary plane definition")
    p.build_form(ref_img, stroke_size=18, n_strokes=360)

    print("  5. Place lights -- sunlit surface accents")
    p.place_lights(ref_img, stroke_size=8, n_strokes=220)

    print("  6. Macke Luminous Planes pass (157th mode)")
    p.macke_luminous_planes_pass(
        n_hue_zones=8,
        sat_target=0.84,
        sat_lift_str=0.68,
        hue_jump_bright=0.22,
        hue_jump_thresh=0.08,
        warm_r=0.96,
        warm_g=0.82,
        warm_b=0.40,
        veil_strength=0.18,
        opacity=0.82,
    )

    print("  7. Paint Golden Ground pass (session 246 improvement)")
    p.paint_golden_ground_pass(
        ground_r=0.76,
        ground_g=0.56,
        ground_b=0.22,
        midtone_str=0.26,
        shadow_thresh=0.30,
        shadow_ground_r=0.48,
        shadow_ground_g=0.28,
        shadow_ground_b=0.10,
        shadow_str=0.20,
        highlight_thresh=0.78,
        highlight_r=0.99,
        highlight_g=0.94,
        highlight_b=0.74,
        highlight_str=0.12,
        opacity=0.70,
    )

    print("  8. Final sheen pass")
    p.canvas.sheen_pass()

    out_path = "s246_macke_marche_a_tunis.png"
    p.save(out_path)
    print(f"  Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    main()
