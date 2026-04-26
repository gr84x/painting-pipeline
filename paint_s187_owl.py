"""
paint_s187_owl.py — Original composition: "The Watcher at Dusk"

Session 187 painting — inspired by Lovis Corinth (1858–1925).

IMAGE DESCRIPTION
=================
Subject & Composition:
  A solitary great horned owl perched on a snow-laden pine bough, viewed from
  slightly below and to the right — a low three-quarter angle that lends the bird
  quiet monumentality.  The owl faces slightly left, amber eyes catching pale
  diffuse winter light, head tilted at a precise degree of attentive stillness.
  Emotionally: alert, composed, watchful — absolute predatory patience.

The Figure:
  The owl is large, occupying roughly the upper 55% of the frame vertically.
  Feathers ruffled against deep cold; ear tufts fully erect.  Pale facial disc
  surrounds amber-gold irises against near-black pupils.  White bib visible
  below the bill.  The barred warm tawny-brown plumage carries directional
  feather-tract detail across shoulders and crown.  Massive grey-brown talons
  grip frost-rimed bark with visible tension.  The pine bough bends slightly
  under accumulated snow.

The Environment:
  Deep boreal forest, late-winter twilight.  Background: dark blue-grey vertical
  spruce columns receding into violet-purple distance shadow — partially veiled
  by falling snow.  A pale lemon-amber light source (low winter sun, off-frame
  right) strikes the owl's right shoulder, the facial disc, and the snow mounded
  on the bough.  Foreground: the primary bough fills the lower third; scattered
  pine needles protrude through the snow; a few snowflakes catch the amber light
  as luminous points.  The air between the trees carries a cold, heavy silence —
  the blue-grey void has spatial depth and weight.

Technique & Palette:
  Lovis Corinth's directional impasto — vigorous angled brushwork with
  momentum and tonal contrast.  The corinth_stroke_velocity_field_pass enhances
  visible edge energy at tonal transitions (feather-barring, branch bark, snow
  mound edges).  Dark warm ground glows through, Rembrandtesque.
  Palette:
    Amber-gold lit feathers:   (0.84, 0.68, 0.36)
    Warm tawny-brown body:     (0.56, 0.40, 0.22)
    Cool blue-grey shadow:     (0.40, 0.46, 0.58)
    Deep violet-black voids:   (0.10, 0.08, 0.16)
    Ivory-white facial disc:   (0.92, 0.88, 0.80)
    Snow and bib highlights:   (0.96, 0.93, 0.88)
    Pine bough sage-dark:      (0.22, 0.28, 0.18)

Mood & Intent:
  Silent power.  The image is built to deliver the absolute stillness of a deep
  winter forest — a held breath in cold darkness — with the owl as its sovereign.
  The viewer should feel quiet awe and the strange comfort of watchful patience.
  There is no narrative, no threat — only presence, precision, and wild dignity.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter
from art_catalog import get_style

W, H = 540, 780


def build_owl_reference(w: int, h: int) -> Image.Image:
    """
    Synthetic reference for owl-on-bough composition.
    Low-angle view; owl upper-centre; dark boreal background; lit from right.
    """
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None] * np.ones((1, w), dtype=np.float32)
    xx = np.ones((h, 1), dtype=np.float32) * np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :]

    def _blend(base, colour, alpha):
        a = alpha[:, :, None]
        return base * (1.0 - a) + colour[None, None, :] * a

    # ── Background: boreal dusk forest ───────────────────────────────────────
    sky_top  = np.array([0.28, 0.28, 0.38], dtype=np.float32)   # deep violet-grey sky
    sky_mid  = np.array([0.38, 0.36, 0.48], dtype=np.float32)   # blue-purple treeline
    sky_warm = np.array([0.56, 0.44, 0.28], dtype=np.float32)   # amber-gold horizon glow right

    t_top  = np.clip(1.0 - yy * 3.0, 0.0, 1.0)
    t_base = np.clip(yy * 2.5 - 0.5, 0.0, 1.0)
    t_mid  = np.clip(1.0 - t_top - t_base, 0.0, 1.0)

    arr = (sky_top[None, None, :] * t_top[:, :, None]
         + sky_mid[None, None, :] * t_mid[:, :, None]
         + sky_mid[None, None, :] * t_base[:, :, None])

    # Amber horizon glow — off-frame right
    glow_x  = np.clip((xx - 0.55) / 0.50, 0.0, 1.0)
    glow_y  = np.clip(1.0 - yy * 2.5, 0.0, 1.0)
    glow    = (glow_x * glow_y * 0.55).astype(np.float32)
    arr = _blend(arr, sky_warm, glow)

    # Spruce trunk columns — dark verticals receding left
    for tx in [0.12, 0.22, 0.72, 0.82, 0.92]:
        trunk_d = np.abs(xx - tx) / 0.018
        trunk_alpha = np.clip(1.0 - trunk_d, 0.0, 1.0) * 0.72
        arr = _blend(arr, np.array([0.06, 0.07, 0.10], dtype=np.float32), trunk_alpha)

    # Mid-distance tree masses — soft purple-grey
    for mx, mw in [(0.18, 0.14), (0.35, 0.10), (0.65, 0.12), (0.88, 0.10)]:
        md = np.abs(xx - mx) / mw
        mass_a = np.clip(1.0 - md, 0.0, 1.0) * 0.38 * np.clip(yy * 3.0, 0.0, 1.0)
        arr = _blend(arr, np.array([0.14, 0.12, 0.20], dtype=np.float32), mass_a)

    arr = np.clip(arr, 0.0, 1.0)

    # ── Snowflakes — scattered luminous points ────────────────────────────────
    rng = np.random.default_rng(42)
    for _ in range(55):
        sx = rng.uniform(0.05, 0.95)
        sy = rng.uniform(0.0, 0.82)
        sf_d = ((xx - sx) / 0.006)**2 + ((yy - sy) / 0.006)**2
        sf_a = np.clip(1.0 - sf_d, 0.0, 1.0) ** 2 * 0.60
        arr = _blend(arr, np.array([0.92, 0.88, 0.80], dtype=np.float32), sf_a)

    # ── Pine bough — diagonal lower third ────────────────────────────────────
    bough_y_at_x = 0.68 + (xx - 0.50) * 0.05   # very slight downward slope right→left
    bough_d = np.abs(yy - bough_y_at_x) / 0.048
    bough_alpha = np.clip(1.0 - bough_d, 0.0, 1.0) ** 1.2
    bark = np.array([0.22, 0.18, 0.13], dtype=np.float32)
    arr = _blend(arr, bark, bough_alpha * 0.90)

    # Snow on bough upper surface
    snow_d = np.abs(yy - (bough_y_at_x - 0.022)) / 0.022
    snow_above = (yy < bough_y_at_x).astype(np.float32)
    snow_a = np.clip(1.0 - snow_d, 0.0, 1.0) ** 1.5 * snow_above * 0.82
    arr = _blend(arr, np.array([0.94, 0.92, 0.88], dtype=np.float32), snow_a)

    # Lit upper bough face from amber-right
    lit_bough = snow_a * np.clip((xx - 0.35) / 0.60, 0.0, 1.0)
    arr = _blend(arr, np.array([0.88, 0.74, 0.46], dtype=np.float32), lit_bough * 0.40)

    # Pine needle suggestions — dark thin protrusions below bough
    for nx in np.arange(0.08, 0.92, 0.07):
        nd_x = np.abs(xx - nx) / 0.010
        nd_y = np.clip((yy - bough_y_at_x) / 0.06, 0.0, 1.0)
        needle_a = np.clip(1.0 - nd_x, 0.0, 1.0) * nd_y * 0.45
        arr = _blend(arr, np.array([0.18, 0.24, 0.15], dtype=np.float32), needle_a.astype(np.float32))

    arr = np.clip(arr, 0.0, 1.0)

    # ── Owl body — upper centre, viewed from slightly below ───────────────────
    owl_cx, owl_cy = 0.500, 0.390    # body centre (slightly right of absolute centre)
    owl_rx, owl_ry = 0.175, 0.260    # body ellipse

    ox = (xx - owl_cx) / owl_rx
    oy = (yy - owl_cy) / owl_ry
    owl_d = ox**2 + oy**2

    # Base tawny-brown body
    body_col = np.array([0.52, 0.38, 0.20], dtype=np.float32)
    body_a = np.clip(1.40 - owl_d, 0.0, 1.0) ** 0.60
    arr = _blend(arr, body_col, body_a)

    # Feather barring — horizontal dark bands
    for bar_cy in np.arange(-0.55, 0.80, 0.18):
        bar_y = owl_cy + bar_cy * owl_ry
        bar_d = np.abs(yy - bar_y) / 0.012
        in_body = (owl_d < 1.20).astype(np.float32)
        bar_a = np.clip(1.0 - bar_d, 0.0, 1.0) ** 1.5 * in_body * 0.28
        arr = _blend(arr, np.array([0.28, 0.20, 0.10], dtype=np.float32), bar_a)

    # Warm amber-gold lit side — right shoulder/flank
    lit_d = ((ox + 0.50)**2 + (oy + 0.10)**2)
    lit_a = np.clip(1.30 - lit_d, 0.0, 1.0) ** 1.5 * body_a * 0.70
    arr = _blend(arr, np.array([0.82, 0.66, 0.34], dtype=np.float32), lit_a)

    # Cool shadow left flank
    shad_d = ((-ox + 0.40)**2 + (oy - 0.10)**2)
    shad_a = np.clip(1.10 - shad_d, 0.0, 1.0) ** 2.0 * body_a * 0.55
    arr = _blend(arr, np.array([0.32, 0.30, 0.40], dtype=np.float32), shad_a)

    # ── Head ─────────────────────────────────────────────────────────────────
    head_cx, head_cy = 0.496, 0.195
    head_rx, head_ry = 0.115, 0.128
    hx = (xx - head_cx) / head_rx
    hy = (yy - head_cy) / head_ry
    head_d = hx**2 + hy**2

    head_col = np.array([0.48, 0.36, 0.18], dtype=np.float32)
    head_a = np.clip(1.38 - head_d, 0.0, 1.0) ** 0.55
    arr = _blend(arr, head_col, head_a)

    # Crown barring
    crown_bar_d = np.abs(hy + 0.45) / 0.08
    crown_in_head = (head_d < 1.10).astype(np.float32)
    crown_a = np.clip(1.0 - crown_bar_d, 0.0, 1.0) * crown_in_head * 0.30
    arr = _blend(arr, np.array([0.22, 0.16, 0.08], dtype=np.float32), crown_a)

    # Ear tufts — two dark vertical projections
    for tuft_ox in [-0.65, 0.55]:
        tuft_cx = head_cx + tuft_ox * head_rx
        tuft_base_y = head_cy - head_ry * 0.88
        tuft_x_d = np.abs(xx - tuft_cx) / 0.014
        tuft_y_d = np.clip((tuft_base_y - yy) / 0.055, 0.0, 1.0)
        tuft_a = np.clip(1.0 - tuft_x_d, 0.0, 1.0) ** 1.5 * tuft_y_d * 0.85
        arr = _blend(arr, np.array([0.18, 0.14, 0.08], dtype=np.float32), tuft_a.astype(np.float32))

    # Facial disc — pale ivory ellipse
    disc_d = (hx**2 * 0.85 + hy**2)
    disc_a = np.clip(0.68 - disc_d, 0.0, 1.0) ** 0.55 * head_a
    arr = _blend(arr, np.array([0.90, 0.86, 0.78], dtype=np.float32), disc_a)

    # Disc rim — dark border
    disc_rim_d = np.abs(disc_d ** 0.5 - 0.82) / 0.12
    disc_rim_a = np.clip(1.0 - disc_rim_d, 0.0, 1.0) * head_a * 0.45
    arr = _blend(arr, np.array([0.18, 0.14, 0.10], dtype=np.float32), disc_rim_a)

    # Lit right side of head from amber source
    head_lit_d = ((hx + 0.55)**2 + (hy + 0.15)**2)
    head_lit_a = np.clip(1.10 - head_lit_d, 0.0, 1.0) ** 2.0 * head_a * 0.62
    arr = _blend(arr, np.array([0.88, 0.72, 0.46], dtype=np.float32), head_lit_a)

    # Eyes — amber irises with dark pupils
    for eye_ox, eye_oy in [(-0.32, -0.12), (0.32, -0.12)]:
        eye_cx = head_cx + eye_ox * head_rx
        eye_cy = head_cy + eye_oy * head_ry
        eye_d = ((xx - eye_cx) / 0.022)**2 + ((yy - eye_cy) / 0.022)**2
        iris_a = np.clip(1.0 - eye_d, 0.0, 1.0) ** 1.2
        arr = _blend(arr, np.array([0.82, 0.60, 0.12], dtype=np.float32), iris_a)
        pupil_d = ((xx - eye_cx) / 0.012)**2 + ((yy - eye_cy) / 0.012)**2
        pupil_a = np.clip(1.0 - pupil_d, 0.0, 1.0) ** 2.0
        arr = _blend(arr, np.array([0.04, 0.04, 0.06], dtype=np.float32), pupil_a)
        # Eye catchlight
        hl_d = ((xx - (eye_cx + 0.008)) / 0.006)**2 + ((yy - (eye_cy - 0.006)) / 0.006)**2
        hl_a = np.clip(1.0 - hl_d, 0.0, 1.0) ** 2 * 0.85
        arr = _blend(arr, np.array([0.95, 0.92, 0.88], dtype=np.float32), hl_a)

    # Bill — pale grey-ivory curved shape
    bill_d = ((xx - head_cx) / 0.030)**2 + ((yy - (head_cy + head_ry * 0.16)) / 0.025)**2
    bill_a = np.clip(1.0 - bill_d, 0.0, 1.0) ** 1.5 * 0.72
    arr = _blend(arr, np.array([0.76, 0.72, 0.62], dtype=np.float32), bill_a)

    # White bib — below bill
    bib_d = ((xx - head_cx) / 0.085)**2 + ((yy - (head_cy + head_ry * 0.55)) / 0.040)**2
    bib_a = np.clip(0.90 - bib_d, 0.0, 1.0) ** 1.2 * body_a * 0.82
    arr = _blend(arr, np.array([0.94, 0.92, 0.86], dtype=np.float32), bib_a)

    # ── Talons gripping bough ─────────────────────────────────────────────────
    for talon_ox in [-0.08, 0.06]:
        talon_cx = owl_cx + talon_ox
        talon_y  = owl_cy + owl_ry * 0.98
        talon_d  = ((xx - talon_cx) / 0.032)**2 + ((yy - talon_y) / 0.028)**2
        talon_a  = np.clip(1.0 - talon_d, 0.0, 1.0) ** 1.2 * 0.78
        arr = _blend(arr, np.array([0.45, 0.38, 0.28], dtype=np.float32), talon_a)

    arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(4))
    return img


def paint(output_path: str = "s187_owl.png") -> str:
    """
    Paint 'The Watcher at Dusk' — great horned owl in boreal winter twilight.
    Lovis Corinth directional impasto with 94th mode corinth_stroke_velocity_field_pass.
    """
    print("=" * 64)
    print("  Session 187 — 'The Watcher at Dusk'")
    print("  Great horned owl, boreal forest, winter twilight")
    print("  Technique: Lovis Corinth directional impasto")
    print("  94th mode: corinth_stroke_velocity_field_pass")
    print("=" * 64)

    ref = build_owl_reference(W, H)
    print(f"  Reference built  ({W}x{H})")

    corinth = get_style("lovis_corinth")
    p = Painter(W, H)

    print("  [1/22] Tone ground — warm dark Corinthian brown ...")
    p.tone_ground(corinth.ground_color, texture_strength=0.08)

    print("  [2/22] Underpainting ...")
    p.underpainting(ref, stroke_size=58, n_strokes=140)

    print("  [3/22] Block-in ...")
    p.block_in(ref, stroke_size=36, n_strokes=300)

    print("  [4/22] Build form ...")
    p.build_form(ref, stroke_size=12, n_strokes=1200)

    print("  [5/22] Shadow color temperature — cool shadows, warm lights ...")
    p.shadow_color_temperature_pass(
        shadow_thresh     = 0.36,
        cool_b            = 0.045,
        cool_r            = 0.018,
        highlight_thresh  = 0.65,
        warm_r            = 0.032,
        warm_g            = 0.016,
        opacity           = 0.26,
    )

    print("  [6/22] Tonal envelope — amber-gold right source ...")
    p.tonal_envelope_pass(
        center_x      = 0.60,
        center_y      = 0.25,
        radius        = 0.52,
        lift_strength = 0.10,
        lift_warmth   = 0.40,
        edge_darken   = 0.08,
        gamma         = 1.8,
    )

    print("  [7/22] Warm ambient occlusion — deepen recesses ...")
    p.warm_ambient_occlusion_pass(
        occ_radius  = 14.0,
        shad_lo     = 0.08,
        shad_hi     = 0.38,
        warm_r      = 0.04,
        warm_g      = 0.018,
        opacity     = 0.30,
    )

    print("  [8/22] Skin subsurface scatter — feather warmth ...")
    p.skin_subsurface_scatter_pass(
        scatter_sigma    = 4.5,
        scatter_strength = 0.18,
        amber_r          = 0.04,
        amber_b          = -0.025,
        opacity          = 0.24,
    )

    print("  [9/22] Chromatic vignette — deepen forest void ...")
    p.chromatic_vignette_pass(
        radius          = 0.68,
        darken_strength = 0.22,
        cool_b          = 0.055,
        cool_r_reduce   = 0.025,
        vig_gamma       = 1.8,
        luma_lo         = 0.06,
        opacity         = 0.36,
    )

    print("  [10/22] Peripheral defocus — isolate owl in sharp focus ...")
    p.peripheral_defocus_pass(
        inner_radius  = 0.32,
        blur_sigma    = 5.0,
        power         = 2.2,
        blur_strength = 0.52,
        opacity       = 0.34,
    )

    print("  [11/22] Selective focus — crisp eyes and bib ...")
    p.selective_focus_pass(
        center_x        = 0.496,
        center_y        = 0.195,
        focus_radius    = 0.28,
        max_blur_radius = 3.5,
        desaturation    = 0.12,
        gamma           = 2.0,
    )

    print("  [12/22] Ceruti dignity shadow pass — dignify the deep voids ...")
    p.ceruti_dignity_shadow_pass(
        shadow_lo    = 0.06,
        shadow_hi    = 0.38,
        warm_r_delta = 0.014,
        warm_g_delta = 0.008,
        opacity      = 0.28,
    )

    print("  [13/22] Fra Galgario living surface — feather inner luminescence ...")
    p.fra_galgario_living_surface_pass(
        glow_lo     = 0.32,
        glow_hi     = 0.76,
        luma_peak   = 0.54,
        half_width  = 0.22,
        glow_r_lift = 0.020,
        glow_g_lift = 0.010,
        opacity     = 0.26,
    )

    print("  [14/22] Chromatic temperature field — Corinth warm/cool opposition ...")
    p.chromatic_temperature_field_pass(
        warm_strength    = 0.028,
        cool_strength    = 0.022,
        warm_luma_lo     = 0.60,
        cool_luma_hi     = 0.32,
        transition_width = 0.25,
        opacity          = 0.30,
    )

    print("  [15/22] Luminance preserving chroma boost — saturate feathers ...")
    p.luminance_preserving_chroma_boost_pass(
        boost         = 0.14,
        luma_lo       = 0.15,
        luma_hi       = 0.80,
        opacity       = 0.24,
    )

    print("  [16/22] Multilayer atmospheric veil — forest air depth ...")
    p.multilayer_atmospheric_veil_pass(
        sigma_fine    = 1.2,
        sigma_medium  = 4.5,
        sigma_coarse  = 12.0,
        weight_fine   = 0.38,
        weight_medium = 0.34,
        weight_coarse = 0.28,
        edge_thresh   = 0.05,
        opacity       = 0.26,
    )

    print("  [17/22] Local statistical harmony — regional colour coherence ...")
    p.local_statistical_harmony_pass(
        sigma            = 12.0,
        harmony_strength = 0.12,
        luma_lo          = 0.10,
        luma_hi          = 0.86,
        opacity          = 0.22,
    )

    print("  [18/22] *** CORINTH STROKE VELOCITY FIELD PASS [94th mode] ***")
    p.corinth_stroke_velocity_field_pass(
        detail_sigma_fine   = 1.0,
        detail_sigma_coarse = 3.8,
        sharpen_strength    = 0.32,
        mag_gate_thresh     = 0.035,
        luma_lo             = 0.08,
        luma_hi             = 0.92,
        opacity             = 0.32,
    )

    print("  [19/22] Chromatic edge halation — feather-tip glow ...")
    p.chromatic_edge_halation_pass(
        grad_threshold  = 0.05,
        bloom_sigma     = 3.5,
        bleed_strength  = 0.16,
        luma_lo         = 0.20,
        luma_hi         = 0.88,
        opacity         = 0.22,
    )

    print("  [20/22] Shadow chroma depth — deepen purple-blue background ...")
    p.shadow_chroma_depth_pass(
        shadow_lo    = 0.10,
        shadow_hi    = 0.40,
        amplify      = 0.22,
        highlight_lo = 0.78,
        reduce       = 0.14,
        opacity      = 0.22,
    )

    print("  [21/22] Place lights — snow catchlights, eye specular ...")
    p.place_lights(ref, stroke_size=4, n_strokes=280)

    print("  [22/22] Final amber glaze + finish ...")
    # Warm amber-brown final unifier — Corinth's golden ground quality
    p.glaze((0.60, 0.46, 0.26), opacity=0.038)
    p.finish(vignette=0.30, crackle=False)

    result = p.canvas.to_pil()
    result.save(output_path)
    print(f"\n  Painting saved -> {output_path}  ({W}x{H})")
    print("=" * 64)
    return output_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "s187_owl.png"
    paint(out)
