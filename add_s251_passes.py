import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"C:\Users\4nick\AppData\Local\Temp\painting-pipeline"

BACON_PASS = """
    def bacon_isolated_figure_pass(
        self,
        focal_x:          float = 0.50,
        focal_y:          float = 0.50,
        rx:               float = 0.38,
        ry:               float = 0.46,
        transition_width: float = 0.08,
        exterior_strength: float = 0.72,
        smear_angle:      float = 25.0,
        smear_length:     int   = 14,
        mid_luminance:    float = 0.48,
        smear_bandwidth:  float = 0.30,
        smear_opacity:    float = 0.70,
        flat_hue:         float = 0.06,
        flat_sat:         float = 0.72,
        exterior_blend:   float = 0.58,
        opacity:          float = 0.85,
    ) -> None:
        r\"\"\"Bacon Isolated Figure -- session 251, 162nd distinct painting mode.

        THREE-STAGE ISOLATED FIGURE SMEAR:

        Stage 1 ELLIPTICAL ISOLATION VIGNETTE: Build per-pixel elliptical
        distance map from (focal_x * w, focal_y * h) with semi-axes
        (rx * min_dim, ry * min_dim). Normalise so ellipse boundary = 1.0.
        Build exterior weight: ext_w = clip((d_norm - 1.0) / transition_width,
        0, 1) smoothed by cosine curve (1 - cos(pi * t)) / 2.
        Darken exterior: r_ext = r * (1 - exterior_strength * ext_w).
        NOVEL: (a) ELLIPTICAL ISOLATION VIGNETTE -- first pass to use a
        configurable elliptical (not circular, not corner-based) spatial zone
        as primary spatial structure; vignette_pass uses corner-based quartic
        falloff; chroma_focus uses circular radial field for saturation (not
        darkening); no prior pass uses explicit ellipse with configurable
        aspect ratio (rx != ry) as primary spatial mask.

        Stage 2 DIRECTIONAL LINEAR SMEAR: Compute interior mask int_w = 1 -
        ext_w. Per-pixel luminance lum; smear weight sw = clip(1 - |lum -
        mid_luminance| / smear_bandwidth, 0, 1): smear is strongest in mid-
        tone pixels (flesh), weakest at bright highlights and deep shadows.
        Apply discrete linear motion-blur kernel of smear_length pixels at
        smear_angle degrees. NOVEL: (b) DISCRETE LINEAR MOTION-BLUR KERNEL
        WEIGHTED BY MID-TONE LUMINANCE PROXIMITY -- first pass to apply a
        directional line-averaging kernel (not Gaussian) to simulate Bacon
        rag-scrub smear technique; prior blur passes use isotropic Gaussian
        forms or structure-guided filtering.

        Stage 3 FLAT BACKGROUND TONE FIELD: In exterior zone (ext_w > 0),
        blend pixel hue toward flat_hue and saturation toward flat_sat by
        exterior_blend * ext_w. Unifies background to flat tone field --
        Bacon characteristic raw sienna, cobalt, or viridian ground.
        NOVEL: (c) HUE AND SATURATION FIELD UNIFICATION IN EXTERIOR ELLIPSE
        ZONE -- first pass to apply coordinated hue + saturation target
        blending in the exterior isolation zone.

        focal_x, focal_y   : Ellipse centre as fraction of width/height.
        rx, ry             : Ellipse semi-axes as fraction of min(w,h).
        transition_width   : Smooth transition band width (ellipse normalised).
        exterior_strength  : Darkening in exterior zone (0=none, 1=black).
        smear_angle        : Direction of motion blur in degrees (0=horizontal).
        smear_length       : Number of pixels in linear smear kernel.
        mid_luminance      : Luminance around which smear is strongest.
        smear_bandwidth    : Halfwidth of smear weight around mid_luminance.
        smear_opacity      : Smear blend strength.
        flat_hue           : Target hue for background field (0=red, 0.06=sienna).
        flat_sat           : Target saturation for background field.
        exterior_blend     : Hue/sat blend strength toward flat field.
        opacity            : Final composite opacity.
        \"\"\"
        import numpy as _np

        print("    Bacon Isolated Figure pass (session 251, 162nd mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # Stage 1: Elliptical isolation vignette
        min_dim = float(min(w, h))
        cx = float(focal_x) * w
        cy = float(focal_y) * h
        axr = max(float(rx) * min_dim, 1.0)
        axc = max(float(ry) * min_dim, 1.0)
        ys = _np.arange(h, dtype=_np.float32)
        xs = _np.arange(w, dtype=_np.float32)
        yy, xx = _np.meshgrid(ys, xs, indexing='ij')
        d_norm = _np.sqrt(((xx - cx) / axr) ** 2 + ((yy - cy) / axc) ** 2).astype(_np.float32)
        tw = max(float(transition_width), 1e-3)
        t_raw = _np.clip((d_norm - 1.0) / tw, 0.0, 1.0).astype(_np.float32)
        ext_w = ((1.0 - _np.cos(_np.pi * t_raw)) / 2.0).astype(_np.float32)
        int_w = (1.0 - ext_w).astype(_np.float32)

        es = float(exterior_strength)
        r1 = (r0 * (1.0 - es * ext_w)).astype(_np.float32)
        g1 = (g0 * (1.0 - es * ext_w)).astype(_np.float32)
        b1 = (b0 * (1.0 - es * ext_w)).astype(_np.float32)

        # Stage 2: Directional linear smear in interior
        ang_rad = float(smear_angle) * _np.pi / 180.0
        dy = float(_np.sin(ang_rad))
        dx = float(_np.cos(ang_rad))
        sl = max(int(smear_length), 1)
        half = sl // 2

        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        ml = float(mid_luminance)
        sb = max(float(smear_bandwidth), 1e-3)
        sw = _np.clip(1.0 - _np.abs(lum1 - ml) / sb, 0.0, 1.0).astype(_np.float32)

        offsets = _np.arange(-half, sl - half, dtype=_np.float32)
        off_y = offsets * dy
        off_x = offsets * dx

        acc_r = _np.zeros_like(r1)
        acc_g = _np.zeros_like(g1)
        acc_b = _np.zeros_like(b1)

        for k in range(sl):
            sy = _np.clip(_np.round(yy + off_y[k]).astype(_np.int32), 0, h - 1)
            sx = _np.clip(_np.round(xx + off_x[k]).astype(_np.int32), 0, w - 1)
            acc_r += r1[sy, sx]
            acc_g += g1[sy, sx]
            acc_b += b1[sy, sx]

        smear_r = (acc_r / sl).astype(_np.float32)
        smear_g = (acc_g / sl).astype(_np.float32)
        smear_b = (acc_b / sl).astype(_np.float32)

        so = float(smear_opacity)
        blend = so * int_w * sw
        r2 = (r1 + blend * (smear_r - r1)).astype(_np.float32)
        g2 = (g1 + blend * (smear_g - g1)).astype(_np.float32)
        b2 = (b1 + blend * (smear_b - b1)).astype(_np.float32)

        # Stage 3: Flat background tone field
        maxc  = _np.maximum(_np.maximum(r2, g2), b2)
        minc  = _np.minimum(_np.minimum(r2, g2), b2)
        delta = maxc - minc
        d_safe = _np.where(delta > 1e-8, delta, 1.0).astype(_np.float32)

        is_r  = (maxc == r2) & (delta > 1e-8)
        is_g  = (~is_r) & (maxc == g2) & (delta > 1e-8)
        is_b  = (~is_r) & (~is_g) & (maxc == b2) & (delta > 1e-8)
        hue_raw = _np.where(is_r, (g2 - b2) / d_safe, 0.0)
        hue_raw = _np.where(is_g, 2.0 + (b2 - r2) / d_safe, hue_raw)
        hue_raw = _np.where(is_b, 4.0 + (r2 - g2) / d_safe, hue_raw)
        hue = (hue_raw / 6.0 % 1.0).astype(_np.float32)
        sat = _np.where(maxc > 1e-8, delta / (maxc + 1e-8), 0.0).astype(_np.float32)
        val = maxc.astype(_np.float32)

        fh = float(flat_hue)
        fs = float(flat_sat)
        eb = float(exterior_blend)
        diff_h = ((fh - hue + 0.5) % 1.0 - 0.5).astype(_np.float32)
        blend_ext = (ext_w * eb).astype(_np.float32)
        hue3 = (hue + blend_ext * diff_h) % 1.0
        sat3 = _np.clip(sat + blend_ext * (fs - sat), 0.0, 1.0).astype(_np.float32)
        val3 = val

        h6 = hue3 * 6.0
        i  = _np.floor(h6).astype(_np.int32) % 6
        f_ = (h6 - _np.floor(h6)).astype(_np.float32)
        p_ = (val3 * (1.0 - sat3)).astype(_np.float32)
        q_ = (val3 * (1.0 - sat3 * f_)).astype(_np.float32)
        t_ = (val3 * (1.0 - sat3 * (1.0 - f_))).astype(_np.float32)
        r3 = _np.where(i == 0, val3, _np.where(i == 1, q_, _np.where(i == 2, p_,
             _np.where(i == 3, p_, _np.where(i == 4, t_, val3))))).astype(_np.float32)
        g3 = _np.where(i == 0, t_, _np.where(i == 1, val3, _np.where(i == 2, val3,
             _np.where(i == 3, q_, _np.where(i == 4, p_, p_))))).astype(_np.float32)
        b3 = _np.where(i == 0, p_, _np.where(i == 1, p_, _np.where(i == 2, t_,
             _np.where(i == 3, val3, _np.where(i == 4, val3, q_))))).astype(_np.float32)
        r3 = _np.clip(r3, 0.0, 1.0)
        g3 = _np.clip(g3, 0.0, 1.0)
        b3 = _np.clip(b3, 0.0, 1.0)

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
        int_coverage = float(int_w.mean())
        smear_active = float((blend * sw > 0.05).mean())
        ext_hue_shift = float((_np.abs(diff_h) * blend_ext).mean())
        print(f"    Bacon Isolated Figure complete (int_coverage={int_coverage:.3f} "
              f"smear_active={smear_active:.3f} ext_hue_shift={ext_hue_shift:.4f})")
"""

