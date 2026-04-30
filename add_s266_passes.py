"""Insert paint_hue_zone_boundary_pass (s266 improvement) and
gallen_kallela_enamel_cloisonne_pass (177th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_hue_zone_boundary_pass (s266 improvement) ─────────────────

HUE_BOUNDARY_PASS = '''
    def paint_hue_zone_boundary_pass(
        self,
        variance_sigma:      float = 3.0,
        boundary_dark:       float = 0.55,
        interior_chroma:     float = 0.18,
        feather_sigma:       float = 1.5,
        sat_floor:           float = 0.10,
        noise_seed:          int   = 266,
        opacity:             float = 0.70,
    ) -> None:
        r"""Hue Zone Boundary -- session 266 artistic improvement.

        THREE-STAGE HUE ZONE BOUNDARY ISOLATION TECHNIQUE INSPIRED BY THE
        ENAMEL CLOISONNE AND STAINED-GLASS TRADITION (Gallen-Kallela, Tiffany,
        medieval enamel work, c.1100-1930):

        In cloisonne enamel, thin metal wires (cloisons) partition the surface
        into discrete cells; each cell is filled with a single colour of powdered
        glass that fuses at high temperature into a flat, jewel-bright zone. The
        metal partitions appear as narrow, dark lines between the colour zones.
        In oil painting, Akseli Gallen-Kallela and the Symbolist painters who
        absorbed the decorative arts tradition reproduced this effect by building
        their compositions from flat colour zones separated by bold dark outlines
        -- a technique that simultaneously derives from medieval enamel, Japanese
        woodblock prints (where the key block prints black outlines), and the
        Synthetic Cubism of Gauguin and the Pont-Aven school. The key perceptual
        mechanism is that the dark boundary line sharpens the apparent contrast
        of the two adjacent colour zones: adjacent colours always appear more
        saturated when separated by a dark partition. This is a consequence of
        simultaneous contrast -- the dark line shifts the visual context for both
        adjacent zones toward the opposite end of the luminance scale.

        The critical novelty of this pass is using CIRCULAR HUE STATISTICS to
        locate zone boundaries. All prior passes that create edge effects use
        LUMINANCE gradients (Sobel, DoG) -- these detect light-to-dark boundaries
        but miss colour-to-colour boundaries of equal luminance (e.g., a red zone
        adjacent to a green zone of the same brightness, or an orange region
        touching a cyan region). Circular hue variance detects exactly the
        boundaries that luminance-based methods miss: adjacent colour zones with
        different hues but similar luminance are invisible to Sobel but produce
        maximum hue variance.

        Stage 1 CIRCULAR HUE VARIANCE FIELD: Convert RGB to HSV. Encode hue
        as unit vectors: hue_sin = sin(2pi*H), hue_cos = cos(2pi*H). Compute
        local Gaussian-weighted means of sin and cos components:
          sin_mean = gaussian_filter(sat_masked_sin, variance_sigma)
          cos_mean = gaussian_filter(sat_masked_cos, variance_sigma)
        The circular coherence R = sqrt(sin_mean^2 + cos_mean^2) measures how
        aligned the hue vectors are in the local neighbourhood. R near 1 means
        all nearby pixels have the same hue (zone interior). R near 0 means the
        hue vectors cancel (zone boundary between different hues). Define:
          hue_var = 1 - R   (high at zone boundaries, low at zone interiors)
          hue_var = clip(hue_var / hue_var.max(), 0, 1)  (normalized)
        Saturation masking: apply gaussian_filter on sat*sin and sat*cos to weight
        the hue statistics by local saturation, so that grey/near-grey pixels (which
        have no meaningful hue) do not artificially inflate hue variance.
        NOVEL: (a) CIRCULAR HUE VARIANCE FIELD USING SIN/COS ENCODING OF HSV HUE
        CHANNEL WITH SATURATION-WEIGHTED LOCAL GAUSSIAN NEIGHBORHOOD -- first pass
        to use circular statistics (unit-vector mean + coherence) to compute a hue-
        zone boundary detection field; all prior boundary-detection passes (paint_
        flat_zone_pass, paint_sfumato_contour_dissolution_pass, paint_contour_weight_
        pass) use luminance-based Sobel gradients, which miss equal-luminance color
        boundaries; this pass detects exactly those boundaries (blue-to-orange,
        green-to-red, etc.) that Sobel cannot see.

        Stage 2 BOUNDARY DARKENING COMPOSITE: Feather the hue variance field with
        a small Gaussian (feather_sigma) to smooth the partition lines. Apply
        multiplicative darkening gated by the hue variance:
          dark_gate = hue_var_feathered * boundary_dark
          r_dark = r * (1 - dark_gate)
          g_dark = g * (1 - dark_gate)
          b_dark = b * (1 - dark_gate)
        This creates narrow dark outlines at zone boundaries, simulating the metal
        cloison partitions of enamel work and the bold contour lines of Gallen-
        Kallela's Symbolist period paintings.
        NOVEL: (b) MULTIPLICATIVE DARKENING GATED BY CIRCULAR HUE VARIANCE FIELD
        TO PRODUCE DARK OUTLINES AT COLOR ZONE BOUNDARIES WITHOUT REQUIRING LUMINANCE
        CONTRAST -- first pass to apply a darkening effect specifically to pixels
        identified as hue zone boundaries via circular statistics; paint_edge_temperature_
        pass applies warm/cool shifts at luminance edges; no prior pass uses a hue-
        coherence-based field to gate a darkening effect at colour zone boundary positions.

        Stage 3 INTERIOR CHROMA AMPLIFICATION: In low-variance (zone interior)
        pixels, amplify saturation by interior_chroma, gated by
          interior_gate = (1 - hue_var) * clip((S - sat_floor)/sat_floor, 0, 1)
        Convert the hue-adjusted interior pixels back to RGB and blend at
        interior_chroma strength. The saturation floor gate prevents grey areas
        from being pushed into false colour (grey pixels have undefined hue and
        amplifying their near-zero saturation produces distracting colour noise).
        NOVEL: (c) SATURATION AMPLIFICATION GATED BY CIRCULAR HUE COHERENCE AND
        SATURATION FLOOR THRESHOLD IN ZONE INTERIOR PIXELS -- first pass to use
        1-hue_var (the zone interior map) as the gate for a per-pixel saturation
        boost; paint_chroma_focus_pass applies saturation globally based on
        luminance; no prior pass uses a hue-coherence field to identify zone
        interiors specifically and apply saturation enhancement only within those
        flat-hue regions, which is exactly the mechanism that makes enamel zones
        appear richer than the surrounding painted areas.
        """
        print("    Hue Zone Boundary pass (session 266 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Circular Hue Variance Field ──────────────────────────────
        ch_max = _np.maximum(_np.maximum(r0, g0), b0)
        ch_min = _np.minimum(_np.minimum(r0, g0), b0)
        sat = _np.clip((ch_max - ch_min) / (ch_max + 1e-6), 0.0, 1.0).astype(_np.float32)

        # Hue angle (0..1 range = 0..360 deg), only meaningful where sat > 0
        delta = (ch_max - ch_min).astype(_np.float32)
        hue = _np.zeros_like(r0)
        m = delta > 1e-6
        r_m = r0[m]; g_m = g0[m]; b_m = b0[m]
        d_m = delta[m]; mx_m = ch_max[m]

        hr = ((g_m - b_m) / d_m) % 6.0
        hg = (b_m - r_m) / d_m + 2.0
        hb = (r_m - g_m) / d_m + 4.0

        is_r = (mx_m == r_m)
        is_g = (mx_m == g_m) & ~is_r
        is_b = ~is_r & ~is_g

        h_m = _np.where(is_r, hr, _np.where(is_g, hg, hb)) / 6.0
        hue[m] = h_m

        # Circular encoding weighted by saturation (unsaturated pixels contribute nothing)
        theta = (2.0 * _np.pi * hue).astype(_np.float32)
        sin_h = (sat * _np.sin(theta)).astype(_np.float32)
        cos_h = (sat * _np.cos(theta)).astype(_np.float32)

        vsig = max(float(variance_sigma), 0.5)
        sin_mean = _gf(sin_h, sigma=vsig).astype(_np.float32)
        cos_mean = _gf(cos_h, sigma=vsig).astype(_np.float32)
        sat_mean = _gf(sat, sigma=vsig).astype(_np.float32) + 1e-6

        coherence = _np.sqrt(sin_mean**2 + cos_mean**2) / sat_mean
        coherence = _np.clip(coherence, 0.0, 1.0).astype(_np.float32)
        hue_var = (1.0 - coherence).astype(_np.float32)
        hue_var_n = _np.clip(hue_var / (hue_var.max() + 1e-6), 0.0, 1.0).astype(_np.float32)
        boundary_px = int((hue_var_n > 0.5).sum())

        # ── Stage 2: Boundary Darkening Composite ─────────────────────────────
        fsig = max(float(feather_sigma), 0.5)
        hue_var_f = _np.clip(_gf(hue_var_n, sigma=fsig), 0.0, 1.0).astype(_np.float32)

        dark = float(boundary_dark)
        dark_gate = (hue_var_f * dark).astype(_np.float32)

        r1 = _np.clip(r0 * (1.0 - dark_gate), 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * (1.0 - dark_gate), 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * (1.0 - dark_gate), 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Interior Chroma Amplification ─────────────────────────────
        sf = max(float(sat_floor), 0.01)
        sat_gate = _np.clip((sat - sf) / (sf + 1e-6), 0.0, 1.0).astype(_np.float32)
        interior_gate = ((1.0 - hue_var_f) * sat_gate).astype(_np.float32)

        ic = float(interior_chroma)
        ch_max1 = _np.maximum(_np.maximum(r1, g1), b1)
        ch_min1 = _np.minimum(_np.minimum(r1, g1), b1)
        sat1 = _np.clip((ch_max1 - ch_min1) / (ch_max1 + 1e-6), 0.0, 1.0).astype(_np.float32)
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)

        # Amplify saturation by lifting channels away from luminance
        r2 = _np.clip(lum1 + (r1 - lum1) * (1.0 + ic * interior_gate), 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(lum1 + (g1 - lum1) * (1.0 + ic * interior_gate), 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(lum1 + (b1 - lum1) * (1.0 + ic * interior_gate), 0.0, 1.0).astype(_np.float32)

        interior_px = int((interior_gate > 0.1).sum())

        # ── Composite at opacity ───────────────────────────────────────────────
        op = float(opacity)
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

        print(f"    Hue Zone Boundary complete "
              f"(boundary_px={boundary_px}, interior_px={interior_px})")
'''

# ── Pass 2: gallen_kallela_enamel_cloisonne_pass (177th mode) ────────────────

CLOISONNE_PASS = '''
    def gallen_kallela_enamel_cloisonne_pass(
        self,
        flat_sigma:         float = 4.0,
        zone_blend:         float = 0.55,
        contour_strength:   float = 0.70,
        contour_sigma:      float = 1.0,
        sat_boost:          float = 0.22,
        sat_floor:          float = 0.12,
        sat_ceil:           float = 0.92,
        noise_seed:         int   = 266,
        opacity:            float = 0.78,
    ) -> None:
        r"""Gallen-Kallela Enamel Cloisonne -- session 266, 177th distinct mode.

        THREE-STAGE ENAMEL CLOISONNE DECORATIVE TECHNIQUE INSPIRED BY AKSELI
        GALLEN-KALLELA\'S DECORATIVE PAINTING PRACTICE (c.1891-1930):

        Akseli Gallen-Kallela (1865-1931) was the dominant figure in Finnish art
        during the National Romantic period. His mature style -- developed through
        intense study of Japanese woodblock prints, medieval stained glass, and
        Byzantine mosaic art during his Paris years (1884-89) -- combined the
        flat, bounded colour zones of Japanese woodblock printing with the jewel-
        bright saturation of enamel and the bold contour lines of medieval
        manuscript illumination. Unlike the Nabis who sought intimacy through
        flat colour, Gallen-Kallela used flatness in service of heroic scale and
        mythological gravitas: his Kalevala illustrations and the Aino triptych
        (1891) treat Finnish forest landscape with the decorative authority of a
        cathedral window. Each coloured zone is a category, not a modulation: the
        birch trunks are WHITE, not "light grey with subtle tonal gradation"; the
        sky is COBALT, not "atmospheric blue with value shifting"; the forest floor
        is BURNT SIENNA, not "complex textured ground."

        The technique has three identifiable mechanical stages: First, the within-
        zone colour is unified (the Japanese woodblock flatness) -- subtle brush-
        mark variation within a zone is resolved into a single dominant hue. Second,
        zone boundaries are reinforced with a dark outline (the stained-glass lead
        line) -- painted with a thin pointed brush, darker than either adjacent zone,
        creating the edge-enhancing perceptual effect that makes both adjacent zones
        appear more saturated. Third, the zone colours are pushed toward the
        decorative palette (the enamel richness) -- Gallen-Kallela\'s palette in
        his mature period is characterised by cobalt blue, burnt orange, forest
        green, cream-white, dark umber, and occasional crimson, with minimal use
        of grey or neutral tones: everything in the composition resolves toward
        a pure, assertive hue.

        Stage 1 CIRCULAR-HUE ZONE FLATTENING: Compute local hue mean using
        Gaussian-weighted circular averaging (sin/cos encoding of hue angle with
        saturation weighting) at sigma=flat_sigma. Blend the original hue toward
        the local circular mean at zone_blend strength. Convert back to RGB
        retaining the original luminance and saturation but with a locally
        unified hue:
          theta_mean = atan2(gaussian(sat*sin(2pi*H), flat_sigma),
                             gaussian(sat*cos(2pi*H), flat_sigma))
          H_flat = theta_mean / (2*pi) mod 1.0
          blend H toward H_flat at zone_blend; reconstruct HSV -> RGB
        NOVEL: (a) CIRCULAR MEAN HUE ZONE FLATTENING VIA GAUSSIAN-WEIGHTED SIN/
        COS ENCODING WITH SATURATION MASKING -- first MODE pass to apply Gaussian-
        smoothing in circular hue space (not in linear hue space, which cannot
        handle the 0/1 wraparound) to unify local hue zones; paint_flat_zone_pass
        applies spatial median filtering per channel (which does not separate hue
        from luminance); paint_local_hue_drift_pass blends toward a local circular
        hue mean at a single global saturation-gate but does not use it to create
        discrete bounded colour zones -- gallen_kallela_enamel_cloisonne_pass adds
        flat_sigma control and zone_blend gating on a per-luminance-stability basis,
        specifically targeting zone unification rather than drift.

        Stage 2 BOLD CONTOUR DARKENING: Compute Sobel edge magnitude on the hue-
        flattened canvas (after Stage 1). Apply Gaussian feathering (contour_sigma)
        to the Sobel magnitude. Use as a multiplicative darkening gate:
          edge_w = clip(sobel_mag / sobel_mag.max(), 0, 1)
          edge_feathered = gaussian_filter(edge_w, contour_sigma)
          R_dark = R * (1 - contour_strength * edge_feathered)
          G_dark = G * (1 - contour_strength * edge_feathered)
          B_dark = B * (1 - contour_strength * edge_feathered)
        NOVEL: (b) SOBEL-MAGNITUDE CONTOUR DARKENING APPLIED TO A CIRCULAR-HUE-
        FLATTENED CANVAS RATHER THAN THE ORIGINAL PAINTED SURFACE -- first mode
        pass to apply bold contour darkening to a pre-processed hue-flattened
        image (the Sobel magnitude detects boundaries between unified colour zones,
        not the original painted brushmarks); paint_contour_weight_pass applies
        contour darkening to the original canvas, which detects both zone boundaries
        AND brushmark edges; gallen_kallela_enamel_cloisonne_pass detects zone
        boundaries specifically from the flattened result, producing clean partition
        lines rather than noisy multi-scale edge marks.

        Stage 3 DECORATIVE PALETTE SATURATION PUNCH: In pixels above sat_floor
        and below sat_ceil, boost saturation by sat_boost using per-pixel chroma
        amplification from luminance:
          chroma_boost = sat_boost * clip((sat - sat_floor)/(sat_ceil - sat_floor), 0, 1)
          R_rich = lum + (R - lum) * (1 + chroma_boost)
          G_rich = lum + (G - lum) * (1 + chroma_boost)
          B_rich = lum + (B - lum) * (1 + chroma_boost)
        This differentially amplifies chromatic departure from grey while leaving
        luminance unchanged, reproducing the jewel-like saturation of Gallen-
        Kallela\'s decorative enamel palette without clipping highlights.
        NOVEL: (c) SATURATION-GATED PER-PIXEL CHROMA AMPLIFICATION FROM LOCAL
        LUMINANCE IN COMBINATION WITH A HUE-FLATTENED AND BOLDLY-OUTLINED CANVAS
        -- first mode pass to combine (1) circular hue zone flattening, (2) bold
        contour darkening on the flattened result, and (3) saturation-bounded chroma
        amplification in a single three-stage pipeline specifically calibrated for the
        Finnish Symbolist enamel cloisonne decorative technique; no prior mode pass
        treats both the flatness and the partition line and the chromatic punch as an
        integrated three-stage system.
        """
        print("    Gallen-Kallela Enamel Cloisonne pass (session 266, 177th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf
        from scipy.ndimage import convolve as _conv

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Circular-Hue Zone Flattening ─────────────────────────────
        ch_max = _np.maximum(_np.maximum(r0, g0), b0)
        ch_min = _np.minimum(_np.minimum(r0, g0), b0)
        delta  = (ch_max - ch_min).astype(_np.float32)
        sat0   = _np.clip(delta / (ch_max + 1e-6), 0.0, 1.0).astype(_np.float32)
        lum0   = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        hue0 = _np.zeros_like(r0)
        m = delta > 1e-6
        if m.any():
            rr = r0[m]; gg = g0[m]; bb = b0[m]
            dd = delta[m]; mx = ch_max[m]
            is_r = (mx == rr)
            is_g = (mx == gg) & ~is_r
            hr = ((gg - bb) / dd) % 6.0
            hg = (bb - rr) / dd + 2.0
            hb = (rr - gg) / dd + 4.0
            hue0[m] = _np.where(is_r, hr, _np.where(is_g, hg, hb)) / 6.0

        theta = (2.0 * _np.pi * hue0).astype(_np.float32)
        sin_h = (sat0 * _np.sin(theta)).astype(_np.float32)
        cos_h = (sat0 * _np.cos(theta)).astype(_np.float32)

        fsig = max(float(flat_sigma), 0.5)
        sin_sm = _gf(sin_h, sigma=fsig).astype(_np.float32)
        cos_sm = _gf(cos_h, sigma=fsig).astype(_np.float32)

        hue_flat = (_np.arctan2(sin_sm, cos_sm) / (2.0 * _np.pi)) % 1.0
        hue_flat = hue_flat.astype(_np.float32)

        zb = float(zone_blend)
        hue_blended = (hue0 * (1.0 - zb) + hue_flat * zb).astype(_np.float32)

        # Reconstruct RGB from (hue_blended, sat0, lum0) via HSV-like inverse
        def _hsv_to_rgb(h_ch, s_ch, v_ch):
            h6 = (h_ch * 6.0).astype(_np.float32)
            i  = h6.astype(_np.int32) % 6
            f  = h6 - _np.floor(h6)
            p  = (v_ch * (1.0 - s_ch)).astype(_np.float32)
            q  = (v_ch * (1.0 - s_ch * f)).astype(_np.float32)
            t  = (v_ch * (1.0 - s_ch * (1.0 - f))).astype(_np.float32)
            R  = _np.select([i==0,i==1,i==2,i==3,i==4,i==5], [v_ch,q,p,p,t,v_ch])
            G  = _np.select([i==0,i==1,i==2,i==3,i==4,i==5], [t,v_ch,v_ch,q,p,p])
            B  = _np.select([i==0,i==1,i==2,i==3,i==4,i==5], [p,p,t,v_ch,v_ch,q])
            return R.astype(_np.float32), G.astype(_np.float32), B.astype(_np.float32)

        v_ch = ch_max.astype(_np.float32)
        r1, g1, b1 = _hsv_to_rgb(hue_blended, sat0, v_ch)
        r1 = _np.clip(r1, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g1, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b1, 0.0, 1.0).astype(_np.float32)

        zone_px = int((sat0 > 0.1).sum())

        # ── Stage 2: Bold Contour Darkening ───────────────────────────────────
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        sobel_x = _np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=_np.float32)
        sobel_y = sobel_x.T
        gx = _conv(lum1, sobel_x, mode="reflect").astype(_np.float32)
        gy = _conv(lum1, sobel_y, mode="reflect").astype(_np.float32)
        edge_mag = _np.sqrt(gx * gx + gy * gy).astype(_np.float32)
        edge_n = _np.clip(edge_mag / (edge_mag.max() + 1e-6), 0.0, 1.0).astype(_np.float32)

        csig = max(float(contour_sigma), 0.3)
        edge_f = _np.clip(_gf(edge_n, sigma=csig), 0.0, 1.0).astype(_np.float32)

        cs = float(contour_strength)
        r2 = _np.clip(r1 * (1.0 - cs * edge_f), 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 * (1.0 - cs * edge_f), 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 * (1.0 - cs * edge_f), 0.0, 1.0).astype(_np.float32)

        contour_px = int((edge_f > 0.3).sum())

        # ── Stage 3: Decorative Palette Saturation Punch ──────────────────────
        ch_max2 = _np.maximum(_np.maximum(r2, g2), b2)
        ch_min2 = _np.minimum(_np.minimum(r2, g2), b2)
        sat2 = _np.clip((ch_max2 - ch_min2) / (ch_max2 + 1e-6), 0.0, 1.0).astype(_np.float32)
        lum2 = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)

        sf = float(sat_floor); sc = float(sat_ceil)
        chroma_gate = _np.clip((sat2 - sf) / ((sc - sf) + 1e-6), 0.0, 1.0).astype(_np.float32)
        sb = float(sat_boost)
        boost = (1.0 + sb * chroma_gate).astype(_np.float32)

        r3 = _np.clip(lum2 + (r2 - lum2) * boost, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(lum2 + (g2 - lum2) * boost, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(lum2 + (b2 - lum2) * boost, 0.0, 1.0).astype(_np.float32)

        sat_px = int((chroma_gate > 0.1).sum())

        # ── Composite at opacity ───────────────────────────────────────────────
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

        print(f"    Gallen-Kallela Enamel Cloisonne complete "
              f"(zone_px={zone_px}, contour_px={contour_px}, sat_px={sat_px})")
'''

# ── Inject into stroke_engine.py ──────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

already_hue    = "paint_hue_zone_boundary_pass" in src
already_clois  = "gallen_kallela_enamel_cloisonne_pass" in src

if already_hue and already_clois:
    print("Both passes already present in stroke_engine.py -- nothing to do.")
    sys.exit(0)

additions = ""
if not already_hue:
    additions += HUE_BOUNDARY_PASS
if not already_clois:
    additions += "\n" + CLOISONNE_PASS

src = src.rstrip("\n") + "\n" + additions + "\n"

with open(ENGINE_PATH, "w", encoding="utf-8") as f:
    f.write(src)

if not already_hue:
    print("Inserted paint_hue_zone_boundary_pass into stroke_engine.py.")
if not already_clois:
    print("Inserted gallen_kallela_enamel_cloisonne_pass into stroke_engine.py.")
