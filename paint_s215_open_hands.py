"""
paint_s215_open_hands.py — Original composition: "Open Hands"

Session 215 painting — inspired by Lucian Freud (1922–2011).

IMAGE DESCRIPTION
=================
Subject & Composition:
  A solitary woman seated in three-quarter view, slightly below eye level —
  as if the viewer occupies a low stool directly across from her. She faces
  three-quarters left, her gaze falling just past the canvas edge with the
  unfocused intensity of someone deep in exhausted thought. Her form is
  substantial — heavyset, filling the lower two-thirds of the canvas with an
  unselfconscious physical presence that Freud sought obsessively. She is
  positioned slightly left of centre, with negative space opening to the right
  where the studio wall catches raking light.

The Figure:
  A woman in her mid-fifties, heavyset, wearing a simple pale cotton
  undergarment — the fabric bunched and creased at the abdomen where it has
  rucked up from sitting. Her hands rest open in her lap, palms up, fingers
  slightly curled, as though she has just set something down or is too tired
  to hold anything anymore. Her left hand is slightly higher than her right.
  Her bare shoulders carry the cool greenish-grey of north-light shadow across
  the trapezius and upper arm; her chest and face hold a warmer, rawer tone —
  raw sienna over a cool umber ground. Her expression is one of resigned
  vulnerability: not sadness exactly, but the emotional exhaustion that has
  settled past self-consciousness into something more permanent. The skin
  reads as biological fact — not beauty or ugliness, simply the presence of
  a body that has been looked at for a very long time.

The Environment:
  A small London studio, spare and entirely utilitarian. A worn wooden slat-
  back chair occupies the lower-left frame edge, its rail visible as a dark
  horizontal behind the figure's hip. The floor is bare darkened floorboards —
  years of oil paint and turpentine have blackened the grain. At the lower
  right, a half-squeezed tube of paint lies abandoned on the floor, a small
  bright note of cadmium against the dark wood. The background is uneven
  plaster: cream-white near the top, sliding into warm grey in the shadow
  behind the figure's left shoulder. There is no ornament, no furniture, no
  window in frame — only wall, floor, and the figure. The light falls from
  a north-facing window just off the upper-left edge of the canvas: cool,
  absolute, raking, merciless in its revelation of every surface it touches.
  The shadow on the right side of the figure's body is deep, cool, and final.

Technique & Palette:
  Lucian Freud's late-period loaded-brush impasto — 126th distinct mode:
  freud_impasto_vulnerability_pass. Cool titanium white highlights build on
  the shoulder ridge, the collarbone, the dorsal surface of the left hand.
  Warm raw-sienna passages breathe in the forearm and face. Shadow areas
  are pushed toward the characteristic cool green-grey of Freud's studio
  ambient — (0.44, 0.49, 0.40) — the tone that reads as skin seen through
  north light, not as darkness. The paint surface thickens at ridges of
  form: the brow, the collarbone, the knuckle line. The ridge amplification
  pass exaggerates local luminance contrast wherever paint would physically
  build up, then pulls shadows toward the cool green-grey tone, then applies
  the raking light gradient that brightens the upper portions of the canvas
  and lets the lower fall into studio ambient.

  Palette:
    Warm flesh highlight:       (0.82, 0.72, 0.60)
    Mid flesh — raw sienna-grey:(0.58, 0.53, 0.45)
    Shadow — cool green-grey:   (0.44, 0.49, 0.40)
    Raw umber dark:             (0.28, 0.25, 0.20)
    Cold titanium white:        (0.90, 0.90, 0.88)
    Near-black studio shadow:   (0.15, 0.15, 0.12)
    Mid-tone unifying warmth:   (0.55, 0.50, 0.42)

Mood & Intent:
  The image aims for the uncomfortable intimacy that is Freud's hallmark —
  the sense of having looked at someone far too carefully and for far too long.
  The open hands are the composition's emotional centre: hands that have
  released whatever they were holding. The viewer should feel the weight of
  sustained attention, the biological fact of the human body, and underneath
  the ruthless scrutiny, an unmistakable and complicated affection. No
  flattery. No distance. Only the paint, the light, and the person.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter
from art_catalog import get_style

W, H = 540, 780


def build_open_hands_reference(w: int, h: int) -> Image.Image:
    """
    Synthetic reference for the Open Hands composition.
    Seated heavyset woman in three-quarter view, north-light studio,
    hands open in lap, cool green-grey shadows, warm flesh highlights.
    """
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None] * np.ones((1, w), dtype=np.float32)
    xx = np.ones((h, 1), dtype=np.float32) * np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]

    def _blend(base, colour, alpha):
        a = np.clip(alpha[:, :, None] if alpha.ndim == 2 else alpha, 0.0, 1.0)
        return base * (1.0 - a) + colour[None, None, :] * a

    # ── Studio wall — uneven plaster, cream to warm grey ─────────────────────
    wall_hi  = np.array([0.88, 0.85, 0.78], dtype=np.float32)
    wall_lo  = np.array([0.62, 0.59, 0.52], dtype=np.float32)
    wall_t   = np.clip(yy * 1.1, 0.0, 1.0)[:, :, None]  # (H, W, 1)
    arr      = wall_hi[None, None, :] * (1.0 - wall_t) + wall_lo[None, None, :] * wall_t

    # Raking light gradient on wall — brighter upper-left corner
    upper_left_light = np.clip(1.0 - (xx * 0.6 + yy * 0.4), 0.0, 1.0) * 0.18
    arr = np.clip(arr + upper_left_light[:, :, None] * np.array([0.10, 0.09, 0.08]), 0.0, 1.0)

    # Plaster texture — slight uneven warmth patches
    rng = np.random.RandomState(215)
    plaster_noise = rng.uniform(-0.025, 0.025, (h, w, 3)).astype(np.float32)
    arr = np.clip(arr + plaster_noise, 0.0, 1.0)

    # ── Dark studio floor — blackened floorboards ─────────────────────────────
    floor_y    = 0.74
    floor_fade = np.clip((yy - floor_y) / 0.05, 0.0, 1.0)
    floor_col  = np.array([0.22, 0.19, 0.14], dtype=np.float32)
    arr        = _blend(arr, floor_col, floor_fade * 0.92)

    # Floorboard grain lines
    for board_y in np.linspace(floor_y + 0.02, 1.0, 18):
        byd = np.abs(yy - board_y) / 0.004
        bya = np.clip(1.0 - byd, 0.0, 1.0) ** 2 * 0.18 * floor_fade
        arr = _blend(arr, np.array([0.12, 0.10, 0.07], dtype=np.float32), bya)

    # Shadow pooling at floor-wall junction
    wall_floor_jx = np.clip((yy - floor_y + 0.04) / 0.08, 0.0, 1.0) * \
                    np.clip((0.78 - xx) / 0.06, 0.0, 1.0) * 0.40
    arr = _blend(arr, np.array([0.10, 0.09, 0.07], dtype=np.float32), wall_floor_jx)

    # ── Chair slat — dark horizontal bar behind figure hip ────────────────────
    chair_y    = 0.68
    chair_x_lo = 0.05
    chair_x_hi = 0.42
    chair_fade = (
        np.clip(1.0 - np.abs(yy - chair_y) / 0.013, 0.0, 1.0) *
        np.clip((xx - chair_x_lo) / 0.015, 0.0, 1.0) *
        np.clip((chair_x_hi - xx) / 0.015, 0.0, 1.0)
    ) ** 0.8
    arr = _blend(arr, np.array([0.16, 0.13, 0.10], dtype=np.float32), chair_fade * 0.85)

    # Chair vertical posts
    for post_x in [0.10, 0.30]:
        pd = np.abs(xx - post_x) / 0.009
        pa = np.clip(1.0 - pd, 0.0, 1.0) ** 1.2 * \
             np.clip((yy - chair_y) / 0.03, 0.0, 1.0) * \
             np.clip((floor_y + 0.06 - yy) / 0.02, 0.0, 1.0)
        arr = _blend(arr, np.array([0.16, 0.13, 0.10], dtype=np.float32), pa * 0.75)

    # ── Abandoned paint tube — lower right ────────────────────────────────────
    tube_cx = 0.76
    tube_cy = 0.90
    tube_d  = ((xx - tube_cx) / 0.046) ** 2 + ((yy - tube_cy) / 0.018) ** 2
    tube_a  = np.clip(1.0 - tube_d, 0.0, 1.0) ** 0.7 * floor_fade
    arr     = _blend(arr, np.array([0.82, 0.28, 0.06], dtype=np.float32), tube_a * 0.80)

    # ── Figure — seated heavyset woman in three-quarter view ──────────────────
    # Flesh tones: warm highlight, cool shadow
    flesh_warm = np.array([0.78, 0.64, 0.52], dtype=np.float32)
    flesh_mid  = np.array([0.62, 0.54, 0.44], dtype=np.float32)
    flesh_cool = np.array([0.44, 0.49, 0.40], dtype=np.float32)  # Freud shadow
    garment    = np.array([0.87, 0.84, 0.78], dtype=np.float32)  # pale cotton

    fig_cx     = 0.40   # figure centre x (left of centre)
    head_cy    = 0.18
    torso_cy   = 0.42
    lap_cy     = 0.62

    # ── Head — three-quarter view, facing slightly left ───────────────────────
    head_rx = 0.072
    head_ry = 0.085
    hd = ((xx - (fig_cx - 0.03)) / head_rx) ** 2 + ((yy - head_cy) / head_ry) ** 2
    ha = np.clip(1.30 - hd, 0.0, 1.0) ** 0.55

    # Face: warm on lit side (right), cool on shadow side (left)
    face_light = np.clip((xx - (fig_cx - 0.09)) / 0.09, 0.0, 1.0)[:, :, None]  # (H,W,1)
    face_col   = flesh_warm[None, None, :] * face_light + flesh_cool[None, None, :] * (1.0 - face_light)  # (H,W,3)
    # blend face_col into arr using ha as alpha
    ha3 = np.clip(ha[:, :, None] * 0.92, 0.0, 1.0)
    arr = np.clip(arr * (1.0 - ha3) + face_col * ha3, 0.0, 1.0)

    # Lit side highlight (upper right of face)
    lit_d = ((xx - (fig_cx + 0.01)) / 0.032) ** 2 + ((yy - (head_cy - 0.015)) / 0.028) ** 2
    lit_a = np.clip(1.0 - lit_d, 0.0, 1.0) ** 1.5 * ha
    arr   = _blend(arr, np.array([0.88, 0.78, 0.64], dtype=np.float32), lit_a * 0.55)

    # Shadow side (left cheek/jaw) — cool green-grey
    shd = ((xx - (fig_cx - 0.07)) / 0.034) ** 2 + ((yy - (head_cy + 0.018)) / 0.040) ** 2
    sha = np.clip(1.0 - shd, 0.0, 1.0) ** 1.2 * ha
    arr = _blend(arr, flesh_cool, sha * 0.60)

    # Hair — dark, pulled loosely back
    hair_col = np.array([0.22, 0.18, 0.14], dtype=np.float32)
    hair_d   = ((xx - (fig_cx - 0.04)) / 0.064) ** 2 + ((yy - (head_cy - 0.065)) / 0.038) ** 2
    hair_a   = np.clip(0.95 - hair_d, 0.0, 1.0) ** 1.1
    arr      = _blend(arr, hair_col, hair_a * 0.88)

    # Temple wisps
    for wx, wy in [(fig_cx + 0.022, head_cy - 0.018), (fig_cx - 0.078, head_cy - 0.012)]:
        wd = ((xx - wx) / 0.018) ** 2 + ((yy - wy) / 0.024) ** 2
        wa = np.clip(0.80 - wd, 0.0, 1.0) ** 1.3 * ha
        arr = _blend(arr, hair_col, wa * 0.55)

    # ── Neck ──────────────────────────────────────────────────────────────────
    neck_cx = fig_cx - 0.010
    neck_d  = ((xx - neck_cx) / 0.022) ** 2 + ((yy - (head_cy + head_ry * 0.78)) / 0.030) ** 2
    neck_a  = np.clip(1.25 - neck_d, 0.0, 1.0) ** 0.65
    arr     = _blend(arr, flesh_mid, neck_a * 0.85)

    # ── Shoulders and upper body — wide, substantial ──────────────────────────
    # Left shoulder (in shadow — cool green-grey)
    ls_cx = fig_cx - 0.16
    ls_d  = ((xx - ls_cx) / 0.090) ** 2 + ((yy - 0.30) / 0.060) ** 2
    ls_a  = np.clip(1.20 - ls_d, 0.0, 1.0) ** 0.55
    arr   = _blend(arr, flesh_cool, ls_a * 0.85)

    # Right shoulder (lit — warm flesh)
    rs_cx = fig_cx + 0.14
    rs_d  = ((xx - rs_cx) / 0.085) ** 2 + ((yy - 0.28) / 0.058) ** 2
    rs_a  = np.clip(1.20 - rs_d, 0.0, 1.0) ** 0.55
    arr   = _blend(arr, flesh_warm, rs_a * 0.82)

    # Collarbone highlight — thin bright ridge
    collar_d  = ((xx - (fig_cx - 0.01)) / 0.085) ** 2 + ((yy - 0.24) / 0.012) ** 2
    collar_a  = np.clip(1.0 - collar_d, 0.0, 1.0) ** 1.8
    arr       = _blend(arr, np.array([0.88, 0.84, 0.76], dtype=np.float32), collar_a * 0.45)

    # ── Garment — pale cotton, bunched at abdomen ─────────────────────────────
    garment_d = ((xx - fig_cx) / 0.170) ** 2 + ((yy - 0.52) / 0.210) ** 2
    garment_a = np.clip(1.15 - garment_d, 0.0, 1.0) ** 0.50
    arr       = _blend(arr, garment, garment_a * 0.90)

    # Fabric creases — faint darker lines
    for cy in [0.44, 0.50, 0.56, 0.62]:
        cd = np.abs(yy - cy) / 0.005 + np.abs(xx - (fig_cx + 0.04)) / 0.120
        ca = np.clip(1.0 - cd, 0.0, 1.0) ** 2 * garment_a * 0.35
        arr = _blend(arr, np.array([0.68, 0.66, 0.61], dtype=np.float32), ca)

    # ── Left arm — in shadow, cool ────────────────────────────────────────────
    for frac in np.linspace(0.0, 1.0, 80):
        ax  = fig_cx - 0.16 + frac * 0.06
        ay  = 0.32 + frac * 0.26
        aw  = 0.028 * (1.0 - frac * 0.15)
        ad  = ((xx - ax) / aw) ** 2 + ((yy - ay) / (aw * 2.0)) ** 2
        aa  = np.clip(1.0 - ad, 0.0, 1.0) ** 0.75
        col = flesh_cool * (1.0 - frac * 0.2) + flesh_mid * (frac * 0.2)
        arr = _blend(arr, col, aa * 0.82)

    # ── Right arm — lit, warm ─────────────────────────────────────────────────
    for frac in np.linspace(0.0, 1.0, 80):
        ax  = fig_cx + 0.15 - frac * 0.08
        ay  = 0.30 + frac * 0.28
        aw  = 0.030 * (1.0 - frac * 0.12)
        ad  = ((xx - ax) / aw) ** 2 + ((yy - ay) / (aw * 2.0)) ** 2
        aa  = np.clip(1.0 - ad, 0.0, 1.0) ** 0.75
        col = flesh_warm * (1.0 - frac * 0.15) + flesh_mid * (frac * 0.15)
        arr = _blend(arr, col, aa * 0.84)

    # ── Hands in lap — open, palms up ─────────────────────────────────────────
    # Left hand (slightly higher, palm catching light)
    lh_cx = fig_cx - 0.06
    lh_cy = 0.66
    lh_d  = ((xx - lh_cx) / 0.060) ** 2 + ((yy - lh_cy) / 0.038) ** 2
    lh_a  = np.clip(1.10 - lh_d, 0.0, 1.0) ** 0.65
    arr   = _blend(arr, flesh_mid, lh_a * 0.86)

    # Palm highlight — concave catching raking light
    lhp_d = ((xx - (lh_cx + 0.010)) / 0.028) ** 2 + ((yy - (lh_cy - 0.005)) / 0.018) ** 2
    lhp_a = np.clip(1.0 - lhp_d, 0.0, 1.0) ** 1.5 * lh_a
    arr   = _blend(arr, np.array([0.84, 0.74, 0.60], dtype=np.float32), lhp_a * 0.48)

    # Left hand fingers — slightly curled
    for i, (fx, fy, fw) in enumerate([
        (lh_cx - 0.040, lh_cy + 0.022, 0.014),
        (lh_cx - 0.015, lh_cy + 0.030, 0.013),
        (lh_cx + 0.012, lh_cy + 0.028, 0.012),
        (lh_cx + 0.036, lh_cy + 0.022, 0.011),
    ]):
        fd = ((xx - fx) / fw) ** 2 + ((yy - fy) / (fw * 1.6)) ** 2
        fa = np.clip(1.0 - fd, 0.0, 1.0) ** 0.85
        arr = _blend(arr, flesh_mid, fa * 0.78)

    # Right hand (lower, slightly more in shadow)
    rh_cx = fig_cx + 0.08
    rh_cy = 0.69
    rh_d  = ((xx - rh_cx) / 0.058) ** 2 + ((yy - rh_cy) / 0.035) ** 2
    rh_a  = np.clip(1.10 - rh_d, 0.0, 1.0) ** 0.65
    arr   = _blend(arr, flesh_mid * 0.92 + flesh_cool * 0.08, rh_a * 0.84)

    # Right hand fingers
    for i, (fx, fy, fw) in enumerate([
        (rh_cx - 0.038, rh_cy + 0.020, 0.013),
        (rh_cx - 0.014, rh_cy + 0.028, 0.012),
        (rh_cx + 0.012, rh_cy + 0.026, 0.012),
        (rh_cx + 0.034, rh_cy + 0.020, 0.011),
    ]):
        fd = ((xx - fx) / fw) ** 2 + ((yy - fy) / (fw * 1.6)) ** 2
        fa = np.clip(1.0 - fd, 0.0, 1.0) ** 0.85
        col = flesh_mid if i < 2 else flesh_cool
        arr = _blend(arr, col, fa * 0.76)

    # ── Thumb accents ─────────────────────────────────────────────────────────
    for tx, ty in [(lh_cx + 0.050, lh_cy - 0.006), (rh_cx - 0.052, rh_cy - 0.004)]:
        td = ((xx - tx) / 0.016) ** 2 + ((yy - ty) / 0.022) ** 2
        ta = np.clip(1.0 - td, 0.0, 1.0) ** 1.0
        arr = _blend(arr, flesh_mid, ta * 0.70)

    # ── Studio shadow — deep right side of figure ─────────────────────────────
    shadow_mask = np.clip((xx - 0.55) / 0.12, 0.0, 1.0) * \
                  np.clip((yy - 0.20) / 0.10, 0.0, 1.0) * 0.45
    arr = _blend(arr, np.array([0.15, 0.15, 0.12], dtype=np.float32), shadow_mask)

    # ── Final soft pre-blur (Freud's paint still wet and blending) ────────────
    arr = np.clip(arr, 0.0, 1.0)
    arr_uint8 = (arr * 255).astype(np.uint8)
    img = Image.fromarray(arr_uint8, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(2.8))
    return img


def paint(output_path: str = "s215_open_hands.png") -> str:
    """
    Paint 'Open Hands' — heavyset woman in north-light studio, palms open.
    Lucian Freud impasto vulnerability: 126th mode.
    """
    print("=" * 64)
    print("  Session 215 — 'Open Hands'")
    print("  Seated woman, north-light London studio, hands open in lap")
    print("  Technique: Lucian Freud Impasto Vulnerability")
    print("  126th mode: freud_impasto_vulnerability_pass")
    print("=" * 64)

    ref_img = build_open_hands_reference(W, H)
    print(f"  Reference built  ({W}x{H})")

    freud = get_style("lucian_freud")
    p = Painter(W, H)

    # Cool grey-brown ground — Freud's studio-toned canvas
    print("  [1] Tone ground — cool grey-brown ...")
    p.tone_ground(freud.ground_color, texture_strength=0.06)

    # Large underpainting — establish tonal masses
    print("  [2] Underpainting — large tonal masses ...")
    p.underpainting(ref_img, stroke_size=36, n_strokes=2200)

    # Block in — loaded brush marks, mid-range
    print("  [3] Block in — loaded hog-hair marks ...")
    p.block_in(ref_img, stroke_size=22, n_strokes=2800)

    # Build form — smaller strokes, establish flesh volumes
    print("  [4] Build form — flesh volumes ...")
    p.build_form(ref_img, stroke_size=12, n_strokes=3400)

    # Place lights — impasto highlight strokes
    print("  [5] Place lights — impasto highlights ...")
    p.place_lights(ref_img, stroke_size=6, n_strokes=380)

    # ── Freud signature pass — impasto vulnerability ──────────────────────────
    print("  [6] freud_impasto_vulnerability_pass (126th mode) ...")
    p.freud_impasto_vulnerability_pass(
        ridge_radius=4,
        ridge_threshold=0.04,
        ridge_strength=0.55,
        shadow_threshold=0.38,
        shadow_cool_strength=0.40,
        raking_falloff=0.72,
        opacity=0.78,
    )

    # Lost and found edges — Freud's edges dissolve into shadow and reform in light
    print("  [7] Edge lost and found ...")
    p.edge_lost_and_found_pass(strength=0.40, figure_only=False)

    # Meso detail — skin pore texture, paint ridges
    print("  [8] Meso detail ...")
    p.meso_detail_pass(opacity=0.30)

    # Finish — minimal vignette, no crackle (modern canvas)
    print("  [9] Finish ...")
    p.finish(vignette=0.14, crackle=False)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    out = paint()
    print(f"\n  Done: {out}")
