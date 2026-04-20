"""
paint_mona_lisa_s104_direct.py

Applies session-104 passes directly via numpy/PIL on top of the session-103
painting — bypasses the Painter class entirely to avoid the slow linen-texture
initialization (pure-Python Perlin noise over 842K pixels).

Session-104 additions applied:
  1. giordano_rapidita_luminosa_pass  -- Luca Giordano, Neapolitan Baroque
  2. zenith_luminance_boost           -- atmospheric_depth_pass improvement
  3. Gentle vignette + warm glaze     -- sealing finish
"""

import sys
import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(__file__))

W, H = 780, 1080

# ── Find the session-103 base painting ───────────────────────────────────────
CANDIDATES = [
    os.path.join(os.path.dirname(__file__), "mona_lisa_s103.png"),
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        ".claude", "worktrees", "charming-ramanujan", "mona_lisa_s103.png"
    ),
    r"C:\Source\painting-pipeline\.claude\worktrees\charming-ramanujan\mona_lisa_s103.png",
]

base_path = None
for c in CANDIDATES:
    if os.path.exists(c):
        base_path = os.path.abspath(c)
        break

if base_path is None:
    raise FileNotFoundError(
        f"Cannot find mona_lisa_s103.png. Searched:\n  " + "\n  ".join(CANDIDATES)
    )

print(f"Base image: {base_path}")


# ── Figure mask ───────────────────────────────────────────────────────────────
def make_figure_mask() -> np.ndarray:
    """Standard Mona Lisa figure mask — soft ellipse centred on the figure."""
    cx   = 0.515 * W
    cy   = 0.50  * H
    rx   = 0.26  * W
    ry   = 0.50  * H
    ys, xs = np.ogrid[:H, :W]
    d2  = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2
    mask = (d2 <= 1.0).astype(np.float32)
    mask = gaussian_filter(mask, sigma=18.0)
    mask = np.clip(mask / mask.max(), 0.0, 1.0)
    return mask


def giordano_pass(rgb: np.ndarray, fig_mask: np.ndarray) -> np.ndarray:
    """
    Luca Giordano rapidità luminosa pass.

    Three effects:
      1. Warm golden upper-right aureole in the background.
      2. Warm golden rim on the lit (upper-right) figure edges.
      3. Subtle cool-violet push in the deepest shadows.
    """
    print("  Giordano rapidità luminosa pass ...")
    r0, g0, b0 = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    lum = 0.299 * r0 + 0.587 * g0 + 0.114 * b0

    r_out = r0.copy()
    g_out = g0.copy()
    b_out = b0.copy()

    # Coordinate grids
    ys_f = np.arange(H, dtype=np.float32)[:, np.newaxis] / H
    xs_f = np.arange(W, dtype=np.float32)[np.newaxis, :] / W

    # 1. Upper-right golden aureole
    aureole_cx, aureole_cy = 0.88, 0.06
    aureole_radius = 0.72
    dist = np.sqrt((xs_f - aureole_cx) ** 2 + (ys_f - aureole_cy) ** 2).astype(np.float32)
    aureole_mask = np.exp(-0.5 * (dist / aureole_radius) ** 2)

    bg_weight  = 1.0 - fig_mask
    fig_weight = fig_mask * 0.30
    combined   = bg_weight + fig_weight

    r_out = np.clip(r_out + aureole_mask * combined * 0.052, 0.0, 1.0)
    g_out = np.clip(g_out + aureole_mask * combined * 0.028, 0.0, 1.0)
    b_out = np.clip(b_out + aureole_mask * combined * 0.007, 0.0, 1.0)

    # 2. Warm golden rim on lit figure edges
    fig_smooth = gaussian_filter(fig_mask, sigma=3.0)
    fig_edge   = np.clip(fig_mask - fig_smooth, 0.0, 1.0)
    fig_edge   = gaussian_filter(fig_edge.astype(np.float32), sigma=2.0)
    upper_right_weight = np.clip((1.0 - ys_f) * 0.5 + xs_f * 0.5, 0.0, 1.0).astype(np.float32)
    rim_mask   = np.clip(fig_edge * upper_right_weight, 0.0, 1.0)
    rim_strength = 0.040

    r_out = np.clip(r_out + rim_mask * rim_strength * 1.4, 0.0, 1.0)
    g_out = np.clip(g_out + rim_mask * rim_strength * 0.9, 0.0, 1.0)
    b_out = np.clip(b_out + rim_mask * rim_strength * 0.3, 0.0, 1.0)

    # 3. Shadow violet depth
    shadow_hi  = 0.30
    shadow_band = np.clip((shadow_hi - lum) / (shadow_hi + 1e-6), 0.0, 1.0)
    shadow_band = gaussian_filter(shadow_band.astype(np.float32), sigma=5.0)
    b_out = np.clip(b_out + shadow_band * 0.013, 0.0, 1.0)
    r_out = np.clip(r_out + shadow_band * 0.005, 0.0, 1.0)

    # Composite at opacity=0.30
    opacity = 0.30
    r_final = r0 * (1.0 - opacity) + r_out * opacity
    g_final = g0 * (1.0 - opacity) + g_out * opacity
    b_final = b0 * (1.0 - opacity) + b_out * opacity

    out = np.stack([r_final, g_final, b_final], axis=2).astype(np.float32)
    print("  Giordano pass complete.")
    return out


