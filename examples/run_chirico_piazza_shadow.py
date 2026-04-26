"""
run_chirico_piazza_shadow.py — Session 198

"The Abandoned Piazza at Dusk" — after Giorgio de Chirico

Image Description
─────────────────
Subject & Composition
    An empty Italian Renaissance piazza at late afternoon, viewed from a
    low three-quarter perspective that exaggerates the depth recession.
    A classical arcade of arches stretches along the left side in sharp
    perspective, its columns casting long shadow fingers across the pale
    ochre stone floor toward the lower right.  A solitary standing
    figure — a featureless mannequin in a cone-shaped form, like
    de Chirico's Disquieting Muses — occupies the right centre of the
    frame, motionless, facing away into the deepest shadow.
    A red rubber ball rests on the piazza floor in the lower foreground,
    unexplained and incongruous.  At the far vanishing point, the
    silhouette of a steam locomotive — tiny, precise — crosses the
    horizon from left to right, trailing a white plume of smoke that
    curves upward and dissolves into the deep blue sky.

The Figure
    The mannequin is approximately two-thirds of the canvas height —
    disproportionately tall relative to the architecture, as though
    from another scale of reality.  Smooth terracotta-coloured surface,
    faceless ovoid head, conical torso.  No visible emotion because no
    face: the emotional content is entirely in posture — rigid
    uprightness, turned slightly from the viewer, attentive to something
    beyond the frame.  Its shadow is the longest of all: a cold
    blue-grey needle reaching from its base across the entire lower
    canvas toward the viewer.

The Environment
    The piazza stone is warm pale cream with subtle geometry suggesting
    rectangular paving blocks in perspective recession.  The arcade on
    the left throws seven alternating light-and-shadow bands across the
    floor — warm ochre lit zones between cold Prussian-grey shadow
    bands.  The sky fills the upper third: deep Prussian blue-green
    overhead, transitioning to a compressed band of orange-gold at the
    horizon line.  The horizontal shadow-edge between sky and
    architecture is hard, as though cut with a knife.  The far right
    opens onto open piazza space, no boundary visible — the world simply
    ends at the canvas edge.  The foreground shadow area is cool and
    dense, almost purple-grey; the midground lit zones glow warm
    terracotta; the far horizon is a single sharp line of light.

Technique & Palette
    De Chirico Metaphysical Shadow pass (chirico_metaphysical_shadow_pass,
    109th distinct mode).  Shadow rays project from every architectural
    edge at a low afternoon angle — the arcade columns, the mannequin's
    silhouette, the locomotive smoke column.  Cool Prussian blue-grey
    fills the shadow zones; warm ochre and terracotta dominate the lit
    surfaces.  The two-temperature contrast — warm sunlit stone against
    cool impossible shadow — creates the characteristic de Chirico
    feeling of disquiet.
    Palette: terracotta orange, ochre gold, raw sienna, Prussian blue-grey,
    pale cream, near-black umber, warm grey.

Mood & Intent
    Time has stopped.  The piazza has always been empty; the locomotive
    has always been crossing that horizon; the mannequin has always been
    standing there.  The rubber ball has never been thrown.  De Chirico
    described his work as painting the shadow of a dream just before
    waking — this image holds that precise interval.  The viewer
    carries away the specific anxiety of an empty afternoon: not terror
    but presentiment, the certainty that something is about to happen
    that will not.  The impossibly long shadows argue that the sun
    setting here is not the sun from any ordinary day.

Session 198 pass used:
    chirico_metaphysical_shadow_pass  (109th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "chirico_piazza_shadow.png"
)
W, H = 800, 1000   # tall portrait — emphasises the verticality of shadow-fall


def build_reference() -> np.ndarray:
    """
    Synthetic tonal reference encoding the metaphysical piazza scene.

    Tonal zones:
      - Sky (upper third): deep Prussian blue-green, compressed orange horizon band
      - Arcade arcade wall (left strip): warm terracotta vertical mass
      - Arcade shadow bands: alternating ochre-lit / blue-grey shadow stripes on floor
      - Piazza floor (centre + right): warm cream stone, perspective recession lines
      - Mannequin figure: terracotta cone, centre-right, two-thirds canvas height
      - Mannequin shadow: long blue-grey needle pointing lower-right
      - Red rubber ball: small vivid red circle, lower-left foreground
      - Locomotive: tiny dark silhouette + white smoke at far horizon
    """
    rng = np.random.default_rng(198)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Sky: Prussian blue-green gradient with orange horizon band ────────────
    sky_top   = np.array([0.06, 0.16, 0.38])   # deep Prussian blue
    sky_mid   = np.array([0.10, 0.22, 0.45])   # slightly lighter mid-sky
    sky_hor   = np.array([0.88, 0.56, 0.12])   # compressed orange-gold at horizon

    sky_bound = 0.32    # sky occupies top 32% of canvas
    sky_frac  = np.clip(ys / sky_bound, 0.0, 1.0)
    t_hor = np.clip((sky_frac - 0.70) * 3.5, 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = (
            sky_top[ch] * (1 - sky_frac) + sky_mid[ch] * sky_frac
        ) * (1 - t_hor) + sky_hor[ch] * t_hor

    # ── Piazza floor: warm cream stone (below sky) ────────────────────────────
    floor_frac = np.clip((ys - sky_bound) / (1.0 - sky_bound), 0.0, 1.0)
    floor_r = 0.88 + 0.06 * (1.0 - floor_frac)   # warmer near horizon
    floor_g = 0.82 + 0.06 * (1.0 - floor_frac)
    floor_b = 0.60 + 0.08 * (1.0 - floor_frac)
    ref[:, :, 0] = np.where(ys > sky_bound, floor_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(ys > sky_bound, floor_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(ys > sky_bound, floor_b, ref[:, :, 2])

    # Subtle perspective paving lines: horizontal bands darker at regular intervals
    n_pave = 14
    for pi in range(n_pave):
        # Paving lines converge toward horizon — space them more tightly near top
        t_pi = (pi / float(n_pave)) ** 1.5
        line_y = sky_bound + t_pi * (1.0 - sky_bound - 0.05)
        pave_dist = np.abs(ys - line_y) / 0.006
        pave_mask = np.clip(1.0 - pave_dist, 0.0, 1.0) ** 1.5 * 0.18
        ref[:, :, 0] -= pave_mask * 0.10
        ref[:, :, 1] -= pave_mask * 0.08
        ref[:, :, 2] -= pave_mask * 0.05

    # ── Arcade wall: warm terracotta vertical strip on left ────────────────────
    arcade_right = 0.22   # arcade occupies left 22% of canvas width
    arcade_r = 0.78; arcade_g = 0.44; arcade_b = 0.16
    arcade_frac = np.clip(1.0 - xs / arcade_right, 0.0, 1.0) ** 0.5
    ref[:, :, 0] = ref[:, :, 0] * (1 - arcade_frac) + arcade_r * arcade_frac
    ref[:, :, 1] = ref[:, :, 1] * (1 - arcade_frac) + arcade_g * arcade_frac
    ref[:, :, 2] = ref[:, :, 2] * (1 - arcade_frac) + arcade_b * arcade_frac

    # Arcade arches: dark recessed zones (deep umber) at regular intervals
    n_arches = 5
    for ai in range(n_arches):
        # Arches narrow in perspective toward the top
        arc_t = ai / float(n_arches)
        # Arch bottom position (on floor level, in perspective)
        arc_y_bot = sky_bound + (1.0 - sky_bound) * (0.10 + 0.80 * (1.0 - arc_t ** 0.6))
        arc_height = 0.10 + 0.20 * (1.0 - arc_t)
        arc_y_top = arc_y_bot - arc_height
        arc_x_cen = arcade_right * 0.55
        arc_x_hw = (0.06 + 0.02 * (1.0 - arc_t)) * (1.0 - arc_t * 0.4)
        arc_dist_x = np.abs(xs - arc_x_cen) / max(arc_x_hw, 0.01)
        arc_y_frac = np.clip((ys - arc_y_top) / max(arc_height, 0.01), 0.0, 1.0)
        # Arch silhouette: ellipse bottom, rectangle top
        arch_shape = np.clip(1.0 - arc_dist_x, 0.0, 1.0) ** 0.5 * arc_y_frac
        arch_zone = np.where((ys >= arc_y_top) & (ys <= arc_y_bot), arch_shape, 0.0)
        ref[:, :, 0] -= arch_zone * 0.55
        ref[:, :, 1] -= arch_zone * 0.50
        ref[:, :, 2] -= arch_zone * 0.42

    # ── Arcade shadow bands on floor (alternating lit/shadow stripes) ──────────
    # Seven bands of alternating warm-lit / cool-shadow from arcade to right
    for sb in range(7):
        # Shadow band position: starts at left (below arcade) and extends diagonally
        shadow_frac = sb / 7.0
        band_x_start = arcade_right + shadow_frac * 0.55
        band_x_end   = band_x_start + 0.045
        # Shadow bands slant slightly (perspective): right edge tilts up
        band_slant = 0.08 * (1.0 - shadow_frac)
        band_ys_adjusted = ys - (xs - band_x_start) * band_slant
        band_x_mask = np.clip(
            1.0 - np.abs(xs - (band_x_start + 0.022)) / 0.022, 0.0, 1.0
        )
        floor_only = np.where(ys > sky_bound + 0.02, 1.0, 0.0)
        if sb % 2 == 1:  # shadow band: cool Prussian grey
            band_strength = 0.55 * (1.0 - shadow_frac * 0.5)
            ref[:, :, 0] -= band_x_mask * floor_only * band_strength * 0.35
            ref[:, :, 1] -= band_x_mask * floor_only * band_strength * 0.28
            ref[:, :, 2] += band_x_mask * floor_only * band_strength * 0.08
        else:   # lit band: push toward warm ochre
            band_strength = 0.30 * (1.0 - shadow_frac * 0.3)
            ref[:, :, 0] += band_x_mask * floor_only * band_strength * 0.12
            ref[:, :, 1] += band_x_mask * floor_only * band_strength * 0.06

    # ── Mannequin figure: terracotta cone, centre-right ───────────────────────
    man_cx  = 0.64
    man_cy  = 0.72   # centre of figure
    man_hw  = 0.06
    man_hh  = 0.28
    man_dist = np.sqrt(((xs - man_cx) / man_hw) ** 2 + ((ys - man_cy) / man_hh) ** 2)
    man_mask = np.clip(1.0 - man_dist ** 0.70, 0.0, 1.0)
    # Terracotta body
    ref[:, :, 0] = ref[:, :, 0] * (1 - man_mask) + 0.76 * man_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - man_mask) + 0.42 * man_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - man_mask) + 0.18 * man_mask

    # Mannequin head: small ovoid
    head_cy = man_cy - man_hh * 0.80
    head_r  = 0.038
    head_dist = np.sqrt(((xs - man_cx) / head_r) ** 2 + ((ys - head_cy) / head_r) ** 2)
    head_mask = np.clip(1.0 - head_dist, 0.0, 1.0) ** 0.9
    ref[:, :, 0] = ref[:, :, 0] * (1 - head_mask) + 0.72 * head_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - head_mask) + 0.38 * head_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - head_mask) + 0.14 * head_mask

    # Mannequin shadow: long blue-grey needle extending lower-right
    shadow_angle_deg = 225.0   # shadow direction (lower-right in image coords)
    import math
    shadow_dx = math.cos(shadow_angle_deg * math.pi / 180.0)
    shadow_dy = -math.sin(shadow_angle_deg * math.pi / 180.0)
    shadow_length = 0.42  # fraction of min(W,H)
    n_shadow_steps = 80
    man_foot_y = man_cy + man_hh
    for si in range(1, n_shadow_steps + 1):
        t_s = si / n_shadow_steps
        sx = man_cx + shadow_dx * shadow_length * t_s
        sy = man_foot_y + abs(shadow_dy) * shadow_length * t_s
        atten = 1.0 - t_s * 0.85
        sw = 0.032 * atten + 0.008
        sdist = np.sqrt(((xs - sx) / max(sw, 0.004)) ** 2 + ((ys - sy) / max(sw * 0.4, 0.003)) ** 2)
        smask = np.clip(1.0 - sdist, 0.0, 1.0) ** 1.2 * 0.65 * atten
        floor_mask = np.where(ys > sky_bound + 0.02, 1.0, 0.0)
        smask = smask * floor_mask
        ref[:, :, 0] -= smask * 0.42
        ref[:, :, 1] -= smask * 0.38
        ref[:, :, 2] += smask * 0.08

    # ── Red rubber ball: vivid red circle, lower-left foreground ─────────────
    ball_cx = 0.28
    ball_cy = 0.90
    ball_r  = 0.025
    ball_dist = np.sqrt(((xs - ball_cx) / ball_r) ** 2 + ((ys - ball_cy) / ball_r) ** 2)
    ball_mask = np.clip(1.0 - ball_dist, 0.0, 1.0) ** 0.8
    # Vivid cadmium red
    ref[:, :, 0] = ref[:, :, 0] * (1 - ball_mask) + 0.88 * ball_mask
    ref[:, :, 1] = ref[:, :, 1] * (1 - ball_mask) + 0.12 * ball_mask
    ref[:, :, 2] = ref[:, :, 2] * (1 - ball_mask) + 0.08 * ball_mask
    # Ball shadow on ground
    bshadow_dist = np.sqrt(((xs - ball_cx - 0.025) / 0.022) ** 2 + ((ys - ball_cy - 0.010) / 0.008) ** 2)
    bshadow_mask = np.clip(1.0 - bshadow_dist, 0.0, 1.0) ** 1.5 * 0.45
    ref[:, :, 0] -= bshadow_mask * 0.30
    ref[:, :, 1] -= bshadow_mask * 0.26
    ref[:, :, 2] += bshadow_mask * 0.04

    # ── Locomotive silhouette at horizon ──────────────────────────────────────
    loco_cx  = 0.70
    loco_y   = sky_bound + 0.01
    loco_hw  = 0.048
    loco_hh  = 0.018
    loco_dist = np.sqrt(((xs - loco_cx) / loco_hw) ** 2 + ((ys - loco_y) / loco_hh) ** 2)
    loco_mask = np.clip(1.0 - loco_dist ** 0.80, 0.0, 1.0)
    ref[:, :, 0] -= loco_mask * 0.55
    ref[:, :, 1] -= loco_mask * 0.52
    ref[:, :, 2] -= loco_mask * 0.38

    # Smoke plume
    smoke_cx = loco_cx - 0.010
    for sp in range(20):
        sp_t = sp / 20.0
        sp_x = smoke_cx - sp_t * 0.08
        sp_y = loco_y - sp_t * 0.10
        sp_r = 0.014 + sp_t * 0.018
        sp_dist = np.sqrt(((xs - sp_x) / sp_r) ** 2 + ((ys - sp_y) / sp_r) ** 2)
        sp_mask = np.clip(1.0 - sp_dist, 0.0, 1.0) ** 1.5 * 0.55 * (1.0 - sp_t * 0.6)
        sky_only = np.where(ys <= sky_bound + 0.02, 1.0, 0.0)
        sp_mask = sp_mask * sky_only
        ref[:, :, 0] = ref[:, :, 0] * (1 - sp_mask) + 0.85 * sp_mask
        ref[:, :, 1] = ref[:, :, 1] * (1 - sp_mask) + 0.85 * sp_mask
        ref[:, :, 2] = ref[:, :, 2] * (1 - sp_mask) + 0.82 * sp_mask

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'The Abandoned Piazza at Dusk' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=198)

    # ── Ground: warm ochre — sun-baked piazza linen ───────────────────────────
    p.tone_ground((0.88, 0.84, 0.68), texture_strength=0.025)

    # ── Underpainting: lay in the deep architectural masses ───────────────────
    p.underpainting(ref_pil, stroke_size=52)

    # ── Block in: broad colour zones ─────────────────────────────────────────
    p.block_in(ref_pil, stroke_size=28)

    # ── Build form: structural directional strokes ────────────────────────────
    p.build_form(ref_pil, stroke_size=12)

    # ── Lights: clarify the lit stone surfaces ────────────────────────────────
    p.place_lights(ref_pil, stroke_size=8)

    # ── De Chirico Metaphysical Shadow — THE signature effect ─────────────────
    # Primary pass: strong architectural shadow projection
    p.chirico_metaphysical_shadow_pass(
        shadow_angle=225.0,
        shadow_length=0.38,
        shadow_opacity=0.75,
        warm_strength=0.48,
        warm_opacity=0.40,
        edge_threshold=0.15,
        opacity=0.82,
        seed=198,
    )

    # Second shadow pass: deeper shadows from darker edge threshold
    p.chirico_metaphysical_shadow_pass(
        shadow_angle=220.0,
        shadow_length=0.22,
        shadow_opacity=0.55,
        warm_strength=0.30,
        warm_opacity=0.22,
        edge_threshold=0.28,
        opacity=0.42,
        seed=1980,
    )

    # ── Meso detail: sharpen the architecture's edges ─────────────────────────
    p.meso_detail_pass(strength=0.30, opacity=0.28)

    # ── Glazing: unifying warm amber haze over the whole image ───────────────
    p.glaze((0.78, 0.62, 0.28), opacity=0.10)

    # ── Vignette: draw focus into the piazza and the mannequin ───────────────
    p.focal_vignette_pass(vignette_strength=0.30, opacity=0.45)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
