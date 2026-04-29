"""Insert kiefer_scorched_earth_pass and paint_impasto_ridge_cast_pass into
stroke_engine.py (session 253).

NOTE: This script was already executed during session 253. Running it again
will fail the existence check. It is preserved as a record of the change.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

SCORCHED_EARTH_PASS = """
    def kiefer_scorched_earth_pass(
        self,
        n_zones:        int   = 8,
        ash_tone:       tuple = (0.28, 0.26, 0.24),
        max_ash_blend:  float = 0.68,
        dark_push:      float = 0.14,
        n_cracks:       int   = 18,
        crack_width:    int   = 3,
        crack_depth:    float = 0.38,
        crack_tone:     tuple = (0.14, 0.12, 0.10),
        lum_ceiling:    float = 0.60,
        straw_angle:    float = 15.0,
        straw_period:   int   = 9,
        fiber_strength: float = 0.38,
        straw_lo:       float = 0.30,
        straw_hi:       float = 0.65,
        straw_color:    tuple = (0.76, 0.68, 0.28),
        opacity:        float = 0.82,
        seed:           int   = 253,
    ) -> None:
        r\"\"\"Anselm Kiefer Scorched Earth -- session 253, 164th distinct painting mode.

        THREE-STAGE SCORCHED FIELD WITH STRAW AND LEAD:

        Stage 1 ASHEN FIELD DESATURATION GRADIENT: Divide the canvas into
        n_zones equal horizontal depth strips (foreground=bottom to
        background=top). For each zone compute a fractional blend weight
        zone_frac = (zone_index / n_zones) * max_ash_blend, representing the
        increasing ashen haze toward the horizon. Convert each pixel to HSV;
        blend the pixel colour toward ash_tone at zone_frac. Additionally gate
        the blend by pixel luminance: dark pixels (lum < 0.35) receive an extra
        darkening push of dark_push toward near-black (charred zone); mid-tone
        pixels (0.35 ≤ lum < 0.65) receive full ash blend (scorched field);
        light pixels (lum ≥ 0.65) receive half blend (unburned edge glint).
        NOVEL: (a) ZONE-PARTITIONED LUMINANCE-GATED SIMULTANEOUS DESATURATION
        AND DARKENING IN DEPTH GRADIENT -- first pass to apply zone-indexed
        horizontal strip desaturation that simultaneously pushes dark pixels
        toward charcoal and mid-tones toward ash while preserving light-pixel
        chroma, parameterised by depth position (foreground to horizon); no
        prior depth-gradient pass (paint_aerial_perspective_pass uses colour
        shift by global y-coordinate without luminance gating; paint_glaze_
        gradient_pass applies a unitary glaze colour without zone partitioning
        or luminance-gated differential treatment).

        Stage 2 LEAD SHEET CRACK VEINING: Generate n_cracks sinusoidal crack
        trajectories. Each crack: amplitude A = rng.uniform(4, 28) pixels,
        frequency f = rng.uniform(0.005, 0.020) cycles/pixel, phase phi =
        rng.uniform(0, 2π), origin y_origin = rng.uniform(0.1, 0.9) * h.
        For each x in [0, w): crack_y = y_origin + A * sin(2π * f * x + phi).
        For pixels within crack_width of crack_y AND with pixel lum < lum_ceiling,
        blend the pixel colour toward crack_tone at crack_depth.
        NOVEL: (b) SINUSOIDAL DIRECTIONAL VEIN NETWORK WITH LUMINANCE-GATED
        DISCONTINUITY -- first pass to generate crack-path veinings as
        composites of sinusoidal directional trajectories with per-pixel
        luminance gating (cracks only appear on dark/mid-tone surfaces, not
        on light areas); the crackle pass in ArtStyle uses a boolean crackle
        flag applied elsewhere as isotropic Voronoi noise; no prior stroke_engine
        pass draws structured sinusoidal directional vein paths with luminance-
        threshold discontinuity.

        Stage 3 STRAW FIBER WARM OVERLAY: Compute a tilted sinusoidal fiber
        texture oriented at straw_angle degrees from horizontal (representing
        Kiefer's embedded straw at the characteristic ~15° ploughed-furrow
        angle). For each pixel (x, y): compute the fiber coordinate along
        the rotated axis: u = x * cos(θ) + y * sin(θ), where θ = straw_angle
        in radians. fiber = 0.5 + 0.5 * sin(2π * u / straw_period). Gate the
        overlay on pixel luminance: apply only where straw_lo ≤ lum ≤ straw_hi
        (Kiefer's straw rests on mid-tone surfaces, not in deep shadow or
        highlight). Blend fiber_strength of straw_color into the mid-lum pixels
        at each fiber peak (fiber > 0.55).
        NOVEL: (c) ROTATED SINGLE-DIRECTION CHROMATIC SINUSOIDAL FIBER TEXTURE
        GATED ON MID-LUMINANCE -- first pass to apply a tilted (non-orthogonal)
        single-direction sinusoidal fiber grid with warm chromatic coloring
        (straw gold) exclusively at mid-luminance pixels; paint_surface_tooth_pass
        (s252) uses an orthogonal H×V product for achromatic canvas texture;
        no prior pass applies a rotated single-axis sinusoidal fiber with
        chromatic hue blending gated on a mid-luminance band.

        n_zones        : Number of horizontal depth zones for ash gradient.
        ash_tone       : Target RGB colour for ashen blending (charcoal grey).
        max_ash_blend  : Maximum blend fraction at the topmost (horizon) zone.
        dark_push      : Extra luminance reduction for dark pixels in each zone.
        n_cracks       : Number of sinusoidal lead-crack trajectories.
        crack_width    : Pixel half-width of each crack vein.
        crack_depth    : Blend fraction toward crack_tone at crack centres.
        crack_tone     : Target RGB colour for crack darkening (near-black).
        lum_ceiling    : Luminance threshold above which cracks are suppressed.
        straw_angle    : Fiber direction in degrees from horizontal (0=horiz).
        straw_period   : Fiber repeat period in pixels.
        fiber_strength : Blend fraction of straw_color at fiber peaks.
        straw_lo       : Lower luminance bound for straw overlay zone.
        straw_hi       : Upper luminance bound for straw overlay zone.
        straw_color    : Warm straw-gold RGB for fiber overlay.
        opacity        : Final composite opacity.
        seed           : RNG seed for reproducible crack layout.
        \"\"\"
        import numpy as _np

        print("    Kiefer Scorched Earth pass (session 253, 164th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        rng = _np.random.default_rng(seed)

        # Working in float32 [0,1]
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        lum0 = (0.299 * r0 + 0.587 * g0 + 0.114 * b0)

        # Stage 1: Ashen field desaturation gradient
        ar, ag, ab = float(ash_tone[0]), float(ash_tone[1]), float(ash_tone[2])
        r1 = r0.copy()
        g1 = g0.copy()
        b1 = b0.copy()

        zone_h = h / float(n_zones)
        for zi in range(n_zones):
            # Zone 0 = bottom (foreground), zone n_zones-1 = top (horizon)
            # Flip so horizon gets max blend: high zi = higher y? No:
            # y=0 is top (sky/horizon), y=h-1 is bottom (foreground).
            # We want top zones (small y) to be more ashen.
            y_top = int(zi * zone_h)
            y_bot = int((zi + 1) * zone_h)
            y_bot = min(y_bot, h)
            # Zone fraction: 0 at bottom (foreground), 1 at top (horizon)
            denom = float(max(n_zones - 1, 1))
            zone_frac = (float(n_zones - 1 - zi) / denom) * float(max_ash_blend)

            lum_z = lum0[y_top:y_bot, :]
            r_z = r0[y_top:y_bot, :]
            g_z = g0[y_top:y_bot, :]
            b_z = b0[y_top:y_bot, :]

            # Luminance-gated blend weights
            dark_mask   = (lum_z < 0.35).astype(_np.float32)
            mid_mask    = ((lum_z >= 0.35) & (lum_z < 0.65)).astype(_np.float32)
            light_mask  = (lum_z >= 0.65).astype(_np.float32)

            w_dark  = zone_frac * dark_mask
            w_mid   = zone_frac * mid_mask
            w_light = zone_frac * 0.5 * light_mask

            blend = w_dark + w_mid + w_light

            # Blend toward ash
            r1[y_top:y_bot, :] = r_z * (1.0 - blend) + ar * blend
            g1[y_top:y_bot, :] = g_z * (1.0 - blend) + ag * blend
            b1[y_top:y_bot, :] = b_z * (1.0 - blend) + ab * blend

            # Extra dark push for dark pixels
            dp = float(dark_push) * dark_mask * zone_frac
            r1[y_top:y_bot, :] = _np.clip(r1[y_top:y_bot, :] - dp, 0.0, 1.0)
            g1[y_top:y_bot, :] = _np.clip(g1[y_top:y_bot, :] - dp, 0.0, 1.0)
            b1[y_top:y_bot, :] = _np.clip(b1[y_top:y_bot, :] - dp, 0.0, 1.0)

        # Stage 2: Lead sheet crack veining
        r2 = r1.copy()
        g2 = g1.copy()
        b2 = b1.copy()
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1)
        cr, cg, cb = float(crack_tone[0]), float(crack_tone[1]), float(crack_tone[2])
        cd = float(crack_depth)
        lc = float(lum_ceiling)
        cw = int(crack_width)

        xs = _np.arange(w, dtype=_np.float32)

        for _ in range(int(n_cracks)):
            amp   = float(rng.uniform(4.0, 28.0))
            freq  = float(rng.uniform(0.005, 0.020))
            phase = float(rng.uniform(0.0, 2.0 * _np.pi))
            y_orig = float(rng.uniform(0.1, 0.9)) * h

            # Crack y-coordinate per x
            crack_ys = y_orig + amp * _np.sin(2.0 * _np.pi * freq * xs + phase)
            crack_ys = _np.clip(_np.round(crack_ys).astype(_np.int32), 0, h - 1)

            for dy in range(-cw, cw + 1):
                ys_idx = _np.clip(crack_ys + dy, 0, h - 1)
                # Luminance gate: only darken dark/mid pixels
                lum_vals = lum1[ys_idx, xs.astype(_np.int32)]
                mask = (lum_vals < lc).astype(_np.float32)

                # Blend strength falls off with distance from crack centre
                dist_frac = 1.0 - abs(dy) / float(cw + 1)
                blend_c = cd * dist_frac * mask

                cols = xs.astype(_np.int32)
                r2[ys_idx, cols] = r2[ys_idx, cols] * (1.0 - blend_c) + cr * blend_c
                g2[ys_idx, cols] = g2[ys_idx, cols] * (1.0 - blend_c) + cg * blend_c
                b2[ys_idx, cols] = b2[ys_idx, cols] * (1.0 - blend_c) + cb * blend_c

        # Stage 3: Straw fiber warm overlay
        r3 = r2.copy()
        g3 = g2.copy()
        b3 = b2.copy()
        lum2 = (0.299 * r2 + 0.587 * g2 + 0.114 * b2)

        theta = float(straw_angle) * _np.pi / 180.0
        cos_t = float(_np.cos(theta))
        sin_t = float(_np.sin(theta))
        sp = float(straw_period)
        fs = float(fiber_strength)
        sr, sg, sb = float(straw_color[0]), float(straw_color[1]), float(straw_color[2])
        s_lo, s_hi = float(straw_lo), float(straw_hi)

        # Coordinate grids
        ys_grid, xs_grid = _np.mgrid[0:h, 0:w]
        u = xs_grid * cos_t + ys_grid * sin_t
        fiber = (0.5 + 0.5 * _np.sin(2.0 * _np.pi * u / sp)).astype(_np.float32)

        # Mask: mid-luminance AND fiber peak
        mid_lum_mask = ((lum2 >= s_lo) & (lum2 <= s_hi)).astype(_np.float32)
        fiber_peak   = (fiber > 0.55).astype(_np.float32)
        straw_mask   = mid_lum_mask * fiber_peak * fs

        r3 = _np.clip(r2 * (1.0 - straw_mask) + sr * straw_mask, 0.0, 1.0)
        g3 = _np.clip(g2 * (1.0 - straw_mask) + sg * straw_mask, 0.0, 1.0)
        b3 = _np.clip(b2 * (1.0 - straw_mask) + sb * straw_mask, 0.0, 1.0)

        # Final composite
        op = float(opacity)
        new_r = r0 * (1.0 - op) + r3 * op
        new_g = g0 * (1.0 - op) + g3 * op
        new_b = b0 * (1.0 - op) + b3 * op

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()
        straw_pixels = int((straw_mask > 0).sum())
        crack_coverage = float((r3 < r2 - 0.01).mean())
        print(f"    Scorched Earth complete (straw_pixels={straw_pixels}, "
              f"crack_coverage={crack_coverage:.4f})")
