"""
paint_s219_dancer.py — Original composition: "La Tournade"
(The Turn)

Session 219 painting — inspired by Giovanni Boldini (1842–1931).

IMAGE DESCRIPTION
=================
Subject & Composition:
  A young woman, viewed from slightly below at a three-quarter angle, is
  caught mid-turn at the edge of a gaslit Paris salon. She has just pivoted
  on her heel to face the viewer — a movement arrested rather than posed.
  She is the sole subject; the salon environment dissolves around her into
  spiraling warm darkness.

The Figure:
  Age: mid-twenties, oval face — high cheekbones, luminous ivory skin, dark
  expressive eyes with a spark of cool white at the inner corner. Her dark
  chestnut hair is swept up in a loose arrangement, a few tendrils falling
  free at the neck. She wears an evening gown of deep blue-black silk, the
  bodice tightly fitted, the skirt flaring outward from the hips in a silk
  cascade that is still in motion — the turn has not yet resolved. The
  neckline is low, a small pearl pendant on a gold chain catching the light.
  One gloved hand extends slightly outward, fingers loosely spread, as though
  she was in conversation a moment ago. Emotional state: vivid social
  electricity — delighted surprise at being noticed, a slight arch of
  amusement, consciousness of her own beauty, and the unmistakable energy
  of someone who controls every room they enter.

The Environment:
  A grand Paris salon at night, ca. 1895. Behind her: the warm umber-gold
  blur of gaslit chandeliers, indistinct figures in dark formalwear, the
  ghost of gilt mirror frames and wall sconces. The background is
  deliberately dissolved into Boldini's signature swirling marks — warm gold
  halos from the chandelier, deep umber in the social shadow. Floor: a pale
  champagne parquet, catching a warm reflection of the chandelier. Foreground:
  nothing competes with the figure. The space she inhabits is intimate and
  immediate; the salon crowds the dark behind her.

Technique & Palette:
  Giovanni Boldini Belle Époque — 130th distinct mode:
  boldini_belle_epoque_swirl_pass. Radial spiral warp centred on the figure
  dissolves the background into centrifugal brushwork. Warm gold chromatic
  enhancement bathes the ivory skin and the pale champagne areas in gaslit
  warmth. Directional edge elongation turns dress folds and background details
  into long calligraphic swirls. The chromatic_zoning_pass (session 219
  improvement) deepens the cool-ambient shadow articulation in the dress and
  background, enriches the midtone carnation warmth in the skin, and
  desaturates the pearl/ivory highlights toward bone-white.

  Palette:
    — Warm ivory flesh     (0.90, 0.82, 0.68)   — face, neck, décolletage
    — Gold gaslight        (0.96, 0.88, 0.62)   — forehead, cheekbone highlight
    — Mid-tone sienna      (0.78, 0.56, 0.32)   — face shadow, jaw transition
    — Deep blue-black silk (0.14, 0.16, 0.26)   — gown mass
    — Champagne-white      (0.92, 0.90, 0.88)   — skirt highlight, glove
    — Mauve silk fold      (0.62, 0.50, 0.68)   — dress fold, shadow
    — Warm umber salon     (0.28, 0.18, 0.10)   — background mass
    — Icy pearl white      (0.95, 0.95, 0.97)   — pearl pendant, eye spark

Mood & Intent:
  Boldini believed that a portrait must capture not the person as they are
  when standing still — anyone can paint a statue — but as they are in the
  instant before thought catches up with movement. This woman is in that
  instant. She is all energy and self-possession. Walk away from this painting
  feeling the heat of a Paris salon at its best hour: the candles, the silk,
  the conversation, the danger of being seen. The swirling brushwork refuses
  to let the eye rest; it pushes you back toward the face, the hand, the
  living centre of the composition.
"""

import numpy as np
from PIL import Image, ImageFilter

from stroke_engine import Painter
from art_catalog import get_style

W, H = 780, 1040   # portrait — standing figure, floor visible at bottom


