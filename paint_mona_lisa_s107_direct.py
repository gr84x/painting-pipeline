"""
paint_mona_lisa_s107_direct.py — Direct numpy-only painting for session 107.

Bypasses the Painter class (pycairo dependency) entirely.
Loads mona_lisa_s106.png and applies the session 107 Boltraffio additions
using pure numpy + PIL operations.

Use when the full paint_mona_lisa_s107.py encounters MemoryError or import
hangs due to concurrent background Python processes.
"""

import sys
import os
import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))

try:
    from scipy.ndimage import gaussian_filter as gf
except ImportError:
    # Fallback: simple Gaussian via PIL
    def gf(arr, sigma):
        img = Image.fromarray((arr * 255).astype(np.uint8))
        img = img.filter(ImageFilter.GaussianBlur(radius=sigma))
        return np.array(img, dtype=np.float32) / 255.0


W, H = 780, 1080

# ── Find base image ───────────────────────────────────────────────────────────
BASE_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "..", "mona_lisa_s106.png"),
    "C:/Source/painting-pipeline/mona_lisa_s106.png",
    "/c/Source/painting-pipeline/mona_lisa_s106.png",
]
base_path = None
for c in BASE_CANDIDATES:
    c = os.path.abspath(c)
    if os.path.exists(c):
        base_path = c
        break

if base_path is None:
    # Fall back to s101 if s106 not found
    for c in [
        "C:/Source/painting-pipeline/mona_lisa_s101.png",
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "..", "mona_lisa_s101.png"),
    ]:
        c = os.path.abspath(c)
        if os.path.exists(c):
            base_path = c
            print(f"  Note: using s101 base (s106 not found)", flush=True)
            break

if base_path is None:
    raise FileNotFoundError("Cannot find a base painting (s106 or s101).")

print(f"Loading base: {base_path}", flush=True)


# ── Load image ────────────────────────────────────────────────────────────────

img = Image.open(base_path).convert("RGB")
if img.size != (W, H):
    img = img.resize((W, H), Image.LANCZOS)

# Work in float32 [0, 1] RGB
rgb = np.array(img, dtype=np.float32) / 255.0
r = rgb[:, :, 0].copy()
g = rgb[:, :, 1].copy()
b = rgb[:, :, 2].copy()

print("Applying Boltraffio pearled sfumato pass (session 107)...", flush=True)


