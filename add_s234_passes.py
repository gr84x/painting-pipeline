"""Append session 234 passes to stroke_engine.py."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

RYDER_PASS = '''
    def ryder_moonlit_sea_pass(
        self,
        dark_thresh:         float = 0.32,
        dark_power:          float = 1.80,
        dark_crush:          float = 0.40,
        light_thresh:        float = 0.64,
        light_power:         float = 1.50,
        light_lift:          float = 0.30,
        amber_center:        float = 0.40,
        amber_width:         float = 0.26,
        amber_r:             float = 0.14,
        amber_g:             float = 0.06,
        amber_b:             float = 0.10,
        amber_str:           float = 0.72,
        dissolution_sigma:   float = 2.20,
        dissolution_blend:   float = 0.22,
        opacity:             float = 0.85,
    ) -> None:
        """
        Ryder Moonlit Sea -- session 234: ONE HUNDRED AND FORTY-FIFTH distinct mode.

        Implements Albert Pinkham Ryder (1847-1910) visionary Tonalism technique.
        Ryder reduced sea and sky to bare elemental masses -- near-black water,
        pale luminous sky, a small incandescent moon -- and built his canvases up
        over years with thick paint and resinous varnish glazes, creating a dreaming,
        dissolving quality unlike any of his contemporaries.  His "Moonlit Cove"
        (c.1880-90) reduces the world to three tonal zones and a ghostly luminous
        presence.  His "Death on a Pale Horse" and "Jonah" push further into
        visionary hallucination.  Ryder's method: obsessive reworking with asphaltum
        and other bituminous mediums, causing his surfaces to craze and amber over
        time.  The hallmark: simplified masses, amber-ochre mid-tone tint from aged
        medium, and softened contours where forms dissolve into each other like shapes
        in a half-remembered dream.

        Three-stage mechanism:

        Stage 1 TONAL MASSING (zone-selective luminance pull):
          dark_gate  = clip((dark_thresh  - lum) / (dark_thresh  + 1e-6), 0, 1)^dark_power
          light_gate = clip((lum - light_thresh) / (1-light_thresh+1e-6), 0, 1)^light_power
          Shadows: R,G,B *= (1 - dark_gate * dark_crush)   -- pull darks to near-black
          Lights:  R,G,B += (1-ch) * light_gate * light_lift -- lift lights toward white

        Stage 2 AMBER OCHRE GLAZE (aged medium simulation):
          amber_gate = exp(-0.5 * ((lum - amber_center) / amber_width)^2)
          R += amber_r * amber_gate * amber_str
          G += amber_g * amber_gate * amber_str
          B -= amber_b * amber_gate * amber_str
          Bell curve centered at lum=0.40 (shadow-mid boundary).  Models the yellow-
          orange cast of Ryder's lead white and resinous medium as it aged over decades.

        Stage 3 VISIONARY DISSOLUTION (global form softening):
          R_blur, G_blur, B_blur = gaussian_filter(R, dissolution_sigma), etc.
          ch_out = ch_blur * dissolution_blend + ch_in * (1 - dissolution_blend)
          Isotropic low-pass blur blended back to dissolve hard contours globally,
          producing the dream-like, boundary-erasing quality of his later work.

        NOVEL vs. existing passes:
        (a) Zone-selective dual tonal pull: dark zones crushed independently of light zones
            being lifted -- not a global S-curve (distinct from tonal_compression_pass
            which applies a flat compression factor); first pass using separate power
            gates for dark-crush and light-lift simultaneously as two independent
            luminance-zone operations;
        (b) Bell-curve amber glaze at lum=0.40 (shadow-mid boundary): different from
            moreau_gilded_pass (bell at lum=0.60 for gold in mid-brights) and
            moreau_jeweled_ornament_pass (bell at lum=0.60 for grain) -- Ryder's
            amber was strongest at the transition from mid-tone to shadow, not in
            the upper mid-tones; B subtracted (not just R+G added) for ochre shift;
        (c) Global dissolution blur: first pass applying a uniform isotropic Gaussian
            blur composited at a low blend ratio for form dissolution;
            sfumato_veil_pass is edge-masked (blurs only at detected edges),
            hammershoi_grey_interior_pass applies blur within narrow luminance bands;
            this pass blurs the entire surface uniformly, creating Ryder's indistinct
            dream-like form merging.

        dark_thresh       : Luminance below which tonal crushing begins.
        dark_power        : Power exponent for shadow gate (higher = sharper boundary).
        dark_crush        : Fractional darkening multiplier in shadow zone (0-1).
        light_thresh      : Luminance above which tonal lifting begins.
        light_power       : Power exponent for highlight gate.
        light_lift        : Push-toward-white amplitude in highlight zone.
        amber_center      : Bell-curve centre luminance for amber glaze.
        amber_width       : Bell-curve sigma for amber glaze.
        amber_r/g/b       : R+, G+ and B- shift amounts for amber tint.
        amber_str         : Overall amplitude of amber glaze.
        dissolution_sigma : Gaussian sigma for form dissolution blur (pixels).
        dissolution_blend : Blend ratio of blurred-to-original (0=no blur, 1=full blur).
        opacity           : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Ryder Moonlit Sea pass (session 234 -- 145th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Tonal Massing — zone-selective dual luminance pull
        dt = float(dark_thresh)
        dp = float(dark_power)
        dc = float(dark_crush)
        dark_gate = _np.clip((dt - lum) / (dt + 1e-6), 0.0, 1.0) ** dp
        crush = 1.0 - dark_gate * dc
        r1 = _np.clip(r0 * crush, 0.0, 1.0)
        g1 = _np.clip(g0 * crush, 0.0, 1.0)
        b1 = _np.clip(b0 * crush, 0.0, 1.0)

        lt = float(light_thresh)
        lp = float(light_power)
        ll = float(light_lift)
        light_gate = _np.clip((lum - lt) / (1.0 - lt + 1e-6), 0.0, 1.0) ** lp
        r1 = _np.clip(r1 + (1.0 - r1) * light_gate * ll, 0.0, 1.0)
        g1 = _np.clip(g1 + (1.0 - g1) * light_gate * ll, 0.0, 1.0)
        b1 = _np.clip(b1 + (1.0 - b1) * light_gate * ll, 0.0, 1.0)

        # Stage 2: Amber Ochre Glaze — aged medium simulation (bell at lum=0.40)
        ac = float(amber_center)
        aw = float(amber_width)
        astr = float(amber_str)
        amber_gate = _np.exp(-0.5 * ((lum - ac) / (aw + 1e-6)) ** 2).astype(_np.float32)
        r2 = _np.clip(r1 + float(amber_r) * amber_gate * astr, 0.0, 1.0)
        g2 = _np.clip(g1 + float(amber_g) * amber_gate * astr, 0.0, 1.0)
        b2 = _np.clip(b1 - float(amber_b) * amber_gate * astr, 0.0, 1.0)

        # Stage 3: Visionary Dissolution — global form softening
        ds = float(dissolution_sigma)
        db = float(dissolution_blend)
        if ds > 0.1 and db > 0.01:
            r_blur = _gf(r2, ds).astype(_np.float32)
            g_blur = _gf(g2, ds).astype(_np.float32)
            b_blur = _gf(b2, ds).astype(_np.float32)
            r3 = r_blur * db + r2 * (1.0 - db)
            g3 = g_blur * db + g2 * (1.0 - db)
            b3 = b_blur * db + b2 * (1.0 - db)
        else:
            r3, g3, b3 = r2, g2, b2

        # Composite at opacity
        op = float(opacity)
        new_r = _np.clip(r0 * (1.0 - op) + r3 * op, 0.0, 1.0)
        new_g = _np.clip(g0 * (1.0 - op) + g3 * op, 0.0, 1.0)
        new_b = _np.clip(b0 * (1.0 - op) + b3 * op, 0.0, 1.0)

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        n_dark   = int((dark_gate  > 0.15).sum())
        n_light  = int((light_gate > 0.10).sum())
        n_amber  = int((amber_gate > 0.20).sum())
        print(f"    Ryder Moonlit Sea complete "
              f"(dark_px={n_dark} light_px={n_light} amber_px={n_amber})")
'''

VARNISH_DEPTH_PASS = '''
    def paint_varnish_depth_pass(
        self,
        sat_center:       float = 0.45,
        sat_width:        float = 0.28,
        sat_boost:        float = 0.35,
        sheen_thresh:     float = 0.72,
        sheen_sigma:      float = 3.50,
        sheen_strength:   float = 0.06,
        opacity:          float = 0.70,
        seed:             int   = 234,
    ) -> None:
        """
        Paint Varnish Depth -- session 234 artistic improvement.

        Models the optical depth added by layers of picture varnish on a finished
        oil painting.  A well-varnished surface produces three observable effects:
        (1) dry mid-tone pigments are 'wetted', recovering their saturated chroma
        (varnish fills the micro-gaps that scatter light from dry paint, restoring
        the optically smooth surface that shows full colour); (2) the very brightest
        zones acquire a faint specular micro-sheen — coherent reflected light from
        the smooth resin surface; (3) the overall surface reads as slightly deeper
        and more unified, as surface scatter is reduced.

        Two-stage mechanism:

        Stage 1 SATURATION ENRICHMENT (dry pigment wetted by varnish):
          sat_gate = exp(-0.5 * ((lum - sat_center) / sat_width)^2)  -- bell at 0.45
          lum3 = 0.299*R + 0.587*G + 0.114*B
          sat_scale = 1 + sat_boost * sat_gate
          R_sat = clip(lum3 + (R - lum3) * sat_scale, 0, 1)
          Saturates the mid-tone zone (peaked at 0.45) while leaving shadows and
          highlights nearly unchanged -- matching the photometric reality that dry
          paint loses chroma most visibly in mid-tones.

        Stage 2 SPECULAR MICRO-SHEEN (glossy resin surface):
          noise_raw = gaussian_filter(standard_normal(h, w), sheen_sigma) -- smooth noise
          noise_norm = (noise_raw - noise_raw.min()) / (noise_raw.ptp() + 1e-6) * 2 - 1
          sheen_gate = clip((lum - sheen_thresh) / (1 - sheen_thresh + 1e-6), 0, 1)^2
          R,G,B += noise_norm * sheen_strength * sheen_gate
          Adds coherent Gaussian-smoothed noise micro-texture only in the near-white
          zone (lum > sheen_thresh), simulating the slight micro-unevenness of a
          varnish surface catching directional light.

        NOVEL vs. existing passes:
        (a) Bell-curve sat boost peaked at lum=0.45 (shadow-mid boundary):
            Explicitly models varnish's property of wetting dry pigment. Distinct from
            sorolla_mediterranean_light_pass warm_boost (bell at 0.62, models sunlit
            mid-tone zone), and from bonnard_chromatic_intimism_pass (global additive
            saturation scale, no luminance gating).  The 0.45 center targets the
            specific zone where dry-paint scatter is strongest;
        (b) Coherent Gaussian-noise sheen gated to near-white only (lum > 0.72):
            Distinct from moreau_jeweled_ornament_pass (grain bell at lum=0.60),
            dry_granulation_pass (grain in shadow zone lum < 0.45),
            bristle_separation_texture_pass (directional texture across all zones).
            This is the first pass applying smooth coherent noise exclusively in
            the near-white highlight zone to simulate glossy surface micro-texture.

        sat_center     : Bell-curve centre luminance for saturation wetness peak.
        sat_width      : Bell-curve sigma (spread) for saturation gate.
        sat_boost      : Maximum saturation scale boost at peak (0=none, 0.35=standard).
        sheen_thresh   : Luminance above which specular sheen applies.
        sheen_sigma    : Gaussian sigma for coherent noise generation (pixels).
        sheen_strength : Amplitude of sheen noise additive.
        opacity        : Final composite opacity.
        seed           : RNG seed for reproducible noise.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Paint Varnish Depth pass (session 234 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Saturation enrichment — varnish wets dry mid-tone pigment
        sc = float(sat_center)
        sw = float(sat_width)
        sb = float(sat_boost)
        sat_gate = _np.exp(-0.5 * ((lum - sc) / (sw + 1e-6)) ** 2).astype(_np.float32)
        lum3 = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        sat_scale = 1.0 + sb * sat_gate
        r1 = _np.clip(lum3 + (r0 - lum3) * sat_scale, 0.0, 1.0)
        g1 = _np.clip(lum3 + (g0 - lum3) * sat_scale, 0.0, 1.0)
        b1 = _np.clip(lum3 + (b0 - lum3) * sat_scale, 0.0, 1.0)

        # Stage 2: Specular micro-sheen — coherent Gaussian noise in near-white zones
        rng = _np.random.RandomState(int(seed))
        noise_raw = _gf(
            rng.standard_normal((h, w)).astype(_np.float32),
            float(sheen_sigma)
        ).astype(_np.float32)
        p_min, p_max = float(noise_raw.min()), float(noise_raw.max())
        if p_max - p_min > 1e-6:
            noise_norm = (noise_raw - p_min) / (p_max - p_min) * 2.0 - 1.0
        else:
            noise_norm = noise_raw * 0.0
        noise_norm = noise_norm.astype(_np.float32)

        st = float(sheen_thresh)
        ss = float(sheen_strength)
        sheen_gate = _np.clip(
            (lum - st) / (1.0 - st + 1e-6), 0.0, 1.0) ** 2
        r2 = _np.clip(r1 + noise_norm * ss * sheen_gate, 0.0, 1.0)
        g2 = _np.clip(g1 + noise_norm * ss * sheen_gate, 0.0, 1.0)
        b2 = _np.clip(b1 + noise_norm * ss * sheen_gate, 0.0, 1.0)

        # Composite at opacity
        op = float(opacity)
        new_r = _np.clip(r0 * (1.0 - op) + r2 * op, 0.0, 1.0)
        new_g = _np.clip(g0 * (1.0 - op) + g2 * op, 0.0, 1.0)
        new_b = _np.clip(b0 * (1.0 - op) + b2 * op, 0.0, 1.0)

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        n_sat   = int((sat_gate  > 0.20).sum())
        n_sheen = int((sheen_gate > 0.10).sum())
        print(f"    Paint Varnish Depth pass complete (sat_px={n_sat} sheen_px={n_sheen})")
'''


with open('stroke_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'ryder_moonlit_sea_pass' not in content, 'ryder_moonlit_sea_pass already exists!'
assert 'paint_varnish_depth_pass' not in content, 'paint_varnish_depth_pass already exists!'

content = content + RYDER_PASS + VARNISH_DEPTH_PASS

with open('stroke_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. stroke_engine.py new length: {len(content)} chars')
