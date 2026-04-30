"""Insert Zao Wou-Ki entry into art_catalog.py (session 268).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

ZAO_WOU_KI_ENTRY = '''
    # ── Zao Wou-Ki ───────────────────────────────────────────────────────────
    "zao_wou_ki": ArtStyle(
        artist="Zao Wou-Ki",
        movement="Lyrical Abstraction / Chinese-French Abstract Expressionism",
        nationality="Chinese-French",
        period="1920-2013",
        palette=[
            (0.98, 0.88, 0.42),   # luminous gold — the radiant interior center
            (0.04, 0.06, 0.16),   # deep blue-black — peripheral ink void
            (0.88, 0.54, 0.12),   # amber ochre — warm transition zone
            (0.14, 0.22, 0.52),   # indigo — deep cool periphery
            (0.96, 0.72, 0.30),   # warm apricot — inner glow halo
            (0.32, 0.44, 0.68),   # cerulean blue — atmospheric mid-distance
            (0.60, 0.36, 0.14),   # burnt sienna — earth and rock forms
            (0.82, 0.80, 0.74),   # misty white — mist and void passages
            (0.22, 0.28, 0.40),   # slate grey — shadow zone transition
        ],
        ground_color=(0.92, 0.90, 0.84),    # warm cream-white — lyrical ground
        stroke_size=22,
        wet_blend=0.38,                      # atmospheric softness
        edge_softness=0.32,                  # dissolved lyrical edges
        jitter=0.050,                        # vital gestural energy
        glazing=None,
        crackle=False,
        chromatic_split=False,               # unified atmospheric field
        technique=(
            "Chinese-French Lyrical Abstraction. Zao Wou-Ki (Zhao Wuji, "
            "1920-2013) synthesised two traditions whose fundamental concerns "
            "proved identical: the Song Dynasty ink painting principle of xu "
            "(the void as active pictorial space) and the gestural field "
            "painting of American Abstract Expressionism. Both traditions "
            "organised the picture plane around the energy-relationship between "
            "mark and emptiness; Zao understood that the Shanghai brush tradition "
            "and the New York gesture tradition were solving the same problem by "
            "different means. His mature paintings (1954-2013) are organised "
            "around a LUMINOUS CENTER architecture: a zone of warm, golden, "
            "blinding light radiates from the interior of the canvas, surrounded "
            "by deep blue-black peripheral zones where calligraphic ink-like "
            "marks orbit the interior. Between center and edge, the colour "
            "temperature undergoes an extreme shift: warm orange-gold at the "
            "core, cool blue-indigo at the dark periphery. No horizon, no "
            "named forms, no narrative -- yet the eye reads the composition as "
            "a felt landscape: the luminous center as sun, sky, or valley light; "
            "the peripheral marks as mountain, rock, storm. This landscape "
            "reading arises from compositional logic, not depicted form. Zao "
            "called his paintings \'windows onto the imaginary\' -- frames that "
            "open onto felt rather than depicted space. He trained at the "
            "Hangzhou Academy under Lin Fengmian, arrived in Paris 1948, and "
            "absorbed Cézanne, Klee, Matisse, Hartung, and de Kooning without "
            "sacrificing the calligraphic energy of the Chinese brush tradition. "
            "His later triptychs (1970s-2000s) achieve panoramic scale while "
            "maintaining the luminous-center / dark-periphery architecture."
        ),
        famous_works=[
            ("10.05.60",                     "1960"),
            ("Hommage a Matisse",             "1986"),
            ("01.01.68",                      "1968"),
            ("Triptych, 1969",               "1969"),
            ("Juin-octobre 1985",             "1985"),
            ("A Pierre Reverdy",             "1971"),
            ("Sans titre (11.09.06)",         "2006"),
            ("Triptych -- Hommage a Henri Matisse", "1986"),
        ],
        inspiration=(
            "zao_wou_ki_ink_atmosphere_pass(): FOUR-STAGE LYRICAL ABSTRACTION "
            "TECHNIQUE -- 179th distinct mode. "
            "(1) LUMINOUS CENTER DETECTION AND RADIAL GLOW: locate the painted "
            "luminance peak via Gaussian-smoothed luminance argmax; build a "
            "content-aligned radial glow field from that peak; amplify brightness "
            "and warmth in the detected light zone without imposing a fixed "
            "compositional center; "
            "(2) DARK PERIPHERAL VIGNETTE TOWARD BLUE-BLACK: non-linear "
            "(power-1.5) peripheral darkening centered on the detected luminous "
            "peak toward deep blue-black (0.04/0.06/0.14), creating the "
            "asymmetric dark surround of Zao\'s luminous-center compositions; "
            "(3) DUAL THERMAL COLOR FIELD: luminance-proportional hue shift "
            "toward gold in bright zones (lum > 0.55) and toward blue-indigo "
            "in dark zones (lum < 0.35), with shift magnitude proportional to "
            "tonal depth -- first pass to apply opposite hue rotations "
            "simultaneously to both bright and dark zones scaled by luminance; "
            "(4) INK CALLIGRAPHIC STREAK SYNTHESIS: gestural ink marks placed "
            "in the peripheral zone (beyond radial threshold), oriented "
            "tangentially to the radial field from the detected luminous center "
            "with angular noise, rendered as anti-aliased Gaussian line segments."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"zao_wou_ki"' in src:
    print("zao_wou_ki already in catalog -- nothing to do.")
    sys.exit(0)

INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + ZAO_WOU_KI_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Zao Wou-Ki into art_catalog.py.")
