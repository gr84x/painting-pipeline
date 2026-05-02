"""Insert Eugene Carriere entry into art_catalog.py (session 286).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

CARRIERE_ENTRY = '''
    # ── Eugène Carrière ──────────────────────────────────────────────────────────
    "eugene_carriere": ArtStyle(
        artist="Eugène Carrière",
        movement="Symbolism / Post-Impressionism",
        nationality="French",
        period="1849-1906",
        palette=[
            (0.52, 0.38, 0.22),   # warm bistre-brown -- Carriere primary tone
            (0.18, 0.12, 0.07),   # deep warm umber -- shadow depth
            (0.72, 0.58, 0.38),   # amber-ochre -- midtone warmth
            (0.62, 0.48, 0.30),   # sienna-brown -- mid-warm tone
            (0.84, 0.72, 0.52),   # pale bistre -- near-highlight warm
            (0.36, 0.26, 0.16),   # mid-dark umber -- modelling shadow
            (0.90, 0.82, 0.64),   # warm off-white -- highlight peak
            (0.44, 0.32, 0.18),   # dark bistre -- background tone
            (0.28, 0.20, 0.12),   # deep brown -- merged shadow zone
            (0.68, 0.52, 0.34),   # amber-brown -- form modelling mid
        ],
        ground_color=(0.22, 0.16, 0.10),  # dark warm umber ground
        stroke_size=14,
        wet_blend=0.52,
        edge_softness=0.42,
        jitter=0.018,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Symbolism / French Post-Impressionism. Eugene Carriere (1849-1906) "
            "was the preeminent French Symbolist painter of intimate domestic subjects. "
            "He trained under Alexandre Cabanel at the Ecole des Beaux-Arts but "
            "developed a radically personal technique: a warm monochromatic palette "
            "of bistre, umber, and sienna from which figures emerge as if materializing "
            "from warm darkness. His studio school (l\'Academie Carriere in Montmartre) "
            "trained Matisse, Puy, and Derain -- the founders of Fauvism. "
            "Rodin described Carriere\'s technique: \'He paints shadows that are born.\' "
            "CARRIERE\'S FIVE TECHNICAL SIGNATURES: "
            "(1) WARM MONOCHROME DOMINANCE: entire canvas unified in bistre-brown, "
            "all local colour subordinated to a pervading warm temperature. "
            "(2) FORM EMERGENCE FROM WARM DARKNESS: figures grow from dark warm ground "
            "via scumbled lighter passages; background and figure share same base tone. "
            "(3) SOFT EDGE DISSOLUTION: every edge is soft; luminance contrast readable "
            "but spatial sharpness dissolved; forms appear to occupy air not surfaces. "
            "(4) DEEP SHADOW UNIFICATION: all dark zones merge toward a single common "
            "deep warm umber; shadows share a unified tone regardless of source. "
            "(5) PERIPHERAL EDGE FADE: consistent darkening of all canvas edges, "
            "drawing the eye inward to the warm luminance at the centre. "
            "THE GREAT WORKS: \'Maternity\' (1892) -- mother and infant in warm shadow; "
            "\'Portrait of Paul Verlaine\' (1891) -- poet materializing from darkness; "
            "\'The Sick Child\' (1885) -- tender domestic scene in warm monochrome; "
            "\'Portrait of Anatole France\' (1895) -- novelist in deep bistre atmosphere."
        ),
        famous_works=[
            ("Maternity",                             "1892"),
            ("Portrait of Paul Verlaine",             "1891"),
            ("The Sick Child",                        "1885"),
            ("Portrait of Anatole France",            "1895"),
            ("Intimate Family",                       "1895"),
            ("The Kiss",                              "1893"),
            ("Mother and Child",                      "1900"),
            ("Portrait of Marguerite Carriere",       "1901"),
            ("Reading",                               "1894"),
            ("The Theatre Box",                       "1894"),
        ],
        inspiration=(
            "carriere_smoky_reverie_pass(): FOUR-STAGE WARM MONOCHROME SYSTEM "
            "-- 197th distinct mode. "
            "(1) WARM SEPIA TINT: L = luminance; R_s = L * sepia_r (default 0.58), "
            "G_s = L * sepia_g (0.44), B_s = L * sepia_b (0.28); "
            "R1 = R + (R_s - R) * sepia_strength (0.68); "
            "FIRST PASS to apply luminance-scaled warm tint uniformly across all zones "
            "without luminance gating -- prior warm pushes are zone-gated (repin midtone "
            "bell, grosz colour-dominance mask, s284 HSV hue rotation). "
            "(2) EXPONENTIAL SHADOW MERGE: gate = exp(-L / tau) (default tau=0.28); "
            "R2 = R1 + gate * strength * (dark_r - R1); dark = (0.12, 0.08, 0.05); "
            "FIRST use of negative exponential exp(-L/tau) as luminance zone gate -- "
            "prior shadow gates use hard threshold (repin), power law (grosz gamma), "
            "or linear ramp within fixed range (s281 shadow_temperature). "
            "(3) GRADIENT-MAGNITUDE SOFT EDGE DISSOLUTION: G_norm = normalized gradient; "
            "weight = clip(sqrt(G_norm)*dissolve_strength, 0, 1); "
            "R3 = R2*(1-weight) + Gaussian(R2, sigma)*weight; "
            "FIRST pass to use G_norm as blur weight (MORE blur at HIGH gradient zones); "
            "ALL prior edge passes sharpen at high G_norm (repin, lost/found edges) or "
            "smooth interior zones at low G_norm (grosz interior flatten, savrasov mist). "
            "(4) PERIPHERAL EDGE FADE: d_edge = min(x, W-1-x, y, H-1-y) / (min(W,H)*0.5); "
            "border_gate = clip(1 - d_edge * falloff, 0, 1); scale = 1 - gate * strength; "
            "FIRST use of minimum-distance-to-canvas-boundary as zone gate (Chebyshev / "
            "L-inf norm); focal_vignette_pass (s278) uses L2 radial from detected center -- "
            "geometrically distinct; peripheral fade is canvas-absolute, not content-adaptive."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

assert "eugene_carriere" not in src, "eugene_carriere already exists in art_catalog.py"

ANCHOR = "\n\n}\n\n\ndef get_style"
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, CARRIERE_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: eugene_carriere entry inserted.")
