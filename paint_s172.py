"""
paint_s172.py — Session 172 painting with Hendrick Avercamp-inspired passes.

Runs the HIGH_RENAISSANCE Mona Lisa pipeline then applies:
  - avercamp_winter_atmosphere_pass (SIXTY-FIFTH DISTINCT MODE)
  - diagonal_light_gradient_pass (SIXTY-SIXTH DISTINCT MODE)
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from examples.mona_lisa_portrait import build_reference, W, H
from stroke_engine import Painter
from art_catalog import get_style

OUTPUT = "mona_lisa_s172.png"

print("=" * 64)
print("  Mona Lisa — Session 172 (Hendrick Avercamp inspiration)")
print("  HIGH_RENAISSANCE + avercamp_winter_atmosphere_pass")
print("  + diagonal_light_gradient_pass")
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

# Session 172 — new passes
p.avercamp_winter_atmosphere_pass(
    silver_r=0.73, silver_g=0.76, silver_b=0.82,
    grey_strength=0.28,
    warm_r=0.048, warm_g=0.020,
    warmth_lo=0.32, warmth_hi=0.70,
    warmth_strength=0.55,
    opacity=0.52,
)
print("  [10/12] Avercamp winter atmosphere pass (s172)")

p.diagonal_light_gradient_pass(
    angle_deg=48.0,
    warm_r=0.038, warm_g=0.015,
    cool_b=0.032, cool_r_reduce=0.015,
    luma_lo=0.08, luma_hi=0.90,
    gamma=1.5,
    opacity=0.42,
)
print("  [11/12] Diagonal light gradient pass (s172)")

p.finish(vignette=0.18, crackle=True)
print("  [12/12] Finish")

result = p.canvas.to_pil()
result.save(OUTPUT)
print(f"\n  Painting saved -> {OUTPUT}  ({W}×{H})")
print("=" * 64)
