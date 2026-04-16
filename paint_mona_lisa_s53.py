"""
paint_mona_lisa_s53.py — Session 53 portrait painting.

Paints a Mona Lisa-inspired portrait using the full stroke-engine pipeline:
  - Synthetic reference image constructed per the prompt description
  - Leonardo sfumato palette and technique
  - sfumato_veil_pass()            — dissolve all edges into smoke
  - weyden_angular_shadow_pass()   — (session 53) refine shadow geometry
  - aerial_perspective_pass()      — atmospheric depth in the background landscape
  - penumbra_zone_pass()           — warm blush in the light-to-shadow transition

Composition (per the prompt):
  Woman, half-length, right of centre, three-quarter pose.
  Oval face, faint brows, dark heavy-lidded eyes, ambiguous lip corners.
  Dark hair parted centre, dark translucent veil.
  Dark forest-green / blue-black dress, amber neckline trim, gauze wrap.
  Dreamlike geological landscape: winding path left, river middle-distance,
  rocky terrain, left horizon slightly higher than right — subtle uncanny tilt.
  Sfumato throughout; cool atmospheric haze; warm ochre foreground, pale
  blue-grey far distance.
"""

import sys
import os
import math

sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter

W, H = 780, 1080


# ─────────────────────────────────────────────────────────────────────────────
# Reference image construction
# ─────────────────────────────────────────────────────────────────────────────

