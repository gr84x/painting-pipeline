"""
paint_s279_ancient_light.py -- Session 279

"Ancient Light -- in the manner of William Blake"

Image Description
-----------------
Subject & Composition
    A vast cosmic sky seen from a high mountain ridge at the edge of night,
    looking upward and outward from a rocky promontory. Portrait format
    1040 x 1440. The viewpoint is from near the surface of the rocky ridge,
    elevated above sea level, looking slightly upward -- the horizon sits at
    the lower 22% of the canvas, and the full upper 78% is sky. The
    composition is structured in three vertical bands of light:

    (1) CENTRAL RADIANCE SHAFT (35-65% horizontal): A column of warm golden
        light descends from the uppermost sky, expanding downward like a
        trumpet or horn shape -- narrow at zenith, broad at horizon.
        This is the primary divine light source: celestial gold radiating
        from a single point of origin beyond the top frame.
    (2) STORM FLANKS (left 35% and right 35%): Deep turbulent cloud masses
        in dark grey-blue and deep ultramarine, curling and billowing inward
        toward the central shaft. Their underlit surfaces catch the golden
        glow; their interiors are pure spiritual darkness.
    (3) ROCKY RIDGE (lower 22%): A silhouetted mountain ridge in near-black
        umber, jagged and irregular, its upper surface barely catching the
        lowest edge of the golden light. The ridge is the single solid
        element in an otherwise pure atmosphere.

The Figure
    No human figures. The landscape is the sole subject -- as Blake intended
    in his pure atmospheric visions, where landscape becomes theology.
    The light column is the protagonist: ancient, emanating, pressing
    downward through clouds that resist and glow. The rocky ridge at
    the bottom is the receiving earth: dark, resistant, the lowest rung
    of the Blakean cosmos between material ground and divine fire above.

The Environment
    ZENITH ORIGIN (top 8%): Near-black at the very top -- the highest
    spiritual void before light begins. Color: deep indigo-black (0.06, 0.08,
    0.20), the absolute night from which divine radiance descends.

    UPPER CLOUD MASS (8-40%): Turbulent storm clouds in dark grey-blue
    (0.18, 0.20, 0.32 in shadow; 0.42, 0.44, 0.55 in partial lit areas).
    The clouds mass inward toward the central light column, their inner
    edges receiving warm golden light while their outer flanks recede into
    deep ultramarine. Cloud texture: large rolling forms, not sharp edges
    -- soft transitions with occasional crisp lit highlights.

    CENTRAL GOLDEN SHAFT (expanding downward): The divine light column.
    At its core: pure radiant gold-white (0.95, 0.90, 0.72) -- almost
    white at the center, yellowing outward. The shaft widens from a point
    at zenith to approximately 60% of canvas width at the horizon. Edge
    of shaft: warm amber (0.82, 0.68, 0.28) graduating into orange-grey
    at the boundary with the storm flanks.

    MIDDLE SKY (40-70%): The zone where shaft and storm meet. Central band
    is warm amber-gold; left and right are lit cloud undersides catching
    warm reflected light (0.55, 0.48, 0.28) before darkening outward to
    ultramarine storm cloud. This is the most tonally complex region --
    the battle between spiritual light and material darkness.

    LOWER SKY / HORIZON GLOW (70-78%): The lowest cloud layer just above
    the ridge, strongly lit from below by the light shaft striking the
    rocks. The underside of the horizon clouds are warmly illuminated
    (0.70, 0.52, 0.22), their edges dark. The horizon itself glows with
    orange-amber warmth (0.78, 0.58, 0.20).

    ROCKY RIDGE (78-100%): The mountain silhouette. Deep near-black umber
    (0.10, 0.07, 0.05) with very slight warm glowing on the highest rock
    surfaces that catch the horizon light (0.28, 0.20, 0.10). The ridge
    is irregular and jagged -- not a smooth curve but a broken series of
    dark peaks and valleys. A few individual boulders are suggested as
    darker masses within the ridge.

Technique & Palette
    William Blake mode -- session 279, 190th distinct mode.

    The Blake Visionary Radiance pass transforms this atmospheric painting
    into a Blakean vision: the iso-luminance rings create the characteristic
    concentric corona structure around the central light shaft; the gold
    celestial tinting intensifies the warm zones into divine fire; the dark
    contour reinforcement traces the cloud and ridge edges with the dark
    bounding line Blake regarded as the fundamental truth of art; and the
    ultramarine shadow infusion turns the storm cloud depths into deep
    spiritual blue.

    The Surface Grain improvement adds fine canvas grain in the thin-painted
    areas -- the dark zenith sky, the shadowed cloud undersides -- simulating
    Blake's actual painted surface.

    Pipeline:
    1. Procedural reference: cosmic sky with central light shaft, storm cloud
       flanks, and dark rocky ridge silhouette at base.
    2. tone_ground: warm vellum-parchment (0.72, 0.66, 0.52).
    3. underpainting x2: establish the fundamental light/dark tonal structure.
    4. block_in x2: broad sky masses -- central shaft, storm flanks, ridge.
    5. build_form x2: cloud texture, shaft gradation, ridge detail.
    6. place_lights: shaft core highlights, cloud-edge gleams.
    7. blake_visionary_radiance_pass (190th mode): ring corona + gold celestial
       tinting + dark contour reinforcement + ultramarine shadow infusion.
    8. paint_surface_grain_pass (s279 improvement): band-pass grain in thin-
       painted dark areas (zenith sky, cloud shadow zones).
    9. paint_aerial_perspective_pass: atmospheric haze deepening the far sky.

    Palette (Blake ancient light):
    celestial gold (0.88/0.72/0.14) -- divine radiance shaft core (0.95/0.90/0.72) --
    deep ultramarine void (0.10/0.15/0.48) -- storm cloud (0.18/0.20/0.32) --
    warm amber horizon (0.78/0.58/0.20) -- cloud lit underside (0.55/0.48/0.28) --
    ridge near-black (0.10/0.07/0.05) -- ridge warm catch (0.28/0.20/0.10) --
    partial lit cloud (0.42/0.44/0.55) -- zenith void (0.06/0.08/0.20)

Mood & Intent
    The painting asks one question: what does divine light look like as it
    passes through the material world? Blake spent his life painting that
    question. The light descends from an unseen source beyond the frame --
    ancient, purposeful, pressing -- and everything in the composition exists
    in relation to it: the storm clouds resist and glow; the rocks receive and
    darken; the horizon burns with the collision of gold fire and dark earth.

    The mood is sublime and unsettling -- not the gentle sublime of Constable
    or Turner, but Blake's specific theological sublime, where natural
    phenomena are vehicles for spiritual war. The darkness around the light
    shaft is not mere weather but the material world's resistance to the
    divine. The gold at the center is not beautiful in the aesthetic sense --
    it is dangerous, overwhelming, ancient.

    The viewer is positioned on the rocky ridge -- the last solid ground before
    the void. Above: everything is movement and light and darkness in conflict.
    Below: solid stone, the body, the earth that Blake painted all his life as
    both prison and foundation.
"""
import sys
import os
import math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

