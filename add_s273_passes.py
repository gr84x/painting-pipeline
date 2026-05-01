"""Insert paint_transparent_glaze_pass (s273 improvement) and
klein_ib_field_pass (184th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_transparent_glaze_pass (s273 improvement) ───────────────────

TRANSPARENT_GLAZE_PASS = '''
    def paint_transparent_glaze_pass(
        self,
        glaze_r:          float = 0.05,
        glaze_g:          float = 0.10,
        glaze_b:          float = 0.75,
        light_threshold:  float = 0.32,
        glaze_strength:   float = 0.30,
        coverage_sigma:   float = 3.2,
        coverage_density: float = 0.70,
        coverage_seed:    int   = 273,
        opacity:          float = 0.65,
    ) -> None:
        r"""Transparent Glaze (Oil Glazing Over Light Passages) -- session 273 improvement.

        SIMULATION OF THE CLASSICAL OIL PAINTING TECHNIQUE OF GLAZING --
        THE APPLICATION OF A THIN LAYER OF TRANSPARENT PIGMENT-IN-MEDIUM OVER
        DRIED LIGHTER PASSAGES TO ENRICH AND DEEPEN COLOR WHILE PRESERVING
        THE LUMINOSITY AND FORM OF THE UNDERPAINT:

        Glazing is one of the oldest and most fundamental indirect oil painting
        techniques, documented in the works of Van Eyck, Raphael, Titian, Rubens,
        and Rembrandt, and distinguished from ALL OTHER paint application techniques
        by its OPTICAL (not chemical) mixing model. Where scumbling (paint_scumbling_
        veil_pass, s272) applies a semi-opaque LIGHTER paint over darker passages
        using a linear coverage blend, glazing uses a TRANSPARENT DARKER paint over
        LIGHTER passages and operates by MULTIPLICATIVE COLOR MIXING -- the physical
        model of a thin transparent colored filter.

        PHYSICAL MODEL -- BEER-LAMBERT THIN-FILM OPTICS:
        When light hits a glazed passage, it must pass through the thin transparent
        glaze layer TWICE: once entering (hitting the underpaint) and once exiting
        (reflecting back toward the viewer). Each passage absorbs wavelengths
        according to the glaze pigment\'s transmittance spectrum. For a glaze of
        color (gr, gg, gb) applied at strength s, the mathematical result is:
          out_channel = original_channel * (1 - s) + original_channel * glaze_channel * s
                      = original_channel * (1 - s + s * glaze_channel)
                      = original_channel * (1 - s * (1 - glaze_channel))
        This is MULTIPLICATIVE BLENDING at strength s -- equivalent to applying a
        tinted transparent glass filter over the underpaint. A pure blue glaze
        (0.05, 0.10, 0.75) suppresses red and green by (1-s), passes blue nearly
        intact -- the underpaint becomes richer and deeper while retaining its form.
        This is fundamentally different from ALL prior paint_ improvement passes,
        which use LINEAR INTERPOLATION (out = A + (B-A)*t) rather than multiplication.
        NOVEL: (a) MULTIPLICATIVE THIN-FILM COMPOSITING (BEER-LAMBERT MODEL) --
        no prior paint_ improvement pass uses multiply-mode compositing; all prior
        passes use linear interpolation: scumbling veil (linterp to bright color),
        reflected light (linterp to ambient reflection), translucency bloom (linterp
        to glow color), chromatic vibration (linterp to shifted hue), aerial
        perspective (linterp to cool grey). The multiply blend is the only physically
        accurate model of transparent-filter light transmission and cannot be achieved
        by linear interpolation.

        THE LIGHT ZONE: Glazing applies to LIGHTER PASSAGES (pixels above
        light_threshold in luminance). This is the mirror image of scumbling (s272),
        which applies only to dark zones (pixels below dark_threshold). Together the
        two passes cover the full tonal range: scumbling modifies shadows, glazing
        modifies lights and midtones. In traditional oil technique, painters alternate
        glaze and scumble layers to build up the full complexity of a painted surface:
        each glaze enriches the color of a light passage; each scumble lightens and
        atmospherizes a dark passage; the combined effect of multiple layers is
        inaccessible to direct painting.
        NOVEL: (b) LIGHT-ZONE RESTRICTION (OPPOSITE ZONE TO SCUMBLING) --
        paint_scumbling_veil_pass (s272) applies only to dark zones (L < threshold),
        leaving bright zones untouched. paint_transparent_glaze_pass applies only to
        light zones (L > threshold), leaving dark zones untouched. No prior pass
        explicitly targets light passages for enrichment while preserving all shadow
        passages from modification -- paint_luminance_stretch_pass shifts the entire
        tonal range; paint_color_bloom_pass blooms around bright zones but adds light,
        not transparent color; paint_aerial_perspective_pass applies to distant zones,
        not to bright zones per se.

        SPATIALLY CORRELATED COVERAGE: The glaze is applied with a brush, which
        deposits paint in a directional, spatially variable pattern. A Gaussian-blurred
        noise field (sigma = coverage_sigma) produces a spatially correlated coverage
        mask with the characteristic scale of brush-width variation. Only pixels in
        the coverage_mask AND above light_threshold receive the glaze.
        NOVEL: (c) BRUSH-PASSAGE COVERAGE MASK FOR GLAZING ZONE -- the same spatially-
        correlated noise mask pattern as scumbling (s272), but applied to the opposite
        luminance zone and with multiplicative rather than linear color mixing.

        HISTORICAL USES OF GLAZING:
        -- VAN EYCK: multiple thin oil glazes over white gesso ground. The gesso
           reflects light back through all glaze layers simultaneously, producing
           the extraordinary luminosity of Flemish panel painting.
        -- TITIAN: golden red glazes (lead white + red lake) over greyed-blue
           underpaint in flesh passages. The glaze warms the grey without losing the
           form established in the underpainting.
        -- RUBENS: transparent warm glazes over cool impasto lights in drapery.
           The glaze adds depth without covering the light.
        -- REMBRANDT: transparent brown-ochre glazes over painted passage to unify
           tone and add the characteristic amber depth of his mature work.
        -- VERMEER: cobalt green glazes (small + malachite + indigo) over lighter
           passages in his blue-green drapery. The glaze gives the characteristic
           deep, jewel-like quality of Vermeer blue that cannot be achieved by any
           direct painting approach.
        """
        print("    Transparent Glaze (Oil Glazing Over Light Passages) pass (session 273 improvement)...")

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

        # ── Stage 1: Light zone detection ─────────────────────────────────────
        light_mask = (lum >= float(light_threshold)).astype(_np.float32)

        # ── Stage 2: Spatially correlated coverage mask ────────────────────────
        rng = _np.random.default_rng(int(coverage_seed))
        noise_raw = rng.uniform(0.0, 1.0, (h, w)).astype(_np.float32)
        noise_blur = _gf(noise_raw, sigma=float(coverage_sigma)).astype(_np.float32)
        nmin, nmax = float(noise_blur.min()), float(noise_blur.max())
        noise_norm = (noise_blur - nmin) / (nmax - nmin + 1e-8)

        density_thr = 1.0 - float(coverage_density)
        raw_cover   = (noise_norm > density_thr).astype(_np.float32)
        cover_mask  = (raw_cover * light_mask).astype(_np.float32)

        # ── Stage 3: Multiplicative glaze (Beer-Lambert thin-film model) ──────
        gr = float(glaze_r)
        gg = float(glaze_g)
        gb = float(glaze_b)
        gs = float(glaze_strength)

        # out_c = original_c * (1 - gs * (1 - glaze_c)) on covered pixels
        glaze_factor_r = 1.0 - gs * (1.0 - gr)
        glaze_factor_g = 1.0 - gs * (1.0 - gg)
        glaze_factor_b = 1.0 - gs * (1.0 - gb)

        glazed_r = _np.clip(r0 * glaze_factor_r, 0.0, 1.0).astype(_np.float32)
        glazed_g = _np.clip(g0 * glaze_factor_g, 0.0, 1.0).astype(_np.float32)
        glazed_b = _np.clip(b0 * glaze_factor_b, 0.0, 1.0).astype(_np.float32)

        # ── Stage 4: Opacity composite over coverage mask ─────────────────────
        op = float(opacity)
        blend = cover_mask * op

        out_r = _np.clip(r0 + (glazed_r - r0) * blend, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 + (glazed_g - g0) * blend, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 + (glazed_b - b0) * blend, 0.0, 1.0).astype(_np.float32)

        out_arr = _np.zeros((h, w, 4), dtype=_np.uint8)
        out_arr[:, :, 0] = (out_b * 255).astype(_np.uint8)
        out_arr[:, :, 1] = (out_g * 255).astype(_np.uint8)
        out_arr[:, :, 2] = (out_r * 255).astype(_np.uint8)
        out_arr[:, :, 3] = orig[:, :, 3]

        surface.get_data()[:] = out_arr.tobytes()

'''

# ── Pass 2: klein_ib_field_pass (184th mode) ──────────────────────────────────

KLEIN_IB_FIELD_PASS = '''
    def klein_ib_field_pass(
        self,
        ikb_r:             float = 0.00,
        ikb_g:             float = 0.18,
        ikb_b:             float = 0.65,
        resonance_weight:  float = 0.70,
        tint_strength:     float = 0.42,
        micro_texture:     float = 0.018,
        texture_seed:      int   = 273,
        depth_amplitude:   float = 0.045,
        depth_scale:       float = 0.008,
        warm_suppress:     float = 0.28,
        opacity:           float = 0.72,
    ) -> None:
        r"""Klein IKB Field (International Klein Blue Monochrome) -- session 273, 184th mode.

        THREE-STAGE TECHNIQUE INSPIRED BY YVES KLEIN (1928-1962) -- FRENCH ARTIST
        AND INVENTOR OF INTERNATIONAL KLEIN BLUE (IKB), ONE OF THE DEFINING WORKS
        OF POST-WAR AVANT-GARDE ART:

        Yves Klein was born in Nice in 1928 and died aged 34, leaving behind a body
        of work of radical simplicity and extraordinary visual power. His central
        contribution -- and his obsession from his earliest works to his final
        paintings -- was the MONOCHROME: a single, perfectly uniform, intensely
        saturated field of pure color applied to canvas, board, or architectural
        surface. Klein was not the first artist to make monochrome paintings (Malevich,
        Rodchenko, and Rauschenberg preceded him), but he was the first to insist on
        the PHYSICAL REALITY of the painted surface as the primary aesthetic event --
        not as a sign pointing to something else (Malevich\'s spiritual absolute) but
        as a direct, unmediated sensory experience.

        INTERNATIONAL KLEIN BLUE (IKB 79):
        Klein\'s decisive technical breakthrough came in 1956, when in collaboration
        with Parisian paint chemist Edouard Adam, he developed a proprietary binding
        medium -- Rhodopas M60A polymer resin dissolved in ethyl acetate and toluene
        -- that could suspend pure ultramarine pigment (PB29, the same pigment used
        in lapis lazuli grinding since the Medieval period) while preserving its
        optical character. Traditional binders (linseed oil, egg tempera, gum arabic)
        coat and darken the pigment crystals: the oil wets the crystal surface and
        reduces the light-scattering differential, diminishing the color\'s apparent
        intensity. Klein\'s Rhodopas resin dries to a MATTE, TRANSPARENT polymer
        film that binds the crystals together while leaving their air-facing surfaces
        free to scatter light independently -- like dry powdered pigment, but fixed
        permanently to the support. The result is a blue that APPEARS TO HAVE NO
        SURFACE: the eye cannot find a reflective plane to rest on, and the color
        appears to extend BEYOND the physical canvas, as if the canvas were an opening
        into an infinite blue space.

        Klein registered IKB as a commercial color on May 19, 1960 (Soleau Envelope
        63471). It is a specific preparation of PB29 ultramarine: in sRGB display
        space, IKB plots at approximately RGB(0, 47, 167) -- a deep, electric
        ultramarine that lies at the extreme saturation limit of the blue gamut
        without crossing into purple (violet) or turquoise (cyan).

        ANTHROPOMETRIES AND FIRE PAINTINGS:
        In addition to monochromes, Klein created two other major series. The
        ANTHROPOMETRIES (1960-61) were made by pressing the bodies of nude models
        (coated in IKB) against white canvas -- the human figure as living brush.
        The gestures were performed in public at Galerie internationale d\'art
        contemporain, Paris, March 1960, to an audience of hundreds, while a chamber
        orchestra played Klein\'s MONOTONE SYMPHONY (1949): a single sustained D-major
        chord for 20 minutes, followed by 20 minutes of silence. The FIRE PAINTINGS
        (FC series, 1961-62) were made with a gas flame, burning the canvas surface
        to carbonize and char specific zones while leaving others intact.

        Stage 1 CHROMATIC RESONANCE-WEIGHTED IKB TINTING: Compute the \'blue
        resonance\' of each pixel -- how aligned it is with the IKB hue vector in
        RGB color space. A pixel with high blue resonance (already in the blue-
        ultramarine family) receives the full IKB tint; a pixel with low resonance
        (warm, orange, or complementary to IKB) receives a reduced tint, softening
        the color transition rather than brutally overpainting. The resonance is
        computed as the normalized dot product of the pixel\'s (r,g,b) vector with
        the IKB color vector: resonance = dot([r,g,b], [ikb_r,ikb_g,ikb_b]) / (|pixel| * |ikb| + eps).
        The tint strength for each pixel is then: effective_strength = tint_strength *
        (resonance_weight * resonance + (1 - resonance_weight)). A perfectly cold
        ultramarine pixel gets full strength; a warm orange pixel gets
        (1-resonance_weight) fraction of full strength.
        NOVEL: (a) CHROMATIC RESONANCE-WEIGHTED TINTING -- no prior artist pass
        applies a tint whose STRENGTH varies by the existing pixel\'s hue affinity
        for the target color. Prior tint passes apply uniform strength to all pixels
        (ernst_decalcomania_pass blends based on pressure zones; okeeffe_organic_form_
        pass biases toward organic hues uniformly; goncharova_rayonist_pass shifts
        hue along directional ray angles). This pass computes a scalar dot-product
        alignment between each pixel\'s existing hue and the target IKB hue and uses
        it to MODULATE tinting strength -- strong tinting of already-blue pixels,
        gentle tinting of warm-family pixels.

        Stage 2 MATTE PIGMENT MICRO-TEXTURE: Klein\'s unique technical achievement
        was removing all binder gloss to expose pure pigment crystals. This produces
        a very fine, high-spatial-frequency texture visible only at close range --
        the surface scattering of individual pigment particles. Simulate by adding
        Gaussian noise at micro-texture amplitude and very small sigma (sigma=0.8
        pixels, below paint_granulation_pass\'s canvas-tooth scale), applied to all
        three channels simultaneously to avoid color noise that would break
        monochrome character.
        NOVEL: (b) SUB-PIXEL-SCALE ISOCHROMATIC MICRO-TEXTURE -- paint_granulation_
        pass (canvas weave texture) and paint_surface_tooth_pass (canvas ground
        interaction) both operate at larger spatial scales (2-8 pixel characteristic
        scale) and apply texture differentially per channel. This pass applies single-
        channel luminance micro-noise at σ<1 pixel (pigment grain scale) to all
        channels equally (isochromatic), preserving monochrome character while
        adding physical surface presence. No prior pass applies purely isochromatic
        micro-noise at sub-pixel sigma.

        Stage 3 WARM SUPPRESSION TOWARD BLUE-NEUTRAL: Klein\'s monochromes
        eliminate all warm hues -- the viewer experiences pure, non-relational color
        with nothing to establish a warm-cool contrast. Identify warm-dominant pixels
        (those where R > B significantly, indicating red/orange/yellow influence)
        and suppress their warmth by reducing R and increasing B proportionally.
        The suppression is proportional to the pixel\'s measured \'warmth\'
        (warmth = max(r - b, 0)) and the warm_suppress parameter.
        NOVEL: (c) HUE-SELECTIVE WARM SUPPRESSION toward cool-blue neutrality --
        prior passes that shift color balance (paint_warm_cool_separation_pass,
        paint_chromatic_underdark_pass, paint_aerial_perspective_pass) all apply
        a FIXED color shift UNIFORMLY to all pixels in a target zone. This pass
        computes each pixel\'s individual WARMTH VALUE (r - b excess) and suppresses
        that specific excess proportionally -- warm pixels are shifted toward blue-
        neutral by an amount proportional to HOW WARM they are; cool pixels are
        unchanged. The suppression is content-adaptive and directional (warm → cool).
        """
        print("    Klein IKB Field (International Klein Blue Monochrome) pass (session 273, 184th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        ir = float(ikb_r)
        ig = float(ikb_g)
        ib = float(ikb_b)
        ikb_mag = (ir**2 + ig**2 + ib**2) ** 0.5 + 1e-8

        # ── Stage 1: Chromatic resonance-weighted IKB tinting ─────────────────
        pixel_mag = _np.sqrt(r0**2 + g0**2 + b0**2).astype(_np.float32) + 1e-8
        dot_product = (r0 * ir + g0 * ig + b0 * ib).astype(_np.float32)
        resonance = _np.clip(dot_product / (pixel_mag * ikb_mag), 0.0, 1.0).astype(_np.float32)

        rw = float(resonance_weight)
        ts = float(tint_strength)
        eff_strength = (ts * (rw * resonance + (1.0 - rw))).astype(_np.float32)

        tinted_r = _np.clip(r0 + (ir - r0) * eff_strength, 0.0, 1.0).astype(_np.float32)
        tinted_g = _np.clip(g0 + (ig - g0) * eff_strength, 0.0, 1.0).astype(_np.float32)
        tinted_b = _np.clip(b0 + (ib - b0) * eff_strength, 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Matte pigment micro-texture (isochromatic) ───────────────
        rng = _np.random.default_rng(int(texture_seed))
        noise_raw = rng.uniform(-1.0, 1.0, (h, w)).astype(_np.float32)
        # Sigma < 1 pixel -- individual pigment grain scale
        noise_micro = _gf(noise_raw, sigma=0.8).astype(_np.float32)
        mt = float(micro_texture)
        # Apply the same luminance noise to all three channels (isochromatic)
        tinted_r = _np.clip(tinted_r + noise_micro * mt, 0.0, 1.0).astype(_np.float32)
        tinted_g = _np.clip(tinted_g + noise_micro * mt, 0.0, 1.0).astype(_np.float32)
        tinted_b = _np.clip(tinted_b + noise_micro * mt, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Warm suppression toward blue-neutral ─────────────────────
        warmth = _np.clip(tinted_r - tinted_b, 0.0, 1.0).astype(_np.float32)
        ws = float(warm_suppress)
        warmth_correction = warmth * ws * 0.5
        tinted_r = _np.clip(tinted_r - warmth_correction, 0.0, 1.0).astype(_np.float32)
        tinted_b = _np.clip(tinted_b + warmth_correction * 0.5, 0.0, 1.0).astype(_np.float32)

        # ── Composite with master opacity ─────────────────────────────────────
        op    = float(opacity)
        out_r = _np.clip(r0 + (tinted_r - r0) * op, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 + (tinted_g - g0) * op, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 + (tinted_b - b0) * op, 0.0, 1.0).astype(_np.float32)

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

if "paint_transparent_glaze_pass" in src:
    print("paint_transparent_glaze_pass already in stroke_engine.py -- skipping.")
else:
    INSERT_BEFORE = "    def paint_scumbling_veil_pass("
    idx = src.find(INSERT_BEFORE)
    if idx == -1:
        print("ERROR: could not find paint_scumbling_veil_pass insertion point.")
        sys.exit(1)
    new_src = src[:idx] + TRANSPARENT_GLAZE_PASS + src[idx:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src)
    print("Inserted paint_transparent_glaze_pass into stroke_engine.py.")
    src = new_src

if "klein_ib_field_pass" in src:
    print("klein_ib_field_pass already in stroke_engine.py -- skipping.")
else:
    INSERT_BEFORE2 = "    def paint_scumbling_veil_pass("
    idx2 = src.find(INSERT_BEFORE2)
    if idx2 == -1:
        print("ERROR: could not find second insertion point.")
        sys.exit(1)
    new_src2 = src[:idx2] + KLEIN_IB_FIELD_PASS + src[idx2:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src2)
    print("Inserted klein_ib_field_pass into stroke_engine.py.")
