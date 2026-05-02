"""Insert Camille Pissarro entry into art_catalog.py (session 288).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

PISSARRO_ENTRY = '''
    # ── Camille Pissarro ─────────────────────────────────────────────────────────
    "camille_pissarro": ArtStyle(
        artist="Camille Pissarro",
        movement="Impressionism / Neo-Impressionism",
        nationality="French (born Danish West Indies)",
        period="1830-1903",
        palette=[
            (0.52, 0.62, 0.42),   # sage green -- cool shadow grass, foliage underside
            (0.72, 0.78, 0.58),   # muted yellow-green -- sunlit field, hay
            (0.88, 0.80, 0.55),   # warm straw gold -- high-key sunlit ground
            (0.62, 0.70, 0.75),   # cool slate blue -- sky, atmospheric distance
            (0.78, 0.65, 0.48),   # warm ochre -- earth path, tilled soil
            (0.42, 0.52, 0.48),   # cool muted teal -- shaded water, shadow foliage
            (0.92, 0.86, 0.62),   # pale amber cream -- high sky, sunlit facade
            (0.58, 0.48, 0.38),   # raw umber -- bark, shadow earth, road
            (0.72, 0.58, 0.52),   # dusty rose -- peasant garment, warm twilight
            (0.35, 0.42, 0.36),   # deep shadow green -- interior foliage mass
        ],
        ground_color=(0.78, 0.72, 0.58),  # warm buff linen -- Pissarro's typical ground
        stroke_size=11,
        wet_blend=0.42,
        edge_softness=0.48,
        jitter=0.038,
        glazing=None,
        crackle=False,
        chromatic_split=True,
        technique=(
            "Impressionism / Neo-Impressionism. Camille Pissarro (1830-1903) "
            "was born in Charlotte Amalie, Danish West Indies (now US Virgin Islands), "
            "to a Sephardic Jewish father and Creole mother. He arrived in Paris in 1855 "
            "and became the only painter to exhibit in ALL EIGHT Impressionist exhibitions "
            "(1874-1886), earning him the title 'Dean of the Impressionists.' He was the "
            "patriarch figure who mentored Cézanne, Gauguin, Seurat, and Signac. "
            "His politics were anarchist throughout his life -- his art was inseparable "
            "from his belief in the dignity of rural labour. "
            "PISSARRO'S FIVE DEFINING TECHNICAL SIGNATURES: "
            "(1) DIVISIONIST OPTICAL MIXING: In his mature Neo-Impressionist period "
            "(1885-1891, influenced by Seurat), Pissarro placed discrete touches of "
            "pure pigment side-by-side, relying on the viewer's eye to blend them "
            "optically at distance. Unlike Seurat's rigid dot, Pissarro's touches are "
            "irregular -- comma-shaped, hatched, pointillist -- retaining a handmade "
            "tremor. The mix is not mechanical but organic, each touch slightly different. "
            "(2) COOL SAGE-GREEN SHADOWS: Pissarro's most characteristic shadow note "
            "is a cool sage-green: not the violet shadows of Monet, not the blue-black "
            "of Degas. In fields, orchards, and peasant gardens, his shadow zones carry "
            "a muted green-grey that gives his landscapes their particular freshness. "
            "(3) WARM AMBER ATMOSPHERIC LIGHT: The light in Pissarro's midday and "
            "afternoon landscapes is warm straw-amber: the colour of French sunlight "
            "filtered through humid air, not the blue-white of Riviera light. His high- "
            "key lights are warm rather than cold. "
            "(4) MUTED PALETTE WITH COHERENT HUE FAMILIES: Unlike Fauvists who push "
            "each hue toward its pure spectral extreme, Pissarro's palette has a "
            "characteristic grey-green undertone -- a light atmospheric veil that "
            "gives all colours a unified, slightly muted quality while preserving their "
            "hue identity within their 'family.' His greens are all sage-family; his "
            "ambers are all ochre-family; his blues are all slate-family. "
            "(5) PEASANT SUBJECT HUMANITY: Pissarro's primary subjects are peasant "
            "workers -- women gleaning, men hoeing, children herding geese. The figure "
            "is always embedded in the landscape, never dominant over it; it gives scale "
            "and movement to the field without becoming portraiture. "
            "THE GREAT WORKS: 'Peasant Women Planting Pea Sticks' (1891); "
            "'The Boulevard Montmartre at Night' (1897); 'Harvest at Montfoucault' (1876); "
            "'Apple Picking at Eragny-sur-Epte' (1888); "
            "'La Côte des Boeufs at the Hermitage' (1877); "
            "'The Crystal Palace' (1871); 'Hoarfrost, Peasant Girl Making a Fire' (1888)."
        ),
        famous_works=[
            ("Peasant Women Planting Pea Sticks",         "1891"),
            ("The Boulevard Montmartre at Night",          "1897"),
            ("Harvest at Montfoucault",                    "1876"),
            ("Apple Picking at Eragny-sur-Epte",           "1888"),
            ("La Côte des Boeufs at the Hermitage",        "1877"),
            ("The Crystal Palace",                         "1871"),
            ("Hoarfrost, Peasant Girl Making a Fire",      "1888"),
            ("The Red Roofs, Corner of a Village",         "1877"),
            ("Banks of the Oise near Pontoise",            "1873"),
            ("The Gleaners",                               "1889"),
        ],
        inspiration=(
            "pissarro_divisionist_shimmer_pass(): FOUR-STAGE DIVISIONIST SHIMMER "
            "-- 199th distinct mode. "
            "(1) STOCHASTIC CHROMATIC NEIGHBOR BLEND: For K=6 random displacement "
            "vectors (dy, dx) within dot_radius circle, sample shifted canvas versions "
            "via np.roll; compute per-pixel color distance cdist = sqrt(sum((C-N)^2)); "
            "weight w = exp(-cdist / color_sigma); accumulated weighted average blended "
            "at shimmer_strength. FIRST STOCHASTIC (random-seed-driven) SPATIAL SAMPLING "
            "in engine -- all 198 prior passes use deterministic kernels (Gaussian, "
            "median, Sobel, box). The random neighbor selection introduces controlled "
            "optical mixing variability that mimics pointillist color vibration. "
            "(2) COOL SAGE-GREEN SHADOW: gate = smoothstep(lum, shadow_hi=0.38, shadow_lo=0.22); "
            "push R,G,B toward (0.36/0.52/0.38); weighted by gate. Pissarro's "
            "characteristic cool-green shadow tone, distinct from violet (Monet), "
            "blue-grey (Hammershoi), or warm umber (Repin). "
            "(3) WARM AMBER HIGHLIGHT: gate = smoothstep(lum, hi_lo=0.68, hi_hi=0.85); "
            "push toward (0.94/0.86/0.58) warm straw-amber. Pissarro's atmospheric "
            "warmth in high-key zones. "
            "(4) SECTOR-MEDIAN HUE COHERENCE: Convert to HSV; divide H into 12 sectors "
            "of 30 degrees; for each sector compute median H within sector; "
            "H_new = H + (H_med - H) * coherence * S_weight; convert back. "
            "FIRST PASS to normalize hue toward per-sector data-driven medians -- "
            "creates intra-sector hue family coherence. Derain Stage 2 pushes toward "
            "fixed spectral targets (red/green/blue); the present stage uses the IMAGE'S "
            "OWN sector median (data-driven, not fixed palette), creating organic "
            "coherence within each hue range."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

assert "camille_pissarro" not in src, "camille_pissarro already exists in art_catalog.py"

ANCHOR = "\n\n}\n\n\ndef get_style"
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, PISSARRO_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: camille_pissarro entry inserted.")
