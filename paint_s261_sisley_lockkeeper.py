"""
paint_s261_sisley_lockkeeper.py -- Session 261

"The Lock-Keeper's Garden at Flood Tide" -- in the manner of Alfred Sisley

Image Description
-----------------
Subject & Composition
    A small lock-keeper's cottage garden on the bank of a Thames tributary in
    late October. The river has risen over its normal level and the lower third
    of the garden -- the vegetable beds, the path of cinders, the low wooden
    fence -- is submerged beneath still flood-water, pewter-coloured and flat.
    The composition is horizontal: sky takes up the upper 42% of the canvas,
    water and reflected garden the lower 58%. The garden's back wall, a low
    brick parapet, marks the horizontal boundary between the earth zone and the
    sky. A single leafless willow occupies the right third, its trailing
    branches touching the water surface. The cottage gable is visible at the
    far left, its pale cream stucco face catching the diffuse midday light.

The Environment
    Late October, midday, overcast. The sky is a characteristic Sisley silver:
    pale cool grey-white with a very faint warm band at the horizon -- a thin
    line of ivory just above the roofline of the cottage, the only warmth in
    the picture. The cloud layer is smooth and even, giving no shadows. The
    flood-water is pewter grey, almost perfectly still, reflecting the sky and
    the pale shapes of the submerged garden. A few late cosmos flowers --
    white, pale rose -- project above the water surface on stems that disappear
    below. A small wooden punt is tied to the willow trunk, its flat bottom
    dark-stained, its painter rope yellow-grey and slack. The willow branches
    are bare, fine grey-brown filaments against the silver sky. The cottage
    chimney emits a thin vertical thread of white smoke that bends almost
    imperceptibly to the left. The brick parapet garden wall has a warm
    reddish undertone that is the only colour note stronger than silver in
    the whole composition. The garden beyond the flood zone -- a narrow strip
    visible above the water line -- shows a rosebush past flowering, its hips
    orange-red and vivid against the grey.

The Figure
    No human figure is present. The implied presence of the lock-keeper is the
    punt, the smoke, the neatly kept garden (now submerged). The absence of
    the human is not loss -- it is the particular vacancy of Sisley's paintings,
    in which the world goes on without need of observation.

Technique & Palette
    Sisley Silver Veil mode -- session 261, 172nd distinct mode.

    Stage 1 SILVER SKY BAND (sky_fraction=0.42, sky_strength=0.40):
    The upper 42% of the canvas receives a linear vertical silver tint, strongest
    at the top edge, blending toward silver-grey (0.84, 0.85, 0.88). This
    concentrates the characteristic Sisley sky silverness at the top and lets
    it fade smoothly to the land tones without a hard transition.

    Stage 2 MIDGROUND SILVER ATMOSPHERIC HAZE (haze_center=0.56,
    haze_strength=0.35): A Gaussian bell centered at luminance 0.56 blends
    mid-luminance pixels toward the cool neutral silver (0.78, 0.78, 0.81).
    This affects the water surface, the submerged garden zone, and the middle-
    distance willow mass -- creating the characteristic Sisley silver mist that
    makes his midgrounds recede without going dark or cold.

    Stage 3 HORIZONTAL SKY MOTION BLUR (sky_blur_sigma=7.0, sky_blur_opacity=0.50):
    A strictly 1D horizontal Gaussian blur, applied only in the sky zone with
    a vertically decaying weight, creates the horizontal wind-driven quality of
    Sisley's cloud painting. It smooths the silver sky without blurring the
    land-sky boundary, preserving the horizon band structure.

    Triple Zone Glaze improvement: Applied at the end with shadow_opacity=0.10,
    mid_opacity=0.07, highlight_opacity=0.12 -- adding a faint cool blue push
    in shadows (water depth), warm neutral in midtones (flood surface), and a
    cream lift in highlights (cottage wall, horizon band).

    Stage-by-stage palette build:
    Ground: silver-grey overcast imprimatura (0.80, 0.82, 0.80)
    Block-in: sky, water, cottage, willow masses
    Build form: garden detail, water reflections, willow branch structure
    Place lights: horizon band warmth, cottage highlight, water surface specular
    Sisley Silver Veil pass: sky silver, midground haze, horizontal sky blur
    Triple Zone Glaze: shadow cool, midtone neutral, highlight cream
    Atmospheric Recession pass: subtle far-wall softening
    Tonal Key pass: confirm mid-high key

    Palette: silver-sky (0.84/0.85/0.88) -- pewter-water (0.65/0.67/0.70) --
    cottage-cream (0.90/0.88/0.82) -- willow-grey (0.45/0.44/0.40) --
    willow-branch (0.38/0.36/0.32) -- brick-warm (0.62/0.44/0.36) --
    horizon-ivory (0.92/0.90/0.82) -- cosmos-white (0.90/0.89/0.86) --
    cosmos-rose (0.82/0.68/0.66) -- rosehip-red (0.75/0.38/0.28) --
    punt-dark (0.28/0.24/0.20) -- flood-reflect (0.70/0.72/0.76) --
    smoke-white (0.88/0.88/0.86) -- garden-earth (0.55/0.48/0.38)

Mood & Intent
    The image carries the particular Sisley quality: weather as emotional state.
    The flood is neither dramatic nor distressing -- it is simply what happened
    overnight, and now the garden is underwater and the lock-keeper has gone
    indoors and lit the fire. The silver of the sky is reflected perfectly in
    the pewter water below, so the canvas is unified top to bottom by the same
    cool neutral tone. The rosehips are the one vivid note -- orange-red in the
    grey -- and they perform the function of all colour accents in Sisley:
    they anchor the eye and confirm that the world is still warm, still present,
    even on an overcast October afternoon. The viewer is intended to leave
    feeling the specific quality of English autumn light on still water: hushed,
    pewter, continuous, and somehow enough.
"""

