"""Insert foujita_milky_ground_contour_pass and paint_sfumato_contour_dissolution_pass
into stroke_engine.py (session 260).

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: foujita_milky_ground_contour_pass ─────────────────────────────────

FOUJITA_PASS = """
    def foujita_milky_ground_contour_pass(
        self,
        ivory_r:            float = 0.97,
        ivory_g:            float = 0.95,
        ivory_b:            float = 0.88,
        ivory_threshold:    float = 0.70,
        ivory_strength:     float = 0.55,
        contour_threshold:  float = 0.06,
        contour_width:      int   = 1,
        contour_darkness:   float = 0.72,
        hatch_spacing:      int   = 4,
        hatch_amplitude:    float = 0.035,
        hatch_sigma:        float = 0.8,
        noise_seed:         int   = 260,
        opacity:            float = 0.78,
    ) -> None:
        r\"\"\"Tsuguharu Foujita Milky Ground Contour -- session 260, 171st distinct mode.

        THREE-STAGE JAPANESE-FRENCH MILKY IVORY TECHNIQUE INSPIRED BY
        FOUJITA'S OIL PAINTINGS (1918-1960):

        Tsuguharu Foujita (1886-1968) was the Japanese painter of the Ecole de
        Paris celebrated for a unique oil technique combining Japanese ink-drawing
        precision with Western oil paint.  His most famous innovation was a
        luminous milky-white ground achieved by repeated fine sanding of ivory-
        tinted titanium-white grounds and glazing with creamy, almost dry paint.
        This gave his nudes, cats, and figures a porcelain glow distinct from all
        Western painting.  He applied contour lines not with charcoal but with a
        very fine sable brush in oil paint -- thin, unwavering Japanese-ink lines
        that defined volumes without chiaroscuro shading.  Across pale surfaces
        he built fine directional micro-texture marks (like cat-fur hatching) using
        individual tiny brushmarks aligned to surface contour and hair direction.
        The three stages below model these three phenomena.

        Stage 1 MILKY IVORY GROUND LIFT: Foujita's prepared grounds glowed with
        a warm ivory luminosity from within the paint film.  Model this by lifting
        highlight regions toward the target ivory color (ivory_r, ivory_g, ivory_b).
        For each pixel, compute:
          lum = 0.299*R + 0.587*G + 0.114*B
          If lum > ivory_threshold:
            weight = ivory_strength * (lum - ivory_threshold) / (1 - ivory_threshold + 1e-6)
            R_new = R * (1 - weight) + ivory_r * weight
            G_new = G * (1 - weight) + ivory_g * weight
            B_new = B * (1 - weight) + ivory_b * weight
          Else: pass through unchanged
        This concentrates the ivory warmth in the luminous highlight passages,
        precisely where Foujita's prepared ground showed through the thin paint.
        NOVEL: (a) HIGHLIGHT-TARGETED WARM IVORY TONE DRIFT PROPORTIONAL TO
        LUMINANCE ABOVE A THRESHOLD -- first pass to blend highlights specifically
        toward a target ivory color with per-pixel weight proportional to how far
        each pixel's luminance exceeds the threshold; paint_tonal_key_pass (s255)
        shifts whole histogram; no prior pass isolates above-threshold pixels and
        blends them toward a specific warm ivory target color.

        Stage 2 JAPANESE INK CONTOUR TRACING: Foujita's sable-brush ink lines
        are the structural skeleton of his images -- placed precisely at tonal
        boundaries where dark meets light.  Model this by computing a Sobel-based
        gradient magnitude of the current luminance channel, normalising it, and
        darkening pixels where the normalised gradient exceeds contour_threshold:
          gx = Sobel(lum, axis=1)    (horizontal derivative)
          gy = Sobel(lum, axis=0)    (vertical derivative)
          grad = sqrt(gx^2 + gy^2)
          grad_norm = grad / (grad.max() + 1e-6)  (in [0,1])
          contour_mask = (grad_norm > contour_threshold).astype(float)
          if contour_width > 1: dilate mask by contour_width pixels (binary dilation)
          darkness_weight = contour_darkness * contour_mask
          R_new = R * (1 - darkness_weight)   (darkening toward black)
          G_new = G * (1 - darkness_weight)
          B_new = B * (1 - darkness_weight)
        This produces hair-thin dark contours at all significant tonal transitions,
        exactly replicating the structural role of Foujita's sable-brush oil lines.
        NOVEL: (b) SOBEL-GRADIENT CONTOUR MAP DARKENED AS JAPANESE-INK SABLE LINE
        SIMULATION -- first pass to use normalised Sobel gradient magnitude to
        construct a binary contour mask and apply multiplicative darkening along
        that mask to simulate Japanese-ink precision line drawing in oil;
        weyden_angular_shadow_pass (s246) uses directional lighting to build
        edge shadows; no prior pass uses a normalised Sobel edge map as an
        explicit contour-line darkening mask emulating Japanese ink-brush lines.

        Stage 3 DIRECTIONAL MICRO-TEXTURE HATCHING: Foujita built fine
        directional marks across pale zones -- fur, skin, and fabric surfaces
        show individual hairline marks aligned to the local surface normal and
        direction of hair/fibre growth.  Model this by computing local gradient
        orientation from the luminance image, then generating a sinusoidal
        hatching pattern oriented perpendicular to the local gradient (i.e.,
        along contours, not across them) and modulated by a pale-zone mask:
          pale_mask = clip(1 - 4*(lum - 0.75)^2, 0, 1)  (bell centred on lum=0.75)
          angle = atan2(gy, gx + 1e-6)   (local orientation angle)
          For each pixel (y, x):
            hatch_phase = x * cos(angle[y,x]) + y * sin(angle[y,x])
            hatch_val = sin(2*pi * hatch_phase / hatch_spacing)
            luminance_bump = hatch_amplitude * hatch_val * pale_mask[y,x]
          Apply luminance bump: R += bump, G += bump, B += bump (clipped)
        This creates fine parallel micro-texture lines across the bright pale zones
        while leaving shadows and contours unaffected -- exactly Foujita's surface.
        NOVEL: (c) ORIENTATION-ALIGNED SINUSOIDAL HATCHING IN PALE ZONES DERIVED
        FROM LOCAL SOBEL GRADIENT ANGLE -- first pass to use per-pixel atan2(gy, gx)
        as the hatch orientation and a bell-function pale-zone mask centred on a
        mid-high luminance value; paint_granulation_pass (s258) adds chromatic
        frequency-based texture; no prior pass computes per-pixel sine hatch phase
        from local gradient orientation to simulate directional brushmark micro-
        texture in the light zones only.
        \"\"\"
        print("    Foujita Milky Ground Contour pass (session 260, 171st mode)...")

        import math as _math
        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Milky Ivory Ground Lift ──────────────────────────────────
        ir = float(ivory_r)
        ig = float(ivory_g)
        ib = float(ivory_b)
        thr = float(ivory_threshold)
        iso = float(ivory_strength)

        above = _np.maximum(0.0, lum - thr).astype(_np.float32)
        denom = max(1.0 - thr, 1e-6)
        w_ivory = _np.clip(iso * above / denom, 0.0, 1.0).astype(_np.float32)

        r1 = (r0 * (1.0 - w_ivory) + ir * w_ivory).astype(_np.float32)
        g1 = (g0 * (1.0 - w_ivory) + ig * w_ivory).astype(_np.float32)
        b1 = (b0 * (1.0 - w_ivory) + ib * w_ivory).astype(_np.float32)

        # ── Stage 2: Japanese Ink Contour Tracing ─────────────────────────────
        from scipy.ndimage import sobel as _sobel, binary_dilation as _bdil

        gy_raw = _sobel(lum, axis=0).astype(_np.float32)
        gx_raw = _sobel(lum, axis=1).astype(_np.float32)
        grad = _np.sqrt(gx_raw ** 2 + gy_raw ** 2).astype(_np.float32)
        gmax = float(grad.max())
        grad_norm = (grad / (gmax + 1e-6)).astype(_np.float32)

        ct = float(contour_threshold)
        contour_mask = (grad_norm > ct).astype(_np.float32)

        cw = int(contour_width)
        if cw > 1:
            struct = _np.ones((cw, cw), dtype=bool)
            contour_mask = _bdil(contour_mask > 0, structure=struct).astype(_np.float32)

        cd = float(contour_darkness)
        dark_weight = cd * contour_mask
        r2 = _np.clip(r1 * (1.0 - dark_weight), 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 * (1.0 - dark_weight), 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 * (1.0 - dark_weight), 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Directional Micro-Texture Hatching ───────────────────────
        ha = float(hatch_amplitude)
        hs = int(max(hatch_spacing, 2))
        hsg = float(hatch_sigma)

        # pale_zone bell centred on lum=0.75
        pale_mask = _np.clip(1.0 - 4.0 * (lum - 0.75) ** 2, 0.0, 1.0).astype(_np.float32)
        if hsg > 0.0:
            pale_mask = _gf(pale_mask, sigma=hsg).astype(_np.float32)

        # local gradient orientation (angle of steepest ascent)
        angle = _np.arctan2(gy_raw, gx_raw + 1e-8).astype(_np.float32)

        ys = _np.arange(h, dtype=_np.float32)
        xs = _np.arange(w, dtype=_np.float32)
        xg, yg = _np.meshgrid(xs, ys)

        cos_a = _np.cos(angle).astype(_np.float32)
        sin_a = _np.sin(angle).astype(_np.float32)

        # hatch phase: project (x, y) onto direction perpendicular to gradient
        # (i.e., along iso-luminance contours): direction = (-sin, cos)
        hatch_phase = (-sin_a * xg + cos_a * yg).astype(_np.float32)
        hatch_val = _np.sin(2.0 * _np.float32(_math.pi) * hatch_phase / hs).astype(_np.float32)
        bump = (ha * hatch_val * pale_mask).astype(_np.float32)

        r3 = _np.clip(r2 + bump, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 + bump, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 + bump, 0.0, 1.0).astype(_np.float32)

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

        contour_px = int(contour_mask.sum())
        pale_px    = int((pale_mask > 0.1).sum())
        lifted_px  = int((w_ivory > 0.05).sum())
        print(f"    Foujita Milky Ground Contour complete "
              f"(lifted_px={lifted_px}, contour_px={contour_px}, pale_px={pale_px})")
"""

# ── Pass 2: paint_sfumato_contour_dissolution_pass ────────────────────────────

SFUMATO_PASS = """
    def paint_sfumato_contour_dissolution_pass(
        self,
        edge_sigma:        float = 1.2,
        edge_threshold:    float = 0.04,
        blur_sigma:        float = 2.5,
        dissolve_strength: float = 0.70,
        shadow_bias:       float = 0.25,
        noise_seed:        int   = 260,
        opacity:           float = 0.65,
    ) -> None:
        r\"\"\"Sfumato Contour Dissolution -- session 260 improvement.

        THREE-STAGE EDGE-TARGETED SFUMATO SOFTENING INSPIRED BY LEONARDO DA
        VINCI'S SMOKELESS BLENDING TECHNIQUE (c.1490-1517):

        Leonardo da Vinci described sfumato (Italian: smoke) as a technique in
        which contours are dissolved rather than drawn: colours blend at their
        edges without hard lines, transitions disappear gradually like smoke,
        and forms emerge from shadow rather than being bounded by outline.
        Technically, Leonardo achieved this by dozens of near-invisible thin
        glaze strokes at boundary zones, each fractionally shifting tone and
        hue without ever asserting a hard edge.  The result is that forms appear
        to emerge from or dissolve into their backgrounds -- edges are alive and
        ambiguous rather than fixed.  No prior pass specifically targets DETECTED
        EDGE ZONES for selective softening; broad blur passes affect the whole
        image uniformly.  This pass implements sfumato as an edge-aware,
        spatially-selective blur that dissolves ONLY the boundary zones while
        leaving interior textured areas and fully dark shadows intact.

        Stage 1 EDGE DETECTION AND ZONE MAP: Compute a Gaussian-smoothed
        luminance gradient using a fine-scale Sobel after Gaussian pre-smoothing:
          lum_smooth = gaussian_filter(lum, sigma=edge_sigma)
          gx = Sobel(lum_smooth, axis=1)
          gy = Sobel(lum_smooth, axis=0)
          edge_map = sqrt(gx^2 + gy^2)
          edge_map_norm = edge_map / (edge_map.max() + 1e-6)  (in [0,1])
          sfumato_zone = clip(edge_map_norm / (edge_threshold + 1e-6), 0, 1)
        This isolates the boundary-transition zone around every tonal edge.
        NOVEL: (a) GAUSSIAN-PRE-SMOOTHED SOBEL EDGE MAP AS A SPATIALLY-SELECTIVE
        BLUR MASK TARGETING SFUMATO DISSOLUTION ZONES -- first pass to combine
        a scale-controlled Gaussian pre-smooth with Sobel to produce a soft
        sfumato-zone mask; paint_granulation_pass (s258) uses frequency
        decomposition for texture; no prior pass uses a Gaussian-smoothed Sobel
        to define a per-pixel zone mask that drives a spatially-selective blur
        rather than a global one.

        Stage 2 EDGE-TARGETED GAUSSIAN BLUR: Apply a Gaussian blur to the full
        RGB image (sigma = blur_sigma) and blend it with the original using the
        sfumato_zone mask as the blend weight:
          blurred_R, G, B = gaussian_filter(R, G, B, sigma=blur_sigma)
          sfumato_blend = sfumato_zone * dissolve_strength
          R_soft = R * (1 - sfumato_blend) + blurred_R * sfumato_blend
          G_soft = G * (1 - sfumato_blend) + blurred_G * sfumato_blend
          B_soft = B * (1 - sfumato_blend) + blurred_B * sfumato_blend
        Interior zones (low edge response) receive no blur; boundary zones receive
        blur weighted by how strongly they read as transitions.  This produces
        locally soft edges while preserving interior textural clarity.
        NOVEL: (b) PER-PIXEL SPATIALLY-VARYING GAUSSIAN BLUR WEIGHTED BY EDGE-
        ZONE MAP FOR SFUMATO EDGE DISSOLUTION -- first pass to use a continuous
        edge-response field (rather than binary mask or global param) to
        interpolate between original and blurred versions at each pixel;
        wet_on_wet_bleeding_pass applies diffusion globally; no prior pass uses
        per-pixel edge-response magnitude as a continuous blend weight for a
        spatially-selective Gaussian softening operation at detected boundaries.

        Stage 3 SHADOW-BIAS TONAL DEEPENING: In Leonardo's sfumato the
        shadow sides of forms dissolve most strongly -- they go darker as well
        as softer, deepening the illusion of recession.  Model this by applying
        a luminance-dependent multiplicative darkening within the sfumato zone:
          shadow_weight = sfumato_zone * shadow_bias * (1 - lum)
          R_final = R_soft * (1 - shadow_weight)
          G_final = G_soft * (1 - shadow_weight)
          B_final = B_soft * (1 - shadow_weight)
        High sfumato_zone + low luminance (dark edge region) receives most
        darkening; bright edge zones (rim lights) receive much less.
        NOVEL: (c) SFUMATO-ZONE-GATED LUMINANCE-INVERSE SHADOW DEEPENING --
        first pass to multiply the sfumato_zone mask by (1 - lum) to produce a
        shadow-deepening weight that is strongest at dark sfumato boundary zones;
        warm_shadow_lift_pass lifts shadows globally; no prior pass uses the
        product of a per-pixel sfumato-zone weight and (1-luminance) as the
        driving input for a multiplicative darkening of shadow-edge boundary pixels.
        \"\"\"
        print("    Sfumato Contour Dissolution pass (session 260 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        from scipy.ndimage import sobel as _sobel

        # ── Stage 1: Edge Detection and Zone Map ──────────────────────────────
        es = max(float(edge_sigma), 0.3)
        lum_smooth = _gf(lum, sigma=es).astype(_np.float32)

        gy_raw = _sobel(lum_smooth, axis=0).astype(_np.float32)
        gx_raw = _sobel(lum_smooth, axis=1).astype(_np.float32)
        edge_map = _np.sqrt(gx_raw ** 2 + gy_raw ** 2).astype(_np.float32)
        emax = float(edge_map.max())
        edge_norm = (edge_map / (emax + 1e-6)).astype(_np.float32)

        et = max(float(edge_threshold), 1e-6)
        sfumato_zone = _np.clip(edge_norm / et, 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Edge-Targeted Gaussian Blur ──────────────────────────────
        bs = max(float(blur_sigma), 0.5)
        r_blur = _gf(r0, sigma=bs).astype(_np.float32)
        g_blur = _gf(g0, sigma=bs).astype(_np.float32)
        b_blur = _gf(b0, sigma=bs).astype(_np.float32)

        ds = float(dissolve_strength)
        sfumato_blend = (sfumato_zone * ds).astype(_np.float32)

        r1 = _np.clip(r0 * (1.0 - sfumato_blend) + r_blur * sfumato_blend, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * (1.0 - sfumato_blend) + g_blur * sfumato_blend, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * (1.0 - sfumato_blend) + b_blur * sfumato_blend, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Shadow-Bias Tonal Deepening ──────────────────────────────
        sb = float(shadow_bias)
        shadow_weight = _np.clip(sfumato_zone * sb * (1.0 - lum), 0.0, 1.0).astype(_np.float32)

        r2 = _np.clip(r1 * (1.0 - shadow_weight), 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 * (1.0 - shadow_weight), 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 * (1.0 - shadow_weight), 0.0, 1.0).astype(_np.float32)

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

        edge_px = int((sfumato_zone > 0.5).sum())
        deep_px = int((shadow_weight > 0.1).sum())
        print(f"    Sfumato Contour Dissolution complete "
              f"(edge_zone_px={edge_px}, deepened_px={deep_px}, "
              f"blur_sigma={blur_sigma:.1f}, dissolve={dissolve_strength:.2f})")
"""

# ── Inject into stroke_engine.py ──────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

already_foujita  = "foujita_milky_ground_contour_pass" in src
already_sfumato  = "paint_sfumato_contour_dissolution_pass" in src

if already_foujita and already_sfumato:
    print("Both passes already present in stroke_engine.py -- nothing to do.")
    sys.exit(0)

# Append new passes at the end of the file (after last content)
additions = ""
if not already_foujita:
    additions += FOUJITA_PASS
if not already_sfumato:
    additions += "\n" + SFUMATO_PASS

src = src.rstrip("\n") + "\n" + additions + "\n"

with open(ENGINE_PATH, "w", encoding="utf-8") as f:
    f.write(src)

if not already_foujita:
    print("Inserted foujita_milky_ground_contour_pass into stroke_engine.py.")
if not already_sfumato:
    print("Inserted paint_sfumato_contour_dissolution_pass into stroke_engine.py.")
