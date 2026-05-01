"""Insert William Blake entry into art_catalog.py (session 279).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

BLAKE_ENTRY = '''
    # ── William Blake ─────────────────────────────────────────────────────────
    "william_blake": ArtStyle(
        artist="William Blake",
        movement="British Romanticism / Visionary Art / Illuminated Printing",
        nationality="British",
        period="1757-1827",
        palette=[
            (0.88, 0.72, 0.14),   # celestial gold -- divine fire, radiant glow
            (0.10, 0.15, 0.48),   # deep ultramarine -- spiritual void, night sky
            (0.78, 0.30, 0.10),   # vermilion flame -- body, earth, fire
            (0.85, 0.82, 0.70),   # pale parchment -- illuminated page, bare flesh
            (0.22, 0.12, 0.08),   # near-black umber -- dark contour lines, void
            (0.62, 0.58, 0.82),   # pale violet-blue -- intermediate sky, vision
            (0.28, 0.40, 0.22),   # dark viridian-green -- organic, earthly growth
            (0.82, 0.68, 0.50),   # warm tan -- flesh tone, manuscript vellum
            (0.52, 0.08, 0.08),   # deep crimson -- blood, spiritual sacrifice
            (0.92, 0.90, 0.82),   # near-white cream -- radiant center, divine light
        ],
        ground_color=(0.72, 0.66, 0.52),     # warm vellum/parchment ground
        stroke_size=9,
        wet_blend=0.18,
        edge_softness=0.06,
        jitter=0.022,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "British Romanticism and Visionary Art. William Blake (1757-1827) "
            "was born in Soho, London. He trained as an engraver under James "
            "Basire, learning to cut precise lines into copper, and briefly "
            "attended the Royal Academy before developing an entirely personal "
            "aesthetic rooted in visionary experience, Protestant mysticism, "
            "and radical politics. He invented RELIEF ETCHING -- writing and "
            "drawing directly onto copper plates with acid-resistant medium -- "
            "to produce his ILLUMINATED BOOKS (Songs of Innocence, Songs of "
            "Experience, The Marriage of Heaven and Hell, Jerusalem), each copy "
            "hand-colored by Blake and his wife Catherine in watercolor and "
            "tempera. His paintings in tempera and watercolor -- 'The Ancient "
            "of Days,' 'Newton,' 'Elohim Creating Adam,' 'Nebuchadnezzar,' "
            "'The Ghost of a Flea' -- are among the most intense and singular "
            "images in British art: hallucinatory, executed in a technique he "
            "called 'fresco' (actually a distemper of carpenter's glue and "
            "pigment on wood or canvas), combining engraving precision with "
            "painting color. "
            "THE WIRY BOUNDING LINE: Blake's central aesthetic principle was the "
            "supremacy of the precise, dark outline. 'The more distinct, sharp, "
            "and wiry the bounding line, the more perfect the work of art.' He "
            "attacked sfumato and atmospheric vagueness: 'Blots and blurs are "
            "not art.' Every form in a Blake painting is enclosed by a crisp "
            "dark line, darkest on the shadow side -- the boundary between "
            "spiritual and material worlds made visible. "
            "DIVINE RADIANCE: Blake's theology of light is specific: the divine "
            "emits not mere illumination but a TRANSFORMING RADIANCE that "
            "manifests as concentric rings around celestial sources -- multiple "
            "alternating bands of light and slight shadow, like interference "
            "rings of a heavenly vibration propagating outward. In 'The Ancient "
            "of Days,' 'Job,' and 'Jerusalem' this corona structure is explicit. "
            "CELESTIAL PALETTE: Gold and warm flame are the colors of divine "
            "creative fire; deep ultramarine is the color of spiritual depth "
            "and the void out of which creation emerges. His flesh tones are "
            "warm (vermilion-tan) in light, cool ultramarine in deep shadow -- "
            "a strong warm-cool duality that structures every composition. "
            "ILLUMINATED BOOK TECHNIQUE: Blake's pages combine precise relief- "
            "etched text and images with fluid hand-applied watercolor washes. "
            "The result is a layered surface: dark etched line over warm tinted "
            "ground, with floating washes of gold, blue, and crimson. "
            "SIGNATURE WORKS: Songs of Innocence (1789); Songs of Experience "
            "(1794); The Marriage of Heaven and Hell (1790-93); Jerusalem "
            "(1804-20); The Ancient of Days (1794); Newton (1795-c.1805); "
            "Elohim Creating Adam (1795); Nebuchadnezzar (1795); Pity (1795); "
            "The Ghost of a Flea (c.1819-20); The Book of Job illustrations "
            "(1823-25); Dante illustrations (1824-27)."
        ),
        famous_works=[
            ("Songs of Innocence",          "1789"),
            ("The Marriage of Heaven and Hell", "1790-93"),
            ("Songs of Experience",         "1794"),
            ("The Ancient of Days",         "1794"),
            ("Newton",                      "1795-c.1805"),
            ("Elohim Creating Adam",        "1795"),
            ("Nebuchadnezzar",              "1795"),
            ("Pity",                        "1795"),
            ("Jerusalem",                   "1804-20"),
            ("The Ghost of a Flea",         "c.1819-20"),
        ],
        inspiration=(
            "blake_visionary_radiance_pass(): FOUR-STAGE VISIONARY LIGHT AND "
            "CONTOUR SYSTEM -- 190th distinct mode. "
            "(1) ISO-LUMINANCE RING MODULATION: smooth luminance field used as "
            "phase angle of sin(2*pi*L_smooth*n_rings); first pass to apply "
            "periodic sinusoidal modulation keyed to the painting's own smooth "
            "luminance value (rings follow iso-luminance contours of the painting). "
            "(2) WARM GOLD CELESTIAL TINTING: smooth-luminance-gated blend toward "
            "celestial gold (0.88/0.72/0.14); first pass to gate warm shift on "
            "spatially smoothed luminance, targeting large-scale bright zones. "
            "(3) DARK CONTOUR REINFORCEMENT: shadow-side contour darkening via "
            "gradient direction offset; darken pixel one step in the dark "
            "direction; first pass to apply asymmetric shadow-side-only darkening. "
            "(4) DEEP SHADOW ULTRAMARINE INFUSION: smooth-luminance-gated blend "
            "toward ultramarine (0.10/0.15/0.48) in dark zones; first pass to "
            "push shadows toward cool blue specifically rather than warm shifts."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

ANCHOR = '    # ── Jan Toorop'
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, BLAKE_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: william_blake entry inserted.")
