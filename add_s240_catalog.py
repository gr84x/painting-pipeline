"""Insert raoul_dufy entry into art_catalog.py (session 240)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

DUFY_ENTRY = '''    "raoul_dufy": ArtStyle(
        artist="Raoul Dufy",
        movement="Fauvism / Post-Impressionism",
        nationality="French",
        period="1877-1953",
        palette=[
            (0.14, 0.42, 0.78),   # clear cerulean blue — sky and Mediterranean sea
            (0.88, 0.82, 0.38),   # warm Naples yellow — sunlit ground and sails
            (0.88, 0.32, 0.24),   # vermillion-red — regatta pennants and hulls
            (0.18, 0.60, 0.44),   # viridian green — palm foliage and waterline
            (0.96, 0.96, 0.94),   # near-white — sails and sunlit surf foam
            (0.62, 0.24, 0.64),   # violet — shadow cast on the promenade
            (0.14, 0.28, 0.56),   # deep cobalt — sea shadow and sky depth
            (0.96, 0.72, 0.28),   # gold-ochre — sunlit beach sand and awnings
        ],
        ground_color=(0.92, 0.92, 0.90),
        stroke_size=5,
        wet_blend=0.18,
        edge_softness=0.28,
        jitter=0.06,
        glazing=(0.14, 0.52, 0.82),
        crackle=False,
        chromatic_split=True,
        technique=(
            "Raoul Dufy (1877-1953) developed his signature technique through a "
            "decisive discovery made around 1905-1908: colour and line could be "
            "liberated from each other and applied as entirely independent systems "
            "on the same canvas.  Where traditional painting subordinates colour "
            "to drawing -- filling the drawn forms with the appropriate tint -- "
            "Dufy separates them entirely.  His outlines (drawn rapidly in ink, "
            "watercolour, or loaded brush, sometimes in black or dark blue) are "
            "laid first or last as spontaneous calligraphic marks; the colour "
            "washes are applied in broad, flat, luminous areas that deliberately "
            "exceed or mis-register against those outlines.  A sail may be drawn "
            "in rapid strokes while the blue of the sea bleeds across it from "
            "the adjacent wash; a race-horse\'s silhouette in ink floats over a "
            "yellow-green field wash that pays no attention to the drawn boundary.  "
            "The visual result is a sense of joyous spontaneity and light -- as if "
            "the colour is sunlight itself, too diffuse and vital to stay within "
            "drawn lines.  His palette is consistently festive and high-keyed: "
            "cerulean, cobalt, vermillion, Naples yellow, viridian, and white -- "
            "the palette of the Mediterranean, of regattas at Cowes and Deauville, "
            "of the Promenade des Anglais in full summer sun.  He worked extensively "
            "in watercolour and gouache as well as oil, and his handling of all three "
            "retains the same loose, luminous quality.  His famous large decorative "
            "works -- La Fee Electricite (1937) and the Palais de Chaillot murals -- "
            "carry this technique to monumental scale.  His subjects are celebrations "
            "of modern leisure: yachts under spinnakers, racehorses at the paddock, "
            "Nice in July, orchestras mid-performance, motor races and garden parties."
        ),
        famous_works=[
            ("The Regatta at Cowes",              "1934"),
            ("Nice - La Baie des Anges",          "1929"),
            ("La Fee Electricite",                "1937"),
            ("Paddock at Epsom",                  "1930"),
            ("Homage to Mozart",                  "1915"),
            ("The Seine at Chatou",               "1905"),
            ("Deauville, the Paddock",            "1935"),
            ("Open Window, Nice",                 "1928"),
        ],
        inspiration=(
            "dufy_chromatic_dissociation_pass(): ONE HUNDRED AND FIFTY-FIRST distinct mode -- "
            "three-stage chromatic dissociation simulation -- "
            "(1) OUTLINE EXTRACTION AND DARKENING: Sobel magnitude smoothed with Gaussian "
            "sigma; edge_gate = clip(mag_norm/threshold, 0,1)^0.6; "
            "ch = ch*(1-edge_gate*darkness) -- FIRST pass to model ink-outline occlusion: "
            "edge zone pushed toward near-black independently (not merely contrast-sharpened); "
            "(2) CHROMINANCE SPATIAL DISSOCIATION: cb_ch = ch - lum; "
            "cb_ch_shifted = roll(cb_ch, (dy, dx)); ch_dissociated = clip(lum + cb_ch_shifted, 0, 1) -- "
            "FIRST pass to spatially translate chrominance independently of luminance, "
            "producing intentional colour-line mis-registration; "
            "(3) FAUVIST SATURATION LIFT: sat_scale = 1 + saturation_lift; "
            "ch_vivid = lum + (ch - lum)*sat_scale -- vivid transparent watercolour quality.  "
            "Use near-white ground (0.92, 0.92, 0.90).  "
            "Best for festive, light-filled subjects: regattas, racetracks, Mediterranean "
            "promenades, concert halls.  Combine with paint_sfumato_focus_pass to draw "
            "the eye to the primary subject while periphery softens."
        ),
    ),
'''

INSERT_BEFORE = '}\n\n\ndef get_style'

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'raoul_dufy' not in content, 'Raoul Dufy already in catalog!'
assert INSERT_BEFORE in content, f'Anchor not found in art_catalog.py'

content = content.replace(INSERT_BEFORE, DUFY_ENTRY + INSERT_BEFORE)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. Raoul Dufy entry inserted into art_catalog.py')

import importlib
for mod in list(sys.modules.keys()):
    if 'art_catalog' in mod:
        del sys.modules[mod]
import art_catalog
s = art_catalog.CATALOG['raoul_dufy']
print(f'Verified: {s.artist} ({s.movement}) | {len(art_catalog.CATALOG)} total artists')
