"""Insert Ilya Repin entry into art_catalog.py (session 283).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

REPIN_ENTRY = '''
    # ── Ilya Repin ────────────────────────────────────────────────────────────
    "ilya_repin": ArtStyle(
        artist="Ilya Repin",
        movement="Russian Realism / Peredvizhniki",
        nationality="Ukrainian-Russian",
        period="1844-1930",
        palette=[
            (0.70, 0.50, 0.32),   # warm umber-flesh -- Repin's lit midtone; lit skin and earth
            (0.28, 0.28, 0.48),   # cool violet-shadow -- transparent shadow glaze
            (0.54, 0.38, 0.22),   # raw sienna -- mid-dark flesh and worn cloth
            (0.82, 0.72, 0.52),   # straw gold -- sunlit fabric highlights and warm sky
            (0.22, 0.20, 0.18),   # dark umber -- deepest shadow, hair, dark ground
            (0.88, 0.82, 0.70),   # chalk-cream -- bright highlight on lit forehead and collar
            (0.46, 0.50, 0.58),   # grey-silver -- Volga water, overcast sky, worn linen
            (0.38, 0.30, 0.20),   # dark burnt sienna -- shadow transition, clothing darks
            (0.64, 0.56, 0.40),   # ochre-grey -- dried steppe grass, earth, weathered wood
            (0.34, 0.36, 0.44),   # cool mid-shadow -- eye-socket, collar shadow, indoors dark
        ],
        ground_color=(0.58, 0.44, 0.30),     # warm burnt umber ground (Repin's toned canvas)
        stroke_size=10,
        wet_blend=0.28,
        edge_softness=0.14,
        jitter=0.022,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Russian Realism, Peredvizhniki. "
            "Ilya Yefimovich Repin (1844-1930) was born in Chuguev, Ukraine "
            "to a military settler family. His talent emerged early; he received "
            "his first training in Chuguev before entering the Imperial Academy "
            "of Arts in St. Petersburg in 1864. His 1871 graduation painting "
            "earned him the major gold medal and a scholarship to Europe. He "
            "spent 1873-1876 in Paris, studying Impressionism but ultimately "
            "rejecting its primacy of optical sensation over psychological truth. "
            "Back in Russia, he joined the Peredvizhniki -- the Wanderers -- and "
            "devoted his career to painting Russian life with unflinching, "
            "compassionate realism. He is universally regarded as the supreme "
            "figurative painter in Russian art history. "
            "REPIN'S FIVE TECHNICAL-PSYCHOLOGICAL SIGNATURES: "
            "(1) FORM-FOLLOWING DIRECTIONAL IMPASTO: Repin oriented his brushstrokes "
            "to follow the planes of his subjects' forms -- strokes along the "
            "cheek plane lie parallel to the cheekbone; strokes on the brow "
            "follow the orbital arch. The paint reads as surface, not pigment. "
            "(2) MIDTONE WARM UMBER-FLESH: Repin's lit surfaces carry a specific "
            "warm umber in the middle values -- raw sienna with a flesh undertone "
            "(approx. 0.70/0.50/0.32 RGB). This is where his subjects' character lives. "
            "(3) COOL TRANSPARENT SHADOW GLAZES: Repin's shadows are never opaque. "
            "He glazed cool blue-violets (approx. 0.28/0.28/0.48 RGB) over his "
            "shadow passages, allowing the warm ground to show through. Shadows "
            "feel airy, filled with reflected light, never dead or flat. "
            "(4) FORM-PLANE DIRECTIONAL SOFTENING: Within each broad plane, "
            "Repin applied slightly directional strokes that blur along the "
            "plane rather than across it, creating smooth surfaces within planes "
            "while keeping inter-plane edges structurally sharp. "
            "(5) PSYCHOLOGICAL EDGE CRISPENING: The character-defining edges "
            "(jaw, brow arc, collar) are the sharpest elements in Repin's work. "
            "He deliberately maintained these structural edges while allowing "
            "non-structural passages to remain softly merged. The sharpest edge "
            "directs the eye to the deepest psychological content. "
            "THE GREAT WORKS: 'Barge Haulers on the Volga' (1873) -- eleven burlaki "
            "pulling a steamship upriver; the central figure Kanin, a former priest, "
            "with concentrated psychological complexity. 'Ivan the Terrible and His "
            "Son Ivan' (1885) -- the Tsar cradling his son after striking him, "
            "a mask of horror and remorse. 'They Did Not Expect Him' (1884) -- "
            "the return of a political exile, the moment of recognition frozen "
            "in unbearable suspension. 'Reply of the Zaporozhian Cossacks' (1891) -- "
            "rough warriors composing an insolent reply to the Ottoman Sultan, every "
            "face psychologically distinct."
        ),
        famous_works=[
            ("Barge Haulers on the Volga",              "1873"),
            ("Ivan the Terrible and His Son Ivan",      "1885"),
            ("They Did Not Expect Him",                 "1884"),
            ("Reply of the Zaporozhian Cossacks",       "1891"),
            ("Portrait of Leo Tolstoy",                 "1887"),
            ("Portrait of Modest Musorgsky",            "1881"),
            ("Sadko",                                   "1876"),
            ("Portrait of Pavel Tretyakov",             "1883"),
            ("Krestny Khod in Kursk Province",          "1883"),
            ("Arrest of a Propagandist",                "1880-1892"),
        ],
        inspiration=(
            "repin_character_depth_pass(): FOUR-STAGE PSYCHOLOGICAL REALISM SYSTEM "
            "-- 194th distinct mode. "
            "(1) GRADIENT-ORIENTATION FORM BLUR: compute Gx, Gy from L; "
            "G_norm = |G|/percentile(|G|,80); apply isotropic Gaussian blur "
            "(sigma=form_blur_sigma) weighted by G_norm * form_blend; "
            "first pass to use LOCAL GRADIENT MAGNITUDE to gate a form-smoothing "
            "step, approximating direction-following brushwork without per-pixel "
            "directional filtering. "
            "(2) MIDTONE WARM UMBER ACCENT: bell-gate mask (mid_lo=0.30, mid_hi=0.62); "
            "push toward warm umber-flesh (0.70/0.50/0.32); Repin's specific "
            "midtone palette identity; distinct from savrasov cool-grey (s282) "
            "by both gate range and target color. "
            "(3) COOL TRANSPARENT SHADOW DEEPENING: smoothstep shadow mask "
            "(shadow_thresh=0.32); push toward cool violet (0.28/0.28/0.48); "
            "fixed artist-specific target (vs. shadow_temperature_pass s281 "
            "which adapts target from scene highlight data). "
            "(4) STRUCTURAL EDGE CRISPENING: gradient magnitude percentile gate; "
            "tight unsharp mask (sigma=1.1, amount=0.50); recovers character-defining "
            "edges after the form-blur and color stages; first pass to end with "
            "a gradient-gated USM as the psychological-edge finalizer."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

assert "ilya_repin" not in src, "ilya_repin already exists in art_catalog.py"

ANCHOR = "\n\n}\n\n\ndef get_style"
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, REPIN_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: ilya_repin entry inserted.")
