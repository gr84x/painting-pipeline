"""
paint_s255_wyeth_winter_oak.py -- Session 255

"Winter Oak, Brandywine" -- after Andrew Wyeth

Image Description
-----------------
Subject & Composition
    A solitary leafless oak tree stands at the crest of a low rise, slightly
    right of canvas center. Viewed from below and to the left, looking very
    slightly upward, so the root line meets the ground about 40% from the
    bottom. The tree occupies the central two-thirds of the canvas height.
    The composition is asymmetric: the main trunk leans a few degrees left,
    and a long heavy branch extends far to the left before rising. No other
    trees are visible. The sky fills the upper 60% of the canvas. A weathered
    split-rail fence descends diagonally from the upper left to the lower right
    across the foreground slope.

The Figure (the tree)
    The oak is old and gnarled, with a dark umber, deeply fissured bark. Main
    trunk diameter approximately 20 inches at the base, tapering as it divides.
    At the first division, about 40% up the tree, the trunk splits into three
    major branches; these divide again and again until the uppermost twigs
    are single pixels against the sky. The bark is dark warm brown lit slightly
    on the upper-left surfaces -- the diffuse winter overhead light catches the
    ridges. The tree's silhouette is irregular and asymmetric. Not the romantic
    oak of Victorian illustration, but the specific, worn individuality of a
    tree that has endured two hundred winters.

The Environment
    The sky is pale and nearly white at the upper left, warming to a faint
    ochre-grey at the horizon. There is no visible sun -- this is the sourceless,
    diffuse light of an overcast January day. The ground is frozen dark umber-
    brown with sparse patches of dried amber grass at the lower right. The hill
    crests just below the tree's root line and descends gently to the right.
    The far distance (upper right) is a pale grey-ochre, suggesting a frozen
    Pennsylvania farm field. The split-rail fence runs diagonally: three grey
    weathered rails, the lower two crossing the foreground, the upper one
    nearly horizontal behind the tree. The boundaries between sky, hill crest,
    and ground are soft but present -- not sfumato, but tempera's specific
    quality of distinct values that nearly merge.

Technique & Palette
    Andrew Wyeth Tempera Dry-Brush mode -- session 255, 166th distinct mode.

    Stage 1, DRY CHALK SURFACE: chalk_amplitude=0.022. Horizontal-grain
    asymmetric Gaussian noise (sigma_y=3.0, sigma_x=0.5) adds the characteristic
    chalky, fibrous quality of egg tempera on gessoed panel. The grain is most
    visible in the sky and bark midtones.

    Stage 2, MIDTONE PRECISION: midtone_low=0.20, midtone_high=0.80,
    contrast_strength=0.45. Unsharp-mask local contrast gated to the midtone
    band differentiates the bark ridges, fence rails, and far field. The sky
    and deepest shadow remain undisturbed.

    Stage 3, DRY-BRUSH FIBER TRACES: fiber_low_lum=0.15, fiber_high_lum=0.48,
    fiber_density=0.05, fiber_brightness=0.09. Sparse horizontal fiber traces
    at bark-to-sky and bark-to-hill transitions simulate the dry-brush mark
    where the loaded brush lifts off rough cold-press paper.

    Tonal Key improvement: target_key=0.42 (slightly low-key -- winter, somber,
    cold). key_strength=4.5. Bayer dithering at dither_amplitude=0.006.

    Palette: Winter sky pale (0.86/0.84/0.78) -- Sky warm horizon
    (0.80/0.76/0.66) -- Bark dark umber (0.28/0.22/0.16) -- Bark mid
    (0.48/0.38/0.28) -- Bark warm light (0.60/0.50/0.38) -- Ground dark
    frozen (0.36/0.30/0.22) -- Ground ochre (0.62/0.52/0.36) -- Dry grass
    amber (0.72/0.62/0.40) -- Fence weathered grey (0.60/0.58/0.52) --
    Far distance pale (0.72/0.68/0.58)

Mood & Intent
    This is a painting of endurance and particularity. Wyeth painted what he
    knew with exactitude -- not a generic oak but THIS oak, in THIS field,
    in THIS light. The bare branches against the winter sky capture both the
    vulnerability and the permanence of the living world. The tree stands where
    it has always stood. The frozen ground will give slightly in spring; the
    bark does not change. This is a painting about time that does not become
    a painting about nostalgia -- it is too precise, too specific, too cold
    for sentiment. The viewer feels the temperature of the air, the hardness
    of the frozen soil underfoot, the faint warmth at the horizon that is
    not yet spring but promises it. There is no human figure. There is no
    narrative. There is only the tree and the field, which are sufficient.
"""

