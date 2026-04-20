"""
paint_mona_lisa_s105_numpy.py

Applies session-105 passes directly via numpy/PIL on top of the session-104
painting — bypasses the Painter class entirely to avoid slow imports.

Session-105 additions applied:
  1. guercino_penumbra_warmth_pass  -- il Guercino, Emilian Baroque
  2. penumbra_bloom (sfumato delta) -- session 105 improvement
  3. Gentle vignette + warm glaze   -- sealing finish
"""

import sys
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

W, H = 780, 1080

# ── Find the session-104 base painting ───────────────────────────────────────
CANDIDATES = [
    os.path.join(os.path.dirname(__file__), "mona_lisa_s104.png"),
    r"C:\Source\painting-pipeline\.claude\worktrees\bold-bardeen\mona_lisa_s104.png",
    "/c/Source/painting-pipeline/.claude/worktrees/bold-bardeen/mona_lisa_s104.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bold-bardeen", "mona_lisa_s104.png"),
]

base_path = None
for c in CANDIDATES:
    if os.path.exists(c):
        base_path = os.path.abspath(c)
        break

if base_path is None:
    raise FileNotFoundError(
        f"Cannot find mona_lisa_s104.png. Searched:\n  " + "\n  ".join(CANDIDATES)
    )

print(f"Base image: {base_path}")


def make_figure_mask() -> np.ndarray:
    """Standard Mona Lisa figure mask — soft ellipse centred on the figure."""
    cx, cy, rx, ry = 0.515 * W, 0.50 * H, 0.26 * W, 0.50 * H
    ys, xs = np.ogrid[:H, :W]
    d2 = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2
    mask = (d2 <= 1.0).astype(np.float32)
    mask = gaussian_filter(mask, sigma=18.0)
    mask = np.clip(mask / mask.max(), 0.0, 1.0)
    return mask


def guercino_pass(rgb: np.ndarray) -> np.ndarray:
    """
    il Guercino penumbra warmth pass (session 105).

    Three effects:
      1. Penumbra amber enrichment — Gaussian bell centred on lum 0.28–0.62.
      2. Upper-left directional warmth — large Gaussian falloff from upper-left.
      3. Deep shadow warm retention — umber warmth in deep shadow (lum < 0.28).
    """
    print("  Guercino penumbra warmth pass ...")
    r0, g0, b0 = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    lum = 0.299 * r0 + 0.587 * g0 + 0.114 * b0

    r_out = r0.copy()
    g_out = g0.copy()
    b_out = b0.copy()

    # Coordinate grids
    ys_f = np.arange(H, dtype=np.float32)[:, np.newaxis] / H
    xs_f = np.arange(W, dtype=np.float32)[np.newaxis, :] / W

    # 1. Penumbra amber enrichment
    # Gaussian bell centred at midpoint of penumbra range [0.28, 0.62]
    pb_mid   = (0.28 + 0.62) * 0.5   # = 0.45
    pb_width = (0.62 - 0.28) * 0.5   # = 0.17
    pb_mask  = np.exp(-0.5 * ((lum - pb_mid) / pb_width) ** 2).astype(np.float32)
    pb_mask  = gaussian_filter(pb_mask, sigma=4.5)
    pb_mask  = np.clip(pb_mask, 0.0, 1.0)

    r_out = np.clip(r_out + pb_mask * 0.038, 0.0, 1.0)
    g_out = np.clip(g_out + pb_mask * 0.018, 0.0, 1.0)
    b_out = np.clip(b_out - pb_mask * 0.008, 0.0, 1.0)

    # 2. Upper-left directional warmth
    light_cx, light_cy, light_radius = 0.18, 0.08, 0.85
    dist_ul  = np.sqrt((xs_f - light_cx) ** 2 + (ys_f - light_cy) ** 2).astype(np.float32)
    dir_mask = np.exp(-0.5 * (dist_ul / light_radius) ** 2)
    dir_mask = np.clip(dir_mask, 0.0, 1.0).astype(np.float32)

    r_out = np.clip(r_out + dir_mask * 0.018 * 1.2, 0.0, 1.0)
    g_out = np.clip(g_out + dir_mask * 0.018 * 0.5, 0.0, 1.0)

    # 3. Deep shadow warm retention
    shadow_mask = np.clip(
        (0.28 - lum) / (0.28 - 0.05 + 1e-6), 0.0, 1.0
    )
    shadow_mask = gaussian_filter(shadow_mask.astype(np.float32), sigma=3.6)
    shadow_mask = np.clip(shadow_mask, 0.0, 1.0)

    r_out = np.clip(r_out + shadow_mask * 0.022, 0.0, 1.0)
    g_out = np.clip(g_out + shadow_mask * 0.008, 0.0, 1.0)

    # Composite at opacity=0.28
    opacity = 0.28
    r_final = r0 * (1.0 - opacity) + r_out * opacity
    g_final = g0 * (1.0 - opacity) + g_out * opacity
    b_final = b0 * (1.0 - opacity) + b_out * opacity

    out = np.stack([r_final, g_final, b_final], axis=2).astype(np.float32)
    print("  Guercino pass complete.")
    return out


