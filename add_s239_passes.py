"""Append dix_neue_sachlichkeit_pass (150th mode) + paint_glaze_gradient_pass to stroke_engine.py (session 239)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

DIX_PASS = r'''
    def dix_neue_sachlichkeit_pass(
        self,
        compress_strength: float = 0.45,
        midtone_gamma:     float = 1.8,
        surge_lo:          float = 0.28,
        surge_hi:          float = 0.68,
        saturation_surge:  float = 0.38,
        hi_thresh:         float = 0.78,
        hi_power:          float = 1.5,
        hi_crispness:      float = 0.55,
        opacity:           float = 0.80,
    ) -> None:
        r"""
        Dix Neue Sachlichkeit -- session 239: ONE HUNDRED AND FIFTIETH distinct mode.

        Implements Otto Dix (1891-1969) New Objectivity (Neue Sachlichkeit) tonal
        technique.  Dix\'s defining visual language: surgical midtone compression
        that collapses ambiguous grey tones toward definite light or shadow,
        heightened saturation at shadow-to-highlight transition boundaries, and
        forensic crisping of the topmost highlights to near-white -- producing the
        hard, enamel-like surface quality of his Weimar-era portraits and war paintings.

        THREE-STAGE NEW OBJECTIVITY SIMULATION:

        Stage 1 MIDTONE TONAL COMPRESSION:
        t = abs(lum - 0.5) / 0.5  (distance from neutral mid-grey, in [0,1])
        compress_gate = t ** midtone_gamma
        target = 1.0 if lum >= 0.5 else 0.0
        lum_new = lum + (target - lum) * compress_gate * compress_strength
        Each channel shifted proportionally: ch_new = ch + (ch_new/lum) * (lum_new-lum)
        Luminances close to 0.5 (compress_gate near 0) are almost unaffected;
        luminances further from 0.5 are pushed harder toward their nearest extreme.
        FIRST pass in project to use luminance-distance-from-neutral as a gate:
        (a) unlike shadow-gate passes that operate from lum=0 upward, this gate
            peaks at lum=0 AND lum=1, with minimum at lum=0.5 -- inverting the
            usual gate curve; (b) first pass where the direction of the shift
            reverses sign depending on which side of midgrey the pixel falls.

        Stage 2 BOUNDARY SATURATION SURGE:
        edge_gate = sobel_magnitude normalised to [0,1]
        zone_gate = bell on [surge_lo, surge_hi]: triangular peak at centre,
                    zero outside -- isolates the transition zone between shadow
                    and highlight (Dix\'s most characteristic region of colour).
        combined = edge_gate * zone_gate
        sat_scale = 1 + saturation_surge * combined
        lum3 = luminance of Stage 1 result; ch_sat = lum3 + (ch-lum3)*sat_scale.
        Saturation boost is strongest where there is BOTH an edge AND a mid-tone
        pixel -- exactly at shadow-to-light transitions.
        FIRST pass to boost saturation specifically at mid-tone EDGE BOUNDARIES
        (joint gate: high gradient AND transition luminance zone).  Prior
        saturation passes boost globally or in a single luminance zone.

        Stage 3 FORENSIC HIGHLIGHT CRISPING:
        hi_gate = clip((lum - hi_thresh) / (1 - hi_thresh), 0, 1) ** hi_power
        R,G,B += hi_gate * hi_crispness * (1 - channel)  -- pushes toward white.
        Simulates the enamel-hard white highlights characteristic of Dix\'s
        oil-over-tempera technique, where the topmost impasto catches light
        with surgical precision.

        NOVEL vs. existing passes:
        (a) LUMINANCE-DISTANCE-FROM-NEUTRAL COMPRESSION GATE (t=|lum-0.5|/0.5)
            with sign-reversing shift direction -- first pass where the tonal
            shift inverts sign at lum=0.5; all prior lum-gated passes use
            monotone gates (shadow or highlight only).
        (b) JOINT EDGE-AND-ZONE SATURATION GATE (sobel_mag * zone_bell) --
            first pass to boost saturation only where high gradient AND mid-tone
            luminance coincide simultaneously.
        (c) THREE-STAGE UNIFIED MODEL: midtone compression + boundary saturation
            surge + highlight crisping in one pass -- no prior pass combines
            tonal redistribution with a joint spatial-luminance saturation boost.

        compress_strength : Fraction of midtone pushed toward nearest extreme [0,1].
        midtone_gamma     : Power curve for compression gate (>1: faster at extremes).
        surge_lo/hi       : Luminance band for the saturation surge zone.
        saturation_surge  : Max saturation multiplier increase [0, 1.0].
        hi_thresh         : Luminance above which highlight crisping begins.
        hi_power          : Sharpness of highlight gate transition.
        hi_crispness      : Max push toward white in highlight zone [0, 1].
        opacity           : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import sobel as _sobel

        print("    Dix Neue Sachlichkeit pass (session 239: 150th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Midtone tonal compression
        t = (_np.abs(lum - 0.5) / 0.5).astype(_np.float32)
        compress_gate = (t ** float(midtone_gamma)).astype(_np.float32)
        target = (lum >= 0.5).astype(_np.float32)  # 1.0 for light, 0.0 for dark
        cs = float(compress_strength)
        lum_new = lum + (target - lum) * compress_gate * cs
        # Preserve chroma by shifting channels proportionally
        scale = _np.where(_np.abs(lum) > 1e-6, lum_new / (lum + 1e-6), 1.0).astype(_np.float32)
        r1 = _np.clip(r0 * scale, 0.0, 1.0)
        g1 = _np.clip(g0 * scale, 0.0, 1.0)
        b1 = _np.clip(b0 * scale, 0.0, 1.0)

        # Stage 2: Boundary saturation surge
        sx = _sobel(lum, axis=1).astype(_np.float32)
        sy = _sobel(lum, axis=0).astype(_np.float32)
        mag = _np.sqrt(sx ** 2 + sy ** 2).astype(_np.float32)
        mag_norm = mag / (mag.max() + 1e-7)

        sl, sh = float(surge_lo), float(surge_hi)
        zone_mid  = (sl + sh) * 0.5
        zone_half = (sh - sl) * 0.5 + 1e-7
        zone_gate = _np.clip(1.0 - _np.abs(lum - zone_mid) / zone_half, 0.0, 1.0).astype(_np.float32)

        combined  = (mag_norm * zone_gate).astype(_np.float32)
        ss = float(saturation_surge)
        sat_scale = (1.0 + ss * combined).astype(_np.float32)

        lum3 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        r2 = _np.clip(lum3 + (r1 - lum3) * sat_scale, 0.0, 1.0)
        g2 = _np.clip(lum3 + (g1 - lum3) * sat_scale, 0.0, 1.0)
        b2 = _np.clip(lum3 + (b1 - lum3) * sat_scale, 0.0, 1.0)

        # Stage 3: Forensic highlight crisping
        ht = float(hi_thresh)
        hp = float(hi_power)
        hc = float(hi_crispness)
        hi_gate = _np.clip((lum - ht) / (1.0 - ht + 1e-7), 0.0, 1.0) ** hp
        r3 = _np.clip(r2 + hi_gate * hc * (1.0 - r2), 0.0, 1.0)
        g3 = _np.clip(g2 + hi_gate * hc * (1.0 - g2), 0.0, 1.0)
        b3 = _np.clip(b2 + hi_gate * hc * (1.0 - b2), 0.0, 1.0)

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

        n_compressed = int((compress_gate > 0.4).sum())
        n_surged     = int((combined       > 0.2).sum())
        n_crisped    = int((hi_gate        > 0.2).sum())
        print(f"    Dix Neue Sachlichkeit complete "
              f"(compressed_px={n_compressed} surged_px={n_surged} crisped_px={n_crisped})")
'''

GLAZE_GRADIENT_PASS = r'''
    def paint_glaze_gradient_pass(
        self,
        color:         tuple = (0.58, 0.32, 0.08),
        axis:          str   = 'y',
        opacity_near:  float = 0.0,
        opacity_far:   float = 0.10,
        gamma:         float = 1.5,
        reverse:       bool  = False,
        blend_mode:    str   = 'multiply',
    ) -> None:
        r"""
        Paint Glaze Gradient -- session 239 artistic improvement.

        Traditional oil painting glazing applies a thin transparent layer of pure,
        highly diluted colour over dried paint.  A GRADIENT GLAZE varies the
        concentration of the wash along a single axis -- the artist loads a broad
        flat brush and progressively thins or thickens the wash as they work across
        the canvas.  Turner used descending warm golden glazes; Vermeer applied
        selective cool blue-grey glazes over warm imprimatura in his skies.

        AXIAL GRADIENT TRANSPARENT GLAZE:
        t = linspace(0, 1, canvas_height_or_width) along chosen axis.
        t_curved = t ** gamma  (non-linear power-curve build).
        If reverse: t_curved = (1-t) ** gamma.
        alpha(pixel) = opacity_near + (opacity_far - opacity_near) * t_curved.
        Two blend modes:
        'multiply': result = original * (1 - alpha*(1 - glaze_col))
            Deepens and tints colour; appropriate for glazes over mid/light values.
        'screen':   result = 1 - (1-original)*(1 - alpha*glaze_col)
            Lightens and adds luminosity; appropriate for glazes over darks.

        NOVEL vs. existing passes:
        (a) SPATIALLY VARYING (AXIAL GRADIENT) GLAZE OPACITY -- the existing
            glaze() method applies a single uniform opacity over the entire canvas;
            this pass creates a smooth directional build from opacity_near to
            opacity_far, modelling the physical technique of a gradient wash.
            No prior pass applies a spatially varying transparent overlay along
            a chosen axis.
        (b) GAMMA-CURVED GRADIENT RAMP -- non-linear power curve allows the glaze
            to build slowly at first then accelerate, matching natural variation
            in brush load as paint thins during the stroke.
        (c) DUAL BLEND MODES (multiply / screen) -- selects between two physically
            distinct glaze interaction models based on blend_mode parameter.

        color        : RGB glaze colour as normalised floats.
        axis         : 'y' (top-to-bottom) or 'x' (left-to-right).
        opacity_near : Glaze opacity at the near end of the gradient (t=0).
        opacity_far  : Glaze opacity at the far end of the gradient (t=1).
        gamma        : Power curve for gradient build (>1 slow start / fast end).
        reverse      : Swap near and far ends of the gradient.
        blend_mode   : 'multiply' or 'screen'.
        """
        import numpy as _np

        print("    Paint Glaze Gradient pass (session 239 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # Build 1-D ramp along chosen axis
        n = h if axis == 'y' else w
        t = _np.linspace(0.0, 1.0, n, dtype=_np.float32)
        if reverse:
            t = 1.0 - t
        t_curved = t ** float(gamma)
        on = float(opacity_near)
        of = float(opacity_far)
        alpha_1d = (on + (of - on) * t_curved).astype(_np.float32)

        if axis == 'y':
            alpha = alpha_1d[:, _np.newaxis]
        else:
            alpha = alpha_1d[_np.newaxis, :]

        gr = _np.float32(float(color[0]))
        gg = _np.float32(float(color[1]))
        gb = _np.float32(float(color[2]))

        if blend_mode == 'screen':
            r1 = _np.clip(1.0 - (1.0 - r0) * (1.0 - alpha * gr), 0.0, 1.0)
            g1 = _np.clip(1.0 - (1.0 - g0) * (1.0 - alpha * gg), 0.0, 1.0)
            b1 = _np.clip(1.0 - (1.0 - b0) * (1.0 - alpha * gb), 0.0, 1.0)
        else:  # multiply
            r1 = _np.clip(r0 * (1.0 - alpha * (1.0 - gr)), 0.0, 1.0)
            g1 = _np.clip(g0 * (1.0 - alpha * (1.0 - gg)), 0.0, 1.0)
            b1 = _np.clip(b0 * (1.0 - alpha * (1.0 - gb)), 0.0, 1.0)

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(r1 * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(g1 * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(b1 * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        alpha_mean = float(alpha_1d.mean())
        alpha_max  = float(alpha_1d.max())
        print(f"    Paint Glaze Gradient complete "
              f"(axis={axis} blend={blend_mode} "
              f"alpha_mean={alpha_mean:.3f} alpha_max={alpha_max:.3f})")
'''

with open('stroke_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'dix_neue_sachlichkeit_pass' not in content,  'Dix pass already exists!'
assert 'paint_glaze_gradient_pass'  not in content,  'Glaze gradient pass already exists!'

content = content + DIX_PASS + GLAZE_GRADIENT_PASS

with open('stroke_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. stroke_engine.py new length: {len(content)} chars')

# Verify importable
import importlib
for mod in list(sys.modules.keys()):
    if 'stroke_engine' in mod:
        del sys.modules[mod]
import stroke_engine
assert hasattr(stroke_engine.Painter, 'dix_neue_sachlichkeit_pass'),  'Dix pass missing'
assert hasattr(stroke_engine.Painter, 'paint_glaze_gradient_pass'),   'Glaze gradient pass missing'
print('Verified: both new methods present in Painter.')
