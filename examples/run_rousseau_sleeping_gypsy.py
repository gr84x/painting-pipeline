"""
run_rousseau_sleeping_gypsy.py — Session 202

"The Gypsy Sleeps While the Lion Watches" — after Henri Rousseau

Image Description
─────────────────
Subject & Composition
    A lone sleeping figure — a wandering gypsy musician — lies on their back
    on a flat desert plain, viewed from a low vantage point at ground level,
    from slightly to the right and several metres back.  The figure occupies
    the lower-centre third of the canvas in a horizontal band.  Towering
    above and behind, to the upper-left, a full ivory moon hangs in a flat
    indigo-violet sky.  A lion stands at the right edge of the canvas,
    front-facing, watching the sleeper with golden curious eyes — not
    threatening, not retreating.  On the near side of the figure: a mandolin,
    lying on its back in the dirt, strings catching moonlight.  A ceramic
    water jug rests near the figure's feet.  The horizon is a single flat
    dark line where the sandy plain meets the theatrical sky.

The Figure
    The gypsy lies fully supine, arms folded loosely across their chest.
    They wear a white and ochre-striped robe that drapes in flat, Rousseau-
    like stacked folds — no volumetric shading, each stripe a uniform flat
    band of colour.  The face is turned slightly to the right, eyes closed,
    expression utterly peaceful — a sleep too deep for the desert, too
    unguarded for the world.  A dark cloth is bound loosely around their
    head; a long walking staff rests beside them.  The skin is warm amber-
    ochre, picked out by the sourceless moonlight.  Emotional state: absolute
    surrender to sleep; the lion and the moon and the desert do not intrude.

The Environment
    The desert plain is flat and featureless — a dark sandy ground that
    fades to near-black indigo at the horizon.  There is no rock, no tree,
    no landmark.  The sky is Rousseau's impossible flat blue-violet: a single
    uniform tonal field broken only by the ivory disk of the moon, surrounded
    by a faint halo of warm amber.  No stars are visible — the sky is a
    painted flat backdrop.  The lion's sandy-tawny coat catches the same
    sourceless moonlight as the gypsy's robe: its mane is dark, its body
    pale gold.  At the very bottom foreground: the sand grain — the only
    texture in the scene — rendered as a fine horizontal band of warm
    ivory-ochre.

Technique & Palette
    Henri Rousseau's Naïve / Post-Impressionist technique: smooth, thin
    paint coats with no visible brushwork; each element — the sky, the
    ground, the figure, the lion, the moon — painted as a discrete flat
    luminance zone separated from its neighbour by a crisp silhouette edge.
    Rousseau Naïve Luminance pass (113th distinct mode) as the primary
    chromatic effect — void band deepens to indigo-black, foliage band
    (here: the dark ground and lion shadow) receives deep-green tint,
    mid-lit band (figure robe, lion body, moonlit sand) pushed toward warm
    amber, highlight band (moon disk, robe stripe, mandolin body) pushed
    toward cool ivory.  Sky vignette at the top injects theatrical
    blue-violet without disturbing the foreground.

    Palette: near-black indigo void, deep dark-green ground, moonlit amber-
    gold, cool ivory-white, theatrical sky blue-violet, tawny lion gold,
    warm ochre skin, striped robe white and ochre.

Mood & Intent
    The image asks a question Rousseau posed in the original 1897 canvas:
    what is the difference between the dreamer and the dreamed?  The lion
    does not attack because the gypsy is somewhere else entirely — the music
    from the mandolin still drifting in the air, audible to the lion, holds
    the scene suspended.  The moon is impassive.  The desert is impassive.
    The lion is merely curious.  Intended emotions: stillness, mystery, the
    particular peace of someone who has given themselves over completely
    to sleep in a dangerous place — and found, to their unconscious
    surprise, that the danger has become a guardian.

Session 202 pass used:
    rousseau_naive_luminance_pass  (113th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "rousseau_sleeping_gypsy.png"
)
W, H = 960, 1100   # landscape-ish portrait — wide flat desert, tall sky


def build_reference() -> np.ndarray:
    """
    Synthetic reference for 'The Gypsy Sleeps While the Lion Watches'.

    Tonal zones:
      - Sky (upper 55%): flat indigo-violet with ivory moon disk
      - Desert plain (lower 45%): dark sandy ground fading to near-black at horizon
      - Sleeping figure (centre-lower): horizontal band, striped robe
      - Lion (right side): tawny gold silhouette
      - Mandolin (near figure): warm amber shape with ivory highlights
      - Moon halo: soft warm amber ring around ivory disk
    """
    rng = np.random.default_rng(202)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # Horizon sits at 52% of canvas height
    horizon_y = 0.52

    # ── Sky: flat theatrical blue-violet ─────────────────────────────────────
    sky_col = np.array([0.18, 0.20, 0.45])   # Rousseau flat sky
    sky_mask = np.clip(1.0 - (ys - 0.0) / (horizon_y + 0.01), 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] += sky_col[ch] * sky_mask

    # ── Desert ground: dark sandy plain ──────────────────────────────────────
    ground_col_far  = np.array([0.10, 0.10, 0.15])   # near-black indigo at horizon
    ground_col_near = np.array([0.38, 0.30, 0.18])   # warm sandy-ochre near viewer
    # Lerp from far to near across the ground zone
    ground_t = np.clip((ys - horizon_y) / (1.0 - horizon_y + 1e-6), 0.0, 1.0)
    for ch in range(3):
        ground_col = ground_col_far[ch] * (1 - ground_t) + ground_col_near[ch] * ground_t
        ref[:, :, ch] += ground_col * (1.0 - sky_mask)

    # Fine sand texture at ground level
    sand_noise = rng.random((H, W)).astype(np.float32)
    sand_smooth = gaussian_filter(sand_noise, sigma=1.5)
    sand_texture = (sand_smooth - 0.5) * 0.06
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + sand_texture * (1.0 - sky_mask), 0.0, 1.0)

    # ── Moon disk: ivory disk, upper-left sky ─────────────────────────────────
    moon_cx, moon_cy = 0.30, 0.20
    moon_r = 0.08
    moon_dist = np.sqrt((xs - moon_cx) ** 2 + (ys - moon_cy) ** 2)
    moon_mask = np.clip(1.0 - moon_dist / moon_r, 0.0, 1.0) ** 1.5
    moon_col = np.array([0.92, 0.90, 0.80])   # ivory moonlight
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - moon_mask) + moon_col[ch] * moon_mask

    # Moon halo: soft warm amber glow around moon disk
    halo_r = moon_r * 2.8
    halo_mask = np.clip(
        (1.0 - moon_dist / halo_r) * (1.0 - moon_mask), 0.0, 1.0
    ) ** 1.8
    halo_col = np.array([0.55, 0.48, 0.22])   # warm amber halo
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - halo_mask * 0.55) + halo_col[ch] * halo_mask * 0.55

    # ── Sleeping figure: horizontal band, centre-lower ────────────────────────
    fig_cx   = 0.44   # slightly left of centre
    fig_cy   = 0.72   # on the desert plain
    fig_half_w = 0.30
    fig_half_h = 0.06

    fig_dist = np.sqrt(
        ((xs - fig_cx) / fig_half_w) ** 2 + ((ys - fig_cy) / fig_half_h) ** 2
    )
    fig_mask = np.clip(1.0 - fig_dist ** 1.8, 0.0, 1.0)

    # Robe base: warm ivory-ochre ground
    robe_col = np.array([0.88, 0.82, 0.60])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - fig_mask) + robe_col[ch] * fig_mask

    # Robe stripes: alternating ochre and white horizontal bands
    stripe_freq = 18.0
    stripe_t = np.clip(np.sin((xs - (fig_cx - fig_half_w)) * stripe_freq * math.pi) * 0.5 + 0.5, 0.0, 1.0)
    stripe_a_col = np.array([0.78, 0.62, 0.22])   # ochre stripe
    stripe_b_col = np.array([0.94, 0.90, 0.78])   # white stripe
    for ch in range(3):
        stripe_col = stripe_a_col[ch] * (1 - stripe_t) + stripe_b_col[ch] * stripe_t
        ref[:, :, ch] = ref[:, :, ch] * (1 - fig_mask * 0.70) + stripe_col * fig_mask * 0.70

    # Head: dark cloth binding at left end of figure
    head_cx = fig_cx - fig_half_w * 0.82
    head_cy = fig_cy - 0.015
    head_dist = np.sqrt(
        ((xs - head_cx) / 0.048) ** 2 + ((ys - head_cy) / 0.055) ** 2
    )
    head_mask = np.clip(1.0 - head_dist ** 1.8, 0.0, 1.0)
    # Face: warm amber skin
    face_col = np.array([0.72, 0.52, 0.22])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - head_mask) + face_col[ch] * head_mask
    # Dark cloth on upper head
    cloth_cy = head_cy - 0.020
    cloth_dist = np.sqrt(
        ((xs - head_cx) / 0.038) ** 2 + ((ys - cloth_cy) / 0.025) ** 2
    )
    cloth_mask = np.clip(1.0 - cloth_dist ** 2.0, 0.0, 1.0)
    cloth_col = np.array([0.18, 0.14, 0.10])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - cloth_mask) + cloth_col[ch] * cloth_mask

    # Walking staff: thin dark diagonal line beside figure
    staff_cx = fig_cx - fig_half_w * 0.68
    staff_angle = 0.12   # slight diagonal
    for ch in range(3):
        staff_col_val = 0.22
        staff_x_from_centre = xs - staff_cx
        staff_y_from_top = ys - (fig_cy - 0.14)
        staff_line_dist = np.abs(staff_x_from_centre - staff_y_from_top * staff_angle)
        staff_mask = np.clip(1.0 - staff_line_dist / 0.006, 0.0, 1.0)
        staff_len_mask = np.where(
            (ys >= fig_cy - 0.16) & (ys <= fig_cy + fig_half_h * 1.1), 1.0, 0.0
        )
        ref[:, :, ch] = ref[:, :, ch] * (1 - staff_mask * staff_len_mask * 0.85) + \
                        staff_col_val * staff_mask * staff_len_mask * 0.85

    # ── Mandolin: warm amber oval near figure's torso ─────────────────────────
    mand_cx = fig_cx + 0.02
    mand_cy = fig_cy + 0.085
    mand_hw = 0.072
    mand_hh = 0.038
    mand_dist = np.sqrt(
        ((xs - mand_cx) / mand_hw) ** 2 + ((ys - mand_cy) / mand_hh) ** 2
    )
    mand_mask = np.clip(1.0 - mand_dist ** 2.0, 0.0, 1.0)
    mand_col = np.array([0.55, 0.38, 0.12])   # warm amber-brown mandolin body
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - mand_mask) + mand_col[ch] * mand_mask
    # Mandolin strings: faint bright lines across the body
    string_x = mand_cx + (xs - mand_cx) * 0.0
    strings_dist = np.abs(np.sin((xs - (mand_cx - mand_hw)) / (mand_hw * 2) * math.pi * 5))
    strings_mask = np.clip(1.0 - strings_dist / 0.25, 0.0, 1.0) * mand_mask
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + strings_mask * 0.30, 0.0, 1.0)

    # Water jug: rounded dark shape near figure's feet
    jug_cx = fig_cx + fig_half_w * 0.88
    jug_cy = fig_cy + 0.005
    jug_dist = np.sqrt(
        ((xs - jug_cx) / 0.028) ** 2 + ((ys - jug_cy) / 0.040) ** 2
    )
    jug_mask = np.clip(1.0 - jug_dist ** 2.2, 0.0, 1.0)
    jug_col = np.array([0.28, 0.22, 0.18])   # dark terracotta jug
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - jug_mask) + jug_col[ch] * jug_mask

    # ── Lion: right side, tawny silhouette ────────────────────────────────────
    lion_cx  = 0.82
    lion_cy  = 0.68
    lion_hw  = 0.14
    lion_hh  = 0.15
    lion_dist = np.sqrt(
        ((xs - lion_cx) / lion_hw) ** 2 + ((ys - lion_cy) / lion_hh) ** 2
    )
    lion_body = np.clip(1.0 - lion_dist ** 1.5, 0.0, 1.0)
    lion_col = np.array([0.68, 0.52, 0.22])   # tawny sandy lion gold
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - lion_body) + lion_col[ch] * lion_body

    # Lion head: slightly raised above body
    lion_head_cx = lion_cx - 0.010
    lion_head_cy = lion_cy - lion_hh * 0.72
    lion_head_dist = np.sqrt(
        ((xs - lion_head_cx) / 0.065) ** 2 + ((ys - lion_head_cy) / 0.060) ** 2
    )
    lion_head = np.clip(1.0 - lion_head_dist ** 1.8, 0.0, 1.0)
    lion_face = np.array([0.75, 0.60, 0.28])   # slightly lighter face
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - lion_head) + lion_face[ch] * lion_head

    # Mane: dark ring around the head
    mane_dist = np.sqrt(
        ((xs - lion_head_cx) / 0.090) ** 2 + ((ys - lion_head_cy) / 0.082) ** 2
    )
    mane_ring = np.clip(
        (1.0 - mane_dist ** 1.2) - lion_head * 0.70, 0.0, 1.0
    )
    mane_col = np.array([0.22, 0.16, 0.08])   # dark brown-black mane
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - mane_ring * 0.85) + mane_col[ch] * mane_ring * 0.85

    # Lion eyes: two small amber-gold points
    for eye_x_off, eye_y_off in [(-0.020, -0.010), (0.020, -0.010)]:
        eye_cx = lion_head_cx + eye_x_off
        eye_cy = lion_head_cy + eye_y_off
        eye_dist = np.sqrt(
            ((xs - eye_cx) / 0.010) ** 2 + ((ys - eye_cy) / 0.009) ** 2
        )
        eye_m = np.clip(1.0 - eye_dist ** 2.0, 0.0, 1.0)
        eye_c = np.array([0.92, 0.72, 0.10])   # amber-gold lion eyes
        for ch in range(3):
            ref[:, :, ch] = ref[:, :, ch] * (1 - eye_m) + eye_c[ch] * eye_m

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'The Gypsy Sleeps While the Lion Watches' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=202)

    # ── Ground: deep dark-green — Rousseau's jungle-origin palette ────────────
    p.tone_ground((0.12, 0.18, 0.10), texture_strength=0.012)

    # ── Underpainting: establish the sky, plain, and main shapes ──────────────
    p.underpainting(ref_pil, stroke_size=60)

    # ── Block in: flat broad zones — sky, ground, figure, lion masses ─────────
    p.block_in(ref_pil, stroke_size=24)

    # ── Build form: robe stripes, lion silhouette, moon disk ──────────────────
    p.build_form(ref_pil, stroke_size=10)

    # ── Lights: ivory moon disk, robe white stripes, mandolin highlight ────────
    p.place_lights(ref_pil, stroke_size=5)

    # ── Rousseau Naïve Luminance — THE signature effect ───────────────────────
    # Primary pass: full stratification — deepen voids, green the ground,
    # amber the mid-lit figure and lion, ivory the moon and robe highlights
    p.rousseau_naive_luminance_pass(
        void_strength=0.58,
        foliage_strength=0.45,
        midlit_strength=0.50,
        highlight_strength=0.42,
        sky_strength=0.38,
        void_color=(0.06, 0.06, 0.18),
        foliage_color=(0.08, 0.28, 0.10),
        midlit_color=(0.75, 0.65, 0.25),
        highlight_color=(0.90, 0.88, 0.78),
        sky_color=(0.22, 0.28, 0.58),
        opacity=0.76,
    )

    # Second pass: gently deepen the stratification without overwriting detail
    p.rousseau_naive_luminance_pass(
        void_strength=0.30,
        foliage_strength=0.22,
        midlit_strength=0.28,
        highlight_strength=0.20,
        sky_strength=0.20,
        opacity=0.32,
    )

    # ── Tonal compression: Rousseau's airless, matte surface ──────────────────
    p.tonal_compression_pass(shadow_lift=0.02, highlight_compress=0.97, midtone_contrast=0.04)

    # ── Edge definition: crisp silhouette edges — figure against ground,
    #    lion against sky, moon disk boundary ─────────────────────────────────
    p.edge_definition_pass(strength=0.28, opacity=0.22)

    # ── Meso detail: subtle surface refinement on lion fur and robe folds ─────
    p.meso_detail_pass(strength=0.12, opacity=0.10)

    # ── No impasto glaze — Rousseau used none; smooth immaculate surface ──────

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
