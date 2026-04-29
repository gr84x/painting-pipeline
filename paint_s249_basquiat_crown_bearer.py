"""
paint_s249_basquiat_crown_bearer.py -- Session 249

"The Crown Bearer" -- after Jean-Michel Basquiat

Image Description
-----------------
Subject & Composition
    A single standing young man seen frontally, slightly larger than life, his
    figure filling the portrait canvas from crown to thigh. He faces directly
    forward: confrontational and calm simultaneously, the figure of Basquiat's
    repeated crown-bearer, the anointed one. The composition is centred,
    near-symmetric, and almost hieratic -- like an icon or a playing card.
    The background is raw near-black ground with scattered bright graffiti
    fragments.

The Figure
    A young Black man in his twenties. His head is a warm brown oval, slightly
    squarer at the jaw -- schematic rather than observed, a signifier of a face
    rather than a portrait of one. Two small dark oval eyes, direct and unafraid.
    A curved darker line for the lips. His hair is a close-cropped afro, very
    dark, merging almost imperceptibly with the near-black background at the
    edges of the head. His neck is broad. His shoulders are wide. He wears a
    plain off-white t-shirt -- flat, almost the white of unprimed canvas. His
    arms hang at his sides in loose fists. The lower edge of the canvas cuts off
    at mid-thigh: the figure does not need feet, it already owns the ground.

    Emotional state: still. Certain. Not aggressive -- but not asking permission
    either.

The Crown
    Chrome yellow. Three triangular points, slightly irregular, slightly
    wobbling -- this is a hand-drawn crown, not a manufactured one. It floats
    centred above the head, a gap of dark air between its base and his hair.
    The floating says: this crown did not arrive by inheritance. It arrived and
    is permanent.

The Environment
    Near-black ground -- the dark of Lower Manhattan at 3 AM, the dark of raw
    unprimed canvas, the dark of everything that has tried to erase this figure.
    Scattered across the dark background: small red marks, yellow dots, a blue
    fragment, white sparks -- graffiti residue, evidence that this wall has been
    written on before and will be again. No ground plane, no sky, no
    architecture. Just the dark field and the figure within it.

Technique & Palette
    Jean-Michel Basquiat Neo-Expressionist Scrawl mode -- session 249, 160th
    distinct mode.

    Stage 1, PER-PIXEL CHANNEL DISCRETE POSTERIZATION (n_levels=5): Each R, G,
    B channel is independently rounded down to the nearest of 5 discrete steps
    using floor(channel * 5) / 5. The result flattens the continuous tonal
    modulation of the painted figure into discrete flat-colour zones: the chrome
    yellow crown becomes a single bright plane; the off-white shirt becomes a
    single flat zone; the warm brown flesh steps into three or four distinct flat
    tones. This is the graphic, sign-painter directness of Basquiat flat primary-
    colour zones, where colour is applied as a single unambiguous decision.

    Stage 2, RANDOM DIRECTIONAL CRUDE MARK OVERLAY (n_marks=220): 220 random
    short oriented marks are scattered across the canvas, each rasterized as a
    short line segment at a random angle and position. Dark marks (65%) and
    light marks (35%) create the energetic, frenetic mark-field that covers
    every surface in Basquiat's work -- the evidence of gesture, urgency,
    process.

    Stage 3, MIDTONE SATURATION AMPLIFICATION (sat_boost=0.45): Pixels in the
    midtone luminance window [0.22, 0.72] -- the warm flesh tones, the off-white
    shirt, the mid-value mark fragments -- are pushed further from grey, toward
    maximum chromatic presence.

    Paint Chroma Focus improvement (session 249): The focus point is placed at
    the face/crown centre (x=0.50, y=0.22). The central zone (radius=0.35 *
    min(H,W)) receives a saturation boost of 0.30; the peripheral zone receives
    a saturation reduction of 0.20. The face and crown become the most vivid
    area of the canvas; the lower torso and corners become quieter.

    Palette: Near-black (background, hair) -- Chrome yellow (crown, 0.94/0.82/0.06) --
    Cadmium red (graffiti marks, 0.90/0.16/0.10) -- Warm brown (flesh, 0.66/0.44/0.22) --
    Off-white (t-shirt, 0.90/0.88/0.82) -- Cobalt-ultramarine (bg fragment, 0.14/0.18/0.70)

Mood & Intent
    This painting tries to do what Basquiat did with his crown figures: to anoint.
    To say that this person is royalty. That this body has dignity and grace.
    That the crude marks do not diminish the figure -- they assert the terms of
    its existence.

    The directness of the gaze says: I am here. The crown says: and I have
    always been here.

    The viewer should feel the power of a direct gaze from a figure who has
    claimed his own space. The crude marks are not signs of degradation but
    signs of presence: evidence that this person was here, is here, and will
    remain here. That is what Basquiat's crown means. That is what this painting
    intends.

    Paint with patience and practice, like a true artist.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "s249_basquiat_crown_bearer.png"
)
W, H = 540, 720   # portrait format -- 3:4 proportion


def build_reference() -> np.ndarray:
    """
    Synthetic reference for "The Crown Bearer".

    Zones (y fraction from top):
      - Background:    entire canvas, near-black + scattered graffiti marks
      - Crown:         y 0.04 - 0.17, centred x 0.34-0.66, chrome yellow
      - Hair halo:     slight dark ring just outside head ellipse
      - Head:          ellipse cy=0.265, rx=0.145, ry=0.105, warm brown
      - Eyes:          small dark ovals at cy=0.255
      - Neck:          x 0.44-0.56, y 0.355-0.435
      - Torso/shirt:   x 0.26-0.74, y 0.425-0.76, off-white
      - Arms:          x 0.10-0.28 and 0.72-0.90, y 0.44-0.72, flesh
    """
    rng = np.random.default_rng(249)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys  = np.linspace(0.0, 1.0, H)[:, None]
    xs  = np.linspace(0.0, 1.0, W)[None, :]

    # ── Background: near-black with slight noise ─────────────────────────────
    bg = np.array([0.07, 0.07, 0.06])
    for ch in range(3):
        ref[:, :, ch] = bg[ch]
    bg_noise = gaussian_filter(
        rng.random((H, W)).astype(np.float32) - 0.5, sigma=4.0
    ) * 0.022
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + bg_noise, 0.0, 1.0)

    # ── Scattered graffiti marks in background ────────────────────────────────
    spot_colors = [
        np.array([0.88, 0.16, 0.10]),   # cadmium red
        np.array([0.90, 0.80, 0.12]),   # chrome yellow
        np.array([0.14, 0.18, 0.65]),   # cobalt blue
        np.array([0.90, 0.90, 0.87]),   # near-white
        np.array([0.80, 0.52, 0.12]),   # orange
    ]
    for _ in range(60):
        bx  = float(rng.uniform(0.04, 0.96))
        by  = float(rng.uniform(0.04, 0.96))
        br  = float(rng.uniform(0.003, 0.011))
        sc  = spot_colors[int(rng.integers(0, len(spot_colors)))]
        dist = np.sqrt((xs - bx) ** 2 + (ys - by) ** 2)
        spot = (dist <= br).astype(np.float32)
        for ch in range(3):
            ref[:, :, ch] = np.clip(ref[:, :, ch] + sc[ch] * spot * 0.80, 0.0, 1.0)

    # ── CROWN: three-point, chrome yellow ────────────────────────────────────
    crown_color = np.array([0.94, 0.82, 0.06])
    crown_base_yt = 0.118
    crown_base_yb = 0.168
    crown_base_xl = 0.335
    crown_base_xr = 0.665

    base_mask = (
        (ys >= crown_base_yt) & (ys <= crown_base_yb) &
        (xs >= crown_base_xl) & (xs <= crown_base_xr)
    ).astype(np.float32)

    spike_defs = [
        (0.50 - 0.145, 0.062, 0.068),   # left spike: (tip_x, tip_y, half_base_width)
        (0.50,          0.035, 0.072),   # centre spike
        (0.50 + 0.145, 0.065, 0.068),   # right spike
    ]
    crown_mask = base_mask.copy()
    for (tip_x, tip_y, hw) in spike_defs:
        frac = np.clip((ys - tip_y) / max(crown_base_yt - tip_y, 0.001), 0.0, 1.0)
        tri_xl = tip_x - hw * frac
        tri_xr = tip_x + hw * frac
        spike_mask = (
            (ys >= tip_y) & (ys <= crown_base_yt) &
            (xs >= tri_xl) & (xs <= tri_xr)
        ).astype(np.float32)
        crown_mask = np.clip(crown_mask + spike_mask, 0.0, 1.0)

    for ch in range(3):
        ref[:, :, ch] = (ref[:, :, ch] * (1.0 - crown_mask) +
                         crown_color[ch] * crown_mask)

    # ── HAIR: dark ring just outside the head ellipse ────────────────────────
    head_cx   = 0.50
    head_cy   = 0.265
    head_rx   = 0.145
    head_ry   = 0.108
    hair_rx   = head_rx + 0.028
    hair_ry   = head_ry + 0.020

    head_ell = (
        ((xs - head_cx) / head_rx) ** 2 +
        ((ys - head_cy) / head_ry) ** 2 <= 1.0
    ).astype(np.float32)

    hair_ell = (
        ((xs - head_cx) / hair_rx) ** 2 +
        ((ys - head_cy) / hair_ry) ** 2 <= 1.0
    ).astype(np.float32)

    hair_ring = hair_ell * (1.0 - head_ell)
    hair_c = np.array([0.08, 0.07, 0.05])
    for ch in range(3):
        ref[:, :, ch] = (ref[:, :, ch] * (1.0 - hair_ring) +
                         hair_c[ch] * hair_ring)

    # ── HEAD: warm brown oval ─────────────────────────────────────────────────
    flesh = np.array([0.66, 0.44, 0.22])
    for ch in range(3):
        ref[:, :, ch] = (ref[:, :, ch] * (1.0 - head_ell) +
                         flesh[ch] * head_ell)

    # Slight luminosity gradient on face (lighter forehead, darker jaw)
    face_grad = np.clip(1.0 - (ys - (head_cy - head_ry)) /
                        max(2.0 * head_ry, 0.01), 0.1, 0.5) * head_ell
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + np.array([0.04, 0.03, 0.01])[ch] * face_grad,
                                 0.0, 1.0)

    # ── EYES: small dark ovals ────────────────────────────────────────────────
    for eye_x in [head_cx - 0.052, head_cx + 0.052]:
        eye_y = head_cy - 0.012
        eye_ell = (
            ((xs - eye_x) / 0.026) ** 2 +
            ((ys - eye_y) / 0.021) ** 2 <= 1.0
        ).astype(np.float32)
        for ch in range(3):
            ref[:, :, ch] = ref[:, :, ch] * (1.0 - eye_ell) + 0.05 * eye_ell

    # ── NECK ─────────────────────────────────────────────────────────────────
    neck_xl = 0.44
    neck_xr = 0.56
    neck_yt = head_cy + head_ry - 0.010
    neck_yb = head_cy + head_ry + 0.080
    neck_mask = (
        (xs >= neck_xl) & (xs <= neck_xr) &
        (ys >= neck_yt) & (ys <= neck_yb)
    ).astype(np.float32)
    neck_c = np.array([0.60, 0.39, 0.18])
    for ch in range(3):
        ref[:, :, ch] = (ref[:, :, ch] * (1.0 - neck_mask) +
                         neck_c[ch] * neck_mask)

    # ── TORSO: off-white t-shirt ──────────────────────────────────────────────
    torso_xl = 0.24
    torso_xr = 0.76
    torso_yt = neck_yb - 0.012
    torso_yb = 0.775
    torso_mask = (
        (xs >= torso_xl) & (xs <= torso_xr) &
        (ys >= torso_yt) & (ys <= torso_yb)
    ).astype(np.float32)
    shirt_c = np.array([0.90, 0.88, 0.82])
    for ch in range(3):
        ref[:, :, ch] = (ref[:, :, ch] * (1.0 - torso_mask) +
                         shirt_c[ch] * torso_mask)

    # ── ARMS: flesh tone, flanking the torso ─────────────────────────────────
    arm_yt = torso_yt + 0.018
    arm_yb = 0.72
    for (arm_xl, arm_xr) in [(0.08, 0.26), (0.74, 0.92)]:
        arm_mask = (
            (xs >= arm_xl) & (xs <= arm_xr) &
            (ys >= arm_yt) & (ys <= arm_yb)
        ).astype(np.float32)
        for ch in range(3):
            ref[:, :, ch] = np.clip(
                ref[:, :, ch] * (1.0 - arm_mask) + flesh[ch] * arm_mask,
                0.0, 1.0
            )

    # ── LOWER BODY: dark shorts suggestion ───────────────────────────────────
    lower_xl = 0.26
    lower_xr = 0.74
    lower_yt = 0.775
    lower_yb = 1.00
    lower_mask = (
        (xs >= lower_xl) & (xs <= lower_xr) &
        (ys >= lower_yt) & (ys <= lower_yb)
    ).astype(np.float32)
    lower_c = np.array([0.14, 0.12, 0.11])  # dark, almost matching background
    for ch in range(3):
        ref[:, :, ch] = (ref[:, :, ch] * (1.0 - lower_mask * 0.7) +
                         lower_c[ch] * lower_mask * 0.7)

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'The Crown Bearer' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=249)

    # Ground: near-black -- raw, unprimed-canvas dark
    p.tone_ground((0.10, 0.09, 0.07), texture_strength=0.018)

    # Underpainting: establish the broad masses
    p.underpainting(ref_pil, stroke_size=80)

    # Block in: lay down the major colour zones -- crown, head, shirt, arms
    p.block_in(ref_pil, stroke_size=28)

    # Build form: tighten the figure contours and edge definition
    p.build_form(ref_pil, stroke_size=14)

    # Place lights: warm top light on crown and forehead
    p.place_lights(ref_pil, stroke_size=6)

    # ── BASQUIAT NEO-EXPRESSIONIST SCRAWL -- session 249, 160th distinct mode ─

    # First pass: primary posterization + full mark field + midtone boost
    p.basquiat_neo_expressionist_scrawl_pass(
        n_levels=5,
        n_marks=220,
        mark_length=18,
        mark_width=2.2,
        mark_strength=0.22,
        dark_mark_frac=0.62,
        mid_lo=0.22,
        mid_hi=0.72,
        sat_boost=0.45,
        opacity=0.84,
        seed=249,
    )

    # Second pass: lighter posterization + additional fine marks for texture
    p.basquiat_neo_expressionist_scrawl_pass(
        n_levels=8,
        n_marks=120,
        mark_length=10,
        mark_width=1.5,
        mark_strength=0.14,
        dark_mark_frac=0.70,
        mid_lo=0.28,
        mid_hi=0.68,
        sat_boost=0.20,
        opacity=0.38,
        seed=492,
    )

    # ── PAINT CHROMA FOCUS -- session 249 improvement ────────────────────────
    # Focus on face and crown zone: amplify chromatic intensity at centre
    p.paint_chroma_focus_pass(
        focus_x=0.50,
        focus_y=0.22,   # face/crown level
        focus_radius=0.35,
        center_sat_boost=0.30,
        periphery_sat_reduce=0.20,
        opacity=0.55,
    )

    # Final vignette: deepen the dark ground corners
    p.focal_vignette_pass(vignette_strength=0.32, opacity=0.48)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()