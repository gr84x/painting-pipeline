"""Insert paint_shadow_temperature_pass (s281 improvement) and
shishkin_forest_density_pass (192nd mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_shadow_temperature_pass (s281 improvement) ─────────────────

SHADOW_TEMPERATURE_PASS = '''
    def paint_shadow_temperature_pass(
        self,
        highlight_percentile:  float = 85.0,
        shadow_threshold:      float = 0.36,
        shadow_softness:       float = 0.12,
        shadow_strength:       float = 0.32,
        highlight_reinforce:   float = 0.18,
        highlight_threshold:   float = 0.70,
        bias_scale:            float = 3.5,
        cool_shadow_color:     tuple = (0.28, 0.30, 0.50),
        warm_shadow_color:     tuple = (0.58, 0.40, 0.20),
        cool_highlight_color:  tuple = (0.72, 0.84, 0.92),
        warm_highlight_color:  tuple = (0.92, 0.82, 0.55),
        opacity:               float = 0.80,
    ) -> None:
        r"""Shadow Temperature (Warm-Light / Cool-Shadow Doctrine) -- s281 improvement.

        THE CHROMATIC OPPOSITION PRINCIPLE OF CLASSICAL OIL PAINTING:

        Every great colorist from Rubens to Velazquez to Sorolla understood the
        principle of OPPOSING COLOR TEMPERATURES between lights and shadows: when
        the dominant light source is warm (golden hour, candlelight, firelight),
        the shadows must lean cool (violet, blue-gray); when the light is cool
        (overcast sky, north light, moonlight), the shadows should carry warmth
        (amber, raw sienna, reddish earth). This opposition creates the chromatic
        tension that makes a painting vibrate with light -- it is the fundamental
        reason that academic oil paintings feel luminous even in areas of
        deep shadow.

        The principle was articulated by Chevreul in "The Law of Simultaneous
        Contrast of Colours" (1839) and was the basis of Impressionist color
        doctrine. It appears in Monet's blue shadows on snow, in Sorolla's
        cool violet shadows in Mediterranean sunlight, in Rembrandt's warm
        amber fill-light opposing his cool main-light backgrounds. The system
        is asymmetric: the light side gets its full temperature, the shadow
        side gets the opposite, creating a dialogue across the value range that
        unifies the composition through contrast.

        No prior improvement pass in this engine dynamically measures the
        existing image's light temperature and uses that measurement to drive
        an opposing push in the shadow zones. Prior warm/cool passes either:
        (a) apply fixed-direction saturation amplification based on hue
            classification (paint_warm_cool_separation_pass, s251);
        (b) apply hardcoded target colors to specific luminance zones
            (goya: dark brown in shadows; fechin: raw sienna in midtones;
             blake: gold in highlights -- all hardcoded, not data-driven);
        (c) apply uniform cool haze by depth estimate
            (paint_depth_atmosphere_pass, s268 -- not driven by light temp).

        This pass is the first to: (1) SAMPLE the existing image's highlight
        pixels to measure the dominant light color temperature; (2) COMPUTE
        the opposing temperature as the response; and (3) APPLY the opposing
        push to shadow zones with strength proportional to the measured bias.

        Stage 1 HIGHLIGHT TEMPERATURE SAMPLING (Light Color Measurement):
        Extract the highlight zone: pixels where L > percentile(L,
        highlight_percentile). Compute the mean RGB of these pixels:
          (R_hi_mean, G_hi_mean, B_hi_mean)
        Compute warm_bias = R_hi_mean - B_hi_mean. Positive warm_bias means
        the dominant light is warm (red-orange-yellow); negative means cool
        (blue-cyan-green). The magnitude of warm_bias indicates how
        strongly colored the light source is.
        NOVEL: (a) DYNAMIC LIGHT TEMPERATURE FROM HIGHLIGHT SAMPLING --
        no prior improvement pass reads the existing canvas to measure the
        current dominant light color temperature and uses it to drive
        chromatic decisions. All prior color-push passes hardcode their
        target colors. This pass is data-adaptive: the push direction changes
        based on what the image contains.

        Stage 2 SHADOW ZONE SOFT MASKING (Smooth Shadow Identification):
        Compute shadow_mask = clip((shadow_threshold - L) / shadow_softness,
        0, 1). Values in (shadow_threshold - shadow_softness, shadow_threshold)
        form a soft transition band; pixels below that band get mask = 1.0.
        The soft mask avoids the hard edge artifacts that threshold clipping
        would produce at the shadow boundary.

        Stage 3 OPPOSING CHROMATIC PUSH IN SHADOWS (Complementary Temperature):
        Determine opposing color from warm_bias:
          if warm_bias > 0: shadow_target = cool_shadow_color (violet-blue)
          if warm_bias < 0: shadow_target = warm_shadow_color (amber-ochre)
        Compute bias_strength = clip(abs(warm_bias) * bias_scale, 0, 1).
        Push strength = shadow_strength * shadow_mask * bias_strength.
        C_shadow = C + (shadow_target - C) * push_strength
        NOVEL: (b) BIAS-ADAPTIVE OPPOSING COLOR PUSH -- the direction of
        the shadow color push is computed from the image measurement rather
        than being hardcoded. A warm image gets cool shadows; a cool image
        gets warm shadows. The strength scales with how extreme the measured
        bias is: a strongly golden-hour painting gets a stronger cool-shadow
        push than a nearly neutral image. No prior pass dynamically determines
        push direction from measured data.

        Stage 4 AMBIENT LIGHT REINFORCEMENT IN HIGHLIGHTS (Temperature Dialogue):
        In the highlight zone (L > highlight_threshold), lightly reinforce
        the dominant light temperature:
          if warm_bias > 0: push toward warm_highlight_color (warm gold)
          if warm_bias < 0: push toward cool_highlight_color (cool sky)
        push = highlight_reinforce * highlight_mask * bias_strength
        highlight_mask = clip((L - highlight_threshold) / (1 - highlight_threshold), 0, 1)
        This creates a warm/cool DIALOGUE across the full value range:
        highlights pull in the dominant direction, shadows pull in the
        opposite direction, creating the chromatic tension that distinguishes
        great colorist painting.
        NOVEL: (c) SIMULTANEOUS DUAL-ZONE TEMPERATURE DIALOGUE -- highlights
        reinforced in dominant temperature while shadows receive the opposing
        temperature; this creates the chromatic conversation across value
        range (warm lights/cool shadows or cool lights/warm shadows) that
        prior passes do not produce because they operate on a single value
        zone without the opposing counterpart. The dual application in a
        single pass is key: it produces a coherent temperature system, not
        isolated zone effects.
        """
        print("    Shadow Temperature pass (session 281 improvement)...")

        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H, W = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)

        # Stage 1: Highlight temperature sampling
        hp = float(highlight_percentile)
        L_hi_thresh = float(_np.percentile(L, hp))
        hi_mask = (L > L_hi_thresh).astype(_np.float32)
        hi_count = max(float(hi_mask.sum()), 1.0)
        R_hi_mean = float((R * hi_mask).sum()) / hi_count
        G_hi_mean = float((G * hi_mask).sum()) / hi_count
        B_hi_mean = float((B * hi_mask).sum()) / hi_count
        warm_bias  = R_hi_mean - B_hi_mean   # positive = warm, negative = cool

        bs = float(bias_scale)
        bias_strength = min(abs(warm_bias) * bs, 1.0)

        # Stage 2: Shadow zone soft masking
        st = float(shadow_threshold)
        ss = max(float(shadow_softness), 0.01)
        shadow_mask = _np.clip((st - L) / ss, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Opposing chromatic push in shadows
        if warm_bias >= 0.0:
            # Warm light → cool shadows
            sr = float(cool_shadow_color[0])
            sg = float(cool_shadow_color[1])
            sb = float(cool_shadow_color[2])
        else:
            # Cool light → warm shadows
            sr = float(warm_shadow_color[0])
            sg = float(warm_shadow_color[1])
            sb = float(warm_shadow_color[2])

        sstr = float(shadow_strength)
        push = shadow_mask * (sstr * bias_strength)
        R1 = _np.clip(R + (sr - R) * push, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (sg - G) * push, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (sb - B) * push, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Ambient light reinforcement in highlights (temperature dialogue)
        ht = float(highlight_threshold)
        highlight_mask = _np.clip((L - ht) / max(1.0 - ht, 0.01), 0.0, 1.0
                                  ).astype(_np.float32)

        if warm_bias >= 0.0:
            # Warm light: reinforce warmth in highlights
            hr = float(warm_highlight_color[0])
            hg = float(warm_highlight_color[1])
            hb = float(warm_highlight_color[2])
        else:
            # Cool light: reinforce cool in highlights
            hr = float(cool_highlight_color[0])
            hg = float(cool_highlight_color[1])
            hb = float(cool_highlight_color[2])

        hstr = float(highlight_reinforce)
        hpush = highlight_mask * (hstr * bias_strength)
        R2 = _np.clip(R1 + (hr - R1) * hpush, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (hg - G1) * hpush, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (hb - B1) * hpush, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R2 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G2 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B2 - B) * op, 0.0, 1.0).astype(_np.float32)

        shadow_px   = int((shadow_mask > 0.1).sum())
        highlight_px = int((highlight_mask > 0.1).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Shadow Temperature complete "
              f"(warm_bias={warm_bias:+.3f}, bias_strength={bias_strength:.3f}, "
              f"shadow_px={shadow_px}, highlight_px={highlight_px})")

'''

# ── Pass 2: shishkin_forest_density_pass (192nd mode) ─────────────────────────

SHISHKIN_FOREST_PASS = '''
    def shishkin_forest_density_pass(
        self,
        bark_vlong:          int   = 22,
        bark_vshort:         int   = 2,
        bark_strength:       float = 0.35,
        dapple_sigma:        float = 4.0,
        dapple_threshold:    float = 0.012,
        dapple_r:            float = 0.64,
        dapple_g:            float = 0.72,
        dapple_b:            float = 0.38,
        dapple_strength:     float = 0.28,
        floor_threshold:     float = 0.32,
        floor_softness:      float = 0.14,
        floor_r:             float = 0.52,
        floor_g:             float = 0.34,
        floor_b:             float = 0.14,
        floor_strength:      float = 0.30,
        haze_threshold:      float = 0.20,
        haze_sigma:          float = 2.5,
        haze_r:              float = 0.50,
        haze_g:              float = 0.58,
        haze_b:              float = 0.64,
        haze_strength:       float = 0.32,
        opacity:             float = 0.90,
    ) -> None:
        r"""Shishkin Forest Density (Russian Realism / Forest Interior) -- 192nd mode.

        IVAN IVANOVICH SHISHKIN (1832-1898) -- RUSSIAN REALIST;
        MASTER OF THE FOREST INTERIOR AND BARK TEXTURE:

        Ivan Shishkin was born in Yelabuga (now Tatarstan) to a merchant family.
        He studied at the Moscow School of Painting, then at the Imperial Academy
        of Arts in St. Petersburg under Sokol, and finally in Dusseldorf under
        Calame -- a training that gave him an almost scientific command of natural
        forms. He traveled extensively, sketching forests with the same obsessive
        attention to botanical detail that Durer brought to grass and hare.
        He was a founding member of the Peredvizhniki (Wanderers) along with
        Repin, Kramskoi, and Savitsky, and became their resident landscape
        specialist -- the one painter among them who could render a pine needle
        with the same authority as a pine forest.

        SHISHKIN\'S THREE OBSESSIONS:
        1. BARK TEXTURE -- The rough, plated bark of mature Russian pines was
           Shishkin\'s signature subject. He rendered the vertical grain, the
           horizontal shadow bands, the warm amber glow of the lit side, and
           the cool gray-green of lichen-covered shaded surfaces with a
           specificity that no other 19th-century painter approached. His
           tree trunks are almost architectural in their structural clarity.
        2. DAPPLED CANOPY LIGHT -- Light filtering through a pine canopy creates
           irregular alternating zones of bright sunlit needles and deep cool
           shadow. Shishkin rendered this as a mosaic of carefully observed
           values, never smoothing the complexity into generic green masses.
           His canopies have a density and layered intricacy visible even in
           photographs of his paintings.
        3. FOREST ATMOSPHERE -- Despite his documentary precision, Shishkin\'s
           forests have a palpable atmosphere: cool blue-green haze in the
           deeper recesses, warm amber glow where the forest floor catches
           late afternoon sun, the sense of moist, resinous air between the
           trunks. He achieved this through careful value management: very
           dark accents in the deepest shadow recesses, very warm lights
           on sun-facing bark, and a graduated cool recession into depth.

        SELECTED WORKS:
        - "Pine Forest" (1872) -- dense interior, shafts of light
        - "Rye" (1878) -- landscape with distant forest, birds of prey
        - "Morning in a Pine Forest" (1889) -- with bears by Savitsky
        - "Ship Grove" (1898) -- final masterwork, cathedral-like pines
        - "Pine on the Rock" (1860) -- atmospheric cliff-edge single tree
        - "In the Wild North" (1891) -- snowbound pine in moonlight
        - "Pine Forest: Mastovaya Grove in Vyatka Province" (1872)

        Stage 1 VERTICAL BARK TEXTURE ANISOTROPY (Pine Trunk Grain):
        Apply elongated vertical uniform filter to the canvas:
          kernel_shape = (2*bark_vlong+1, 2*bark_vshort+1) -- tall, narrow
          M_vert_C = uniform_filter(C, size=kernel_shape)
        Blend toward vertical-filtered version: C1 = C + (M_vert - C) * bark_strength
        The vertical kernel (long in y, short in x) averages local neighborhoods
        more along the vertical axis, producing a vertical grain texture that
        aligns with tree trunk structure. Applied to all channels, it creates a
        subtle vertical streaking in the image that reinforces trunk directionality
        and bark grain without introducing color shifts.
        NOVEL: (a) PURELY VERTICAL ANISOTROPIC MEAN FOR BARK SIMULATION --
        prior directional-anisotropic passes use turbulent velocity fields
        (fechin: 4 orientations weighted by field; gorky: none) or isotropic
        filters. This pass uses a SINGLE ORIENTATION -- vertical -- with
        a kernel asymmetry (bark_vlong/bark_vshort ~ 11:1 ratio) far more
        extreme than any prior anisotropic pass. The vertical direction is
        motivated by the physical orientation of tree trunk bark grain; the
        extreme aspect ratio ensures genuine directional texture rather than
        a mild smoothing.

        Stage 2 CANOPY LIGHT DAPPLING (Local Variance Saturation Enhancement):
        Compute local luminance variance: L1 = luminance of C1
          L1_sq_blur = GaussianFilter(L1^2, sigma=dapple_sigma)
          L1_blur    = GaussianFilter(L1,   sigma=dapple_sigma)
          L_var      = max(L1_sq_blur - L1_blur^2, 0)  (local variance)
        High L_var pixels are in dappled transition zones (sunlit patches
        adjacent to shadow areas). In high-variance zones, push toward the
        sunlit-foliage color (dapple_r, dapple_g, dapple_b -- warm yellow-green):
          dapple_mask = clip(L_var / dapple_threshold, 0, 1) * dapple_strength
          C_dapple = C1 + (dapple_color - C1) * dapple_mask
        NOVEL: (b) LOCAL LUMINANCE VARIANCE AS DAPPLED-LIGHT PROXY --
        Local variance identifies zones where adjacent pixels have very different
        luminance values (the characteristic signature of light/shadow transition
        in dappled canopy). No prior pass uses per-pixel local variance as a gate
        for a color enhancement. Prior passes gate on absolute luminance (value
        threshold), gradient magnitude (edge strength), or spatial position.
        Local variance targets the VARIABILITY of luminance in a neighborhood,
        not the absolute value -- it fires maximally in the flickering
        light/shadow transition zones of a canopy, not in the flat light or flat
        dark areas. This is the physical signature of dappled forest light.

        Stage 3 FOREST FLOOR SHADOW WARMTH (Ochre Earth in Shadow Zones):
        Identify shadow pixels: L < floor_threshold with soft falloff:
          floor_mask = clip((floor_threshold - L) / floor_softness, 0, 1)
        Push shadow zone toward warm forest-floor earth: (floor_r/g/b)
          C3 = C2 + (floor_color - C2) * floor_mask * floor_strength
        The forest floor earth colors (0.52/0.34/0.14 -- raw umber/ochre) are
        present in Shishkin\'s shadow zones as warm luminous undertones where
        the sandy forest soil reflects warm indirect light into the base
        of shadow areas.
        NOVEL: (c) SHADOW-ZONE WARM EARTH PUSH --
        Prior shadow-zone color modifications push toward neutral dark
        (goya: umber/black deepening), or add cool (paint_depth_atmosphere:
        cool haze). This pass pushes shadow zones toward warm earth ochre,
        encoding the specific quality of forest floor warm indirect
        reflection -- the phenomenon where sandy soil and leaf litter
        reflect warm ambient light into the lower shadow zones. Shishkin
        used this systematically; it distinguishes his forest interiors
        from darker, cooler Northern European forest paintings.

        Stage 4 DISTANT DESATURATED FOREST HAZE (Saturation-Gated Cool Recession):
        Compute per-pixel saturation from RGB:
          C_max = max(R,G,B),  C_min = min(R,G,B)
          S = (C_max - C_min) / max(C_max, 1e-6)
        Smooth saturation: S_smooth = GaussianFilter(S, sigma=haze_sigma)
        Identify desaturated zones: S_smooth < haze_threshold
        Push toward cool blue-green forest haze (haze_r/g/b):
          haze_mask = clip(1 - S_smooth / haze_threshold, 0, 1)
          C4 = C3 + (haze_color - C3) * haze_mask * haze_strength
        NOVEL: (d) DESATURATION-GATED COOL FOREST HAZE --
        The existing depth_atmosphere_pass (s268) estimates depth from
        vertical position and local CONTRAST (standard deviation) and
        applies haze uniformly based on that depth estimate. This stage
        gates SOLELY on per-pixel SATURATION -- the chroma of the pixel --
        which is a fundamentally different signal: naturally desaturated areas
        (gray bark, neutral shadow, atmospheric background) receive the cool
        push, while saturated foreground foliage and sunlit bark do not. This
        is more physically motivated for forest scenes: the cool haze is
        specifically the blue-shifted distant atmosphere that desaturates
        distant trunks and undergrowth, regardless of whether they sit at
        the top of the canvas or not. A desaturated tree trunk anywhere in
        the image is likely at distance; a saturated green foreground is close.
        """
        print("    Shishkin Forest Density pass (192nd mode)...")

        import numpy as _np
        from scipy.ndimage import uniform_filter as _uf, gaussian_filter as _gf

        canvas = self.canvas
        H, W = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        L = (0.299 * R + 0.587 * G + 0.114 * B).astype(_np.float32)

        # Stage 1: Vertical bark texture anisotropy
        vl = max(int(bark_vlong),  1)
        vs = max(int(bark_vshort), 1)
        ksize_y = 2 * vl + 1
        ksize_x = 2 * vs + 1
        R_vert = _uf(R, size=(ksize_y, ksize_x)).astype(_np.float32)
        G_vert = _uf(G, size=(ksize_y, ksize_x)).astype(_np.float32)
        B_vert = _uf(B, size=(ksize_y, ksize_x)).astype(_np.float32)
        bs = float(bark_strength)
        R1 = _np.clip(R + (R_vert - R) * bs, 0.0, 1.0).astype(_np.float32)
        G1 = _np.clip(G + (G_vert - G) * bs, 0.0, 1.0).astype(_np.float32)
        B1 = _np.clip(B + (B_vert - B) * bs, 0.0, 1.0).astype(_np.float32)

        # Stage 2: Canopy light dappling (local variance saturation enhancement)
        L1 = (0.299 * R1 + 0.587 * G1 + 0.114 * B1).astype(_np.float32)
        dsig = max(float(dapple_sigma), 0.5)
        L1sq_blur = _gf(L1 * L1, sigma=dsig).astype(_np.float32)
        L1_blur   = _gf(L1,       sigma=dsig).astype(_np.float32)
        L_var = _np.maximum(L1sq_blur - L1_blur * L1_blur, 0.0).astype(_np.float32)
        dt = max(float(dapple_threshold), 1e-5)
        dapple_mask = _np.clip(L_var / dt, 0.0, 1.0).astype(_np.float32)
        dstr = float(dapple_strength)
        dr, dg, db = float(dapple_r), float(dapple_g), float(dapple_b)
        R2 = _np.clip(R1 + (dr - R1) * dapple_mask * dstr, 0.0, 1.0).astype(_np.float32)
        G2 = _np.clip(G1 + (dg - G1) * dapple_mask * dstr, 0.0, 1.0).astype(_np.float32)
        B2 = _np.clip(B1 + (db - B1) * dapple_mask * dstr, 0.0, 1.0).astype(_np.float32)

        # Stage 3: Forest floor shadow warmth (ochre earth in shadow zones)
        L2 = (0.299 * R2 + 0.587 * G2 + 0.114 * B2).astype(_np.float32)
        ft = float(floor_threshold)
        fsft = max(float(floor_softness), 0.01)
        floor_mask = _np.clip((ft - L2) / fsft, 0.0, 1.0).astype(_np.float32)
        fstr = float(floor_strength)
        fr, fg, fb_ = float(floor_r), float(floor_g), float(floor_b)
        R3 = _np.clip(R2 + (fr - R2) * floor_mask * fstr, 0.0, 1.0).astype(_np.float32)
        G3 = _np.clip(G2 + (fg - G2) * floor_mask * fstr, 0.0, 1.0).astype(_np.float32)
        B3 = _np.clip(B2 + (fb_ - B2) * floor_mask * fstr, 0.0, 1.0).astype(_np.float32)

        # Stage 4: Distant desaturated forest haze (saturation-gated cool recession)
        C_max = _np.maximum(_np.maximum(R3, G3), B3).astype(_np.float32)
        C_min = _np.minimum(_np.minimum(R3, G3), B3).astype(_np.float32)
        S = _np.where(C_max > 1e-6, (C_max - C_min) / (C_max + 1e-6),
                      _np.zeros_like(C_max)).astype(_np.float32)
        hsig = max(float(haze_sigma), 0.5)
        S_smooth = _gf(S, sigma=hsig).astype(_np.float32)
        ht = max(float(haze_threshold), 1e-4)
        haze_mask = _np.clip(1.0 - S_smooth / ht, 0.0, 1.0).astype(_np.float32)
        hstr = float(haze_strength)
        hr_, hg_, hb_ = float(haze_r), float(haze_g), float(haze_b)
        R4 = _np.clip(R3 + (hr_ - R3) * haze_mask * hstr, 0.0, 1.0).astype(_np.float32)
        G4 = _np.clip(G3 + (hg_ - G3) * haze_mask * hstr, 0.0, 1.0).astype(_np.float32)
        B4 = _np.clip(B3 + (hb_ - B3) * haze_mask * hstr, 0.0, 1.0).astype(_np.float32)

        # Composite at opacity
        op = float(opacity)
        R_out = _np.clip(R + (R4 - R) * op, 0.0, 1.0).astype(_np.float32)
        G_out = _np.clip(G + (G4 - G) * op, 0.0, 1.0).astype(_np.float32)
        B_out = _np.clip(B + (B4 - B) * op, 0.0, 1.0).astype(_np.float32)

        dapple_px = int((dapple_mask > 0.1).sum())
        haze_px   = int((haze_mask   > 0.1).sum())

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

        print(f"    Shishkin Forest Density complete "
              f"(dapple_px={dapple_px}, haze_px={haze_px})")

'''

# ── Append both passes to stroke_engine.py (after last method) ───────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

# Verify neither pass already exists
assert "paint_shadow_temperature_pass" not in src, \
    "paint_shadow_temperature_pass already exists in stroke_engine.py"
assert "shishkin_forest_density_pass" not in src, \
    "shishkin_forest_density_pass already exists in stroke_engine.py"

# Append to end of file
with open(SE_PATH, "a", encoding="utf-8") as f:
    f.write(SHADOW_TEMPERATURE_PASS)
    f.write(SHISHKIN_FOREST_PASS)

print("stroke_engine.py patched: paint_shadow_temperature_pass (s281 improvement)"
      " + shishkin_forest_density_pass (192nd mode) appended.")
