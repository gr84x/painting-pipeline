"""
paint_mona_lisa_s169.py — Mona Lisa portrait for session 169.

Subject: enigmatic half-length female figure, three-quarter pose, sfumato
technique, dreamlike geological landscape background, dark veil, dark dress,
folded hands — the full Renaissance portrait prompt.

Artistic discovery (session 169): Albrecht Altdorfer (c. 1480–1538)
  - Founder of the Danube School (Donauschule); Germany's greatest
    landscape painter before Romanticism codified that impulse
  - First European artist to paint pure landscapes — no figures at all —
    treating the natural world as an autonomous subject
  - Atmospheric vertical layering: sky (cool silver-blue), mid-distance
    forest (deep blue-green), earth (warm amber-umber) — each zone
    with its own chromatic identity
  - Famous for twilight and nocturne effects: 'Nativity at Night' (c.1520),
    one of the first true night paintings in Western art
  - His masterpiece 'The Battle of Alexander at Issus' (1529) subordinates
    thousands of soldiers to a vast apocalyptic sky — figures lost in cosmos
  - Painted on lime-wood with white chalk gesso; vivid glazed colour

New pipeline enhancement (session 169):
  - altdorfer_forest_atmosphere_pass: FIFTY-NINTH DISTINCT MODE
    LUMINANCE-STRATIFIED VERTICAL ATMOSPHERIC DEPTH LAYERING:
    (1) Sky band (upper, y_norm < sky_band_hi): cool silver-blue shift in
        highlights — cool_b+, cool_r−, cool_g−, gated by luma floor
    (2) Forest/mid-distance band (sky_band_hi ≤ y_norm ≤ earth_band_lo):
        deep blue-green shift in mid-tones — forest_b+, forest_g+, forest_r−
    (3) Earth/shadow band (lower, y_norm > earth_band_lo): warm amber-umber
        in shadows — earth_r+, earth_g+, gated by luma ceiling
    — FIRST and ONLY pass to segment the canvas into THREE INDEPENDENT
    HORIZONTAL Y-COORDINATE BANDS each with its OWN chromatic temperature
    shift and its OWN luminance gate.

  - vibrance_selective_pass: SIXTIETH DISTINCT MODE
    SATURATION-INVERSE SELECTIVE CHROMA AMPLIFICATION (random improvement):
    (1) Per-pixel HSV saturation: S = (max(r,g,b) − min(r,g,b)) / (max+ε)
    (2) Vibrance gate: vib_gate = (1 − S)^gamma — peaks for dull/grey pixels
    (3) Luminance gate: protects extreme shadows and specular peaks
    (4) Chroma amplification: neutral-mean decomposition (n=(r+g+b)/3),
        out = n + delta × (1 + vibrance_strength × vib_gate × luma_gate)
    — FIRST and ONLY pass to gate chroma boost on the INVERSE of existing
    saturation — preferentially lifts muted pixels while protecting vivid ones.
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


def paint(output_path: str = "mona_lisa_s169.png") -> str:
    """Full Leonardo sfumato pipeline with session 169 Altdorfer atmospheric passes."""
    print("=" * 64)
    print("  Session 169 — Mona Lisa sfumato portrait")
    print("  Artistic discovery: Albrecht Altdorfer (c. 1480–1538)")
    print("    Danube School — atmospheric vertical depth layering")
    print("    FIFTY-NINTH MODE: altdorfer_forest_atmosphere_pass")
    print("    — three-band Y-stratified chromatic depth layering")
    print("    SIXTIETH MODE: vibrance_selective_pass")
    print("    — saturation-inverse selective chroma boost")
    print("=" * 64)

    ref = build_reference(W, H)
    ref.save("mona_lisa_s169_reference.png")
    print(f"  Reference saved -> mona_lisa_s169_reference.png  ({W}x{H})")

    leo = get_style("leonardo")
    p = Painter(W, H)

    print("  [1/22] Tone ground ...")
    p.tone_ground(leo.ground_color, texture_strength=0.06)

    print("  [2/22] Underpainting ...")
    p.underpainting(ref, stroke_size=52, n_strokes=160)

    print("  [3/22] Block-in ...")
    p.block_in(ref, stroke_size=34, n_strokes=340)

    print("  [4/22] Build form ...")
    p.build_form(ref, stroke_size=10, n_strokes=1400)

    print("  [5/22] Sfumato veil pass ...")
    p.sfumato_veil_pass(
        ref,
        n_veils       = 10,
        blur_radius   = 14.0,
        warmth        = 0.36,
        veil_opacity  = 0.07,
        edge_only     = True,
        chroma_dampen = 0.22,
    )

    print("  [6/22] Edge sfumato dissolution pass ...")
    p.edge_sfumato_dissolution_pass(
        grad_threshold = 0.10,
        blur_sigma     = 6.0,
        edge_strength  = 0.38,
        opacity        = 0.30,
    )

    print("  [7/22] Skin subsurface scatter pass ...")
    p.skin_subsurface_scatter_pass(
        scatter_sigma    = 5.0,
        scatter_strength = 0.20,
        warm_boost       = 1.04,
        cool_damp        = 0.97,
        opacity          = 0.26,
    )

    print("  [8/22] Tonal envelope pass ...")
    p.tonal_envelope_pass(
        center_x      = 0.492,
        center_y      = 0.31,
        radius        = 0.48,
        lift_strength = 0.09,
        lift_warmth   = 0.34,
        edge_darken   = 0.07,
        gamma         = 1.9,
    )

    print("  [9/22] Selective focus pass ...")
    p.selective_focus_pass(
        center_x        = 0.492,
        center_y        = 0.28,
        focus_radius    = 0.34,
        max_blur_radius = 2.8,
        desaturation    = 0.10,
        gamma           = 2.2,
    )

    print("  [10/22] Massys bridge glazing pass ...")
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

    print("  [11/22] Reynolds Grand Manner mezzotint tone pass ...")
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

    print("  [12/22] Schedoni luminous emergence pass ...")
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

    print("  [13/22] Warm highlight bloom pass ...")
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

    print("  [14/22] Shadow color temperature pass ...")
    p.shadow_color_temperature_pass(
        shadow_thresh   = 0.42,
        shadow_power    = 1.4,
        cool_b          = 0.035,
        cool_r          = 0.012,
        cool_g          = 0.005,
        highlight_thresh= 0.62,
        highlight_power = 1.3,
        warm_r          = 0.028,
        warm_g          = 0.012,
        opacity         = 0.24,
    )

    print("  [15/22] Film grain overlay pass ...")
    p.film_grain_overlay_pass(
        grain_sigma    = 0.022,
        grain_gamma    = 0.72,
        grain_strength = 0.85,
        opacity        = 0.50,
        seed           = 169,
    )

    print("  [16/22] Van der Werff ivory alabaster pass ...")
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

    print("  [17/22] Craquelure texture pass ...")
    p.craquelure_texture_pass(
        sigma_fine      = 1.2,
        sigma_coarse    = 5.0,
        crack_threshold = 0.58,
        crack_depth     = 0.14,
        opacity         = 0.48,
        seed            = 169,
    )

    print("  [18/22] Clouet enamel precision pass ...")
    p.clouet_enamel_precision_pass(
        cool_r        = 0.90,
        cool_g        = 0.88,
        cool_b        = 0.94,
        tint_strength = 0.16,
        hi_threshold  = 0.40,
        hi_gate_power = 1.6,
        opacity       = 0.38,
    )

    print("  [19/22] Wtewael copper jewel pass ...")
    p.wtewael_copper_jewel_pass(
        saturation_boost = 0.28,
        mid_lo           = 0.28,
        mid_hi           = 0.76,
        mid_power        = 1.6,
        shadow_threshold = 0.20,
        shadow_power     = 2.2,
        copper_r         = 0.045,
        copper_g         = 0.015,
        opacity          = 0.38,
    )

    print("  [20/22] Altdorfer forest atmosphere pass — FIFTY-NINTH DISTINCT MODE ...")
    # Altdorfer's vertical atmospheric depth layering applied to the dreamlike
    # geological background of the Mona Lisa: the upper sky band cools toward
    # pale silver-blue (sfumato aerial perspective), the mid-distance forest
    # band deepens toward blue-green (Altdorfer's dense forest atmosphere),
    # and the lower earth band warms to amber-umber (dark forest floor).
    # Applied at moderate opacity so Leonardo's warm ochre ground is not
    # overwhelmed — the atmospheric layers enrich the landscape without
    # shifting the figure's warm flesh tones.
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
        opacity        = 0.46,
    )

    print("  [21/22] Vibrance selective pass — SIXTIETH DISTINCT MODE ...")
    # Perceptual vibrance: boosts less-saturated (muted) pixels preferentially
    # while leaving already-vivid pixels unchanged.  After all the tonal and
    # colour passes, the muted mid-ground tones may appear slightly washed out;
    # vibrance restores their natural depth without making vivid flesh tones
    # garish.  Applied at moderate strength to preserve the painting's quiet,
    # interior character.
    p.vibrance_selective_pass(
        vibrance_strength = 0.38,
        vibrance_gamma    = 1.5,
        luma_lo           = 0.10,
        luma_hi           = 0.88,
        opacity           = 0.44,
    )

    print("  [22/22] Place lights, final glaze + finish ...")
    p.place_lights(ref, stroke_size=5, n_strokes=320)
    p.glaze((0.70, 0.50, 0.20), opacity=0.048)
    p.finish(vignette=0.28, crackle=True)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Painting saved -> {output_path}  ({W}x{H})")
    print("=" * 64)
    return output_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "mona_lisa_s169.png"
    paint(out)
