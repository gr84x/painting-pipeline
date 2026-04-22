"""Session 125 v4 — Mona Lisa: manually paint dress, focused strokes only on face/hands."""
import sys, os, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W, H = 780, 1040

# ─── Reference image ──────────────────────────────────────────────────────────
ref = np.zeros((H, W, 3), dtype=np.float32)

# Sky
for y in range(H):
    t = y / H
    ref[y, :, 0] = np.clip(0.64 + t * 0.22, 0, 1)
    ref[y, :, 1] = np.clip(0.68 + t * 0.16, 0, 1)
    ref[y, :, 2] = np.clip(0.78 - t * 0.22, 0, 1)

# Left landscape
for x in range(W // 2):
    xn = x / (W // 2)
    ridge = int(H * 0.28 + xn * H * 0.11 + np.sin(x * 0.06) * H * 0.026)
    for y in range(ridge, H):
        d = min(1.0, (y - ridge) / max(1, H - ridge))
        ref[y, x] = np.clip([0.40 + d*0.22, 0.44 + d*0.18, 0.46 + d*0.10], 0, 1)

# Right landscape
for x in range(W // 2, W):
    xn = (x - W // 2) / (W // 2)
    ridge = int(H * 0.34 + xn * H * 0.06 + np.sin(x * 0.05) * H * 0.020)
    for y in range(ridge, H):
        d = min(1.0, (y - ridge) / max(1, H - ridge))
        ref[y, x] = np.clip([0.38 + d*0.24, 0.42 + d*0.20, 0.44 + d*0.14], 0, 1)

# Water glint
ref[int(H*0.40):int(H*0.48), int(W*0.52):int(W*0.82)] = [0.52, 0.62, 0.74]

# Winding path
for i in range(120):
    pt = i / 120
    px = int(W*0.03 + pt*W*0.18 + np.sin(pt*7)*W*0.030)
    py = int(H*0.27 + pt*H*0.42)
    for dx in range(-4, 5):
        nx = px + dx
        if 0 <= nx < W and 0 <= py < H:
            ref[py, nx] = [0.54, 0.52, 0.46]

# Figure
fig_cx = int(W * 0.52)
fcx, fcy = fig_cx + 5, int(H * 0.244)
frx, fry = 88, 112
lxp, lyp = fcx + 2, fcy + 50
hcx, hcy = fig_cx - 4, int(H * 0.785)

# Dress
for y in range(90, min(920, H)):
    bt = (y - 90) / 830
    if bt < 0.08:
        hw = int(152 * bt / 0.08)
    elif bt < 0.28:
        hw = 152
    else:
        hw = int(152 + (bt - 0.28) * 64)
    x1, x2 = max(0, fig_cx - hw), min(W, fig_cx + hw)
    for x in range(x1, x2):
        xn = (x - x1) / max(1, x2 - x1) * 2 - 1
        light = 1.0 - 0.18 * xn - 0.06 * bt
        ref[y, x] = np.clip([0.12*light, 0.18*light, 0.13*light], 0, 1)

# Neckline trim
ref[395:410, fig_cx-72:fig_cx+86] = [0.72, 0.56, 0.24]

# Gauze
for y in range(410, 648):
    for x in range(fig_cx-90, fig_cx+100):
        if 0 <= y < H and 0 <= x < W:
            ref[y, x] = np.clip(ref[y, x] * 0.68 + np.array([0.66, 0.63, 0.56]) * 0.32, 0, 1)

# Neck
ncx = fig_cx + 8
for y in range(306, 422):
    nw = 33
    for x in range(ncx - nw, ncx + nw):
        if 0 <= x < W:
            t = abs(x - ncx) / nw
            lf = 1.0 - 0.18 * t
            ref[y, x] = np.clip([0.86*lf, 0.72*lf, 0.54*lf], 0, 1)

# Face
ys_g, xs_g = np.mgrid[fcy-fry:fcy+fry, fcx-frx:fcx+frx]
fxg = (xs_g - fcx) / frx
fyg = (ys_g - fcy) / fry
face_in = (fxg**2 + fyg**2) <= 1.0
light_g = np.clip(1.12 - 0.28*fxg - 0.20*fyg, 0.54, 1.20)
chin_sh = np.clip((fyg - 0.50) * 0.30, 0.0, 0.16)
skin_r = np.clip((0.87 - chin_sh) * light_g, 0, 1)
skin_g2 = np.clip((0.71 - chin_sh*0.7) * light_g, 0, 1)
skin_b = np.clip((0.53 - chin_sh*0.5) * light_g, 0, 1)
y0f, y1f = fcy-fry, fcy+fry
x0f, x1f = fcx-frx, fcx+frx
ref[y0f:y1f, x0f:x1f, 0] = np.where(face_in, skin_r,  ref[y0f:y1f, x0f:x1f, 0])
ref[y0f:y1f, x0f:x1f, 1] = np.where(face_in, skin_g2, ref[y0f:y1f, x0f:x1f, 1])
ref[y0f:y1f, x0f:x1f, 2] = np.where(face_in, skin_b,  ref[y0f:y1f, x0f:x1f, 2])

# Eyes
for ex_off, ew in [(-32, 16), (24, 15)]:
    ex, ey = fcx + ex_off, fcy - 14
    for dy in range(-9, 10):
        for dx in range(-ew, ew+1):
            nx, ny = ex+dx, ey+dy
            if 0<=nx<W and 0<=ny<H:
                d = (dx/ew)**2 + (dy/9)**2
                if d < 1.0:
                    ref[ny, nx] = [0.16, 0.11, 0.07]
    for dy in range(-13, -7):
        for dx in range(-ew-3, ew+4):
            nx, ny = ex+dx, ey+dy
            if 0<=nx<W and 0<=ny<H:
                d = (dx/(ew+3))**2 + (dy/7)**2
                if d < 1.0:
                    ref[ny, nx] = np.clip(ref[ny, nx]*0.60, 0, 1)

# Eyebrows (very faint)
for ex_off in [-32, 24]:
    ebx, eby = fcx + ex_off, fcy - 36
    for y in range(eby-2, eby+3):
        for x in range(ebx-12, ebx+14):
            if 0<=x<W and 0<=y<H:
                ref[y, x] = np.clip(ref[y, x]*0.90 + np.array([0.30, 0.22, 0.14])*0.10, 0, 1)

# Lips
for y in range(lyp-8, lyp+9):
    for x in range(lxp-18, lxp+18):
        if 0<=y<H and 0<=x<W:
            d = ((x-lxp)/18)**2 + ((y-lyp)/8)**2
            if d < 1.0:
                corner = abs((x-lxp)/18)**2 * 0.06
                ref[y, x] = np.clip([0.66, 0.44+corner, 0.38], 0, 1)

# Nose shadow
for y in range(fcy+8, fcy+40):
    nt = (y - fcy - 8) / 32
    for x in range(fcx-5, fcx+8):
        if 0<=y<H and 0<=x<W:
            t = abs(x - fcx) / 7
            ref[y, x] = np.clip(ref[y, x] - 0.07*(1-t)*nt, 0, 1)

# Hair
for y in range(fcy-fry-25, fcy+fry-12):
    for x in range(fcx-frx-28, fcx+frx+28):
        if 0<=y<H and 0<=x<W:
            fxl = (x - fcx) / (frx+28)
            fyl = (y - fcy) / fry
            in_face = (fxl**2 + fyl**2) < 0.80
            if not in_face and abs(fxl) > 0.43:
                wave = np.sin((y - fcy) * 0.10) * 0.018
                ref[y, x] = np.clip([0.24+wave, 0.17, 0.11], 0, 1)

# Veil
vcx, vcy = fcx, fcy - fry + 16
vrx, vry = 96, 40
for y in range(vcy-vry, vcy+vry):
    for x in range(vcx-vrx, vcx+vrx):
        if 0<=y<H and 0<=x<W:
            d = ((x-vcx)/vrx)**2 + ((y-vcy)/vry)**2
            if d < 1.0:
                alpha = 0.44 * (1 - d**0.5)
                ref[y, x] = np.clip(ref[y, x]*(1-alpha) + np.array([0.12, 0.09, 0.07])*alpha, 0, 1)

# Hands
for y in range(hcy-32, hcy+65):
    for x in range(hcx-66, hcx+44):
        if 0<=y<H and 0<=x<W:
            d = ((x-(hcx-14))/56)**2*0.68 + ((y-hcy)/48)**2
            if d < 1.0:
                lf = 0.88 - 0.12*abs((x-hcx)/66)
                ref[y, x] = np.clip([0.80*lf, 0.65*lf, 0.48*lf], 0, 1)
for y in range(hcy-50, hcy+38):
    for x in range(hcx-28, hcx+68):
        if 0<=y<H and 0<=x<W:
            d = ((x-(hcx+20))/50)**2*0.64 + ((y-(hcy-6))/44)**2
            if d < 1.0:
                lf = 0.91 - 0.10*abs((x-(hcx+20))/50)
                ref[y, x] = np.clip([0.82*lf, 0.67*lf, 0.50*lf], 0, 1)

# Smooth
for c in range(3):
    ref[:, :, c] = gaussian_filter(ref[:, :, c], sigma=2.0)

ref_img = Image.fromarray((np.clip(ref, 0, 1) * 255).astype(np.uint8), "RGB")

print("Reference built. Building painter…")

from stroke_engine import Painter, ellipse_mask, anatomy_flow_field, spherical_flow
from art_catalog import get_style
import cairo

leo = get_style("leonardo")
p = Painter(W, H)

# ── Step 1: copy the entire reference onto the canvas ────────────────────────
# This pre-paints background AND figure with reference colors
ref_arr = np.array(ref_img).astype(np.float32) / 255.0  # H W 3 RGB
buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((H, W, 4)).copy()
buf[:, :, 0] = (ref_arr[:, :, 2] * 255).astype(np.uint8)  # B channel (cairo BGRA)
buf[:, :, 1] = (ref_arr[:, :, 1] * 255).astype(np.uint8)  # G
buf[:, :, 2] = (ref_arr[:, :, 0] * 255).astype(np.uint8)  # R
buf[:, :, 3] = 255
p.canvas.surface.get_data()[:] = buf.tobytes()
print("  canvas initialized from reference")

# ── Step 2: overlay warm ochre ground on figure area ─────────────────────────
# Create figure mask
mask = np.zeros((H, W), dtype=np.float32)
for y in range(90, min(920, H)):
    bt = (y - 90) / 830
    if bt < 0.08:
        hw = int(152 * bt / 0.08)
    elif bt < 0.28:
        hw = 152
    else:
        hw = int(152 + (bt - 0.28) * 64)
    x1m, x2m = max(0, fig_cx - hw), min(W, fig_cx + hw)
    mask[y, x1m:x2m] = 1.0
for y in range(fcy-fry-28, fcy+fry+28):
    for x in range(fcx-frx-30, fcx+frx+30):
        if 0<=y<H and 0<=x<W:
            d = ((x-fcx)/(frx+30))**2 + ((y-fcy)/(fry+30))**2
            if d < 1.0:
                mask[y, x] = 1.0
mask = gaussian_filter(mask, sigma=5.5)
mask = np.clip(mask, 0, 1)
mask_img = Image.fromarray((mask * 255).astype(np.uint8), "L")
p.set_figure_mask(mask_img)
p._comp_map = p._build_composition_map(focal_xy=(fcx / W, fcy / H))

# ── Step 3: linen texture pass to add canvas tooth ───────────────────────────
# (already done by Painter.__init__ via tone_ground call below)
p.tone_ground(leo.ground_color, texture_strength=0.06)
print("  tone_ground (light)")

# ── Step 4: re-assert the reference colors on canvas (tone_ground overwrote) ──
buf2 = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((H, W, 4)).copy()
# Blend back toward reference: background fully, figure partially
for c_ref, c_cairo, cname in [(0, 2, 'R'), (1, 1, 'G'), (2, 0, 'B')]:
    ch_ref = (ref_arr[:, :, c_ref] * 255).astype(np.uint8)
    # Outside figure: fully restore reference
    # Inside figure: restore 80% reference, keep 20% ground tone
    blend = 1.0 - mask * 0.20
    buf2[:, :, c_cairo] = np.clip(ch_ref * blend + buf2[:, :, c_cairo] * (1 - blend), 0, 255).astype(np.uint8)
buf2[:, :, 3] = 255
p.canvas.surface.get_data()[:] = buf2.tobytes()
print("  reference re-asserted")

# ── Step 5: focused passes ONLY on face, neck, and hands ─────────────────────
sphere_f = spherical_flow(W, H, fcx, fcy, frx, fry)
face_f = anatomy_flow_field(W, H, fcx, fcy, frx, fry, gradient_fallback=sphere_f)

face_m    = ellipse_mask(W, H, fcx, fcy, int(frx*1.02), int(fry*1.00), feather=0.28)
eyes_m    = ellipse_mask(W, H, fcx, fcy-fry//4, int(frx*0.76), int(fry*0.44), feather=0.22)
lips_m    = ellipse_mask(W, H, lxp, lyp, int(frx*0.46), int(fry*0.23), feather=0.24)
hands_m   = ellipse_mask(W, H, hcx, hcy, 72, 58, feather=0.30)

p.focused_pass(ref_img, face_m,  stroke_size=7,  n_strokes=2000, opacity=0.86, wet_blend=0.92, form_angles=face_f)
p.focused_pass(ref_img, eyes_m,  stroke_size=4,  n_strokes=1200, opacity=0.88, wet_blend=0.62, form_angles=face_f)
p.focused_pass(ref_img, lips_m,  stroke_size=3,  n_strokes=700,  opacity=0.90, wet_blend=0.62, form_angles=face_f)
p.focused_pass(ref_img, hands_m, stroke_size=6,  n_strokes=600,  opacity=0.82, wet_blend=0.86, form_angles=None)
print("  focused_pass (face/hands only)")

# Highlights
p.place_lights(ref_img, stroke_size=4, n_strokes=700)
print("  place_lights")

# ── Sfumato veil ──────────────────────────────────────────────────────────────
p.sfumato_veil_pass(ref_img, n_veils=14, blur_radius=8.0, warmth=0.30,
                    veil_opacity=0.052, edge_only=True)
print("  sfumato_veil")

# ── Session 125: chromatic aerial perspective ─────────────────────────────────
p.chromatic_aerial_perspective_pass(
    sky_fraction=0.46, cool_r=0.54, cool_g=0.62, cool_b=0.78,
    haze_strength=0.22, desat_strength=0.26, haze_lift=0.08,
    gamma=1.15, blur_radius=20.0, opacity=0.82,
)
print("  aerial_perspective")

# Albani sky-shadow
p.albani_arcadian_grace_pass(
    peach_r=0.026, peach_g=0.010, sky_b=0.032, sky_r=0.009,
    ambient_lift=0.005, blur_radius=4.0, opacity=0.16,
)
print("  albani_grace")

# Leonardo glazes
p.glaze(leo.glazing, opacity=0.060)
p.glaze((0.60, 0.44, 0.20), opacity=0.035)

# Edge
p.edge_lost_and_found_pass(
    focal_xy=(fcx/W, fcy/H), found_radius=0.32,
    found_sharpness=0.50, lost_blur=1.8, strength=0.28, figure_only=False,
)
print("  edge")

p.finish(vignette=0.36, crackle=False)
print("  finish")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s125_portrait_v4.png")
p.save(out)
print(f"\nSaved: {out}")
