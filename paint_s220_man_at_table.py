"""
paint_s220_man_at_table.py — Original composition: "The Patient One"

Session 220 painting — inspired by Luc Tuymans (1958–present).

IMAGE DESCRIPTION
=================
Subject & Composition:
  An elderly man, viewed from slightly above at a three-quarter angle, is
  seated at a bare kitchen table. He is the sole subject. A single white
  ceramic cup sits on the table directly in front of him, untouched.
  The composition is cropped — his knees disappear at the bottom edge;
  the ceiling cuts off just above his thinning hair. He sits near the
  left-centre of the frame; the empty right side of the table and the pale
  bare wall behind him carry as much presence as he does.

The Figure:
  Age: mid-seventies. Slender, slightly hunched. Wearing a plain pale
  grey button-up shirt — the kind that has been washed many times. His
  large, veined hands rest flat on the table. Head slightly bowed. He is
  not looking at the cup, not looking at the viewer. His gaze is directed
  somewhere just below the table's surface — interior, unreadable. Face:
  angular, deeply lined at the eyes and forehead, thin white hair
  side-parted. Mouth closed, not tense. Thin white eyebrows. The overall
  emotional state is not grief, not peace — it is the patience of someone
  who has stopped expecting much.

The Environment:
  A bare kitchen interior, northern light entering from a single unseen
  window at the upper left. The table surface is white formica — pale,
  flat, slightly reflective. The wall behind is painted a once-white
  colour that has greyed with time — nearly the same tone as the shirt.
  The floor is barely visible at the bottom edge, pale linoleum. No
  objects on the wall. No curtains visible. A single overhead light is
  off — all illumination is the cold, flat, diffuse north light. No
  shadows are deep; no highlights are warm. The room refuses to be cosy.

Technique & Palette:
  Luc Tuymans style — 131st distinct mode: tuymans_pale_wash_pass.
  Near-achromatic palette: pale bone, washed grey, cold off-white.
  The flesh of the hands and face retains only the faintest warmth —
  not enough to comfort. tuymans_pale_wash_pass strips chromatic
  saturation, applies a cold north-light pallor, compresses the tonal
  range to create the washed-out quality.
  bristle_separation_texture_pass (session 220 improvement) adds
  the micro-striations of a fanned brush — the bare, functional mark-
  making of someone working quickly, without sentiment.

  Palette:
    — Pale bone white      (0.88, 0.86, 0.82)   — table surface, shirt highlight
    — Warm light grey      (0.76, 0.73, 0.68)   — lit flesh, hair
    — Cool middle grey     (0.60, 0.58, 0.55)   — wall, shadow zones
    — Muted neutral grey   (0.44, 0.42, 0.40)   — shirt shadow, hands shadow
    — Desaturated warm     (0.82, 0.79, 0.73)   — face midtone, flesh
    — Pale sienna-grey     (0.64, 0.61, 0.57)   — shadow flesh, eye zone
    — Near-black grey      (0.34, 0.32, 0.30)   — deepest values, iris
    — Near-white           (0.93, 0.92, 0.90)   — cup interior, overexposed

Mood & Intent:
  This painting is about the weight of a Sunday morning in winter.
  Not sorrow — the man is not performing sadness. He is simply present,
  the way furniture is present. The cold north light strips the scene
  of comfort and significance. The cup of coffee cools. Tuymans believed
  that the ordinary, rendered precisely and without sentimentality,
  becomes permanently strange. Walk away from this painting with the
  feeling that you have just looked at something that should not have
  mattered — and does.
"""

import numpy as np
from PIL import Image, ImageFilter

from stroke_engine import Painter
from art_catalog import get_style

W, H = 780, 1040   # portrait — figure at table, slightly cropped


def _blend(base: np.ndarray, color: tuple, alpha_hw: np.ndarray) -> np.ndarray:
    """Alpha-blend color (RGB float) into base (H, W, 3) using alpha (H, W)."""
    c = np.array(color, dtype=np.float32)
    a = np.clip(alpha_hw, 0.0, 1.0)[:, :, np.newaxis]
    return base + (c - base) * a


