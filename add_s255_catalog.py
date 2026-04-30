"""Insert andrew_wyeth entry into art_catalog.py (session 255).

Run once to modify art_catalog.py; preserved as a change record afterward.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))

WYETH_ENTRY = """    "andrew_wyeth": ArtStyle(
        artist="Andrew Wyeth",
        movement="American Realism / Regionalism",
        nationality="American",
        period="1917–2009",
        palette=[
            (0.82, 0.76, 0.62),   # dry straw / bleached grass
            (0.68, 0.56, 0.40),   # raw umber mid-tone
            (0.48, 0.40, 0.30),   # raw umber shadow
            (0.28, 0.24, 0.18),   # deep umber dark
            (0.86, 0.84, 0.78),   # titanium white / pale gesso
            (0.62, 0.58, 0.52),   # cool grey-stone
            (0.76, 0.62, 0.46),   # warm flesh-ochre
            (0.52, 0.46, 0.36),   # burnt sienna mid
            (0.44, 0.48, 0.54),   # cold blue-grey winter sky
            (0.38, 0.36, 0.30),   # dark olive ground
        ],
        ground_color=(0.72, 0.66, 0.52),    # dry warm ochre gesso
        stroke_size=6,
        wet_blend=0.22,                      # very dry -- tempera dries immediately
        edge_softness=0.18,                  # crisp -- tempera holds hard edges
        jitter=0.04,
        glazing=None,                        # tempera does not use oil glazes
        crackle=False,
        chromatic_split=False,
        technique=(
            "Andrew Wyeth (1917–2009, Chadds Ford, Pennsylvania) is among the "
            "most technically singular American painters of the twentieth "
            "century. Self-taught, the son of illustrator N. C. Wyeth, he spent "
            "his entire career working within a few square miles: the Brandywine "
            "Valley of Pennsylvania and Cushing, Maine. He worked almost "
            "exclusively in egg tempera on gessoed panel and dry-brush "
            "watercolour, choosing media that enforced severe discipline -- "
            "egg tempera dries on contact and cannot be reworked, blended, or "
            "reconstituted. Three technical signatures define Wyeth's work: "
            "(1) CHALKY DRY TEMPERA SURFACE -- egg tempera dries immediately "
            "on the gessoed panel, leaving a dry, chalky, slightly fibrous "
            "surface entirely unlike oil paint; Wyeth built extraordinary "
            "textural depth through cross-hatched, tightly controlled strokes "
            "that are individually invisible but collectively produce a surface "
            "with the quality of woven cloth or bleached bone; the tempera "
            "grain is most visible in the half-tones -- in the transition from "
            "light to dark across an old barn wall or a hillside of dried grass; "
            "(2) MIDTONE PRECISION AND TONAL RANGE DISCIPLINE -- Wyeth worked "
            "with a deeply restricted palette that rarely used pure black or "
            "brilliant white; his tonal range is concentrated in the mid-values, "
            "and within that range he achieved the finest possible "
            "differentiation -- the shadow side of a grass stem reads "
            "differently from the shadow side of the soil inches below it; this "
            "midtone precision is the result of the discipline of tempera, which "
            "requires each value to be mixed and applied precisely; "
            "(3) DRY-BRUSH WATERCOLOUR TEXTURE -- in his watercolour work, "
            "Wyeth used a near-pigment-starved brush dragged across rough cold-"
            "press paper; the pigment catches only on the peaks of the paper "
            "grain, leaving bare paper visible between the fibres; the result "
            "is a characteristic speckled or fibrous texture at tonal "
            "transitions where the brush lifts away from the surface before "
            "fully completing its stroke."
        ),
        famous_works=[
            ("Christina's World",       "1948"),
            ("Winter Fields",           "1942"),
            ("Wind from the Sea",       "1947"),
            ("Groundhog Day",           "1959"),
            ("Winter",                  "1946"),
            ("The Hunter",              "1943"),
            ("Soaring",                 "1950"),
            ("Brown Swiss",             "1957"),
            ("Spring Beauty",           "1943"),
        ],
        inspiration=(
            "wyeth_tempera_drybrush_pass(): ONE HUNDRED AND SIXTY-SIXTH "
            "(166th) distinct mode -- three-stage egg-tempera dry-surface "
            "simulation inspired by Wyeth's technique on gessoed panel -- "
            "(1) DRY CHALK SURFACE: apply horizontally-biased high-frequency "
            "noise in the luminance domain; asymmetric Gaussian blur "
            "sigma=(y=3.0, x=0.5) creates horizontal grain; noise amplitude "
            "chalk_amplitude applied uniformly to all three channels to "
            "preserve hue while adding chalky grain; first pass to apply "
            "directional asymmetric-blur luminance-domain noise to simulate "
            "the dry horizontal grain of egg tempera on gessoed panel; "
            "(2) MIDTONE PRECISION BAND CONTRAST: apply unsharp-mask local "
            "contrast (canvas - Gaussian_sigma8_blur) gated by a luminance "
            "band mask [midtone_low, midtone_high]; pixels inside the band "
            "receive contrast_strength of the local contrast; outside the band "
            "the correction ramps to zero over a 0.15 lum transition; first "
            "pass to apply luminance-band-gated unsharp-mask contrast "
            "enhancement targeting only the midtone zone for tonal precision; "
            "(3) DRY-BRUSH FIBER TRACES: in tonal transition zones "
            "[fiber_low_lum, fiber_high_lum], add a horizontally-blurred "
            "sparse noise field (sigma=(0, 1.5)); sparse activation at "
            "fiber_density fraction of pixels, blurred horizontally to create "
            "fiber-like runs; applied at fiber_brightness; first pass to "
            "generate a horizontally-blurred sparse noise field applied at "
            "tonal transition zones as a dry-brush fiber-trace simulation."
        ),
    ),
"""

CATALOG_FILE = os.path.join(REPO, "art_catalog.py")

with open(CATALOG_FILE, "r", encoding="utf-8") as f:
    src = f.read()

assert "andrew_wyeth" not in src, "andrew_wyeth already present in art_catalog.py"

INSERT_BEFORE = '    "paula_rego":'
assert INSERT_BEFORE in src, f"Anchor {INSERT_BEFORE!r} not found in art_catalog.py"

new_src = src.replace(INSERT_BEFORE, WYETH_ENTRY + INSERT_BEFORE)

with open(CATALOG_FILE, "w", encoding="utf-8") as f:
    f.write(new_src)

print("andrew_wyeth entry inserted into art_catalog.py")
