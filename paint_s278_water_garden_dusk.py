"""
paint_s278_water_garden_dusk.py -- Session 278

"The Water Garden at Dusk -- in the manner of Jan Toorop"

Image Description
-----------------
Subject & Composition
    A Japanese-Dutch ornamental water garden viewed at dusk from the near bank,
    looking diagonally across a rectangular lily pond toward a willow-draped far
    wall. Portrait format 1040 x 1440. The viewpoint is slightly elevated -- about
    1.5 meters above the near stone path -- creating a gentle downward perspective
    across the water. The composition is organized in five horizontal zones:

    (1) Sky (upper 22%): deep cobalt-indigo at zenith, warming to amber-rose at
        the horizon line, the last light of dusk bleeding warm color along the
        waterline.
    (2) Willow curtain (upper 40%, framing both sides): long, flowing arcs of
        weeping willow branches descend from outside the frame, sweeping across
        the upper canvas in organic Art Nouveau curves -- the primary linear
        element of the composition.
    (3) Far bank vegetation (35-55% from top): dark silhouetted irises, reeds,
        and a low stone garden wall barely visible behind the foliage, their
        forms flat and decorative as a Japanese woodblock horizon.
    (4) Still pond surface (35-80%): the center and heart of the painting --
        dark, near-mirrorlike water reflecting the amber-violet sky above, with
        water lilies scattered across the surface: flat circular pads in dark
        olive-green, white and pale pink blossoms open in the last light.
    (5) Near bank foreground (lower 20%): dark stone path edge, tufts of
        ornamental grass, edge of the lily pond.

The Figure
    No human or animal figures. The water garden itself is the sole subject.
    The lily pond is the protagonist -- ancient, still, perfectly receptive. The
    water reads as pure surface: the sky's reflection and the pond floor are
    inseparable. The water lilies are the garden's emotional state: open, quiet,
    at the apex of their daily bloom just as the light fails. Their flat circular
    pads extend in overlapping clusters, creating a decorative pattern across the
    water's face. The blossoms are turned toward the last warmth at the horizon.

The Environment
    SKY (upper 22%): Deep cobalt-indigo at zenith (0.12, 0.10, 0.38), warming
    progressively toward the horizon to warm amber-rose (0.78, 0.50, 0.22) at
    the waterline. The horizon band is the warmest element in the painting --
    a narrow band of amber gold that provides the painting's warmth anchor. The
    sky carries the faintest trace of cirrus cloud texture -- horizontal striations
    in slightly darker and lighter indigo.

    WILLOW CURTAIN (both sides, arcing inward): Long weeping willow branches
    descend in graceful S-curves from the top frame edges. Their color is dark
    olive-emerald (0.15, 0.25, 0.12), their texture formed by the branching of
    hundreds of fine hanging frond-lines. The willow forms create an organic
    arch that frames the pond and sky, their flowing linear character the primary
    Art Nouveau element. The outermost willow branches receive a faint warm amber
    tinge where the horizon light catches them.

    FAR BANK (35-55%): Dark decorative silhouettes of tall bearded irises, their
    sword-like leaves creating vertical linear rhythms. Behind them: low stone
    wall, barely visible. Between the iris leaves: glimpses of the distant amber
    sky. The far bank is flat, dark, almost graphic in its decorative simplicity
    -- a Japanese print horizon.

    STILL POND (35-80%): The water is deep, dark, and still -- a near-mirror of
    the sky above, slightly darker (the water absorbs some light). The amber
    horizon reflects as a warm band across the mid-pond, breaking into rippled
    warm fragments near the lily pad edges. The upper pond (near the far bank)
    reflects cooler indigo sky; the lower pond (near the near bank) is darkest,
    reflecting only the zenith indigo.

    WATER LILIES: Scattered across the pond surface in loose organic clusters.
    Lily pads: flat circular discs in dark olive-green (0.25, 0.38, 0.18), each
    with a characteristic radial notch. Size range: 40-90px diameter. Some pads
    have gentle wet reflections at their edges. Blossoms: white (0.88, 0.86, 0.80)
    and pale pink (0.82, 0.58, 0.56), star-shaped, their petals open in the last
    warmth. Perhaps 8-12 blossoms visible, several clustered near center-pond.

    NEAR BANK FOREGROUND (lower 20%): Dark stone path (0.18, 0.16, 0.14), rough
    rectangular stone edges. Tufts of ornamental grasses and sedge at the water's
    edge (0.22, 0.28, 0.14), slightly backlit by the horizon warmth.

Technique & Palette
    Jan Toorop mode -- session 278, 189th distinct mode.

    The Toorop Symbolist Line pass drives this painting's character: the
    tonal posterization creates flat graphic zones from the smooth procedural
    reference; the iso-contour threading draws dark flowing lines along every
    tonal boundary; the flat-zone hatching fills the smooth water surface and
    sky with fine diagonal ornament; and the warm ink burnishing gives the
    contour network its characteristic sepia quality.

    Pipeline:
    1. Procedural reference: dusk sky gradient, willow arch framing, far bank
       iris silhouettes, still water with lily pads and blossoms, near bank path.
    2. tone_ground: warm buff-parchment (0.62, 0.56, 0.42).
    3. underpainting x2: establish flat tonal structure.
    4. block_in x2: broad masses -- sky, pond, bank, willow.
    5. build_form x2: willow frond details, lily pad surfaces, far bank.
    6. place_lights: lily blossoms and amber horizon reflection.
    7. toorop_symbolist_line_pass (189th mode): posterization + contour lines +
       flat zone hatching + warm ink burnishing.
    8. paint_focal_vignette_pass (s278 improvement): auto-detect focal center
       (pond surface / lily cluster), darken edges, warm center.
    9. paint_aerial_perspective_pass: atmospheric depth into far bank.

    Palette (Toorop dusk water garden):
    ink black (0.06/0.05/0.04) -- warm sepia (0.28/0.20/0.10) --
    cobalt indigo sky (0.12/0.10/0.38) -- amber horizon (0.78/0.50/0.22) --
    dark olive emerald (0.15/0.25/0.12) -- still dark water (0.08/0.10/0.24) --
    lily pad green (0.25/0.38/0.18) -- white blossom (0.88/0.86/0.80) --
    pink blossom (0.82/0.58/0.56) -- iris silhouette (0.10/0.08/0.18)

Mood & Intent
    The painting is a meditation on surface and depth: the water garden gives
    the viewer something to look AT (the flat decorative surface of lily pads
    and reflected sky) and something to look THROUGH (the depth of the water
    beneath). Toorop's Art Nouveau linear treatment transforms the organic forms
    into ornament -- the willow branches, the iris leaves, the lily pad edges
    all become elements in a flowing decorative system.

    The mood is contemplative and slightly melancholic -- dusk rather than
    dawn, the fading of warmth. The amber horizon is the last generous warmth;
    the indigo sky above is coming in. The open lily blossoms will close with
    the dark. There is a quality of the Japanese mono no aware -- the beauty of
    things in their transience -- combined with the Symbolist association of
    water gardens with mystical passage (the lily pond as threshold between
    seen and unseen).

    The viewer should feel stillness, the pleasure of ornament, and the
    particular sadness of beautiful things at the moment they begin to end.
"""

