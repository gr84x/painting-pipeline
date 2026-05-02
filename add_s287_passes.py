"""Insert paint_median_clarity_pass (s287 improvement) and
hartley_elemental_mass_pass (198th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_median_clarity_pass (s287 improvement) ─────────────────────

MEDIAN_CLARITY_PASS = '''
    def paint_median_clarity_pass(
        self,
        median_size:          int   = 5,
        detail_boost:         float = 1.90,
        midtone_center:       float = 0.50,
        midtone_width:        float = 0.38,
        shadow_floor:         float = 0.14,
        shadow_reset_strength:float = 0.60,
        opacity:              float = 0.80,
    ) -> None:
        r"""Median Clarity -- s287 improvement.

        THE PHYSICAL BASIS: RANK-ORDER DETAIL EXTRACTION WITH
        MEDIAN FILTER BASE AND SHADOW-FLOOR PROTECTION

        The question of which component of an image contains "structure"
        (gross form, broad colour masses) and which contains "detail"
        (fine texture, paint marks, edge sharpness) underlies every
        sharpening, clarifying, and frequency-separation pass in painting
        software. The standard answer since the 1980s has been: use a
        Gaussian blur as the "structure" estimate, subtract it to get
        "detail," then amplify the detail and recombine. This is exactly
        what the frequency separation pass (s285) implements.

        The median filter offers a fundamentally different estimate of
        "structure." Unlike the Gaussian -- which is a weighted average
        that blends every pixel with all its neighbours -- the median
        selects the middle value of a neighbourhood sorted by intensity.
        This produces a radically different artifact profile:

          * EDGE PRESERVATION: A Gaussian blurs step edges toward gradients;
            a median preserves step edges intact within the filter radius.
            A thin painted line (1-2px wide) disappears into a Gaussian blur
            at any sigma larger than the line width. A median filter of
            size 5×5 preserves lines 3+ pixels wide unchanged; only lines
            thinner than 2px are affected.

          * OUTLIER REJECTION: A single bright specular or very dark crack
            in a painted surface pulls the Gaussian mean toward it for the
            entire sigma radius. The median ignores outliers completely,
            providing a clean "background" for the surface around fine marks.

          * TEXTURE ALIASING: Gaussian-based detail layers alias with painted
            texture in a smoothly varying way. Median-based detail layers
            have sharper "pop" because the base is non-linear; texture details
            appear as absolute deviations from a step-function base rather
            than relative deviations from a smooth one.

        These properties make the median-based clarity pass particularly
        suited to painterly images, where:
          - Thick impasto ridges (bright outliers above the local mean)
          - Dark shadow cracks (dark outliers below the local mean)
          - Preserved paint edges (not smeared by the base)
        all need to be treated differently from smooth gradients.

        ARTISTIC CONTEXT: CLARITY VS. SHARPNESS

        In photographic processing, "clarity" (distinct from sharpness) refers
        to mid-frequency contrast enhancement: the range of detail between
        fine texture (sharpening) and global contrast (levels). In painting
        practice, this corresponds to the visibility of individual brush strokes
        and the legibility of internal form modeling -- the kind of presence
        Hartley achieved through thick application of paint without blending.
        The median filter, with its preserved-edge characteristic, is the
        appropriate base for a clarity pass intended to enhance painted detail
        rather than photographic fine grain.

        STAGE 1 -- PER-CHANNEL MEDIAN FILTER:

        For each colour channel C in {R, G, B}:
          C_med = median_filter(C, size=median_size)

        The median_filter uses a square neighbourhood of median_size x
        median_size pixels (default 5x5 = 25 pixels). It ranks all 25
        values and returns the 13th-ranked (middle) value.

        NOVEL: (a) FIRST USE OF RANK-ORDER (NON-LINEAR) FILTER IN ENGINE.
        Every prior spatial smoothing operation in this engine uses
        scipy.ndimage.gaussian_filter: a linear convolution kernel whose
        output is a weighted average of neighbourhood values. The median
        filter is fundamentally non-linear: its output is not derivable
        from any linear combination of neighbouring pixels. It is the
        canonical example of an order-statistic (rank-order) filter. No
        prior pass in the 197-mode engine uses median_filter, max_filter,
        min_filter, or any rank-order operation. This is the first.

        STAGE 2 -- DETAIL LAYER EXTRACTION:

        For each channel:
          C_detail = C - C_med

        C_detail contains: preserved painted edges, fine texture above and
        below the local median, and specular/shadow outliers.

        NOVEL: (b) MEDIAN-BASED DETAIL LAYER (vs GAUSSIAN-BASED).
        The s285 frequency separation pass uses:
          low = Gaussian(canvas, sigma=16)
          high = canvas - low
        The present pass uses:
          low = median_filter(canvas, size=5)
          detail = canvas - low
        These are mathematically distinct. The median-based detail layer
        has zero contribution from step edges within the filter radius
        (because the median preserves steps); the Gaussian-based detail
        layer has a bipolar spike at every step edge. The practical
        consequence: median-based detail is a cleaner representation of
        local texture deviation; Gaussian-based detail contains both
        texture AND a ringing artifact at sharp paint edges.

        STAGE 3 -- MIDTONE-GATED DETAIL AMPLIFICATION:

        Compute luminance L = 0.299R + 0.587G + 0.114B.
        Midtone bell gate:
          bell = max(0, 1 - |L - midtone_center| / midtone_half_width)^2

        Amplification factor at each pixel:
          amp = 1.0 + bell * (detail_boost - 1.0)

        Amplified detail: C_detail_amp = C_detail * amp

        Recombined: C_boosted = C_med + C_detail_amp

        In the midtone zone (near L=midtone_center): amp ≈ detail_boost.
        In shadows (L≈0) and highlights (L≈1): amp ≈ 1.0 (neutral).
        This confines the clarity enhancement to the range of luminance
        values where painted form is most legible: the middle third of
        the tonal range.

        STAGE 4 -- SHADOW-FLOOR PROTECTION:

        Detail amplification can lift the very darkest pixels (where the
        original image was near-black) by amplifying a detail layer that
        might contain negative values above the median base. To prevent
        Hartley\'s deep shadow masses from being lifted toward grey:

          shadow_gate = clip( (shadow_floor - L) / max(shadow_floor, eps), 0, 1 )
          C_out = C_boosted + shadow_gate * shadow_reset_strength * (C - C_boosted)

        Where shadow_gate is 1.0 at L=0 (pure black) and 0.0 at L=shadow_floor.
        The blend (C_boosted + gate * strength * (C - C_boosted)) = lerp toward
        original, so very dark pixels are partially reset to their pre-pass
        values.

        NOVEL: (c) SHADOW-FLOOR PROTECTION PASS.
        No prior clarity or sharpening pass in this engine applies a
        post-amplification shadow reset. The s285 frequency separation
        pass applies uniform opacity to the recombined canvas; it does
        not protect any specific tonal zone from amplification. The
        paint_tonal_rebalance_pass (s286) operates on the full tonal
        range. The present Stage 4 specifically identifies the very
        darkest pixels (L < shadow_floor) and reduces the effect of
        the preceding amplification in those zones, protecting Hartley\'s
        characteristically deep dark masses from being washed out.
        """
        print("    Median Clarity pass (session 287 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf
        from scipy.ndimage import median_filter as _mf

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        eps = 1e-6
        sz  = max(int(median_size), 3)

        # Stage 1: Median filter (rank-order non-linear smoothing)
        R_med = _mf(R, size=sz).astype(_np.float32)
        G_med = _mf(G, size=sz).astype(_np.float32)
        B_med = _mf(B, size=sz).astype(_np.float32)

        # Stage 2: Detail extraction (original - median)
        R_det = (R - R_med).astype(_np.float32)
        G_det = (G - G_med).astype(_np.float32)
        B_det = (B - B_med).astype(_np.float32)

        # Stage 3: Midtone-gated detail amplification
        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)
        hw = max(float(midtone_width) * 0.5, 0.05)
        mc = float(midtone_center)
        bell_raw = _np.clip(1.0 - _np.abs(L - mc) / hw, 0.0, 1.0).astype(_np.float32)
        bell = (bell_raw * bell_raw).astype(_np.float32)

        db = float(detail_boost)
        amp = (1.0 + bell * (db - 1.0)).astype(_np.float32)

        R_boost = _np.clip(R_med + R_det * amp, 0.0, 1.0).astype(_np.float32)
        G_boost = _np.clip(G_med + G_det * amp, 0.0, 1.0).astype(_np.float32)
        B_boost = _np.clip(B_med + B_det * amp, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Shadow-floor protection (blend back toward original for deep darks)
        sf  = max(float(shadow_floor), 0.01)
        srs = float(shadow_reset_strength)
        shadow_gate = _np.clip((sf - L) / sf, 0.0, 1.0).astype(_np.float32)
        reset_weight = (shadow_gate * srs).astype(_np.float32)
        R_sf = (R_boost + reset_weight * (R - R_boost)).astype(_np.float32)
        G_sf = (G_boost + reset_weight * (G - G_boost)).astype(_np.float32)
        B_sf = (B_boost + reset_weight * (B - B_boost)).astype(_np.float32)
        R_sf = _np.clip(R_sf, 0.0, 1.0).astype(_np.float32)
        G_sf = _np.clip(G_sf, 0.0, 1.0).astype(_np.float32)
        B_sf = _np.clip(B_sf, 0.0, 1.0).astype(_np.float32)

        # Final opacity blend
        op = float(opacity)
        R_out = _np.clip(R + (R_sf - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G_sf - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B_sf - B) * op, 0.0, 1.0).astype(_np.float32)

        boosted_px  = int((bell > 0.20).sum())
        shadow_px   = int((shadow_gate > 0.10).sum())
        detail_rms  = float(_np.sqrt(_np.mean(R_det ** 2 + G_det ** 2 + B_det ** 2)))

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Median Clarity complete "
              f"(med_size={sz}, detail_boost={db:.2f}, boosted_px={boosted_px}, "
              f"shadow_px={shadow_px}, detail_rms={detail_rms:.4f})")

'''

# ── Pass 2: hartley_elemental_mass_pass (198th mode) ─────────────────────────

HARTLEY_ELEMENTAL_MASS_PASS = '''
    def hartley_elemental_mass_pass(
        self,
        palette_strength:          float = 0.52,
        interior_tile_n_h:         int   = 14,
        interior_tile_n_w:         int   = 10,
        interior_flatten_strength: float = 0.36,
        edge_darken_strength:      float = 0.55,
        edge_dark_r:               float = 0.06,
        edge_dark_g:               float = 0.06,
        edge_dark_b:               float = 0.06,
        dark_desat_thresh:         float = 0.28,
        dark_desat_strength:       float = 0.58,
        bright_sat_thresh:         float = 0.70,
        bright_sat_strength:       float = 0.52,
        opacity:                   float = 0.85,
    ) -> None:
        r"""Hartley Elemental Mass -- 198th mode (American Modernism / Marsden Hartley).

        MARSDEN HARTLEY (1877-1943) -- AMERICAN MODERNIST;
        POET OF THE ELEMENTAL LANDSCAPE:

        Marsden Hartley was born in Lewiston, Maine, in 1877, the youngest of
        nine children in a working-class English immigrant family. His mother
        died when he was eight; his father remarried and moved to Cleveland,
        leaving Hartley effectively orphaned in Maine. These twin abandonments
        -- the loss of his mother and the loss of his native Maine -- would
        shape every significant work he ever made. He spent his life returning
        to Maine in paint, even when physically elsewhere, and the mountains,
        sea cliffs, and dark spruce forests of his home state became the
        vehicle through which he processed the elemental forces of his interior
        life.

        Hartley studied at the Cleveland School of Art and then with William
        Merritt Chase in New York. But his deepest formative influence came
        through his encounter with Cezanne: the structured faceting of form,
        the insistence on underlying geometric architecture beneath the
        surface of nature, the refusal to prettify. He traveled to Paris
        (1912) and Berlin (1913-1915), where his exposure to German
        Expressionism -- particularly Franz Marc and Wassily Kandinsky --
        amplified Cezanne\'s structural logic with a chromatic intensity and
        emotional directness that Cezanne himself would have resisted.

        His German paintings (the "Portrait Arrangements" and abstract works
        of 1913-15) are his most famous: kaleidoscopic, militaristic, full
        of compressed symbols. But the work that matters most in this engine\'s
        context is the late Maine and New England work of the 1930s-40s:
        massive, simplified, dark, utterly committed to the physical weight
        of rock and mountain and sea.

        HARTLEY\'S FIVE DEFINING TECHNICAL CHARACTERISTICS:

        1. RESTRICTED EARTHEN PALETTE: Hartley\'s Maine paintings use a
           severely limited palette -- deep blue-black, dark green, raw umber,
           burnt sienna, vermillion accent, near-black, and warm cream. No
           lavenders, no delicate blues, no complex colour mixing. The palette
           is the palette of granite, dark spruce, grey sea, and the particular
           orange-amber of a Maine November sky. Every colour is pushed toward
           one of these anchors; mixed or ambiguous colours are either committed
           to one anchor or darkened to near-black.

        2. FLAT COLOUR PLANE CONSTRUCTION: Inspired by Cezanne\'s "passage"
           technique, Hartley built his canvases from discrete colour planes --
           large zones of near-uniform colour bounded by visible edges. Within
           each plane, the paint is physically thick and the colour relatively
           constant; the spatial boundaries between planes are visible as
           darker, more gestural transitions. This gives his work a mosaic-like
           or stained-glass quality, each element reading as a solid mass rather
           than a gradated form.

        3. BOLD PAINT-DRAWN OUTLINES: Hartley often reinforced the boundaries
           between his colour planes with additional dark paint that functions
           like a drawn outline -- but loaded with pigment, not a thin line.
           The dark paint at edges bridges the two adjacent colour planes and
           creates a third zone: a dark transition that has the function of
           traditional drawing but the physical substance of painting. This
           is not contour drawing; it is painted boundary.

        4. DARK MASS DOMINANCE: Hartley\'s subjects -- Mt. Katahdin, the rocks
           of Dogtown, the dark Atlantic -- are characteristically dark. Very
           dark. He did not lighten or soften dark masses for compositional
           "balance." The mountain in "Katahdin, Autumn No. 1" (1939-40) is
           nearly pure black-green; the sky above it burns with an orange
           the more intense for the darkness below. His willingness to let
           dark masses be dark -- rather than lifting them to mid-grey to
           show internal variation -- is a structural decision, not a
           consequence of limited materials.

        5. ANTI-CORRELATED SATURATION: In Hartley\'s paintings, the darkest
           zones are nearly desaturated -- the massive dark forms of rock
           and mountain lean toward grey-black, not coloured. But the
           lighter zones -- the sky, the reflected light on water, the
           autumn hillside -- are intensely saturated. This anti-correlation
           between luminance and saturation (darker = less saturated, lighter
           = more saturated) is distinctive and gives his late work its
           characteristic quality of sombre gravity in the darks and
           chromatic vitality in the lights.

        THE GREAT WORKS:
        "Katahdin, Autumn No. 1" (1939-1940): Maine\'s Mt. Katahdin as a
        massive dark triangular mass against a burning sky -- the distillation
        of Hartley\'s entire pictorial approach.

        "Evening Storm, Schoodic, Maine" (1942): Atlantic storm waves as
        dark, flat, impacted planes of blue-black and grey-white foam.

        "Blueberry Highway, Dogtown" (1931): Rocky glacial landscape in
        Gloucester reduced to flat planes of umber, grey, and deep green.

        "Dead Plover" (1940-41): Still-life with a dead bird, rendered with
        the same physical gravity he brought to the Maine coast.

        "Fox Island, Georgetown, Maine" (1937): Small island, sea, and sky
        in intensely limited palette -- dark masses and burning light.

        NOVELTY ANALYSIS: FOUR DISTINCT MATHEMATICAL INNOVATIONS:

        Stage 1 NEAREST-PALETTE-COLOR COMMITMENT:
        Define the Hartley Maine palette H of 8 colour anchors.
        For each pixel p = (R, G, B), find the nearest colour h* in H:
          h* = argmin_h ||p - h||_2
        Compute push weight:
          dist_norm = ||p - h*||_2 / P95(min_dist_across_image)
          push = (1 - clip(dist_norm, 0, 1)) * palette_strength
        Apply: R1 = R + (h*_R - R) * push

        NOVEL: (a) FIRST PER-PIXEL NEAREST-PALETTE-COLOR SELECTION
        USING L2 DISTANCE IN RGB SPACE.
        Prior colour commitment passes:
          -- derain_fauve_intensity_pass Stage 2: divides H (hue) into 6
             sectors and pushes toward the canonical spectral hue within
             each sector. This operates in HSV space (hue angle only) and
             every pixel in a sector is pushed toward the SAME target hue.
          -- grosz Stage 3: a SINGLE global target colour (acid green) gated
             by per-channel colour dominance mask; every "green-dominant" pixel
             gets the same push.
          -- repin Stage 2: SINGLE target warm flesh colour in midtone zone.
          -- carriere Stage 1: SINGLE sepia target (R_s = L * sepia_r);
             same target for every pixel.
        The present stage is the first to: (i) maintain a DISCRETE PALETTE
        of N specific colours; (ii) compute L2 distance from each pixel to
        ALL N palette colours; (iii) push each pixel toward its OWN nearest
        palette colour (different pixels may be pushed toward different targets);
        (iv) weight the push strength by the distance to the nearest colour
        (closer pixels pushed more, since they are "almost committed").

        Stage 2 COARSE TILE INTERIOR FLATTENING:
        Divide the canvas into n_h × n_w tiles.
        For each tile, compute mean colour (R_tile, G_tile, B_tile).
        Blur tile means with Gaussian sigma ≈ tile_height//3 to soften
        hard tile boundaries.
        Apply in interior zones (low gradient):
          interior_weight = clip(1 - G_norm, 0, 1) * flatten_strength
          R2 = R1 + (R_tile - R1) * interior_weight

        NOVEL: (b) FIRST PASS TO USE COARSE SPATIAL TILE AVERAGING AS
        THE INTERIOR MASS TARGET (vs GAUSSIAN BLUR).
        Prior interior-softening passes:
          -- grosz Stage 2: interior_mask = 1 - G_norm; blends toward
             Gaussian(R, sigma=large). The target is a spatially CONTINUOUS
             Gaussian blur, which varies smoothly across every pixel.
          -- savrasov Stage 1: Gaussian blur of entire canvas blended uniformly;
             no interior/edge gate.
          -- paint_frequency_separation_pass (s285): Gaussian(sigma=16) as
             low-frequency base for entire canvas.
        Tile averaging partitions the canvas into N × M rectangular regions,
        each with its own CONSTANT mean colour target. The boundary between
        adjacent tiles is a step function; after tile-boundary Gaussian smoothing,
        it is a soft step. The resulting target map has discrete coarse structure
        (the spatial scale of individual colour planes) rather than the
        continuously varying gradient of Gaussian blur. This matches Hartley\'s
        flat-plane construction more accurately.

        Stage 3 SYMMETRIC BILATERAL EDGE DARKENING:
        Using unsigned gradient magnitude G_norm (0=interior, 1=edge):
          edge_weight = G_norm * edge_darken_strength
          R3 = R2 + (edge_dark_r - R2) * edge_weight

        NOVEL: (c) FIRST PASS TO USE UNSIGNED G_NORM AS A SYMMETRIC
        BILATERAL EDGE OUTLINE GATE.
        Prior G_norm-gated passes:
          -- carriere Stage 3: uses G_norm as a blur weight (MORE blur
             at HIGH gradient -- completely opposite direction to sharpening).
          -- repin Stage 4: unsharp mask at G_norm > percentile threshold
             (SHARPENS at edges, does not darken them toward near-black).
          -- paint_lost_found_edges_pass: sharpens at high G_norm zones.
          -- grosz Stage 1: uses SIGNED Gx (directional component of gradient),
             not unsigned magnitude; produces a directional cast-shadow effect
             on one side of edges only.
        The present stage uses UNSIGNED G_norm (the gradient MAGNITUDE,
        not the signed directional component) to DARKEN BOTH SIDES of every
        edge toward a near-black outline colour. The result is a bilateral
        darkening: both the bright and dark sides of the edge are pulled
        toward near-black, in proportion to G_norm. This produces Hartley\'s
        characteristic painted-outline effect, which his thick dark boundary
        paint creates. It is geometrically symmetric (both sides, not one),
        and uses darkening not sharpening as the operation.

        Stage 4 LUMINANCE-ANTI-CORRELATED SATURATION:
        Compute channel deviation from grey: dev_R = R3 - mean_chan.
        DARK ZONE: L3 < dark_desat_thresh → desaturate toward grey:
          grey_weight = clip((dark_desat_thresh - L3)/dark_desat_thresh, 0, 1) * dark_desat_strength
          R_dk = R3 + grey_weight * (mean_chan - R3)
        BRIGHT ZONE: L3 > bright_sat_thresh → amplify saturation:
          bright_weight = clip((L3 - bright_sat_thresh)/(1-bright_sat_thresh), 0, 1) * bright_sat_strength
          R4 = R_dk + (R_dk - mean_chan) * bright_weight

        NOVEL: (d) FIRST PASS TO IMPLEMENT A CONTINUOUS LUMINANCE-ANTI-CORRELATED
        SATURATION CURVE: dark zones desaturated toward grey, bright zones
        amplified away from grey, in the SAME pass.
        Prior saturation-modifying passes:
          -- derain Stage 1: S^gamma (power-law saturation expansion in HSV);
             applied UNIFORMLY to all luminance levels (S channel only).
          -- carriere Stage 1: sepia tint R1 = R + (L*sepia_r - R)*strength;
             shifts all zones toward a single warm sepia target (desaturation
             toward warm monochrome, not neutral grey, and applied uniformly).
          -- paint_chromatic_shadow_shift_pass (s284): HSV hue rotation by
             zone (shadow and highlight get DIFFERENT hue shifts); operates
             on H channel (hue angle), not saturation amount.
        The present stage: (i) operates directly on the RGB deviation from
        grey (mean_channel), which is the natural RGB representation of
        saturation; (ii) applies OPPOSITE operations to dark and bright zones
        simultaneously (desaturate darks, amplify brights); (iii) creates a
        MONOTONIC ANTI-CORRELATION between luminance and saturation across
        the full tonal range. No prior pass implements this continuously
        opposing dual-zone saturation modulation.
        """
        print("    Hartley Elemental Mass pass (198th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        eps = 1e-6

        # Gradient magnitude for interior/edge gating
        L_init = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)
        gsig = 1.8
        Gx = _gf(L_init, sigma=gsig, order=[0, 1]).astype(_np.float32)
        Gy = _gf(L_init, sigma=gsig, order=[1, 0]).astype(_np.float32)
        G_mag = _np.sqrt(Gx * Gx + Gy * Gy).astype(_np.float32)
        p92 = float(_np.percentile(G_mag, 92.0))
        G_mag_norm = _np.clip(G_mag / max(p92, eps), 0.0, 1.0).astype(_np.float32)

        # ── Stage 1: Nearest-palette-colour commitment ───────────────────────────
        # Hartley Maine palette: 8 colours
        PALETTE = _np.array([
            [0.08, 0.12, 0.08],   # deep shadow green
            [0.06, 0.08, 0.18],   # blue-black granite
            [0.35, 0.22, 0.12],   # raw umber
            [0.70, 0.32, 0.14],   # burnt sienna / vermillion
            [0.09, 0.07, 0.05],   # near-black (dark mass)
            [0.78, 0.72, 0.55],   # warm cream / chalk
            [0.18, 0.28, 0.12],   # forest green
            [0.65, 0.48, 0.22],   # raw sienna / ochre
        ], dtype=_np.float32)    # (8, 3)

        flat = _np.stack([R, G, B], axis=-1).reshape(-1, 3)  # (H*W, 3)
        # L2 distance to each palette colour
        diff = flat[:, None, :] - PALETTE[None, :, :]        # (H*W, 8, 3)
        dist_sq = (diff * diff).sum(axis=-1)                  # (H*W, 8)
        nearest_idx = dist_sq.argmin(axis=-1)                 # (H*W,)
        nearest_dist = _np.sqrt(dist_sq.min(axis=-1))         # (H*W,)

        # Normalize distance for push weighting
        d_p95 = max(float(_np.percentile(nearest_dist, 95.0)), eps)
        dist_norm = _np.clip(nearest_dist / d_p95, 0.0, 1.0).astype(_np.float32)
        push_w = ((1.0 - dist_norm) * float(palette_strength)).astype(_np.float32)

        nearest_colours = PALETTE[nearest_idx]               # (H*W, 3)
        nearest_R = nearest_colours[:, 0].reshape(H_, W_).astype(_np.float32)
        nearest_G = nearest_colours[:, 1].reshape(H_, W_).astype(_np.float32)
        nearest_B = nearest_colours[:, 2].reshape(H_, W_).astype(_np.float32)
        push_2d   = push_w.reshape(H_, W_).astype(_np.float32)

        R1 = _np.clip(R + (nearest_R - R) * push_2d, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (nearest_G - G) * push_2d, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (nearest_B - B) * push_2d, 0.0, 1.0).astype(_np.float32)

        palette_pushed = int((push_2d > 0.10).sum())

        # ── Stage 2: Coarse tile interior flattening ─────────────────────────────
        n_ty = max(int(interior_tile_n_h), 4)
        n_tx = max(int(interior_tile_n_w), 4)
        ty_sz = max(H_ // n_ty, 4)
        tx_sz = max(W_ // n_tx, 4)

        R_tile_map = _np.zeros((H_, W_), dtype=_np.float32)
        G_tile_map = _np.zeros((H_, W_), dtype=_np.float32)
        B_tile_map = _np.zeros((H_, W_), dtype=_np.float32)

        for ity in range(n_ty + 1):
            y0t = ity * ty_sz
            y1t = min(y0t + ty_sz, H_)
            if y0t >= H_:
                break
            for itx in range(n_tx + 1):
                x0t = itx * tx_sz
                x1t = min(x0t + tx_sz, W_)
                if x0t >= W_:
                    break
                R_tile_map[y0t:y1t, x0t:x1t] = float(R1[y0t:y1t, x0t:x1t].mean())
                G_tile_map[y0t:y1t, x0t:x1t] = float(G1[y0t:y1t, x0t:x1t].mean())
                B_tile_map[y0t:y1t, x0t:x1t] = float(B1[y0t:y1t, x0t:x1t].mean())

        sigma_tile = float(max(ty_sz // 3, 2))
        R_tile_map = _gf(R_tile_map, sigma=sigma_tile).astype(_np.float32)
        G_tile_map = _gf(G_tile_map, sigma=sigma_tile).astype(_np.float32)
        B_tile_map = _gf(B_tile_map, sigma=sigma_tile).astype(_np.float32)

        interior_w = _np.clip(1.0 - G_mag_norm, 0.0, 1.0).astype(_np.float32) * float(interior_flatten_strength)
        R2 = _np.clip(R1 + (R_tile_map - R1) * interior_w, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (G_tile_map - G1) * interior_w, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (B_tile_map - B1) * interior_w, 0.0, 1.0).astype(_np.float32)

        flattened_px = int((interior_w > 0.10).sum())

        # ── Stage 3: Symmetric bilateral edge darkening ──────────────────────────
        eds = float(edge_darken_strength)
        edr = float(edge_dark_r)
        edg = float(edge_dark_g)
        edb = float(edge_dark_b)
        edge_w = (G_mag_norm * eds).astype(_np.float32)
        R3 = _np.clip(R2 + (edr - R2) * edge_w, 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G2 + (edg - G2) * edge_w, 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B2 + (edb - B2) * edge_w, 0.0, 1.0).astype(_np.float32)

        edge_px = int((edge_w > 0.15).sum())

        # ── Stage 4: Luminance-anti-correlated saturation ────────────────────────
        L3 = (0.299 * R3 + 0.587 * G3 + 0.114 * B3).astype(_np.float32)
        mean_chan = ((R3 + G3 + B3) / 3.0).astype(_np.float32)

        # Dark zone: desaturate toward grey
        ddt = float(dark_desat_thresh)
        dds = float(dark_desat_strength)
        grey_w = _np.clip((ddt - L3) / max(ddt, eps), 0.0, 1.0).astype(_np.float32) * dds
        R_dk = _np.clip(R3 + grey_w * (mean_chan - R3), 0.0, 1.0).astype(_np.float32)
        G_dk = _np.clip(G3 + grey_w * (mean_chan - G3), 0.0, 1.0).astype(_np.float32)
        B_dk = _np.clip(B3 + grey_w * (mean_chan - B3), 0.0, 1.0).astype(_np.float32)

        # Bright zone: amplify saturation (push away from grey)
        bst = float(bright_sat_thresh)
        bss = float(bright_sat_strength)
        denom_bright = max(1.0 - bst, eps)
        bright_w = _np.clip((L3 - bst) / denom_bright, 0.0, 1.0).astype(_np.float32) * bss
        mean_chan_dk = ((R_dk + G_dk + B_dk) / 3.0).astype(_np.float32)
        R4 = _np.clip(R_dk + (R_dk - mean_chan_dk) * bright_w, 0.0, 1.0).astype(_np.float32)
        G4 = _np.clip(G_dk + (G_dk - mean_chan_dk) * bright_w, 0.0, 1.0).astype(_np.float32)
        B4 = _np.clip(B_dk + (B_dk - mean_chan_dk) * bright_w, 0.0, 1.0).astype(_np.float32)

        dark_desat_px = int((grey_w > 0.10).sum())
        bright_sat_px = int((bright_w > 0.10).sum())

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

        print(f"    Hartley Elemental Mass complete "
              f"(palette_pushed={palette_pushed}, flattened={flattened_px}, "
              f"edge_px={edge_px}, dark_desat={dark_desat_px}, bright_sat={bright_sat_px})")

'''

# ── Append both passes to stroke_engine.py ───────────────────────────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8-sig") as f:
    src = f.read()

assert "paint_median_clarity_pass" not in src, \
    "paint_median_clarity_pass already exists in stroke_engine.py"
assert "hartley_elemental_mass_pass" not in src, \
    "hartley_elemental_mass_pass already exists in stroke_engine.py"

with open(SE_PATH, "a", encoding="utf-8") as f:
    f.write(MEDIAN_CLARITY_PASS)
    f.write(HARTLEY_ELEMENTAL_MASS_PASS)

print("stroke_engine.py patched: paint_median_clarity_pass (s287 improvement)"
      " + hartley_elemental_mass_pass (198th mode) appended.")
