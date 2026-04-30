"""
paint_s258_morandi_vessels.py -- Session 258

"Five Vessels, Morning Light" -- after Giorgio Morandi

Image Description
-----------------
Subject & Composition
    Five ceramic vessels arranged on a narrow shelf or table ledge at strict
    eye level -- the viewer is seated, eye plane exactly at the shelf surface.
    Arranged from left to right: a tall, narrow bottle with a rounded shoulder
    and cylindrical neck; a medium-height vase with a widening body and small
    mouth; a squat round jar with a flat lid; a second tall bottle, slightly
    taller than the first, positioned just behind the others so its shoulder
    breaks the horizon line of the shelf; and a shallow oval bowl resting
    at the far right, its interior plane nearly parallel to the viewer's eye.
    The grouping is asymmetric -- the two bottles flank the central jar, the
    vase breaks to the left of center, the bowl trails off to the right. The
    arrangement generates five distinct negative-space intervals between and
    around the vessels: each interval is as carefully weighted as the forms
    themselves. The composition is horizontal, classical, still.

The Figure
    The vessels are not described individually -- they are described as a
    collective. They are all ceramic, all slightly different shades of the
    same grey-ochre-dust family: the tall left bottle is a warm ash-grey
    with a slight blue undertone on its shaded flank; the vase is the warmest
    object, catching more of the side light and reading as dusty ochre on its
    lit face; the squat jar is the most neutral, a flat cool grey; the second
    bottle, set slightly back, is in slightly more shadow, its tone stepping
    down to a quiet blue-grey; the oval bowl is the palest object -- its
    interior a near-vellum, slightly yellowish white. Each form is rendered
    as a simplified ellipse of revolution. Highlights are not specular points
    but broad, soft zones of slightly warmer, slightly paler tone. Shadows
    are not dark -- they are merely less pale. The tallest vessel reaches
    about two-thirds of the canvas height. The shelf line falls at exactly
    the lower third of the canvas. The vessels sit on the shelf without
    shadow beneath them -- Morandi rarely painted cast shadows.

The Environment
    The background is a pale warm grey -- somewhere between plaster and ash --
    shifting barely perceptibly lighter toward the upper right where diffuse
    daylight enters from outside the frame. This is a studio interior:
    Via Fondazza, Bologna, morning. The shelf surface is a warm off-white,
    visible beneath the vessels as a narrow horizontal band. There is a very
    faint horizon line between the wall and the shelf -- not a hard edge but
    a tonal transition, slightly darker where wall meets shelf. There are no
    other objects, no tablecloth patterns, no window. The space is reduced to
    its essence: vessel, ground, wall, light. The edge between background
    and vessel is soft where the vessel tone is close to the background tone
    (the lighter flanks of the grey bottle disappear slightly into the wall);
    slightly harder where there is enough tonal contrast to resolve the silhouette.
    The overall edge quality throughout is gently resolved -- never harsh,
    never lost.

Technique & Palette
    Morandi Dusty Vessel mode -- session 258, 169th distinct mode.

    The morandi_dusty_vessel_pass is applied after the vessels are blocked in
    and modelled: the pass desaturates the chromatic foundation toward the
    dusty ash-grey palette Morandi used, compresses the tonal range so that
    no value in the painting reads as a true black or a true white
    (target_mid=0.54, compress_strength=0.38 -- Morandi's range ran roughly
    from about 0.35 to 0.82 on a standard luminance scale), and then applies
    the ochre ground reveal in the lightest areas, tinting the near-white
    vellum interior of the bowl and the lit face of the vase with a faint
    warm gold bleed, as if the warm linen primer is showing through the
    thin final glazes of pale paint. opacity=0.82 leaves the underlying
    tonal drawing largely intact while applying Morandi's characteristic
    atmospheric transformation.

    Granulation improvement (session 258): The granulation pass adds the
    fine material texture of Morandi's paint surface -- he worked his paintings
    over months, sanding between sessions, producing a surface with a slight
    granular quality. Warm pigment particles settle slightly into the low-
    frequency valleys (the subtle fissures between layers); cool light reflects
    slightly off the ridges (edges and lighter masses). granule_sigma=3.0 sets
    the scale of the granulation to match the medium-fine texture of a sanded
    oil surface; warm_shift=0.035, cool_shift=0.035 keep the chromatic effect
    extremely subtle -- this should read as texture, not as colour change.
    edge_sharpen=0.25 restores a gentle edge resolution across the vessel
    contours, giving the painting that Morandi quality of softness-with-
    definition: forms that are resolved without being mechanical.

    Stage-by-stage palette build:
    Ground: warm linen-grey (0.82, 0.79, 0.70)
    Block-in: grey vessel masses and pale wall
    Build form: tonal gradation on vessel bodies
    Place lights: pale highlights on lit flanks
    Morandi Dusty Vessel pass: saturation reduction, tonal compression, ochre glow
    Granulation pass: physical paint surface texture
    Tonal Key pass (s255): confirm overall key
    Edge Temperature pass (s256): warm/cool contrast at vessel edges
    Shadow Bleed pass (s257): faint warm bounce in shadow zones

    Palette: vessel-ash-warm (0.62/0.58/0.50) -- vessel-grey (0.54/0.54/0.52) --
    vessel-blue-grey (0.50/0.52/0.56) -- vessel-ochre (0.68/0.62/0.48) --
    vessel-pale (0.78/0.76/0.66) -- bowl-interior (0.86/0.84/0.74) --
    shelf-white (0.88/0.86/0.78) -- wall-grey (0.72/0.70/0.64) --
    wall-light (0.80/0.79/0.72) -- shadow-flank (0.42/0.42/0.44)

Mood & Intent
    The intent is the radical intimacy of Morandi's project: the discovery
    that a small group of ordinary vessels, painted in a small room over
    half a century, contains as much content as any history painting or
    landscape. What does it mean to look at the same five objects every
    morning for forty years? The vessels accumulate time. They are not
    symbols of anything -- they refuse allegory. They are simply what they
    are: containers, surfaces, light, form. The mood is pre-verbal quiet.
    Not melancholy (there is no absence here, nothing has been lost) -- just
    the particular silence of a room before the day has begun its demands.
    The ochre glow in the lightest passages is the only warmth: the morning
    light, as it always is, arriving slowly.
"""

