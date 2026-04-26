"""
run_riley_op_art_current.py — Session 195

Paints a Bridget Riley-inspired Op Art composition: "Current" — a field of
undulating sinusoidal wave bands whose frequency is modulated by the underlying
tonal structure of a coastal cliff face seen from directly below, the sky above
a pure white void.  The rock's dark stratified geology tightens the waves into
dense optical vibration; the pale sky relaxes them into slow, wide undulations.
The tension between regions creates an illusion of the cliff surface breathing
— receding and advancing as the eye traverses the optical field.

The composition is strictly black-and-white, honouring Riley's early 1960s
practice before she introduced colour.  No naturalistic representation remains
— only the frequency-modulated wave field encodes the original subject.

Session 195 pass used:
  riley_op_art_wave_pass  (106th distinct mode)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "riley_op_art_current.png"
)
W, H = 800, 800   # square format — Riley's preferred Op Art proportions


def build_reference() -> np.ndarray:
    """
    Synthetic reference for a coastal cliff-sky scene.

    This reference is only used for its luminance structure — the wave
    frequency will be higher (tighter) where the reference is dark
    (the stratified rock face) and lower (wider) where it is bright (sky).

    Zones:
      - Pure white sky — upper quarter (y < 0.25)
      - Transition haze — upper-mid zone
      - Dark stratified cliff face — lower two-thirds
        with horizontal strata bands of varying darkness
      - Deepest shadow at cliff base (y > 0.85)
    """
    rng = np.random.default_rng(195)
    ref = np.zeros((H, W, 3), dtype=np.float32)
    ys = np.linspace(0.0, 1.0, H)[:, None]
    xs = np.linspace(0.0, 1.0, W)[None, :]

    # ── Sky: pure white void ──────────────────────────────────────────────────
    sky_boundary = 0.28
    sky_t = np.clip(ys / sky_boundary, 0.0, 1.0)
    sky_lum = 1.0 - 0.15 * sky_t ** 2    # near-white at top, slight grey near cliff
    ref[:, :, 0] = sky_lum
    ref[:, :, 1] = sky_lum
    ref[:, :, 2] = sky_lum

    # ── Cliff face: dark stratified geology ───────────────────────────────────
    cliff_t = np.clip((ys - sky_boundary) / (1.0 - sky_boundary), 0.0, 1.0)
    # Base cliff luminance: darkens toward the bottom
    cliff_base = 0.55 - 0.45 * cliff_t ** 1.4

    # Horizontal strata bands — each band a different tone
    n_strata = 18
    strata_lum = cliff_base.copy()
    for si in range(n_strata):
        band_y = sky_boundary + (si + 0.5) * (1.0 - sky_boundary) / n_strata
        band_width = rng.uniform(0.015, 0.045)
        band_dark = rng.uniform(0.0, 0.30)   # how much darker this stratum is
        band_mask = np.exp(-((ys - band_y) ** 2) / (2 * band_width ** 2))
        strata_lum = strata_lum - band_dark * band_mask

    strata_lum = np.clip(strata_lum, 0.02, 0.80)

    # Add fine-grain geological noise (simulates rock texture)
    noise = rng.standard_normal((H, W)).astype(np.float32) * 0.04
    strata_lum = np.clip(strata_lum + noise, 0.02, 0.80)

    # Apply cliff over sky
    cliff_mask = ys >= sky_boundary
    ref[:, :, 0] = np.where(cliff_mask, strata_lum, ref[:, :, 0])
    ref[:, :, 1] = np.where(cliff_mask, strata_lum * 0.98, ref[:, :, 1])
    ref[:, :, 2] = np.where(cliff_mask, strata_lum * 0.94, ref[:, :, 2])

    # ── Deep shadow at base ───────────────────────────────────────────────────
    shadow_t = np.clip((ys - 0.82) / 0.18, 0.0, 1.0)
    shadow = (1.0 - shadow_t ** 0.5) * 0.0 + shadow_t ** 0.5 * 0.0
    # Darken base
    ref[:, :, 0] = ref[:, :, 0] * (1.0 - 0.6 * shadow_t ** 2)
    ref[:, :, 1] = ref[:, :, 1] * (1.0 - 0.6 * shadow_t ** 2)
    ref[:, :, 2] = ref[:, :, 2] * (1.0 - 0.6 * shadow_t ** 2)

    return np.clip(ref, 0.0, 1.0)


def main() -> str:
    """Paint the Riley Op Art 'Current' and return the output path."""
    ref_arr = build_reference()
    ref_pil = Image.fromarray((ref_arr * 255).astype(np.uint8), "RGB")

    p = Painter(W, H)

    # ── Ground: pure white — Riley's immaculate prepared surface ─────────────
    p.tone_ground((0.99, 0.99, 0.99), texture_strength=0.0)

    # ── Primary Riley wave pass: black/white — early 1960s palette ────────────
    p.riley_op_art_wave_pass(
        ref_pil,
        n_waves=100,
        base_amplitude=14.0,
        freq_modulation=0.85,
        base_frequency=0.010,
        color_a=(0.04, 0.04, 0.04),    # near-black
        color_b=(0.97, 0.97, 0.97),    # near-white
        opacity=0.95,
        seed=195,
    )

    # ── Second pass: slightly different phase, reduced amplitude ──────────────
    # Adds interference beats — the subtle "moiré" ripple in Riley's work
    p.riley_op_art_wave_pass(
        ref_pil,
        n_waves=24,
        base_amplitude=6.0,
        freq_modulation=0.40,
        base_frequency=0.018,
        color_a=(0.10, 0.10, 0.10),
        color_b=(0.90, 0.90, 0.90),
        opacity=0.18,
        seed=999,
    )

    p.canvas.surface.write_to_png(OUTPUT)
    print(f"Saved: {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    main()
