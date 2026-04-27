"""
paint_s217_pheasant.py — Original composition: "Slaughtered Pheasant with Ceramic Bowl"

Session 217 painting — inspired by Chaïm Soutine (1893–1943).

IMAGE DESCRIPTION
=================
Subject & Composition:
  A male pheasant, slaughtered and hung upside-down by one ochre-yellow foot,
  occupies the left-center of the canvas. The bird hangs at a slight angle,
  the long barred tail feathers fanning down and to the left, the neck and
  iridescent head dropping in a loose arc. In the lower right, a white ceramic
  bowl catches a hard slant of window light, its interior gleaming bone-white
  against the warm dark ground.

The Figure:
  Full autumn plumage — copper-russet body streaked with raw umber, an
  iridescent blue-green head feather flash, a white collar ring against the
  crimson wattle. One wing droops heavier than the other, partially opened.
  The single bound foot at the top, tied with rough kitchen twine to a wooden
  hook, is the only taut point in an otherwise limp, gravity-surrendered form.
  The tail bars — dun gold and dark umber — sweep across the lower left corner.
  The bird is emphatically dead but its colors burn with vitality. Emotional
  state: beyond emotion; it is the painter who feels everything.

The Environment:
  A stone butcher's back-room or market kitchen. The wall behind is rough warm
  plaster — raw umber, burnt sienna, dark ochre — alive with Soutine's
  writhing brushwork, no single flat area. A narrow wooden shelf cuts across
  the upper edge. The counter surface in the foreground is a cold stone grey.
  The light falls hard from the upper left, casting a long warm shadow from
  the bird to the right. The room feels cramped, the color pressurized. The
  background is not passive; it churns with as much energy as the subject.

Technique & Palette:
  Chaïm Soutine Expressionism — 128th distinct mode:
  soutine_visceral_distortion_pass. Multi-frequency sinusoidal coordinate
  warping (three layers: low/mid/high frequency) via map_coordinates makes
  the bird's form writhe with muscular energy despite its stillness. Red-ochre
  chromatic push saturates the rich pheasant plumage. Aggressive impasto ridge
  carving amplifies the physical texture of feathers and rough plaster.

  Palette:
    — Beef-blood red (0.72, 0.08, 0.05)     — pheasant head and throat
    — Burnt sienna  (0.62, 0.28, 0.10)     — main body feathers
    — Cadmium orange (0.90, 0.48, 0.05)    — wing coverts and flank
    — Yellow ochre  (0.76, 0.60, 0.12)     — hanging foot, tail bars
    — Raw umber     (0.25, 0.14, 0.07)     — mid-shadow tones
    — Dark umber    (0.18, 0.10, 0.06)     — background plaster, deep shadow
    — Bone white    (0.94, 0.90, 0.78)     — collar ring, bowl, light catch
    — Viridian flash (0.12, 0.30, 0.15)    — iridescent head feathers

Mood & Intent:
  The painting inhabits Soutine's central paradox: the most brilliant color
  belongs to dead things. The pheasant's plumage, most vivid in the moment
  after slaughter, charges the canvas with the co-existence of beauty and
  ruin. The writhing surface refuses stillness. The viewer is simultaneously
  seduced by the richness of the color and unsettled by what carries it.
  Walk away with the reds burning in the eye.
"""

import numpy as np
from PIL import Image, ImageFilter

from stroke_engine import Painter
from art_catalog import get_style

W, H = 780, 1040   # portrait — the natural format for a hanging subject


def _blend(base: np.ndarray, color: tuple, alpha_hw: np.ndarray) -> np.ndarray:
    """Alpha-blend color (RGB float) into base (H, W, 3) using alpha (H, W)."""
    c = np.array(color, dtype=np.float32)
    a = np.clip(alpha_hw, 0.0, 1.0)[:, :, np.newaxis]
    return base + (c - base) * a


