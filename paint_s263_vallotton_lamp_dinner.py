"""
paint_s263_vallotton_lamp_dinner.py -- Session 263

"Dinner, by Lamplight" -- in the manner of Félix Vallotton

Image Description
-----------------
Subject & Composition
    A lamp-lit dining room in a bourgeois Paris apartment, seen at a slight
    elevation — as if the viewer stands in a doorway, half-concealed, looking
    across the room at an oblique angle. The room is divided by the harsh drama
    of a single suspended kerosene lamp: directly below it, the round dinner
    table is an island of warm amber light. Three figures are seated at the
    table: a woman in a dark dress, seen from behind, on the near side; a man
    facing slightly left at the far side, his face half-lit by the lamp; and a
    second woman at the right, her profile cut from the lamplight into near-
    silhouette. The floor is dark warm parquet, its surface catching only the
    weakest reflected glow from the lamp. The walls dissolve into near-black at
    their edges, pressing the scene inward toward the island of light.

The Figure
    The three figures are treated in the Vallotton manner — not as psychological
    portraits but as human masses, silhouetted against or submerged within the
    lamp's geometry. The near woman's dark dress forms the largest mass, a flat
    near-black shape against the warm tablecloth. The facing man is defined by
    the half-lit side of his face — the lamp illuminates his forehead and left
    cheek while the right side falls toward black. The profile woman is almost
    entirely dark, her silhouette reading as a single flat shape cut from the
    surrounding lamplight. Their emotional states are suspended and ambiguous:
    they are at a shared meal but the tension Vallotton valued — the distance
    between bodies at the same table — is the subject. Nothing dramatic is
    happening; everything is slightly wrong.

The Environment
    The kerosene lamp hangs at centre-upper-canvas, its amber glass shade
    pooling warm light in a cone downward. The table beneath it holds a white
    tablecloth with a single dark wine bottle at centre, two wine glasses of
    amber, a bread plate, and the soft white of porcelain dishes. The chair
    backs in the foreground are dark lacquered wood. The floor is warm parquet,
    catching a thin reflected glow from the table's edges. The walls are papered
    in a deep warm dark, almost invisible except at the boundary of the lamp
    zone where the wallpaper colour is faintly suggested — a dark burgundy,
    perhaps, or deep olive. A curtained doorway occupies the left background,
    through which a slightly brighter room is barely visible — a typical Vallotton
    mise-en-abyme of observed domestic spaces. The boundary between light and
    shadow is extreme: not a gradient but nearly a geometric cut, the circle of
    the lamp defining a hard luminance threshold that leaves the periphery in
    near-total darkness.

Technique & Palette
    Vallotton Dark Interior mode -- session 263, 174th distinct painting mode.

    Stage 1 SHADOW CRUSH (shadow_crush=0.38, crush_steepness=6.0):
    All pixels with luminance below 0.38 are aggressively compressed toward
    near-black via a sigmoid function with steepness=6.0. This creates the
    characteristic Vallotton darkness: flat, total, lacquer-black shadows in
    which forms are only suggested by slight variations in the near-black zone.

    Stage 2 RADIAL LAMP WARMTH POOL (lamp_cx=0.48, lamp_cy=0.28,
    lamp_radius=0.28, lamp_strength=0.34):
    A concentrated radial warm-amber pool (0.96, 0.88, 0.62) centred on the
    hanging lamp at image position (0.48, 0.28) with quadratic falloff over
    radius 0.28 of image width. This creates the concentric warm island that
    defines the table zone and gives the faces their half-lit quality.

    Stage 3 JAPANESE INK CONTOUR (contour_thresh=0.05, contour_dark=0.55):
    Hard Sobel-based contours are detected and darkened multiplicatively,
    adding the woodcut-quality ink lines that define the silhouette of the
    near woman against the tablecloth, the lamp's cord against the ceiling,
    and the chair backs in the foreground. These are not soft edges -- they
    are hard lines.

    Flat Zone improvement (s263): Applied to create the Nabis flat-colour-zone
    quality using spatial median filtering with edge-preserved composite. This
    unifies the dark zones into near-uniform flat fields and the warm mid-zones
    into smooth warm planes.

    Colour build:
    Ground: near-black imprimatura (0.18, 0.15, 0.12) -- dark, warm, total
    Underpainting: deep warm umber structure
    Block-in: lamp zone warm, shadow zones near-black, tablecloth cream
    Build form: face planes, dress mass, wine bottle / glasses
    Place lights: lamp highlight, tablecloth edge, wine amber
    Flat Zone pass (s263): zone unification, edge preservation
    Vallotton Dark Interior (s263 174th mode): shadow crush, lamp pool, contour
    Triple Zone Glaze (s261): deep cool shadows, warm lamp mid, cream highlight
    Shadow Bleed (s257): warm reflected light on floor and walls

    Full palette:
    lamp-amber (0.96/0.88/0.62) -- near-black (0.10/0.08/0.06) --
    tablecloth-cream (0.90/0.86/0.76) -- dark-dress (0.16/0.12/0.10) --
    skin-lamp-lit (0.88/0.72/0.52) -- skin-shadow (0.42/0.32/0.24) --
    floor-warm (0.36/0.28/0.18) -- wall-dark (0.22/0.18/0.14) --
    wine-amber (0.72/0.52/0.22) -- bottle-dark (0.14/0.16/0.12) --
    chair-dark (0.20/0.16/0.12) -- doorway-beyond (0.55/0.48/0.38)

Mood & Intent
    This image embodies the Vallotton domestic: the ordinary meal in the
    impossible light. The kerosene lamp makes philosophers of everyone at the
    table -- their faces half-lit, their expressions impossible to read entirely.
    The viewer stands in the doorway, uninvited, watching a private scene.
    Nothing in the room acknowledges the observer. The extreme darkness at the
    periphery presses the world inward toward the lamp's warmth, making the
    table into a kind of sanctuary -- a warm island in the surrounding dark --
    while the figures at the table remain isolated from each other despite their
    physical proximity. The viewer should feel the specific weight of a fin-de-
    siècle Paris evening: the amber glow, the silence between people who have
    said everything and not enough, and the voyeuristic complicity of seeing
    what you were not meant to see.
"""

