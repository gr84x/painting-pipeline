"""Insert paint_contre_jour_rim_pass (s282 improvement) and
savrasov_lyrical_mist_pass (193rd mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_contre_jour_rim_pass (s282 improvement) ────────────────────

CONTRE_JOUR_RIM_PASS = '''
    def paint_contre_jour_rim_pass(
        self,
        bright_threshold:    float = 0.70,
        dark_threshold:      float = 0.42,
        gradient_sigma:      float = 1.5,
        rim_sigma:           float = 3.0,
        rim_strength:        float = 0.52,
        rim_r:               float = 0.88,
        rim_g:               float = 0.62,
        rim_b:               float = 0.24,
        cool_edge_strength:  float = 0.30,
        cool_edge_r:         float = 0.52,
        cool_edge_g:         float = 0.62,
        cool_edge_b:         float = 0.80,
        edge_percentile:     float = 75.0,
        opacity:             float = 0.80,
    ) -> None:
        r"""Contre-Jour Rim Light -- s282 improvement.

        THE CONTRE-JOUR PHENOMENON IN PAINTING:

        Contre-jour (French: "against the daylight") describes the compositional
        and optical arrangement where the dominant light source is placed behind
        the subject, creating a silhouetted or back-lit figure. This arrangement
        produces a distinctive range of edge effects that are among the most
        prized in the history of painting:

        RIM LIGHT (warm): At the silhouette edge of a back-lit subject, the
        light source wraps partially around the form, creating a narrow band
        of warm, often golden or orange-amber luminance that traces the outline
        of the dark subject against the bright background. This rim is caused
        by light scattering through thin materials (hair, leaves, cloth) and by
        subsurface scattering in translucent subjects. Sargent, Sorolla, and
        Rembrandt all exploited this phenomenon: in Sorolla\'s beach scenes,
        contre-jour figures carry a brilliant white-gold rim against the sun-lit
        Mediterranean sea; in Rembrandt\'s candlelit portraits, the warm rim of
        light at the edge of a dark figure against shadow gives that edge a
        vibrating luminosity that flat-lit painting cannot achieve.

        COOL HALATION (cool): Simultaneously, on the light side of the boundary
        (the bright background adjacent to the dark subject), a narrow zone of
        slightly cooler, more desaturated color appears. This is the shadow
        cast by the dark subject\'s edge onto the adjacent bright area (the
        half-shadow or penumbra of an extended light source), combined with
        the simultaneous contrast effect where a dark border makes adjacent
        bright areas appear slightly cooler and less saturated than they
        actually are.

        PRIOR PASSES AND NOVELTY:
        All prior improvement passes in this engine affect either: (a) the entire
        canvas uniformly (surface_grain, depth_atmosphere); (b) luminance-defined
        zones regardless of edge structure (shadow_temperature -- threshold on L);
        (c) gradient-magnitude edges without distinguishing which side is bright
        and which is dark (lost_found_edges -- applies USM to "found" edges
        without a bright/dark asymmetry). No prior pass:
          (i)  constructs an explicit bright-zone mask and a dark-zone mask;
          (ii) computes the DARK SIDE of bright/dark boundaries (dark zone
               adjacent to bright zone) to apply a warm rim;
          (iii) computes the BRIGHT SIDE of those same boundaries to apply a
               complementary cool edge.
        This pass is the first to model the specific optical geometry of contre-
        jour lighting -- applying different chromatic effects to the two sides of
        a luminance boundary rather than treating the edge as a single entity.

        Stage 1 BRIGHT/DARK ZONE CLASSIFICATION (Luminance Boundary Identification):
        Compute grayscale luminance L.
        bright_mask = (L > bright_threshold) as float
        dark_mask   = (L < dark_threshold)   as float
        The gap between thresholds (midtones) is not masked, preventing
        treatment of midtone gradients as contre-jour boundaries.
        Compute gradient magnitude via Gaussian derivative to weight the final
        effect by the actual sharpness of the luminance transition:
          G = sqrt(Gx^2 + Gy^2)  from sigma=gradient_sigma derivatives
        Normalize: G_norm = G / percentile(G, edge_percentile) (unit scale)
        NOVEL: (a) DUAL-SIDE LUMINANCE MASK -- bright and dark zone masks are
        constructed INDEPENDENTLY from separate thresholds and used separately
        to apply opposing effects. Prior passes apply a single zone operation
        (shadow_temperature: shadow_mask; lost_found_edges: found/lost by
        gradient strength). This pass uses the geometric relationship BETWEEN
        two zone masks, not the masks in isolation.

        Stage 2 DARK-SIDE RIM LIGHT (Warm Rim at Silhouette Edge):
        Dilate the bright_mask by convolving with a Gaussian of sigma=rim_sigma:
          bright_dilated = GaussianFilter(bright_mask, sigma=rim_sigma)
        This dilation extends the bright-zone "reach" by ~rim_sigma pixels.
        rim_mask = dark_mask * bright_dilated * clip(G_norm, 0, 1)
        rim_mask identifies dark-zone pixels near the bright zone, weighted by
        local gradient magnitude (stronger rim at sharper luminance transitions).
        Push these pixels toward warm rim color (rim_r/g/b -- golden orange):
          C_rim = C + (rim_color - C) * rim_mask * rim_strength
        NOVEL: (b) DARK-SIDE-OF-BOUNDARY WARM PUSH -- no prior pass uses
        bright-mask dilation to identify dark pixels specifically adjacent to the
        bright zone. Prior warm-zone passes operate on absolute luminance thresholds
        or midtone Gaussian gates -- they do not distinguish dark pixels near
        a bright zone from dark pixels in open shadow. The dark-side-of-boundary
        selectivity is the defining property of contre-jour rim simulation.

        Stage 3 BRIGHT-SIDE COOL EDGE (Cool Halation at Illuminated Boundary):
        Dilate the dark_mask symmetrically:
          dark_dilated = GaussianFilter(dark_mask, sigma=rim_sigma)
        cool_edge_mask = bright_mask * dark_dilated * clip(G_norm, 0, 1)
        Identifies bright-zone pixels adjacent to dark zone, weighted by
        gradient magnitude.
        Push toward cool halation color (cool_edge_r/g/b -- cool sky-blue):
          C_cool = C_rim + (cool_edge - C_rim) * cool_edge_mask * cool_edge_strength
        NOVEL: (c) BRIGHT-SIDE-OF-BOUNDARY COOL PUSH applied simultaneously with
        (b): the rim pass creates a DIALOGUE between the two sides of the
        luminance boundary -- warm rim on the dark side, cool halation on the
        bright side. The two effects are geometrically complementary: they exist
        at the same boundary but on opposite sides, modeling the actual optical
        physics of contre-jour illumination.

        Stage 4 GRADIENT-MAGNITUDE WEIGHTING (Sharp-Edge Selectivity):
        The G_norm factor in both rim_mask and cool_edge_mask ensures that the
        rim and cool-edge effects are strongest at sharp luminance boundaries
        (tree silhouettes against sky, figures against bright windows) and
        absent at soft gradients (atmospheric recession, tonal blending).
        This confines the effect to genuine structural edges rather than
        applying it uniformly to the bright/dark transition zone.
        NOVEL: (d) GRADIENT-WEIGHTED SPATIAL MASKING COMBINED WITH ZONE
        GEOMETRY -- the gradient weight acts as a texture-sensitive gate that
        turns off the rim effect in smooth gradients while maximizing it at
        hard silhouette edges. No prior pass uses this combination of (zone
        geometry via dilation) × (gradient magnitude as continuity weight).
        """
        print("    Contre-Jour Rim Light pass (session 282 improvement)...")

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

        # Stage 1: Bright/dark zone classification + gradient magnitude
        bt = float(bright_threshold)
        dt = float(dark_threshold)
        bright_mask = (L > bt).astype(_np.float32)
        dark_mask   = (L < dt).astype(_np.float32)

        gsig = max(float(gradient_sigma), 0.5)
        Gx = _gf(L, sigma=gsig, order=[0, 1]).astype(_np.float32)
        Gy = _gf(L, sigma=gsig, order=[1, 0]).astype(_np.float32)
        Gmag = _np.sqrt(Gx * Gx + Gy * Gy).astype(_np.float32)
        ep = float(edge_percentile)
        G_scale = max(float(_np.percentile(Gmag, ep)), 1e-6)
        G_norm = _np.clip(Gmag / G_scale, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Dark-side rim light (warm rim at silhouette edge)
        rsig = max(float(rim_sigma), 0.5)
        bright_dilated = _gf(bright_mask, sigma=rsig).astype(_np.float32)
        rim_mask = (dark_mask * bright_dilated * G_norm).astype(_np.float32)

        rstr = float(rim_strength)
        rr, rg, rb_ = float(rim_r), float(rim_g), float(rim_b)
        R1 = _np.clip(R + (rr - R) * rim_mask * rstr, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (rg - G) * rim_mask * rstr, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (rb_ - B) * rim_mask * rstr, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Bright-side cool edge (cool halation at illuminated boundary)
        dark_dilated = _gf(dark_mask, sigma=rsig).astype(_np.float32)
        cool_edge_mask = (bright_mask * dark_dilated * G_norm).astype(_np.float32)

        cestr = float(cool_edge_strength)
        cer, ceg, ceb = float(cool_edge_r), float(cool_edge_g), float(cool_edge_b)
        R2 = _np.clip(R1 + (cer - R1) * cool_edge_mask * cestr, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (ceg - G1) * cool_edge_mask * cestr, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (ceb - B1) * cool_edge_mask * cestr, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R2 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G2 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B2 - B) * op, 0.0, 1.0).astype(_np.float32)

        rim_px      = int((rim_mask      > 0.05).sum())
        cool_px     = int((cool_edge_mask > 0.05).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Contre-Jour Rim complete "
              f"(rim_px={rim_px}, cool_px={cool_px}, "
              f"G_scale={G_scale:.4f})")

'''

# ── Pass 2: savrasov_lyrical_mist_pass (193rd mode) ───────────────────────────

SAVRASOV_LYRICAL_MIST_PASS = '''
    def savrasov_lyrical_mist_pass(
        self,
        mist_hwidth:         int   = 40,
        mist_vwidth:         int   = 2,
        mist_strength:       float = 0.30,
        mid_lo:              float = 0.38,
        mid_hi:              float = 0.68,
        mid_r:               float = 0.62,
        mid_g:               float = 0.67,
        mid_b:               float = 0.76,
        mid_strength:        float = 0.28,
        branch_sigma:        float = 1.2,
        branch_percentile:   float = 80.0,
        branch_sharp:        float = 0.55,
        branch_sharp_sigma:  float = 0.8,
        horizon_zone:        float = 0.60,
        horizon_sat_thresh:  float = 0.22,
        horizon_sat_sigma:   float = 3.0,
        horizon_r:           float = 0.74,
        horizon_g:           float = 0.68,
        horizon_b:           float = 0.46,
        horizon_strength:    float = 0.32,
        opacity:             float = 0.88,
    ) -> None:
        r"""Savrasov Lyrical Mist (Russian Lyrical Landscape) -- 193rd mode.

        ALEXEI KONDRATYEVICH SAVRASOV (1830-1897) -- RUSSIAN REALIST;
        FOUNDER OF THE LYRICAL LANDSCAPE TRADITION:

        Alexei Savrasov was born in Moscow in 1830 to a merchant family.
        He entered the Moscow School of Painting at fourteen and showed such
        precocious talent that he was made a full member of the Imperial
        Academy by the age of twenty-four. His early work was competent but
        conventional; his great breakthrough came in 1871 when he exhibited
        "The Rooks Have Come Back" -- a painting of bare birch trees against
        a pale grey-violet late-winter sky, with a church and village visible
        across a field, and rooks returning to nest in the still-bare branches.
        The painting was immediately recognized as transformative: it was the
        first time a Russian landscape had achieved genuine lyrical emotion
        through the specific observation of a specific season in a specific
        place, rather than through Italianate idealization.

        SAVRASOV\'S FOUR TECHNICAL AND EMOTIONAL SIGNATURES:

        1. HORIZONTAL ATMOSPHERIC MIST LAYERING: Savrasov\'s skies are not
           painted as a simple gradient from blue to light, but as a series
           of horizontal atmospheric layers -- subtle bands of different
           luminance and hue that record the actual optical structure of the
           lower atmosphere on a damp late-winter day. The layers are most
           visible near the horizon, where water vapor, fog, and distance
           interact to create a succession of pale grays, violets, and
           ochers that are unmistakably Russian and unmistakably Savrasov.
           No prior 19th-century Russian landscape painter had rendered
           this horizontal layering with such meteorological precision.

        2. EARLY SPRING COOL-GREY LIGHT: The specific color of Russian late-
           February and early-March light -- after the coldest grey of deep
           winter but before the warmth of spring -- is a luminous, slightly
           violet-toned grey that Savrasov captured better than any of his
           successors. It is not the blue-grey of deep shadow, not the
           golden-grey of autumn -- it is the particular temperature of
           light filtered through cloud and residual winter haze, carrying
           a hint of the sky\'s violet and the earth\'s ochre simultaneously.
           Isaac Levitan, who learned directly from Savrasov, described his
           teacher\'s grey as "full of color, though seemingly colorless."

        3. BARE-BRANCH PRECISION AGAINST SKY: Savrasov\'s most technically
           demanding passages are the bare birch and alder branches silhouetted
           against his pale skies. These are not decorative, impressionistic
           gestures: they are specific, botanically accurate renderings of how
           branches fork and taper. The branches are the sharpest, most
           defined elements in his otherwise atmospheric paintings, and they
           function as the emotional spine of the composition -- the proof
           that the artist has seen this specific tree in this specific field.

        4. WARM STRAW HORIZON BLEEDS: Despite the cool, muted dominant tone,
           Savrasov\'s lower zones carry a subtle warmth -- the yellow-ocher
           of snow-covered stubble fields, the raw sienna of distant earth
           where the snow has melted in patches, the warm amber of dead
           grass at the field margins. This warm note in the lower zone
           creates a temperature gradient from the cool sky to the warm earth
           that is the structural color signature of the lyrical landscape.

        LEGACY: Savrasov taught Isaac Levitan and Konstantin Korovin at the
        Moscow School. Levitan described him as "the father of Russian lyrical
        landscape" and his influence on the Peredvizhniki landscape tradition
        is second only to Shishkin\'s. His masterwork "The Rooks Have Come Back"
        remains the single most emotionally recognized landscape in Russian art.

        Stage 1 HORIZONTAL ATMOSPHERIC MIST BANDING (Layered Atmosphere):
        Apply elongated HORIZONTAL uniform filter to all channels:
          kernel_shape = (2*mist_vwidth+1, 2*mist_hwidth+1) -- wide in x, narrow in y
          C_mist = uniform_filter(C, size=kernel_shape)
        Blend toward mist version: C1 = C + (C_mist - C) * mist_strength
        The horizontal kernel (long in x, short in y) averages local color over
        wide horizontal bands, creating the layered atmospheric bands visible in
        Savrasov\'s skies. The very narrow vertical dimension (mist_vwidth ~ 2)
        preserves vertical structure (trunks, branches) while horizontalizing
        the atmosphere.
        NOVEL: (a) HORIZONTAL UNIFORM FILTER for atmosphere -- the shishkin
        pass (s281) uses VERTICAL filter (22:2 height:width ratio) for bark grain.
        This pass uses the TRANSPOSED kernel orientation (horizontal: ~1:20 ratio)
        for layered atmospheric banding. No prior pass applies a horizontal-dominant
        uniform filter. The two passes are geometric complements: shishkin models
        vertical texture (bark), savrasov models horizontal texture (atmosphere).

        Stage 2 EARLY SPRING COOL-GREY PUSH IN MID-LUMINANCE (Savrasov Grey):
        After mist, compute luminance L1 of C1.
        In mid-luminance zone (mid_lo < L1 < mid_hi), push toward Savrasov grey
        (mid_r/g/b -- cool blue-grey with slight violet undertone):
          mid_mask = smoothstep(L1, mid_lo, mid_lo+0.08) * smoothstep(mid_hi+0.08, mid_hi, L1)
        (bell-shaped gate centered in the midtone range)
          C2 = C1 + (mid_color - C1) * mid_mask * mid_strength
        NOVEL: (b) MID-LUMINANCE BELL-GATE COLOR PUSH -- prior zone operations
        use either a step threshold (bright/dark cutoff), a soft ramp (shadow
        softness), or absolute luminance above/below a threshold. This pass uses
        a bell-shaped smooth gate: full effect only in the middle of the luminance
        range, falling off at both brighter and darker extremes. The bell shape
        (product of two opposing smoothstep functions) is distinct from all prior
        masking techniques. The target -- mid-luminance rather than shadow or
        highlight -- matches the specific observation that Savrasov\'s characteristic
        grey is a mid-value, not a shadow or highlight, color.

        Stage 3 BARE BRANCH CONTRAST RECOVERY (Vertical-Gradient Sharpening):
        The mist of Stage 1 softens all details. Recover branch detail by
        selectively sharpening where the VERTICAL GRADIENT is strongest:
          Gy = GaussianDerivative(L2, sigma=branch_sigma, order=[1, 0])
          |Gy| identifies horizontal edges -- the outlines of branches against sky
        Build branch_edge_mask from high-|Gy| pixels:
          branch_edge_mask = clip(|Gy| / percentile(|Gy|, branch_percentile), 0, 1)
        Apply unsharp mask to C2 in high-|Gy| zones:
          C_sharp = C2 + (C2 - GaussianFilter(C2, branch_sharp_sigma)) * branch_sharp
          C3 = C2 + (C_sharp - C2) * branch_edge_mask
        NOVEL: (c) VERTICAL GRADIENT (Gy) AS BRANCH-DETECTION GATE -- the
        vertical component of the spatial gradient (Gy = dL/dy) is maximized at
        HORIZONTAL edges: the bottom of a sky region touching the top of a branch
        cluster, or the outline of a branch crossing the pale sky. These are
        precisely the horizontal-edge features that define bare tree branches
        against a sky. Prior passes use gradient MAGNITUDE (total edge strength)
        without decomposing into directional components. This pass isolates the
        y-component specifically, targeting horizontal-edge features rather than
        all edges. The decomposition into Gx vs Gy components is novel.

        Stage 4 WARM STRAW HORIZON BLEED (Lower-Zone Ochre Push):
        In the spatial lower zone of the canvas (Yn > horizon_zone -- lower X%
        of image height), identify low-saturation pixels:
          S = (C_max - C_min) / max(C_max, 1e-6)
          S_smooth = GaussianFilter(S, sigma=horizon_sat_sigma)
          low_sat_mask = clip(1 - S_smooth / horizon_sat_thresh, 0, 1)
        Combine with spatial lower-zone mask:
          zone_mask = clip((Yn - horizon_zone) / (1 - horizon_zone), 0, 1)
          horizon_mask = zone_mask * low_sat_mask
        Push toward warm straw-ochre (horizon_r/g/b -- yellow-ocher):
          C4 = C3 + (horizon_color - C3) * horizon_mask * horizon_strength
        NOVEL: (d) SPATIAL LOWER-ZONE × SATURATION GATE -- the shishkin pass
        (s281) used desaturation-only gate (no spatial constraint). This pass
        combines a SPATIAL constraint (lower zone of canvas) with a SATURATION
        gate: only low-saturation pixels in the lower zone receive the ochre push.
        This confines the warm ochre to where it belongs in Savrasov\'s landscapes:
        the distant snow-covered fields (desaturated + lower canvas zone), not the
        warm-colored foreground earth or the saturated mid-tones. The spatial×
        saturation product gate is distinct from all prior zone combinations.
        """
        print("    Savrasov Lyrical Mist pass (193rd mode)...")

        import numpy as _np
        from scipy.ndimage import uniform_filter as _uf, gaussian_filter as _gf

        canvas = self.canvas
        H, W = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        # Stage 1: Horizontal atmospheric mist banding
        mh = max(int(mist_hwidth), 1)
        mv = max(int(mist_vwidth), 1)
        kx = 2 * mh + 1
        ky = 2 * mv + 1
        R_mist = _uf(R, size=(ky, kx)).astype(_np.float32)
        G_mist = _uf(G, size=(ky, kx)).astype(_np.float32)
        B_mist = _uf(B, size=(ky, kx)).astype(_np.float32)
        ms = float(mist_strength)
        R1 = _np.clip(R  + (R_mist - R)  * ms, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G  + (G_mist - G)  * ms, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B  + (B_mist - B)  * ms, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Early spring cool-grey push in mid-luminance (bell gate)
        L1 = (0.299 * R1 + 0.587 * G1 + 0.114 * B1).astype(_np.float32)
        ml = float(mid_lo)
        mh_ = float(mid_hi)
        band = max(0.08, (mh_ - ml) * 0.25)
        lo_ramp  = _np.clip((L1 - ml)  / max(band, 1e-5), 0.0, 1.0).astype(_np.float32)
        hi_ramp  = _np.clip((mh_ - L1) / max(band, 1e-5), 0.0, 1.0).astype(_np.float32)
        mid_mask = (lo_ramp * hi_ramp).astype(_np.float32)
        midstr   = float(mid_strength)
        mr_, mg_, mb_ = float(mid_r), float(mid_g), float(mid_b)
        R2 = _np.clip(R1 + (mr_ - R1) * mid_mask * midstr, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (mg_ - G1) * mid_mask * midstr, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (mb_ - B1) * mid_mask * midstr, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Bare branch contrast recovery (vertical-gradient y-component sharpening)
        L2 = (0.299 * R2 + 0.587 * G2 + 0.114 * B2).astype(_np.float32)
        bsig = max(float(branch_sigma), 0.3)
        Gy = _np.abs(_gf(L2, sigma=bsig, order=[1, 0])).astype(_np.float32)
        bp = float(branch_percentile)
        gy_scale = max(float(_np.percentile(Gy, bp)), 1e-6)
        branch_edge_mask = _np.clip(Gy / gy_scale, 0.0, 1.0).astype(_np.float32)

        bsharp_sig = max(float(branch_sharp_sigma), 0.2)
        R2b = _gf(R2, sigma=bsharp_sig).astype(_np.float32)
        G2b = _gf(G2, sigma=bsharp_sig).astype(_np.float32)
        B2b = _gf(B2, sigma=bsharp_sig).astype(_np.float32)
        bsharp = float(branch_sharp)
        R_sharp = _np.clip(R2 + (R2 - R2b) * bsharp, 0.0, 1.0).astype(_np.float32)
        G_sharp = _np.clip(G2 + (G2 - G2b) * bsharp, 0.0, 1.0).astype(_np.float32)
        B_sharp = _np.clip(B2 + (B2 - B2b) * bsharp, 0.0, 1.0).astype(_np.float32)
        R3 = _np.clip(R2 + (R_sharp - R2) * branch_edge_mask, 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G2 + (G_sharp - G2) * branch_edge_mask, 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B2 + (B_sharp - B2) * branch_edge_mask, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Warm straw horizon bleed (lower-zone × saturation gate)
        Yn = _np.linspace(0.0, 1.0, H, dtype=_np.float32)[:, _np.newaxis]
        hz = float(horizon_zone)
        zone_mask = _np.clip((Yn - hz) / max(1.0 - hz, 0.01), 0.0, 1.0).astype(_np.float32)
        zone_mask = _np.broadcast_to(zone_mask, (H, W)).astype(_np.float32)

        C3_max = _np.maximum(_np.maximum(R3, G3), B3).astype(_np.float32)
        C3_min = _np.minimum(_np.minimum(R3, G3), B3).astype(_np.float32)
        S3 = _np.where(C3_max > 1e-6, (C3_max - C3_min) / (C3_max + 1e-6),
                       _np.zeros_like(C3_max)).astype(_np.float32)
        hsat_sig = max(float(horizon_sat_sigma), 0.5)
        S3_smooth = _gf(S3, sigma=hsat_sig).astype(_np.float32)
        hst = max(float(horizon_sat_thresh), 1e-4)
        low_sat_mask = _np.clip(1.0 - S3_smooth / hst, 0.0, 1.0).astype(_np.float32)
        horizon_mask = (zone_mask * low_sat_mask).astype(_np.float32)

        hstr = float(horizon_strength)
        hr_, hg_, hb_ = float(horizon_r), float(horizon_g), float(horizon_b)
        R4 = _np.clip(R3 + (hr_ - R3) * horizon_mask * hstr, 0.0, 1.0).astype(_np.float32)
        G4 = _np.clip(G3 + (hg_ - G3) * horizon_mask * hstr, 0.0, 1.0).astype(_np.float32)
        B4 = _np.clip(B3 + (hb_ - B3) * horizon_mask * hstr, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R4 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G4 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B4 - B) * op, 0.0, 1.0).astype(_np.float32)

        mid_px     = int((mid_mask     > 0.05).sum())
        branch_px  = int((branch_edge_mask > 0.10).sum())
        horizon_px = int((horizon_mask > 0.05).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Savrasov Lyrical Mist complete "
              f"(mid_px={mid_px}, branch_px={branch_px}, horizon_px={horizon_px})")

'''

# ── Append both passes to stroke_engine.py (after last method) ───────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8-sig") as f:
    src = f.read()

# Verify neither pass already exists
assert "paint_contre_jour_rim_pass" not in src, \
    "paint_contre_jour_rim_pass already exists in stroke_engine.py"
assert "savrasov_lyrical_mist_pass" not in src, \
    "savrasov_lyrical_mist_pass already exists in stroke_engine.py"

# Append to end of file
with open(SE_PATH, "a", encoding="utf-8") as f:
    f.write(CONTRE_JOUR_RIM_PASS)
    f.write(SAVRASOV_LYRICAL_MIST_PASS)

print("stroke_engine.py patched: paint_contre_jour_rim_pass (s282 improvement)"
      " + savrasov_lyrical_mist_pass (193rd mode) appended.")
