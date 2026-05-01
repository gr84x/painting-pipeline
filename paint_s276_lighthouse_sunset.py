"""
paint_s276_lighthouse_sunset.py -- Session 276

"Point Reyes Lighthouse at Dusk -- in the manner of Wayne Thiebaud"

Image Description
-----------------
Subject & Composition
    A lone lighthouse perched on a rocky coastal headland, seen from a low
    three-quarter angle slightly below and to the left of the tower. The lighthouse
    stands at center-right on a dark basalt outcrop, its white cylinder rising
    against a sunset sky. The viewpoint is from the cliff path, looking up at the
    lighthouse from approximately 40% height, so the tower and its red-capped
    lantern room dominate the upper third of the canvas. Landscape format 1440x1040.

    The composition divides into four horizontal bands that interpenetrate as
    Thiebaud-style chromatic planes: a deep violet-indigo sky with a warm amber-
    orange band at the horizon; the white lighthouse tower with its red iron cap;
    a mid-ground of dark basalt rock, tidal pools, and wind-bent coastal grass;
    and a foreground of rough stone slabs with shallow salt-water pools catching
    the last light.

The Figure
    The lighthouse is the solitary protagonist -- cylindrical, white-painted
    masonry, approximately three-quarters of the canvas height. Its surface
    reads as two planes: the sun-facing side (warm cream-gold, slightly pink from
    the sunset glow) and the shadow face (cool blue-violet, receiving the ambient
    skylight). The lantern room is a deep iron-red cap with small pane windows
    that catch amber-gold highlights. Below the lantern, a white cast-iron gallery
    railing creates a horizontal accent.

    The lighthouse projects the energy of steadfast solitude -- a human sentinel
    in a wild landscape, offering orientation in darkness and storm. Its emotional
    state is calm confidence, an absolute anchor in the turbulence of sea and wind.

The Environment
    SKY (upper 30%): Deep violet-indigo at the zenith, graduating to a saturated
    warm amber-orange at the horizon, with a thin band of pale yellow just above
    the horizon. A few cirrus wisps catch rose-gold light. The sky has the deep
    chromatic richness of civil twilight -- full of color, not yet dark.

    CLIFF AND ROCK (middle 40%): Dark basalt headland, almost black in the deepest
    shadows, but with subtle green-grey lichen patches and warm rust-brown iron
    seams. The rock surface is irregular, fractured, with tide-eroded hollows.
    Tidal pools in the foreground rock catch reflections of the amber sky -- small
    mirrors of warm gold among dark stone. Wind-bent coastal grass (pale straw-
    yellow and olive-green) grows in the rock crevices.

    OCEAN (lower 15%): Deep steel-blue, just visible beyond the rock at the base of
    the cliff. White foam traces mark where waves meet the headland.

    BACKGROUND: The far coastline fades into the atmospheric haze of the horizon --
    a warm violet-grey smear against the amber sky. The deep blue-indigo sea
    extends to the horizon edge.

    The boundaries in this scene are crisp where rock meets sky (hard edge), soft
    where sky blends to the horizon band (gradual gradient), and rough/broken
    where rock meets sea (fractured foam). The lighthouse edges are the crispest
    in the composition -- the clean geometry of masonry against organic rock.

Technique & Palette
    Wayne Thiebaud mode -- session 276, 187th distinct mode.

    The Thiebaud technique transforms a romantic coastal landscape into a study in
    chromatic halos: the lighthouse edges glow with warm cream halos on the lit
    face and are bounded by pink-violet colored shadows. The tidal pools have halo
    glows around their reflections. The rock-sky boundary has a warm amber halo
    along the upper rock edge. The entire painting has the quality of objects
    isolated in their own luminous zone -- Thiebaud's pies and cakes transformed
    into lighthouse and basalt.

    Pipeline:
    1. Procedural reference: sunset sky gradient, lighthouse cylinder, rock
       headland, tidal pools, ocean band, coastal grass.
    2. tone_ground: warm amber-rose (0.48, 0.36, 0.24).
    3. underpainting x2: establish value structure.
    4. block_in x2: sky gradients, lighthouse form, rock masses.
    5. build_form x2: lighthouse surface planes, rock texture, tidal pools.
    6. place_lights: sunset sky glow, lit lighthouse face, tidal pool reflections.
    7. paint_complementary_shadow_pass (s276 improvement): detect warm sunset
       light, tint shadow zones with blue-violet complement.
    8. thiebaud_halo_shadow_pass (s276, 187th mode): chromatic halos on all
       object edges -- warm cream on lit side, pink-violet shadow on dark side.
    9. paint_aerial_perspective_pass: atmospheric recession toward horizon.

    Palette (Thiebaud sunset coastal):
    warm cream (0.97/0.94/0.85) -- sunset amber (0.92/0.65/0.28) --
    violet sky (0.28/0.22/0.52) -- salmon shadow (0.86/0.52/0.54) --
    basalt dark (0.18/0.16/0.14) -- lighthouse white (0.95/0.93/0.90) --
    iron-red cap (0.65/0.20/0.16) -- pale gold reflection (0.92/0.82/0.45)

Mood & Intent
    The painting is a meditation on solitude and orientation. The lighthouse
    stands at the exact boundary between the human world of built form and the
    natural world of rock and sea and sky. Thiebaud's halo technique makes the
    lighthouse glow with an almost sacred luminosity -- the warm halos around
    its edges suggest not just light on painted masonry, but light as meaning:
    a beacon, a presence, a fixed point in the indifferent flow of tide and wind.

    The viewer should feel the particular melancholy-beauty of the coast at
    dusk: the warmth of the last light, the cold of the coming dark, the
    steadiness of a human structure in a wild place. The colored shadows
    (pink-violet beside warm gold) give the painting the slightly unreal,
    heightened-perception quality of Thiebaud's best work.
"""

