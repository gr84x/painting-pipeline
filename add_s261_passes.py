"""Insert sisley_silver_veil_pass and paint_triple_zone_glaze_pass
into stroke_engine.py (session 261).

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: sisley_silver_veil_pass ──────────────────────────────────────────

SISLEY_PASS = """
    def sisley_silver_veil_pass(
        self,
        sky_fraction:       float = 0.42,
        sky_r:              float = 0.84,
        sky_g:              float = 0.85,
        sky_b:              float = 0.88,
        sky_strength:       float = 0.38,
        haze_center:        float = 0.56,
        haze_band:          float = 0.18,
        haze_r:             float = 0.78,
        haze_g:             float = 0.78,
        haze_b:             float = 0.81,
        haze_strength:      float = 0.32,
        sky_blur_sigma:     float = 6.0,
        sky_blur_opacity:   float = 0.48,
        noise_seed:         int   = 261,
        opacity:            float = 0.78,
    ) -> None:
        r\"\"\"Alfred Sisley Silver Veil -- session 261, 172nd distinct mode.

        THREE-STAGE SILVERY IMPRESSIONIST LANDSCAPE TECHNIQUE INSPIRED BY
        ALFRED SISLEY'S ATMOSPHERIC PAINTING (c.1870-1899):

        Alfred Sisley (1839-1899), the most consistently atmospheric of the
        Impressionists, painted the same reaches of the Seine and Loing rivers
        for thirty years, developing three defining painterly qualities: a
        characteristic cool silver sky that sets the tonal key of the whole
        picture, a neutral silver mist at middle distances that softens and
        desaturates the midground without introducing warm or cool bias, and
        predominantly horizontal stroke direction in sky and water that gives
        his paintings the quality of wind-driven cloud movement.

        Stage 1 SILVER SKY BAND: Sisley devoted more canvas to sky than any
        other Impressionist, treating it as a cool silver-grey field with an
        occasional warm horizon accent.  Model this by applying a cool silver
        tint (sky_r, sky_g, sky_b) to the upper sky_fraction of the image with
        a linear vertical weight that is strongest at the top and zero at the
        sky boundary:
          sky_weight(y) = clip(1 - y / (sky_fraction * H), 0, 1) * sky_strength
          R_new = R * (1 - sky_weight) + sky_r * sky_weight
          G_new = G * (1 - sky_weight) + sky_g * sky_weight
          B_new = B * (1 - sky_weight) + sky_b * sky_weight
        NOVEL: (a) VERTICAL-ZONE-BOUNDED ADDITIVE SILVER TINT IN UPPER HEIGHT
        FRACTION -- first pass to apply a spatially-bounded tint limited to a
        configurable upper height fraction (sky_fraction) with a linear vertical
        weight gradient strongest at the top edge and zero at the zone boundary;
        paint_glaze_gradient_pass applies a multiplicative glaze over the FULL
        CANVAS along an axis; paint_atmospheric_recession_pass shifts color
        temperature from far to near; no prior pass applies an additive blend
        toward a specific silver target limited to a configurable TOP FRACTION
        of the canvas height with linear weight decay to zero at the fraction
        boundary.

        Stage 2 MIDGROUND SILVER ATMOSPHERIC HAZE: At middle distances, Sisley
        applied a thin neutral-grey veil that softens midground colours toward
        a cool silver -- neither warm nor cool, simply neutral and atmospheric.
        Model this via a Gaussian bell-curve weight centered on the midtone
        luminance (haze_center), blending pixels in that luminance band toward
        the silver target (haze_r, haze_g, haze_b):
          bell_weight = exp(-0.5 * ((lum - haze_center) / haze_band)^2) * haze_strength
          R_new = R * (1 - bell_weight) + haze_r * bell_weight
          G_new = G * (1 - bell_weight) + haze_g * bell_weight
          B_new = B * (1 - bell_weight) + haze_b * bell_weight
        NOVEL: (b) GAUSSIAN BELL LUMINANCE WINDOW BLENDING TOWARD A NEUTRAL
        COOL SILVER TARGET AT THE MID-LUMINANCE BAND -- first pass to use a
        Gaussian bell centered at lum=0.56 (mid-luminance) to drive a blend
        toward a specific cool-neutral silver (near-grey with slight blue bias),
        modelling Sisley's atmospheric silver mist; chirico Stage 2 uses a
        similar bell formula but drives toward warm sienna; foujita Stage 1 uses
        a one-sided above-threshold ramp; no prior pass uses a Gaussian bell
        centered on mid-luminance to blend toward a cool neutral silver as
        opposed to a warm or strongly hued target.

        Stage 3 HORIZONTAL SKY MOTION BLUR: Sisley's skies and water surfaces
        are painted with predominantly horizontal strokes, giving them a
        horizontal atmospheric motion quality.  Model this by applying a
        directional (horizontal-axis only) Gaussian blur restricted to the upper
        sky zone:
          For rows y in [0, sky_fraction * H]:
            blur_weight = clip(1 - y / (sky_fraction * H), 0, 1) * sky_blur_opacity
            blurred_R(y) = gaussian_filter_1d(R(y), sigma=sky_blur_sigma, axis=1)
            blurred_G(y) = gaussian_filter_1d(G(y), sigma=sky_blur_sigma, axis=1)
            blurred_B(y) = gaussian_filter_1d(B(y), sigma=sky_blur_sigma, axis=1)
            R_new(y) = R(y) * (1 - blur_weight) + blurred_R(y) * blur_weight
          (Rows below sky_fraction receive no blur.)
        NOVEL: (c) UNIDIRECTIONAL (HORIZONTAL-AXIS) GAUSSIAN BLUR (sigma_y=0,
        sigma_x>0) RESTRICTED TO A CONFIGURABLE UPPER VERTICAL ZONE WITH
        VERTICALLY-DECAYING BLEND WEIGHT -- first pass to apply a strictly 1D
        horizontal-only Gaussian blur (along axis=1, sigma_y=0 so vertical
        structure is preserved) limited to the top sky_fraction of the image
        with a vertical weight gradient; paint_sfumato_focus_pass applies
        isotropic radial blur; paint_atmospheric_recession_pass applies uniform
        isotropic blur; no prior pass applies a unidirectional (1D horizontal)
        blur restricted to a spatially-bounded upper vertical zone.
        \"\"\"
        print("    Sisley Silver Veil pass (session 261, 172nd mode)...")

        from scipy.ndimage import gaussian_filter1d as _gf1d

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Silver Sky Band ───────────────────────────────────────────
        sf = float(sky_fraction)
        sky_rows = int(sf * h)
        sr = float(sky_r); sg = float(sky_g); sb_col = float(sky_b)
        sstr = float(sky_strength)

        ys = _np.arange(h, dtype=_np.float32)
        sky_w = _np.clip(1.0 - ys / (max(sky_rows, 1)), 0.0, 1.0) * sstr
        sky_w = sky_w[:, _np.newaxis]  # (h, 1) broadcast over width

        r1 = _np.clip(r0 * (1.0 - sky_w) + sr * sky_w, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * (1.0 - sky_w) + sg * sky_w, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * (1.0 - sky_w) + sb_col * sky_w, 0.0, 1.0).astype(_np.float32)

        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)

        # ── Stage 2: Midground Silver Atmospheric Haze ────────────────────────
        hc = float(haze_center)
        hb = max(float(haze_band), 1e-4)
        hstr = float(haze_strength)
        hr = float(haze_r); hg = float(haze_g); hb_col = float(haze_b)

        bell = _np.exp(-0.5 * ((lum1 - hc) / hb) ** 2).astype(_np.float32)
        bell_w = _np.clip(bell * hstr, 0.0, 1.0).astype(_np.float32)

        r2 = _np.clip(r1 * (1.0 - bell_w) + hr * bell_w, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 * (1.0 - bell_w) + hg * bell_w, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 * (1.0 - bell_w) + hb_col * bell_w, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Horizontal Sky Motion Blur ───────────────────────────────
        bs = max(float(sky_blur_sigma), 0.5)
        bop = float(sky_blur_opacity)

        # Horizontal-only blur (1D along axis=1) for full image first
        r_hblur = _gf1d(r2, sigma=bs, axis=1).astype(_np.float32)
        g_hblur = _gf1d(g2, sigma=bs, axis=1).astype(_np.float32)
        b_hblur = _gf1d(b2, sigma=bs, axis=1).astype(_np.float32)

        # Apply blur only in sky zone with vertically-decaying weight
        sky_blur_w = _np.clip(1.0 - ys / (max(sky_rows, 1)), 0.0, 1.0) * bop
        sky_blur_w = sky_blur_w[:, _np.newaxis]

        r3 = _np.clip(r2 * (1.0 - sky_blur_w) + r_hblur * sky_blur_w, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 * (1.0 - sky_blur_w) + g_hblur * sky_blur_w, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 * (1.0 - sky_blur_w) + b_hblur * sky_blur_w, 0.0, 1.0).astype(_np.float32)

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

        sky_px  = int((sky_w[:, 0] > 0.02).sum()) * w
        haze_px = int((bell_w > 0.05).sum())
        blur_px = int((sky_blur_w[:, 0] > 0.02).sum()) * w
        print(f"    Sisley Silver Veil complete "
              f"(sky_tinted_px={sky_px}, haze_px={haze_px}, "
              f"sky_blurred_px={blur_px})")
"""

# ── Pass 2: paint_triple_zone_glaze_pass ──────────────────────────────────────

TRIPLE_ZONE_GLAZE_PASS = """
    def paint_triple_zone_glaze_pass(
        self,
        shadow_pivot:     float = 0.28,
        highlight_pivot:  float = 0.68,
        zone_feather:     float = 0.12,
        shadow_r:         float = 0.25,
        shadow_g:         float = 0.28,
        shadow_b:         float = 0.48,
        shadow_opacity:   float = 0.12,
        mid_r:            float = 0.72,
        mid_g:            float = 0.68,
        mid_b:            float = 0.52,
        mid_opacity:      float = 0.08,
        highlight_r:      float = 0.92,
        highlight_g:      float = 0.88,
        highlight_b:      float = 0.78,
        highlight_opacity: float = 0.10,
        feather_sigma:    float = 8.0,
        noise_seed:       int   = 261,
        opacity:          float = 0.72,
    ) -> None:
        r\"\"\"Triple Zone Glaze -- session 261 artistic improvement.

        THREE-STAGE INDEPENDENT ZONE GLAZING INSPIRED BY OLD MASTER OIL
        GLAZING PRACTICE (Titian, Rubens, Rembrandt, c.1500-1700):

        Traditional oil glazing applies thin transparent colour layers over
        dried paint to modify colour relationships within specific tonal zones.
        Titian would apply a warm amber glaze selectively in the midtone flesh
        passages; Rembrandt would deepen shadow zones with a cool brown-black
        transparent scumble while leaving highlights untouched; Vermeer applied
        a cool blue-grey glaze in shadow zones while warming highlight passages
        with a cream veil.  In each case the glaze colours for shadow, midtone,
        and highlight zones were INDEPENDENT colour choices reflecting the
        painter's reading of the specific light quality.

        Stage 1 THREE-ZONE LUMINANCE SEGMENTATION WITH GAUSSIAN FEATHERING:
        Compute three smooth zone masks with Gaussian-feathered boundaries:
          raw_shadow    = clip((shadow_pivot - lum) / zone_feather, 0, 1)
          raw_highlight = clip((lum - highlight_pivot) / zone_feather, 0, 1)
          raw_mid       = clip(1 - raw_shadow - raw_highlight, 0, 1)
          shadow_mask    = gaussian_filter(raw_shadow,    sigma=feather_sigma)
          highlight_mask = gaussian_filter(raw_highlight, sigma=feather_sigma)
          mid_mask       = gaussian_filter(raw_mid,       sigma=feather_sigma)
        Gaussian feathering prevents hard zone boundaries.
        NOVEL: (a) GAUSSIAN-FEATHERED THREE-ZONE LUMINANCE SEGMENTATION WITH
        INDEPENDENT MASK PER ZONE -- first pass to Gaussian-blur the raw
        luminance-threshold zone masks before using them as glaze opacity
        weights, creating smooth zone boundary transitions; paint_split_toning
        uses linear ramp transitions without Gaussian smoothing of the mask
        itself; no prior pass Gaussian-blurs the zone membership masks to
        create spatially-smoothed zone boundaries before compositing.

        Stage 2 INDEPENDENT ZONE GLAZE APPLICATION:
        Apply a distinct transparent glaze colour to each zone:
          glaze_R = R + shadow_mask*shadow_opacity*(shadow_r - R)
                      + mid_mask*mid_opacity*(mid_r - R)
                      + highlight_mask*highlight_opacity*(highlight_r - R)
          (same for G, B channels)
        Each zone glaze has its own (R,G,B) target and opacity.
        NOVEL: (b) THREE INDEPENDENT TARGET-COLOR TRANSPARENT GLAZES APPLIED
        SIMULTANEOUSLY TO THREE LUMINANCE ZONES -- first pass to apply three
        separate color-targeted glazes each with its own (R,G,B) and opacity
        to three independently-segmented luminance zones; paint_split_toning
        applies opposing incremental offsets to two zones only; paint_glaze_gradient
        applies ONE color over a spatial gradient; no prior pass applies THREE
        distinct target colors to three independently-controlled tonal zones.

        Stage 3 ZONE-BOUNDARY ANTI-CONTAMINATION FEATHERING:
        At pixels where two zone masks are both significant, reduce glaze
        opacity to prevent colour fringing:
          blend_conflict = shadow_mask * highlight_mask
                         + shadow_mask * mid_mask * 0.5
                         + mid_mask * highlight_mask * 0.5
          feather_gate = clip(1 - blend_conflict * 2.5, 0.3, 1.0)
          final = original * (1 - feather_gate) + glaze * feather_gate
        NOVEL: (c) MULTI-ZONE OVERLAP CONFLICT DETECTION AND OPACITY REDUCTION --
        first pass to compute a zone-overlap conflict weight and attenuate glaze
        opacity at zone boundaries, preventing colour fringing from simultaneous
        zone membership.
        \"\"\"
        print("    Triple Zone Glaze pass (session 261 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Three-Zone Segmentation with Gaussian Feathering ─────────
        sp  = float(shadow_pivot)
        hp  = float(highlight_pivot)
        zf  = max(float(zone_feather), 1e-4)
        fsg = max(float(feather_sigma), 0.5)

        raw_shadow    = _np.clip((sp - lum) / zf, 0.0, 1.0).astype(_np.float32)
        raw_highlight = _np.clip((lum - hp) / zf, 0.0, 1.0).astype(_np.float32)
        raw_mid       = _np.clip(1.0 - raw_shadow - raw_highlight, 0.0, 1.0).astype(_np.float32)

        shadow_mask    = _gf(raw_shadow,    sigma=fsg).astype(_np.float32)
        highlight_mask = _gf(raw_highlight, sigma=fsg).astype(_np.float32)
        mid_mask       = _gf(raw_mid,       sigma=fsg).astype(_np.float32)

        shadow_mask    = _np.clip(shadow_mask    / (shadow_mask.max()    + 1e-6), 0.0, 1.0)
        highlight_mask = _np.clip(highlight_mask / (highlight_mask.max() + 1e-6), 0.0, 1.0)
        mid_mask       = _np.clip(mid_mask       / (mid_mask.max()       + 1e-6), 0.0, 1.0)

        # ── Stage 2: Independent Zone Glaze Application ───────────────────────
        sr = float(shadow_r);  sg_c = float(shadow_g); sb_col = float(shadow_b)
        so = float(shadow_opacity)
        mr = float(mid_r);     mg = float(mid_g);      mb = float(mid_b)
        mo = float(mid_opacity)
        hr = float(highlight_r); hg = float(highlight_g); hb = float(highlight_b)
        ho = float(highlight_opacity)

        glaze_r = (r0
                   + shadow_mask    * so * (sr - r0)
                   + mid_mask       * mo * (mr - r0)
                   + highlight_mask * ho * (hr - r0))
        glaze_g = (g0
                   + shadow_mask    * so * (sg_c - g0)
                   + mid_mask       * mo * (mg - g0)
                   + highlight_mask * ho * (hg - g0))
        glaze_b = (b0
                   + shadow_mask    * so * (sb_col - b0)
                   + mid_mask       * mo * (mb - b0)
                   + highlight_mask * ho * (hb - b0))

        glaze_r = _np.clip(glaze_r, 0.0, 1.0).astype(_np.float32)
        glaze_g = _np.clip(glaze_g, 0.0, 1.0).astype(_np.float32)
        glaze_b = _np.clip(glaze_b, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Zone-Boundary Anti-Contamination Feathering ──────────────
        blend_conflict = (shadow_mask * highlight_mask
                          + shadow_mask * mid_mask * 0.5
                          + mid_mask * highlight_mask * 0.5).astype(_np.float32)
        feather_gate = _np.clip(1.0 - blend_conflict * 2.5, 0.3, 1.0).astype(_np.float32)

        r1 = _np.clip(r0 * (1.0 - feather_gate) + glaze_r * feather_gate, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * (1.0 - feather_gate) + glaze_g * feather_gate, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * (1.0 - feather_gate) + glaze_b * feather_gate, 0.0, 1.0).astype(_np.float32)

        # ── Composite at opacity ───────────────────────────────────────────────
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

        shadow_px    = int((shadow_mask > 0.1).sum())
        mid_px       = int((mid_mask > 0.1).sum())
        highlight_px = int((highlight_mask > 0.1).sum())
        conflict_px  = int((blend_conflict > 0.1).sum())
        print(f"    Triple Zone Glaze complete "
              f"(shadow_px={shadow_px}, mid_px={mid_px}, "
              f"highlight_px={highlight_px}, conflict_feathered_px={conflict_px})")
"""

# ── Inject into stroke_engine.py ──────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

already_sisley  = "sisley_silver_veil_pass" in src
already_triple  = "paint_triple_zone_glaze_pass" in src

if already_sisley and already_triple:
    print("Both passes already present in stroke_engine.py -- nothing to do.")
    sys.exit(0)

additions = ""
if not already_sisley:
    additions += SISLEY_PASS
if not already_triple:
    additions += "\n" + TRIPLE_ZONE_GLAZE_PASS

src = src.rstrip("\n") + "\n" + additions + "\n"

with open(ENGINE_PATH, "w", encoding="utf-8") as f:
    f.write(src)

if not already_sisley:
    print("Inserted sisley_silver_veil_pass into stroke_engine.py.")
if not already_triple:
    print("Inserted paint_triple_zone_glaze_pass into stroke_engine.py.")
