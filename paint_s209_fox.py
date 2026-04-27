"""
paint_s209_fox.py — Original composition: "Pause at the Birch Line"

Session 209 painting — inspired by Josef Albers (1888–1976).

IMAGE DESCRIPTION
=================
Subject & Composition:
  A lone red fox, viewed from eye level slightly below (a 15° upward angle),
  standing at the exact boundary between open snow-covered meadow and the edge of
  a bare birch woodland.  The fox faces three-quarters left, paused mid-step —
  right forepaw lifted — as if caught by a sound just beyond the frame.  Viewed
  from the right and slightly behind, giving a diagonal compositional line from
  lower-right foreground toward upper-left forest interior.

The Figure:
  The fox occupies the lower-centre of the frame, roughly 40% of canvas height.
  Its coat is a rich burnt-sienna / cadmium-orange — brilliant against cold blue-
  white snow.  The throat and belly are cream-white, shaded pale grey beneath.
  Dark stockings below the knee.  The tail curves down and right, tipped white.
  One amber eye visible — iris catching cold winter light, dark elliptical pupil.
  Ears pricked forward, listening.  The lifted forepaw shows dark pads and curved
  black claws.  Emotional state: alert, suspended — the precise instant between
  flight and curiosity, the body still vibrating with decision.

The Environment:
  Left and background: a row of white-barked birch trees, marked with dark
  horizontal striations, receding into cool pale grey-blue winter fog.  The snow
  on the ground is blue-white in shadow, warmer cream where afternoon sun falls
  diagonally from upper-right.  Snow surface has subtle wind-scalloped crust
  texture.  Right foreground: a few dried seed-heads and thin bramble stems
  protrude from the snow, dark and brittle.  Upper half: the dim blue-grey
  interior of the birch wood — pale light filters through bare branches, no
  leaves, no warmth.  Air is cold and absolutely clear.  A mood of deep winter
  stillness and the electric awareness that comes from encountering a wild creature.

Technique & Palette:
  Josef Albers' 'Homage to the Square' chromatic interaction principle.
  The albers_homage_square_pass divides the canvas into concentric Chebyshev
  rectangular zones.  The fox — warm cadmium orange at compositional centre —
  pushes surrounding zones toward cool blue; the cool birch-snow surround
  exaggerates the fox's warmth at the zone boundaries.  Colour is structure.
  Flat zones, precise edges, no atmospheric blending — the temperature boundary
  between creature and world is the painting's subject.

  Palette:
    Cadmium orange (fox coat lit):    (0.88, 0.50, 0.12)
    Burnt sienna (fox body shadow):   (0.68, 0.28, 0.08)
    Cream-white (snow lit):           (0.94, 0.93, 0.88)
    Blue-white (snow in shadow):      (0.78, 0.84, 0.92)
    Cool grey (birch fog):            (0.60, 0.62, 0.68)
    Warm amber (winter sunlight):     (0.90, 0.76, 0.42)
    Dark bark grey:                   (0.22, 0.22, 0.25)

Mood & Intent:
  The painting captures the exact quality of encountering a wild creature in
  deep winter — mutual recognition held in suspension.  The Albers chromatic
  zone interaction amplifies the perceptual contrast: warm living creature
  inside cold dead stillness.  Warm light barely surviving against cold
  advance.  The viewer should feel the cold air, the silence, and the electric
  aliveness of the fox's awareness — the sense that something sees back.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter
from art_catalog import get_style

W, H = 540, 780


def build_fox_reference(w: int, h: int) -> Image.Image:
    """
    Synthetic reference for fox-at-birch-line composition.
    Fox at centre-lower, birch forest background, diagonal winter sunlight.
    """
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None] * np.ones((1, w), dtype=np.float32)
    xx = np.ones((h, 1), dtype=np.float32) * np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]

    def _blend(base, colour, alpha):
        a = np.clip(alpha[:, :, None], 0.0, 1.0)
        return base * (1.0 - a) + colour[None, None, :] * a

    # ── Background: birch woodland interior ──────────────────────────────────
    sky_top  = np.array([0.50, 0.54, 0.62], dtype=np.float32)   # cool blue-grey fog
    sky_bot  = np.array([0.70, 0.72, 0.76], dtype=np.float32)   # lighter near horizon
    arr = (sky_top[None, None, :] * (1.0 - yy[:, :, None]) +
           sky_bot[None, None, :] * yy[:, :, None])

    # Diagonal winter sunlight wash — from upper-right
    sun_x = 1.10
    sun_y = -0.10
    sun_dist = np.sqrt((xx - sun_x) ** 2 + (yy - sun_y) ** 2)
    sun_a = np.clip(0.55 - sun_dist * 0.40, 0.0, 0.38)
    arr = _blend(arr, np.array([0.92, 0.82, 0.60], dtype=np.float32), sun_a)

    # ── Birch trunks — vertical white columns with dark striations ────────────
    trunk_xs = [0.04, 0.14, 0.24, 0.38, 0.52, 0.68, 0.82, 0.94]
    trunk_widths = [0.016, 0.022, 0.018, 0.014, 0.019, 0.016, 0.021, 0.013]
    trunk_top_ys = [0.0, 0.0, 0.02, 0.0, 0.0, 0.01, 0.0, 0.03]
    trunk_bot_ys = [0.75, 0.78, 0.80, 0.72, 0.74, 0.76, 0.77, 0.70]
    for tx, tw, ty_top, ty_bot in zip(trunk_xs, trunk_widths, trunk_top_ys, trunk_bot_ys):
        in_trunk_y = ((yy >= ty_top) & (yy <= ty_bot)).astype(np.float32)
        trunk_d = np.abs(xx - tx) / tw
        trunk_a = np.clip(1.0 - trunk_d, 0.0, 1.0) ** 0.8 * in_trunk_y
        # Birch bark — near white with slight warmth
        arr = _blend(arr, np.array([0.88, 0.87, 0.84], dtype=np.float32), trunk_a * 0.82)
        # Dark horizontal striations on each trunk
        for stria_y_frac in [0.18, 0.32, 0.45, 0.58, 0.68]:
            stria_y = ty_top + (ty_bot - ty_top) * stria_y_frac
            stria_d = np.abs(yy - stria_y) / 0.006
            stria_a = np.clip(1.0 - stria_d, 0.0, 1.0) * trunk_a * 0.72
            arr = _blend(arr, np.array([0.18, 0.18, 0.20], dtype=np.float32), stria_a)

    # ── Snow ground — occupies lower ~38% of canvas ──────────────────────────
    snow_horizon = 0.61
    snow_a = np.clip((yy - snow_horizon) / 0.06, 0.0, 1.0)
    # Snow base: cool blue-white in shadow
    snow_base = np.array([0.86, 0.89, 0.94], dtype=np.float32)
    arr = _blend(arr, snow_base, snow_a)
    # Lit snow areas — warm diagonal sunlight from right
    snow_lit_a = np.clip((xx - 0.35) / 0.40, 0.0, 1.0) * snow_a * 0.42
    arr = _blend(arr, np.array([0.95, 0.93, 0.88], dtype=np.float32), snow_lit_a)
    # Snow shadow under forest — left side cooler and darker
    snow_shadow_a = np.clip((0.50 - xx) / 0.30, 0.0, 1.0) * snow_a * 0.30
    arr = _blend(arr, np.array([0.65, 0.70, 0.80], dtype=np.float32), snow_shadow_a)
    # Wind-scalloped snow texture (subtle horizontal ridges)
    for ridge_y in np.linspace(snow_horizon + 0.04, 1.0, 14):
        ridge_d = np.abs(yy - ridge_y) / 0.012
        ridge_a = np.clip(0.45 - ridge_d, 0.0, 1.0) * snow_a * 0.18
        arr = _blend(arr, np.array([0.96, 0.95, 0.93], dtype=np.float32), ridge_a)

    # ── Bramble stems — dried plants in foreground right ─────────────────────
    # Simplified as thin slightly-curved dark lines
    for stem_x, stem_lean in [(0.75, 0.04), (0.82, -0.03), (0.88, 0.02), (0.92, 0.05)]:
        for frac in np.linspace(0.0, 0.18, 60):
            stem_y = 1.0 - frac
            cx = stem_x + stem_lean * frac
            stem_d = np.abs(xx - cx) / 0.005
            stem_a = np.clip(1.0 - stem_d, 0.0, 1.0) * np.clip((stem_y - snow_horizon + 0.01) / 0.06, 0.0, 1.0)
            arr = _blend(arr, np.array([0.20, 0.19, 0.22], dtype=np.float32), stem_a * 0.70)
        # Seed head at top of stem
        sh_x = stem_x + stem_lean * 0.18
        sh_y = 1.0 - 0.18
        sh_d = ((xx - sh_x) / 0.012) ** 2 + ((yy - sh_y) / 0.016) ** 2
        sh_a = np.clip(1.0 - sh_d, 0.0, 1.0) * 0.65
        arr = _blend(arr, np.array([0.28, 0.25, 0.22], dtype=np.float32), sh_a)

    # ── Fox body — warm orange ellipse ───────────────────────────────────────
    fox_cx = 0.44
    fox_cy = 0.72
    fox_rx = 0.092
    fox_ry = 0.130

    body_d = ((xx - fox_cx) / fox_rx) ** 2 + ((yy - fox_cy) / fox_ry) ** 2
    body_a = np.clip(1.35 - body_d, 0.0, 1.0) ** 0.60
    fox_base = np.array([0.82, 0.44, 0.10], dtype=np.float32)   # burnt-sienna orange
    arr = _blend(arr, fox_base, body_a)

    # Sunlit upper body — brighter orange-amber on right shoulder
    lit_d = ((xx - (fox_cx + 0.04)) / 0.055) ** 2 + ((yy - (fox_cy - 0.07)) / 0.070) ** 2
    lit_a = np.clip(1.0 - lit_d, 0.0, 1.0) ** 1.5 * body_a
    arr = _blend(arr, np.array([0.90, 0.56, 0.14], dtype=np.float32), lit_a * 0.65)

    # Shadow flank — darker left side
    shadow_d = ((xx - (fox_cx - 0.05)) / 0.055) ** 2 + ((yy - fox_cy) / 0.08) ** 2
    shadow_a = np.clip(0.85 - shadow_d, 0.0, 1.0) * body_a
    arr = _blend(arr, np.array([0.55, 0.22, 0.06], dtype=np.float32), shadow_a * 0.45)

    # Belly and throat — cream-white
    belly_cx = fox_cx - 0.01
    belly_cy = fox_cy + 0.025
    belly_d = ((xx - belly_cx) / 0.038) ** 2 + ((yy - belly_cy) / 0.075) ** 2
    belly_a = np.clip(0.82 - belly_d, 0.0, 1.0) ** 0.8 * body_a
    arr = _blend(arr, np.array([0.92, 0.90, 0.84], dtype=np.float32), belly_a)

    # ── Fox head ─────────────────────────────────────────────────────────────
    head_cx = fox_cx - 0.06
    head_cy = fox_cy - fox_ry * 0.88
    head_rx = 0.058
    head_ry = 0.060
    head_d = ((xx - head_cx) / head_rx) ** 2 + ((yy - head_cy) / head_ry) ** 2
    head_a = np.clip(1.30 - head_d, 0.0, 1.0) ** 0.55
    arr = _blend(arr, np.array([0.80, 0.42, 0.10], dtype=np.float32), head_a)

    # Face lit — sunlight on right muzzle side
    face_lit_d = ((xx - (head_cx + 0.030)) / 0.035) ** 2 + ((yy - head_cy) / 0.040) ** 2
    face_lit_a = np.clip(1.0 - face_lit_d, 0.0, 1.0) ** 1.5 * head_a
    arr = _blend(arr, np.array([0.88, 0.54, 0.18], dtype=np.float32), face_lit_a * 0.55)

    # Muzzle — elongated pale snout
    muzzle_cx = head_cx - head_rx * 0.70
    muzzle_cy = head_cy + head_ry * 0.22
    muzzle_d = ((xx - muzzle_cx) / 0.048) ** 2 + ((yy - muzzle_cy) / 0.026) ** 2
    muzzle_a = np.clip(0.90 - muzzle_d, 0.0, 1.0) ** 0.8 * 0.88
    arr = _blend(arr, np.array([0.75, 0.56, 0.34], dtype=np.float32), muzzle_a)

    # Nose — dark tip
    nose_d = ((xx - (muzzle_cx - 0.040)) / 0.012) ** 2 + ((yy - muzzle_cy) / 0.012) ** 2
    nose_a = np.clip(1.0 - nose_d, 0.0, 1.0) ** 2.0
    arr = _blend(arr, np.array([0.14, 0.12, 0.14], dtype=np.float32), nose_a)

    # Eye — amber with dark pupil
    eye_cx = head_cx - head_rx * 0.22
    eye_cy = head_cy - head_ry * 0.08
    eye_d = ((xx - eye_cx) / 0.018) ** 2 + ((yy - eye_cy) / 0.018) ** 2
    eye_a = np.clip(1.0 - eye_d, 0.0, 1.0) ** 1.2
    arr = _blend(arr, np.array([0.76, 0.54, 0.10], dtype=np.float32), eye_a)
    pupil_d = ((xx - eye_cx) / 0.009) ** 2 + ((yy - eye_cy) / 0.012) ** 2
    pupil_a = np.clip(1.0 - pupil_d, 0.0, 1.0) ** 2.0
    arr = _blend(arr, np.array([0.06, 0.05, 0.06], dtype=np.float32), pupil_a)
    # Catchlight
    hl_d = ((xx - (eye_cx + 0.006)) / 0.005) ** 2 + ((yy - (eye_cy - 0.005)) / 0.005) ** 2
    hl_a = np.clip(1.0 - hl_d, 0.0, 1.0) ** 2 * 0.80
    arr = _blend(arr, np.array([0.96, 0.94, 0.90], dtype=np.float32), hl_a)

    # Ears — pointed, dark-backed
    for ear_ox, ear_oy, ear_ang in [(-0.28, -0.78, -0.20), (-0.05, -0.85, 0.12)]:
        ear_cx = head_cx + ear_ox * head_rx
        ear_cy = head_cy + ear_oy * head_ry
        ear_d = ((xx - ear_cx) / 0.022) ** 2 + ((yy - ear_cy) / 0.040) ** 2
        ear_a = np.clip(1.0 - ear_d, 0.0, 1.0) ** 0.8
        arr = _blend(arr, np.array([0.72, 0.28, 0.06], dtype=np.float32), ear_a * head_a * 1.2)
        # Dark ear interior
        ear_inner_d = ((xx - (ear_cx + 0.006)) / 0.014) ** 2 + ((yy - (ear_cy + 0.010)) / 0.028) ** 2
        ear_inner_a = np.clip(0.80 - ear_inner_d, 0.0, 1.0) * ear_a * 0.70
        arr = _blend(arr, np.array([0.16, 0.10, 0.06], dtype=np.float32), ear_inner_a)

    # ── Fox legs — dark stockings ─────────────────────────────────────────────
    for leg_ox, leg_oy in [(-0.06, 0.95), (0.04, 0.98), (0.10, 0.94), (0.18, 0.97)]:
        leg_cx = fox_cx + leg_ox
        leg_base_y = fox_cy + fox_ry * leg_oy
        leg_d = ((xx - leg_cx) / 0.016) ** 2 + ((yy - leg_base_y) / 0.035) ** 2
        leg_a = np.clip(1.0 - leg_d, 0.0, 1.0) ** 0.9
        arr = _blend(arr, np.array([0.26, 0.22, 0.16], dtype=np.float32), leg_a * 0.88)

    # Lifted forepaw — right front leg raised at 45°
    paw_cx = fox_cx - 0.10
    paw_cy = fox_cy + fox_ry * 0.68
    paw_d = ((xx - paw_cx) / 0.018) ** 2 + ((yy - paw_cy) / 0.025) ** 2
    paw_a = np.clip(1.0 - paw_d, 0.0, 1.0) ** 1.2
    arr = _blend(arr, np.array([0.20, 0.18, 0.14], dtype=np.float32), paw_a * 0.90)

    # ── Tail — sweeping down and right ────────────────────────────────────────
    # Parametric tail arc
    for frac in np.linspace(0.0, 1.0, 200):
        tail_x = fox_cx + 0.08 + frac * 0.14
        tail_y = fox_cy + fox_ry * 0.20 + frac * 0.22 + frac ** 1.8 * 0.08
        tail_w = 0.028 * (1.0 - frac * 0.3)
        t_d = ((xx - tail_x) / tail_w) ** 2 + ((yy - tail_y) / (tail_w * 1.6)) ** 2
        t_a = np.clip(1.0 - t_d, 0.0, 1.0) ** 0.7
        tail_col = (np.array([0.75, 0.38, 0.08], dtype=np.float32) * (1.0 - frac * 0.15) +
                    np.array([0.92, 0.90, 0.86], dtype=np.float32) * frac * 0.15)
        arr = _blend(arr, tail_col, t_a * 0.82)
    # White tail tip
    tip_d = ((xx - (fox_cx + 0.22)) / 0.024) ** 2 + ((yy - (fox_cy + fox_ry * 0.42)) / 0.030) ** 2
    tip_a = np.clip(1.0 - tip_d, 0.0, 1.0) ** 1.2
    arr = _blend(arr, np.array([0.96, 0.94, 0.90], dtype=np.float32), tip_a)

    arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(3.5))
    return img


def paint(output_path: str = "s209_fox.png") -> str:
    """
    Paint 'Pause at the Birch Line' — red fox at winter woodland edge.
    Josef Albers chromatic interaction: 120th mode albers_homage_square_pass.
    """
    print("=" * 64)
    print("  Session 209 — 'Pause at the Birch Line'")
    print("  Red fox at birch woodland edge, deep winter")
    print("  Technique: Josef Albers chromatic zone interaction")
    print("  120th mode: albers_homage_square_pass")
    print("=" * 64)

    ref_img = build_fox_reference(W, H)
    ref_arr = np.array(ref_img, dtype=np.float32) / 255.0
    print(f"  Reference built  ({W}x{H})")

    albers = get_style("josef_albers")
    p = Painter(W, H)

    # Ground: Albers' medium grey Masonite feel
    print("  [1] Tone ground — medium grey ...")
    p.tone_ground(albers.ground_color, texture_strength=0.04)

    print("  [2] Underpainting ...")
    p.underpainting(ref_img, stroke_size=32, n_strokes=1800)

    print("  [3] Block in — broad colour zones ...")
    p.block_in(ref_img, stroke_size=20, n_strokes=2200)

    print("  [4] Build form ...")
    p.build_form(ref_img, stroke_size=10, n_strokes=2800)

    print("  [5] Place lights ...")
    p.place_lights(ref_img, stroke_size=5, n_strokes=280)

    print("  [6] Meso detail ...")
    p.meso_detail_pass(opacity=0.32)

    # ── Albers signature pass — chromatic zone interaction ────────────────────
    print("  [7] albers_homage_square_pass (120th mode) ...")
    p.albers_homage_square_pass(
        n_zones=6,
        contrast_strength=0.18,
        zone_sigma=9.0,
        opacity=0.60,
    )

    # Finishing
    print("  [8] Edge definition ...")
    p.edge_definition_pass(opacity=0.28)

    # Cool-blue glaze to unify the winter palette
    print("  [9] Final cool glaze ...")
    p.glaze((0.56, 0.60, 0.72), opacity=0.035)

    print("  [10] Finish (vignette + crackle off) ...")
    p.finish(vignette=0.30, crackle=False)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    out = paint()
    print(f"\n  Done: {out}")
