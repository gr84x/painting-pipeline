"""Insert George Grosz entry into art_catalog.py (session 284).

Run once. Preserved as a change record afterward.

Note: oskar_kokoschka already existed in the catalog from a prior session.
This session adds george_grosz as the 195th mode artist, with the
grosz_neue_sachlichkeit_pass implementing his New Objectivity style.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

GROSZ_ENTRY = '''
    # ── George Grosz ──────────────────────────────────────────────────────────
    "george_grosz": ArtStyle(
        artist="George Grosz",
        movement="German Expressionism / Neue Sachlichkeit (New Objectivity) / Berlin Dada",
        nationality="German (later American)",
        period="1893-1959",
        palette=[
            (0.78, 0.84, 0.14),   # acid yellow-green -- Grosz's sickly Weimar flesh
            (0.90, 0.22, 0.14),   # cadmium vermillion -- violence, lust, emergency
            (0.12, 0.10, 0.20),   # near-black deep -- heavy contour line, cast shadow
            (0.72, 0.58, 0.28),   # ochre-tan -- bourgeois flesh, bureaucratic drab
            (0.18, 0.26, 0.48),   # prussian blue -- night, uniform, cold machinery
            (0.88, 0.80, 0.56),   # straw-buff -- paper, wall, weak winter daylight
            (0.48, 0.12, 0.12),   # dark crimson -- blood, morality, official wax seal
            (0.36, 0.48, 0.22),   # olive-green -- military, decay, overgrown ruin
            (0.82, 0.74, 0.52),   # warm parchment -- document, skin, aged plaster
            (0.10, 0.08, 0.16),   # warm dark -- deep shadow with ground show-through
        ],
        ground_color=(0.36, 0.28, 0.18),     # warm raw umber ground (Grosz's toned support)
        stroke_size=9,
        wet_blend=0.24,
        edge_softness=0.10,
        jitter=0.018,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "German Expressionism / Neue Sachlichkeit / Berlin Dada. "
            "George Grosz (1893-1959) was born in Berlin and studied in Dresden "
            "and Berlin before the First World War. The war and the Weimar Republic "
            "that followed -- with its inflation, street violence, feverish "
            "decadence, and latent fascism -- became the raw material of his "
            "entire artistic practice. He was a founding member of Berlin Dada "
            "(1918) and a central figure in the Neue Sachlichkeit (New Objectivity). "
            "He was prosecuted three times for offences against public morality. "
            "In 1933, the day after Hitler came to power, Grosz emigrated to the "
            "United States, where he taught in New York until 1959. He returned "
            "to Germany the year of his death. "
            "GROSZ'S FIVE TECHNICAL SIGNATURES: "
            "(1) DIRECTIONAL CAST SHADOW LINE: raking light from upper-left casts "
            "heavy dark lines on the right/lower edges of every form, creating a "
            "graphic, paper-cut quality rather than volumetric modelling. "
            "(2) FLAT ZONE GRAPHIC UNIFICATION: between the dark contour lines, "
            "relatively flat, smooth areas of uniform colour -- poster-like, "
            "type-identifying, not individualising. "
            "(3) ACID YELLOW-GREEN PALETTE: sickly, jaundiced colours suggesting "
            "disease, moral corruption, and poisoned atmosphere. Cadmium yellow-"
            "green flesh, garish vermillion accents, prussian blue shadows. "
            "(4) DEEP SHADOW OPACITY WITH WARM GROUND SHOW-THROUGH: the darkest "
            "regions pushed toward a deep warm dark, with the painted ground "
            "slightly visible, giving shadows substance and weight. "
            "(5) GAMMA-EXPANDED MID-TONES (Harsh Fluorescent Clarity): the tonal "
            "curve is expanded with gamma < 1.0, lifting mid-values to model "
            "the harsh, remorseless, over-lit quality of Grosz's Weimar daylight. "
            "THE GREAT WORKS: 'Pillars of Society' (1926) -- a gallery of Weimar "
            "German types, each displaying their hypocrisy in face and posture; "
            "'The Funeral / Dedication to Oskar Panizza' (1917-18) -- Bruegel-like "
            "urban chaos in lurid colour; 'Eclipse of the Sun' (1926) -- a headless "
            "general taking orders from a businessman; 'Metropolis' (1916-17) -- "
            "Berlin as a collision of human types and industrial architecture."
        ),
        famous_works=[
            ("Pillars of Society",                                     "1926"),
            ("The Funeral (Dedication to Oskar Panizza)",              "1917-18"),
            ("Eclipse of the Sun",                                     "1926"),
            ("Metropolis",                                             "1916-17"),
            ("The Agitator",                                           "1928"),
            ("Republican Automatons",                                  "1920"),
            ("Grey Day",                                               "1921"),
            ("The Poet Max Herrmann-Neisse",                           "1927"),
            ("Big City",                                               "1916-17"),
            ("Peace II",                                               "1946"),
        ],
        inspiration=(
            "grosz_neue_sachlichkeit_pass(): FOUR-STAGE NEW OBJECTIVITY SYSTEM "
            "-- 195th distinct mode. "
            "(1) SIGNED-Gx DIRECTIONAL CAST SHADOW EDGE: Gx = d/dx(L), Gy = d/dy(L); "
            "shadow_edge_mask = clip(-Gx_norm, 0, 1) * G_norm; "
            "darken shadow side of edges: R1 = R * (1 - shadow_edge_mask * shadow_darken); "
            "FIRST PASS to use SIGNED gradient component (signed Gx, not just |G|) "
            "to model a directed illumination field -- prior passes use G_mag only. "
            "(2) INTERIOR ZONE FLATTENING: interior_mask = 1 - G_norm; "
            "R2 = R1 + interior * flat_strength * (Gaussian(R1, zone_sigma) - R1); "
            "spatial smoothing gated to low-gradient interior zones. "
            "(3) ACID COLOUR PUSH: green-dominance gate = clip((G - max(R,B)) / 0.10, 0, 1); "
            "× mid-bell gate [0.35-0.80]; push toward cadmium yellow-green (0.78/0.84/0.14); "
            "FIRST PASS to use per-channel colour dominance metric (G > max(R,B)) as gate. "
            "(4) GAMMA TONAL EXPANSION: L3_gamma = L3^gamma (gamma=0.80); "
            "scale = L3_gamma / L3; R4 = R3 * scale; "
            "FIRST PASS to apply power-law gamma correction to tonal range. "
            "gamma < 1 lifts mid-tones (harsh fluorescent quality of Grosz's Weimar)."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

assert "george_grosz" not in src, "george_grosz already exists in art_catalog.py"

ANCHOR = "\n\n}\n\n\ndef get_style"
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, GROSZ_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: george_grosz entry inserted.")
