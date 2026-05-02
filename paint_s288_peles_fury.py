"""Session 288 -- Camille Pissarro (199th mode)
pissarro_divisionist_shimmer_pass + paint_structure_tensor_pass

Subject & Composition:
    "Pele's Fury — Kīlauea at Midnight" — A Hawaiian volcanic eruption viewed from
    a low vantage point on the lava field, looking directly up toward the active
    caldera of Kīlauea. The volcanic cone occupies the center of the canvas, its
    dark triangular silhouette rising from the bottom edge to roughly one-third
    height. The composition is divided into three horizontal registers: the
    foreground lava field (black, glowing cracks), the volcanic cone with its
    channeled flows (dark with rivers of fire), and the sky above (deep indigo
    pierced by the orange-crimson glow of the eruption). The caldera mouth sits
    at the apex of the cone, a circular incandescence that is the brightest point
    in the composition and the source of all warmth and light.

The Figure:
    There is no human figure. The subject is purely elemental: fire, stone, night,
    and the sea. The volcanic cone functions as the compositional protagonist — an
    ancient, autonomous presence that existed before humanity and will continue
    after. If there is an emotional subject, it is Pele herself in the Hawaiian
    tradition: the goddess of volcanoes, neither malevolent nor benevolent, simply
    creative and destructive in equal measure. The caldera glow is her eye; the
    lava flows are her reaching fingers. The emotional state of the volcano is
    not anger but total indifference — the same indifference Pissarro found in the
    French countryside: nature doing what nature does, regardless of who watches.

The Environment:
    SKY: The sky occupies the upper 30% of the canvas. At the zenith, it is deep
    midnight indigo — the color of Hawaii at 2am, far from urban light. Moving
    downward toward the volcanic cone, the sky transitions through navy to deep
    crimson-purple, lit by the glow of the eruption. Approximately 200 stars
    pierce the indigo in the upper quadrants where the glow has not yet reached,
    scattered irregularly, several slightly larger than the rest. No moon. A
    smudge of the Milky Way would be appropriate but is not required. The stars
    are white-blue in the clear sky, transitioning to warm amber-white where the
    eruption glow reaches them. Billowing smoke and ash plumes rise from the
    caldera mouth and drift slowly to the northeast, partially obscuring the
    upper-center sky.

    VOLCANIC CONE: The cone occupies the central 60% of the canvas height
    (approximately y=0.28 to y=0.80). It is a broad, low shield volcano shape —
    Kīlauea is not the steep stratovolcano of popular imagination but a broad,
    gently sloping shield. Dark volcanic rock: not pure black but a very deep
    blue-green-black, the color of fresh basalt seen by firelight. The cone
    surface is essentially featureless except where lava flows interrupt it.
    Three main lava flow channels cross the visible surface: one runs nearly
    straight down the center from the caldera to the cone base; two branch
    diagonally to the left and right about one-third of the way down, like a
    delta dividing. Each flow channel is a river of orange-crimson light against
    the dark rock, brighter and more yellow-white at the center where the lava
    is hottest, darkening to orange and finally rust-red at its cooling margins.
    The flows meander slightly but are essentially laminar — Kīlauea's pahoehoe
    lava moves smoothly.

    CALDERA: The caldera mouth at the summit is a small circular glow, perhaps
    5% of the canvas width. It is the hottest and brightest area: white-yellow
    at the absolute center, immediately transitioning to orange, then crimson,
    then the deep red-black of still-hot but cooling lava at its edge. Around the
    caldera, the volcanic rock takes on a warm amber glow from the reflected heat.

    SEA: The Pacific Ocean occupies narrow strips on either side and at the base
    of the canvas where the cone does not reach. The sea at midnight is very dark —
    near-black — but it holds faint orange reflections of the eruption in
    horizontal bands of rippled light. The transition from black rock to black sea
    is subtle; the separation is given by the slight sheen of the water surface
    versus the matte texture of the lava field.

    FOREGROUND LAVA FIELD: The foreground from y=0.82 to the bottom edge is the
    viewer's immediate ground: a field of cooled aa lava (rough, jagged, clinker-
    like). The surface is very dark — near-black — but crossed by a network of
    fine glowing cracks where the cooled crust has fractured and the still-molten
    interior is visible. These cracks form an irregular web, brightest where widest,
    dimming rapidly away from the crack centers. A few larger fractures near the
    bottom edge are wide enough to show pools of deep orange-red molten lava.

Technique & Palette:
    Camille Pissarro's divisionist shimmer technique applied to volcanic light. The
    pissarro_divisionist_shimmer_pass contributes four transformations: (1) stochastic
    chromatic neighbor blending creates optical color vibration at the interfaces
    between the fire glow and the dark rock — the boundary between crimson and black
    shimmers as Pissarro's forest edges shimmer between sage-green and amber; (2) the
    cool sage-green shadow push finds the shadow zones of the dark rock and gives them
    a subtly cool, greenish undertone rather than pure black — the same technique
    Pissarro used to keep his shadow zones alive rather than dead; (3) the warm amber
    highlight push enriches the caldera glow and the lava channel centers with
    Pissarro's characteristic straw-gold warmth; (4) sector-median hue coherence
    unifies the reds and oranges of the fire into coherent families, preventing
    scattered disconnected color notes.

    Palette: deep indigo-black (sky/sea/rock), deep crimson (glow horizon), orange
    (lava channels), yellow-white (caldera center), cool sage-green (rock shadows),
    warm amber (reflected firelight), grey-smoke (ash plume). Every dark mass is
    never pure neutral black — it carries either the cool blue-green of volcanic
    basalt or the warm orange reflection of fire.

Mood & Intent:
    The painting intends to place the viewer inside something larger and older than
    human civilization. Kīlauea has been erupting continuously since 1983; it has
    added new coastline to the Big Island of Hawaii. It is not a disaster. It is
    creation. The lava flows do not destroy — they extend the land. The mood is one
    of awe without terror: the feeling of standing at the origin point of stone, at
    the place where the Earth makes new material from its own interior. Pissarro's
    divisionist technique, applied here, is meant to render the volcano not as a
    dramatic spectacle but as a living system — the same patient optical attention
    he brought to a peasant field in Normandy applied to a field of fire in the
    Pacific. The viewer should feel simultaneously very small (the volcano is
    incomprehensibly larger) and very alive (this is where the world comes from).
    The stars above should reinforce this: the same universe that made the stars
    made this fire. Paint with patience and practice, like a true artist.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stroke_engine import Painter

# ── Canvas dimensions ────────────────────────────────────────────────────────
W, H = 1440, 1040   # landscape -- volcanic panorama
SEED = 288
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s288_peles_fury.png")


# ── Reference: procedural Kīlauea volcanic night scene ───────────────────────

def build_reference() -> np.ndarray:
    """Procedural volcanic night reference.

    Zones:
      0.00-0.30 : sky (deep indigo top → crimson near cone)
      0.28-0.80 : volcanic cone (dark shield, lava flows, caldera)
      0.78-1.00 : sea (dark, reflection bands) and foreground lava field
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    yf = yy.astype(np.float32) / H
    xf = xx.astype(np.float32) / W

    # Summit / caldera position
    cx = 0.50
    cy = 0.28

    # ── 1. Sky background ────────────────────────────────────────────────────
    # Deep indigo at top, darkening toward bottom (darkness of the horizon)
    sky_grad = np.clip(1.0 - yf * 1.8, 0.0, 1.0).astype(np.float32)
    ref[:, :, 0] = 0.015 + 0.025 * sky_grad
    ref[:, :, 1] = 0.015 + 0.020 * sky_grad
    ref[:, :, 2] = 0.06  + 0.10  * sky_grad

    # Caldera glow spread across sky (orange-red)
    gd = np.sqrt((xf - cx) ** 2 + (yf - cy) ** 2 * 1.8).astype(np.float32)
    glow_sky_r = np.clip(0.55 * np.exp(-gd / 0.22), 0.0, 1.0).astype(np.float32)
    glow_sky_g = np.clip(0.22 * np.exp(-gd / 0.15), 0.0, 1.0).astype(np.float32)
    glow_sky_b = np.clip(0.04 * np.exp(-gd / 0.09), 0.0, 1.0).astype(np.float32)
    ref[:, :, 0] = np.clip(ref[:, :, 0] + glow_sky_r * 0.65, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + glow_sky_g * 0.42, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + glow_sky_b * 0.22, 0.0, 1.0)

    # ── 2. Stars ─────────────────────────────────────────────────────────────
    rng = np.random.default_rng(SEED)
    n_stars = 220
    s_y = rng.integers(0, int(H * 0.55), n_stars)
    s_x = rng.integers(0, W, n_stars)
    s_b = rng.uniform(0.45, 0.95, n_stars)
    # temperature: cool stars blue-white, warm stars amber-white
    s_t = rng.uniform(0.0, 1.0, n_stars)
    for sy, sx, sb, st in zip(s_y, s_x, s_b, s_t):
        if gd[sy, sx] < 0.12:   # skip stars inside glow core
            continue
        sr = sb * (0.85 + 0.15 * st)
        sg = sb * (0.88 + 0.10 * (1 - st))
        sb_val = sb * (0.95 - 0.15 * st)
        ref[sy, sx, 0] = np.clip(ref[sy, sx, 0] + sr * 0.7, 0.0, 1.0)
        ref[sy, sx, 1] = np.clip(ref[sy, sx, 1] + sg * 0.7, 0.0, 1.0)
        ref[sy, sx, 2] = np.clip(ref[sy, sx, 2] + sb_val * 0.7, 0.0, 1.0)

    # ── 3. Volcanic cone mask ────────────────────────────────────────────────
    base_y = 0.82
    base_lx = 0.02
    base_rx = 0.98
    t_cone = np.clip((yf - cy) / (base_y - cy), 0.0, 1.0).astype(np.float32)
    cone_left  = cx + (base_lx - cx) * t_cone
    cone_right = cx + (base_rx - cx) * t_cone
    in_cone = (yf >= cy) & (xf >= cone_left) & (xf <= cone_right)

    # Cone base color: very dark basalt (warm dark at base, cool dark at top)
    cone_warm = (t_cone * 0.015 + 0.005).astype(np.float32)
    cone_r = np.clip(cone_warm + 0.008, 0.0, 1.0)
    cone_g = np.clip(cone_warm + 0.012, 0.0, 1.0)
    cone_b = np.clip(cone_warm + 0.008, 0.0, 1.0)

    ref[:, :, 0] = np.where(in_cone, cone_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(in_cone, cone_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(in_cone, cone_b, ref[:, :, 2])

    # ── 4. Fire-reflected glow on cone ───────────────────────────────────────
    glow_cone = np.clip(0.60 * np.exp(-gd / 0.20), 0.0, 1.0).astype(np.float32)
    ref[:, :, 0] = np.where(in_cone,
                            np.clip(ref[:, :, 0] + glow_cone * 0.75, 0.0, 1.0),
                            ref[:, :, 0])
    ref[:, :, 1] = np.where(in_cone,
                            np.clip(ref[:, :, 1] + glow_cone * 0.28, 0.0, 1.0),
                            ref[:, :, 1])
    ref[:, :, 2] = np.where(in_cone,
                            np.clip(ref[:, :, 2] + glow_cone * 0.03, 0.0, 1.0),
                            ref[:, :, 2])

    # ── 5. Lava flow channels ────────────────────────────────────────────────
    # Three channels: center, left-fork, right-fork
    flow_w_sq = (0.012) ** 2
    flows = [
        # (x_start, y_start, x_end, y_end, brightness, meander_freq, meander_amp)
        (0.500, cy,    0.500, 0.58,  1.00, 14.0, 0.010),   # center to fork
        (0.500, 0.58,  0.340, 0.80,  0.82,  8.0, 0.014),   # left fork
        (0.500, 0.58,  0.660, 0.80,  0.82,  8.0, 0.014),   # right fork
        (0.500, cy,    0.440, 0.72,  0.60, 11.0, 0.008),   # secondary left
        (0.500, cy,    0.560, 0.72,  0.60, 11.0, 0.008),   # secondary right
    ]
    for (fx0, fy0, fx1, fy1, fbrn, mfreq, mamp) in flows:
        n_pts = 280
        ts = np.linspace(0.0, 1.0, n_pts, dtype=np.float32)
        flow_xf = fx0 + (fx1 - fx0) * ts + mamp * np.sin(ts * mfreq * np.pi).astype(np.float32)
        flow_yf = fy0 + (fy1 - fy0) * ts

        for k in range(n_pts):
            dist_sq = ((xf - flow_xf[k]) ** 2 + (yf - flow_yf[k]) ** 2).astype(np.float32)
            intensity = np.exp(-dist_sq / flow_w_sq).astype(np.float32)
            fade = float(fbrn) * (1.0 - ts[k] * 0.5)
            # hot center: white-yellow; edges: orange-red
            hot = np.clip(intensity * fade * 0.90, 0.0, 1.0)
            warm = np.clip(intensity * fade * 0.55, 0.0, 1.0)
            cool = np.clip(intensity * fade * 0.05, 0.0, 1.0)
            ref[:, :, 0] = np.clip(ref[:, :, 0] + hot,  0.0, 1.0)
            ref[:, :, 1] = np.clip(ref[:, :, 1] + warm, 0.0, 1.0)
            ref[:, :, 2] = np.clip(ref[:, :, 2] + cool, 0.0, 1.0)

    # ── 6. Caldera / lava lake at summit ─────────────────────────────────────
    caldera_d = np.sqrt((xf - cx) ** 2 * 5.0 + (yf - cy) ** 2 * 3.0).astype(np.float32)
    caldera   = np.clip(1.0 - caldera_d / 0.055, 0.0, 1.0) ** 2
    ref[:, :, 0] = np.clip(ref[:, :, 0] + caldera * 0.95, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + caldera * 0.72, 0.0, 1.0)
    ref[:, :, 2] = np.clip(ref[:, :, 2] + caldera * 0.22, 0.0, 1.0)

    # ── 7. Smoke / ash plume ─────────────────────────────────────────────────
    # Rising from caldera, drifting NE (right), widening
    n_smoke = 35
    smoke_ts = np.linspace(0.0, 1.0, n_smoke, dtype=np.float32)
    for st in smoke_ts:
        sx_c = cx + 0.06 * st
        sy_c = cy - 0.25 * st
        if sy_c < 0.0:
            break
        sw = 0.04 + st * 0.10
        smoke_d = np.sqrt((xf - sx_c) ** 2 / (sw ** 2) + (yf - sy_c) ** 2 / (0.04 ** 2))
        alpha_s = np.clip(0.45 * np.exp(-smoke_d ** 2), 0.0, 1.0).astype(np.float32)
        smoke_c = 0.08 + st * 0.06  # grey
        ref[:, :, 0] = np.clip(ref[:, :, 0] * (1 - alpha_s) + smoke_c * alpha_s, 0.0, 1.0)
        ref[:, :, 1] = np.clip(ref[:, :, 1] * (1 - alpha_s) + smoke_c * 0.95 * alpha_s, 0.0, 1.0)
        ref[:, :, 2] = np.clip(ref[:, :, 2] * (1 - alpha_s) + smoke_c * 0.90 * alpha_s, 0.0, 1.0)

    # ── 8. Sea (outside cone, below base_y) ──────────────────────────────────
    in_sea = (yf >= base_y) & ~in_cone
    # Dark sea base
    sea_r = np.full_like(yf, 0.04)
    sea_g = np.full_like(yf, 0.045)
    sea_b = np.full_like(yf, 0.07)
    # Fire reflection on water (horizontal ripple bands)
    sea_glow = np.clip(0.38 * np.exp(-gd / 0.28), 0.0, 1.0).astype(np.float32)
    ripple = (0.012 * np.sin(yf * H * 0.9) * np.exp(-(yf - base_y) * 8)).astype(np.float32)
    sea_r = np.clip(sea_r + sea_glow * 0.70 + ripple, 0.0, 1.0)
    sea_g = np.clip(sea_g + sea_glow * 0.28 + ripple * 0.4, 0.0, 1.0)
    sea_b = np.clip(sea_b + sea_glow * 0.04, 0.0, 1.0)
    ref[:, :, 0] = np.where(in_sea, sea_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(in_sea, sea_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(in_sea, sea_b, ref[:, :, 2])

    # ── 9. Foreground lava field (aa lava cracks) ─────────────────────────────
    fg_start = 0.86
    in_fg = (yf >= fg_start)
    # Dark aa lava base
    fg_dark = (0.025 + (yf - fg_start) * 0.01).astype(np.float32)
    ref[:, :, 0] = np.where(in_fg, fg_dark, ref[:, :, 0])
    ref[:, :, 1] = np.where(in_fg, fg_dark, ref[:, :, 1])
    ref[:, :, 2] = np.where(in_fg, fg_dark * 0.8, ref[:, :, 2])

    # Glowing cracks: Moire-like crack pattern
    crack_x = np.abs(np.sin(xx.astype(np.float32) * 0.18 + yy.astype(np.float32) * 0.07))
    crack_y = np.abs(np.sin(yy.astype(np.float32) * 0.22 + xx.astype(np.float32) * 0.05))
    crack_pat = np.minimum(crack_x, crack_y)
    crack_glow = np.clip(1.0 - crack_pat / 0.03, 0.0, 1.0).astype(np.float32) * 0.80
    # Taper cracks toward top of fg zone
    crack_fade = np.clip((yf - fg_start) / 0.06, 0.0, 1.0).astype(np.float32)
    crack_glow = crack_glow * crack_fade
    ref[:, :, 0] = np.where(in_fg,
                            np.clip(ref[:, :, 0] + crack_glow * 0.92, 0.0, 1.0),
                            ref[:, :, 0])
    ref[:, :, 1] = np.where(in_fg,
                            np.clip(ref[:, :, 1] + crack_glow * 0.38, 0.0, 1.0),
                            ref[:, :, 1])
    ref[:, :, 2] = np.where(in_fg,
                            np.clip(ref[:, :, 2] + crack_glow * 0.03, 0.0, 1.0),
                            ref[:, :, 2])

    return np.clip(ref, 0.0, 1.0)


# ── Main ─────────────────────────────────────────────────────────────────────

print(f"Session 288: Pissarro (199th mode) — Pele's Fury, Kīlauea at Midnight")
print(f"Canvas: {W}×{H}  seed={SEED}")

print("Building procedural reference...")
ref_f32 = build_reference()
# Convert to uint8 for Painter (engine expects 0-255 range)
ref = (ref_f32 * 255).astype(np.uint8)

print("Initializing painter...")
p = Painter(W, H, seed=SEED)

# Ground: very dark volcanic earth, warm trace
p.tone_ground(color=(0.05, 0.04, 0.03), texture_strength=0.018)

# Underpainting: deep monochrome structure
print("Pass: underpainting...")
p.underpainting(ref, stroke_size=52, n_strokes=250, dry_amount=0.88)

# Block-in: broad volcanic masses
print("Pass: block_in (broad)...")
p.block_in(ref, stroke_size=34, n_strokes=480, dry_amount=0.75)
print("Pass: block_in (medium)...")
p.block_in(ref, stroke_size=20, n_strokes=500, dry_amount=0.68)

# Build form: model lava flows, sky gradient, rock texture
print("Pass: build_form (medium)...")
p.build_form(ref, stroke_size=13, n_strokes=540, dry_amount=0.60)
print("Pass: build_form (fine)...")
p.build_form(ref, stroke_size=6,  n_strokes=440, dry_amount=0.52)

# Place lights: caldera glow, star glints, lava crack accents
print("Pass: place_lights...")
p.place_lights(ref, stroke_size=4, n_strokes=320)

# Artist pass: Pissarro divisionist shimmer
print("Pass: pissarro_divisionist_shimmer_pass...")
p.pissarro_divisionist_shimmer_pass(
    dot_radius=5,
    n_samples=6,
    color_sigma=0.13,
    shimmer_strength=0.20,
    shadow_hi=0.36,
    shadow_lo=0.18,
    shadow_green=(0.36, 0.52, 0.38),
    shadow_strength=0.25,
    highlight_lo=0.65,
    highlight_hi=0.88,
    warm_amber=(0.94, 0.86, 0.58),
    highlight_strength=0.22,
    hue_coherence=0.32,
    n_hue_sectors=12,
    opacity=0.80,
)

# Improvement pass: structure tensor anisotropic sharpening
print("Pass: paint_structure_tensor_pass...")
p.paint_structure_tensor_pass(
    outer_sigma=3.0,
    inner_sigma=1.2,
    sharpen_amount=0.50,
    coherence_threshold=0.10,
    opacity=0.68,
)

print(f"Saving → {OUTPUT}")
p.save(OUTPUT)
print("Done.")