from stroke_engine import Painter

# ── Canvas and output ─────────────────────────────────────────────────────────
W, H   = 1040, 1440
SEED   = 279
OUT    = "s279_ancient_light.png"


# ── Build reference ───────────────────────────────────────────────────────────
def build_reference() -> np.ndarray:
    """Procedural reference: cosmic light shaft breaking through storm clouds."""
    rng = np.random.default_rng(SEED)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    ys, xs = np.mgrid[0:H, 0:W]
    t_y = ys.astype(np.float32) / H
    t_x = xs.astype(np.float32) / W

    # ── 1. Base sky: deep indigo-ultramarine gradient ─────────────────────────
    # Zenith: near-black indigo; lower sky: deep navy
    sky_base_r = (0.06 + t_y * 0.14 + rng.random((H, W)).astype(np.float32) * 0.015)
    sky_base_g = (0.08 + t_y * 0.14 + rng.random((H, W)).astype(np.float32) * 0.015)
    sky_base_b = (0.20 + t_y * 0.20 + rng.random((H, W)).astype(np.float32) * 0.018)
    ref[:, :, 0] = np.clip(sky_base_r, 0, 1)
    ref[:, :, 1] = np.clip(sky_base_g, 0, 1)
    ref[:, :, 2] = np.clip(sky_base_b, 0, 1)

    # ── 2. Central light shaft ────────────────────────────────────────────────
    shaft_center_x = W // 2
    # Shaft half-width: widens from 40px at top to 340px at horizon
    horizon_y = int(H * 0.78)
    shaft_top_hw  = 38.0
    shaft_bot_hw  = 340.0

    for y in range(min(horizon_y, H)):
        t_shaft = y / float(horizon_y)
        shaft_hw = shaft_top_hw + (shaft_bot_hw - shaft_top_hw) * t_shaft
        dist_from_center = np.abs(xs[y, :].astype(np.float32) - shaft_center_x)
        # Core: Gaussian falloff within shaft
        shaft_weight = np.exp(-0.5 * (dist_from_center / max(shaft_hw, 1.0)) ** 2).astype(np.float32)
        # Core brightness: warm gold, bright at center
        shaft_r = np.float32(0.95 - t_shaft * 0.18)   # warm golden core
        shaft_g = np.float32(0.88 - t_shaft * 0.22)
        shaft_b = np.float32(0.62 - t_shaft * 0.30)
        # Apply shaft over existing sky
        ref[y, :, 0] = np.clip(ref[y, :, 0] + shaft_r * shaft_weight * 0.92, 0, 1)
        ref[y, :, 1] = np.clip(ref[y, :, 1] + shaft_g * shaft_weight * 0.92, 0, 1)
        ref[y, :, 2] = np.clip(ref[y, :, 2] + shaft_b * shaft_weight * 0.92, 0, 1)

    # ── 3. Storm cloud masses (left and right flanks) ─────────────────────────
    # Left cloud mass
    for y in range(int(H * 0.06), int(H * 0.72)):
        t_c = (y - int(H * 0.06)) / float(int(H * 0.72) - int(H * 0.06))
        # Cloud boundary moves inward as we descend
        cloud_right = int(W * 0.08 + W * 0.28 * (1.0 - t_c * 0.5))
        for x in range(0, min(cloud_right, W)):
            t_x_cloud = x / float(max(cloud_right, 1))
            # Cloud: dark grey-blue, lit slightly on inner edge by shaft glow
            inner_glow = max(0.0, (t_x_cloud - 0.6) / 0.4)  # inner 40% catches glow
            cloud_r = 0.14 + inner_glow * 0.28 + rng.random() * 0.03
            cloud_g = 0.16 + inner_glow * 0.24 + rng.random() * 0.03
            cloud_b = 0.30 + inner_glow * 0.18 + rng.random() * 0.03
            alpha = 0.75 + rng.random() * 0.15
            ref[y, x, 0] = ref[y, x, 0] * (1 - alpha) + cloud_r * alpha
            ref[y, x, 1] = ref[y, x, 1] * (1 - alpha) + cloud_g * alpha
            ref[y, x, 2] = ref[y, x, 2] * (1 - alpha) + cloud_b * alpha

    # Right cloud mass
    for y in range(int(H * 0.06), int(H * 0.72)):
        t_c = (y - int(H * 0.06)) / float(int(H * 0.72) - int(H * 0.06))
        cloud_left = int(W * 0.92 - W * 0.28 * (1.0 - t_c * 0.5))
        for x in range(max(cloud_left, 0), W):
            t_x_cloud = 1.0 - (x - cloud_left) / float(max(W - cloud_left, 1))
            inner_glow = max(0.0, (t_x_cloud - 0.6) / 0.4)
            cloud_r = 0.14 + inner_glow * 0.28 + rng.random() * 0.03
            cloud_g = 0.16 + inner_glow * 0.24 + rng.random() * 0.03
            cloud_b = 0.30 + inner_glow * 0.18 + rng.random() * 0.03
            alpha = 0.75 + rng.random() * 0.15
            ref[y, x, 0] = ref[y, x, 0] * (1 - alpha) + cloud_r * alpha
            ref[y, x, 1] = ref[y, x, 1] * (1 - alpha) + cloud_g * alpha
            ref[y, x, 2] = ref[y, x, 2] * (1 - alpha) + cloud_b * alpha

    # ── 4. Mid-sky cloud texture (volumetric) ─────────────────────────────────
    # Scatter cloud clumps across the middle sky using Gaussian blobs
    n_cloud_clumps = 28
    for _ in range(n_cloud_clumps):
        cx = rng.integers(0, W)
        cy = rng.integers(int(H * 0.10), int(H * 0.65))
        rx = rng.integers(60, 200)
        ry = rng.integers(40, 120)
        cloud_lum = 0.18 + rng.random() * 0.22  # variable cloud darkness
        # Lit edge (inner facing shaft) gets warmer
        dist_to_shaft = abs(cx - shaft_center_x)
        lit_bonus = max(0.0, (1.0 - dist_to_shaft / (W * 0.5)) * 0.15)

        # Draw Gaussian blob
        x0 = max(0, cx - 2 * rx)
        x1 = min(W, cx + 2 * rx)
        y0 = max(0, cy - 2 * ry)
        y1 = min(H, cy + 2 * ry)
        if x1 <= x0 or y1 <= y0:
            continue
        sub_ys, sub_xs = np.mgrid[y0:y1, x0:x1]
        dist2 = ((sub_xs - cx).astype(np.float32) / max(rx, 1)) ** 2 + \
                ((sub_ys - cy).astype(np.float32) / max(ry, 1)) ** 2
        blob = np.exp(-dist2 * 1.5).astype(np.float32)
        alpha = blob * (0.40 + rng.random() * 0.25)
        cr = cloud_lum + lit_bonus * 0.6
        cg = cloud_lum + lit_bonus * 0.5
        cb = cloud_lum + 0.08 + lit_bonus * 0.2
        ref[y0:y1, x0:x1, 0] = np.clip(
            ref[y0:y1, x0:x1, 0] * (1 - alpha) + cr * alpha, 0, 1)
        ref[y0:y1, x0:x1, 1] = np.clip(
            ref[y0:y1, x0:x1, 1] * (1 - alpha) + cg * alpha, 0, 1)
        ref[y0:y1, x0:x1, 2] = np.clip(
            ref[y0:y1, x0:x1, 2] * (1 - alpha) + cb * alpha, 0, 1)

    # ── 5. Horizon glow band ──────────────────────────────────────────────────
    hor_y0 = int(H * 0.70)
    hor_y1 = int(H * 0.80)
    for y in range(hor_y0, min(hor_y1, H)):
        t_h = (y - hor_y0) / float(hor_y1 - hor_y0)
        # Center of horizon: warmest; edges: darker
        for x in range(W):
            t_hx = abs(x - shaft_center_x) / float(W * 0.5)
            horizon_warm = max(0.0, (1.0 - t_hx * 1.2)) * (1.0 - t_h * 0.8)
            ref[y, x, 0] = np.clip(ref[y, x, 0] + 0.40 * horizon_warm, 0, 1)
            ref[y, x, 1] = np.clip(ref[y, x, 1] + 0.26 * horizon_warm, 0, 1)
            ref[y, x, 2] = np.clip(ref[y, x, 2] + 0.02 * horizon_warm, 0, 1)

    # ── 6. Rocky ridge silhouette (lower 22%) ─────────────────────────────────
    # Generate jagged ridge profile using sum of sine waves
    ridge_base = int(H * 0.78)
    ridge_profile = np.zeros(W, dtype=np.float32)
    # Sum of several sine waves at different frequencies for natural jagged shape
    for freq, amp, phase in [
        (2.4, 0.06, 0.0),
        (5.8, 0.04, 1.2),
        (11.2, 0.025, 2.5),
        (22.0, 0.012, 0.8),
        (45.0, 0.006, 1.7),
    ]:
        ridge_profile += amp * np.sin(
            np.linspace(0, freq * 2 * math.pi, W) + phase)
    # Ridge height: 0.10-0.20 of canvas from bottom
    ridge_min = int(H * 0.80)
    ridge_max = int(H * 0.91)
    ridge_height = ridge_min + (ridge_max - ridge_min) * (
        (ridge_profile - ridge_profile.min()) /
        max(ridge_profile.max() - ridge_profile.min(), 1e-6))
    ridge_height = ridge_height.astype(int)

    for x in range(W):
        rh = max(0, min(H - 1, ridge_height[x]))
        # Everything below ridge height is rock
        for y in range(rh, H):
            # Dark umber rock
            lum = 0.08 + rng.random() * 0.04
            # Slight warm catch at the very ridge top surface (lit by horizon glow)
            dist_to_top = y - rh
            if dist_to_top < 8:
                warm_catch = max(0.0, 0.18 * (1.0 - dist_to_top / 8.0))
                dist_from_shaft_x = abs(x - shaft_center_x) / float(W * 0.5)
                warm_catch *= max(0, 1.0 - dist_from_shaft_x * 1.5)
                ref[y, x, 0] = np.clip(lum * 0.82 + warm_catch * 0.70, 0, 1)
                ref[y, x, 1] = np.clip(lum * 0.68 + warm_catch * 0.50, 0, 1)
                ref[y, x, 2] = np.clip(lum * 0.52 + warm_catch * 0.15, 0, 1)
            else:
                ref[y, x, 0] = np.clip(lum * 0.82, 0, 1)
                ref[y, x, 1] = np.clip(lum * 0.68, 0, 1)
                ref[y, x, 2] = np.clip(lum * 0.52, 0, 1)

    # ── 7. Final soft blur ────────────────────────────────────────────────────
    for c in range(3):
        ref[:, :, c] = gaussian_filter(ref[:, :, c].astype(np.float64),
                                        sigma=1.2).astype(np.float32)
    # Re-sharpen shaft core (preserve hard shaft edge)
    shaft_weights = np.zeros((H, W), dtype=np.float32)
    for y in range(min(horizon_y, H)):
        t_shaft = y / float(horizon_y)
        shaft_hw = shaft_top_hw + (shaft_bot_hw - shaft_top_hw) * t_shaft
        dist_from_center = np.abs(xs[y, :].astype(np.float32) - shaft_center_x)
        shaft_weights[y, :] = np.exp(
            -0.5 * (dist_from_center / max(shaft_hw * 0.4, 1.0)) ** 2)
    # Slight additional brightness at core center
    core_boost = shaft_weights * 0.06
    ref[:, :, 0] = np.clip(ref[:, :, 0] + core_boost, 0, 1)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + core_boost * 0.85, 0, 1)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + core_boost * 0.40, 0, 1)

    return (np.clip(ref, 0, 1) * 255).astype(np.uint8)


