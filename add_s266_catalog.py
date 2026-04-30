"""Insert Akseli Gallen-Kallela entry into art_catalog.py (session 266).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

GALLEN_KALLELA_ENTRY = '''
    # ── Akseli Gallen-Kallela ────────────────────────────────────────────────
    "akseli_gallen_kallela": ArtStyle(
        artist="Akseli Gallen-Kallela",
        movement="Finnish National Romanticism / Symbolism / Art Nouveau",
        nationality="Finnish",
        period="1865–1931",
        palette=[
            (0.94, 0.92, 0.88),   # birch white — brilliant trunk highlight
            (0.12, 0.10, 0.08),   # dark umber — trunk node, forest shadow
            (0.82, 0.40, 0.08),   # burnt orange — autumn leaf, dusk sky
            (0.18, 0.26, 0.72),   # cobalt blue — sky, lake, Finland's colour
            (0.14, 0.32, 0.14),   # deep forest green — spruce, pine shadow
            (0.68, 0.52, 0.12),   # golden ochre — autumn floor, late sun
            (0.06, 0.08, 0.18),   # lake blue-black — dark water, night
            (0.72, 0.18, 0.12),   # crimson — Kalevala accent, rowan berry
        ],
        ground_color=(0.24, 0.18, 0.10),    # dark umber ground
        stroke_size=16,
        wet_blend=0.38,                      # firm, loaded brush — low wet blend
        edge_softness=0.22,                  # hard edges, bold outlines
        jitter=0.035,                        # restrained — zones, not impressionism
        glazing=None,
        crackle=False,
        chromatic_split=False,               # no chromatic aberration — flat clean zones
        technique=(
            "Finnish National Romantic enamel cloisonne. Gallen-Kallela builds "
            "his compositions from flat, boldly bounded colour zones directly "
            "inspired by Japanese woodblock printing, medieval stained glass, and "
            "Byzantine enamel work. Each zone is a declarative category of colour "
            "— the birch trunk is WHITE, the sky is COBALT, the forest floor is "
            "BURNT SIENNA — rather than a modulated tonal field. Zone boundaries "
            "are reinforced with bold dark outlines painted with a thin pointed "
            "brush (the cloison effect). The palette is assertively decorative: "
            "cobalt blue, burnt orange, forest green, cream-white, dark umber, and "
            "crimson accent; neutral greys and half-tones are minimal. The effect "
            "is simultaneously monumental and intimate — the heroic scale of "
            "Kalevala mythology rendered in the domestic language of stained glass. "
            "Gallen-Kallela's mature oil technique emphasises loaded flat strokes "
            "applied with a painting knife or stiff hog-hair brush, building "
            "surfaces that have the enamel quality of glazed tile rather than the "
            "atmospheric haze of French Impressionism. The absence of aerial "
            "perspective is intentional — the forest behind the lake reads as a "
            "flat dark silhouette, not a receding atmospheric plane."
        ),
        famous_works=[
            ("The Aino Myth (triptych)",          "1891"),
            ("Symposium",                         "1894"),
            ("Lake Keitele",                      "1906"),
            ("The Kalevala Illustrations",        "1922"),
            ("Autumn Landscape",                  "1902"),
            ("Forssa",                            "1888"),
            ("Boy and Crow",                      "1884"),
            ("Fishing in the Stream",             "1886"),
        ],
        inspiration=(
            "gallen_kallela_enamel_cloisonne_pass(): THREE-STAGE ENAMEL CLOISONNE "
            "DECORATIVE TECHNIQUE -- 177th distinct mode. "
            "(1) CIRCULAR-HUE ZONE FLATTENING: Gaussian-weighted circular mean of "
            "hue (sin/cos encoding, sigma=flat_sigma) blended toward local hue mean "
            "at zone_blend strength -- unifies within-zone hue to create flat colour "
            "areas in the Japanese woodblock / enamel tradition; "
            "(2) BOLD CONTOUR DARKENING: Sobel edge magnitude computed from the "
            "hue-flattened canvas (not original), Gaussian-feathered, applied as "
            "multiplicative darkening at contour_strength -- produces clean bold "
            "partition lines between unified zones; "
            "(3) DECORATIVE PALETTE SATURATION PUNCH: saturation-gated per-pixel "
            "chroma amplification from luminance (sat_boost, bounded by sat_floor "
            "and sat_ceil) -- pushes zones toward the jewel-bright enamel quality "
            "of Gallen-Kallela\'s decorative palette."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"akseli_gallen_kallela"' in src:
    print("akseli_gallen_kallela already in catalog -- nothing to do.")
    sys.exit(0)

INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + GALLEN_KALLELA_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Akseli Gallen-Kallela into art_catalog.py.")
