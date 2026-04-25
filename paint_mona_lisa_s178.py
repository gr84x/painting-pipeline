"""
paint_mona_lisa_s178.py — Mona Lisa portrait for session 178.

Subject: enigmatic half-length female figure, three-quarter pose, sfumato
technique, dreamlike geological landscape background, dark veil, dark dress,
folded hands — the full Renaissance portrait prompt.

Artistic discovery (session 178): Adriaen Brouwer (1605/06–1638)
  - Supreme master of the Flemish tavern genre; collected obsessively by
    Rubens (17 works) and Rembrandt (8 works) — the highest endorsement
    any genre painter has ever received from peers of that stature
  - Painted rough peasants, card-sharps, smokers and brawlers with a
    directness and economy that transcends genre: Van Gogh studied him
    closely as a pioneer of expressive impasto two centuries before the term
  - Extreme alla prima technique: thin paint on very dark umber ground,
    no underpainting, no blending time — the gesture is the truth
  - Palette is radically limited: raw umber, yellow ochre, tobacco amber,
    a touch of vermilion, lead white — almost no blue or cool green
  - His darkness is warm, never cool: the near-black ground breathes amber
    warmth through thin paint everywhere, unifying figure and interior
  - Single warm light source (candle, window, hearth) against shadow void

New pipeline enhancements (session 178):
  - brouwer_tavern_glow_pass: SEVENTY-FOURTH DISTINCT MODE
    THREE-ZONE BROUWER REALISM ENCODING:
    (1) AMBER MID-TONE WARMTH — Gaussian bell gate on mid-luminance
        (luma 0.28–0.62): R + amber_r, G + amber_g, B − amber_b_reduce;
        Brouwer's mid-tones are warm tobacco, not daylight grey
    (2) SMOKY SHADOW DESATURATION — linear gate below smoke_hi (0.30):
        chromatic desaturation toward luminance mean (smoke_desat=0.08);
        tavern smoke mutes colour in the darkest zones — warm grey, not void
    (3) WARM CANDLELIGHT ACCENT — linear gate above accent_lo (0.55):
        R + accent_r, G + accent_g; where the single warm source touches
        flesh, it leaves a golden flicker that is never neutral
    NOVEL: FIRST pass combining tobacco-amber mid-tone Gaussian bell AND
    smoky shadow chromatic desaturation AND warm candlelight highlight accent.

  - penumbra_chroma_bloom (sfumato_veil_pass improvement): SESSION 178
    After all sfumato veils, selectively boosts colour saturation in the
    penumbra zone (luma 0.28–0.52) via Gaussian bell gate.  Art-historical
    basis: multispectral analysis of the Mona Lisa (Louvre 2020) shows
    maximum chromatic warmth in the mid-shadow transition — carnation at
    the shadow edge — not in the highlights (ivory-desaturated) or the deep
    shadows (umber-muted).  Neutral-mean chromatic expansion:
    delta = channel - neutral; boosted = neutral + delta × (1 + bloom × gate).
    First sfumato improvement to target the penumbra CHROMA specifically,
    distinct from penumbra_bloom (s105, targets luminance warmth).
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


def paint(output_path: str = "mona_lisa_s178.png") -> str:
    """Full Leonardo sfumato pipeline with session 178 Brouwer tavern glow + penumbra chroma bloom."""
    print("=" * 64)
    print("  Session 178 — Mona Lisa sfumato portrait")
    print("  Artistic discovery: Adriaen Brouwer (1605/06–1638)")
    print("    Flemish-Dutch Genre Realism — alla prima tavern painter")
    print("    Tobacco amber mid-tones; smoky shadow void")
    print("    SEVENTY-FOURTH MODE: brouwer_tavern_glow_pass")
    print("    -- THREE-ZONE: amber mid-tones + smoky shadows + candlelight")
    print("    SESSION 178 IMPROVEMENT: sfumato penumbra_chroma_bloom")
    print("    -- Penumbra saturation boost from Mona Lisa multispectral data")
    print("=" * 64)

    ref = build_reference(W, H)
    ref.save("mona_lisa_s178_reference.png")
    print(f"  Reference saved -> mona_lisa_s178_reference.png  ({W}x{H})")

    leo = get_style("leonardo")
    p = Painter(W, H)

    print("  [1/26] Tone ground ...")
    p.tone_ground(leo.ground_color, texture_strength=0.06)

    print("  [2/26] Underpainting ...")
    p.underpainting(ref, stroke_size=52, n_strokes=160)

    print("  [3/26] Block-in ...")
    p.block_in(ref, stroke_size=34, n_strokes=340)

    print("  [4/26] Build form ...")
    p.build_form(ref, stroke_size=10, n_strokes=1400)

    print("  [5/26] Sfumato veil pass (with s178 penumbra_chroma_bloom) ...")
    p.sfumato_veil_pass(
        ref,
        n_veils                     = 10,
        blur_radius                 = 14.0,
        warmth                      = 0.36,
        veil_opacity                = 0.07,
        edge_only                   = True,
        chroma_dampen               = 0.22,
        depth_gradient              = 0.45,
        shadow_warm_recovery        = 0.15,
        highlight_ivory_lift        = 0.06,
        atmospheric_blue_shift      = 0.35,
        penumbra_bloom              = 0.07,
        highlight_sharpness_recovery= 0.10,
        highlight_sharpness_thresh  = 0.75,
        highlight_sharpness_sigma   = 1.2,
        penumbra_chroma_bloom       = 0.18,
        penumbra_chroma_lo          = 0.28,
        penumbra_chroma_hi          = 0.52,
    )

    print("  [6/26] Edge sfumato dissolution pass ...")
    p.edge_sfumato_dissolution_pass(
        grad_threshold = 0.10,
        blur_sigma     = 6.0,
        edge_strength  = 0.38,
        opacity        = 0.30,
    )

    print("  [7/26] Figure contour atmosphere pass ...")
    p.figure_contour_atmosphere_pass(
        blur_sigma      = 6.0,
        bleed_strength  = 0.28,
        edge_threshold  = 0.05,
        luma_lo         = 0.06,
        luma_hi         = 0.92,
        opacity         = 0.42,
    )

    print("  [8/26] Skin subsurface scatter pass ...")
    p.skin_subsurface_scatter_pass(
        scatter_sigma    = 5.0,
        scatter_strength = 0.20,
        amber_r          = 0.05,
        amber_b          = -0.03,
        opacity          = 0.26,
    )

    print("  [9/26] Tonal envelope pass ...")
    p.tonal_envelope_pass(
        center_x      = 0.492,
        center_y      = 0.31,
        radius        = 0.48,
        lift_strength = 0.09,
        lift_warmth   = 0.34,
        edge_darken   = 0.07,
        gamma         = 1.9,
    )

    print("  [10/26] Selective focus pass ...")
    p.selective_focus_pass(
        center_x        = 0.492,
        center_y        = 0.28,
        focus_radius    = 0.34,
        max_blur_radius = 2.8,
        desaturation    = 0.10,
        gamma           = 2.2,
    )

    print("  [11/26] Massys bridge glazing pass ...")
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

    print("  [12/26] Reynolds Grand Manner mezzotint tone pass ...")
    p.reynolds_grand_manner_pass(
        amber_strength  = 0.05,
        amber_r         = 0.07,
        amber_g         = 0.03,
        amber_b_reduce  = 0.05,
        highlight_lo    = 0.70,
        highlight_power = 1.5,
        hi_boost        = 0.03,
        shadow_hi       = 0.30,
        shadow_power    = 1.5,
        shadow_deepen_r = 0.10,
        shadow_deepen_g = 0.08,
        shadow_deepen_b = 0.06,
        opacity         = 0.20,
    )

    print("  [13/26] Schedoni luminous emergence pass ...")
    p.schedoni_luminous_emergence_pass(
        shadow_hi      = 0.28,
        shad_power     = 1.8,
        compress       = 0.20,
        highlight_lo   = 0.62,
        hi_power       = 1.4,
        chroma_boost   = 0.28,
        glow_r         = 0.025,
        glow_g         = 0.015,
        opacity        = 0.26,
    )

    print("  [14/26] Warm highlight bloom pass ...")
    p.warm_highlight_bloom_pass(
        warm_r_thresh  = 0.58,
        warm_r_ratio   = 1.04,
        luma_thresh    = 0.56,
        bloom_sigma    = 14.0,
        bloom_strength = 0.12,
        bloom_r        = 0.82,
        bloom_g        = 0.64,
        bloom_b        = 0.32,
        opacity        = 0.18,
    )

    print("  [15/26] Shadow color temperature pass ...")
    p.shadow_color_temperature_pass(
        shadow_thresh    = 0.42,
        shadow_power     = 1.4,
        cool_b           = 0.035,
        cool_r           = 0.012,
        cool_g           = 0.005,
        highlight_thresh = 0.62,
        highlight_power  = 1.3,
        warm_r           = 0.028,
        warm_g           = 0.012,
        opacity          = 0.24,
    )

    print("  [16/26] Film grain overlay pass ...")
    p.film_grain_overlay_pass(
        grain_sigma    = 0.022,
        grain_gamma    = 0.72,
        grain_strength = 0.85,
        opacity        = 0.50,
        seed           = 178,
    )

    print("  [17/26] Van der Werff ivory alabaster pass ...")
    p.van_der_werff_ivory_alabaster_pass(
        skin_r_lo       = 0.44,
        skin_r_hi       = 1.00,
        skin_g_lo       = 0.24,
        skin_g_hi       = 0.80,
        skin_b_lo       = 0.12,
        skin_b_hi       = 0.60,
        skin_rg_margin  = 0.06,
        hi_lo           = 0.54,
        ivory_b_lift    = 0.08,
        ivory_r_reduce  = 0.04,
        shadow_hi       = 0.46,
        shadow_b_lift   = 0.06,
        shadow_r_reduce = 0.05,
        opacity         = 0.36,
    )

    print("  [18/26] Craquelure texture pass ...")
    p.craquelure_texture_pass(
        sigma_fine      = 1.2,
        sigma_coarse    = 5.0,
        crack_threshold = 0.58,
        crack_depth     = 0.14,
        opacity         = 0.48,
        seed            = 178,
    )

    print("  [19/26] Clouet enamel precision pass ...")
    p.clouet_enamel_precision_pass(
        cool_r        = 0.90,
        cool_g        = 0.88,
        cool_b        = 0.94,
        tint_strength = 0.16,
        hi_threshold  = 0.40,
        hi_gate_power = 1.6,
        opacity       = 0.38,
    )

    print("  [20/26] Altdorfer forest atmosphere pass ...")
    p.altdorfer_forest_atmosphere_pass(
        sky_band_hi    = 0.28,
        earth_band_lo  = 0.72,
        sky_cool_b     = 0.048,
        sky_cool_r     = 0.018,
        sky_cool_g     = 0.006,
        sky_luma_lo    = 0.32,
        forest_cool_b  = 0.035,
        forest_warm_g  = 0.014,
        forest_cool_r  = 0.022,
        forest_luma_lo = 0.16,
        forest_luma_hi = 0.70,
        earth_warm_r   = 0.038,
        earth_warm_g   = 0.014,
        earth_luma_hi  = 0.52,
        opacity        = 0.40,
    )

    print("  [21/26] Luminance gradient warmth pass ...")
    p.luminance_gradient_warmth_pass(
        warm_r     = 0.042,
        warm_g     = 0.016,
        grad_gamma = 1.6,
        grad_sigma = 2.0,
        luma_lo    = 0.14,
        luma_hi    = 0.80,
        opacity    = 0.36,
    )

    print("  [22/26] Multi-layer atmospheric veil pass ...")
    p.multilayer_atmospheric_veil_pass(opacity=0.35)

    print("  [23/26] Doggiono Leonardesque warmth pass ...")
    p.doggiono_leonardesque_warmth_pass(opacity=0.28)

    print("  [24/26] Boucher pastel radiance pass ...")
    p.boucher_pastel_radiance_pass(
        flesh_lo       = 0.44,
        flesh_hi       = 0.72,
        flesh_r        = 0.018,
        flesh_g        = 0.010,
        flesh_b_reduce = 0.014,
        sky_band       = 0.32,
        sky_cool_b     = 0.028,
        sky_cool_g     = 0.006,
        sky_cool_r     = 0.010,
        sat_boost      = 0.10,
        sat_gate_lo    = 0.32,
        sat_gate_hi    = 0.78,
        opacity        = 0.30,
    )

    print("  [25/26] Brouwer tavern glow pass -- SEVENTY-FOURTH DISTINCT MODE ...")
    # Applied at moderate opacity so Brouwer's tobacco amber enriches the
    # Leonardesque sfumato palette: the mid-tones gain warmth and vitality,
    # the shadow void acquires smoky muting, and the highlights flash with
    # candlelight warmth.  Complements rather than conflicts with Boucher's
    # peach-cream (which targets lighter flesh) by working in the darker mid-
    # tone zone where Brouwer's tavern palette lives.
    p.brouwer_tavern_glow_pass(
        amber_lo       = 0.28,
        amber_hi       = 0.60,
        amber_r        = 0.022,
        amber_g        = 0.008,
        amber_b_reduce = 0.014,
        smoke_hi       = 0.28,
        smoke_desat    = 0.06,
        accent_lo      = 0.58,
        accent_r       = 0.014,
        accent_g       = 0.006,
        opacity        = 0.34,
    )

    print("  [26/26] Place lights, final glaze + finish ...")
    p.place_lights(ref, stroke_size=5, n_strokes=320)
    p.glaze((0.70, 0.50, 0.20), opacity=0.048)
    p.finish(vignette=0.28, crackle=True)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Painting saved -> {output_path}  ({W}x{H})")
    print("=" * 64)
    return output_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "mona_lisa_s178.png"
    paint(out)