# ── Build reference ───────────────────────────────────────────────────────────
print("Building procedural reference...")
ref = build_reference()
Image.fromarray(ref).save("s279_reference.png")
print(f"  Reference saved: s279_reference.png ({W}x{H})")

# ── Painting pipeline ─────────────────────────────────────────────────────────
p = Painter(W, H, seed=SEED)

print("tone_ground...")
p.tone_ground((0.72, 0.66, 0.52), texture_strength=0.016)

print("underpainting (broad)...")
p.underpainting(ref, stroke_size=56, n_strokes=220)

print("underpainting (medium)...")
p.underpainting(ref, stroke_size=38, n_strokes=210)

print("block_in (broad)...")
p.block_in(ref, stroke_size=32, n_strokes=460)

print("block_in (medium)...")
p.block_in(ref, stroke_size=20, n_strokes=500)

print("build_form (medium)...")
p.build_form(ref, stroke_size=12, n_strokes=490)

print("build_form (fine)...")
p.build_form(ref, stroke_size=6, n_strokes=400)

print("place_lights...")
p.place_lights(ref, stroke_size=4, n_strokes=280)

print("blake_visionary_radiance_pass (190th mode)...")
p.blake_visionary_radiance_pass(
    n_rings            = 7,
    ring_strength      = 0.07,
    ring_smooth_sigma  = 14.0,
    gold_threshold     = 0.50,
    gold_strength      = 0.38,
    gold_r             = 0.88,
    gold_g             = 0.72,
    gold_b             = 0.14,
    contour_strength   = 0.28,
    contour_threshold  = 0.042,
    ultra_threshold    = 0.36,
    ultra_strength     = 0.30,
    ultra_r            = 0.10,
    ultra_g            = 0.15,
    ultra_b            = 0.48,
    opacity            = 0.88,
)

print("paint_surface_grain_pass (s279 improvement)...")
p.paint_surface_grain_pass(
    grain_strength     = 0.055,
    coverage_radius    = 4,
    coverage_boost     = 3.2,
    linen_r            = 0.78,
    linen_g            = 0.68,
    linen_b            = 0.52,
    grain_sigma_fine   = 0.8,
    grain_sigma_coarse = 2.3,
    seed               = 279,
    opacity            = 0.90,
)

print("paint_aerial_perspective_pass...")
p.paint_aerial_perspective_pass()

print(f"Saving {OUT}...")
p.save(OUT)
print(f"Done: {OUT}")
