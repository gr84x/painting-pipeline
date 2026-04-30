"""Insert hilma_af_klint_biomorphic_pass and paint_shadow_bleed_pass
into stroke_engine.py (session 257).

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

BIOMORPHIC_PASS = """
    def hilma_af_klint_biomorphic_pass(
        self,
        ring_count:       float = 5.0,
        ring_amplitude:   float = 0.35,
        warm_push:        float = 0.08,
        cool_push:        float = 0.08,
        haze_sigma:       float = 18.0,
        haze_strength:    float = 0.10,
        opacity:          float = 0.78,
    ) -> None:
        r\"\"\"Hilma af Klint Biomorphic Abstraction -- session 257, 168th distinct mode.

        THREE-STAGE BIOMORPHIC ABSTRACTION INSPIRED BY AF KLINT'S
        "THE PAINTINGS FOR THE TEMPLE" (1906-1915):

        Hilma af Klint (1862-1944) was a Swedish artist who produced large-scale
        abstract paintings of extraordinary originality, keeping them private
        until after her death. Working in Stockholm from 1906, she painted
        nearly two hundred major canvases in "The Paintings for the Temple"
        series -- biomorphic forms, concentric ovals and spirals, interlocking
        warm and cool colour zones -- before Kandinsky exhibited his first
        abstract works. Her technical signatures: concentric oval/circular
        forms suggesting growth and cosmic cycles; warm amber/orange zones
        (symbolising earthly/masculine energy) opposed by cool blue/violet
        (cosmic/feminine energy); soft transitions where forms bleed into
        each other; luminous halos along form boundaries. The present pass
        derives three stages from these observations.

        Stage 1 CONCENTRIC RADIAL GROWTH RING FIELD: Compute the luminance-
        weighted centroid of the canvas (the visual centre of gravity):
          lum = 0.299R + 0.587G + 0.114B
          cy = sum(y * lum) / sum(lum),  cx = sum(x * lum) / sum(lum)
        From (cy, cx), compute the radial distance field r(y,x). Normalise by
        the mean distance to the four canvas corners so r_norm in [0, ~1].
        Apply a sine wave: ring_field = 0.5 * (1 + sin(2*pi * r_norm *
        ring_count)). This produces concentric growth rings at ring_count
        intervals between 0 and 1, peaking (1.0) at the ring centres and
        troughing (0.0) at the ring midpoints. Scale by ring_amplitude so
        the effect is proportional to the user parameter.
        NOVEL: (a) LUMINANCE-WEIGHTED CENTROID AS RADIAL RING ORIGIN WITH
        SINE-WAVE FREQUENCY RING FIELD -- first pass to derive the centroid
        of the image from the luminance distribution and use it as the origin
        of a sine-frequency radial ring field; no prior pass generates
        concentric sine-wave rings from a computed centroid; paint_warm_cool_
        separation_pass (s251) uses quadrant splits; no prior pass applies
        sin(2*pi*r_norm*freq) growth rings from a luminance-centroid origin.

        Stage 2 BIOMORPHIC ZONE COLOUR RESONANCE: Apply a chromatic warm/cool
        push to each ring zone. For each pixel, compute the ring_field value
        from Stage 1. Inner-ring pixels (ring_field > 0.5) receive a warm push:
          dR = +warm_push * (ring_field - 0.5) * 2
          dB = -warm_push * (ring_field - 0.5) * 2
        Outer-ring pixels (ring_field <= 0.5) receive a cool push:
          dR = -cool_push * (0.5 - ring_field) * 2
          dB = +cool_push * (0.5 - ring_field) * 2
        The push strength is proportional to distance from the 0.5 transition,
        so it is zero at ring boundaries and maximum at ring centres. This
        simulates af Klint's deliberate warm-inner / cool-outer zone pairing
        in her temple paintings.
        NOVEL: (b) RADIAL RING-FIELD DISTANCE-WEIGHTED CHROMATIC WARM/COOL ZONE
        RESONANCE -- first pass to apply chromatic warm/cool colour push with
        strength proportional to the ring_field value's distance from the
        midpoint (0.5), creating alternating warm/cool zones at sine-wave ring
        radii from the luminance centroid; paint_edge_temperature_pass (s256)
        uses hue-distance masks at warm/cool boundaries; no prior pass uses a
        radial sine-wave ring distance as the weight for a chromatic zone push.

        Stage 3 LUMINOUS BOUNDARY HAZE: Compute the absolute value of the
        gradient of the ring_field using central differences:
          gy = ring_field[2:,:] - ring_field[:-2,:]  (padded)
          gx = ring_field[:,2:] - ring_field[:,:-2]  (padded)
          ring_grad = sqrt(gy^2 + gx^2)
        The gradient magnitude is maximum exactly at the ring transition points
        (where sine crosses zero -- the 0.5 value line). Apply a wide Gaussian
        blur with sigma=haze_sigma to spread the gradient into a broad luminous
        zone. Normalise to [0, 1]. Apply as a multiplicative luminosity boost:
          scale = 1 + haze_strength * haze_field
          R *= scale, G *= scale, B *= scale  (clipped to [0,1])
        This simulates the characteristic af Klint boundary luminosity: a soft
        glow at each zone transition, as if the transition line itself radiates
        outward into both the warm and cool zones it separates.
        NOVEL: (c) GRADIENT MAGNITUDE OF RADIAL SINE-WAVE RING FIELD BLURRED
        INTO A WIDE LUMINOSITY HAZE AT RING ZONE TRANSITIONS -- first pass to
        compute the spatial gradient of a ring_field, apply wide Gaussian to
        spread the gradient into a broad glow zone, and use it as a
        multiplicative luminosity scale; no prior pass extracts ring boundary
        gradients and blurs them into a luminous haze; paint_edge_temperature_
        pass (s256) uses gradient of a hue-membership difference map for a
        channel push, not a luminosity scale; no prior pass uses ring boundary
        gradient as a multiplicative brightness field.

        ring_count     : Number of concentric rings (sine periods over r_norm).
        ring_amplitude : Amplitude of the ring field (0=flat, 1=full sine).
        warm_push      : Max warm channel push at ring peak (inner zone).
        cool_push      : Max cool channel push at ring trough (outer zone).
        haze_sigma     : Gaussian sigma for luminous boundary haze spread.
        haze_strength  : Multiplicative luminosity boost at ring boundaries.
        opacity        : Final composite opacity.
        \"\"\"
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Hilma af Klint Biomorphic pass (session 257, 168th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        # Cairo BGRA
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # Stage 1: Luminance-weighted centroid + radial ring field
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        lum_sum = float(lum.sum()) + 1e-8

        ys = _np.arange(h, dtype=_np.float32).reshape(-1, 1)
        xs = _np.arange(w, dtype=_np.float32).reshape(1, -1)

        cy = float((ys * lum).sum()) / lum_sum
        cx = float((xs * lum).sum()) / lum_sum

        # Radial distance field
        dy = ys - cy
        dx = xs - cx
        r_field = _np.sqrt(dy ** 2 + dx ** 2).astype(_np.float32)

        # Normalise by mean distance to canvas corners
        corners = [
            _np.sqrt(cy ** 2 + cx ** 2),
            _np.sqrt(cy ** 2 + (w - cx) ** 2),
            _np.sqrt((h - cy) ** 2 + cx ** 2),
            _np.sqrt((h - cy) ** 2 + (w - cx) ** 2),
        ]
        mean_corner_dist = float(_np.mean(corners)) + 1e-8
        r_norm = (r_field / mean_corner_dist).astype(_np.float32)

        # Sine-wave ring field in [0, 1]
        rc = float(ring_count)
        ring_field = (0.5 * (1.0 + _np.sin(2.0 * _np.pi * r_norm * rc))).astype(_np.float32)
        ring_amp = float(ring_amplitude)

        # Stage 2: Biomorphic zone colour resonance
        wp = float(warm_push)
        cp = float(cool_push)

        inner_weight = _np.clip((ring_field - 0.5) * 2.0, 0.0, 1.0).astype(_np.float32)
        outer_weight = _np.clip((0.5 - ring_field) * 2.0, 0.0, 1.0).astype(_np.float32)

        dR = (ring_amp * wp * inner_weight - ring_amp * cp * outer_weight).astype(_np.float32)
        dB = (-ring_amp * wp * inner_weight + ring_amp * cp * outer_weight).astype(_np.float32)

        r1 = _np.clip(r0 + dR, 0.0, 1.0).astype(_np.float32)
        g1 = g0.copy()
        b1 = _np.clip(b0 + dB, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Luminous boundary haze at ring transition zones
        gy = _np.pad(ring_field[2:, :] - ring_field[:-2, :], ((1, 1), (0, 0)), mode='edge')
        gx = _np.pad(ring_field[:, 2:] - ring_field[:, :-2], ((0, 0), (1, 1)), mode='edge')
        ring_grad = _np.sqrt(gy ** 2 + gx ** 2).astype(_np.float32)

        haze_field = _gf(ring_grad, sigma=float(haze_sigma)).astype(_np.float32)
        hm = haze_field.max()
        if hm > 1e-8:
            haze_field /= hm

        scale = (1.0 + float(haze_strength) * haze_field).astype(_np.float32)
        r2 = _np.clip(r1 * scale, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 * scale, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 * scale, 0.0, 1.0).astype(_np.float32)

        # Final composite
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

        print(f"    af Klint Biomorphic complete "
              f"(centroid=({cx:.0f},{cy:.0f}), rings={ring_count:.1f}, "
              f"haze_sigma={haze_sigma:.1f})")
"""

SHADOW_BLEED_PASS = """
    def paint_shadow_bleed_pass(
        self,
        shadow_threshold:  float = 0.35,
        bright_threshold:  float = 0.72,
        bleed_sigma:       float = 8.0,
        reflect_strength:  float = 0.14,
        warm_r:            float = 0.85,
        warm_g:            float = 0.60,
        warm_b:            float = 0.30,
        opacity:           float = 0.75,
    ) -> None:
        r\"\"\"Shadow Bleed -- Reflected Warm Light in Shadows -- session 257 improvement.

        THREE-STAGE REFLECTED SECONDARY ILLUMINATION IN SHADOW ZONES:

        Reflected light (or bounced light) is a fundamental principle in
        traditional oil painting: bright surfaces in the scene act as secondary
        light sources, casting diffuse light back into the shadow sides of
        adjacent objects. This effect is responsible for the characteristic
        warmth found deep in the shadows of Old Master paintings -- a warm
        amber glow visible on the underside of a chin or at the shaded edge of
        an arm, where the warm ground plane bounces light back. Without
        reflected light, shadows are flat, cold, and dead. With it, the dark
        areas are alive and connected to the light. This pass synthesises that
        effect by detecting the spatial relationship between bright and shadow
        regions and injecting a warm tint into the shadow boundary zone.

        Stage 1 SHADOW BOUNDARY PROXIMITY FIELD: Compute per-pixel luminance
        lum = 0.299R + 0.587G + 0.114B. Create a binary shadow mask:
          shadow_mask = (lum < shadow_threshold)  [0=lit, 1=shadow]
        Apply Gaussian blur with sigma=bleed_sigma to create a smooth shadow-
        boundary field that transitions from 1 inside deep shadows to 0
        outside, with a gradient falloff zone proportional to bleed_sigma.
        This field represents the proximity of each pixel to the shadow interior
        weighted by its depth within the shadow.
        NOVEL: (a) SMOOTH SHADOW BOUNDARY PROXIMITY FIELD FROM GAUSSIAN-BLURRED
        BINARY LUMINANCE-THRESHOLD SHADOW MASK -- first pass to derive a smooth
        shadow boundary proximity map by Gaussian-blurring a per-pixel binary
        shadow mask (not an edge-detection gradient), producing a continuous
        scalar field encoding depth-within-shadow proximity; paint_lost_found_
        edges_pass applies gradient-of-luminance for edge softening -- it does
        not threshold into binary shadow zones; no prior pass produces a smooth
        binary-mask-derived shadow proximity field.

        Stage 2 BRIGHT REGION PROXIMITY FIELD: Create a binary bright mask:
          bright_mask = (lum > bright_threshold)
        Apply identical Gaussian blur at bleed_sigma to create a smooth bright-
        source proximity field: each pixel's value encodes how near it is to a
        bright region (the secondary light source). The two fields independently
        capture the shadow interior and the bright source; their product in
        Stage 3 will identify only the zone where both are simultaneously true.
        NOVEL: (b) BRIGHT SOURCE PROXIMITY FIELD FROM GAUSSIAN-BLURRED BINARY
        LUMINANCE-THRESHOLD MASK AS SECONDARY LIGHT SOURCE INDICATOR -- first
        pass to independently derive a bright-source proximity field from a
        blurred binary luminance-threshold mask; the physical model is that any
        bright area acts as a secondary diffuse source; no prior pass derives
        a separate bright-source proximity field for use in a reflected-light
        injection; paint_halation_pass (s?) concentrates on a single bright
        point, not a spatial field of all bright areas.

        Stage 3 REFLECTED WARM LIGHT INJECTION AT SHADOW-BRIGHT INTERSECTION:
        Compute the reflected light injection field:
          reflect_field = shadow_proximity * bright_proximity
        This field is nonzero only in the zone that is simultaneously inside a
        shadow and near a bright surface -- the exact physical location where
        reflected secondary illumination occurs. Apply a warm tint:
          R += reflect_strength * reflect_field * (warm_r - r)
          G += reflect_strength * reflect_field * (warm_g - g)
          B += reflect_strength * reflect_field * (warm_b - b)
        This moves pixels in the reflected zone toward the warm colour
        (warm_r, warm_g, warm_b) at a rate proportional to reflect_field and
        reflect_strength. The warm default (0.85, 0.60, 0.30) simulates diffuse
        warm environmental light bouncing from a sunlit ground or warm wall.
        NOVEL: (c) REFLECTED WARM TINT INJECTION DRIVEN BY SHADOW-BRIGHT
        PROXIMITY PRODUCT AS REFLECTED SECONDARY LIGHT SIMULATION -- first pass
        to derive the reflected light injection zone as the PRODUCT of shadow
        and bright proximity fields and apply a directional colour nudge
        (toward warm_r/g/b) proportional to the product; no prior pass
        synthesises a spatial reflected-light zone from the product of two
        proximity fields; paint_warm_cool_separation_pass (s251) applies a
        global spatial push by quadrant; paint_edge_temperature_pass (s256)
        applies temperature contrast at hue-zone boundaries -- neither computes
        a proximity-product zone; this is the first pass to model secondary
        diffuse reflected illumination from bright surfaces into adjacent
        shadow zones.

        shadow_threshold : Luminance ceiling for shadow zone (0-1).
        bright_threshold : Luminance floor for bright (source) zone (0-1).
        bleed_sigma      : Gaussian sigma for proximity field smoothing.
        reflect_strength : Amplitude of warm tint injection at peak.
        warm_r/g/b       : RGB target colour of the reflected secondary light.
        opacity          : Final composite opacity.
        \"\"\"
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Shadow Bleed pass (session 257 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        # Cairo BGRA
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Shadow proximity field (blurred binary shadow mask)
        shadow_mask = (lum < float(shadow_threshold)).astype(_np.float32)
        shadow_prox = _gf(shadow_mask, sigma=float(bleed_sigma)).astype(_np.float32)
        sp_max = shadow_prox.max()
        if sp_max > 1e-8:
            shadow_prox /= sp_max

        # Stage 2: Bright-source proximity field (blurred binary bright mask)
        bright_mask = (lum > float(bright_threshold)).astype(_np.float32)
        bright_prox = _gf(bright_mask, sigma=float(bleed_sigma)).astype(_np.float32)
        bp_max = bright_prox.max()
        if bp_max > 1e-8:
            bright_prox /= bp_max

        # Stage 3: Product zone = reflected light injection field
        reflect_field = (shadow_prox * bright_prox).astype(_np.float32)
        rf_max = reflect_field.max()
        if rf_max > 1e-8:
            reflect_field /= rf_max

        rs = float(reflect_strength)
        wr = float(warm_r)
        wg = float(warm_g)
        wb = float(warm_b)

        r1 = _np.clip(r0 + rs * reflect_field * (wr - r0), 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 + rs * reflect_field * (wg - g0), 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 + rs * reflect_field * (wb - b0), 0.0, 1.0).astype(_np.float32)

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

        shadow_px = int(shadow_mask.sum())
        reflect_px = int((reflect_field > 0.1).sum())
        print(f"    Shadow Bleed complete (shadow_px={shadow_px}, "
              f"reflect_zone_px={reflect_px}, "
              f"reflect_strength={reflect_strength:.3f})")
"""

# ─── Injection anchors ────────────────────────────────────────────────────────

# Artist pass goes before kollwitz_charcoal_compression_pass
ARTIST_ANCHOR = "    def kollwitz_charcoal_compression_pass("

# Improvement pass goes after paint_edge_temperature_pass (end of file)
IMPROVE_ANCHOR = (
    "        boundary_px = int((boundary_zone > 0.1).sum())\n"
    "        print(f\"    Edge Temperature complete \"\n"
    "              f\"(boundary_px={boundary_px}, \"\n"
    "              f\"contrast_strength={contrast_strength:.3f})\")"
)

engine_path = os.path.join(REPO, "stroke_engine.py")
with open(engine_path, "r", encoding="utf-8") as f:
    src = f.read()

if "hilma_af_klint_biomorphic_pass" in src:
    print("hilma_af_klint_biomorphic_pass already present -- skipping.")
else:
    if ARTIST_ANCHOR not in src:
        print(f"ERROR: artist anchor not found in stroke_engine.py", file=sys.stderr)
        sys.exit(1)
    src = src.replace(ARTIST_ANCHOR, BIOMORPHIC_PASS + "\n" + ARTIST_ANCHOR, 1)
    print("Inserted hilma_af_klint_biomorphic_pass.")

if "paint_shadow_bleed_pass" in src:
    print("paint_shadow_bleed_pass already present -- skipping.")
else:
    if IMPROVE_ANCHOR not in src:
        print(f"ERROR: improvement anchor not found in stroke_engine.py", file=sys.stderr)
        sys.exit(1)
    src = src.replace(IMPROVE_ANCHOR, IMPROVE_ANCHOR + SHADOW_BLEED_PASS, 1)
    print("Inserted paint_shadow_bleed_pass.")

with open(engine_path, "w", encoding="utf-8") as f:
    f.write(src)

print("stroke_engine.py updated successfully.")
