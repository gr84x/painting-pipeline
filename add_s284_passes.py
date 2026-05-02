"""Insert paint_chromatic_shadow_shift_pass (s284 improvement) and
kokoschka_vibrating_surface_pass (195th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_chromatic_shadow_shift_pass (s284 improvement) ─────────────

CHROMATIC_SHADOW_SHIFT_PASS = '''
    def paint_chromatic_shadow_shift_pass(
        self,
        shadow_thresh:       float = 0.38,
        shadow_range:        float = 0.15,
        shadow_hue_shift:    float = 28.0,
        highlight_thresh:    float = 0.72,
        highlight_range:     float = 0.14,
        highlight_hue_shift: float = 12.0,
        shift_strength:      float = 0.80,
        opacity:             float = 0.75,
    ) -> None:
        r"""Chromatic Shadow Shift -- s284 improvement.

        THE PHYSICAL BASIS: HUE ROTATION IN SHADOW AND HIGHLIGHT ZONES

        In traditional oil painting, shadows are never simply dark versions of
        the lit colour. They shift in hue. This phenomenon -- called "chromatic
        shadow" in colour theory and "simultaneous contrast" in perceptual
        psychology -- has several independent causes:

        1. SKY-LIGHT HUE CONTAMINATION: Outdoor shadows receive skylight from
           above. Since sky radiates predominantly in the blue-violet range
           (Rayleigh scattering of short-wavelength photons), shadows on warm
           subjects (ochre stone, bare earth, human skin) are pushed toward
           cool blue-violet. A yellow-ochre wall in sunlight casts a shadow
           tinged with grey-blue from the sky.

        2. SIMULTANEOUS CONTRAST (SIMULTANEOUS COLOUR INDUCTION): Adjacent
           complementary colours appear mutually enhanced. The visual system,
           adapted to the dominant warm key-light, interprets shadow areas
           through a complementary filter. If the key light is warm (orange),
           the eye interprets the shadow zone as its complement (blue-violet).
           This is not an optical illusion; it is the mechanism by which the
           brain separates illumination from surface colour.

        3. REFLECTIVE LIGHT HUES: Shadows receive bounced light from nearby
           surfaces. A figure in a garden receives green-reflected light from
           grass on their shaded side. A harbour scene receives blue-green from
           water. The reflected hue contamination is always in the shadow zone.

        4. HIGHLIGHT WARM SHIFT: Conversely, direct-lit highlights -- where the
           key light strikes the surface most perpendicularly -- are shifted
           toward the key light's hue. For the common warm lighting conditions
           of classical and Expressionist painting (candle, incandescent, late
           afternoon sun), highlights shift toward amber-warm, slightly away
           from the cool middle tones.

        This shadow-cool / highlight-warm hue separation is described by:
          - Delacroix: "There are no neutral shadows; the shadow of a warm
            object is always tinged with its complement."
          - Cézanne: explicitly constructed his colour using hue opposition
            between the warm-lit facets and cool-shadow facets.
          - Kokoschka: used vivid cobalt and prussian blue in shadow passages
            alongside crimson in lit zones, creating a violent chromatic charge.
          - Sorolla: pushed shadow zones to deep cool blue-violet, lit zones
            to warm acid yellow-green, creating the Mediterranean light effect.

        NOVELTY ANALYSIS: FIRST PASS TO OPERATE IN HSV COLOUR SPACE.
        Every prior pass in this engine operates on RGB channels directly:
          - shadow_temperature_pass (s281): LERP toward warm/cool targets in RGB
          - contre_jour_rim_pass (s282): LERP at luminance boundaries in RGB
          - form_curvature_tint_pass (s283): LERP on convex/concave zones in RGB
          - repin_character_depth_pass (s283): warm/cool push in RGB with gates
          - All edge, texture, and structural passes: direct RGB manipulation
        No prior pass:
          (i)   converts the canvas from RGB to HSV colour space;
          (ii)  modifies the HUE ANGLE independently of saturation and value;
          (iii) applies a HUE ROTATION (angular shift of the hue circle) rather
                than a hue PUSH (LERP toward a fixed target hue);
          (iv)  converts back from HSV to RGB after modification.
        The distinction between a hue PUSH and a hue ROTATION is critical:
          PUSH: new_H = LERP(old_H, target_H, mask * strength)
                This moves all hues toward one fixed target; a red and a blue
                in shadow both move toward, say, blue-violet (0.67). The amount
                depends on their angular distance from the target.
          ROTATION: new_H = old_H + delta_H * mask * strength
                This shifts EVERY hue by the SAME angular amount. A red in
                shadow shifts +28 deg (toward orange-red, i.e., hue 28 deg).
                A blue in shadow shifts +28 deg (toward blue-violet). A green
                shifts +28 deg (toward yellow-green). The direction and magnitude
                are identical for all hues, but the RESULT is different because
                each starting hue is different. This preserves the hue
                RELATIONSHIPS between colours while shifting them uniformly
                around the wheel -- modelling the physics of a coloured ambient
                light field, which tints all colours equally.

        Stage 1 RGB TO HSV CONVERSION (First HSV operation in engine):
        For each pixel, convert (R, G, B) to (H, S, V) using standard formulas:
          V = max(R, G, B)
          delta = max(R, G, B) - min(R, G, B)
          S = delta / V                          (if V > 0, else 0)
          H computed from which channel is maximum:
            if max = R: H = ((G - B) / delta) mod 6
            if max = G: H = (B - R) / delta + 2
            if max = B: H = (R - G) / delta + 4
          H normalized to [0, 1] range (divide by 6)
        The value channel V serves as the luminance proxy for zone masking.
        NOVEL: (a) HSV CONVERSION -- first time this engine works in the
        HSV representation of colour rather than the raw RGB channels.

        Stage 2 SHADOW ZONE HUE ROTATION:
        shadow_mask = clip((shadow_thresh - V) / max(shadow_range, 0.01), 0, 1)
        H_new = (H + shadow_hue_shift / 360.0 * shadow_mask * shift_strength) mod 1.0
        The shadow zone (V < shadow_thresh) receives a positive hue rotation
        of shadow_hue_shift degrees. Default: +28 degrees shifts the hue
        toward warmer-complementary (orange-red shifts toward yellow, blue
        shifts toward blue-violet, green shifts toward cyan). This models
        the blue-sky ambient light component in outdoor shadows.
        NOVEL: (b) ANGULAR HUE ROTATION IN SHADOW ZONE -- no prior pass adds
        a fixed angular delta to the hue channel. Prior passes LERP toward a
        fixed colour target, which has the same effect for all hues (equal pull
        toward the same destination). The rotation preserves inter-hue
        relationships while shifting the collective hue cluster in the shadow.

        Stage 3 HIGHLIGHT ZONE HUE TILT:
        highlight_mask = clip((V - highlight_thresh) / max(highlight_range, 0.01), 0, 1)
        H_new = (H_new - highlight_hue_shift / 360.0 * highlight_mask * shift_strength) mod 1.0
        The highlight zone (V > highlight_thresh) receives a NEGATIVE rotation
        of highlight_hue_shift degrees. Default: -12 degrees shifts highlights
        slightly backward on the hue wheel (toward the key-light's natural hue).
        This creates the warm-highlight / cool-shadow hue opposition that
        characterizes luminous painting from Delacroix to Kokoschka.
        NOVEL: (c) OPPOSING ROTATIONS IN SHADOW AND HIGHLIGHT ZONES -- both
        zones receive hue rotations, but in opposite angular directions. The
        midtone zone (mid-V) receives no rotation, acting as the hue anchor.
        This three-zone structure (shadow rotated +, midtone unchanged,
        highlight rotated -) models the full chromatic temperature structure
        of naturally lit painting.

        Stage 4 HSV TO RGB CONVERSION AND COMPOSITE:
        Convert modified (H_new, S, V) back to (R_new, G_new, B_new) using
        the standard inverse HSV-to-RGB formula. Composite at opacity:
          R_out = R + (R_new - R) * opacity
        The shadow_px and highlight_px counts measure actual coverage.
        NOVEL: (d) ROUND-TRIP HSV PROCESSING PRESERVING SATURATION AND VALUE
        -- the pass modifies ONLY the hue channel; S and V are read from RGB
        and written back unchanged. This is structurally distinct from
        colour-temperature passes that modify all three RGB channels: the
        RGB-to-HSV decomposition allows surgical modification of one perceptual
        dimension (hue) without contaminating the others (brightness, chroma).
        """
        print("    Chromatic Shadow Shift pass (session 284 improvement)...")

        import numpy as _np

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        # Stage 1: RGB → HSV
        Cmax = _np.maximum(_np.maximum(R, G), B).astype(_np.float32)
        Cmin = _np.minimum(_np.minimum(R, G), B).astype(_np.float32)
        delta = (Cmax - Cmin).astype(_np.float32)

        V_ch = Cmax.copy()

        S_ch = _np.where(Cmax > 1e-8, delta / _np.maximum(Cmax, 1e-8), 0.0
                         ).astype(_np.float32)

        H_ch = _np.zeros((H_, W_), dtype=_np.float32)
        eps = 1e-8
        d_safe = _np.maximum(delta, eps)
        mask_r = (Cmax == R) & (delta > eps)
        mask_g = (Cmax == G) & (delta > eps)
        mask_b = (Cmax == B) & (delta > eps)
        H_ch = _np.where(mask_r, ((G - B) / d_safe) % 6.0, H_ch)
        H_ch = _np.where(mask_g, (B - R) / d_safe + 2.0, H_ch)
        H_ch = _np.where(mask_b, (R - G) / d_safe + 4.0, H_ch)
        H_ch = (H_ch / 6.0).astype(_np.float32)  # normalise to [0, 1]

        # Stage 2: Shadow zone hue rotation (positive shift)
        st  = float(shadow_thresh)
        sr  = max(float(shadow_range), 0.01)
        shadow_mask = _np.clip((st - V_ch) / sr, 0.0, 1.0).astype(_np.float32)

        sshift = float(shadow_hue_shift) / 360.0 * float(shift_strength)
        H_new = (H_ch + sshift * shadow_mask) % 1.0

        # Stage 3: Highlight zone hue tilt (negative shift)
        ht  = float(highlight_thresh)
        hr  = max(float(highlight_range), 0.01)
        highlight_mask = _np.clip((V_ch - ht) / hr, 0.0, 1.0).astype(_np.float32)

        hshift = float(highlight_hue_shift) / 360.0 * float(shift_strength)
        H_new = (H_new - hshift * highlight_mask) % 1.0

        # Stage 4: HSV → RGB
        h6   = H_new * 6.0
        i_ch = _np.floor(h6).astype(_np.int32) % 6
        f_ch = (h6 - _np.floor(h6)).astype(_np.float32)
        p_ch = (V_ch * (1.0 - S_ch)).astype(_np.float32)
        q_ch = (V_ch * (1.0 - f_ch * S_ch)).astype(_np.float32)
        t_ch = (V_ch * (1.0 - (1.0 - f_ch) * S_ch)).astype(_np.float32)

        R_new = _np.select(
            [i_ch == 0, i_ch == 1, i_ch == 2, i_ch == 3, i_ch == 4, i_ch == 5],
            [V_ch, q_ch, p_ch, p_ch, t_ch, V_ch]
        ).astype(_np.float32)
        G_new = _np.select(
            [i_ch == 0, i_ch == 1, i_ch == 2, i_ch == 3, i_ch == 4, i_ch == 5],
            [t_ch, V_ch, V_ch, q_ch, p_ch, p_ch]
        ).astype(_np.float32)
        B_new = _np.select(
            [i_ch == 0, i_ch == 1, i_ch == 2, i_ch == 3, i_ch == 4, i_ch == 5],
            [p_ch, p_ch, t_ch, V_ch, V_ch, q_ch]
        ).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R_new - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G_new - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B_new - B) * op, 0.0, 1.0).astype(_np.float32)

        shadow_px    = int((shadow_mask    > 0.05).sum())
        highlight_px = int((highlight_mask > 0.05).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Chromatic Shadow Shift complete "
              f"(shadow_px={shadow_px}, highlight_px={highlight_px})")

'''

# ── Pass 2: kokoschka_vibrating_surface_pass (195th mode) ────────────────────

KOKOSCHKA_VIBRATING_SURFACE_PASS = '''
    def kokoschka_vibrating_surface_pass(
        self,
        gradient_sigma:      float = 1.1,
        edge_percentile:     float = 80.0,
        glow_lo:             float = 0.35,
        glow_hi:             float = 0.70,
        glow_r:              float = 0.94,
        glow_g:              float = 0.82,
        glow_b:              float = 0.52,
        glow_strength:       float = 0.22,
        edge_r:              float = 0.28,
        edge_g:              float = 0.50,
        edge_b:              float = 0.90,
        edge_strength:       float = 0.28,
        sat_boost:           float = 0.30,
        opacity:             float = 0.84,
    ) -> None:
        r"""Kokoschka Vibrating Surface (Austrian Expressionism) -- 195th mode.

        OSKAR KOKOSCHKA (1886-1980) -- AUSTRIAN EXPRESSIONIST;
        PAINTER OF THE INNER VISION AND THE AGITATED SOUL:

        Oskar Kokoschka was born in Pöchlarn, Austria in 1886, the son of a
        Czech goldsmith. He studied at the Vienna School of Arts and Crafts
        from 1904, initially working in the Wiener Werkstätte decorative arts
        movement. By 1908, exposed to the psychoanalytic climate of Freudian
        Vienna, Kokoschka broke decisively with decorative art and began his
        series of psychological portraits that brought him international
        notoriety and scandal.

        His early Vienna portraits -- of Adolf Loos, Karl Kraus, Herwarth
        Walden, Else Lasker-Schüler -- are among the most intense psychological
        investigations in Western painting. Kokoschka did not paint appearances.
        He believed that the surface of the face was merely a mask obscuring
        the inner psychic reality, and that the painter's task was to strip
        away that mask through obsessive observation until the interior life
        of the sitter became visible. His sitters frequently emerged looking
        haggard, disturbed, and exposed -- though Kokoschka insisted he was
        revealing their truest nature.

        His most famous single painting, "Die Windsbraut" ("The Bride of the
        Wind," also known as "The Tempest," 1913-14), is a monumental self-
        portrait with his lover Alma Mahler, the two figures swirling in a
        shell-shaped vortex of swirling blue and violet air, suspended above
        an alpine landscape. The painting is simultaneously a personal
        confession and a technical manifesto: all form is in constant agitation,
        all surfaces vibrate, the boundary between body and world dissolves.

        After severe wounds suffered in World War I, Kokoschka moved through
        Dresden, Vienna again, Paris, London (where he spent the war years),
        Salzburg and finally Villeneuve-sur-Mer on Lake Geneva, where he died
        in 1980 at the age of 93. His landscape paintings of Dresden, the
        Prague panorama, Constantinople from the Galata Bridge, and the Aegean
        coastline share a panoramic, vibrating energy: the entire landscape
        seems to breathe and shift, observed from an elevated position that
        Kokoschka described as "the cosmic viewpoint."

        KOKOSCHKA'S FIVE DEFINING TECHNICAL CHARACTERISTICS:

        1. THE VIBRATING BRUSHSTROKE: Kokoschka applied paint in short, agitated,
           comma-like or spiral strokes that never settled into a smooth surface.
           The strokes remain individually legible, creating a physical texture
           of restless motion. Even in quiet areas of sky or water, the strokes
           impart a trembling quality. Kokoscha called this the "heartbeat of
           the paint."

        2. CHROMATIC EDGE ACCENTUATION: At the edges between forms -- where
           flesh meets air, where rock meets water, where building meets sky --
           Kokoschka applied vivid, often unexpected colour accents. Not the
           dark outlines of Beckmann or the blurred transitions of the
           Impressionists, but vivid cobalt blues, prussian violets, raw siennas
           at the boundary zone. These chromatic edge accents function like
           the leading lines in stained glass, separating colour zones with
           vivid, charged boundaries.

        3. INNER CHROMATIC GLOW: Kokoschka believed in an inner light latent
           in subjects -- a warmth or luminosity emanating from the subject
           itself rather than reflected from an external source. He achieved
           this by enriching the mid-luminance zones -- the broad middle register
           between the extremes of deep shadow and specular highlight -- with
           a characteristic warm amber-ochre-cream. The skin of his subjects
           glows from within; the walls of his cities emit light rather than
           merely reflecting it.

        4. AGGRESSIVE CHROMATIC SATURATION IN FORM INTERIORS: Within the bounded
           areas of any form (away from the edges), Kokoschka pushed colour to
           its maximum chroma. He regarded desaturated, grey-toned painting as
           morally timid. Every zone of his canvases carries its full chromatic
           load: a blue zone is electric cobalt, not powder blue; a yellow zone
           is cadmium-burning, not buff.

        5. THE RGB MULTI-CHANNEL GRADIENT (NOVELTY BASIS): Kokoschka perceived
           colour transitions independently of tonal transitions. A red-to-green
           boundary at equal luminance (isobrightness colour contrast) was, for
           him, as significant an edge as a light-to-dark boundary. His eyes
           registered chromatic contrast (opposition in hue and saturation at
           similar value) as equal in structural importance to tonal contrast.
           The engine implements this by computing the GRADIENT MAGNITUDE across
           all three RGB channels simultaneously, detecting colour-domain edges
           that pure luminance gradient would miss.

        THE GREAT WORKS:
        "Die Windsbraut (The Bride of the Wind)" (1913-14): A monumental (181 x
        220 cm) swirling composition of two figures in a shell-vortex of blue
        air above an alpine landscape. The entire surface vibrates and rotates.

        "Portrait of Adolf Loos" (1909): The architect, stripped bare of social
        facade, rendered in trembling energetic strokes that make the sitter
        seem barely contained within his skin.

        "Prague -- View from the Moldau Bridge" (1934): A panoramic cityscape
        seen from an elevated position with Kokoschka's characteristic cosmic
        viewpoint -- the entire city breathes and shifts in electric afternoon light.

        "Constantinople" (1929): The Bosporus, the minarets, the crowded harbour
        seen from the Galata Bridge at high noon -- a tumultuous, jewel-coloured
        landscape that makes the viewer feel both above and within the scene.

        "Portrait of a Young Woman (Hanna)" (1932): The subject's face appears
        to vibrate with inner light -- the warm amber skin against vivid cobalt
        background creates the chromatic edge accentuation that defines
        Kokoschka's mature portrait style.

        Stage 1 RGB MULTI-CHANNEL COLOUR GRADIENT EXTRACTION:
        Compute spatial derivatives of each colour channel independently:
          for C in {R, G, B}:
            Gc_x = GaussianDerivative(C, sigma=gradient_sigma, order=[0,1])
            Gc_y = GaussianDerivative(C, sigma=gradient_sigma, order=[1,0])
        Combine into a total colour gradient magnitude:
          color_grad = sqrt( (GR_x^2 + GR_y^2) + (GG_x^2 + GG_y^2) + (GB_x^2 + GB_y^2) )
        This measures the rate of change of the full colour vector in space,
        not just of the luminance scalar. Edges between equally-bright surfaces
        of different colour (e.g., red fabric against green foliage at matched
        luminance) are detected by this measure and missed by luminance gradient.
        Normalise: color_grad_norm = clip(color_grad / percentile(color_grad, edge_percentile), 0, 1)
        Build edge_mask from color_grad_norm.
        NOVEL: (a) RGB MULTI-CHANNEL COLOUR GRADIENT -- this is the first pass
        in this engine to compute and use the COLOUR GRADIENT MAGNITUDE across
        all three channels. Every prior gradient computation uses luminance:
          L = 0.299R + 0.587G + 0.114B
          Gx, Gy from L (repin_character_depth_pass Stage 1, Stage 4;
                          savrasov_lyrical_mist_pass Stage 3;
                          contre_jour_rim_pass Stage 2;
                          form_curvature_tint_pass Stage 2;
                          lost_found_edges_pass; paint_shadow_temperature_pass)
        The colour gradient detects edges that exist in hue/saturation space
        but not in luminance space, capturing a class of boundaries that all
        prior passes miss entirely.

        Stage 2 INNER CHROMATIC GLOW (Kokoschka's Emanating Inner Light):
        Compute luminance L from Stage-1 channels R, G, B.
        Apply a bell-gate in the mid-luminance zone [glow_lo, glow_hi]:
          lo_ramp = clip((L - glow_lo) / max(band, 1e-5), 0, 1)
          hi_ramp = clip((glow_hi - L) / max(band, 1e-5), 0, 1)
          glow_mask = lo_ramp * hi_ramp
        Within the interior of forms (zone_mask = 1 - sqrt(edge_mask)):
          combined_mask = glow_mask * (1 - sqrt(edge_mask))
        Push toward Kokoschka's warm amber inner-glow (glow_r/g/b = 0.94/0.82/0.52):
          R1 = R + combined_mask * glow_strength * (glow_r - R)
        The zone_mask restriction ensures the inner glow applies within forms,
        not at their chromatic edges, creating the interior luminosity without
        contaminating the edge coloration of Stage 3.
        NOVEL: (b) INTERIOR-GATED MID-LUMINANCE WARM GLOW -- Prior mid-luminance
        bell-gate passes (savrasov_lyrical_mist_pass, repin_character_depth_pass)
        apply the mid-gate uniformly across the entire canvas. This pass adds a
        second gate from Stage 1: the colour gradient edge mask. The result is a
        glow that applies to INTERIOR ZONES only (low colour-gradient) and is
        suppressed at edges. This two-gate combination (luminance bell AND colour
        gradient complement) is the first dual-gate structure in any pass.

        Stage 3 VIVID CHROMATIC EDGE ACCENT (Kokoschka's Charged Boundaries):
        Use the colour gradient edge_mask from Stage 1.
        Push high-gradient pixels toward Kokoschka's characteristic cobalt edge
        accent (edge_r/g/b = 0.28/0.50/0.90 -- vivid cobalt blue):
          R2 = R1 + edge_mask * edge_strength * (edge_r - R1)
          G2 = G1 + edge_mask * edge_strength * (edge_g - G1)
          B2 = B1 + edge_mask * edge_strength * (edge_b - B1)
        NOVEL: (c) COLOUR-GRADIENT-GATED CHROMATIC PUSH AT EDGES -- This is the
        first pass to:
          (i)  use the colour gradient (not luminance gradient) to locate edges;
          (ii) apply a COLOURED push (not darkening, not sharpening) at those edges.
        Prior edge-modifying passes:
          - lost_found_edges_pass: alternately sharpens and blurs using luminance
            gradient; does not apply a colour push.
          - repin_character_depth_pass Stage 4: sharpens using luminance gradient.
          - paint_contre_jour_rim_pass: applies warm rim and cool edge at luminance
            boundaries, using dilated luminance masks.
        None uses colour-gradient edge detection + chromatic colour push together.

        Stage 4 INTERIOR SATURATION SURGE (Expressionist Full-Chroma Interiors):
        Build interior_mask = 1 - clip(edge_mask, 0, 1)  (inverted edge mask).
        Apply saturation boost within low-gradient interior zones:
          grey = (R2 + G2 + B2) / 3.0
          sat_boost_R = (R2 - grey) * sat_boost
          R3 = clip(R2 + interior_mask * sat_boost_R, 0, 1)
        NOVEL: (d) INTERIOR-GATED SATURATION BOOST COMPLEMENTARY TO EDGE TREATMENT
        -- This stage is the structural complement to Stage 3: edges are pushed
        toward a specific chromatic accent colour (Stage 3), while interiors are
        pushed toward higher chroma of their OWN existing colour (Stage 4).
        The combination creates the Kokoschka opposition: edges charged with an
        external chromatic impulse (cobalt accent), interiors charged with the
        maximum expression of their own intrinsic colour. No prior pass implements
        this complementary edge-vs-interior colour treatment. The closest prior pass
        (paint_focal_vignette_pass, s278) applies a radial spatial gate, not one
        derived from local colour gradient structure.
        """
        print("    Kokoschka Vibrating Surface pass (195th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H_, W_ = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H_, W_, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        # Stage 1: RGB multi-channel colour gradient
        gsig = max(float(gradient_sigma), 0.5)
        GR_x = _gf(R, sigma=gsig, order=[0, 1]).astype(_np.float32)
        GR_y = _gf(R, sigma=gsig, order=[1, 0]).astype(_np.float32)
        GG_x = _gf(G, sigma=gsig, order=[0, 1]).astype(_np.float32)
        GG_y = _gf(G, sigma=gsig, order=[1, 0]).astype(_np.float32)
        GB_x = _gf(B, sigma=gsig, order=[0, 1]).astype(_np.float32)
        GB_y = _gf(B, sigma=gsig, order=[1, 0]).astype(_np.float32)

        color_grad = _np.sqrt(
            GR_x * GR_x + GR_y * GR_y +
            GG_x * GG_x + GG_y * GG_y +
            GB_x * GB_x + GB_y * GB_y
        ).astype(_np.float32)

        ep = float(edge_percentile)
        cg_scale = max(float(_np.percentile(color_grad, ep)), 1e-6)
        edge_mask = _np.clip(color_grad / cg_scale, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Inner chromatic glow (interior-gated, mid-luminance bell gate)
        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)
        gl = float(glow_lo)
        gh = float(glow_hi)
        band = max(0.08, (gh - gl) * 0.25)
        lo_ramp = _np.clip((L - gl)  / max(band, 1e-5), 0.0, 1.0).astype(_np.float32)
        hi_ramp = _np.clip((gh - L) / max(band, 1e-5), 0.0, 1.0).astype(_np.float32)
        glow_mask = (lo_ramp * hi_ramp).astype(_np.float32)

        interior = _np.clip(1.0 - _np.sqrt(edge_mask), 0.0, 1.0).astype(_np.float32)
        combined_glow = (glow_mask * interior).astype(_np.float32)

        gstr = float(glow_strength)
        gr_, gg_, gb_ = float(glow_r), float(glow_g), float(glow_b)
        R1 = _np.clip(R + combined_glow * gstr * (gr_ - R), 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + combined_glow * gstr * (gg_ - G), 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + combined_glow * gstr * (gb_ - B), 0.0, 1.0).astype(_np.float32)

        # Stage 3: Vivid chromatic edge accent (cobalt blue at colour-gradient edges)
        estr = float(edge_strength)
        er_, eg_, eb_ = float(edge_r), float(edge_g), float(edge_b)
        R2 = _np.clip(R1 + edge_mask * estr * (er_ - R1), 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + edge_mask * estr * (eg_ - G1), 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + edge_mask * estr * (eb_ - B1), 0.0, 1.0).astype(_np.float32)

        # Stage 4: Interior saturation surge (complementary to edge treatment)
        interior_mask = _np.clip(1.0 - edge_mask, 0.0, 1.0).astype(_np.float32)
        grey2 = ((R2 + G2 + B2) / 3.0).astype(_np.float32)
        sb = float(sat_boost)
        R3 = _np.clip(R2 + interior_mask * (R2 - grey2) * sb, 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G2 + interior_mask * (G2 - grey2) * sb, 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B2 + interior_mask * (B2 - grey2) * sb, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R3 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G3 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B3 - B) * op, 0.0, 1.0).astype(_np.float32)

        edge_px     = int((edge_mask     > 0.20).sum())
        glow_px     = int((combined_glow > 0.05).sum())
        interior_px = int((interior_mask > 0.50).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Kokoschka Vibrating Surface complete "
              f"(edge_px={edge_px}, glow_px={glow_px}, interior_px={interior_px})")

'''

# ── Append both passes to stroke_engine.py ───────────────────────────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8-sig") as f:
    src = f.read()

assert "paint_chromatic_shadow_shift_pass" not in src, \
    "paint_chromatic_shadow_shift_pass already exists in stroke_engine.py"
assert "kokoschka_vibrating_surface_pass" not in src, \
    "kokoschka_vibrating_surface_pass already exists in stroke_engine.py"

with open(SE_PATH, "a", encoding="utf-8") as f:
    f.write(CHROMATIC_SHADOW_SHIFT_PASS)
    f.write(KOKOSCHKA_VIBRATING_SURFACE_PASS)

print("stroke_engine.py patched: paint_chromatic_shadow_shift_pass (s284 improvement)"
      " + kokoschka_vibrating_surface_pass (195th mode) appended.")
