"""paint_s245.py -- Session 245: The Mystic at Prayer (Alexej von Jawlensky Abstract Head, 156th mode)."""
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
from stroke_engine import Painter

W, H = 500, 660

# Jawlensky palette
HOT_AMBER        = (0.88, 0.62, 0.14)   # inner face warmth
DEEP_ORANGE      = (0.86, 0.36, 0.12)   # mid-face
ROSE_VIOLET      = (0.72, 0.18, 0.44)   # cheek / brow warmth
DEEP_COBALT      = (0.14, 0.24, 0.68)   # cool outer zones
ACID_OLIVE       = (0.26, 0.50, 0.18)   # peripheral accent
ULTRAMARINE_DARK = (0.08, 0.10, 0.38)   # thick contour lines
WARM_IVORY       = (0.94, 0.90, 0.82)   # inner highlight
DEEP_VIOLET      = (0.36, 0.14, 0.54)   # outer shadow field
SAFFRON          = (0.92, 0.74, 0.10)   # face crown
WARM_GOLD        = (0.82, 0.58, 0.10)   # forehead glow
COOL_TEAL        = (0.12, 0.42, 0.50)   # outer teal accent
NEAR_BLACK       = (0.07, 0.06, 0.08)   # ground / background


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


def _radial_gradient(arr, cx, cy, r_inner, r_outer, col_inner, col_outer):
    """Fill a radial gradient from col_inner at r_inner to col_outer at r_outer."""
    h, w = arr.shape[:2]
    ci = np.array(col_inner, dtype=np.float32)
    co = np.array(col_outer, dtype=np.float32)
    for dy in range(-int(r_outer * 1.1), int(r_outer * 1.1) + 1):
        for dx in range(-int(r_outer * 1.1), int(r_outer * 1.1) + 1):
            px, py = int(cx + dx), int(cy + dy)
            if 0 <= px < w and 0 <= py < h:
                d = math.sqrt(dx * dx + dy * dy)
                if d <= r_outer:
                    if d <= r_inner:
                        t = 0.0
                    else:
                        t = (d - r_inner) / (r_outer - r_inner + 1e-6)
                    t = max(0.0, min(1.0, t))
                    arr[py, px] = ci * (1.0 - t) + co * t


def _gradient_row(arr, y0, y1, col_top, col_bot):
    h, w = arr.shape[:2]
    y0i, y1i = max(0, int(y0)), min(h, int(y1))
    span = max(y1i - y0i, 1)
    for y in range(y0i, y1i):
        t = (y - y0i) / span
        c = np.array(col_top, dtype=np.float32) * (1.0 - t) + np.array(col_bot, dtype=np.float32) * t
        arr[y, :] = _blend(arr[y, :], c, 1.0)