import sys
import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stroke_engine import Painter

W, H = 960, 840
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "s255_wyeth_winter_oak.png")

rng = random.Random(255)


def draw_branch(arr, x, y, angle, length, thickness, depth, rng_local):
    """Recursively draw tree branches onto arr (numpy h x w x 3)."""
    if depth == 0 or length < 2:
        return
    # Endpoint
    rad = math.radians(angle)
    ex = x + length * math.sin(rad)
    ey = y - length * math.cos(rad)

    h, w = arr.shape[:2]
    # Draw line using Bresenham-style approach
    steps = max(int(length * 2), 2)
    for i in range(steps + 1):
        t = i / float(steps)
        px = int(round(x + t * (ex - x)))
        py = int(round(y + t * (ey - y)))
        # Thickness determines draw radius
        r_draw = max(1, int(round(thickness * (1.0 - t * 0.3))))
        # Bark colour: dark umber, slightly lighter on one side
        bark_base = np.array([70, 56, 40], dtype=float)
        bark_light = np.array([152, 128, 96], dtype=float)
        # Light comes from upper-left: angle_to_light
        light_frac = max(0.0, math.sin(rad + 0.5)) * 0.35
        col = (bark_base * (1.0 - light_frac) + bark_light * light_frac).astype(np.uint8)
        for dy in range(-r_draw, r_draw + 1):
            for dx in range(-r_draw, r_draw + 1):
                nx_, ny_ = px + dx, py + dy
                if 0 <= nx_ < w and 0 <= ny_ < h:
                    if dx * dx + dy * dy <= r_draw * r_draw:
                        arr[ny_, nx_] = col

    # Branch splits
    if depth > 1:
        n_children = 2 if depth > 2 else rng_local.randint(2, 3)
        for _ in range(n_children):
            angle_jitter = rng_local.uniform(-32, 32)
            child_angle = angle + angle_jitter
            child_length = length * rng_local.uniform(0.58, 0.74)
            child_thick = max(0.5, thickness * rng_local.uniform(0.55, 0.72))
            draw_branch(arr, ex, ey, child_angle, child_length, child_thick,
                        depth - 1, rng_local)


