"""Insert André Derain entry into art_catalog.py (session 285).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

DERAIN_ENTRY = '''
    # ── André Derain ─────────────────────────────────────────────────────────────
    "andre_derain": ArtStyle(
        artist="André Derain",
        movement="Fauvism / Post-Impressionism / Early Modernism",
        nationality="French",
        period="1880-1954",
        palette=[
            (0.90, 0.40, 0.08),   # cadmium orange-red -- Fauve primary warm
            (0.14, 0.52, 0.78),   # cobalt cerulean -- Fauve primary cool
            (0.12, 0.62, 0.38),   # viridian emerald -- Collioure water green
            (0.88, 0.82, 0.12),   # cadmium yellow -- electric Fauve yellow
            (0.52, 0.18, 0.72),   # violet-crimson -- Fauve shadow complement
            (0.94, 0.56, 0.22),   # warm amber-ochre -- Mediterranean light
            (0.20, 0.28, 0.68),   # deep cobalt -- Fauve shadow blue
            (0.82, 0.20, 0.18),   # cadmium vermillion -- boat hulls, rooftops
            (0.72, 0.82, 0.36),   # acid yellow-green -- Fauve light accent
            (0.10, 0.18, 0.38),   # deep navy -- harbour depth, night water
        ],
        ground_color=(0.92, 0.88, 0.76),  # raw linen / near-white Derain ground
        stroke_size=12,
        wet_blend=0.32,
        edge_softness=0.18,
        jitter=0.022,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Fauvism / French Post-Impressionism. André Derain (1880-1954) "
            "co-founded Fauvism with Henri Matisse during their summer at "
            "Collioure in 1905. Derain was the more explosive and direct "
            "of the two founders -- he pushed colour liberation to its logical "
            "extreme, using pigment squeezed directly from the tube, minimally "
            "mixed, applied in broad flat passages with vigorous brushwork. "
            "His London series (1906) for dealer Ambroise Vollard converted "
            "the grey Thames into vivid orange, pink, and cobalt passages. "
            "DERAIN'S FIVE TECHNICAL SIGNATURES: "
            "(1) SATURATION MAXIMISATION: colours at or near full chroma, "
            "squeezed from the tube with minimal mixing; grey zones treated "
            "as colour in their own right, not as neutrals. "
            "(2) MULTI-SECTOR SPECTRAL COMMITMENT: each region of the canvas "
            "commits fully to its hue sector; no gradual hue transitions. "
            "(3) SIMULTANEOUS CONTRAST EXPLOITATION: complementary hues placed "
            "deliberately adjacent to mutually amplify their apparent intensity. "
            "(4) GRADIENT-DIRECTED TEMPERATURE ASYMMETRY: warm light-facing "
            "surfaces, cool shadow-facing surfaces -- the directional cosine "
            "of the surface normal against the light direction as zone gate. "
            "(5) FAUVE GROUND SHOW-THROUGH: raw canvas or lightly-primed "
            "ground visible between energetic brushstrokes; the bare support "
            "acts as a neutral fourth colour. "
            "THE GREAT WORKS: 'The Pool of London' (1906) -- Thames as orange "
            "and gold dream; 'Boats at Collioure' (1905) -- pure cadmium and "
            "cobalt harbour; 'Mountains at Collioure' (1905) -- violet and "
            "orange Pyrenean landscape; 'Charing Cross Bridge' (1906) -- "
            "London railway bridge in electric Fauve light."
        ),
        famous_works=[
            ("The Pool of London",                    "1906"),
            ("Boats at Collioure",                    "1905"),
            ("The Harbour of Collioure",              "1905"),
            ("Mountains at Collioure",                "1905"),
            ("Charing Cross Bridge",                  "1906"),
            ("The Thames at London",                  "1906"),
            ("Turning Road, L\'Estaque",              "1906"),
            ("The Dance",                             "1906"),
            ("Portrait of Matisse",                   "1905"),
            ("London Bridge",                         "1906"),
        ],
        inspiration=(
            "derain_fauve_intensity_pass(): FOUR-STAGE FAUVE CHROMATIC SYSTEM "
            "-- 196th distinct mode. "
            "(1) HSV S-CHANNEL POWER CURVE: RGB→HSV, S_new = S^sat_gamma "
            "(default gamma=0.60, sub-unity = expansion toward full saturation); "
            "FIRST PASS to apply power-law transformation to the S (saturation) "
            "channel of HSV -- s284 rotated H; no prior pass operated on S. "
            "(2) SIX-SECTOR HUE COMMITMENT: classify H into 6 spectral sectors "
            "(0-60, 60-120, 120-180, 180-240, 240-300, 300-360 degrees); push "
            "toward sector spectral centre weighted by S_new; "
            "FIRST PASS with 6-sector hue classification, per-sector push targets. "
            "(3) LOCAL COLOUR CONTRAST AMPLIFICATION: for each channel independently: "
            "C_contrast = clip(C + (C - Gaussian(C, local_sigma)) * amplify, 0, 1); "
            "FIRST PASS to amplify colour-channel deviations from local spatial mean "
            "uniformly across all channels without luminance gate. "
            "(4) GRADIENT-ANGLE WARM/COOL PUSH: dot = cos(atan2(Gy,Gx) - light_angle); "
            "light_mask = clip(dot,0,1)*G_norm; shadow_mask = clip(-dot,0,1)*G_norm; "
            "warm push at light-facing pixels, cool push at shadow-facing pixels; "
            "FIRST PASS to use the FULL 2D GRADIENT ANGLE (atan2) as directional "
            "cosine zone gate -- prior passes use G_mag only, or fixed-axis Gx only."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

assert "andre_derain" not in src, "andre_derain already exists in art_catalog.py"

ANCHOR = "\n\n}\n\n\ndef get_style"
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, DERAIN_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: andre_derain entry inserted.")
