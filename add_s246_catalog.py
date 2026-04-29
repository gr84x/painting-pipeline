"""Insert august_macke entry into art_catalog.py (session 246)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

MACKE_ENTRY = '''    "august_macke": ArtStyle(
        artist="August Macke",
        movement="German Expressionism / Der Blaue Reiter",
        nationality="German",
        period="1887-1914",
        palette=[
            (0.95, 0.78, 0.20),   # cadmium yellow (Tunisian noon sun, sand)
            (0.14, 0.32, 0.76),   # cobalt blue (shadow wall, djellaba shadow)
            (0.92, 0.26, 0.10),   # vermilion-orange (hanging fabric, market goods)
            (0.28, 0.62, 0.88),   # cerulean (sky glimpse, awning stripe)
            (0.98, 0.96, 0.90),   # warm ivory-white (blazing sunlit wall)
            (0.78, 0.42, 0.22),   # terracotta-burnt sienna (architecture, jars)
            (0.72, 0.86, 0.16),   # acid yellow-green (market silk, foliage)
            (0.32, 0.14, 0.52),   # deep violet (doorway shadow, deep shade)
        ],
        ground_color=(0.82, 0.66, 0.28),
        stroke_size=12,
        wet_blend=0.18,
        edge_softness=0.10,
        jitter=0.08,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "August Macke (1887-1914) was the youngest and most lyrical "
            "member of Der Blaue Reiter, the Munich-based Expressionist circle "
            "that also included Wassily Kandinsky, Franz Marc, and Paul Klee. "
            "Where Kandinsky was theoretical and Marc was symbolic, Macke was "
            "purely sensory: his paintings are celebrations of light, colour, "
            "and the surface of the visible world -- women in hats, parks, "
            "market stalls, children at shop windows. He died at the Western "
            "Front in September 1914, aged twenty-seven, just five months after "
            "his most famous artistic journey: a two-week watercolour trip to "
            "Tunisia in April 1914 with Paul Klee and Louis Moilliet. The "
            "Tunisian works -- dozens of luminous watercolours painted at "
            "Tunis, Saint-Germain, Hammamet, and Kairouan -- are considered "
            "among the finest produced in that tradition, comparable to "
            "Delacroix\'s Moroccan voyage of 1832. The North African light "
            "unlocked the defining quality of Macke\'s mature vision: the "
            "reduction of visual experience to flat, luminous COLOUR PLANES. "
            "Unlike chiaroscuro-based painting, where form is modelled from "
            "light and shadow, Macke treats each coloured zone as a flat, "
            "semi-transparent field of maximum chromatic intensity. A shadow "
            "wall is not a darkened version of the lit wall -- it is a "
            "completely different, equally intense colour (cobalt blue or deep "
            "violet) placed in direct adjacency with the blazing warm-white of "
            "the sunlit surface. The boundary between these planes does not "
            "blend or dissolve -- it is the energetic site of the painting, "
            "where the clash of hue is the subject.  Macke\'s key technical "
            "principles: (1) COLOUR PLANE PURITY -- each zone of the picture "
            "is assigned its own hue at or near maximum saturation; the colour "
            "is not graded within the zone; (2) BOUNDARY LUMINANCE LIFT -- "
            "where two highly saturated colour planes meet, the boundary zone "
            "brightens rather than darkens; the light seems to be emitted from "
            "the interface itself, as in stained glass seen from inside a "
            "cathedral; (3) WARM GOLDEN GROUND TRANSPARENCY -- Macke works on "
            "a warm, golden-tan ground that is allowed to breathe through the "
            "paint layer, particularly in mid-values; the ground unifies the "
            "palette with a common warm undertone; lighter passages absorb "
            "more of this ground warmth than shadows, which fall into cool "
            "violet-blue; (4) JOYFUL PALETTE SYNTAX -- the colour range is "
            "always affirmative: cadmium yellow, vermilion-orange, cobalt "
            "blue, acid yellow-green, warm ivory -- never muddy, never "
            "ambiguous; Macke\'s world has the clarity of a Moroccan tile "
            "pattern seen in direct sunlight. His death at twenty-seven made "
            "his already radiant production feel, in retrospect, like a life "
            "lived at maximum chromatic intensity right up to its sudden end."
        ),
        famous_works=[
            ("Promenade",                              "1913"),
            ("Kairouan I",                             "1914"),
            ("Kairouan II",                            "1914"),
            ("Saint-Germain near Tunis",               "1914"),
            ("Turkish Café I",                         "1914"),
            ("Zoological Garden I",                    "1912"),
            ("Lady in a Green Jacket",                 "1913"),
            ("Children at the Fountain I",             "1912"),
        ],
        inspiration=(
            "macke_luminous_planes_pass(): ONE HUNDRED AND FIFTY-SEVENTH "
            "distinct mode -- three-stage luminous colour plane simulation -- "
            "(1) HUE-ZONE SATURATION NORMALISATION: divide the hue wheel into "
            "n_hue_zones equal sectors; for each sector compute the 80th-"
            "percentile saturation of pixels in that sector and lift all "
            "sector pixels toward sat_target using a per-sector scale factor "
            "derived from p80 -- first pass to apply per-hue-sector "
            "percentile-referenced saturation normalisation (prior passes "
            "boost saturation globally, at warm-cool boundaries, or radially, "
            "not per-hue-zone using zone-local percentile statistics); "
            "(2) CIRCULAR HUE GRADIENT BOUNDARY BRIGHTENING: decompose hue "
            "into sin(hue) and cos(hue), apply Sobel gradient to each "
            "component, combine magnitudes to produce a circular hue gradient "
            "map; brighten pixels at high hue-jump boundaries rather than "
            "darkening them -- first pass to detect boundaries using the "
            "circular hue gradient (not luminance gradient) and to apply "
            "brightening (not darkening) at colour-plane interfaces; "
            "(3) LUMINANCE-PROPORTIONAL WARM GOLDEN VEIL: blend each pixel "
            "toward a warm golden colour with blend weight proportional to "
            "existing pixel luminance -- brighter pixels absorb more of the "
            "warm veil, simulating warm golden ground showing through thinner "
            "paint in lit zones -- first pass to scale a warm-colour blend "
            "by current pixel luminance.  Best for joyful, saturated subjects: "
            "market scenes, figures in sun, landscape with strong colour fields."
        ),
    ),
'''

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'august_macke' not in content, 'august_macke entry already exists!'

insert_before = '\n}\n\n\ndef get_style'
assert insert_before in content, 'Insertion marker not found!'

content = content.replace(insert_before, '\n' + MACKE_ENTRY + '}\n\n\ndef get_style', 1)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. art_catalog.py new length: {len(content)} chars')

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'art_catalog' in mod:
        del _sys.modules[mod]
import art_catalog
assert 'august_macke' in art_catalog.CATALOG, 'august_macke missing from CATALOG'
entry = art_catalog.CATALOG['august_macke']
assert entry.artist == 'August Macke', f'artist mismatch: {entry.artist!r}'
print(f'Verified: august_macke in CATALOG. Total artists: {len(art_catalog.CATALOG)}')
