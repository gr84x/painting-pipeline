"""Append grosz_neue_sachlichkeit_pass (195th mode) to stroke_engine.py.

This supplementary script adds the primary 195th mode artist pass after the
kokoschka_vibrating_surface_pass (which was appended in add_s284_passes.py).
George Grosz (1893-1959) -- German Expressionist / New Objectivity.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

GROSZ_PASS = '''
    def grosz_neue_sachlichkeit_pass(
        self,
        gradient_sigma:     float = 1.3,
        shadow_darken:      float = 0.60,
        zone_sigma:         float = 6.0,
        flat_strength:      float = 0.28,
        acid_strength:      float = 0.26,
        acid_r:             float = 0.78,
        acid_g:             float = 0.84,
        acid_b:             float = 0.14,
        dark_push_r:        float = 0.10,
        dark_push_g:        float = 0.08,
        dark_push_b:        float = 0.16,
        dark_push_strength: float = 0.22,
        gamma_value:        float = 0.80,
        opacity:            float = 0.82,
    ) -> None:
        r"""Grosz Neue Sachlichkeit (German New Objectivity -- Weimar Satirist) -- 195th mode.

        GEORGE GROSZ (1893-1959) -- GERMAN SATIRIST, EXPRESSIONIST, AND
        CHRONICLER OF WEIMAR GERMANY\'S GROTESQUE SOCIAL THEATRE:

        George Grosz was born in Berlin in 1893, the son of an innkeeper. He
        studied at the Dresden Academy and the Berlin School of Arts and Crafts
        before the First World War, during which he served twice and was twice
        declared unfit for service on psychological grounds. The war and its
        aftermath -- the Weimar Republic with its inflation, street violence,
        political assassinations, and feverish decadence -- became the raw
        material for his most important work.

        Grosz was a founding member of Berlin Dada (1918) and later a central
        figure in the Neue Sachlichkeit (New Objectivity) movement. While the
        New Objectivity label encompassed both the "Verists" (Grosz, Dix) and
        the "Magic Realists" (Schad, Räderscheidt), Grosz was the supreme Verist:
        his paintings and drawings attacked the military, the bourgeoisie, the
        church, and the institutions of Weimar society with a ferocity unmatched
        in the visual arts. He was prosecuted three times for "offences against
        public morality" and once for "blasphemy" for his portfolio "Ecce Homo"
        (1923).

        In 1933, the day after Hitler came to power, Grosz emigrated to the
        United States, where he spent the rest of his career teaching in New
        York. He returned to Germany in 1959 and died there the same year,
        weeks after his return.

        GROSZ\'S FIVE DEFINING TECHNICAL CHARACTERISTICS:

        1. THE DIRECTIONAL CAST SHADOW LINE (Raking Light Model): Grosz
           structured his images with an implied raking light from the upper
           left, creating heavy cast shadows on the right and lower edges of
           every form. This is not Rembrandt\'s modelled rounding; it is a
           graphic convention -- the shadow is painted as a dark edge, a bold
           cast line, giving every form a harsh two-dimensionality. The painted
           form looks cut from paper, not modelled in clay.

        2. FLAT ZONE GRAPHIC UNIFICATION: Between the dark contour lines, Grosz
           applied relatively flat areas of uniform colour. These zones are not
           the shimmering, varied brushwork of the Impressionists or the faceted
           strokes of the Post-Impressionists. They are graphic, almost poster-
           like: a single local colour applied smoothly within its defined area.
           The flatness emphasises the satirical reading -- these are not living
           beings but types, figures in a political cartoon.

        3. ACID YELLOW-GREEN PALETTE (Moral Sickness as Colour): Grosz\'s figures
           frequently carry a sickly, jaundiced colour: yellow-green flesh, acid
           ochre fabric, garish vermillion accents. This is not naturalistic; it
           is deliberately disturbing. The acid colour suggests disease, moral
           corruption, poisoned atmosphere. It is the colour of the Weimar
           night club, the hospital ward, the courtroom.

        4. DEEP SHADOW OPACITY WITH DARK GROUND SHOW-THROUGH: Grosz\'s darkest
           zones -- the interiors of buildings, the shadows under hat-brims, the
           backs of figures -- are pushed toward a deep, slightly warm dark. The
           dark ground of the canvas shows through the paint in these zones,
           creating the impression that the darkness has substance and weight,
           not merely an absence of light.

        5. HARSH TONAL CLARITY (Gamma-Expanded Mid-Values): Despite the brutal
           subject matter, Grosz\'s actual tonal range is unusually clear and
           well-separated. Mid-values are pushed slightly brighter by a gamma
           expansion (equivalent to a power curve of approximately gamma=0.80),
           creating the harsh, over-lit quality of fluorescent lighting or
           German daylight in winter -- clinical, remorseless, with no soft
           half-light to hide the subject\'s ugliness.

        THE GREAT WORKS:
        "Pillars of Society" (1926): A horrifying gallery of Weimar German
        types -- a military officer with a chamber pot for a skull, a priest with
        a bloody dagger, a journalist with feces in his head -- each displaying
        the hypocrisy of their class in their face and posture.

        "The Funeral (Dedication to Oskar Panizza)" (1917-18): A Bruegel-like
        panorama of urban chaos -- a hearse in a red-lit city, surrounded by
        grotesque, hysterical crowds. The composition is compressed, the colour
        lurid.

        "Eclipse of the Sun" (1926): A headless general takes orders from a
        businessman while politicians eat their documents and the sun is blocked
        by a dollar sign. The flatness and harsh colour are typical.

        "Metropolis" (1916-17): An early work showing the Expressionist-Cubist
        synthesis: the Berlin street rendered as an overlapping collision of
        human types, vehicles, and buildings in violent primary and acid colours.

        Stage 1 DIRECTIONAL CAST SHADOW EDGE (Signed-Gradient Asymmetric Darkening):
        Compute the signed spatial gradient of the luminance channel:
          L  = 0.299R + 0.587G + 0.114B
          Gx = GaussianDerivative(L, sigma=gradient_sigma, order=[0,1])
          Gy = GaussianDerivative(L, sigma=gradient_sigma, order=[1,0])
        The SIGN of Gx encodes the light-direction at each edge:
          Gx > 0: luminance is increasing left-to-right (bright side is to the right)
          Gx < 0: luminance is decreasing left-to-right (dark side is to the right;
                  this is the SHADOW SIDE under a left-to-right illumination model)
        Compute gradient magnitude for edge weighting:
          G_mag = sqrt(Gx^2 + Gy^2)
          Gx_scale = max(percentile(|Gx|, 85), 1e-6)
          G_scale  = max(percentile(G_mag,  80), 1e-6)
          Gx_norm = clip(Gx / Gx_scale, -1, 1)
          G_norm  = clip(G_mag / G_scale, 0, 1)
        Build directional shadow mask from NEGATIVE Gx (light from upper-left,
        shadows fall on right/lower edges):
          shadow_edge_mask = clip(-Gx_norm, 0, 1) * G_norm
        Apply darkening on the shadow side:
          R1 = R * (1 - shadow_edge_mask * shadow_darken)
        NOVEL: (a) SIGNED GRADIENT DIRECTION AS EDGE TREATMENT GATE -- this is
        the FIRST pass in this engine to use the SIGN of a gradient component
        (Gx or Gy) as a discriminating gate, rather than the MAGNITUDE alone.
        Every prior pass that uses gradient information uses G_mag, |Gx|, or |Gy|:
          - savrasov_lyrical_mist_pass Stage 3: uses |Gy| (unsigned y-derivative)
          - contre_jour_rim_pass: uses G_mag (luminance boundary detection)
          - repin_character_depth_pass Stages 1+4: uses G_mag
          - form_curvature_tint_pass: uses Laplacian (second derivative, signed,
            but used for convex/concave sign, not directional illumination)
        No prior pass uses a signed FIRST-ORDER gradient component (signed Gx or Gy)
        to model a directed illumination field at edges. The signed-Gx approach
        encodes the Grosz "raking light from upper-left" model: it darkens pixels
        on the SHADOW SIDE of edges (where luminance falls in the illumination
        direction) while leaving the lit side untouched.

        Stage 2 FLAT ZONE GRAPHIC UNIFICATION (Interior Colour Homogenisation):
        Build interior_mask = (1 - G_norm).                Low-gradient areas.
        Apply zone-flattening blur weighted by interior:
          R_blur2 = GaussianFilter(R1, sigma=zone_sigma)
          R2 = R1 + interior_mask * flat_strength * (R_blur2 - R1)
        This smooths low-gradient zones while leaving high-gradient edges sharp,
        creating Grosz\'s graphic, flat-zone quality.
        NOVEL: (b) INTERIOR-GATED ZONE FLATTENING -- while the kokoschka_vibrating
        _surface_pass (s284 bonus) uses a colour-gradient interior mask for saturation
        boost, this pass uses a LUMINANCE-GRADIENT interior mask for SPATIAL
        FLATTENING (directional blur toward local mean). The mathematical quantity
        (interior_mask from luminance G_norm) and the operation (spatial smoothing,
        not saturation) are distinct from Stage 4 of the Kokoschka pass.

        Stage 3 ACID COLOUR PUSH (Grosz\'s Sickly Weimar Palette):
        Compute luminance L2 from R2/G2/B2.
        Identify yellow-green-dominant zones: where G2 > R2 and G2 > B2 and the
        luminance is in mid-range [0.35, 0.80]:
          green_dom = clip((G2 - _np.maximum(R2, B2)) / 0.15, 0, 1)
          mid_gate  = bell_gate(L2, 0.35, 0.80)
          acid_mask = green_dom * mid_gate
        Push acid pixels toward Grosz\'s signature yellow-green (acid_r/g/b =
        0.78/0.84/0.14 -- a jarring cadmium yellow-green):
          R3 = R2 + acid_mask * acid_strength * (acid_r - R2)
        Also push the darkest regions toward a deep warm dark (dark_push_r/g/b):
          dark_mask = clip((0.25 - L2) / 0.15, 0, 1)
          R3 += dark_mask * dark_push_strength * (dark_push_r - R3)
        NOVEL: (c) GREEN-DOMINANCE GATE FOR ACID PUSH -- no prior pass uses a
        per-channel DOMINANCE metric (G2 > max(R2, B2)) as a gate for a colour
        push. Prior colour-temperature passes use luminance thresholds alone
        (shadow_temperature_pass, repin_character_depth_pass Stages 2+3, etc.)
        or the Laplacian sign (form_curvature_tint_pass). The green-dominance
        gate identifies specifically chromatic zones in colour space, not in
        luminance space -- it will push a bright yellow-green sky differently
        from a similarly-bright warm ochre sky, selecting only the green-dominant
        portions for the acid push.

        Stage 4 GAMMA TONAL EXPANSION (Grosz\'s Harsh Fluorescent Clarity):
        Compute L3 from R3/G3/B3.
        Apply a power-law gamma expansion:
          L3_gamma = clip(L3, 0, 1)^gamma_value         [gamma_value = 0.80]
          scale = L3_gamma / max(L3, 1e-6)
          R4 = clip(R3 * scale, 0, 1)
        For gamma_value < 1.0: mid-tones are lifted (expanded upward), giving the
        canvas the harsh, fluorescent quality of Grosz\'s work. The scale factor
        preserves hue (all channels multiplied by the same ratio) while adjusting
        the tonal curve.
        NOVEL: (d) POWER-LAW GAMMA TONAL REMAPPING -- This is the FIRST pass in
        this engine to apply a power-law (gamma / exponent) tonal curve to the
        canvas. Prior passes that modify tone use: linear pushes (LERP toward
        a target), sigmoid mappings (none yet), unsharp mask (add high-freq detail),
        luminance-threshold gating (shadow/highlight zone selection). None applies
        C^gamma or a scale-factor-based power curve. The gamma operation is the
        classic non-linear tonal adjustment of photography and film, translated
        here into the painting domain to model the specific tonal signature of
        Grosz\'s mid-values. Gamma < 1 (expansion) models the effect of harsh,
        flat, even illumination (no shadows to hide the detail): everything is
        lit, everything is visible, no soft transition is allowed.
        """
        print("    Grosz Neue Sachlichkeit pass (195th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)

        # Stage 1: Signed-Gx directional cast shadow edge
        gsig = max(float(gradient_sigma), 0.5)
        Gx = _gf(L, sigma=gsig, order=[0, 1]).astype(_np.float32)
        Gy = _gf(L, sigma=gsig, order=[1, 0]).astype(_np.float32)
        G_mag = _np.sqrt(Gx * Gx + Gy * Gy).astype(_np.float32)

        gx_scale = max(float(_np.percentile(_np.abs(Gx), 85.0)), 1e-6)
        g_scale  = max(float(_np.percentile(G_mag,        80.0)), 1e-6)
        Gx_norm = _np.clip(Gx / gx_scale, -1.0, 1.0).astype(_np.float32)
        G_norm  = _np.clip(G_mag / g_scale, 0.0, 1.0).astype(_np.float32)

        # Shadow side: where luminance is decreasing left-to-right (Gx < 0)
        shadow_edge_mask = (_np.clip(-Gx_norm, 0.0, 1.0) * G_norm).astype(_np.float32)

        sd = float(shadow_darken)
        R1 = _np.clip(R * (1.0 - shadow_edge_mask * sd), 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G * (1.0 - shadow_edge_mask * sd), 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B * (1.0 - shadow_edge_mask * sd), 0.0, 1.0).astype(_np.float32)

        # Stage 2: Interior zone flattening (graphic unification)
        interior = _np.clip(1.0 - G_norm, 0.0, 1.0).astype(_np.float32)
        zsig = max(float(zone_sigma), 1.0)
        R_blur2 = _gf(R1, sigma=zsig).astype(_np.float32)
        G_blur2 = _gf(G1, sigma=zsig).astype(_np.float32)
        B_blur2 = _gf(B1, sigma=zsig).astype(_np.float32)
        fs = float(flat_strength)
        R2 = _np.clip(R1 + interior * fs * (R_blur2 - R1), 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + interior * fs * (G_blur2 - G1), 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + interior * fs * (B_blur2 - B1), 0.0, 1.0).astype(_np.float32)

        # Stage 3: Acid colour push (green-dominance gate + dark push)
        L2 = (0.299 * R2 + 0.587 * G2 + 0.114 * B2).astype(_np.float32)
        green_dom = _np.clip(
            (G2 - _np.maximum(R2, B2)) / max(0.10, 1e-6), 0.0, 1.0
        ).astype(_np.float32)
        lo_a, hi_a = 0.35, 0.80
        band_a = max(0.08, (hi_a - lo_a) * 0.25)
        lo_ramp_a = _np.clip((L2 - lo_a) / max(band_a, 1e-5), 0.0, 1.0).astype(_np.float32)
        hi_ramp_a = _np.clip((hi_a - L2) / max(band_a, 1e-5), 0.0, 1.0).astype(_np.float32)
        mid_gate_a = (lo_ramp_a * hi_ramp_a).astype(_np.float32)
        acid_mask = (green_dom * mid_gate_a).astype(_np.float32)

        astr = float(acid_strength)
        ar_, ag_, ab_ = float(acid_r), float(acid_g), float(acid_b)
        R3 = _np.clip(R2 + acid_mask * astr * (ar_ - R2), 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G2 + acid_mask * astr * (ag_ - G2), 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B2 + acid_mask * astr * (ab_ - B2), 0.0, 1.0).astype(_np.float32)

        # Dark push toward deep warm shadow
        dark_mask = _np.clip((0.25 - L2) / max(0.15, 1e-5), 0.0, 1.0).astype(_np.float32)
        dstr = float(dark_push_strength)
        dr_, dg_, db_ = float(dark_push_r), float(dark_push_g), float(dark_push_b)
        R3 = _np.clip(R3 + dark_mask * dstr * (dr_ - R3), 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G3 + dark_mask * dstr * (dg_ - G3), 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B3 + dark_mask * dstr * (db_ - B3), 0.0, 1.0).astype(_np.float32)

        # Stage 4: Gamma tonal expansion
        L3 = (0.299 * R3 + 0.587 * G3 + 0.114 * B3).astype(_np.float32)
        L3_safe = _np.maximum(L3, 1e-8)
        gv = float(gamma_value)
        L3_gamma = _np.clip(L3_safe, 0.0, 1.0) ** gv
        scale = (L3_gamma / L3_safe).astype(_np.float32)
        R4 = _np.clip(R3 * scale, 0.0, 1.0).astype(_np.float32)
        G4 = _np.clip(G3 * scale, 0.0, 1.0).astype(_np.float32)
        B4 = _np.clip(B3 * scale, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R4 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G4 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B4 - B) * op, 0.0, 1.0).astype(_np.float32)

        shadow_edge_px = int((shadow_edge_mask > 0.15).sum())
        acid_px        = int((acid_mask        > 0.05).sum())
        dark_px        = int((dark_mask        > 0.05).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Grosz Neue Sachlichkeit complete "
              f"(shadow_edge_px={shadow_edge_px}, acid_px={acid_px}, "
              f"dark_px={dark_px})")

'''

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8-sig") as f:
    src = f.read()

assert "grosz_neue_sachlichkeit_pass" not in src, \
    "grosz_neue_sachlichkeit_pass already exists in stroke_engine.py"

with open(SE_PATH, "a", encoding="utf-8") as f:
    f.write(GROSZ_PASS)

print("stroke_engine.py patched: grosz_neue_sachlichkeit_pass (195th mode) appended.")
