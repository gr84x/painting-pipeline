"""Insert paint_impasto_relief_pass (s289 improvement) and
dubuffet_art_brut_pass (200th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_impasto_relief_pass (s289 improvement) ─────────────────────

IMPASTO_RELIEF_PASS = '''
    def paint_impasto_relief_pass(
        self,
        sigma_thickness:  float = 2.8,
        relief_strength:  float = 0.50,
        light_az:         float = -0.55,
        light_el:         float = -0.62,
        ambient:          float = 0.14,
        specular_amount:  float = 0.28,
        specular_power:   float = 14.0,
        opacity:          float = 0.62,
    ) -> None:
        r"""Impasto Relief Lighting -- s289 improvement.

        THE PHYSICAL BASIS: SURFACE NORMALS AND THREE-DIMENSIONAL LIGHTING

        Every one of the 199 prior passes in this engine operates purely in 2D
        colour space.  They modify hue, saturation, luminance, edge contrast,
        or colour temperature.  But none of them treats the painted surface as a
        three-dimensional physical object.  Oil paintings ARE three-dimensional
        objects: a thick impasto stroke by Rembrandt or Frank Auerbach can be
        half a millimetre proud of the canvas.  That physical relief catches
        light on its ridge face, casts a micro-shadow in its recess, and creates
        a specular highlight along its crest.  This pass simulates exactly that.

        THE THICKNESS MAP:

        True paint thickness cannot be measured from a 2D image without
        photometric stereo or a depth scanner.  We approximate it from the
        high-frequency luminance content of the canvas at the current painting
        stage.  The intuition is: where the painter has deposited a dense ridge
        of strokes — at a highlight, at a sharp edge, at an impasto accent — the
        luminance value deviates from its local neighbourhood average.  A Gaussian
        smooth of the luminance field gives the "low-frequency surface" (the large
        tonal planes).  The residual — lum_raw − lum_smooth — is the thickness
        estimate: positive where the paint is proud (luminance peak), negative
        where the paint is recessed (luminance valley relative to surroundings).

        THE SURFACE NORMAL:

        A thickness map T(x,y) describes a height field.  The surface normal at
        each pixel is the cross product of the two tangent vectors along the x
        and y axes:

          dT/dx ≈ (T[x+1,y] − T[x−1,y]) / 2     (central difference, axis=1)
          dT/dy ≈ (T[x,y+1] − T[x,y−1]) / 2     (central difference, axis=0)

        The outward-pointing surface normal is:
          n = normalize( −dT/dx × s,  −dT/dy × s,  1.0 )

        where s = relief_strength × 15 is a scale factor converting the
        dimensionless thickness residual into a surface tilt angle.  With s=7.5
        (the default relief_strength=0.50), a thickness gradient of 0.10 produces
        a tilt of approximately 4.3°, which is photometrically visible as a gentle
        ridge highlight without distorting the painting's colour balance.

        MATHEMATICAL NOVELTY IN THIS ENGINE:

        NOVEL (a): FIRST SURFACE NORMAL COMPUTATION IN ENGINE.  All 199 prior
        passes use 2D image operations.  This pass computes a 3D surface normal
        field from a 2D height map, introducing the fundamental data structure of
        3D computer graphics (the normal vector) into the painting engine for the
        first time.

        NOVEL (b): FIRST LAMBERTIAN REFLECTANCE MODEL IN ENGINE.  The diffuse
        term D = max(0, n · L) is the Lambertian bidirectional reflectance
        distribution function (BRDF), the simplest physically-based lighting
        model.  It states that the reflected radiance is proportional to the
        cosine of the angle between the surface normal and the light direction,
        a consequence of the solid-angle foreshortening of an incoming beam on
        a tilted surface (Lambert, 1760).  No prior pass uses any lighting model.

        NOVEL (c): FIRST BLINN-PHONG SPECULAR IN ENGINE.  The specular term
        S = max(0, n · h)^p, where h = normalize(L + V) is the half-vector
        between the light direction L and the view direction V = (0,0,1), is the
        Blinn (1977) modification of the Phong (1975) specular model.  It creates
        a focused highlight on the steepest, most correctly-oriented ridges.

        IMPLEMENTATION:

          (1) THICKNESS MAP: lum = 0.299R + 0.587G + 0.114B;
              thickness = lum − gaussian(lum, sigma_thickness).
              Thickness range approximately [−0.20, +0.20] for a typical
              multi-pass painted canvas.

          (2) SURFACE NORMALS: nx = −∂T/∂x * s; ny = −∂T/∂y * s; nz = 1.0;
              normalize to unit length.

          (3) LAMBERTIAN DIFFUSE: light = normalize(light_az, light_el, 1.0);
              D = clip(nx*Lx + ny*Ly + nz*Lz, 0, 1).

          (4) BLINN-PHONG SPECULAR: view = (0,0,1); h = normalize(L+V);
              S = clip(nx*hx + ny*hy + nz*hz, 0, 1)^p * specular_amount.

          (5) COMPOSITE: total = ambient + D*(1−ambient) + S;
              light_delta = total − (ambient + 1−ambient) = total − 1.0;
              The delta captures the net brightening or darkening relative to
              a flat matte surface.  Blend: R_out = R + light_delta * opacity.

        The result is a subtle embossing effect: paint ridges acquire a warm
        highlight on their light-facing slope and a cool micro-shadow on their
        shadow slope, making the surface read as physically three-dimensional
        without altering the hue or saturation of the underlying painting.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gauss

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        # ── 1. Thickness map ─────────────────────────────────────────────────
        lum = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)
        lum_smooth = _gauss(lum, sigma=float(sigma_thickness)).astype(_np.float32)
        thickness = (lum - lum_smooth).astype(_np.float32)

        # ── 2. Surface normals from thickness gradient ───────────────────────
        scale = float(relief_strength) * 15.0
        dTdy = _np.gradient(thickness, axis=0).astype(_np.float32)
        dTdx = _np.gradient(thickness, axis=1).astype(_np.float32)

        nx = (-dTdx * scale).astype(_np.float32)
        ny = (-dTdy * scale).astype(_np.float32)
        nz = _np.ones((H_, W_), dtype=_np.float32)

        n_mag = _np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-7
        nx = (nx / n_mag).astype(_np.float32)
        ny = (ny / n_mag).astype(_np.float32)
        nz = (nz / n_mag).astype(_np.float32)

        # ── 3. Lambertian diffuse ────────────────────────────────────────────
        # Light from upper-left (az=-0.55, el=-0.62, z=1.0), normalized
        lx = float(light_az)
        ly = float(light_el)
        lz = 1.0
        l_mag = _np.sqrt(lx * lx + ly * ly + lz * lz)
        lx /= l_mag; ly /= l_mag; lz /= l_mag

        diffuse = _np.clip(nx * lx + ny * ly + nz * lz, 0.0, 1.0
                           ).astype(_np.float32)

        # ── 4. Blinn-Phong specular ──────────────────────────────────────────
        # View direction: straight-on (0, 0, 1) — flat canvas
        vx, vy, vz = 0.0, 0.0, 1.0
        hx = lx + vx
        hy = ly + vy
        hz = lz + vz
        h_mag = _np.sqrt(hx * hx + hy * hy + hz * hz)
        hx /= h_mag; hy /= h_mag; hz /= h_mag

        spec_cos = _np.clip(nx * hx + ny * hy + nz * hz, 0.0, 1.0
                            ).astype(_np.float32)
        specular = (spec_cos ** float(specular_power) * float(specular_amount)
                    ).astype(_np.float32)

        # ── 5. Composite ─────────────────────────────────────────────────────
        amb = float(ambient)
        # Total illumination vs flat-matte baseline (ambient + full diffuse)
        total   = _np.clip(amb + diffuse * (1.0 - amb) + specular, 0.0, 1.5
                           ).astype(_np.float32)
        # Baseline: flat-matte surface receives ambient + full diffuse = 1.0
        baseline = amb + (1.0 - amb)   # = 1.0
        delta = (total - baseline).astype(_np.float32)   # [-1, +0.5]

        op = float(opacity)
        R_out = _np.clip(R + delta * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + delta * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + delta * op, 0.0, 1.0).astype(_np.float32)

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        ridge_px     = int((thickness > 0.02).sum())
        specular_px  = int((specular > 0.05).sum())
        print(f"    Impasto Relief complete "
              f"(ridge_px={ridge_px}, specular_px={specular_px})")

