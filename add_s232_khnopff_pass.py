"""Append khnopff_frozen_reverie_pass (143rd mode) to stroke_engine.py."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

KHNOPFF_PASS = '''
    def khnopff_frozen_reverie_pass(
        self,
        desat_str:       float = 0.55,
        cool_shift:      float = 0.055,
        reverie_sigma:   float = 1.80,
        mist_str:        float = 0.50,
        bright_start:    float = 0.58,
        bright_range:    float = 0.25,
        pearl_b_boost:   float = 0.030,
        pearl_start:     float = 0.70,
        opacity:         float = 0.80,
    ) -> None:
        """
        Khnopff Frozen Reverie -- session 232: ONE HUNDRED AND FORTY-THIRD distinct mode.

        Implements Fernand Khnopff (1858-1921) Belgian Symbolist atmosphere:
        everything muted toward cool silver-grey, forms dissolved into atmospheric
        mist in shadows and midtones, while highlights remain crisp and pearl-cool.
        The effect: a remembered vision seen through fine Belgian mist, emotionally
        suspended between waking and dreaming.

        Three-stage mechanism:

        Stage 1 COOL SILVER VEIL (desaturation toward cool grey):
          ch_desat = lum + (ch - lum) * (1 - desat_str)  [pull toward grey]
          cool_gate = clip(1 - lum/0.65, 0, 1)  [strongest in shadow, zero at lum=0.65]
          B_desat += cool_shift * cool_gate
          R_desat -= cool_shift * 0.45 * cool_gate
          [Shadows become cool blue-grey; mid-tones cool slightly; highlights left warmer]

        Stage 2 REVERIE MIST BLUR (atmospheric dissolution in non-highlights):
          blur_r,g,b = gaussian_filter(ch_desat, reverie_sigma)
          bright_gate = clip((lum - bright_start) / bright_range, 0, 1)  [0→shadow, 1→highlight]
          mist_blend = mist_str * (1 - bright_gate)
          ch_mist = ch_blur * mist_blend + ch_desat * (1 - mist_blend)
          [Highlights crisp; shadows and midtones dissolved into atmospheric softness]

        Stage 3 PEARL HIGHLIGHT COOL TINT:
          pearl_gate = clip((lum - pearl_start) / 0.20, 0, 1)  [activates in bright zone]
          B_out += pearl_gate * pearl_b_boost
          [Adds characteristic cool-white pearl quality to brightest highlights;
           distinct from Moreau's warm gold -- Khnopff highlights are pearl, not gold]

        NOVEL vs. existing passes:
        (a) Simultaneous global cool desaturation (pulling toward blue-grey, not neutral
            grey) + luminance-gated atmospheric mist blur -- no prior pass combines both;
            hammershoi_grey_interior_pass uses a midtone bell grey veil + unidirectional
            window gradient (very different spatial logic);
        (b) Mist blur that preserves crisp highlights via bright_gate: the blur amount
            is 0 in bright zones, maximum in shadows -- inverse of midtone_clarity_pass
            which sharpens midtones; no prior pass applies selective blur by luminance;
        (c) Cool pearl tint in highlights (B+ at lum>pearl_start): opposite of
            moreau_jeweled_ornament_pass warm gilding; models the Belgian grey-light
            highlight quality (north European light, not Mediterranean gold);
        (d) The cool_gate for desaturation is strongest in shadows (inversely luminance-
            gated): shadows are coolest, mid-tones slightly cool, highlights neutral --
            the opposite of most prior passes which work from neutral darkness outward.

        desat_str     : Desaturation strength (0=no change, 1=fully grey).
        cool_shift    : Blue channel boost in shadow/mid zones; R reduced proportionally.
        reverie_sigma : Gaussian sigma for atmospheric mist blur.
        mist_str      : Maximum mist blend fraction (in darkest zones).
        bright_start  : Luminance at which mist blur begins to fade (highlight preservation).
        bright_range  : Luminance range over which mist fades from mist_str to 0.
        pearl_b_boost : Blue channel boost in brightest highlights (cool pearl quality).
        pearl_start   : Luminance at which pearl cool tint activates.
        opacity       : Final composite opacity.
        """
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        print("    Khnopff Frozen Reverie pass (session 232 -- 143rd mode)...")

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # Stage 1: Cool silver veil -- desaturation + cool push in shadow/mid zones
        ds = float(desat_str)
        r1 = _np.clip(lum + (r0 - lum) * (1.0 - ds), 0.0, 1.0)
        g1 = _np.clip(lum + (g0 - lum) * (1.0 - ds), 0.0, 1.0)
        b1 = _np.clip(lum + (b0 - lum) * (1.0 - ds), 0.0, 1.0)

        cool_gate = _np.clip(1.0 - lum / (0.65 + 1e-6), 0.0, 1.0).astype(_np.float32)
        cs = float(cool_shift)
        r1 = _np.clip(r1 - cs * 0.45 * cool_gate, 0.0, 1.0)
        b1 = _np.clip(b1 + cs * cool_gate, 0.0, 1.0)

        # Stage 2: Reverie mist blur -- atmospheric dissolution gated away from highlights
        rs = float(reverie_sigma)
        r_blur = _gf(r1, rs).astype(_np.float32)
        g_blur = _gf(g1, rs).astype(_np.float32)
        b_blur = _gf(b1, rs).astype(_np.float32)

        bs_val = float(bright_start)
        br_val = float(bright_range)
        bright_gate = _np.clip((lum - bs_val) / (br_val + 1e-6), 0.0, 1.0).astype(_np.float32)
        ms = float(mist_str)
        mist_blend = ms * (1.0 - bright_gate)

        r2 = r_blur * mist_blend + r1 * (1.0 - mist_blend)
        g2 = g_blur * mist_blend + g1 * (1.0 - mist_blend)
        b2 = b_blur * mist_blend + b1 * (1.0 - mist_blend)

        # Stage 3: Pearl highlight cool tint -- B+ in brightest zones
        ps = float(pearl_start)
        pearl_gate = _np.clip((lum - ps) / (0.20 + 1e-6), 0.0, 1.0).astype(_np.float32)
        pb = float(pearl_b_boost)
        b3 = _np.clip(b2 + pearl_gate * pb, 0.0, 1.0)
        r3 = r2
        g3 = g2

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

        n_mist   = int((mist_blend > 0.3).sum())
        n_crisp  = int((bright_gate > 0.5).sum())
        n_pearl  = int((pearl_gate > 0.2).sum())
        print(f"    Khnopff Frozen Reverie complete "
              f"(mist_px={n_mist} crisp_px={n_crisp} pearl_px={n_pearl})")
'''

with open('stroke_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content + KHNOPFF_PASS

with open('stroke_engine.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Khnopff pass appended. New length: {len(new_content)} chars")