import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "s258_morandi_vessels.png")

W, H = 800, 660
RNG = random.Random(258)


# ── Colour palette ─────────────────────────────────────────────────────────────

WALL_GREY        = (0.72, 0.70, 0.64)
WALL_LIGHT       = (0.80, 0.79, 0.72)
SHELF_WHITE      = (0.88, 0.86, 0.78)
VESSEL_ASH_WARM  = (0.62, 0.58, 0.50)
VESSEL_GREY      = (0.54, 0.54, 0.52)
VESSEL_BLUE_GREY = (0.50, 0.52, 0.56)
VESSEL_OCHRE     = (0.68, 0.62, 0.48)
VESSEL_PALE      = (0.78, 0.76, 0.66)
BOWL_INTERIOR    = (0.86, 0.84, 0.74)
SHADOW_FLANK     = (0.42, 0.42, 0.44)
VESSEL_MID       = (0.58, 0.57, 0.52)
VESSEL_RIM       = (0.74, 0.72, 0.64)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def draw_cylinder_vessel(
    arr: np.ndarray,
    cx: int,         # center x
    shelf_y: int,    # y of shelf surface
    body_w: int,     # half-width at widest point
    neck_w: int,     # half-width at neck
    neck_h: int,     # height of neck
    body_h: int,     # height of body (below neck junction)
    shoulder_h: int, # height of shoulder taper from body to neck
    col_lit: tuple,
    col_mid: tuple,
    col_shadow: tuple,
) -> None:
    """Draw a simplified bottle/vase form as a tonal cylinder with shoulder."""
    h_arr, w_arr = arr.shape[:2]
    total_h = body_h + shoulder_h + neck_h
    vessel_top = shelf_y - total_h

    for row in range(max(0, vessel_top), min(h_arr, shelf_y)):
        fy = row - vessel_top           # 0 at top, total_h at bottom
        fy_norm = fy / total_h

        if fy < neck_h:
            # Neck zone
            hw = neck_w
        elif fy < neck_h + shoulder_h:
            # Shoulder taper
            t = (fy - neck_h) / max(1, shoulder_h)
            hw = int(neck_w + (body_w - neck_w) * t)
        else:
            # Body zone
            hw = body_w

        left  = max(0, cx - hw)
        right = min(w_arr, cx + hw)

        for col in range(left, right):
            fx = (col - left) / max(1, right - left)
            # Light from upper-left: left third is lit, right third in shadow
            if fx < 0.22:
                t = (0.22 - fx) / 0.22
                colour = lerp(col_mid, col_lit, t * 0.75)
            elif fx > 0.72:
                t = (fx - 0.72) / 0.28
                colour = lerp(col_mid, col_shadow, t * 0.65)
            else:
                colour = col_mid
            arr[row, col, :] = colour


