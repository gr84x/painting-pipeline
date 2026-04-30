"""Insert vuillard_chromatic_dissolution_pass and paint_local_hue_drift_pass
into stroke_engine.py (session 262).

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: vuillard_chromatic_dissolution_pass ───────────────────────────────

VUILLARD_PASS = """
    def vuillard_chromatic_dissolution_pass(
        self,
        hue_blur_sigma:    float = 12.0,
        hue_blend:         float = 0.55,
        ochre_r:           float = 0.78,
        ochre_g:           float = 0.66,
        ochre_b:           float = 0.42,
        ochre_strength:    float = 0.22,
        ochre_lum_lo:      float = 0.35,
        ochre_lum_hi:      float = 0.72,
        grain_amplitude:   float = 0.028,
        grain_sigma:       float = 0.8,
        noise_seed:        int   = 262,
        opacity:           float = 0.80,
    ) -> None:
        r\"\"\"Édouard Vuillard Chromatic Dissolution -- session 262, 173rd distinct mode.

        THREE-STAGE INTIMIST PATTERN DISSOLUTION TECHNIQUE INSPIRED BY
        ÉDOUARD VUILLARD (1868-1940):

        Édouard Vuillard (1868-1940), a member of the Nabi group with Bonnard
        and Sérusier, developed a style of domestic intimism unlike any other
        painter's.  His defining achievement is the DISSOLUTION OF BOUNDARY
        between figure and environment: in his interiors, a woman's blouse
        cannot be distinguished from the wallpaper behind her, a tablecloth
        merges into the floor, a brooch is the same colour as a picture frame.
        Three techniques create this quality:

        (1) LOCAL HUE AVERAGING (pattern dissolution): Vuillard perceived and
        painted the AVERAGE local hue rather than the precise hue of each
        individual object.  In practice, he would mix a colour drawn from a
        wide local sample of the scene and apply it consistently across figure
        and background alike.  This can be modelled by spatially blurring the
        hue channel of the image and blending the blurred hue back into the
        original, pushing nearby areas of different hue toward a shared local
        average.  The result is that the hard hue boundaries between object
        and background soften: both share a common local chromatic field.

        (2) WARM OCHRE GROUND PENETRATION: Vuillard frequently painted in
        PEINTURE À LA COLLE (distemper on cardboard), a matte, dry medium that
        absorbs colour differently from oil.  The warm ochre-brown of the
        unprepared cardboard reads through all subsequent layers, giving his
        interiors a warm, amber-yellow undertone in the midtone range.  Bright
        highlights remain cool (they are the thinnest paint), deep shadows
        remain cool (they are the darkest underpaint), but the midtone range
        is warmed by the ground penetrating the thin distemper layer above.

        (3) MATTE DISTEMPER SURFACE GRAIN: Peinture à la colle produces a
        characteristically matte, powdery surface unlike oil or pastel.
        Individual marks are not visible as brushstrokes but as faint tonal
        variations in the dried distemper layer.  This grain is more isotropic
        and finer than oil impasto; it reads as a warm, velvety skin rather
        than directional brushwork.

        Stage 1 LOCAL HUE AVERAGING: Convert the image from RGB to HSV (or
        equivalent HSL), spatially Gaussian-blur the hue channel at a wide
        sigma (hue_blur_sigma), then blend the blurred hue back into the
        original at hue_blend strength.  Convert back to RGB.
          [H, S, V] = rgb_to_hsv(R, G, B)
          H_blur    = gaussian_filter(H, sigma=hue_blur_sigma)
          H_new     = H * (1 - hue_blend) + H_blur * hue_blend
          [R', G', B'] = hsv_to_rgb(H_new, S, V)
        NOVEL: (a) SPATIAL GAUSSIAN BLUR OF HSV HUE CHANNEL ONLY (S AND V
        UNCHANGED) THEN PARTIAL BLEND BACK INTO ORIGINAL HUE -- first pass
        to apply a spatially-blurred hue blend using only the hue channel
        of HSV (not affecting saturation or value), creating the soft hue
        dissolution between adjacent areas; intimiste_pattern_pass adds
        repeating textile STROKES; no prior pass spatially averages the HSV
        hue channel with Gaussian blur and blends toward the local hue mean.

        Stage 2 WARM OCHRE MIDTONE PENETRATION: In the midtone luminance
        band (lum in [ochre_lum_lo, ochre_lum_hi]), apply a warm ochre tint
        with a smooth bell-curve weight.  The bell is Gaussian-shaped,
        centred at (ochre_lum_lo + ochre_lum_hi) / 2:
          lum_center = (ochre_lum_lo + ochre_lum_hi) / 2
          lum_sigma  = (ochre_lum_hi - ochre_lum_lo) / 4
          ochre_gate = exp(-0.5 * ((lum - lum_center) / lum_sigma)^2) * ochre_strength
          R_new = clip(R + ochre_gate * (ochre_r - R), 0, 1)
          G_new = clip(G + ochre_gate * (ochre_g - G), 0, 1)
          B_new = clip(B + ochre_gate * (ochre_b - B), 0, 1)
        NOVEL: (b) GAUSSIAN BELL MIDTONE-BOUNDED WARM OCHRE TINT BLEND (WITH
        CENTRE AT MID-RANGE OF [ochre_lum_lo, ochre_lum_hi] AND SIGMA DERIVED
        FROM BAND HALF-WIDTH) -- first pass to apply an ochre/amber warm tint
        specifically in the midtone band using a Gaussian bell computed from
        configurable lum_lo/lum_hi parameters, distinct from triple_zone_glaze
        (which uses hard pivot thresholds) and from split_toning (two hard zones);
        the ochre target (0.78, 0.66, 0.42) is the peinture-à-la-colle cardboard
        ground colour, a specific warm amber not used in any prior pass.

        Stage 3 MATTE DISTEMPER SURFACE GRAIN: Generate smooth low-amplitude
        noise by creating random noise and blurring it (grain_sigma) to remove
        pixel-scale harshness, then add to the image at grain_amplitude:
          raw_noise = rng.standard_normal((H, W)) * grain_amplitude
          smooth_noise = gaussian_filter(raw_noise, sigma=grain_sigma)
          R_new = clip(R + smooth_noise, 0, 1)
          G_new = clip(G + smooth_noise, 0, 1)
          B_new = clip(B + smooth_noise, 0, 1)
        Applying the same smooth_noise to all three channels produces an
        achromatic (luminance-only) grain -- the powdery matte distemper
        surface.
        NOVEL: (c) SINGLE-CHANNEL (LUMINANCE-ONLY) SMOOTH NOISE GRAIN VIA
        IDENTICAL NOISE ADDED TO ALL THREE RGB CHANNELS (ACHROMATIC GRAIN,
        NOT CHROMATIC) -- first pass to produce an achromatic grain by adding
        a single Gaussian-smoothed noise field identically to R, G, and B;
        paint_granulation_pass uses per-channel different noise to produce
        CHROMATIC grain; paint_film_grain_overlay_pass uses per-channel noise;
        no prior pass adds a single smooth noise to all three channels to
        produce achromatic (luminance-only) grain that does not shift hue.
        \"\"\"
        print("    Vuillard Chromatic Dissolution pass (session 262, 173rd mode)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        rng_local = _np.random.default_rng(int(noise_seed))

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Local Hue Averaging ──────────────────────────────────────
        hs = max(float(hue_blur_sigma), 0.5)
        hb = float(hue_blend)

        # RGB -> HSV
        c_max = _np.maximum(_np.maximum(r0, g0), b0)
        c_min = _np.minimum(_np.minimum(r0, g0), b0)
        delta = c_max - c_min

        # Value
        v = c_max.copy()

        # Saturation
        s = _np.where(c_max > 1e-6, delta / (c_max + 1e-6), 0.0).astype(_np.float32)

        # Hue (0..1 range)
        hue = _np.zeros((h, w), dtype=_np.float32)
        eps = 1e-6
        mask_r = (c_max == r0) & (delta > eps)
        mask_g = (c_max == g0) & (delta > eps)
        mask_b = (c_max == b0) & (delta > eps)
        hue[mask_r] = ((g0[mask_r] - b0[mask_r]) / (delta[mask_r] + eps)) % 6.0
        hue[mask_g] = (b0[mask_g] - r0[mask_g]) / (delta[mask_g] + eps) + 2.0
        hue[mask_b] = (r0[mask_b] - g0[mask_b]) / (delta[mask_b] + eps) + 4.0
        hue = hue / 6.0  # normalise to [0, 1]

        # Blur hue (circular -- encode as sin/cos to handle wraparound)
        hue_sin = _np.sin(hue * 2.0 * _np.pi).astype(_np.float32)
        hue_cos = _np.cos(hue * 2.0 * _np.pi).astype(_np.float32)
        hue_sin_blur = _gf(hue_sin, sigma=hs)
        hue_cos_blur = _gf(hue_cos, sigma=hs)
        hue_blur = (_np.arctan2(hue_sin_blur, hue_cos_blur) / (2.0 * _np.pi)) % 1.0

        hue_new = (hue * (1.0 - hb) + hue_blur * hb) % 1.0

        # HSV -> RGB
        h6 = hue_new * 6.0
        i  = _np.floor(h6).astype(_np.int32) % 6
        f  = (h6 - _np.floor(h6)).astype(_np.float32)
        p  = _np.clip(v * (1.0 - s),          0.0, 1.0).astype(_np.float32)
        q  = _np.clip(v * (1.0 - s * f),       0.0, 1.0).astype(_np.float32)
        t  = _np.clip(v * (1.0 - s * (1.0 - f)), 0.0, 1.0).astype(_np.float32)

        r1 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5], [v, q, p, p, t, v], default=v).astype(_np.float32)
        g1 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5], [t, v, v, q, p, p], default=v).astype(_np.float32)
        b1 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5], [p, p, t, v, v, q], default=v).astype(_np.float32)

        r1 = _np.clip(r1, 0.0, 1.0)
        g1 = _np.clip(g1, 0.0, 1.0)
        b1 = _np.clip(b1, 0.0, 1.0)

        # ── Stage 2: Warm Ochre Midtone Penetration ───────────────────────────
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        or_ = float(ochre_r); og = float(ochre_g); ob = float(ochre_b)
        ostr = float(ochre_strength)
        llo = float(ochre_lum_lo); lhi = float(ochre_lum_hi)
        lc = (llo + lhi) * 0.5
        lsig = max((lhi - llo) * 0.25, 1e-4)

        ochre_gate = _np.clip(
            _np.exp(-0.5 * ((lum1 - lc) / lsig) ** 2) * ostr,
            0.0, 1.0
        ).astype(_np.float32)

        r2 = _np.clip(r1 + ochre_gate * (or_ - r1), 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 + ochre_gate * (og - g1), 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 + ochre_gate * (ob - b1), 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Matte Distemper Surface Grain ────────────────────────────
        ga = float(grain_amplitude)
        gs = max(float(grain_sigma), 0.3)

        raw_noise = rng_local.standard_normal((h, w)).astype(_np.float32) * ga
        smooth_noise = _gf(raw_noise, sigma=gs).astype(_np.float32)

        r3 = _np.clip(r2 + smooth_noise, 0.0, 1.0).astype(_np.float32)
        g3 = _np.clip(g2 + smooth_noise, 0.0, 1.0).astype(_np.float32)
        b3 = _np.clip(b2 + smooth_noise, 0.0, 1.0).astype(_np.float32)

        # ── Composite at opacity ───────────────────────────────────────────────
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

        ochre_px = int((ochre_gate > 0.05).sum())
        print(f"    Vuillard Chromatic Dissolution complete "
              f"(hue_blend={hb:.2f}, ochre_px={ochre_px}, "
              f"grain_amplitude={ga:.3f})")
"""

# ── Pass 2: paint_local_hue_drift_pass ────────────────────────────────────────

LOCAL_HUE_DRIFT_PASS = """
    def paint_local_hue_drift_pass(
        self,
        drift_sigma:   float = 18.0,
        drift_strength: float = 0.40,
        saturation_floor: float = 0.08,
        saturation_ceil:  float = 0.90,
        noise_seed:    int   = 262,
        opacity:       float = 0.70,
    ) -> None:
        r\"\"\"Local Hue Drift -- session 262 artistic improvement.

        SPATIALLY-VARYING HUE FIELD DRIFT WITH SATURATION CLAMP.

        In many painting traditions the precise hue of a small object area is
        not recorded independently but is allowed to drift toward the dominant
        local hue.  Vuillard merged figure with environment through shared hue
        fields.  Cézanne allowed large orange still-life planes to echo the
        warm grey of the tablecloth below.  Morandi reduced all vessels in a
        group to the same narrow hue range regardless of their actual ceramic
        colour.  In all cases the mechanism is LOCAL HUE AVERAGING: the eye
        adapts to the dominant hue of a spatial region and perceives smaller
        hue variations within it as uniform.

        Stage 1 CIRCULAR-MEAN HUE BLUR WITH SATURATION GATE: Extract the HSV
        hue channel.  Encode as (sin(2π·H), cos(2π·H)) to handle the circular
        wraparound at red (H=0/1).  Gaussian-blur each component at sigma
        drift_sigma.  Reconstruct the blurred hue via arctan2.  The drift is
        applied proportional to pixel saturation: fully-desaturated pixels
        (grey) have no hue to drift; fully-saturated pixels drift maximally.
          H_sin_blur = gaussian_filter(sin(2π·H), sigma=drift_sigma)
          H_cos_blur = gaussian_filter(cos(2π·H), sigma=drift_sigma)
          H_drift    = arctan2(H_sin_blur, H_cos_blur) / (2π) mod 1
          s_gate     = clip((S - saturation_floor) / (saturation_ceil - saturation_floor), 0, 1)
          H_new      = H * (1 - drift_strength * s_gate) + H_drift * drift_strength * s_gate
        NOVEL: (a) SATURATION-GATED CIRCULAR-MEAN HUE DRIFT -- first pass to
        apply a circular-mean hue blur (via sin/cos encoding) gated by per-pixel
        saturation; hammershoi uses global desat not hue blur; vuillard_chromatic
        dissolution_pass (this session) applies a fixed hue_blend without
        saturation gating; this pass modulates drift_strength by local saturation
        so grey pixels drift less than coloured pixels.

        Stage 2 SATURATION CLAMP: After hue drift, clamp saturation to the
        range [saturation_floor, saturation_ceil].  This prevents isolated
        highly-saturated pixels from remaining isolated after the drift (which
        would create hue artifacts) and ensures grey pixels are not assigned
        saturated colours:
          S_new = clip(S, saturation_floor, saturation_ceil)
        NOVEL: (b) GLOBAL SATURATION CLAMP APPLIED AFTER HUE DRIFT TO MAINTAIN
        PERCEPTUAL COHERENCE -- no prior pass implements a saturation clamp
        following a spatial hue manipulation; this removes drift artifacts at
        chromatic boundaries where the blurred hue diverges from the original.

        Stage 3 RECONSTRUCT AND COMPOSITE: Convert modified HSV back to RGB
        and composite at opacity.
        \"\"\"
        print("    Local Hue Drift pass (session 262 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        # ── Stage 1: Circular-Mean Hue Blur with Saturation Gate ──────────────
        ds = max(float(drift_sigma), 0.5)
        dstr = float(drift_strength)
        sfl = float(saturation_floor)
        sc  = float(saturation_ceil)

        c_max = _np.maximum(_np.maximum(r0, g0), b0)
        c_min = _np.minimum(_np.minimum(r0, g0), b0)
        delta = c_max - c_min
        v = c_max.copy()
        s = _np.where(c_max > 1e-6, delta / (c_max + 1e-6), 0.0).astype(_np.float32)

        eps = 1e-6
        hue = _np.zeros((h, w), dtype=_np.float32)
        mask_r = (c_max == r0) & (delta > eps)
        mask_g = (c_max == g0) & (delta > eps)
        mask_b = (c_max == b0) & (delta > eps)
        hue[mask_r] = ((g0[mask_r] - b0[mask_r]) / (delta[mask_r] + eps)) % 6.0
        hue[mask_g] = (b0[mask_g] - r0[mask_g]) / (delta[mask_g] + eps) + 2.0
        hue[mask_b] = (r0[mask_b] - g0[mask_b]) / (delta[mask_b] + eps) + 4.0
        hue = hue / 6.0

        hue_sin = _np.sin(hue * 2.0 * _np.pi).astype(_np.float32)
        hue_cos = _np.cos(hue * 2.0 * _np.pi).astype(_np.float32)
        hsb = _gf(hue_sin, sigma=ds)
        hcb = _gf(hue_cos, sigma=ds)
        hue_drift = (_np.arctan2(hsb, hcb) / (2.0 * _np.pi)) % 1.0

        s_gate = _np.clip((s - sfl) / max(sc - sfl, eps), 0.0, 1.0).astype(_np.float32)
        hue_new = (hue * (1.0 - dstr * s_gate) + hue_drift * dstr * s_gate) % 1.0

        # ── Stage 2: Saturation Clamp ──────────────────────────────────────────
        s_new = _np.clip(s, sfl, sc).astype(_np.float32)

        # ── Stage 3: HSV -> RGB ────────────────────────────────────────────────
        h6 = hue_new * 6.0
        i  = _np.floor(h6).astype(_np.int32) % 6
        f  = (h6 - _np.floor(h6)).astype(_np.float32)
        p  = _np.clip(v * (1.0 - s_new),                 0.0, 1.0).astype(_np.float32)
        q  = _np.clip(v * (1.0 - s_new * f),             0.0, 1.0).astype(_np.float32)
        t  = _np.clip(v * (1.0 - s_new * (1.0 - f)),     0.0, 1.0).astype(_np.float32)

        r1 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5], [v, q, p, p, t, v], default=v).astype(_np.float32)
        g1 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5], [t, v, v, q, p, p], default=v).astype(_np.float32)
        b1 = _np.select([i==0, i==1, i==2, i==3, i==4, i==5], [p, p, t, v, v, q], default=v).astype(_np.float32)
        r1 = _np.clip(r1, 0.0, 1.0)
        g1 = _np.clip(g1, 0.0, 1.0)
        b1 = _np.clip(b1, 0.0, 1.0)

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

        drifted_px = int((s_gate > 0.1).sum())
        print(f"    Local Hue Drift complete "
              f"(drift_sigma={ds:.1f}, drifted_px={drifted_px})")
"""

# ── Inject into stroke_engine.py ─────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

already_vuillard   = "vuillard_chromatic_dissolution_pass" in src
already_hue_drift  = "paint_local_hue_drift_pass" in src

if already_vuillard and already_hue_drift:
    print("Both passes already present in stroke_engine.py -- nothing to do.")
    sys.exit(0)

additions = ""
if not already_vuillard:
    additions += VUILLARD_PASS
if not already_hue_drift:
    additions += "\n" + LOCAL_HUE_DRIFT_PASS

src = src.rstrip("\n") + "\n" + additions + "\n"

with open(ENGINE_PATH, "w", encoding="utf-8") as f:
    f.write(src)

if not already_vuillard:
    print("Inserted vuillard_chromatic_dissolution_pass into stroke_engine.py.")
if not already_hue_drift:
    print("Inserted paint_local_hue_drift_pass into stroke_engine.py.")
