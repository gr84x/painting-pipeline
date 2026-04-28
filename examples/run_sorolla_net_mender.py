"""
run_sorolla_net_mender.py
Session 226 — Joaquín Sorolla (1863–1923)
Spanish Luminism / Post-Impressionism

═══════════════════════════════════════════════════════════════════════════════
IMAGE DESCRIPTION: "The Net Mender, Valencia Noon"
═══════════════════════════════════════════════════════════════════════════════

Subject & Composition
─────────────────────
An elderly Spanish fisherman mends a large fishing net on a sun-bleached wooden
dock in Valencia, observed from a viewpoint slightly below dock level — as if
the viewer is seated in the cool shadow beneath a canvas awning, looking out
into the dazzling midday light.  This low angle places the fisherman against
the far harbour and a thin strip of cobalt sky rather than against the dock
behind him, giving him an unconscious monumentality.

He sits three-quarter left on an overturned wooden crate at the centre of the
canvas, bent forward over his work, both hands threading a long wooden needle
through the ochre-coloured mesh that fans out across his lap and the dock
planks around him.  His posture is completely absorbed, slightly stooped from
decades of this posture, shoulders broad and settled.

The Figure
──────────
The fisherman is perhaps sixty-eight.  He wears a loose white linen shirt
thrown fully open at the collar, the fabric brilliant white in direct noon
sun — bleached past colour, almost pure luminous white at the shoulder where
the sun hits full and warm peach-gold at the turning edges.  His dark canvas
trousers are worn smooth at the knees; rope sandals lie just visible below
the net.  His face is remarkable: deeply tanned and leathered to the colour
of dark sienna, forehead and nose creased from years of squinting, eyes
nearly closed against the glare yet clearly reading every inch of mesh by
touch alone.  His hands are extraordinary — large, dark-knuckled, utterly
certain — moving through the net with the ease of reflex.

His emotional state is concentrated absorption: not effort, not labour in
any pained sense, but the steady satisfaction of a person doing something
their body knows completely, sustained by decades of practice into something
close to meditation.

The Environment
───────────────
The dock planks in the mid-ground are bleached almost white by decades of
salt and sun, cut diagonally by crisp cast shadows from rigging ropes and
mooring posts above.  Where fish have recently been laid and water has
splashed, the planks are darker and wet, creating irregular patches of
warm umber against the sun-bleached pale.  Three or four small orange-red
clay fishing floats sit in the lower-right corner catching the light, their
glaze reflecting tiny bright specular flashes.

Beyond the fisherman, the harbour opens: two dark wooden Valencian fishing
boats (laúdes) are moored in the mid-distance, their furled ochre sails tied
to short masts, their dark hulls partially reflected in the harbour water.
The near water between the dock edge and the boats is shallow-water cyan —
transparent enough to see hints of the pale sand bottom — and its disturbed
surface carries dozens of stochastic specular scatter points, small bright
flashes where the midday sun bounces off individual wave facets.  The deep
water beyond the boats is architectural Mediterranean azure, intense and
structural rather than atmospheric.

The sky is visible only as a narrow strip at the top of the canvas — cobalt,
cloudless, almost enamel in its depth — because the low viewpoint pushes the
horizon high and the harbour fills most of the upper register.

In the immediate foreground: the cool blue-violet shadow under the awning,
the bottom edge of the dock planks in shadow (warm umber with violet-blue
cool reflection), and the near edge of the net spilling off the dock in a
pale ochre tangle.

Technique & Palette
────────────────────
Technique: Joaquín Sorolla's plein-air Mediterranean luminism.  Broad, wet,
decisive strokes loaded with paint — a single stroke describes form, light,
and material simultaneously.  The white linen shirt is built from three or
four strokes: one for the full lit plane (near-white), one for the warm
turning edge (peach-gold), one for the shadow side (cool azure-grey), with
wet blending at all transitions.  The dock planks are horizontal strokes
laid quickly left to right, colour varying stroke to stroke to describe
texture without rendering each grain.  The water is rapid diagonal strokes
in two or three values with scattered bright whites for the specular scatter.

Palette:
  • Sun-bleached dock:    (0.96, 0.95, 0.92) — dock planks and linen near-white
  • Mediterranean azure:  (0.28, 0.58, 0.86) — sky, deep harbour, shirt shadow
  • Ochre net/sail:       (0.86, 0.62, 0.22) — fish net, furled ochre laúd sails
  • Warm sienna flesh:    (0.72, 0.44, 0.26) — fisherman's neck, hands, dark face
  • Deep plank umber:     (0.40, 0.32, 0.22) — wet dark dock planks and shadow
  • Warm peach highlight: (0.96, 0.88, 0.68) — shirt turning edges, sunlit flesh
  • Shallow-water cyan:   (0.62, 0.82, 0.92) — near harbour transparent shallows
  • Cast shadow mauve:    (0.42, 0.40, 0.60) — dock cast shadows in midday blue
  • Clay float red:       (0.74, 0.38, 0.22) — fishing floats in lower right

Mood & Intent
─────────────
The painting attempts to capture what Sorolla called the "dazzle" of the
Mediterranean at full noon — not a romantic or picturesque light, but the
raw sensory fact of it: how it bleaches colour to near-white on all
illuminated surfaces, how it turns shadows into transparent pools of
reflected sky-blue, how it makes the ordinary labour of an old man
repairing a net look as radiant as a saint in a church painting.

The viewer should feel the specific heat-weight of noon, the smell of salt
and tar and old wood, the rhythmic peace of the fisherman's work — and
underneath all that, the particular joy Sorolla felt when he looked directly
at the Mediterranean sun and decided to paint it exactly as it was, without
apology or softening.

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
OUTPUT = os.path.join(os.path.dirname(__file__), "sorolla_net_mender.png")


def build_reference() -> np.ndarray:
    """Construct a synthetic reference for The Net Mender, Valencia Noon."""
    rng = np.random.RandomState(226)
    ref = np.zeros((H, W, 3), dtype=np.float32)

    xs = np.linspace(0, 1, W)[None, :]
    ys = np.linspace(0, 1, H)[:, None]

    # ── Sky — thin cobalt strip at top (low viewpoint, horizon high) ────────
    sky_mask = np.clip(1.0 - ys / 0.12, 0, 1)
    sky_col  = np.array([0.28, 0.58, 0.86])
    for ch in range(3):
        ref[:, :, ch] = sky_col[ch] * sky_mask

    # ── Harbour water — deep azure fading to shallow cyan near dock ──────────
    water_top  = 0.12
    water_bot  = 0.52
    water_mask = np.clip((ys - water_top) / (water_bot - water_top), 0, 1) * \
                 np.clip(1.0 - (ys - water_top) / (water_bot - water_top), 0, 1) * 4
    water_mask = np.clip((ys - water_top) / max(water_bot - water_top, 1e-6), 0, 1)
    water_mask = np.clip(water_mask * np.clip(1.0 - (ys - water_bot) / 0.10, 0, 1), 0, 1)
    # Deep azure in middle, shallow cyan near bottom of water zone
    deep_col  = np.array([0.28, 0.58, 0.86])
    cyan_col  = np.array([0.62, 0.82, 0.92])
    near_frac = np.clip((ys - 0.35) / 0.15, 0, 1)
    for ch in range(3):
        water_ch = deep_col[ch] * (1 - near_frac) + cyan_col[ch] * near_frac
        ref[:, :, ch] = ref[:, :, ch] * (1 - water_mask) + water_ch * water_mask

    # ── Stochastic specular scatter on water surface ─────────────────────────
    scatter_row_mask = np.clip((ys - 0.14) / 0.06, 0, 1) * np.clip(1.0 - (ys - 0.40) / 0.10, 0, 1)
    scatter_row_mask = np.broadcast_to(scatter_row_mask, (H, W)).copy()
    flash = (rng.random_sample((H, W)).astype(np.float32) < 0.025) * scatter_row_mask
    flash_brightness = rng.uniform(0.5, 1.0, (H, W)).astype(np.float32)
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + flash * flash_brightness * 0.70, 0, 1)

    # ── Two fishing boats (laúdes) in mid-distance ───────────────────────────
    boat_specs = [
        (0.22, 0.28, 0.12, 0.38),   # (x_centre, x_half_width, y_top, y_bot)
        (0.68, 0.10, 0.16, 0.38),
    ]
    hull_col = np.array([0.20, 0.20, 0.18])
    for bcx, bhw, byt, byb in boat_specs:
        for py in range(int(byt * H), int(byb * H)):
            y_frac   = (py / H - byt) / (byb - byt)
            half_w   = bhw * (0.30 + 0.70 * y_frac) * W
            cx       = int(bcx * W)
            x0       = max(0, int(cx - half_w))
            x1       = min(W - 1, int(cx + half_w))
            if x0 < x1:
                ref[py, x0:x1, :] = hull_col
        # Mast — thin vertical line
        mast_x = int(bcx * W)
        mast_y0 = max(0, int((byt - 0.10) * H))
        mast_y1 = int(byt * H)
        mast_col = np.array([0.30, 0.24, 0.16])
        ref[mast_y0:mast_y1, max(0, mast_x - 1):mast_x + 2, :] = mast_col
        # Furled ochre sail
        sail_col = np.array([0.86, 0.62, 0.22])
        sail_y0  = mast_y0 + 4
        sail_y1  = sail_y0 + int(0.06 * H)
        ref[sail_y0:sail_y1, max(0, mast_x - 3):mast_x + 4, :] = sail_col

    # ── Dock planks — sun-bleached pale, horizontal bands ───────────────────
    dock_top = 0.50
    dock_col_sun   = np.array([0.94, 0.93, 0.88])
    dock_col_wet   = np.array([0.40, 0.32, 0.22])
    for py in range(int(dock_top * H), H):
        y_frac = (py / H - dock_top) / (1.0 - dock_top)
        # Alternating plank bands
        plank_idx = int(py / max(int(0.018 * H), 1))
        plank_bright = dock_col_sun * (0.92 + 0.08 * (plank_idx % 2))
        for ch in range(3):
            ref[py, :, ch] = plank_bright[ch]

    # ── Wet dark patches on dock ─────────────────────────────────────────────
    wet_positions = [(0.12, 0.60, 0.10, 0.06), (0.80, 0.70, 0.08, 0.04),
                     (0.45, 0.82, 0.06, 0.03)]
    for wcx, wcy, ww, wh in wet_positions:
        for py in range(max(0, int((wcy - wh) * H)), min(H, int((wcy + wh) * H))):
            for px in range(max(0, int((wcx - ww) * W)), min(W, int((wcx + ww) * W))):
                fy = (py / H - wcy) / wh
                fx = (px / W - wcx) / ww
                if fx * fx + fy * fy < 1.0:
                    ref[py, px, :] = dock_col_wet

    # ── Cast shadows on dock (diagonal strips from rigging) ─────────────────
    shad_col = np.array([0.42, 0.40, 0.60])
    for rope_x in [0.10, 0.35, 0.72, 0.88]:
        for py in range(int(dock_top * H), H):
            y_off = py - int(dock_top * H)
            px_c  = int((rope_x + y_off * 0.005) * W)
            for dx in range(-3, 4):
                px2 = px_c + dx
                if 0 <= px2 < W:
                    alpha = 0.35 * max(0, 1 - abs(dx) / 3)
                    ref[py, px2, :] = ref[py, px2, :] * (1 - alpha) + shad_col * alpha

    # ── Foreground awning shadow (bottom quarter, left side) ────────────────
    awn_mask = np.clip((0.82 - ys) / 0.08, 0, 1) * np.clip(1.0 - xs / 0.25, 0, 1)
    awn_col  = np.array([0.35, 0.32, 0.52])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - awn_mask * 0.70) + awn_col[ch] * awn_mask * 0.70

    # ── Clay fishing floats — lower right ────────────────────────────────────
    float_col = np.array([0.74, 0.38, 0.22])
    for fcx, fcy, fr in [(0.82, 0.88, 0.022), (0.90, 0.85, 0.018),
                          (0.86, 0.91, 0.016), (0.78, 0.93, 0.020)]:
        for py in range(max(0, int((fcy - fr) * H)), min(H, int((fcy + fr) * H))):
            for px in range(max(0, int((fcx - fr) * W)), min(W, int((fcx + fr) * W))):
                fy = (py / H - fcy) / fr
                fx = (px / W - fcx) / fr
                dist = fx * fx + fy * fy
                if dist < 1.0:
                    lit = 0.85 + 0.15 * (1.0 - fx)
                    ref[py, px, :] = np.clip(float_col * lit, 0, 1)
                    # Specular highlight
                    if dist < 0.09 and fx < -0.1 and fy < -0.1:
                        ref[py, px, :] = [0.96, 0.94, 0.88]

    # ── The net — ochre mesh spreading across dock ───────────────────────────
    net_col_light = np.array([0.90, 0.72, 0.38])
    net_col_shad  = np.array([0.62, 0.48, 0.22])
    # Mesh grid pattern across the dock lap area
    net_cx, net_cy = 0.46, 0.72
    for py in range(max(0, int(0.58 * H)), min(H, int(0.90 * H))):
        y_frac = (py / H - net_cy)
        for px in range(max(0, int(0.15 * W)), min(W, int(0.80 * W))):
            x_frac = (px / W - net_cx)
            dist = (x_frac * x_frac + y_frac * y_frac) ** 0.5
            if dist > 0.30:
                continue
            # Mesh pattern: horizontal and vertical grid lines
            in_h = (py % max(int(0.012 * H), 1)) < 2
            in_v = (px % max(int(0.012 * H), 1)) < 2
            if in_h or in_v:
                alpha = np.clip(0.80 - dist * 1.8, 0, 1)
                lit = net_col_light if x_frac < 0 else net_col_shad
                ref[py, px, :] = ref[py, px, :] * (1 - alpha) + lit * alpha

    # ── Fisherman figure ─────────────────────────────────────────────────────
    fig_cx  = 0.46   # centre x
    fig_cy  = 0.58   # body centre y

    # Dark canvas trousers
    tr_w, tr_h = 0.065, 0.15
    for py in range(max(0, int((fig_cy - tr_h * 0.2) * H)),
                    min(H, int((fig_cy + tr_h) * H))):
        for px in range(max(0, int((fig_cx - tr_w) * W)),
                        min(W, int((fig_cx + tr_w) * W))):
            fy = (py / H - fig_cy) / tr_h
            fx = (px / W - fig_cx) / (tr_w * (0.5 + 0.5 * abs(fy)))
            if fx * fx + fy * fy < 1.0:
                ref[py, px, :] = [0.22, 0.20, 0.18]

    # White linen shirt — torso
    sh_cx, sh_cy = fig_cx + 0.005, fig_cy - 0.10
    sh_w,  sh_h  = 0.070, 0.12
    for py in range(max(0, int((sh_cy - sh_h) * H)),
                    min(H, int((sh_cy + sh_h) * H))):
        for px in range(max(0, int((sh_cx - sh_w) * W)),
                        min(W, int((sh_cx + sh_w) * W))):
            fy = (py / H - sh_cy) / sh_h
            fx = (px / W - sh_cx) / (sh_w * (0.6 + 0.4 * abs(fy)))
            if fx * fx + fy * fy < 1.0:
                # Bleached white on left (sun side), warm cream in centre, azure shadow right
                if fx < -0.3:
                    ref[py, px, :] = [0.97, 0.96, 0.94]   # near-white sun
                elif fx < 0.2:
                    ref[py, px, :] = [0.94, 0.88, 0.72]   # warm peach-gold turning edge
                else:
                    ref[py, px, :] = [0.60, 0.68, 0.82]   # azure shadow side

    # Bent shoulders / back — darker fabric
    back_cx, back_cy = fig_cx - 0.005, sh_cy - 0.06
    back_w, back_h   = 0.080, 0.065
    for py in range(max(0, int((back_cy - back_h) * H)),
                    min(H, int((back_cy + back_h) * H))):
        for px in range(max(0, int((back_cx - back_w) * W)),
                        min(W, int((back_cx + back_w) * W))):
            fy = (py / H - back_cy) / back_h
            fx = (px / W - back_cx) / (back_w * (0.7 + 0.3 * abs(fy)))
            if fx * fx + fy * fy < 1.0:
                lit = 0.92 + 0.08 * (-fx)
                ref[py, px, :] = [0.92 * lit, 0.90 * lit, 0.84 * lit]

    # Head — dark sienna, deeply tanned, facing left-and-down
    hd_cx, hd_cy = fig_cx + 0.005, sh_cy - sh_h - 0.02
    hd_rw, hd_rh = 0.038, 0.044
    for py in range(max(0, int((hd_cy - hd_rh) * H)),
                    min(H, int((hd_cy + hd_rh) * H))):
        for px in range(max(0, int((hd_cx - hd_rw) * W)),
                        min(W, int((hd_cx + hd_rw) * W))):
            fy = (py / H - hd_cy) / hd_rh
            fx = (px / W - hd_cx) / hd_rw
            if fx * fx + fy * fy < 1.0:
                # Dark sienna skin, slightly lighter toward sun side
                lit = 0.90 + 0.10 * (-fx)
                ref[py, px, :] = [0.56 * lit, 0.36 * lit, 0.20 * lit]

    # Hat (worn canvas sun hat, pale warm grey)
    hat_cx, hat_cy = hd_cx - 0.004, hd_cy - 0.034
    hat_w, hat_h   = 0.055, 0.024
    for py in range(max(0, int((hat_cy - hat_h) * H)),
                    min(H, int((hat_cy + hat_h) * H))):
        for px in range(max(0, int((hat_cx - hat_w) * W)),
                        min(W, int((hat_cx + hat_w) * W))):
            fy = (py / H - hat_cy) / hat_h
            fx = (px / W - hat_cx) / hat_w
            if fx * fx + fy * fy < 1.2:
                brim = 0.88 + 0.08 * (-fx)
                ref[py, px, :] = [0.82 * brim, 0.78 * brim, 0.68 * brim]

    # Hands — large, dark, positioned over the net
    hand_positions = [(fig_cx - 0.040, fig_cy + 0.06), (fig_cx + 0.025, fig_cy + 0.08)]
    for hx, hy in hand_positions:
        hw, hh2 = 0.028, 0.018
        for py in range(max(0, int((hy - hh2) * H)), min(H, int((hy + hh2) * H))):
            for px in range(max(0, int((hx - hw) * W)), min(W, int((hx + hw) * W))):
                fy = (py / H - hy) / hh2
                fx = (px / W - hx) / hw
                if fx * fx + fy * fy < 1.0:
                    lit = 0.85 + 0.15 * (-fx)
                    ref[py, px, :] = [0.52 * lit, 0.32 * lit, 0.18 * lit]

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'The Net Mender, Valencia Noon' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=226)

    # Ground: warm Valencian off-white — Sorolla's high-key priming
    p.tone_ground((0.92, 0.90, 0.86), texture_strength=0.005)

    # Underpainting: establish tonal massing with large broad strokes
    p.underpainting(ref_pil, stroke_size=72)

    # Block in: structural colour zones — dock, water, figure
    p.block_in(ref_pil, stroke_size=30)

    # Build form: the decisive broad strokes of Sorolla's wet-loaded brush
    p.build_form(ref_pil, stroke_size=14)

    # Place lights: brilliant whites on linen shirt, foam, float highlights
    p.place_lights(ref_pil, stroke_size=5)

    # SESSION IMPROVEMENT: Diffuse boundary — wet-into-wet bleed at colour edges
    p.diffuse_boundary_pass(
        low_grad=0.03,
        high_grad=0.20,
        sigma=1.4,
        strength=0.50,
        opacity=0.60,
    )

    # PRIMARY PASS: Sorolla Mediterranean Light
    p.sorolla_mediterranean_light_pass(
        bleach_thresh=0.80,
        bleach_strength=0.60,
        azure_shadow_r=0.28,
        azure_shadow_g=0.58,
        azure_shadow_b=0.86,
        shadow_thresh=0.40,
        scatter_density=0.005,
        scatter_brightness=0.60,
        warm_boost=0.10,
        opacity=0.84,
        seed=226,
    )

    # Light cool glaze — thin Mediterranean air, slight azure unification
    p.glaze((0.78, 0.88, 0.98), opacity=0.025)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
