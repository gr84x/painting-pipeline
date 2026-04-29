"""Append signac_divisionist_mosaic_pass (153rd mode) + paint_color_bloom_pass to stroke_engine.py (session 242)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

SIGNAC_PASS = r'''
    def signac_divisionist_mosaic_pass(
        self,
        patch_size:  int   = 6,
        comp_mix:    float = 0.35,
        sat_boost:   float = 0.22,
        hue_thresh:  float = 80.0,
        blend_sigma: float = 0.8,
        opacity:     float = 0.72,
    ) -> None:
        r"""
        Signac Divisionist Mosaic -- session 242: ONE HUNDRED AND FIFTY-THIRD distinct mode.

        Implements Paul Signac (1863-1935) Divisionist technique.  A passionate
        sailor and devoted theorist, Signac extended Seurat's pointillism into a
        more muscular, directional practice: where Seurat used tiny circular dots of
        uniform size arranged in a dense, isotropic field, Signac evolved toward
        larger rectangular or square mosaic-like brushstrokes -- each a flat patch of
        pure, unmixed colour whose visual effect depended on optical mixing at distance.
        He grounded his method in three bodies of colour science:

          - Michel-Eugene Chevreul's law of simultaneous contrast: two complementary
            colours placed adjacent will each appear more vivid than either would in
            isolation (orange appears more orange next to blue; blue more intensely
            blue next to orange).
          - Ogden Rood's Modern Chromatics (1879): a scientific model of chromatic
            mixing describing how pigments and coloured lights mix differently, and
            providing the first rigorous colour circle with accurate complementary pairs.
          - Charles Henry's harmonic and aesthetic theories: directional lines carry
            emotional weight; colour intervals mirror musical intervals.

        The result: a canvas that from close range reads as a shimmering mosaic of
        discrete coloured patches, but at gallery distance resolves into luminous,
        vibrating passages of pure optical light.

        THREE-STAGE DIVISIONIST MOSAIC SIMULATION:

        Stage 1 PATCH QUANTIZATION:
        The canvas is subdivided into patch_size x patch_size rectangular tiles.
        For each tile, the mean RGB colour is computed by vectorised block-reshape
        mean pooling (no per-pixel Python loops):
            r_tile = mean(r_ch[tile]) over all pixels in the tile
        The mean is broadcast back to the full tile, producing flat-colour mosaic
        patches -- each representing one of Signac's rectangular brushstrokes.
        NOVEL: (a) VECTORISED RECTANGULAR PATCH QUANTIZATION -- first pass to apply
        divisionist colour quantization via numpy block-reshape mean pooling, producing
        a rectangular-patch mosaic; pointillist_pass applies circular dots at random
        positions; fauvist_mosaic_pass uses Voronoi / random zone assignment; neither
        uses rectangular block-mean quantization with numpy reshape.

        Stage 2 COMPLEMENTARY INTERLEAVING:
        Within each patch, a tile-level checkerboard mask -- (patch_row + patch_col) % 2 --
        assigns even tiles to the primary (mean) colour and odd tiles to the complementary
        colour (hue rotated 180 degrees on the colour wheel, same saturation and value):
            comp_hue = (patch_hue + 180.0) % 360.0
            comp_rgb = hsv_to_rgb(comp_hue, patch_sat, patch_val)
            mosaic_pixel = primary  if (patch_row + patch_col) % 2 == 0
                         = primary * (1 - comp_mix) + complement * comp_mix  otherwise
        This implements Chevreul's simultaneous contrast at the intra-patch level:
        each tile contains both the dominant hue and its complement, maximising the
        optical vibrancy of the mosaic at close range.
        NOVEL: (b) TILE-LEVEL COMPLEMENTARY CHECKERBOARD -- first pass to interleave
        the primary colour and its 180-degree hue complement within the same quantized
        patch using a tile-index (not single-pixel) checkerboard; chromatic_split_pass
        shifts RGB channels laterally; pointillist_pass places random complementary
        dots offset by a fixed distance; neither interleaves hue-opposite tiles within
        the same quantized block.

        Stage 3 SIMULTANEOUS CONTRAST BOUNDARY BOOST:
        At boundaries between adjacent patches, Chevreul's simultaneous contrast
        effect intensifies: opposing-hue colours at a shared edge appear more vivid
        than identical patches surrounded by neutral neighbours.  To simulate this:
            hdiff = min(|hue_A - hue_B|, 360 - |hue_A - hue_B|)  (wrap-around distance)
            boost = sat_boost * clip((hdiff - hue_thresh) / (180 - hue_thresh), 0, 1)
            sat_boosted = clip(patch_sat + boost * is_boundary_pixel, 0, 1)
        Applied only to pixels on the boundary rows/columns of each patch.
        NOVEL: (c) SIMULTANEOUS CONTRAST SATURATION BOOST AT OPPOSING-HUE BOUNDARIES
        -- first pass to detect adjacent patches with large hue differences (> hue_thresh)
        and boost saturation specifically at those inter-patch boundaries proportionally
        to how far the adjacent hues are apart on the colour wheel; no prior pass applies
        Chevreul simultaneous contrast as a boundary-localised, hue-distance-weighted
        saturation boost.

        patch_size  : Width/height of each rectangular mosaic patch in pixels.
        comp_mix    : Fraction of complementary colour blended into odd-tile patches (0..1).
        sat_boost   : Maximum saturation boost at high-hue-contrast patch boundaries.
        hue_thresh  : Minimum hue difference (degrees) before boundary boost activates.
        blend_sigma : Light Gaussian sigma for post-mosaic integration blur.
        opacity     : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gauss

        print("    Signac Divisionist Mosaic pass (session 242: 153rd mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        ps = max(2, int(patch_size))

        # ── Stage 1: Patch quantization via block-reshape mean pooling ────────
        ph = ((h - 1) // ps + 1) * ps
        pw = ((w - 1) // ps + 1) * ps

        def _pad(a):
            return _np.pad(a, ((0, ph - h), (0, pw - w)), mode='edge').astype(_np.float32)

        rp, gp, bp_ch = _pad(r0), _pad(g0), _pad(b0)
        n_ph, n_pw = ph // ps, pw // ps

        rr = rp.reshape(n_ph, ps, n_pw, ps).mean(axis=(1, 3)).astype(_np.float32)
        gg = gp.reshape(n_ph, ps, n_pw, ps).mean(axis=(1, 3)).astype(_np.float32)
        bb = bp_ch.reshape(n_ph, ps, n_pw, ps).mean(axis=(1, 3)).astype(_np.float32)

        patch_r = _np.repeat(_np.repeat(rr, ps, axis=0), ps, axis=1)[:h, :w].astype(_np.float32)
        patch_g = _np.repeat(_np.repeat(gg, ps, axis=0), ps, axis=1)[:h, :w].astype(_np.float32)
        patch_b = _np.repeat(_np.repeat(bb, ps, axis=0), ps, axis=1)[:h, :w].astype(_np.float32)

        # ── RGB <-> HSV helpers (fully vectorised) ────────────────────────────
        def _rgb_to_hsv(r, g, b):
            maxc = _np.maximum(r, _np.maximum(g, b)).astype(_np.float32)
            minc = _np.minimum(r, _np.minimum(g, b)).astype(_np.float32)
            v    = maxc
            diff = (maxc - minc).astype(_np.float32)
            s    = _np.where(maxc > 1e-7, diff / (maxc + 1e-7), 0.0).astype(_np.float32)
            eps  = 1e-7
            h_deg = _np.zeros_like(r, dtype=_np.float32)
            mr = (maxc == r) & (diff > eps)
            mg = (maxc == g) & ~mr & (diff > eps)
            mb = (maxc == b) & ~mr & ~mg & (diff > eps)
            h_deg[mr] = (60.0 * ((g[mr] - b[mr]) / (diff[mr] + eps))) % 360.0
            h_deg[mg] = (60.0 * ((b[mg] - r[mg]) / (diff[mg] + eps))) + 120.0
            h_deg[mb] = (60.0 * ((r[mb] - g[mb]) / (diff[mb] + eps))) + 240.0
            h_deg = h_deg % 360.0
            return h_deg, s, v

        def _hsv_to_rgb(h_deg, s, v):
            h6 = (h_deg / 60.0).astype(_np.float32)
            i  = _np.floor(h6).astype(_np.int32) % 6
            f  = (h6 - _np.floor(h6)).astype(_np.float32)
            p  = (v * (1.0 - s)).astype(_np.float32)
            q  = (v * (1.0 - f * s)).astype(_np.float32)
            t  = (v * (1.0 - (1.0 - f) * s)).astype(_np.float32)
            r_ = _np.select([i == 0, i == 1, i == 2, i == 3, i == 4], [v, q, p, p, t], default=v)
            g_ = _np.select([i == 0, i == 1, i == 2, i == 3, i == 4], [t, v, v, q, p], default=p)
            b_ = _np.select([i == 0, i == 1, i == 2, i == 3, i == 4], [p, p, t, v, v], default=q)
            return r_.astype(_np.float32), g_.astype(_np.float32), b_.astype(_np.float32)

        ph_map, ps_map, pv_map = _rgb_to_hsv(patch_r, patch_g, patch_b)

        # ── Stage 2: Complementary interleaving ──────────────────────────────
        # Tile-level checkerboard by patch row/col index
        iy = _np.arange(h)[:, None] // ps   # patch row index
        ix = _np.arange(w)[None, :] // ps   # patch col index
        tile_check = ((iy + ix) % 2).astype(_np.float32)  # 0=primary, 1=complement

        comp_h = (ph_map + 180.0) % 360.0
        comp_r, comp_g, comp_b_ch = _hsv_to_rgb(comp_h, ps_map, pv_map)

        cm = float(comp_mix)
        r_mosaic = _np.where(tile_check > 0.5, patch_r * (1.0 - cm) + comp_r * cm, patch_r).astype(_np.float32)
        g_mosaic = _np.where(tile_check > 0.5, patch_g * (1.0 - cm) + comp_g * cm, patch_g).astype(_np.float32)
        b_mosaic = _np.where(tile_check > 0.5, patch_b * (1.0 - cm) + comp_b_ch * cm, patch_b).astype(_np.float32)

        # ── Stage 3: Simultaneous contrast boundary saturation boost ─────────
        ht = float(hue_thresh)
        sb = float(sat_boost)

        # Hue-difference map: compare each patch hue with rightward and downward neighbor
        hue_r_shift = _np.roll(ph_map, -1, axis=1)
        hue_d_shift = _np.roll(ph_map, -1, axis=0)
        hdiff_h = _np.abs(ph_map - hue_r_shift)
        hdiff_h = _np.minimum(hdiff_h, 360.0 - hdiff_h)
        hdiff_v = _np.abs(ph_map - hue_d_shift)
        hdiff_v = _np.minimum(hdiff_v, 360.0 - hdiff_v)
        hdiff   = _np.maximum(hdiff_h, hdiff_v).astype(_np.float32)

        # Boundary mask: pixels on edge rows/cols of each patch
        prow = _np.arange(h)[:, None] % ps
        pcol = _np.arange(w)[None, :] % ps
        is_boundary = ((prow == 0) | (prow == ps - 1) |
                       (pcol == 0) | (pcol == ps - 1)).astype(_np.float32)

        boost = _np.clip((hdiff - ht) / (180.0 - ht + 1e-7), 0.0, 1.0) * sb * is_boundary
        boost = boost.astype(_np.float32)

        hm, sm, vm = _rgb_to_hsv(r_mosaic, g_mosaic, b_mosaic)
        sm_boosted = _np.clip(sm + boost, 0.0, 1.0).astype(_np.float32)
        r_out, g_out, b_out = _hsv_to_rgb(hm, sm_boosted, vm)

        # Light integration blur
        if float(blend_sigma) > 0.05:
            bs = float(blend_sigma)
            r_out = _gauss(r_out, sigma=bs).astype(_np.float32)
            g_out = _gauss(g_out, sigma=bs).astype(_np.float32)
            b_out = _gauss(b_out, sigma=bs).astype(_np.float32)

        r_out = _np.clip(r_out, 0.0, 1.0)
        g_out = _np.clip(g_out, 0.0, 1.0)
        b_out = _np.clip(b_out, 0.0, 1.0)

        op    = float(opacity)
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

        mean_sat = float(sm.mean())
        mean_boost = float(boost.mean())
        print(f"    Signac Divisionist Mosaic complete "
              f"(patch_size={ps} comp_mix={cm:.2f} "
              f"mean_sat={mean_sat:.3f} mean_boundary_boost={mean_boost:.4f})")
'''

COLOR_BLOOM_PASS = r'''
    def paint_color_bloom_pass(
        self,
        bloom_threshold: float = 0.52,
        bloom_sigma:     float = 3.0,
        bloom_strength:  float = 0.28,
        chroma_shift:    float = 0.015,
        opacity:         float = 0.65,
    ) -> None:
        r"""
        Paint Color Bloom -- session 242 artistic improvement.

        In any physical painting made with oil or egg-tempera pigments, highly
        saturated colours exhibit a phenomenon painters call "irradiation" or colour
        bloom: vivid reds, blues, and yellows appear to glow or spread slightly beyond
        their physical paint boundary, halating into neighbouring, less-saturated areas.
        This is partly perceptual (the eye's over-response to intense chroma) and partly
        optical: highly saturated pigments absorb and re-emit light with a very selective
        spectral response, producing slight chromatic scattering at their physical edge.
        The blue channel scatters more than red (shorter wavelength, higher diffraction
        index), producing a faint chromatic fringe -- blue bleeding slightly further than
        red -- at the boundary of any intensely saturated region.

        THREE-STAGE SATURATION-GATED COLOUR BLOOM:

        Stage 1 SATURATION-GATED BLOOM MASK:
        For each pixel, compute saturation S = (max_rgb - min_rgb) / max_rgb.
        Create a graduated bloom mask weighted by excess saturation above threshold:
            bloom_mask = clip((S - bloom_threshold) / (1.0 - bloom_threshold), 0, 1)
        Only pixels with S > bloom_threshold contribute to the bloom source.
        The graduated weighting means more saturated pixels create a stronger bloom.
        NOVEL: (a) SATURATION-THRESHOLD-GATED BLOOM SOURCE -- first pass to apply
        colour irradiation specifically and only to pixels exceeding a per-pixel
        saturation threshold, with the bloom mask weighted proportionally to the
        excess saturation; all prior passes apply effects uniformly or gated by
        luminance (not saturation); the saturation gate is physically correct because
        irradiation is a property of spectral purity (chroma), not brightness (value).

        Stage 2 GAUSSIAN COLOUR BLEEDING:
        The bloom mask is spread outward by Gaussian diffusion to model the halo of
        irradiation in adjacent, less-saturated pixels:
            bloom_spread = gaussian_blur(bloom_mask, sigma=bloom_sigma)
            effective_strength = bloom_spread * bloom_strength
            ch_bloomed = ch_original * (1 - effective_strength) + ch_blurred * effective_strength
        where ch_blurred = gaussian_blur(ch_original, sigma=bloom_sigma).
        The blurred channel carries the saturated source colour outward; the bloom_spread
        mask controls where that colour bleeds and by how much.
        NOVEL: (b) SATURATION-PROPORTIONAL BLOOM SPREAD -- first pass where the
        intensity of colour bleeding into adjacent pixels is proportional to how much
        the source pixel's saturation exceeds the threshold; the spread is not just
        the Gaussian blur of the image but the Gaussian spread of the SATURATION EXCESS
        MASK, so the bloom extends further from more deeply saturated sources and
        barely at all from borderline-saturated ones.

        Stage 3 CHROMATIC FRINGE:
        Blue light (shorter wavelength, higher refractive index) diffracts slightly
        more at colour boundaries than red light, creating a faint blue-biased fringe
        at the outer edge of highly saturated colour zones:
            b_extra = gaussian_blur(b_channel, sigma=bloom_sigma * (1 + 2*chroma_shift))
            fringe_mask = clip(blur(bloom_mask, sigma=bloom_sigma*(1+chroma_shift))
                               - bloom_mask, 0, 1)
            b_final = b_bloomed + fringe_mask * chroma_shift * b_extra
        The fringe_mask isolates the OUTER ANNULAR ZONE of the bloom halo -- the region
        where the spread exceeds the source but is still elevated -- and adds a small
        blue bias there.
        NOVEL: (c) SATURATION-GATED DIFFERENTIAL CHROMATIC FRINGE -- first pass to
        apply a blue-biased chromatic spread specifically at the outer annular zone of
        high-saturation colour halos; the existing chromatic_split_pass applies a
        uniform lateral channel offset across the entire canvas; this pass targets
        only the outer fringe of saturation-gated bloom regions, and only boosts blue
        (not all channels), matching the physical optics of short-wavelength diffraction.

        bloom_threshold : Minimum saturation (0..1) for a pixel to be a bloom source.
        bloom_sigma     : Gaussian sigma for colour spread and fringe calculation.
        bloom_strength  : Maximum blend fraction of bloomed vs original colour in adjacent pixels.
        chroma_shift    : Magnitude of blue-channel extra spread (as fraction of bloom_sigma).
        opacity         : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gauss

        print("    Paint Color Bloom pass (session 242 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Saturation-gated bloom mask ─────────────────────────────
        maxc = _np.maximum(r0, _np.maximum(g0, b0)).astype(_np.float32)
        minc = _np.minimum(r0, _np.minimum(g0, b0)).astype(_np.float32)
        sat  = _np.where(maxc > 1e-7, (maxc - minc) / (maxc + 1e-7), 0.0).astype(_np.float32)

        bt = float(bloom_threshold)
        bloom_mask = _np.clip((sat - bt) / (1.0 - bt + 1e-7), 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Gaussian colour bleeding ────────────────────────────────
        bs  = float(bloom_sigma)
        bst = float(bloom_strength)
        cs  = float(chroma_shift)

        r_blur = _gauss(r0, sigma=bs).astype(_np.float32)
        g_blur = _gauss(g0, sigma=bs).astype(_np.float32)
        b_blur = _gauss(b0, sigma=bs).astype(_np.float32)   # base blur for bleeding

        bloom_spread = _gauss(bloom_mask, sigma=bs).astype(_np.float32)
        bloom_spread = _np.clip(bloom_spread, 0.0, 1.0)

        eff = bloom_spread * bst
        r_bloomed = _np.clip(r0 * (1.0 - eff) + r_blur * eff, 0.0, 1.0).astype(_np.float32)
        g_bloomed = _np.clip(g0 * (1.0 - eff) + g_blur * eff, 0.0, 1.0).astype(_np.float32)
        b_bloomed = _np.clip(b0 * (1.0 - eff) + b_blur * eff, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Chromatic fringe (blue bleeds further) ──────────────────
        b_extra    = _gauss(b0, sigma=bs * (1.0 + 2.0 * cs)).astype(_np.float32)
        fringe_spread = _gauss(bloom_mask, sigma=bs * (1.0 + cs)).astype(_np.float32)
        fringe_mask   = _np.clip(fringe_spread - bloom_mask, 0.0, 1.0).astype(_np.float32)

        b_final = _np.clip(b_bloomed + fringe_mask * cs * b_extra, 0.0, 1.0).astype(_np.float32)

        r_out = r_bloomed
        g_out = g_bloomed
        b_out = b_final

        op    = float(opacity)
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

        mean_bloom_coverage = float(bloom_spread.mean())
        mean_sat = float(sat.mean())
        print(f"    Paint Color Bloom complete "
              f"(threshold={bt:.2f} sigma={bs:.1f} "
              f"mean_sat={mean_sat:.3f} bloom_coverage={mean_bloom_coverage:.3f})")
'''

with open('stroke_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'signac_divisionist_mosaic_pass' not in content, 'Signac pass already exists!'
assert 'paint_color_bloom_pass'         not in content, 'Color bloom pass already exists!'

content = content + SIGNAC_PASS + COLOR_BLOOM_PASS

with open('stroke_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. stroke_engine.py new length: {len(content)} chars')

import sys as _sys
for mod in list(_sys.modules.keys()):
    if 'stroke_engine' in mod:
        del _sys.modules[mod]
import stroke_engine
assert hasattr(stroke_engine.Painter, 'signac_divisionist_mosaic_pass'), 'Signac pass missing'
assert hasattr(stroke_engine.Painter, 'paint_color_bloom_pass'),         'Color bloom pass missing'
print('Verified: both new methods present in Painter.')
