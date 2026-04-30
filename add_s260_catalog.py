"""Insert tsuguharu_foujita entry into art_catalog.py (session 260).

Run once to modify art_catalog.py; preserved as a change record afterward.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))

FOUJITA_ENTRY = """    "tsuguharu_foujita": ArtStyle(
        artist="Tsuguharu Foujita",
        movement="École de Paris / Japanese-Western Synthesis",
        nationality="Japanese-French",
        period="1886–1968",
        palette=[
            (0.97, 0.95, 0.88),   # milky ivory white, the luminous ground
            (0.18, 0.15, 0.12),   # lamp black, precise contour line
            (0.90, 0.72, 0.58),   # warm peach, nude skin light
            (0.78, 0.55, 0.42),   # raw sienna, skin mid-tone
            (0.65, 0.80, 0.82),   # muted teal, textile shadow
            (0.92, 0.85, 0.72),   # naples yellow, ambient warm glow
            (0.42, 0.38, 0.52),   # muted violet-grey, cast shadow
            (0.72, 0.62, 0.55),   # dusty rose-tan, secondary warmth
        ],
        ground_color=(0.97, 0.95, 0.88),    # milky ivory ground
        stroke_size=4,
        wet_blend=0.04,
        edge_softness=0.08,
        jitter=0.010,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Tsuguharu Foujita (1886–1968), born in Tokyo, emigrated to Paris "
            "in 1913 and became the most celebrated Japanese painter of the "
            "École de Paris circle. His work achieved an extraordinary synthesis "
            "of Japanese ink-painting discipline with Western oil technique. "
            "Three defining technical properties mark his mature style: "
            "(1) THE MILKY WHITE GROUND — Foujita's most famous innovation: "
            "a luminous, near-opaque ivory-white paint film achieved by "
            "applying extremely smooth, finely sanded titanium-white grounds "
            "and laying thin, creamy paint over them with a precise sable brush. "
            "The result was a skin quality unlike anything in Western painting: "
            "translucent, cool-warm, and luminous at the same time — as if "
            "light emanated from within the painted surface. Art historians "
            "believe the specific mixture included rabbit-skin glue and a "
            "particular Japanese pigment composition, though the exact recipe "
            "was never published. The milky white appears in his nudes, "
            "cats, and figures alike, giving them a porcelain luminosity; "
            "(2) JAPANESE-INK CONTOUR DRAWING — Foujita never abandoned the "
            "Japanese sumie ink-drawing tradition. He drew his outlines in "
            "oil paint applied with a very fine sable brush to create hair-thin "
            "contour lines of remarkable precision, defining volumes without "
            "Western modeling (chiaroscuro). The line is the structural element "
            "rather than tonal shadow — a profoundly Eastern approach applied "
            "to Western oil on canvas. Individual cat hairs, eyelashes, fur "
            "patterns, and fabric weave details are drawn as individual "
            "fine marks, not blended as texture; "
            "(3) SURFACE MICRO-TEXTURE — across his pale grounds Foujita laid "
            "a fine overall texture built from tiny individual marks — visible "
            "in cat fur, human skin, and textile surfaces alike. This "
            "micro-mark field gives the surface a tactile, almost tactile "
            "quality under raking light. The texture is directional, following "
            "surface contour and hair growth direction, functioning as a "
            "hatching-like tone-building system derived from Japanese calligraphy "
            "and ink practice but executed in oil paint."
        ),
        famous_works=[
            ("Self-Portrait with Cat",                "1928"),
            ("Reclining Nude with Toile de Jouy",     "1922"),
            ("The Two Friends",                        "1926"),
            ("My Room (the Alarm Clock)",              "1921"),
            ("Reclining Nude",                         "1918"),
            ("Cat",                                    "1927"),
            ("Woman with a Cat",                       "1923"),
            ("Mother and Child",                       "1959"),
            ("Battle of Adwa",                         "1938"),
            ("Nudes",                                  "1918"),
        ],
        inspiration=(
            "Foujita’s milky white ground and Japanese ink-contour technique "
            "inspired the foujita_milky_ground_contour_pass (171st distinct "
            "painting mode, session 260). The pass models three phenomena: "
            "(1) ivory ground luminosity lift that targets near-white highlight "
            "regions and pushes them toward the characteristic milky pearlescent "
            "tone of his prepared ground; (2) fine Japanese-ink contour tracing "
            "drawn along tonal-boundary edges in near-black oil-line marks, "
            "placed at the exact pixel-width precision of his sable-brush "
            "technique; (3) directional micro-texture hatching across pale "
            "surface zones, following local orientation to create the "
            "characteristic cat-fur and skin-surface fine mark field."
        ),
    ),
"""

CATALOG_FILE = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_FILE, "r", encoding="utf-8") as f:
    src = f.read()

if '"tsuguharu_foujita"' in src:
    print("tsuguharu_foujita already present -- skipping.")
    sys.exit(0)

# Insert before the closing brace of artist_catalog dict
# The pattern is the last entry then "}" closing the dict
ANCHOR = '    "zurbaran": ArtStyle('
if ANCHOR not in src:
    print(f"ERROR: anchor not found: {ANCHOR!r}")
    sys.exit(1)

src = src.replace(ANCHOR, FOUJITA_ENTRY + ANCHOR)

with open(CATALOG_FILE, "w", encoding="utf-8") as f:
    f.write(src)

print("tsuguharu_foujita inserted into art_catalog.py successfully.")