WARMCOOL_PASS = """
    def paint_warm_cool_separation_pass(
        self,
        warm_boost:     float = 0.28,
        cool_boost:     float = 0.24,
        warm_lum_shift: float = 0.04,
        cool_lum_shift: float = 0.03,
        opacity:        float = 0.55,
    ) -> None:
        r\"\"\"Paint Warm-Cool Separation -- session 251 artistic improvement.

        THREE-STAGE TEMPERATURE CHROMATIC PUSH:

        Stage 1 WARM-COOL HUE ZONE CLASSIFICATION: Compute per-pixel hue in
        HSV. Build warm weight warm_w as cosine proximity centred on
        warm_hue_centre=0.07 (red-orange-yellow, [0,0.16] + [0.9,1.0] wrap).
        Build cool weight cool_w as cosine proximity centred on
        cool_hue_centre=0.62 (blue-violet, [0.50,0.75]). Both weights
        modulated by saturation so achromatic pixels are unaffected.
        NOVEL: (a) DUAL HUE-ZONE WARM-COOL CLASSIFICATION -- first improvement
        pass to explicitly build separate warm-zone and cool-zone cosine
        proximity weight maps modulated by saturation; prior saturation passes
        (chroma_focus: radial; chromatic_underdark: shadow-luminance-gated;
        basquiat midtone: luminance-range) do not classify by warm/cool hue.

        Stage 2 INDEPENDENT WARM AND COOL SATURATION PUSH: Apply separate
        saturation amplifications: warm zones receive +warm_boost * warm_w,
        cool zones receive +cool_boost * cool_w. Strongly warm or cool pixels
        receive a larger saturation boost than neutral pixels, causing
        temperature poles to pull further apart in colour space.
        NOVEL: (b) DUAL INDEPENDENT TEMPERATURE-ZONE SATURATION AMPLIFICATION
        -- first improvement pass to simultaneously boost warm-zone and cool-
        zone saturation via independent per-pixel weights.

        Stage 3 TEMPERATURE-DEPENDENT LUMINOSITY ADJUSTMENT: lum_shift =
        warm_lum_shift * warm_w - cool_lum_shift * cool_w; val_new = clip(val
        + lum_shift, 0, 1). Follows perceptual temperature rule: warm colours
        appear lighter, cool colours appear heavier (used by Rubens, Delacroix,
        Venetian colorists).
        NOVEL: (c) TEMPERATURE-DEPENDENT LUMINOSITY ADJUSTMENT -- first
        improvement pass to adjust per-pixel luminosity (HSV value) based on
        warm/cool hue classification; prior passes apply luminosity changes
        based on brightness thresholds, radial position, or shadow masks.

        warm_boost     : Saturation amplification in warm hue zones.
        cool_boost     : Saturation amplification in cool hue zones.
        warm_lum_shift : Luminosity lift applied in warm zones.
        cool_lum_shift : Luminosity drop applied in cool zones.
        opacity        : Final composite opacity.
        \"\"\"
        import numpy as _np

        print("    Paint Warm-Cool Separation pass (session 251 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # Compute HSV
        maxc  = _np.maximum(_np.maximum(r0, g0), b0)
        minc  = _np.minimum(_np.minimum(r0, g0), b0)
        delta = maxc - minc
        d_safe = _np.where(delta > 1e-8, delta, 1.0).astype(_np.float32)

        is_r  = (maxc == r0) & (delta > 1e-8)
        is_g  = (~is_r) & (maxc == g0) & (delta > 1e-8)
        is_b  = (~is_r) & (~is_g) & (maxc == b0) & (delta > 1e-8)
        hue_raw = _np.where(is_r, (g0 - b0) / d_safe, 0.0)
        hue_raw = _np.where(is_g, 2.0 + (b0 - r0) / d_safe, hue_raw)
        hue_raw = _np.where(is_b, 4.0 + (r0 - g0) / d_safe, hue_raw)
        hue = (hue_raw / 6.0 % 1.0).astype(_np.float32)
        sat = _np.where(maxc > 1e-8, delta / (maxc + 1e-8), 0.0).astype(_np.float32)
        val = maxc.astype(_np.float32)

        # Stage 1: Warm-cool zone classification
        warm_center = 0.07
        warm_radius = 0.20
        dw = _np.minimum(_np.abs(hue - warm_center),
                         1.0 - _np.abs(hue - warm_center)).astype(_np.float32)
        warm_w = _np.clip(
            (_np.cos(_np.pi * _np.clip(dw / warm_radius, 0.0, 1.0)) * 0.5 + 0.5) * sat,
            0.0, 1.0
        ).astype(_np.float32)

        cool_center = 0.62
        cool_radius = 0.22
        dc = _np.abs(hue - cool_center).astype(_np.float32)
        cool_w = _np.clip(
            (_np.cos(_np.pi * _np.clip(dc / cool_radius, 0.0, 1.0)) * 0.5 + 0.5) * sat,
            0.0, 1.0
        ).astype(_np.float32)

        # Stage 2: Independent saturation push
        wb = float(warm_boost)
        cb = float(cool_boost)
        sat2 = _np.clip(sat + wb * warm_w + cb * cool_w, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Temperature luminosity adjustment
        wls = float(warm_lum_shift)
        cls_ = float(cool_lum_shift)
        lum_shift = wls * warm_w - cls_ * cool_w
        val2 = _np.clip(val + lum_shift, 0.0, 1.0).astype(_np.float32)

        # HSV -> RGB
        h6 = hue * 6.0
        i  = _np.floor(h6).astype(_np.int32) % 6
        f_ = (h6 - _np.floor(h6)).astype(_np.float32)
        p_ = (val2 * (1.0 - sat2)).astype(_np.float32)
        q_ = (val2 * (1.0 - sat2 * f_)).astype(_np.float32)
        t_ = (val2 * (1.0 - sat2 * (1.0 - f_))).astype(_np.float32)
        r2 = _np.where(i == 0, val2, _np.where(i == 1, q_, _np.where(i == 2, p_,
             _np.where(i == 3, p_, _np.where(i == 4, t_, val2))))).astype(_np.float32)
        g2 = _np.where(i == 0, t_, _np.where(i == 1, val2, _np.where(i == 2, val2,
             _np.where(i == 3, q_, _np.where(i == 4, p_, p_))))).astype(_np.float32)
        b2 = _np.where(i == 0, p_, _np.where(i == 1, p_, _np.where(i == 2, t_,
             _np.where(i == 3, val2, _np.where(i == 4, val2, q_))))).astype(_np.float32)
        r2 = _np.clip(r2, 0.0, 1.0)
        g2 = _np.clip(g2, 0.0, 1.0)
        b2 = _np.clip(b2, 0.0, 1.0)

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
        warm_area = float((warm_w > 0.1).mean())
        cool_area = float((cool_w > 0.1).mean())
        print(f"    Warm-Cool Separation complete (warm_area={warm_area:.3f} "
              f"cool_area={cool_area:.3f})")
"""

se_path = os.path.join(REPO, "stroke_engine.py")
with open(se_path, "r", encoding="utf-8") as f:
    content = f.read()

if "bacon_isolated_figure_pass" in content:
    print("bacon pass already exists, skipping")
else:
    content = content + BACON_PASS + WARMCOOL_PASS
    with open(se_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Done. stroke_engine.py new length: {len(content)} chars")