"""
paint_s257_afklint_elm_spring.py -- Session 257

"Elm, First Light of Spring" -- after Hilma af Klint

Image Description
-----------------
Subject & Composition
    A single ancient elm tree fills the canvas from edge to edge, viewed from
    directly below and very slightly to the right -- a worm's-eye perspective
    that makes the trunk feel massive and the sky a living presence between the
    branches. The trunk base anchors the lower-center of the composition,
    bifurcating at about one-third height into two main structural arms that
    reach across the upper two-thirds. Secondary branches radiate outward from
    these arms in natural asymmetric arcing gestures, reaching toward the four
    canvas edges. The outermost terminal branches bear the first unfurling leaf
    clusters of early spring -- small, citron-yellow-green, lit from above.

The Figure
    The elm is very old -- the trunk's circumference suggests three or four
    centuries. Its bark is deeply furrowed with long vertical fissures, the
    ridges between them grey-brown and slightly silvered where the light
    catches. At the bifurcation point there is a large pale callus where an
    old limb was lost decades ago. The trunk is backlit from above, so its
    silhouette edge catches a rim of warm amber afternoon light while its
    face is in soft cool blue-grey shadow. The branches thin rapidly as they
    radiate outward -- from wrist-thick at the first fork to twig-fine at the
    tips. At the branch ends, the first true leaves of the year are just
    emerging: tight clusters of five or six small leaves, still pleated and
    slightly translucent, colour somewhere between citron and yellow-green
    against the pale sky. There are perhaps twenty such clusters visible,
    scattered at the outer edges of the canopy. The tree's emotional state --
    to the extent a tree has one -- is patient renewal: this tree has stood
    through many winters and does not rush its spring.

The Environment
    The sky behind the tree is pale early-spring cerulean, lightening toward
    near-white directly above where the light is most intense. Near the horizon
    (bottom frame edge) the sky is warmer and slightly amber-tinted from the
    low sun angle. The bark texture in the foreground trunk has a rough,
    three-dimensional quality -- ridges and fissures catching the light at
    different angles. In the background (upper corners) the small outer branch
    tips are slightly softer-focused in the cool haze of the sky, demonstrating
    the atmospheric depth of the canopy's depth. The boundaries between bark
    and sky are sharp at the main trunk, soft and hazy at the delicate outer
    branches. Ground detail is not visible -- the viewer is lying on their
    back beneath the tree, looking straight up.

Technique & Palette
    Hilma af Klint Biomorphic mode -- session 257, 168th distinct mode.

    The af Klint biomorphic pass is applied after the tree is blocked in and
    built: the luminance-weighted centroid of the composition falls roughly at
    the bifurcation point of the trunk (the visual center of gravity of the
    painting), and concentric growth rings radiate outward from this point.
    The ring count is set to 4.5 so that the inner ring zone (warm push)
    encompasses the trunk and the base of the major branches, while the outer
    ring zones alternate warm/cool outward to the sky areas. The effect
    is subtle on the bark (warm tones slightly intensified in the trunk zone)
    but more visible in the sky (the cool outer rings pull the sky toward the
    cool-blue-violet of af Klint's cosmic colour, alternating with the near-
    white zones). The haze boundary glow (haze_sigma=22) creates a subtle
    luminosity at the ring transitions that reads as an otherworldly quality --
    the tree is both botanical and spiritual simultaneously.

    Shadow Bleed improvement (session 257): Warm reflected light is injected
    into the shadow zone of the trunk's near face and the dark fissures between
    bark ridges. The reflected source is the warm ground and sky ambient,
    bouncing diffuse warm light back into the shadow side of the bark. The
    bleed_sigma=10 ensures the warm tint bleeds smoothly into the deeper shadow
    zones, avoiding a sharp painted-on quality. reflect_strength=0.18 keeps
    the effect subtle -- visible as warmth rather than obvious tinting.

    Stage-by-stage palette build:
    Ground: pale cerulean-grey wash (0.86, 0.89, 0.92) -- late morning sky tone
    Block-in: dark trunk massing in bark grey (0.24, 0.20, 0.17)
    Build form: bark ridge detail and branch gradients
    Place lights: rim light on trunk edge, first-leaf citron at branch tips
    af Klint Biomorphic pass: ring resonance from bifurcation centroid
    Shadow Bleed pass: warm bounced light in bark fissures
    Edge Temperature (s256 improvement): warm/cool boundary at bark edge
    Tonal Key (s255 improvement): slight dark-key push for gravitas

    Palette: bark-dark (0.18/0.15/0.12) -- bark-grey (0.36/0.30/0.25) --
    bark-warm (0.52/0.44/0.34) -- rim-amber (0.72/0.60/0.38) --
    sky-cerulean (0.64/0.80/0.92) -- sky-pale (0.90/0.94/0.97) --
    sky-warm (0.86/0.82/0.68) -- first-leaf (0.68/0.82/0.28) --
    bark-shadow (0.26/0.24/0.22) -- callus-pale (0.72/0.68/0.60)

Mood & Intent
    The painting is about the specific patience of trees. A tree does not
    experience winter as loss -- it waits. The first leaves do not appear as
    a celebration but as a quiet fact, like the return of something that
    left without ceremony. Viewed from below, the viewer is placed in the
    position of something small -- a child, an animal, a supplicant --
    beneath a form that has been here far longer than they have and will
    remain after they leave. The af Klint biomorphic pass adds to this the
    quality of invisible growth patterns made visible: the tree's annual rings
    (recorded inside the trunk, invisible from outside) are projected outward
    as a luminous field, as if the tree's history of growth is broadcasting
    outward into the surrounding air. The mood is reverent, still, and
    quietly hopeful.
"""

