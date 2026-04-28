"""
quick_s91.py -- Session 91 quick-apply script.

Loads mona_lisa_s90.png into a Painter canvas and applies only the NEW
session 91 additions, avoiding the expensive stroke pipeline that causes
MemoryError on the 780x1080 canvas.

New passes applied:
  - franz_marc_prismatic_vitality_pass()  (new artist, s91)
  - cool_atmospheric_recession_pass(warm_ground_glow=0.12, cool_strength=0,
      bright_lift=0, desaturate=0, blur_background=0)
    -- warm ground glow only; recession was already applied in s90.

Output: mona_lisa_s91.png
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
import cairo
from stroke_engine import Painter

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
S90_PATH = os.path.join(REPO_DIR, "mona_lisa_s90.png")
OUT_PATH = os.path.join(REPO_DIR, "mona_lisa_s91.png")


def make_figure_mask(W: int, H: int) -> np.ndarray:
    """Float32 (H, W) mask: 1.0=figure, 0.0=background."""
    mask = np.zeros((H, W), dtype=np.float32)

    face_cx = W // 2 + 8
    face_cy = int(H * 0.215)
    face_rx = int(W * 0.138)
    face_ry = int(H * 0.185)
    for y in range(max(0, face_cy - face_ry - 10), min(H, face_cy + face_ry + 10)):
        for x in range(max(0, face_cx - face_rx - 10), min(W, face_cx + face_rx + 10)):
            dx = (x - face_cx) / face_rx
            dy = (y - face_cy) / face_ry
            if dx * dx + dy * dy <= 1.1:
                mask[y, x] = 1.0

    for y in range(int(H * 0.36), H):
        t = (y - H * 0.36) / (H - H * 0.36)
        hw = int(W * (0.20 + 0.14 * t))
        cx = W // 2
        x0 = max(0, cx - hw)
        x1 = min(W, cx + hw)
        mask[y, x0:x1] = 1.0

    from scipy.ndimage import gaussian_filter
    mask = np.clip(gaussian_filter(mask, sigma=12.0), 0.0, 1.0)
    return mask


def load_png_into_painter(p: Painter, path: str) -> None:
    """Load a PNG file directly into the Painter's Cairo canvas."""
    img = Image.open(path).convert("RGB")
    W, H = img.size
    assert W == p.w and H == p.h, f"Size mismatch: PNG={W}x{H}, Painter={p.w}x{p.h}"

    arr_rgb = np.array(img, dtype=np.uint8)
    arr_bgra = np.zeros((H, W, 4), dtype=np.uint8)
    arr_bgra[:, :, 0] = arr_rgb[:, :, 2]   # B <- R
    arr_bgra[:, :, 1] = arr_rgb[:, :, 1]   # G <- G
    arr_bgra[:, :, 2] = arr_rgb[:, :, 0]   # R <- B  (Cairo BGRA)
    arr_bgra[:, :, 3] = 255

    surface = cairo.ImageSurface.create_for_data(
        bytearray(arr_bgra.tobytes()), cairo.FORMAT_ARGB32, W, H)
    p.canvas.ctx.set_source_surface(surface, 0, 0)
    p.canvas.ctx.paint()


def paint() -> str:
    print("Session 91 quick-apply -- loading mona_lisa_s90.png")
    print("New artist: Franz Marc (German Expressionism / Der Blaue Reiter, 1880-1916)")
    print("New pass:   franz_marc_prismatic_vitality_pass()")
    print("New param:  cool_atmospheric_recession_pass(warm_ground_glow=0.12)")
    print()

    s90 = Image.open(S90_PATH)
    W, H = s90.size
    print(f"Canvas: {W} x {H}")

    p = Painter(W, H)

    print("Loading s90 image into canvas...")
    load_png_into_painter(p, S90_PATH)

    print("Setting figure mask...")
    p.set_figure_mask(make_figure_mask(W, H))

    # -- SESSION 91: Franz Marc prismatic vitality pass (NEW) -----------------
    print("Franz Marc prismatic vitality pass (session 91 -- NEW)...")
    p.franz_marc_prismatic_vitality_pass(
        blue_push        = 0.14,
        yellow_push      = 0.10,
        red_deepen       = 0.08,
        bloom_thresh     = 0.42,
        bloom_sigma      = 3.0,
        bloom_strength   = 0.12,
        sat_boost_lo     = 0.32,
        sat_boost_hi     = 0.74,
        sat_boost_amount = 0.18,
        sat_boost_thresh = 0.16,
        blur_radius      = 3.5,
        opacity          = 0.28,
    )

    # -- SESSION 91: warm_ground_glow (new parameter) -------------------------
    # Apply ONLY the warm glow; set all recession effects to 0 to avoid
    # double-applying the atmospheric recession that was already in s90.
    print("Cool atmospheric recession -- warm_ground_glow ONLY (session 91 improvement)...")
    p.cool_atmospheric_recession_pass(
        horizon_y                 = 0.54,
        cool_strength             = 0.0,    # already applied in s90
        bright_lift               = 0.0,    # already applied in s90
        desaturate                = 0.0,    # already applied in s90
        blur_background           = 0.0,    # already applied in s90
        feather                   = 0.12,
        opacity                   = 0.65,
        lateral_horizon_asymmetry = 0.06,   # same as s90
        warm_ground_glow          = 0.12,   # NEW: warm amber near horizon
    )

    # Old-master varnish finalisation
    print("Old-master varnish pass...")
    p.old_master_varnish_pass(
        amber_strength  = 0.12,
        edge_darken     = 0.10,
        highlight_desat = 0.06,
        opacity         = 0.28,
    )

    # Final warm amber glaze
    print("Final glaze (warm amber)...")
    p.glaze((0.58, 0.44, 0.16), opacity=0.034)

    # Finish (vignette + crackle)
    print("Finishing (vignette + crackle)...")
    p.finish(vignette=0.50, crackle=True)

    p.save(OUT_PATH)
    print(f"\nPainting complete: {OUT_PATH}")
    return OUT_PATH


if __name__ == "__main__":
    paint()
