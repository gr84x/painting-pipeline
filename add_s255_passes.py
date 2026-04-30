"""Insert wyeth_tempera_drybrush_pass and paint_tonal_key_pass into
stroke_engine.py (session 255).

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

TEMPERA_DRYBRUSH_PASS = """
    def wyeth_tempera_drybrush_pass(
        self,
        chalk_amplitude:  float = 0.018,
        midtone_low:      float = 0.22,
        midtone_high:     float = 0.78,
        contrast_strength: float = 0.40,
        fiber_low_lum:    float = 0.15,
        fiber_high_lum:   float = 0.42,
        fiber_density:    float = 0.04,
        fiber_brightness: float = 0.08,
        opacity:          float = 0.78,
        seed:             int   = 255,
    ) -> None:
        r\"\"\"Andrew Wyeth Tempera Dry-Brush -- session 255, 166th distinct painting mode.

        THREE-STAGE EGG-TEMPERA DRY-SURFACE SIMULATION INSPIRED BY WYETH:

        Stage 1 DRY CHALK SURFACE: Generate seeded random noise with an
        asymmetric Gaussian blur applied to create a horizontally-biased grain
        direction. The noise is generated via numpy.random.default_rng(seed)
        .standard_normal((h, w)), then blurred with scipy.ndimage.gaussian_filter
        using sigma=(3.0, 0.5) -- a tall vertical sigma of 3.0 and narrow
        horizontal sigma of 0.5. This strongly elongates the noise in the
        vertical direction, creating horizontal grain that simulates the
        characteristic horizontal-stroke mark of egg tempera applied with a
        small flat brush across a gessoed panel. The noise is normalised to
        [-1, 1] and then added uniformly to all three channels at chalk_amplitude.
        Adding the same value to R, G, and B preserves the per-pixel hue while
        adding a luminance-domain grain. Values are clamped to [0, 1].
        NOVEL: (a) HORIZONTALLY-BIASED ASYMMETRIC GAUSSIAN NOISE IN THE
        LUMINANCE DOMAIN FOR EGG-TEMPERA CHALK SURFACE SIMULATION -- first
        pass to apply a seeded standard-normal noise field blurred with an
        asymmetric (tall-vertical) Gaussian to create horizontal grain
        direction, applied uniformly to all channels to preserve hue; no
        prior pass generates directional grain noise using asymmetric blur
        sigma for tempera surface simulation; paint_surface_tooth_pass (s252)
        uses a different surface texture mechanism; no prior pass applies
        horizontally-biased noise to simulate the directional chalky grain
        of egg tempera on gessoed panel.

        Stage 2 MIDTONE PRECISION BAND CONTRAST: Compute the luminance of the
        Stage 1 result. Compute a blurred luminance reference via
        gaussian_filter(lum, sigma=8.0). Compute the local contrast signal
        as the unsharp-mask residual: local_contrast = lum - lum_blurred.
        Compute a soft luminance band mask for the midtone region [midtone_low,
        midtone_high]: the mask ramps from 0 to 1 over the lower 0.15 lum
        above midtone_low, stays 1 in the interior, and ramps back from 1 to
        0 over the upper 0.15 lum below midtone_high. Apply the local contrast
        enhancement within the band: new_channel = channel + local_contrast *
        contrast_strength * band_mask. Values are clamped to [0, 1].
        This simulates Wyeth's extraordinary differentiation within midtone
        values, achieved through the discipline of egg tempera (which cannot
        be blended and requires each value to be mixed and placed precisely).
        NOVEL: (b) LUMINANCE-BAND-GATED UNSHARP-MASK LOCAL CONTRAST
        ENHANCEMENT TARGETING ONLY THE MIDTONE ZONE -- first pass to apply
        an unsharp-mask contrast residual (canvas - Gaussian_blur) gated by a
        soft luminance band mask that restricts enhancement to the midtone
        range [midtone_low, midtone_high]; meso_detail_pass and
        micro_detail_pass apply spatial detail enhancement globally; no prior
        pass uses a smooth luminance-band mask to confine local contrast
        enhancement to the midtone zone for simulating tempera tonal precision.

        Stage 3 DRY-BRUSH FIBER TRACES AT TONAL TRANSITIONS: Compute the
        luminance of the Stage 2 result. Identify tonal transition pixels
        in the dark-to-mid zone [fiber_low_lum, fiber_high_lum] using a soft
        tent mask (ramps over 0.10 lum at each edge). Generate a sparse binary
        noise field: random uniform values with threshold (1 - fiber_density)
        activate only fiber_density fraction of pixels. Apply a horizontal-only
        Gaussian blur with sigma=(0.0, 1.5) to the sparse field, creating
        horizontal fiber-like runs where isolated activated pixels smear into
        short horizontal traces. Apply this field at fiber_brightness as an
        additive brightness offset, masked by the tonal transition zone mask.
        This simulates the dry-brush watercolour technique: a near-pigment-
        starved brush dragged across rough cold-press paper catches only on the
        grain peaks, leaving bare paper visible between fibres. The effect is
        most visible at dark-to-mid tonal transitions where the brush lifts
        before completing its stroke.
        NOVEL: (c) HORIZONTALLY-BLURRED SPARSE NOISE FIELD APPLIED AS ADDITIVE
        FIBER-TRACE BRIGHTNESS IN TONAL TRANSITION ZONES -- first pass to
        generate a sparse activation field (fiber_density fraction active),
        blur it horizontally-only (sigma=(0, 1.5)) to create fiber-like runs,
        and apply it as an additive brightening within the dark-to-mid tonal
        transition zone [fiber_low_lum, fiber_high_lum]; no prior pass
        generates a sparse-then-horizontal-blur noise field for fiber-trace
        simulation; paint_scumble_pass deposits dry marks on texture peaks
        globally; no prior pass creates directional fiber traces restricted
        to tonal transition zones as a dry-brush paper-grain simulation.

        chalk_amplitude  : Amplitude of horizontal-grain noise (luminance domain).
        midtone_low      : Lower luminance bound of midtone precision band.
        midtone_high     : Upper luminance bound of midtone precision band.
        contrast_strength: Unsharp-mask contrast strength within the midtone band.
        fiber_low_lum    : Lower lum bound of tonal transition zone for fibers.
        fiber_high_lum   : Upper lum bound of tonal transition zone for fibers.
        fiber_density    : Fraction of pixels activated in sparse fiber field.
        fiber_brightness : Additive brightness amplitude of fiber traces.
        opacity          : Final composite opacity.
        seed             : RNG seed for reproducibility.
        \"\"\"
        import numpy as _np

        print("    Wyeth Tempera Dry-Brush pass (session 255, 166th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        # Working in float32 [0,1] -- cairo BGRA order
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0

        from scipy.ndimage import gaussian_filter as _gf

        # ── Stage 1: Dry chalk surface (horizontal-grain noise) ───────────
        rng = _np.random.default_rng(int(seed))
        noise = rng.standard_normal((h, w)).astype(_np.float32)
        # Asymmetric blur: sigma_y=3.0 elongates vertically -> horizontal grain
        noise_directional = _gf(noise, sigma=(3.0, 0.5)).astype(_np.float32)
        noise_max = float(_np.abs(noise_directional).max())
        if noise_max > 1e-6:
            noise_directional /= noise_max

        ca = float(chalk_amplitude)
        r1 = _np.clip(r0 + noise_directional * ca, 0.0, 1.0)
        g1 = _np.clip(g0 + noise_directional * ca, 0.0, 1.0)
        b1 = _np.clip(b0 + noise_directional * ca, 0.0, 1.0)

        # ── Stage 2: Midtone precision band contrast ───────────────────────
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        lum_blur = _gf(lum1, sigma=8.0).astype(_np.float32)
        local_contrast = (lum1 - lum_blur).astype(_np.float32)

        ml = float(midtone_low)
        mh = float(midtone_high)
        ramp = 0.15
        # Lower ramp: 0->1 from ml to ml+ramp
        lower_ramp = _np.clip((lum1 - ml) / (ramp + 1e-6), 0.0, 1.0)
        # Upper ramp: 1->0 from mh-ramp to mh
        upper_ramp = _np.clip((mh - lum1) / (ramp + 1e-6), 0.0, 1.0)
        band_mask = (lower_ramp * upper_ramp).astype(_np.float32)

        cs = float(contrast_strength)
        r2 = _np.clip(r1 + local_contrast * cs * band_mask, 0.0, 1.0)
        g2 = _np.clip(g1 + local_contrast * cs * band_mask, 0.0, 1.0)
        b2 = _np.clip(b1 + local_contrast * cs * band_mask, 0.0, 1.0)

        # ── Stage 3: Dry-brush fiber traces at tonal transitions ───────────
        lum2 = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)

        fl = float(fiber_low_lum)
        fh = float(fiber_high_lum)
        fiber_ramp = 0.10
        fib_lower = _np.clip((lum2 - fl) / (fiber_ramp + 1e-6), 0.0, 1.0)
        fib_upper = _np.clip((fh - lum2) / (fiber_ramp + 1e-6), 0.0, 1.0)
        fiber_zone = (fib_lower * fib_upper).astype(_np.float32)

        # Sparse activation field with horizontal blur for fiber-like runs
        rng2 = _np.random.default_rng(int(seed) + 1)
        sparse = (rng2.uniform(0.0, 1.0, (h, w)) >
                  (1.0 - float(fiber_density))).astype(_np.float32)
        fiber_blurred = _gf(sparse, sigma=(0.0, 1.5)).astype(_np.float32)
        fib_max = float(fiber_blurred.max())
        if fib_max > 1e-6:
            fiber_blurred /= fib_max

        fb = float(fiber_brightness)
        fiber_add = fiber_blurred * fiber_zone * fb
        r3 = _np.clip(r2 + fiber_add, 0.0, 1.0)
        g3 = _np.clip(g2 + fiber_add, 0.0, 1.0)
        b3 = _np.clip(b2 + fiber_add, 0.0, 1.0)

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

        n_fiber = int((fiber_zone * fiber_blurred > 0.1).sum())
        print(f"    Wyeth Tempera Dry-Brush complete (fiber_pixels={n_fiber})")