import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "s261_sisley_lockkeeper.png")

W, H = 760, 580
RNG = random.Random(261)

# ── Colour palette ─────────────────────────────────────────────────────────────

SILVER_SKY       = (0.84, 0.85, 0.88)
SKY_UPPER        = (0.80, 0.82, 0.86)
PEWTER_WATER     = (0.65, 0.67, 0.70)
WATER_REFLECT    = (0.70, 0.72, 0.76)
WATER_DARK       = (0.52, 0.54, 0.58)
COTTAGE_CREAM    = (0.90, 0.88, 0.82)
COTTAGE_SHADOW   = (0.72, 0.70, 0.65)
HORIZON_IVORY    = (0.92, 0.90, 0.82)
WILLOW_GREY      = (0.45, 0.44, 0.40)
WILLOW_BRANCH    = (0.38, 0.36, 0.32)
BRICK_WARM       = (0.62, 0.44, 0.36)
BRICK_MORTAR     = (0.55, 0.50, 0.46)
COSMOS_WHITE     = (0.90, 0.89, 0.86)
COSMOS_ROSE      = (0.82, 0.68, 0.66)
ROSEHIP_RED      = (0.75, 0.38, 0.28)
PUNT_DARK        = (0.28, 0.24, 0.20)
PUNT_ROPE        = (0.62, 0.60, 0.50)
SMOKE            = (0.88, 0.88, 0.86)
GARDEN_EARTH     = (0.55, 0.48, 0.38)
SUBMERGED_EARTH  = (0.48, 0.50, 0.55)  # earth seen through water


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(a[i] * (1.0 - t) + b[i] * t for i in range(len(a)))