import sys
import os
import math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stroke_engine import Painter

# ── Canvas setup ─────────────────────────────────────────────────────────────
W, H = 1040, 1440
SEED = 278
OUT  = "s278_water_garden_dusk.png"


def build_reference() -> np.ndarray:
    """Procedural reference: Japanese-Dutch water garden at dusk."""
    rng = np.random.default_rng(SEED)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    sky_h      = int(H * 0.22)
    willow_h   = int(H * 0.40)
    far_bank_y = int(H * 0.35)
    far_bank_b = int(H * 0.55)
    pond_y     = int(H * 0.35)
    pond_b     = int(H * 0.80)
    near_bank  = int(H * 0.80)

    # ── Sky zone (upper 22%) ─────────────────────────────────────────────────
    for y in range(sky_h):
        t = y / float(sky_h - 1)            # 0=zenith, 1=horizon
        # cobalt-indigo zenith → amber-rose horizon
        r = 0.12 + t * 0.66
        g = 0.10 + t * 0.40
        b = 0.38 - t * 0.16
        ref[y, :, :] = np.clip([r, g, b], 0, 1)

    # Sky cirrus texture (very faint horizontal striations)
    for _ in range(18):
        sy = rng.integers(2, sky_h - 4)
        sx0 = rng.integers(0, W // 3)
        sw = rng.integers(W // 4, W * 2 // 3)
        strength = 0.04 + rng.random() * 0.03
        for x in range(sx0, min(W, sx0 + sw)):
            ref[sy, x, 0] = np.clip(ref[sy, x, 0] - strength, 0, 1)
            ref[sy, x, 1] = np.clip(ref[sy, x, 1] - strength * 0.9, 0, 1)

    # ── Willow curtain (both sides, arcing downward) ─────────────────────────
    # Left willow: arc from top-left, sweeping down and inward
    def draw_willow_frond(x0, y0, angle_deg, length, sag, thick, warmth=0.0):
        """Draw a single weeping willow frond arc."""
        angle = angle_deg * math.pi / 180.0
        for step in range(length):
            t = step / float(length)
            # Sag gives the drooping quality
            x = int(x0 + step * math.cos(angle) + sag * t * t * math.sin(angle))
            y = int(y0 + step * math.sin(angle) + sag * t * t * math.cos(angle))
            if 0 <= x < W and 0 <= y < H:
                base_g = 0.20 + rng.random() * 0.06
                base_r = 0.14 + warmth * 0.30 + rng.random() * 0.04
                base_b = 0.10 + rng.random() * 0.03
                alpha = (0.5 + rng.random() * 0.3) * (1.0 - t * 0.4)
                for dy in range(-thick, thick + 1):
                    ny = np.clip(y + dy, 0, H - 1)
                    ref[ny, x, 0] = np.clip(
                        ref[ny, x, 0] * (1 - alpha) + base_r * alpha, 0, 1)
                    ref[ny, x, 1] = np.clip(
                        ref[ny, x, 1] * (1 - alpha) + base_g * alpha, 0, 1)
                    ref[ny, x, 2] = np.clip(
                        ref[ny, x, 2] * (1 - alpha) + base_b * alpha, 0, 1)

    # Left willow fronds -- descend from upper-left, arcing right
    for i in range(28):
        x0 = rng.integers(-20, int(W * 0.20))
        y0 = rng.integers(0, int(H * 0.12))
        angle = 75 + rng.random() * 20
        length = rng.integers(200, 480)
        sag = rng.integers(60, 180)
        thick = 1 if rng.random() > 0.5 else 0
        warmth = 0.3 if x0 > 60 else 0.1
        draw_willow_frond(x0, y0, angle, length, sag, thick, warmth)

    # Right willow fronds -- descend from upper-right, arcing left
    for i in range(26):
        x0 = rng.integers(int(W * 0.80), W + 20)
        y0 = rng.integers(0, int(H * 0.12))
        angle = 100 + rng.random() * 20
        length = rng.integers(200, 460)
        sag = rng.integers(-180, -60)
        thick = 1 if rng.random() > 0.5 else 0
        warmth = 0.25
        draw_willow_frond(x0, y0, angle, length, sag, thick, warmth)

    # ── Still pond surface (35-80%) ──────────────────────────────────────────
    for y in range(pond_y, pond_b):
        t = (y - pond_y) / float(pond_b - pond_y)  # 0=far bank, 1=near bank
        # Far end of pond reflects amber horizon; near end reflects indigo zenith
        # Mirror the sky: far pond = amber, near pond = cool indigo
        t_sky = 1.0 - t         # far end = horizon (amber), near end = zenith (indigo)
        r = 0.08 + t_sky * 0.58     # amber reflection decreases toward near bank
        g = 0.10 + t_sky * 0.32
        b = 0.24 - t_sky * 0.12
        # Water is darker than sky (absorption ~20%)
        r = r * 0.72
        g = g * 0.70
        b = b * 0.80
        ref[y, :, :] = np.clip([r, g, b], 0, 1)

    # Water surface micro-ripple (very faint)
    water_noise = rng.random((pond_b - pond_y, W)).astype(np.float32) * 0.03
    wn_smooth = gaussian_filter(water_noise, sigma=1.5)
    for c in range(3):
        ref[pond_y:pond_b, :, c] = np.clip(
            ref[pond_y:pond_b, :, c] + wn_smooth - 0.015, 0, 1)

    # ── Far bank: iris silhouettes and reeds (35-55%) ────────────────────────
    def draw_iris_leaf(cx, base_y, height, angle_deg, width=3):
        """Draw a sword-like iris leaf."""
        angle = angle_deg * math.pi / 180.0
        for step in range(height):
            t = step / float(height)
            x = int(cx + step * math.sin(angle))
            y = int(base_y - step * math.cos(angle))
            if 0 <= x < W and 0 <= y < H:
                w = max(1, int(width * (1.0 - t * 0.6)))
                for dx in range(-w, w + 1):
                    nx = np.clip(x + dx, 0, W - 1)
                    alpha = 0.70 + rng.random() * 0.20
                    ref[y, nx, 0] = np.clip(
                        ref[y, nx, 0] * (1 - alpha) + 0.10 * alpha, 0, 1)
                    ref[y, nx, 1] = np.clip(
                        ref[y, nx, 1] * (1 - alpha) + 0.08 * alpha, 0, 1)
                    ref[y, nx, 2] = np.clip(
                        ref[y, nx, 2] * (1 - alpha) + 0.18 * alpha, 0, 1)

    for i in range(22):
        cx = rng.integers(10, W - 10)
        height = rng.integers(80, 200)
        angle = rng.integers(-12, 13)
        draw_iris_leaf(cx, far_bank_b, height, angle, width=3)

    # Reeds: thin dark verticals
    for i in range(35):
        rx = rng.integers(0, W)
        ry0 = rng.integers(far_bank_y + 20, far_bank_b)
        rh = rng.integers(40, 140)
        rw = 1
        for dy in range(rh):
            sy = ry0 - dy
            if 0 <= sy < H:
                alpha = 0.65 + rng.random() * 0.25
                ref[sy, rx, 0] = np.clip(
                    ref[sy, rx, 0] * (1 - alpha) + 0.08 * alpha, 0, 1)
                ref[sy, rx, 1] = np.clip(
                    ref[sy, rx, 1] * (1 - alpha) + 0.07 * alpha, 0, 1)
                ref[sy, rx, 2] = np.clip(
                    ref[sy, rx, 2] * (1 - alpha) + 0.15 * alpha, 0, 1)

    # Stone garden wall (barely visible behind far bank)
    wall_y = int(H * 0.38)
    wall_h = int(H * 0.05)
    for y in range(wall_y, wall_y + wall_h):
        t_y = (y - wall_y) / float(wall_h)
        lum = 0.22 + rng.random((W,)) * 0.06
        ref[y, :, 0] = np.clip(lum * 0.78, 0, 1)
        ref[y, :, 1] = np.clip(lum * 0.72, 0, 1)
        ref[y, :, 2] = np.clip(lum * 0.65, 0, 1)

    # ── Water lily pads ──────────────────────────────────────────────────────
    pad_centers = []
    # Scatter pads across the pond
    for _ in range(32):
        px = rng.integers(int(W * 0.08), int(W * 0.92))
        py = rng.integers(int(H * 0.42), int(H * 0.78))
        radius = rng.integers(22, 54)
        pad_centers.append((px, py, radius))

        # Draw circular pad
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                dist2 = dx * dx + dy * dy
                if dist2 <= radius * radius:
                    nx = px + dx
                    ny = py + dy
                    if 0 <= nx < W and 0 <= ny < H:
                        # Radial notch: exclude a small wedge (lily pad notch)
                        ang = math.atan2(dy, dx)
                        notch_angle = math.pi * 0.65  # notch direction
                        notch_half = 0.18
                        is_notch = abs(ang - notch_angle) < notch_half
                        if not is_notch:
                            alpha = 0.78 + rng.random() * 0.18
                            # Darker olive-green for pad
                            pad_r = 0.22 + rng.random() * 0.06
                            pad_g = 0.35 + rng.random() * 0.08
                            pad_b = 0.15 + rng.random() * 0.05
                            # Near edge: slightly lighter (wet reflection)
                            edge_dist = abs(math.sqrt(dist2) - radius)
                            if edge_dist < 3:
                                pad_r += 0.08
                                pad_g += 0.06
                            ref[ny, nx, 0] = np.clip(
                                ref[ny, nx, 0] * (1 - alpha) + pad_r * alpha, 0, 1)
                            ref[ny, nx, 1] = np.clip(
                                ref[ny, nx, 1] * (1 - alpha) + pad_g * alpha, 0, 1)
                            ref[ny, nx, 2] = np.clip(
                                ref[ny, nx, 2] * (1 - alpha) + pad_b * alpha, 0, 1)

    # ── Water lily blossoms ───────────────────────────────────────────────────
    blossom_count = 0
    for (px, py, pad_r) in rng.choice(
            np.array(pad_centers),
            size=min(11, len(pad_centers)), replace=False):
        if blossom_count >= 11:
            break
        # Place blossom slightly off-center of pad
        bx = int(px) + rng.integers(-8, 9)
        by = int(py) + rng.integers(-8, 9)
        br = rng.integers(10, 22)

        # Choose white or pink
        if rng.random() > 0.45:
            bl_r, bl_g, bl_b = 0.88, 0.86, 0.80     # white blossom
        else:
            bl_r, bl_g, bl_b = 0.82, 0.58, 0.56     # pale pink blossom

        # Draw star-shaped blossom (6 petals)
        n_petals = 6
        for petal in range(n_petals):
            petal_angle = petal * 2 * math.pi / n_petals + rng.random() * 0.3
            for step in range(br):
                t_p = step / float(br)
                px2 = int(bx + step * math.cos(petal_angle))
                py2 = int(by + step * math.sin(petal_angle))
                petal_w = max(1, int((1.0 - t_p) * 5))
                if 0 <= px2 < W and 0 <= py2 < H:
                    for dw in range(-petal_w, petal_w + 1):
                        npx = np.clip(px2 + dw, 0, W - 1)
                        alpha = 0.82 + rng.random() * 0.15
                        # Warm center on white blossom
                        center_warm = max(0, 1.0 - t_p * 3) * 0.08
                        ref[py2, npx, 0] = np.clip(
                            ref[py2, npx, 0] * (1 - alpha) +
                            (bl_r + center_warm) * alpha, 0, 1)
                        ref[py2, npx, 1] = np.clip(
                            ref[py2, npx, 1] * (1 - alpha) + bl_g * alpha, 0, 1)
                        ref[py2, npx, 2] = np.clip(
                            ref[py2, npx, 2] * (1 - alpha) + bl_b * alpha, 0, 1)
        blossom_count += 1

    # ── Near bank foreground (lower 20%) ─────────────────────────────────────
    for y in range(near_bank, H):
        t = (y - near_bank) / float(H - near_bank)
        # Dark stone path
        stone_r = 0.18 + rng.random() * 0.06
        stone_g = 0.15 + rng.random() * 0.05
        stone_b = 0.12 + rng.random() * 0.04
        ref[y, :, :] = np.clip(
            [stone_r * (1 - t * 0.3), stone_g * (1 - t * 0.3), stone_b * (1 - t * 0.3)],
            0, 1)

    # Ornamental grasses at water edge
    grass_y = near_bank
    for i in range(40):
        gx = rng.integers(0, W)
        for j in range(rng.integers(3, 10)):
            gy = grass_y + rng.integers(-15, 30)
            gh = rng.integers(20, 55)
            gangle = rng.random() * 30 - 15
            for step in range(gh):
                t = step / float(gh)
                sx = int(gx + step * math.sin(gangle * math.pi / 180.0))
                sy = int(gy - step * math.cos(gangle * math.pi / 180.0))
                if 0 <= sx < W and 0 <= sy < H:
                    gr = 0.20 + rng.random() * 0.06
                    gg = 0.26 + rng.random() * 0.08
                    gb = 0.12 + rng.random() * 0.04
                    alpha = 0.55 + rng.random() * 0.30
                    ref[sy, sx, 0] = np.clip(
                        ref[sy, sx, 0] * (1 - alpha) + gr * alpha, 0, 1)
                    ref[sy, sx, 1] = np.clip(
                        ref[sy, sx, 1] * (1 - alpha) + gg * alpha, 0, 1)
                    ref[sy, sx, 2] = np.clip(
                        ref[sy, sx, 2] * (1 - alpha) + gb * alpha, 0, 1)

    # ── Final smooth ─────────────────────────────────────────────────────────
    for c in range(3):
        ref[:, :, c] = gaussian_filter(ref[:, :, c], sigma=0.8)

    return (np.clip(ref, 0, 1) * 255).astype(np.uint8)


# ── Build reference ───────────────────────────────────────────────────────────
print("Building procedural reference...")
ref = build_reference()
Image.fromarray(ref).save("s278_reference.png")
print(f"  Reference saved: s278_reference.png ({W}x{H})")

# ── Painting pipeline ─────────────────────────────────────────────────────────
p = Painter(W, H, seed=SEED)

print("tone_ground...")
p.tone_ground((0.62, 0.56, 0.42), texture_strength=0.018)

print("underpainting (broad)...")
p.underpainting(ref, stroke_size=52, n_strokes=240)

print("underpainting (medium)...")
p.underpainting(ref, stroke_size=34, n_strokes=220)

print("block_in (broad)...")
p.block_in(ref, stroke_size=32, n_strokes=460)

print("block_in (medium)...")
p.block_in(ref, stroke_size=18, n_strokes=530)

print("build_form (medium)...")
p.build_form(ref, stroke_size=11, n_strokes=510)

print("build_form (fine)...")
p.build_form(ref, stroke_size=5, n_strokes=410)

print("place_lights...")
p.place_lights(ref, stroke_size=4, n_strokes=300)

print("toorop_symbolist_line_pass (189th mode)...")
p.toorop_symbolist_line_pass(
    n_zones            = 4,
    zone_strength      = 0.42,
    edge_threshold     = 0.038,
    line_darkness      = 0.52,
    line_length        = 7,
    hatch_period       = 6.5,
    hatch_width        = 1.3,
    hatch_angle_deg    = 40.0,
    hatch_strength     = 0.12,
    hatch_grad_limit   = 0.022,
    warm_ink_r         = 0.30,
    warm_ink_g         = 0.20,
    warm_ink_b         = 0.10,
    warm_ink_opacity   = 0.20,
    opacity            = 0.86,
)

print("paint_focal_vignette_pass (s278 improvement)...")
p.paint_focal_vignette_pass(
    vignette_strength  = 0.48,
    edge_color_cool    = 0.05,
    center_color_warm  = 0.04,
    focal_percentile   = 80.0,
    falloff_exponent   = 1.9,
    opacity            = 0.92,
)

print("paint_aerial_perspective_pass...")
p.paint_aerial_perspective_pass()

print(f"Saving {OUT}...")
p.save(OUT)
print(f"Done: {OUT}")
