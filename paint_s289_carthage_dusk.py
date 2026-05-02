"""Session 289 -- Jean Dubuffet (200th mode)
dubuffet_art_brut_pass + paint_impasto_relief_pass

Subject & Composition:
    "The Ruins of Carthage at Dusk" -- Looking west across the archaeological
    site of ancient Carthage on the Tunisian coast, near modern-day Tunis.
    The sun has just set below the horizon; the sky burns with layered orange
    and crimson transitioning through violet to deep indigo at the zenith.
    Three tall columns from a Roman-era temple (the Antonine Baths columns)
    rise in the middle-left ground, their limestone catching the last warm light
    against the dark sky. Ruined walls and collapsed arches spread across the
    middle ground in a broken irregular line. The Mediterranean Sea is visible
    between and beyond the ruins as a dark strip of deep ultramarine. The
    foreground is raw ochre and sienna earth scattered with limestone fragments,
    rubble, and patches of low scrubby Mediterranean vegetation.

The Figure:
    No human figure. The subject is the ruins themselves -- ancient stones that
    have witnessed Phoenician merchants, Hannibal's generals, Roman senators,
    Vandal kings, Byzantine bishops, and Arab conquerors across three thousand
    years. The emotional state of the ruins is one of absolute, impersonal
    antiquity. They are not melancholy (that would be a human projection) but
    simply themselves: matter that has endured. Dubuffet would have appreciated
    this: in Art Brut, the stone has as much presence as the figure, and often
    more. The ruins are the protagonist in the same way earth and sand are the
    protagonist in his Texturologies -- not depicted matter but matter itself,
    thick and autonomous on the surface.

The Environment:
    SKY: The sky occupies the upper 38% of the canvas. At the zenith it is deep
    indigo-violet (dusk, not night -- still some atmospheric blue remaining).
    Moving downward it transitions through warm violet-magenta to burnt orange
    at the horizon. This is not a calm sunset but a theatrical one: the colours
    are saturated and slightly unsettling, more Douanier Rousseau than Turner.
    Two or three stars are faintly visible in the upper indigo zone.

    COLUMNS: Three standing Roman columns in the middle-left zone, approximately
    60% canvas height. Limestone: warm yellow-orange catching the last direct
    light on their west face, cool grey-violet in shadow. Their capitals are
    partly ruined. They cast long shadows eastward across the rubble field.
    The column shafts are slightly irregular, weathered over two millennia.

    RUINED WALLS: Stretching from left to right across the middle ground, a
    broken horizontal line of stone walls, collapsed arches, and rubble mounds.
    The walls are in various states of decay: some still standing to several
    metres height, others reduced to scattered blocks. The stone is warm ochre
    and sienna limestone, darkened by time and vegetation.

    SEA: Visible in the right-center zone between the ruins and the sky, as a
    horizontal band of deep ultramarine -- the specific dark blue of the
    Mediterranean at dusk, neither green nor purple but a saturated mineral blue.
    The sea horizon is slightly curved, a reminder of distance.

    FOREGROUND: Raw earth: ochre, sienna, burnt umber. Scattered limestone
    fragments ranging from powder to large blocks. Low scrubby vegetation:
    patches of pale grey-green rosemary and sparse grass. The foreground reads
    as material -- grain and texture are as important as colour.

Technique & Palette:
    Jean Dubuffet's Art Brut approach applied to ancient Mediterranean ruins.
    The dubuffet_art_brut_pass contributes four transformations: (1) the cellular
    network scoring divides the ruined stone surfaces into irregular jigsaw regions
    separated by dark scored lines, as if the stones themselves were sections of
    an Hourloupe composition; (2) earth material grain adds coarse granularity to
    the ochre earth and limestone surfaces, making the paint read as actual
    compressed matter rather than smooth brushwork; (3) L1 palette contraction
    pulls the varied natural colours of stone, sky, and vegetation toward
    Dubuffet's five raw-material anchors -- bone white, raw umber, iron red,
    ochre, graphite -- creating the forceful flatness of the Hourloupe series;
    (4) edge darkening emphasizes the boundary between each ruined form with
    heavy scored lines, reading the architectural edges as Dubuffet would have
    drawn them: primitive, authoritative, anti-illusionistic. The impasto relief
    pass adds physical dimensionality to the paint surface, making the stone
    textures read as genuinely three-dimensional.

    Palette: deep indigo-violet (sky), burnt orange-crimson (horizon glow),
    warm ochre-yellow (lit column faces), cool grey-violet (shadowed stone),
    deep ultramarine (sea), raw umber (earth), graphite (scored outlines).

Mood & Intent:
    The painting intends to create a collision between the oldest civilization
    and the most aggressively anti-civilizational art style. Carthage was the
    most cosmopolitan city of the ancient Mediterranean; Dubuffet spent his career
    attacking cosmopolitan cultural sophistication. Applied to Carthage, Art Brut
    becomes a kind of violent archaeology: stripping the ruins back to raw matter,
    refusing the romantic nostalgia of conventional ruin painting (no Hubert
    Robert golden light, no Piranesi dramatic darkness), insisting instead on
    the physical presence of the stone itself -- its granularity, its ochre
    earthiness, its heavy outlines. The viewer should feel the weight of the stone
    and the flatness of the earth, and should sense that three thousand years of
    history compress into the same five colours: bone, umber, red, ochre, black.
    Paint with patience and practice, like a true artist.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stroke_engine import Painter

# ── Canvas dimensions ────────────────────────────────────────────────────────
W, H = 1440, 1040   # landscape -- panoramic ruin view
SEED = 289
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s289_carthage_dusk.png")


# ── Reference: procedural Carthage dusk scene ────────────────────────────────

def build_reference() -> np.ndarray:
    """Procedural Carthage at dusk reference.

    Zones:
      0.00-0.38 : sky (deep indigo zenith → burnt orange horizon)
      0.32-0.68 : columns + ruined walls (limestone, ochre, violet shadow)
      0.58-0.72 : sea band (deep ultramarine)
      0.65-1.00 : foreground earth (ochre, sienna, rubble)
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    yf = yy.astype(np.float32) / H
    xf = xx.astype(np.float32) / W

    rng = np.random.default_rng(SEED)

    # ── 1. Sky gradient ──────────────────────────────────────────────────────
    # Deep indigo at zenith (yf=0) → violet-magenta → burnt orange at horizon (yf~0.38)
    t_sky = np.clip(yf / 0.38, 0.0, 1.0).astype(np.float32)   # 0=zenith, 1=horizon

    # Zenith: deep indigo (0.08, 0.07, 0.22)
    # Horizon: burnt orange (0.88, 0.38, 0.08)
    # Use cubic ease for dramatic sunset banding
    t2 = (t_sky * t_sky * (3.0 - 2.0 * t_sky)).astype(np.float32)   # smoothstep

    sky_r = 0.08 + (0.88 - 0.08) * t2
    sky_g = 0.07 + (0.38 - 0.07) * t2
    sky_b = 0.22 + (0.08 - 0.22) * t2

    # Add magenta band in the middle of sky transition
    mag_zone = np.exp(-((t_sky - 0.55) ** 2) / (2 * 0.08 ** 2)).astype(np.float32)
    sky_r = np.clip(sky_r + 0.22 * mag_zone, 0.0, 1.0)
    sky_g = np.clip(sky_g - 0.04 * mag_zone, 0.0, 1.0)
    sky_b = np.clip(sky_b + 0.10 * mag_zone, 0.0, 1.0)

    ref[:, :, 0] = sky_r
    ref[:, :, 1] = sky_g
    ref[:, :, 2] = sky_b

    # Mask sky above horizon (yf < 0.40)
    sky_mask = (yf < 0.40)

    # ── 2. Stars ─────────────────────────────────────────────────────────────
    n_stars = 8
    for _ in range(n_stars):
        sy = int(rng.integers(0, int(H * 0.22)))
        sx = int(rng.integers(0, W))
        sb = float(rng.uniform(0.4, 0.75))
        ref[sy, sx, 0] = np.clip(ref[sy, sx, 0] + sb * 0.5, 0.0, 1.0)
        ref[sy, sx, 1] = np.clip(ref[sy, sx, 1] + sb * 0.5, 0.0, 1.0)
        ref[sy, sx, 2] = np.clip(ref[sy, sx, 2] + sb * 0.7, 0.0, 1.0)

    # ── 3. Sea band ──────────────────────────────────────────────────────────
    # Visible between top of walls (yf~0.56) and base of columns (yf~0.68)
    # and through gaps on the right side
    sea_top = 0.56; sea_bot = 0.70
    sea_right_cutoff = 0.38   # columns block left side
    t_sea = np.clip((yf - sea_top) / (sea_bot - sea_top), 0.0, 1.0).astype(np.float32)
    in_sea = (yf >= sea_top) & (yf <= sea_bot) & (xf >= sea_right_cutoff)

    sea_r = 0.06 + t_sea * 0.04
    sea_g = 0.10 + t_sea * 0.06
    sea_b = 0.42 + t_sea * 0.05   # deep ultramarine

    ref[:, :, 0] = np.where(in_sea, sea_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(in_sea, sea_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(in_sea, sea_b, ref[:, :, 2])

    # ── 4. Foreground earth ──────────────────────────────────────────────────
    fg_start = 0.68
    in_fg = (yf >= fg_start)

    # Gradient: lighter ochre at top of fg, darker umber toward bottom
    t_fg = np.clip((yf - fg_start) / (1.0 - fg_start), 0.0, 1.0).astype(np.float32)

    # Ochre-sienna-umber gradient
    fg_r = 0.72 - t_fg * 0.28
    fg_g = 0.52 - t_fg * 0.28
    fg_b = 0.18 - t_fg * 0.08

    # Add coarse earthy noise
    noise_fg = rng.uniform(0.0, 1.0, (H, W)).astype(np.float32)
    fg_r = np.clip(fg_r + (noise_fg - 0.5) * 0.12, 0.0, 1.0)
    fg_g = np.clip(fg_g + (noise_fg - 0.5) * 0.10, 0.0, 1.0)
    fg_b = np.clip(fg_b + (noise_fg - 0.5) * 0.06, 0.0, 1.0)

    ref[:, :, 0] = np.where(in_fg, fg_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(in_fg, fg_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(in_fg, fg_b, ref[:, :, 2])

    # Scattered limestone rubble patches in foreground
    n_rubble = 18
    for _ in range(n_rubble):
        ry = int(rng.integers(int(H * 0.72), int(H * 0.95)))
        rx = int(rng.integers(0, W))
        rw = int(rng.integers(15, 55))
        rh = int(rng.integers(8, 22))
        r1 = max(0, ry - rh // 2); r2 = min(H, ry + rh // 2)
        c1 = max(0, rx - rw // 2); c2 = min(W, rx + rw // 2)
        lum_r = float(rng.uniform(0.72, 0.90))   # pale limestone
        ref[r1:r2, c1:c2, 0] = np.clip(lum_r + 0.0, 0.0, 1.0)
        ref[r1:r2, c1:c2, 1] = np.clip(lum_r - 0.08, 0.0, 1.0)
        ref[r1:r2, c1:c2, 2] = np.clip(lum_r - 0.22, 0.0, 1.0)

    # Low scrub vegetation patches
    n_scrub = 12
    for _ in range(n_scrub):
        sy = int(rng.integers(int(H * 0.70), int(H * 0.90)))
        sx = int(rng.integers(0, W))
        sw = int(rng.integers(20, 60))
        sh = int(rng.integers(10, 28))
        r1 = max(0, sy - sh // 2); r2 = min(H, sy + sh // 2)
        c1 = max(0, sx - sw // 2); c2 = min(W, sx + sw // 2)
        ref[r1:r2, c1:c2, 0] = np.clip(ref[r1:r2, c1:c2, 0] * 0.62 + 0.14, 0.0, 1.0)
        ref[r1:r2, c1:c2, 1] = np.clip(ref[r1:r2, c1:c2, 1] * 0.70 + 0.18, 0.0, 1.0)
        ref[r1:r2, c1:c2, 2] = np.clip(ref[r1:r2, c1:c2, 2] * 0.55 + 0.08, 0.0, 1.0)

    # ── 5. Ruined walls (middle ground) ─────────────────────────────────────
    # Irregular horizontal band of stone walls
    wall_top = 0.50; wall_bot = 0.72

    # Base wall color: warm ochre-limestone
    # Wall presence: irregular "top edge" profile across width
    rng2 = np.random.default_rng(SEED + 10)
    # Wall profile: rough top edge varies with x position
    wall_profile_x = np.linspace(0.0, 1.0, W, dtype=np.float32)

    # Generate jagged wall tops using random harmonics
    wall_top_y = np.zeros(W, dtype=np.float32)
    for freq in [2.5, 5.0, 8.0, 13.0, 21.0]:
        amp = float(rng2.uniform(0.012, 0.040))
        phase = float(rng2.uniform(0.0, 2 * np.pi))
        wall_top_y += amp * np.sin(freq * np.pi * wall_profile_x + phase)

    wall_top_y = wall_top + 0.05 + wall_top_y
    wall_top_y = np.clip(wall_top_y, wall_top, wall_bot - 0.04)

    for col in range(W):
        wt = int(wall_top_y[col] * H)
        wb = int(wall_bot * H)
        if wt >= wb:
            continue

        # Base limestone color with slight variation
        noise_col = float(rng2.uniform(-0.06, 0.06))
        stone_r = 0.72 + noise_col
        stone_g = 0.58 + noise_col * 0.7
        stone_b = 0.32 + noise_col * 0.4

        # Left portion (shadow): cooler, more grey
        if col < W * 0.40:
            stone_r = 0.52 + noise_col
            stone_g = 0.48 + noise_col * 0.7
            stone_b = 0.42 + noise_col * 0.3

        ref[wt:wb, col, 0] = np.clip(stone_r, 0.0, 1.0)
        ref[wt:wb, col, 1] = np.clip(stone_g, 0.0, 1.0)
        ref[wt:wb, col, 2] = np.clip(stone_b, 0.0, 1.0)

    # ── 6. Columns ───────────────────────────────────────────────────────────
    # Three tall Corinthian columns, left-center zone
    col_tops    = [0.32, 0.28, 0.35]   # yf of column top (capital)
    col_bots    = [0.72, 0.72, 0.72]   # yf of column base
    col_centers = [0.18, 0.26, 0.34]   # xf of column center
    col_widths  = [0.022, 0.018, 0.020] # xf width

    for ctr, bot, cx, cw in zip(col_tops, col_bots, col_centers, col_widths):
        ct_px = int(ctr * H)
        cb_px = int(bot * H)
        cl_px = max(0, int((cx - cw / 2) * W))
        cr_px = min(W, int((cx + cw / 2) * W))

        # Column shaft: warm ochre lit face, cool grey shadow
        # Light comes from west (left side of column → west face = lit)
        for row in range(ct_px, cb_px):
            for col in range(cl_px, cr_px):
                t_col = (col - cl_px) / max(cr_px - cl_px - 1, 1)   # 0=left, 1=right
                # Left face: lit by setting sun (warm) -- right: shadow (cool)
                lit_r = 0.88 - t_col * 0.30
                lit_g = 0.72 - t_col * 0.28
                lit_b = 0.38 - t_col * 0.10 + t_col * 0.12

                # Vertical wear: random darker bands simulating horizontal joints
                t_row = (row - ct_px) / max(cb_px - ct_px - 1, 1)
                joint = 0.85 + 0.15 * np.sin(t_row * 22.0)
                ref[row, col, 0] = np.clip(lit_r * joint, 0.0, 1.0)
                ref[row, col, 1] = np.clip(lit_g * joint, 0.0, 1.0)
                ref[row, col, 2] = np.clip(lit_b * joint, 0.0, 1.0)

        # Column capital (top): slightly wider, more decoration
        cap_h = max(int((ctr + 0.035) * H), ct_px)
        cap_extra = int(cw * W * 0.4)
        cl_cap = max(0, cl_px - cap_extra)
        cr_cap = min(W, cr_px + cap_extra)
        ref[ct_px:cap_h, cl_cap:cr_cap, 0] = np.clip(0.88 * 0.95, 0.0, 1.0)
        ref[ct_px:cap_h, cl_cap:cr_cap, 1] = np.clip(0.72 * 0.95, 0.0, 1.0)
        ref[ct_px:cap_h, cl_cap:cr_cap, 2] = np.clip(0.40 * 0.95, 0.0, 1.0)

    # ── 7. Column shadows on ground (eastward) ───────────────────────────────
    for cx, cw in zip(col_centers, col_widths):
        # Long shadow stretching right and down from each column
        shadow_len_x = 0.22   # how far right the shadow extends
        shadow_start_y = 0.68
        shadow_end_y   = 0.78
        sl_x = cx
        sr_x = min(1.0, cx + shadow_len_x)
        st_y = int(shadow_start_y * H)
        sb_y = int(shadow_end_y * H)
        sl_px = max(0, int(sl_x * W))
        sr_px = min(W, int(sr_x * W))
        if st_y < sb_y and sl_px < sr_px:
            ref[st_y:sb_y, sl_px:sr_px, 0] *= 0.60
            ref[st_y:sb_y, sl_px:sr_px, 1] *= 0.60
            ref[st_y:sb_y, sl_px:sr_px, 2] *= 0.68

    return np.clip(ref, 0.0, 1.0)


# ── Main ─────────────────────────────────────────────────────────────────────

print(f"Session 289: Dubuffet (200th mode) — The Ruins of Carthage at Dusk")
print(f"Canvas: {W}×{H}  seed={SEED}")

print("Building procedural reference...")
ref_f32 = build_reference()
# Convert to uint8 for Painter (engine expects 0-255 range)
ref = (ref_f32 * 255).astype(np.uint8)

print("Initializing painter...")
p = Painter(W, H, seed=SEED)

# Ground: raw ochre-sienna earth — Dubuffet's toned ground
p.tone_ground(color=(0.42, 0.32, 0.18), texture_strength=0.025)

# Underpainting: structural monochrome
print("Pass: underpainting...")
p.underpainting(ref, stroke_size=54, n_strokes=250, dry_amount=0.88)

# Block-in: broad masses — sky, walls, earth
print("Pass: block_in (broad)...")
p.block_in(ref, stroke_size=36, n_strokes=490, dry_amount=0.76)
print("Pass: block_in (medium)...")
p.block_in(ref, stroke_size=22, n_strokes=510, dry_amount=0.70)

# Build form: column volumes, wall textures, foreground detail
print("Pass: build_form (medium)...")
p.build_form(ref, stroke_size=14, n_strokes=560, dry_amount=0.62)
print("Pass: build_form (fine)...")
p.build_form(ref, stroke_size=7,  n_strokes=460, dry_amount=0.54)

# Place lights: horizon glow, lit column faces, rubble highlights
print("Pass: place_lights...")
p.place_lights(ref, stroke_size=4, n_strokes=310)

# Improvement pass: impasto relief lighting
print("Pass: paint_impasto_relief_pass...")
p.paint_impasto_relief_pass(
    sigma_thickness=2.8,
    relief_strength=0.50,
    light_az=-0.55,
    light_el=-0.62,
    ambient=0.14,
    specular_amount=0.28,
    specular_power=14.0,
    opacity=0.62,
)

# Artist pass: Dubuffet Art Brut (200th mode)
print("Pass: dubuffet_art_brut_pass...")
p.dubuffet_art_brut_pass(
    cell_freq_a=0.042,
    cell_freq_b=0.031,
    cell_freq_c=0.058,
    cell_freq_d=0.027,
    cell_line_width=0.030,
    cell_line_dark=0.72,
    grain_strength=0.055,
    grain_seed=289,
    palette_strength=0.38,
    edge_dark_strength=0.60,
    edge_dark_sigma=1.2,
    opacity=0.82,
)

print(f"Saving → {OUTPUT}")
p.save(OUTPUT)
print("Done.")
