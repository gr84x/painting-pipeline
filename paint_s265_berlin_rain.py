"""
paint_s265_berlin_rain.py -- Session 265

"Berliner Strassenszene im Regen" -- in the manner of Lesser Ury

Image Description
-----------------
Subject & Composition
    A solitary woman stands at the threshold of a Berlin cafe awning on a wet
    November evening, 1900. She occupies the lower-left third of the canvas,
    silhouetted in three-quarter profile against the warm amber glow of the
    cafe's street-level windows. The viewpoint is at street level, slightly
    below the figure's eye-line, as if the painter stands a few paces away on
    the opposite pavement. A wrought-iron gas lamp post rises vertically in the
    left quarter of the canvas, its globe casting the nearest amber halo. The
    upper 40% of the canvas is the deep prussian-blue night sky and dark
    building silhouettes. The lower 35% is wet cobblestone pavement, the
    stones' dark surfaces reading as a fractured mirror.

The Figure
    A young woman, perhaps 26, in a dark charcoal-green evening coat that
    reaches her ankles. A small dark hat. Her face is turned three-quarters
    away from the viewer -- we see the line of her jaw, the pale column of
    her neck, the suggestion of her profile. Her right hand, gloved, is raised
    slightly at her side -- not hailing, not gesturing, simply present. Her
    posture is upright, undefeated by the rain and cold. Her emotional state:
    a specific urban solitude -- the state of being alone in public, surrounded
    by warmth you are not quite inside. She does not want rescue. She is simply
    here, at the edge of the light, waiting for something unnamed. Her silhouette
    is the darkest element in the composition; the cafe light behind her creates
    a faint warm rim along her left shoulder and hat brim.

The Environment
    A Berlin street in the Mitte district, a rainy November night. Behind the
    figure: two tall rectangular cafe windows, each about 100px wide x 180px tall
    at canvas scale, their amber interiors visible through the glass as warm
    diffuse glow rather than readable detail. The facade between and above the
    windows is prussian dark stone. A horizontal cafe awning runs just above the
    windows. To the left of the figure, the gas lamp post: a slim dark vertical
    line from the lower edge of the canvas to about one-third canvas height,
    topped by the amber globe and its halo of warm dispersed light. The right
    half of the canvas above the pavement zone is deeper in shadow -- the street
    curves away into the prussian night, a second lamp barely visible at
    mid-distance (smaller, cooler, suggesting recession). The foreground
    cobblestones: each stone slightly different in its degree of wet-sheen.
    The amber lamp reflection in the pavement directly below the lamp post:
    a bright oval of warm reflected light that breaks and elongates downward.
    The cafe window reflections in the pavement: two dim amber rectangles,
    distorted and elongated horizontally by the water film.

Technique & Palette
    Lesser Ury Nocturne mode -- session 265, 176th distinct painting mode.

    Stage 1 WET PAVEMENT VERTICAL MIRROR REFLECTION (sky_fraction=0.42,
    pavement_fraction=0.38, h_blur_sigma=20.0, v_blur_sigma=4.0,
    reflection_attenuation=0.35, reflection_opacity=0.65):
    The upper 42% of the painted canvas -- sky, building tops, gas lamp globe,
    cafe window upper halves -- is flipped vertically and composited into the
    lower 38% (pavement zone) as a heavily horizontally blurred mirror image.
    The horizontal blur (sigma=20) elongates the warm lamp glow and window
    rectangles into the characteristic Ury pavement-mirror streaks. Attenuated
    to 35% of source luminance (the cobblestones absorb 65% of incident light).

    Stage 2 GAS-LAMP AMBER CORONA (lamp_threshold=0.60, corona_sigma=24.0,
    corona_strength=0.20, amber_dr=0.16, amber_dg=0.05, amber_db_cut=0.14):
    Pixels above luminance 0.60 (the lamp globe, window highlight zones) are
    shifted toward warm amber, and the warm excess is diffused by a sigma=24
    Gaussian to create the characteristic Ury corona: a soft spreading halo
    of amber light that penetrates the prussian blue haze for 80-120px around
    each light source.

    Stage 3 PRUSSIAN BLUE NIGHT-SHADOW COOLER (shadow_threshold=0.30,
    shadow_r_scale=0.72, shadow_g_scale=0.80, shadow_b_lift=0.025,
    shadow_strength=0.72):
    All pixels below luminance 0.30 are cooled toward prussian blue: R scaled
    to 72%, G to 80%, B lifted slightly. This shifts the shadow mass of the
    figure silhouette, the dark building facades, the shadow-side cobblestones,
    and the receding street into the characteristic Ury prussian blue-indigo
    that makes the amber light sources appear warmer by contrast.

    Wet Surface Gleam improvement (s265): spec_threshold=0.68,
    streak_sigma=22.0, gleam_r=0.30, gleam_g=0.22, gleam_b=0.12,
    opacity=0.52. Applied before the Ury pass to create warm vertical gleam
    trails from the lamp globe and cafe window highlights -- the physical
    specular reflection elongated downward on the wet pavement surface.

    Stage-by-stage pipeline:
    Ground: prussian-tinted dark (0.05, 0.06, 0.16) toned linen
    Underpainting: structural geometry, lamp post, figure silhouette
    Block-in (broad): sky dark, cafe front, figure mass, pavement dark
    Block-in (medium): lamp glow zone, window amber, figure coat detail
    Build form (medium): figure modelling, facade stone, lamp post shadow
    Build form (fine): cobblestone texture, figure rim light, window glass
    Place lights: lamp globe, window amber, pavement reflection core
    Wet Surface Gleam (s265): vertical warm gleam trails from bright sources
    Ury Nocturne Reflection (s265 176th mode): pavement mirror, corona, shadows
    Atmospheric Recession (s259): depth recession toward background street
    Shadow Bleed (s257): warm reflected cafe light bleeding onto near figure

    Full palette:
    prussian-night (0.05/0.06/0.18) -- indigo-black (0.04/0.04/0.12) --
    amber-lamp (0.78/0.52/0.18) -- cafe-warm (0.82/0.60/0.30) --
    pavement-reflection (0.42/0.30/0.12) -- wet-stone (0.14/0.14/0.22) --
    lamp-specular (0.92/0.82/0.68) -- figure-dark (0.12/0.14/0.16) --
    figure-rim (0.46/0.38/0.24) -- sky-violet (0.08/0.08/0.20) --
    building-dark (0.10/0.10/0.16) -- awning-shadow (0.16/0.14/0.18)

Mood & Intent
    The painting carries the particular quality Ury found in the new Berlin: the
    modern city as a space of beautiful, chosen aloneness. The woman is not lost
    or abandoned -- she is simply at the edge of the light, which is where
    interesting things happen. The amber warmth of the cafe is behind her, real
    and present, but she faces the prussian dark of the street. The wet pavement
    mirrors everything above it, making the street both more complex and more
    melancholy -- every lamp doubled, every figure duplicated in distortion
    below their feet. The viewer is intended to feel the specific quality of
    November rain in a city at night: not cold despair but a kind of alert
    solitude, the city's beauty visible precisely because the weather has
    emptied the street of the comfortable and the incurious.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "s265_berlin_rain.png")

W, H = 1040, 1440   # portrait — urban nocturne, vertical composition


# ── Palette ────────────────────────────────────────────────────────────────────

PRUSSIAN_NIGHT    = (0.05, 0.06, 0.18)
INDIGO_BLACK      = (0.04, 0.04, 0.12)
AMBER_LAMP        = (0.78, 0.52, 0.18)
CAFE_WARM         = (0.82, 0.60, 0.30)
PAVEMENT_REFL     = (0.42, 0.30, 0.12)
WET_STONE         = (0.14, 0.14, 0.22)
LAMP_SPECULAR     = (0.92, 0.82, 0.68)
FIGURE_DARK       = (0.12, 0.14, 0.16)
FIGURE_RIM        = (0.46, 0.38, 0.24)
SKY_VIOLET        = (0.08, 0.08, 0.20)
BUILDING_DARK     = (0.10, 0.10, 0.16)
AWNING_SHADOW     = (0.16, 0.14, 0.18)
WINDOW_AMBER_CORE = (0.88, 0.68, 0.30)
PAVEMENT_BASE     = (0.11, 0.11, 0.18)


def lerp(a, b, t):
    t = max(0.0, min(1.0, float(t)))
    return tuple(float(a[i]) * (1.0 - t) + float(b[i]) * t for i in range(3))


def smooth(t):
    t = max(0.0, min(1.0, float(t)))
    return t * t * (3.0 - 2.0 * t)


def build_reference(w: int, h: int) -> np.ndarray:
    """Build procedural reference for 'Berliner Strassenszene im Regen'.

    Returns float32 RGB array, shape (H, W, 3), values in [0, 1].

    Composition zones (as fraction of H):
      0.00-0.38  Sky and upper building silhouettes (prussian dark)
      0.38-0.65  Street-level zone: cafe front, figure, lamp (main action)
      0.65-1.00  Wet cobblestone pavement (dark with reflections)
    """
    rng = np.random.RandomState(265)
    ref = np.zeros((h, w, 3), dtype=np.float32)

    xs = np.arange(w, dtype=np.float32) / max(w - 1, 1)
    ys = np.arange(h, dtype=np.float32) / max(h - 1, 1)

    # Zone boundaries (in pixels)
    sky_bot     = int(h * 0.38)    # sky/building top zone ends
    street_bot  = int(h * 0.65)    # street-level zone ends
    pave_top    = street_bot        # pavement starts here
    pave_bot    = h

    # ── Zone 1: Sky and building silhouettes ─────────────────────────────────
    for row in range(sky_bot):
        fy = row / max(sky_bot - 1, 1)
        # Deep prussian blue at top, slightly warmer/lighter toward street level
        col = lerp(INDIGO_BLACK, PRUSSIAN_NIGHT, smooth(fy * 0.6))
        # Add very slight violet tint to upper sky
        col = lerp(col, SKY_VIOLET, smooth(fy * 0.3) * 0.4)
        # Add subtle horizontal variation for building silhouette texture
        noise = rng.uniform(-0.01, 0.01, w).astype(np.float32)
        ref[row, :, 0] = np.clip(col[0] + noise * 0.5, 0.0, 1.0)
        ref[row, :, 1] = np.clip(col[1] + noise * 0.4, 0.0, 1.0)
        ref[row, :, 2] = np.clip(col[2] + noise * 0.6, 0.0, 1.0)

    # Building silhouette mass: darker block in upper-right (building facade)
    # The right 60% of the upper zone has building mass
    bld_left = int(w * 0.30)
    for row in range(sky_bot):
        fy = row / max(sky_bot - 1, 1)
        for col in range(bld_left, w):
            # Building is darker than the sky
            bld_tone = lerp(BUILDING_DARK, INDIGO_BLACK, smooth(1.0 - fy))
            ref[row, col, 0] = bld_tone[0] + rng.uniform(-0.008, 0.008)
            ref[row, col, 1] = bld_tone[1] + rng.uniform(-0.006, 0.006)
            ref[row, col, 2] = bld_tone[2] + rng.uniform(-0.010, 0.010)
    ref[:sky_bot, bld_left:, :] = np.clip(ref[:sky_bot, bld_left:, :], 0.0, 1.0)

    # ── Zone 2: Street-level zone ────────────────────────────────────────────
    for row in range(sky_bot, street_bot):
        fy = (row - sky_bot) / max(street_bot - sky_bot - 1, 1)
        base = lerp(BUILDING_DARK, WET_STONE, smooth(fy * 0.5))
        ref[row, :, 0] = np.clip(base[0] + rng.uniform(-0.01, 0.01, w), 0.0, 1.0)
        ref[row, :, 1] = np.clip(base[1] + rng.uniform(-0.008, 0.008, w), 0.0, 1.0)
        ref[row, :, 2] = np.clip(base[2] + rng.uniform(-0.012, 0.012, w), 0.0, 1.0)

    # ── Cafe windows: two amber rectangles in the right 55% ──────────────────
    # Window 1 (left of two)
    win1_left  = int(w * 0.48)
    win1_right = int(w * 0.63)
    win1_top   = int(h * 0.40)
    win1_bot   = int(h * 0.60)

    # Window 2 (right of two)
    win2_left  = int(w * 0.68)
    win2_right = int(w * 0.84)
    win2_top   = int(h * 0.40)
    win2_bot   = int(h * 0.60)

    for wr, wl, wt, wb in [(win1_right, win1_left, win1_top, win1_bot),
                             (win2_right, win2_left, win2_top, win2_bot)]:
        for row in range(wt, wb):
            fy = (row - wt) / max(wb - wt - 1, 1)
            # Warmer/brighter in the middle, slightly dimmer at edges
            brightness = 0.85 + 0.10 * np.sin(fy * np.pi)
            for col in range(wl, wr):
                fx = (col - wl) / max(wr - wl - 1, 1)
                b2 = brightness * (0.85 + 0.12 * np.sin(fx * np.pi))
                ref[row, col, 0] = np.clip(WINDOW_AMBER_CORE[0] * b2 + rng.uniform(-0.02, 0.02), 0.0, 1.0)
                ref[row, col, 1] = np.clip(WINDOW_AMBER_CORE[1] * b2 + rng.uniform(-0.02, 0.02), 0.0, 1.0)
                ref[row, col, 2] = np.clip(WINDOW_AMBER_CORE[2] * b2 + rng.uniform(-0.02, 0.02), 0.0, 1.0)

    # Warm ambient spill around windows (cafe light escaping)
    cafe_spill_cx = int(w * 0.66)
    cafe_spill_cy = int(h * 0.50)
    for row in range(sky_bot, street_bot):
        for col in range(int(w * 0.40), w):
            dx = (col - cafe_spill_cx) / (w * 0.32)
            dy = (row - cafe_spill_cy) / (h * 0.16)
            dist = np.sqrt(dx * dx + dy * dy)
            spill = max(0.0, 1.0 - dist) * 0.08
            ref[row, col, 0] = np.clip(ref[row, col, 0] + spill * 0.90, 0.0, 1.0)
            ref[row, col, 1] = np.clip(ref[row, col, 1] + spill * 0.55, 0.0, 1.0)
            ref[row, col, 2] = np.clip(ref[row, col, 2] + spill * 0.18, 0.0, 1.0)

    # Awning: dark band above windows
    awning_top = int(h * 0.37)
    awning_bot = int(h * 0.42)
    for row in range(awning_top, awning_bot):
        for col in range(int(w * 0.40), w):
            ref[row, col, :] = np.array(AWNING_SHADOW)

    # ── Gas lamp post (left 18% of canvas) ───────────────────────────────────
    lamp_cx      = int(w * 0.16)
    lamp_globe_y = int(h * 0.36)   # lamp globe centre
    lamp_globe_r = int(w * 0.025)  # globe radius

    # Post: narrow dark vertical line
    post_left  = lamp_cx - int(w * 0.008)
    post_right = lamp_cx + int(w * 0.008)
    post_top   = lamp_globe_y + lamp_globe_r
    post_bot   = street_bot
    for row in range(post_top, post_bot):
        for col in range(max(0, post_left), min(w, post_right)):
            ref[row, col, :] = np.array((0.08, 0.08, 0.10))

    # Globe: bright amber circle
    for row in range(max(0, lamp_globe_y - lamp_globe_r - 2),
                     min(h, lamp_globe_y + lamp_globe_r + 2)):
        for col in range(max(0, lamp_cx - lamp_globe_r - 2),
                         min(w, lamp_cx + lamp_globe_r + 2)):
            dx = col - lamp_cx
            dy = row - lamp_globe_y
            dist = np.sqrt(dx * dx + dy * dy)
            if dist < lamp_globe_r:
                t = 1.0 - dist / lamp_globe_r
                globe = lerp(AMBER_LAMP, LAMP_SPECULAR, t)
                ref[row, col, :] = globe
            elif dist < lamp_globe_r + 2:
                ref[row, col, :] = AMBER_LAMP

    # Lamp halo (warm glow spreading into surrounding dark)
    halo_r = int(w * 0.12)
    for row in range(max(0, lamp_globe_y - halo_r), min(h, lamp_globe_y + halo_r)):
        for col in range(max(0, lamp_cx - halo_r), min(w, lamp_cx + halo_r)):
            dx = col - lamp_cx
            dy = row - lamp_globe_y
            dist = np.sqrt(dx * dx + dy * dy)
            if lamp_globe_r < dist < halo_r:
                t = 1.0 - (dist - lamp_globe_r) / (halo_r - lamp_globe_r)
                halo_str = smooth(t) * 0.18
                ref[row, col, 0] = np.clip(ref[row, col, 0] + halo_str * 0.90, 0.0, 1.0)
                ref[row, col, 1] = np.clip(ref[row, col, 1] + halo_str * 0.55, 0.0, 1.0)
                ref[row, col, 2] = np.clip(ref[row, col, 2] + halo_str * 0.12, 0.0, 1.0)

    # Second distant lamp (mid-right, receding)
    lamp2_cx = int(w * 0.75)
    lamp2_cy = int(h * 0.37)
    lamp2_r  = int(w * 0.012)
    for row in range(max(0, lamp2_cy - lamp2_r), min(h, lamp2_cy + lamp2_r)):
        for col in range(max(0, lamp2_cx - lamp2_r), min(w, lamp2_cx + lamp2_r)):
            dx = col - lamp2_cx
            dy = row - lamp2_cy
            if np.sqrt(dx * dx + dy * dy) < lamp2_r:
                ref[row, col, :] = lerp(AMBER_LAMP, (0.60, 0.40, 0.14), 0.5)

    # ── Figure: dark silhouette in lower-left of street zone ─────────────────
    fig_cx   = int(w * 0.32)   # figure center x
    fig_top  = int(h * 0.42)   # top of hat
    fig_bot  = int(h * 0.64)   # feet
    fig_head_r = int(w * 0.032)
    fig_body_w = int(w * 0.065)

    # Head (oval)
    head_cy = fig_top + int(h * 0.04)
    for row in range(max(0, head_cy - fig_head_r),
                     min(h, head_cy + fig_head_r + 4)):
        for col in range(max(0, fig_cx - fig_head_r),
                         min(w, fig_cx + fig_head_r)):
            dx = (col - fig_cx) / max(fig_head_r, 1)
            dy = (row - head_cy) / max(fig_head_r * 1.3, 1)
            if dx * dx + dy * dy < 1.0:
                ref[row, col, :] = FIGURE_DARK

    # Body (tapered rectangle)
    shoulder_y = head_cy + fig_head_r + 2
    for row in range(shoulder_y, fig_bot):
        fy = (row - shoulder_y) / max(fig_bot - shoulder_y - 1, 1)
        half_w = int(fig_body_w * (1.0 - fy * 0.25))   # slight taper
        for col in range(max(0, fig_cx - half_w), min(w, fig_cx + half_w)):
            ref[row, col, :] = FIGURE_DARK

    # Rim light on left shoulder from cafe (warm edge)
    rim_col_start = fig_cx - int(fig_body_w * 0.8)
    rim_col_end   = fig_cx - int(fig_body_w * 0.5)
    for row in range(shoulder_y, shoulder_y + int((fig_bot - shoulder_y) * 0.4)):
        fy = (row - shoulder_y) / max(int((fig_bot - shoulder_y) * 0.4), 1)
        rim_str = smooth(1.0 - fy) * 0.35
        for col in range(max(0, rim_col_start), min(w, rim_col_end)):
            ref[row, col, 0] = np.clip(FIGURE_DARK[0] + rim_str * FIGURE_RIM[0], 0.0, 1.0)
            ref[row, col, 1] = np.clip(FIGURE_DARK[1] + rim_str * FIGURE_RIM[1], 0.0, 1.0)
            ref[row, col, 2] = np.clip(FIGURE_DARK[2] + rim_str * FIGURE_RIM[2], 0.0, 1.0)

    # ── Zone 3: Wet cobblestone pavement ─────────────────────────────────────
    for row in range(pave_top, pave_bot):
        fy = (row - pave_top) / max(pave_bot - pave_top - 1, 1)
        # Darker toward bottom, slight blue cast
        base = lerp(WET_STONE, INDIGO_BLACK, smooth(fy * 0.7))
        noise = rng.normal(0, 0.012, w).astype(np.float32)
        ref[row, :, 0] = np.clip(base[0] + noise * 0.8, 0.0, 1.0)
        ref[row, :, 1] = np.clip(base[1] + noise * 0.7, 0.0, 1.0)
        ref[row, :, 2] = np.clip(base[2] + noise, 0.0, 1.0)

    # Lamp reflection in pavement (below lamp post, bright amber oval)
    refl_cx = lamp_cx
    refl_cy = pave_top + int((pave_bot - pave_top) * 0.15)
    refl_rx = int(w * 0.06)
    refl_ry = int((pave_bot - pave_top) * 0.20)
    for row in range(max(pave_top, refl_cy - refl_ry),
                     min(pave_bot, refl_cy + refl_ry)):
        for col in range(max(0, refl_cx - refl_rx),
                         min(w, refl_cx + refl_rx)):
            dx = (col - refl_cx) / max(refl_rx, 1)
            dy = (row - refl_cy) / max(refl_ry, 1)
            t = max(0.0, 1.0 - np.sqrt(dx * dx + dy * dy))
            if t > 0:
                refl = lerp(WET_STONE, PAVEMENT_REFL, smooth(t) * 0.85)
                ref[row, col, :] = refl

    # Window reflections in pavement (two dim amber rectangles, slightly wider)
    for wl, wr, wt, wb in [
        (int(w * 0.44), int(w * 0.66), pave_top, pave_top + int((pave_bot - pave_top) * 0.35)),
        (int(w * 0.64), int(w * 0.86), pave_top, pave_top + int((pave_bot - pave_top) * 0.35)),
    ]:
        for row in range(max(pave_top, wt), min(pave_bot, wb)):
            fy2 = (row - wt) / max(wb - wt - 1, 1)
            str_ = smooth(1.0 - fy2) * 0.30   # fades toward bottom
            for col in range(max(0, wl), min(w, wr)):
                ref[row, col, 0] = np.clip(ref[row, col, 0] + str_ * 0.45, 0.0, 1.0)
                ref[row, col, 1] = np.clip(ref[row, col, 1] + str_ * 0.28, 0.0, 1.0)
                ref[row, col, 2] = np.clip(ref[row, col, 2] + str_ * 0.06, 0.0, 1.0)

    return np.clip(ref, 0.0, 1.0)


def main():
    print("Session 265 -- Berliner Strassenszene im Regen (after Lesser Ury)")
    print(f"Canvas: {W}x{H}")
    print()

    ref_arr  = build_reference(W, H)
    ref_uint8 = (ref_arr * 255).astype(np.uint8)
    print("Reference built.")

    p = Painter(W, H, seed=265)

    # ── Ground: prussian-tinted dark ─────────────────────────────────────────
    print("Toning ground (prussian dark)...")
    p.tone_ground((0.05, 0.06, 0.16), texture_strength=0.014)

    # ── Underpainting: night sky, lamp geometry, figure silhouette ────────────
    print("Underpainting...")
    p.underpainting(ref_uint8, stroke_size=54, n_strokes=220)
    p.underpainting(ref_uint8, stroke_size=44, n_strokes=240)

    # ── Block-in: dark zones, cafe amber, lamp halo, pavement ─────────────────
    print("Blocking in masses...")
    p.block_in(ref_uint8, stroke_size=34, n_strokes=460)
    p.block_in(ref_uint8, stroke_size=20, n_strokes=500)

    # ── Build form: figure silhouette, window detail, pavement texture ─────────
    print("Building form...")
    p.build_form(ref_uint8, stroke_size=12, n_strokes=520)
    p.build_form(ref_uint8, stroke_size=6,  n_strokes=460)

    # ── Place lights: lamp globe, window cores, reflection accents ────────────
    print("Placing lights...")
    p.place_lights(ref_uint8, stroke_size=5, n_strokes=300)
    p.place_lights(ref_uint8, stroke_size=3, n_strokes=280)

    # ── Wet Surface Gleam (s265 improvement) ─────────────────────────────────
    print("Applying Wet Surface Gleam pass (s265 improvement)...")
    p.paint_wet_surface_gleam_pass(
        spec_threshold=0.68,
        streak_sigma=22.0,
        gleam_r=0.30,
        gleam_g=0.22,
        gleam_b=0.12,
        feather_sigma=2.0,
        noise_seed=265,
        opacity=0.52,
    )

    # ── Ury Nocturne Reflection (176th mode) ──────────────────────────────────
    print("Applying Ury Nocturne Reflection pass (176th mode)...")
    p.ury_nocturne_reflection_pass(
        sky_fraction=0.42,
        pavement_fraction=0.38,
        h_blur_sigma=20.0,
        v_blur_sigma=4.0,
        reflection_attenuation=0.35,
        reflection_opacity=0.65,
        lamp_threshold=0.60,
        corona_sigma=24.0,
        corona_strength=0.20,
        amber_dr=0.16,
        amber_dg=0.05,
        amber_db_cut=0.14,
        shadow_threshold=0.30,
        shadow_r_scale=0.72,
        shadow_g_scale=0.80,
        shadow_b_lift=0.025,
        shadow_strength=0.72,
        noise_seed=265,
        opacity=0.82,
    )

    # ── Atmospheric Recession (s259) ──────────────────────────────────────────
    print("Applying Atmospheric Recession pass...")
    p.paint_atmospheric_recession_pass(
        recession_direction="top",
        haze_lift=0.06,
        desaturation=0.22,
        cool_shift_r=0.03,
        cool_shift_g=0.01,
        cool_shift_b=0.10,
        near_fraction=0.25,
        far_fraction=0.80,
        opacity=0.40,
    )

    # ── Shadow Bleed (s257) ───────────────────────────────────────────────────
    print("Applying Shadow Bleed pass...")
    p.paint_shadow_bleed_pass(
        shadow_threshold=0.25,
        bright_threshold=0.55,
        bleed_sigma=10.0,
        reflect_strength=0.08,
        warm_r=0.78,
        warm_g=0.52,
        warm_b=0.18,
        opacity=0.30,
    )

    # ── Granulation (s258) ────────────────────────────────────────────────────
    print("Applying Granulation pass...")
    p.paint_granulation_pass(
        granule_sigma=1.4,
        granule_scale=0.032,
        warm_shift=0.02,
        cool_shift=0.02,
        edge_sharpen=0.20,
        noise_seed=265,
        opacity=0.40,
    )

    # ── Save ──────────────────────────────────────────────────────────────────
    print(f"Saving to {OUTPUT_PATH}...")
    p.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
