"""
paint_s259_rysselberghe_regatta.py -- Session 259

"Regatta at Nieuwpoort, Flood Tide" -- after Théo van Rysselberghe

Image Description
-----------------
Subject & Composition
    Seven sailing dinghies mid-race on the Belgian North Sea, viewed from a low
    angle at water level, slightly elevated port-side. The boats spread across
    the canvas in a loose diagonal cluster from lower-left to upper-right -- the
    nearest boat fills the lower-left quarter, large and immediate; the farthest
    are small shapes dissolving into light near the upper-right horizon. The
    composition is diagonally structured, the recession line exactly aligned with
    the race fleet's bearing.

The Figure
    The nearest boat: a small wooden racing dinghy with a white mainsail and
    red jib, heeled well over, crew of two -- one hiking out hard over the
    windward rail (silhouette, male, strain in shoulders and arms), one at the
    tiller. The sails are taut, the leading edge of the mainsail throwing a
    shadow back across the hull. The hull is natural varnished wood. Behind it,
    six more boats at varying distances -- progressively smaller, sails lightening
    and fragmenting into pure colour-point values as they recede. The farthest
    read as three white triangles and two coloured triangles against the sky.

The Environment
    Belgian North Sea coast near Nieuwpoort, late morning flood tide, midsummer.
    Sky: intense cobalt blue overhead, paling through cerulean to a warm luminous
    pale yellow-white at the horizon, where summer haze blurs sea and sky. The
    sea surface: chopped into short wavelets in the foreground -- deep viridian-
    cobalt in the troughs, cadmium-yellow highlights on wave crests. Middle
    distance: the sea unifies toward pure cobalt. Far distance: silvery blue-
    white, barely distinguishable from the hazy sky. Foreground spray catches
    the sun as diamond flashes. A grey-ochre breakwater strip sits at the horizon.

Technique & Palette
    Rysselberghe Chromatic Dot Field mode -- session 259, 170th distinct mode.
    Atmospheric Recession improvement (session 259) applied in top direction to
    drive the hazy horizon recession. Granulation pass adds physical canvas
    texture through the thin paint film. Shadow Bleed pass (s257) adds warm
    bounce into shadow zones. Edge Temperature pass (s256) sharpens the
    sail-edge warm/cool contrast.

    Palette: cobalt blue sky -- viridian sea mid -- cadmium yellow wave crest --
    white sail -- cherry red jib -- varnished wood ochre -- pale cerulean haze --
    spectral warm white horizon -- deep blue-black trough -- orange-shadow hull

Mood & Intent
    Speed, light, chromatic exuberance. The sails as pure colour-units in an
    all-encompassing field of spectral light. The water as the most complex
    colour problem in painting, shifting from viridian to cobalt to silver
    across the canvas depth. The viewer should walk away saturated with light --
    from above, reflected from below, thrown by the sails -- and with the mild
    dizziness of following the fleet into the haze.
"""

import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "s259_rysselberghe_regatta.png")

W, H = 820, 640
RNG  = random.Random(259)

# ── Colour palette ─────────────────────────────────────────────────────────────

SKY_COBALT       = (0.14, 0.38, 0.78)
SKY_CERULEAN     = (0.48, 0.70, 0.90)
SKY_HAZE         = (0.88, 0.90, 0.94)
HORIZON_WARM     = (0.94, 0.92, 0.82)

SEA_TROUGH       = (0.08, 0.28, 0.55)
SEA_VIRIDIAN     = (0.14, 0.55, 0.46)
SEA_MID          = (0.20, 0.44, 0.70)
SEA_FAR          = (0.68, 0.78, 0.88)
WAVE_CREST       = (0.86, 0.82, 0.38)
WAVE_HIGHLIGHT   = (0.96, 0.96, 0.88)

