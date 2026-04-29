"""Append de_stael_palette_knife_mosaic_pass and paint_halation_pass to stroke_engine.py (session 248)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

DE_STAEL_PASS = '''
    def de_stael_palette_knife_mosaic_pass(
        self,
        tile_h:           int   = 24,
        tile_w:           int   = 32,
        knife_angle_deg:  float = 12.0,
        knife_texture_str: float = 0.06,
        boundary_width:   int   = 2,
        boundary_strength: float = 0.18,
        opacity:          float = 0.85,
    ) -> None:
        r"""Nicolas de Stael Palette Knife Mosaic -- session 248: ONE HUNDRED AND FIFTY-NINTH distinct mode.

        THREE-STAGE PALETTE KNIFE MOSAIC (Nicolas de Stael):

        Stage 1 RECTANGULAR TILE MEAN QUANTIZATION: Divide the canvas into a
        grid of non-overlapping rectangular tiles of size (tile_h x tile_w)
        pixels, with edge tiles cropped to the canvas boundary. For each tile,
        compute the arithmetic mean of the R, G, and B channels across all pixels
        within the tile. Replace every pixel in the tile with this mean colour.
        The result is a mosaic of flat rectangular colour planes, each carrying
        the average hue and luminance of the original region it covers.
        NOVEL: (a) RECTANGULAR TILE MEAN QUANTIZATION AS PRIMARY COLOUR STAGE --
        first pass to divide the canvas into a rectangular grid and replace each
        tile with its mean colour (spatial mean pooling over rectangular blocks)
        as a primary image-processing operation; prior passes use Gaussian blurs
        (spatially-continuous weighted averaging), Sobel operators (edge
        detection from adjacent pixel differences), frequency decompositions
        (DoG bandpass), or percentile operations -- none replace pixel values
        with the mean of a rectangular tile grid.

        Stage 2 INTRA-TILE DIRECTIONAL KNIFE GRADIENT: Build a (tile_h x tile_w)
        directional gradient template by computing, at each local pixel position
        (dy, dx) within the tile (centred, normalised to [-1, +1]),
        t = dx * cos(a) + dy * sin(a), where a = knife_angle_deg in radians.
        Tile this template across the full canvas (cropping edge tiles to canvas
        bounds). Multiply the template by knife_texture_str to obtain per-pixel
        luminance adjustments. Add these adjustments to all three channels of the
        quantized result. The effect is a slight directional luminance gradient
        within each colour block, simulating the way a palette knife dragged
        across a thick paint deposit deposits slightly more pigment at one edge
        than the other.
        NOVEL: (b) INTRA-TILE DIRECTIONAL LUMINANCE GRADIENT -- first pass to
        add a parametric directional luminance ramp within each quantized tile
        using a shared gradient template that is tiled across the canvas; the
        gradient direction is controlled by knife_angle_deg and is the same for
        all tiles, reproducing the consistent stroke direction of a single palette-
        knife passage across a composition; prior directional passes (kollwitz
        grain, diffuse_boundary) apply convolutional kernels to the full canvas,
        not a per-tile spatial ramp.

        Stage 3 TILE BOUNDARY GAP DARKENING: For each pixel, compute its
        distance to the nearest horizontal or vertical tile boundary: dist_row =
        min(row % tile_h, tile_h - 1 - row % tile_h) and similarly for
        dist_col; take min_dist = min(dist_row, dist_col). Apply a darkening
        weight = clip((boundary_width - min_dist) / boundary_width, 0, 1) *
        boundary_strength. Subtract this weight from all three channels. The
        result is a thin darkened zone along every tile boundary, simulating the
        slight trough or gap where a palette knife lifts between adjacent paint
        deposits.
        NOVEL: (c) TILE BOUNDARY GAP DARKENING -- first pass to compute per-
        pixel proximity to quantized tile boundaries and apply a proportional
        darkening in that proximity zone; the trough geometry is derived directly
        from the tile grid parameters (tile_h, tile_w) and applies identically
        at every tile edge throughout the canvas; no prior pass darkens pixels
        specifically based on their distance to a spatial quantization boundary.

        tile_h           : Height of each rectangular tile in pixels.
        tile_w           : Width of each rectangular tile in pixels.
        knife_angle_deg  : Angle (degrees) of the intra-tile knife gradient.
        knife_texture_str: Max luminance adjustment amplitude within each tile.
        boundary_width   : Width in pixels of the boundary darkening zone.
        boundary_strength: Maximum darkening applied at the tile boundary edge.
        opacity          : Final composite opacity.
        """
        import numpy as _np

        print("    de Stael Palette Knife Mosaic pass (session 248: 159th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        th = int(max(1, tile_h))
        tw = int(max(1, tile_w))

        # Stage 1: Rectangular tile mean quantization (vectorised via padding)
        pad_h = (th - (h % th)) % th
        pad_w = (tw - (w % tw)) % tw
        def _tile_mean(ch):
            padded = _np.pad(ch, ((0, pad_h), (0, pad_w)), mode='edge')
            Hp, Wp = padded.shape
            ntr = Hp // th
            ntc = Wp // tw
            blocked = padded.reshape(ntr, th, ntc, tw)
            means   = blocked.mean(axis=(1, 3))        # (ntr, ntc)
            expanded = _np.repeat(_np.repeat(means, th, axis=0), tw, axis=1)
            return expanded[:h, :w].astype(_np.float32)

        r1 = _tile_mean(r0)
        g1 = _tile_mean(g0)
        b1 = _tile_mean(b0)

        # Stage 2: Intra-tile directional knife gradient (tiled template)
        ang_rad = _np.deg2rad(float(knife_angle_deg))
        cos_a   = float(_np.cos(ang_rad))
        sin_a   = float(_np.sin(ang_rad))
        tile_ys = _np.linspace(-1.0, 1.0, th).astype(_np.float32)[:, None]
        tile_xs = _np.linspace(-1.0, 1.0, tw).astype(_np.float32)[None, :]
        tile_grad = (tile_xs * cos_a + tile_ys * sin_a) * float(knife_texture_str)

        pad_h2  = (th - (h % th)) % th
        pad_w2  = (tw - (w % tw)) % tw
        ntr2    = (h + pad_h2) // th
        ntc2    = (w + pad_w2) // tw
        tiled   = _np.tile(tile_grad, (ntr2, ntc2))[:h, :w].astype(_np.float32)
        r1 = _np.clip(r1 + tiled, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g1 + tiled, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b1 + tiled, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Tile boundary gap darkening
        row_idx    = _np.arange(h).astype(_np.int32)
        col_idx    = _np.arange(w).astype(_np.int32)
        row_offset = row_idx % th
        col_offset = col_idx % tw
        dist_row   = _np.minimum(row_offset, th - 1 - row_offset).astype(_np.float32)[:, None]
        dist_col   = _np.minimum(col_offset, tw - 1 - col_offset).astype(_np.float32)[None, :]
        min_dist   = _np.minimum(dist_row, dist_col)
        bw         = float(max(1, boundary_width))
        bs         = float(boundary_strength)
        bw_weight  = _np.clip((bw - min_dist) / bw, 0.0, 1.0) * bs
        r2 = _np.clip(r1 - bw_weight, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 - bw_weight, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 - bw_weight, 0.0, 1.0).astype(_np.float32)

        op    = float(opacity)
        new_r = r0 * (1.0 - op) + r2 * op
        new_g = g0 * (1.0 - op) + g2 * op
        new_b = b0 * (1.0 - op) + b2 * op
        buf = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()
        n_tiles = ((h + th - 1) // th) * ((w + tw - 1) // tw)
        print(f"    de Stael Palette Knife Mosaic complete (tile={th}x{tw} "
              f"n_tiles={n_tiles} knife_angle={float(knife_angle_deg):.1f}deg "
              f"boundary_w={int(boundary_width)} boundary_str={bs:.3f})")
'''

HALATION_PASS = '''
    def paint_halation_pass(
        self,
        halation_thresh:  float = 0.76,
        halation_sigma:   float = 16.0,
        tint_r:           float = 1.00,
        tint_g:           float = 0.68,
        tint_b:           float = 0.30,
        bloom_strength:   float = 0.28,
        opacity:          float = 0.55,
    ) -> None:
        r"""Paint Halation -- session 248 artistic improvement.

        BRIGHTNESS-GATED WARM GAUSSIAN BLOOM: Extract pixels whose luminance
        exceeds halation_thresh. Expand those bright areas with a wide Gaussian
        bloom at halation_sigma. Tint the bloom with (tint_r, tint_g, tint_b)
        -- default warm orange, simulating the warm halation glow of dusk light
        or incandescent sources bleeding into surrounding areas. Add the tinted
        bloom back into the canvas at bloom_strength, then composite with the
        original at opacity.

        THREE-STAGE HALATION:

        Stage 1 LUMINANCE-THRESHOLDED BRIGHT-PIXEL MASK: Compute per-pixel
        luminance lum = 0.299r + 0.587g + 0.114b. Compute a soft bright mask:
        bright = clip((lum - halation_thresh) / max(1 - halation_thresh, 0.01),
        0, 1). This gives a continuous mask whose value rises from 0 at the
        threshold to 1 at full brightness.
        NOVEL: (a) LUMINANCE-THRESHOLD-GATED HALATION BLOOM -- first improvement
        pass to extract a brightness-based continuous pixel mask for bloom
        generation; prior improvement passes that gate on luminance use it for
        other purposes: aerial_perspective_pass gates DoG frequency selection,
        kollwitz_charcoal_etching_pass gates shadow grain -- none compute a
        continuous bright-zone mask specifically for bloom generation.

        Stage 2 GAUSSIAN BLOOM WITH RGB TINT: Apply a 2D Gaussian filter at
        sigma=halation_sigma to the bright mask to produce a soft radial bloom
        field. Multiply by (tint_r, tint_g, tint_b) * bloom_strength to obtain
        per-channel bloom contributions. Add these contributions directly to the
        original channel values and clip.
        NOVEL: (b) TINTED BRIGHTNESS-GATED GAUSSIAN BLOOM -- first improvement
        pass to (i) compute a brightness-gated luminance mask, (ii) expand it
        via wide Gaussian blurring to create a soft radial glow field, (iii)
        apply a user-specified RGB tint to the glow, and (iv) additively blend
        the result; prior improvement passes: color_bloom_pass (saturation-based
        expansion, not brightness-gated), optical_vibration_pass (warm-cool
        boundary oscillation, not bloom), golden_ground_pass (uniform warm
        overlay, not spatially varying), imprimatura_warmth_pass (uniform warm
        blend), luminance_stretch_pass (tonal normalisation) -- none create a
        brightness-gated, tinted, spatially-soft Gaussian glow.

        Stage 3 OPACITY COMPOSITE: Blend the bloomed result with the original
        canvas at opacity.

        halation_thresh  : Luminance threshold above which pixels contribute to bloom.
        halation_sigma   : Gaussian sigma for bloom expansion (larger = wider glow).
        tint_r/g/b       : RGB colour tint applied to the bloom (default warm orange).
        bloom_strength   : Amplitude of the additive bloom contribution.
        opacity          : Final composite opacity (0=no change, 1=full effect).
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Paint Halation pass (session 248 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # Stage 1: Luminance-thresholded bright-pixel mask
        lum   = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        ht    = float(halation_thresh)
        denom = max(1.0 - ht, 0.01)
        bright = _np.clip((lum - ht) / denom, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Gaussian bloom with RGB tint
        sig = float(halation_sigma)
        bs  = float(bloom_strength)
        bloom_field = _gf(bright, sigma=sig).astype(_np.float32)
        bloom_r = bloom_field * float(tint_r) * bs
        bloom_g = bloom_field * float(tint_g) * bs
        bloom_b = bloom_field * float(tint_b) * bs
        r1 = _np.clip(r0 + bloom_r, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 + bloom_g, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 + bloom_b, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Opacity composite
        op    = float(opacity)
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
        bloom_mean = float(bloom_field.mean())
        bright_frac = float((bright > 0.01).mean())
        print(f"    Paint Halation complete (thresh={ht:.2f} sigma={sig:.1f} "
              f"bloom_strength={bs:.2f} bright_frac={bright_frac:.3f} "
              f"bloom_mean={bloom_mean:.4f})")
'''


with open('stroke_engine.py', 'a', encoding='utf-8') as f:
    f.write(DE_STAEL_PASS)
    f.write(HALATION_PASS)

print('Done. Verifying imports...')

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'stroke_engine' in mod:
        del _sys.modules[mod]
from stroke_engine import Painter
assert hasattr(Painter, 'de_stael_palette_knife_mosaic_pass'), 'de_stael_palette_knife_mosaic_pass missing'
assert hasattr(Painter, 'paint_halation_pass'), 'paint_halation_pass missing'
print('Both new passes found on Painter class.')
new_line_count = open('stroke_engine.py', 'r', encoding='utf-8').read().count('\n')
print(f'stroke_engine.py now has approximately {new_line_count} lines')
