"""Append session 231 passes to stroke_engine.py."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

VRUBEL_PASS = '''
    def vrubel_crystal_facet_pass(
        self,
        facet_sigma:   float = 4.5,
        edge_thresh:   float = 0.18,
        grout_depth:   float = 0.45,
        jewel_boost:   float = 0.30,
        opacity:       float = 0.80,
    ) -> None:
        """
        Vrubel Crystal Facet -- session 231: ONE HUNDRED AND FORTY-SECOND distinct mode.

        Implements Mikhail Vrubel (1856-1910) mosaic-crystalline surface technique.
        Vrubel built forms from angular, facet-like brushstrokes separated by dark
        edges -- like a shattered stained-glass window reassembled on canvas.  The
        surface reads as a field of crystalline colour planes, not a continuous tonal
        gradation.

        Mechanism: detect region-level luminance gradient boundaries from a
        pre-smoothed field (so we find macro-scale "tile" edges, not pixel noise);
        darken at those boundaries to simulate dark grout lines between mosaic tiles;
        boost saturation in the low-gradient interior of each facet for the jewel-like
        iridescent quality.

        Stage 1 FACET EDGE DETECTION:
          lum_smooth = gaussian_filter(lum, facet_sigma);
          dx = sobel(lum_smooth, axis=1); dy = sobel(lum_smooth, axis=0);
          grad = sqrt(dx^2+dy^2); normalise to [0,1];
          edge_gate = clip(grad/edge_thresh, 0, 1)^0.7.

        Stage 2 GROUT DARKENING:
          grout_factor = 1 - edge_gate * grout_depth;
          r1 = r*grout_factor, g1 = g*grout_factor, b1 = b*grout_factor.

        Stage 3 FACET INTERIOR JEWEL BOOST:
          facet_int = 1 - edge_gate;  (high in flat interiors, zero at edges)
          sat_scale = 1 + jewel_boost * facet_int;
          lum1 = weighted-luminance(r1,g1,b1);
          r2 = clip(lum1 + (r1-lum1)*sat_scale, 0,1) etc.

        NOVEL vs. existing passes:
        (a) Pre-smoothed Sobel gradient at macro scale (facet_sigma~4-5px) targets
            region-level colour plane boundaries -- distinct from edge_definition_pass
            which operates at pixel scale with an unsharp mask;
        (b) Dual-zone treatment: grout-darkening at detected edges + jewel-saturation
            boost in flat interiors -- no prior pass does this paired treatment;
        (c) impasto_relief_pass uses directional Sobel on luminance-as-height for 3D
            raking light; this pass uses isotropic gradient magnitude for 2D mosaic
            segmentation -- orthogonal operations.

        facet_sigma  : Gaussian pre-smooth radius; larger = bigger facets.
        edge_thresh  : Normalised gradient at which grout darkening reaches full.
        grout_depth  : Strength of edge darkening (1.0 = full black grout).
        jewel_boost  : Saturation multiplier in facet interiors.
        opacity      : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, sobel as _sobel

        print("    Vrubel Crystal Facet pass (session 231 -- 142nd mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Facet edge detection from pre-smoothed luminance
        fs = float(facet_sigma)
        lum_smooth = _gf(lum, fs).astype(_np.float32)
        dx = _sobel(lum_smooth, axis=1).astype(_np.float32)
        dy = _sobel(lum_smooth, axis=0).astype(_np.float32)
        grad = _np.sqrt(dx ** 2 + dy ** 2).astype(_np.float32)
        g_max = grad.max()
        if g_max > 1e-6:
            grad = grad / g_max

        et = float(edge_thresh)
        edge_gate = _np.clip(grad / (et + 1e-6), 0.0, 1.0) ** 0.7

        # Stage 2: Grout darkening at facet edges
        gd = float(grout_depth)
        grout_factor = 1.0 - edge_gate * gd
        r1 = _np.clip(r0 * grout_factor, 0.0, 1.0)
        g1 = _np.clip(g0 * grout_factor, 0.0, 1.0)
        b1 = _np.clip(b0 * grout_factor, 0.0, 1.0)

        # Stage 3: Facet interior jewel-saturation boost
        facet_int = 1.0 - edge_gate
        jb = float(jewel_boost)
        sat_scale = 1.0 + jb * facet_int
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        r2 = _np.clip(lum1 + (r1 - lum1) * sat_scale, 0.0, 1.0)
        g2 = _np.clip(lum1 + (g1 - lum1) * sat_scale, 0.0, 1.0)
        b2 = _np.clip(lum1 + (b1 - lum1) * sat_scale, 0.0, 1.0)

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

        n_edge = int((edge_gate > 0.5).sum())
        n_facet = int((facet_int > 0.5).sum())
        print(f"    Vrubel Crystal Facet complete "
              f"(edge_px={n_edge} facet_px={n_facet})")
'''

CLARITY_PASS = '''
    def midtone_clarity_pass(
        self,
        clarity_center: float = 0.50,
        clarity_width:  float = 0.22,
        sharpness:      float = 0.55,
        blur_sigma:     float = 1.4,
        opacity:        float = 0.65,
    ) -> None:
        """
        Midtone Clarity -- session 231 artistic improvement.

        Applies a luminance-selective unsharp mask: sharpening is strongest in the
        mid-tone zone (default lum=0.50) and fades to zero in deep shadows and bright
        highlights.  This preserves the painterly softness of those extremes while
        giving the mid-tone forms (where the eye reads structural detail) crisp,
        readable definition -- a technique closely related to the Ansel Adams zone
        approach and the classical painter technique of rendering form most precisely
        in the half-lights.

        Mechanism:
          clarity_gate = exp(-0.5*((lum-clarity_center)/clarity_width)^2)  [bell-curve]
          unsharp_delta = lum - gaussian_blur(lum, blur_sigma)
          luminance delta applied: delta = clarity_gate * sharpness * unsharp_delta
          Each channel: ch += delta (luminance shift, preserves hue)

        NOVEL vs. existing passes:
        - edge_definition_pass: uniform unsharp mask applied to all pixels regardless
          of luminance (no bell-curve gate).
        - edge_quality_variation_pass: varies edge softness spatially by zone, not by
          per-pixel luminance level.
        - impasto_relief_pass: directional Sobel gradient to simulate 3D paint surface
          (R/G/B weighted differently -- no luminance gate).
        - hammershoi_grey_interior_pass: stillness haze is a SOFTENING (blur) gated
          by midtone bell; this is its complement -- midtone SHARPENING with same gate.
        - Novel: (a) luminance bell-curve gate at configurable mid-tone centre; (b)
          sharpening complement to midtone-gated blurring (no prior pass combines
          these into a single perceptual clarity tool); (c) only channel-uniform
          luminance delta applied (no colour fringing).

        clarity_center : Luminance at which sharpening is strongest (0=black, 1=white).
        clarity_width  : Bell-curve half-width; larger = broader zone of sharpening.
        sharpness      : Unsharp mask amplitude.
        blur_sigma     : Gaussian sigma for the low-pass component.
        opacity        : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Midtone Clarity pass (session 231 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Bell-curve gate: strongest sharpening at clarity_center
        cc = float(clarity_center)
        cw = float(clarity_width)
        clarity_gate = _np.exp(-0.5 * ((lum - cc) / (cw + 1e-6)) ** 2).astype(_np.float32)

        # Unsharp mask delta (luminance channel)
        bs = float(blur_sigma)
        lum_blur = _gf(lum, bs).astype(_np.float32)
        unsharp_delta = (lum - lum_blur).astype(_np.float32)

        # Gated sharpening delta
        sh = float(sharpness)
        delta = clarity_gate * sh * unsharp_delta

        # Apply luminance delta uniformly to all channels
        r1 = _np.clip(r0 + delta,        0.0, 1.0)
        g1 = _np.clip(g0 + delta,        0.0, 1.0)
        b1 = _np.clip(b0 + delta * 0.95, 0.0, 1.0)

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

        n_active = int((clarity_gate > 0.5).sum())
        n_sharp  = int((delta > 0.003).sum())
        print(f"    Midtone Clarity pass complete (active_px={n_active} sharpened_px={n_sharp})")
'''

with open('stroke_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content + VRUBEL_PASS + CLARITY_PASS

with open('stroke_engine.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Passes appended. New length: {len(new_content)} chars")
