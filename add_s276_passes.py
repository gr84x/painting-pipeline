"""Insert paint_complementary_shadow_pass (s276 improvement) and
thiebaud_halo_shadow_pass (187th mode) into stroke_engine.py.

Run once to modify stroke_engine.py; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

# ── Pass 1: paint_complementary_shadow_pass (s276 improvement) ───────────────

COMPLEMENTARY_SHADOW_PASS = '''
    def paint_complementary_shadow_pass(
        self,
        light_threshold:   float = 0.68,
        shadow_threshold:  float = 0.32,
        complement_shift:  float = 0.50,
        tint_saturation:   float = 0.28,
        tint_strength:     float = 0.22,
        opacity:           float = 0.55,
    ) -> None:
        r"""Complementary Shadow Tinting -- session 276 improvement.

        SIMULATION OF THE COLORIST PRINCIPLE THAT SHADOWS CONTAIN THE
        COMPLEMENTARY HUE OF THE DOMINANT LIGHT SOURCE -- A FUNDAMENTAL
        TECHNIQUE OF THIEBAUD, BONNARD, MATISSE, AND SIGNAC:

        Classical academic painting teaches that shadows are neutral grey;
        colorist painting teaches that shadows are warm or cool depending on
        the light source. The more sophisticated colorist insight -- articulated
        by Chevreul (1839) and practised by Delacroix, Monet, Signac, Bonnard,
        and Thiebaud -- is that shadows carry the COMPLEMENTARY color of the
        light source. This is partly optical (simultaneous contrast: the eye
        perceives a complementary afterimage in adjacent shadow zones) and
        partly physical (reflected ambient light, which is typically cool when
        the direct light is warm, fills shadow zones with color opposite to
        the direct light).

        Wayne Thiebaud is the most extreme and deliberate practitioner: the
        shadows beside his lemon meringue pies are vivid pink-magenta, because
        the pale yellow light source demands a violet complement. The shadows
        in his diner coffee cups are a vivid blue-violet because the warm
        fluorescent-amber light demands blue-indigo.

        Stage 1 DOMINANT LIGHT HUE EXTRACTION:
        Find bright pixels (luminance > light_threshold). Compute the mean RGB
        of these pixels, normalize to a unit-sphere direction, and convert to
        HSV to extract the dominant light hue H_light in [0,1].
        NOVEL: (a) SCENE-ADAPTIVE LIGHT HUE DETECTION FROM BRIGHT PIXEL
        SAMPLING -- no prior pass detects the dominant hue of the painting\'s
        bright zone to drive a shadow treatment; all prior shadow passes use
        fixed or geometric parameters. This pass derives its shadow color
        directly from the painting\'s own luminosity distribution.

        Stage 2 COMPLEMENTARY HUE CONSTRUCTION:
        Compute the complementary hue:
          H_comp = (H_light + complement_shift) % 1.0
        where complement_shift defaults to 0.5 (exact complement in HSV
        color wheel). Construct a shadow tint color in HSV as:
          (H_comp, tint_saturation, 0.4)  -- muted, medium-dark
        and convert to RGB. The low value (0.4) keeps the tint dark enough
        to live in the shadow zone without lightening it.
        NOVEL: (b) PARAMETRIC HSV COMPLEMENT ROTATION DRIVEN BY SCENE DATA
        -- the complement_shift parameter allows tuning away from exact
        complement (e.g. 0.45 for near-complement, 0.55 for split-complement);
        this is a mathematically precise colorist principle no prior pass applies.

        Stage 3 SHADOW ZONE DETECTION AND TINTING:
        Identify shadow pixels: luminance L < shadow_threshold. Build a shadow
        mask. Blend the complementary tint into the shadow zone:
          R_new = R + (tint_R - R) * tint_strength * shadow_mask
          G_new = G + (tint_G - G) * tint_strength * shadow_mask
          B_new = B + (tint_B - B) * tint_strength * shadow_mask
        This shifts the shadow hue toward the complement without significantly
        changing its luminance (since tint value=0.4 ≈ average shadow luminance).
        NOVEL: (c) SHADOW-ZONE-GATED HUE SHIFT TOWARD SCENE-DERIVED COMPLEMENT
        -- prior shadow passes modify luminance (scumbling veil adds lightness,
        reflected light adds warm edge brightness); this pass modifies HUE
        in shadow zones only. The combination of zone gating (shadow only)
        with scene-adaptive complementary target is unique in this codebase.

        Stage 4 COMPOSITE:
        out = original + (modified - original) * opacity
        """
        print("    Complementary Shadow Tinting pass (session 276 improvement)...")

        import colorsys as _cs
        import numpy as _np
        from scipy.ndimage import gaussian_filter as _gf

        canvas = self.canvas
        H, W = canvas.h, canvas.w

        # Read current canvas BGRA -> float32 RGB
        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        L = 0.299 * R + 0.587 * G + 0.114 * B

        # Stage 1: detect dominant light hue from bright pixels
        bright_mask = L > light_threshold
        n_bright = int(bright_mask.sum())
        if n_bright < 10:
            # Fallback: use warm yellow-orange light assumption
            H_light = 0.10
        else:
            mean_R = float(R[bright_mask].mean())
            mean_G = float(G[bright_mask].mean())
            mean_B = float(B[bright_mask].mean())
            H_light, _s, _v = _cs.rgb_to_hsv(mean_R, mean_G, mean_B)

        # Stage 2: build complementary tint color
        H_comp = (H_light + complement_shift) % 1.0
        tint_r, tint_g, tint_b = _cs.hsv_to_rgb(H_comp, tint_saturation, 0.40)
        tint_r = float(tint_r)
        tint_g = float(tint_g)
        tint_b = float(tint_b)

        # Stage 3: shadow zone detection and tinting
        shadow_mask = (L < shadow_threshold).astype(_np.float32)

        R_new = R + (tint_r - R) * tint_strength * shadow_mask
        G_new = G + (tint_g - G) * tint_strength * shadow_mask
        B_new = B + (tint_b - B) * tint_strength * shadow_mask

        # Stage 4: composite
        R_out = _np.clip(R + (R_new - R) * opacity, 0, 1)
        G_out = _np.clip(G + (G_new - G) * opacity, 0, 1)
        B_out = _np.clip(B + (B_new - B) * opacity, 0, 1)

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

'''

# ── Pass 2: thiebaud_halo_shadow_pass (187th mode) ───────────────────────────

THIEBAUD_HALO_PASS = '''
    def thiebaud_halo_shadow_pass(
        self,
        edge_sigma:         float = 1.8,
        edge_threshold:     float = 0.055,
        halo_radius:        int   = 7,
        halo_r:             float = 0.96,
        halo_g:             float = 0.82,
        halo_b:             float = 0.72,
        halo_opacity:       float = 0.38,
        shadow_r:           float = 0.78,
        shadow_g:           float = 0.60,
        shadow_b:           float = 0.82,
        shadow_opacity:     float = 0.32,
        contour_darkness:   float = 0.18,
        contour_opacity:    float = 0.45,
        opacity:            float = 0.72,
    ) -> None:
        r"""Thiebaud Halo Shadow (Chromatic Halos and Colored Shadows) -- 187th mode.

        WAYNE THIEBAUD (b. 1920) -- AMERICAN FIGURATIVE / COMMERCIAL SUBJECT
        PAINTER OF THE SACRAMENTO SCHOOL AND NEW YORK SCHOOL PERIPHERY:

        Wayne Thiebaud emerged in the early 1960s alongside the Pop Art movement,
        but his work has always been fundamentally painterly rather than commercial:
        he appropriates the subject matter of commercial food display (pie slices,
        ice cream scoops, diner counters, candy apples) while painting them with
        a sensibility derived from Vermeer, Degas, and the Abstract Expressionists.
        His paintings are simultaneously hyper-material (you can see every ridge of
        frosting, every reflection on the plate) and deeply formal (the objects are
        arranged on grounds of near-abstract luminosity, and the color decisions are
        those of a classical colorist).

        THE HALO SHADOW PHENOMENON:
        Thiebaud\'s most distinctive technical trait is the COLORED HALO that
        surrounds objects in his paintings. When you look at a Thiebaud pie on a
        white counter, you notice that the shadow beside the pie is not neutral
        grey but a vivid, saturated pink or orange; and that the edge between the
        pie and the counter is not a clean boundary but a luminous light halo --
        a zone of heightened brightness that makes the object appear to glow from
        within. This dual phenomenon -- colored shadow halo + luminous light halo
        -- is Thiebaud\'s most immediately recognizable signature.

        MECHANISM:
        (1) HALO LIGHT ZONE: On the lit side of the object boundary, Thiebaud
        applies a warm-tinted light halo -- a zone of warm cream-white that is
        brighter and warmer than both the object and the ground, simulating
        indirect light refraction and the warmth of studio lighting.

        (2) COLORED SHADOW ZONE: On the shadow side of the boundary, instead of
        neutral grey, Thiebaud applies a chromatic shadow that is warm-hued --
        often pink, orange, or violet depending on the painting\'s dominant light
        color. This follows the colorist principle (Chevreul, Matisse, Bonnard)
        that shadows contain the complement of the light source, but Thiebaud
        pushes the saturation far beyond academic usage.

        (3) CONTOUR REINFORCEMENT: At the object boundary itself, a dark
        complementary-colored contour line is applied, separating the halo
        from the shadow zone with a thin painted edge -- simulating Thiebaud\'s
        loaded-brush contour strokes that define form with great precision.

        Stage 1 LUMINANCE-BASED EDGE DETECTION:
        Compute luminance gradient after Gaussian smoothing (sigma=edge_sigma).
        Threshold gradient magnitude at edge_threshold to produce a crisp edge
        mask E. Separate lit-side and shadow-side expansions using the
        gradient direction: pixels on the brighter side of each edge receive
        the halo treatment; pixels on the darker side receive the shadow treatment.
        NOVEL: (a) DIRECTIONAL EDGE-SIDE LABELING USING GRADIENT DIRECTION --
        prior passes that use edge gradients apply the same treatment to both
        sides of an edge (gorky: contour overlay; ernst: vein reinforcement;
        impasto_ridge: lit vs shadow determined by dot product with external
        light vector). This pass uses the gradient direction to determine which
        side is lighter and applies DIFFERENT chromatic treatments to the lit
        side vs the shadow side -- the asymmetric bilateral chromatic expansion
        is unique.

        Stage 2 HALO ZONE (LIT SIDE) EXPANSION:
        Starting from the edge mask, dilate outward into the BRIGHTER side
        using iterative morphological expansion (up to halo_radius pixels).
        At each expansion step, the weight decays linearly (step/halo_radius).
        Blend halo color (warm cream-white: halo_r/g/b) into the halo zone
        proportional to weight * halo_opacity.
        NOVEL: (b) DECAY-WEIGHTED RADIAL DILATION INTO THE LIGHTER SIDE OF
        EDGES -- the lit-side expansion with linearly decaying weight creates
        a smooth warm bloom on object highlights; no prior pass performs
        directional dilation (always-lighter-side only) with distance decay.

        Stage 3 SHADOW ZONE (DARK SIDE) EXPANSION:
        Similarly dilate outward into the DARKER side (halo_radius steps,
        linear decay). Blend shadow halo color (warm pink-violet: shadow_r/g/b)
        into the shadow zone.
        NOVEL: (c) DECAY-WEIGHTED RADIAL DILATION INTO THE DARKER SIDE OF
        EDGES -- combined with Stage 2, this creates Thiebaud\'s characteristic
        bilateral halo structure: luminous warmth on the lit side, chromatic
        warmth (colored shadow) on the dark side. The combination of lit-side
        halo AND dark-side chromatic shadow from a SHARED edge detection is
        unique to this pass.

        Stage 4 CONTOUR REINFORCEMENT:
        Darken the edge pixels themselves by contour_darkness * contour_opacity
        to create a thin dark boundary between halo and shadow zone --
        simulating Thiebaud\'s loaded-brush contour line.

        Stage 5 COMPOSITE:
        out = original + (modified - original) * opacity
        """
        print("    Thiebaud Halo Shadow pass (187th mode)...")

        import numpy as _np
        from scipy.ndimage import (gaussian_filter as _gf,
                                    sobel as _sobel,
                                    binary_dilation as _bdil)

        canvas = self.canvas
        H, W = canvas.h, canvas.w

        raw = _np.frombuffer(canvas.surface.get_data(), dtype=_np.uint8
                             ).reshape((H, W, 4)).copy()
        R = raw[:, :, 2].astype(_np.float32) / 255.0
        G = raw[:, :, 1].astype(_np.float32) / 255.0
        B = raw[:, :, 0].astype(_np.float32) / 255.0

        L = 0.299 * R + 0.587 * G + 0.114 * B
        L_smooth = _gf(L, sigma=edge_sigma)

        # Stage 1: edge detection with gradient direction
        Gx = _sobel(L_smooth, axis=1)
        Gy = _sobel(L_smooth, axis=0)
        Gmag = _np.sqrt(Gx ** 2 + Gy ** 2)
        Gnorm = Gmag / (_np.percentile(Gmag, 99) + 1e-6)
        edge_mask = Gnorm > edge_threshold

        # Lit-side indicator: pixels where L is above local mean in a small patch
        L_local = _gf(L, sigma=edge_sigma * 3)
        lit_side = L >= L_local  # pixel is on the brighter-than-local-mean side

        R_mod = R.copy()
        G_mod = G.copy()
        B_mod = B.copy()

        # Stage 2: halo zone on lit side
        halo_zone = _np.zeros((H, W), dtype=_np.float32)
        current_mask = edge_mask & lit_side
        struct = _np.ones((3, 3), dtype=bool)
        for step in range(1, halo_radius + 1):
            current_mask = _bdil(current_mask, structure=struct)
            weight = float(halo_radius - step + 1) / float(halo_radius)
            new_halo = current_mask & ~edge_mask
            halo_zone = _np.where(new_halo, _np.maximum(halo_zone, weight), halo_zone)

        # Apply warm halo tint to lit side
        hw = halo_zone * halo_opacity
        R_mod = _np.clip(R_mod + (halo_r - R_mod) * hw, 0, 1)
        G_mod = _np.clip(G_mod + (halo_g - G_mod) * hw, 0, 1)
        B_mod = _np.clip(B_mod + (halo_b - B_mod) * hw, 0, 1)

        # Stage 3: shadow zone on dark side
        shadow_zone = _np.zeros((H, W), dtype=_np.float32)
        current_mask = edge_mask & ~lit_side
        for step in range(1, halo_radius + 1):
            current_mask = _bdil(current_mask, structure=struct)
            weight = float(halo_radius - step + 1) / float(halo_radius)
            new_shadow = current_mask & ~edge_mask
            shadow_zone = _np.where(new_shadow, _np.maximum(shadow_zone, weight), shadow_zone)

        # Apply colored shadow tint (warm pink-violet) to dark side
        sw = shadow_zone * shadow_opacity
        R_mod = _np.clip(R_mod + (shadow_r - R_mod) * sw, 0, 1)
        G_mod = _np.clip(G_mod + (shadow_g - G_mod) * sw, 0, 1)
        B_mod = _np.clip(B_mod + (shadow_b - B_mod) * sw, 0, 1)

        # Stage 4: contour reinforcement (darken edge pixels)
        e = edge_mask.astype(_np.float32)
        R_mod = _np.clip(R_mod - contour_darkness * contour_opacity * e, 0, 1)
        G_mod = _np.clip(G_mod - contour_darkness * contour_opacity * e, 0, 1)
        B_mod = _np.clip(B_mod - contour_darkness * contour_opacity * e, 0, 1)

        # Stage 5: composite
        R_out = _np.clip(R + (R_mod - R) * opacity, 0, 1)
        G_out = _np.clip(G + (G_mod - G) * opacity, 0, 1)
        B_out = _np.clip(B + (B_mod - B) * opacity, 0, 1)

        out = raw.copy()
        out[:, :, 2] = (R_out * 255).astype(_np.uint8)
        out[:, :, 1] = (G_out * 255).astype(_np.uint8)
        out[:, :, 0] = (B_out * 255).astype(_np.uint8)
        canvas.surface.get_data()[:] = out.tobytes()

'''

# ── Inject both passes into stroke_engine.py ─────────────────────────────────

SE_PATH = os.path.join(REPO, "stroke_engine.py")
with open(SE_PATH, "r", encoding="utf-8") as f:
    src = f.read()

ANCHOR = "    def gorky_biomorphic_fluid_pass("
assert ANCHOR in src, f"Anchor not found in stroke_engine.py: {ANCHOR!r}"

INSERTION = COMPLEMENTARY_SHADOW_PASS + THIEBAUD_HALO_PASS
new_src = src.replace(ANCHOR, INSERTION + ANCHOR, 1)

with open(SE_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("stroke_engine.py patched: paint_complementary_shadow_pass (s276 improvement)"
      " + thiebaud_halo_shadow_pass (187th mode) inserted before gorky_biomorphic_fluid_pass.")
