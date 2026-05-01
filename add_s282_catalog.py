"""Insert Alexei Savrasov entry into art_catalog.py (session 282).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

SAVRASOV_ENTRY = '''
    # ── Alexei Savrasov ───────────────────────────────────────────────────────
    "alexei_savrasov": ArtStyle(
        artist="Alexei Savrasov",
        movement="Russian Realism / Lyrical Landscape / Peredvizhniki",
        nationality="Russian",
        period="1830-1897",
        palette=[
            (0.64, 0.68, 0.74),   # Savrasov grey -- the cool violet-grey of late-winter Russian light
            (0.76, 0.74, 0.68),   # pale sky -- overcast late February, near-white warm-grey at zenith
            (0.44, 0.40, 0.34),   # bare branch umber -- birch twigs against pale sky
            (0.74, 0.68, 0.46),   # warm straw ochre -- snow-covered stubble fields in weak sunlight
            (0.32, 0.30, 0.26),   # dark bark -- shadow side of bare birch trunks
            (0.82, 0.80, 0.76),   # high snow -- snow-covered rooftops and open field highlights
            (0.48, 0.44, 0.38),   # melting earth -- exposed soil where snow has retreated
            (0.58, 0.62, 0.68),   # sky reflection in thaw water -- cool blue in puddles and channels
            (0.52, 0.48, 0.36),   # dead grass -- winter-bleached field grass at lower margins
            (0.36, 0.38, 0.44),   # distant treeline grey -- forest silhouette in cool haze
        ],
        ground_color=(0.68, 0.64, 0.56),     # pale warm-grey ground (overcast winter light)
        stroke_size=9,
        wet_blend=0.22,
        edge_softness=0.20,
        jitter=0.018,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Russian Realism, Lyrical Landscape, Peredvizhniki. "
            "Alexei Kondratyevich Savrasov (1830-1897) was born in Moscow "
            "to a merchant family and entered the Moscow School of Painting "
            "at fourteen. He showed such early talent that he was made a full "
            "member of the Imperial Academy of Arts by the age of twenty-four. "
            "His early career was competent but conventional -- Italianate in "
            "composition and idealized in treatment of light. His decisive "
            "breakthrough came in 1871 when he exhibited 'The Rooks Have Come "
            "Back' at the first Peredvizhniki exhibition in St. Petersburg. "
            "The painting -- a view of bare birch trees against a pale grey-violet "
            "late-winter sky, with rooks returning to their nests, a church and "
            "bell tower visible across the field -- was immediately understood "
            "as transformative. It was the first Russian landscape to achieve "
            "genuine lyrical emotion through the specific observation of a specific "
            "place and season rather than through idealization. "
            "SAVRASOV'S FOUR TECHNICAL SIGNATURES: "
            "(1) HORIZONTAL ATMOSPHERIC MIST LAYERING: Savrasov's skies are "
            "painted as subtle horizontal bands of different luminance and hue "
            "-- not a simple gradient but a record of the actual optical structure "
            "of the lower atmosphere on a damp late-winter day: water vapor, fog, "
            "and distance creating a succession of pale grays, violets, and ochers "
            "near the horizon. No prior Russian landscape painter had rendered "
            "this horizontal layering with such meteorological precision. "
            "(2) EARLY SPRING COOL-GREY: The specific color of Russian late-February "
            "and early-March light -- after the coldest grey of deep winter but "
            "before the warmth of spring -- is a luminous, slightly violet-toned "
            "grey that Savrasov captured better than any of his successors. "
            "Isaac Levitan, who learned directly from Savrasov, described his "
            "teacher's grey as 'full of color, though seemingly colorless.' "
            "(3) BARE-BRANCH PRECISION: Savrasov's bare birch and alder branches "
            "silhouetted against pale skies are botanically specific and sharply "
            "rendered -- the sharpest elements in otherwise atmospheric paintings. "
            "They function as the emotional spine of the composition. "
            "(4) WARM STRAW HORIZON BLEEDS: Despite the cool dominant tone, "
            "Savrasov's lower zones carry a warm note -- snow-covered stubble "
            "fields in yellow-ochre, raw sienna where snow has melted, warm amber "
            "dead grass at the field margins. This warm note in the lower zone "
            "creates the color temperature dialogue that distinguishes his work "
            "from purely grey winter landscapes. "
            "LEGACY: Savrasov taught Isaac Levitan and Konstantin Korovin. "
            "His 'The Rooks Have Come Back' remains the most emotionally recognized "
            "landscape in the history of Russian painting."
        ),
        famous_works=[
            ("The Rooks Have Come Back",           "1871"),
            ("Thaw",                               "1874"),
            ("Rainbow",                            "1875"),
            ("Early Spring",                       "1880"),
            ("Spring Day",                         "1873"),
            ("Village. Winter",                    "1871"),
            ("At the Beginning of Spring",         "1883"),
            ("The Volga near Yuryevets",           "1870"),
            ("Winter Night",                       "1869"),
            ("Country Road",                       "1873"),
        ],
        inspiration=(
            "savrasov_lyrical_mist_pass(): FOUR-STAGE LYRICAL LANDSCAPE SYSTEM "
            "-- 193rd distinct mode. "
            "(1) HORIZONTAL ATMOSPHERIC MIST BANDING: horizontal uniform filter "
            "(kernel ~1:40 height:width ratio, e.g. 5×81 pixels); complement of "
            "shishkin's vertical filter (s281); first pass to use horizontal-dominant "
            "uniform filter for atmospheric layering rather than bark grain. "
            "(2) MID-LUMINANCE BELL-GATE COOL-GREY PUSH: bell-shaped smoothstep "
            "gate (product of two opposing ramps) centered in mid-luminance range "
            "(0.38-0.68); push toward Savrasov cool-grey (0.62/0.67/0.76); first "
            "pass to use bell-shaped gate targeting mid-luminance specifically rather "
            "than thresholded high/low zones. "
            "(3) VERTICAL GRADIENT (Gy) SHARPENING FOR BARE BRANCHES: y-component "
            "of Gaussian derivative isolates horizontal edges (branch outlines "
            "against sky); unsharp mask applied only in high-Gy zones; first pass "
            "to decompose gradient into directional components and use a single "
            "component (Gy) as a pass gate. "
            "(4) LOWER-ZONE × SATURATION GATE WARM OCHRE HORIZON: spatial lower-zone "
            "mask × low-saturation mask combined (shishkin used saturation-only, "
            "no spatial constraint); push toward warm straw-ochre (0.74/0.68/0.46); "
            "first pass to gate horizon color push on BOTH spatial position AND "
            "saturation simultaneously."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

# Verify no duplicate
assert "alexei_savrasov" not in src, "alexei_savrasov already exists in art_catalog.py"

# Insert before the closing brace of CATALOG dict
ANCHOR = "\n\n}\n\n\ndef get_style"
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, SAVRASOV_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: alexei_savrasov entry inserted.")
