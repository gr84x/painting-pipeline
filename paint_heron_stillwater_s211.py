"""
paint_heron_stillwater_s211.py — Session 211 painting.

'The Heron at Stillwater' — Joan Miró inspired biomorphic abstraction.
A great blue heron in a Miró primary-colour marsh at dusk.

Uses miro_surrealist_biomorph_pass (122nd distinct mode).
"""

import sys
import os
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))

from stroke_engine import Painter

OUTPUT = os.path.join(os.path.dirname(__file__), "heron_stillwater_s211.png")
W, H = 900, 1100
SEED = 211

np.random.seed(SEED)


# ─────────────────────────────────────────────────────────────────────────────
# Build synthetic reference: "The Heron at Stillwater"
# ─────────────────────────────────────────────────────────────────────────────

def build_reference(w: int, h: int) -> Image.Image:
    """
    Construct a simplified reference image capturing the key compositional
    and colour zones of the heron-at-dusk scene:

      Sky (rows 0..h*0.60): gradient from deep ultramarine at top
        through cobalt to a burning cadmium-yellow/red horizon band
      Treeline silhouette (rows h*0.57..h*0.63): dark near-black
      Water/marsh (rows h*0.60..h): golden ochre reflection with
        darker cool zones and the heron silhouette
      Heron body (centred, left-of-centre): tall dark slate-grey shape
      Neck/head: S-curve silhouette with ochre bill detail
      Cattail reeds (right side): dark vertical spears
    """
    arr = np.zeros((h, w, 3), dtype=np.uint8)

    # ── Sky: ultramarine top → cobalt mid → cadmium-red band → yellow horizon ──
    sky_bottom = int(h * 0.62)
    for y in range(sky_bottom):
        t = y / sky_bottom  # 0=top, 1=horizon

        if t < 0.50:
            # Ultramarine deep blue top → cobalt blue mid
            r = int(np.interp(t, [0, 0.50], [15,  30]))
            g = int(np.interp(t, [0, 0.50], [25,  55]))
            b = int(np.interp(t, [0, 0.50], [180, 160]))
        elif t < 0.72:
            # Cobalt → muted teal (atmospheric transition)
            t2 = (t - 0.50) / 0.22
            r = int(np.interp(t2, [0, 1], [30,  90]))
            g = int(np.interp(t2, [0, 1], [55,  90]))
            b = int(np.interp(t2, [0, 1], [160, 100]))
        elif t < 0.88:
            # Teal → cadmium red-orange glow at horizon
            t2 = (t - 0.72) / 0.16
            r = int(np.interp(t2, [0, 1], [90,  225]))
            g = int(np.interp(t2, [0, 1], [90,   55]))
            b = int(np.interp(t2, [0, 1], [100,  20]))
        else:
            # Cadmium red → cadmium yellow at the very horizon
            t2 = (t - 0.88) / 0.12
            r = int(np.interp(t2, [0, 1], [225, 250]))
            g = int(np.interp(t2, [0, 1], [55,  210]))
            b = int(np.interp(t2, [0, 1], [20,   10]))

        arr[y, :] = [r, g, b]

    # ── Treeline silhouette ────────────────────────────────────────────────────
    tree_top   = int(h * 0.575)
    tree_bot   = int(h * 0.625)
    # Irregular silhouette using a simple noise profile
    rng = np.random.default_rng(42)
    tree_heights = np.zeros(w, dtype=int)
    base = int(h * 0.595)
    for x in range(w):
        noise_val = int(rng.integers(0, int(h * 0.025)))
        tree_heights[x] = base - noise_val
    for x in range(w):
        top_y = tree_heights[x]
        arr[top_y:tree_bot, x] = [12, 14, 18]  # near-black treeline

    # ── Water / marsh: golden reflection ──────────────────────────────────────
    water_top = int(h * 0.615)
    for y in range(water_top, h):
        t = (y - water_top) / (h - water_top)
        # Golden ochre reflection at water surface → darker warm mid
        r = int(np.interp(t, [0, 0.3, 1.0], [190, 160, 120]))
        g = int(np.interp(t, [0, 0.3, 1.0], [140, 110,  80]))
        b = int(np.interp(t, [0, 0.3, 1.0], [ 35,  30,  25]))
        arr[y, :] = [r, g, b]

    # Reflection stripe of the red horizon band in water
    stripe_top = int(h * 0.62)
    stripe_bot = int(h * 0.68)
    for y in range(stripe_top, stripe_bot):
        arr[y, :, 0] = np.minimum(arr[y, :, 0].astype(int) + 55, 255).astype(np.uint8)
        arr[y, :, 1] = np.maximum(arr[y, :, 1].astype(int) - 20, 0).astype(np.uint8)

    # ── Heron body silhouette ──────────────────────────────────────────────────
    # Standing left-of-centre, body from ~38% to ~72% of width, 28% to 68% height
    heron_cx = int(w * 0.36)
    heron_body_top    = int(h * 0.28)
    heron_body_bottom = int(h * 0.68)
    body_w = int(w * 0.06)
    body_h = heron_body_bottom - heron_body_top

    img_pil = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(img_pil)

    # Body: ellipse-ish dark blue-grey
    body_color = (75, 85, 100)
    draw.ellipse([
        heron_cx - body_w,
        heron_body_top + int(body_h * 0.10),
        heron_cx + body_w,
        heron_body_bottom
    ], fill=body_color)

    # Neck: S-curve approximated as two connected rectangles
    neck_w = int(w * 0.018)
    neck_top_x = heron_cx - int(w * 0.015)
    # Upper neck segment (curves backward then forward)
    neck_seg1_top    = int(h * 0.20)
    neck_seg1_bottom = int(h * 0.36)
    draw.rectangle([
        neck_top_x - neck_w, neck_seg1_top,
        neck_top_x + neck_w, neck_seg1_bottom
    ], fill=(80, 90, 108))
    # Lower neck tilted forward
    neck_seg2_top    = int(h * 0.33)
    neck_seg2_bottom = int(h * 0.46)
    neck_bottom_x = heron_cx + int(w * 0.005)
    draw.rectangle([
        neck_bottom_x - neck_w, neck_seg2_top,
        neck_bottom_x + neck_w, neck_seg2_bottom
    ], fill=(78, 88, 106))

    # Head: small oval
    head_cx = heron_cx - int(w * 0.022)
    head_cy = int(h * 0.21)
    head_rx = int(w * 0.022)
    head_ry = int(h * 0.018)
    draw.ellipse([
        head_cx - head_rx, head_cy - head_ry,
        head_cx + head_rx, head_cy + head_ry
    ], fill=(72, 80, 98))

    # Bill: long dagger pointing down-left (dark ochre/yellow)
    bill_start_x = head_cx - head_rx
    bill_start_y = head_cy + int(head_ry * 0.3)
    bill_end_x   = head_cx - head_rx - int(w * 0.07)
    bill_end_y   = head_cy + int(h * 0.06)
    draw.line([
        (bill_start_x, bill_start_y),
        (bill_end_x, bill_end_y)
    ], fill=(190, 148, 40), width=max(2, int(w * 0.006)))

    # Eye: small golden dot
    eye_x = head_cx - int(head_rx * 0.3)
    eye_y = head_cy - int(head_ry * 0.1)
    eye_r = max(2, int(w * 0.007))
    draw.ellipse([eye_x - eye_r, eye_y - eye_r, eye_x + eye_r, eye_y + eye_r],
                 fill=(210, 175, 30))

    # Legs: two thin dark lines from body bottom to water surface
    leg_top_y  = heron_body_bottom - int(h * 0.02)
    leg_bot_y  = int(h * 0.74)
    leg1_x = heron_cx - int(w * 0.015)
    leg2_x = heron_cx + int(w * 0.015)
    leg_color = (55, 65, 78)
    draw.line([(leg1_x, leg_top_y), (leg1_x - int(w * 0.008), leg_bot_y)],
              fill=leg_color, width=max(2, int(w * 0.004)))
    draw.line([(leg2_x, leg_top_y), (leg2_x + int(w * 0.008), leg_bot_y)],
              fill=leg_color, width=max(2, int(w * 0.004)))

    # Wing plumes: slightly lighter wispy hint at left body edge
    draw.arc([
        heron_cx - body_w - int(w * 0.04),
        heron_body_top + int(body_h * 0.35),
        heron_cx + int(w * 0.01),
        heron_body_bottom + int(h * 0.02)
    ], start=200, end=260, fill=(110, 120, 138), width=max(2, int(w * 0.005)))

    # ── Cattail reeds (right side) ────────────────────────────────────────────
    reed_positions = [
        int(w * 0.68), int(w * 0.72), int(w * 0.75),
        int(w * 0.80), int(w * 0.85), int(w * 0.88),
        int(w * 0.92), int(w * 0.95),
    ]
    reed_heights = [
        int(h * 0.22), int(h * 0.18), int(h * 0.25),
        int(h * 0.20), int(h * 0.15), int(h * 0.28),
        int(h * 0.17), int(h * 0.23),
    ]
    reed_color = (18, 20, 25)
    for rx, rt in zip(reed_positions, reed_heights):
        reed_bottom = int(h * 0.80) + rng.integers(-20, 20).item()
        reed_x_wobble = rx + rng.integers(-4, 4).item()
        draw.line([(reed_x_wobble, rt), (rx, reed_bottom)],
                  fill=reed_color, width=max(2, int(w * 0.003)))
        # Cattail seed head
        draw.ellipse([rx - int(w * 0.008), rt - int(h * 0.025),
                      rx + int(w * 0.008), rt + int(h * 0.005)],
                     fill=(45, 30, 20))

    # ── A few biomorphic cloud shapes (Miró-style blobs in the sky) ────────────
    cloud_shapes = [
        (int(w * 0.15), int(h * 0.08), int(w * 0.09), int(h * 0.035)),
        (int(w * 0.60), int(h * 0.05), int(w * 0.12), int(h * 0.030)),
        (int(w * 0.82), int(h * 0.12), int(w * 0.07), int(h * 0.025)),
        (int(w * 0.42), int(h * 0.14), int(w * 0.08), int(h * 0.020)),
    ]
    cloud_color = (180, 100, 20)  # warm copper-orange clouds
    for cx, cy, crx, cry in cloud_shapes:
        draw.ellipse([cx - crx, cy - cry, cx + crx, cy + cry],
                     fill=cloud_color)

    # ── Heron's reflection in water (simplified inverted blob) ────────────────
    refl_top = int(h * 0.72)
    refl_bot = int(h * 0.82)
    draw.ellipse([
        heron_cx - body_w - int(w * 0.01),
        refl_top,
        heron_cx + body_w + int(w * 0.01),
        refl_bot
    ], fill=(55, 60, 72))

    arr = np.array(img_pil, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


# ─────────────────────────────────────────────────────────────────────────────
# Main painting pipeline
# ─────────────────────────────────────────────────────────────────────────────

def paint():
    print("Session 211 — The Heron at Stillwater")
    print("Artist inspiration: Joan Miró (Surrealism / Abstract Art)")
    print("Pass: miro_surrealist_biomorph_pass (122nd distinct mode)")
    print()

    print("  Building reference image ...")
    ref = build_reference(W, H)

    print("  Initialising painter ...")
    p = Painter(W, H, seed=SEED)

    print("  tone_ground() — warm raw canvas ...")
    p.tone_ground(color=(0.94, 0.92, 0.85))

    print("  underpainting() — broad mass strokes ...")
    p.underpainting(ref, stroke_size=22, n_strokes=900)

    print("  block_in() — major colour zones ...")
    p.block_in(ref, stroke_size=15, n_strokes=700)

    print("  build_form() — simplified structural strokes ...")
    p.build_form(ref, stroke_size=7, n_strokes=500)

    print("  miro_surrealist_biomorph_pass() — 122nd distinct mode ...")
    p.miro_surrealist_biomorph_pass(
        flat_strength=0.72,
        outline_strength=0.88,
        edge_sigma=1.5,
        opacity=0.80,
    )

    print(f"  Writing {OUTPUT} ...")
    p.canvas.surface.write_to_png(OUTPUT)
    print(f"  Done. → {OUTPUT}")


if __name__ == "__main__":
    paint()
