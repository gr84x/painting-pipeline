"""
paint_s212_window_figure.py — Original composition: "The Window"

Session 212 painting — inspired by Piet Mondrian (1872–1944).

IMAGE DESCRIPTION
=================
Subject & Composition:
  A single human figure — a woman — seen entirely from behind, standing
  close to a tall, narrow window that occupies the centre-right of the
  canvas. She is slightly right of centre, vertical axis aligned with the
  window's central mullion. She faces the window, arms hanging loosely at
  her sides. Viewpoint is from slightly behind and slightly above her left
  shoulder, as if we are standing two metres back in a dim interior room.
  The composition has strong vertical tension: the window frame, her spine,
  and the distant building facade beyond the glass all create parallel
  vertical lines that echo and answer each other.

The Figure:
  The woman is of medium height, slight build, standing with a quality of
  stillness that suggests she has been here for some time — not waiting,
  not watching, simply existing in relation to the light. Her dark hair is
  pulled up at the nape of the neck with a few loose strands. She wears a
  simple long-sleeved dress of deep cobalt blue — the exact blue of
  Mondrian's primary palette — which falls to mid-calf. The fabric is
  plain with no ornamentation, fitting the neoplastic aesthetic. Her bare
  arms hang at her sides with a quality of quiet surrender. We cannot see
  her face. Her emotional state is one of deep, unresolved contemplation —
  the kind of stillness that has no outcome and needs none.

The Environment:
  The room she stands in is spare: plain off-white plaster walls with a
  warm cream ground, a single dark wooden floor that catches a rectangle of
  pale light from the window. The room is dim in the corners; it seems to
  recede into pure abstraction at the edges. The window itself is the source
  of all meaning: it is a tall, narrow casement window of the kind found in
  Amsterdam canal houses, divided by a thick black wooden frame into six
  panes — two columns of three panes each. The panes are clear glass, and
  through them we see the façade of a building across a narrow canal: red
  brick, warm and saturated, with rectangular windows arranged in a strict
  vertical-horizontal grid. Above the roofline, a pale winter sky of cool
  gray-white. The canal itself is just barely visible at the bottom — a
  strip of deep blue-gray water. Rain has just stopped; the brick is
  darkened with moisture and has an extra saturated warmth. The boundary
  between glass-pane and outdoor world is precise and rectangular — the
  window mullion at full black imposes Mondrian's grid on nature itself.
  Foreground: the floor reflects the window light as a sharp yellow
  rectangle — primary yellow — landing on the wooden boards at the woman's
  feet.

Technique & Palette:
  Piet Mondrian's Neoplastic Grid — the 123rd distinct mode:
  mondrian_neoplastic_grid_pass. The content-derived grid detection finds
  the strongest tonal seams in the composition (the window frame, the
  building edge, the horizon line) and snaps them to orthogonal black lines.
  Within the cells, regions are assigned to Mondrian's restricted palette:
  the cobalt dress maps to primary blue; the brick facade maps to primary
  red; the floor light-patch maps to primary yellow; the sky and wall areas
  map to white and gray. The result is a compositional translation of a
  real scene into neoplastic vocabulary — the woman herself becomes a blue
  vertical element in a grid of primaries.

  Palette:
    Primary red    (brick facade, warm):    (0.86, 0.08, 0.06)
    Primary yellow (floor light):           (0.97, 0.87, 0.02)
    Primary blue   (dress, canal water):    (0.01, 0.17, 0.54)
    White          (sky, plaster walls):    (0.94, 0.92, 0.88)
    Gray           (window glass shadow):   (0.72, 0.72, 0.72)
    Black          (window frame, grid):    (0.06, 0.06, 0.08)

Mood & Intent:
  The painting asks whether abstraction is an escape from the world or a
  deeper form of seeing it. Mondrian believed that nature's underlying
  structure — the pure vertical and horizontal tensions of force and
  counter-force — was more true than its surface appearance. The woman at
  the window is looking through a grid at a world that is already a grid.
  The viewer should feel the cold dry air of a Dutch winter morning, the
  comfort of an interior, and underneath it all, the vertiginous sense that
  the world beyond the glass has been simplified into exactly what it
  essentially is: a composition of rectangles, primaries, and black lines.
  Contemplation, clarity, and the quiet melancholy of precision.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter
from art_catalog import get_style

W, H = 540, 780


def build_window_figure_reference(w: int, h: int) -> Image.Image:
    """
    Synthetic reference for the window figure composition.
    Off-white interior room, woman in cobalt blue, tall window
    looking onto Amsterdam brick facade at dawn.
    """
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None] * np.ones((1, w), dtype=np.float32)
    xx = np.ones((h, 1), dtype=np.float32) * np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]

    def _blend(base, colour, alpha):
        a = np.clip(alpha[:, :, None], 0.0, 1.0)
        return base * (1.0 - a) + colour[None, None, :] * a

    # ── Interior room base — warm off-white plaster ───────────────────────────
    wall_col = np.array([0.91, 0.88, 0.80], dtype=np.float32)
    arr = np.ones((h, w, 3), dtype=np.float32) * wall_col[None, None, :]

    # Corners and edges are slightly darker (dim interior)
    corner_dark = ((xx - 0.5) ** 2 + (yy - 0.5) ** 2) * 0.22
    arr = _blend(arr, np.array([0.60, 0.56, 0.50], dtype=np.float32), corner_dark)

    # ── Floor — dark wooden boards ────────────────────────────────────────────
    floor_y = 0.72   # floor starts 72% down
    floor_mask = np.clip((yy - floor_y) / 0.04, 0.0, 1.0)
    floor_col = np.array([0.28, 0.22, 0.14], dtype=np.float32)
    arr = _blend(arr, floor_col, floor_mask * 0.88)

    # Floor boards — faint horizontal lines
    for board_y in np.linspace(floor_y + 0.04, 1.0, 12):
        bd = np.abs(yy - board_y) / 0.003
        ba = np.clip(1.0 - bd, 0.0, 1.0) ** 2 * 0.25
        arr = _blend(arr, np.array([0.18, 0.14, 0.09], dtype=np.float32), ba * floor_mask)

    # ── Window light patch on floor — primary yellow ──────────────────────────
    win_left_x  = 0.48
    win_right_x = 0.72
    win_light_y = floor_y
    win_light_bottom = min(1.0, floor_y + 0.24)
    light_x_mask = np.clip(
        (1.0 - np.abs(xx - (win_left_x + win_right_x) * 0.5) /
         ((win_right_x - win_left_x) * 0.5)), 0.0, 1.0
    )
    light_y_mask = np.clip((yy - win_light_y) / 0.04, 0.0, 1.0) * \
                   np.clip((win_light_bottom - yy) / 0.06, 0.0, 1.0)
    light_a = light_x_mask * light_y_mask * 0.70
    arr = _blend(arr, np.array([0.97, 0.87, 0.02], dtype=np.float32), light_a)

    # ── Window area — tall casement window centre-right ───────────────────────
    win_top_y   = 0.04
    win_bot_y   = floor_y
    win_w       = win_right_x - win_left_x
    win_h_frac  = win_bot_y - win_top_y

    # Glass panes — sky at top (pale gray-white), brick facade mid/lower
    # Canal strip at very bottom of window
    sky_col  = np.array([0.88, 0.88, 0.85], dtype=np.float32)
    brick_col = np.array([0.70, 0.22, 0.10], dtype=np.float32)
    canal_col = np.array([0.14, 0.24, 0.40], dtype=np.float32)

    sky_frac    = 0.18   # top 18% of window height = sky
    canal_frac  = 0.10   # bottom 10% of window height = canal

    inside_win_x = (xx >= win_left_x) & (xx <= win_right_x)
    inside_win_y = (yy >= win_top_y)  & (yy <= win_bot_y)
    inside_win   = inside_win_x & inside_win_y

    # Normalised y within window [0=top, 1=bottom]
    t_win_y = np.clip((yy - win_top_y) / win_h_frac, 0.0, 1.0)

    # Sky region (top of window)
    sky_a = np.clip(1.0 - (t_win_y - sky_frac) / 0.03, 0.0, 1.0) * inside_win.astype(np.float32)
    arr = _blend(arr, sky_col, sky_a)

    # Brick facade (middle/main portion)
    brick_lo = sky_frac
    brick_hi = 1.0 - canal_frac
    brick_a  = (
        np.clip((t_win_y - brick_lo) / 0.04, 0.0, 1.0) *
        np.clip((brick_hi - t_win_y) / 0.04, 0.0, 1.0) *
        inside_win.astype(np.float32)
    )
    arr = _blend(arr, brick_col, brick_a * 0.90)

    # Brick texture — vertical mortar lines
    for bx in np.linspace(win_left_x + 0.02, win_right_x - 0.02, 14):
        bxd = np.abs(xx - bx) / 0.003
        bxa = np.clip(1.0 - bxd, 0.0, 1.0) ** 2 * 0.22 * brick_a
        arr = _blend(arr, np.array([0.48, 0.14, 0.07], dtype=np.float32), bxa)

    # Horizontal mortar lines
    for by_t in np.linspace(sky_frac + 0.06, brick_hi - 0.04, 10):
        by = win_top_y + by_t * win_h_frac
        byd = np.abs(yy - by) / 0.004
        bya = np.clip(1.0 - byd, 0.0, 1.0) ** 2 * 0.18 * inside_win.astype(np.float32)
        arr = _blend(arr, np.array([0.50, 0.16, 0.08], dtype=np.float32), bya)

    # Building windows (in brick facade) — darker rectangles
    for bwin_x, bwin_y_t, bwin_w, bwin_h in [
        (0.53, 0.32, 0.045, 0.12),
        (0.65, 0.32, 0.045, 0.12),
        (0.53, 0.55, 0.045, 0.12),
        (0.65, 0.55, 0.045, 0.12),
    ]:
        bwin_y = win_top_y + bwin_y_t * win_h_frac
        bx_d = np.abs(xx - bwin_x) / (bwin_w * 0.5)
        by_d = np.abs(yy - bwin_y) / (bwin_h * 0.5)
        bw_a = np.clip(1.0 - np.maximum(bx_d, by_d), 0.0, 1.0) * inside_win.astype(np.float32) * brick_a
        arr = _blend(arr, np.array([0.06, 0.10, 0.16], dtype=np.float32), bw_a)

    # Canal strip
    canal_a = (
        np.clip((t_win_y - (1.0 - canal_frac)) / 0.02, 0.0, 1.0) *
        inside_win.astype(np.float32)
    )
    arr = _blend(arr, canal_col, canal_a * 0.85)

    # ── Window frame — thick black mullions ───────────────────────────────────
    frame_w   = 0.010   # side frame thickness in canvas fraction
    mullion_w = 0.008   # vertical mullion
    crossbar_h = 0.005  # horizontal crossbar

    def _frame_line_x(cx, fw):
        return np.clip(1.0 - np.abs(xx - cx) / fw, 0.0, 1.0)

    def _frame_line_y(cy, fh):
        return np.clip(1.0 - np.abs(yy - cy) / fh, 0.0, 1.0)

    frame_black = np.array([0.06, 0.06, 0.08], dtype=np.float32)

    # Left and right frame edges
    for fx in [win_left_x, win_right_x]:
        fa = _frame_line_x(fx, frame_w) * inside_win_y.astype(np.float32)
        arr = _blend(arr, frame_black, fa)

    # Top and bottom frame edges
    for fy in [win_top_y, win_bot_y]:
        fa = _frame_line_y(fy, crossbar_h) * inside_win_x.astype(np.float32)
        arr = _blend(arr, frame_black, fa)

    # Central vertical mullion
    win_mid_x = (win_left_x + win_right_x) * 0.50
    fa = _frame_line_x(win_mid_x, mullion_w) * inside_win_y.astype(np.float32)
    arr = _blend(arr, frame_black, fa)

    # Three horizontal crossbars (dividing into 3 rows of panes)
    for t_y in [0.33, 0.66]:
        fy = win_top_y + t_y * win_h_frac
        fa = _frame_line_y(fy, crossbar_h) * inside_win_x.astype(np.float32)
        arr = _blend(arr, frame_black, fa)

    # ── Woman figure — cobalt blue dress, seen from behind ────────────────────
    fig_cx = win_left_x - 0.07   # slightly left of window's left edge
    fig_top_y = 0.14
    fig_bot_y = floor_y

    # Dress body (main torso + skirt)
    body_col = np.array([0.01, 0.17, 0.54], dtype=np.float32)   # primary blue

    # Torso (upper body)
    torso_cx = fig_cx
    torso_cy = fig_top_y + (floor_y - fig_top_y) * 0.30
    torso_rx = 0.040
    torso_ry = 0.120
    td = ((xx - torso_cx) / torso_rx) ** 2 + ((yy - torso_cy) / torso_ry) ** 2
    ta = np.clip(1.30 - td, 0.0, 1.0) ** 0.55
    arr = _blend(arr, body_col, ta * 0.94)

    # Skirt (wider, flares gently)
    skirt_cy = floor_y - 0.10
    skirt_rx = 0.052
    skirt_ry = 0.135
    sd = ((xx - fig_cx) / skirt_rx) ** 2 + ((yy - skirt_cy) / skirt_ry) ** 2
    sa = np.clip(1.20 - sd, 0.0, 1.0) ** 0.50
    arr = _blend(arr, body_col, sa * 0.93)

    # Hem edge — slightly lighter at the very bottom of dress
    hem_cy = floor_y - 0.01
    hem_d  = np.abs(yy - hem_cy) / 0.012
    hem_a  = np.clip(1.0 - hem_d, 0.0, 1.0) ** 1.4 * \
             np.clip(1.0 - np.abs(xx - fig_cx) / skirt_rx, 0.0, 1.0) * 0.35
    arr = _blend(arr, np.array([0.10, 0.28, 0.65], dtype=np.float32), hem_a)

    # Arms — bare, hanging at sides
    arm_col = np.array([0.82, 0.66, 0.54], dtype=np.float32)   # warm skin
    for arm_ox, arm_tilt in [(-0.042, 0.004), (0.044, -0.004)]:
        for frac in np.linspace(0.0, 1.0, 70):
            ax = fig_cx + arm_ox + arm_tilt * frac
            ay = torso_cy + torso_ry * 0.65 + frac * 0.130
            aw = 0.013 * (1.0 - frac * 0.25)
            ad = ((xx - ax) / aw) ** 2 + ((yy - ay) / (aw * 2.2)) ** 2
            aa = np.clip(1.0 - ad, 0.0, 1.0) ** 0.75
            arr = _blend(arr, arm_col, aa * 0.88)

    # ── Head and hair ─────────────────────────────────────────────────────────
    head_cx = fig_cx - 0.004
    head_cy = fig_top_y + 0.06
    head_rx = 0.032
    head_ry = 0.040
    hd = ((xx - head_cx) / head_rx) ** 2 + ((yy - head_cy) / head_ry) ** 2
    ha = np.clip(1.25 - hd, 0.0, 1.0) ** 0.60
    arr = _blend(arr, arm_col, ha * 0.90)

    # Hair — dark, pulled up
    hair_col = np.array([0.14, 0.10, 0.08], dtype=np.float32)
    hh_d = ((xx - head_cx) / 0.030) ** 2 + ((yy - (head_cy - head_ry * 0.30)) / 0.020) ** 2
    hh_a = np.clip(0.85 - hh_d, 0.0, 1.0) ** 1.0 * ha
    arr = _blend(arr, hair_col, hh_a)

    # Hair bun at nape
    bun_d = ((xx - (head_cx + 0.010)) / 0.018) ** 2 + ((yy - (head_cy + 0.022)) / 0.016) ** 2
    bun_a = np.clip(0.90 - bun_d, 0.0, 1.0) ** 1.2 * 0.80
    arr = _blend(arr, hair_col, bun_a)

    # Neckline
    neck_d = ((xx - head_cx) / 0.015) ** 2 + ((yy - (head_cy + head_ry * 0.85)) / 0.022) ** 2
    neck_a = np.clip(1.0 - neck_d, 0.0, 1.0) ** 0.8
    arr = _blend(arr, arm_col, neck_a * 0.80)

    # ── Final adjustments ─────────────────────────────────────────────────────
    arr = np.clip(arr, 0.0, 1.0)
    arr_uint8 = (arr * 255).astype(np.uint8)
    img = Image.fromarray(arr_uint8, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(2.5))
    return img


def paint(output_path: str = "s212_window_figure.png") -> str:
    """
    Paint 'The Window' — woman in cobalt blue looking at Amsterdam brick facade.
    Piet Mondrian neoplastic grid decomposition: 123rd mode.
    """
    print("=" * 64)
    print("  Session 212 — 'The Window'")
    print("  Woman in cobalt blue at casement window, Amsterdam canal facade")
    print("  Technique: Piet Mondrian Neoplastic Grid Decomposition")
    print("  123rd mode: mondrian_neoplastic_grid_pass")
    print("=" * 64)

    ref_img = build_window_figure_reference(W, H)
    ref_arr = np.array(ref_img, dtype=np.float32) / 255.0
    print(f"  Reference built  ({W}x{H})")

    mondrian = get_style("piet_mondrian")
    p = Painter(W, H)

    # White/off-white ground — Mondrian's raw canvas foundation
    print("  [1] Tone ground — white ground ...")
    p.tone_ground(mondrian.ground_color, texture_strength=0.03)

    print("  [2] Underpainting ...")
    p.underpainting(ref_img, stroke_size=28, n_strokes=1800)

    print("  [3] Block in — broad colour planes ...")
    p.block_in(ref_img, stroke_size=18, n_strokes=2200)

    print("  [4] Build form ...")
    p.build_form(ref_img, stroke_size=9, n_strokes=2800)

    print("  [5] Place lights ...")
    p.place_lights(ref_img, stroke_size=5, n_strokes=280)

    # ── Mondrian signature pass — neoplastic grid decomposition ───────────────
    print("  [6] mondrian_neoplastic_grid_pass (123rd mode) ...")
    p.mondrian_neoplastic_grid_pass(
        h_lines=4,
        v_lines=5,
        line_width=5,
        grid_strength=0.82,
        opacity=0.78,
    )

    # Crisp edge definition — after grid pass to reinforce structure
    print("  [7] Edge definition ...")
    p.edge_definition_pass(opacity=0.22)

    print("  [8] Finish (vignette only) ...")
    p.finish(vignette=0.18, crackle=False)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    out = paint()
    print(f"\n  Done: {out}")
