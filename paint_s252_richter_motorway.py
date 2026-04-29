"""
paint_s252_richter_motorway.py -- Session 252

"Motorway in Rain" -- after Gerhard Richter

Image Description
-----------------
Subject & Composition
    A section of wet German motorway viewed from directly above at a shallow
    diagonal -- the road surface occupies the full canvas, filling it edge to
    edge. Two lanes of tarmac recede in a tight perspective from the lower
    right to upper left, the white lane markings pulled into blurred streaks
    by motion and rain. No sky is visible. No horizon. The road is everything.
    Two dark vehicular smears at mid-left suggest cars that have dissolved
    into their own velocity. The composition is horizontal, nearly abstract,
    with the asphalt surface as both ground and subject.

The Figure
    The cars -- two of them, side by side -- exist as dark rectangular
    masses dragged horizontally across the wet tarmac, their outlines
    completely dissolved into the surrounding wet surface. They have the
    density of shadows without the precision of objects. No windows, no
    wheels, no chrome -- only the pressure of mass moving through wet paint.
    Emotional state: velocity as erasure, the modern landscape as surface
    without interiority, objects subsumed into weather.

The Environment
    The tarmac is a complex chromatic neutral -- not grey but a layered
    field of cool blue-grey, warm ash, and cold near-black. The wet surface
    holds light: horizontal bands of pale silver-white reflection from
    overhead strip lighting dissolve and smear across the dark ground.
    The lane markings are white -- or were white -- now drawn out into
    long trailing smears by the squeegee and the implied rain. The road
    edges at left and right dissolve into near-black. Foreground detail
    is high: every water channel, every tarmac ridge is articulated.
    Toward the upper-left the entire surface dissolves into a uniform
    near-grey, as if the photograph were taken at the limit of depth
    of field or the road disappears into its own distance.

Technique & Palette
    Gerhard Richter Squeegee Drag mode -- session 252, 163rd distinct mode.

    Stage 1, HORIZONTAL DRAG BAND DECOMPOSITION: n_bands=28, band_min=18,
    band_max=65. The squeegee bands follow the implied road surface --
    drag_fraction=0.72 mixes the dark asphalt tones laterally, creating
    the characteristic horizontal smear of the photo-based works while
    introducing the physical directness of the squeegee. drag_offset=10
    samples from 10 rows above and below each band, giving wide mixing.

    Stage 2, LATERAL PIGMENT CHANNEL TRAILS: sat_threshold=0.18 is low
    (the palette is largely desaturated); trail_length=60, trail_strength=0.62.
    The most saturated pixels -- the warm-grey tarmac and the cool blue
    reflections -- leave long horizontal trails reproducing the colour
    rivers of Richter's Cage and Strontium series.

    Stage 3, DRAG RESIDUE LUMINANCE MODULATION: residue_amp=0.042. The
    subtle sinusoidal brightness variation across band heights reproduces
    the paint thickness variation visible in high-resolution photographs
    of Richter's abstract surfaces.

    Surface Tooth improvement (session 252): grain_size=8, fiber_amplitude=0.022,
    cross_boost=0.014, ridge_strength=0.018, light_angle=38. The fine woven-
    linen texture grounds the paint surface in physical reality, contrasting
    with the dematerialised velocity of the subject.

    Palette: Cool blue-grey tarmac (0.42/0.44/0.46) -- Warm ash mid-grey
    (0.62/0.60/0.56) -- Wet silver reflection (0.84/0.84/0.82) -- Near-black
    asphalt depth (0.12/0.12/0.14) -- Cadmium warm trace (0.72/0.52/0.28) --
    Cold blue-violet distance (0.34/0.38/0.52) -- White lane marking
    (0.94/0.94/0.92)

Mood & Intent
    The image intends the quality Richter identified in his photo-paintings:
    the blurring as epistemology -- what painting can claim to know about an
    image is always already compromised by the act of painting it. The
    motorway is both specific (post-war German modernity, wet winter,
    fluorescent strip-light) and universal (the road as the modern sublime,
    infrastructure as landscape). The viewer should feel the speed and the
    cold and the particular quality of attention that photographs allow --
    a world seen without a body.
"""

import sys
import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stroke_engine import Painter

W, H = 1100, 900
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "s252_richter_motorway.png")

rng = random.Random(252)


