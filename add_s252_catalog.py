"""Insert gerhard_richter entry into art_catalog.py (session 252).

NOTE: This script was already executed during session 252. Running it again
will fail the assertion check. It is preserved as a record of the change.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))

RICHTER_ENTRY = """    "gerhard_richter": ArtStyle(
        artist="Gerhard Richter",
        movement="Neo-Expressionism / Photorealism / Abstract Painting",
        nationality="German",
        period="1932–present",
        palette=[
            (0.82, 0.78, 0.74),   # warm neutral grey
            (0.92, 0.88, 0.84),   # light grey / near-white
            (0.28, 0.26, 0.24),   # dark graphite
            (0.72, 0.38, 0.18),   # cadmium orange-red
            (0.24, 0.42, 0.64),   # cerulean blue
            (0.38, 0.58, 0.32),   # mid viridian green
            (0.88, 0.76, 0.22),   # cadmium yellow
            (0.52, 0.48, 0.46),   # mid neutral grey
            (0.14, 0.16, 0.18),   # near-black cool
            (0.68, 0.62, 0.56),   # warm tan
        ],
        ground_color=(0.86, 0.82, 0.78),
        stroke_size=32,
        wet_blend=0.78,
        edge_softness=0.65,
        jitter=0.14,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Gerhard Richter (born 1932, Dresden) is one of the most significant "
            "painters of the twentieth and twenty-first centuries, working in two "
            "completely opposed modes that he has pursued simultaneously for over "
            "fifty years: photorealistic painting derived from photographs (usually "
            "blurred, usually grey, usually depicting ordinary life, landscapes, or "
            "historical violence) and large-scale abstract painting made by dragging "
            "thick oil paint across the canvas with a wide rubber or metal squeegee. "
            "The two modes are not contradictions but complementary investigations "
            "into the relationship between chance and intention, between image and "
            "surface, between painting and photography. Richter left East Germany "
            "for the West in 1961, just before the Wall closed. His first major "
            "works were paintings derived from amateur photographs -- family "
            "snapshots, newspaper images -- rendered with meticulous realism then "
            "smeared and blurred while the paint was still wet. The blur was not "
            "decorative but epistemological: a commentary on what painting could "
            "claim to know. The abstract squeegee works began in the 1970s with "
            "the Vermalung (overpainted) works and expanded into the large-scale "
            "Abstract Paintings (Abstraktes Bild) series that dominates his late "
            "practice. His technical signature: (1) THE SQUEEGEE DRAG -- Richter "
            "builds up a heavily loaded canvas with bright colours in thick "
            "application, then drags a wide squeegee blade across the surface in "
            "a single sustained gesture; the blade simultaneously mixes, layers, "
            "reveals, and buries the colours beneath; each drag creates colour "
            "rivers, chromatic trails at the blade edges, and exposed underlayers "
            "where paint has been removed; the surface is both dense and "
            "transparent at once; (2) LAYERED ACCUMULATION -- the squeegee "
            "paintings are built up over months or years with many drag events, "
            "each adding new colour while partially destroying the previous "
            "state; the final surface retains geological strata of previous "
            "drag events visible through the uppermost layer; (3) CHANCE AND "
            "CONTROL -- Richter speaks of the squeegee paintings as a dialogue "
            "between intention and accident; he loads the colour intentionally "
            "but the drag event introduces unpredictable mixing and revelation; "
            "the outcome could not be predicted from the inputs; (4) PHOTO-BLUR "
            "TECHNIQUE -- in the photorealist works, a soft brush is dragged "
            "across the wet surface with a long horizontal stroke, blurring the "
            "image into the indistinct quality of a memory or a photograph taken "
            "through glass; the blur is isotropic near the centre and directional "
            "at the edges."
        ),
        famous_works=[
            ("Uncle Rudi",                               "1965"),
            ("Eight Student Nurses",                     "1966"),
            ("October 18, 1977 (series)",                "1988"),
            ("Abstraktes Bild (649-2)",                  "1987"),
            ("Cage (1-6)",                               "2006"),
            ("Betty",                                    "1988"),
            ("Strontium",                                "2004"),
            ("Birkenau",                                 "2014"),
        ],
        inspiration=(
            "richter_squeegee_drag_pass(): ONE HUNDRED AND SIXTY-THIRD "
            "distinct mode -- three-stage squeegee drag -- "
            "(1) HORIZONTAL DRAG BAND DECOMPOSITION: divide canvas into "
            "n_bands horizontal strips of randomly varied height (band_min "
            "to band_max pixels); for each band, compute a lateral drag by "
            "blending pixel colours toward the mean colour of adjacent y-offset "
            "rows scaled by drag_fraction; accumulate a per-pixel drag weight "
            "map; first pass to apply spatially partitioned horizontal drag "
            "averaging that mixes colour between adjacent bands rather than "
            "a uniform global blur; (2) LATERAL PIGMENT CHANNEL TRAILS: "
            "at each inter-band boundary detect pixels above sat_threshold; "
            "apply a directional horizontal blur of width trail_length to "
            "create pigment channel trails -- concentrated colour ridges left "
            "by the squeegee blade edge; first pass to detect saturation-gated "
            "pigment concentrations at drag-band boundaries and apply "
            "directional trail blur along the drag axis as a distinct stage; "
            "(3) DRAG RESIDUE LUMINANCE MODULATION: for each drag band apply "
            "a sinusoidal luminance modulation of frequency 1/band_height "
            "with amplitude residue_amp: brightening at the leading edge "
            "(paint thinned by blade), darkening at trailing edge (paint "
            "accumulated before blade); first pass to apply band-coordinated "
            "sinusoidal luminance modulation to simulate squeegee paint "
            "thickness variation."
        ),
    ),
"""

catalog_path = os.path.join(REPO, "art_catalog.py")
with open(catalog_path, "r", encoding="utf-8") as f:
    content = f.read()

assert "gerhard_richter" not in content, "gerhard_richter already exists -- already applied"
insert_before = "\n}\n\n\ndef get_style"
assert insert_before in content, "marker not found in art_catalog.py"
content = content.replace(insert_before, "\n" + RICHTER_ENTRY + "}\n\n\ndef get_style", 1)

with open(catalog_path, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Done. art_catalog.py new length: {len(content)} chars")
