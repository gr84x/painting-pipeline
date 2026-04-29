"""Append macke_luminous_planes_pass and paint_golden_ground_pass to stroke_engine.py (session 246)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

MACKE_PASS = '''
    def macke_luminous_planes_pass(
        self,
        n_hue_zones:     int   = 8,
        sat_target:      float = 0.82,
        sat_lift_str:    float = 0.65,
        hue_jump_bright: float = 0.20,
        hue_jump_thresh: float = 0.10,
        warm_r:          float = 0.96,
        warm_g:          float = 0.84,
        warm_b:          float = 0.42,
        veil_strength:   float = 0.20,
        opacity:         float = 0.80,
    ) -> None:
        r"""Macke Luminous Planes -- session 246: ONE HUNDRED AND FIFTY-SEVENTH distinct mode.

        THREE-STAGE LUMINOUS COLOUR PLANE SIMULATION (August Macke):

        Stage 1 HUE-ZONE SATURATION NORMALISATION: Divide the hue wheel into n_hue_zones
        equal sectors (width = 360/n_hue_zones degrees). For each sector, compute the 80th-
        percentile saturation of pixels belonging to that sector. If p80 < sat_target and
        p80 > 0.01, compute a per-sector scale factor = sat_target / p80, clamped to [1, 2.5].
        Lift each pixel in the sector: s_new = clip(s * (1 + (scale - 1) * sat_lift_str), 0, 1).
        Sectors already at or above sat_target are left unchanged.
        NOVEL: (a) PER-HUE-SECTOR PERCENTILE-REFERENCED SATURATION LIFT -- first pass to
        independently normalise each hue sector's saturation toward a uniform target using
        that sector's own 80th-percentile as the reference; prior passes boost saturation
        globally (color_bloom), at warm-cool boundaries (optical_vibration), in periphery only
        (jawlensky), or not at all -- none apply per-hue-sector percentile-normalised lift.

        Stage 2 CIRCULAR HUE GRADIENT BOUNDARY BRIGHTENING: Decompose the hue angle into
        sin(hue_rad) and cos(hue_rad). Apply Sobel gradient to each component to produce
        hue_gx and hue_gy. Combine: circular_grad = sqrt(sin_gx^2 + sin_gy^2 + cos_gx^2 +
        cos_gy^2). Normalise by 99th percentile. Pixels above hue_jump_thresh are brightened:
        v_new = clip(v + boundary_map * hue_jump_bright, 0, 1).
        NOVEL: (b) CIRCULAR HUE GRADIENT BRIGHTENING AT COLOUR-PLANE BOUNDARIES -- first pass
        to (i) detect boundaries via the CIRCULAR HUE GRADIENT (sin/cos Sobel, not luminance
        Sobel) and (ii) apply BRIGHTENING rather than darkening at those boundaries; jawlensky,
        beckmann, kirchner all use luminance-gradient Sobel for edge detection and darken or
        blend toward dark at edges; none brighten at hue-jump boundaries.

        Stage 3 LUMINANCE-PROPORTIONAL WARM GOLDEN VEIL: Compute luminance lum = 0.299r +
        0.587g + 0.114b. Blend each pixel toward the warm golden colour (warm_r, warm_g,
        warm_b) with weight = lum * veil_strength. Brighter pixels absorb more of the warm
        veil, simulating Macke's golden-tan ground showing through thinner paint in lit zones.
        NOVEL: (c) LUMINANCE-WEIGHTED WARM VEIL BLEND -- first pass to blend toward a warm
        colour with weight directly proportional to existing pixel luminance; imprimatura_warmth
        applies the same warm blend uniformly; aerial_perspective uses DoG-gated tinting;
        jawlensky uses radial distance from centre; none scale the warm blend by current lum.

        n_hue_zones     : Number of equal hue sectors for saturation normalisation.
        sat_target      : Saturation target for sector lifting.
        sat_lift_str    : Interpolation strength toward scale-corrected saturation.
        hue_jump_bright : Maximum brightness lift at colour-plane boundaries.
        hue_jump_thresh : Normalised circular-gradient threshold for boundary activation.
        warm_r/g/b      : RGB components of the warm golden veil colour.
        veil_strength   : Maximum warm veil blend weight (at luminance = 1.0).
        opacity         : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import sobel as _sobel

        print("    Macke Luminous Planes pass (session 246: 157th mode)...")

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

        # Stage 1: Per-hue-zone saturation normalisation
        st_float  = float(sat_target)
        sl_float  = float(sat_lift_str)
        nz        = int(n_hue_zones)
        zone_w    = 360.0 / nz
        sat_new   = sat.copy()
        for z in range(nz):
            lo = z * zone_w
            hi = (z + 1) * zone_w
            mask = (hue >= lo) & (hue < hi)
            n_px = int(mask.sum())
            if n_px < 5:
                continue
            p80 = float(_np.percentile(sat[mask], 80))
            if p80 < st_float and p80 > 0.01:
                scale = min(st_float / p80, 2.5)
                sat_zone = sat[mask] * (1.0 + (scale - 1.0) * sl_float)
                sat_new[mask] = _np.clip(sat_zone, 0.0, 1.0).astype(_np.float32)
        sat_new = _np.clip(sat_new, 0.0, 1.0).astype(_np.float32)
        r1, g1, b1 = _hsv_to_rgb(hue, sat_new, val)

        # Stage 2: Circular hue gradient boundary brightening
        hue_rad  = _np.deg2rad(hue).astype(_np.float32)
        sin_h    = _np.sin(hue_rad).astype(_np.float32)
        cos_h    = _np.cos(hue_rad).astype(_np.float32)
        sin_gx   = _sobel(sin_h, axis=1).astype(_np.float32)
        sin_gy   = _sobel(sin_h, axis=0).astype(_np.float32)
        cos_gx   = _sobel(cos_h, axis=1).astype(_np.float32)
        cos_gy   = _sobel(cos_h, axis=0).astype(_np.float32)
        circ_grad = _np.sqrt(sin_gx**2 + sin_gy**2 + cos_gx**2 + cos_gy**2).astype(_np.float32)
        p99  = max(float(_np.percentile(circ_grad, 99)), 1e-7)
        circ_norm = _np.clip(circ_grad / p99, 0.0, 1.0).astype(_np.float32)
        jt   = float(hue_jump_thresh)
        jb   = float(hue_jump_bright)
        boundary_map = _np.clip((circ_norm - jt) / (1.0 - jt + 1e-7), 0.0, 1.0)
        hue2, sat2, val2 = _rgb_to_hsv(r1, g1, b1)
        val2_out = _np.clip(val2 + boundary_map * jb, 0.0, 1.0).astype(_np.float32)
        r2, g2, b2 = _hsv_to_rgb(hue2, sat2, val2_out)

        # Stage 3: Luminance-proportional warm golden veil
        wr   = float(warm_r)
        wg   = float(warm_g)
        wb   = float(warm_b)
        vs   = float(veil_strength)
        lum2 = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)
        veil_w = _np.clip(lum2 * vs, 0.0, 1.0).astype(_np.float32)
        r3 = _np.clip(r2 * (1.0 - veil_w) + wr * veil_w, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 * (1.0 - veil_w) + wg * veil_w, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 * (1.0 - veil_w) + wb * veil_w, 0.0, 1.0).astype(_np.float32)

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
        print(f"    Macke Luminous Planes complete (n_zones={nz} sat_target={st_float:.2f} "
              f"boundary_mean={float(boundary_map.mean()):.3f} "
              f"veil_str={vs:.2f})")
