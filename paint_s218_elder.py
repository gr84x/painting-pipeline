"""
paint_s218_elder.py — Original composition: "The Scholar's Study"

Session 218 painting — inspired by Oskar Kokoschka (1886–1980).

IMAGE DESCRIPTION
=================
Subject & Composition:
  An elderly man, viewed from slightly above and to the left at three-quarter
  angle, is seated at a heavy wooden desk in a scholar's study. He leans
  forward over a spread of open manuscripts, hands flat on the desk surface,
  head turned to face the viewer with an expression of sudden attention —
  as though interrupted in deep thought. He is the sole subject; the
  environment crowds and presses around him.

The Figure:
  Age: late sixties, angular face — broad forehead, deep-set dark eyes, heavy
  brow ridge, a wide jaw gone a little slack with age. Grey hair swept back
  from the temples. He wears a dark wool jacket (near-black, slightly greenish
  in the shadows) over a white shirt, collar open. His hands are large and
  prominent on the dark desk — the hands of a man who has spent his life with
  objects and pages. The left hand is flat, the right slightly cupped. Emotional
  state: raw alertness, barely masked irritability at the interruption. There is
  something he was on the verge of understanding.

The Environment:
  A low-ceilinged study lined with books. The background is dominated by the
  dark vertical mass of bookshelves — warm ochre spines punctuating the dark
  umber mass. A narrow vertical window on the left side of the canvas admits
  cold cerulean evening light — a hard rectangle of blue that cuts against the
  warm interior. Upper right corner: a lamp glow, a warm ochre-gold ellipse
  that spills across the top of his head and the nearest desk corner. The desk
  surface is dark mahogany. The wall visible between shelves is warm raw ochre
  plaster. The room feels compressed, the air thick with the smell of paper.

Technique & Palette:
  Oskar Kokoschka Expressionism — 129th distinct mode:
  kokoschka_anxious_portrait_pass. DoG contour darkening with stochastic noise
  modulation creates the heavy, scratchy painted outlines characteristic of
  Kokoschka's early portraits. Warm/cool zone chromatic push — flesh red in
  midtones, blue-green in shadows — establishes the psychological tension.
  Expressive shadow gamma deepens the dark zones to near-black.

  Palette:
    — Warm living flesh (0.72, 0.40, 0.22)   — face, hands, lamp-lit surfaces
    — Blue-green shadow (0.20, 0.40, 0.45)   — shadow zones, cool recesses
    — Dark umber        (0.20, 0.12, 0.06)   — jacket, bookshelves, deep shadow
    — Raw ochre plaster (0.68, 0.54, 0.28)   — background wall, book spines
    — Cadmium red       (0.75, 0.18, 0.12)   — single accent book spine, wattle flash
    — Bone white        (0.90, 0.88, 0.78)   — collar, lamp highlight, page edges
    — Cerulean blue     (0.35, 0.52, 0.68)   — window light, cool cast on left
    — Burnt sienna mid  (0.52, 0.28, 0.14)   — skin shadow transition, desk warmth

Mood & Intent:
  The painting asks what it costs to have lived with the mind. Kokoschka
  believed that the psychological reality of a person — their anxiety, their
  latent violence, their need — could be forced out through a particular kind
  of looking. This man has been looked at until he is temporarily defenseless.
  The warm/cool tension refuses resolution: the lamp warmth and the evening
  window blue exist simultaneously and without compromise. Walk away unsettled
  by the directness of the gaze, and aware that the painter was equally
  exposed in the act of making it.
"""

import numpy as np
from PIL import Image, ImageFilter

from stroke_engine import Painter
from art_catalog import get_style

W, H = 760, 1000   # portrait — seated figure, desk occupies lower third


def _blend(base: np.ndarray, color: tuple, alpha_hw: np.ndarray) -> np.ndarray:
    """Alpha-blend color (RGB float) into base (H, W, 3) using alpha (H, W)."""
    c = np.array(color, dtype=np.float32)
    a = np.clip(alpha_hw, 0.0, 1.0)[:, :, np.newaxis]
    return base + (c - base) * a


