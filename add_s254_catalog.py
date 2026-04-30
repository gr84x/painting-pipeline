"""Insert paula_rego entry into art_catalog.py (session 254).

Run once to modify art_catalog.py; preserved as a change record afterward.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))

REGO_ENTRY = """    "paula_rego": ArtStyle(
        artist="Paula Rego",
        movement="Figurative / Neo-Expressionism",
        nationality="Portuguese-British",
        period="1935–2022",
        palette=[
            (0.22, 0.18, 0.14),   # deep shadow black-brown
            (0.68, 0.52, 0.38),   # warm earthy sienna
            (0.84, 0.76, 0.62),   # pale flesh ochre
            (0.46, 0.38, 0.54),   # muted violet-grey
            (0.28, 0.40, 0.28),   # dull sage green
            (0.72, 0.38, 0.26),   # burnt terracotta red
            (0.88, 0.84, 0.76),   # cold cream white
            (0.52, 0.48, 0.44),   # mid neutral grey
            (0.36, 0.28, 0.44),   # dark plum shadow
            (0.78, 0.68, 0.44),   # warm golden straw
        ],
        ground_color=(0.60, 0.54, 0.46),
        stroke_size=22,
        wet_blend=0.30,
        edge_softness=0.28,
        jitter=0.14,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Paula Rego (1935–2022, Lisbon / London) is among the most "
            "powerful figurative painters of the twentieth century, known for "
            "psychologically charged narratives drawn from fairy tales, folk "
            "mythology, nursery rhymes, and her own Portuguese Catholic "
            "childhood. She studied at the Slade School of Fine Art under "
            "William Coldstream and later became the first Associate Artist "
            "at the National Gallery, London. Her work consistently centres on "
            "women -- their power, subjugation, resilience, and darkness -- "
            "and is notable for its deliberately distorted, heavy-bodied "
            "figures that root characters in physical reality rather than "
            "idealisation. Three technical signatures define Rego's work: "
            "(1) FLAT FIGURE BLOCKING WITH TONAL POSTERISATION -- Rego applies "
            "pastel (her dominant medium from the 1990s onward) in large flat "
            "zones of colour with remarkably little blending; each area is a "
            "single flattened tone, almost posterised, giving figures the "
            "weight and immediacy of cut paper silhouettes; there is no "
            "atmospheric perspective softening -- every surface is equally "
            "present; (2) HEAVY CONTOUR OUTLINING AND EDGE TENSION -- the "
            "boundaries between figure and ground, between light and shadow "
            "planes, are drawn with deliberate heaviness; Rego uses a dark, "
            "slightly warm outline to define forms with the directness of a "
            "cartoonist and the weight of a woodcut; these outlines are not "
            "academic but psychological -- they contain the figure, they make "
            "it solid and inescapable; (3) CONFRONTATIONAL SPATIAL FLATTENING "
            "-- Rego eliminates deep perspective, pressing figures against flat "
            "backgrounds or shallow stage-like settings; the figures loom, "
            "they fill the picture plane; this pictorial flattening combined "
            "with heavy figuration creates the specific psychological pressure "
            "of her work -- there is no escape from the figure, no distance, "
            "no relief through recession."
        ),
        famous_works=[
            ("The Maids",                         "1987"),
            ("Dog Women",                         "1994"),
            ("Jane Eyre (series)",                "2001–2002"),
            ("The Dance",                         "1988"),
            ("Abortion (series)",                 "1998–1999"),
            ("Nursery Rhymes (series)",           "1989"),
            ("The Family",                        "1988"),
            ("Angel",                             "1998"),
            ("Pendle Witches (series)",           "1996"),
        ],
        inspiration=(
            "rego_flat_figure_pass(): ONE HUNDRED AND SIXTY-FIFTH "
            "(165th) distinct mode -- three-stage flat figure posterisation "
            "with contour weight and chromatic tension -- "
            "(1) TONAL ZONE POSTERISATION: reduce the canvas colour space to "
            "n_levels flat tonal steps using per-channel quantisation; within "
            "each quantised zone apply a local mean-colour smoothing weighted "
            "by zone_blend to produce the flat, area-filled quality of Rego's "
            "pastel zones; first pass to apply zone-mean colour flattening as "
            "a figurative posterisation (distinct from paint_posterize_pass "
            "which quantises globally without local zone-mean smoothing); "
            "(2) WARM CONTOUR OUTLINING: detect luminance-gradient edges above "
            "contour_threshold; darken those edge pixels by blending toward "
            "a warm dark outline_tone at contour_strength; apply contour "
            "width of contour_px pixels via dilation; first pass to apply "
            "warm-toned darkening specifically to detected contour-edge pixels "
            "as a figurative outline simulation (distinct from "
            "paint_contour_weight_pass which applies variable-weight contours); "
            "(3) CHROMATIC ZONE TENSION: divide canvas into a 2x2 spatial grid; "
            "apply a slight warm push (toward tension_warm) to figure-zone "
            "pixels (upper-right and lower-left quadrants) and a slight cool "
            "push (toward tension_cool) to ground-zone pixels; first pass to "
            "apply quadrant-indexed warm/cool chromatic tension as a spatial "
            "figure-ground separation technique."
        ),
    ),
"""

CATALOG_FILE = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_FILE, "r", encoding="utf-8") as f:
    src = f.read()

assert "paula_rego" not in src, "paula_rego already present in art_catalog.py"

INSERT_BEFORE = '    "anselm_kiefer":'
assert INSERT_BEFORE in src, f"Anchor {INSERT_BEFORE!r} not found in art_catalog.py"

new_src = src.replace(INSERT_BEFORE, REGO_ENTRY + INSERT_BEFORE)

with open(CATALOG_FILE, "w", encoding="utf-8") as f:
    f.write(new_src)

print("paula_rego entry inserted into art_catalog.py")
