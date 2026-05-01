"""
paint_s277_gorge_at_midnight.py -- Session 277

"The Gorge at Midnight -- in the manner of Francisco de Goya"

Image Description
-----------------
Subject & Composition
    A deep mountain gorge seen from above and slightly to the side, at the
    moment of absolute midnight. The viewpoint is from the rim of the gorge
    looking steeply down into the chasm. The gorge walls plunge from the
    canvas edges toward a dark, barely visible ribbon of water at the bottom
    center. Portrait format 1040 x 1440.

    The composition is structured around a single stark division: the
    overwhelming darkness of the gorge interior against the marginally paler
    dark sky above. A sliver of moonlit rock face on the left wall catches
    the only light in the scene -- a narrow vertical band of pale warm-grey,
    the sole interruption in a world of near-black. The water at the gorge
    bottom is a thin pale thread, almost invisible.

The Figure
    There is no human figure. The gorge itself is the protagonist: vast,
    indifferent, geologically ancient. The craggy walls are the subject --
    fractured limestone with dark fissures, patches of iron-rust staining,
    sparse dry vegetation caught in the rock faces. The walls communicate
    geological time and the absolute scale of nature against which human
    life is vanishingly small. Their emotional state is perfect, ancient
    indifference.

The Environment
    SKY (upper 15%): Near-black, a shade above absolute darkness. Prussian
    blue-black at zenith, with no moon visible (the moon is implied by the
    light on the rock wall, but out of frame to the upper left). One or two
    faint stars -- barely distinguishable points of marginally paler dark.

    GORGE WALLS (left 30% and right 30%): Dark craggy rock faces of warm
    near-black umber, with fractures and overhangs. The left wall catches
    a narrow strip of oblique moonlight -- a cool pale-grey vertical band
    (value ~0.55-0.70) that defines form through contrast with everything
    around it. Below the lit strip the left wall falls back into shadow.
    The right wall is in complete darkness, barely distinguishable from the
    void of the gorge interior.

    GORGE INTERIOR / VOID (center 40%): The deep center of the gorge is
    near-absolute black -- the darkest zone in the composition. The eye
    cannot resolve the far wall. A faint warm umber glow suggests distant
    rock, but no form is legible. This is Goya's void: the abyss that
    stares back.

    WATER (lower center): A narrow thread of pale grey-silver at the gorge
    floor, barely visible, catching nothing but the faintest ambient
    reflection of the sky. It communicates the presence of water not through
    brightness but through a slight texture difference from the rock.

    The scene's texture: rock faces are rough and dry, with hard fractured
    edges. The void has no texture -- it is a flat absolute dark. The sky is
    slightly granular with noise. The only smooth zone is the sliver of water.

Technique & Palette
    Goya mode -- session 277, 188th distinct mode.

    The Goya Black Vision pass drives this painting's character: the dark
    ground penetration warms and deepens all shadow zones with raw umber;
    the sigmoid tonal compression renders the gorge's three-zone chiaroscuro
    (void-dark / shadow-midtone / moonlit accent); the transition zone
    turbulence gives the rock faces their rough, agitated edges; the halation
    bloom pass gives the single lit strip of rock a soft corona.

    Pipeline:
    1. Procedural reference: dark sky, near-void gorge interior, craggy walls,
       single lit moonlit strip, water thread.
    2. tone_ground: deep warm umber (0.22, 0.15, 0.08).
    3. underpainting x2: establish near-black value structure.
    4. block_in x2: gorge walls, sky, void interior.
    5. build_form x2: rock surface detail, lit wall strip, water thread.
    6. place_lights: the single moonlit band and water thread.
    7. goya_black_vision_pass (188th mode): dark ground, tonal compression,
       shadow warmth, transition turbulence.
    8. paint_halation_bloom_pass (s277 improvement): soft bloom around the
       single lit strip of moonlit rock.
    9. paint_aerial_perspective_pass: atmospheric recession into gorge depth.

    Palette (Goya midnight gorge):
    bone black (0.06/0.05/0.04) -- raw umber (0.26/0.18/0.10) --
    prussian dark (0.10/0.12/0.18) -- moonlit grey (0.68/0.65/0.60) --
    pale silver water (0.72/0.70/0.66) -- iron rust (0.38/0.20/0.12) --
    deep umber void (0.14/0.10/0.07) -- faint star (0.82/0.80/0.78)

Mood & Intent
    The painting is a meditation on scale, darkness, and the indifference of
    the natural world. Goya's late landscapes share this quality: in "The Dog"
    (one of the Black Paintings), a small head peers over a vast pale expanse
    of nothing -- the ground, the void, the unknowable beyond. Here, there is
    no dog, no figure, no human presence at all. Only the gorge.

    The single lit strip of moonlit rock is the painting's lifeline -- the
    one element that gives the eye purchase in an overwhelming darkness. It
    reads simultaneously as geological fact (the moon hits this face of rock)
    and emotional fact (in absolute darkness, even the faintest light matters).

    The viewer should feel vertigo, the weight of geological time, and a
    particular kind of Spanish romanticism -- not the decorative sublime of
    Caspar David Friedrich, but something rawer, more violent in its darkness,
    closer to the earth.
"""

