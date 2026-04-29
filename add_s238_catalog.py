"""Insert lyonel_feininger entry into art_catalog.py (session 238)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

FEININGER_ENTRY = '''    "lyonel_feininger": ArtStyle(
        artist="Lyonel Feininger",
        movement="Expressionism, Cubism, Bauhaus",
        nationality="American-German",
        period="1871-1956",
        palette=[
            (0.14, 0.20, 0.42),   # prussian cobalt blue
            (0.72, 0.56, 0.22),   # amber ochre gold
            (0.38, 0.44, 0.52),   # slate grey-blue
            (0.58, 0.50, 0.68),   # dusty lavender-violet
            (0.82, 0.80, 0.72),   # ivory cream
            (0.16, 0.16, 0.18),   # near-black architectural line
            (0.44, 0.58, 0.48),   # muted sage green
            (0.72, 0.38, 0.18),   # warm terracotta orange
        ],
        ground_color=(0.62, 0.64, 0.70),
        stroke_size=5.0,
        wet_blend=0.40,
        edge_softness=0.20,
        jitter=0.04,
        glazing=(0.12, 0.16, 0.28),
        crackle=False,
        chromatic_split=False,
        technique=(
            "Lyonel Feininger spent his formative years as a caricaturist before "
            "encountering Cubism in Paris in 1906-07, and the meeting transformed "
            "his practice permanently.  His mature paintings are built from "
            "overlapping, interlocking wedges and prisms of atmospheric colour -- "
            "the visual logic of a crystal examined under directional light.  Each "
            "angular plane carries its own tonal and chromatic identity: one face "
            "of a church spire in cool cobalt shadow, the adjacent face in warm "
            "amber light, the transition across the edge sharp and decisive.  His "
            "architectural subjects -- the Gothic churches of Thuringia, especially "
            "the series of eleven Gelmeroda paintings (1913-1936) -- are dissolved "
            "into these geometric planes while retaining their monumental vertical "
            "energy.  His coastal and marine paintings apply the same prismatic "
            "logic to water, sky, and sail: the surface of the sea fractures into "
            "geometric tiles of reflected light, each tile a slightly different hue "
            "and luminance.  The palette is consistently atmospheric: prussian "
            "cobalt, slate violet, amber ochre, sage green, and ivory -- cool "
            "dominates, with warm amber used sparingly as accent.  Feininger\'s "
            "line is structural, not decorative: sharp diagonals define the crystal "
            "faces; the composition is organised by vectors of directional force "
            "rather than by tonal mass.  He was a founding master at the Bauhaus "
            "where his influence on twentieth-century design education was profound."
        ),
        famous_works=[
            ("Gelmeroda IV", "1915"),
            ("Gelmeroda VIII", "1921"),
            ("The Steamer Odin II", "1927"),
            ("Street in Paris", "1909"),
            ("Sailing Boats", "1929"),
            ("The Cathedral", "1919"),
            ("Side-Wheeler", "1913"),
            ("Village Church", "1931"),
        ],
        inspiration=(
            "feininger_crystalline_prism_pass(): two-stage crystalline facet "
            "simulation -- "
            "(1) Coherent angle map via circular Gaussian averaging: sx=sobel(lum,1); "
            "sy=sobel(lum,0); angle=atan2(sy,sx); z_cos=gaussian(cos(angle),sigma); "
            "z_sin=gaussian(sin(angle),sigma); coherent_angle=atan2(z_sin,z_cos) -- "
            "FIRST pass in project to use gradient DIRECTION (not magnitude) as "
            "primary variable; FIRST circular/angular spatial average; "
            "(2) Prismatic warm/cool chromatic mapping: warm_cool=cos(angle*cycles); "
            "R+=warm_cool*ct*0.78, G+=*0.28, B-=*0.92 -- warm crystal faces get "
            "amber tilt; cool faces get cobalt tilt; FIRST direction-angle cyclic "
            "chromatic modulation.  Use misty slate ground "
            "(0.62, 0.64, 0.70).  Best for architectural subjects (spires, "
            "masts, angular forms), coastal/marine scenes with geometric water "
            "facets, and compositions with strong diagonal angular structure.  "
            "Combine with paint_split_toning_pass for reinforced temperature contrast."
        ),
    ),
'''

INSERT_BEFORE = '}\n\n\ndef get_style'

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'lyonel_feininger' not in content, 'Feininger already in catalog!'
assert INSERT_BEFORE in content, f'Anchor not found in art_catalog.py'

content = content.replace(INSERT_BEFORE, FEININGER_ENTRY + INSERT_BEFORE)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. Feininger entry inserted into art_catalog.py')

import importlib, sys
for mod in ['art_catalog']:
    if mod in sys.modules:
        del sys.modules[mod]
import art_catalog
s = art_catalog.CATALOG['lyonel_feininger']
print(f'Verified: {s.artist} ({s.movement}) | {len(art_catalog.CATALOG)} total artists')