def build_pheasant_reference(w: int, h: int) -> Image.Image:
    """
    Build a synthetic reference image: hanging pheasant (left-center) +
    white ceramic bowl (lower right), dark warm plaster background.
    """
    arr = np.zeros((h, w, 3), dtype=np.float32)

    yf  = np.linspace(0.0, 1.0, h)
    xf  = np.linspace(0.0, 1.0, w)
    yy  = yf[:, np.newaxis]   # (H,1)
    xx  = xf[np.newaxis, :]   # (1,W)

    rng = np.random.RandomState(217)

    # ── Background: warm umber plaster ────────────────────────────────────────
    # Base coat: dark warm ochre-umber
    arr[:, :, 0] = 0.30
    arr[:, :, 1] = 0.16
    arr[:, :, 2] = 0.07

    # Large-scale plaster variation — warm patches
    for _ in range(8):
        cx = rng.uniform(0.1, 0.9)
        cy = rng.uniform(0.1, 0.9)
        r  = rng.uniform(0.12, 0.30)
        warm = rng.uniform(0.05, 0.14)
        dist = np.sqrt((xx - cx)**2 + (yy - cy)**2)
        patch_a = np.clip(1.0 - dist / r, 0.0, 1.0) ** 1.8 * warm
        arr[:, :, 0] += patch_a * rng.uniform(0.12, 0.25)
        arr[:, :, 1] += patch_a * rng.uniform(0.05, 0.12)
        arr[:, :, 2] += patch_a * rng.uniform(0.01, 0.05)

    # Fine plaster noise
    noise = rng.uniform(-0.04, 0.04, (h, w)).astype(np.float32)
    arr[:, :, 0] += noise
    arr[:, :, 1] += noise * 0.7
    arr[:, :, 2] += noise * 0.4

    # ── Shelf: narrow dark horizontal at top ──────────────────────────────────
    shelf_a = np.clip(1.0 - np.abs(yy - 0.04) / 0.025, 0.0, 1.0) * 0.90
    shelf_a = np.broadcast_to(shelf_a, (h, w)).copy()
    arr = _blend(arr, (0.20, 0.12, 0.06), shelf_a)

    # ── Counter: cold stone grey at bottom ───────────────────────────────────
    counter_a = np.clip((yy - 0.82) / 0.06, 0.0, 1.0) ** 0.8
    counter_a = np.broadcast_to(counter_a, (h, w)).copy()
    arr = _blend(arr, (0.52, 0.48, 0.44), counter_a)

    # Horizontal counter edge line
    edge_a = np.clip(1.0 - np.abs(yy - 0.82) / 0.008, 0.0, 1.0) * 0.70
    edge_a = np.broadcast_to(edge_a, (h, w)).copy()
    arr = _blend(arr, (0.22, 0.15, 0.10), edge_a)

    # ── Pheasant: hung upside-down, centered-left ─────────────────────────────
    # Foot-hook point at (x=0.40, y=0.07) — tight twine point at top
    # Bird body: elongated oval, main mass from y=0.12 to y=0.62, cx~0.38
    # Head/neck: from y=0.62 to y=0.80, curves left toward cx~0.32
    # Tail fan: from y=0.58 to y=0.95, fans out left from cx~0.35 to cx~0.10

    # Body (main oval — copper-russet core)
    body_cx = 0.39
    body_cy = 0.37
    body_rx = 0.105
    body_ry = 0.22
    body_dist = np.sqrt(((xx - body_cx) / body_rx)**2 + ((yy - body_cy) / body_ry)**2)
    body_a = np.clip(1.0 - body_dist, 0.0, 1.0) ** 0.65
    arr = _blend(arr, (0.68, 0.28, 0.08), body_a * 0.92)

    # Body highlight — burnt sienna mid-tones on right/upper body
    highlight_dist = np.sqrt(((xx - (body_cx - 0.025)) / (body_rx * 0.7))**2
                             + ((yy - (body_cy - 0.05)) / (body_ry * 0.55))**2)
    highlight_a = np.clip(1.0 - highlight_dist, 0.0, 1.0) ** 1.2 * 0.55
    arr = _blend(arr, (0.82, 0.42, 0.14), highlight_a)

    # Wing droop: left wing hanging lower — elongated oval, lower-left
    wing_cx, wing_cy = 0.30, 0.50
    wing_rx, wing_ry = 0.065, 0.13
    wing_angle = 0.35   # slight rotation
    dx_w = (xx - wing_cx) * np.cos(wing_angle) + (yy - wing_cy) * np.sin(wing_angle)
    dy_w = -(xx - wing_cx) * np.sin(wing_angle) + (yy - wing_cy) * np.cos(wing_angle)
    wing_dist = np.sqrt((dx_w / wing_rx)**2 + (dy_w / wing_ry)**2)
    wing_a = np.clip(1.0 - wing_dist, 0.0, 1.0) ** 0.80 * 0.88
    arr = _blend(arr, (0.50, 0.22, 0.06), wing_a)

    # Wing shadow edge (darker)
    wing_sh_dist = np.sqrt(((xx - 0.26) / 0.055)**2 + ((yy - 0.53) / 0.10)**2)
    wing_sh_a = np.clip(1.0 - wing_sh_dist, 0.0, 1.0) ** 1.5 * 0.45
    arr = _blend(arr, (0.22, 0.10, 0.04), wing_sh_a)

    # ── Neck + head (lower portion of bird, hanging down) ────────────────────
    # Neck: tapers from body downward, curves slightly left
    for i, (nx, ny, nr) in enumerate([
        (0.39, 0.62, 0.035),
        (0.37, 0.66, 0.032),
        (0.35, 0.70, 0.030),
        (0.33, 0.73, 0.027),
    ]):
        neck_dist = np.sqrt(((xx - nx) / nr)**2 + ((yy - ny) / (nr * 1.4))**2)
        neck_a = np.clip(1.0 - neck_dist, 0.0, 1.0) ** 0.8 * 0.85
        color = (0.52, 0.20, 0.06) if i < 2 else (0.18, 0.28, 0.10)
        arr = _blend(arr, color, neck_a)

    # White collar ring
    collar_dist = np.sqrt(((xx - 0.36) / 0.040)**2 + ((yy - 0.68) / 0.018)**2)
    collar_a = np.clip(1.0 - collar_dist, 0.0, 1.0) ** 1.0 * 0.85
    arr = _blend(arr, (0.92, 0.90, 0.80), collar_a)

    # Head: iridescent dark green with red wattle flash
    head_dist = np.sqrt(((xx - 0.32) / 0.042)**2 + ((yy - 0.76) / 0.052)**2)
    head_a = np.clip(1.0 - head_dist, 0.0, 1.0) ** 0.75 * 0.90
    arr = _blend(arr, (0.10, 0.28, 0.12), head_a)

    # Red wattle on head
    wattle_dist = np.sqrt(((xx - 0.31) / 0.018)**2 + ((yy - 0.78) / 0.014)**2)
    wattle_a = np.clip(1.0 - wattle_dist, 0.0, 1.0) ** 1.0 * 0.82
    arr = _blend(arr, (0.70, 0.06, 0.04), wattle_a)

    # Beak — small pale point below head
    beak_dist = np.sqrt(((xx - 0.30) / 0.010)**2 + ((yy - 0.81) / 0.018)**2)
    beak_a = np.clip(1.0 - beak_dist, 0.0, 1.0) ** 1.2 * 0.78
    arr = _blend(arr, (0.76, 0.62, 0.30), beak_a)

    # ── Tail fan: long barred feathers fanning lower-left ─────────────────────
    # Tail base at body bottom (x=0.36, y=0.58), fans out left and down
    # Individual tail feathers as elongated pointed ovals at angles
    tail_colors = [
        (0.70, 0.55, 0.15),   # dun gold bar
        (0.28, 0.18, 0.07),   # dark umber bar
        (0.68, 0.52, 0.14),
        (0.25, 0.15, 0.06),
        (0.72, 0.56, 0.16),
    ]
    tail_angles = [-0.35, -0.55, -0.75, -0.90, -1.08]  # radians (down-left)
    tail_lengths = [0.38, 0.42, 0.44, 0.40, 0.35]

    for feather_i, (ang, ln) in enumerate(zip(tail_angles, tail_lengths)):
        # Feather centerline direction
        fdx = np.sin(ang)   # x-component of feather direction
        fdy = np.cos(ang)   # y-component (positive = down)
        base_x, base_y = 0.36, 0.60

        # Feather as narrow elongated oval along the angle direction
        # Rotate canvas coords to feather frame
        dx_f = (xx - base_x) * np.cos(ang) - (yy - base_y) * np.sin(ang)
        dy_f = (xx - base_x) * np.sin(ang) + (yy - base_y) * np.cos(ang)

        # Elongated oval: narrow width, full length
        feather_half_len = ln * 0.5
        feather_half_wid = 0.018 + 0.006 * feather_i * 0.1
        # Taper toward tip
        along_t = dy_f / (feather_half_len + 1e-6)
        width_taper = np.clip(1.0 - np.abs(along_t) ** 0.7, 0.0, 1.0)
        feather_dist = (np.abs(dx_f) / (feather_half_wid * width_taper + 1e-5)
                        + (np.clip(dy_f - feather_half_len, 0.0, None) / (feather_half_len * 0.2 + 1e-5))
                        + (np.clip(-dy_f, 0.0, None) / (feather_half_len * 0.1 + 1e-5)))
        feather_a = np.clip(1.0 - feather_dist * 0.7, 0.0, 1.0) ** 0.60 * 0.82
        arr = _blend(arr, tail_colors[feather_i % len(tail_colors)], feather_a)

        # Bar pattern across feather
        bar_phase = np.sin((dy_f / (feather_half_len + 1e-6)) * 22.0)
        bar_a = feather_a * np.clip(bar_phase, 0.0, 1.0) * 0.35
        dark = tail_colors[(feather_i + 1) % len(tail_colors)]
        arr = _blend(arr, dark, bar_a)

    # ── Hanging foot + twine ──────────────────────────────────────────────────
    # Foot: narrow ochre-yellow above body top
    foot_dist = np.sqrt(((xx - 0.40) / 0.012)**2 + ((yy - 0.09) / 0.045)**2)
    foot_a = np.clip(1.0 - foot_dist, 0.0, 1.0) ** 1.0 * 0.90
    arr = _blend(arr, (0.78, 0.60, 0.12), foot_a)

    # Toes hanging (small projections)
    for tx, ty in [(0.38, 0.11), (0.42, 0.11), (0.40, 0.13)]:
        toe_dist = np.sqrt(((xx - tx) / 0.007)**2 + ((yy - ty) / 0.020)**2)
        toe_a = np.clip(1.0 - toe_dist, 0.0, 1.0) ** 1.2 * 0.82
        arr = _blend(arr, (0.72, 0.54, 0.10), toe_a)

    # Twine: thin dark line from top of foot to shelf
    twine_dist = np.abs(xx - 0.40) / 0.005 + np.clip(yy - 0.06, 0.0, None) * 1e4
    twine_a = np.clip(1.0 - twine_dist * 3.0, 0.0, 1.0) * (yy < 0.065)
    twine_a = np.broadcast_to(twine_a, (h, w)).copy()
    arr = _blend(arr, (0.28, 0.20, 0.10), twine_a)

    # Hook on shelf
    hook_dist = np.sqrt(((xx - 0.40) / 0.010)**2 + ((yy - 0.055) / 0.010)**2)
    hook_a = np.clip(1.0 - hook_dist, 0.0, 1.0) ** 1.0 * 0.88
    arr = _blend(arr, (0.35, 0.28, 0.18), hook_a)

    # ── Shadow from bird on wall (right side) ────────────────────────────────
    shadow_cx = 0.52
    shadow_cy = 0.38
    shadow_rx, shadow_ry = 0.12, 0.28
    shadow_dist = np.sqrt(((xx - shadow_cx) / shadow_rx)**2
                          + ((yy - shadow_cy) / shadow_ry)**2)
    shadow_a = np.clip(1.0 - shadow_dist, 0.0, 1.0) ** 1.5 * 0.38
    arr = _blend(arr, (0.16, 0.09, 0.05), shadow_a)

    # ── White ceramic bowl (lower right) ─────────────────────────────────────
    bowl_cx, bowl_cy = 0.74, 0.90
    bowl_rx, bowl_ry = 0.12, 0.072

    # Bowl exterior ellipse
    bowl_dist = np.sqrt(((xx - bowl_cx) / bowl_rx)**2 + ((yy - bowl_cy) / bowl_ry)**2)
    bowl_outer_a = np.clip(1.0 - bowl_dist, 0.0, 1.0) ** 0.60 * 0.92
    arr = _blend(arr, (0.90, 0.88, 0.82), bowl_outer_a)

    # Bowl interior (slightly inset, darker)
    bowl_inner_dist = np.sqrt(((xx - bowl_cx) / (bowl_rx * 0.80))**2
                              + ((yy - (bowl_cy + 0.010)) / (bowl_ry * 0.70))**2)
    bowl_inner_a = np.clip(1.0 - bowl_inner_dist, 0.0, 1.0) ** 0.75 * 0.80
    arr = _blend(arr, (0.78, 0.75, 0.68), bowl_inner_a)

    # Bowl highlight — slant light from upper left
    bowl_hi_dist = np.sqrt(((xx - (bowl_cx - 0.04)) / (bowl_rx * 0.35))**2
                           + ((yy - (bowl_cy - 0.020)) / (bowl_ry * 0.35))**2)
    bowl_hi_a = np.clip(1.0 - bowl_hi_dist, 0.0, 1.0) ** 1.5 * 0.72
    arr = _blend(arr, (0.96, 0.94, 0.90), bowl_hi_a)

    # Bowl rim — thin dark ellipse
    bowl_rim_dist = np.abs(np.sqrt(((xx - bowl_cx) / bowl_rx)**2
                                   + ((yy - bowl_cy) / bowl_ry)**2) - 1.0)
    bowl_rim_a = np.clip(1.0 - bowl_rim_dist / 0.06, 0.0, 1.0) * (yy >= bowl_cy - bowl_ry) * 0.65
    arr = _blend(arr, (0.35, 0.30, 0.22), bowl_rim_a)

    # ── Directional light — upper left warmth ─────────────────────────────────
    light_a = np.clip(1.0 - (xx * 0.6 + yy * 0.4), 0.0, 1.0) ** 2.0 * 0.18
    light_a = np.broadcast_to(light_a, (h, w)).copy()
    arr = _blend(arr, (0.92, 0.80, 0.60), light_a)

    arr = np.clip(arr, 0.0, 1.0)
    arr_u8 = (arr * 255).astype(np.uint8)
    img = Image.fromarray(arr_u8, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(1.4))
    return img


