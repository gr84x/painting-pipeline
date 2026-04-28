"""
paint_s222_last_light.py — Original composition: "The Last Light of Winter"

Session 222 painting — inspired by Helene Schjerfbeck (1862–1946).

IMAGE DESCRIPTION
=================
Subject & Composition:
  A single elderly Finnish woman in close three-quarter portrait, viewed from
  slightly above and fractionally to the right. The figure occupies most of the
  canvas vertically; the composition is tight and close — barely any air above
  the white hair, the blouse vanishing at the bottom edge. She is the only
  subject.

The Figure:
  Age: approximately eighty-five. Face in near-profile, tilted slightly
  downward and to the left. Sparse white hair pulled loosely back, a few
  strands falling at the temple. She wears a plain dark garment at the
  very bottom of the frame — the merest suggestion of a collar. Her eyes
  are closed, or cast so far down the lids dominate. The emotional state
  is interior stillness — not grief, not peace, but the specific quality
  of someone who has outlasted most of the things that once mattered. The
  skin has the translucence of very advanced age: thin over the cheekbones,
  nearly papery at the temple. The nose is delicate, the lips barely a
  thin line, the chin pointed.

The Environment:
  The background is almost nothing — a pale grey-white plane with the
  faintest suggestion of a tall window at the upper right, bleeding cold
  diffuse winter light. The boundary between background and figure is
  deliberately unclear at the periphery. Only the central oval of the face
  is fully articulated. Hair, ears, collar dissolve toward the edges.
  No furniture is visible. The ground is a warm linen-white.

Technique & Palette:
  Helene Schjerfbeck style — 133rd distinct mode: schjerfbeck_sparse_portrait_pass.
  Peripheral dissolution blurs background and periphery; tonal flattening
  compresses the face into soft planes of light and shadow; a Nordic cool
  wash bleaches toward chalk-white under diffuse winter light; a thin veil
  lifts the dark tones slightly.

  halation_glow_pass (session 222 improvement) creates a warm luminous bloom
  from the window light landing on her temple and upper brow — not dramatic,
  just the specific quality of winter light that reveals without warming.

  Palette:
    — Chalk-white flesh        (0.88, 0.84, 0.78)  — lit cheek and brow
    — Warm ochre mid-tone      (0.72, 0.65, 0.56)  — skin plane, central face
    — Grey-brown shadow        (0.48, 0.45, 0.43)  — shadow under jaw, eye socket
    — Deep charcoal            (0.30, 0.28, 0.26)  — iris, lip line, hair accent
    — Warm bone highlight      (0.80, 0.75, 0.68)  — brow highlight, cheekbone
    — Cool blue-grey           (0.62, 0.62, 0.65)  — dissolved periphery
    — Raw umber structural     (0.52, 0.46, 0.38)  — structural shadow line

Mood & Intent:
  This painting is about the quality of light at the end of a life — not
  dramatic, not sorrowful, simply present. The face reduced to its essential
  planes is not a portrait of weakness; it is the image of something that has
  been distilled. The halation around her lit temple suggests not warmth but
  the particular cold luminosity of Scandinavian winter: a light that reveals
  without flattering, that shows a face as it is, as it always will have been.
  Walk away with the feeling of having stood in a very quiet room.
"""

import numpy as np
from PIL import Image, ImageFilter

from stroke_engine import Painter
from art_catalog import get_style

W, H = 760, 1020   # portrait — close-cropped head


def _blend(base: np.ndarray, color: tuple, alpha_hw: np.ndarray) -> np.ndarray:
    """Alpha-blend color (RGB float) into base (H, W, 3) using alpha (H, W)."""
    c = np.array(color, dtype=np.float32)
    a = np.clip(alpha_hw, 0.0, 1.0)[:, :, np.newaxis]
    return base + (c - base) * a


