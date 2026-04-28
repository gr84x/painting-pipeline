"""Append session 235 passes to stroke_engine.py."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

NOLDE_PASS = r'''
    def nolde_incandescent_surge_pass(
        self,
        shadow_ceil:       float = 0.30,
        shadow_power:      float = 1.80,
        shadow_r_push:     float = 0.10,
        shadow_b_drop:     float = 0.07,
        mid_center:        float = 0.50,
        mid_width:         float = 0.20,
        surge_boost:       float = 0.70,
        bloom_chroma_min:  float = 0.22,
        bloom_lum_min:     float = 0.38,
        bloom_sigma:       float = 3.50,
        bloom_warm_r:      float = 0.06,
        bloom_warm_g:      float = 0.03,
        bloom_warm_b:      float = 0.01,
        opacity:           float = 0.84,
    ) -> None:
        """
        Nolde Incandescent Surge -- session 235: ONE HUNDRED AND FORTY-SIXTH distinct mode.

        Implements Emil Nolde (1867-1956) incandescent colour-expressionism technique.
        Nolde, the great colourist of German Expressionism, painted with primordial colour
        force: his shadows glow warm (orange-red) against near-black voids, his mid-tones
        surge to full spectral intensity, and intense saturated zones radiate a luminous
        halo of warm light.  Crucially, Nolde INVERTS the academic warm-light / cool-shadow
        convention: his shadows are warm (fire and earth), his lights are often cooler or
        neutral.  He paints northern sea storms, florals of savage colour intensity, and
        barbaric figurative subjects with an almost spiritual chromatic violence.

        Three-stage mechanism, sharing one luminance and chroma map:

        Stage 1  SHADOW WARMTH INVERSION (inverted from academic convention):
          dark_gate = clip((shadow_ceil - lum) / shadow_ceil, 0, 1) ^ shadow_power
          R += dark_gate * shadow_r_push   [warm red push into shadows]
          B -= dark_gate * shadow_b_drop   [pull cool blue from shadow zones]
          Creates Nolde's characteristic warm-red ground in dark recesses --
          the OPPOSITE of academic painting where shadows are cool.
          Differs from warm_cool_zone_pass (which warms LIGHTS, cools SHADOWS).

        Stage 2  MID-TONE CHROMATIC SURGE (bell-curve at lum=0.50):
          mid_gate = exp(-0.5 * ((lum - mid_center) / mid_width)^2)
          ch_dev = ch - lum
          R,G,B = clip(lum + ch_dev * (1 + surge_boost * mid_gate), 0, 1)
          Bell-curve centred at lum=0.50 saturates mid-tone colours toward their
          most intense spectral expression -- Nolde's mid-tones are maximum-chroma,
          never grey.  Peak at lum=0.50 is distinct from Moreau's penumbra bell
          at lum=0.28 (s232) and from Chagall's chroma-gate approach (s234).

        Stage 3  VIVID BLOOM HALATION (dual chroma+lum gate):
          vivid_mask = clip((chroma - bloom_chroma_min) / 0.30, 0, 1)
                     * clip((lum_post - bloom_lum_min) / 0.30, 0, 1)
          bloom_halo = gaussian_filter(vivid_mask, bloom_sigma)
          R,G,B += bloom_halo * bloom_warm_r/g/b
          Intense saturated AND luminous zones radiate a warm halation into
          surrounding areas -- models Nolde's incandescent glow quality where
          vivid colour zones seem to emit warm light.  Requires BOTH high chroma
          AND sufficient luminance (dual gate), preventing bloom in vivid-but-dark
          zones (e.g. deep saturated shadows).

        NOVEL vs. existing passes:
        (a) Shadow warmth inversion: dark zones pushed WARM (R+, B-) while lights
            stay cool/neutral -- the OPPOSITE of warm_cool_zone_pass which follows
            academic convention; no prior pass inverts the warm/cool temperature
            relationship between lights and shadows;
        (b) Mid-tone bell-curve chromatic surge at lum=0.50: chroma gate targets
            lum=0.50 (true mid-tones) -- distinct from chagall_lyrical_dream_pass
            (s234) which uses max-min chroma as gate (not luminance) and from
            chromatic_chiaroscuro_pass (s234) which uses lum=0.28 (penumbra);
        (c) Dual chroma+lum gated bloom halation: requires BOTH high chroma AND
            sufficient luminance -- no prior bloom/corona pass uses this dual gate
            (kuindzhi_moonlit_radiance s233 gates corona on lum alone; warm_highlight_
            bloom and radiance_bloom also gate on lum alone).

        shadow_ceil      : Luminance ceiling for shadow warmth inversion.
        shadow_power     : Power exponent for shadow gate (higher = steeper falloff).
        shadow_r_push    : Red channel boost in shadow zones (warmth).
        shadow_b_drop    : Blue channel reduction in shadow zones (warmth).
        mid_center       : Luminance centre of mid-tone chromatic surge bell.
        mid_width        : Standard deviation (sigma) of the surge bell-curve.
        surge_boost      : Peak saturation multiplier in the surge zone.
        bloom_chroma_min : Minimum chroma for vivid bloom trigger.
        bloom_lum_min    : Minimum luminance for vivid bloom trigger.
        bloom_sigma      : Gaussian blur sigma for bloom halation spread.
        bloom_warm_r     : Red channel component of bloom warm tint.
        bloom_warm_g     : Green channel component of bloom warm tint.
        bloom_warm_b     : Blue channel component of bloom warm tint.
        opacity          : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Nolde Incandescent Surge pass (session 235 -- 146th mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Shadow Warmth Inversion
        sc  = float(shadow_ceil)
        sp  = float(shadow_power)
        srp = float(shadow_r_push)
        sbd = float(shadow_b_drop)
        dark_gate = _np.clip((sc - lum) / (sc + 1e-6), 0.0, 1.0) ** sp
        r1 = _np.clip(r0 + dark_gate * srp, 0.0, 1.0)
        g1 = g0
        b1 = _np.clip(b0 - dark_gate * sbd, 0.0, 1.0)

        # Stage 2: Mid-tone Chromatic Surge (bell-curve at mid_center)
        mc  = float(mid_center)
        mw  = float(mid_width)
        sb  = float(surge_boost)
        lum1 = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        mid_gate = _np.exp(-0.5 * ((lum1 - mc) / (mw + 1e-6)) ** 2).astype(_np.float32)
        scale = 1.0 + sb * mid_gate
        r2 = _np.clip(lum1 + (r1 - lum1) * scale, 0.0, 1.0)
        g2 = _np.clip(lum1 + (g1 - lum1) * scale, 0.0, 1.0)
        b2 = _np.clip(lum1 + (b1 - lum1) * scale, 0.0, 1.0)

        # Stage 3: Vivid Bloom Halation (dual chroma + lum gate)
        bcm  = float(bloom_chroma_min)
        blm  = float(bloom_lum_min)
        bsig = float(bloom_sigma)
        bwr  = float(bloom_warm_r)
        bwg  = float(bloom_warm_g)
        bwb  = float(bloom_warm_b)
        lum2 = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)
        chroma2 = (_np.maximum(_np.maximum(r2, g2), b2)
                   - _np.minimum(_np.minimum(r2, g2), b2)).astype(_np.float32)
        chroma_gate = _np.clip((chroma2 - bcm) / (0.30 + 1e-6), 0.0, 1.0)
        lum_gate    = _np.clip((lum2 - blm)   / (0.30 + 1e-6), 0.0, 1.0)
        vivid_mask  = (chroma_gate * lum_gate).astype(_np.float32)
        bloom_halo  = _gf(vivid_mask, bsig).astype(_np.float32)
        r3 = _np.clip(r2 + bloom_halo * bwr, 0.0, 1.0)
        g3 = _np.clip(g2 + bloom_halo * bwg, 0.0, 1.0)
        b3 = _np.clip(b2 + bloom_halo * bwb, 0.0, 1.0)

        # Composite at opacity
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

        n_dark   = int((dark_gate > 0.20).sum())
        n_mid    = int((mid_gate > 0.30).sum())
        n_bloom  = int((bloom_halo > 0.05).sum())
        print(f"    Nolde Incandescent Surge complete "
              f"(dark_px={n_dark} mid_px={n_mid} bloom_px={n_bloom})")
