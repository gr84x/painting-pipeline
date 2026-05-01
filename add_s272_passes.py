"""Insert paint_scumbling_veil_pass (s272 improvement) and
ernst_decalcomania_pass (183rd mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_scumbling_veil_pass (s272 improvement) ──────────────────────

SCUMBLING_VEIL_PASS = '''
    def paint_scumbling_veil_pass(
        self,
        dark_threshold:   float = 0.38,
        veil_lightness:   float = 0.22,
        veil_warmth:      float = 0.04,
        coverage_sigma:   float = 2.5,
        coverage_seed:    int   = 272,
        coverage_density: float = 0.62,
        opacity:          float = 0.55,
    ) -> None:
        r"""Scumbling Veil (Dry Brush Semi-Opaque Light Veil) -- session 272 improvement.

        SIMULATION OF THE CLASSICAL OIL PAINTING TECHNIQUE OF SCUMBLING --
        THE APPLICATION OF A SEMI-OPAQUE LIGHTER PAINT LAYER OVER DRIED DARKER
        PASSAGES WITH A DRY, STIFF BRUSH THAT DEPOSITS PAINT UNEVENLY, LEAVING
        THE UNDERLYING DARK PARTIALLY VISIBLE THROUGH A BROKEN, AIRY VEIL:

        Scumbling is one of the fundamental indirect oil painting techniques,
        distinguished from glazing (which uses transparent dark paint over lighter)
        and from impasto (which uses fully opaque thick paint). In scumbling, a
        LIGHTER paint -- often slightly opaque, often slightly warm -- is dragged
        over a DRIED DARKER surface. The stiff dry brush picks up paint from the
        tube with very little medium and skips across the surface texture, leaving
        paint on the peaks of the ground texture and missing the valleys. The
        result is a broken, open texture that allows the underlying dark to breathe
        through the lighter veil. When viewed from a normal distance, the eye
        blends the two layers and perceives an intermediate tone with atmospheric
        depth -- darker than the scumble color alone, lighter than the dark beneath,
        but with a quality of airiness that neither tone alone could produce.

        The technique was used extensively by:
        -- RUBENS: to veil shadow passages with a warm earth scumble, keeping
           shadows luminous and preventing them from going dead (the scumble
           maintains \'les ombres doivent etre transparentes\' -- shadows must be
           transparent to reflected light).
        -- REMBRANDT: to scumble cool, thin white-grey over dried dark brown
           grounds in his portrait backgrounds, creating the characteristic
           softly luminous dark zone that surrounds his figures.
        -- TURNER: extensive scumbling of pale creams and warm whites over dark
           and mid-tone passages to achieve the atmospheric haze of his mature work.
        -- EL GRECO: scumbling of cool grey-white over deep umber grounds to
           create the silvery grey passages in his drapery shadows.

        The key characteristics of scumbling that distinguish it from other
        passage-modifying techniques:
        (a) LIGHTER OVER DARKER: always applied in the direction from dark to
            light -- a lighter, higher-value paint over a dried darker layer.
        (b) BROKEN COVERAGE: the paint is not applied uniformly. The dry brush
            skips, leaving gaps. This broken quality is essential -- it is what
            gives scumbling its atmospheric, hazy character.
        (c) SEMI-OPAQUE, NOT TRANSPARENT: unlike a glaze, the scumble covers
            rather than tints -- but incompletely.
        (d) TEMPERATURE MODULATION: scumbles are often slightly warmer or cooler
            than the underlying dark, introducing a subtle color contrast at the
            boundary between covered and uncovered areas.

        Stage 1 DARK ZONE IDENTIFICATION: Compute luminance L from the current
        canvas. Identify dark zone pixels as L < dark_threshold. These are the
        areas where real scumbling would be applied -- the shadows, dark grounds,
        and deep tonal passages that benefit from a lightening veil.
        NOVEL: (a) DARK-ZONE-RESTRICTED LIGHTENING VEIL -- all prior paint_
        improvement passes that apply lightening effects (paint_halation_pass,
        paint_luminance_stretch_pass, paint_color_bloom_pass, paint_wet_surface_
        gleam_pass, paint_translucency_bloom_pass, paint_reflected_light_pass)
        either (i) apply to specific zones detected by luminance thresholds but
        then ADD a glow, bloom, or reflection effect driven by nearby bright pixels,
        or (ii) uniformly shift luminance across the image; none of them simulate
        the scumbling process of SELECTIVELY LIGHTENING ONLY DARK ZONES with a
        semi-opaque veil of lighter paint while leaving the already-light zones
        completely untouched -- scumbling has no effect on passages that are
        already lighter than the scumble color.

        Stage 2 VEIL COLOR DERIVATION: For each dark pixel, derive a scumble veil
        color by taking the underlying RGB and computing:
          veil_R = clip(canvas_R + veil_lightness + veil_warmth,   0, 1)
          veil_G = clip(canvas_G + veil_lightness,                 0, 1)
          veil_B = clip(canvas_B + veil_lightness - veil_warmth*2, 0, 1)
        This adds a general lift (veil_lightness) plus a small warm bias
        (veil_warmth shifts red up and blue down), producing a warm, slightly
        opaque light paint color -- just above the underlying dark -- that is
        content-adaptive (it reflects the hue of the underlying passage) rather
        than a fixed preset color.
        NOVEL: (b) CONTENT-ADAPTIVE VEIL COLOR DERIVED FROM UNDERLYING PIXEL --
        prior improvement passes that apply a lightening or tinting effect use
        either (i) a preset fixed color target (paint_atmospheric_recession_pass:
        fixed cool grey-blue), or (ii) a directional hue bias (paint_warm_cool_
        separation_pass), or (iii) a nearby-pixel average (paint_reflected_light_pass);
        none of them derive the applied veil color by taking the UNDERLYING PIXEL
        VALUE AND ADDING a fixed lightness lift plus warm bias -- the scumble veil
        is inherently the color of a lighter, warmer version of what is beneath it,
        not a preset hue imposed from outside.

        Stage 3 BROKEN COVERAGE SIMULATION: Generate a noise coverage mask to
        simulate the dry brush\'s uneven deposition. The mask is computed as:
          noise_field = gaussian_filter(rand_uniform(h,w,seed), sigma=coverage_sigma)
          noise_norm  = (noise_field - min) / (max - min + eps)
          coverage_mask = (noise_norm > (1 - coverage_density)) & dark_zone_mask
        The noise field is spatially correlated (via Gaussian blur) to simulate
        the fact that dry brush coverage is uneven at the scale of brush hairs
        (high frequency) and also at the scale of brush width (low frequency) --
        the Gaussian sigma controls the coverage grain size. The density parameter
        determines what fraction of dark zone pixels receive the scumble veil.
        NOVEL: (c) GAUSSIAN-BLURRED NOISE COVERAGE MASK RESTRICTED TO DARK ZONES --
        no prior paint_ improvement pass uses a SPATIALLY CORRELATED RANDOM COVERAGE
        MASK gated to a luminance-detected zone to simulate partial, broken paint
        deposition; paint_granulation_pass applies noise to the WHOLE image; paint_
        surface_tooth_pass applies a uniform textured modulation; this pass generates
        a noise field, blurs it to achieve paintbrush-scale correlation, thresholds
        it at a density parameter, and gates the result to the dark zone only.

        Stage 4 ATMOSPHERIC OPACITY COMPOSITE: Blend the scumble veil into the
        canvas at the coverage pixels using the global opacity:
          out[y,x] = canvas[y,x] + (veil[y,x] - canvas[y,x]) * coverage_mask[y,x] * opacity
        Outside the dark zone, canvas is unchanged. Within the dark zone but in
        uncovered (noise-below-threshold) pixels, canvas is also unchanged. Only
        covered dark pixels receive the veil, at the strength set by opacity.
        The combination of partial coverage (coverage_density) and opacity produces
        a layered look that reads as a translucent broken veil over deep shadow.
        """
        print("    Scumbling Veil (Dry Brush Semi-Opaque Light Veil) pass (session 272 improvement)...")

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

        # ── Stage 1: Dark zone detection ──────────────────────────────────────
        dark_mask = (lum < float(dark_threshold)).astype(_np.float32)

        # ── Stage 2: Content-adaptive veil color derivation ───────────────────
        vl  = float(veil_lightness)
        vw  = float(veil_warmth)
        veil_r = _np.clip(r0 + vl + vw,        0.0, 1.0).astype(_np.float32)
        veil_g = _np.clip(g0 + vl,              0.0, 1.0).astype(_np.float32)
        veil_b = _np.clip(b0 + vl - vw * 2.0,  0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Broken coverage simulation ───────────────────────────────
        rng = _np.random.default_rng(int(coverage_seed))
        noise_raw = rng.uniform(0.0, 1.0, (h, w)).astype(_np.float32)
        noise_blur = _gf(noise_raw, sigma=float(coverage_sigma)).astype(_np.float32)
        nmin, nmax = float(noise_blur.min()), float(noise_blur.max())
        noise_norm = (noise_blur - nmin) / (nmax - nmin + 1e-8)

        density_thr = 1.0 - float(coverage_density)
        raw_cover   = (noise_norm > density_thr).astype(_np.float32)
        cover_mask  = (raw_cover * dark_mask).astype(_np.float32)

        # ── Stage 4: Atmospheric opacity composite ────────────────────────────
        op = float(opacity)
        blend = cover_mask * op

        out_r = _np.clip(r0 + (veil_r - r0) * blend, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 + (veil_g - g0) * blend, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 + (veil_b - b0) * blend, 0.0, 1.0).astype(_np.float32)

        out_arr = _np.zeros((h, w, 4), dtype=_np.uint8)
        out_arr[:, :, 0] = (out_b * 255).astype(_np.uint8)
        out_arr[:, :, 1] = (out_g * 255).astype(_np.uint8)
        out_arr[:, :, 2] = (out_r * 255).astype(_np.uint8)
        out_arr[:, :, 3] = orig[:, :, 3]

        surface.get_data()[:] = out_arr.tobytes()

'''

# ── Pass 2: ernst_decalcomania_pass (183rd mode) ───────────────────────────────

ERNST_DECALCOMANIA_PASS = '''
    def ernst_decalcomania_pass(
        self,
        pressure_scale:    float = 0.045,
        pressure_octaves:  int   = 6,
        transfer_strength: float = 0.32,
        bio_zone_sigma:    float = 6.0,
        bio_dark_r:        float = 0.28,
        bio_dark_g:        float = 0.18,
        bio_dark_b:        float = 0.10,
        bio_light_r:       float = 0.58,
        bio_light_g:       float = 0.50,
        bio_light_b:       float = 0.38,
        vein_strength:     float = 0.18,
        noise_seed:        int   = 272,
        opacity:           float = 0.70,
    ) -> None:
        r"""Ernst Decalcomania (Biomorphic Paint Transfer Texture) -- session 272, 183rd mode.

        FOUR-STAGE TECHNIQUE INSPIRED BY MAX ERNST (1891-1976) -- GERMAN-FRENCH
        SURREALIST PAINTER AND INVENTOR OF DECALCOMANIA, FROTTAGE, AND GRATTAGE
        AS SYSTEMATIC PAINTERLY TECHNIQUES:

        Max Ernst was one of the most technically inventive painters of the
        twentieth century. Where other Surrealists (Dali, Magritte) achieved
        dreamlike imagery through hyperrealist illusionism applied to impossible
        subjects, Ernst developed a suite of automatic, chance-based techniques
        that allowed unconscious imagery to emerge directly from the physical
        behavior of paint:

        FROTTAGE (1925): Placing paper over a rough surface and rubbing a pencil
        across it, Ernst discovered that the accidental textures produced suggested
        organic forms -- forests, creatures, geological structures. He developed
        this into the series \'Histoire Naturelle\' (1926), where rubbings of
        floorboards, wire mesh, and leaves became primordial landscapes.

        GRATTAGE: Applying a thick layer of paint to canvas and then scraping it
        with a palette knife or toothed implement. The scraping reveals the
        underlying layer in irregular patterns, creating accidental textures that
        suggest bark, rock strata, or skin.

        DECALCOMANIA (1936): Ernst adopted this technique from Oscar Dominguez,
        who had introduced it to the Surrealist group. The method: spread wet
        paint thickly on a sheet of paper or glass; press another surface firmly
        against it; pull the two surfaces apart rapidly. The paint splits along
        lines determined by surface adhesion, pigment viscosity, and the direction
        and speed of separation -- producing dendritic, cave-like, visceral forms
        that no artist could consciously plan. Ernst used decalcomania extensively
        in his later work: \'Surrealism and Painting\' (1942), the \'Antipope\'
        series, and the landmark \'Europe After the Rain II\' (1940-42), where
        the technique produced a post-apocalyptic landscape of ruined cities,
        half-organic spires, and biomorphic rock formations.

        What Ernst saw in decalcomania was the image of GEOLOGICAL TIME compressed
        into the instant of paint separation: the formation of caves by water
        dissolving limestone; the branching of river deltas from above; the growth
        of crystal structures in mineral solution; the articulation of living tissue
        in biological cross-section. His genius was to recognize these textures as
        already-images -- already landscapes, already creatures -- requiring only
        the slightest intervention of the painter\'s selective perception to become
        fully realized paintings.

        KEY WORKS USING DECALCOMANIA:
        -- \'Europe After the Rain II\' (1940-42): The defining decalcomania painting.
           A post-apocalyptic landscape of ruined architecture and organic spires,
           the surface entirely decalcomania texture, painted over in earth ochres,
           prussian blues, and deep greens. The forms are simultaneously geological,
           architectural, and biological.
        -- \'The Eye of Silence\' (1943-44): Decalcomania landscape with central
           eye-like void, desert atmosphere.
        -- \'Vox Angelica\' (1943): Panel painting combining decalcomania texture
           zones with other automatic techniques.
        -- \'Surrealism and Painting\' (1942): Bird-headed Loplop figure amid
           decalcomania environment.

        Stage 1 PRESSURE FIELD GENERATION: Simulate the uneven pressure distribution
        when two surfaces are pressed together and pulled apart. Generate a MULTI-
        OCTAVE TURBULENCE FIELD using layered sine-wave noise at exponentially
        increasing frequencies and exponentially decreasing amplitudes:
          pressure[y,x] = sum_k (1/2^k) * sin(freq_k * x + phase_kx) * sin(freq_k * y + phase_ky)
        where freq_k = pressure_scale * 2^k for k = 0..pressure_octaves-1.
        The turbulence field simulates the complex, multi-scale spatial variation
        of pressure in the paint layer: large-scale undulations (from uneven hand
        pressure) and small-scale irregularities (from surface texture and pigment
        clumping). Normalize the field to [0, 1].
        NOVEL: (a) MULTI-OCTAVE TURBULENCE PRESSURE FIELD FOR PAINT TRANSFER
        SIMULATION -- no prior artist pass uses a turbulence field to model a
        PHYSICAL TRANSFER PROCESS; prior passes use noise for stroke placement
        (paint_granulation_pass), for coverage masks (paint_scumbling_veil_pass),
        or for pattern generation; this pass uses turbulence to model the PRESSURE
        DISTRIBUTION in a two-surface paint separation, which is a fundamentally
        different physical model.

        Stage 2 PAINT TRANSFER ZONE DETECTION: The decalcomania process creates
        two distinct zones:
          HIGH-PRESSURE TRANSFER ZONE (pressure > 0.5 in normalized field): where
            the two surfaces were pressed firmly together, paint TRANSFERS more
            completely, leaving the source surface darker and the result surface
            richer with paint mass. These zones are darker, more saturated.
          LOW-PRESSURE TRANSFER ZONE (pressure <= 0.5): where the surfaces barely
            touched, or where they separated too quickly, paint BRIDGES in thin
            filaments and then ruptures, leaving dendritic \'vein\' patterns at the
            boundary. These zones are paler, with delicate linear structures.
        Compute the BIOMORPHIC BOUNDARY as the gradient of the pressure field
        (after smoothing with bio_zone_sigma): high gradient = zone boundary =
        where the paint-vein dendritic structures form. This boundary is the
        visual signature of decalcomania.
        NOVEL: (b) BIOMORPHIC ZONE BOUNDARY FROM PRESSURE FIELD GRADIENT --
        prior passes that compute zone boundaries use: luminance gradients (paint_
        hue_zone_boundary_pass -- gradient of luminance), content-variance thresholds
        (kittelsen_nordic_mist_pass -- variance-gated luminance), or structural edge
        detectors (paint_sfumato_contour_dissolution_pass -- Canny-equivalent);
        this pass computes the boundary as the GRADIENT OF A SYNTHETIC PRESSURE
        FIELD, not of any pixel property, making the zone structure entirely
        independent of the underlying image content -- the decalcomania texture
        is overlaid as an independent structural layer, just as in the physical
        technique.

        Stage 3 BIOMORPHIC COLOR INJECTION: Apply Ernst\'s characteristic
        decalcomania color palette to the detected zones:
          HIGH-PRESSURE ZONE: blend toward bio_dark (ochre-earth, umber-dark) --
            the dense, rich-pigment color of the thick transferred paint mass.
          LOW-PRESSURE ZONE: blend toward bio_light (pale ochre, sand, warm grey) --
            the thin, drawn-out color of the barely-transferred veil.
          BOUNDARY (vein zone): inject a darker, more saturated color to emphasize
            the dendritic split lines -- the moment where paint bridged and ruptured.
        NOVEL: (c) PRESSURE-FIELD-DRIVEN DUAL-ZONE CHROMATIC INJECTION -- the
        color is determined by the SYNTHETIC pressure field, not by the image
        luminance or any pixel property. The paint chemistry (thick mass = dark,
        thin veil = light, split boundary = dark vein) drives the colorization.
        No prior pass applies color based on a SYNTHETIC PHYSICAL PROCESS FIELD
        rather than on image properties.

        Stage 4 DENDRITIC VEIN REINFORCEMENT: The characteristic linear structures
        of decalcomania -- the fine, branching veins where paint bridged and split --
        are reinforced by darkening the gradient-peak (vein) pixels. The vein
        strength is modulated by the gradient magnitude (stronger at sharp zone
        boundaries, weaker where the pressure field changes gradually). This
        recreates the delicate, hair-fine dendritic lines that cross the pale
        zones in Ernst\'s decalcomania paintings and give them their biological,
        organic quality.
        """
        print("    Ernst Decalcomania (Biomorphic Paint Transfer Texture) pass (session 272, 183rd mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, sobel as _sobel

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Multi-octave turbulence pressure field ───────────────────
        rng = _np.random.default_rng(int(noise_seed))
        ys = _np.arange(h, dtype=_np.float32).reshape(-1, 1)
        xs = _np.arange(w, dtype=_np.float32).reshape(1, -1)

        pressure = _np.zeros((h, w), dtype=_np.float32)
        amp  = 1.0
        freq = float(pressure_scale)
        for k in range(int(pressure_octaves)):
            phx = float(rng.uniform(0, 2 * _np.pi))
            phy = float(rng.uniform(0, 2 * _np.pi))
            phx2 = float(rng.uniform(0, 2 * _np.pi))
            phy2 = float(rng.uniform(0, 2 * _np.pi))
            pressure += amp * (
                _np.sin(freq * xs + phx) * _np.sin(freq * ys + phy) +
                0.5 * _np.sin(freq * 1.7 * xs + phx2) * _np.sin(freq * 1.3 * ys + phy2)
            ).astype(_np.float32)
            amp  *= 0.55
            freq *= 2.0

        pmin, pmax = float(pressure.min()), float(pressure.max())
        pressure = ((pressure - pmin) / (pmax - pmin + 1e-8)).astype(_np.float32)

        # ── Stage 2: Zone detection and boundary gradient ─────────────────────
        ps = float(bio_zone_sigma)
        psmooth = _gf(pressure, sigma=ps).astype(_np.float32)

        gy = _sobel(psmooth.astype(_np.float64), axis=0).astype(_np.float32)
        gx = _sobel(psmooth.astype(_np.float64), axis=1).astype(_np.float32)
        grad_mag = _np.sqrt(gy ** 2 + gx ** 2).astype(_np.float32)
        gmax = float(grad_mag.max())
        grad_norm = (grad_mag / (gmax + 1e-8)).astype(_np.float32)

        high_zone = (pressure > 0.5).astype(_np.float32)
        low_zone  = (1.0 - high_zone).astype(_np.float32)

        # ── Stage 3: Biomorphic color injection ───────────────────────────────
        ts  = float(transfer_strength)
        bdr = float(bio_dark_r)
        bdg = float(bio_dark_g)
        bdb = float(bio_dark_b)
        blr = float(bio_light_r)
        blg = float(bio_light_g)
        blb = float(bio_light_b)

        blend_dark  = high_zone * ts
        blend_light = low_zone  * (ts * 0.65)

        tint_r = _np.clip(
            r0 + (bdr - r0) * blend_dark + (blr - r0) * blend_light, 0.0, 1.0
        ).astype(_np.float32)
        tint_g = _np.clip(
            g0 + (bdg - g0) * blend_dark + (blg - g0) * blend_light, 0.0, 1.0
        ).astype(_np.float32)
        tint_b = _np.clip(
            b0 + (bdb - b0) * blend_dark + (blb - b0) * blend_light, 0.0, 1.0
        ).astype(_np.float32)

        # ── Stage 4: Dendritic vein reinforcement ─────────────────────────────
        vs = float(vein_strength)
        tint_r = _np.clip(tint_r - grad_norm * vs * 0.60, 0.0, 1.0).astype(_np.float32)
        tint_g = _np.clip(tint_g - grad_norm * vs * 0.55, 0.0, 1.0).astype(_np.float32)
        tint_b = _np.clip(tint_b - grad_norm * vs * 0.40, 0.0, 1.0).astype(_np.float32)

        # ── Composite with master opacity ─────────────────────────────────────
        op    = float(opacity)
        out_r = _np.clip(r0 + (tint_r - r0) * op, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 + (tint_g - g0) * op, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 + (tint_b - b0) * op, 0.0, 1.0).astype(_np.float32)

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

if "paint_scumbling_veil_pass" in src:
    print("paint_scumbling_veil_pass already in stroke_engine.py -- skipping.")
else:
    INSERT_BEFORE = "    def kittelsen_nordic_mist_pass("
    idx = src.find(INSERT_BEFORE)
    if idx == -1:
        print("ERROR: could not find kittelsen_nordic_mist_pass insertion point.")
        sys.exit(1)
    new_src = src[:idx] + SCUMBLING_VEIL_PASS + src[idx:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src)
    print("Inserted paint_scumbling_veil_pass into stroke_engine.py.")
    src = new_src

if "ernst_decalcomania_pass" in src:
    print("ernst_decalcomania_pass already in stroke_engine.py -- skipping.")
else:
    INSERT_BEFORE2 = "    def kittelsen_nordic_mist_pass("
    idx2 = src.find(INSERT_BEFORE2)
    if idx2 == -1:
        print("ERROR: could not find second insertion point.")
        sys.exit(1)
    new_src2 = src[:idx2] + ERNST_DECALCOMANIA_PASS + src[idx2:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src2)
    print("Inserted ernst_decalcomania_pass into stroke_engine.py.")