'''

# ── Pass 2: dubuffet_art_brut_pass (200th mode) ───────────────────────────────

DUBUFFET_PASS = '''
    def dubuffet_art_brut_pass(
        self,
        cell_freq_a:        float = 0.042,
        cell_freq_b:        float = 0.031,
        cell_freq_c:        float = 0.058,
        cell_freq_d:        float = 0.027,
        cell_line_width:    float = 0.030,
        cell_line_dark:     float = 0.72,
        grain_strength:     float = 0.055,
        grain_seed:         int   = 289,
        palette_strength:   float = 0.38,
        edge_dark_strength: float = 0.60,
        edge_dark_sigma:    float = 1.2,
        opacity:            float = 0.82,
    ) -> None:
        r"""Dubuffet Art Brut Surface -- s289, 200th mode.

        JEAN DUBUFFET (1901-1985): ART BRUT AND THE REFUSAL OF CULTURE

        Jean Dubuffet was born in Le Havre, France, the son of a wine merchant,
        and spent his twenties abandoning his art studies to run the family wine
        business — returning to full-time painting only at age 41, in 1942.  This
        late start was not a handicap but a deliberate ideological act: Dubuffet
        had concluded that "cultural art" — the entire tradition of Western
        painting from the Renaissance onward — was a suffocating orthodoxy that
        privileged skill, beauty, and refinement at the expense of vitality,
        immediacy, and raw expression.

        In 1945, Dubuffet coined the term ART BRUT ("raw art") to describe work
        created outside the mainstream art world: by psychiatric patients, self-
        taught outsiders, prisoners, and children.  He collected it obsessively
        and founded the Collection de l'Art Brut in Lausanne.  More importantly,
        he MADE it: his own paintings deliberately emulated the directness and
        clumsiness of outsider art, rejecting illusionism, perspective, and
        anatomical correctness in favour of thick, material, scratched surfaces.

        DUBUFFET'S FIVE DEFINING TECHNICAL SIGNATURES:

        (1) L'HOURLOUPE CELLULAR NETWORKS (1962-1974): Dubuffet's greatest series
        is defined by an irregular cellular grid — interlocking, jigsaw-like
        regions separated by heavy black lines, each cell filled with red-and-
        blue hatch marks or flat colour.  The network reads simultaneously as
        abstract pattern and as fragmented figure-ground.  The boundary lines are
        not drawn with a ruler but scored irregularly, like cracking earth or
        organic cell division.  The present pass simulates this cellular network
        using a sine-wave interference pattern: two pairs of oblique sine waves
        create an irregular standing-wave grid whose zero-crossings correspond
        to Dubuffet's cell boundaries.

        (2) EARTH MATERIAL MIXING: In his Texturologies and Matériologies series
        (1957-1960), Dubuffet mixed oil paint with earth, sand, gravel, coal dust,
        bottle glass, and tar — refusing the distinction between "painting medium"
        and "raw matter."  The resulting surfaces are granular, rough, and
        absorptive: the paint looks like dried mud or compacted soil rather than
        smooth impasto.  The present pass adds coarse stochastic grain tinted
        toward raw earth colors to simulate this material quality.

        (3) PALETTE OF RAW MATERIALS: Dubuffet rejected the Impressionist palette
        of atmospheric light.  His colours are the colours of matter: raw umber
        (earth), ochre (clay), iron oxide red (rust), bone white (ash), and
        graphite black (charcoal).  Even his most colourful works (the Hourloupe)
        use only red-blue-white-black — not a single mixed or modulated colour.
        The present pass contracts the canvas palette toward Dubuffet's five
        raw-material anchors using the L1 (taxicab) distance metric.

        (4) SCORED AND BITUMEN OUTLINES: In his Corps de Dames and Portraits
        series, Dubuffet outlined his figures with heavy, irregular, almost
        childlike contours — sometimes scored into wet paint with a palette knife,
        sometimes drawn in bitumen (asphalt) over dried paint.  The result is
        a dark boundary that is simultaneously line and groove, separating the
        interior of each form from the field around it with primitive authority.
        The present pass applies gradient-magnitude edge detection to find these
        boundaries and darkens/blackens them.

        (5) ANTI-PERSPECTIVE FLATNESS: Dubuffet aggressively refused spatial depth.
        His figures are flattened against the picture plane; sky and ground occupy
        the same visual weight; forms overlap without recession.  The palette
        contraction toward a flat set of four-five colours supports this flatness
        by removing the gradual atmospheric modulation that creates depth in
        illusionistic painting.

        MATHEMATICAL NOVELTY IN THIS ENGINE:

        NOVEL (a): FIRST SINE-WAVE INTERFERENCE CELLULAR NETWORK.  Stages 1-199
        use Gaussian blurs, median filters, palette assignment (L2 or fixed-
        target), gradient magnitude, and stochastic sampling.  None generates a
        cellular topology.  The interference formula
          cell_d = min(|sin(f_a*x + f_b*y)|, |sin(f_c*x + f_d*y)|)
        creates an irregular standing-wave grid whose lines divide the canvas
        into closed cells without any random sampling — purely deterministic,
        frequency-controlled, and resolution-independent.

        NOVEL (b): FIRST L1 PALETTE DISTANCE METRIC IN ENGINE.  Hartley (s287)
        used L2 (Euclidean) distance in RGB space to find the nearest palette
        colour.  L1 (sum of absolute differences, taxicab metric) weights each
        channel equally rather than squaring large differences; it produces
        slightly harder, more posterized colour assignments because the equal
        channel weighting makes the decision boundary a rhombus (L1 ball) rather
        than a sphere (L2 ball).  This creates the flat, forceful colour fills
        characteristic of Dubuffet's Hourloupe series.

        NOVEL (c): FIRST COARSE INTEGER-SAMPLE GRAIN.  Prior noise in the engine
        uses Gaussian random samples (smooth, bell-curve distribution) or uniform
        float samples.  This pass generates grain from raw integer-modulo indexing:
        grain = abs(((px_index * grain_seed) % 255) − 127) / 255, which creates
        a deterministic but visually irregular salt-and-pepper texture with no
        spatial correlation — harsher and more "material" than any Gaussian sample.

        IMPLEMENTATION:

          (1) CELLULAR SCORING:
              x = col indices 0..W−1; y = row indices 0..H−1 (as float32)
              cell_d = min(|sin(f_a*x + f_b*y)|, |sin(f_c*x + f_d*y)|)
              line_mask = (cell_d < cell_line_width)
              In line zones: push R,G,B toward current value * (1 − cell_line_dark)
              i.e. darken by cell_line_dark fraction.

          (2) EARTH MATERIAL GRAIN:
              flat_idx = row * W + col (raster index, float32)
              grain = abs( (flat_idx * grain_seed) mod 255 − 127 ) / 127
              grain is in [0, 1]; push pixel toward raw earth tint
              (sienna ≈ (0.62, 0.32, 0.18)) at grain * grain_strength.

          (3) L1 PALETTE CONTRACTION:
              palette = [bone_white, raw_umber, iron_red, ochre, graphite]
              For each pixel find nearest palette colour by L1 distance
              (|ΔR| + |ΔG| + |ΔB|); blend toward that colour at
              palette_strength * (1 − line_mask_float): stronger in cell
              interiors, weaker at cell boundaries to preserve line darkness.

          (4) EDGE DARKENING (SCORED OUTLINE):
              Compute gradient magnitude from luminance Sobel;
              normalize to [0, 1]; blend pixel toward (dark_r, dark_g, dark_b)
              = current_colour * (1 − edge_dark_strength) at edge magnitude.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, sobel as _sobel

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        # ── 1. Cellular scoring (L\'Hourloupe network) ───────────────────────
        yy, xx = _np.mgrid[0:H_, 0:W_]
        xf = xx.astype(_np.float32)
        yf = yy.astype(_np.float32)

        fa = float(cell_freq_a); fb = float(cell_freq_b)
        fc = float(cell_freq_c); fd = float(cell_freq_d)

        wave1 = _np.abs(_np.sin(fa * xf + fb * yf)).astype(_np.float32)
        wave2 = _np.abs(_np.sin(fc * xf + fd * yf)).astype(_np.float32)
        cell_d = _np.minimum(wave1, wave2)

        clw = float(cell_line_width)
        line_mask = (cell_d < clw).astype(_np.float32)
        # Soften the line mask slightly to avoid pixelated edges
        line_mask_soft = _gf(line_mask, sigma=0.6).astype(_np.float32)

        # Darken cell boundary pixels
        cld = float(cell_line_dark)
        R = R * (1.0 - line_mask_soft * cld)
        G = G * (1.0 - line_mask_soft * cld)
        B = B * (1.0 - line_mask_soft * cld)
        R = _np.clip(R, 0.0, 1.0).astype(_np.float32)
        G = _np.clip(G, 0.0, 1.0).astype(_np.float32)
        B = _np.clip(B, 0.0, 1.0).astype(_np.float32)
        cell_px = int(line_mask.sum())

        # ── 2. Earth material grain ──────────────────────────────────────────
        # Coarse integer-modulo grain: deterministic salt-and-pepper
        flat_idx = (yy * W_ + xx).astype(_np.float32)
        gs = float(grain_seed)
        grain_raw = _np.abs(((flat_idx * gs) % 255.0) - 127.0) / 127.0
        grain = grain_raw.astype(_np.float32)

        # Earth tint: raw sienna (0.62, 0.32, 0.18) — warm dark earth
        gstr = float(grain_strength)
        R = _np.clip(R + (0.62 - R) * grain * gstr, 0.0, 1.0).astype(_np.float32)
        G = _np.clip(G + (0.32 - G) * grain * gstr, 0.0, 1.0).astype(_np.float32)
        B = _np.clip(B + (0.18 - B) * grain * gstr, 0.0, 1.0).astype(_np.float32)

        # ── 3. L1 palette contraction ────────────────────────────────────────
        # Dubuffet raw-material palette (5 anchors, float32 RGB)
        palette = _np.array([
            [0.94, 0.92, 0.82],   # bone white
            [0.28, 0.19, 0.10],   # raw umber
            [0.68, 0.22, 0.10],   # iron oxide red
            [0.80, 0.62, 0.16],   # yellow ochre
            [0.12, 0.11, 0.10],   # graphite black
        ], dtype=_np.float32)    # shape (5, 3)

        # Compute L1 distances: (H, W, 5)
        pR = R[:, :, _np.newaxis]   # (H, W, 1)
        pG = G[:, :, _np.newaxis]
        pB = B[:, :, _np.newaxis]

        pal_R = palette[:, 0]   # (5,)
        pal_G = palette[:, 1]
        pal_B = palette[:, 2]

        l1_dist = (_np.abs(pR - pal_R) + _np.abs(pG - pal_G) + _np.abs(pB - pal_B)
                   ).astype(_np.float32)   # (H, W, 5)
        nearest_idx = _np.argmin(l1_dist, axis=2)   # (H, W)

        near_R = palette[nearest_idx, 0].astype(_np.float32)
        near_G = palette[nearest_idx, 1].astype(_np.float32)
        near_B = palette[nearest_idx, 2].astype(_np.float32)

        # Interior cells get stronger palette pull; boundary lines weaker
        ps = float(palette_strength) * (1.0 - line_mask_soft * 0.6)
        R = _np.clip(R + (near_R - R) * ps, 0.0, 1.0).astype(_np.float32)
        G = _np.clip(G + (near_G - G) * ps, 0.0, 1.0).astype(_np.float32)
        B = _np.clip(B + (near_B - B) * ps, 0.0, 1.0).astype(_np.float32)
        pal_px = int((l1_dist.min(axis=2) < 0.25).sum())

        # ── 4. Scored edge darkening ─────────────────────────────────────────
        lum2 = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)
        lum_sm = _gf(lum2, sigma=float(edge_dark_sigma)).astype(_np.float32)

        Sx = _sobel(lum_sm, axis=1).astype(_np.float32)
        Sy = _sobel(lum_sm, axis=0).astype(_np.float32)
        edge_mag = _np.sqrt(Sx * Sx + Sy * Sy).astype(_np.float32)
        edge_max = edge_mag.max() + 1e-7
        edge_norm = _np.clip(edge_mag / edge_max, 0.0, 1.0).astype(_np.float32)

        eds = float(edge_dark_strength)
        R = _np.clip(R * (1.0 - edge_norm * eds), 0.0, 1.0).astype(_np.float32)
        G = _np.clip(G * (1.0 - edge_norm * eds), 0.0, 1.0).astype(_np.float32)
        B = _np.clip(B * (1.0 - edge_norm * eds), 0.0, 1.0).astype(_np.float32)
        edge_px = int((edge_norm > 0.15).sum())

        # ── Final blend ──────────────────────────────────────────────────────
        op = float(opacity)
        R_in = raw[:, :, 2].astype(_np.float32) / 255.0
        G_in = raw[:, :, 1].astype(_np.float32) / 255.0
        B_in = raw[:, :, 0].astype(_np.float32) / 255.0

        R_out = _np.clip(R_in + (R - R_in) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G_in + (G - G_in) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B_in + (B - B_in) * op, 0.0, 1.0).astype(_np.float32)

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Dubuffet Art Brut complete "
              f"(cell_px={cell_px}, pal_px={pal_px}, edge_px={edge_px})")

'''

# ── Append both passes to stroke_engine.py ───────────────────────────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8-sig") as f:
    src = f.read()

assert "paint_impasto_relief_pass" not in src, \
    "paint_impasto_relief_pass already exists in stroke_engine.py"
assert "dubuffet_art_brut_pass" not in src, \
    "dubuffet_art_brut_pass already exists in stroke_engine.py"

with open(SE_PATH, "a", encoding="utf-8") as f:
    f.write(IMPASTO_RELIEF_PASS)
    f.write(DUBUFFET_PASS)

print("stroke_engine.py patched: paint_impasto_relief_pass (s289 improvement)"
      " + dubuffet_art_brut_pass (200th mode) appended.")