'''

GOLDEN_GROUND_PASS = '''
    def paint_golden_ground_pass(
        self,
        ground_r:         float = 0.72,
        ground_g:         float = 0.52,
        ground_b:         float = 0.22,
        midtone_str:      float = 0.28,
        shadow_thresh:    float = 0.32,
        shadow_ground_r:  float = 0.48,
        shadow_ground_g:  float = 0.28,
        shadow_ground_b:  float = 0.10,
        shadow_str:       float = 0.22,
        highlight_thresh: float = 0.76,
        highlight_r:      float = 0.98,
        highlight_g:      float = 0.92,
        highlight_b:      float = 0.72,
        highlight_str:    float = 0.14,
        opacity:          float = 0.72,
    ) -> None:
        r"""Paint Golden Ground -- session 246 artistic improvement.

        Simulates the technique of painting over a warm, coloured ground in three
        value zones: the mid-tones echo the ground colour most strongly; the shadows
        are anchored to a deeper, richer version of the ground; the highlights receive
        a subtle warm golden kiss. Together these three zones unify the palette with
        a common warm undertone, the way a warm-ochre imprimatura unifies an oil painting.

        THREE-STAGE GOLDEN GROUND ECHO:

        Stage 1 MIDTONE GROUND ECHO: Compute midtone proximity for each pixel as
        proximity = max(0, 1 - 2 * |lum - 0.5|) where lum is pixel luminance. Blend the
        pixel toward the ground colour (ground_r/g/b) with weight = proximity * midtone_str.
        Pixels near 50% luminance are pulled most strongly toward the ground; pixels at
        full light or full dark are barely affected.
        NOVEL: (a) MIDTONE-PROXIMITY-WEIGHTED GROUND BLEND -- first pass to use
        max(0, 1-2|lum-0.5|) as the blend weight toward a ground colour; no prior pass uses
        proximity-to-midpoint-luminance as its primary blend driver; imprimatura_warmth
        applies uniformly; beckmann uses edge proximity; jawlensky uses radial centroid
        distance; aerial perspective uses DoG frequency gates.

        Stage 2 SHADOW WARMTH ANCHOR: In shadow zones (lum < shadow_thresh), apply an
        additional blend toward a deeper, richer ground tone (shadow_ground_r/g/b) with
        weight = (shadow_thresh - lum) / shadow_thresh * shadow_str. Darker pixels receive
        stronger shadow anchoring.
        NOVEL: (b) SHADOW-GATED DEEP GROUND ANCHOR -- first pass to apply a distinct
        deeper-tone ground blend exclusively to shadow-value pixels using a value threshold
        gate; no prior pass applies a second, darker ground-tone blend with its own value-
        gated weight formula specifically in the shadow zone.

        Stage 3 GOLDEN HIGHLIGHT KISS: In highlight zones (lum > highlight_thresh), blend
        toward a warm near-white golden colour (highlight_r/g/b) with weight =
        (lum - highlight_thresh) / (1 - highlight_thresh) * highlight_str. Brighter
        highlights receive a stronger warm golden tint, simulating warm impasto catching
        ambient golden light.
        NOVEL: (c) HIGHLIGHT-GATED GOLDEN WARM TINT -- first pass to apply a warm near-white
        tint exclusively to pixels above an upper luminance threshold with a third, distinct
        value-gated weight formula; no prior pass handles midtone/shadow/highlight as three
        separate value zones each with their own ground-colour target and blend strength.

        ground_r/g/b      : RGB of the mid-tone ground echo colour (warm ochre default).
        midtone_str       : Blend strength for midtone ground echo.
        shadow_thresh     : Upper luminance boundary for shadow zone.
        shadow_ground_r/g/b : Darker, richer ground colour for shadow anchoring.
        shadow_str        : Blend strength for shadow zone anchor.
        highlight_thresh  : Lower luminance boundary for highlight zone.
        highlight_r/g/b   : Warm near-white golden colour for highlight kiss.
        highlight_str     : Maximum blend strength for highlight kiss.
        opacity           : Final composite opacity.
        """
        import numpy as _np

        print("    Paint Golden Ground pass (session 246 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Midtone ground echo
        gr  = float(ground_r)
        gg  = float(ground_g)
        gb  = float(ground_b)
        mts = float(midtone_str)
        proximity  = _np.clip(1.0 - 2.0 * _np.abs(lum - 0.5), 0.0, 1.0).astype(_np.float32)
        mid_w      = proximity * mts
        r1 = _np.clip(r0 + (gr - r0) * mid_w, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 + (gg - g0) * mid_w, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 + (gb - b0) * mid_w, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Shadow warmth anchor
        sgr = float(shadow_ground_r)
        sgg = float(shadow_ground_g)
        sgb = float(shadow_ground_b)
        sth = float(shadow_thresh)
        sst = float(shadow_str)
        shadow_w = _np.clip(
            _np.where(lum < sth, (sth - lum) / (sth + 1e-7) * sst, 0.0),
            0.0, 1.0).astype(_np.float32)
        r2 = _np.clip(r1 + (sgr - r1) * shadow_w, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 + (sgg - g1) * shadow_w, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 + (sgb - b1) * shadow_w, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Golden highlight kiss
        htr = float(highlight_r)
        htg = float(highlight_g)
        htb = float(highlight_b)
        hth = float(highlight_thresh)
        hts = float(highlight_str)
        highlight_w = _np.clip(
            _np.where(lum > hth, (lum - hth) / (1.0 - hth + 1e-7) * hts, 0.0),
            0.0, 1.0).astype(_np.float32)
        r3 = _np.clip(r2 + (htr - r2) * highlight_w, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 + (htg - g2) * highlight_w, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 + (htb - b2) * highlight_w, 0.0, 1.0).astype(_np.float32)

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
        mean_mid = float(mid_w.mean())
        mean_shd = float(shadow_w.mean())
        mean_hlt = float(highlight_w.mean())
        print(f"    Paint Golden Ground complete (midtone_str={mts:.2f} "
              f"shadow_str={sst:.2f} highlight_str={hts:.2f} "
              f"mean_mid_w={mean_mid:.3f} mean_shd_w={mean_shd:.3f} "
              f"mean_hlt_w={mean_hlt:.3f})")
'''

with open('stroke_engine.py', 'a', encoding='utf-8') as f:
    f.write(MACKE_PASS)
    f.write(GOLDEN_GROUND_PASS)

print('Done. Verifying imports...')

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'stroke_engine' in mod:
        del _sys.modules[mod]
from stroke_engine import Painter
assert hasattr(Painter, 'macke_luminous_planes_pass'), 'macke_luminous_planes_pass missing'
assert hasattr(Painter, 'paint_golden_ground_pass'), 'paint_golden_ground_pass missing'
print('Both new passes found on Painter class.')
new_line_count = open('stroke_engine.py', 'r', encoding='utf-8').read().count('\n')
print(f'stroke_engine.py now has approximately {new_line_count} lines')