def draw_squat_jar(
    arr: np.ndarray,
    cx: int,
    shelf_y: int,
    body_w: int,
    body_h: int,
    lid_h: int,
    col_lit: tuple,
    col_mid: tuple,
    col_shadow: tuple,
) -> None:
    """Draw a squat rounded jar with a flat lid."""
    h_arr, w_arr = arr.shape[:2]
    top_y = shelf_y - body_h - lid_h

    # Lid
    for row in range(max(0, top_y), min(h_arr, top_y + lid_h)):
        half_lid = int(body_w * 0.60)
        for col in range(max(0, cx - half_lid), min(w_arr, cx + half_lid)):
            fx = (col - (cx - half_lid)) / max(1, 2 * half_lid)
            colour = lerp(col_lit, col_mid, fx * 0.5)
            arr[row, col, :] = colour

    # Body (slightly rounded top)
    for row in range(max(0, top_y + lid_h), min(h_arr, shelf_y)):
        fy = (row - (top_y + lid_h)) / max(1, body_h)
        # Slight narrowing at very bottom
        if fy > 0.85:
            hw = int(body_w * (1.0 - (fy - 0.85) / 0.15 * 0.10))
        else:
            hw = body_w
        for col in range(max(0, cx - hw), min(w_arr, cx + hw)):
            fx = (col - (cx - hw)) / max(1, 2 * hw)
            if fx < 0.20:
                colour = lerp(col_mid, col_lit, (0.20 - fx) / 0.20 * 0.70)
            elif fx > 0.75:
                colour = lerp(col_mid, col_shadow, (fx - 0.75) / 0.25 * 0.60)
            else:
                colour = col_mid
            arr[row, col, :] = colour


def draw_oval_bowl(
    arr: np.ndarray,
    cx: int,
    shelf_y: int,
    outer_w: int,
    height: int,
    col_rim: tuple,
    col_interior: tuple,
    col_shadow: tuple,
) -> None:
    """Draw a shallow oval bowl seen at eye-level (mostly rim + slight interior)."""
    h_arr, w_arr = arr.shape[:2]
    top_y = shelf_y - height

    for row in range(max(0, top_y), min(h_arr, shelf_y)):
        fy = (row - top_y) / max(1, height)
        hw = int(outer_w * math.sqrt(1.0 - (1.0 - fy) ** 2) if fy < 1.0 else outer_w)
        hw = max(1, hw)
        rim_w = max(2, int(outer_w * 0.10))

        for col in range(max(0, cx - hw), min(w_arr, cx + hw)):
            # Distance from left/right edge of this row
            d_left  = col - (cx - hw)
            d_right = (cx + hw) - col
            d_edge  = min(d_left, d_right)

            if d_edge <= rim_w:
                colour = col_rim
            elif fy < 0.25:
                # Top of bowl - rim visible
                colour = col_interior
            else:
                # Interior
                t = (fy - 0.25) / 0.75
                colour = lerp(col_interior, col_shadow, t * 0.15)
            arr[row, col, :] = colour


