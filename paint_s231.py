"""
paint_s231.py -- Session 231 painting: "The Demon at the Edge of the World"

Mikhail Vrubel inspired Symbolist composition.
Vrubel Crystal Facet mode (142nd distinct mode).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageFilter
import numpy as np

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "s231_vrubel_demon_edge.png")

W, H = 800, 1000


def build_reference_image() -> Image.Image:
    """Build a synthetic reference approximating the scene composition."""
    img = Image.new("RGB", (W, H), (15, 12, 35))
    draw = ImageDraw.Draw(img)

    # Deep violet-indigo sky background (upper 60%)
    for y in range(int(H * 0.60)):
        t = y / (H * 0.60)
        r = int(12 + t * 20)
        g = int(10 + t * 15)
        b = int(35 + t * 55)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Rocky precipice — dark masses in lower 50%
    rock_points = [
        (0, int(H * 0.55)), (int(W * 0.18), int(H * 0.48)),
        (int(W * 0.35), int(H * 0.52)), (int(W * 0.50), int(H * 0.44)),
        (int(W * 0.65), int(H * 0.50)), (int(W * 0.82), int(H * 0.46)),
        (W, int(H * 0.53)), (W, H), (0, H)
    ]
    draw.polygon(rock_points, fill=(22, 18, 40))

    # Rock face details — lighter faceted planes
    draw.polygon([
        (int(W*0.12), int(H*0.58)), (int(W*0.28), int(H*0.52)),
        (int(W*0.35), int(H*0.62)), (int(W*0.20), int(H*0.72))
    ], fill=(42, 35, 68))

    draw.polygon([
        (int(W*0.55), int(H*0.54)), (int(W*0.72), int(H*0.50)),
        (int(W*0.78), int(H*0.60)), (int(W*0.62), int(H*0.68))
    ], fill=(38, 30, 60))

    # Sunset glow on horizon — distant mauve-gold band
    for y in range(int(H * 0.38), int(H * 0.52)):
        t = 1.0 - abs(y - int(H * 0.45)) / (H * 0.07)
        t = max(0.0, t)
        r = int(140 * t + 12 * (1-t))
        g = int(90 * t + 10 * (1-t))
        b = int(160 * t + 50 * (1-t))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Demon figure — seated, central, large
    # Body: deep violet-blue torso
    draw.ellipse([
        int(W*0.28), int(H*0.12),
        int(W*0.72), int(H*0.72)
    ], fill=(28, 22, 68))

    # Wings spread wide — dark angular shapes
    # Left wing
    wing_left = [
        (int(W*0.28), int(H*0.25)),
        (int(W*0.02), int(H*0.08)),
        (int(W*0.05), int(H*0.32)),
        (int(W*0.15), int(H*0.55)),
        (int(W*0.32), int(H*0.48)),
    ]
    draw.polygon(wing_left, fill=(18, 15, 48))

    # Right wing
    wing_right = [
        (int(W*0.72), int(H*0.25)),
        (int(W*0.98), int(H*0.08)),
        (int(W*0.95), int(H*0.32)),
        (int(W*0.85), int(H*0.55)),
        (int(W*0.68), int(H*0.48)),
    ]
    draw.polygon(wing_right, fill=(18, 15, 48))

    # Wing iridescent highlights (malachite-green edge highlights)
    draw.line([
        (int(W*0.28), int(H*0.25)),
        (int(W*0.02), int(H*0.08)),
    ], fill=(45, 95, 75), width=3)
    draw.line([
        (int(W*0.72), int(H*0.25)),
        (int(W*0.98), int(H*0.08)),
    ], fill=(45, 95, 75), width=3)

    # Torso faceted planes — violet and gold
    draw.polygon([
        (int(W*0.38), int(H*0.28)), (int(W*0.50), int(H*0.22)),
        (int(W*0.56), int(H*0.38)), (int(W*0.44), int(H*0.45)),
    ], fill=(75, 58, 135))  # violet mid-tone torso

    draw.polygon([
        (int(W*0.44), int(H*0.28)), (int(W*0.58), int(H*0.24)),
        (int(W*0.60), int(H*0.36)), (int(W*0.50), int(H*0.40)),
    ], fill=(95, 78, 155))  # lighter torso facet

    # Head — upper centre
    draw.ellipse([
        int(W*0.38), int(H*0.04),
        int(W*0.62), int(H*0.26)
    ], fill=(60, 48, 105))

    # Face — pale warm highlight
    draw.ellipse([
        int(W*0.42), int(H*0.06),
        int(W*0.58), int(H*0.22)
    ], fill=(148, 115, 88))

    # Eyes — luminous gold
    draw.ellipse([int(W*0.45), int(H*0.10), int(W*0.49), int(H*0.14)], fill=(200, 165, 50))
    draw.ellipse([int(W*0.51), int(H*0.10), int(W*0.55), int(H*0.14)], fill=(200, 165, 50))
    draw.ellipse([int(W*0.46), int(H*0.11), int(W*0.48), int(H*0.13)], fill=(10, 8, 20))
    draw.ellipse([int(W*0.52), int(H*0.11), int(W*0.54), int(H*0.13)], fill=(10, 8, 20))

    # Gold crown / halo — fragmented jewel accents
    for angle_deg in range(0, 360, 22):
        import math
        angle = math.radians(angle_deg)
        cx, cy = int(W*0.50), int(H*0.13)
        rx, ry = int(W*0.14), int(H*0.11)
        x = int(cx + rx * math.cos(angle))
        y = int(cy + ry * math.sin(angle))
        draw.ellipse([x-4, y-4, x+4, y+4], fill=(185, 148, 40))

    # Arms/hands reaching downward and outward
    # Left arm
    draw.polygon([
        (int(W*0.32), int(H*0.45)),
        (int(W*0.22), int(H*0.55)),
        (int(W*0.18), int(H*0.68)),
        (int(W*0.28), int(H*0.72)),
        (int(W*0.36), int(H*0.60)),
    ], fill=(55, 42, 90))

    # Right arm
    draw.polygon([
        (int(W*0.68), int(H*0.45)),
        (int(W*0.78), int(H*0.55)),
        (int(W*0.82), int(H*0.68)),
        (int(W*0.72), int(H*0.72)),
        (int(W*0.64), int(H*0.60)),
    ], fill=(55, 42, 90))

    # Hands — pale warm tones
    draw.ellipse([int(W*0.15), int(H*0.64), int(W*0.22), int(H*0.72)], fill=(120, 95, 72))
    draw.ellipse([int(W*0.78), int(H*0.64), int(W*0.85), int(H*0.72)], fill=(120, 95, 72))

    # Flowing robes at base — violet-purple cascade
    draw.polygon([
        (int(W*0.28), int(H*0.58)), (int(W*0.72), int(H*0.58)),
        (int(W*0.82), int(H*0.80)), (int(W*0.68), int(H*0.92)),
        (int(W*0.50), int(H*0.88)), (int(W*0.32), int(H*0.92)),
        (int(W*0.18), int(H*0.80)),
    ], fill=(45, 35, 82))

    # Robe fold highlights
    for i, x in enumerate([int(W*0.35), int(W*0.50), int(W*0.65)]):
        alpha = 55 + i * 15
        draw.line([
            (x, int(H*0.60)), (x - 20 + i*10, int(H*0.90))
        ], fill=(70 + alpha, 55 + alpha, 115 + alpha), width=2)

    # Scattered jewel-point flowers / lilac blossoms at base
    for px, py in [(int(W*0.12), int(H*0.85)), (int(W*0.22), int(H*0.92)),
                   (int(W*0.75), int(H*0.87)), (int(W*0.88), int(H*0.91)),
                   (int(W*0.50), int(H*0.95)), (int(W*0.38), int(H*0.93))]:
        draw.ellipse([px-6, py-6, px+6, py+6], fill=(140, 95, 160))
        draw.ellipse([px-2, py-2, px+2, py+2], fill=(185, 140, 210))

    # Apply slight blur to blend
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))

    return img


def main():
    print("Session 231 — Mikhail Vrubel: Crystal Facet (142nd mode)")
    print(f"Output: {OUTPUT_PATH}")

    try:
        from stroke_engine import Painter

        print("Building reference image...")
        ref = build_reference_image()

        print("Creating painter...")
        p = Painter(W, H)

        print("Painting sequence:")
        print("  tone_ground (deep violet-indigo imprimatura)...")
        p.tone_ground((0.20, 0.18, 0.38), texture_strength=0.06)

        print("  underpainting...")
        p.underpainting(ref, stroke_size=52, n_strokes=150)

        print("  block_in x2...")
        p.block_in(ref, stroke_size=36, n_strokes=300)
        p.block_in(ref, stroke_size=22, n_strokes=200)

        print("  build_form x2...")
        p.build_form(ref, stroke_size=14, n_strokes=500)
        p.build_form(ref, stroke_size=10, n_strokes=400)

        print("  place_lights...")
        p.place_lights(ref, stroke_size=6, n_strokes=400)

        print("  vrubel_crystal_facet_pass (142nd mode)...")
        p.vrubel_crystal_facet_pass(
            facet_sigma=4.5,
            edge_thresh=0.16,
            grout_depth=0.50,
            jewel_boost=0.35,
            opacity=0.85,
        )

        print("  midtone_clarity_pass (s231 improvement)...")
        p.midtone_clarity_pass(
            clarity_center=0.48,
            clarity_width=0.24,
            sharpness=0.60,
            blur_sigma=1.5,
            opacity=0.70,
        )

        print("  impasto_relief_pass...")
        p.impasto_relief_pass(
            light_angle=2.20,
            relief_scale=0.08,
            thickness_gate=0.28,
            opacity=0.45,
        )

        print("  glaze (cool violet-blue)...")
        p.glaze((0.55, 0.50, 0.70), opacity=0.20)

        print("  vignette...")
        p.vignette(strength=0.35)

        print(f"Saving to {OUTPUT_PATH}...")
        p.canvas.save(OUTPUT_PATH)
        print("Done.")

    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
        print("\nFalling back to PIL-only output...")
        ref = build_reference_image()
        ref.save(OUTPUT_PATH)
        print(f"Saved reference image as fallback: {OUTPUT_PATH}")

    return OUTPUT_PATH


if __name__ == "__main__":
    out = main()
    print(f"\nOutput file: {out}")
    if os.path.exists(out):
        size = os.path.getsize(out)
        print(f"File size: {size:,} bytes")
    else:
        print("ERROR: Output file not created!")
