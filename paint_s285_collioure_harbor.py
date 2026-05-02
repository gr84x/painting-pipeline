"""Session 285 -- André Derain (196th mode)
derain_fauve_intensity_pass + paint_frequency_separation_pass

Subject & Composition:
    "Collioure au Midi -- The Harbour at Noon, 1905" -- the medieval fishing
    harbour of Collioure seen from the stone quay on a hot Mediterranean noon.
    Three moored fishing boats in the immediate foreground -- one cadmium-orange,
    one cobalt blue, one vivid vermillion -- occupy the lower third. Behind them,
    the harbour wall curves leftward toward the medieval fortified church tower.
    The midground is a stepped arrangement of whitewashed and ochre buildings
    climbing the steep hillside. The composition is slightly elevated, looking
    down into the harbour from the quay level, with the horizon bisecting the
    canvas at roughly 55% height.

The Figure:
    No human figures are present. The fishing boats are the central characters --
    their hulls bold and present, their reflections broken by the harbour swell.
    The boats' emotional state: expectant, at rest in the midday heat. The town
    behind them: ancient, indifferent to the heat, baking in silence. The mood
    is that particular Mediterranean stillness of high noon -- everything arrested
    in the excess of light.

The Environment:
    SKY: A Fauve sky of pure cerulean-cobalt in the upper third, transitioning
    through electric azure toward a warm yellow-gold just above the horizon.
    No cloud -- the sky is a flat, luminous plane of deep blue, the kind of blue
    that Derain called "too blue to be real." A narrow band of warm haze at the
    horizon separates sky from the upper town.

    WATER: The harbour water is the most complex element -- not naturalistic blue-
    green but a Fauve surface of multiple colour zones: deep cobalt where the
    shadow of the quay falls across it, vivid orange-cadmium where it catches the
    noon sun directly, flashes of viridian where it reflects the hillside vegetation,
    violet-grey in the cool interior shadow. The reflections of the three boats
    are broken, bright, colour fragments in the surface.

    BUILDINGS / HILLSIDE: The steep hillside behind the harbour carries whitewashed
    walls reflecting intense noon light -- near-white with warm amber tinting --
    and orange-red tile roofs. Deep violet-purple shadows in doorways and alleys
    cut between the structures. Vegetation (olive, cypress, scrub) appears as
    vivid acid green-yellow patches between the buildings.

    FORTIFICATION TOWER: At the left, the medieval Tour du Château de Collioure
    rises -- a warm ochre-grey stone tower with a small dome, rendered in flat
    plane with strong cast shadows. Its silhouette is the compositional anchor.

    QUAY FOREGROUND: The stone quay occupies the bottom edge -- rough-textured
    warm ochre stone with violet shadow pooling in the cracks. The boats are
    moored to iron rings, their hulls close and large.

Technique & Palette:
    André Derain's Fauve method, Collioure 1905. The palette is built around
    three primary Fauve oppositions: cadmium orange vs. cobalt cerulean (the
    dominant boats), viridian vs. violet-crimson (hillside vs. shadows), cadmium
    yellow vs. deep navy (sky accent vs. harbour depth). Colours are unmixed
    or minimally mixed -- each zone commits fully to its hue. No grey, no neutral:
    shadows are vivid violet-blue, lights are vivid amber-orange.
    The derain_fauve_intensity_pass enforces saturation power-curve expansion,
    6-sector hue commitment, local colour contrast amplification (simultaneous
    contrast), and gradient-angle warm/cool directional push.

Mood & Intent:
    The image aims for the specific Fauve quality described by Matisse after
    seeing Derain's Collioure paintings: "colour for colour's own sake." The
    viewer should feel the heat of the Mediterranean noon as a chromatic
    event -- the light not described but enacted in paint. The harbour is a
    pretext for colour. The three boats are primary, secondary, tertiary -- a
    colour exercise in disguise. The intent is joy: unironic, unmediated,
    physical joy in pure colour against the ancient stone and bright water.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stroke_engine import Painter

# ── Canvas dimensions ────────────────────────────────────────────────────────
W, H = 1440, 1040   # landscape -- Collioure harbour panorama
SEED = 285

# ── Reference: procedural Collioure harbour at noon ──────────────────────────

def build_reference() -> np.ndarray:
    """Construct a vivid Fauve Collioure harbour reference."""
    from scipy.ndimage import gaussian_filter as gf
    rng = np.random.default_rng(SEED)

    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    xs = np.linspace(0.0, 1.0, W, dtype=np.float32)[None, :]

    horizon = 0.52   # horizon at 52% from top

    # ── Sky (upper 52%) ───────────────────────────────────────────────────────
    sky_zone = ys < horizon
    # Deep cobalt at top → cerulean → warm yellow-gold near horizon
    sky_frac = np.clip(ys / (horizon + 0.01), 0.0, 1.0)  # 0 = top, 1 = horizon

    sky_r = np.clip(0.08 + sky_frac * 0.78, 0.0, 1.0)   # cobalt → warm gold
    sky_g = np.clip(0.18 + sky_frac * 0.60, 0.0, 1.0)
    sky_b = np.clip(0.82 - sky_frac * 0.34, 0.0, 1.0)   # deep blue → lighter

    # Fauve: push sky toward electric cobalt-cerulean (less naturalistic)
    sky_r = np.clip(sky_r * 0.80, 0.0, 1.0)
    sky_g = np.clip(sky_g * 0.90, 0.0, 1.0)

    ref[:, :, 0] = np.where(sky_zone, sky_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(sky_zone, sky_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(sky_zone, sky_b, ref[:, :, 2])

    # ── Harbour water (middle band: horizon to ~68%) ──────────────────────────
    water_top = horizon
    water_bot = 0.68
    water_zone = (ys >= water_top) & (ys < water_bot)
    water_frac = np.clip((ys - water_top) / (water_bot - water_top + 0.01), 0.0, 1.0)

    # Base: deep navy-cobalt harbour
    w_r = np.full((H, W), 0.12, dtype=np.float32)
    w_g = np.full((H, W), 0.22, dtype=np.float32)
    w_b = np.full((H, W), 0.58, dtype=np.float32)

    # Noon sunlight patches on water: vivid cadmium-orange reflections
    sun_noise = gf(rng.random((H, W)).astype(np.float32), sigma=[4, 18])
    sun_patch = np.clip((sun_noise - 0.54) * 5.0, 0.0, 1.0) * water_zone.astype(np.float32)
    w_r = np.clip(w_r + sun_patch * 0.78, 0.0, 1.0)
    w_g = np.clip(w_g + sun_patch * 0.44, 0.0, 1.0)
    w_b = np.clip(w_b + sun_patch * 0.02, 0.0, 1.0)

    # Viridian-green reflections of hillside vegetation
    vir_noise = gf(rng.random((H, W)).astype(np.float32), sigma=[3, 12])
    vir_patch = np.clip((vir_noise - 0.60) * 4.5, 0.0, 1.0) * water_zone.astype(np.float32)
    w_r = np.clip(w_r + vir_patch * (-0.02), 0.0, 1.0)
    w_g = np.clip(w_g + vir_patch * 0.40, 0.0, 1.0)
    w_b = np.clip(w_b + vir_patch * 0.12, 0.0, 1.0)

    # Quay shadow on water (left band): deep violet-blue
    quay_shadow_x = xs < 0.28
    quay_shad_zone = water_zone & quay_shadow_x
    w_r = np.where(quay_shad_zone, np.clip(w_r * 0.52, 0.0, 1.0), w_r)
    w_g = np.where(quay_shad_zone, np.clip(w_g * 0.48, 0.0, 1.0), w_g)
    w_b = np.where(quay_shad_zone, np.clip(w_b * 0.92, 0.0, 1.0), w_b)

    ref[:, :, 0] = np.where(water_zone, w_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(water_zone, w_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(water_zone, w_b, ref[:, :, 2])

    # ── Hillside buildings (left 45%, above water) ────────────────────────────
    hill_zone = (ys < water_top) & (ys >= 0.20) & (xs < 0.48)

    # Stepped buildings: whitewashed walls + orange tile roofs
    hill_noise = gf(rng.random((H, W)).astype(np.float32), sigma=5)
    hb_r = np.clip(0.80 + hill_noise * 0.12, 0.0, 1.0)
    hb_g = np.clip(0.72 + hill_noise * 0.10, 0.0, 1.0)
    hb_b = np.clip(0.58 + hill_noise * 0.08, 0.0, 1.0)

    ref[:, :, 0] = np.where(hill_zone, hb_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(hill_zone, hb_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(hill_zone, hb_b, ref[:, :, 2])

    # Tile roofs: vivid orange-red bands
    for (ry0, ry1, rx0, rx1) in [
        (0.30, 0.34, 0.04, 0.18), (0.34, 0.37, 0.10, 0.22),
        (0.37, 0.40, 0.16, 0.28), (0.40, 0.43, 0.22, 0.34),
        (0.43, 0.46, 0.06, 0.16), (0.46, 0.49, 0.18, 0.30),
    ]:
        y0, y1 = int(ry0 * H), int(ry1 * H)
        x0, x1 = int(rx0 * W), int(rx1 * W)
        ref[y0:y1, x0:x1, 0] = 0.82
        ref[y0:y1, x0:x1, 1] = 0.28
        ref[y0:y1, x0:x1, 2] = 0.10

    # Shadow doorways and alleys: deep violet
    for (ry0, ry1, rx0, rx1) in [
        (0.32, 0.38, 0.04, 0.07), (0.38, 0.44, 0.12, 0.15),
        (0.28, 0.36, 0.20, 0.23), (0.36, 0.42, 0.28, 0.31),
        (0.42, 0.48, 0.08, 0.11), (0.30, 0.34, 0.35, 0.38),
    ]:
        y0, y1 = int(ry0 * H), int(ry1 * H)
        x0, x1 = int(rx0 * W), int(rx1 * W)
        ref[y0:y1, x0:x1, 0] = 0.26
        ref[y0:y1, x0:x1, 1] = 0.14
        ref[y0:y1, x0:x1, 2] = 0.42

    # Vegetation patches: acid yellow-green
    for (ry0, ry1, rx0, rx1) in [
        (0.22, 0.28, 0.06, 0.14), (0.26, 0.32, 0.22, 0.30),
        (0.20, 0.26, 0.38, 0.46),
    ]:
        y0, y1 = int(ry0 * H), int(ry1 * H)
        x0, x1 = int(rx0 * W), int(rx1 * W)
        veg_noise = gf(rng.random((y1 - y0, x1 - x0)).astype(np.float32), sigma=3)
        ref[y0:y1, x0:x1, 0] = np.clip(0.22 + veg_noise * 0.28, 0.0, 1.0)
        ref[y0:y1, x0:x1, 1] = np.clip(0.62 + veg_noise * 0.24, 0.0, 1.0)
        ref[y0:y1, x0:x1, 2] = np.clip(0.12 + veg_noise * 0.18, 0.0, 1.0)

    # ── Fortification tower (far left) ────────────────────────────────────────
    tower_x0, tower_x1 = int(0.01 * W), int(0.10 * W)
    tower_y0, tower_y1 = int(0.20 * H), int(0.68 * H)
    tower_noise = gf(rng.random((tower_y1 - tower_y0, tower_x1 - tower_x0)
                                 ).astype(np.float32), sigma=3)
    ref[tower_y0:tower_y1, tower_x0:tower_x1, 0] = np.clip(0.62 + tower_noise * 0.14, 0.0, 1.0)
    ref[tower_y0:tower_y1, tower_x0:tower_x1, 1] = np.clip(0.52 + tower_noise * 0.10, 0.0, 1.0)
    ref[tower_y0:tower_y1, tower_x0:tower_x1, 2] = np.clip(0.30 + tower_noise * 0.10, 0.0, 1.0)

    # Tower shadow side (right edge): deep violet
    ts_x0 = tower_x1 - int(0.018 * W)
    ref[tower_y0:tower_y1, ts_x0:tower_x1, 0] = 0.22
    ref[tower_y0:tower_y1, ts_x0:tower_x1, 1] = 0.14
    ref[tower_y0:tower_y1, ts_x0:tower_x1, 2] = 0.48

    # Tower dome (top)
    dome_cx = int(0.055 * W)
    dome_cy = int(0.22 * H)
    dome_r  = int(0.030 * W)
    Y_, X_ = np.ogrid[:H, :W]
    dome_mask = ((X_ - dome_cx) ** 2 + (Y_ - dome_cy) ** 2) < dome_r ** 2
    ref[dome_mask, 0] = 0.68
    ref[dome_mask, 1] = 0.58
    ref[dome_mask, 2] = 0.38

    # ── Right hillside (right 55%, middle ground) ─────────────────────────────
    rhill_zone = (ys >= 0.24) & (ys < water_top) & (xs >= 0.48)
    rh_noise = gf(rng.random((H, W)).astype(np.float32), sigma=6)
    rh_r = np.clip(0.76 + rh_noise * 0.16, 0.0, 1.0)
    rh_g = np.clip(0.66 + rh_noise * 0.14, 0.0, 1.0)
    rh_b = np.clip(0.50 + rh_noise * 0.10, 0.0, 1.0)

    ref[:, :, 0] = np.where(rhill_zone, rh_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(rhill_zone, rh_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(rhill_zone, rh_b, ref[:, :, 2])

    # Right hillside tile roofs
    for (ry0, ry1, rx0, rx1) in [
        (0.30, 0.34, 0.52, 0.64), (0.34, 0.38, 0.62, 0.74),
        (0.38, 0.42, 0.70, 0.82), (0.42, 0.46, 0.76, 0.88),
        (0.26, 0.30, 0.56, 0.68), (0.28, 0.32, 0.80, 0.92),
    ]:
        y0, y1 = int(ry0 * H), int(ry1 * H)
        x0, x1 = int(rx0 * W), int(rx1 * W)
        ref[y0:y1, x0:x1, 0] = 0.80
        ref[y0:y1, x0:x1, 1] = 0.26
        ref[y0:y1, x0:x1, 2] = 0.08

    # Right hillside shadows
    for (ry0, ry1, rx0, rx1) in [
        (0.32, 0.40, 0.50, 0.53), (0.36, 0.44, 0.64, 0.67),
        (0.40, 0.48, 0.74, 0.77), (0.28, 0.36, 0.88, 0.91),
    ]:
        y0, y1 = int(ry0 * H), int(ry1 * H)
        x0, x1 = int(rx0 * W), int(rx1 * W)
        ref[y0:y1, x0:x1, 0] = 0.24
        ref[y0:y1, x0:x1, 1] = 0.12
        ref[y0:y1, x0:x1, 2] = 0.44

    # ── Quay stone (lower ~32%, behind the boats) ─────────────────────────────
    quay_top = 0.68
    quay_zone = ys >= quay_top
    qn = gf(rng.random((H, W)).astype(np.float32), sigma=[3, 12])
    q_r = np.clip(0.68 + qn * 0.14, 0.0, 1.0)
    q_g = np.clip(0.56 + qn * 0.12, 0.0, 1.0)
    q_b = np.clip(0.30 + qn * 0.10, 0.0, 1.0)

    # Violet shadow pools in quay cracks
    crack_noise = gf(rng.random((H, W)).astype(np.float32), sigma=[2, 8])
    crack = np.clip((crack_noise - 0.64) * 6.0, 0.0, 1.0) * quay_zone.astype(np.float32)
    q_r = np.clip(q_r - crack * 0.38, 0.0, 1.0)
    q_g = np.clip(q_g - crack * 0.42, 0.0, 1.0)
    q_b = np.clip(q_b - crack * 0.10, 0.0, 1.0)

    ref[:, :, 0] = np.where(quay_zone, q_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(quay_zone, q_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(quay_zone, q_b, ref[:, :, 2])

    # ── Three fishing boats (foreground, on the water/quay boundary) ──────────
    # Boat 1: cadmium orange -- center-left
    b1_x0, b1_x1 = int(0.30 * W), int(0.48 * W)
    b1_y0, b1_y1 = int(0.56 * H), int(0.76 * H)
    # Hull (lower 40% of boat zone)
    bh1_y0 = int(0.62 * H)
    ref[bh1_y0:b1_y1, b1_x0:b1_x1, 0] = 0.92
    ref[bh1_y0:b1_y1, b1_x0:b1_x1, 1] = 0.44
    ref[bh1_y0:b1_y1, b1_x0:b1_x1, 2] = 0.08
    # Deck/upper structure: slightly lighter warm amber
    ref[b1_y0:bh1_y0, b1_x0:b1_x1, 0] = 0.82
    ref[b1_y0:bh1_y0, b1_x0:b1_x1, 1] = 0.66
    ref[b1_y0:bh1_y0, b1_x0:b1_x1, 2] = 0.28
    # Boat shadow: deep violet under hull
    ref[b1_y1 - int(0.015 * H):b1_y1, b1_x0:b1_x1, 0] = 0.24
    ref[b1_y1 - int(0.015 * H):b1_y1, b1_x0:b1_x1, 1] = 0.12
    ref[b1_y1 - int(0.015 * H):b1_y1, b1_x0:b1_x1, 2] = 0.42

    # Boat 1 reflection in water (below boat)
    ref_y0 = b1_y0 - int(0.04 * H)
    ref_y1 = b1_y0
    refl_noise = gf(rng.random((ref_y1 - ref_y0, b1_x1 - b1_x0)
                               ).astype(np.float32), sigma=[1, 6])
    ref[ref_y0:ref_y1, b1_x0:b1_x1, 0] = np.clip(0.82 + refl_noise * 0.14 - 0.10, 0.0, 1.0)
    ref[ref_y0:ref_y1, b1_x0:b1_x1, 1] = np.clip(0.36 + refl_noise * 0.12 - 0.10, 0.0, 1.0)
    ref[ref_y0:ref_y1, b1_x0:b1_x1, 2] = np.clip(0.10 + refl_noise * 0.10, 0.0, 1.0)

    # Boat 2: cobalt cerulean -- center
    b2_x0, b2_x1 = int(0.50 * W), int(0.68 * W)
    b2_y0, b2_y1 = int(0.58 * H), int(0.78 * H)
    bh2_y0 = int(0.65 * H)
    ref[bh2_y0:b2_y1, b2_x0:b2_x1, 0] = 0.12
    ref[bh2_y0:b2_y1, b2_x0:b2_x1, 1] = 0.40
    ref[bh2_y0:b2_y1, b2_x0:b2_x1, 2] = 0.84
    ref[b2_y0:bh2_y0, b2_x0:b2_x1, 0] = 0.22
    ref[b2_y0:bh2_y0, b2_x0:b2_x1, 1] = 0.56
    ref[b2_y0:bh2_y0, b2_x0:b2_x1, 2] = 0.78
    # Cobalt boat reflection
    ref2_y0 = b2_y0 - int(0.04 * H)
    ref2_y1 = b2_y0
    refl2_noise = gf(rng.random((ref2_y1 - ref2_y0, b2_x1 - b2_x0)
                                ).astype(np.float32), sigma=[1, 6])
    ref[ref2_y0:ref2_y1, b2_x0:b2_x1, 0] = np.clip(0.08 + refl2_noise * 0.10, 0.0, 1.0)
    ref[ref2_y0:ref2_y1, b2_x0:b2_x1, 1] = np.clip(0.30 + refl2_noise * 0.14, 0.0, 1.0)
    ref[ref2_y0:ref2_y1, b2_x0:b2_x1, 2] = np.clip(0.72 + refl2_noise * 0.16, 0.0, 1.0)

    # Boat 3: vivid vermillion -- center-right
    b3_x0, b3_x1 = int(0.72 * W), int(0.90 * W)
    b3_y0, b3_y1 = int(0.60 * H), int(0.80 * H)
    bh3_y0 = int(0.68 * H)
    ref[bh3_y0:b3_y1, b3_x0:b3_x1, 0] = 0.88
    ref[bh3_y0:b3_y1, b3_x0:b3_x1, 1] = 0.14
    ref[bh3_y0:b3_y1, b3_x0:b3_x1, 2] = 0.12
    ref[b3_y0:bh3_y0, b3_x0:b3_x1, 0] = 0.76
    ref[b3_y0:bh3_y0, b3_x0:b3_x1, 1] = 0.36
    ref[b3_y0:bh3_y0, b3_x0:b3_x1, 2] = 0.22
    # Vermillion boat reflection
    ref3_y0 = b3_y0 - int(0.04 * H)
    ref3_y1 = b3_y0
    refl3_noise = gf(rng.random((ref3_y1 - ref3_y0, b3_x1 - b3_x0)
                                ).astype(np.float32), sigma=[1, 6])
    ref[ref3_y0:ref3_y1, b3_x0:b3_x1, 0] = np.clip(0.78 + refl3_noise * 0.14, 0.0, 1.0)
    ref[ref3_y0:ref3_y1, b3_x0:b3_x1, 1] = np.clip(0.10 + refl3_noise * 0.10, 0.0, 1.0)
    ref[ref3_y0:ref3_y1, b3_x0:b3_x1, 2] = np.clip(0.12 + refl3_noise * 0.12, 0.0, 1.0)

    # Masts (thin vertical lines on the three boats)
    for (mx, my0, my1) in [
        (int(0.39 * W), int(0.36 * H), int(0.62 * H)),  # boat 1 mast
        (int(0.59 * W), int(0.34 * H), int(0.64 * H)),  # boat 2 mast
        (int(0.81 * W), int(0.38 * H), int(0.66 * H)),  # boat 3 mast
    ]:
        mw = max(2, int(0.003 * W))
        mx0 = max(0, mx - mw // 2)
        mx1 = min(W, mx + mw // 2 + 1)
        ref[my0:my1, mx0:mx1, 0] = 0.44
        ref[my0:my1, mx0:mx1, 1] = 0.28
        ref[my0:my1, mx0:mx1, 2] = 0.16

    # ── Final softening pass ──────────────────────────────────────────────────
    ref[:, :, 0] = gf(ref[:, :, 0], sigma=1.2).astype(np.float32)
    ref[:, :, 1] = gf(ref[:, :, 1], sigma=1.2).astype(np.float32)
    ref[:, :, 2] = gf(ref[:, :, 2], sigma=1.2).astype(np.float32)

    ref = np.clip(ref, 0.0, 1.0)
    return ref


# ── Build reference ───────────────────────────────────────────────────────────
print("Building procedural reference (Collioure harbour)...")
ref = build_reference()

ref_uint8 = (ref * 255).astype(np.uint8)
Image.fromarray(ref_uint8).save("s285_reference.png")
print("Reference saved: s285_reference.png")

# ── Painting pipeline ─────────────────────────────────────────────────────────
print("Initialising painter...")
p = Painter(W, H, seed=SEED)

ref_u8 = (ref * 255).astype(np.uint8)

# Ground: raw linen / near-white Derain ground
print("Tone ground...")
p.tone_ground(color=(0.92, 0.88, 0.76), texture_strength=0.018)

# Underpainting: broad tonal structure
print("Underpainting...")
p.underpainting(ref_u8, stroke_size=54, n_strokes=250, dry_amount=0.58)

# Block in: broad colour masses (Derain worked fast and broad)
print("Block in (broad)...")
p.block_in(ref_u8, stroke_size=32, n_strokes=460, dry_amount=0.50)
print("Block in (medium)...")
p.block_in(ref_u8, stroke_size=20, n_strokes=500, dry_amount=0.46)

# Build form: modelling the harbour architecture and boats
print("Build form (medium)...")
p.build_form(ref_u8, stroke_size=12, n_strokes=520, dry_amount=0.42)
print("Build form (fine)...")
p.build_form(ref_u8, stroke_size=6, n_strokes=440, dry_amount=0.36)

# Place lights: vivid highlights on boat hulls, water flashes, roof ridges
print("Place lights...")
p.place_lights(ref_u8, stroke_size=4, n_strokes=300)

# ── s285 improvement: Frequency Separation ───────────────────────────────────
print("Frequency Separation (s285 improvement)...")
p.paint_frequency_separation_pass(
    low_sigma=16.0,
    sat_boost=0.42,
    lum_contrast=0.52,
    recombine_weight=0.70,
    opacity=0.78,
)

# ── s285 artist pass: Derain Fauve Intensity (196th mode) ────────────────────
print("Derain Fauve Intensity (196th mode)...")
p.derain_fauve_intensity_pass(
    sat_gamma=0.60,
    sector_strength=0.28,
    local_sigma=14.0,
    contrast_amplify=0.48,
    angle_strength=0.20,
    light_angle_deg=220.0,
    warm_r=0.94,
    warm_g=0.76,
    warm_b=0.36,
    cool_r=0.28,
    cool_g=0.48,
    cool_b=0.88,
    opacity=0.80,
)

# ── s284 improvement: Chromatic Shadow Shift ──────────────────────────────────
print("Chromatic Shadow Shift (s284 improvement)...")
p.paint_chromatic_shadow_shift_pass(
    shadow_thresh=0.38,
    shadow_range=0.14,
    shadow_hue_shift=22.0,
    highlight_thresh=0.70,
    highlight_range=0.14,
    highlight_hue_shift=10.0,
    shift_strength=0.72,
    opacity=0.65,
)

# ── Final output ──────────────────────────────────────────────────────────────
output_path = "s285_collioure_harbor.png"
p.save(output_path)
print(f"Saved: {output_path}")