def build_winter_oak_reference(w, h):
    """Build reference: winter field, oak tree silhouette, fence rails."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    rng_local = random.Random(2550)

    # ── Sky: pale overcast, slight warm tint at horizon ───────────────────
    sky_top    = np.array([218, 214, 208], dtype=float)   # pale grey-white
    sky_horiz  = np.array([200, 192, 170], dtype=float)   # warm ochre-grey horizon
    horizon_y  = int(h * 0.40)   # horizon line at 40% from top

    for y in range(horizon_y):
        t = y / float(horizon_y)
        col = (sky_top * (1.0 - t) + sky_horiz * t).astype(np.uint8)
        arr[y, :] = col

    # ── Far distance (hill line): very pale ochre-grey ─────────────────────
    hill_far_y = int(h * 0.40)
    hill_y     = int(h * 0.56)   # base of the oak's hill
    far_col    = np.array([182, 172, 148], dtype=float)
    mid_col    = np.array([156, 134, 100], dtype=float)   # dark frozen mid-ground

    for y in range(hill_far_y, hill_y):
        t = (y - hill_far_y) / float(hill_y - hill_far_y)
        col = (far_col * (1.0 - t) + mid_col * t).astype(np.uint8)
        arr[y, :] = col

    # ── Ground: dark frozen umber, left darker, right lighter with grass ───
    ground_dark   = np.array([88, 72, 50], dtype=float)
    ground_mid    = np.array([148, 122, 82], dtype=float)
    ground_grass  = np.array([176, 152, 100], dtype=float)  # dry amber grass

    for y in range(hill_y, h):
        depth = (y - hill_y) / float(h - hill_y)
        for x in range(w):
            x_frac = x / float(w)
            # Right side is slightly lighter/more grassy
            mix = min(1.0, x_frac * 1.2 + depth * 0.3)
            if mix < 0.5:
                col = (ground_dark * (1.0 - mix * 2) + ground_mid * mix * 2).astype(np.uint8)
            else:
                mix2 = (mix - 0.5) * 2.0
                col = (ground_mid * (1.0 - mix2) + ground_grass * mix2).astype(np.uint8)
            arr[y, x] = col

    # ── Hill crest: slight darkening along the skyline ─────────────────────
    for y in range(hill_y - 4, hill_y + 8):
        t = abs(y - hill_y) / 8.0
        for x in range(w):
            if 0 <= y < h:
                arr[y, x] = (arr[y, x].astype(float) * (0.75 + 0.25 * t)).astype(np.uint8)

    # ── Sparse dried grass blades in foreground ────────────────────────────
    for _ in range(180):
        gx = rng_local.randint(int(w * 0.40), w - 1)
        gy = rng_local.randint(hill_y + 10, h - 4)
        blade_h = rng_local.randint(8, 24)
        blade_lean = rng_local.uniform(-0.6, 0.8)
        grass_col = np.array([
            rng_local.randint(155, 185),
            rng_local.randint(130, 160),
            rng_local.randint(80, 110)
        ], dtype=np.uint8)
        for step in range(blade_h):
            px = int(gx + step * blade_lean * 0.4)
            py = gy - step
            if 0 <= px < w and 0 <= py < h:
                arr[py, px] = grass_col

    # ── Split-rail fence: diagonal left-lower to right-upper ──────────────
    # Three rails: defined by start/end pairs, slightly weathered grey
    fence_col_1 = np.array([148, 144, 136], dtype=np.uint8)  # upper rail
    fence_col_2 = np.array([138, 134, 126], dtype=np.uint8)  # middle
    fence_col_3 = np.array([128, 124, 116], dtype=np.uint8)  # lower

    rails = [
        # (x0, y0, x1, y1, colour, thickness)
        (int(w * 0.02), int(h * 0.74), int(w * 0.46), int(h * 0.60), fence_col_1, 3),
        (int(w * 0.02), int(h * 0.80), int(w * 0.46), int(h * 0.67), fence_col_2, 3),
        (int(w * 0.02), int(h * 0.86), int(w * 0.50), int(h * 0.76), fence_col_3, 2),
    ]

    for (x0, y0, x1, y1, col, thick) in rails:
        steps = max(abs(x1 - x0), abs(y1 - y0)) * 2
        for i in range(steps + 1):
            t = i / float(steps)
            px = int(round(x0 + t * (x1 - x0)))
            py = int(round(y0 + t * (y1 - y0)))
            for dy in range(-thick // 2, thick // 2 + 1):
                for dx in range(-1, 2):
                    nx_, ny_ = px + dx, py + dy
                    if 0 <= nx_ < w and 0 <= ny_ < h:
                        arr[ny_, nx_] = col

    # ── Fence posts (vertical) ─────────────────────────────────────────────
    post_col = np.array([110, 106, 98], dtype=np.uint8)
    post_positions = [
        (int(w * 0.02), int(h * 0.68), int(h * 0.90)),
        (int(w * 0.24), int(h * 0.63), int(h * 0.85)),
        (int(w * 0.45), int(h * 0.60), int(h * 0.80)),
    ]
    for (px, py_top, py_bot) in post_positions:
        for py in range(py_top, min(py_bot, h)):
            for dx in range(-2, 3):
                if 0 <= px + dx < w:
                    arr[py, px + dx] = post_col

    # ── Oak tree: recursive branching ─────────────────────────────────────
    trunk_x = int(w * 0.54)
    trunk_y = hill_y + 2           # root at hill crest
    trunk_top_y = int(h * 0.14)   # top of trunk before first split

    # Main trunk: thick column from root to first split
    trunk_width_base = 16
    trunk_width_top  = 8
    trunk_col_base  = np.array([70, 56, 40], dtype=np.uint8)
    trunk_col_light = np.array([128, 106, 78], dtype=np.uint8)

    for y in range(trunk_top_y, trunk_y + 1):
        t = (y - trunk_top_y) / float(trunk_y - trunk_top_y + 1)
        tw = int(round(trunk_width_top + (trunk_width_base - trunk_width_top) * t))
        light_side = int(tw * 0.4)   # left 40% is slightly lit
        for dx in range(-tw, tw + 1):
            nx_ = trunk_x + dx
            if 0 <= nx_ < w:
                if dx < -tw + light_side:
                    col = trunk_col_light
                elif dx > tw - 3:
                    # Right edge darkened (shadow)
                    col = np.array([45, 36, 24], dtype=np.uint8)
                else:
                    col = trunk_col_base
                arr[y, nx_] = col

    # Recursive branches from trunk top
    draw_branch(arr, trunk_x, trunk_top_y, -8, 65, 7.0, 6, rng_local)
    draw_branch(arr, trunk_x, trunk_top_y, 18, 58, 6.5, 6, rng_local)
    draw_branch(arr, trunk_x, trunk_top_y, -35, 50, 5.5, 5, rng_local)
    # Long left branch at mid-trunk height
    long_branch_y = trunk_top_y + int((trunk_y - trunk_top_y) * 0.35)
    draw_branch(arr, trunk_x, long_branch_y, -72, 80, 6.0, 5, rng_local)

    return Image.fromarray(arr, "RGB")


def main():
    print(f"Session 255 -- Winter Oak, Brandywine -- {W}x{H}px")

    ref = build_winter_oak_reference(W, H)

    p = Painter(W, H)

    # Tone ground: warm dry ochre -- gessoed panel character
    print("Stage: tone ground...")
    p.tone_ground((0.72, 0.66, 0.52), texture_strength=0.028)

    # Block in: coarse mass -- sky, ground, tree mass
    print("Stage: block in (coarse)...")
    p.block_in(ref, stroke_size=18, n_strokes=280)

    # Build form: medium strokes -- sky gradation, bark texture
    print("Stage: build form...")
    p.build_form(ref, stroke_size=10, n_strokes=220, dry_amount=0.58)

    # Second block-in: tighten colour zones
    print("Stage: block in (medium)...")
    p.block_in(ref, stroke_size=6, n_strokes=180)

    # Place lights: sky lightness at horizon, bark highlights
    print("Stage: place lights...")
    p.place_lights(ref, stroke_size=5, n_strokes=100)

    # Detail block-in: fine bark texture
    print("Stage: detail block-in...")
    p.block_in(ref, stroke_size=3, n_strokes=80)

    # WYETH TEMPERA DRY-BRUSH PASS (166th mode)
    print("Stage: Wyeth Tempera Dry-Brush (166th mode)...")
    p.wyeth_tempera_drybrush_pass(
        chalk_amplitude=0.022,
        midtone_low=0.20,
        midtone_high=0.80,
        contrast_strength=0.45,
        fiber_low_lum=0.15,
        fiber_high_lum=0.48,
        fiber_density=0.05,
        fiber_brightness=0.09,
        opacity=0.80,
        seed=255,
    )

    # TONAL KEY PASS (session 255 improvement)
    print("Stage: Tonal Key improvement (low-key winter)...")
    p.paint_tonal_key_pass(
        target_key=0.42,
        key_strength=4.5,
        dither_amplitude=0.006,
        opacity=0.60,
    )

    # Vignette: darken corners, focus on tree
    print("Stage: focal vignette...")
    p.focal_vignette_pass(vignette_strength=0.28, opacity=0.45)

    # Subtle cool glaze: winter sky coolness
    print("Stage: final cool glaze...")
    p.glaze(color=(0.72, 0.76, 0.80), opacity=0.05)

    print(f"Saving to {OUT} ...")
    p.save(OUT)
    print("Done.")
    return OUT


if __name__ == "__main__":
    main()
