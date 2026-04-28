"""Insert emil_nolde entry into art_catalog.py (session 235)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

NOLDE_ENTRY = '''    "emil_nolde": ArtStyle(
        artist="Emil Nolde",
        movement="German Expressionism, Die Brücke",
        nationality="German-Danish",
        period="1867–1956",
        palette=[
            (0.72, 0.08, 0.04),   # savage crimson-red
            (0.88, 0.42, 0.04),   # incandescent orange
            (0.90, 0.78, 0.06),   # explosive chrome yellow
            (0.06, 0.22, 0.55),   # deep cobalt sea-night
            (0.12, 0.38, 0.18),   # dark northern pine-green
            (0.38, 0.08, 0.28),   # deep violet-plum shadow
            (0.92, 0.86, 0.68),   # warm bone/ash light
            (0.28, 0.12, 0.04),   # raw umber dark ground
        ],
        ground_color=(0.12, 0.06, 0.02),
        stroke_size=5.0,
        wet_blend=0.55,
        edge_softness=0.25,
        jitter=0.08,
        glazing=(0.10, 0.04, 0.02),
        crackle=False,
        chromatic_split=False,
        technique=(
            "Nolde paints with primordial colour violence: pure pigments at maximum "
            "saturation applied wet-into-wet on paper or with broad impasto on canvas, "
            "colours bleeding and fusing at boundaries into luminous incandescent zones. "
            "His shadows break academic convention -- they glow warm (orange-red earth) "
            "rather than cool blue-grey, with near-black voids surrounding the glowing "
            "colour fields like the darkness around a fire.  Mid-tones surge to full "
            "spectral intensity: no half-measures, no neutral transitions.  Saturated "
            "colour zones radiate a visible halo of warm light into surrounding passages. "
            "He favoured the North Sea coast of Schleswig-Holstein and the Jutland "
            "peninsula -- northern storms, dark sky against luminous sea-foam.  His "
            "florals are explosions of colour set against black or near-black grounds. "
            "Religious subjects receive barbaric, mask-like colour treatment: raw umber, "
            "savage crimson, bone white against darkness.  His 'unpainted pictures' "
            "(Ungemalte Bilder), created secretly during the Nazi ban on his work, show "
            "his palette at its most concentrated and explosive."
        ),
        famous_works=[
            ("Flower Garden", "1908"),
            ("Dance Around the Golden Calf", "1910"),
            ("The Sea (Nordsee)", "1913"),
            ("Large Sunflowers I", "1928"),
            ("Wildly Dancing Children", "1909"),
            ("Masks and Dahlias", "1919"),
            ("Candle Dancers", "1912"),
        ],
        inspiration=(
            "nolde_incandescent_surge_pass(): three-stage chromatic surge -- "
            "(1) shadow warmth inversion: dark zones pushed warm (R+, B-), "
            "OPPOSITE of academic warm-light/cool-shadow; (2) mid-tone chromatic "
            "surge: bell-curve at lum=0.50 drives mid-tones to full spectral "
            "intensity; (3) vivid bloom halation: dual chroma+lum gate radiates "
            "warm halo from intense colour zones.  Use ground_color=(0.12, 0.06, 0.02) "
            "(raw umber dark imprimatura).  Best for florals, northern seascapes, "
            "figurative scenes with dark atmospheric backgrounds, savage colour drama."
        ),
    ),
'''

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'emil_nolde' not in content, 'emil_nolde already in catalog!'

# Insert before closing brace + get_style function
marker = '\n}\n\n\ndef get_style'
idx = content.find(marker)
assert idx != -1, f'Marker not found in art_catalog.py!'

new_content = content[:idx] + '\n' + NOLDE_ENTRY + content[idx:]

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

# Verify
import importlib, art_catalog
importlib.reload(art_catalog)
assert 'emil_nolde' in art_catalog.CATALOG
entry = art_catalog.CATALOG['emil_nolde']
print(f'Done. Catalog now has {len(art_catalog.CATALOG)} entries.')
print(f'emil_nolde: {entry.artist}, {entry.movement}, {entry.period}')
print(f'palette[0]: {entry.palette[0]}')
print(f'famous_works[0]: {entry.famous_works[0]}')