import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "s263_vallotton_lamp_dinner.png")

W, H = 1200, 1200  # square — lamplight scene is symmetric around the light source

# ── Palette ────────────────────────────────────────────────────────────────────

NEAR_BLACK     = (0.10, 0.08, 0.06)
DEEP_DARK      = (0.18, 0.14, 0.10)
DARK_WARM      = (0.25, 0.20, 0.14)
LAMP_AMBER     = (0.96, 0.88, 0.62)
LAMP_MID       = (0.78, 0.66, 0.44)
LAMP_EDGE      = (0.52, 0.42, 0.28)
TABLECLOTH     = (0.90, 0.86, 0.76)
TABLECLOTH_SH  = (0.68, 0.62, 0.50)
SKIN_LIT       = (0.88, 0.72, 0.52)
SKIN_HALF      = (0.62, 0.48, 0.32)
SKIN_DARK      = (0.38, 0.28, 0.18)
DARK_DRESS     = (0.16, 0.12, 0.10)
WINE_AMBER     = (0.72, 0.52, 0.22)
BOTTLE_DARK    = (0.14, 0.16, 0.12)
CHAIR_DARK     = (0.20, 0.16, 0.12)
FLOOR_WARM     = (0.36, 0.28, 0.18)
FLOOR_REFLECT  = (0.48, 0.38, 0.24)
WALL_DARK      = (0.22, 0.18, 0.14)
DOORWAY_LIGHT  = (0.55, 0.48, 0.38)
LAMP_GLASS     = (0.92, 0.84, 0.60)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(a[i] * (1.0 - t) + b[i] * t for i in range(len(a)))


def lamp_weight(px, py, cx, cy, radius):
    """Quadratic falloff weight from lamp centre."""
    dx = (px / W - cx)
    dy = (py / H - cy)
    d = math.sqrt(dx * dx + dy * dy)
    return max(0.0, 1.0 - d / radius) ** 2