def build_scene(w, h):
    arr = np.zeros((h, w, 3), dtype=np.float32)

    # ── Background: concentric colour fields -- Jawlensky icon-like ────────────
    # Deep cobalt-violet outer field (the void / infinite dark)
    _gradient_row(arr, 0, h, DEEP_VIOLET, NEAR_BLACK)

    # Cobalt blue mid outer ring
    face_cx, face_cy = w * 0.50, h * 0.42
    _radial_gradient(arr, face_cx, face_cy,
                     r_inner=int(h * 0.50), r_outer=int(h * 0.75),
                     col_inner=DEEP_COBALT, col_outer=DEEP_VIOLET)

    # Cool teal transitional zone just outside face
    _radial_gradient(arr, face_cx, face_cy,
                     r_inner=int(h * 0.36), r_outer=int(h * 0.52),
                     col_inner=COOL_TEAL, col_outer=DEEP_COBALT)

    # ── Head/face: simplified iconic form ─────────────────────────────────────
    # Cranium -- outer warm gold dome
    _ellipse(arr, face_cx, face_cy - h * 0.06, w * 0.34, h * 0.42,
             WARM_GOLD, opacity=0.96, feather=0.08)

    # Inner face -- hot amber centre (the radiant spiritual warmth)
    _radial_gradient(arr, face_cx, face_cy + h * 0.02,
                     r_inner=int(h * 0.12), r_outer=int(h * 0.30),
                     col_inner=HOT_AMBER, col_outer=DEEP_ORANGE)

    # Forehead saffron crown glow
    _ellipse(arr, face_cx, face_cy - h * 0.14, w * 0.28, h * 0.18,
             SAFFRON, opacity=0.88, feather=0.18)

    # Cheek blush: rose-violet flush
    for ex, ey in [(-w * 0.18, h * 0.05), (w * 0.18, h * 0.05)]:
        _ellipse(arr, face_cx + ex, face_cy + ey, w * 0.10, h * 0.08,
                 ROSE_VIOLET, opacity=0.72, feather=0.35)

    # ── Eyes: closed, downcast, in prayer ─────────────────────────────────────
    for ex_off in [-w * 0.12, w * 0.12]:
        ey_center = face_cy + h * 0.01
        ex_center = face_cx + ex_off
        # Upper lid mass (dark closed lid)
        _ellipse(arr, ex_center, ey_center, w * 0.08, h * 0.025,
                 ULTRAMARINE_DARK, opacity=0.92, feather=0.12)
        # Lower lid lighter rim
        _ellipse(arr, ex_center, ey_center + h * 0.015, w * 0.07, h * 0.012,
                 HOT_AMBER, opacity=0.55, feather=0.22)
        # Heavy eyelid contour line
        _line(arr, int(ex_center - w * 0.09), int(ey_center - h * 0.008),
              int(ex_center + w * 0.09), int(ey_center - h * 0.008),
              ULTRAMARINE_DARK, thickness=3, opacity=0.90)

    # ── Nose: simplified vertical band ────────────────────────────────────────
    nose_top = face_cy + h * 0.04
    nose_bot = face_cy + h * 0.13
    # Central warm ridge
    _rect(arr, face_cx - w * 0.025, nose_top, face_cx + w * 0.025, nose_bot,
          DEEP_ORANGE, 0.80)
    # Nostril flares -- ultramarine dark
    _ellipse(arr, face_cx - w * 0.04, nose_bot, w * 0.028, h * 0.018,
             ULTRAMARINE_DARK, opacity=0.88, feather=0.14)
    _ellipse(arr, face_cx + w * 0.04, nose_bot, w * 0.028, h * 0.018,
             ULTRAMARINE_DARK, opacity=0.88, feather=0.14)

    # ── Mouth: closed, serene, barely parted ──────────────────────────────────
    mouth_y = face_cy + h * 0.20
    _ellipse(arr, face_cx, mouth_y, w * 0.12, h * 0.022,
             ROSE_VIOLET, opacity=0.85, feather=0.18)
    # Upper lip contour
    _line(arr, int(face_cx - w * 0.12), int(mouth_y - h * 0.012),
          int(face_cx + w * 0.12), int(mouth_y - h * 0.012),
          ULTRAMARINE_DARK, thickness=2, opacity=0.82)
    # Lower lip shadow
    _line(arr, int(face_cx - w * 0.10), int(mouth_y + h * 0.014),
          int(face_cx + w * 0.10), int(mouth_y + h * 0.014),
          ULTRAMARINE_DARK, thickness=2, opacity=0.70)

    # ── Beard: deep warm ochre flowing downward ────────────────────────────────
    beard_cx, beard_top = face_cx, mouth_y + h * 0.02
    _ellipse(arr, beard_cx, beard_top + h * 0.08, w * 0.22, h * 0.14,
             DEEP_ORANGE, opacity=0.90, feather=0.16)
    # Beard lower mass fades into violet
    _ellipse(arr, beard_cx, beard_top + h * 0.15, w * 0.18, h * 0.10,
             ROSE_VIOLET, opacity=0.72, feather=0.22)
    # Central highlight of beard
    _ellipse(arr, beard_cx, beard_top + h * 0.08, w * 0.10, h * 0.06,
             WARM_IVORY, opacity=0.38, feather=0.40)

    # ── Hair and head crown ────────────────────────────────────────────────────
    # Hair mass both sides -- deep cobalt blue
    for side_x in [face_cx - w * 0.30, face_cx + w * 0.30]:
        _ellipse(arr, side_x, face_cy - h * 0.06, w * 0.10, h * 0.25,
                 DEEP_COBALT, opacity=0.92, feather=0.14)
    # Crown centre warmth
    _ellipse(arr, face_cx, face_cy - h * 0.38, w * 0.20, h * 0.10,
             SAFFRON, opacity=0.80, feather=0.22)

    # ── Neck and collar ────────────────────────────────────────────────────────
    neck_top = face_cy + h * 0.28
    neck_bot = face_cy + h * 0.42
    _rect(arr, face_cx - w * 0.08, neck_top, face_cx + w * 0.08, neck_bot,
          DEEP_ORANGE, 0.88)
    # Collar -- cool acid olive band
    _rect(arr, face_cx - w * 0.25, neck_bot - h * 0.01, face_cx + w * 0.25, neck_bot + h * 0.04,
          ACID_OLIVE, 0.82)
    # Shoulder masses
    _ellipse(arr, face_cx, neck_bot + h * 0.08, w * 0.40, h * 0.10,
             DEEP_COBALT, opacity=0.88, feather=0.14)

    # ── Radiant inner aura: warm ivory inner glow around face ─────────────────
    _radial_gradient(arr, face_cx, face_cy,
                     r_inner=0, r_outer=int(h * 0.28),
                     col_inner=WARM_IVORY, col_outer=HOT_AMBER)
    # Blend this glow very softly over existing face (low opacity, feathered)
    # (already baked into the radial gradient above at low intensity)

    # ── Ultramarine contour reinforcement: head outline ────────────────────────
    # Head border
    for r_off in range(4):
        _ellipse(arr, face_cx, face_cy - h * 0.06,
                 w * 0.34 + r_off, h * 0.42 + r_off,
                 ULTRAMARINE_DARK, opacity=0.06, feather=0.50)
    # Neck contour lines
    _line(arr, int(face_cx - w * 0.08), int(neck_top),
          int(face_cx - w * 0.08), int(neck_bot),
          ULTRAMARINE_DARK, thickness=3, opacity=0.80)
    _line(arr, int(face_cx + w * 0.08), int(neck_top),
          int(face_cx + w * 0.08), int(neck_bot),
          ULTRAMARINE_DARK, thickness=3, opacity=0.80)

    # ── Subtle background abstract bands (Jawlensky near-vertical colour zones) ─
    band_colors = [DEEP_VIOLET, DEEP_COBALT, COOL_TEAL, DEEP_COBALT, DEEP_VIOLET]
    band_w = w / len(band_colors)
    for i, bc in enumerate(band_colors):
        _rect(arr, i * band_w, 0, (i + 1) * band_w, h, bc, 0.18)

    return arr