"""

IMPASTO_RIDGE_PASS = """
    def paint_impasto_ridge_cast_pass(
        self,
        edge_sensitivity: float = 0.55,
        shadow_offset:    int   = 4,
        shadow_strength:  float = 0.28,
        highlight_strength: float = 0.12,
        light_angle:      float = 135.0,
        ridge_threshold:  float = 0.08,
        opacity:          float = 0.75,
    ) -> None:
        r\"\"\"Impasto Ridge Cast Shadows -- session 253 improvement pass.

        THREE-STAGE IMPASTO DEPTH SIMULATION:

        Simulates the three-dimensional quality of thick impasto paint by
        detecting luminance-gradient ridge edges (where paint has been applied
        thickly) and synthesizing cast micro-shadows and catch-light highlights
        from those ridges based on a configurable light direction.

        Stage 1 RIDGE DETECTION: Compute the luminance image and apply a
        Sobel-like edge detection using horizontal and vertical finite
        differences. Compute gradient magnitude = sqrt(Gx^2 + Gy^2).
        Threshold at ridge_threshold * edge_sensitivity to isolate strong
        ridges that represent thick impasto edges. Scale ridge map to [0,1].
        NOVEL: (a) SOBEL-MAGNITUDE RIDGE MAP FOR IMPASTO DEPTH -- first pass
        to compute a Sobel-derived gradient magnitude map for the explicit
        purpose of identifying thick impasto ridges; no prior pass uses a
        gradient magnitude image as the source map for shadow and highlight
        synthesis (paint_lost_found_edges_pass modifies edge softness but does
        not synthesise 3D cast shadows from those edges; paint_aerial_perspective
        uses global-y luminance shifts rather than local edge topology).

        Stage 2 SHADOW CASTING: Compute the anti-light direction from
        light_angle (degrees from top, clockwise): shadow_dx = sin(angle),
        shadow_dy = cos(angle) (downward in image coords). For each pixel
        with ridge_map > ridge_threshold: write a darkening offset at
        (x + shadow_dx * shadow_offset, y + shadow_dy * shadow_offset),
        proportional to ridge_map * shadow_strength. Accumulate shadow
        contributions across all ridge pixels into a shadow buffer; apply
        shadow buffer as multiplicative darkening: pixel *= (1 - shadow_buf).
        NOVEL: (b) DIRECTIONAL SHADOW CAST FROM RIDGE TOPOLOGY -- first pass
        to compute directional cast-shadow displacement from a ridge map
        (pushing shadow pixels in the anti-light direction by shadow_offset
        pixels with ridge-proportional intensity); paint_sfumato_focus_pass
        and paint_split_toning apply global or region luminance shifts -- none
        displace a shadow specifically from detected ridge positions.

        Stage 3 HIGHLIGHT LEADING EDGE: Compute the light-facing direction
        opposite to the shadow: highlight_dx = -shadow_dx, highlight_dy =
        -shadow_dy. For each ridge pixel, write a brightening at
        (x + highlight_dx, y + highlight_dy) proportional to
        ridge_map * highlight_strength. Apply as additive luminance boost
        (clamped to 1.0). This creates the catch-light that makes impasto
        physically three-dimensional -- the bright edge where the paint ridge
        faces the light source.
        NOVEL: (c) CATCH-LIGHT HIGHLIGHT ON LIGHT-FACING RIDGE EDGE --
        first pass to apply an additive luminance highlight displaced in the
        light-facing direction from each ridge pixel; the highlight is paired
        with the shadow displacement as a complete light-source simulation from
        physical surface topology; paint_glaze_gradient_pass and paint_halation
        apply global luminance increases -- none compute per-ridge catch-lights
        at positions offset by the ridge-normal vs. light-direction projection.

        edge_sensitivity  : Multiplier for gradient threshold (higher = fewer ridges).
        shadow_offset     : Pixel distance of shadow cast in anti-light direction.
        shadow_strength   : Darkening magnitude at shadow centre (0–1).
        highlight_strength: Brightening magnitude at catch-light (0–1).
        light_angle       : Light source angle in degrees, clockwise from top.
        ridge_threshold   : Gradient magnitude threshold for ridge detection.
        opacity           : Final composite opacity (0=no change, 1=full effect).
        \"\"\"
        import numpy as _np

        print("    Impasto Ridge Cast pass (session 253 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        r0 = orig[:, :, 2].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0)

        # Stage 1: Ridge detection via finite-difference gradient magnitude
        # Horizontal gradient
        gx = _np.zeros_like(lum)
        gx[:, 1:-1] = lum[:, 2:] - lum[:, :-2]
        gx[:, 0] = lum[:, 1] - lum[:, 0]
        gx[:, -1] = lum[:, -1] - lum[:, -2]
        # Vertical gradient
        gy = _np.zeros_like(lum)
        gy[1:-1, :] = lum[2:, :] - lum[:-2, :]
        gy[0, :] = lum[1, :] - lum[0, :]
        gy[-1, :] = lum[-1, :] - lum[-2, :]

        grad_mag = _np.sqrt(gx ** 2 + gy ** 2).astype(_np.float32)
        thresh = float(ridge_threshold) * float(edge_sensitivity)
        ridge_map = _np.clip((grad_mag - thresh) / (1.0 - thresh + 1e-6), 0.0, 1.0)

        # Stage 2: Shadow casting
        ang_rad = float(light_angle) * _np.pi / 180.0
        # Anti-light direction (shadow falls away from light)
        sdx = int(round(float(_np.sin(ang_rad)) * float(shadow_offset)))
        sdy = int(round(float(_np.cos(ang_rad)) * float(shadow_offset)))

        shadow_buf = _np.zeros((h, w), dtype=_np.float32)
        src_y, src_x = _np.mgrid[0:h, 0:w]
        dst_y = _np.clip(src_y + sdy, 0, h - 1)
        dst_x = _np.clip(src_x + sdx, 0, w - 1)
        _np.add.at(shadow_buf, (dst_y, dst_x), ridge_map * float(shadow_strength))
        shadow_buf = _np.clip(shadow_buf, 0.0, 1.0)

        r1 = _np.clip(r0 * (1.0 - shadow_buf), 0.0, 1.0)
        g1 = _np.clip(g0 * (1.0 - shadow_buf), 0.0, 1.0)
        b1 = _np.clip(b0 * (1.0 - shadow_buf), 0.0, 1.0)

        # Stage 3: Highlight on light-facing ridge edge
        hdx = -sdx
        hdy = -sdy
        hl_buf = _np.zeros((h, w), dtype=_np.float32)
        dst_hy = _np.clip(src_y + hdy, 0, h - 1)
        dst_hx = _np.clip(src_x + hdx, 0, w - 1)
        _np.add.at(hl_buf, (dst_hy, dst_hx), ridge_map * float(highlight_strength))
        hl_buf = _np.clip(hl_buf, 0.0, 1.0)

        r2 = _np.clip(r1 + hl_buf, 0.0, 1.0)
        g2 = _np.clip(g1 + hl_buf, 0.0, 1.0)
        b2 = _np.clip(b1 + hl_buf, 0.0, 1.0)

        # Final composite
        op = float(opacity)
        new_r = r0 * (1.0 - op) + r2 * op
        new_g = g0 * (1.0 - op) + g2 * op
        new_b = b0 * (1.0 - op) + b2 * op

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()
        n_ridge = int((ridge_map > 0.05).sum())
        shadow_cov = float((shadow_buf > 0.01).mean())
        print(f"    Impasto Ridge Cast complete (ridge_pixels={n_ridge}, "
              f"shadow_coverage={shadow_cov:.4f})")
"""

ENGINE_FILE = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_FILE, "r", encoding="utf-8") as f:
    src = f.read()

assert "kiefer_scorched_earth_pass" not in src, \
    "kiefer_scorched_earth_pass already present in stroke_engine.py"
assert "paint_impasto_ridge_cast_pass" not in src, \
    "paint_impasto_ridge_cast_pass already present in stroke_engine.py"

# Insert both passes before paint_surface_tooth_pass (last improvement from s252)
ANCHOR = "    def paint_surface_tooth_pass("
assert ANCHOR in src, f"Anchor {ANCHOR!r} not found in stroke_engine.py"

new_src = src.replace(
    ANCHOR,
    SCORCHED_EARTH_PASS + "\n" + "    def paint_impasto_ridge_cast_pass(" +
    IMPASTO_RIDGE_PASS.split("    def paint_impasto_ridge_cast_pass(", 1)[1] +
    "\n" + ANCHOR
)

with open(ENGINE_FILE, "w", encoding="utf-8") as f:
    f.write(new_src)

print("kiefer_scorched_earth_pass and paint_impasto_ridge_cast_pass inserted into stroke_engine.py")
