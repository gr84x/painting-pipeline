"""
run_ensor_brussels_procession.py — Session 201

"The Procession of Hollow Faces" — after James Ensor

Image Description
─────────────────
Subject & Composition
    A dense carnival procession viewed from a low vantage point slightly behind
    and to the right of a central masked figure.  The crowd fills the canvas
    edge to edge — no sky, no empty ground, only press of bodies.  The central
    figure is taller than the crowd and turned three-quarters back toward the
    viewer: its carnival mask — white, expressionless, with painted black eye
    hollows — is the only still point in the churning mass.  Around it: a
    chaos of hats, feathered headpieces, smaller masks, banners in crimson and
    carnival blue, arms raised in celebration or alarm.  No individual face is
    readable except the central mask.  The crowd presses forward and to the
    left; the central figure holds its ground.

The Figure
    The central figure is tall, dressed in a dark coat with a wide-brimmed hat
    above the white mask.  The mask is Ensor's signature commedia dell'arte
    blank: oval, smooth, the eye hollows painted deep indigo-black, two red
    spots high on the cheeks like fever or rouge.  The coat is dark charcoal —
    almost black — which makes the mask float.  The figure's posture is upright,
    slightly stiff — not a performer, not a reveller.  It witnesses.  The
    emotional state: detachment within chaos.  The crowd does not quite touch
    it.  There is a half-inch of stillness around it.  The crowd swarms; the
    figure simply stands.

The Environment
    No outdoor space is visible — the crowd is the environment.  At the top
    edge, a fragment of a red-and-gold carnival banner stretches across; at
    left, a yellow pennant.  At the right edge, the corner of a stone building
    is barely visible — medieval Belgian architecture, a pale ochre stone.
    The foreground is cobblestones just visible at the very bottom: dark grey,
    glistening, partially obscured by feet and the hem of coats.  The crowd's
    costumes are garish and varied: acid yellow, carnival blue, lime green,
    crimson, violet.  The overall chromatic energy of the crowd is maximum
    dissonance — every adjacent figure wears a complementary colour to its
    neighbour.  The sky is absent; the crowd is sky and ground and horizon.

Technique & Palette
    James Ensor's Belgian Expressionist / Symbolist technique: warm ochre
    ground visible in passages, thick loaded impasto strokes of pure colour
    placed without blending, acidic complementary clashes.  Ensor Carnival
    Mask pass (112th distinct mode) as the primary chromatic effect —
    bidirectional chroma polarization amplifies warm zones warmer and cool
    zones cooler while simultaneously injecting the complement as a ghost,
    producing the chromatic dissonance Ensor cultivated.  Stochastic impasto
    sparkle catches paint ridges in raking light.  Ochre ground reveal
    shows through the darkest passages.

    Palette: warm ochre ground, acid golden-yellow, burnt orange-red,
    vivid carnival blue, carnival violet, acidic lime-green, near-white mask,
    near-black void, crimson-rose.

Mood & Intent
    The image asks what it means to look at a crowd and see no faces — only
    masks.  Ensor said his carnival figures were not caricatures but portraits:
    the mask is the true face, and beneath it is the void he painted as
    near-black.  The central figure does not celebrate and does not flee.  It
    observes.  The viewer is given Ensor's own vantage point — inside the
    procession, close enough to smell the paint, far enough to see that no
    one here is real.  The emotion intended: unease beneath festivity.
    The sense that the carnival has been going on for a very long time and
    will not stop.

Session 201 pass used:
    ensor_carnival_mask_pass  (112th distinct mode)
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
    os.path.dirname(os.path.abspath(__file__)), "ensor_brussels_procession.png"
)
W, H = 960, 1120   # portrait — crowd fills the frame, no horizon escape


def build_reference() -> np.ndarray:
    """
    Synthetic reference for 'The Procession of Hollow Faces'.

    Tonal zones:
      - Crowd mass: warm ochre ground with garish chromatic noise
      - Central masked figure: dark coat, pale oval mask
      - Banner strip: crimson-gold at top
      - Cobblestones: dark grey at bottom edge
      - Stone corner: pale ochre stone at right edge
    """
    rng = np.random.default_rng(201)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Warm ochre ground base ────────────────────────────────────────────────
    ground = np.array([0.72, 0.62, 0.32])
    for ch in range(3):
        ref[:, :, ch] = ground[ch]

    # ── Crowd noise: dense chromatic patches representing figures ─────────────
    # Generate multiple scales of noise and map to carnival colours
    crowd_noise_r = rng.random((H, W)).astype(np.float32)
    crowd_noise_g = rng.random((H, W)).astype(np.float32)
    crowd_noise_b = rng.random((H, W)).astype(np.float32)

    # Blur at several scales — different figures at different distances
    crowd_r  = gaussian_filter(crowd_noise_r, sigma=18.0)
    crowd_g  = gaussian_filter(crowd_noise_g, sigma=14.0)
    crowd_b  = gaussian_filter(crowd_noise_b, sigma=22.0)

    # Normalise each to [0, 1]
    def norm(a):
        mn, mx = a.min(), a.max()
        return (a - mn) / (mx - mn + 1e-8)

    crowd_r = norm(crowd_r)
    crowd_g = norm(crowd_g)
    crowd_b = norm(crowd_b)

    # Map through Ensor's carnival palette:
    # Palette: yellow (0.88,0.72,0.18), orange-red (0.82,0.35,0.12),
    #          blue (0.18,0.42,0.78), violet (0.55,0.18,0.62),
    #          lime (0.28,0.68,0.32), crimson (0.78,0.22,0.30)
    ensor_palette = np.array([
        [0.88, 0.72, 0.18],   # yellow
        [0.82, 0.35, 0.12],   # orange-red
        [0.18, 0.42, 0.78],   # blue
        [0.55, 0.18, 0.62],   # violet
        [0.28, 0.68, 0.32],   # lime
        [0.78, 0.22, 0.30],   # crimson
    ], dtype=np.float32)

    # Assign crowd patches by quantising the noise into palette buckets
    palette_idx = (crowd_r * 5.999).astype(int)   # 0–5 index
    for ch in range(3):
        palette_col = np.zeros((H, W), dtype=np.float32)
        for i, col in enumerate(ensor_palette):
            palette_col = np.where(palette_idx == i, col[ch], palette_col)
        # Blend strongly into the ochre ground
        ref[:, :, ch] = ref[:, :, ch] * 0.30 + palette_col * 0.70

    # Add fine noise for brushstroke texture
    fine_noise = (rng.random((H, W)).astype(np.float32) - 0.5) * 0.08
    fine_noise = gaussian_filter(fine_noise, sigma=1.2)
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + fine_noise, 0.0, 1.0)

    # ── Dark zones: figure boundaries and shadow passages ────────────────────
    # Large-scale dark blobs for dark-coated figures in the crowd
    dark_noise = rng.random((H, W)).astype(np.float32)
    dark_smooth = gaussian_filter(dark_noise, sigma=30.0)
    dark_smooth = norm(dark_smooth)
    dark_mask = np.clip((dark_smooth - 0.62) * 4.0, 0.0, 1.0)
    dark_col = np.array([0.10, 0.08, 0.06])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - dark_mask * 0.75) + dark_col[ch] * dark_mask * 0.75

    # ── Banner strip at top: crimson-gold ────────────────────────────────────
    banner_h = 0.06
    banner_mask = np.clip(1.0 - ys / (banner_h + 0.01), 0.0, 1.0)
    banner_col = np.array([0.82, 0.35, 0.12])   # crimson-orange banner
    # Add alternating crimson / yellow stripes
    stripe_freq = 14
    stripe = np.clip(np.sin(xs * stripe_freq * math.pi) * 0.5 + 0.5, 0.0, 1.0)
    banner_r_col = banner_col[0] * (1 - stripe) + 0.88 * stripe
    banner_g_col = banner_col[1] * (1 - stripe) + 0.72 * stripe
    banner_b_col = banner_col[2] * (1 - stripe) + 0.18 * stripe
    for ch, bc in enumerate([banner_r_col, banner_g_col, banner_b_col]):
        ref[:, :, ch] = ref[:, :, ch] * (1 - banner_mask * 0.85) + bc * banner_mask * 0.85

    # ── Cobblestones at bottom edge ───────────────────────────────────────────
    cobble_h = 0.10
    cobble_mask = np.clip((ys - (1.0 - cobble_h)) / (cobble_h + 0.01), 0.0, 1.0)
    cobble_noise = rng.random((H, W)).astype(np.float32)
    cobble_smooth = gaussian_filter(cobble_noise, sigma=3.0)
    cobble_smooth = norm(cobble_smooth)
    cobble_grid = (np.abs(np.sin(xs * 20 * math.pi)) * np.abs(np.sin(ys * 8 * math.pi))) ** 0.3
    cobble_base = np.array([0.25, 0.22, 0.18])   # dark grey cobblestone
    cobble_col  = np.array([0.32, 0.28, 0.22])   # slightly lighter mortar
    for ch in range(3):
        cobble_c = cobble_base[ch] * (1 - cobble_grid) + cobble_col[ch] * cobble_grid
        cobble_c = cobble_c + cobble_smooth * 0.06 - 0.03
        ref[:, :, ch] = ref[:, :, ch] * (1 - cobble_mask * 0.80) + cobble_c * cobble_mask * 0.80

    # ── Central masked figure ─────────────────────────────────────────────────
    fig_cx = 0.48
    fig_cy = 0.50   # vertical centre

    # Body: tall dark coat
    body_top_y = 0.12
    body_bot_y = 0.96
    body_hw    = 0.075
    body_dist  = np.sqrt(
        ((xs - fig_cx) / body_hw) ** 2 + ((ys - fig_cy) / 0.42) ** 2
    )
    body_mask = np.clip(1.0 - body_dist ** 1.2, 0.0, 1.0)
    body_vert = np.where((ys >= body_top_y) & (ys <= body_bot_y), 1.0, 0.0)
    body_mask = body_mask * body_vert
    body_col  = np.array([0.10, 0.08, 0.07])   # near-black charcoal coat
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - body_mask) + body_col[ch] * body_mask

    # Hat above the mask
    hat_cx = fig_cx + 0.012   # slight tilt
    hat_cy = 0.20
    hat_hw = 0.095
    hat_hh = 0.065
    hat_dist = np.sqrt(
        ((xs - hat_cx) / hat_hw) ** 2 + ((ys - hat_cy) / hat_hh) ** 2
    )
    hat_mask = np.clip(1.0 - hat_dist ** 1.5, 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - hat_mask) + body_col[ch] * hat_mask

    # Hat brim: wider, flatter
    brim_cy = hat_cy + hat_hh * 0.9
    brim_hw = hat_hw * 1.6
    brim_hh = hat_hh * 0.22
    brim_dist = np.sqrt(
        ((xs - hat_cx) / brim_hw) ** 2 + ((ys - brim_cy) / brim_hh) ** 2
    )
    brim_mask = np.clip(1.0 - brim_dist ** 2.0, 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - brim_mask) + body_col[ch] * brim_mask

    # Mask face: white oval, slightly taller than wide
    mask_cx = fig_cx + 0.010   # slight turn — three-quarters view
    mask_cy = 0.33
    mask_hw = 0.052
    mask_hh = 0.072
    mask_dist = np.sqrt(
        ((xs - mask_cx) / mask_hw) ** 2 + ((ys - mask_cy) / mask_hh) ** 2
    )
    mask_face = np.clip(1.0 - mask_dist ** 2.5, 0.0, 1.0)
    mask_col  = np.array([0.94, 0.92, 0.88])   # near-white plaster mask
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - mask_face) + mask_col[ch] * mask_face

    # Eye hollows: deep indigo-black ovals on the mask
    for eye_x_off, eye_y_off in [(-0.018, -0.018), (0.018, -0.018)]:
        eye_cx = mask_cx + eye_x_off
        eye_cy = mask_cy + eye_y_off
        eye_dist = np.sqrt(
            ((xs - eye_cx) / 0.013) ** 2 + ((ys - eye_cy) / 0.016) ** 2
        )
        eye_mask = np.clip(1.0 - eye_dist ** 2.0, 0.0, 1.0)
        eye_col  = np.array([0.06, 0.05, 0.14])   # deep indigo-black
        for ch in range(3):
            ref[:, :, ch] = ref[:, :, ch] * (1 - eye_mask) + eye_col[ch] * eye_mask

    # Rouge spots: two crimson dots high on the mask cheeks
    for rouge_x_off, rouge_y_off in [(-0.024, 0.008), (0.024, 0.008)]:
        rx = mask_cx + rouge_x_off
        ry = mask_cy + rouge_y_off
        rdist = np.sqrt(
            ((xs - rx) / 0.012) ** 2 + ((ys - ry) / 0.008) ** 2
        )
        rouge_m = np.clip(1.0 - rdist ** 2.0, 0.0, 1.0)
        rouge_c = np.array([0.80, 0.18, 0.22])   # crimson rouge
        for ch in range(3):
            ref[:, :, ch] = ref[:, :, ch] * (1 - rouge_m * 0.65) + rouge_c[ch] * rouge_m * 0.65

    # ── Stone corner at right edge ────────────────────────────────────────────
    corner_mask = np.clip((xs - 0.88) / 0.10, 0.0, 1.0) * np.clip(1.0 - (ys - 0.60) / 0.38, 0.0, 1.0)
    corner_col  = np.array([0.70, 0.62, 0.44])   # pale ochre Belgian stone
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - corner_mask * 0.55) + corner_col[ch] * corner_mask * 0.55

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'The Procession of Hollow Faces' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=201)

    # ── Ground: warm ochre imprimatura — Ensor's souvenir-shop warmth ─────────
    p.tone_ground((0.72, 0.62, 0.32), texture_strength=0.025)

    # ── Underpainting: lay in crowd masses and central figure ─────────────────
    p.underpainting(ref_pil, stroke_size=55)

    # ── Block in: broad gestural passages — carnival colour masses ───────────
    p.block_in(ref_pil, stroke_size=22)

    # ── Build form: figure volumes, mask face, hat ────────────────────────────
    p.build_form(ref_pil, stroke_size=9)

    # ── Lights: mask white, banner highlights, impasto accent marks ───────────
    p.place_lights(ref_pil, stroke_size=4)

    # ── Ensor Carnival Mask — THE signature effect ────────────────────────────
    # Primary pass: full bidirectional chroma polarization at high intensity
    p.ensor_carnival_mask_pass(
        warm_boost=0.44,
        cool_boost=0.40,
        complement_ghost=0.20,
        sparkle_strength=0.26,
        ground_reveal=0.30,
        ground_color=(0.72, 0.62, 0.32),
        opacity=0.74,
    )

    # Second pass: push the dissonance further without blowing out the mask
    p.ensor_carnival_mask_pass(
        warm_boost=0.28,
        cool_boost=0.25,
        complement_ghost=0.12,
        sparkle_strength=0.15,
        ground_reveal=0.18,
        ground_color=(0.72, 0.62, 0.32),
        opacity=0.38,
    )

    # ── Meso detail: refine mask face, banner edges, cobblestone joints ───────
    p.meso_detail_pass(strength=0.18, opacity=0.14)

    # ── Micro detail: impasto surface texture marks ───────────────────────────
    p.micro_detail_pass(strength=0.10, opacity=0.10)

    # ── No unifying glaze — Ensor never used one; abrupt colour clash is intent
    # Mild edge definition to sharpen mask outline against the crowd
    p.edge_definition_pass(sharpness=0.22, opacity=0.18)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
