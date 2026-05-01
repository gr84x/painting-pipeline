"""Insert paint_crepuscular_ray_pass (s283 improvement) and
bierstadt_luminous_glory_pass (194th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_crepuscular_ray_pass (s283 improvement) ────────────────────

CREPUSCULAR_RAY_PASS = '''
    def paint_crepuscular_ray_pass(
        self,
        source_detect_sigma:  float = 20.0,
        source_top_fraction:  float = 0.60,
        n_rays:               int   = 7,
        ray_sharpness:        float = 3.0,
        ray_angular_noise:    float = 0.22,
        ray_color_r:          float = 0.95,
        ray_color_g:          float = 0.80,
        ray_color_b:          float = 0.45,
        dist_falloff:         float = 1.2,
        ray_strength:         float = 0.20,
        lum_gate:             float = 0.28,
        noise_seed:           int   = 283,
        opacity:              float = 0.80,
    ) -> None:
        r"""Crepuscular Ray Light Shafts -- s283 improvement.

        CREPUSCULAR RAYS IN PAINTING AND NATURE:

        Crepuscular rays (from Latin crepusculum -- twilight) are the visible
        shafts of sunlight that radiate from a partially obscured light source,
        most commonly the sun behind storm clouds, through gaps in a forest
        canopy, or at the low angles of dawn and dusk when atmospheric particles
        scatter the light into discrete beams. They are called crepuscular because
        they appear most vividly at the crepuscular hours of dawn and dusk, though
        they can occur at any time with the right atmospheric conditions. Their
        counterpart, "anticrepuscular rays," radiate from the anti-solar point on
        the opposite horizon.

        IN PAINTING: Crepuscular rays are one of the most powerful compositional
        tools available to the landscape painter. They:
        (1) Establish a light source direction even when the sun is not visible
        (2) Create dramatic diagonals that organize the picture plane
        (3) Give atmospheric substance -- they are only visible when the air
            contains haze, dust, smoke, or moisture, so they simultaneously
            communicate the presence of atmosphere
        (4) Connect earth and sky -- a ray that falls from above to illuminate
            a specific part of the landscape creates a "spotlight" effect that
            focuses the viewer's attention

        The technique was exploited most dramatically by Albert Bierstadt, whose
        Sierra Nevada and Rocky Mountain scenes regularly feature shafts of golden
        afternoon light breaking through storm clouds. J.M.W. Turner used it in
        his harbor and marine scenes. Claude Lorrain placed crepuscular rays in
        his harbor visions to create the "golden haze" quality that made his
        morning light compositions so distinctive.

        PRIOR PASSES AND NOVELTY:
        The existing improvement passes affect the canvas through:
        (a) Zone-based luminance/color operations (shadow_temperature,
            savrasov_lyrical_mist): these use spatial vertical zones or
            luminance thresholds but apply UNIFORM effects within those zones
        (b) Edge-based operations (contre_jour_rim, lost_found_edges): detect
            boundaries and apply effects to one or both sides of the boundary
        (c) Uniform surface effects (surface_grain, depth_atmosphere): apply
            over the entire canvas without a spatial anchor point

        No prior pass:
          (i)   DETECTS A SPECIFIC SOURCE POINT in the image (argmax of smoothed
                luminance, constrained to the top portion of the frame)
          (ii)  CONVERTS TO POLAR COORDINATES from that detected source point,
                computing per-pixel angle and radial distance
          (iii) APPLIES AN ANGULAR PERIODICITY -- a cosine function in angle
                space -- that produces discrete "ray lobes" radiating from the
                source point
          (iv)  COMBINES angular lobe mask × radial distance falloff ×
                luminance gate as a MULTIPLICATIVE chain

        This pass is the first to model directional radial light emission from
        a CONTENT-DETECTED source point. All prior "global" effects lack a
        geometric anchor; all prior edge effects anchor to BOUNDARIES rather than
        to a POINT.

        Stage 1 SOURCE DETECTION (Luminance Argmax in Bounded Zone):
        Compute grayscale luminance L = 0.299R + 0.587G + 0.114B.
        Gaussian smooth: L_sm = GaussianFilter(L, source_detect_sigma).
        Gate to the top source_top_fraction of the image height:
          L_sm[round(H*source_top_fraction):, :] = 0
        sy, sx = argmax(L_sm over H×W) -- detected source position.
        Constraining to the top portion ensures the detected source is a sky/sun
        region rather than a bright foreground element.
        NOVEL: (a) CONTENT-AWARE SOURCE POINT DETECTION via luminance argmax
        in a bounded zone. No prior pass detects a specific location in the
        canvas as a geometric anchor for subsequent per-pixel operations.

        Stage 2 POLAR COORDINATE TRANSFORMATION FROM SOURCE:
        Yg, Xg = meshgrid(0:H, 0:W) -- pixel position grids.
        dy = Yg - sy, dx = Xg - sx.
        angle = atan2(dy, dx)  -- per-pixel angle from source in [-π, π].
        dist  = sqrt(dy² + dx²).
        dist_norm = dist / sqrt(H² + W²).  -- normalized distance, [0,1].
        NOVEL: (b) POLAR COORDINATE FIELD CENTERED ON DETECTED SOURCE --
        the first per-pixel polar transformation in the engine, and the first
        use of atan2 (angular field) as a spatial coordinate for effect gating.

        Stage 3 ANGULAR RAY LOBE PATTERN (Directional beam synthesis):
        Add angular noise to break regularity:
          rng = RandomGenerator(noise_seed)
          angle_noise = rng.uniform(-ray_angular_noise, ray_angular_noise, (H,W))
          angle_noisy = angle + angle_noise
        Compute ray lobes: n_rays discrete positive lobes over [0, 2π]:
          ray_base = max(0, cos(n_rays * angle_noisy)) ** ray_sharpness
        cos(n * φ) completes n full cycles over 2π, giving n positive lobes
        (the "rays") separated by n negative lobes (the "shadow gaps").
        max(0,·)^sharpness concentrates the positive lobes: sharpness=1 gives
        wide, soft rays; sharpness=4+ gives narrow, defined shafts.
        NOVEL: (c) COSINE-BASED ANGULAR PERIODICITY for ray synthesis --
        the first angular-frequency operation in the engine, distinct from all
        prior directional operations (which use gradient direction as a feature
        detector, not as a basis for periodic pattern synthesis).

        Stage 4 RADIAL FALLOFF × LUMINANCE GATE:
        Distance falloff (rays brightest at source, fade with distance):
          ray_falloff = (1 - dist_norm) ** dist_falloff
        Luminance gate (rays only visible in non-dark regions):
          lum_gate_mask = clip((L - lum_gate) / (1 - lum_gate), 0, 1)
        Combined ray mask:
          ray_mask = ray_base * ray_falloff * lum_gate_mask
        NOVEL: (d) MULTIPLICATIVE COMBINATION: angular periodicity ×
        radial falloff × luminance gate -- three independent spatial
        functions (angular, radial, luminance) multiplied per-pixel.
        Prior passes chain at most two spatial functions.

        Stage 5 ADDITIVE WARM GOLDEN COMPOSITE:
        Apply ray_mask as additive warm light (ray_color_r/g/b):
          R_out = clip(R + ray_color_r * ray_mask * ray_strength, 0, 1)
        Composite at opacity:
          R_final = R + (R_out - R) * opacity
        """
        print("    Crepuscular Ray Light Shafts pass (session 283 improvement)...")

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

        # Stage 1: Source detection
        sigma = max(float(source_detect_sigma), 1.0)
        L_sm = _gf(L, sigma=sigma).astype(_np.float32)
        # Gate to top source_top_fraction of image
        gate_row = int(H * float(source_top_fraction))
        L_gated = L_sm.copy()
        L_gated[gate_row:, :] = 0.0
        sy, sx = _np.unravel_index(_np.argmax(L_gated), L_gated.shape)

        # Stage 2: Polar coordinates from source
        Yg, Xg = _np.mgrid[0:H, 0:W].astype(_np.float32)
        dy = Yg - float(sy)
        dx = Xg - float(sx)
        angle = _np.arctan2(dy, dx).astype(_np.float32)
        dist = _np.sqrt(dy * dy + dx * dx).astype(_np.float32)
        dist_max = max(float(_np.sqrt(H * H + W * W)), 1.0)
        dist_norm = _np.clip(dist / dist_max, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Angular ray lobe pattern with noise
        rng = _np.random.default_rng(int(noise_seed))
        ang_noise = rng.uniform(
            -float(ray_angular_noise), float(ray_angular_noise), (H, W)
        ).astype(_np.float32)
        angle_noisy = (angle + ang_noise).astype(_np.float32)

        n = max(int(n_rays), 1)
        sp = max(float(ray_sharpness), 0.5)
        ray_base = _np.maximum(
            0.0, _np.cos(n * angle_noisy).astype(_np.float32)
        ) ** sp

        # Stage 4: Radial falloff × luminance gate
        df = max(float(dist_falloff), 0.1)
        ray_falloff = ((1.0 - dist_norm) ** df).astype(_np.float32)

        lg = float(lum_gate)
        lum_denom = max(1.0 - lg, 1e-5)
        lum_gate_mask = _np.clip((L - lg) / lum_denom, 0.0, 1.0).astype(_np.float32)

        ray_mask = (ray_base * ray_falloff * lum_gate_mask).astype(_np.float32)

        # Stage 5: Additive warm golden composite
        rs = float(ray_strength)
        rr, rg, rb_ = float(ray_color_r), float(ray_color_g), float(ray_color_b)
        R_out = _np.clip(R + rr * ray_mask * rs, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + rg * ray_mask * rs, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + rb_ * ray_mask * rs, 0.0, 1.0).astype(_np.float32)

        op = float(opacity)
        R_final = _np.clip(R + (R_out - R) * op, 0.0, 1.0).astype(_np.float32)
        G_final = _np.clip(G + (G_out - G) * op, 0.0, 1.0).astype(_np.float32)
        B_final = _np.clip(B + (B_out - B) * op, 0.0, 1.0).astype(_np.float32)

        ray_px = int((ray_mask > 0.05).sum())

        out = raw.copy()
        out[:, :, 2] = (R_final * 255).astype(_np.uint8)
        out[:, :, 1] = (G_final * 255).astype(_np.uint8)
        out[:, :, 0] = (B_final * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Crepuscular Ray complete "
              f"(source=({sy},{sx}), n_rays={n_rays}, ray_px={ray_px})")

'''

# ── Pass 2: bierstadt_luminous_glory_pass (194th mode) ────────────────────────

BIERSTADT_LUMINOUS_GLORY_PASS = '''
    def bierstadt_luminous_glory_pass(
        self,
        sky_zone:            float = 0.38,
        sky_bright_lo:       float = 0.52,
        horizon_r:           float = 0.92,
        horizon_g:           float = 0.88,
        horizon_b:           float = 0.68,
        horizon_strength:    float = 0.34,
        zenith_fraction:     float = 0.16,
        zenith_dark_thresh:  float = 0.45,
        zenith_r:            float = 0.14,
        zenith_g:            float = 0.18,
        zenith_b:            float = 0.42,
        zenith_strength:     float = 0.38,
        mid_lo:              float = 0.38,
        mid_hi:              float = 0.75,
        mid_sat_thresh:      float = 0.55,
        mid_zone_lo:         float = 0.33,
        mid_zone_hi:         float = 0.70,
        amber_r:             float = 0.94,
        amber_g:             float = 0.74,
        amber_b:             float = 0.30,
        amber_strength:      float = 0.28,
        lower_zone:          float = 0.72,
        lower_dark_thresh:   float = 0.38,
        umber_r:             float = 0.44,
        umber_g:             float = 0.28,
        umber_b:             float = 0.14,
        umber_strength:      float = 0.30,
        opacity:             float = 0.88,
    ) -> None:
        r"""Bierstadt Luminous Glory (American Luminism / Hudson River School) -- 194th mode.

        ALBERT BIERSTADT (1830-1902) -- AMERICAN LUMINIST, HUDSON RIVER SCHOOL:

        Albert Bierstadt was born in Solingen, Germany in 1830 and emigrated
        with his family to New Bedford, Massachusetts at age two. He returned
        to Germany to study painting in Dusseldorf (1853-1857), where he absorbed
        the German Romantic landscape tradition -- dramatic chiaroscuro, theatrical
        lighting, and the monumental treatment of nature. He returned to America
        and joined the Clarence King survey expedition to the Rocky Mountains in
        1859, making hundreds of oil sketches and photographs on the trail. These
        sketches became the basis for his enormous studio canvases, some reaching
        6 × 10 feet, which made him the most commercially successful American
        painter of his era.

        BIERSTADT\'S FOUR PICTORIAL SYSTEMS:

        1. LUMINOUS HORIZON ARCHITECTURE -- SKY:
           Bierstadt\'s sky is not a simple gradient. It follows a specific luminance
           architecture: the ZENITH is the darkest sky zone, carrying deep ultramarine
           blue or near-black storm cloud grey; the sky BRIGHTENS moving downward toward
           the horizon line; the HORIZON ITSELF is the brightest zone -- warm cream,
           pale gold, or brilliant white -- as the low-angle sun light is scattered
           maximally through the atmospheric column. This zenith-dark / horizon-bright
           architecture is the inverse of what most painters and photographers render
           (where the sky darkens toward the horizon in flat daylight). It arises from
           two conditions: (a) the sun at a low angle near the horizon rather than
           overhead, and (b) storm clouds at mid-sky creating a dark midtone band with
           open sky visible near the horizon.

        2. WARM AMBER THEATRICAL HAZE -- MIDDLE DISTANCE:
           The most immediately identifiable Bierstadt color is the warm amber-golden
           haze that pervades his middle distance -- the zone between the near mountains
           and the sky, where dust, moisture, and late-afternoon light combine to create
           a luminous warm gold. This color is both atmospheric (the actual color of
           dust-laden air in late afternoon) and theatrical (he intensified it far
           beyond what photographs recorded). It is often described as "Bierstadt
           gold" and is the defining color of his mature style.

        3. COOL DEEP ZENITH / WARM GOLDEN HORIZON COLOR OPPOSITION:
           The opposition between the warm golden horizon and the cool dark zenith
           creates an extreme color temperature gradient across the sky that Bierstadt
           used as the dominant color tension in his paintings. This opposition also
           "frames" the warm middle-distance haze: the cool sky above and below the
           mountain makes the amber middle zone appear warmer by contrast.

        4. WARM UMBER FOREGROUND SHADOW ENRICHMENT:
           In his foreground shadows -- the patches of dark ground, rock, and forest
           floor in the near zone -- Bierstadt consistently applied a warm umber-
           sienna note rather than neutral grey. This warm shadow in the near zone
           mirrors the warm haze in the middle zone and creates a coherent "warm
           interior" light quality that makes his paintings glow from within, as if
           the entire scene were lit by a source of warm, golden light.

        Stage 1 LUMINOUS HORIZON UPLIFT (Sky zone bright-toward-horizon):
        Build sky_mask: smooth spatial gate for top sky_zone fraction of image.
        Within sky zone, build a horizon_weight: 0 at zenith (top), 1 at horizon
        (bottom of sky zone):
          horizon_weight = Yn_in_sky_fraction ** 1.8   (Yn_frac = 0 at top, 1 at bottom of sky)
        bright_mask: pixels in sky zone with L > sky_bright_lo.
        Push these pixels toward horizon_color weighted by horizon_weight:
          C1 = C + (horizon_color - C) * sky_mask * horizon_weight * bright_mask * horizon_strength
        NOVEL: (a) HORIZON-UPWARD LUMINANCE ARCHITECTURE WITHIN BOUNDED SKY ZONE --
        the horizon_weight increases DOWNWARD inside the sky zone (from top toward
        horizon). This models the specific Bierstadt sky structure where the bottom
        of the sky is brighter than the top. No prior pass applies a spatially-
        inverted weight WITHIN a bounded upper zone. Prior sky-related operations
        use uniform zone behavior or top-of-image darkening.

        Stage 2 COOL ULTRAMARINE ZENITH PUSH (Dark dramatic zenith):
        In the topmost zenith_fraction of image:
          zenith_mask = spatial gate (top zenith_fraction, soft boundary)
          dark_in_zenith = clip(1 - L / zenith_dark_thresh, 0, 1)
            (strong where L is small, zero where L > zenith_dark_thresh)
          zenith_mask_final = zenith_mask * dark_in_zenith
        Push toward deep ultramarine (zenith_r/g/b):
          C2 = C1 + (zenith_color - C1) * zenith_mask_final * zenith_strength
        NOVEL: (b) DARK-ZONE-IN-TOP-FRACTION COOL PUSH -- targets dark pixels
        specifically within the top spatial fraction. The combination (spatial top
        fraction) × (low luminance gate) produces a mask that activates only for
        dark areas in the top of the image -- the storm clouds and dark zenith sky.
        Stage 4 below applies the geometric INVERSE: dark areas in BOTTOM zone
        get a WARM push. The zenith-cool / foreground-warm duality is novel.

        Stage 3 WARM AMBER MIDDLE-DISTANCE THEATRICAL HAZE:
        Build mid_zone_mask: vertical spatial gate for mid_zone_lo < Yn < mid_zone_hi.
        Build lum_gate: bell-shaped in luminance (mid_lo < L < mid_hi).
        Build sat_gate: low saturation gate (S < mid_sat_thresh):
          S = (C_max - C_min) / max(C_max, 1e-6)
          sat_gate = clip(1 - S / mid_sat_thresh, 0, 1)
        Combined: amber_mask = mid_zone_mask * lum_gate * sat_gate
        Push toward amber (amber_r/g/b):
          C3 = C2 + (amber_color - C2) * amber_mask * amber_strength
        NOVEL: (c) TRIPLE-GATED MIDDLE HAZE: spatial zone × luminance bell ×
        saturation gate -- three independent conditions all required simultaneously.
        Stage 2 uses two conditions (spatial + luminance). The saturation gate is
        novel in this context: it ensures the amber push goes to areas with low
        saturation (desaturated atmospheric haze) but not to already-colored
        midtone objects (green trees, blue shadows). The triple gate prevents
        color contamination of already-saturated scene elements.

        Stage 4 LOWER ZONE WARM UMBER FOREGROUND SHADOW ENRICHMENT:
        Build lower_mask: spatial gate for bottom lower_zone fraction:
          lower_mask = clip((Yn - lower_zone) / (1 - lower_zone), 0, 1)
        Build dark_gate: gate for dark pixels:
          dark_gate = clip(1 - L / lower_dark_thresh, 0, 1)
        Combined: umber_mask = lower_mask * dark_gate
        Push toward warm umber (umber_r/g/b):
          C4 = C3 + (umber_color - C3) * umber_mask * umber_strength
        NOVEL: (d) DARK-IN-BOTTOM-ZONE WARM PUSH -- the geometric complement of
        Stage 2 (dark+top=cool). Together, stages 2 and 4 implement:
          dark + top    → cool ultramarine  (storm cloud zenith)
          dark + bottom → warm umber        (foreground earth shadow)
        This "dark-zone temperature inversion" -- same luminance condition, opposite
        spatial zone, opposite color push -- is novel. No prior pass pair in the
        engine encodes a systematic spatial inversion of a luminance-gated effect.
        """
        print("    Bierstadt Luminous Glory pass (194th mode)...")

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

        # Per-pixel normalized Y coordinate [0=top, 1=bottom]
        Yn = _np.linspace(0.0, 1.0, H, dtype=_np.float32)[:, _np.newaxis]
        Yn = _np.broadcast_to(Yn, (H, W)).astype(_np.float32)

        # Stage 1: Luminous horizon uplift in sky zone
        sz = float(sky_zone)
        # sky_mask: 1 in top sz fraction, soft boundary over 0.04
        sky_mask = _np.clip(1.0 - (Yn - sz + 0.04) / 0.04, 0.0, 1.0).astype(_np.float32)
        # horizon_weight: Yn fraction within sky zone (0 at top, 1 at bottom of sky)
        Yn_in_sky = _np.clip(Yn / max(sz, 0.01), 0.0, 1.0).astype(_np.float32)
        horizon_weight = (Yn_in_sky ** 1.8).astype(_np.float32)
        # bright_mask in sky zone
        sbl = float(sky_bright_lo)
        bright_in_sky = _np.clip((L - sbl) / max(1.0 - sbl, 0.01), 0.0, 1.0).astype(_np.float32)

        h_str = float(horizon_strength)
        hr_, hg_, hb_ = float(horizon_r), float(horizon_g), float(horizon_b)
        h_mask = (sky_mask * horizon_weight * bright_in_sky).astype(_np.float32)
        R1 = _np.clip(R + (hr_ - R) * h_mask * h_str, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (hg_ - G) * h_mask * h_str, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (hb_ - B) * h_mask * h_str, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Cool ultramarine zenith push
        zf = float(zenith_fraction)
        zenith_spatial = _np.clip(1.0 - (Yn - zf + 0.03) / 0.03, 0.0, 1.0).astype(_np.float32)
        zdt = max(float(zenith_dark_thresh), 0.01)
        dark_in_zenith = _np.clip(1.0 - L / zdt, 0.0, 1.0).astype(_np.float32)
        z_mask = (zenith_spatial * dark_in_zenith).astype(_np.float32)

        z_str = float(zenith_strength)
        zr_, zg_, zb_ = float(zenith_r), float(zenith_g), float(zenith_b)
        R2 = _np.clip(R1 + (zr_ - R1) * z_mask * z_str, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (zg_ - G1) * z_mask * z_str, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (zb_ - B1) * z_mask * z_str, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Warm amber middle-distance theatrical haze (triple gate)
        mzlo, mzhi = float(mid_zone_lo), float(mid_zone_hi)
        band_w = max((mzhi - mzlo) * 0.12, 0.01)
        mid_zone_mask = (_np.clip((Yn - mzlo) / band_w, 0.0, 1.0) *
                         _np.clip((mzhi - Yn) / band_w, 0.0, 1.0)).astype(_np.float32)

        mlo, mhi = float(mid_lo), float(mid_hi)
        lum_band_w = max((mhi - mlo) * 0.20, 0.01)
        lum_gate_ = (_np.clip((L - mlo) / lum_band_w, 0.0, 1.0) *
                     _np.clip((mhi - L) / lum_band_w, 0.0, 1.0)).astype(_np.float32)

        L2 = (0.299 * R2 + 0.587 * G2 + 0.114 * B2).astype(_np.float32)
        C2_max = _np.maximum(_np.maximum(R2, G2), B2).astype(_np.float32)
        C2_min = _np.minimum(_np.minimum(R2, G2), B2).astype(_np.float32)
        S2 = _np.where(C2_max > 1e-6,
                       (C2_max - C2_min) / (C2_max + 1e-6),
                       _np.zeros_like(C2_max)).astype(_np.float32)
        mst = max(float(mid_sat_thresh), 0.01)
        sat_gate_ = _np.clip(1.0 - S2 / mst, 0.0, 1.0).astype(_np.float32)

        amber_mask = (mid_zone_mask * lum_gate_ * sat_gate_).astype(_np.float32)
        a_str = float(amber_strength)
        ar_, ag_, ab_ = float(amber_r), float(amber_g), float(amber_b)
        R3 = _np.clip(R2 + (ar_ - R2) * amber_mask * a_str, 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G2 + (ag_ - G2) * amber_mask * a_str, 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B2 + (ab_ - B2) * amber_mask * a_str, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Lower zone warm umber foreground shadow enrichment
        lz = float(lower_zone)
        lower_mask = _np.clip((Yn - lz) / max(1.0 - lz, 0.01), 0.0, 1.0).astype(_np.float32)
        ldt = max(float(lower_dark_thresh), 0.01)
        dark_gate_ = _np.clip(1.0 - L / ldt, 0.0, 1.0).astype(_np.float32)
        umber_mask = (lower_mask * dark_gate_).astype(_np.float32)

        u_str = float(umber_strength)
        ur_, ug_, ub_ = float(umber_r), float(umber_g), float(umber_b)
        R4 = _np.clip(R3 + (ur_ - R3) * umber_mask * u_str, 0.0, 1.0).astype(_np.float32)
        G4 = _np.clip(G3 + (ug_ - G3) * umber_mask * u_str, 0.0, 1.0).astype(_np.float32)
        B4 = _np.clip(B3 + (ub_ - B3) * umber_mask * u_str, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R4 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G4 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B4 - B) * op, 0.0, 1.0).astype(_np.float32)

        h_px     = int((h_mask     > 0.05).sum())
        z_px     = int((z_mask     > 0.05).sum())
        amber_px = int((amber_mask > 0.05).sum())
        umber_px = int((umber_mask > 0.05).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Bierstadt Luminous Glory complete "
              f"(h_px={h_px}, z_px={z_px}, amber_px={amber_px}, umber_px={umber_px})")

'''

# ── Append both passes to stroke_engine.py (after last method) ───────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8-sig") as f:
    src = f.read()

# Verify neither pass already exists
assert "paint_crepuscular_ray_pass" not in src, \
    "paint_crepuscular_ray_pass already exists in stroke_engine.py"
assert "bierstadt_luminous_glory_pass" not in src, \
    "bierstadt_luminous_glory_pass already exists in stroke_engine.py"

# Append to end of file
with open(SE_PATH, "a", encoding="utf-8") as f:
    f.write(CREPUSCULAR_RAY_PASS)
    f.write(BIERSTADT_LUMINOUS_GLORY_PASS)

print("stroke_engine.py patched: paint_crepuscular_ray_pass (s283 improvement)"
      " + bierstadt_luminous_glory_pass (194th mode) appended.")
