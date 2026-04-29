"""Append session 236 passes to stroke_engine.py."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

KUPKA_PASS = r'''
    def kupka_orphic_fugue_pass(
        self,
        *,
        hue_amplitude:   float = 0.12,
        hue_period_frac: float = 0.28,
        hue_phase:       float = 0.0,
        centroid_thresh: float = 0.55,
        chroma_boost:    float = 0.28,
        mid_lum_center:  float = 0.52,
        mid_lum_width:   float = 0.22,
        opacity:         float = 0.82,
    ) -> None:
        """
        Kupka Orphic Fugue -- session 236: ONE HUNDRED AND FORTY-SEVENTH distinct mode.

        Implements Frantisek Kupka (1871-1957), Czech-French pioneer of pure
        abstraction and originator of Orphism.  Kupka's 'Amorpha: Fugue in Two
        Colors' (1912) and 'Vertical Planes in Blue and Red' (1913) use repeating
        colour themes radiating from a luminous focus -- a 'colour fugue' where
        hue rotates periodically outward from the compositional centre, like
        concentric rings of a musical canon.  Unlike Delaunay's multi-disk
        complementary pairs, Kupka's fugue is a SINGLE RADIAL OSCILLATION of
        hue across the whole canvas, creating chromatic rhythm from one focal point.

        TWO-STAGE mechanism operating entirely in HSV colour space:

        Stage 1  RADIAL HUE FUGUE (concentric hue oscillation):
          (a) Luminance centroid: cx, cy = sum(x * lum^2) / sum(lum^2) -- the
              weighted centre of luminous pixels anchors the fugue focus.
          (b) Radial distance field: r_norm = sqrt((x-cx)^2 + (y-cy)^2) / min(w,h)
          (c) Hue rotation field: delta_H = hue_amplitude * sin(2pi * r_norm /
              hue_period_frac + hue_phase) -- sinusoidal oscillation of hue
              around its original value, period set as fraction of image width.
          (d) Apply to HSV hue channel: H_out = (H_in + delta_H) mod 1.0
          Warm hues (reds, oranges) cycle through cool (blues, greens) and back,
          creating Kupka's characteristic concentric colour-ring fugue structure.

        Stage 2  CHROMATIC INTENSITY SURGE (mid-tone saturation amplification):
          bell = exp(-0.5 * ((V - mid_lum_center) / mid_lum_width)^2)
          S_out = clip(S_in * (1 + chroma_boost * bell), 0, 1)
          Bell centred at V=0.52 (true mid-value zone) drives mid-tone colours
          toward their most intense expression -- Kupka's 'colour without
          compromise' aesthetic; pure hues at maximum saturation, no neutrals.

        NOVEL vs. all existing passes:
        (a) FIRST pass to operate in HSV colour space and apply HUE ROTATION as
            its primary operation.  All prior chromatic passes (Nolde shadow
            warmth inversion, Delaunay ring fields, Delacroix complementary
            vibration, warm_cool_zone_pass, chagall_lyrical_dream, etc.) add or
            subtract fixed RGB offsets or scale RGB channel deviations -- none
            rotates the hue wheel.  HSV hue rotation is fundamentally different:
            it shifts ALL saturated pixels along the colour wheel simultaneously,
            preserving their value and saturation while cycling their hue.
        (b) LUMINANCE-CENTROID radial field: the radial origin is the luminosity-
            weighted compositional focus (centroid of lum^2), NOT the geometric
            centre or a fixed point.  This makes the fugue naturally orbit the
            most luminous element (light source, bright face, etc.).  Delaunay's
            orphist_disk_pass uses a golden-angle spiral of MULTIPLE independent
            centres each with separate complementary pairs; this pass uses ONE
            centroid with a continuous sinusoidal rotation.
        (c) Hue rotation PERIOD as fraction of image diagonal, making the fugue
            scale correctly with image dimensions.

        hue_amplitude   : Max hue rotation (0-1 hue-wheel scale; 0.12 ~ 43 deg).
        hue_period_frac : Spatial period of hue oscillation as fraction of
                          min(W,H) -- smaller = more concentric rings.
        hue_phase       : Phase offset for the sinusoidal cycle (radians).
        centroid_thresh : Luminance threshold used to weight the centroid.
        chroma_boost    : Maximum saturation scale-up at the bell peak.
        mid_lum_center  : Value (luminance) at the centre of the saturation bell.
        mid_lum_width   : Width (sigma) of the saturation bell in value units.
        opacity         : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf
        import math as _math

        print("    Kupka Orphic Fugue pass (session 236 -- 147th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        # Cairo stores BGRA
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Radial hue fugue ────────────────────────────────────────
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Luminance-weighted centroid (centroid of bright pixels)
        ct = float(centroid_thresh)
        weight = _np.clip((lum - ct) / (1.0 - ct + 1e-7), 0.0, 1.0) ** 2
        w_sum = float(weight.sum()) + 1e-12
        yy, xx = _np.mgrid[0:h, 0:w]
        cx = float((xx * weight).sum()) / w_sum
        cy = float((yy * weight).sum()) / w_sum

        # Radial distance field normalised by min(w, h)
        r_norm = _np.sqrt(((xx - cx) / min(w, h)) ** 2
                          + ((yy - cy) / min(w, h)) ** 2).astype(_np.float32)

        # Hue rotation field: sinusoidal wave outward from centroid
        tp = float(hue_period_frac)
        phase = float(hue_phase)
        delta_H = (float(hue_amplitude)
                   * _np.sin(2.0 * _math.pi * r_norm / tp + phase)
                   ).astype(_np.float32)

        # RGB → HSV (vectorised)
        Cmax = _np.maximum(_np.maximum(r0, g0), b0)
        Cmin = _np.minimum(_np.minimum(r0, g0), b0)
        delta_c = Cmax - Cmin

        V = Cmax
        S = _np.where(Cmax > 1e-7, delta_c / _np.maximum(Cmax, 1e-7),
                      0.0).astype(_np.float32)

        safe_d = _np.maximum(delta_c, 1e-7)
        H_r = ((g0 - b0) / safe_d) % 6.0
        H_g = (b0 - r0) / safe_d + 2.0
        H_b = (r0 - g0) / safe_d + 4.0
        is_r = (Cmax == r0)
        is_g = (~is_r) & (Cmax == g0)
        H_raw = _np.where(is_r, H_r, _np.where(is_g, H_g, H_b)) / 6.0
        H = _np.where(delta_c > 1e-7, H_raw % 1.0, 0.0).astype(_np.float32)

        # Apply hue rotation (stays in [0, 1))
        H_out = (H + delta_H) % 1.0

        # ── Stage 2: Chromatic intensity surge (bell saturation boost) ───────
        bell = _np.exp(-0.5 * ((V - float(mid_lum_center))
                               / float(mid_lum_width)) ** 2).astype(_np.float32)
        S_out = _np.clip(S * (1.0 + float(chroma_boost) * bell), 0.0, 1.0)

        # HSV → RGB (vectorised)
        H6 = H_out * 6.0
        I = _np.floor(H6).astype(_np.int32) % 6
        f = (H6 - _np.floor(H6)).astype(_np.float32)
        p = (V * (1.0 - S_out)).astype(_np.float32)
        q = (V * (1.0 - f * S_out)).astype(_np.float32)
        t = (V * (1.0 - (1.0 - f) * S_out)).astype(_np.float32)

        r1 = _np.where(I==0, V, _np.where(I==1, q, _np.where(I==2, p,
             _np.where(I==3, p, _np.where(I==4, t, V))))).astype(_np.float32)
        g1 = _np.where(I==0, t, _np.where(I==1, V, _np.where(I==2, V,
             _np.where(I==3, q, _np.where(I==4, p, p))))).astype(_np.float32)
        b1 = _np.where(I==0, p, _np.where(I==1, p, _np.where(I==2, t,
             _np.where(I==3, V, _np.where(I==4, V, q))))).astype(_np.float32)

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

        n_rotated = int(((_np.abs(delta_H) > 0.04) & (S > 0.08)).sum())
        n_boosted = int((bell > 0.5).sum())
        print(f"    Kupka Orphic Fugue complete "
              f"(rotated_px={n_rotated} boosted_px={n_boosted} "
              f"centroid=({cx:.1f},{cy:.1f}))")
'''

MEDIUM_POOLING_PASS = r'''
    def paint_medium_pooling_pass(
        self,
        *,
        pool_size:     int   = 5,
        pool_depth:    float = 0.045,
        pool_sat_lift: float = 0.14,
        pool_thresh:   float = 0.035,
        pool_power:    float = 0.75,
        opacity:       float = 0.62,
    ) -> None:
        """
        Paint Medium Pooling -- session 236 artistic improvement.

        Models the physical pooling of drying oil medium (linseed, stand oil) in
        the valleys between impasto brush strokes.  Oil medium flows by gravity
        and surface tension into the low points of the paint topography as it
        dries over hours.  In these 'pools' the paint is:
          (a) Slightly DARKER -- medium pooling deepens apparent colour depth.
          (b) More SATURATED -- wet pooled medium refracts more light, restoring
              the vivid colour that dry unpooled pigment loses.
        This effect is clearly visible in close examination of old master oil
        surfaces -- the low points between strokes retain a glossy, darker,
        more saturated appearance compared to the adjacent dry ridges.

        THREE-STAGE MORPHOLOGICAL MODEL:

        Stage 1  VALLEY DETECTION via morphological erosion:
          eroded = grey_erosion(lum, size=pool_size)  [local minimum field]
          valley_depth = lum - eroded                 [distance above local min]
          valley_gate = clip(1 - valley_depth/pool_thresh, 0, 1)^pool_power
          Pixels where valley_depth is SMALL (near the local minimum) are the
          actual paint valleys -- where medium pools.  Note: we are looking for
          pixels that ARE near the floor, not far above it.

        Stage 2  VALLEY DARKENING:
          R,G,B *= (1 - pool_depth * valley_gate)
          Attenuates all channels equally -- pooled medium does not shift hue,
          only darkens by increasing optical path through the medium layer.

        Stage 3  VALLEY SATURATION ENRICHMENT:
          lum3 = 0.299R + 0.587G + 0.114B (after darkening)
          R,G,B = clip(lum3 + (R,G,B - lum3) * (1 + pool_sat_lift * valley_gate))
          Boosts chroma in valleys -- refracting medium 'brings back' the
          saturation lost to dry pigment scatter, exactly as wetting a dry
          pigment cake reveals its true colour.

        NOVEL vs. existing improvement passes:
        (a) MORPHOLOGICAL EROSION (grey_erosion) -- FIRST improvement pass using
            a morphological operator.  All prior passes use Gaussian smoothing,
            Sobel edges, or additive noise.  grey_erosion provides a local-minimum
            field that is mathematically distinct from any filter used so far.
        (b) VALLEY-GATE METRIC: we detect pixels by their PROXIMITY TO LOCAL
            MINIMUM (valley_depth small), not by gradient magnitude (Sobel) or
            luminance threshold.  A pixel can be dark AND a valley, or mid-tone
            AND a valley, so this is orthogonal to luminance gating.
        (c) CO-LOCATED DARKENING + SATURATION BOOST in the valley zone models
            the two simultaneous effects of pooled medium (depth darkening and
            saturation restoration) as a single physically motivated pass.
            impasto_relief_pass applies directional Sobel relief independently.
            paint_varnish_depth_pass applies saturation at mid-lum without valley
            detection.  paint_pigment_granulation_pass uses chroma (not valley)
            for gating.  None of these capture the valley-specific dual effect.

        pool_size     : Morphological erosion kernel size (pixels; larger = wider
                        valleys detected).
        pool_depth    : Maximum luminance attenuation in valley zones [0, 0.15].
        pool_sat_lift : Maximum saturation boost in valley zones [0, 0.35].
        pool_thresh   : Valley depth threshold -- larger means less of the image
                        qualifies as 'in a valley'.
        pool_power    : Power exponent on the valley gate (higher = sharper cutoff).
        opacity       : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import grey_erosion as _erode

        print("    Paint Medium Pooling pass (session 236 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Valley detection via morphological erosion
        ps = int(pool_size)
        eroded = _erode(lum, size=ps).astype(_np.float32)
        valley_depth = (lum - eroded).astype(_np.float32)
        pt = float(pool_thresh)
        valley_gate = _np.clip(
            1.0 - valley_depth / (pt + 1e-7), 0.0, 1.0
        ) ** float(pool_power)

        # Stage 2: Valley darkening
        pd = float(pool_depth)
        r1 = _np.clip(r0 * (1.0 - pd * valley_gate), 0.0, 1.0)
        g1 = _np.clip(g0 * (1.0 - pd * valley_gate), 0.0, 1.0)
        b1 = _np.clip(b0 * (1.0 - pd * valley_gate), 0.0, 1.0)

        # Stage 3: Valley saturation enrichment
        ps2 = float(pool_sat_lift)
        lum3 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        lum3_3 = lum3[:, :, _np.newaxis]
        sat_scale = 1.0 + ps2 * valley_gate
        r2 = _np.clip(lum3 + (r1 - lum3) * sat_scale, 0.0, 1.0)
        g2 = _np.clip(lum3 + (g1 - lum3) * sat_scale, 0.0, 1.0)
        b2 = _np.clip(lum3 + (b1 - lum3) * sat_scale, 0.0, 1.0)

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

        n_valley = int((valley_gate > 0.2).sum())
        n_dark   = int((valley_gate > 0.5).sum())
        print(f"    Paint Medium Pooling complete "
              f"(valley_px={n_valley} deep_valley_px={n_dark})")
'''


with open('stroke_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'kupka_orphic_fugue_pass' not in content, 'Pass already exists!'
assert 'paint_medium_pooling_pass' not in content, 'Pass already exists!'

content = content + KUPKA_PASS + MEDIUM_POOLING_PASS

with open('stroke_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. stroke_engine.py new length: {len(content)} chars')
