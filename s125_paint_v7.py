"""Session 125 v7 — Mona Lisa: dress starts at shoulders, landscape visible beside head."""
import sys, os, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W, H = 780, 1040

ref = np.zeros((H, W, 3), dtype=np.float32)

# Sky
for y in range(H):
    t = y / H
    ref[y, :, 0] = np.clip(0.64 + t*0.20, 0, 1)
    ref[y, :, 1] = np.clip(0.68 + t*0.14, 0, 1)
    ref[y, :, 2] = np.clip(0.76 - t*0.18, 0, 1)

# Left landscape
for x in range(W // 2):
    xn = x / (W // 2)
    ridge = int(H*0.30 + xn*H*0.11 + np.sin(x*0.055)*H*0.025)
    for y in range(ridge, H):
        d = min(1.0, (y-ridge) / max(1, H-ridge))
        ref[y, x] = np.clip([0.38+d*0.22, 0.43+d*0.18, 0.45+d*0.10], 0, 1)

# Winding path
for i in range(140):
    pt = i / 140
    px = int(W*0.04 + pt*W*0.20 + np.sin(pt*7.5)*W*0.032)
    py = int(H*0.27 + pt*H*0.45)
    for dx in range(-5, 6):
        nx = px + dx
        if 0<=nx<W and 0<=py<H:
            ref[py, nx] = [0.56, 0.54, 0.48]

# Right landscape
for x in range(W // 2, W):
    xn = (x - W//2) / (W//2)
    ridge = int(H*0.37 + xn*H*0.06 + np.sin(x*0.05)*H*0.020)
    for y in range(ridge, H):
        d = min(1.0, (y-ridge) / max(1, H-ridge))
        ref[y, x] = np.clip([0.36+d*0.24, 0.41+d*0.20, 0.43+d*0.14], 0, 1)

# Water — more subtle, no hard rectangle
for y in range(int(H*0.43), int(H*0.50)):
    for x in range(int(W*0.53), int(W*0.82)):
        ty = (y - int(H*0.43)) / (int(H*0.50) - int(H*0.43))
        alpha = 0.5 * (1 - abs(ty - 0.5)*2)  # fade at edges
        ref[y, x] = ref[y, x]*(1-alpha) + np.array([0.52, 0.62, 0.74])*alpha

# Blur background
for c in range(3):
    ref[:, :, c] = gaussian_filter(ref[:, :, c], sigma=1.5)

# ── Layout: key coordinates ───────────────────────────────────────────────────
fig_cx = int(W * 0.515)
fcx, fcy = fig_cx + 4, int(H * 0.244)   # face center
frx, fry = 88, 112                        # face half-radii
shoulder_y = fcy + fry + 10              # dress starts below neck base
lxp, lyp = fcx + 2, fcy + 50            # lips
hcx, hcy = fig_cx - 4, int(H * 0.785)   # hands

# ── Dress body — starts at shoulder_y, NOT above face ────────────────────────
def body_hw(y):
    if y < shoulder_y:
        return 0
    bt = (y - shoulder_y) / max(1, H - shoulder_y)
    if bt < 0.05:   # taper up at top of dress (shoulder emergence)
        return int(175 * bt / 0.05)
    if bt < 0.35:   # full shoulder width
        return 175
    if bt < 0.55:   # slight waist taper
        t = (bt - 0.35) / 0.20
        return int(175 - t*30)
    if bt < 0.75:   # hips expand
        t = (bt - 0.55) / 0.20
        return int(145 + t*40)
    # Lap/bottom — widen
    t = min(1.0, (bt - 0.75) / 0.25)
    return int(185 + t*55)

for y in range(shoulder_y, min(940, H)):
    hw = body_hw(y)
    if hw <= 0:
        continue
    x1, x2 = max(0, fig_cx-hw), min(W, fig_cx+hw)
    for x in range(x1, x2):
        xn = (x-x1)/max(1, x2-x1)*2-1
        light = 1.0 - 0.14*xn - 0.04*(y-shoulder_y)/(H-shoulder_y)
        ref[y, x] = np.clip([0.13*light, 0.19*light, 0.14*light], 0, 1)

# Subtle neckline
for y in range(shoulder_y-3, shoulder_y+16):
    t_y = (y - (shoulder_y-3)) / 19
    for x in range(fig_cx-60, fig_cx+72):
        if 0<=x<W:
            dist = abs(x-fig_cx)/66
            alpha = 0.12*(1-dist)*(1-abs(t_y-0.5)*2)
            ref[y, x] = np.clip(ref[y, x]*(1-alpha) + np.array([0.68, 0.54, 0.22])*alpha, 0, 1)

# Gauze wrap
for y in range(shoulder_y+20, shoulder_y+240):
    hw = body_hw(y)
    gx1, gx2 = max(0, fig_cx-hw+8), min(W, fig_cx+hw-8)
    for x in range(gx1, gx2):
        if ref[y, x, 1] < 0.25:
            dist = abs(x-fig_cx)/max(1, hw-8)
            alpha = max(0, 0.16*(1-dist*1.3))
            ref[y, x] = np.clip(ref[y, x]*(1-alpha)+np.array([0.58, 0.56, 0.48])*alpha, 0, 1)

# Neck — connects face oval base to dress top
neck_y0 = fcy + int(fry * 0.72)   # base of face oval
neck_y1 = shoulder_y + 10
ncx = fig_cx + 8
for y in range(neck_y0, neck_y1):
    t_n = (y - neck_y0) / max(1, neck_y1 - neck_y0)
    nw = int(30 + t_n*22)  # widens from narrow neck to shoulders
    for x in range(ncx-nw, ncx+nw):
        if 0<=x<W:
            t = abs(x-ncx)/nw
            lf = 1.0 - 0.16*t
            ref[y, x] = np.clip([0.86*lf, 0.72*lf, 0.54*lf], 0, 1)

# ── Face ─────────────────────────────────────────────────────────────────────
ys_g, xs_g = np.mgrid[fcy-fry:fcy+fry, fcx-frx:fcx+frx]
fxg = (xs_g-fcx)/frx
fyg = (ys_g-fcy)/fry
face_in = (fxg**2+fyg**2) <= 1.0
light_g = np.clip(1.14 - 0.26*fxg - 0.18*fyg, 0.56, 1.22)
chin_sh = np.clip((fyg-0.48)*0.28, 0.0, 0.15)
skin_r  = np.clip((0.88-chin_sh)*light_g, 0, 1)
skin_g2 = np.clip((0.72-chin_sh*0.68)*light_g, 0, 1)
skin_b  = np.clip((0.54-chin_sh*0.48)*light_g, 0, 1)
y0f, y1f = fcy-fry, fcy+fry
x0f, x1f = fcx-frx, fcx+frx
ref[y0f:y1f, x0f:x1f, 0] = np.where(face_in, skin_r,  ref[y0f:y1f, x0f:x1f, 0])
ref[y0f:y1f, x0f:x1f, 1] = np.where(face_in, skin_g2, ref[y0f:y1f, x0f:x1f, 1])
ref[y0f:y1f, x0f:x1f, 2] = np.where(face_in, skin_b,  ref[y0f:y1f, x0f:x1f, 2])

# Eyes
for ex_off, ew in [(-33, 16), (25, 15)]:
    ex, ey = fcx+ex_off, fcy-14
    for dy in range(-9, 10):
        for dx in range(-ew, ew+1):
            nx, ny = ex+dx, ey+dy
            if 0<=nx<W and 0<=ny<H:
                d = (dx/ew)**2+(dy/9)**2
                if d < 1.0:
                    ref[ny, nx] = [0.16, 0.11, 0.07]
    for dy in range(-13, -7):
        for dx in range(-ew-3, ew+4):
            nx, ny = ex+dx, ey+dy
            if 0<=nx<W and 0<=ny<H:
                d = (dx/(ew+3))**2+(dy/7)**2
                if d < 1.0:
                    ref[ny, nx] = np.clip(ref[ny, nx]*0.58, 0, 1)

# Eyebrows (very faint)
for ex_off in [-33, 25]:
    ebx, eby = fcx+ex_off, fcy-37
    for y in range(eby-2, eby+3):
        for x in range(ebx-12, ebx+14):
            if 0<=x<W and 0<=y<H:
                ref[y, x] = np.clip(ref[y,x]*0.91 + np.array([0.28,0.20,0.12])*0.09, 0, 1)

# Lips
for y in range(lyp-8, lyp+9):
    for x in range(lxp-18, lxp+18):
        if 0<=y<H and 0<=x<W:
            d = ((x-lxp)/18)**2+((y-lyp)/8)**2
            if d < 1.0:
                corner = abs((x-lxp)/18)**2*0.06
                ref[y, x] = np.clip([0.66, 0.44+corner, 0.38], 0, 1)

# Nose
for y in range(fcy+8, fcy+40):
    nt = (y-fcy-8)/32
    for x in range(fcx-5, fcx+8):
        if 0<=y<H and 0<=x<W:
            t = abs(x-fcx)/7
            ref[y, x] = np.clip(ref[y,x] - 0.07*(1-t)*nt, 0, 1)

# Hair — dark brown waves on sides of face/head
for y in range(fcy-fry-24, fcy+fry-5):
    for x in range(fcx-frx-28, fcx+frx+28):
        if 0<=y<H and 0<=x<W:
            fxl = (x-fcx)/(frx+28)
            fyl = (y-fcy)/fry
            in_face = (fxl**2+fyl**2) < 0.80
            at_side = abs(fxl) > 0.44
            if not in_face and at_side:
                # Only draw hair where the background is visible (beside the head)
                wave = np.sin((y-fcy)*0.09)*0.018
                ref[y, x] = np.clip([0.23+wave, 0.16, 0.10], 0, 1)

# Veil — soft rounded dome only over top of head, not extending to sides as square
vcx, vcy = fcx, fcy - fry + 22
vrx, vry = 98, 44
for y in range(max(0,vcy-vry), min(H,vcy+vry)):
    for x in range(max(0,vcx-vrx), min(W,vcx+vrx)):
        d = ((x-vcx)/vrx)**2 + ((y-vcy)/vry)**2
        if d < 1.0:
            alpha = 0.38 * max(0, 1 - d**0.38)
            ref[y, x] = np.clip(ref[y,x]*(1-alpha) + np.array([0.12,0.09,0.07])*alpha, 0, 1)

# Hands
for y in range(hcy-35, hcy+68):
    for x in range(hcx-68, hcx+46):
        if 0<=y<H and 0<=x<W:
            d = ((x-(hcx-14))/58)**2*0.66+((y-hcy)/50)**2
            if d < 1.0:
                lf = 0.87-0.12*abs((x-hcx)/68)
                ref[y, x] = np.clip([0.78*lf, 0.64*lf, 0.47*lf], 0, 1)
for y in range(hcy-52, hcy+40):
    for x in range(hcx-30, hcx+70):
        if 0<=y<H and 0<=x<W:
            d = ((x-(hcx+20))/52)**2*0.62+((y-(hcy-6))/46)**2
            if d < 1.0:
                lf = 0.90-0.10*abs((x-(hcx+20))/52)
                ref[y, x] = np.clip([0.80*lf, 0.66*lf, 0.49*lf], 0, 1)

# Final smooth + extra on face
for c in range(3):
    ref[:, :, c] = gaussian_filter(ref[:, :, c], sigma=1.6)
for c in range(3):
    face_region = ref[y0f:y1f, x0f:x1f, c].copy()
    face_smooth = gaussian_filter(face_region, sigma=2.8)
    ref[y0f:y1f, x0f:x1f, c] = np.where(face_in, face_smooth, ref[y0f:y1f, x0f:x1f, c])

ref_img = Image.fromarray((np.clip(ref,0,1)*255).astype(np.uint8), "RGB")
print("Reference built.")

from stroke_engine import Painter, ellipse_mask, anatomy_flow_field, spherical_flow
from art_catalog import get_style

leo = get_style("leonardo")
p = Painter(W, H)

# Bootstrap canvas
ref_arr = np.array(ref_img).astype(np.float32)/255.0
buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((H,W,4)).copy()
buf[:,:,0] = (ref_arr[:,:,2]*255).astype(np.uint8)
buf[:,:,1] = (ref_arr[:,:,1]*255).astype(np.uint8)
buf[:,:,2] = (ref_arr[:,:,0]*255).astype(np.uint8)
buf[:,:,3] = 255
p.canvas.surface.get_data()[:] = buf.tobytes()

# Figure mask — body + head
mask = np.zeros((H,W), dtype=np.float32)
for y in range(shoulder_y, min(940, H)):
    hw = body_hw(y)
    if hw > 0:
        mask[y, max(0,fig_cx-hw):min(W,fig_cx+hw)] = 1.0
# Neck
for y in range(neck_y0, neck_y1):
    t_n = (y-neck_y0)/max(1, neck_y1-neck_y0)
    nw = int(30+t_n*22)
    mask[y, max(0,ncx-nw):min(W,ncx+nw)] = 1.0
# Head
for y in range(fcy-fry-30, fcy+fry+30):
    for x in range(fcx-frx-32, fcx+frx+32):
        if 0<=y<H and 0<=x<W:
            d = ((x-fcx)/(frx+32))**2+((y-fcy)/(fry+32))**2
            if d < 1.0:
                mask[y, x] = 1.0
mask = gaussian_filter(mask, sigma=6.0)
mask = np.clip(mask, 0, 1)
mask_img = Image.fromarray((mask*255).astype(np.uint8), "L")
p.set_figure_mask(mask_img)
p._comp_map = p._build_composition_map(focal_xy=(fcx/W, fcy/H))

# Subtle texture
p.tone_ground(leo.ground_color, texture_strength=0.03)
buf2 = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((H,W,4)).copy()
blend = 1.0 - mask*0.12
for c_ref, c_cairo in [(0,2),(1,1),(2,0)]:
    ch = ref_arr[:,:,c_ref]*255
    buf2[:,:,c_cairo] = np.clip(ch*blend + buf2[:,:,c_cairo]*(1-blend), 0, 255).astype(np.uint8)
buf2[:,:,3] = 255
p.canvas.surface.get_data()[:] = buf2.tobytes()

# ── Focused passes ────────────────────────────────────────────────────────────
sphere_f = spherical_flow(W, H, fcx, fcy, frx, fry)
face_f   = anatomy_flow_field(W, H, fcx, fcy, frx, fry, gradient_fallback=sphere_f)

face_m  = ellipse_mask(W, H, fcx, fcy, int(frx*1.00), int(fry*0.98), feather=0.30)
eyes_m  = ellipse_mask(W, H, fcx, fcy-fry//4, int(frx*0.74), int(fry*0.43), feather=0.22)
lips_m  = ellipse_mask(W, H, lxp, lyp, int(frx*0.44), int(fry*0.22), feather=0.24)
hands_m = ellipse_mask(W, H, hcx, hcy, 74, 60, feather=0.30)

p.focused_pass(ref_img, face_m,  stroke_size=7,  n_strokes=2000, opacity=0.78, wet_blend=0.96, form_angles=face_f)
p.focused_pass(ref_img, eyes_m,  stroke_size=3,  n_strokes=1400, opacity=0.87, wet_blend=0.68, form_angles=face_f)
p.focused_pass(ref_img, lips_m,  stroke_size=3,  n_strokes=750,  opacity=0.90, wet_blend=0.68, form_angles=face_f)
p.focused_pass(ref_img, hands_m, stroke_size=6,  n_strokes=650,  opacity=0.80, wet_blend=0.90, form_angles=None)
print("  focused_pass")

# Post-stroke face smoothing
buf3 = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((H,W,4)).copy()
y0s, y1s = max(0,fcy-fry-6), min(H,fcy+fry+6)
x0s, x1s = max(0,fcx-frx-6), min(W,fcx+frx+6)
for ci in range(3):
    region = buf3[y0s:y1s, x0s:x1s, ci].astype(np.float32)
    smooth_r = gaussian_filter(region, sigma=3.0)
    h_c, w_c = region.shape
    # Build face blend mask aligned to the crop
    face_blend = np.zeros((h_c, w_c), dtype=np.float32)
    # Offset within the face_in array
    fy_off = max(0, y0s - y0f)
    fx_off = max(0, x0s - x0f)
    fy_end = min(y1f - y0f, fy_off + h_c)
    fx_end = min(x1f - x0f, fx_off + w_c)
    dst_h = fy_end - fy_off
    dst_w = fx_end - fx_off
    face_blend[:dst_h, :dst_w] = face_in[fy_off:fy_end, fx_off:fx_end].astype(np.float32)
    buf3[y0s:y1s, x0s:x1s, ci] = np.clip(
        region*(1-face_blend*0.70) + smooth_r*face_blend*0.70, 0, 255
    ).astype(np.uint8)
p.canvas.surface.get_data()[:] = buf3.tobytes()
print("  face smoothed")

p.place_lights(ref_img, stroke_size=4, n_strokes=700)

# Sfumato
p.sfumato_veil_pass(ref_img, n_veils=10, blur_radius=7.0, warmth=0.28, veil_opacity=0.040, edge_only=False)
p.sfumato_veil_pass(ref_img, n_veils=8,  blur_radius=9.5, warmth=0.32, veil_opacity=0.032, edge_only=True)
print("  sfumato")

# Session 125: chromatic aerial perspective
p.chromatic_aerial_perspective_pass(
    sky_fraction=0.44, cool_r=0.54, cool_g=0.62, cool_b=0.78,
    haze_strength=0.24, desat_strength=0.28, haze_lift=0.09,
    gamma=1.12, blur_radius=22.0, opacity=0.85,
)
print("  aerial_perspective (s125)")

p.albani_arcadian_grace_pass(
    peach_r=0.022, peach_g=0.008, sky_b=0.028, sky_r=0.007,
    ambient_lift=0.004, blur_radius=4.0, opacity=0.14,
)
print("  albani_grace")

p.glaze(leo.glazing, opacity=0.065)
p.glaze((0.58, 0.42, 0.18), opacity=0.038)

p.edge_lost_and_found_pass(
    focal_xy=(fcx/W, fcy/H), found_radius=0.34,
    found_sharpness=0.52, lost_blur=2.0, strength=0.25, figure_only=False,
)

p.finish(vignette=0.32, crackle=False)
print("  finish")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s125_portrait_v7.png")
p.save(out)
print(f"Saved: {out}")
