"""
paint_mona_lisa_s164.py — Mona Lisa portrait for session 164.

Subject: enigmatic half-length female figure, three-quarter pose, sfumato
technique, dreamlike geological landscape background, dark veil, dark dress,
folded hands — the full Renaissance portrait prompt.

Artistic discovery (session 164): Artemisia Gentileschi (1593–c.1656)
  - Roman/Neapolitan Baroque painter, daughter of Orazio Gentileschi
  - One of the most significant female artists before the modern era
  - Known for powerful, dramatic Caravaggesque style with intense directional
    spotlight from upper-left and vivid lit-zone chroma amplification
  - Her signature: psychological directness, warm amber-ivory flesh in spotlight,
    near-black void backgrounds, saturated costume colours in lit zones

New pipeline enhancements (session 164):
  - gentileschi_dramatic_flesh_pass: FIFTY-FIRST DISTINCT MODE
    DIRECTIONAL TENEBRISM WITH ANISOTROPIC CHROMA-LIFT:
    (1) Spatial directional gradient (upper-left to lower-right) as illumination model
    (2) Shadow deepening: (1 - spot_wt) x luma gate — anisotropic, not uniform
    (3) Warm amber lift in spotlight zone
    (4) Directional chroma amplification — saturated colours intensify in spotlight
  - shadow_color_temperature_pass: FIFTY-SECOND DISTINCT MODE
    LUMINANCE-GATED DUAL COLOR TEMPERATURE SEPARATION:
    Simultaneously cools shadows (blue-violet shift) and warms highlights
    (amber shift) — Old Master warm-light / cool-shadow colour harmony
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
    sky   = np.array([0.62, 0.64, 0.68], dtype=np.float32)
    rocks = np.array([0.44, 0.48, 0.47], dtype=np.float32)
    earth = np.array([0.28, 0.33, 0.29], dtype=np.float32)

    t_sky   = np.clip(1.0 - yy * 4.5, 0.0, 1.0)
    t_earth = np.clip((yy - 0.68) * 5.0, 0.0, 1.0)
    t_mid   = np.clip(1.0 - t_sky - t_earth, 0.0, 1.0)

    arr = (sky[None, None, :]   * t_sky[:, :, None]
         + rocks[None, None, :] * t_mid[:, :, None]
         + earth[None, None, :] * t_earth[:, :, None])

    # Horizon mismatch — left sits slightly higher, creating uncanny quality
    left_lift = np.clip(0.55 - xx, 0.0, 0.55) * 0.14
    arr += left_lift[:, :, None] * np.array([0.02, 0.06, 0.16], dtype=np.float32)

    # Winding path on the left
    path_x = 0.24 + (yy - 0.30) * 0.20
    path_dist = np.abs(xx - path_x) / 0.045
    path_mask = (np.clip(1.0 - path_dist, 0.0, 1.0)
                 * np.clip((yy - 0.25) / 0.40, 0.0, 1.0))
    arr += path_mask[:, :, None] * np.array([0.07, 0.08, 0.06], dtype=np.float32)

    # Rocky outcrops — craggy formations mid-background
    for rx, ry, rsx, rsy in [(0.14, 0.42, 0.09, 0.07),
                               (0.82, 0.44, 0.07, 0.05),
                               (0.64, 0.37, 0.06, 0.04),
                               (0.90, 0.50, 0.05, 0.08)]:
        rd = ((xx - rx) / rsx)**2 + ((yy - ry) / rsy)**2
        rmask = np.clip(1.2 - rd, 0.0, 1.0) ** 1.5 * 0.38
        arr = _blend(arr, np.array([0.26, 0.28, 0.25], dtype=np.float32), rmask)

    # Water / river suggestion — middle distance, right of centre
    water_d = ((xx - 0.72) / 0.22)**2 + ((yy - 0.46) / 0.04)**2
    water_mask = np.clip(1.0 - water_d, 0.0, 1.0)**2 * 0.32
    arr += water_mask[:, :, None] * np.array([0.16, 0.22, 0.32], dtype=np.float32)

    arr = np.clip(arr, 0.0, 1.0)

    # ── Figure: torso, positioned slightly right of centre ───────────────────
    fig_cx, fig_cy = 0.512, 0.628
    fig_rx, fig_ry = 0.30, 0.44
    fx = (xx - fig_cx) / fig_rx
    fy = (yy - fig_cy) / fig_ry
    fig_d = fx**2 + fy**2

    flesh = np.array([0.74, 0.60, 0.44], dtype=np.float32)
    fig_alpha = np.clip(1.55 - fig_d, 0.0, 1.0) ** 0.55
    arr = _blend(arr, flesh, fig_alpha)

    # Dark forest-green / blue-black dress
    dress = np.array([0.09, 0.14, 0.11], dtype=np.float32)
    d_alpha = np.clip(1.2 - fig_d, 0.0, 1.0) * (yy > 0.56).astype(np.float32) * 0.78
    arr = _blend(arr, dress, d_alpha)

    # Semi-transparent gauze wrap — layered fabric depth
    gauze = np.array([0.34, 0.38, 0.35], dtype=np.float32)
    g_alpha = (np.clip(0.90 - fig_d, 0.0, 1.0)
               * ((yy > 0.48) & (yy < 0.66) & (fig_d < 0.90)).astype(np.float32) * 0.26)
    arr = _blend(arr, gauze, g_alpha)

    # Amber-gold neckline trim
    neck_d = ((xx - fig_cx) / 0.14)**2 + ((yy - 0.47) / 0.022)**2
    neck_mask = np.clip(1.0 - neck_d, 0.0, 1.0) ** 2 * 0.55 * (yy > 0.45).astype(np.float32)
    arr = _blend(arr, np.array([0.80, 0.64, 0.20], dtype=np.float32), neck_mask)

    # ── Head ─────────────────────────────────────────────────────────────────
    head_cx, head_cy = 0.492, 0.260
    head_rx, head_ry = 0.122, 0.154
    hx = (xx - head_cx) / head_rx
    hy = (yy - head_cy) / head_ry
    head_d = hx**2 + hy**2

    face = np.array([0.85, 0.73, 0.55], dtype=np.float32)
    head_alpha = np.clip(1.45 - head_d, 0.0, 1.0) ** 0.50
    arr = _blend(arr, face, head_alpha)

    # Upper-left light — high forehead catchlight
    lit_d = (hx + 0.30)**2 + (hy + 0.20)**2
    lit_alpha = np.clip(1.0 - lit_d, 0.0, 1.0) ** 1.8 * 0.52 * head_alpha
    arr = _blend(arr, np.array([0.92, 0.84, 0.68], dtype=np.float32), lit_alpha)

    # Shadow on right cheek
    shad_d = (-hx + 0.30)**2 + (hy - 0.08)**2
    shad_alpha = np.clip(1.0 - shad_d, 0.0, 1.0) ** 2.2 * 0.42 * head_alpha
    arr = _blend(arr, np.array([0.48, 0.36, 0.24], dtype=np.float32), shad_alpha)

    # Smooth high forehead
    brow_d = ((xx - head_cx) / (head_rx * 1.12))**2 + ((yy - (head_cy - head_ry * 0.74)) / 0.02)**2
    brow_mask = np.clip(1.0 - brow_d, 0.0, 1.0) ** 2 * 0.20
    arr = _blend(arr, np.array([0.88, 0.78, 0.62], dtype=np.float32), brow_mask)

    # ── Hair: dark warm brown, centre-parted ─────────────────────────────────
    hair_d = (((xx - head_cx) / (head_rx * 1.56))**2
              + ((yy - head_cy) / (head_ry * 1.42))**2)
    face_zone = (np.abs(hx) < 0.50) & (hy > -0.62) & (hy < 0.72)
    hair_mask = (hair_d < 1.0) & ~face_zone & (hy < 0.55)
    h_alpha = np.where(hair_mask, np.clip(1.0 - hair_d, 0.0, 1.0) * 0.88, 0.0)
    arr = _blend(arr, np.array([0.16, 0.11, 0.07], dtype=np.float32), h_alpha)

    # Dark translucent veil over crown
    veil_zone = (hair_d < 0.70) & (hy < -0.08) & (yy < 0.27)
    v_alpha = np.clip(0.70 - hair_d, 0.0, 1.0) * 0.55 * veil_zone.astype(np.float32)
    arr = _blend(arr, np.array([0.09, 0.07, 0.06], dtype=np.float32), v_alpha)

    # ── Hands: folded in lap, right over left ────────────────────────────────
    hndx = (xx - 0.505) / 0.178
    hndy = (yy - 0.852) / 0.083
    hands_d = hndx**2 + hndy**2
    hand_alpha = np.clip(1.28 - hands_d, 0.0, 1.0) ** 0.70 * 0.80
    arr = _blend(arr, np.array([0.72, 0.58, 0.42], dtype=np.float32), hand_alpha)

    # Right hand — draped over left, catches more light
    rh_d = ((xx - 0.524) / 0.092)**2 + ((yy - 0.840) / 0.040)**2
    rh_alpha = np.clip(1.0 - rh_d, 0.0, 1.0) ** 1.5 * 0.28
    arr = _blend(arr, np.array([0.80, 0.68, 0.52], dtype=np.float32), rh_alpha)

    arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    ref = Image.fromarray(arr, "RGB")
    ref = ref.filter(ImageFilter.GaussianBlur(5))
    return ref


def paint(output_path: str = "mona_lisa_s164.png") -> str:
    """Full Leonardo sfumato pipeline with session 164 Artemisia Gentileschi passes."""
    print("=" * 64)
    print("  Session 164 — Mona Lisa sfumato portrait")
    print("  Artistic discovery: Artemisia Gentileschi (1593–c.1656)")
    print("    FIFTY-FIRST MODE: gentileschi_dramatic_flesh_pass")
    print("    — directional tenebrism with anisotropic chroma-lift")
    print("    FIFTY-SECOND MODE: shadow_color_temperature_pass")
    print("    — warm-light / cool-shadow dual temperature split")
    print("=" * 64)

    ref = build_reference(W, H)
    ref.save("mona_lisa_s164_reference.png")
    print(f"  Reference saved -> mona_lisa_s164_reference.png  ({W}x{H})")

    leo = get_style("leonardo")
    p = Painter(W, H)

    print("  [1/18] Tone ground ...")
    p.tone_ground(leo.ground_color, texture_strength=0.06)

    print("  [2/18] Underpainting ...")
    p.underpainting(ref, stroke_size=52, n_strokes=160)

    print("  [3/18] Block-in ...")
    p.block_in(ref, stroke_size=34, n_strokes=340)

    print("  [4/18] Build form ...")
    p.build_form(ref, stroke_size=10, n_strokes=1400)

    print("  [5/18] Sfumato veil pass ...")
    p.sfumato_veil_pass(
        ref,
        n_veils       = 10,
        blur_radius   = 14.0,
        warmth        = 0.36,
        veil_opacity  = 0.07,
        edge_only     = True,
        chroma_dampen = 0.22,
    )

    print("  [6/18] Edge sfumato dissolution pass ...")
    p.edge_sfumato_dissolution_pass(
        grad_threshold = 0.10,
        blur_sigma     = 6.0,
        edge_strength  = 0.38,
        opacity        = 0.30,
    )

    print("  [7/18] Skin subsurface scatter pass ...")
    p.skin_subsurface_scatter_pass(
        scatter_sigma    = 5.0,
        scatter_strength = 0.20,
        warm_boost       = 1.04,
        cool_damp        = 0.97,
        opacity          = 0.26,
    )

    print("  [8/18] Tonal envelope pass ...")
    p.tonal_envelope_pass(
        center_x      = 0.492,
        center_y      = 0.31,
        radius        = 0.48,
        lift_strength = 0.09,
        lift_warmth   = 0.34,
        edge_darken   = 0.07,
        gamma         = 1.9,
    )

    print("  [9/18] Selective focus pass ...")
    p.selective_focus_pass(
        center_x        = 0.492,
        center_y        = 0.28,
        focus_radius    = 0.34,
        max_blur_radius = 2.8,
        desaturation    = 0.10,
        gamma           = 2.2,
    )

    print("  [10/18] Massys bridge glazing pass (s162 heritage) ...")
    p.massys_bridge_glazing_pass(
        flesh_warm_r        = 0.09,
        flesh_warm_g        = 0.04,
        flesh_warm_b_reduce = 0.06,
        shadow_cool_lo      = 0.20,
        shadow_cool_hi      = 0.44,
        shadow_cool_b       = 0.06,
        shadow_cool_r       = 0.03,
        pearl_lo            = 0.62,
        pearl_hi            = 0.80,
        pearl_r             = 0.04,
        pearl_b             = 0.02,
        skin_sigma          = 6.0,
        opacity             = 0.24,
    )

    print("  [11/18] Reynolds Grand Manner mezzotint tone pass ...")
    p.reynolds_grand_manner_pass(
        amber_strength  = 0.06,
        amber_r         = 0.08,
        amber_g         = 0.04,
        amber_b_reduce  = 0.06,
        highlight_lo    = 0.70,
        highlight_power = 1.5,
        hi_boost        = 0.04,
        shadow_hi       = 0.30,
        shadow_power    = 1.5,
        shadow_deepen_r = 0.12,
        shadow_deepen_g = 0.10,
        shadow_deepen_b = 0.08,
        opacity         = 0.24,
    )

    print("  [12/18] Schedoni luminous emergence pass (s163 heritage) ...")
    p.schedoni_luminous_emergence_pass(
        shadow_hi      = 0.28,
        shad_power     = 1.8,
        compress       = 0.22,
        highlight_lo   = 0.62,
        hi_power       = 1.4,
        chroma_boost   = 0.30,
        glow_r         = 0.03,
        glow_g         = 0.018,
        opacity        = 0.28,
    )

    print("  [13/18] Warm highlight bloom pass (s163 heritage) ...")
    p.warm_highlight_bloom_pass(
        warm_r_thresh  = 0.58,
        warm_r_ratio   = 1.04,
        luma_thresh    = 0.56,
        bloom_sigma    = 14.0,
        bloom_strength = 0.14,
        bloom_r        = 0.82,
        bloom_g        = 0.64,
        bloom_b        = 0.32,
        opacity        = 0.20,
    )

    print("  [14/18] Gentileschi dramatic flesh pass — FIFTY-FIRST DISTINCT MODE ...")
    # Upper-left spotlight with directional anisotropic chroma-lift.
    # Applied gently so it enhances the sfumato rather than overriding it:
    # slight directional deepening of the lower-right shadow zone + warm
    # amber lift in the upper-left spotlight zone.
    p.gentileschi_dramatic_flesh_pass(
        dir_x         = 0.55,   # horizontal left-bias: upper-left spotlight
        dir_y         = 0.45,   # vertical top-bias
        shadow_hi     = 0.36,   # compress deep shadow pixels
        shadow_deepen = 0.32,   # moderate — sfumato softens the tenebrism
        luma_lo       = 0.42,
        amber_r       = 0.040,  # warm amber lift in spotlight zone
        amber_g       = 0.018,
        chroma_boost  = 0.28,   # moderate chroma amplification in spotlight
        opacity       = 0.30,
    )

    print("  [15/18] Shadow color temperature pass — FIFTY-SECOND DISTINCT MODE ...")
    # Warm-light / cool-shadow split: the Old Master colour temperature harmony
    # that gives the penumbra its characteristic 'pearly' quality.
    p.shadow_color_temperature_pass(
        shadow_thresh   = 0.42,
        shadow_power    = 1.4,
        cool_b          = 0.038,    # subtle blue-violet in shadows
        cool_r          = 0.014,
        cool_g          = 0.006,
        highlight_thresh= 0.62,
        highlight_power = 1.3,
        warm_r          = 0.032,    # gentle amber in highlights
        warm_g          = 0.014,
        opacity         = 0.26,
    )

    print("  [16/18] Place lights ...")
    p.place_lights(ref, stroke_size=5, n_strokes=320)

    print("  [17/18] Final glaze ...")
    p.glaze((0.70, 0.50, 0.20), opacity=0.06)

    print("  [18/18] Finish ...")
    p.finish(vignette=0.28, crackle=True)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Painting saved -> {output_path}  ({W}x{H})")
    print("=" * 64)
    return output_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "mona_lisa_s164.png"
    paint(out)
