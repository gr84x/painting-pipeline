"""Append session 232 passes to stroke_engine.py."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

MOREAU_PASS = '''
    def moreau_jeweled_ornament_pass(
        self,
        grain_strength:  float = 0.06,
        grain_sigma:     float = 0.55,
        grain_center:    float = 0.60,
        grain_width:     float = 0.22,
        lum_lift:        float = 0.055,
        glow_center:     float = 0.58,
        glow_width:      float = 0.24,
        gold_r_shift:    float = 0.040,
        gold_g_shift:    float = 0.018,
        gold_b_shift:    float = 0.032,
        gold_threshold:  float = 0.52,
        opacity:         float = 0.82,
    ) -> None:
        """
        Moreau Jeweled Ornament -- session 232: ONE HUNDRED AND FORTY-THIRD distinct mode.

        Implements Gustave Moreau (1826-1898) encrusted mythological surface technique.
        Moreau built his paintings like illuminated manuscripts -- every surface dense
        with ornamental grain, every lit zone glowing with an inner jewel luminosity,
        every highlight cast in warm burnished gold.  The effect is a surface that
        reads as simultaneously flat (decorative pattern) and deep (translucent glazing).

        Three-stage mechanism:

        Stage 1 ORNAMENTAL GRAIN:
          noise = gaussian_filter(random_field, grain_sigma) -- spatially coherent fine grain
          norm to [-0.5, 0.5];
          grain_gate = exp(-0.5*((lum-grain_center)/grain_width)^2)  [bell, peaks at 0.60]
          ch += grain_gate * grain_strength * noise

        Stage 2 JEWEL LUMINOSITY LIFT:
          glow_gate = exp(-0.5*((lum-glow_center)/glow_width)^2)  [bell, peaks at 0.58]
          delta_lum = glow_gate * lum_lift
          ch += delta_lum  (uniform channel lift -- preserves hue, brightens mid zone)

        Stage 3 WARM GILDING TINT:
          gold_gate = clip((lum - gold_threshold) / 0.20, 0, 1)  [ramp in bright zone]
          R += gold_gate * gold_r_shift
          G += gold_gate * gold_g_shift
          B -= gold_gate * gold_b_shift

        NOVEL vs. existing passes:
        (a) Spatially-coherent ornamental grain gated by luminance bell (grain_sigma ~0.5px
            produces fine, smooth texture clusters, not sharp pixel noise) -- no prior pass
            adds gated grain as a primary mechanism;
        (b) Separate luminosity lift in the mid-bright zone (lum 0.40-0.75) to simulate
            Moreau's translucent glaze glow from beneath the surface -- distinct from
            midtone_clarity_pass which sharpens detail rather than lifting brightness;
        (c) Warm gilding tint ramp in highlights (R+, G+, B-) -- models burnished gold
            light on illuminated surfaces -- no prior pass implements highlight-zone
            colour temperature shift as a standalone operation;
        (d) All three stages operate on different luminance zones and accumulate without
            cancelling each other: grain peaks at lum=0.60, glow peaks at lum=0.58,
            gold ramp activates above lum=0.52.

        grain_strength : Amplitude of ornamental grain texture.
        grain_sigma    : Gaussian sigma for coherent grain; smaller = finer ornament.
        grain_center   : Luminance at which grain is strongest (bell-curve peak).
        grain_width    : Bell half-width for grain gate.
        lum_lift       : Brightness lift in the jewel-glow zone.
        glow_center    : Luminance at which glow lift is strongest.
        glow_width     : Bell half-width for glow gate.
        gold_r_shift   : Red channel shift in warm gilding highlights.
        gold_g_shift   : Green channel shift in warm gilding highlights.
        gold_b_shift   : Blue channel reduction in warm gilding highlights.
        gold_threshold : Luminance above which warm gilding ramp begins.
        opacity        : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Moreau Jeweled Ornament pass (session 232 -- 143rd mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Ornamental grain -- coherent fine texture gated by luminance bell
        rng = _np.random.RandomState(2320)
        raw_noise = rng.uniform(-0.5, 0.5, size=(self.canvas.h, self.canvas.w)).astype(_np.float32)
        coherent_noise = _gf(raw_noise, float(grain_sigma)).astype(_np.float32)
        gc = float(grain_center)
        gw = float(grain_width)
        grain_gate = _np.exp(-0.5 * ((lum - gc) / (gw + 1e-6)) ** 2).astype(_np.float32)
        gs = float(grain_strength)
        grain_delta = grain_gate * gs * coherent_noise
        r1 = _np.clip(r0 + grain_delta, 0.0, 1.0)
        g1 = _np.clip(g0 + grain_delta, 0.0, 1.0)
        b1 = _np.clip(b0 + grain_delta, 0.0, 1.0)

        # Stage 2: Jewel luminosity lift in mid-bright zone
        glc = float(glow_center)
        glw = float(glow_width)
        glow_gate = _np.exp(-0.5 * ((lum - glc) / (glw + 1e-6)) ** 2).astype(_np.float32)
        ll = float(lum_lift)
        delta_lum = glow_gate * ll
        r2 = _np.clip(r1 + delta_lum, 0.0, 1.0)
        g2 = _np.clip(g1 + delta_lum, 0.0, 1.0)
        b2 = _np.clip(b1 + delta_lum, 0.0, 1.0)

        # Stage 3: Warm gilding tint in highlights
        gt = float(gold_threshold)
        gold_gate = _np.clip((lum - gt) / 0.20, 0.0, 1.0).astype(_np.float32)
        r3 = _np.clip(r2 + gold_gate * float(gold_r_shift), 0.0, 1.0)
        g3 = _np.clip(g2 + gold_gate * float(gold_g_shift), 0.0, 1.0)
        b3 = _np.clip(b2 - gold_gate * float(gold_b_shift), 0.0, 1.0)

        # Composite at opacity
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

        n_grain  = int((grain_gate > 0.5).sum())
        n_glow   = int((glow_gate > 0.5).sum())
        n_gilded = int((gold_gate > 0.2).sum())
        print(f"    Moreau Jeweled Ornament complete "
              f"(grain_px={n_grain} glow_px={n_glow} gilded_px={n_gilded})")
'''

WARM_COOL_PASS = '''
    def warm_cool_zone_pass(
        self,
        warm_threshold: float = 0.52,
        warm_ramp:      float = 0.20,
        warm_r_lift:    float = 0.045,
        warm_b_drop:    float = 0.030,
        cool_threshold: float = 0.34,
        cool_ramp:      float = 0.18,
        cool_b_lift:    float = 0.040,
        cool_r_drop:    float = 0.022,
        cool_g_drop:    float = 0.008,
        opacity:        float = 0.70,
    ) -> None:
        """
        Warm-Cool Zone -- session 232 artistic improvement.

        Applies the classical academic painter's principle of warm light / cool shadow:
        highlights are pushed toward warm (R+, B-) and deep shadows are shifted toward
        cool (B+, R-, slight G-).  This replicates the atmospheric colour temperature
        separation used by Moreau, Bouguereau, Cabanel, and the entire Academic tradition
        -- warm light sources (sun, candle, gold) cast warm highlights; the shadow
        zones, unilluminated by direct light, pick up the cool ambient sky or air.

        Both gates are smooth linear ramps to avoid banding:
          warm_gate = clip((lum - warm_threshold) / warm_ramp, 0, 1)
            -- zero below warm_threshold, linearly rises to 1 at warm_threshold+warm_ramp
          cool_gate = clip((cool_threshold - lum) / cool_ramp, 0, 1)
            -- zero above cool_threshold, linearly rises to 1 at cool_threshold-cool_ramp

        Warm highlights:
          R += warm_gate * warm_r_lift
          B -= warm_gate * warm_b_drop

        Cool shadows:
          B += cool_gate * cool_b_lift
          R -= cool_gate * cool_r_drop
          G -= cool_gate * cool_g_drop

        NOVEL vs. existing passes:
        - hammershoi_grey_interior_pass: specific warm/cool lifts (hi_gate, sh_gate) are
          minor secondary adjustments tied to its dominant grey-veil mechanism and
          unidirectional window gradient.  This pass makes warm/cool temperature
          separation the primary, standalone operation.
        - chromatic_memory_pass: pulls toward local spatial colour average -- no warm/cool
          logic, no luminance-gated temperature model.
        - midtone_clarity_pass: luminance-gated unsharp mask -- sharpening, not colour
          temperature.  Different goal.
        - No prior pass implements warm-light / cool-shadow as a configurable, standalone
          atmospheric separation tool.
        - Novel: (a) dual independent ramp gates (warm and cool) on separate luminance
          zones with no overlap at mid-tones; (b) the mid-tone zone [cool_threshold,
          warm_threshold] is intentionally untouched -- mid-tones stay neutral, enforcing
          the classical tonality model; (c) configurable thresholds and ramp widths allow
          calibration from subtle Academic polish to bold Expressionist contrast.

        warm_threshold : Luminance at which warm shift begins to activate.
        warm_ramp      : Ramp width over which warm gate rises from 0 to 1.
        warm_r_lift    : Red channel gain in warm highlight zone.
        warm_b_drop    : Blue channel reduction in warm highlight zone.
        cool_threshold : Luminance at which cool shift begins to activate.
        cool_ramp      : Ramp width over which cool gate rises from 0 to 1.
        cool_b_lift    : Blue channel gain in cool shadow zone.
        cool_r_drop    : Red channel reduction in cool shadow zone.
        cool_g_drop    : Green channel reduction in cool shadow zone.
        opacity        : Final composite opacity.
        """
        import numpy as _np

        print("    Warm-Cool Zone pass (session 232 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Warm gate: smooth ramp from 0 at warm_threshold to 1 at warm_threshold+warm_ramp
        wt = float(warm_threshold)
        wr = float(warm_ramp)
        warm_gate = _np.clip((lum - wt) / (wr + 1e-6), 0.0, 1.0).astype(_np.float32)

        # Cool gate: smooth ramp from 0 at cool_threshold to 1 at cool_threshold-cool_ramp
        ct = float(cool_threshold)
        cr = float(cool_ramp)
        cool_gate = _np.clip((ct - lum) / (cr + 1e-6), 0.0, 1.0).astype(_np.float32)

        # Warm highlight adjustment
        r1 = _np.clip(r0 + warm_gate * float(warm_r_lift), 0.0, 1.0)
        b1 = _np.clip(b0 - warm_gate * float(warm_b_drop), 0.0, 1.0)

        # Cool shadow adjustment (applied to the already warm-adjusted channels)
        r2 = _np.clip(r1 - cool_gate * float(cool_r_drop), 0.0, 1.0)
        g2 = _np.clip(g0 - cool_gate * float(cool_g_drop), 0.0, 1.0)
        b2 = _np.clip(b1 + cool_gate * float(cool_b_lift), 0.0, 1.0)

        # Composite at opacity
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

        n_warm = int((warm_gate > 0.2).sum())
        n_cool = int((cool_gate > 0.2).sum())
        print(f"    Warm-Cool Zone pass complete (warm_px={n_warm} cool_px={n_cool})")
'''

with open('stroke_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content + MOREAU_PASS + WARM_COOL_PASS

with open('stroke_engine.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Passes appended. New length: {len(new_content)} chars")
