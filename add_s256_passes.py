"""Insert kollwitz_charcoal_compression_pass and paint_edge_temperature_pass
into stroke_engine.py (session 256).

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

CHARCOAL_COMPRESSION_PASS = """
    def kollwitz_charcoal_compression_pass(
        self,
        dark_power:         float = 1.55,
        smear_angle_deg:    float = 38.0,
        smear_sigma_along:  float = 5.0,
        smear_sigma_across: float = 0.6,
        smear_strength:     float = 0.55,
        lift_density:       float = 0.014,
        lift_radius:        float = 2.5,
        lift_strength:      float = 0.22,
        opacity:            float = 0.82,
        seed:               int   = 256,
    ) -> None:
        r\"\"\"Käthe Kollwitz Charcoal Compression -- session 256, 167th distinct mode.

        THREE-STAGE CHARCOAL MEDIUM SIMULATION INSPIRED BY KOLLWITZ:

        Stage 1 DARK TONAL COMPRESSION: Apply a power-law luminance
        compression that pushes the tonal range toward the dark half of the
        scale, simulating charcoal's inability to produce luminance above the
        raw paper value. Compute per-pixel luminance:
        lum = 0.299R + 0.587G + 0.114B. Apply power-law: new_lum =
        lum ** dark_power. When dark_power > 1 the midtones and lights
        collapse toward the dark end (0.5 ** 1.55 ≈ 0.34). Compute per-channel
        luminance scale: scale = new_lum / (lum + 1e-6), clamped to [0.05, 4.0].
        Apply to all channels. This makes the few pale passages read with
        heightened contrast against the surrounding compressed dark mass.
        NOVEL: (a) POWER-LAW LUMINANCE COMPRESSION TOWARD THE DARK HALF OF THE
        TONAL SCALE AS A CHARCOAL MEDIUM SIMULATION -- first pass to apply a
        power-law exponent > 1 to the luminance field to push the tonal
        distribution toward darkness, simulating charcoal's fundamental
        constraint that the paper surface provides the ceiling; no prior pass
        applies a direct luminance power-law for dark-range compression;
        paint_tonal_key_pass (s255) applies sigmoid remapping; no prior pass
        uses power-law lum ** dark_power for directional dark compression.

        Stage 2 DIRECTIONAL CHARCOAL SMEAR: Simulate the broad lateral sweep
        of the charcoal stick or the side of the hand along the gesture axis.
        Rotate the Stage 1 image by -smear_angle_deg degrees (scipy.ndimage
        .rotate, reshape=False, mode='reflect'). Apply an anisotropic Gaussian
        blur with sigma=(smear_sigma_along, smear_sigma_across): long sigma
        along the y-axis (which, in the rotated frame, aligns with the smear
        direction) and short sigma across the x-axis to preserve detail
        perpendicular to the stroke. Rotate back by +smear_angle_deg degrees.
        Blend with Stage 1 at smear_strength: result = (1 - smear_strength) *
        stage1 + smear_strength * smeared. The directionality creates the
        gestural sweep quality in Kollwitz's broad mid-tone marks.
        NOVEL: (b) ANGLE-PARAMETERISED ANISOTROPIC SMEAR VIA PAIRED IMAGE
        ROTATION WITH ASYMMETRIC GAUSSIAN -- first pass to implement a
        directional smear by rotating the canvas to align the smear axis with
        the filter's long axis (sigma_along >> sigma_across), applying the
        blur, then rotating back; no prior pass uses paired forward/back image
        rotation to achieve anisotropic directional smear at an arbitrary
        angle; wyeth_tempera_drybrush_pass (s255) uses asymmetric sigma in a
        fixed orientation without rotation.

        Stage 3 CHARCOAL HIGHLIGHT LIFT: In charcoal the brightest passages
        are produced by erasing, not by applying a light pigment. Simulate
        kneaded-eraser lifting at sparse random locations in the upper tonal
        zone. Using seeded RNG, generate a uniform random field; threshold at
        1 - lift_density to activate lift_density fraction of pixels.
        Apply Gaussian blur with sigma=lift_radius to create soft lift zones
        (the eraser removes charcoal from a small area, softening the boundary
        of the lifted spot). Weight the lift by how dark the pixel currently
        is: lift_amount = lift_strength * lift_field * (1 - new_lum), where
        new_lum is the current luminance from Stage 2; this ensures the lift
        is strongest where the charcoal is darkest and produces the smallest
        brightening where the paper is already near-white (no charcoal to
        remove). Add lift_amount to all channels.
        NOVEL: (c) SPARSE ERASER-LIFT ZONES WEIGHTED BY LOCAL DARKNESS AS
        CHARCOAL HIGHLIGHT SIMULATION -- first pass to generate sparse lifted-
        highlight zones (Gaussian-blurred sparse binary field) where the lift
        brightness is inversely proportional to the current luminance,
        simulating kneaded-eraser charcoal removal; no prior pass models the
        erasure process (darkness-weighted additive brightening from a sparse
        Gaussian-blurred field); wyeth_tempera_drybrush_pass (s255) stage 3
        uses a sparse field additively but in a tonal-transition zone for
        fiber traces, not as an eraser-lift simulation, and does not weight by
        (1 - lum); no prior pass simulates charcoal removal with a
        darkness-weighted sparse lift field.

        dark_power         : Power-law exponent (> 1 = compress toward dark).
        smear_angle_deg    : Smear direction in degrees (0 = horizontal).
        smear_sigma_along  : Gaussian sigma along smear axis (long blur).
        smear_sigma_across : Gaussian sigma across smear axis (short blur).
        smear_strength     : Blend fraction of smeared image (0=no smear).
        lift_density       : Fraction of pixels activated as lift zones.
        lift_radius        : Gaussian blur radius for lift zone softening.
        lift_strength      : Peak brightness added at lift zones.
        opacity            : Final composite opacity.
        seed               : RNG seed for reproducibility.
        \"\"\"
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf
        from scipy.ndimage import rotate as _rot

        print("    Kollwitz Charcoal Compression pass (session 256, 167th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        # Cairo BGRA order
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # Stage 1: Dark tonal compression via power-law
        lum0 = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        new_lum1 = _np.power(_np.clip(lum0, 0.0, 1.0), float(dark_power)).astype(_np.float32)
        scale1 = _np.clip(new_lum1 / (lum0 + 1e-6), 0.05, 4.0).astype(_np.float32)
        r1 = _np.clip(r0 * scale1, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * scale1, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * scale1, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Directional charcoal smear via rotation + asymmetric Gaussian
        ang = float(smear_angle_deg)
        sa  = float(smear_sigma_along)
        sc  = float(smear_sigma_across)

        def _smear_channel(ch):
            rotated  = _rot(ch, angle=-ang, reshape=False, mode='reflect',
                            order=1).astype(_np.float32)
            blurred  = _gf(rotated, sigma=(sa, sc)).astype(_np.float32)
            unrotated = _rot(blurred, angle=ang, reshape=False, mode='reflect',
                             order=1).astype(_np.float32)
            return _np.clip(unrotated, 0.0, 1.0)

        sm = float(smear_strength)
        r2 = _np.clip((1.0 - sm) * r1 + sm * _smear_channel(r1), 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip((1.0 - sm) * g1 + sm * _smear_channel(g1), 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip((1.0 - sm) * b1 + sm * _smear_channel(b1), 0.0, 1.0).astype(_np.float32)

        # Stage 3: Sparse eraser-lift zones weighted by local darkness
        rng = _np.random.default_rng(int(seed))
        sparse = (rng.uniform(0.0, 1.0, size=(h, w)) > (1.0 - float(lift_density))).astype(_np.float32)
        lift_field = _gf(sparse, sigma=float(lift_radius)).astype(_np.float32)
        if lift_field.max() > 1e-8:
            lift_field /= lift_field.max()

        lum2 = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)
        lift_amount = float(lift_strength) * lift_field * (1.0 - lum2)
        r3 = _np.clip(r2 + lift_amount, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 + lift_amount, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 + lift_amount, 0.0, 1.0).astype(_np.float32)

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

        lifted_px = int((lift_field > 0.05).sum())
        print(f"    Kollwitz Charcoal complete (dark_power={dark_power:.2f}, "
              f"smear_angle={smear_angle_deg:.0f}°, "
              f"lift_zones={lifted_px}px)")
"""

EDGE_TEMPERATURE_PASS = """
    def paint_edge_temperature_pass(
        self,
        warm_hue_center:   float = 0.05,
        warm_hue_width:    float = 0.18,
        cool_hue_center:   float = 0.60,
        cool_hue_width:    float = 0.20,
        gradient_zone_px:  float = 3.5,
        contrast_strength: float = 0.14,
        opacity:           float = 0.72,
    ) -> None:
        r\"\"\"Edge Temperature Contrast -- session 256 improvement pass.

        THREE-STAGE SIMULTANEOUS TEMPERATURE CONTRAST AT WARM/COOL BOUNDARIES:

        Addresses the fundamental painting observation that warm and cool
        colour zones, when adjacent, each appear more extreme at their shared
        boundary than they do in isolation -- a phenomenon called simultaneous
        colour contrast. Painters (Chevreul, Albers, Itten) have used this
        deliberately: warm-lit areas appear warmer when their shadow edge
        abuts a cool-toned zone, and cool shadows appear cooler when they
        meet warm light. This pass detects the spatial boundaries between warm-
        and cool-hued regions and applies a bidirectional temperature push
        that intensifies both sides of each boundary.

        Stage 1 WARM/COOL HSV HUE MEMBERSHIP MASKS: Convert each RGB pixel to
        HSV. Compute a soft warm-hue membership mask using a Gaussian bell over
        hue distance from warm_hue_center (wrapping around the hue circle):
          dist_w = min(|H - warm_hue_center|, 1 - |H - warm_hue_center|)
          warm_mask = exp(-(dist_w / warm_hue_width) ** 2)
        Compute cool_mask identically for cool_hue_center and cool_hue_width.
        Both masks are in [0, 1]; saturated pixels contribute more weight
        (multiply by S) so achromatic pixels do not trigger false boundaries.
        NOVEL: (a) SATURATION-WEIGHTED SOFT HSV HUE-MEMBERSHIP MASKS FOR
        SIMULTANEOUS WARM/COOL TEMPERATURE CONTRAST -- first pass to compute
        per-pixel warm and cool hue membership via wrapped Gaussian bell over
        hue distance, weighted by HSV saturation; no prior pass builds dual
        hue-membership masks from HSV hue-angle distance for warm/cool
        temperature operations; paint_warm_cool_separation_pass (s251) applies
        a global spatial warm/cool push without per-pixel hue membership
        detection; no prior pass uses saturation-weighted Gaussian hue-distance
        masks to localise a temperature operation to genuinely chromatic pixels.

        Stage 2 TEMPERATURE BOUNDARY GRADIENT ZONE: Compute the finite-
        difference gradient magnitude of (warm_mask - cool_mask):
          diff = warm_mask - cool_mask  (in [-1, 1])
          gy = diff[2:, :] - diff[:-2, :]  (central difference, rows)
          gx = diff[:, 2:] - diff[:, :-2]  (central difference, cols)
          grad_mag = sqrt(gy_padded^2 + gx_padded^2)
        Apply Gaussian blur with sigma=gradient_zone_px to spread the detected
        boundary into a smooth zone of influence. Normalise to [0, 1].
        NOVEL: (b) GRADIENT MAGNITUDE OF THE WARM-COOL MEMBERSHIP DIFFERENCE
        MAP SMOOTHED INTO A TEMPERATURE BOUNDARY ZONE -- first pass to detect
        spatial boundaries between warm and cool hue regions via the gradient
        of the signed membership difference (warm_mask - cool_mask), then
        spread the boundary into a smooth zone via Gaussian blur; no prior pass
        computes the gradient of a hue-membership difference map to locate
        warm/cool boundaries; paint_lost_found_edges_pass detects luminance
        edges; no prior pass uses hue-space gradient detection.

        Stage 3 BIDIRECTIONAL SIMULTANEOUS TEMPERATURE CONTRAST: At each
        pixel, compute a signed temperature signal:
          temp_signal = contrast_strength * boundary_zone *
                        (warm_mask - cool_mask)
        Apply as a bidirectional red-blue push:
          R += temp_signal * 0.12
          B -= temp_signal * 0.08
        When temp_signal > 0 (warm-zone boundary pixel) this pushes R up and
        B down (warmer). When temp_signal < 0 (cool-zone boundary pixel) R
        goes down and B goes up (cooler). Pixels far from any warm/cool
        boundary (boundary_zone ≈ 0) receive no push, preserving the interior
        of zones unchanged.
        NOVEL: (c) BIDIRECTIONAL SIMULTANEOUS TEMPERATURE CONTRAST PUSH DRIVEN
        BY SIGNED HUE-MEMBERSHIP DIFFERENCE WEIGHTED BY SMOOTH BOUNDARY ZONE
        -- first pass to apply a single signed R/B push derived from
        (warm_mask - cool_mask) * boundary_zone, pushing warm-side pixels
        warmer and cool-side pixels cooler simultaneously in one operation;
        paint_warm_cool_separation_pass (s251) applies a global spatial push
        indexed by image quadrant; no prior pass applies bidirectional
        simultaneous temperature contrast at per-pixel hue boundaries using
        a smooth boundary-zone weighting.

        warm_hue_center   : Center of warm hue range in HSV [0, 1] (~orange).
        warm_hue_width     : Gaussian half-width of warm hue range.
        cool_hue_center    : Center of cool hue range in HSV [0, 1] (~blue).
        cool_hue_width     : Gaussian half-width of cool hue range.
        gradient_zone_px   : Gaussian sigma for boundary zone spread (pixels).
        contrast_strength  : Temperature push amplitude at boundaries.
        opacity            : Final composite opacity.
        \"\"\"
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf
        import colorsys as _cs

        print("    Edge Temperature pass (session 256 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        # Cairo BGRA
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # Stage 1: Warm/cool hue membership masks (vectorised HSV)
        # Convert RGB -> HSV without looping using colorsys-equivalent formulae
        maxc = _np.maximum(_np.maximum(r0, g0), b0).astype(_np.float32)
        minc = _np.minimum(_np.minimum(r0, g0), b0).astype(_np.float32)
        saturation = _np.where(maxc > 1e-6, (maxc - minc) / (maxc + 1e-6), 0.0).astype(_np.float32)

        delta = (maxc - minc + 1e-9).astype(_np.float32)
        # Hue computation (vectorised)
        hue = _np.zeros((h, w), dtype=_np.float32)
        # Red is max
        mask_r = (maxc == r0) & (maxc > minc)
        hue[mask_r] = ((g0[mask_r] - b0[mask_r]) / delta[mask_r]) % 6.0
        # Green is max
        mask_g = (maxc == g0) & (maxc > minc) & ~mask_r
        hue[mask_g] = (b0[mask_g] - r0[mask_g]) / delta[mask_g] + 2.0
        # Blue is max
        mask_b = (maxc == b0) & (maxc > minc) & ~mask_r & ~mask_g
        hue[mask_b] = (r0[mask_b] - g0[mask_b]) / delta[mask_b] + 4.0
        hue = (hue / 6.0) % 1.0   # normalise to [0, 1]

        def _soft_hue_mask(hue_arr, center, width):
            # Gaussian bell over wrapped hue distance, weighted by saturation
            dist = _np.abs(hue_arr - center)
            dist = _np.minimum(dist, 1.0 - dist)   # wrap-around
            return _np.exp(-(dist / (float(width) + 1e-8)) ** 2).astype(_np.float32) * saturation

        wm = _soft_hue_mask(hue, float(warm_hue_center), float(warm_hue_width))
        cm = _soft_hue_mask(hue, float(cool_hue_center), float(cool_hue_width))

        # Stage 2: Gradient of (warm - cool) difference map -> boundary zone
        diff = (wm - cm).astype(_np.float32)   # in [-1, 1]

        # Central-difference gradient (pad to preserve shape)
        gy = _np.pad(diff[2:, :] - diff[:-2, :], ((1, 1), (0, 0)), mode='edge')
        gx = _np.pad(diff[:, 2:] - diff[:, :-2], ((0, 0), (1, 1)), mode='edge')
        grad_mag = _np.sqrt(gy ** 2 + gx ** 2).astype(_np.float32)

        boundary_zone = _gf(grad_mag, sigma=float(gradient_zone_px)).astype(_np.float32)
        bz_max = boundary_zone.max()
        if bz_max > 1e-8:
            boundary_zone /= bz_max

        # Stage 3: Bidirectional simultaneous temperature contrast push
        cs = float(contrast_strength)
        temp_signal = (cs * boundary_zone * diff).astype(_np.float32)

        r1 = _np.clip(r0 + temp_signal * 0.12, 0.0, 1.0).astype(_np.float32)
        g1 = g0.copy()
        b1 = _np.clip(b0 - temp_signal * 0.08, 0.0, 1.0).astype(_np.float32)

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

        boundary_px = int((boundary_zone > 0.1).sum())
        print(f"    Edge Temperature complete "
              f"(boundary_px={boundary_px}, "
              f"contrast_strength={contrast_strength:.3f})")
"""

# ─── Injection anchors ────────────────────────────────────────────────────────

# The artist pass goes before wyeth_tempera_drybrush_pass
ARTIST_ANCHOR = "    def wyeth_tempera_drybrush_pass("

# The improvement pass goes after the last existing improvement pass
# (paint_surface_tooth_pass ends with the last print statement)
IMPROVE_ANCHOR = (
    "        fiber_coverage = float((fiber_map > 0.6).mean())\n"
    "        print(f\"    Surface Tooth complete (grain_size={grain_size}, \"\n"
    "              f\"fiber_coverage={fiber_coverage:.3f})\")"
)

engine_path = os.path.join(REPO, "stroke_engine.py")
with open(engine_path, "r", encoding="utf-8") as f:
    src = f.read()

if "kollwitz_charcoal_compression_pass" in src:
    print("kollwitz_charcoal_compression_pass already present -- skipping.")
else:
    if ARTIST_ANCHOR not in src:
        print(f"ERROR: artist anchor not found in stroke_engine.py", file=sys.stderr)
        sys.exit(1)
    src = src.replace(ARTIST_ANCHOR, CHARCOAL_COMPRESSION_PASS + "\n" + ARTIST_ANCHOR, 1)
    print("Inserted kollwitz_charcoal_compression_pass.")

if "paint_edge_temperature_pass" in src:
    print("paint_edge_temperature_pass already present -- skipping.")
else:
    if IMPROVE_ANCHOR not in src:
        print(f"ERROR: improvement anchor not found in stroke_engine.py", file=sys.stderr)
        sys.exit(1)
    src = src.replace(IMPROVE_ANCHOR, IMPROVE_ANCHOR + EDGE_TEMPERATURE_PASS, 1)
    print("Inserted paint_edge_temperature_pass.")

with open(engine_path, "w", encoding="utf-8") as f:
    f.write(src)

print("stroke_engine.py updated successfully.")
