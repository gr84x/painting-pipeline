"""Insert joan_mitchell entry into art_catalog.py (session 250)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

MITCHELL_ENTRY = """    "joan_mitchell": ArtStyle(
        artist="Joan Mitchell",
        movement="Abstract Expressionism",
        nationality="American",
        period="1925-1992",
        palette=[
            (0.14, 0.36, 0.72),
            (0.22, 0.54, 0.28),
            (0.92, 0.84, 0.18),
            (0.82, 0.26, 0.18),
            (0.90, 0.88, 0.84),
            (0.14, 0.12, 0.10),
            (0.68, 0.30, 0.64),
            (0.62, 0.80, 0.88),
            (0.88, 0.58, 0.22),
            (0.38, 0.64, 0.30),
        ],
        ground_color=(0.92, 0.90, 0.84),
        stroke_size=22,
        wet_blend=0.38,
        edge_softness=0.22,
        jitter=0.18,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Joan Mitchell (1925-1992) was born in Chicago into a privileged "
            "literary family -- her mother was the founder of Poetry magazine -- "
            "and trained at the Art Institute of Chicago and the School of the "
            "Art Institute before arriving in New York in 1950, where she became "
            "one of the few women fully integrated into the first generation of "
            "Abstract Expressionists, exhibiting alongside de Kooning, Kline, and "
            "Guston at the Cedar Tavern and the Club. In 1955 she moved to France, "
            "eventually settling permanently at Vetheuil on the Seine near Monet's "
            "garden at Giverny in 1968, where she produced the large-scale, "
            "polyptych-format paintings of her mature period. Mitchell's paintings "
            "are not abstract in the sense of having no external referent -- she "
            "maintained that her work was always about something: the memory of a "
            "place, the energy of a landscape, the feeling of a particular light "
            "at a particular time. She called her paintings 'remembered landscapes'. "
            "Her technical signature: (1) LARGE-ARC GESTURAL SWEEP -- Mitchell "
            "painted at full arm extension with a large brush, the marks following "
            "the arc of the arm's natural movement; marks are long, curved, "
            "rhythmic, and physically committed; they carry the velocity of the "
            "body through the paint; (2) ALL-OVER INTENSITY WITH DENSE AND SPARSE "
            "ZONES -- Mitchell did not use conventional figure/ground hierarchy; "
            "the canvas surface is activated everywhere, but with varying density: "
            "areas of dense impasto alternate with zones where the white ground "
            "shows through thinly; this rhythm of fullness and emptiness creates "
            "the breathing quality of her compositions; (3) CHROMATIC VOLTAGE -- "
            "Mitchell used colours that should clash and somehow do not; cobalt "
            "blue against viridian against cadmium yellow against alizarin crimson "
            "-- the combinations are extreme and the relationships work because the "
            "marks carry enough gestural energy to fuse them; (4) WET-INTO-WET "
            "BLENDING -- Mitchell worked on large canvases with paint that was "
            "often still wet, so adjacent marks blend at their boundaries; the "
            "transition between a blue mark and a yellow adjacent mark is not a "
            "hard line but a soft zone of green where they met; (5) POLYPTYCH "
            "SCALE -- in her mature work, Mitchell worked across multiple conjoined "
            "panels; the composition does not end but continues across the joins; "
            "each panel has its own internal logic but participates in a larger "
            "orchestration."
        ),
        famous_works=[
            ("Ladybug",                                      "1957"),
            ("George Went Swimming at Barnes Hole, but It Got Too Cold", "1957"),
            ("City Landscape",                               "1955"),
            ("Grandes Carrieres",                            "1961"),
            ("Chasse Interdite",                             "1973"),
            ("La Grande Vallee (series)",                    "1983"),
            ("Sunflowers",                                   "1990"),
            ("Ici",                                          "1992"),
        ],
        inspiration=(
            "mitchell_gestural_arc_pass(): ONE HUNDRED AND SIXTY-FIRST "
            "distinct mode -- three-stage gestural lyric arc -- "
            "(1) LARGE CIRCULAR ARC GESTURAL MARKS: generate n_arcs circular arc "
            "marks each defined by a random centre (cx, cy), radius r, start "
            "angle, arc span, and mark width; render by computing per-pixel "
            "minimum angular distance to the nearest arc point within the span; "
            "apply brightness_shift within width/2 of the arc; first pass to "
            "rasterize gestural overlay marks as curved circular arc segments "
            "rather than straight line segments; Basquiat marks (s249) use "
            "straight segment rasters; Kline gestural slash (s119) uses "
            "calligraphic mega-strokes derived from luminance gradient orientation "
            "-- neither parameterizes marks as curved circular arcs; "
            "(2) WET-SPREAD DIRECTIONAL COLOUR BLEED: detect high-saturation "
            "pixels (saturated paint marks); for each such pixel compute a "
            "direction toward the local colour centroid gradient; apply an "
            "anisotropic Gaussian blur along that direction to simulate wet paint "
            "spreading into adjacent areas; first pass to apply a saturation-gated "
            "anisotropic colour bleed: spreading only from highly saturated pixels "
            "using per-pixel directional blur alignment; no prior pass applies "
            "saturation-gated directional spreading as its primary blending stage; "
            "(3) MARK DENSITY SATURATION RHYTHM: using the arc density map "
            "computed in stage 1 (count of arc marks that pass within influence "
            "radius of each pixel), boost saturation in dense-mark zones and "
            "allow saturation to recede in sparse zones; first pass to modulate "
            "saturation by a spatially derived mark density field from the "
            "gestural mark overlay, creating the dense-sparse rhythmic alternation "
            "of Abstract Expressionist all-over composition; prior saturation "
            "passes (chroma_focus: radial; Basquiat midtone: luminance-gated) "
            "use geometric or luminance criteria rather than mark-density. Best "
            "for non-representational, all-over, high-energy subjects; landscape "
            "memory; large-format compositions with rhythmic colour fields."
        ),
    ),
"""

with open("art_catalog.py", "r", encoding="utf-8") as f:
    content = f.read()

assert "joan_mitchell" not in content, "joan_mitchell already exists in catalog"
insert_before = "\n}\n\n\ndef get_style"
assert insert_before in content, "marker not found in art_catalog.py"
content = content.replace(insert_before, "\n" + MITCHELL_ENTRY + "}\n\n\ndef get_style", 1)

with open("art_catalog.py", "w", encoding="utf-8") as f:
    f.write(content)

print(f"Done. art_catalog.py new length: {len(content)} chars")
