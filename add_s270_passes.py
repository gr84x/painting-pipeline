"""Insert paint_translucency_bloom_pass (s270 improvement) and
okeeffe_organic_form_pass (181st mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_translucency_bloom_pass (s270 improvement) ─────────────────

TRANSLUCENCY_BLOOM_PASS = '''
    def paint_translucency_bloom_pass(
        self,
        lum_low:          float = 0.52,
        lum_high:         float = 0.88,
        sat_threshold:    float = 0.08,
        bloom_sigma:      float = 12.0,
        bloom_warmth:     float = 0.14,
        bloom_strength:   float = 0.22,
        halo_sigma:       float = 3.5,
        halo_opacity:     float = 0.18,
        noise_seed:       int   = 270,
        opacity:          float = 0.72,
    ) -> None:
        r"""Translucency Bloom (Transmitted Light Glow) -- session 270 improvement.

        SIMULATION OF TRANSMITTED-LIGHT TRANSLUCENCY IN THIN ORGANIC MATERIAL,
        INSPIRED BY THE OPTICAL QUALITY OF ILLUMINATED FLOWER PETALS, LEAF TISSUE,
        AND OTHER ORGANIC MEMBRANES AS STUDIED BY GEORGIA O\'KEEFFE, JAN VAN HUYSUM,
        AND ODILON REDON, AND BY THE PHYSICS OF SUB-SURFACE LIGHT SCATTERING:

        When light strikes a thin organic membrane such as a flower petal, it does
        not simply reflect from the surface: part of it passes INTO the material,
        scatters through the internal tissue structure, and exits at a slightly
        different position and angle -- the phenomenon known as sub-surface
        scattering. The result is a characteristic soft, warm glow visible in the
        interior of translucent forms when backlighted or strongly sidelighted.
        The material appears to be lit FROM WITHIN -- its interior is warmer and
        lighter than the surface would predict from reflectance alone. This quality
        is the single most recognisable characteristic of a sunlit petal: the crisp
        edge of the form contrasts with the almost luminous warmth of the interior.

        Georgia O\'Keeffe studied this quality intensively in her close-up flower
        paintings of the 1920s-30s (Jimson Weed, Poppies, Canna Lily). She rendered
        it through smooth gradients that become warmer as they move toward the
        petal interior, and through a luminous, low-texture surface that captures
        the sense of internal light without depicting any individual scatter event.
        Jan van Huysum\'s extraordinary 18th-century flower paintings achieve a
        similar effect through thin glazes of warm lead white over cooler
        underpainting in petal passages: the cool underpaint "glows" through the
        warm surface glaze, creating the impression of interior illumination. Odilon
        Redon exploited the same principle in his pastel and oil flower works,
        where he described the light of flowers as "a light that comes from within."

        In oil painting, the effect is approximated by: (1) identifying zones that
        are both sufficiently luminous (light is reaching through the material)
        and low in local colour saturation deviation (the interior of a smooth,
        thin zone, not a texture-rich surface zone); (2) computing a warm bloom --
        a large-scale soft glow that warms and lightens these zones from the inside
        out; and (3) adding a narrow luminous halo at the detected zone boundaries,
        simulating the intense brightness at the petal edge where the scattering
        path is shortest and the transmitted-plus-reflected light adds.

        Stage 1 TRANSLUCENT ZONE DETECTION: Build a luminance image L from the
        canvas. Compute local luminance mean L_mean via Gaussian blur at
        sigma=bloom_sigma. A pixel is in a TRANSLUCENT ZONE if:
          (a) L[y,x] is in the mid-to-high range [lum_low, lum_high] -- bright
              enough for light to have penetrated, not so bright it is a
              highlight reflection;
          (b) the local saturation (max-min / max) is below sat_threshold -- the
              pixel is in a smooth, low-chroma zone characteristic of a thin
              unpigmented or lightly-pigmented membrane region.
        NOVEL: (a) JOINT LUMINANCE-SATURATION TRANSLUCENCY DETECTOR -- no prior
        pass uses the combination of mid-to-high luminance AND low saturation
        as a physical proxy for thin-material translucency; all prior passes that
        use luminance thresholds do so for tonal-range segmentation (tonal_key_pass,
        triple_zone_glaze_pass) without coupling to a saturation condition;
        the physical motivation is that truly translucent thin material zones are
        simultaneously bright (light passes through) and low-chroma (the internal
        pigmentation is sparse, so the material colour is pale or nearly neutral).

        Stage 2 WARM INNER BLOOM: For each detected translucent zone pixel, apply
        a warm luminous lift:
          new_R = R + bloom_warmth * (1 - R) * zone_mask       -- adds warmth
          new_G = G + bloom_warmth * 0.55 * (1 - G) * zone_mask
          new_B = B - bloom_warmth * 0.30 * B * zone_mask       -- reduces cool
        Then apply a large Gaussian blur to the accumulated glow field at
        sigma=bloom_sigma and blend it back into the canvas at bloom_strength.
        This creates the characteristic INTERIOR WARM GLOW of backlighted
        thin material, smoothly distributed across the detected zone, not
        centred on any individual pixel.
        NOVEL: (b) BLURRED WARM GLOW FIELD ACCUMULATED FROM TRANSLUCENT ZONE
        PIXELS -- prior glow/bloom passes (paint_halation_pass, paint_color_bloom_pass)
        build bloom fields from high-luminance or high-saturation pixels; this
        pass accumulates glow only from the joint lum-and-low-sat zone, making
        the bloom specifically interior to thin material forms rather than
        attached to bright highlights or saturated colour peaks; the physics-
        motivated target zone makes this a translucency simulation, not a
        lens-flare or light-leak effect.

        Stage 3 EDGE LUMINOUS HALO: Detect the BOUNDARY of the translucent zone
        using a dilated-minus-original morphological edge operation: dilate
        zone_mask at radius ~ halo_sigma pixels, subtract original zone_mask,
        yielding a thin boundary ring. Blend a luminous warm-white halo at
        halo_opacity over the canvas in this boundary ring, slightly blurred
        (sigma = halo_sigma * 0.5) to soften it.
        NOVEL: (c) TRANSLUCENT ZONE BOUNDARY HALO VIA MORPHOLOGICAL EDGE --
        no prior pass computes a morphological boundary ring from a content-
        derived zone mask and applies a localised luminous halo at that boundary;
        paint_halation_pass applies a global diffuse glow from a luminance mask
        without a boundary ring; this pass specifically targets the boundary of
        the detected translucent zone, simulating the characteristic brightness
        at the very edge of a petal where the two light paths (reflected AND
        transmitted) add together, producing a thin bright outline on the
        illuminated edge of the form.
        """
        print("    Translucency Bloom (Transmitted Light Glow) pass (session 270 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, binary_dilation as _bd

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Translucent Zone Detection ───────────────────────────────
        r_max = _np.maximum(_np.maximum(r0, g0), b0)
        r_min = _np.minimum(_np.minimum(r0, g0), b0)
        sat   = _np.where(r_max > 1e-6,
                          (r_max - r_min) / (r_max + 1e-6),
                          _np.zeros_like(r_max)).astype(_np.float32)

        ll = float(lum_low)
        lh = float(lum_high)
        st = float(sat_threshold)
        zone_mask = (
            (lum >= ll) & (lum <= lh) & (sat < st)
        ).astype(_np.float32)

        # ── Stage 2: Warm Inner Bloom ─────────────────────────────────────────
        bw  = float(bloom_warmth)
        bs  = float(bloom_strength)
        sig = max(float(bloom_sigma), 1.0)

        # Per-pixel warm lift gated to zone
        glow_r = (r0 + bw * (1.0 - r0) * zone_mask).astype(_np.float32)
        glow_g = (g0 + bw * 0.55 * (1.0 - g0) * zone_mask).astype(_np.float32)
        glow_b = (b0 - bw * 0.30 * b0 * zone_mask).astype(_np.float32)

        # Diffuse the glow field across the zone
        glow_r_blur = _gf(glow_r * zone_mask, sigma=sig).astype(_np.float32)
        glow_g_blur = _gf(glow_g * zone_mask, sigma=sig).astype(_np.float32)
        glow_b_blur = _gf(glow_b * zone_mask, sigma=sig).astype(_np.float32)

        # Normalise blur to avoid darkening away from zone
        zone_blur = _gf(zone_mask, sigma=sig).astype(_np.float32)
        safe_zone = _np.where(zone_blur > 1e-4, zone_blur, _np.ones_like(zone_blur))
        glow_r_n = (glow_r_blur / safe_zone).astype(_np.float32)
        glow_g_n = (glow_g_blur / safe_zone).astype(_np.float32)
        glow_b_n = (glow_b_blur / safe_zone).astype(_np.float32)

        # Blend only over zone pixels
        blend_r = _np.where(zone_mask > 0.5,
                            r0 + (glow_r_n - r0) * bs,
                            r0).astype(_np.float32)
        blend_g = _np.where(zone_mask > 0.5,
                            g0 + (glow_g_n - g0) * bs,
                            g0).astype(_np.float32)
        blend_b = _np.where(zone_mask > 0.5,
                            b0 + (glow_b_n - b0) * bs,
                            b0).astype(_np.float32)

        blend_r = _np.clip(blend_r, 0.0, 1.0).astype(_np.float32)
        blend_g = _np.clip(blend_g, 0.0, 1.0).astype(_np.float32)
        blend_b = _np.clip(blend_b, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Edge Luminous Halo ───────────────────────────────────────
        hs  = max(float(halo_sigma), 1.0)
        ho  = float(halo_opacity)
        rad = max(int(round(hs)), 1)
        struct = _np.ones((2 * rad + 1, 2 * rad + 1), dtype=bool)
        zone_bool = zone_mask > 0.5
        dilated   = _bd(zone_bool, structure=struct)
        boundary  = (dilated & ~zone_bool).astype(_np.float32)
        boundary_soft = _gf(boundary, sigma=hs * 0.5).astype(_np.float32)
        bmax = float(boundary_soft.max())
        if bmax > 1e-6:
            boundary_soft = (boundary_soft / bmax).astype(_np.float32)

        # Warm-white halo
        halo_r = _np.clip(blend_r + boundary_soft * ho * 1.00, 0.0, 1.0).astype(_np.float32)
        halo_g = _np.clip(blend_g + boundary_soft * ho * 0.92, 0.0, 1.0).astype(_np.float32)
        halo_b = _np.clip(blend_b + boundary_soft * ho * 0.80, 0.0, 1.0).astype(_np.float32)

        # ── Composite with master opacity ─────────────────────────────────────
        op = float(opacity)
        out_r = _np.clip(r0 + (halo_r - r0) * op, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 + (halo_g - g0) * op, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 + (halo_b - b0) * op, 0.0, 1.0).astype(_np.float32)

        out_arr = _np.zeros((h, w, 4), dtype=_np.uint8)
        out_arr[:, :, 0] = (out_b * 255).astype(_np.uint8)
        out_arr[:, :, 1] = (out_g * 255).astype(_np.uint8)
        out_arr[:, :, 2] = (out_r * 255).astype(_np.uint8)
        out_arr[:, :, 3] = orig[:, :, 3]

        surface.get_data()[:] = out_arr.tobytes()

'''

# ── Pass 2: okeeffe_organic_form_pass (181st mode) ───────────────────────────

OKEEFFE_ORGANIC_FORM_PASS = '''
    def okeeffe_organic_form_pass(
        self,
        variance_sigma:       float = 6.0,
        smooth_sigma:         float = 2.5,
        smooth_strength:      float = 0.30,
        mid_lum_low:          float = 0.28,
        mid_lum_high:         float = 0.68,
        mid_variance_cap:     float = 0.025,
        sat_lift:             float = 0.14,
        edge_threshold:       float = 0.018,
        edge_sharpen_amount:  float = 0.45,
        edge_sharpen_sigma:   float = 1.8,
        noise_seed:           int   = 270,
        opacity:              float = 0.78,
    ) -> None:
        r"""O\'Keeffe Organic Form (Smooth Gradient Modeling) -- session 270, 181st mode.

        FOUR-STAGE ORGANIC FORM REFINEMENT TECHNIQUE INSPIRED BY GEORGIA O\'KEEFFE
        (1887-1986) -- AMERICAN MODERNIST, FOUNDING FIGURE OF AMERICAN ABSTRACTION:

        Georgia O\'Keeffe developed one of the most distinctive painting surfaces in
        20th-century art: a silky, almost frictionless finish within each form --
        no visible brushwork, no texture, no impasto in the interior of forms --
        combined with hard, precise edges where one colour mass meets another.
        Within a single petal or hill or bone, the paint moves from light to shadow
        through a smooth, continuous gradient. At the boundary between two masses,
        the edge is clean and crisp, like a passage from one note to another in
        music rather than a gradual transition. This was not a limitation of her
        technique but a deliberate optical strategy: the smoothness of interior
        modeling focuses attention on FORM rather than SURFACE, while the crisp
        edges emphasise the RELATIONSHIP between adjacent forms rather than the
        material of the paint film.

        The third characteristic of her surfaces is the saturation intensification
        at the FORM-TURNING ZONE -- the area where the surface curves away from
        the light, passing through the mid-tonal range. In this zone, the colour
        becomes its most intense: a red petal is reddest where it begins to turn
        into shadow; a white flower is most luminously warm in the light-to-shadow
        transition. This is related to the principle of FORM MODELLING in classical
        oil painting, where the richest colour is placed in the transition zone
        rather than the deepest shadow or highest light. O\'Keeffe extended this
        to her abstracted organic forms, making the form-turning zone a zone of
        maximum colour presence.

        Stage 1 SMOOTH INTERIOR ZONE DETECTION: Compute the local luminance
        variance over a neighbourhood of sigma=variance_sigma using the formula:
          var[y,x] = gaussian(L^2, sigma) - gaussian(L, sigma)^2
        Low-variance zones (smooth interior of a form, where the tonal gradient
        is gentle and monotonic) are identified as smooth_mask = var < var_threshold.
        NOVEL: (a) LOCAL LUMINANCE VARIANCE AS A FORM INTERIOR DETECTOR --
        flat_zone_pass (s250) uses luminance standard deviation to identify
        flat zones for stylised treatment; this pass uses variance specifically
        to separate smooth, continuously-modelled form INTERIORS from edgy
        BOUNDARY ZONES, and then applies the smoothing and sharpening in the
        OPPOSITE zones -- smoothing the smooth interiors further, sharpening only
        the genuine edges. Prior passes do not use variance to gate opposing
        operations on complementary zone types.

        Stage 2 INTERIOR SURFACE SMOOTHING: Apply a Gaussian blur at
        sigma=smooth_sigma to the canvas, then blend the blurred version toward
        the current canvas AT smooth_strength, but ONLY in the smooth_mask zone.
        In high-variance edge zones, no smoothing is applied. The result refines
        the already-smooth interior modeling of each form, reducing micro-texture
        and surface grain within the form body while leaving all edges untouched.
        NOVEL: (b) VARIANCE-GATED GAUSSIAN SMOOTHING APPLIED ONLY TO LOW-VARIANCE
        ZONES -- all prior smoothing operations (sfumato_focus_pass: global Gaussian
        falloff from center; wet_on_wet_bleeding_pass: blend based on proximity
        to base colour; depth_atmosphere_pass: blend toward haze colour at
        depth-estimated zones) are not gated to detected variance structure of
        the image; this pass applies the smoothing ONLY where the surface is
        already smooth, concentrating the O\'Keeffe silkiness exactly in the zone
        where it exists in her painting -- the form interior -- and not at the
        edges, where it would destroy the clean boundary definition.

        Stage 3 TONAL TRANSITION SATURATION LIFT: Detect the FORM-TURNING ZONE
        as pixels satisfying: lum in [mid_lum_low, mid_lum_high] AND local
        variance in (0, mid_variance_cap] -- i.e., the pixel is in the
        mid-tonal range (not a highlight, not a deep shadow) AND the local surface
        is smooth (a continuous tonal gradient rather than a texture zone).
        In this detected form-turning zone, apply a saturation lift:
          sat_new = sat + sat_lift * form_turning_mask
        by pulling each channel away from luminance proportionally.
        NOVEL: (c) JOINT LUMINANCE + VARIANCE FORM-TURNING ZONE DETECTION --
        no prior pass identifies the form-turning zone using a two-condition gate
        of (a) mid-luminance range AND (b) low local variance; chromatic_zoning_pass
        divides the canvas into spatial sectors; tonal_key_pass adjusts the global
        tonal range; gorky_biomorphic_fluid_pass uses saturation deviation (not
        luminance) to find form zones; this pass detects the specific mid-tonal
        smooth zone that corresponds to the form-turning region in a classically-
        modelled rounded form, and applies the saturation intensification that
        O\'Keeffe places at this zone.

        Stage 4 EDGE ZONE CRISP CONTRAST ENHANCEMENT: Detect the edge zone as
        pixels where local variance > edge_threshold AND (the pixel is NOT in the
        smooth interior). Apply unsharp masking to the canvas in this zone only:
          usm_canvas = canvas - alpha * gaussian(canvas, sigma_sharp)
          edge_enhanced = canvas + edge_sharpen_amount * (canvas - usm_canvas)
        where the enhancement is blended AT the detected edge mask. This sharpens
        the boundaries between adjacent colour masses without touching the smooth
        interior of any form.
        NOVEL: (d) EDGE-ZONE-GATED UNSHARP MASKING -- unsharp masking (USM) is
        a standard sharpening technique; the novel element is gating it strictly
        to high-variance edge zones detected from the content, leaving all smooth
        interior zones completely unaffected; paint_sfumato_contour_dissolution_pass
        and paint_lost_found_edges_pass apply LOCAL BLUR at edges (soft edges);
        no prior pass applies LOCAL SHARPENING (USM) gated to detected high-
        variance edge zones while leaving low-variance smooth zones untouched.
        """
        print("    O\'Keeffe Organic Form (Smooth Gradient Modeling) pass (session 270, 181st mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Smooth Interior Zone Detection ───────────────────────────
        vs = max(float(variance_sigma), 0.5)
        lum2 = (lum ** 2).astype(_np.float32)
        lum_mean  = _gf(lum,  sigma=vs).astype(_np.float32)
        lum2_mean = _gf(lum2, sigma=vs).astype(_np.float32)
        local_var = _np.clip(lum2_mean - lum_mean ** 2, 0.0, None).astype(_np.float32)

        # Adaptive variance threshold: 10th percentile of nonzero variance
        nonzero_var = local_var[local_var > 1e-6]
        if len(nonzero_var) > 0:
            var_thr = float(_np.percentile(nonzero_var, 25))
        else:
            var_thr = 0.005
        smooth_mask = (local_var <= var_thr).astype(_np.float32)

        # ── Stage 2: Interior Surface Smoothing ───────────────────────────────
        ss = max(float(smooth_sigma), 0.5)
        st = float(smooth_strength)
        blurred_r = _gf(r0, sigma=ss).astype(_np.float32)
        blurred_g = _gf(g0, sigma=ss).astype(_np.float32)
        blurred_b = _gf(b0, sigma=ss).astype(_np.float32)

        sm_r = _np.where(smooth_mask > 0.5,
                         r0 + (blurred_r - r0) * st,
                         r0).astype(_np.float32)
        sm_g = _np.where(smooth_mask > 0.5,
                         g0 + (blurred_g - g0) * st,
                         g0).astype(_np.float32)
        sm_b = _np.where(smooth_mask > 0.5,
                         b0 + (blurred_b - b0) * st,
                         b0).astype(_np.float32)

        sm_r = _np.clip(sm_r, 0.0, 1.0).astype(_np.float32)
        sm_g = _np.clip(sm_g, 0.0, 1.0).astype(_np.float32)
        sm_b = _np.clip(sm_b, 0.0, 1.0).astype(_np.float32)

        # Recompute luminance after smoothing
        lum2_post = (0.299 * sm_r + 0.587 * sm_g + 0.114 * sm_b).astype(_np.float32)

        # ── Stage 3: Tonal Transition Saturation Lift ─────────────────────────
        mid_ll = float(mid_lum_low)
        mid_lh = float(mid_lum_high)
        mvc    = float(mid_variance_cap)
        sl     = float(sat_lift)

        form_turn = (
            (lum2_post >= mid_ll) &
            (lum2_post <= mid_lh) &
            (local_var <= mvc)
        ).astype(_np.float32)

        # Pull channels away from luminance to boost saturation
        sat_r = _np.clip(sm_r + (sm_r - lum2_post) * sl * form_turn, 0.0, 1.0).astype(_np.float32)
        sat_g = _np.clip(sm_g + (sm_g - lum2_post) * sl * form_turn, 0.0, 1.0).astype(_np.float32)
        sat_b = _np.clip(sm_b + (sm_b - lum2_post) * sl * form_turn, 0.0, 1.0).astype(_np.float32)

        # ── Stage 4: Edge Zone Crisp Contrast Enhancement ─────────────────────
        et  = float(edge_threshold)
        ea  = float(edge_sharpen_amount)
        ess = max(float(edge_sharpen_sigma), 0.5)

        edge_mask = (local_var > et).astype(_np.float32)

        blur_r = _gf(sat_r, sigma=ess).astype(_np.float32)
        blur_g = _gf(sat_g, sigma=ess).astype(_np.float32)
        blur_b = _gf(sat_b, sigma=ess).astype(_np.float32)

        usm_r = _np.clip(sat_r + (sat_r - blur_r) * ea * edge_mask, 0.0, 1.0).astype(_np.float32)
        usm_g = _np.clip(sat_g + (sat_g - blur_g) * ea * edge_mask, 0.0, 1.0).astype(_np.float32)
        usm_b = _np.clip(sat_b + (sat_b - blur_b) * ea * edge_mask, 0.0, 1.0).astype(_np.float32)

        # ── Composite with master opacity ─────────────────────────────────────
        op = float(opacity)
        out_r = _np.clip(r0 + (usm_r - r0) * op, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 + (usm_g - g0) * op, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 + (usm_b - b0) * op, 0.0, 1.0).astype(_np.float32)

        out_arr = _np.zeros((h, w, 4), dtype=_np.uint8)
        out_arr[:, :, 0] = (out_b * 255).astype(_np.uint8)
        out_arr[:, :, 1] = (out_g * 255).astype(_np.uint8)
        out_arr[:, :, 2] = (out_r * 255).astype(_np.uint8)
        out_arr[:, :, 3] = orig[:, :, 3]

        surface.get_data()[:] = out_arr.tobytes()

'''

# ── Insertion logic ──────────────────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if "paint_translucency_bloom_pass" in src:
    print("paint_translucency_bloom_pass already in stroke_engine.py -- skipping.")
else:
    INSERT_BEFORE = "    def gorky_biomorphic_fluid_pass("
    idx = src.find(INSERT_BEFORE)
    if idx == -1:
        print("ERROR: could not find gorky_biomorphic_fluid_pass insertion point.")
        import sys; sys.exit(1)
    new_src = src[:idx] + TRANSLUCENCY_BLOOM_PASS + src[idx:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src)
    print("Inserted paint_translucency_bloom_pass into stroke_engine.py.")
    src = new_src

if "okeeffe_organic_form_pass" in src:
    print("okeeffe_organic_form_pass already in stroke_engine.py -- skipping.")
else:
    # Insert after paint_translucency_bloom_pass (before gorky)
    INSERT_BEFORE2 = "    def gorky_biomorphic_fluid_pass("
    idx2 = src.find(INSERT_BEFORE2)
    if idx2 == -1:
        print("ERROR: could not find second insertion point.")
        import sys; sys.exit(1)
    new_src2 = src[:idx2] + OKEEFFE_ORGANIC_FORM_PASS + src[idx2:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src2)
    print("Inserted okeeffe_organic_form_pass into stroke_engine.py.")
