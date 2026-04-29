"""Insert francis_bacon entry into art_catalog.py (session 251).

NOTE: This script was already executed during session 251. Running it again
will fail the assertion check. It is preserved as a record of the change.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))

BACON_ENTRY = """    "francis_bacon": ArtStyle(
        artist="Francis Bacon",
        movement="Figurative Expressionism",
        nationality="Irish-British",
        period="1909-1992",
        palette=[
            (0.62, 0.28, 0.08),
            (0.84, 0.44, 0.18),
            (0.42, 0.18, 0.12),
            (0.90, 0.86, 0.72),
            (0.06, 0.08, 0.42),
            (0.08, 0.10, 0.08),
            (0.22, 0.44, 0.24),
            (0.72, 0.52, 0.32),
            (0.88, 0.30, 0.12),
            (0.48, 0.46, 0.52),
        ],
        ground_color=(0.88, 0.82, 0.68),
        stroke_size=18,
        wet_blend=0.28,
        edge_softness=0.40,
        jitter=0.22,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Francis Bacon (1909-1992) was born in Dublin to English parents and "
            "arrived in London in the 1920s, initially working as an interior "
            "decorator before arriving at painting without formal training in the "
            "early 1930s. His breakthrough came with Three Studies for Figures at "
            "the Base of a Crucifixion (1944). See catalog entry for full technique."
        ),
        famous_works=[
            ("Three Studies for Figures at the Base of a Crucifixion", "1944"),
            ("Study after Velazquez's Portrait of Pope Innocent X",     "1953"),
            ("Three Studies for a Self-Portrait",                       "1979"),
            ("Triptych May-June 1973",                                  "1973"),
            ("Figure with Meat",                                        "1954"),
        ],
        inspiration="bacon_isolated_figure_pass(): 162nd distinct mode",
    ),
"""

catalog_path = os.path.join(REPO, "art_catalog.py")
with open(catalog_path, "r", encoding="utf-8") as f:
    content = f.read()

assert "francis_bacon" not in content, "francis_bacon already exists -- already applied"
insert_before = "\n}\n\n\ndef get_style"
assert insert_before in content, "marker not found in art_catalog.py"
content = content.replace(insert_before, "\n" + BACON_ENTRY + "}\n\n\ndef get_style", 1)

with open(catalog_path, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Done. art_catalog.py new length: {len(content)} chars")