def build_reference(w: int, h: int) -> Image.Image:
    """
    Synthetic reference: elderly woman in close three-quarter portrait.
    Pale diffuse winter light from upper right; dissolved periphery.
    """
    arr = np.zeros((h, w, 3), dtype=np.float32)

    yf = np.linspace(0.0, 1.0, h)
    xf = np.linspace(0.0, 1.0, w)
    yy = yf[:, np.newaxis]
    xx = xf[np.newaxis, :]

    rng = np.random.RandomState(222)

    # ── Background: pale grey-white linen ────────────────────────────────────
    arr[:, :, 0] = 0.82
    arr[:, :, 1] = 0.80
    arr[:, :, 2] = 0.77

    # Subtle tonal variation — uneven diffuse light
    for _ in range(5):
        cx = rng.uniform(0.0, 1.0)
        cy = rng.uniform(0.0, 0.80)
        r  = rng.uniform(0.25, 0.60)
        val = rng.uniform(-0.03, 0.04)
        dist = np.sqrt(((xx - cx) / (r * 0.8))**2 + ((yy - cy) / r)**2)
        pa = np.clip(1.0 - dist, 0.0, 1.0) ** 1.5 * val
        arr += pa[:, :, np.newaxis] * np.array([1.0, 1.0, 1.0])

    # Window light: cold, diffuse, from upper right
    wl_dist = np.sqrt(((xx - 1.05) / 0.55)**2 + ((yy - 0.0) / 0.55)**2)
    wl_a = np.clip(1.0 - wl_dist, 0.0, 1.0) ** 0.65 * 0.14
    arr = _blend(arr, (0.92, 0.92, 0.94), wl_a)

    # Fine grain noise
    noise = rng.uniform(-0.010, 0.010, (h, w)).astype(np.float32)
    arr[:, :, 0] += noise
    arr[:, :, 1] += noise * 0.9
    arr[:, :, 2] += noise * 0.85

    # ── Dark garment: suggestion at very bottom of frame ─────────────────────
    garment_a = np.clip((yy - 0.84) / 0.07, 0.0, 1.0) ** 1.2
    garment_a = np.broadcast_to(garment_a, (h, w)).copy()
    arr = _blend(arr, (0.20, 0.19, 0.18), garment_a * 0.92)

    # Collar hint — slightly lighter band at neckline
    collar_a = np.clip(1.0 - np.abs(yy - 0.855) / 0.014, 0.0, 1.0) * \
               np.clip(1.0 - np.abs(xx - 0.50) / 0.060, 0.0, 1.0) * 0.30
    collar_a = np.broadcast_to(collar_a, (h, w)).copy()
    arr = _blend(arr, (0.68, 0.64, 0.60), collar_a)

    # ── Neck ─────────────────────────────────────────────────────────────────
    neck_cx, neck_cy = 0.50, 0.810
    neck_rx, neck_ry = 0.042, 0.040
    neck_dist = np.sqrt(((xx - neck_cx) / neck_rx)**2 + ((yy - neck_cy) / neck_ry)**2)
    neck_a = np.clip(1.0 - neck_dist, 0.0, 1.0) ** 0.80 * 0.88
    arr = _blend(arr, (0.80, 0.74, 0.66), neck_a)

    # Neck shadow — right side away from window
    neck_shd_dist = np.sqrt(((xx - 0.42) / 0.022)**2 + ((yy - 0.815) / 0.038)**2)
    neck_shd_a = np.clip(1.0 - neck_shd_dist, 0.0, 1.0) ** 1.2 * 0.45
    arr = _blend(arr, (0.52, 0.48, 0.44), neck_shd_a)

    # ── Head: oval, tilted left and slightly down ─────────────────────────────
    head_cx, head_cy = 0.48, 0.390
    head_rx, head_ry = 0.175, 0.360
    head_dist = np.sqrt(((xx - head_cx) / head_rx)**2 + ((yy - head_cy) / head_ry)**2)
    head_a = np.clip(1.0 - head_dist, 0.0, 1.0) ** 0.58
    arr = _blend(arr, (0.78, 0.72, 0.64), head_a * 0.90)

    # ── Window light on face: upper right temple and brow ────────────────────
    lit_dist = np.sqrt(((xx - 0.62) / 0.090)**2 + ((yy - 0.220) / 0.095)**2)
    lit_a = np.clip(1.0 - lit_dist, 0.0, 1.0) ** 1.2 * 0.55
    arr = _blend(arr, (0.87, 0.84, 0.80), lit_a)

    # Left cheek — deeper shadow, face turned away
    lche_dist = np.sqrt(((xx - 0.36) / 0.060)**2 + ((yy - 0.420) / 0.080)**2)
    lche_a = np.clip(1.0 - lche_dist, 0.0, 1.0) ** 1.3 * 0.52
    arr = _blend(arr, (0.55, 0.50, 0.45), lche_a)

    # Right cheekbone — lit, prominent
    rche_dist = np.sqrt(((xx - 0.60) / 0.055)**2 + ((yy - 0.390) / 0.060)**2)
    rche_a = np.clip(1.0 - rche_dist, 0.0, 1.0) ** 1.4 * 0.48
    arr = _blend(arr, (0.84, 0.80, 0.74), rche_a)

    # ── Forehead ─────────────────────────────────────────────────────────────
    forehead_dist = np.sqrt(((xx - 0.50) / 0.120)**2 + ((yy - 0.185) / 0.065)**2)
    forehead_a = np.clip(1.0 - forehead_dist, 0.0, 1.0) ** 0.85 * 0.65
    arr = _blend(arr, (0.82, 0.77, 0.70), forehead_a)

    # Forehead lines — barely visible
    for line_y in [0.215, 0.232, 0.250]:
        hl_a = np.clip(1.0 - np.abs(yy - line_y) / 0.004, 0.0, 1.0) * \
               np.clip(1.0 - head_dist * 0.7, 0.0, 1.0) * 0.10
        hl_a = np.broadcast_to(hl_a, (h, w)).copy()
        arr = _blend(arr, (0.60, 0.56, 0.51), hl_a)

    # ── Hair: white, sparse, pulled back ─────────────────────────────────────
    # Main hair mass — very top of head
    hair_dist = np.sqrt(((xx - 0.49) / 0.168)**2 + ((yy - 0.072) / 0.120)**2)
    hair_a = np.clip(1.0 - hair_dist, 0.0, 1.0) ** 0.62 * (yy < 0.185)
    hair_a = np.broadcast_to(hair_a, (h, w)).copy()
    arr = _blend(arr, (0.84, 0.83, 0.82), hair_a * 0.78)

    # Stray strands at right temple
    strand_dist = np.sqrt(((xx - 0.64) / 0.018)**2 + ((yy - 0.235) / 0.055)**2)
    strand_a = np.clip(1.0 - strand_dist, 0.0, 1.0) ** 1.4 * 0.35
    arr = _blend(arr, (0.78, 0.76, 0.75), strand_a)

    # Left temple hair edge
    lhair_dist = np.sqrt(((xx - 0.32) / 0.025)**2 + ((yy - 0.250) / 0.040)**2)
    lhair_a = np.clip(1.0 - lhair_dist, 0.0, 1.0) ** 1.1 * 0.40
    arr = _blend(arr, (0.65, 0.63, 0.62), lhair_a)

    # ── Eyes: closed or cast far down ────────────────────────────────────────
    # Left eye (viewer's left — face turned left)
    for ex, ey, scale_x in [(0.420, 0.348, 0.90), (0.570, 0.328, 0.82)]:
        # Upper lid — prominent, closed
        lid_dist = np.sqrt(((xx - ex) / (0.038 * scale_x))**2 + ((yy - ey) / 0.010)**2)
        lid_a = np.clip(1.0 - lid_dist, 0.0, 1.0) ** 0.85 * 0.65
        arr = _blend(arr, (0.52, 0.47, 0.42), lid_a)

        # Eye socket shadow — deep, age-deepened
        sock_dist = np.sqrt(((xx - ex) / (0.042 * scale_x))**2 + ((yy - ey) / 0.022)**2)
        sock_a = np.clip(1.0 - sock_dist, 0.0, 1.0) ** 0.80 * 0.50
        arr = _blend(arr, (0.48, 0.42, 0.38), sock_a)

        # Thin dark lash line
        lash_a = np.clip(1.0 - np.abs(yy - ey) / 0.006, 0.0, 1.0) * \
                 np.clip(1.0 - np.abs(xx - ex) / (0.036 * scale_x), 0.0, 1.0) * 0.45
        lash_a = np.broadcast_to(lash_a, (h, w)).copy()
        arr = _blend(arr, (0.30, 0.27, 0.25), lash_a)

    # ── Nose: delicate, slightly turned left ─────────────────────────────────
    nose_dist = np.sqrt(((xx - 0.470) / 0.022)**2 + ((yy - 0.452) / 0.068)**2)
    nose_a = np.clip(1.0 - nose_dist, 0.0, 1.0) ** 0.90 * 0.52
    arr = _blend(arr, (0.72, 0.66, 0.58), nose_a)

    # Nose shadow — right side, window light from right
    nshd_dist = np.sqrt(((xx - 0.448) / 0.014)**2 + ((yy - 0.462) / 0.030)**2)
    nshd_a = np.clip(1.0 - nshd_dist, 0.0, 1.0) ** 1.3 * 0.42
    arr = _blend(arr, (0.50, 0.45, 0.40), nshd_a)

    # Nose highlight — right tip
    nhi_dist = np.sqrt(((xx - 0.492) / 0.012)**2 + ((yy - 0.498) / 0.010)**2)
    nhi_a = np.clip(1.0 - nhi_dist, 0.0, 1.0) ** 1.8 * 0.40
    arr = _blend(arr, (0.86, 0.82, 0.76), nhi_a)

    # ── Mouth: barely a thin line ────────────────────────────────────────────
    mouth_dist = np.sqrt(((xx - 0.462) / 0.038)**2 + ((yy - 0.548) / 0.010)**2)
    mouth_a = np.clip(1.0 - mouth_dist, 0.0, 1.0) ** 1.0 * 0.48
    arr = _blend(arr, (0.52, 0.47, 0.42), mouth_a)

    # Lower lip — slight volume
    lip_dist = np.sqrt(((xx - 0.460) / 0.030)**2 + ((yy - 0.562) / 0.012)**2)
    lip_a = np.clip(1.0 - lip_dist, 0.0, 1.0) ** 1.2 * 0.30
    arr = _blend(arr, (0.68, 0.61, 0.54), lip_a)

    # ── Jaw and chin: pointed, angular ───────────────────────────────────────
    chin_dist = np.sqrt(((xx - 0.458) / 0.048)**2 + ((yy - 0.640) / 0.040)**2)
    chin_a = np.clip(1.0 - chin_dist, 0.0, 1.0) ** 1.0 * 0.55
    arr = _blend(arr, (0.72, 0.66, 0.58), chin_a)

    jaw_shd_dist = np.sqrt(((xx - 0.385) / 0.055)**2 + ((yy - 0.600) / 0.055)**2)
    jaw_shd_a = np.clip(1.0 - jaw_shd_dist, 0.0, 1.0) ** 1.2 * 0.40
    arr = _blend(arr, (0.46, 0.42, 0.38), jaw_shd_a)

    # Chin highlight — window light grazes underside of chin
    chi_hi_dist = np.sqrt(((xx - 0.490) / 0.028)**2 + ((yy - 0.668) / 0.012)**2)
    chi_hi_a = np.clip(1.0 - chi_hi_dist, 0.0, 1.0) ** 1.6 * 0.32
    arr = _blend(arr, (0.82, 0.78, 0.72), chi_hi_a)

    arr = np.clip(arr, 0.0, 1.0)
    arr_u8 = (arr * 255).astype(np.uint8)
    img = Image.fromarray(arr_u8, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(0.7))
    return img