import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import cairo
from PIL import Image
from stroke_engine import Painter, mix_paint

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "s257_afklint_elm_spring.png")

W, H = 720, 960
RNG = random.Random(257)


# ─── Colour constants ──────────────────────────────────────────────────────────

BARK_DARK        = (0.18, 0.15, 0.12)
BARK_GREY        = (0.36, 0.30, 0.25)
BARK_MID         = (0.44, 0.37, 0.30)
BARK_WARM        = (0.52, 0.44, 0.34)
RIM_AMBER        = (0.72, 0.60, 0.38)
BARK_SHADOW      = (0.26, 0.24, 0.22)
CALLUS_PALE      = (0.72, 0.68, 0.60)
SKY_CERULEAN     = (0.64, 0.80, 0.92)
SKY_PALE         = (0.90, 0.94, 0.97)
SKY_WARM         = (0.86, 0.82, 0.68)
SKY_OUTER        = (0.72, 0.84, 0.90)
FIRST_LEAF       = (0.68, 0.82, 0.28)
LEAF_PALE        = (0.78, 0.88, 0.48)
BRANCH_DARK      = (0.22, 0.18, 0.14)
BRANCH_MID       = (0.38, 0.32, 0.26)


def lerp(a, b, t):
    """Linear interpolate between two colour tuples."""
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def _ellipse_mask(arr, cy, cx, ry, rx):
    """Return True where (y-cy)^2/ry^2 + (x-cx)^2/rx^2 < 1."""
    h, w = arr.shape[:2]
    ys = np.arange(h).reshape(-1, 1)
    xs = np.arange(w).reshape(1, -1)
    return ((ys - cy) / ry) ** 2 + ((xs - cx) / rx) ** 2 < 1.0


