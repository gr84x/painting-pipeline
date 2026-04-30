"""Update hilma_af_klint catalog inspiration to reference new biomorphic pass (session 257).

Run once to modify art_catalog.py; preserved as a change record afterward.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))

OLD_INSPIRATION = (
    '        inspiration=(\n'
    '            "Contrast large warm (amber/orange) zones against cool blue/violet zones. "\\n\n'
    '            "Use flowing spherical_flow() field for organic curved strokes. "\\n\n'
    '            "Jewel palette hint. Light pale ground visible in low-density areas."\\n\n'
    '        ),\n'
)

NEW_INSPIRATION = (
    '        inspiration=(\n'
    '            "hilma_af_klint_biomorphic_pass(): ONE HUNDRED AND SIXTY-EIGHTH "\n'
    '            "(168th) distinct mode -- three-stage biomorphic abstraction -- "\n'
    '            "(1) CONCENTRIC RADIAL GROWTH RING FIELD: compute luminance-weighted "\n'
    '            "centroid; radial distance field from centroid normalised by mean corner "\n'
    '            "distance; sine wave ring_field = 0.5*(1+sin(2*pi*r_norm*ring_count)); "\n'
    '            "first pass to generate concentric sine-wave rings from luminance-weighted "\n'
    '            "centroid for biomorphic abstraction; (2) BIOMORPHIC ZONE COLOUR RESONANCE: "\n'
    '            "inner ring zones (ring_field>0.5) pushed warm (R up, B down), outer zones "\n'
    '            "pushed cool (R down, B up), strength proportional to distance from 0.5 "\n'
    '            "transition; first pass to apply radial ring-distance-weighted chromatic "\n'
    '            "warm/cool zone push; (3) LUMINOUS BOUNDARY HAZE: gradient magnitude of "\n'
    '            "ring_field blurred at haze_sigma; applied as multiplicative luminosity "\n'
    '            "boost at ring boundaries; first pass to add luminosity glow along sine-wave "\n'
    '            "ring boundaries from a centroid-radial field."\n'
    '        ),\n'
)

catalog_path = os.path.join(REPO, "art_catalog.py")
with open(catalog_path, "r", encoding="utf-8") as f:
    src = f.read()

if "hilma_af_klint_biomorphic_pass" in src:
    print("hilma_af_klint inspiration already updated -- nothing to do.")
    sys.exit(0)

if OLD_INSPIRATION not in src:
    # Try alternate approach: find the hilma_af_klint block and update inline
    import re
    pattern = r'("hilma_af_klint".*?inspiration=\()([^)]+?)(\),\s*\),)'
    match = re.search(pattern, src, re.DOTALL)
    if not match:
        print("ERROR: could not locate hilma_af_klint inspiration field", file=sys.stderr)
        sys.exit(1)
    new_insp = (
        '"hilma_af_klint_biomorphic_pass(): ONE HUNDRED AND SIXTY-EIGHTH '
        '(168th) distinct mode -- three-stage biomorphic abstraction -- '
        '(1) CONCENTRIC RADIAL GROWTH RING FIELD: compute luminance-weighted '
        'centroid; radial distance normalised by mean corner distance; '
        'ring_field = 0.5*(1+sin(2*pi*r_norm*ring_count)); '
        'first pass to generate concentric sine-wave rings from luminance-weighted centroid; '
        '(2) BIOMORPHIC ZONE COLOUR RESONANCE: inner zones pushed warm, outer zones cool, '
        'strength proportional to ring_field distance from 0.5; '
        'first pass to apply radial ring-distance-weighted chromatic warm/cool zone push; '
        '(3) LUMINOUS BOUNDARY HAZE: gradient magnitude of ring_field blurred at haze_sigma, '
        'applied as multiplicative luminosity boost at ring boundaries; '
        'first pass to add luminosity glow along sine-wave ring boundaries."'
    )
    old_block = match.group(0)
    new_block = old_block[:old_block.index(match.group(2))] + "\n            " + new_insp + "\n        " + match.group(3)
    src = src.replace(old_block, new_block, 1)
else:
    src = src.replace(OLD_INSPIRATION, NEW_INSPIRATION, 1)

with open(catalog_path, "w", encoding="utf-8") as f:
    f.write(src)

print("Updated hilma_af_klint inspiration in art_catalog.py.")
