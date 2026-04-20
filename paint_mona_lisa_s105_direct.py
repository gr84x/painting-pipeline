"""
paint_mona_lisa_s105_direct.py

Loads the completed session-104 painting as a starting canvas and applies
only the session-105 additions on top of it.  Uses the loaded s104 PNG as
the reference (avoiding make_reference() rebuild), making this much faster.

Session 105 additions:
  1. guercino_penumbra_warmth_pass()     -- il Guercino, Emilian Baroque
  2. sfumato_veil with penumbra_bloom    -- session 105 improvement
  3. Final edge / varnish / glaze / finish
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from stroke_engine import Painter
from scipy.ndimage import gaussian_filter

W, H = 780, 1080

# Find the session-104 base painting
S104_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s104.png"),
    "/c/Source/painting-pipeline/.claude/worktrees/bold-bardeen/mona_lisa_s104.png",
    "C:/Source/painting-pipeline/.claude/worktrees/bold-bardeen/mona_lisa_s104.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bold-bardeen", "mona_lisa_s104.png"),
]

base_path = None
for c in S104_CANDIDATES:
    if os.path.exists(c):
        base_path = os.path.abspath(c)
        break

if base_path is None:
    raise FileNotFoundError(
        f"Cannot find mona_lisa_s104.png. Searched:\n" +
        "\n".join(f"  {c}" for c in S104_CANDIDATES)
    )

print(f"Loading session-104 base: {base_path}", flush=True)


def make_figure_mask() -> np.ndarray:
    mask = np.zeros((H, W), dtype=np.float32)
    cx, cy, rx, ry = 0.515 * W, 0.50 * H, 0.26 * W, 0.50 * H
    ys, xs = np.ogrid[:H, :W]
    d2 = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2
    mask[d2 <= 1.0] = 1.0
    mask = gaussian_filter(mask, sigma=18.0)
    mask = np.clip(mask / mask.max(), 0.0, 1.0)
    return mask


def load_png_into_painter(p: Painter, path: str) -> None:
    img = Image.open(path).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    rgb = np.array(img, dtype=np.uint8)
    bgra = np.zeros((H, W, 4), dtype=np.uint8)
    bgra[:, :, 0] = rgb[:, :, 2]   # B
    bgra[:, :, 1] = rgb[:, :, 1]   # G
    bgra[:, :, 2] = rgb[:, :, 0]   # R
    bgra[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = bgra.tobytes()


def paint(out_dir: str = ".") -> str:
    print("Session 105 direct painting (warm-start from s104)", flush=True)
    print("Applying: guercino_penumbra_warmth_pass + sfumato penumbra_bloom", flush=True)
    print(flush=True)

    # Load s104 as base canvas
    p = Painter(W, H)
    load_png_into_painter(p, base_path)
    p.set_figure_mask(make_figure_mask())

    # Use the s104 PNG directly as the sfumato reference
    print("Loading reference image...", flush=True)
    ref_img = Image.open(base_path).convert("RGB")
    if ref_img.size != (W, H):
        ref_img = ref_img.resize((W, H), Image.LANCZOS)

    # ── SESSION 105 NEW: Guercino penumbra warmth pass ───────────────────────
    print("Guercino penumbra warmth pass (session 105 -- NEW)...", flush=True)
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
    print("Sfumato veil pass with penumbra_bloom=0.06 (session 105)...", flush=True)
    p.sfumato_veil_pass(
        reference               = ref_img,
        n_veils                 = 3,
        veil_opacity            = 0.08,
        warmth                  = 0.32,
        shadow_warm_recovery    = 0.06,
        chroma_gate             = 0.42,
        highlight_ivory_lift    = 0.04,
        highlight_ivory_thresh  = 0.82,
        atmospheric_blue_shift  = 0.20,
        penumbra_bloom          = 0.06,
        penumbra_bloom_lo       = 0.30,
        penumbra_bloom_hi       = 0.60,
    )

    # ── Re-apply final passes ─────────────────────────────────────────────────
    print("Edge lost-and-found pass...", flush=True)
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

    print("Old-master varnish pass...", flush=True)
    p.old_master_varnish_pass(
        amber_strength  = 0.12,
        edge_darken     = 0.10,
        highlight_desat = 0.06,
        opacity         = 0.28,
    )

    print("Final glaze (warm amber)...", flush=True)
    p.glaze((0.58, 0.44, 0.16), opacity=0.034)

    print("Finishing (vignette + crackle)...", flush=True)
    p.finish(vignette=0.50, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s105.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}", flush=True)
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