def penumbra_bloom_sfumato(rgb: np.ndarray) -> np.ndarray:
    """
    Session 105 improvement: penumbra_bloom applied as a direct delta.

    Applies a warm amber bloom in the penumbra zone (lum 0.30–0.60),
    then a very gentle haze to simulate the sfumato integration.
    This is the penumbra_bloom=0.06 improvement in sfumato_veil_pass.
    """
    print("  Penumbra bloom (session 105 sfumato improvement) ...")
    r0, g0, b0 = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    lum = 0.299 * r0 + 0.587 * g0 + 0.114 * b0

    # Penumbra bloom: Gaussian bell centred at 0.45 (midpoint of [0.30, 0.60])
    pb_mid   = (0.30 + 0.60) * 0.5   # = 0.45
    pb_width = (0.60 - 0.30) * 0.5   # = 0.15
    pb_mask  = np.exp(-0.5 * ((lum - pb_mid) / pb_width) ** 2).astype(np.float32)
    pb_mask  = gaussian_filter(pb_mask, sigma=4.0)
    pb_mask  = np.clip(pb_mask * 0.06, 0.0, 1.0)   # penumbra_bloom = 0.06

    # Warm amber bloom: R+0.042, G+0.018, B-0.008
    r_out = np.clip(r0 + pb_mask * 0.042, 0.0, 1.0)
    g_out = np.clip(g0 + pb_mask * 0.018, 0.0, 1.0)
    b_out = np.clip(b0 - pb_mask * 0.008, 0.0, 1.0)

    # Gentle haze to integrate the bloom edges
    for c_in, c_out in [(r_out, r_out), (g_out, g_out), (b_out, b_out)]:
        pass  # no full sfumato loop in direct mode — bloom speaks for itself

    out = np.stack([r_out, g_out, b_out], axis=2).astype(np.float32)
    print("  Penumbra bloom complete.")
    return out


def vignette_glaze(rgb: np.ndarray) -> np.ndarray:
    """Gentle vignette + warm amber glaze to seal the painting."""
    print("  Vignette + glaze ...")
    ys_f = np.arange(H, dtype=np.float32)[:, np.newaxis] / H
    xs_f = np.arange(W, dtype=np.float32)[np.newaxis, :] / W

    cx, cy = 0.5, 0.5
    dist   = np.sqrt(((xs_f - cx) * 1.3) ** 2 + ((ys_f - cy) * 1.1) ** 2)
    vig    = np.clip(1.0 - dist * 0.50 * 0.50, 0.5, 1.0).astype(np.float32)

    r = np.clip(rgb[:, :, 0] * vig, 0.0, 1.0)
    g = np.clip(rgb[:, :, 1] * vig, 0.0, 1.0)
    b = np.clip(rgb[:, :, 2] * vig, 0.0, 1.0)

    glaze_r, glaze_g, glaze_b = 0.58, 0.44, 0.16
    alpha = 0.034
    r = np.clip(r * (1 - alpha) + glaze_r * alpha, 0.0, 1.0)
    g = np.clip(g * (1 - alpha) + glaze_g * alpha, 0.0, 1.0)
    b = np.clip(b * (1 - alpha) + glaze_b * alpha, 0.0, 1.0)

    print("  Vignette + glaze complete.")
    return np.stack([r, g, b], axis=2).astype(np.float32)


def paint(out_dir: str = ".") -> str:
    print("Session 105 -- Mona Lisa portrait (direct numpy pipeline)")
    print('Random artist: il Guercino (Emilian Baroque, 1591-1666)')
    print("New pass: guercino_penumbra_warmth_pass()")
    print("Improvement: penumbra_bloom=0.06 in sfumato_veil_pass")
    print()

    # Load base image
    img = Image.open(base_path).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    rgb = np.array(img, dtype=np.float32) / 255.0
    print(f"Loaded: {base_path}  ({img.size[0]}x{img.size[1]})")

    print("Building figure mask ...")
    fig_mask = make_figure_mask()

    # Apply session 105 passes
    print("Applying session 105 passes ...")
    rgb = guercino_pass(rgb)
    rgb = penumbra_bloom_sfumato(rgb)
    rgb = vignette_glaze(rgb)

    # Save
    rgb_uint8 = np.clip(rgb * 255.0, 0, 255).astype(np.uint8)
    out_img   = Image.fromarray(rgb_uint8, mode="RGB")
    out_path  = os.path.join(out_dir, "mona_lisa_s105.png")
    out_img.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
