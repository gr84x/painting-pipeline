"""
paint_s251_bacon_bull.py -- Session 251

"Bull at Rest" -- after Francis Bacon

Image Description
-----------------
Subject & Composition
    A bull viewed from below and to the left -- nearly head-on -- standing
    in absolute stillness at the centre of the canvas. The animal fills
    two-thirds of the canvas height. Its massive head is lowered, the broad
    muzzle pressing slightly forward as if scenting the air. The horns sweep
    outward at the same level as the top of the frame. The composition is
    axially symmetrical with a slight lean to the animal left shoulder.

The Figure
    The bull hide is a deep warm umber-ochre with thick flesh tones -- not
    a naturalistic hide, but the memory of a hide, smeared and pulled. The
    musculature of the neck and shoulder is rendered in directional strokes
    running upper-left to lower-right, as if the painter had dragged a rag
    across the half-wet paint. The eye -- just one visible, at the left edge
    -- is a single dark globe with the quality of absolute impassivity.
    Emotional state: contained power, absolute patience, the vacancy of
    pure physical existence. The body is both specific and generic -- Bacon
    intended flesh, not illustration.

The Environment
    Raw cadmium orange flat field surrounds the figure, entirely flat and
    unarticulated -- no horizon, no room, no floor, no shadow -- just the
    intense ground pushing the figure outward into visibility. A faint
    elliptical boundary separates figure from ground, barely visible as a
    slight darkening at the edge of the flesh zone. The background is
    uniform and presses forward.

Technique & Palette
    Francis Bacon Isolated Figure mode -- session 251, 162nd distinct mode.

    Stage 1, ELLIPTICAL ISOLATION VIGNETTE: Ellipse (rx=0.36, ry=0.45)
    concentrates visual energy on the figure. Exterior darkened by
    exterior_strength=0.65 toward near-black, with a smooth cosine
    transition band of width=0.09. Separates the figure from the flat
    orange void with the spatial precision Bacon called an armature.

    Stage 2, DIRECTIONAL LINEAR SMEAR: smear_angle=42 degrees (upper-left
    to lower-right, along the shoulder slope), smear_length=16 pixels.
    Smear weight sw weighted by mid_luminance=0.46, smear_bandwidth=0.30:
    strongest in warm flesh mid-tones, weakest at highlights and near-
    blacks. The smeared pixels record the directional rag-scrub of Bacon
    working across wet paint in the hide passages. smear_opacity=0.72.

    Stage 3, FLAT BACKGROUND TONE FIELD: flat_hue=0.08 (cadmium orange),
    flat_sat=0.80, exterior_blend=0.70. Converts the exterior zone to a
    unified cadmium orange field -- the raw ground Bacon rolled on with
    a house-painter brush to achieve absolute colour uniformity.

    Paint Warm-Cool Separation improvement (session 251): warm_boost=0.26
    lifts the warm ochre and sienna passages; cool_boost=0.22 deepens the
    cool grey shadows in the hide. warm_lum_shift=0.03 follows Delacroix
    perceptual rule (warm=lighter), cool_lum_shift=0.025 (cool=heavier).

    Palette: Warm ochre-umber (0.84/0.44/0.18) -- Raw sienna (0.62/0.28/0.08)
    -- Deep burnt umber (0.28/0.14/0.06) -- Cadmium orange ground
    (0.88/0.42/0.10) -- Near-black (0.08/0.06/0.04) -- Pale highlight
    (0.90/0.86/0.72) -- Cool grey (0.48/0.46/0.52)

Mood & Intent
    The image intends the quality Bacon called "the brutality of fact" --
    not a symbolic bull, not a metaphorical bull, but the specific weight
    and presence of flesh. The viewer should feel something about the animal
    not as creature but as matter: the sensation of confronting a mass of
    living tissue with no mediation of sentiment or narrative.
"""

import sys
import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stroke_engine import Painter

W, H = 900, 1100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s251_bacon_bull.png")


