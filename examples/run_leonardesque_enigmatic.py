"""
run_leonardesque_enigmatic.py — Half-length portrait after Leonardo's method.

Composition
-----------
  Woman seated slightly right of centre. Body in three-quarter pose (45° right),
  head nearly full-face to the viewer. Hands folded in lap, right over left,
  lower-centre of the frame.

The figure
  Face    : Oval, high smooth forehead, barely-perceptible eyebrows. Dark
            heavy-lidded eyes gazing directly at the viewer. Straight, refined
            nose. Closed lips with corners turned very slightly upward — the
            ambiguity between smile and neutral is the essential quality.
  Skin    : Seamless warm ivory. Light from upper left. No visible brushwork.
  Hair    : Dark brown, centre-parted, soft waves, covered by a dark
            semi-transparent veil draped over the crown.
  Dress   : Dark forest-green / blue-black. Thin amber trim at the neckline.
            Semi-transparent gauze wrap over shoulder and chest.

Background
  Imaginary geological wilderness: winding road on the left snaking into
  distance; rocky craggy formations; sparse vegetation; a river or body of
  water in the middle distance. Left horizon sits slightly higher than right
  (uncanny, subtly disorienting quality). Distant forms dissolve into cool
  blue-grey atmospheric haze — sfumato recession.

Technique
  Sfumato throughout — no hard outlines; edges melt into atmosphere.
  Warm ochres / raw umbers / ivory / soft flesh for the figure.
  Cool grey-blues / muted greens / dusty lavenders for the background.
  Glazing logic: thin transparent layers build luminous depth.
  Upper-left diffused light; gentle, imperceptible tonal transitions.

Pass sequence (in order)
  1.  tone_ground             — Leonardo's warm ochre ground
  2.  underpainting           — dead-colour value structure
  3.  block_in × 3            — broad → medium → tight value patches
  4.  build_form × 2          — mid-tone / dark-half modelling
  5.  atmospheric_depth_pass  — aerial perspective on landscape BEFORE figure
                                detail is refined
  6.  place_lights            — specular light placements
  7.  focused_pass            — face detail concentration (small strokes,
                                following the curved surface of the skull)
  8.  warm_cool_boundary_pass — tonal boundary vibration (warm light / cool
                                shadow edge vitality)
  9.  subsurface_glow_pass    — translucent skin: haemoglobin scattering at
                                the silhouette edge
  10. sfumato_veil_pass       — 9 warm amber veils; chroma_dampen replicates
                                the grey-amber edge quality in X-ray studies
                                of Leonardo's Mona Lisa
  11. glazed_panel_pass       — 10 transparent glaze layers; warm shadows,
                                cool highlights — Flemish luminous depth
  12. glaze (amber)           — Leonardo's characteristic unifying amber tone
  13. finish                  — vignette + aged crackle varnish
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter


W, H = 780, 1080


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic reference image
# ─────────────────────────────────────────────────────────────────────────────

def make_reference() -> Image.Image:
    """
    Build a richly-coloured synthetic reference for the stroke engine.

    The reference establishes the colour structure the passes paint toward.
    Values are saturated so the engine deposits strong, visible paint — the
    subsequent sfumato and glazing passes will unify and soften everything.

    Coordinate system: (0, 0) = top-left.  Y increases downward.
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # ── Sky: medium blue-grey, slightly warmer near the horizon ──────────────
    sky_top = np.array([0.52, 0.58, 0.70])
    sky_hor = np.array([0.64, 0.67, 0.72])
    for y in range(H):
        t = min(1.0, y / (H * 0.55))
        ref[y] = sky_top * (1 - t) + sky_hor * t

    # ── Distant haze band near the horizon — pale, cool, near-white ──────────
    # Sits at ~35–45% down the canvas. Left side slightly higher than right
    # to create the subtle uncanny horizon mismatch.
    for x in range(W):
        hor_l = int(H * 0.38)                      # left horizon (higher)
        hor_r = int(H * 0.42)                      # right horizon (lower)
        hor_y = hor_l + int((hor_r - hor_l) * x / W)
        haze  = np.array([0.76, 0.80, 0.86])
        for y in range(max(0, hor_y - 28), min(H, hor_y + 18)):
            band_t = 1.0 - abs(y - hor_y) / 28.0
            band_t = max(0.0, band_t) ** 1.4
            ref[y, x] = ref[y, x] * (1 - band_t * 0.55) + haze * band_t * 0.55

    # ── Rocky mid-distance terrain, olive / grey-green ───────────────────────
    terrain = np.array([0.30, 0.35, 0.24])
    rock    = np.array([0.42, 0.40, 0.32])
    for x in range(W):
        hor_l = int(H * 0.41)
        hor_r = int(H * 0.46)
        hor_y = hor_l + int((hor_r - hor_l) * x / W)
        for y in range(hor_y, min(H, hor_y + int(H * 0.14))):
            t = (y - hor_y) / (H * 0.14)
            ref[y, x] = terrain * (1 - t) + rock * t

    # ── River / water: cool steel-blue band in the left middle distance ───────
    river_y  = int(H * 0.46)
    river_hw = int(H * 0.020)
    river_cx = int(W * 0.33)
    river_w  = int(W * 0.24)
    river_c  = np.array([0.38, 0.46, 0.60])
    for y in range(river_y - river_hw, river_y + river_hw):
        if 0 <= y < H:
            for x in range(max(0, river_cx - river_w), min(W, river_cx + river_w)):
                et = max(0.0, 1.0 - abs(y - river_y) / river_hw)
                ref[y, x] = ref[y, x] * (1 - et * 0.62) + river_c * et * 0.62

    # ── Winding path / road on the left side, snaking into distance ──────────
    # Modelled as a sinusoidal curve that narrows toward the horizon.
    path_c = np.array([0.55, 0.50, 0.38])
    for frac in range(0, W // 2):
        x = frac
        # Path centre follows a gentle curve: starts centre-left, drifts right
        pcx = int(W * 0.14 + (frac / (W * 0.48)) ** 1.4 * W * 0.11
                  + math.sin(frac / (W * 0.12)) * W * 0.025)
        # Path width narrows with distance (toward horizon)
        pw = max(3, int(W * 0.038 * (1.0 - frac / (W * 0.50)) + 4))
        mid_y_l = int(H * 0.43)
        mid_y_r = int(H * 0.46)
        for y in range(mid_y_l - int(H * 0.06), mid_y_l + int(H * 0.04)):
            if 0 <= y < H:
                dist = abs(x - pcx)
                if dist <= pw and 0 <= x < W:
                    pt = max(0.0, 1.0 - dist / pw)
                    ref[y, x] = ref[y, x] * (1 - pt * 0.50) + path_c * pt * 0.50

    # ── Foreground ground: warm dark earth, cooling toward mid-ground ─────────
    fg_start = int(H * 0.80)
    fg_c     = np.array([0.24, 0.20, 0.14])
    for y in range(fg_start, H):
        t = (y - fg_start) / (H - fg_start)
        ref[y] = ref[y] * (1 - t * 0.8) + fg_c * t * 0.8

    # ── Parapet / ledge: very subtle warm dark shape at the very bottom ───────
    parapet_top = int(H * 0.89)
    parapet_c   = np.array([0.18, 0.15, 0.10])
    for y in range(parapet_top, H):
        t = (y - parapet_top) / (H - parapet_top)
        ref[y] = ref[y] * (1 - t * 0.65) + parapet_c * t * 0.65

    # ── Figure torso: dark forest-green / blue-black dress ───────────────────
    fig_cx      = int(W * 0.545)     # figure centre, slightly right of canvas centre
    torso_w     = int(W * 0.255)
    torso_top   = int(H * 0.340)
    torso_btm   = H - 20
    dress_lit   = np.array([0.08, 0.23, 0.17])   # lit forest-green
    dress_shd   = np.array([0.03, 0.07, 0.13])   # shadowed blue-black
    for y in range(torso_top, torso_btm):
        taper = (y - torso_top) / max(1, torso_btm - torso_top)
        hw = int(torso_w * (0.66 + taper * 0.34))
        for x in range(max(0, fig_cx - hw), min(W, fig_cx + hw)):
            st = max(0.0, (x - fig_cx) / max(hw, 1))
            col = dress_lit * (1 - st * 0.65) + dress_shd * st * 0.65
            ref[y, x] = col

    # ── Gauze wrap: semi-transparent olive overlay on chest / left shoulder ───
    gauze_c = np.array([0.26, 0.35, 0.28])
    for y in range(int(H * 0.360), int(H * 0.510)):
        for x in range(fig_cx - int(torso_w * 0.78), fig_cx + int(torso_w * 0.52)):
            if 0 <= x < W:
                gm = 0.20 * max(0.0, 1.0 - abs(x - fig_cx) / (torso_w * 0.62))
                ref[y, x] = ref[y, x] * (1 - gm) + gauze_c * gm

    # ── Amber neckline trim ───────────────────────────────────────────────────
    neck_y  = int(H * 0.393)
    trim_c  = np.array([0.80, 0.56, 0.18])
    trim_hw = int(torso_w * 0.37)
    for y in range(neck_y - 3, neck_y + 6):
        if 0 <= y < H:
            for x in range(fig_cx - trim_hw, fig_cx + int(torso_w * 0.30)):
                if 0 <= x < W:
                    ref[y, x] = trim_c

    # ── Skin palette ─────────────────────────────────────────────────────────
    skin_lit = np.array([0.90, 0.76, 0.53])    # warm ivory in light
    skin_shd = np.array([0.48, 0.34, 0.22])    # raw umber in shadow

    # Neck
    neck_cx = fig_cx - int(W * 0.008)
    neck_hw = int(W * 0.053)
    for y in range(int(H * 0.275), int(H * 0.385)):
        for x in range(neck_cx - neck_hw, neck_cx + neck_hw):
            if 0 <= x < W:
                lt = max(0.0, 1.0 - abs(x - (neck_cx - neck_hw // 4))
                         / (neck_hw * 0.80))
                ref[y, x] = skin_shd * (1 - lt) + skin_lit * lt

    # Face — oval, light from upper-left ────────────────────────────────────
    face_cx = fig_cx - int(W * 0.018)
    face_cy = int(H * 0.197)
    face_rx = int(W * 0.124)
    face_ry = int(W * 0.164)

    for y in range(face_cy - face_ry - 10, face_cy + face_ry + 10):
        for x in range(face_cx - face_rx - 10, face_cx + face_rx + 10):
            if 0 <= y < H and 0 <= x < W:
                dx = (x - face_cx) / face_rx
                dy = (y - face_cy) / face_ry
                d  = dx * dx + dy * dy
                if d <= 1.06:
                    # Upper-left light model: normal dot with (-0.68, -0.52)
                    nl  = max(0.0, min(1.0, (-0.68 * dx - 0.52 * dy) * 1.45 + 0.28))
                    col = skin_shd * (1 - nl) + skin_lit * nl
                    # Soft fade at the oval boundary
                    fade = (max(0.0, 1.0 - (d - 0.84) / 0.22)
                            if d > 0.84 else 1.0)
                    ref[y, x] = ref[y, x] * (1 - fade) + col * fade

    # Hair: dark warm brown, centre-parted, waves on either side ─────────────
    hair_lit = np.array([0.22, 0.13, 0.06])
    hair_shd = np.array([0.06, 0.04, 0.01])
    hair_spread_x = int(W * 0.072)
    hair_spread_y = int(W * 0.024)
    for y in range(face_cy - face_ry - 6, face_cy + int(face_ry * 0.62)):
        for x in range(face_cx - face_rx - hair_spread_x,
                       face_cx + face_rx + int(W * 0.055)):
            if 0 <= y < H and 0 <= x < W:
                fdx    = (x - face_cx) / face_rx
                fdy    = (y - face_cy) / face_ry
                face_d = fdx * fdx + fdy * fdy
                outer_d = ((x - face_cx) / (face_rx + hair_spread_x)) ** 2 + \
                          ((y - face_cy) / (face_ry + hair_spread_y)) ** 2
                if outer_d <= 1.06 and face_d >= 0.86:
                    ht  = max(0.0, (x - face_cx) / (face_rx + int(W * 0.01)))
                    col = hair_lit * (1 - ht * 0.50) + hair_shd * ht * 0.50
                    ref[y, x] = col

    # Veil: dark semi-transparent over crown / temples ────────────────────────
    veil_c = np.array([0.07, 0.05, 0.08])
    for y in range(face_cy - face_ry - 4, face_cy + int(face_ry * 0.42)):
        for x in range(face_cx - face_rx - int(W * 0.030),
                       face_cx + face_rx + int(W * 0.018)):
            if 0 <= y < H and 0 <= x < W:
                fdx = (x - face_cx) / face_rx
                fdy = (y - face_cy) / face_ry
                if fdx * fdx + fdy * fdy >= 0.88:
                    ref[y, x] = veil_c

    # Eyes: dark, heavy-lidded ─────────────────────────────────────────────────
    eye_sep = int(face_rx * 0.46)
    eye_y   = face_cy - int(face_ry * 0.065)
    eye_rx  = int(face_rx * 0.215)
    eye_ry  = int(face_ry * 0.108)
    iris_c  = np.array([0.10, 0.08, 0.06])
    sclera  = np.array([0.82, 0.75, 0.62])     # warm ivory sclera

    for ex in [face_cx - eye_sep, face_cx + eye_sep]:
        for dy_e in range(-eye_ry - 2, eye_ry + 3):
            for dx_e in range(-eye_rx - 2, eye_rx + 3):
                ey = eye_y + dy_e
                ex2 = ex + dx_e
                if 0 <= ey < H and 0 <= ex2 < W:
                    de_full  = (dx_e / eye_rx)  ** 2 + (dy_e / eye_ry)  ** 2
                    de_iris  = (dx_e / (eye_rx * 0.52)) ** 2 + \
                               (dy_e / (eye_ry * 0.55)) ** 2
                    if de_full <= 1.0:
                        if de_iris <= 1.0:
                            fade_e = max(0.0, 1.0 - de_iris * 0.4)
                            ref[ey, ex2] = ref[ey, ex2] * (1 - fade_e) \
                                           + iris_c * fade_e
                        else:
                            fade_e = max(0.0, 1.0 - (de_full - 0.55) / 0.45)
                            ref[ey, ex2] = ref[ey, ex2] * (1 - fade_e * 0.45) \
                                           + sclera * fade_e * 0.45

    # Lips: closed, warm rose; corners turned very slightly upward ────────────
    lip_cx = face_cx + int(face_rx * 0.030)
    lip_cy = face_cy + int(face_ry * 0.470)
    lip_c  = np.array([0.66, 0.38, 0.27])

    for dy_l in range(-int(face_ry * 0.055), int(face_ry * 0.055) + 1):
        for dx_l in range(-int(face_rx * 0.28), int(face_rx * 0.28) + 1):
            lx = lip_cx + dx_l
            ly = lip_cy + dy_l
            if 0 <= ly < H and 0 <= lx < W:
                bow = abs(dx_l) / (face_rx * 0.26)
                # Very subtle upward curve at the outer corners — the
                # ambiguous quality: neither smile nor neutral.
                corner_lift = 0.015 * bow * bow
                lry = face_ry * (0.048 + 0.016 * bow * bow)
                dl  = (dx_l / (face_rx * 0.268)) ** 2 + \
                      ((dy_l + corner_lift * face_ry) / lry) ** 2
                if dl <= 1.0:
                    fade_l = max(0.0, 1.0 - dl * 0.55)
                    ref[ly, lx] = ref[ly, lx] * (1 - fade_l) + lip_c * fade_l

    # Hands: folded in lower centre; right draped over left ───────────────────
    hand_cx = fig_cx - int(W * 0.042)
    hand_cy = int(H * 0.735)
    hrx     = int(face_rx * 0.70)
    hry     = int(face_ry * 0.37)
    for dy_h in range(-hry, hry + 1):
        for dx_h in range(-hrx, hrx + 1):
            hx = hand_cx + dx_h
            hy = hand_cy + dy_h
            if 0 <= hy < H and 0 <= hx < W:
                dh = (dx_h / hrx) ** 2 + (dy_h / hry) ** 2
                if dh <= 1.0:
                    nl  = max(0.0, min(1.0, 0.54 - dx_h / (hrx * 1.75)))
                    col = skin_shd * (1 - nl) + skin_lit * nl
                    fd  = (max(0.0, 1.0 - (dh - 0.76) / 0.24)
                           if dh > 0.76 else 1.0)
                    ref[hy, hx] = ref[hy, hx] * (1 - fd) + col * fd

    # Apply a gentle blur to smooth colour transitions in the reference —
    # the stroke engine will impose its own painted texture on top.
    img = Image.fromarray((np.clip(ref, 0, 1) * 255).astype(np.uint8), "RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=2.6))
    return img


def _make_face_ellipse_mask(h: int, w: int) -> np.ndarray:
    """
    Float32 (H, W) mask for the face region: 1.0 inside the face ellipse,
    0.0 outside, with a soft cosine fall-off at the boundary.

    Used by focused_pass() to concentrate fine-detail strokes on the face.
    """
    fig_cx  = int(w * 0.545)
    face_cx = fig_cx - int(w * 0.018)
    face_cy = int(h * 0.197)
    face_rx = int(w * 0.124) * 2     # expand the region slightly beyond
    face_ry = int(w * 0.164) * 2     # the face oval to include the neck

    mask = np.zeros((h, w), dtype=np.float32)
    ys, xs = np.ogrid[:h, :w]
    dx = (xs - face_cx) / face_rx
    dy = (ys - face_cy) / face_ry
    d  = dx ** 2 + dy ** 2
    # Smooth fall-off: 1.0 for d ≤ 0.70, cosine ramp to 0 at d = 1.0
    core   = d <= 0.70
    ramp   = (d > 0.70) & (d <= 1.0)
    mask[core]  = 1.0
    t = (d[ramp] - 0.70) / 0.30
    mask[ramp]  = 0.5 * (1.0 + np.cos(np.pi * t))
    return mask


# ─────────────────────────────────────────────────────────────────────────────
# Painting orchestration
# ─────────────────────────────────────────────────────────────────────────────

def paint(out_path: str = None) -> str:
    if out_path is None:
        out_path = os.path.join(os.path.dirname(__file__), '..',
                                'leonardesque_enigmatic.png')

    print("Building synthetic reference…")
    ref = make_reference()
    ref_path = os.path.join(os.path.dirname(__file__), '..', 'leonardesque_ref.png')
    ref.save(ref_path)
    print(f"  Reference saved: {ref_path}")

    W_r, H_r = ref.size
    print(f"  Canvas: {W_r}×{H_r}")

    p = Painter(W_r, H_r)

    # ── 1. Leonardo's warm ochre ground ───────────────────────────────────────
    # A yellow-ochre / raw umber tone warms the lights from below and gives the
    # shadows their amber quality even before any strokes are placed.
    print("\nStep 1 — Toning ground (warm ochre)…")
    p.tone_ground((0.54, 0.45, 0.26), texture_strength=0.055)

    # ── 2. Underpainting — dead-colour value structure ────────────────────────
    # Loose, desaturated, value-only. Leonardo's *verdaccio* equivalent.
    print("Step 2 — Underpainting (verdaccio value structure)…")
    p.underpainting(ref, stroke_size=56, n_strokes=260)

    # ── 3. Block-in: broad → medium → tight ──────────────────────────────────
    print("Step 3 — Block in (broad)…")
    p.block_in(ref, stroke_size=40, n_strokes=480)

    print("Step 3 — Block in (medium)…")
    p.block_in(ref, stroke_size=24, n_strokes=650)

    print("Step 3 — Block in (tight)…")
    p.block_in(ref, stroke_size=14, n_strokes=750)

    # Save the raw block-in so the painting's architectural skeleton is visible
    # if the user wants to inspect intermediate stages.
    base_path = os.path.join(os.path.dirname(__file__), '..', 'leonardesque_base.png')
    p.save(base_path)
    print(f"  Base block-in saved: {base_path}")

    # ── 4. Build form ─────────────────────────────────────────────────────────
    print("Step 4 — Build form (primary modelling)…")
    p.build_form(ref, stroke_size=9, n_strokes=900)

    print("Step 4 — Build form (fine)…")
    p.build_form(ref, stroke_size=5, n_strokes=650)

    # ── 5. Atmospheric depth (aerial perspective) ─────────────────────────────
    # Applied before face detail is refined so the background recession is
    # established first and the figure reads against it naturally.
    # Cool blue-grey haze: matches the cool grey-blue of the distant landscape.
    print("Step 5 — Atmospheric depth pass (sfumato aerial perspective)…")
    p.atmospheric_depth_pass(
        haze_color      = (0.72, 0.77, 0.86),   # cool dusty blue-grey
        desaturation    = 0.68,
        lightening      = 0.52,
        depth_gamma     = 1.8,                   # effect concentrates near horizon
        background_only = True,                  # landscape only; leave figure
    )

    # ── 6. Place lights ───────────────────────────────────────────────────────
    print("Step 6 — Place lights (specular highlights)…")
    p.place_lights(ref, stroke_size=5, n_strokes=580)

    # ── 7. Focused pass — face detail ─────────────────────────────────────────
    # Concentrates fine strokes on the face region. stroke_size=4 follows the
    # micro-form of the cheekbones, orbital rims, nose, and lip boundary.
    print("Step 7 — Focused pass (face detail)…")
    face_mask = _make_face_ellipse_mask(H_r, W_r)
    p.focused_pass(
        ref,
        region_mask = face_mask,
        stroke_size = 4,
        n_strokes   = 800,
        opacity     = 0.78,
        wet_blend   = 0.08,     # low wet-blend on face: no dragged marks
        jitter_amt  = 0.018,    # very low colour jitter: skin is unified
        curvature   = 0.05,
    )

    # ── 8. Warm-cool boundary vibration ──────────────────────────────────────
    # Micro-pushes warm/cool tones at every colour boundary — gives the
    # face-to-background edge the "inhabited" quality of hand-painted transitions.
    print("Step 8 — Warm-cool boundary pass…")
    p.warm_cool_boundary_pass(
        strength    = 0.12,
        edge_thresh = 0.07,
        blur_sigma  = 1.6,
    )

    # ── 9. Subsurface scattering glow ────────────────────────────────────────
    # Warm vermilion-orange at the silhouette — haemoglobin scattering through
    # the thin skin at the figure edge. Applied before sfumato so the glow is
    # unified under the sfumato veil layers.
    print("Step 9 — Subsurface glow (translucent skin edge)…")
    p.subsurface_glow_pass(
        ref,
        glow_color    = (0.88, 0.40, 0.22),     # warm vermilion-orange
        glow_strength = 0.14,
        blur_sigma    = 9.0,
        edge_falloff  = 0.60,
    )

    # ── 10. Sfumato veil pass ─────────────────────────────────────────────────
    # The defining technique. Nine warm amber veils; chroma_dampen=0.24 gives
    # the subtle grey-amber edge quality found in X-ray studies of the Mona Lisa
    # (particularly visible at the corners of the mouth and the jaw line).
    # edge_only=True ensures the figure interior remains clear while only the
    # transitional boundary zones acquire the smoky atmospheric quality.
    print("Step 10 — Sfumato veil pass (9 veils, chroma_dampen=0.24)…")
    p.sfumato_veil_pass(
        ref,
        n_veils       = 9,
        blur_radius   = 10.0,
        warmth        = 0.30,
        veil_opacity  = 0.048,
        edge_only     = True,
        chroma_dampen = 0.24,
    )

    # ── 11. Glazed panel pass ─────────────────────────────────────────────────
    # Ten transparent glaze layers simulate the optical depth of an oil-on-panel
    # painting built on a chalk-white gesso ground. Shadows accumulate warm
    # amber-umber; highlights retain cool panel brightness.
    print("Step 11 — Glazed panel pass (10 transparent layers)…")
    p.glazed_panel_pass(
        ref,
        n_glaze_layers    = 10,
        glaze_opacity     = 0.065,
        shadow_warmth     = 0.30,
        highlight_cool    = 0.14,
        shadow_thresh     = 0.36,
        highlight_thresh  = 0.74,
        panel_bloom       = 0.07,
    )

    # ── 12. Final amber unifying glaze ───────────────────────────────────────
    # Leonardo's characteristic varnish tone — a thin warm amber coat that
    # ties all values together and gives the painting its golden interior light.
    print("Step 12 — Final amber glaze…")
    p.glaze((0.62, 0.44, 0.14), opacity=0.055)

    # ── 13. Finish: vignette + aged crackle varnish ───────────────────────────
    # Vignette darkens the corners and draws attention to the face.
    # Crackle simulates the fine network of aged oil varnish — authenticates
    # the sense that this is a panel painting centuries old.
    print("Step 13 — Finish (vignette + crackle varnish)…")
    p.finish(vignette=0.48, crackle=True)

    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    import sys
    _out = sys.argv[1] if len(sys.argv) > 1 else None
    result = paint(_out)
    print("Done:", result)
