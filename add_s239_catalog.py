"""Insert otto_dix entry into art_catalog.py (session 239)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

DIX_ENTRY = '''    "otto_dix": ArtStyle(
        artist="Otto Dix",
        movement="Expressionism, Neue Sachlichkeit (New Objectivity)",
        nationality="German",
        period="1891-1969",
        palette=[
            (0.14, 0.10, 0.08),   # near-black contour / coal shadow
            (0.82, 0.62, 0.44),   # raw flesh / light ochre skin
            (0.58, 0.18, 0.08),   # deep cadmium red-brown
            (0.78, 0.72, 0.62),   # pale yellow-grey highlight
            (0.24, 0.20, 0.18),   # dark umber shadow
            (0.62, 0.42, 0.28),   # warm sienna mid-tone
            (0.44, 0.38, 0.32),   # grey-brown neutral
            (0.90, 0.86, 0.80),   # near-white bare plaster / light ground
        ],
        ground_color=(0.82, 0.78, 0.70),
        stroke_size=4.5,
        wet_blend=0.22,
        edge_softness=0.10,
        jitter=0.04,
        glazing=(0.34, 0.20, 0.08),
        crackle=False,
        chromatic_split=False,
        technique=(
            "Otto Dix (1891-1969) emerged from the German Expressionism of Die "
            "Brücke and Grosz but moved toward the New Objectivity (Neue "
            "Sachlichkeit) of the 1920s -- a reaction against Expressionism\'s "
            "emotional distortion, seeking instead a merciless, hyper-acute "
            "realism that exposed social conditions without sentimentality.  His "
            "technique was the antithesis of Impressionist softness: hard, "
            "surgical contours drawn from Old Master metalpoint precision; "
            "flattened midtones that compress the tonal range into extreme "
            "contrast; and an almost forensic illumination -- harsh frontal or "
            "three-quarter light that leaves no shadow ambiguity.  His wartime "
            "triptychs (Der Krieg, 1932) are among the most confrontational "
            "images in twentieth-century painting: decomposing bodies, barbed "
            "wire, and mustard-gas disfigurement rendered with the same "
            "meticulous brushwork as a Renaissance altarpiece.  His Weimar-era "
            "portraits -- prostitutes, journalists, industrialists, war "
            "veterans -- use this same surgical clarity to dissect class and "
            "power.  The palette is austere and often cold: raw flesh, dark "
            "umber, yellow-grey plaster light, near-black contour.  Colour is "
            "not decorative but diagnostic -- each hue assigned to a precise "
            "function in the tonal hierarchy.  Dix returned to Old Master "
            "techniques after 1920, working in tempera under-painting with "
            "oil glazes, which gives his surfaces their hard enamel-like "
            "quality.  His line is the most precise in German Expressionism: "
            "tight, controlled, without the nervous flutter of Schiele or the "
            "calligraphic sweep of Kirchner."
        ),
        famous_works=[
            ("Der Krieg (The War) Triptych", "1929-32"),
            ("Portrait of the Journalist Sylvia von Harden", "1926"),
            ("Metropolis Triptych", "1928"),
            ("The Trench", "1923"),
            ("Portrait of Hugo Erfurth with Dog", "1926"),
            ("Nude Girl on Fur", "1932"),
            ("The Triumph of Death", "1934"),
            ("Flanders", "1934-36"),
        ],
        inspiration=(
            "dix_neue_sachlichkeit_pass(): three-stage New Objectivity simulation -- "
            "(1) MIDTONE TONAL COMPRESSION: distance-from-neutral metric "
            "t=abs(lum-0.5)/0.5; compress_gate=t**midtone_gamma; "
            "target=(1 if lum>0.5 else 0); lum_new=lum+(target-lum)*compress_gate*cs -- "
            "FIRST pass to implement tonal compression via luminance-distance-from-neutral "
            "gate: midtones pushed toward their nearest extreme, creating the flat, "
            "surgical midtone quality of Neue Sachlichkeit; "
            "(2) BOUNDARY SATURATION SURGE: edge_gate=sobel_mag gated to "
            "[transit_lo, transit_hi] luminance transition zone; sat_scale=1+surge*gate; "
            "ch=lum3+(ch-lum3)*sat_scale -- FIRST pass to boost saturation specifically "
            "at shadow-to-highlight transition boundaries (mid-gradient zone), not "
            "globally or in shadows/highlights alone; "
            "(3) FORENSIC HIGHLIGHT CRISPING: hi_gate=clip((lum-hi_thresh)/"
            "(1-hi_thresh),0,1)**hi_power; R,G,B pushed toward near-white at max gate -- "
            "combined tonal compression + boundary saturation + highlight crispening "
            "in one unified model.  Use warm plaster ground (0.82, 0.78, 0.70).  "
            "Best for portraits, figures, urban scenes, and subjects with strong "
            "tonal contrast.  Combine with paint_glaze_gradient_pass for descending "
            "warm ochre wash reinforcing the plaster-ground quality."
        ),
    ),
'''

INSERT_BEFORE = '}\n\n\ndef get_style'

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'otto_dix' not in content, 'Otto Dix already in catalog!'
assert INSERT_BEFORE in content, f'Anchor not found in art_catalog.py'

content = content.replace(INSERT_BEFORE, DIX_ENTRY + INSERT_BEFORE)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. Otto Dix entry inserted into art_catalog.py')

import importlib
for mod in list(sys.modules.keys()):
    if 'art_catalog' in mod:
        del sys.modules[mod]
import art_catalog
s = art_catalog.CATALOG['otto_dix']
print(f'Verified: {s.artist} ({s.movement}) | {len(art_catalog.CATALOG)} total artists')