"""

TONAL_KEY_PASS = """
    def paint_tonal_key_pass(
        self,
        target_key:       float = 0.50,
        key_strength:     float = 4.0,
        dither_amplitude: float = 0.006,
        opacity:          float = 0.65,
    ) -> None:
        r\"\"\"Tonal Key Correction with Micro-Dithering -- session 255 improvement pass.

        THREE-STAGE TONAL KEY MANAGEMENT INSPIRED BY THE PAINTER'S CONCEPT
        OF KEY (HIGH-KEY, MID-KEY, LOW-KEY):

        Addresses the fundamental painting concept of tonal key: whether a
        work is high-key (luminous, light-filled), low-key (somber, dark), or
        mid-key (balanced). Artists deliberately work in a key to create a
        unified emotional tone. The pipeline can drift toward arbitrary tonal
        distributions; this pass analyses the actual tonal distribution and
        applies a sigmoid remapping to correct or set the key, then adds
        micro-tonal dithering to prevent posterisation in compressed zones.

        Stage 1 LUMINANCE MEDIAN ANALYSIS: Compute the per-pixel luminance:
        lum = 0.299R + 0.587G + 0.114B. Compute the median luminance value
        (50th percentile across all h*w pixels) using numpy.median(lum). The
        median is the robust tonal center of mass of the painting -- where the
        bulk of pixels live tonally. Unlike the mean, the median is not dragged
        by extreme darks (a small black vignette) or extreme lights (a single
        bright highlight).
        NOVEL: (a) LUMINANCE MEDIAN ANALYSIS AS TONAL CENTER OF MASS FOR
        KEY CORRECTION -- first pass to compute the luminance median as the
        painting's tonal center of mass in order to drive a subsequent
        key correction; no prior pass computes a full-image luminance
        statistical measure to inform a tonal remapping; paint_glazing_pass
        applies a fixed-colour glaze; no prior pass measures the painting's
        current key and applies a targeted correction based on the measured
        tonal distribution.

        Stage 2 SIGMOID KEY CORRECTION: Compute per-pixel luminance deviation
        from the median: dev = lum - median_lum. Apply sigmoid key remapping:
        sigmoid_input = dev * key_strength + (target_key - 0.5) * key_strength;
        new_lum = 1 / (1 + exp(-sigmoid_input)); this maps the tonal
        distribution through a sigmoid function centred at target_key,
        compressing darks or lights depending on the target direction.
        Apply per-channel luminance scaling: scale = new_lum / (lum + 1e-6),
        clamped to [0.05, 20.0] to prevent extreme rescaling; final_channel =
        channel * scale clamped to [0, 1].
        NOVEL: (b) SIGMOID LUMINANCE REMAPPING DRIVEN BY MEASURED TONAL MEDIAN
        TO PUSH THE DISTRIBUTION TOWARD A USER-SPECIFIED KEY -- first pass to
        apply a sigmoid function to per-pixel luminance deviations from the
        computed median to correct the tonal key; no prior pass applies a
        sigmoid luminance remapping; paint_vignette_pass darkens edges;
        no prior pass uses a sigmoid of (dev * key_strength + key_offset) to
        push the tonal distribution toward a specified key value.

        Stage 3 MICRO-TONAL DITHERING WITH 4x4 BAYER MATRIX: Apply ordered
        dithering using a 4x4 Bayer threshold matrix to prevent posterisation
        artifacts in compressed tonal zones. The matrix values [0..15] are
        normalised to [-0.5, 0.5] and scaled by dither_amplitude. The matrix
        is tiled to canvas dimensions via numpy.tile. The same offset is added
        to all three channels (luminance-domain dithering), preserving hue
        while adding the micro-tonal variation needed to break banding in
        compressed tonal areas. dither_amplitude of 0.006 adds approximately
        ±1.5/255 tonal variation -- invisible in normal viewing but sufficient
        to break banding.
        NOVEL: (c) 4x4 BAYER MATRIX ORDERED DITHERING IN THE LUMINANCE DOMAIN
        AS A TONAL ANTI-POSTERISATION STEP -- first pass to apply a Bayer
        threshold matrix as ordered dithering to the canvas; no prior pass
        uses an ordered-dither pattern; paint_chromatic_aberration_pass
        introduces RGB channel displacement fringing; no prior pass applies
        a Bayer matrix to prevent banding in compressed tonal zones.

        target_key        : Target tonal key (0=low-key, 0.5=mid, 1.0=high-key).
        key_strength      : Sigmoid steepness controlling correction aggressiveness.
        dither_amplitude  : Peak amplitude of Bayer dither offset (0.006 = subtle).
        opacity           : Final composite opacity.
        \"\"\"
        import numpy as _np

        print("    Tonal Key pass (session 255 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        r0 = orig[:, :, 2].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        b0 = orig[:, :, 0].astype(_np.float32) / 255.0

        # Stage 1: Luminance median analysis
        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)
        median_lum = float(_np.median(lum))

        # Stage 2: Sigmoid key correction
        dev = (lum - median_lum).astype(_np.float64)
        tgt = float(target_key)
        ks  = float(key_strength)
        sigmoid_input = dev * ks + (tgt - 0.5) * ks
        new_lum = (1.0 / (1.0 + _np.exp(-sigmoid_input))).astype(_np.float32)

        eps = 1e-6
        scale = _np.clip(new_lum / (lum + eps), 0.05, 20.0).astype(_np.float32)
        r1 = _np.clip(r0 * scale, 0.0, 1.0)
        g1 = _np.clip(g0 * scale, 0.0, 1.0)
        b1 = _np.clip(b0 * scale, 0.0, 1.0)

        # Stage 3: Micro-tonal dithering with 4x4 Bayer matrix
        bayer4 = _np.array([
            [ 0,  8,  2, 10],
            [12,  4, 14,  6],
            [ 3, 11,  1,  9],
            [15,  7, 13,  5],
        ], dtype=_np.float32) / 16.0 - 0.5   # normalised to [-0.5, 0.5]

        tiles_y = h // 4 + 1
        tiles_x = w // 4 + 1
        bayer_full = _np.tile(bayer4, (tiles_y, tiles_x))[:h, :w]
        dither = bayer_full * float(dither_amplitude)

        r2 = _np.clip(r1 + dither, 0.0, 1.0)
        g2 = _np.clip(g1 + dither, 0.0, 1.0)
        b2 = _np.clip(b1 + dither, 0.0, 1.0)

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

        print(f"    Tonal Key complete (median_lum={median_lum:.3f}, "
              f"target_key={target_key:.2f})")
"""

ENGINE_FILE = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_FILE, "r", encoding="utf-8") as f:
    src = f.read()

assert "wyeth_tempera_drybrush_pass" not in src, \
    "wyeth_tempera_drybrush_pass already present in stroke_engine.py"
assert "paint_tonal_key_pass" not in src, \
    "paint_tonal_key_pass already present in stroke_engine.py"

# Insert before rego_flat_figure_pass (last artist pass from s254)
ANCHOR = "    def rego_flat_figure_pass("
assert ANCHOR in src, f"Anchor {ANCHOR!r} not found in stroke_engine.py"

new_src = src.replace(
    ANCHOR,
    TEMPERA_DRYBRUSH_PASS + "\n" + "    def paint_tonal_key_pass(" +
    TONAL_KEY_PASS.split("    def paint_tonal_key_pass(", 1)[1] +
    "\n" + ANCHOR
)

with open(ENGINE_FILE, "w", encoding="utf-8") as f:
    f.write(new_src)

print("wyeth_tempera_drybrush_pass and paint_tonal_key_pass inserted into stroke_engine.py")
