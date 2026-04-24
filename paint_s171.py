"""
paint_s171.py — Session 171 painting with Abraham Bloemaert-inspired passes.

Runs the HIGH_RENAISSANCE Mona Lisa pipeline then applies:
  - bloemaert_pastoral_iridescence_pass (SIXTY-THIRD DISTINCT MODE)
  - chromatic_vignette_pass (SIXTY-FOURTH DISTINCT MODE)
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from examples.mona_lisa_portrait import build_reference, W, H
from stroke_engine import Painter
from art_catalog import get_style

OUTPUT = "mona_lisa_s171.png"

print("=" * 64)
print("  Mona Lisa — Session 171 (Abraham Bloemaert inspiration)")
print("  HIGH_RENAISSANCE + bloemaert_pastoral_iridescence_pass")
print("  + chromatic_vignette_pass")
print("=" * 64)

ref = build_reference(W, H)
leo = get_style("leonardo")
p = Painter(W, H)

p.tone_ground(leo.ground_color, texture_strength=0.06)
print("  [1/12] Tone ground")

p.underpainting(ref, stroke_size=48, n_strokes=160)
print("  [2/12] Underpainting")

p.block_in(ref, stroke_size=32, n_strokes=340)
print("  [3/12] Block-in")

p.build_form(ref, stroke_size=10, n_strokes=1400)
print("  [4/12] Build form")

p.sfumato_veil_pass(ref, n_veils=10, blur_radius=14.0, warmth=0.38,
                    veil_opacity=0.07, edge_only=True, chroma_dampen=0.20)
print("  [5/12] Sfumato veil")

p.tonal_envelope_pass(center_x=0.488, center_y=0.32, radius=0.48,
                      lift_strength=0.09, lift_warmth=0.35,
                      edge_darken=0.07, gamma=1.9)
print("  [6/12] Tonal envelope")

p.selective_focus_pass(center_x=0.488, center_y=0.29, focus_radius=0.34,
                       max_blur_radius=2.8, desaturation=0.10, gamma=2.2)
print("  [7/12] Selective focus")

p.place_lights(ref, stroke_size=5, n_strokes=320)
print("  [8/12] Place lights")

p.glaze((0.72, 0.52, 0.22), opacity=0.06)
print("  [9/12] Unifying glaze")

# Session 171 — new passes
p.bloemaert_pastoral_iridescence_pass(
    hf_sigma=2.5, threshold=0.03,
    warm_r=0.045, warm_g=0.018,
    cool_b=0.055, cool_r_reduce=0.025,
    luma_lo=0.08, luma_hi=0.92,
    opacity=0.50,
)
print("  [10/12] Bloemaert pastoral iridescence pass (s171)")

p.chromatic_vignette_pass(
    radius=0.72, darken_strength=0.28,
    cool_b=0.035, cool_r_reduce=0.018,
    vig_gamma=2.2, luma_lo=0.06,
    opacity=0.55,
)
print("  [11/12] Chromatic vignette pass (s171)")

p.finish(vignette=0.18, crackle=True)
print("  [12/12] Finish")

result = p.canvas.to_pil()
result.save(OUTPUT)
print(f"\n  Painting saved -> {OUTPUT}  ({W}×{H})")
print("=" * 64)
