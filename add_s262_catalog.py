"""Insert edouard_vuillard entry into art_catalog.py (session 262).

Run once to modify art_catalog.py; preserved as a change record afterward.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))

VUILLARD_ENTRY = """    "edouard_vuillard": ArtStyle(
        artist="Édouard Vuillard",
        movement="Nabi / Post-Impressionist Intimism",
        nationality="French",
        period="1868–1940",
        palette=[
            (0.78, 0.66, 0.42),   # cardboard ochre -- peinture à la colle warm ground
            (0.62, 0.52, 0.38),   # amber shadow -- mid-warm interior shadow tone
            (0.84, 0.76, 0.60),   # warm cream -- lit plaster and tabletop
            (0.48, 0.42, 0.35),   # dark warm brown -- furniture and wood shadow
            (0.72, 0.68, 0.58),   # dusty mid-ochre -- wallpaper ground tone
            (0.56, 0.62, 0.48),   # sage-olive -- fabric and foliage accent
            (0.68, 0.44, 0.38),   # terracotta -- warm accent in textile pattern
            (0.38, 0.35, 0.30),   # deep warm charcoal -- door frame and deep shadow
            (0.86, 0.82, 0.70),   # pale warm highlight -- lit curtain or tablecloth
            (0.52, 0.58, 0.64),   # muted blue-grey -- cooler shadow accent
        ],
        ground_color=(0.72, 0.62, 0.44),    # warm cardboard ochre -- peinture à la colle
        stroke_size=5,
        wet_blend=0.24,
        edge_softness=0.58,
        jitter=0.016,
        glazing=(0.80, 0.74, 0.56),    # warm amber unifying veil
        crackle=False,
        chromatic_split=False,
        technique=(
            "Édouard Vuillard (1868-1940), member of the Nabi group with "
            "Bonnard and Sérusier, developed a style of domestic intimism "
            "unlike any other painter's.  His defining achievement is the "
            "DISSOLUTION OF BOUNDARY between figure and environment: in his "
            "interiors, a woman's blouse cannot be distinguished from the "
            "wallpaper behind her, a tablecloth merges into the floor, a brooch "
            "is the same colour as a picture frame.  "
            "Three techniques create this quality: "
            "(1) LOCAL HUE AVERAGING -- Vuillard perceived and painted the "
            "AVERAGE local hue rather than the precise hue of each individual "
            "object.  He would mix a colour drawn from a wide local sample "
            "of the scene and apply it consistently across figure and background "
            "alike.  Hard hue boundaries between object and background dissolve: "
            "both share a common local chromatic field.  This is the mechanism "
            "that makes a figure at Vuillard 'disappear' into the room -- not "
            "through loss of form but through shared hue; "
            "(2) WARM OCHRE GROUND PENETRATION -- Vuillard frequently painted "
            "in PEINTURE À LA COLLE (distemper on cardboard), a matte, dry "
            "medium.  The warm ochre-brown of the unprepared cardboard reads "
            "through all subsequent layers, giving his interiors a warm amber-"
            "yellow undertone in the midtone range.  Bright highlights remain "
            "cool (thinnest paint); deep shadows remain cool (darkest underpaint); "
            "but the midtone range is warmed by the ground penetrating the thin "
            "distemper layer; "
            "(3) MATTE DISTEMPER SURFACE GRAIN -- peinture à la colle produces "
            "a characteristically matte, powdery surface.  Individual marks are "
            "not visible as brushstrokes but as faint tonal variations in the "
            "dried distemper layer.  The grain is isotropic and fine; it reads "
            "as a warm, velvety skin rather than directional brushwork.  "
            "Together these three qualities create the sensation of being inside "
            "one of Vuillard's rooms: warm, patterned, dense, and perfectly still."
        ),
        famous_works=[
            ("The Dinner Table",                     "1892"),
            ("The Seamstress",                       "1893"),
            ("Mother and Sister of the Artist",      "1893"),
            ("Interior with Pink Wallpaper I",       "1898"),
            ("The Mantelpiece",                      "1905"),
            ("Woman in a Striped Dress",             "1895"),
            ("Under the Lamp",                       "1892"),
            ("The Conversation",                     "1892"),
            ("The Flowered Dress",                   "1891"),
            ("Lunch at Vasouy",                      "1901"),
        ],
        inspiration=(
            "vuillard_chromatic_dissolution_pass -- ONE HUNDRED AND "
            "SEVENTY-THIRD distinct painting mode (session 262).  "
            "Three-stage intimist pattern dissolution model: "
            "(1) LOCAL HUE AVERAGING: Gaussian blur of HSV hue channel "
            "(via circular sin/cos encoding to handle wraparound) at "
            "hue_blur_sigma=12, blended at hue_blend=0.55, creating "
            "Vuillard's dissolution of hue boundaries between figure and "
            "background (novel: first pass to spatially average only the "
            "hue channel via circular blur, not affecting S or V); "
            "(2) WARM OCHRE MIDTONE PENETRATION: Gaussian bell centred at "
            "lum=(ochre_lum_lo+ochre_lum_hi)/2=0.535, sigma=0.0925, blending "
            "midtone pixels toward cardboard ochre (0.78, 0.66, 0.42) at "
            "ochre_strength=0.22, modelling peinture-à-la-colle ground "
            "penetration (novel: first pass to use this specific ochre target "
            "with lum-range-derived Gaussian bell); "
            "(3) MATTE DISTEMPER GRAIN: achromatic grain (same Gaussian-smoothed "
            "noise added to all three channels) at grain_amplitude=0.028, "
            "grain_sigma=0.8, producing luminance-only grain without hue shift "
            "(novel: first pass to produce achromatic grain by adding identical "
            "noise to R, G, B, as opposed to per-channel chromatic grain)."
        ),
    ),
"""

CATALOG_FILE = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_FILE, "r", encoding="utf-8") as f:
    src = f.read()

if '"edouard_vuillard"' in src:
    print("edouard_vuillard already present -- skipping.")
    sys.exit(0)

# Insert before the last closing brace of CATALOG dict
ANCHOR = "\n}\n"
if ANCHOR not in src:
    ANCHOR = "\n}"
if ANCHOR not in src:
    print("ERROR: could not find catalog closing brace")
    sys.exit(1)

last_pos = src.rfind(ANCHOR)
src = src[:last_pos] + "\n" + VUILLARD_ENTRY + src[last_pos:]

with open(CATALOG_FILE, "w", encoding="utf-8") as f:
    f.write(src)

print("edouard_vuillard inserted into art_catalog.py successfully.")
