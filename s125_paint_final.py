"""Session 125 final — post-process v7 output: canvas unification and blur."""
import sys, os, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load the v7 output as starting point
src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s125_portrait_v7.png")
canvas = np.array(Image.open(src)).astype(np.float32) / 255.0  # H W 3

H, W = canvas.shape[:2]

# ── Soft unified blur — simulate the atmospheric unity of sfumato ─────────────
# Apply mild Gaussian to entire canvas: blends hard edges between elements
unified = canvas.copy()
for c in range(3):
    unified[:, :, c] = gaussian_filter(unified[:, :, c], sigma=1.2)

# Blend: keep sharpness in face, apply blur everywhere else
fig_cx = int(W * 0.515)
fcx, fcy = fig_cx + 4, int(H * 0.244)
frx, fry = 88, 112

ys_g, xs_g = np.mgrid[0:H, 0:W]
face_dist = ((xs_g - fcx) / (frx*1.6))**2 + ((ys_g - fcy) / (fry*1.6))**2
# 0 = inside face zone (keep sharp), 1 = outside (apply blur)
blur_weight = np.clip(face_dist - 0.6, 0.0, 1.0) / 0.6
blur_weight = np.clip(blur_weight, 0, 1)

for c in range(3):
    canvas[:, :, c] = canvas[:, :, c] * (1 - blur_weight * 0.55) + unified[:, :, c] * blur_weight * 0.55

# ── Strengthen hair/veil-to-background transition with sfumato blur ───────────
# The hair area above face tends to have hard edges — soften them
hair_region_y = slice(max(0, fcy-fry-30), fcy+20)
for c in range(3):
    hr = canvas[hair_region_y, :, c].copy()
    canvas[hair_region_y, :, c] = gaussian_filter(hr, sigma=1.8)

# ── Final warm glaze over entire canvas to unify tonality ─────────────────────
# Leonardo's warm umber unification
glaze_r, glaze_g, glaze_b = 0.62, 0.50, 0.28
opacity = 0.038
canvas[:, :, 0] = np.clip(canvas[:, :, 0] * (1-opacity) + glaze_r * opacity, 0, 1)
canvas[:, :, 1] = np.clip(canvas[:, :, 1] * (1-opacity) + glaze_g * opacity, 0, 1)
canvas[:, :, 2] = np.clip(canvas[:, :, 2] * (1-opacity) + glaze_b * opacity, 0, 1)

# ── Vignette — gentle oval darkening at corners ───────────────────────────────
vx = (xs_g / W - 0.5) * 2
vy = (ys_g / H - 0.5) * 2
vignette = np.clip((vx**2 + vy**2) ** 0.5, 0, 1) ** 1.8
vignette_strength = 0.28
for c in range(3):
    canvas[:, :, c] = np.clip(canvas[:, :, c] * (1 - vignette * vignette_strength), 0, 1)

# ── Slightly boost face luminosity ───────────────────────────────────────────
# Face area should be the brightest element — add a gentle lift
face_glow = np.clip(1.0 - face_dist * 0.6, 0, 1)
face_glow = gaussian_filter(face_glow.astype(np.float32), sigma=20.0)
face_glow = np.clip(face_glow, 0, 1) * 0.06   # very subtle
for c in range(3):
    canvas[:, :, c] = np.clip(canvas[:, :, c] + face_glow, 0, 1)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s125_portrait_final.png")
result = Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8), "RGB")
result.save(out)
print(f"Saved: {out}")
