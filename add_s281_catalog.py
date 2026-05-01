"""Insert Ivan Shishkin entry into art_catalog.py (session 281).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

SHISHKIN_ENTRY = '''
    # ── Ivan Shishkin ─────────────────────────────────────────────────────────
    "ivan_shishkin": ArtStyle(
        artist="Ivan Shishkin",
        movement="Russian Realism / Peredvizhniki / Naturalist Landscape",
        nationality="Russian",
        period="1832-1898",
        palette=[
            (0.28, 0.34, 0.18),   # deep forest shadow green -- receding pine canopy
            (0.42, 0.50, 0.22),   # sunlit mid-canopy green -- lit pine clusters
            (0.62, 0.48, 0.24),   # warm amber bark -- sun-facing trunk surface
            (0.32, 0.24, 0.14),   # dark umber bark -- shadow side of trunks
            (0.72, 0.62, 0.38),   # golden afternoon light -- sky/canopy glow
            (0.52, 0.34, 0.14),   # raw umber forest floor -- earth and needle litter
            (0.50, 0.58, 0.64),   # cool haze blue-gray -- distant forest atmosphere
            (0.24, 0.28, 0.20),   # dark forest recess -- deep shadow between trunks
            (0.68, 0.60, 0.42),   # warm sandy path -- forest clearing, sandy soil
            (0.46, 0.54, 0.34),   # muted sage canopy -- mid-distance pine foliage
        ],
        ground_color=(0.42, 0.32, 0.18),     # warm earth ochre ground (forest floor)
        stroke_size=10,
        wet_blend=0.18,
        edge_softness=0.14,
        jitter=0.022,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Russian Realism, Peredvizhniki, Naturalist Landscape. "
            "Ivan Ivanovich Shishkin (1832-1898) was born in Yelabuga (now "
            "Tatarstan) to a merchant family with an interest in local history "
            "and natural science. He studied at the Moscow School of Painting, "
            "then at the Imperial Academy of Arts in St. Petersburg, and "
            "subsequently in Dusseldorf under the Swiss landscape painter "
            "Rudolf Calame -- a training that gave him an almost scientific "
            "command of natural forms. He was a founding member of the "
            "Peredvizhniki (Wanderers) alongside Repin, Kramskoi, and "
            "Savitsky, and became the group's preeminent landscape specialist. "
            "SHISHKIN'S THREE TECHNICAL OBSESSIONS: "
            "(1) BARK TEXTURE: Shishkin rendered the vertical grain, "
            "horizontal shadow bands, warm amber lit surfaces, and cool "
            "lichen-covered shadow sides of mature Russian pine bark with "
            "a specificity unprecedented in landscape painting. His trunks "
            "are almost architectural -- structural, material, and weight-bearing. "
            "(2) DAPPLED CANOPY LIGHT: Light filtering through a pine canopy "
            "creates irregular alternating zones of bright sunlit needles and "
            "deep cool shadow. Shishkin rendered this as a mosaic of carefully "
            "observed values, never smoothing the complexity into generic green "
            "masses. His canopies have a density and layered intricacy visible "
            "even in photographs of his finished paintings. "
            "(3) FOREST ATMOSPHERE: Despite his documentary precision, Shishkin's "
            "forests have palpable atmosphere: cool blue-green haze in the deeper "
            "recesses, warm amber glow where the forest floor catches late afternoon "
            "sun, the sense of moist resinous air between the trunks. He achieved "
            "this through careful value management: very dark accents in the deepest "
            "shadow recesses, very warm lights on sun-facing bark, and graduated "
            "cool recession into depth. "
            "RUSSIAN FOREST PALETTE: Deep shadow greens (nearly neutral), warm "
            "amber bark, cool umber shadow-side bark, golden afternoon light at "
            "the canopy edge, warm sandy ochre at the forest floor, and cool "
            "blue-gray atmospheric haze in the receding distance. "
            "PEREDVIZHNIKI INFLUENCE: The Wanderers' commitment to painting "
            "Russia's actual landscape -- not idealized Italianate scenery -- "
            "gave Shishkin's subject matter its specificity. He painted the "
            "forests of Vyatka Province, Valaam Island, and the Baltic coast "
            "with the same documentary faithfulness he brought to individual trees. "
            "SIGNATURE WORKS: Pine Forest (1872); Rye (1878); Morning in a Pine "
            "Forest (1889, bears by Konstantin Savitsky); Ship Grove (1898); "
            "Pine on the Rock (1860); In the Wild North (1891); Forest in the "
            "Kuntsevo District (1877); Oak Grove (1887)."
        ),
        famous_works=[
            ("Pine Forest",                      "1872"),
            ("Rye",                              "1878"),
            ("Morning in a Pine Forest",         "1889"),
            ("Ship Grove",                       "1898"),
            ("Pine on the Rock",                 "1860"),
            ("In the Wild North",                "1891"),
            ("Forest in the Kuntsevo District",  "1877"),
            ("Oak Grove",                        "1887"),
            ("Midday. Environs of Moscow",       "1869"),
            ("Forest Distances",                 "1884"),
        ],
        inspiration=(
            "shishkin_forest_density_pass(): FOUR-STAGE FOREST INTERIOR SYSTEM "
            "-- 192nd distinct mode. "
            "(1) VERTICAL BARK TEXTURE ANISOTROPY: purely vertical anisotropic "
            "mean filter (kernel ~22:2 height:width aspect ratio); first pass "
            "to use a single-orientation vertical kernel for bark grain simulation "
            "rather than turbulent velocity field or multiple orientations. "
            "(2) CANOPY LIGHT DAPPLING: local luminance variance "
            "(E[L^2] - E[L]^2) as dappled-light proxy; high-variance pixels "
            "are in light/shadow transition zones; push toward warm sunlit "
            "foliage yellow-green; first pass to use LOCAL VARIANCE as a "
            "zone-selection gate rather than absolute luminance or gradient. "
            "(3) FOREST FLOOR SHADOW WARMTH: shadow-zone push toward warm "
            "forest earth ochre (0.52/0.34/0.14); shadow-zone warm push "
            "distinct from prior passes (Fechin: midtone sienna; Goya: "
            "deep umber dark reinforcement; depth_atmosphere: cool haze). "
            "(4) DESATURATION-GATED COOL FOREST HAZE: per-pixel saturation "
            "S=(C_max-C_min)/C_max computed, smoothed; low-saturation zones "
            "pushed toward cool blue-green forest haze (0.50/0.58/0.64); first "
            "pass to gate cool push on DESATURATION rather than vertical "
            "position, luminance zone, or local contrast."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

# Verify no duplicate
assert "ivan_shishkin" not in src, "ivan_shishkin already exists in art_catalog.py"

# Insert before the closing brace of CATALOG dict
ANCHOR = "\n\n}\n\n\ndef get_style"
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, SHISHKIN_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: ivan_shishkin entry inserted.")
