"""Session 125 — Mona Lisa sfumato portrait render."""
import sys, os, numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W, H = 780, 1040

# ─── Synthetic Mona Lisa reference ──────────────────────────────────────────
ref = np.zeros((H, W, 3), dtype=np.float32)

# Sky — pale blue-grey gradient
for y in range(H):
    t = y / H
    ref[y, :] = [0.56 + t*0.24, 0.60 + t*0.16, 0.72 - t*0.24]

# Left rocky landscape — slightly higher horizon
for x in range(W // 2):
    xn = x / (W // 2)
    ridge = int(H * 0.32 + xn * H * 0.09 + np.sin(x * 0.07) * H * 0.022)
    for y in range(ridge, H):
        d = (y - ridge) / max(1, H - ridge)
        ref[y, x] = np.clip([0.30 + d*0.18, 0.34 + d*0.16, 0.36 + d*0.10], 0, 1)

# Right landscape — slightly lower, subtle water glint
for x in range(W // 2, W):
    xn = (x - W//2) / (W//2)
    ridge = int(H * 0.38 + xn * H * 0.05 + np.sin(x * 0.055) * H * 0.018)
    for y in range(ridge, H):
        d = (y - ridge) / max(1, H - ridge)
        ref[y, x] = np.clip([0.28 + d*0.20, 0.32 + d*0.18, 0.34 + d*0.12], 0, 1)

# Water glint mid-right
wy1, wy2 = int(H * 0.44), int(H * 0.50)
wx1, wx2 = int(W * 0.55), int(W * 0.78)
ref[wy1:wy2, wx1:wx2] = [0.48, 0.54, 0.64]

# Winding path left side
for i in range(100):
    pt = i / 100
    px = int(W * 0.04 + pt * W * 0.16 + np.sin(pt * 8) * W * 0.028)
    py = int(H * 0.30 + pt * H * 0.40)
    for dx in range(-3, 4):
        for dy in range(-1, 2):
            nx2, ny2 = px+dx, py+dy
            if 0 <= nx2 < W and 0 <= ny2 < H:
                ref[ny2, nx2] = [0.46, 0.42, 0.36]

# ── Figure body — dark forest-green dress ────────────────────────────────────
fig_cx = int(W * 0.52)
for y in range(100, min(880, H)):
    bt = (y - 100) / 780
    hw = int(110 + bt * 35) if bt > 0.12 else int(110 * bt / 0.12)
    x1, x2 = max(0, fig_cx - hw), min(W, fig_cx + hw)
    for x in range(x1, x2):
        xn = (x - x1) / max(1, x2 - x1) * 2 - 1
        light = 1.0 - 0.25 * xn - 0.10 * bt
        ref[y, x] = np.clip([0.13*light, 0.19*light, 0.14*light], 0, 1)

# Neckline gold trim
ny1a, ny2a = 393, 406
nx1a, nx2a = fig_cx - 70, fig_cx + 80
ref[ny1a:ny2a, nx1a:nx2a] = np.clip([[0.70, 0.55, 0.22]], 0, 1)

# Gauze wrap over chest
gy1, gy2, gx1, gx2 = 406, 625, fig_cx - 85, fig_cx + 95
chunk = ref[gy1:gy2, gx1:gx2].copy()
ref[gy1:gy2, gx1:gx2] = np.clip(chunk * 0.72 + np.array([0.62, 0.59, 0.50]) * 0.28, 0, 1)

# ── Neck ─────────────────────────────────────────────────────────────────────
ncx = fig_cx + 6
for y in range(305, 415):
    nw = 30
    for x in range(ncx - nw, ncx + nw):
        if 0 <= x < W:
            t = abs(x - ncx) / nw
            lf = 1.0 - 0.18 * t
            ref[y, x] = np.clip([0.80*lf, 0.64*lf, 0.46*lf], 0, 1)

# ── Face ─────────────────────────────────────────────────────────────────────
fcx, fcy = fig_cx + 4, int(H * 0.24)
frx, fry = 80, 100

ys_g, xs_g = np.mgrid[fcy-fry:fcy+fry, fcx-frx:fcx+frx]
fxg = (xs_g - fcx) / frx
fyg = (ys_g - fcy) / fry
face_in = (fxg**2 + fyg**2) <= 1.0
light_g = np.clip(1.0 - 0.28*fxg - 0.18*fyg, 0.5, 1.15)

skin_r = np.clip(0.83 * light_g, 0, 1)
skin_g2 = np.clip(0.67 * light_g, 0, 1)
skin_b = np.clip(0.48 * light_g, 0, 1)

y0, y1a = fcy - fry, fcy + fry
x0, x1a = fcx - frx, fcx + frx
ref[y0:y1a, x0:x1a, 0] = np.where(face_in, skin_r,  ref[y0:y1a, x0:x1a, 0])
ref[y0:y1a, x0:x1a, 1] = np.where(face_in, skin_g2, ref[y0:y1a, x0:x1a, 1])
ref[y0:y1a, x0:x1a, 2] = np.where(face_in, skin_b,  ref[y0:y1a, x0:x1a, 2])

# Eyes
for ex_off, ew in [(-28, 14), (20, 13)]:
    ex, ey = fcx + ex_off, fcy - 8
    for dy in range(-7, 9):
        for dx in range(-ew, ew+1):
            nx3, ny3 = ex+dx, ey+dy
            if 0 <= nx3 < W and 0 <= ny3 < H:
                d = (dx/ew)**2 + (dy/8)**2
                if d < 1.0:
                    ref[ny3, nx3] = [0.18, 0.13, 0.08]

# Lips
lxp, lyp = fcx + 2, fcy + 44
for y in range(lyp - 7, lyp + 8):
    for x in range(lxp - 17, lxp + 17):
        if 0 <= y < H and 0 <= x < W:
            d = ((x-lxp)/17)**2 + ((y-lyp)/7)**2
            if d < 1.0:
                ref[y, x] = [0.65, 0.42, 0.36]

# Nose shadow
for y in range(fcy + 5, fcy + 32):
    for x in range(fcx - 7, fcx + 9):
        if 0 <= y < H and 0 <= x < W:
            t = abs(x - fcx) / 8
            ref[y, x] = np.clip(ref[y, x] - 0.06*(1-t), 0, 1)

# ── Hair — dark brown ────────────────────────────────────────────────────────
for y in range(fcy - fry - 18, fcy + fry - 18):
    for x in range(fcx - frx - 22, fcx + frx + 22):
        if 0 <= y < H and 0 <= x < W:
            fxl = (x - fcx) / (frx + 22)
            fyl = (y - fcy) / fry
            in_face = (fxl**2 + fyl**2) < 0.85
            if not in_face and abs(fxl) > 0.46:
                wave = np.sin((y - fcy) * 0.12) * 0.025
                ref[y, x] = np.clip([0.22 + wave, 0.16, 0.10], 0, 1)

# ── Dark translucent veil ─────────────────────────────────────────────────────
vcx, vcy = fcx, fcy - fry + 12
vrx, vry = 90, 36
for y in range(vcy - vry, vcy + vry):
    for x in range(vcx - vrx, vcx + vrx):
        if 0 <= y < H and 0 <= x < W:
            d = ((x-vcx)/vrx)**2 + ((y-vcy)/vry)**2
            if d < 1.0:
                alpha = 0.50 * (1 - d**0.5)
                ref[y, x] = np.clip(ref[y, x]*(1-alpha) + np.array([0.10, 0.07, 0.05])*alpha, 0, 1)

# ── Hands — lower center, right over left ────────────────────────────────────
hcx, hcy = fig_cx - 5, int(H * 0.78)
for y in range(hcy - 42, hcy + 58):
    for x in range(hcx - 64, hcx + 67):
        if 0 <= y < H and 0 <= x < W:
            d = ((x-hcx)/66)**2 * 0.68 + ((y-hcy)/50)**2
            if d < 1.0:
                lf = 0.92 - 0.14 * abs((x-hcx)/66)
                ref[y, x] = np.clip([0.76*lf, 0.61*lf, 0.44*lf], 0, 1)

# ── Smooth reference ──────────────────────────────────────────────────────────
for c in range(3):
    ref[:, :, c] = gaussian_filter(ref[:, :, c], sigma=2.5)

ref_img = Image.fromarray((np.clip(ref, 0, 1) * 255).astype(np.uint8), "RGB")

# ── Figure mask ──────────────────────────────────────────────────────────────
mask = np.zeros((H, W), dtype=np.float32)
for y in range(100, min(880, H)):
    bt = (y - 100) / 780
    hw = int(110 + bt * 35) if bt > 0.12 else int(110 * bt / 0.12)
    x1m, x2m = max(0, fig_cx - hw), min(W, fig_cx + hw)
    mask[y, x1m:x2m] = 1.0
for y in range(fcy - fry - 12, fcy + fry + 22):
    for x in range(fcx - frx - 14, fcx + frx + 14):
        if 0 <= y < H and 0 <= x < W:
            d = ((x-fcx)/(frx+14))**2 + ((y-fcy)/(fry+16))**2
            if d < 1.0:
                mask[y, x] = 1.0
mask = gaussian_filter(mask, sigma=5.5)
mask = np.clip(mask, 0, 1)
mask_img = Image.fromarray((mask * 255).astype(np.uint8), "L")

print("Reference synthesized. Starting stroke pipeline...")

# ─── Stroke engine pipeline ───────────────────────────────────────────────────
from stroke_engine import Painter, ellipse_mask, anatomy_flow_field, spherical_flow
from art_catalog import get_style

leo = get_style("leonardo")
p = Painter(W, H)
p.set_figure_mask(mask_img)
p._comp_map = p._build_composition_map(focal_xy=p._derive_focal_xy())
p.seal_background(ref_img)

p.tone_ground(leo.ground_color, texture_strength=0.09)
print("  tone_ground done")

p.underpainting(ref_img, stroke_size=30, n_strokes=110)
print("  underpainting done")

p.block_in(ref_img, stroke_size=26, n_strokes=240)
print("  block_in done")

p.build_form(ref_img, stroke_size=10, n_strokes=620)
print("  build_form done")

# Focused face detail
sphere_f = spherical_flow(W, H, fcx, fcy, frx, fry)
face_f = anatomy_flow_field(W, H, fcx, fcy, frx, fry, gradient_fallback=sphere_f)
face_m = ellipse_mask(W, H, fcx, fcy, int(frx*1.05), int(fry*1.02), feather=0.28)
eyes_m = ellipse_mask(W, H, fcx, fcy - fry//4, int(frx*0.80), int(fry*0.48), feather=0.22)
lips_m = ellipse_mask(W, H, fcx+2, fcy+44, int(frx*0.50), int(fry*0.26), feather=0.26)

p.focused_pass(ref_img, face_m, stroke_size=8,  n_strokes=1400, opacity=0.82, wet_blend=0.88, form_angles=face_f)
p.focused_pass(ref_img, eyes_m, stroke_size=5,  n_strokes=900,  opacity=0.85, wet_blend=0.55, form_angles=face_f)
p.focused_pass(ref_img, lips_m, stroke_size=4,  n_strokes=560,  opacity=0.86, wet_blend=0.55, form_angles=face_f)
print("  focused_pass done")

p.place_lights(ref_img, stroke_size=5, n_strokes=500)
print("  place_lights done")

# Sfumato — Leonardo's defining technique
p.sfumato_veil_pass(ref_img, n_veils=10, blur_radius=7.2, warmth=0.28, veil_opacity=0.058, edge_only=True)
print("  sfumato_veil done")

# Session 125 improvement: chromatic aerial perspective
p.chromatic_aerial_perspective_pass(
    sky_fraction=0.50, cool_r=0.56, cool_g=0.64, cool_b=0.80,
    haze_strength=0.18, desat_strength=0.22, haze_lift=0.06,
    gamma=1.20, blur_radius=16.0, opacity=0.72,
)
print("  aerial_perspective done")

# Albani arcadian pass — sky-reflected shadow fill
p.albani_arcadian_grace_pass(
    peach_r=0.030, peach_g=0.012, sky_b=0.036, sky_r=0.011,
    ambient_lift=0.007, blur_radius=4.5, opacity=0.20,
)
print("  albani_grace done")

# Warm unifying glaze
p.glaze((0.58, 0.42, 0.18), opacity=0.065)

# Edge lost-and-found
p.edge_lost_and_found_pass(
    focal_xy=p._derive_focal_xy(), found_radius=0.28,
    found_sharpness=0.45, lost_blur=1.8, strength=0.32, figure_only=False,
)
print("  edge_lost_found done")

p.finish(vignette=0.44, crackle=True)
print("  finish done")

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s125_portrait.png")
p.save(out_path)
print(f"Saved: {out_path}")
