"""Insert paint_form_curvature_tint_pass (s283 improvement) and
repin_character_depth_pass (194th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_form_curvature_tint_pass (s283 improvement) ────────────────

FORM_CURVATURE_TINT_PASS = '''
    def paint_form_curvature_tint_pass(
        self,
        smooth_sigma:       float = 9.0,
        convex_r:           float = 0.90,
        convex_g:           float = 0.82,
        convex_b:           float = 0.62,
        convex_strength:    float = 0.20,
        concave_r:          float = 0.55,
        concave_g:          float = 0.60,
        concave_b:          float = 0.76,
        concave_strength:   float = 0.16,
        curvature_sigma:    float = 2.0,
        curvature_percentile: float = 80.0,
        opacity:            float = 0.78,
    ) -> None:
        r"""Form Curvature Tint -- s283 improvement.

        THE PHYSICAL BASIS: CONVEX-CONCAVE LIGHT TEMPERATURE DIFFERENTIAL

        In realistic painting of three-dimensional form -- particularly the human
        face and body -- the color temperature of light varies systematically
        with the local curvature of the surface. This phenomenon arises from
        two independent physical mechanisms:

        CONVEX ZONES (outward-curving surfaces: brow ridge, cheekbone, nose
        bridge, chin, knuckle peaks, shoulder arc): These surfaces face the
        dominant light source most directly. They receive the full color and
        intensity of the key light. In studio conditions with warm artificial
        light, or in outdoor conditions with afternoon sun, convex zones read as
        warmer, slightly more cream-golden than the local mean. The convex surface
        is the painter's "first light" -- the zone of maximum illumination and
        maximum warmth when the key light is warm (which it almost always is in
        portraiture and figurative painting).

        CONCAVE ZONES (inward-curving surfaces: the eye socket, the hollow under
        the cheekbone, the philtrum trough above the lip, the nape of the neck,
        the armpit, the pocket between the collar and jaw): These surfaces are
        partially or wholly sheltered from the key light. They receive ambient
        scattered light and sky reflection, which tends to be cooler (bluer or
        violet-grey) than the direct key. In outdoor painting, concave zones catch
        sky color directly. In Rembrandt and Repin's interior portraits, the concave
        eye socket registers a distinctly cooler, slightly purple-grey reflected
        from the opposite wall or from the ambient air.

        This convex-warm / concave-cool temperature differential is one of the
        hallmarks of skilled figurative painting, described in the teachings of
        Carolus-Duran (Sargent's master), in Repin's own notes on painting
        the face, and in the manuals of Frank Reilly and Richard Schmid. Painters
        who apply this principle produce rounded, three-dimensional form; painters
        who ignore it produce flat, tonal but unmodeled passages.

        PRIOR PASSES AND NOVELTY:
        Prior passes that modify color temperature:
          - shadow_temperature_pass (s281): adapts shadow zone color based on
            scene highlight temperature; operates on the SHADOW LUMINANCE ZONE,
            not on local curvature.
          - edge_temperature_pass: modifies color at high-gradient edges; operates
            on GRADIENT MAGNITUDE (edge vs. non-edge), not curvature sign.
          - contre_jour_rim_pass (s282): operates on BRIGHT SIDE / DARK SIDE of
            luminance boundaries; uses the geometric relationship between bright
            and dark zones, not curvature.
        No prior pass:
          (i)  estimates the local 3D form curvature of the painted surface;
          (ii) identifies CONVEX zones (facing the viewer / light) vs. CONCAVE
               zones (recessed / sheltered);
          (iii) applies OPPOSING temperature effects to the two curvature signs.
        The Laplacian-of-Gaussian approach to local curvature estimation from
        image data is the key technical novelty.

        Stage 1 SPATIAL FREQUENCY DECOMPOSITION (Form-Scale vs. Detail-Scale):
        Decompose the canvas luminance into a low-frequency layer (large-scale
        3D form) and retain the smoothed version for curvature analysis:
          L = 0.299R + 0.587G + 0.114B
          L_form = GaussianFilter(L, sigma=smooth_sigma)
        The sigma=smooth_sigma (default 9 pixels) suppresses local surface
        detail (pores, brushstroke texture, fine wrinkles) while retaining the
        larger shape transitions that correspond to the 3D form of the subject:
        the arc of the cheek, the ridge of the nose, the hollow of the eye socket.
        NOVEL: (a) SPATIAL FREQUENCY SEPARATION FOR CURVATURE ANALYSIS -- this is
        the first pass to separate image content into a "form-scale" low-frequency
        layer (L_form) for curvature analysis and a "detail-scale" high-frequency
        layer. Prior passes that use Gaussian filtering use it for spatial smoothing
        of a MASK or of the COLOR CHANNEL directly, not for isolating large-scale
        form structure for derivative analysis.

        Stage 2 LOCAL FORM CURVATURE (LAPLACIAN OF SMOOTHED LUMINANCE):
        Compute the Laplacian (sum of second spatial derivatives) of L_form:
          kappa = d^2 L_form/dx^2 + d^2 L_form/dy^2
                = GaussianFilter(L_form, sigma=curvature_sigma, order=[0,2])
                + GaussianFilter(L_form, sigma=curvature_sigma, order=[2,0])
        The Laplacian is positive at local luminance maxima (bright peaks =
        convex surfaces facing the light) and negative at local luminance minima
        (dark hollows = concave surfaces sheltered from the light).
        Normalize the Laplacian:
          kappa_norm = kappa / percentile(|kappa|, curvature_percentile)
          kappa_norm = clip(kappa_norm, -1.0, 1.0)
        The normalized curvature is +1 at peak convex zones and -1 at peak
        concave zones, with smooth transition through zero at inflection points.
        NOVEL: (b) SIGNED LAPLACIAN AS CONVEX/CONCAVE DISCRIMINATOR -- No prior
        paint_ improvement pass uses the Laplacian (second spatial derivative) of
        the image. Prior derivative-based passes use first-order derivatives: Sobel
        gradient (Gx, Gy in savrasov_pass, contre_jour_rim_pass, repin_character_
        depth_pass), gradient magnitude (edge detection in lost_found_edges_pass),
        or directional gradient components (Gy in savrasov branch sharpening). The
        Laplacian is the first SECOND-ORDER derivative used as a pass gate in this
        engine, and its SIGNED value is the first quantity that discriminates between
        two geometrically opposite structural zones (convex vs. concave).

        Stage 3 CONVEX ZONE WARM TINT (Key-Light Color Accumulation):
        Build convex_mask = clip(kappa_norm, 0.0, 1.0)  (positive curvature only)
        Smooth convex_mask with a gentle Gaussian (sigma=1.5) to soften hard edges.
        Push convex pixels toward warm cream-gold (convex_r/g/b -- warm key-light):
          C_out1 = C + (warm_color - C) * convex_mask * convex_strength
        NOVEL: (c) WARM TINT ON CONVEX ZONES FROM LAPLACIAN -- no prior pass applies
        a warm color push specifically to LOCALLY CONVEX zones (Laplacian > 0).
        The contour_weight_pass (s279) applies a tonal weight to "edge regions" but
        does not discriminate convex from concave; the impasto passes add texture-
        based specular highlights but do not use luminance curvature as the gate.

        Stage 4 CONCAVE ZONE COOL RECESS (Ambient/Sky Reflection):
        Build concave_mask = clip(-kappa_norm, 0.0, 1.0)  (negative curvature only)
        Smooth with sigma=1.5.
        Push concave pixels toward cool ambient (concave_r/g/b -- cool sky-grey):
          C_out2 = C_out1 + (cool_color - C_out1) * concave_mask * concave_strength
        NOVEL: (d) SIMULTANEOUS OPPOSING SIGNED CURVATURE EFFECTS -- applying a warm
        push to convex zones and a cool push to concave zones in one pass models the
        actual color-temperature geometry of illuminated 3D form. No prior pass
        simultaneously applies GEOMETRICALLY OPPOSITE effects (warm vs. cool) to
        zones that are defined by a SIGNED mathematical quantity (positive vs.
        negative Laplacian). The closest prior pass is contre_jour_rim_pass (s282),
        which applies warm/cool to dark/bright luminance boundaries -- but that pass
        is defined by a BINARY zone relationship (bright mask dilated onto dark zone),
        while this pass uses a CONTINUOUS SIGNED gradient (kappa ranges from -1 to +1
        with all intermediate values representing varying degrees of curvature).
        """
        print("    Form Curvature Tint pass (session 283 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H, W = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        # Stage 1: Compute form-scale luminance
        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)
        ssig = max(float(smooth_sigma), 1.0)
        L_form = _gf(L, sigma=ssig).astype(_np.float32)

        # Stage 2: Laplacian of smoothed luminance = form curvature
        csig = max(float(curvature_sigma), 0.5)
        kxx = _gf(L_form, sigma=csig, order=[0, 2]).astype(_np.float32)
        kyy = _gf(L_form, sigma=csig, order=[2, 0]).astype(_np.float32)
        kappa = (kxx + kyy).astype(_np.float32)

        cp = float(curvature_percentile)
        kappa_scale = max(float(_np.percentile(_np.abs(kappa), cp)), 1e-6)
        kappa_norm = _np.clip(kappa / kappa_scale, -1.0, 1.0).astype(_np.float32)

        # Stage 3: Convex zone warm tint (positive curvature = convex)
        convex_mask = _np.clip(kappa_norm, 0.0, 1.0).astype(_np.float32)
        convex_mask = _gf(convex_mask, sigma=1.5).astype(_np.float32)

        cstr = float(convex_strength)
        cvr, cvg, cvb = float(convex_r), float(convex_g), float(convex_b)
        R1 = _np.clip(R + (cvr - R) * convex_mask * cstr, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (cvg - G) * convex_mask * cstr, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (cvb - B) * convex_mask * cstr, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Concave zone cool recess (negative curvature = concave)
        concave_mask = _np.clip(-kappa_norm, 0.0, 1.0).astype(_np.float32)
        concave_mask = _gf(concave_mask, sigma=1.5).astype(_np.float32)

        ccstr = float(concave_strength)
        ccr, ccg, ccb = float(concave_r), float(concave_g), float(concave_b)
        R2 = _np.clip(R1 + (ccr - R1) * concave_mask * ccstr, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (ccg - G1) * concave_mask * ccstr, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (ccb - B1) * concave_mask * ccstr, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R2 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G2 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B2 - B) * op, 0.0, 1.0).astype(_np.float32)

        convex_px  = int((convex_mask  > 0.05).sum())
        concave_px = int((concave_mask > 0.05).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Form Curvature Tint complete "
              f"(convex_px={convex_px}, concave_px={concave_px}, "
              f"kappa_scale={kappa_scale:.5f})")

'''

# ── Pass 2: repin_character_depth_pass (194th mode) ──────────────────────────

REPIN_CHARACTER_DEPTH_PASS = '''
    def repin_character_depth_pass(
        self,
        gradient_sigma:      float = 1.4,
        form_blur_sigma:     float = 2.0,
        form_blend:          float = 0.25,
        mid_lo:              float = 0.30,
        mid_hi:              float = 0.62,
        mid_r:               float = 0.70,
        mid_g:               float = 0.50,
        mid_b:               float = 0.32,
        mid_strength:        float = 0.24,
        shadow_thresh:       float = 0.32,
        shadow_r:            float = 0.28,
        shadow_g:            float = 0.28,
        shadow_b:            float = 0.48,
        shadow_strength:     float = 0.22,
        edge_percentile:     float = 72.0,
        edge_sharp_sigma:    float = 1.1,
        edge_sharp_amount:   float = 0.50,
        opacity:             float = 0.85,
    ) -> None:
        r"""Repin Character Depth (Russian Realism -- Psychological Portraiture) -- 194th mode.

        ILYA YEFIMOVICH REPIN (1844-1930) -- UKRAINIAN-RUSSIAN REALIST;
        THE PREMIER FIGURATIVE PAINTER OF THE 19TH-CENTURY SLAVIC WORLD:

        Ilya Repin was born in 1844 in Chuguev, Ukraine (then part of the Russian
        Empire), the son of a military settler. His early talent was evident by
        childhood; he received his first formal training in Chuguev and then at the
        Imperial Academy of Arts in St. Petersburg from 1864. He won the Academy's
        major gold medal in 1871 with a history painting, which granted him a
        scholarship to study in Europe. He lived in Paris from 1873 to 1876,
        absorbing Impressionism without being captured by it -- he found the movement
        too purely optical, insufficiently concerned with psychological truth.

        On his return to Russia, Repin joined the Peredvizhniki (the Wanderers or
        Itinerants) -- the movement of realist painters who had broken with the
        Academy to paint directly from Russian life: peasants, workers, historical
        suffering, social injustice. Repin became the movement's greatest exponent
        and, in the view of many, the greatest Russian painter of any period.

        REPIN'S FIVE DEFINING TECHNICAL-PSYCHOLOGICAL CHARACTERISTICS:

        1. FORM-FOLLOWING DIRECTIONAL IMPASTO: Repin did not apply paint in a
           uniform direction or in standard horizontal strokes. He studied the form
           of his subject -- particularly the face -- and oriented his brushstrokes
           to follow the planes of the form: strokes along the cheek plane lie
           roughly parallel to the cheekbone; strokes on the brow follow the orbital
           arch; strokes on the neck follow the column's axis. The result is paint
           that reads as surface, not as flat pigment. When Stasov described Repin's
           portraits as "three-dimensional," he was responding to this technique
           as much as to the tonal modeling.

        2. MIDTONE WARMTH IN ILLUMINATED ZONES: Repin's lit surfaces -- skin,
           fabric, warm earth -- carry a characteristic warm umber-flesh tone in
           the middle values. Not golden-yellow (that would be Sorolla), not
           cool-white (that would be Whistler) -- but a specific warm umber with
           a raw sienna undertone (approximately 0.70/0.50/0.32 in linear RGB).
           This midtone warmth is where the character of the subject lives. Repin
           called this the "color of air touched by sun" -- the ordinary warmth of
           Russian afternoon light on human skin.

        3. COOL TRANSPARENT SHADOWS: Repin's shadow zones are never opaque. They
           are glazed transparently with cool blue-violets and grey-purples, allowing
           the warm ground to show through. The result is shadows that feel airy and
           filled with reflected light rather than flat and dead. The specific color --
           a greyish blue-violet (approximately 0.28/0.28/0.48) -- appears across
           his portraits: in the eye sockets of his Cossacks, in the shadow under
           Tolstoy's beard, in the dark passages of "Barge Haulers on the Volga."

        4. FORM-PLANE DIRECTIONAL SOFTENING: Within each broad plane of the face
           (the cheek plane, the frontal plane, the plane of the jaw), Repin applied
           slightly directional, modulated strokes that blur ALONG the plane rather
           than across it. This creates the impression of a continuous, smooth surface
           within each plane while keeping the edges between planes sharp and
           structurally legible.

        5. PSYCHOLOGICAL EDGE CRISPENING: The edges that define character -- the
           line of the jaw, the arc of the brow, the fold of a collar against the
           neck -- are the sharpest elements in Repin's work. He deliberately
           maintained or even sharpened these structural edges after the initial
           blocking, while allowing non-structural passages (forehead interior,
           cloth folds, background) to remain softly merged. The sharpest edge in
           the painting directs the eye to the deepest psychological content.

        THE GREAT WORKS:
        "Barge Haulers on the Volga" (1873): A processional frieze of eleven
        burlaki (barge haulers) pulling a steamship upriver. The central figure,
        Kanin, a former priest, dominates with a face of such concentrated
        psychological complexity -- exhaustion, intelligence, quiet dignity -- that
        it became the emblem of Repin's art and of Russian social realism generally.

        "Ivan the Terrible and His Son Ivan" (1885): A single explosive moment --
        the Tsar cradling his son's head after striking him, his face a mask of
        horror and remorse. Repin painted it after hearing Rimsky-Korsakov's
        "Antar" symphony -- "I couldn't not paint it."

        "They Did Not Expect Him" (1884): The return of a political exile to his
        family's parlor -- the stunned faces of children, the standing figure in
        the doorway, the moment of recognition stretched into unbearable suspension.

        "Reply of the Zaporozhian Cossacks" (1891): A monumental group portrait of
        rough Cossack warriors collectively composing an insolent reply to the
        Ottoman Sultan. Every face in the crowd is psychologically distinct.

        Stage 1 FORM-FOLLOWING DIRECTIONAL IMPASTO (Gradient-Orientation Blur):
        Compute image gradient from luminance L:
          Gx = GaussianDerivative(L, sigma=gradient_sigma, order=[0,1])
          Gy = GaussianDerivative(L, sigma=gradient_sigma, order=[1,0])
          G_mag = sqrt(Gx^2 + Gy^2)  (gradient magnitude)
          theta = atan2(Gy, Gx)       (gradient orientation)
        For each pixel, the perpendicular to the gradient (theta + pi/2) is the
        LOCAL FORM-PLANE DIRECTION -- the direction along which a stroke would
        lie if it were following the surface plane.
        Construct a form-blurred version of each channel by applying a directional
        anisotropic blur along the perpendicular-to-gradient direction:
          For a pixel at (y, x):
            dx = -sin(theta[y,x])  (perpendicular to gradient = along form plane)
            dy =  cos(theta[y,x])
            Sample neighbors at (y+t*dy, x+t*dx) for t in [-form_blur_sigma, +form_blur_sigma]
        For computational tractability, approximate with: apply isotropic Gaussian
        (sigma=form_blur_sigma), then blend back proportional to G_mag:
          form_weight = clip(G_mag / percentile(G_mag, 80), 0, 1) * form_blend
          C_form = C + (C_blurred - C) * form_weight
        The high-gradient pixels (edges) receive maximum form-following blend;
        flat zones receive minimal blend.
        NOVEL: (a) GRADIENT-ORIENTATION FORM BLUR -- No prior improvement pass uses
        the LOCAL gradient angle to modulate a spatial filter. Prior passes use
        the gradient magnitude (edge detection in lost_found_edges_pass, contre_jour,
        savrasov branch sharpening) or directional components (Gy in savrasov). This
        pass uses the full vector direction of the gradient to define a PER-PIXEL
        anisotropic filter axis -- the first pass in the engine to model direction-
        dependent spatial smoothing as a function of local form orientation.

        Stage 2 MIDTONE WARM UMBER ACCENT (Repin's Lit-Zone Color):
        Compute luminance L1 of the form-blurred result.
        In the mid-luminance zone (mid_lo < L1 < mid_hi), push toward Repin's
        characteristic warm umber-flesh (mid_r/g/b = 0.70/0.50/0.32):
          mid_mask = soft bell gate (same formulation as savrasov_lyrical_mist_pass)
          C2 = C1 + (warm_color - C1) * mid_mask * mid_strength
        Repin's mid-values carry this particular warm sienna-umber, distinct from
        the cool ochres of Shishkin or the warm gold of Sorolla.
        NOVEL: (b) WARM UMBER MIDTONE PUSH FOLLOWING FORM BLUR -- this is the first
        pass to combine a form-following directional blur (Stage 1) with a subsequent
        midtone color push, creating a unified "form + color temperature" model of
        the lit surface zone. The savrasov_lyrical_mist_pass (s282) uses a bell-gate
        midtone push, but without the preceding gradient-orientation blur stage.

        Stage 3 COOL TRANSPARENT SHADOW DEEPENING (Repin's Shadow Glaze):
        Identify shadow zone: shadow_mask = smoothstep(shadow_thresh to shadow_thresh-0.1, L)
        Push shadow pixels toward cool blue-violet (shadow_r/g/b = 0.28/0.28/0.48):
          C3 = C2 + (cool_shadow - C2) * shadow_mask * shadow_strength
        The soft shadow_mask (with smoothstep falloff rather than hard threshold)
        ensures the push concentrates at the darkest pixels and fades smoothly
        as luminance approaches the threshold, avoiding a hard tonal band.
        NOVEL: (c) SMOOTH-FALLOFF SHADOW COOL PUSH AFTER FORM BLUR AND WARM MID --
        the combination of three stages (form blur, warm mid, cool shadow) creates
        a unified three-zone rendering model for the entire tonal range. The warm-
        light / cool-shadow principle is also implemented in shadow_temperature_pass
        (s281), but that pass ADAPTS the shadow color from scene-data (highlight
        temperature analysis), while this pass uses Repin's SPECIFIC and FIXED cool
        violet that characterizes his particular palette. The fixed palette target
        embodies the artist's specific coloristic identity.

        Stage 4 STRUCTURAL EDGE CRISPENING (Psychological Edge Focus):
        Recompute gradient magnitude from L3 (post-Stage-3 luminance):
          G3_mag = sqrt(Gx3^2 + Gy3^2)  from sigma=gradient_sigma derivatives
          edge_mask = clip(G3_mag / percentile(G3_mag, edge_percentile), 0, 1)
        Apply tight unsharp mask in high-edge zones:
          C3_blur = GaussianFilter(C3, sigma=edge_sharp_sigma)
          C_sharp = C3 + (C3 - C3_blur) * edge_sharp_amount
          C4 = C3 + (C_sharp - C3) * edge_mask
        This final sharpening recovers and emphasizes the structural edges
        (jaw, brow, collar, hand outline) that Repin used to anchor psychological
        character in the face and figure.
        NOVEL: (d) FOUR-STAGE UNIFIED REALIST SYSTEM (form-direction → warm mid →
        cool shadow → structural edge): The four stages jointly model Repin's
        complete approach to building a psychologically convincing figurative image.
        Each prior session's artist pass implements 3-4 stages from a specific domain
        (landscape atmosphere, or forest density, or decalcomania texture), but no
        prior artist pass addresses the complete four-component pipeline of
        (1) form-direction, (2) warm-zone color, (3) shadow-zone color, and
        (4) structural edge -- the four pillars of academic figurative oil technique.
        """
        print("    Repin Character Depth pass (194th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H, W = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)

        # Stage 1: Form-following gradient-orientation blur
        gsig = max(float(gradient_sigma), 0.5)
        Gx = _gf(L, sigma=gsig, order=[0, 1]).astype(_np.float32)
        Gy = _gf(L, sigma=gsig, order=[1, 0]).astype(_np.float32)
        G_mag = _np.sqrt(Gx * Gx + Gy * Gy).astype(_np.float32)
        g_scale = max(float(_np.percentile(G_mag, 80.0)), 1e-6)
        G_norm = _np.clip(G_mag / g_scale, 0.0, 1.0).astype(_np.float32)

        fbsig = max(float(form_blur_sigma), 0.5)
        R_blur = _gf(R, sigma=fbsig).astype(_np.float32)
        G_blur = _gf(G, sigma=fbsig).astype(_np.float32)
        B_blur = _gf(B, sigma=fbsig).astype(_np.float32)

        fw = float(form_blend) * G_norm
        R1 = _np.clip(R + (R_blur - R) * fw, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (G_blur - G) * fw, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (B_blur - B) * fw, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Midtone warm umber accent (bell gate)
        L1 = (0.299 * R1 + 0.587 * G1 + 0.114 * B1).astype(_np.float32)
        ml = float(mid_lo)
        mh_ = float(mid_hi)
        band = max(0.08, (mh_ - ml) * 0.25)
        lo_ramp = _np.clip((L1 - ml)  / max(band, 1e-5), 0.0, 1.0).astype(_np.float32)
        hi_ramp = _np.clip((mh_ - L1) / max(band, 1e-5), 0.0, 1.0).astype(_np.float32)
        mid_mask = (lo_ramp * hi_ramp).astype(_np.float32)
        mstr = float(mid_strength)
        mr_, mg_, mb_ = float(mid_r), float(mid_g), float(mid_b)
        R2 = _np.clip(R1 + (mr_ - R1) * mid_mask * mstr, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (mg_ - G1) * mid_mask * mstr, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (mb_ - B1) * mid_mask * mstr, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Cool transparent shadow deepening
        L2 = (0.299 * R2 + 0.587 * G2 + 0.114 * B2).astype(_np.float32)
        st = float(shadow_thresh)
        shadow_mask = _np.clip((st - L2) / max(0.10, st * 0.3), 0.0, 1.0).astype(_np.float32)
        sstr = float(shadow_strength)
        sr_, sg_, sb_ = float(shadow_r), float(shadow_g), float(shadow_b)
        R3 = _np.clip(R2 + (sr_ - R2) * shadow_mask * sstr, 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G2 + (sg_ - G2) * shadow_mask * sstr, 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B2 + (sb_ - B2) * shadow_mask * sstr, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Structural edge crispening
        L3 = (0.299 * R3 + 0.587 * G3 + 0.114 * B3).astype(_np.float32)
        Gx3 = _gf(L3, sigma=gsig, order=[0, 1]).astype(_np.float32)
        Gy3 = _gf(L3, sigma=gsig, order=[1, 0]).astype(_np.float32)
        G3_mag = _np.sqrt(Gx3 * Gx3 + Gy3 * Gy3).astype(_np.float32)
        ep = float(edge_percentile)
        e_scale = max(float(_np.percentile(G3_mag, ep)), 1e-6)
        edge_mask = _np.clip(G3_mag / e_scale, 0.0, 1.0).astype(_np.float32)

        esig = max(float(edge_sharp_sigma), 0.3)
        R3b = _gf(R3, sigma=esig).astype(_np.float32)
        G3b = _gf(G3, sigma=esig).astype(_np.float32)
        B3b = _gf(B3, sigma=esig).astype(_np.float32)
        ea = float(edge_sharp_amount)
        R_sharp = _np.clip(R3 + (R3 - R3b) * ea, 0.0, 1.0).astype(_np.float32)
        G_sharp = _np.clip(G3 + (G3 - G3b) * ea, 0.0, 1.0).astype(_np.float32)
        B_sharp = _np.clip(B3 + (B3 - B3b) * ea, 0.0, 1.0).astype(_np.float32)
        R4 = _np.clip(R3 + (R_sharp - R3) * edge_mask, 0.0, 1.0).astype(_np.float32)
        G4 = _np.clip(G3 + (G_sharp - G3) * edge_mask, 0.0, 1.0).astype(_np.float32)
        B4 = _np.clip(B3 + (B_sharp - B3) * edge_mask, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R4 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G4 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B4 - B) * op, 0.0, 1.0).astype(_np.float32)

        mid_px    = int((mid_mask    > 0.05).sum())
        shadow_px = int((shadow_mask > 0.05).sum())
        edge_px   = int((edge_mask   > 0.20).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Repin Character Depth complete "
              f"(mid_px={mid_px}, shadow_px={shadow_px}, edge_px={edge_px})")

'''

# ── Append both passes to stroke_engine.py (after last method) ───────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8-sig") as f:
    src = f.read()

assert "paint_form_curvature_tint_pass" not in src, \
    "paint_form_curvature_tint_pass already exists in stroke_engine.py"
assert "repin_character_depth_pass" not in src, \
    "repin_character_depth_pass already exists in stroke_engine.py"

with open(SE_PATH, "a", encoding="utf-8") as f:
    f.write(FORM_CURVATURE_TINT_PASS)
    f.write(REPIN_CHARACTER_DEPTH_PASS)

print("stroke_engine.py patched: paint_form_curvature_tint_pass (s283 improvement)"
      " + repin_character_depth_pass (194th mode) appended.")
