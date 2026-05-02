"""Insert paint_frequency_separation_pass (s285 improvement) and
derain_fauve_intensity_pass (196th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_frequency_separation_pass (s285 improvement) ───────────────

FREQUENCY_SEPARATION_PASS = '''
    def paint_frequency_separation_pass(
        self,
        low_sigma:         float = 18.0,
        sat_boost:         float = 0.45,
        lum_contrast:      float = 0.55,
        recombine_weight:  float = 0.72,
        opacity:           float = 0.80,
    ) -> None:
        r"""Frequency Separation -- s285 improvement.

        THE PHYSICAL BASIS: LAPLACIAN PYRAMID DECOMPOSITION OF PAINTED SURFACE

        A painted canvas contains spatial information at multiple scales
        simultaneously:

        1. LOW-FREQUENCY INFORMATION (large spatial scales, sigma >> 1): the
           broad colour masses -- sky vs. ground, flesh vs. background, shadow
           vs. light. These correspond to the painter's initial block-in phase
           and carry the fundamental colour relationships of the composition.
           In low-frequency space, colour is relatively uniform within regions;
           edges are blurred into gradual transitions.

        2. HIGH-FREQUENCY INFORMATION (small spatial scales, sigma ~ 1-3): the
           brushstroke texture, edge accentuation, fine detail, surface grain,
           and stroke-to-stroke variation. These correspond to the painter's
           glazing, scumbling, and final detail work. In high-frequency space,
           large flat areas are nearly zero; detail-rich zones carry signal.

        Frequency separation as a technique originates in photographic retouching
        (digital restoration, portrait photography skin retouching) but has deep
        roots in traditional oil painting practice:
          - Rubens applied successive thin colour glazes over an opaque grisaille
            underpainting -- working low and high frequency on separate layers.
          - Rembrandt's heavy impasto at lights (high-frequency) versus thin
            transparent darks (low-frequency) is a physical frequency separation.
          - Derain and the Fauves consciously worked with broad colour masses
            (low-frequency colour) accented by energetic brushwork (high-frequency
            texture), which makes frequency separation particularly appropriate
            as the s285 improvement alongside the Derain artist pass.

        THE DECOMPOSITION:
          low_freq   = Gaussian(canvas, sigma=low_sigma)       [colour masses]
          high_freq  = canvas - low_freq                        [detail residue]
          canvas     = low_freq + high_freq                     [exact reconstruction]

        The key invariant: low_freq + high_freq = canvas exactly. The high
        frequency component has zero mean over large regions (approximately);
        its values are both positive and negative (the raw colour deviation
        from the local mean). The absolute sum reconstructs the original.

        STAGE 1: LAPLACIAN DECOMPOSITION -- NOVEL TECHNIQUE IN THIS ENGINE.

        Every prior pass in this engine operates on the full-resolution canvas
        directly. No prior pass has separated the canvas into independent spatial-
        frequency components and then modified those components before recombining.

        The closest prior operations:
          - paint_lost_found_edges_pass (s280): blurs selected zones (low-pass) XOR
            sharpens selected zones (unsharp mask = original + (original - blur));
            operates in the luminance-gated edge framework, never decomposes the
            whole canvas into low+high components simultaneously.
          - underpainting / block_in / build_form: operate as separate rendering
            stages with independent stroke calls; they do not decompose the
            current canvas state into frequency bands.
          - Gaussian filtering used in: repin Stage 1, grosz Stage 2 (interior
            flattening via Gaussian), form_curvature_tint Stage 1 -- but always
            applied to the whole canvas, not decomposed and recombined.

        This pass is the first to:
          (i)  decompose the entire canvas into low_freq + high_freq residue;
          (ii) apply DIFFERENT colour operations to each component independently;
          (iii) recombine the modified components into the output.

        Stage 1 LAPLACIAN DECOMPOSITION:
          low_freq  = Gaussian(canvas_RGB, sigma=low_sigma)   [shape: H x W x 3]
          high_freq = canvas_RGB - low_freq                    [signed residue]
        For each channel independently. The Gaussian sigma controls the
        frequency split point: large sigma = more energy in low-freq; small
        sigma = thin colour boundary in low-freq.

        Stage 2 LOW-FREQUENCY SATURATION BOOST:
        In the low-frequency component, the broad colour masses are relatively
        pure and the hue is cleanly delineated. Boosting saturation here
        enriches the fundamental colour identity of each region without
        contaminating edge texture. For each pixel in low_freq:
          grey_lo  = mean(lo_R, lo_G, lo_B)
          lo_R_new = lo_R + (lo_R - grey_lo) * sat_boost
        This is a simple departure-from-grey amplification applied to the
        smooth low-frequency component. The effect is to saturate the broad
        colour zones while leaving the fine detail layer (high_freq) unchanged.
        NOVEL: saturation boost applied exclusively to the LOW-FREQUENCY
        COMPONENT of the decomposed canvas -- no prior pass modifies a
        frequency-separated sub-image.

        Stage 3 HIGH-FREQUENCY LUMINANCE CONTRAST AMPLIFICATION:
        In the high-frequency (detail) component, values range from negative
        (dark side of edges) to positive (bright side). Amplifying this
        component enhances edge contrast and brushstroke visibility. For
        each channel:
          hi_C_new = hi_C * (1.0 + lum_contrast)
        Clipping is deferred to Stage 4 recombination. The effect of amplifying
        the high-frequency residue is equivalent to an unsharp mask but:
          - applied globally (no luminance gate);
          - applied to the isolated high-freq component (not canvas + USM);
          - applied to all colour channels equally (not luminance-only).
        NOVEL: direct amplification of the isolated HIGH-FREQUENCY RESIDUE
        component; structurally distinct from luminance-gated unsharp masking.

        Stage 4 RECOMBINATION WITH CLIPPING AND COMPOSITE:
          reconstructed = clip(lo_R_new + hi_R_new, 0, 1)
        Composite with original at opacity:
          R_out = R + (reconstructed_R - R) * recombine_weight * opacity
        The recombine_weight modulates how much of the frequency-modified
        image replaces the original, allowing partial application that
        preserves some of the pre-separation character.
        """
        print("    Frequency Separation pass (session 285 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        sig = max(float(low_sigma), 1.0)

        # Stage 1: Laplacian decomposition
        lo_R = _gf(R, sigma=sig).astype(_np.float32)
        lo_G = _gf(G, sigma=sig).astype(_np.float32)
        lo_B = _gf(B, sigma=sig).astype(_np.float32)
        hi_R = (R - lo_R).astype(_np.float32)
        hi_G = (G - lo_G).astype(_np.float32)
        hi_B = (B - lo_B).astype(_np.float32)

        # Stage 2: Low-frequency saturation boost
        sb = float(sat_boost)
        grey_lo = ((lo_R + lo_G + lo_B) / 3.0).astype(_np.float32)
        lo_R_new = (lo_R + (lo_R - grey_lo) * sb).astype(_np.float32)
        lo_G_new = (lo_G + (lo_G - grey_lo) * sb).astype(_np.float32)
        lo_B_new = (lo_B + (lo_B - grey_lo) * sb).astype(_np.float32)

        # Stage 3: High-frequency contrast amplification
        lc = float(lum_contrast)
        hi_R_new = (hi_R * (1.0 + lc)).astype(_np.float32)
        hi_G_new = (hi_G * (1.0 + lc)).astype(_np.float32)
        hi_B_new = (hi_B * (1.0 + lc)).astype(_np.float32)

        # Stage 4: Recombination and composite
        rw = float(recombine_weight)
        op = float(opacity)
        blend = rw * op

        R_rec = _np.clip(lo_R_new + hi_R_new, 0.0, 1.0).astype(_np.float32)
        G_rec = _np.clip(lo_G_new + hi_G_new, 0.0, 1.0).astype(_np.float32)
        B_rec = _np.clip(lo_B_new + hi_B_new, 0.0, 1.0).astype(_np.float32)

        R_out = _np.clip(R + (R_rec - R) * blend, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G_rec - G) * blend, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B_rec - B) * blend, 0.0, 1.0).astype(_np.float32)

        lo_px = int(H_ * W_)
        hi_energy = float(_np.mean(_np.abs(hi_R_new) + _np.abs(hi_G_new) + _np.abs(hi_B_new)))

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Frequency Separation complete "
              f"(sigma={sig:.1f}, lo_px={lo_px}, hi_energy={hi_energy:.4f})")

'''

# ── Pass 2: derain_fauve_intensity_pass (196th mode) ─────────────────────────

DERAIN_FAUVE_INTENSITY_PASS = '''
    def derain_fauve_intensity_pass(
        self,
        sat_gamma:         float = 0.60,
        sector_strength:   float = 0.30,
        local_sigma:       float = 14.0,
        contrast_amplify:  float = 0.50,
        angle_strength:    float = 0.22,
        light_angle_deg:   float = 225.0,
        warm_r:            float = 0.92,
        warm_g:            float = 0.74,
        warm_b:            float = 0.34,
        cool_r:            float = 0.28,
        cool_g:            float = 0.50,
        cool_b:            float = 0.88,
        opacity:           float = 0.82,
    ) -> None:
        r"""Derain Fauve Intensity -- 196th mode (Fauvism / André Derain).

        ANDRÉ DERAIN (1880-1954) -- FRENCH FAUVE PAINTER;
        CO-INVENTOR OF FAUVISM WITH HENRI MATISSE:

        André Derain was born in Chatou, a river town on the Seine west of Paris,
        in 1880. He studied at the Académie Carrière in Paris, where he met Henri
        Matisse in 1899 -- a meeting that would catalyse one of the decisive
        stylistic revolutions in Western painting. In the summer of 1905, Derain
        and Matisse worked together at Collioure, a small fishing village on the
        Mediterranean coast of France near the Spanish border, producing a body of
        work that would be exhibited that autumn at the Salon d'Automne. When the
        critic Louis Vauxcelles described Matisse and Derain's canvases as
        surrounded by the works of more conventional painters, he exclaimed: "Donatello
        au milieu des fauves!" -- Donatello among the wild beasts. The name Fauvism
        stuck.

        Derain's contribution to Fauvism was technically and temperamentally
        distinct from Matisse's. Where Matisse was meditative and structured,
        Derain was explosive and direct. He pushed the implications of the Post-
        Impressionist liberation from naturalistic colour further than Matisse
        initially dared. His Collioure paintings of 1905 -- "The Harbour of
        Collioure," "Boats at Collioure," "The Mountains at Collioure" -- are
        studies in chromatic courage: the sea is orange and pink as easily as
        blue; the land is violet and green; the sky is lemon yellow where it
        meets a red horizon. The shadows cast by boats are rendered not in
        dark values of the local colour but in vivid contrasting hues.

        In 1906, Derain moved to London for a commission by the art dealer
        Ambroise Vollard, producing a series of London paintings -- "The Pool of
        London," "Charing Cross Bridge," "The Thames at London" -- that rank among
        the most electrifying urban landscapes in early twentieth-century painting.
        London's grey fog and grey Thames are converted by Derain's Fauve method
        into orange, pink, violet, and deep cobalt -- the city transformed by
        colour into an impossible dream of itself.

        Derain's five defining technical characteristics:

        1. CHROMATIC SATURATION MAXIMISATION: Derain worked with colours squeezed
           directly from the tube, minimally mixed or diluted. He regarded the act
           of mixing colours as a reduction of their energy. Each colour area on
           his canvas carries its maximum achievable chroma. No timid half-tones,
           no grey zones unless grey itself was the local colour.

        2. MULTI-SECTOR SPECTRAL COMMITMENT: Rather than building colour through
           tonal gradations within one hue, Derain allocated distinct hue sectors
           to different regions of the composition and maximised the colour within
           each sector. The sky was not blue-to-white; it was cobalt to cadmium
           orange. The water was not blue-to-black; it was viridian to crimson.
           Each sector commits fully to its hue identity.

        3. LOCAL COLOUR CONTRAST AMPLIFICATION (SIMULTANEOUS CONTRAST):
           Derain understood and exploited Chevreul's law of simultaneous colour
           contrast -- that adjacent complementary colours appear mutually
           intensified. He placed areas of opposing hue deliberately adjacent to
           each other. The spatial effect is that each colour area appears to
           vibrate at its own frequency when placed next to its complement.
           The mathematical implementation: amplify each pixel's colour deviation
           from its local neighbourhood mean, creating maximum colour separation
           between adjacent regions.

        4. GRADIENT-DIRECTED TEMPERATURE ASYMMETRY: In Fauve work (and in
           Impressionism before it), the direction of the light source determines
           a systematic warm/cool temperature asymmetry across the scene. The
           illuminated side of every form -- the side facing the dominant light
           source -- is warmer (more amber, more orange) because it receives the
           direct warm light. The shadowed side -- facing away from the light,
           receiving only sky and reflected light -- is cooler (more blue, more
           violet). Derain made this asymmetry explicit and exaggerated, which in
           Fauve paintings reads as a colour temperature tide moving across the
           canvas. The implementation uses the GRADIENT DIRECTION ANGLE (not just
           gradient magnitude) to determine which side of each form faces the
           light -- a novel gate never before used in this engine.

        5. THE FAUVE GROUND SHOW-THROUGH: Derain often worked rapidly on raw or
           white-primed canvas, leaving areas of the ground visible between
           energetic strokes. The visible ground acts as a fourth neutral zone
           between the chromatic passages -- an unpainted white that optically
           mixes with the surrounding vivid colours. The pipeline models this
           effect via the frequency-separation improvement (paint_frequency_
           separation_pass), which separates and independently enhances the
           broad colour masses and fine stroke texture.

        THE GREAT WORKS:
        "The Pool of London" (1906): The Thames crowded with dark sailing vessels,
        their hulls reflected in water rendered as orange and ochre -- London's
        industrial sky transformed into vivid gold.

        "Boats at Collioure" (1905): The Collioure harbour with moored boats
        rendered in slabs of pure cadmium orange, cobalt blue, and viridian --
        colour used as flat structural zone rather than atmospheric gradient.

        "Mountains at Collioure" (1905): The Pyrenean foothills behind Collioure
        rendered as interlocking planes of vivid violet, orange, and yellow-green
        -- landscape geometry made visible through chromatic contrast.

        "Charing Cross Bridge" (1906): The Thames at night with the railway bridge
        silhouetted against an orange sky -- London remade as a Fauve dream.

        "Harbour of Collioure" (1905): Collioure's medieval fortifications seen
        from the water, rendered in the flattened, poster-like colour zones that
        define Derain's mature Fauve technique.

        NOVELTY ANALYSIS: FOUR DISTINCT MATHEMATICAL INNOVATIONS:

        Stage 1 HSV SATURATION POWER CURVE (Chromatic Saturation Maximisation):
        Prior passes in this engine that operate in HSV space:
          - paint_chromatic_shadow_shift_pass (s284): modifies the HUE channel
            (H) with angular rotation. S and V are preserved unchanged.
          - All other passes: operate directly in RGB without HSV conversion.
        This stage modifies the SATURATION CHANNEL (S), applying a power-law
        curve: S_new = S^sat_gamma. With sat_gamma < 1 (default 0.60):
          S_new > S for all S > 0: saturation is expanded toward maximum.
          The curve shape is concave-up: weak saturation is boosted most.
        Specifically, S=0.30 → S_new = 0.30^0.60 = 0.51; S=0.60 → 0.74;
        S=0.90 → 0.93. Low-saturation areas gain the most; fully saturated
        areas are already at max. The power curve gives a smooth, non-clipping
        boost that preserves relative hue relationships while universally
        pushing colours toward purity.
        NOVEL: (a) POWER-LAW CURVE ON THE S CHANNEL OF HSV -- first pass to
        operate a gamma transformation on the saturation (S) channel. s284
        operated on H (angular); no prior pass operated on S or V independently.

        Stage 2 SIX-SECTOR HUE COMMITMENT (Multi-Sector Spectral Push):
        Using the current H channel (after stage 1 RGB→HSV), classify each
        pixel into one of six spectral sectors:
          Sector 0 (H ∈ [0, 1/6)): red-orange → push toward cadmium orange-red
          Sector 1 (H ∈ [1/6, 2/6)): yellow → push toward cadmium yellow
          Sector 2 (H ∈ [2/6, 3/6)): yellow-green/green → push toward viridian
          Sector 3 (H ∈ [3/6, 4/6)): cyan-turquoise → push toward cerulean
          Sector 4 (H ∈ [4/6, 5/6)): blue-violet → push toward cobalt blue
          Sector 5 (H ∈ [5/6, 1)): magenta-red → push toward crimson-violet
        For each sector, push the pixel's H toward the sector centre:
          H_target = sector_center[sector]
          H_new = H + (H_target - H) * S * sector_strength
        The push is weighted by S (saturation): grey pixels (S~0) receive no
        push; vivid pixels (S~1) receive full push. This ensures the hue
        sectoring only affects already-vivid chromatic areas.
        NOVEL: (b) SIX-SECTOR HUE CLASSIFICATION -- first pass to divide the
        colour wheel into 6 explicit hue sectors and apply a different push
        target per sector. Prior passes push toward one fixed colour (warm or
        cool target); paint_chromatic_shadow_shift_pass (s284) rotates ALL
        hues by the same fixed angle. Here each pixel's push direction and
        target depend on which hue sector it inhabits -- hue determines
        destination.

        Stage 3 LOCAL COLOUR CONTRAST AMPLIFICATION (Simultaneous Contrast):
        For each RGB channel independently:
          neighbourhood_mean = Gaussian(C, sigma=local_sigma)
          C_contrast = clip(C + (C - neighbourhood_mean) * contrast_amplify, 0, 1)
        This amplifies each pixel's colour deviation from its local spatial mean,
        increasing inter-area colour separation without gating on luminance or
        gradient magnitude.
        NOVEL: (c) UNIFORM COLOUR-CHANNEL LOCAL CONTRAST AMPLIFICATION -- prior
        sharpening passes in this engine use luminance gradient as the gate:
          - repin_character_depth_pass Stage 4: unsharp mask gated by G_norm > thresh
          - paint_lost_found_edges_pass: luminance-gradient controlled sharpening
        This stage amplifies colour departures from local mean uniformly across
        all three channels without any luminance gate or edge gate. The effect
        is equivalent to spatial saturation boosting but derived from the
        local colour context (the deviation is relative to local neighbours,
        not relative to global grey). Complementary colours placed adjacent to
        each other are mutually amplified; similar-hue neighbours suppress each
        other (their mean is already near their value).

        Stage 4 GRADIENT-ANGLE WARM/COOL DIRECTIONAL PUSH (Temperature Asymmetry):
        Compute the spatial gradient of the luminance channel:
          L = 0.299 R + 0.587 G + 0.114 B
          Gx = d/dx(L, sigma=2.5)
          Gy = d/dy(L, sigma=2.5)
          gradient_angle = atan2(Gy, Gx)   [range: -pi to pi]
        The gradient angle points from dark to bright (in the direction of
        increasing luminance). The light source direction (light_angle_deg,
        measured from +x axis counterclockwise, default 225° = upper-left)
        defines which pixels face the light:
          angle_diff = cos(gradient_angle - light_angle_rad)
          light_mask = clip(angle_diff, 0, 1)   [1 = fully facing light]
          shadow_mask = clip(-angle_diff, 0, 1)  [1 = fully facing away]
        Gate by gradient magnitude G_norm (only meaningful at edges):
          light_mask  *= G_norm
          shadow_mask *= G_norm
        Apply warm push to light-facing zones, cool push to shadow-facing zones:
          R3 = R2 + light_mask * angle_strength * (warm_r - R2)
               + shadow_mask * angle_strength * (cool_r - R2)
        NOVEL: (d) GRADIENT DIRECTION ANGLE AS ZONE GATE -- no prior pass uses
        atan2(Gy, Gx) to determine directional facing. Prior gradient passes use:
          - G_norm = sqrt(Gx^2 + Gy^2): magnitude only (repin, savrasov, kokoschka)
          - Gx alone (signed): directional but only one axis (grosz_neue_sachlichkeit
            Stage 1 uses signed Gx for cast shadow -- a fixed-axis choice).
          - Gy alone: vertical derivative (savrasov Stage 3 for branch sharpening)
        This stage uses the FULL 2D GRADIENT VECTOR ANGLE via atan2(), classifying
        whether each pixel's gradient vector points toward or away from the chosen
        light source direction. The dot product cos(gradient_angle - light_angle)
        is the first use of a DIRECTIONAL COSINE as a zone gate in this engine.
        Gx (grosz Stage 1) is a fixed-axis directional choice (always horizontal);
        the atan2() angle gate works for any light direction, computed per-pixel.
        """
        print("    Derain Fauve Intensity pass (196th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        # Stage 1: HSV saturation power curve (S-channel gamma)
        sg = max(float(sat_gamma), 0.10)

        Cmax = _np.maximum(_np.maximum(R, G), B).astype(_np.float32)
        Cmin = _np.minimum(_np.minimum(R, G), B).astype(_np.float32)
        delta = (Cmax - Cmin).astype(_np.float32)
        eps = 1e-8

        V_ch = Cmax.copy()
        S_ch = _np.where(Cmax > eps, delta / _np.maximum(Cmax, eps), 0.0
                         ).astype(_np.float32)

        d_safe = _np.maximum(delta, eps)
        mask_r = (Cmax == R) & (delta > eps)
        mask_g = (Cmax == G) & (delta > eps)
        mask_b = (Cmax == B) & (delta > eps)
        H_ch = _np.zeros((H_, W_), dtype=_np.float32)
        H_ch = _np.where(mask_r, ((G - B) / d_safe) % 6.0, H_ch)
        H_ch = _np.where(mask_g, (B - R) / d_safe + 2.0, H_ch)
        H_ch = _np.where(mask_b, (R - G) / d_safe + 4.0, H_ch)
        H_ch = (H_ch / 6.0).astype(_np.float32)  # [0, 1]

        # Power-law saturation expansion
        S_new = _np.power(_np.clip(S_ch, 0.0, 1.0), sg).astype(_np.float32)

        # Stage 2: Six-sector hue commitment (hue push toward sector spectral centre)
        # Sector centres (normalised hue 0-1): red-orange, yellow, green, cyan, blue, magenta
        sector_centers = _np.array([0.04, 0.17, 0.35, 0.50, 0.67, 0.92],
                                    dtype=_np.float32)
        ss = float(sector_strength)
        H_new = H_ch.copy()
        for sec_idx in range(6):
            lo = sec_idx / 6.0
            hi = (sec_idx + 1) / 6.0
            in_sector = (H_ch >= lo) & (H_ch < hi)
            center = sector_centers[sec_idx]
            delta_h = center - H_ch
            H_new = _np.where(in_sector, H_ch + delta_h * S_new * ss, H_new)
        H_new = (H_new % 1.0).astype(_np.float32)

        # HSV → RGB reconstruction after stage 1+2
        h6   = H_new * 6.0
        i_ch = _np.floor(h6).astype(_np.int32) % 6
        f_ch = (h6 - _np.floor(h6)).astype(_np.float32)
        p_ch = (V_ch * (1.0 - S_new)).astype(_np.float32)
        q_ch = (V_ch * (1.0 - f_ch * S_new)).astype(_np.float32)
        t_ch = (V_ch * (1.0 - (1.0 - f_ch) * S_new)).astype(_np.float32)

        R1 = _np.select(
            [i_ch == 0, i_ch == 1, i_ch == 2, i_ch == 3, i_ch == 4, i_ch == 5],
            [V_ch, q_ch, p_ch, p_ch, t_ch, V_ch]
        ).astype(_np.float32)
        G1 = _np.select(
            [i_ch == 0, i_ch == 1, i_ch == 2, i_ch == 3, i_ch == 4, i_ch == 5],
            [t_ch, V_ch, V_ch, q_ch, p_ch, p_ch]
        ).astype(_np.float32)
        B1 = _np.select(
            [i_ch == 0, i_ch == 1, i_ch == 2, i_ch == 3, i_ch == 4, i_ch == 5],
            [p_ch, p_ch, t_ch, V_ch, V_ch, q_ch]
        ).astype(_np.float32)

        R1 = _np.clip(R1, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G1, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B1, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Local colour contrast amplification (simultaneous contrast)
        lsig = max(float(local_sigma), 2.0)
        ca   = float(contrast_amplify)
        mn_R = _gf(R1, sigma=lsig).astype(_np.float32)
        mn_G = _gf(G1, sigma=lsig).astype(_np.float32)
        mn_B = _gf(B1, sigma=lsig).astype(_np.float32)
        R2 = _np.clip(R1 + (R1 - mn_R) * ca, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (G1 - mn_G) * ca, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (B1 - mn_B) * ca, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Gradient-angle warm/cool directional push
        L = (0.299 * R2 + 0.587 * G2 + 0.114 * B2).astype(_np.float32)
        gsig2 = 2.5
        Gx = _gf(L, sigma=gsig2, order=[0, 1]).astype(_np.float32)
        Gy = _gf(L, sigma=gsig2, order=[1, 0]).astype(_np.float32)
        G_mag = _np.sqrt(Gx * Gx + Gy * Gy).astype(_np.float32)
        G_norm = (_np.clip(G_mag / _np.maximum(
            float(_np.percentile(G_mag, 90.0)), 1e-6), 0.0, 1.0
        )).astype(_np.float32)

        light_rad = float(light_angle_deg) * _np.pi / 180.0
        grad_angle = _np.arctan2(Gy, Gx).astype(_np.float32)
        dot = _np.cos(grad_angle - light_rad).astype(_np.float32)
        light_mask  = (_np.clip(dot,  0.0, 1.0) * G_norm).astype(_np.float32)
        shadow_mask = (_np.clip(-dot, 0.0, 1.0) * G_norm).astype(_np.float32)

        astr = float(angle_strength)
        wr, wg, wb = float(warm_r), float(warm_g), float(warm_b)
        cr_, cg_, cb_ = float(cool_r), float(cool_g), float(cool_b)

        R3 = _np.clip(
            R2 + light_mask * astr * (wr - R2) + shadow_mask * astr * (cr_ - R2),
            0.0, 1.0
        ).astype(_np.float32)
        G3 = _np.clip(
            G2 + light_mask * astr * (wg - G2) + shadow_mask * astr * (cg_ - G2),
            0.0, 1.0
        ).astype(_np.float32)
        B3 = _np.clip(
            B2 + light_mask * astr * (wb - B2) + shadow_mask * astr * (cb_ - B2),
            0.0, 1.0
        ).astype(_np.float32)

        # Final composite
        op = float(opacity)
        R_out = _np.clip(R + (R3 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G3 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B3 - B) * op, 0.0, 1.0).astype(_np.float32)

        sat_px   = int((S_new > 0.50).sum())
        light_px = int((light_mask  > 0.10).sum())
        shad_px  = int((shadow_mask > 0.10).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Derain Fauve Intensity complete "
              f"(sat_px={sat_px}, light_px={light_px}, shadow_px={shad_px})")

'''

# ── Append both passes to stroke_engine.py ───────────────────────────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8-sig") as f:
    src = f.read()

assert "paint_frequency_separation_pass" not in src, \
    "paint_frequency_separation_pass already exists in stroke_engine.py"
assert "derain_fauve_intensity_pass" not in src, \
    "derain_fauve_intensity_pass already exists in stroke_engine.py"

with open(SE_PATH, "a", encoding="utf-8") as f:
    f.write(FREQUENCY_SEPARATION_PASS)
    f.write(DERAIN_FAUVE_INTENSITY_PASS)

print("stroke_engine.py patched: paint_frequency_separation_pass (s285 improvement)"
      " + derain_fauve_intensity_pass (196th mode) appended.")
