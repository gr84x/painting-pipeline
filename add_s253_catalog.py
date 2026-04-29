"""Insert anselm_kiefer entry into art_catalog.py (session 253).

NOTE: This script was already executed during session 253. Running it again
will fail the assertion check. It is preserved as a record of the change.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))

KIEFER_ENTRY = """    "anselm_kiefer": ArtStyle(
        artist="Anselm Kiefer",
        movement="Neo-Expressionism / Conceptual Art",
        nationality="German",
        period="1945–present",
        palette=[
            (0.26, 0.24, 0.22),   # oxidized lead grey-black
            (0.52, 0.46, 0.38),   # scorched umber ash
            (0.78, 0.70, 0.28),   # dry straw gold
            (0.38, 0.34, 0.30),   # charcoal mid-grey
            (0.88, 0.84, 0.76),   # pale ashen white
            (0.58, 0.38, 0.18),   # rust iron-oxide red
            (0.22, 0.28, 0.20),   # dark forest shadow-green
            (0.66, 0.60, 0.52),   # warm dull lead
            (0.42, 0.38, 0.32),   # earth brown
            (0.14, 0.12, 0.10),   # near-black char
        ],
        ground_color=(0.44, 0.40, 0.34),
        stroke_size=42,
        wet_blend=0.38,
        edge_softness=0.42,
        jitter=0.22,
        glazing=None,
        crackle=True,
        chromatic_split=False,
        technique=(
            "Anselm Kiefer (born 1945, Donaueschingen, Germany) is one of the "
            "most significant painters to emerge from post-war Europe, creating "
            "vast, heavily material paintings that confront Germany's history, "
            "mythology, religion, and mystical traditions. He studied under "
            "Joseph Beuys and absorbed Beuys's belief in the transformative power "
            "of material — but where Beuys used fat and felt, Kiefer uses lead, "
            "straw, sand, ash, wire, seed husks, crushed glass, and shellac. "
            "His canvases (often measuring several metres) are not painted so "
            "much as built — physical deposits of matter embedded in and over "
            "painted surfaces, creating geological strata of material history. "
            "Three central technical signatures define Kiefer's work: "
            "(1) SCORCHED FIELD PERSPECTIVE -- most paintings establish a deep, "
            "aerial-perspective landscape with a low horizon and a vast ploughed, "
            "burned, or snow-covered field filling the lower two-thirds of the "
            "canvas; the field converges on a narrow horizon and sky beyond; this "
            "structure is simultaneously a German Romantic landscape (Friedrich's "
            "vast terrain) and a scorched historical wound; the ashen, charcoal, "
            "and straw tones drain the landscape of pastoral beauty and fill it "
            "with residue; (2) LEAD AND STRAW INCORPORATION -- Kiefer's canvases "
            "physically hold matter; straw is embedded in the painted surface in "
            "diagonal lines suggesting ploughed furrows or fallen soldiers; lead "
            "sheets are applied flat or crumpled over painted areas, their "
            "grey metallic surface cracking over time into distinctive veining "
            "patterns; the lead is not used symbolically alone but for its "
            "material weight, its resistance to decay, its association with "
            "alchemy and Saturn; (3) TEXTUAL AND MYTHOLOGICAL INSCRIPTION -- "
            "titles, names, and fragments of text appear directly on the surface "
            "in thick impasto or scratched through paint layers; Norse myth "
            "(Wotan, Siegfried), Kabbalah (the Tree of Life, the Sephirot), "
            "and German Romantic poetry (Celan's 'Todesfuge') are embedded as "
            "direct material presence; the meaning is not illustrative but "
            "archaeological -- as if the paintings are surfaces dug from cultural "
            "sediment."
        ),
        famous_works=[
            ("Ways of Worldly Wisdom",               "1976"),
            ("Sulamith",                              "1983"),
            ("The Orders of the Night",               "1996"),
            ("Breaking of the Vessels",               "1990"),
            ("Sternenfall (Falling Stars)",           "1995"),
            ("Your Golden Hair, Margarete",           "1981"),
            ("The Heavenly Palaces",                  "2004"),
            ("Occupations",                           "1969"),
        ],
        inspiration=(
            "kiefer_scorched_earth_pass(): ONE HUNDRED AND SIXTY-FOURTH "
            "(164th) distinct mode -- three-stage scorched field with straw "
            "and lead -- "
            "(1) ASHEN FIELD DESATURATION GRADIENT: divide the canvas into "
            "n_zones horizontal depth strips; for each zone apply a "
            "zone-fraction-weighted blend toward an ash grey tone; gate the "
            "desaturation by pixel luminance so dark pixels are pushed charcoal, "
            "mid-tones become ash, lights retain edge chroma; first pass to "
            "apply zone-partitioned luminance-gated simultaneous desaturation "
            "and darkening in a gradient from foreground to horizon; "
            "(2) LEAD SHEET CRACK VEINING: trace n_cracks sinusoidal "
            "trajectories across the canvas with random phase, frequency, and "
            "amplitude; darken pixels within crack_width of each trajectory by "
            "crack_depth toward crack_tone where lum < lum_ceiling; first pass "
            "to generate network crack-path veinings as composites of "
            "sinusoidal directional vein paths with luminance-gated "
            "discontinuity; "
            "(3) STRAW FIBER WARM OVERLAY: at mid-luminance pixels (straw_lo "
            "to straw_hi lum), apply a tilted sinusoidal fiber texture oriented "
            "at straw_angle degrees from horizontal, coloured with warm straw "
            "gold (0.76, 0.68, 0.28) at fiber_strength; first pass to apply a "
            "rotated single-direction chromatic sinusoidal fiber texture gated "
            "on mid-luminance regions."
        ),
    ),
"""

CATALOG_FILE = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_FILE, "r", encoding="utf-8") as f:
    src = f.read()

assert "anselm_kiefer" not in src, "anselm_kiefer already present in art_catalog.py"

INSERT_BEFORE = '    "gerhard_richter":'
assert INSERT_BEFORE in src, f"Anchor {INSERT_BEFORE!r} not found in art_catalog.py"

new_src = src.replace(INSERT_BEFORE, KIEFER_ENTRY + INSERT_BEFORE)

with open(CATALOG_FILE, "w", encoding="utf-8") as f:
    f.write(new_src)

print("anselm_kiefer entry inserted into art_catalog.py")
