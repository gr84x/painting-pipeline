"""
paint_s272_desert_after_rain.py -- Session 272

"Europe After the Rain II -- Desert Spires at Twilight"
in the manner of Max Ernst (Surrealism / Dada)

Image Description
-----------------
Subject & Composition
    A vast surrealist desert landscape at deep twilight -- canvas landscape
    format (1440 x 1040). The composition is organized in three horizontal
    bands: a luminous sky occupying the upper 45% of the canvas, a midground
    of massive eroded stone spires occupying the central 35%, and a cracked
    desert floor with rain puddles in the lower 20%. The viewpoint is low --
    the horizon sits at roughly 55% from the top, giving the stone spires
    enormous apparent height and setting the sky as the dominant force.
    No single spire is centered; the group is weighted slightly left-of-center,
    with open desert and sky on the right providing compositional breathing room.

The Subject
    The stone spires are the primary subject -- five to seven irregular columns
    of deeply eroded sandstone, ranging from near-black silhouette on the left
    to warm ochre-umber lit on the right where the last light of the setting sun
    still touches them. Their forms are biomorphic: not simple cylinders but
    organic, swelling, tapering shapes that suggest both geological process and
    arrested biological growth -- the forms of decalcomania, of paint pulled from
    a surface, of limestone cave formations. Their surfaces carry the complete
    Ernst decalcomania texture: zones of dense paint mass alternating with thin
    veil passages, crossed by fine dendritic vein lines. The tallest spire (left
    cluster) rises almost to the top of the canvas; the smallest (right, solo)
    stands apart, almost delicate. Between the spires, the dark sky is visible
    as deep prussian-violet slots of negative space.

The Environment
    SKY (upper 45%): Deep violet-indigo at the zenith, transitioning through
    prussian blue in the mid-sky, then through a band of cool slate-grey, to
    a luminous amber-gold along the horizon line. This is not a sunset gradient
    but the last 15 minutes after sunset -- the sun is gone, only its afterglow
    remains as a compressed band of warmth against the rising violet-indigo of
    space above. A faint secondary zone of pale apricot sits just above the
    horizon, slightly wider than the amber band, suggesting the remnant of a
    cloud bank now dissolving. The sky has the quality of extreme stillness after
    a storm: the air is clear, the light fading fast, the atmosphere heavy with
    recently-fallen moisture.

    MIDGROUND -- SPIRES (35%): The eroded sandstone columns emerge from the flat
    desert floor. Their bases merge with the foreground cracked earth; their tops
    are cut as dark profiles against the transitional sky. The left-side spires
    are mostly in shadow -- cool blue-violet on their west-facing surfaces, deep
    umber-black on their shaded east faces. The right-side spire still carries
    warm ochre-gold on its top, the last direct light touching any surface in the
    scene. The rock texture is the complete Ernst decalcomania surface: biomorphic
    zones of dense umber alternating with pale sand-ochre veils, crossed at
    irregular intervals by fine dark vein lines -- the fossilized trace of paint
    that bridged two surfaces and then ruptured.

    FOREGROUND -- CRACKED EARTH (lower 20%): The desert floor is a network of
    deep polygonal cracks, the classic pattern of sun-dried mud, here occurring
    after a rain event. The surface between the cracks is flat, dark, slightly
    wet-looking -- darker than when dry. In the cracks themselves: deep shadow,
    blue-violet. Several shallow oval and crescent-shaped puddles of standing
    rainwater reflect the sky above -- small mirrors of amber-gold and violet
    laid into the cracked earth. Their edges are perfectly still; not a ripple.
    The puddle reflections are cooler and slightly more desaturated than the
    sky they mirror, because water absorbs some of the reflected light.

Technique & Palette
    Max Ernst Surrealism / Decalcomania mode -- session 272, 183rd distinct mode.

    Pipeline:
    1. Procedural reference: sky gradient (violet-indigo to amber horizon),
       spire silhouettes with warm-lit and cool-shadow zones, cracked earth
       foreground, rain puddles reflecting sky.
    2. tone_ground: warm umber-ochre (0.20, 0.16, 0.10).
    3. underpainting x2: establish tonal architecture -- dark spires, luminous sky,
       cracked earth.
    4. block_in x2: build sky gradient, spire mass, foreground texture.
    5. build_form x2: develop spire surface detail, earth crack network, puddle
       reflections.
    6. place_lights: horizon amber glow, warm light on right spire top, puddle
       reflections.
    7. paint_scumbling_veil_pass (s272 improvement): apply semi-opaque warm veil
       over dark shadow passages in spire bases and earth cracks.
    8. ernst_decalcomania_pass (s272, 183rd mode): biomorphic paint transfer texture
       applied to the whole canvas -- pressure-field-driven zone differentiation,
       umber-ochre in dense zones, pale sand in veil zones, dendritic vein lines.
    9. paint_aerial_perspective_pass: cool atmospheric recession in sky distance.
    10. paint_chromatic_underdark_pass: deep blue-violet in deepest shadow zones.

    Full palette:
    umber-ochre (0.32/0.20/0.08) -- pale-sand-ochre (0.58/0.50/0.35) --
    prussian-blue-indigo (0.08/0.12/0.24) -- dark-umber (0.18/0.14/0.10) --
    terracotta (0.62/0.42/0.22) -- pale-warm-grey (0.72/0.68/0.55) --
    deep-forest-green (0.12/0.22/0.16) -- muted-rose-umber (0.48/0.35/0.28) --
    light-gold (0.85/0.76/0.55)

Mood & Intent
    The painting intends GEOLOGICAL TIME AND THE SURREALIST AFTERMATH. Max Ernst
    painted "Europe After the Rain II" between 1940 and 1942, in exile in New York,
    using the decalcomania technique to evoke the devastation of a continent at war.
    This painting stands in that tradition: the desert spires are the ruins of
    something -- an ancient civilization, a geological event, a biological process --
    whose precise nature cannot be determined. The viewer stands in the aftermath,
    looking at forms that are simultaneously stone, bone, architecture, and fungal
    growth. The rain has just passed; the air is clear; the sky is filling with
    night. The puddles on the cracked earth are the only legible signs of recent
    change. The painting should leave the viewer with a feeling of profound temporal
    displacement -- standing in deep geological time, after something vast has
    happened, before darkness fully closes.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stroke_engine import Painter

W, H = 1440, 1040
SEED = 272
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s272_desert_after_rain.png")


def build_reference() -> np.ndarray:
    """Build a procedural reference for the Ernst desert landscape.

    Returns uint8 (H, W, 3) in range 0-255.
    """
    rng = np.random.default_rng(SEED)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # ── Sky gradient (upper 48%) ──────────────────────────────────────────────
    horizon_y = int(H * 0.52)   # y coordinate of the horizon line

    for y in range(horizon_y):
        t = y / float(horizon_y - 1)  # 0 = zenith, 1 = horizon

        # Zenith: deep prussian violet-indigo (0.06, 0.08, 0.28)
        # Horizon: warm amber-gold (0.86, 0.70, 0.36)
        # Intermediate: prussian blue (0.10, 0.18, 0.42) at t=0.5

        if t < 0.55:
            # Upper sky: violet-indigo -> prussian blue
            s = t / 0.55
            r = 0.06 + (0.10 - 0.06) * s
            g = 0.08 + (0.18 - 0.08) * s
            b = 0.28 + (0.42 - 0.28) * s
        elif t < 0.80:
            # Mid sky: prussian blue -> slate blue-grey
            s = (t - 0.55) / 0.25
            r = 0.10 + (0.30 - 0.10) * s
            g = 0.18 + (0.32 - 0.18) * s
            b = 0.42 + (0.48 - 0.42) * s
        else:
            # Near horizon: slate blue-grey -> amber gold
            s = (t - 0.80) / 0.20
            r = 0.30 + (0.86 - 0.30) * s
            g = 0.32 + (0.70 - 0.32) * s
            b = 0.48 + (0.36 - 0.48) * s

        # Add subtle horizontal noise for sky texture
        noise = rng.uniform(-0.008, 0.008, W).astype(np.float32)
        ref[y, :, 0] = np.clip(r + noise, 0, 1)
        ref[y, :, 1] = np.clip(g + noise * 0.6, 0, 1)
        ref[y, :, 2] = np.clip(b + noise * 0.4, 0, 1)

    # ── Desert floor and spires (lower 52%) ───────────────────────────────────
    ground_y = horizon_y

    # Base desert floor: dark warm umber, slightly wet
    for y in range(ground_y, H):
        t = (y - ground_y) / float(H - ground_y - 1)
        # Near horizon: lighter warm ochre; near bottom: dark umber
        r = 0.28 + 0.12 * (1.0 - t) + rng.uniform(-0.015, 0.015)
        g = 0.20 + 0.08 * (1.0 - t) + rng.uniform(-0.012, 0.012)
        b = 0.10 + 0.04 * (1.0 - t) + rng.uniform(-0.008, 0.008)
        ref[y, :, 0] = np.clip(r, 0, 1)
        ref[y, :, 1] = np.clip(g, 0, 1)
        ref[y, :, 2] = np.clip(b, 0, 1)

    # ── Crack network (foreground) ────────────────────────────────────────────
    crack_start_y = int(H * 0.80)
    crack_rng = np.random.default_rng(SEED + 1)

    for y in range(crack_start_y, H):
        for x in range(0, W, 1):
            # Polygonal crack pattern via modular arithmetic with jitter
            cx = int(x / 55 + crack_rng.uniform(-0.5, 0.5))
            cy = int((y - crack_start_y) / 45 + crack_rng.uniform(-0.5, 0.5))
            # Distance to nearest grid line (simulates crack)
            dx = (x % 55) / 55.0
            dy = ((y - crack_start_y) % 45) / 45.0
            dist_to_crack = min(dx, 1-dx, dy, 1-dy)
            if dist_to_crack < 0.08:
                # Crack: deep blue-violet shadow
                depth = 1.0 - dist_to_crack / 0.08
                ref[y, x, 0] = np.clip(ref[y, x, 0] * (1 - depth * 0.55) + 0.06 * depth, 0, 1)
                ref[y, x, 1] = np.clip(ref[y, x, 1] * (1 - depth * 0.55) + 0.06 * depth, 0, 1)
                ref[y, x, 2] = np.clip(ref[y, x, 2] * (1 - depth * 0.55) + 0.18 * depth, 0, 1)

    # ── Rain puddles (foreground, lower 20%) ─────────────────────────────────
    puddle_rng = np.random.default_rng(SEED + 2)
    puddles = [
        # (cx, cy, rx, ry) -- center x, center y, radius x, radius y
        (int(W * 0.18), int(H * 0.88), 55, 22),
        (int(W * 0.44), int(H * 0.93), 80, 28),
        (int(W * 0.70), int(H * 0.86), 45, 18),
        (int(W * 0.84), int(H * 0.91), 65, 24),
        (int(W * 0.30), int(H * 0.97), 40, 14),
    ]
    for (px, py, prx, pry) in puddles:
        for dy in range(-pry - 2, pry + 2):
            yyy = py + dy
            if yyy < 0 or yyy >= H:
                continue
            for dx in range(-prx - 2, prx + 2):
                xxx = px + dx
                if xxx < 0 or xxx >= W:
                    continue
                dist_ellipse = (dx / prx) ** 2 + (dy / pry) ** 2
                if dist_ellipse <= 1.0:
                    # Reflect sky color from corresponding sky y
                    sky_y = int(horizon_y * 0.85 * (1 - dist_ellipse))
                    sky_y = min(sky_y, horizon_y - 1)
                    # Puddle reflects sky, slightly desaturated and darker
                    ref[yyy, xxx, 0] = ref[sky_y, xxx, 0] * 0.82
                    ref[yyy, xxx, 1] = ref[sky_y, xxx, 1] * 0.82
                    ref[yyy, xxx, 2] = ref[sky_y, xxx, 2] * 0.88

    # ── Stone spires (midground) ──────────────────────────────────────────────
    # Define spire shapes as trapezoid-ish columns using parametric profiles
    spire_base_y   = ground_y
    spire_rng      = np.random.default_rng(SEED + 3)

    # Each spire: (center_x_frac, base_y_frac, top_y_frac, base_half_w, top_half_w, light_side)
    spires = [
        # Left cluster -- in shadow, dark blue-umber
        (0.14, 0.52, 0.12, 55, 18, False),
        (0.22, 0.52, 0.18, 70, 22, False),
        (0.32, 0.52, 0.08, 85, 26, False),
        # Center-right -- transitional
        (0.48, 0.52, 0.22, 60, 20, False),
        # Right -- warm lit side
        (0.72, 0.52, 0.30, 50, 15, True),
    ]

    for (cx_f, base_f, top_f, bw, tw, lit) in spires:
        cx      = int(cx_f * W)
        base_y  = int(base_f * H)
        top_y   = int(top_f * H)
        height  = base_y - top_y

        for y in range(top_y, base_y + 1):
            # Linear interpolation of width from top to base
            t = (y - top_y) / float(height + 1)
            # Add slight organic bulge at 60% height
            bulge = 0.12 * np.sin(np.pi * t) * (1.0 + 0.3 * np.sin(3 * np.pi * t))
            half_w = int(tw + (bw - tw) * t + bulge * bw)
            half_w = max(half_w, 6)

            x_left  = cx - half_w
            x_right = cx + half_w

            for x in range(max(0, x_left), min(W, x_right + 1)):
                dist_from_left  = x - x_left
                dist_from_right = x_right - x
                edge_dist = min(dist_from_left, dist_from_right)
                width = x_right - x_left + 1
                edge_frac = edge_dist / float(width * 0.5 + 1)

                if lit:
                    # Right side -- warm ochre, top has warm light
                    light_fraction = max(0.0, 1.0 - 2 * t)  # warmest at top
                    r = 0.38 + 0.25 * light_fraction + 0.08 * edge_frac
                    g = 0.26 + 0.18 * light_fraction + 0.04 * edge_frac
                    b = 0.10 + 0.05 * light_fraction + 0.02 * edge_frac
                else:
                    # Shadow side -- cool blue-umber
                    shadow_depth = 0.4 + 0.3 * (1 - edge_frac)
                    r = 0.16 * (1 - shadow_depth) + 0.08 * shadow_depth
                    g = 0.13 * (1 - shadow_depth) + 0.10 * shadow_depth
                    b = 0.10 * (1 - shadow_depth) + 0.22 * shadow_depth

                # Surface texture noise
                n = spire_rng.uniform(-0.02, 0.02)
                ref[y, x, 0] = np.clip(r + n, 0, 1)
                ref[y, x, 1] = np.clip(g + n * 0.8, 0, 1)
                ref[y, x, 2] = np.clip(b + n * 0.6, 0, 1)

            # Hard left/right edge darkening (shadow line)
            for x in range(max(0, x_left - 3), min(W, x_left + 2)):
                if 0 <= x < W:
                    ref[y, x, :] *= 0.62

    # Convert to uint8
    return (np.clip(ref, 0, 1) * 255).astype(np.uint8)


def main():
    print(f"Session 272 -- Max Ernst Decalcomania -- Desert After Rain")
    print(f"Canvas: {W} x {H}")
    print()

    print("Building procedural reference...")
    ref = build_reference()
    print(f"  Reference: {ref.shape}, dtype={ref.dtype}, range=[{ref.min()},{ref.max()}]")

    print("Initialising Painter...")
    p = Painter(W, H, seed=SEED)

    print("Laying ground...")
    p.tone_ground((0.20, 0.16, 0.10), texture_strength=0.025)

    print("Underpainting (x2)...")
    p.underpainting(ref, stroke_size=52, n_strokes=240)
    p.underpainting(ref, stroke_size=36, n_strokes=260)

    print("Block-in (x2)...")
    p.block_in(ref, stroke_size=30, n_strokes=480)
    p.block_in(ref, stroke_size=20, n_strokes=500)

    print("Build form (x2)...")
    p.build_form(ref, stroke_size=12, n_strokes=520)
    p.build_form(ref, stroke_size=6,  n_strokes=420)

    print("Place lights...")
    p.place_lights(ref, stroke_size=4, n_strokes=300)

    print("Scumbling veil pass (s272 improvement)...")
    p.paint_scumbling_veil_pass(
        dark_threshold=0.36,
        veil_lightness=0.20,
        veil_warmth=0.05,
        coverage_sigma=2.8,
        coverage_seed=SEED,
        coverage_density=0.58,
        opacity=0.52,
    )

    print("Ernst decalcomania pass (183rd mode)...")
    p.ernst_decalcomania_pass(
        pressure_scale=0.042,
        pressure_octaves=6,
        transfer_strength=0.30,
        bio_zone_sigma=6.5,
        bio_dark_r=0.30,
        bio_dark_g=0.19,
        bio_dark_b=0.08,
        bio_light_r=0.60,
        bio_light_g=0.52,
        bio_light_b=0.36,
        vein_strength=0.20,
        noise_seed=SEED,
        opacity=0.68,
    )

    print("Aerial perspective pass...")
    p.paint_aerial_perspective_pass()

    print("Chromatic underdark pass...")
    p.paint_chromatic_underdark_pass()

    print(f"Saving to {OUT}...")
    p.save(OUT)
    print("Done.")


if __name__ == "__main__":
    main()
