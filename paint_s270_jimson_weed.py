"""
paint_s270_jimson_weed.py -- Session 270

"White Jimson Weed, Desert Night" -- in the manner of Georgia O'Keeffe
(American Modernist Organic Abstraction)

Image Description
-----------------
Subject & Composition
    A single large jimson weed (Datura wrightii) flower viewed from slightly
    below and in front, the enormous white trumpet blossom filling the portrait
    canvas (1040 × 1440). The flower is centred and monumental -- five fused
    petals form a deep funnel that opens toward the viewer, the interior of the
    tube dropping into deep crimson shadow at the base, the outer petals curling
    and spreading into near-white luminosity at the tips. The composition
    references O'Keeffe's "Jimson Weed/White Flower No. 1" (1932) -- the largest
    flower painting ever sold at auction -- in which a single datura bloom is
    enlarged to canvas scale, stripped of all botanical illustration, and made
    purely architectural: the curve of one petal is as grand as the face of a
    cliff, the shadow at the throat as deep as a canyon. No stem, no leaf, no
    context beyond the flower itself and the deep indigo sky behind it.

The Subject
    The flower occupies approximately 80% of the canvas area. Five petals
    radiate from a central trumpet throat: the petals are pure white in the
    highlights, shading through warm peach and salmon in the mid-tones, then
    through deep rose and crimson as they curve into the throat shadow. Each
    petal has a distinct midrib crease -- the fold at the centre of each section
    of the corolla -- visible as a faint luminous ridge in the near-white outer
    zone and as a slightly warmer tone in the peach mid-zone. The emotional state
    of the subject is NOCTURNAL RADIANCE: the flower blooms at night, its white
    petals acting as a reflector and light-emitter in the darkness. The datura
    is toxic, beautiful, and night-blooming -- a quality of both serenity and
    strangeness.

The Environment
    Background: deep indigo-blue-violet night sky (0.10/0.12/0.30), occupying
    the corners and upper edge of the canvas where the petals don't reach.
    The sky is not uniform -- it is slightly lighter at the upper centre
    (a hint of moonlight) and deeper and cooler at the corners. There are no
    stars, no moon disc, no visible sources -- only the felt quality of full-
    dark desert night. The transition from flower edge to sky is sharp and
    clean, as in all O'Keeffe paintings -- no soft halo, no blurred edge. The
    foreground below the flower throat: a dark warm tone where the stem would
    be, present only as a warm umber depth in the very lowest portion of canvas.

Technique & Palette
    Georgia O'Keeffe Organic Abstraction mode -- session 270, 181st distinct mode.

    Pipeline:
    1. Procedural reference: near-white petal masses with indigo sky background,
       salmon-to-crimson throat, petal structure defined by radial gradients.
    2. tone_ground: warm cream (0.94, 0.90, 0.84) -- O'Keeffe's pale ground
       shows through petal translucency.
    3. underpainting x2: establish large tonal masses -- white blossom vs
       deep indigo sky, crimson throat depth.
    4. block_in x2 (broad and medium): petal planes, sky corners, throat.
    5. build_form x2 (medium and fine): petal curvature, midrib crease, form
       turning zones from white to salmon to crimson.
    6. place_lights: outer petal highlights, moonlit petal edges.
    7. paint_translucency_bloom_pass (s270 improvement): transmitted-light warm
       glow in thin petal interior zones; edge halo at petal boundaries.
    8. okeeffe_organic_form_pass (270, 181st mode): smooth interior modeling,
       form-turning saturation lift, crisp edge sharpening between petal and sky.
    9. paint_lost_found_edges_pass: soften the few soft petal-to-petal transitions
       (inner petals) while keeping the flower-to-sky edge hard.
    10. paint_granulation_pass: fine pigment granulation in the throat shadow.

    Full palette:
    near-white (0.98/0.96/0.92) -- pale-peach (0.94/0.78/0.68) --
    deep-salmon (0.88/0.56/0.42) -- crimson (0.72/0.30/0.28) --
    indigo-night (0.10/0.12/0.30) -- sage (0.28/0.44/0.30) --
    warm-sand (0.72/0.60/0.40) -- soft-violet (0.52/0.46/0.72) --
    golden (0.90/0.82/0.58)

Mood & Intent
    The image intends NOCTURNAL RADIANCE and MONUMENTAL QUIETUDE. The viewer
    is confronted with the flower as architecture -- a structure as large and
    ordered as any built thing, but made of living tissue and open only in
    darkness. The white of the petals is not innocent or gentle; it is the white
    of something that glows in the dark by internal necessity. The deep indigo
    sky presses against the petals; the flower holds. The emotion is a kind of
    reverent strangeness -- the datura does not bloom for human eyes, and
    observing it at this scale, this close, feels like a trespass.
"""

