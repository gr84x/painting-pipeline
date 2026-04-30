"""Insert rysselberghe_chromatic_dot_field_pass and paint_atmospheric_recession_pass
into stroke_engine.py (session 259).

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: rysselberghe_chromatic_dot_field_pass ─────────────────────────────

RYSSELBERGHE_PASS = """
    def rysselberghe_chromatic_dot_field_pass(
        self,
        spectral_boost:       float = 0.35,
        luminosity_gain:      float = 0.18,
        luminosity_threshold: float = 0.42,
        dot_spacing:          int   = 8,
        dot_jitter:           float = 0.30,
        dot_sigma:            float = 1.8,
        dot_amplitude:        float = 0.04,
        noise_seed:           int   = 259,
        opacity:              float = 0.72,
    ) -> None:
        r\"\"\"Théo van Rysselberghe Chromatic Dot Field -- session 259, 170th distinct mode.

        THREE-STAGE NEO-IMPRESSIONIST POINTILLIST CHROMATIC FIELD EFFECT
        INSPIRED BY VAN RYSSELBERGHE'S DIVISIONIST TECHNIQUE (1890-1926):

        Théo van Rysselberghe (1862-1926) was the leading Belgian practitioner of
        Neo-Impressionist Divisionism.  His method: apply pigment as discrete units
        of near-pure spectral colour, trusting the eye to mix them optically at
        viewing distance.  Optical mixture yields higher apparent luminosity than
        physical mixing because subtractive pigment mixing absorbs light while
        adjacent pure-hue dots combine additively in the eye.  The systematic dot
        application creates a fine all-over surface vibration and a chromatic
        intensity no blended technique can achieve.  The three stages below model
        the perceptual and physical phenomena of this approach.

        Stage 1 SPECTRAL HUE SATURATION BOOST: Convert each pixel to HSV.  For each
        pixel's hue angle h (0-1 representing 0-360°), compute its angular distance
        to the nearest spectral primary:
          primaries = [0.0, 1/6, 2/6, 3/6, 4/6, 5/6]  (red, yellow, green, cyan, blue, violet)
          d = min over primaries: | h - p | (angular, wrap-around)
          boost_s = spectral_boost * (1 - 2*d/primary_spacing)  (zero at mid-point between primaries)
          s_new = clip(s + boost_s, 0, 1)
        This sharpens the chromatic identity of each pixel by pushing its hue toward
        the nearest pure spectral primary -- modelling the pointillist practice of
        selecting pure unmixed pigment for each dot rather than blending toward an
        intermediate hue.
        NOVEL: (a) HUE-ANGLE-DEPENDENT SATURATION PUSH TOWARD NEAREST SPECTRAL PRIMARY
        AS A MODEL OF PURE-PIGMENT DOT COLOUR SELECTION -- first pass to compute
        angular proximity to spectral primaries and scale saturation boost proportionally;
        paint_granulation_pass (s258) adjusts saturation indirectly via luminance scaling;
        no prior pass uses each pixel's angular distance to the nearest spectral primary
        to drive a proportional saturation amplification.

        Stage 2 OPTICAL LUMINOSITY ENHANCEMENT: Neo-Impressionist optical colour
        mixing produces a glow not achievable through physical pigment blending.
        Simulate this with a saturation-gated luminance lift:
          sat_excess = max(0, s_new - luminosity_threshold)
          lum_lift = luminosity_gain * sat_excess / (1 - luminosity_threshold + 1e-6)
          lum_new = clip(lum + lum_lift, 0, 1)
          scale = lum_new / (lum + 1e-6)
          R *= scale, G *= scale, B *= scale
        Highly saturated pixels (pure chromatic dots) are brightened; near-grey
        pixels are unaffected.  This approximates the luminous shimmer of pure-pigment
        dot fields in Mediterranean sunlight.
        NOVEL: (b) SATURATION-GATED LUMINANCE LIFT AS A MODEL OF OPTICAL COLOUR
        MIXING LUMINOSITY GAIN IN NEO-IMPRESSIONISM -- first pass to use each pixel's
        own saturation (after the hue boost) as the gate for a luminance enhancement
        operation; paint_tonal_key_pass (s255) shifts overall key via histogram
        percentile; no prior pass uses per-pixel saturation as the explicit gate
        and scaling input for a luminance boost modelling Neo-Impressionist optical mixing.

        Stage 3 DOT FIELD TEXTURE: Generate a perturbed regular grid of dot centres
        (spacing = dot_spacing pixels, each centre jittered by ±dot_jitter * dot_spacing
        in x and y using the noise_seed RNG).  At each dot centre (cx, cy) stamp a
        2D Gaussian luminance bump of amplitude ±dot_amplitude (alternating sign
        on a checkerboard pattern: sign = (-1)^(i+j) where i,j are grid indices,
        so adjacent dots are light and dark, giving the micro-contrast of discrete
        paint marks on a textured ground):
          bump[row, col] = dot_amplitude * sign * exp(-((row-cy)^2 + (col-cx)^2)
                           / (2 * dot_sigma^2))
        Apply as luminance modulation: lum_dot = lum_prev + bump_field; scale RGB.
        NOVEL: (c) SPATIALLY-PERIODIC JITTERED GRID OF GAUSSIAN-PROFILE LUMINANCE
        BUMPS WITH ALTERNATING SIGN CHECKERBOARD AS A PAINT-MARK DISCRETISATION
        TEXTURE -- first pass to stamp a fresh spatial dot grid (with alternating
        light/dark bumps) onto the canvas as luminance micro-modulation independently
        of the existing paint texture; paint_granulation_pass (s258) decomposes the
        existing canvas texture via frequency decomposition; no prior pass generates
        a new spatial dot grid and stamps Gaussian-profile bumps with alternating
        checkerboard sign pattern as an independent texture layer.

        spectral_boost       : Max saturation increase toward nearest spectral primary (0-1).
        luminosity_gain      : Max luminance lift for fully saturated pixels (0-1).
        luminosity_threshold : Saturation threshold below which no luminance boost (0-1).
        dot_spacing          : Grid spacing in pixels for dot centres.
        dot_jitter           : Fraction of dot_spacing for random centre displacement (0-1).
        dot_sigma            : Gaussian sigma for each dot bump in pixels.
        dot_amplitude        : Max luminance delta per dot bump (± this value).
        noise_seed           : RNG seed for dot centre jitter.
        opacity              : Final composite opacity.
        \"\"\"
        import numpy as _np

        print("    Rysselberghe Chromatic Dot Field pass (session 259, 170th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        # Cairo BGRA ordering
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Spectral Hue Saturation Boost (HSV-space) ────────────────
        cmax = _np.maximum(_np.maximum(r0, g0), b0)
        cmin = _np.minimum(_np.minimum(r0, g0), b0)
        delta = (cmax - cmin).astype(_np.float32)
        v = cmax.copy()
        s = _np.where(cmax > 1e-6, delta / (cmax + 1e-8), 0.0).astype(_np.float32)

        eps = 1e-8
        hue = _np.zeros((h, w), dtype=_np.float32)
        m_r = (cmax == r0) & (delta > eps)
        m_g = (cmax == g0) & (delta > eps)
        m_b = (cmax == b0) & (delta > eps)
        hue[m_r] = (((g0[m_r] - b0[m_r]) / (delta[m_r] + eps)) % 6.0) / 6.0
        hue[m_g] = (((b0[m_g] - r0[m_g]) / (delta[m_g] + eps)) + 2.0) / 6.0
        hue[m_b] = (((r0[m_b] - g0[m_b]) / (delta[m_b] + eps)) + 4.0) / 6.0
        hue = _np.clip(hue, 0.0, 1.0)

        # Six spectral primaries evenly spaced in [0, 1) hue circle
        primaries = _np.array([0.0, 1.0/6, 2.0/6, 3.0/6, 4.0/6, 5.0/6],
                               dtype=_np.float32)
        primary_spacing = 1.0 / 6.0  # 60° gap between primaries

        # Minimum circular angular distance to nearest primary
        hue_exp = hue[:, :, _np.newaxis]          # (H, W, 1)
        prim_exp = primaries[_np.newaxis, _np.newaxis, :]  # (1, 1, 6)
        raw_diff = _np.abs(hue_exp - prim_exp)
        angular_dist = _np.minimum(raw_diff, 1.0 - raw_diff)  # wrap
        min_dist = angular_dist.min(axis=2).astype(_np.float32)

        # Boost = max at primary centre, zero at mid-point between two primaries
        boost_factor = _np.clip(
            1.0 - min_dist / (primary_spacing * 0.5),
            0.0, 1.0
        ).astype(_np.float32)
        boost_s = (float(spectral_boost) * boost_factor).astype(_np.float32)
        s1 = _np.clip(s + boost_s, 0.0, 1.0).astype(_np.float32)

        # Rebuild RGB from (hue, s1, v)
        h6 = hue * 6.0
        i = _np.floor(h6).astype(_np.int32) % 6
        f = (h6 - _np.floor(h6)).astype(_np.float32)
        p_v = (v * (1.0 - s1)).astype(_np.float32)
        q_v = (v * (1.0 - s1 * f)).astype(_np.float32)
        t_v = (v * (1.0 - s1 * (1.0 - f))).astype(_np.float32)

        r1 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                        [v, q_v, p_v, p_v, t_v, v], default=v).astype(_np.float32)
        g1 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                        [t_v, v, v, q_v, p_v, p_v], default=v).astype(_np.float32)
        b1 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                        [p_v, p_v, t_v, v, v, q_v], default=v).astype(_np.float32)

        r1 = _np.clip(r1, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g1, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b1, 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Optical Luminosity Enhancement ───────────────────────────
        lg = float(luminosity_gain)
        lt = float(luminosity_threshold)
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        sat_excess = _np.maximum(0.0, s1 - lt).astype(_np.float32)
        sat_range  = max(1.0 - lt, 1e-6)
        lum_lift   = (lg * sat_excess / sat_range).astype(_np.float32)
        lum2       = _np.clip(lum1 + lum_lift, 0.0, 1.0).astype(_np.float32)
        scale2     = (lum2 / _np.maximum(lum1, 1e-6)).astype(_np.float32)
        r2 = _np.clip(r1 * scale2, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 * scale2, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 * scale2, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Dot Field Texture ────────────────────────────────────────
        rng = _np.random.default_rng(int(noise_seed))
        sp  = max(1, int(dot_spacing))
        jit = float(dot_jitter) * sp
        sig = max(0.5, float(dot_sigma))
        amp = float(dot_amplitude)

        bump_field = _np.zeros((h, w), dtype=_np.float32)

        ys = _np.arange(sp // 2, h + sp, sp)
        xs = _np.arange(sp // 2, w + sp, sp)
        for gi, cy_base in enumerate(ys):
            for gj, cx_base in enumerate(xs):
                cy = int(round(cy_base + rng.uniform(-jit, jit)))
                cx = int(round(cx_base + rng.uniform(-jit, jit)))
                # Checkerboard sign
                sign = 1.0 if (gi + gj) % 2 == 0 else -1.0

                # Bounding box for the Gaussian (3 sigma)
                r_min = max(0, cy - int(3 * sig) - 1)
                r_max = min(h, cy + int(3 * sig) + 2)
                c_min = max(0, cx - int(3 * sig) - 1)
                c_max = min(w, cx + int(3 * sig) + 2)
                if r_max <= r_min or c_max <= c_min:
                    continue

                rows = _np.arange(r_min, r_max, dtype=_np.float32)
                cols = _np.arange(c_min, c_max, dtype=_np.float32)
                dr = (rows - cy)[:, _np.newaxis]
                dc = (cols - cx)[_np.newaxis, :]
                gauss = sign * amp * _np.exp(-(dr**2 + dc**2) / (2.0 * sig**2))
                bump_field[r_min:r_max, c_min:c_max] += gauss.astype(_np.float32)

        lum2_full = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)
        lum3 = _np.clip(lum2_full + bump_field, 0.0, 1.0).astype(_np.float32)
        scale3 = (lum3 / _np.maximum(lum2_full, 1e-6)).astype(_np.float32)
        r3 = _np.clip(r2 * scale3, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 * scale3, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 * scale3, 0.0, 1.0).astype(_np.float32)

        # ── Composite at opacity ───────────────────────────────────────────────
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

        boosted_px = int((boost_s > 0.01).sum())
        lifted_px  = int((lum_lift > 0.001).sum())
        print(f"    Rysselberghe Chromatic Dot Field complete "
              f"(spectral_boost={spectral_boost:.2f}, "
              f"boosted_px={boosted_px}, "
              f"lifted_px={lifted_px})")
"""

# ── Pass 2: paint_atmospheric_recession_pass (improvement) ────────────────────

ATMOSPHERIC_RECESSION_PASS = """
    def paint_atmospheric_recession_pass(
        self,
        recession_direction: str   = "top",
        haze_lift:           float = 0.08,
        desaturation:        float = 0.30,
        cool_shift_r:        float = 0.04,
        cool_shift_g:        float = 0.01,
        cool_shift_b:        float = 0.08,
        near_fraction:       float = 0.25,
        far_fraction:        float = 0.85,
        opacity:             float = 0.65,
    ) -> None:
        r\"\"\"Paint Atmospheric Recession -- session 259 improvement.

        THREE-STAGE AERIAL PERSPECTIVE SIMULATION:

        Aerial perspective (atmospheric perspective) is the optical phenomenon
        first described systematically by Leonardo da Vinci: objects at greater
        distances appear lighter, more desaturated, and shifted toward blue-grey
        relative to near objects, as the air column between viewer and subject
        scatters light.  The three physical mechanisms -- (1) luminance lift from
        forward-scattered light filling in shadows, (2) saturation loss from
        atmospheric grey averaging, and (3) cool Rayleigh scattering shifting
        distant hues toward blue -- are modelled in three independent stages.

        The pass defines a linear depth-weight field across the canvas in a
        chosen recession direction:
          weight(row, col) in [0, 1]  (0=near, 1=far)
        All three effects are applied proportional to this weight, interpolated
        between near_fraction (the weight at the nominally near edge of the
        canvas) and far_fraction (the weight at the far edge).

        Stage 1 DISTANCE HAZE LIFT: Push pixel luminance up proportionally to
        depth weight.  The physical mechanism is forward light scatter that adds
        a luminous haze to distant surfaces, reducing apparent shadow depth:
          lum_lift = haze_lift * w
          lum_new = clip(lum + lum_lift, 0, 1)
          scale = lum_new / (lum + 1e-6)
          R *= scale, G *= scale, B *= scale
        NOVEL: (a) DISTANCE-WEIGHT-PROPORTIONAL LUMINANCE LIFT AS A MODEL OF
        ATMOSPHERIC FORWARD-SCATTER HAZE -- first pass to apply a spatially-
        varying luminance increase driven purely by a linear distance-weight
        field; paint_tonal_key_pass (s255) shifts the global key via histogram
        percentile without any spatial gradient; no prior pass applies a
        linearly-weighted per-pixel luminance boost along a spatial depth axis.

        Stage 2 ATMOSPHERIC DESATURATION: Reduce saturation proportional to
        depth weight.  Distant atmospheric averaging dilutes chromatic contrast:
          HSV: s_new = s * (1 - desaturation * w)
        Reconstruct RGB from modified saturation.
        NOVEL: (b) DEPTH-WEIGHT-PROPORTIONAL SATURATION REDUCTION ALONG A
        SPATIAL RECESSION AXIS AS ATMOSPHERIC GREY AVERAGING -- first pass
        to reduce HSV saturation in proportion to a spatial depth weight field;
        morandi_dusty_vessel_pass (s258) applies luminance-weighted saturation
        reduction as a dust veil; no prior pass applies saturation reduction
        as a function of position along a user-defined spatial recession axis.

        Stage 3 COOL AERIAL SHIFT: Blend pixel RGB toward a pale cool aerial
        grey (modelling Rayleigh scattering bias toward shorter wavelengths)
        in proportion to depth weight:
          aerial = (R + cool_shift_r * w, G + cool_shift_g * w, B + cool_shift_b * w)
          Out = blend(In, aerial, cool_weight = w * opacity_local)
        Effectively: R nudged down slightly (warm reduced at distance), B nudged
        up (cool increased at distance), producing the characteristic blue-grey
        haze of distant landscape planes.
        NOVEL: (c) SPATIALLY-VARYING RGB COOL-SHIFT ALONG A DEPTH-AXIS WEIGHT
        FIELD AS RAYLEIGH-SCATTER CHROMATIC RECESSION -- first pass to apply a
        distance-proportional per-channel RGB shift (R down, B up) along a
        user-defined recession axis to simulate atmospheric chromatic cooling;
        paint_shadow_bleed_pass (s257) blends shadow-zone pixels toward a warm
        bounce colour based on proximity to bright pixels; no prior pass applies
        a spatially-varying cool RGB shift proportional to a linear depth-weight
        gradient.

        recession_direction : \"top\" (top=far), \"bottom\" (bottom=far),
                              \"left\" (left=far), \"right\" (right=far).
        haze_lift           : Max luminance increase at far edge (0-1).
        desaturation        : Max saturation reduction fraction at far edge (0-1).
        cool_shift_r/g/b    : Per-channel max shift at far edge (positive = add).
        near_fraction       : Depth weight at the near canvas edge (0-1).
        far_fraction        : Depth weight at the far canvas edge (0-1).
        opacity             : Final composite opacity.
        \"\"\"
        import numpy as _np

        print("    Paint Atmospheric Recession pass (session 259 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Build depth-weight field ───────────────────────────────────────────
        nf = float(near_fraction)
        ff = float(far_fraction)
        d = str(recession_direction).lower()

        if d in ("top", "up"):
            # top = far; row 0 = far weight
            row_t = _np.linspace(ff, nf, h, dtype=_np.float32)
            weight = _np.broadcast_to(row_t[:, _np.newaxis], (h, w)).copy()
        elif d in ("bottom", "down"):
            row_t = _np.linspace(nf, ff, h, dtype=_np.float32)
            weight = _np.broadcast_to(row_t[:, _np.newaxis], (h, w)).copy()
        elif d == "left":
            col_t = _np.linspace(ff, nf, w, dtype=_np.float32)
            weight = _np.broadcast_to(col_t[_np.newaxis, :], (h, w)).copy()
        else:  # right
            col_t = _np.linspace(nf, ff, w, dtype=_np.float32)
            weight = _np.broadcast_to(col_t[_np.newaxis, :], (h, w)).copy()

        weight = weight.astype(_np.float32)

        # ── Stage 1: Distance Haze Lift ────────────────────────────────────────
        hl = float(haze_lift)
        lum_lift = (hl * weight).astype(_np.float32)
        lum1 = _np.clip(lum + lum_lift, 0.0, 1.0).astype(_np.float32)
        scale1 = (lum1 / _np.maximum(lum, 1e-6)).astype(_np.float32)
        r1 = _np.clip(r0 * scale1, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * scale1, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * scale1, 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Atmospheric Desaturation (HSV) ───────────────────────────
        cmax = _np.maximum(_np.maximum(r1, g1), b1)
        cmin = _np.minimum(_np.minimum(r1, g1), b1)
        delta = (cmax - cmin).astype(_np.float32)
        v = cmax.copy()
        s = _np.where(cmax > 1e-6, delta / (cmax + 1e-8), 0.0).astype(_np.float32)

        eps = 1e-8
        hue = _np.zeros((h, w), dtype=_np.float32)
        m_r = (cmax == r1) & (delta > eps)
        m_g = (cmax == g1) & (delta > eps)
        m_b = (cmax == b1) & (delta > eps)
        hue[m_r] = (((g1[m_r] - b1[m_r]) / (delta[m_r] + eps)) % 6.0) / 6.0
        hue[m_g] = (((b1[m_g] - r1[m_g]) / (delta[m_g] + eps)) + 2.0) / 6.0
        hue[m_b] = (((r1[m_b] - g1[m_b]) / (delta[m_b] + eps)) + 4.0) / 6.0
        hue = _np.clip(hue, 0.0, 1.0)

        ds = float(desaturation)
        s2 = _np.clip(s * (1.0 - ds * weight), 0.0, 1.0).astype(_np.float32)

        # Rebuild RGB from (hue, s2, v)
        h6 = hue * 6.0
        i = _np.floor(h6).astype(_np.int32) % 6
        f = (h6 - _np.floor(h6)).astype(_np.float32)
        p_v = (v * (1.0 - s2)).astype(_np.float32)
        q_v = (v * (1.0 - s2 * f)).astype(_np.float32)
        t_v = (v * (1.0 - s2 * (1.0 - f))).astype(_np.float32)

        r2 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                        [v, q_v, p_v, p_v, t_v, v], default=v).astype(_np.float32)
        g2 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                        [t_v, v, v, q_v, p_v, p_v], default=v).astype(_np.float32)
        b2 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5],
                        [p_v, p_v, t_v, v, v, q_v], default=v).astype(_np.float32)

        r2 = _np.clip(r2, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g2, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b2, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Cool Aerial Shift ────────────────────────────────────────
        csr = float(cool_shift_r)
        csg = float(cool_shift_g)
        csb = float(cool_shift_b)
        r3 = _np.clip(r2 - csr * weight, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 - csg * weight, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 + csb * weight, 0.0, 1.0).astype(_np.float32)

        # ── Composite at opacity ───────────────────────────────────────────────
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

        far_px = int((weight > 0.6).sum())
        print(f"    Atmospheric Recession complete "
              f"(direction={recession_direction}, "
              f"haze_lift={haze_lift:.2f}, "
              f"far_px={far_px})")
"""

# ── Inject into stroke_engine.py ──────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

inserted = False

if "rysselberghe_chromatic_dot_field_pass" not in src:
    ANCHOR = "\n    def paint_granulation_pass("
    if ANCHOR not in src:
        print("ERROR: could not find insertion anchor in stroke_engine.py",
              file=sys.stderr)
        sys.exit(1)
    src = src.rstrip("\n") + "\n" + RYSSELBERGHE_PASS + "\n" + ATMOSPHERIC_RECESSION_PASS + "\n"
    inserted = True
    print("Inserted rysselberghe_chromatic_dot_field_pass and paint_atmospheric_recession_pass.")
else:
    print("rysselberghe_chromatic_dot_field_pass already in stroke_engine.py -- nothing to do.")

if "paint_atmospheric_recession_pass" not in src and not inserted:
    src = src.rstrip("\n") + "\n" + ATMOSPHERIC_RECESSION_PASS + "\n"
    inserted = True
    print("Inserted paint_atmospheric_recession_pass.")

with open(ENGINE_PATH, "w", encoding="utf-8") as f:
    f.write(src)

# Verify
with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    check = f.read()

if "rysselberghe_chromatic_dot_field_pass" in check:
    print("rysselberghe_chromatic_dot_field_pass confirmed present.")
if "paint_atmospheric_recession_pass" in check:
    print("paint_atmospheric_recession_pass confirmed present.")
