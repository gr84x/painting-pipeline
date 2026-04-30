"""Insert Arshile Gorky entry into art_catalog.py (session 269).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

GORKY_ENTRY = '''
    # ── Arshile Gorky ────────────────────────────────────────────────────────
    "arshile_gorky": ArtStyle(
        artist="Arshile Gorky",
        movement="Biomorphic Abstraction / Abstract Expressionism",
        nationality="Armenian-American",
        period="1904-1948",
        palette=[
            (0.92, 0.82, 0.58),   # warm cream — luminous ground (shows through)
            (0.14, 0.36, 0.22),   # deep viridian — biomorphic form masses
            (0.72, 0.16, 0.18),   # crimson/burgundy — accent flower forms
            (0.68, 0.44, 0.10),   # ochre amber — warm sky and earth
            (0.30, 0.16, 0.08),   # dark umber — contour drawing medium
            (0.52, 0.32, 0.12),   # burnt sienna — transition zone warmth
            (0.82, 0.72, 0.40),   # yellow-gold — luminous mid-tone
            (0.18, 0.22, 0.38),   # dark indigo — deep shadow masses
            (0.60, 0.22, 0.28),   # rose-crimson — secondary accent
        ],
        ground_color=(0.92, 0.88, 0.76),    # warm cream-ochre — Gorky's characteristic ground
        stroke_size=18,
        wet_blend=0.32,                      # fluid, thin paint quality
        edge_softness=0.28,                  # biomorphic soft edges
        jitter=0.040,                        # organic gestural quality
        glazing=None,
        crackle=False,
        chromatic_split=False,               # unified fluid surface
        technique=(
            "Armenian-American Biomorphic Abstraction. Arshile Gorky "
            "(Vosdanig Manoug Adoian, 1904-1948) spent two decades synthesising "
            "the lessons of Cézanne, Picasso, Miró, and Kandinsky before arriving "
            "at a wholly original language: biomorphic organic forms derived from "
            "memory and automatic drawing, built up in transparent fluid oil washes "
            "on a warm luminous ground. His Garden in Sochi series (c.1940-41) -- "
            "inspired by his father\'s garden in Armenian Van province -- marks the "
            "definitive arrival of his mature style. Biomorphic forms in deep "
            "viridian, crimson, burnt sienna, and ochre float on a pale cream "
            "ground that glows through every layer of thinned oil. Contour lines "
            "in dark umber trace the edges of forms in a manner simultaneously "
            "painted and drawn -- heir to his rigorous study of Ingres\'s line, "
            "transformed by Miró\'s Surrealist biomorphism. Paint is heavily "
            "thinned with turpentine; each layer is a transparent wash. The "
            "ground breathes through the form; the boundary between form and air "
            "is the most richly painted zone, where saturation rises and falls "
            "and the thinned paint bleeds slightly along the canvas grain. Gorky "
            "bridges the European Surrealist tradition (biomorphism, automatism, "
            "the unconscious as pictorial source) and the American Abstract "
            "Expressionism that would follow him: de Kooning, Pollock, and "
            "Rothko all acknowledged his decisive influence. He died in 1948 at "
            "44, leaving a body of work that remains among the most organically "
            "alive in all of twentieth-century painting."
        ),
        famous_works=[
            ("The Artist and His Mother",         "1936"),
            ("Garden in Sochi",                   "1941"),
            ("The Liver is the Cock\'s Comb",      "1944"),
            ("One Year the Milkweed",             "1944"),
            ("Agony",                             "1947"),
            ("Betrothal II",                      "1947"),
            ("The Calendars",                     "1947"),
            ("Dark Green Painting",               "1948"),
        ],
        inspiration=(
            "gorky_biomorphic_fluid_pass(): FOUR-STAGE BIOMORPHIC OIL TECHNIQUE "
            "-- 180th distinct mode. "
            "(1) SATURATION MAP AND FORM ZONE DETECTION: compute per-pixel HSV "
            "saturation, smooth to get local saturation mean, identify high-sat "
            "zones (biomorphic forms: sat > mean * 1.10) and low-sat zones "
            "(air/ground: sat < mean * 0.70) -- first pass to use saturation "
            "deviation from local neighbourhood mean as a form detection signal; "
            "(2) FLUID WASH IN FORM ZONES: enrich high-saturation zones by "
            "pulling channels away from luminance (wash_strength 0.20 ≈ thin "
            "transparent glaze), simulating Gorky\'s heavily-thinned oil washes "
            "that deepen form colour without obliterating the ground; "
            "(3) ORGANIC CONTOUR SYNTHESIS: compute Sobel luminance gradient "
            "magnitude, overlay dark umber contour lines at gradient boundaries "
            "-- simulating Gorky\'s painted contour drawing at biomorphic form "
            "edges, the only pass to introduce a drawn-line quality via gradient "
            "boundary overlay in a specific dark pigment colour; "
            "(4) WARM GROUND RE-EXPOSURE AND PAINT BLEED: lift low-saturation "
            "ground zones toward warm cream (simulating canvas luminosity showing "
            "through thin paint) + Gaussian bleed at contour boundaries (simulating "
            "thinned-medium bleed along canvas grain at form edges)."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"arshile_gorky"' in src:
    print("arshile_gorky already in catalog -- nothing to do.")
    sys.exit(0)

INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + GORKY_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Arshile Gorky into art_catalog.py.")
