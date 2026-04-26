"""
run_munch_sleepwalker_fjord.py — Session 205

"The Sleepwalker at the Fjord's Edge" — after Edvard Munch

Image Description
─────────────────
Subject & Composition
    A lone woman in a white nightgown stands at the very edge of a Norwegian
    dock in pre-dawn darkness, viewed from behind and slightly above.  She is
    centred but drifted slightly left — the void of the fjord and the open
    sky command the right half.  Her arms hang loosely at her sides.  Bare
    feet on weathered dock planks.  Hair loose and dark.  She is not looking
    at anything — or rather she is looking at everything with eyes that are
    closed.  The composition divides into three horizontal registers: the
    sky (upper 38%), the dock/figure transition (middle 20%), and the fjord
    (lower 42%).  All boundaries between them dissolve under the anxiety wave
    field.

The Figure
    The woman occupies roughly the central-left quarter of the canvas.  Her
    nightgown is white — not clean white but the white of something seen by
    half-light: pale cream with warm amber where the wave crests fall on it.
    Her silhouette is Munch's canonical somnambulant pose: upright but without
    volition, arms soft, weight distributed as if she has stopped mid-step.
    She is young — late twenties.  Her emotional state is the one Munch
    understood best: conscious absence.  She is physically present and
    psychologically elsewhere, which is why the anxiety of the landscape is
    hers — it radiates from her figure as one of the two interference focus
    points.  She does not feel afraid.  She does not feel anything.  The
    painting feels afraid on her behalf.

The Environment
    The fjord occupies the lower 42% of the canvas.  Its surface is not
    water in any naturalistic sense — it is a mirror of the anxiety field:
    dark indigo punctuated by concentric interference arcs of fiery red-orange
    and cool violet-indigo that radiate outward from the woman's reflected
    position below her.  The farther shoreline is a low dark mass, barely
    readable, dissolving into the atmospheric band at the horizon.  The dock
    planks beneath her are visible in the middle register — warm amber where
    wave crests fall on them, near-black in the troughs.  The dock extends
    forward (toward the viewer) as a narrow strip, disappearing into the
    lower edge.  The sky is the painting's principal emotional register: a
    field of swirling amber and indigo bands emanating from two sources —
    the woman's figure (lower focus point) and a spectral moon at upper left,
    half-dissolved in cloud (upper focus point).  Where the two wave systems
    constructively interfere, the sky burns red-orange; where they cancel,
    the sky goes a deep, oceanic indigo.  The cloud mass around the moon is
    pale cream-gold, lit from within.  No stars.  No wind.  The air is
    absolutely still — which makes the swirling wave fields more unnerving,
    not less.

Technique & Palette
    Edvard Munch's Norwegian Expressionist / Symbolist technique.  The
    munch_anxiety_swirl_pass (116th distinct mode) is the primary chromatic
    effect: two emotional focus points — the figure centre (0.38, 0.58) and
    the moon node (0.22, 0.18) — emit sine wave fields at frequency 9.0 that
    superpose across the canvas.  Constructive interference zones receive
    warm fiery red-orange injection; destructive zones receive deep indigo.
    High-amplitude zones receive a luma-preserving saturation boost that
    amplifies the colour identity of each pixel toward Munch's hyper-saturated
    anxiety peaks.  A second lower-frequency pass (frequency 4.5) adds a
    larger-scale undulation that echoes the fjord's physical wave structure.

    Palette: fiery red-orange (0.82, 0.28, 0.18) — anxiety heat; deep indigo
    (0.18, 0.22, 0.52) — existential dread; golden amber (0.88, 0.68, 0.22)
    — spectral warmth; pale cream-gold (0.90, 0.85, 0.62) — the moon's halo
    and the nightgown highlight; dark blue-grey (0.22, 0.28, 0.38) — void
    and heavy shadow.

Mood & Intent
    Munch's entire project was the externalisation of inner states.  He did
    not paint the visible world; he painted the world as it appears when you
    are inside a feeling too large to contain.  This image is about the
    specific loneliness of somnambulism: the body moving through space without
    the self present to inhabit it.  The anxiety field is not something
    threatening the woman — it is something emanating from her, invisible to
    her because she is asleep.  The viewer sees what the sleepwalker cannot:
    the emotional weather she carries with her, the interference pattern of
    her unconscious written in colour across a Norwegian fjord at 3am.  The
    intended emotion: a tenderness that is very close to dread.

Session 205 pass used:
    munch_anxiety_swirl_pass  (116th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "munch_sleepwalker_fjord.png"
)
W, H = 960, 1120


def build_reference() -> np.ndarray:
    """
    Synthetic reference for 'The Sleepwalker at the Fjord's Edge'.

    Tonal zones:
      - Sky (upper 38%): swirling amber-indigo, moon glow at upper-left
      - Dock/figure transition (middle 20%): warm amber planks, pale figure
      - Fjord (lower 42%): deep dark indigo water with interference arcs
      - Moon halo (upper-left): pale cream-gold spectral glow
      - Figure silhouette (centre-left): pale nightgown, dark hair
    """
    rng = np.random.default_rng(205)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    sky_frac  = 0.38
    dock_frac = 0.58   # dock/fjord boundary

    # ── Sky base: dark indigo-blue, lightening toward horizon ────────────────
    sky_deep   = np.array([0.10, 0.10, 0.22])
    sky_horiz  = np.array([0.28, 0.30, 0.40])
    sky_t = np.clip((ys - 0.0) / (sky_frac + 0.06), 0.0, 1.0)
    sky_mask_s = np.clip(1.0 - (ys / (sky_frac + 0.08)), 0.0, 1.0)
    for ch in range(3):
        sky_col = sky_deep[ch] * (1 - sky_t) + sky_horiz[ch] * sky_t
        ref[:, :, ch] += sky_col * sky_mask_s

    # ── Moon glow (upper-left sky) ────────────────────────────────────────────
    moon_cx, moon_cy = 0.22, 0.18
    moon_r = 0.22
    moon_dist = np.sqrt((xs - moon_cx) ** 2 + (ys - moon_cy) ** 2)
    moon_glow = np.clip(1.0 - moon_dist / moon_r, 0.0, 1.0) ** 1.6
    moon_col = np.array([0.88, 0.84, 0.62])   # pale cream-gold
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - moon_glow * 0.70 * sky_mask_s) + \
                        moon_col[ch] * moon_glow * 0.70 * sky_mask_s

    # Moon disc core
    core_glow = np.clip(1.0 - moon_dist / (moon_r * 0.22), 0.0, 1.0) ** 2.0
    core_col = np.array([0.95, 0.92, 0.78])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - core_glow * sky_mask_s) + \
                        core_col[ch] * core_glow * sky_mask_s

    # ── Anxious sky noise: organic swirling patches ───────────────────────────
    sky_noise = rng.random((H, W)).astype(np.float32)
    sky_smooth = gaussian_filter(sky_noise, sigma=(8.0, 12.0))
    sky_patches = (np.clip(sky_smooth - 0.42, 0.0, 1.0) * 3.5).clip(0, 0.45)
    warm_sky_col = np.array([0.52, 0.28, 0.12])   # muted warm ochre in sky patches
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - sky_patches * sky_mask_s) + \
                        warm_sky_col[ch] * sky_patches * sky_mask_s

    # ── Dock / figure register (sky_frac to dock_frac) ───────────────────────
    dock_mask = np.clip((ys - sky_frac) / 0.06, 0.0, 1.0) * \
                np.clip(1.0 - (ys - dock_frac) / 0.04, 0.0, 1.0)
    dock_plank_col = np.array([0.30, 0.24, 0.16])   # dark weathered wood

    # Plank grain: subtle horizontal streaking
    plank_noise = rng.random((H, W)).astype(np.float32)
    plank_smooth = gaussian_filter(plank_noise, sigma=(0.5, 12.0))
    plank_grain = np.clip((plank_smooth - 0.48) * 6.0, -0.10, 0.10)

    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - dock_mask) + \
                        np.clip(dock_plank_col[ch] + plank_grain * 0.8, 0.0, 1.0) * dock_mask

    # ── Fjord (below dock_frac) ───────────────────────────────────────────────
    fjord_mask = np.clip((ys - dock_frac) / 0.06, 0.0, 1.0)
    fjord_deep   = np.array([0.06, 0.08, 0.18])
    fjord_mid    = np.array([0.12, 0.16, 0.30])
    fjord_t = np.clip((ys - dock_frac) / (1.0 - dock_frac), 0.0, 1.0)
    for ch in range(3):
        fjord_col = fjord_mid[ch] * (1 - fjord_t) + fjord_deep[ch] * fjord_t
        ref[:, :, ch] = ref[:, :, ch] * (1 - fjord_mask) + fjord_col * fjord_mask

    # Moon reflection path on fjord: narrow warm streak
    refl_cx = moon_cx
    refl_w = 0.10
    refl_dist_x = np.abs(xs - refl_cx)
    refl_y_start = dock_frac + 0.04
    refl_mask = np.clip(
        1.0 - refl_dist_x / (refl_w * (1.0 + (ys - refl_y_start) * 1.2)),
        0.0, 1.0
    ) ** 2.0 * fjord_mask * np.clip((ys - refl_y_start) / 0.06, 0.0, 1.0)
    refl_col = np.array([0.50, 0.44, 0.28])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - refl_mask * 0.60) + \
                        refl_col[ch] * refl_mask * 0.60

    # ── Figure: pale nightgown silhouette (centre-left, dock register) ────────
    fig_cx  = 0.40
    fig_cy  = sky_frac + (dock_frac - sky_frac) * 0.42   # mid of dock register
    fig_w   = 0.062
    fig_h   = (dock_frac - sky_frac) * 0.82

    # Body
    body_dist = np.sqrt(
        ((xs - fig_cx) / fig_w) ** 2 + ((ys - fig_cy) / fig_h) ** 2
    )
    body_mask = np.clip(1.0 - body_dist ** 2.2, 0.0, 1.0)
    nightgown_col = np.array([0.80, 0.76, 0.62])   # warm cream-white
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - body_mask * 0.82) + \
                        nightgown_col[ch] * body_mask * 0.82

    # Head (dark hair, slightly oval, above body centre)
    head_cy = fig_cy - fig_h * 0.68
    head_w  = fig_w * 0.72
    head_h  = fig_h * 0.22
    head_dist = np.sqrt(
        ((xs - fig_cx) / head_w) ** 2 + ((ys - head_cy) / head_h) ** 2
    )
    head_mask = np.clip(1.0 - head_dist ** 2.0, 0.0, 1.0)
    hair_col = np.array([0.12, 0.10, 0.08])   # very dark
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - head_mask * 0.90) + \
                        hair_col[ch] * head_mask * 0.90

    # ── Far shoreline (dark ridge just above fjord transition) ────────────────
    shore_cy = dock_frac + 0.03
    shore_mask = np.exp(-((ys - shore_cy) ** 2) / (0.012 ** 2)) * \
                 np.clip(1.0 - np.abs(xs - 0.75) / 0.35, 0.0, 1.0)
    shore_col = np.array([0.10, 0.12, 0.18])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - shore_mask * 0.75) + \
                        shore_col[ch] * shore_mask * 0.75

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'The Sleepwalker at the Fjord's Edge' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=205)

    # ── Ground: dark warm umber — emotional depth base ────────────────────────
    p.tone_ground((0.38, 0.32, 0.25), texture_strength=0.010)

    # ── Underpainting: sky masses, fjord, dock register, figure mass ──────────
    p.underpainting(ref_pil, stroke_size=62)

    # ── Block in: sky zones, fjord field, dock planks, figure silhouette ─────
    p.block_in(ref_pil, stroke_size=28)

    # ── Build form: figure volume, dock plank texture, fjord surface ──────────
    p.build_form(ref_pil, stroke_size=11)

    # ── Lights: moon halo, nightgown highlight, fjord reflection streak ───────
    p.place_lights(ref_pil, stroke_size=5)

    # ── Munch Anxiety Swirl — PRIMARY effect: two focus points ───────────────
    # Pass 1 (primary): figure node + moon node, tightly sinuous strokes
    p.munch_anxiety_swirl_pass(
        n_swirl_strokes=180,
        swirl_amplitude=0.22,
        swirl_frequency=6.5,
        color_intensity=0.68,
        bg_only=False,
        stroke_opacity=0.42,
        stroke_size=8.0,
        warm_color=(0.82, 0.28, 0.18),
        cool_color=(0.18, 0.22, 0.52),
        focus_points=[(0.40, 0.58), (0.22, 0.18)],
        wave_frequency=9.0,
        opacity=1.0,
    )

    # Pass 2 (secondary): larger swirl amplitude, lower frequency, amber palette
    p.munch_anxiety_swirl_pass(
        n_swirl_strokes=80,
        swirl_amplitude=0.35,
        swirl_frequency=3.5,
        color_intensity=0.45,
        bg_only=False,
        stroke_opacity=0.28,
        stroke_size=14.0,
        warm_color=(0.88, 0.68, 0.22),
        cool_color=(0.22, 0.28, 0.38),
        focus_points=[(0.40, 0.58)],
        wave_frequency=4.5,
        opacity=1.0,
    )

    # ── Atmospheric depth: deepen edges and far distance ─────────────────────
    p.atmospheric_depth_pass(
        haze_color=(0.15, 0.15, 0.30),
        desaturation=0.28,
        lightening=0.12,
        depth_gamma=1.1,
        background_only=False,
        horizon_glow_band=0.0,
    )

    # ── Tonal compression: hold Munch's full emotional range ─────────────────
    p.tonal_compression_pass(shadow_lift=0.02, highlight_compress=0.96, midtone_contrast=0.05)

    # ── Meso detail: brushwork texture, emotional surface energy ─────────────
    p.meso_detail_pass(strength=0.12, opacity=0.10)

    # ── Glaze: cool violet tint to deepen the existential atmosphere ──────────
    p.glaze((0.12, 0.10, 0.28), opacity=0.05)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
