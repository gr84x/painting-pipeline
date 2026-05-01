"""Insert paint_reflected_light_pass (s271 improvement) and
kittelsen_nordic_mist_pass (182nd mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_reflected_light_pass (s271 improvement) ─────────────────────

REFLECTED_LIGHT_PASS = '''
    def paint_reflected_light_pass(
        self,
        shadow_threshold: float = 0.30,
        light_threshold:  float = 0.60,
        search_radius:    float = 40.0,
        reflect_strength: float = 0.18,
        sky_cool:         float = 0.06,
        ground_warm:      float = 0.05,
        noise_seed:       int   = 271,
        opacity:          float = 0.68,
    ) -> None:
        r"""Reflected Light (Secondary/Bounce Light Injection) -- session 271 improvement.

        SIMULATION OF SECONDARY LIGHT BOUNCE IN OIL PAINTING -- THE PHYSICAL
        PROCESS WHEREBY LIGHT REFLECTED FROM ILLUMINATED SURFACES RE-ENTERS
        ADJACENT SHADOW ZONES, MODIFYING THEIR COLOUR AND LIGHTENING THEIR
        DEEPEST PASSAGES:

        In classical oil painting, shadows are never truly dark or neutral:
        they are always partially illuminated by SECONDARY LIGHT -- light that
        has first struck an illuminated surface and then bounced into the shadow
        zone. This secondary light carries the colour of the reflecting surface.
        A red wall reflects warm pinkish light into the shadow on its neighbour;
        a pale sandy ground reflects warm golden bounce into the shadow beneath
        a figure; the open sky reflects cool blue into any upward-facing shadow
        surface. The Venetians understood this as \'luce riflessa\' (reflected
        light); the French academic tradition codified it in the principle that
        \'les ombres participent de la couleur du reflet\' (shadows share the colour
        of the reflected source). Velazquez painted the reflected warm-rose of
        a cardinal\'s robe into the shadow of his neck; Vermeer placed a cool
        blue sky reflection in every shadow on his white walls; Sorolla loaded
        shadows under beach umbrellas with turquoise bounce from the sea.

        The key physical parameters are:
        (a) PROXIMITY: the strength of the reflected light falls off with distance
            from the reflecting surface -- shadows immediately adjacent to a lit
            surface receive the strongest bounce, while distant shadow regions
            receive little. This is the inverse-square law applied to bounced light.
        (b) SHADOW DEPTH: reflected light penetrates shadow zones from the edge
            inward; very deep shadows (far from any lit surface) receive the
            least secondary light.
        (c) COLOUR DERIVATION: the reflected light colour is not a preset warm/cool
            bias, but the ACTUAL colour of nearby lit surfaces, averaged over
            a neighbourhood weighted by proximity.

        Stage 1 SHADOW AND LIGHT ZONE DETECTION: Compute luminance L from the
        current canvas. Pixels with L < shadow_threshold form the SHADOW ZONE;
        pixels with L >= light_threshold form the LIGHT ZONE. The threshold gap
        [shadow_threshold, light_threshold] identifies mid-tone pixels that are
        neither clearly lit nor clearly shadowed -- these are handled with a
        partial weighting. The shadow_mask is a hard binary; the light_mask is
        similarly binary.
        NOVEL: (a) BINARY ZONE SEGMENTATION USED AS SOURCE AND SINK FOR REFLECTED
        LIGHT -- prior passes that touch shadow zones (paint_chromatic_underdark_pass,
        shadow_temperature_relief_pass, paint_warm_cool_separation_pass) apply
        PRESET hue shifts or warm/cool biases; none of them derive the injected
        colour from the actual colours of nearby LIT ZONE PIXELS sampled from
        the current canvas state. This pass uses the existing lit pixel values
        as the source of the reflected colour, making it fully content-adaptive
        rather than a fixed preset.

        Stage 2 PROXIMITY-WEIGHTED LIT SURFACE COLOUR SAMPLING: For each pixel
        position, compute a GAUSSIAN-BLURRED weighted average of the lit zone
        pixel colours using sigma = search_radius / 2.0 (so that the effective
        influence radius of any lit pixel on surrounding shadow pixels equals
        approximately search_radius / 2 standard deviations):
          lit_R_blur = gaussian_filter(R * light_mask, sigma=search_sigma)
          lit_weight = gaussian_filter(light_mask, sigma=search_sigma)
          avg_R[y,x]  = lit_R_blur[y,x] / (lit_weight[y,x] + epsilon)
        The Gaussian blur implicitly implements the inverse-distance weighting:
        nearby lit pixels contribute more to the local average than distant ones.
        NOVEL: (b) GAUSSIAN-BLURRED CONTENT-DERIVED REFLECTED COLOUR -- no prior
        paint_ improvement pass blurs the ACTUAL CANVAS COLOURS of lit-zone pixels
        and uses the result as a spatially-varying reflected colour source; all
        prior shadow-modifying passes use either (i) a fixed preset colour/hue,
        (ii) a luminance-gradient-based warm/cool temperature, or (iii) a
        structural ambient occlusion factor; this pass samples the current lit-zone
        RGB values and diffuses them as reflected colour without any preset bias.

        Stage 3 EDGE-BIASED REFLECTED LIGHT INJECTION: The reflected light is
        injected into shadow zone pixels with a strength that depends on:
          (i) how much nearby lit surface is available (lit_avail, normalised
              to [0,1] using the 95th percentile of lit_weight as reference)
          (ii) shadow EDGE PROXIMITY: at the shadow boundary (lum just below
               shadow_threshold), edge_factor = 1.0; deep in the shadow
               (lum approaching 0), edge_factor fades to 0.2, reflecting the
               physics that secondary light penetrates the shadow from the edge
               inward, not from the centre outward
          reflect_amount = shadow_mask * edge_factor * lit_avail * reflect_strength
        NOVEL: (c) EDGE-BIASED INJECTION MODULATED BY SHADOW DEPTH AND LIT
        AVAILABILITY -- the combination of (shadow-edge proximity) AND (nearby
        lit surface quantity) as the two-factor modulator of injection strength
        is not present in any prior pass; paint_warm_ambient_occlusion_pass uses
        structural occlusion (how enclosed a pixel is geometrically) but not
        shadow-edge proximity nor actual lit-zone sampling.

        Stage 4 VERTICAL COOL-SKY / WARM-GROUND SECONDARY BIAS: After injecting
        the content-derived reflected colour, apply a physically-motivated vertical
        bias: pixels in the UPPER portion of the canvas (sky-facing surfaces) receive
        an additional cool-blue secondary term (sky_cool) because the open sky is
        always a secondary illuminant for upward-facing shadow surfaces; pixels in
        the LOWER portion receive a warm-yellow secondary term (ground_warm) because
        the ground reflects warm light upward into downward-facing shadow passages.
        The bias is applied only within the shadow zone and scales linearly with
        vertical position (0=top, 1=bottom for the warm bias; inverted for cool bias).
        NOVEL: (d) POSITION-DEPENDENT SECONDARY ILLUMINANT BIAS -- the prior
        paint_warm_cool_separation_pass applies a smooth horizontal or vertical
        warm/cool gradient globally; this pass applies the bias ONLY in shadow
        zones, weighted by vertical position, and adds it ON TOP OF the
        content-derived reflected colour, making the final shadow colour the sum
        of actual bounce light from the scene AND the secondary illuminant bias.
        """
        print("    Reflected Light (Secondary Bounce Light Injection) pass (session 271 improvement)...")

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

        # ── Stage 1: Shadow and Light Zone Detection ──────────────────────────
        st  = float(shadow_threshold)
        lt  = float(light_threshold)
        shadow_mask = (lum < st).astype(_np.float32)
        light_mask  = (lum >= lt).astype(_np.float32)

        # ── Stage 2: Proximity-Weighted Lit Surface Colour Sampling ───────────
        search_sigma = max(float(search_radius) / 2.0, 1.0)

        lit_r_blur = _gf(r0 * light_mask, sigma=search_sigma).astype(_np.float32)
        lit_g_blur = _gf(g0 * light_mask, sigma=search_sigma).astype(_np.float32)
        lit_b_blur = _gf(b0 * light_mask, sigma=search_sigma).astype(_np.float32)
        lit_weight = _gf(light_mask, sigma=search_sigma).astype(_np.float32)

        safe_w = _np.where(lit_weight > 1e-5, lit_weight, _np.ones_like(lit_weight))
        avg_r  = (lit_r_blur / safe_w).astype(_np.float32)
        avg_g  = (lit_g_blur / safe_w).astype(_np.float32)
        avg_b  = (lit_b_blur / safe_w).astype(_np.float32)

        # ── Stage 3: Edge-Biased Reflected Light Injection ────────────────────
        rs    = float(reflect_strength)

        # Normalise lit_weight availability
        lit_95 = float(_np.percentile(lit_weight, 95))
        lit_avail = _np.clip(lit_weight / (lit_95 + 1e-6), 0.0, 1.0).astype(_np.float32)

        # Shadow edge proximity: 0 at boundary (lum just below st), 1 deep in shadow
        shadow_edge_depth = _np.clip(1.0 - lum / (st + 1e-6), 0.0, 1.0).astype(_np.float32)
        edge_factor = _np.clip(1.0 - shadow_edge_depth * 0.80, 0.20, 1.0).astype(_np.float32)

        reflect_amount = (shadow_mask * edge_factor * lit_avail * rs).astype(_np.float32)

        # Inject reflected colour into shadow
        inj_r = _np.clip(r0 + (avg_r - r0) * reflect_amount, 0.0, 1.0).astype(_np.float32)
        inj_g = _np.clip(g0 + (avg_g - g0) * reflect_amount, 0.0, 1.0).astype(_np.float32)
        inj_b = _np.clip(b0 + (avg_b - b0) * reflect_amount, 0.0, 1.0).astype(_np.float32)

        # ── Stage 4: Vertical Cool-Sky / Warm-Ground Secondary Bias ───────────
        sc = float(sky_cool)
        gw = float(ground_warm)

        h_frac = _np.linspace(0.0, 1.0, h, dtype=_np.float32)[:, _np.newaxis]  # 0=top, 1=bottom
        sky_factor    = ((1.0 - h_frac) * sc * shadow_mask).astype(_np.float32)
        ground_factor = (h_frac * gw * shadow_mask).astype(_np.float32)

        # Cool sky bounce: raise B, suppress R
        fin_r = _np.clip(inj_r + ground_factor * 0.80 - sky_factor * 0.40, 0.0, 1.0).astype(_np.float32)
        fin_g = _np.clip(inj_g + ground_factor * 0.50 - sky_factor * 0.10, 0.0, 1.0).astype(_np.float32)
        fin_b = _np.clip(inj_b - ground_factor * 0.20 + sky_factor * 0.80, 0.0, 1.0).astype(_np.float32)

        # ── Composite with master opacity ─────────────────────────────────────
        op    = float(opacity)
        out_r = _np.clip(r0 + (fin_r - r0) * op, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 + (fin_g - g0) * op, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 + (fin_b - b0) * op, 0.0, 1.0).astype(_np.float32)

        out_arr = _np.zeros((h, w, 4), dtype=_np.uint8)
        out_arr[:, :, 0] = (out_b * 255).astype(_np.uint8)
        out_arr[:, :, 1] = (out_g * 255).astype(_np.uint8)
        out_arr[:, :, 2] = (out_r * 255).astype(_np.uint8)
        out_arr[:, :, 3] = orig[:, :, 3]

        surface.get_data()[:] = out_arr.tobytes()

'''

# ── Pass 2: kittelsen_nordic_mist_pass (182nd mode) ──────────────────────────

KITTELSEN_NORDIC_MIST_PASS = '''
    def kittelsen_nordic_mist_pass(
        self,
        variance_sigma:      float = 8.0,
        far_lum_low:         float = 0.38,
        far_lum_high:        float = 0.82,
        haze_r:              float = 0.60,
        haze_g:              float = 0.65,
        haze_b:              float = 0.78,
        haze_strength:       float = 0.26,
        silhouette_contrast: float = 0.22,
        dark_violet_r:       float = 0.07,
        dark_violet_g:       float = 0.09,
        dark_violet_b:       float = 0.24,
        dark_strength:       float = 0.28,
        dark_threshold:      float = 0.18,
        noise_seed:          int   = 271,
        opacity:             float = 0.74,
    ) -> None:
        r"""Kittelsen Nordic Mist (Atmospheric Twilight Landscape) -- session 271, 182nd mode.

        FOUR-STAGE ATMOSPHERIC TECHNIQUE INSPIRED BY THEODOR KITTELSEN (1857-1914)
        -- NORWEGIAN PAINTER, ILLUSTRATOR, AND THE DEFINITIVE VISUAL INTERPRETER
        OF NORSE FOLKLORE AND THE NORDIC LANDSCAPE:

        Theodor Kittelsen spent most of his working life in the mountains and
        forests of Norway -- at Fossli above Vøringsfossen, on the shores of
        Tyrifjorden, in the Telemark wilderness, at Snøasen on the Ringerike
        plateau. His painting and illustration emerged directly from this
        landscape: dark peat bogs, birch groves, fjord twilights, misty
        forests populated with his legendary trolls, nisse, and spirits.
        Where the Danish and German Romantics (Friedrich, Dahl) composed their
        landscapes with academic discipline, Kittelsen worked intuitively from
        direct observation and from the interior of Norwegian folk culture.

        The dominant visual characteristic of his atmospheric landscape paintings
        (\'Soria Moria\', \'Black Death\', \'The Plague on the Stair\', the Trollseries)
        is the systematic opposition of NEAR SILHOUETTE against FAR LUMINOSITY.
        In Kittelsen\'s world, near elements are almost black -- dark birch
        silhouettes, heather tufts, peat surfaces -- and they are cut sharply
        against sky, water, or misty middleground that is dramatically lighter.
        The sky is rarely warm: it ranges from cold amber-gold at the very
        horizon (a Norwegian winter twilight) through pale steel blue to deep
        prussian blue-violet at the zenith. His shadows are never black or neutral --
        they carry a deep blue-violet quality that pulls even the darkest zones
        away from simple darkness and into the register of deep, cold water or
        moonlit stone.

        The mist in Kittelsen\'s landscapes is not a simple haze-tint: it is a
        zone of the image where colour and variance collapse together -- the
        smooth, even tonality of fog or mist contrasted with the texture-rich
        foreground. His atmospheric zones have simultaneously high luminance
        (the mist scatters light, brightening the zone) and LOW LOCAL VARIANCE
        (the mist suppresses texture, creating the smooth, featureless quality
        of looking through fog). This joint characteristic is what this pass
        detects: not position (near/far determined by vertical coordinate) but
        CONTENT (near/far determined by the joint luminance-variance signature).

        Stage 1 CONTENT-ADAPTIVE FAR ZONE DETECTION: Compute local luminance
        variance via var[y,x] = gaussian(L^2, variance_sigma) - gaussian(L, variance_sigma)^2.
        Detect FAR/MIST ZONES as pixels satisfying:
          (a) L[y,x] in [far_lum_low, far_lum_high] -- bright enough for
              atmospheric haze, not a direct highlight reflection
          (b) local_var[y,x] <= var_threshold (35th percentile of nonzero var) --
              smooth enough to be a mist or sky zone, not a textured near surface
        NOVEL: (a) JOINT LUMINANCE-RANGE AND LOCAL VARIANCE FAR ZONE DETECTION --
        paint_aerial_perspective_pass (s244) uses blur-difference (coarse vs fine
        blur) as a depth proxy; paint_atmospheric_recession_pass (s259) uses a
        positional gradient (top/bottom/left/right direction fraction); paint_depth_
        atmosphere_pass (s268) uses vertical position weighted with local contrast;
        no prior paint_ improvement pass detects the atmospheric zone using the
        JOINT CONDITION of luminance range AND low local variance, which is the
        correct physical signature of a mist or sky region regardless of its
        position in the image -- a fog bank can appear anywhere in the frame,
        and it is identified by its smoothness AND its brightness, not by its
        position.

        Stage 2 ATMOSPHERIC HAZE TINT IN FAR ZONES: In detected far zones, blend
        the canvas toward haze_color = (haze_r, haze_g, haze_b) (a cool Prussian
        blue-grey) at strength haze_strength * (1 + brightness_weight * 0.5),
        where brightness_weight = (L - far_lum_low) / (far_lum_high - far_lum_low).
        The haze tint is stronger in brighter far-zone pixels, simulating the
        physics of light scattering through the atmosphere: at greater distances,
        the atmospheric column is longer and the haze effect more pronounced,
        which also makes the image progressively lighter. Outside the far zone,
        no tinting is applied.
        NOVEL: (b) LUMINANCE-MODULATED HAZE TINT GATED TO VARIANCE-DETECTED
        FAR ZONE -- prior aerial perspective passes apply haze globally with a
        directional or blur-difference gradient; this pass gates the haze tint
        strictly to the variance-detected mist/sky zone and further modulates
        the tint strength by luminance within that zone, implementing the
        Kittelsen sky gradient (maximum haze near the horizon where the sky
        is brightest, minimum haze at the dark zenith).

        Stage 3 SILHOUETTE EDGE CONTRAST HARDENING: Compute the GRADIENT
        MAGNITUDE of the far_zone mask after smoothing (sigma=2): this gives
        a map of where the near/far boundary lies. At these boundary pixels,
        apply a BIDIRECTIONAL CONTRAST BOOST:
          -- On the NEAR side of the boundary (dark silhouette side):
             darken by silhouette_contrast * 0.8 * gradient_magnitude
          -- On the FAR side of the boundary (mist/sky side):
             lighten slightly by silhouette_contrast * 0.2 * gradient_magnitude
        This recreates Kittelsen\'s razor-sharp black silhouettes of birch trees,
        trolls, and rocky outcrops standing in front of luminous sky or mist.
        NOVEL: (c) ZONE-MASK-GRADIENT SILHOUETTE CONTRAST HARDENER -- no prior
        pass derives a boundary gradient from a CONTENT-ADAPTIVE zone mask (not
        a structural edge detector on pixel values, but a gradient of the detected
        atmospheric zone) and uses it for BIDIRECTIONAL contrast enhancement
        (simultaneous darkening of near side and lightening of far side at the
        zone boundary); paint_sfumato_contour_dissolution_pass and related passes
        SOFTEN edges; this pass HARDENS them at the near/far boundary; the
        content-adaptive zone mask source makes the silhouette detection respond
        to the actual atmospheric topology of the image.

        Stage 4 DEEP SHADOW BLUE-VIOLET UNDERLAYER: Detect deep shadow pixels
        (L < dark_threshold) and blend them toward dark_violet_color =
        (dark_violet_r, dark_violet_g, dark_violet_b) -- a Prussian blue-violet.
        The blend strength is proportional to how far below dark_threshold the
        pixel is: shadow_depth = clip((dark_threshold - L) / dark_threshold, 0, 1),
        with inject amount = dark_strength * shadow_depth. This pulls dark forest
        interiors, peat bog surfaces, and deep shadow zones away from neutral
        black and into Kittelsen\'s characteristic deep cold blue-violet.
        NOVEL: (d) LUMINANCE-GATED BLUE-VIOLET DARK ZONE UNDERLAYER -- paint_
        chromatic_underdark_pass (s250) shifts shadow hue via HSV hue rotation
        using a preset dark_hue angle; this pass directly blends the shadow zone
        toward a specific RGB target color (prussian blue-violet) with a depth-
        proportional strength -- the implementation difference is direct RGB target
        blending (vs HSV rotation) and the dark zone is detected by a hard
        luminance threshold rather than a soft ramp (different from underdark\'s
        soft fade); the target colour (prussian blue-violet) is Kittelsen-specific
        and distinct from the underdark hue parameter.
        """
        print("    Kittelsen Nordic Mist (Atmospheric Twilight Landscape) pass (session 271, 182nd mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, sobel as _sobel

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Content-Adaptive Far Zone Detection ──────────────────────
        vs   = max(float(variance_sigma), 0.5)
        lum2 = (lum ** 2).astype(_np.float32)
        lm   = _gf(lum,  sigma=vs).astype(_np.float32)
        lm2  = _gf(lum2, sigma=vs).astype(_np.float32)
        local_var = _np.clip(lm2 - lm ** 2, 0.0, None).astype(_np.float32)

        nz_var = local_var[local_var > 1e-6]
        var_thr = float(_np.percentile(nz_var, 35)) if len(nz_var) > 0 else 0.006

        fll = float(far_lum_low)
        flh = float(far_lum_high)
        far_zone = (
            (lum >= fll) & (lum <= flh) & (local_var <= var_thr)
        ).astype(_np.float32)

        # ── Stage 2: Atmospheric Haze Tint ────────────────────────────────────
        hs   = float(haze_strength)
        hr   = float(haze_r)
        hg   = float(haze_g)
        hb   = float(haze_b)

        # Luminance-modulated blend strength within far zone
        lum_weight = _np.clip((lum - fll) / (flh - fll + 1e-6), 0.0, 1.0).astype(_np.float32)
        haze_blend = _np.clip(far_zone * hs * (1.0 + lum_weight * 0.5), 0.0, 1.0).astype(_np.float32)

        tint_r = _np.clip(r0 + (hr - r0) * haze_blend, 0.0, 1.0).astype(_np.float32)
        tint_g = _np.clip(g0 + (hg - g0) * haze_blend, 0.0, 1.0).astype(_np.float32)
        tint_b = _np.clip(b0 + (hb - b0) * haze_blend, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Silhouette Edge Contrast Hardening ───────────────────────
        fz_smooth = _gf(far_zone, sigma=2.0).astype(_np.float32)
        gy = _sobel(fz_smooth.astype(_np.float64), axis=0).astype(_np.float32)
        gx = _sobel(fz_smooth.astype(_np.float64), axis=1).astype(_np.float32)
        grad_mag = _np.sqrt(gy ** 2 + gx ** 2).astype(_np.float32)
        gmax = float(grad_mag.max())
        grad_norm = (grad_mag / (gmax + 1e-8)).astype(_np.float32)

        sc = float(silhouette_contrast)
        near_zone  = (1.0 - far_zone).astype(_np.float32)
        sil_dark   = (grad_norm * near_zone).astype(_np.float32)
        sil_light  = (grad_norm * far_zone).astype(_np.float32)

        cont_r = _np.clip(tint_r - sil_dark * sc * 0.80 + sil_light * sc * 0.20, 0.0, 1.0).astype(_np.float32)
        cont_g = _np.clip(tint_g - sil_dark * sc * 0.80 + sil_light * sc * 0.20, 0.0, 1.0).astype(_np.float32)
        cont_b = _np.clip(tint_b - sil_dark * sc * 0.70 + sil_light * sc * 0.20, 0.0, 1.0).astype(_np.float32)

        # ── Stage 4: Deep Shadow Blue-Violet Underlayer ───────────────────────
        dt   = float(dark_threshold)
        dstr = float(dark_strength)
        dvr  = float(dark_violet_r)
        dvg  = float(dark_violet_g)
        dvb  = float(dark_violet_b)

        shadow_depth = _np.clip((dt - lum) / (dt + 1e-6), 0.0, 1.0).astype(_np.float32)
        dark_inject  = _np.clip(shadow_depth * dstr, 0.0, 1.0).astype(_np.float32)

        dark_r = _np.clip(cont_r + (dvr - cont_r) * dark_inject, 0.0, 1.0).astype(_np.float32)
        dark_g = _np.clip(cont_g + (dvg - cont_g) * dark_inject, 0.0, 1.0).astype(_np.float32)
        dark_b = _np.clip(cont_b + (dvb - cont_b) * dark_inject, 0.0, 1.0).astype(_np.float32)

        # ── Composite with master opacity ─────────────────────────────────────
        op    = float(opacity)
        out_r = _np.clip(r0 + (dark_r - r0) * op, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 + (dark_g - g0) * op, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 + (dark_b - b0) * op, 0.0, 1.0).astype(_np.float32)

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

if "paint_reflected_light_pass" in src:
    print("paint_reflected_light_pass already in stroke_engine.py -- skipping.")
else:
    INSERT_BEFORE = "    def gorky_biomorphic_fluid_pass("
    idx = src.find(INSERT_BEFORE)
    if idx == -1:
        print("ERROR: could not find gorky_biomorphic_fluid_pass insertion point.")
        sys.exit(1)
    new_src = src[:idx] + REFLECTED_LIGHT_PASS + src[idx:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src)
    print("Inserted paint_reflected_light_pass into stroke_engine.py.")
    src = new_src

if "kittelsen_nordic_mist_pass" in src:
    print("kittelsen_nordic_mist_pass already in stroke_engine.py -- skipping.")
else:
    INSERT_BEFORE2 = "    def gorky_biomorphic_fluid_pass("
    idx2 = src.find(INSERT_BEFORE2)
    if idx2 == -1:
        print("ERROR: could not find second insertion point.")
        sys.exit(1)
    new_src2 = src[:idx2] + KITTELSEN_NORDIC_MIST_PASS + src[idx2:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src2)
    print("Inserted kittelsen_nordic_mist_pass into stroke_engine.py.")
