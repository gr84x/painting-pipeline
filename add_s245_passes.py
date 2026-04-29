"""Append jawlensky_abstract_head_pass and paint_optical_vibration_pass to stroke_engine.py (session 245)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

JAWLENSKY_PASS = '''
    def jawlensky_abstract_head_pass(
        self,
        inner_radius:  float = 0.35,
        outer_radius:  float = 0.55,
        warm_hue:      float = 35.0,
        cool_hue:      float = 230.0,
        warmth_str:    float = 0.50,
        cool_str:      float = 0.45,
        cool_sat_lift: float = 0.12,
        cool_val_lift: float = 0.06,
        edge_thresh:   float = 0.10,
        edge_blue_r:   float = 0.08,
        edge_blue_g:   float = 0.10,
        edge_blue_b:   float = 0.38,
        edge_snap:     float = 0.72,
        opacity:       float = 0.80,
    ) -> None:
        r"""Jawlensky Abstract Head -- session 245: ONE HUNDRED AND FIFTY-SIXTH distinct mode.

        THREE-STAGE ICONIC RADIAL WARMTH SIMULATION (Alexej von Jawlensky):

        Stage 1 RADIAL WARMTH GRADIENT: Compute the normalised radial distance of each
        pixel from the image centroid. Pixels within inner_radius (fraction of half-diagonal)
        receive a hue attraction toward warm_hue (amber/saffron ~35 deg) with strength
        (1 - dist/inner_radius) * warmth_str. This encodes Jawlensky radial inner warmth.
        NOVEL: (a) RADIAL CENTRE-TO-PERIPHERY WARMTH MAP -- first pass to apply
        inward-warm/outward-cool hue shift weighted by normalised radial distance from
        image centroid; prior passes apply uniform warm tints (imprimatura), directional
        DoG-gated tints (aerial perspective), or edge-based snaps (Beckmann armature).

        Stage 2 COOL PERIPHERAL PUSH: Pixels beyond outer_radius receive a complementary
        hue attraction toward cool_hue (blue-violet ~230 deg) with strength proportional
        to (dist-outer_radius)/(1-outer_radius+eps)*cool_str. Simultaneously, saturation
        is boosted by cool_sat_lift and value is lifted by cool_val_lift in the outer zone.
        NOVEL: (b) COMPLEMENTARY COOL OUTER PUSH -- first pass to simultaneously apply
        cool hue shift + saturation boost + value lift in the image periphery only, weighted
        by radial distance from centroid.

        Stage 3 ULTRAMARINE EDGE TINT: Detect high-gradient boundaries via normalised
        Sobel magnitude. Blend edge pixels toward ultramarine-dark (edge_blue_r/g/b)
        rather than pure black. Unlike Beckmann (strips saturation + snaps to achromatic
        black) or Kirchner (multiplicative darkening), this blends toward a chromatically
        blue dark, producing Jawlensky blue-tinted contour lines.
        NOVEL: (c) CHROMATIC BLUE EDGE BLEND -- first pass to blend gradient-detected
        edge pixels toward a configurable blue-dark rather than achromatic black.

        inner_radius  : Radial fraction of half-diagonal for warm inner zone.
        outer_radius  : Radial fraction for start of cool outer zone.
        warm_hue      : Target hue (degrees) for inner warmth attraction (~35 amber).
        cool_hue      : Target hue (degrees) for outer cool attraction (~230 blue-violet).
        warmth_str    : Maximum warm hue attraction strength at centroid.
        cool_str      : Maximum cool hue attraction strength at periphery.
        cool_sat_lift : Saturation boost in outer zone.
        cool_val_lift : Value (brightness) lift in outer zone.
        edge_thresh   : Normalised gradient threshold for blue edge activation.
        edge_blue_r/g/b : RGB components of the ultramarine edge colour.
        edge_snap     : Maximum blend strength toward edge colour at strongest edges.
        opacity       : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import sobel as _sobel

        print("    Jawlensky Abstract Head pass (session 245: 156th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        def _rgb_to_hsv(r, g, b):
            maxc = _np.maximum(r, _np.maximum(g, b)).astype(_np.float32)
            minc = _np.minimum(r, _np.minimum(g, b)).astype(_np.float32)
            v    = maxc
            diff = (maxc - minc).astype(_np.float32)
            s    = _np.where(maxc > 1e-7, diff / (maxc + 1e-7), 0.0).astype(_np.float32)
            eps  = 1e-7
            h_deg = _np.zeros_like(r, dtype=_np.float32)
            mr = (maxc == r) & (diff > eps)
            mg = (maxc == g) & ~mr & (diff > eps)
            mb = (maxc == b) & ~mr & ~mg & (diff > eps)
            h_deg[mr] = (60.0 * ((g[mr] - b[mr]) / (diff[mr] + eps))) % 360.0
            h_deg[mg] = (60.0 * ((b[mg] - r[mg]) / (diff[mg] + eps))) + 120.0
            h_deg[mb] = (60.0 * ((r[mb] - g[mb]) / (diff[mb] + eps))) + 240.0
            h_deg = h_deg % 360.0
            return h_deg, s, v

        def _hsv_to_rgb(h_deg, s, v):
            h6 = (h_deg / 60.0).astype(_np.float32)
            i  = _np.floor(h6).astype(_np.int32) % 6
            f  = (h6 - _np.floor(h6)).astype(_np.float32)
            p  = (v * (1.0 - s)).astype(_np.float32)
            q  = (v * (1.0 - f * s)).astype(_np.float32)
            t_ = (v * (1.0 - (1.0 - f) * s)).astype(_np.float32)
            r_ = _np.select([i==0,i==1,i==2,i==3,i==4],[v,q,p,p,t_], default=v)
            g_ = _np.select([i==0,i==1,i==2,i==3,i==4],[t_,v,v,q,p], default=p)
            b_ = _np.select([i==0,i==1,i==2,i==3,i==4],[p,p,t_,v,v], default=q)
            return r_.astype(_np.float32), g_.astype(_np.float32), b_.astype(_np.float32)

        # Radial distance map normalised to half-diagonal
        cy_c = (h - 1) / 2.0
        cx_c = (w - 1) / 2.0
        half_diag = _np.hypot(cy_c, cx_c)
        ys = _np.arange(h, dtype=_np.float32)
        xs = _np.arange(w, dtype=_np.float32)
        yy, xx = _np.meshgrid(ys, xs, indexing="ij")
        dist_map = _np.hypot(yy - cy_c, xx - cx_c).astype(_np.float32)
        dist_norm = _np.clip(dist_map / (half_diag + 1e-7), 0.0, 1.0).astype(_np.float32)

        hue, sat, val = _rgb_to_hsv(r0, g0, b0)

        # Stage 1: Radial warmth gradient
        ir = float(inner_radius)
        wh = float(warm_hue)
        ws = float(warmth_str)
        warm_weight = _np.clip((1.0 - dist_norm / (ir + 1e-7)), 0.0, 1.0).astype(_np.float32)
        warm_weight = _np.where(dist_norm < ir, warm_weight, 0.0).astype(_np.float32)
        raw_diff_w = wh - hue
        rot_w = _np.where(raw_diff_w > 180.0, raw_diff_w - 360.0,
                _np.where(raw_diff_w < -180.0, raw_diff_w + 360.0, raw_diff_w))
        hue1 = (hue + rot_w * warm_weight * ws) % 360.0
        r1, g1, b1 = _hsv_to_rgb(hue1, sat, val)

        # Stage 2: Cool peripheral push
        orr = float(outer_radius)
        ch_ = float(cool_hue)
        cs_ = float(cool_str)
        csl = float(cool_sat_lift)
        cvl = float(cool_val_lift)
        cool_weight = _np.clip((dist_norm - orr) / (1.0 - orr + 1e-7), 0.0, 1.0).astype(_np.float32)
        cool_weight = _np.where(dist_norm > orr, cool_weight, 0.0).astype(_np.float32)
        hue2, sat2, val2 = _rgb_to_hsv(r1, g1, b1)
        raw_diff_c = ch_ - hue2
        rot_c = _np.where(raw_diff_c > 180.0, raw_diff_c - 360.0,
                _np.where(raw_diff_c < -180.0, raw_diff_c + 360.0, raw_diff_c))
        hue2_out = (hue2 + rot_c * cool_weight * cs_) % 360.0
        sat2_out = _np.clip(sat2 + cool_weight * csl, 0.0, 1.0).astype(_np.float32)
        val2_out = _np.clip(val2 + cool_weight * cvl, 0.0, 1.0).astype(_np.float32)
        r2, g2, b2 = _hsv_to_rgb(hue2_out, sat2_out, val2_out)

        # Stage 3: Ultramarine edge tint
        lum2 = (0.299*r2 + 0.587*g2 + 0.114*b2).astype(_np.float32)
        gx = _sobel(lum2, axis=1).astype(_np.float32)
        gy = _sobel(lum2, axis=0).astype(_np.float32)
        grad_mag  = _np.hypot(gx, gy).astype(_np.float32)
        p99 = max(float(_np.percentile(grad_mag, 99)), 1e-7)
        grad_norm = _np.clip(grad_mag / p99, 0.0, 1.0).astype(_np.float32)
        et = float(edge_thresh)
        es = float(edge_snap)
        er = float(edge_blue_r)
        eg = float(edge_blue_g)
        eb = float(edge_blue_b)
        edge_weight = _np.clip((grad_norm - et) / (1.0 - et + 1e-7), 0.0, 1.0) * es
        r_out = _np.clip(r2 * (1.0 - edge_weight) + er * edge_weight, 0.0, 1.0).astype(_np.float32)
        g_out = _np.clip(g2 * (1.0 - edge_weight) + eg * edge_weight, 0.0, 1.0).astype(_np.float32)
        b_out = _np.clip(b2 * (1.0 - edge_weight) + eb * edge_weight, 0.0, 1.0).astype(_np.float32)

        op    = float(opacity)
        new_r = r0 * (1.0 - op) + r_out * op
        new_g = g0 * (1.0 - op) + g_out * op
        new_b = b0 * (1.0 - op) + b_out * op
        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()
        print(f"    Jawlensky Abstract Head complete (warmth_str={ws:.2f} "
              f"cool_str={cs_:.2f} edge_snap={es:.2f} "
              f"mean_warm={float(warm_weight.mean()):.3f} "
              f"mean_cool={float(cool_weight.mean()):.3f})")
'''

OPTICAL_VIBRATION_PASS = '''
    def paint_optical_vibration_pass(
        self,
        boundary_sigma: float = 8.0,
        diverge_str:    float = 0.35,
        vibration_str:  float = 0.28,
        warm_anchor:    float = 30.0,
        cool_anchor:    float = 210.0,
        opacity:        float = 0.72,
    ) -> None:
        r"""Paint Optical Vibration -- session 245 artistic improvement.

        Simultaneous contrast is the perceptual phenomenon theorised by Josef Albers
        in Interaction of Color (1963): colours appear to change their perceived hue
        depending on surrounding colours. The effect is strongest at warm-cool chromatic
        boundaries. Expressionists such as Jawlensky and Kirchner deliberately placed
        warm-cool pairs adjacent to maximise the optical oscillation.

        THREE-STAGE SIMULTANEOUS CONTRAST VIBRATION:

        Stage 1 WARM-COOL FIELD GRADIENT BOUNDARY DETECTION: Classify each pixel as
        warm (hue in [320,360] union [0,90] degrees) or cool (hue in [90,270] degrees).
        Apply Gaussian blur to produce a smooth warm-density field. Compute gradient
        magnitude of this field to identify warm-cool boundary zones.
        NOVEL: (a) WARM-COOL FIELD GRADIENT BOUNDARY MAP -- first pass to classify
        pixels into warm/cool chromatic fields and use the gradient of the blurred
        classification field to identify chromatic transition zones.

        Stage 2 COMPLEMENTARY HUE DIVERGENCE: At boundary zones, push warm pixels toward
        warm_anchor and cool pixels toward cool_anchor. Push = boundary_map * diverge_str.
        NOVEL: (b) BOUNDARY-GATED COMPLEMENTARY DIVERGENCE -- first pass to push warm and
        cool pixels in opposite hue directions exclusively at chromatic boundary zones.

        Stage 3 BOUNDARY SATURATION VIBRATION: Boost saturation proportionally to
        boundary_map * vibration_str at boundary zones, creating optical oscillation.
        NOVEL: (c) TRANSITION-ZONE SATURATION BOOST -- first pass to boost saturation
        specifically at warm-cool chromatic interfaces rather than globally or radially.

        boundary_sigma : Gaussian blur sigma for warm-cool field smoothing.
        diverge_str    : Hue divergence strength at boundary zones.
        vibration_str  : Saturation boost strength at boundary zones.
        warm_anchor    : Hue target for warm-side divergence (~30 deg, orange).
        cool_anchor    : Hue target for cool-side divergence (~210 deg, blue-green).
        opacity        : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gauss, sobel as _sobel

        print("    Paint Optical Vibration pass (session 245 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        def _rgb_to_hsv(r, g, b):
            maxc = _np.maximum(r, _np.maximum(g, b)).astype(_np.float32)
            minc = _np.minimum(r, _np.minimum(g, b)).astype(_np.float32)
            v    = maxc
            diff = (maxc - minc).astype(_np.float32)
            s    = _np.where(maxc > 1e-7, diff / (maxc + 1e-7), 0.0).astype(_np.float32)
            eps  = 1e-7
            hd   = _np.zeros_like(r, dtype=_np.float32)
            mr = (maxc == r) & (diff > eps)
            mg = (maxc == g) & ~mr & (diff > eps)
            mb = (maxc == b) & ~mr & ~mg & (diff > eps)
            hd[mr] = (60.0 * ((g[mr] - b[mr]) / (diff[mr] + eps))) % 360.0
            hd[mg] = (60.0 * ((b[mg] - r[mg]) / (diff[mg] + eps))) + 120.0
            hd[mb] = (60.0 * ((r[mb] - g[mb]) / (diff[mb] + eps))) + 240.0
            hd = hd % 360.0
            return hd, s, v

        def _hsv_to_rgb(hd, s, v):
            h6 = (hd / 60.0).astype(_np.float32)
            i  = _np.floor(h6).astype(_np.int32) % 6
            f  = (h6 - _np.floor(h6)).astype(_np.float32)
            p  = (v * (1.0 - s)).astype(_np.float32)
            q  = (v * (1.0 - f * s)).astype(_np.float32)
            t_ = (v * (1.0 - (1.0 - f) * s)).astype(_np.float32)
            r_ = _np.select([i==0,i==1,i==2,i==3,i==4],[v,q,p,p,t_], default=v)
            g_ = _np.select([i==0,i==1,i==2,i==3,i==4],[t_,v,v,q,p], default=p)
            b_ = _np.select([i==0,i==1,i==2,i==3,i==4],[p,p,t_,v,v], default=q)
            return r_.astype(_np.float32), g_.astype(_np.float32), b_.astype(_np.float32)

        hue, sat, val = _rgb_to_hsv(r0, g0, b0)

        # Stage 1: Warm-cool field gradient boundary detection
        is_warm = ((hue <= 90.0) | (hue >= 320.0)).astype(_np.float32)
        bs = float(boundary_sigma)
        warm_field = _gauss(is_warm, sigma=bs).astype(_np.float32)
        gx = _sobel(warm_field, axis=1).astype(_np.float32)
        gy = _sobel(warm_field, axis=0).astype(_np.float32)
        boundary_raw = _np.hypot(gx, gy).astype(_np.float32)
        p99 = max(float(_np.percentile(boundary_raw, 99)), 1e-7)
        boundary_map = _np.clip(boundary_raw / p99, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Complementary hue divergence at boundaries
        wa = float(warm_anchor)
        ca = float(cool_anchor)
        ds = float(diverge_str)
        raw_diff_warm = wa - hue
        rot_warm = _np.where(raw_diff_warm > 180.0, raw_diff_warm - 360.0,
                   _np.where(raw_diff_warm < -180.0, raw_diff_warm + 360.0, raw_diff_warm))
        raw_diff_cool = ca - hue
        rot_cool = _np.where(raw_diff_cool > 180.0, raw_diff_cool - 360.0,
                   _np.where(raw_diff_cool < -180.0, raw_diff_cool + 360.0, raw_diff_cool))
        rot_dir = _np.where(is_warm > 0.5, rot_warm, rot_cool).astype(_np.float32)
        hue_out = (hue + rot_dir * boundary_map * ds) % 360.0

        # Stage 3: Boundary saturation vibration
        vs = float(vibration_str)
        sat_out = _np.clip(sat + boundary_map * vs, 0.0, 1.0).astype(_np.float32)

        r_out, g_out, b_out = _hsv_to_rgb(hue_out, sat_out, val)
        r_out = _np.clip(r_out, 0.0, 1.0)
        g_out = _np.clip(g_out, 0.0, 1.0)
        b_out = _np.clip(b_out, 0.0, 1.0)

        op    = float(opacity)
        new_r = r0 * (1.0 - op) + r_out * op
        new_g = g0 * (1.0 - op) + g_out * op
        new_b = b0 * (1.0 - op) + b_out * op
        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()
        mean_boundary = float(boundary_map.mean())
        mean_warm = float(is_warm.mean())
        print(f"    Paint Optical Vibration complete (sigma={bs:.1f} "
              f"diverge={ds:.2f} vibration={vs:.2f} "
              f"mean_boundary={mean_boundary:.3f} "
              f"mean_warm_frac={mean_warm:.3f})")
'''

with open('stroke_engine.py', 'a', encoding='utf-8') as f:
    f.write(JAWLENSKY_PASS)
    f.write(OPTICAL_VIBRATION_PASS)

print('Done. Verifying imports...')

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'stroke_engine' in mod:
        del _sys.modules[mod]
from stroke_engine import Painter
assert hasattr(Painter, 'jawlensky_abstract_head_pass'), 'jawlensky_abstract_head_pass missing'
assert hasattr(Painter, 'paint_optical_vibration_pass'), 'paint_optical_vibration_pass missing'
print('Both new passes found on Painter class.')
new_line_count = open('stroke_engine.py', 'r', encoding='utf-8').read().count('\n')
print(f'stroke_engine.py now has approximately {new_line_count} lines')
