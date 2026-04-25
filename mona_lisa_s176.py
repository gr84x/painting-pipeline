"""
mona_lisa_s176.py — Session 176 Mona Lisa render.

Inspired by Marco d'Oggiono, Leonardo's Milanese pupil, this session enhances
the Leonardesque pipeline with two new passes:

  - doggiono_leonardesque_warmth_pass (pass 73): THREE-GATE tinting — warm ivory
    highlights, cool violet shadow depth, sfumato edge dissolution.  Encodes
    Marco's inherited Leonardo-school warmth: peaks glow amber-ivory rather than
    cool-pearl, shadows retain gentle violet depth without hard contrast.

  - multilayer_atmospheric_veil_pass (pass 74, random improvement): THREE-SCALE
    sfumato applied simultaneously at fine (σ=1.5), medium (σ=4.5), and coarse
    (σ=12.0) spatial frequencies, all gated on Sobel edge magnitude.  Creates
    the layered atmospheric dissolution that characterises Leonardo's glazing
    technique — edges dissolve at multiple depths simultaneously.

Pipeline:
  tone_ground -> underpainting -> block_in -> build_form
  -> sfumato_veil_pass -> doggiono_leonardesque_warmth_pass (s176 new)
  -> multilayer_atmospheric_veil_pass (s176 new)
  -> skin_subsurface_scatter_pass -> figure_contour_atmosphere_pass
  -> tonal_envelope_pass -> selective_focus_pass
  -> place_lights -> glaze -> finish
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
    """Synthetic Mona Lisa reference: landscape background + figure + face."""
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None] * np.ones((1, w), dtype=np.float32)
    xx = np.ones((h, 1), dtype=np.float32) * np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]

    def _blend(base, colour, alpha):
        a = alpha[:, :, None]
        return base * (1.0 - a) + colour[None, None, :] * a

    # ── Background landscape with aerial perspective ──────────────────────────
    sky   = np.array([0.66, 0.68, 0.70], dtype=np.float32)
    rocks = np.array([0.48, 0.53, 0.52], dtype=np.float32)
    earth = np.array([0.32, 0.38, 0.34], dtype=np.float32)

    t_sky   = np.clip(1.0 - yy * 4.5,        0.0, 1.0)
    t_earth = np.clip((yy - 0.68) * 5.0,     0.0, 1.0)
    t_mid   = np.clip(1.0 - t_sky - t_earth, 0.0, 1.0)

    arr = (sky[None, None, :]   * t_sky[:, :, None]
         + rocks[None, None, :] * t_mid[:, :, None]
         + earth[None, None, :] * t_earth[:, :, None])

    # Left side cool atmospheric tint (sfumato background)
    left_tint = np.clip(0.55 - xx, 0.0, 0.55) * 0.10
    arr += left_tint[:, :, None] * np.array([0.02, 0.06, 0.12], dtype=np.float32)

    # Winding path on left side
    path_x_centre = 0.25 + (yy - 0.30) * 0.18
    path_dist = np.abs(xx - path_x_centre) / 0.04
    path_mask = (np.clip(1.0 - path_dist, 0.0, 1.0)
                 * np.clip((yy - 0.25) / 0.40, 0.0, 1.0))
    arr += path_mask[:, :, None] * np.array([0.05, 0.06, 0.04], dtype=np.float32)

    # Water/river in middle distance (right side)
    water_d = (((xx - 0.70) / 0.20)**2 + ((yy - 0.48) / 0.04)**2)
    water_mask = np.clip(1.0 - water_d, 0.0, 1.0) ** 2 * 0.35
    arr += water_mask[:, :, None] * np.array([0.18, 0.22, 0.28], dtype=np.float32)

    # Left horizon sits slightly higher than right — subtle uncanny mismatch
    horizon_mismatch = np.where(xx < 0.5,
                                np.clip((0.22 - yy) / 0.04, 0.0, 1.0),
                                np.clip((0.26 - yy) / 0.04, 0.0, 1.0))
    arr = _blend(arr, np.array([0.62, 0.65, 0.68], dtype=np.float32),
                 horizon_mismatch.astype(np.float32) * 0.55)

    arr = np.clip(arr, 0.0, 1.0)

    # ── Figure: half-length portrait, slightly right of centre ───────────────
    fig_cx, fig_cy = 0.505, 0.62
    fig_rx, fig_ry = 0.30, 0.44
    fx = (xx - fig_cx) / fig_rx
    fy = (yy - fig_cy) / fig_ry
    fig_d = fx**2 + fy**2

    flesh = np.array([0.76, 0.62, 0.47], dtype=np.float32)
    fig_alpha = np.clip(1.55 - fig_d, 0.0, 1.0) ** 0.60
    arr = _blend(arr, flesh, fig_alpha)

    # Dark forest-green / blue-black dress
    dress = np.array([0.14, 0.20, 0.17], dtype=np.float32)
    d_alpha = np.clip(1.2 - fig_d, 0.0, 1.0) * (yy > 0.58) * 0.72
    arr = _blend(arr, dress, d_alpha)

    # Semi-transparent gauze wrap over chest
    gauze = np.array([0.38, 0.42, 0.40], dtype=np.float32)
    g_alpha = (np.clip(0.90 - fig_d, 0.0, 1.0)
               * ((yy > 0.50) & (yy < 0.66) & (fig_d < 0.90)) * 0.30)
    arr = _blend(arr, gauze, g_alpha)

    # Golden neckline trim
    trim = np.array([0.68, 0.55, 0.22], dtype=np.float32)
    trim_zone = (yy > 0.53) & (yy < 0.57) & (fig_d < 0.35)
    t_alpha = np.clip(0.35 - fig_d, 0.0, 1.0) * trim_zone * 0.55
    arr = _blend(arr, trim, t_alpha)

    # ── Head and face ─────────────────────────────────────────────────────────
    head_cx, head_cy = 0.488, 0.265
    head_rx, head_ry = 0.125, 0.158
    hx = (xx - head_cx) / head_rx
    hy = (yy - head_cy) / head_ry
    head_d = hx**2 + hy**2

    face = np.array([0.84, 0.72, 0.56], dtype=np.float32)
    head_alpha = np.clip(1.45 - head_d, 0.0, 1.0) ** 0.52
    arr = _blend(arr, face, head_alpha)

    # Upper-left light source: warm illumination on lit side
    lit_d = (hx + 0.30)**2 + (hy + 0.15)**2
    lit_alpha = np.clip(1.0 - lit_d, 0.0, 1.0) ** 1.8 * 0.55 * head_alpha
    arr = _blend(arr, np.array([0.91, 0.82, 0.68], dtype=np.float32), lit_alpha)

    # Shadow side — warm ochre shadow (not cool)
    shad_d = (-hx + 0.25)**2 + (hy - 0.10)**2
    shad_alpha = np.clip(1.0 - shad_d, 0.0, 1.0) ** 2.2 * 0.45 * head_alpha
    arr = _blend(arr, np.array([0.52, 0.40, 0.28], dtype=np.float32), shad_alpha)

    # ── Hair: dark brown, parted at centre, partially covered by veil ────────
    hair_d = (((xx - head_cx) / (head_rx * 1.55))**2
              + ((yy - head_cy) / (head_ry * 1.42))**2)
    face_zone = (np.abs(hx) < 0.50) & (hy > -0.62) & (hy < 0.72)
    hair_mask = (hair_d < 1.0) & ~face_zone & (hy < 0.52)
    h_alpha = np.where(hair_mask, np.clip(1.0 - hair_d, 0.0, 1.0) * 0.88, 0.0)
    arr = _blend(arr, np.array([0.19, 0.14, 0.09], dtype=np.float32), h_alpha)

    # Dark translucent veil over crown
    veil_zone = (hair_d < 0.70) & (hy < -0.10) & (yy < 0.28)
    v_alpha = np.clip(0.70 - hair_d, 0.0, 1.0) * 0.55 * veil_zone
    arr = _blend(arr, np.array([0.12, 0.10, 0.08], dtype=np.float32), v_alpha)

    # ── Folded hands, lower centre of composition ─────────────────────────────
    hndx = (xx - 0.504) / 0.175
    hndy = (yy - 0.845) / 0.085
    hands_d = hndx**2 + hndy**2
    hand_alpha = np.clip(1.25 - hands_d, 0.0, 1.0) ** 0.72 * 0.78
    arr = _blend(arr, np.array([0.74, 0.60, 0.45], dtype=np.float32), hand_alpha)

    arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    ref = Image.fromarray(arr, "RGB")
    ref = ref.filter(ImageFilter.GaussianBlur(5))
    return ref


def paint_mona_lisa(output_path: str = "mona_lisa_s176.png") -> str:
    print("=" * 66)
    print("  Mona Lisa — Session 176")
    print("  Marco d'Oggiono × multilayer_atmospheric_veil (three-scale sfumato)")
    print("=" * 66)

    ref = build_reference(W, H)
    leo = get_style("leonardo")
    p = Painter(W, H)

    # ── Warm amber panel ground — Milanese tradition ──────────────────────────
    p.tone_ground(leo.ground_color, texture_strength=0.06)
    print("\n  [1/13] Tone ground complete")

    # ── Broad underpainting — atmospheric tonal layout ────────────────────────
    p.underpainting(ref, stroke_size=48, n_strokes=160)
    print("  [2/13] Underpainting complete")

    # ── Mid-range colour masses ───────────────────────────────────────────────
    p.block_in(ref, stroke_size=32, n_strokes=340)
    print("  [3/13] Block-in complete")

    # ── Form building — sfumato-guided strokes ────────────────────────────────
    p.build_form(ref, stroke_size=10, n_strokes=1400)
    print("  [4/13] Build form complete")

    # ── Leonardo sfumato veil — primary edge dissolution ─────────────────────
    p.sfumato_veil_pass(
        ref,
        n_veils       = 10,
        blur_radius   = 14.0,
        warmth        = 0.38,
        veil_opacity  = 0.07,
        edge_only     = True,
        chroma_dampen = 0.20,
    )
    print("  [5/13] Sfumato veil pass complete")

    # ── Session 176: doggiono_leonardesque_warmth_pass ────────────────────────
    # THREE-GATE: warm ivory in highlights + cool violet in shadows + sfumato at edges.
    # Marco d'Oggiono's inherited Leonardesque warmth: peaks glow amber-ivory,
    # shadows retain violet depth without Boltraffio's harder blue-grey.
    p.doggiono_leonardesque_warmth_pass(
        highlight_lo     = 0.60,
        ivory_r          = 0.022,
        ivory_g          = 0.014,
        ivory_b          = 0.003,
        shadow_hi        = 0.38,
        shadow_r         = 0.010,
        shadow_g         = 0.002,
        shadow_b         = 0.020,
        edge_thresh      = 0.06,
        edge_rng         = 0.10,
        sfumato_sigma    = 2.5,
        sfumato_strength = 0.30,
        opacity          = 0.35,
    )
    print("  [6/13] d'Oggiono Leonardesque warmth pass complete (s176 new — pass 73)")

    # ── Session 176: multilayer_atmospheric_veil_pass ─────────────────────────
    # THREE-SCALE sfumato: fine σ=1.5 / medium σ=4.5 / coarse σ=12.0.
    # Weighted blend (40/35/25) gated on Sobel edge magnitude.
    # Dissolves edges at multiple spatial frequencies simultaneously, creating
    # the atmospheric depth quality of Leonardo's layered glazing technique.
    p.multilayer_atmospheric_veil_pass(
        sigma_fine    = 1.5,
        sigma_medium  = 4.5,
        sigma_coarse  = 12.0,
        weight_fine   = 0.40,
        weight_medium = 0.35,
        weight_coarse = 0.25,
        edge_thresh   = 0.04,
        edge_rng      = 0.12,
        opacity       = 0.42,
    )
    print("  [7/13] Multi-layer atmospheric veil pass complete (s176 new — pass 74)")

    # ── Session 175: skin_subsurface_scatter_pass ─────────────────────────────
    p.skin_subsurface_scatter_pass(
        scatter_sigma    = 8.0,
        scatter_strength = 0.22,
        amber_r          = 0.08,
        amber_b          = -0.05,
        opacity          = 0.50,
    )
    print("  [8/13] Skin subsurface scatter pass complete")

    # ── Session 174: figure_contour_atmosphere_pass ───────────────────────────
    p.figure_contour_atmosphere_pass(
        blur_sigma      = 5.0,
        bleed_strength  = 0.20,
        edge_threshold  = 0.05,
        luma_lo         = 0.05,
        luma_hi         = 0.95,
        opacity         = 0.38,
    )
    print("  [9/13] Figure contour atmosphere pass complete")

    # ── Compositional tonal envelope — portrait lighting vignette ─────────────
    p.tonal_envelope_pass(
        center_x      = 0.488,
        center_y      = 0.32,
        radius        = 0.48,
        lift_strength = 0.09,
        lift_warmth   = 0.35,
        edge_darken   = 0.07,
        gamma         = 1.9,
    )
    print("  [10/13] Tonal envelope pass complete")

    # ── Selective focus — face is sharpest, edges soften ──────────────────────
    p.selective_focus_pass(
        center_x        = 0.488,
        center_y        = 0.29,
        focus_radius    = 0.34,
        max_blur_radius = 2.8,
        desaturation    = 0.10,
        gamma           = 2.2,
    )
    print("  [11/13] Selective focus pass complete")

    # ── Final lights and glaze ────────────────────────────────────────────────
    p.place_lights(ref, stroke_size=5, n_strokes=320)
    print("  [12/13] Place lights complete")

    p.glaze((0.72, 0.52, 0.22), opacity=0.06)
    print("  [13/13] Final amber glaze complete")

    p.finish(vignette=0.28, crackle=True)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Painting saved -> {output_path}  ({W}×{H})")
    print("=" * 66)
    return output_path


if __name__ == "__main__":
    out = "mona_lisa_s176.png"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    paint_mona_lisa(out)
