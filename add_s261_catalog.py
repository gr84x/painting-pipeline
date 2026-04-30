"""Insert alfred_sisley entry into art_catalog.py (session 261).

Run once to modify art_catalog.py; preserved as a change record afterward.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))

SISLEY_ENTRY = """    "alfred_sisley": ArtStyle(
        artist="Alfred Sisley",
        movement="French Impressionism",
        nationality="British-French",
        period="1839–1899",
        palette=[
            (0.82, 0.84, 0.88),   # silver-cool sky -- overcast pale vault
            (0.74, 0.76, 0.80),   # pewter mid-sky -- cloud base cool grey
            (0.68, 0.72, 0.64),   # sage-grey foliage -- muted English trees
            (0.55, 0.60, 0.58),   # grey-green waterway -- canal or river grey
            (0.90, 0.88, 0.84),   # pale horizon light -- warm thin line at skyline
            (0.42, 0.44, 0.40),   # shadow foliage -- tree interior deep cool green
            (0.72, 0.68, 0.60),   # warm earth path -- unpaved road or bank
            (0.48, 0.52, 0.60),   # cool shadow water -- reflected grey-blue
            (0.62, 0.64, 0.70),   # atmospheric mid-grey -- silver haze mid-distance
            (0.35, 0.36, 0.34),   # dark oak structure -- lock gate, wooden bridge
        ],
        ground_color=(0.80, 0.82, 0.80),    # silver-grey overcast imprimatura
        stroke_size=7,
        wet_blend=0.22,
        edge_softness=0.38,
        jitter=0.018,
        glazing=(0.82, 0.82, 0.85),    # cool silver unifying veil
        crackle=False,
        chromatic_split=False,
        technique=(
            "Alfred Sisley (1839-1899), British by birth, lived and worked almost "
            "entirely in France, painting the same reach of the Seine and Loing "
            "rivers throughout his life.  He is the most consistently atmospheric "
            "of the Impressionists and the one whose work is most specifically "
            "about weather as an emotional state. "
            "Three defining characteristics of his mature technique: "
            "(1) THE SILVER SKY -- Sisley devoted more canvas to sky than any "
            "other Impressionist.  His skies are not Monet's vivid cerulean or "
            "Turner's violent gold but a characteristic English-northern SILVER: "
            "a cool grey-white with a faint warm horizon band, achieved by "
            "layering thin washes of grey-white with occasional pale blue and "
            "cream in horizontal strokes.  The silver sky becomes the tonal key "
            "of the whole picture -- everything is read against it.  Trees look "
            "dark against the silver, water reflects it.  The palette of the land "
            "is chosen to harmonize with the sky rather than to express itself; "
            "(2) THE ATMOSPHERIC SILVER HAZE -- at middle distances (50-200m), "
            "Sisley applied a thin neutral-grey veil that softens and desaturates "
            "the midground: colours there drift toward silver, edges soften, "
            "saturation declines.  This is not the warm golden haze of Claude Lorrain "
            "nor the blue-cool recession of a mountain painter -- it is a specific "
            "English NEUTRAL SILVER MIST, neither warm nor cool, that gives his "
            "midgrounds their quality of gentle recession without theatrics; "
            "(3) THE HORIZONTAL STROKE -- Sisley applied paint in predominantly "
            "horizontal strokes, especially in skies and water.  These strokes "
            "lie parallel to the horizon line and create a subtle sense of "
            "horizontal motion in both the clouds and the water surface.  In "
            "his skies this horizontal directionality gives the impression of "
            "wind-driven cloud movement; in water it reinforces the still, "
            "mirror quality of calm flood-water.  His land strokes are more "
            "varied but the sky and water are consistently horizontal, creating "
            "a strong compositional axis that holds the landscape to the earth."
        ),
        famous_works=[
            ("Flood at Port-Marly",                "1876"),
            ("The Bridge at Villeneuve-la-Garenne", "1872"),
            ("Snow at Louveciennes",                "1878"),
            ("The Loing Canal",                     "1892"),
            ("Hampton Court Bridge",                "1874"),
            ("Under the Bridge at Hampton Court",   "1874"),
            ("Barges on the Loing",                 "1885"),
            ("The Moret Bridge in Sunlight",        "1890"),
            ("Boats at Argenteuil",                 "1872"),
            ("Avenue of Chestnut Trees near La Celle-Saint-Cloud", "1867"),
        ],
        inspiration=(
            "sisley_silver_veil_pass -- ONE HUNDRED AND SEVENTY-SECOND distinct "
            "painting mode (session 261).  Three-stage silvery Impressionist "
            "landscape model: "
            "(1) SILVER SKY BAND: cool silver-grey tint applied to a configurable "
            "upper height fraction, blending toward target silver with a linear "
            "vertical weight; "
            "(2) MIDGROUND SILVER HAZE: Gaussian bell-curve (centered lum=0.56) "
            "blend toward a neutral cool-silver, creating Sisley's silver mist "
            "in the mid-luminance atmospheric zone; "
            "(3) HORIZONTAL SKY MOTION BLUR: directional (horizontal-axis only, "
            "sigma_y=0) Gaussian blur restricted to the sky fraction, creating "
            "the horizontal wind-driven movement quality of his cloud painting. "
            "NOVEL: (a) vertical-zone-bounded additive silver tint in upper "
            "height fraction (first pass to bound tint to configurable top band); "
            "(b) Gaussian bell centered on lum=0.56 blending toward cool neutral "
            "silver (distinct from chirico warm bell and all prior midtone passes); "
            "(c) unidirectional horizontal Gaussian blur (sigma_y=0) in a "
            "configurable upper vertical zone (first pass to apply 1D directional "
            "blur restricted to a height band)."
        ),
    ),
"""

CATALOG_FILE = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_FILE, "r", encoding="utf-8") as f:
    src = f.read()

if '"alfred_sisley"' in src:
    print("alfred_sisley already present -- skipping.")
    sys.exit(0)

# Insert before alma_tadema (alphabetical: 'alfred' before 'alma')
ANCHOR = '    "alma_tadema":'
if ANCHOR not in src:
    ANCHOR = '    "anders_zorn":'
if ANCHOR not in src:
    print(f"ERROR: anchor not found")
    sys.exit(1)

src = src.replace(ANCHOR, SISLEY_ENTRY + ANCHOR, 1)

with open(CATALOG_FILE, "w", encoding="utf-8") as f:
    f.write(src)

print("alfred_sisley inserted into art_catalog.py successfully.")
