"""Insert paint_palette_knife_ridge_pass (s267 improvement) and
goncharova_rayonist_pass (178th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_palette_knife_ridge_pass (s267 improvement) ────────────────

PALETTE_KNIFE_RIDGE_PASS = '''
    def paint_palette_knife_ridge_pass(
        self,
        ridge_freq:    float = 0.18,
        ridge_scale:   float = 0.055,
        ridge_sigma:   float = 8.0,
        lum_lo:        float = 0.18,
        lum_hi:        float = 0.82,
        noise_seed:    int   = 267,
        opacity:       float = 0.65,
    ) -> None:
        r"""Palette Knife Ridge Texture -- session 267 artistic improvement.

        THREE-STAGE PALETTE KNIFE RIDGE TEXTURE INSPIRED BY THE DIRECT IMPASTO
        TECHNIQUE OF NATALIA GONCHAROVA AND THE NEO-PRIMITIVIST PAINTERS
        (c.1905-1915):

        Natalia Goncharova (1881-1962) and her contemporaries in the Russian
        Neo-Primitivist movement painted with a directness that derived from
        peasant icon painting and folk art traditions: broad, flat strokes
        applied with a loaded palette knife or stiff hog-hair brush, building
        surfaces that carry visible material evidence of their construction.
        The palette knife in particular produces a characteristic surface
        topology: each stroke deposits paint in a flat slab with steep raised
        edges -- the knife lifts away a ridge of paint at the stroke boundary,
        and the interior of the stroke is level or slightly concave where the
        knife blade compressed the paint. When raking light hits such a surface,
        alternating ridges and troughs catch highlights and cast micro-shadows
        that follow the directional logic of the stroke. These ridges are not
        random (as canvas grain is) nor fixed-direction (as woven fiber is):
        they run PERPENDICULAR to the knife stroke direction, which itself
        follows the form of the subject -- a painter building the roundness of
        a sunflower petal applies strokes along the petal axis, so ridges run
        transversely across it.

        The critical novelty of this pass is computing a GRADIENT-FOLLOWING
        SPATIAL SINUSOIDAL RIDGE TEXTURE. The local luminance gradient direction
        is used to infer the dominant paint-application direction (the knife
        stroke axis), and the ridge texture is generated perpendicular to that
        axis as a spatial sinusoid. This means the ridge pattern locally adapts
        to the form of the subject: ridges are radial on round objects, horizontal
        on flat ground planes, and diagonal on angled surfaces. No prior pass
        generates a form-following ridge texture; all prior texture passes use
        either isotropic noise (granulation), woven grid patterns (surface_tooth),
        or gradient-magnitude shadow casting on EXISTING ridges (impasto_ridge_cast).
        This pass synthesises new ridge marks that authentically follow the
        painted forms as a palette knife would.

        Stage 1 LOCAL GRADIENT DIRECTION FIELD: Compute the luminance image from
        the canvas RGB. Apply Sobel gradient operators to get (Gx, Gy). Encode
        the gradient direction as unit vectors (sin_g, cos_g) = (sin(angle),
        cos(angle)) where angle = atan2(Gy, Gx). Apply Gaussian smoothing to
        sin_g and cos_g at sigma=ridge_sigma to produce a smooth gradient
        direction field (vectorial averaging handles the pi-periodic wrap-around
        of direction vectors). Reconstruct smoothed_angle = atan2(smooth_sin,
        smooth_cos). This is the local "flow direction" of the painted form.
        NOVEL: (a) VECTORIAL GRADIENT DIRECTION SMOOTHING VIA SIN/COS CIRCULAR
        MEAN AT LARGE SIGMA -- all prior passes that use gradient direction use
        the raw Sobel direction without smoothing (paint_impasto_ridge_cast_pass
        uses gradient magnitude, not direction; paint_edge_temperature_pass uses
        Sobel magnitude as a gate without computing direction); smoothing the
        direction field at ridge_sigma=8px removes small-scale noise and yields
        a coherent stroke-direction field that follows the major forms of the
        subject rather than individual brushmark edges.

        Stage 2 PERPENDICULAR RIDGE FREQUENCY SYNTHESIS: Compute the ridge
        direction as perpendicular to the gradient: perp_angle = smoothed_angle
        + pi/2. For every pixel (y, x) compute the ridge phase:
          ridge_phase = (X * cos(perp_angle) + Y * sin(perp_angle)) * ridge_freq
          ridge_tex = sin(ridge_phase * 2 * pi)
        where X = horizontal coordinate grid, Y = vertical coordinate grid.
        The result is a spatially-varying sinusoidal ridge pattern that locally
        aligns perpendicular to the estimated stroke direction. At ridge_freq=0.18
        cycles/pixel, ridges are approximately 5-6 pixels wide at painting scale --
        the visual width of a palette knife ridge on a 1040-1440px canvas.
        NOVEL: (b) GRADIENT-DIRECTION-FOLLOWING SPATIAL SINUSOIDAL RIDGE TEXTURE
        -- first pass to generate per-pixel ridge texture by dotting the pixel
        coordinate with the LOCAL PERPENDICULAR DIRECTION rather than a global
        fixed direction or isotropic noise; paint_surface_tooth_pass uses dual
        sinusoidal grids at 0° and 90° (fixed global axes, not form-following);
        paint_granulation_pass uses Gaussian-smoothed random noise (isotropic,
        no directional coherence); this pass generates ridges that curve and
        reorient to follow the round forms, flat planes, and diagonal surfaces
        of the subject exactly as a palette knife does.

        Stage 3 LUMINANCE-GATED RIDGE COMPOSITE: Apply the ridge texture as a
        direct luminance lift/depression:
          lum_gate = 4 * clip((lum - lum_lo)/(lum_hi-lum_lo), 0, 1) *
                         clip((lum_hi - lum)/(lum_hi-lum_lo), 0, 1)
          (peaks at lum = (lum_lo + lum_hi)/2, falls to zero at both extremes)
          delta = ridge_tex * lum_gate * ridge_scale
          new_r = clip(r + delta, 0, 1)
          new_g = clip(g + delta, 0, 1)
          new_b = clip(b + delta, 0, 1)
        The luminance gate ensures ridges are prominent in mid-tones (where the
        most active palette knife work is typically visible) and invisible in
        deep shadows or pure highlights, which is correct for raking light
        conditions where ridge contrast is highest in the intermediate tonal zone.
        NOVEL: (c) BELL-CURVE LUMINANCE GATE FOR RIDGE VISIBILITY, PEAKING AT
        MID-TONE -- no prior texture pass uses a symmetric mid-tone bell gate
        (the product of two linear ramps, equalling a triangular/bell shape at
        the mid-luminance point); paint_granulation_pass uses a global opacity
        without luminance gating; paint_surface_tooth_pass uses a fixed ridge_
        strength without gating; this gate physically models the behaviour of
        raking light on an undulating surface, where the greatest tonal contrast
        between ridge peaks (bright) and trough valleys (dark) occurs at
        intermediate luminance levels -- pure whites show no ridge contrast
        because both peak and trough are bright; pure blacks show none because
        both are dark.
        """
        print("    Palette Knife Ridge Texture pass (session 267 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf
        from scipy.ndimage import convolve as _conv

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Local Gradient Direction Field ────────────────────────────
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        sobel_x = _np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=_np.float32)
        sobel_y = sobel_x.T
        gx = _conv(lum, sobel_x, mode="reflect").astype(_np.float32)
        gy = _conv(lum, sobel_y, mode="reflect").astype(_np.float32)

        angle = _np.arctan2(gy, gx).astype(_np.float32)
        sin_g = _np.sin(angle).astype(_np.float32)
        cos_g = _np.cos(angle).astype(_np.float32)

        rsig = max(float(ridge_sigma), 0.5)
        smooth_sin = _gf(sin_g, sigma=rsig).astype(_np.float32)
        smooth_cos = _gf(cos_g, sigma=rsig).astype(_np.float32)
        smoothed_angle = _np.arctan2(smooth_sin, smooth_cos).astype(_np.float32)

        # ── Stage 2: Perpendicular Ridge Frequency Synthesis ──────────────────
        perp_angle = (smoothed_angle + _np.pi / 2.0).astype(_np.float32)

        Y_grid, X_grid = _np.mgrid[0:h, 0:w]
        X_f = X_grid.astype(_np.float32)
        Y_f = Y_grid.astype(_np.float32)

        ridge_phase = (
            X_f * _np.cos(perp_angle) + Y_f * _np.sin(perp_angle)
        ).astype(_np.float32)

        rf = float(ridge_freq)
        ridge_tex = _np.sin(ridge_phase * rf * 2.0 * _np.pi).astype(_np.float32)

        # ── Stage 3: Luminance-Gated Ridge Composite ──────────────────────────
        lo = float(lum_lo)
        hi = float(lum_hi)
        span = max(hi - lo, 1e-4)
        ramp_lo = _np.clip((lum - lo) / span, 0.0, 1.0).astype(_np.float32)
        ramp_hi = _np.clip((hi - lum) / span, 0.0, 1.0).astype(_np.float32)
        lum_gate = (4.0 * ramp_lo * ramp_hi).astype(_np.float32)

        rs = float(ridge_scale)
        delta = (ridge_tex * lum_gate * rs).astype(_np.float32)

        new_r = _np.clip(r0 + delta, 0.0, 1.0).astype(_np.float32)
        new_g = _np.clip(g0 + delta, 0.0, 1.0).astype(_np.float32)
        new_b = _np.clip(b0 + delta, 0.0, 1.0).astype(_np.float32)

        # ── Composite at opacity ───────────────────────────────────────────────
        op = float(opacity)
        final_r = r0 * (1.0 - op) + new_r * op
        final_g = g0 * (1.0 - op) + new_g * op
        final_b = b0 * (1.0 - op) + new_b * op

        ridge_px = int((lum_gate > 0.3).sum())

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(final_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(final_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(final_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        print(f"    Palette Knife Ridge complete (active_px={ridge_px})")
'''

# ── Pass 2: goncharova_rayonist_pass (178th mode) ─────────────────────────────

RAYONIST_PASS = '''
    def goncharova_rayonist_pass(
        self,
        n_angles:           int   = 4,
        ray_sigma:          float = 24.0,
        ray_strength:       float = 0.32,
        shimmer_angle:      float = 14.0,
        shimmer_freq:       float = 0.06,
        shimmer_threshold:  float = 0.12,
        noise_seed:         int   = 267,
        opacity:            float = 0.72,
    ) -> None:
        r"""Goncharova Rayonist -- session 267, 178th distinct mode.

        THREE-STAGE RAYONIST LIGHT FRACTURE TECHNIQUE INSPIRED BY NATALIA
        GONCHAROVA\'S RAYONIST PAINTING PRACTICE (c.1912-1914):

        Natalia Goncharova (1881-1962) co-developed Rayonism (Luchism) with
        Mikhail Larionov as the first fully abstract art movement to originate
        in Russia. The theoretical basis, published in the 1913 manifesto
        "Rayonism and Futurism", holds that the eye does not perceive objects
        directly but rather the REFLECTED RAYS OF LIGHT that objects emit into
        the space between subject and viewer. Painting, therefore, should render
        not the object but these dynamic ray fields -- the electromagnetic
        interaction of illuminated surfaces. In practice, Rayonist paintings
        dissolve recognizable forms into crossing bands of directional colour,
        each band representing a ray of reflected light traveling in a specific
        direction. Where rays from adjacent objects cross, the colours interfere
        and mix, producing chromatic complexity at intersection zones. The 1913
        Rayonist works (Cats, Linen, Forest, Glass) show objects fragmented into
        long, roughly parallel colour streaks that cross each other at various
        angles; the underlying form is still legible but buried beneath the
        dynamic ray field.

        The implementation models this through three identifiable mechanical
        stages: First, the existing paint colors on the canvas are elongated
        simultaneously in multiple directions through directional Gaussian
        blurring -- this "stretches" each colour into ray-like extensions along
        4 angles (0°, 45°, 90°, 135°, covering the full directional space at
        45° intervals). Each directional blur approximates a family of parallel
        light rays traveling in that direction. Second, the multi-directional
        streak synthesis is blended over the original canvas weighted by
        luminance, so that bright areas (the natural light emitters) contribute
        more strongly to the ray field than dark areas -- this is the Rayonist
        principle that brightly illuminated surfaces generate the most energetic
        ray emission. Third, in the zones where the rayonist treatment diverges
        most strongly from the original (the crossing-ray interference zones),
        a spatial alternating hue rotation introduces chromatic shimmer --
        adjacent sub-regions shift hue in opposite directions, creating the
        prismatic colour separation that Goncharova achieved through deliberate
        complementary colour placement within ray bands.

        Stage 1 MULTI-ANGLE DIRECTIONAL STREAK SYNTHESIS: Iterate over N=4
        angles [0, 45, 90, 135] degrees. For each angle:
          a. Rotate each RGB channel by -angle_deg (bilinear for 45/135,
             np.rot90 for 90, identity for 0), reshape=False (canvas size
             preserved), mode=\'reflect\' (edges continue with mirrored content).
          b. Apply 1D Gaussian blur along axis=1 (the row axis, which after
             rotation represents the ray direction): sigma=ray_sigma=24px.
          c. Apply 1D Gaussian blur along axis=0 (cross direction): sigma=1.5px
             to smooth interpolation artifacts without smearing transversally.
          d. Rotate back by +angle_deg.
          e. Accumulate in streak_r, streak_g, streak_b.
        streak_mean = accumulated / N_ANGLES.
        NOVEL: (a) MULTI-ANGLE 1D DIRECTIONAL GAUSSIAN STREAK SYNTHESIS COVERING
        FULL 180° DIRECTIONAL SPACE IN 45° STEPS -- first mode pass to apply a
        family of directional 1D Gaussian blurs at multiple angles and sum them
        into a streak composite; paint_shadow_bleed_pass applies a single-
        direction multi-scale Gaussian blur (luminance-weighted); paint_sisley_
        silver_veil_pass applies a single horizontal motion blur in the sky zone;
        no prior mode pass applies elongating directional blurs at 4+ distinct
        angles and composites them, which is the mechanism that creates the
        multi-directional ray field characteristic of Rayonist paintings.

        Stage 2 LUMINANCE-WEIGHTED STREAK OVERLAY: Compute a source weight map
        from the original luminance:
          source_w = clip(lum / (lum.max() + eps), 0, 1)  (normalized luminance)
          source_w_n = gaussian_filter(source_w, sigma=4)  (smooth weighting)
        Blend the streak mean over the original at ray_strength, modulated by
        source weight:
          blend_factor = ray_strength * (0.4 + 0.6 * source_w_n)
          ray_r = r0 * (1 - blend_factor) + streak_mean_r * blend_factor
          ray_g = g0 * (1 - blend_factor) + streak_mean_g * blend_factor
          ray_b = b0 * (1 - blend_factor) + streak_mean_b * blend_factor
        This ensures bright areas (sunflower discs, sky highlights) generate
        stronger ray extensions than dark areas, consistent with the Rayonist
        physical model of ray emission strength proportional to light intensity.
        NOVEL: (b) LUMINANCE-PROPORTIONAL WEIGHTING OF STREAK CONTRIBUTION --
        first mode pass to modulate the directional streak strength per-pixel
        by the normalised original luminance; prior blending passes use a fixed
        global opacity; this creates spatially-varying ray density that is
        highest at bright emission zones and lowest in deep shadows, physically
        modelling the directional dispersion of light sources.

        Stage 3 CHROMATIC HUE SHIMMER AT RAY INTERFERENCE ZONES: Compute the
        per-pixel ray energy:
          ray_energy = mean(|ray_composite - original|) over RGB channels
        In pixels where ray_energy > shimmer_threshold, apply a spatially
        alternating hue rotation:
          spatial_sign = sign(sin(X * shimmer_freq * 2*pi) *
                              cos(Y * shimmer_freq * 2*pi))
          hue_delta = (shimmer_angle / 360.0) * spatial_sign
        Convert to HSV, shift H by hue_delta, convert back to RGB. Gate by
        the shimmer_mask (ray_energy > shimmer_threshold). This creates
        alternating warm/cool patches within the ray interference zones,
        reproducing the chromatic vibration of Goncharova\'s Rayonist canvases
        where adjacent ray bands carry complementary colours.
        NOVEL: (c) SPATIALLY-ALTERNATING HUE ROTATION GATED BY RAY DIVERGENCE
        FIELD -- first mode pass to gate a hue rotation by the DIFFERENCE
        between the directional-streak composite and the original canvas (the
        "ray interference field"); prior hue-rotation passes use luminance or
        saturation gates; this pass identifies specifically the zones where ray
        mixing creates new chromatic conditions and applies the complementary
        shimmer only there, which is the mechanism behind Goncharova\'s
        prismatic colour placement along crossing ray paths.
        """
        print("    Goncharova Rayonist pass (session 267, 178th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter1d as _gf1d
        from scipy.ndimage import gaussian_filter as _gf
        from scipy.ndimage import rotate as _rot_fn

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Multi-Angle Directional Streak Synthesis ─────────────────
        def _rotate_ch(ch, ang_deg):
            """Rotate 2D float32 array by ang_deg CCW; exact for 0/90."""
            if ang_deg == 0:
                return ch.copy()
            if ang_deg == 90:
                return _np.rot90(ch, k=1).astype(_np.float32)
            return _rot_fn(ch, angle=float(ang_deg), reshape=False,
                           order=1, mode="reflect").astype(_np.float32)

        def _unrotate_ch(ch, ang_deg):
            """Inverse rotation."""
            if ang_deg == 0:
                return ch
            if ang_deg == 90:
                return _np.rot90(ch, k=3).astype(_np.float32)
            return _rot_fn(ch, angle=-float(ang_deg), reshape=False,
                           order=1, mode="reflect").astype(_np.float32)

        rs = float(ray_sigma)
        angles = [0, 45, 90, 135]
        n_ang = len(angles)

        streak_r = _np.zeros((h, w), dtype=_np.float32)
        streak_g = _np.zeros((h, w), dtype=_np.float32)
        streak_b = _np.zeros((h, w), dtype=_np.float32)

        for ang in angles:
            rr = _rotate_ch(r0, ang)
            rg = _rotate_ch(g0, ang)
            rb = _rotate_ch(b0, ang)

            rr_h = rr.shape[0]; rr_w = rr.shape[1]

            br = _gf1d(_gf1d(rr, sigma=rs, axis=1), sigma=1.5, axis=0)
            bg = _gf1d(_gf1d(rg, sigma=rs, axis=1), sigma=1.5, axis=0)
            bb = _gf1d(_gf1d(rb, sigma=rs, axis=1), sigma=1.5, axis=0)

            ur = _unrotate_ch(br, ang)
            ug = _unrotate_ch(bg, ang)
            ub = _unrotate_ch(bb, ang)

            # After un-rotation, shape may differ for 90° on non-square images.
            # Crop or pad to (h, w) to ensure consistent accumulation.
            ur = ur[:h, :w]
            ug = ug[:h, :w]
            ub = ub[:h, :w]

            streak_r += ur
            streak_g += ug
            streak_b += ub

        streak_r /= float(n_ang)
        streak_g /= float(n_ang)
        streak_b /= float(n_ang)

        # ── Stage 2: Luminance-Weighted Streak Overlay ─────────────────────────
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        source_w = _np.clip(lum / (lum.max() + 1e-6), 0.0, 1.0).astype(_np.float32)
        source_w_n = _gf(source_w, sigma=4.0).astype(_np.float32)

        ray_str = float(ray_strength)
        blend_f = (ray_str * (0.4 + 0.6 * source_w_n)).astype(_np.float32)
        blend_f = _np.clip(blend_f, 0.0, 1.0).astype(_np.float32)

        ray_r = (r0 * (1.0 - blend_f) + streak_r * blend_f).astype(_np.float32)
        ray_g = (g0 * (1.0 - blend_f) + streak_g * blend_f).astype(_np.float32)
        ray_b = (b0 * (1.0 - blend_f) + streak_b * blend_f).astype(_np.float32)

        ray_r = _np.clip(ray_r, 0.0, 1.0).astype(_np.float32)
        ray_g = _np.clip(ray_g, 0.0, 1.0).astype(_np.float32)
        ray_b = _np.clip(ray_b, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Chromatic Hue Shimmer at Ray Interference Zones ──────────
        ray_energy = (
            _np.abs(ray_r - r0) + _np.abs(ray_g - g0) + _np.abs(ray_b - b0)
        ) / 3.0
        ray_energy = ray_energy.astype(_np.float32)

        shimmer_mask = (ray_energy > float(shimmer_threshold)).astype(_np.float32)
        shimmer_count = int(shimmer_mask.sum())

        if shimmer_count > 0:
            Y_grid, X_grid = _np.mgrid[0:h, 0:w]
            sf = float(shimmer_freq)
            spatial_sign = _np.sign(
                _np.sin(X_grid.astype(_np.float32) * sf * 2.0 * _np.pi) *
                _np.cos(Y_grid.astype(_np.float32) * sf * 2.0 * _np.pi)
            ).astype(_np.float32)
            hue_delta = (float(shimmer_angle) / 360.0 * spatial_sign).astype(_np.float32)

            # HSV hue rotation for shimmer pixels
            ch_max = _np.maximum(_np.maximum(ray_r, ray_g), ray_b)
            ch_min = _np.minimum(_np.minimum(ray_r, ray_g), ray_b)
            delta   = (ch_max - ch_min).astype(_np.float32)
            sat_v   = _np.clip(delta / (ch_max + 1e-6), 0.0, 1.0).astype(_np.float32)
            val_v   = ch_max.astype(_np.float32)

            hue_v = _np.zeros_like(ray_r)
            m = delta > 1e-6
            if m.any():
                rr2 = ray_r[m]; gg2 = ray_g[m]; bb2 = ray_b[m]
                dd2 = delta[m]; mx2 = ch_max[m]
                is_r = (mx2 == rr2)
                is_g = (mx2 == gg2) & ~is_r
                hr2 = ((gg2 - bb2) / dd2) % 6.0
                hg2 = (bb2 - rr2) / dd2 + 2.0
                hb2 = (rr2 - gg2) / dd2 + 4.0
                hue_v[m] = _np.where(is_r, hr2, _np.where(is_g, hg2, hb2)) / 6.0

            new_h = (hue_v + hue_delta) % 1.0

            # HSV → RGB
            h6  = (new_h * 6.0).astype(_np.float32)
            i_a = h6.astype(_np.int32) % 6
            f_a = (h6 - _np.floor(h6)).astype(_np.float32)
            p_a = (val_v * (1.0 - sat_v)).astype(_np.float32)
            q_a = (val_v * (1.0 - sat_v * f_a)).astype(_np.float32)
            t_a = (val_v * (1.0 - sat_v * (1.0 - f_a))).astype(_np.float32)

            sh_r = _np.select([i_a==0,i_a==1,i_a==2,i_a==3,i_a==4,i_a==5],
                              [val_v,q_a,p_a,p_a,t_a,val_v]).astype(_np.float32)
            sh_g = _np.select([i_a==0,i_a==1,i_a==2,i_a==3,i_a==4,i_a==5],
                              [t_a,val_v,val_v,q_a,p_a,p_a]).astype(_np.float32)
            sh_b = _np.select([i_a==0,i_a==1,i_a==2,i_a==3,i_a==4,i_a==5],
                              [p_a,p_a,t_a,val_v,val_v,q_a]).astype(_np.float32)

            sh_r = _np.clip(sh_r, 0.0, 1.0).astype(_np.float32)
            sh_g = _np.clip(sh_g, 0.0, 1.0).astype(_np.float32)
            sh_b = _np.clip(sh_b, 0.0, 1.0).astype(_np.float32)

            ray_r = (ray_r * (1.0 - shimmer_mask) + sh_r * shimmer_mask).astype(_np.float32)
            ray_g = (ray_g * (1.0 - shimmer_mask) + sh_g * shimmer_mask).astype(_np.float32)
            ray_b = (ray_b * (1.0 - shimmer_mask) + sh_b * shimmer_mask).astype(_np.float32)

        # ── Composite at opacity ───────────────────────────────────────────────
        op = float(opacity)
        new_r = r0 * (1.0 - op) + ray_r * op
        new_g = g0 * (1.0 - op) + ray_g * op
        new_b = b0 * (1.0 - op) + ray_b * op

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        print(f"    Goncharova Rayonist complete "
              f"(shimmer_px={shimmer_count})")
'''

# ── Inject into stroke_engine.py ──────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

already_ridge    = "paint_palette_knife_ridge_pass" in src
already_rayonist = "goncharova_rayonist_pass" in src

if already_ridge and already_rayonist:
    print("Both passes already present in stroke_engine.py -- nothing to do.")
    sys.exit(0)

additions = ""
if not already_ridge:
    additions += PALETTE_KNIFE_RIDGE_PASS
if not already_rayonist:
    additions += "\n" + RAYONIST_PASS

src = src.rstrip("\n") + "\n" + additions + "\n"

with open(ENGINE_PATH, "w", encoding="utf-8") as f:
    f.write(src)

if not already_ridge:
    print("Inserted paint_palette_knife_ridge_pass into stroke_engine.py.")
if not already_rayonist:
    print("Inserted goncharova_rayonist_pass into stroke_engine.py.")