def build_reference(w: int, h: int) -> Image.Image:
    """
    Build a procedural reference image for 'Elm, First Light of Spring':
    - Pale cerulean sky background
    - Massive trunk center-bottom, bifurcating at ~35% height
    - Two main structural arms reaching upper-left and upper-right
    - Secondary branches radiating from arms
    - First-leaf clusters at branch tips
    - Warm sky at lower frame, cool sky at upper frame
    - Rim light on trunk edges
    """
    arr = np.zeros((h, w, 3), dtype=np.float32)

    # ── Background: Sky ───────────────────────────────────────────────────────
    for row in range(h):
        fy = row / h
        # Bottom 20% of canvas = looking toward lower sky (warmer)
        # Top of canvas = looking up into the brightest sky
        if fy > 0.80:
            # Near-horizon warm sky at very bottom
            t = (fy - 0.80) / 0.20
            sky_col = lerp(SKY_CERULEAN, SKY_WARM, t * 0.6)
        elif fy < 0.15:
            # Near-zenith pale sky at very top
            t = (0.15 - fy) / 0.15
            sky_col = lerp(SKY_CERULEAN, SKY_PALE, t * 0.7)
        else:
            sky_col = SKY_CERULEAN
        arr[row, :, :] = sky_col

    # ── Trunk body ─────────────────────────────────────────────────────────────
    trunk_cx = int(w * 0.50)     # trunk centered
    trunk_base_half_w = int(w * 0.095)   # base width
    trunk_top_half_w  = int(w * 0.055)   # width at bifurcation point

    bifurc_y = int(h * 0.62)    # bifurcation at 62% from top (38% from bottom)

    for row in range(int(h * 0.60), h):
        fy = row / h
        # Trunk widens toward the base
        taper = (fy - 0.60) / 0.40    # 0 at bifurcation, 1 at bottom
        half_w = int(trunk_top_half_w + (trunk_base_half_w - trunk_top_half_w) * taper)
        left  = max(0, trunk_cx - half_w)
        right = min(w, trunk_cx + half_w)
        arr[row, left:right, :] = BARK_GREY

    # ── Add bark texture / value differentiation to trunk ─────────────────────
    for row in range(bifurc_y, h):
        fy = row / h
        taper = (fy - 0.62) / 0.38
        half_w = int(trunk_top_half_w + (trunk_base_half_w - trunk_top_half_w) * taper)
        left  = max(0, trunk_cx - half_w)
        right = min(w, trunk_cx + half_w)
        for col in range(left, right):
            fx_local = (col - left) / max(1, right - left)
            # Left quarter of trunk face: lit by rim from left
            if fx_local < 0.18:
                t = (0.18 - fx_local) / 0.18
                arr[row, col, :] = lerp(BARK_GREY, RIM_AMBER, t * 0.45)
            # Right edge rim light
            elif fx_local > 0.82:
                t = (fx_local - 0.82) / 0.18
                arr[row, col, :] = lerp(BARK_GREY, RIM_AMBER, t * 0.35)
            # Center face: cool backlit shadow
            elif 0.35 <= fx_local <= 0.65:
                arr[row, col, :] = BARK_SHADOW
            # Warm midtone sides
            else:
                arr[row, col, :] = BARK_MID

    # ── Bark fissures (vertical dark lines in trunk) ───────────────────────────
    fissure_cols = [
        int(trunk_cx - trunk_top_half_w * 0.55),
        int(trunk_cx - trunk_top_half_w * 0.15),
        int(trunk_cx + trunk_top_half_w * 0.20),
        int(trunk_cx + trunk_top_half_w * 0.60),
    ]
    for fc in fissure_cols:
        if 0 <= fc < w:
            for row in range(bifurc_y, h):
                fy = row / h
                taper = (fy - 0.62) / 0.38
                half_w_r = int(trunk_top_half_w + (trunk_base_half_w - trunk_top_half_w) * taper)
                if abs(fc - trunk_cx) <= half_w_r:
                    arr[row, max(0, fc-1):min(w, fc+2), :] = BARK_DARK

    # ── Callus scar at bifurcation ─────────────────────────────────────────────
    callus_cy = bifurc_y - int(h * 0.04)
    callus_cx = trunk_cx + int(w * 0.03)
    mask = _ellipse_mask(arr, callus_cy, callus_cx,
                         int(h * 0.025), int(w * 0.025))
    arr[mask] = CALLUS_PALE

    # ── Main structural arm: LEFT ──────────────────────────────────────────────
    # Arc from bifurcation sweeping upper-left
    def draw_branch(arr_ref, y0, x0, y1, x1, width_start, width_end, col_start, col_end, steps=60):
        for i in range(steps):
            t = i / steps
            y = int(y0 + (y1 - y0) * t)
            x = int(x0 + (x1 - x0) * t)
            bw = int(width_start + (width_end - width_start) * t)
            bw = max(1, bw)
            col = lerp(col_start, col_end, t)
            r_start = max(0, y - bw)
            r_end   = min(h, y + bw + 1)
            c_start = max(0, x - bw)
            c_end   = min(w, x + bw + 1)
            arr_ref[r_start:r_end, c_start:c_end, :] = col

    # Left main arm: bifurcation → upper-left
    draw_branch(arr,
        y0=bifurc_y, x0=trunk_cx - int(w * 0.02),
        y1=int(h * 0.12), x1=int(w * 0.12),
        width_start=19, width_end=7,
        col_start=BARK_GREY, col_end=BRANCH_MID,
        steps=80)

    # Right main arm: bifurcation → upper-right
    draw_branch(arr,
        y0=bifurc_y, x0=trunk_cx + int(w * 0.02),
        y1=int(h * 0.10), x1=int(w * 0.85),
        width_start=17, width_end=6,
        col_start=BARK_GREY, col_end=BRANCH_MID,
        steps=80)

    # ── Secondary branches off left arm ───────────────────────────────────────
    secondary_branches = [
        # (y_start, x_start, y_end, x_end, w_start, w_end)
        (int(h * 0.50), int(w * 0.38), int(h * 0.05), int(w * 0.05), 11, 4),
        (int(h * 0.42), int(w * 0.32), int(h * 0.08), int(w * 0.28), 9, 3),
        (int(h * 0.35), int(w * 0.26), int(h * 0.03), int(w * 0.45), 8, 3),
        (int(h * 0.28), int(w * 0.20), int(h * 0.02), int(w * 0.65), 7, 2),
        # Off right arm
        (int(h * 0.48), int(w * 0.62), int(h * 0.07), int(w * 0.70), 10, 4),
        (int(h * 0.38), int(w * 0.70), int(h * 0.05), int(w * 0.90), 9, 3),
        (int(h * 0.28), int(w * 0.78), int(h * 0.04), int(w * 0.98), 7, 2),
        # Upward secondary
        (int(h * 0.45), int(w * 0.48), int(h * 0.02), int(w * 0.50), 10, 3),
        (int(h * 0.40), int(w * 0.44), int(h * 0.04), int(w * 0.35), 8, 3),
        (int(h * 0.38), int(w * 0.56), int(h * 0.04), int(w * 0.68), 8, 3),
    ]
    for (y0, x0, y1, x1, ws, we) in secondary_branches:
        draw_branch(arr, y0, x0, y1, x1, ws, we,
                    BRANCH_MID, BRANCH_DARK, steps=50)

    # ── Tertiary fine branches ─────────────────────────────────────────────────
    tertiary = [
        (int(h * 0.20), int(w * 0.15), int(h * 0.02), int(w * 0.02), 4, 1),
        (int(h * 0.18), int(w * 0.22), int(h * 0.01), int(w * 0.12), 3, 1),
        (int(h * 0.15), int(w * 0.30), int(h * 0.01), int(w * 0.22), 3, 1),
        (int(h * 0.12), int(w * 0.18), int(h * 0.00), int(w * 0.35), 2, 1),
        (int(h * 0.10), int(w * 0.50), int(h * 0.00), int(w * 0.48), 3, 1),
        (int(h * 0.12), int(w * 0.66), int(h * 0.01), int(w * 0.82), 3, 1),
        (int(h * 0.15), int(w * 0.72), int(h * 0.02), int(w * 0.95), 3, 1),
        (int(h * 0.22), int(w * 0.80), int(h * 0.04), int(w * 0.99), 3, 1),
        (int(h * 0.08), int(w * 0.43), int(h * 0.00), int(w * 0.28), 2, 1),
        (int(h * 0.08), int(w * 0.55), int(h * 0.00), int(w * 0.72), 2, 1),
    ]
    for (y0, x0, y1, x1, ws, we) in tertiary:
        draw_branch(arr, y0, x0, y1, x1, ws, we,
                    BRANCH_DARK, BRANCH_DARK, steps=30)

    # ── First-leaf clusters at branch tips ─────────────────────────────────────
    leaf_positions = [
        (int(h * 0.03), int(w * 0.07),  18),
        (int(h * 0.02), int(w * 0.15),  14),
        (int(h * 0.02), int(w * 0.28),  15),
        (int(h * 0.01), int(w * 0.45),  16),
        (int(h * 0.00), int(w * 0.50),  12),
        (int(h * 0.01), int(w * 0.65),  15),
        (int(h * 0.02), int(w * 0.80),  14),
        (int(h * 0.03), int(w * 0.95),  16),
        (int(h * 0.04), int(w * 0.98),  12),
        (int(h * 0.06), int(w * 0.42),  13),
        (int(h * 0.06), int(w * 0.60),  13),
        (int(h * 0.05), int(w * 0.36),  11),
        (int(h * 0.04), int(w * 0.70),  12),
        (int(h * 0.07), int(w * 0.23),  11),
        (int(h * 0.08), int(w * 0.50),  10),
    ]
    for (lcy, lcx, lr) in leaf_positions:
        for dy in range(-lr, lr + 1):
            for dx in range(-lr, lr + 1):
                dist = math.sqrt(dy * dy + dx * dx)
                if dist <= lr:
                    ry = lcy + dy
                    rx = lcx + dx
                    if 0 <= ry < h and 0 <= rx < w:
                        falloff = 1.0 - dist / lr
                        leaf_col = lerp(FIRST_LEAF, LEAF_PALE, falloff * 0.4)
                        # Blend over sky background
                        sky_row = arr[ry, rx, :].copy()
                        blend = falloff ** 0.7
                        arr[ry, rx, :] = lerp(sky_row, leaf_col, blend * 0.85)

    # ── Rim light on left arm and trunk silhouette edge ───────────────────────
    # Apply a narrow warm rim on the right edge of left arm
    # (already handled in the branch gradient above, but add a thin line)
    for row in range(int(h * 0.10), bifurc_y):
        fy = row / h
        # Find leftmost bark pixel in this row and brighten it
        for col in range(w):
            p = arr[row, col, :]
            # Detect left bark edge
            if p[0] > 0.2 and p[0] < 0.65:
                # Check if sky pixel immediately to left
                if col == 0 or arr[row, col - 1, 0] > 0.55:
                    arr[row, max(0, col):min(w, col + 2), :] = RIM_AMBER
                    break

    arr_uint8 = np.clip(arr * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(arr_uint8, "RGB")


def main():
    print("Session 257 -- Elm, First Light of Spring (after Hilma af Klint)")
    print(f"Canvas: {W}×{H}")
    print()

    ref = build_reference(W, H)
    print("Reference built.")

    p = Painter(W, H)

    # Ground: pale cerulean-grey sky wash
    print("Toning ground...")
    p.tone_ground((0.86, 0.89, 0.92), texture_strength=0.025)

    # Block in masses: sky, trunk, arms
    print("Blocking in masses...")
    p.block_in(ref, stroke_size=36, n_strokes=140)

    # Build form: bark detail, branch gradients
    print("Building form...")
    p.build_form(ref, stroke_size=14, n_strokes=90)

    # Place lights: rim light on trunk edges, first-leaf citron
    print("Placing lights...")
    p.place_lights(ref, stroke_size=6, n_strokes=60)

    # ── af Klint Biomorphic pass (168th mode) ──────────────────────────────────
    print("Applying Hilma af Klint Biomorphic pass...")
    p.hilma_af_klint_biomorphic_pass(
        ring_count=4.5,         # 4.5 concentric zones from bifurcation centroid
        ring_amplitude=0.28,    # moderate ring chromatic amplitude
        warm_push=0.06,         # gentle warm push in inner ring zones (bark)
        cool_push=0.07,         # gentle cool push in outer ring zones (sky)
        haze_sigma=22.0,        # wide luminous haze at ring boundaries
        haze_strength=0.12,     # subtle luminosity at ring transitions
        opacity=0.72,
    )

    # ── Shadow Bleed pass (improvement) ─────────────────────────────────────────
    print("Applying Shadow Bleed pass...")
    p.paint_shadow_bleed_pass(
        shadow_threshold=0.38,   # shadow = bark fissures + deep shadow face
        bright_threshold=0.70,   # bright = sky + rim light on trunk edge
        bleed_sigma=10.0,        # wide bleed: warm light bleeds deep into bark shadow
        reflect_strength=0.18,   # subtle warm bounce
        warm_r=0.82,             # warm amber bounce colour (afternoon light)
        warm_g=0.62,
        warm_b=0.28,
        opacity=0.72,
    )

    # ── Edge Temperature pass (s256) ────────────────────────────────────────────
    print("Applying Edge Temperature pass...")
    p.paint_edge_temperature_pass(
        warm_hue_center=0.08,    # amber-warm (rim light, leaf yellow-green)
        warm_hue_width=0.20,
        cool_hue_center=0.58,    # cerulean sky
        cool_hue_width=0.18,
        gradient_zone_px=3.0,
        contrast_strength=0.10,  # gentle -- this is a naturalistic painting
        opacity=0.60,
    )

    # ── Tonal Key pass (s255) ──────────────────────────────────────────────────
    print("Applying Tonal Key pass...")
    p.paint_tonal_key_pass(
        target_key=0.58,        # slightly high-key -- spring light quality
        key_strength=2.5,
        dither_amplitude=0.004,
        opacity=0.45,
    )

    # ── Contour Weight pass (s254) ─────────────────────────────────────────────
    print("Applying Contour Weight pass...")
    p.paint_contour_weight_pass(
        contour_threshold=0.05,
        max_weight=0.80,
        weight_exponent=1.3,
        taper_strength=0.20,
        opacity=0.45,
    )

    # Save
    print(f"Saving to {OUTPUT_PATH}...")
    p.save(OUTPUT_PATH)
    print("Done.")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