import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

from stroke_engine import Painter

# ── Canvas dimensions ────────────────────────────────────────────────────────
W, H = 1040, 1440
SEED = 270
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s270_jimson_weed.png")


def build_reference(w: int, h: int) -> np.ndarray:
    """Build a procedural reference for the jimson weed close-up.

    Returns uint8 (H, W, 3) suitable for passing directly to Painter methods.
    The reference establishes:
      - Deep indigo-violet night sky in the background corners
      - Five petal masses radiating from a central throat
      - Near-white outer petals shading through peach/salmon to crimson throat
      - Soft petal midrib ridges as warm light lines on each petal
    """
    from scipy.ndimage import gaussian_filter

    arr = np.zeros((h, w, 3), dtype=np.float32)

    # ── Background: deep indigo night sky ────────────────────────────────────
    # Start with full indigo fill
    arr[:, :, 0] = 0.10   # R
    arr[:, :, 1] = 0.12   # G
    arr[:, :, 2] = 0.30   # B

    # Slight moonlit brightening at upper centre
    cy_sky = int(h * 0.05)
    cx_sky = w // 2
    for y in range(h):
        for x in range(w):
            d = np.sqrt((y - cy_sky) ** 2 + (x - cx_sky) ** 2)
            sky_lift = np.exp(-d ** 2 / (2 * (w * 0.35) ** 2)) * 0.06
            arr[y, x, 0] += sky_lift * 0.80
            arr[y, x, 1] += sky_lift * 0.82
            arr[y, x, 2] += sky_lift * 1.00

    # ── Flower petal mask using five-petal radial gradient ───────────────────
    # Centre of the flower: upper-centre of canvas, slightly below midpoint
    cx = w // 2
    cy = int(h * 0.46)

    # Throat radius and outer petal radius
    throat_r = int(min(w, h) * 0.10)
    petal_r  = int(min(w, h) * 0.52)

    # Generate five petal shapes using radial sinusoidal mask
    # Each petal is a lobe of a 5-fold symmetry, elongated toward petal tip
    petal_count = 5
    petal_angle_offset = np.pi / 2  # first petal points upward

    petal_mask   = np.zeros((h, w), dtype=np.float32)
    petal_depth  = np.zeros((h, w), dtype=np.float32)   # 0=outer tip, 1=throat
    petal_crease = np.zeros((h, w), dtype=np.float32)   # midrib crease indicator

    for y in range(h):
        for x in range(w):
            dx = x - cx
            dy = y - cy
            r  = np.sqrt(dx * dx + dy * dy)
            theta = np.arctan2(dy, dx)

            # Five-petal boundary: radial extent varies with angle
            # Each petal is centred on one of 5 angles
            petal_angles = [petal_angle_offset + (i * 2 * np.pi / petal_count)
                            for i in range(petal_count)]

            # Find closest petal angle
            diffs = [(theta - pa + np.pi) % (2 * np.pi) - np.pi
                     for pa in petal_angles]
            min_diff = min(abs(d) for d in diffs)

            # Petal half-width angle (controls petal width)
            petal_half_width = np.pi / petal_count * 0.9

            # Petal radial extent = petal_r * (1 + 0.18*cos elongation)
            # elongated in the direction of each petal's axis
            best_pa_idx = np.argmin([abs(d) for d in diffs])
            best_pa = petal_angles[best_pa_idx]
            # Angular weight: Gaussian falloff from petal axis
            ang_weight = np.exp(-min_diff ** 2 / (2 * (petal_half_width * 0.55) ** 2))
            local_petal_r = petal_r * (0.82 + 0.24 * ang_weight)

            if r <= local_petal_r and min_diff <= petal_half_width:
                petal_mask[y, x] = 1.0
                petal_depth[y, x] = min(r / local_petal_r, 1.0)  # 0 at center, 1 at tip

                # Midrib crease: thin zone along each petal's central axis
                crease_half = petal_half_width * 0.09
                crease_weight = np.exp(-min_diff ** 2 / (2 * crease_half ** 2))
                petal_crease[y, x] = crease_weight

    # Smooth the masks to remove pixelation
    petal_mask_s   = gaussian_filter(petal_mask.astype(np.float64), sigma=8).astype(np.float32)
    petal_depth_s  = gaussian_filter(petal_depth.astype(np.float64), sigma=6).astype(np.float32)
    petal_crease_s = gaussian_filter(petal_crease.astype(np.float64), sigma=4).astype(np.float32)

    # Clamp
    petal_mask_s   = np.clip(petal_mask_s,   0.0, 1.0)
    petal_depth_s  = np.clip(petal_depth_s,  0.0, 1.0)
    petal_crease_s = np.clip(petal_crease_s, 0.0, 1.0)

    # ── Petal colour: white outer → peach → salmon → crimson throat ───────────
    # depth=0 (center throat): crimson (0.72, 0.30, 0.28)
    # depth=0.25: deep salmon (0.88, 0.56, 0.42)
    # depth=0.55: pale peach (0.94, 0.78, 0.68)
    # depth=1.0 (outer tip): near-white (0.98, 0.96, 0.92)

    def petal_color(depth: float):
        """Piecewise colour gradient along petal radius."""
        d = float(np.clip(depth, 0.0, 1.0))
        if d < 0.25:
            t = d / 0.25
            r = 0.72 + (0.88 - 0.72) * t
            g = 0.30 + (0.56 - 0.30) * t
            b = 0.28 + (0.42 - 0.28) * t
        elif d < 0.55:
            t = (d - 0.25) / 0.30
            r = 0.88 + (0.94 - 0.88) * t
            g = 0.56 + (0.78 - 0.56) * t
            b = 0.42 + (0.68 - 0.42) * t
        else:
            t = (d - 0.55) / 0.45
            r = 0.94 + (0.98 - 0.94) * t
            g = 0.78 + (0.96 - 0.78) * t
            b = 0.68 + (0.92 - 0.68) * t
        return np.clip(r, 0, 1), np.clip(g, 0, 1), np.clip(b, 0, 1)

    # Vectorize petal colour mapping
    pc_r = np.zeros((h, w), dtype=np.float32)
    pc_g = np.zeros((h, w), dtype=np.float32)
    pc_b = np.zeros((h, w), dtype=np.float32)

    depth_flat = petal_depth_s.ravel()
    for idx, d in enumerate(depth_flat):
        r_, g_, b_ = petal_color(d)
        pc_r.ravel()[idx] = r_
        pc_g.ravel()[idx] = g_
        pc_b.ravel()[idx] = b_

    # Midrib crease: warm luminous lift along crease (slightly lighter/warmer)
    crease_lift = petal_crease_s * petal_mask_s * 0.06
    pc_r = np.clip(pc_r + crease_lift * 1.00, 0.0, 1.0)
    pc_g = np.clip(pc_g + crease_lift * 0.85, 0.0, 1.0)
    pc_b = np.clip(pc_b + crease_lift * 0.70, 0.0, 1.0)

    # ── Composite petal over sky ──────────────────────────────────────────────
    pm = petal_mask_s[:, :, np.newaxis]
    arr = arr * (1.0 - pm) + np.stack([pc_r, pc_g, pc_b], axis=-1) * pm

    # ── Throat depth: warm umber at the very center ───────────────────────────
    ys, xs = np.mgrid[0:h, 0:w]
    dist_center = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2).astype(np.float32)
    throat_zone = np.clip(1.0 - dist_center / (throat_r * 2.5), 0.0, 1.0)
    throat_zone = (throat_zone ** 2.0).astype(np.float32)

    arr[:, :, 0] = np.clip(arr[:, :, 0] + throat_zone * (0.28 - arr[:, :, 0]) * 0.80, 0.0, 1.0)
    arr[:, :, 1] = np.clip(arr[:, :, 1] + throat_zone * (0.10 - arr[:, :, 1]) * 0.80, 0.0, 1.0)
    arr[:, :, 2] = np.clip(arr[:, :, 2] + throat_zone * (0.10 - arr[:, :, 2]) * 0.80, 0.0, 1.0)

    # ── Convert to uint8 ─────────────────────────────────────────────────────
    return (np.clip(arr, 0.0, 1.0) * 255).astype(np.uint8)


