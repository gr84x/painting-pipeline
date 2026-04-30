"""Insert Natalia Goncharova entry into art_catalog.py (session 267).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

GONCHAROVA_ENTRY = '''
    # ── Natalia Goncharova ───────────────────────────────────────────────────
    "natalia_goncharova": ArtStyle(
        artist="Natalia Goncharova",
        movement="Russian Avant-Garde / Rayonism / Neo-Primitivism",
        nationality="Russian",
        period="1881-1962",
        palette=[
            (0.92, 0.76, 0.10),   # sunflower gold — petals, harvest light
            (0.24, 0.14, 0.04),   # disc brown — sunflower centre, deep umber
            (0.16, 0.42, 0.10),   # stem green — leaves, stalk, peasant green
            (0.10, 0.14, 0.58),   # cobalt blue — sky field, Rayonist void
            (0.86, 0.44, 0.06),   # amber orange — evening light, ray warmth
            (0.24, 0.14, 0.52),   # violet — shadow ray, Rayonist cool
            (0.90, 0.62, 0.10),   # horizon gold — warm Rayonist source
            (0.58, 0.38, 0.14),   # sienna earth — ground, peasant palette
            (0.96, 0.90, 0.70),   # pale cream — canvas ground, sky zenith
        ],
        ground_color=(0.32, 0.22, 0.10),    # warm sienna-brown ground
        stroke_size=20,
        wet_blend=0.30,                      # direct, loaded marks — low blend
        edge_softness=0.18,                  # bold flat edges, Neo-Primitivist
        jitter=0.045,                        # energetic jitter — Rayonist vitality
        glazing=None,
        crackle=False,
        chromatic_split=True,                # Rayonist chromatic decomposition
        technique=(
            "Russian Rayonism and Neo-Primitivism. Goncharova\'s mature painting "
            "practice combines two seemingly opposed impulses: the bold, flat "
            "colour zones of Russian peasant icon painting and folk embroidery "
            "(Neo-Primitivism, 1906-1912) and the dynamic dissolving forms of "
            "Rayonism (1912-1914), in which all objects are understood as emitters "
            "of reflected light rays that cross in the space between subject and "
            "viewer. Her Rayonist paintings dissolve recognisable forms -- cats, "
            "sunflowers, forests, cyclists -- into families of roughly parallel "
            "coloured bands (rays), each family representing light reflected from "
            "a surface in a specific direction. Where ray families from different "
            "surfaces cross, the colours interfere: warm sunflower-gold rays cross "
            "cool violet-blue sky rays, producing zones of chromatic complexity "
            "at the intersections. The underlying form survives as a structural "
            "ghost but the dominant visual experience is one of dynamic energy "
            "exchange. In her Neo-Primitivist paintings, the folk-art flatness "
            "and bright declarative colours persist from her earlier Fauve period "
            "but with a specifically Russian peasant flavour: the peasant palette "
            "of dusty ochre, forest green, and burnt sienna, the compositional "
            "directness of icon and lubock (folk woodblock print), and the "
            "hieratic scale-independence where large and small figures coexist "
            "without spatial logic."
        ),
        famous_works=[
            ("Sunflowers",                  "1907"),
            ("The Cyclist",                 "1913"),
            ("Cats (Rayonist Percept)",      "1913"),
            ("The Peacock",                 "1911"),
            ("Haycutting",                  "1910"),
            ("The Forest",                  "1913"),
            ("Laundry",                     "1912"),
            ("Fishermen",                   "1909"),
        ],
        inspiration=(
            "goncharova_rayonist_pass(): THREE-STAGE RAYONIST LIGHT FRACTURE "
            "TECHNIQUE -- 178th distinct mode. "
            "(1) MULTI-ANGLE DIRECTIONAL STREAK SYNTHESIS: For each of 4 angles "
            "(0, 45, 90, 135 degrees), rotate the canvas, apply 1D Gaussian blur "
            "(ray_sigma=24px) along the rotated horizontal axis, rotate back, and "
            "accumulate -- the mean of 4 directional blurs synthesises crossing "
            "ray fields in the full 180-degree directional space; "
            "(2) LUMINANCE-WEIGHTED STREAK OVERLAY: bright pixels generate stronger "
            "ray contributions (normalised luminance modulates blend_factor at each "
            "pixel), simulating Rayonist ray emission proportional to light-source "
            "intensity; "
            "(3) CHROMATIC HUE SHIMMER AT RAY INTERFERENCE ZONES: in pixels where "
            "the ray composite diverges from the original above shimmer_threshold, "
            "a spatially-alternating hue rotation (+/-shimmer_angle degrees, "
            "alternating by sin(x*freq)*cos(y*freq) sign) creates chromatic "
            "vibration in the crossing-ray interference zones."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"natalia_goncharova"' in src:
    print("natalia_goncharova already in catalog -- nothing to do.")
    sys.exit(0)

INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + GONCHAROVA_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Natalia Goncharova into art_catalog.py.")
