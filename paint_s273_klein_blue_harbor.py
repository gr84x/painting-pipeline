"""
paint_s273_klein_blue_harbor.py -- Session 273

"The Harbor at Nice at Dusk -- Into the Blue Void"
in the manner of Yves Klein (Nouveau Réalisme / Monochromism)

Image Description
-----------------
Subject & Composition
    A harbor view from a balcony in Nice, France, at the precise moment of late
    dusk when the Mediterranean sea and the cobalt sky above dissolve into
    International Klein Blue -- the same blue Klein grew up beneath and later
    registered as his own. Canvas format: landscape (1440 x 1040). The composition
    is organized in four horizontal bands: the sky occupying the upper 52%, a thin
    horizon band at 52-56%, the sea occupying 56-88%, and a dark balcony ledge
    at the extreme bottom 12%. The balcony occupies the full width; a single iron
    railing runs horizontally near the bottom of frame. One slender sailboat mast
    rises vertically in the center-right zone (roughly x=60%), barely perceptible
    against the blue -- a dark silhouette extending from the sea into the sky.
    On the far left (leftmost 15%), the dark ochre-terracotta silhouette of the
    old harbor wall curves gently inward, grounding the composition in the specific
    geography of Nice without insisting on it.

The Subject
    The primary subject is the BLUE ITSELF -- the International Klein Blue that
    dominates the entire canvas and is simultaneously sky, sea, and the void
    between them. The distinguishing feature is that sky and sea are the SAME
    color, separated only by a thin, barely luminous horizon line where the last
    of the sun's warmth lingers as a pale cerulean band no more than 20 pixels
    wide. The sea surface is not calm -- there is a very slight chop, visible as
    the faintest dark-blue texture in the lower portion -- but from this distance
    the texture reads as surface variation within the blue field rather than as
    waves. The harbor wall on the far left is dark terracotta-umber, deeply
    weathered, receding into the blue distance at roughly 30 degrees. The
    sailboat mast is a single pencil-thin vertical mark of near-black, rising
    from the sea surface to a point just above the horizon. The iron balcony
    railing at the bottom runs the full width as a near-horizontal dark grey mark.

The Environment
    SKY (upper 52%): Not a gradient of conventional colors but a deep, uniform
    IKB field that grades from slightly deeper navy at the zenith (cooler, more
    saturated) to slightly lighter electric ultramarine at the horizon (more
    luminous as the last light disperses). The gradient is subtle -- the entire
    sky reads as one continuous blue field with no visible sunset coloring. The
    quality is the quality of Klein's monochromes: color freed from incident,
    from event, from subject. The sky simply IS blue.

    HORIZON (52-56%): A narrow band of slightly lighter, more luminous blue --
    not warm gold or orange, but a pale cornflower-cerulean that represents the
    last refraction of visible light at dusk. This thin seam is the only evidence
    that there was ever a sun. It is barely distinguishable from the sky and sea
    on either side; its primary function is spatial orientation, not drama.

    SEA (56-88%): Deep International Klein Blue, slightly textured. The water
    is slightly darker than the sky -- the sea absorbs rather than transmits
    light -- but the color family is identical. The surface has very faint
    horizontal micro-texture (slight chop) that resolves as a directional
    variation within the blue field. In the center, a subtle oval of slightly
    lighter reflection beneath where the horizon would mirror into the flat water.

    HARBOR WALL (far left, 0-15%): Dark warm silhouette -- terracotta-umber,
    ochre-tinged at the top where the stone catches the last ambient light.
    The form curves gently; its top edge is irregular (stone parapet).
    The wall recedes both horizontally (its face shrinks as it retreats)
    and in depth (it gets darker and cooler as it recedes into the blue).

    BALCONY (lower 12%): Flat dark grey-ochre surface of the balcony floor and
    the top of the parapet wall. A single iron railing: a thin dark horizontal
    line with very slight perspective convergence. Not detailed; its function is
    to anchor the viewer's position and establish the viewpoint as FROM a balcony
    rather than from water level.

Technique & Palette
    Yves Klein Monochromism / IKB field mode -- session 273, 184th distinct mode.

    Pipeline:
    1. Procedural reference: deep IKB blue gradient (sky and sea), horizon seam,
       harbor wall left, balcony bottom, sailboat mast.
    2. tone_ground: deep cobalt-navy (0.02, 0.10, 0.52) -- IKB ground color.
    3. underpainting x2: establish tonal architecture -- blue field, dark wall,
       horizon luminosity.
    4. block_in x2: build sky and sea blue masses, harbor wall form.
    5. build_form x2: develop sea surface texture, horizon refinement.
    6. place_lights: horizon glow, water reflection, railing highlight.
    7. paint_transparent_glaze_pass (s273 improvement): apply IKB-tinted
       transparent glaze over the lighter sky and horizon passages -- enriches
       and deepens the blue field through multiplicative thin-film color physics.
    8. klein_ib_field_pass (s273, 184th mode): IKB chromatic resonance tinting
       + matte pigment micro-texture + warm suppression.
    9. paint_aerial_perspective_pass: cool atmospheric recession in deep distance.
    10. paint_chromatic_underdark_pass: deep blue-navy in deepest shadow zones.

    Full palette:
    IKB ultramarine (0.00/0.18/0.65) -- deep cobalt-navy (0.04/0.10/0.42) --
    electric violet-blue (0.22/0.34/0.78) -- deep navy-black (0.06/0.06/0.28) --
    pale cerulean horizon (0.38/0.55/0.82) -- dark terracotta-umber (0.25/0.15/0.08)
    -- near-black iron (0.10/0.10/0.14) -- warm stone-ochre (0.42/0.30/0.16)

Mood & Intent
    The painting intends THE VOID OF PURE COLOR. Yves Klein spent the last six
    years of his life pursuing one idea: that a sufficiently pure, sufficiently
    saturated color, applied with sufficient conviction to a sufficiently large
    surface, stops being a representation of anything and becomes a PRESENCE --
    a direct encounter between the viewer's perceptual field and the color itself,
    unmediated by subject, composition, or narrative. Klein said the sky is his
    first work of art. This painting is the literal image that preceded that idea:
    standing on a balcony in Nice at dusk, looking out at the sea and sky as they
    dissolve into each other, recognizing in that dissolution the possibility of a
    painting that is nothing but blue. The viewer should feel not calm but something
    more acute: the slight vertigo of color that has no edge, no subject, no story --
    only the endless, unflinching fact of its own blueness.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stroke_engine import Painter

W, H = 1440, 1040
SEED = 273
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s273_klein_blue_harbor.png")


def build_reference() -> np.ndarray:
    """Build a procedural reference for the Nice harbor blue void.

    Returns uint8 (H, W, 3) in range 0-255.
    """
    rng = np.random.default_rng(SEED)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    horizon_y     = int(H * 0.52)   # sky/sea boundary
    horizon_low_y = int(H * 0.56)   # end of horizon seam
    balcony_y     = int(H * 0.88)   # start of balcony/railing zone

    # ── Sky (upper 52%) ────────────────────────────────────────────────────────
    ikb_r, ikb_g, ikb_b = 0.00, 0.18, 0.65
    for y in range(horizon_y):
        t = y / float(horizon_y - 1)   # 0 = zenith, 1 = horizon
        # Zenith: deeper, darker navy; horizon: slightly lighter electric cobalt
        deepen = 1.0 - t * 0.22        # gets slightly lighter toward horizon
        r = ikb_r * deepen
        g = (ikb_g + t * 0.06) * deepen
        b = (ikb_b + t * 0.10) * deepen
        noise = rng.uniform(-0.006, 0.006, W).astype(np.float32)
        ref[y, :, 0] = np.clip(r + noise * 0.3, 0, 1)
        ref[y, :, 1] = np.clip(g + noise * 0.4, 0, 1)
        ref[y, :, 2] = np.clip(b + noise * 0.5, 0, 1)

    # ── Horizon seam (52-56%): pale cerulean ──────────────────────────────────
    for y in range(horizon_y, horizon_low_y):
        t = (y - horizon_y) / float(horizon_low_y - horizon_y + 1)
        # Peak luminosity at center of seam
        seam_peak = 1.0 - abs(t - 0.5) * 2.0
        r = 0.30 + seam_peak * 0.10
        g = 0.48 + seam_peak * 0.10
        b = 0.80 + seam_peak * 0.04
        noise = rng.uniform(-0.005, 0.005, W).astype(np.float32)
        ref[y, :, 0] = np.clip(r + noise * 0.3, 0, 1)
        ref[y, :, 1] = np.clip(g + noise * 0.4, 0, 1)
        ref[y, :, 2] = np.clip(b + noise * 0.5, 0, 1)

    # ── Sea (56-88%) ───────────────────────────────────────────────────────────
    for y in range(horizon_low_y, balcony_y):
        t = (y - horizon_low_y) / float(balcony_y - horizon_low_y - 1)
        # Sea slightly darker than sky; gets darker toward foreground
        r = 0.00
        g = (0.14 - t * 0.04)
        b = (0.56 - t * 0.10)
        # Very subtle horizontal chop texture
        chop_scale = 0.008 * (0.4 + 0.6 * t)
        noise = rng.uniform(-chop_scale, chop_scale, W).astype(np.float32)
        ref[y, :, 0] = np.clip(r + noise * 0.2, 0, 1)
        ref[y, :, 1] = np.clip(g + noise * 0.5, 0, 1)
        ref[y, :, 2] = np.clip(b + noise, 0, 1)

    # ── Subtle reflection oval under horizon center ───────────────────────────
    ref_cx = int(W * 0.52)
    ref_ry = int(H * 0.74)
    for dy in range(-40, 40):
        yyy = ref_ry + dy
        if yyy < horizon_low_y or yyy >= balcony_y:
            continue
        for dx in range(-120, 120):
            xxx = ref_cx + dx
            if xxx < 0 or xxx >= W:
                continue
            d = (dx / 120.0) ** 2 + (dy / 40.0) ** 2
            if d <= 1.0:
                lift = 0.04 * (1.0 - d)
                ref[yyy, xxx, 1] = np.clip(ref[yyy, xxx, 1] + lift, 0, 1)
                ref[yyy, xxx, 2] = np.clip(ref[yyy, xxx, 2] + lift * 1.5, 0, 1)

    # ── Harbor wall (left 15%) ─────────────────────────────────────────────────
    wall_right = int(W * 0.15)
    wall_top_y = int(H * 0.38)    # top of wall (above horizon, into sky)
    wall_base_y = balcony_y

    for x in range(0, wall_right):
        t_x = x / float(wall_right + 1)   # 0 = left edge, 1 = right edge
        # Wall gets thinner and recedes (lower top edge) toward right
        top_y = int(wall_top_y + (horizon_y - wall_top_y) * t_x ** 0.6)
        for y in range(top_y, wall_base_y):
            t_y = (y - top_y) / float(wall_base_y - top_y + 1)
            # Terracotta-umber, darker toward base and right edge
            darkness = 0.4 + 0.3 * t_y + 0.2 * t_x
            r = np.clip(0.32 * (1.0 - darkness * 0.6), 0, 1)
            g = np.clip(0.18 * (1.0 - darkness * 0.5), 0, 1)
            b = np.clip(0.08 * (1.0 - darkness * 0.4), 0, 1)
            # Add ochre top highlight on wall parapet
            if y == top_y or y == top_y + 1:
                r = np.clip(r * 1.6, 0, 1)
                g = np.clip(g * 1.3, 0, 1)
            n = rng.uniform(-0.015, 0.015)
            ref[y, x, 0] = np.clip(r + n, 0, 1)
            ref[y, x, 1] = np.clip(g + n * 0.7, 0, 1)
            ref[y, x, 2] = np.clip(b + n * 0.5, 0, 1)

    # ── Sailboat mast (center-right, vertical) ────────────────────────────────
    mast_x = int(W * 0.62)
    mast_top_y = int(H * 0.32)     # mast top: well into sky
    mast_base_y = int(H * 0.64)    # mast base: below horizon, in sea

    for y in range(mast_top_y, mast_base_y):
        for dx in [-1, 0]:
            xx = mast_x + dx
            if 0 <= xx < W:
                ref[y, xx, 0] = 0.06
                ref[y, xx, 1] = 0.06
                ref[y, xx, 2] = 0.14

    # ── Balcony and railing (lower 12%) ────────────────────────────────────────
    for y in range(balcony_y, H):
        t = (y - balcony_y) / float(H - balcony_y + 1)
        # Dark warm grey-ochre, getting darker toward bottom
        r = np.clip(0.18 - t * 0.08, 0, 1)
        g = np.clip(0.14 - t * 0.06, 0, 1)
        b = np.clip(0.12 - t * 0.05, 0, 1)
        noise = rng.uniform(-0.01, 0.01, W).astype(np.float32)
        ref[y, :, 0] = np.clip(r + noise, 0, 1)
        ref[y, :, 1] = np.clip(g + noise * 0.8, 0, 1)
        ref[y, :, 2] = np.clip(b + noise * 0.6, 0, 1)

    # Iron railing: thin near-black horizontal line at top of balcony
    railing_y = balcony_y + 4
    for x in range(0, W):
        # Slight perspective taper
        ref[railing_y,   x, :] = [0.10, 0.10, 0.14]
        ref[railing_y+1, x, :] = [0.08, 0.08, 0.12]
        # Thin top highlight on rail
        ref[railing_y-1, x, :] = [0.24, 0.28, 0.40]

    # Convert to uint8
    return (np.clip(ref, 0, 1) * 255).astype(np.uint8)


def main():
    print(f"Session 273 -- Yves Klein IKB Monochrome -- Harbor at Nice")
    print(f"Canvas: {W} x {H}")
    print()

    print("Building procedural reference...")
    ref = build_reference()
    print(f"  Reference: {ref.shape}, dtype={ref.dtype}, range=[{ref.min()},{ref.max()}]")

    print("Initialising Painter...")
    p = Painter(W, H, seed=SEED)

    print("Laying ground...")
    p.tone_ground((0.02, 0.10, 0.52), texture_strength=0.018)

    print("Underpainting (x2)...")
    p.underpainting(ref, stroke_size=54, n_strokes=220)
    p.underpainting(ref, stroke_size=38, n_strokes=250)

    print("Block-in (x2)...")
    p.block_in(ref, stroke_size=30, n_strokes=460)
    p.block_in(ref, stroke_size=18, n_strokes=500)

    print("Build form (x2)...")
    p.build_form(ref, stroke_size=12, n_strokes=500)
    p.build_form(ref, stroke_size=6,  n_strokes=400)

    print("Place lights...")
    p.place_lights(ref, stroke_size=4, n_strokes=280)

    print("Transparent glaze pass (s273 improvement) -- IKB blue glaze over sky/sea...")
    p.paint_transparent_glaze_pass(
        glaze_r=0.00,
        glaze_g=0.12,
        glaze_b=0.72,
        light_threshold=0.25,
        glaze_strength=0.32,
        coverage_sigma=3.5,
        coverage_density=0.74,
        coverage_seed=SEED,
        opacity=0.68,
    )

    print("Klein IKB field pass (184th mode)...")
    p.klein_ib_field_pass(
        ikb_r=0.00,
        ikb_g=0.18,
        ikb_b=0.65,
        resonance_weight=0.72,
        tint_strength=0.44,
        micro_texture=0.016,
        texture_seed=SEED,
        depth_amplitude=0.040,
        depth_scale=0.008,
        warm_suppress=0.32,
        opacity=0.74,
    )

    print("Aerial perspective pass...")
    p.paint_aerial_perspective_pass()

    print("Chromatic underdark pass...")
    p.paint_chromatic_underdark_pass()

    print(f"Saving to {OUT}...")
    p.save(OUT)
    print("Done.")


if __name__ == "__main__":
    main()
