"""Insert Marsden Hartley entry into art_catalog.py (session 287).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

HARTLEY_ENTRY = '''
    # ── Marsden Hartley ──────────────────────────────────────────────────────────
    "marsden_hartley": ArtStyle(
        artist="Marsden Hartley",
        movement="American Modernism / Expressionism",
        nationality="American",
        period="1877-1943",
        palette=[
            (0.08, 0.12, 0.08),   # deep shadow green -- dark spruce, shadow mountain
            (0.06, 0.08, 0.18),   # blue-black granite -- Katahdin rock face
            (0.35, 0.22, 0.12),   # raw umber -- rocky ground, bark
            (0.70, 0.32, 0.14),   # burnt sienna / vermillion -- autumn accent
            (0.09, 0.07, 0.05),   # near-black -- deep shadow mass, outline
            (0.78, 0.72, 0.55),   # warm cream / chalk -- sky light, foam
            (0.18, 0.28, 0.12),   # forest green -- dense spruce
            (0.65, 0.48, 0.22),   # raw sienna / ochre -- dawn sky, ledge
            (0.28, 0.36, 0.22),   # muted sage -- distant treeline
            (0.82, 0.54, 0.18),   # deep amber -- October sky horizon
        ],
        ground_color=(0.12, 0.10, 0.08),  # dark raw umber ground
        stroke_size=18,
        wet_blend=0.38,
        edge_softness=0.22,
        jitter=0.022,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "American Modernism / Expressionism. Marsden Hartley (1877-1943) "
            "was born in Lewiston, Maine, and is the pre-eminent painter of the "
            "American elemental landscape. He studied with William Merritt Chase "
            "and discovered Cezanne in Paris (1912), then spent time in Berlin "
            "(1913-15) where German Expressionism amplified Cezanne's structural logic "
            "with chromatic intensity. His late Maine and New England work (1930s-40s) "
            "is the heart of his achievement: massive simplified dark forms, severely "
            "restricted palette, Cezannesque flat plane construction. "
            "HARTLEY'S FIVE TECHNICAL SIGNATURES: "
            "(1) RESTRICTED EARTHEN PALETTE: deep blue-black, dark green, raw umber, "
            "burnt sienna, near-black, warm cream -- all colours of granite, spruce, "
            "grey sea, and Maine autumn sky. No lavenders or complex mixes. "
            "(2) FLAT COLOUR PLANE CONSTRUCTION: Cezanne's 'passage' technique -- "
            "large zones of near-uniform colour, physically thick paint, spatial "
            "boundaries as visible darker transitions. Mosaic or stained-glass quality. "
            "(3) BOLD PAINT-DRAWN OUTLINES: dark paint at edges functions as drawn "
            "outline but with the physical substance of painting -- thick boundary colour "
            "bridging adjacent planes. "
            "(4) DARK MASS DOMINANCE: mountains, rocks, and sea are characteristically "
            "very dark; Hartley did not lift darks for compositional balance. Katahdin "
            "in 'Katahdin, Autumn No. 1' is nearly pure black-green. "
            "(5) ANTI-CORRELATED SATURATION: darkest zones nearly desaturated; "
            "lighter zones intensely saturated. Dark mass gravity + chromatic sky vitality. "
            "THE GREAT WORKS: 'Katahdin, Autumn No. 1' (1939-40) -- near-black mountain "
            "against burning sky; 'Evening Storm, Schoodic, Maine' (1942) -- Atlantic "
            "storm as dark flat planes; 'Blueberry Highway, Dogtown' (1931) -- rocky "
            "glacial landscape in severely limited palette; 'Fox Island' (1937)."
        ),
        famous_works=[
            ("Katahdin, Autumn No. 1",              "1939-1940"),
            ("Evening Storm, Schoodic, Maine",       "1942"),
            ("Blueberry Highway, Dogtown",           "1931"),
            ("Dead Plover",                          "1940-1941"),
            ("Fox Island, Georgetown, Maine",        "1937"),
            ("Smelt Brook Falls",                    "1937"),
            ("Dogtown Common, Cape Ann",             "1936"),
            ("The Wave",                             "1940"),
            ("Mount Katahdin, Maine",                "1942"),
            ("Ghosts on the Road, Dogtown",         "1936"),
        ],
        inspiration=(
            "hartley_elemental_mass_pass(): FOUR-STAGE ELEMENTAL MASS SYSTEM "
            "-- 198th distinct mode. "
            "(1) NEAREST-PALETTE-COLOR COMMITMENT: PALETTE = 8-color Hartley Maine set; "
            "flat = pixels.reshape(-1, 3); diff = flat[:,None,:] - PALETTE[None,:,:]; "
            "nearest_idx = argmin(sum(diff^2, axis=-1), axis=-1); "
            "push = (1 - clip(nearest_dist/P95(nearest_dist), 0, 1)) * palette_strength; "
            "FIRST pass to compute per-pixel L2 distance to multiple palette targets "
            "and push each pixel toward its own nearest colour (different pixels may "
            "target different palette anchors). All prior colour commitment passes use "
            "a single global target (repin, carriere) or HSV-sector hue (derain). "
            "(2) COARSE TILE INTERIOR FLATTENING: canvas partitioned into n_h x n_w tiles; "
            "R_tile[tile] = mean(R_in_tile); Gaussian-smooth tile boundaries; "
            "interior_w = (1 - G_norm) * strength; R2 = R1 + (R_tile - R1) * interior_w; "
            "FIRST use of step-function spatial tile partition as the interior mass target; "
            "all prior interior-smoothing passes use Gaussian blur (continuous, no discrete "
            "spatial structure). Tile averaging creates discrete colour planes. "
            "(3) SYMMETRIC BILATERAL EDGE DARKENING: edge_w = G_norm * strength; "
            "R3 = R2 + (edge_dark - R2) * edge_w; edge_dark = (0.06, 0.06, 0.06); "
            "FIRST pass to use unsigned G_norm as symmetric bilateral edge outline gate "
            "(BOTH sides of every edge pushed toward near-black equally). "
            "Grosz Stage 1 uses SIGNED Gx (directional, one side only); "
            "repin Stage 4 uses G_norm for sharpening (not darkening). "
            "(4) LUMINANCE-ANTI-CORRELATED SATURATION: "
            "dark gate = clip((dark_thresh - L)/dark_thresh, 0, 1) * dark_desat_str; "
            "R_dk = R3 + dark_gate * (mean_channel - R3) [desaturate darks toward grey]; "
            "bright gate = clip((L - bright_thresh)/(1-bright_thresh), 0, 1) * bright_str; "
            "R4 = R_dk + (R_dk - mean_channel_dk) * bright_gate [amplify sat in brights]; "
            "FIRST pass with continuous luminance-anti-correlated saturation curve: "
            "dark zones desaturated, bright zones amplified, in same pass. "
            "Derain Stage 1: power-law S^gamma applied uniformly (not anti-correlated). "
            "Carriere Stage 1: sepia tint (desaturation toward warm, not neutral grey). "
            "S284 chromatic_shadow_shift: hue rotation (H channel), not saturation amount."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

assert "marsden_hartley" not in src, "marsden_hartley already exists in art_catalog.py"

ANCHOR = "\n\n}\n\n\ndef get_style"
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, HARTLEY_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: marsden_hartley entry inserted.")
