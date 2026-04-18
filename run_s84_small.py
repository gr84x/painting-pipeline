"""Quick run of session-84 pipeline at reduced resolution (520x720) to avoid MemoryError."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageFilter
from stroke_engine import Painter

W, H = 520, 720


def make_reference():
    ref = np.zeros((H, W, 3), dtype=np.float32)
    sky_top = np.array([0.72, 0.74, 0.78])
    sky_bottom = np.array([0.42, 0.48, 0.58])
    sky_band = int(H * 0.62)
    for y in range(sky_band):
        t = y / sky_band
        ref[y, :] = sky_top * (1 - t) + sky_bottom * t
    for x in range(W):
        hy = int(H * (0.52 + (x / W) * 0.04))
        for y in range(hy, H):
            t = (y - hy) / (H - hy)
            ref[y, x] = np.array([0.28, 0.30, 0.24]) * (1 - t) + np.array([0.18, 0.14, 0.09]) * t
    crag_c = np.array([0.35, 0.33, 0.28])
    for cx, cy, rx, ry in [(int(W*0.10), int(H*0.45), int(W*0.07), int(H*0.06)),
                            (int(W*0.22), int(H*0.42), int(W*0.06), int(H*0.08))]:
        for y in range(max(0, cy-ry), min(H, cy+ry+1)):
            for x in range(max(0, cx-rx), min(W, cx+rx+1)):
                dx, dy = (x-cx)/rx, (y-cy)/ry
                d = dx*dx + dy*dy
                if d <= 1.05:
                    fade = max(0.0, 1.0-(d-0.82)/0.23) if d > 0.82 else 1.0
                    ref[y, x] = ref[y, x]*(1-fade) + crag_c*fade
    right_crags = [(int(W*0.82), int(H*0.49), int(W*0.08), int(H*0.05)),
                   (int(W*0.92), int(H*0.46), int(W*0.07), int(H*0.06))]
    crag_r = np.array([0.38, 0.36, 0.30])
    for cx, cy, rx, ry in right_crags:
        for y in range(max(0, cy-ry), min(H, cy+ry+1)):
            for x in range(max(0, cx-rx), min(W, cx+rx+1)):
                dx, dy = (x-cx)/rx, (y-cy)/ry
                d = dx*dx + dy*dy
                if d <= 1.05:
                    fade = max(0.0, 1.0-(d-0.82)/0.23) if d > 0.82 else 1.0
                    ref[y, x] = ref[y, x]*(1-fade) + crag_r*fade
    path_c = np.array([0.50, 0.46, 0.34])
    for seg in range(30):
        t = seg / 30.0
        px = int(W * (0.04 + t*0.18 + 0.06*math.sin(t*math.pi*2.5)))
        py = int(H * (0.76 - t*0.28))
        pw = max(2, int(W * 0.028 * (1 - t*0.55)))
        for dy in range(-pw, pw+1):
            for dx in range(-pw, pw+1):
                fy, fx = py+dy, px+dx
                if 0 <= fy < H and 0 <= fx < W:
                    dp = math.sqrt(dx*dx + dy*dy) / pw
                    if dp <= 1.0:
                        fm = max(0.0, 1.0 - dp*0.8) * 0.6
                        ref[fy, fx] = ref[fy, fx]*(1-fm) + path_c*fm
    river_y, river_h = int(H*0.47), int(H*0.022)
    river_c = np.array([0.42, 0.52, 0.64])
    for y in range(river_y-river_h, river_y+river_h):
        if 0 <= y < H:
            for x in range(int(W*0.25), int(W*0.44)):
                et = max(0.0, 1.0 - abs(y-river_y)/river_h)
                ref[y, x] = ref[y, x]*(1-et*0.62) + river_c*et*0.62
    veg_c = np.array([0.22, 0.28, 0.16])
    for cx, cy, rx, ry in [(int(W*0.16), int(H*0.55), int(W*0.03), int(H*0.04)),
                            (int(W*0.85), int(H*0.56), int(W*0.03), int(H*0.04))]:
        for y in range(max(0, cy-ry), min(H, cy+ry+1)):
            for x in range(max(0, cx-rx), min(W, cx+rx+1)):
                dx, dy = (x-cx)/rx, (y-cy)/ry
                d = dx*dx + dy*dy
                if d <= 1.0:
                    fade = max(0.0, 1.0-(d-0.75)/0.25) if d > 0.75 else 1.0
                    ref[y, x] = ref[y, x]*(1-fade*0.7) + veg_c*fade*0.7
    dress_c = np.array([0.10, 0.13, 0.10])
    for y in range(int(H*0.38), H):
        for x in range(int(W*0.16), int(W*0.84)):
            t_body = max(0.0, min(1.0, (y - H*0.38)/(H*0.28)))
            half_w = int(W * (0.24 + 0.10*t_body))
            cx2 = W // 2
            if abs(x - cx2) <= half_w:
                dist_edge = (half_w - abs(x-cx2)) / half_w
                fade = min(1.0, dist_edge*4.0)
                ref[y, x] = ref[y, x]*(1-fade) + dress_c*fade
    neck_y = int(H*0.40)
    neck_c = np.array([0.72, 0.60, 0.28])
    for y in range(neck_y-3, neck_y+4):
        for x in range(int(W*0.33), int(W*0.67)):
            if 0 <= y < H:
                ref[y, x] = ref[y, x]*0.4 + neck_c*0.6
    skin_hi = np.array([0.88, 0.76, 0.58])
    skin_mid = np.array([0.76, 0.60, 0.42])
    skin_sh = np.array([0.52, 0.38, 0.24])
    def paint_skin(cx, cy, rx, ry, lit_dir=(0.35, -0.70)):
        for y in range(max(0, cy-ry-3), min(H, cy+ry+4)):
            for x in range(max(0, cx-rx-3), min(W, cx+rx+4)):
                dx, dy = (x-cx)/rx, (y-cy)/ry
                d = dx*dx + dy*dy
                if d <= 1.08:
                    shade = max(0.0, min(1.0, dx*lit_dir[0] + dy*lit_dir[1]))
                    c = skin_hi*(1-shade)*0.5 + skin_mid*0.5 + skin_sh*shade*0.5
                    fade = max(0.0, 1.0-(d-0.85)/0.23) if d > 0.85 else 1.0
                    ref[y, x] = ref[y, x]*(1-fade) + np.clip(c, 0, 1)*fade
    face_cx, face_cy = W//2 + 5, int(H*0.215)
    face_rx, face_ry = int(W*0.125), int(H*0.168)
    paint_skin(face_cx, face_cy, face_rx, face_ry)
    for y in range(int(H*0.370), int(H*0.415)):
        for x in range(W//2+3-int(W*0.048), W//2+3+int(W*0.048)):
            if 0 <= x < W:
                ref[y, x] = skin_mid
    paint_skin(W//2, int(H*0.78), int(W*0.15), int(H*0.06), lit_dir=(0.2, -0.5))
    hair_c = np.array([0.14, 0.11, 0.08])
    hair_top = face_cy - face_ry - 5
    for side in [-1, 1]:
        for seg in range(20):
            t = seg / 20.0
            hx = face_cx + side*int(face_rx*(0.3 + t*0.7))
            hy = hair_top + int(face_ry*t*1.5)
            for dy in range(-12, 13):
                for dx in range(-8, 9):
                    fy, fx = hy+dy, hx+dx
                    if 0 <= fy < H and 0 <= fx < W:
                        d = math.sqrt(dx*dx*0.6 + dy*dy)
                        if d < 11:
                            fade = max(0.0, 1.0 - d/11.0) * 0.80
                            ref[fy, fx] = ref[fy, fx]*(1-fade) + hair_c*fade
    hair_mid = np.array([0.22, 0.18, 0.12])
    veil_y = hair_top - 8
    for y in range(max(0, veil_y-15), min(H, face_cy + face_ry//2)):
        for x in range(int(W*0.25), int(W*0.75)):
            if 0 <= y < H:
                dist_top = max(0, y - veil_y) / (face_ry * 0.6)
                veil_str = max(0.0, 1.0 - dist_top) * 0.55
                ref[y, x] = ref[y, x]*(1-veil_str) + hair_mid*veil_str
    gauze_c = np.array([0.64, 0.58, 0.48])
    for y in range(int(H*0.40), int(H*0.72)):
        for x in range(int(W*0.20), int(W*0.52)):
            dy_f = (y - H*0.40) / (H*0.32)
            dx_f = (x - W*0.20) / (W*0.32)
            fade = max(0.0, 1.0 - (dy_f + dx_f)*0.7) * 0.38
            ref[y, x] = ref[y, x]*(1-fade) + gauze_c*fade
    eye_c = np.array([0.12, 0.10, 0.08])
    for ox, oy in [(-int(W*0.048), -int(H*0.022)), (int(W*0.048), -int(H*0.022))]:
        ex, ey = face_cx+ox, face_cy+oy
        for dy in range(-6, 7):
            for dx in range(-15, 16):
                if 0 <= ey+dy < H and 0 <= ex+dx < W:
                    d = (dx/13.0)**2 + (dy/5.0)**2
                    if d <= 1.0:
                        fade = max(0.0, 1.0-d) * 0.85
                        ref[ey+dy, ex+dx] = ref[ey+dy, ex+dx]*(1-fade) + eye_c*fade
    lip_c = np.array([0.74, 0.50, 0.40])
    lip_cx, lip_cy = face_cx+1, face_cy + int(face_ry*0.52)
    for dy in range(-6, 7):
        for dx in range(-14, 15):
            if 0 <= lip_cy+dy < H and 0 <= lip_cx+dx < W:
                d = (dx/11.0)**2 + (dy/4.5)**2
                if d <= 1.0:
                    fade = max(0.0, 1.0-d) * 0.68
                    ref[lip_cy+dy, lip_cx+dx] = ref[lip_cy+dy, lip_cx+dx]*(1-fade) + lip_c*fade
    ref_uint8 = np.clip(ref*255, 0, 255).astype(np.uint8)
    ref_img = Image.fromarray(ref_uint8)
    ref_img = ref_img.filter(ImageFilter.GaussianBlur(radius=12))
    return ref_img


def make_mask():
    from scipy.ndimage import gaussian_filter
    mask = np.zeros((H, W), dtype=np.float32)
    face_cx, face_cy = W//2+5, int(H*0.215)
    face_rx, face_ry = int(W*0.138), int(H*0.185)
    ys, xs = np.ogrid[:H, :W]
    face_d = ((xs-face_cx)/face_rx)**2 + ((ys-face_cy)/face_ry)**2
    mask[face_d <= 1.15] = 1.0
    body_top = int(H*0.37)
    for y in range(body_top, H):
        t = (y - body_top) / (H - body_top)
        half_w = int(W * (0.22 + 0.12*t))
        cx = W // 2
        mask[y, max(0, cx-half_w):min(W, cx+half_w)] = 1.0
    mask = gaussian_filter(mask, sigma=8.0)
    mask = np.clip(mask / mask.max(), 0.0, 1.0)
    return mask


def paint():
    print("Session 84 (reduced resolution 520x720) -- Mona Lisa portrait")
    print("Random artist: Pietro Perugino (Umbrian / High Renaissance, c. 1446-1523)")
    print()
    ref = make_reference()
    p = Painter(W, H)
    p.set_figure_mask(make_mask())
    p.tone_ground((0.54, 0.46, 0.28), texture_strength=0.05)
    print("Underpainting...")
    p.underpainting(ref, stroke_size=38, n_strokes=200)
    p.block_in(ref, stroke_size=28, n_strokes=380)
    p.ground_tone_recession_pass(horizon_y=0.54, fg_warm_lift=0.032, bg_cool_lift=0.038, transition_band=0.22, opacity=0.48)
    p.block_in(ref, stroke_size=16, n_strokes=450)
    p.build_form(ref, stroke_size=10, n_strokes=700)
    p.build_form(ref, stroke_size=5, n_strokes=520)
    print("Atmospheric and artistic passes...")
    p.patinir_weltlandschaft_pass(warm_foreground=0.06, green_midground=0.05, cool_distance=0.10, horizon_near=0.52, horizon_far=0.70, transition_blur=10.0, opacity=0.58)
    p.cool_atmospheric_recession_pass(horizon_y=0.54, cool_strength=0.16, bright_lift=0.06, desaturate=0.42, blur_background=True, feather=0.12, opacity=0.64)
    p.parmigianino_serpentine_elegance_pass(porcelain_strength=0.10, lavender_shadow=0.08, silver_highlight=0.06, opacity=0.36)
    p.vigee_le_brun_pearlescent_grace_pass(rose_bloom_strength=0.07, pearl_highlight=0.06, shadow_warmth=0.04, midtone_low=0.45, midtone_high=0.82, opacity=0.46)
    p.subsurface_scatter_pass(scatter_strength=0.10, scatter_radius=5.0, scatter_low=0.42, scatter_high=0.82, penumbra_warm=0.05, shadow_cool=0.03, opacity=0.42)
    p.correggio_golden_tenderness_pass(midtone_low=0.30, midtone_high=0.78, gold_lift=0.055, amber_shadow=0.045, face_cx=0.512, face_cy=0.210, face_rx=0.140, face_ry=0.190, glow_strength=0.048, blur_radius=9.0, opacity=0.46)
    p.guido_reni_angelic_grace_pass(face_cx=0.512, face_cy=0.210, face_rx=0.125, face_ry=0.168, pearl_lift=0.07, pearl_cool=0.04, cheek_rose=0.045, lip_rose=0.055, shadow_violet=0.042, blur_radius=8.0, opacity=0.50)
    p.anguissola_intimacy_pass(focus_cx=0.512, focus_cy=0.210, focus_radius=0.155, sharpen_strength=0.70, eye_cx_offset=0.048, eye_cy_offset=-0.018, eye_radius=0.032, lip_cy_offset=0.055, lip_rx=0.052, lip_ry=0.020, periphery_soften=0.45, warm_ambient=0.018, opacity=0.52)
    p.alma_tadema_marble_luminance_pass(marble_warm_strength=0.07, specular_cool_shift=0.05, specular_thresh=0.82, translucent_low=0.50, translucent_high=0.82, opacity=0.45)
    p.mantegna_sculptural_form_pass(highlight_lift=0.09, shadow_deepen=0.07, edge_crisp=0.05, blur_radius=3.5, opacity=0.44)
    p.david_neoclassical_clarity_pass(figure_cx=0.512, figure_top=0.02, figure_bottom=0.90, figure_rx=0.30, bg_cool_shift=0.058, contour_crisp=0.048, amber_glaze=0.038, blur_radius=6.0, opacity=0.46)
    p.canaletto_luminous_veduta_pass(sky_lift=0.08, stone_warm=0.06, water_cool=0.06, sky_band=0.52, opacity=0.52)
    p.weyden_angular_shadow_pass(shadow_thresh=0.36, light_thresh=0.62, edge_sharpen=0.38, shadow_cool=0.06, highlight_cool=0.03, opacity=0.50)
    p.sfumato_thermal_gradient_pass(warm_strength=0.10, cool_strength=0.12, horizon_y=0.52, gradient_width=0.28, edge_soften_radius=7, opacity=0.62)
    print("Sfumato veil...")
    p.sfumato_veil_pass(ref, n_veils=9, blur_radius=9.0, warmth=0.26, veil_opacity=0.046, edge_only=True, chroma_dampen=0.22, depth_gradient=0.55, shadow_warm_recovery=0.12)
    p.translucent_gauze_pass(zone_top=0.38, zone_bottom=0.58, opacity=0.26, cool_shift=0.04, weave_strength=0.010, blur_radius=5.0)
    p.giorgione_tonal_poetry_pass(midtone_low=0.32, midtone_high=0.68, luminous_lift=0.06, warm_shadow_strength=0.04, cool_edge_strength=0.04, opacity=0.48)
    p.place_lights(ref, stroke_size=4, n_strokes=420)
    p.aerial_perspective_pass(sky_band=0.58, fade_power=2.0, desaturation=0.52, cool_push=0.11, haze_lift=0.06, opacity=0.70)
    p.crystalline_surface_pass(specular_radius=2.2, specular_strength=0.10, specular_thresh=0.82, micro_cool_shift=0.04, halo_radius=6.0, halo_warmth=0.05, halo_thresh=0.68, opacity=0.50)
    p.highlight_bloom_pass(threshold=0.76, bloom_sigma=10.0, bloom_opacity=0.28, bloom_color=(1.00, 0.97, 0.90), multi_scale=True, figure_only=False, chromatic_bloom=True)
    p.luminous_haze_pass(haze_warmth=0.038, haze_opacity=0.10, haze_color=(0.88, 0.76, 0.50), soften_radius=2.2, contrast_damp=0.055, shadow_lift=0.016, opacity=0.50)
    p.watteau_crepuscular_reverie_pass(amber_shift=0.032, shadow_lift=0.020, edge_soften=3.0, crepuscular_low=0.32, crepuscular_high=0.72, periphery_darken=0.055, opacity=0.44)
    p.de_hooch_threshold_light_pass(light_x=0.12, light_width=0.55, light_falloff=0.60, warm_color=(0.78, 0.58, 0.28), cool_color=(0.36, 0.46, 0.58), warm_strength=0.20, cool_strength=0.14, doorway_y=0.28, doorway_h=0.50, doorway_w=0.16, doorway_x=0.84, opacity=0.38)
    p.skin_zone_temperature_pass(face_cx=0.512, face_cy=0.196, face_rx=0.125, face_ry=0.168, forehead_warm=0.035, temple_cool=0.028, nose_pink=0.038, lip_rose=0.030, jaw_cool=0.025, blur_radius=8.0, opacity=0.55)
    p.warm_cool_form_duality_pass(warm_strength=0.06, cool_strength=0.06, midtone=0.48, transition_width=0.18, blur_radius=6.0, opacity=0.52)
    p.steen_warm_vitality_pass(face_cx=0.512, face_cy=0.210, face_rx=0.140, face_ry=0.195, amber_lift=0.048, rose_flush=0.034, shadow_warmth=0.032, shadow_thresh=0.36, highlight_thresh=0.72, blur_radius=8.0, opacity=0.52)
    p.poussin_classical_clarity_pass(shadow_cool=0.06, midtone_lift=0.04, saturation_cap=0.82, highlight_ivory=0.04, opacity=0.35)
    p.rigaud_velvet_drapery_pass(velvet_thresh=0.30, velvet_dark=0.10, velvet_warm_r=0.06, velvet_warm_g=0.03, silk_thresh=0.68, silk_cool_b=0.08, silk_cool_r=0.03, blur_radius=5.0, opacity=0.48)
    p.lotto_chromatic_anxiety_pass(flesh_mid_lo=0.40, flesh_mid_hi=0.75, cool_b_boost=0.07, cool_r_reduce=0.04, eye_left_cx=0.466, eye_left_cy=0.198, eye_right_cx=0.560, eye_right_cy=0.198, eye_rx=0.060, eye_ry=0.038, eye_contrast=0.10, eye_cool_b=0.04, eye_cool_r=0.025, bg_mid_lo=0.28, bg_mid_hi=0.68, bg_green_lift=0.045, bg_blue_lift=0.028, blur_radius=4.0, opacity=0.46)
    p.andrea_del_sarto_golden_sfumato_pass(flesh_mid_lo=0.45, flesh_mid_hi=0.78, gold_r_boost=0.050, gold_g_boost=0.028, sfumato_blur=5.0, edge_grad_lo=0.06, edge_grad_hi=0.22, harmony_sat_cap=0.85, harmony_pull=0.055, blur_radius=4.5, opacity=0.46)
    p.chardin_granular_intimacy_pass(dab_radius=2.8, dab_density=0.52, mute_strength=0.18, lum_cap=0.88, lum_cap_str=0.26, warm_gray_r=0.70, warm_gray_g=0.66, warm_gray_b=0.55, opacity=0.34, rng_seed=81)
    p.gericault_romantic_turbulence_pass(shadow_thresh=0.32, shadow_warm_r=0.13, shadow_warm_g=0.05, shadow_cool_b=0.11, turb_low=0.30, turb_high=0.68, turb_strength=0.048, turb_frequency=8.0, contrast_midpoint=0.48, contrast_gain=3.5, contrast_strength=0.13, opacity=0.44, rng_seed=82)
    p.fra_filippo_lippi_tenerezza_pass(flesh_mid_lo=0.42, flesh_mid_hi=0.80, rose_r_boost=0.046, rose_g_boost=0.016, rose_b_dampen=0.026, glow_thresh=0.72, glow_lift=0.038, glow_blur=7.0, bg_cool_shift=0.020, bg_desaturate=0.10, bg_thresh=0.44, blur_radius=5.5, opacity=0.42)
    print("Perugino serene grace pass (session 84 NEW)...")
    p.perugino_serene_grace_pass(sky_band=0.52, sky_cool_b=0.050, sky_desaturate=0.28, sky_lift=0.038, shadow_thresh_lo=0.18, shadow_thresh_hi=0.44, shadow_cool_b=0.026, shadow_cool_r=0.010, shadow_violet_g=0.005, midtone_lo=0.40, midtone_hi=0.76, smooth_sigma=3.0, smooth_strength=0.16, blur_radius=6.0, opacity=0.38)
    p.edge_lost_and_found_pass(focal_xy=(0.512, 0.195), found_radius=0.28, found_sharpness=0.48, lost_blur=2.0, strength=0.34, figure_only=True, gradient_selectivity=0.65)
    p.old_master_varnish_pass(amber_strength=0.12, edge_darken=0.10, highlight_desat=0.06, opacity=0.28)
    p.glaze((0.58, 0.44, 0.16), opacity=0.034)
    p.finish(vignette=0.50, crackle=True)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mona_lisa_s84.png")
    p.save(out_path)
    print(f"Done: {out_path}")
    return out_path


if __name__ == "__main__":
    paint()
