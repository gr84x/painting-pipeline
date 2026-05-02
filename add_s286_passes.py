"""Insert paint_tonal_rebalance_pass (s286 improvement) and
carriere_smoky_reverie_pass (197th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_tonal_rebalance_pass (s286 improvement) ────────────────────

TONAL_REBALANCE_PASS = '''
    def paint_tonal_rebalance_pass(
        self,
        shadow_percentile:   float = 5.0,
        highlight_percentile:float = 95.0,
        curve_sharpness:     float = 1.60,
        shoulder_start:      float = 0.90,
        max_scale:           float = 1.80,
        opacity:             float = 0.85,
    ) -> None:
        r"""Tonal Rebalance -- s286 improvement.

        THE PHYSICAL BASIS: ADAPTIVE SIGMOIDAL TONE MAPPING WITH
        PERCENTILE AUTO-LEVELS AND LUMINANCE-RATIO CHROMATIC PRESERVATION

        Every painted canvas contains a tonal distribution shaped by its
        content: a night scene clusters luminance values in the lower quarter;
        a high-key plein-air sketch clusters them in the upper quarter; a
        balanced composition spreads them more evenly across the full range.
        The tonal rebalance pass performs two operations in sequence:

          (i)  auto-levels stretch: expands the painting\'s actual tonal range
               to use the full available dynamic range [0, 1], anchored to
               content-adaptive percentile shadow and highlight points;
          (ii) S-curve shaping: applies a symmetric sigmoidal contrast curve
               (hyperbolic tangent) that lifts shadows, steepens midtones,
               and compresses highlights -- analogous to the film S-curve
               or darkroom "burning and dodging in the midtone zone."

        HISTORICAL AND ARTISTIC CONTEXT:

        Tonal calibration has been a preoccupation of painters since the
        discovery of value modeling in the early Renaissance. Leonardo\'s
        sfumato was in part a tonal strategy: compress the darkest darks
        toward a common deep shadow tone, preserve the gradients in the
        midtones. Rembrandt\'s darkroom technique was the opposite: hold
        the shadows near-black and reserve all dynamic range for the upper
        midtones and lights where the face is modelled. Turner\'s late work
        compresses all values toward the upper luminance range, trading
        depth for luminosity.

        In photography, the "S-curve" in darkroom printing corresponds
        exactly to the hyperbolic tangent: greater sensitivity in the
        midtones (film grain alignment, silver crystal response), with
        shoulder (highlight roll-off) and toe (shadow lift) that soften
        the extremes. Ansel Adams\'s Zone System formalized this: each of
        his 10 zones corresponds to a segment of a continuous tonal curve.

        In digital painting, tonal rebalancing is performed by luminance
        histogram remapping -- adjusting the mapping between input and
        output tonal values based on the image\'s actual histogram. The
        percentile auto-levels stretch ensures the image uses its full
        dynamic range; the S-curve then shapes that range into an
        aesthetically pleasing distribution.

        STAGE 1 -- PERCENTILE AUTO-LEVELS (ADAPTIVE TONAL STRETCH):

        Compute luminance L = 0.299R + 0.587G + 0.114B for all pixels.
        Find the shadow point P_lo = percentile(L, shadow_percentile) and
        the highlight point P_hi = percentile(L, highlight_percentile).
        Remap linearly:
          L_norm = clip( (L - P_lo) / max(P_hi - P_lo, eps), 0, 1 )

        This expands the image\'s actual tonal range [P_lo, P_hi] to fill
        [0, 1] completely, discarding only the clipped tails (the darkest
        shadow_percentile% and the brightest (100-highlight_percentile)%).

        NOVEL: (a) PERCENTILE-BASED PER-IMAGE TONAL RANGE DETECTION.
        Every prior pass in this engine that modifies luminance or contrast
        uses fixed parameters (gamma exponents, fixed thresholds, fixed
        target colors). No prior pass has computed the image\'s actual tonal
        range from its histogram and used that measurement to drive an
        adaptive correction. This is the first pass to:
          (i)  measure the painting\'s actual tonal distribution;
          (ii) derive its shadow and highlight endpoints dynamically;
          (iii) perform a content-adaptive linear stretch based on those
                measured endpoints -- not a fixed global parameter.

        STAGE 2 -- HYPERBOLIC TANGENT S-CURVE:

        Apply a smooth, symmetric S-curve to L_norm:
          u = L_norm * 2.0 - 1.0         [remap [0,1] to [-1,+1]]
          L_curve = 0.5 + 0.5 * tanh(k * u) / tanh(k)

        Where k = curve_sharpness (default 1.60). The tanh curve has the
        following properties:
          - Passes through (0, 0), (0.5, 0.5), (1.0, 1.0) exactly:
            the neutral midpoint is preserved.
          - Symmetric around the midpoint (0.5 → 0.5 is a fixed point).
          - Slopes steeply near midpoint (high midtone contrast), gently
            at 0 and 1 (shadow lift, highlight compression).
          - The parameter k controls sharpness: k→0 gives identity; k→∞
            gives a step function; k=1.6 gives a moderate S-curve.

        NOVEL: (b) HYPERBOLIC TANGENT TONE CURVE.
        Prior S-curves and contrast operations in this engine:
          - Grosz Stage 4: power-law gamma expansion L^0.80 (monotone
            power law, no inflection, all-zones compression/expansion).
          - Sigmoids mentioned in engine docstrings use 1/(1+exp(-x)) for
            binary zone masking (e.g., midtone bell functions), not as a
            tone curve applied to the full canvas.
          - Midtone S-curve references in some passes apply polynomial
            ZONE MASKS to select midtone pixels, not a curve applied to
            all luminance values.
        The tanh curve is different from all of these: it is a true
        tone curve (maps every luminance value to a remapped value),
        symmetric (L=0.5 is a fixed point), and has a continuously
        adjustable shape parameter k. No prior pass applies tanh() to
        the luminance channel as a canvas-wide tone mapping function.

        STAGE 3 -- LUMINANCE-RATIO CHROMATIC PRESERVATION:

        Rather than desaturating toward grey as a side-effect of luminance
        adjustment, preserve the hue angle (R:G:B ratios) exactly by
        applying a per-pixel multiplicative luminance scaling:

          scale = clip( L_curve / max(L_norm, eps), 0, max_scale )
          R_out_unmixed = clip( R * scale, 0, 1 )

        This scales each RGB channel by the same factor scale, which:
          (i)  preserves R:G:B ratios (hue angle unchanged);
          (ii) changes luminance from L_norm to L_curve;
          (iii) preserves saturation implicitly (since hue is unchanged).

        NOVEL: (c) LUMINANCE-RATIO CHROMATIC PRESERVATION.
        All prior luminance modification passes in this engine apply
        additive operations (R_new = R + blend * (target_R - R)) which
        inherently shift hue when the target color differs from the
        current color. This pass uses a MULTIPLICATIVE RATIO (scale =
        L_new / L_old) which is the only operation that changes luminance
        while preserving hue angle exactly. The additive blend has a
        known "greying out" artifact when used at high blend strengths;
        ratio scaling has no such artifact. This is the first pass to
        use luminance ratio as a chroma-preserving channel amplifier.

        STAGE 4 -- HIGHLIGHT SHOULDER COMPRESSION:

        After S-curve, very bright pixels (L_out > shoulder_start) receive
        a gentle soft-clipping to prevent harsh white zones:
          excess = clip( L_out - shoulder_start, 0, None )
          L_shoulder = shoulder_start + excess * (1 - shoulder_start) /
                       sqrt(1 + (excess / (1 - shoulder_start))^2)

        This is a hyperbolic soft-clamp that asymptotically approaches 1.0
        as excess grows, never exactly reaching it, preventing pure white
        while smoothly rolling off the brightest highlights.

        NOVEL: (d) HYPERBOLIC HIGHLIGHT KNEE.
        Prior passes clip highlights with np.clip(..., 0, 1) which is a
        hard knee (discontinuous first derivative at 1.0). No prior pass
        applies a smooth soft-clamp with a continuous soft rolloff to
        prevent blowout. The hyperbolic form x/sqrt(1+x^2) is different
        from the tanh form and gives a different rolloff shape. This is
        the first pass to implement soft highlight compression independent
        of a full tone curve.
        """
        print("    Tonal Rebalance pass (session 286 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        eps = 1e-6

        # Stage 1: Percentile auto-levels
        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)
        p_lo = float(_np.percentile(L, float(shadow_percentile)))
        p_hi = float(_np.percentile(L, float(highlight_percentile)))
        span = max(p_hi - p_lo, eps)
        L_norm = _np.clip((L - p_lo) / span, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Hyperbolic tangent S-curve
        k = max(float(curve_sharpness), 0.01)
        u = (L_norm * 2.0 - 1.0).astype(_np.float32)
        tanh_k = float(_np.tanh(k))
        L_curve = (0.5 + 0.5 * _np.tanh(k * u) / tanh_k).astype(_np.float32)
        L_curve = _np.clip(L_curve, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Luminance-ratio chromatic preservation
        ms = float(max_scale)
        scale = _np.clip(L_curve / _np.maximum(L_norm, eps), 0.0, ms
                         ).astype(_np.float32)
        R_adj = _np.clip(R * scale, 0.0, 1.0).astype(_np.float32)
        G_adj = _np.clip(G * scale, 0.0, 1.0).astype(_np.float32)
        B_adj = _np.clip(B * scale, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Highlight shoulder compression
        sh = float(shoulder_start)
        def _soft_shoulder(arr: "_np.ndarray") -> "_np.ndarray":
            excess = _np.clip(arr - sh, 0.0, None).astype(_np.float32)
            tail = (1.0 - sh)
            return (sh + excess * tail / _np.sqrt(1.0 + (excess / tail) ** 2)
                    ).astype(_np.float32)

        R_sh = _np.where(R_adj > sh, _soft_shoulder(R_adj), R_adj
                         ).astype(_np.float32)
        G_sh = _np.where(G_adj > sh, _soft_shoulder(G_adj), G_adj
                         ).astype(_np.float32)
        B_sh = _np.where(B_adj > sh, _soft_shoulder(B_adj), B_adj
                         ).astype(_np.float32)

        # Composite with original at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R_sh - R) * op, 0.0, 1.0).astype(_np.uint8 if False else _np.float32)
        G_out = _np.clip(G + (G_sh - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B_sh - B) * op, 0.0, 1.0).astype(_np.float32)

        lo_count  = int((L < p_lo + 0.01).sum())
        hi_count  = int((L > p_hi - 0.01).sum())
        mid_mean  = float(_np.mean(L_curve[(L_norm > 0.45) & (L_norm < 0.55)]))

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Tonal Rebalance complete "
              f"(p_lo={p_lo:.3f}, p_hi={p_hi:.3f}, k={k:.2f}, "
              f"mid_mean={mid_mean:.3f}, lo_px={lo_count}, hi_px={hi_count})")

'''

# ── Pass 2: carriere_smoky_reverie_pass (197th mode) ─────────────────────────

CARRIERE_SMOKY_REVERIE_PASS = '''
    def carriere_smoky_reverie_pass(
        self,
        sepia_r:             float = 0.58,
        sepia_g:             float = 0.44,
        sepia_b:             float = 0.28,
        sepia_strength:      float = 0.68,
        shadow_tau:          float = 0.28,
        shadow_strength:     float = 0.52,
        shadow_dark_r:       float = 0.12,
        shadow_dark_g:       float = 0.08,
        shadow_dark_b:       float = 0.05,
        dissolve_sigma:      float = 3.2,
        dissolve_strength:   float = 0.55,
        border_falloff:      float = 3.8,
        border_strength:     float = 0.62,
        opacity:             float = 0.88,
    ) -> None:
        r"""Carriere Smoky Reverie -- 197th mode (Symbolism / Eugene Carriere).

        EUGENE CARRIERE (1849-1906) -- FRENCH SYMBOLIST PAINTER;
        MASTER OF THE WARM MONOCHROME:

        Eugene Carriere was born in Gournay-sur-Marne in 1849 and received his
        early training in Strasbourg before moving to Paris, where he became a
        pupil of Alexandre Cabanel at the Ecole des Beaux-Arts. His first
        significant canvases were conventional portraits and genre scenes, but
        around 1880 he began developing the radically distinctive technique
        that would define his mature work: a deliberately monochromatic palette
        of warm browns, sepia, and bistre from which figures and faces emerge
        with an almost preternatural psychological presence.

        The catalyst for this transformation was a personal loss: his study of
        the Old Masters, particularly the warm shadows of Rembrandt and the
        atmospheric dissolve of Velazquez\'s late interiors, combined with his
        own emotional response to the intimacy of family life, produced the
        characteristic Carriere effect -- forms that seem to emerge from
        warm darkness rather than being placed upon a ground. His friend
        Auguste Rodin wrote of Carriere: "He paints shadows that are born."

        Carriere became one of the central figures of the Symbolist movement
        in France, exhibiting regularly at the Salon de la Rose + Croix and
        at his own independent exhibitions. He founded a studio school in
        Montmartre (l\'Academie Carriere) where his students included Henri
        Matisse, Jean Puy, and Andre Derain -- the very painters who would
        overthrow Symbolism in favour of Fauvism. The irony is complete: the
        master of monochrome darkness trained the inventors of pure chromatic
        liberation. When Derain described his education at the Academie
        Carriere, he recalled learning above all else to see form in shadow --
        the lesson he spent the rest of his life inverting.

        CARRIERE\'S FIVE DEFINING TECHNICAL CHARACTERISTICS:

        1. WARM MONOCHROME DOMINANCE: Unlike neutral greyscale painters,
           Carriere chose a warm bistre-brown as the organizing tone of
           his entire canvas. All local colours -- flesh, fabric, wood,
           shadow, light -- were subordinated to the warm monochrome
           field. The effect is of a single pervading temperature that
           unifies every element. No cool greys exist in a Carriere; even
           the deepest shadows carry warmth. This makes his paintings
           feel intimate and interior regardless of subject.

        2. FORM EMERGENCE FROM WARM DARKNESS: Rather than placing figures
           on a background, Carriere began every canvas with a dark warm
           ground and allowed forms to emerge from it by applying
           successive thin scumbles of warmer, lighter colour. The result
           is that his figures literally grow out of the darkness, as if
           the act of painting is an act of recovery, finding the form
           that was always present in the void. The background and figure
           share the same fundamental tone; only the luminance distinguishes
           them, not the hue.

        3. SOFT EDGE DISSOLUTION: Every edge in a Carriere is soft. Not
           merely blurred -- specifically, Carriere understood that the
           apparent sharpness of an edge is proportional to the luminance
           contrast across it. He worked to maintain the luminance contrast
           while dissolving the spatial sharpness: the eye reads the edge
           as a separation of values, not as a drawn line. This technique
           creates the impression of form in space -- three-dimensional
           presence -- without any hard contour. The figure seems to occupy
           air rather than sit on a surface.

        4. DEEP SHADOW UNIFICATION: All the dark zones of a Carriere painting
           merge toward a single common dark warm tone -- a deep umber that
           carries no distinguishable hue variation. The shadow cast by a
           sleeve and the shadow in a background corner are the same colour.
           This unity of dark creates compositional coherence: the darks do
           not compete with each other because they are all the same.

        5. PERIPHERAL DARKENING (EDGE FADE): Carriere consistently darkened
           the extreme edges and corners of his canvases, drawing the eye
           inward to the warm luminance at the centre. Unlike the focal
           vignette (which centers on the brightest zone), Carriere\'s edge
           fade was a formal device -- a consistent peripheral shadow,
           equal on all sides, that reinforces the sense of depth and
           locates the subject in a spatial pocket of warmth.

        THE GREAT WORKS:
        "Maternity" (1892): A mother holding a sleeping infant, both faces
        dissolved in warm shadow, the faces emerging as two zones of warm
        luminance from a unified dark ground.

        "Portrait of Paul Verlaine" (1891): The poet rendered in characteristic
        bistre monochrome, his features materializing from the warm darkness
        with an expression of weary intelligence.

        "The Sick Child" (1885): A tender domestic scene in which the child
        and parent are unified by shared warm shadow, the urgency of the
        subject conveyed entirely through luminance contrast.

        "Portrait of Anatole France" (1895): The novelist\'s face emerging
        from deep warm darkness, the entire canvas a single tonal gesture.

        "Intimate Family" (1895): Multiple figures grouped in characteristic
        Carriere integration -- the dark between figures and the dark of the
        background are indistinguishable, creating a unified organic mass.

        NOVELTY ANALYSIS: FOUR DISTINCT MATHEMATICAL INNOVATIONS:

        Stage 1 WARM SEPIA TINT (Monochrome Dominance):
        Compute luminance L, build sepia target: R_s = L * sepia_r,
        G_s = L * sepia_g, B_s = L * sepia_b. Blend with original:
          R1 = R + (R_s - R) * sepia_strength
        This creates a luminance-preserving warm tint across the whole canvas.
        NOVEL: (a) LUMINANCE-SCALED WARM TINT APPLIED UNIFORMLY WITHOUT
        LUMINANCE GATING. Prior warm/sepia operations in this engine:
          - repin Stage 2: warm midtone push toward (0.70/0.50/0.32) --
            gated to lum bell 0.30-0.62 (midtone zone only, not full canvas)
          - grosz Stage 3: acid green push -- gated by per-channel colour
            dominance mask (not applied to all zones uniformly)
          - paint_chromatic_shadow_shift_pass (s284): hue rotation in HSV
            space -- operates on H channel, not a monochrome sepia tint
          - warm_tint in some early passes: applied additively with a fixed
            colour, not via luminance scaling (sepia = L * warm_target)
        This stage tints the entire canvas (no zone gate) by scaling each
        pixel\'s luminance by the warm sepia triplet -- the tint strength
        at any pixel is proportional to that pixel\'s luminance, which
        automatically preserves relative value contrast while adding warmth.
        The formula R_s = L * sepia_r is the first "luminance-scaled" tint
        in the engine -- distinct from additive tinting.

        Stage 2 EXPONENTIAL SHADOW MERGE:
        Gate = exp(-L / shadow_tau) [exponential decay from 0 at L=0]
        Push toward deep warm dark: R2 = R1 + gate * strength * (dark_r - R1)
        NOVEL: (b) EXPONENTIAL DECAY FUNCTION AS LUMINANCE ZONE GATE.
        Prior shadow/dark zone gates in the engine:
          - repin Stage 3: L < 0.32 (hard threshold step function)
          - grosz Stage 4: gamma L^0.80 (power law, applied to all zones)
          - savrasov: midtone bell function (triangular/parabolic shape,
            non-zero only in 0.38-0.68 zone)
          - paint_shadow_temperature_pass (s281): linear ramp within
            shadow_range of shadow_thresh (trapezoidal gate)
        exp(-L/tau) is a different mathematical family: it is maximal at
        L=0 (pure black), decays smoothly and monotonically to near-zero
        at bright values, has no hard threshold, and the parameter tau
        controls the rate of decay (not a simple threshold). For tau=0.28:
        L=0.0 → gate=1.0; L=0.28 → gate=0.37; L=0.56 → gate=0.14;
        L=0.84 → gate=0.05. FIRST pass to use negative exponential as gate.

        Stage 3 GRADIENT-MAGNITUDE-WEIGHTED SOFT EDGE DISSOLUTION:
        G_norm = normalized gradient magnitude (0=interior, 1=edge)
        blurred = Gaussian(canvas, sigma=dissolve_sigma)
        weight = clip(G_norm^0.5 * dissolve_strength, 0, 1)
        output = canvas * (1 - weight) + blurred * weight
        NOVEL: (c) MORE BLUR WHERE G_NORM IS HIGHER -- opposite to all prior
        edge-related passes in this engine, which:
          - SHARPEN at high G_norm zones (repin Stage 4 unsharp mask;
            paint_lost_found_edges_pass sharpening branch)
          - SMOOTH at low G_norm / interior zones (grosz Stage 2 interior
            flattening; savrasov Stage 1 mist blur on interior)
          - Apply uniform Gaussian to entire canvas (repin Stage 1)
        This is the first pass to use G_norm as a blur WEIGHT (not a blur
        gate to avoid). The counterintuitive result: edges in Carriere\'s
        paintings are soft specifically because the luminance gradient is
        high -- the contrast is visible but the spatial sharpness is gone.

        Stage 4 PERIPHERAL EDGE FADE (Canvas Border Darkening):
        d_edge = min(x, W-1-x, y, H-1-y) / (min(W,H) * 0.5)
        border_gate = clip(1 - d_edge * border_falloff, 0, 1)
        scale = 1 - border_gate * border_strength
        R4 = R3 * scale
        NOVEL: (d) MINIMUM-DISTANCE-TO-BOUNDARY AS ZONE GATE.
        The paint_focal_vignette_pass (s278) uses RADIAL DISTANCE from a
        DETECTED FOCAL CENTER (luminance-weighted centroid) as its zone gate:
          d_focal = sqrt((x-cx)^2 + (y-cy)^2) / d_max_diagonal
        This stage uses MINIMUM DISTANCE TO THE NEAREST CANVAS BOUNDARY:
          d_edge = min(x, W-1-x, y, H-1-y)  [Chebyshev distance to border]
        The two are geometrically distinct:
          - focal vignette: L2 circle from detected content center
          - peripheral fade: L_infinity rectangle from canvas perimeter
        The focal vignette is content-adaptive (center moves with content);
        the peripheral fade is canvas-absolute (always darkens the
        rectangular border). For Carriere\'s technique, the peripheral fade
        is appropriate: his darkening was a formal device applied uniformly
        to all four canvas edges regardless of where the subject was.
        """
        print("    Carriere Smoky Reverie pass (197th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        eps = 1e-6

        # Stage 1: Warm sepia tint (luminance-scaled monochrome reduction)
        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)
        sr, sg, sb = float(sepia_r), float(sepia_g), float(sepia_b)
        ss = float(sepia_strength)
        R_s = (L * sr).astype(_np.float32)
        G_s = (L * sg).astype(_np.float32)
        B_s = (L * sb).astype(_np.float32)
        R1 = _np.clip(R + (R_s - R) * ss, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (G_s - G) * ss, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (B_s - B) * ss, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Exponential shadow merge
        tau = max(float(shadow_tau), 0.01)
        gate = _np.exp(-L / tau).astype(_np.float32)
        sstr = float(shadow_strength)
        dr, dg, db_ = float(shadow_dark_r), float(shadow_dark_g), float(shadow_dark_b)
        R2 = _np.clip(R1 + gate * sstr * (dr - R1), 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + gate * sstr * (dg - G1), 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + gate * sstr * (db_ - B1), 0.0, 1.0).astype(_np.float32)

        # Stage 3: Gradient-magnitude soft edge dissolution
        L2 = (0.299 * R2 + 0.587 * G2 + 0.114 * B2).astype(_np.float32)
        gsig = 1.8
        Gx = _gf(L2, sigma=gsig, order=[0, 1]).astype(_np.float32)
        Gy = _gf(L2, sigma=gsig, order=[1, 0]).astype(_np.float32)
        G_mag = _np.sqrt(Gx * Gx + Gy * Gy).astype(_np.float32)
        p90 = float(_np.percentile(G_mag, 90.0))
        G_norm = _np.clip(G_mag / max(p90, eps), 0.0, 1.0).astype(_np.float32)

        dsig = max(float(dissolve_sigma), 0.5)
        dstr = float(dissolve_strength)
        blur_R = _gf(R2, sigma=dsig).astype(_np.float32)
        blur_G = _gf(G2, sigma=dsig).astype(_np.float32)
        blur_B = _gf(B2, sigma=dsig).astype(_np.float32)
        weight = _np.clip(_np.sqrt(G_norm) * dstr, 0.0, 1.0).astype(_np.float32)
        R3 = (R2 * (1.0 - weight) + blur_R * weight).astype(_np.float32)
        G3 = (G2 * (1.0 - weight) + blur_G * weight).astype(_np.float32)
        B3 = (B2 * (1.0 - weight) + blur_B * weight).astype(_np.float32)

        # Stage 4: Peripheral edge fade (min-distance-to-boundary gate)
        xs = _np.arange(W_, dtype=_np.float32)
        ys = _np.arange(H_, dtype=_np.float32)
        XX, YY = _np.meshgrid(xs, ys)
        d_left   = XX.astype(_np.float32)
        d_right  = (W_ - 1 - XX).astype(_np.float32)
        d_top    = YY.astype(_np.float32)
        d_bottom = (H_ - 1 - YY).astype(_np.float32)
        d_edge_px = _np.minimum(_np.minimum(d_left, d_right),
                                _np.minimum(d_top, d_bottom)).astype(_np.float32)
        ref_size = float(min(W_, H_)) * 0.5
        d_edge_norm = (d_edge_px / max(ref_size, 1.0)).astype(_np.float32)

        bfall = float(border_falloff)
        bstr  = float(border_strength)
        border_gate = _np.clip(1.0 - d_edge_norm * bfall, 0.0, 1.0
                               ).astype(_np.float32)
        scale = (1.0 - border_gate * bstr).astype(_np.float32)
        R4 = _np.clip(R3 * scale, 0.0, 1.0).astype(_np.float32)
        G4 = _np.clip(G3 * scale, 0.0, 1.0).astype(_np.float32)
        B4 = _np.clip(B3 * scale, 0.0, 1.0).astype(_np.float32)

        # Final composite
        op = float(opacity)
        R_out = _np.clip(R + (R4 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G4 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B4 - B) * op, 0.0, 1.0).astype(_np.float32)

        sepia_px  = int((weight > 0.10).sum())
        shadow_px = int((gate > 0.30).sum())
        border_px = int((border_gate > 0.10).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Carriere Smoky Reverie complete "
              f"(sepia_px={sepia_px}, shadow_px={shadow_px}, border_px={border_px})")

'''

# ── Append both passes to stroke_engine.py ───────────────────────────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8-sig") as f:
    src = f.read()

assert "paint_tonal_rebalance_pass" not in src, \
    "paint_tonal_rebalance_pass already exists in stroke_engine.py"
assert "carriere_smoky_reverie_pass" not in src, \
    "carriere_smoky_reverie_pass already exists in stroke_engine.py"

with open(SE_PATH, "a", encoding="utf-8") as f:
    f.write(TONAL_REBALANCE_PASS)
    f.write(CARRIERE_SMOKY_REVERIE_PASS)

print("stroke_engine.py patched: paint_tonal_rebalance_pass (s286 improvement)"
      " + carriere_smoky_reverie_pass (197th mode) appended.")
