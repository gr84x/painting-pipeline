"""
paint_s247_kollwitz_mourning.py — Session 247

"The Weight of the Earth" — after Käthe Kollwitz

Image Description
─────────────────
Subject & Composition
    A lone woman crouched on bare winter earth, seen from a slightly elevated
    three-quarter angle from her left. Her hunched mass occupies the lower-
    centre two-thirds of the canvas. The composition is asymmetric and
    heavy: the figure pulls downward. A single bare branch crosses the upper-
    left quadrant. Behind her, the vast pale sky presses down.

The Figure
    She is broad and heavy-set, her dark shawl pulled tight around shoulders
    curved in grief. Her back is toward us, the nape of her neck and top of
    grey hair just visible beneath the shawl's edge. Her left hand is pressed
    flat against the cold earth, large-knuckled, the palm wide. Her right arm
    curves across her body, hidden in the shawl. The black skirt fans around
    her where she crouches. Her face is buried, absent — Kollwitz never needs
    a face to communicate grief. Emotional state: absolute, wordless mourning,
    the grief that has moved past weeping into something older and heavier.

The Environment
    Bare winter earth — cold, flat, textured with frost and dead grass stubble.
    The tone is dark grey-brown with faint directional texture. The horizon line
    is very low (one-quarter up from bottom), leaving the woman pressed between
    the dark ground and the vast pale sky. The sky is the colour of old paper —
    warm grey-white, flat, no clouds, not luminous, not hopeful. A single bare
    deciduous branch enters from the upper left, its thin dark silhouette an
    angular counterpoint to the rounded, collapsed form below.

Technique & Palette
    Käthe Kollwitz Charcoal Etching mode — session 247, 158th distinct mode.
    Stage 1 WARM CHARCOAL MONOCHROME: desaturation via dual-endpoint ramp maps
    lum=0 toward warm deep-black (14, 10, 7) and lum=1 toward warm paper-white
    (95, 90, 80). Stage 2 SIGMOID TONAL CONTRAST: k=8 sigmoid expands the tonal
    range — the sky brightens toward paper, the shawl deepens toward charcoal
    black. Stage 3 DIRECTIONAL SHADOW GRAIN at 50°: oriented hatching texture in
    the shadow zones simulates charcoal mark-making. Paint Luminance Stretch
    improvement: percentile-anchored tonal normalisation (p2/p98) ensures full
    tonal range.

    Palette: warm deep black · sepia brown · warm grey · pale cream-white ·
    ochre-grey earth · near-black branch silhouette

Mood & Intent
    The image is built from a single emotion: the weight of earth. Kollwitz
    made this image many times — the crouching woman, the pressed hand, the
    absent face. She was not illustrating grief. She was recording its physical
    form: the way grief turns the body toward the ground, the way the hands press
    against the earth as if trying to reach what is buried. The viewer is not
    meant to feel sorrow. They are meant to recognise weight — to feel, in their
    own body, the pull that the figure is feeling. No colour interferes with this.
    No light offers relief. The pale sky is not hope. It is simply the emptiness
    above a person who has lost everything they cared for.

    Paint with patience and practice, like a true artist.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "s247_kollwitz_weight_of_earth.png"
)
W, H = 960, 1120   # portrait — emphasises downward pull, sky above, earth below


def build_reference() -> np.ndarray:
    """
    Synthetic tonal reference for 'The Weight of the Earth'.

    Tonal zones:
      - Sky (upper 65%): pale warm grey-white, slightly warmer near horizon
      - Bare branch: thin dark diagonal, upper-left quadrant
      - Horizon line: slight darkening where earth meets sky
      - Earth ground (lower 35%): dark grey-brown, textured
      - Woman figure: rounded, heavy dark mass in lower-centre
      - Shawl: near-black over shoulders/back
      - Grey hair: slightly lighter than shawl at nape
      - Hands: pale grey-ochre, pressed to earth (left hand visible)
    """
    rng = np.random.default_rng(247)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Sky: pale warm grey-white — paper tone ────────────────────────────────
    horizon_y  = 0.65   # horizon very low — vast sky above
    sky_top_c  = np.array([0.82, 0.79, 0.73])   # pale warm grey at top
    sky_hor_c  = np.array([0.75, 0.72, 0.66])   # slightly warmer near horizon
    sky_frac   = np.clip(ys / horizon_y, 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = sky_top_c[ch] * (1.0 - sky_frac) + sky_hor_c[ch] * sky_frac

    # Faint uneven texture in sky (cloud impression, aged paper)
    sky_noise  = rng.random((H, W)).astype(np.float32) - 0.5
    sky_smooth = gaussian_filter(sky_noise, sigma=28.0) * 0.035
    sky_zone   = np.clip(1.0 - sky_frac, 0.0, 1.0)
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + sky_smooth * sky_zone[:, :, None].squeeze() if False
                                else ref[:, :, ch] + sky_smooth * float(1.0), 0.0, 1.0)

    # ── Earth ground: dark grey-brown, textured ───────────────────────────────
    earth_top_c  = np.array([0.28, 0.24, 0.18])   # dark warm-grey at top of earth
    earth_deep_c = np.array([0.14, 0.11, 0.08])   # near-black deep earth
    earth_frac   = np.clip((ys - horizon_y) / (1.0 - horizon_y + 1e-7), 0.0, 1.0)
    earth_mask   = (ys > horizon_y).astype(np.float32)
    for ch in range(3):
        earth_col = earth_top_c[ch] * (1.0 - earth_frac) + earth_deep_c[ch] * earth_frac
        ref[:, :, ch] = ref[:, :, ch] * (1.0 - earth_mask) + earth_col * earth_mask

    # Earth texture: frost stubble, directional
    earth_noise  = rng.random((H, W)).astype(np.float32) - 0.5
    earth_horiz  = gaussian_filter(earth_noise, sigma=(2.0, 8.0)) * 0.06
    for ch in range(3):
        ref[:, :, ch] = np.clip(
            ref[:, :, ch] + earth_horiz * earth_mask, 0.0, 1.0
        )

    # ── Horizon line: slight darkening at the junction ───────────────────────
    hor_band = np.exp(-0.5 * ((ys - horizon_y) / 0.012) ** 2) * 0.18
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] - hor_band, 0.0, 1.0)

    # ── Woman figure: heavy rounded mass, lower-centre ───────────────────────
    fig_cx    = 0.48   # slightly left of centre
    fig_cy    = 0.80   # low in frame (within earth zone)
    fig_rw    = 0.20   # horizontal radius — broad figure
    fig_rh    = 0.13   # vertical radius — crouched, compact

    fig_dist  = ((xs - fig_cx) / fig_rw) ** 2 + ((ys - fig_cy) / fig_rh) ** 2
    fig_mask  = np.clip(1.0 - fig_dist ** 0.7, 0.0, 1.0)

    # Core of figure: near-black shawl
    shawl_c   = np.array([0.10, 0.08, 0.07])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1.0 - fig_mask) + shawl_c[ch] * fig_mask

    # Shawl centre (upper-back of figure): deepest dark
    shawl_cx  = fig_cx
    shawl_cy  = fig_cy - 0.04
    shawl_dist = ((xs - shawl_cx) / 0.12) ** 2 + ((ys - shawl_cy) / 0.07) ** 2
    shawl_mask = np.clip(1.0 - shawl_dist ** 0.6, 0.0, 1.0) * fig_mask
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] - shawl_mask * 0.08, 0.0, 1.0)

    # Upper edge of figure: slight rim of lighter value where light falls on back
    rim_cy    = fig_cy - fig_rh * 0.7
    rim_band  = np.exp(-0.5 * ((ys - rim_cy) / 0.018) ** 2)
    rim_mask  = rim_band * fig_mask * 0.45
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + rim_mask * 0.18, 0.0, 1.0)

    # Grey hair at nape: small lighter patch at top of figure, centre-left
    hair_cx   = fig_cx - 0.02
    hair_cy   = fig_cy - fig_rh * 0.85
    hair_dist = ((xs - hair_cx) / 0.035) ** 2 + ((ys - hair_cy) / 0.022) ** 2
    hair_mask = np.clip(1.0 - hair_dist ** 1.2, 0.0, 1.0) * fig_mask
    hair_c    = np.array([0.42, 0.38, 0.33])   # warm grey hair
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1.0 - hair_mask) + hair_c[ch] * hair_mask

    # ── Left hand pressed flat on earth: slightly left-forward of figure ──────
    hand_cx   = fig_cx - 0.12
    hand_cy   = fig_cy + 0.06
    hand_rw   = 0.060
    hand_rh   = 0.030
    hand_dist = ((xs - hand_cx) / hand_rw) ** 2 + ((ys - hand_cy) / hand_rh) ** 2
    hand_mask = np.clip(1.0 - hand_dist ** 1.0, 0.0, 1.0)
    hand_c    = np.array([0.50, 0.42, 0.32])   # pale ochre-grey skin, work-worn
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1.0 - hand_mask * 0.80) + hand_c[ch] * hand_mask * 0.80

    # Finger detail: three dark lines across hand
    for fx in [0.015, 0.030, 0.042]:
        fd   = np.abs(xs - (hand_cx + fx)) / 0.004
        fv   = np.where((ys > hand_cy - hand_rh * 0.8) & (ys < hand_cy + hand_rh * 0.8), 1.0, 0.0)
        fm   = np.clip(1.0 - fd ** 2, 0.0, 1.0) * fv * hand_mask
        for ch in range(3):
            ref[:, :, ch] = np.clip(ref[:, :, ch] - fm * 0.14, 0.0, 1.0)

    # ── Skirt spread: dark fabric fanning on the ground around figure ─────────
    skirt_cy  = fig_cy + fig_rh * 0.6
    skirt_dist = ((xs - fig_cx) / 0.28) ** 2 + ((ys - skirt_cy) / 0.07) ** 2
    skirt_mask = np.clip(1.0 - skirt_dist ** 1.2, 0.0, 1.0) * earth_mask
    skirt_c   = np.array([0.12, 0.09, 0.07])   # near-black worn fabric
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1.0 - skirt_mask * 0.70) + skirt_c[ch] * skirt_mask * 0.70

    # ── Bare branch: thin dark diagonal, upper-left ───────────────────────────
    # Branch goes from (0.02, 0.05) to (0.42, 0.45) — upper-left to mid-left
    for seg_t in np.linspace(0.0, 1.0, 240):
        bx = 0.02 + seg_t * 0.40
        by = 0.05 + seg_t * 0.40
        # Main branch — tapers from 0.008 at base to 0.003 at tip
        bw  = 0.008 * (1.0 - seg_t * 0.6)
        bd  = np.sqrt(((xs - bx) / bw) ** 2 + ((ys - by) / (bw * 0.3)) ** 2)
        bm  = np.clip(1.0 - bd ** 1.5, 0.0, 1.0) * float(by < horizon_y)
        bc  = np.array([0.06, 0.05, 0.04])
        for ch in range(3):
            ref[:, :, ch] = ref[:, :, ch] * (1.0 - bm) + bc[ch] * bm

    # Small secondary branch — forks upward from mid-point
    for seg_t in np.linspace(0.0, 1.0, 120):
        bx = 0.24 + seg_t * 0.12
        by = 0.26 - seg_t * 0.12
        bw  = 0.004 * (1.0 - seg_t * 0.5)
        bd  = np.sqrt(((xs - bx) / (bw + 0.001)) ** 2 + ((ys - by) / (bw * 0.3 + 0.001)) ** 2)
        bm  = np.clip(1.0 - bd ** 2.0, 0.0, 1.0) * float(by > 0.0 and by < horizon_y)
        for ch in range(3):
            ref[:, :, ch] = ref[:, :, ch] * (1.0 - bm * 0.80) + 0.06 * bm * 0.80

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'The Weight of the Earth' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=247)

    # Ground: warm cream-grey — the paper that is always visible through charcoal
    p.tone_ground((0.82, 0.78, 0.70), texture_strength=0.025)

    # Underpainting: establish tonal masses — figure, sky, earth
    p.underpainting(ref_pil, stroke_size=70)

    # Block in: dark figure mass, pale sky, dark earth floor
    p.block_in(ref_pil, stroke_size=30)

    # Build form: figure weight and volume, earth texture, branch silhouette
    p.build_form(ref_pil, stroke_size=14)

    # Lights: rim of light on figure's back, pale hand, hair
    p.place_lights(ref_pil, stroke_size=6)

    # ── KOLLWITZ CHARCOAL ETCHING — session 247, 158th distinct mode ──────────
    # First pass: full desaturation toward warm charcoal ramp + strong sigmoid + grain
    p.kollwitz_charcoal_etching_pass(
        desat_str=0.90,
        warm_r=0.93, warm_g=0.88, warm_b=0.78,   # warm cream-white paper
        dark_r=0.12, dark_g=0.09, dark_b=0.06,   # warm deep-black charcoal
        sigmoid_k=8.0,
        shadow_thresh=0.36,
        grain_angle_deg=50.0,                      # directional hatching at 50°
        grain_strength=0.14,
        grain_kernel_len=11,
        opacity=0.90,
    )

    # Second pass: lighter, refines the tonal separation without over-hardening
    p.kollwitz_charcoal_etching_pass(
        desat_str=0.60,
        sigmoid_k=4.0,
        shadow_thresh=0.30,
        grain_angle_deg=140.0,                     # cross-hatch at 140°
        grain_strength=0.08,
        grain_kernel_len=7,
        opacity=0.40,
    )

    # ── PAINT LUMINANCE STRETCH — session 247 improvement ─────────────────────
    # Ensure full tonal range: paper white to charcoal black
    p.paint_luminance_stretch_pass(
        lo_pct=2.0,
        hi_pct=97.0,
        opacity=0.70,
    )

    # Final vignette: draw the eye to the figure, deepen the edges
    p.focal_vignette_pass(vignette_strength=0.30, opacity=0.50)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
