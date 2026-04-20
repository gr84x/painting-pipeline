"""
paint_mona_lisa_s105_warmstart.py

Loads the completed session-104 painting as a starting canvas and applies
only the session-105 additions on top of it.  This avoids re-running all
104 prior passes and lets the session-105 contribution stand alone.

Session 105 additions:
  1. guercino_penumbra_warmth_pass()   -- il Guercino, Emilian Baroque
  2. sfumato_veil_pass with penumbra_bloom=0.06  (session 105 improvement)
  3. Final edge / varnish / glaze / finish  (reapplied to seal the new pass)
"""

import sys
import os
import math
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image, ImageFilter
from stroke_engine import Painter
from scipy.ndimage import gaussian_filter

# ── Configuration ────────────────────────────────────────────────────────────
W, H = 780, 1080

# Find the session-104 base painting.
S104_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), "mona_lisa_s104.png"),
    os.path.join(
        os.path.dirname(__file__),
        "..", "bold-bardeen", "mona_lisa_s104.png"
    ),
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".claude", "worktrees", "bold-bardeen", "mona_lisa_s104.png"
    ),
    # Main repo root
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "mona_lisa_s104.png"
    ),
]

base_path = None
for c in S104_CANDIDATES:
    p_abs = os.path.abspath(c)
    if os.path.exists(p_abs):
        base_path = p_abs
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s104.png. "
        f"Searched: {S104_CANDIDATES}"
    )

print(f"Loading session-104 base: {base_path}")


def make_figure_mask() -> np.ndarray:
    """Figure mask for the standard Mona Lisa composition."""
    mask = np.zeros((H, W), dtype=np.float32)
    cx   = 0.515 * W
    cy   = 0.50  * H
    rx   = 0.26  * W
    ry   = 0.50  * H
    ys, xs = np.ogrid[:H, :W]
    d2  = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2
    mask[d2 <= 1.0] = 1.0
    mask = gaussian_filter(mask, sigma=18.0)
    mask = np.clip(mask / mask.max(), 0.0, 1.0)
    return mask


def make_reference() -> Image.Image:
    """Rebuild the synthetic reference for sfumato_veil_pass."""
    ref = Image.new("RGB", (W, H), (110, 100, 72))
    px  = ref.load()

    def horizon_y(x: int) -> int:
        return int(0.54 * H - 8 * (x / W - 0.5))

    for y in range(H):
        for x in range(W):
            hy = horizon_y(x)
            if y < hy:
                t = (hy - y) / max(hy, 1)
                r = int(130 + 60 * t)
                g = int(140 + 50 * t)
                b = int(155 + 60 * t)
            else:
                t = (y - hy) / max(H - hy, 1)
                r = int(120 - 30 * t)
                g = int(110 - 25 * t)
                b = int(80  - 20 * t)
            px[x, y] = (
                min(255, max(0, r)),
                min(255, max(0, g)),
                min(255, max(0, b)),
            )

    def in_torso(x, y):
        cx_t = 0.515 * W
        top  = 0.38 * H
        bot  = H
        rx_t = 0.16 * W
        rx_b = 0.22 * W
        if y < top or y > bot:
            return False
        t    = (y - top) / (bot - top)
        rx   = rx_t + (rx_b - rx_t) * t
        return abs(x - cx_t) <= rx

    for y in range(H):
        for x in range(W):
            if in_torso(x, y):
                px[x, y] = (28, 52, 45)

    face_cx = int(0.515 * W)
    face_cy = int(0.215 * H)
    face_rx = int(0.105 * W)
    face_ry = int(0.155 * H)

    def paint_skin_ellipse(cx, cy, rx, ry, lit_dir=(0.35, -0.70)):
        for y in range(cy - ry - 2, cy + ry + 2):
            for x in range(cx - rx - 2, cx + rx + 2):
                if not (0 <= x < W and 0 <= y < H):
                    continue
                nx = (x - cx) / rx
                ny = (y - cy) / ry
                d  = math.sqrt(nx * nx + ny * ny)
                if d > 1.0:
                    continue
                dot    = nx * lit_dir[0] + ny * lit_dir[1]
                light  = 0.55 + 0.45 * max(dot, 0.0)
                base_r = 215
                base_g = 175
                base_b = 130
                r = int(base_r * light)
                g = int(base_g * light)
                b = int(base_b * light)
                alpha  = min(1.0, (1.0 - d) * 4.0)
                old_r, old_g, old_b = px[x, y]
                px[x, y] = (
                    min(255, max(0, int(old_r * (1 - alpha) + r * alpha))),
                    min(255, max(0, int(old_g * (1 - alpha) + g * alpha))),
                    min(255, max(0, int(old_b * (1 - alpha) + b * alpha))),
                )

    paint_skin_ellipse(face_cx, face_cy, face_rx, face_ry)
    paint_skin_ellipse(
        int(0.515 * W), int(0.355 * H),
        int(0.058 * W), int(0.085 * H),
        lit_dir=(0.30, -0.60),
    )
    paint_skin_ellipse(
        int(0.515 * W), int(0.42 * H),
        int(0.095 * W), int(0.052 * H),
        lit_dir=(0.28, -0.55),
    )
    paint_skin_ellipse(
        int(0.48 * W), int(0.82 * H),
        int(0.082 * W), int(0.048 * H),
        lit_dir=(0.25, -0.50),
    )
    paint_skin_ellipse(
        int(0.53 * W), int(0.855 * H),
        int(0.080 * W), int(0.042 * H),
        lit_dir=(0.25, -0.50),
    )
    return ref.filter(ImageFilter.GaussianBlur(radius=3))