def main():
    print("Session 245 -- The Mystic at Prayer (Alexej von Jawlensky Abstract Head)")
    print("Canvas:", W, "x", H)

    ref = build_scene(W, H)
    ref_img = Image.fromarray((np.clip(ref, 0, 1) * 255).astype(np.uint8), "RGB")

    p = Painter(W, H)
    print("  1. Tone ground -- deep violet-umber")
    p.tone_ground((0.16, 0.14, 0.10), texture_strength=0.04)

    print("  2. Underpainting -- block in major masses")
    p.underpainting(ref_img, stroke_size=50)

    print("  3. Block in -- primary colour planes")
    p.block_in(ref_img, stroke_size=30, n_strokes=440)

    print("  4. Build form -- secondary modelling")
    p.build_form(ref_img, stroke_size=16, n_strokes=340)

    print("  5. Place lights -- inner warmth highlights")
    p.place_lights(ref_img, stroke_size=7, n_strokes=200)

    print("  6. Jawlensky Abstract Head pass (156th mode)")
    p.jawlensky_abstract_head_pass(
        inner_radius=0.38,
        outer_radius=0.58,
        warm_hue=35.0,
        cool_hue=228.0,
        warmth_str=0.52,
        cool_str=0.46,
        cool_sat_lift=0.10,
        cool_val_lift=0.05,
        edge_thresh=0.09,
        edge_blue_r=0.08,
        edge_blue_g=0.10,
        edge_blue_b=0.38,
        edge_snap=0.74,
        opacity=0.82,
    )

    print("  7. Paint Optical Vibration pass (session 245 improvement)")
    p.paint_optical_vibration_pass(
        boundary_sigma=9.0,
        diverge_str=0.32,
        vibration_str=0.26,
        warm_anchor=28.0,
        cool_anchor=212.0,
        opacity=0.68,
    )

    print("  8. Final sheen pass")
    p.canvas.sheen_pass()

    out_path = "s245_jawlensky_mystic_at_prayer.png"
    p.save(out_path)
    print(f"  Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    main()
