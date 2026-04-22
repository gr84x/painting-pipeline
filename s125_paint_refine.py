"""Session 125 refinement — dissolve the hair boundary into background."""
import sys, os, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s125_portrait_final.png")
canvas = np.array(Image.open(src)).astype(np.float32) / 255.0
H, W = canvas.shape[:2]

fig_cx = int(W * 0.515)
fcx, fcy = fig_cx + 4, int(H * 0.244)
frx, fry = 88, 112

ys_g, xs_g = np.mgrid[0:H, 0:W]

# ── Detect edges in the canvas and blur them in the hair region ───────────────
# Hair zone: above the face shoulder line
hair_y0 = max(0, fcy - fry - 35)
hair_y1 = fcy + 30
hair_x0 = max(0, fcx - frx - 50)
hair_x1 = min(W, fcx + frx + 50)

# In the hair zone, apply strong edge-softening
hair_chunk = canvas[hair_y0:hair_y1, hair_x0:hair_x1].copy()
# Blur strongly to dissolve hard edges
for c in range(3):
    hair_chunk[:, :, c] = gaussian_filter(hair_chunk[:, :, c], sigma=4.5)

# Re-apply but preserve face area (face should stay sharp)
face_dist_crop = ((xs_g[hair_y0:hair_y1, hair_x0:hair_x1] - fcx) / (frx * 1.1))**2 + \
                 ((ys_g[hair_y0:hair_y1, hair_x0:hair_x1] - fcy) / (fry * 1.1))**2
# Outside face: blend strongly; inside face: keep original
outside_face = np.clip((face_dist_crop - 0.55) / 0.35, 0, 1)
outside_face_3d = outside_face[:, :, np.newaxis]

canvas[hair_y0:hair_y1, hair_x0:hair_x1] = (
    canvas[hair_y0:hair_y1, hair_x0:hair_x1] * (1 - outside_face_3d * 0.60) +
    hair_chunk * outside_face_3d * 0.60
)

# ── Blur the figure/background boundary all around ───────────────────────────
# Create a soft edge mask — high at edges of the figure, 0 in center and background
# Use the gradient of a distance field
fig_dist = ((xs_g - fig_cx) / 220)**2 + ((ys_g - (fcy + 200)) / 380)**2
# Edge zone: 0.7 to 1.1 in dist
edge_zone = np.clip((fig_dist - 0.65) / 0.45, 0, 1) * np.clip((1.30 - fig_dist) / 0.45, 0, 1)

blurred = canvas.copy()
for c in range(3):
    blurred[:, :, c] = gaussian_filter(canvas[:, :, c], sigma=3.0)

for c in range(3):
    canvas[:, :, c] = canvas[:, :, c] * (1 - edge_zone * 0.45) + blurred[:, :, c] * edge_zone * 0.45

# ── Strengthen the face luminosity relative to surroundings ──────────────────
face_dist_full = ((xs_g - fcx) / (frx * 1.2))**2 + ((ys_g - fcy) / (fry * 1.2))**2
face_glow = np.clip(1.0 - face_dist_full, 0, 1)
face_glow = gaussian_filter(face_glow.astype(np.float32), sigma=15.0)
face_glow = np.clip(face_glow, 0, 1) * 0.055

for c in range(3):
    canvas[:, :, c] = np.clip(canvas[:, :, c] + face_glow, 0, 1)

# Final warm amber glaze
opacity = 0.020
canvas[:, :, 0] = np.clip(canvas[:, :, 0]*(1-opacity) + 0.60*opacity, 0, 1)
canvas[:, :, 1] = np.clip(canvas[:, :, 1]*(1-opacity) + 0.48*opacity, 0, 1)
canvas[:, :, 2] = np.clip(canvas[:, :, 2]*(1-opacity) + 0.25*opacity, 0, 1)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s125_portrait_refined.png")
Image.fromarray((np.clip(canvas, 0, 1)*255).astype(np.uint8), "RGB").save(out)
print(f"Saved: {out}")
