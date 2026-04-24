"""
paint_mona_lisa_s161.py — Mona Lisa portrait for session 161.

Subject: enigmatic half-length female figure, three-quarter pose, sfumato
technique, dreamlike geological landscape background, dark veil, forest-green
dress, folded hands.

Artistic discovery (session 161): Joshua Reynolds (1723–1792)
  - British Grand Manner portraitist, founder of the Royal Academy
  - Invented the "mezzotint tone" — a unifying warm amber glaze across all elements
  - Bold lead-white impasto in lights; bitumen/umber glazing in shadows

New pipeline enhancement:
  - reynolds_grand_manner_pass: mezzotint amber unification — FORTY-SEVENTH DISTINCT MODE
    Flat non-gated amber glaze (uniform across all luminance) pulls the entire
    composition into a single warm, honey-amber key in the tradition of Reynolds'
    Grand Manner tonal unity.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter
from art_catalog import get_style

W, H = 530, 770


def build_reference(w: int, h: int) -> Image.Image:
    """Synthetic compositional reference — Mona Lisa layout."""
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None] * np.ones((1, w), dtype=np.float32)
    xx = np.ones((h, 1), dtype=np.float32) * np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]

    def _blend(base, colour, alpha):
        a = alpha[:, :, None]
        return base * (1.0 - a) + colour[None, None, :] * a

    # ── Background: atmospheric landscape with sfumato recession ─────────────
    sky   = np.array([0.64, 0.66, 0.68], dtype=np.float32)
    rocks = np.array([0.46, 0.51, 0.50], dtype=np.float32)
    earth = np.array([0.30, 0.36, 0.32], dtype=np.float32)

    t_sky   = np.clip(1.0 - yy * 4.5, 0.0, 1.0)
    t_earth = np.clip((yy - 0.68) * 5.0, 0.0, 1.0)
    t_mid   = np.clip(1.0 - t_sky - t_earth, 0.0, 1.0)

    arr = (sky[None, None, :]   * t_sky[:, :, None]
         + rocks[None, None, :] * t_mid[:, :, None]
         + earth[None, None, :] * t_earth[:, :, None])

    # Horizon mismatch — left sits slightly higher than right
    left_lift = np.clip(0.55 - xx, 0.0, 0.55) * 0.12
    arr += left_lift[:, :, None] * np.array([0.02, 0.06, 0.14], dtype=np.float32)

    # Winding path on the left
    path_x = 0.25 + (yy - 0.30) * 0.18
    path_dist = np.abs(xx - path_x) / 0.04
    path_mask = (np.clip(1.0 - path_dist, 0.0, 1.0)
                 * np.clip((yy - 0.25) / 0.40, 0.0, 1.0))
    arr += path_mask[:, :, None] * np.array([0.06, 0.07, 0.05], dtype=np.float32)

    # Rocky outcrops — darker masses mid-background
    for rx, ry, rsx, rsy in [(0.15, 0.42, 0.08, 0.06),
                               (0.80, 0.45, 0.07, 0.05),
                               (0.65, 0.38, 0.06, 0.04)]:
        rd = ((xx - rx) / rsx)**2 + ((yy - ry) / rsy)**2
        rmask = np.clip(1.2 - rd, 0.0, 1.0) ** 1.5 * 0.35
        arr = _blend(arr, np.array([0.28, 0.30, 0.27], dtype=np.float32), rmask)

    # Water suggestion — middle distance right of centre
    water_d = ((xx - 0.70) / 0.20)**2 + ((yy - 0.48) / 0.03)**2
    water_mask = np.clip(1.0 - water_d, 0.0, 1.0)**2 * 0.30
    arr += water_mask[:, :, None] * np.array([0.18, 0.22, 0.30], dtype=np.float32)

    arr = np.clip(arr, 0.0, 1.0)

    # ── Figure: torso / lap ───────────────────────────────────────────────────
    fig_cx, fig_cy = 0.508, 0.625
    fig_rx, fig_ry = 0.29, 0.43
    fx = (xx - fig_cx) / fig_rx
    fy = (yy - fig_cy) / fig_ry
    fig_d = fx**2 + fy**2

    flesh = np.array([0.76, 0.62, 0.47], dtype=np.float32)
    fig_alpha = np.clip(1.55 - fig_d, 0.0, 1.0) ** 0.58
    arr = _blend(arr, flesh, fig_alpha)

    # Dark forest-green dress — lower torso and lap
    dress = np.array([0.12, 0.18, 0.14], dtype=np.float32)
    d_alpha = np.clip(1.2 - fig_d, 0.0, 1.0) * (yy > 0.57).astype(np.float32) * 0.75
    arr = _blend(arr, dress, d_alpha)

    # Semi-transparent gauze wrap
    gauze = np.array([0.36, 0.40, 0.38], dtype=np.float32)
    g_alpha = (np.clip(0.88 - fig_d, 0.0, 1.0)
               * ((yy > 0.50) & (yy < 0.65) & (fig_d < 0.88)).astype(np.float32) * 0.28)
    arr = _blend(arr, gauze, g_alpha)

    # Thin amber-gold neckline trim
    neck_d = ((xx - fig_cx) / 0.14)**2 + ((yy - 0.48) / 0.022)**2
    neck_mask = np.clip(1.0 - neck_d, 0.0, 1.0) ** 2 * 0.60 * (yy > 0.46).astype(np.float32)
    arr = _blend(arr, np.array([0.82, 0.66, 0.22], dtype=np.float32), neck_mask)

    # ── Head: slightly left of torso centre, upper third ─────────────────────
    head_cx, head_cy = 0.490, 0.262
    head_rx, head_ry = 0.124, 0.156
    hx = (xx - head_cx) / head_rx
    hy = (yy - head_cy) / head_ry
    head_d = hx**2 + hy**2

    face = np.array([0.84, 0.72, 0.55], dtype=np.float32)
    head_alpha = np.clip(1.45 - head_d, 0.0, 1.0) ** 0.50
    arr = _blend(arr, face, head_alpha)

    # Upper-left light source
    lit_d = (hx + 0.28)**2 + (hy + 0.18)**2
    lit_alpha = np.clip(1.0 - lit_d, 0.0, 1.0) ** 1.8 * 0.52 * head_alpha
    arr = _blend(arr, np.array([0.92, 0.83, 0.68], dtype=np.float32), lit_alpha)

    # Shadow on right side
    shad_d = (-hx + 0.28)**2 + (hy - 0.08)**2
    shad_alpha = np.clip(1.0 - shad_d, 0.0, 1.0) ** 2.2 * 0.44 * head_alpha
    arr = _blend(arr, np.array([0.50, 0.38, 0.26], dtype=np.float32), shad_alpha)

    # Smooth high forehead — hairline recedes softly at temples
    brow_d = ((xx - head_cx) / (head_rx * 1.10))**2 + ((yy - (head_cy - head_ry * 0.72)) / 0.02)**2
    brow_mask = np.clip(1.0 - brow_d, 0.0, 1.0) ** 2 * 0.22
    arr = _blend(arr, np.array([0.86, 0.76, 0.60], dtype=np.float32), brow_mask)

    # ── Hair: dark warm brown, centre-parted, soft waves ─────────────────────
    hair_d = (((xx - head_cx) / (head_rx * 1.54))**2
              + ((yy - head_cy) / (head_ry * 1.40))**2)
    face_zone = (np.abs(hx) < 0.50) & (hy > -0.60) & (hy < 0.72)
    hair_mask = (hair_d < 1.0) & ~face_zone & (hy < 0.55)
    h_alpha = np.where(hair_mask, np.clip(1.0 - hair_d, 0.0, 1.0) * 0.90, 0.0)
    arr = _blend(arr, np.array([0.18, 0.13, 0.08], dtype=np.float32), h_alpha)

    # Dark translucent veil over crown
    veil_zone = (hair_d < 0.68) & (hy < -0.10) & (yy < 0.27)
    v_alpha = np.clip(0.68 - hair_d, 0.0, 1.0) * 0.58 * veil_zone.astype(np.float32)
    arr = _blend(arr, np.array([0.10, 0.08, 0.07], dtype=np.float32), v_alpha)

    # ── Hands: folded in lap, right over left ────────────────────────────────
    hndx = (xx - 0.505) / 0.175
    hndy = (yy - 0.848) / 0.082
    hands_d = hndx**2 + hndy**2
    hand_alpha = np.clip(1.25 - hands_d, 0.0, 1.0) ** 0.70 * 0.80
    arr = _blend(arr, np.array([0.74, 0.60, 0.44], dtype=np.float32), hand_alpha)

    # Right hand slightly lighter (draped over left, catches more light)
    rh_d = ((xx - 0.52) / 0.09)**2 + ((yy - 0.838) / 0.04)**2
    rh_alpha = np.clip(1.0 - rh_d, 0.0, 1.0) ** 1.5 * 0.30
    arr = _blend(arr, np.array([0.82, 0.70, 0.55], dtype=np.float32), rh_alpha)

    arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    ref = Image.fromarray(arr, "RGB")
    ref = ref.filter(ImageFilter.GaussianBlur(5))
    return ref


def paint(output_path: str = "mona_lisa_s161.png") -> str:
    """Full Leonardo sfumato pipeline with session 161 Reynolds mezzotint pass."""
    print("=" * 64)
    print("  Session 161 — Mona Lisa sfumato portrait")
    print("  Artistic discovery: Joshua Reynolds — Grand Manner mezzotint tone")
    print("=" * 64)

    ref = build_reference(W, H)
    ref.save("mona_lisa_s161_reference.png")
    print(f"  Reference saved -> mona_lisa_s161_reference.png  ({W}×{H})")

    leo = get_style("leonardo")
    p = Painter(W, H)

    print("  [1/14] Tone ground ...")
    p.tone_ground(leo.ground_color, texture_strength=0.06)

    print("  [2/14] Underpainting ...")
    p.underpainting(ref, stroke_size=50, n_strokes=160)

    print("  [3/14] Block-in ...")
    p.block_in(ref, stroke_size=32, n_strokes=340)

    print("  [4/14] Build form ...")
    p.build_form(ref, stroke_size=10, n_strokes=1400)

    print("  [5/14] Sfumato veil pass ...")
    p.sfumato_veil_pass(
        ref,
        n_veils       = 10,
        blur_radius   = 14.0,
        warmth        = 0.38,
        veil_opacity  = 0.07,
        edge_only     = True,
        chroma_dampen = 0.22,
    )

    print("  [6/14] Edge sfumato dissolution pass (session 159) ...")
    p.edge_sfumato_dissolution_pass(
        grad_threshold = 0.10,
        blur_sigma     = 6.0,
        edge_strength  = 0.38,
        opacity        = 0.30,
    )

    print("  [7/14] Skin subsurface scatter pass (session 159) ...")
    p.skin_subsurface_scatter_pass(
        scatter_sigma    = 5.0,
        scatter_strength = 0.22,
        warm_boost       = 1.04,
        cool_damp        = 0.97,
        opacity          = 0.28,
    )

    print("  [8/14] Tonal envelope pass ...")
    p.tonal_envelope_pass(
        center_x      = 0.490,
        center_y      = 0.31,
        radius        = 0.48,
        lift_strength = 0.09,
        lift_warmth   = 0.35,
        edge_darken   = 0.07,
        gamma         = 1.9,
    )

    print("  [9/14] Selective focus pass ...")
    p.selective_focus_pass(
        center_x        = 0.490,
        center_y        = 0.28,
        focus_radius    = 0.34,
        max_blur_radius = 2.8,
        desaturation    = 0.10,
        gamma           = 2.2,
    )

    print("  [10/14] Moro regal presence pass (subtle — tonal polish) ...")
    p.moro_regal_presence_pass(
        shadow_hi       = 0.28,
        shadow_deepen   = 0.18,
        shadow_power    = 1.5,
        highlight_lo    = 0.72,
        silver_b        = 0.08,
        silver_r        = 0.04,
        highlight_power = 1.8,
        opacity         = 0.18,
    )

    print("  [11/14] Reynolds Grand Manner mezzotint tone pass (session 161) ...")
    p.reynolds_grand_manner_pass(
        amber_strength  = 0.06,   # gentle flat amber glaze — the mezzotint tone
        amber_r         = 0.08,
        amber_g         = 0.04,
        amber_b_reduce  = 0.06,
        highlight_lo    = 0.70,
        highlight_power = 1.5,
        hi_boost        = 0.04,   # subtle impasto brightening at peaks
        shadow_hi       = 0.30,
        shadow_power    = 1.5,
        shadow_deepen_r = 0.12,   # warm umber shadow deepening
        shadow_deepen_g = 0.10,
        shadow_deepen_b = 0.08,
        opacity         = 0.32,
    )

    print("  [12/14] Place lights ...")
    p.place_lights(ref, stroke_size=5, n_strokes=320)

    print("  [13/14] Final glaze ...")
    p.glaze((0.72, 0.52, 0.22), opacity=0.06)

    print("  [14/14] Finish ...")
    p.finish(vignette=0.28, crackle=True)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Painting saved -> {output_path}  ({W}×{H})")
    print("=" * 64)
    return output_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "mona_lisa_s161.png"
    paint(out)
