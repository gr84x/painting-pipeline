"""
paint_mona_lisa_s104_warmstart.py

Loads the completed session-103 painting as a starting canvas and applies
only the session-104 additions on top of it.  This avoids re-running all
103 prior passes and lets the session-104 contribution stand alone.

Session 104 additions:
  1. giordano_rapidita_luminosa_pass()   -- Luca Giordano, Neapolitan Baroque
  2. atmospheric_depth_pass with zenith_luminance_boost=0.09  (already in s103;
     here we apply a delta pass that only adds the zenith boost to the s103 base)
  3. Final edge / varnish / glaze / finish  (reapplied to seal the new pass)
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
from scipy.ndimage import gaussian_filter

# ── Configuration ────────────────────────────────────────────────────────────
W, H = 780, 1080

# Find the session-103 base painting.
S103_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), "mona_lisa_s103.png"),
    os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", ".claude", "worktrees", "charming-ramanujan", "mona_lisa_s103.png"
    ),
]

base_path = None
for c in S103_CANDIDATES:
    if os.path.exists(c):
        base_path = os.path.abspath(c)
        break

if base_path is None:
    raise FileNotFoundError(
        "Cannot find mona_lisa_s103.png. "
        f"Searched: {S103_CANDIDATES}"
    )

print(f"Loading session-103 base: {base_path}")


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


def load_png_into_painter(p: Painter, path: str) -> None:
    """
    Load a PNG image into the Painter canvas buffer.

    Cairo uses BGRA format internally.  We open the PNG as RGB, convert to
    BGRA uint8, and write the bytes directly into the cairo surface buffer.
    """
    img = Image.open(path).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    rgb = np.array(img, dtype=np.uint8)   # (H, W, 3)  R, G, B

    # Build BGRA array
    bgra = np.zeros((H, W, 4), dtype=np.uint8)
    bgra[:, :, 0] = rgb[:, :, 2]   # B
    bgra[:, :, 1] = rgb[:, :, 1]   # G
    bgra[:, :, 2] = rgb[:, :, 0]   # R
    bgra[:, :, 3] = 255             # A

    p.canvas.surface.get_data()[:] = bgra.tobytes()


def paint(out_dir: str = ".") -> str:
    print("Session 104 warm-start painting")
    print('Applying: giordano_rapidita_luminosa_pass + zenith_luminance_boost')
    print()

    # Create painter and load s103 as base
    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # ── Session 104 NEW: Giordano rapidità luminosa pass ─────────────────────
    print("Luca Giordano rapidità luminosa pass (session 104 -- NEW)...")
    p.giordano_rapidita_luminosa_pass(
        aureole_cx          = 0.88,
        aureole_cy          = 0.06,
        aureole_radius      = 0.72,
        aureole_r           = 0.052,
        aureole_g           = 0.028,
        aureole_b           = 0.007,
        rim_strength        = 0.040,
        rim_sigma           = 3.0,
        shadow_hi           = 0.30,
        shadow_violet_b     = 0.013,
        shadow_violet_r     = 0.005,
        blur_radius         = 5.0,
        opacity             = 0.30,
    )

    # ── Session 104 IMPROVEMENT: zenith luminance boost ───────────────────────
    # Apply a narrow atmospheric depth pass that contributes only the zenith
    # boost — keeping desaturation/lightening very low so we don't disturb
    # the s103 background, only adding the Giordano ceiling-sky brightness.
    print("Atmospheric zenith luminance boost (session 104 improvement)...")
    p.atmospheric_depth_pass(
        haze_color              = (0.72, 0.78, 0.88),
        desaturation            = 0.04,     # tiny — avoid disturbing s103 atm depth
        lightening              = 0.03,     # tiny
        depth_gamma             = 1.6,
        background_only         = True,
        horizon_glow_band       = 0.0,      # already applied in s103
        zenith_luminance_boost  = 0.09,     # session 104 improvement
        zenith_band_sigma       = 0.10,
    )

    # ── Final sealing passes ──────────────────────────────────────────────────
    print("Edge lost-and-found pass (sealing)...")
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

    print("Old-master varnish pass...")
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

    out_path = os.path.join(out_dir, "mona_lisa_s104.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
