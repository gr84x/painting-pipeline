"""Append kollwitz_charcoal_etching_pass and paint_luminance_stretch_pass to stroke_engine.py (session 247)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

KOLLWITZ_PASS = '''
    def kollwitz_charcoal_etching_pass(
        self,
        desat_str:        float = 0.85,
        warm_r:           float = 0.95,
        warm_g:           float = 0.90,
        warm_b:           float = 0.80,
        dark_r:           float = 0.14,
        dark_g:           float = 0.10,
        dark_b:           float = 0.07,
        sigmoid_k:        float = 7.0,
        shadow_thresh:    float = 0.38,
        grain_angle_deg:  float = 45.0,
        grain_strength:   float = 0.12,
        grain_kernel_len: int   = 9,
        opacity:          float = 0.88,
    ) -> None:
        r"""Kollwitz Charcoal Etching -- session 247: ONE HUNDRED AND FIFTY-EIGHTH distinct mode.

        THREE-STAGE WARM MONOCHROME SOCIAL REALISM (Käthe Kollwitz):

        Stage 1 WARM CHARCOAL MONOCHROME CONVERSION: Compute per-pixel luminance lum =
        0.299r + 0.587g + 0.114b. Build the two-endpoint warm charcoal ramp: for each
        pixel, charcoal_r = lum * warm_r + (1 - lum) * dark_r (and likewise for g, b),
        mapping lum=0 to (dark_r, dark_g, dark_b) — a deep warm black — and lum=1 to
        (warm_r, warm_g, warm_b) — a warm paper white. Blend each pixel from its original
        colour toward this charcoal image with weight = desat_str. The result is a
        desaturated near-monochrome image that retains organic warmth: shadows fall into
        sepia-dark, highlights glow with paper-white warmth.
        NOVEL: (a) DUAL-ENDPOINT WARM CHARCOAL RAMP AS DESATURATION TARGET -- first pass
        to parameterise the desaturation target as a two-colour charcoal ramp (separate
        endpoints for shadow and highlight zones) rather than achromatic grey; prior
        desaturation operations in this codebase blend toward a single neutral grey or
        toward a single warm colour (imprimatura_warmth, golden_ground); none parameterise
        separate warm endpoints for the shadow zone and the highlight zone and interpolate
        by luminance between them.

        Stage 2 SIGMOID TONAL CONTRAST EXPANSION: Recompute luminance of the post-
        desaturation image lum1. Apply the symmetric sigmoid: lum2 = 1 / (1 + exp(-k *
        (lum1 - 0.5))), with k = sigmoid_k (default 7.0). Scale all three channels by the
        contrast ratio: r_out = r_in * (lum2 / max(lum1, eps)). This expands the tonal
        range: dark pixels grow darker; bright pixels grow brighter; the overall effect
        simulates the extreme tonal contrast of Kollwitz's charcoal drawings and etching
        plates, where the deepest blacks are absolute and the highlights approach pure paper.
        NOVEL: (b) PARAMETRIC SYMMETRIC SIGMOID TONE CURVE -- first pass to apply a
        symmetric logistic sigmoid as a standalone tonal contrast stage; prior passes use
        Sobel-based edge maps, DoG-gated frequency bands, percentile-anchored linear
        stretches, or luminance-threshold gates for tonal adjustment -- none apply a smooth
        parametric sigmoid that is differentiable everywhere and symmetric around the mid-
        tone.

        Stage 3 DIRECTIONAL SHADOW GRAIN (Lithographic Mark Texture): Build a 1D
        directional kernel of length grain_kernel_len at angle grain_angle_deg using
        sub-pixel bilinear accumulation along the parametric line. Convolve the post-
        sigmoid luminance channel with this kernel to produce a blurred-along-direction
        version. Subtract the blurred version from the original luminance to obtain a
        high-frequency directional residual (the grain). In shadow pixels (lum2 <
        shadow_thresh), blend this residual grain back into each channel with weight =
        grain_strength * ((shadow_thresh - lum2) / shadow_thresh). The result is a
        visible directional mark texture in dark zones, simulating the hatched strokes of
        Kollwitz's charcoal and etching work.
        NOVEL: (c) PARAMETRIC-ANGLE DIRECTIONAL GRAIN IN SHADOW ZONE -- first pass to (i)
        construct a directional 1D convolution kernel at a user-specified angle using sub-
        pixel sampling, (ii) extract the high-frequency residual by subtracting the
        directional blur, and (iii) add this oriented texture exclusively to pixels below a
        shadow luminance threshold with luminance-proportional blending weight; no prior pass
        applies direction-specific convolutional texture gated by a shadow luminance
        threshold.

        desat_str        : Overall desaturation blend strength (0=no change, 1=full charcoal).
        warm_r/g/b       : Warm paper-white endpoint colour at luminance = 1.
        dark_r/g/b       : Warm deep-black endpoint colour at luminance = 0.
        sigmoid_k        : Steepness of sigmoid tonal contrast curve (higher = more contrast).
        shadow_thresh    : Luminance threshold below which shadow grain is applied.
        grain_angle_deg  : Angle in degrees of the directional grain kernel.
        grain_strength   : Maximum grain blend weight in the deepest shadow pixels.
        grain_kernel_len : Length of the 1D directional grain kernel (odd preferred).
        opacity          : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import convolve as _convolve

        print("    Kollwitz Charcoal Etching pass (session 247: 158th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum0 = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Warm charcoal monochrome conversion
        wr = float(warm_r); wg = float(warm_g); wb = float(warm_b)
        dr = float(dark_r); dg = float(dark_g); db = float(dark_b)
        ds = float(desat_str)
        charcoal_r = (lum0 * wr + (1.0 - lum0) * dr).astype(_np.float32)
        charcoal_g = (lum0 * wg + (1.0 - lum0) * dg).astype(_np.float32)
        charcoal_b = (lum0 * wb + (1.0 - lum0) * db).astype(_np.float32)
        r1 = _np.clip(r0 * (1.0 - ds) + charcoal_r * ds, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * (1.0 - ds) + charcoal_g * ds, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * (1.0 - ds) + charcoal_b * ds, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Sigmoid tonal contrast expansion
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        k    = float(sigmoid_k)
        lum2 = (1.0 / (1.0 + _np.exp(-k * (lum1 - 0.5)))).astype(_np.float32)
        ratio = (lum2 / (lum1 + 1e-7)).astype(_np.float32)
        r2 = _np.clip(r1 * ratio, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 * ratio, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 * ratio, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Directional shadow grain
        klen    = max(3, int(grain_kernel_len))
        ang_rad = _np.deg2rad(float(grain_angle_deg))
        dx      = _np.cos(ang_rad)
        dy      = _np.sin(ang_rad)
        # Build 1D kernel by sampling along parametric line with sub-pixel weights
        half    = klen // 2
        kernel_2d = _np.zeros((klen, klen), dtype=_np.float32)
        for i in range(klen):
            t  = float(i - half)
            px = t * dx
            py = t * dy
            ix = int(_np.floor(px))
            iy = int(_np.floor(py))
            fx = px - ix
            fy = py - iy
            for (row_off, col_off, w_val) in [
                (iy,     ix,     (1 - fy) * (1 - fx)),
                (iy,     ix + 1, (1 - fy) * fx),
                (iy + 1, ix,     fy * (1 - fx)),
                (iy + 1, ix + 1, fy * fx),
            ]:
                r_idx = row_off + half
                c_idx = col_off + half
                if 0 <= r_idx < klen and 0 <= c_idx < klen:
                    kernel_2d[r_idx, c_idx] += w_val
        k_sum = kernel_2d.sum()
        if k_sum > 1e-7:
            kernel_2d /= k_sum

        lum2_for_grain = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)
        blurred_lum    = _convolve(lum2_for_grain, kernel_2d, mode='reflect').astype(_np.float32)
        grain_residual = (lum2_for_grain - blurred_lum).astype(_np.float32)

        st        = float(shadow_thresh)
        gs        = float(grain_strength)
        shadow_mask = (lum2_for_grain < st).astype(_np.float32)
        grain_w     = _np.clip(
            shadow_mask * ((st - lum2_for_grain) / (st + 1e-7)) * gs,
            0.0, 0.5).astype(_np.float32)
        r3 = _np.clip(r2 + grain_residual * grain_w, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 + grain_residual * grain_w, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 + grain_residual * grain_w, 0.0, 1.0).astype(_np.float32)

        op    = float(opacity)
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
        mean_grain = float(_np.abs(grain_residual).mean())
        print(f"    Kollwitz Charcoal Etching complete (desat={ds:.2f} sigmoid_k={k:.1f} "
              f"angle={float(grain_angle_deg):.0f}deg shadow_thresh={st:.2f} "
              f"mean_grain={mean_grain:.4f})")
'''

LUMINANCE_STRETCH_PASS = '''
    def paint_luminance_stretch_pass(
        self,
        lo_pct:  float = 2.0,
        hi_pct:  float = 98.0,
        opacity: float = 0.80,
    ) -> None:
        r"""Paint Luminance Stretch -- session 247 artistic improvement.

        PERCENTILE-ANCHORED TONAL NORMALISATION: Compute the lo_pct and hi_pct
        percentiles of the canvas luminance (lum = 0.299r + 0.587g + 0.114b).
        Map the luminance range [p_lo, p_hi] linearly to [0, 1] by computing a scale
        factor and offset. Apply the same linear transform proportionally to all three
        channels: channel_out = clip((channel - p_lo * channel/lum) * scale, 0, 1).
        Pixels at or below the p_lo luminance percentile are driven toward black; pixels
        at or above the p_hi percentile are driven toward their maximum saturation-
        corrected value. The transform is applied per-pixel using the global percentile
        anchors, not per-channel, so hue is preserved -- only the tonal range changes.

        THREE-STAGE TONAL NORMALISATION:

        Stage 1 LUMINANCE PERCENTILE ANCHORING: Compute lum = 0.299r + 0.587g + 0.114b
        for every pixel. Find p_lo = np.percentile(lum, lo_pct) and p_hi =
        np.percentile(lum, hi_pct). If p_hi - p_lo < 0.05 (very flat image), the pass
        still runs but has minimal visible effect.

        Stage 2 LUMINANCE-PROPORTIONAL CHANNEL SCALING: Compute scale = 1.0 / (p_hi -
        p_lo + eps). For each pixel, compute the normalised luminance lum_n = clip((lum -
        p_lo) * scale, 0, 1). Scale each channel by (lum_n / max(lum, eps)): this
        brightens dark pixels (lum < p_lo → drives toward 0) and brightens bright pixels
        (lum near p_hi → drives toward maximum) while preserving their hue angle.
        NOVEL: (a) LUMINANCE-PROPORTIONAL PERCENTILE STRETCH WITH HUE PRESERVATION --
        first improvement pass to apply a percentile-anchored linear luminance stretch
        that scales all three channels together proportionally so hue is preserved; no
        prior improvement pass applies a tonal range normalisation using luminance
        percentiles; paint_color_bloom_pass expands saturation; paint_optical_vibration_
        pass adds warm-cool boundary flicker; paint_aerial_perspective_pass uses DoG
        frequency gating; paint_imprimatura_warmth_pass, paint_golden_ground_pass warm
        the palette; paint_lost_found_edges_pass refines edge contrast; none normalise
        the full tonal range via percentile anchors.

        Stage 3 OPACITY COMPOSITE: Blend result with original canvas at opacity.

        lo_pct   : Lower percentile for tonal anchor (pixels below → towards black).
        hi_pct   : Upper percentile for tonal anchor (pixels above → towards max).
        opacity  : Final composite opacity.
        """
        import numpy as _np

        print("    Paint Luminance Stretch pass (session 247 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # Stage 1: Compute luminance percentile anchors
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        p_lo = float(_np.percentile(lum, float(lo_pct)))
        p_hi = float(_np.percentile(lum, float(hi_pct)))
        span = p_hi - p_lo
        scale = 1.0 / max(span, 1e-6)

        # Stage 2: Luminance-proportional channel scaling (hue-preserving)
        lum_n = _np.clip((lum - p_lo) * scale, 0.0, 1.0).astype(_np.float32)
        ratio = (lum_n / (lum + 1e-7)).astype(_np.float32)
        r1 = _np.clip(r0 * ratio, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * ratio, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * ratio, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Opacity composite
        op    = float(opacity)
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
        lum_out = (0.299 * new_r + 0.587 * new_g + 0.114 * new_b)
        print(f"    Paint Luminance Stretch complete (p_lo={p_lo:.3f} p_hi={p_hi:.3f} "
              f"span={span:.3f} lum_out_mean={float(lum_out.mean()):.3f})")
'''

with open('stroke_engine.py', 'a', encoding='utf-8') as f:
    f.write(KOLLWITZ_PASS)
    f.write(LUMINANCE_STRETCH_PASS)

print('Done. Verifying imports...')

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'stroke_engine' in mod:
        del _sys.modules[mod]
from stroke_engine import Painter
assert hasattr(Painter, 'kollwitz_charcoal_etching_pass'), 'kollwitz_charcoal_etching_pass missing'
assert hasattr(Painter, 'paint_luminance_stretch_pass'), 'paint_luminance_stretch_pass missing'
print('Both new passes found on Painter class.')
new_line_count = open('stroke_engine.py', 'r', encoding='utf-8').read().count('\n')
print(f'stroke_engine.py now has approximately {new_line_count} lines')
