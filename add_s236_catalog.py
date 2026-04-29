"""Insert frantisek_kupka entry into art_catalog.py (session 236)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

KUPKA_ENTRY = '''    "frantisek_kupka": ArtStyle(
        artist="Frantisek Kupka",
        movement="Orphism, Abstract Art",
        nationality="Czech-French",
        period="1871–1957",
        palette=[
            (0.04, 0.18, 0.62),   # prussian blue
            (0.88, 0.10, 0.08),   # cadmium red
            (0.96, 0.84, 0.04),   # chrome yellow
            (0.04, 0.56, 0.26),   # emerald green
            (0.14, 0.44, 0.78),   # cerulean
            (0.72, 0.08, 0.54),   # magenta-violet
            (0.94, 0.90, 0.82),   # ivory white
            (0.06, 0.06, 0.10),   # near-black
        ],
        ground_color=(0.08, 0.08, 0.14),
        stroke_size=5.5,
        wet_blend=0.48,
        edge_softness=0.20,
        jitter=0.04,
        glazing=(0.02, 0.04, 0.10),
        crackle=False,
        chromatic_split=False,
        technique=(
            "Kupka was the first artist to exhibit a purely non-representational "
            "painting ('Amorpha: Fugue in Two Colors', 1912), predating Delaunay "
            "and Mondrian.  His 'Orphic' technique centres on the musical analogy: "
            "colour is to painting what sound is to music -- a purely abstract force "
            "with its own rhythm, structure, and emotional power.  He organises colour "
            "into concentric fugal rings radiating from a luminous focus: warm hues "
            "(reds, oranges) transition through cool (blues, greens) and back in "
            "repeating cycles, like a canon or fugue in musical counterpoint.  In the "
            "'Vertical Planes' series (1913) pure colour planes stack like organ pipes, "
            "each plane a pure unmixed hue at full saturation -- no white mixtures, no "
            "grey transitions.  He applies paint in flat, even layers within each colour "
            "zone, achieving maximum chromatic intensity by avoiding any blending that "
            "would dilute the hue.  His palette is drawn directly from the spectral "
            "sequence: primary red, yellow, blue, then their spectral intermediates -- "
            "no earth pigments, no neutrals.  The ground is near-black so all colour "
            "reads against an absorptive field, increasing apparent saturation."
        ),
        famous_works=[
            ("Amorpha: Fugue in Two Colors", "1912"),
            ("Vertical Planes in Blue and Red", "1913"),
            ("Around a Point", "1911"),
            ("Disks of Newton", "1912"),
            ("The First Step", "1910"),
            ("Philosophical Architecture", "1913"),
            ("Creation", "1920"),
        ],
        inspiration=(
            "kupka_orphic_fugue_pass(): two-stage orphic transformation -- "
            "(1) radial hue fugue: luminance-weighted centroid anchors a sinusoidal "
            "hue rotation field; delta_H = amplitude * sin(2pi * r / period); "
            "FIRST pass to rotate HSV hue as primary operation, creating Kupka\\'s "
            "concentric colour-ring fugue from one luminous focus; "
            "(2) chromatic intensity surge: bell-curve saturation boost at V=0.52 "
            "drives mid-tones to full spectral intensity.  Use ground_color=(0.08, "
            "0.08, 0.14) (near-black ground).  Best for figurative or landscape "
            "subjects with a strong luminous focal point (light source, face, moon) "
            "that the concentric hue rings can orbit."
        ),
    ),
'''

INSERT_BEFORE = '}\n\n\ndef get_style'

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'frantisek_kupka' not in content, 'Kupka already in catalog!'
assert INSERT_BEFORE in content, f'Anchor not found in art_catalog.py'

content = content.replace(INSERT_BEFORE, KUPKA_ENTRY + INSERT_BEFORE)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. Kupka entry inserted into art_catalog.py')

# Verify
import importlib, sys
for mod in ['art_catalog']:
    if mod in sys.modules:
        del sys.modules[mod]
import art_catalog
s = art_catalog.CATALOG['frantisek_kupka']
print(f'Verified: {s.artist} ({s.movement}) | {len(art_catalog.CATALOG)} total artists')
