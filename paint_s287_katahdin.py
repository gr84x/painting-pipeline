"""Session 287 -- Marsden Hartley (198th mode)
hartley_elemental_mass_pass + paint_median_clarity_pass

Subject & Composition:
    "Katahdin at First Light" -- Mount Katahdin dominates the canvas as a vast
    dark triangular mass, its broad plateau summit cutting across the upper third
    of a portrait canvas. The mountain is viewed from the southwest at dawn,
    approximately from the bog meadows below Chimney Pond. The composition places
    the summit slightly left of center, its flanks descending asymmetrically: the
    left cliff edge drops steeply, almost vertical, to the treeline; the right
    flank descends in a longer, more gradual arc, its face partly lit by the
    rising sun off-frame to the right. Two smaller satellite ridges bracket the
    peak on either side. The lower two-thirds of the canvas transition through
    the serrated dark spruce treeline, a still boggy pond, and finally the dark
    rocky foreground where the viewer stands among lichen-encrusted granite slabs.

The Figure:
    There is no human figure. The subject is purely elemental: mountain, sky, tree,
    stone, water. Hartley often painted this way in his late Maine work -- the
    landscape as protagonist, not backdrop. The emotional presence is in the scale
    of the mountain against the mortal-scaled foreground boulders, and in the
    burning intensity of the dawn sky pressing against the almost absolute darkness
    of the rock. If there is a "figure" in this painting, it is Mt. Katahdin itself:
    ancient, massive, self-sufficient, indifferent. The mountain's emotional state
    is geological patience. It has stood here ten thousand years and will stand ten
    thousand more.

The Environment:
    SKY: The sky occupies the upper 28% of the canvas. At the very top, it is
    deep indigo-violet (the last of night, still present in the zenith). As the
    eye descends toward the horizon, the sky brightens through slate blue, then
    transitions sharply into an intense burnt orange-amber band where the sun is
    just below the horizon. This orange band is narrow but very bright -- the
    burning horizon that gives Hartley's Maine skies their drama. The boundary
    between the deep mountain silhouette and the burning horizon is the painting's
    primary contrast: near-black against near-white-orange.

    MOUNTAIN: The mountain occupies nearly half the canvas. Its colour is
    Hartley's characteristic dark blue-green-black: not pure black, but the
    cold dark of granite and dense spruce seen from a distance at low light.
    The left cliff face is nearly vertical and nearly featureless -- a dark wall.
    The right flank shows the faintest warmth where the first dawn rays catch
    the south-facing scree slopes, a subtle ochre-umber modulation in the otherwise
    absolute darkness of the mass. The summit plateau is ragged at its edges:
    the near-horizontal line broken by irregular buttresses and ridgelines.

    TREELINE: The treeline at 62%-72% height is a ragged dark fringe of mature
    black spruce: irregular vertical dark shapes, each slightly different in
    height, collectively forming a bristling horizon line between the mountain
    body above and the open bog below. The spruce are nearly the same dark
    colour as the mountain but distinguishable by their organic vertical rhythm.

    POND / BOG: A small still pond occupies 68%-78% height, slightly left of
    center. The water is dark but catches the burning horizon in a narrow
    horizontal band -- a compressed reflection of the orange sky, broken by
    the silhouetted reeds at the pond's margins. This is the only horizontal
    element in a composition of verticals and the dominant diagonal of the
    mountain flanks.

    FOREGROUND: The foreground from 76% to the bottom is the viewer's world:
    dark granite slabs, lichen-covered, their surfaces flat and roughly
    horizontal. The lichen adds the palest trace of grey-cream to the dark rock.
    One large boulder shape in the lower right occupies a significant area,
    its mass rhyming with the mountain above. A single ancient spruce snag --
    dead, its branches broken off -- stands near the left edge of the foreground,
    a dark exclamation point at the canvas edge.

Technique & Palette:
    Marsden Hartley's elemental mass technique: severely restricted Maine palette
    of dark blue-black, deep shadow green, raw umber, burnt sienna, near-black,
    warm cream, forest green, and raw sienna ochre. The hartley_elemental_mass_pass
    commits each pixel to its nearest palette anchor, flattens interior colour
    planes using coarse tile averaging, reinforces painted outlines at all edges,
    and creates the luminance-anti-correlated saturation characteristic of
    Hartley's mature work (dark masses desaturate toward grey, bright sky amplifies
    toward intense warm colour). The paint_median_clarity_pass enhances the
    crisp impasto quality of the paint surface using median-filter-based detail
    extraction, with shadow-floor protection preserving the depth of the darkest
    mountain masses.

Mood & Intent:
    The painting intends to place the viewer in relation to something ancient and
    absolute. Katahdin is not picturesque; it is not comfortable. It is the
    northern edge of something. The burnt sky behind it is not a beautiful sunset
    but a primal event: the return of the sun, indifferent to the mountain and to
    the viewer equally. The mood is austere, elevated, slightly vertiginous -- the
    feeling Hartley described when he wrote of being "in the presence of something
    that asks nothing of the human." The viewer should feel small in the right way:
    not diminished, but proportionately located in the order of things. Hartley
    wanted his late Maine landscapes to achieve what he called "the granite feeling"
    -- a sensation of geological permanence transmitted through paint. The darkest
    darks should feel genuinely dark; the burning sky should feel genuinely hot;
    the still pond should feel genuinely cold. Paint with patience and practice,
    like a true artist.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stroke_engine import Painter

# ── Canvas dimensions ────────────────────────────────────────────────────────
W, H = 1040, 1440   # portrait -- mountain dominates vertical space
SEED = 287

# ── Reference: procedural Katahdin-at-dawn scene ─────────────────────────────

def build_reference() -> np.ndarray:
    """Build a Hartley-inspired Maine mountain reference.

    Zones:
      0.00-0.28 : sky (deep indigo top → burning orange horizon)
      0.04-0.64 : mountain mass (dark triangular bulk)
      0.60-0.72 : spruce treeline (serrated dark fringe)
      0.66-0.78 : bog pond (reflective, dark)
      0.74-1.00 : rocky granite foreground
    """
    from scipy.ndimage import gaussian_filter as gf
    rng = np.random.default_rng(SEED)

    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    xs = np.linspace(0.0, 1.0, W, dtype=np.float32)[None, :]

    # ── Sky (0.00 - 0.28) ─────────────────────────────────────────────────────
    sky_frac = 0.28
    sky_zone = ys < sky_frac
    # t=0 at top, t=1 at horizon
    t_sky = np.clip(ys / (sky_frac + 0.01), 0.0, 1.0)

    # Deep indigo at top → burnt orange at horizon
    sky_r = np.clip(0.12 + t_sky * 0.68, 0.0, 1.0)   # 0.12 → 0.80
    sky_g = np.clip(0.14 + t_sky * 0.28, 0.0, 1.0)   # 0.14 → 0.42
    sky_b = np.clip(0.30 - t_sky * 0.18, 0.0, 1.0)   # 0.30 → 0.12

    # Narrow burning band near horizon (t > 0.72)
    burn_gate = np.clip((t_sky - 0.72) / 0.14, 0.0, 1.0)
    sky_r = np.clip(sky_r + burn_gate * 0.18, 0.0, 1.0)
    sky_g = np.clip(sky_g - burn_gate * 0.06, 0.0, 1.0)
    sky_b = np.clip(sky_b - burn_gate * 0.08, 0.0, 1.0)

    # Very subtle cloud texture in sky
    sky_noise = gf(rng.random((H, W)).astype(np.float32), sigma=24)
    sky_noise = (sky_noise - 0.5) * 0.06
    sky_r = np.clip(sky_r + sky_noise * sky_zone.astype(np.float32), 0.0, 1.0)
    sky_g = np.clip(sky_g + sky_noise * sky_zone.astype(np.float32) * 0.7, 0.0, 1.0)

    ref[:, :, 0] = np.where(sky_zone, sky_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(sky_zone, sky_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(sky_zone, sky_b, ref[:, :, 2])

    # ── Mountain mass (0.04 - 0.64) ────────────────────────────────────────────
    # Katahdin: broad plateau summit, peak slightly left of center
    # Define mountain silhouette as a function of x

    # Summit plateau: broadly flat from x=0.24 to x=0.72, at y≈0.05-0.08
    # Left cliff: steep descent from x=0.24 down to x=0.10, y=0.64
    # Right flank: gentler from x=0.72 down to x=0.96, y=0.64
    # Irregular buttresses and ridgelines

    def mountain_top_y(x_frac):
        """Returns the y-fraction of the mountain top at given x."""
        # Plateau region
        if 0.26 <= x_frac <= 0.70:
            base = 0.058
            # Add some irregularity: a few ridgeline bumps
            bump1 = 0.018 * np.exp(-((x_frac - 0.38) / 0.06) ** 2)  # left buttress
            bump2 = 0.014 * np.exp(-((x_frac - 0.58) / 0.05) ** 2)  # right buttress
            notch = 0.010 * np.exp(-((x_frac - 0.50) / 0.04) ** 2)  # slight summit dip
            return base + bump1 + bump2 - notch
        elif x_frac < 0.26:
            # Steep left cliff: linear from (0.26, 0.058) to (0.06, 0.64)
            t = (0.26 - x_frac) / max(0.26 - 0.06, 0.01)
            return 0.058 + t * (0.64 - 0.058)
        else:
            # Gentler right flank: from (0.70, 0.058) to (0.98, 0.64)
            t = (x_frac - 0.70) / max(0.98 - 0.70, 0.01)
            return 0.058 + t * (0.64 - 0.058)

    # Build per-column top_y array
    x_arr = np.linspace(0.0, 1.0, W, dtype=np.float32)
    top_y_arr = np.array([mountain_top_y(float(x)) for x in x_arr], dtype=np.float32)
    # Add mild per-column noise to ragged the profile
    col_noise = gf(rng.random(W).astype(np.float32), sigma=4) - 0.5
    top_y_arr = np.clip(top_y_arr + col_noise * 0.012, 0.0, 0.65)

    # Build mountain mask
    top_y_2d = top_y_arr[None, :]        # (1, W)
    mtn_zone = (ys > top_y_2d) & (ys < 0.65)

    # Mountain colour: dark blue-green-black
    mtn_noise = gf(rng.random((H, W)).astype(np.float32), sigma=12)
    mtn_r = np.clip(0.08 + mtn_noise * 0.06, 0.0, 1.0)
    mtn_g = np.clip(0.10 + mtn_noise * 0.07, 0.0, 1.0)
    mtn_b = np.clip(0.09 + mtn_noise * 0.05, 0.0, 1.0)

    # Dawn light on right flank (ochre warmth where sun catches rock)
    right_flank_zone = (xs > 0.56) & (ys > 0.12) & (ys < 0.50)
    dawn_gate = np.clip(
        np.clip((xs - 0.56) / 0.24, 0.0, 1.0) *
        np.clip((0.50 - ys) / 0.30, 0.0, 1.0) * 2.0, 0.0, 0.45
    )
    dawn_gate = gf(dawn_gate.astype(np.float32), sigma=16).astype(np.float32)
    dawn_gate = np.clip(dawn_gate * 1.4, 0.0, 0.35)

    mtn_r = np.clip(mtn_r + dawn_gate * 0.22, 0.0, 1.0)
    mtn_g = np.clip(mtn_g + dawn_gate * 0.12, 0.0, 1.0)
    mtn_b = np.clip(mtn_b + dawn_gate * 0.02, 0.0, 1.0)

    # Mountain area texture noise (large-scale rock faces)
    rock_noise = gf(rng.random((H, W)).astype(np.float32), sigma=28)
    mtn_r = np.clip(mtn_r + (rock_noise - 0.5) * 0.04 * mtn_zone.astype(np.float32), 0.0, 1.0)
    mtn_g = np.clip(mtn_g + (rock_noise - 0.5) * 0.04 * mtn_zone.astype(np.float32), 0.0, 1.0)

    ref[:, :, 0] = np.where(mtn_zone, mtn_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(mtn_zone, mtn_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(mtn_zone, mtn_b, ref[:, :, 2])

    # ── Spruce treeline (0.60 - 0.73) ─────────────────────────────────────────
    # Serrated dark fringe of spruces across the image
    treeline_base_y = 0.70   # base of treeline
    tree_height_frac = 0.10  # height of trees above their base

    # Per-column tree top with seeded irregularity
    rng2 = np.random.default_rng(SEED + 1)
    raw_tree_heights = rng2.uniform(0.04, tree_height_frac, W).astype(np.float32)
    # Smooth to get natural grouping, then add back small-scale noise
    smooth_heights = gf(raw_tree_heights, sigma=6).astype(np.float32)
    fine_heights = raw_tree_heights - smooth_heights
    tree_top_y = treeline_base_y - smooth_heights - np.abs(fine_heights) * 0.5

    tree_top_2d = tree_top_y[None, :]   # (1, W)
    # Treeline zone: between tree top and treeline_base
    tree_zone = (ys > tree_top_2d) & (ys < treeline_base_y)
    # Also include mountain zone overlap (dark spruce in front of mountain)
    tree_zone = tree_zone | ((ys > 0.60) & (ys < 0.64) & (ys > top_y_2d))

    # Very dark spruce colour
    tr_noise = gf(rng.random((H, W)).astype(np.float32), sigma=5) * 0.02
    tr_r = np.clip(0.06 + tr_noise, 0.0, 1.0)
    tr_g = np.clip(0.09 + tr_noise * 1.2, 0.0, 1.0)
    tr_b = np.clip(0.06 + tr_noise * 0.8, 0.0, 1.0)

    ref[:, :, 0] = np.where(tree_zone, tr_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(tree_zone, tr_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(tree_zone, tr_b, ref[:, :, 2])

    # ── Bog pond (0.68 - 0.78, x: 0.18 - 0.62) ─────────────────────────────
    pond_y0, pond_y1 = 0.68, 0.78
    pond_x0, pond_x1 = 0.18, 0.62
    pond_zone = (ys >= pond_y0) & (ys < pond_y1) & (xs >= pond_x0) & (xs < pond_x1)

    # Dark water with narrow horizontal sky reflection near top
    pond_t = np.clip((ys - pond_y0) / (0.04), 0.0, 1.0)  # 0=pond top, 1=deeper
    # Reflection zone: top 35% of pond
    refl_gate = np.clip(1.0 - pond_t * 2.5, 0.0, 1.0)

    # Base water: near-black cold
    pond_r = np.clip(0.08 + 0.04 * refl_gate * 0.6 + gf(
        rng.random((H, W)).astype(np.float32), sigma=3) * 0.02, 0.0, 1.0)
    pond_g = np.clip(0.09 + 0.03 * refl_gate * 0.5, 0.0, 1.0)
    pond_b = np.clip(0.12 + 0.05 * refl_gate, 0.0, 1.0)

    # Horizontal orange-sky reflection band
    sky_reflect_gate = np.clip(1.0 - (ys - pond_y0) / 0.028, 0.0, 1.0)
    pond_r = np.clip(pond_r + sky_reflect_gate * 0.42, 0.0, 1.0)
    pond_g = np.clip(pond_g + sky_reflect_gate * 0.20, 0.0, 1.0)
    pond_b = np.clip(pond_b + sky_reflect_gate * 0.04, 0.0, 1.0)

    # Broken ripple texture in reflection
    ripple_noise = gf(rng.random((H, W)).astype(np.float32), sigma=[1, 8])
    ripple_mask = sky_reflect_gate * np.clip(ripple_noise * 2.0 - 0.8, 0.0, 1.0)
    pond_r = np.clip(pond_r + ripple_mask * 0.18, 0.0, 1.0)
    pond_g = np.clip(pond_g + ripple_mask * 0.08, 0.0, 1.0)

    # Reed silhouettes at pond margins
    reed_noise = gf(rng.random((H, W)).astype(np.float32), sigma=[2, 1])
    reed_mask = (
        ((xs < pond_x0 + 0.06) | (xs > pond_x1 - 0.06)) &
        pond_zone &
        (reed_noise > 0.52)
    )
    pond_r = np.where(reed_mask, 0.05, pond_r)
    pond_g = np.where(reed_mask, 0.07, pond_g)
    pond_b = np.where(reed_mask, 0.05, pond_b)

    ref[:, :, 0] = np.where(pond_zone, pond_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(pond_zone, pond_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(pond_zone, pond_b, ref[:, :, 2])

    # ── Rocky granite foreground (0.74 - 1.00) ───────────────────────────────
    fg_zone = ys >= 0.74
    fg_noise_large = gf(rng.random((H, W)).astype(np.float32), sigma=22)
    fg_noise_med   = gf(rng.random((H, W)).astype(np.float32), sigma=8)
    fg_noise_fine  = gf(rng.random((H, W)).astype(np.float32), sigma=2)

    rock_r = np.clip(0.16 + fg_noise_large * 0.10 + fg_noise_med * 0.06, 0.0, 1.0)
    rock_g = np.clip(0.13 + fg_noise_large * 0.08 + fg_noise_med * 0.05, 0.0, 1.0)
    rock_b = np.clip(0.10 + fg_noise_large * 0.06 + fg_noise_med * 0.04, 0.0, 1.0)

    # Lichen: palest grey-cream on some rock faces
    lichen_mask = (fg_noise_fine > 0.60) & (fg_noise_large > 0.55)
    rock_r = np.where(lichen_mask, np.clip(rock_r + 0.18, 0.0, 1.0), rock_r)
    rock_g = np.where(lichen_mask, np.clip(rock_g + 0.16, 0.0, 1.0), rock_g)
    rock_b = np.where(lichen_mask, np.clip(rock_b + 0.12, 0.0, 1.0), rock_b)

    # Large boulder: lower right
    boulder_cx, boulder_cy = int(0.72 * W), int(0.88 * H)
    boulder_rx, boulder_ry = int(0.14 * W), int(0.08 * H)
    Y_, X_ = np.ogrid[:H, :W]
    boulder_mask = (
        ((X_ - boulder_cx) / max(boulder_rx, 1)) ** 2 +
        ((Y_ - boulder_cy) / max(boulder_ry, 1)) ** 2
    ) <= 1.0
    b_noise = gf(rng.random((H, W)).astype(np.float32), sigma=6)
    rock_r = np.where(boulder_mask, np.clip(0.22 + b_noise * 0.08, 0.0, 1.0), rock_r)
    rock_g = np.where(boulder_mask, np.clip(0.17 + b_noise * 0.06, 0.0, 1.0), rock_g)
    rock_b = np.where(boulder_mask, np.clip(0.12 + b_noise * 0.04, 0.0, 1.0), rock_b)
    # Boulder top edge catches dawn light
    boulder_top = boulder_mask & (Y_ < boulder_cy - boulder_ry // 3)
    rock_r = np.where(boulder_top, np.clip(rock_r + 0.12, 0.0, 1.0), rock_r)
    rock_g = np.where(boulder_top, np.clip(rock_g + 0.08, 0.0, 1.0), rock_g)

    # Dead spruce snag: left foreground column
    snag_x0, snag_x1 = int(0.08 * W), int(0.11 * W)
    snag_y0, snag_y1 = int(0.74 * H), int(0.98 * H)
    rock_r[snag_y0:snag_y1, snag_x0:snag_x1] = 0.08
    rock_g[snag_y0:snag_y1, snag_x0:snag_x1] = 0.07
    rock_b[snag_y0:snag_y1, snag_x0:snag_x1] = 0.06

    ref[:, :, 0] = np.where(fg_zone, rock_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(fg_zone, rock_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(fg_zone, rock_b, ref[:, :, 2])

    # ── Mid-ground: ground between treeline and pond (0.64 - 0.74) ──────────
    mid_zone = (ys >= 0.64) & (ys < 0.74)
    mid_noise = gf(rng.random((H, W)).astype(np.float32), sigma=10)
    mid_r = np.clip(0.14 + mid_noise * 0.08, 0.0, 1.0)
    mid_g = np.clip(0.17 + mid_noise * 0.09, 0.0, 1.0)
    mid_b = np.clip(0.10 + mid_noise * 0.06, 0.0, 1.0)

    ref[:, :, 0] = np.where(mid_zone & ~pond_zone, mid_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(mid_zone & ~pond_zone, mid_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(mid_zone & ~pond_zone, mid_b, ref[:, :, 2])

    # ── Final softening ───────────────────────────────────────────────────────
    for c in range(3):
        ref[:, :, c] = gf(ref[:, :, c], sigma=0.8).astype(np.float32)

    return np.clip(ref, 0.0, 1.0).astype(np.float32)


# ── Build reference ───────────────────────────────────────────────────────────
print("Building procedural reference (Katahdin at first light)...")
ref = build_reference()

ref_uint8 = (ref * 255).astype(np.uint8)
Image.fromarray(ref_uint8).save("s287_reference.png")
print("Reference saved: s287_reference.png")

# ── Painting pipeline ─────────────────────────────────────────────────────────
print("Initialising painter...")
p = Painter(W, H, seed=SEED)

ref_u8 = (ref * 255).astype(np.uint8)

# Ground: dark raw umber -- Hartley's characteristic dark base
print("Tone ground (dark raw umber)...")
p.tone_ground(color=(0.12, 0.10, 0.08), texture_strength=0.025)

# Underpainting: establish the fundamental tonal architecture
print("Underpainting (broad)...")
p.underpainting(ref_u8, stroke_size=54, n_strokes=250, dry_amount=0.62)
print("Underpainting (medium)...")
p.underpainting(ref_u8, stroke_size=42, n_strokes=230, dry_amount=0.58)

# Block in: broad flat masses -- Hartley built from large colour planes
print("Block in (broad)...")
p.block_in(ref_u8, stroke_size=36, n_strokes=460, dry_amount=0.50)
print("Block in (medium)...")
p.block_in(ref_u8, stroke_size=24, n_strokes=510, dry_amount=0.46)

# Build form: mountain texture, treeline detail, rock surface
print("Build form (medium)...")
p.build_form(ref_u8, stroke_size=14, n_strokes=520, dry_amount=0.42)
print("Build form (fine)...")
p.build_form(ref_u8, stroke_size=7, n_strokes=440, dry_amount=0.38)

# Place lights: dawn sky glows, pond reflection, boulder top light
print("Place lights...")
p.place_lights(ref_u8, stroke_size=4, n_strokes=300)

# ── s287 improvement: Median Clarity ─────────────────────────────────────────
print("Median Clarity (s287 improvement)...")
p.paint_median_clarity_pass(
    median_size=5,
    detail_boost=1.85,
    midtone_center=0.48,
    midtone_width=0.36,
    shadow_floor=0.16,
    shadow_reset_strength=0.55,
    opacity=0.75,
)

# ── s287 artist pass: Hartley Elemental Mass (198th mode) ────────────────────
print("Hartley Elemental Mass (198th mode)...")
p.hartley_elemental_mass_pass(
    palette_strength=0.50,
    interior_tile_n_h=14,
    interior_tile_n_w=10,
    interior_flatten_strength=0.34,
    edge_darken_strength=0.52,
    edge_dark_r=0.06,
    edge_dark_g=0.06,
    edge_dark_b=0.06,
    dark_desat_thresh=0.26,
    dark_desat_strength=0.55,
    bright_sat_thresh=0.68,
    bright_sat_strength=0.50,
    opacity=0.82,
)

# ── s286 improvement: Tonal Rebalance (enhance dramatic sky/mountain contrast) ─
print("Tonal Rebalance (s286 improvement)...")
p.paint_tonal_rebalance_pass(
    shadow_percentile=3.0,
    highlight_percentile=95.0,
    curve_sharpness=1.70,
    shoulder_start=0.88,
    max_scale=1.80,
    opacity=0.72,
)

# ── s285 improvement: Frequency Separation (crisp paint surface texture) ──────
print("Frequency Separation (s285 improvement)...")
p.paint_frequency_separation_pass(
    low_sigma=12.0,
    sat_boost=0.22,
    lum_contrast=0.36,
    recombine_weight=0.58,
    opacity=0.50,
)

# ── Final output ──────────────────────────────────────────────────────────────
output_path = "s287_katahdin.png"
p.save(output_path)
print(f"Saved: {output_path}")