def make_reference() -> Image.Image:
    """
    Construct a richly coloured synthetic reference that encodes the composition
    described in the prompt.  The reference is blurred before painting so that
    the stroke engine operates on smooth colour masses rather than hard pixels.
    """
    ref = np.zeros((H, W, 3), dtype=np.float32)

    # ── Sky / upper background: pale blue-grey, lightening toward the top ───────
    sky_top    = np.array([0.72, 0.74, 0.78])   # pale near-white at the top
    sky_bottom = np.array([0.42, 0.48, 0.58])   # deeper cool blue at horizon
    sky_band   = int(H * 0.62)
    for y in range(sky_band):
        t = y / sky_band
        ref[y, :] = sky_top * (1 - t) + sky_bottom * t

    # ── Landscape below sky ───────────────────────────────────────────────────
    # The prompt specifies: left horizon slightly HIGHER than right (subtle tilt).
    # Left side: craggy rocky terrain, winding path, more elevation
    # Right side: slightly lower horizon, flatter, more water suggestion

    # Horizon line: tilted slightly (left ~52% height, right ~56% height)
    def horizon_y(x: int) -> int:
        t = x / W
        return int(H * (0.52 + t * 0.04))   # left=52%, right=56%

    # Fill below horizon with landscape gradient
    for x in range(W):
        hy = horizon_y(x)
        for y in range(hy, H):
            t = (y - hy) / (H - hy)
            # Deep dusty olive-green → warm dark earth foreground
            far  = np.array([0.28, 0.30, 0.24])
            near = np.array([0.18, 0.14, 0.09])
            ref[y, x] = far * (1 - t) + near * t

    # ── Rocky crags — left side ────────────────────────────────────────────────
    # Several jagged rocky formations in the left background
    crag_c  = np.array([0.35, 0.33, 0.28])
    crag_sh = np.array([0.18, 0.17, 0.14])
    rock_formations = [
        # (cx, cy, rx, ry) — rough ellipses
        (int(W * 0.10), int(H * 0.45), int(W * 0.07), int(H * 0.06)),
        (int(W * 0.22), int(H * 0.42), int(W * 0.06), int(H * 0.08)),
        (int(W * 0.08), int(H * 0.40), int(W * 0.05), int(H * 0.05)),
    ]
    for cx, cy, rx, ry in rock_formations:
        for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
            for x in range(max(0, cx - rx), min(W, cx + rx + 1)):
                dx = (x - cx) / rx
                dy = (y - cy) / ry
                d = dx * dx + dy * dy
                if d <= 1.05:
                    shade = max(0, -dx * 0.5)   # light from left
                    c = crag_c * (1 - shade * 0.5) + crag_sh * shade * 0.5
                    fade = max(0.0, 1.0 - (d - 0.82) / 0.23) if d > 0.82 else 1.0
                    ref[y, x] = ref[y, x] * (1 - fade) + c * fade

    # ── Rocky crags — right side (lower, more muted) ──────────────────────────
    right_crags = [
        (int(W * 0.82), int(H * 0.49), int(W * 0.08), int(H * 0.05)),
        (int(W * 0.92), int(H * 0.46), int(W * 0.07), int(H * 0.06)),
    ]
    crag_r = np.array([0.38, 0.36, 0.30])
    for cx, cy, rx, ry in right_crags:
        for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
            for x in range(max(0, cx - rx), min(W, cx + rx + 1)):
                dx = (x - cx) / rx
                dy = (y - cy) / ry
                d = dx * dx + dy * dy
                if d <= 1.05:
                    fade = max(0.0, 1.0 - (d - 0.82) / 0.23) if d > 0.82 else 1.0
                    ref[y, x] = ref[y, x] * (1 - fade) + crag_r * fade

    # ── Winding path on left ──────────────────────────────────────────────────
    # Path meanders from lower-left toward the middle distance
    path_c = np.array([0.50, 0.46, 0.34])
    for seg in range(40):
        t = seg / 40.0
        # Serpentine path curving in from left edge toward centre
        px = int(W * (0.04 + t * 0.18 + 0.06 * math.sin(t * math.pi * 2.5)))
        py = int(H * (0.76 - t * 0.28))
        pw = max(3, int(W * 0.028 * (1 - t * 0.55)))
        for dy in range(-pw, pw + 1):
            for dx in range(-pw, pw + 1):
                fy, fx = py + dy, px + dx
                if 0 <= fy < H and 0 <= fx < W:
                    d_path = math.sqrt(dx * dx + dy * dy) / pw
                    if d_path <= 1.0:
                        fm = max(0.0, 1.0 - d_path * 0.8) * 0.6
                        ref[fy, fx] = ref[fy, fx] * (1 - fm) + path_c * fm

    # ── River / water in mid-distance ────────────────────────────────────────
    river_y  = int(H * 0.47)
    river_h  = int(H * 0.022)
    river_xL = int(W * 0.25)
    river_xR = int(W * 0.44)
    river_c  = np.array([0.42, 0.52, 0.64])   # cool steel-blue
    for y in range(river_y - river_h, river_y + river_h):
        if 0 <= y < H:
            for x in range(river_xL, river_xR):
                if 0 <= x < W:
                    et = max(0.0, 1.0 - abs(y - river_y) / river_h)
                    ref[y, x] = ref[y, x] * (1 - et * 0.62) + river_c * et * 0.62

    # ── Sparse vegetation ─────────────────────────────────────────────────────
    veg_c = np.array([0.22, 0.28, 0.16])
    for veg in [
        (int(W * 0.16), int(H * 0.55), int(W * 0.03), int(H * 0.04)),
        (int(W * 0.30), int(H * 0.57), int(W * 0.02), int(H * 0.03)),
        (int(W * 0.85), int(H * 0.56), int(W * 0.03), int(H * 0.04)),
    ]:
        cx, cy, rx, ry = veg
        for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
            for x in range(max(0, cx - rx), min(W, cx + rx + 1)):
                dx = (x - cx) / max(rx, 1)
                dy = (y - cy) / max(ry, 1)
                if dx * dx + dy * dy <= 1.0:
                    ref[y, x] = veg_c

    # ─────────────────────────────────────────────────────────────────────────
    # Figure
    # ─────────────────────────────────────────────────────────────────────────

    # Figure is right of centre (3/4 view, body ~45° right, face nearly forward)
    fig_cx   = int(W * 0.54)   # slightly right of centre
    fig_top  = int(H * 0.06)   # top of figure (above head)

    # ── Torso — dark forest-green / blue-black dress ──────────────────────────
    torso_top    = int(H * 0.36)
    torso_bottom = H - 10
    # Body turned 45° → slight asymmetry in shoulder width
    dress_lit    = np.array([0.05, 0.18, 0.14])   # lit forest-green
    dress_shadow = np.array([0.03, 0.06, 0.10])   # shadow blue-black

    for y in range(torso_top, torso_bottom):
        taper = (y - torso_top) / max(1, torso_bottom - torso_top)
        hw = int(W * (0.14 + taper * 0.12))   # widens toward bottom
        x_shift = int(W * 0.018)              # slight rightward lean (3/4 pose)
        for x in range(max(0, fig_cx - hw - x_shift), min(W, fig_cx + hw)):
            # Light from upper left
            side_t = (x - (fig_cx - x_shift)) / (hw * 2.0)
            col = dress_lit * (1 - side_t * 0.85) + dress_shadow * side_t * 0.85
            ref[y, x] = col

    # ── Gauze wrap — semi-transparent over chest ──────────────────────────────
    gauze_c = np.array([0.22, 0.30, 0.25])
    for y in range(int(H * 0.38), int(H * 0.52)):
        for x in range(fig_cx - int(W * 0.18), fig_cx + int(W * 0.13)):
            if 0 <= x < W:
                gm = 0.18 * max(0.0, 1 - abs(x - (fig_cx - int(W * 0.02))) / (W * 0.14))
                ref[y, x] = ref[y, x] * (1 - gm) + gauze_c * gm

    # ── Amber neckline trim ───────────────────────────────────────────────────
    neck_y = int(H * 0.405)
    trim_c = np.array([0.80, 0.56, 0.20])
    for y in range(neck_y - 3, neck_y + 7):
        if 0 <= y < H:
            for x in range(fig_cx - int(W * 0.09), fig_cx + int(W * 0.07)):
                if 0 <= x < W:
                    ref[y, x] = trim_c

    # ── Skin tones — lit face area ────────────────────────────────────────────
    skin_light  = np.array([0.90, 0.78, 0.56])   # warm ivory
    skin_shadow = np.array([0.48, 0.35, 0.22])   # raw sienna shadow

    # Neck
    neck_cx = fig_cx - int(W * 0.012)
    neck_hw = int(W * 0.055)
    for y in range(int(H * 0.28), int(H * 0.40)):
        for x in range(neck_cx - neck_hw, neck_cx + neck_hw):
            if 0 <= x < W:
                lt = max(0.0, 1 - abs(x - (neck_cx - neck_hw // 4)) / (neck_hw * 0.8))
                ref[y, x] = skin_shadow * (1 - lt) + skin_light * lt

    # ── Face — oval, smooth, high forehead ───────────────────────────────────
    # Face is almost directly facing viewer (turned slightly rightward from body)
    face_cx = fig_cx - int(W * 0.015)   # very slightly left of figure centre
    face_cy = int(H * 0.196)
    face_rx = int(W * 0.125)            # horizontal radius
    face_ry = int(W * 0.168)            # vertical radius (tall oval)

    # High forehead: face_cy shifted slightly downward (hairline recedes at temples)
    for y in range(face_cy - face_ry - 10, face_cy + face_ry + 10):
        for x in range(face_cx - face_rx - 10, face_cx + face_rx + 10):
            if 0 <= y < H and 0 <= x < W:
                dx = (x - face_cx) / face_rx
                dy = (y - face_cy) / face_ry
                # Slightly narrowed at top (temple recession) — multiply x radius at top
                temple_factor = 1.0 + max(0.0, -dy) * 0.25
                d = (dx * temple_factor) ** 2 + dy * dy
                if d <= 1.06:
                    # Light from upper left
                    nl = max(0.0, min(1.0, (-0.58 * dx - 0.52 * dy) * 1.45 + 0.30))
                    col = skin_shadow * (1 - nl) + skin_light * nl
                    fade = max(0.0, 1.0 - (d - 0.86) / 0.20) if d > 0.86 else 1.0
                    ref[y, x] = ref[y, x] * (1 - fade) + col * fade

    # ── Hair — dark brown, centre-parted, soft waves ──────────────────────────
    hair_c = np.array([0.18, 0.11, 0.05])
    hair_s = np.array([0.06, 0.04, 0.02])
    # Hair extends wider than face, falls on either side
    for y in range(face_cy - face_ry - 8, face_cy + int(face_ry * 0.70)):
        for x in range(face_cx - int(face_rx * 1.7), face_cx + int(face_rx * 1.6)):
            if 0 <= y < H and 0 <= x < W:
                fdx = (x - face_cx) / face_rx
                fdy = (y - face_cy) / face_ry
                face_d = fdx * fdx + fdy * fdy
                outer_d = ((x - face_cx) / (face_rx * 1.58)) ** 2 + \
                          ((y - face_cy) / (face_ry * 1.05)) ** 2
                if outer_d <= 1.05 and face_d >= 0.88:
                    ht = max(0.0, (x - face_cx) / (face_rx + W * 0.01))
                    ref[y, x] = hair_c * (1 - ht * 0.42) + hair_s * ht * 0.42

    # ── Veil — dark translucent over crown and shoulders ─────────────────────
    veil_c = np.array([0.07, 0.05, 0.08])
    for y in range(face_cy - face_ry - 2, face_cy + int(face_ry * 0.32)):
        for x in range(face_cx - int(face_rx * 1.55), face_cx + int(face_rx * 1.45)):
            if 0 <= y < H and 0 <= x < W:
                fdx = (x - face_cx) / face_rx
                fdy = (y - face_cy) / face_ry
                if fdx * fdx + fdy * fdy >= 0.88:
                    ref[y, x] = veil_c * 0.85 + ref[y, x] * 0.15

    # ── Eyes — dark, heavy-lidded, direct gaze ────────────────────────────────
    # Very faint brows (nearly absent)
    eye_sep = int(face_rx * 0.44)
    eye_y   = face_cy - int(face_ry * 0.06)
    eye_rx  = int(face_rx * 0.22)
    eye_ry  = int(face_ry * 0.10)
    iris_c  = np.array([0.10, 0.08, 0.06])
    lid_c   = np.array([0.12, 0.09, 0.07])

    for ex in [face_cx - eye_sep, face_cx + eye_sep]:
        for dy_e in range(-eye_ry - 2, eye_ry + 3):
            for dx_e in range(-eye_rx - 2, eye_rx + 3):
                ey = eye_y + dy_e
                ex2 = ex + dx_e
                if 0 <= ey < H and 0 <= ex2 < W:
                    de = (dx_e / eye_rx) ** 2 + (dy_e / eye_ry) ** 2
                    if de <= 1.05:
                        col = lid_c if abs(dy_e) > eye_ry * 0.55 else iris_c
                        fade_e = max(0.0, 1.0 - de * 0.55)
                        ref[ey, ex2] = ref[ey, ex2] * (1 - fade_e) + col * fade_e

    # ── Nose — straight, refined, subtle ─────────────────────────────────────
    nose_cx = face_cx + int(face_rx * 0.06)   # slight rightward offset (3/4 pose)
    nose_cy = face_cy + int(face_ry * 0.26)
    nose_c  = np.array([0.54, 0.38, 0.26])    # warm shadow under nose
    for dy_n in range(-int(face_ry * 0.05), int(face_ry * 0.05) + 1):
        for dx_n in range(-int(face_rx * 0.12), int(face_rx * 0.12) + 1):
            nx, ny = nose_cx + dx_n, nose_cy + dy_n
            if 0 <= ny < H and 0 <= nx < W:
                dn = (dx_n / (face_rx * 0.11)) ** 2 + (dy_n / (face_ry * 0.045)) ** 2
                if dn <= 1.0:
                    ref[ny, nx] = ref[ny, nx] * 0.45 + nose_c * 0.55

    # ── Lips — closed, subtle upward corners (the ambiguous Mona Lisa smile) ──
    lip_cx = face_cx + int(face_rx * 0.05)
    lip_cy = face_cy + int(face_ry * 0.48)
    lip_c  = np.array([0.60, 0.36, 0.26])     # warm rose, not saturated red

    for dy_l in range(-int(face_ry * 0.055), int(face_ry * 0.058) + 1):
        for dx_l in range(-int(face_rx * 0.29), int(face_rx * 0.29) + 1):
            lx = lip_cx + dx_l
            ly = lip_cy + dy_l
            if 0 <= ly < H and 0 <= lx < W:
                # Slight upward bow at corners — ambiguous, not a full smile
                bow = abs(dx_l) / max(1, face_rx * 0.26)
                lry = face_ry * 0.050 * (1.0 + 0.14 * bow ** 2)
                dl  = (dx_l / (face_rx * 0.27)) ** 2 + (dy_l / lry) ** 2
                if dl <= 1.0:
                    fade_l = max(0.0, 1.0 - dl * 0.60)
                    ref[ly, lx] = ref[ly, lx] * (1 - fade_l) + lip_c * fade_l

    # ── Chin shadow ───────────────────────────────────────────────────────────
    chin_cy = face_cy + int(face_ry * 0.82)
    chin_c  = np.array([0.44, 0.30, 0.18])
    for dy_c in range(-int(face_ry * 0.10), int(face_ry * 0.06) + 1):
        for dx_c in range(-int(face_rx * 0.44), int(face_rx * 0.44) + 1):
            cx2, cy2 = face_cx + dx_c, chin_cy + dy_c
            if 0 <= cy2 < H and 0 <= cx2 < W:
                dc = (dx_c / (face_rx * 0.43)) ** 2 + (dy_c / (face_ry * 0.09)) ** 2
                if dc <= 1.0:
                    ref[cy2, cx2] = ref[cy2, cx2] * 0.55 + chin_c * 0.45

    # ── Hands — folded in lower-centre ───────────────────────────────────────
    hand_cx = fig_cx - int(W * 0.038)
    hand_cy = int(H * 0.725)
    hrx     = int(face_rx * 0.70)
    hry     = int(face_ry * 0.35)
    for dy_h in range(-hry, hry + 1):
        for dx_h in range(-hrx, hrx + 1):
            hx = hand_cx + dx_h
            hy = hand_cy + dy_h
            if 0 <= hy < H and 0 <= hx < W:
                dh = (dx_h / hrx) ** 2 + (dy_h / hry) ** 2
                if dh <= 1.0:
                    # Right hand draped over left (light on right side)
                    nl = max(0.0, min(1.0, 0.52 - dx_h / (hrx * 1.85)))
                    col = skin_shadow * (1 - nl) + skin_light * nl
                    fd  = max(0.0, 1.0 - (dh - 0.76) / 0.24) if dh > 0.76 else 1.0
                    ref[hy, hx] = ref[hy, hx] * (1 - fd) + col * fd

    # ── Apply gentle blur to smooth all transitions ───────────────────────────
    img = Image.fromarray((np.clip(ref, 0, 1) * 255).astype(np.uint8), "RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=3.2))
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Painting pipeline
# ─────────────────────────────────────────────────────────────────────────────

def paint(out_dir: str = ".") -> str:
    print("Building synthetic reference…")
    ref = make_reference()
    ref_path = os.path.join(out_dir, "mona_lisa_s53_ref.png")
    ref.save(ref_path)
    print(f"  Reference saved: {ref_path}")

    print("Initialising Painter…")
    p = Painter(W, H)

    # ── Warm ochre imprimatura (Leonardo's ground) ────────────────────────────
    print("Toning ground (warm ochre imprimatura)…")
    p.tone_ground((0.54, 0.46, 0.28), texture_strength=0.05)

    # ── Underpainting — dead-colour value structure ───────────────────────────
    print("Underpainting…")
    p.underpainting(ref, stroke_size=55, n_strokes=300)

    # ── Block in — colour masses, large strokes ───────────────────────────────
    print("Block in (large)…")
    p.block_in(ref, stroke_size=40, n_strokes=550)

    print("Block in (medium)…")
    p.block_in(ref, stroke_size=24, n_strokes=700)

    # ── Build form — directional strokes following surface curvature ──────────
    print("Build form…")
    p.build_form(ref, stroke_size=14, n_strokes=1100)

    print("Build form (fine)…")
    p.build_form(ref, stroke_size=7, n_strokes=800)

    # Save a base painting checkpoint
    base_path = os.path.join(out_dir, "mona_lisa_s53_base.png")
    p.save(base_path)
    print(f"  Base painting saved: {base_path}")

    # ── Session 53 improvement: weyden_angular_shadow_pass ────────────────────
    # This enriches the shadow geometry in the figure before the sfumato veil —
    # adding Weyden's cool-shadow quality and slightly sharpened penumbra edge
    # as a substrate that the sfumato will then soften.  The interaction between
    # the angular shadow structure and the sfumato veil produces a shadow that is
    # neither fully dissolved (Leonardo) nor sharply angular (Weyden) but something
    # in between: a shadow that has underlying geometric resolve but is wrapped in
    # atmospheric haze — exactly the quality of the Mona Lisa's face shadows.
    print("Weyden angular shadow pass (session 53)…")
    p.weyden_angular_shadow_pass(
        shadow_thresh  = 0.36,
        light_thresh   = 0.62,
        edge_sharpen   = 0.38,    # moderate — will be further softened by sfumato
        shadow_cool    = 0.06,    # subtle cool push — not Flemish-harsh
        highlight_cool = 0.03,    # very light cool on lit flesh
        opacity        = 0.55,    # blend at moderate strength
    )

    # ── Sfumato veil — the defining Leonardo technique ────────────────────────
    print("Sfumato veil pass…")
    p.sfumato_veil_pass(
        ref,
        n_veils       = 9,
        blur_radius   = 10.0,
        warmth        = 0.32,
        veil_opacity  = 0.048,
        edge_only     = True,
        chroma_dampen = 0.26,
    )

    # ── Penumbra zone pass — warm demitint (Titian's contribution via s51) ────
    print("Penumbra zone pass (demitint warmth)…")
    p.penumbra_zone_pass(
        light_thresh    = 0.62,
        shadow_thresh   = 0.36,
        penumbra_warmth = 0.07,
        penumbra_chroma = 0.05,
        opacity         = 0.60,
    )

    # ── Place final lights — impasto highlights ───────────────────────────────
    print("Place lights…")
    p.place_lights(ref, stroke_size=5, n_strokes=650)

    # ── Aerial perspective — atmospheric haze in upper background ─────────────
    print("Aerial perspective pass…")
    p.aerial_perspective_pass(
        sky_band     = 0.58,
        fade_power   = 2.0,
        desaturation = 0.55,
        cool_push    = 0.12,
        haze_lift    = 0.06,
        opacity      = 0.72,
    )

    # ── Warm amber unifying glaze ─────────────────────────────────────────────
    print("Final glaze (warm amber)…")
    p.glaze((0.62, 0.44, 0.14), opacity=0.055)

    # ── Finish: vignette + crackle ────────────────────────────────────────────
    print("Finishing (vignette + crackle)…")
    p.finish(vignette=0.50, crackle=True)

    out_path = os.path.join(out_dir, "mona_lisa_s53_final.png")
    p.save(out_path)
    print(f"\nPainting complete: {out_path}")
    return out_path


if __name__ == "__main__":
    result = paint(out_dir=os.path.dirname(os.path.abspath(__file__)))
    print("Done:", result)
