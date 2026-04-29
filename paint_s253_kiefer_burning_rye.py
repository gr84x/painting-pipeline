"""
paint_s253_kiefer_burning_rye.py -- Session 253

"Burning Rye Field, Margarete" -- after Anselm Kiefer

Image Description
-----------------
Subject & Composition
    A vast scorched rye field viewed at a low angle from ground level,
    looking straight toward a distant horizon. The field dominates the
    lower two-thirds of the canvas, stretching in deep converging perspective
    furrows from the lower corners to a narrow vanishing point. Above the
    horizon a dense, ashen sky occupies the upper third. A single vertical
    element -- a charred wooden post or remnant stalk -- rises at the
    left-center of the mid-ground, breaking the horizontal severity of the
    field. No human figures. No comfort.

The Figure
    The lone post is dark as burnt bone -- charcoal grey with traces of
    rust iron-oxide, the vertical axis that anchors the entire composition's
    geometry. Its surface is cracked, leaded, the sinusoidal fissures of
    Kiefer's lead-sheet surfaces tracking across its mass. It is at rest,
    standing with the absolute stillness of something that has survived by
    not resisting. Emotional state: endurance, weight, the quality of
    something that will outlast the burning.

The Environment
    The rye field is a complex layered surface: scorched umber-black in the
    deep foreground, warming to ash-grey in the middle distance, dissolving
    to pale ashen white-yellow at the horizon where the burned stalks meet
    the sky. The furrows converge with mathematical precision into the
    distance -- dark trenches alternating with raised ridges of dried and
    charred straw. The sky above the horizon is dense and layered: a
    horizontal gradient from pale flax-white at the horizon line through
    graphite mid-grey to near-black at the top edge, as if heavy with ash
    still falling. The boundaries between field and sky are hard and exact --
    a Kiefer horizon has the flatness and precision of a ruled line.
    Background detail: sky is nearly uniform in value with faint horizontal
    banding (stratified ash layers). Foreground detail: every furrow ridge
    articulated, the straw-gold fiber overlay running at the 15-degree
    ploughed-field angle across the dried stalks of the middle distance.

Technique & Palette
    Anselm Kiefer Scorched Earth mode -- session 253, 164th distinct mode.

    Stage 1, ASHEN FIELD DESATURATION GRADIENT: n_zones=10, max_ash_blend=0.72.
    The gradient works from the near-black scorched foreground upward toward
    the pale ashen horizon, desaturating and simultaneously darkening dark
    pixels (charred zone) while preserving the slight warm chroma of
    mid-ground straw stalks. dark_push=0.18 pushes the foreground furrow
    trenches toward near-black.

    Stage 2, LEAD SHEET CRACK VEINING: n_cracks=28, crack_depth=0.42,
    lum_ceiling=0.55. The sinusoidal crack trajectories wander across the
    field surface and the burned post, simulating the distinctive cracking
    pattern of Kiefer's lead-impregnated surfaces. Suppressed above 0.55
    luminance so the pale sky retains its bare ashen quality.

    Stage 3, STRAW FIBER WARM OVERLAY: straw_angle=14, straw_period=8,
    fiber_strength=0.42. The tilted warm-golden fiber texture activates
    across the mid-luminance ploughed field -- the dead straw resting in
    angled furrows, still retaining a ghost of its summer warmth against
    the cold char. Gated on lum 0.28 to 0.62.

    Impasto Ridge Cast improvement (session 253): light_angle=145 (upper-right
    light), shadow_offset=5, shadow_strength=0.30, highlight_strength=0.14.
    Every ridge of impasto paint -- furrow edge, stalk tip, post surface --
    casts a small directional shadow and catches a sliver of cold light,
    giving the physical dimensionality of a surface built with matter, not
    merely painted.

    Palette: Scorched near-black (0.14/0.12/0.10) -- Charred umber
    (0.26/0.22/0.18) -- Ash grey mid (0.52/0.48/0.44) -- Pale ashen
    horizon (0.82/0.78/0.70) -- Straw warm gold (0.76/0.68/0.28) --
    Lead grey (0.44/0.42/0.40) -- Rust iron trace (0.58/0.32/0.16) --
    Cold sky white (0.88/0.86/0.82)

Mood & Intent
    The painting carries the specific weight Kiefer assigns to German
    landscape: beautiful and terrible simultaneously, scorched by a history
    that cannot be undone, the field as both agricultural fact and historical
    wound. "Your golden hair, Margarete" -- the rye field is the hair of the
    dead woman in Celan's 'Death Fugue', the burning both literal (a field
    after harvest, or after fire) and metaphorical (a culture consuming
    itself). The viewer should feel the vast cold weight of the sky pressing
    on the land, the texture of the burned field underfoot, and the solitary
    dignity of the post that has not fallen. Grief without sentimentality.
    Endurance without redemption.
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
                   "s253_kiefer_burning_rye.png")

rng = random.Random(253)


def build_burning_rye_reference(w, h):
    """Build a reference image: scorched rye field with converging furrows."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)

    horizon_y = int(h * 0.38)   # horizon sits at 38% from top

    # --- Sky ---
    for y in range(horizon_y):
        t = y / float(horizon_y)   # 0 at top, 1 at horizon
        # Top: near-black ash, bottom: pale ashen white at horizon
        sky_dark  = np.array([24, 22, 20], dtype=float)
        sky_light = np.array([210, 202, 185], dtype=float)
        # Exponential brightening toward horizon
        frac = t ** 0.55
        col = (sky_dark * (1.0 - frac) + sky_light * frac).astype(np.uint8)
        arr[y, :] = col

    # --- Field with converging perspective furrows ---
    vp_x = w * 0.50          # vanishing point x (center)
    vp_y = horizon_y          # vanishing point y

    n_furrows = 28
    # Furrow lines radiate from vanishing point
    # Angle range: from left edge to right edge at bottom
    left_angle  = math.atan2(h - vp_y, 0 - vp_x)
    right_angle = math.atan2(h - vp_y, w - vp_x)

    # Build field base: dark scorched umber
    for y in range(horizon_y, h):
        depth_t = (y - horizon_y) / float(h - horizon_y)  # 0 at horizon, 1 at bottom
        # Horizon: pale ash; foreground: near-black char
        far_col  = np.array([140, 118,  88], dtype=float)
        near_col = np.array([ 36,  28,  18], dtype=float)
        col = (far_col * (1.0 - depth_t) + near_col * depth_t ** 0.7).astype(np.uint8)
        arr[y, :] = col

    # Draw furrow ridges as lighter bands radiating from VP
    draw = ImageDraw.Draw(Image.fromarray(arr, "RGB"))

    for i in range(n_furrows + 1):
        frac = i / float(n_furrows)
        # Bottom x from far-left to far-right
        bx = int(frac * w)
        by = h - 1
        # Draw a line from bottom edge to vanishing point
        # Use numpy to draw the furrow directly in the array
        # Furrow is a narrow lighter ridge
        dx = float(vp_x) - bx
        dy = float(vp_y) - by
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1:
            continue
        steps = int(dist)
        for s in range(steps):
            t = s / float(steps)
            px = int(bx + dx * t)
            py = int(by + dy * t)
            if 0 <= px < w and horizon_y <= py < h:
                depth_t = (py - horizon_y) / float(h - horizon_y)
                # Furrow ridge color: warm straw gold fading to ash in distance
                warm = np.array([120, 100, 50], dtype=float)
                cold = np.array([100,  95, 88], dtype=float)
                col = (warm * depth_t + cold * (1.0 - depth_t)).astype(np.uint8)
                # Narrow ridge: 1-2px wide
                for ox in range(-1, 2):
                    npx = px + ox
                    if 0 <= npx < w:
                        arr[py, npx] = np.clip(
                            arr[py, npx].astype(int) + (col.astype(int) - arr[py, npx]) // 2,
                            0, 255
                        ).astype(np.uint8)

    # --- Burned post / charred stake at left-center ---
    post_x = int(w * 0.38)
    post_top_y = int(h * 0.15)
    post_bot_y = int(h * 0.74)
    post_w = 14
    for y in range(post_top_y, post_bot_y):
        t_post = (y - post_top_y) / float(post_bot_y - post_top_y)
        # Wider at base, narrower at tip
        pw = max(4, int(post_w * (0.5 + 0.5 * t_post)))
        # Post colour: very dark, charcoal-graphite with rust trace
        post_col = np.array([32 + int(8 * t_post), 22, 14], dtype=np.uint8)
        x0 = post_x - pw // 2
        x1 = post_x + pw // 2
        for px in range(max(0, x0), min(w, x1)):
            arr[y, px] = post_col

    # Add slight texture variation to post
    for y in range(post_top_y, post_bot_y):
        pw = max(4, int(post_w * (0.5 + 0.5 * (y - post_top_y) / float(post_bot_y - post_top_y))))
        for px in range(max(0, post_x - pw // 2), min(w, post_x + pw // 2)):
            noise = rng.randint(-8, 8)
            arr[y, px] = np.clip(arr[y, px].astype(int) + noise, 0, 255).astype(np.uint8)

    return Image.fromarray(arr, "RGB")


def main():
    print(f"Session 253 -- Burning Rye Field, Margarete -- {W}x{H}px")

    ref = build_burning_rye_reference(W, H)

    p = Painter(W, H)

    # Tone ground: warm dark ashen brown
    print("Stage: tone ground...")
    p.tone_ground((0.30, 0.26, 0.20), texture_strength=0.04)

    # Block in from reference -- coarse strokes to establish field masses
    print("Stage: block in (coarse)...")
    p.block_in(ref, stroke_size=28, n_strokes=360)

    # Second block-in pass with finer strokes
    print("Stage: block in (medium)...")
    p.block_in(ref, stroke_size=14, n_strokes=280)

    # Build form -- adds dry-brush dimensionality
    print("Stage: build form...")
    p.build_form(ref, stroke_size=10, n_strokes=240, dry_amount=0.62)

    # Detail pass via another tight block-in
    print("Stage: detail block-in...")
    p.block_in(ref, stroke_size=6, n_strokes=160)

    # Place lights: horizon glow, sky edge
    print("Stage: place lights...")
    p.place_lights(ref, stroke_size=8, n_strokes=100)

    # KIEFER SCORCHED EARTH PASS (164th mode)
    print("Stage: Kiefer Scorched Earth (164th mode)...")
    p.kiefer_scorched_earth_pass(
        n_zones=10,
        ash_tone=(0.28, 0.26, 0.24),
        max_ash_blend=0.72,
        dark_push=0.18,
        n_cracks=28,
        crack_width=3,
        crack_depth=0.42,
        crack_tone=(0.10, 0.09, 0.08),
        lum_ceiling=0.55,
        straw_angle=14.0,
        straw_period=8,
        fiber_strength=0.42,
        straw_lo=0.28,
        straw_hi=0.62,
        straw_color=(0.76, 0.68, 0.28),
        opacity=0.86,
        seed=253,
    )

    # IMPASTO RIDGE CAST PASS (session 253 improvement)
    print("Stage: Impasto Ridge Cast improvement...")
    p.paint_impasto_ridge_cast_pass(
        edge_sensitivity=0.48,
        shadow_offset=5,
        shadow_strength=0.30,
        highlight_strength=0.14,
        light_angle=145.0,
        ridge_threshold=0.06,
        opacity=0.72,
    )

    # Subtle vignette to push corners into shadow
    print("Stage: focal vignette...")
    p.focal_vignette_pass(vignette_strength=0.22, opacity=0.55)

    # Final cool ashen glaze
    print("Stage: final glaze...")
    p.glaze(color=(0.68, 0.66, 0.62), opacity=0.10)

    print(f"Saving to {OUT} ...")
    p.save(OUT)
    print("Done.")
    return OUT


if __name__ == "__main__":
    main()
