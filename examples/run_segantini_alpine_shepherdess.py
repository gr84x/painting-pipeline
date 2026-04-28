"""
run_segantini_alpine_shepherdess.py
Session 225 — Giovanni Segantini (1858–1899)
Alpine Symbolism / Neo-Impressionism

═══════════════════════════════════════════════════════════════════════════════
IMAGE DESCRIPTION: "Vigil at the Snowline"
═══════════════════════════════════════════════════════════════════════════════

Subject & Composition
─────────────────────
A lone shepherdess stands at centre-right of frame at the boundary between a
high alpine snowfield and a thin wedge of meadow.  She is viewed from slightly
below — the camera positioned perhaps a metre lower than her feet — so that she
cuts against the immense cold sky behind her rather than against the ground.
This low viewpoint, characteristic of Segantini's peasant-dignity canvases,
gives her the involuntary monumentality of someone who has always lived at
altitude and simply occupies the landscape as a fact.  She faces three-quarter
left, her gaze directed across the valley into unseen distance.  A crook of
pale ash-wood rests lightly against her right shoulder; her left hand holds
the end.  Three white sheep graze in the near-left foreground, their backs
visible just above the snow, their heads down and invisible in the drift.

The Figure
──────────
The shepherdess is perhaps twenty-two, slight but wind-solidified.  She wears
a coarse dark wool dress — deep warm umber-brown — and a pale blue-white apron
folded up slightly at the hem from walking.  A white linen headscarf is tied
firmly under her chin, casting a shadow across her brow.  Her skin is the
weathered warm rose-peach of someone who spends every day above 2,000 metres:
never delicate, always alive.  Her expression is one of absolute interior
stillness: not melancholy, not longing, but the focused quietude of someone
whose attention is distributed across an enormous territory of air and snow
and silence, processing it all at once without effort.  She has been here so
long that the landscape has stopped being scenery and become simply her body
extended.

The Environment
───────────────
The foreground is a narrow tilted plane of refrozen snow, granular and
glittering.  Its shadows are not grey but a vivid violet-blue — the cold sky
reflecting in the crystalline surface at a flat angle.  Running diagonally
across the lower-left is a partially buried stone wall, its top course
exposed, the rough grey schist still speckled with frozen lichen.  Three
dark Engadine firs fill the far-left margin: almost black-green, their
branches holding small loads of snow, their trunks vertical and close as
sentries.  Behind the figure and the firs, the land drops away into the
valley — a vast blue-grey silence — before the opposite peaks rise again in
pale blue-white silhouette.  The sky is the architectural cobalt of extreme
altitude: utterly cloudless, intense as enamel, the blue deepening toward
the upper margin of the canvas.  Low in the right sky, the sun sits small
and white-hot, producing hard-edged shadows that cut clean across the snow
like geometry.

Technique & Palette
────────────────────
Technique: Giovanni Segantini's 'pennellate a virgola' — the stitch-weave
Divisionism.  Every surface is built from short parallel comma-strokes whose
direction follows the form: horizontal on flat snow, diagonal on the mountain
slope, curling along the volume of the figure and the sheep's backs.  Adjacent
strokes are chromatic neighbours — gold beside blue-violet, sage beside umber
— so the surface vibrates at viewing distance.  The ground is a warm primed
white; because strokes are laid dry on this ground, the white reads between
them as luminous optical matrix.

Palette:
  • Snow luminance:      (0.92, 0.96, 1.00) — pure highland diffuse white
  • Alpine sky blue:     (0.52, 0.72, 0.90) — cold clear atmosphere
  • Deep fir green:      (0.20, 0.36, 0.24) — conifer shadow passages
  • Golden ochre:        (0.84, 0.70, 0.32) — dry grass tufts through snow
  • Warm umber:          (0.38, 0.26, 0.16) — earth, bark, figure dress
  • Snow shadow mauve:   (0.68, 0.54, 0.72) — violet-blue in shaded snow
  • Pale sage:           (0.62, 0.78, 0.52) — sunlit lichen, meadow fringe

Mood & Intent
─────────────
The image attempts to convey what Segantini called "the purity of great
solitudes" — not the romantic loneliness of a figure lost in nature, but its
opposite: the composed sufficiency of a person completely at home in a world
that has made them larger, clearer, simpler.  The shepherdess is not dwarfed
by the alpine scale; she is equal to it.  The violet snow shadows and
intensified cobalt sky produce a quality of light that feels both hyper-real
and slightly visionary — the way very cold, very clear air makes everything
look more itself than it usually does.  The viewer should feel the specific
cold, the specific silence, the specific weight of responsibility that comes
with caring for other lives in a vast and indifferent terrain — and underneath
all that, a kind of joy in belonging precisely there.

═══════════════════════════════════════════════════════════════════════════════
IMPLEMENTATION
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from stroke_engine import Painter

W, H   = 780, 1080
OUTPUT = os.path.join(os.path.dirname(__file__), "segantini_alpine_shepherdess.png")


def build_reference() -> np.ndarray:
    """Construct a synthetic reference image for the Alpine Shepherdess scene."""
    rng = np.random.RandomState(225)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    xs = np.linspace(0, 1, W)[None, :]
    ys = np.linspace(0, 1, H)[:, None]

    # ── Sky — architectural cobalt deepening upward ──────────────────────────
    sky_r = 0.52 + 0.20 * ys          # cooler at top
    sky_g = 0.72 + 0.12 * ys
    sky_b = 0.95 - 0.08 * ys
    for ch, val in enumerate([sky_r, sky_g, sky_b]):
        ref[:, :, ch] = np.broadcast_to(val if val.shape == (H, 1) else val, (H, W))
    # Ensure sky uses correct scalar channel values
    ref[:, :, 0] = np.clip(0.52 + 0.20 * np.linspace(0, 1, H)[:, None], 0, 1)
    ref[:, :, 1] = np.clip(0.72 + 0.12 * np.linspace(0, 1, H)[:, None], 0, 1)
    ref[:, :, 2] = np.clip(0.95 - 0.08 * np.linspace(0, 1, H)[:, None], 0, 1)

    # ── Horizon ridge — far peaks in pale blue-white ─────────────────────────
    horizon_y = 0.38    # peaks sit at 38% down from top
    peak_vals = np.sin(xs[0] * np.pi * 3.0) * 0.04 + horizon_y
    ridge_mask = np.clip(1.0 - (ys[:, 0][:, None] - peak_vals[None, :]) / 0.06, 0, 1)
    ridge_col  = np.array([0.82, 0.88, 0.96])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - ridge_mask * 0.65) + ridge_col[ch] * ridge_mask * 0.65

    # ── Snowfield — main surface below sky ────────────────────────────────────
    snow_top   = 0.42
    snow_mask  = np.clip((ys[:, 0] - snow_top)[:, None] / 0.08, 0, 1)
    snow_base  = np.array([0.90, 0.93, 0.97])   # slightly blue-white
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - snow_mask) + snow_base[ch] * snow_mask

    # ── Snow violet shadows — diagonal shadow from firs (left) ───────────────
    shadow_x_fade = np.clip(1.0 - xs / 0.45, 0, 1)
    shadow_y_fade = np.clip((ys[:, 0] - 0.50)[:, None] / 0.30, 0, 1)
    shadow_mask   = shadow_x_fade * shadow_y_fade * 0.55
    shadow_col    = np.array([0.65, 0.52, 0.78])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - shadow_mask) + shadow_col[ch] * shadow_mask

    # Sun hard-shadow diagonal (right side of canvas)
    sun_shadow_mask = np.clip((0.75 - xs) / 0.10, 0, 1) * np.clip((ys[:, 0] - 0.55)[:, None] / 0.06, 0, 1)
    sun_shad_col    = np.array([0.60, 0.50, 0.76])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - sun_shadow_mask * 0.40) + sun_shad_col[ch] * sun_shadow_mask * 0.40

    # ── Snow granular texture (refractive glitter) ────────────────────────────
    glitter = rng.uniform(0, 1, (H, W)).astype(np.float32)
    glitter_mask = snow_mask * np.clip(glitter - 0.88, 0, 1) / 0.12
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + glitter_mask * 0.22, 0, 1)

    # ── Dark fir trees — left margin ─────────────────────────────────────────
    for tx, tw in [(0.04, 0.040), (0.11, 0.038), (0.17, 0.035)]:
        trunk_h = 0.55    # tree base at 55% down
        tree_top = 0.15   # top of tree
        for py in range(H):
            y_frac = py / H
            if not (tree_top < y_frac < trunk_h):
                continue
            tree_progress = (y_frac - tree_top) / (trunk_h - tree_top)
            half_w = tw * (0.15 + 0.85 * tree_progress) * W
            cx = int(tx * W)
            x0 = max(0, int(cx - half_w))
            x1 = min(W - 1, int(cx + half_w))
            if x0 >= x1:
                continue
            fir_col = np.array([0.16, 0.30, 0.18])
            for ch in range(3):
                ref[py, x0:x1, ch] = fir_col[ch]
        # Snow on branches — white cap at top
        cap_h = int(tree_top * H) + 8
        cx    = int(tx * W)
        x0    = max(0, cx - int(tw * 0.6 * W))
        x1    = min(W - 1, cx + int(tw * 0.6 * W))
        ref[max(0, cap_h - 4):cap_h, x0:x1, :] = [0.92, 0.96, 1.00]

    # ── Valley depth (background between firs and peaks) ─────────────────────
    valley_mask = np.clip(
        (1.0 - np.abs(xs - 0.50) / 0.22) * np.clip((0.42 - ys[:, 0])[:, None] / 0.08, 0, 1),
        0, 1)
    valley_col  = np.array([0.62, 0.72, 0.84])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - valley_mask * 0.55) + valley_col[ch] * valley_mask * 0.55

    # ── Stone wall — partial diagonal across lower-left ───────────────────────
    wall_y0 = 0.70
    wall_y1 = 0.76
    wall_x1 = 0.50
    wall_col = np.array([0.46, 0.44, 0.42])
    for py in range(int(wall_y0 * H), int(wall_y1 * H)):
        y_frac  = py / H
        x_end   = int(wall_x1 * W * (1.0 - (y_frac - wall_y0) / (wall_y1 - wall_y0) * 0.3))
        x_start = max(0, x_end - int(0.40 * W))
        ref[py, x_start:x_end, :] = wall_col
    # Lichen spots on wall
    for _ in range(60):
        lx = rng.randint(0, int(0.42 * W))
        ly = rng.randint(int(wall_y0 * H), int(wall_y1 * H))
        r2 = rng.randint(1, 4)
        lic = np.array([0.58, 0.62, 0.48])
        for dy in range(-r2, r2 + 1):
            for dx in range(-r2, r2 + 1):
                if dy * dy + dx * dx <= r2 * r2:
                    ry2, rx2 = ly + dy, lx + dx
                    if 0 <= ry2 < H and 0 <= rx2 < W:
                        ref[ry2, rx2, :] = lic

    # ── Three sheep — foreground left, partially in snow ─────────────────────
    sheep_positions = [(0.14, 0.64), (0.22, 0.67), (0.08, 0.70)]
    for scx, scy in sheep_positions:
        sw, sh2 = 0.068, 0.046
        for py in range(max(0, int((scy - sh2) * H)), min(H, int((scy + sh2) * H))):
            for px in range(max(0, int((scx - sw) * W)), min(W, int((scx + sw) * W))):
                fy = (py / H - scy) / sh2
                fx = (px / W - scx) / sw
                if fx * fx + fy * fy < 1.0:
                    # Wool white with slight warm tinge
                    ref[py, px, :] = [0.90 + rng.uniform(-0.04, 0.04),
                                      0.89 + rng.uniform(-0.03, 0.03),
                                      0.85 + rng.uniform(-0.03, 0.03)]
        # Small dark head (not visible in deep snow)
        hx, hy = int((scx + sw * 0.9) * W), int((scy - sh2 * 0.3) * H)
        for dy in range(-3, 4):
            for dx in range(-4, 5):
                if 0 <= hy + dy < H and 0 <= hx + dx < W:
                    ref[hy + dy, hx + dx, :] = [0.22, 0.16, 0.10]

    # ── The Shepherdess ───────────────────────────────────────────────────────
    fig_cx = 0.60    # centre x
    fig_cy = 0.52    # centre y of body (foot at 0.82)

    # Dress (dark umber-brown ellipse)
    dr_w, dr_h = 0.060, 0.220
    for py in range(max(0, int((fig_cy - dr_h) * H)), min(H, int((fig_cy + dr_h) * H))):
        for px in range(max(0, int((fig_cx - dr_w) * W)), min(W, int((fig_cx + dr_w) * W))):
            fy = (py / H - fig_cy) / dr_h
            fx = (px / W - fig_cx) / (dr_w * (0.7 + 0.3 * abs(fy)))
            if fx * fx + fy * fy < 1.0:
                shd = 0.85 + 0.15 * fx    # slight lit-right gradient
                ref[py, px, :] = [0.38 * shd, 0.26 * shd, 0.16 * shd]

    # Apron (pale blue-white, lower front)
    ap_cx, ap_cy = fig_cx - 0.005, fig_cy + 0.05
    ap_w, ap_h   = 0.030, 0.100
    for py in range(max(0, int((ap_cy - ap_h) * H)), min(H, int((ap_cy + ap_h) * H))):
        for px in range(max(0, int((ap_cx - ap_w) * W)), min(W, int((ap_cx + ap_w) * W))):
            fy = (py / H - ap_cy) / ap_h
            fx = (px / W - ap_cx) / ap_w
            if fx * fx + fy * fy < 1.0:
                ref[py, px, :] = [0.80, 0.84, 0.90]

    # Head (warm rose-peach)
    hd_cx, hd_cy = fig_cx + 0.010, fig_cy - dr_h + 0.030
    hd_r = 0.030
    for py in range(max(0, int((hd_cy - hd_r) * H)), min(H, int((hd_cy + hd_r) * H))):
        for px in range(max(0, int((hd_cx - hd_r) * W)), min(W, int((hd_cx + hd_r) * W))):
            fy = (py / H - hd_cy) / (hd_r * 1.15)
            fx = (px / W - hd_cx) / hd_r
            if fx * fx + fy * fy < 1.0:
                lit = 0.90 + 0.10 * (1.0 - fx)
                ref[py, px, :] = [0.84 * lit, 0.62 * lit, 0.48 * lit]

    # Headscarf (white linen, slightly creamy)
    sc_cx, sc_cy = hd_cx - 0.005, hd_cy - 0.012
    sc_w, sc_h   = 0.036, 0.026
    for py in range(max(0, int((sc_cy - sc_h) * H)), min(H, int((sc_cy + sc_h) * H))):
        for px in range(max(0, int((sc_cx - sc_w) * W)), min(W, int((sc_cx + sc_w) * W))):
            fy = (py / H - sc_cy) / sc_h
            fx = (px / W - sc_cx) / sc_w
            if fx * fx + fy * fy < 1.0:
                ref[py, px, :] = [0.94, 0.93, 0.90]

    # Shepherd's crook (pale ash-wood diagonal line)
    crook_x0 = int((fig_cx + 0.035) * W)
    crook_y0 = int((hd_cy + 0.010) * H)
    crook_x1 = int((fig_cx + 0.045) * W)
    crook_y1 = int((fig_cy + dr_h + 0.020) * H)
    steps    = max(abs(crook_x1 - crook_x0), abs(crook_y1 - crook_y0))
    if steps > 0:
        for i in range(steps + 1):
            t   = i / steps
            px  = int(crook_x0 + t * (crook_x1 - crook_x0))
            py  = int(crook_y0 + t * (crook_y1 - crook_y0))
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < W and 0 <= ny < H:
                        ref[ny, nx, :] = [0.74, 0.66, 0.50]

    # ── Sun — small white-hot disc in upper right ─────────────────────────────
    sun_cx, sun_cy = 0.86, 0.12
    sun_r          = 0.018
    for py in range(max(0, int((sun_cy - sun_r) * H)), min(H, int((sun_cy + sun_r) * H))):
        for px in range(max(0, int((sun_cx - sun_r) * W)), min(W, int((sun_cx + sun_r) * W))):
            fy = (py / H - sun_cy) / sun_r
            fx = (px / W - sun_cx) / sun_r
            dist = fx * fx + fy * fy
            if dist < 1.0:
                ref[py, px, :] = [1.00, 1.00, 0.96]
    # Subtle corona
    for py in range(max(0, int((sun_cy - sun_r * 2.5) * H)), min(H, int((sun_cy + sun_r * 2.5) * H))):
        for px in range(max(0, int((sun_cx - sun_r * 2.5) * W)), min(W, int((sun_cx + sun_r * 2.5) * W))):
            fy = (py / H - sun_cy) / (sun_r * 2.5)
            fx = (px / W - sun_cx) / (sun_r * 2.5)
            dist = fx * fx + fy * fy
            if 0.16 < dist < 1.0:
                alpha = (1.0 - dist) * 0.25
                ref[py, px, :] = np.clip(ref[py, px, :] + np.array([1.0, 0.98, 0.90]) * alpha, 0, 1)

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'Vigil at the Snowline' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=225)

    # Ground: warm primed white — Segantini's white ground for optical stroke interaction
    p.tone_ground((0.90, 0.88, 0.82), texture_strength=0.006)

    # Underpainting: establish tonal masses with large strokes
    p.underpainting(ref_pil, stroke_size=65)

    # Block in: structural colour zones
    p.block_in(ref_pil, stroke_size=28)

    # Build form: paint-plane strokes building volume
    p.build_form(ref_pil, stroke_size=12)

    # Place lights: tight strokes on the brightest snow highlights
    p.place_lights(ref_pil, stroke_size=5)

    # PRIMARY PASS: Segantini's stitch-weave Divisionism
    p.segantini_stitch_weave_pass(
        stitch_density=14.0,
        weave_strength=0.16,
        warm_target_r=0.84,
        warm_target_g=0.70,
        warm_target_b=0.32,
        cool_target_r=0.52,
        cool_target_g=0.72,
        cool_target_b=0.90,
        saturation_boost=0.12,
        opacity=0.82,
    )

    # SESSION IMPROVEMENT: Alpine luminance intensification
    p.alpine_luminance_intensification_pass(
        shadow_violet_r=0.62,
        shadow_violet_g=0.52,
        shadow_violet_b=0.88,
        shadow_thresh=0.35,
        highlight_boost=0.06,
        highlight_thresh=0.80,
        chroma_scale=1.20,
        opacity=0.70,
    )

    # Halation: sun disc bloom into surrounding sky
    p.halation_glow_pass(
        threshold=0.85,
        bloom_sigma=0.04,
        bloom_intensity=0.28,
        glow_warm_r=1.00,
        glow_warm_g=0.99,
        glow_warm_b=0.94,
        opacity=0.50,
    )

    # Light glaze: subtle cool unification — thin alpine air
    p.glaze((0.80, 0.86, 0.96), opacity=0.03)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
