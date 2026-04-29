"""Insert alexej_von_jawlensky entry into art_catalog.py (session 245)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

JAWLENSKY_ENTRY = '''    "alexej_von_jawlensky": ArtStyle(
        artist="Alexej von Jawlensky",
        movement="Russian-German Expressionism / Der Blaue Reiter",
        nationality="Russian-German",
        period="1864-1941",
        palette=[
            (0.88, 0.62, 0.14),   # hot amber-saffron (Jawlensky face centre)
            (0.86, 0.36, 0.12),   # deep orange (mid-face warmth)
            (0.72, 0.18, 0.44),   # rose-violet (cheeks / brow warmth)
            (0.14, 0.24, 0.68),   # deep cobalt blue (cool outer zones)
            (0.26, 0.50, 0.18),   # acid olive green (peripheral accent)
            (0.08, 0.10, 0.38),   # near-ultramarine dark (thick contour lines)
            (0.94, 0.90, 0.82),   # warm ivory white (inner light highlight)
            (0.36, 0.14, 0.54),   # deep violet (outer shadow field)
        ],
        ground_color=(0.16, 0.14, 0.10),
        stroke_size=10,
        wet_blend=0.20,
        edge_softness=0.08,
        jitter=0.10,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Alexej von Jawlensky (1864-1941) arrived at painting late -- he served "
            "as an officer in the Russian Imperial Army until 1896 -- but his "
            "development accelerated with startling intensity.  Born in Torzhok, "
            "Russia, he trained under Ilya Repin in St. Petersburg before moving to "
            "Munich, where he encountered Kandinsky and co-founded the Neue "
            "Kunstlervereinigung Munchen (1909), a precursor to Der Blaue Reiter.  "
            "Two profound formative influences defined his mature work: (1) the flat, "
            "radiant colour fields and hieratic frontality of Russian Orthodox icons "
            "and Byzantine mosaics -- he absorbed their sense of the image as sacred "
            "presence rather than illusionistic window; and (2) the intensified "
            "colour and simplified form of Matisse and the Fauves, encountered during "
            "a 1905 Paris visit.  From these sources Jawlensky forged a lifelong "
            "project: the reduction of the human face to its essential spiritual "
            "architecture.  His early Expressionist heads retain some individual "
            "identity; after 1917, with the \"Variations\" and \"Meditations\" series, "
            "the face dissolves into pure radiant geometry -- a large central oval of "
            "warm amber or saffron for the forehead and cheeks, flanked by cool "
            "blue-violet or deep green for the shadows and hair, and unified by a "
            "thick, heavy contour line in near-ultramarine black that simultaneously "
            "bounds form and declares the drawn structure beneath the paint.  "
            "Jawlensky\'s most important technical innovation is the RADIAL WARMTH "
            "GRADIENT: the inner zones of the face are always hot -- amber, saffron, "
            "rose -- while the outer zones cool into blue-violet, deep green, or "
            "indigo.  This is not naturalistic modelling from a light source; it is "
            "the externalisation of inner spiritual heat.  The face radiates warmth "
            "from its centre outward, like a lamp whose light grows cooler toward the "
            "edges of its aura.  Key technical features: (1) Radial warm-to-cool "
            "gradient from image centre to periphery -- inner warmth as spiritual "
            "metaphor; (2) Thick near-ultramarine contour lines (not pure black -- "
            "the outlines carry chromatic blue, distinguishing them from Beckmann\'s "
            "achromatic armature); (3) Simplified, iconic frontality -- forms reduced "
            "to essential planar masses; (4) High impasto surface with visible "
            "directional brush loading in the inner warm zones; (5) Byzantine/icon "
            "influence: the image as devotional object, the face as spiritual portal "
            "rather than psychological portrait.  By 1934, severe arthritis had "
            "reduced his hand to a near-claw; he began painting miniature \"Meditations\" "
            "-- tiny works no larger than a postcard -- holding the brush in his fist.  "
            "He completed over 1,200 of these small masterpieces before his death, "
            "each a concentrated statement of the radiant face as spiritual form."
        ),
        famous_works=[
            ("Mystical Head: Galka",                     "1917"),
            ("Abstract Head: Blue Light",                "1926"),
            ("Abstract Head: Inner Vision",              "1926"),
            ("Saviour\'s Face",                           "1918"),
            ("Abstract Head: Rose and Orange",           "1925"),
            ("The Red Shawl",                            "1909"),
            ("Meditation",                               "1937"),
            ("Head: Yellow-Orange",                      "1928"),
        ],
        inspiration=(
            "jawlensky_abstract_head_pass(): ONE HUNDRED AND FIFTY-SIXTH "
            "distinct mode -- three-stage iconic radial warmth simulation -- "
            "(1) RADIAL WARMTH GRADIENT: compute normalised radial distance from "
            "image centroid; inner zone (dist < inner_radius) receives warm hue "
            "attraction toward amber/saffron anchor (warm_hue~35 deg) weighted by "
            "(1-dist/inner_radius)*warmth_str; this externalises Jawlensky\'s inner "
            "spiritual heat as radial center-to-periphery warmth -- FIRST pass to "
            "apply inward-warm/outward-cool hue shift weighted by normalised radial "
            "distance from the image centroid; prior passes apply uniform warm tints "
            "(imprimatura), directional DoG tints (aerial perspective), or edge-based "
            "snaps (Beckmann armature) -- none use a centre-to-periphery radial "
            "weight as the primary driver of hue shift; "
            "(2) COOL PERIPHERAL PUSH: outer zone (dist > outer_radius) receives hue "
            "attraction toward blue-violet anchor (cool_hue~230 deg) weighted by "
            "(dist-outer_radius)/(1-outer_radius+eps)*cool_str, with simultaneous "
            "saturation boost and value lift in outer zones -- FIRST pass to apply "
            "cool-hue shift + saturation boost + value lift together in the image "
            "periphery only; prior passes apply these operations globally or by "
            "edge-proximity, not by radial distance from centroid; "
            "(3) ULTRAMARINE EDGE TINT: detect high-gradient edges via Sobel; blend "
            "edge pixels toward deep ultramarine-dark (blue_r~0.08, blue_g~0.10, "
            "blue_b~0.38) rather than pure black -- FIRST pass to apply a "
            "chromatically blue (not achromatic) edge darkening at gradient boundaries; "
            "Beckmann snaps to desaturated black; Kirchner darkens multiplicatively "
            "without saturation removal; this produces the distinctively blue-tinted "
            "thick contour lines of Jawlensky\'s Abstract Heads.  Best for portraiture, "
            "frontal faces, and spiritual/devotional subject matter."
        ),
    ),
'''

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'alexej_von_jawlensky' not in content, 'Alexej von Jawlensky entry already exists!'

insert_before = '\n}\n\n\ndef get_style'
assert insert_before in content, 'Insertion marker not found!'

content = content.replace(insert_before, '\n' + JAWLENSKY_ENTRY + '}\n\n\ndef get_style', 1)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. art_catalog.py new length: {len(content)} chars')

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'art_catalog' in mod:
        del _sys.modules[mod]
import art_catalog
assert 'alexej_von_jawlensky' in art_catalog.CATALOG, 'alexej_von_jawlensky missing from CATALOG'
entry = art_catalog.CATALOG['alexej_von_jawlensky']
assert entry.artist == 'Alexej von Jawlensky', f'artist mismatch: {entry.artist!r}'
print(f'Verified: alexej_von_jawlensky in CATALOG. Total artists: {len(art_catalog.CATALOG)}')