def _blend(base: np.ndarray, color: tuple, alpha_hw: np.ndarray) -> np.ndarray:
    """Alpha-blend color (RGB float) into base (H, W, 3) using alpha (H, W)."""
    c = np.array(color, dtype=np.float32)
    a = np.clip(alpha_hw, 0.0, 1.0)[:, :, np.newaxis]
    return base + (c - base) * a


def build_dancer_reference(w: int, h: int) -> Image.Image:
    """
    Synthetic reference: young woman mid-turn in Paris salon.
    Background: warm umber with gaslit chandeliers. Figure: ivory flesh
    in deep blue-black silk gown. Floor: pale champagne parquet.
    """
    arr = np.zeros((h, w, 3), dtype=np.float32)

    yf = np.linspace(0.0, 1.0, h)
    xf = np.linspace(0.0, 1.0, w)
    yy = yf[:, np.newaxis]   # (H, 1)
    xx = xf[np.newaxis, :]   # (1, W)

    rng = np.random.RandomState(219)

    # ── Background: deep warm umber salon ─────────────────────────────────────
    arr[:, :, 0] = 0.28
    arr[:, :, 1] = 0.18
    arr[:, :, 2] = 0.10

    # Large-scale umber variation — salon depth
    for _ in range(8):
        cx = rng.uniform(0.0, 1.0)
        cy = rng.uniform(0.0, 0.80)
        r  = rng.uniform(0.18, 0.45)
        warm = rng.uniform(0.03, 0.10)
        dist = np.sqrt((xx - cx)**2 + (yy - cy)**2)
        pa = np.clip(1.0 - dist / r, 0.0, 1.0) ** 1.8 * warm
        arr[:, :, 0] += pa * rng.uniform(0.04, 0.14)
        arr[:, :, 1] += pa * rng.uniform(0.02, 0.08)
        arr[:, :, 2] += pa * rng.uniform(0.01, 0.04)

    noise = rng.uniform(-0.018, 0.018, (h, w)).astype(np.float32)
    arr[:, :, 0] += noise * 0.9
    arr[:, :, 1] += noise * 0.7
    arr[:, :, 2] += noise * 0.4

    # ── Chandelier glow: warm gold halos upper centre ─────────────────────────
    for chand_x, chand_y, chand_r, chand_str in [
        (0.50, 0.04, 0.22, 0.52),
        (0.22, 0.06, 0.14, 0.30),
        (0.78, 0.07, 0.14, 0.28),
    ]:
        chand_dist = np.sqrt(((xx - chand_x) / (chand_r * 0.5))**2 +
                             ((yy - chand_y) / (chand_r * 0.35))**2)
        core_a = np.clip(1.0 - chand_dist, 0.0, 1.0) ** 0.5 * chand_str
        arr = _blend(arr, (0.97, 0.91, 0.64), core_a)

        halo_dist = np.sqrt(((xx - chand_x) / chand_r)**2 +
                            ((yy - chand_y) / (chand_r * 0.75))**2)
        halo_a = np.clip(1.0 - halo_dist, 0.0, 1.0) ** 2.0 * chand_str * 0.45
        arr = _blend(arr, (0.78, 0.60, 0.30), halo_a)

    # ── Gilt mirror frame: right edge upper ───────────────────────────────────
    mirror_a = np.clip((xx - 0.78) / 0.06, 0.0, 1.0) * np.clip((0.55 - yy) / 0.40, 0.0, 1.0)
    mirror_a = np.broadcast_to(mirror_a, (h, w)).copy()
    arr = _blend(arr, (0.58, 0.44, 0.18), mirror_a * 0.38)

    # ── Background figures: dark silhouettes at middle depth ──────────────────
    for fx, fy in [(0.14, 0.40), (0.82, 0.38), (0.72, 0.46)]:
        fig_dist = np.sqrt(((xx - fx) / 0.045)**2 + ((yy - fy) / 0.160)**2)
        fig_a = np.clip(1.0 - fig_dist, 0.0, 1.0) ** 0.65 * 0.72
        arr = _blend(arr, (0.14, 0.09, 0.06), fig_a)

    # ── Parquet floor: champagne warm horizontal band ─────────────────────────
    floor_top = 0.88
    floor_a = np.clip((yy - floor_top) / 0.05, 0.0, 1.0) ** 0.7
    floor_a = np.broadcast_to(floor_a, (h, w)).copy()
    arr = _blend(arr, (0.72, 0.66, 0.50), floor_a * 0.70)

    # Parquet reflection of chandelier glow on floor
    refl_dist = np.sqrt(((xx - 0.50) / 0.30)**2 + ((yy - 0.94) / 0.08)**2)
    refl_a = np.clip(1.0 - refl_dist, 0.0, 1.0) ** 1.5 * 0.38
    arr = _blend(arr, (0.90, 0.82, 0.55), refl_a)

    # Parquet lines — thin horizontal stripes
    for line_y in np.arange(0.890, 0.980, 0.018):
        line_a = np.clip(1.0 - np.abs(yy - line_y) / 0.002, 0.0, 1.0) * \
                 np.clip((yy - floor_top) / 0.05, 0.0, 1.0) * 0.22
        line_a = np.broadcast_to(line_a, (h, w)).copy()
        arr = _blend(arr, (0.50, 0.42, 0.28), line_a)

    # ── Gown: deep blue-black silk mass — main figure body ────────────────────
    # Bodice: fitted ellipse, upper figure (approx 0.32–0.68 x, 0.38–0.82 y)
    bodice_cx, bodice_cy = 0.50, 0.58
    bodice_rx, bodice_ry = 0.150, 0.220
    bodice_dist = np.sqrt(((xx - bodice_cx) / bodice_rx)**2 +
                          ((yy - bodice_cy) / bodice_ry)**2)
    bodice_a = np.clip(1.0 - bodice_dist, 0.0, 1.0) ** 0.55
    arr = _blend(arr, (0.14, 0.16, 0.26), bodice_a * 0.94)

    # Skirt: wider flare from hip level downward, asymmetrically tilted (mid-turn)
    skirt_cx, skirt_cy = 0.52, 0.80
    skirt_rx, skirt_ry = 0.290, 0.200
    skirt_dist = np.sqrt(((xx - skirt_cx) / skirt_rx)**2 +
                         ((yy - skirt_cy) / skirt_ry)**2)
    skirt_a = np.clip(1.0 - skirt_dist, 0.0, 1.0) ** 0.52
    arr = _blend(arr, (0.14, 0.16, 0.26), skirt_a * 0.90)

    # Skirt highlight — champagne-white caught by chandeliers
    skirt_hi_dist = np.sqrt(((xx - 0.38) / 0.095)**2 + ((yy - 0.78) / 0.065)**2)
    skirt_hi_a = np.clip(1.0 - skirt_hi_dist, 0.0, 1.0) ** 1.5 * 0.68
    arr = _blend(arr, (0.86, 0.84, 0.82), skirt_hi_a)

    # Silk folds — mauve-grey diagonal creases across skirt
    for fold_x, fold_y, fold_angle, fold_str in [
        (0.44, 0.76, 0.3, 0.42), (0.58, 0.82, -0.2, 0.35), (0.36, 0.86, 0.5, 0.30)
    ]:
        fold_dist = np.abs((xx - fold_x) * np.cos(fold_angle) +
                           (yy - fold_y) * np.sin(fold_angle)) / 0.025
        fold_a = np.clip(1.0 - fold_dist, 0.0, 1.0) ** 1.2 * \
                 np.clip(1.0 - skirt_dist, 0.0, 1.0) * fold_str
        fold_a = np.broadcast_to(fold_a, (h, w)).copy()
        arr = _blend(arr, (0.52, 0.44, 0.62), fold_a)

    # ── Gloved hand: champagne-white extended outward ─────────────────────────
    hand_cx, hand_cy = 0.76, 0.52
    hand_rx, hand_ry = 0.065, 0.030
    hand_dist = np.sqrt(((xx - hand_cx) / hand_rx)**2 +
                        ((yy - hand_cy) / hand_ry)**2)
    hand_a = np.clip(1.0 - hand_dist, 0.0, 1.0) ** 0.75 * 0.88
    arr = _blend(arr, (0.90, 0.88, 0.82), hand_a)

    # Glove sheen — icy highlight near fingertips
    finger_a = np.clip(1.0 - np.sqrt(((xx - 0.80) / 0.022)**2 +
                                     ((yy - 0.518) / 0.015)**2), 0.0, 1.0) ** 1.4 * 0.60
    arr = _blend(arr, (0.95, 0.95, 0.96), finger_a)

    # ── Neck + décolletage: ivory, open neckline ──────────────────────────────
    neck_cx, neck_cy = 0.50, 0.335
    neck_rx, neck_ry = 0.048, 0.060
    neck_dist = np.sqrt(((xx - neck_cx) / neck_rx)**2 +
                        ((yy - neck_cy) / neck_ry)**2)
    neck_a = np.clip(1.0 - neck_dist, 0.0, 1.0) ** 0.75 * 0.88
    arr = _blend(arr, (0.88, 0.78, 0.62), neck_a)

    # Décolletage — wider, soft blend
    decol_dist = np.sqrt(((xx - 0.50) / 0.110)**2 + ((yy - 0.395) / 0.048)**2)
    decol_a = np.clip(1.0 - decol_dist, 0.0, 1.0) ** 0.65 * 0.78
    arr = _blend(arr, (0.90, 0.80, 0.64), decol_a)

    # ── Pearl pendant: tiny icy ellipse at neck base ──────────────────────────
    pearl_dist = np.sqrt(((xx - 0.508) / 0.012)**2 + ((yy - 0.378) / 0.012)**2)
    pearl_a = np.clip(1.0 - pearl_dist, 0.0, 1.0) ** 1.3 * 0.85
    arr = _blend(arr, (0.93, 0.93, 0.96), pearl_a)
    pearl_hi_dist = np.sqrt(((xx - 0.505) / 0.005)**2 + ((yy - 0.374) / 0.005)**2)
    pearl_hi_a = np.clip(1.0 - pearl_hi_dist, 0.0, 1.0) ** 1.8 * 0.75
    arr = _blend(arr, (0.98, 0.98, 1.00), pearl_hi_a)

    # ── Head: oval, three-quarter, mid-turn ───────────────────────────────────
    head_cx, head_cy = 0.50, 0.195
    head_rx, head_ry = 0.092, 0.108
    head_dist = np.sqrt(((xx - head_cx) / head_rx)**2 +
                        ((yy - head_cy) / head_ry)**2)
    head_a = np.clip(1.0 - head_dist, 0.0, 1.0) ** 0.62
    arr = _blend(arr, (0.88, 0.76, 0.58), head_a * 0.90)

    # Chandelier gold on cheekbone + forehead right side
    lit_face_dist = np.sqrt(((xx - 0.54) / 0.058)**2 + ((yy - 0.185) / 0.065)**2)
    lit_face_a = np.clip(1.0 - lit_face_dist, 0.0, 1.0) ** 1.3 * 0.60
    arr = _blend(arr, (0.94, 0.86, 0.60), lit_face_a)

    # Left cheek — slightly cooler, turned into shadow
    cool_cheek_dist = np.sqrt(((xx - 0.44) / 0.048)**2 + ((yy - 0.205) / 0.055)**2)
    cool_cheek_a = np.clip(1.0 - cool_cheek_dist, 0.0, 1.0) ** 1.4 * 0.35
    arr = _blend(arr, (0.68, 0.62, 0.56), cool_cheek_a)

    # Forehead — broad, high, lit
    forehead_dist = np.sqrt(((xx - 0.50) / 0.068)**2 + ((yy - 0.130) / 0.042)**2)
    forehead_a = np.clip(1.0 - forehead_dist, 0.0, 1.0) ** 1.0 * 0.72
    arr = _blend(arr, (0.92, 0.82, 0.64), forehead_a)

    # ── Hair: dark chestnut swept up ──────────────────────────────────────────
    # Main hair mass above and around head
    hair_dist = np.sqrt(((xx - 0.50) / 0.098)**2 + ((yy - 0.112) / 0.068)**2)
    hair_a = np.clip(1.0 - hair_dist, 0.0, 1.0) ** 0.65 * (yy < 0.155)
    hair_a = np.broadcast_to(hair_a, (h, w)).copy()
    arr = _blend(arr, (0.28, 0.18, 0.10), hair_a * 0.90)

    # Hair highlight — chandelier catches the upswept arrangement
    hair_hi_dist = np.sqrt(((xx - 0.52) / 0.045)**2 + ((yy - 0.104) / 0.028)**2)
    hair_hi_a = np.clip(1.0 - hair_hi_dist, 0.0, 1.0) ** 1.6 * 0.58
    arr = _blend(arr, (0.62, 0.46, 0.28), hair_hi_a)

    # Loose tendrils at neck right side
    for tx, ty in [(0.58, 0.275), (0.61, 0.310)]:
        tendril_dist = np.sqrt(((xx - tx) / 0.015)**2 + ((yy - ty) / 0.030)**2)
        tendril_a = np.clip(1.0 - tendril_dist, 0.0, 1.0) ** 1.4 * 0.72
        arr = _blend(arr, (0.30, 0.20, 0.12), tendril_a)

    # ── Eyes: dark, expressive ────────────────────────────────────────────────
    for ex, ey in [(0.472, 0.200), (0.538, 0.193)]:
        socket_dist = np.sqrt(((xx - ex) / 0.025)**2 + ((yy - ey) / 0.016)**2)
        socket_a = np.clip(1.0 - socket_dist, 0.0, 1.0) ** 0.85 * 0.62
        arr = _blend(arr, (0.24, 0.15, 0.08), socket_a)
        iris_dist = np.sqrt(((xx - ex) / 0.013)**2 + ((yy - ey) / 0.013)**2)
        iris_a = np.clip(1.0 - iris_dist, 0.0, 1.0) ** 1.3 * 0.90
        arr = _blend(arr, (0.18, 0.20, 0.28), iris_a)
        hi_dist = np.sqrt(((xx - (ex + 0.005)) / 0.004)**2 +
                          ((yy - (ey - 0.005)) / 0.004)**2)
        hi_a = np.clip(1.0 - hi_dist, 0.0, 1.0) ** 1.6 * 0.82
        arr = _blend(arr, (0.95, 0.95, 0.97), hi_a)

    # ── Nose: delicate, slight three-quarter turn ─────────────────────────────
    nose_dist = np.sqrt(((xx - 0.505) / 0.013)**2 + ((yy - 0.240) / 0.035)**2)
    nose_a = np.clip(1.0 - nose_dist, 0.0, 1.0) ** 1.0 * 0.62
    arr = _blend(arr, (0.78, 0.58, 0.40), nose_a)

    nose_hi_dist = np.sqrt(((xx - 0.510) / 0.009)**2 + ((yy - 0.260) / 0.009)**2)
    nose_hi_a = np.clip(1.0 - nose_hi_dist, 0.0, 1.0) ** 1.6 * 0.50
    arr = _blend(arr, (0.92, 0.78, 0.60), nose_hi_a)

    # ── Mouth: slight arch, amused ────────────────────────────────────────────
    mouth_dist = np.sqrt(((xx - 0.50) / 0.034)**2 + ((yy - 0.278) / 0.010)**2)
    mouth_a = np.clip(1.0 - mouth_dist, 0.0, 1.0) ** 1.0 * 0.70
    arr = _blend(arr, (0.62, 0.28, 0.22), mouth_a)

    # Upper lip curve
    for lip_x, lip_y in [(0.490, 0.272), (0.510, 0.272)]:
        ulip_dist = np.sqrt(((xx - lip_x) / 0.010)**2 + ((yy - lip_y) / 0.007)**2)
        ulip_a = np.clip(1.0 - ulip_dist, 0.0, 1.0) ** 1.5 * 0.48
        arr = _blend(arr, (0.48, 0.20, 0.15), ulip_a)

    # Lip highlight — faint warmth on cupid's bow
    lhi_dist = np.sqrt(((xx - 0.50) / 0.018)**2 + ((yy - 0.275) / 0.006)**2)
    lhi_a = np.clip(1.0 - lhi_dist, 0.0, 1.0) ** 1.8 * 0.35
    arr = _blend(arr, (0.82, 0.50, 0.42), lhi_a)

    arr = np.clip(arr, 0.0, 1.0)
    arr_u8 = (arr * 255).astype(np.uint8)
    img = Image.fromarray(arr_u8, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(1.0))
    return img


