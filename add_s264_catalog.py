"""Insert Pierre Soulages entry into art_catalog.py (session 264).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

SOULAGES_ENTRY = '''
    # ── Pierre Soulages ──────────────────────────────────────────────────────────
    "soulages": ArtStyle(
        artist="Pierre Soulages",
        movement="Outrenoir / Abstract",
        nationality="French",
        period="1948–2022",
        palette=[
            (0.03, 0.03, 0.04),   # outrenoir black — total absorption
            (0.08, 0.08, 0.10),   # reflective near-black — squeegee-seam
            (0.15, 0.14, 0.17),   # dark schist — stone interior
            (0.28, 0.26, 0.30),   # deep grey — shadow mid-zone
            (0.48, 0.45, 0.42),   # warm fracture-lit — raking-light seam
            (0.62, 0.60, 0.56),   # pale stone — caught limestone
            (0.18, 0.14, 0.28),   # sky violet — Aveyron dusk
            (0.06, 0.06, 0.08),   # water mirror — quarry pool
        ],
        ground_color=(0.04, 0.04, 0.05),    # outrenoir black ground — total dark
        stroke_size=16,
        wet_blend=0.10,                      # low — matte black acrylic, minimal blending
        edge_softness=0.10,                  # low — hard tool-drag boundaries
        jitter=0.020,                        # very low — tonal, not chromatic variation
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Outrenoir: painting exclusively with black acrylic, building "
            "luminance through surface texture rather than colour. Large "
            "squeegees, palette knives, and custom tools dragged across the "
            "wet black surface create horizontal and diagonal fields of "
            "varying reflectivity -- matte zones beside metallic seams beside "
            "flat absorption fields. Light comes FROM the painting: the tool "
            "marks are the image. No colour after 1979; everything expressed "
            "through the geometry of surface and the physics of reflection. "
            "Soulages described black as \'a colour that concentrates light, "
            "transforms it, and reflects it back in a different form\'. The "
            "resulting canvases read as dark from most angles but transform "
            "into complex luminance landscapes as the viewer moves or the "
            "ambient light shifts. His largest works (3-6 metres) fill the "
            "peripheral vision and become immersive environments of near-black "
            "that the eye reads as variously deep, reflective, warm, or cool "
            "depending on viewing angle and distance."
        ),
        famous_works=[
            ("Peinture 324 x 362 cm, 16 mars 2009", "2009"),
            ("Peinture 222 x 314 cm, 23 mai 1999",  "1999"),
            ("Peinture 130 x 89 cm, 28 juin 1983",  "1983"),
            ("Peinture 65 x 50 cm, 1953",            "1953"),
            ("Brou de noix sur papier",               "1948"),
            ("Peinture 280 x 628 cm",                "1986"),
            ("Peinture 162 x 130 cm, 26 mars 1963",  "1963"),
            ("Triptyque, 2012",                       "2012"),
        ],
        inspiration=(
            "soulages_outrenoir_pass(): THREE-STAGE OUTRENOIR BLACK-TEXTURE "
            "TECHNIQUE -- 175th distinct mode. "
            "(1) ULTRA-BLACK DEEPENING: power-law compression below black_threshold "
            "pushes sub-threshold pixels toward near-zero luminance, simulating "
            "the absorption depth of Soulages\' matte industrial-grade black acrylic; "
            "(2) HORIZONTAL REFLECTIVE STRIPE FIELD: sinusoidal luminance bands "
            "confined to dark-region mask simulate horizontal squeegee-drag marks "
            "catching ambient light at different angles within the black surface; "
            "(3) DARK-SIDE EDGE BLOOM: Sobel edge magnitude weighted by dark-side "
            "proximity (1 - lum), Gaussian-blurred, lifts light pixels at "
            "dark/light boundaries to create the Soulages effect where extreme "
            "darkness makes adjacent light appear brighter than it is."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"soulages"' in src:
    print("Soulages already in catalog -- nothing to do.")
    sys.exit(0)

# Insert just before the closing brace of CATALOG
INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + SOULAGES_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Pierre Soulages into art_catalog.py.")
