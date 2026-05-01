"""Insert paint_focal_vignette_pass (s278 improvement) and
toorop_symbolist_line_pass (189th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_focal_vignette_pass (s278 improvement) ─────────────────────

FOCAL_VIGNETTE_PASS = '''
    def paint_focal_vignette_pass(
        self,
        vignette_strength:   float = 0.52,
        edge_color_cool:     float = 0.05,
        center_color_warm:   float = 0.04,
        focal_percentile:    float = 82.0,
        falloff_exponent:    float = 1.8,
        opacity:             float = 1.0,
    ) -> None:
        r"""Focal Vignette -- session 278 improvement.

        PAINTERLY FOCAL EMPHASIS THROUGH AUTO-DETECTED LUMINANCE CENTER,
        RADIAL DARKENING, AND TEMPERATURE GRADIENT:

        Academic painters from the Baroque through the Impressionists used
        tonal and color vignetting as a compositional tool: darkening the
        periphery to drive the eye inward, and warming the focal zone while
        cooling the edges to reinforce the spatial hierarchy through color
        temperature. Velazquez darkened the corners of Las Meninas to prevent
        visual leakage beyond the figures. Rembrandt's portraits exist on near-
        black grounds with every stroke of highlight directed toward the face.
        Turner's seascapes glow at the horizon center while the fore and sky
        edges cool to grey. This pass formalizes that academic convention:
        detect the painting's natural focal center, darken the radial periphery,
        and apply a warm/cool temperature gradient that reinforces spatial depth.

        Stage 1 AUTO-DETECTION OF FOCAL CENTER FROM LUMINANCE:
        Compute luminance L. Build a weight map W = max(L - threshold, 0)^2
        where threshold = percentile(L, focal_percentile). This creates a
        sparse map of the brightest highlights. Compute the weighted centroid:
          cx = sum(x * W) / sum(W), cy = sum(y * W) / sum(W)
        This is the detected focal center -- the luminance-weighted center of
        mass of the brightest zone. For a painting with a single bright
        highlight (moonlit rock, window, face), cx/cy will land on that zone.
        For a diffuse bright sky, it will land near the center of the bright
        zone. Either way it is semantically meaningful and content-adaptive.
        NOVEL: (a) AUTO-DETECTED FOCAL CENTER VIA LUMINANCE-WEIGHTED CENTROID
        -- all prior Painter passes that apply radial effects use fixed centers
        (image center, or fixed xy). This pass locates the center by
        computing the weighted centroid of the top-k% brightest pixels. No
        prior pass uses luminance-weighted centroid for spatial targeting.

        Stage 2 RADIAL DARKENING (VIGNETTE):
        For each pixel (x, y), compute normalized distance from detected center:
          d = sqrt((x - cx)^2 + (y - cy)^2) / d_max
        where d_max = max diagonal distance from center to image corner.
        Apply power-law falloff: t = min(d^falloff_exponent, 1.0).
        Scale luminance: L_vign = 1.0 - t * vignette_strength.
        Apply as multiplicative scaling to preserve hue:
          R_v = R * L_vign, G_v = G * L_vign, B_v = B * L_vign
        NOVEL: (b) POWER-LAW RADIAL FALLOFF FROM CONTENT-DETECTED CENTER --
        the power-law exponent (falloff_exponent, default 1.8) creates a
        faster-than-linear roll-off near the focal center but a slow
        accumulation at intermediate distances -- matching how painters
        physically apply edge darkening (abrupt near edges, gradual in mid
        range). Prior passes use Gaussian or linear falloffs.

        Stage 3 TEMPERATURE GRADIENT (CENTER WARM / EDGE COOL):
        Simultaneously with the vignette, apply a color temperature shift:
          (i) CENTER WARMTH: blend R += center_color_warm * (1-t), B -= center_color_warm * (1-t)
          Warms the focal center: slight amber/orange shift in the brightest zone.
          (ii) EDGE COOLING: blend B += edge_color_cool * t, R -= edge_color_cool * t
          Cools the periphery: slight blue/grey shift at the far edges.
        Both effects use the same radial falloff t, so they transition smoothly.
        NOVEL: (c) COMBINED WARM-CENTER / COOL-EDGE TEMPERATURE GRADIENT using
        shared radial weight -- prior temperature/hue passes apply uniform
        color shifts to zones defined by luminance thresholds
        (complementary_shadow, umber trace). This pass applies a spatially
        varying warm-cool temperature gradient keyed to the RADIAL DISTANCE
        from the detected focal center -- orthogonal to any luminance-based
        zoning and the first pass to combine spatial and tonal targeting.
        """
        print("    Focal Vignette pass (session 278 improvement)...")

        import numpy as _np

        canvas = self.canvas
        H, W = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)

        # Stage 1: detect focal center via luminance-weighted centroid
        thresh = float(_np.percentile(L, float(focal_percentile)))
        W_map = _np.maximum(L - thresh, 0.0).astype(_np.float32) ** 2
        w_sum = float(W_map.sum()) + 1e-9

        ys, xs = _np.mgrid[0:H, 0:W]
        cx = float((xs * W_map).sum() / w_sum)
        cy = float((ys * W_map).sum() / w_sum)

        # Stage 2: radial darkening vignette
        dx = (xs - cx).astype(_np.float32)
        dy = (ys - cy).astype(_np.float32)
        dist = _np.sqrt(dx * dx + dy * dy)
        corners = [
            _np.sqrt(cx ** 2 + cy ** 2),
            _np.sqrt((W - cx) ** 2 + cy ** 2),
            _np.sqrt(cx ** 2 + (H - cy) ** 2),
            _np.sqrt((W - cx) ** 2 + (H - cy) ** 2),
        ]
        d_max = max(corners) + 1e-6
        d_norm = (dist / d_max).astype(_np.float32)
        fe = max(float(falloff_exponent), 0.5)
        t = _np.minimum(d_norm ** fe, 1.0).astype(_np.float32)

        vs = float(vignette_strength)
        lum_scale = _np.clip(1.0 - t * vs, 0.0, 1.0).astype(_np.float32)

        R_v = _np.clip(R * lum_scale, 0.0, 1.0).astype(_np.float32)
        G_v = _np.clip(G * lum_scale, 0.0, 1.0).astype(_np.float32)
        B_v = _np.clip(B * lum_scale, 0.0, 1.0).astype(_np.float32)

        # Stage 3: temperature gradient (warm center, cool edges)
        cw = float(center_color_warm)
        ec = float(edge_color_cool)
        # Warm center: add red/amber, reduce blue at focal zone (1-t)
        R_v = _np.clip(R_v + cw * (1.0 - t), 0.0, 1.0).astype(_np.float32)
        B_v = _np.clip(B_v - cw * 0.5 * (1.0 - t), 0.0, 1.0).astype(_np.float32)
        # Cool edges: add blue, reduce red at periphery (t)
        B_v = _np.clip(B_v + ec * t, 0.0, 1.0).astype(_np.float32)
        R_v = _np.clip(R_v - ec * 0.5 * t, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R_v - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G_v - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B_v - B) * op, 0.0, 1.0).astype(_np.float32)

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Focal Vignette complete (focal_center=({cx:.1f},{cy:.1f}), "
              f"vignette={vs:.2f})")

'''

# ── Pass 2: toorop_symbolist_line_pass (189th mode) ──────────────────────────

TOOROP_SYMBOLIST_LINE_PASS = '''
    def toorop_symbolist_line_pass(
        self,
        n_zones:           int   = 4,
        zone_strength:     float = 0.36,
        edge_threshold:    float = 0.04,
        line_darkness:     float = 0.55,
        line_length:       int   = 6,
        hatch_period:      float = 6.0,
        hatch_width:       float = 1.2,
        hatch_angle_deg:   float = 38.0,
        hatch_strength:    float = 0.14,
        hatch_grad_limit:  float = 0.025,
        warm_ink_r:        float = 0.28,
        warm_ink_g:        float = 0.18,
        warm_ink_b:        float = 0.08,
        warm_ink_opacity:  float = 0.22,
        opacity:           float = 0.88,
    ) -> None:
        r"""Toorop Symbolist Line (Art Nouveau / Dutch Symbolism) -- 189th mode.

        JAN TOOROP (1858-1928) -- DUTCH SYMBOLIST AND ART NOUVEAU MASTER,
        BORN IN JAVA, PAINTER OF INTRICATE FLOWING LINEAR WORLDS:

        Jan Toorop was born in Purworedjo, Java, then part of the Dutch East
        Indies, and grew up in the Netherlands, studying at the Amsterdam
        Rijksacademie and the Brussels Academie Royale. His early work belongs
        to the Belgian Symbolist circle that included Fernand Khnopff and Jan
        Delville, but his mature style is entirely distinctive: an extraordinarily
        intricate, flowing network of thin dark lines overlaid on flat tonal
        planes, influenced simultaneously by Japanese woodblock prints, Javanese
        wayang kulit shadow puppet theater (with their extreme elongation and
        flatness), English Pre-Raphaelitism (which he absorbed during time in
        London), and continental Symbolism. His masterpiece THE THREE BRIDES
        (1893, Kroller-Muller Museum) -- a life-size drawing on brown paper,
        three meters wide -- is among the most densely realized images in
        Western art: a web of hundreds of flowing hair-lines, elongated figures,
        architectural elements, and symbolic motifs, all interlocked in a single
        breathing linear field.

        TOOROP\'S TECHNICAL SIGNATURE -- THE FLOWING LINE NETWORK:
        The central feature of Toorop\'s mature style is a multi-scale line
        structure that operates simultaneously at three levels: (1) BOLD CONTOUR
        LINES that define the edges of flat tonal zones -- thick, smooth curves
        that separate dark from light; (2) INTERMEDIATE FLOW LINES that follow
        the surface of each tonal zone, tracing its curvature and modeling its
        form without using shading; (3) FINE FILAMENT HATCHING inside flat areas
        that appears almost incidental -- a faint, nervous energy underneath the
        dominant flow lines. All three levels are DARK LINES ON LIGHT OR MIDTONE
        GROUND -- Toorop rarely uses white-line techniques. The lines in flat
        shadow zones are invisible (shadow absorbs them); they emerge in midtone
        and light zones, where the flat tonal ground provides the contrast they
        need.

        JAPANESE PRINT INFLUENCE -- FLAT TONAL PLANES:
        Toorop\'s Japanese influence (his teacher Charles van der Stappen was a
        major Japonisme figure, and Toorop himself collected prints) manifests
        as a tendency toward FLAT TONAL SIMPLIFICATION: rather than smooth
        academic gradations, he worked in 3-4 broadly defined tonal zones with
        clear boundaries, each zone internally flat or very nearly so. The
        flowing line network is then drawn over these flat planes. This flat-
        zone + linear structure combination is the direct inheritance of ukiyo-e
        woodblock technique, in which key blocks (keyblocks) print the line
        structure and color blocks print flat tonal fields.

        WAYANG KULIT INFLUENCE -- ELONGATION AND DENSITY:
        The Javanese shadow puppet theater of his childhood contributed a quality
        of DENSE SYMBOLIC DECORATION within flat areas: the shadow puppets\' flat
        bodies are covered with intricate incised ornament -- scrollwork, flower
        patterns, geometric hatching -- that fills every available surface without
        modeling form. Toorop translates this into his painting as fine decorative
        hatching in flat zones, particularly evident in background areas and
        costume details of his figure compositions.

        Stage 1 ART NOUVEAU TONAL SIMPLIFICATION (Flat Zone Creation):
        Compute luminance L. Define n_zones equally spaced tonal levels between
        0 and 1: level_k = (k + 0.5) / n_zones for k = 0 ... n_zones-1.
        For each pixel, assign it to the nearest level. Blend each channel
        toward its assigned level:
          R_z = R + (level * R/L - R) * zone_strength (preserves hue)
          Equivalent to: R_z = R * (1 - zone_strength) + R * (level/L) * zone_strength
        This pulls each pixel toward the nearest flat tonal level while
        preserving hue (by scaling all channels by the same luminance ratio).
        NOVEL: (a) HUE-PRESERVING TONAL POSTERIZATION via LUMINANCE RATIO
        BLENDING -- prior tonal modification passes (goya sigmoid, levitan warmth
        diffusion) modify luminance or hue by pixel-class. This pass applies a
        NEAREST-LEVEL SNAP to luminance while preserving hue by computing
        the correction as a SCALE FACTOR L_target/(L+eps) applied uniformly to
        all channels. The result is flat zones that retain their original color
        character rather than converting to a fixed palette color.

        Stage 2 ISO-CONTOUR LINE THREADING:
        Compute Sobel gradient magnitude Gmag and direction theta for the
        tonal-simplified luminance L_z. For each pixel where Gmag > edge_threshold:
          - Compute contour direction: phi = theta + pi/2 (perpendicular to gradient)
          - Draw a dark line segment of length line_length in direction phi:
            for step in range(-line_length//2, line_length//2):
              nx = x + round(step * cos(phi))
              ny = y + round(step * sin(phi))
              if valid: darken pixel[ny, nx] by line_darkness
        This creates a web of thin dark lines that follow the iso-luminance
        contours -- the contour line network characteristic of Toorop\'s style.
        NOVEL: (b) ISO-CONTOUR LINE THREADING VIA GRADIENT-PERPENDICULAR
        ORIENTED SEGMENTS -- prior edge-related passes (Khnopff, Zurbaran,
        weyden) detect edges and modify edge pixels in place. This pass uses
        the gradient DIRECTION to orient SHORT LINE SEGMENTS PERPENDICULAR
        TO THE GRADIENT (i.e. along iso-luminance contours) and renders them
        as dark marks independent of the pixel\'s luminance. The result is a
        network of flowing contour lines rather than edge brightening or
        edge darkening along gradient direction. This is the first pass to
        extract and render iso-contour direction as an explicit linear element.

        Stage 3 FLAT ZONE DECORATIVE HATCHING (Wayang Kulit Ornament):
        For pixels where Gmag_z < hatch_grad_limit (flat zones only):
          Compute a periodic stripe value at a fixed decorative angle:
            stripe = (x * cos(hatch_angle) + y * sin(hatch_angle)) % hatch_period
          If stripe < hatch_width: apply darkening of hatch_strength to all channels.
        This creates a fine diagonal hatching in flat tonal areas -- the
        decorative interior patterning of Toorop\'s flat zones.
        NOVEL: (c) CONTENT-ADAPTIVE FLAT-ZONE HATCHING GATED BY GRADIENT
        MAGNITUDE -- prior hatching passes apply uniform global hatching (none
        exist in this codebase). This pass applies hatching ONLY in zones where
        gradient magnitude falls below a threshold (flat/interior zones), leaving
        edge and transition zones unhatched. The result is that hatching appears
        inside the flat tonal areas and disappears at contour edges -- the exact
        distribution of decorative ornament in Toorop\'s mature work.

        Stage 4 WARM INK LINE BURNISHING:
        In transition zones (Gmag_z between edge_threshold and 3*edge_threshold),
        blend a warm ink color (sepia/umber) into each channel:
          R_w = R + (warm_ink_r - R) * warm_ink_opacity * transition_weight
        where transition_weight = Gnorm * warm_ink_opacity for pixels in zone.
        This burnishes the contour lines with Toorop\'s characteristic warm
        ink tone (he worked primarily in black chalk and Indian ink on warm
        ground paper -- the ink has a warm sepia quality when thin, cold black
        only when dense). By tinting the transition zone with warm sepia at low
        opacity, the line network acquires the warm ink register of the
        originals.
        """
        print("    Toorop Symbolist Line pass (189th mode)...")

        import numpy as _np
        from scipy.ndimage import sobel as _sobel

        canvas = self.canvas
        H, W = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)

        # Stage 1: Hue-preserving tonal posterization
        nz = max(int(n_zones), 2)
        zs = float(zone_strength)
        # Quantize luminance to n_zones levels
        L_q = (_np.floor(L * nz) + 0.5) / nz
        L_q = _np.clip(L_q, 0.0, 1.0).astype(_np.float32)
        ratio = (L_q / (L + 1e-6)).astype(_np.float32)
        R1 = _np.clip(R + (R * ratio - R) * zs, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (G * ratio - G) * zs, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (B * ratio - B) * zs, 0.0, 1.0).astype(_np.float32)

        # Stage 2: ISO-contour line threading
        L_z = (0.299 * R1 + 0.587 * G1 + 0.114 * B1).astype(_np.float32)
        Gx = _sobel(L_z.astype(_np.float64), axis=1).astype(_np.float32)
        Gy = _sobel(L_z.astype(_np.float64), axis=0).astype(_np.float32)
        Gmag = _np.sqrt(Gx * Gx + Gy * Gy).astype(_np.float32)
        # Contour angle: perpendicular to gradient
        theta = _np.arctan2(Gy, Gx).astype(_np.float32)
        phi = theta + (_np.float32(_np.pi / 2.0))

        et = float(edge_threshold)
        ld = float(line_darkness)
        ll = max(int(line_length), 2)
        half = ll // 2
        cos_phi = _np.cos(phi).astype(_np.float32)
        sin_phi = _np.sin(phi).astype(_np.float32)

        edge_mask = (Gmag > et)
        ys_arr, xs_arr = _np.where(edge_mask)

        R2 = R1.copy()
        G2 = G1.copy()
        B2 = B1.copy()

        for step in range(-half, half + 1):
            nx = (xs_arr + (step * cos_phi[ys_arr, xs_arr]).round().astype(int)
                  ).clip(0, W - 1)
            ny = (ys_arr + (step * sin_phi[ys_arr, xs_arr]).round().astype(int)
                  ).clip(0, H - 1)
            R2[ny, nx] = _np.clip(R2[ny, nx] * (1.0 - ld * 0.5), 0.0, 1.0)
            G2[ny, nx] = _np.clip(G2[ny, nx] * (1.0 - ld * 0.5), 0.0, 1.0)
            B2[ny, nx] = _np.clip(B2[ny, nx] * (1.0 - ld * 0.55), 0.0, 1.0)

        # Stage 3: Flat zone decorative hatching
        ys_g, xs_g = _np.mgrid[0:H, 0:W]
        ha = float(hatch_angle_deg) * _np.pi / 180.0
        hp = float(hatch_period)
        hw = float(hatch_width)
        hs = float(hatch_strength)
        hgl = float(hatch_grad_limit)

        flat_mask = (Gmag < hgl)
        stripe_val = (xs_g * _np.cos(ha) + ys_g * _np.sin(ha)) % hp
        hatch_hit = (stripe_val < hw) & flat_mask
        hf = hatch_hit.astype(_np.float32)
        R2 = _np.clip(R2 - hs * hf, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G2 - hs * hf, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B2 - hs * 0.85 * hf, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Warm ink burnishing in transition zones
        g99 = float(_np.percentile(Gmag, 99)) + 1e-6
        Gnorm = (Gmag / g99).astype(_np.float32)
        et3 = et * 3.0
        trans_w = _np.clip((Gnorm - et / g99) / (et3 / g99 - et / g99 + 1e-6), 0.0, 1.0
                           ).astype(_np.float32)
        wio = float(warm_ink_opacity)
        wi_r = float(warm_ink_r)
        wi_g = float(warm_ink_g)
        wi_b = float(warm_ink_b)
        w_field = (trans_w * wio).astype(_np.float32)
        R3 = _np.clip(R2 + (wi_r - R2) * w_field, 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G2 + (wi_g - G2) * w_field, 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B2 + (wi_b - B2) * w_field, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R3 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G3 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B3 - B) * op, 0.0, 1.0).astype(_np.float32)

        n_edge = int(edge_mask.sum())
        n_hatch = int(hatch_hit.sum())
        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Toorop Symbolist Line complete "
              f"(n_edge={n_edge}, n_hatch={n_hatch})")

'''

# ── Inject both passes into stroke_engine.py ─────────────────────────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

ANCHOR = "    def goya_black_vision_pass("
assert ANCHOR in src, f"Anchor not found in stroke_engine.py: {ANCHOR!r}"

INSERTION = FOCAL_VIGNETTE_PASS + TOOROP_SYMBOLIST_LINE_PASS
new_src = src.replace(ANCHOR, INSERTION + ANCHOR, 1)

with open(SE_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("stroke_engine.py patched: paint_focal_vignette_pass (s278 improvement)"
      " + toorop_symbolist_line_pass (189th mode) inserted before goya_black_vision_pass.")
