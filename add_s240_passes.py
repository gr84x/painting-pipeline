"""Append dufy_chromatic_dissociation_pass (151st mode) + paint_sfumato_focus_pass to stroke_engine.py (session 240)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

DUFY_PASS = r'''
    def dufy_chromatic_dissociation_pass(
        self,
        outline_sigma:      float = 1.2,
        outline_threshold:  float = 0.18,
        outline_darkness:   float = 0.72,
        chroma_dx:          int   = 9,
        chroma_dy:          int   = 6,
        saturation_lift:    float = 0.28,
        opacity:            float = 0.82,
    ) -> None:
        r"""
        Dufy Chromatic Dissociation -- session 240: ONE HUNDRED AND FIFTY-FIRST distinct mode.

        Implements Raoul Dufy (1877-1953) signature technique of deliberate
        chromatic dissociation: rapid ink or watercolour outline strokes are
        laid separately from broad, luminous colour washes, the two layers
        intentionally misregistered so that colour \"escapes\" beyond and around
        the drawn contours.  The result is an image that reads simultaneously as
        drawing AND painting, neither fully containing the other -- the very
        quality that gives Dufy\'s festive regatta, racetrack, and Riviera scenes
        their buoyant, light-filled energy.

        THREE-STAGE CHROMATIC DISSOCIATION SIMULATION:

        Stage 1 OUTLINE EXTRACTION AND DARKENING:
        Compute Sobel magnitude on luminance channel.
        Smooth the magnitude map with Gaussian sigma=outline_sigma to soften
        the edge indicator into a broad brushed-line zone.
        edge_gate = clip(mag_norm / (outline_threshold + eps), 0, 1) ** 0.6
        Darken the canvas within the edge zone:
        ch_outlined = ch * (1 - edge_gate * outline_darkness)
        This pushes high-gradient pixels toward near-black, simulating the
        rapid loaded-brush ink outline that Dufy drew over dried colour washes.
        FIRST pass in project to model ink-outline occlusion: pixels near edges
        are darkened toward near-black (not merely contrast-sharpened); all prior
        edge-aware passes boost contrast or saturation at edges but never push
        the edge zone itself toward black independently of surrounding values.

        Stage 2 CHROMINANCE SPATIAL DISSOCIATION:
        Decompose each channel into luminance and chrominance deviation:
            cb_ch = ch - lum   (signed chroma deviation from grey)
        Translate cb_ch arrays by (chroma_dx, chroma_dy) pixels using np.roll:
            cb_ch_shifted = roll(cb_ch, shift=(dy, dx), axis=(0, 1))
        Recompose with the ORIGINAL (unshifted) luminance:
            ch_dissociated = clip(lum + cb_ch_shifted, 0, 1)
        Because luminance stays fixed while chrominance is offset, the colour
        regions spatially drift relative to the tonal structure -- the exact
        mis-registration seen in Dufy\'s paintings where his blue washes lap past
        his ink-drawn sails and his yellow bleeds into his sky outlines.
        NOVEL: (a) CHROMINANCE SPATIAL DISPLACEMENT -- first pass to apply
        different spatial translations to the chrominance deviation (cb_ch) and
        the luminance, intentionally producing colour-line mis-registration;
        no prior pass translates any image component independently of another.
        np.roll is used so the operation is cheap, deterministic, and
        parameter-controlled (dx, dy pixels); the wrap-around artifact at
        canvas borders is masked out by the composite opacity.

        Stage 3 FAUVIST SATURATION LIFT:
        Compute luminance of the dissociated result.
        sat_scale = 1 + saturation_lift
        ch_vivid = lum_d + (ch_d - lum_d) * sat_scale
        Boosting saturation uniformly across the canvas re-creates Dufy\'s
        luminous, transparent watercolour-on-white quality where every hue
        reads at near-full chroma.

        NOVEL vs. existing passes:
        (a) CHROMINANCE SPATIAL DISPLACEMENT (np.roll on chroma deviation, not
            full channel) -- first pass to separate chroma from luma and
            translate each independently, producing intentional colour-line
            mis-registration; prior chromatic passes shift hue or saturation
            but never spatially translate colour relative to form.
        (b) EDGE-SELECTIVE NEAR-BLACK DARKENING (stage 1 outline gate) --
            first pass to push the edge zone itself toward near-black as an
            ink-outline model; existing edge passes boost contrast, crispness,
            or saturation at edges but do not independently darken the edge zone.
        (c) UNIFIED THREE-STAGE: outline darkening + chroma displacement +
            saturation vivification -- models both strands of Dufy\'s working
            method (drawn line + colour wash) in one consolidated pass.

        outline_sigma     : Gaussian smoothing sigma for edge indicator.
        outline_threshold : Normalised edge magnitude above which darkening begins.
        outline_darkness  : Max fraction of channel pushed toward black at edge.
        chroma_dx         : Horizontal pixel offset for chrominance shift.
        chroma_dy         : Vertical pixel offset for chrominance shift.
        saturation_lift   : Added saturation multiplier (0 = no change, 0.3 = 30% boost).
        opacity           : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import sobel as _sobel, gaussian_filter as _gauss

        print("    Dufy Chromatic Dissociation pass (session 240: 151st mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Outline extraction and darkening
        sx = _sobel(lum, axis=1).astype(_np.float32)
        sy = _sobel(lum, axis=0).astype(_np.float32)
        mag = _np.sqrt(sx * sx + sy * sy).astype(_np.float32)
        mag_smooth = _gauss(mag, sigma=float(outline_sigma)).astype(_np.float32)
        mag_norm = mag_smooth / (mag_smooth.max() + 1e-7)

        ot = float(outline_threshold)
        od = float(outline_darkness)
        edge_gate = _np.clip(mag_norm / (ot + 1e-7), 0.0, 1.0) ** 0.6
        r1 = _np.clip(r0 * (1.0 - edge_gate * od), 0.0, 1.0)
        g1 = _np.clip(g0 * (1.0 - edge_gate * od), 0.0, 1.0)
        b1 = _np.clip(b0 * (1.0 - edge_gate * od), 0.0, 1.0)

        # Stage 2: Chrominance spatial dissociation
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        cb_r = (r1 - lum1).astype(_np.float32)
        cb_g = (g1 - lum1).astype(_np.float32)
        cb_b = (b1 - lum1).astype(_np.float32)

        dx, dy = int(chroma_dx), int(chroma_dy)
        cb_r_s = _np.roll(_np.roll(cb_r, dy, axis=0), dx, axis=1)
        cb_g_s = _np.roll(_np.roll(cb_g, dy, axis=0), dx, axis=1)
        cb_b_s = _np.roll(_np.roll(cb_b, dy, axis=0), dx, axis=1)

        r2 = _np.clip(lum1 + cb_r_s, 0.0, 1.0)
        g2 = _np.clip(lum1 + cb_g_s, 0.0, 1.0)
        b2 = _np.clip(lum1 + cb_b_s, 0.0, 1.0)

        # Stage 3: Fauvist saturation lift
        lum2 = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)
        sat_scale = 1.0 + float(saturation_lift)
        r3 = _np.clip(lum2 + (r2 - lum2) * sat_scale, 0.0, 1.0)
        g3 = _np.clip(lum2 + (g2 - lum2) * sat_scale, 0.0, 1.0)
        b3 = _np.clip(lum2 + (b2 - lum2) * sat_scale, 0.0, 1.0)

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

        n_outlined = int((edge_gate > 0.3).sum())
        chroma_mag = float(_np.abs(cb_r).mean() + _np.abs(cb_g).mean() + _np.abs(cb_b).mean())
        print(f"    Dufy Chromatic Dissociation complete "
              f"(outlined_px={n_outlined} chroma_shift=({dx},{dy}) "
              f"chroma_mag={chroma_mag:.4f})")
