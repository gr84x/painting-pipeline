"""Insert paint_structure_tensor_pass (s288 improvement) and
pissarro_divisionist_shimmer_pass (199th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_structure_tensor_pass (s288 improvement) ───────────────────

STRUCTURE_TENSOR_PASS = '''
    def paint_structure_tensor_pass(
        self,
        outer_sigma:        float = 3.0,
        inner_sigma:        float = 1.2,
        sharpen_amount:     float = 0.55,
        coherence_threshold:float = 0.08,
        opacity:            float = 0.70,
    ) -> None:
        r"""Structure Tensor Anisotropic Sharpening -- s288 improvement.

        THE PHYSICAL BASIS: STRUCTURE TENSOR AND EIGENVALUE COHERENCE GATING

        Every prior sharpening or detail-enhancement pass in this engine uses
        an ISOTROPIC operation: the unsharp mask applies the same kernel in all
        spatial directions simultaneously. At a painted edge -- a boundary
        between two colour planes, the silhouette of a form, the sharp edge of
        a brushstroke -- isotropic sharpening amplifies detail both perpendicular
        to the edge (across it, the direction that makes it sharper) and parallel
        to the edge (along it, the direction that adds noise and ringing). This
        is why standard unsharp mask at strong settings introduces characteristic
        "halo" artifacts: bright overshoots on one side of edges and dark
        overshoots on the other.

        The structure tensor, introduced by Förstner (1986) and popularized by
        Harris & Stephens (1988) for corner detection, provides a fundamentally
        different description of local image geometry. Instead of asking
        "how strong is the gradient here?" (a scalar), it asks "in what
        directions does the image vary, and how much, and how coherently?" (a
        tensor, a 2×2 matrix of spatial statistics).

        Given a single-channel image I, its gradient at pixel (x, y) is
        the vector (∂I/∂x, ∂I/∂y). The outer product of this vector with
        itself is:
          M(x,y) = [[Ix², IxIy],
                    [IxIy, Iy²]]

        This 2×2 matrix, summed (or Gaussian-smoothed) over a local neighbourhood,
        is the structure tensor J:
          J = G_σ * M = [[G_σ(Ix²), G_σ(IxIy)],
                          [G_σ(IxIy), G_σ(Iy²)]]
                       = [[Jxx, Jxy],
                          [Jxy, Jyy]]

        The eigenvalues λ₁ ≥ λ₂ of J describe the variance of the gradient
        in the two principal directions at that location:

          λ₁ = large, λ₂ ≈ 0  → EDGE: one strong direction, gradient
               perpendicular to edge; all gradients in neighbourhood point
               the same way.

          λ₁ ≈ λ₂ > 0 → CORNER or NOISE: gradients in many directions;
               no single dominant orientation.

          λ₁ ≈ λ₂ ≈ 0 → FLAT region: no significant gradient in any direction.

        The COHERENCE is the normalized difference between eigenvalues:
          coherence = (λ₁ − λ₂)² / (λ₁ + λ₂ + ε)²

        This quantity is:
          - Near 1.0 at clear edges (λ₁ >> λ₂)
          - Near 0.0 at flat regions and isotropic noise (λ₁ ≈ λ₂)
          - Dimensionless and scale-invariant (the normalization removes
            dependence on the overall gradient magnitude)

        MATHEMATICAL NOVELTY IN THIS ENGINE:

        NOVEL (a): FIRST STRUCTURE TENSOR IN ENGINE.
        The structure tensor is defined by the outer product of the image gradient
        with itself, integrated (smoothed) over a local neighbourhood:
          Jxx = G_σ_outer(Ix · Ix)
          Jxy = G_σ_outer(Ix · Iy)
          Jyy = G_σ_outer(Iy · Iy)
        This is a second-order spatial statistics operation: it involves products
        of first-order derivatives (the gradient), then spatial smoothing of
        those products. All 198 prior passes in this engine use:
          - First-order gradients directly (Sobel Gx, Gy, or G_norm): grosz,
            repin, carriere, hartley, derain, savrasov.
          - Gaussian smoothing of the raw image or of a single channel: all
            gaussian_filter calls.
        None compute the OUTER PRODUCT of the gradient with itself and then
        smooth that product. This is the first use of the 2×2 gradient
        covariance matrix (structure tensor) as a local image descriptor.

        NOVEL (b): FIRST EIGENVALUE DECOMPOSITION IN ENGINE.
        The structure tensor J is a symmetric positive semi-definite 2×2 matrix.
        Its eigenvalues λ₁, λ₂ can be computed in closed form:
          trace = Jxx + Jyy
          disc  = sqrt( ((Jxx - Jyy)/2)² + Jxy² )
          λ₁    = trace/2 + disc
          λ₂    = trace/2 - disc
        This is the first use of eigenvalue analysis in the engine. Prior passes
        that involve linear algebra operate only on first-order quantities
        (gradient magnitude, gradient direction via atan2). The eigenvalue
        decomposition extracts the principal axes of the local gradient
        distribution -- a qualitatively different kind of geometric information.

        NOVEL (c): COHERENCE MAP AS SHARPENING GATE.
        coherence = (λ₁ − λ₂)² / (λ₁ + λ₂ + ε)²
        This map takes value near 1 at genuine image edges (where the gradient
        is consistently oriented across the neighbourhood) and near 0 at flat
        regions, isotropic noise, and corners (where gradients are multidirectional
        or absent). Using coherence as the opacity weight for sharpening means:
          - Genuine, consistent edges receive full sharpening strength
          - Flat areas receive zero sharpening (no noise amplification)
          - Noisy or cornered regions receive partial sharpening proportional to
            their coherence

        All 198 prior sharpening passes gate on: gradient magnitude G_norm (a
        first-order quantity), luminance L, or a hand-tuned percentile threshold.
        None use coherence (a normalized eigenvalue ratio from the structure
        tensor) as the sharpening gate. Using coherence separates "genuine
        edge-ness" (consistent single-direction gradient) from "general gradient
        strength" (high G_norm can include noisy textures and corners).

        NOVEL (d): COHERENCE-MODULATED OPACITY BLEND.
        The final blend uses the coherence map as a per-pixel opacity:
          canvas_out = canvas + sharpened_delta * coherence * opacity
        This means sharpening is automatically strongest at the most
        edge-coherent pixels and automatically absent at flat/noisy zones.
        No prior pass uses a spatially adaptive opacity derived from an
        eigenvalue statistic.

        STAGE 1 -- STRUCTURE TENSOR COMPUTATION:

        Compute the luminance channel:
          L = 0.299R + 0.587G + 0.114B

        Compute gradient components using Gaussian derivatives:
          Ix = G_σ_inner(L, order=[0,1])   ∂L/∂x
          Iy = G_σ_inner(L, order=[1,0])   ∂L/∂y

        Compute the three independent components of the structure tensor:
          Jxx = G_σ_outer(Ix * Ix)
          Jxy = G_σ_outer(Ix * Iy)
          Jyy = G_σ_outer(Iy * Iy)

        STAGE 2 -- EIGENVALUE DECOMPOSITION AND COHERENCE MAP:

        For each pixel:
          trace = Jxx + Jyy
          disc  = sqrt( ((Jxx - Jyy)/2)² + Jxy² + ε )
          λ₁    = trace/2 + disc    (larger eigenvalue)
          λ₂    = trace/2 - disc    (smaller eigenvalue, ≥ 0)

        Coherence:
          coherence = ((λ₁ - λ₂) / (λ₁ + λ₂ + ε))²

        The squaring makes the coherence map more selective:
        values below 0.5 are strongly suppressed, so only the most
        clearly edge-like regions receive strong sharpening.

        STAGE 3 -- COHERENCE-GATED UNSHARP MASK:

        For each colour channel C in {R, G, B}:
          C_blur     = G_σ_inner(C)            (Gaussian smoothing)
          C_sharp    = C + sharpen_amount * (C - C_blur)
          C_clamped  = clip(C_sharp, 0, 1)

        This is a standard isotropic unsharp mask. Its anisotropic
        effective behaviour comes entirely from Stage 4 (the coherence
        gate), not from the sharpening kernel itself.

        STAGE 4 -- COHERENCE-MODULATED OPACITY BLEND:

        For each channel:
          delta       = C_sharp - C_original
          effective_w = coherence * opacity
          C_out       = clip(C + delta * effective_w, 0, 1)

        Where coherence is the per-pixel map from Stage 2, values in [0,1].
        This concentrates the sharpening effect on genuine edge regions
        (high coherence) and leaves flat areas, noise, and corners
        essentially untouched (low coherence).
        """
        print("    Structure Tensor Anisotropic Sharpening (s288 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        eps = 1e-8
        si  = float(inner_sigma)
        so  = float(outer_sigma)

        # Stage 1: Structure tensor computation
        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)

        Ix = _gf(L, sigma=si, order=[0, 1]).astype(_np.float32)  # dL/dx
        Iy = _gf(L, sigma=si, order=[1, 0]).astype(_np.float32)  # dL/dy

        Jxx = _gf((Ix * Ix).astype(_np.float32), sigma=so).astype(_np.float32)
        Jxy = _gf((Ix * Iy).astype(_np.float32), sigma=so).astype(_np.float32)
        Jyy = _gf((Iy * Iy).astype(_np.float32), sigma=so).astype(_np.float32)

        # Stage 2: Eigenvalue decomposition (closed-form 2x2 symmetric)
        trace = (Jxx + Jyy).astype(_np.float32)
        half_diff = ((Jxx - Jyy) * 0.5).astype(_np.float32)
        disc = _np.sqrt((half_diff * half_diff + Jxy * Jxy).astype(_np.float32) + eps
                        ).astype(_np.float32)

        lam1 = (trace * 0.5 + disc).astype(_np.float32)
        lam2 = _np.clip((trace * 0.5 - disc).astype(_np.float32), 0.0, None
                        ).astype(_np.float32)

        lam_sum = (lam1 + lam2 + eps).astype(_np.float32)
        lam_diff = (lam1 - lam2).astype(_np.float32)
        coherence_raw = (lam_diff / lam_sum).astype(_np.float32)
        coherence = (coherence_raw * coherence_raw).astype(_np.float32)

        # Apply coherence threshold (suppress very low values)
        ct = float(coherence_threshold)
        coherence = _np.clip((coherence - ct) / max(1.0 - ct, eps), 0.0, 1.0
                             ).astype(_np.float32)

        # Stage 3: Isotropic unsharp mask per channel
        sa = float(sharpen_amount)
        R_blur = _gf(R, sigma=si).astype(_np.float32)
        G_blur = _gf(G, sigma=si).astype(_np.float32)
        B_blur = _gf(B, sigma=si).astype(_np.float32)

        R_sharp = _np.clip(R + sa * (R - R_blur), 0.0, 1.0).astype(_np.float32)
        G_sharp = _np.clip(G + sa * (G - G_blur), 0.0, 1.0).astype(_np.float32)
        B_sharp = _np.clip(B + sa * (B - B_blur), 0.0, 1.0).astype(_np.float32)

        # Stage 4: Coherence-modulated opacity blend
        op = float(opacity)
        eff_w = (coherence * op).astype(_np.float32)

        R_out = _np.clip(R + (R_sharp - R) * eff_w, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G_sharp - G) * eff_w, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B_sharp - B) * eff_w, 0.0, 1.0).astype(_np.float32)

        edge_px      = int((coherence > 0.30).sum())
        high_coh_px  = int((coherence > 0.70).sum())
        coh_mean     = float(coherence.mean())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Structure Tensor complete "
              f"(coherence_mean={coh_mean:.4f}, edge_px={edge_px}, "
              f"high_coh_px={high_coh_px})")

'''

# ── Pass 2: pissarro_divisionist_shimmer_pass (199th mode) ────────────────────

PISSARRO_PASS = '''
    def pissarro_divisionist_shimmer_pass(
        self,
        dot_radius:          int   = 6,
        n_samples:           int   = 6,
        color_sigma:         float = 0.12,
        shimmer_strength:    float = 0.22,
        shadow_hi:           float = 0.38,
        shadow_lo:           float = 0.20,
        shadow_green:        tuple = (0.36, 0.52, 0.38),
        shadow_strength:     float = 0.28,
        highlight_lo:        float = 0.68,
        highlight_hi:        float = 0.88,
        warm_amber:          tuple = (0.94, 0.86, 0.58),
        highlight_strength:  float = 0.24,
        hue_coherence:       float = 0.35,
        n_hue_sectors:       int   = 12,
        opacity:             float = 0.82,
    ) -> None:
        r"""Pissarro Divisionist Shimmer -- 199th mode.

        CAMILLE PISSARRO (1830-1903) -- DEAN OF THE IMPRESSIONISTS;
        ANARCHIST PATRIARCH OF OPTICAL COLOUR MIXING:

        Camille Pissarro occupies a singular position in the history of
        Impressionism: he is the only artist to have exhibited in all eight
        Impressionist exhibitions (1874-1886), the undisputed patriarch who
        mentored Cézanne, Gauguin, Seurat, Signac, and countless others. Born
        in the Danish West Indies to a Sephardic Jewish father and a Creole
        mother, he arrived in Paris in 1855 and spent the rest of his life as
        an outsider-within -- a foreign-born anarchist at the centre of the most
        important art movement of his century.

        His technique evolved dramatically over his life. The early work (1860s)
        is Courbet-influenced: solid, textured, earthbound. The Impressionist
        peak (1870s-early 1880s) is his most celebrated: loose, vibrant, directly
        observed landscapes and peasant scenes at Pontoise and Eragny. His Neo-
        Impressionist period (1885-1891), where Seurat's pointillist system
        captivated him, is technically his most systematic. He eventually found
        Seurat's rigidity too constraining and returned to a freer touch, but the
        experience permanently changed how he thought about colour placement.

        PISSARRO'S FOUR DEFINING TECHNICAL CHARACTERISTICS:

        1. DIVISIONIST OPTICAL MIXING -- THE TREMBLING DOT:
        Where Seurat placed his dots with mechanical regularity, Pissarro's
        "dots" are irregular -- comma-shaped touches, short hatching strokes,
        patches -- retaining the handmade quality he never wished to abandon.
        The principle is the same: place pure colour adjacent to pure colour
        and let the eye mix them. But the execution is organic, varying in size
        and direction as the hand responds to the subject. This produces a surface
        that SHIMMERS rather than buzzes: a constant gentle optical vibration
        as the eye alternates between resolving individual touches and averaging
        them into a field of colour.

        2. COOL SAGE-GREEN SHADOWS:
        Pissarro's shadow note is distinct from Monet's violet, Renoir's blue,
        or Degas's grey-black. In his plein-air fields, orchards, and village
        scenes, the shadow zones carry a characteristic sage-green: the colour of
        grass-in-shadow, of foliage on its shaded underside, of a sunlit meadow
        at midday. This green shadow tone is his most identifiable regional
        character -- it roots his landscapes firmly in the damp, green Normandy
        and Île-de-France countryside where he spent most of his working life.

        3. WARM AMBER ATMOSPHERIC LIGHT:
        Pissarro's high-key lights are warm rather than cold. The sunlight in
        his fields and orchards is straw-gold, the colour of late-morning French
        light -- not the blue-white of Mediterranean glare, not the icy white
        of Monet's late series. This warmth gives his paintings a quality of
        gentle inhabitable atmosphere, a landscape you could walk into without
        squinting.

        4. SECTOR-HUE FAMILY COHERENCE:
        Across any given Pissarro canvas, the greens form a family, the ambers
        form a family, the blues form a family. Within each hue zone, there are
        many individual touches of slightly different colour -- the optical
        vibration -- but they share a parent hue from which they deviate only
        slightly. This "hue family coherence" is what gives his divisionist
        canvases their paradoxical quality of being simultaneously vibrating and
        unified: many colours, one register.

        THE GREAT WORKS:
        "Peasant Women Planting Pea Sticks" (1891): the full divisionist system
        applied to a figure-in-landscape composition; sage-green field, amber
        light, trembling dot field throughout.

        "The Boulevard Montmartre at Night" (1897): the Parisian street scene as
        a field of orange gas-lamp dots against blue-grey stone and cobbles --
        the city given the same optical-mixing treatment as the countryside.

        "La Côte des Boeufs at the Hermitage, Pontoise" (1877): the most
        purely painterly work of the Impressionist peak; a wall of layered autumn
        foliage rendered as interlocking sage-green, ochre, and amber touches.

        NOVELTY ANALYSIS: FOUR DISTINCT MATHEMATICAL INNOVATIONS:

        Stage 1 STOCHASTIC CHROMATIC NEIGHBOR BLEND:
        For k = 1 to n_samples, draw a random integer displacement
          dy_k ~ U(-dot_radius, dot_radius)
          dx_k ~ U(-dot_radius, dot_radius)
        using the canvas instance's rng (numpy.random.default_rng with
        seed derived from SEED_288):
          neighbor_k = roll(canvas_channel, dy_k, dx_k)
          color_dist_k = sqrt(sum_over_channels((C - neighbor_k)^2))
          w_k = exp(-color_dist_k / color_sigma)

        Accumulated weighted average:
          R_acc = R + sum_k(neighbor_R_k * w_k)
          W_acc = 1 + sum_k(w_k)
          R_blend = R_acc / W_acc

        Final shimmer blend:
          R1 = R + (R_blend - R) * shimmer_strength

        NOVEL: FIRST STOCHASTIC (RANDOM-SEED-DRIVEN) SPATIAL SAMPLING
        IN ENGINE. All 198 prior passes use DETERMINISTIC spatial kernels:
          -- Gaussian filter: fixed Gaussian kernel (linear, shift-invariant)
          -- Median filter (s287): deterministic rank-order (fixed neighbourhood)
          -- Tile averaging (s287 Stage 2): deterministic grid
          -- Sobel gradient: fixed 3x3 kernel
          -- np.roll with fixed offsets: used in contre_jour and others for
             simple single-direction shifts (always one direction, always same
             amount)
        The present stage uses RANDOM integer offsets drawn from a seeded
        RNG, producing K independent stochastic shifts per pass call. The
        weighted average over random neighbours is a stochastic bilateral
        filter: similar to the bilateral filter in weighting by colour
        similarity, but using random sparse sampling rather than a
        dense neighbourhood kernel. This is the first use of any stochastic
        operation in the 199-pass engine.

        Stage 2 COOL SAGE-GREEN SHADOW PUSH:
        Compute luminance L1 = 0.299R1 + 0.587G1 + 0.114B1.
        Smooth gate: gate = smoothstep(L1, edge_lo=shadow_lo, edge_hi=shadow_hi)
          gate = clip((shadow_hi - L1) / (shadow_hi - shadow_lo), 0, 1)
          gate_smooth = gate * gate * (3 - 2*gate)   (cubic Hermite interpolant)
        Apply: R2 = R1 + gate_smooth * shadow_strength * (shadow_green_R - R1)

        Target: shadow_green = (0.36, 0.52, 0.38) -- cool sage-green.
        This is the colour of grass-in-shadow in Normandy; neither violet
        (Monet) nor blue-grey (Hammershoi) nor warm umber (Repin, Carriere).
        It is Pissarro's most characteristic regional shadow tone.

        Stage 3 WARM AMBER HIGHLIGHT PUSH:
        gate_hi = clip((L2 - highlight_lo) / (highlight_hi - highlight_lo), 0, 1)
        gate_hi_smooth = gate_hi * gate_hi * (3 - 2*gate_hi)
        R3 = R2 + gate_hi_smooth * highlight_strength * (warm_amber_R - R2)

        Target: warm_amber = (0.94, 0.86, 0.58) -- warm straw-gold.
        Pissarro's atmospheric morning-light colour: warm, humid, terrestrial.
        Not the cold blue-white of Cezanne's Provence or Sorolla's Valencia.

        Stage 4 SECTOR-MEDIAN HUE COHERENCE:
        Convert R3, G3, B3 to HSV:
          V   = max(R3, G3, B3)
          S   = (V - min) / (V + eps)
          H   = ... (standard 6-sector HSV hue computation)

        Divide the 360-degree hue circle into n_hue_sectors equal sectors.
        For each sector s:
          mask_s = pixels where sector_index(H) == s
          H_med_s = median(H[mask_s])   (circular, handled by sector bounds)
          H_diff_s = H[mask_s] - H_med_s  (deviation from sector median)
          H_new[mask_s] = H_med_s + H_diff_s * (1 - hue_coherence * S[mask_s])

        The weight (1 - hue_coherence * S) means:
          -- Highly saturated pixels (S≈1): strong pull toward sector median
          -- Desaturated pixels (S≈0): no hue correction (hue is ill-defined
             for greys, which should not be hue-corrected)

        Convert back to RGB.

        NOVEL: FIRST PASS TO COMPUTE PER-SECTOR DATA-DRIVEN MEDIAN HUES
        AND APPLY INTRA-SECTOR COHERENCE. Prior hue-modifying passes:
          -- derain Stage 2: pushes H toward FIXED SPECTRAL TARGETS for each
             of 6 sectors (canonical pure red, yellow, green, cyan, blue,
             magenta). The target is FIXED regardless of image content.
          -- paint_chromatic_shadow_shift_pass (s284): rotates H by a FIXED
             AMOUNT in shadow/highlight zones (constant offset, not median).
        The present stage computes the median hue of the IMAGE ITSELF within
        each sector -- targets are DATA-DRIVEN, varying per image. The pull
        is toward the image's own hue center of mass in each zone, creating
        INTRA-SECTOR COHERENCE (Pissarro's hue families) without imposing a
        fixed spectral target. This is fundamentally different from both prior
        approaches.
        """
        print("    Pissarro Divisionist Shimmer pass (199th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        eps = 1e-7

        # ── Stage 1: Stochastic chromatic neighbor blend ─────────────────────────
        rng = _np.random.default_rng(2880)
        dr  = int(dot_radius)
        cs  = float(color_sigma)
        K   = int(n_samples)
        ss  = float(shimmer_strength)

        R_acc = R.copy().astype(_np.float32)
        G_acc = G.copy().astype(_np.float32)
        B_acc = B.copy().astype(_np.float32)
        W_acc = _np.ones((H_, W_), dtype=_np.float32)

        for _ in range(K):
            dy = int(rng.integers(-dr, dr + 1))
            dx = int(rng.integers(-dr, dr + 1))
            nR = _np.roll(_np.roll(R, dy, axis=0), dx, axis=1).astype(_np.float32)
            nG = _np.roll(_np.roll(G, dy, axis=0), dx, axis=1).astype(_np.float32)
            nB = _np.roll(_np.roll(B, dy, axis=0), dx, axis=1).astype(_np.float32)
            cdist = _np.sqrt(
                (R - nR) ** 2 + (G - nG) ** 2 + (B - nB) ** 2 + eps
            ).astype(_np.float32)
            w = _np.exp(-cdist / max(cs, eps)).astype(_np.float32)
            R_acc += nR * w
            G_acc += nG * w
            B_acc += nB * w
            W_acc += w

        R_blend = (R_acc / W_acc).astype(_np.float32)
        G_blend = (G_acc / W_acc).astype(_np.float32)
        B_blend = (B_acc / W_acc).astype(_np.float32)

        R1 = _np.clip(R + (R_blend - R) * ss, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (G_blend - G) * ss, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (B_blend - B) * ss, 0.0, 1.0).astype(_np.float32)

        shimmer_px = int((W_acc > (1 + K * 0.3)).sum())

        # ── Stage 2: Cool sage-green shadow push ─────────────────────────────────
        L1 = (0.299 * R1 + 0.587 * G1 + 0.114 * B1).astype(_np.float32)
        sh_hi = float(shadow_hi)
        sh_lo = float(shadow_lo)
        sh_rng = max(sh_hi - sh_lo, eps)
        gate_s = _np.clip((sh_hi - L1) / sh_rng, 0.0, 1.0).astype(_np.float32)
        gate_s = (gate_s * gate_s * (3.0 - 2.0 * gate_s)).astype(_np.float32)  # cubic Hermite

        sg_r, sg_g, sg_b = float(shadow_green[0]), float(shadow_green[1]), float(shadow_green[2])
        str_s = float(shadow_strength)
        R2 = _np.clip(R1 + gate_s * str_s * (sg_r - R1), 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + gate_s * str_s * (sg_g - G1), 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + gate_s * str_s * (sg_b - B1), 0.0, 1.0).astype(_np.float32)

        shadow_px = int((gate_s > 0.15).sum())

        # ── Stage 3: Warm amber highlight push ───────────────────────────────────
        L2 = (0.299 * R2 + 0.587 * G2 + 0.114 * B2).astype(_np.float32)
        hi_lo = float(highlight_lo)
        hi_hi = float(highlight_hi)
        hi_rng = max(hi_hi - hi_lo, eps)
        gate_h = _np.clip((L2 - hi_lo) / hi_rng, 0.0, 1.0).astype(_np.float32)
        gate_h = (gate_h * gate_h * (3.0 - 2.0 * gate_h)).astype(_np.float32)  # cubic Hermite

        wa_r, wa_g, wa_b = float(warm_amber[0]), float(warm_amber[1]), float(warm_amber[2])
        str_h = float(highlight_strength)
        R3 = _np.clip(R2 + gate_h * str_h * (wa_r - R2), 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G2 + gate_h * str_h * (wa_g - G2), 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B2 + gate_h * str_h * (wa_b - B2), 0.0, 1.0).astype(_np.float32)

        highlight_px = int((gate_h > 0.15).sum())

        # ── Stage 4: Sector-median hue coherence ─────────────────────────────────
        cmax = _np.max(_np.stack([R3, G3, B3], axis=-1), axis=-1).astype(_np.float32)
        cmin = _np.min(_np.stack([R3, G3, B3], axis=-1), axis=-1).astype(_np.float32)
        delta_c = (cmax - cmin).astype(_np.float32)

        # Saturation (HSV)
        S_hsv = _np.where(cmax > eps, delta_c / (cmax + eps), 0.0).astype(_np.float32)

        # Hue in degrees [0, 360)
        H_deg = _np.zeros((H_, W_), dtype=_np.float32)
        mask_valid = (delta_c > eps)
        mask_r = mask_valid & (cmax == R3)
        mask_g = mask_valid & (cmax == G3) & ~mask_r
        mask_b = mask_valid & (cmax == B3) & ~mask_r & ~mask_g

        H_deg[mask_r] = (60.0 * ((G3[mask_r] - B3[mask_r]) / (delta_c[mask_r] + eps)) % 360.0)
        H_deg[mask_g] = (60.0 * ((B3[mask_g] - R3[mask_g]) / (delta_c[mask_g] + eps)) + 120.0)
        H_deg[mask_b] = (60.0 * ((R3[mask_b] - G3[mask_b]) / (delta_c[mask_b] + eps)) + 240.0)
        H_deg = H_deg % 360.0

        n_sec = int(n_hue_sectors)
        sec_size = 360.0 / n_sec
        hc = float(hue_coherence)

        H_new = H_deg.copy()
        for s_idx in range(n_sec):
            h_lo_s = s_idx * sec_size
            h_hi_s = h_lo_s + sec_size
            mask_sec = mask_valid & (H_deg >= h_lo_s) & (H_deg < h_hi_s)
            if mask_sec.sum() < 3:
                continue
            H_sec = H_deg[mask_sec]
            H_med_s = float(_np.median(H_sec))
            H_diff_s = H_sec - H_med_s
            # Circular wrap: keep deviation in [-180, +180]
            H_diff_s = ((H_diff_s + 180.0) % 360.0) - 180.0
            sat_w = S_hsv[mask_sec]
            H_new[mask_sec] = (H_med_s + H_diff_s * (1.0 - hc * sat_w)) % 360.0

        # Convert modified HSV back to RGB
        # V = cmax, S = S_hsv, H = H_new
        H6  = H_new / 60.0
        I_h = _np.floor(H6).astype(_np.int32) % 6
        f   = (H6 - _np.floor(H6)).astype(_np.float32)
        V   = cmax
        p   = (V * (1.0 - S_hsv)).astype(_np.float32)
        q   = (V * (1.0 - f * S_hsv)).astype(_np.float32)
        t   = (V * (1.0 - (1.0 - f) * S_hsv)).astype(_np.float32)

        R4 = _np.zeros_like(R3)
        G4 = _np.zeros_like(G3)
        B4 = _np.zeros_like(B3)

        for i_h_val, (r_src, g_src, b_src) in enumerate([
            (V, t, p), (q, V, p), (p, V, t), (p, q, V), (t, p, V), (V, p, q)
        ]):
            m = (I_h == i_h_val)
            R4[m] = r_src[m]
            G4[m] = g_src[m]
            B4[m] = b_src[m]

        # For pixels with no saturation (grey), preserve original
        grey_mask = ~mask_valid
        R4[grey_mask] = R3[grey_mask]
        G4[grey_mask] = G3[grey_mask]
        B4[grey_mask] = B3[grey_mask]

        R4 = _np.clip(R4, 0.0, 1.0).astype(_np.float32)
        G4 = _np.clip(G4, 0.0, 1.0).astype(_np.float32)
        B4 = _np.clip(B4, 0.0, 1.0).astype(_np.float32)

        corrected_px = int(mask_valid.sum())

        # Final opacity blend
        op = float(opacity)
        R_out = _np.clip(R + (R4 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G4 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B4 - B) * op, 0.0, 1.0).astype(_np.float32)

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Pissarro Divisionist Shimmer complete "
              f"(shimmer_px={shimmer_px}, shadow_px={shadow_px}, "
              f"highlight_px={highlight_px}, hue_corrected_px={corrected_px})")

'''

# ── Append both passes to stroke_engine.py ───────────────────────────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8-sig") as f:
    src = f.read()

assert "paint_structure_tensor_pass" not in src, \
    "paint_structure_tensor_pass already exists in stroke_engine.py"
assert "pissarro_divisionist_shimmer_pass" not in src, \
    "pissarro_divisionist_shimmer_pass already exists in stroke_engine.py"

with open(SE_PATH, "a", encoding="utf-8") as f:
    f.write(STRUCTURE_TENSOR_PASS)
    f.write(PISSARRO_PASS)

print("stroke_engine.py patched: paint_structure_tensor_pass (s288 improvement)"
      " + pissarro_divisionist_shimmer_pass (199th mode) appended.")
