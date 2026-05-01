"""Insert paint_halation_bloom_pass (s277 improvement) and
goya_black_vision_pass (188th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_halation_bloom_pass (s277 improvement) ─────────────────────

HALATION_BLOOM_PASS = '''
    def paint_halation_bloom_pass(
        self,
        bloom_threshold: float = 0.80,
        bloom_sigma:     float = 18.0,
        warm_r_boost:    float = 0.08,
        warm_b_cut:      float = 0.04,
        bloom_opacity:   float = 0.35,
        opacity:         float = 1.0,
    ) -> None:
        r"""Halation Bloom -- session 277 improvement.

        SIMULATION OF OPTICAL BLOOM AND HALATION -- THE BLEEDING OF INTENSE
        LIGHT SOURCES INTO SURROUNDING AREAS -- AS SEEN IN PHOTOGRAPHY, HUMAN
        VISION, AND OLD MASTER GLAZED PAINTINGS:

        In the physical world, very bright light sources bleed into adjacent
        areas through two mechanisms: (1) OPTICAL HALATION in film/glass, where
        light reflects from the film substrate and re-exposes adjacent silver
        grains, creating a soft glow around overexposed highlights; (2) LIGHT
        SCATTER in the human eye and in dense oil-painting glazes, where intense
        luminance in one region generates a soft corona of light in adjacent zones.
        In Old Master paintings, thick layers of resinous oil medium around
        highlight passages create a natural halation effect: the medium scatters
        and refracts highlight light into the surrounding glaze, producing the
        characteristic "inner glow" of Rembrandt's highlights and Vermeer's
        window panes. Goya's final paintings -- especially the Quinta del Sordo
        murals -- use thick white impasto in isolated highlights that appear to
        glow against the dark ground precisely because of this halation effect
        in the paint medium.

        Stage 1 BRIGHT SOURCE EXTRACTION:
        Compute luminance L = 0.299R + 0.587G + 0.114B. Extract pixels where
        L > bloom_threshold as light sources. All other pixels contribute zero
        to the bloom layer. This isolates genuinely bright zones (specular
        highlights, bright sky areas, lit surfaces) from midtones and shadows.
        NOVEL: (a) LUMINANCE-THRESHOLDED SOURCE ISOLATION -- prior glow/bloom
        passes (e.g. translucency_bloom) apply bloom to the whole image or to
        saturation zones; this pass isolates ONLY the brightest pixels as bloom
        sources and zeroes all other pixels in the bloom layer, creating precise
        luminance-gated halos.

        Stage 2 PRE-BLOOM WARM TINT APPLICATION:
        Apply a warm color shift to the extracted bright sources before blurring:
          source_R += warm_r_boost * source_mask
          source_B -= warm_b_cut   * source_mask
        This makes the bloom carry warmth rather than matching the source color
        neutrally, simulating the warm scatter of tungsten/candlelight and the
        yellow-amber tint of aged oil medium.
        NOVEL: (b) PRE-DIFFUSION COLOR TRANSFORM ON ISOLATED SOURCES -- the warm
        tint is applied BEFORE blurring, so the resulting bloom halo inherits a
        warm character that is distinct from the source color. Prior passes that
        add color after blurring (or blend uniformly warm tints) cannot produce
        a bloom whose color character differs from the underlying source.

        Stage 3 GAUSSIAN BLOOM DIFFUSION:
        Apply Gaussian blur at bloom_sigma (default 18 px) to each warm-tinted
        source channel independently. This creates a broad, soft glow that extends
        well beyond the original source boundaries -- the characteristic halation
        corona.

        Stage 4 ADDITIVE COMPOSITING:
        Blend the bloom onto the original image ADDITIVELY:
          R_out = clip(R_orig + bloom_R * bloom_opacity, 0, 1)
          G_out = clip(G_orig + bloom_G * bloom_opacity, 0, 1)
          B_out = clip(B_orig + bloom_B * bloom_opacity, 0, 1)
        Additive compositing correctly simulates light addition (bright areas
        receive more total light, appearing more luminous) rather than color
        replacement. The final opacity parameter scales the strength of the
        additive application.
        NOVEL: (c) ADDITIVE (NOT ALPHA) COMPOSITING OF BLOOM LAYER -- all prior
        Painter passes use alpha-blending: out = orig*(1-op) + mod*op. This pass
        uses ADDITIVE compositing: out = clip(orig + bloom*opacity, 0, 1). Additive
        compositing is the correct physical model for bloom/halation (light
        accumulates; it does not replace prior light) and is the first additive
        compositing operation in this codebase. The clip to [0,1] creates the
        characteristic "bloom clipping" of overexposed film.
        """
        print("    Halation Bloom pass (session 277 improvement)...")

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

        # Stage 1: extract bright sources
        source_mask = (L > bloom_threshold).astype(_np.float32)
        src_R = R * source_mask
        src_G = G * source_mask
        src_B = B * source_mask

        # Stage 2: pre-bloom warm tint
        wr = float(warm_r_boost)
        wb = float(warm_b_cut)
        src_R = _np.clip(src_R + wr * source_mask, 0.0, 1.0)
        src_B = _np.clip(src_B - wb * source_mask, 0.0, 1.0)

        # Stage 3: Gaussian bloom diffusion
        sig = max(float(bloom_sigma), 0.5)
        bloom_R = _gf(src_R, sigma=sig).astype(_np.float32)
        bloom_G = _gf(src_G, sigma=sig).astype(_np.float32)
        bloom_B = _gf(src_B, sigma=sig).astype(_np.float32)

        # Stage 4: additive compositing
        bo = float(bloom_opacity)
        op = float(opacity)
        R_out = _np.clip(R + bloom_R * bo * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + bloom_G * bo * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + bloom_B * bo * op, 0.0, 1.0).astype(_np.float32)

        n_sources = int(source_mask.sum())
        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Halation Bloom complete (n_sources={n_sources}, sigma={sig:.1f})")

'''

# ── Pass 2: goya_black_vision_pass (188th mode) ───────────────────────────────

GOYA_BLACK_VISION_PASS = '''
    def goya_black_vision_pass(
        self,
        ground_r:            float = 0.26,
        ground_g:            float = 0.19,
        ground_b:            float = 0.11,
        ground_strength:     float = 0.38,
        sigmoid_midpoint:    float = 0.42,
        sigmoid_steepness:   float = 5.5,
        tonal_min:           float = 0.00,
        tonal_max:           float = 1.02,
        desaturate_thresh:   float = 0.50,
        desaturate_strength: float = 0.42,
        umber_r:             float = 0.28,
        umber_g:             float = 0.18,
        umber_b:             float = 0.10,
        umber_blend:         float = 0.35,
        grad_low:            float = 0.04,
        grad_high:           float = 0.48,
        noise_sigma:         float = 2.8,
        noise_strength:      float = 0.032,
        seed:                int   = 277,
        opacity:             float = 0.78,
    ) -> None:
        r"""Goya Black Vision (Dark Romanticism / Black Paintings) -- 188th mode.

        FRANCISCO DE GOYA (1746-1828) -- SPANISH COURT PAINTER TURNED DARK
        ROMANTIC VISIONARY, PRECURSOR OF EXPRESSIONISM AND MODERN ART:

        Goya began his career as a successful rococo decorative painter (tapestry
        cartoons for the Royal Manufactory, 1775-1792) before illness in 1792-93
        left him permanently deaf, turned him inward, and catalyzed the most
        radical transformation in European painting history. His career traces an
        arc from luminous tapestry pastorals through political disaster paintings
        (Third of May, 1808) to the Black Paintings (Pinturas negras, 1820-23):
        a series of fourteen monumental oil murals painted directly on the plaster
        walls of his country house outside Madrid, "La Quinta del Sordo" (The
        House of the Deaf Man).

        THE BLACK PAINTINGS:
        No commission, no patron, no audience -- Goya painted these works for
        himself, apparently with no intention of sale or exhibition. They were
        discovered only after his death, transferred to canvas, and acquired by
        the Prado. Their subject matter ranges from devouring myth (Saturn
        Devouring His Son) to political satire (Two Old Men Eating Soup) to
        nightmare vision (Witches\' Sabbath) to existential landscape (The Dog).
        Technically, they represent Goya\'s most radical work: dark brown and
        bone-black grounds, paint applied with palette knife and fingers, raw
        gestural marks, and isolated pale highlights that emerge from the darkness
        with hallucinatory intensity.

        TECHNICAL CHARACTER:
        (1) DARK GROUND PENETRATION: Goya applied a dark brown ground (raw umber
        + lead white) to the plaster, then built up dark paint masses with bone
        black, Prussian blue, and burnt sienna. The brown ground shows through
        thin paint passages, giving the shadow zones a characteristic warm near-
        black quality distinct from cool neutral shadow.

        (2) TONAL COMPRESSION / CHIAROSCURO DRAMA: The Black Paintings operate
        in a very limited tonal range: most of the canvas is in deep shadow
        (values 0.0-0.35), a band of midtone exists at 0.35-0.60, and the
        highlights are isolated, intense, and bright (0.75-1.0). There is almost
        nothing in the 0.60-0.75 range -- the transition from shadow to light is
        abrupt and theatrical. This is the opposite of academic painting\'s smooth
        five-value system; Goya compresses to three values with hard boundaries
        between them.

        (3) GESTURAL MARK AND TRANSITION TURBULENCE: In the modelling passages
        (where light meets shadow), Goya\'s paint application is rough, agitated,
        almost violent -- he used palette knives, rags, and his own fingers to
        drag and smear paint across the transition zones. The flat dark masses
        and flat light areas have relatively smooth surfaces; the transitions
        between them carry raw, expressive texture.

        (4) WARM DARK PIGMENT: Goya\'s blacks are not cool neutral. They derive
        from bone black (warm, slightly brown), raw umber (warm ochre-brown),
        and occasionally Prussian blue-black (which has a slight warm tint in
        heavy impasto). The warm quality of Goya\'s dark zones is fundamental to
        the psychological temperature of the Black Paintings -- they feel not
        cold and nihilistic but hot, visceral, alive with darkness.

        Stage 1 DARK EARTH GROUND PENETRATION:
        Compute luminance L. For each pixel, compute a ground blend weight:
          w_ground = ground_strength * (1 - L)^2
        This weight is maximum in the deepest darks and falls quadratically as
        luminance increases, reaching zero by the time L = 1. Blend the warm
        umber ground color (ground_r, ground_g, ground_b) into all channels
        at this weight:
          R_g = R + (ground_r - R) * w_ground
        NOVEL: (a) QUADRATIC LUMINANCE-DEPENDENT GROUND INFUSION -- all prior
        passes that apply a fixed-color tint to shadow zones use a linear
        threshold mask (shadow_mask = L < threshold). This pass uses a
        QUADRATIC WEIGHT (1-L)^2 that is continuous (no threshold discontinuity)
        and falls nonlinearly: the ground penetrates twice as strongly into very
        dark zones vs. halftone zones, matching the physics of transparent dark
        paint over a warm ground where the thinnest dark passages (lightest darks)
        show proportionally less ground than opaque dark masses.

        Stage 2 SIGMOID TONAL DRAMA AMPLIFICATION:
        Apply a parametric sigmoid tonal curve to luminance:
          sig(L) = 1 / (1 + exp(-steepness * (L - midpoint)))
          L_new = tonal_min + (tonal_max - tonal_min) * sig(L)
        This compresses midtones toward darkness while preserving/boosting
        the brightest highlights. Apply by computing the ratio L_new / (L+eps)
        and scaling all channels:
          R_new = clip(R * (L_new / (L + eps)), 0, 1)
        Hue relationships are preserved because all channels are scaled by the
        same luminance ratio.
        NOVEL: (b) PARAMETRIC SIGMOID TONAL COMPRESSION preserving HUE RATIOS
        -- prior tonal contrast passes use linear or affine transforms (lifting
        darks, pushing lights). This pass uses a true sigmoid (smooth, nonlinear,
        with parametric midpoint and steepness) to compress the tonal distribution
        into Goya\'s characteristic three-zone chiaroscuro. Applying the sigmoid
        via luminance ratio (not per-channel) preserves the hue of all pixels
        while changing their value -- a combined tonal + hue-preserving transform
        that no prior pass implements.

        Stage 3 SHADOW DESATURATION WITH WARM UMBER TRACE:
        For shadow pixels (L_original < desaturate_thresh), compute a blend weight:
          w_desat = desaturate_strength * (1 - L / desaturate_thresh)
        (zero at threshold, maximum in deepest shadow). Apply combined:
          (i) DESATURATION: blend toward luminance grey:
              R_d = R + (L - R) * w_desat * 0.60
          (ii) UMBER TRACE: blend toward warm umber:
              R_d = R_d + (umber_r - R_d) * w_desat * umber_blend
        NOVEL: (c) SIMULTANEOUS SHADOW DESATURATION AND WARM HUE SHIFT --
        prior shadow passes desaturate (scumbling_veil) OR add complementary
        hue (complementary_shadow_pass) OR add warm edge (reflected_light_pass).
        This pass does both: desaturates the shadow AND shifts its residual hue
        toward warm umber, using a single continuous weight derived from luminance.
        The combination creates Goya\'s warm-near-black shadow character without
        turning shadows grey.

        Stage 4 TRANSITION ZONE TURBULENCE:
        Compute the Sobel gradient magnitude of luminance. Normalize to [0,1].
        Define transition pixels as those where the normalized gradient is in
        (grad_low, grad_high) -- above flat areas, below hard-edge areas.
        Generate a smooth noise field: sample uniform random (seeded), apply
        Gaussian filter at noise_sigma, normalize to zero mean unit std.
        Apply the noise to all channels, weighted by the transition mask and
        gradient magnitude:
          R_mod += noise * Gnorm * (transition_mask) * noise_strength
        NOVEL: (d) GRADIENT-MAGNITUDE-WEIGHTED TRANSITION ZONE NOISE -- prior
        texture passes add noise uniformly (globally or with a fixed opacity).
        This pass adds noise ONLY in the TRANSITION ZONE (neither flat dark
        masses nor flat lights) and weights the noise strength by GRADIENT
        MAGNITUDE within that zone. The result is roughest where luminance
        changes most rapidly (the modelling/edge zones) and absent in the flat
        dark masses and lights -- exactly matching Goya\'s rough transition
        passages with smooth flat zones.
        """
        print("    Goya Black Vision pass (188th mode)...")

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

        # Stage 1: dark earth ground penetration (quadratic weight)
        gs = float(ground_strength)
        gr, gg, gb = float(ground_r), float(ground_g), float(ground_b)
        w_ground = gs * (1.0 - L) ** 2
        R1 = _np.clip(R + (gr - R) * w_ground, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (gg - G) * w_ground, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (gb - B) * w_ground, 0.0, 1.0).astype(_np.float32)

        # Stage 2: sigmoid tonal drama
        mp = float(sigmoid_midpoint)
        st = float(sigmoid_steepness)
        t_min = float(tonal_min)
        t_max = float(tonal_max)
        sig_val = 1.0 / (1.0 + _np.exp(-st * (L - mp)))
        L_new = _np.clip(t_min + (t_max - t_min) * sig_val, 0.0, 1.05).astype(_np.float32)
        ratio = (L_new / (L + 1e-6)).astype(_np.float32)
        R2 = _np.clip(R1 * ratio, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 * ratio, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 * ratio, 0.0, 1.0).astype(_np.float32)

        # Stage 3: shadow desaturation + warm umber trace
        dthresh = float(desaturate_thresh)
        ds = float(desaturate_strength)
        ur, ug, ub = float(umber_r), float(umber_g), float(umber_b)
        ublend = float(umber_blend)
        below = (L < dthresh).astype(_np.float32)
        safe_dthresh = dthresh if dthresh > 1e-6 else 1e-6
        w_desat = ds * (1.0 - L / safe_dthresh) * below
        w_desat = _np.clip(w_desat, 0.0, 1.0).astype(_np.float32)
        # Desaturate toward grey
        L2 = (0.299 * R2 + 0.587 * G2 + 0.114 * B2).astype(_np.float32)
        R3 = _np.clip(R2 + (L2 - R2) * w_desat * 0.60, 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G2 + (L2 - G2) * w_desat * 0.60, 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B2 + (L2 - B2) * w_desat * 0.60, 0.0, 1.0).astype(_np.float32)
        # Warm umber trace
        R3 = _np.clip(R3 + (ur - R3) * w_desat * ublend, 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G3 + (ug - G3) * w_desat * ublend, 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B3 + (ub - B3) * w_desat * ublend, 0.0, 1.0).astype(_np.float32)

        # Stage 4: transition zone turbulence
        Gx = _sobel(L.astype(_np.float64), axis=1).astype(_np.float32)
        Gy = _sobel(L.astype(_np.float64), axis=0).astype(_np.float32)
        Gmag = _np.sqrt(Gx ** 2 + Gy ** 2).astype(_np.float32)
        g99 = float(_np.percentile(Gmag, 99)) + 1e-6
        Gnorm = (Gmag / g99).astype(_np.float32)
        gl = float(grad_low)
        gh = float(grad_high)
        trans_mask = ((Gnorm > gl) & (Gnorm < gh)).astype(_np.float32)
        rng = _np.random.default_rng(int(seed))
        raw_noise = rng.random((H, W)).astype(_np.float32)
        ns = max(float(noise_sigma), 0.3)
        smooth_noise = _gf(raw_noise, sigma=ns).astype(_np.float32)
        mn = float(smooth_noise.mean())
        sd = float(smooth_noise.std()) + 1e-6
        smooth_noise = ((smooth_noise - mn) / sd).astype(_np.float32)
        nstr = float(noise_strength)
        weight = (trans_mask * Gnorm * nstr).astype(_np.float32)
        R4 = _np.clip(R3 + smooth_noise * weight, 0.0, 1.0).astype(_np.float32)
        G4 = _np.clip(G3 + smooth_noise * weight, 0.0, 1.0).astype(_np.float32)
        B4 = _np.clip(B3 + smooth_noise * weight * 0.82, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R4 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G4 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B4 - B) * op, 0.0, 1.0).astype(_np.float32)

        trans_px = int(trans_mask.sum())
        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Goya Black Vision complete (trans_px={trans_px})")

'''

# ── Inject both passes into stroke_engine.py ─────────────────────────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

ANCHOR = "    def thiebaud_halo_shadow_pass("
assert ANCHOR in src, f"Anchor not found in stroke_engine.py: {ANCHOR!r}"

INSERTION = HALATION_BLOOM_PASS + GOYA_BLACK_VISION_PASS
new_src = src.replace(ANCHOR, INSERTION + ANCHOR, 1)

with open(SE_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("stroke_engine.py patched: paint_halation_bloom_pass (s277 improvement)"
      " + goya_black_vision_pass (188th mode) inserted before thiebaud_halo_shadow_pass.")
