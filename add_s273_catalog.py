"""Insert Yves Klein entry into art_catalog.py (session 273).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

KLEIN_ENTRY = '''
    # ── Yves Klein ────────────────────────────────────────────────────────────
    "yves_klein": ArtStyle(
        artist="Yves Klein",
        movement="Nouveau Réalisme / Monochromism",
        nationality="French",
        period="1928-1962",
        palette=[
            (0.00, 0.18, 0.65),   # IKB ultramarine (International Klein Blue 79)
            (0.04, 0.10, 0.42),   # deep cobalt-navy -- shadow passages in blue field
            (0.22, 0.34, 0.78),   # electric violet-blue -- lighter IKB surface
            (0.06, 0.06, 0.28),   # deep navy-black -- silhouette passages
            (0.65, 0.55, 0.22),   # gold leaf (monogold series)
            (0.82, 0.18, 0.08),   # rose carmine (monopink series)
            (0.90, 0.90, 0.90),   # near-white (the void / empty room)
            (0.08, 0.28, 0.55),   # transitional cobalt -- horizon zone
            (0.12, 0.12, 0.58),   # prussian-ultramarine midtone
        ],
        ground_color=(0.02, 0.10, 0.52),     # deep IKB cobalt ground
        stroke_size=22,
        wet_blend=0.10,                       # minimal blending -- pure pigment, no oil wet-into-wet
        edge_softness=0.14,                   # fairly hard edges -- pure color zones
        jitter=0.020,                         # low jitter -- meditative, controlled application
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Nouveau Réalisme and Monochromism. Yves Klein (1928-1962) was a French "
            "artist and the defining figure of post-war monochrome painting, whose "
            "central achievement was the development of International Klein Blue "
            "(IKB 79) -- a proprietary ultramarine pigment in Rhodopas M60A resin "
            "binder that preserves the pure optical character of dry pigment while "
            "permanently fixing it to the support. Traditional oil binders coat pigment "
            "crystals, reducing their light-scattering efficiency and darkening the "
            "perceived color. Klein's resin medium binds without coating, leaving air-"
            "facing crystal surfaces free to scatter light independently -- the result "
            "is a blue that appears to have NO SURFACE, extending beyond the canvas "
            "into an infinite chromatic space. Klein registered IKB as a commercial "
            "color on May 19, 1960. In addition to monochromes in IKB, he made "
            "MONOGOLD (22-carat gold leaf applied to panel) and MONOPINK series. "
            "His ANTHROPOMETRIES (1960-61) were made by pressing IKB-coated nude "
            "bodies against white canvas -- the human figure as living brush -- "
            "performed publicly at Galerie internationale d'art contemporain, Paris, "
            "to a chamber orchestra playing his MONOTONE SYMPHONY (1949): one "
            "sustained D-major chord for 20 minutes, followed by 20 minutes of "
            "silence. His FIRE PAINTINGS (FC series, 1961-62) were made by burning "
            "canvas with a gas torch, carbonizing specific zones while leaving others "
            "intact. Klein said: 'The sky is my first work of art.' He grew up in "
            "Nice, and his monochromes carry the specific quality of the Côte d'Azur "
            "sky -- the way the blue Mediterranean light makes the sky and sea "
            "dissolve into each other at the horizon until color alone remains, "
            "freed from form and depth."
        ),
        famous_works=[
            ("IKB 3",                                    "1960"),
            ("Monochrome Blue (IKB 191)",                "1962"),
            ("Anthropometry of the Blue Period (ANT 82)", "1960"),
            ("Fire Painting FC 1",                       "1961"),
            ("Sponge Relief Blue (RE 51)",               "1961"),
            ("Relief Éponge Bleu Monochrome",            "1958"),
            ("The Void (Le Vide)",                       "1958"),
            ("Leap into the Void",                       "1960"),
            ("Requiem (RE 22)",                          "1960"),
            ("Monotone Symphony",                        "1949"),
        ],
        inspiration=(
            "klein_ib_field_pass(): THREE-STAGE CHROMATIC FIELD INSPIRED BY YVES KLEIN "
            "AND INTERNATIONAL KLEIN BLUE -- 184th distinct mode. "
            "(1) CHROMATIC RESONANCE-WEIGHTED IKB TINTING: compute dot-product alignment "
            "between each pixel's RGB vector and the IKB color vector; blue-family pixels "
            "receive full tint_strength, warm/complementary pixels receive reduced tinting "
            "(scaled by resonance_weight); first pass to modulate tinting strength by "
            "existing hue AFFINITY for the target color rather than by zone, distance, or "
            "pressure; "
            "(2) MATTE PIGMENT MICRO-TEXTURE: add isochromatic (same-amplitude) Gaussian "
            "noise at sigma=0.8 pixels (sub-pixel scale, below canvas-weave scale) to all "
            "three channels simultaneously; simulates pure pigment crystal scattering at "
            "the matte surface; first pass to apply sub-pixel-sigma ISOCHROMATIC noise "
            "(preserving monochrome character); "
            "(3) WARM SUPPRESSION: reduce red excess (warmth = max(R-B, 0)) proportionally "
            "to each pixel's measured warmth; warm pixels shift toward cool blue-neutral, "
            "cool pixels unchanged; first pass to suppress warmth content-adaptively by "
            "MEASURED WARMTH VALUE rather than by fixed zone or uniform color shift."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"yves_klein"' in src:
    print("yves_klein already in catalog -- nothing to do.")
    sys.exit(0)

INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + KLEIN_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Yves Klein into art_catalog.py.")