def paint(output_path: str = "s222_last_light.png") -> str:
    """
    Paint 'The Last Light of Winter'.
    Helene Schjerfbeck style: 133rd mode — schjerfbeck_sparse_portrait_pass.
    Session 222 improvement: halation_glow_pass.
    """
    print("=" * 64)
    print("  Session 222 — 'The Last Light of Winter'")
    print("  Elderly woman — close portrait, diffuse winter light")
    print("  Technique: Helene Schjerfbeck Finnish Modernism")
    print("  133rd mode: schjerfbeck_sparse_portrait_pass")
    print("  + halation_glow_pass (session 222 improvement)")
    print("=" * 64)

    ref_img = build_reference(W, H)
    print(f"  Reference built  ({W}x{H})")

    schjerfbeck = get_style("helene_schjerfbeck")
    p = Painter(W, H)

    # Pale warm linen ground — Schjerfbeck's bleached Nordic base
    print("  [1] Tone ground — pale warm linen ...")
    p.tone_ground(schjerfbeck.ground_color, texture_strength=0.03)

    # Underpainting — sparse tonal masses, no detail
    print("  [2] Underpainting — sparse masses ...")
    p.underpainting(ref_img, stroke_size=55, n_strokes=1100)

    # Block in — head and background plane
    print("  [3] Block in — form and ground ...")
    p.block_in(ref_img, stroke_size=24, n_strokes=1800)

    # Build form — face planes, hair, collar
    print("  [4] Build form — face planes ...")
    p.build_form(ref_img, stroke_size=9, n_strokes=1900)

    # Place lights — window catches on brow, cheekbone, chin
    print("  [5] Place lights — cold window catches ...")
    p.place_lights(ref_img, stroke_size=3, n_strokes=220)

    # ── Schjerfbeck signature pass — Sparse Portrait ──────────────────────────
    print("  [6] schjerfbeck_sparse_portrait_pass (133rd mode) ...")
    p.schjerfbeck_sparse_portrait_pass(
        dissolution_radius=0.42,
        dissolution_strength=0.72,
        flatten_sigma=3.5,
        flatten_strength=0.48,
        cool_shift=0.14,
        veil_opacity=0.07,
        opacity=0.80,
    )

    # ── Session 222 artistic improvement — Halation Glow ─────────────────────
    print("  [7] halation_glow_pass (session 222 improvement) ...")
    p.halation_glow_pass(
        threshold=0.72,
        bloom_sigma=0.035,
        bloom_intensity=0.28,
        glow_warm_r=0.98,
        glow_warm_g=0.94,
        glow_warm_b=0.82,
        opacity=0.55,
    )

    # Edge definition — restrained; Schjerfbeck's edges are selective
    print("  [8] Edge definition ...")
    p.edge_definition_pass(strength=0.18)

    # Meso detail — surface texture of aged skin, hair texture
    print("  [9] Meso detail ...")
    p.meso_detail_pass(opacity=0.12)

    # Canvas grain — linen breathes through thin paint
    print("  [10] Canvas grain ...")
    p.canvas_grain_pass()

    # Finish — minimal vignette anchors the dissolution
    print("  [11] Finish ...")
    p.finish(vignette=0.12, crackle=False)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    out = paint()
    print(f"\n  Done: {out}")
