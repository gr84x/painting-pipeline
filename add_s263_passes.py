"""Insert paint_flat_zone_pass (s263 improvement) and
vallotton_dark_interior_pass (174th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_flat_zone_pass (s263 improvement) ──────────────────────────

FLAT_ZONE_PASS = '''
    def paint_flat_zone_pass(
        self,
        zone_radius:    int   = 5,
        preserve_edges: float = 0.82,
        ground_r:       float = 0.78,
        ground_g:       float = 0.72,
        ground_b:       float = 0.62,
        ground_strength: float = 0.08,
        edge_sigma:     float = 1.5,
        noise_seed:     int   = 263,
        opacity:        float = 0.68,
    ) -> None:
        r"""Flat Zone -- session 263 artistic improvement.

        THREE-STAGE FLAT-COLOUR ZONE UNIFICATION INSPIRED BY NABIS AND
        JAPANESE WOODBLOCK PRINT TECHNIQUE (Vallotton, Vuillard, Sérusier,
        Hokusai, c.1885-1910):

        The Nabis were inspired by Gauguin\'s dictum that painting should be
        flat coloured surfaces assembled in a certain order.  Félix Vallotton,
        Édouard Vuillard, and Paul Sérusier treated each zone of a composition
        as a near-uniform patch of colour -- the wallpaper a single dusty mauve
        field, the tablecloth a single warm cream, the dress a single muted rose
        -- modulated only by the texture of the support and the slight chaos of
        individual marks.  This is the anti-academic, anti-tonal quality they
        absorbed from Japanese woodblock prints: flat, bounded, assertively
        two-dimensional.  The spatial median filter (not a Gaussian) is the
        correct model for this: it smooths within each colour zone while
        preserving the hard boundaries between zones (since the median of a
        group spanning a sharp edge stays on one side or the other, unlike the
        Gaussian average which bridges it).

        Stage 1 SPATIAL MEDIAN ZONE FLATTENING: Apply ndimage.median_filter
        with footprint size (2*zone_radius+1)^2 to each colour channel
        independently:
          R_flat = median_filter(R, size=2*zone_radius+1)
          G_flat = median_filter(G, size=2*zone_radius+1)
          B_flat = median_filter(B, size=2*zone_radius+1)
        Median filtering removes within-zone tonal graduation while preserving
        the high-contrast edges between zones (the median at a boundary pixel
        is determined by whichever side dominates the filter footprint, so the
        edge location is preserved at half-pixel precision rather than being
        smeared like a Gaussian).
        NOVEL: (a) CHANNEL-BY-CHANNEL SPATIAL MEDIAN FILTER FOR FLAT-ZONE
        UNIFICATION WITH EDGE PRESERVATION -- first pass to apply a spatial
        median filter (ndimage.median_filter) independently per colour channel
        to create Nabis-style flat colour zones while inherently preserving
        edge boundaries; paint_scumble_pass applies a dry-brush drag with
        random stroke placement; paint_atmospheric_recession_pass applies an
        isotropic Gaussian blur for atmospheric haze; no prior pass applies a
        spatial median filter that specifically preserves zone boundary edges
        while smoothing within-zone tonal variation.

        Stage 2 EDGE-PRESERVED COMPOSITE: Compute a Sobel edge magnitude mask
        from the original image:
          Gx = convolve(lum, sobel_x); Gy = convolve(lum, sobel_y)
          edge_mag = sqrt(Gx^2 + Gy^2)
          edge_blur = gaussian_filter(edge_mag, sigma=edge_sigma)
          edge_w = clip(edge_blur / edge_blur.max(), 0, 1) * preserve_edges
        Blend: R_out = R_flat*(1-edge_w) + R*edge_w
        NOVEL: (b) SOBEL-MAGNITUDE EDGE PRESERVATION MASK APPLIED TO A MEDIAN-
        FILTERED COMPOSITE -- first pass to compute a Sobel gradient-based
        edge-preservation mask and use it to alpha-blend a spatially-filtered
        image (retaining the original at edges) so that the flat-zone filter
        does not destroy form-defining contours; paint_sfumato_contour_dissolution
        uses a similar Sobel mask but ADDS dissolution at edges rather than
        using it to PRESERVE them; no prior pass applies a Sobel magnitude mask
        to preferentially retain the original image at edges while using a
        spatial flattening filter in the interior of flat zones.

        Stage 3 WARM GROUND REVEAL IN FLAT ZONES: In image regions where local
        saturation is low (flat, near-grey zones), blend a faint trace of the
        warm ground colour (ground_r, ground_g, ground_b):
          local_sat = (max_channel - min_channel) / (max_channel + 1e-6)
          ground_w = clip((flat_thresh - local_sat) / flat_thresh, 0, 1)
                     * ground_strength
          R_final = R_out + ground_w * (ground_r - R_out)
        NOVEL: (c) SATURATION-GATED WARM GROUND COLOUR REVEAL IN LOW-SATURATION
        ZONES -- first pass to use per-pixel local saturation as a gate to blend
        a warm ground colour specifically into flat/neutral areas while leaving
        chromatic zones untouched; paint_triple_zone_glaze applies a luminance-
        gated glaze; no prior pass uses local saturation (chroma) as the gate
        for a selective warm-ground-reveal blend.
        """
        print("    Flat Zone pass (session 263 improvement)...")

        import numpy as _np
        from scipy.ndimage import median_filter as _mf, gaussian_filter as _gf
        from scipy.ndimage import convolve as _conv

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Spatial Median Zone Flattening ───────────────────────────
        sz  = max(3, 2 * int(zone_radius) + 1)
        r_flat = _mf(r0, size=sz).astype(_np.float32)
        g_flat = _mf(g0, size=sz).astype(_np.float32)
        b_flat = _mf(b0, size=sz).astype(_np.float32)

        # ── Stage 2: Edge-Preserved Composite ─────────────────────────────────
        lum0 = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        sobel_x = _np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=_np.float32)
        sobel_y = sobel_x.T

        gx = _conv(lum0, sobel_x, mode="reflect").astype(_np.float32)
        gy = _conv(lum0, sobel_y, mode="reflect").astype(_np.float32)
        edge_mag = _np.sqrt(gx * gx + gy * gy).astype(_np.float32)

        esig = max(float(edge_sigma), 0.5)
        edge_blur = _gf(edge_mag, sigma=esig).astype(_np.float32)
        emx = edge_blur.max()
        edge_norm = _np.clip(edge_blur / (emx + 1e-6), 0.0, 1.0).astype(_np.float32)

        pe = float(preserve_edges)
        edge_w = (edge_norm * pe).astype(_np.float32)

        r1 = (r_flat * (1.0 - edge_w) + r0 * edge_w).astype(_np.float32)
        g1 = (g_flat * (1.0 - edge_w) + g0 * edge_w).astype(_np.float32)
        b1 = (b_flat * (1.0 - edge_w) + b0 * edge_w).astype(_np.float32)

        # ── Stage 3: Warm Ground Reveal in Flat Zones ─────────────────────────
        ch_max = _np.maximum(_np.maximum(r1, g1), b1)
        ch_min = _np.minimum(_np.minimum(r1, g1), b1)
        local_sat = (ch_max - ch_min) / (ch_max + 1e-6)
        local_sat = _np.clip(local_sat, 0.0, 1.0).astype(_np.float32)

        flat_thresh = 0.30
        ground_blend = _np.clip((flat_thresh - local_sat) / (flat_thresh + 1e-6),
                                0.0, 1.0).astype(_np.float32)
        ground_blend = (ground_blend * float(ground_strength)).astype(_np.float32)

        gr_r = float(ground_r); gr_g = float(ground_g); gr_b = float(ground_b)

        r2 = _np.clip(r1 + ground_blend * (gr_r - r1), 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 + ground_blend * (gr_g - g1), 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 + ground_blend * (gr_b - b1), 0.0, 1.0).astype(_np.float32)

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

        flat_px   = int((local_sat < flat_thresh).sum())
        edge_px   = int((edge_w > 0.3).sum())
        ground_px = int((ground_blend > 0.03).sum())
        print(f"    Flat Zone pass complete "
              f"(flat_px={flat_px}, edge_preserved_px={edge_px}, "
              f"ground_reveal_px={ground_px})")
'''

# ── Pass 2: vallotton_dark_interior_pass (174th mode) ────────────────────────

VALLOTTON_PASS = '''
    def vallotton_dark_interior_pass(
        self,
        shadow_crush:    float = 0.38,
        crush_steepness: float = 6.0,
        lamp_cx:         float = 0.50,
        lamp_cy:         float = 0.35,
        lamp_radius:     float = 0.22,
        lamp_r:          float = 0.96,
        lamp_g:          float = 0.88,
        lamp_b:          float = 0.62,
        lamp_strength:   float = 0.32,
        contour_sigma:   float = 1.2,
        contour_thresh:  float = 0.055,
        contour_dark:    float = 0.55,
        noise_seed:      int   = 263,
        opacity:         float = 0.80,
    ) -> None:
        r"""Vallotton Dark Interior -- session 263, 174th distinct mode.

        THREE-STAGE STARK INTERIOR CHIAROSCURO TECHNIQUE INSPIRED BY
        FÉLIX VALLOTTON\'S LAMP-LIT INTERIOR PAINTINGS (c.1895-1920):

        Félix Vallotton (1865-1925), the Swiss-French Nabi, painted interiors
        of a fundamentally different quality from his colleague Vuillard.  Where
        Vuillard dissolved figure into ground with equal-intensity marks, Vallotton
        DRAMATIZED the domestic interior: the lamp-lit room was a stage for
        psychological tension, with hard shadows that cut across the floor in
        geometric precision, figures that become silhouettes against bright
        backgrounds, and a Japanese-influenced flatness that gave every object
        the weight of a symbol.  Three technical signatures define his work:
        (1) SHADOW CRUSH: Vallotton pushed dark zones to near-black with extreme
        contrast -- the shadow under the table, the back wall behind the figure,
        the dark dress fabric -- these are darker than the Impressionists would
        ever permit, almost black, against which even a mid-grey reads as light;
        (2) RADIAL LAMP POOL: a warm amber radial glow centred on the light source
        (a kerosene lamp, a hanging lamp-shade) that bleeds warmth into the
        middle-zone colours in a concentric gradient; (3) JAPANESE INK CONTOUR:
        hard dark outlines at major tonal transitions -- the silhouette of a
        figure against the lamp-lit wall, the edge of the table on the floor --
        modelling his woodcut-influenced approach where contours are drawn, not
        implied.

        Stage 1 SHADOW CRUSH: For pixels with luminance below shadow_crush,
        apply a sigmoid-steepened compression that pushes them toward near-black:
          lum_offset = lum - shadow_crush
          crushed_lum = shadow_crush / (1 + exp(-crush_steepness * lum_offset))
          scale = crushed_lum / (lum + 1e-6), clamped [0, 1]
          R_crushed = R * scale; G_crushed = G * scale; B_crushed = B * scale
        This creates the characteristic Vallotton near-black shadow zone that
        sits below all other tonal ranges in the painting.
        NOVEL: (a) SIGMOID-STEEPENED SHADOW CRUSH BELOW A LUMINANCE THRESHOLD
        -- first pass to apply a sigmoid function specifically below shadow_crush
        (not above as paint_tonal_key does with target key) to push sub-threshold
        pixels aggressively toward near-black while leaving mid-tones and lights
        untouched; paint_tonal_key applies a full-range sigmoid shift; no prior
        pass uses a below-threshold sigmoid to create the Vallotton flat near-
        black shadow pool independently of the mid/highlight tonal zones.

        Stage 2 RADIAL LAMP WARMTH POOL: Compute a radial distance falloff from
        the lamp centre (lamp_cx, lamp_cy in [0,1] image coordinates):
          dx = (x/W - lamp_cx); dy = (y/H - lamp_cy)
          dist = sqrt(dx^2 + dy^2)
          lamp_w = clip(1 - dist/lamp_radius, 0, 1)^2 * lamp_strength
          R_warm = R + lamp_w * (lamp_r - R)
          G_warm = G + lamp_w * (lamp_g - G)
          B_warm = B + lamp_w * (lamp_b - B)
        The quadratic falloff (^2) creates a pool of warmth concentrated near
        the lamp that fades smoothly to the room\'s ambient tone.
        NOVEL: (b) QUADRATIC-FALLOFF RADIAL WARM LAMP POOL CENTRED ON A
        CONFIGURABLE IMAGE-SPACE LAMP COORDINATE -- first pass to apply a
        radially-decaying warm-colour blend centred on a user-specified lamp
        position (lamp_cx, lamp_cy as fractions of image dimensions) with a
        quadratic distance falloff; paint_halation_pass applies isotropic Gaussian
        bloom from bright regions generally; no prior pass applies a configurable
        positional warm-light pool with quadratic falloff centred at an arbitrary
        image-coordinate lamp position rather than at detected bright regions.

        Stage 3 JAPANESE INK CONTOUR OVERLAY: Detect major tonal boundaries via
        Sobel gradient; threshold at contour_thresh to produce a binary edge map;
        apply Gaussian blur (sigma=contour_sigma) to anti-alias; darken edge
        pixels toward contour_dark fraction of their current value:
          edge_mask = gaussian_filter(sobel_mag > contour_thresh, sigma=contour_sigma)
          R_contour = R * (1 - edge_mask * contour_dark)
          (same G, B)
        This creates the ink-drawn contour lines that give Vallotton\'s interiors
        their woodcut quality -- every major silhouette bounded by a dark line.
        NOVEL: (c) THRESHOLD-AND-BLUR EDGE MASK APPLIED AS A DARKENING MULTIPLIER
        TO ADD INK-QUALITY CONTOURS -- first pass to threshold a Sobel gradient map
        to produce a binary edge mask, Gaussian-anti-alias it, and use it as a
        multiplicative darkening factor (not additive like paint_contour_weight_pass)
        so edges DARKEN the existing colour rather than adding a fixed black value;
        paint_contour_weight_pass adds a fixed dark displacement; no prior pass
        multiplies a Gaussian-anti-aliased thresholded Sobel mask against the
        current colour channels to darken edges proportionally to their current
        value rather than adding a fixed dark increment.
        """
        print("    Vallotton Dark Interior pass (session 263, 174th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, convolve as _conv

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Shadow Crush ─────────────────────────────────────────────
        sc  = float(shadow_crush)
        ks  = float(crush_steepness)
        lum_offset = lum - sc
        crushed_lum = (sc / (1.0 + _np.exp(-ks * lum_offset))).astype(_np.float32)
        crushed_lum = _np.where(lum < sc, crushed_lum, lum).astype(_np.float32)
        scale = _np.clip(crushed_lum / (lum + 1e-6), 0.0, 1.0).astype(_np.float32)

        r1 = _np.clip(r0 * scale, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * scale, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * scale, 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Radial Lamp Warmth Pool ──────────────────────────────────
        lcx = float(lamp_cx); lcy = float(lamp_cy)
        lr  = max(float(lamp_radius), 0.01)
        ls  = float(lamp_strength)
        lr_v = float(lamp_r); lg_v = float(lamp_g); lb_v = float(lamp_b)

        xs = (_np.arange(w, dtype=_np.float32) / w)[_np.newaxis, :]
        ys = (_np.arange(h, dtype=_np.float32) / h)[:, _np.newaxis]
        dx = xs - lcx
        dy = ys - lcy
        dist = _np.sqrt(dx * dx + dy * dy).astype(_np.float32)
        lamp_w = _np.clip(1.0 - dist / lr, 0.0, 1.0) ** 2 * ls
        lamp_w = lamp_w.astype(_np.float32)

        r2 = _np.clip(r1 + lamp_w * (lr_v - r1), 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 + lamp_w * (lg_v - g1), 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 + lamp_w * (lb_v - b1), 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Japanese Ink Contour Overlay ─────────────────────────────
        csig = max(float(contour_sigma), 0.3)
        cthr = float(contour_thresh)
        cdrk = float(contour_dark)

        sobel_x = _np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=_np.float32)
        sobel_y = sobel_x.T
        lum2 = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)
        gx = _conv(lum2, sobel_x, mode="reflect").astype(_np.float32)
        gy = _conv(lum2, sobel_y, mode="reflect").astype(_np.float32)
        sobel_mag = _np.sqrt(gx * gx + gy * gy).astype(_np.float32)
        smx = sobel_mag.max()
        sobel_norm = (sobel_mag / (smx + 1e-6)).astype(_np.float32)

        edge_binary = (sobel_norm > cthr).astype(_np.float32)
        edge_mask = _gf(edge_binary, sigma=csig).astype(_np.float32)
        edge_mask = _np.clip(edge_mask / (edge_mask.max() + 1e-6), 0.0, 1.0).astype(_np.float32)
        darken = (1.0 - edge_mask * cdrk).astype(_np.float32)

        r3 = _np.clip(r2 * darken, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 * darken, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 * darken, 0.0, 1.0).astype(_np.float32)

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

        crushed_px = int((lum < sc).sum())
        lamp_px    = int((lamp_w > 0.05).sum())
        contour_px = int((edge_mask > 0.1).sum())
        print(f"    Vallotton Dark Interior complete "
              f"(crushed_px={crushed_px}, lamp_pool_px={lamp_px}, "
              f"contour_px={contour_px})")
'''

# ── Inject into stroke_engine.py ──────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

already_flat     = "paint_flat_zone_pass" in src
already_vallotton = "vallotton_dark_interior_pass" in src

if already_flat and already_vallotton:
    print("Both passes already present in stroke_engine.py -- nothing to do.")
    sys.exit(0)

additions = ""
if not already_flat:
    additions += FLAT_ZONE_PASS
if not already_vallotton:
    additions += "\n" + VALLOTTON_PASS

src = src.rstrip("\n") + "\n" + additions + "\n"

with open(ENGINE_PATH, "w", encoding="utf-8") as f:
    f.write(src)

if not already_flat:
    print("Inserted paint_flat_zone_pass into stroke_engine.py.")
if not already_vallotton:
    print("Inserted vallotton_dark_interior_pass into stroke_engine.py.")
