"""Insert Wayne Thiebaud entry into art_catalog.py (session 276).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

THIEBAUD_ENTRY = '''
    # ── Wayne Thiebaud ────────────────────────────────────────────────────────
    "wayne_thiebaud": ArtStyle(
        artist="Wayne Thiebaud",
        movement="American Figurative / Sacramento School",
        nationality="American",
        period="1920-2021",
        palette=[
            (0.97, 0.94, 0.85),   # warm cream-white -- lit ground and halo
            (0.94, 0.74, 0.56),   # peach-ochre -- warm direct light on objects
            (0.86, 0.52, 0.54),   # salmon-rose -- characteristic colored shadow
            (0.72, 0.55, 0.74),   # warm violet -- deep colored shadow zone
            (0.98, 0.82, 0.42),   # yellow-gold -- lemon meringue / custard light
            (0.56, 0.80, 0.78),   # cool mint -- ice cream / icing complement
            (0.30, 0.18, 0.12),   # deep umber -- contour line and cast shadow
            (0.88, 0.62, 0.32),   # orange-amber -- warm light source
            (0.76, 0.88, 0.64),   # pale chartreuse -- lime/pistachio accent
            (0.95, 0.95, 0.95),   # near-white -- luminous table ground
        ],
        ground_color=(0.96, 0.93, 0.88),     # warm off-white ground
        stroke_size=10,
        wet_blend=0.28,
        edge_softness=0.08,
        jitter=0.028,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Chromatic halo shadows. Wayne Thiebaud (1920-2021) was an American "
            "painter associated with the Sacramento School and the commercial-subject "
            "figurative tradition that emerged alongside Pop Art in the early 1960s. "
            "Although his subject matter -- pie slices, ice cream scoops, diner counters, "
            "candy apples, lipsticks, and deli food displays -- superficially resembles "
            "Pop Art\'s appropriation of consumer culture, Thiebaud\'s project was always "
            "fundamentally painterly: he was interested in the light, color, and material "
            "surface of these familiar objects, not in their cultural meaning. "
            "His paintings are deeply influenced by Vermeer\'s treatment of light on "
            "surfaces, Chardin\'s still-life gravity, Degas\'s color, and the Abstract "
            "Expressionist understanding of paint as material. "
            "HALO SHADOW TECHNIQUE: Thiebaud\'s most recognizable signature is the "
            "chromatic halo that surrounds objects. On the lit side of an object, he "
            "applies a warm cream-white zone of heightened brightness -- an inner light "
            "halo. On the shadow side, instead of neutral grey, he applies a vivid "
            "chromatic shadow: pink, salmon, orange, or violet depending on the painting\'s "
            "light color. This colored shadow follows the Chevreul/Delacroix principle "
            "that shadows contain the complement of the light source, but Thiebaud "
            "exaggerates the saturation far beyond naturalistic observation. "
            "IMPASTO TECHNIQUE: Paint is applied thickly, often with a loaded palette "
            "knife for frosting and icing passages, with visible stroke ridges. "
            "SIGNATURE WORKS: Display Cakes (1963) -- three cake slices on white with "
            "vivid pink-orange shadow halos; Pies Pies Pies (1961) -- row of pie slices "
            "with luminous white-cream grounds; Encased Cakes (1961); Deli (1994); "
            "Sunset Streets (1985) -- San Francisco streets as colored planes."
        ),
        famous_works=[
            ("Display Cakes",              "1963"),
            ("Pies Pies Pies",             "1961"),
            ("Encased Cakes",              "1961"),
            ("Three Machines",             "1963"),
            ("Refrigerator Pies",          "1962"),
            ("Deli",                       "1994"),
            ("Sunset Streets",             "1985"),
            ("Downgrade",                  "2001"),
            ("Ripley Ridge",               "1977"),
            ("Lemon Meringue Pie",         "1964"),
        ],
        inspiration=(
            "thiebaud_halo_shadow_pass(): THREE-STAGE CHROMATIC BILATERAL "
            "HALO EXPANSION -- 187th distinct mode. "
            "(1) LUMINANCE GRADIENT EDGE DETECTION WITH LIT/SHADOW SIDE LABELING: "
            "Sobel gradient after Gaussian smoothing identifies object boundaries; "
            "each edge pixel is labeled lit-side (L >= local mean) or shadow-side; "
            "first pass to apply DIRECTIONALLY ASYMMETRIC bilateral expansion from "
            "detected edges. "
            "(2) LIT-SIDE HALO EXPANSION: decay-weighted radial dilation into the "
            "brighter side of each edge; warm cream-white tint applied; simulates "
            "Thiebaud\'s luminous inner light halo around objects. "
            "(3) SHADOW-SIDE CHROMATIC EXPANSION: decay-weighted radial dilation "
            "into the darker side; warm pink-violet tint applied; simulates "
            "Thiebaud\'s characteristic colored shadow (complement of light source). "
            "(4) CONTOUR REINFORCEMENT: edge pixels darkened to separate halo from "
            "shadow zone with a thin boundary line."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

ANCHOR = '    # ── Arshile Gorky'
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, THIEBAUD_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: wayne_thiebaud entry inserted.")
