"""Insert paint_chromatic_vibration_pass (s269 improvement) and
gorky_biomorphic_fluid_pass (180th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_chromatic_vibration_pass (s269 improvement) ────────────────

CHROMATIC_VIBRATION_PASS = '''
    def paint_chromatic_vibration_pass(
        self,
        vibration_sigma:     float = 8.0,
        vibration_strength:  float = 0.18,
        boundary_threshold:  float = 0.04,
        saturation_boost:    float = 0.12,
        noise_seed:          int   = 269,
        opacity:             float = 0.70,
    ) -> None:
        r"""Chromatic Vibration (Simultaneous Contrast) -- session 269 improvement.

        OPTICAL COLOR VIBRATION TECHNIQUE INSPIRED BY THE LAWS OF SIMULTANEOUS
        CONTRAST FIRST CODIFIED BY MICHEL-EUGENE CHEVREUL (1839) AND EXPLOITED
        IN PAINTING FROM THE NEO-IMPRESSIONISTS TO THE FAUVISTS:

        Chevreul\'s law of simultaneous contrast states that two adjacent colours
        mutually enhance their apparent differences: a warm orange placed against
        a cool blue will appear more orange and the blue more blue than either
        would appear in isolation. The optical vibration that results at the
        boundary zone -- where warm and cool passages meet -- is a perceptual
        phenomenon produced by the contrast-amplifying response of the human
        visual system, not by any literal change in the pigments themselves. It
        was central to Seurat\'s Divisionism (where tiny dots of complementary
        colour create optical mixing and simultaneous contrast simultaneously),
        to Delacroix\'s advice to paint shadows cool when the light is warm (so
        that warm and cool are always in contact), to Matisse\'s Fauvist heightening
        of colour temperature contrasts beyond naturalistic limits, and to
        Albers\'s systematic exploration in Interaction of Color (1963).

        In oil painting, the effect is achieved by making warm zones slightly
        warmer and cool zones slightly cooler at their shared boundaries, and by
        lifting the saturation of both zones at the meeting edge. This is not
        a change to the overall colour temperature of the painting -- it is a
        LOCAL enhancement of the existing temperature relationship wherever
        warm and cool passages are in contact. Viewed from a distance, the eye
        senses a "shimmer" or "vibration" at colour boundaries that gives the
        painting a quality of living light.

        Stage 1 WARM-COOL TEMPERATURE SIGNAL: For each pixel, compute the colour
        temperature signal T = R - B (the red-minus-blue channel). Warm pixels
        (orange, ochre, gold, red) have T > 0; cool pixels (blue, violet, cerulean)
        have T < 0; neutral grey has T ≈ 0. This approximates the warm-cool axis
        of the Munsell colour space using only the RGB channels.
        NOVEL: (a) WARM-COOL TEMPERATURE FIELD FROM R-B CHANNEL -- no prior pass
        uses R-B as an explicit warm-cool temperature signal for boundary
        detection; paint_edge_temperature_pass applies a warm/cool split at
        LUMINANCE edges (not colour temperature edges) with a fixed warm/cool
        assignment based on the edge normal direction; paint_warm_cool_boundary_pass
        divides the canvas into spatial halves (not per-pixel temperature zones);
        this pass computes a continuous per-pixel temperature map from the RGB
        channels and uses it to detect warm/cool meeting zones.

        Stage 2 LOCAL MEAN TEMPERATURE: Smooth T with a Gaussian at
        sigma=vibration_sigma to compute the local neighbourhood mean temperature
        T_mean[y,x]. This represents the "background colour temperature" that a
        pixel is embedded in.

        Stage 3 TEMPERATURE DEVIATION: Compute T_dev = T - T_mean for each pixel.
        Positive T_dev means the pixel is warmer than its neighbourhood; negative
        T_dev means it is cooler. In a painting with smooth colour zones,
        |T_dev| is near zero everywhere; at warm-cool boundaries, |T_dev| is large.
        NOVEL: (b) LOCAL COLOUR TEMPERATURE DEVIATION AS A BOUNDARY SIGNAL --
        the local deviation of T from its smoothed mean identifies exactly the
        pixels that are anomalously warm or cool relative to their surroundings,
        which is precisely where simultaneous contrast effects are strongest; no
        prior pass computes this residual or uses it as a mask.

        Stage 4 BOUNDARY MASK: Build vib_mask = where |T_dev| > boundary_threshold.
        This isolates the pixels at warm-cool boundaries that will receive the
        vibration enhancement.

        Stage 5 TEMPERATURE AMPLIFICATION: In the masked boundary zone, push each
        pixel further in the direction of its existing temperature deviation:
          delta_R =  T_dev * vibration_strength  (warm pixels: R increases)
          delta_B = -T_dev * vibration_strength  (warm pixels: B decreases)
        This makes warm-adjacent pixels slightly warmer and cool-adjacent pixels
        slightly cooler, sharpening the contrast at the boundary.
        NOVEL: (c) CONTENT-ADAPTIVE LOCAL TEMPERATURE CONTRAST AMPLIFICATION --
        the shift magnitude and direction are computed individually per pixel from
        the local temperature deviation, not from a global warm/cool assignment;
        the amplification adapts to the existing colour relationships in the
        painting, reinforcing whatever contrasts are already present rather than
        imposing a fixed warm/cool structure.

        Stage 6 SATURATION BOOST IN VIBRATION ZONES: In the boundary mask, boost
        saturation by pulling each channel away from the local luminance:
          new_R = R + (R - L) * saturation_boost   (where L = 0.299R + 0.587G + 0.114B)
        This increases the colourfulness of both warm and cool passages at the
        boundary, which increases the perceptual contrast and the vibration effect.
        NOVEL: (d) LUMINANCE-RELATIVE SATURATION BOOST GATED TO TEMPERATURE
        BOUNDARY ZONES -- prior saturation-modifying passes either apply global
        saturation shifts (scumble_pass: desaturation globally) or apply in fixed
        spatial zones (atmospheric_recession_pass: desaturation in the top strip);
        this pass boosts saturation specifically and only where warm-cool boundaries
        have been detected, leaving the homogeneous interior of colour zones
        unaffected.
        """
        print("    Chromatic Vibration (Simultaneous Contrast) pass (session 269 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Warm-Cool Temperature Signal ─────────────────────────────
        temp = (r0 - b0).astype(_np.float32)

        # ── Stage 2: Local Mean Temperature ───────────────────────────────────
        sig = max(float(vibration_sigma), 0.5)
        temp_mean = _gf(temp, sigma=sig).astype(_np.float32)

        # ── Stage 3: Temperature Deviation ────────────────────────────────────
        temp_dev = (temp - temp_mean).astype(_np.float32)

        # ── Stage 4: Boundary Mask ────────────────────────────────────────────
        thr = max(float(boundary_threshold), 1e-4)
        vib_mask = (_np.abs(temp_dev) > thr).astype(_np.float32)

        # ── Stage 5: Temperature Amplification ────────────────────────────────
        vs = float(vibration_strength)
        delta_r = _np.clip(temp_dev * vs * vib_mask, -0.30, 0.30).astype(_np.float32)
        delta_b = _np.clip(-temp_dev * vs * vib_mask, -0.30, 0.30).astype(_np.float32)

        new_r = _np.clip(r0 + delta_r, 0.0, 1.0).astype(_np.float32)
        new_g = g0.copy()
        new_b = _np.clip(b0 + delta_b, 0.0, 1.0).astype(_np.float32)

        # ── Stage 6: Saturation Boost in Vibration Zones ──────────────────────
        lum_v = (0.299 * new_r + 0.587 * new_g + 0.114 * new_b).astype(_np.float32)
        sb = float(saturation_boost)
        new_r2 = _np.clip(new_r + (new_r - lum_v) * sb * vib_mask, 0.0, 1.0).astype(_np.float32)
        new_g2 = _np.clip(new_g + (new_g - lum_v) * sb * vib_mask, 0.0, 1.0).astype(_np.float32)
        new_b2 = _np.clip(new_b + (new_b - lum_v) * sb * vib_mask, 0.0, 1.0).astype(_np.float32)

        # ── Composite at opacity ───────────────────────────────────────────────
        op = float(opacity)
        final_r = _np.clip(r0 * (1.0 - op) + new_r2 * op, 0.0, 1.0).astype(_np.float32)
        final_g = _np.clip(g0 * (1.0 - op) + new_g2 * op, 0.0, 1.0).astype(_np.float32)
        final_b = _np.clip(b0 * (1.0 - op) + new_b2 * op, 0.0, 1.0).astype(_np.float32)

        vib_px = int((vib_mask > 0).sum())

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(final_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(final_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(final_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        print(f"    Chromatic Vibration complete (vib_px={vib_px})")
'''

# ── Pass 2: gorky_biomorphic_fluid_pass (180th mode) ─────────────────────────

GORKY_PASS = '''
    def gorky_biomorphic_fluid_pass(
        self,
        wash_sigma:          float = 7.0,
        wash_strength:       float = 0.20,
        contour_threshold:   float = 0.08,
        contour_opacity:     float = 0.30,
        contour_color:       tuple = (0.12, 0.08, 0.06),
        bleed_sigma:         float = 1.8,
        bleed_opacity:       float = 0.18,
        ground_warmth:       float = 0.10,
        ground_color:        tuple = (0.92, 0.82, 0.62),
        noise_seed:          int   = 269,
        opacity:             float = 0.80,
    ) -> None:
        r"""Gorky Biomorphic Fluid -- session 269, 180th distinct mode.

        FOUR-STAGE BIOMORPHIC OIL TECHNIQUE INSPIRED BY ARSHILE GORKY\'S
        MATURE PAINTING PRACTICE (c.1940-1948):

        Arshile Gorky (born Vosdanig Manoug Adoian, 1904-1948) was an Armenian-
        American painter who spent his career translating the organic richness of
        his Armenian childhood into a new abstract visual language that bridged
        European Surrealism and American Abstract Expressionism. Born in Khorkom
        village on the eastern shore of Lake Van, he survived the Armenian Genocide
        and arrived in the United States in 1920. His early work was rigorous
        self-education in the masters: he worked systematically through Cézanne,
        then Picasso, then Miró, then Kandinsky -- using each as a school before
        moving on. The mature Gorky of the early 1940s was completely himself.

        His Garden in Sochi series (c.1940-1941) -- a group of six paintings
        inspired by the garden of his father\'s house in Van province -- marks the
        first definitive arrival of his mature style. These paintings are built
        from biomorphic forms: rounded, irregular, organic shapes that suggest
        plant, body, and geological forms without depicting any of them. The forms
        are derived from memory and automatic drawing, not observation -- they have
        the quality of things half-remembered, the organic logic of living forms
        without the constraints of photographic representation. The technique is
        characterised by:

        (1) FLUID WASH CONSTRUCTION: Gorky thinned his oil paints heavily with
        turpentine, applying them in multiple transparent layers so that the warm
        cream or ochre ground shows through the forms. Each layer is a wash rather
        than an opaque stroke. The result is a painting that breathes -- the
        luminous ground is visible through the form, and each successive layer
        modifies the colour without obliterating what is underneath.

        (2) SATURATION-GUIDED FORM ENRICHMENT: The biomorphic "forms" in Gorky\'s
        work are zones of higher saturation set against a more neutral, luminous
        ground. The forms glow with concentrated colour (deep viridian, crimson,
        burnt sienna, ochre) while the ground breathes in pale cream and warm grey.
        The transition between form and ground is the most painted zone -- where
        saturation rises and falls, where colour temperature shifts, where contour
        lines appear and disappear.

        (3) ORGANIC CONTOUR DRAWING: Gorky draws his biomorphic contours with a
        fine brush in a dark colour (often dark umber or blue-black), tracing the
        edges of forms with a line that is simultaneously drawn and painted --
        neither a strict outline nor a tonal modelling stroke. The line appears
        and disappears, thickens and thins, responding to the form beneath it
        rather than imposing an external shape. This is the legacy of his
        systematic study of Ingres\'s contour drawing, transformed by his contact
        with Miró\'s biomorphic Surrealism.

        (4) TRANSLUCENT BLEED AT BOUNDARIES: Because Gorky\'s paints were heavily
        thinned, they tended to bleed slightly at the boundary between form and
        ground -- the paint wicked along the grain of the canvas, softening hard
        edges and creating the slightly diffuse, atmospheric edge quality that is
        characteristic of his surfaces. This bleed is not accidental -- Gorky
        exploited it as part of the form-building process, sometimes encouraging
        it, sometimes blotting it, to control the boundary between form and air.

        Stage 1 SATURATION MAP AND FORM ZONE DETECTION: Compute the per-pixel
        HSV saturation S = (max(R,G,B) - min(R,G,B)) / (max(R,G,B) + ε). Smooth
        S with a Gaussian at sigma=wash_sigma to get S_mean (local neighbourhood
        saturation). Identify HIGH SATURATION ZONES where S > S_mean * 1.1 -- these
        are the "biomorphic forms." Identify LOW SATURATION ZONES where
        S < S_mean * 0.7 -- these are the "air/ground" zones.
        NOVEL: (a) SATURATION-RELATIVE FORM DETECTION -- no prior pass uses per-
        pixel saturation deviation from the local neighbourhood mean as a form
        detection signal; underpainting/block_in/build_form all use luminance
        error; flat_zone_pass uses luminance standard deviation; this pass uses
        local saturation deviation, making it sensitive to colour richness
        independent of lightness -- detecting Gorky\'s characteristic richly-
        coloured forms against a pale, desaturated ground.

        Stage 2 FLUID WASH IN FORM ZONES: In high-saturation zones, apply a thin
        transparent wash that enriches the existing colour by pulling each channel
        away from local luminance:
          wash_R = R + (R - L) * wash_strength   (where L = luminance)
        This is analogous to a transparent glaze in oil painting: it deepens and
        enriches the hue without changing its character. The wash_strength
        (default 0.20) corresponds to approximately 20% enrichment -- a very thin,
        transparent layer.
        NOVEL: (b) LUMINANCE-RELATIVE COLOUR ENRICHMENT GATED TO SATURATION
        ZONES -- the saturation enrichment is applied only in zones identified by
        the saturation-relative form detector (Stage 1), not globally; prior glaze
        passes (venetian_glaze_pass, velatura_pass) apply glazes to the whole
        canvas or to fixed luminance zones; this pass confines the enrichment to
        the detected form zones, preserving the pale luminous quality of the ground
        zones.

        Stage 3 ORGANIC CONTOUR SYNTHESIS: Compute the spatial gradient magnitude
        of luminance using Sobel operators:
          grad_mag = sqrt(Sobel_x(L)^2 + Sobel_y(L)^2)
        Normalise to [0, 1]. Build a contour_mask = where normalised
        grad_mag > contour_threshold. Blend a dark contour color (deep umber
        0.12/0.08/0.06, approximating Gorky\'s dark contour medium) over the
        post-wash canvas at contour_opacity in the contour zone.
        NOVEL: (c) LUMINANCE-GRADIENT CONTOUR OVERLAY IN DARK UMBER -- prior
        edge passes (edge_lost_and_found_pass: selectively blurs/sharpens edges;
        paint_sfumato_contour_dissolution_pass: blurs at edges) modify edges by
        blurring or sharpening them; this pass OVERLAYS a drawn contour line in
        a specific dark-umber colour at detected edges, introducing a "drawn line"
        quality that is unique to Gorky\'s technique of combining oil paint and
        contour drawing in a single layer.

        Stage 4 WARM GROUND RE-EXPOSURE AND PAINT BLEED: In low-saturation
        "ground" zones, apply a small lift toward the warm cream ground color:
          new_R = R + ground_R * ground_warmth * (1 - R)   (lifts toward cream)
        This simulates the luminous ground showing through thin paint in ground
        zones -- the characteristic transparency of Gorky\'s surfaces.
        Then apply a bleed effect at contour boundaries: blur the post-wash
        canvas at sigma=bleed_sigma, and blend the blurred version toward the
        current canvas at bleed_opacity in the contour zone only. This simulates
        the slight thinning-medium bleed at the form/ground boundary.
        NOVEL: (d) DUAL GROUND RE-EXPOSURE + PAINT BLEED AT SATURATION BOUNDARY
        -- the combination of warm-ground re-exposure in ground zones (simulating
        canvas luminosity showing through thin paint) with directional bleed at
        detected form boundaries (simulating thinned-medium bleed along canvas
        grain) is unique to Gorky\'s oil technique and has no precedent in prior
        passes.
        """
        print("    Gorky Biomorphic Fluid pass (session 269, 180th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, sobel as _sobel

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Saturation Map and Form Zone Detection ───────────────────
        r_max = _np.maximum(_np.maximum(r0, g0), b0)
        r_min = _np.minimum(_np.minimum(r0, g0), b0)
        sat = _np.where(r_max > 1e-6,
                        (r_max - r_min) / (r_max + 1e-6),
                        _np.zeros_like(r_max)).astype(_np.float32)

        ws = max(float(wash_sigma), 0.5)
        sat_mean = _gf(sat, sigma=ws).astype(_np.float32)
        sat_mean_safe = _np.maximum(sat_mean, 1e-4)

        high_sat = (sat > sat_mean_safe * 1.10).astype(_np.float32)
        low_sat  = (sat < sat_mean_safe * 0.70).astype(_np.float32)

        # ── Stage 2: Fluid Wash in Form Zones ────────────────────────────────
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        wst = float(wash_strength)

        wash_r = _np.clip(r0 + (r0 - lum) * wst * high_sat, 0.0, 1.0).astype(_np.float32)
        wash_g = _np.clip(g0 + (g0 - lum) * wst * high_sat, 0.0, 1.0).astype(_np.float32)
        wash_b = _np.clip(b0 + (b0 - lum) * wst * high_sat, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Organic Contour Synthesis ────────────────────────────────
        lum_gy = _sobel(lum.astype(_np.float64), axis=0).astype(_np.float32)
        lum_gx = _sobel(lum.astype(_np.float64), axis=1).astype(_np.float32)
        grad_mag = _np.sqrt(lum_gy ** 2 + lum_gx ** 2).astype(_np.float32)
        gm_max = float(grad_mag.max()) + 1e-6
        grad_norm = (grad_mag / gm_max).astype(_np.float32)

        ct = max(float(contour_threshold), 0.01)
        contour_mask = (grad_norm > ct).astype(_np.float32)

        cr_c, cg_c, cb_c = (float(contour_color[0]),
                             float(contour_color[1]),
                             float(contour_color[2]))
        co = float(contour_opacity)
        wash_r = _np.clip(wash_r * (1.0 - co * contour_mask) + cr_c * co * contour_mask,
                          0.0, 1.0).astype(_np.float32)
        wash_g = _np.clip(wash_g * (1.0 - co * contour_mask) + cg_c * co * contour_mask,
                          0.0, 1.0).astype(_np.float32)
        wash_b = _np.clip(wash_b * (1.0 - co * contour_mask) + cb_c * co * contour_mask,
                          0.0, 1.0).astype(_np.float32)

        # ── Stage 4: Warm Ground Re-Exposure and Paint Bleed ──────────────────
        gr_r, gr_g, gr_b = (float(ground_color[0]),
                             float(ground_color[1]),
                             float(ground_color[2]))
        gw = float(ground_warmth)
        wash_r = _np.clip(wash_r + gr_r * gw * low_sat * (1.0 - wash_r), 0.0, 1.0).astype(_np.float32)
        wash_g = _np.clip(wash_g + gr_g * gw * low_sat * (1.0 - wash_g), 0.0, 1.0).astype(_np.float32)
        wash_b = _np.clip(wash_b + gr_b * gw * low_sat * (1.0 - wash_b), 0.0, 1.0).astype(_np.float32)

        bs = max(float(bleed_sigma), 0.3)
        bleed_r = _gf(wash_r, sigma=bs).astype(_np.float32)
        bleed_g = _gf(wash_g, sigma=bs).astype(_np.float32)
        bleed_b = _gf(wash_b, sigma=bs).astype(_np.float32)
        bo = float(bleed_opacity)
        wash_r = _np.clip(wash_r * (1.0 - bo * contour_mask) + bleed_r * bo * contour_mask,
                          0.0, 1.0).astype(_np.float32)
        wash_g = _np.clip(wash_g * (1.0 - bo * contour_mask) + bleed_g * bo * contour_mask,
                          0.0, 1.0).astype(_np.float32)
        wash_b = _np.clip(wash_b * (1.0 - bo * contour_mask) + bleed_b * bo * contour_mask,
                          0.0, 1.0).astype(_np.float32)

        # ── Composite at opacity ───────────────────────────────────────────────
        op = float(opacity)
        final_r = _np.clip(r0 * (1.0 - op) + wash_r * op, 0.0, 1.0).astype(_np.float32)
        final_g = _np.clip(g0 * (1.0 - op) + wash_g * op, 0.0, 1.0).astype(_np.float32)
        final_b = _np.clip(b0 * (1.0 - op) + wash_b * op, 0.0, 1.0).astype(_np.float32)

        high_sat_px = int(high_sat.sum())
        contour_px  = int(contour_mask.sum())

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(final_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(final_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(final_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        print(f"    Gorky Biomorphic Fluid complete "
              f"(high_sat_px={high_sat_px}, contour_px={contour_px})")
'''

# ── Inject into stroke_engine.py ──────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

already_vibration = "paint_chromatic_vibration_pass" in src
already_gorky     = "gorky_biomorphic_fluid_pass" in src

if already_vibration and already_gorky:
    print("Both passes already present in stroke_engine.py -- nothing to do.")
    sys.exit(0)

additions = ""
if not already_vibration:
    additions += CHROMATIC_VIBRATION_PASS
if not already_gorky:
    additions += "\n" + GORKY_PASS

src = src.rstrip("\n") + "\n" + additions + "\n"

with open(ENGINE_PATH, "w", encoding="utf-8") as f:
    f.write(src)

if not already_vibration:
    print("Inserted paint_chromatic_vibration_pass into stroke_engine.py.")
if not already_gorky:
    print("Inserted gorky_biomorphic_fluid_pass into stroke_engine.py.")
