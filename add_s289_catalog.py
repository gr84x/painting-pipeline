"""Insert Jean Dubuffet entry into art_catalog.py (session 289).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

DUBUFFET_ENTRY = '''
    # ── Jean Dubuffet ─────────────────────────────────────────────────────────
    "jean_dubuffet": ArtStyle(
        artist="Jean Dubuffet",
        movement="Art Brut / Outsider Art",
        nationality="French",
        period="1901-1985",
        palette=[
            (0.94, 0.92, 0.82),   # bone white -- chalky, flat, ash-like highlights
            (0.28, 0.19, 0.10),   # raw umber -- the dominant earth dark
            (0.68, 0.22, 0.10),   # iron oxide red -- rust, blood, raw mineral
            (0.80, 0.62, 0.16),   # yellow ochre -- clay, dry earth, warm mid
            (0.12, 0.11, 0.10),   # graphite black -- scored outlines, shadows
            (0.45, 0.34, 0.22),   # burnt sienna -- mid-tone earth mass
            (0.58, 0.50, 0.36),   # raw sienna -- lighter earth middle
            (0.20, 0.30, 0.52),   # Hourloupe blue -- flat saturated cell fill
            (0.78, 0.22, 0.24),   # Hourloupe red -- flat saturated cell fill
            (0.88, 0.84, 0.72),   # pale limestone -- architectural, skull-like
        ],
        ground_color=(0.42, 0.32, 0.18),  # raw sienna earth -- Dubuffet's typical ground
        stroke_size=18,
        wet_blend=0.22,
        edge_softness=0.20,
        jitter=0.055,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Art Brut / Outsider Art. Jean Dubuffet (1901-1985) was born in "
            "Le Havre, France, son of a wine merchant, and spent his twenties "
            "abandoning his art studies to run the family wine business, returning "
            "to full-time painting only at 41. This deliberate rejection of formal "
            "training was an ideological act: Dubuffet had concluded that Western "
            "art tradition was a suffocating orthodoxy of skill and refinement. "
            "In 1945 he coined the term ART BRUT ('raw art') for work created "
            "outside mainstream art: by psychiatric patients, self-taught outsiders, "
            "children. He collected it obsessively and founded the Collection de "
            "l'Art Brut in Lausanne. More importantly, he made it himself: his "
            "paintings deliberately emulated the directness and clumsiness of "
            "outsider art, rejecting illusionism in favour of thick, material, "
            "scratched surfaces. "
            "DUBUFFET'S FIVE DEFINING TECHNICAL SIGNATURES: "
            "(1) L'HOURLOUPE CELLULAR NETWORKS (1962-1974): His greatest series "
            "is defined by an irregular cellular grid -- interlocking jigsaw-like "
            "regions separated by heavy black lines, each cell filled with red-and-"
            "blue hatching or flat colour. The boundary lines are scored irregularly, "
            "like cracking earth or organic cell division. "
            "(2) EARTH MATERIAL MIXING: In his Texturologies/Materiologies (1957-1960), "
            "Dubuffet mixed paint with earth, sand, gravel, coal dust, glass, and tar. "
            "The surfaces are granular and absorptive: paint looks like dried mud. "
            "(3) PALETTE OF RAW MATERIALS: Dubuffet rejected Impressionist atmospheric "
            "light. His colours are the colours of matter: umber (earth), ochre (clay), "
            "iron oxide (rust), bone white (ash), graphite (charcoal). Even his most "
            "colourful works use only red-blue-white-black. "
            "(4) SCORED AND BITUMEN OUTLINES: Heavy, irregular, childlike contours -- "
            "sometimes scored into wet paint, sometimes drawn in bitumen over dry paint. "
            "Dark, primitive boundaries separate each form with raw authority. "
            "(5) ANTI-PERSPECTIVE FLATNESS: Dubuffet aggressively refused spatial depth. "
            "Figures are flattened against the picture plane; the five-colour palette "
            "removes atmospheric modulation that creates illusionistic depth. "
            "THE GREAT WORKS: 'Corps de Dames' (1950-1951); 'L'Hourloupe' series "
            "(1962-1974); 'Texturologies' (1957-1960); 'Paris Polka' (1961); "
            "'Coucou Bazar' (1972-1973 performance installation); "
            "'Mire G 115' (1983); 'Banque des figures' (1971)."
        ),
        famous_works=[
            ("Corps de Dames: Olympia",            "1950"),
            ("Texturologie XXV",                    "1958"),
            ("Paris Polka",                         "1961"),
            ("L'Hourloupe: Mur bleu",               "1966"),
            ("Jardin achard",                       "1970"),
            ("Banque des figures",                  "1971"),
            ("Coucou Bazar",                        "1973"),
            ("Mire G 115 (Bords et dedans)",        "1983"),
            ("Logologie V",                         "1984"),
            ("Non-lieux",                           "1984"),
        ],
        inspiration=(
            "dubuffet_art_brut_pass(): FOUR-STAGE ART BRUT SURFACE -- 200th "
            "distinct mode. "
            "(1) CELLULAR SCORING: sine-wave interference pattern: "
            "cell_d = min(|sin(fa*x+fb*y)|, |sin(fc*x+fd*y)|); "
            "line_mask = (cell_d < cell_line_width); darken boundary pixels by "
            "cell_line_dark fraction. FIRST CELLULAR NETWORK in engine -- "
            "creates irregular jigsaw topology simulating Dubuffet's l'Hourloupe "
            "cell divisions. "
            "(2) EARTH MATERIAL GRAIN: flat_idx = row*W+col; "
            "grain = abs(((flat_idx * grain_seed) mod 255) - 127) / 127; "
            "push toward raw sienna (0.62/0.32/0.18) at grain*grain_strength. "
            "FIRST INTEGER-MODULO GRAIN in engine (prior passes use Gaussian or "
            "uniform float noise); creates harsh deterministic salt-and-pepper "
            "simulating mixed earth material. "
            "(3) L1 PALETTE CONTRACTION: 5-entry raw-material palette; "
            "L1 distance = |dR|+|dG|+|dB| (taxicab metric); find nearest palette "
            "colour; blend at palette_strength*(1-line_mask*0.6). "
            "FIRST L1 PALETTE METRIC in engine (Hartley s287 used L2 Euclidean); "
            "L1 ball is rhombus vs L2 sphere, producing harder posterized fills. "
            "(4) SCORED EDGE DARKENING: Sobel edge magnitude on Gaussian-smoothed "
            "luminance; normalize; multiply pixel colour by (1-edge_norm*eds). "
            "Emulates Dubuffet's bitumen/charcoal scored outlines."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

assert "jean_dubuffet" not in src, "jean_dubuffet already exists in art_catalog.py"

ANCHOR = "\n\n}\n\n\ndef get_style"
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, DUBUFFET_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: jean_dubuffet entry inserted.")