def main():
    print(f"Session 270 -- White Jimson Weed, Desert Night")
    print(f"Georgia O'Keeffe Organic Abstraction -- 181st distinct mode")
    print(f"Canvas: {W} × {H}")
    print()

    print("Building procedural reference...")
    ref = build_reference(W, H)
    print(f"  Reference shape: {ref.shape}, dtype: {ref.dtype}")

    print("Initialising Painter...")
    p = Painter(W, H, seed=SEED)

    # ── 1. Toned ground: warm cream ──────────────────────────────────────────
    print("  tone_ground (warm cream 0.94/0.90/0.84)...")
    p.tone_ground((0.94, 0.90, 0.84), texture_strength=0.015)

    # ── 2. Underpainting x2 ──────────────────────────────────────────────────
    print("  underpainting pass 1 (large)...")
    p.underpainting(ref, stroke_size=52, n_strokes=240)
    print("  underpainting pass 2 (medium)...")
    p.underpainting(ref, stroke_size=32, n_strokes=260)

    # ── 3. Block in x2 ───────────────────────────────────────────────────────
    print("  block_in pass 1 (broad, stroke=32)...")
    p.block_in(ref, stroke_size=32, n_strokes=480)
    print("  block_in pass 2 (medium, stroke=18)...")
    p.block_in(ref, stroke_size=18, n_strokes=500)

    # ── 4. Build form x2 ─────────────────────────────────────────────────────
    print("  build_form pass 1 (medium, stroke=12)...")
    p.build_form(ref, stroke_size=12, n_strokes=520)
    print("  build_form pass 2 (fine, stroke=6)...")
    p.build_form(ref, stroke_size=6, n_strokes=440)

    # ── 5. Place lights ───────────────────────────────────────────────────────
    print("  place_lights (stroke=4)...")
    p.place_lights(ref, stroke_size=4, n_strokes=300)

    # ── 6. Translucency Bloom pass (s270 improvement) ─────────────────────────
    print("  paint_translucency_bloom_pass (s270 improvement)...")
    p.paint_translucency_bloom_pass(
        lum_low=0.50,
        lum_high=0.90,
        sat_threshold=0.10,
        bloom_sigma=14.0,
        bloom_warmth=0.12,
        bloom_strength=0.24,
        halo_sigma=4.0,
        halo_opacity=0.15,
        opacity=0.70,
    )

    # ── 7. O'Keeffe Organic Form pass (181st mode) ────────────────────────────
    print("  okeeffe_organic_form_pass (session 270, 181st mode)...")
    p.okeeffe_organic_form_pass(
        variance_sigma=7.0,
        smooth_sigma=3.0,
        smooth_strength=0.32,
        mid_lum_low=0.30,
        mid_lum_high=0.70,
        mid_variance_cap=0.022,
        sat_lift=0.16,
        edge_threshold=0.020,
        edge_sharpen_amount=0.42,
        edge_sharpen_sigma=1.6,
        opacity=0.80,
    )

    # ── 8. Lost and found edges: soften inner petal-to-petal boundaries ───────
    print("  paint_lost_found_edges_pass...")
    p.paint_lost_found_edges_pass()

    # ── 9. Pigment granulation in deep zones ──────────────────────────────────
    print("  paint_granulation_pass...")
    p.paint_granulation_pass()

    # ── 10. Save ──────────────────────────────────────────────────────────────
    print(f"  Saving to {OUT}...")
    p.save(OUT)
    print(f"Done. Output: {OUT}")
    return OUT


if __name__ == "__main__":
    main()
