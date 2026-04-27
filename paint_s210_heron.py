"""
paint_s210_heron.py — Original composition: "The Amber Shore"

Session 210 painting — inspired by Hans Hofmann (1880–1966).

IMAGE DESCRIPTION
=================
Subject & Composition:
  A great blue heron (Ardea herodias), seen from the right side at a slight
  diagonal — 10° behind and 5° below eye level — standing absolutely motionless
  in shallow coastal tidal water, perhaps 20cm deep. The bird is positioned at
  centre-left, occupying about 55% of the canvas height. It faces left, neck
  drawn into a slow-S hunting curve, head tilted fractionally downward, one
  leg raised mid-stride as if the bird paused in mid-step when it sensed
  something in the water below. The composition runs from lower-left foreground
  (warm water surface catching sunrise) to upper-right (deep violet predawn sky).
  A strong diagonal: the horizon line cuts across the canvas at roughly 40%
  from the bottom, glowing amber, with the heron straddling this line between
  sky-world and water-world.

The Figure:
  The heron is a large, ancient-looking bird — 1.2 metres tall, slate-blue-grey
  body, long dark dagger bill, white face with a black supercilium stripe and a
  black plume trailing from the crown. The neck feathers are streaked white and
  grey. The wings are folded, the primaries showing deep charcoal slate at the
  tips. The long legs are yellowish-grey, disappearing below the water surface.
  The raised foot — long toed, slightly spread — is just above the water line,
  catching the amber sunrise light on its upper surface while casting a cool
  violet-blue shadow beneath. The eye is a fierce, concentrated amber-yellow,
  pupil vertical and dark. The bird's emotional state is one of supreme, focused
  patience — the concentration of a predator for whom stillness is the only
  strategy. Not tense: still. Not waiting: already arrived.

The Environment:
  Coastal estuary at first light. The far horizon is a band of deep, saturated
  cadmium orange-gold where the sun has just broken below the cloud line —
  this warmth PUSHES hard toward the viewer (Hofmann's push-pull at maximum).
  Above this band, the sky graduates through warm amber to cool apricot to
  the deep blue-violet of the remaining predawn sky at the top — this cool
  PULLS away into depth. Below the horizon, the water reflects the sunrise:
  broken amber and gold streaks run horizontally across the estuary surface,
  interrupted by cool blue-grey where the water is in shadow. The foreground
  water is darkest — deep cool teal-grey with amber highlights where ripples
  catch the low sunrise angle. In the far left background, a distant treeline
  of mangrove or coastal reeds sits as a dark blue-violet silhouette, barely
  warmer than the sky. A few thin horizontal bands of cloud at the horizon
  catch the orange-gold beneath and deep charcoal above. The water surface
  shows concentric ripples from the heron's submerged leg — three gentle rings
  expanding outward in cool grey-blue, with amber glints at the crest of each
  ring where the light catches the curve.

Technique & Palette:
  Hans Hofmann's Push-Pull principle — the 121st distinct mode:
  hofmann_push_pull_pass. Warm areas of the canvas (the amber sunrise, the
  golden water reflections, the lit portions of the heron's neck and legs)
  ADVANCE toward the viewer — they appear physically closer than their actual
  position in the composition would suggest. Cool areas (the heron's blue-grey
  body and the predawn violet sky) RECEDE — the bird itself, despite being the
  foreground subject, is being pulled backward in perceptual space by the cool
  temperature of its plumage. This creates a thrilling perceptual paradox: the
  sunrise behind the bird feels closer than the bird itself, and the heron
  exists in a zone of spatial tension between two advancing and receding forces.
  This is exactly the spatial paradox Hofmann described — colour creates space
  independent of position.

  Palette:
    Cadmium orange-gold (sunrise band):    (0.94, 0.62, 0.10)
    Deep amber (water reflection lit):     (0.88, 0.50, 0.12)
    Apricot-warm (sky near horizon):       (0.84, 0.62, 0.38)
    Violet-blue (predawn upper sky):       (0.22, 0.24, 0.48)
    Cool blue-grey (heron body):           (0.44, 0.48, 0.58)
    Deep charcoal (heron wing tips/bill):  (0.16, 0.16, 0.20)
    Amber-yellow (heron eye):              (0.86, 0.72, 0.12)
    Teal-grey (foreground water):          (0.24, 0.34, 0.40)
    Pale gold (water ripple crests):       (0.92, 0.80, 0.48)

Mood & Intent:
  The painting is about the exact moment before the strike — when the heron has
  committed to stillness as action, when patience has become a form of violence.
  The Hofmann push-pull deepens the tension: the warm world of sunlight is
  pressing forward into the viewer's space while the cold, disciplined bird
  recedes into its own still blue-grey interior. The heron is simultaneously
  the most present and the most withdrawn thing in the frame. The viewer should
  feel the cold air carrying the smell of salt and mud, the absolute silence
  broken only by water, and underneath it all, something like reverence — for
  the efficiency of a creature that has perfected the art of waiting.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter
from art_catalog import get_style

W, H = 540, 780


def build_heron_reference(w: int, h: int) -> Image.Image:
    """
    Synthetic reference for the great blue heron at dawn composition.
    Warm amber sunrise horizon, cool violet predawn sky, heron in tidal water.
    """
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None] * np.ones((1, w), dtype=np.float32)
    xx = np.ones((h, 1), dtype=np.float32) * np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]

    def _blend(base, colour, alpha):
        a = np.clip(alpha[:, :, None], 0.0, 1.0)
        return base * (1.0 - a) + colour[None, None, :] * a

    horizon_y = 0.40   # horizon at 40% from top

    # ── Sky: gradient from deep violet-blue at top through apricot to amber ──
    # Upper predawn sky — deep blue-violet
    sky_deep = np.array([0.22, 0.24, 0.48], dtype=np.float32)
    # Near-horizon apricot
    sky_apricot = np.array([0.84, 0.62, 0.38], dtype=np.float32)
    # At horizon: cadmium orange-gold band
    horizon_gold = np.array([0.94, 0.62, 0.10], dtype=np.float32)

    # Build sky as vertical gradient (top=blue-violet, horizon=orange-gold)
    t_sky = np.clip(yy / horizon_y, 0.0, 1.0)   # 0=top (violet), 1=horizon (gold)
    # Two-stage blend: upper half violet→apricot, lower half apricot→gold
    t1 = np.clip(t_sky * 2.0, 0.0, 1.0)
    t2 = np.clip(t_sky * 2.0 - 1.0, 0.0, 1.0)
    arr = (sky_deep[None, None, :] * (1.0 - t1) +
           sky_apricot[None, None, :] * t1 * (1.0 - t2) +
           horizon_gold[None, None, :] * t2)
    # Apply gradient only above horizon
    sky_mask = (yy < horizon_y).astype(np.float32)
    base = sky_deep[None, None, :] * np.ones((h, w, 3), dtype=np.float32)
    arr = arr * sky_mask[:, :, None] + base * (1.0 - sky_mask[:, :, None])

    # ── Horizon glow band — saturated cadmium orange across the horizon ───────
    horizon_dist = np.abs(yy - horizon_y)
    horizon_glow_a = np.clip(0.50 - horizon_dist * 12.0, 0.0, 0.50)
    arr = _blend(arr, horizon_gold, horizon_glow_a)

    # ── Cloud streaks near horizon ────────────────────────────────────────────
    for cloud_y_frac, cloud_h_frac, cloud_dark in [
        (0.32, 0.022, 0.50),   # dark cloud above glow
        (0.36, 0.012, 0.30),   # thin dark stripe
        (0.38, 0.008, 0.55),   # darker cloud just above horizon
    ]:
        cloud_d = np.abs(yy - cloud_y_frac) / cloud_h_frac
        cloud_a = np.clip(1.0 - cloud_d, 0.0, 1.0) ** 0.7 * cloud_dark
        arr = _blend(arr, np.array([0.14, 0.14, 0.20], dtype=np.float32), cloud_a)

    # ── Water: occupies lower 60% of canvas ──────────────────────────────────
    water_horizon = horizon_y
    water_mask = np.clip((yy - water_horizon) / 0.04, 0.0, 1.0)

    # Water base: deep cool teal-grey, darker in foreground
    water_deep = np.array([0.24, 0.34, 0.40], dtype=np.float32)
    water_mid  = np.array([0.30, 0.40, 0.48], dtype=np.float32)
    water_near_horizon = np.array([0.48, 0.52, 0.58], dtype=np.float32)

    # Gradient from cool teal (foreground bottom) to lighter near horizon
    t_water = np.clip((yy - water_horizon) / (1.0 - water_horizon), 0.0, 1.0)
    # Reverse: near horizon (t→0) is lighter, foreground (t→1) is darker
    water_colour = (water_near_horizon[None, None, :] * (1.0 - t_water) +
                    water_deep[None, None, :] * t_water)
    arr = arr * (1.0 - water_mask[:, :, None]) + water_colour * water_mask[:, :, None]

    # ── Amber reflection streaks on water surface ─────────────────────────────
    # Sunrise is reflected as horizontal bands on water near horizon
    for ref_y_frac in np.linspace(water_horizon + 0.02, water_horizon + 0.18, 8):
        ref_w = 0.006 + 0.002 * np.random.RandomState(int(ref_y_frac * 1000)).uniform()
        ref_d = np.abs(yy - ref_y_frac) / ref_w
        # Reflection slightly narrower left (shadow of treeline) and wider right
        ref_x_fade = np.clip(xx * 1.4, 0.0, 1.0)
        ref_a = np.clip(1.0 - ref_d, 0.0, 1.0) ** 0.6 * 0.55 * water_mask * ref_x_fade
        arr = _blend(arr, np.array([0.92, 0.60, 0.16], dtype=np.float32), ref_a)

    # Ripple crests (concentric rings from heron leg position)
    heron_x = 0.38
    heron_water_y = water_horizon + 0.04   # where legs enter water
    for ring_r in [0.04, 0.08, 0.13]:
        dist_from_leg = np.sqrt(((xx - heron_x) * 1.2) ** 2 + (yy - heron_water_y) ** 2)
        ring_d = np.abs(dist_from_leg - ring_r) / 0.008
        ring_a = np.clip(1.0 - ring_d, 0.0, 1.0) ** 1.5 * water_mask * 0.40
        # Inner crest: warm amber; trough: cool blue-grey
        arr = _blend(arr, np.array([0.92, 0.78, 0.38], dtype=np.float32), ring_a)

    # ── Distant mangrove/reed treeline — deep blue-violet silhouette ──────────
    treeline_y = horizon_y - 0.04
    # Irregular treeline profile
    tree_heights = np.zeros(w, dtype=np.float32)
    rng = np.random.RandomState(42)
    for _ in range(25):
        tc = rng.uniform(0.0, 0.6)
        tw = rng.uniform(0.02, 0.07)
        th = rng.uniform(0.02, 0.05)
        xs_i = np.linspace(0.0, 1.0, w, dtype=np.float32)
        tree_heights += np.clip(1.0 - np.abs(xs_i - tc) / tw, 0.0, 1.0) * th
    tree_heights = np.clip(tree_heights, 0.0, 0.06)

    for xi in range(w):
        top_y = treeline_y - tree_heights[xi]
        tree_col = np.array([0.16, 0.18, 0.30], dtype=np.float32)   # deep blue-violet
        t_d = np.abs(yy[:, xi] - (top_y + treeline_y) * 0.5) / max((treeline_y - top_y) * 0.5, 0.001)
        tree_a = np.clip(1.0 - t_d, 0.0, 1.0) * np.clip((treeline_y - yy[:, xi]) / 0.008, 0.0, 1.0)
        # Only draw where we're above horizon (sky area)
        above_horizon = (yy[:, xi] < horizon_y).astype(np.float32)
        in_tree = (yy[:, xi] >= top_y).astype(np.float32) * above_horizon
        arr[:, xi, :] = arr[:, xi, :] * (1.0 - in_tree[:, None] * 0.85) + tree_col[None, :] * in_tree[:, None] * 0.85

    # ── Heron body — tall, slate-blue-grey bird ───────────────────────────────
    heron_cx = 0.38
    heron_cy = 0.48    # body centre (straddles horizon)
    heron_rx = 0.065
    heron_ry = 0.170

    # Body ellipse
    body_d = ((xx - heron_cx) / heron_rx) ** 2 + ((yy - heron_cy) / heron_ry) ** 2
    body_a = np.clip(1.35 - body_d, 0.0, 1.0) ** 0.55
    heron_body_col = np.array([0.44, 0.48, 0.58], dtype=np.float32)   # slate blue-grey
    arr = _blend(arr, heron_body_col, body_a * 0.92)

    # Darker wing tips at lower body
    wing_d = ((xx - (heron_cx + 0.02)) / 0.085) ** 2 + ((yy - (heron_cy + 0.08)) / 0.08) ** 2
    wing_a = np.clip(0.80 - wing_d, 0.0, 1.0) * body_a
    arr = _blend(arr, np.array([0.20, 0.20, 0.26], dtype=np.float32), wing_a * 0.60)

    # Lit neck/chest — where sunrise amber catches the right shoulder
    neck_lit_d = ((xx - (heron_cx + 0.03)) / 0.040) ** 2 + ((yy - (heron_cy - 0.11)) / 0.065) ** 2
    neck_lit_a = np.clip(0.90 - neck_lit_d, 0.0, 1.0) * body_a
    arr = _blend(arr, np.array([0.62, 0.60, 0.64], dtype=np.float32), neck_lit_a * 0.45)

    # ── Heron neck — S-curve extending upward ─────────────────────────────────
    # Parametric S-curve from body top to head
    for frac in np.linspace(0.0, 1.0, 120):
        # S-curve: lower portion angles right, upper portion curves left
        curve = 0.028 * np.sin(frac * np.pi)
        nx = heron_cx + curve - frac * 0.025
        ny = heron_cy - heron_ry * 0.80 - frac * 0.200
        nw = 0.022 * (1.0 - frac * 0.3)
        neck_d = ((xx - nx) / nw) ** 2 + ((yy - ny) / (nw * 1.8)) ** 2
        neck_a = np.clip(1.0 - neck_d, 0.0, 1.0) ** 0.7
        # Neck colour: streaked white and grey — slightly lighter than body
        neck_col = np.array([0.52, 0.55, 0.62], dtype=np.float32)
        arr = _blend(arr, neck_col, neck_a * 0.88)

    # White face/cheek stripe
    face_cx = heron_cx - 0.020
    face_cy = heron_cy - heron_ry * 0.80 - 0.200
    face_d = ((xx - face_cx) / 0.025) ** 2 + ((yy - face_cy) / 0.038) ** 2
    face_a = np.clip(0.85 - face_d, 0.0, 1.0) ** 0.8
    arr = _blend(arr, np.array([0.90, 0.88, 0.85], dtype=np.float32), face_a * 0.80)

    # ── Head ─────────────────────────────────────────────────────────────────
    head_cx = heron_cx - 0.020
    head_cy = heron_cy - heron_ry * 0.80 - 0.215
    head_rx = 0.038
    head_ry = 0.042
    head_d = ((xx - head_cx) / head_rx) ** 2 + ((yy - head_cy) / head_ry) ** 2
    head_a = np.clip(1.25 - head_d, 0.0, 1.0) ** 0.60
    arr = _blend(arr, heron_body_col, head_a * 0.90)

    # Black crown / supercilium stripe
    crown_d = ((xx - head_cx) / 0.028) ** 2 + ((yy - (head_cy - head_ry * 0.40)) / 0.018) ** 2
    crown_a = np.clip(0.80 - crown_d, 0.0, 1.0) ** 0.9 * head_a
    arr = _blend(arr, np.array([0.10, 0.10, 0.14], dtype=np.float32), crown_a)

    # Black occipital plume — trailing from back of head
    for plume_frac in np.linspace(0.0, 1.0, 60):
        px = head_cx + 0.012 + plume_frac * 0.065
        py = head_cy - head_ry * 0.30 + plume_frac * 0.025
        pw = 0.008 * (1.0 - plume_frac * 0.5)
        pd = ((xx - px) / pw) ** 2 + ((yy - py) / (pw * 2)) ** 2
        pa = np.clip(0.9 - pd, 0.0, 1.0) ** 1.2 * 0.70
        arr = _blend(arr, np.array([0.10, 0.10, 0.14], dtype=np.float32), pa)

    # Eye — fierce amber-yellow
    eye_cx = head_cx - head_rx * 0.25
    eye_cy = head_cy
    eye_d = ((xx - eye_cx) / 0.014) ** 2 + ((yy - eye_cy) / 0.014) ** 2
    eye_a = np.clip(1.0 - eye_d, 0.0, 1.0) ** 1.4
    arr = _blend(arr, np.array([0.86, 0.72, 0.12], dtype=np.float32), eye_a)
    pupil_d = ((xx - eye_cx) / 0.006) ** 2 + ((yy - eye_cy) / 0.009) ** 2
    pupil_a = np.clip(1.0 - pupil_d, 0.0, 1.0) ** 2.0
    arr = _blend(arr, np.array([0.06, 0.05, 0.06], dtype=np.float32), pupil_a)
    # Catchlight
    hl_d = ((xx - (eye_cx + 0.004)) / 0.004) ** 2 + ((yy - (eye_cy - 0.004)) / 0.004) ** 2
    hl_a = np.clip(1.0 - hl_d, 0.0, 1.0) ** 2 * 0.85
    arr = _blend(arr, np.array([0.96, 0.94, 0.88], dtype=np.float32), hl_a)

    # ── Bill — long dark dagger ───────────────────────────────────────────────
    bill_cx = head_cx - head_rx * 1.30
    bill_cy = head_cy + head_ry * 0.15
    for bill_frac in np.linspace(0.0, 1.0, 80):
        bx = head_cx - head_rx * 0.90 - bill_frac * 0.120
        by = head_cy + head_ry * 0.18 + bill_frac * 0.010
        bw = 0.009 * (1.0 - bill_frac * 0.55)
        bd = ((xx - bx) / bw) ** 2 + ((yy - by) / (bw * 0.8)) ** 2
        ba = np.clip(0.95 - bd, 0.0, 1.0) ** 0.8
        # Bill: dark yellow-grey near head, dark grey at tip
        bill_col = (np.array([0.50, 0.48, 0.28], dtype=np.float32) * (1.0 - bill_frac) +
                    np.array([0.18, 0.17, 0.16], dtype=np.float32) * bill_frac)
        arr = _blend(arr, bill_col, ba * 0.90)

    # ── Legs — long yellowish-grey stilts going into water ────────────────────
    for leg_ox, leg_lean in [(-0.022, 0.005), (0.022, -0.003)]:
        for frac in np.linspace(0.0, 1.0, 80):
            lx = heron_cx + leg_ox + leg_lean * frac
            ly = heron_cy + heron_ry * 0.80 + frac * 0.120
            lw = 0.010
            ld = ((xx - lx) / lw) ** 2 + ((yy - ly) / (lw * 1.5)) ** 2
            la = np.clip(1.0 - ld, 0.0, 1.0) ** 0.9
            # Above water: yellowish-grey; below: teal blend
            above = (ly < water_horizon + 0.01)
            leg_col = (np.array([0.58, 0.55, 0.42], dtype=np.float32) if above
                       else np.array([0.28, 0.38, 0.42], dtype=np.float32))
            arr = _blend(arr, leg_col, la * 0.88)

    # Raised foot — catching amber sunrise on upper surface
    paw_cx = heron_cx + 0.050
    paw_cy = heron_cy + heron_ry * 0.78
    for toe_ang, toe_len in [(-0.30, 0.035), (0.0, 0.040), (0.30, 0.035), (0.65, 0.025)]:
        for tf in np.linspace(0.0, 1.0, 40):
            tx = paw_cx + np.sin(toe_ang) * tf * toe_len
            ty = paw_cy + np.cos(toe_ang) * tf * toe_len * 0.5
            td = ((xx - tx) / 0.007) ** 2 + ((yy - ty) / 0.007) ** 2
            ta = np.clip(1.0 - td, 0.0, 1.0) ** 1.2
            # Upper surface lit by amber sunrise
            arr = _blend(arr, np.array([0.72, 0.62, 0.32], dtype=np.float32), ta * 0.80)

    arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(3.0))
    return img


def paint(output_path: str = "s210_heron.png") -> str:
    """
    Paint 'The Amber Shore' — great blue heron at coastal dawn.
    Hans Hofmann push-pull chromatic spatial tension: 121st mode.
    """
    print("=" * 64)
    print("  Session 210 — 'The Amber Shore'")
    print("  Great blue heron at coastal estuary, first light")
    print("  Technique: Hans Hofmann Push-Pull chromatic spatial tension")
    print("  121st mode: hofmann_push_pull_pass")
    print("=" * 64)

    ref_img = build_heron_reference(W, H)
    ref_arr = np.array(ref_img, dtype=np.float32) / 255.0
    print(f"  Reference built  ({W}x{H})")

    hofmann = get_style("hans_hofmann")
    p = Painter(W, H)

    # Ground: warm raw umber — Hofmann liked warm wood-panel grounds
    print("  [1] Tone ground — warm umber ...")
    p.tone_ground(hofmann.ground_color, texture_strength=0.05)

    print("  [2] Underpainting ...")
    p.underpainting(ref_img, stroke_size=30, n_strokes=2000)

    print("  [3] Block in — broad colour planes ...")
    p.block_in(ref_img, stroke_size=20, n_strokes=2400)

    print("  [4] Build form ...")
    p.build_form(ref_img, stroke_size=10, n_strokes=3000)

    print("  [5] Place lights ...")
    p.place_lights(ref_img, stroke_size=5, n_strokes=320)

    print("  [6] Meso detail ...")
    p.meso_detail_pass(opacity=0.28)

    # ── Hofmann signature pass — push-pull chromatic spatial tension ──────────
    print("  [7] hofmann_push_pull_pass (121st mode) ...")
    p.hofmann_push_pull_pass(
        push_sigma=18.0,
        push_strength=0.28,
        pull_strength=0.22,
        opacity=0.65,
    )

    # Finishing
    print("  [8] Edge definition ...")
    p.edge_definition_pass(opacity=0.26)

    # Warm glaze — sunrise amber tinting the whole surface lightly
    print("  [9] Final warm sunrise glaze ...")
    p.glaze((0.72, 0.50, 0.18), opacity=0.038)

    print("  [10] Finish (vignette + crackle off) ...")
    p.finish(vignette=0.32, crackle=False)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    out = paint()
    print(f"\n  Done: {out}")
