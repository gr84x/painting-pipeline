"""Insert georges_rouault entry into art_catalog.py (session 237)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

ROUAULT_ENTRY = '''    "georges_rouault": ArtStyle(
        artist="Georges Rouault",
        movement="Expressionism, Fauvism",
        nationality="French",
        period="1871-1958",
        palette=[
            (0.06, 0.04, 0.06),   # near-black contour
            (0.72, 0.08, 0.10),   # deep crimson
            (0.10, 0.18, 0.62),   # cobalt blue
            (0.08, 0.42, 0.18),   # emerald green
            (0.82, 0.54, 0.08),   # amber ochre
            (0.46, 0.08, 0.22),   # burgundy
            (0.90, 0.86, 0.74),   # ivory bone
            (0.84, 0.32, 0.08),   # cadmium orange
        ],
        ground_color=(0.08, 0.06, 0.08),
        stroke_size=6.0,
        wet_blend=0.52,
        edge_softness=0.15,
        jitter=0.05,
        glazing=(0.06, 0.04, 0.08),
        crackle=False,
        chromatic_split=False,
        technique=(
            "Rouault apprenticed as a stained-glass maker before training under "
            "Gustave Moreau at the Ecole des Beaux-Arts, and the lead-camed window "
            "never left his imagination.  His canvases are built on the same "
            "structural logic as medieval glass: thick, vigorously impastoed dark "
            "contour lines -- sometimes applied with a palette knife -- divide the "
            "composition into closed zones of jewel-like saturated colour.  Deep "
            "crimson, cobalt blue, emerald green, and amber ochre sit inside the "
            "lead lines at maximum intensity; the black borders amplify each "
            "colour\'s apparent luminosity by contrast.  His subjects were drawn "
            "from the moral margins: clowns with lined faces, corrupt judges, "
            "prostitutes, and above all the suffering Christ -- all rendered with "
            "a savage compassion that made his religious canvases among the most "
            "spiritually forceful of the twentieth century.  The Miserere "
            "series (1922-1927, published 1948) extended the stained-glass idiom "
            "into aquatint: heavy blacks around anguished figures, occasional "
            "tonal whites for sacred light.  His surfaces are deliberately rough "
            "and unresolved at close range; the stained-glass unity only appears "
            "at the viewing distance of a cathedral nave.  Ground is near-black "
            "so that contour zones read as absolute darkness against the jeweled "
            "interior colour."
        ),
        famous_works=[
            ("The Three Judges", "1913"),
            ("Christ Mocked by Soldiers", "1932"),
            ("Miserere (series)", "1922-1948"),
            ("The Old Clown", "1917"),
            ("Prostitute Before a Mirror", "1906"),
            ("Circus Trio", "1924"),
            ("The Holy Face", "1946"),
        ],
        inspiration=(
            "rouault_stained_glass_pass(): three-stage stained-glass simulation -- "
            "(1) Sobel gradient magnitude detects colour-zone boundaries; contour_gate "
            "= clip(grad_norm/contour_thresh)^contour_power drives high-gradient "
            "pixels toward near-black (lead line darkening) -- FIRST pass to use a "
            "derivative/gradient operator as its primary tool; "
            "(2) Lead-line cool tint: at maximum contour, push blue (B+lead_cool), "
            "drain red and green (R-, G-), shifting the darkened boundary toward "
            "the blue-grey of raw lead came; "
            "(3) Interior jewel saturation: interior_gate=1-contour_gate; "
            "ch=lum+(ch-lum)*(1+jewel_boost*interior_gate) pumps colour saturation "
            "in enclosed low-gradient zones, simulating Rouault\'s jewel-tone "
            "interior fills.  Use near-black ground (0.08, 0.06, 0.08).  Best for "
            "figurative subjects with strong tonal contrast (clowns, religious "
            "figures, animals against sky), bold colour zones, and compositions "
            "that benefit from a stained-glass gravity of outline."
        ),
    ),
'''

INSERT_BEFORE = '}\n\n\ndef get_style'

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'georges_rouault' not in content, 'Rouault already in catalog!'
assert INSERT_BEFORE in content, f'Anchor not found in art_catalog.py'

content = content.replace(INSERT_BEFORE, ROUAULT_ENTRY + INSERT_BEFORE)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. Rouault entry inserted into art_catalog.py')

import importlib, sys
for mod in ['art_catalog']:
    if mod in sys.modules:
        del sys.modules[mod]
import art_catalog
s = art_catalog.CATALOG['georges_rouault']
print(f'Verified: {s.artist} ({s.movement}) | {len(art_catalog.CATALOG)} total artists')
