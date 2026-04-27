"""
paint_s216_horizon_coast.py — Original composition: "Horizon Coast"

Session 216 painting — inspired by Richard Diebenkorn (1922–1993).

IMAGE DESCRIPTION
=================
Subject & Composition:
  A weathered wooden fishing pier extends diagonally from the lower-left
  corner into the middle distance of a flat coastal bay — a single strong
  diagonal cutting across the dominant horizontal register of the composition.
  The viewpoint is slightly elevated, perhaps from a low dune or the deck of
  a beachfront structure, looking northwest across still water toward an open
  horizon. The pier's recession into depth is the only narrative movement in
  an otherwise static scene. No figures. No boats. Just the geometry of
  land, water, and sky.

The Environment:
  The scene is organized in four distinct horizontal zones in the manner of
  Diebenkorn's Ocean Park series:
    — Foreground: wet sand, warm ochre and tan, darkened at the tide-line
      where the last wave left a glaze of reflected sky. The pier pilings
      begin here, four visible cross-braces receding into middle ground.
    — Middle water: flat, shallow bay, the surface a muted blue-green barely
      darker than the sky, broken only by the long shadow of the pier falling
      across it at a low angle.
    — Distant ocean: a band of deeper, cooler Pacific blue at the horizon —
      the same blue Diebenkorn returned to obsessively across 135 Ocean Park
      works. Slightly darker than the sky, with a hard horizon edge softened
      by marine haze.
    — Sky: the dominant upper zone. A cool, bleached blue-white — not noon
      blue but mid-morning California sky seen through a thin marine layer
      that softens shadows and makes every color slightly luminous. A single
      pale contrail dissolves across the upper third.

  The boundaries between zones carry the thin ruled lines characteristic of
  Diebenkorn: the sand-to-water edge is a precise line of foam, the water-
  to-sky edge at the horizon is the sharpest line in the painting. Within
  each zone there is variation — the sand is not one flat color but carries
  evidence of an underpainting — but the overall character is of contained,
  open color fields.

Technique & Palette:
  Richard Diebenkorn's Ocean Park method — 127th distinct mode:
  diebenkorn_ocean_park_pass. Horizontal zone segmentation with Gaussian
  smoothing within each zone, thin boundary line marks, and a coastal palette
  shift that lifts luminosity and cools shadows toward Pacific blue-gray.

  Palette:
    — Warm chalk white (0.82, 0.80, 0.72) — sky and foam
    — Pacific blue (0.56, 0.70, 0.76) — water and sky zones
    — Dusty sage (0.64, 0.74, 0.62) — distant coastal vegetation hint
    — Sandy ochre (0.86, 0.78, 0.58) — foreground sand
    — Muted terra cotta (0.68, 0.58, 0.52) — pier timber in raking light
    — Cool blue-gray (0.82, 0.85, 0.88) — haze and shadow
    — Deep slate (0.42, 0.50, 0.46) — deep-water band and pier shadow

Mood & Intent:
  The painting seeks the quality of arrested time specific to mid-morning
  coastal light — the moment after the marine layer has thinned but before
  the afternoon heat arrives, when color is most itself and shadows are soft
  and short. The pier is a human intrusion into the geometry of coast, but
  it has been here long enough to belong. The horizon line — that absolute
  blue Diebenkorn drew and erased and redrew across 20 years of Ocean Park —
  carries the painting's emotional weight: the feeling of standing at the
  edge of something vast, calm, and indifferent. Not melancholy. Stillness.
"""

import numpy as np
from PIL import Image, ImageFilter

from stroke_engine import Painter
from art_catalog import get_style

W, H = 900, 720   # landscape format — suited to the horizontal composition


