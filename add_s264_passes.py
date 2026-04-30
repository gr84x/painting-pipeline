"""Insert paint_luminance_excavation_pass (s264 improvement) and
soulages_outrenoir_pass (175th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_luminance_excavation_pass (s264 improvement) ───────────────

EXCAVATION_PASS = '''
    def paint_luminance_excavation_pass(
        self,
        dark_threshold:   float = 0.36,
        variance_sigma:   float = 4.0,
        texture_strength: float = 0.09,
        lift_amount:      float = 0.035,
        noise_seed:       int   = 264,
        opacity:          float = 0.62,
    ) -> None:
        r"""Luminance Excavation -- session 264 artistic improvement.

        THREE-STAGE MICRO-TEXTURE RECOVERY IN DARK REGIONS INSPIRED BY THE
        CHALLENGE FACED BY PAINTERS WORKING IN EXTREME LOW-KEY REGISTERS
        (Soulages, Reinhardt, Malevich, c.1960-2000):

        Any painter working with very dark values faces a fundamental tension:
        the pigment carries internal texture -- direction of application, tonal
        variance within a single loaded stroke, canvas grain pressing through --
        but these are compressed to near-invisibility at low luminance because
        the eye\'s sensitivity to luminance differences falls steeply in dark
        regions (Weber-Fechner law).  The solution the great dark-field painters
        discovered: create MICRO-TEXTURE that operates at luminance differences
        too small to read as distinct value steps but large enough to register
        as surface quality.  A Soulages canvas that reads as "pure black" from
        a distance reveals, on close approach, a complex internal landscape of
        slight luminance variation -- traces of the squeegee drag, the groove of
        the palette knife, the pooling of medium in a depression -- that give the
        black its depth.  This pass excavates and amplifies that latent micro-
        texture from the dark regions of the canvas.

        Stage 1 DARK REGION ISOLATION: Compute per-pixel luminance; isolate all
        pixels below dark_threshold:
          lum = 0.299*R + 0.587*G + 0.114*B
          dark_mask = (lum < dark_threshold).astype(float)
        Apply Gaussian blur to dark_mask with sigma=2.0 to feather edges:
          dark_w = gaussian_filter(dark_mask, sigma=2.0), clamped [0, 1]
        NOVEL: (a) LUMINANCE-THRESHOLD DARK REGION MASK WITH GAUSSIAN FEATHER --
        first improvement to isolate sub-threshold pixels using a feathered binary
        luminance mask; paint_shadow_bleed_pass uses a similar threshold but for
        bleeding colour outward; no prior improvement uses a feathered dark-region
        mask specifically to EXCAVATE internal micro-variation without affecting
        mid/light zones.

        Stage 2 LOCAL LUMINANCE VARIANCE VIA DOG: Within dark regions, compute
        local luminance variance using a difference-of-Gaussians approximation:
          lum_fine   = gaussian_filter(lum, sigma=variance_sigma / 4.0)
          lum_coarse = gaussian_filter(lum, sigma=variance_sigma)
          dog        = abs(lum_fine - lum_coarse)
          dog_norm   = clip(dog / (dog.max() + 1e-6), 0, 1)
        The DoG reveals local micro-variation at scale variance_sigma -- the
        frequency band where paint texture lives (2-20 pixels).
        NOVEL: (b) DIFFERENCE-OF-GAUSSIANS MICRO-TEXTURE EXTRACTION APPLIED
        SELECTIVELY TO DARK REGIONS -- first improvement to use a DoG approach
        (subtracting a coarse Gaussian from a fine Gaussian) to extract micro-
        texture frequency content and use it to selectively amplify buried
        variation; paint_scumble_pass adds physical dry-brush texture; no prior
        improvement uses DoG to excavate and amplify EXISTING sub-threshold
        variation already present in the canvas from prior strokes.

        Stage 3 MICRO-TEXTURE LIFT: Use dog_norm as a micro-texture guide to
        lift dark region luminance very slightly:
          lift = dog_norm * texture_strength * dark_w * lift_amount
          R_lift = R + lift  (same G, B, clipped to [0, 1])
        This gives dark zones a subtle internal relief: the canvas grain, the
        stroke direction, the pooling of pigment -- all very slightly lighter
        against their near-black surroundings, exactly as in Soulages\' Outrenoir.
        NOVEL: (c) DOG-GUIDED LUMINANCE MICRO-LIFT CONFINED TO DARK MASK REGION --
        first improvement to use a DoG micro-texture map to slightly raise
        luminance WITHIN dark regions (using dark_w as gate) so that buried
        stroke texture becomes visible without globally brightening the dark zones;
        paint_craquelure_pass adds crack texture globally; no prior improvement
        uses DoG micro-texture extraction followed by a dark-region-gated lift
        that excavates buried stroke variation from sub-threshold zones.
        """
        print("    Luminance Excavation pass (session 264 improvement)...")

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

        # ── Stage 1: Dark Region Isolation ────────────────────────────────────
        dt       = float(dark_threshold)
        dark_mask = (lum < dt).astype(_np.float32)
        dark_w    = _np.clip(_gf(dark_mask, sigma=2.0), 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Local Luminance Variance (DoG) ───────────────────────────
        vsig       = max(float(variance_sigma), 1.0)
        lum_fine   = _gf(lum, sigma=max(vsig / 4.0, 0.5)).astype(_np.float32)
        lum_coarse = _gf(lum, sigma=vsig).astype(_np.float32)
        dog        = _np.abs(lum_fine - lum_coarse).astype(_np.float32)
        dog_norm   = _np.clip(dog / (dog.max() + 1e-6), 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Micro-Texture Lift ───────────────────────────────────────
        ts   = float(texture_strength)
        la   = float(lift_amount)
        lift = (dog_norm * ts * dark_w * la).astype(_np.float32)

        r1 = _np.clip(r0 + lift, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 + lift, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 + lift, 0.0, 1.0).astype(_np.float32)

        # ── Composite at opacity ───────────────────────────────────────────────
        op    = float(opacity)
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

        dark_px    = int(dark_mask.sum())
        texture_px = int((dog_norm > 0.1).sum())
        lifted_px  = int((lift > 0.001).sum())
        print(f"    Luminance Excavation complete "
              f"(dark_px={dark_px}, texture_px={texture_px}, lifted_px={lifted_px})")
'''

# ── Pass 2: soulages_outrenoir_pass (175th mode) ──────────────────────────────

SOULAGES_PASS = '''
    def soulages_outrenoir_pass(
        self,
        black_threshold:  float = 0.42,
        deepening_power:  float = 2.4,
        stripe_freq:      float = 26.0,
        stripe_strength:  float = 0.055,
        stripe_threshold: float = 0.48,
        bloom_sigma:      float = 2.8,
        bloom_strength:   float = 0.07,
        noise_seed:       int   = 264,
        opacity:          float = 0.80,
    ) -> None:
        r"""Soulages Outrenoir -- session 264, 175th distinct mode.

        THREE-STAGE OUTRENOIR REFLECTIVE-BLACK TECHNIQUE INSPIRED BY
        PIERRE SOULAGES\' MATURE ABSTRACT PAINTING (c.1979-2022):

        Pierre Soulages (1919-2022), born in Conques, Aveyron, France, spent
        seven decades building one of the most radical bodies of work in modern
        painting.  In 1979 he made the discovery that would define the rest of
        his career: while working on a canvas that had accumulated too much black
        paint to develop further, he turned off his studio lights and looked at
        the canvas in the dark -- and found it emanating light.  The surfaces of
        the accumulated black paint, dragged by large squeegees and palette knives
        into grooves, furrows, ridges, and flat planes at different orientations,
        were catching and reflecting ambient light differently, creating a
        topographic luminance map WITHIN the black itself.  He called this
        discovery "Outrenoir" -- beyond black -- because the black was not the
        absence of light but its generator.  From that point, Soulages painted
        only with black, never again using colour.  His canvases are built from
        the trace of the tool rather than from pigment colour: a flat-dragged
        squeegee leaves a matte field; a sharp-edged tool leaves a bright seam;
        a curved drag leaves a field of varying reflectivity across its arc.
        The viewer experiences this as pure luminance contrast within the
        supposedly single-valued darkness: zones of near-total absorption beside
        zones of bright metallic sheen, all within the same black.

        Stage 1 ULTRA-BLACK DEEPENING: For pixels below black_threshold, apply
        a power-law compression that pushes luminance toward near-zero:
          lum_norm = clip(lum / black_threshold, 0, 1)
          scale    = lum_norm^(deepening_power - 1.0)  for lum < black_threshold
          scale    = 1.0                                 for lum >= black_threshold
          R_deep   = R * scale  (same G, B; scale clamped [0, 1])
        This creates the Soulages pigment depth: the pure absorption of industrial-
        grade matte black acrylic, richer and darker than any conventional paint.
        NOVEL: (a) POWER-LAW LUMINANCE COMPRESSION BELOW A THRESHOLD TO CREATE
        SOULAGES-STYLE ULTRA-BLACK DEPTH -- first pass to apply a configurable
        power-law scaling (lum/threshold)^(power-1) specifically to sub-threshold
        pixels, independently compressing dark zones without affecting mid/lights;
        vallotton_dark_interior_pass uses sigmoid-steepened compression; no prior
        pass applies a power-law (gamma-style) compression below a specific
        luminance threshold to push near-darks toward total black while leaving
        mid-tones and highlights entirely untouched.

        Stage 2 HORIZONTAL REFLECTIVE STRIPE FIELD: Within dark regions (below
        stripe_threshold), add a field of subtle horizontal luminance variations
        that simulate Soulages\' horizontal squeegee-drag marks catching light:
          y_norm   = arange(H) / H
          stripe_t = (sin(y_norm * stripe_freq * pi) + 1.0) / 2.0
          dark_mask = clip(1 - lum / stripe_threshold, 0, 1)^2
          stripe_add = stripe_t * stripe_strength * dark_mask
          R_stripe = R + stripe_add  (same G, B, achromatic)
        The sinusoidal stripe pattern, confined to dark zones by dark_mask,
        creates the impression of horizontal tool marks catching ambient light
        at different angles -- bright-seam / matte-field alternation.
        NOVEL: (b) SINUSOIDAL HORIZONTAL STRIPE FIELD CONFINED TO DARK-REGION
        MASK TO SIMULATE SQUEEGEE-DRAG REFLECTIVE SEAMS -- first pass to use a
        sinusoidal luminance variation (sin(y*freq*pi)) confined to a dark-region
        mask to create horizontal surface-reflectivity bands within black zones;
        paint_brushstroke_grain_pass adds physical stroke texture; no prior pass
        applies a sinusoidal luminance-stripe field specifically confined to
        sub-threshold dark zones to simulate horizontal tool-mark reflectivity
        within a Soulages-style ultra-black field.

        Stage 3 EDGE LUMINANCE BLOOM AT DARK/LIGHT BOUNDARIES: At the transition
        between deep-black and lighter areas, slightly amplify the light side --
        the "black makes the white whiter" phenomenon Soulages himself described:
          edge_mag   = sqrt(sobel_x^2 + sobel_y^2)
          dark_side  = clip(1 - lum, 0, 1)
          bloom_raw  = edge_mag * dark_side
          bloom_blur = gaussian_filter(bloom_raw, sigma=bloom_sigma)
          bloom_norm = clip(bloom_blur / bloom_blur.max(), 0, 1)
          R_bloom    = R + bloom_norm * bloom_strength  (same G, B)
        The bloom occurs from the dark side, pushing adjacent light pixels very
        slightly brighter, increasing perceived luminance contrast without
        touching the dark zone itself.
        NOVEL: (c) DARK-SIDE-WEIGHTED EDGE BLOOM AT DARK/LIGHT TRANSITIONS TO
        SIMULATE SOULAGES\' CONTRAST AMPLIFICATION EFFECT -- first pass to weight
        a Sobel edge magnitude by proximity to dark regions (dark_side = 1 - lum)
        and use this dark-proximity-edge product (Gaussian-blurred) to LIFT the
        light pixels at dark boundaries without touching the dark regions themselves;
        paint_halation_pass blooms from bright regions outward; no prior pass
        applies dark-side-weighted edge lifting to create the effect where extreme
        darkness makes surrounding light appear brighter.
        """
        print("    Soulages Outrenoir pass (session 264, 175th mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, convolve as _conv

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Ultra-Black Deepening ────────────────────────────────────
        bt       = float(black_threshold)
        dp       = max(float(deepening_power), 1.0)
        lum_norm = _np.clip(lum / (bt + 1e-6), 0.0, 1.0).astype(_np.float32)
        scale    = _np.where(
            lum < bt,
            lum_norm ** max(dp - 1.0, 0.0),
            _np.ones((h, w), dtype=_np.float32),
        ).astype(_np.float32)
        scale = _np.clip(scale, 0.0, 1.0).astype(_np.float32)

        r1 = _np.clip(r0 * scale, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 * scale, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 * scale, 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Horizontal Reflective Stripe Field ───────────────────────
        sf  = float(stripe_freq)
        ss  = float(stripe_strength)
        st  = float(stripe_threshold)

        y_norm   = (_np.arange(h, dtype=_np.float32) / max(h - 1, 1))[:, _np.newaxis]
        stripe_t = ((_np.sin(y_norm * sf * _np.pi) + 1.0) / 2.0).astype(_np.float32)
        stripe_t = _np.broadcast_to(stripe_t, (h, w)).copy().astype(_np.float32)

        lum1      = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        dark_mask = (_np.clip(1.0 - lum1 / (st + 1e-6), 0.0, 1.0) ** 2).astype(_np.float32)
        stripe_add = (stripe_t * ss * dark_mask).astype(_np.float32)

        r2 = _np.clip(r1 + stripe_add, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 + stripe_add, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 + stripe_add, 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Edge Luminance Bloom at Dark/Light Boundaries ───────────
        bsig = max(float(bloom_sigma), 0.5)
        bst  = float(bloom_strength)

        sobel_x  = _np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=_np.float32)
        sobel_y  = sobel_x.T
        lum2     = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)
        gx       = _conv(lum2, sobel_x, mode="reflect").astype(_np.float32)
        gy       = _conv(lum2, sobel_y, mode="reflect").astype(_np.float32)
        edge_mag = _np.sqrt(gx * gx + gy * gy).astype(_np.float32)

        dark_side  = _np.clip(1.0 - lum2, 0.0, 1.0).astype(_np.float32)
        bloom_raw  = (edge_mag * dark_side).astype(_np.float32)
        bloom_blur = _gf(bloom_raw, sigma=bsig).astype(_np.float32)
        bmx        = bloom_blur.max()
        bloom_norm = _np.clip(bloom_blur / (bmx + 1e-6), 0.0, 1.0).astype(_np.float32)

        r3 = _np.clip(r2 + bloom_norm * bst, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 + bloom_norm * bst, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 + bloom_norm * bst, 0.0, 1.0).astype(_np.float32)

        # ── Composite at opacity ───────────────────────────────────────────────
        op    = float(opacity)
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

        deepened_px = int((lum < bt).sum())
        stripe_px   = int((stripe_add > 0.005).sum())
        bloom_px    = int((bloom_norm > 0.10).sum())
        print(f"    Soulages Outrenoir complete "
              f"(deepened_px={deepened_px}, stripe_px={stripe_px}, "
              f"bloom_px={bloom_px})")
'''

# ── Inject into stroke_engine.py ──────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

already_excav    = "paint_luminance_excavation_pass" in src
already_soulages = "soulages_outrenoir_pass" in src

if already_excav and already_soulages:
    print("Both passes already present in stroke_engine.py -- nothing to do.")
    sys.exit(0)

additions = ""
if not already_excav:
    additions += EXCAVATION_PASS
if not already_soulages:
    additions += "\n" + SOULAGES_PASS

src = src.rstrip("\n") + "\n" + additions + "\n"

with open(ENGINE_PATH, "w", encoding="utf-8") as f:
    f.write(src)

if not already_excav:
    print("Inserted paint_luminance_excavation_pass into stroke_engine.py.")
if not already_soulages:
    print("Inserted soulages_outrenoir_pass into stroke_engine.py.")
