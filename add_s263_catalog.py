"""Insert Félix Vallotton entry into art_catalog.py (session 263).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

VALLOTTON_ENTRY = '''
    # ── Félix Vallotton ───────────────────────────────────────────────────────
    "vallotton": ArtStyle(
        artist="Félix Vallotton",
        movement="Nabis / Post-Impressionist",
        nationality="Swiss-French",
        period="1892–1925",
        palette=[
            (0.12, 0.10, 0.08),   # near-black shadow — Vallotton\'s dominant dark
            (0.88, 0.78, 0.48),   # warm lamp amber — kerosene glow
            (0.72, 0.62, 0.42),   # mid ochre — lit floor/table
            (0.42, 0.36, 0.28),   # warm mid-shadow — flesh in dim light
            (0.88, 0.85, 0.78),   # pale cream — bright tablecloth / window light
            (0.55, 0.35, 0.30),   # muted red-brown — dress/curtain shadows
            (0.30, 0.28, 0.22),   # dark olive — wall in shadow
            (0.92, 0.88, 0.76),   # soft highlight — lamp-lit face / white fabric
        ],
        ground_color=(0.25, 0.22, 0.18),    # dark warm ground — near-black imprimatura
        stroke_size=9,
        wet_blend=0.08,                      # very low — flat dry zones, no blending
        edge_softness=0.15,                  # very low — hard, woodcut-quality edges
        jitter=0.035,                        # low — within zones, colour is uniform
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Stark lamp-lit interior: near-black shadow zones juxtaposed with "
            "concentrated warm amber lamp pools. Japanese woodcut flatness -- "
            "figures become silhouettes against bright backgrounds, forms defined "
            "by hard outline rather than tonal modelling. Strong influence of "
            "Hiroshige and Hokusai in the simplification of domestic space to "
            "flat geometric planes. Shadow areas are crushed to near-black; "
            "mid-tones are warm and reduced to two or three flat values; "
            "highlights are kept small, tight, and high-key. Psychological "
            "tension through extreme tonal contrast and voyeuristic composition "
            "(figures glimpsed through doorways, seen from behind). "
            "Technically: flat oil on canvas, no impasto, almost no visible "
            "brushwork in finished zones -- the surface is as smooth and matte "
            "as lacquer."
        ),
        famous_works=[
            ("Dinner, by Lamplight",   "1899"),
            ("The Visit",              "1899"),
            ("The Ball",               "1899"),
            ("Intimacy",               "1891"),
            ("Naked Woman Standing",   "1905"),
            ("The Lie",                "1897"),
            ("The Supper",             "1899"),
        ],
        inspiration=(
            "vallotton_dark_interior_pass(): THREE-STAGE STARK INTERIOR "
            "CHIAROSCURO -- (1) SHADOW CRUSH: sigmoid-steepened compression "
            "below shadow_crush threshold pushes near-shadow pixels to near-black; "
            "(2) RADIAL LAMP WARMTH POOL: quadratic-falloff warm-amber blend "
            "centred on configurable lamp_cx/lamp_cy position; "
            "(3) JAPANESE INK CONTOUR: thresholded Sobel + Gaussian anti-alias "
            "used as multiplicative darkening to add woodcut-quality ink outlines."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"vallotton"' in src:
    print("Vallotton already in catalog -- nothing to do.")
    sys.exit(0)

# Insert just before the closing brace of CATALOG
INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + VALLOTTON_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Félix Vallotton into art_catalog.py.")
