"""Insert Lesser Ury entry into art_catalog.py (session 265).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

URY_ENTRY = '''
    # ── Lesser Ury ───────────────────────────────────────────────────────────────
    "lesser_ury": ArtStyle(
        artist="Lesser Ury",
        movement="German Impressionism / Post-Impressionism",
        nationality="German",
        period="1870–1931",
        palette=[
            (0.05, 0.06, 0.18),   # prussian blue night — deep shadow field
            (0.04, 0.04, 0.12),   # indigo black — total night shadow
            (0.78, 0.52, 0.18),   # amber gas-lamp — warm light source
            (0.82, 0.60, 0.30),   # warm cafe interior — window glow
            (0.42, 0.30, 0.12),   # amber cobblestone reflection
            (0.18, 0.18, 0.28),   # wet cobblestone — slicked dark pavement
            (0.88, 0.76, 0.60),   # lamp highlight — brightest specular
            (0.32, 0.28, 0.40),   # dusk violet — sky above street lamps
        ],
        ground_color=(0.06, 0.07, 0.16),    # prussian-tinted dark ground
        stroke_size=14,
        wet_blend=0.55,                      # impressionist blending, moderate wet
        edge_softness=0.45,                  # softened edges for atmospheric haze
        jitter=0.055,                        # moderate chromatic jitter
        glazing=None,
        crackle=False,
        chromatic_split=True,                # slight chromatic separation at edges
        technique=(
            "Berlin Nocturne: the wet street as mirror. Ury builds his paintings "
            "from two extreme poles — prussian blue shadow (cold, deep, total) and "
            "warm amber gaslight (intimate, pooled, spreading) — with little or no "
            "mid-range between them. The cobblestones are treated as a reflecting "
            "plane: the gas lamps and cafe windows above them produce elongated "
            "mirror images in the wet surface below, painted with long horizontal "
            "strokes of warm amber on the dark cobblestone field. Light sources "
            "have a characteristic double structure: the bright core of the lamp or "
            "window itself (painted in warm cream-amber, thick, loaded brush) and "
            "a surrounding atmospheric corona (soft warm ambient glow spreading into "
            "the prussian dark via thin, transparent glazes). The figures in Ury\'s "
            "street scenes are treated as silhouettes or near-silhouettes — their "
            "edges dissolved by the atmospheric spread of the surrounding gaslight "
            "corona. Ury never painted in plein air for his nocturnes; he worked "
            "from studio sketches made at night, which gave his paintings a "
            "concentrated, distilled quality — the perfect memory of night rather "
            "than the imperfect observation of it. His brushwork in the shadow zones "
            "is thin and transparent; in the light zones, thick and opaque; the "
            "contrast between these two surface qualities reinforces the luminance "
            "contrast of the gas lamp against the prussian dark."
        ),
        famous_works=[
            ("Im Cafe",                           "1892"),
            ("Nasse Berliner Strasse bei Nacht",  "1889"),
            ("Berliner Stadtbahn",                "1889"),
            ("Unter den Linden im Regen",         "1904"),
            ("Frau im Cafe",                      "1898"),
            ("Interieur (Im Theater)",            "1899"),
            ("Strassenzene in Berlin",            "1920"),
            ("Tiergarten im Herbst",              "1910"),
        ],
        inspiration=(
            "ury_nocturne_reflection_pass(): THREE-STAGE BERLIN NOCTURNE TECHNIQUE -- "
            "176th distinct mode. "
            "(1) WET PAVEMENT VERTICAL MIRROR REFLECTION: upper canvas sky_fraction "
            "flipped vertically, asymmetrically Gaussian-blurred (heavy horizontal for "
            "rain-elongated reflections, light vertical for softening), darkened by "
            "reflection_attenuation, composited into lower pavement_fraction to simulate "
            "wet cobblestone mirror reflections of gas lamps and cafe windows; "
            "(2) GAS-LAMP AMBER CORONA: luminance-gated warm-amber hue shift on bright "
            "pixels (adding amber_dr to R, amber_dg to G, subtracting amber_db_cut from B) "
            "followed by Gaussian diffusion at corona_sigma, simulating atmospheric spread "
            "of warm gaslight halos into prussian night air; "
            "(3) PRUSSIAN BLUE NIGHT-SHADOW COOLER: differential per-channel scaling "
            "(R*shadow_r_scale < 1, G*shadow_g_scale < 1, B + shadow_b_lift > 0) gated by "
            "shadow luminance mask, shifting sub-threshold darks toward prussian blue / indigo "
            "in the manner of Ury\'s characteristic night shadow hue."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

if '"lesser_ury"' in src:
    print("lesser_ury already in catalog -- nothing to do.")
    sys.exit(0)

INSERT_BEFORE = "\n}\n"
idx = src.rfind(INSERT_BEFORE)
if idx == -1:
    print("ERROR: could not find closing brace of CATALOG dict.")
    sys.exit(1)

new_src = src[:idx] + URY_ENTRY + src[idx:]

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("Inserted Lesser Ury into art_catalog.py.")
