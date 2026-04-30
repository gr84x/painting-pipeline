"""
paint_s262_vuillard_windowsill.py -- Session 262

"Windowsill with Ceramic Vessel and Folded Cloth" -- in the manner of Édouard Vuillard

Image Description
-----------------
Subject & Composition
    A narrow domestic windowsill seen from slightly below eye-level, occupying
    nearly the full width of the canvas.  The composition is three-layered: a
    flat plane of dark warm-brown wall (lower quarter), the windowsill surface
    (middle band), and the window itself giving onto a pale grey-white winter
    exterior (upper half).  The geometry is deliberately compressed -- the sill
    is shallow, the wall very close, and the window close behind -- so that all
    three zones are pressed together in shallow depth.

The Figure
    No human figure.  Three objects crowd the sill:

    (A) A small round-bellied ceramic vessel (height ~15cm), glazed an uneven
    warm ash-grey -- pale on the lit side, warm beige on the shadow side --
    positioned left-of-centre.  Its neck is short and the rim slightly chipped.
    Inside, two dried autumn branches with small papery seedheads rise at
    irregular angles.  The branches are a warm ochre-brown.

    (B) A folded textile -- a woman's headscarf or small napkin -- draped to the
    right of the vessel.  The fabric is cream-ochre with a faint printed pattern
    (small diamond shapes in a slightly darker ochre).  The fold creates a
    triangular shadow on the sill.

    (C) At the far right, partially cut off by the canvas edge, the corner of a
    small picture frame protrudes: dark warm walnut, the glass giving a faint
    cool reflection.  It hangs on the wall just above and behind the sill.

The Environment
    Interior: a Paris apartment, February.  The wallpaper behind and above the
    sill is a warm faded ochre with a barely-visible small-repeat diamond pattern
    in a slightly darker amber -- Vuillard's invariable background register.
    The sill surface is dark warm wood (unpainted), slightly dusty.  The window
    glass is frosted with the pale featureless luminance of an overcast winter
    sky -- near-white, no sky or building visible, just light.  The window frame
    is white paint slightly yellowed, the glazing bar visible as a pale grey
    horizontal band across the light source.  The mood is absolutely still --
    nothing has moved here for hours.

Technique & Palette
    Vuillard Chromatic Dissolution mode -- session 262, 173rd distinct mode.

    The palette follows Vuillard's cardboard distemper register:
    - Ground: warm ochre-cardboard imprimatura (0.72, 0.62, 0.44)
    - Wallpaper/background: amber-ochre (0.75, 0.65, 0.46)
    - Vessel: warm ash-grey to beige (0.78, 0.74, 0.66) -- (0.64, 0.56, 0.44)
    - Textile: cream-ochre (0.84, 0.76, 0.58) with amber shadow (0.62, 0.52, 0.40)
    - Sill wood: dark warm brown (0.34, 0.28, 0.20)
    - Window light: near-white (0.92, 0.91, 0.88)
    - Dried branches: warm ochre (0.70, 0.56, 0.32)

    Stage-by-stage:
    Ground: warm ochre imprimatura
    Block-in: light source (window), sill, vessel, cloth masses
    Build form: vessel form, cloth fold, branch detail, wallpaper register
    Place lights: window light bloom, vessel highlight
    Vuillard Chromatic Dissolution: hue averaging (figure/ground dissolution),
                                    ochre midtone warm penetration,
                                    matte distemper grain
    Local Hue Drift: drift saturation-gated, sigma=20
    Triple Zone Glaze: cool blue shadows (sill), warm amber mids (wall)
    Tonal Key pass: mid-high key confirm

Mood & Intent
    The image intends stillness and enclosure -- a room that has held these
    objects for years and will hold them for years more.  The ochre warmth
    speaks of domestic time: not the dramatic time of events but the slow time
    of inhabited space.  The window light is the only external thing in the
    picture and it is without incident -- just grey light, doing its work.
    The viewer should feel the specific gravity of a warm room in a cold city
    in winter, and the particular quality of attention a painter brings to
    objects no one else has noticed.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw
from stroke_engine import Painter

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "s262_vuillard_windowsill.png")

W, H = 1040, 1440   # portrait -- Vuillard often worked vertically

RNG = np.random.default_rng(262)


def add_noise(arr: np.ndarray, sigma: float, amplitude: float) -> np.ndarray:
    """Add smooth luminance noise."""
    raw = RNG.standard_normal(arr.shape[:2]).astype(np.float32) * amplitude
    smooth = gaussian_filter(raw, sigma=sigma)
    if arr.ndim == 3:
        return np.clip(arr + smooth[:, :, None], 0.0, 1.0)
    return np.clip(arr + smooth, 0.0, 1.0)


def gradient(h: int, w: int, y0: float, y1: float,
             c0: tuple, c1: tuple) -> np.ndarray:
    """Vertical gradient strip between normalized y-coordinates."""
    band = np.zeros((h, w, 3), np.float32)
    r0 = max(0, int(y0 * h))
    r1 = min(h, int(y1 * h))
    if r0 >= r1:
        return band
    ys = np.linspace(0.0, 1.0, r1 - r0, dtype=np.float32)[:, None]
    for c in range(3):
        band[r0:r1, :, c] = c0[c] * (1.0 - ys) + c1[c] * ys
    return band


def oval_mask(h: int, w: int, cy: float, cx: float,
              ry: float, rx: float, feather: float = 8.0) -> np.ndarray:
    """Soft oval mask in normalized coordinates."""
    ys = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    xs = np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]
    dist = np.sqrt(((ys - cy) / max(ry, 1e-4)) ** 2
                   + ((xs - cx) / max(rx, 1e-4)) ** 2)
    # 0 = inside, 1 = outside
    mask = np.clip(dist, 0.0, 1.0 + feather / h)
    mask = np.clip(1.0 - (mask - 1.0) * h / feather, 0.0, 1.0).astype(np.float32)
    return mask


def rect_mask(h: int, w: int, y0: float, y1: float,
              x0: float, x1: float, feather: float = 6.0) -> np.ndarray:
    """Soft rectangular mask."""
    ys = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    xs = np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]
    my = np.clip(np.minimum((ys - y0) / max(feather / h, 1e-4),
                             (y1 - ys) / max(feather / h, 1e-4)), 0.0, 1.0)
    mx = np.clip(np.minimum((xs - x0) / max(feather / w, 1e-4),
                             (x1 - xs) / max(feather / w, 1e-4)), 0.0, 1.0)
    return (my * mx).astype(np.float32)


def build_reference() -> Image.Image:
    """
    Procedural reference for Vuillard windowsill scene.
    Returns a PIL Image (uint8 RGB) for correct _prep() handling.

    Zones (top -> bottom):
      Window: near-white cold light (upper 50%)
      Sill edge: thin dark wood line (~52-55%)
      Sill surface: dark warm brown (~55-72%)
      Wall below sill: warm ochre (~72-100%)

    Objects:
      Vessel (left-of-centre, sill surface)
      Textile/cloth (right of vessel)
      Wallpaper pattern (on window reveal walls)
      Dried branches rising from vessel
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # ── Zone 1: Window / exterior light (top 50%) ────────────────────────────
    # Overcast sky: near-white with very slight warm tint toward bottom
    sky_end = 0.50
    sky_band = gradient(H, W, 0.0, sky_end,
                        (0.93, 0.92, 0.90),   # top -- bright diffuse
                        (0.88, 0.87, 0.84))   # bottom -- slight warm
    ref[:int(sky_end * H), :] = sky_band[:int(sky_end * H), :]

    # Window glazing bar: pale horizontal line at ~38%
    bar_y = int(0.38 * H)
    ref[bar_y - 3:bar_y + 3, :] = np.array([0.72, 0.72, 0.70], np.float32)

    # ── Zone 2: Sill edge (52-55%) ────────────────────────────────────────────
    sill_top = 0.52
    sill_surf_start = 0.55
    sill_edge = gradient(H, W, sill_top, sill_surf_start,
                         (0.28, 0.22, 0.16),
                         (0.30, 0.24, 0.18))
    mask_se = rect_mask(H, W, sill_top, sill_surf_start, 0.0, 1.0, feather=4.0)
    ref += sill_edge * mask_se[:, :, None]

    # ── Zone 3: Sill surface (55-72%) ─────────────────────────────────────────
    sill_surf_end = 0.72
    sill_surf = gradient(H, W, sill_surf_start, sill_surf_end,
                         (0.36, 0.29, 0.20),
                         (0.30, 0.24, 0.16))
    mask_ss = rect_mask(H, W, sill_surf_start, sill_surf_end, 0.0, 1.0, feather=4.0)
    ref += sill_surf * mask_ss[:, :, None]

    # ── Zone 4: Wall below sill (72-100%) ────────────────────────────────────
    wall_below = gradient(H, W, sill_surf_end, 1.0,
                          (0.68, 0.58, 0.40),   # upper wall -- warm amber
                          (0.56, 0.46, 0.32))   # lower -- slightly darker
    mask_wb = rect_mask(H, W, sill_surf_end, 1.0, 0.0, 1.0, feather=6.0)
    ref += wall_below * mask_wb[:, :, None]

    # ── Wallpaper on window-reveal side walls (left + right strips, top half) ─
    reveal_w = 0.08  # 8% of width = window reveal
    reveal_color = np.array([0.75, 0.64, 0.46], np.float32)  # ochre amber
    ml = rect_mask(H, W, 0.0, sky_end, 0.0, reveal_w, feather=6.0)
    mr = rect_mask(H, W, 0.0, sky_end, 1.0 - reveal_w, 1.0, feather=6.0)
    ref += ml[:, :, None] * reveal_color
    ref += mr[:, :, None] * reveal_color

    # ── OBJECT A: Ceramic vessel (left-of-centre on sill) ─────────────────────
    # Vessel body: ovoid, centred at (~38%, 62.5%)
    v_cx, v_cy = 0.38, 0.625
    v_rx, v_ry = 0.085, 0.055   # ellipse semi-axes in normalised coords
    mask_vessel = oval_mask(H, W, v_cy, v_cx, v_ry, v_rx, feather=10.0)

    # Lit side (left) is pale grey, shadow side (right) is warm beige
    xs = np.linspace(0.0, 1.0, W, dtype=np.float32)[None, :]
    vessel_lit_frac = np.clip((v_cx - xs) / (v_rx * 2.0) + 0.5, 0.0, 1.0)  # 1=far left=lit
    vessel_col_r = 0.78 * vessel_lit_frac + 0.62 * (1.0 - vessel_lit_frac)
    vessel_col_g = 0.74 * vessel_lit_frac + 0.54 * (1.0 - vessel_lit_frac)
    vessel_col_b = 0.68 * vessel_lit_frac + 0.42 * (1.0 - vessel_lit_frac)
    vessel_col = np.stack([vessel_col_r.squeeze(),
                           vessel_col_g.squeeze(),
                           vessel_col_b.squeeze()], axis=-1)
    # broadcast to (H, W, 3)
    vessel_col = np.broadcast_to(vessel_col[None, :, :], (H, W, 3)).copy().astype(np.float32)

    # Slightly darker at the very bottom (shadow under vessel)
    ys = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    vert_shadow = 1.0 - 0.15 * np.clip((ys - (v_cy - v_ry)) / (v_ry * 1.5), 0.0, 1.0)
    vessel_col *= vert_shadow[:, :, None]

    # Add vessel neck (narrower oval at top)
    neck_cx, neck_cy = v_cx, v_cy - v_ry * 0.85
    neck_rx, neck_ry = v_rx * 0.38, v_ry * 0.40
    mask_neck = oval_mask(H, W, neck_cy, neck_cx, neck_ry, neck_rx, feather=8.0)
    neck_col = np.array([0.76, 0.70, 0.62], np.float32)
    vessel_col[mask_neck > 0.1] = (vessel_col[mask_neck > 0.1] * 0.5
                                    + neck_col * 0.5)
    mask_vessel_full = np.clip(mask_vessel + mask_neck * 0.8, 0.0, 1.0)

    ref = (ref * (1.0 - mask_vessel_full[:, :, None])
           + vessel_col * mask_vessel_full[:, :, None])

    # ── OBJECT B: Folded textile (right of vessel) ────────────────────────────
    # Main cloth body: roughly rectangular, slightly tapered
    cloth_y0, cloth_y1 = 0.58, 0.70
    cloth_x0, cloth_x1 = 0.52, 0.82
    mask_cloth = rect_mask(H, W, cloth_y0, cloth_y1, cloth_x0, cloth_x1, feather=8.0)

    cloth_col = np.array([0.84, 0.76, 0.58], np.float32)
    # Fold shadow: dark triangle on left half of cloth
    fold_mask = rect_mask(H, W, cloth_y0, cloth_y1, cloth_x0, cloth_x0 + 0.12, feather=5.0)
    fold_col  = np.array([0.62, 0.52, 0.40], np.float32)
    cloth_arr = (cloth_col * (1.0 - fold_mask[:, :, None])
                 + fold_col * fold_mask[:, :, None])

    ref = (ref * (1.0 - mask_cloth[:, :, None])
           + cloth_arr * mask_cloth[:, :, None])

    # ── OBJECT C: Partial picture frame (far right, mid-height on wall) ──────
    frame_y0, frame_y1 = 0.38, 0.56
    frame_x0, frame_x1 = 0.88, 1.0
    mask_frame_outer = rect_mask(H, W, frame_y0, frame_y1, frame_x0, frame_x1, feather=4.0)
    mask_frame_inner = rect_mask(H, W, frame_y0 + 0.015, frame_y1 - 0.015,
                                 frame_x0 + 0.018, frame_x1, feather=3.0)
    frame_border = np.clip(mask_frame_outer - mask_frame_inner, 0.0, 1.0)
    frame_col = np.array([0.38, 0.30, 0.22], np.float32)  # dark walnut
    glass_col = np.array([0.82, 0.82, 0.84], np.float32)  # faint cool reflection

    ref = (ref * (1.0 - frame_border[:, :, None])
           + frame_col * frame_border[:, :, None])
    ref = (ref * (1.0 - mask_frame_inner[:, :, None] * 0.6)
           + glass_col * mask_frame_inner[:, :, None] * 0.6)

    # ── Dried branches in vessel ──────────────────────────────────────────────
    # Two angled lines drawn on reference image as thin warm strips
    branch_col = np.array([0.68, 0.52, 0.30], np.float32)

    # Branch 1: leans right-and-up from vessel neck
    # Represent as a very narrow oval stretched diagonally
    for bx, by, bangle, blen in [
        (0.42, 0.35, 0.25, 0.18),   # right-lean branch
        (0.36, 0.32, -0.10, 0.22),  # slight-left branch
    ]:
        bm = oval_mask(H, W, by, bx, blen, 0.012, feather=6.0)
        ref = (ref * (1.0 - bm[:, :, None] * 0.85)
               + branch_col * bm[:, :, None] * 0.85)

    # ── Wallpaper subtle diamond pattern noise ────────────────────────────────
    # Faint diamond repeat visible on wall zones
    wall_zone = rect_mask(H, W, sky_end, 1.0, 0.0, 1.0, feather=8.0)
    # Create subtle diamond pattern via periodically modulated grid
    ys_grid = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    xs_grid = np.linspace(0.0, 1.0, W, dtype=np.float32)[None, :]
    diamond = (np.cos(ys_grid * H / 28 * np.pi * 2)
               * np.cos(xs_grid * W / 28 * np.pi * 2)) * 0.025
    diamond = diamond.astype(np.float32)
    ref[:, :, 0] = np.clip(ref[:, :, 0] + diamond * wall_zone, 0.0, 1.0)
    ref[:, :, 1] = np.clip(ref[:, :, 1] + diamond * wall_zone * 0.8, 0.0, 1.0)

    # ── Sill dust / subtle grain ──────────────────────────────────────────────
    ref = add_noise(ref, sigma=1.5, amplitude=0.012)

    # ── Final: convert to PIL Image (uint8) for correct painter ingestion ────
    ref = np.clip(ref, 0.0, 1.0)
    return Image.fromarray((ref * 255).astype(np.uint8), "RGB")


