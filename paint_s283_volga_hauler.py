"""Session 283: Ilya Repin -- 'The Hauler's Path at Sunset'

SUBJECT & COMPOSITION:
The Volga River at golden hour, seen from the high near bank looking east across
the water. The towpath — the worn clay track where barge haulers once pulled their
ropes — runs diagonally from the lower-left foreground into the middle distance,
tracing the bank edge. The composition divides into three bands: a warm, textured
foreground bank of baked clay and dry grass; the vast silver-gold river surface
in the middle ground, catching the last oblique rays of the setting sun; and above
it, a towering Russian sky — amber-ochre at the horizon where the sun descends,
deepening through violet-rose to deep cerulean-grey overhead.

THE ENVIRONMENT:
The near bank (foreground): hard-packed clay in warm raw sienna and ochre, scored
by the deep grooves of rope-drag and foot traffic. A coil of tarred rope lies at
the right foreground, with two short iron spikes driven into the clay beside it —
the tools of the hauler's trade. Dry summer grass grows at the bank's crumbling
edge, bleached straw-gold. The transition from bank to water is abrupt: a low
clay cliff of perhaps half a meter, its shadow falling cool violet-grey onto the
water below.

The river (middle ground): the Volga in late summer, broad and slow. The center
of the river catches the setting sun in a long horizontal band of near-white
gold — the light column that stretches from the far shore to the near bank.
On either side of this column the water darkens: deep grey-green in the shadows
to the left, violet-grey to the right. Three distant barges — low, dark, barely
visible — move slowly upriver in the middle distance, their shapes silhouetted
against the lit water column. A faint mist rises from the river's warm surface
into the cooler air above.

The sky (upper half): the greatest element in the composition. A vast, sweeping
Russian sky. At the horizon, warm amber-orange — the sun just below frame —
bleeds up through ochre-gold into warm rose. Above that, the temperature shifts:
cool violet-rose transitions to deep cerulean-grey at the zenith. Three or four
large cumulus clouds catch the warm underlight on their lower faces while their
tops disappear into the cooler blue. The clouds are painted loosely, with broad
gestural strokes, not laboriously rendered — the sky is mood, not documentation.

TECHNIQUE & PALETTE:
Ilya Repin's realist oil method applied to landscape: direct, confident strokes
following the form of each zone. The sky receives horizontal, slightly curved
strokes following the dome of the atmosphere. The river receives long horizontal
strokes following the current direction. The bank receives shorter, more varied
strokes following the irregular clay texture.

Dominant palette: warm ochre-sienna (foreground bank), chalk-cream and warm gold
(lit river), deep grey-green and violet (shadowed water), amber-orange and rose
(low sky), cool cerulean and blue-grey (upper sky), dark umber silhouettes (barges
and far bank). The characteristic Repin temperature dialogue: warm earth against
cool sky, warm lit water against cool shadowed water.

MOOD & INTENT:
The barge haulers are absent from frame — but their presence saturates every
element. The towpath exists only because their bodies wore it into the earth.
The rope coil and iron spikes are the residue of their labor. The river they
pulled against still moves, indifferent and powerful. The painting inhabits
the same emotional territory as Repin's great canvases: the weight of ordinary
human struggle against indifferent nature, witnessed without sentimentality and
without hierarchy, simply seen in its full gravity and beauty.

ARTIST: Ilya Yefimovich Repin (1844-1930), Ukrainian-Russian, Peredvizhniki.
NEW PASSES: repin_character_depth_pass (194th mode) + paint_form_curvature_tint_pass (improvement)
"""

import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image, ImageFilter

from stroke_engine import Painter

# ── Canvas dimensions ─────────────────────────────────────────────────────────
W, H = 1440, 1040   # landscape format: wide river panorama

# ── Procedural reference: Volga at sunset ─────────────────────────────────────