def build_reference(w=W, h=H):
    """Build a reference image: bull silhouette in warm flesh tones on orange ground."""
    rng = random.Random(251)
    arr = np.zeros((h, w, 3), dtype=np.uint8)

    # ── Background: flat cadmium orange ──────────────────────────────────────
    arr[:] = [26, 107, 224]   # BGR for cadmium orange (0.88, 0.42, 0.10 in RGB)

    cx = w * 0.50
    cy = h * 0.52
    # Bull body dimensions
    body_rx = w * 0.28
    body_ry = h * 0.26
    neck_cx = cx - w * 0.02
    neck_cy = cy - h * 0.18
    neck_rx = w * 0.14
    neck_ry = h * 0.20
    head_cx = cx - w * 0.02
    head_cy = cy - h * 0.32
    head_rx = w * 0.16
    head_ry = h * 0.14

    def in_ellipse(x, y, ex, ey, er, ec):
        return ((x - ex) / er) ** 2 + ((y - ey) / ec) ** 2 <= 1.0

    # Draw body zones with warm umber tones
    for y in range(h):
        for x in range(w):
            in_body = in_ellipse(x, y, cx, cy, body_rx, body_ry)
            in_neck = in_ellipse(x, y, neck_cx, neck_cy, neck_rx, neck_ry)
            in_head = in_ellipse(x, y, head_cx, head_cy, head_rx, head_ry)
            if in_body or in_neck or in_head:
                # Warm umber with luminance variation by position
                base_r = 0.84 + rng.gauss(0, 0.04)
                base_g = 0.44 + rng.gauss(0, 0.04)
                base_b = 0.18 + rng.gauss(0, 0.03)
                # Darken toward the edges and bottom
                dist_cx = abs(x - cx) / body_rx
                dist_cy = abs(y - cy) / body_ry
                edge_d = (dist_cx ** 2 + dist_cy ** 2) ** 0.5
                darken = max(0.0, edge_d - 0.5) * 0.3
                base_r = max(0.10, base_r - darken)
                base_g = max(0.06, base_g - darken * 0.8)
                base_b = max(0.04, base_b - darken * 0.5)
                # Cool shadow on left flank
                if x < cx - body_rx * 0.4:
                    cool_shift = (cx - body_rx * 0.4 - x) / (body_rx * 0.4) * 0.22
                    base_r = max(0.10, base_r - cool_shift)
                    base_g = max(0.06, base_g - cool_shift * 0.5)
                    base_b = min(0.60, base_b + cool_shift * 0.3)
                arr[y, x] = [
                    int(np.clip(base_b * 255, 0, 255)),
                    int(np.clip(base_g * 255, 0, 255)),
                    int(np.clip(base_r * 255, 0, 255)),
                ]

    # Convert BGR array to RGB PIL image
    img = Image.fromarray(arr[:, :, ::-1], "RGB")

    # Add horn lines with ImageDraw
    draw = ImageDraw.Draw(img)
    horn_w = int(w * 0.008)
    # Left horn
    draw.line(
        [(int(head_cx - head_rx * 0.7), int(head_cy - head_ry * 0.7)),
         (int(head_cx - head_rx * 1.6), int(head_cy - head_ry * 1.8))],
        fill=(65, 45, 25), width=horn_w
    )
    # Right horn
    draw.line(
        [(int(head_cx + head_rx * 0.7), int(head_cy - head_ry * 0.7)),
         (int(head_cx + head_rx * 1.6), int(head_cy - head_ry * 1.8))],
        fill=(65, 45, 25), width=horn_w
    )
    # Eye
    eye_x = int(head_cx - head_rx * 0.42)
    eye_y = int(head_cy - head_ry * 0.1)
    eye_r = int(w * 0.018)
    draw.ellipse(
        [eye_x - eye_r, eye_y - eye_r, eye_x + eye_r, eye_y + eye_r],
        fill=(10, 8, 6)
    )
    # Eye highlight
    draw.ellipse(
        [eye_x + eye_r//3, eye_y - eye_r//2,
         eye_x + eye_r//3 + eye_r//3, eye_y - eye_r//2 + eye_r//3],
        fill=(220, 215, 200)
    )

    return img


def main():
    rng = random.Random(251)

    print("Building reference image...")
    ref = build_reference(W, H)

    print(f"Creating painter ({W}x{H})...")
    p = Painter(W, H)

    print("Tone ground (warm linen)...")
    p.tone_ground((0.88, 0.82, 0.68), texture_strength=0.04)

    print("Underpainting (broad ground wash)...")
    p.underpainting(ref, stroke_size=55, n_strokes=80)

    print("Block in (mass construction)...")
    p.block_in(ref, stroke_size=28, n_strokes=220)

    print("Build form...")
    p.build_form(ref, stroke_size=12, n_strokes=160)

    print("Place lights...")
    p.place_lights(ref, stroke_size=6, n_strokes=80)

    print("bacon_isolated_figure_pass (162nd mode)...")
    p.bacon_isolated_figure_pass(
        focal_x=0.50,
        focal_y=0.52,
        rx=0.36,
        ry=0.45,
        transition_width=0.09,
        exterior_strength=0.65,
        smear_angle=42.0,
        smear_length=16,
        mid_luminance=0.46,
        smear_bandwidth=0.30,
        smear_opacity=0.72,
        flat_hue=0.08,
        flat_sat=0.80,
        exterior_blend=0.70,
        opacity=0.90,
    )

    print("paint_warm_cool_separation_pass (improvement)...")
    p.paint_warm_cool_separation_pass(
        warm_boost=0.26,
        cool_boost=0.22,
        warm_lum_shift=0.03,
        cool_lum_shift=0.025,
        opacity=0.52,
    )

    print("Glazing (warm amber unification)...")
    p.glaze((0.72, 0.52, 0.22), opacity=0.06)

    print(f"Saving to {OUT}...")
    p.save(OUT)
    print("Done.")


if __name__ == "__main__":
    main()