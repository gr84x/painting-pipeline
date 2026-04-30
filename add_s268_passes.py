"""Insert paint_depth_atmosphere_pass (s268 improvement) and
zao_wou_ki_ink_atmosphere_pass (179th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_depth_atmosphere_pass (s268 improvement) ───────────────────

DEPTH_ATMOSPHERE_PASS = '''
    def paint_depth_atmosphere_pass(
        self,
        haze_color:       tuple = (0.76, 0.82, 0.92),
        depth_sigma:      float = 40.0,
        max_haze:         float = 0.35,
        vertical_weight:  float = 0.60,
        contrast_weight:  float = 0.40,
        contrast_radius:  float = 8.0,
        noise_seed:       int   = 268,
        opacity:          float = 0.75,
    ) -> None:
        r"""Depth Atmosphere (Aerial Perspective) -- session 268 improvement.

        AERIAL PERSPECTIVE SIMULATION INSPIRED BY THE CLASSICAL OIL PAINTING
        PRINCIPLE CODIFIED BY LEONARDO DA VINCI (c. 1490s) AND CENTRAL TO
        WESTERN LANDSCAPE PAINTING FROM CLAUDE LORRAIN TO J.M.W. TURNER:

        Aerial perspective (also called atmospheric perspective) is the optical
        phenomenon by which distant objects appear lighter, cooler in hue
        (shifted toward blue-grey), lower in contrast, and softer in edge
        definition as a result of the scattering of light by the intervening
        atmosphere. Leonardo described it in the Treatise on Painting: objects
        at a distance lose their warm colours and their sharp edges, taking on
        the blue of the air between them and the eye. Turner's late paintings
        exploit this principle to dissolve distant forms into luminous haze
        while keeping foreground elements vivid and warm. Corot systematically
        greys and lightens his backgrounds as they recede. Chinese ink painting
        uses kongyun (empty cloud) to represent distant mountain peaks dissolved
        into white mist -- atmospheric perspective has been a cross-cultural
        universal of landscape painting for millennia.

        The implementation estimates a SPATIAL DEPTH MAP from two independent
        signals: (1) the vertical position in the canvas (higher in the picture
        plane conventionally indicates greater distance in landscape convention),
        and (2) the local contrast at each pixel (low local contrast indicates
        smooth, textureless distant passages; high local contrast indicates
        detailed, close-range material). These are linearly combined into a
        composite depth estimate, smoothed with a large Gaussian to avoid harsh
        boundaries, and used to linearly blend each pixel toward a cool haze
        color. The result simulates the cumulative blue scattering of
        atmospheric depth without requiring a geometric 3D model.

        Stage 1 VERTICAL DEPTH SIGNAL: Build a vertical gradient y_depth[y, x]
        = y / (H-1) that increases linearly from 0.0 at the bottom (near
        foreground) to 1.0 at the top (far background). This encodes the
        landscape convention that higher pixels represent greater distance.
        NOVEL: (a) VERTICAL POSITION AS DEPTH PROXY -- no prior pass uses
        canvas vertical position as a spatial depth signal; paint_atmospheric_
        recession_pass (s237) applies a fixed vertical gradient desaturation
        based on canvas-height fractions with hard threshold zones, not a
        smooth blended depth map computed from multiple cues; this pass
        constructs a continuous gradient, not a zonally-thresholded function,
        and combines it with a second independent signal (local contrast).

        Stage 2 LOCAL CONTRAST DEPTH SIGNAL: Compute the luminance image L.
        For each pixel, compute the local mean luminance using a Gaussian blur
        at sigma=contrast_radius, and the local standard deviation from
        sqrt(gaussian(L^2) - gaussian(L)^2). Normalise: low local std = distant
        (depth signal = 1), high local std = close (depth signal = 0). This
        contrast_depth signal detects smooth distant sky and mist passages
        versus textured close-range grass, bark, or stone.
        NOVEL: (b) LOCAL CONTRAST AS A DISTANCE SIGNAL FUSED WITH VERTICAL
        POSITION -- no prior pass computes per-pixel local standard deviation
        to estimate scene depth; this is a signal-processing approach to
        scene depth estimation without any 3D model; local std falls naturally
        in aerial-hazed distant regions because atmospheric blurring removes
        fine-scale texture detail, making the depth signal self-consistent with
        the optical physics of aerial perspective.

        Stage 3 COMPOSITE DEPTH MAP: Blend the two signals:
          depth = vertical_weight * y_depth + contrast_weight * contrast_depth
        Apply Gaussian smoothing at sigma=depth_sigma to suppress edges and
        produce a spatially-smooth transition. Clamp to [0, 1].

        Stage 4 ATMOSPHERIC HAZE BLEND: For each pixel:
          haze_amount = depth * max_haze
          new_r = r * (1 - haze_amount) + haze_r * haze_amount
          new_g = g * (1 - haze_amount) + haze_g * haze_amount
          new_b = b * (1 - haze_amount) + haze_b * haze_amount
        where (haze_r, haze_g, haze_b) is the haze_color (default: cool
        blue-grey 0.76/0.82/0.92, approximating clear-sky atmospheric blue).
        This shift simultaneously lightens dark distant passages, cools warm
        colours, and reduces saturation -- the three perceptual signatures of
        aerial perspective.
        NOVEL: (c) PER-PIXEL MULTI-CUE DEPTH-WEIGHTED LINEAR HAZE BLEND --
        all prior passes that affect distant regions do so with fixed vertical
        zones (atmospheric_recession_pass: three fixed bands at canvas thirds)
        or global operators (sfumato_contour_dissolution: edge softening via
        gradient-magnitude gate, no distance cue). This pass is the first to
        compute a continuous per-pixel depth field from two spatial signals
        (vertical position + local contrast), smooth it to a coherent depth map,
        and use it to control a linear haze blend per pixel -- producing a
        smooth, form-following aerial recession that adapts to any composition.
        """
        print("    Depth Atmosphere (Aerial Perspective) pass (session 268 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Vertical Depth Signal ────────────────────────────────────
        y_idx = _np.arange(h, dtype=_np.float32)
        y_norm = y_idx / max(float(h - 1), 1.0)
        # y=0 is the TOP (far/sky); depth increases toward top, so invert y_norm
        y_depth = _np.tile((1.0 - y_norm)[:, _np.newaxis], (1, w)).astype(_np.float32)

        # ── Stage 2: Local Contrast Depth Signal ──────────────────────────────
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        cr = max(float(contrast_radius), 0.5)
        lum_mean = _gf(lum, sigma=cr).astype(_np.float32)
        lum2_mean = _gf(lum ** 2, sigma=cr).astype(_np.float32)
        local_var = _np.maximum(lum2_mean - lum_mean ** 2, 0.0).astype(_np.float32)
        local_std = _np.sqrt(local_var).astype(_np.float32)
        std_max = float(local_std.max()) + 1e-6
        contrast_depth = _np.clip(1.0 - local_std / std_max, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Composite Depth Map ──────────────────────────────────────
        vw = float(vertical_weight)
        cw = float(contrast_weight)
        depth = (vw * y_depth + cw * contrast_depth).astype(_np.float32)
        ds = max(float(depth_sigma), 0.5)
        depth = _gf(depth, sigma=ds).astype(_np.float32)
        depth = _np.clip(depth, 0.0, 1.0).astype(_np.float32)

        # ── Stage 4: Atmospheric Haze Blend ───────────────────────────────────
        hr, hg, hb = float(haze_color[0]), float(haze_color[1]), float(haze_color[2])
        mh = float(max_haze)
        haze_amt = (depth * mh).astype(_np.float32)

        new_r = (r0 * (1.0 - haze_amt) + hr * haze_amt).astype(_np.float32)
        new_g = (g0 * (1.0 - haze_amt) + hg * haze_amt).astype(_np.float32)
        new_b = (b0 * (1.0 - haze_amt) + hb * haze_amt).astype(_np.float32)

        new_r = _np.clip(new_r, 0.0, 1.0)
        new_g = _np.clip(new_g, 0.0, 1.0)
        new_b = _np.clip(new_b, 0.0, 1.0)

        # ── Composite at opacity ───────────────────────────────────────────────
        op = float(opacity)
        final_r = r0 * (1.0 - op) + new_r * op
        final_g = g0 * (1.0 - op) + new_g * op
        final_b = b0 * (1.0 - op) + new_b * op

        hazed_px = int((haze_amt > 0.05).sum())

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(final_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(final_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(final_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        print(f"    Depth Atmosphere complete (hazed_px={hazed_px})")
'''

# ── Pass 2: zao_wou_ki_ink_atmosphere_pass (179th mode) ──────────────────────

ZAO_WOU_KI_PASS = '''
    def zao_wou_ki_ink_atmosphere_pass(
        self,
        glow_sigma:         float = 0.18,
        glow_strength:      float = 0.26,
        vignette_strength:  float = 0.40,
        vignette_color:     tuple = (0.04, 0.06, 0.14),
        warm_boost:         float = 0.16,
        cool_shift:         float = 0.14,
        ink_n_strokes:      int   = 28,
        ink_length_frac:    float = 0.22,
        ink_width:          float = 2.8,
        ink_opacity:        float = 0.55,
        noise_seed:         int   = 268,
        opacity:            float = 0.82,
    ) -> None:
        r"""Zao Wou-Ki Ink Atmosphere -- session 268, 179th distinct mode.

        FOUR-STAGE LYRICAL ABSTRACTION TECHNIQUE INSPIRED BY ZAO WOU-KI\'S
        PAINTING PRACTICE (c.1954-2013):

        Zao Wou-Ki (Zhao Wuji, 1920-2013) was a Chinese-French painter who
        synthesised the spatial philosophy of Song Dynasty ink painting
        (shanshui -- mountain-water landscape) with the chromatic ambition of
        Western Abstract Expressionism, developing a distinctive pictorial
        language that has no direct precedent in either tradition. Born in
        Beijing into an educated family with access to classical Chinese art,
        he trained at the Hangzhou Academy under Lin Fengmian, absorbing the
        ink painting tradition\'s treatment of empty space (xu -- the void) as
        an active pictorial element. He arrived in Paris in 1948 and absorbed
        Cézanne, Klee, Matisse, and later de Kooning -- but his essential
        innovation was not to synthesise these influences but to find that the
        fundamental concern of Chinese ink painting (the energy-relationship
        between mark and void) was identical to the fundamental concern of
        American Abstract Expressionism (the gestural field and its atmospheric
        ground). This identity, not synthesis, is the source of his originality.

        His mature paintings (from the mid-1950s onward) are organised around a
        single structural principle: a LUMINOUS CENTER surrounded by dark,
        calligraphically-marked peripheral zones. The center is not simply
        bright -- it is a zone of warm, golden, almost blinding light, as though
        a furnace or sun or spiritual presence radiates from the interior of the
        canvas. The periphery is not simply dark -- it is a zone of deep blue-
        black or indigo where ink-like gestural marks (jottings, curves, sweeping
        arcs) carry the calligraphic energy of the hand while remaining
        fundamentally abstract. Between center and edge, colour temperature
        shifts are extreme: warm orange-gold in the luminous core, cool blue-
        violet in the outer dark zone, with a narrow transitional band where
        warm and cool clash and create chromatic complexity.

        The composition has no horizon, no named forms, no narrative -- yet the
        eye reads it immediately as a landscape: the luminous center as sky or
        sun or distant valley light, the dark marks as mountain, rock, forest,
        or storm. This landscape reading arises entirely from the structural
        logic of the luminous-center / dark-periphery architecture, not from
        any depicted form. Zao called his paintings "windows onto the imaginary"
        -- the frame opens onto a felt rather than depicted space.

        Stage 1 LUMINOUS CENTER DETECTION AND RADIAL GLOW AMPLIFICATION:
        Compute the luminance L of the canvas. Smooth L with a wide Gaussian at
        sigma = glow_sigma * min(H, W) (expressed as a fraction of canvas size).
        Find the peak location (cy_peak, cx_peak) of the smoothed luminance --
        this is the detected luminous center. Build a radial proximity map:
          center_dist[y, x] = sqrt(((y-cy_peak)/H)^2 + ((x-cx_peak)/W)^2)
          radial_glow = exp(-center_dist^2 / (glow_sigma^2 * 2))
        Apply the glow as a luminance lift:
          glow_lift = radial_glow * glow_strength
          r_glow = clip(r0 + glow_lift * (1 - r0), 0, 1)  (lifts toward white)
          g_glow = clip(g0 + glow_lift * (1 - g0), 0, 1)
          b_glow = clip(b0 + glow_lift * (1 - b0), 0, 1)  (cools less than warm)
        NOVEL: (a) CANVAS-WIDE LUMINOUS CENTER DETECTION VIA SMOOTHED LUMINANCE
        PEAK, FOLLOWED BY CONTENT-ALIGNED RADIAL BRIGHTENING -- first pass to
        locate the brightest region of the PAINTED CANVAS (not a fixed point)
        and amplify it with a content-aligned radial field; prior passes with
        radial operators use fixed centers (canvas center, fixed fraction of
        canvas size); this pass reads the actual painted luminance distribution
        and reinforces the existing compositional light source, making the glow
        a signal-amplifying operation rather than an imposed geometry.

        Stage 2 DARK PERIPHERAL VIGNETTE:
        Using the same center_dist map:
          vignette_weight = center_dist^1.5 (non-linear: rapid darkening past midfield)
          vignette_weight = clip(vignette_weight / vignette_weight.max(), 0, 1)
          new_r = r_glow * (1 - vignette_strength * vignette_weight) + vc_r * vignette_strength * vignette_weight
          (similarly for g, b, using vignette_color = deep blue-black (0.04/0.06/0.14))
        NOVEL: (b) CONTENT-ALIGNED NON-LINEAR PERIPHERAL VIGNETTE TOWARD DEEP
        BLUE-BLACK, CENTERED ON THE DETECTED LUMINOUS PEAK -- all prior vignette
        operators in the engine use the CANVAS CENTER as the vignette center and
        apply a fixed power-law or Gaussian falloff; this pass centers the
        vignette on the DETECTED LUMINOUS PEAK (which may be anywhere in the
        canvas), creating an asymmetric vignette that reinforces the existing
        spatial asymmetry of the composition; the blue-black target color models
        Zao\'s peripheral indigo-black zones, not generic dark grey.

        Stage 3 DUAL THERMAL COLOR FIELD (WARM CENTER, COOL PERIPHERY):
        Compute final luminance L_post from stage-2 result.
        In bright regions (L_post > 0.55): shift hue toward warm gold:
          hue_delta_warm = +warm_boost * (L_post - 0.55) / 0.45  (scaled by excess lum)
        In dark regions (L_post < 0.35): shift hue toward cool blue-indigo:
          hue_delta_cool = -cool_shift * (0.35 - L_post) / 0.35  (scaled by depth)
        Apply HSV hue rotation at those zones only.
        NOVEL: (c) LUMINANCE-ZONED DUAL THERMAL HUE SHIFT WITH VARIABLE
        MAGNITUDE -- first pass to apply OPPOSITE hue rotations to bright and
        dark zones in the same operation, with the rotation magnitude scaled
        continuously by how bright or dark the pixel is (not a binary gate);
        paint_edge_temperature_pass applies a single warm/cool split at edges
        (not at luminance zones, not dual-direction, not scaled by luminance
        depth); paint_warm_cool_separation_pass applies fixed warm/cool shifts
        in fixed screen halves (not luminance-guided, not scaled by tonal depth);
        this pass creates the characteristic Zao Wou-Ki THERMAL FIELD where
        the color temperature gradient runs from warm gold at the luminous center
        through neutral mid-tones to deep blue-indigo at the dark periphery.

        Stage 4 INK CALLIGRAPHIC STREAK SYNTHESIS:
        Generate ink_n_strokes gestural ink marks in the outer zone of the
        canvas (distance from center_peak > 0.20 * min(H, W)). Each mark:
          a. Random anchor point in the peripheral zone
          b. Direction approximately tangential to the radial field from center
             (angle = atan2(anchor_y - cy_peak, anchor_x - cx_peak) + pi/2 + noise)
             with angular noise ~ Uniform(-35°, +35°)
          c. Length = ink_length_frac * min(H, W) * Uniform(0.5, 1.4)
          d. Rendered as a Gaussian-blurred line (sigma=ink_width/2) with dark
             blue-black ink color, blended at ink_opacity
        This creates the calligraphic peripheral marks that carry the gestural
        energy of Zao\'s ink-painting heritage in the outer dark zone.
        NOVEL: (d) CONTENT-ALIGNED TANGENTIAL INK STROKE PLACEMENT IN THE
        PERIPHERAL ZONE -- all prior calligraphic/gestural passes (twombly_
        calligraphic_scrawl_pass: random clusters across whole canvas; mitchell_
        gestural_arc_pass: content-detected arcs at edge boundaries; kline_
        gestural_slash_pass: large diagonal slashes at detected major axis)
        place marks based on content edges or randomly; this pass places marks
        specifically in the PERIPHERAL ZONE (beyond a radial threshold from the
        luminous center) and orients them TANGENTIALLY to the radial field,
        generating the circling, orbiting quality of Zao\'s peripheral
        calligraphic marks that spiral around the luminous interior.
        """
        print("    Zao Wou-Ki Ink Atmosphere pass (session 268, 179th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf
        from PIL import Image as _Image, ImageDraw as _ImageDraw

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        rng = _np.random.default_rng(int(noise_seed))

        # ── Stage 1: Luminous Center Detection and Radial Glow ────────────────
        lum0 = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        glow_sigma_px = max(float(glow_sigma) * float(min(h, w)), 4.0)
        lum_smooth = _gf(lum0, sigma=glow_sigma_px).astype(_np.float32)

        peak_idx = int(_np.argmax(lum_smooth))
        cy_peak = float(peak_idx // w)
        cx_peak = float(peak_idx % w)

        Y_grid, X_grid = _np.mgrid[0:h, 0:w]
        cy_n = cy_peak / float(max(h - 1, 1))
        cx_n = cx_peak / float(max(w - 1, 1))
        y_n = Y_grid.astype(_np.float32) / float(max(h - 1, 1))
        x_n = X_grid.astype(_np.float32) / float(max(w - 1, 1))
        center_dist = _np.sqrt((y_n - cy_n) ** 2 + (x_n - cx_n) ** 2).astype(_np.float32)

        gs = float(glow_sigma)
        radial_glow = _np.exp(-center_dist ** 2 / (2.0 * gs ** 2)).astype(_np.float32)
        glow_lift = (radial_glow * float(glow_strength)).astype(_np.float32)

        r_g = _np.clip(r0 + glow_lift * (1.0 - r0), 0.0, 1.0).astype(_np.float32)
        g_g = _np.clip(g0 + glow_lift * (1.0 - g0), 0.0, 1.0).astype(_np.float32)
        b_g = _np.clip(b0 + glow_lift * (1.0 - b0) * 0.7, 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Dark Peripheral Vignette ─────────────────────────────────
        vc_r, vc_g, vc_b = (float(vignette_color[0]),
                             float(vignette_color[1]),
                             float(vignette_color[2]))
        cd_max = float(center_dist.max()) + 1e-6
        vw = _np.clip((center_dist ** 1.5) / (cd_max ** 1.5), 0.0, 1.0).astype(_np.float32)
        vs = float(vignette_strength)

        r_v = (r_g * (1.0 - vs * vw) + vc_r * vs * vw).astype(_np.float32)
        g_v = (g_g * (1.0 - vs * vw) + vc_g * vs * vw).astype(_np.float32)
        b_v = (b_g * (1.0 - vs * vw) + vc_b * vs * vw).astype(_np.float32)
        r_v = _np.clip(r_v, 0.0, 1.0).astype(_np.float32)
        g_v = _np.clip(g_v, 0.0, 1.0).astype(_np.float32)
        b_v = _np.clip(b_v, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Dual Thermal Color Field ─────────────────────────────────
        lum1 = (0.299 * r_v + 0.587 * g_v + 0.114 * b_v).astype(_np.float32)

        # HSV decomposition helper
        def _rgb_to_hsv(r, g, b):
            mx = _np.maximum(_np.maximum(r, g), b)
            mn = _np.minimum(_np.minimum(r, g), b)
            delta = mx - mn
            val = mx.copy()
            sat = _np.where(mx > 1e-6, delta / (mx + 1e-6), 0.0).astype(_np.float32)
            hue = _np.zeros_like(r)
            m = delta > 1e-6
            if m.any():
                rr2 = r[m]; gg2 = g[m]; bb2 = b[m]
                dd2 = delta[m]; mx2 = mx[m]
                is_r = (mx2 == rr2)
                is_g = (mx2 == gg2) & ~is_r
                hr2 = ((gg2 - bb2) / dd2) % 6.0
                hg2 = (bb2 - rr2) / dd2 + 2.0
                hb2 = (rr2 - gg2) / dd2 + 4.0
                hue[m] = _np.where(is_r, hr2, _np.where(is_g, hg2, hb2)) / 6.0
            return hue, sat, val

        def _hsv_to_rgb(hue, sat, val):
            h6 = (hue * 6.0).astype(_np.float32)
            i_a = h6.astype(_np.int32) % 6
            f_a = (h6 - _np.floor(h6)).astype(_np.float32)
            p_a = (val * (1.0 - sat)).astype(_np.float32)
            q_a = (val * (1.0 - sat * f_a)).astype(_np.float32)
            t_a = (val * (1.0 - sat * (1.0 - f_a))).astype(_np.float32)
            out_r = _np.select([i_a==0,i_a==1,i_a==2,i_a==3,i_a==4,i_a==5],
                               [val,q_a,p_a,p_a,t_a,val]).astype(_np.float32)
            out_g = _np.select([i_a==0,i_a==1,i_a==2,i_a==3,i_a==4,i_a==5],
                               [t_a,val,val,q_a,p_a,p_a]).astype(_np.float32)
            out_b = _np.select([i_a==0,i_a==1,i_a==2,i_a==3,i_a==4,i_a==5],
                               [p_a,p_a,t_a,val,val,q_a]).astype(_np.float32)
            return (
                _np.clip(out_r, 0.0, 1.0),
                _np.clip(out_g, 0.0, 1.0),
                _np.clip(out_b, 0.0, 1.0),
            )

        hue_v, sat_v, val_v = _rgb_to_hsv(r_v, g_v, b_v)

        # Warm zone (bright): hue shift toward gold (hue ~0.10)
        warm_thr = 0.55
        warm_mask = lum1 > warm_thr
        warm_mag = (_np.clip((lum1 - warm_thr) / max(1.0 - warm_thr, 1e-4),
                             0.0, 1.0) * float(warm_boost)).astype(_np.float32)
        # Shift hue toward ~0.10 (gold/orange)
        gold_target = 0.10
        hue_warm_delta = ((gold_target - hue_v) * warm_mag * warm_mask.astype(_np.float32))

        # Cool zone (dark): hue shift toward blue-indigo (hue ~0.67)
        cool_thr = 0.35
        cool_mask = lum1 < cool_thr
        cool_mag = (_np.clip((cool_thr - lum1) / max(cool_thr, 1e-4),
                             0.0, 1.0) * float(cool_shift)).astype(_np.float32)
        indigo_target = 0.67
        hue_cool_delta = ((indigo_target - hue_v) * cool_mag * cool_mask.astype(_np.float32))

        new_hue = _np.clip(hue_v + hue_warm_delta + hue_cool_delta, 0.0, 1.0).astype(_np.float32)
        r_t, g_t, b_t = _hsv_to_rgb(new_hue, sat_v, val_v)

        # ── Stage 4: Ink Calligraphic Streak Synthesis ────────────────────────
        # Render ink strokes onto a float32 RGBA accumulator
        ink_acc_r = r_t.copy()
        ink_acc_g = g_t.copy()
        ink_acc_b = b_t.copy()

        ink_r_val, ink_g_val, ink_b_val = 0.04, 0.06, 0.14  # deep blue-black ink
        ink_op = float(ink_opacity)
        peripheral_radius = 0.20
        min_dim = float(min(h, w))
        length_base = float(ink_length_frac) * min_dim
        iw = max(float(ink_width), 0.5)
        sigma_line = iw / 2.0

        for _ in range(int(ink_n_strokes)):
            # Sample anchor in peripheral zone
            for _attempt in range(80):
                ay = int(rng.integers(0, h))
                ax = int(rng.integers(0, w))
                d = center_dist[ay, ax]
                if d > peripheral_radius:
                    break
            # Direction: tangential to radial field + noise
            base_angle = _np.arctan2(float(ay) - cy_peak, float(ax) - cx_peak) + _np.pi / 2.0
            noise_angle = rng.uniform(-35.0, 35.0) * _np.pi / 180.0
            angle = base_angle + noise_angle
            length = length_base * float(rng.uniform(0.5, 1.4))

            x0_f = ax - _np.cos(angle) * length / 2.0
            y0_f = ay - _np.sin(angle) * length / 2.0
            x1_f = ax + _np.cos(angle) * length / 2.0
            y1_f = ay + _np.sin(angle) * length / 2.0

            # Rasterise as anti-aliased line via distance-to-segment
            # Clip bounding box
            bx0 = max(0, int(min(x0_f, x1_f) - iw * 3))
            bx1 = min(w, int(max(x0_f, x1_f) + iw * 3) + 1)
            by0 = max(0, int(min(y0_f, y1_f) - iw * 3))
            by1 = min(h, int(max(y0_f, y1_f) + iw * 3) + 1)
            if bx1 <= bx0 or by1 <= by0:
                continue

            patch_Y, patch_X = _np.mgrid[by0:by1, bx0:bx1]
            pY = patch_Y.astype(_np.float32)
            pX = patch_X.astype(_np.float32)

            dx = float(x1_f - x0_f); dy = float(y1_f - y0_f)
            seg_len2 = dx * dx + dy * dy
            if seg_len2 < 1.0:
                continue
            t = _np.clip(
                ((pX - x0_f) * dx + (pY - y0_f) * dy) / seg_len2,
                0.0, 1.0
            )
            proj_x = x0_f + t * dx
            proj_y = y0_f + t * dy
            dist2 = (pX - proj_x) ** 2 + (pY - proj_y) ** 2
            line_alpha = _np.exp(-dist2 / (2.0 * sigma_line ** 2)) * ink_op

            ink_acc_r[by0:by1, bx0:bx1] = _np.clip(
                ink_acc_r[by0:by1, bx0:bx1] * (1.0 - line_alpha) + ink_r_val * line_alpha,
                0.0, 1.0
            )
            ink_acc_g[by0:by1, bx0:bx1] = _np.clip(
                ink_acc_g[by0:by1, bx0:bx1] * (1.0 - line_alpha) + ink_g_val * line_alpha,
                0.0, 1.0
            )
            ink_acc_b[by0:by1, bx0:bx1] = _np.clip(
                ink_acc_b[by0:by1, bx0:bx1] * (1.0 - line_alpha) + ink_b_val * line_alpha,
                0.0, 1.0
            )

        # ── Composite at opacity ───────────────────────────────────────────────
        op = float(opacity)
        final_r = (r0 * (1.0 - op) + ink_acc_r * op).astype(_np.float32)
        final_g = (g0 * (1.0 - op) + ink_acc_g * op).astype(_np.float32)
        final_b = (b0 * (1.0 - op) + ink_acc_b * op).astype(_np.float32)
        final_r = _np.clip(final_r, 0.0, 1.0)
        final_g = _np.clip(final_g, 0.0, 1.0)
        final_b = _np.clip(final_b, 0.0, 1.0)

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(final_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(final_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(final_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        print(f"    Zao Wou-Ki Ink Atmosphere complete "
              f"(center=({int(cx_peak)},{int(cy_peak)}), "
              f"strokes={int(ink_n_strokes)})")
'''

# ── Inject into stroke_engine.py ──────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

already_depth = "paint_depth_atmosphere_pass" in src
already_zao   = "zao_wou_ki_ink_atmosphere_pass" in src

if already_depth and already_zao:
    print("Both passes already present in stroke_engine.py -- nothing to do.")
    sys.exit(0)

additions = ""
if not already_depth:
    additions += DEPTH_ATMOSPHERE_PASS
if not already_zao:
    additions += "\n" + ZAO_WOU_KI_PASS

src = src.rstrip("\n") + "\n" + additions + "\n"

with open(ENGINE_PATH, "w", encoding="utf-8") as f:
    f.write(src)

if not already_depth:
    print("Inserted paint_depth_atmosphere_pass into stroke_engine.py.")
if not already_zao:
    print("Inserted zao_wou_ki_ink_atmosphere_pass into stroke_engine.py.")
