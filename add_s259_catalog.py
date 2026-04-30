"""Insert theo_van_rysselberghe entry into art_catalog.py (session 259).

Run once to modify art_catalog.py; preserved as a change record afterward.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))

RYSSELBERGHE_ENTRY = """    "theo_van_rysselberghe": ArtStyle(
        artist="Th\xe9o van Rysselberghe",
        movement="Belgian Neo-Impressionism / Divisionism / Pointillism",
        nationality="Belgian",
        period="1862–1926",
        palette=[
            (0.95, 0.87, 0.30),   # cadmium yellow, sunlight peak
            (0.12, 0.42, 0.75),   # cobalt blue, sky and shadow
            (0.18, 0.62, 0.52),   # viridian, sea mid-tone
            (0.88, 0.52, 0.24),   # cadmium orange, sunset warmth
            (0.74, 0.84, 0.92),   # pale cerulean, sky highlight
            (0.92, 0.90, 0.82),   # warm white, linen/sail
            (0.52, 0.76, 0.48),   # chrome green, foliage
            (0.88, 0.68, 0.58),   # naples yellow-pink, skin warm
        ],
        ground_color=(0.95, 0.93, 0.85),    # warm white canvas
        stroke_size=6,
        wet_blend=0.06,
        edge_softness=0.18,
        jitter=0.025,
        glazing=None,
        crackle=False,
        chromatic_split=True,
        technique=(
            "Th\xe9o van Rysselberghe (1862–1926) was the leading Belgian practitioner "
            "of Neo-Impressionist Divisionism and a founding member of Les XX, "
            "the Brussels-based avant-garde group that introduced Seurat and "
            "Signac to Belgian audiences. He worked primarily in oil on canvas, "
            "applying pure spectral pigment in small, carefully separated "
            "brush-marks that the eye mixes optically at viewing distance. His "
            "subjects ranged from Mediterranean coastal scenes and garden figures "
            "to formal portraits of bourgeois intellectuals and Symbolist "
            "figures. Three technical signatures define van Rysselberghe's work: "
            "(1) CHROMATIC DOT DECOMPOSITION — Rysselberghe applied pigment "
            "as discrete units of near-pure spectral colour. Rather than "
            "physically mixing pigments on the palette, he placed complementary "
            "and adjacent spectral hue-dots next to each other on the canvas "
            "surface, trusting the viewer's eye to perform the mixture at a "
            "distance. This optical mixture yields a higher apparent luminosity "
            "than physical pigment mixing: mixed pigments absorb more light "
            "(subtractive); juxtaposed pure-hue dots add luminous intensities "
            "(additive-ish). The result is a shimmering surface quality "
            "distinct from plein-air impressionism; "
            "(2) MEDITERRANEAN LUMINOSITY — from the 1890s onward van "
            "Rysselberghe spent increasing time on the Mediterranean coast "
            "at Cap-N\xe8gre. The intense solar light of the Mediterranean gave "
            "his palette an extraordinary chromatic range: shadows in the "
            "Mediterranean sun are not grey but violet-cobalt; lit areas are "
            "not white but yellow-green-cadmium; the sea itself fragments into "
            "viridian, cerulean, and cobalt depending on depth and angle; "
            "(3) STRUCTURED SURFACE VIBRATION — the systematic dot application "
            "gives his canvases a fine, all-over surface texture not found in "
            "other schools: the paint film is physically a field of discrete "
            "dabs of approximately equal size, creating a measurable spatial "
            "frequency in the mark structure that is separate from the "
            "compositional structure. This surface vibration gives his work "
            "its characteristic aliveness: the surface seems to shimmer and "
            "breathe even in reproduction."
        ),
        famous_works=[
            ("The Family in the Orchard",         "1890"),
            ("The Promenade",                     "1901"),
            ("Boats Drying, Normandy",             "1892"),
            ("Maria Sèthe at the Harmonium",       "1891"),
            ("Regatta at Nieuwpoort",              "1893"),
            ("In July (Before the Storm)",         "1904"),
            ("Portrait of Emile Verhaeren",        "1892"),
            ("Reading in the Garden",              "1903"),
            ("The Bath",                           "1912"),
            ("Sea at Ambleteuse",                  "1900"),
        ],
        inspiration=(
            "rysselberghe_chromatic_dot_field_pass(): ONE HUNDRED AND SEVENTIETH "
            "(170th) distinct mode — three-stage Neo-Impressionist pointillist "
            "chromatic field effect — "
            "(1) SPECTRAL HUE SATURATION BOOST: hue-angle-dependent saturation push "
            "toward nearest spectral primary (red/yellow/green/cyan/blue/violet); "
            "models pure unmixed pigment selection for each dot unit; "
            "first pass for hue-angle-dependent spectral-primary proximity saturation boost; "
            "(2) OPTICAL LUMINOSITY ENHANCEMENT: saturation-gated luminance lift "
            "in high-saturation pixels simulating additive optical mixing luminosity gain; "
            "first pass to use per-pixel saturation as gate for luminance enhancement "
            "as a model of Neo-Impressionist optical colour mixing; "
            "(3) DOT FIELD TEXTURE: spatially-periodic jittered grid of Gaussian-profile "
            "luminance bumps simulating discrete paint mark discretisation; "
            "first pass to stamp a fresh spatial dot grid as luminance micro-modulation."
        ),
    ),
"""

ANCHOR = '"leon_spilliaert": ArtStyle('

catalog_path = os.path.join(REPO, "art_catalog.py")
with open(catalog_path, "r", encoding="utf-8") as f:
    src = f.read()

if '"theo_van_rysselberghe"' in src:
    print("theo_van_rysselberghe already present -- nothing to do.")
    sys.exit(0)

if ANCHOR not in src:
    # Fallback to gerhard_richter anchor
    ANCHOR = '"gerhard_richter": ArtStyle('
    if ANCHOR not in src:
        print(f"ERROR: anchor not found in art_catalog.py", file=sys.stderr)
        sys.exit(1)

src = src.replace(ANCHOR, RYSSELBERGHE_ENTRY + "    " + ANCHOR, 1)

with open(catalog_path, "w", encoding="utf-8") as f:
    f.write(src)

print("Inserted theo_van_rysselberghe into art_catalog.py.")