def build_motorway_reference(w, h):
    """
    Construct a synthetic reference image of a wet motorway viewed from above
    at a shallow diagonal.  Two lanes recede upper-left, dark vehicle masses
    at mid-left, silver reflections, lane markings.
    """
    arr = np.zeros((h, w, 3), dtype=np.uint8)

    # Base tarmac -- layered cool-warm grey
    for y in range(h):
        t = y / float(h)
        r = int(98 + 28 * t)
        g = int(96 + 26 * t)
        b = int(102 + 22 * t)
        arr[y, :] = [r, g, b]

    # Perspective lane markings (diagonal streaks from lower-right to upper-left)
    # Road edges
    left_x  = int(w * 0.08)
    right_x = int(w * 0.92)
    mid_x   = (left_x + right_x) // 2

    # Subtle road edge darkening
    for x in range(w):
        edge_d = min(abs(x - left_x), abs(x - right_x)) / float(w * 0.15)
        dark = int(max(0, 28 - 28 * min(edge_d, 1.0)))
        arr[:, x, 0] = np.clip(arr[:, x, 0].astype(int) - dark, 0, 255)
        arr[:, x, 1] = np.clip(arr[:, x, 1].astype(int) - dark, 0, 255)
        arr[:, x, 2] = np.clip(arr[:, x, 2].astype(int) - dark, 0, 255)

    # Lane dividing line -- white (blurred in passes)
    lw = 6
    for y in range(h):
        # Lane line runs from bottom-right to top-left perspective
        x_lane = int(mid_x + (y - h // 2) * 0.12)
        for dx in range(-lw, lw + 1):
            xi = x_lane + dx
            if 0 <= xi < w:
                alpha = max(0.0, 1.0 - abs(dx) / float(lw))
                arr[y, xi, :] = np.clip(
                    arr[y, xi, :].astype(float) + 160 * alpha, 0, 255
                ).astype(np.uint8)

    # Dashed centre marking
    dash_w = 4
    for y in range(0, h, 36):
        for dy in range(20):
            row = y + dy
            if row >= h:
                break
            x_dash = int(mid_x - 80 + (row - h // 2) * 0.08)
            for dx in range(-dash_w, dash_w + 1):
                xi = x_dash + dx
                if 0 <= xi < w:
                    alpha = max(0.0, 1.0 - abs(dx) / float(dash_w))
                    arr[row, xi, :] = np.clip(
                        arr[row, xi, :].astype(float) + 140 * alpha, 0, 255
                    ).astype(np.uint8)

    # Silver reflection band -- horizontal strip of overhead lighting
    refl_y = int(h * 0.38)
    refl_h = int(h * 0.12)
    for y in range(refl_y, min(refl_y + refl_h, h)):
        t = (y - refl_y) / float(refl_h)
        bright = int(88 * (1.0 - abs(2 * t - 1.0) ** 2))
        arr[y, left_x:right_x, :] = np.clip(
            arr[y, left_x:right_x, :].astype(int) + bright, 0, 255
        ).astype(np.uint8)

    # Vehicle masses -- two dark rectangular smears at mid-left
    for veh in [(int(w * 0.18), int(h * 0.54)), (int(w * 0.28), int(h * 0.54))]:
        vx, vy = veh
        vw, vh = int(w * 0.08), int(h * 0.12)
        y0 = max(0, vy - vh // 2)
        y1 = min(h, vy + vh // 2)
        x0 = max(0, vx - vw // 2)
        x1 = min(w, vx + vw // 2)
        # Soft dark mass
        for y in range(y0, y1):
            for x in range(x0, x1):
                dy_frac = abs(y - vy) / float(vh // 2)
                dx_frac = abs(x - vx) / float(vw // 2)
                mask = max(0.0, 1.0 - max(dy_frac, dx_frac) ** 1.5)
                dark = int(72 * mask)
                arr[y, x, :] = np.clip(arr[y, x, :].astype(int) - dark, 0, 255).astype(np.uint8)

    # Upper-left distance fade to uniform cool grey
    fade_x = int(w * 0.65)
    for y in range(h):
        for x in range(w):
            dx = max(0, fade_x - x) / float(fade_x)
            dy = max(0, int(h * 0.2) - y) / float(h * 0.2)
            fade = min(dx * 1.8 + dy * 1.0, 1.0)
            if fade > 0:
                grey_r, grey_g, grey_b = 132, 130, 134
                arr[y, x, 0] = int(arr[y, x, 0] * (1 - fade) + grey_r * fade)
                arr[y, x, 1] = int(arr[y, x, 1] * (1 - fade) + grey_g * fade)
                arr[y, x, 2] = int(arr[y, x, 2] * (1 - fade) + grey_b * fade)

    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGB")


def main():
    p = Painter(W, H)

    print("Stage: tone ground...")
    # Cool grey-beige ground, light texture
    p.tone_ground((0.52, 0.50, 0.48), texture_strength=0.04)

    print("Stage: block in reference...")
    ref = build_motorway_reference(W, H)
    p.block_in(ref, stroke_size=22, n_strokes=320)

    print("Stage: second block-in (detail layer)...")
    p.block_in(ref, stroke_size=10, n_strokes=180)

    print("Stage: vignette...")
    p.focal_vignette_pass(vignette_strength=0.18, opacity=0.60)

    print("Stage: Richter Squeegee Drag (163rd mode)...")
    p.richter_squeegee_drag_pass(
        n_bands=28,
        band_min=18,
        band_max=65,
        drag_fraction=0.72,
        drag_offset=10,
        sat_threshold=0.18,
        trail_length=60,
        trail_strength=0.62,
        residue_amp=0.042,
        opacity=0.88,
        seed=252,
    )

    print("Stage: Surface Tooth improvement...")
    p.paint_surface_tooth_pass(
        grain_size=8,
        fiber_amplitude=0.022,
        cross_boost=0.014,
        ridge_strength=0.018,
        light_angle=38.0,
        opacity=0.60,
        seed=4252,
    )

    print("Stage: final vignette deepening...")
    p.focal_vignette_pass(vignette_strength=0.12, opacity=0.40)

    print(f"Saving to {OUT} ...")
    p.save(OUT)
    print("Done.")


if __name__ == "__main__":
    main()
