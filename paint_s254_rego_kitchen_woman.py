"""
paint_s254_rego_kitchen_woman.py -- Session 254

"Woman at Kitchen Table" -- after Paula Rego

Image Description
-----------------
Subject & Composition
    A stout woman seated squarely at a kitchen table, viewed from a slightly
    elevated angle -- as if the viewer is standing while she is seated. She
    faces directly forward, head tilted slightly right, filling the lower
    two-thirds of the canvas. The table occupies the foreground, its edge
    running across the lower quarter of the frame. A large, amber-eyed
    tabby cat sits on the table to her left, facing the same direction as
    the woman -- both pairs of eyes, human and animal, look directly at
    the viewer. The composition is deliberately frontal, claustrophobic,
    pressing the figure against the picture plane.

The Figure
    The woman is broad-shouldered, heavy-handed, in her fifties. She wears
    a dark green dress with a white collar. Her hands rest flat on the table
    in front of a white ceramic cup -- her right hand open, relaxed; her
    left hand closed in a loose fist. Her face is broad, with high cheekbones
    and a set jaw; her expression is neither hostile nor welcoming -- it is
    watchful, deliberate, the face of someone who has absorbed the weight
    of many things and released none of them. Her dark hair is pulled back.
    Emotional state: contained power, patience worn to its exact edge, quiet
    authority. Not angry. Not sad. Fully present, waiting.

    The cat is large, solidly built, with a round face and pale-gold eyes.
    It sits in the classic loaf position, paws tucked, tail curled around
    its left flank. Its fur is warm ochre-brown with darker tabby stripes.
    Emotional state: total self-possession, indifference and alertness
    simultaneously -- very Rego-like.

The Environment
    The kitchen is stark and close. Behind the woman: a flat dark-green
    painted wall fills the upper half of the canvas; a single high window
    at the upper right admits a cold grey exterior light that does not warm
    the room. The table surface is plain pale wood -- scrubbed, dry, slightly
    worn at the edges. A second chair is visible at the table's far right,
    its back just visible at the canvas edge, empty. The boundaries between
    the wall, table, and chair are hard-edged, unblended -- flat planes
    described with the directness of a woodcut. No decorative objects.
    No softening. The space is real, ordinary, without romance.

Technique & Palette
    Paula Rego Flat Figure mode -- session 254, 165th distinct mode.

    Stage 1, TONAL ZONE POSTERISATION: n_levels=7, zone_blend=0.68.
    Colours are reduced to flat tonal zones in the manner of Rego's pastel:
    the dark green wall, the warm flesh tones, the deep shadow in the figure's
    dress become unified areas rather than continuously modelled forms. The
    zone_blend=0.68 preserves the organic warmth of hand-mixed pastel zones
    without digital harshness.

    Stage 2, WARM CONTOUR OUTLINING: contour_threshold=0.06,
    contour_strength=0.62, contour_px=2, outline_tone=(0.14, 0.09, 0.06).
    The heavy warm-brown outline defines the woman's silhouette against the
    wall, the cat against the table, the cup against the tablecloth. These
    are not atmospheric softened edges -- they are drawn boundaries, direct
    and unequivocal.

    Stage 3, CHROMATIC ZONE TENSION: tension_warm=(0.68, 0.48, 0.28),
    tension_cool=(0.36, 0.46, 0.58), tension_strength=0.10. The woman and
    cat (figure quadrants) are pushed very slightly warmer; the wall and
    table edge (ground quadrants) slightly cooler. This establishes the
    psychological separation between animate and inanimate without visible
    colour-shifting.

    Contour Weight improvement (session 254): contour_threshold=0.05,
    max_weight=0.50, weight_exponent=1.2, junction_boost=0.18,
    taper_strength=0.32. The secondary contour pass thickens junctions (where
    the woman's arm meets the table edge, where the cat meets the background)
    and tapers the lines toward their endpoints, giving the drawing the
    specificity of a careful hand.

    Palette: Wall dark green (0.22/0.38/0.22) -- Dress shadow (0.20/0.26/0.20)
    -- Dress mid (0.28/0.40/0.28) -- Flesh warm (0.74/0.54/0.40) --
    Flesh shadow (0.52/0.34/0.24) -- Cat ochre (0.76/0.60/0.32) --
    Cat stripe dark (0.40/0.30/0.18) -- Table pale (0.82/0.76/0.62) --
    Cup white (0.90/0.88/0.84) -- Window cool (0.60/0.66/0.74) --
    Deep shadow (0.18/0.14/0.12)

Mood & Intent
    This is a painting in Rego's mode of domestic confrontation: the kitchen
    as a space of female power, endurance, and ambiguity. The woman is not
    threatening but she is not subordinate either. She has sat at this table
    a thousand times and will sit here a thousand more. The cat beside her
    doubles her quality of watchful self-possession. The viewer feels
    observed, measured, found neither sufficient nor insufficient -- simply
    noted. The cold grey light from the window suggests a morning before
    warmth arrives, before the day's demands. The painting is still. It does
    not explain itself. That is its authority.
"""

