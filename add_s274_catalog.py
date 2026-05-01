"""Insert Isaak Levitan (s274) into art_catalog.py.

Run once; preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

LEVITAN_ENTRY = '''
    # ── Isaak Levitan ─────────────────────────────────────────────────────────
    "isaak_levitan": ArtStyle(
        artist="Isaak Levitan",
        movement="Russian Lyrical Impressionism / Peredvizhniki",
        nationality="Russian (born in Kibartai, Lithuania)",
        period="1880–1900",
        palette=[
            (0.82, 0.68, 0.28),   # golden birch ochre — the defining Levitan autumn
            (0.72, 0.56, 0.22),   # deep ochre-amber — mature autumn foliage
            (0.48, 0.38, 0.20),   # warm dark umber — birch shadow, wet ground
            (0.24, 0.34, 0.45),   # cool water-sky blue-grey
            (0.42, 0.52, 0.60),   # overcast Russian sky — cool pewter blue
            (0.62, 0.60, 0.50),   # warm horizon mist — golden-grey at sunset
            (0.78, 0.74, 0.62),   # pale birch trunk — creamy warm white
            (0.12, 0.18, 0.14),   # dark conifer — almost black pine-green
            (0.52, 0.48, 0.36),   # autumn grass — dried, pale, warm
            (0.32, 0.42, 0.38),   # still water reflection — deep, slightly green
        ],
        ground_color=(0.58, 0.52, 0.38),    # warm buff — toned linen ground
        stroke_size=11,
        wet_blend=0.72,
        edge_softness=0.68,
        jitter=0.08,
        glazing=(0.62, 0.58, 0.42),         # warm golden atmospheric glaze
        crackle=False,
        chromatic_split=False,
        technique=(
            "Russian Lyrical Impressionism. Isaak Levitan (1860-1900) was the supreme "
            "poet of the Russian landscape -- a painter who transformed the vast, flat, "
            "melancholy terrain of Russia into an art of intimate emotional intensity. "
            "His mature work belongs to a tradition he essentially invented: the "
            "LYRICAL LANDSCAPE, in which the external scene is a vehicle for an "
            "internal emotional state. Levitan himself called this \'mood painting\' "
            "(nastroenie), and it was this quality -- the sense of a painting that "
            "looks out at the world and feels -- that set him apart from the documentary "
            "realism of his Peredvizhniki contemporaries. "
            "Levitan was a student and protege of Savrasov (whose \'The Rooks Have "
            "Arrived\' established the tradition of lyrical Russian landscape), but "
            "he radicalized Savrasov\'s approach under the influence of French "
            "Impressionism, which he encountered on his travels to Western Europe. "
            "The resulting synthesis -- Impressionist colour sensitivity, loose "
            "facture, and atmospheric light effects, applied to the Russian landscape "
            "with a deeply Slavic emotional register -- is entirely his own. "
            "AUTUMN: Levitan\'s autumn paintings are his most celebrated. \'Golden "
            "Autumn\' (1895) shows a river turning a bend through birch-lined banks: "
            "the gold is so saturated, so intensely joyful, that it reads almost as "
            "grief -- joy at maximum before the cold arrives. \'March\' (1895) shows "
            "the first spring thaw, with golden tree trunks catching afternoon sun "
            "against blue shadows in the snow: a painting of pure warm-cool "
            "temperature contrast. These autumn works use a WARM-COOL SPLIT that is "
            "their technical foundation: warm golden foliage and warm light against "
            "cool blue-grey sky, shadow, and water. The warm-cool boundary is not "
            "sharp (Levitan uses soft transitions) but is present in every passage. "
            "REFLECTIVE WATER: Levitan\'s lakes and rivers are among the most "
            "beautiful reflective surfaces in Western painting. \'Quiet Abode\' "
            "(1890), \'Birch Grove\' (1885-1889), \'Above Eternal Peace\' (1894): "
            "all feature still water that mirrors the sky and trees above, slightly "
            "darkened and desaturated by the water\'s partial absorption. The "
            "reflections are never perfect mirrors -- Levitan introduces a subtle "
            "ripple or softening that makes them feel wet rather than glassy. "
            "TECHNICAL APPROACH: Levitan worked in layers: a transparent imprimatura "
            "(often warm ochre-buff on a fine linen canvas), blocked in with broad "
            "opaque strokes establishing the major tonal zones, then built up with "
            "increasingly specific strokes. His autumn foliage is painted with "
            "DIRECTIONAL IMPASTO -- small, loaded strokes following the direction "
            "of leaf growth, applied over a dry ground. The sky is worked wet-into-wet "
            "with broad, smooth strokes. The atmospheric quality of his distances is "
            "achieved through a thin warm GLAZE over the mid-distance (trees, far "
            "bank), which unifies without covering. "
            "CHROMATIC WARMTH DIFFUSION: The most characteristic optical quality "
            "of Levitan\'s autumn paintings is the way warm colors \'glow\' -- the "
            "golden birch foliage seems to radiate warmth into adjacent cool areas. "
            "The sky immediately above a golden birch takes on a warm tinge; the "
            "water below a golden bank glows with reflected warmth. This effect is "
            "partly physical (reflected light) but Levitan exaggerated it as a "
            "painterly device, using it to unify the warm-cool split and to give "
            "the golden passages their characteristic luminosity."
        ),
        famous_works=[
            ("Golden Autumn",          "1895"),
            ("March",                  "1895"),
            ("Above Eternal Peace",    "1894"),
            ("Quiet Abode",            "1890"),
            ("Vladimirka",             "1892"),
            ("Birch Grove",            "1885-1889"),
            ("The Lake. Russia",       "1900"),
            ("Autumn Day. Sokolniki",  "1879"),
            ("Evening Bells",          "1892"),
            ("After the Rain. Plyos",  "1889"),
        ],
        inspiration=(
            "levitan_autumn_shimmer_pass(): CHROMATIC WARMTH DIFFUSION FROM AUTUMN "
            "FOLIAGE -- 185th distinct mode. "
            "(1) WARM SOURCE DETECTION: identify warm-saturated pixels where R > "
            "warm_threshold AND (R - B) > warmth_spread_min -- these are the golden "
            "autumn foliage zones from which warmth diffuses; "
            "(2) WARMTH SIGNAL DIFFUSION: apply Gaussian blur to the warm source map "
            "with a large sigma (warmth_sigma ~40px), producing a smooth diffuse "
            "warmth field that falls off with distance from foliage sources; "
            "(3) WARM TINT APPLICATION: for pixels receiving diffused warmth signal, "
            "blend toward a warm golden hue (R+, B-) proportional to the diffused "
            "signal strength, capped by tint_max_opacity -- warm golden glow spills "
            "into adjacent sky and water zones; "
            "(4) COOL PRESERVATION: the tint is gated by a COOL-ZONE DETECTOR "
            "(pixels below luminance_floor are shadows and receive less tint to "
            "preserve cool shadow integrity -- Levitan always kept his shadows cool "
            "and transparent even as his lights were warm)."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"isaak_levitan"' in src:
    print("isaak_levitan already in catalog -- nothing to do.")
    sys.exit(0)

INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + LEVITAN_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Isaak Levitan into art_catalog.py.")