import sys
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stroke_engine import Painter

# ── Canvas setup ─────────────────────────────────────────────────────────────
W, H = 1040, 1440
SEED = 277
OUT  = "s277_gorge_at_midnight.png"


def build_reference() -> np.ndarray:
    """Procedural reference: deep mountain gorge at midnight."""
    rng = np.random.default_rng(SEED)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # ── Sky (upper 15%) ───────────────────────────────────────────────────────
    sky_h = int(H * 0.15)
    for y in range(sky_h):
        t = y / float(sky_h - 1)        # 0=top, 1=horizon
        # Near-black prussian-dark at top, marginally lighter at base
        r = 0.055 + t * 0.025
        g = 0.058 + t * 0.022
        b = 0.085 + t * 0.030
        ref[y, :, :] = np.clip([r, g, b], 0, 1)

    # Faint stars (barely lighter than sky)
    for _ in range(22):
        sy = rng.integers(2, sky_h - 4)
        sx = rng.integers(10, W - 10)
        star_v = 0.28 + rng.random() * 0.30
        sr = star_v * 0.96
        sg = star_v * 0.94
        sb = star_v * 1.00
        sw = rng.integers(1, 3)
        ref[sy:sy + sw, sx:sx + sw, :] = np.clip([sr, sg, sb], 0, 1)

    # ── Gorge void / interior (center) ───────────────────────────────────────
    # The gorge interior is the darkest region -- near-absolute void
    gorge_cx   = int(W * 0.50)
    gorge_half = int(W * 0.20)   # half-width of the void at mid-height

    for y in range(sky_h, H):
        t_y = (y - sky_h) / float(H - sky_h)   # 0=top of gorge, 1=bottom
        # Gorge opens wider as we go deeper, then narrows to floor
        if t_y < 0.7:
            half_w = int(gorge_half * (1.0 + t_y * 0.6))
        else:
            half_w = int(gorge_half * (1.0 + 0.42) * (1.0 - (t_y - 0.7) / 0.3 * 0.5))
        x0 = gorge_cx - half_w
        x1 = gorge_cx + half_w
        # Void: near-black with slight warm umber undertone
        void_r = 0.08 + rng.random() * 0.02
        void_g = 0.06 + rng.random() * 0.02
        void_b = 0.04 + rng.random() * 0.01
        if 0 <= x0 < W and x1 > 0:
            ref[y, max(0, x0):min(W, x1), :] = np.clip([void_r, void_g, void_b], 0, 1)

    # ── Left gorge wall (receives moonlight on a narrow strip) ────────────────
    # Left wall base: dark umber rock
    for y in range(sky_h, H):
        x_wall_right = max(0, int(gorge_cx - int(gorge_half * (1.0 + min((y - sky_h) / float(H - sky_h), 0.7) * 0.6))) )
        x_wall_left  = 0
        if x_wall_right <= x_wall_left:
            continue
        for x in range(x_wall_left, min(W, x_wall_right)):
            # Dark warm umber rock with noise
            t_x = x / float(max(x_wall_right, 1))
            # Shadow gradient: darker at gorge edge, slightly lighter at rim
            base_lum = 0.10 + (1.0 - t_x) * 0.06
            r = base_lum * (0.90 + rng.random() * 0.08)
            g = base_lum * (0.78 + rng.random() * 0.07)
            b = base_lum * (0.60 + rng.random() * 0.06)
            ref[y, x, :] = np.clip([r, g, b], 0, 1)

    # Moonlit strip on left wall (narrow vertical band, upper-to-mid left)
    moon_strip_x0 = int(W * 0.12)
    moon_strip_x1 = int(W * 0.21)
    moon_strip_y0 = int(H * 0.12)
    moon_strip_y1 = int(H * 0.62)
    for y in range(moon_strip_y0, moon_strip_y1):
        t_y = (y - moon_strip_y0) / float(moon_strip_y1 - moon_strip_y0)
        # Light is strongest at top, fades as it goes into shadow lower down
        moon_strength = 1.0 - t_y * 0.65
        for x in range(moon_strip_x0, moon_strip_x1):
            # Moonlit cool grey-white on rock
            t_x = (x - moon_strip_x0) / float(moon_strip_x1 - moon_strip_x0)
            # Bright band at center of strip, fading at edges
            falloff = 1.0 - abs(t_x - 0.50) * 2.0
            falloff = max(0.0, falloff)
            lum = (0.48 + rng.random() * 0.08) * moon_strength * falloff
            # Cool grey-white moonlight on limestone
            r = lum * 0.94
            g = lum * 0.93
            b = lum * 1.00
            if ref[y, x, 0] < 0.5:  # only if not already in void
                ref[y, x, :] = np.clip([r, g, b], 0, 1)

    # ── Right gorge wall (in complete shadow) ────────────────────────────────
    for y in range(sky_h, H):
        x_wall_left = min(W, int(gorge_cx + int(gorge_half * (1.0 + min((y - sky_h) / float(H - sky_h), 0.7) * 0.6))) )
        x_wall_right = W
        if x_wall_left >= x_wall_right:
            continue
        for x in range(x_wall_left, x_wall_right):
            t_x = (x - x_wall_left) / float(max(x_wall_right - x_wall_left, 1))
            base_lum = 0.08 + t_x * 0.05
            r = base_lum * (0.88 + rng.random() * 0.08)
            g = base_lum * (0.75 + rng.random() * 0.07)
            b = base_lum * (0.58 + rng.random() * 0.06)
            ref[y, x, :] = np.clip([r, g, b], 0, 1)

    # Iron-rust staining veins in rock walls
    for _ in range(12):
        rx = rng.integers(5, W - 5)
        ry0 = rng.integers(sky_h, H - 60)
        rlen = rng.integers(30, 100)
        rw = rng.integers(2, 5)
        for dy in range(rlen):
            sy = ry0 + dy
            sx = rx + rng.integers(-3, 4)
            if 0 <= sy < H and 0 <= sx < W:
                ref[sy, max(0, sx):min(W, sx + rw), :] = np.clip(
                    [0.30 + rng.random() * 0.08, 0.14 + rng.random() * 0.05,
                     0.08 + rng.random() * 0.04], 0, 1
                )

    # Rock fractures / dark fissures
    for _ in range(18):
        fx = rng.integers(0, W - 5)
        fy0 = rng.integers(sky_h, H - 40)
        flen = rng.integers(20, 80)
        for dy in range(flen):
            sy = fy0 + dy
            sx = fx + rng.integers(-2, 3)
            if 0 <= sy < H and 0 <= sx < W:
                ref[sy, max(0, sx):min(W, sx + 2), :] = np.clip(
                    [0.04, 0.03, 0.02], 0, 1
                )

    # ── Water thread at gorge floor ───────────────────────────────────────────
    water_y0 = int(H * 0.86)
    water_y1 = int(H * 0.92)
    water_cx = int(W * 0.49)
    water_w  = int(W * 0.06)
    for y in range(water_y0, water_y1):
        for x in range(max(0, water_cx - water_w), min(W, water_cx + water_w)):
            t_x = abs(x - water_cx) / float(water_w)
            lum = (0.28 + rng.random() * 0.06) * (1.0 - t_x)
            r = lum * 0.90
            g = lum * 0.92
            b = lum * 1.00
            ref[y, x, :] = np.clip([r, g, b], 0, 1)

    # Sparse dry vegetation on rock faces
    for _ in range(28):
        vx = rng.integers(10, W - 20)
        vy = rng.integers(int(H * 0.25), int(H * 0.80))
        vw = rng.integers(4, 16)
        vh = rng.integers(6, 20)
        alpha = 0.35 + rng.random() * 0.25
        veg_r = 0.18 + rng.random() * 0.08
        veg_g = 0.16 + rng.random() * 0.06
        veg_b = 0.09 + rng.random() * 0.04
        ref[vy:vy + vh, vx:vx + vw, :] = np.clip(
            (1 - alpha) * ref[vy:vy + vh, vx:vx + vw, :] +
            alpha * np.array([veg_r, veg_g, veg_b]),
            0, 1
        )

    # Smooth the reference slightly
    for c in range(3):
        ref[:, :, c] = gaussian_filter(ref[:, :, c], sigma=0.7)

    return (np.clip(ref, 0, 1) * 255).astype(np.uint8)


