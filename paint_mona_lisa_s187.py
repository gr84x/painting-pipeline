"""
paint_mona_lisa_s187.py — Mona Lisa portrait for session 187.

Subject: enigmatic half-length female figure, three-quarter pose, sfumato
technique, dreamlike geological landscape background, dark veil, dark dress,
folded hands — the full Renaissance portrait prompt.

Artistic discovery (session 187): Ambrogio de Predis (c. 1455–after 1508)
  - Milanese Leonardesque / Italian Renaissance
  - Crystalline metallic precision within sfumato — cool-silver highlights
  - Leonardo's closest Milanese court collaborator (Virgin of the Rocks)
  - Portrait of a Young Woman (Bianca Maria Sforza?), c. 1493–1496
  - Portrait of Emperor Maximilian I, c. 1502
  - Defining quality: COOL-SILVER TOP HIGHLIGHTS — the topmost lit zone on
    flesh carries a subtle blue-grey tint, like polished silver rather than
    candlelight, producing an enamelled, jewel-like reading unique among
    Milanese sfumato painters.  Structural precision just beneath the sfumato
    surface distinguishes de Predis from pure Leonardo dissolution.

New pipeline enhancements (session 187):
  - de_predis_crystalline_clarity_pass: NINETY-FOURTH DISTINCT MODE
    PRECISION UNSHARP-MASK WITH COOL-SILVER EDGE TINTING:
    Applies a precision USM restricted to the mid-to-bright luma range
    (luma_lo=0.35, luma_hi=0.85), then tints the detected edge zones with a
    cool-silver shift (cool_r_shift=-0.010, cool_b_shift=0.015).  The edge
    detection is derived from the unsharp residual magnitude.  This implements
    de Predis's defining quality: broad sfumato softness in the passages, with
    crystalline metallic precision at key structural transitions.
    NOVEL: FIRST pass to combine UNSHARP-MASK SHARPENING with COOL-SILVER
    CHROMATIC TINT on detected edges — distinct from all prior passes.

  - luminous_midtone_lift_pass: RANDOM IMPROVEMENT
    WARM BELL-CURVE LUMINANCE LIFT IN THE MIDTONE REGISTER:
    A symmetric bell-curve gate centred at the midpoint of [mid_lo, mid_hi]
    selectively lifts R, G, B in the midtone zone, loading maximum luminosity
    into the mid-value register.  Models the Old Master technique of making
    forms appear self-illuminated rather than merely reflecting surface light.
    NOVEL: FIRST pass to apply SYMMETRIC MIDTONE-BAND BELL-CURVE LIFT without
    asymmetric peak bias — distinct from fra_galgario_living_surface_pass.
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

    # Horizon mismatch — left sits slightly higher
    left_lift = np.clip(0.55 - xx, 0.0, 0.55) * 0.14
    arr += left_lift[:, :, None] * np.array([0.02, 0.06, 0.16], dtype=np.float32)

    # Winding path on the left
    path_x = 0.24 + (yy - 0.30) * 0.20
    path_dist = np.abs(xx - path_x) / 0.045
    path_mask = (np.clip(1.0 - path_dist, 0.0, 1.0)
                 * np.clip((yy - 0.25) / 0.40, 0.0, 1.0))
    arr += path_mask[:, :, None] * np.array([0.07, 0.08, 0.06], dtype=np.float32)

    # Rocky outcrops
    for rx, ry, rsx, rsy in [(0.14, 0.42, 0.09, 0.07),
                               (0.82, 0.44, 0.07, 0.05),
                               (0.64, 0.37, 0.06, 0.04),
                               (0.90, 0.50, 0.05, 0.08)]:
        rd = ((xx - rx) / rsx)**2 + ((yy - ry) / rsy)**2
        rmask = np.clip(1.2 - rd, 0.0, 1.0) ** 1.5 * 0.38
        arr = _blend(arr, np.array([0.26, 0.28, 0.25], dtype=np.float32), rmask)

    # Water suggestion
    water_d = ((xx - 0.72) / 0.22)**2 + ((yy - 0.46) / 0.04)**2
    water_mask = np.clip(1.0 - water_d, 0.0, 1.0)**2 * 0.32
    arr += water_mask[:, :, None] * np.array([0.16, 0.22, 0.32], dtype=np.float32)
    arr = np.clip(arr, 0.0, 1.0)

    # ── Figure: torso, slightly right of centre ───────────────────────────────
    fig_cx, fig_cy = 0.512, 0.628
    fig_rx, fig_ry = 0.30, 0.44
    fx = (xx - fig_cx) / fig_rx
    fy = (yy - fig_cy) / fig_ry
    fig_d = fx**2 + fy**2

    flesh = np.array([0.74, 0.60, 0.44], dtype=np.float32)
    fig_alpha = np.clip(1.55 - fig_d, 0.0, 1.0) ** 0.55
    arr = _blend(arr, flesh, fig_alpha)

    dress = np.array([0.09, 0.14, 0.11], dtype=np.float32)
    d_alpha = np.clip(1.2 - fig_d, 0.0, 1.0) * (yy > 0.56).astype(np.float32) * 0.78
    arr = _blend(arr, dress, d_alpha)

    gauze = np.array([0.34, 0.38, 0.35], dtype=np.float32)
    g_alpha = (np.clip(0.90 - fig_d, 0.0, 1.0)
               * ((yy > 0.48) & (yy < 0.66) & (fig_d < 0.90)).astype(np.float32) * 0.26)
    arr = _blend(arr, gauze, g_alpha)

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

    lit_d = (hx + 0.30)**2 + (hy + 0.20)**2
    lit_alpha = np.clip(1.0 - lit_d, 0.0, 1.0) ** 1.8 * 0.52 * head_alpha
    arr = _blend(arr, np.array([0.92, 0.84, 0.68], dtype=np.float32), lit_alpha)

    shad_d = (-hx + 0.30)**2 + (hy - 0.08)**2
    shad_alpha = np.clip(1.0 - shad_d, 0.0, 1.0) ** 2.2 * 0.42 * head_alpha
    arr = _blend(arr, np.array([0.48, 0.36, 0.24], dtype=np.float32), shad_alpha)

    brow_d = ((xx - head_cx) / (head_rx * 1.12))**2 + ((yy - (head_cy - head_ry * 0.74)) / 0.02)**2
    brow_mask = np.clip(1.0 - brow_d, 0.0, 1.0) ** 2 * 0.20
    arr = _blend(arr, np.array([0.88, 0.78, 0.62], dtype=np.float32), brow_mask)

    # ── Hair ─────────────────────────────────────────────────────────────────
    hair_d = (((xx - head_cx) / (head_rx * 1.56))**2
              + ((yy - head_cy) / (head_ry * 1.42))**2)
    face_zone = (np.abs(hx) < 0.50) & (hy > -0.62) & (hy < 0.72)
    hair_mask = (hair_d < 1.0) & ~face_zone & (hy < 0.55)
    h_alpha = np.where(hair_mask, np.clip(1.0 - hair_d, 0.0, 1.0) * 0.88, 0.0)
    arr = _blend(arr, np.array([0.16, 0.11, 0.07], dtype=np.float32), h_alpha)

    veil_zone = (hair_d < 0.70) & (hy < -0.08) & (yy < 0.27)
    v_alpha = np.clip(0.70 - hair_d, 0.0, 1.0) * 0.55 * veil_zone.astype(np.float32)
    arr = _blend(arr, np.array([0.09, 0.07, 0.06], dtype=np.float32), v_alpha)

    # ── Hands ─────────────────────────────────────────────────────────────────
    hndx = (xx - 0.505) / 0.178
    hndy = (yy - 0.852) / 0.083
    hands_d = hndx**2 + hndy**2
    hand_alpha = np.clip(1.28 - hands_d, 0.0, 1.0) ** 0.70 * 0.80
    arr = _blend(arr, np.array([0.72, 0.58, 0.42], dtype=np.float32), hand_alpha)

    rh_d = ((xx - 0.524) / 0.092)**2 + ((yy - 0.840) / 0.040)**2
    rh_alpha = np.clip(1.0 - rh_d, 0.0, 1.0) ** 1.5 * 0.28
    arr = _blend(arr, np.array([0.80, 0.68, 0.52], dtype=np.float32), rh_alpha)

    arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    ref = Image.fromarray(arr, "RGB")
    ref = ref.filter(ImageFilter.GaussianBlur(5))
    return ref


def paint(output_path: str = "mona_lisa_s187.png") -> str:
    """Full Leonardo sfumato pipeline with session 187 de Predis-inspired passes."""
    print("=" * 64)
    print("  Session 187 — Mona Lisa sfumato portrait")
    print("  Artistic discovery: Ambrogio de Predis (c. 1455–after 1508)")
    print("    Milanese Leonardesque — crystalline metallic precision")
    print("    Leonardo's closest court collaborator (Virgin of the Rocks)")
    print("    Portrait of a Young Woman (Bianca Maria Sforza?)")
    print("    Cool-silver highlights — enamelled, jewel-like flesh quality")
    print("    NINETY-FOURTH MODE: de_predis_crystalline_clarity_pass")
    print("    -- Precision USM + cool-silver edge tinting")
    print("    RANDOM IMPROVEMENT: luminous_midtone_lift_pass")
    print("    -- Warm bell-curve luminance lift in the midtone register")
    print("=" * 64)

    ref = build_reference(W, H)
    print(f"  Reference built  ({W}x{H})")

    leo = get_style("leonardo")
    p = Painter(W, H)

    print("  [1/38] Tone ground ...")
    p.tone_ground(leo.ground_color, texture_strength=0.06)

    print("  [2/38] Underpainting ...")
    p.underpainting(ref, stroke_size=52, n_strokes=160)

    print("  [3/38] Block-in ...")
    p.block_in(ref, stroke_size=34, n_strokes=340)

    print("  [4/38] Build form ...")
    p.build_form(ref, stroke_size=10, n_strokes=1400)

    print("  [5/38] Sfumato veil pass ...")
    p.sfumato_veil_pass(
        ref,
        n_veils                      = 10,
        blur_radius                  = 14.0,
        warmth                       = 0.36,
        veil_opacity                 = 0.07,
        edge_only                    = True,
        chroma_dampen                = 0.22,
        depth_gradient               = 0.45,
        shadow_warm_recovery         = 0.15,
        highlight_ivory_lift         = 0.06,
        atmospheric_blue_shift       = 0.35,
        penumbra_bloom               = 0.07,
        highlight_sharpness_recovery = 0.10,
        highlight_sharpness_thresh   = 0.75,
        highlight_sharpness_sigma    = 1.2,
    )

    print("  [6/38] Edge sfumato dissolution pass ...")
    p.edge_sfumato_dissolution_pass(
        grad_threshold = 0.10,
        blur_sigma     = 6.0,
        edge_strength  = 0.38,
        opacity        = 0.30,
    )

    print("  [7/38] Figure contour atmosphere pass ...")
    p.figure_contour_atmosphere_pass(
        blur_sigma     = 6.0,
        bleed_strength = 0.28,
        edge_threshold = 0.05,
        luma_lo        = 0.06,
        luma_hi        = 0.92,
        opacity        = 0.42,
    )

    print("  [8/38] Skin subsurface scatter pass ...")
    p.skin_subsurface_scatter_pass(
        scatter_sigma    = 5.0,
        scatter_strength = 0.20,
        amber_r          = 0.05,
        amber_b          = -0.03,
        opacity          = 0.26,
    )

    print("  [9/38] Tonal envelope pass ...")
    p.tonal_envelope_pass(
        center_x      = 0.492,
        center_y      = 0.31,
        radius        = 0.48,
        lift_strength = 0.09,
        lift_warmth   = 0.34,
        edge_darken   = 0.07,
        gamma         = 1.9,
    )

    print("  [10/38] Selective focus pass ...")
    p.selective_focus_pass(
        center_x        = 0.492,
        center_y        = 0.28,
        focus_radius    = 0.34,
        max_blur_radius = 2.8,
        desaturation    = 0.10,
        gamma           = 2.2,
    )

    print("  [11/38] Massys bridge glazing pass ...")
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
        opacity             = 0.22,
    )

    print("  [12/38] Reynolds Grand Manner mezzotint tone pass ...")
    p.reynolds_grand_manner_pass(
        amber_strength  = 0.05,
        amber_r         = 0.07,
        amber_g         = 0.03,
        amber_b_reduce  = 0.05,
        highlight_lo    = 0.70,
        highlight_power = 1.5,
        hi_boost        = 0.03,
        shadow_hi       = 0.38,
        shadow_deepen_r = 0.10,
        shadow_deepen_g = 0.09,
        shadow_deepen_b = 0.08,
        opacity         = 0.26,
    )

    print("  [13/38] Luminance gradient warmth pass ...")
    p.luminance_gradient_warmth_pass(
        grad_sigma  = 2.0,
        warm_r      = 0.025,
        warm_g      = 0.012,
        luma_lo     = 0.10,
        luma_hi     = 0.82,
        opacity     = 0.28,
    )

    print("  [14/38] Warm ambient occlusion pass ...")
    p.warm_ambient_occlusion_pass(
        occ_radius  = 18.0,
        shad_lo     = 0.10,
        shad_hi     = 0.40,
        warm_r      = 0.05,
        warm_g      = 0.02,
        opacity     = 0.28,
    )

    print("  [15/38] Shadow color temperature pass ...")
    p.shadow_color_temperature_pass(
        shadow_thresh     = 0.38,
        cool_b            = 0.040,
        cool_r            = 0.016,
        highlight_thresh  = 0.68,
        warm_r            = 0.030,
        warm_g            = 0.014,
        opacity           = 0.24,
    )

    print("  [16/38] Multilayer atmospheric veil pass ...")
    p.multilayer_atmospheric_veil_pass(
        sigma_fine    = 1.5,
        sigma_medium  = 5.0,
        sigma_coarse  = 14.0,
        weight_fine   = 0.40,
        weight_medium = 0.36,
        weight_coarse = 0.24,
        edge_thresh   = 0.06,
        opacity       = 0.28,
    )

    print("  [17/38] Peripheral defocus pass ...")
    p.peripheral_defocus_pass(
        inner_radius  = 0.38,
        blur_sigma    = 4.0,
        power         = 2.0,
        blur_strength = 0.48,
        opacity       = 0.30,
    )

    print("  [18/38] Luminance preserving chroma boost pass ...")
    p.luminance_preserving_chroma_boost_pass(
        boost         = 0.12,
        luma_lo       = 0.18,
        luma_hi       = 0.82,
        opacity       = 0.22,
    )

    print("  [19/38] Shadow chroma depth pass ...")
    p.shadow_chroma_depth_pass(
        shadow_lo    = 0.12,
        shadow_hi    = 0.44,
        amplify      = 0.24,
        highlight_lo = 0.80,
        reduce       = 0.18,
        opacity      = 0.24,
    )

    print("  [20/38] Tonal bounded warmth pass ...")
    p.tonal_bounded_warmth_pass(
        mid_dark_lo = 0.18,
        mid_dark_hi = 0.44,
        warm_r      = 0.022,
        warm_g      = 0.012,
        warm_b      = -0.005,
        void_hi     = 0.08,
        void_cool_b = 0.010,
        void_cool_r = -0.006,
        opacity     = 0.28,
    )

    print("  [21/38] Canvas tooth texture pass ...")
    p.canvas_tooth_texture_pass(
        tooth_freq  = 48.0,
        tooth_lo    = 0.22,
        tooth_hi    = 0.68,
        tooth_depth = 0.10,
        ground_r    = 0.60,
        ground_g    = 0.52,
        ground_b    = 0.36,
        opacity     = 0.28,
    )

    print("  [22/38] Chromatic vignette pass ...")
    p.chromatic_vignette_pass(
        radius          = 0.72,
        darken_strength = 0.18,
        cool_b          = 0.04,
        cool_r_reduce   = 0.02,
        vig_gamma       = 2.0,
        luma_lo         = 0.08,
        opacity         = 0.32,
    )

    print("  [23/38] Cesare da Sesto clarity pass ...")
    p.cesare_da_sesto_clarity_pass(
        smooth_thresh    = 0.30,
        grad_sigma       = 1.5,
        warm_r           = 0.018,
        warm_g           = 0.008,
        mid_grad_center  = 0.50,
        mid_grad_width   = 0.22,
        cool_b           = 0.016,
        cool_r           = 0.008,
        opacity          = 0.26,
    )

    print("  [24/38] Benozzo Gozzoli pageant pass ...")
    p.benozzo_gozzoli_pageant_pass(
        snap_strength = 0.08,
        luma_lo       = 0.15,
        luma_hi       = 0.86,
        opacity       = 0.20,
    )

    print("  [25/38] Sirani contextual warmth pass [s183, 86th mode] ...")
    p.sirani_contextual_warmth_pass(
        field_sigma          = 28.0,
        warm_bias_threshold  = 0.03,
        warm_r_delta         = 0.020,
        warm_g_delta         = 0.012,
        warm_b_delta         = 0.010,
        opacity              = 0.38,
    )

    print("  [26/38] Adaptive tonal pivot pass [s183, 87th mode] ...")
    p.adaptive_tonal_pivot_pass(
        contrast_strength = 0.22,
        sigmoid_slope     = 6.0,
        opacity           = 0.30,
    )

    print("  [27/38] *** CERUTI DIGNITY SHADOW PASS [s184, 88th mode] ***")
    p.ceruti_dignity_shadow_pass(
        shadow_lo    = 0.08,
        shadow_hi    = 0.42,
        warm_r_delta = 0.018,
        warm_g_delta = 0.010,
        opacity      = 0.32,
    )

    print("  [28/38] *** HUE COHERENCE FIELD PASS [s184, 89th mode] ***")
    p.hue_coherence_field_pass(
        field_sigma         = 22.0,
        coherence_boost     = 0.15,
        dissonance_suppress = 0.10,
        opacity             = 0.28,
    )

    print("  [29/38] *** FRA GALGARIO LIVING SURFACE PASS [s185, 90th mode] ***")
    p.fra_galgario_living_surface_pass(
        glow_lo     = 0.35,
        glow_hi     = 0.80,
        luma_peak   = 0.58,
        half_width  = 0.20,
        glow_r_lift = 0.022,
        glow_g_lift = 0.012,
        opacity     = 0.30,
    )

    print("  [30/38] *** CHROMATIC TEMPERATURE FIELD PASS [s185, 91st mode] ***")
    p.chromatic_temperature_field_pass(
        warm_strength    = 0.025,
        cool_strength    = 0.020,
        warm_luma_lo     = 0.62,
        cool_luma_hi     = 0.35,
        transition_width = 0.22,
        opacity          = 0.28,
    )

    print("  [31/38] *** SOLARIO CHROMATIC POLAR PASS [s186, 93rd mode] ***")
    p.solario_chromatic_polar_pass(
        hue_rotate_deg = 7.0,
        chroma_boost   = 0.12,
        l_lo           = 20.0,
        l_hi           = 85.0,
        opacity        = 0.26,
    )

    print("  [32/38] *** LOCAL STATISTICAL HARMONY PASS [s186, random improvement] ***")
    p.local_statistical_harmony_pass(
        sigma            = 14.0,
        harmony_strength = 0.15,
        luma_lo          = 0.12,
        luma_hi          = 0.88,
        opacity          = 0.24,
    )

    print("  [33/38] *** DE PREDIS CRYSTALLINE CLARITY PASS [s187, 94th mode] ***")
    p.de_predis_crystalline_clarity_pass(
        sharp_sigma    = 1.5,
        sharp_strength = 0.30,
        cool_r_shift   = -0.010,
        cool_b_shift   = 0.015,
        luma_lo        = 0.35,
        luma_hi        = 0.85,
        opacity        = 0.26,
    )

    print("  [34/38] *** LUMINOUS MIDTONE LIFT PASS [s187, random improvement] ***")
    p.luminous_midtone_lift_pass(
        mid_lo  = 0.30,
        mid_hi  = 0.68,
        lift_r  = 0.022,
        lift_g  = 0.012,
        lift_b  = 0.004,
        opacity = 0.26,
    )

    print("  [35/38] Chromatic edge halation pass ...")
    p.chromatic_edge_halation_pass(
        grad_threshold  = 0.06,
        bloom_sigma     = 4.0,
        bleed_strength  = 0.18,
        luma_lo         = 0.18,
        luma_hi         = 0.90,
        opacity         = 0.24,
    )

    print("  [36/38] Skin subsurface scatter pass (final warm glow) ...")
    p.skin_subsurface_scatter_pass(
        scatter_sigma    = 3.5,
        scatter_strength = 0.14,
        amber_r          = 0.035,
        amber_b          = -0.018,
        opacity          = 0.20,
    )

    print("  [37/38] Sfumato veil final ...")
    p.sfumato_veil_pass(
        ref,
        n_veils                      = 4,
        blur_radius                  = 8.0,
        warmth                       = 0.24,
        veil_opacity                 = 0.05,
        edge_only                    = True,
        chroma_dampen                = 0.14,
        depth_gradient               = 0.28,
        shadow_warm_recovery         = 0.10,
        highlight_ivory_lift         = 0.04,
        atmospheric_blue_shift       = 0.22,
        penumbra_bloom               = 0.04,
        highlight_sharpness_recovery = 0.08,
        highlight_sharpness_thresh   = 0.80,
        highlight_sharpness_sigma    = 1.0,
    )

    print("  [38/38] Place lights, final glaze + finish ...")
    p.place_lights(ref, stroke_size=5, n_strokes=320)
    # Cool-warm glaze — de Predis's restrained enamelled palette
    p.glaze((0.70, 0.65, 0.58), opacity=0.032)
    p.finish(vignette=0.28, crackle=True)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Painting saved -> {output_path}  ({W}x{H})")
    print("=" * 64)
    return output_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "mona_lisa_s187.png"
    paint(out)
