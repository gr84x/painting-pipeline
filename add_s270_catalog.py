"""Insert Georgia O'Keeffe entry into art_catalog.py (session 270).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

OKEEFFE_ENTRY = '''
    # ── Georgia O\'Keeffe ─────────────────────────────────────────────────────
    "georgia_okeeffe": ArtStyle(
        artist="Georgia O\'Keeffe",
        movement="American Modernism / Precisionism-adjacent Organic Abstraction",
        nationality="American",
        period="1887-1986",
        palette=[
            (0.98, 0.96, 0.92),   # near-white — luminous petal interior
            (0.94, 0.78, 0.68),   # pale peach — warm petal transition
            (0.88, 0.56, 0.42),   # deep salmon — form-turning zone
            (0.72, 0.30, 0.28),   # crimson — deep petal shadow
            (0.14, 0.22, 0.42),   # deep indigo — desert night sky
            (0.28, 0.44, 0.30),   # sage — New Mexico vegetation
            (0.72, 0.60, 0.40),   # warm sand — desert ground
            (0.52, 0.46, 0.72),   # soft violet — twilight sky gradient
            (0.90, 0.82, 0.58),   # golden — late afternoon desert light
        ],
        ground_color=(0.94, 0.90, 0.84),    # warm cream — O\'Keeffe\'s pale luminous ground
        stroke_size=16,
        wet_blend=0.18,                      # smooth, controlled paint application
        edge_softness=0.12,                  # mostly hard edges between forms
        jitter=0.012,                        # minimal jitter — precise form boundaries
        glazing=None,
        crackle=False,
        chromatic_split=False,               # unified, smooth colour within forms
        technique=(
            "American Modernist Organic Abstraction. Georgia O\'Keeffe (1887-1986) "
            "spent sixty years evolving one of the most distinctive surfaces in "
            "American art: the silky, almost frictionless interior of each painted "
            "form, combined with hard, precise edges where one colour mass meets "
            "another. Her close-up flower paintings of the 1920s-30s (Jimson Weed, "
            "Poppies, Calla Lily, Canna) enlarged organic forms to architectural "
            "scale, eliminating decorative detail and forcing the viewer to attend "
            "only to the abstract structure of the form itself: the smooth gradient "
            "from light to shadow, the colour intensification at the form-turning "
            "zone, the clean boundary between adjacent colour masses, and the "
            "characteristic translucent inner glow of backlighted petals where "
            "light passes through the thin membrane. Her New Mexico landscape "
            "paintings (Black Mesa, Pedernal, the Ghost Ranch series from the "
            "1930s onward) apply the same principles to land: rolling hills become "
            "simplified colour masses with hard silhouette edges and smooth tonal "
            "gradients on their faces. O\'Keeffe aligned with the Precisionists "
            "(Sheeler, Demuth, Strand) in her preference for clean, unambiguous "
            "form, but she applied it not to the machine-made but to the organic. "
            "Her palette is wide: warm creams and salmons through deep crimsons "
            "in the flower period; indigo, sage, deep red earth, warm gold, and "
            "bone-white in the desert period. Ground shows through in the petal "
            "interior as a warm luminous presence -- not as bare canvas, but as "
            "the felt warmth of thin paint on a well-prepared surface. The form- "
            "turning zone -- the middle tonal range where a surface curves away "
            "from the light -- is always the most saturated and most richly coloured "
            "zone of any O\'Keeffe form."
        ),
        famous_works=[
            ("Black Iris III",                  "1926"),
            ("Jimson Weed/White Flower No. 1",  "1932"),
            ("Red Canna",                        "1919"),
            ("Cow\'s Skull: Red, White, and Blue","1931"),
            ("Black Mesa Landscape, New Mexico", "1930"),
            ("Pelvis with the Moon",            "1943"),
            ("Sky Above Clouds IV",             "1965"),
            ("Ram\'s Head, White Hollyhock",     "1935"),
        ],
        inspiration=(
            "okeeffe_organic_form_pass(): FOUR-STAGE ORGANIC FORM REFINEMENT "
            "TECHNIQUE -- 181st distinct mode. "
            "(1) LOCAL LUMINANCE VARIANCE ZONE DETECTION: compute per-pixel local "
            "luminance variance via gaussian(L^2) - gaussian(L)^2 at variance_sigma; "
            "identify SMOOTH INTERIOR zones (var <= 25th-percentile of nonzero var) "
            "and EDGE zones (var > edge_threshold); first pass to use the joint "
            "topology of smooth vs edge zones as opposing targets for smoothing and "
            "sharpening respectively; "
            "(2) VARIANCE-GATED INTERIOR SMOOTHING: blend Gaussian-blurred canvas "
            "toward current canvas at smooth_strength BUT ONLY in smooth interior "
            "zones -- zero effect at edge zones; first pass to gate Gaussian "
            "smoothing specifically to low-variance form interior regions, "
            "concentrating the O\'Keeffe silky surface quality in the correct zone; "
            "(3) FORM-TURNING ZONE SATURATION LIFT: detect pixels in mid-luminance "
            "range [0.28, 0.68] AND low local variance (below mid_variance_cap); "
            "apply saturation lift by pulling each channel away from luminance -- "
            "first pass to use joint luminance-range and variance conditions to "
            "locate the tonal transition zone and apply targeted saturation "
            "intensification; "
            "(4) EDGE-GATED UNSHARP MASKING: in high-variance edge zones, apply "
            "unsharp masking (canvas + amount*(canvas - blur)) leaving smooth "
            "interior completely untouched -- first pass to gate USM sharpening "
            "to variance-detected edge zones only, creating O\'Keeffe\'s clean crisp "
            "boundary between adjacent colour masses."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"georgia_okeeffe"' in src:
    print("georgia_okeeffe already in catalog -- nothing to do.")
    sys.exit(0)

INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + OKEEFFE_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Georgia O'Keeffe into art_catalog.py.")
