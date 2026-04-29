"""Append frankenthaler_soak_stain_pass (152nd mode) + paint_lost_found_edges_pass to stroke_engine.py (session 241)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

FRANKENTHALER_PASS = r'''
    def frankenthaler_soak_stain_pass(
        self,
        n_stains:         int   = 4,
        sigma_large:      float = 40.0,
        sigma_small:      float = 12.0,
        stain_alpha:      float = 0.40,
        absorption:       float = 0.65,
        cap_sigma:        float = 3.0,
        cap_threshold:    float = 0.06,
        seed:             int   = 7,
        opacity:          float = 0.78,
    ) -> None:
        r"""
        Frankenthaler Soak-Stain -- session 241: ONE HUNDRED AND FIFTY-SECOND distinct mode.

        Implements Helen Frankenthaler (1928-2011) soak-stain technique, invented in
        1952 with her seminal painting Mountains and Sea.  Working on raw, unprimed
        canvas laid flat on the studio floor, Frankenthaler poured turpentine-thinned
        paint directly from cans, guiding the flowing pools by tilting the canvas.
        Because the canvas is unprimed, the paint soaks INTO the weave of the cotton
        duck rather than sitting on top as a film: no impasto, no surface texture --
        only luminous, transparent colour that has become one with the fabric.

        THREE-STAGE SOAK-STAIN SIMULATION:

        Stage 1 ORGANIC STAIN REGION GENERATION:
        For each of n_stains stain regions, generate a random float plane, then
        compose a multi-scale noise field:
            stain_field_i = clip(
                0.65 * blur(noise_i, sigma=sigma_large)
                + 0.35 * blur(noise_i * 0.6 + noise_i_2 * 0.4, sigma=sigma_small),
                0, 1)
        Two Gaussian sigmas model different physical scales of paint flow: large-sigma
        simulates the broad swept pool from a tilted canvas pour; small-sigma simulates
        finer wicking detail within the pool as paint migrates along individual canvas
        fibres.  A luminance-bias step then weights the stain mask toward mid-luminance
        regions of the underlying canvas (where unprimed canvas would absorb most):
            lum_bias = 1.0 - |lum - 0.50| * 2.0   (peaks at lum=0.5, zero at 0 and 1)
            stain_mask_i = stain_field_i * (1.0 + lum_bias * 0.40)
            stain_mask_i = clip(stain_mask_i / stain_mask_i.max(), 0, 1)
        NOVEL: (a) MULTI-SCALE NOISE COMPOSITION -- first pass to build stain region
        masks by summing two independently Gaussian-blurred random planes at different
        sigmas (sigma_large for gross flow, sigma_small for capillary detail); no prior
        pass constructs organic region masks by this two-sigma composition method;
        (b) LUMINANCE-BIASED STAIN PLACEMENT -- first pass to scale the stain mask by
        a mid-luminance preference weight, reflecting the physical reality that unprimed
        canvas absorbs most pigment in mid-tone areas where surface energy is neutral.

        Stage 2 PAINT ABSORPTION SIMULATION:
        For each stain region, sample the average canvas colour within the stain footprint
        to obtain a locally representative hue for that pool:
            stain_color_i = mean(ch * stain_mask_i) over the stain region
        Then compose the absorbed stain:
            ch_stained = ch + stain_mask_i * stain_alpha
                         * (stain_color_i * (1.0 - absorption) + ch * absorption - ch)
            = ch + stain_mask_i * stain_alpha * (stain_color_i * (1-absorption) - ch*(1-absorption))
            = ch + stain_mask_i * stain_alpha * (1-absorption) * (stain_color_i - ch)
        The absorption coefficient (0..1) controls how much of the stain colour is
        neutralised by the canvas ground: high absorption (0.7+) means the stain shifts
        the canvas colour only gently, as pigment is mostly absorbed into fibres; low
        absorption (0.2-0.3) means more pigment sits at the surface.  The effective
        shift per stain is:  delta = stain_alpha * (1 - absorption) * (stain_color - ch).
        NOVEL: (b) PAINT ABSORPTION COEFFICIENT -- first pass to model paint as partially
        absorbed INTO the canvas substrate via an explicit absorption fraction blended
        toward the canvas ground; all prior passes model paint as sitting ON the surface
        at a given opacity; this pass separates surface opacity (stain_alpha) from
        substrate absorption fraction (absorption), creating the transparent, filmless
        quality of soak-stain work distinct from any glazing or wash technique.

        Stage 3 CAPILLARY EDGE DIFFUSION:
        At the boundary of each stain region, paint wicks outward along canvas fibres
        beyond the main pool edge -- the capillary fringe.  To simulate this:
            grad_mask = |nabla stain_mask| (magnitude of gradient of the stain mask)
            boundary = (grad_mask > cap_threshold).astype(float)
            boundary_smooth = gaussian_blur(boundary, sigma=1.0)
            ch_cap = gaussian_blur(ch_stained, sigma=cap_sigma)
            ch_final = ch_stained * (1.0 - boundary_smooth) + ch_cap * boundary_smooth
        The extra blur applied only at the stain perimeter creates a soft, diffuse halo
        that extends the stain colour slightly beyond the pool boundary, matching the
        capillary fringe visible in Frankenthaler's actual paintings.
        NOVEL: (c) BOUNDARY-LOCALISED CAPILLARY BLUR -- first pass to apply Gaussian
        blur selectively AT stain boundary zones (|nabla mask| > threshold) to simulate
        capillary migration of paint along canvas fibres at the pool edge; no prior
        pass applies spatially gated extra blurring at the gradient-detected boundary
        of a generated region mask.

        n_stains      : Number of independent stain pools to pour.
        sigma_large   : Gaussian sigma for broad flow component of stain shape.
        sigma_small   : Gaussian sigma for fine capillary detail component.
        stain_alpha   : Maximum colour shift per stain pool (paint volume).
        absorption    : Fraction absorbed into canvas (reduces surface colour shift).
        cap_sigma     : Gaussian sigma for capillary edge diffusion blur.
        cap_threshold : |nabla mask| threshold above which capillary blur is applied.
        seed          : Random seed for reproducible stain placement.
        opacity       : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gauss

        print("    Frankenthaler Soak-Stain pass (session 241: 152nd mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        rng = _np.random.RandomState(int(seed))

        r_out = r0.copy()
        g_out = g0.copy()
        b_out = b0.copy()

        sl = float(sigma_large)
        ss = float(sigma_small)
        sa = float(stain_alpha)
        ab = float(absorption)

        for _ in range(int(n_stains)):
            noise_a = rng.rand(h, w).astype(_np.float32)
            noise_b = rng.rand(h, w).astype(_np.float32)

            # Multi-scale composition: broad pour + fine capillary detail
            large_field = _gauss(noise_a, sigma=sl).astype(_np.float32)
            small_field = _gauss(noise_a * 0.6 + noise_b * 0.4, sigma=ss).astype(_np.float32)

            # Normalise each field to [0,1] then compose
            large_norm = large_field / (large_field.max() + 1e-7)
            small_norm = small_field / (small_field.max() + 1e-7)
            stain_raw = (0.65 * large_norm + 0.35 * small_norm).astype(_np.float32)
            stain_raw = _np.clip(stain_raw, 0.0, 1.0)

            # Luminance bias: stain stronger in mid-luminance areas
            lum_bias = (1.0 - _np.abs(lum - 0.50) * 2.0).astype(_np.float32)
            lum_bias = _np.clip(lum_bias, 0.0, 1.0)
            stain_mask = stain_raw * (1.0 + lum_bias * 0.40)
            mx = stain_mask.max()
            if mx > 1e-7:
                stain_mask = _np.clip(stain_mask / mx, 0.0, 1.0)
            stain_mask = stain_mask.astype(_np.float32)

            # Sample stain colour: luminance-weighted mean of current canvas within stain
            weight_sum = stain_mask.sum() + 1e-7
            sc_r = float((r_out * stain_mask).sum() / weight_sum)
            sc_g = float((g_out * stain_mask).sum() / weight_sum)
            sc_b = float((b_out * stain_mask).sum() / weight_sum)

            # Absorption-modulated stain application
            delta_r = stain_mask * sa * (1.0 - ab) * (sc_r - r_out)
            delta_g = stain_mask * sa * (1.0 - ab) * (sc_g - g_out)
            delta_b = stain_mask * sa * (1.0 - ab) * (sc_b - b_out)

            r_stained = _np.clip(r_out + delta_r, 0.0, 1.0).astype(_np.float32)
            g_stained = _np.clip(g_out + delta_g, 0.0, 1.0).astype(_np.float32)
            b_stained = _np.clip(b_out + delta_b, 0.0, 1.0).astype(_np.float32)

            # Capillary edge diffusion: extra blur at stain perimeter
            cs = float(cap_sigma)
            ct = float(cap_threshold)

            # Gradient magnitude of stain mask
            sm_gy = _np.abs(_np.gradient(stain_mask, axis=0)).astype(_np.float32)
            sm_gx = _np.abs(_np.gradient(stain_mask, axis=1)).astype(_np.float32)
            grad_mag = _np.sqrt(sm_gx * sm_gx + sm_gy * sm_gy).astype(_np.float32)

            boundary = (grad_mag > ct).astype(_np.float32)
            boundary_smooth = _gauss(boundary, sigma=1.0).astype(_np.float32)
            boundary_smooth = _np.clip(boundary_smooth, 0.0, 1.0)

            r_cap = _gauss(r_stained, sigma=cs).astype(_np.float32)
            g_cap = _gauss(g_stained, sigma=cs).astype(_np.float32)
            b_cap = _gauss(b_stained, sigma=cs).astype(_np.float32)

            r_out = r_stained * (1.0 - boundary_smooth) + r_cap * boundary_smooth
            g_out = g_stained * (1.0 - boundary_smooth) + g_cap * boundary_smooth
            b_out = b_stained * (1.0 - boundary_smooth) + b_cap * boundary_smooth

            r_out = _np.clip(r_out, 0.0, 1.0).astype(_np.float32)
            g_out = _np.clip(g_out, 0.0, 1.0).astype(_np.float32)
            b_out = _np.clip(b_out, 0.0, 1.0).astype(_np.float32)

        op = float(opacity)
        new_r = r0 * (1.0 - op) + r_out * op
        new_g = g0 * (1.0 - op) + g_out * op
        new_b = b0 * (1.0 - op) + b_out * op

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        mean_shift = float(_np.abs(r_out - r0).mean() + _np.abs(g_out - g0).mean() + _np.abs(b_out - b0).mean())
        print(f"    Frankenthaler Soak-Stain complete "
              f"(n_stains={n_stains} sigma=({sl},{ss}) "
              f"absorption={absorption:.2f} mean_shift={mean_shift:.4f})")
'''

LOST_FOUND_EDGES_PASS = r'''
    def paint_lost_found_edges_pass(
        self,
        found_sharpness:  float = 1.60,
        found_radius:     float = 1.0,
        lost_sigma:       float = 2.2,
        importance_k:     float = 5.0,
        cx:               float = 0.5,
        cy:               float = 0.5,
        focal_weight:     float = 0.45,
        opacity:          float = 0.68,
    ) -> None:
        r"""
        Paint Lost-and-Found Edges -- session 241 artistic improvement.

        The "lost and found" edge doctrine is a cornerstone of classical oil painting
        as practised by Rembrandt, Velazquez, Sargent, and Zorn.  A "found" (hard)
        edge occurs at the boundary of the primary subject, in areas of maximum
        contrast or maximum light-dark transition, and wherever the painter wants
        the eye to stop and look.  A "lost" (soft) edge occurs in the periphery,
        where forms turn away from the light, where one dark mass meets another, or
        where the painter wants the eye to pass through without stopping.  The
        principle is that differential edge quality creates a visual hierarchy:
        found edges lead; lost edges recede.  A painting with every edge equally
        sharp is as loud as one with every note fortissimo.

        DIFFERENTIAL EDGE TREATMENT -- FOUND EDGES SHARPENED, LOST EDGES SOFTENED:

        1. EDGE STRENGTH MAP:
           Compute Sobel magnitude on luminance channel.
           edge_mag = sqrt(sobel_x^2 + sobel_y^2), normalised to [0,1].

        2. LOCAL CONTRAST MAP:
           Compute local standard deviation of luminance in a 9x9 neighbourhood:
           local_std = sqrt(blur(lum^2, sigma=3) - blur(lum, sigma=3)^2)
           Normalise: local_std_norm = local_std / local_std.max().

        3. FOCAL PROXIMITY WEIGHT:
           Radial distance from (cx, cy): dist_norm as fraction of image diagonal.
           proximity = 1.0 / (1.0 + exp(importance_k * (dist_norm - 0.45)))
           (High near centre, low at periphery -- sigmoid fall-off.)

        4. IMPORTANCE SCORE:
           importance = (1 - focal_weight) * (edge_mag * local_std_norm)
                        + focal_weight * proximity
           Combined score balances local edge strength (contrast) against spatial
           proximity to the designated focal centre.

        5. FOUND EDGE SHARPENING:
           Unsharp mask: blurred = gaussian_blur(ch, sigma=found_radius)
                          sharp = ch + found_sharpness * (ch - blurred)
           found_gate = clip(importance, 0, 1)^0.7
           ch_found = ch * (1 - found_gate) + sharp * found_gate

        6. LOST EDGE SOFTENING:
           soft = gaussian_blur(ch, sigma=lost_sigma)
           lost_gate = clip(1.0 - importance, 0, 1)^0.7
           ch_lost = ch_found * (1 - lost_gate) + soft * lost_gate

        NOVEL vs. existing passes:
        (a) DIFFERENTIAL EDGE TREATMENT -- first pass to simultaneously SHARPEN
            high-importance (found) edges via unsharp mask AND SOFTEN low-importance
            (lost) edges via Gaussian blur in a single unified pass governed by the
            same importance metric; no prior pass combines both selective sharpening
            and selective softening; existing edge-aware passes either only boost
            contrast/sharpness or only blur, never both directions at once.
        (b) COMBINED IMPORTANCE METRIC -- first pass to fuse local-contrast-at-edge
            (edge_mag * local_std_norm) with radial focal proximity (sigmoid centred
            at cx, cy) into a single importance score that classifies each pixel on
            the found-to-lost spectrum; prior focal passes (sfumato_focus_pass) blur
            radially but do not also sharpen the focal zone, and prior contrast passes
            sharpen globally without softening peripheral edges.
        (c) CONTINUOUS FOUND/LOST SPECTRUM -- gate functions with 0.7 exponent create
            a continuous spectrum from fully found (sharp) to fully lost (soft) rather
            than a binary threshold; this matches how skilled painters modulate edge
            quality along a continuum rather than a step function.

        found_sharpness : Unsharp-mask amplification factor for found edges.
        found_radius    : Gaussian sigma for unsharp-mask base blur.
        lost_sigma      : Gaussian sigma for lost-edge softening.
        importance_k    : Sigmoid steepness for focal-proximity falloff.
        cx, cy          : Focal centre as fractions of canvas width/height.
        focal_weight    : Blend weight between local-contrast and proximity (0=contrast only, 1=proximity only).
        opacity         : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gauss

        print("    Paint Lost-Found Edges pass (session 241 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # 1. Edge strength: Sobel magnitude on luminance
        from scipy.ndimage import sobel as _sobel
        sx = _sobel(lum, axis=1).astype(_np.float32)
        sy = _sobel(lum, axis=0).astype(_np.float32)
        edge_mag = _np.sqrt(sx * sx + sy * sy).astype(_np.float32)
        edge_norm = edge_mag / (edge_mag.max() + 1e-7)

        # 2. Local contrast: local std in neighbourhood
        lum_sq = lum * lum
        local_mean = _gauss(lum, sigma=3.0).astype(_np.float32)
        local_mean_sq = _gauss(lum_sq, sigma=3.0).astype(_np.float32)
        local_var = _np.clip(local_mean_sq - local_mean * local_mean, 0.0, None)
        local_std = _np.sqrt(local_var).astype(_np.float32)
        std_norm = local_std / (local_std.max() + 1e-7)

        # 3. Focal proximity
        xs = _np.linspace(0.0, 1.0, w, dtype=_np.float32)
        ys = _np.linspace(0.0, 1.0, h, dtype=_np.float32)
        xg, yg = _np.meshgrid(xs, ys)
        dist = _np.sqrt((xg - float(cx)) ** 2 + (yg - float(cy)) ** 2).astype(_np.float32)
        diag = float(_np.sqrt(2.0) * 0.5)
        dist_norm = _np.clip(dist / (diag + 1e-7), 0.0, 1.0).astype(_np.float32)
        ik = float(importance_k)
        proximity = (1.0 / (1.0 + _np.exp(ik * (dist_norm - 0.45)))).astype(_np.float32)

        # 4. Importance score
        fw = float(focal_weight)
        contrast_score = (edge_norm * std_norm).astype(_np.float32)
        cs_norm = contrast_score / (contrast_score.max() + 1e-7)
        importance = ((1.0 - fw) * cs_norm + fw * proximity).astype(_np.float32)
        importance = importance / (importance.max() + 1e-7)

        # 5. Found edge sharpening (unsharp mask)
        fr = float(found_radius)
        fs = float(found_sharpness)
        r_blur_f = _gauss(r0, sigma=fr).astype(_np.float32)
        g_blur_f = _gauss(g0, sigma=fr).astype(_np.float32)
        b_blur_f = _gauss(b0, sigma=fr).astype(_np.float32)

        r_sharp = _np.clip(r0 + fs * (r0 - r_blur_f), 0.0, 1.0).astype(_np.float32)
        g_sharp = _np.clip(g0 + fs * (g0 - g_blur_f), 0.0, 1.0).astype(_np.float32)
        b_sharp = _np.clip(b0 + fs * (b0 - b_blur_f), 0.0, 1.0).astype(_np.float32)

        found_gate = _np.clip(importance, 0.0, 1.0) ** 0.7
        r_found = r0 * (1.0 - found_gate) + r_sharp * found_gate
        g_found = g0 * (1.0 - found_gate) + g_sharp * found_gate
        b_found = b0 * (1.0 - found_gate) + b_sharp * found_gate

        # 6. Lost edge softening
        ls = float(lost_sigma)
        r_soft = _gauss(r_found, sigma=ls).astype(_np.float32)
        g_soft = _gauss(g_found, sigma=ls).astype(_np.float32)
        b_soft = _gauss(b_found, sigma=ls).astype(_np.float32)

        lost_gate = _np.clip(1.0 - importance, 0.0, 1.0) ** 0.7
        r1 = _np.clip(r_found * (1.0 - lost_gate) + r_soft * lost_gate, 0.0, 1.0)
        g1 = _np.clip(g_found * (1.0 - lost_gate) + g_soft * lost_gate, 0.0, 1.0)
        b1 = _np.clip(b_found * (1.0 - lost_gate) + b_soft * lost_gate, 0.0, 1.0)

        op = float(opacity)
        new_r = r0 * (1.0 - op) + r1 * op
        new_g = g0 * (1.0 - op) + g1 * op
        new_b = b0 * (1.0 - op) + b1 * op

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        found_mean = float(found_gate.mean())
        lost_mean  = float(lost_gate.mean())
        print(f"    Paint Lost-Found Edges complete "
              f"(focus=({cx:.2f},{cy:.2f}) found_mean={found_mean:.3f} "
              f"lost_mean={lost_mean:.3f})")
'''

with open('stroke_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'frankenthaler_soak_stain_pass' not in content, 'Frankenthaler pass already exists!'
assert 'paint_lost_found_edges_pass'   not in content, 'Lost-found edges pass already exists!'

content = content + FRANKENTHALER_PASS + LOST_FOUND_EDGES_PASS

with open('stroke_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. stroke_engine.py new length: {len(content)} chars')

# Verify importable
import sys as _sys
for mod in list(_sys.modules.keys()):
    if 'stroke_engine' in mod:
        del _sys.modules[mod]
import stroke_engine
assert hasattr(stroke_engine.Painter, 'frankenthaler_soak_stain_pass'), 'Frankenthaler pass missing'
assert hasattr(stroke_engine.Painter, 'paint_lost_found_edges_pass'),    'Lost-found pass missing'
print('Verified: both new methods present in Painter.')