def paint(output_path: str = "s217_pheasant.png") -> str:
    """
    Paint 'Slaughtered Pheasant with Ceramic Bowl'.
    Chaïm Soutine Expressionism: 128th mode — soutine_visceral_distortion_pass.
    """
    print("=" * 64)
    print("  Session 217 — 'Slaughtered Pheasant with Ceramic Bowl'")
    print("  Hanging pheasant in butcher's back-room, white bowl")
    print("  Technique: Chaïm Soutine Expressionism")
    print("  128th mode: soutine_visceral_distortion_pass")
    print("=" * 64)

    ref_img = build_pheasant_reference(W, H)
    print(f"  Reference built  ({W}x{H})")

    soutine = get_style("chaim_soutine")
    p = Painter(W, H)

    # Dark reddish-brown ground — Soutine's characteristic warm dark ground
    print("  [1] Tone ground — dark reddish-brown ...")
    p.tone_ground(soutine.ground_color, texture_strength=0.08)

    # Broad underpainting — establish dark warm masses
    print("  [2] Underpainting — warm masses ...")
    p.underpainting(ref_img, stroke_size=50, n_strokes=1600)

    # Block in — build the bird form and background energy
    print("  [3] Block in — pheasant form ...")
    p.block_in(ref_img, stroke_size=32, n_strokes=2400)

    # Build form — feather structure, bowl form
    print("  [4] Build form — feather and plaster detail ...")
    p.build_form(ref_img, stroke_size=15, n_strokes=2800)

    # Place lights — collar flash, bowl highlight, foot color
    print("  [5] Place lights — iridescent accents ...")
    p.place_lights(ref_img, stroke_size=6, n_strokes=380)

    # ── Soutine signature pass — Visceral Distortion ──────────────────────────
    print("  [6] soutine_visceral_distortion_pass (128th mode) ...")
    p.soutine_visceral_distortion_pass(
        warp_strength=7.0,
        red_push=0.20,
        ochre_warm=0.28,
        impasto_radius=6,
        impasto_strength=0.50,
        opacity=0.75,
    )

    # Edge definition — feather edges, bowl rim
    print("  [7] Edge definition ...")
    p.edge_definition_pass(strength=0.40)

    # Meso detail — plaster texture, feather micro-texture
    print("  [8] Meso detail ...")
    p.meso_detail_pass(opacity=0.28)

    # Warm ochre glaze — unify with Soutine's characteristic warm undertow
    print("  [9] Warm glaze ...")
    p.glaze((0.58, 0.32, 0.08), opacity=0.10)

    # Finish — no crackle, light vignette to darken the corners
    print("  [10] Finish ...")
    p.finish(vignette=0.18, crackle=False)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    out = paint()
    print(f"\n  Done: {out}")
