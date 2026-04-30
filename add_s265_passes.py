"""Insert paint_wet_surface_gleam_pass (s265 improvement) and
ury_nocturne_reflection_pass (176th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_wet_surface_gleam_pass (s265 improvement) ─────────────────

GLEAM_PASS = '''
    def paint_wet_surface_gleam_pass(
        self,
        spec_threshold:   float = 0.72,
        streak_sigma:     float = 18.0,
        gleam_r:          float = 0.28,
        gleam_g:          float = 0.20,
        gleam_b:          float = 0.10,
        feather_sigma:    float = 1.5,
        noise_seed:       int   = 265,
        opacity:          float = 0.55,
    ) -> None:
        r"""Wet Surface Gleam -- session 265 artistic improvement.

        THREE-STAGE VERTICAL DOWNWARD LIGHT-TRAIL FROM BRIGHT SOURCES ON RAIN-
        WET SURFACES INSPIRED BY THE PHYSICAL OPTICS OF SPECULAR REFLECTION ON
        RAIN-SLICKED COBBLESTONES (Ury, Sisley, Sickert, c.1880-1920):

        When rain coats a cobblestone or tile surface with a thin continuous film
        of water, every light source above the horizon -- gas lamp, cafe window,
        electric arc -- produces a specular reflection in that film. The geometry
        of the reflection is determined by the Fresnel equations and the geometry
        of the surface relative to the viewer: from a low angle of incidence (the
        viewer looking down at cobblestones a few metres away), the reflection of
        a point source is elongated vertically in the direction away from the
        viewer (downward in the image), because slight variations in surface
        slope across the cobblestone field scatter the reflection angle over a
        range of vertical positions while keeping the horizontal position tightly
        constrained. The result, visible in every Ury nocturne and Sisley river
        painting, is that light sources produce downward "gleam trails" on wet
        surfaces -- narrow, warm, vertically elongated bands of reflected light
        that terminate in the dark surface below each source.

        Stage 1 SPECULAR MASK EXTRACTION: Compute per-pixel luminance;
        build a soft specular mask of all pixels above spec_threshold:
          lum      = 0.299*R + 0.587*G + 0.114*B
          spec_raw = clip((lum - spec_threshold) / max(1 - spec_threshold, 0.01), 0, 1)
          spec_mask = gaussian_filter(spec_raw, sigma=feather_sigma), clamped [0, 1]
        The feathering ensures that only genuinely bright pixels (gas lamps,
        window highlights, sky patches) contribute to the gleam trail.
        NOVEL: (a) LUMINANCE-THRESHOLD SPECULAR MASK WITH GAUSSIAN FEATHER --
        first improvement to extract a soft specular mask using per-pixel lum
        clipped above a configurable spec_threshold then feathered with a small
        Gaussian; paint_luminance_stretch_pass globally stretches luminance; no
        prior improvement builds a specular-threshold mask specifically to guide
        a vertical streak simulating physical wet-surface optics.

        Stage 2 VERTICAL GAUSSIAN STREAK: Apply 1D Gaussian blur along the
        vertical axis (axis=0) to the specular mask with sigma=streak_sigma:
          streak = gaussian_filter1d(spec_mask, sigma=streak_sigma, axis=0)
          streak = clip(streak / (streak.max() + 1e-6), 0, 1)
        The 1D vertical blur elongates the bright specular spots downward
        (and slightly upward for reflections above the source), producing the
        characteristic narrow downward gleam trail of a gas lamp reflection
        on rain-wet cobblestones. streak_sigma=18.0 gives ~36-pixel trails at
        full resolution, matching Ury\'s observed gleam lengths.
        NOVEL: (b) 1D VERTICAL GAUSSIAN STREAK FROM SPECULAR MASK -- first
        improvement to apply gaussian_filter1d along axis=0 to a specular-
        threshold mask to create downward "light trail" streaks; paint_sfumato_
        contour_dissolution_pass uses Gaussian blur for horizontal edge softening;
        no prior improvement applies 1D vertical Gaussian blur specifically to a
        specular mask to model the elongated reflection geometry of light sources
        on rain-wet surfaces.

        Stage 3 WARM-TINTED GLEAM COMPOSITE: Apply a warm-tinted gleam using
        the streak as a lift guide, with per-channel warm weights:
          r_lift = streak * gleam_r
          g_lift = streak * gleam_g  (gleam_g < gleam_r)
          b_lift = streak * gleam_b  (gleam_b < gleam_g)
          R_out  = clip(R + r_lift, 0, 1), G_out, B_out
        gleam_r > gleam_g > gleam_b ensures the gleam is warm (amber-ivory)
        rather than white, matching the warm colour temperature of gas lamps
        and cafe windows that Ury depicted.
        NOVEL: (c) PER-CHANNEL WARM-TINTED GLEAM LIFT FROM VERTICAL STREAK --
        first improvement to use a vertically-streaked specular mask with
        asymmetric per-channel weights (R > G > B) to place warm downward gleam
        marks on the canvas; paint_golden_ground_pass applies warm tinting
        globally; no prior improvement uses specular-extract-then-vertically-
        streak followed by a warm per-channel tint to create warm, downward-
        elongated gleam streaks specifically from bright-source pixels only.
        """
        print("    Wet Surface Gleam pass (session 265 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf, gaussian_filter1d as _gf1d

        surface = self.canvas.surface
        orig = _np.frombuffer(surface.get_data(), dtype=_np.uint8).reshape(
            (self.canvas.h, self.canvas.w, 4)).copy()
        h, w = orig.shape[:2]

        b0 = orig[:, :, 0].astype(_np.float32) / 255.0
        g0 = orig[:, :, 1].astype(_np.float32) / 255.0
        r0 = orig[:, :, 2].astype(_np.float32) / 255.0

        lum = (0.299 * r0 + 0.587 * g0 + 0.114 * b0).astype(_np.float32)

        # ── Stage 1: Specular Mask Extraction ─────────────────────────────────
        st       = float(spec_threshold)
        denom    = max(1.0 - st, 0.01)
        spec_raw = _np.clip((lum - st) / denom, 0.0, 1.0).astype(_np.float32)
        fsig     = max(float(feather_sigma), 0.5)
        spec_mask = _np.clip(_gf(spec_raw, sigma=fsig), 0.0, 1.0).astype(_np.float32)

        # ── Stage 2: Vertical Gaussian Streak ─────────────────────────────────
        ssig   = max(float(streak_sigma), 1.0)
        streak = _gf1d(spec_mask, sigma=ssig, axis=0).astype(_np.float32)
        streak = _np.clip(streak / (streak.max() + 1e-6), 0.0, 1.0).astype(_np.float32)

        # ── Stage 3: Warm-Tinted Gleam Composite ──────────────────────────────
        gr = float(gleam_r)
        gg = float(gleam_g)
        gb = float(gleam_b)

        r1 = _np.clip(r0 + streak * gr, 0.0, 1.0).astype(_np.float32)
        g1 = _np.clip(g0 + streak * gg, 0.0, 1.0).astype(_np.float32)
        b1 = _np.clip(b0 + streak * gb, 0.0, 1.0).astype(_np.float32)

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

        spec_px   = int((spec_mask > 0.05).sum())
        streak_px = int((streak > 0.05).sum())
        gleam_px  = int((streak * gr > 0.005).sum())
        print(f"    Wet Surface Gleam complete "
              f"(spec_px={spec_px}, streak_px={streak_px}, gleam_px={gleam_px})")
'''

# ── Pass 2: ury_nocturne_reflection_pass (176th mode) ────────────────────────

URY_PASS = '''
    def ury_nocturne_reflection_pass(
        self,
        sky_fraction:           float = 0.45,
        pavement_fraction:      float = 0.40,
        h_blur_sigma:           float = 18.0,
        v_blur_sigma:           float = 3.5,
        reflection_attenuation: float = 0.38,
        reflection_opacity:     float = 0.62,
        lamp_threshold:         float = 0.62,
        corona_sigma:           float = 22.0,
        corona_strength:        float = 0.18,
        amber_dr:               float = 0.14,
        amber_dg:               float = 0.04,
        amber_db_cut:           float = 0.12,
        shadow_threshold:       float = 0.32,
        shadow_r_scale:         float = 0.74,
        shadow_g_scale:         float = 0.82,
        shadow_b_lift:          float = 0.022,
        shadow_strength:        float = 0.70,
        noise_seed:             int   = 265,
        opacity:                float = 0.78,
    ) -> None:
        r"""Ury Nocturne Reflection -- session 265, 176th distinct mode.

        THREE-STAGE NOCTURNE STREET REFLECTION TECHNIQUE INSPIRED BY
        LESSER URY\'S BERLIN NIGHT SCENES (c.1888-1920):

        Lesser Ury (1861-1931) was a German-Jewish Impressionist who spent most
        of his career painting Berlin\'s cafes, streets, and parks. His mature
        work in the 1890s-1900s established him as one of the foremost painters
        of the nocturne street scene in European art. Working from the charged
        intersection of Impressionism, Japonisme, and the new electric and gas
        lighting of the modern city, Ury developed a distinctive visual language:
        prussian-blue / indigo shadow zones that make the warm amber of gas lamps
        and cafe interiors appear almost incandescent; a technique of depicting
        wet cobblestones by treating the pavement as a mirror that inverts and
        elongates the light sources above it; and a characteristic "corona" around
        light sources -- a Gaussian bloom of warm amber spreading into atmospheric
        haze -- that gives his nocturnes their quality of urban fog and gaslight
        mystery. Unlike Monet\'s haystacks (nature) or Whistler\'s nocturnes
        (aestheticism), Ury\'s paintings are fundamentally about the new,
        specifically URBAN experience of artificial light: the way it pools and
        reflects and halos in a city at night, creating islands of warmth in a
        sea of prussian dark.

        Stage 1 WET PAVEMENT VERTICAL MIRROR REFLECTION: Take the upper
        sky_fraction rows of the canvas as the "light source zone"; flip them
        vertically to create a physical mirror image; apply asymmetric Gaussian
        blur (heavy horizontal: sigma=h_blur_sigma to elongate reflections along
        the pavement; light vertical: sigma=v_blur_sigma for softening); darken
        by reflection_attenuation (water absorbs ~62% of incident light); then
        composite over the lower pavement_fraction rows at reflection_opacity:
          source_zone  = canvas[0 : sky_rows, :, :]
          mirror       = source_zone[::-1, :, :]    (vertical flip)
          mirror_blur  = gaussian_filter(mirror, sigma=(v_blur, h_blur))
          mirror_dark  = mirror_blur * reflection_attenuation
          canvas[pave_start:, :, :] = blend(canvas, mirror_dark, reflection_opacity)
        NOVEL: (a) UPPER-CANVAS VERTICAL FLIP + ASYMMETRIC GAUSSIAN BLUR +
        LUMINANCE ATTENUATION COMPOSITED INTO LOWER CANVAS TO SIMULATE WET
        PAVEMENT MIRROR REFLECTIONS -- first pass to extract a configurable
        sky_fraction of the canvas, flip it vertically, apply a 2D Gaussian
        with DIFFERENT sigma values on each axis (heavy horizontal for rain-
        elongated reflections, light vertical for softening), then darken and
        composite into the lower pavement_fraction; paint_sfumato_focus_pass
        blurs specific regions uniformly; no prior pass creates pavement-plane
        reflections by flipping upper canvas content with asymmetric per-axis
        blur and luminance attenuation.

        Stage 2 GAS-LAMP AMBER CORONA: Build a warm amber corona around light
        sources. Identify pixels above lamp_threshold by luminance; shift those
        pixels toward warm amber by adding amber increments (amber_dr, amber_dg)
        and subtracting from blue (amber_db_cut); Gaussian-blur the warm-amber
        excess at sigma=corona_sigma to simulate atmospheric diffusion; composite
        at corona_strength:
          lamp_mask  = clip(lum - lamp_threshold, 0, 1) / (1 - lamp_threshold)
          r_excess   = clip(r + amber_dr * lamp_mask, 0, 1) - r
          g_excess   = clip(g + amber_dg * lamp_mask, 0, 1) - g
          b_excess   = clip(b - amber_db_cut * lamp_mask, 0, 1) - b
          r_glow     = gaussian_filter(r_excess * lamp_mask, corona_sigma)
          R_out      = R + r_glow * corona_strength
        NOVEL: (b) LUMINANCE-GATED WARM-AMBER HUE SHIFT FOLLOWED BY GAUSSIAN
        DIFFUSION TO CREATE GAS-LAMP ATMOSPHERIC CORONA -- first pass to extract
        a luminance-threshold lamp mask, apply differential per-channel warm-amber
        shift (adding R/G, subtracting B) specifically to bright pixels only, then
        Gaussian-blur the warm excess to create a spreading amber corona simulating
        gaslight atmospheric scattering; paint_halation_pass spreads achromatic
        luminance outward from bright zones; no prior pass applies warm-amber hue
        shifting to a luminance-gated bright mask followed by Gaussian diffusion of
        the warm excess to create specifically amber (not white) coronas.

        Stage 3 PRUSSIAN BLUE NIGHT-SHADOW COOLER: For all pixels below
        shadow_threshold luminance, cool the shadow hue toward prussian blue by
        applying differential per-channel scaling and a slight blue lift:
          r_out = r * shadow_r_scale                  (< 1, reduces red)
          g_out = g * shadow_g_scale                  (< 1, reduces green less)
          b_out = clip(b + shadow_b_lift, 0, 1)        (slight blue lift in darks)
        Blend the cooled shadow at shadow_strength, gated by
          shadow_mask = clip(1 - lum / shadow_threshold, 0, 1):
          R_final = R*(1 - gate) + r_out*gate,  gate = shadow_mask * shadow_strength
        NOVEL: (c) DIFFERENTIAL PER-CHANNEL SCALING WITH BLUE LIFT GATED BY
        SHADOW LUMINANCE MASK TO CREATE PRUSSIAN-BLUE NIGHT SHADOWS -- first pass
        to apply asymmetric per-channel factors (R*scale_r < 1, G*scale_g < 1,
        B + lift > 0) specifically to sub-threshold dark pixels only, shifting
        their hue toward prussian blue while leaving mid-tones and highlights
        untouched; paint_warm_cool_separation_pass divides the canvas by luminance
        but applies global warm/cool shifts; no prior pass applies configurable
        per-channel differential scaling specifically to the low-luminance shadow
        zone only to cool darks toward prussian blue / indigo in the manner of
        Ury, Sickert, or the Paris Impressionist nocturne tradition.
        """
        print("    Ury Nocturne Reflection pass (session 265, 176th mode)...")

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

        r1 = r0.copy()
        g1 = g0.copy()
        b1 = b0.copy()

        # ── Stage 1: Wet Pavement Vertical Mirror Reflection ──────────────────
        sky_rows  = max(1, int(h * float(sky_fraction)))
        pave_rows = max(1, int(h * float(pavement_fraction)))
        pave_start = h - pave_rows

        src_r = r1[:sky_rows, :].copy()
        src_g = g1[:sky_rows, :].copy()
        src_b = b1[:sky_rows, :].copy()

        mir_r = src_r[::-1, :].copy()
        mir_g = src_g[::-1, :].copy()
        mir_b = src_b[::-1, :].copy()

        hsig = max(float(h_blur_sigma), 1.0)
        vsig = max(float(v_blur_sigma), 0.5)
        mir_r = _gf(mir_r, sigma=(vsig, hsig)).astype(_np.float32)
        mir_g = _gf(mir_g, sigma=(vsig, hsig)).astype(_np.float32)
        mir_b = _gf(mir_b, sigma=(vsig, hsig)).astype(_np.float32)

        att = float(reflection_attenuation)
        mir_r = (mir_r * att).astype(_np.float32)
        mir_g = (mir_g * att).astype(_np.float32)
        mir_b = (mir_b * att).astype(_np.float32)

        use_rows = min(pave_rows, mir_r.shape[0])
        ref_op   = float(reflection_opacity)

        for i in range(use_rows):
            dst_row = pave_start + i
            if dst_row >= h:
                break
            src_i = min(i, mir_r.shape[0] - 1)
            r1[dst_row, :] = _np.clip(
                r1[dst_row, :] * (1.0 - ref_op) + mir_r[src_i, :] * ref_op, 0.0, 1.0)
            g1[dst_row, :] = _np.clip(
                g1[dst_row, :] * (1.0 - ref_op) + mir_g[src_i, :] * ref_op, 0.0, 1.0)
            b1[dst_row, :] = _np.clip(
                b1[dst_row, :] * (1.0 - ref_op) + mir_b[src_i, :] * ref_op, 0.0, 1.0)

        refl_px = use_rows * w

        # ── Stage 2: Gas-Lamp Amber Corona ────────────────────────────────────
        lum1       = (0.299 * r1 + 0.587 * g1 + 0.114 * b1).astype(_np.float32)
        lt         = float(lamp_threshold)
        lamp_denom = max(1.0 - lt, 0.01)
        lamp_mask  = _np.clip((lum1 - lt) / lamp_denom, 0.0, 1.0).astype(_np.float32)

        adr  = float(amber_dr)
        adg  = float(amber_dg)
        adb  = float(amber_db_cut)
        csig = max(float(corona_sigma), 1.0)
        cst  = float(corona_strength)

        warm_r_excess = (_np.clip(r1 + adr * lamp_mask, 0.0, 1.0) - r1).astype(_np.float32)
        warm_g_excess = (_np.clip(g1 + adg * lamp_mask, 0.0, 1.0) - g1).astype(_np.float32)
        warm_b_excess = (_np.clip(b1 - adb * lamp_mask, 0.0, 1.0) - b1).astype(_np.float32)

        glow_r = _gf((warm_r_excess * lamp_mask).astype(_np.float32), sigma=csig)
        glow_g = _gf((warm_g_excess * lamp_mask).astype(_np.float32), sigma=csig)
        glow_b = _gf((warm_b_excess * lamp_mask).astype(_np.float32), sigma=csig)

        r2 = _np.clip(r1 + glow_r * cst, 0.0, 1.0).astype(_np.float32)
        g2 = _np.clip(g1 + glow_g * cst, 0.0, 1.0).astype(_np.float32)
        b2 = _np.clip(b1 + glow_b * cst, 0.0, 1.0).astype(_np.float32)
        lamp_px = int((lamp_mask > 0.1).sum())

        # ── Stage 3: Prussian Blue Night-Shadow Cooler ────────────────────────
        lum2 = (0.299 * r2 + 0.587 * g2 + 0.114 * b2).astype(_np.float32)
        st2  = float(shadow_threshold)
        ss   = float(shadow_strength)
        shdw = _np.clip(1.0 - lum2 / (st2 + 1e-6), 0.0, 1.0).astype(_np.float32)
        gate = (shdw * ss).astype(_np.float32)

        rs = float(shadow_r_scale)
        gs = float(shadow_g_scale)
        bl = float(shadow_b_lift)

        r3_cool = _np.clip(r2 * rs, 0.0, 1.0).astype(_np.float32)
        g3_cool = _np.clip(g2 * gs, 0.0, 1.0).astype(_np.float32)
        b3_cool = _np.clip(b2 + bl, 0.0, 1.0).astype(_np.float32)

        r3 = (r2 * (1.0 - gate) + r3_cool * gate).astype(_np.float32)
        g3 = (g2 * (1.0 - gate) + g3_cool * gate).astype(_np.float32)
        b3 = (b2 * (1.0 - gate) + b3_cool * gate).astype(_np.float32)

        shadow_px = int((shdw > 0.5).sum())

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

        print(f"    Ury Nocturne Reflection complete "
              f"(refl_px={refl_px}, lamp_px={lamp_px}, shadow_px={shadow_px})")
'''

# ── Inject into stroke_engine.py ──────────────────────────────────────────────

ENGINE_PATH = os.path.join(REPO, "stroke_engine.py")

with open(ENGINE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

already_gleam = "paint_wet_surface_gleam_pass" in src
already_ury   = "ury_nocturne_reflection_pass" in src

if already_gleam and already_ury:
    print("Both passes already present in stroke_engine.py -- nothing to do.")
    sys.exit(0)

additions = ""
if not already_gleam:
    additions += GLEAM_PASS
if not already_ury:
    additions += "\n" + URY_PASS

src = src.rstrip("\n") + "\n" + additions + "\n"

with open(ENGINE_PATH, "w", encoding="utf-8") as f:
    f.write(src)

if not already_gleam:
    print("Inserted paint_wet_surface_gleam_pass into stroke_engine.py.")
if not already_ury:
    print("Inserted ury_nocturne_reflection_pass into stroke_engine.py.")
