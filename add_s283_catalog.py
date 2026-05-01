"""Insert Albert Bierstadt entry into art_catalog.py (session 283).

Run once. Preserved as a change record afterward.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.abspath(__file__))

BIERSTADT_ENTRY = '''
    # ── Albert Bierstadt ──────────────────────────────────────────────────────
    "albert_bierstadt": ArtStyle(
        artist="Albert Bierstadt",
        movement="American Luminism / Hudson River School / Rocky Mountain School",
        nationality="German-American",
        period="1830-1902",
        palette=[
            (0.92, 0.88, 0.68),   # Bierstadt horizon -- warm cream-gold near-horizon sky
            (0.14, 0.18, 0.42),   # deep ultramarine zenith -- dramatic dark sky
            (0.94, 0.74, 0.30),   # Bierstadt amber -- the theatrical golden middle-distance haze
            (0.38, 0.42, 0.52),   # cool blue-grey mountain -- far distance in aerial perspective
            (0.12, 0.16, 0.10),   # dark pine black-green -- dense conifer forest silhouette
            (0.92, 0.92, 0.94),   # mountain snow -- brilliant white on high peaks
            (0.68, 0.54, 0.30),   # warm amber mountain -- near ridgeline in golden light
            (0.44, 0.52, 0.64),   # lake reflection -- cool still water mirroring sky
            (0.44, 0.28, 0.14),   # foreground umber -- warm earth shadow in near zone
            (0.60, 0.56, 0.22),   # golden meadow -- autumn grass in valley sunlight
        ],
        ground_color=(0.62, 0.58, 0.42),     # warm amber-ochre ground
        stroke_size=18,
        wet_blend=0.28,
        edge_softness=0.22,
        jitter=0.032,
        glazing=(0.94, 0.78, 0.38),
        crackle=False,
        chromatic_split=False,
        technique=(
            "American Luminism, Hudson River School, Rocky Mountain School. "
            "Albert Bierstadt (1830-1902) was born in Solingen, Germany and "
            "emigrated with his family to New Bedford, Massachusetts at age two. "
            "He studied painting in Dusseldorf (1853-1857), absorbing the German "
            "Romantic tradition of dramatic chiaroscuro and theatrical landscape "
            "treatment. He joined the Clarence King Rocky Mountain survey in 1859, "
            "making hundreds of oil sketches from nature, then produced enormous "
            "studio canvases (some 6x10 feet) that made him the most commercially "
            "successful American painter of his era. "
            "BIERSTADT'S FOUR PICTORIAL SYSTEMS: "
            "(1) LUMINOUS HORIZON ARCHITECTURE: The sky brightens toward the "
            "horizon, reversing the normal daylight sky gradient. The ZENITH is "
            "the darkest zone -- deep ultramarine blue or storm cloud grey; the "
            "HORIZON is the brightest -- warm cream, pale gold, or brilliant white "
            "as low-angle sunlight scatters through the atmospheric column. This "
            "zenith-dark/horizon-bright structure arises from his characteristic "
            "subject: storms with open sky near the horizon and dark clouds overhead. "
            "(2) THEATRICAL AMBER MIDDLE-DISTANCE HAZE: The most immediately "
            "recognizable Bierstadt color -- warm amber-gold pervading the middle "
            "distance between near mountains and sky, where dust, moisture, and "
            "late-afternoon light combine. Critics called it melodramatic; the public "
            "called it sublime. 'Bierstadt gold' is his signature palette note. "
            "(3) COOL ZENITH / WARM HORIZON COLOR OPPOSITION: The extreme color "
            "temperature contrast between ultramarine zenith and warm golden "
            "horizon frames the amber middle zone, making it appear warmer "
            "by simultaneous contrast. This opposition creates the sense of "
            "divine theatrical light that defines his mature compositions. "
            "(4) WARM UMBER FOREGROUND SHADOW: In near-zone shadows -- dark "
            "ground, rock faces, forest floor -- Bierstadt applied warm umber- "
            "sienna rather than neutral grey, creating a coherent warm interior "
            "light quality that makes his paintings glow from within. "
            "LEGACY: Bierstadt's paintings were among the highest-priced works "
            "by any living American artist in the 1860s-1870s. His enormous "
            "canvases toured as standalone exhibitions with paid admission. "
            "Luminism critic John Baur identified in his work the defining "
            "quality of American Luminism: 'light from within, the painting "
            "itself becoming a source of illumination.'"
        ),
        famous_works=[
            ("The Rocky Mountains, Lander's Peak",  "1863"),
            ("Storm in the Rocky Mountains, Mt. Rosalie", "1866"),
            ("Among the Sierra Nevada, California", "1868"),
            ("Sunset in the Yosemite Valley",       "1868"),
            ("The Domes of the Yosemite",            "1867"),
            ("Cotopaxi",                             "1862"),
            ("Looking Down Yosemite Valley",         "1865"),
            ("The Last of the Buffalo",              "1888"),
            ("Cho-looke, the Yosemite Fall",         "1864"),
            ("Mount Corcoran",                       "1876-1877"),
        ],
        inspiration=(
            "bierstadt_luminous_glory_pass(): FOUR-STAGE LUMINOUS ARCHITECTURE "
            "-- 194th distinct mode. "
            "(1) LUMINOUS HORIZON UPLIFT: in top sky_zone fraction, a horizon_weight "
            "that INCREASES toward bottom of sky (inverted spatial gradient within "
            "bounded zone); bright pixels pushed toward warm cream-gold; first pass "
            "to apply an inverted spatial weight inside a bounded upper zone. "
            "(2) COOL ULTRAMARINE ZENITH: in top zenith_fraction, low-luminance "
            "pixels pushed toward deep ultramarine; (spatial top) x (low luminance) "
            "gate; paired with stage 4 as geometric complement. "
            "(3) WARM AMBER MIDDLE-DISTANCE HAZE: triple gate (spatial mid-zone x "
            "luminance bell x low-saturation gate); first triple-gated single-zone "
            "operation; saturation gate prevents contamination of already-colored "
            "scene elements; pushes toward Bierstadt amber (0.94/0.74/0.30). "
            "(4) WARM UMBER FOREGROUND SHADOW: (spatial bottom zone) x (low "
            "luminance gate); geometric inverse of stage 2 (dark+top=cool, "
            "dark+bottom=warm); the dark-zone temperature inversion duality "
            "between stages 2 and 4 is the architecturally novel contribution."
        ),
    ),
'''

CATALOG_PATH = os.path.join(REPO, "art_catalog.py")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    src = f.read()

# Verify no duplicate
assert "albert_bierstadt" not in src, "albert_bierstadt already exists in art_catalog.py"

# Insert before the closing brace of CATALOG dict
ANCHOR = "\n\n}\n\n\ndef get_style"
assert ANCHOR in src, f"Anchor not found in art_catalog.py: {ANCHOR!r}"

new_src = src.replace(ANCHOR, BIERSTADT_ENTRY + ANCHOR, 1)

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(new_src)

print("art_catalog.py patched: albert_bierstadt entry inserted.")
