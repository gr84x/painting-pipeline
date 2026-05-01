"""Insert Pablo Picasso entry into art_catalog.py (session 275).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

PICASSO_ENTRY = '''
    # ── Pablo Picasso ──────────────────────────────────────────────────────────
    "picasso": ArtStyle(
        artist="Pablo Picasso",
        movement="Cubism (Analytic Cubism)",
        nationality="Spanish-French",
        period="1881-1973",
        palette=[
            (0.72, 0.60, 0.30),   # ochre -- defining Analytic Cubism warm tan
            (0.58, 0.56, 0.52),   # warm grey -- mid-register neutral plane
            (0.35, 0.27, 0.15),   # raw umber -- deep shadow facet
            (0.88, 0.84, 0.72),   # pale cream -- light-receiving plane
            (0.14, 0.11, 0.08),   # dark umber-black -- facet boundary lines
            (0.48, 0.42, 0.28),   # muted ochre-grey -- transitional plane zone
            (0.22, 0.18, 0.10),   # deep brown -- recessive deep shadow
            (0.80, 0.74, 0.54),   # warm buff -- secondary light register
            (0.32, 0.32, 0.30),   # neutral cool grey -- shadow-side plane
        ],
        ground_color=(0.55, 0.48, 0.30),     # warm ochre imprimatura
        stroke_size=12,
        wet_blend=0.32,
        edge_softness=0.15,
        jitter=0.035,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Analytic Cubism. Pablo Picasso (1881-1973) was the Spanish-French painter "
            "and co-founder of Cubism, the most influential visual art movement of the "
            "twentieth century. Working alongside Georges Braque in Paris from 1907-1914, "
            "Picasso developed a pictorial language that abandoned single-viewpoint "
            "perspective inherited from the Renaissance and replaced it with a simultaneous "
            "multi-viewpoint analysis of three-dimensional form on a two-dimensional surface. "
            "The intellectual starting point was Cezanne\'s insight that every natural form "
            "can be analyzed as cylinder, sphere, and cone. Picasso took this geometric "
            "analysis to its conclusion: if a form consists of multiple geometric planes, "
            "why show only the planes visible from one viewpoint? CUBISM collapses the "
            "temporal experience of walking around an object -- seeing all its planes "
            "sequentially -- into a single simultaneous image. "
            "ANALYTIC CUBISM (1907-1912): Severely restricted palette -- ochre, raw umber, "
            "warm grey, pale cream, near-black -- to eliminate color as distraction and "
            "force attention onto structural analysis. The surface is fractured into "
            "hundreds of small angular facets, each a different tonal register of the "
            "restricted palette, suggesting a different plane at a different angle to the "
            "light. Subject and ground interpenetrate. "
            "SIGNATURE WORKS: Portrait of Ambroise Vollard (1910) -- the art dealer\'s "
            "face fragmented into 60+ angular facets in grey-ochre-umber; Ma Jolie "
            "(1911-12) -- figure so thoroughly analyzed only traces of form remain; "
            "Les Demoiselles d\'Avignon (1907) -- pre-Cubist breakthrough; "
            "Three Musicians (1921) -- Synthetic Cubism at its most joyful; "
            "Guernica (1937) -- bombing of the Basque town in black, white, and grey "
            "Cubist fragments: screaming figures, horse, bull, flames, broken lamp."
        ),
        famous_works=[
            ("Les Demoiselles d\'Avignon",       "1907"),
            ("Portrait of Ambroise Vollard",     "1910"),
            ("Ma Jolie",                         "1911-12"),
            ("Bottle of Vieux Marc",             "1913"),
            ("Three Musicians",                  "1921"),
            ("Girl Before a Mirror",             "1932"),
            ("Guernica",                         "1937"),
            ("Weeping Woman",                    "1937"),
            ("Night Fishing at Antibes",         "1939"),
            ("Le Dejeuner sur l\'herbe",          "1960"),
        ],
        inspiration=(
            "picasso_cubist_fragmentation_pass(): FOUR-STAGE ANGULAR VORONOI FACET "
            "DECOMPOSITION -- 186th distinct mode. "
            "(1) DISPLACEMENT-DISTORTED VORONOI TESSELLATION: gaussian-blurred noise "
            "field displaces pixel coordinate space before KDTree nearest-neighbor "
            "assignment; creates irregular angular shard-like cells; first pass to use "
            "displacement-distorted pixel coordinates for tessellation; "
            "(2) PER-FACET TONAL VARIATION: N(0, tonal_variance) luminance shifts per "
            "Voronoi cell; stacked-plane effect with independent tonal registers; first "
            "pass to apply per-region independent random luminance modulation; "
            "(3) ANALYTIC CUBISM PALETTE RESTRICTION: KDTree nearest-colour to palette "
            "{ochre, warm_grey, raw_umber, pale_cream, dark_umber}; mutes toward the "
            "restricted 1909-1912 ochre-grey-umber continuum; first pass to restrict "
            "palette to a historically-defined pigment set; "
            "(4) FACET BOUNDARY DARKENING: discrete Voronoi boundary detection (4-"
            "connected neighbour difference); darkened by edge_darkness; dilated by "
            "edge_width; simulates the dark contour lines between Cubist planes."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"picasso"' in src:
    print("picasso already in catalog -- nothing to do.")
    sys.exit(0)

INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + PICASSO_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Pablo Picasso into art_catalog.py.")