'''

GRANULATION_PASS = r'''
    def paint_pigment_granulation_pass(
        self,
        coarse_sigma:   float = 6.00,
        fine_sigma:     float = 1.20,
        coarse_weight:  float = 0.60,
        fine_weight:    float = 0.40,
        chroma_min:     float = 0.10,
        granule_depth:  float = 0.08,
        valley_r_push:  float = 0.025,
        valley_g_push:  float = 0.012,
        opacity:        float = 0.55,
    ) -> None:
        """
        Pigment Granulation -- session 235 artistic improvement.

        Simulates the characteristic granulation of mineral pigments in wet watercolour
        technique.  Certain heavy-particle pigments (French Ultramarine, Burnt Sienna,
        Manganese Blue, Raw Umber) granulate as they dry: heavy pigment particles settle
        into the paper's micro-valleys while the liquid medium carries finer particles
        to surface peaks, creating a distinctive stippled/mottled clumping texture within
        colour washes.  This pass models the physical settling process:

        Stage 1  MULTI-SCALE GRANULATION TEXTURE:
          coarse_field = gaussian_filter(uniform_noise, coarse_sigma)
          fine_field   = gaussian_filter(uniform_noise_2, fine_sigma)
          granulation  = coarse_weight * coarse_field + fine_weight * fine_field
          [both fields normalised to [-1, 1] before weighting]
          Two independent noise fields at different scales are blended to model the
          two-level structure of granulation: coarse pigment clusters (coarse_sigma)
          within a finer random distribution (fine_sigma).  Multi-scale composition
          is physically motivated -- mineral pigments form clusters of varying sizes.

        Stage 2  CHROMA GATING (more pigment = more granulation):
          chroma = max(R,G,B) - min(R,G,B)
          chroma_gate = clip((chroma - chroma_min) / (1 - chroma_min), 0, 1)
          [low-chroma/neutral areas granulate less: less mineral pigment present]
          Granulation is gated by local chroma -- heavily pigmented (saturated)
          areas granulate more intensely than neutral washes.  Physically correct:
          granulation arises from heavy pigment particles, so neutral near-grey
          areas (low chroma) are mostly binder/gum with little heavy pigment.

        Stage 3  PEAK/VALLEY VALUE VARIATION + VALLEY WARM TINT:
          grain_gated = granulation * chroma_gate
          [peaks: grain_gated > 0 -- slightly lighter (pigment on paper surface)]
          [valleys: grain_gated < 0 -- slightly darker + warm push]
          peak_mask   = clip(grain_gated, 0, 1)
          valley_mask = clip(-grain_gated, 0, 1)
          R,G,B += peak_mask * granule_depth          [lighter peaks]
          R,G,B -= valley_mask * granule_depth        [darker valleys]
          R += valley_mask * valley_r_push            [warm orange-brown valley tint]
          G += valley_mask * valley_g_push            [warm green-earth valley tint]
          Valley tint models the specific property of granulating earth pigments:
          Burnt Sienna and Raw Umber valley-clumps have a characteristic warm
          orange-brown colour distinct from the overall wash hue.

        NOVEL vs. existing passes:
        (a) Dual-frequency coherent noise (coarse_sigma=6 px clusters + fine_sigma=1.2 px
            granules): first pass to use two independent Gaussian-filtered noise fields
            at different scales composed additively; canvas_grain_pass uses a single
            Gaussian-filtered noise; film_grain_overlay_pass uses a single Gaussian noise
            with uniform distribution; no prior pass uses multi-scale noise composition;
        (b) Chroma gating for granulation texture (higher chroma = more grain): physically
            motivated by pigment particle density; prior texture passes (canvas_grain_pass,
            film_grain_overlay_pass) gate on luminance or apply uniformly, not on chroma;
        (c) Directional valley warm tint: valley zones (dark granulation clumps) receive
            a separate warm push (valley_r_push, valley_g_push) modelling the specific
            hue of mineral pigment clumps distinct from the host wash -- no prior texture
            pass applies a hue-shifted tint selectively to the dark granulation zones.

        coarse_sigma   : Gaussian sigma for coarse-scale pigment cluster noise.
        fine_sigma     : Gaussian sigma for fine-scale individual-granule noise.
        coarse_weight  : Blend weight of the coarse field (0-1).
        fine_weight    : Blend weight of the fine field (0-1).
        chroma_min     : Minimum chroma threshold below which granulation is suppressed.
        granule_depth  : Amplitude of the light/dark value variation (0-1).
        valley_r_push  : Red channel boost in dark valley granulation zones.
        valley_g_push  : Green channel boost in dark valley granulation zones.
        opacity        : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Pigment Granulation pass (session 235 improvement)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        rng = _np.random.default_rng(seed=137)

        # Stage 1: Multi-scale granulation texture
        cs = float(coarse_sigma)
        fs = float(fine_sigma)
        cw = float(coarse_weight)
        fw = float(fine_weight)
        noise_c_raw = rng.uniform(0.0, 1.0, (h, w)).astype(_np.float32)
        noise_f_raw = rng.uniform(0.0, 1.0, (h, w)).astype(_np.float32)
        coarse_field = _gf(noise_c_raw, cs)
        fine_field   = _gf(noise_f_raw, fs)
        # Normalise each to [-1, 1]
        def _norm(field):
            mn, mx = field.min(), field.max()
            span = mx - mn + 1e-8
            return (field - mn) / span * 2.0 - 1.0
        coarse_norm = _norm(coarse_field)
        fine_norm   = _norm(fine_field)
        granulation = (cw * coarse_norm + fw * fine_norm).astype(_np.float32)
        # Re-normalise combined field to [-1, 1]
        granulation = _norm(granulation)

        # Stage 2: Chroma gating
        cm_min = float(chroma_min)
        chroma = (_np.maximum(_np.maximum(r0, g0), b0)
                  - _np.minimum(_np.minimum(r0, g0), b0)).astype(_np.float32)
        chroma_gate = _np.clip((chroma - cm_min) / (1.0 - cm_min + 1e-6), 0.0, 1.0)
        grain_gated = granulation * chroma_gate

        # Stage 3: Peak/valley variation + valley warm tint
        gd  = float(granule_depth)
        vrp = float(valley_r_push)
        vgp = float(valley_g_push)
        peak_mask   = _np.clip(grain_gated,  0.0, 1.0)
        valley_mask = _np.clip(-grain_gated, 0.0, 1.0)
        r1 = _np.clip(r0 + peak_mask * gd - valley_mask * gd + valley_mask * vrp,
                      0.0, 1.0)
        g1 = _np.clip(g0 + peak_mask * gd - valley_mask * gd + valley_mask * vgp,
                      0.0, 1.0)
        b1 = _np.clip(b0 + peak_mask * gd - valley_mask * gd, 0.0, 1.0)

        # Composite at opacity
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

        n_peak   = int((peak_mask > 0.10).sum())
        n_valley = int((valley_mask > 0.10).sum())
        n_chroma = int((chroma_gate > 0.20).sum())
        print(f"    Pigment Granulation complete "
              f"(peak_px={n_peak} valley_px={n_valley} chroma_px={n_chroma})")
'''


with open('stroke_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'nolde_incandescent_surge_pass' not in content, 'Pass already exists!'
assert 'paint_pigment_granulation_pass' not in content, 'Pass already exists!'

content = content + NOLDE_PASS + GRANULATION_PASS

with open('stroke_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. stroke_engine.py new length: {len(content)} chars')