import sys
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stroke_engine import Painter

# ── Canvas setup ─────────────────────────────────────────────────────────────
W, H = 1440, 1040
SEED = 276
OUT  = "s276_lighthouse_sunset.png"


def build_reference() -> np.ndarray:
    """Procedural reference: coastal cliff lighthouse at sunset."""
    rng = np.random.default_rng(SEED)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # ── Sky (upper 30%) ──────────────────────────────────────────────────────
    sky_h = int(H * 0.30)
    for y in range(sky_h):
        t = y / float(sky_h - 1)        # 0=top, 1=horizon
        # Violet-indigo at top -> amber-orange at bottom
        r = 0.18 + t * (0.92 - 0.18)
        g = 0.14 + t * (0.62 - 0.14)
        b = 0.45 + t * (0.18 - 0.45)
        ref[y, :, :] = np.clip([r, g, b], 0, 1)

    # Thin pale-yellow band just above horizon
    band_start = int(sky_h * 0.80)
    for y in range(band_start, sky_h):
        t = (y - band_start) / float(sky_h - band_start)
        r = 0.92 + t * (0.98 - 0.92)
        g = 0.75 + t * (0.88 - 0.75)
        b = 0.28 + t * (0.50 - 0.28)
        ref[y, :, :] = np.clip([r, g, b], 0, 1)

    # Subtle cirrus wisps (horizontal smears)
    for _ in range(6):
        cy = rng.integers(5, band_start - 10)
        cx = rng.integers(50, W - 50)
        cw = rng.integers(80, 220)
        ch = rng.integers(4, 12)
        x0 = max(0, cx - cw // 2)
        x1 = min(W, cx + cw // 2)
        y0 = max(0, cy - ch // 2)
        y1 = min(H, cy + ch // 2)
        wisp_r = 0.80 + rng.random() * 0.15
        wisp_g = 0.65 + rng.random() * 0.20
        wisp_b = 0.72 + rng.random() * 0.18
        alpha = 0.25
        ref[y0:y1, x0:x1, :] = (
            (1 - alpha) * ref[y0:y1, x0:x1, :] +
            alpha * np.array([wisp_r, wisp_g, wisp_b])
        )

    # ── Ocean (lower 15%) ─────────────────────────────────────────────────────
    ocean_start = int(H * 0.85)
    for y in range(ocean_start, H):
        t = (y - ocean_start) / float(H - ocean_start)
        r = 0.12 + t * 0.06
        g = 0.18 + t * 0.08
        b = 0.38 + t * 0.12
        ref[y, :, :] = np.clip([r, g, b], 0, 1)

    # Foam traces at cliff base
    foam_y = int(H * 0.86)
    for _ in range(12):
        fx = rng.integers(0, W)
        fw = rng.integers(30, 90)
        fh = rng.integers(2, 6)
        x0 = max(0, fx)
        x1 = min(W, fx + fw)
        ref[foam_y:foam_y + fh, x0:x1, :] = np.clip([0.85, 0.88, 0.90], 0, 1)

    # ── Rock headland (middle 40% -> 85%) ────────────────────────────────────
    rock_start = sky_h
    rock_end   = ocean_start

    # Base rock color: dark basalt with slight variation
    for y in range(rock_start, rock_end):
        t = (y - rock_start) / float(rock_end - rock_start)
        for x in range(W):
            xt = x / float(W - 1)
            # Rock is darkest at center/bottom (deeper shadow), lighter at edges
            shadow_factor = 0.7 + 0.3 * abs(xt - 0.5) * 2
            r = (0.20 + rng.random() * 0.04) * shadow_factor
            g = (0.18 + rng.random() * 0.04) * shadow_factor
            b = (0.16 + rng.random() * 0.04) * shadow_factor
            ref[y, x, :] = np.clip([r, g, b], 0, 1)

    # Smooth the rock base
    for c in range(3):
        ref[rock_start:rock_end, :, c] = gaussian_filter(
            ref[rock_start:rock_end, :, c], sigma=3
        )

    # Lichen patches (green-grey)
    for _ in range(25):
        lx = rng.integers(0, W - 60)
        ly = rng.integers(rock_start, rock_end - 10)
        lw = rng.integers(20, 80)
        lh = rng.integers(8, 30)
        alpha = 0.3 + rng.random() * 0.25
        ref[ly:ly + lh, lx:lx + lw, :] = np.clip(
            (1 - alpha) * ref[ly:ly + lh, lx:lx + lw, :] +
            alpha * np.array([0.35, 0.40, 0.28]),
            0, 1
        )

    # Iron-rust seams in rock
    for _ in range(8):
        seam_x = rng.integers(100, W - 100)
        seam_y0 = rng.integers(rock_start, rock_end - 40)
        seam_len = rng.integers(30, 120)
        seam_w = rng.integers(2, 5)
        for dy in range(seam_len):
            sy = seam_y0 + dy
            sx = seam_x + rng.integers(-2, 3)
            if 0 <= sy < H and 0 <= sx < W:
                ref[sy, max(0, sx):min(W, sx + seam_w), :] = np.clip(
                    [0.48, 0.28, 0.14], 0, 1
                )

    # Tidal pools (small bright gold reflections in rock)
    for _ in range(7):
        px = rng.integers(100, W - 150)
        py = rng.integers(int(H * 0.65), int(H * 0.82))
        pw = rng.integers(15, 50)
        ph = rng.integers(8, 18)
        # Tidal pool reflects amber sunset sky
        pool_r = 0.88 + rng.random() * 0.08
        pool_g = 0.75 + rng.random() * 0.10
        pool_b = 0.32 + rng.random() * 0.12
        ref[py:py + ph, px:px + pw, :] = np.clip([pool_r, pool_g, pool_b], 0, 1)

    # Coastal grass tufts in rock crevices
    for _ in range(35):
        gx = rng.integers(50, W - 80)
        gy = rng.integers(int(H * 0.55), int(H * 0.80))
        gw = rng.integers(6, 24)
        gh = rng.integers(10, 30)
        grass_r = 0.58 + rng.random() * 0.20
        grass_g = 0.55 + rng.random() * 0.22
        grass_b = 0.22 + rng.random() * 0.12
        alpha = 0.4
        ref[gy:gy + gh, gx:gx + gw, :] = np.clip(
            (1 - alpha) * ref[gy:gy + gh, gx:gx + gw, :] +
            alpha * np.array([grass_r, grass_g, grass_b]),
            0, 1
        )

    # ── Lighthouse cylinder (center-right, spanning rock/sky boundary) ────────
    # Tower base at 70% height, top at 12% height
    lh_cx   = int(W * 0.62)          # horizontal center
    lh_base = int(H * 0.70)          # y of base
    lh_top  = int(H * 0.12)          # y of top
    lh_r    = int(W * 0.040)         # radius
    tower_h = lh_base - lh_top

    for y in range(lh_top, lh_base):
        # Slight taper: radius reduces from base to top
        t_taper = (lh_base - y) / float(tower_h)
        r_at_y = int(lh_r * (0.75 + 0.25 * (1 - t_taper)))
        x0 = lh_cx - r_at_y
        x1 = lh_cx + r_at_y
        for x in range(max(0, x0), min(W, x1)):
            # Sun-facing side (left of center) = warm cream-gold
            # Shadow side (right of center) = cool blue-violet-grey
            t_x = (x - x0) / float(x1 - x0 + 1)  # 0=shadow, 1=lit
            if t_x > 0.5:    # lit face (toward evening sun on left)
                r = 0.96 - (t_x - 0.5) * 0.06
                g = 0.90 - (t_x - 0.5) * 0.04
                b = 0.82 - (t_x - 0.5) * 0.08
            else:             # shadow face
                r = 0.78 + t_x * 0.12
                g = 0.76 + t_x * 0.12
                b = 0.88 + t_x * 0.06
            ref[y, x, :] = np.clip([r, g, b], 0, 1)

    # Lighthouse gallery railing (horizontal band)
    gallery_y = lh_top + int(tower_h * 0.88)
    for y in range(gallery_y - 3, gallery_y + 5):
        ref[y, max(0, lh_cx - lh_r - 4):min(W, lh_cx + lh_r + 4), :] = [0.92, 0.88, 0.82]

    # Lantern room cap (red iron)
    cap_top  = lh_top
    cap_bot  = lh_top + int(tower_h * 0.14)
    cap_w    = lh_r + 6
    for y in range(cap_top, cap_bot):
        for x in range(max(0, lh_cx - cap_w), min(W, lh_cx + cap_w)):
            ref[y, x, :] = np.clip([0.65, 0.20, 0.16], 0, 1)

    # Lantern windows (amber-gold)
    win_y = cap_top + int((cap_bot - cap_top) * 0.35)
    win_h = int((cap_bot - cap_top) * 0.45)
    for wx_off in [-cap_w // 2, cap_w // 2 - 6]:
        ref[win_y:win_y + win_h,
            max(0, lh_cx + wx_off):min(W, lh_cx + wx_off + 8), :] = \
            np.clip([0.98, 0.82, 0.30], 0, 1)

    # Light beam stub (thin pale gold triangle from lantern to upper right)
    beam_tip_x = lh_cx + int(W * 0.18)
    beam_tip_y = cap_top - int(H * 0.04)
    beam_base  = int(W * 0.012)
    for step in range(60):
        t = step / 59.0
        bx = int(lh_cx + t * (beam_tip_x - lh_cx))
        by = int(cap_top + t * (beam_tip_y - cap_top))
        bw = max(1, int(beam_base * (1 - t)))
        alpha = 0.30 * (1 - t)
        ref[max(0, by - bw):min(H, by + bw),
            max(0, bx - bw):min(W, bx + bw), :] = np.clip(
            (1 - alpha) * ref[max(0, by - bw):min(H, by + bw),
                              max(0, bx - bw):min(W, bx + bw), :] +
            alpha * np.array([0.98, 0.94, 0.75]),
            0, 1
        )

    # Final smoothing pass on whole reference (preserves hard edges)
    for c in range(3):
        ref[:, :, c] = gaussian_filter(ref[:, :, c], sigma=0.8)

    return (np.clip(ref, 0, 1) * 255).astype(np.uint8)


# ── Build reference ───────────────────────────────────────────────────────────
print("Building procedural reference...")
ref = build_reference()
Image.fromarray(ref).save("s276_reference.png")
print(f"  Reference saved: s276_reference.png ({W}x{H})")

# ── Painting pipeline ─────────────────────────────────────────────────────────
p = Painter(W, H, seed=SEED)

print("tone_ground...")
p.tone_ground((0.48, 0.36, 0.24), texture_strength=0.018)

print("underpainting (broad)...")
p.underpainting(ref, stroke_size=52, n_strokes=240)

print("underpainting (medium)...")
p.underpainting(ref, stroke_size=34, n_strokes=220)

print("block_in (broad)...")
p.block_in(ref, stroke_size=32, n_strokes=460)

print("block_in (medium)...")
p.block_in(ref, stroke_size=20, n_strokes=500)

print("build_form (medium)...")
p.build_form(ref, stroke_size=12, n_strokes=540)

print("build_form (fine)...")
p.build_form(ref, stroke_size=6, n_strokes=440)

print("place_lights...")
p.place_lights(ref, stroke_size=4, n_strokes=300)

print("paint_complementary_shadow_pass (s276 improvement)...")
p.paint_complementary_shadow_pass(
    light_threshold  = 0.72,
    shadow_threshold = 0.28,
    complement_shift = 0.50,
    tint_saturation  = 0.30,
    tint_strength    = 0.22,
    opacity          = 0.58,
)

print("thiebaud_halo_shadow_pass (187th mode)...")
p.thiebaud_halo_shadow_pass(
    edge_sigma       = 1.6,
    edge_threshold   = 0.050,
    halo_radius      = 8,
    halo_r           = 0.97, halo_g=0.92, halo_b=0.80,
    halo_opacity     = 0.40,
    shadow_r         = 0.82, shadow_g=0.56, shadow_b=0.82,
    shadow_opacity   = 0.34,
    contour_darkness = 0.20,
    contour_opacity  = 0.48,
    opacity          = 0.74,
)

print("paint_aerial_perspective_pass...")
p.paint_aerial_perspective_pass()

print(f"Saving {OUT}...")
p.save(OUT)
print(f"Done: {OUT}")