SAIL_WHITE       = (0.94, 0.93, 0.88)
SAIL_SHADOW      = (0.62, 0.68, 0.82)
JIB_RED          = (0.82, 0.22, 0.14)
JIB_RED_SHADOW   = (0.55, 0.12, 0.08)
JIB_ORANGE       = (0.88, 0.56, 0.18)
JIB_BLUE         = (0.18, 0.42, 0.72)
HULL_OAK         = (0.68, 0.52, 0.28)
HULL_SHADOW      = (0.32, 0.24, 0.12)
HULL_GREEN       = (0.22, 0.48, 0.30)
HULL_WHITE       = (0.88, 0.86, 0.82)
FIGURE_DARK      = (0.14, 0.12, 0.10)
WATER_LINE       = (0.06, 0.18, 0.38)
BREAKWATER_OCHRE = (0.72, 0.66, 0.52)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(a[i] * (1.0 - t) + b[i] * t for i in range(3))


def lerp3(a, b, c, t):
    """Three-point lerp: a at t=0, b at t=0.5, c at t=1."""
    if t < 0.5:
        return lerp(a, b, t * 2.0)
    return lerp(b, c, (t - 0.5) * 2.0)


def noise2(x, y, seed=0):
    """Cheap pseudorandom noise in [-1, 1]."""
    n = int(x * 1013 + y * 7193 + seed * 3917)
    n = (n >> 13) ^ n
    n = (n * (n * n * 15731 + 789221) + 1376312589) & 0x7FFFFFFF
    return (n / 1073741824.0) - 1.0


