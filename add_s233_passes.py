"""Append session 233 passes to stroke_engine.py."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

KUINDZHI_PASS = '''
    def kuindzhi_moonlit_radiance_pass(
        self,
        halo_sigma:        float = 14.0,
        halo_strength:     float = 0.18,
        velvet_power:      float = 2.20,
        velvet_threshold:  float = 0.28,
        moon_cold_b_shift: float = 0.10,
        moon_cold_r_drop:  float = 0.06,
        moon_threshold:    float = 0.68,
        shadow_b_push:     float = 0.06,
        shadow_threshold:  float = 0.22,
        streak_width:      float = 0.06,
        streak_strength:   float = 0.14,
        opacity:           float = 0.88,
    ) -> None:
        """
        Kuindzhi Moonlit Radiance -- session 233: ONE HUNDRED AND FORTY-FOURTH distinct mode.

        Implements Arkhip Kuindzhi (1842-1910) theatrical moonlight technique.
        Kuindzhi's "Moonlit Night on the Dnieper" (1880) stunned contemporaries with
        its impossibly incandescent moon -- crowds queued for hours, some suspecting
        a hidden light behind the canvas.  His method: near-black velvet shadows pushed
        to absolute darkness, a luminous cold-white moon surrounded by a radiating halo
        of pale light, and a vertical reflection streak on still water below.

        Four-stage mechanism, all sharing one luminance map:

        Stage 1 LUMINOUS HALO CORONA:
          bright_mask = clip((lum - moon_threshold) / (1-moon_threshold), 0, 1)
          halo_expanded = gaussian_filter(bright_mask, halo_sigma)
          corona = halo_expanded * (1 - bright_mask)   -- ring outside the source
          R,G,B += corona * halo_strength               -- pale cold ring

        Stage 2 SHADOW VELVETING:
          dark_mask = clip((velvet_threshold - lum) / velvet_threshold, 0, 1)
          velvet_gate = dark_mask ** velvet_power        -- power-curve in shadows
          R,G,B *= (1 - velvet_gate * 0.45)            -- crush to near-black

        Stage 3 CHROMATIC MOONLIGHT SHIFT:
          High zone (lum > moon_threshold): B += moon_cold_b_shift * bright_mask
                                            R -= moon_cold_r_drop * bright_mask
          Low zone (lum < shadow_threshold): B += shadow_b_push * dark_mask
          Models cold blue-white moonlight in highlights, indigo push in deep shadows.

        Stage 4 LUNAR REFLECTION STREAK:
          x_norm in [0, 1]; dist_from_centre = |x_norm - 0.5|
          streak_gate = clip(1 - dist_from_centre / streak_width, 0, 1)^1.5
          lum_streak = uniform_filter(lum, size=1) along vertical axis
          streak_lum = lum * streak_gate              -- vertical bar on water zone
          R,G,B += streak_lum * streak_strength * streak_gate
          Simulates the vertical shimmer of moonlight reflected on still water.

        NOVEL vs. existing passes:
        (a) Halo corona: Gaussian-expanded mask minus the source mask creates a ring of
            light AROUND the bright zone -- no prior pass models a light source corona;
        (b) Power-curve shadow velveting: dark^power crushes shadow gradients to near-black
            without touching mid-tones -- distinct from warm_cool_zone_pass which shifts
            colour temperature, not tonal depth;
        (c) Chromatic moonlight shift: cold blue-white in bright zone (B+, R-) combined
            with indigo push in deep shadows (B+) models the dual-temperature moonlit palette;
        (d) Vertical reflection streak: spatial distance from x-centre creates a narrow
            luminous column simulating moon-on-water -- first pass using horizontal
            distance to modulate a vertical luminance feature.

        halo_sigma        : Gaussian radius for expanding the bright zone corona.
        halo_strength     : Brightness of the halo ring additive boost.
        velvet_power      : Power exponent for shadow velveting (higher = more crushing).
        velvet_threshold  : Luminance below which velveting applies.
        moon_cold_b_shift : Blue channel boost in highlight zone (moonlight coldness).
        moon_cold_r_drop  : Red channel reduction in highlight zone.
        moon_threshold    : Luminance above which moonlight tint applies.
        shadow_b_push     : Blue channel push in deep shadow zone (indigo darkness).
        shadow_threshold  : Luminance below which indigo shadow push applies.
        streak_width      : Half-width of the vertical reflection streak (0-0.5).
        streak_strength   : Amplitude of the reflection streak additive.
        opacity           : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Kuindzhi Moonlit Radiance pass (session 233 -- 144th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Luminous Halo Corona
        mt = float(moon_threshold)
        bright_mask = _np.clip((lum - mt) / (1.0 - mt + 1e-6), 0.0, 1.0)
        halo_expanded = _gf(bright_mask, float(halo_sigma)).astype(_np.float32)
        corona = _np.clip(halo_expanded - bright_mask * 0.5, 0.0, 1.0)
        hs = float(halo_strength)
        r1 = _np.clip(r0 + corona * hs * 0.85, 0.0, 1.0)
        g1 = _np.clip(g0 + corona * hs * 0.90, 0.0, 1.0)
        b1 = _np.clip(b0 + corona * hs,        0.0, 1.0)

        # Stage 2: Shadow Velveting
        vt = float(velvet_threshold)
        dark_mask = _np.clip((vt - lum) / (vt + 1e-6), 0.0, 1.0)
        vp = float(velvet_power)
        velvet_gate = dark_mask ** vp
        crush = 1.0 - velvet_gate * 0.45
        r2 = _np.clip(r1 * crush, 0.0, 1.0)
        g2 = _np.clip(g1 * crush, 0.0, 1.0)
        b2 = _np.clip(b1 * crush, 0.0, 1.0)

        # Stage 3: Chromatic Moonlight Shift
        cb = float(moon_cold_b_shift)
        cr = float(moon_cold_r_drop)
        sb = float(shadow_b_push)
        st_low = float(shadow_threshold)
        shadow_gate = _np.clip((st_low - lum) / (st_low + 1e-6), 0.0, 1.0)
        r3 = _np.clip(r2 - bright_mask * cr, 0.0, 1.0)
        g3 = g2
        b3 = _np.clip(b2 + bright_mask * cb + shadow_gate * sb, 0.0, 1.0)

        # Stage 4: Lunar Reflection Streak
        sw = float(streak_width)
        ss = float(streak_strength)
        x_idx = _np.arange(w, dtype=_np.float32) / (w - 1)
        dist_from_centre = _np.abs(x_idx - 0.5)
        streak_gate_1d = _np.clip(1.0 - dist_from_centre / (sw + 1e-6), 0.0, 1.0) ** 1.5
        streak_gate = _np.broadcast_to(streak_gate_1d[None, :], (h, w)).copy()
        streak_lum = lum * streak_gate * ss
        r4 = _np.clip(r3 + streak_lum * 0.85, 0.0, 1.0)
        g4 = _np.clip(g3 + streak_lum * 0.90, 0.0, 1.0)
        b4 = _np.clip(b3 + streak_lum,        0.0, 1.0)

        # Composite at opacity
        op = float(opacity)
        new_r = r0 * (1.0 - op) + r4 * op
        new_g = g0 * (1.0 - op) + g4 * op
        new_b = b0 * (1.0 - op) + b4 * op

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        n_halo    = int((corona > 0.05).sum())
        n_velvet  = int((velvet_gate > 0.20).sum())
        n_moon    = int((bright_mask > 0.10).sum())
        n_streak  = int((streak_gate > 0.20).sum())
        print(f"    Kuindzhi Moonlit Radiance complete "
              f"(halo_px={n_halo} velvet_px={n_velvet} "
              f"moon_px={n_moon} streak_px={n_streak})")
'''

GRAVITY_DRIFT_PASS = '''
    def paint_gravity_drift_pass(
        self,
        drift_sigma_down:  float = 3.5,
        drift_sigma_up:    float = 0.6,
        thick_threshold:   float = 0.35,
        thick_power:       float = 1.40,
        drift_strength:    float = 0.55,
        opacity:           float = 0.60,
    ) -> None:
        """
        Paint Gravity Drift -- session 233 artistic improvement.

        Models the subtle physical sag of wet oil paint under gravity: thick paint
        (modelled by high luminance as a paint-height proxy) slowly spreads downward,
        softening the lower edge of each mark while leaving the upper edge crisp.
        This creates the characteristically organic quality of freshly applied impasto —
        a living surface whose forms drift fractionally under their own weight.

        Mechanism: asymmetric 1-D Gaussian blur in the vertical axis.
        A downward kernel (length = drift_sigma_down * 4, normalized) is applied
        to each column independently.  The effect is then blended back in proportion
        to a paint-thickness gate derived from luminance.

        Implementation via 1D uniform convolution approximation:
          kernel_down: 1D array of length K; values = exp(-0.5*(i/sigma_down)^2)
                       for i in [0, K) -- causal (forward/downward only)
          kernel_up  : 1D array of length K; values = exp(-0.5*(i/sigma_up)^2)
                       for i in [0, K) -- causal upward
          Both normalized to sum=1.
          Per-column, convolve each channel with (kernel_down - kernel_up) to get
          the net downward drift delta, scaled by drift_strength.

          thick_gate = clip((lum - thick_threshold) / (1 - thick_threshold), 0, 1)
                        ^ thick_power
          ch_out = ch_orig + drift_delta * thick_gate * drift_strength

        NOVEL vs. existing passes:
        (a) Asymmetric kernel (down >> up): prior anisotropic passes (batoni_silk_sheen)
            use symmetric elongated kernels along a direction; this pass uses a
            non-symmetric causal kernel that has NO symmetry -- downward spread is
            much longer than upward, producing a physically grounded asymmetric effect.
        (b) Thickness gate from luminance: only thick paint (bright zones) sags --
            thin paint and shadows stay crisp.  impasto_relief_pass models topography
            under raking light; this pass models the MOTION of thick paint over time.
        (c) Column-wise 1D convolution (axis=0, scipy.ndimage.convolve1d) rather than
            isotropic Gaussian -- first pass to use a directional 1D causal kernel.

        drift_sigma_down : Downward spread sigma in pixels.
        drift_sigma_up   : Upward counter-drift (smaller = more one-sided).
        thick_threshold  : Luminance below which paint is too thin to drift.
        thick_power      : Power shaping of thickness gate (higher = steeper).
        drift_strength   : Amplitude of the drift blend.
        opacity          : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import convolve1d as _c1d

        print("    Paint Gravity Drift pass (session 233 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Build asymmetric downward kernel
        sd = float(drift_sigma_down)
        su = float(drift_sigma_up)
        K = max(5, int(sd * 5) | 1)  # odd length
        i = _np.arange(K, dtype=_np.float32)
        k_down = _np.exp(-0.5 * (i / (sd + 1e-6)) ** 2)
        k_down /= k_down.sum()
        k_up   = _np.exp(-0.5 * (i / (su + 1e-6)) ** 2)
        k_up  /= k_up.sum()
        # Net drift = downward spread minus upward spread
        k_net = k_down - k_up  # causal positive = downward

        # Apply per-channel column-wise 1D convolution (axis=0 = vertical)
        r_drift = _c1d(r0, k_net, axis=0, mode='reflect').astype(_np.float32)
        g_drift = _c1d(g0, k_net, axis=0, mode='reflect').astype(_np.float32)
        b_drift = _c1d(b0, k_net, axis=0, mode='reflect').astype(_np.float32)

        # Thickness gate: only thick/bright paint drifts
        tt = float(thick_threshold)
        tp = float(thick_power)
        thick_gate = _np.clip(
            (lum - tt) / (1.0 - tt + 1e-6), 0.0, 1.0) ** tp

        ds = float(drift_strength)
        r1 = _np.clip(r0 + (r_drift - r0) * thick_gate * ds, 0.0, 1.0)
        g1 = _np.clip(g0 + (g_drift - g0) * thick_gate * ds, 0.0, 1.0)
        b1 = _np.clip(b0 + (b_drift - b0) * thick_gate * ds, 0.0, 1.0)

        # Composite at opacity
        op = float(opacity)
        new_r = r0 * (1.0 - op) + r1 * op
        new_g = g0 * (1.0 - op) + g1 * op
        new_b = b0 * (1.0 - op) + b1 * op

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        n_thick  = int((thick_gate > 0.15).sum())
        n_active = int((_np.abs(r_drift - r0) > 0.002).sum())
        print(f"    Paint Gravity Drift pass complete (thick_px={n_thick} active_px={n_active})")
'''


with open('stroke_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Verify passes don't already exist
assert 'kuindzhi_moonlit_radiance_pass' not in content, 'Pass already exists!'
assert 'paint_gravity_drift_pass' not in content, 'Pass already exists!'

content = content + KUINDZHI_PASS + GRAVITY_DRIFT_PASS

with open('stroke_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. stroke_engine.py new length: {len(content)} chars')