def build_reference(w: int, h: int) -> Image.Image:
    """Build the procedural reference for Five Vessels, Morning Light."""
    arr = np.zeros((h, w, 3), dtype=np.float32)

    shelf_y = int(h * 0.68)   # Shelf at lower third

    # ── Background wall ────────────────────────────────────────────────────────
    for row in range(h):
        for col in range(w):
            fy = row / h
            fx = col / w
            # Subtle light from upper right
            light_t = (1.0 - fy) * 0.12 + fx * 0.08
            wall_col = lerp(WALL_GREY, WALL_LIGHT, light_t)
            arr[row, col, :] = wall_col

    # ── Shelf surface (below shelf_y) ─────────────────────────────────────────
    for row in range(shelf_y, h):
        depth_t = (row - shelf_y) / max(1, h - shelf_y)
        for col in range(w):
            colour = lerp(SHELF_WHITE, lerp(SHELF_WHITE, WALL_GREY, 0.3), depth_t * 0.4)
            arr[row, col, :] = colour

    # ── Wall-shelf horizon (subtle): slightly darker transition ────────────────
    for row in range(max(0, shelf_y - 2), min(h, shelf_y + 3)):
        darkness = 1.0 - abs(row - shelf_y) / 3.0
        for col in range(w):
            cur = arr[row, col, :].copy()
            arr[row, col, :] = lerp(cur, lerp(cur, (0.35, 0.34, 0.30), 0.1), darkness * 0.25)

    # ── Vessel 1: Tall narrow bottle, left ────────────────────────────────────
    draw_cylinder_vessel(
        arr,
        cx=int(w * 0.22),
        shelf_y=shelf_y,
        body_w=int(w * 0.040),
        neck_w=int(w * 0.014),
        neck_h=int(h * 0.16),
        body_h=int(h * 0.18),
        shoulder_h=int(h * 0.06),
        col_lit=VESSEL_PALE,
        col_mid=VESSEL_ASH_WARM,
        col_shadow=SHADOW_FLANK,
    )

    # ── Vessel 2: Medium vase, warmest ────────────────────────────────────────
    draw_cylinder_vessel(
        arr,
        cx=int(w * 0.36),
        shelf_y=shelf_y,
        body_w=int(w * 0.055),
        neck_w=int(w * 0.022),
        neck_h=int(h * 0.09),
        body_h=int(h * 0.20),
        shoulder_h=int(h * 0.08),
        col_lit=VESSEL_OCHRE,
        col_mid=VESSEL_ASH_WARM,
        col_shadow=SHADOW_FLANK,
    )

    # ── Vessel 3: Squat round jar, center ─────────────────────────────────────
    draw_squat_jar(
        arr,
        cx=int(w * 0.50),
        shelf_y=shelf_y,
        body_w=int(w * 0.052),
        body_h=int(h * 0.15),
        lid_h=int(h * 0.025),
        col_lit=VESSEL_RIM,
        col_mid=VESSEL_GREY,
        col_shadow=SHADOW_FLANK,
    )

    # ── Vessel 4: Second tall bottle, slightly behind, right-center ───────────
    draw_cylinder_vessel(
        arr,
        cx=int(w * 0.62),
        shelf_y=shelf_y,
        body_w=int(w * 0.038),
        neck_w=int(w * 0.016),
        neck_h=int(h * 0.20),
        body_h=int(h * 0.17),
        shoulder_h=int(h * 0.05),
        col_lit=VESSEL_MID,
        col_mid=VESSEL_BLUE_GREY,
        col_shadow=SHADOW_FLANK,
    )

    # ── Vessel 5: Shallow oval bowl, right ─────────────────────────────────────
    draw_oval_bowl(
        arr,
        cx=int(w * 0.81),
        shelf_y=shelf_y,
        outer_w=int(w * 0.080),
        height=int(h * 0.055),
        col_rim=VESSEL_GREY,
        col_interior=BOWL_INTERIOR,
        col_shadow=SHADOW_FLANK,
    )

    arr_uint8 = np.clip(arr * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(arr_uint8, "RGB")


def main():
    print("Session 258 -- Five Vessels, Morning Light (after Giorgio Morandi)")
    print(f"Canvas: {W}x{H}")
    print()

    ref = build_reference(W, H)
    print("Reference built.")

    p = Painter(W, H)

    # Ground: warm linen-grey imprimatura
    print("Toning ground...")
    p.tone_ground((0.82, 0.79, 0.70), texture_strength=0.022)

    # Block in: wall, shelf, vessel masses
    print("Blocking in masses...")
    p.block_in(ref, stroke_size=30, n_strokes=160)

    # Build form: tonal gradation on vessel bodies
    print("Building form...")
    p.build_form(ref, stroke_size=12, n_strokes=120)

    # Place lights: pale highlights on lit flanks and bowl interior
    print("Placing lights...")
    p.place_lights(ref, stroke_size=5, n_strokes=80)

    # ── Morandi Dusty Vessel pass (169th mode) ────────────────────────────────
    print("Applying Morandi Dusty Vessel pass...")
    p.morandi_dusty_vessel_pass(
        dust_veil=0.52,         # moderate saturation loss in shadows
        compress_strength=0.38, # Morandi narrow tonal window
        target_mid=0.54,        # compress toward warm cream mid
        reveal_threshold=0.68,  # ochre shows in the lightest ~32% of pixels
        reveal_strength=0.22,   # subtle warm-gold glow in highlights
        ochre_r=0.88,
        ochre_g=0.80,
        ochre_b=0.52,
        opacity=0.82,
    )

    # ── Granulation pass (improvement) ───────────────────────────────────────
    print("Applying Granulation pass...")
    p.paint_granulation_pass(
        granule_sigma=3.0,      # medium-fine paint surface scale
        granule_scale=0.12,     # moderate granulation amplitude
        warm_shift=0.035,       # very subtle warm-in-valley
        cool_shift=0.035,       # very subtle cool-on-ridge
        edge_sharpen=0.25,      # restore gentle edge definition
        opacity=0.68,
    )

    # ── Edge Temperature pass (s256) ────────────────────────────────────────
    print("Applying Edge Temperature pass...")
    p.paint_edge_temperature_pass(
        warm_hue_center=0.09,   # ochre/amber warm
        warm_hue_width=0.20,
        cool_hue_center=0.60,   # blue-grey cool
        cool_hue_width=0.18,
        gradient_zone_px=3.0,
        contrast_strength=0.07, # very gentle -- Morandi's edges dissolve
        opacity=0.50,
    )

    # ── Tonal Key pass (s255) ──────────────────────────────────────────────
    print("Applying Tonal Key pass...")
    p.paint_tonal_key_pass(
        target_key=0.62,        # slightly high-key (morning light)
        key_strength=2.0,
        dither_amplitude=0.003,
        opacity=0.38,
    )

    # ── Shadow Bleed pass (s257) ───────────────────────────────────────────
    print("Applying Shadow Bleed pass...")
    p.paint_shadow_bleed_pass(
        shadow_threshold=0.42,  # vessel shadow flanks
        bright_threshold=0.72,  # vessel lit faces and bowl interior
        bleed_sigma=12.0,       # wide bleed -- warm light diffuses through studio
        reflect_strength=0.12,  # very subtle bounce
        warm_r=0.86,
        warm_g=0.78,
        warm_b=0.52,
        opacity=0.55,
    )

    # Save
    print(f"Saving to {OUTPUT_PATH}...")
    p.save(OUTPUT_PATH)
    print("Done.")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
