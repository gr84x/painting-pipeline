"""Insert Theodor Kittelsen entry into art_catalog.py (session 271).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

KITTELSEN_ENTRY = '''
    # ── Theodor Kittelsen ────────────────────────────────────────────────────
    "theodor_kittelsen": ArtStyle(
        artist="Theodor Kittelsen",
        movement="Norwegian Romantic Realism / Folk Illustration",
        nationality="Norwegian",
        period="1857-1914",
        palette=[
            (0.06, 0.08, 0.22),   # deep prussian blue-violet -- dark water / forest shadow
            (0.72, 0.74, 0.78),   # pale silver-grey -- atmospheric mist / fog
            (0.85, 0.70, 0.40),   # amber-gold -- twilight horizon sky
            (0.12, 0.10, 0.08),   # deep umber -- near foreground vegetation / peat
            (0.45, 0.52, 0.68),   # cool blue-grey -- mid-sky / reflected water
            (0.88, 0.88, 0.86),   # near-white silver -- birch bark / moonlit snow
            (0.08, 0.12, 0.10),   # forest-green-black -- conifer silhouettes
            (0.80, 0.55, 0.35),   # warm rose-amber -- horizon glow water reflection
            (0.30, 0.32, 0.50),   # cool slate-violet -- distant hillside in mist
        ],
        ground_color=(0.16, 0.14, 0.12),     # dark peat-umber ground
        stroke_size=18,
        wet_blend=0.22,                       # moderate wet blend for atmospheric softness
        edge_softness=0.30,                   # soft edges in mist zones, hard at silhouettes
        jitter=0.040,                         # moderate jitter -- painterly Nordic roughness
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Norwegian Romantic Realism and Folk Illustration. Theodor Kittelsen "
            "(1857-1914) spent the greater part of his working life immersed in "
            "the Norwegian wilderness -- above Vøringsfossen, beside Tyrifjorden, "
            "deep in the Telemark forests and on the Ringerike plateau. His "
            "painting and illustration grew directly from this landscape and from "
            "his intimate knowledge of Norwegian folk tradition (Asbjørnsen and "
            "Moe's Norske Folkeeventyr provided the literary world; Kittelsen "
            "provided its definitive visual form). He is the painter of the Norwegian "
            "troll, the nisse, the draugen, and the huldr -- but also of the most "
            "quietly devastating atmospheric landscapes in Scandinavian art: 'Soria "
            "Moria Castle' (1900), the 'Black Death' series (1900), the troll "
            "paintings of the 1890s, and the extraordinary bog-and-birch twilight "
            "paintings of his Snøasen period. The dominant structural principle of "
            "his landscapes is SILHOUETTE OPPOSITION: near elements (birch trunks, "
            "heather, boulders, trolls) are cut as near-black shapes against far "
            "elements (sky, mist, water surface) that are dramatically brighter. "
            "The near/far boundary is almost always hard -- a razor edge of dark "
            "against light. His atmospheric zones (sky, fog, still water) are "
            "characterised by simultaneous high luminance AND low local variance: "
            "smooth, featureless zones of soft colour against which the near "
            "silhouettes are read. His shadow zones carry a deep blue-violet "
            "quality -- the colour of cold still water, moonlit stone, peat bog "
            "at dusk -- that pulls even the darkest passages away from neutral "
            "black and into a register of depth and cold. Palette: prussian "
            "blue-violet (deep water/shadow), amber-gold (twilight horizon), "
            "pale silver-grey (mist/fog), near-black umber (foreground), cool "
            "blue-grey (sky/water), silver (birch bark)."
        ),
        famous_works=[
            ("Soria Moria Castle",            "1900"),
            ("The Black Death on the Stairs", "1900"),
            ("Nøkken",                         "1904"),
            ("Troll",                          "1892"),
            ("The Plague",                    "1900"),
            ("Princess in the Blue Mountain", "1900"),
            ("Fossegrimen",                   "1887"),
            ("Huldra Disappears into the Mountain", "1906"),
        ],
        inspiration=(
            "kittelsen_nordic_mist_pass(): FOUR-STAGE ATMOSPHERIC TWILIGHT TECHNIQUE "
            "-- 182nd distinct mode. "
            "(1) CONTENT-ADAPTIVE FAR ZONE DETECTION: compute local luminance variance "
            "via gaussian(L^2)-gaussian(L)^2 at variance_sigma; detect far/mist zones "
            "as pixels with luminance in [far_lum_low, far_lum_high] AND local variance "
            "below 35th-percentile threshold -- joint luminance-range AND variance "
            "condition, not positional gradient; first pass to detect atmospheric zones "
            "via this joint content-adaptive test; "
            "(2) ATMOSPHERIC HAZE TINT IN FAR ZONES: blend far zones toward cool "
            "prussian blue-grey (haze_r, haze_g, haze_b) at luminance-modulated "
            "strength -- brighter far-zone pixels receive stronger haze tint; "
            "(3) SILHOUETTE EDGE CONTRAST HARDENING: compute gradient of far-zone "
            "mask, at zone boundaries darken near side and lighten far side; first "
            "pass to derive silhouette contrast from zone-mask gradient rather than "
            "pixel-value edge detector; "
            "(4) DEEP SHADOW BLUE-VIOLET UNDERLAYER: detect deep shadows (L < "
            "dark_threshold) and blend toward prussian blue-violet color; strength "
            "proportional to shadow depth; recreates Kittelsen's characteristic cold "
            "blue-violet in dark forest, bog, and water zones."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"theodor_kittelsen"' in src:
    print("theodor_kittelsen already in catalog -- nothing to do.")
    sys.exit(0)

INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + KITTELSEN_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Theodor Kittelsen into art_catalog.py.")
