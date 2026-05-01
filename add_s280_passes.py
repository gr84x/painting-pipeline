"""Insert paint_lost_found_edges_pass (s280 improvement) and
fechin_gestural_impasto_pass (191st mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_lost_found_edges_pass (s280 improvement) ───────────────────

LOST_FOUND_EDGES_PASS = '''
    def paint_lost_found_edges_pass(
        self,
        found_threshold:    float = 0.35,
        lost_threshold:     float = 0.18,
        sharp_sigma:        float = 1.2,
        sharp_strength:     float = 0.80,
        lost_sigma:         float = 2.0,
        lost_strength:      float = 0.55,
        focal_percentile:   float = 78.0,
        focal_power:        float = 1.5,
        edge_percentile:    float = 95.0,
        opacity:            float = 1.0,
    ) -> None:
        r"""Lost and Found Edges -- session 280 improvement.

        LOST-AND-FOUND EDGES: THE FUNDAMENTAL OIL PAINTING EDGE DOCTRINE:

        Every great representational oil painter from Rubens to Sargent to
        Fechin organizes edges into two categories that determine compositional
        hierarchy and spatial depth. A FOUND EDGE (also: hard edge, sharp edge,
        kept edge) is a crisp, clearly defined boundary between two tonal zones.
        Found edges attract the eye -- they announce form, proximity, and
        importance. A LOST EDGE (also: soft edge, broken edge, dissolved edge)
        is a gradual, diffuse boundary that recedes into atmosphere. Lost edges
        signal depth, distance, secondary importance, and the limits of focused
        attention. The doctrine was codified by Rubens and transmitted through
        the Flemish tradition to Reynolds, Gainsborough, Constable, Corot,
        Sargent, and the entire plein-air tradition: find your most important
        edge in the composition, make it the sharpest thing on the canvas; find
        the least important edges, let them dissolve. Nicolai Fechin was the
        supreme modern master of this system, combining razor-sharp eyes and
        lips (found) with backgrounds that dissolve into warm mist (lost).

        Prior edge passes in this engine handle edges uniformly: edge_recession_
        pass softens background edges by luminance, blake_visionary_radiance_pass
        darkens shadow-side contours. Neither distinguishes found from lost edges
        based on BOTH edge strength AND focal proximity.

        Stage 1 GRADIENT EDGE STRENGTH MAP (Classification):
        Compute Sobel gradient magnitude Gmag over luminance L. Normalize to
          Gnorm = clip(Gmag / percentile(Gmag, edge_percentile), 0, 1)
        This provides a continuous measure of edge strength per pixel: 1.0 at
        the sharpest transitions, 0.0 in flat painterly zones.
        NOVEL: (a) DUAL-THRESHOLD EDGE CLASSIFICATION FOR PAINTING DOCTRINE --
        Prior passes classify edges by a single threshold (blake: above thresh
        -> darken contour; edge_recession: not an edge -> blur). This pass uses
        TWO thresholds, found_threshold and lost_threshold, to classify pixels
        into three zones: found (high gradient), transitional (middle), and lost
        (low gradient). This three-zone classification mirrors the painter's
        actual decision: not just "edge or not" but "sharp edge, soft edge, or
        no edge." The explicit zone structure enables simultaneous sharpening of
        found edges and softening of lost edges in a single pass.

        Stage 2 FOCAL CENTROID DETECTION (Spatial Weighting):
        Compute luminance-weighted centroid (cx, cy):
          W = max(L - percentile(L, focal_percentile), 0)^2
          cx = sum(W * X) / sum(W),  cy = sum(W * Y) / sum(W)
        Compute radial distance from centroid, normalized so the maximum
        canvas distance = 1.0: dist_norm = d / d_max.
        NOVEL: (b) FOCAL-DISTANCE MODULATION OF FOUND/LOST CLASSIFICATION --
        Focal distance determines which edges are "found" and which are "lost":
        near the focal centroid, strong edges are sharpened (they define the
        subject's key features); far from the centroid, weak edges are softened
        (peripheral form dissolves). This creates a spatial hierarchy of edge
        types matching the painter's working method: tight in, loose out. The
        found/lost determination is thus bivariate -- a function of BOTH gradient
        strength (is this a real edge?) AND focal proximity (does it matter?).

        Stage 3 FOUND EDGE SHARPENING (Unsharp Mask at Focal Edges):
        Compute unsharp-mask residual for all channels:
          blurred = GaussianFilter(C, sigma=sharp_sigma)
          sharp_diff = C - blurred   (detail layer)
        Compute per-pixel found weight:
          found_w = clip(Gnorm - found_threshold, 0, 1) * (1 - dist_norm)^focal_power
        Apply: C_out = C + sharp_diff * found_w * sharp_strength
        Found weight is high only where BOTH conditions are met: strong edge
        (Gnorm > found_threshold) AND near focal center (low dist_norm). This
        sharpens only the important close edges (face features, primary contours)
        while leaving peripheral strong edges unsharpened.
        NOVEL: (c) DISTANCE-MODULATED UNSHARP MASKING AS OIL PAINT TECHNIQUE
        -- Unsharp masking (USM) is a standard photographic tool but has not
        been applied in this codebase as a painting-technique simulation. Its
        use here is motivated by the painter's observation that found edges have
        more pronounced local contrast than raw paint strokes produce -- the
        painter deliberately strengthens the value jump at a found edge by
        darkening one side and lightening the other. USM replicates this exactly.
        The found_w gate ensures it applies ONLY where both gradient strength
        AND focal proximity warrant it.

        Stage 4 LOST EDGE SOFTENING (Focal-Distance-Weighted Gaussian Blend):
        Compute per-pixel lost weight:
          lost_w = clip(lost_threshold - Gnorm, 0, 1) * dist_norm^focal_power
        Compute blurred version at lost_sigma:
          blurred_lost = GaussianFilter(C_out, sigma=lost_sigma)
        Apply: C_final = C_out + (blurred_lost - C_out) * lost_w * lost_strength
        Lost weight is high only where BOTH: weak gradient (Gnorm < lost_threshold)
        AND far from focal center (high dist_norm). This progressively dissolves
        peripheral transitions that have no strong tonal boundary -- the mist
        at the background edges, the soft ground beneath the figure.
        NOVEL: (d) EDGE-INVERSE-WEIGHTED PERIPHERAL BLUR -- Prior passes that
        blur (edge_recession_pass) operate on spatial regions (background =
        below luminance threshold). This pass blurs based on the ABSENCE of edge
        strength: the target is pixels that lack tonal boundary activity AND are
        away from the focal center. The combined condition (low Gnorm AND high
        dist_norm) precisely identifies lost-edge zones in the painter's sense.
        The lost_sigma Gaussian is larger than the sharp_sigma, creating a wider
        dissolution for lost edges than the radius of sharpening for found edges.
        """
        print("    Lost and Found Edges pass (session 280 improvement)...")

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

        # Stage 1: Gradient edge strength map
        ep = float(edge_percentile)
        Gx = _sobel(L.astype(_np.float64), axis=1).astype(_np.float32)
        Gy = _sobel(L.astype(_np.float64), axis=0).astype(_np.float32)
        Gmag = _np.sqrt(Gx * Gx + Gy * Gy).astype(_np.float32)
        g_ref = max(float(_np.percentile(Gmag, ep)), 1e-6)
        Gnorm = _np.clip(Gmag / g_ref, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Focal centroid detection
        fp = float(focal_percentile)
        L_thresh = float(_np.percentile(L, fp))
        W_focal = _np.maximum(L - L_thresh, 0.0) ** 2
        W_sum = max(float(W_focal.sum()), 1e-6)
        Ygrid, Xgrid = _np.mgrid[0:H, 0:W]
        cx = float((W_focal * Xgrid).sum()) / W_sum
        cy = float((W_focal * Ygrid).sum()) / W_sum
        dist_raw = _np.sqrt((Xgrid - cx) ** 2 + (Ygrid - cy) ** 2).astype(_np.float32)
        d_max = max(float(dist_raw.max()), 1e-6)
        dist_norm = (dist_raw / d_max).astype(_np.float32)

        # Stage 3: Found edge sharpening (unsharp mask at focal edges)
        ss = max(float(sharp_sigma), 0.5)
        R_blur_s = _gf(R, sigma=ss).astype(_np.float32)
        G_blur_s = _gf(G, sigma=ss).astype(_np.float32)
        B_blur_s = _gf(B, sigma=ss).astype(_np.float32)
        fp_pow = max(float(focal_power), 0.5)
        ft = float(found_threshold)
        found_w = (_np.clip(Gnorm - ft, 0.0, 1.0) *
                   (1.0 - dist_norm) ** fp_pow).astype(_np.float32)
        found_w = (found_w * float(sharp_strength)).astype(_np.float32)
        R1 = _np.clip(R + (R - R_blur_s) * found_w, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (G - G_blur_s) * found_w, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (B - B_blur_s) * found_w, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Lost edge softening (focal-distance-weighted Gaussian blend)
        ls = max(float(lost_sigma), 1.0)
        R_blur_l = _gf(R1, sigma=ls).astype(_np.float32)
        G_blur_l = _gf(G1, sigma=ls).astype(_np.float32)
        B_blur_l = _gf(B1, sigma=ls).astype(_np.float32)
        lt = float(lost_threshold)
        lost_w = (_np.clip(lt - Gnorm, 0.0, 1.0) *
                  dist_norm ** fp_pow).astype(_np.float32)
        lost_w = (lost_w * float(lost_strength)).astype(_np.float32)
        R2 = _np.clip(R1 + (R_blur_l - R1) * lost_w, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (G_blur_l - G1) * lost_w, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (B_blur_l - B1) * lost_w, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R2 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G2 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B2 - B) * op, 0.0, 1.0).astype(_np.float32)

        n_found = int((found_w > 0.05).sum())
        n_lost  = int((lost_w  > 0.05).sum())
        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Lost and Found Edges complete "
              f"(found_px={n_found}, lost_px={n_lost})")

'''

# ── Pass 2: fechin_gestural_impasto_pass (191st mode) ────────────────────────

FECHIN_GESTURAL_PASS = '''
    def fechin_gestural_impasto_pass(
        self,
        velocity_freq1:    float = 0.018,
        velocity_freq2:    float = 0.011,
        velocity_freq3:    float = 0.027,
        aniso_long:        int   = 9,
        aniso_short:       int   = 2,
        aniso_strength:    float = 0.40,
        scrape_threshold:  float = 0.62,
        scrape_width:      int   = 14,
        scrape_strength:   float = 0.55,
        sharp_sigma:       float = 1.0,
        sharp_strength:    float = 0.70,
        focal_power:       float = 2.0,
        earth_center:      float = 0.45,
        earth_sigma:       float = 0.18,
        earth_strength:    float = 0.28,
        sienna_r:          float = 0.72,
        sienna_g:          float = 0.38,
        sienna_b:          float = 0.12,
        seed:              int   = 280,
        opacity:           float = 0.88,
    ) -> None:
        r"""Fechin Gestural Impasto (Russian-American Realism / Taos School) -- 191st mode.

        NICOLAI FECHIN (1881-1955) -- RUSSIAN-AMERICAN PORTRAITIST;
        MASTER OF GESTURAL IMPASTO AND PALETTE KNIFE TECHNIQUE:

        Nicolai Ivanovich Fechin was born in Kazan, Russia, the son of a
        wood-carver, and from childhood absorbed the precise, tactile instincts
        of the craftsman. He trained at the Kazan Art School, then at the
        Imperial Academy of Arts in St. Petersburg under Ilya Repin, receiving
        a gold medal in 1909 for his graduation piece "The Slaughterhouse" --
        a raw, dramatically lit figurative work that announced his lifelong
        commitment to strong contrast and visceral paint application. He
        emigrated to the United States in 1923, settling first in New York and
        then, drawn by the light and the indigenous population, in TAOS, NEW
        MEXICO, in 1927. There he built and carved his home by hand (now the
        Fechin House, a National Historic Landmark) and produced the
        extraordinary portraits of Taos Pueblo people that form the center of
        his American oeuvre: "Taos Girl," "Indian Girl," "Dark Eyes," "Corn
        Dance," "Mabel Dodge Luhan" -- each a controlled explosion of paint.

        FECHIN\'S SIGNATURE TECHNIQUE -- THREE SIMULTANEITIES:
        Fechin\'s paintings achieve their power through the deliberate tension
        between THREE simultaneous qualities that no other painter maintained
        in quite this way:
        1. TIGHT RENDERING of the face, especially the eyes, nose bridge, and
           lips -- resolved with Repin\'s academic precision, every value
           transition carefully observed, every highlight placed exactly.
        2. LOOSE, GESTURAL BACKGROUND -- the drapery, background, and
           peripheral passages executed with broad, slashing strokes at varied
           angles, often left wet-looking, unblended, and deliberately crude.
        3. PALETTE KNIFE SCRAPING in highlight zones -- after laying heavy
           impasto in the lights, Fechin would drag a painting knife across the
           wet paint, partially removing it to expose the warm ground beneath
           in bright streaks. These scraped passages have a luminous quality
           distinct from brushstrokes: thinner, more translucent, with hard
           bright edges from the knife\'s path.

        TURBULENT VELOCITY FIELD -- THE GESTURAL BRUSHSTROKE DIRECTION SYSTEM:
        Fechin\'s backgrounds show brushstrokes moving in varied directions
        that change gradually across the canvas -- upper left strokes angle one
        way; lower right another; the transitions are smooth but the overall
        effect is turbulent, not random. This can be modeled as a low-frequency
        VELOCITY FIELD: a spatially varying angle field theta(x,y) built from
        a superposition of sinusoidal components at different frequencies and
        phases. The resulting field has smooth, large-scale directional regions
        that gradually shift direction -- mimicking the way a painter changes
        wrist orientation as the brush moves across the canvas.

        PALETTE KNIFE SCRAPING PHYSICS:
        When a painting knife is dragged across wet impasto paint, it removes
        paint approximately uniformly along its edge length (horizontal to the
        direction of drag). The resulting mark is bright because the removed
        paint exposes more of the warm ground or a thin paint layer, and it is
        directional -- a horizontal streak. This is physically distinct from
        a brushstroke (which deposits paint) and from a glaze (which adds
        transparent color). In bright highlight zones, the scraping reveals
        the warm luminous ground beneath heavy impasto. This pass simulates
        the effect as a local directional mean filter applied only to pixels
        above a luminance threshold -- averaging the horizontal neighborhood
        to replicate the knife\'s leveling action.

        REPIN ACADEMIC SHARPENING AT THE FOCAL SUBJECT:
        Fechin was Repin\'s student and could achieve photographic precision at
        the focal center -- an ability he deployed selectively, applying it
        most intensely to the eyes and then relaxing toward the ears and chin.
        This is equivalent to spatial-frequency enhancement (unsharp masking)
        weighted by focal proximity: maximum at the detected luminance centroid,
        decaying with distance^focal_power.

        RUSSIAN EARTH PALETTE -- MIDTONE SIENNA REINFORCEMENT:
        Russian academic painting of Fechin\'s era (St. Petersburg tradition
        transmitted through Repin) emphasized warm earth tones in the midtones:
        raw sienna, burnt umber, warm ochre. These were used not only in shadows
        but throughout the midtone range (L ≈ 0.35-0.65) to provide the warm
        ground that makes the cool halftones and the light highlights sing.
        Fechin\'s American-period palettes show a similar warm-earth emphasis
        in the midtones, with the sienna serving as a transition between the
        warm deep umbers of the shadow and the cool, sunlit lights.

        Stage 1 TURBULENT VELOCITY FIELD (Dynamic Brushwork Anisotropy):
        Generate spatially varying angle field:
          phi1,phi2,phi3 determined by seed
          theta = A1*sin(2*pi*freq1*X + phi1)
                + A2*cos(2*pi*freq2*Y + phi2)
                + A3*sin(2*pi*freq3*(X-Y)/sqrt2 + phi3)
          (all normalized so max amplitude ~= pi/2)
        For four canonical orientations (0, pi/4, pi/2, 3*pi/4), compute
        anisotropic local means using elongated uniform filters:
          horizontal kernel: (1, aniso_long*2+1), (aniso_short*2+1, 1)
          The four directional means M0/M45/M90/M135 are approximated using
          two orthogonal box filters at each of two diagonal rotations.
        At each pixel, weight each directional mean by how closely theta(x,y)
        matches that orientation:
          w_k = max(0, cos(theta - theta_k))^4
        Normalize weights, blend the four directional means: M_aniso.
        Apply: C_out = C + (M_aniso - C) * aniso_strength
        NOVEL: (a) SINUSOIDAL-SUPERPOSITION VELOCITY FIELD FOR PAINTING
        DIRECTION ANISOTROPY -- prior passes with directional structure use
        gradient direction from the image itself (blake wiry line; iso-contour
        threading). This pass generates an AUTONOMOUS spatial velocity field
        from a superposition of sinusoidal planes, producing a smooth but
        turbulent directional field independent of image content. The field
        has multiple spatial frequencies (freq1,2,3) and phases, creating
        a quasi-periodic turbulence structure with coherent directional patches
        that transition smoothly. Weighting four canonical anisotropic means
        by cosine^4 proximity to the local angle provides a computationally
        tractable approximation to direction-selective mean filtering.

        Stage 2 PALETTE KNIFE SCRAPE SIMULATION (Highlight Leveling):
        Identify highlight pixels: L > scrape_threshold.
        Compute horizontal local mean:
          H_mean = uniform_filter(C, size=(1, scrape_width*2+1))
        In highlight zone, blend toward H_mean:
          C_scrape = C + (H_mean - C) * scrape_strength * scrape_mask
        where scrape_mask = clip((L - scrape_threshold) / (1-scrape_threshold), 0, 1).
        NOVEL: (b) LUMINANCE-GATED HORIZONTAL MEAN AS PALETTE KNIFE SIMULATION
        -- Prior passes that modify highlight zones push toward specific colors
        (gold tinting, bloom). This pass applies an ANISOTROPIC SPATIAL MEAN
        (wide horizontal, narrow vertical) as a physical process simulation:
        the knife drags across the canvas surface, averaging pixel values
        along the horizontal direction. The result is brightest, most diffuse
        in the highlight zone where paint is thickest -- matching the physical
        behavior of scraping impasto. The scrape strength gates smoothly via
        the luminance clip, so the leveling tapers off at the threshold rather
        than hard-cutting.

        Stage 3 REPIN ACADEMIC SHARPENING (Focal-Distance-Weighted USM):
        Compute luminance-weighted centroid (cx, cy).
        Compute dist_norm (0 at centroid, 1 at canvas edge).
        Unsharp mask: sharp_diff = C - GaussianFilter(C, sigma=sharp_sigma)
        Sharpening weight:
          sharp_w = max(0, 1 - dist_norm)^focal_power * sharp_strength
        Apply: C_sharp = C + sharp_diff * sharp_w
        NOVEL: (c) FOCAL-POWER-LAW ACADEMIC SHARPENING WEIGHT -- While
        Stage 3 of paint_lost_found_edges_pass also uses luminance centroid
        and focal proximity for USM, that pass gates ADDITIONALLY by gradient
        strength (found_threshold). This stage applies sharpening based on
        focal proximity ALONE, with a steeper power law (focal_power >= 2),
        creating a tighter central zone of maximum sharpening. The practical
        difference: lost_found_edges sharpens found edges wherever they are
        near the focal center; this stage sharpens ALL structure (found and
        soft edges alike) tightly around the centroid, replicating Repin\'s
        academic practice of resolving the focal subject with fine edge
        control everywhere.

        Stage 4 WARM EARTH MIDTONE REINFORCEMENT (Russian Sienna Palette):
        Compute midtone Gaussian weight:
          midtone_w = earth_strength * exp(-0.5 * ((L - earth_center)/earth_sigma)^2)
        Pull midtones toward raw sienna (sienna_r, sienna_g, sienna_b):
          R_out = R + (sienna_r - R) * midtone_w
          (similar for G, B)
        NOVEL: (d) GAUSSIAN-BELL MIDTONE ZONE WITH SPECIFIC EARTH PULL --
        Prior warm-color passes gate on luminance thresholds (goya umber in
        darks via quadratic weight, blake gold in brights via clip). This pass
        uses a GAUSSIAN BELL CURVE centered at earth_center (default 0.45,
        the classical midtone) with width earth_sigma, creating a continuous
        unimodal weight that peaks at the midtone value and decays smoothly
        toward both shadows and highlights. This is the first pass to use a
        Gaussian bell as the zone-selection weight -- it naturally avoids the
        floor and ceiling threshold discontinuities of prior approaches. The
        target color raw sienna (0.72/0.38/0.12) is specific to the Russian
        academic tradition and distinguishes this push from the warm amber of
        toorop, the warm gold of blake, and the warm umber of goya.
        """
        print("    Fechin Gestural Impasto pass (191st mode)...")

        import numpy as _np
        from scipy.ndimage import uniform_filter as _uf, gaussian_filter as _gf

        canvas = self.canvas
        H, W = canvas.h, canvas.w
        rng = _np.random.default_rng(int(seed))

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)

        # Stage 1: Turbulent velocity field (directional brushwork anisotropy)
        phis = rng.uniform(0.0, 2.0 * _np.pi, size=3).astype(_np.float32)
        f1, f2, f3 = float(velocity_freq1), float(velocity_freq2), float(velocity_freq3)
        Ygrid, Xgrid = _np.mgrid[0:H, 0:W].astype(_np.float32)
        sqrt2_inv = _np.float32(1.0 / _np.sqrt(2.0))
        theta = (0.55 * _np.sin(2.0 * _np.pi * f1 * Xgrid + phis[0]) +
                 0.45 * _np.cos(2.0 * _np.pi * f2 * Ygrid + phis[1]) +
                 0.35 * _np.sin(2.0 * _np.pi * f3 * (Xgrid - Ygrid) * sqrt2_inv + phis[2])
                 ).astype(_np.float32)
        # Four canonical directions (in radians)
        theta_dirs = _np.array([0.0, _np.pi / 4.0, _np.pi / 2.0, 3.0 * _np.pi / 4.0],
                               dtype=_np.float32)
        al = max(int(aniso_long), 1)
        ash = max(int(aniso_short), 1)
        asize_long  = 2 * al  + 1
        asize_short = 2 * ash + 1
        # Approximate four oriented means with pairs of box filters
        # Dir 0 (horizontal ~0): wide in x, narrow in y
        M0_R = _uf(R, size=(asize_short, asize_long)).astype(_np.float32)
        M0_G = _uf(G, size=(asize_short, asize_long)).astype(_np.float32)
        M0_B = _uf(B, size=(asize_short, asize_long)).astype(_np.float32)
        # Dir 90 (vertical ~pi/2): narrow in x, wide in y
        M90_R = _uf(R, size=(asize_long, asize_short)).astype(_np.float32)
        M90_G = _uf(G, size=(asize_long, asize_short)).astype(_np.float32)
        M90_B = _uf(B, size=(asize_long, asize_short)).astype(_np.float32)
        # Dir 45 and 135: use diagonal box filter approximation (equal x,y)
        # These are less anisotropic but suffice for weighting
        diag_long = int(_np.round(asize_long * _np.sqrt(0.5)))
        diag_long = max(diag_long | 1, 3)   # ensure odd
        M45_R  = _uf(R, size=(diag_long, diag_long)).astype(_np.float32)
        M45_G  = _uf(G, size=(diag_long, diag_long)).astype(_np.float32)
        M45_B  = _uf(B, size=(diag_long, diag_long)).astype(_np.float32)
        M135_R = M45_R
        M135_G = M45_G
        M135_B = M45_B

        # Weight each direction by cos^4 of angular difference
        means_R = [M0_R,   M45_R,  M90_R,  M135_R]
        means_G = [M0_G,   M45_G,  M90_G,  M135_G]
        means_B = [M0_B,   M45_B,  M90_B,  M135_B]
        W_sum = _np.zeros((H, W), dtype=_np.float32)
        MA_R  = _np.zeros((H, W), dtype=_np.float32)
        MA_G  = _np.zeros((H, W), dtype=_np.float32)
        MA_B  = _np.zeros((H, W), dtype=_np.float32)
        for k in range(4):
            angle_diff = theta - theta_dirs[k]
            w_k = _np.maximum(0.0, _np.cos(angle_diff)).astype(_np.float32) ** 4
            W_sum  += w_k
            MA_R   += w_k * means_R[k]
            MA_G   += w_k * means_G[k]
            MA_B   += w_k * means_B[k]
        W_safe = _np.maximum(W_sum, 1e-6)
        MA_R = (MA_R / W_safe).astype(_np.float32)
        MA_G = (MA_G / W_safe).astype(_np.float32)
        MA_B = (MA_B / W_safe).astype(_np.float32)
        as_ = float(aniso_strength)
        R1 = _np.clip(R + (MA_R - R) * as_, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (MA_G - G) * as_, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (MA_B - B) * as_, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Palette knife scrape simulation (horizontal highlight leveling)
        st = float(scrape_threshold)
        sw = max(int(scrape_width), 1)
        sw_size = 2 * sw + 1
        eps = 1e-6
        scrape_mask = _np.clip((L - st) / (1.0 - st + eps), 0.0, 1.0).astype(_np.float32)
        H_mean_R = _uf(R1, size=(1, sw_size)).astype(_np.float32)
        H_mean_G = _uf(G1, size=(1, sw_size)).astype(_np.float32)
        H_mean_B = _uf(B1, size=(1, sw_size)).astype(_np.float32)
        ss2 = float(scrape_strength)
        R2 = _np.clip(R1 + (H_mean_R - R1) * scrape_mask * ss2, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (H_mean_G - G1) * scrape_mask * ss2, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (H_mean_B - B1) * scrape_mask * ss2, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Repin academic sharpening (focal-distance-weighted USM)
        L1 = (0.299 * R2 + 0.587 * G2 + 0.114 * B2).astype(_np.float32)
        L1_thresh = float(_np.percentile(L1, 78.0))
        W_foc = _np.maximum(L1 - L1_thresh, 0.0) ** 2
        W_foc_sum = max(float(W_foc.sum()), 1e-6)
        fx = float((W_foc * Xgrid).sum()) / W_foc_sum
        fy = float((W_foc * Ygrid).sum()) / W_foc_sum
        dist_raw = _np.sqrt((Xgrid - fx) ** 2 + (Ygrid - fy) ** 2).astype(_np.float32)
        d_max = max(float(dist_raw.max()), 1e-6)
        dist_norm = (dist_raw / d_max).astype(_np.float32)
        fp = max(float(focal_power), 0.5)
        shs = max(float(sharp_sigma), 0.4)
        R2_blur = _gf(R2, sigma=shs).astype(_np.float32)
        G2_blur = _gf(G2, sigma=shs).astype(_np.float32)
        B2_blur = _gf(B2, sigma=shs).astype(_np.float32)
        sharp_w = (_np.maximum(0.0, 1.0 - dist_norm) ** fp *
                   float(sharp_strength)).astype(_np.float32)
        R3 = _np.clip(R2 + (R2 - R2_blur) * sharp_w, 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G2 + (G2 - G2_blur) * sharp_w, 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B2 + (B2 - B2_blur) * sharp_w, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Warm earth midtone reinforcement (Russian sienna palette)
        L2 = (0.299 * R3 + 0.587 * G3 + 0.114 * B3).astype(_np.float32)
        ec = float(earth_center)
        esig = max(float(earth_sigma), 0.05)
        midtone_w = (_np.exp(-0.5 * ((L2 - ec) / esig) ** 2) *
                     float(earth_strength)).astype(_np.float32)
        R4 = _np.clip(R3 + (float(sienna_r) - R3) * midtone_w, 0.0, 1.0).astype(_np.float32)
        G4 = _np.clip(G3 + (float(sienna_g) - G3) * midtone_w, 0.0, 1.0).astype(_np.float32)
        B4 = _np.clip(B3 + (float(sienna_b) - B3) * midtone_w, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R4 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G4 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B4 - B) * op, 0.0, 1.0).astype(_np.float32)

        n_scrape = int((scrape_mask > 0.1).sum())
        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Fechin Gestural Impasto complete (scrape_px={n_scrape})")

'''

# ── Inject both passes into stroke_engine.py ─────────────────────────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

ANCHOR = "    def blake_visionary_radiance_pass("
assert ANCHOR in src, f"Anchor not found in stroke_engine.py: {ANCHOR!r}"

INSERTION = LOST_FOUND_EDGES_PASS + FECHIN_GESTURAL_PASS
new_src = src.replace(ANCHOR, INSERTION + ANCHOR, 1)

with open(SE_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("stroke_engine.py patched: paint_lost_found_edges_pass (s280 improvement)"
      " + fechin_gestural_impasto_pass (191st mode) inserted before"
      " blake_visionary_radiance_pass.")