def build_reference(w: int, h: int) -> Image.Image:
    """Build the procedural reference for Lock-Keeper's Garden at Flood Tide."""
    arr = np.zeros((h, w, 3), dtype=np.float32)

    # Layout proportions
    sky_bot   = int(h * 0.42)   # sky ends here
    horizon_y = sky_bot          # horizon line
    flood_top = int(h * 0.42)   # flood water starts
    flood_bot = int(h * 0.72)   # flood water ends (ground rises beyond)
    wall_top  = int(h * 0.44)   # brick parapet top
    wall_bot  = int(h * 0.50)   # brick parapet bottom

    cottage_lx = 0
    cottage_rx = int(w * 0.22)
    cottage_top = int(h * 0.12)

    willow_cx  = int(w * 0.78)
    willow_bot = int(h * 0.58)
    willow_top = int(h * 0.05)

    # ── Sky ───────────────────────────────────────────────────────────────────
    for row in range(sky_bot):
        fy = row / max(1, sky_bot)
        for col in range(w):
            # Silver sky, very slightly warmer near horizon
            warm_t = fy * 0.10  # a touch warmer toward horizon
            sky_col = lerp(SKY_UPPER, HORIZON_IVORY, warm_t * 0.15)
            arr[row, col, :] = sky_col

    # Horizon warmth band (thin warm strip just above the land)
    horizon_band = max(2, int(h * 0.012))
    for row in range(max(0, horizon_y - horizon_band), horizon_y):
        fy = (row - (horizon_y - horizon_band)) / max(1, horizon_band)
        for col in range(w):
            arr[row, col, :] = lerp(SILVER_SKY, HORIZON_IVORY, fy * 0.55)

    # ── Cottage (left) ────────────────────────────────────────────────────────
    for row in range(cottage_top, sky_bot):
        fy = (row - cottage_top) / max(1, sky_bot - cottage_top)
        for col in range(cottage_lx, cottage_rx):
            fx = (col - cottage_lx) / max(1, cottage_rx - cottage_lx)
            # Window light mid-left
            shade = 1.0 - fx * 0.20
            arr[row, col, :] = lerp(COTTAGE_SHADOW, COTTAGE_CREAM, shade * 0.7 + 0.3)

    # Cottage gable top (triangular roof suggestion)
    roof_peak = int(h * 0.10)
    for row in range(roof_peak, cottage_top):
        fy = (row - roof_peak) / max(1, cottage_top - roof_peak)
        roof_w = int(cottage_rx * (1.0 - fy * 0.4))
        for col in range(0, min(w, roof_w)):
            arr[row, col, :] = lerp(WILLOW_GREY, COTTAGE_SHADOW, fy * 0.5)

    # Chimney
    chimney_x = int(w * 0.08)
    chimney_w = max(3, int(w * 0.012))
    for row in range(0, cottage_top):
        for col in range(max(0, chimney_x - chimney_w), min(w, chimney_x + chimney_w)):
            arr[row, col, :] = lerp(WILLOW_GREY, BRICK_WARM, 0.5)

    # Smoke
    for row in range(max(0, int(h * 0.02)), int(h * 0.10)):
        fy = (row - int(h * 0.02)) / max(1, int(h * 0.08))
        smoke_col = chimney_x - int(fy * 4)  # drifts slightly left
        if 0 <= smoke_col < w:
            arr[row, smoke_col, :] = lerp(SILVER_SKY, SMOKE, 0.6)

    # ── Brick parapet wall ────────────────────────────────────────────────────
    for row in range(wall_top, wall_bot):
        fy = (row - wall_top) / max(1, wall_bot - wall_top)
        for col in range(w):
            # Brick pattern: repeating horizontal course
            course = math.sin(col * 0.4) * 0.04 + math.sin(row * 1.2) * 0.03
            arr[row, col, :] = lerp(BRICK_MORTAR, BRICK_WARM, 0.55 + course)

    # ── Garden above flood (thin strip visible above water) ───────────────────
    garden_strip_top = wall_bot
    garden_strip_bot = flood_top
    for row in range(garden_strip_top, min(h, garden_strip_bot + 5)):
        for col in range(w):
            arr[row, col, :] = GARDEN_EARTH

    # Rosehips (vivid orange-red accent on right side of garden strip)
    rosehip_cx = int(w * 0.55)
    rosehip_cy = int((garden_strip_top + garden_strip_bot) / 2)
    for dy in range(-int(h * 0.025), int(h * 0.025)):
        for dx in range(-int(w * 0.025), int(w * 0.025)):
            cy = rosehip_cy + dy
            cx = rosehip_cx + dx
            if 0 <= cy < h and 0 <= cx < w:
                d = math.sqrt(dx ** 2 + dy ** 2)
                if d < w * 0.018:
                    arr[cy, cx, :] = lerp(ROSEHIP_RED, GARDEN_EARTH,
                                          d / (w * 0.018))

    # ── Flood water ───────────────────────────────────────────────────────────
    for row in range(flood_top, min(h, flood_bot)):
        fy = (row - flood_top) / max(1, flood_bot - flood_top)
        for col in range(w):
            fx = col / w
            # Water reflects sky silver with slight darkening at edges
            depth_t = fy * 0.25
            edge_t  = 4.0 * fx * (1.0 - fx) * 0.15  # brighter in center
            water_col = lerp(PEWTER_WATER, WATER_REFLECT, edge_t)
            water_col = lerp(water_col, WATER_DARK, depth_t)
            arr[row, col, :] = water_col

    # Submerged garden hints (subtle) under flood
    submerged_zone = int(h * 0.06)
    for row in range(flood_top, min(h, flood_top + submerged_zone)):
        for col in range(w):
            fy = (row - flood_top) / max(1, submerged_zone)
            blend_t = (1.0 - fy) * 0.25  # fades as water deepens
            arr[row, col, :] = lerp(arr[row, col, :], SUBMERGED_EARTH, blend_t)

    # Cosmos flowers projecting above water
    for flower_cx, flower_color in [
        (int(w * 0.30), COSMOS_WHITE),
        (int(w * 0.37), COSMOS_ROSE),
        (int(w * 0.43), COSMOS_WHITE),
        (int(w * 0.26), COSMOS_ROSE),
    ]:
        stem_top = int(flood_top - h * 0.055)
        stem_bot = flood_top
        stem_x   = flower_cx
        for row in range(max(0, stem_top), stem_bot):
            if 0 <= stem_x < w:
                arr[row, stem_x, :] = lerp(WILLOW_GREY, GARDEN_EARTH, 0.5)
        # Flower head
        for dy in range(-max(2, int(h * 0.015)), max(3, int(h * 0.020))):
            for dx in range(-max(2, int(w * 0.008)), max(3, int(w * 0.012))):
                cy = stem_top + dy
                cx = flower_cx + dx
                if 0 <= cy < h and 0 <= cx < w:
                    d = math.sqrt(dx ** 2 + (dy * 1.4) ** 2)
                    if d < w * 0.010:
                        arr[cy, cx, :] = flower_color

    # ── Ground zone (below flood) ─────────────────────────────────────────────
    for row in range(flood_bot, h):
        fy = (row - flood_bot) / max(1, h - flood_bot)
        for col in range(w):
            arr[row, col, :] = lerp(GARDEN_EARTH, WILLOW_GREY, fy * 0.25)

    # ── Willow tree (right) ───────────────────────────────────────────────────
    # Trunk
    trunk_w = max(3, int(w * 0.010))
    for row in range(willow_top + int(h * 0.15), willow_bot):
        for col in range(max(0, willow_cx - trunk_w), min(w, willow_cx + trunk_w)):
            arr[row, col, :] = lerp(WILLOW_GREY, PUNT_DARK, 0.5)

    # Branches (fine trailing filaments -- approximated with thin diagonal bands)
    for branch_angle, branch_len, branch_x0 in [
        (0.55, 0.22, willow_cx - int(w * 0.01)),
        (-0.40, 0.20, willow_cx + int(w * 0.005)),
        (0.85, 0.18, willow_cx - int(w * 0.025)),
        (-0.70, 0.16, willow_cx + int(w * 0.020)),
        (0.30, 0.14, willow_cx),
    ]:
        branch_top_row = int(h * 0.08)
        branch_n = int(branch_len * h)
        for step in range(branch_n):
            by = branch_top_row + step
            bx = branch_x0 + int(step * branch_angle * (w / h))
            bw = max(1, int(w * 0.003))
            for col in range(max(0, bx - bw), min(w, bx + bw)):
                if 0 <= by < h:
                    arr[by, col, :] = lerp(
                        arr[by, col, :], WILLOW_BRANCH, 0.70
                    )

    # ── Punt (left of willow on water) ────────────────────────────────────────
    punt_lx = int(willow_cx - w * 0.09)
    punt_rx = int(willow_cx - w * 0.01)
    punt_ty = int(flood_top + h * 0.12)
    punt_by = punt_ty + max(5, int(h * 0.028))
    for row in range(punt_ty, punt_by):
        fy = (row - punt_ty) / max(1, punt_by - punt_ty)
        for col in range(punt_lx, punt_rx):
            arr[row, col, :] = lerp(PUNT_DARK, WILLOW_GREY, fy * 0.25)

    arr = np.clip(arr, 0.0, 1.0)
    return Image.fromarray((arr * 255).astype(np.uint8), "RGB")