def zenith_boost_pass(rgb: np.ndarray, fig_mask: np.ndarray) -> np.ndarray:
    """
    Session 104 improvement: zenith luminance boost in the background sky zone.

    Lifts luminance at the very top of the canvas with a cool-blue cerulean bias,
    simulating the brilliant open sky of Giordano's ceiling compositions.
    """
    print("  Zenith luminance boost pass ...")
    r0, g0, b0 = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]

    bg_weight = 1.0 - fig_mask

    zenith_sigma_px = max(0.10 * H, 1.0)
    row_dist_z = np.arange(H, dtype=np.float32) / zenith_sigma_px
    zenith_profile = np.exp(-0.5 * row_dist_z ** 2)[:, np.newaxis]  # (H, 1)
    zenith_weight  = zenith_profile * bg_weight * 0.09

    zenith_color = np.array([0.88, 0.92, 0.98], dtype=np.float32)
    r_final = r0 * (1.0 - zenith_weight * 0.45) + zenith_color[0] * (zenith_weight * 0.45)
    g_final = g0 * (1.0 - zenith_weight * 0.45) + zenith_color[1] * (zenith_weight * 0.45)
    b_final = b0 * (1.0 - zenith_weight * 0.45) + zenith_color[2] * (zenith_weight * 0.45)
    r_final = np.clip(r_final + zenith_weight * 0.06, 0.0, 1.0)
    g_final = np.clip(g_final + zenith_weight * 0.06, 0.0, 1.0)
    b_final = np.clip(b_final + zenith_weight * 0.06, 0.0, 1.0)

    out = np.stack([r_final, g_final, b_final], axis=2).astype(np.float32)
    print("  Zenith boost complete.")
    return out


def vignette_glaze(rgb: np.ndarray) -> np.ndarray:
    """Gentle vignette + warm amber glaze to seal the painting."""
    print("  Vignette + glaze ...")
    ys_f = np.arange(H, dtype=np.float32)[:, np.newaxis] / H
    xs_f = np.arange(W, dtype=np.float32)[np.newaxis, :] / W

    # Vignette: darken toward corners
    cx, cy = 0.5, 0.5
    dist   = np.sqrt(((xs_f - cx) * 1.3) ** 2 + ((ys_f - cy) * 1.1) ** 2)
    vig    = np.clip(1.0 - dist * 0.50 * 0.50, 0.5, 1.0).astype(np.float32)

    r = np.clip(rgb[:, :, 0] * vig, 0.0, 1.0)
    g = np.clip(rgb[:, :, 1] * vig, 0.0, 1.0)
    b = np.clip(rgb[:, :, 2] * vig, 0.0, 1.0)

    # Warm amber glaze
    glaze_r, glaze_g, glaze_b = 0.58, 0.44, 0.16
    alpha = 0.034
    r = np.clip(r * (1 - alpha) + glaze_r * alpha, 0.0, 1.0)
    g = np.clip(g * (1 - alpha) + glaze_g * alpha, 0.0, 1.0)
    b = np.clip(b * (1 - alpha) + glaze_b * alpha, 0.0, 1.0)

    print("  Vignette + glaze complete.")
    return np.stack([r, g, b], axis=2).astype(np.float32)


def paint(out_dir: str = ".") -> str:
    print("Session 104 -- Mona Lisa portrait (direct numpy pipeline)")
    print('Random artist: Luca Giordano "Fa Presto" (Neapolitan Baroque, 1634-1705)')
    print("New pass: giordano_rapidita_luminosa_pass()")
    print("Improvement: zenith_luminance_boost in atmospheric_depth_pass")
    print()

    # Load base image
    img = Image.open(base_path).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    rgb = np.array(img, dtype=np.float32) / 255.0
    print(f"Loaded: {base_path}  ({img.size[0]}x{img.size[1]})")

    # Build figure mask
    print("Building figure mask ...")
    fig_mask = make_figure_mask()

    # Apply session-104 passes
    rgb = giordano_pass(rgb, fig_mask)
    rgb = zenith_boost_pass(rgb, fig_mask)
    rgb = vignette_glaze(rgb)

    # Save
    out = np.clip(rgb * 255.0, 0, 255).astype(np.uint8)
    result = Image.fromarray(out, "RGB")
    out_path = os.path.join(out_dir, "mona_lisa_s104.png")
    result.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