def build_reference(w: int, h: int) -> np.ndarray:
    """
    Build a landscape reference:
      top 55%   → sky (amber horizon → cerulean zenith)
      next 8%   → far bank (dark treeline silhouette)
      next 25%  → river (lit column centre, dark flanks)
      bottom 12% → near bank (warm clay, dry grass)
    """
    rng = np.random.default_rng(283)
    ref = np.zeros((h, w, 3), dtype=np.float32)

    sky_h    = int(h * 0.55)
    bank_h   = int(h * 0.08)
    river_h  = int(h * 0.25)
    fore_h   = h - sky_h - bank_h - river_h

    Y = np.arange(h, dtype=np.float32)

    # ── SKY: horizon amber → midsky rose-violet → zenith blue-grey ──────────
    # Gradient: row 0=zenith (top), row sky_h-1=horizon (bottom of sky)
    for row in range(sky_h):
        t = row / max(sky_h - 1, 1)   # 0=zenith, 1=horizon
        # zenith: cool cerulean-grey (0.42, 0.52, 0.72)
        # mid:    violet-rose (0.72, 0.52, 0.64)
        # horizon: amber-gold (0.92, 0.70, 0.38)
        if t < 0.5:
            s = t / 0.5
            r = 0.42 + s * (0.72 - 0.42)
            g = 0.52 + s * (0.52 - 0.52)
            b = 0.72 + s * (0.64 - 0.72)
        else:
            s = (t - 0.5) / 0.5
            r = 0.72 + s * (0.94 - 0.72)
            g = 0.52 + s * (0.72 - 0.52)
            b = 0.64 + s * (0.34 - 0.64)
        noise = (rng.random(w).astype(np.float32) - 0.5) * 0.018
        ref[row, :, 0] = np.clip(r + noise, 0, 1)
        ref[row, :, 1] = np.clip(g + noise * 0.6, 0, 1)
        ref[row, :, 2] = np.clip(b + noise * 0.4, 0, 1)

    # ── CLOUD MASSES: 3 large soft clouds in sky zone ────────────────────────
    cloud_defs = [
        dict(cy=int(sky_h * 0.30), cx=int(w * 0.25), rx=int(w * 0.18), ry=int(sky_h * 0.12),
             r=0.88, g=0.80, b=0.72),  # warm-lit base
        dict(cy=int(sky_h * 0.20), cx=int(w * 0.65), rx=int(w * 0.22), ry=int(sky_h * 0.10),
             r=0.84, g=0.76, b=0.80),  # rose-tinted
        dict(cy=int(sky_h * 0.40), cx=int(w * 0.80), rx=int(w * 0.12), ry=int(sky_h * 0.08),
             r=0.90, g=0.82, b=0.64),  # warm amber-base cloud
    ]
    Y_sky, X_sky = np.mgrid[:sky_h, :w]
    for cd in cloud_defs:
        dist = np.sqrt(((X_sky - cd['cx']) / cd['rx']) ** 2 +
                       ((Y_sky - cd['cy']) / cd['ry']) ** 2)
        alpha = np.clip(1.2 - dist, 0.0, 1.0).astype(np.float32)
        alpha = alpha ** 1.5
        noise_c = (rng.random((sky_h, w)).astype(np.float32) - 0.5) * 0.04
        alpha = np.clip(alpha + noise_c * alpha, 0.0, 1.0)
        ref[:sky_h, :, 0] += alpha * (cd['r'] - ref[:sky_h, :, 0])
        ref[:sky_h, :, 1] += alpha * (cd['g'] - ref[:sky_h, :, 1])
        ref[:sky_h, :, 2] += alpha * (cd['b'] - ref[:sky_h, :, 2])
    ref[:sky_h] = np.clip(ref[:sky_h], 0, 1)

    # ── FAR BANK: dark treeline silhouette ────────────────────────────────────
    row0 = sky_h
    row1 = sky_h + bank_h
    for col in range(w):
        # Irregular treeline height with sine variation
        tree_variation = (np.sin(col * 0.03) * 0.3 + np.sin(col * 0.007) * 0.7) * 0.5 + 0.5
        tree_h = int(bank_h * (0.4 + tree_variation * 0.6))
        # Fill dark umber-green for trees
        for row in range(row0, row1):
            depth = (row - row0) / bank_h
            if depth < (1.0 - tree_h / bank_h):
                # Sky showing through upper gaps
                sky_frac = 1.0 - depth * bank_h / max(tree_h, 1)
                ref[row, col, :] = ref[row0 - 1, col, :] * sky_frac + \
                    np.array([0.18, 0.20, 0.18]) * (1 - sky_frac)
            else:
                # Dark treeline: deep umber-green
                ref[row, col, 0] = 0.14 + rng.random() * 0.04
                ref[row, col, 1] = 0.16 + rng.random() * 0.04
                ref[row, col, 2] = 0.13 + rng.random() * 0.03

    # ── RIVER: lit column at centre, dark flanks, cool shadow ────────────────
    row0 = sky_h + bank_h
    row1 = row0 + river_h
    x_vals = np.arange(w, dtype=np.float32)
    # Lit column centred at ~55% width (angled sun reflection)
    lit_centre = w * 0.52
    lit_sigma  = w * 0.14
    lit_column = np.exp(-0.5 * ((x_vals - lit_centre) / lit_sigma) ** 2)
    for row in range(row0, row1):
        depth = (row - row0) / river_h  # 0=top (far bank), 1=bottom (near bank)
        # Base river colour: cool grey-green, darker at flanks
        base_r = 0.34 + depth * 0.06
        base_g = 0.38 + depth * 0.04
        base_b = 0.42 + depth * 0.02
        # Lit column: warm near-white gold
        lit_r = 0.90 + depth * 0.04
        lit_g = 0.84 + depth * 0.02
        lit_b = 0.62
        noise_r = (rng.random(w).astype(np.float32) - 0.5) * 0.025
        ref[row, :, 0] = np.clip(base_r + lit_column * (lit_r - base_r) + noise_r, 0, 1)
        ref[row, :, 1] = np.clip(base_g + lit_column * (lit_g - base_g) + noise_r * 0.8, 0, 1)
        ref[row, :, 2] = np.clip(base_b + lit_column * (lit_b - base_b) + noise_r * 0.5, 0, 1)

    # Barges: 3 small dark shapes in mid-river
    barge_defs = [
        dict(cx=int(w * 0.28), cy=int((row0 + row1) / 2) - 8, bw=80, bh=12),
        dict(cx=int(w * 0.44), cy=int((row0 + row1) / 2) + 4, bw=100, bh=14),
        dict(cx=int(w * 0.62), cy=int((row0 + row1) / 2) - 4, bw=65, bh=10),
    ]
    for bd in barge_defs:
        r0b = bd['cy'] - bd['bh'] // 2
        r1b = bd['cy'] + bd['bh'] // 2
        c0b = bd['cx'] - bd['bw'] // 2
        c1b = bd['cx'] + bd['bw'] // 2
        r0b = max(row0, r0b); r1b = min(row1, r1b)
        c0b = max(0, c0b);    c1b = min(w, c1b)
        ref[r0b:r1b, c0b:c1b, :] = 0.12

    # ── FOREGROUND BANK: warm ochre clay, dry grass, rope coil ───────────────
    row0 = row1
    for row in range(row0, h):
        depth = (row - row0) / max(h - row0, 1)  # 0=top of bank, 1=bottom
        # Base: warm raw sienna ochre, darker toward bottom
        base_r = 0.62 + depth * 0.08
        base_g = 0.46 + depth * 0.04
        base_b = 0.24 + depth * 0.02
        noise_f = (rng.random(w).astype(np.float32) - 0.5) * 0.06
        # Grass streaks at bank edge (top of foreground)
        grass_fade = np.clip(1.0 - depth * 4, 0, 1)
        grass_r = 0.58; grass_g = 0.52; grass_b = 0.28
        ref[row, :, 0] = np.clip(base_r + (grass_r - base_r) * grass_fade + noise_f, 0, 1)
        ref[row, :, 1] = np.clip(base_g + (grass_g - base_g) * grass_fade + noise_f * 0.8, 0, 1)
        ref[row, :, 2] = np.clip(base_b + (grass_b - base_b) * grass_fade + noise_f * 0.5, 0, 1)

    # Towpath groove: diagonal dark line from lower-left
    for row in range(row0 + int((h - row0) * 0.2), h):
        col_centre = int(w * 0.25 + (row - row0) * 0.6)
        for dc in range(-6, 7):
            col = col_centre + dc
            if 0 <= col < w:
                groove_alpha = max(0, 1.0 - abs(dc) / 6.0) * 0.45
                ref[row, col, 0] *= (1 - groove_alpha * 0.4)
                ref[row, col, 1] *= (1 - groove_alpha * 0.4)
                ref[row, col, 2] *= (1 - groove_alpha * 0.3)

    # Rope coil: dark circular shape at right foreground
    coil_cy = row0 + int((h - row0) * 0.55)
    coil_cx = int(w * 0.78)
    Y_fore, X_fore = np.mgrid[row0:h, :w]
    dist_coil = np.sqrt((X_fore - coil_cx) ** 2 + (Y_fore - coil_cy) ** 2)
    coil_alpha = np.clip(1.0 - (dist_coil - 28) / 18.0, 0.0, 1.0)
    inner_clear = np.clip((dist_coil - 12) / 8.0, 0.0, 1.0)
    coil_mask = (coil_alpha * inner_clear).astype(np.float32)
    ref[row0:h, :, 0] = np.clip(ref[row0:h, :, 0] * (1 - coil_mask * 0.7), 0, 1)
    ref[row0:h, :, 1] = np.clip(ref[row0:h, :, 1] * (1 - coil_mask * 0.7), 0, 1)
    ref[row0:h, :, 2] = np.clip(ref[row0:h, :, 2] * (1 - coil_mask * 0.6), 0, 1)

    # ── Soft global blur for painting-like reference ──────────────────────────
    ref_pil = Image.fromarray((ref * 255).astype(np.uint8))
    ref_pil = ref_pil.filter(ImageFilter.GaussianBlur(radius=1.5))
    ref = np.array(ref_pil).astype(np.uint8)

    return ref


