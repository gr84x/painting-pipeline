"""Insert richter_squeegee_drag_pass and paint_surface_tooth_pass into
stroke_engine.py (session 252).

NOTE: This script was already executed during session 252. Running it again
will fail the existence check. It is preserved as a record of the change.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

SQUEEGEE_PASS = """
    def richter_squeegee_drag_pass(
        self,
        n_bands:        int   = 22,
        band_min:       int   = 28,
        band_max:       int   = 90,
        drag_fraction:  float = 0.62,
        drag_offset:    int   = 8,
        sat_threshold:  float = 0.28,
        trail_length:   int   = 48,
        trail_strength: float = 0.55,
        residue_amp:    float = 0.055,
        opacity:        float = 0.80,
        seed:           int   = 252,
    ) -> None:
        r\"\"\"Gerhard Richter Squeegee Drag -- session 252, 163rd distinct painting mode.

        THREE-STAGE SQUEEGEE DRAG:

        Stage 1 HORIZONTAL DRAG BAND DECOMPOSITION: Divide the canvas into
        n_bands horizontal strips of randomly varied height, each between
        band_min and band_max pixels (RNG seeded with seed). For each band,
        simulate a lateral squeegee drag by blending pixel colours toward the
        mean colour of rows at +/- drag_offset above and below the band centre,
        scaled by drag_fraction. The blended result reproduces the squeegee
        picking up paint from adjacent zones and mixing it as it travels across.
        Accumulate a per-pixel drag weight map (1.0 within band interiors,
        tapering to 0 at boundaries via cosine ramp of width 6px).
        NOVEL: (a) SPATIALLY PARTITIONED HORIZONTAL DRAG BAND AVERAGING --
        first pass to mix pixel colours via explicit band decomposition with
        adjacent-row sampling (drag_offset rows above/below); all prior
        directional blur passes (bacon smear, mitchell arc spread, kollwitz
        charcoal) apply either global convolution kernels or mark-local
        operations -- none decompose the canvas into random-height horizontal
        drag bands with cross-band colour averaging as the primary colour
        stage.

        Stage 2 LATERAL PIGMENT CHANNEL TRAILS: At each inter-band boundary
        (transition rows between adjacent bands), detect pixels whose HSV
        saturation exceeds sat_threshold. For each such pixel, apply a 1-D
        horizontal mean-filter of width trail_length centred on that pixel,
        then blend trail_strength of this filtered value back over the current
        pixel colour. This creates the concentrated pigment channel ridges left
        by the squeegee blade edge -- the colour rivers that are the most
        recognisable visual signature of Richter's abstract paintings.
        NOVEL: (b) SATURATION-GATED DIRECTIONAL TRAIL BLUR AT DRAG BOUNDARIES
        -- first pass to detect pigment concentration at drag-band boundary
        rows and apply a directional horizontal trail blur exclusively at those
        boundaries as a distinct secondary stage; basquiat marks (s249) apply
        a random directional segment raster; bacon (s251) applies a directional
        linear smear modulated by mid-tone luminance -- neither gates the trail
        operation on band boundary position combined with per-pixel saturation.

        Stage 3 DRAG RESIDUE LUMINANCE MODULATION: Within each drag band,
        apply a sinusoidal luminance modulation with frequency 1 cycle per
        band-height and amplitude residue_amp. The modulation phase is set so
        that the leading edge of each band (top row) receives a positive
        luminance shift (paint thinned by the blade advancing) and the
        trailing edge (bottom row) receives a negative shift (paint
        accumulated ahead of the blade). The effect is a subtle periodic
        brightening-darkening rhythm across band boundaries.
        NOVEL: (c) BAND-COORDINATED SINUSOIDAL LUMINANCE MODULATION -- first
        pass to apply a per-band sinusoidal brightness variation parameterised
        by fractional position within the band (0=leading edge, 1=trailing
        edge) to simulate squeegee paint thickness variation; no prior pass
        applies luminance variation coordinated to explicitly defined band
        positions; paint_aerial_perspective uses gradient falloff by global
        y-coordinate; this pass uses per-band local phase position.

        n_bands        : Number of horizontal drag bands.
        band_min       : Minimum band height in pixels.
        band_max       : Maximum band height in pixels.
        drag_fraction  : Blend fraction toward adjacent-row mean (0=no drag, 1=full).
        drag_offset    : Y-distance (rows) to sample for adjacent colour mixing.
        sat_threshold  : HSV saturation threshold for pigment trail detection.
        trail_length   : Width of horizontal trail blur in pixels.
        trail_strength : Blend fraction for trail blur (0=none, 1=full trail).
        residue_amp    : Amplitude of sinusoidal luminance modulation (0–0.15).
        opacity        : Final composite opacity (0=no change, 1=full effect).
        seed           : RNG seed for reproducible band layout.
        \"\"\"
        import numpy as _np

        print("    Richter Squeegee Drag pass (session 252, 163rd mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        rng = _np.random.default_rng(int(seed))

        # Build random band layout
        bmin = max(int(band_min), 4)
        bmax = max(int(band_max), bmin + 4)
        band_heights = rng.integers(bmin, bmax + 1, size=int(n_bands)).tolist()
        # Fill remaining canvas rows with the last band height
        bands = []
        y = 0
        for bh in band_heights:
            if y >= h:
                break
            end = min(y + bh, h)
            bands.append((y, end))
            y = end
        if y < h:
            bands.append((y, h))

        # Stage 1: Horizontal drag band decomposition
        r1 = r0.copy()
        g1 = g0.copy()
        b1 = b0.copy()
        drag_weight = _np.zeros((h, w), dtype=_np.float32)
        off = max(int(drag_offset), 1)
        df = float(drag_fraction)
        taper = 6

        for (y0, y1) in bands:
            bh = max(y1 - y0, 1)
            # Rows to sample for adjacent colour
            sample_lo = max(y0 - off, 0)
            sample_hi = min(y1 + off, h)
            mean_r = r0[sample_lo:sample_hi, :].mean(axis=0)
            mean_g = g0[sample_lo:sample_hi, :].mean(axis=0)
            mean_b = b0[sample_lo:sample_hi, :].mean(axis=0)

            # Interior drag weight with cosine taper at band edges
            for row in range(y0, y1):
                local_pos = row - y0
                # Cosine taper from band top and bottom
                t_top = min(local_pos, taper) / float(taper)
                t_bot = min((y1 - 1 - row), taper) / float(taper)
                w_factor = (
                    (1.0 - _np.cos(_np.pi * t_top)) / 2.0 *
                    (1.0 - _np.cos(_np.pi * t_bot)) / 2.0
                )
                drag_weight[row, :] = float(w_factor)
                r1[row, :] = r0[row, :] * (1.0 - df * w_factor) + mean_r * df * w_factor
                g1[row, :] = g0[row, :] * (1.0 - df * w_factor) + mean_g * df * w_factor
                b1[row, :] = b0[row, :] * (1.0 - df * w_factor) + mean_b * df * w_factor

        # Stage 2: Lateral pigment channel trails at band boundaries
        r2 = r1.copy()
        g2 = g1.copy()
        b2 = b1.copy()

        sat_thr = float(sat_threshold)
        tl = max(int(trail_length), 1)
        ts = float(trail_strength)

        # Compute HSV saturation of dragged result
        max_c = _np.maximum(_np.maximum(r1, g1), b1)
        min_c = _np.minimum(_np.minimum(r1, g1), b1)
        sat_1 = _np.where(max_c > 1e-8, (max_c - min_c) / (max_c + 1e-8), 0.0).astype(_np.float32)

        # Boundary rows: rows that are within 2 pixels of a band edge
        boundary_mask = _np.zeros(h, dtype=bool)
        for (y0, y1) in bands:
            for dy in range(min(3, y1 - y0)):
                if y0 + dy < h:
                    boundary_mask[y0 + dy] = True
                if y1 - 1 - dy >= 0:
                    boundary_mask[y1 - 1 - dy] = True

        half_t = tl // 2
        pad = _np.zeros(w + 2 * half_t, dtype=_np.float32)

        for row in range(h):
            if not boundary_mask[row]:
                continue
            sat_row = sat_1[row, :]
            high_sat = (sat_row > sat_thr)
            if not high_sat.any():
                continue

            # Horizontal mean filter for trail blur
            def _htrail(ch_row):
                padded = _np.pad(ch_row, half_t, mode='edge')
                cs = _np.cumsum(padded)
                sums = cs[tl:] - cs[:-tl]
                return (sums / tl).astype(_np.float32)

            trail_r = _htrail(r1[row, :])
            trail_g = _htrail(g1[row, :])
            trail_b = _htrail(b1[row, :])

            blend = (high_sat * ts).astype(_np.float32)
            r2[row, :] = r1[row, :] * (1.0 - blend) + trail_r * blend
            g2[row, :] = g1[row, :] * (1.0 - blend) + trail_g * blend
            b2[row, :] = b1[row, :] * (1.0 - blend) + trail_b * blend

        # Stage 3: Drag residue sinusoidal luminance modulation
        r3 = r2.copy()
        g3 = g2.copy()
        b3 = b2.copy()
        amp = float(residue_amp)

        for (y0, y1) in bands:
            bh = float(max(y1 - y0, 1))
            for row in range(y0, y1):
                t = (row - y0) / bh   # 0 at leading edge, 1 at trailing
                # Positive at leading (paint thinned), negative at trailing
                lum_mod = amp * _np.cos(_np.pi * t)
                r3[row, :] = _np.clip(r2[row, :] + lum_mod, 0.0, 1.0)
                g3[row, :] = _np.clip(g2[row, :] + lum_mod, 0.0, 1.0)
                b3[row, :] = _np.clip(b2[row, :] + lum_mod, 0.0, 1.0)

        # Final composite
        op = float(opacity)
        new_r = r0 * (1.0 - op) + r3 * op
        new_g = g0 * (1.0 - op) + g3 * op
        new_b = b0 * (1.0 - op) + b3 * op

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()
        n_boundary = int(boundary_mask.sum())
        print(f"    Squeegee Drag complete ({len(bands)} bands, {n_boundary} boundary rows)")
"""

SURFACE_TOOTH_PASS = """
    def paint_surface_tooth_pass(
        self,
        grain_size:        int   = 12,
        fiber_amplitude:   float = 0.030,
        cross_boost:       float = 0.018,
        light_angle:       float = 42.0,
        ridge_strength:    float = 0.025,
        opacity:           float = 0.72,
        seed:              int   = 4252,
    ) -> None:
        r\"\"\"Canvas Surface Tooth -- session 252 improvement pass.

        THREE-STAGE CANVAS SURFACE TOOTH:

        Simulates the physical texture of a woven linen or cotton canvas --
        the raised warp-and-weft fiber grid that gives painted surfaces their
        characteristic tactile quality.

        Stage 1 WOVEN FIBER PATTERN: Generate a dual-direction periodic
        fiber texture using two sinusoidal grids:
          H_fiber(x, y) = sin(2π * y / grain_size + noise_y[x,y])
          V_fiber(x, y) = sin(2π * x / grain_size + noise_x[x,y])
        Combine: fiber_map = H_fiber * V_fiber (product gives crossing peaks)
        Add fiber_amplitude * fiber_map to luminance channel.
        NOVEL: (a) DUAL-DIRECTION WARP-AND-WEFT SINUSOIDAL FIBER PRODUCT --
        first pass to generate a simulated woven fiber texture using the
        product of two orthogonal sinusoidal grids (H × V) to produce peaks
        at fiber crossings and valleys along fiber runs; prior texture passes
        (make_linen_texture, make_cold_press_texture) generate isotropic or
        Gaussian noise textures -- none compute a structured periodic fiber
        grid with directional warp/weft periodicity and crossing peaks.

        Stage 2 FIBER CROSSING MICRO-CONTRAST: At fiber crossing points
        (where fiber_map > 0.6, i.e., both H and V are in phase), apply a
        per-pixel local micro-contrast boost: darken dark values, lighten
        light values by cross_boost in the [0.2, 0.8] luminance range.
        This simulates paint accumulating at raised fiber crossings (where
        the weave peak catches and holds paint).
        NOVEL: (b) PEAK-GATED LOCAL MICRO-CONTRAST AT FIBER INTERSECTIONS --
        first pass to apply luminance-dependent micro-contrast boost
        exclusively at fiber crossing peak locations; paint_optical_vibration
        applies contrast amplification globally; all prior contrast passes
        operate on full-canvas luminance criteria -- none gate contrast
        adjustment on a structured spatial peak-detection grid.

        Stage 3 DIRECTIONAL RIDGE CATCH-LIGHT: Along horizontal fiber
        ridges (H_fiber > 0.5), apply a directional luminance highlight based
        on the dot product of each ridge normal with the light direction
        (light_angle degrees from horizontal). Ridge normals point upward from
        the weave surface; ridges facing the light source receive a luminance
        boost of ridge_strength, those facing away receive a subtle dimming.
        NOVEL: (c) ANISOTROPIC DIRECTIONAL HIGHLIGHT DERIVED FROM SURFACE
        RELIEF ORIENTATION -- first pass to compute ridge normals from a
        periodic surface relief map and apply a directional diffuse-light
        highlight based on the ridge-normal vs. light-vector dot product;
        no prior pass applies directional lighting derived from simulated
        surface topology.

        grain_size      : Fiber period in pixels (warp/weft spacing).
        fiber_amplitude : Brightness modulation amplitude from fiber grid.
        cross_boost     : Micro-contrast amplification at fiber crossings.
        light_angle     : Light source direction in degrees (0=from right,
                          90=from below, 42=upper-right typical studio).
        ridge_strength  : Luminance boost/dim amplitude for ridge catch-light.
        opacity         : Final composite opacity (0=no change, 1=full effect).
        seed            : RNG seed for fiber phase noise.
        \"\"\"
        import numpy as _np

        print("    Surface Tooth pass (session 252 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        rng = _np.random.default_rng(int(seed))
        gs = max(int(grain_size), 2)

        # Stage 1: Woven fiber pattern
        ys = _np.arange(h, dtype=_np.float32)
        xs = _np.arange(w, dtype=_np.float32)
        yy, xx = _np.meshgrid(ys, xs, indexing='ij')

        # Small random phase noise per-pixel to break periodicity
        noise_y = rng.uniform(-0.3, 0.3, size=(h, w)).astype(_np.float32)
        noise_x = rng.uniform(-0.3, 0.3, size=(h, w)).astype(_np.float32)

        H_fiber = _np.sin(2.0 * _np.pi * (yy / gs) + noise_y).astype(_np.float32)
        V_fiber = _np.sin(2.0 * _np.pi * (xx / gs) + noise_x).astype(_np.float32)
        fiber_map = (H_fiber * V_fiber).astype(_np.float32)   # [-1, 1]

        fa = float(fiber_amplitude)
        lum0 = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        lum1 = _np.clip(lum0 + fa * fiber_map, 0.0, 1.0).astype(_np.float32)

        # Apply luminance change proportionally to RGB channels
        scale = _np.where(lum0 > 1e-5, lum1 / (lum0 + 1e-5), 1.0).astype(_np.float32)
        scale = _np.clip(scale, 0.0, 2.0)
        r1 = _np.clip(r0 * scale, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * scale, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * scale, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Fiber crossing micro-contrast
        crossing_mask = (fiber_map > 0.60).astype(_np.float32)
        cb = float(cross_boost)
        lum2 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        # Micro-contrast: push away from 0.5 for mid-tones
        mid_weight = _np.where(
            (lum2 > 0.20) & (lum2 < 0.80),
            2.0 * _np.abs(lum2 - 0.5) * crossing_mask,
            0.0
        ).astype(_np.float32)
        micro_shift = cb * _np.sign(lum2 - 0.5) * mid_weight
        r2 = _np.clip(r1 + micro_shift, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 + micro_shift, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 + micro_shift, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Directional ridge catch-light
        ang_rad = float(light_angle) * _np.pi / 180.0
        # Light direction vector (in image plane)
        lx = float(_np.cos(ang_rad))
        ly = -float(_np.sin(ang_rad))   # y increases downward
        # Ridge normals from H_fiber gradient (horizontal ridges)
        ridge_mask = (H_fiber > 0.50).astype(_np.float32)
        # Normal points upward (negative y in image coords)
        # Dot with light direction: lx * 0 + ly * (-1) = -ly = sin(angle)
        dot = float(-ly)   # constant for horizontal ridges
        rs = float(ridge_strength)
        light_mod = rs * dot * ridge_mask
        r3 = _np.clip(r2 + light_mod, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 + light_mod, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 + light_mod, 0.0, 1.0).astype(_np.float32)

        # Final composite
        op = float(opacity)
        new_r = r0 * (1.0 - op) + r3 * op
        new_g = g0 * (1.0 - op) + g3 * op
        new_b = b0 * (1.0 - op) + b3 * op

        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()
        fiber_coverage = float((fiber_map > 0.6).mean())
        print(f"    Surface Tooth complete (grain_size={grain_size}, "
              f"fiber_coverage={fiber_coverage:.3f})")
"""

se_path = os.path.join(REPO, "stroke_engine.py")
with open(se_path, "r", encoding="utf-8") as f:
    content = f.read()

if "richter_squeegee_drag_pass" in content:
    print("richter_squeegee_drag_pass already exists, skipping")
else:
    content = content + SQUEEGEE_PASS + SURFACE_TOOTH_PASS
    with open(se_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Done. stroke_engine.py new length: {len(content)} chars")
