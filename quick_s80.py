"""Quick s80 preview: apply new del Sarto pass to existing s70 painting."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image
import numpy as np
import cairo

print("Loading s70 painting...", flush=True)
img = Image.open("mona_lisa_s70_final.png").convert("RGB")
w, h = img.size
print(f"  {w}x{h}", flush=True)

from stroke_engine import Painter
print("Painter imported", flush=True)

p = Painter(w, h)

# Load the existing painting into the canvas
arr = np.array(img, dtype=np.float32) / 255.0
r_ch = arr[:, :, 0]; g_ch = arr[:, :, 1]; b_ch = arr[:, :, 2]
bgra = np.zeros((h, w, 4), dtype=np.uint8)
bgra[:, :, 0] = (b_ch * 255).astype(np.uint8)
bgra[:, :, 1] = (g_ch * 255).astype(np.uint8)
bgra[:, :, 2] = (r_ch * 255).astype(np.uint8)
bgra[:, :, 3] = 255
p.canvas.surface.get_data()[:] = bgra.tobytes()
print("Canvas loaded from s70", flush=True)

print("Applying Lotto chromatic anxiety pass (s79)...", flush=True)
p.lotto_chromatic_anxiety_pass(
    flesh_mid_lo=0.40, flesh_mid_hi=0.75,
    cool_b_boost=0.07, cool_r_reduce=0.04,
    eye_left_cx=0.468, eye_left_cy=0.198,
    eye_right_cx=0.562, eye_right_cy=0.198,
    eye_rx=0.060, eye_ry=0.038,
    eye_contrast=0.10, eye_cool_b=0.04, eye_cool_r=0.025,
    bg_mid_lo=0.28, bg_mid_hi=0.68,
    bg_green_lift=0.045, bg_blue_lift=0.028,
    blur_radius=4.5, opacity=0.46,
)

print("Applying Andrea del Sarto golden sfumato pass (s80 NEW)...", flush=True)
p.andrea_del_sarto_golden_sfumato_pass(
    flesh_mid_lo=0.45, flesh_mid_hi=0.78,
    gold_r_boost=0.050, gold_g_boost=0.028,
    sfumato_blur=5.5, edge_grad_lo=0.06, edge_grad_hi=0.22,
    harmony_sat_cap=0.85, harmony_pull=0.055,
    blur_radius=5.0, opacity=0.46,
)

print("Applying old master varnish...", flush=True)
p.old_master_varnish_pass(
    amber_strength=0.12, edge_darken=0.10, highlight_desat=0.06, opacity=0.28,
)
p.glaze((0.58, 0.44, 0.16), opacity=0.034)
p.finish(vignette=0.50, crackle=True)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s80.png")
p.save(out_path)
print(f"Saved: {out_path}", flush=True)