def main():
    print("Session 261 -- Lock-Keeper's Garden at Flood Tide (after Alfred Sisley)")
    print(f"Canvas: {W}x{H}")
    print()

    ref = build_reference(W, H)
    print("Reference built.")

    p = Painter(W, H)

    # Ground: silver-grey overcast imprimatura
    print("Toning ground...")
    p.tone_ground((0.80, 0.82, 0.80), texture_strength=0.014)

    # Block in: sky, water, cottage, willow masses
    print("Blocking in masses...")
    p.block_in(ref, stroke_size=30, n_strokes=160)

    # Build form: garden detail, willow branch structure, water reflections
    print("Building form...")
    p.build_form(ref, stroke_size=12, n_strokes=130)

    # Place lights: horizon band warmth, cottage highlight, water specular
    print("Placing lights...")
    p.place_lights(ref, stroke_size=5, n_strokes=80)

    # ── Sisley Silver Veil pass (172nd mode) ──────────────────────────────────
    print("Applying Sisley Silver Veil pass...")
    p.sisley_silver_veil_pass(
        sky_fraction=0.42,
        sky_r=0.84,
        sky_g=0.85,
        sky_b=0.88,
        sky_strength=0.40,
        haze_center=0.56,
        haze_band=0.17,
        haze_r=0.78,
        haze_g=0.78,
        haze_b=0.81,
        haze_strength=0.35,
        sky_blur_sigma=7.0,
        sky_blur_opacity=0.50,
        noise_seed=261,
        opacity=0.80,
    )

    # ── Triple Zone Glaze pass (improvement) ─────────────────────────────────
    print("Applying Triple Zone Glaze pass...")
    p.paint_triple_zone_glaze_pass(
        shadow_pivot=0.30,
        highlight_pivot=0.70,
        zone_feather=0.14,
        shadow_r=0.30,
        shadow_g=0.32,
        shadow_b=0.50,
        shadow_opacity=0.10,
        mid_r=0.75,
        mid_g=0.76,
        mid_b=0.80,
        mid_opacity=0.07,
        highlight_r=0.92,
        highlight_g=0.90,
        highlight_b=0.84,
        highlight_opacity=0.12,
        feather_sigma=10.0,
        noise_seed=261,
        opacity=0.70,
    )

    # ── Atmospheric Recession pass (s259) ─────────────────────────────────────
    print("Applying Atmospheric Recession pass...")
    p.paint_atmospheric_recession_pass(
        recession_direction="top",
        haze_lift=0.03,
        desaturation=0.06,
        cool_shift_r=0.015,
        cool_shift_g=0.008,
        cool_shift_b=0.015,
        near_fraction=0.18,
        far_fraction=0.82,
        opacity=0.38,
    )

    # ── Tonal Key pass (s255) ─────────────────────────────────────────────────
    print("Applying Tonal Key pass...")
    p.paint_tonal_key_pass(
        target_key=0.62,
        key_strength=1.6,
        dither_amplitude=0.003,
        opacity=0.28,
    )

    # ── Shadow Bleed pass (s257) ──────────────────────────────────────────────
    print("Applying Shadow Bleed pass...")
    p.paint_shadow_bleed_pass(
        shadow_threshold=0.42,
        bright_threshold=0.72,
        bleed_sigma=12.0,
        reflect_strength=0.08,
        warm_r=0.88,
        warm_g=0.85,
        warm_b=0.70,
        opacity=0.38,
    )

    # Save
    print(f"Saving to {OUTPUT_PATH}...")
    p.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
