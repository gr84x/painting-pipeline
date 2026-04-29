"""Insert paul_signac entry into art_catalog.py (session 242)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

SIGNAC_ENTRY = '''    "paul_signac": ArtStyle(
        artist="Paul Signac",
        movement="Neo-Impressionism / Divisionism",
        nationality="French",
        period="1863-1935",
        palette=[
            (0.18, 0.52, 0.82),   # deep cerulean — Mediterranean harbour water
            (0.92, 0.72, 0.22),   # warm chrome yellow — sunlit sails and rigging
            (0.28, 0.68, 0.52),   # sea green — shallow harbour shallows
            (0.80, 0.34, 0.18),   # vivid vermilion-orange — complementary to blue
            (0.64, 0.22, 0.62),   # violet-magenta — shadow complement to yellow
            (0.88, 0.92, 0.96),   # cool white — sky light and water shimmer
            (0.94, 0.88, 0.32),   # lemon yellow — sun glare on wave crests
            (0.34, 0.24, 0.70),   # deep violet — deep water shadow
        ],
        ground_color=(0.96, 0.96, 0.92),
        stroke_size=6,
        wet_blend=0.08,
        edge_softness=0.12,
        jitter=0.08,
        glazing=(0.18, 0.52, 0.82),
        crackle=False,
        chromatic_split=True,
        technique=(
            "Paul Signac (1863-1935) was co-founder and leading theorist of "
            "Neo-Impressionism, evolving Georges Seurat\'s pointillism into what he "
            "termed Divisionism -- a systematic science of colour applied through "
            "distinct, directional, rectangular brushstrokes.  Unlike Seurat\'s "
            "uniform circular dots, Signac moved toward larger square or rectangular "
            "mosaic-like touches -- sometimes called confetti strokes -- each "
            "separately placed patch of pure colour contributing to an optical mixture "
            "when viewed from normal gallery distance.  He grounded his method in the "
            "colour science of Michel-Eugene Chevreul (simultaneous contrast of hues), "
            "Ogden Rood\'s modern chromatic diagrams, and Charles Henry\'s theories of "
            "emotional directional lines.  A passionate sailor, Signac painted over "
            "500 harbour and coastal scenes from Brittany to Istanbul; the Mediterranean "
            "ports of Saint-Tropez, Marseille, and Antibes are his spiritual homeland.  "
            "His palette is high-keyed and intensely saturated: deep cerulean and "
            "sea-green alongside vivid orange and violet-magenta -- complementary pairs "
            "that generate maximum vibrancy through simultaneous contrast.  He added "
            "thin blue or violet outlines to strongly lit edges to prevent halation.  "
            "His technique evolved from tight controlled mosaic in the 1890s to freer, "
            "almost gestural rectangular strokes by 1900-1920.  His major theoretical "
            "text D\'Eugene Delacroix au Neo-Impressionnisme (1899) became the canonical "
            "account of the movement and influenced Matisse, Derain, and the Fauves.  "
            "Major works span from the geometric precision of Gas Tanks at Clichy (1886) "
            "to the luminous freedom of The Port of Saint-Tropez (1905) and the jewelled "
            "mosaics of Constantinople, the Golden Horn (1907)."
        ),
        famous_works=[
            ("Gas Tanks at Clichy",                          "1886"),
            ("Junction of the Seine and Marne at Conflans", "1902"),
            ("The Port of Saint-Tropez",                    "1905"),
            ("Venice, the Green Canal",                     "1904"),
            ("Rotterdam, the Dark Quay",                    "1906"),
            ("Constantinople, the Golden Horn",             "1907"),
            ("Antibes, Afternoon Effect",                   "1914"),
            ("Le Pont des Arts",                            "1925"),
        ],
        inspiration=(
            "signac_divisionist_mosaic_pass(): ONE HUNDRED AND FIFTY-THIRD distinct mode -- "
            "three-stage divisionist mosaic simulation -- "
            "(1) PATCH QUANTIZATION: canvas subdivided into patch_size x patch_size "
            "rectangular regions; local mean colour computed for each patch by "
            "vectorised block-reshape mean pooling; the mean is broadcast back, "
            "creating flat-colour mosaic tiles -- FIRST pass to apply divisionist "
            "colour quantization via vectorised block-reshape mean pooling producing "
            "rectangular brushstroke mosaic; distinct from pointillist_pass (circular "
            "dots) and fauvist_mosaic_pass (Voronoi/random zones); "
            "(2) COMPLEMENTARY INTERLEAVING: within each patch, a tile-level "
            "checkerboard mask -- (patch_row + patch_col) % 2 -- assigns even tiles "
            "to the primary colour and odd tiles to the complementary (hue rotated "
            "180 degrees, same saturation and value); blend ratio controlled by "
            "comp_mix parameter: final = primary*(1-comp_mix) + complement*comp_mix "
            "-- FIRST pass to interleave the primary colour and its 180-degree hue "
            "complement within each quantized tile using a tile-level (not "
            "single-pixel) checkerboard; chromatic_split_pass offsets channels "
            "laterally; this pass interleaves hue-opposite tiles within the same "
            "quantized block, implementing Chevreul simultaneous contrast at the "
            "intra-patch level; "
            "(3) SIMULTANEOUS CONTRAST BOUNDARY BOOST: detect inter-patch boundaries "
            "and compute hue difference between adjacent tile means; where "
            "|delta_hue| > hue_thresh, boost saturation by "
            "sat_boost * (|delta_hue|-hue_thresh) / (180-hue_thresh) -- FIRST pass "
            "to apply Chevreul simultaneous contrast at detected opposing-hue patch "
            "boundaries, boosting saturation proportionally to how far adjacent hues "
            "are apart on the colour wheel.  Best for harbour/coastal scenes, strongly "
            "lit subjects, any composition where optical colour mixing and vibrant "
            "simultaneous contrast are desired.  Combine with place_lights() before "
            "calling for best harmonic results."
        ),
    ),
'''

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'paul_signac' not in content, 'Paul Signac entry already exists!'

insert_before = '\n}\n\n\ndef get_style'
assert insert_before in content, f'Insertion marker not found!'

content = content.replace(insert_before, '\n' + SIGNAC_ENTRY + '}\n\n\ndef get_style', 1)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. art_catalog.py new length: {len(content)} chars')

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'art_catalog' in mod:
        del _sys.modules[mod]
import art_catalog
assert 'paul_signac' in art_catalog.CATALOG, 'paul_signac missing from CATALOG'
entry = art_catalog.CATALOG['paul_signac']
assert entry.artist == 'Paul Signac', f'artist mismatch: {entry.artist!r}'
print(f'Verified: paul_signac in CATALOG. Total artists: {len(art_catalog.CATALOG)}')