# ── Build reference ───────────────────────────────────────────────────────────
print("Building procedural reference...")
ref = build_reference()
Image.fromarray(ref).save("s277_reference.png")
print(f"  Reference saved: s277_reference.png ({W}x{H})")

# ── Painting pipeline ─────────────────────────────────────────────────────────
p = Painter(W, H, seed=SEED)

print("tone_ground...")
p.tone_ground((0.22, 0.15, 0.08), texture_strength=0.022)

print("underpainting (broad)...")
p.underpainting(ref, stroke_size=54, n_strokes=230)

print("underpainting (medium)...")
p.underpainting(ref, stroke_size=36, n_strokes=210)

print("block_in (broad)...")
p.block_in(ref, stroke_size=34, n_strokes=450)

print("block_in (medium)...")
p.block_in(ref, stroke_size=20, n_strokes=510)

print("build_form (medium)...")
p.build_form(ref, stroke_size=12, n_strokes=520)

print("build_form (fine)...")
p.build_form(ref, stroke_size=6, n_strokes=430)

print("place_lights...")
p.place_lights(ref, stroke_size=4, n_strokes=290)

print("goya_black_vision_pass (188th mode)...")
p.goya_black_vision_pass(
    ground_r            = 0.26,
    ground_g            = 0.18,
    ground_b            = 0.10,
    ground_strength     = 0.45,
    sigmoid_midpoint    = 0.38,
    sigmoid_steepness   = 6.0,
    tonal_min           = 0.00,
    tonal_max           = 1.02,
    desaturate_thresh   = 0.48,
    desaturate_strength = 0.46,
    umber_r             = 0.28,
    umber_g             = 0.18,
    umber_b             = 0.10,
    umber_blend         = 0.38,
    grad_low            = 0.04,
    grad_high           = 0.50,
    noise_sigma         = 2.6,
    noise_strength      = 0.038,
    seed                = SEED,
    opacity             = 0.82,
)

print("paint_halation_bloom_pass (s277 improvement)...")
p.paint_halation_bloom_pass(
    bloom_threshold = 0.72,
    bloom_sigma     = 14.0,
    warm_r_boost    = 0.05,
    warm_b_cut      = 0.03,
    bloom_opacity   = 0.28,
    opacity         = 1.0,
)

print("paint_aerial_perspective_pass...")
p.paint_aerial_perspective_pass()

print(f"Saving {OUT}...")
p.save(OUT)
print(f"Done: {OUT}")
