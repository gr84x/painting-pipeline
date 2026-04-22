"""Session 125 v2 — Mona Lisa sfumato portrait, improved reference."""
import sys, os, numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W, H = 780, 1040

# ─── Build a luminous synthetic reference ─────────────────────────────────────
ref = np.zeros((H, W, 3), dtype=np.float32)

# ── Sky / background — cool blue-grey atmosphere ──────────────────────────────
for y in range(H):
    t = y / H
    # Pale warm-grey lower, cool blue-grey upper
    ref[y, :, 0] = np.clip(0.62 + t * 0.22, 0, 1)
    ref[y, :, 1] = np.clip(0.66 + t * 0.18, 0, 1)
    ref[y, :, 2] = np.clip(0.76 - t * 0.20, 0, 1)

# ── Left rocky landscape  ─────────────────────────────────────────────────────
for x in range(W // 2):
    xn = x / (W // 2)
    ridge = int(H * 0.30 + xn * H * 0.10 + np.sin(x * 0.06) * H * 0.025)
    for y in range(ridge, H):
        d = min(1.0, (y - ridge) / max(1, H - ridge))
        r = 0.38 + d * 0.20
        g = 0.42 + d * 0.18
        b = 0.44 + d * 0.12
        ref[y, x] = np.clip([r, g, b], 0, 1)

# ── Right landscape — slightly lower  ────────────────────────────────────────
for x in range(W // 2, W):
    xn = (x - W // 2) / (W // 2)
    ridge = int(H * 0.36 + xn * H * 0.06 + np.sin(x * 0.05) * H * 0.020)
    for y in range(ridge, H):
        d = min(1.0, (y - ridge) / max(1, H - ridge))
        r = 0.36 + d * 0.22
        g = 0.40 + d * 0.20
        b = 0.42 + d * 0.14
        ref[y, x] = np.clip([r, g, b], 0, 1)

# Water glint mid-right
wy1, wy2 = int(H * 0.42), int(H * 0.50)
wx1, wx2 = int(W * 0.54), int(W * 0.80)
for y in range(wy1, wy2):
    for x in range(wx1, wx2):
        ty = (y - wy1) / max(1, wy2 - wy1)
        ref[y, x] = np.clip([0.50 + ty*0.08, 0.60 + ty*0.04, 0.72 - ty*0.06], 0, 1)

# Winding path — left side, slightly lighter than rock
for i in range(120):
    pt = i / 120
    px = int(W * 0.03 + pt * W * 0.18 + np.sin(pt * 7) * W * 0.030)
    py = int(H * 0.28 + pt * H * 0.42)
    pw = max(1, int(5 * (1 - pt)))
    for dx in range(-pw, pw + 1):
        nx, ny = px + dx, py
        if 0 <= nx < W and 0 <= ny < H:
            ref[ny, nx] = np.clip([0.52, 0.50, 0.44], 0, 1)

# ── Figure body — dark forest-green dress, three-quarter pose ─────────────────
fig_cx = int(W * 0.52)
shoulder_w = 148
for y in range(88, min(910, H)):
    bt = (y - 88) / 822
    if bt < 0.08:
        hw = int(shoulder_w * bt / 0.08)
    elif bt < 0.30:
        hw = shoulder_w
    else:
        hw = int(shoulder_w + (bt - 0.30) * 60)
    x1, x2 = max(0, fig_cx - hw), min(W, fig_cx + hw)
    for x in range(x1, x2):
        xn = (x - x1) / max(1, x2 - x1) * 2 - 1  # -1..1
        # Upper-left lighting — left side brighter
        light = 1.0 - 0.20 * xn - 0.08 * bt
        # Forest green dress
        ref[y, x] = np.clip([0.10 * light, 0.16 * light, 0.12 * light], 0, 1)

# ── Neckline — thin amber trim ────────────────────────────────────────────────
trim_y1, trim_y2 = 392, 408
trim_x1, trim_x2 = fig_cx - 72, fig_cx + 84
ref[trim_y1:trim_y2, trim_x1:trim_x2] = [0.72, 0.56, 0.24]

# ── Gauze wrap — semi-transparent ivory over chest ────────────────────────────
gy1, gy2, gx1, gx2 = 408, 640, fig_cx - 88, fig_cx + 98
for y in range(gy1, gy2):
    for x in range(gx1, gx2):
        if 0 <= y < H and 0 <= x < W:
            existing = ref[y, x].copy()
            ref[y, x] = np.clip(existing * 0.70 + np.array([0.64, 0.62, 0.54]) * 0.30, 0, 1)

# ── Neck — luminous warm ivory ────────────────────────────────────────────────
ncx = fig_cx + 8
for y in range(305, 420):
    nw = 32
    for x in range(ncx - nw, ncx + nw):
        if 0 <= x < W:
            t = abs(x - ncx) / nw
            lf = 1.0 - 0.18 * t
            ref[y, x] = np.clip([0.85 * lf, 0.70 * lf, 0.52 * lf], 0, 1)

# ── Face — luminous, upper-left lit, smooth ───────────────────────────────────
fcx, fcy = fig_cx + 5, int(H * 0.245)
frx, fry = 86, 108

ys_g, xs_g = np.mgrid[fcy - fry:fcy + fry, fcx - frx:fcx + frx]
fxg = (xs_g - fcx) / frx
fyg = (ys_g - fcy) / fry
face_in = (fxg ** 2 + fyg ** 2) <= 1.0

# Upper-left light; right/bottom side slightly shadowed
light_g = np.clip(1.10 - 0.30 * fxg - 0.20 * fyg, 0.52, 1.18)
# Shadow at chin / jaw
chin_shadow = np.clip((fyg - 0.55) * 0.35, 0.0, 0.18)

skin_r = np.clip((0.86 - chin_shadow) * light_g, 0, 1)
skin_g = np.clip((0.70 - chin_shadow * 0.8) * light_g, 0, 1)
skin_b = np.clip((0.52 - chin_shadow * 0.6) * light_g, 0, 1)

y0, y1a = fcy - fry, fcy + fry
x0, x1a = fcx - frx, fcx + frx
ref[y0:y1a, x0:x1a, 0] = np.where(face_in, skin_r,  ref[y0:y1a, x0:x1a, 0])
ref[y0:y1a, x0:x1a, 1] = np.where(face_in, skin_g,  ref[y0:y1a, x0:x1a, 1])
ref[y0:y1a, x0:x1a, 2] = np.where(face_in, skin_b,  ref[y0:y1a, x0:x1a, 2])

# High forehead — smooth, hairline recedes softly
for y in range(fcy - fry, fcy - fry + 26):
    for x in range(fcx - frx, fcx + frx):
        if 0 <= y < H and 0 <= x < W and face_in[y - (fcy-fry), x - (fcx-frx)]:
            t = (y - (fcy - fry)) / 26
            ref[y, x] = np.clip(ref[y, x] * (0.92 + 0.08 * t), 0, 1)

# ── Eyes — dark, heavy-lidded, direct gaze ────────────────────────────────────
for ex_off, ew in [(-30, 15), (22, 14)]:
    ex, ey = fcx + ex_off, fcy - 12
    # Iris
    for dy in range(-8, 9):
        for dx in range(-ew, ew + 1):
            nx, ny = ex + dx, ey + dy
            if 0 <= nx < W and 0 <= ny < H:
                d = (dx / ew) ** 2 + (dy / 8) ** 2
                if d < 1.0:
                    ref[ny, nx] = [0.16, 0.11, 0.07]
    # Heavy upper lid shadow
    for dy in range(-11, -6):
        for dx in range(-ew - 2, ew + 3):
            nx, ny = ex + dx, ey + dy
            if 0 <= nx < W and 0 <= ny < H:
                d = (dx / (ew + 2)) ** 2 + (dy / 6) ** 2
                if d < 1.0:
                    ref[ny, nx] = np.clip(ref[ny, nx] * 0.62, 0, 1)

# Eyebrows — very faint, barely there (as per prompt: sparse/shaved)
for ex_off in [-30, 22]:
    ebx, eby = fcx + ex_off, fcy - 34
    for y in range(eby - 3, eby + 3):
        for x in range(ebx - 11, ebx + 13):
            if 0 <= x < W and 0 <= y < H:
                ref[y, x] = np.clip(ref[y, x] * 0.88 + np.array([0.32, 0.24, 0.16]) * 0.12, 0, 1)

# ── Nose — straight, refined ─────────────────────────────────────────────────
for y in range(fcy + 5, fcy + 38):
    nt = (y - fcy - 5) / 33
    for x in range(fcx - 5, fcx + 7):
        if 0 <= y < H and 0 <= x < W:
            t = abs(x - fcx) / 7
            shadow = 0.07 * (1 - t) * nt
            ref[y, x] = np.clip(ref[y, x] - shadow, 0, 1)

# ── Lips — small, ambiguous slight smile ─────────────────────────────────────
lxp, lyp = fcx + 2, fcy + 48
for y in range(lyp - 8, lyp + 9):
    for x in range(lxp - 18, lxp + 18):
        if 0 <= y < H and 0 <= x < W:
            d = ((x - lxp) / 18) ** 2 + ((y - lyp) / 8) ** 2
            if d < 1.0:
                # Slight upward curve at corners — ambiguous
                corner_lift = abs((x - lxp) / 18) ** 2 * 0.05
                ref[y, x] = np.clip([0.66, 0.43 + corner_lift, 0.38], 0, 1)

# ── Hair — dark brown, center-parted, soft waves ──────────────────────────────
for y in range(fcy - fry - 22, fcy + fry - 10):
    for x in range(fcx - frx - 25, fcx + frx + 25):
        if 0 <= y < H and 0 <= x < W:
            fxl = (x - fcx) / (frx + 25)
            fyl = (y - fcy) / fry
            in_face = (fxl ** 2 + fyl ** 2) < 0.82
            if not in_face and abs(fxl) > 0.44:
                wave = np.sin((y - fcy) * 0.10) * 0.020
                ref[y, x] = np.clip([0.24 + wave, 0.17, 0.11], 0, 1)

# ── Dark translucent veil over crown ─────────────────────────────────────────
vcx, vcy = fcx, fcy - fry + 14
vrx, vry = 93, 38
for y in range(vcy - vry, vcy + vry):
    for x in range(vcx - vrx, vcx + vrx):
        if 0 <= y < H and 0 <= x < W:
            d = ((x - vcx) / vrx) ** 2 + ((y - vcy) / vry) ** 2
            if d < 1.0:
                alpha = 0.45 * (1 - d ** 0.5)
                ref[y, x] = np.clip(ref[y, x] * (1 - alpha) + np.array([0.11, 0.08, 0.06]) * alpha, 0, 1)

# ── Hands — right over left, lower center ────────────────────────────────────
hcx, hcy = fig_cx - 4, int(H * 0.782)

# Left hand (underneath)
for y in range(hcy - 30, hcy + 62):
    for x in range(hcx - 62, hcx + 42):
        if 0 <= y < H and 0 <= x < W:
            d = ((x - (hcx - 12)) / 55) ** 2 * 0.7 + ((y - hcy) / 46) ** 2
            if d < 1.0:
                lf = 0.88 - 0.12 * abs((x - hcx) / 62)
                ref[y, x] = np.clip([0.78 * lf, 0.63 * lf, 0.46 * lf], 0, 1)

# Right hand (on top / draped over)
for y in range(hcy - 48, hcy + 36):
    for x in range(hcx - 30, hcx + 66):
        if 0 <= y < H and 0 <= x < W:
            d = ((x - (hcx + 18)) / 48) ** 2 * 0.65 + ((y - (hcy - 6)) / 42) ** 2
            if d < 1.0:
                lf = 0.90 - 0.10 * abs((x - (hcx + 18)) / 48)
                ref[y, x] = np.clip([0.80 * lf, 0.65 * lf, 0.48 * lf], 0, 1)

# ── Soften reference with gentle blur ────────────────────────────────────────
for c in range(3):
    ref[:, :, c] = gaussian_filter(ref[:, :, c], sigma=2.2)

ref_img = Image.fromarray((np.clip(ref, 0, 1) * 255).astype(np.uint8), "RGB")

# ── Figure mask ───────────────────────────────────────────────────────────────
mask = np.zeros((H, W), dtype=np.float32)
# Body
for y in range(88, min(910, H)):
    bt = (y - 88) / 822
    if bt < 0.08:
        hw = int(148 * bt / 0.08)
    elif bt < 0.30:
        hw = 148
    else:
        hw = int(148 + (bt - 0.30) * 60)
    x1m, x2m = max(0, fig_cx - hw), min(W, fig_cx + hw)
    mask[y, x1m:x2m] = 1.0
# Head (generous to include hair / veil)
for y in range(fcy - fry - 25, fcy + fry + 25):
    for x in range(fcx - frx - 28, fcx + frx + 28):
        if 0 <= y < H and 0 <= x < W:
            d = ((x - fcx) / (frx + 28)) ** 2 + ((y - fcy) / (fry + 28)) ** 2
            if d < 1.0:
                mask[y, x] = 1.0
mask = gaussian_filter(mask, sigma=5.5)
mask = np.clip(mask, 0, 1)
mask_img = Image.fromarray((mask * 255).astype(np.uint8), "L")

print("Reference synthesized. Running stroke pipeline…")

# ─── Stroke engine ───────────────────────────────────────────────────────────
from stroke_engine import Painter, ellipse_mask, anatomy_flow_field, spherical_flow
from art_catalog import get_style

leo = get_style("leonardo")
p = Painter(W, H)
p.set_figure_mask(mask_img)
p._comp_map = p._build_composition_map(focal_xy=p._derive_focal_xy())
p.seal_background(ref_img)

# Warm ochre imprimatura
p.tone_ground(leo.ground_color, texture_strength=0.09)
print("  tone_ground")

# Monochrome underpainting
p.underpainting(ref_img, stroke_size=28, n_strokes=120)
print("  underpainting")

# Broad tonal masses
p.block_in(ref_img, stroke_size=24, n_strokes=280)
print("  block_in")

# Form build-up — medium strokes
p.build_form(ref_img, stroke_size=9, n_strokes=700)
print("  build_form")

# ── Focused portrait passes ───────────────────────────────────────────────────
sphere_f = spherical_flow(W, H, fcx, fcy, frx, fry)
face_f = anatomy_flow_field(W, H, fcx, fcy, frx, fry, gradient_fallback=sphere_f)

face_m = ellipse_mask(W, H, fcx, fcy, int(frx * 1.04), int(fry * 1.00), feather=0.28)
eyes_m = ellipse_mask(W, H, fcx, fcy - fry // 4, int(frx * 0.78), int(fry * 0.46), feather=0.22)
lips_m = ellipse_mask(W, H, lxp, lyp, int(frx * 0.48), int(fry * 0.24), feather=0.25)
hands_m = ellipse_mask(W, H, hcx, hcy, 70, 55, feather=0.30)

p.focused_pass(ref_img, face_m,  stroke_size=8, n_strokes=1600, opacity=0.84, wet_blend=0.90, form_angles=face_f)
p.focused_pass(ref_img, eyes_m,  stroke_size=4, n_strokes=1000, opacity=0.87, wet_blend=0.55, form_angles=face_f)
p.focused_pass(ref_img, lips_m,  stroke_size=4, n_strokes=600,  opacity=0.88, wet_blend=0.55, form_angles=face_f)
p.focused_pass(ref_img, hands_m, stroke_size=6, n_strokes=500,  opacity=0.80, wet_blend=0.82, form_angles=None)
print("  focused_pass")

# Highlights — specular lights
p.place_lights(ref_img, stroke_size=5, n_strokes=600)
print("  place_lights")

# ── Sfumato veil — Leonardo's defining technique ──────────────────────────────
p.sfumato_veil_pass(
    ref_img, n_veils=12, blur_radius=7.5, warmth=0.30,
    veil_opacity=0.055, edge_only=True,
)
print("  sfumato_veil")

# ── Session 125: chromatic aerial perspective ─────────────────────────────────
p.chromatic_aerial_perspective_pass(
    sky_fraction=0.48, cool_r=0.54, cool_g=0.62, cool_b=0.78,
    haze_strength=0.20, desat_strength=0.24, haze_lift=0.07,
    gamma=1.18, blur_radius=18.0, opacity=0.75,
)
print("  aerial_perspective (s125)")

# ── Albani arcadian pass — sky-reflected shadow fill ─────────────────────────
p.albani_arcadian_grace_pass(
    peach_r=0.028, peach_g=0.010, sky_b=0.034, sky_r=0.010,
    ambient_lift=0.006, blur_radius=4.5, opacity=0.18,
)
print("  albani_grace")

# Warm Leonardo glaze
p.glaze(leo.glazing, opacity=0.055)
p.glaze((0.60, 0.44, 0.20), opacity=0.040)

# Edge lost-and-found
p.edge_lost_and_found_pass(
    focal_xy=(fcx / W, fcy / H), found_radius=0.30,
    found_sharpness=0.48, lost_blur=1.6, strength=0.30, figure_only=False,
)
print("  edge_lost_found")

# NO crackle — it was obscuring the composition
p.finish(vignette=0.46, crackle=False)
print("  finish")

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s125_portrait_v2.png")
p.save(out_path)
print(f"\nSaved: {out_path}")
