"""Insert helen_frankenthaler entry into art_catalog.py (session 241)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

FRANKENTHALER_ENTRY = '''    "helen_frankenthaler": ArtStyle(
        artist="Helen Frankenthaler",
        movement="Color Field / Abstract Expressionism",
        nationality="American",
        period="1928-2011",
        palette=[
            (0.24, 0.52, 0.78),   # cerulean blue — sky and water stains
            (0.88, 0.54, 0.62),   # rose-carnation — warm poured wash
            (0.92, 0.82, 0.38),   # warm yellow-ochre — sunlit canvas ground
            (0.38, 0.70, 0.50),   # sage green — spreading vegetal pool
            (0.82, 0.44, 0.28),   # terra cotta — dry-edge blush
            (0.74, 0.64, 0.82),   # soft lavender — pooled shadow
            (0.96, 0.94, 0.88),   # off-white — raw canvas luminosity
            (0.28, 0.36, 0.60),   # deep indigo — darkest absorbed pool
        ],
        ground_color=(0.94, 0.92, 0.86),
        stroke_size=0,
        wet_blend=0.60,
        edge_softness=0.72,
        jitter=0.04,
        glazing=(0.24, 0.52, 0.78),
        crackle=False,
        chromatic_split=False,
        technique=(
            "Helen Frankenthaler (1928-2011) invented the soak-stain technique in 1952 "
            "with her breakthrough painting Mountains and Sea, fundamentally changing "
            "the direction of American abstract painting and inaugurating the Color Field "
            "movement.  Working on raw, unprimed canvas spread flat on the studio floor, "
            "she poured thinned paint -- oil paint diluted with turpentine to near-wash "
            "consistency, or later acrylic heavily thinned -- directly from cans and "
            "buckets, tilting and walking the canvas to guide the flowing pools.  Because "
            "the canvas is unprimed, the paint does not sit as a film on the surface: it "
            "soaks INTO the weave of the cotton duck, staining the fibres themselves and "
            "becoming one with the fabric.  The result is an image with no paint layer in "
            "the traditional sense -- no impasto, no brushwork texture, no surface "
            "reflection -- only luminous, transparent colour that reads as pure light "
            "rather than applied pigment.  Where pools of different colours meet, they "
            "blend with soft, irregular edges set by capillary absorption and the tilt "
            "of the canvas; there are no drawn contours, no boundaries between colour "
            "zones other than the natural edge of the absorbed stain.  The raw canvas "
            "itself reads as an active colour -- its warm off-white integrates with the "
            "stains, creating a unified luminous field.  Her palette was consistently "
            "high-keyed, transparent, and lyrical: cerulean blues, rose, sage green, "
            "lavender, and warm yellow-ochre -- the palette of Mediterranean light and "
            "open watercolour washes.  She influenced Morris Louis, Kenneth Noland, and "
            "Jules Olitski, launching a generation of stain painters.  Her major works "
            "include Mountains and Sea (1952), Eden (1956), Before the Caves (1958), "
            "Interior Landscape (1964), and Flood (1967)."
        ),
        famous_works=[
            ("Mountains and Sea",      "1952"),
            ("Eden",                   "1956"),
            ("Before the Caves",       "1958"),
            ("Interior Landscape",     "1964"),
            ("Flood",                  "1967"),
            ("Moveable Blue",          "1973"),
            ("Hint from Bassano",      "1973"),
            ("Natural Answer",         "1976"),
        ],
        inspiration=(
            "frankenthaler_soak_stain_pass(): ONE HUNDRED AND FIFTY-SECOND distinct mode -- "
            "three-stage soak-stain simulation -- "
            "(1) ORGANIC STAIN REGION GENERATION: multi-scale noise field composed of "
            "two Gaussian-blurred random planes (sigma_large, sigma_small) summed with "
            "weights; stain_field = clip(w_large*blur(noise,sigma_large) + "
            "w_small*blur(noise,sigma_small), 0, 1) -- FIRST pass to generate organic "
            "stain region masks using luminance-biased multi-scale noise composition; "
            "no prior pass builds region masks from summed multi-sigma random fields; "
            "(2) PAINT ABSORPTION SIMULATION: ch_stained = ch_canvas*(1-stain_mask) + "
            "(ch_canvas + stain_color*stain_alpha)*stain_mask; absorption_factor blends "
            "stain color toward canvas ground, modelling pigment wicking INTO canvas "
            "fibres rather than sitting on top -- FIRST pass to model sub-surface "
            "absorption: paint thinned by blending toward canvas ground via absorption "
            "coefficient rather than opacity alone; "
            "(3) CAPILLARY EDGE DIFFUSION: boundary_mask = |nabla stain_mask| > cap_thresh; "
            "ch_cap = gaussian_blur(ch_stained, sigma=cap_sigma); "
            "ch_final = ch_cap*boundary_mask + ch_stained*(1-boundary_mask) -- "
            "FIRST pass to apply stain-boundary-localised extra Gaussian blur simulating "
            "capillary paint migration along canvas fibres at the stain perimeter.  "
            "Use off-white raw canvas ground (0.94, 0.92, 0.86).  "
            "Best for lyrical abstract subjects: open colour fields, soft landscape "
            "horizons, atmospheric abstraction.  Combine with paint_lost_found_edges_pass "
            "to selectively re-crisp key structural boundaries while preserving the "
            "soak quality of peripheral areas."
        ),
    ),
'''

with open('art_catalog.py', 'r', encoding='utf-8') as f:
    content = f.read()

assert 'helen_frankenthaler' not in content, 'Frankenthaler entry already exists!'

# Insert before the closing } of CATALOG
insert_before = '\n}\n\n\ndef get_style'
assert insert_before in content, f'Insertion marker not found!'

content = content.replace(insert_before, '\n' + FRANKENTHALER_ENTRY + '}\n\n\ndef get_style', 1)

with open('art_catalog.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. art_catalog.py new length: {len(content)} chars')

# Verify importable and entry present
import importlib, sys as _sys
for mod in list(_sys.modules.keys()):
    if 'art_catalog' in mod:
        del _sys.modules[mod]
import art_catalog
assert 'helen_frankenthaler' in art_catalog.CATALOG, 'Frankenthaler missing from CATALOG'
entry = art_catalog.CATALOG['helen_frankenthaler']
assert entry.artist == 'Helen Frankenthaler', f'artist mismatch: {entry.artist!r}'
print(f'Verified: helen_frankenthaler in CATALOG. Total artists: {len(art_catalog.CATALOG)}')
