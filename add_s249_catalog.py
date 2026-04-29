"""Insert jean_michel_basquiat entry into art_catalog.py (session 249)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASQUIAT_ENTRY = """    "jean_michel_basquiat": ArtStyle(
        artist="Jean-Michel Basquiat",
        movement="Neo-Expressionism / Street Art / Graffiti",
        nationality="American",
        period="1960-1988",
        palette=[
            (0.07, 0.07, 0.06),
            (0.90, 0.16, 0.10),
            (0.96, 0.84, 0.08),
            (0.92, 0.91, 0.88),
            (0.68, 0.46, 0.24),
            (0.14, 0.18, 0.70),
            (0.12, 0.52, 0.22),
            (0.90, 0.52, 0.12),
            (0.30, 0.30, 0.30),
            (0.76, 0.80, 0.14),
        ],
        ground_color=(0.10, 0.09, 0.07),
        stroke_size=20,
        wet_blend=0.10,
        edge_softness=0.14,
        jitter=0.16,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Jean-Michel Basquiat (1960-1988) was born in Brooklyn, New York, to "
            "Haitian and Puerto Rican parents. He dropped out of high school at "
            "seventeen, began sleeping in Tompkins Square Park and selling hand-"
            "painted postcards, and emerged from the SAMO graffiti movement "
            "(1977-1979) -- a pseudonymous identity shared with Al Diaz that "
            "appeared across Lower Manhattan walls in short, enigmatic phrases "
            "challenging the commercial art world -- to become, in barely eight "
            "productive years, one of the most celebrated artists of the twentieth "
            "century. His career was inseparable from his life in the downtown "
            "New York scene: he was the first graffiti artist elevated to gallery "
            "status, exhibited at the Annina Nosei Gallery at twenty and sold at "
            "Sotheby's at twenty-one; he was on the cover of the New York Times "
            "Magazine at twenty-two. He died of a heroin overdose at twenty-seven. "
            "His entire painting career lasted less than a decade. "
            "His technical signature: (1) RAW MARK ENERGY -- Basquiat's primary "
            "compositional language was the crude mark: the line drawn fast, the "
            "word scratched through, the colour applied flat with a house "
            "painter's brush or a spray can or a marker; the surface of a Basquiat "
            "carries the evidence of its making at every point; paint is thick in "
            "some areas and barely there in others; gestures are left unresolved; "
            "(2) FLAT COLOUR FIELDS -- beneath the marks and figures, Basquiat "
            "applied flat, undiluted areas of primary colour -- cadmium red, chrome "
            "yellow, raw white, near-black -- in direct house-paint opacity; these "
            "areas are not gradated, not tonal, not atmospheric; they carry the "
            "graphic directness of sign painting; (3) TEXT AND SYMBOL -- words, "
            "phrases, numbers, anatomical labels, crossed-out text, crown symbols, "
            "copyright marks, arrows, and SAMO inscriptions are as much visual "
            "marks as the painted figures; Basquiat painted as a writer and drew "
            "as a painter; (4) SCHEMATIC ANATOMY -- the human body appears in "
            "Basquiat's work as a diagram rather than an observed form: skull-like "
            "faces with teeth exposed, figures that reveal their bones, anatomical "
            "labelling, the separation of skin from what lies beneath; this is body "
            "as text, body as symbol; (5) THE CROWN -- Basquiat's most iconic "
            "symbol is the three-point crown, which appears repeatedly above "
            "figures, beside signatures, and as a standalone motif; it signifies "
            "royalty, Black cultural kingship, defiance of erasure, and the "
            "elevation of his subjects to the status of kings and heroes."
        ),
        famous_works=[
            ("Untitled (Skull)",                         "1981"),
            ("Hollywood Africans",                       "1983"),
            ("Charles the First",                        "1982"),
            ("Riding with Death",                        "1988"),
            ("Trumpet",                                  "1984"),
            ("Self-Portrait",                            "1982"),
            ("Untitled (History of Black People)",       "1983"),
            ("Per Capita",                               "1981"),
        ],
        inspiration=(
            "basquiat_neo_expressionist_scrawl_pass(): ONE HUNDRED AND SIXTIETH "
            "distinct mode -- three-stage neo-expressionist scrawl -- "
            "(1) PER-PIXEL CHANNEL DISCRETE POSTERIZATION: quantize each R, G, B "
            "channel independently to n_levels discrete steps using floor(ch * "
            "n_levels) / n_levels; first pass to apply global per-pixel per-"
            "channel discrete level quantization as a primary colour stage; "
            "de Stael tile mean quantization averages a spatial tile region -- "
            "this quantizes each pixel independently by channel; no prior pass "
            "applies global discrete per-channel rounding as its primary colour "
            "stage; (2) RANDOM DIRECTIONAL CRUDE MARK OVERLAY: generate n_marks "
            "short oriented line-segment rasters at random positions and angles; "
            "for each mark, compute per-pixel distance to the segment within a "
            "local bounding box; darken or brighten pixels within mark_width of "
            "the segment; first pass to build a parametric random field of short "
            "directional line-segment raster marks as an image overlay; "
            "(3) MIDTONE SATURATION AMPLIFICATION: compute per-pixel luminance; "
            "within the midtone luminance window [mid_lo, mid_hi], push each "
            "channel away from its pixel luminance value by sat_boost; first pass "
            "to selectively amplify saturation within a bounded midtone luminance "
            "window while leaving shadows and highlights at their natural "
            "saturation. Best for subjects with strong silhouettes, flat primary "
            "colour areas, and energetic gestural content."
        ),
    ),
"""

with open("art_catalog.py", "r", encoding="utf-8") as f:
    content = f.read()

assert "jean_michel_basquiat" not in content, "already exists"
insert_before = "\n}\n\n\ndef get_style"
assert insert_before in content, "marker not found"
content = content.replace(insert_before, "\n" + BASQUIAT_ENTRY + "}\n\n\ndef get_style", 1)

with open("art_catalog.py", "w", encoding="utf-8") as f:
    f.write(content)

print(f"Done. art_catalog.py new length: {len(content)} chars")