def build_reference(w: int, h: int) -> Image.Image:
    """
    Synthetic reference: elderly man seated at bare kitchen table.
    Cold north light; near-achromatic palette.
    """
    arr = np.zeros((h, w, 3), dtype=np.float32)

    yf = np.linspace(0.0, 1.0, h)
    xf = np.linspace(0.0, 1.0, w)
    yy = yf[:, np.newaxis]   # (H, 1)
    xx = xf[np.newaxis, :]   # (1, W)

    rng = np.random.RandomState(220)

    # ── Background wall: pale grey-white, slightly dirty ──────────────────────
    arr[:, :, 0] = 0.76
    arr[:, :, 1] = 0.75
    arr[:, :, 2] = 0.73

    # Subtle tonal variation — uneven north light across the wall
    for _ in range(6):
        cx = rng.uniform(0.0, 1.0)
        cy = rng.uniform(0.0, 0.70)
        r  = rng.uniform(0.20, 0.55)
        val = rng.uniform(-0.04, 0.05)
        dist = np.sqrt(((xx - cx) / (r * 0.8))**2 + ((yy - cy) / r)**2)
        pa = np.clip(1.0 - dist, 0.0, 1.0) ** 1.5 * val
        arr[:, :, :] += pa[:, :, np.newaxis] * np.array([1.0, 1.0, 1.0])

    # North light brightening: slightly brighter upper-left
    light_dist = np.sqrt(((xx - 0.0) / 0.55)**2 + ((yy - 0.0) / 0.55)**2)
    light_a = np.clip(1.0 - light_dist, 0.0, 1.0) ** 0.7 * 0.08
    arr = _blend(arr, (0.90, 0.90, 0.91), light_a)

    # Fine wall texture noise
    noise = rng.uniform(-0.012, 0.012, (h, w)).astype(np.float32)
    arr[:, :, 0] += noise
    arr[:, :, 1] += noise * 0.9
    arr[:, :, 2] += noise * 0.85

    # ── Table: white formica, flat surface, occupies lower 40% ───────────────
    table_top = 0.60
    table_a = np.clip((yy - table_top) / 0.04, 0.0, 1.0) ** 0.8
    table_a = np.broadcast_to(table_a, (h, w)).copy()
    arr = _blend(arr, (0.88, 0.87, 0.85), table_a * 0.88)

    # Table edge: subtle dark line where wall meets table top
    edge_y = 0.605
    edge_a = np.clip(1.0 - np.abs(yy - edge_y) / 0.006, 0.0, 1.0) * 0.35
    edge_a = np.broadcast_to(edge_a, (h, w)).copy()
    arr = _blend(arr, (0.50, 0.49, 0.47), edge_a)

    # Table light reflection from north window: subtle brightest area upper-left of table
    refl_dist = np.sqrt(((xx - 0.20) / 0.30)**2 + ((yy - 0.64) / 0.12)**2)
    refl_a = np.clip(1.0 - refl_dist, 0.0, 1.0) ** 2.0 * 0.12
    arr = _blend(arr, (0.93, 0.93, 0.94), refl_a)

    # ── White ceramic cup: small, centred slightly left of mid-table ──────────
    cup_cx, cup_cy = 0.46, 0.73
    # Cup body ellipse
    cup_rx, cup_ry = 0.040, 0.048
    cup_dist = np.sqrt(((xx - cup_cx) / cup_rx)**2 + ((yy - cup_cy) / cup_ry)**2)
    cup_a = np.clip(1.0 - cup_dist, 0.0, 1.0) ** 0.65 * 0.92
    arr = _blend(arr, (0.88, 0.87, 0.85), cup_a)

    # Cup left edge — faint shadow
    cup_shadow_dist = np.sqrt(((xx - (cup_cx - 0.025)) / 0.008)**2 +
                              ((yy - cup_cy) / 0.038)**2)
    cup_shadow_a = np.clip(1.0 - cup_shadow_dist, 0.0, 1.0) ** 1.2 * 0.28
    arr = _blend(arr, (0.60, 0.59, 0.58), cup_shadow_a)

    # Cup interior top — slight darker oval
    cup_top_dist = np.sqrt(((xx - cup_cx) / 0.032)**2 +
                           ((yy - (cup_cy - 0.028)) / 0.012)**2)
    cup_top_a = np.clip(1.0 - cup_top_dist, 0.0, 1.0) ** 0.85 * 0.55
    arr = _blend(arr, (0.70, 0.68, 0.64), cup_top_a)

    # Cup highlight — small bright catch on upper-right rim
    cup_hi_dist = np.sqrt(((xx - (cup_cx + 0.022)) / 0.009)**2 +
                          ((yy - (cup_cy - 0.030)) / 0.006)**2)
    cup_hi_a = np.clip(1.0 - cup_hi_dist, 0.0, 1.0) ** 1.7 * 0.60
    arr = _blend(arr, (0.93, 0.93, 0.94), cup_hi_a)

    # Cup cast shadow on table surface — soft, cool
    cast_dist = np.sqrt(((xx - (cup_cx + 0.005)) / 0.055)**2 +
                        ((yy - (cup_cy + 0.028)) / 0.020)**2)
    cast_a = np.clip(1.0 - cast_dist, 0.0, 1.0) ** 1.4 * 0.18
    arr = _blend(arr, (0.68, 0.67, 0.66), cast_a)

    # ── Torso / shirt: pale grey, hunched, below head ─────────────────────────
    torso_cx, torso_cy = 0.46, 0.60
    torso_rx, torso_ry = 0.185, 0.240
    torso_dist = np.sqrt(((xx - torso_cx) / torso_rx)**2 +
                         ((yy - torso_cy) / torso_ry)**2)
    torso_a = np.clip(1.0 - torso_dist, 0.0, 1.0) ** 0.60
    arr = _blend(arr, (0.78, 0.77, 0.74), torso_a * 0.85)

    # Shirt shadow — left side, away from window
    shirt_shd_dist = np.sqrt(((xx - 0.32) / 0.090)**2 + ((yy - 0.56) / 0.180)**2)
    shirt_shd_a = np.clip(1.0 - shirt_shd_dist, 0.0, 1.0) ** 1.0 * 0.45
    arr = _blend(arr, (0.55, 0.54, 0.52), shirt_shd_a)

    # Shirt lit region — right side, faint north light
    shirt_lit_dist = np.sqrt(((xx - 0.58) / 0.075)**2 + ((yy - 0.50) / 0.140)**2)
    shirt_lit_a = np.clip(1.0 - shirt_lit_dist, 0.0, 1.0) ** 1.2 * 0.32
    arr = _blend(arr, (0.86, 0.85, 0.83), shirt_lit_a)

    # Button placket — faint vertical line
    placket_a = np.clip(1.0 - np.abs(xx - 0.462) / 0.006, 0.0, 1.0) * \
                np.clip((yy - 0.38) / 0.02, 0.0, 1.0) * \
                np.clip((0.72 - yy) / 0.02, 0.0, 1.0) * 0.18
    placket_a = np.broadcast_to(placket_a, (h, w)).copy()
    arr = _blend(arr, (0.60, 0.59, 0.58), placket_a)

    # ── Hands: large, veined, resting flat on table ───────────────────────────
    # Left hand — left of cup, slightly closer to edge of table
    for hx, hy, hrx, hry, hstr in [
        (0.28, 0.685, 0.068, 0.030, 0.85),   # left hand, main mass
        (0.64, 0.700, 0.065, 0.028, 0.82),   # right hand, main mass
    ]:
        hd = np.sqrt(((xx - hx) / hrx)**2 + ((yy - hy) / hry)**2)
        ha = np.clip(1.0 - hd, 0.0, 1.0) ** 0.70 * hstr
        arr = _blend(arr, (0.80, 0.76, 0.70), ha)

    # Hand veins / finger separation lines — faint darker lines
    for vx, vy, vangle, vlen in [
        (0.265, 0.678, -0.2, 0.028),
        (0.295, 0.673, 0.1, 0.025),
        (0.320, 0.676, 0.0, 0.022),
        (0.630, 0.695, -0.15, 0.026),
        (0.655, 0.690, 0.05, 0.024),
        (0.680, 0.693, 0.2, 0.022),
    ]:
        vein_dist = np.abs((xx - vx) * np.cos(vangle) + (yy - vy) * np.sin(vangle)) / 0.005
        vein_a = np.clip(1.0 - vein_dist, 0.0, 1.0) ** 1.3 * 0.22
        vein_a = np.broadcast_to(vein_a, (h, w)).copy()
        arr = _blend(arr, (0.58, 0.55, 0.52), vein_a)

    # Hand knuckle highlights — small catches of north light on knuckle peaks
    for kx, ky in [(0.255, 0.672), (0.285, 0.668), (0.310, 0.671),
                   (0.628, 0.686), (0.653, 0.683), (0.678, 0.686)]:
        kd = np.sqrt(((xx - kx) / 0.009)**2 + ((yy - ky) / 0.006)**2)
        ka = np.clip(1.0 - kd, 0.0, 1.0) ** 1.6 * 0.40
        arr = _blend(arr, (0.88, 0.86, 0.83), ka)

    # ── Neck: brief passage between jaw and shirt collar ──────────────────────
    neck_cx, neck_cy = 0.46, 0.37
    neck_rx, neck_ry = 0.040, 0.042
    neck_dist = np.sqrt(((xx - neck_cx) / neck_rx)**2 +
                        ((yy - neck_cy) / neck_ry)**2)
    neck_a = np.clip(1.0 - neck_dist, 0.0, 1.0) ** 0.75 * 0.82
    arr = _blend(arr, (0.80, 0.75, 0.68), neck_a)

    # ── Head: oval, slightly bowed, three-quarter ─────────────────────────────
    head_cx, head_cy = 0.46, 0.215
    head_rx, head_ry = 0.090, 0.108
    head_dist = np.sqrt(((xx - head_cx) / head_rx)**2 +
                        ((yy - head_cy) / head_ry)**2)
    head_a = np.clip(1.0 - head_dist, 0.0, 1.0) ** 0.62
    arr = _blend(arr, (0.80, 0.75, 0.68), head_a * 0.88)

    # North-light: cool bright on upper-left of face
    lit_dist = np.sqrt(((xx - 0.42) / 0.060)**2 + ((yy - 0.190) / 0.065)**2)
    lit_a = np.clip(1.0 - lit_dist, 0.0, 1.0) ** 1.4 * 0.42
    arr = _blend(arr, (0.86, 0.83, 0.79), lit_a)

    # Right cheek — shadow, turned away from light
    rche_dist = np.sqrt(((xx - 0.52) / 0.048)**2 + ((yy - 0.225) / 0.052)**2)
    rche_a = np.clip(1.0 - rche_dist, 0.0, 1.0) ** 1.3 * 0.38
    arr = _blend(arr, (0.60, 0.57, 0.53), rche_a)

    # Forehead — broad, lit
    forehead_dist = np.sqrt(((xx - 0.46) / 0.068)**2 + ((yy - 0.148) / 0.038)**2)
    forehead_a = np.clip(1.0 - forehead_dist, 0.0, 1.0) ** 1.0 * 0.62
    arr = _blend(arr, (0.84, 0.80, 0.74), forehead_a)

    # Forehead lines — faint horizontal creases
    for line_y in [0.152, 0.164, 0.176]:
        hl_a = np.clip(1.0 - np.abs(yy - line_y) / 0.003, 0.0, 1.0) * \
               np.clip(1.0 - head_dist * 0.8, 0.0, 1.0) * 0.14
        hl_a = np.broadcast_to(hl_a, (h, w)).copy()
        arr = _blend(arr, (0.62, 0.59, 0.55), hl_a)

    # ── Hair: thin, white, side-parted ────────────────────────────────────────
    hair_dist = np.sqrt(((xx - 0.46) / 0.092)**2 + ((yy - 0.116) / 0.062)**2)
    hair_a = np.clip(1.0 - hair_dist, 0.0, 1.0) ** 0.65 * (yy < 0.148)
    hair_a = np.broadcast_to(hair_a, (h, w)).copy()
    arr = _blend(arr, (0.82, 0.81, 0.80), hair_a * 0.75)

    # Hair shadow — slightly darker than the head, receding
    hair_shd_dist = np.sqrt(((xx - 0.52) / 0.040)**2 + ((yy - 0.118) / 0.035)**2)
    hair_shd_a = np.clip(1.0 - hair_shd_dist, 0.0, 1.0) ** 1.5 * 0.30
    arr = _blend(arr, (0.62, 0.60, 0.58), hair_shd_a)

    # ── Eyes: downcast, not meeting viewer ────────────────────────────────────
    for ex, ey in [(0.428, 0.218), (0.496, 0.212)]:
        # Eye socket shadow — tired skin around eye
        socket_dist = np.sqrt(((xx - ex) / 0.026)**2 + ((yy - ey) / 0.018)**2)
        socket_a = np.clip(1.0 - socket_dist, 0.0, 1.0) ** 0.90 * 0.45
        arr = _blend(arr, (0.60, 0.56, 0.52), socket_a)
        # Iris / pupil — downcast, looking at nothing
        iris_dist = np.sqrt(((xx - (ex + 0.002)) / 0.011)**2 +
                            ((yy - (ey + 0.006)) / 0.011)**2)
        iris_a = np.clip(1.0 - iris_dist, 0.0, 1.0) ** 1.4 * 0.85
        arr = _blend(arr, (0.35, 0.33, 0.31), iris_a)
        # White of eye — barely visible, mostly shadowed by downcast lid
        white_dist = np.sqrt(((xx - ex) / 0.018)**2 +
                             ((yy - (ey - 0.004)) / 0.010)**2)
        white_a = np.clip(1.0 - white_dist, 0.0, 1.0) ** 1.2 * 0.40
        arr = _blend(arr, (0.84, 0.83, 0.82), white_a)

    # ── Eyebrows: thin, white, barely there ──────────────────────────────────
    for brx, bry in [(0.428, 0.198), (0.496, 0.193)]:
        br_dist = np.sqrt(((xx - brx) / 0.025)**2 + ((yy - bry) / 0.006)**2)
        br_a = np.clip(1.0 - br_dist, 0.0, 1.0) ** 1.2 * 0.28
        arr = _blend(arr, (0.72, 0.70, 0.68), br_a)

    # ── Nose: angular, prominent, cast slight shadow ──────────────────────────
    nose_dist = np.sqrt(((xx - 0.460) / 0.014)**2 + ((yy - 0.255) / 0.035)**2)
    nose_a = np.clip(1.0 - nose_dist, 0.0, 1.0) ** 0.95 * 0.58
    arr = _blend(arr, (0.72, 0.67, 0.60), nose_a)

    nose_shd_dist = np.sqrt(((xx - 0.446) / 0.009)**2 + ((yy - 0.262) / 0.020)**2)
    nose_shd_a = np.clip(1.0 - nose_shd_dist, 0.0, 1.0) ** 1.3 * 0.35
    arr = _blend(arr, (0.55, 0.52, 0.49), nose_shd_a)

    # ── Mouth: closed, thin, no expression ───────────────────────────────────
    mouth_dist = np.sqrt(((xx - 0.458) / 0.032)**2 + ((yy - 0.293) / 0.008)**2)
    mouth_a = np.clip(1.0 - mouth_dist, 0.0, 1.0) ** 1.1 * 0.58
    arr = _blend(arr, (0.58, 0.54, 0.50), mouth_a)

    # Lip line — barely a line, no colour
    lip_a = np.clip(1.0 - np.abs(yy - 0.295) / 0.003, 0.0, 1.0) * \
            np.clip(1.0 - np.abs(xx - 0.458) / 0.028, 0.0, 1.0) * 0.20
    lip_a = np.broadcast_to(lip_a, (h, w)).copy()
    arr = _blend(arr, (0.52, 0.50, 0.48), lip_a)

    # ── Jaw and chin: prominent, angular ─────────────────────────────────────
    chin_dist = np.sqrt(((xx - 0.458) / 0.040)**2 + ((yy - 0.320) / 0.018)**2)
    chin_a = np.clip(1.0 - chin_dist, 0.0, 1.0) ** 1.1 * 0.40
    arr = _blend(arr, (0.72, 0.68, 0.62), chin_a)

    arr = np.clip(arr, 0.0, 1.0)
    arr_u8 = (arr * 255).astype(np.uint8)
    img = Image.fromarray(arr_u8, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    return img


def paint(output_path: str = "s220_man_at_table.png") -> str:
    """
    Paint 'The Patient One'.
    Luc Tuymans style: 131st mode — tuymans_pale_wash_pass.
    Session 220 improvement: bristle_separation_texture_pass.
    """
    print("=" * 64)
    print("  Session 220 — 'The Patient One'")
    print("  Elderly man at bare kitchen table, white cup untouched")
    print("  Technique: Luc Tuymans Contemporary Figuration")
    print("  131st mode: tuymans_pale_wash_pass")
    print("  + bristle_separation_texture_pass (session 220 improvement)")
    print("=" * 64)

    ref_img = build_reference(W, H)
    print(f"  Reference built  ({W}x{H})")

    tuymans = get_style("luc_tuymans")
    p = Painter(W, H)

    # Pale grey-beige ground — Tuymans' near-white, unassertive base
    print("  [1] Tone ground — pale grey-beige ...")
    p.tone_ground(tuymans.ground_color, texture_strength=0.04)

    # Underpainting — establish sparse tonal masses without warmth
    print("  [2] Underpainting — sparse masses ...")
    p.underpainting(ref_img, stroke_size=52, n_strokes=1200)

    # Block in — figure, wall, table surface
    print("  [3] Block in — figure and environment ...")
    p.block_in(ref_img, stroke_size=28, n_strokes=2000)

    # Build form — hands, face, cup, shirt detail
    print("  [4] Build form — face, hands, cup ...")
    p.build_form(ref_img, stroke_size=10, n_strokes=2200)

    # Place lights — cold north-light catches on knuckles, forehead, cup rim
    print("  [5] Place lights — cold north-light accents ...")
    p.place_lights(ref_img, stroke_size=3, n_strokes=280)

    # ── Tuymans signature pass — Pale Wash ────────────────────────────────────
    print("  [6] tuymans_pale_wash_pass (131st mode) ...")
    p.tuymans_pale_wash_pass(
        desaturation_strength=0.72,
        pallor_cool=0.18,
        tonal_compression=0.28,
        thin_paint_blur=1.2,
        opacity=0.80,
    )

    # ── Session 220 artistic improvement — Bristle Separation Texture ─────────
    print("  [7] bristle_separation_texture_pass (session 220 improvement) ...")
    p.bristle_separation_texture_pass(
        separation_strength=0.35,
        bristle_count=5,
        bristle_angle_jitter=0.30,
        highlight_boost=0.10,
        shadow_deepen=0.07,
        opacity=0.50,
    )

    # Edge definition — restrained; Tuymans' edges are precise but not harsh
    print("  [8] Edge definition ...")
    p.edge_definition_pass(strength=0.22)

    # Meso detail — surface of hands, shirt texture, wall imperfections
    print("  [9] Meso detail ...")
    p.meso_detail_pass(opacity=0.16)

    # Canvas grain — linen texture breathes through thin paint
    print("  [10] Canvas grain ...")
    p.canvas_grain_pass()

    # No glaze — Tuymans leaves the surface bare and unvarnished
    # Minimal vignette — just enough to anchor the composition
    print("  [11] Finish ...")
    p.finish(vignette=0.10, crackle=False)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    out = paint()
    print(f"\n  Done: {out}")