import sys
import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stroke_engine import Painter

W, H = 1000, 900
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "s254_rego_kitchen_woman.png")

rng = random.Random(254)


def build_kitchen_woman_reference(w, h):
    """Build reference image: woman at kitchen table with cat."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)

    # ── Background: dark green wall ────────────────────────────────────────
    wall_green = np.array([50, 75, 52], dtype=np.uint8)
    arr[:int(h * 0.65), :] = wall_green

    # ── High window (upper right) -- cold grey exterior light ──────────────
    win_x0, win_y0 = int(w * 0.68), int(h * 0.04)
    win_x1, win_y1 = int(w * 0.88), int(h * 0.28)
    for y in range(win_y0, win_y1):
        for x in range(win_x0, win_x1):
            t_y = (y - win_y0) / float(win_y1 - win_y0)
            t_x = (x - win_x0) / float(win_x1 - win_x0)
            # Cold pale grey-blue light
            light = np.array([192, 198, 208], dtype=float)
            frame_dark = np.array([50, 75, 52], dtype=float)
            # Window pane (interior 80%)
            if 0.08 < t_x < 0.92 and 0.08 < t_y < 0.92:
                frac = 0.88 - 0.15 * t_y
                col = (light * frac + frame_dark * (1.0 - frac)).astype(np.uint8)
            else:
                col = np.array([40, 55, 42], dtype=np.uint8)  # window frame
            arr[y, x] = col

    # ── Table surface: pale scrubbed wood ──────────────────────────────────
    table_y = int(h * 0.72)
    table_pale = np.array([210, 196, 168], dtype=np.uint8)
    table_warm = np.array([195, 178, 148], dtype=np.uint8)
    for y in range(table_y, h):
        depth = (y - table_y) / float(h - table_y)
        col = (table_pale.astype(float) * (1.0 - depth * 0.25) +
               table_warm.astype(float) * depth * 0.25).astype(np.uint8)
        arr[y, :] = col

    # ── Table edge shadow line ─────────────────────────────────────────────
    for y in range(table_y, table_y + 8):
        t = (y - table_y) / 8.0
        arr[y, :] = (np.array([40, 35, 28], dtype=float) * (1.0 - t) +
                     arr[y, :].astype(float) * t).astype(np.uint8)

    # ── Woman's dress: dark green with body mass ───────────────────────────
    # Body region: from table edge up to neck
    body_x0, body_x1 = int(w * 0.18), int(w * 0.78)
    body_y0, body_y1 = int(h * 0.38), table_y + 4
    for y in range(body_y0, body_y1):
        depth = (y - body_y0) / float(body_y1 - body_y0)
        width_frac = 0.55 + 0.20 * depth  # wider at bottom (lap/hips)
        cx = w // 2
        hw = int((body_x1 - body_x0) * width_frac / 2)
        x0 = max(0, cx - hw)
        x1 = min(w, cx + hw)
        # Dress colour: dark green, shadowed at sides
        for x in range(x0, x1):
            dist_center = abs(x - cx) / float(hw + 1)
            shadow_t = dist_center ** 1.6
            dress_light = np.array([60, 88, 60], dtype=float)
            dress_dark  = np.array([28, 40, 28], dtype=float)
            col = (dress_light * (1.0 - shadow_t) + dress_dark * shadow_t).astype(np.uint8)
            arr[y, x] = col

    # ── White collar ───────────────────────────────────────────────────────
    collar_y0, collar_y1 = int(h * 0.37), int(h * 0.43)
    collar_x0, collar_x1 = int(w * 0.36), int(w * 0.64)
    for y in range(collar_y0, collar_y1):
        for x in range(collar_x0, collar_x1):
            dist_c = abs(x - w // 2) / float((collar_x1 - collar_x0) // 2)
            if dist_c < 0.85:
                arr[y, x] = np.array([228, 222, 212], dtype=np.uint8)

    # ── Head and neck ──────────────────────────────────────────────────────
    head_cx  = int(w * 0.48)
    head_cy  = int(h * 0.22)
    head_rx  = int(w * 0.14)
    head_ry  = int(h * 0.17)
    # Neck
    neck_x0, neck_x1 = int(w * 0.43), int(w * 0.53)
    neck_y0, neck_y1 = int(h * 0.35), collar_y0 + 4
    for y in range(neck_y0, neck_y1):
        for x in range(neck_x0, neck_x1):
            arr[y, x] = np.array([190, 138, 98], dtype=np.uint8)

    # Head (ellipse)
    for y in range(head_cy - head_ry, head_cy + head_ry):
        for x in range(head_cx - head_rx, head_cx + head_rx):
            if 0 <= y < h and 0 <= x < w:
                dy = (y - head_cy) / float(head_ry)
                dx = (x - head_cx) / float(head_rx)
                if dx * dx + dy * dy <= 1.0:
                    # Flesh tone, shadowed at sides
                    shadow = (abs(dx) ** 1.4) * 0.5
                    flesh_light = np.array([210, 158, 110], dtype=float)
                    flesh_dark  = np.array([150, 100, 70], dtype=float)
                    col = (flesh_light * (1.0 - shadow) + flesh_dark * shadow).astype(np.uint8)
                    arr[y, x] = col

    # Hair: dark pulled back
    hair_y = head_cy - int(head_ry * 0.55)
    for y in range(head_cy - head_ry, hair_y + int(head_ry * 0.3)):
        for x in range(head_cx - head_rx, head_cx + head_rx):
            if 0 <= y < h and 0 <= x < w:
                dy = (y - head_cy) / float(head_ry)
                dx = (x - head_cx) / float(head_rx)
                if dx * dx + dy * dy <= 1.0 and dy < -0.30:
                    arr[y, x] = np.array([40, 32, 26], dtype=np.uint8)

    # Eyes: dark, direct
    for ex, ey in [(int(w * 0.43), int(h * 0.20)), (int(w * 0.53), int(h * 0.20))]:
        for dy in range(-5, 6):
            for dx in range(-7, 8):
                if 0 <= ey + dy < h and 0 <= ex + dx < w:
                    d = (dx / 7.0) ** 2 + (dy / 5.0) ** 2
                    if d <= 1.0:
                        if d < 0.4:
                            arr[ey + dy, ex + dx] = np.array([22, 16, 12], dtype=np.uint8)
                        else:
                            arr[ey + dy, ex + dx] = np.array([60, 40, 28], dtype=np.uint8)

    # ── Woman's arms / hands on table ──────────────────────────────────────
    # Left arm (viewer's right) -- closed fist
    arm_l_cx, arm_l_y = int(w * 0.28), int(h * 0.78)
    for dy in range(-28, 28):
        for dx in range(-50, 50):
            if 0 <= arm_l_y + dy < h and 0 <= arm_l_cx + dx < w:
                d = (dx / 50.0) ** 2 + (dy / 28.0) ** 2
                if d <= 1.0:
                    shadow = (abs(dx) / 50.0) ** 1.4 * 0.4
                    col = np.array([190 - int(shadow * 80), 138 - int(shadow * 60),
                                    98 - int(shadow * 40)], dtype=np.uint8)
                    arr[arm_l_y + dy, arm_l_cx + dx] = col

    # Right arm (viewer's left) -- open hand
    arm_r_cx, arm_r_y = int(w * 0.70), int(h * 0.79)
    for dy in range(-22, 22):
        for dx in range(-55, 55):
            if 0 <= arm_r_y + dy < h and 0 <= arm_r_cx + dx < w:
                d = (dx / 55.0) ** 2 + (dy / 22.0) ** 2
                if d <= 1.0:
                    shadow = (abs(dx) / 55.0) ** 1.2 * 0.3
                    col = np.array([195 - int(shadow * 70), 142 - int(shadow * 50),
                                    100 - int(shadow * 35)], dtype=np.uint8)
                    arr[arm_r_y + dy, arm_r_cx + dx] = col

    # ── Ceramic cup ────────────────────────────────────────────────────────
    cup_cx, cup_y0, cup_y1 = int(w * 0.50), int(h * 0.73), int(h * 0.84)
    cup_rx = int(w * 0.05)
    for y in range(cup_y0, cup_y1):
        t = (y - cup_y0) / float(cup_y1 - cup_y0)
        # Cup slightly wider at top
        rx = int(cup_rx * (1.0 + 0.15 * (1.0 - t)))
        for dx in range(-rx, rx + 1):
            if 0 <= cup_cx + dx < w:
                dist = abs(dx) / float(rx + 1)
                highlight = (1.0 - dist ** 2) * 0.3
                cup_col = np.array([
                    int(230 + highlight * 25),
                    int(224 + highlight * 25),
                    int(215 + highlight * 25)
                ], dtype=np.uint8)
                arr[y, cup_cx + dx] = np.clip(cup_col, 0, 255).astype(np.uint8)

    # Cup handle
    handle_x = cup_cx + cup_rx + 4
    for y in range(cup_y0 + 8, cup_y0 + 28):
        if 0 <= handle_x + 12 < w:
            arr[y, handle_x:handle_x + 14] = np.array([225, 219, 210], dtype=np.uint8)

    # ── Cat on table (left side) ────────────────────────────────────────────
    cat_cx = int(w * 0.14)
    cat_cy = int(h * 0.74)
    cat_rx = int(w * 0.10)
    cat_ry = int(h * 0.14)

    # Cat body (loaf shape)
    for y in range(cat_cy - cat_ry, cat_cy + int(cat_ry * 0.3)):
        for x in range(cat_cx - cat_rx, cat_cx + cat_rx):
            if 0 <= y < h and 0 <= x < w:
                dy = (y - cat_cy) / float(cat_ry)
                dx = (x - cat_cx) / float(cat_rx)
                if dx * dx + (dy * 1.2) ** 2 <= 1.0:
                    # Ochre-brown tabby base
                    tx = math.sin((x - cat_cx) / 8.0 + y / 12.0)
                    stripe = 0.5 + 0.5 * tx
                    cat_light = np.array([195, 155, 80], dtype=float)
                    cat_dark  = np.array([100, 76, 38], dtype=float)
                    col = (cat_light * stripe + cat_dark * (1.0 - stripe)).astype(np.uint8)
                    arr[y, x] = col

    # Cat head
    cat_hcx = cat_cx - int(w * 0.01)
    cat_hcy = cat_cy - int(h * 0.14)
    cat_hrx = int(w * 0.065)
    cat_hry = int(h * 0.065)
    for y in range(cat_hcy - cat_hry, cat_hcy + cat_hry):
        for x in range(cat_hcx - cat_hrx, cat_hcx + cat_hrx):
            if 0 <= y < h and 0 <= x < w:
                dy = (y - cat_hcy) / float(cat_hry)
                dx = (x - cat_hcx) / float(cat_hrx)
                if dx * dx + dy * dy <= 1.0:
                    shadow = (abs(dx) ** 1.6) * 0.4
                    cat_f_light = np.array([210, 168, 90], dtype=float)
                    cat_f_dark  = np.array([108, 82, 42], dtype=float)
                    col = (cat_f_light * (1.0 - shadow) + cat_f_dark * shadow).astype(np.uint8)
                    arr[y, x] = col

    # Cat eyes: amber
    for ex, ey in [(cat_hcx - int(cat_hrx * 0.38), cat_hcy - int(cat_hry * 0.1)),
                   (cat_hcx + int(cat_hrx * 0.38), cat_hcy - int(cat_hry * 0.1))]:
        for dy in range(-4, 5):
            for dx in range(-5, 6):
                if 0 <= ey + dy < h and 0 <= ex + dx < w:
                    d = (dx / 5.0) ** 2 + (dy / 4.0) ** 2
                    if d <= 1.0:
                        if d < 0.35:
                            arr[ey + dy, ex + dx] = np.array([18, 14, 10], dtype=np.uint8)
                        else:
                            arr[ey + dy, ex + dx] = np.array([200, 148, 30], dtype=np.uint8)

    # Cat ears
    for side in [-1, 1]:
        ear_x = cat_hcx + side * int(cat_hrx * 0.7)
        ear_y = cat_hcy - cat_hry
        for dy in range(-int(cat_hry * 0.6), 0):
            for dx in range(-int(cat_hrx * 0.25), int(cat_hrx * 0.25)):
                px = ear_x + dx
                py = ear_y + dy
                if 0 <= py < h and 0 <= px < w:
                    arr[py, px] = np.array([140, 100, 55], dtype=np.uint8)

    # ── Empty chair back (right edge) ──────────────────────────────────────
    chair_x0, chair_y0 = int(w * 0.90), int(h * 0.42)
    chair_x1, chair_y1 = w, int(h * 0.68)
    for y in range(chair_y0, chair_y1):
        for x in range(chair_x0, chair_x1):
            arr[y, x] = np.array([42, 36, 28], dtype=np.uint8)

    return Image.fromarray(arr, "RGB")


def main():
    print(f"Session 254 -- Woman at Kitchen Table -- {W}x{H}px")

    ref = build_kitchen_woman_reference(W, H)

    p = Painter(W, H)

    # Tone ground: warm neutral earthy ground
    print("Stage: tone ground...")
    p.tone_ground((0.60, 0.54, 0.46), texture_strength=0.035)

    # Block in: coarse mass establishment
    print("Stage: block in (coarse)...")
    p.block_in(ref, stroke_size=22, n_strokes=320)

    # Build form: medium strokes for body volume
    print("Stage: build form...")
    p.build_form(ref, stroke_size=14, n_strokes=260, dry_amount=0.55)

    # Second block-in: tighten colour zones
    print("Stage: block in (medium)...")
    p.block_in(ref, stroke_size=8, n_strokes=200)

    # Place lights: collar, cup, window light
    print("Stage: place lights...")
    p.place_lights(ref, stroke_size=7, n_strokes=120)

    # Detail block-in
    print("Stage: detail block-in...")
    p.block_in(ref, stroke_size=4, n_strokes=100)

    # REGO FLAT FIGURE PASS (165th mode)
    print("Stage: Rego Flat Figure (165th mode)...")
    p.rego_flat_figure_pass(
        n_levels=7,
        zone_blend=0.68,
        contour_threshold=0.06,
        contour_strength=0.62,
        contour_px=2,
        outline_tone=(0.14, 0.09, 0.06),
        tension_warm=(0.68, 0.48, 0.28),
        tension_cool=(0.36, 0.46, 0.58),
        tension_strength=0.10,
        opacity=0.82,
        seed=254,
    )

    # CONTOUR WEIGHT PASS (session 254 improvement)
    print("Stage: Contour Weight improvement...")
    p.paint_contour_weight_pass(
        contour_threshold=0.05,
        max_weight=0.50,
        weight_exponent=1.2,
        outline_tone=(0.12, 0.08, 0.06),
        junction_boost=0.18,
        taper_strength=0.32,
        opacity=0.68,
    )

    # Focal vignette: push corners dark, focus on figure
    print("Stage: focal vignette...")
    p.focal_vignette_pass(vignette_strength=0.30, opacity=0.50)

    # Final cool glaze: very subtle push toward the cold kitchen light
    print("Stage: final cool glaze...")
    p.glaze(color=(0.66, 0.70, 0.74), opacity=0.07)

    print(f"Saving to {OUT} ...")
    p.save(OUT)
    print("Done.")
    return OUT


if __name__ == "__main__":
    main()
