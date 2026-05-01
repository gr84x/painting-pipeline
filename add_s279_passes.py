"""Insert paint_surface_grain_pass (s279 improvement) and
blake_visionary_radiance_pass (190th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_surface_grain_pass (s279 improvement) ──────────────────────

SURFACE_GRAIN_PASS = '''
    def paint_surface_grain_pass(
        self,
        grain_strength:     float = 0.06,
        coverage_radius:    int   = 4,
        coverage_boost:     float = 3.0,
        linen_r:            float = 0.78,
        linen_g:            float = 0.68,
        linen_b:            float = 0.52,
        grain_sigma_fine:   float = 0.8,
        grain_sigma_coarse: float = 2.2,
        seed:               int   = 279,
        opacity:            float = 1.0,
    ) -> None:
        r"""Surface Grain -- session 279 improvement.

        BAND-PASS CANVAS GRAIN SIMULATION WITH COVERAGE-WEIGHTED LINEN TINTING:

        Real oil paintings on linen canvas show fine grain texture wherever the
        paint is applied thinly -- shadow zones, glazed passages, early-layer
        underpainting visible through later strokes.  In thick impasto areas the
        paint fully buries the weave; in thin areas the linen texture reads
        through as a fine warm grain.  Academic painters exploited this:
        Turner left bare, barely-tinted canvas in sky passages so the linen
        grain provided a ready-made sky texture; Constable built cloud lights
        from the linen ground in thin scumbles.  This pass simulates that
        physical effect: it estimates where the paint is thin (low local
        variance == quiet, flat zones) and introduces a fine band-pass grain
        texture there, tinted toward the warm cream of raw linen.

        Stage 1 BAND-PASS GRAIN GENERATION:
        Generate a base random noise field N(0,1). Blur it at two scales:
          smooth_fine   = GaussianFilter(N, sigma=grain_sigma_fine)
          smooth_coarse = GaussianFilter(N, sigma=grain_sigma_coarse)
        The band-pass grain is the DIFFERENCE:
          grain = smooth_fine - smooth_coarse
        This retains only the spatial frequencies between grain_sigma_fine and
        grain_sigma_coarse, eliminating both the highest-frequency single-pixel
        noise (not physically realistic for woven linen) and the very low-
        frequency tonal variations (which belong to the painting, not the grain).
        Normalize by the standard deviation of the grain field so that
        grain_strength is the actual RMS amplitude.
        NOVEL: (a) BAND-PASS GRAIN VIA GAUSSIAN DIFFERENCE -- all prior noise-
        based passes in this codebase use raw noise or a single-scale Gaussian
        blur. This pass generates noise through a difference-of-Gaussians (DoG)
        filter, which is band-limited: it has a specific peak spatial frequency
        (approximately 1 / grain_sigma_coarse cycles per pixel) rather than a
        flat spectrum. The DoG band-pass matches the approximately narrow-band
        spectral structure of real woven linen (the weave creates a periodic
        structure with a characteristic spatial period, not white noise).

        Stage 2 PAINT COVERAGE ESTIMATION VIA LOCAL LUMINANCE VARIANCE:
        Estimate where paint is thick vs thin using LOCAL LUMINANCE VARIANCE:
          L_var = UniformFilter(L^2, r) - UniformFilter(L, r)^2
          coverage = clip(sqrt(L_var) * coverage_boost, 0, 1)
        where r = coverage_radius. High local variance indicates active paint
        with visible brushstrokes and color transitions -- thick coverage that
        buries the canvas grain. Low local variance indicates flat smooth areas
        (shadows, midtone grounds) where the paint is thin.
        grain_weight = 1 - coverage
        NOVEL: (b) LOCAL LUMINANCE VARIANCE AS PAINT-THICKNESS PROXY -- prior
        coverage-aware passes use fixed luminance thresholds or global metrics.
        This pass computes LOCAL variance at the pixel level via the UniformFilter
        identity Var[X] = E[X^2] - E[X]^2, which gives a continuous, spatially
        resolved estimate of paint activity per pixel. Using luminance variance
        prevents the metric from being confused by saturated color areas that
        happen to be tonally uniform. This is the first pass to use spatial
        luminance variance as a per-pixel weight.

        Stage 3 WARM LINEN GRAIN TINTING:
        Rather than simply adding the grain as a luminance perturbation, this
        pass applies it as a COLOR PULL TOWARD THE LINEN CANVAS COLOR:
          grain_app = grain * grain_weight   (scaled by thinness)
          R_out = R + (linen_r - R) * |grain_app|
          G_out = G + (linen_g - G) * |grain_app|
          B_out = B + (linen_b - B) * |grain_app|
        The grain shifts each pixel toward the linen color in proportion to the
        absolute grain amplitude. The shift is always TOWARD linen (not away) --
        there is no darkening, only brightening and warming toward the canvas
        base color. This is physically accurate: the canvas grain appears as
        slightly brighter and warmer than the paint layer above it (bare canvas
        showing through).
        NOVEL: (c) GRAIN AS COLOR PULL TOWARD A PHYSICALLY-MOTIVATED BASE
        SURFACE COLOR -- prior texture passes apply brightness or hue shifts.
        This pass applies grain as a directional color pull toward a specific
        physical color (linen canvas), meaning in dark areas the grain brightens
        (canvas shows through dark paint) and in light areas the grain has
        minimal effect (light paint is close to linen color anyway). This
        correctly models the asymmetric behavior of canvas grain in real
        paintings.
        """
        print("    Surface Grain pass (session 279 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, uniform_filter as _uf

        canvas = self.canvas
        H, W = canvas.h, canvas.w
        rng = _np.random.default_rng(int(seed))

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)

        # Stage 1: Band-pass grain generation (difference of Gaussians)
        noise_base = rng.standard_normal((H, W)).astype(_np.float32)
        gf = max(float(grain_sigma_fine),   0.3)
        gc = max(float(grain_sigma_coarse), gf + 0.5)
        smooth_fine   = _gf(noise_base, sigma=gf).astype(_np.float32)
        smooth_coarse = _gf(noise_base, sigma=gc).astype(_np.float32)
        grain = (smooth_fine - smooth_coarse).astype(_np.float32)
        grain_std = max(float(grain.std()), 1e-6)
        grain = (grain / grain_std * float(grain_strength)).astype(_np.float32)

        # Stage 2: Paint coverage estimation via local luminance variance
        cr = max(int(coverage_radius), 2)
        fsize = 2 * cr + 1
        L_mean  = _uf(L,     size=fsize).astype(_np.float32)
        L2_mean = _uf(L * L, size=fsize).astype(_np.float32)
        L_var   = _np.maximum(L2_mean - L_mean ** 2, 0.0).astype(_np.float32)
        L_std_local = _np.sqrt(L_var).astype(_np.float32)
        cb = max(float(coverage_boost), 0.1)
        coverage     = _np.clip(L_std_local * cb, 0.0, 1.0).astype(_np.float32)
        grain_weight = (1.0 - coverage).astype(_np.float32)
        grain_app    = (grain * grain_weight).astype(_np.float32)

        # Stage 3: Warm linen grain tinting (pull toward canvas color)
        pull  = _np.abs(grain_app).astype(_np.float32)
        R2 = _np.clip(R + (float(linen_r) - R) * pull, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G + (float(linen_g) - G) * pull, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B + (float(linen_b) - B) * pull, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R2 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G2 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B2 - B) * op, 0.0, 1.0).astype(_np.float32)

        grain_active = int((grain_weight > 0.5).sum())
        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Surface Grain complete (grain_active_px={grain_active})")

'''

# ── Pass 2: blake_visionary_radiance_pass (190th mode) ───────────────────────

BLAKE_VISIONARY_PASS = '''
    def blake_visionary_radiance_pass(
        self,
        n_rings:           int   = 8,
        ring_strength:     float = 0.08,
        ring_smooth_sigma: float = 12.0,
        gold_threshold:    float = 0.52,
        gold_strength:     float = 0.36,
        gold_r:            float = 0.88,
        gold_g:            float = 0.72,
        gold_b:            float = 0.14,
        contour_strength:  float = 0.30,
        contour_threshold: float = 0.045,
        ultra_threshold:   float = 0.38,
        ultra_strength:    float = 0.32,
        ultra_r:           float = 0.10,
        ultra_g:           float = 0.15,
        ultra_b:           float = 0.48,
        opacity:           float = 0.88,
    ) -> None:
        r"""Blake Visionary Radiance (British Romanticism / Visionary Art) -- 190th mode.

        WILLIAM BLAKE (1757-1827) -- BRITISH ROMANTIC POET, PAINTER, AND
        PRINTMAKER; PROPHET OF VISIONARY LIGHT AND DIVINE CONTOUR:

        William Blake was born in Soho, London, the son of a hosier, and from
        childhood reported visionary experiences -- seeing angels in a tree on
        Peckham Rye, the face of God at the upstairs window.  He trained as an
        engraver under James Basire, learning to cut precise lines into copper,
        and at the Royal Academy briefly, before abandoning academic training
        to develop an entirely personal aesthetic.  He invented RELIEF ETCHING,
        a technique of writing and drawing directly onto copper plates with acid-
        resistant medium and then etching away the background -- producing his
        ILLUMINATED BOOKS (Songs of Innocence, Songs of Experience, Jerusalem,
        The Marriage of Heaven and Hell), each copy hand-colored in watercolor
        and tempera by himself and his wife Catherine.  His paintings in tempera
        and watercolor -- "The Ancient of Days," "Newton," "Elohim Creating Adam,"
        "The Ghost of a Flea," "Pity," "Hecate" -- are among the most singular
        images in British art: intense, hallucinatory, executed in a technique he
        called "fresco" (actually a distemper of carpenter's glue and pigment
        on wood), combining the precision of engraving with the color of painting.

        THE WIRY BOUNDING LINE -- BLAKE\'S FUNDAMENTAL DOCTRINE:
        Blake\'s central aesthetic principle was the supremacy of the BOUNDING
        LINE -- the crisp, definite outline that separates one form from another.
        "The more distinct, sharp, and wiry the bounding line, the more perfect
        the work of art; and the less keen and sharp, the greater is the evidence
        of weak imitation, plagiarism, and bungling." He attacked the sfumato of
        Rembrandt and the atmospheric vagueness of Reynolds: "Blots and blurs are
        not art; we know them in bad engravers." Each form in a Blake painting is
        enclosed by a dark, precise line -- the boundary between the spiritual
        and material worlds made visible.  In his shadows this line darkens: the
        dark side of a form has a pronounced dark edge, separating the lit surface
        from the deep shadow beneath.

        DIVINE RADIANCE AND THE CORONA OF CELESTIAL LIGHT:
        Blake\'s theology of light is specific: God and the divine emit a radiant
        emanation that does not merely illuminate but TRANSFORMS the surfaces it
        touches.  In "The Ancient of Days," the divine figure is surrounded by
        concentric halos of golden light; in "Job" the Lord appears in a vortex
        of radiant cloud; in "Jerusalem," figures emit concentric rings of blue
        and gold.  This divine radiance manifests in his paintings as concentric
        ring structures around bright sources -- not simple halos but MULTIPLE
        CONCENTRIC BANDS of alternating light and slight shadow, like the
        interference rings of a heavenly vibration propagating outward from
        its divine source.

        GOLD AND ULTRAMARINE -- THE CELESTIAL PALETTE:
        Blake\'s colors are organized by a theology of light: gold and warm
        flame are the colors of divine creative fire; deep ultramarine is the
        color of spiritual depth and the void out of which creation emerges.
        In practice this means his brights are intensely warm (golden vermilion
        for divine fire, pale gold for celestial light) and his darks are
        deeply blue (ultramarine, Prussian blue for spiritual shadow).
        Between these poles: flesh, earth, and neutral tones receive warmer
        treatment in light and cooler in shadow -- a strong warm-cool duality
        that structures every composition.

        Stage 1 ISO-LUMINANCE RING MODULATION (Divine Radiance Corona):
        Compute luminance L. Apply large-sigma Gaussian blur: L_smooth =
        GaussianFilter(L, sigma=ring_smooth_sigma). This smoothed field
        defines the large-scale luminance topology -- the hills and valleys
        of the painting\'s tonal structure.  Generate a RING FIELD using
        L_smooth as the phase variable of a sinusoidal modulation:
          R_rings = ring_strength * sin(2 * pi * L_smooth * n_rings)
        This creates concentric bands of light and shadow that follow the
        iso-luminance contours of the smoothed field.  Where L_smooth is
        high (bright celestial zone), the rings are dense (high spatial
        rate of change per unit of L); where L_smooth is low (dark void),
        they are absent.  Apply additively to all channels equally.
        NOVEL: (a) ISO-LUMINANCE RING MODULATION VIA SINUSOIDAL PHASE
        -- prior passes apply Gaussian blurs (focal_vignette, bloom),
        linear tonal shifts (goya sigmoid), or threshold zones. This pass
        uses the painting\'s OWN smooth luminance field as the PHASE ANGLE
        of a sinusoidal function, generating a ring pattern whose spatial
        period is inversely proportional to local luminance gradient. In
        bright zones the rings are densely spaced (high luminance gradient
        -> rapid phase change); in dark zones they are absent (no phase
        variation). This is the first pass to apply a periodic modulation
        keyed to the local value of the luminance field rather than position.

        Stage 2 WARM GOLD CELESTIAL TINTING (Divine Fire in Bright Zones):
        Compute the soft bright-zone weight:
          w_gold = clip((L_smooth - gold_threshold) / (1 - gold_threshold + eps), 0, 1)^0.7
        Blend bright zones toward celestial gold (gold_r, gold_g, gold_b):
          R_g = R + (gold_r - R) * w_gold * gold_strength
          (similar for G, B)
        Using L_smooth rather than raw L ensures the tinting has soft edges
        matching the large-scale luminance structure rather than sharp
        pixel-by-pixel transitions. The result is that bright focal zones
        glow gold while transition zones receive fractional tinting.
        NOVEL: (b) SMOOTH-LUMINANCE-GATED GOLD CELESTIAL TINTING -- prior
        warm color shifts gate on raw pixel luminance (shadow umber trace,
        warm center of focal vignette) or on saturation (complementary
        shadow). This stage gates on SPATIALLY SMOOTHED LUMINANCE, which
        produces a larger, softer target zone than raw-luminance gating.
        Smooth-luminance gating targets LARGE-SCALE bright areas (the sky
        zone, the central glow) rather than individual bright pixels. The
        celestial gold is a specific warm-yellow target color distinct from
        all prior warm pushes (amber, sepia, ochre); this is the first pass
        to use this particular gold as the warm-zone target.

        Stage 3 DARK CONTOUR REINFORCEMENT (Wiry Bounding Line):
        Compute Sobel gradient magnitude Gmag and direction (gx, gy).
        Normalize the gradient direction to a unit vector (nx, ny).
        For pixels where Gmag > contour_threshold * Gmag_99:
          Step one pixel in the DARK DIRECTION (opposite to gradient):
            xd = x - nx, yd = y - ny
          If valid: darken pixel (xd, yd) by contour_strength:
            C[yd, xd] *= (1 - contour_strength * edge_weight)
          where edge_weight = clip(Gnorm, 0, 1) (normalized gradient).
        This darkens the SHADOW SIDE of each tonal boundary -- the side
        away from which luminance increases. The result is a dark line on
        the shadow face of each form-edge, like Blake\'s inked outlines
        which are always darkest on the shadow side of a contour.
        NOVEL: (c) ASYMMETRIC SHADOW-SIDE CONTOUR DARKENING via GRADIENT
        DIRECTION OFFSET -- prior edge-related passes apply symmetric
        operations to detected edge pixels (iso-contour threading places
        lines on edge pixels; edge_recession_pass applies recession to
        edge zones). This pass uses the gradient DIRECTION to identify the
        DARK SIDE of each edge and specifically darkens a displaced pixel
        in that direction -- creating asymmetric contour lines that appear
        only on the shadow face, not the lit face, of each boundary.

        Stage 4 DEEP SHADOW ULTRAMARINE INFUSION (Blake\'s Spiritual Void):
        In shadow zones defined by L_smooth < ultra_threshold:
          w_ultra = clip((ultra_threshold - L_smooth) / ultra_threshold, 0, 1)^0.6
        Blend toward deep ultramarine (ultra_r, ultra_g, ultra_b):
          R_u = R + (ultra_r - R) * w_ultra * ultra_strength
          (similar for G, B)
        This shifts dark regions toward Blake\'s characteristic spiritual blue
        -- the deep ultramarine of spiritual depth and divine void.
        NOVEL: (d) SMOOTH-LUMINANCE-GATED ULTRAMARINE SHADOW INFUSION --
        prior shadow-zone passes use warm colors: goya umber trace (warm
        sepia in shadows), reflected_light_pass (warm reflected ground in
        shadow), complementary_shadow (hue complement). This is the first
        pass to push shadow zones toward a COOL, SPECIFIC BLUE (ultramarine)
        rather than a warm shift or a luminance-only change. The use of
        L_smooth for gating (same as gold stage) creates a soft, spatially
        coherent shadow infusion rather than a sharp threshold step.
        Combined with the gold tinting of Stage 2, the result is a strong
        warm-cool contrast structure: bright zones gold, dark zones
        ultramarine -- Blake\'s celestial palette.
        """
        print("    Blake Visionary Radiance pass (190th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, sobel as _sobel

        canvas = self.canvas
        H, W = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)

        # Compute smooth luminance field for all stages
        rs = max(float(ring_smooth_sigma), 2.0)
        L_smooth = _gf(L, sigma=rs).astype(_np.float32)

        # Stage 1: Iso-luminance ring modulation
        nr = max(int(n_rings), 1)
        rs2 = float(ring_strength)
        rings = (rs2 * _np.sin(2.0 * _np.pi * L_smooth * nr)).astype(_np.float32)
        R1 = _np.clip(R + rings, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + rings, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + rings, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Warm gold celestial tinting (bright zones)
        gt = max(float(gold_threshold), 0.1)
        eps = 1e-6
        w_gold = _np.clip((L_smooth - gt) / (1.0 - gt + eps), 0.0, 1.0) ** 0.7
        w_gold = (w_gold * float(gold_strength)).astype(_np.float32)
        R2 = _np.clip(R1 + (float(gold_r) - R1) * w_gold, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (float(gold_g) - G1) * w_gold, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (float(gold_b) - B1) * w_gold, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Dark contour reinforcement (wiry bounding line)
        Gx = _sobel(L.astype(_np.float64), axis=1).astype(_np.float32)
        Gy = _sobel(L.astype(_np.float64), axis=0).astype(_np.float32)
        Gmag = _np.sqrt(Gx * Gx + Gy * Gy).astype(_np.float32)
        g99 = max(float(_np.percentile(Gmag, 99)), 1e-6)
        Gnorm = (Gmag / g99).astype(_np.float32)

        ct = float(contour_threshold)
        cs = float(contour_strength)
        # Gradient unit direction (normalized)
        Gmag_safe = _np.maximum(Gmag, 1e-6)
        nx_dir = (Gx / Gmag_safe).astype(_np.float32)
        ny_dir = (Gy / Gmag_safe).astype(_np.float32)

        edge_pixels = (Gnorm > ct)
        ys_e, xs_e = _np.where(edge_pixels)
        # Dark side: one step in the -gradient direction
        xd = _np.clip((xs_e - nx_dir[ys_e, xs_e]).round().astype(int), 0, W - 1)
        yd = _np.clip((ys_e - ny_dir[ys_e, xs_e]).round().astype(int), 0, H - 1)
        edge_wt = _np.clip(Gnorm[ys_e, xs_e], 0.0, 1.0)
        darken = (1.0 - cs * edge_wt).astype(_np.float32)
        R3 = R2.copy()
        G3 = G2.copy()
        B3 = B2.copy()
        _np.minimum.at(R3, (yd, xd), darken * R2[yd, xd] / _np.maximum(R2[yd, xd], 1e-6) * R2[yd, xd])
        # Use direct assignment to darken shadow-side pixels
        R3[yd, xd] = _np.clip(R2[yd, xd] * darken, 0.0, 1.0)
        G3[yd, xd] = _np.clip(G2[yd, xd] * darken, 0.0, 1.0)
        B3[yd, xd] = _np.clip(B2[yd, xd] * darken, 0.0, 1.0)

        # Stage 4: Deep shadow ultramarine infusion (spiritual void)
        ut = max(float(ultra_threshold), 0.1)
        us = float(ultra_strength)
        w_ultra = _np.clip((ut - L_smooth) / (ut + 1e-6), 0.0, 1.0) ** 0.6
        w_ultra = (w_ultra * us).astype(_np.float32)
        R4 = _np.clip(R3 + (float(ultra_r) - R3) * w_ultra, 0.0, 1.0).astype(_np.float32)
        G4 = _np.clip(G3 + (float(ultra_g) - G3) * w_ultra, 0.0, 1.0).astype(_np.float32)
        B4 = _np.clip(B3 + (float(ultra_b) - B3) * w_ultra, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R4 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G4 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B4 - B) * op, 0.0, 1.0).astype(_np.float32)

        n_edge = int(edge_pixels.sum())
        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Blake Visionary Radiance complete (n_edge={n_edge})")

'''

# ── Inject both passes into stroke_engine.py ─────────────────────────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

ANCHOR = "    def toorop_symbolist_line_pass("
assert ANCHOR in src, f"Anchor not found in stroke_engine.py: {ANCHOR!r}"

INSERTION = SURFACE_GRAIN_PASS + BLAKE_VISIONARY_PASS
new_src = src.replace(ANCHOR, INSERTION + ANCHOR, 1)

with open(SE_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("stroke_engine.py patched: paint_surface_grain_pass (s279 improvement)"
      " + blake_visionary_radiance_pass (190th mode) inserted before"
      " toorop_symbolist_line_pass.")
