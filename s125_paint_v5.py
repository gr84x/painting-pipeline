"""Session 125 v5 — Mona Lisa: better proportions, smoother face, rounder veil."""
import sys, os, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W, H = 780, 1040

ref = np.zeros((H, W, 3), dtype=np.float32)

# Sky — cool at top, warm golden near horizon
for y in range(H):
    t = y / H
    ref[y, :, 0] = np.clip(0.64 + t*0.20, 0, 1)
    ref[y, :, 1] = np.clip(0.68 + t*0.14, 0, 1)
    ref[y, :, 2] = np.clip(0.76 - t*0.18, 0, 1)

# Left landscape — higher horizon, winding path
for x in range(W // 2):
    xn = x / (W // 2)
    ridge = int(H*0.30 + xn*H*0.10 + np.sin(x*0.055)*H*0.024)
    for y in range(ridge, H):
        d = min(1.0, (y - ridge) / max(1, H - ridge))
        ref[y, x] = np.clip([0.38+d*0.22, 0.43+d*0.18, 0.45+d*0.10], 0, 1)

# Winding path — lighter tone
for i in range(140):
    pt = i / 140
    px = int(W*0.03 + pt*W*0.20 + np.sin(pt*7.5)*W*0.032)
    py = int(H*0.28 + pt*H*0.44)
    for dx in range(-5, 6):
        nx = px + dx
        if 0 <= nx < W and 0 <= py < H:
            ref[py, nx] = [0.56, 0.54, 0.48]

# Right landscape — slightly lower
for x in range(W // 2, W):
    xn = (x - W//2) / (W//2)
    ridge = int(H*0.36 + xn*H*0.06 + np.sin(x*0.05)*H*0.020)
    for y in range(ridge, H):
        d = min(1.0, (y - ridge) / max(1, H - ridge))
        ref[y, x] = np.clip([0.36+d*0.24, 0.41+d*0.20, 0.43+d*0.14], 0, 1)

# Water glint — mid right, pale blue
for y in range(int(H*0.42), int(H*0.50)):
    for x in range(int(W*0.53), int(W*0.82)):
        t_x = (x - int(W*0.53)) / (int(W*0.82) - int(W*0.53))
        ref[y, x] = np.clip([0.50+t_x*0.06, 0.60+t_x*0.04, 0.72-t_x*0.06], 0, 1)

# Blur background before adding figure
for c in range(3):
    ref[:, :, c] = gaussian_filter(ref[:, :, c], sigma=1.5)

# ── Figure placement ──────────────────────────────────────────────────────────
fig_cx = int(W * 0.51)
fcx, fcy = fig_cx + 4, int(H * 0.244)
frx, fry = 88, 112
lxp, lyp = fcx + 2, fcy + 50
hcx, hcy = fig_cx - 4, int(H * 0.785)

# Dress — wide, three-quarter stance; shoulder_w wider
def draw_dress(ref):
    for y in range(88, min(930, H)):
        bt = (y - 88) / 842
        if bt < 0.06:
            hw = int(175 * bt / 0.06)
        elif bt < 0.25:
            hw = 175
        else:
            hw = int(175 + (bt - 0.25) * 55)
        x1, x2 = max(0, fig_cx - hw), min(W, fig_cx + hw)
        for x in range(x1, x2):
            xn = (x - x1) / max(1, x2 - x1) * 2 - 1
            light = 1.0 - 0.16*xn - 0.05*bt
            # Dark forest-green, not quite black
            ref[y, x] = np.clip([0.12*light, 0.18*light, 0.13*light], 0, 1)

draw_dress(ref)

# Neckline amber trim
ref[395:411, fig_cx-78:fig_cx+92] = [0.72, 0.56, 0.24]

# Gauze wrap — blend smoothly, no hard rectangle
for y in range(412, 652):
    for x in range(fig_cx-92, fig_cx+104):
        if 0<=y<H and 0<=x<W:
            # Only apply gauze to dress pixels (dark ones)
            if ref[y, x, 1] < 0.30:  # inside dress
                # Subtle gauze, no hard edges
                dist_center = abs(x - fig_cx) / 95
                gauze_alpha = max(0, 0.22 - dist_center * 0.15)
                ref[y, x] = np.clip(ref[y, x]*(1-gauze_alpha) + np.array([0.58, 0.56, 0.48])*gauze_alpha, 0, 1)

# Neck
ncx = fig_cx + 8
for y in range(308, 424):
    nw = 34
    for x in range(ncx-nw, ncx+nw):
        if 0 <= x < W:
            t = abs(x - ncx) / nw
            lf = 1.0 - 0.18*t
            ref[y, x] = np.clip([0.86*lf, 0.72*lf, 0.54*lf], 0, 1)

# Face — luminous oval, high smooth forehead
ys_g, xs_g = np.mgrid[fcy-fry:fcy+fry, fcx-frx:fcx+frx]
fxg = (xs_g - fcx) / frx
fyg = (ys_g - fcy) / fry
face_in = (fxg**2 + fyg**2) <= 1.0
light_g = np.clip(1.14 - 0.26*fxg - 0.18*fyg, 0.55, 1.22)
chin_sh = np.clip((fyg - 0.48)*0.28, 0.0, 0.15)
skin_r = np.clip((0.88 - chin_sh)*light_g, 0, 1)
skin_g2 = np.clip((0.72 - chin_sh*0.68)*light_g, 0, 1)
skin_b  = np.clip((0.54 - chin_sh*0.48)*light_g, 0, 1)
y0f, y1f = fcy-fry, fcy+fry
x0f, x1f = fcx-frx, fcx+frx
ref[y0f:y1f, x0f:x1f, 0] = np.where(face_in, skin_r,  ref[y0f:y1f, x0f:x1f, 0])
ref[y0f:y1f, x0f:x1f, 1] = np.where(face_in, skin_g2, ref[y0f:y1f, x0f:x1f, 1])
ref[y0f:y1f, x0f:x1f, 2] = np.where(face_in, skin_b,  ref[y0f:y1f, x0f:x1f, 2])

# Eyes — dark, heavy-lidded
for ex_off, ew in [(-33, 16), (25, 15)]:
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
                    ref[ny, nx] = np.clip(ref[ny, nx]*0.58, 0, 1)

# Very faint eyebrows
for ex_off in [-33, 25]:
    ebx, eby = fcx + ex_off, fcy - 37
    for y in range(eby-2, eby+3):
        for x in range(ebx-12, ebx+14):
            if 0<=x<W and 0<=y<H:
                ref[y, x] = np.clip(ref[y, x]*0.91 + np.array([0.28, 0.20, 0.12])*0.09, 0, 1)

# Lips — small, ambiguous corners
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

# Hair — smooth waves from center part, filling sides of head
for y in range(fcy-fry-28, fcy+fry):
    for x in range(fcx-frx-32, fcx+frx+32):
        if 0<=y<H and 0<=x<W:
            fxl = (x - fcx) / (frx + 32)
            fyl = (y - fcy) / fry
            in_face = (fxl**2 + fyl**2) < 0.78
            at_side = abs(fxl) > 0.40
            if not in_face and at_side:
                wave = np.sin((y-fcy)*0.09)*0.020
                ref[y, x] = np.clip([0.23+wave, 0.16, 0.10], 0, 1)

# Veil — dark translucent, softly rounded over crown
vcx, vcy = fcx, fcy - fry + 18
vrx, vry = 100, 44
for y in range(vcy-vry, vcy+vry+10):
    for x in range(vcx-vrx, vcx+vrx):
        if 0<=y<H and 0<=x<W:
            # Rounder shape — use ellipse blend
            d = ((x-vcx)/vrx)**2 + ((y-vcy)/vry)**2
            if d < 1.0:
                alpha = 0.42 * max(0, 1 - d**0.4)
                ref[y, x] = np.clip(ref[y, x]*(1-alpha) + np.array([0.12, 0.09, 0.07])*alpha, 0, 1)

# Hands
for y in range(hcy-35, hcy+68):
    for x in range(hcx-68, hcx+46):
        if 0<=y<H and 0<=x<W:
            d = ((x-(hcx-14))/58)**2*0.66 + ((y-hcy)/50)**2
            if d < 1.0:
                lf = 0.87 - 0.12*abs((x-hcx)/68)
                ref[y, x] = np.clip([0.78*lf, 0.64*lf, 0.47*lf], 0, 1)
for y in range(hcy-52, hcy+40):
    for x in range(hcx-30, hcx+70):
        if 0<=y<H and 0<=x<W:
            d = ((x-(hcx+20))/52)**2*0.62 + ((y-(hcy-6))/46)**2
            if d < 1.0:
                lf = 0.90 - 0.10*abs((x-(hcx+20))/52)
                ref[y, x] = np.clip([0.80*lf, 0.66*lf, 0.49*lf], 0, 1)

# Final gentle smooth
for c in range(3):
    ref[:, :, c] = gaussian_filter(ref[:, :, c], sigma=1.8)

ref_img = Image.fromarray((np.clip(ref, 0, 1)*255).astype(np.uint8), "RGB")

print("Reference built. Initializing canvas…")

from stroke_engine import Painter, ellipse_mask, anatomy_flow_field, spherical_flow
from art_catalog import get_style

leo = get_style("leonardo")
p = Painter(W, H)

# Bootstrap canvas from reference
ref_arr = np.array(ref_img).astype(np.float32) / 255.0
buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((H, W, 4)).copy()
buf[:, :, 0] = (ref_arr[:, :, 2]*255).astype(np.uint8)  # B
buf[:, :, 1] = (ref_arr[:, :, 1]*255).astype(np.uint8)  # G
buf[:, :, 2] = (ref_arr[:, :, 0]*255).astype(np.uint8)  # R
buf[:, :, 3] = 255
p.canvas.surface.get_data()[:] = buf.tobytes()

# Figure mask
mask = np.zeros((H, W), dtype=np.float32)
for y in range(88, min(930, H)):
    bt = (y - 88) / 842
    if bt < 0.06:
        hw = int(175 * bt / 0.06)
    elif bt < 0.25:
        hw = 175
    else:
        hw = int(175 + (bt-0.25)*55)
    x1m, x2m = max(0, fig_cx-hw), min(W, fig_cx+hw)
    mask[y, x1m:x2m] = 1.0
for y in range(fcy-fry-30, fcy+fry+30):
    for x in range(fcx-frx-32, fcx+frx+32):
        if 0<=y<H and 0<=x<W:
            d = ((x-fcx)/(frx+32))**2 + ((y-fcy)/(fry+32))**2
            if d < 1.0:
                mask[y, x] = 1.0
mask = gaussian_filter(mask, sigma=6.0)
mask = np.clip(mask, 0, 1)
mask_img = Image.fromarray((mask*255).astype(np.uint8), "L")
p.set_figure_mask(mask_img)
p._comp_map = p._build_composition_map(focal_xy=(fcx/W, fcy/H))

# Very light texture pass — linen tooth without losing reference colors
p.tone_ground(leo.ground_color, texture_strength=0.04)

# Re-assert reference on canvas (blend back after tone_ground)
buf2 = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((H, W, 4)).copy()
blend = 1.0 - mask * 0.15  # outside: fully restore; inside figure: 85% restore
for c_ref, c_cairo in [(0, 2), (1, 1), (2, 0)]:
    ch = (ref_arr[:, :, c_ref]*255)
    buf2[:, :, c_cairo] = np.clip(ch*blend + buf2[:, :, c_cairo]*(1-blend), 0, 255).astype(np.uint8)
buf2[:, :, 3] = 255
p.canvas.surface.get_data()[:] = buf2.tobytes()
print("  canvas ready")

# ── Focused passes — face and hands only ─────────────────────────────────────
sphere_f = spherical_flow(W, H, fcx, fcy, frx, fry)
face_f   = anatomy_flow_field(W, H, fcx, fcy, frx, fry, gradient_fallback=sphere_f)

face_m  = ellipse_mask(W, H, fcx, fcy, int(frx*1.02), int(fry*1.00), feather=0.30)
eyes_m  = ellipse_mask(W, H, fcx, fcy-fry//4, int(frx*0.75), int(fry*0.44), feather=0.22)
lips_m  = ellipse_mask(W, H, lxp, lyp, int(frx*0.45), int(fry*0.22), feather=0.24)
hands_m = ellipse_mask(W, H, hcx, hcy, 74, 60, feather=0.30)

# Face — very high wet_blend for sfumato-smooth skin
p.focused_pass(ref_img, face_m,  stroke_size=7,  n_strokes=2400, opacity=0.80, wet_blend=0.94, form_angles=face_f)
p.focused_pass(ref_img, eyes_m,  stroke_size=3,  n_strokes=1300, opacity=0.88, wet_blend=0.65, form_angles=face_f)
p.focused_pass(ref_img, lips_m,  stroke_size=3,  n_strokes=750,  opacity=0.90, wet_blend=0.65, form_angles=face_f)
p.focused_pass(ref_img, hands_m, stroke_size=6,  n_strokes=650,  opacity=0.80, wet_blend=0.88, form_angles=None)
print("  focused_pass")

p.place_lights(ref_img, stroke_size=4, n_strokes=700)
print("  place_lights")

# Sfumato veil
p.sfumato_veil_pass(ref_img, n_veils=16, blur_radius=8.5, warmth=0.30,
                    veil_opacity=0.048, edge_only=True)
print("  sfumato_veil")

# Session 125: chromatic aerial perspective
p.chromatic_aerial_perspective_pass(
    sky_fraction=0.44, cool_r=0.54, cool_g=0.62, cool_b=0.78,
    haze_strength=0.24, desat_strength=0.28, haze_lift=0.09,
    gamma=1.12, blur_radius=22.0, opacity=0.85,
)
print("  aerial_perspective")

# Albani sky-shadow in outdoor penumbra
p.albani_arcadian_grace_pass(
    peach_r=0.024, peach_g=0.008, sky_b=0.030, sky_r=0.008,
    ambient_lift=0.004, blur_radius=4.0, opacity=0.14,
)
print("  albani_grace")

# Leonardo glazes
p.glaze(leo.glazing, opacity=0.065)
p.glaze((0.58, 0.42, 0.18), opacity=0.038)

p.edge_lost_and_found_pass(
    focal_xy=(fcx/W, fcy/H), found_radius=0.34,
    found_sharpness=0.52, lost_blur=2.0, strength=0.25, figure_only=False,
)

p.finish(vignette=0.34, crackle=False)
print("  finish")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s125_portrait_v5.png")
p.save(out)
print(f"\nSaved: {out}")
