"""Insert kathe_kollwitz entry into art_catalog.py (session 256).

Run once to modify art_catalog.py; preserved as a change record afterward.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))

KOLLWITZ_ENTRY = """    "kathe_kollwitz": ArtStyle(
        artist="Käthe Kollwitz",
        movement="German Expressionism / Social Realism",
        nationality="German",
        period="1867–1945",
        palette=[
            (0.12, 0.10, 0.09),   # deep charcoal black
            (0.28, 0.24, 0.21),   # dark graphite shadow
            (0.44, 0.39, 0.34),   # mid charcoal grey
            (0.62, 0.57, 0.51),   # warm mid-grey smear
            (0.78, 0.73, 0.67),   # lifted grey (partial erasure)
            (0.88, 0.85, 0.80),   # near-paper white
            (0.52, 0.46, 0.40),   # brown-grey shadow tone
            (0.36, 0.31, 0.27),   # compressed dark half-tone
        ],
        ground_color=(0.84, 0.80, 0.74),    # raw buff paper
        stroke_size=18,
        wet_blend=0.05,                      # dry -- charcoal does not blend wet
        edge_softness=0.42,                  # smeared edges -- charcoal smudges
        jitter=0.02,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Käthe Kollwitz (1867–1945) was the pre-eminent German Expressionist "
            "printmaker and draughtswoman of the early twentieth century. Working "
            "in Berlin, she produced lithographs, etchings, and charcoal drawings "
            "of extraordinary emotional and technical power. Her subjects -- the "
            "working poor, grieving mothers, anti-war protest -- were inseparable "
            "from her medium: charcoal and lithographic chalk impose a discipline "
            "of tonality that is entirely different from oil paint. Three technical "
            "signatures define Kollwitz's work: "
            "(1) DARK COMPRESSION AND TONAL COLLAPSE -- charcoal applied to buff "
            "paper cannot produce the full tonal range of oil: the paper provides "
            "the lightest value, and charcoal builds downward into darkness; "
            "Kollwitz used this constraint deliberately, compressing the tonal "
            "range toward the dark half of the scale so that the few pale "
            "passages -- an illuminated cheek, a child's forehead -- read with "
            "blinding power against the surrounding dark; the compression is not "
            "an accident of the medium but a rhetorical tool: the darkness presses "
            "in from all sides; "
            "(2) DIRECTIONAL SMEAR AND GESTURAL SWEEP -- Kollwitz built tone "
            "through broad lateral sweeps of the charcoal stick or the side of "
            "her hand, creating directionality in the mark that is absent from "
            "engraving or etching; figures emerge from the dark field through "
            "smeared transitions where the charcoal lifts along its stroke axis; "
            "the smear direction is often diagonal, following the gesture of the "
            "arm and body, and gives her figures their sense of physical weight "
            "and effort; "
            "(3) HIGHLIGHT LIFT -- in charcoal, the brightest passages are "
            "produced not by applying a light medium but by removing the dark one: "
            "erasing, lifting with a kneaded rubber eraser, or wiping with a rag; "
            "Kollwitz used this actively, pulling isolated bright zones from the "
            "dark field to create the sense of a single, harsh light falling on "
            "her subjects from one side; these lifted passages have a specific "
            "quality -- softer-edged than a painted highlight, with a faint "
            "residue of removed pigment at their perimeter."
        ),
        famous_works=[
            ("Woman with Dead Child",              "1903"),
            ("The Weavers' Revolt (cycle)",        "1897"),
            ("Peasants' War (cycle)",              "1908"),
            ("War (woodcut cycle)",                "1923"),
            ("Never Again War",                   "1924"),
            ("Mother with Two Children",           "1932"),
            ("Tower of Mothers",                   "1937"),
            ("Lamentation (In Memory of Ernst)",   "1938"),
            ("Self-Portrait in Profile",           "1938"),
        ],
        inspiration=(
            "Emulate Kollwitz's tonal compression toward darkness, directional "
            "charcoal smear, and eraser-lift highlight. The pipeline pass should: "
            "(1) compress luminance with a power-law toward the dark half of the "
            "tonal range; (2) apply an anisotropic directional smear via image "
            "rotation + asymmetric Gaussian blur to simulate broad gestural marks; "
            "(3) add sparse lifted-highlight zones that reveal near-paper tone "
            "at tonal peaks, simulating kneaded-eraser lifting of charcoal."
        ),
    ),
"""

ANCHOR = '"andrew_wyeth": ArtStyle('

catalog_path = os.path.join(REPO, "art_catalog.py")
with open(catalog_path, "r", encoding="utf-8") as f:
    src = f.read()

if '"kathe_kollwitz"' in src:
    print("kathe_kollwitz already present -- nothing to do.")
    sys.exit(0)

if ANCHOR not in src:
    print(f"ERROR: anchor {ANCHOR!r} not found in art_catalog.py", file=sys.stderr)
    sys.exit(1)

src = src.replace(ANCHOR, KOLLWITZ_ENTRY + "    " + ANCHOR, 1)

with open(catalog_path, "w", encoding="utf-8") as f:
    f.write(src)

print("Inserted kathe_kollwitz into art_catalog.py.")
