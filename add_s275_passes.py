"""Insert paint_impasto_ridge_lighting_pass (s275 improvement) and
picasso_cubist_fragmentation_pass (186th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_impasto_ridge_lighting_pass (s275 improvement) ─────────────

IMPASTO_RIDGE_PASS = '''
    def paint_impasto_ridge_lighting_pass(
        self,
        light_angle_deg:   float = 225.0,
        ridge_strength:    float = 0.60,
        highlight_lift:    float = 0.14,
        shadow_drop:       float = 0.10,
        gradient_sigma:    float = 1.2,
        min_gradient:      float = 0.04,
        ridge_warmth:      float = 0.03,
        opacity:           float = 0.60,
    ) -> None:
        r"""Impasto Ridge Lighting (Directional Raking Light on Paint Ridges) -- session 275 improvement.

        SIMULATION OF HOW OBLIQUE RAKING LIGHT ILLUMINATES THE PHYSICAL RELIEF
        OF IMPASTO PAINT RIDGES -- THE 3D TACTILE QUALITY OF OIL PAINTINGS
        VIEWED UNDER RAKING MUSEUM LIGHTING:

        When an oil painting is placed under raking or oblique light (standard
        museum practice, and the natural light of a north-facing studio window),
        the physical thickness of the paint layer becomes visible as a micro-
        landscape of ridges and valleys. Each brushstroke is a topographic feature:
        the stroke peak is a ridge; the boundary between strokes is a valley; the
        central spine of a loaded-brush stroke is the highest point. Under raking
        light from one direction:
        (a) The face of each ridge that faces toward the light is ILLUMINATED:
            brighter than a flat surface.
        (b) The face of each ridge that points away from the light is in SHADOW:
            darker than average.

        This relief lighting effect is the tactile, three-dimensional quality that
        makes an oil painting alive in person -- used extensively by van Gogh
        (topographic emotion), Rembrandt (loaded light passages in portrait grounds),
        Velazquez (confident single-stroke impasto in light areas), and Sargent
        (fresh wet-on-wet portrait lights).

        Stage 1 LUMINANCE GRADIENT COMPUTATION:
        Compute spatial luminance gradient using Sobel operators after Gaussian
        smoothing at sigma=gradient_sigma, to respond to stroke-scale ridges
        rather than pixel-level noise:
          L = 0.299R + 0.587G + 0.114B
          L_smooth = gaussian_filter(L, sigma=gradient_sigma)
          Gx = Sobel(L_smooth, axis=1)   horizontal gradient
          Gy = Sobel(L_smooth, axis=0)   vertical gradient
          Gmag = sqrt(Gx^2 + Gy^2)
          Gnorm = Gmag / max(Gmag)
        NOVEL: (a) GRADIENT DIRECTION AS PAINT RIDGE ORIENTATION PROXY -- no prior
        pass uses gradient DIRECTION for directional light simulation; prior Sobel
        passes (gorky contour, ernst vein, sfumato dissolution) use MAGNITUDE ONLY
        to detect edges; this pass uses BOTH magnitude (ridge identification) and
        DIRECTION (which way the ridge faces) -- the direction component is novel.

        Stage 2 RIDGE-FACE ILLUMINATION PROJECTION:
        Define light unit vector from light_angle_deg (clockwise from east):
          light_vec = (cos(angle), sin(angle))
        Compute normalised gradient direction and dot with light vector:
          facing = Gx*lx/Gmag + Gy*ly/Gmag
        facing > 0: ridge face toward light (illuminated).
        facing < 0: ridge face away from light (in shadow).
        Restrict to ridge pixels where Gnorm > min_gradient.
        NOVEL: (b) GRADIENT-DIRECTION DOT PRODUCT WITH PARAMETRIC LIGHT DIRECTION
        -- computing the angular relationship between image gradient direction and
        an external light vector is the 2D equivalent of normal-map lighting in
        3D rendering; no prior pass in this codebase performs this operation.

        Stage 3 RIM HIGHLIGHT AND SHADOW INJECTION:
        Lit face (facing > 0):
          R_new = clip(R + highlight_lift * facing * ridge_strength + ridge_warmth)
          G_new = clip(G + highlight_lift * facing * ridge_strength)
          B_new = clip(B + highlight_lift * facing * ridge_strength - ridge_warmth)
        Shadow face (facing < 0):
          all channels: clip(channel - shadow_drop * |facing| * ridge_strength)
        The warmth bias simulates warm light (highlights: red+lift, blue-drop) --
        characteristic of warm studio or afternoon window light.
        NOVEL: (c) FACING-MODULATED DUAL HIGHLIGHT/SHADOW AT GRADIENT RIDGES --
        no prior pass applies BOTH brightening and darkening to HIGH-GRADIENT
        pixels with the choice determined by the gradient-vs-light-direction dot
        product; prior passes apply to luminance zones (bright for lights, dark
        for shadows), not to structural gradient ridges.

        Stage 4 COMPOSITE:
        out = original + (modified - original) * opacity
        """
        print("    Impasto Ridge Lighting (Directional Raking Light) pass (session 275 improvement)...")

        import math as _math
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, sobel as _sobel

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Luminance gradient ────────────────────────────────────────
        lum   = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        lum_s = _gf(lum, sigma=float(gradient_sigma)).astype(_np.float32)
        gx    = _sobel(lum_s.astype(_np.float64), axis=1).astype(_np.float32)
        gy    = _sobel(lum_s.astype(_np.float64), axis=0).astype(_np.float32)
        gmag  = _np.sqrt(gx ** 2 + gy ** 2).astype(_np.float32)
        gmax  = float(gmag.max()) + 1e-8
        gnorm = (gmag / gmax).astype(_np.float32)

        # ── Stage 2: Ridge-face illumination projection ────────────────────────
        angle_rad  = float(light_angle_deg) * _math.pi / 180.0
        lx         = float(_math.cos(angle_rad))
        ly         = float(_math.sin(angle_rad))

        eps        = 1e-8
        safe_gmag  = _np.maximum(gmag, eps)
        gx_unit    = (gx / safe_gmag).astype(_np.float32)
        gy_unit    = (gy / safe_gmag).astype(_np.float32)
        facing     = (gx_unit * lx + gy_unit * ly).astype(_np.float32)

        ridge_mask = (gnorm > float(min_gradient)).astype(_np.float32)
        rs         = float(ridge_strength)
        lit        = _np.maximum(facing,  0.0) * ridge_mask * rs
        dark       = _np.maximum(-facing, 0.0) * ridge_mask * rs

        # ── Stage 3: Rim highlight and shadow injection ────────────────────────
        hl    = float(highlight_lift)
        sd    = float(shadow_drop)
        rw    = float(ridge_warmth)

        mod_r = _np.clip(r0 + lit * (hl + rw) - dark * sd, 0.0, 1.0).astype(_np.float32)
        mod_g = _np.clip(g0 + lit * hl          - dark * sd, 0.0, 1.0).astype(_np.float32)
        mod_b = _np.clip(b0 + lit * (hl - rw)   - dark * sd, 0.0, 1.0).astype(_np.float32)

        # ── Stage 4: Composite ─────────────────────────────────────────────────
        op    = float(opacity)
        out_r = _np.clip(r0 * (1.0 - op) + mod_r * op, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 * (1.0 - op) + mod_g * op, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 * (1.0 - op) + mod_b * op, 0.0, 1.0).astype(_np.float32)

        ridge_px = int(ridge_mask.sum())
        lit_px   = int((lit > 0.02).sum())
        dark_px  = int((dark > 0.02).sum())

        out_arr = _np.zeros((h, w, 4), dtype=_np.uint8)
        out_arr[:, :, 0] = (out_b * 255).astype(_np.uint8)
        out_arr[:, :, 1] = (out_g * 255).astype(_np.uint8)
        out_arr[:, :, 2] = (out_r * 255).astype(_np.uint8)
        out_arr[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = out_arr.tobytes()
        surface.mark_dirty()

        print(f"    Impasto Ridge Lighting complete "
              f"(ridge_px={ridge_px}, lit_px={lit_px}, dark_px={dark_px})")

'''

# ── Pass 2: picasso_cubist_fragmentation_pass (186th mode) ───────────────────

PICASSO_CUBIST_PASS = '''
    def picasso_cubist_fragmentation_pass(
        self,
        n_facets:           int   = 320,
        displacement_sigma: float = 28.0,
        displacement_scale: float = 160.0,
        tonal_variance:     float = 0.065,
        palette_shift:      float = 0.22,
        edge_darkness:      float = 0.50,
        edge_width:         int   = 2,
        noise_seed:         int   = 273,
        opacity:            float = 0.78,
    ) -> None:
        r"""Picasso Cubist Fragmentation (Angular Voronoi Facet Decomposition) -- session 273, 186th mode.

        FOUR-STAGE TECHNIQUE INSPIRED BY PABLO PICASSO (1881-1973) --
        SPANISH-FRENCH CO-FOUNDER OF CUBISM, THE MOST INFLUENTIAL ART MOVEMENT
        OF THE TWENTIETH CENTURY:

        Pablo Picasso, working alongside Georges Braque in Paris from 1907-1914,
        developed CUBISM as a radical response to pictorial representation. Where
        the Impressionists dissolved form into light, and Cezanne rebuilt it with
        geometric planes (cylinder, sphere, cone), Picasso and Braque took
        Cezanne's analysis to its conclusion: if an object can be analyzed into
        geometric planes, WHY SHOW ONLY ONE PLANE AT A TIME? CUBISM collapses
        the temporal experience of walking around a three-dimensional object into
        a SINGLE SIMULTANEOUS IMAGE: multiple viewpoints, overlapping transparent
        planes, all compressed into one moment on the canvas.

        ANALYTIC CUBISM (1907-1912): Severely restricted palette -- ochre, umber,
        grey, near-black, pale cream -- eliminates colour to force attention onto
        structural analysis. The surface is fractured into angular facets, each
        a different tonal register suggesting a different plane at a different angle
        to the light. Key works: Portrait of Ambroise Vollard (1910), Ma Jolie
        (1911-12), Les Demoiselles d\'Avignon (1907), Guernica (1937).

        SYNTHETIC CUBISM (1912-1920): Reverses the process -- builds images from
        flat pre-existing shapes, collage, newsprint, commercial labels. Palette
        expands dramatically. Key works: Three Musicians (1921), Guitar series.

        Stage 1 DISPLACEMENT-DISTORTED VORONOI TESSELLATION:
        Generate N_FACETS seed points across the canvas. Apply a SMOOTH DISPLACEMENT
        FIELD to pixel coordinate space before nearest-neighbor assignment via KDTree:
          dx_field = gaussian_filter(uniform_noise, sigma=displacement_sigma) * displacement_scale
          dy_field = gaussian_filter(uniform_noise, sigma=displacement_sigma) * displacement_scale
          pixel_coords_distorted = pixel_coords + (dx_field, dy_field)
        The displacement creates IRREGULAR ANGULAR SHARD-LIKE CELLS instead of
        smooth convex Voronoi polygons -- Cubist shards, not soap bubbles.
        NOVEL: (a) DISPLACEMENT-DISTORTED VORONOI FOR ANGULAR SHARD TESSELLATION --
        no prior pass uses Voronoi tessellation of any kind; pre-distorting pixel
        coordinates before KDTree assignment (rather than post-hoc warping or
        seed-position jitter) creates angular cells whose shapes are determined by
        the global displacement field rather than by local image content.

        Stage 2 PER-FACET TONAL VARIATION:
        Apply a RANDOM PER-CELL LUMINANCE SHIFT drawn from N(0, tonal_variance)
        to each Voronoi cell, scaling the RGB channels proportionally.
        Creates the STACKED PLANE EFFECT: each facet has its own independent tonal
        register, suggesting it represents a plane at a different angle to the light.
        NOVEL: (b) PER-CELL RANDOM INDEPENDENT TONAL MODULATION -- no prior pass
        applies independent random luminance offsets to spatially-defined canvas
        regions; prior tonal passes apply global shifts or image-content-driven zones
        (dark_zone passes, saturation-zone passes); per-cell independence is new.

        Stage 3 ANALYTIC CUBISM PALETTE RESTRICTION:
        For each pixel, find the nearest colour in the Analytic Cubism palette
        {ochre, warm_grey, raw_umber, pale_cream, dark_umber} and blend toward it
        at palette_shift strength. Mutes and unifies the colour toward the
        characteristic restricted ochre-grey-umber continuum of 1909-1912.
        NOVEL: (c) NEAREST-PALETTE-COLOUR RESTRICTION TO HISTORICAL PIGMENT SET --
        no prior pass restricts palette to a historically-defined pigment set using
        nearest-colour-in-RGB-space computation via KDTree.

        Stage 4 FACET BOUNDARY DARKENING:
        Detect pixels where any 4-connected neighbour has a different Voronoi label.
        Darken boundary pixels by edge_darkness fraction; dilate by edge_width.
        Simulates the characteristic dark contour lines that separate Cubist planes.
        NOVEL: (d) VORONOI-BOUNDARY-DARKENING AS CUBIST PLANE EDGE -- no prior pass
        computes the discrete boundary of a Voronoi tessellation and darkens it with
        a width parameter; prior edge passes detect boundaries from image gradients or
        synthetic fields, not from a computed spatial partition.
        """
        print("    Picasso Cubist Fragmentation (186th mode) pass (session 275)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, binary_dilation as _bd
        from scipy.spatial import KDTree as _KDTree

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        rng = _np.random.default_rng(int(noise_seed))

        # ── Stage 1: Displacement-distorted Voronoi tessellation ──────────────
        n_f     = int(n_facets)
        seeds_y = rng.uniform(0, h, n_f).astype(_np.float32)
        seeds_x = rng.uniform(0, w, n_f).astype(_np.float32)
        seeds   = _np.column_stack([seeds_y, seeds_x]).astype(_np.float32)

        dx_raw  = rng.uniform(-1.0, 1.0, (h, w)).astype(_np.float32)
        dy_raw  = rng.uniform(-1.0, 1.0, (h, w)).astype(_np.float32)
        ds      = float(displacement_scale)
        dx_blur = (_gf(dx_raw, sigma=float(displacement_sigma)) * ds).astype(_np.float32)
        dy_blur = (_gf(dy_raw, sigma=float(displacement_sigma)) * ds).astype(_np.float32)

        yy, xx      = _np.mgrid[0:h, 0:w]
        py_dist     = (yy.astype(_np.float32) + dy_blur).ravel()
        px_dist     = (xx.astype(_np.float32) + dx_blur).ravel()
        pixels_dist = _np.column_stack([py_dist, px_dist]).astype(_np.float32)

        tree = _KDTree(seeds)
        _, labels_flat = tree.query(pixels_dist, workers=1)
        labels = labels_flat.reshape(h, w).astype(_np.int32)

        # ── Stage 2: Per-facet tonal variation ────────────────────────────────
        tv          = float(tonal_variance)
        cell_shifts = rng.normal(0.0, tv, n_f).astype(_np.float32)
        shift_map   = cell_shifts[labels]

        lum         = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        lum_shifted = _np.clip(lum + shift_map, 0.0, 1.0).astype(_np.float32)
        lum_safe    = _np.maximum(lum, 1e-6)
        scale       = (lum_shifted / lum_safe).astype(_np.float32)

        r1 = _np.clip(r0 * scale, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * scale, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * scale, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Analytic Cubism palette restriction ───────────────────────
        palette = _np.array([
            [0.72, 0.60, 0.30],   # ochre
            [0.58, 0.56, 0.52],   # warm grey
            [0.35, 0.27, 0.15],   # raw umber
            [0.88, 0.84, 0.72],   # pale cream
            [0.14, 0.11, 0.08],   # dark umber
        ], dtype=_np.float32)

        ps         = float(palette_shift)
        pixels_rgb = _np.stack([r1.ravel(), g1.ravel(), b1.ravel()], axis=1)
        pal_tree   = _KDTree(palette)
        _, pal_idx = pal_tree.query(pixels_rgb, workers=1)
        nearest    = palette[pal_idx]

        r2 = _np.clip(r1 + (nearest[:, 0].reshape(h, w) - r1) * ps, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 + (nearest[:, 1].reshape(h, w) - g1) * ps, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 + (nearest[:, 2].reshape(h, w) - b1) * ps, 0.0, 1.0).astype(_np.float32)

        # ── Stage 4: Facet boundary darkening ─────────────────────────────────
        right    = _np.abs(labels[:, 1:].astype(_np.float32) - labels[:, :-1].astype(_np.float32)) > 0.5
        down     = _np.abs(labels[1:, :].astype(_np.float32) - labels[:-1, :].astype(_np.float32)) > 0.5
        boundary = _np.zeros((h, w), dtype=bool)
        boundary[:, 1:]  |= right
        boundary[:, :-1] |= right
        boundary[1:, :]  |= down
        boundary[:-1, :] |= down

        ew = int(edge_width)
        if ew > 1:
            struct   = _np.ones((ew * 2 - 1, ew * 2 - 1), dtype=bool)
            boundary = _bd(boundary, structure=struct)

        ed = float(edge_darkness)
        bm = boundary.astype(_np.float32)

        r3 = _np.clip(r2 * (1.0 - bm * ed), 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 * (1.0 - bm * ed), 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 * (1.0 - bm * ed), 0.0, 1.0).astype(_np.float32)

        # ── Composite with master opacity ─────────────────────────────────────
        op    = float(opacity)
        out_r = _np.clip(r0 * (1.0 - op) + r3 * op, 0.0, 1.0).astype(_np.float32)
        out_g = _np.clip(g0 * (1.0 - op) + g3 * op, 0.0, 1.0).astype(_np.float32)
        out_b = _np.clip(b0 * (1.0 - op) + b3 * op, 0.0, 1.0).astype(_np.float32)

        out_arr = _np.zeros((h, w, 4), dtype=_np.uint8)
        out_arr[:, :, 0] = (out_b * 255).astype(_np.uint8)
        out_arr[:, :, 1] = (out_g * 255).astype(_np.uint8)
        out_arr[:, :, 2] = (out_r * 255).astype(_np.uint8)
        out_arr[:, :, 3] = orig[:, :, 3]
        surface.get_data()[:] = out_arr.tobytes()
        surface.mark_dirty()

        boundary_px = int(boundary.sum())
        print(f"    Picasso Cubist Fragmentation complete "
              f"(n_facets={n_f}, boundary_px={boundary_px})")

'''

# ── Insertion logic ──────────────────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if "paint_impasto_ridge_lighting_pass" in src:
    print("paint_impasto_ridge_lighting_pass already in stroke_engine.py -- skipping.")
else:
    INSERT_BEFORE = "    def paint_transparent_glaze_pass("
    idx = src.find(INSERT_BEFORE)
    if idx == -1:
        print("ERROR: could not find paint_transparent_glaze_pass insertion point.")
        sys.exit(1)
    new_src = src[:idx] + IMPASTO_RIDGE_PASS + src[idx:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src)
    print("Inserted paint_impasto_ridge_lighting_pass into stroke_engine.py.")
    src = new_src

if "picasso_cubist_fragmentation_pass" in src:
    print("picasso_cubist_fragmentation_pass already in stroke_engine.py -- skipping.")
else:
    INSERT_BEFORE2 = "    def paint_transparent_glaze_pass("
    idx2 = src.find(INSERT_BEFORE2)
    if idx2 == -1:
        print("ERROR: could not find second insertion point.")
        sys.exit(1)
    new_src2 = src[:idx2] + PICASSO_CUBIST_PASS + src[idx2:]
    with open(ENGINE_PATH, "w", encoding="utf-8") as f:
        f.write(new_src2)
    print("Inserted picasso_cubist_fragmentation_pass into stroke_engine.py.")