def paint(output_path: str = "s219_dancer.png") -> str:
    """
    Paint 'La Tournade' (The Turn).
    Giovanni Boldini Belle Époque: 130th mode — boldini_belle_epoque_swirl_pass.
    Session 219 improvement: chromatic_zoning_pass.
    """
    print("=" * 64)
    print("  Session 219 — 'La Tournade' (The Turn)")
    print("  Young woman mid-turn at Paris salon, silk gown swirling")
    print("  Technique: Giovanni Boldini Belle Époque")
    print("  130th mode: boldini_belle_epoque_swirl_pass")
    print("  + chromatic_zoning_pass (session 219 improvement)")
    print("=" * 64)

    ref_img = build_dancer_reference(W, H)
    print(f"  Reference built  ({W}x{H})")

    boldini = get_style("giovanni_boldini")
    p = Painter(W, H)

    # Warm dark umber ground — Boldini's deep salon tonality
    print("  [1] Tone ground — warm dark umber ...")
    p.tone_ground(boldini.ground_color, texture_strength=0.06)

    # Broad underpainting — establish warm umber masses
    print("  [2] Underpainting — warm masses ...")
    p.underpainting(ref_img, stroke_size=48, n_strokes=1500)

    # Block in — figure, gown, background figures
    print("  [3] Block in — figure and salon ...")
    p.block_in(ref_img, stroke_size=30, n_strokes=2400)

    # Build form — face, neck, décolletage, hand detail
    print("  [4] Build form — face and silk detail ...")
    p.build_form(ref_img, stroke_size=12, n_strokes=2800)

    # Place lights — pearl, eye sparks, chandelier catches
    print("  [5] Place lights — chandelier and jewel accents ...")
    p.place_lights(ref_img, stroke_size=4, n_strokes=360)

    # ── Boldini signature pass — Belle Époque Swirl ───────────────────────────
    print("  [6] boldini_belle_epoque_swirl_pass (130th mode) ...")
    p.boldini_belle_epoque_swirl_pass(
        swirl_strength=8.0,
        swirl_falloff=0.55,
        gold_warmth=0.25,
        elongation_sigma=3.5,
        opacity=0.75,
    )

    # ── Session 219 artistic improvement — Chromatic Zoning ───────────────────
    print("  [7] chromatic_zoning_pass (session 219 improvement) ...")
    p.chromatic_zoning_pass(
        shadow_hue_shift=0.12,
        highlight_ivory_lift=0.08,
        midtone_saturation_boost=0.18,
        opacity=0.65,
    )

    # Edge definition — face contours, gown silhouette
    print("  [8] Edge definition ...")
    p.edge_definition_pass(strength=0.30)

    # Meso detail — silk sheen, hair detail, background ghost-figures
    print("  [9] Meso detail ...")
    p.meso_detail_pass(opacity=0.22)

    # Warm gold glaze — unify with Boldini's salon atmosphere
    print("  [10] Warm gold glaze ...")
    p.glaze((0.72, 0.58, 0.30), opacity=0.10)

    # Finish — moderate vignette pushes eye toward the figure
    print("  [11] Finish ...")
    p.finish(vignette=0.20, crackle=False)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    out = paint()
    print(f"\n  Done: {out}")