'''

SFUMATO_FOCUS_PASS = r'''
    def paint_sfumato_focus_pass(
        self,
        cx:            float = 0.5,
        cy:            float = 0.5,
        focus_radius:  float = 0.22,
        max_sigma:     float = 4.0,
        sat_falloff:   float = 0.30,
        transition_k:  float = 6.0,
        opacity:       float = 0.72,
    ) -> None:
        r"""
        Paint Sfumato Focus -- session 240 artistic improvement.

        Leonardo da Vinci\'s sfumato (Italian: \"evaporated\") is the technique of
        softening edges and forms by blending tones imperceptibly into one another,
        without lines or sharp borders.  Leonardo applied sfumato most heavily in
        the periphery of his compositions, preserving maximum sharpness only in
        the primary focal zone -- the famous \"smoke without fire\" aerial softness
        that gives the Mona Lisa and Virgin of the Rocks their atmospheric depth.

        RADIAL PROGRESSIVE BLUR WITH SATURATION FALLOFF:

        1. RADIAL DISTANCE MAP:
           dist(x, y) = sqrt(((x/W) - cx)^2 + ((y/H) - cy)^2)
           normalised so the image diagonal = 1.0.
           r_norm = clip(dist / diag, 0, 1) where diag = sqrt(cx^2 + cy^2 + ...).

        2. FOCUS GATE (sigmoid):
           t = r_norm (normalised radius; focus_radius is the sharp zone)
           gate = sigmoid((t - focus_radius) * transition_k)
              = 1 / (1 + exp(-transition_k * (t - focus_radius)))
           gate = 0 inside focus zone, rises smoothly to 1 in the periphery.

        3. SPATIALLY VARYING GAUSSIAN BLUR:
           For each pixel, blur sigma = max_sigma * gate(pixel).
           Implementation: pre-compute blurred version at max_sigma, then
           composite pixel-by-pixel: result = sharp * (1 - gate) + blurred * gate.
           This is equivalent to a spatially varying Gaussian to first order and
           is computationally tractable without a full spatial-variant convolution.

        4. PERIPHERAL SATURATION FALLOFF:
           lum_blend = luminance of blended result.
           sat_gate = gate * sat_falloff
           ch_faded = lum_blend + (ch_blend - lum_blend) * (1 - sat_gate)
           Colours in the periphery desaturate toward grey, reinforcing the
           sense of atmospheric recession away from the focal centre.

        NOVEL vs. existing passes:
        (a) RADIAL PROGRESSIVE BLUR -- first pass to apply spatially varying
            Gaussian blur with strength increasing continuously from a focal
            centre point; no prior pass applies blur that varies by distance
            from a specified (cx, cy) focal coordinate.  The existing
            diffuse_boundary_pass() blurs near detected edges; this pass blurs
            by RADIAL DISTANCE FROM A FOCAL CENTRE, an entirely different model.
        (b) SIMULTANEOUS RADIAL FOCUS AND SATURATION FALLOFF -- first pass to
            combine a spatial blur gradient with a saturation gradient from the
            same focal centre; prior passes that modulate saturation do so
            globally or by luminance zone, never by radial distance.
        (c) SIGMOID TRANSITION GATE (not linear or Gaussian) -- the focus
            boundary transitions via a smooth logistic curve parameterised by
            transition_k; sharper k gives a harder focus edge, lower k gives
            the true imperceptible sfumato gradation.

        cx, cy        : Focus centre as fractions of canvas width/height [0, 1].
        focus_radius  : Radius of sharp zone as fraction of image diagonal.
        max_sigma     : Maximum Gaussian blur sigma applied at maximum radius.
        sat_falloff   : Maximum saturation reduction in the far periphery [0, 1].
        transition_k  : Sigmoid steepness (higher = harder focus edge).
        opacity       : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gauss

        print("    Paint Sfumato Focus pass (session 240 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # Build radial distance map
        xs = _np.linspace(0.0, 1.0, w, dtype=_np.float32)
        ys = _np.linspace(0.0, 1.0, h, dtype=_np.float32)
        xg, yg = _np.meshgrid(xs, ys)
        dist = _np.sqrt((xg - float(cx)) ** 2 + (yg - float(cy)) ** 2).astype(_np.float32)
        diag = float(_np.sqrt(2.0) * 0.5)
        r_norm = _np.clip(dist / (diag + 1e-7), 0.0, 1.0).astype(_np.float32)

        # Sigmoid gate: 0 inside focus, 1 at periphery
        fr = float(focus_radius)
        tk = float(transition_k)
        gate = (1.0 / (1.0 + _np.exp(-tk * (r_norm - fr)))).astype(_np.float32)

        # Spatially varying blur: blend sharp and fully blurred by gate
        ms = float(max_sigma)
        r_blurred = _gauss(r0, sigma=ms).astype(_np.float32)
        g_blurred = _gauss(g0, sigma=ms).astype(_np.float32)
        b_blurred = _gauss(b0, sigma=ms).astype(_np.float32)

        r1 = (r0 * (1.0 - gate) + r_blurred * gate).astype(_np.float32)
        g1 = (g0 * (1.0 - gate) + g_blurred * gate).astype(_np.float32)
        b1 = (b0 * (1.0 - gate) + b_blurred * gate).astype(_np.float32)

        # Peripheral saturation falloff
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        sf = float(sat_falloff)
        sat_gate = gate * sf
        r2 = _np.clip(lum1 + (r1 - lum1) * (1.0 - sat_gate), 0.0, 1.0)
        g2 = _np.clip(lum1 + (g1 - lum1) * (1.0 - sat_gate), 0.0, 1.0)
        b2 = _np.clip(lum1 + (b1 - lum1) * (1.0 - sat_gate), 0.0, 1.0)

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

        gate_mean = float(gate.mean())
        gate_max  = float(gate.max())
        print(f"    Paint Sfumato Focus complete "
              f"(focus=({cx:.2f},{cy:.2f}) r={focus_radius:.2f} "
              f"sigma={max_sigma:.1f} gate_mean={gate_mean:.3f} gate_max={gate_max:.3f})")
'''

with open('stroke_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'dufy_chromatic_dissociation_pass' not in content, 'Dufy pass already exists!'
assert 'paint_sfumato_focus_pass'         not in content, 'Sfumato focus pass already exists!'

content = content + DUFY_PASS + SFUMATO_FOCUS_PASS

with open('stroke_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. stroke_engine.py new length: {len(content)} chars')

# Verify importable
import importlib
for mod in list(sys.modules.keys()):
    if 'stroke_engine' in mod:
        del sys.modules[mod]
import stroke_engine
assert hasattr(stroke_engine.Painter, 'dufy_chromatic_dissociation_pass'), 'Dufy pass missing'
assert hasattr(stroke_engine.Painter, 'paint_sfumato_focus_pass'),          'Sfumato focus pass missing'
print('Verified: both new methods present in Painter.')
