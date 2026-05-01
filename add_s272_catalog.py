"""Insert Max Ernst entry into art_catalog.py (session 272).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

ERNST_ENTRY = '''
    # ── Max Ernst ─────────────────────────────────────────────────────────────
    "max_ernst": ArtStyle(
        artist="Max Ernst",
        movement="Surrealism / Dada",
        nationality="German-French",
        period="1891-1976",
        palette=[
            (0.32, 0.20, 0.08),   # umber-ochre -- heavy paint mass, geological rock
            (0.58, 0.50, 0.35),   # pale sand-ochre -- thin paint veil, desert stone
            (0.08, 0.12, 0.24),   # prussian blue-indigo -- deep shadow / sky zone
            (0.18, 0.14, 0.10),   # dark umber -- deep foreground, vein shadows
            (0.62, 0.42, 0.22),   # warm terracotta -- mid-zone stone surface
            (0.72, 0.68, 0.55),   # pale warm grey -- atmospheric sky, mist
            (0.12, 0.22, 0.16),   # deep forest-green -- organic decalcomania zones
            (0.48, 0.35, 0.28),   # muted rose-umber -- biomorphic warm zones
            (0.85, 0.76, 0.55),   # light gold -- horizon atmospheric glow
        ],
        ground_color=(0.20, 0.16, 0.10),     # deep warm umber-ochre ground
        stroke_size=20,
        wet_blend=0.18,                       # moderate -- decalcomania has both sharp and soft edges
        edge_softness=0.22,                   # partially soft -- organic forms dissolve at margins
        jitter=0.038,                         # moderate jitter -- automatic technique, not controlled
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Surrealism and Dada. Max Ernst (1891-1976) was one of the most "
            "technically inventive painters of the twentieth century, and the "
            "central figure of Surrealism after his formative years in the Cologne "
            "Dada circle. Where other Surrealists (Dali, Magritte) achieved their "
            "dreamlike imagery through hyperrealist illusionism applied to impossible "
            "subjects, Ernst developed a suite of AUTOMATIC, CHANCE-BASED TECHNIQUES "
            "that allowed unconscious imagery to emerge directly from the physical "
            "behavior of paint and pencil: frottage (1925, rubbing pencil over "
            "textured surfaces to reveal hidden images), grattage (scraping wet "
            "paint from canvas), and most notably DECALCOMANIA (1936, adopted from "
            "Oscar Dominguez) -- spreading wet paint between two surfaces, pressing "
            "them together, and rapidly pulling them apart to create dendritic, "
            "cave-like, visceral biomorphic textures. Ernst saw in decalcomania "
            "the image of geological time: limestone caves dissolving, river deltas "
            "branching, crystal lattices forming, tissue differentiating. His "
            "masterwork in this mode is 'Europe After the Rain II' (1940-42): a "
            "post-apocalyptic landscape of ruined spires, organic architecture, and "
            "biomorphic stone formations, entirely surface-textured by decalcomania, "
            "overpainted in his characteristic earth palette -- ochre, umber, "
            "prussian blue, deep green. The BIRD SUPERIOR (Loplop) was his totem "
            "alter ego: a bird-headed creature who presides over the artist's work, "
            "appearing in countless paintings as both self-portrait and mythic figure. "
            "Ernst's palette is anchored in geological earth colors -- umber, ochre, "
            "sienna, raw and burnt -- with deep prussian blue and forest green as "
            "the shadow and atmospheric registers. Against this earth palette, "
            "passages of pale warm sand and gold read as light and sky. The surface "
            "texture -- the primary visual experience of his mature work -- is "
            "biological, geological, and architectural simultaneously: the viewer "
            "cannot determine whether they are looking at a rock face, a cave "
            "interior, a cross-section of wood, or the inner surface of a ribcage. "
            "This fundamental ambiguity of material identity is Ernst's central "
            "contribution to the visual art of the twentieth century."
        ),
        famous_works=[
            ("Europe After the Rain II",           "1940-1942"),
            ("The Eye of Silence",                 "1943-1944"),
            ("Celebes",                            "1921"),
            ("Two Children Are Threatened by a Nightingale", "1924"),
            ("The Forest",                         "1925"),
            ("Surrealism and Painting",            "1942"),
            ("The Temptation of St. Anthony",      "1945"),
            ("Vox Angelica",                       "1943"),
            ("The Antipope",                       "1941"),
            ("Une Semaine de Bonte",               "1934"),
        ],
        inspiration=(
            "ernst_decalcomania_pass(): FOUR-STAGE BIOMORPHIC PAINT TRANSFER TEXTURE "
            "-- 183rd distinct mode. "
            "(1) MULTI-OCTAVE TURBULENCE PRESSURE FIELD: layered sine-wave turbulence "
            "at exponentially increasing frequencies, simulating the complex spatial "
            "pressure distribution when two paint-covered surfaces are pressed "
            "together; pressure_octaves layers with amplitude halving at each "
            "frequency doubling; normalized to [0,1]; "
            "(2) PAINT TRANSFER ZONE DETECTION AND BOUNDARY GRADIENT: high-pressure "
            "zones (> 0.5) = dense paint transfer (dark, saturated), low-pressure "
            "zones (<= 0.5) = thin veil transfer (pale); compute Sobel gradient of "
            "Gaussian-smoothed pressure field to locate biomorphic zone boundaries "
            "(dendritic split lines); first pass to derive zone boundaries from a "
            "SYNTHETIC PHYSICAL PROCESS FIELD (pressure) rather than from pixel "
            "luminance, content variance, or position; "
            "(3) BIOMORPHIC COLOR INJECTION: high-pressure zones blended toward "
            "umber-ochre (bio_dark), low-pressure zones toward pale sand-ochre "
            "(bio_light), proportional to pressure field value; Ernst\\'s "
            "characteristic earth palette -- ochre, umber, burnt sienna -- "
            "applied to the pressure-field zones; "
            "(4) DENDRITIC VEIN REINFORCEMENT: darken gradient-peak pixels "
            "(zone boundaries) by vein_strength * gradient_norm, recreating "
            "the fine branching vein lines at decalcomania split boundaries."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"max_ernst"' in src:
    print("max_ernst already in catalog -- nothing to do.")
    sys.exit(0)

INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + ERNST_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Max Ernst into art_catalog.py.")