def build_reference(w: int, h: int) -> Image.Image:
    """Build procedural reference: Belgian sea regatta scene."""
    arr = np.zeros((h, w, 3), dtype=np.float32)
    horizon_y = int(h * 0.42)  # horizon line at 42% down

    # ── Sky gradient ──────────────────────────────────────────────────────────
    for row in range(horizon_y + 1):
        fy = row / max(1, horizon_y)    # 0 = top, 1 = horizon
        for col in range(w):
            sky = lerp3(SKY_COBALT, SKY_CERULEAN, SKY_HAZE, fy)
            # Slight warm right
            fx = col / w
            sky = lerp(sky, HORIZON_WARM, fy * 0.30 * fx * 0.5)
            arr[row, col, :] = sky

    # ── Sea surface ───────────────────────────────────────────────────────────
    for row in range(horizon_y, h):
        fy = (row - horizon_y) / max(1, h - horizon_y)  # 0 = horizon, 1 = bottom
        for col in range(w):
            fx = col / w
            # Base sea colour: cobalt near horizon, viridian in foreground
            sea_base = lerp3(SEA_FAR, SEA_MID, SEA_VIRIDIAN, fy)
            # Wave variation using noise
            wave_n = noise2(col * 0.05, row * 0.12, seed=1)
            wave_amp = fy * 0.18   # more wave variation in foreground
            if wave_n > 0.5:
                colour = lerp(sea_base, WAVE_CREST, (wave_n - 0.5) * wave_amp * 3)
            elif wave_n > 0.0:
                colour = lerp(sea_base, WAVE_HIGHLIGHT, wave_n * wave_amp * 1.5)
            elif wave_n < -0.6:
                colour = lerp(sea_base, SEA_TROUGH, (-wave_n - 0.6) * wave_amp * 4)
            else:
                colour = sea_base
            arr[row, col, :] = colour

    # ── Horizon breakwater strip ──────────────────────────────────────────────
    bw_y0 = horizon_y - 2
    bw_y1 = horizon_y + 4
    bw_x0 = int(w * 0.55)
    bw_x1 = int(w * 0.82)
    for row in range(max(0, bw_y0), min(h, bw_y1)):
        for col in range(bw_x0, bw_x1):
            fade = 1.0 - abs(col - (bw_x0 + bw_x1) / 2) / ((bw_x1 - bw_x0) / 2)
            arr[row, col, :] = lerp(arr[row, col, :].tolist(), BREAKWATER_OCHRE, fade * 0.55)

    # ── Helper: draw a sail triangle ─────────────────────────────────────────
    def draw_sail(arr, pts, col_luff, col_leech):
        """Fill a triangle defined by 3 (x, y) points with a gradient."""
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        y0, y1 = max(0, int(min(ys))), min(h, int(max(ys)) + 2)
        x0, x1 = max(0, int(min(xs))), min(w, int(max(xs)) + 2)

        # Simple scan-line fill using barycentric test
        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        p0, p1, p2 = pts
        area = cross(p0, p1, p2)
        if abs(area) < 1:
            return

        for row in range(y0, y1):
            for col in range(x0, x1):
                w0 = cross(p1, p2, (col, row))
                w1 = cross(p2, p0, (col, row))
                w2 = cross(p0, p1, (col, row))
                if (area > 0 and w0 >= 0 and w1 >= 0 and w2 >= 0) or \
                   (area < 0 and w0 <= 0 and w1 <= 0 and w2 <= 0):
                    # Interpolate by horizontal position within sail
                    tx = (col - x0) / max(1, x1 - x0)
                    arr[row, col, :] = lerp(col_luff, col_leech, tx)

    def draw_hull(arr, cx, waterline_y, hull_w, hull_h, heel_px, col_above, col_below):
        """Draw a heeled dinghy hull as a parallelogram."""
        # Hull is a trapezoid: wide at waterline, narrower at bow
        for row in range(max(0, waterline_y - hull_h), min(h, waterline_y + 3)):
            fy = (row - (waterline_y - hull_h)) / max(1, hull_h)
            # Heel shifts the hull laterally
            x_offset = int(heel_px * (1.0 - fy))
            hw = int(hull_w * (0.5 + 0.5 * (1.0 - fy * 0.3)))
            left  = max(0, cx + x_offset - hw)
            right = min(w, cx + x_offset + hw)
            for col in range(left, right):
                if row > waterline_y - 3:
                    arr[row, col, :] = col_below
                else:
                    fx = (col - left) / max(1, right - left)
                    arr[row, col, :] = lerp(col_above, HULL_SHADOW, fx * 0.5)

    def draw_figure(arr, cx, cy, size, col):
        """Draw a simple silhouette figure (hiking out)."""
        # Body
        body_h = int(size * 0.6)
        body_w = max(2, int(size * 0.18))
        for row in range(max(0, cy - body_h), min(h, cy)):
            for col in range(max(0, cx - body_w), min(w, cx + body_w)):
                arr[row, col, :] = col
        # Arm extended outward (hiking out)
        arm_len = int(size * 0.5)
        arm_y   = cy - int(body_h * 0.6)
        for dx in range(arm_len):
            row = arm_y + int(dx * 0.2)
            col = cx + dx
            if 0 <= row < h and 0 <= col < w:
                arr[row, col, :] = col

    # ── Boat 1 (foreground, nearest, lower-left) ──────────────────────────────
    b1_cx       = int(w * 0.24)
    b1_waterline = int(h * 0.58)
    # Hull
    draw_hull(arr, b1_cx, b1_waterline, int(w * 0.055), int(h * 0.06), -int(w*0.012),
              HULL_OAK, WATER_LINE)
    # Mainsail (white, large)
    ms_foot_l = (int(w * 0.17), b1_waterline - int(h * 0.04))
    ms_foot_r = (int(w * 0.30), b1_waterline - int(h * 0.02))
    ms_head   = (int(w * 0.22), b1_waterline - int(h * 0.30))
    draw_sail(arr, [ms_foot_l, ms_foot_r, ms_head], SAIL_WHITE, SAIL_SHADOW)
    # Red jib
    jib_tack  = (int(w * 0.18), b1_waterline - int(h * 0.04))
    jib_clew  = (int(w * 0.11), b1_waterline - int(h * 0.01))
    jib_head  = (int(w * 0.16), b1_waterline - int(h * 0.20))
    draw_sail(arr, [jib_tack, jib_clew, jib_head], JIB_RED, JIB_RED_SHADOW)
    # Crew figure hiking out
    draw_figure(arr, int(w * 0.29), b1_waterline - int(h * 0.04),
                int(h * 0.09), FIGURE_DARK)

    # ── Boat 2 (slightly behind, center-left) ────────────────────────────────
    b2_cx        = int(w * 0.44)
    b2_waterline = int(h * 0.54)
    b2_scale     = 0.70
    draw_hull(arr, b2_cx, b2_waterline, int(w * 0.038 * b2_scale),
              int(h * 0.042 * b2_scale), -int(w * 0.008),
              HULL_WHITE, WATER_LINE)
    ms2_foot_l = (int(w * 0.40), b2_waterline - int(h * 0.03 * b2_scale))
    ms2_foot_r = (int(w * 0.47), b2_waterline - int(h * 0.015 * b2_scale))
    ms2_head   = (int(w * 0.43), b2_waterline - int(h * 0.22 * b2_scale))
    draw_sail(arr, [ms2_foot_l, ms2_foot_r, ms2_head], SAIL_WHITE, SAIL_SHADOW)
    jib2_tack  = (int(w * 0.42), b2_waterline - int(h * 0.03 * b2_scale))
    jib2_clew  = (int(w * 0.37), b2_waterline - int(h * 0.005 * b2_scale))
    jib2_head  = (int(w * 0.41), b2_waterline - int(h * 0.14 * b2_scale))
    draw_sail(arr, [jib2_tack, jib2_clew, jib2_head], JIB_ORANGE, SAIL_SHADOW)

    # ── Boat 3 (center) ───────────────────────────────────────────────────────
    b3_cx        = int(w * 0.56)
    b3_waterline = int(h * 0.51)
    b3_scale     = 0.52
    draw_hull(arr, b3_cx, b3_waterline, int(w * 0.030 * b3_scale),
              int(h * 0.034 * b3_scale), -int(w * 0.006),
              HULL_GREEN, WATER_LINE)
    ms3_foot_l = (int(w * 0.53), b3_waterline - int(h * 0.022 * b3_scale))
    ms3_foot_r = (int(w * 0.58), b3_waterline - int(h * 0.010 * b3_scale))
    ms3_head   = (int(w * 0.555), b3_waterline - int(h * 0.19 * b3_scale))
    draw_sail(arr, [ms3_foot_l, ms3_foot_r, ms3_head], SAIL_WHITE, SAIL_SHADOW)
    jib3_tack  = (int(w * 0.54), b3_waterline - int(h * 0.020 * b3_scale))
    jib3_clew  = (int(w * 0.50), b3_waterline)
    jib3_head  = (int(w * 0.535), b3_waterline - int(h * 0.11 * b3_scale))
    draw_sail(arr, [jib3_tack, jib3_clew, jib3_head], JIB_BLUE, SAIL_SHADOW)

    # ── Boats 4, 5 (upper middle, smaller) ────────────────────────────────────
    for (bcx, bwy, bscale, jcol) in [
        (int(w * 0.64), int(h * 0.485), 0.38, SAIL_WHITE),
        (int(w * 0.72), int(h * 0.470), 0.28, JIB_RED),
    ]:
        draw_hull(arr, bcx, bwy, int(w * 0.025 * bscale),
                  int(h * 0.028 * bscale), 0,
                  HULL_OAK, WATER_LINE)
        ms_fl = (bcx - int(w * 0.022 * bscale), bwy - int(h * 0.015 * bscale))
        ms_fr = (bcx + int(w * 0.022 * bscale), bwy)
        ms_hd = (bcx - int(w * 0.005 * bscale), bwy - int(h * 0.16 * bscale))
        draw_sail(arr, [ms_fl, ms_fr, ms_hd], SAIL_WHITE, SAIL_SHADOW)

    # ── Boats 6, 7 (near horizon, almost dissolved) ───────────────────────────
    for (bcx, bwy, bscale) in [
        (int(w * 0.80), int(h * 0.455), 0.18),
        (int(w * 0.87), int(h * 0.447), 0.13),
    ]:
        ms_fl = (bcx - int(w * 0.014 * bscale), bwy - int(h * 0.010 * bscale))
        ms_fr = (bcx + int(w * 0.014 * bscale), bwy)
        ms_hd = (bcx, bwy - int(h * 0.13 * bscale))
        draw_sail(arr, [ms_fl, ms_fr, ms_hd],
                  lerp(SAIL_WHITE, SKY_HAZE, 0.45),
                  lerp(SAIL_SHADOW, SKY_HAZE, 0.55))

    arr_uint8 = np.clip(arr * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(arr_uint8, "RGB")


def main():
    print("Session 259 -- Regatta at Nieuwpoort, Flood Tide (after Théo van Rysselberghe)")
    print(f"Canvas: {W}x{H}")
    print()

    ref = build_reference(W, H)
    print("Reference built.")

    p = Painter(W, H)

    # Ground: warm white canvas -- van Rysselberghe's stretched linen
    print("Toning ground...")
    p.tone_ground((0.95, 0.93, 0.85), texture_strength=0.018)

    # Block in: sky, sea, major boat masses
    print("Blocking in masses...")
    p.block_in(ref, stroke_size=28, n_strokes=180)

    # Build form: sail gradients, wave structure, hull modelling
    print("Building form...")
    p.build_form(ref, stroke_size=11, n_strokes=140)

    # Place lights: sail highlights, wave crest flashes, water sparkle
    print("Placing lights...")
    p.place_lights(ref, stroke_size=4, n_strokes=90)

    # ── Rysselberghe Chromatic Dot Field pass (170th mode) ────────────────────
    print("Applying Rysselberghe Chromatic Dot Field pass...")
    p.rysselberghe_chromatic_dot_field_pass(
        spectral_boost=0.38,        # push hues toward spectral primaries
        luminosity_gain=0.16,       # optical mixing luminosity gain
        luminosity_threshold=0.38,  # only boost chromatically rich pixels
        dot_spacing=7,              # fine dot grid -- Rysselberghe's small marks
        dot_jitter=0.28,            # slight irregularity for hand-applied quality
        dot_sigma=1.6,              # soft Gaussian dot profile
        dot_amplitude=0.045,        # subtle luminance micro-modulation
        opacity=0.74,
    )

    # ── Atmospheric Recession pass (improvement) ─────────────────────────────
    print("Applying Atmospheric Recession pass...")
    p.paint_atmospheric_recession_pass(
        recession_direction="top",   # top = far (horizon); bottom = near (foreground)
        haze_lift=0.07,              # gentle horizon brightening
        desaturation=0.25,           # moderate saturation loss toward horizon
        cool_shift_r=0.03,           # subtle warm reduction at distance
        cool_shift_g=0.01,
        cool_shift_b=0.06,           # blue increase at horizon
        near_fraction=0.05,
        far_fraction=0.80,
        opacity=0.62,
    )

    # ── Granulation pass (s258) ───────────────────────────────────────────────
    print("Applying Granulation pass...")
    p.paint_granulation_pass(
        granule_sigma=2.2,           # medium canvas tooth
        granule_scale=0.10,
        warm_shift=0.028,
        cool_shift=0.028,
        edge_sharpen=0.30,           # crisp sail/water edges
        opacity=0.62,
    )

    # ── Edge Temperature pass (s256) ─────────────────────────────────────────
    print("Applying Edge Temperature pass...")
    p.paint_edge_temperature_pass(
        warm_hue_center=0.10,        # yellow/amber sail edges
        warm_hue_width=0.22,
        cool_hue_center=0.62,        # cobalt/blue water edges
        cool_hue_width=0.20,
        gradient_zone_px=2.5,
        contrast_strength=0.10,      # moderate -- crisp sea/sail contrast
        opacity=0.55,
    )

    # ── Shadow Bleed pass (s257) ──────────────────────────────────────────────
    print("Applying Shadow Bleed pass...")
    p.paint_shadow_bleed_pass(
        shadow_threshold=0.35,       # deep sea troughs
        bright_threshold=0.75,       # sails and wave crests
        bleed_sigma=8.0,             # moderate bleed -- sea reflections
        reflect_strength=0.10,
        warm_r=0.88,
        warm_g=0.80,
        warm_b=0.48,
        opacity=0.48,
    )

    # Save
    print(f"Saving to {OUTPUT_PATH}...")
    p.save(OUTPUT_PATH)
    print("Done.")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
