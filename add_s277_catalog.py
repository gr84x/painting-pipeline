"""Insert Francisco de Goya entry into art_catalog.py (session 277).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

GOYA_ENTRY = '''
    # ── Francisco de Goya ─────────────────────────────────────────────────────
    "francisco_goya": ArtStyle(
        artist="Francisco de Goya",
        movement="Spanish Romanticism / Dark Romanticism / Proto-Expressionism",
        nationality="Spanish",
        period="1746-1828",
        palette=[
            (0.06, 0.05, 0.04),   # bone black -- dominant dark mass
            (0.28, 0.20, 0.12),   # raw umber -- warm ground showing through
            (0.52, 0.24, 0.14),   # burnt sienna -- dark red-brown midtone
            (0.94, 0.90, 0.82),   # lead white -- isolated bright highlight
            (0.10, 0.12, 0.18),   # prussian blue-black -- cool dark accent
            (0.78, 0.58, 0.22),   # warm amber-gold -- firelight / candlelight
            (0.68, 0.50, 0.32),   # ochre -- midtone warm earth
            (0.82, 0.74, 0.66),   # light flesh -- pale skin tone (highlights)
            (0.18, 0.14, 0.10),   # deep umber -- near-black with warmth
            (0.44, 0.32, 0.20),   # middle sienna -- shadow with warmth
        ],
        ground_color=(0.22, 0.16, 0.10),     # dark warm brown ground
        stroke_size=14,
        wet_blend=0.38,
        edge_softness=0.12,
        jitter=0.045,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Black Paintings / Dark Romanticism. Francisco de Goya (1746-1828) "
            "was a Spanish court painter whose career underwent a radical "
            "transformation following a severe illness in 1792-93 that left him "
            "permanently deaf. From this crisis emerged the most radical "
            "transformation in European painting until Expressionism: the Black "
            "Paintings (Pinturas negras, 1820-23), fourteen monumental works "
            "painted in oil directly on the plaster walls of his country house "
            "outside Madrid, 'La Quinta del Sordo' (The House of the Deaf Man). "
            "Painted for himself alone, with no patron, no commission, and "
            "apparently no intent of exhibition or sale, the Black Paintings "
            "represent Goya's most radical and personal vision. "
            "DARK GROUND TECHNIQUE: Goya applied a warm brown ground (raw umber + "
            "lead white) to the plaster, then built dense dark masses with bone "
            "black, Prussian blue-black, and burnt sienna. The brown ground "
            "shows through thin passages, giving even the deepest shadows a warm, "
            "living quality distinct from cool academic grey shadow. "
            "CHIAROSCURO DRAMA: The Black Paintings operate in a compressed tonal "
            "range -- most of the canvas is deep shadow (0-0.35 value), midtones "
            "exist only as a narrow transitional band, and highlights are isolated, "
            "intense, almost violent in their brightness. The transition from "
            "shadow to light is abrupt; there is none of academic painting's "
            "smooth five-value modelling. "
            "GESTURAL APPLICATION: In transition and modelling zones, Goya used "
            "palette knives, rags, and his own fingers to drag and smear paint "
            "into agitated, rough textures. Flat dark masses and flat light areas "
            "are smooth; only the passages where light meets shadow carry raw, "
            "expressive marks. "
            "SIGNATURE WORKS: Saturn Devouring His Son (1820-23); Witches' Sabbath "
            "(The Great He-Goat) (1820-23); The Dog (1820-23); Two Old Men Eating "
            "Soup (1820-23); Duel with Cudgels (1820-23); The Third of May 1808 "
            "(1814, earlier but related in spirit); The Colossus (~1808-12)."
        ),
        famous_works=[
            ("Saturn Devouring His Son",                    "1820-23"),
            ("Witches' Sabbath (The Great He-Goat)",        "1820-23"),
            ("The Dog",                                     "1820-23"),
            ("Two Old Men Eating Soup",                     "1820-23"),
            ("Duel with Cudgels",                           "1820-23"),
            ("The Third of May 1808",                       "1814"),
            ("The Colossus",                                "~1808-12"),
            ("The Sleep of Reason Produces Monsters",       "1799"),
            ("Yard with Lunatics",                          "1794"),
            ("Pilgrimage to San Isidro",                    "1820-23"),
        ],
        inspiration=(
            "goya_black_vision_pass(): FOUR-STAGE DARK ROMANTICISM RENDERING -- "
            "188th distinct mode. "
            "(1) DARK EARTH GROUND PENETRATION: quadratic luminance-dependent "
            "blending of warm umber ground into all zones; w_ground = strength * "
            "(1-L)^2; continuous nonlinear ground penetration (no threshold "
            "discontinuity) strongest in deepest darks. "
            "(2) SIGMOID TONAL DRAMA AMPLIFICATION: parametric sigmoid "
            "L_new = f(L) = t_min + (t_max-t_min)/(1+exp(-steepness*(L-midpoint))); "
            "applied via luminance ratio R_new = R * (L_new/(L+eps)) to preserve "
            "hue while compressing midtones toward darkness. "
            "(3) SHADOW DESATURATION WITH WARM UMBER TRACE: simultaneous "
            "desaturation (blend toward L grey) and warm umber hue shift in shadow "
            "zones; single continuous weight w_desat = ds*(1-L/thresh)*below_thresh. "
            "(4) TRANSITION ZONE TURBULENCE: Sobel gradient magnitude used to "
            "identify transition pixels (gl < Gnorm < gh); Gaussian-smoothed "
            "seeded noise applied additively, weighted by Gnorm * transition_mask; "
            "noise absent in flat zones, strongest at luminance boundaries."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

ANCHOR = '    # ── Wayne Thiebaud'
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, GOYA_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: francisco_goya entry inserted.")