print("Building procedural reference: Volga at sunset...")
ref = build_reference(W, H)
print(f"Reference: {ref.shape}, range [{ref.min()}, {ref.max()}]")

# Save reference for inspection
Image.fromarray(ref).save("s283_ref.png")

# ── Painter ───────────────────────────────────────────────────────────────────
print("Initializing painter...")
p = Painter(W, H, seed=283)

# ── Toned ground ──────────────────────────────────────────────────────────────
print("Laying toned ground...")
p.tone_ground(color=(0.48, 0.36, 0.22), texture_strength=0.022)

# ── Underpainting ─────────────────────────────────────────────────────────────
print("Underpainting...")
p.underpainting(ref, stroke_size=54, n_strokes=250)
p.underpainting(ref, stroke_size=38, n_strokes=260)

# ── Block in: broad masses ────────────────────────────────────────────────────
print("Blocking in broad masses...")
p.block_in(ref, stroke_size=34, n_strokes=480)
p.block_in(ref, stroke_size=20, n_strokes=510)

# ── Build form: modelling ─────────────────────────────────────────────────────
print("Building form...")
p.build_form(ref, stroke_size=13, n_strokes=540)
p.build_form(ref, stroke_size=6,  n_strokes=440)

# ── Place lights and accents ──────────────────────────────────────────────────
print("Placing lights...")
p.place_lights(ref, stroke_size=4, n_strokes=310)
p.place_lights(ref, stroke_size=3, n_strokes=290)

