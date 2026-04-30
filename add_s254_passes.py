"""Insert rego_flat_figure_pass and paint_contour_weight_pass into
stroke_engine.py (session 254).

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

FLAT_FIGURE_PASS = """
    def rego_flat_figure_pass(
        self,
        n_levels:         int   = 6,
        zone_blend:       float = 0.72,
        contour_threshold: float = 0.08,
        contour_strength: float = 0.58,
        contour_px:       int   = 2,
        outline_tone:     tuple = (0.16, 0.10, 0.08),
        tension_warm:     tuple = (0.72, 0.52, 0.32),
        tension_cool:     tuple = (0.44, 0.52, 0.66),
        tension_strength: float = 0.12,
        opacity:          float = 0.85,
        seed:             int   = 254,
    ) -> None:
        r\"\"\"Paula Rego Flat Figure -- session 254, 165th distinct painting mode.

        THREE-STAGE FLAT FIGURE POSTERISATION WITH CONTOUR WEIGHT:

        Stage 1 TONAL ZONE POSTERISATION: Quantise the canvas RGB colours into
        n_levels discrete tonal steps per channel using uniform quantisation:
        q = round(v * (n_levels - 1)) / (n_levels - 1). This produces the
        flat, posterised zones of colour characteristic of Rego's pastel work
        -- large areas of a single unmodulated tone. Then apply local zone-mean
        smoothing: for each quantised level, identify all pixels in that zone
        and replace each pixel with a blend of its original value and the zone
        mean colour at zone_blend fraction. This softens the hard digital
        posterisation toward the organic flatness of hand-applied pastel.
        NOVEL: (a) ZONE-MEAN-SMOOTHED POSTERISATION FOR FIGURATIVE FLATNESS --
        first pass to combine per-channel uniform quantisation with per-zone
        local mean blending as a two-step figurative colour flattening; the
        existing paint_posterize or split_toning passes apply global tone
        operations; no prior pass performs quantised zone identification
        followed by zone-mean colour replacement weighted by zone_blend.

        Stage 2 WARM CONTOUR OUTLINING: Compute the luminance image of the
        Stage 1 result. Apply finite-difference gradient magnitude to find
        edges. Pixels with gradient magnitude > contour_threshold are
        edge pixels. Dilate the edge mask by contour_px pixels (expand the
        contour band outward). Blend each edge pixel toward outline_tone at
        contour_strength. outline_tone is a warm dark (near-black brown) that
        gives Rego's figures their characteristic heavy, slightly warm boundary.
        NOVEL: (b) WARM-TONED DARKENING OF FIGURE CONTOURS WITH DILATION --
        first pass to apply warm-toned dark blending specifically at dilated
        gradient-edge pixels as a figurative contour simulation; distinct from
        paint_contour_weight_pass (s254 improvement, below) which applies
        variable-weight thickness scaling; no prior artist pass applies a
        warm-shifted dark tone to dilated edge pixels for contour darkening.

        Stage 3 CHROMATIC ZONE TENSION: Divide the canvas into four spatial
        quadrants. Assign each quadrant a role alternating figure/ground:
        upper-left=ground, upper-right=figure, lower-left=figure,
        lower-right=ground (Rego's typical compositional diagonal). Apply a
        slight warm push (blend tension_strength toward tension_warm) to
        figure-quadrant pixels, and a slight cool push (blend tension_strength
        toward tension_cool) to ground-quadrant pixels. This creates the
        specific warm-figure / cool-ground chromatic tension of Rego's
        compositions without global colour shifting.
        NOVEL: (c) QUADRANT-INDEXED WARM/COOL CHROMATIC TENSION AS SPATIAL
        FIGURE-GROUND SEPARATION -- first pass to apply alternating warm/cool
        chromatic pushes indexed by spatial quadrant position as a figurative
        composition technique; paint_warm_cool_separation_pass (s251) applies
        a global luminance-threshold warm/cool split; no prior pass assigns
        warm/cool roles by spatial quadrant index as a compositional device.

        n_levels          : Number of discrete tonal levels per channel.
        zone_blend        : Blend fraction toward zone mean colour (flatness).
        contour_threshold : Gradient magnitude threshold for contour detection.
        contour_strength  : Blend fraction toward outline_tone at contours.
        contour_px        : Dilation radius for contour band in pixels.
        outline_tone      : Warm dark RGB for contour darkening.
        tension_warm      : RGB target for figure-zone chromatic warmth.
        tension_cool      : RGB target for ground-zone chromatic coolness.
        tension_strength  : Blend fraction for warm/cool zone tension.
        opacity           : Final composite opacity.
        seed              : RNG seed (reserved for future stochastic stages).
        \"\"\"
        import numpy as _np

        print("    Rego Flat Figure pass (session 254, 165th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        # Working in float32 [0,1] -- cairo BGRA order
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0

        # ── Stage 1: Tonal zone posterisation with zone-mean smoothing ─────
        nl = float(n_levels - 1) if n_levels > 1 else 1.0

        # Per-channel quantisation
        r_q = _np.round(r0 * nl) / nl
        g_q = _np.round(g0 * nl) / nl
        b_q = _np.round(b0 * nl) / nl

        # Zone-mean smoothing: for each quantised level, average original
        # colours of all pixels in that level and blend toward the mean
        r1 = r_q.copy()
        g1 = g_q.copy()
        b1 = b_q.copy()

        for li in range(int(n_levels)):
            lv = float(li) / nl
            # Tolerance window for level membership
            tol = 0.5 / nl + 1e-6
            mask = (_np.abs(r_q - lv) < tol) | (_np.abs(g_q - lv) < tol) | \
                   (_np.abs(b_q - lv) < tol)
            if mask.sum() == 0:
                continue
            # Zone mean of original colours
            mr = float(r0[mask].mean())
            mg = float(g0[mask].mean())
            mb = float(b0[mask].mean())
            zb = float(zone_blend)
            r1[mask] = r_q[mask] * (1.0 - zb) + mr * zb
            g1[mask] = g_q[mask] * (1.0 - zb) + mg * zb
            b1[mask] = b_q[mask] * (1.0 - zb) + mb * zb

        # ── Stage 2: Warm contour outlining ───────────────────────────────
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1)

        # Gradient magnitude
        gx = _np.zeros_like(lum1)
        gx[:, 1:-1] = lum1[:, 2:] - lum1[:, :-2]
        gx[:, 0] = lum1[:, 1] - lum1[:, 0]
        gx[:, -1] = lum1[:, -1] - lum1[:, -2]
        gy = _np.zeros_like(lum1)
        gy[1:-1, :] = lum1[2:, :] - lum1[:-2, :]
        gy[0, :] = lum1[1, :] - lum1[0, :]
        gy[-1, :] = lum1[-1, :] - lum1[-2, :]
        grad = _np.sqrt(gx ** 2 + gy ** 2).astype(_np.float32)

        edge_mask = (grad > float(contour_threshold)).astype(_np.float32)

        # Dilate edge mask by contour_px pixels using max-pooling
        if int(contour_px) > 0:
            from scipy.ndimage import maximum_filter as _maxf
            size = 2 * int(contour_px) + 1
            edge_mask = _maxf(edge_mask, size=size).astype(_np.float32)

        ot_r, ot_g, ot_b = float(outline_tone[0]), float(outline_tone[1]), float(outline_tone[2])
        cs = float(contour_strength)

        r2 = r1 * (1.0 - edge_mask * cs) + ot_r * (edge_mask * cs)
        g2 = g1 * (1.0 - edge_mask * cs) + ot_g * (edge_mask * cs)
        b2 = b1 * (1.0 - edge_mask * cs) + ot_b * (edge_mask * cs)

        # ── Stage 3: Chromatic zone tension ───────────────────────────────
        # Quadrant map: figure=(upper-right, lower-left), ground=(upper-left, lower-right)
        cy, cx = h // 2, w // 2
        figure_mask = _np.zeros((h, w), dtype=_np.float32)
        figure_mask[:cy, cx:] = 1.0   # upper-right = figure
        figure_mask[cy:, :cx] = 1.0   # lower-left  = figure
        ground_mask = 1.0 - figure_mask

        tw_r, tw_g, tw_b = float(tension_warm[0]), float(tension_warm[1]), float(tension_warm[2])
        tc_r, tc_g, tc_b = float(tension_cool[0]), float(tension_cool[1]), float(tension_cool[2])
        ts = float(tension_strength)

        # Warm push on figure zones
        r3 = r2 + figure_mask * ts * (tw_r - r2)
        g3 = g2 + figure_mask * ts * (tw_g - g2)
        b3 = b2 + figure_mask * ts * (tw_b - b2)
        # Cool push on ground zones
        r3 = r3 + ground_mask * ts * (tc_r - r3)
        g3 = g3 + ground_mask * ts * (tc_g - g3)
        b3 = b3 + ground_mask * ts * (tc_b - b3)

        r3 = _np.clip(r3, 0.0, 1.0)
        g3 = _np.clip(g3, 0.0, 1.0)
        b3 = _np.clip(b3, 0.0, 1.0)

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
        contour_px_count = int((edge_mask > 0.5).sum())
        print(f"    Rego Flat Figure complete (contour_pixels={contour_px_count})")
"""

CONTOUR_WEIGHT_PASS = """
    def paint_contour_weight_pass(
        self,
        contour_threshold: float = 0.06,
        max_weight:       float = 0.55,
        weight_exponent:  float = 1.4,
        outline_tone:     tuple = (0.12, 0.08, 0.06),
        junction_boost:   float = 0.22,
        taper_strength:   float = 0.38,
        opacity:          float = 0.72,
    ) -> None:
        r\"\"\"Variable-Weight Contour Drawing -- session 254 improvement pass.

        THREE-STAGE CONTOUR WEIGHTING INSPIRED BY FIGURATIVE DRAWING:

        Simulates the variable-weight contour line used by figurative draughts-
        persons: lines are heaviest at junctions and corners (where directions
        change most), and taper toward their ends. Applies the contour to the
        existing painted surface as a darkening layer.

        Stage 1 EDGE GRADIENT FIELD: Compute the luminance image. Apply
        finite-difference horizontal (Gx) and vertical (Gy) gradients. Compute
        gradient magnitude M = sqrt(Gx^2 + Gy^2) and gradient direction
        theta = atan2(Gy, Gx). Threshold M at contour_threshold to produce
        a binary edge map. Scale the sub-threshold edge values to [0, 1]
        representing local edge strength.
        NOVEL: (a) GRADIENT FIELD WITH DIRECTION MAP FOR VARIABLE-WEIGHT
        CONTOUR -- first pass to compute both magnitude AND direction of the
        gradient field simultaneously, retaining both for use in junction
        detection and taper computation; paint_lost_found_edges_pass modifies
        edge softness from a magnitude image only; no prior pass retains the
        gradient direction to inform the weight at each contour pixel.

        Stage 2 JUNCTION DETECTION AND WEIGHT BOOST: For each edge pixel,
        compute the local variation in gradient direction over a 3x3 window
        (angular variance). High angular variance indicates a corner or
        junction (where multiple edges meet). Apply a junction_boost additive
        to the edge weight at these high-variance pixels, clamped to 1.0.
        This gives the characteristic heaviness at corners and junctions of
        a skilled draughtsman's contour line.
        NOVEL: (b) ANGULAR VARIANCE JUNCTION DETECTION FOR CONTOUR WEIGHTING
        -- first pass to compute local angular variance of gradient direction
        as a junction/corner detector, and to use the resulting junction map
        additively on the contour weight; no prior pass uses gradient direction
        angular variance to detect corners for the purpose of modulating
        contour darkness.

        Stage 3 TAPER TOWARD ENDPOINTS AND DARKENING APPLICATION: Apply the
        final contour weight as a power-law scaling: final_weight = edge_weight
        ^ weight_exponent * max_weight. Blend each edge pixel toward
        outline_tone at final_weight (multiplicative darkening plus warm tone
        shift). taper_strength reduces the contour weight at pixels with
        low local edge connectivity (isolated edge pixels = endpoints): compute
        the number of edge neighbours in a 3x3 window; pixels with fewer than
        2 neighbours are endpoints and receive weight multiplied by
        (1 - taper_strength). This produces tapered stroke ends.
        NOVEL: (c) POWER-LAW CONTOUR WEIGHT WITH NEIGHBOUR-COUNT TAPER --
        first pass to apply power-law darkening weight to contour pixels and
        to reduce contour weight at low-connectivity endpoint pixels using a
        3x3 neighbour count; no prior pass combines gradient-magnitude-derived
        contour weight with endpoint taper suppression for variable-thickness
        figurative contour simulation.

        contour_threshold : Gradient magnitude threshold for edge detection.
        max_weight        : Maximum blend fraction toward outline_tone.
        weight_exponent   : Power-law exponent for contour weight scaling.
        outline_tone      : Dark warm RGB for contour darkening.
        junction_boost    : Additive weight increase at junction pixels.
        taper_strength    : Weight reduction at endpoint/isolated edge pixels.
        opacity           : Final composite opacity (0=no change, 1=full).
        \"\"\"
        import numpy as _np

        print("    Contour Weight pass (session 254 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        r0 = orig[:, :, 2].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0)

        # Stage 1: Gradient field (magnitude + direction)
        gx = _np.zeros_like(lum)
        gx[:, 1:-1] = lum[:, 2:] - lum[:, :-2]
        gx[:, 0] = lum[:, 1] - lum[:, 0]
        gx[:, -1] = lum[:, -1] - lum[:, -2]
        gy = _np.zeros_like(lum)
        gy[1:-1, :] = lum[2:, :] - lum[:-2, :]
        gy[0, :] = lum[1, :] - lum[0, :]
        gy[-1, :] = lum[-1, :] - lum[-2, :]

        grad_mag = _np.sqrt(gx ** 2 + gy ** 2).astype(_np.float32)
        grad_dir = _np.arctan2(gy, gx).astype(_np.float32)   # [-pi, pi]

        thresh = float(contour_threshold)
        # Edge weight in [0, 1] above threshold
        edge_weight = _np.clip((grad_mag - thresh) / (grad_mag.max() - thresh + 1e-6),
                               0.0, 1.0)
        edge_mask = (grad_mag > thresh).astype(_np.float32)

        # Stage 2: Junction detection via local angular variance
        # Compute local circular variance of gradient direction in 3x3 window
        sin_dir = _np.sin(grad_dir)
        cos_dir = _np.cos(grad_dir)
        # Local mean direction components via box filter
        from scipy.ndimage import uniform_filter as _uf
        sin_mean = _uf(sin_dir, size=3)
        cos_mean = _uf(cos_dir, size=3)
        # Circular variance in [0, 1]: 0=uniform direction, 1=highly variable
        circ_var = 1.0 - _np.sqrt(sin_mean ** 2 + cos_mean ** 2).astype(_np.float32)
        # Junction pixels: high direction variance on edges
        junction_map = (circ_var * edge_mask).astype(_np.float32)
        # Add junction boost to edge weight
        edge_weight = _np.clip(edge_weight + junction_map * float(junction_boost),
                               0.0, 1.0)

        # Stage 3: Taper at endpoints and apply darkening
        # Count edge neighbours in 3x3 window
        neighbour_sum = _uf(edge_mask, size=3) * 9.0 - edge_mask
        # Endpoint: fewer than 2 neighbours
        endpoint_mask = ((neighbour_sum < 2.0) & (edge_mask > 0.5)).astype(_np.float32)
        edge_weight = edge_weight * (1.0 - endpoint_mask * float(taper_strength))

        # Apply power-law weight scaling
        exp = float(weight_exponent)
        mw = float(max_weight)
        final_w = _np.clip(edge_weight ** exp * mw, 0.0, 1.0)

        # Darken toward outline_tone
        ot_r, ot_g, ot_b = float(outline_tone[0]), float(outline_tone[1]), float(outline_tone[2])
        r1 = r0 * (1.0 - final_w) + ot_r * final_w
        g1 = g0 * (1.0 - final_w) + ot_g * final_w
        b1 = b0 * (1.0 - final_w) + ot_b * final_w

        r1 = _np.clip(r1, 0.0, 1.0)
        g1 = _np.clip(g1, 0.0, 1.0)
        b1 = _np.clip(b1, 0.0, 1.0)

        # Final composite
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
        n_edge = int((edge_mask > 0.5).sum())
        n_junction = int((junction_map > 0.3).sum())
        print(f"    Contour Weight complete (edge_pixels={n_edge}, "
              f"junction_pixels={n_junction})")
"""

ENGINE_FILE = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_FILE, "r", encoding="utf-8") as f:
    src = f.read()

assert "rego_flat_figure_pass" not in src, \
    "rego_flat_figure_pass already present in stroke_engine.py"
assert "paint_contour_weight_pass" not in src, \
    "paint_contour_weight_pass already present in stroke_engine.py"

# Insert before kiefer_scorched_earth_pass (last artist pass from s253)
ANCHOR = "    def kiefer_scorched_earth_pass("
assert ANCHOR in src, f"Anchor {ANCHOR!r} not found in stroke_engine.py"

new_src = src.replace(
    ANCHOR,
    FLAT_FIGURE_PASS + "\n" + "    def paint_contour_weight_pass(" +
    CONTOUR_WEIGHT_PASS.split("    def paint_contour_weight_pass(", 1)[1] +
    "\n" + ANCHOR
)

with open(ENGINE_FILE, "w", encoding="utf-8") as f:
    f.write(new_src)

print("rego_flat_figure_pass and paint_contour_weight_pass inserted into stroke_engine.py")
