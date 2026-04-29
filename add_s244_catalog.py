"""Insert max_beckmann entry into art_catalog.py (session 244)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

BECKMANN_ENTRY = '''    "max_beckmann": ArtStyle(
        artist="Max Beckmann",
        movement="German Expressionism / New Objectivity",
        nationality="German",
        period="1884-1950",
        palette=[
            (0.82, 0.42, 0.28),   # salmon-orange (Beckmann flesh/background)
            (0.62, 0.72, 0.22),   # acid yellow-green (acidic interior light)
            (0.14, 0.28, 0.56),   # cold blue-violet (shadow/drapery)
            (0.60, 0.14, 0.16),   # brick red (theatrical highlight)
            (0.24, 0.44, 0.40),   # deep teal (costume/background)
            (0.06, 0.05, 0.04),   # near-black armature (drawn contour)
            (0.92, 0.90, 0.88),   # zinc white (highlight slab)
            (0.54, 0.34, 0.22),   # raw umber (shadow modelling)
        ],
        ground_color=(0.20, 0.18, 0.14),
        stroke_size=11,
        wet_blend=0.14,
        edge_softness=0.05,
        jitter=0.12,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Max Beckmann (1884-1950) stands apart from his Expressionist contemporaries "
            "by fusing the psychological urgency of German Expressionism with the "
            "compositional density of the Old Masters -- Rubens, Rembrandt, and above "
            "all the medieval German altarpiece tradition.  His mature work is structured "
            "around a black linear armature: every form, however dynamic or distorted, "
            "is enclosed within a drawn contour of near-black paint that simultaneously "
            "bounds pictorial space, declares the act of drawing, and prevents the "
            "canvas from dissolving into Impressionistic colour atmosphere.  This "
            "armature is not an outline applied after the fact -- it is the structural "
            "skeleton of the image, laid in early and reinforced through successive "
            "paint layers.  Within the bounded forms, Beckmann\'s colour is violently "
            "non-naturalistic: salmon-orange backgrounds, acid yellow-green flesh, "
            "cold blue-violet shadows, and theatrical brick-red highlights create a "
            "palette of psychological dissonance rather than optical description.  "
            "His pictorial space is aggressively compressed: figures are forced into "
            "the picture plane, limbs overlap ambiguously, recession is denied by "
            "the uniformly heavy paint surface and the absence of atmospheric "
            "perspective -- the opposite of aerial recession.  This claustrophobia "
            "is not accidental; it encodes the existential condition of a man who "
            "lived through two World Wars, witnessed the collapse of the Weimar "
            "Republic, and was forced into exile by the Nazis (who exhibited his work "
            "in the Entartete Kunst show of 1937).  His triptych format -- borrowed "
            "from the polyptych altarpiece -- transforms secular narratives (circus, "
            "mythological allegory, departure and temptation) into quasi-liturgical "
            "moral confrontations.  Key technical features: (1) Black armature: "
            "heavy contour lines enclose every form, deriving from drawing rather "
            "than the brush; (2) Flat compressed space: no atmospheric recession, "
            "mid-values dominate, extremes are rare; (3) Non-naturalistic palette: "
            "salmon, acid green, cold blue-violet, brick red -- psychologically "
            "charged rather than descriptive; (4) Thick, declarative paint surface: "
            "no sfumato, no glazed transitions -- paint is applied with conviction "
            "and left visible; (5) Narrative density: single canvases contain "
            "multiple figures in overlapping states of action, allegorical props "
            "(fish, candles, masks, ropes) encoded with personal symbolism."
        ),
        famous_works=[
            ("Departure (triptych)",                     "1932-1935"),
            ("The Night",                                "1918-1919"),
            ("The Actors (triptych)",                    "1941-1942"),
            ("Begin the Beguine (triptych)",             "1946-1950"),
            ("Self-Portrait in Tuxedo",                  "1927"),
            ("Carnival",                                 "1920"),
            ("The Dream",                                "1921"),
            ("Double Portrait: Carnival",                "1925"),
        ],
        inspiration=(
            "beckmann_black_armature_pass(): ONE HUNDRED AND FIFTY-FIFTH "
            "distinct mode -- three-stage black armature expressionist simulation -- "
            "(1) GRADIENT-THRESHOLD SATURATION-STRIPPING SNAP TO BLACK: detect "
            "high-gradient edge pixels via normalised Sobel magnitude; where gradient "
            "exceeds armature_thresh, simultaneously strip saturation and snap value "
            "toward black proportional to (grad_norm-thresh)/(1-thresh)*armature_snap "
            "-- FIRST pass to combine saturation removal with value snap at form "
            "boundaries, producing the fully desaturated black armature lines "
            "characteristic of Beckmann\'s drawn contour; prior contour passes darken "
            "multiplicatively without saturation removal; "
            "(2) BIDIRECTIONAL VALUE RANGE COMPRESSION TOWARD MIDTONE: compress entire "
            "tonal range symmetrically toward compress_mid anchor -- V\'=mid+(V-mid)*(1-str) "
            "-- both shadows lift and highlights lower toward the mid-grey zone, producing "
            "the airless, claustrophobic tonal flatness of Beckmann\'s interiors -- "
            "FIRST pass to contract tonal extremes simultaneously toward a single "
            "configurable midtone anchor; "
            "(3) BECKMANN PALETTE ATTRACTION WITH PROPORTIONAL ANGULAR SNAP: five hue "
            "poles (salmon 15, acid yellow-green 80, deep teal 175, cold blue-violet 220, "
            "brick red 350); per-pixel hue moves palette_str fraction of the angular gap "
            "to the nearest in-radius pole -- proportional snap rather than fixed rotation "
            "magnitude -- FIRST pass to apply a proportional-distance angular fraction "
            "hue snap creating sudden non-naturalistic hue jumps.  Best for figure work, "
            "interior scenes, psychological portraits."
        ),
    ),
'''

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'max_beckmann' not in content, 'Max Beckmann entry already exists!'

insert_before = '\n}\n\n\ndef get_style'
assert insert_before in content, 'Insertion marker not found!'

content = content.replace(insert_before, '\n' + BECKMANN_ENTRY + '}\n\n\ndef get_style', 1)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. art_catalog.py new length: {len(content)} chars')

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'art_catalog' in mod:
        del _sys.modules[mod]
import art_catalog
assert 'max_beckmann' in art_catalog.CATALOG, 'max_beckmann missing from CATALOG'
entry = art_catalog.CATALOG['max_beckmann']
assert entry.artist == 'Max Beckmann', f'artist mismatch: {entry.artist!r}'
print(f'Verified: max_beckmann in CATALOG. Total artists: {len(art_catalog.CATALOG)}')