def build_reference(w: int, h: int) -> Image.Image:
    """Build procedural reference for 'Dinner, by Lamplight'."""
    arr = np.zeros((h, w, 3), dtype=np.float32)

    # Lamp position (image coordinates as fractions)
    lamp_cx   = 0.48
    lamp_cy   = 0.25
    lamp_r    = 0.30   # radius of warmth pool
    table_cy  = 0.54   # table vertical centre

    # ── Background: near-black walls everywhere ───────────────────────────────
    arr[:, :, :] = NEAR_BLACK

    # ── Ceiling (top 22%) ─────────────────────────────────────────────────────
    ceil_bot = int(h * 0.22)
    for row in range(ceil_bot):
        fy = row / max(1, ceil_bot)
        for col in range(w):
            wt = lamp_weight(col, row, lamp_cx, lamp_cy, lamp_r * 1.2)
            ceiling_col = lerp(NEAR_BLACK, LAMP_EDGE, wt * 0.45)
            arr[row, col, :] = ceiling_col

    # Lamp cord (narrow vertical line from top to lamp)
    lamp_px = int(lamp_cx * w)
    lamp_py = int(lamp_cy * h)
    cord_w = max(2, int(w * 0.004))
    for row in range(0, lamp_py):
        for col in range(max(0, lamp_px - cord_w), min(w, lamp_px + cord_w)):
            arr[row, col, :] = DARK_WARM

    # Lamp globe
    lamp_globe_r = int(w * 0.045)
    for dy in range(-lamp_globe_r, lamp_globe_r):
        for dx in range(-lamp_globe_r, lamp_globe_r):
            cy = lamp_py + dy; cx = lamp_px + dx
            if 0 <= cy < h and 0 <= cx < w:
                d = math.sqrt(dx * dx + dy * dy)
                if d < lamp_globe_r:
                    t = d / lamp_globe_r
                    arr[cy, cx, :] = lerp(LAMP_GLASS, LAMP_AMBER, t * 0.6)

    # ── Lamp cone / light pool ─────────────────────────────────────────────────
    for row in range(lamp_py, h):
        for col in range(w):
            wt = lamp_weight(col, row, lamp_cx, lamp_cy, lamp_r)
            if wt > 0.01:
                cur = arr[row, col, :]
                arr[row, col, :] = lerp(cur, LAMP_MID, wt * 0.6)

    # ── Walls ──────────────────────────────────────────────────────────────────
    wall_top    = ceil_bot
    floor_top   = int(h * 0.70)

    for row in range(wall_top, floor_top):
        for col in range(w):
            wt = lamp_weight(col, row, lamp_cx, lamp_cy, lamp_r * 1.1)
            wall_base = DARK_WARM if col < w * 0.15 else NEAR_BLACK
            arr[row, col, :] = lerp(wall_base, LAMP_EDGE, wt * 0.28)

    # Doorway (left background, slightly brighter room beyond)
    door_left  = int(w * 0.04)
    door_right = int(w * 0.15)
    door_top   = int(h * 0.28)
    door_bot   = int(h * 0.68)
    for row in range(door_top, door_bot):
        for col in range(door_left, door_right):
            fy = (row - door_top) / max(1, door_bot - door_top)
            fx = (col - door_left) / max(1, door_right - door_left)
            inner_t = min(fx, fy, 1.0 - fx, 1.0 - fy) * 5.0
            arr[row, col, :] = lerp(DOORWAY_LIGHT, NEAR_BLACK, (1.0 - inner_t) * 0.7)

    # ── Floor ──────────────────────────────────────────────────────────────────
    for row in range(floor_top, h):
        fy = (row - floor_top) / max(1, h - floor_top)
        for col in range(w):
            wt = lamp_weight(col, row, lamp_cx, lamp_cy, lamp_r * 0.75)
            floor_base = lerp(NEAR_BLACK, FLOOR_WARM, fy * 0.2)
            arr[row, col, :] = lerp(floor_base, FLOOR_REFLECT, wt * 0.38)

    # ── Round dining table ─────────────────────────────────────────────────────
    table_cx   = int(lamp_cx * w)
    table_cy_px = int(table_cy * h)
    table_rx   = int(w * 0.30)
    table_ry   = int(h * 0.12)

    for row in range(table_cy_px - table_ry, table_cy_px + table_ry):
        for col in range(table_cx - table_rx, table_cx + table_rx):
            if 0 <= row < h and 0 <= col < w:
                ex = (col - table_cx) / table_rx
                ey = (row - table_cy_px) / table_ry
                if ex * ex + ey * ey <= 1.0:
                    wt = lamp_weight(col, row, lamp_cx, lamp_cy, lamp_r)
                    cloth = lerp(TABLECLOTH_SH, TABLECLOTH, wt * 1.2)
                    arr[row, col, :] = cloth

    # Wine bottle
    bottle_cx = int(lamp_cx * w + w * 0.02)
    bottle_top = int(table_cy_px - table_ry * 0.9)
    bottle_bot = int(table_cy_px - table_ry * 0.05)
    bottle_w   = max(4, int(w * 0.015))
    for row in range(bottle_top, bottle_bot):
        for col in range(max(0, bottle_cx - bottle_w), min(w, bottle_cx + bottle_w)):
            arr[row, col, :] = BOTTLE_DARK

    # Wine glasses (two, left and right of bottle)
    for gc in [bottle_cx - int(w * 0.06), bottle_cx + int(w * 0.06)]:
        glass_top = int(table_cy_px - table_ry * 0.75)
        glass_bot = int(table_cy_px - table_ry * 0.10)
        glass_w   = max(2, int(w * 0.008))
        for row in range(glass_top, glass_bot):
            for col in range(max(0, gc - glass_w), min(w, gc + glass_w)):
                fy = (row - glass_top) / max(1, glass_bot - glass_top)
                arr[row, col, :] = lerp(WINE_AMBER, LAMP_AMBER, fy * 0.4 + 0.3)

    # ── Near figure: woman in dark dress, seen from behind ────────────────────
    fig1_cx = int(lamp_cx * w + w * 0.02)
    fig1_top = int(table_cy_px + table_ry * 0.25)
    fig1_bot = int(h * 0.78)
    fig1_w   = int(w * 0.18)
    for row in range(fig1_top, min(h, fig1_bot)):
        fy = (row - fig1_top) / max(1, fig1_bot - fig1_top)
        fw = int(fig1_w * (0.6 + fy * 0.5))
        for col in range(max(0, fig1_cx - fw // 2), min(w, fig1_cx + fw // 2)):
            wt = lamp_weight(col, row, lamp_cx, lamp_cy, lamp_r * 0.6)
            arr[row, col, :] = lerp(DARK_DRESS, DARK_WARM, wt * 0.15)

    # Head of near figure
    head1_cx = fig1_cx - int(w * 0.01)
    head1_cy = int(table_cy_px + table_ry * 0.10)
    head1_r  = int(w * 0.040)
    for dy in range(-head1_r, head1_r):
        for dx in range(-head1_r, head1_r):
            cy = head1_cy + dy; cx = head1_cx + dx
            if 0 <= cy < h and 0 <= cx < w:
                d = math.sqrt(dx * dx + dy * dy)
                if d < head1_r:
                    # Hair, seen from behind
                    arr[cy, cx, :] = lerp(DARK_DRESS, DARK_WARM, 0.1)

    # ── Far figure: man half-lit by lamp ─────────────────────────────────────
    fig2_cx   = int(lamp_cx * w - w * 0.12)
    fig2_row  = int(table_cy_px - table_ry * 0.25)
    head2_r   = int(w * 0.045)
    for dy in range(-head2_r, head2_r):
        for dx in range(-head2_r, head2_r):
            cy = fig2_row + dy; cx = fig2_cx + dx
            if 0 <= cy < h and 0 <= cx < w:
                d = math.sqrt(dx * dx + dy * dy)
                if d < head2_r:
                    t = d / head2_r
                    # Half lit: left side lit by lamp, right side dark
                    fx_frac = (dx + head2_r) / (2 * head2_r)
                    lit_side = max(0.0, 1.0 - fx_frac * 2.5)
                    skin = lerp(SKIN_DARK, SKIN_LIT, lit_side * 0.8)
                    arr[cy, cx, :] = lerp(skin, NEAR_BLACK, t * 0.2)

    # Body of far man
    for row in range(fig2_row + head2_r, min(h, fig2_row + head2_r + int(h * 0.15))):
        fy = (row - (fig2_row + head2_r)) / max(1, int(h * 0.15))
        fw = max(4, int(head2_r * 1.6 * (0.8 + fy * 0.4)))
        for col in range(max(0, fig2_cx - fw // 2), min(w, fig2_cx + fw // 2)):
            wt = lamp_weight(col, row, lamp_cx, lamp_cy, lamp_r)
            arr[row, col, :] = lerp(NEAR_BLACK, DARK_WARM, wt * 0.25)

    # ── Right profile figure: woman in silhouette ─────────────────────────────
    fig3_cx  = int(lamp_cx * w + w * 0.20)
    fig3_row = int(table_cy_px - table_ry * 0.25)
    head3_r  = int(w * 0.042)
    for dy in range(-head3_r, head3_r):
        for dx in range(-head3_r, head3_r):
            cy = fig3_row + dy; cx = fig3_cx + dx
            if 0 <= cy < h and 0 <= cx < w:
                d = math.sqrt(dx * dx + dy * dy)
                if d < head3_r:
                    # Almost entirely dark profile
                    t = d / head3_r
                    wt = lamp_weight(cx, cy, lamp_cx, lamp_cy, lamp_r * 0.8)
                    arr[cy, cx, :] = lerp(NEAR_BLACK, SKIN_HALF, wt * 0.45 * (1 - t * 0.5))

    # Body of right figure
    for row in range(fig3_row + head3_r, min(h, fig3_row + head3_r + int(h * 0.15))):
        fy = (row - (fig3_row + head3_r)) / max(1, int(h * 0.15))
        fw = max(4, int(head3_r * 1.5))
        for col in range(max(0, fig3_cx - fw // 2), min(w, fig3_cx + fw // 2)):
            arr[row, col, :] = lerp(NEAR_BLACK, DARK_WARM, 0.08)

    # ── Chair backs (foreground) ───────────────────────────────────────────────
    for chair_x in [int(lamp_cx * w - w * 0.28), int(lamp_cx * w + w * 0.25)]:
        chair_top = int(h * 0.62)
        chair_bot = int(h * 0.85)
        chair_w   = max(3, int(w * 0.025))
        for row in range(chair_top, chair_bot):
            for col in range(max(0, chair_x - chair_w), min(w, chair_x + chair_w)):
                arr[row, col, :] = CHAIR_DARK

    arr = np.clip(arr, 0.0, 1.0)
    return Image.fromarray((arr * 255).astype(np.uint8), "RGB")


def main():
    print("Session 263 -- Dinner, by Lamplight (after Félix Vallotton)")
    print(f"Canvas: {W}×{H}")
    print()

    ref = build_reference(W, H)
    ref_arr = np.array(ref)   # uint8 (H, W, 3)
    print("Reference built.")

    p = Painter(W, H, seed=263)

    # ── Ground ────────────────────────────────────────────────────────────────
    print("Toning ground...")
    p.tone_ground((0.18, 0.15, 0.12), texture_strength=0.012)

    # ── Underpainting ─────────────────────────────────────────────────────────
    print("Underpainting...")
    p.underpainting(ref_arr, stroke_size=54, n_strokes=220)
    p.underpainting(ref_arr, stroke_size=44, n_strokes=240)

    # ── Block-in ─────────────────────────────────────────────────────────────
    print("Blocking in masses...")
    p.block_in(ref_arr, stroke_size=34, n_strokes=440)
    p.block_in(ref_arr, stroke_size=22, n_strokes=460)

    # ── Build form ───────────────────────────────────────────────────────────
    print("Building form...")
    p.build_form(ref_arr, stroke_size=12, n_strokes=500)
    p.build_form(ref_arr, stroke_size=6,  n_strokes=420)

    # ── Place lights ─────────────────────────────────────────────────────────
    print("Placing lights and lamp accents...")
    p.place_lights(ref_arr, stroke_size=4, n_strokes=280)

    # ── Flat Zone pass (s263 improvement) ────────────────────────────────────
    print("Applying Flat Zone pass...")
    p.paint_flat_zone_pass(
        zone_radius=5,
        preserve_edges=0.80,
        ground_r=0.72,
        ground_g=0.58,
        ground_b=0.42,
        ground_strength=0.06,
        edge_sigma=1.5,
        noise_seed=263,
        opacity=0.60,
    )

    # ── Vallotton Dark Interior pass (174th mode) ─────────────────────────────
    print("Applying Vallotton Dark Interior pass (174th mode)...")
    p.vallotton_dark_interior_pass(
        shadow_crush=0.38,
        crush_steepness=6.0,
        lamp_cx=0.48,
        lamp_cy=0.25,
        lamp_radius=0.28,
        lamp_r=0.96,
        lamp_g=0.88,
        lamp_b=0.62,
        lamp_strength=0.34,
        contour_sigma=1.2,
        contour_thresh=0.055,
        contour_dark=0.55,
        noise_seed=263,
        opacity=0.80,
    )

    # ── Triple Zone Glaze (s261 improvement) ─────────────────────────────────
    print("Applying Triple Zone Glaze pass...")
    p.paint_triple_zone_glaze_pass(
        shadow_pivot=0.22,
        highlight_pivot=0.62,
        zone_feather=0.10,
        shadow_r=0.10,
        shadow_g=0.08,
        shadow_b=0.14,
        shadow_opacity=0.14,
        mid_r=0.72,
        mid_g=0.60,
        mid_b=0.38,
        mid_opacity=0.10,
        highlight_r=0.96,
        highlight_g=0.88,
        highlight_b=0.68,
        highlight_opacity=0.12,
        feather_sigma=9.0,
        noise_seed=263,
        opacity=0.72,
    )

    # ── Shadow Bleed (s257 improvement) ──────────────────────────────────────
    print("Applying Shadow Bleed pass...")
    p.paint_shadow_bleed_pass(
        shadow_threshold=0.35,
        bright_threshold=0.72,
        bleed_sigma=10.0,
        reflect_strength=0.10,
        warm_r=0.78,
        warm_g=0.62,
        warm_b=0.38,
        opacity=0.32,
    )

    # ── Save ──────────────────────────────────────────────────────────────────
    print(f"Saving to {OUTPUT_PATH}...")
    p.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
