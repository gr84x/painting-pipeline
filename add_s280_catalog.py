"""Insert Nicolai Fechin entry into art_catalog.py (session 280).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

FECHIN_ENTRY = '''
    # ── Nicolai Fechin ────────────────────────────────────────────────────────
    "nicolai_fechin": ArtStyle(
        artist="Nicolai Fechin",
        movement="Russian-American Realism / Taos School / Gestural Impressionism",
        nationality="Russian-American",
        period="1881-1955",
        palette=[
            (0.72, 0.38, 0.12),   # raw sienna -- warm midtone, Russian earth ground
            (0.38, 0.20, 0.08),   # burnt umber -- deep shadow anchor, dark contour
            (0.88, 0.72, 0.52),   # warm ochre light -- sunlit flesh, highlight warmth
            (0.22, 0.26, 0.32),   # Payne gray-blue -- cool background, neutral shadow
            (0.82, 0.58, 0.38),   # Naples yellow -- warm diffused light, skin middle
            (0.62, 0.18, 0.12),   # deep vermilion -- lip accent, warm shadow push
            (0.92, 0.88, 0.80),   # near-white cream -- specular highlight, eye white
            (0.48, 0.44, 0.40),   # warm neutral gray -- transitional halftone
            (0.30, 0.34, 0.28),   # dark viridian -- background foliage suggestion
            (0.78, 0.66, 0.52),   # pale warm tan -- ear, temple, secondary flesh
        ],
        ground_color=(0.58, 0.42, 0.26),     # warm burnt sienna ground (traditional academic)
        stroke_size=12,
        wet_blend=0.22,
        edge_softness=0.10,
        jitter=0.030,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Russian-American Realism, Taos School, Gestural Impressionism. "
            "Nicolai Ivanovich Fechin (1881-1955) was born in Kazan, Russia, "
            "the son of a wood-carver. He trained at the Kazan Art School and "
            "then at the Imperial Academy of Arts in St. Petersburg under Ilya "
            "Repin, receiving the Academy's gold medal in 1909 for his "
            "graduation work 'The Slaughterhouse.' He emigrated to the United "
            "States in 1923, settling in Taos, New Mexico in 1927, where he "
            "built and carved his home by hand (now the Fechin House, a National "
            "Historic Landmark) and produced his most celebrated portraits of "
            "Taos Pueblo people: 'Taos Girl,' 'Indian Girl,' 'Dark Eyes,' "
            "'Corn Dance,' 'Mabel Dodge Luhan.' "
            "FECHIN'S THREE SIMULTANEITIES -- the defining tension in his work: "
            "(1) TIGHT ACADEMIC RENDERING of the focal subject (eyes, nose, "
            "lips) executed with Repin's precision; every value transition "
            "carefully observed, every highlight placed exactly. "
            "(2) LOOSE GESTURAL BACKGROUND -- drapery, environment, and "
            "peripheral passages in broad slashing strokes at varied angles, "
            "deliberately left crude and unblended. "
            "(3) PALETTE KNIFE SCRAPING in highlight zones -- after laying "
            "heavy impasto in the lights, Fechin dragged a knife across the "
            "wet paint, partially removing it to expose the warm ground in "
            "bright streaks with a translucent luminosity distinct from any "
            "brushstroke. "
            "TURBULENT BRUSHWORK DIRECTION: Fechin's backgrounds show strokes "
            "moving in varied directions that change gradually across the canvas, "
            "creating a turbulent but coherent directional energy that enlivens "
            "the peripheral passages without fragmenting the composition. "
            "RUSSIAN EARTH PALETTE: Warm raw sienna and burnt umber in the "
            "midtones and shadows, with cool Payne gray in the background and "
            "warm ochre-cream in the lights -- an earth-anchored palette that "
            "makes his portraits glow with inner warmth. "
            "REPIN'S INFLUENCE: Fechin retained Repin's academic discipline "
            "of exacting observation and structural clarity at the focal "
            "subject, deploying it selectively as the conceptual foil to his "
            "gestural periphery. The tension between academic precision and "
            "gestural freedom is the formal engine of his work. "
            "SIGNATURE WORKS: Taos Girl (c.1927-28); Indian Girl (c.1927-30); "
            "Dark Eyes (c.1930); Corn Dance (c.1930); Mabel Dodge Luhan "
            "(c.1930); Self-Portrait (c.1910); Portrait of a Woman (c.1912); "
            "The Slaughterhouse (1909); Adoration of the Magi study (c.1913)."
        ),
        famous_works=[
            ("Taos Girl",               "c.1927-28"),
            ("Indian Girl",             "c.1927-30"),
            ("Dark Eyes",               "c.1930"),
            ("Corn Dance",              "c.1930"),
            ("Mabel Dodge Luhan",       "c.1930"),
            ("The Slaughterhouse",      "1909"),
            ("Self-Portrait",           "c.1910"),
            ("Portrait of a Woman",     "c.1912"),
            ("Adoration of the Magi",   "c.1913"),
            ("Kuibyshev Portrait",      "c.1940"),
        ],
        inspiration=(
            "fechin_gestural_impasto_pass(): FOUR-STAGE GESTURAL IMPASTO AND "
            "EARTH PALETTE SYSTEM -- 191st distinct mode. "
            "(1) TURBULENT VELOCITY FIELD ANISOTROPY: spatially varying angle "
            "field from superposed sinusoidal planes (3 frequencies/phases); "
            "directional anisotropic mean blend weighted by cos^4 of angle "
            "proximity; first pass to use autonomous sinusoidal-superposition "
            "flow field (not image gradient) for directional brushwork structure. "
            "(2) PALETTE KNIFE SCRAPE SIMULATION: luminance-gated horizontal "
            "uniform-filter mean applied to highlight zone (L>scrape_threshold); "
            "first pass to simulate knife scraping via anisotropic spatial "
            "averaging in highlight zones only. "
            "(3) REPIN ACADEMIC FOCAL SHARPENING: unsharp mask weighted by "
            "focal-distance power law (1-dist_norm)^focal_power; first pass "
            "to apply USM gated by focal proximity alone (without gradient "
            "threshold). "
            "(4) GAUSSIAN-BELL MIDTONE SIENNA REINFORCEMENT: Gaussian bell "
            "curve centered at earth_center with earth_sigma; first pass to "
            "use Gaussian bell for zone selection (prior passes use threshold "
            "clips); specific target raw sienna (0.72/0.38/0.12)."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

ANCHOR = '    # ── William Blake'
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, FECHIN_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: nicolai_fechin entry inserted.")
