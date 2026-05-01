"""Insert Jan Toorop entry into art_catalog.py (session 278).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

TOOROP_ENTRY = '''
    # ── Jan Toorop ────────────────────────────────────────────────────────────
    "jan_toorop": ArtStyle(
        artist="Jan Toorop",
        movement="Dutch Symbolism / Art Nouveau / Post-Impressionism",
        nationality="Dutch (born in Java, Dutch East Indies)",
        period="1858-1928",
        palette=[
            (0.08, 0.06, 0.04),   # dense ink black -- dominant line color
            (0.28, 0.20, 0.10),   # warm sepia -- thin ink wash, warm ground
            (0.12, 0.10, 0.32),   # deep indigo-violet -- Symbolist night sky
            (0.72, 0.45, 0.12),   # warm amber -- twilight horizon glow
            (0.15, 0.25, 0.12),   # dark olive-emerald -- willow, reeds
            (0.25, 0.38, 0.18),   # medium olive -- water lily pads
            (0.88, 0.86, 0.80),   # parchment white -- water lily blossom
            (0.82, 0.58, 0.56),   # pale rose -- pink blossom
            (0.08, 0.10, 0.24),   # deep indigo water -- still pond
            (0.48, 0.42, 0.62),   # cool mauve-violet -- midtone shadow
        ],
        ground_color=(0.68, 0.62, 0.50),     # warm buff/brown paper ground
        stroke_size=10,
        wet_blend=0.25,
        edge_softness=0.08,
        jitter=0.028,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Dutch Symbolism and Art Nouveau. Jan Toorop (1858-1928) was born "
            "in Purworedjo, Java, in the Dutch East Indies, raised in the "
            "Netherlands, and studied at the Amsterdam Rijksacademie and the "
            "Brussels Academie Royale des Beaux-Arts. He is the most distinctive "
            "draftsman of the Dutch Symbolist movement: a painter and graphic "
            "artist whose mature work is immediately recognizable by its "
            "extraordinary density of flowing, spidery lines drawn over flat "
            "tonal planes, combining influences from three cultures -- Dutch "
            "graphic tradition, Japanese woodblock prints, and Javanese wayang "
            "kulit shadow puppet theater. "
            "LINEAR NETWORK: Toorop's central technique is a multi-scale web of "
            "thin dark lines (Indian ink on warm-toned paper, or drawn into "
            "chalk grounds) that operates at three simultaneous levels: bold "
            "contour lines at tonal zone edges, intermediate flow lines tracing "
            "surface curvature, and fine filament hatching inside flat zones. "
            "The linear structure is always dark on light or midtone -- the flat "
            "planes provide the contrast, and the lines define form without shading. "
            "JAPONISME AND FLAT PLANES: From ukiyo-e woodblock prints (which he "
            "collected and studied), Toorop inherited the habit of organizing a "
            "composition into 3-4 broadly defined flat tonal zones with crisp "
            "boundaries, rather than academic smooth gradation. The linear "
            "network is then drawn over these flat zones -- the keyblock structure "
            "of the woodblock translated into drawing. "
            "WAYANG KULIT ORNAMENT: The Javanese shadow puppet theater of his "
            "Javanese childhood contributed the quality of dense decorative filling "
            "within flat zones: the shadow puppets' flat bodies are covered with "
            "incised scrollwork and geometric ornament. In Toorop's work this "
            "becomes fine hatching and decorative patterning in background and "
            "interior zones. "
            "SYMBOLIST CONTENT: Toorop was part of the Belgian Symbolist circle "
            "(Khnopff, Delville, Minne) and shared their interest in spiritual, "
            "death, and erotic symbolism. He converted to Roman Catholicism in "
            "1905 and much of his later work is devotional. His secular masterwork "
            "is THE THREE BRIDES (1893) -- a life-size drawing (2.8m x 1.5m) on "
            "brown paper, depicting three brides at the moment of mystical marriage "
            "-- Flesh, Spirit, and Death -- surrounded by an unbroken web of hair "
            "streams, angel forms, and symbolic flora. "
            "COLOR AND TECHNIQUE: In paint Toorop worked primarily in pastel and "
            "watercolor (often combined), reserving oil for early and late works. "
            "His oil palette is typically muted -- warm buffs, deep violets, dark "
            "greens -- with the draftsmanship carrying the composition rather than "
            "color relationships. In his Neo-Impressionist period (1891-1900, "
            "influenced by Seurat and Signac), he used divisionist color "
            "application, though always with his characteristic linear overlay. "
            "SIGNATURE WORKS: The Three Brides (1893); O Grave Where Is Thy "
            "Victory (1892); The Garden of Sorrow (1891); September Fog (1892); "
            "Faith in Decline (1894); The Sea (1899); The Waters (1900); Self-"
            "Portrait (1900)."
        ),
        famous_works=[
            ("The Three Brides",                    "1893"),
            ("O Grave Where Is Thy Victory",        "1892"),
            ("The Garden of Sorrow",                "1891"),
            ("September Fog",                       "1892"),
            ("Faith in Decline",                    "1894"),
            ("The Sea",                             "1899"),
            ("The Waters",                          "1900"),
            ("Song of the Times",                   "1893"),
            ("Desire and Gratification",            "1893"),
            ("Self-Portrait",                       "1900"),
        ],
        inspiration=(
            "toorop_symbolist_line_pass(): FOUR-STAGE ART NOUVEAU LINEAR NETWORK "
            "-- 189th distinct mode. "
            "(1) HUE-PRESERVING TONAL POSTERIZATION: nearest-level luminance "
            "snap into n_zones flat zones; applied as luminance scale ratio "
            "R_z = R * (L_target/(L+eps)) preserving hue; creates Toorop's "
            "flat graphic planes. "
            "(2) ISO-CONTOUR LINE THREADING: Sobel gradient direction used to "
            "place dark line segments PERPENDICULAR to gradient (along iso- "
            "luminance contours); first pass to render oriented contour-following "
            "line segments. "
            "(3) FLAT ZONE DECORATIVE HATCHING: gradient-magnitude gated stripe "
            "pattern at fixed decorative angle; only active in low-gradient "
            "(flat) zones; simulates Toorop's wayang kulit ornamental infill. "
            "(4) WARM INK BURNISHING: transition zone sepia tinting weighted "
            "by normalized gradient magnitude; warm ink quality in contour zones."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

ANCHOR = '    # ── Francisco de Goya'
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, TOOROP_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: jan_toorop entry inserted.")
