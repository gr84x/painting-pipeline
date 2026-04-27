"""
run_rothko_color_field.py — Session 213

Paints a Mark Rothko-inspired colour-field canvas: three luminous horizontal
fields — a deep cadmium-red sky descending into a brooding crimson mesa horizon,
which dissolves into a warm ochre-earth ground below.  No foreground objects,
no narrative: only the relationship between the three fields of colour and the
charged zones where they exhale into each other.

The canvas is wide and approximately square, intended to be experienced at
close range where peripheral vision fills entirely with colour and the painted
fields lose their objecthood.  The Rothko pass amplifies each band's dominant
hue and dissolves the interband boundaries through a sigmoid-weighted gradient,
producing the characteristic 'breathing' edge — the defining quality of every
Rothko.

Session 213 pass used:
  rothko_color_field_pass  (124th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "rothko_color_field.png"
)
W, H = 900, 780   # wide, nearly square — Rothko's preferred format


def build_reference() -> np.ndarray:
    """
    Synthetic reference for the Rothko three-field colour composition.

    Zones (top to bottom):
      - Upper field (40%): deep cadmium red → burnt orange gradient
      - Middle field (30%): dark crimson mesa silhouette with violet undertone
      - Lower field (30%): warm ochre-earth ground fading to sienna
    Each zone has subtle tonal variation to give the Rothko pass differentiated
    material to amplify and dissolve.
    """
    rng = np.random.default_rng(213)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # Band boundaries
    y_upper = 0.40   # top of middle band
    y_lower = 0.70   # top of lower band

    # ── Upper field: deep cadmium red → burnt orange ─────────────────────────
    t_up = np.clip(ys / y_upper, 0.0, 1.0)   # 0 = top, 1 = upper/mid boundary
    upper_r = 0.70 + 0.12 * t_up             # red darkens slightly at top
    upper_g = 0.06 + 0.18 * t_up             # a little more warmth toward boundary
    upper_b = 0.04 + 0.02 * t_up
    # Subtle horizontal colour wash variation
    wash_x = rng.standard_normal((1, W)).astype(np.float32) * 0.04
    wash_y = rng.standard_normal((H, 1)).astype(np.float32) * 0.03
    upper_r = np.clip(upper_r + wash_x + wash_y, 0.0, 1.0)
    upper_g = np.clip(upper_g + wash_y * 0.6, 0.0, 1.0)
    upper_b = np.clip(upper_b + wash_x * 0.4, 0.0, 1.0)

    mask_up = ys < y_upper
    ref[:, :, 0] = np.where(mask_up, upper_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(mask_up, upper_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(mask_up, upper_b, ref[:, :, 2])

    # ── Middle field: dark crimson with violet-black undertone ───────────────
    t_mid = np.clip((ys - y_upper) / (y_lower - y_upper), 0.0, 1.0)
    mid_r = 0.48 - 0.08 * t_mid             # darkens toward lower boundary
    mid_g = 0.04 + 0.02 * t_mid
    mid_b = 0.06 + 0.06 * t_mid             # slight violet lift
    wash2_x = rng.standard_normal((1, W)).astype(np.float32) * 0.03
    wash2_y = rng.standard_normal((H, 1)).astype(np.float32) * 0.025
    mid_r = np.clip(mid_r + wash2_x + wash2_y, 0.0, 1.0)
    mid_g = np.clip(mid_g + wash2_y * 0.5, 0.0, 1.0)
    mid_b = np.clip(mid_b + wash2_x * 0.5 + wash2_y * 0.3, 0.0, 1.0)

    mask_mid = (ys >= y_upper) & (ys < y_lower)
    ref[:, :, 0] = np.where(mask_mid, mid_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(mask_mid, mid_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(mask_mid, mid_b, ref[:, :, 2])

    # ── Lower field: warm ochre-earth → deep sienna ──────────────────────────
    t_lo = np.clip((ys - y_lower) / (1.0 - y_lower), 0.0, 1.0)
    low_r = 0.62 - 0.14 * t_lo             # ochre lightens near mid boundary
    low_g = 0.36 - 0.12 * t_lo
    low_b = 0.10 - 0.04 * t_lo
    wash3_x = rng.standard_normal((1, W)).astype(np.float32) * 0.03
    wash3_y = rng.standard_normal((H, 1)).astype(np.float32) * 0.025
    low_r = np.clip(low_r + wash3_x + wash3_y, 0.0, 1.0)
    low_g = np.clip(low_g + wash3_y * 0.6, 0.0, 1.0)
    low_b = np.clip(low_b + wash3_x * 0.3, 0.0, 1.0)

    mask_lo = ys >= y_lower
    ref[:, :, 0] = np.where(mask_lo, low_r, ref[:, :, 0])
    ref[:, :, 1] = np.where(mask_lo, low_g, ref[:, :, 1])
    ref[:, :, 2] = np.where(mask_lo, low_b, ref[:, :, 2])

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Build the Rothko colour-field painting and save to OUTPUT."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H)

    # Deep warm ground — Rothko's characteristic dark imprimatura
    p.tone_ground((0.18, 0.10, 0.06), texture_strength=0.06)

    # Underpainting: broad horizontal sweeps of raw colour
    p.underpainting(ref_pil, stroke_size=52, dry_amount=0.80)

    # Block in: soft, large colour planes — no detail, just mass
    p.block_in(ref_pil, stroke_size=38, dry_amount=0.55)

    # Rothko colour-field pass: amplify bands, dissolve boundaries, add depth veil
    p.rothko_color_field_pass(
        n_bands=3,
        hue_strength=0.68,
        edge_sigma=28.0,
        veil_factor=0.88,
        opacity=0.80,
    )

    p.finish()
    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