def boltraffio_pearled_sfumato(
    r, g, b,
    pearl_lo=0.72,
    pearl_r=0.010, pearl_g=0.015, pearl_b=0.022,
    shadow_hi=0.28,
    shadow_b=0.018, shadow_g=0.006, shadow_r=0.004,
    flesh_lo=0.40, flesh_hi=0.72,
    clarity_sigma=0.8, clarity_strength=0.14,
    blur_radius=4.0,
    opacity=0.32,
):
    """
    Pure numpy implementation of boltraffio_pearled_sfumato_pass().

    Three stages:
    1. Pearl highlight clarification — cool-silver push in high-lum zones
    2. Cool-blue deep shadow atmosphere — more pronounced blue in shadows
    3. Mid-flesh crystalline clarity — gentle unsharp mask in flesh zone
    """
    r0, g0, b0 = r.copy(), g.copy(), b.copy()
    r_out, g_out, b_out = r.copy(), g.copy(), b.copy()

    lum = 0.299 * r0 + 0.587 * g0 + 0.114 * b0

    # ── Stage 1: Pearl highlight clarification ────────────────────────────────
    # In highlight zones (lum > pearl_lo), shift toward cool silver-pearl.
    hi_mask = np.clip((lum - pearl_lo) / (1.0 - pearl_lo + 1e-6), 0.0, 1.0)
    hi_mask = gf(hi_mask.astype(np.float32), blur_radius)
    hi_mask = np.clip(hi_mask, 0.0, 1.0)
    r_out = np.clip(r_out + hi_mask * pearl_r, 0.0, 1.0)
    g_out = np.clip(g_out + hi_mask * pearl_g, 0.0, 1.0)
    b_out = np.clip(b_out + hi_mask * pearl_b, 0.0, 1.0)

    # ── Stage 2: Cool-blue deep shadow atmosphere ─────────────────────────────
    # In deep shadow zones (lum < shadow_hi), add cool-blue north-light quality.
    sh_mask = np.clip((shadow_hi - lum) / (shadow_hi + 1e-6), 0.0, 1.0)
    sh_mask = gf(sh_mask.astype(np.float32), blur_radius)
    sh_mask = np.clip(sh_mask, 0.0, 1.0)
    r_out = np.clip(r_out - sh_mask * shadow_r, 0.0, 1.0)
    g_out = np.clip(g_out + sh_mask * shadow_g, 0.0, 1.0)
    b_out = np.clip(b_out + sh_mask * shadow_b, 0.0, 1.0)

    # ── Stage 3: Mid-flesh crystalline clarity ────────────────────────────────
    # Unsharp mask at low strength in mid-flesh zone [flesh_lo, flesh_hi].
    flesh_bell = np.clip(
        (lum - flesh_lo) / (flesh_hi - flesh_lo + 1e-6), 0.0, 1.0
    ) * np.clip(
        (flesh_hi - lum) / (flesh_hi - flesh_lo + 1e-6), 0.0, 1.0
    ) * 4.0
    flesh_bell = np.clip(flesh_bell, 0.0, 1.0)
    flesh_bell = gf(flesh_bell.astype(np.float32), blur_radius)
    flesh_bell = np.clip(flesh_bell, 0.0, 1.0)

    r_blur = gf(r_out.astype(np.float32), clarity_sigma)
    g_blur = gf(g_out.astype(np.float32), clarity_sigma)
    b_blur = gf(b_out.astype(np.float32), clarity_sigma)

    cw = flesh_bell * clarity_strength
    r_out = np.clip(r_out + (r_out - r_blur) * cw, 0.0, 1.0)
    g_out = np.clip(g_out + (g_out - g_blur) * cw, 0.0, 1.0)
    b_out = np.clip(b_out + (b_out - b_blur) * cw, 0.0, 1.0)

    # ── Composite at opacity ──────────────────────────────────────────────────
    r_f = r0 * (1.0 - opacity) + r_out * opacity
    g_f = g0 * (1.0 - opacity) + g_out * opacity
    b_f = b0 * (1.0 - opacity) + b_out * opacity
    return r_f, g_f, b_f


r, g, b = boltraffio_pearled_sfumato(r, g, b)
print("  Pearl highlight clarification: done", flush=True)
print("  Cool-blue shadow atmosphere: done", flush=True)
print("  Mid-flesh crystalline clarity: done", flush=True)

# ── Save ──────────────────────────────────────────────────────────────────────

out_rgb = np.stack([r, g, b], axis=2)
out_rgb = np.clip(out_rgb * 255.0, 0, 255).astype(np.uint8)
out_img = Image.fromarray(out_rgb)

# Gentle final warm amber glaze (consistent with cumulative sessions)
# Very subtle — just to maintain warm amber unity of the series
print("Final warm amber glaze...", flush=True)
warm = np.array(out_img, dtype=np.float32) / 255.0
amber = np.array([0.58, 0.44, 0.16], dtype=np.float32)
warm = warm * (1 - 0.034) + amber * 0.034
warm = np.clip(warm * 255, 0, 255).astype(np.uint8)
out_img = Image.fromarray(warm)

# Save to main painting directory
out_dir = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."
))
out_path = os.path.join(out_dir, "mona_lisa_s107.png")
out_img.save(out_path)
print(f"\nPainting complete: {out_path}", flush=True)
print(f"Dimensions: {out_img.size}", flush=True)
