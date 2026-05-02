"""Session 286 -- Eugène Carrière (197th mode)
carriere_smoky_reverie_pass + paint_tonal_rebalance_pass

Subject & Composition:
    "The Canal at Dusk" -- a solitary woman stands at the stone edge of a
    narrow urban canal, viewed from slightly behind and to her left. The
    composition is portrait-oriented: the figure occupies the lower-center
    third, her back to the viewer, standing very still as if absorbed in
    thought. The canal runs horizontally across the middle of the frame,
    its dark water catching broken amber reflections from gas lamps and
    lit windows on the far bank. The far-bank buildings rise as dark
    irregular masses in the upper half, their windows warm against the
    evening. Bare pollarded willows on the far bank arc their tracery
    of branches against the grey sky. The foreground is wet cobblestones,
    rain-slick, picking up the amber reflections of the single gas lamp
    visible at the upper right.

The Figure:
    A woman in a long dark coat, slightly hunched against the cold. She
    holds a loose bunch of cut irises at her side, their petals barely
    visible against the dark coat -- a detail that rewards close looking.
    Her felt hat brim curves slightly over her hair. Her posture is one
    of chosen stillness, not sadness: she has stopped here deliberately,
    looking at the water, pausing in the city's anonymous evening.
    Emotional state: contemplative, at peace with solitude. The viewer
    senses she has been walking and has stopped simply to look at the water.

The Environment:
    SKY: A narrow strip of warm amber-grey sky at the top, the city glow
    just visible before the darkness deepens. No visible stars -- the sky
    is overcast, diffuse, the kind of grey that holds the last of evening.

    CANAL: The water is dark (near-black with the ambient) except where
    gas-lamp light creates a smear of amber on the surface -- broken by
    the gentle movement of the water into irregular comma-shapes of warm
    gold. The far bank reflection adds a series of vertical amber columns
    that waver and dissipate toward the near bank. The water carries a
    suggestion of depth: cool blue-black in shadow, warm amber in the
    lamp-lit zones.

    FAR-BANK BUILDINGS: Low stone tenements, three or four storeys, their
    facades dark umber-grey, windows lit from within in warm amber. Six to
    eight windows visible, each a small rectangle of warm light. Between
    buildings, narrow dark passages. The edges of the buildings are soft --
    they blur into the dusky sky, the roofline barely distinguishable from
    the heavy grey above.

    WILLOWS: Two or three pollarded willows on the far bank, their trunks
    dark, their branching silhouettes radiating upward into the grey sky.
    The branches are fine, dark against the near-white sky, the tree forms
    occupying the left side of the composition and providing the composition's
    primary vertical counterpoint to the horizontal canal.

    FOREGROUND: Wet cobblestones, dark and reflective. The gas lamp on the
    right casts a cone of warm amber light that pools on the near bank and
    catches the wet stones in patches. The edge of the canal (a low stone
    lip) defines the boundary between near and far. The woman stands on
    this lip, looking down and across.

Technique & Palette:
    Eugène Carrière's smoky reverie technique -- warm monochromatic
    bistre-brown palette with forms emerging from warm darkness. The
    carriere_smoky_reverie_pass enforces the luminance-scaled sepia tint,
    exponential shadow merge toward deep warm umber, gradient-magnitude
    soft edge dissolution, and peripheral edge fade.
    The paint_tonal_rebalance_pass applies percentile auto-levels stretch
    and hyperbolic tangent S-curve contrast shaping.
    Palette: deep warm umber, amber-bistre, warm near-dark, lamp amber,
    pale warm near-white at lamp highlights. No cool tones; even the
    canal's dark water carries warmth.

Mood & Intent:
    The painting explores the beauty of the city in its private hours --
    the moment when a life pauses in public space without demand or
    expectation. The viewer should feel the quality of urban solitude:
    not loneliness, but the deep comfort of being anonymous in a city
    that continues around you. The mist softens everything; the Carrière
    technique makes the familiar strange. The canal becomes a mirror not
    of the buildings across it but of the woman's interior state --
    dark, still, lit from within. The irises she carries are a private
    gesture: beauty chosen for no audience.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stroke_engine import Painter

# ── Canvas dimensions ────────────────────────────────────────────────────────
W, H = 1040, 1440   # portrait -- standing figure, canal scene
SEED = 286

# ── Reference: procedural canal-at-dusk scene ────────────────────────────────

def build_reference() -> np.ndarray:
    """Construct a warm, dusky urban canal reference in Carriere tones."""
    from scipy.ndimage import gaussian_filter as gf
    rng = np.random.default_rng(SEED)

    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys  = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    xs  = np.linspace(0.0, 1.0, W, dtype=np.float32)[None, :]

    # ── Sky (top 20%) ─────────────────────────────────────────────────────────
    sky_frac = 0.18
    sky_zone = ys < sky_frac
    sk_t = np.clip(ys / (sky_frac + 0.01), 0.0, 1.0)  # 0=top, 1=horizon
    sky_r = np.clip(0.54 + sk_t * 0.18, 0.0, 1.0)
    sky_g = np.clip(0.42 + sk_t * 0.14, 0.0, 1.0)
    sky_b = np.clip(0.22 + sk_t * 0.10, 0.0, 1.0)
    # Sky is overcast, dull -- dim it
    sky_r = sky_r * 0.62
    sky_g = sky_g * 0.54
    sky_b = sky_b * 0.46
    ref[:, :, 0] = np.where(sky_zone, sky_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(sky_zone, sky_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(sky_zone, sky_b, ref[:, :, 2])

    # ── Far-bank buildings (20%-52%) ──────────────────────────────────────────
    bldg_y0, bldg_y1 = sky_frac, 0.52
    bldg_zone = (ys >= bldg_y0) & (ys < bldg_y1)

    # Base: dark warm umber-grey facade
    bd_noise = gf(rng.random((H, W)).astype(np.float32), sigma=8)
    bd_r = np.clip(0.22 + bd_noise * 0.08, 0.0, 1.0)
    bd_g = np.clip(0.16 + bd_noise * 0.06, 0.0, 1.0)
    bd_b = np.clip(0.10 + bd_noise * 0.04, 0.0, 1.0)
    ref[:, :, 0] = np.where(bldg_zone, bd_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(bldg_zone, bd_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(bldg_zone, bd_b, ref[:, :, 2])

    # Lit windows: warm amber rectangles
    window_specs = [
        (0.22, 0.27, 0.08, 0.14),   # left group, upper row
        (0.22, 0.27, 0.22, 0.28),
        (0.28, 0.34, 0.06, 0.12),   # left group, lower row
        (0.28, 0.34, 0.18, 0.24),
        (0.22, 0.27, 0.48, 0.54),   # center group
        (0.22, 0.27, 0.62, 0.68),
        (0.28, 0.34, 0.52, 0.58),
        (0.28, 0.34, 0.72, 0.78),
        (0.22, 0.27, 0.82, 0.88),   # right group
        (0.28, 0.34, 0.86, 0.92),
        (0.36, 0.42, 0.12, 0.18),   # lower building row
        (0.36, 0.42, 0.38, 0.44),
        (0.36, 0.42, 0.66, 0.72),
    ]
    for (ry0, ry1, rx0, rx1) in window_specs:
        y0, y1 = int(ry0 * H), int(ry1 * H)
        x0, x1 = int(rx0 * W), int(rx1 * W)
        # Warm amber window glow
        wn = gf(rng.random((y1 - y0, x1 - x0)).astype(np.float32), sigma=2)
        ref[y0:y1, x0:x1, 0] = np.clip(0.82 + wn * 0.12, 0.0, 1.0)
        ref[y0:y1, x0:x1, 1] = np.clip(0.58 + wn * 0.10, 0.0, 1.0)
        ref[y0:y1, x0:x1, 2] = np.clip(0.18 + wn * 0.06, 0.0, 1.0)

    # Window glow haloes: diffuse amber around windows
    for (ry0, ry1, rx0, rx1) in window_specs:
        y0, y1 = int(ry0 * H), int(ry1 * H)
        x0, x1 = int(rx0 * W), int(rx1 * W)
        pad = 12
        hy0, hy1 = max(0, y0 - pad), min(H, y1 + pad)
        hx0, hx1 = max(0, x0 - pad), min(W, x1 + pad)
        halo_mask = np.zeros((H, W), dtype=np.float32)
        halo_mask[y0:y1, x0:x1] = 1.0
        halo_mask = gf(halo_mask, sigma=pad * 0.6).astype(np.float32)
        halo_mask = np.clip(halo_mask * 3.0, 0.0, 0.5)
        halo_zone = bldg_zone.squeeze() if bldg_zone.shape != (H, W) else bldg_zone
        ref[:, :, 0] = np.clip(ref[:, :, 0] + halo_mask * 0.28, 0.0, 1.0)
        ref[:, :, 1] = np.clip(ref[:, :, 1] + halo_mask * 0.18, 0.0, 1.0)
        ref[:, :, 2] = np.clip(ref[:, :, 2] + halo_mask * 0.06, 0.0, 1.0)

    # Building separations (dark passages between buildings)
    sep_specs = [
        (0.20, 0.52, 0.34, 0.37),
        (0.20, 0.52, 0.46, 0.49),
        (0.20, 0.52, 0.78, 0.81),
    ]
    for (ry0, ry1, rx0, rx1) in sep_specs:
        y0, y1 = int(ry0 * H), int(ry1 * H)
        x0, x1 = int(rx0 * W), int(rx1 * W)
        ref[y0:y1, x0:x1, 0] = 0.08
        ref[y0:y1, x0:x1, 1] = 0.06
        ref[y0:y1, x0:x1, 2] = 0.04

    # Pollarded willow trunks (left side, behind canal)
    willow_specs = [
        (0.20, 0.52, 0.04, 0.07),   # main left trunk
        (0.20, 0.46, 0.14, 0.16),   # second trunk
    ]
    for (ry0, ry1, rx0, rx1) in willow_specs:
        y0, y1 = int(ry0 * H), int(ry1 * H)
        x0, x1 = int(rx0 * W), int(rx1 * W)
        ref[y0:y1, x0:x1, 0] = 0.12
        ref[y0:y1, x0:x1, 1] = 0.09
        ref[y0:y1, x0:x1, 2] = 0.06

    # Willow branch tracery: fine dark lines in sky
    for cx, base_y in [(int(0.055 * W), int(0.20 * H)), (int(0.15 * W), int(0.22 * H))]:
        for angle_frac in np.linspace(-0.3, 0.3, 12):
            angle = np.pi * (0.35 + angle_frac * 0.5)  # spreading upward
            length = rng.uniform(0.06, 0.14) * H
            dx = int(np.cos(angle) * length)
            dy = -int(abs(np.sin(angle)) * length)
            bw = max(1, int(0.002 * W))
            x_end = np.clip(cx + dx, 0, W - 1)
            y_end = np.clip(base_y + dy, 0, H - 1)
            # Draw thin line via linear interpolation
            n_pts = max(abs(dx), abs(-dy), 1) + 1
            lxs = np.linspace(cx, x_end, n_pts).astype(int)
            lys = np.linspace(base_y, y_end, n_pts).astype(int)
            lxs = np.clip(lxs, 0, W - 1)
            lys = np.clip(lys, 0, H - 1)
            for lx, ly in zip(lxs, lys):
                x0_ = max(0, lx - bw)
                x1_ = min(W, lx + bw + 1)
                ref[ly, x0_:x1_, 0] = 0.10
                ref[ly, x0_:x1_, 1] = 0.08
                ref[ly, x0_:x1_, 2] = 0.05

    # ── Canal / water (52%-62%) ───────────────────────────────────────────────
    canal_y0, canal_y1 = 0.52, 0.62
    canal_zone = (ys >= canal_y0) & (ys < canal_y1)

    # Base: near-black water
    cw_r = np.full((H, W), 0.10, dtype=np.float32)
    cw_g = np.full((H, W), 0.07, dtype=np.float32)
    cw_b = np.full((H, W), 0.05, dtype=np.float32)

    # Amber window reflections in water (vertical smears)
    for (ry0, ry1, rx0, rx1) in window_specs:
        rx_c = (rx0 + rx1) * 0.5
        ref_x0 = max(0, int((rx_c - 0.04) * W))
        ref_x1 = min(W, int((rx_c + 0.04) * W))
        ref_cy0, ref_cy1 = int(canal_y0 * H), int(canal_y1 * H)
        rn = gf(rng.random((ref_cy1 - ref_cy0, ref_x1 - ref_x0)
                           ).astype(np.float32), sigma=[2, 4])
        # Reflection fades with distance from canal top
        fade = np.linspace(0.6, 0.1, ref_cy1 - ref_cy0
                           ).astype(np.float32)[:, None]
        ref[ref_cy0:ref_cy1, ref_x0:ref_x1, 0] = np.clip(
            cw_r[ref_cy0:ref_cy1, ref_x0:ref_x1] + (0.68 + rn * 0.18) * fade, 0.0, 1.0)
        ref[ref_cy0:ref_cy1, ref_x0:ref_x1, 1] = np.clip(
            cw_g[ref_cy0:ref_cy1, ref_x0:ref_x1] + (0.42 + rn * 0.12) * fade, 0.0, 1.0)
        ref[ref_cy0:ref_cy1, ref_x0:ref_x1, 2] = np.clip(
            cw_b[ref_cy0:ref_cy1, ref_x0:ref_x1] + (0.12 + rn * 0.04) * fade, 0.0, 1.0)

    # Gas lamp reflection (right side of canal)
    lamp_cx = int(0.78 * W)
    lamp_y0 = int(canal_y0 * H)
    lamp_y1 = int(canal_y1 * H)
    lamp_xr = 40
    lamp_rn = gf(rng.random((lamp_y1 - lamp_y0, lamp_xr * 2)
                            ).astype(np.float32), sigma=[3, 6])
    lamp_fade = np.linspace(0.9, 0.2, lamp_y1 - lamp_y0).astype(np.float32)[:, None]
    lx0, lx1 = max(0, lamp_cx - lamp_xr), min(W, lamp_cx + lamp_xr)
    ref[lamp_y0:lamp_y1, lx0:lx1, 0] = np.clip(
        cw_r[lamp_y0:lamp_y1, lx0:lx1] + (0.80 + lamp_rn[:, :lx1 - lx0] * 0.12) * lamp_fade,
        0.0, 1.0)
    ref[lamp_y0:lamp_y1, lx0:lx1, 1] = np.clip(
        cw_g[lamp_y0:lamp_y1, lx0:lx1] + (0.52 + lamp_rn[:, :lx1 - lx0] * 0.10) * lamp_fade,
        0.0, 1.0)
    ref[lamp_y0:lamp_y1, lx0:lx1, 2] = np.clip(
        cw_b[lamp_y0:lamp_y1, lx0:lx1] + (0.14 + lamp_rn[:, :lx1 - lx0] * 0.04) * lamp_fade,
        0.0, 1.0)

    ref[:, :, 0] = np.where(canal_zone, cw_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(canal_zone, cw_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(canal_zone, cw_b, ref[:, :, 2])
    # Re-apply reflections on top of base (already written above into cw channels)
    # Use the updated cw arrays
    ref[int(canal_y0 * H):int(canal_y1 * H), :, 0] = cw_r[int(canal_y0 * H):int(canal_y1 * H), :]
    ref[int(canal_y0 * H):int(canal_y1 * H), :, 1] = cw_g[int(canal_y0 * H):int(canal_y1 * H), :]
    ref[int(canal_y0 * H):int(canal_y1 * H), :, 2] = cw_b[int(canal_y0 * H):int(canal_y1 * H), :]

    # ── Canal stone edge / near bank (62%-68%) ────────────────────────────────
    bank_zone = (ys >= canal_y1) & (ys < 0.68)
    bn = gf(rng.random((H, W)).astype(np.float32), sigma=[2, 8])
    bk_r = np.clip(0.28 + bn * 0.08, 0.0, 1.0)
    bk_g = np.clip(0.20 + bn * 0.06, 0.0, 1.0)
    bk_b = np.clip(0.12 + bn * 0.04, 0.0, 1.0)
    # Gas lamp warmth on near stone edge (right side)
    lamp_bank = np.zeros((H, W), dtype=np.float32)
    lamp_bank[:, max(0, lamp_cx - 80):min(W, lamp_cx + 80)] = 1.0
    lamp_bank = gf(lamp_bank, sigma=40).astype(np.float32) * bank_zone.astype(np.float32)
    bk_r = np.clip(bk_r + lamp_bank * 0.32, 0.0, 1.0)
    bk_g = np.clip(bk_g + lamp_bank * 0.18, 0.0, 1.0)
    bk_b = np.clip(bk_b + lamp_bank * 0.04, 0.0, 1.0)
    ref[:, :, 0] = np.where(bank_zone, bk_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(bank_zone, bk_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(bank_zone, bk_b, ref[:, :, 2])

    # ── Gas lamp post (right side, 44%-68%) ──────────────────────────────────
    lamp_post_x0, lamp_post_x1 = int(0.765 * W), int(0.795 * W)
    lamp_post_y0, lamp_post_y1 = int(0.44 * H), int(0.68 * H)
    ref[lamp_post_y0:lamp_post_y1, lamp_post_x0:lamp_post_x1, 0] = 0.20
    ref[lamp_post_y0:lamp_post_y1, lamp_post_x0:lamp_post_x1, 1] = 0.15
    ref[lamp_post_y0:lamp_post_y1, lamp_post_x0:lamp_post_x1, 2] = 0.09
    # Lamp head glowing orb
    lamp_head_cx, lamp_head_cy = int(0.78 * W), int(0.46 * H)
    lamp_head_r = int(0.022 * W)
    Y_, X_ = np.ogrid[:H, :W]
    lamp_mask = ((X_ - lamp_head_cx) ** 2 + (Y_ - lamp_head_cy) ** 2) <= lamp_head_r ** 2
    ref[lamp_mask, 0] = 0.96
    ref[lamp_mask, 1] = 0.82
    ref[lamp_mask, 2] = 0.44
    # Lamp halo diffusion
    lamp_halo = np.zeros((H, W), dtype=np.float32)
    lamp_halo[lamp_mask] = 1.0
    lamp_halo = gf(lamp_halo, sigma=28).astype(np.float32)
    lamp_halo_zone = (ys >= 0.40) & (ys < 0.62)
    ref[:, :, 0] = np.clip(ref[:, :, 0] + lamp_halo * 0.38 * lamp_halo_zone.astype(np.float32),
                            0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + lamp_halo * 0.22 * lamp_halo_zone.astype(np.float32),
                            0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + lamp_halo * 0.06 * lamp_halo_zone.astype(np.float32),
                            0.0, 1.0)

    # ── Wet cobblestone foreground (68%-100%) ─────────────────────────────────
    fg_zone = ys >= 0.68
    cob_noise = gf(rng.random((H, W)).astype(np.float32), sigma=[1.5, 3])
    cob_grid_x = (np.sin(xs * W / 28.0 * np.pi)).astype(np.float32)
    cob_grid_y = (np.sin(ys * H / 18.0 * np.pi)).astype(np.float32)
    cob_grid = np.clip((cob_grid_x * cob_grid_y) * 0.5 + 0.5, 0.0, 1.0).astype(np.float32)
    cobble_r = np.clip(0.18 + cob_noise * 0.07 + cob_grid * 0.04, 0.0, 1.0)
    cobble_g = np.clip(0.13 + cob_noise * 0.05 + cob_grid * 0.03, 0.0, 1.0)
    cobble_b = np.clip(0.08 + cob_noise * 0.03 + cob_grid * 0.02, 0.0, 1.0)
    # Rain puddle reflections on cobblestones -- amber from lamp
    puddle_mask = np.zeros((H, W), dtype=np.float32)
    puddle_mask[lamp_mask] = 1.0
    puddle_mask = gf(puddle_mask, sigma=60).astype(np.float32)
    puddle_mask = np.clip(puddle_mask * 5.0, 0.0, 1.0) * fg_zone.astype(np.float32)
    cobble_r = np.clip(cobble_r + puddle_mask * 0.42, 0.0, 1.0)
    cobble_g = np.clip(cobble_g + puddle_mask * 0.24, 0.0, 1.0)
    cobble_b = np.clip(cobble_b + puddle_mask * 0.06, 0.0, 1.0)
    # Window light reflections on wet stones
    for (ry0, ry1, rx0, rx1) in window_specs[:4]:
        rx_c = (rx0 + rx1) * 0.5
        wref_x0 = max(0, int((rx_c - 0.06) * W))
        wref_x1 = min(W, int((rx_c + 0.06) * W))
        wref_y0, wref_y1 = int(0.72 * H), int(0.88 * H)
        wr_mask = np.zeros((H, W), dtype=np.float32)
        wr_mask[wref_y0:wref_y1, wref_x0:wref_x1] = 0.5
        wr_mask = gf(wr_mask, sigma=22).astype(np.float32) * fg_zone.astype(np.float32)
        cobble_r = np.clip(cobble_r + wr_mask * 0.24, 0.0, 1.0)
        cobble_g = np.clip(cobble_g + wr_mask * 0.14, 0.0, 1.0)
        cobble_b = np.clip(cobble_b + wr_mask * 0.04, 0.0, 1.0)
    ref[:, :, 0] = np.where(fg_zone, cobble_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(fg_zone, cobble_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(fg_zone, cobble_b, ref[:, :, 2])

    # ── Figure: woman, center, 62%-94% ───────────────────────────────────────
    fig_cx = int(0.45 * W)
    fig_y0 = int(0.62 * H)
    fig_y1 = int(0.94 * H)
    fig_w  = int(0.12 * W)
    fig_x0 = max(0, fig_cx - fig_w // 2)
    fig_x1 = min(W, fig_cx + fig_w // 2)

    # Dark coat body
    fn = gf(rng.random((fig_y1 - fig_y0, fig_x1 - fig_x0)).astype(np.float32), sigma=3)
    coat_r = np.clip(0.14 + fn * 0.05, 0.0, 1.0)
    coat_g = np.clip(0.10 + fn * 0.04, 0.0, 1.0)
    coat_b = np.clip(0.07 + fn * 0.03, 0.0, 1.0)
    ref[fig_y0:fig_y1, fig_x0:fig_x1, 0] = coat_r
    ref[fig_y0:fig_y1, fig_x0:fig_x1, 1] = coat_g
    ref[fig_y0:fig_y1, fig_x0:fig_x1, 2] = coat_b

    # Head (hat): small dark oval above coat
    head_cy = int(0.60 * H)
    head_cx = int(0.46 * W)
    head_ry, head_rx = int(0.030 * H), int(0.030 * W)
    Y_h, X_h = np.ogrid[:H, :W]
    head_mask = (((X_h - head_cx) / max(head_rx, 1)) ** 2 +
                 ((Y_h - head_cy) / max(head_ry, 1)) ** 2) <= 1.0
    ref[head_mask, 0] = 0.18
    ref[head_mask, 1] = 0.13
    ref[head_mask, 2] = 0.09

    # Iris bunch (slight warmer dark purple-blue tinge against coat)
    iris_x0, iris_x1 = fig_x1 - int(0.03 * W), min(W, fig_x1 + int(0.02 * W))
    iris_y0, iris_y1 = int(0.80 * H), int(0.90 * H)
    ref[iris_y0:iris_y1, iris_x0:iris_x1, 0] = 0.22
    ref[iris_y0:iris_y1, iris_x0:iris_x1, 1] = 0.16
    ref[iris_y0:iris_y1, iris_x0:iris_x1, 2] = 0.30

    # ── Light interaction: lamp amber on left shoulder of figure ──────────────
    shoulder_mask = np.zeros((H, W), dtype=np.float32)
    shoulder_mask[int(0.62 * H):int(0.72 * H), fig_x1:min(W, fig_x1 + int(0.06 * W))] = 1.0
    shoulder_mask = gf(shoulder_mask, sigma=12).astype(np.float32)
    shoulder_mask = np.clip(shoulder_mask * 2.0, 0.0, 0.4)
    ref[:, :, 0] = np.clip(ref[:, :, 0] + shoulder_mask * 0.28, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + shoulder_mask * 0.14, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + shoulder_mask * 0.03, 0.0, 1.0)

    # ── Global atmosphere: very light warm mist across the whole scene ────────
    mist = gf(rng.random((H, W)).astype(np.float32), sigma=40).astype(np.float32)
    mist = np.clip((mist - 0.40) * 2.0, 0.0, 1.0) * 0.08
    # Mist heavier in middle (canal zone) and above
    mist_fade = np.clip(1.0 - np.abs(ys - 0.45) * 4.0, 0.0, 1.0).astype(np.float32)
    mist = mist * mist_fade
    ref[:, :, 0] = np.clip(ref[:, :, 0] + mist * 0.48, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + mist * 0.36, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + mist * 0.20, 0.0, 1.0)

    # ── Final softening ───────────────────────────────────────────────────────
    for c in range(3):
        ref[:, :, c] = gf(ref[:, :, c], sigma=1.0).astype(np.float32)

    return np.clip(ref, 0.0, 1.0).astype(np.float32)


# ── Build reference ───────────────────────────────────────────────────────────
print("Building procedural reference (canal at dusk)...")
ref = build_reference()

ref_uint8 = (ref * 255).astype(np.uint8)
Image.fromarray(ref_uint8).save("s286_reference.png")
print("Reference saved: s286_reference.png")

# ── Painting pipeline ─────────────────────────────────────────────────────────
print("Initialising painter...")
p = Painter(W, H, seed=SEED)

ref_u8 = (ref * 255).astype(np.uint8)

# Ground: dark warm umber ground (Carriere's characteristic dark base)
print("Tone ground (dark warm umber)...")
p.tone_ground(color=(0.22, 0.16, 0.10), texture_strength=0.022)

# Underpainting: broad tonal structure from deep dark
print("Underpainting...")
p.underpainting(ref_u8, stroke_size=52, n_strokes=260, dry_amount=0.60)
p.underpainting(ref_u8, stroke_size=40, n_strokes=220, dry_amount=0.55)

# Block in: broad warm masses -- Carriere built form through scumbling
print("Block in (broad)...")
p.block_in(ref_u8, stroke_size=34, n_strokes=480, dry_amount=0.52)
print("Block in (medium)...")
p.block_in(ref_u8, stroke_size=22, n_strokes=520, dry_amount=0.48)

# Build form: canal reflections, building texture, figure
print("Build form (medium)...")
p.build_form(ref_u8, stroke_size=13, n_strokes=540, dry_amount=0.44)
print("Build form (fine)...")
p.build_form(ref_u8, stroke_size=6, n_strokes=460, dry_amount=0.38)

# Place lights: gas lamp glows, window highlights, wet cobblestone glints
print("Place lights...")
p.place_lights(ref_u8, stroke_size=4, n_strokes=320)

# ── s286 improvement: Tonal Rebalance ────────────────────────────────────────
print("Tonal Rebalance (s286 improvement)...")
p.paint_tonal_rebalance_pass(
    shadow_percentile=4.0,
    highlight_percentile=94.0,
    curve_sharpness=1.55,
    shoulder_start=0.88,
    max_scale=1.75,
    opacity=0.80,
)

# ── s286 artist pass: Carriere Smoky Reverie (197th mode) ────────────────────
print("Carriere Smoky Reverie (197th mode)...")
p.carriere_smoky_reverie_pass(
    sepia_r=0.58,
    sepia_g=0.44,
    sepia_b=0.28,
    sepia_strength=0.72,
    shadow_tau=0.26,
    shadow_strength=0.55,
    shadow_dark_r=0.12,
    shadow_dark_g=0.08,
    shadow_dark_b=0.05,
    dissolve_sigma=3.0,
    dissolve_strength=0.52,
    border_falloff=3.6,
    border_strength=0.60,
    opacity=0.88,
)

# ── s285 improvement: Frequency Separation ───────────────────────────────────
print("Frequency Separation (s285 improvement)...")
p.paint_frequency_separation_pass(
    low_sigma=14.0,
    sat_boost=0.30,
    lum_contrast=0.42,
    recombine_weight=0.62,
    opacity=0.60,
)

# ── Final output ──────────────────────────────────────────────────────────────
output_path = "s286_canal_dusk.png"
p.save(output_path)
print(f"Saved: {output_path}")