def build_scholar_reference(w: int, h: int) -> Image.Image:
    """
    Synthetic reference: elderly scholar at desk in a study.
    Left: cold cerulean window. Right: warm lamp. Figure centered-slightly-right.
    Bookshelves fill background. Heavy dark desk at lower portion.
    """
    arr = np.zeros((h, w, 3), dtype=np.float32)

    yf = np.linspace(0.0, 1.0, h)
    xf = np.linspace(0.0, 1.0, w)
    yy = yf[:, np.newaxis]   # (H, 1)
    xx = xf[np.newaxis, :]   # (1, W)

    rng = np.random.RandomState(218)

    # ── Background: warm ochre-sienna plaster wall ────────────────────────────
    arr[:, :, 0] = 0.52
    arr[:, :, 1] = 0.40
    arr[:, :, 2] = 0.18

    # Large-scale plaster warmth variation
    for _ in range(6):
        cx = rng.uniform(0.1, 0.9)
        cy = rng.uniform(0.0, 0.7)
        r  = rng.uniform(0.15, 0.35)
        warm = rng.uniform(0.04, 0.12)
        dist = np.sqrt((xx - cx)**2 + (yy - cy)**2)
        pa = np.clip(1.0 - dist / r, 0.0, 1.0) ** 1.5 * warm
        arr[:, :, 0] += pa * rng.uniform(0.08, 0.18)
        arr[:, :, 1] += pa * rng.uniform(0.04, 0.10)
        arr[:, :, 2] -= pa * rng.uniform(0.01, 0.05)

    noise = rng.uniform(-0.025, 0.025, (h, w)).astype(np.float32)
    arr[:, :, 0] += noise * 0.8
    arr[:, :, 1] += noise * 0.6
    arr[:, :, 2] += noise * 0.3

    # ── Bookshelves: dark umber mass at top and sides ─────────────────────────
    # Top bookshelf band
    shelf_top_a = np.clip((0.22 - yy) / 0.10, 0.0, 1.0) ** 0.7
    shelf_top_a = np.broadcast_to(shelf_top_a, (h, w)).copy()
    arr = _blend(arr, (0.18, 0.10, 0.05), shelf_top_a * 0.92)

    # Book spines in top shelf — ochre and dark alternating verticals
    for xi in np.arange(0.22, 0.98, 0.055):
        spine_col = (rng.uniform(0.55, 0.78), rng.uniform(0.35, 0.58), rng.uniform(0.10, 0.25))
        spine_a = (np.abs(xx - xi) < 0.018) * np.clip((0.18 - yy) / 0.08, 0.0, 1.0) ** 0.5
        spine_a = np.broadcast_to(spine_a, (h, w)).copy()
        arr = _blend(arr, spine_col, spine_a * 0.75)

    # Right side shelves (partial, x > 0.82)
    right_shelf_a = np.clip((xx - 0.82) / 0.06, 0.0, 1.0) ** 0.6 * np.clip((0.65 - yy) / 0.40, 0.0, 1.0)
    right_shelf_a = np.broadcast_to(right_shelf_a, (h, w)).copy()
    arr = _blend(arr, (0.16, 0.09, 0.04), right_shelf_a * 0.85)

    # ── Window: narrow rectangle left side — cold cerulean blue ───────────────
    win_x0, win_x1 = 0.04, 0.17
    win_y0, win_y1 = 0.06, 0.50
    win_mask = ((xx >= win_x0) & (xx <= win_x1) & (yy >= win_y0) & (yy <= win_y1)).astype(np.float32)
    arr = _blend(arr, (0.52, 0.68, 0.82), win_mask * 0.88)

    # Window frame (dark surround)
    frame_dist = np.minimum(
        np.minimum(np.abs(xx - win_x0), np.abs(xx - win_x1)),
        np.minimum(np.abs(yy - win_y0), np.abs(yy - win_y1))
    )
    frame_a = np.clip(1.0 - frame_dist / 0.012, 0.0, 1.0) * win_mask * 0.0
    # Outer frame dark edge
    frame_border = np.clip(1.0 - (
        np.minimum(np.abs(xx - (win_x0 - 0.01)), np.abs(xx - (win_x1 + 0.01))) +
        np.minimum(np.abs(yy - (win_y0 - 0.01)), np.abs(yy - (win_y1 + 0.01)))
    ) / 0.015, 0.0, 1.0)
    frame_border = np.broadcast_to(frame_border, (h, w)).copy()
    arr = _blend(arr, (0.18, 0.12, 0.06), frame_border * 0.55 * (1.0 - win_mask))

    # Cold blue window spill on left wall and figure left
    spill_a = np.clip((0.22 - xx) / 0.18, 0.0, 1.0) ** 1.5 * np.clip((0.65 - yy) / 0.45, 0.0, 1.0) * 0.32
    spill_a = np.broadcast_to(spill_a, (h, w)).copy()
    arr = _blend(arr, (0.40, 0.58, 0.75), spill_a)

    # ── Lamp glow: upper right warm ellipse ───────────────────────────────────
    lamp_cx, lamp_cy = 0.88, 0.08
    lamp_dist = np.sqrt(((xx - lamp_cx) / 0.14)**2 + ((yy - lamp_cy) / 0.10)**2)
    lamp_body_a = np.clip(1.0 - lamp_dist, 0.0, 1.0) ** 0.6 * 0.85
    arr = _blend(arr, (0.96, 0.88, 0.58), lamp_body_a)

    # Warm lamp light spill onto upper right portion
    spill_r_a = np.clip(1.0 - np.sqrt(((xx - lamp_cx) / 0.45)**2 + ((yy - lamp_cy) / 0.38)**2), 0.0, 1.0) ** 2.0 * 0.28
    spill_r_a = np.broadcast_to(spill_r_a, (h, w)).copy()
    arr = _blend(arr, (0.85, 0.70, 0.40), spill_r_a)

    # ── Desk: heavy dark mahogany horizontal band ──────────────────────────────
    desk_top = 0.70
    desk_bottom = 0.88
    desk_a = np.clip((yy - desk_top) / 0.04, 0.0, 1.0) * np.clip((desk_bottom - yy) / 0.04, 0.0, 1.0)
    desk_a = np.broadcast_to(desk_a, (h, w)).copy() ** 0.5
    arr = _blend(arr, (0.22, 0.13, 0.06), desk_a * 0.90)

    # Desk top edge line — bright reflection from lamp
    desk_edge_a = np.clip(1.0 - np.abs(yy - desk_top) / 0.008, 0.0, 1.0) * np.clip((xx - 0.22) / 0.10, 0.0, 1.0) * 0.60
    desk_edge_a = np.broadcast_to(desk_edge_a, (h, w)).copy()
    arr = _blend(arr, (0.72, 0.58, 0.32), desk_edge_a)

    # Open manuscripts on desk: pale pages lower center
    page_cx, page_cy = 0.52, 0.73
    page_rx, page_ry = 0.22, 0.042
    page_dist = np.sqrt(((xx - page_cx) / page_rx)**2 + ((yy - page_cy) / page_ry)**2)
    page_a = np.clip(1.0 - page_dist, 0.0, 1.0) ** 0.60 * 0.82
    arr = _blend(arr, (0.88, 0.85, 0.74), page_a)

    # Page text lines — faint horizontal strokes
    for line_y in np.arange(0.710, 0.745, 0.007):
        line_a = np.clip(1.0 - np.abs(yy - line_y) / 0.0015, 0.0, 1.0) * page_a * 0.28
        line_a = np.broadcast_to(line_a, (h, w)).copy()
        arr = _blend(arr, (0.38, 0.32, 0.22), line_a)

    # ── Figure: torso — dark wool jacket ──────────────────────────────────────
    torso_cx, torso_cy = 0.50, 0.57
    torso_rx, torso_ry = 0.185, 0.165
    torso_dist = np.sqrt(((xx - torso_cx) / torso_rx)**2 + ((yy - torso_cy) / torso_ry)**2)
    torso_a = np.clip(1.0 - torso_dist, 0.0, 1.0) ** 0.55
    arr = _blend(arr, (0.18, 0.12, 0.07), torso_a * 0.92)

    # Jacket highlight (lamp light on right shoulder)
    shoulder_dist = np.sqrt(((xx - 0.62) / 0.07)**2 + ((yy - 0.42) / 0.09)**2)
    shoulder_a = np.clip(1.0 - shoulder_dist, 0.0, 1.0) ** 1.4 * 0.42
    arr = _blend(arr, (0.35, 0.22, 0.12), shoulder_a)

    # Left shoulder — window blue-cold cast
    l_shoulder_dist = np.sqrt(((xx - 0.38) / 0.07)**2 + ((yy - 0.44) / 0.08)**2)
    l_shoulder_a = np.clip(1.0 - l_shoulder_dist, 0.0, 1.0) ** 1.4 * 0.38
    arr = _blend(arr, (0.18, 0.24, 0.32), l_shoulder_a)

    # ── Collar + shirt: white near neck ───────────────────────────────────────
    collar_cx, collar_cy = 0.50, 0.39
    collar_rx, collar_ry = 0.060, 0.028
    collar_dist = np.sqrt(((xx - collar_cx) / collar_rx)**2 + ((yy - collar_cy) / collar_ry)**2)
    collar_a = np.clip(1.0 - collar_dist, 0.0, 1.0) ** 0.85 * 0.82
    arr = _blend(arr, (0.90, 0.88, 0.80), collar_a)

    # ── Neck ──────────────────────────────────────────────────────────────────
    neck_cx, neck_cy = 0.50, 0.35
    neck_rx, neck_ry = 0.042, 0.058
    neck_dist = np.sqrt(((xx - neck_cx) / neck_rx)**2 + ((yy - neck_cy) / neck_ry)**2)
    neck_a = np.clip(1.0 - neck_dist, 0.0, 1.0) ** 0.80 * 0.88
    arr = _blend(arr, (0.68, 0.38, 0.20), neck_a)

    # ── Head: angular, three-quarter ──────────────────────────────────────────
    head_cx, head_cy = 0.50, 0.22
    head_rx, head_ry = 0.090, 0.100
    head_dist = np.sqrt(((xx - head_cx) / head_rx)**2 + ((yy - head_cy) / head_ry)**2)
    head_a = np.clip(1.0 - head_dist, 0.0, 1.0) ** 0.65
    arr = _blend(arr, (0.72, 0.40, 0.22), head_a * 0.90)

    # Lamp-lit right side of face — warm highlight
    face_lit_dist = np.sqrt(((xx - 0.54) / 0.058)**2 + ((yy - 0.20) / 0.062)**2)
    face_lit_a = np.clip(1.0 - face_lit_dist, 0.0, 1.0) ** 1.2 * 0.55
    arr = _blend(arr, (0.82, 0.52, 0.30), face_lit_a)

    # Window-cold left cheek
    face_cool_dist = np.sqrt(((xx - 0.44) / 0.045)**2 + ((yy - 0.22) / 0.055)**2)
    face_cool_a = np.clip(1.0 - face_cool_dist, 0.0, 1.0) ** 1.4 * 0.38
    arr = _blend(arr, (0.52, 0.52, 0.60), face_cool_a)

    # Forehead — broad, high
    forehead_dist = np.sqrt(((xx - 0.50) / 0.075)**2 + ((yy - 0.14) / 0.042)**2)
    forehead_a = np.clip(1.0 - forehead_dist, 0.0, 1.0) ** 1.0 * 0.72
    arr = _blend(arr, (0.75, 0.44, 0.24), forehead_a)

    # ── Grey hair swept back ───────────────────────────────────────────────────
    hair_dist = np.sqrt(((xx - 0.50) / 0.095)**2 + ((yy - 0.12) / 0.062)**2)
    hair_a = np.clip(1.0 - hair_dist, 0.0, 1.0) ** 0.70 * (yy < 0.16)
    hair_a = np.broadcast_to(hair_a, (h, w)).copy()
    arr = _blend(arr, (0.52, 0.50, 0.48), hair_a * 0.88)

    # Hair highlight (lamp)
    hair_hi_dist = np.sqrt(((xx - 0.54) / 0.048)**2 + ((yy - 0.11) / 0.030)**2)
    hair_hi_a = np.clip(1.0 - hair_hi_dist, 0.0, 1.0) ** 1.5 * 0.52
    arr = _blend(arr, (0.78, 0.75, 0.68), hair_hi_a)

    # ── Eyes: deep-set, intense ───────────────────────────────────────────────
    for ex, ey in [(0.47, 0.21), (0.54, 0.20)]:
        # Eye socket shadow
        socket_dist = np.sqrt(((xx - ex) / 0.028)**2 + ((yy - ey) / 0.018)**2)
        socket_a = np.clip(1.0 - socket_dist, 0.0, 1.0) ** 0.9 * 0.65
        arr = _blend(arr, (0.28, 0.18, 0.10), socket_a)
        # Iris
        iris_dist = np.sqrt(((xx - ex) / 0.014)**2 + ((yy - ey) / 0.014)**2)
        iris_a = np.clip(1.0 - iris_dist, 0.0, 1.0) ** 1.2 * 0.88
        arr = _blend(arr, (0.20, 0.22, 0.28), iris_a)
        # Highlight dot
        hi_dist = np.sqrt(((xx - (ex + 0.004)) / 0.004)**2 + ((yy - (ey - 0.004)) / 0.004)**2)
        hi_a = np.clip(1.0 - hi_dist, 0.0, 1.0) ** 1.5 * 0.78
        arr = _blend(arr, (0.90, 0.90, 0.88), hi_a)

    # ── Nose bridge + nose tip ────────────────────────────────────────────────
    nose_dist = np.sqrt(((xx - 0.502) / 0.014)**2 + ((yy - 0.255) / 0.040)**2)
    nose_a = np.clip(1.0 - nose_dist, 0.0, 1.0) ** 1.0 * 0.70
    arr = _blend(arr, (0.62, 0.32, 0.15), nose_a)

    # Nose tip highlight
    nose_hi_dist = np.sqrt(((xx - 0.506) / 0.010)**2 + ((yy - 0.278) / 0.010)**2)
    nose_hi_a = np.clip(1.0 - nose_hi_dist, 0.0, 1.0) ** 1.5 * 0.58
    arr = _blend(arr, (0.80, 0.55, 0.35), nose_hi_a)

    # ── Mouth: firm, wide ─────────────────────────────────────────────────────
    mouth_dist = np.sqrt(((xx - 0.50) / 0.038)**2 + ((yy - 0.295) / 0.010)**2)
    mouth_a = np.clip(1.0 - mouth_dist, 0.0, 1.0) ** 1.0 * 0.72
    arr = _blend(arr, (0.35, 0.18, 0.10), mouth_a)

    # Upper lip line
    ulip_dist = np.sqrt(((xx - 0.50) / 0.030)**2 + ((yy - 0.290) / 0.007)**2)
    ulip_a = np.clip(1.0 - ulip_dist, 0.0, 1.0) ** 1.2 * 0.55
    arr = _blend(arr, (0.28, 0.14, 0.08), ulip_a)

    # ── Hands on desk ─────────────────────────────────────────────────────────
    # Left hand (flat, lower left of center)
    lhand_cx, lhand_cy = 0.40, 0.725
    lhand_rx, lhand_ry = 0.072, 0.028
    lhand_dist = np.sqrt(((xx - lhand_cx) / lhand_rx)**2 + ((yy - lhand_cy) / lhand_ry)**2)
    lhand_a = np.clip(1.0 - lhand_dist, 0.0, 1.0) ** 0.70 * 0.85
    arr = _blend(arr, (0.65, 0.36, 0.18), lhand_a)

    # Right hand (slightly cupped, lower right)
    rhand_cx, rhand_cy = 0.60, 0.720
    rhand_rx, rhand_ry = 0.062, 0.026
    rhand_dist = np.sqrt(((xx - rhand_cx) / rhand_rx)**2 + ((yy - rhand_cy) / rhand_ry)**2)
    rhand_a = np.clip(1.0 - rhand_dist, 0.0, 1.0) ** 0.70 * 0.85
    arr = _blend(arr, (0.70, 0.38, 0.18), rhand_a)

    # Knuckle highlights on both hands
    for hx, hy in [(0.38, 0.716), (0.41, 0.714), (0.44, 0.716),
                   (0.58, 0.712), (0.61, 0.710), (0.64, 0.713)]:
        kn_dist = np.sqrt(((xx - hx) / 0.010)**2 + ((yy - hy) / 0.007)**2)
        kn_a = np.clip(1.0 - kn_dist, 0.0, 1.0) ** 1.5 * 0.48
        arr = _blend(arr, (0.82, 0.55, 0.32), kn_a)

    # ── Accent: one red book spine on right shelf ──────────────────────────────
    red_spine_a = (np.abs(xx - 0.84) < 0.014) * np.clip((0.14 - yy) / 0.06, 0.0, 1.0) ** 0.5
    red_spine_a = np.broadcast_to(red_spine_a, (h, w)).copy()
    arr = _blend(arr, (0.75, 0.18, 0.12), red_spine_a * 0.78)

    # ── Floor: dark at very bottom ─────────────────────────────────────────────
    floor_a = np.clip((yy - 0.88) / 0.06, 0.0, 1.0) ** 0.8
    floor_a = np.broadcast_to(floor_a, (h, w)).copy()
    arr = _blend(arr, (0.14, 0.08, 0.04), floor_a)

    arr = np.clip(arr, 0.0, 1.0)
    arr_u8 = (arr * 255).astype(np.uint8)
    img = Image.fromarray(arr_u8, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    return img


def paint(output_path: str = "s218_elder.png") -> str:
    """
    Paint 'The Scholar's Study'.
    Oskar Kokoschka Expressionism: 129th mode — kokoschka_anxious_portrait_pass.
    """
    print("=" * 64)
    print("  Session 218 — 'The Scholar's Study'")
    print("  Elderly scholar at desk, window left, lamp right")
    print("  Technique: Oskar Kokoschka Expressionism")
    print("  129th mode: kokoschka_anxious_portrait_pass")
    print("=" * 64)

    ref_img = build_scholar_reference(W, H)
    print(f"  Reference built  ({W}x{H})")

    kokoschka = get_style("oskar_kokoschka")
    p = Painter(W, H)

    # Warm raw sienna ground — Kokoschka's characteristic warm canvas
    print("  [1] Tone ground — warm raw sienna ...")
    p.tone_ground(kokoschka.ground_color, texture_strength=0.07)

    # Broad underpainting — establish warm masses
    print("  [2] Underpainting — warm masses ...")
    p.underpainting(ref_img, stroke_size=45, n_strokes=1400)

    # Block in — build figure and environment masses
    print("  [3] Block in — figure and room ...")
    p.block_in(ref_img, stroke_size=28, n_strokes=2200)

    # Build form — face, hands, books, jacket
    print("  [4] Build form — face and hand detail ...")
    p.build_form(ref_img, stroke_size=13, n_strokes=2600)

    # Place lights — collar, lamp highlights, eye catch-lights
    print("  [5] Place lights — lamp and window accents ...")
    p.place_lights(ref_img, stroke_size=5, n_strokes=340)

    # ── Kokoschka signature pass — Anxious Portrait ───────────────────────────
    print("  [6] kokoschka_anxious_portrait_pass (129th mode) ...")
    p.kokoschka_anxious_portrait_pass(
        edge_darkness=0.55,
        color_tension=0.30,
        scratch_strength=0.40,
        shadow_gamma=1.8,
        opacity=0.80,
    )

    # Edge definition — contour lines, face edges
    print("  [7] Edge definition ...")
    p.edge_definition_pass(strength=0.35)

    # Meso detail — book spine texture, desk grain
    print("  [8] Meso detail ...")
    p.meso_detail_pass(opacity=0.24)

    # Warm sienna glaze — unify with Kokoschka's warm ground undertow
    print("  [9] Warm glaze ...")
    p.glaze((0.55, 0.28, 0.12), opacity=0.09)

    # Finish — light vignette
    print("  [10] Finish ...")
    p.finish(vignette=0.16, crackle=False)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    out = paint()
    print(f"\n  Done: {out}")