def main() -> None:
    print("Session 262 -- Édouard Vuillard: Windowsill with Ceramic Vessel")
    print("=" * 60)

    # ── Build reference ───────────────────────────────────────────────────────
    print("Building reference image...")
    ref = build_reference()  # PIL Image (uint8)

    # ── Initialise painter ────────────────────────────────────────────────────
    p = Painter(W, H, seed=262)

    # ── Ground: warm ochre-cardboard imprimatura ──────────────────────────────
    print("Toning ground...")
    p.tone_ground(color=(0.72, 0.62, 0.44), texture_strength=0.025)

    # ── Underpainting ─────────────────────────────────────────────────────────
    print("Underpainting...")
    p.underpainting(ref, stroke_size=52, n_strokes=240)
    p.underpainting(ref, stroke_size=38, n_strokes=220)

    # ── Block in broad masses ─────────────────────────────────────────────────
    print("Block in...")
    p.block_in(ref, stroke_size=32, n_strokes=460)
    p.block_in(ref, stroke_size=20, n_strokes=480)

    # ── Build form ────────────────────────────────────────────────────────────
    print("Building form...")
    p.build_form(ref, stroke_size=12, n_strokes=520)
    p.build_form(ref, stroke_size=6, n_strokes=440)

    # ── Place lights ──────────────────────────────────────────────────────────
    print("Placing lights...")
    p.place_lights(ref, stroke_size=4, n_strokes=300)
    p.place_lights(ref, stroke_size=3, n_strokes=280)

    # ── Vuillard Chromatic Dissolution (artist pass) ─────────────────────────
    print("Vuillard Chromatic Dissolution pass...")
    p.vuillard_chromatic_dissolution_pass(
        hue_blur_sigma=14.0,
        hue_blend=0.52,
        ochre_r=0.78, ochre_g=0.66, ochre_b=0.42,
        ochre_strength=0.26,
        ochre_lum_lo=0.34, ochre_lum_hi=0.74,
        grain_amplitude=0.025,
        grain_sigma=0.9,
        noise_seed=262,
        opacity=0.82,
    )

    # ── Local Hue Drift (pipeline improvement) ────────────────────────────────
    print("Local Hue Drift pass...")
    p.paint_local_hue_drift_pass(
        drift_sigma=20.0,
        drift_strength=0.38,
        saturation_floor=0.06,
        saturation_ceil=0.88,
        noise_seed=262,
        opacity=0.68,
    )

    # ── Triple Zone Glaze: cool blue shadows, warm amber mids ────────────────
    print("Triple Zone Glaze pass...")
    p.paint_triple_zone_glaze_pass(
        shadow_pivot=0.30,
        highlight_pivot=0.70,
        shadow_r=0.30, shadow_g=0.32, shadow_b=0.48,
        shadow_opacity=0.10,
        mid_r=0.76, mid_g=0.68, mid_b=0.46,
        mid_opacity=0.08,
        highlight_r=0.90, highlight_g=0.88, highlight_b=0.82,
        highlight_opacity=0.09,
        feather_sigma=9.0,
        noise_seed=262,
        opacity=0.70,
    )

    # ── Tonal Key pass: confirm mid-high key ─────────────────────────────────
    print("Tonal Key pass...")
    p.paint_tonal_key_pass()

    # ── Save ──────────────────────────────────────────────────────────────────
    print(f"Saving to {OUTPUT}...")
    p.save(OUTPUT)
    print("Done.")


if __name__ == "__main__":
    main()
