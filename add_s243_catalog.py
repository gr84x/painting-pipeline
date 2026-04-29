"""Insert ernst_ludwig_kirchner entry into art_catalog.py (session 243)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

KIRCHNER_ENTRY = '''    "ernst_ludwig_kirchner": ArtStyle(
        artist="Ernst Ludwig Kirchner",
        movement="German Expressionism / Die Brücke",
        nationality="German",
        period="1880-1938",
        palette=[
            (0.82, 0.12, 0.14),   # vivid cadmium red
            (0.14, 0.26, 0.72),   # deep cobalt blue
            (0.88, 0.84, 0.08),   # acid chrome yellow
            (0.16, 0.28, 0.14),   # dark olive black
            (0.52, 0.72, 0.22),   # acid lime green (Kirchner flesh distortion)
            (0.72, 0.14, 0.58),   # vivid magenta-violet
            (0.92, 0.90, 0.88),   # zinc white
            (0.28, 0.08, 0.06),   # near-black umber (woodcut contour)
        ],
        ground_color=(0.18, 0.16, 0.12),
        stroke_size=9,
        wet_blend=0.18,
        edge_softness=0.06,
        jitter=0.14,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Ernst Ludwig Kirchner (1880-1938) co-founded Die Brücke (The Bridge) "
            "in Dresden in 1905 with Erich Heckel, Karl Schmidt-Rottluff, and Fritz "
            "Bleyl -- the first and most confrontational of the German Expressionist "
            "groups.  Die Brücke took its name from Nietzsche\'s Also sprach Zarathustra "
            "-- the artist as a bridge between the decadent present and a spiritually "
            "renewed future.  Kirchner\'s painterly technique was forged in deliberate "
            "opposition to the academic tradition and to French Impressionism\'s "
            "attachment to pleasant sensation.  Instead he pursued raw psychological "
            "truth: angular, aggressive line; unnaturalistic, dissonant colour; figures "
            "elongated and distorted into states of inner tension.  His palette "
            "abandoned naturalism entirely -- flesh becomes acid green or cobalt blue, "
            "the sky a saturated cadmium red, shadows a near-black umber that owes "
            "nothing to observed light.  His chief pictorial inheritance was from African "
            "and Oceanic sculpture (seen at the Dresden Ethnographic Museum), medieval "
            "German woodcuts, and the graphic urgency of Van Gogh.  His move to Berlin "
            "in 1911 intensified his subject matter: the anonymity and sexual charge "
            "of the modern metropolis -- street scenes, dance halls, cafe corners, "
            "Potsdamer Platz prostitutes -- rendered with angular, jittery brushwork "
            "that conveys nervous urban energy.  Characteristic technical features: "
            "(1) Bold black contour lines derived from woodblock printing -- forms are "
            "enclosed within dark, drawn boundaries that flatten pictorial space; "
            "(2) Flat, slab-like colour planes within each bounded form -- Kirchner "
            "refused modelling through tone, preferring harsh tonal jumps between "
            "adjacent planes of pure, unblended colour; (3) Dissonant, chromatic "
            "colour choices -- Kirchner\'s colours are psychologically charged, not "
            "descriptive; reds clash with greens, yellows sit against violets, no "
            "colour rests comfortably with its neighbour; (4) Angular, hatched "
            "brushwork in large strokes -- aggressive rectangular marks that declare "
            "the hand of the maker; (5) Emotional rather than descriptive light -- "
            "lamplight is yellow acid, shadows are blue-black voids, highlights are "
            "zinc-white slabs.  The Nazis declared his work degenerate (entartet) in "
            "1937; 639 of his works were confiscated.  He destroyed much of his "
            "remaining work and shot himself in 1938.  His surviving oeuvre -- some "
            "20,000 works on paper and 1,400 paintings -- constitutes one of the most "
            "viscerally powerful and stylistically coherent bodies of work in "
            "twentieth-century art."
        ),
        famous_works=[
            ("Street, Berlin",                          "1913"),
            ("Potsdamer Platz",                         "1914"),
            ("Five Women in the Street",                "1913"),
            ("Self-Portrait as a Soldier",              "1915"),
            ("Seated Woman (Franzi)",                   "1910"),
            ("Winter Moonlit Night",                    "1919"),
            ("The Red Tower in Halle",                  "1915"),
            ("Bathers at Moritzburg",                   "1909"),
        ],
        inspiration=(
            "kirchner_brucke_expressionist_pass(): ONE HUNDRED AND FIFTY-FOURTH "
            "distinct mode -- three-stage Die Brücke expressionist simulation -- "
            "(1) CHROMATIC DISSONANCE AMPLIFICATION: compute per-pixel hue angle; "
            "for mid-range hues (not already at a Kirchner chromatic pole), apply "
            "a nonlinear hue rotation that pulls the colour toward the nearest "
            "Kirchner chromatic extreme (vivid red, cobalt blue, acid yellow); "
            "simultaneously boost saturation proportionally to displacement -- "
            "FIRST pass to apply psychologically-directed chromatic pull toward a "
            "curated set of artist-specific hue poles using per-pixel hue distance "
            "weighting; (2) WOODCUT CONTOUR DARKENING: detect edges by Sobel gradient "
            "magnitude; gate darkening to pixels where gradient exceeds contour_thresh; "
            "darken multiplicatively proportional to gradient magnitude -- FIRST pass "
            "to apply multiplicative darkening proportional to Sobel gradient magnitude, "
            "simulating the black contour lines of German woodblock printing; "
            "(3) FLAT PLANE VALUE POLARIZATION: within each pixel\'s local neighbourhood, "
            "compute local luminance mean; pixels above mean are pushed brighter, pixels "
            "below are pushed darker -- FIRST pass to apply local-mean-relative luminance "
            "polarization creating hard tonal jumps between light and dark planes "
            "characteristic of Kirchner\'s refusal to model form through gradual tonal "
            "transition.  Best for portraits, figure work, urban scenes."
        ),
    ),
'''

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'ernst_ludwig_kirchner' not in content, 'Ernst Ludwig Kirchner entry already exists!'

insert_before = '\n}\n\n\ndef get_style'
assert insert_before in content, 'Insertion marker not found!'

content = content.replace(insert_before, '\n' + KIRCHNER_ENTRY + '}\n\n\ndef get_style', 1)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. art_catalog.py new length: {len(content)} chars')

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'art_catalog' in mod:
        del _sys.modules[mod]
import art_catalog
assert 'ernst_ludwig_kirchner' in art_catalog.CATALOG, 'ernst_ludwig_kirchner missing from CATALOG'
entry = art_catalog.CATALOG['ernst_ludwig_kirchner']
assert entry.artist == 'Ernst Ludwig Kirchner', f'artist mismatch: {entry.artist!r}'
print(f'Verified: ernst_ludwig_kirchner in CATALOG. Total artists: {len(art_catalog.CATALOG)}')