def load_png_into_painter(p: Painter, path: str) -> None:
    """Load a PNG image into the Painter canvas buffer (Cairo BGRA)."""
    img = Image.open(path).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    rgb = np.array(img, dtype=np.uint8)

    bgra = np.zeros((H, W, 4), dtype=np.uint8)
    bgra[:, :, 0] = rgb[:, :, 2]   # B
    bgra[:, :, 1] = rgb[:, :, 1]   # G
    bgra[:, :, 2] = rgb[:, :, 0]   # R
    bgra[:, :, 3] = 255             # A

    p.canvas.surface.get_data()[:] = bgra.tobytes()


def paint(out_dir: str = ".") -> str:
    print("Session 105 warm-start painting")
    print('Applying: guercino_penumbra_warmth_pass + sfumato_veil penumbra_bloom')
    print()

    # Create painter and load s104 as base
    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # Build reference for sfumato_veil_pass
    print("Building synthetic reference...")
    ref = make_reference()

    # ── SESSION 105 NEW: Guercino penumbra warmth pass ───────────────────────
    print("Guercino penumbra warmth pass (session 105 -- NEW)...")
    p.guercino_penumbra_warmth_pass(
        penumbra_lo         = 0.28,
        penumbra_hi         = 0.62,
        amber_r             = 0.038,
        amber_g             = 0.018,
        amber_b             = 0.008,
        light_cx            = 0.18,
        light_cy            = 0.08,
        light_radius        = 0.85,
        directional_str     = 0.018,
        shadow_lo           = 0.05,
        shadow_hi           = 0.28,
        shadow_warm_r       = 0.022,
        shadow_warm_g       = 0.008,
        blur_radius         = 4.5,
        opacity             = 0.28,
    )

    # ── SESSION 105 IMPROVEMENT: sfumato_veil with penumbra_bloom ────────────
    print("Sfumato veil pass (s105 -- penumbra_bloom=0.06)...")
    p.sfumato_veil_pass(
        reference               = ref,
        n_veils                 = 3,
        veil_opacity            = 0.08,
        warmth                  = 0.32,
        shadow_warm_recovery    = 0.06,
        chroma_gate             = 0.42,
        highlight_ivory_lift    = 0.04,
        highlight_ivory_thresh  = 0.82,
        atmospheric_blue_shift  = 0.20,
        penumbra_bloom          = 0.06,   # session 105 improvement
        penumbra_bloom_lo       = 0.30,
        penumbra_bloom_hi       = 0.60,
    )

    # ── Re-apply final passes to seal the new contribution ───────────────────
    print("Edge lost-and-found pass (re-seal)...")
    p.edge_lost_and_found_pass(
        focal_xy             = (0.515, 0.195),
        found_radius         = 0.28,
        found_sharpness      = 0.48,
        lost_blur            = 2.0,
        strength             = 0.34,
        figure_only          = True,
        gradient_selectivity = 0.65,
        soft_halo_strength   = 0.14,
    )

    print("Old-master varnish pass (re-seal)...")
    p.old_master_varnish_pass(
        amber_strength  = 0.12,
        edge_darken     = 0.10,
        highlight_desat = 0.06,
        opacity         = 0.28,
    )

    print("Final glaze (warm amber)...")
    p.glaze((0.58, 0.44, 0.16), opacity=0.034)

    print("Finishing (vignette + crackle)...")
    p.finish(vignette=0.50, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s105.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
