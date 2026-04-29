"""Insert nicolas_de_stael entry into art_catalog.py (session 248)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

DE_STAEL_ENTRY = '''    "nicolas_de_stael": ArtStyle(
        artist="Nicolas de Stael",
        movement="Abstract Expressionism / Lyrical Abstraction",
        nationality="Russian-French",
        period="1914-1955",
        palette=[
            (0.84, 0.42, 0.18),   # burnt sienna-orange (hull colour, sunset band)
            (0.18, 0.32, 0.72),   # cobalt blue (sky, water depth, hull)
            (0.78, 0.68, 0.28),   # raw ochre-yellow (stone, sand, boat hull)
            (0.54, 0.24, 0.16),   # brick red (boat hull, rooftop)
            (0.32, 0.46, 0.56),   # slate blue-grey (water, shadow, weathered hull)
            (0.92, 0.86, 0.74),   # pale cream (sky upper, superstructure, sun)
            (0.62, 0.32, 0.10),   # deep terra cotta (harbour wall, shadow ground)
            (0.24, 0.38, 0.28),   # dark sea green (water shadow, deep harbour)
            (0.88, 0.62, 0.22),   # amber gold (dusk light, water reflection)
            (0.14, 0.18, 0.32),   # near-black navy (boat shadow, night water)
        ],
        ground_color=(0.84, 0.56, 0.22),
        stroke_size=18,
        wet_blend=0.18,
        edge_softness=0.08,
        jitter=0.06,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Nicolas de Stael (1914-1955) was born in Saint Petersburg to an "
            "aristocratic Russian family, fled the Bolshevik Revolution as a "
            "child, was orphaned in Poland at six, spent his youth in Brussels "
            "and studied at the Academie Royale des Beaux-Arts, then crossed "
            "through Morocco, Spain, and Italy before settling in Paris and later "
            "Provence. His entire painting life lasted barely fifteen years, yet "
            "he produced approximately a thousand works and achieved, in the last "
            "five years of his life, a transition so complete and so rapid that it "
            "constitutes one of the more dramatic evolutions in post-war European "
            "painting. He began as a rigorous, near-monochromatic abstractionist "
            "working in thick impasto planes, moved through his middle period of "
            "radical mosaic-like rectangular colour blocks at the height of his "
            "reputation (1950-1952), and in his last two years (1953-1955) turned "
            "to explicit Mediterranean figuration -- boats, beaches, concerts, "
            "still lifes, nudes -- in which the abstract colour-block sensibility "
            "had been absorbed into a simplified figurative language of "
            "extraordinary directness. He killed himself in Antibes in March "
            "1955, aged forty, leaving on his easel a monumental unfinished "
            "canvas of a concert at the Palais du Chaillot. "
            "His technical signature: (1) PALETTE KNIFE COLOUR BLOCKS -- de "
            "Stael's primary tool was the palette knife, not the brush; paint was "
            "applied in thick rectangular deposits, each block carrying a single "
            "dominant colour; adjacent blocks are different colours, creating a "
            "mosaic of flat planes; the knife lifts between deposits, leaving a "
            "slight gap or trough at each boundary; (2) INTRA-BLOCK DIRECTIONALITY "
            "-- within each colour block the knife drag is visible as a slight "
            "directional modulation: one edge of the block is slightly lighter "
            "where the knife arrived with full paint load, the opposite edge "
            "slightly darker where the knife lifted and left less pigment; "
            "(3) PLANAR SIMPLIFICATION -- unlike the layered, veiled chromatic "
            "complexity of Venetian glazing, de Stael works in a single direct "
            "decisive application; each block is what it is; there is no "
            "underpainting showing through; the colour is fully opaque and "
            "saturated; (4) RICH MEDITERRANEAN PALETTE -- after moving to "
            "Provence and the south of France, his palette moved from the dark "
            "earth tones of his early Paris period to intense, high-key "
            "Mediterranean colours: cobalt blue, burnt orange, raw ochre, brick "
            "red, sea green, amber gold, the blue-grey of Mediterranean shadow; "
            "(5) BOUNDARY DARKNESS -- the slight gap between adjacent knife "
            "deposits creates a thin dark line at every block boundary, giving "
            "the mosaic a structured, almost architectural grid quality even when "
            "the colour blocks themselves are irregular in shape."
        ),
        famous_works=[
            ("The Footballers",                              "1952"),
            ("Agrigento",                                    "1953"),
            ("Boats (Les Barques)",                          "1954"),
            ("Rooftops",                                     "1952"),
            ("Still Life with Candlestick",                  "1955"),
            ("The Concert (unfinished)",                     "1955"),
            ("Landscape, Honfleur",                          "1952"),
            ("Marathon (Abstract Composition)",              "1948"),
        ],
        inspiration=(
            "de_stael_palette_knife_mosaic_pass(): ONE HUNDRED AND FIFTY-NINTH "
            "distinct mode -- three-stage palette knife mosaic -- "
            "(1) RECTANGULAR TILE MEAN QUANTIZATION: divide canvas into "
            "non-overlapping tiles of (tile_h x tile_w) pixels; for each tile "
            "compute mean R, G, B across all tile pixels; replace tile pixels "
            "with this mean; first pass to apply rectangular spatial mean pooling "
            "as a primary colour stage (no prior pass uses tile mean quantization); "
            "(2) INTRA-TILE DIRECTIONAL KNIFE GRADIENT: build a (tile_h x tile_w) "
            "directional gradient template at knife_angle_deg; tile it across the "
            "full canvas; add the result * knife_texture_str to all channels; "
            "first pass to add a tiled parametric directional ramp within "
            "quantized colour blocks; (3) TILE BOUNDARY GAP DARKENING: compute "
            "per-pixel distance to nearest tile boundary (horizontal or vertical); "
            "apply boundary_strength darkening proportional to boundary proximity; "
            "first pass to darken pixels specifically by their distance to "
            "quantization tile boundaries. Best for subjects with bold geometric "
            "colour areas: harbour scenes, boats, rooftops, landscapes, footballers."
        ),
    ),
'''

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'nicolas_de_stael' not in content, 'nicolas_de_stael entry already exists!'

insert_before = '\n}\n\n\ndef get_style'
assert insert_before in content, 'Insertion marker not found!'

content = content.replace(insert_before, '\n' + DE_STAEL_ENTRY + '}\n\n\ndef get_style', 1)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. art_catalog.py new length: {len(content)} chars')

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'art_catalog' in mod:
        del _sys.modules[mod]
import art_catalog
assert 'nicolas_de_stael' in art_catalog.CATALOG, 'nicolas_de_stael missing from CATALOG'
entry = art_catalog.CATALOG['nicolas_de_stael']
assert entry.artist == 'Nicolas de Stael', f'artist mismatch: {entry.artist!r}'
print(f'Verified: nicolas_de_stael in CATALOG. Total artists: {len(art_catalog.CATALOG)}')
