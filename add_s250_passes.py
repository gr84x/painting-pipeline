"""Append mitchell_gestural_arc_pass and paint_chromatic_underdark_pass to stroke_engine.py (session 250)."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

MITCHELL_PASS = '''
    def mitchell_gestural_arc_pass(
        self,
        n_arcs:           int   = 28,
        arc_radius_lo:    float = 0.18,
        arc_radius_hi:    float = 0.55,
        arc_span_lo:      float = 0.55,
        arc_span_hi:      float = 2.20,
        mark_width:       float = 4.5,
        brightness_shift: float = 0.20,
        dark_frac:        float = 0.35,
        wet_sat_thresh:   float = 0.28,
        wet_sigma_lo:     float = 1.4,
        wet_sigma_hi:     float = 3.0,
        wet_strength:     float = 0.32,
        density_boost:    float = 0.26,
        density_reduce:   float = 0.14,
        opacity:          float = 0.80,
        seed:             int   = 250,
    ) -> None:
        r"""Joan Mitchell Gestural Arc -- session 250: ONE HUNDRED AND SIXTY-FIRST distinct mode.

        THREE-STAGE GESTURAL LYRIC ARC (Joan Mitchell):

        Stage 1 LARGE CIRCULAR ARC GESTURAL MARKS: Generate n_arcs arc marks,
        each defined by a random centre point (cx * W, cy * H), a radius r in
        [arc_radius_lo, arc_radius_hi] * min(H, W), a random start_angle in
        [0, 2*pi), and a random arc_span in [arc_span_lo, arc_span_hi] radians.
        For each pixel (row, col), compute the vector from the arc centre to the
        pixel; compute the pixel's angular distance to the nearest arc point
        (clamped to the arc span); compute Euclidean distance from the pixel to
        that nearest arc point. Pixels within mark_width/2 of the nearest arc
        point receive brightness_shift (dark_frac fraction of arcs darken,
        remainder brighten). Accumulate all arc contributions into a delta field.
        NOVEL: (a) CIRCULAR ARC SEGMENT GESTURAL RASTER MARKS -- first pass to
        rasterize gestural overlay marks as curved circular arc segments defined
        by centre, radius, start angle, and arc span; Basquiat (s249) uses
        straight line-segment rasters; Franz Kline (s119) uses calligraphic
        mega-strokes derived from luminance gradient orientation along straight
        paths; no prior pass parameterizes marks as curved circular arc segments.

        Stage 2 WET-SPREAD DIRECTIONAL COLOUR BLEED: Identify high-saturation
        pixels (pixels with per-pixel HSV saturation > wet_sat_thresh) as
        saturated paint marks. For each channel, apply an anisotropic Gaussian
        blur: along the horizontal axis with sigma=wet_sigma_hi and along the
        vertical axis with sigma=wet_sigma_lo (approximating lateral spread of
        arm-direction paint). Blend the spread result with the original via the
        saturation mask (more spread where saturation is highest) at wet_strength.
        NOVEL: (b) SATURATION-GATED ANISOTROPIC COLOUR BLEED -- first pass to
        identify high-saturation pixels as saturated paint marks and apply
        anisotropic Gaussian blending weighted by per-pixel saturation; prior
        wet-blend passes apply uniform or luminance-driven blending; no prior
        pass gates the anisotropic bleed by the per-pixel saturation value.

        Stage 3 MARK DENSITY SATURATION RHYTHM: Using the arc density field D
        accumulated in Stage 1 (counting how many arcs pass within mark_width
        of each pixel), normalise D to [0, 1]. In high-density zones (D > 0.5),
        boost saturation by density_boost * (D - 0.5) * 2. In low-density zones
        (D < 0.5), reduce saturation by density_reduce * (0.5 - D) * 2. This
        creates the dense-sparse rhythmic alternation of all-over composition.
        NOVEL: (c) MARK-DENSITY-GATED SATURATION RHYTHM -- first pass to
        modulate saturation by a spatially derived arc mark density field,
        creating rhythmic chromatic alternation that matches gestural mark
        density; chroma_focus (s249) uses a geometric radial field; Basquiat
        midtone sat (s249) uses a luminance threshold; no prior pass gates
        saturation by a computed mark-density spatial map.

        n_arcs           : Number of circular arc gestural marks.
        arc_radius_lo/hi : Arc radius range as fraction of min(H, W).
        arc_span_lo/hi   : Arc angular span range in radians.
        mark_width       : Width of each arc mark in pixels.
        brightness_shift : Luminance change applied within mark width.
        dark_frac        : Fraction of arcs that darken (polarity = -1).
        wet_sat_thresh   : Saturation threshold above which bleed applies.
        wet_sigma_lo/hi  : Anisotropic Gaussian sigmas (lo = narrow, hi = wide).
        wet_strength     : Opacity of wet-spread blend onto original.
        density_boost    : Saturation boost in high-density arc zones.
        density_reduce   : Saturation reduction in low-density arc zones.
        opacity          : Final composite opacity.
        seed             : RNG seed for arc position reproducibility.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gauss

        print("    Mitchell Gestural Arc pass (session 250: 161st mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        rng = _np.random.default_rng(int(seed))
        rows_f = _np.arange(h, dtype=_np.float32)[:, None]
        cols_f = _np.arange(w, dtype=_np.float32)[None, :]

        # ── Stage 1: Large circular arc gestural marks ─────────────────────
        delta_arc   = _np.zeros((h, w), dtype=_np.float32)
        density_map = _np.zeros((h, w), dtype=_np.float32)
        mw_half = float(mark_width) / 2.0
        min_dim = float(min(h, w))
        bs = float(brightness_shift)
        df = float(dark_frac)

        for _ in range(int(n_arcs)):
            cx     = float(rng.uniform(0.1, 0.9)) * w
            cy     = float(rng.uniform(0.1, 0.9)) * h
            r_norm = float(rng.uniform(float(arc_radius_lo), float(arc_radius_hi)))
            radius = r_norm * min_dim
            start  = float(rng.uniform(0.0, 2.0 * _np.pi))
            span   = float(rng.uniform(float(arc_span_lo), float(arc_span_hi)))
            pol    = -1.0 if rng.random() < df else 1.0

            # Per-pixel angle relative to arc centre
            dy_pix = rows_f - cy
            dx_pix = cols_f - cx
            ang    = _np.arctan2(dy_pix, dx_pix).astype(_np.float32)

            # Clamp angle to arc span (modular arithmetic)
            dang = ((ang - start + _np.pi) % (2.0 * _np.pi) - _np.pi).astype(_np.float32)
            clamped = _np.clip(dang, 0.0, float(span))
            # Nearest arc point: point at (cx + radius*cos(start+clamped), ...)
            nearest_ang = start + clamped
            nx = cx + radius * _np.cos(nearest_ang).astype(_np.float32)
            ny = cy + radius * _np.sin(nearest_ang).astype(_np.float32)

            dist = _np.sqrt((cols_f - nx) ** 2 + (rows_f - ny) ** 2).astype(_np.float32)
            inside = (dist <= mw_half).astype(_np.float32)
            delta_arc   += inside * (pol * bs)
            density_map += inside

        delta_arc   = _np.clip(delta_arc, -0.6, 0.6)
        r1 = _np.clip(r0 + delta_arc, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 + delta_arc, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 + delta_arc, 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Wet-spread directional colour bleed ────────────────────
        maxc  = _np.maximum(_np.maximum(r1, g1), b1)
        minc  = _np.minimum(_np.minimum(r1, g1), b1)
        sat   = _np.where(maxc > 1e-8, (maxc - minc) / (maxc + 1e-8), 0.0).astype(_np.float32)
        sat_w = _np.clip((sat - float(wet_sat_thresh)) / max(1.0 - float(wet_sat_thresh), 0.01),
                         0.0, 1.0).astype(_np.float32)

        sl, sh = float(wet_sigma_lo), float(wet_sigma_hi)
        def _aniso_blur(ch):
            bl_h = _gauss(ch, sigma=[sl, sh])   # narrow vertical, wide horizontal
            bl_v = _gauss(ch, sigma=[sh, sl])   # wide vertical, narrow horizontal
            return ((bl_h + bl_v) * 0.5).astype(_np.float32)

        ws = float(wet_strength)
        r2 = _np.clip(r1 * (1.0 - sat_w * ws) + _aniso_blur(r1) * sat_w * ws, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 * (1.0 - sat_w * ws) + _aniso_blur(g1) * sat_w * ws, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 * (1.0 - sat_w * ws) + _aniso_blur(b1) * sat_w * ws, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Mark density saturation rhythm ─────────────────────────
        d_max = float(density_map.max())
        if d_max > 0:
            d_norm = (density_map / d_max).astype(_np.float32)
        else:
            d_norm = density_map.astype(_np.float32)

        maxc2 = _np.maximum(_np.maximum(r2, g2), b2)
        minc2 = _np.minimum(_np.minimum(r2, g2), b2)
        lum2  = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)

        hi_dens = _np.clip(d_norm - 0.5, 0.0, 0.5) * 2.0   # 0->1 for dense zones
        lo_dens = _np.clip(0.5 - d_norm, 0.0, 0.5) * 2.0   # 0->1 for sparse zones

        db = float(density_boost)
        dr = float(density_reduce)

        def _mod_sat(ch, _lum, boost_w, reduce_w):
            boosted  = _lum + (ch - _lum) * (1.0 + db * boost_w)
            reduced  = _lum + (ch - _lum) * (1.0 - dr * reduce_w)
            return _np.clip(boosted * boost_w + reduced * reduce_w + ch * (1.0 - boost_w - reduce_w),
                            0.0, 1.0).astype(_np.float32)

        bw = _np.clip(hi_dens, 0.0, 1.0)
        rw = _np.clip(lo_dens * (1.0 - bw), 0.0, 1.0)
        r3 = _mod_sat(r2, lum2, bw, rw)
        g3 = _mod_sat(g2, lum2, bw, rw)
        b3 = _mod_sat(b2, lum2, bw, rw)

        op    = float(opacity)
        new_r = r0 * (1.0 - op) + r3 * op
        new_g = g0 * (1.0 - op) + g3 * op
        new_b = b0 * (1.0 - op) + b3 * op
        buf   = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()
        arc_cov   = float((density_map > 0).mean())
        dense_cov = float((d_norm > 0.5).mean())
        print(f"    Mitchell Gestural Arc complete (n_arcs={int(n_arcs)} "
              f"arc_coverage={arc_cov:.3f} dense_zones={dense_cov:.3f})")
'''

UNDERDARK_PASS = '''
    def paint_chromatic_underdark_pass(
        self,
        shadow_thresh:  float = 0.32,
        shadow_fade:    float = 0.12,
        dark_hue:       float = 0.72,
        dark_strength:  float = 0.40,
        clarity_sigma:  float = 1.6,
        clarity_amount: float = 0.22,
        opacity:        float = 0.50,
    ) -> None:
        r"""Paint Chromatic Underdark -- session 250 artistic improvement.

        THREE-STAGE SHADOW CHROMATIC ENRICHMENT:

        Stage 1 SHADOW MASK CONSTRUCTION: Compute per-pixel luminance
        lum = 0.299r + 0.587g + 0.114b. Build a smooth shadow mask with a
        soft ramp: shadow_mask = clip((shadow_thresh - lum) / shadow_fade, 0, 1).
        Pixels with lum << shadow_thresh receive mask=1.0 (full shadow); pixels
        with lum slightly below shadow_thresh receive a partial mask; pixels
        with lum >= shadow_thresh receive mask=0.0 (no effect). This produces
        a spatially smooth shadow zone without hard boundaries.
        NOVEL: (a) CONFIGURABLE HUE ANCHOR SHADOW ENRICHMENT -- first improvement
        pass to rotate shadow-zone pixel hues in HSV space toward a configurable
        deep chromatic anchor hue (dark_hue), weighted by per-pixel saturation
        and shadow_mask; prior improvement passes (chroma_focus: radial boost/
        reduce; halation: bright bloom; golden_ground: warm tone overlay;
        aerial_perspective: luminance gradient; luminance_stretch: range expand;
        optical_vibration: hue-shift by gradient magnitude) do not apply a
        configurable deep hue target specifically in shadow zones via HSV rotation.

        Stage 2 HUE-BIASED SHADOW ENRICHMENT: Convert RGB to HSV per pixel.
        In shadow zones, rotate the hue toward dark_hue by angular interpolation:
        hue_new = hue + shadow_mask * sat * dark_strength * delta_hue, where
        delta_hue is the shortest angular path from hue to dark_hue (mod 1.0).
        Convert back to RGB. The result: coloured shadows pick up a deep violet-
        indigo (or configurable) cast, adding chromatic richness to what would
        otherwise be flat dark areas, a technique of the great colorists from
        Velazquez to Bonnard.
        NOVEL: (b) SATURATION-WEIGHTED HSV HUE ROTATION TOWARD DEEP ANCHOR IN
        SHADOW ZONE -- the hue rotation is scaled by the pixel's existing
        saturation (s), so achromatic pixels are unaffected while chromatic
        shadow pixels gain a hue bias; no prior improvement pass applies a
        saturation-modulated, anchor-targeted hue rotation within a luminance-
        defined shadow zone.

        Stage 3 SHADOW CLARITY LIFT: Apply an unsharp mask within the shadow
        zone: blurred = Gaussian(r2, sigma=clarity_sigma); clarity_delta =
        (r2 - blurred) * clarity_amount * shadow_mask. Add clarity_delta to
        each channel. This lifts local contrast in the shadow zone, preventing
        dark areas from becoming undifferentiated flat black and preserving the
        textural information that lies in dark passages.
        NOVEL: (c) SHADOW-ZONE UNSHARP MASK CLARITY -- first improvement pass
        to apply unsharp mask (local contrast lift) specifically within the
        shadow-zone mask; prior improvement passes do not target local contrast
        enhancement to shadow regions; edge passes (edge_definition, edge_lost_
        and_found) apply sharpening globally or by focal zone, not shadow-masked.

        shadow_thresh  : Luminance below which the shadow mask begins.
        shadow_fade    : Width of the smooth transition band above shadow_thresh.
        dark_hue       : Target deep hue for shadow enrichment (0=red, 0.72=blue-violet).
        dark_strength  : Maximum hue rotation strength within shadow zone.
        clarity_sigma  : Gaussian sigma for the unsharp mask blur.
        clarity_amount : Unsharp mask strength within shadow zone.
        opacity        : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gauss

        print("    Paint Chromatic Underdark pass (session 250 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Shadow mask ────────────────────────────────────────────
        lum  = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        fade = max(float(shadow_fade), 1e-6)
        sh_mask = _np.clip((float(shadow_thresh) - lum) / fade, 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Hue-biased shadow enrichment ──────────────────────────
        maxc  = _np.maximum(_np.maximum(r0, g0), b0)
        minc  = _np.minimum(_np.minimum(r0, g0), b0)
        delta = maxc - minc
        d_safe = _np.where(delta > 1e-8, delta, 1.0).astype(_np.float32)

        is_r  = (maxc == r0) & (delta > 1e-8)
        is_g  = (~is_r) & (maxc == g0) & (delta > 1e-8)
        is_b  = (~is_r) & (~is_g) & (maxc == b0) & (delta > 1e-8)
        hue_raw = _np.where(is_r, (g0 - b0) / d_safe, 0.0)
        hue_raw = _np.where(is_g, 2.0 + (b0 - r0) / d_safe, hue_raw)
        hue_raw = _np.where(is_b, 4.0 + (r0 - g0) / d_safe, hue_raw)
        hue     = (hue_raw / 6.0 % 1.0).astype(_np.float32)
        sat     = _np.where(maxc > 1e-8, delta / (maxc + 1e-8), 0.0).astype(_np.float32)
        val     = maxc.astype(_np.float32)

        dh   = float(dark_hue)
        diff = ((dh - hue + 0.5) % 1.0 - 0.5).astype(_np.float32)  # shortest path
        ds   = float(dark_strength)
        hue1 = (hue + sh_mask * sat * ds * diff) % 1.0

        # HSV → RGB
        h6 = hue1 * 6.0
        i  = _np.floor(h6).astype(_np.int32) % 6
        f  = (h6 - _np.floor(h6)).astype(_np.float32)
        p  = (val * (1.0 - sat)).astype(_np.float32)
        q  = (val * (1.0 - sat * f)).astype(_np.float32)
        t_ = (val * (1.0 - sat * (1.0 - f))).astype(_np.float32)
        r1 = _np.where(i == 0, val, _np.where(i == 1, q, _np.where(i == 2, p,
             _np.where(i == 3, p, _np.where(i == 4, t_, val))))).astype(_np.float32)
        g1 = _np.where(i == 0, t_, _np.where(i == 1, val, _np.where(i == 2, val,
             _np.where(i == 3, q, _np.where(i == 4, p, p))))).astype(_np.float32)
        b1 = _np.where(i == 0, p, _np.where(i == 1, p, _np.where(i == 2, t_,
             _np.where(i == 3, val, _np.where(i == 4, val, q))))).astype(_np.float32)
        r1 = _np.clip(r1, 0.0, 1.0)
        g1 = _np.clip(g1, 0.0, 1.0)
        b1 = _np.clip(b1, 0.0, 1.0)

        # ── Stage 3: Shadow clarity lift ───────────────────────────────────
        ca = float(clarity_amount)
        cs = max(float(clarity_sigma), 0.5)

        def _clarity(ch):
            blurred = _gauss(ch, sigma=cs)
            return _np.clip(ch + (ch - blurred) * ca * sh_mask, 0.0, 1.0).astype(_np.float32)

        r2 = _clarity(r1)
        g2 = _clarity(g1)
        b2 = _clarity(b1)

        op    = float(opacity)
        new_r = r0 * (1.0 - op) + r2 * op
        new_g = g0 * (1.0 - op) + g2 * op
        new_b = b0 * (1.0 - op) + b2 * op
        buf   = orig.copy()
        buf[:, :, 2] = _np.clip(new_r * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 1] = _np.clip(new_g * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 0] = _np.clip(new_b * 255, 0, 255).astype(_np.uint8)
        buf[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()
        shadow_area = float((sh_mask > 0.1).mean())
        sat_mean    = float(sat[sh_mask > 0.3].mean()) if (sh_mask > 0.3).any() else 0.0
        print(f"    Chromatic Underdark complete (shadow_area={shadow_area:.3f} "
              f"sat_mean_in_shadow={sat_mean:.3f} dark_hue={float(dark_hue):.2f})")
'''

with open("stroke_engine.py", "a", encoding="utf-8") as f:
    f.write(MITCHELL_PASS)
    f.write(UNDERDARK_PASS)

print("Done. Verifying imports...")

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if "stroke_engine" in mod:
        del _sys.modules[mod]
from stroke_engine import Painter
assert hasattr(Painter, "mitchell_gestural_arc_pass"), "mitchell_gestural_arc_pass missing"
assert hasattr(Painter, "paint_chromatic_underdark_pass"), "paint_chromatic_underdark_pass missing"
print("Both new passes found on Painter class.")
new_line_count = open("stroke_engine.py", "r", encoding="utf-8").read().count("\n")
print(f"stroke_engine.py now has approximately {new_line_count} lines")