def build_horizon_coast_reference(w: int, h: int) -> Image.Image:
    """
    Build a synthetic reference image organized in four horizontal zones
    with a diagonal pier structure for Diebenkorn Ocean Park rendering.
    """
    arr = np.zeros((h, w, 3), dtype=np.float32)
    xx  = np.linspace(0.0, 1.0, w)[np.newaxis, :]   # (1, W)
    yy  = np.linspace(0.0, 1.0, h)[:, np.newaxis]   # (H, 1)

    def _blend(base, color, alpha):
        c = np.array(color, dtype=np.float32)
        return base + (c - base) * np.clip(alpha, 0.0, 1.0)[..., np.newaxis]

    # ── Zone boundaries (y fractions) ─────────────────────────────────────────
    z_sand_top   = 0.0
    z_sand_bot   = 0.62   # sand occupies lower 38% of canvas
    z_water_bot  = 0.40   # mid-water band
    z_ocean_bot  = 0.30   # deep ocean band
    # sky: 0.0 → 0.30

    # ── Sky zone (0.0 → z_ocean_bot) ─────────────────────────────────────────
    sky_top  = np.array([0.86, 0.88, 0.92], dtype=np.float32)   # bleached zenith
    sky_bot  = np.array([0.76, 0.82, 0.88], dtype=np.float32)   # horizon haze
    sky_grad = np.clip(yy / z_ocean_bot, 0.0, 1.0)
    sky_col  = sky_top[np.newaxis, np.newaxis, :] * (1.0 - sky_grad[..., np.newaxis]) + \
               sky_bot[np.newaxis, np.newaxis, :] * sky_grad[..., np.newaxis]
    sky_mask = np.clip(1.0 - (yy - z_ocean_bot) / 0.04, 0.0, 1.0)
    arr = _blend(arr, [0.0, 0.0, 0.0], sky_mask * 0.0)  # initialize
    arr += sky_col * (yy < z_ocean_bot)

    # ── Deep ocean band (z_ocean_bot → z_water_bot) ───────────────────────────
    ocean_col  = np.array([0.46, 0.62, 0.72], dtype=np.float32)
    ocean_mask = (yy >= z_ocean_bot) & (yy < z_water_bot)
    arr += ocean_col * ocean_mask

    # ── Mid-water band (z_water_bot → z_sand_bot) ────────────────────────────
    water_top = np.array([0.60, 0.74, 0.80], dtype=np.float32)
    water_bot = np.array([0.70, 0.80, 0.76], dtype=np.float32)  # warmer near sand
    water_frac = np.clip((yy - z_water_bot) / (z_sand_bot - z_water_bot), 0.0, 1.0)
    water_col  = water_top * (1.0 - water_frac) + water_bot * water_frac
    water_mask = (yy >= z_water_bot) & (yy < z_sand_bot)
    arr += water_col * water_mask

    # ── Sand / foreground (z_sand_bot → 1.0) ─────────────────────────────────
    sand_top = np.array([0.76, 0.74, 0.62], dtype=np.float32)   # wet sand at tide line
    sand_bot = np.array([0.88, 0.82, 0.64], dtype=np.float32)   # dry sand foreground
    sand_frac = np.clip((yy - z_sand_bot) / (1.0 - z_sand_bot), 0.0, 1.0)
    sand_col  = sand_top * (1.0 - sand_frac) + sand_bot * sand_frac
    sand_mask = (yy >= z_sand_bot)
    arr += sand_col * sand_mask

    # ── Pier structure — diagonal from lower-left to mid-distance ─────────────
    # Pier deck: a diagonal band, narrowing with perspective
    # Pier goes from (0.04, 0.98) at bottom-left to (0.45, 0.48) at middle
    def pier_x_at_y(y_frac):
        """Return pier centerline x at given y_frac."""
        # Linear perspective recession
        t = np.clip((y_frac - 0.48) / (0.98 - 0.48), 0.0, 1.0)
        return 0.04 + (0.45 - 0.04) * (1.0 - t)

    pier_center_x = pier_x_at_y(yy)          # (H, 1)
    pier_width_frac = 0.003 + 0.022 * np.clip((yy - 0.48) / 0.50, 0.0, 1.0)  # widens nearer
    pier_dist = np.abs(xx - pier_center_x) / np.maximum(pier_width_frac, 1e-4)
    pier_alpha = np.clip(1.0 - pier_dist, 0.0, 1.0) ** 0.7 * (yy >= 0.48)

    pier_color = np.array([0.62, 0.54, 0.46], dtype=np.float32)   # weathered timber
    arr = _blend(arr, pier_color, pier_alpha * 0.85)

    # Pier side shadow (underside, slightly darker cool)
    pier_shadow_dist = np.abs(xx - (pier_center_x + pier_width_frac * 1.2)) / \
                       np.maximum(pier_width_frac * 0.6, 1e-4)
    pier_shadow_a = np.clip(1.0 - pier_shadow_dist, 0.0, 1.0) ** 1.2 * (yy >= 0.50)
    arr = _blend(arr, [0.30, 0.34, 0.38], pier_shadow_a * 0.50)

    # ── Pier shadow cast on water ─────────────────────────────────────────────
    shadow_x_offset = 0.018   # shadow falls slightly right of pier in morning light
    pier_shadow_water_dist = np.abs(
        xx - (pier_center_x + shadow_x_offset)) / np.maximum(pier_width_frac * 0.8, 1e-4)
    water_shadow_a = np.clip(1.0 - pier_shadow_water_dist, 0.0, 1.0) * \
                     ((yy >= z_water_bot) & (yy < z_sand_bot))
    arr = _blend(arr, [0.36, 0.46, 0.54], water_shadow_a * 0.55)

    # ── Horizon line accent — thin dark band at ocean/sky boundary ────────────
    horizon_dist = np.abs(yy - z_ocean_bot)
    horizon_a    = np.clip(1.0 - horizon_dist / 0.008, 0.0, 1.0) * 0.60
    arr = _blend(arr, [0.34, 0.44, 0.52], horizon_a)

    # ── Foam line — thin bright band at sand/water boundary ───────────────────
    foam_dist = np.abs(yy - z_sand_bot)
    foam_a    = np.clip(1.0 - foam_dist / 0.012, 0.0, 1.0) * 0.70
    arr = _blend(arr, [0.92, 0.92, 0.92], foam_a)

    # ── Contrail — single pale diagonal line in upper sky ─────────────────────
    contrail_dist = np.abs((yy - 0.08) - (xx - 0.20) * 0.18)
    contrail_a    = np.clip(1.0 - contrail_dist / 0.006, 0.0, 1.0) * \
                    (yy < 0.22) * (xx > 0.18) * 0.35
    arr = _blend(arr, [0.92, 0.92, 0.94], contrail_a)

    # ── Subtle sand texture (noise) ───────────────────────────────────────────
    rng        = np.random.RandomState(216)
    sand_noise = rng.uniform(-0.03, 0.03, (h, w)).astype(np.float32)
    sand_noise_mask = (yy >= z_sand_bot)[:, :, 0] if yy.shape[1] == 1 else (yy >= z_sand_bot)
    arr[:, :, 0] += sand_noise * sand_noise_mask.squeeze()
    arr[:, :, 1] += sand_noise * 0.8 * sand_noise_mask.squeeze()
    arr[:, :, 2] += sand_noise * 0.5 * sand_noise_mask.squeeze()

    arr = np.clip(arr, 0.0, 1.0)
    arr_u8 = (arr * 255).astype(np.uint8)
    img = Image.fromarray(arr_u8, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(1.8))
    return img


