"""Insert morandi_dusty_vessel_pass and paint_granulation_pass
into stroke_engine.py (session 258).

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: morandi_dusty_vessel_pass ─────────────────────────────────────────

MORANDI_PASS = """
    def morandi_dusty_vessel_pass(
        self,
        dust_veil:         float = 0.55,
        compress_strength: float = 0.40,
        target_mid:        float = 0.52,
        reveal_threshold:  float = 0.72,
        reveal_strength:   float = 0.25,
        ochre_r:           float = 0.86,
        ochre_g:           float = 0.80,
        ochre_b:           float = 0.56,
        opacity:           float = 0.80,
    ) -> None:
        r\"\"\"Giorgio Morandi Dusty Still-Life -- session 258, 169th distinct mode.

        THREE-STAGE DUSTY VESSEL EFFECT INSPIRED BY MORANDI'S
        "STILL LIFE" PAINTINGS (1916-1964):

        Giorgio Morandi (1890-1964) spent almost his entire life in Bologna,
        painting the same small group of bottles, jars, and boxes with obsessive
        variation.  His technical signatures: an almost matte, powder-dry paint
        surface built from thin, re-worked layers of earth pigments over a warm
        ground; colour differences so subtle they hover at the threshold of
        perception -- warm grey against cool grey, ochre against sand; tonal
        range compressed to roughly a third of the available scale; the highest
        lights barely reach a creamy vellum; the deepest shadows rarely go below
        a warm ash grey; and a characteristic warm-ochre glow in the very
        lightest passages where the ground colour bleeds through thin paint.
        The three stages below derive from these observations.

        Stage 1 DUSTY DESATURATION VEIL: Convert each pixel from RGB to HSV
        (hue h, saturation s, value v).  Apply a luminance-weighted saturation
        reduction:
          lum = 0.299*R + 0.587*G + 0.114*B
          s_new = s * max(0, 1 - dust_veil * (1 - lum))
        Shadow pixels (low lum) lose the most saturation; light pixels retain
        slightly more colour.  The intent is Morandi's characteristic loss of
        chromatic identity in the shadows -- every colour in shadow becomes a
        version of warm grey.  Set s_new back into HSV and convert to RGB.
        NOVEL: (a) LUMINANCE-WEIGHTED SATURATION REDUCTION AS DUSTY SHADOW
        DESATURATION VEIL -- first pass to derive the saturation suppression
        factor from (1 - lum), so darker pixels are de-saturated more
        aggressively; paint_shadow_bleed_pass (s257) adds warm tint in the
        shadow zone but does not modify saturation; no prior pass applies a
        luminance-weighted saturation clamp as a dust/atmospheric effect.

        Stage 2 TONAL COMPRESSION: In luminance space, push all pixel values
        toward a target mid-tone:
          lum_new = lum + compress_strength * (target_mid - lum)
          scale = lum_new / (lum + 1e-6)  (protect against zero)
          R *= scale,  G *= scale,  B *= scale
        With target_mid ~0.52 and compress_strength ~0.40, the tonal range
        contracts toward the mid-grey: very dark pixels brighten slightly
        (ashes in Morandi never go truly black) and very light pixels are
        pulled back from stark white (Morandi's brightest lights are cream,
        not white).  The result is the narrow, velvety tonal window that
        distinguishes Morandi from all other still-life painters.
        NOVEL: (b) LUMINANCE-PUSH-TOWARD-MIDTONE TONAL COMPRESSION WITHOUT
        GAMMA CORRECTION -- first pass to compress tonal range by shifting
        individual pixel luminance toward a defined mid target via lerp and
        then scaling RGB proportionally; paint_tonal_key_pass (s255) shifts
        the overall key by a global histogram percentile adjustment; no prior
        pass applies a pixel-wise lerp of luminance toward a user-defined
        mid-tone value as its sole purpose.

        Stage 3 OCHRE GROUND REVEAL: In the lightest pixels (lum > reveal_threshold),
        blend the RGB values toward the warm ochre ground colour (ochre_r, ochre_g,
        ochre_b) at a rate proportional to how far above the threshold the pixel is:
          t = min(1, (lum - reveal_threshold) / (1 - reveal_threshold))
          reveal = reveal_strength * t
          R = R*(1-reveal) + ochre_r*reveal
          G = G*(1-reveal) + ochre_g*reveal
          B = B*(1-reveal) + ochre_b*reveal
        This simulates the glowing warm quality Morandi's paintings show in their
        brightest passages -- a consequence of thin paint over a warm ochre
        imprimatura: the ground bleeds through and tints the pale highlight.
        NOVEL: (c) LUMINANCE-GATED GROUND COLOUR BLEED IN NEAR-HIGHLIGHT PIXELS
        AS A THIN-PAINT IMPRIMATURA REVEAL -- first pass to identify pixels above
        a luminance reveal_threshold and blend them toward a user-specified warm
        ground colour proportional to their excess luminance; paint_shadow_bleed_pass
        (s257) blends toward a warm colour in shadow zones based on proximity to
        bright pixels; this stage applies the inverse: blending near-highlight
        pixels toward the ground colour as a luminance-gated glaze reveal,
        distinct from shadow zone proximity logic.

        dust_veil         : Saturation reduction amplitude (0=no dust, 1=greyscale
                            in the darkest shadows).
        compress_strength : Fraction of distance toward target_mid to move (0-1).
        target_mid        : Luminance target for compression (0-1; ~0.52 = cream).
        reveal_threshold  : Luminance above which ground colour begins to show.
        reveal_strength   : Max blend fraction toward ochre at the lightest pixels.
        ochre_r/g/b       : RGB of the warm ground colour to reveal.
        opacity           : Final composite opacity.
        \"\"\"
        import numpy as _np
        import colorsys as _cs

        print("    Morandi Dusty Vessel pass (session 258, 169th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        # Cairo BGRA ordering
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Dusty Desaturation Veil (HSV saturation reduction) ──────
        # Vectorised HSV round-trip using per-channel operations
        # max/min per pixel for value and saturation
        cmax = _np.maximum(_np.maximum(r0, g0), b0)
        cmin = _np.minimum(_np.minimum(r0, g0), b0)
        delta = (cmax - cmin).astype(_np.float32)

        # Value = cmax
        v = cmax.copy()

        # Saturation = delta / (cmax + 1e-8)
        s = _np.where(cmax > 1e-6, delta / (cmax + 1e-8), 0.0).astype(_np.float32)

        # Hue in [0, 1]
        eps = 1e-8
        hue = _np.zeros((h, w), dtype=_np.float32)
        m_r = (cmax == r0) & (delta > eps)
        m_g = (cmax == g0) & (delta > eps)
        m_b = (cmax == b0) & (delta > eps)

        hue[m_r] = (((g0[m_r] - b0[m_r]) / (delta[m_r] + eps)) % 6.0) / 6.0
        hue[m_g] = (((b0[m_g] - r0[m_g]) / (delta[m_g] + eps)) + 2.0) / 6.0
        hue[m_b] = (((r0[m_b] - g0[m_b]) / (delta[m_b] + eps)) + 4.0) / 6.0
        hue = _np.clip(hue, 0.0, 1.0)

        # Luminance-weighted saturation suppression
        dv = float(dust_veil)
        reduction = _np.maximum(0.0, 1.0 - dv * (1.0 - lum)).astype(_np.float32)
        s1 = (s * reduction).astype(_np.float32)

        # Back to RGB from HSV (s1, v)
        h6 = hue * 6.0
        i = _np.floor(h6).astype(_np.int32) % 6
        f = (h6 - _np.floor(h6)).astype(_np.float32)
        p = (v * (1.0 - s1)).astype(_np.float32)
        q = (v * (1.0 - s1 * f)).astype(_np.float32)
        t2 = (v * (1.0 - s1 * (1.0 - f))).astype(_np.float32)

        r1 = _np.select(
            [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
            [v, q, p, p, t2, v], default=v).astype(_np.float32)
        g1 = _np.select(
            [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
            [t2, v, v, q, p, p], default=v).astype(_np.float32)
        b1 = _np.select(
            [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
            [p, p, t2, v, v, q], default=v).astype(_np.float32)

        r1 = _np.clip(r1, 0.0, 1.0)
        g1 = _np.clip(g1, 0.0, 1.0)
        b1 = _np.clip(b1, 0.0, 1.0)

        # ── Stage 2: Tonal Compression ─────────────────────────────────────────
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        cs = float(compress_strength)
        tm = float(target_mid)
        lum2 = (lum1 + cs * (tm - lum1)).astype(_np.float32)
        scale = (lum2 / _np.maximum(lum1, 1e-6)).astype(_np.float32)
        r2 = _np.clip(r1 * scale, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 * scale, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 * scale, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Ochre Ground Reveal in near-highlights ────────────────────
        rt = float(reveal_threshold)
        rs_f = float(reveal_strength)
        or_ = float(ochre_r)
        og_ = float(ochre_g)
        ob_ = float(ochre_b)

        lum2_full = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)
        range_hi = max(1.0 - rt, 1e-6)
        t_reveal = _np.clip((lum2_full - rt) / range_hi, 0.0, 1.0).astype(_np.float32)
        reveal = (rs_f * t_reveal).astype(_np.float32)

        r3 = _np.clip(r2 * (1.0 - reveal) + or_ * reveal, 0.0, 1.0)
        g3 = _np.clip(g2 * (1.0 - reveal) + og_ * reveal, 0.0, 1.0)
        b3 = _np.clip(b2 * (1.0 - reveal) + ob_ * reveal, 0.0, 1.0)

        # ── Composite at opacity ───────────────────────────────────────────────
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

        reveal_px = int((t_reveal > 0.01).sum())
        print(f"    Morandi Dusty Vessel complete "
              f"(dust_veil={dust_veil:.2f}, compress={compress_strength:.2f}, "
              f"reveal_px={reveal_px})")
"""

# ── Pass 2: paint_granulation_pass (improvement) ──────────────────────────────

GRANULATION_PASS = """
    def paint_granulation_pass(
        self,
        granule_sigma:   float = 2.0,
        granule_scale:   float = 0.06,
        warm_shift:      float = 0.04,
        cool_shift:      float = 0.04,
        edge_sharpen:    float = 0.35,
        noise_seed:      int   = 42,
        opacity:         float = 0.70,
    ) -> None:
        r\"\"\"Paint Granulation -- session 258 improvement.

        THREE-STAGE PIGMENT GRANULATION SIMULATION:

        Traditional oil and watercolour painters observe that pigment particles
        of differing density settle differently on a textured surface: heavier
        particles collect in the tooth valleys (producing dark, warm particle
        concentrations) while lighter pigments stay at the peaks (producing
        cool, bright highlights in the granule structure).  This pass models
        that behaviour procedurally.

        Stage 1 TEXTURE FREQUENCY DECOMPOSITION: Separate the canvas luminance
        into a low-frequency base layer (Gaussian-blurred at granule_sigma) and
        a high-frequency residual (the difference -- the texture/detail component):
          lum_smooth = gaussian_filter(lum, sigma=granule_sigma)
          lum_detail = lum - lum_smooth
        The detail layer captures existing paint edges, brush marks, and
        impasto ridges.  The smooth layer is the large tonal mass.
        NOVEL: (a) GAUSSIAN LOW/HIGH FREQUENCY DECOMPOSITION OF CANVAS LUMINANCE
        AS A GRANULATION STRUCTURE FIELD -- first pass to use the Laplacian-of-
        Gaussian residual (lum - blur) as the spatial granule distribution field;
        paint_impasto_ridge_cast_pass uses Sobel edge of a smoothed luminance as
        an impasto relief field; no prior pass uses the absolute difference between
        luminance and its Gaussian blur as the granulation particle placement map.

        Stage 2 CHROMATIC GRANULATION: Use the detail layer (lum_detail) as
        a signed particle field: positive values = paint ridges (peaks);
        negative values = valleys.  Apply a chromatic push:
          At peaks (lum_detail > 0):  nudge toward cool (B up, R down)
            scale = granule_scale * lum_detail (normalised to max)
            R -= warm_shift * scale
            B += cool_shift * scale
          In valleys (lum_detail < 0): nudge toward warm (R up, B down)
            scale = granule_scale * abs(lum_detail) (normalised to max)
            R += warm_shift * scale
            B -= cool_shift * scale
        This is the physical inversion of naive intuition: pigment VALLEYS are
        where warm, heavy particles concentrate (the paint is thick there);
        PEAKS are exposed -- the surface reflects coolly with less pigment.
        NOVEL: (b) SIGNED DETAIL-LAYER-DRIVEN CHROMATIC PUSH WITH WARM-IN-VALLEY
        / COOL-ON-PEAK GRANULATION POLARITY -- first pass to apply opposing warm
        and cool chromatic nudges at the PEAKS and VALLEYS of a Gaussian residual
        field; paint_surface_tooth_pass (s252) adds luminance modulation based on
        a noise field for surface texture; no prior pass splits a Gaussian residual
        into signed peak/valley regions and applies opposing warm/cool channel
        pushes to each region independently.

        Stage 3 EDGE CLARITY ENHANCEMENT: To counteract the slight softening
        from the granulation process, apply an unsharp mask to the detail layer:
          lum_sharp = lum + edge_sharpen * lum_detail
        Reconstruct RGB by scaling each channel proportionally:
          scale = lum_sharp / (lum + 1e-6)
          R *= scale,  G *= scale,  B *= scale
        This restores edge definition at brush stroke boundaries and object
        contours, giving the granulated surface a crisp, resolved quality
        at high frequencies while retaining the granule texture at mid-frequency.
        NOVEL: (c) UNSHARP MASK APPLIED TO THE SAME GAUSSIAN RESIDUAL FIELD
        USED FOR GRANULATION, AS A PAIRED SHARPENING STAGE -- first pass to
        recombine the granulation residual as an unsharp mask to restore edge
        contrast after the chromatic granulation; paint_surface_tooth_pass adds
        noise-modulated luminance; no prior pass uses the same Laplacian residual
        both for chromatic granulation and as an unsharp mask in two paired stages.

        granule_sigma : Gaussian sigma for the frequency decomposition.
        granule_scale : Amplitude scaling for the chromatic granulation push.
        warm_shift    : Max warm (R+/B-) push amplitude in valley pixels.
        cool_shift    : Max cool (B+/R-) push amplitude at ridge pixels.
        edge_sharpen  : Unsharp mask strength (0=none, 1=full residual add).
        noise_seed    : RNG seed for any stochastic noise component (unused for
                        determinism; reserved for future per-channel noise).
        opacity       : Final composite opacity.
        \"\"\"
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Paint Granulation pass (session 258 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Frequency decomposition ──────────────────────────────────
        sig = max(float(granule_sigma), 0.5)
        lum_smooth = _gf(lum, sigma=sig).astype(_np.float32)
        lum_detail = (lum - lum_smooth).astype(_np.float32)

        detail_max = _np.abs(lum_detail).max()
        if detail_max < 1e-8:
            # Flat canvas -- nothing to granulate; just composite identity
            detail_norm = lum_detail
        else:
            detail_norm = (lum_detail / detail_max).astype(_np.float32)  # in [-1, 1]

        # ── Stage 2: Chromatic granulation ────────────────────────────────────
        gs = float(granule_scale)
        ws = float(warm_shift)
        cs_f = float(cool_shift)

        # Peaks: lum_detail > 0  → cool push (B up, R down)
        peak_mask = (detail_norm > 0).astype(_np.float32)
        valley_mask = (detail_norm < 0).astype(_np.float32)

        peak_strength  = detail_norm * peak_mask   * gs   # >= 0
        valley_strength = -detail_norm * valley_mask * gs   # >= 0

        r1 = _np.clip(r0 - peak_strength * ws + valley_strength * ws, 0.0, 1.0).astype(_np.float32)
        g1 = g0.copy()   # G channel largely unaffected (warm/cool is R-B axis)
        b1 = _np.clip(b0 + peak_strength * cs_f - valley_strength * cs_f, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Edge clarity unsharp mask ────────────────────────────────
        es = float(edge_sharpen)
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        lum1_sharp = _np.clip(lum1 + es * lum_detail, 0.0, 1.0).astype(_np.float32)

        scale = (lum1_sharp / _np.maximum(lum1, 1e-6)).astype(_np.float32)
        r2 = _np.clip(r1 * scale, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 * scale, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 * scale, 0.0, 1.0).astype(_np.float32)

        # ── Composite at opacity ───────────────────────────────────────────────
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

        peak_px   = int(peak_mask.sum())
        valley_px = int(valley_mask.sum())
        print(f"    Paint Granulation complete "
              f"(peaks={peak_px}, valleys={valley_px}, "
              f"edge_sharpen={edge_sharpen:.2f})")
"""

# ── Inject into stroke_engine.py ──────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

# Check if already inserted
if "morandi_dusty_vessel_pass" in src:
    print("morandi_dusty_vessel_pass already in stroke_engine.py -- nothing to do.")
else:
    # Insert before the final line of the class or at the class end
    # Find the last def in the class and append after it
    ANCHOR = "\n    def paint_shadow_bleed_pass("
    if ANCHOR not in src:
        print("ERROR: could not find insertion anchor in stroke_engine.py", file=sys.stderr)
        sys.exit(1)
    # Insert the new passes after the full shadow_bleed_pass method.
    # Strategy: find the last occurrence of the class-level methods by appending
    # before the trailing newlines at very end of file.
    src = src.rstrip("\n") + "\n" + MORANDI_PASS + "\n" + GRANULATION_PASS + "\n"
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(src)
    print("Inserted morandi_dusty_vessel_pass and paint_granulation_pass into stroke_engine.py.")

if "paint_granulation_pass" in src:
    print("paint_granulation_pass confirmed present.")
