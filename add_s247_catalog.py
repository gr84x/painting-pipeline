"""Insert kathe_kollwitz entry into art_catalog.py (session 247)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

KOLLWITZ_ENTRY = '''    "kathe_kollwitz": ArtStyle(
        artist="Käthe Kollwitz",
        movement="German Expressionism / Social Realism",
        nationality="German",
        period="1867-1945",
        palette=[
            (0.12, 0.09, 0.07),   # warm deep black (charcoal shadow, sepia dark)
            (0.38, 0.30, 0.22),   # warm dark umber (mid shadow, charcoal mid-tone)
            (0.62, 0.54, 0.44),   # warm grey (mid-tone, stone, worn fabric)
            (0.82, 0.76, 0.66),   # warm light grey (highlighted skin, paper tone)
            (0.95, 0.90, 0.80),   # warm paper white (light peak, lithographic ground)
            (0.48, 0.38, 0.28),   # sepia brown (etching plate tone, aged paper)
            (0.24, 0.20, 0.16),   # near-black (deep shadow, vignette edge)
            (0.70, 0.62, 0.50),   # ochre-grey (transition tone, worn wall stone)
        ],
        ground_color=(0.82, 0.76, 0.66),
        stroke_size=14,
        wet_blend=0.10,
        edge_softness=0.05,
        jitter=0.04,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Käthe Kollwitz (1867-1945) was the pre-eminent German Expressionist "
            "printmaker and draughtswoman of the early twentieth century -- the only "
            "artist ever elected to the Prussian Academy of Arts as a full member during "
            "its imperial period (1919), and subsequently the first woman to hold a full "
            "professorship there. Her medium was never oil paint; she worked almost "
            "exclusively in graphite, charcoal, chalk, etching, aquatint, mezzotint, "
            "lithography, and woodcut. The total absence of colour in her mature work was "
            "not a limitation but an ideology: she believed that the full palette of oil "
            "painting was an instrument of bourgeois pleasure, incompatible with the "
            "experience of hunger, bereavement, and class struggle that was her subject. "
            "Her subjects were the working poor of Berlin -- women mourning dead sons, "
            "mothers clutching infants, labour marches, death personified as a dark "
            "embracing figure -- and the parents of the First World War dead, including "
            "her own son Peter, killed at Diksmuide in 1914. The 'Grieving Parents' "
            "sculptures at the Vladslo German War Cemetery in Belgium, completed in 1932, "
            "are her most public monument: the kneeling stone figures of herself and her "
            "husband facing Peter\'s grave. "
            "Her technical signature: (1) WARM CHARCOAL MONOCHROME -- the near-absence "
            "of chromatic colour does not produce a cold, photographic grey but a warm "
            "sepia-and-charcoal range where the paper ground (warm buff or cream) shows "
            "through the lightest passages, and the shadows fall into deep warm black; "
            "the result feels organic, bodily, made by hand; (2) SIGMOID TONAL CONTRAST "
            "-- the deepest darks are very deep and the highest lights are very bright; "
            "the contrast range is wider than any chromatic painting could sustain, "
            "because there is no colour information competing for attention; she pushes "
            "the values to the edges of the tonal scale; (3) DIRECTIONAL GRAIN TEXTURE "
            "in shadow zones -- her charcoal and lithographic work shows the directionality "
            "of the mark-making in the darkest areas: parallel or sub-parallel strokes at "
            "a consistent angle create an almost tactile surface; the grain is not random "
            "noise but oriented marks, as in the crossed hatching of an etching plate; "
            "(4) SILHOUETTE WEIGHT -- figures and faces read first as dark silhouettes "
            "against the lighter ground; the internal modelling is subordinate to the "
            "gestalt shape; (5) EMOTIONAL CONCENTRATION -- Kollwitz never painted a "
            "landscape, a still life, or an abstract form; every mark she made served a "
            "single purpose: to make the viewer feel the weight of human suffering and "
            "the dignity of endurance. Her prints were mass-produced and distributed as "
            "political art, intended for factory walls and union halls, not private "
            "collections. The Nazis confiscated her work from museums in 1936; she died "
            "in Moritzburg, Saxony, in April 1945, sixteen days before the war ended."
        ),
        famous_works=[
            ("Weaver\'s Revolt: The March of the Weavers",  "1897"),
            ("Peasant War: Outbreak",                         "1903"),
            ("Mother with Dead Child",                        "1903"),
            ("Self-Portrait with Hand on Forehead",           "1910"),
            ("War: The Sacrifice",                            "1922"),
            ("Grieving Parents (sculptures, Vladslo)",        "1932"),
            ("Never Again War",                               "1924"),
            ("Death Seizes a Woman",                          "1934"),
        ],
        inspiration=(
            "kollwitz_charcoal_etching_pass(): ONE HUNDRED AND FIFTY-EIGHTH "
            "distinct mode -- three-stage warm monochrome social realism -- "
            "(1) WARM CHARCOAL MONOCHROME CONVERSION: compute luminance; map "
            "each pixel to a two-endpoint warm charcoal ramp (dark_r/g/b at "
            "lum=0, warm_r/g/b at lum=1) then blend from original toward this "
            "charcoal image with weight desat_str; first pass to desaturate "
            "using a dual-endpoint warm charcoal ramp parameterised separately "
            "for shadows and highlights rather than blending toward achromatic "
            "grey (no prior pass maps luminance to a two-colour charcoal ramp "
            "as the desaturation target); "
            "(2) SIGMOID TONAL CONTRAST EXPANSION: apply lum_new = "
            "1/(1+exp(-k*(lum-0.5))) with k=sigmoid_k to the post-desaturation "
            "luminance, then scale each channel by lum_new/max(lum+1e-7, eps); "
            "first pass to apply a parametric symmetric sigmoid tone curve as a "
            "standalone contrast stage (prior passes use Sobel edge maps, "
            "percentile stretches, or luminance thresholds -- none apply sigmoid); "
            "(3) DIRECTIONAL SHADOW GRAIN: build a 1D line kernel at "
            "grain_angle_deg by accumulating sub-pixel Gaussian weight along a "
            "parametric line direction; convolve the shadow zone (lum < "
            "shadow_thresh) with this kernel; add the high-frequency residual "
            "texture back into the dark area; first pass to add angular "
            "directional texture specifically in the shadow zone using a "
            "parametric-angle line kernel (no prior pass applies direction-"
            "specific convolutional texture gated by shadow luminance). Best for "
            "figurative subjects that benefit from graphic, monochromatic drama: "
            "portraits, groups, hands, grief and weight."
        ),
    ),
'''

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'kathe_kollwitz' not in content, 'kathe_kollwitz entry already exists!'

insert_before = '\n}\n\n\ndef get_style'
assert insert_before in content, 'Insertion marker not found!'

content = content.replace(insert_before, '\n' + KOLLWITZ_ENTRY + '}\n\n\ndef get_style', 1)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. art_catalog.py new length: {len(content)} chars')

import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'art_catalog' in mod:
        del _sys.modules[mod]
import art_catalog
assert 'kathe_kollwitz' in art_catalog.CATALOG, 'kathe_kollwitz missing from CATALOG'
entry = art_catalog.CATALOG['kathe_kollwitz']
assert entry.artist == 'Käthe Kollwitz', f'artist mismatch: {entry.artist!r}'
print(f'Verified: kathe_kollwitz in CATALOG. Total artists: {len(art_catalog.CATALOG)}')
