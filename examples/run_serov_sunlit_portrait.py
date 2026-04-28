"""
run_serov_sunlit_portrait.py -- Session 224

"Afternoon Light at the Window" -- after Valentin Serov

Image Description
-----------------
Subject & Composition
    A young Russian woman in her early twenties sits at a sunlit interior window,
    seen in three-quarter view from slightly above.  She is positioned left of
    centre; the window and its white curtain dominate the right third of the
    canvas, flooding the room with afternoon light.  Her body is angled slightly
    away from the viewer but her face turns gently toward the light source,
    making her expression available without confrontation.  The composition
    divides into three lateral registers: the figure and shaded wall (left half),
    the transition zone of curtain and table edge (centre), and the luminous
    window itself (right third).  In the foreground, lower-centre: a ceramic
    bowl holds three ripe peaches -- a direct homage to Serov's "Girl with
    Peaches" (1887).

The Figure
    The woman is light-complexioned, with dark brown hair pinned loosely above
    the nape of her neck.  She wears a simple cream-white blouse, lightly
    starched, with a round collar.  Her hands rest folded in her lap -- one
    visible on the near knee, palm upward, fingers loosely open.  The light
    side of her face (right, toward the window) is bathed in warm peach-amber:
    this is direct summer sunlight on flesh, the colour of the sun itself
    warming what it touches.  The shadow side (left, away from the window)
    carries a distinct cool blue-violet, the reflected light of open sky
    coming through the same window at a different angle.  This is not neutral
    grey or umber shadow -- it is chromatic shadow, and it is Serov's defining
    technical insight.  Her expression is one of absorbed private contentment:
    she has paused in whatever she was doing, not bored, not performing, simply
    present in the warmth of an unremarkable afternoon that she will never
    specifically remember but that constitutes, in aggregate, the texture of
    a good life.

The Environment
    A Russian interior in late summer, probably at a dacha or country house.
    The walls are pale ochre plaster -- warm in the direct light of the window,
    slightly cooler and more muted where the light does not reach directly.
    White muslin curtains hang at the right side, catching and diffusing the
    direct sunlight into a luminous glow that fills rather than spotlights.
    Where the curtain folds, it carries cool shadows of the same blue-violet
    as the shadows on the woman's face: the interior light is consistent and
    physically plausible, every shadow in the room fed by the same sky.
    The foreground table is dark polished mahogany, its surface reflecting
    a thin specular streak from the window.  On the near side of the table:
    the ceramic bowl of peaches -- amber-orange where the sun strikes them,
    a deeper rose-brown in their shadow curves.  The room has the quality of
    summer afternoon stillness: warm, slightly golden-dusty, no sound except
    the occasional shift of curtain in a barely perceptible breeze.

Technique & Palette
    Valentin Serov's plein-air portraiture.  Primary pass: serov_sunlit_portrait_pass
    (session 224, 135th distinct mode) -- warm peach-amber tint applied to highlight
    zones, cool blue-violet applied to shadow zones, luminosity lift simulating
    outdoor ambient brightness, chromatic mid-tone vibration for broken-colour
    freshness.  Session improvement: color_temperature_oscillation_pass -- highlights
    warm golden, mid-tone transitions cool, shadow depths warm umber.  Secondary:
    halation_glow_pass -- bloom from window highlights into surrounding mid-tones.
    Foundation passes: warm linen ground tone_ground, underpainting (large strokes),
    block_in (structural masses), build_form (form-plane strokes), place_lights
    (tight highlight strokes).

    Palette: warm peach-amber (0.96, 0.82, 0.64) -- sunlit flesh; cool blue-violet
    (0.55, 0.55, 0.78) -- shadow passages; near-white sunlight (0.98, 0.96, 0.88)
    -- window brilliance and highest highlights; warm cream (0.90, 0.88, 0.82)
    -- blouse in diffuse light; pale ochre plaster (0.88, 0.82, 0.68) -- wall
    ground; amber-orange (0.96, 0.72, 0.42) -- peach foreground accent; dark
    mahogany (0.28, 0.18, 0.10) -- foreground table.

Mood & Intent
    This image is about the private warmth of an ordinary afternoon -- the kind
    of moment that is unremarkable in the experiencing but constitutes, in
    memory, everything.  Serov's great subject was not dramatic events or
    allegorical figures but the quality of light as it falls on people who are
    simply being alive.  The chromatic warm/cool oscillation creates the physical
    sensation of a real room with real outdoor light: the viewer feels the
    temperature difference between the sunlit side of the woman's face and the
    cool shadow beside it.  The bowl of peaches in the foreground is a
    deliberate citation of Serov's most beloved image -- a reminder that the
    Russian summer afternoon has always been this luminous, this transient, and
    this inexplicably sufficient.  Intended emotions: warmth, quiet joy, the
    specific sensory richness of light on skin on a summer afternoon.

Session 224 passes used:
    serov_sunlit_portrait_pass  (135th distinct mode)
    color_temperature_oscillation_pass  (session 224 artistic improvement)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "serov_sunlit_portrait.png"
)
W, H = 820, 1080


def build_reference() -> np.ndarray:
    """
    Synthetic reference for 'Afternoon Light at the Window'.

    Tonal zones:
      - Background wall (pale ochre plaster, whole canvas)
      - Window glow (upper-right: brilliant warm bloom)
      - Curtain (right side: white muslin with cool fold shadows)
      - Figure (centre-left: warm sunlit face/cool shadow side, cream blouse)
      - Foreground table (lower portion: dark mahogany)
      - Peach bowl (lower-centre: warm amber-orange fruits)
    """
    rng = np.random.default_rng(224)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys  = np.linspace(0.0, 1.0, H)[:, None]
    xs  = np.linspace(0.0, 1.0, W)[None, :]

    # -- Background: pale ochre plaster wall ---------------------------------
    wall = np.array([0.88, 0.82, 0.68])
    for ch in range(3):
        ref[:, :, ch] = wall[ch]

    # Subtle plaster texture
    wall_noise  = rng.random((H, W)).astype(np.float32)
    wall_smooth = gaussian_filter(wall_noise, sigma=(4.0, 6.0)) - 0.5
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + wall_smooth * 0.035, 0.0, 1.0)

    # -- Window light (upper-right): brilliant warm bloom --------------------
    win_cx, win_cy = 0.84, 0.22
    win_dist = np.sqrt(((xs - win_cx) / 0.30) ** 2 + ((ys - win_cy) / 0.38) ** 2)
    win_glow = np.clip(1.0 - win_dist, 0.0, 1.0) ** 1.2
    win_col  = np.array([0.98, 0.96, 0.88])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - win_glow * 0.76) + win_col[ch] * win_glow * 0.76

    # -- Curtain (right side): white with cool shadow folds ------------------
    curtain_mask = (
        np.clip((xs - 0.65) / 0.10, 0.0, 1.0)
        * np.clip(1.0 - ys / 0.82, 0.0, 1.0)
    )
    fold_light  = 0.90 + (np.sin(xs * 38.0) * 0.5 + 0.5) * 0.08
    curtain_r   = np.clip(fold_light, 0.0, 1.0)
    curtain_g   = np.clip(fold_light * 0.98, 0.0, 1.0)
    curtain_b   = np.clip(fold_light * 1.00, 0.0, 1.0)
    for ch, col in enumerate([curtain_r, curtain_g, curtain_b]):
        ref[:, :, ch] = ref[:, :, ch] * (1 - curtain_mask * 0.72) + col * curtain_mask * 0.72

    # -- Figure: young woman, centre-left, three-quarter view ----------------
    fig_cx = 0.42
    fig_cy = 0.44

    # Face (ellipse, slightly offset for three-quarter turn)
    face_cx, face_cy = fig_cx - 0.018, fig_cy - 0.26
    face_w,  face_h  = 0.088, 0.112
    face_dist  = np.sqrt(((xs - face_cx) / face_w) ** 2 + ((ys - face_cy) / face_h) ** 2)
    face_mask  = np.clip(1.18 - face_dist, 0.0, 1.0)

    # Warm/cool gradient: right side (toward window) warm; left side cool shadow
    face_sun   = np.clip((xs - face_cx + 0.05) / 0.10, 0.0, 1.0)
    face_warm  = np.array([0.94, 0.78, 0.60])   # sunlit peach
    face_cool  = np.array([0.66, 0.62, 0.74])   # reflected sky in shadow
    for ch in range(3):
        face_col = face_warm[ch] * face_sun + face_cool[ch] * (1.0 - face_sun)
        ref[:, :, ch] = ref[:, :, ch] * (1 - face_mask * 0.88) + face_col * face_mask * 0.88

    # Hair (dark warm brown above face)
    hair_cy   = face_cy - face_h * 0.60
    hair_dist = np.sqrt(((xs - face_cx) / (face_w * 1.08)) ** 2 +
                        ((ys - hair_cy)  / (face_h * 0.42)) ** 2)
    hair_mask = np.clip(1.1 - hair_dist, 0.0, 1.0)
    hair_col  = np.array([0.20, 0.13, 0.07])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - hair_mask * 0.88) + hair_col[ch] * hair_mask * 0.88

    # Neck
    neck_cy   = face_cy + face_h * 0.78
    neck_dist = np.sqrt(((xs - face_cx) / (face_w * 0.52)) ** 2 +
                        ((ys - neck_cy)  / (face_h * 0.38)) ** 2)
    neck_mask = np.clip(1.1 - neck_dist, 0.0, 1.0)
    neck_col  = np.array([0.88, 0.74, 0.58])   # warm lit neck
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - neck_mask * 0.80) + neck_col[ch] * neck_mask * 0.80

    # Body / blouse (cream-white, lower-centre)
    body_cy   = fig_cy + 0.08
    body_dist = np.sqrt(((xs - fig_cx) / 0.22) ** 2 + ((ys - body_cy) / 0.30) ** 2)
    body_mask = np.clip(1.0 - body_dist, 0.0, 1.0) ** 0.65
    blouse    = np.array([0.90, 0.88, 0.84])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - body_mask * 0.76) + blouse[ch] * body_mask * 0.76

    # -- Foreground table (dark polished mahogany) ---------------------------
    table_top = 0.74
    table_mask = np.clip((ys - table_top) / 0.08, 0.0, 1.0)
    table_col  = np.array([0.26, 0.17, 0.09])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - table_mask) + table_col[ch] * table_mask

    # Specular streak across table surface
    spec_x    = np.exp(-((xs - 0.50) ** 2) / (0.16 ** 2))
    spec_y    = np.clip((ys - table_top) / 0.04, 0.0, 1.0) * np.clip(
                    1.0 - (ys - table_top - 0.10) / 0.06, 0.0, 1.0)
    table_spec = spec_x * spec_y * 0.18
    for ch in range(3):
        ref[:, :, ch] = np.clip(ref[:, :, ch] + table_spec, 0.0, 1.0)

    # -- Peach bowl (lower-centre, homage to "Girl with Peaches") -----------
    bowl_cx, bowl_cy = 0.36, 0.80
    bowl_dist = np.sqrt(((xs - bowl_cx) / 0.10) ** 2 + ((ys - bowl_cy) / 0.045) ** 2)
    bowl_mask = np.clip(1.0 - bowl_dist, 0.0, 1.0)
    bowl_col  = np.array([0.52, 0.38, 0.22])
    for ch in range(3):
        ref[:, :, ch] = ref[:, :, ch] * (1 - bowl_mask * 0.58) + bowl_col[ch] * bowl_mask * 0.58

    for pcx, pcy in [(0.33, 0.74), (0.39, 0.73), (0.36, 0.71)]:
        p_dist = np.sqrt(((xs - pcx) / 0.046) ** 2 + ((ys - pcy) / 0.050) ** 2)
        p_mask = np.clip(1.0 - p_dist, 0.0, 1.0) ** 0.65
        p_sun  = np.clip((xs - pcx + 0.02) / 0.05, 0.0, 1.0)
        peach_lit = np.array([0.96, 0.72, 0.40])
        peach_shd = np.array([0.78, 0.48, 0.26])
        for ch in range(3):
            p_col = peach_lit[ch] * p_sun + peach_shd[ch] * (1.0 - p_sun)
            ref[:, :, ch] = ref[:, :, ch] * (1 - p_mask * 0.86) + p_col * p_mask * 0.86

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint 'Afternoon Light at the Window' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H, seed=224)

    # Ground: warm light linen -- plein-air brightness
    p.tone_ground((0.84, 0.80, 0.70), texture_strength=0.008)

    # Underpainting: establish tonal masses
    p.underpainting(ref_pil, stroke_size=60)

    # Block in: structural colour zones
    p.block_in(ref_pil, stroke_size=26)

    # Build form: paint-plane strokes building volume
    p.build_form(ref_pil, stroke_size=10)

    # Place lights: tight strokes on the brightest highlights
    p.place_lights(ref_pil, stroke_size=5)

    # PRIMARY PASS: Serov's plein-air warm-cool light system
    p.serov_sunlit_portrait_pass(
        warm_shift=0.28,
        cool_shift=0.22,
        highlight_thresh=0.62,
        shadow_thresh=0.42,
        luminosity_lift=0.05,
        vibration_strength=0.05,
        opacity=0.85,
    )

    # SESSION IMPROVEMENT: warm/cool oscillation across luminance zones
    p.color_temperature_oscillation_pass(
        warm_highlight_r=0.98,
        warm_highlight_g=0.94,
        warm_highlight_b=0.78,
        cool_midtone_r=0.84,
        cool_midtone_g=0.90,
        cool_midtone_b=0.98,
        warm_shadow_r=0.42,
        warm_shadow_g=0.26,
        warm_shadow_b=0.10,
        highlight_gate=0.70,
        shadow_gate=0.38,
        strength=0.22,
        opacity=0.70,
    )

    # Halation: bloom from window light into surrounding curtain/wall
    p.halation_glow_pass(
        threshold=0.78,
        bloom_sigma=0.05,
        bloom_intensity=0.30,
        glow_warm_r=1.00,
        glow_warm_g=0.96,
        glow_warm_b=0.82,
        opacity=0.55,
    )

    # Light atmospheric veil: very subtle warm unification
    p.glaze((0.90, 0.80, 0.62), opacity=0.04)

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
