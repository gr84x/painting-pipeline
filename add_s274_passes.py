"""Insert paint_edge_recession_pass (s274 improvement) and
levitan_autumn_shimmer_pass (185th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_edge_recession_pass (s274 improvement) ──────────────────────

EDGE_RECESSION_PASS = '''
    def paint_edge_recession_pass(
        self,
        focal_cx:       float = 0.5,
        focal_cy:       float = 0.5,
        focal_radius:   float = 0.18,
        max_blur_sigma: float = 3.2,
        edge_threshold: float = 0.12,
        edge_sigma:     float = 1.2,
        opacity:        float = 0.72,
    ) -> None:
        r"""Edge Recession (Lost-and-Found Focal Softening) -- session 274 improvement.

        SIMULATION OF THE CLASSICAL ACADEMIC OIL PAINTING TECHNIQUE OF
        LOST-AND-FOUND EDGES: EDGES NEAR THE FOCAL POINT ARE KEPT CRISP
        ("FOUND"), EDGES AT THE PERIPHERY ARE PROGRESSIVELY SOFTENED
        ("LOST") INTO THE SURROUNDING FIELD.

        The lost-and-found edge technique is one of the fundamental tools of
        the academic realist tradition. It was articulated systematically by
        John Singer Sargent, Joaquin Sorolla, and their teacher Carolus-Duran,
        and it is visible in every great figurative painting of the 17th-19th
        centuries -- Velazquez, Rembrandt, Sargent, Zorn:

        FOUND EDGES: Hard, clear, high-contrast transitions between two areas
        of different value or color. Found edges demand the viewer\'s attention
        -- they are used at the primary point of interest (the eye of a
        portrait, the focal object in a still life) and at any boundary where
        the artist wants to draw attention. In painting, found edges are
        created by placing wet paint with a loaded brush alongside a dried
        edge without blending.

        LOST EDGES: Soft, dissolved, graduated transitions where one area
        merges into another without a distinct boundary. Lost edges allow the
        viewer\'s eye to slide from one area to another without being held.
        They are used in backgrounds, shadows, peripheral areas, and anywhere
        the artist wants to create depth, atmosphere, or mystery. In painting,
        lost edges are created by blending wet paint into adjacent wet paint,
        or by softening a dried edge with a dry fan brush.

        SOFT (BROKEN) EDGES: The intermediate case -- an edge that is neither
        perfectly hard nor fully dissolved. This is the most common edge type
        in academic painting, used in mid-distance passages and secondary
        subjects.

        The rule of thumb: the closer to the focal point (the "center of
        interest"), the harder the edges. The further from the focal point,
        the softer the edges. This creates a hierarchy of visual attention
        that guides the viewer\'s eye through the composition.

        Stage 1 EDGE DETECTION: Detect all edges in the canvas using a
        Sobel gradient on the luminance channel. Smooth the input first
        (edge_sigma Gaussian) to reduce pixel noise. Normalize the gradient
        magnitude to [0,1] to get an edge map E where 1 = strong edge.
        The threshold edge_threshold defines what counts as a "real" edge
        vs. smooth texture.
        NOVEL: (a) EDGE-RESTRICTED FOCAL SOFTENING -- no prior paint_
        improvement pass operates specifically on DETECTED EDGES; prior
        passes that blur or soften (paint_sfumato_contour_dissolution_pass,
        paint_aerial_perspective_pass) apply blur UNIFORMLY to ALL pixels
        in a zone; this pass restricts its action to pixels that are ON
        an edge (edge map > threshold), leaving smooth texture areas
        untouched while selectively softening hard edges at the periphery.

        Stage 2 FOCAL DISTANCE COMPUTATION: For each pixel (x, y), compute
        the normalized distance D from the focal point:
          dx = (x/w - focal_cx) / aspect_ratio
          dy = (y/h - focal_cy)
          D = sqrt(dx^2 + dy^2)
        Pixels within focal_radius of the focal point receive D_eff = 0
        (full edge preservation). Beyond focal_radius, D_eff increases
        linearly to 1 at the canvas corners.
        NOVEL: (b) FOCAL POINT PARAMETERIZED SPATIAL CONTROL -- no prior
        paint_ improvement pass uses an explicit FOCAL POINT (cx, cy) to
        spatially modulate any effect; prior passes with spatial modulation
        use: row position (paint_aerial_perspective_pass -- modulated by y),
        luminance zone (paint_scumbling_veil_pass -- gated to dark zone),
        or uniform application; the focal point creates a RADIAL gradient
        of effect rather than a directional or luminance-based one.

        Stage 3 DISTANCE-WEIGHTED BLUR STRENGTH: Compute blur sigma for
        each pixel as:
          sigma_map[y,x] = max_blur_sigma * D_eff[y,x]
        A single global blur at the maximum sigma is computed, then
        the original and blurred are blended per-pixel:
          blend_weight = D_eff * E * opacity
          out = canvas * (1 - blend_weight) + blurred * blend_weight
        The result is that edges near the focal point are unchanged
        (blend_weight ~ 0), while peripheral edges are blended toward
        the blurred version (blend_weight ~ opacity).
        NOVEL: (c) EDGE-MODULATED FOCAL-DISTANCE BLEND -- the blending
        uses a combined weight of (edge map) * (focal distance), meaning
        only edge pixels far from focus are affected; smooth areas are
        always unchanged; this is the first pass to combine an edge
        detector with a focal distance map as its weighting function.
        """
        print("    Edge Recession (Lost-and-Found Focal Softening) pass (session 274 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, sobel as _sobel

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Edge detection ───────────────────────────────────────────
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        lum_smooth = _gf(lum, sigma=float(edge_sigma)).astype(_np.float32)
        gy = _sobel(lum_smooth.astype(_np.float64), axis=0).astype(_np.float32)
        gx = _sobel(lum_smooth.astype(_np.float64), axis=1).astype(_np.float32)
        edge_mag = _np.sqrt(gy ** 2 + gx ** 2).astype(_np.float32)
        emax = float(edge_mag.max())
        edge_norm = (edge_mag / (emax + 1e-8)).astype(_np.float32)
        edge_map = _np.clip((edge_norm - float(edge_threshold)) /
                            (1.0 - float(edge_threshold) + 1e-8), 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Focal distance map ───────────────────────────────────────
        ys = _np.arange(h, dtype=_np.float32).reshape(-1, 1) / float(h)
        xs = _np.arange(w, dtype=_np.float32).reshape(1, -1) / float(w)
        aspect = float(w) / float(h)
        dx = (xs - float(focal_cx)) / aspect
        dy = ys - float(focal_cy)
        dist = _np.sqrt(dx ** 2 + dy ** 2).astype(_np.float32)
        fr = float(focal_radius)
        max_dist = _np.sqrt((max(float(focal_cx), 1.0 - float(focal_cx)) / aspect) ** 2 +
                            max(float(focal_cy), 1.0 - float(focal_cy)) ** 2)
        d_eff = _np.clip((dist - fr) / (max_dist - fr + 1e-8), 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Blur and edge-modulated focal blend ──────────────────────
        blur_sig = float(max_blur_sigma)
        r_blur = _gf(r0, sigma=blur_sig).astype(_np.float32)
        g_blur = _gf(g0, sigma=blur_sig).astype(_np.float32)
        b_blur = _gf(b0, sigma=blur_sig).astype(_np.float32)

        blend_w = (d_eff * edge_map * float(opacity)).astype(_np.float32)
        blend_w = _np.clip(blend_w, 0.0, 1.0)

        out_r = _np.clip(r0 + (r_blur - r0) * blend_w, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 + (g_blur - g0) * blend_w, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 + (b_blur - b0) * blend_w, 0.0, 1.0).astype(_np.float32)

        out_arr = _np.zeros((h, w, 4), dtype=_np.uint8)
        out_arr[:, :, 0] = (out_b * 255).astype(_np.uint8)
        out_arr[:, :, 1] = (out_g * 255).astype(_np.uint8)
        out_arr[:, :, 2] = (out_r * 255).astype(_np.uint8)
        out_arr[:, :, 3] = orig[:, :, 3]

        surface.get_data()[:] = out_arr.tobytes()

'''

# ── Pass 2: levitan_autumn_shimmer_pass (185th mode) ──────────────────────────

LEVITAN_SHIMMER_PASS = '''
    def levitan_autumn_shimmer_pass(
        self,
        warm_threshold:    float = 0.52,
        warmth_spread_min: float = 0.14,
        warmth_sigma:      float = 42.0,
        tint_r_boost:      float = 0.06,
        tint_g_boost:      float = 0.03,
        tint_b_reduce:     float = 0.08,
        tint_max_opacity:  float = 0.55,
        luminance_floor:   float = 0.25,
        noise_seed:        int   = 274,
    ) -> None:
        r"""Levitan Autumn Shimmer (Chromatic Warmth Diffusion) -- session 274, 185th mode.

        THREE-STAGE CHROMATIC WARMTH DIFFUSION TECHNIQUE INSPIRED BY ISAAK
        LEVITAN (1860-1900) -- RUSSIAN LYRICAL IMPRESSIONIST AND SUPREME
        POET OF THE RUSSIAN AUTUMN LANDSCAPE:

        Isaak Levitan was born in Kibartai (then part of the Russian Empire,
        now Lithuania) in 1860 and died in Moscow in 1900 at the age of
        thirty-nine, leaving behind a body of work that constitutes perhaps
        the most emotionally concentrated landscape painting of the nineteenth
        century. He was a student of the Peredvizhniki movement -- the Russian
        Wanderers, who rejected academic painting in favor of realist depictions
        of Russian life -- but he took that movement\'s documentary approach and
        transmuted it into pure lyrical expression. His great teacher was Alexei
        Savrasov (\'The Rooks Have Arrived\', 1871), who taught him that the
        landscape painting is primarily an emotional event, not a topographical
        record.

        What distinguishes Levitan\'s autumn paintings -- \'Golden Autumn\' (1895),
        \'March\' (1895), \'Birch Grove\' (1885-1889) -- from other autumn
        landscapes is the quality of the WARM LIGHT: the golden birch foliage
        seems not merely to be lit by warm light, but to EMANATE warmth, to
        glow from within and radiate into the surrounding cool atmosphere. The
        sky immediately above a golden birch cluster takes on a warm tinge --
        not because Levitan painted it warm, but because the eye, confronted
        with the contrast between the warm leaves and the cool air, perceives
        the warmth as \'bleeding\' outward. Levitan exploited this perceptual
        phenomenon deliberately: he warmed the sky-zones adjacent to golden
        foliage, cooled the shadows below and beside the warm areas, and
        thereby created a CHROMATIC TEMPERATURE DIALOGUE that is the primary
        optical experience of his autumn paintings.

        CHROMATIC WARMTH DIFFUSION as a painterly technique is related to but
        distinct from:
        -- REFLECTED LIGHT (paint_reflected_light_pass): which adds light bounced
           from adjacent bright warm surfaces -- a physically accurate phenomenon
           operating at short range, driven by proximity to light-reflecting
           surfaces. Levitan\'s warm diffusion operates at longer range and is a
           PERCEPTUAL phenomenon: the warm-cool contrast makes the viewer\'s eye
           perceive more warmth than is literally present.
        -- AERIAL PERSPECTIVE (paint_aerial_perspective_pass): which COOLS
           distant zones due to scattering -- the opposite thermal direction.
        -- SCUMBLING VEIL (paint_scumbling_veil_pass): which LIGHTENS dark zones
           with a semi-opaque veil -- a lightness effect, not a hue temperature.

        Stage 1 WARM SOURCE DETECTION AND SIGNAL GENERATION:
        Identify warm-saturated source pixels where:
          R > warm_threshold  AND  (R - B) > warmth_spread_min
        Build warmth source map W_source. Apply wide Gaussian diffusion:
          W_diffuse = gaussian_filter(W_source, sigma=warmth_sigma)
        Normalize to [0,1]. Large sigma (~42px) produces a broad, smooth
        warmth field falling off gently from foliage sources.
        NOVEL: (a) WARM-SOURCE CHROMATIC DIFFUSION -- no prior artist pass
        uses a DETECTED CHROMATIC WARMTH (R - B differential) as a source
        mask for diffusing a chromatic tint; prior passes use luminance
        (scumbling: dark zone; reflected light: bright zone) or position
        (aerial: y coordinate); the source here is the WARM-COOL HUE
        TEMPERATURE DIFFERENTIAL, an independent chromatic axis.

        Stage 2 COOL ZONE GATING:
        To preserve Levitan\'s characteristic cool, transparent shadows:
          lum = 0.299*R + 0.587*G + 0.114*B
          cool_gate = clip((lum - luminance_floor) / luminance_floor, 0, 1)
        Pixels below luminance_floor (deep shadows) receive minimal tint.
        NOVEL: (b) LUMINANCE-GATED WARM TINT -- the tint strength is
        modulated by LUMINANCE FLOOR GATING, preventing warm diffusion from
        filling shadows, maintaining the warm-cool temperature dialogue
        characteristic of Levitan.

        Stage 3 WARM TINT APPLICATION:
        For each pixel, compute final tint weight:
          tint_w = W_diffuse_norm * cool_gate * tint_max_opacity
        Apply warm tint:
          out_R = clip(R + tint_r_boost * tint_w, 0, 1)
          out_G = clip(G + tint_g_boost * tint_w, 0, 1)
          out_B = clip(B - tint_b_reduce * tint_w, 0, 1)
        NOVEL: (c) ADDITIVE WARM SHIFT (R+, G slight, B-) DRIVEN BY
        DIFFUSED CHROMATIC DISTANCE -- the tint direction (warm golden:
        R+G slight+B-) is specific to autumn foliage warmth; combined with
        the diffused warmth signal, this creates a SPATIALLY LOCALIZED
        WARM CORONA around autumn foliage zones.
        """
        print("    Levitan Autumn Shimmer (Chromatic Warmth Diffusion) pass (session 274, 185th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Warm source detection and diffusion ──────────────────────
        wt   = float(warm_threshold)
        wsm  = float(warmth_spread_min)
        warm_source = ((r0 > wt) & ((r0 - b0) > wsm)).astype(_np.float32)
        sig  = float(warmth_sigma)
        w_diffuse = _gf(warm_source, sigma=sig).astype(_np.float32)
        wmax = float(w_diffuse.max())
        w_norm = (w_diffuse / (wmax + 1e-8)).astype(_np.float32)

        # Exclude the source pixels themselves (already warm)
        w_norm = (w_norm * (1.0 - warm_source)).astype(_np.float32)
        wmax2 = float(w_norm.max())
        if wmax2 > 0:
            w_norm = (w_norm / (wmax2 + 1e-8)).astype(_np.float32)

        # ── Stage 2: Cool zone gating (preserve shadow coolness) ──────────────
        lf = float(luminance_floor)
        cool_gate = _np.clip((lum - lf) / (lf + 1e-8), 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Warm tint application ───────────────────────────────────
        tint_w = (w_norm * cool_gate * float(tint_max_opacity)).astype(_np.float32)

        out_r = _np.clip(r0 + float(tint_r_boost) * tint_w, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 + float(tint_g_boost) * tint_w, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 - float(tint_b_reduce) * tint_w, 0.0, 1.0).astype(_np.float32)

        out_arr = _np.zeros((h, w, 4), dtype=_np.uint8)
        out_arr[:, :, 0] = (out_b * 255).astype(_np.uint8)
        out_arr[:, :, 1] = (out_g * 255).astype(_np.uint8)
        out_arr[:, :, 2] = (out_r * 255).astype(_np.uint8)
        out_arr[:, :, 3] = orig[:, :, 3]

        surface.get_data()[:] = out_arr.tobytes()

'''

# ── Insertion logic ──────────────────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if "paint_edge_recession_pass" in src:
    print("paint_edge_recession_pass already in stroke_engine.py -- skipping.")
else:
    INSERT_BEFORE = "    def klein_ib_field_pass("
    idx = src.find(INSERT_BEFORE)
    if idx == -1:
        print("ERROR: could not find klein_ib_field_pass insertion point.")
        sys.exit(1)
    new_src = src[:idx] + EDGE_RECESSION_PASS + src[idx:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src)
    print("Inserted paint_edge_recession_pass into stroke_engine.py.")
    src = new_src

if "levitan_autumn_shimmer_pass" in src:
    print("levitan_autumn_shimmer_pass already in stroke_engine.py -- skipping.")
else:
    INSERT_BEFORE2 = "    def klein_ib_field_pass("
    idx2 = src.find(INSERT_BEFORE2)
    if idx2 == -1:
        print("ERROR: could not find second insertion point.")
        sys.exit(1)
    new_src2 = src[:idx2] + LEVITAN_SHIMMER_PASS + src[idx2:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src2)
    print("Inserted levitan_autumn_shimmer_pass into stroke_engine.py.")