def paint(output_path: str = "s216_horizon_coast.png") -> str:
    """
    Paint 'Horizon Coast' — California coastal bay with pier, four horizontal zones.
    Richard Diebenkorn Ocean Park: 127th mode.
    """
    print("=" * 64)
    print("  Session 216 — 'Horizon Coast'")
    print("  Weathered pier, four horizontal zones, Pacific morning light")
    print("  Technique: Richard Diebenkorn Ocean Park")
    print("  127th mode: diebenkorn_ocean_park_pass")
    print("=" * 64)

    ref_img = build_horizon_coast_reference(W, H)
    print(f"  Reference built  ({W}x{H})")

    diebenkorn = get_style("richard_diebenkorn")
    p = Painter(W, H)

    # Warm off-white ground — Diebenkorn's prepared canvas
    print("  [1] Tone ground — warm off-white ...")
    p.tone_ground(diebenkorn.ground_color, texture_strength=0.04)

    # Broad underpainting — establish the horizontal zone masses
    print("  [2] Underpainting — horizontal zones ...")
    p.underpainting(ref_img, stroke_size=42, n_strokes=1800)

    # Block in — wide horizontal strokes, open field character
    print("  [3] Block in — wide field strokes ...")
    p.block_in(ref_img, stroke_size=30, n_strokes=2200)

    # Build form — coastal detail, pier structure
    print("  [4] Build form — coastal detail ...")
    p.build_form(ref_img, stroke_size=14, n_strokes=2600)

    # Place lights — foam line, horizon accent, contrail
    print("  [5] Place lights — luminous accents ...")
    p.place_lights(ref_img, stroke_size=5, n_strokes=320)

    # ── Diebenkorn signature pass — Ocean Park ────────────────────────────────
    print("  [6] diebenkorn_ocean_park_pass (127th mode) ...")
    p.diebenkorn_ocean_park_pass(
        n_zones=5,
        zone_smooth_sigma=28.0,
        smooth_blend_frac=0.55,
        line_width=2,
        line_opacity=0.62,
        palette_shift=0.30,
        luminosity_boost=0.07,
        opacity=0.65,
    )

    # Edge definition — sharpen the horizon line and foam line
    print("  [7] Edge definition ...")
    p.edge_definition_pass(strength=0.35)

    # Meso detail — surface variation within zones
    print("  [8] Meso detail ...")
    p.meso_detail_pass(opacity=0.22)

    # Finish — minimal vignette, no crackle
    print("  [9] Finish ...")
    p.finish(vignette=0.10, crackle=False)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    out = paint()
    print(f"\n  Done: {out}")