# ── Repin character depth pass (194th mode) ───────────────────────────────────
print("Applying Repin Character Depth pass (194th mode)...")
p.repin_character_depth_pass(
    gradient_sigma=1.4,
    form_blur_sigma=2.2,
    form_blend=0.26,
    mid_lo=0.30,
    mid_hi=0.62,
    mid_r=0.70,
    mid_g=0.50,
    mid_b=0.32,
    mid_strength=0.24,
    shadow_thresh=0.32,
    shadow_r=0.28,
    shadow_g=0.28,
    shadow_b=0.48,
    shadow_strength=0.22,
    edge_percentile=72.0,
    edge_sharp_sigma=1.1,
    edge_sharp_amount=0.50,
    opacity=0.82,
)

# ── Form curvature tint pass (s283 improvement) ───────────────────────────────
print("Applying Form Curvature Tint pass (s283 improvement)...")
p.paint_form_curvature_tint_pass(
    smooth_sigma=10.0,
    convex_r=0.90,
    convex_g=0.82,
    convex_b=0.60,
    convex_strength=0.18,
    concave_r=0.52,
    concave_g=0.56,
    concave_b=0.74,
    concave_strength=0.14,
    curvature_sigma=2.0,
    curvature_percentile=80.0,
    opacity=0.72,
)

# ── contre-jour rim for the low-angle sunset light ────────────────────────────
print("Applying contre-jour rim pass...")
p.paint_contre_jour_rim_pass(
    bright_threshold=0.72,
    dark_threshold=0.38,
    rim_sigma=4.0,
    rim_strength=0.46,
    rim_r=0.96,
    rim_g=0.74,
    rim_b=0.36,
    cool_edge_strength=0.24,
    cool_edge_r=0.50,
    cool_edge_g=0.58,
    cool_edge_b=0.82,
    opacity=0.68,
)

# ── Shadow temperature ────────────────────────────────────────────────────────
print("Applying shadow temperature pass...")
p.paint_shadow_temperature_pass(
    warm_shadow_color=(0.50, 0.36, 0.16),
    cool_shadow_color=(0.28, 0.30, 0.52),
    warm_highlight_color=(0.96, 0.82, 0.52),
    cool_highlight_color=(0.68, 0.80, 0.96),
    shadow_strength=0.28,
    opacity=0.58,
)

# ── Lost and found edges ──────────────────────────────────────────────────────
print("Applying lost and found edges...")
p.paint_lost_found_edges_pass()

# ── Save ──────────────────────────────────────────────────────────────────────
output = "s283_volga_hauler.png"
p.save(output)
print(f"\nSaved: {output}")
print("Session 283 complete -- The Hauler's Path at Sunset (Ilya Repin / 194th mode)")
