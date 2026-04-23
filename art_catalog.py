"""
art_catalog.py — A catalog of famous paintings, artists, and their characteristic styles.

Usage
-----
from art_catalog import CATALOG, ArtStyle, get_style

style = get_style("seurat")
print(style.technique)

# All artists
for name, s in CATALOG.items():
    print(name, "—", s.movement)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

Color = Tuple[float, float, float]


@dataclass
class ArtStyle:
    """
    Describes the characteristic technique and palette of an artist or movement.

    palette         : key pigment colours as (R, G, B) floats in [0, 1]
    ground_color    : typical toned ground / canvas colour
    stroke_size     : characteristic stroke or mark size (small = detail-oriented)
    wet_blend       : how much wet-on-wet blending; 0 = dry/broken, 1 = very blended
    edge_softness   : 0 = crisp edges, 1 = full soft fusion (sfumato)
    jitter          : colour variation per stroke
    glazing         : colour of final unifying glaze, or None
    crackle         : whether aged-crackle finish is appropriate
    chromatic_split : apply divisionist complementary-dot splitting
    technique       : prose description of the defining technique
    famous_works    : list of (title, year) for context
    inspiration     : what to take from this style in the pipeline
    """
    artist:         str
    movement:       str
    nationality:    str
    period:         str   # e.g. "1880–1910"
    palette:        List[Color]
    ground_color:   Color
    stroke_size:    float
    wet_blend:      float
    edge_softness:  float
    jitter:         float
    glazing:        Optional[Color]
    crackle:        bool
    chromatic_split: bool
    technique:      str
    famous_works:   List[Tuple[str, str]]   # (title, year)
    inspiration:    str


# ─────────────────────────────────────────────────────────────────────────────
# Catalog entries
# ─────────────────────────────────────────────────────────────────────────────

CATALOG: Dict[str, ArtStyle] = {

    # ── Leonardo da Vinci ──────────────────────────────────────────────────────
    "leonardo": ArtStyle(
        artist="Leonardo da Vinci",
        movement="High Renaissance",
        nationality="Italian",
        period="1480–1519",
        palette=[
            (0.78, 0.63, 0.45),   # warm flesh — raw sienna base
            (0.52, 0.43, 0.29),   # mid-tone shadow
            (0.22, 0.18, 0.10),   # deep umber shadow
            (0.60, 0.55, 0.40),   # sfumato haze
            (0.38, 0.46, 0.35),   # landscape green distance
            (0.55, 0.60, 0.52),   # aerial blue-grey far distance
        ],
        ground_color=(0.55, 0.47, 0.30),    # warm ochre imprimatura
        stroke_size=5,
        wet_blend=0.92,                      # heavy blending — no visible brushmarks
        edge_softness=0.95,                  # sfumato: edges dissolve into smoke
        jitter=0.015,
        glazing=(0.62, 0.52, 0.32),          # amber unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Sfumato — edges dissolved in imperceptible transitions 'like smoke'. "
            "No hard outlines; forms emerge from deeply blended shadow."
        ),
        famous_works=[
            ("Mona Lisa", "c. 1503–1519"),
            ("Virgin of the Rocks", "1483–1486"),
            ("Lady with an Ermine", "c. 1489–1491"),
        ],
        inspiration=(
            "Maximise wet_blend and edge_softness to make boundaries disappear. "
            "Warm amber glaze over the whole surface unifies all flesh tones."
        ),
    ),

    # ── Rembrandt van Rijn ─────────────────────────────────────────────────────
    "rembrandt": ArtStyle(
        artist="Rembrandt van Rijn",
        movement="Dutch Golden Age / Baroque",
        nationality="Dutch",
        period="1620–1669",
        palette=[
            (0.82, 0.68, 0.48),   # highlight flesh — naples yellow-red
            (0.60, 0.44, 0.25),   # mid-tone flesh
            (0.30, 0.20, 0.10),   # deep Vandyke brown shadow
            (0.08, 0.05, 0.02),   # near-black background
            (0.70, 0.55, 0.30),   # warm light on objects
        ],
        ground_color=(0.18, 0.12, 0.06),    # very dark brown ground
        stroke_size=8,
        wet_blend=0.30,
        edge_softness=0.60,
        jitter=0.04,
        glazing=(0.50, 0.35, 0.10),          # deep amber varnish effect
        crackle=True,
        chromatic_split=False,
        technique=(
            "Chiaroscuro and impasto highlights. Broad dark grounds with luminous "
            "impasto whites and flesh tones built up in thick paste on the lit side. "
            "Characteristic single Rembrandt triangle of light on the shadow cheek."
        ),
        famous_works=[
            ("Self-Portrait with Two Circles", "c. 1665–1669"),
            ("The Night Watch", "1642"),
            ("The Anatomy Lesson of Dr. Nicolaes Tulp", "1632"),
        ],
        inspiration=(
            "Dark toned ground. Very high contrast. place_lights() with large "
            "impasto dots only on the true specular peaks (lum^4.5 weighting)."
        ),
    ),

    # ── Johannes Vermeer ──────────────────────────────────────────────────────
    "vermeer": ArtStyle(
        artist="Johannes Vermeer",
        movement="Dutch Golden Age",
        nationality="Dutch",
        period="1653–1675",
        palette=[
            (0.82, 0.72, 0.52),   # warm window light on skin
            (0.60, 0.52, 0.38),   # mid-flesh
            (0.22, 0.30, 0.55),   # ultramarine blue (expensive lapis)
            (0.78, 0.65, 0.25),   # golden yellow ochre fabric
            (0.35, 0.40, 0.30),   # natural green shadow
            (0.85, 0.80, 0.70),   # pearl / creamy white highlight
        ],
        ground_color=(0.40, 0.35, 0.22),    # mid warm imprimatura
        stroke_size=6,
        wet_blend=0.45,
        edge_softness=0.75,
        jitter=0.020,
        glazing=(0.72, 0.65, 0.45),          # warm window-light glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Single north-facing window light; cool diffuse shadows. Luminous, "
            "smooth flesh against saturated costumes. Pointillist-like light dots "
            "('Vermeer pearls') on highlight areas suggest diffused specular glow."
        ),
        famous_works=[
            ("Girl with a Pearl Earring", "c. 1664–1665"),
            ("The Milkmaid", "c. 1657–1658"),
            ("Woman Reading a Letter", "c. 1663"),
        ],
        inspiration=(
            "place_lights() with very small bright dots ('pearls') on edges of "
            "highlights. Cool shadows, warm lights — a 2:1 warm/cool split."
        ),
    ),

    # ── Caravaggio ────────────────────────────────────────────────────────────
    "caravaggio": ArtStyle(
        artist="Michelangelo Merisi da Caravaggio",
        movement="Baroque",
        nationality="Italian",
        period="1592–1610",
        palette=[
            (0.84, 0.68, 0.44),   # candlelit flesh highlight
            (0.45, 0.28, 0.12),   # mid-tone brown shadow
            (0.06, 0.04, 0.02),   # near-black background (tenebrism)
            (0.72, 0.22, 0.10),   # blood / deep red
            (0.30, 0.35, 0.15),   # deep olive shadow flesh
        ],
        ground_color=(0.06, 0.04, 0.02),    # black ground — extreme tenebrism
        stroke_size=9,
        wet_blend=0.25,
        edge_softness=0.35,
        jitter=0.05,
        glazing=None,
        crackle=True,
        chromatic_split=False,
        technique=(
            "Tenebrism — extreme light/dark contrast with figures emerging "
            "from near-black shadow. A single harsh directional light source. "
            "Almost no mid-tones; the transition from light to dark is abrupt."
        ),
        famous_works=[
            ("Judith Beheading Holofernes", "1598–1599"),
            ("The Calling of Saint Matthew", "1600"),
            ("Supper at Emmaus", "1601"),
        ],
        inspiration=(
            "Ultra-dark ground; skip underpainting blending; crank contrast in "
            "focused_pass. block_in should be very dark."
        ),
    ),

    # ── Claude Monet ──────────────────────────────────────────────────────────
    "monet": ArtStyle(
        artist="Claude Monet",
        movement="Impressionism",
        nationality="French",
        period="1865–1926",
        palette=[
            (0.88, 0.82, 0.55),   # straw/gold light
            (0.55, 0.72, 0.85),   # cerulean sky
            (0.50, 0.68, 0.45),   # spring green
            (0.82, 0.65, 0.70),   # lilac shadow
            (0.72, 0.58, 0.40),   # warm sienna path
            (0.90, 0.90, 0.80),   # diffuse white highlight
        ],
        ground_color=(0.72, 0.65, 0.55),    # pale warm ground
        stroke_size=12,
        wet_blend=0.20,
        edge_softness=0.25,
        jitter=0.060,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Broken-colour Impressionism. Short, visible brushstrokes of pure or "
            "near-pure pigment. Shadows tinted with complementary colours rather "
            "than mixed brown. En plein air work prioritises light effect over "
            "precise form. No black used in shadows."
        ),
        famous_works=[
            ("Impression, Sunrise", "1872"),
            ("Water Lilies series", "1896–1926"),
            ("Haystacks series", "1890–1891"),
        ],
        inspiration=(
            "Large stroke_size, high jitter. Shadow regions: inject cool "
            "lavender/blue strokes rather than darkening the local colour."
        ),
    ),

    # ── Georges Seurat ────────────────────────────────────────────────────────
    "seurat": ArtStyle(
        artist="Georges Seurat",
        movement="Post-Impressionism / Pointillism / Divisionism",
        nationality="French",
        period="1883–1891",
        palette=[
            (0.92, 0.88, 0.55),   # cadmium yellow — sunlit grass
            (0.55, 0.72, 0.88),   # cerulean blue — water / sky
            (0.90, 0.55, 0.35),   # orange — warm flesh in sun
            (0.45, 0.62, 0.45),   # chromium oxide green
            (0.80, 0.45, 0.65),   # mauve / complementary violet
            (0.95, 0.92, 0.75),   # naples yellow — hazy light
        ],
        ground_color=(0.85, 0.80, 0.65),    # pale canvas showing between dots
        stroke_size=4,
        wet_blend=0.02,                      # ZERO wet blending — each dot is independent
        edge_softness=0.10,                  # crisp dots; forms defined by dot density
        jitter=0.04,
        glazing=None,
        crackle=False,
        chromatic_split=True,                # Seurat's signature: dots + complements
        technique=(
            "Divisionism (Chromoluminarism). Pure pigment dots placed side-by-side "
            "rather than mixed on the palette. The eye fuses them optically at "
            "distance, creating a luminosity impossible with physical mixing. "
            "Warm sunlit areas: yellow-orange dots interspersed with violet-blue. "
            "Shadow areas: blue-violet with orange accents. "
            "The technique builds on Chevreul's law of simultaneous contrast: "
            "every colour intensifies when placed next to its complement."
        ),
        famous_works=[
            ("A Sunday on La Grande Jatte", "1884–1886"),
            ("Bathers at Asnières", "1884"),
            ("The Circus", "1890–1891"),
            ("Evening, Honfleur", "1886"),
        ],
        inspiration=(
            "Use pointillist_pass() instead of block_in()/build_form(). "
            "Enable chromatic_split=True: for each primary dot, add a small "
            "complementary dot offset by ~2 dot radii. Zero wet blending. "
            "dot_size=3–5px. High dot count (8000+)."
        ),
    ),

    # ── Vincent van Gogh ──────────────────────────────────────────────────────
    "van_gogh": ArtStyle(
        artist="Vincent van Gogh",
        movement="Post-Impressionism",
        nationality="Dutch",
        period="1881–1890",
        palette=[
            (0.18, 0.22, 0.65),   # Prussian blue — night sky / shadows
            (0.95, 0.90, 0.30),   # chrome yellow — wheat / stars
            (0.62, 0.48, 0.22),   # raw sienna — earth
            (0.30, 0.58, 0.35),   # viridian green — cypress / fields
            (0.85, 0.45, 0.20),   # burnt orange — flame / sunflower
            (0.48, 0.38, 0.72),   # violet — shadows
        ],
        ground_color=(0.42, 0.35, 0.22),    # medium warm ground
        stroke_size=10,
        wet_blend=0.28,
        edge_softness=0.20,
        jitter=0.075,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Thick impasto brushwork in highly expressive, swirling directions. "
            "Colours bold, emotional, non-naturalistic. Dark Prussian blue "
            "shadows against burning cadmium yellows. Strokes visible as "
            "sculptural ridges. Contour lines reinforce form outlines."
        ),
        famous_works=[
            ("The Starry Night", "1889"),
            ("Sunflowers", "1888"),
            ("Bedroom in Arles", "1888"),
            ("Wheat Field with Crows", "1890"),
        ],
        inspiration=(
            "High curvature in stroke_path; large stroke_size; high jitter. "
            "Swirling flow field derived from image gradients with amplified curvature."
        ),
    ),

    # ── Hilma af Klint ────────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    "hilma_af_klint": ArtStyle(
        artist="Hilma af Klint",
        movement="Abstract / Spiritual / Proto-Abstract Expressionism",
        nationality="Swedish",
        period="1906–1944",
        palette=[
            (0.90, 0.65, 0.15),   # golden amber — warm spiritual light
            (0.25, 0.45, 0.78),   # cerulean blue — cosmic depth
            (0.92, 0.35, 0.28),   # vermillion red — life force
            (0.55, 0.82, 0.45),   # spring green — growth/nature
            (0.78, 0.72, 0.88),   # lavender — spiritual plane
            (0.15, 0.15, 0.20),   # near-black — void / ground
        ],
        ground_color=(0.95, 0.93, 0.88),    # pale canvas — her work is often light-grounded
        stroke_size=8,
        wet_blend=0.35,
        edge_softness=0.55,
        jitter=0.030,
        glazing=(0.90, 0.85, 0.70),          # warm translucent glaze
        crackle=False,
        chromatic_split=False,
        technique=(
            "Biomorphic abstraction with sweeping organic curves and bold colour fields. "
            "Warm amber and orange zones opposed by cool blue-violet. "
            "Spiral and circular forms suggesting cosmic cycles and invisible forces. "
            "Works often large-scale (The Paintings for the Temple, 1906–1915). "
            "Colour used symbolically — orange=masculine/earth, blue=feminine/cosmos. "
            "af Klint preceded Kandinsky's abstract work by several years though "
            "she kept it private, only for posthumous exhibition."
        ),
        famous_works=[
            ("The Paintings for the Temple (Series I–III)", "1906–1915"),
            ("The Swan, No. 17", "1915"),
            ("Altarpiece, No. 1", "1915"),
            ("Tree of Knowledge, No. 5", "1913"),
        ],
        inspiration=(
            "Contrast large warm (amber/orange) zones against cool blue/violet zones. "
            "Use flowing spherical_flow() field for organic curved strokes. "
            "Jewel palette hint. Light pale ground visible in low-density areas."
        ),
    ),

    # ── J.M.W. Turner ────────────────────────────────────────────────────────
    # Randomly selected artist for this session's atmospheric-light inspiration.
    "turner": ArtStyle(
        artist="Joseph Mallord William Turner",
        movement="Romanticism / Proto-Impressionism",
        nationality="British",
        period="1796–1851",
        palette=[
            (0.98, 0.92, 0.60),   # incandescent white-yellow — sun core
            (0.95, 0.72, 0.28),   # golden amber — atmospheric light aureole
            (0.80, 0.58, 0.35),   # warm ochre — haze mid-tone
            (0.48, 0.62, 0.78),   # cool cerulean — atmospheric recession
            (0.32, 0.28, 0.48),   # blue-violet — deep shadow / storm
            (0.88, 0.82, 0.70),   # luminous cream — diffused sky
        ],
        ground_color=(0.80, 0.75, 0.60),    # warm pale ground — light source centre
        stroke_size=18,
        wet_blend=0.75,                      # very high blending — colours bleed into each other
        edge_softness=0.90,                  # near-total dissolution of form edges
        jitter=0.045,
        glazing=(0.95, 0.85, 0.55),          # brilliant warm glaze — sunlight flooding the surface
        crackle=True,
        chromatic_split=False,
        technique=(
            "Vortex composition: radiant light at centre dissolves all edges "
            "outward into atmospheric haze. Extremely wet blending with swirling "
            "concentric strokes sweeping away from the light source. Forms "
            "dematerialise into colour and light — 'the sun is God' (his dying words). "
            "Late works nearly abstract: water, sky, and mist fuse into a single "
            "luminous field with no firm horizon. Warm yellows at the light vortex "
            "shift to cool blue-violet at the periphery."
        ),
        famous_works=[
            ("The Fighting Temeraire", "1839"),
            ("Rain, Steam, and Speed", "1844"),
            ("Snow Storm — Steam-Boat off a Harbour's Mouth", "1842"),
            ("Light and Colour (Goethe's Theory)", "1843"),
        ],
        inspiration=(
            "Use luminous_glow_pass(): place many overlapping radial soft gradients "
            "centred on the brightest point (sun/lamp). Each ring: warm core → "
            "cool haze periphery. Very high wet_blend + edge_softness so the figure "
            "dissolves into the light. Stack warm glaze last."
        ),
    ),

    # ── Gustav Klimt ─────────────────────────────────────────────────────────
    "klimt": ArtStyle(
        artist="Gustav Klimt",
        movement="Art Nouveau / Symbolism / Vienna Secession",
        nationality="Austrian",
        period="1897–1918",
        palette=[
            (0.85, 0.70, 0.15),   # gold leaf — his signature metallic richness
            (0.92, 0.82, 0.40),   # pale gold — highlights on gold areas
            (0.45, 0.20, 0.10),   # deep sienna — figure flesh in shadow
            (0.78, 0.58, 0.42),   # warm flesh — face and hands
            (0.15, 0.25, 0.48),   # midnight blue — negative space
            (0.68, 0.35, 0.55),   # mauve — floral pattern accents
        ],
        ground_color=(0.20, 0.16, 0.08),    # very dark ground — gold stands out
        stroke_size=6,
        wet_blend=0.15,
        edge_softness=0.40,
        jitter=0.025,
        glazing=(0.88, 0.75, 0.20),          # golden metallic glaze — entire surface
        crackle=False,
        chromatic_split=False,
        technique=(
            "Flat gold-leaf mosaic pattern areas surrounding naturalistically "
            "rendered flesh. The figure and robe fuse into a single gold field "
            "decorated with geometric and floral patterns (spirals, rectangles, "
            "eye motifs). Faces and hands painted with delicate, blended realism "
            "in sharp contrast to the flat decorative surroundings. "
            "Byzantine influence: gold background replaces three-dimensional space. "
            "Strong black contour defines figure against abstract ornamental field."
        ),
        famous_works=[
            ("The Kiss", "1907–1908"),
            ("Portrait of Adele Bloch-Bauer I", "1907"),
            ("Judith and the Head of Holofernes", "1901"),
            ("The Tree of Life", "1905–1909"),
        ],
        inspiration=(
            "Two-zone technique: face/hands — high wet_blend, detailed; "
            "robe/background — flat gold, geometric pattern overlay. "
            "Apply gold glaze at full canvas level. "
            "Use thin dark contour strokes around the figure boundary."
        ),
    ),

    # ── Paul Cézanne ──────────────────────────────────────────────────────────
    "cezanne": ArtStyle(
        artist="Paul Cézanne",
        movement="Post-Impressionism / Proto-Cubism",
        nationality="French",
        period="1861–1906",
        palette=[
            (0.70, 0.58, 0.40),   # warm ochre — Mont Sainte-Victoire rock
            (0.42, 0.55, 0.38),   # cool green — foliage planes
            (0.68, 0.48, 0.32),   # sienna — earth and terracotta
            (0.52, 0.60, 0.72),   # blue-grey — atmospheric distance
            (0.80, 0.72, 0.55),   # cream highlight — still life
            (0.30, 0.25, 0.18),   # dark umber — deep shadow planes
        ],
        ground_color=(0.60, 0.52, 0.38),    # warm mid-ground
        stroke_size=10,
        wet_blend=0.18,
        edge_softness=0.35,
        jitter=0.040,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Constructive, parallel 'passage' brushwork: small rectangular strokes "
            "laid in systematic diagonal bands that build volume through colour "
            "modulation rather than tonal blending. Forms reduced to geometric "
            "essentials — cylinders, spheres, cones. Warm/cool colour modulation "
            "replaces chiaroscuro: warm = convex / lit; cool = recessive / shadow. "
            "Contours deliberately left unresolved ('passage') to fuse figure "
            "and background. Influenced every Cubist and Modernist that followed."
        ),
        famous_works=[
            ("Mont Sainte-Victoire series", "1882–1906"),
            ("The Card Players", "1894–1895"),
            ("The Large Bathers", "1898–1906"),
            ("Still Life with Apples", "1895–1898"),
        ],
        inspiration=(
            "Diagonal parallel stroke bands: angle ~35° or ~-35°, stroke_size medium, "
            "wet_blend low. Cool palette for receding planes; warm for advancing. "
            "Moderate curvature — strokes are nearly straight but grouped directionally."
        ),
    ),

    # ── Diego Velázquez ───────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Velázquez pioneered "painting the air" — the atmosphere between figures —
    # and applied paint with breathtaking virtuosity and apparent looseness that
    # only resolves into crisp form at the correct viewing distance.
    "velazquez": ArtStyle(
        artist="Diego Rodríguez de Silva y Velázquez",
        movement="Spanish Baroque",
        nationality="Spanish",
        period="1617–1660",
        palette=[
            (0.82, 0.62, 0.44),   # warm flesh — silvery rose highlight
            (0.55, 0.40, 0.25),   # mid-flesh — raw sienna
            (0.28, 0.20, 0.12),   # deep umber shadow
            (0.60, 0.56, 0.50),   # silvery grey — armour / neutral mid
            (0.18, 0.14, 0.08),   # near-black — deep shadow / background
            (0.80, 0.68, 0.42),   # warm ochre — lit costume / fabric
        ],
        ground_color=(0.28, 0.22, 0.14),    # warm dark ground (walnut-oil imprimatura)
        stroke_size=8,
        wet_blend=0.38,                      # alla prima: wet strokes drag into each other
        edge_softness=0.52,                  # edges present but lose resolution up close
        jitter=0.050,
        glazing=(0.65, 0.50, 0.22),          # warm amber final glaze — unifies flesh
        crackle=True,
        chromatic_split=False,
        technique=(
            "Alla prima (wet-in-wet) with virtuosic apparent looseness. "
            "Velázquez 'paints the air' — the luminous space between objects — "
            "not the objects themselves. Broad, confident strokes of pure colour "
            "that look unfinished at close range but coalesce into form at the "
            "correct viewing distance. Cool silvery neutrals oppose warm flesh. "
            "Shadows transparent, not opaque; deep darks achieved by glazing "
            "over the brown ground. Las Meninas (1656): masterwork of illusionism."
        ),
        famous_works=[
            ("Las Meninas", "1656"),
            ("Portrait of Pope Innocent X", "1650"),
            ("The Rokeby Venus", "1647–1651"),
            ("The Spinners (Las Hilanderas)", "c. 1657"),
        ],
        inspiration=(
            "Medium wet_blend + edge_softness: edges are present but soft, "
            "not razor-sharp. block_in() strokes unusually large — Velázquez "
            "worked at arm's length. High jitter in build_form(). Final "
            "focused_pass uses warm flesh against cool silvery half-tones. "
            "The ground reads through in shadow areas."
        ),
    ),

    # ── John Singer Sargent ───────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Sargent was the consummate virtuoso of both oil alla prima and transparent
    # watercolour.  His watercolours are the subject of this session's new
    # rendering pass: wet washes, hard-edge blooms, pigment granulation, and
    # the economy of saving bare paper for the brightest lights.
    "sargent": ArtStyle(
        artist="John Singer Sargent",
        movement="American Realism / Impressionism / Watercolour Virtuosity",
        nationality="American/British",
        period="1874–1925",
        palette=[
            (0.88, 0.82, 0.68),   # warm cream — sunlit stucco / flesh highlight
            (0.72, 0.62, 0.45),   # golden ochre — warm mid-tone flesh
            (0.42, 0.52, 0.65),   # cool shadow blue — the shadow side of everything
            (0.25, 0.38, 0.28),   # deep viridian — foliage, water shadow
            (0.85, 0.70, 0.50),   # warm sienna — sunlit fabric, earth
            (0.20, 0.18, 0.22),   # near-black — anchor darks, very restrained
        ],
        ground_color=(0.95, 0.93, 0.88),    # bare cream watercolour paper (or pale primed canvas)
        stroke_size=14,
        wet_blend=0.55,                      # moderate — confident but not overworked
        edge_softness=0.45,                  # crisp wet-edge blooms + soft interior washes
        jitter=0.035,
        glazing=None,                        # watercolours don't use oil glazes
        crackle=False,
        chromatic_split=False,
        technique=(
            "Virtuosic alla prima — both oil and watercolour.  Watercolour technique: "
            "wet-in-wet initial washes for soft sky/background tones; hard-edge 'blooms' "
            "where a charged wet stroke meets a drying wash.  Pigment granulates in the "
            "hollows of rough paper.  Lights are SAVED PAPER — no white paint. "
            "The 'Sargent drag': a loaded flat brush drawn rapidly across dry rough-surface "
            "paper picks up peaks, leaving channels of bare cream between the strokes — "
            "creates sparkling light on water, foliage, and sunlit walls in a single pass. "
            "Oil work: broad confident strokes; no reworking.  A face in three marks. "
            "Cool blue-grey shadows oppose warm cream-yellow lights everywhere."
        ),
        famous_works=[
            ("Carnation, Lily, Lily, Rose", "1885–1886"),
            ("Madame X (Portrait of Madame Pierre Gautreau)", "1884"),
            ("El Jaleo", "1882"),
            ("Muddy Alligators", "1917"),           # watercolour masterpiece
            ("Santa Maria della Salute", "1904"),   # watercolour — 'Sargent drag' sky
        ],
        inspiration=(
            "Use watercolor_wash_pass(): wet-into-wet washes for background, "
            "'Sargent drag' for sunlit surfaces, hard blooms at wet wash edges. "
            "Lights = bare paper (never painted white). "
            "Cool blue shadows, warm cream-yellow lights — always opposite temperature."
        ),
    ),

    # ── Francisco Goya ────────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Goya's late "Pinturas Negras" (Black Paintings, 1819–1823) are among
    # the most psychologically raw works in Western art.  Painted directly
    # onto the plaster walls of his country house (Quinta del Sordo) with
    # crude tools, they represent a complete rejection of courtly polish.
    # Saturn Devouring His Son, The Dog, Witches' Sabbath — their power
    # comes from what is NOT painted: vast void backgrounds that swallow
    # the subject.  Goya is the ancestor of Expressionism, Surrealism, and
    # every subsequent dark figurative tradition.
    "goya": ArtStyle(
        artist="Francisco José de Goya y Lucientes",
        movement="Romanticism / Proto-Expressionism / Black Paintings",
        nationality="Spanish",
        period="1786–1828",
        palette=[
            (0.04, 0.03, 0.02),   # near-black void — the dominant 'colour'
            (0.28, 0.20, 0.10),   # charred umber — mid shadow
            (0.68, 0.55, 0.35),   # ashen ochre — ravaged flesh
            (0.55, 0.28, 0.12),   # raw sienna — earthen mid-tone
            (0.72, 0.18, 0.08),   # blood red — rare hot accent
            (0.80, 0.78, 0.70),   # pale ash — spectral highlight
        ],
        ground_color=(0.04, 0.03, 0.02),    # black ground — darkness is the canvas
        stroke_size=14,
        wet_blend=0.20,                      # strokes deliberately crude, not blended
        edge_softness=0.30,
        jitter=0.070,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Pinturas Negras (Black Paintings) technique. "
            "Near-black ground with near-black background — the subject is "
            "imprisoned in void.  Crude, urgent brushwork applied with spatula "
            "and rags as well as brushes.  Flesh is ashen, spectral, barely "
            "differentiating from shadow.  A single blood-red or ochre accent "
            "carries enormous weight against the surrounding darkness.  Forms are "
            "barely resolved — they emerge from blackness and dissolve back into it. "
            "No decorative flourish; only visceral necessity.  Goya painted these "
            "works aged 73–75, deaf, embittered, living alone, for no patron."
        ),
        famous_works=[
            ("Saturn Devouring His Son", "1819–1823"),
            ("The Dog (Perro Semihundido)", "1819–1823"),
            ("Witches' Sabbath (El Aquelarre)", "1821–1823"),
            ("Duel with Cudgels", "1820–1823"),
            ("The Third of May 1808", "1814"),  # earlier but equally raw
        ],
        inspiration=(
            "Use dark_void_pass(): near-black ground, massive void background, "
            "figures barely sketched in umber/ochre against darkness. "
            "Single blood-red or pale-ash accent stroke for maximum weight. "
            "Crude, spatula-like flat strokes; no sfumato or glaze refinement."
        ),
    ),

    # ── Édouard Manet ─────────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Manet is the fulcrum between Realism and Impressionism.  He rejected
    # academic chiaroscuro (smooth tonal gradients modeling 3D volume) in favour
    # of FLAT VALUE PLANES separated by bold dark strokes.  His contemporaries
    # were scandalized — Olympia (1863) looks like a playing card, not a nude.
    # That 'flatness' is the revolutionary act: he painted what the eye SEES
    # (flat colour patches) not what the mind KNOWS (a round, modelled body).
    # Influenced every modern painter.  Influenced photography, Japanese prints,
    # Cézanne, Monet, and ultimately all of Western modernism.
    "manet": ArtStyle(
        artist="Édouard Manet",
        movement="Realism / Pre-Impressionism / Modernism",
        nationality="French",
        period="1856–1883",
        palette=[
            (0.88, 0.78, 0.62),   # warm cream — sunlit flesh / fabric highlight
            (0.65, 0.58, 0.48),   # silvery ochre — mid-tone, very neutral
            (0.52, 0.50, 0.52),   # cool silver-grey — shadow half-tone (cool)
            (0.08, 0.06, 0.07),   # rich black — Manet used black as a pure colour
            (0.75, 0.42, 0.22),   # warm sienna — warm costume / background
            (0.82, 0.82, 0.80),   # pearl white — highest highlight
        ],
        ground_color=(0.52, 0.50, 0.48),    # cool mid-tone grey ground — not warm like old masters
        stroke_size=11,
        wet_blend=0.28,                      # alla prima but not heavily blended — flat patches
        edge_softness=0.20,                  # fairly crisp; flat planes meet at visible boundaries
        jitter=0.038,
        glazing=None,                        # no old-master glazing — direct paint only
        crackle=False,
        chromatic_split=False,
        technique=(
            "Flat value-plane technique. Forms modelled in 3–5 discrete tonal bands "
            "with minimal gradient between them — a 'playing card' flatness that "
            "scandalized the Paris Salon. Black used as a positive chromatic colour, "
            "not just shadow (unlike Impressionists who excluded black). "
            "Cool silver-grey half-tones oppose warm cream lights — never a brown "
            "transition zone. Confident, loaded-brush alla prima strokes. "
            "Edges between value planes are soft-but-present, not sfumato-dissolved. "
            "Manet built an image like a mosaic of colored shapes, each flatly painted."
        ),
        famous_works=[
            ("Olympia", "1863"),
            ("Le Déjeuner sur l'herbe", "1863"),
            ("A Bar at the Folies-Bergère", "1882"),
            ("The Balcony", "1868–1869"),
            ("Émile Zola", "1868"),
        ],
        inspiration=(
            "Use flat_plane_pass(): quantize to 4–5 value bands, apply flat "
            "loaded-brush stroke patches per band with minimal blending. "
            "Bold dark strokes (not outlines) mark transitions between planes. "
            "Black is a colour — use it in shadow areas without warming it. "
            "Cool silver half-tone; warm cream light. No sfumato, no brown mid-tones."
        ),
    ),

    # ── Egon Schiele ──────────────────────────────────────────────────────────
    "egon_schiele": ArtStyle(
        artist="Egon Schiele",
        movement="Viennese Expressionism / Vienna Secession",
        nationality="Austrian",
        period="1907–1918",
        palette=[
            (0.90, 0.80, 0.72),   # pale pinkish-white flesh — anemic, barely warm
            (0.68, 0.72, 0.52),   # sickly greenish flesh — shadowed under-planes
            (0.75, 0.58, 0.35),   # ochre mid-tone — interior body mass
            (0.55, 0.22, 0.08),   # warm dark sienna-red — his characteristic hot contour
            (0.12, 0.07, 0.04),   # near-black — primary contour line colour
            (0.72, 0.12, 0.04),   # blood red — rare accent mark, surgical restraint
            (0.38, 0.18, 0.10),   # deep burnt umber — limb shadow boundary
        ],
        ground_color=(0.94, 0.91, 0.85),    # off-white paper — Schiele worked on paper not canvas
        stroke_size=3,
        wet_blend=0.04,                      # almost no wet blending — contour drawing is dry
        edge_softness=0.04,                  # hard angular edges — no sfumato
        jitter=0.020,
        glazing=None,                        # no oil glaze — mostly gouache/watercolour on paper
        crackle=False,
        chromatic_split=False,
        technique=(
            "Angular, fractured contour lines dominate — the line itself is the primary "
            "medium. Contours re-start and overlap, pressed hard at critical joints "
            "(knuckles, elbows, collarbones) and feathering to near-nothing between. "
            "Figure interiors are flat, barely-modelled patches of pale, slightly sickly "
            "flesh tone — often greenish or yellowish rather than warm pink, giving "
            "figures a gaunt, cadaverous look. Backgrounds are minimal or absent: "
            "the figure exists in void, unanchored by landscape or interior. "
            "Poses are twisted, contorted, psychologically raw — limbs at extreme "
            "angles that no academic painter would permit. Schiele's line expresses "
            "the anguish of the body, not its ideal beauty."
        ),
        famous_works=[
            ("Self-Portrait with Physalis", "1912"),
            ("The Embrace (Lovers II)", "1917"),
            ("Death and the Maiden", "1915"),
            ("Seated Couple", "1915"),
            ("Reclining Female Nude", "1914"),
        ],
        inspiration=(
            "Use angular_contour_pass(): detect figure edges with Sobel, then lay "
            "short (10–25px) angular, fractured dark line segments along those edges. "
            "Each segment slightly deviates in direction to create the re-starting "
            "quality. Interior fill: flat, muted, slightly desaturated pale flesh "
            "(pull toward green-ochre, not warm pink). Background remains near-bare "
            "paper — just a flat warm-white void."
        ),
    ),

    # ── Mark Rothko ───────────────────────────────────────────────────────────
    "rothko": ArtStyle(
        artist="Mark Rothko",
        movement="Abstract Expressionism / Color Field",
        nationality="American (Latvian-born)",
        period="1950–1970",
        palette=[
            (0.72, 0.15, 0.08),   # deep cadmium red — his most iconic field
            (0.55, 0.08, 0.04),   # maroon — shadowed band beneath
            (0.88, 0.45, 0.12),   # warm orange — glowing upper band
            (0.18, 0.08, 0.06),   # near-black — compressed lower void
            (0.80, 0.62, 0.30),   # ochre gold — the luminous halo between bands
            (0.45, 0.18, 0.22),   # plum — cooler variant band
        ],
        ground_color=(0.14, 0.06, 0.04),   # very dark sienna — the absorbing depth
        stroke_size=40,
        wet_blend=0.72,           # very high — paint washes melt into each other
        edge_softness=0.90,       # bands have no hard edge — they breathe
        jitter=0.025,
        glazing=None,             # no final glaze — the layers ARE the surface
        crackle=False,
        chromatic_split=False,
        technique=(
            "Color Field — large horizontal bands of thinly-applied paint layered "
            "over each other in many washes. No brushwork visible; no hard edges. "
            "Bands appear to float or vibrate against each other through simultaneous "
            "contrast. Dark absorbing background makes light bands seem self-luminous. "
            "Rothko applied up to 20 thin washes per band using a wide brush and "
            "rabbit-skin glue sizing to control paint absorption into unprimed canvas."
        ),
        famous_works=[
            ("No. 61 (Rust and Blue)", "1953"),
            ("Orange, Red, Yellow", "1961"),
            ("Black on Maroon", "1958"),
            ("No. 14", "1960"),
            ("Seagram Murals (Harvard series)", "1962"),
        ],
        inspiration=(
            "color_field_pass() — analyze reference for vertical color distribution, "
            "map to 3–5 softly-edged horizontal bands, build each with many thin "
            "transparent washes to achieve luminous optical depth. The figure, if "
            "present, is not erased but subordinated — it becomes a warmth within "
            "the field rather than a defined form."
        ),
    ),

    # ── Katsushika Hokusai ────────────────────────────────────────────────────
    "hokusai": ArtStyle(
        artist="Katsushika Hokusai",
        movement="Ukiyo-e / Japanese Woodblock",
        nationality="Japanese",
        period="1779–1849",
        palette=[
            (0.15, 0.38, 0.72),   # Prussian blue (Bokashi) — his signature
            (0.85, 0.88, 0.92),   # pale winter sky
            (0.22, 0.22, 0.22),   # ink black — contour lines
            (0.88, 0.72, 0.40),   # warm ochre — earth
            (0.78, 0.32, 0.18),   # vermillion — accents
            (0.92, 0.90, 0.82),   # cream white — wave foam
        ],
        ground_color=(0.90, 0.88, 0.80),    # rice paper / cream
        stroke_size=4,
        wet_blend=0.08,
        edge_softness=0.15,
        jitter=0.020,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Flat colour areas defined by bold ink outlines. Prussian blue "
            "gradients (bokashi) to suggest sky, water, and distance. "
            "Dynamic asymmetric compositions; extreme close-up + distant view. "
            "Strong contour lines over minimal modelling. Pattern-within-pattern."
        ),
        famous_works=[
            ("The Great Wave off Kanagawa", "c. 1831"),
            ("Thirty-Six Views of Mount Fuji", "1830–1832"),
            ("Fine Wind, Clear Morning (Red Fuji)", "c. 1831"),
        ],
        inspiration=(
            "toon_paint() mode with flat colour; thin contour ink strokes. "
            "Prussian blue dominant in atmospheric distance zones."
        ),
    ),

    # ── El Greco ──────────────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # El Greco (Domenikos Theotokopoulos, 1541–1614) was a Greek painter who
    # settled in Toledo, Spain and never assimilated into the Renaissance
    # mainstream.  His work is immediately recognisable by a handful of
    # obsessive formal choices that no contemporary would have endorsed:
    #   - Extreme vertical elongation of figures (especially in late works)
    #   - Jewel-tone palette: vermilion, cerulean, lemon yellow, viridian —
    #     colours that vibrate against each other rather than harmonise
    #   - Supernatural, inner-lit passages of pale silver-grey flesh that
    #     glow from within the surrounding darkness
    #   - Stormy, turbulent backgrounds (View of Toledo) or near-void darks
    #   - Expressive, almost sculptural drapery in violent folds
    #
    # El Greco's style is now classified as Mannerist — a late phase of the
    # Renaissance characterised by exaggeration for expressive effect rather
    # than idealized naturalism.  But he went further than any Mannerist:
    # his elongation reaches towards the spiritually dematerialised, as if
    # the spirit was stretching the body upward toward heaven.
    #
    # Pipeline key: elongation_distortion_pass() — vertically distorts the
    # figure region and applies jewel-tone saturation boost to the whole
    # canvas, then adds inner-glow to pale flesh highlights.
    "el_greco": ArtStyle(
        artist="Domenikos Theotokopoulos (El Greco)",
        movement="Mannerism / Spanish Renaissance",
        nationality="Greek-Spanish",
        period="1577–1614",
        palette=[
            (0.78, 0.20, 0.14),   # vermilion red — his most saturated warm
            (0.20, 0.35, 0.72),   # deep cerulean blue — cold spirit zone
            (0.88, 0.82, 0.22),   # lemon yellow — supernatural light source
            (0.22, 0.52, 0.38),   # viridian green — costume / foliage accents
            (0.82, 0.80, 0.78),   # silver-grey flesh — inner spiritual glow
            (0.10, 0.08, 0.18),   # deep purple-black void — near-black bg
        ],
        ground_color=(0.12, 0.10, 0.20),    # deep violet-black ground — dark spiritual void
        stroke_size=7,
        wet_blend=0.22,                      # moderate blending — drapery is decisive, not blurred
        edge_softness=0.35,                  # edges present but softened by inner glow
        jitter=0.040,
        glazing=(0.28, 0.20, 0.48),          # cool violet glaze — the uncanny pallor of his flesh
        crackle=True,
        chromatic_split=False,
        technique=(
            "Extreme figure elongation: limbs, fingers, and faces stretched upward "
            "beyond anatomical possibility — the spirit pulling matter toward heaven. "
            "Jewel-tone palette (vermilion, cerulean, lemon, viridian) in violent "
            "contrast, divorced from natural local colour. Silver-grey inner-lit flesh "
            "glows as if figures are self-luminous rather than lit from outside. "
            "Turbulent, sculptural drapery in angular, impossible folds. "
            "Dark void or storm-cloud backgrounds concentrate attention on the figure. "
            "Influence: El Manierismo + Byzantine icon tradition + Titian's Venetian colour. "
            "Cézanne and Picasso (Proto-Cubism) both cited El Greco as forefather."
        ),
        famous_works=[
            ("The Burial of the Count of Orgaz", "1586–1588"),
            ("View of Toledo", "c. 1596–1600"),
            ("The Disrobing of Christ (El Espolio)", "1577–1579"),
            ("Portrait of a Cardinal (probably Cardinal Niño de Guevara)", "c. 1600"),
            ("The Opening of the Fifth Seal", "1608–1614"),
        ],
        inspiration=(
            "Use elongation_distortion_pass(): stretch the figure region vertically "
            "by 12–18% to simulate El Greco's characteristic elongation. "
            "Apply jewel-tone saturation boost (HSV: s *= 1.3) to the whole canvas. "
            "Pale silver flesh areas get an inner-glow compositing pass: "
            "a soft bright warm halo radiating outward from the lightest flesh pixels. "
            "Dark violet-black void ground with the cool glazing glaze at finish."
        ),
    ),

    # ── Paul Gauguin ──────────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Gauguin abandoned his Paris stockbroker career, his family, and European
    # civilisation itself to paint in Martinique, Brittany (Vision After the
    # Sermon, 1888), and ultimately Tahiti and the Marquesas Islands (1891–1903).
    #
    # His defining technique is Cloisonnism / Synthetism — named after cloisonné
    # enamel jewellery where metallic lead lines ('cloisons') separate flat zones
    # of vivid coloured glass.  Bernard and Anquetin coined the term; Gauguin
    # pushed it furthest.  Forms are reduced to their essential silhouette and
    # filled with bold, anti-naturalistic, emotion-driven colour — teal where a
    # European painter would use grey, hot magenta where pink, golden ochre
    # everywhere the eye expects brown or green.
    #
    # His Tahitian palette is among the most exotic in Western art: luminous
    # cadmium orange, deep cerulean, hot rose-magenta, viridian green, warm gold,
    # and near-black Prussian outlines.  Colour is divorced from description and
    # becomes pure expressive force.  'Where Do We Come From? What Are We? Where
    # Are We Going?' (1897–98) is the summation — a 12-foot mural painted in a
    # fever, Gauguin planning suicide immediately after.
    "gauguin": ArtStyle(
        artist="Paul Gauguin",
        movement="Post-Impressionism / Synthetism / Cloisonnism",
        nationality="French",
        period="1880–1903",
        palette=[
            (0.10, 0.42, 0.60),   # deep cerulean — Tahitian sea
            (0.85, 0.38, 0.18),   # cadmium orange-red — tropical warmth
            (0.80, 0.62, 0.08),   # golden ochre — sand, skin highlight
            (0.72, 0.18, 0.45),   # hot rose-magenta — flower, garment
            (0.18, 0.52, 0.35),   # viridian green — foliage, shadow
            (0.06, 0.04, 0.10),   # near-black Prussian — the cloison line
        ],
        ground_color=(0.88, 0.80, 0.60),    # warm cream-ochre — raw canvas
        stroke_size=5,
        wet_blend=0.06,                      # Synthetism is flat, not blended
        edge_softness=0.12,                  # crisp zone boundaries (the cloisonné line)
        jitter=0.025,
        glazing=None,                        # no final oil glaze — colour is raw
        crackle=False,
        chromatic_split=False,
        technique=(
            "Cloisonnism / Synthetism: forms reduced to flat zones of saturated, "
            "anti-naturalistic colour enclosed in dark, thick organic contour lines. "
            "Named after cloisonné enamel — lead 'cloisons' separate vivid glass fields. "
            "Colour chosen for emotional truth, not optical accuracy: teal shadows, "
            "magenta flesh, golden ochre where convention demands neutral brown. "
            "Gauguin's Tahitian palette (1891–1903) is among the most exotic in "
            "Western art: hot cadmium orange, deep cerulean, rose-magenta, viridian. "
            "No chiaroscuro modelling — a single flat zone may span an entire torso. "
            "The dark cloisonné outline (Prussian black-blue) reads simultaneously as "
            "drawing and as leading in a stained-glass window."
        ),
        famous_works=[
            ("Vision After the Sermon (Jacob Wrestling with the Angel)", "1888"),
            ("The Yellow Christ", "1889"),
            ("Nafea Faa Ipoipo (When Will You Marry?)", "1892"),
            ("The Spirit of the Dead Watching (Manao Tupapau)", "1892"),
            ("Where Do We Come From? What Are We? Where Are We Going?", "1897–1898"),
            ("Nevermore", "1897"),
        ],
        inspiration=(
            "Use cloisonne_pass(): quantize reference to 6–10 flat colour zones, "
            "boost saturation and drift hues toward Tahitian tropical palette, "
            "fill each zone with flat opaque strokes, then draw thick dark organic "
            "Prussian-blue contour lines along all zone boundaries — the cloisonné "
            "leading that gives the technique its stained-glass graphic power. "
            "Ground: warm cream-ochre. No wet blending; no sfumato."
        ),
    ),

    # ── Caspar David Friedrich ─────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Friedrich is the supreme master of the *Romantische Landschaft* — the
    # landscape as psychological state.  Where earlier landscapists described
    # nature, Friedrich used it to make the viewer feel the experience of
    # standing small before something incomprehensibly vast.
    #
    # His defining compositional device is the *Rückenfigur* (back-turned
    # figure): a lone traveller or monk seen from behind, gazing out at the
    # infinite sea, mountains, fog, or moonlit plain.  We cannot see the
    # figure's expression; we are invited to inhabit their stillness instead.
    #
    # His technique applies *Luftperspektive* (aerial perspective) with
    # extraordinary rigour: foreground elements are dark silhouettes with full
    # chroma; middle-distance forms are desaturated grey-green; the far horizon
    # dissolves to pale cerulean or golden-amber mist.  Each distance zone is
    # painted in a coherent atmospheric register, never mixed.
    #
    # Key works:
    #   Wanderer above the Sea of Fog (1818) — the definitive Rückenfigur
    #   Monk by the Sea (1808–1810)           — nothing but sea, sky, one figure
    #   The Sea of Ice (1823–1824)            — romantic sublime at its extreme
    #   Two Men Contemplating the Moon (1819) — intimate, nocturnal, companionate
    #   The Stages of Life (1835)             — allegorical ships + figures
    #
    # Pipeline key: atmospheric_depth_pass() — applies progressive aerial
    # perspective to background zone, making distant elements bluer, lighter,
    # and less saturated the further they recede into the sky.
    "caspar_david_friedrich": ArtStyle(
        artist="Caspar David Friedrich",
        movement="German Romanticism",
        nationality="German",
        period="1795–1840",
        palette=[
            (0.72, 0.82, 0.92),   # pale cerulean sky — the infinite vault
            (0.88, 0.84, 0.62),   # warm golden horizon — amber mist at dusk
            (0.10, 0.10, 0.08),   # near-black silhouette — foreground pine/rock
            (0.52, 0.56, 0.48),   # cool grey-green midground — desaturated hills
            (0.78, 0.74, 0.60),   # warm mist tone — atmospheric middle distance
            (0.36, 0.42, 0.52),   # blue-grey atmospheric haze — far recession
            (0.22, 0.20, 0.16),   # dark earth foreground — frozen soil/stone
        ],
        ground_color=(0.18, 0.16, 0.12),    # dark earth — dramatic foreground
        stroke_size=11,
        wet_blend=0.52,                      # moderate: sky blends; silhouettes do not
        edge_softness=0.68,                  # soft horizon; crisp near silhouettes
        jitter=0.022,
        glazing=(0.72, 0.68, 0.50),          # warm amber — late-afternoon horizon glow
        crackle=True,
        chromatic_split=False,
        technique=(
            "Aerial perspective applied with systematic rigour: foreground is dark, "
            "saturated, and sharp-edged; middle distance desaturates and softens; "
            "far horizon dissolves to luminous pale cerulean or amber mist. "
            "Rückenfigur: lone silhouette figure seen from behind, scale dwarfed by nature. "
            "Emotional through restraint — the figure's inaccessibility creates the sublime. "
            "Tonal key is cool and low: dark earth, grey-green hills, pale infinite sky. "
            "Surfaces are smoothly blended — no visible brushwork; the atmosphere IS the paint. "
            "Symmetrical compositions with a single dominant vertical axis (cliff, figure, tree). "
            "Moonlight and dusk are preferred: the transitional light of threshold states."
        ),
        famous_works=[
            ("Wanderer above the Sea of Fog", "1818"),
            ("Monk by the Sea", "1808–1810"),
            ("The Sea of Ice", "1823–1824"),
            ("Two Men Contemplating the Moon", "1819–1820"),
            ("The Stages of Life", "1835"),
        ],
        inspiration=(
            "Use atmospheric_depth_pass(): apply progressive aerial perspective to "
            "the background zone — desaturate and cool pixels progressively with "
            "their distance from the foreground (y-depth in the frame). "
            "Foreground silhouettes remain dark and saturated; sky dissolves to "
            "pale blue-grey. Warm amber glaze on the horizon band; cool blue "
            "glaze on the zenith."
        ),
    ),
    # ── Frida Kahlo ───────────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Frida Kahlo (1907–1954) was a Mexican painter whose work defies easy
    # categorisation — she rejected the Surrealist label André Breton applied to
    # her ("I never painted dreams. I painted my own reality"), but her imagery
    # draws from folk medicine, Aztec mythology, Catholic iconography, and psychic
    # autobiography with an intensity that has no Western parallel.
    #
    # Her technique is rooted in the retablo/ex-voto tradition — small devotional
    # paintings on metal sheet or masonite commissioned by common people to thank
    # a saint for miraculous intervention.  The retablo style is characterised by:
    #   1. Flat, simplified forms with minimal shading — no chiaroscuro modelling
    #   2. Intense, anti-naturalistic colour — volcanic earth reds, turquoise,
    #      hot magenta, deep jungle greens
    #   3. Heavy dark contour outlines that define every object as a discrete zone
    #   4. Decorative symbolic objects — Tehuana dress, hummingbirds, spider
    #      monkeys, exotic flora, Aztec artefacts — treated with equal weight to
    #      the subject's face
    #   5. Bilateral, near-symmetrical composition with the figure centered and
    #      objects arranged ceremonially
    #
    # Kahlo painted almost exclusively on a small scale (most works < 50×40 cm),
    # working in oil on Masonite board.  She used house-painting brushes for large
    # areas and fine sable for detail — the same mix a retablo craftsman would use.
    # There is no sfumato, no atmospheric depth, no conventional modelling: the
    # painting operates as pure symbolic inventory.
    #
    # Her palette is among the most distinctive in twentieth-century painting.  In
    # 'Self-Portrait with Thorn Necklace and Hummingbird' (1940) the background
    # foliage is a near-uniform deep emerald; the face is modelled in only three
    # values of warm ivory-ochre; the necklace blood spots are cadmium red against
    # deep umber skin.  Colour creates emotional temperature, not spatial recession.
    "frida_kahlo": ArtStyle(
        artist="Frida Kahlo",
        movement="Mexican Modernism / Naïve Surrealism / Retablo Folk Art",
        nationality="Mexican",
        period="1925–1954",
        palette=[
            (0.80, 0.22, 0.12),   # cadmium red — blood, passion, pain
            (0.14, 0.42, 0.25),   # deep jungle green — dense foliage
            (0.82, 0.60, 0.12),   # golden ochre — warm flesh highlight
            (0.68, 0.16, 0.42),   # hot magenta — Tehuana dress / hibiscus
            (0.12, 0.38, 0.60),   # cerulean blue — sky zones, ribbon
            (0.10, 0.07, 0.05),   # near-black umber — outline / shadow core
            (0.90, 0.82, 0.65),   # warm ivory — face highlight
        ],
        ground_color=(0.72, 0.58, 0.32),    # warm ochre-amber — masonite preparation
        stroke_size=7,
        wet_blend=0.06,                      # flat loaded zones, not blended
        edge_softness=0.10,                  # hard dark outlines; no sfumato
        jitter=0.030,
        glazing=None,                        # no unifying varnish glaze — paint is raw
        crackle=False,                       # masonite / metal panel does not crackle
        chromatic_split=False,
        technique=(
            "Retablo / ex-voto folk technique: forms reduced to flat saturated zones "
            "separated by heavy dark contour outlines.  No chiaroscuro modelling — "
            "three tonal values at most per form.  Colour is anti-naturalistic and "
            "emotionally driven: jungle greens, volcanic reds, Aztec turquoise. "
            "Composition is bilateral and iconic — the figure centered, symbolic objects "
            "arranged with ceremonial equality.  Fine sable detail strokes for hair, "
            "embroidery, and flora.  Tiny scale; paint applied thinly and precisely. "
            "Simultaneous contrast at every zone boundary — warm figure edge against "
            "cool background creates perceptual vibration."
        ),
        famous_works=[
            ("The Two Fridas", "1939"),
            ("Self-Portrait with Thorn Necklace and Hummingbird", "1940"),
            ("The Broken Column", "1944"),
            ("Without Hope", "1945"),
            ("Self-Portrait with Monkey", "1938"),
        ],
        inspiration=(
            "Use folk_retablo_pass(): posterize canvas to flat zones, boost saturation "
            "toward Kahlo's volcanic palette, apply heavy dark outline contours along all "
            "zone boundaries.  Enable boundary_vibration=True for simultaneous warm/cool "
            "contrast at every edge — this is the perceptual 'hum' of her figure-ground "
            "relationships.  No sfumato, no atmospheric depth, no wet blending."
        ),
    ),


    # ── Wassily Kandinsky ──────────────────────────────────────────────────────
    #
    # Kandinsky (1866–1944) is the artist most widely credited with painting the
    # first fully non-representational work — "Composition V" (1911) — and with
    # providing the theoretical underpinning for abstract art in his treatise
    # "Concerning the Spiritual in Art" (1911).  A synesthete, he perceived sound
    # as colour and colour as sound; each pigment carried an emotional and acoustic
    # resonance that he encoded in his composition theory:
    #
    #   • Yellow — sharp, trumpet-like, restless, advancing toward the viewer
    #   • Blue   — receding, heavenly, deep, organ / cello register
    #   • Red    — powerful, earthbound, drumbeat warmth
    #   • White  — the silence before sound; a canvas waiting to speak
    #   • Black  — the silence after sound; the extinguishing of all resonance
    #
    # His career divides into three phases:
    #   1. Lyrical (1900–1913): loose, organic, swirling forms derived from
    #      Russian folk art and Wagner — "Improvisation" and early "Composition"
    #      series.  Forms are suggestive of landscape and horsemen but dissolving.
    #   2. Bauhaus / Analytic (1922–1933): precise geometric abstraction —
    #      circles, triangles, lines on ordered grounds. Kandinsky taught the
    #      Bauhaus colour theory course; his late German work is cool, rational,
    #      mathematically arranged. "Composition VIII" (1923) is the archetype.
    #   3. Biomorphic Paris (1933–1944): organic, quasi-biological shapes floating
    #      against flat pastel grounds — "Composition X" (1939), "Sky Blue" (1940).
    #
    # Technically he worked in oil on canvas and gouache on paper.  His grounds
    # were often a neutral off-white — he wanted colour to radiate from the surface
    # unaffected by a warm or dark tone.  Paint application was controlled; no
    # impasto.  His Bauhaus works have an almost enamel surface quality.
    #
    # The defining element of the pipeline inspiration: the *geometric resonance
    # pass* — scatter floating geometric primitives (circles, triangles, radiating
    # lines) across the canvas, each coloured by Kandinsky's synesthetic theory.
    # The result gives any painting an abstract, musical, internally vibrating
    # quality, as if the formal subject is being dissolved into pure sensation.
    "kandinsky": ArtStyle(
        artist="Wassily Kandinsky",
        movement="Der Blaue Reiter / Bauhaus Abstract / Abstract Expressionism",
        nationality="Russian-German",
        period="1900–1944",
        palette=[
            (0.95, 0.84, 0.12),   # cadmium yellow — advancing, trumpet-sharp
            (0.08, 0.18, 0.68),   # ultramarine blue — receding, cello-deep
            (0.82, 0.16, 0.12),   # vermilion red — drumbeat warmth
            (0.06, 0.06, 0.06),   # near-black — extinguished resonance
            (0.94, 0.94, 0.90),   # ivory white — silence before sound
            (0.10, 0.52, 0.28),   # emerald green — neutral, static rest
            (0.55, 0.22, 0.70),   # violet — quiet, wavering, uncertain
        ],
        ground_color=(0.92, 0.91, 0.87),    # off-white — colour radiates cleanly
        stroke_size=8,
        wet_blend=0.10,                      # geometric forms have crisp edges
        edge_softness=0.15,                  # hard geometry; circles have clean arcs
        jitter=0.018,                        # pure pigment; minimal variation
        glazing=None,                        # colour is direct; no unifying glaze
        crackle=False,                       # modern canvas; no aged crackle
        chromatic_split=False,
        technique=(
            "Synesthetic geometric abstraction.  Each colour carries an emotional "
            "and acoustic resonance — yellow advances like a trumpet, blue recedes "
            "like a cello, red pulses like a drum.  Bauhaus phase: precise circles, "
            "triangles, and radiating lines on ordered off-white grounds.  Lyrical "
            "phase: organic swirling forms derived from folk imagery, dissolving into "
            "pure sensation.  No representational subject — composition is built from "
            "colour weight, tension-line, and geometric counterpoint.  Flat, controlled "
            "paint application; no impasto; enamel-quality surface.  'Colour is the "
            "keyboard, the eye is the hammer, the soul is the string.'"
        ),
        famous_works=[
            ("Composition VII", "1913"),
            ("Yellow-Red-Blue", "1925"),
            ("Several Circles", "1926"),
            ("Composition VIII", "1923"),
            ("Improvisation 28 (Second Version)", "1912"),
            ("Sky Blue", "1940"),
        ],
        inspiration=(
            "Use geometric_resonance_pass(): scatter floating geometric primitives "
            "(circles, triangles, radiating tension lines) across the canvas. "
            "Colour each primitive by Kandinsky's synesthetic theory: yellow → "
            "advancing triangles; blue → receding circles; red → stable squares; "
            "black → sharp tension lines.  Apply at very low opacity so the "
            "underlying painting reads through — the result gives any composition "
            "an internally vibrating, musical quality."
        ),
    ),

    # ── Titian (Tiziano Vecellio) ─────────────────────────────────────────────
    #
    # Titian is the supreme master of Venetian colorism — the doctrine that
    # colour, not line, is the primary vehicle of pictorial truth.  Where
    # Florentine painters drew a linear cartoon and filled it with tone,
    # Titian built his paintings from colour itself: dense warm glazes laid
    # wet-into-wet, then scraped back, re-glazed, and scraped again over
    # weeks and months.  X-ray reveals radically reworked passages in nearly
    # every major work.
    #
    # Key technical facts:
    #
    #   Ground: Venetian painters primed canvas with a warm red-earth imprimatura
    #   that glows through thin colour layers in the final work.  Titian's
    #   grounds range from warm red (early work) to a cooler grey-buff in his
    #   late "unfinished" style.
    #
    #   Glazing: Thin transparent layers of lead white + Venice turpentine +
    #   pigment.  Flesh is built from transparent glazes of vermilion and
    #   red lake over a white underpaint, producing a translucent, luminous
    #   pink rather than an opaque flesh tone.  Deep shadows are glazed with
    #   raw umber + Venetian red — warm rather than cold.
    #
    #   Impasto: Highlights are loaded impasto — thick passages of lead white
    #   and pale yellow.  The contrast between translucent shadows and opaque
    #   peaks gives the surface its three-dimensional texture.
    #
    #   Late style: Titian's last works (1560s–1576) abandon precise contour
    #   entirely.  Brushwork is visible and gestural; figures dissolve into a
    #   shimmering atmosphere of broken colour.  Vasari noted he used his
    #   fingers as much as his brushes.
    #
    #   Palette: Dominated by rich scarlet (vermilion + red lake), warm gold
    #   (Naples yellow, lead white, yellow ochre), deep Venetian blue (lapis
    #   lazuli modified with lead white), and warm ivory flesh.  The overall
    #   key is warm — blues are used sparingly as spatial punctuation, not
    #   ambient tone.
    #
    # Pipeline inspiration: the venetian_glaze_pass() — build warm transparent
    # glaze layers that deepen shadows with red-amber warmth while preserving
    # translucency.  Impasto highlight strokes are applied last in opaque thick
    # passages.  subsurface_glow_pass() simulates the translucent skin quality
    # achieved by Titian's red-lake glazes over white ground.
    "titian": ArtStyle(
        artist="Titian (Tiziano Vecellio)",
        movement="Venetian Renaissance / Venetian Colorism",
        nationality="Italian (Venetian)",
        period="1490–1576",
        palette=[
            (0.84, 0.28, 0.18),   # vermilion-red — Titian's defining colour
            (0.76, 0.52, 0.18),   # Naples yellow-gold — lit passages
            (0.90, 0.80, 0.60),   # warm ivory flesh — lit skin
            (0.52, 0.32, 0.20),   # warm umber — flesh mid-tone
            (0.30, 0.20, 0.12),   # deep raw umber shadow
            (0.28, 0.38, 0.62),   # Venetian lapis blue — cool accent
            (0.60, 0.18, 0.14),   # deep red lake — transparent shadow glaze
        ],
        ground_color=(0.54, 0.34, 0.22),    # warm red-earth imprimatura
        stroke_size=14,
        wet_blend=0.82,                      # rich wet-into-wet blending
        edge_softness=0.72,                  # softer than Baroque, firmer than sfumato
        jitter=0.038,                        # Titian's surfaces have organic irregularity
        glazing=(0.72, 0.40, 0.18),          # warm Venetian red-amber glaze
        crackle=True,                        # 16th-century Venetian canvas
        chromatic_split=False,
        technique=(
            "Venetian colorism: colour replaces line as structural element. "
            "Transparent warm glazes (vermilion, red lake, yellow ochre) "
            "over white underpaint produce luminous, translucent flesh. "
            "Deep shadows glazed with warm umber rather than cool grey. "
            "Impasto highlights in thick lead white and Naples yellow. "
            "Late works: gestural broken brushwork; fingers used as much as brushes. "
            "The warm red-earth ground glows through thin colour zones."
        ),
        famous_works=[
            ("Assumption of the Virgin", "1516–1518"),
            ("Bacchus and Ariadne", "1520–1523"),
            ("Venus of Urbino", "1538"),
            ("Portrait of a Man", "c. 1512"),
            ("The Flaying of Marsyas", "c. 1570–1576"),
            ("Pieta", "c. 1576"),
        ],
        inspiration=(
            "Use venetian_glaze_pass(): build translucent warm glaze layers "
            "that deepen shadows with red-amber warmth while preserving luminosity. "
            "Follow with subsurface_glow_pass() to simulate the translucent skin "
            "quality of red-lake glazes over white ground — edges of the face and "
            "hands glow warm red as light passes through thin skin. "
            "Impasto highlight strokes are thick and directional, applied last. "
            "The ground colour (warm red-earth) should remain visible in thin zones."
        ),
    ),


    # ── Henri Matisse ─────────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Matisse was the supreme leader of Fauvism (Les Fauves — "the wild beasts"),
    # the first great revolt against naturalistic colour in European painting.
    # Where Impressionism observed light and transcribed its effects faithfully,
    # Fauvism discarded that mandate entirely: colour was pure emotional energy,
    # applied straight from the tube with maximum saturation, with no obligation
    # to represent the actual hue of the subject.  A face could be green.  A
    # shadow could be hot orange.  The sky could be flat vermilion.  Matisse
    # declared: "I cannot slavishly copy nature.  I must interpret it, and submit
    # it to the spirit of the picture."  The result was explosive, joyful, and
    # absolutely flat — no shadows, no modelling, no chiaroscuro.  Just pure colour
    # zones separated by bold outlines and placed for maximum chromatic intensity.
    # His palette evolved through Fauvism into the extraordinary cut-paper work of
    # his final decade: *Jazz* (1947), *The Snail* (1953) — colour alone, no line.
    "matisse": ArtStyle(
        artist="Henri Matisse",
        movement="Fauvism / Post-Impressionism / Decorative Modernism",
        nationality="French",
        period="1896–1954",
        palette=[
            (0.92, 0.18, 0.12),   # cadmium red — pure, hot, unmixed
            (0.96, 0.72, 0.04),   # cadmium yellow — solar, maximum saturation
            (0.08, 0.52, 0.72),   # cerulean blue — cool foil to the warm zones
            (0.12, 0.68, 0.28),   # viridian green — jungle, nature, anti-naturalistic
            (0.88, 0.45, 0.08),   # cadmium orange — sunlit planes
            (0.75, 0.10, 0.55),   # violet-rose — shadow as pure colour, not grey
            (0.96, 0.94, 0.80),   # pale cream — the ground reading through, or light
        ],
        ground_color=(0.96, 0.94, 0.80),    # pale canvas — Matisse let light show through
        stroke_size=10,
        wet_blend=0.06,                      # nearly no blending — flat, direct, decisive
        edge_softness=0.10,                  # bold outlines; no sfumato
        jitter=0.025,
        glazing=None,                        # no glazing — colour is applied direct and final
        crackle=False,
        chromatic_split=False,
        technique=(
            "Fauvist mosaic technique: colour zones laid flat and unmixed, "
            "at maximum saturation.  No shadow modelling — shadow areas receive "
            "a COMPLEMENTARY hot colour (orange shadow beside blue form, purple "
            "shadow beside yellow) rather than a darkened or desaturated version "
            "of the local colour.  Outlines (contours) are drawn in pure colour "
            "(often deep red, green, or blue) rather than neutral black. "
            "Forms are simplified to their essential silhouette — detail "
            "suppressed to allow colour to assert itself.  Backgrounds are as "
            "flat and saturated as the figure.  Matisse saw colour not as a "
            "descriptive tool but as an architectural structure: each zone "
            "must balance its neighbours across the whole canvas like a chord."
        ),
        famous_works=[
            ("Woman with a Hat", "1905"),
            ("The Joy of Life (Bonheur de Vivre)", "1905–1906"),
            ("The Dance", "1910"),
            ("Red Room (Harmony in Red)", "1908"),
            ("Blue Nude II", "1952"),   # late cut-paper period
        ],
        inspiration=(
            "Use fauvist_mosaic_pass(): quantize reference to N bold zones, "
            "replace each zone's hue with a pure Fauvist colour from the palette, "
            "suppress luminance modelling (flatten to mid-value), apply bold "
            "coloured contour outlines (not black).  Shadow zones → complementary "
            "hot colour, not grey.  Zero sfumato, zero glazing, maximum saturation."
        ),
    ),


    # ── Amedeo Modigliani ──────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Modigliani (1884–1920) was an Italian painter of the École de Paris whose
    # singular portraiture style is among the most immediately recognisable in
    # Western art.  Born in Livorno, he came to Paris in 1906, absorbed the formal
    # simplifications of Paul Cézanne and the mask aesthetics of African and
    # Cycladic sculpture, and forged a style that has no true antecedent.
    #
    # His faces are oval — elongated to an extreme that echoes medieval Sienese
    # altarpieces and African ritual masks — with swan necks, tilted heads, and
    # almond-shaped eyes rendered as solid ellipses of a single cool colour with
    # no pupils (or with tiny irises reduced to slits).  The nose is suggested by
    # a single narrow ridge-line; the mouth is small and precisely placed.  There
    # is almost no chiaroscuro: flesh is a warm, flat ochre that barely modulates
    # across the face.  A single thin shadow-blue beneath the chin separates face
    # from neck.  The background — when not a warm neutral — is a single cool
    # cobalt or viridian plane.
    #
    # This radical simplification was not poverty of means but philosophical
    # intention: Modigliani wanted to paint the soul rather than the surface.
    # His primary influences were Sienese Gothic painting (Duccio, Simone Martini),
    # African masks, Cycladic marble heads, and Cézanne's structural reduction.
    # Brancusi introduced him to the direct-cut sculpture that made him think of
    # form as the primary reality beneath appearance.
    #
    # Pipeline: warm ochre ground, oil underpainting, build_form (minimal),
    # oval_mask_pass() for the mask-like face (warm flat flesh, almond-eye ovals,
    # smooth oval contour outline), warm_cool_boundary_pass() for simultaneous
    # contrast at the face/background boundary.
    "modigliani": ArtStyle(
        artist="Amedeo Modigliani",
        movement="École de Paris / Post-Impressionism / Primitivism",
        nationality="Italian",
        period="1906–1920",
        palette=[
            (0.84, 0.62, 0.38),   # warm ochre flesh — the defining Modigliani skin tone
            (0.68, 0.44, 0.24),   # raw sienna shadow — the only face shadow allowed
            (0.22, 0.38, 0.70),   # cobalt blue — the eye fill colour (no pupils)
            (0.24, 0.60, 0.42),   # viridian cool — background plane colour
            (0.90, 0.78, 0.52),   # Naples yellow-ivory — lit passages and hands
            (0.10, 0.07, 0.06),   # near-black outline — the mask contour
            (0.62, 0.54, 0.72),   # blue-grey mauve — cool shadow / background neutral
        ],
        ground_color=(0.78, 0.62, 0.40),    # warm sand-ochre — Modigliani worked on
        # unprepared or lightly primed canvas; the ochre ground glows through thin areas
        stroke_size=9,
        wet_blend=0.12,                      # minimal blending — flat, decisive colour zones
        edge_softness=0.15,                  # outlines are present but not totally hard
        jitter=0.020,
        glazing=None,                        # no formal glazing — colour applied direct
        crackle=False,                       # his works are relatively recent (1906-1920)
        chromatic_split=False,
        technique=(
            "Primitivist mask technique: highly elongated oval faces derived from "
            "African mask forms and Cycladic marble sculpture.  Almond-shaped eyes "
            "rendered as solid ellipses of cobalt blue or grey-violet with no pupils "
            "(or tiny irises reduced to crescent slits).  Nose suggested by a single "
            "narrow ridge; lips small and precisely placed.  Neck stretched far beyond "
            "anatomical proportion — as long as the face itself.  Flesh is warm flat "
            "ochre with almost no modelling; the single shadow colour (raw sienna or "
            "blue-grey) appears only beneath the chin and in the eye sockets. "
            "Backgrounds are single flat planes of cobalt, viridian, or grey-mauve — "
            "never illusionistic space.  The contour outline (near-black) is the "
            "primary structural element — drawn as one continuous oval, unbroken."
        ),
        famous_works=[
            ("Jeanne Hébuterne with a Hat", "1918"),
            ("Nu couché (sur le côté gauche)", "1917"),
            ("Portrait of Lunia Czechowska", "1918"),
            ("Seated Nude", "1916"),
            ("Portrait of Paul Guillaume", "1916"),
            ("Reclining Nude (La Grande Nue)", "1919"),
        ],
        inspiration=(
            "Use oval_mask_pass() to impose the Modigliani mask on the figure: "
            "flatten face modelling to warm-ochre field, draw smooth oval contour, "
            "elongate neck.  Follow with warm_cool_boundary_pass() to create the "
            "simultaneous-contrast edge vibration between warm flesh and cool "
            "cobalt/viridian background — the boundary that makes his figures "
            "appear to glow against their surroundings."
        ),
    ),

    # ── Jan van Eyck ──────────────────────────────────────────────────────────
    "jan_van_eyck": ArtStyle(
        artist="Jan van Eyck",
        movement="Early Netherlandish",
        nationality="Flemish",
        period="1422–1441",
        palette=[
            (0.92, 0.88, 0.78),   # chalk-white gesso highlight
            (0.82, 0.68, 0.42),   # warm golden-amber flesh
            (0.55, 0.38, 0.22),   # warm umber shadow
            (0.18, 0.28, 0.52),   # deep lapis lazuli blue (ultramarine)
            (0.62, 0.18, 0.12),   # deep vermilion red
            (0.28, 0.42, 0.22),   # dark malachite green
            (0.38, 0.28, 0.14),   # warm dark umber outline
        ],
        ground_color=(0.95, 0.93, 0.88),    # chalk-white gesso panel (almost pure white)
        stroke_size=4,
        wet_blend=0.55,                      # moderate — glazing requires careful blending
        edge_softness=0.45,                  # moderate — Flemish edges are present but softened by glaze layers
        jitter=0.012,                        # very low — precision Flemish technique
        glazing=(0.75, 0.58, 0.28),          # warm amber final varnish glaze (linseed + walnut oil)
        crackle=True,                        # 15th-century oak panel — characteristic craquelure
        chromatic_split=False,
        technique=(
            "Flemish panel painting technique: chalk-white gesso ground applied over "
            "seasoned oak panel in multiple fine layers, sanded to glass smoothness. "
            "Underdrawing in metalpoint or ink visible under infrared.  Paint built in "
            "thin transparent oil glazes using walnut or linseed oil — each layer must "
            "dry completely before the next is applied, creating extraordinary "
            "luminosity as light passes through stacked transparent films and reflects "
            "from the white ground beneath.  Highlights are near-white with cool grey "
            "halftone; shadows accumulate warm umber and amber glazes.  "
            "Extraordinary micro-detail in all areas: individual hairs, fabric weave "
            "threads, reflections in polished metal and pearls, dewdrops on foliage. "
            "Contours are precise but slightly softened by the final glaze layer. "
            "Colours are gem-like and deeply saturated: lapis lazuli, vermilion, "
            "malachite — ground as fine pigment particles in oil, not tempera."
        ),
        famous_works=[
            ("The Arnolfini Portrait", "1434"),
            ("Ghent Altarpiece (Adoration of the Mystic Lamb)", "1432"),
            ("Portrait of a Man in a Turban", "1433"),
            ("Madonna of Chancellor Rolin", "1435"),
            ("The Virgin of the Chancellor Rolin", "1435"),
            ("Portrait of Margareta van Eyck", "1439"),
        ],
        inspiration=(
            "Use glazed_panel_pass() to replicate van Eyck's stacked transparent oil "
            "glaze technique on a white gesso ground — thin warm washes accumulate in "
            "shadow zones while highlights retain the brilliant white ground luminosity. "
            "Follow with micro_detail_pass() to enhance fine-scale edge contrast, "
            "replicating the hyper-crisp Flemish detail in hair strands, fabric texture, "
            "and gemstone highlights.  Palette: lapis blue, vermilion, malachite green "
            "over chalk-white with warm amber unifying glaze."
        ),
    ),

    # ── Eugène Delacroix ─────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Delacroix is the fulcrum between Romantic grandeur and the chromatic
    # revolution that produced Impressionism.  His pivotal discovery — recorded
    # obsessively in his journal — was that SHADOWS CONTAIN THE COMPLEMENT of
    # the dominant light colour.  Under warm yellow candlelight the shadow side
    # of a face must contain violet; in clear daylight shadows lean blue-violet,
    # not grey-brown.  This is the empirical origin of Chevreul's simultaneous-
    # contrast law and the foundation on which Monet, Renoir, and Seurat built
    # their entire enterprise.  Without Delacroix there is no Impressionism.
    "delacroix": ArtStyle(
        artist="Eugène Delacroix",
        movement="French Romanticism / Colorism",
        nationality="French",
        period="1816–1863",
        palette=[
            (0.82, 0.28, 0.12),   # vermilion red — theatrical fire, blood, urgency
            (0.22, 0.30, 0.75),   # cobalt blue — sky, armour, shadow complement
            (0.78, 0.62, 0.18),   # cadmium yellow-gold — sunlight, armour, crown
            (0.25, 0.42, 0.22),   # viridian — foliage, distant landscape
            (0.80, 0.55, 0.38),   # warm sienna — flesh, sandy earth
            (0.45, 0.28, 0.62),   # violet — shadow complement to warm light
            (0.22, 0.12, 0.08),   # dark umber — deep shadow, defining darks
        ],
        ground_color=(0.42, 0.30, 0.18),    # warm brown ground — building on Rubens' method
        stroke_size=10,
        wet_blend=0.32,                      # alla prima with vigorous wet-into-wet
        edge_softness=0.45,                  # edges present but gestural, not precise
        jitter=0.055,                        # energetic colour variation stroke to stroke
        glazing=(0.62, 0.35, 0.12),          # warm amber unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "The defining innovation: colored shadows.  Warm light → shadow is "
            "cool violet/blue; cool light → shadow is warm amber/orange.  This "
            "chromatic opposition (not tonal darkening) makes Delacroix's paintings "
            "vibrate with optical energy absent from academic predecessors.  Vigorous, "
            "gestural brushwork — strokes larger and more expressive than the Old "
            "Masters; heavy influence of Rubens in rhetorical grandeur and warm umber "
            "grounds.  Diagonal compositional thrust: figures rise from lower-left to "
            "upper-right, creating momentum and upheaval (Liberty Leading the People, "
            "Death of Sardanapalus).  Historical and literary subjects as vehicles for "
            "colour drama over historical accuracy."
        ),
        famous_works=[
            ("Liberty Leading the People", "1830"),
            ("The Death of Sardanapalus", "1827"),
            ("Women of Algiers in Their Apartment", "1834"),
            ("The Massacre at Chios", "1824"),
            ("Jacob Wrestling with the Angel", "1861"),
            ("The Tiger Hunt", "1854"),
        ],
        inspiration=(
            "Use chromatic_shadow_pass(): identify shadow zones (lum < 0.45) and "
            "add a subtle complementary colour tint — violet/blue in warm-lit shadows, "
            "amber/orange in cool-lit shadows.  Combine with vigorous wet_blend alla "
            "prima strokes.  Preserve luminance so only chrominance shifts.  "
            "The result gives shadows depth and warmth that grey shadow mixing cannot."
        ),
    ),

    # ── Artemisia Gentileschi ──────────────────────────────────────────────────
    "artemisia_gentileschi": ArtStyle(
        artist="Artemisia Gentileschi",
        movement="Italian Baroque / Caravaggesque",
        nationality="Italian",
        period="1593–1656",
        palette=[
            (0.88, 0.74, 0.55),   # warm ivory highlight flesh
            (0.72, 0.55, 0.35),   # mid-tone amber flesh
            (0.42, 0.28, 0.14),   # deep warm umber shadow
            (0.08, 0.06, 0.04),   # near-black velvety background void
            (0.62, 0.10, 0.12),   # deep crimson drapery
            (0.14, 0.20, 0.45),   # blue-black deep drapery
            (0.72, 0.58, 0.18),   # golden amber fabric highlight
            (0.52, 0.22, 0.08),   # burnt sienna transitional shadow
        ],
        ground_color=(0.20, 0.14, 0.08),    # dark warm brown ground (alla prima)
        stroke_size=7,
        wet_blend=0.18,                      # moderate — smooth flesh but decisive drapery
        edge_softness=0.55,                  # moderately soft — light melts into shadow
        jitter=0.025,
        glazing=(0.55, 0.38, 0.14),          # warm amber deepening glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Caravaggesque chiaroscuro refined into luminous, seamless flesh.  "
            "Unlike Caravaggio's rough impasto, Gentileschi's lit surfaces are "
            "smooth and seamless — built from thin, carefully blended layers of "
            "lead white and warm flesh pigment.  A single directed light source "
            "illuminates a tight pool of the composition; the rest falls into deep, "
            "velvety warm shadow.  The falloff from light to dark is smooth but "
            "decisive — a Gaussian spotlight with warm amber tones in the light "
            "and deep Vandyke brown in the shadow.  Drapery is painted in rich "
            "jewel tones: crimson lake, blue-black, gold — with bold impasto "
            "highlights on fabric ridges.  The shadow side retains just enough "
            "detail to read form without competing with the illuminated zone."
        ),
        famous_works=[
            ("Judith Slaying Holofernes", "c. 1614–1620"),
            ("Self-Portrait as the Allegory of Painting", "c. 1638–1639"),
            ("Susanna and the Elders", "1610"),
            ("Lucretia", "c. 1621"),
            ("Cleopatra", "c. 1621"),
            ("Esther Before Ahasuerus", "c. 1628–1635"),
        ],
        inspiration=(
            "Use chiaroscuro_focus_pass() to create Gentileschi's directed spotlight: "
            "a warm ivory pool of light surrounded by deep warm shadow.  "
            "tone_ground() should use a very dark warm brown (near-black umber). "
            "block_in() and build_form() with moderate wet_blend for smooth flesh. "
            "highlight_bloom_pass() adds the subtle luminous quality of her "
            "specular highlights without rough impasto texture.  "
            "Palette: ivory flesh, burnt sienna mid-tones, Vandyke brown shadows, "
            "deep crimson and blue-black drapery, gold fabric highlights."
        ),
    ),

    # ── Tamara de Lempicka ────────────────────────────────────────────────────
    "tamara_de_lempicka": ArtStyle(
        artist="Tamara de Lempicka",
        movement="Art Deco / Figurative Modernism",
        nationality="Polish-French",
        period="1920–1956",
        palette=[
            (0.92, 0.82, 0.68),   # warm ivory highlight flesh
            (0.82, 0.62, 0.44),   # mid-tone amber flesh
            (0.52, 0.36, 0.24),   # warm shadow flesh
            (0.14, 0.18, 0.38),   # deep steel-blue drapery
            (0.72, 0.18, 0.22),   # bold carmine red
            (0.88, 0.80, 0.55),   # warm gold-cream
            (0.38, 0.42, 0.48),   # cool metallic grey
            (0.08, 0.06, 0.08),   # near-black deep shadow
        ],
        ground_color=(0.55, 0.50, 0.42),    # warm neutral buff ground
        stroke_size=8,
        wet_blend=0.06,                      # low — polished surfaces, no visible brushwork
        edge_softness=0.08,                  # very crisp edges — the Art Deco hard line
        jitter=0.015,
        glazing=None,                        # no unifying glaze — colour is direct and lacquered
        crackle=False,                       # modern canvas; not aged yet
        chromatic_split=False,
        technique=(
            "Smooth cubist-influenced figurative painting with a lacquered, metallic "
            "surface quality.  De Lempicka painted in discrete, clearly bounded planes — "
            "influenced by Ingres' smoothness and Léger's Cubist geometry.  Each flesh "
            "zone is rendered as a separate smooth facet, creating the sense of a figure "
            "carved from polished metal or enamel.  Highlights are cool silver-cream; "
            "shadows are deep and warm.  Contour edges are sharp and decisive, often "
            "reinforced with a slightly darker boundary tone.  The palette is rich, "
            "saturated, and limited: bold carmine reds, deep steel-blue drapery, warm "
            "ivory flesh, and metallic cool greys.  Backgrounds are simplified, "
            "geometric architectural forms — chrome, glass, and steel.  The overall "
            "effect is simultaneously glamorous, cool, and slightly unsettling: flesh "
            "rendered with mechanical precision."
        ),
        famous_works=[
            ("Auto Portrait (Tamara in the Green Bugatti)", "1929"),
            ("Young Lady with Gloves", "1930"),
            ("The Musician", "1929"),
            ("Kizette on the Balcony", "1927"),
            ("La Belle Rafaela", "1927"),
            ("Donna Reclinata", "1946"),
        ],
        inspiration=(
            "Use art_deco_facet_pass() to create de Lempicka's signature polished "
            "geometric facets: smooth flesh planes with metallic boundary sheen, "
            "suppressed micro-texture within zones, boosted contrast at zone edges. "
            "tone_ground() with warm neutral buff.  underpainting + block_in + "
            "build_form to establish the cubist-influenced form language before the "
            "facet pass flattens and polishes each zone.  No glaze — the surface is "
            "lacquered and final.  Low crackle: these are 1920s–1940s paintings."
        ),
    ),

    # ── Édouard Vuillard ──────────────────────────────────────────────────────
    "vuillard": ArtStyle(
        artist="Édouard Vuillard",
        movement="Nabis / Post-Impressionist Intimisme",
        nationality="French",
        period="1890–1940",
        palette=[
            (0.72, 0.55, 0.46),   # dusty rose — characteristic Vuillard warm mid-tone
            (0.42, 0.45, 0.32),   # muted olive green — foliage and fabric
            (0.52, 0.30, 0.28),   # subdued burgundy / madder — textile shadows
            (0.74, 0.67, 0.48),   # warm ochre — linen and skin in even light
            (0.22, 0.22, 0.30),   # dark blue-grey — wall shadows and deep interior
            (0.62, 0.52, 0.56),   # dusty mauve — wallpaper mid-ground
            (0.36, 0.28, 0.18),   # deep warm brown — wooden furniture and outlines
            (0.84, 0.79, 0.68),   # pale cream — highlight passages and table linen
        ],
        ground_color=(0.60, 0.54, 0.44),    # warm buff — mid-toned chalky ground
        stroke_size=7,
        wet_blend=0.12,                      # low — chalky matte surface, zones stay flat
        edge_softness=0.28,                  # low-moderate — edges present but absorbed
        jitter=0.055,                        # high — surface patterning is uniform chaos
        glazing=None,                        # no unifying glaze — matte throughout
        crackle=False,
        chromatic_split=False,
        technique=(
            "Intimisme: flat chalky zones of muted colour applied in dense, uniform "
            "short marks that cover figure and background with equal intensity. "
            "Figures do not stand out from their setting but dissolve into it — "
            "a woman's dress pattern merges with the wallpaper behind her. "
            "Inspired by Japanese woodblock prints (flat colour, bold silhouette) "
            "but translated into a scumbled, chalky oil-paint surface. "
            "No strong tonal modelling — the picture plane is uniformly activated. "
            "Light is diffuse, interior, and sourceless. Palette is muted and warm: "
            "dusty roses, olive greens, subdued crimsons, warm ochres — never pure "
            "primaries. The overall key is mid-value; no extreme lights or darks."
        ),
        famous_works=[
            ("Mother and Sister of the Artist", "1893"),
            ("The Suitor", "1893"),
            ("Interior, Mother and Sister", "c. 1893"),
            ("Luncheon", "c. 1901"),
            ("The Artist's Paint Box and Moss Roses", "1898"),
        ],
        inspiration=(
            "Use flat_plane_pass() with high jitter to scatter short marks uniformly "
            "across both figure and background. background_pass() should use the same "
            "stroke_size as the figure — the intimiste effect depends on equal treatment "
            "of all surfaces. scumble_pass() (dry-brush drag) over the finished surface "
            "replicates the chalky, slightly rough matte quality of Vuillard's distemper "
            "and oil-on-cardboard technique. intimiste_pattern_pass() can further seed "
            "the background with repeating textile motifs for wallpaper depth. "
            "No final glaze — the surface must stay matte. "
            "Palette: dusty rose, olive green, subdued burgundy, warm ochre, mauve."
        ),
    ),

    # ── Joaquín Sorolla ───────────────────────────────────────────────────────
    "sorolla": ArtStyle(
        artist="Joaquín Sorolla y Bastida",
        movement="Spanish Luminismo / Impressionism",
        nationality="Spanish",
        period="1890–1923",
        palette=[
            (0.98, 0.96, 0.88),   # brilliant white sunlight (titanium white / lead white)
            (0.94, 0.82, 0.52),   # warm golden sunlit flesh
            (0.60, 0.78, 0.92),   # Mediterranean sea blue
            (0.35, 0.62, 0.78),   # deep water blue-cyan
            (0.88, 0.92, 0.72),   # sun-bleached sand / dry grass
            (0.72, 0.55, 0.35),   # warm shadow flesh — violet-tinged brown
            (0.62, 0.70, 0.52),   # dappled shade — cool olive green
            (0.92, 0.88, 0.96),   # cool violet reflected light in shadows
        ],
        ground_color=(0.70, 0.68, 0.58),    # warm buff / primed linen in direct sun
        stroke_size=10,
        wet_blend=0.38,                      # fluid but not fully blended — lively
        edge_softness=0.45,                  # soft but readable edges; no sfumato
        jitter=0.055,                        # high colour variation — vibrant optical mix
        glazing=None,                        # no unifying glaze — brilliance is the point
        crackle=False,
        chromatic_split=False,
        technique=(
            "Luminismo — the Spanish outdoor Impressionism of maximum sunlight. "
            "Sorolla built intense illumination through simultaneous contrast: "
            "warm white or golden highlights against cool violet and blue shadows. "
            "Characteristic dappled light pools scatter across figure, fabric, and "
            "water as broken, high-key strokes. Wet-into-wet for the broad passages; "
            "decisive loaded-brush impasto dabs for the brightest specular points. "
            "The shadow side of flesh is never brown — it is violet-tinted cool, "
            "in Impressionist opposition to the warm direct light."
        ),
        famous_works=[
            ("Sewing the Sail", "1896"),
            ("Sorolla's Children on the Beach", "1909"),
            ("Walk on the Beach", "1909"),
            ("The Beach at Valencia by Morning Light", "1908"),
            ("Sad Inheritance!", "1899"),
            ("Louis Comfort Tiffany", "1911"),
        ],
        inspiration=(
            "Use dappled_light_pass() to scatter the signature broken pools of "
            "Mediterranean sunlight across the canvas. Warm-cool simultaneous "
            "contrast is the core move: wherever the sunlit key hits (warm golden), "
            "the adjacent shadow answers in cool violet. High jitter and moderately "
            "low wet_blend keeps strokes lively and optically mixed rather than "
            "muddied. Final highlights are impasto-bright white with a yellow cast."
        ),
    ),

    # ── Raphael Sanzio ────────────────────────────────────────────────────────
    # Raffaello Sanzio da Urbino (1483–1520) is the exemplar of High Renaissance
    # *clarity* — the luminous, harmonious ideal that Leonardo approached through
    # sfumato smoke, but Raphael achieved through controlled warm light and
    # gentle, rounded form building.  Where Leonardo dissolved edges, Raphael
    # *rounded* them: each form receives a soft penumbra gradient that preserves
    # legibility while conveying perfect three-dimensionality.  His flesh is not
    # smoky but LUCID — warm ivory lit from a high upper-left source, with
    # luminous midtones that feel self-illuminated rather than merely reflected.
    # The shadows are transparent, never heavy.
    #
    # The defining quality that separates Raphael from every other Renaissance
    # master is the *radiance* of his lit zones: the transition from shadow to
    # light passes through a glowing, warm-amber midtone zone that appears to
    # emit light rather than receive it — as if a candle burned inside the form.
    # This quality is best approximated by a gentle Gaussian bloom centred on
    # bright midtone pixels, tinted warm amber.
    "raphael": ArtStyle(
        artist="Raphael Sanzio (Raffaello Sanzio da Urbino)",
        movement="High Renaissance / Umbrian School",
        nationality="Italian",
        period="1500–1520",
        palette=[
            (0.90, 0.80, 0.62),   # luminous warm ivory flesh highlight
            (0.72, 0.58, 0.38),   # warm golden amber midtone — the radiant zone
            (0.52, 0.38, 0.22),   # warm umber shadow — transparent, never black
            (0.38, 0.28, 0.14),   # deep warm brown — deepest shadow passage
            (0.50, 0.62, 0.80),   # Raphael sky blue — Sistine Madonna azure
            (0.32, 0.50, 0.28),   # verdaccio-tinged green — landscape distance
            (0.88, 0.84, 0.72),   # near-white ivory — highlight peak
            (0.60, 0.44, 0.24),   # warm sienna — drapery mid-value
        ],
        ground_color=(0.60, 0.50, 0.32),    # warm medium-ochre imprimatura
        stroke_size=7,
        wet_blend=0.35,                      # soft blending — forms round gently
        edge_softness=0.58,                  # clear but rounded — no hard planes
        jitter=0.022,
        glazing=(0.68, 0.55, 0.30),          # warm golden unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "High Renaissance clarity — idealized, harmonious form with luminous "
            "warm midtones that appear self-illuminated.  Raphael built form through "
            "controlled tonal gradients rather than sfumato haze: each plane receives "
            "a soft, warm penumbra that rounds forms gently without dissolving edges "
            "into ambiguity.  Shadows are transparent warm umber, never heavy or "
            "opaque.  The defining quality is the *radiant midtone zone* — a warm "
            "amber glow in the lit-to-shadow transition that gives his figures an "
            "inner luminosity unique in Western painting."
        ),
        famous_works=[
            ("Sistine Madonna", "1512"),
            ("School of Athens", "1509–1511"),
            ("The Transfiguration", "1516–1520"),
            ("La Fornarina", "c. 1518–1519"),
            ("Portrait of Baldassare Castiglione", "c. 1514–1515"),
            ("The Triumph of Galatea", "1512"),
        ],
        inspiration=(
            "Use radiance_bloom_pass() to create the glowing warm-amber midtone "
            "zone that defines Raphael's inner luminosity. Warm wet_blend rounds "
            "forms gently without sfumato haze. Transparent warm umber shadows — "
            "apply reflected_light_pass() so all shadow areas receive subtle warm "
            "bounce from the ground plane below. Final warm golden glaze unifies "
            "the luminous tonality."
        ),
    ),


    # ── Francisco de Zurbarán ─────────────────────────────────────────────────
    # ── Jean-Auguste-Dominique Ingres ─────────────────────────────────────────
    "ingres": ArtStyle(
        artist="Jean-Auguste-Dominique Ingres",
        movement="French Neoclassicism / Academic Idealism",
        nationality="French",
        period="1800–1867",
        palette=[
            (0.95, 0.92, 0.86),   # luminous ivory-pearl highlight — Ingres' porcelain light
            (0.86, 0.78, 0.64),   # warm cream flesh midtone
            (0.72, 0.60, 0.44),   # warm amber lower midtone
            (0.50, 0.38, 0.24),   # warm sienna half-shadow
            (0.25, 0.18, 0.12),   # dark warm umber deep shadow
            (0.06, 0.04, 0.10),   # blue-black drapery / background
            (0.38, 0.52, 0.72),   # cerulean-blue turban / drapery accent
            (0.92, 0.90, 0.88),   # cool silver-white satin fabric highlight
        ],
        ground_color=(0.75, 0.68, 0.52),    # warm light ochre-buff ground
        stroke_size=5,
        wet_blend=0.28,                      # deliberate but not dry — smooth transitions
        edge_softness=0.35,                  # classical clarity: edges present but not harsh
        jitter=0.022,
        glazing=(0.80, 0.72, 0.55),          # subtle warm ivory unifying tone
        crackle=True,
        chromatic_split=False,
        technique=(
            "Ingres achieved a seamlessly smooth, porcelain-like skin surface — "
            "often called 'cold' or 'ivory' by contemporaries — through obsessive "
            "wet-into-wet blending of closely-valued flesh tones, leaving no trace "
            "of brushwork.  Highlights receive a barely perceptible cool-pearl tint "
            "(approaching silver-white) while flesh midtones carry a warm rose blush.  "
            "Drapery is rendered with crisp, almost architectural precision — each fold "
            "a deliberate linear decision, not a blended accident.  Contour lines are "
            "the foundation: Ingres drew before he painted, and the drawing shows "
            "through as a precise governing armature.  Shadows are transparent warm "
            "umber, never heavy; they recede without drama, unlike Baroque chiaroscuro.  "
            "Background tones are deep blue-black, giving the pale figure maximum "
            "contrast, but the edge between figure and ground is often deliberately "
            "merged — the drapery and background nearly match in value at the far edge "
            "so the figure emerges only from its lit passages."
        ),
        famous_works=[
            ("La Grande Odalisque", "1814"),
            ("Madame Rivière", "1806"),
            ("The Turkish Bath (Le Bain turc)", "1862"),
            ("Princess de Broglie", "1853"),
            ("Madame Moitessier", "1856"),
            ("Oedipus and the Sphinx", "1808"),
        ],
        inspiration=(
            "Use porcelain_skin_pass() to achieve Ingres' seamlessly smooth flesh: "
            "bilateral smoothing in flesh zones suppresses brushstroke texture; "
            "cool-pearl tint at highlights (lum > 0.74) and rose blush in midtones "
            "(0.40 < lum < 0.68) recreate his characteristic porcelain-ivory quality.  "
            "tonal_compression_pass() lifts the deepest shadows slightly and compresses "
            "the brightest highlights — the academic value structure that gives Ingres "
            "paintings their velvety, refined tonal range."
        ),
    ),

    "zurbaran": ArtStyle(
        artist="Francisco de Zurbarán",
        movement="Spanish Golden Age / Tenebrist Baroque",
        nationality="Spanish",
        period="1598–1664",
        palette=[
            (0.95, 0.94, 0.90),   # brilliant linen-white — the defining tone
            (0.80, 0.77, 0.68),   # warm ivory shadow in white cloth
            (0.60, 0.52, 0.36),   # warm ochre at deep cloth folds
            (0.30, 0.22, 0.12),   # dark umber in the fold recesses
            (0.05, 0.04, 0.03),   # near-black void background
            (0.60, 0.10, 0.08),   # deep crimson — occasional drapery accent
            (0.82, 0.64, 0.22),   # warm amber-gold — halo or fabric trim
            (0.82, 0.68, 0.48),   # warm ivory-olive flesh
        ],
        ground_color=(0.12, 0.08, 0.05),   # very dark warm brown ground
        stroke_size=6,
        wet_blend=0.22,                     # precise, deliberate — not blended
        edge_softness=0.28,                 # crisp edges, especially fabric-to-void
        jitter=0.025,
        glazing=None,                       # monastic austerity: no warm unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Tenebrist void backgrounds with hyper-real white fabric emerging from "
            "absolute darkness.  Zurbarán achieved a sculptural, almost photographic "
            "quality in white cloth — every fold precisely modelled with warm ochre "
            "shadows and near-black recesses.  The defining characteristic is the "
            "razor-sharp edge between brilliant white cloth and the near-black void: "
            "this 'found edge' is the most precisely rendered boundary in 17th-century "
            "painting.  Flesh tones are warm but secondary to the fabric drama.  "
            "No atmospheric perspective, no landscape — pure figure against absolute void."
        ),
        famous_works=[
            ("Saint Francis in Meditation", "c. 1635–1639"),
            ("Still Life with Pottery Jars", "c. 1636"),
            ("The Immaculate Conception", "c. 1628–1630"),
            ("Agnus Dei", "c. 1635–1640"),
            ("Saint Serapion", "1628"),
            ("Still Life with Four Vessels", "c. 1650"),
        ],
        inspiration=(
            "Use luminous_fabric_pass() to isolate brilliant white/ivory cloth zones "
            "and sharpen their fold micro-contrast against deep umber recesses.  "
            "The void background must be near-black; edge_lost_and_found_pass() places "
            "razor-sharp 'found edges' at the fabric-void boundary.  Heavy vignette "
            "crushes the painting's periphery further into darkness."
        ),
    ),

    # ── Georges de La Tour ─────────────────────────────────────────────────────
    # ── Jean-Baptiste-Siméon Chardin ──────────────────────────────────────────
    "chardin": ArtStyle(
        artist="Jean-Baptiste-Siméon Chardin",
        movement="French Naturalism / Rococo",
        nationality="French",
        period="1699–1779",
        palette=[
            (0.86, 0.78, 0.62),   # warm creamy white — bread, cloth, white faience
            (0.72, 0.64, 0.50),   # warm mid-grey — pewter and linen shadow
            (0.58, 0.50, 0.36),   # deep warm taupe — ceramic shadow, earthenware
            (0.80, 0.68, 0.44),   # golden ochre — copper, brass, warm wood
            (0.45, 0.40, 0.32),   # slate grey-brown — cast shadow on table
            (0.70, 0.56, 0.40),   # warm flesh — boy's face, child subjects
            (0.35, 0.32, 0.26),   # cool mid-shadow — blue-grey penumbra
        ],
        ground_color=(0.42, 0.38, 0.28),    # mid warm grey — toile or oak panel
        stroke_size=5,
        wet_blend=0.22,                      # broken surface — marks stay distinct but soft
        edge_softness=0.65,                  # edges dissolve softly; no hard contours
        jitter=0.038,
        glazing=(0.68, 0.60, 0.42),          # warm unifying amber-grey glaze
        crackle=False,
        chromatic_split=False,
        technique=(
            "Chardin's surfaces are built through small, directional dry-brush marks "
            "of subtly varied related colours overlapping in thin layers — creating a "
            "granular, powdery optical texture Diderot called 'pastel without a stylus'. "
            "He works from dark to light: a warm toned ground, then shadow masses, then "
            "progressive lighter passages, each in varied hues (the grey is never one "
            "grey — it is ochre-grey, blue-grey, and pink-grey placed adjacently). "
            "His edges are consistently soft; forms dissolve at their boundaries into "
            "the warm air of the domestic interior. No impasto peaks, no virtuoso marks — "
            "the surface is uniformly worked, intimate, and absolutely resolved."
        ),
        famous_works=[
            ("The Ray (La Raie)", "1728"),
            ("The House of Cards", "c. 1736–1737"),
            ("Boy with a Spinning Top", "c. 1738"),
            ("The Young Schoolmistress", "c. 1736–1740"),
            ("Grace Before a Meal (Le Bénédicité)", "1740"),
            ("The Copper Drinking Fountain", "c. 1733–1734"),
        ],
        inspiration=(
            "Use dry_granulation_pass() to simulate Chardin's distinctive powdery surface: "
            "stamp tiny directional marks of varied related hues at low opacity over form-built "
            "passages.  The palette should mix warm ochre-grey, blue-grey, and pink-grey in "
            "the same shadow region — optical mixing, not physical blending.  Follow with a "
            "light warm amber glaze to unify the granular surface into Chardin's characteristic "
            "soft domestic atmosphere."
        ),
    ),

    # ── Gustave Courbet ───────────────────────────────────────────────────────
    "courbet": ArtStyle(
        artist="Gustave Courbet",
        movement="French Realism",
        nationality="French",
        period="1848–1877",
        palette=[
            (0.72, 0.60, 0.42),   # warm flesh — raw sienna mid-tone
            (0.38, 0.28, 0.16),   # deep umber shadow — dark Vandyke brown
            (0.08, 0.06, 0.04),   # near-black void — Courbet's characteristic dark ground
            (0.55, 0.48, 0.30),   # warm ochre — natural fabric, straw, earth
            (0.28, 0.32, 0.20),   # dark olive green — shadow foliage, coat cloth
            (0.82, 0.72, 0.52),   # warm ivory highlight — lit flesh, limestone
            (0.44, 0.36, 0.24),   # muted mid-brown — stone, bark, working-class fabric
        ],
        ground_color=(0.12, 0.09, 0.05),    # very dark warm brown ground — bituminous base
        stroke_size=14,
        wet_blend=0.18,                      # palette knife: flat planes, edges stay crisp
        edge_softness=0.25,                  # clean edges — knife drag leaves hard boundaries
        jitter=0.04,
        glazing=(0.55, 0.38, 0.15),          # deep amber-brown unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Palette knife realism — thick impasto applied with flexible steel knives "
            "rather than brushes. Each knife stroke deposits a flat, smooth plane of "
            "paint with a clean edge and a ridge of raised pigment along its boundary. "
            "Courbet builds form through adjacent planes of different tone rather than "
            "blended gradients. Dark earthy ground (often black-brown bituminous base) "
            "shows through gaps, creating atmospheric depth. The surface has directional "
            "texture — the drag mark of the knife — visible across the entire canvas. "
            "Unlike academic illusionism, forms are rendered with uncompromising material "
            "honesty: stone looks like stone, flesh like flesh, fabric like fabric."
        ),
        famous_works=[
            ("The Stone Breakers", "1849"),
            ("Burial at Ornans", "1849–1850"),
            ("The Artist's Studio", "1854–1855"),
            ("The Origin of the World", "1866"),
            ("Woman with a Parrot", "1866"),
            ("The Wave", "c. 1869–1870"),
        ],
        inspiration=(
            "Use palette_knife_pass() as the primary form-building pass: flat planes of "
            "muted earth colour with knife-drag texture. Dark ground visible in gaps. "
            "Low wet_blend, moderate edge_softness — the knife leaves clean boundaries "
            "between planes. Follow with a deep amber-brown glaze to unify the dark tonal range."
        ),
    ),

    "georges_de_la_tour": ArtStyle(
        artist="Georges de La Tour",
        movement="French Baroque / Nocturne",
        nationality="French",
        period="1593–1652",
        palette=[
            (0.92, 0.68, 0.22),   # warm amber candle-core — the defining light tone
            (0.82, 0.52, 0.14),   # deep amber-orange — mid-illuminated flesh
            (0.78, 0.65, 0.42),   # warm ivory — directly lit flesh
            (0.58, 0.30, 0.08),   # dark amber-rust — flesh in shadow
            (0.22, 0.12, 0.04),   # deep warm brown — receding shadow
            (0.06, 0.04, 0.02),   # near-black void — the surrounding darkness
            (0.68, 0.48, 0.22),   # warm ochre — mid-tone transitional flesh
        ],
        ground_color=(0.06, 0.04, 0.02),    # near-black warm brown ground
        stroke_size=7,
        wet_blend=0.55,                      # smooth blending — forms are simplified and rounded
        edge_softness=0.45,                  # soft penumbra around lit forms, but clear geometry
        jitter=0.018,
        glazing=(0.75, 0.45, 0.12),          # warm amber unifying glaze — the candlelight tint
        crackle=True,
        chromatic_split=False,
        technique=(
            "Nocturne candlelight — a single concealed candle as the sole light source, "
            "casting warm amber radiance onto simplified, almost geometrically pure forms. "
            "La Tour strips away all superfluous detail; drapery becomes smooth cylinders, "
            "faces are serene oval masks. The transition from warm amber light to absolute "
            "darkness is gradual and luminous — not Caravaggio's sudden chiaroscuro cut, "
            "but a long, tender gradient. The void beyond the candlelight is absolute, "
            "near-black, with no reflected light or ambient fill. Flesh tones shift from "
            "warm ivory in direct light through deep amber-rust in shadow to near-black at "
            "the extreme. The result is meditative, still, and intimate."
        ),
        famous_works=[
            ("The Penitent Magdalene", "c. 1640"),
            ("The Newborn (La Nativité)", "c. 1648"),
            ("St. Joseph the Carpenter", "c. 1640"),
            ("The Fortune Teller", "c. 1630–1640"),
            ("Job Mocked by His Wife", "c. 1625–1650"),
            ("The Dream of St. Joseph", "c. 1640"),
        ],
        inspiration=(
            "Use candlelight_pass() to simulate La Tour's defining nocturne quality: "
            "place a warm amber radial gradient from the candle position, "
            "crushing the periphery toward near-black while pushing flesh tones to warm "
            "amber-ivory in the illuminated zone.  The falloff should be gradual and "
            "luminous — not a sharp cutoff.  Follow with a heavy warm amber glaze "
            "to unify all lit surfaces into the characteristic candlelit tonality."
        ),
    ),

    # ── William-Adolphe Bouguereau ─────────────────────────────────────────────
    "bouguereau": ArtStyle(
        artist="William-Adolphe Bouguereau",
        movement="French Academic Realism",
        nationality="French",
        period="1848–1905",
        palette=[
            (0.95, 0.84, 0.70),   # warm ivory highlight — the luminous lit flesh
            (0.85, 0.68, 0.52),   # warm mid-flesh — raw sienna tinted skin
            (0.72, 0.55, 0.40),   # golden shadow flesh — ochre-brown transition
            (0.52, 0.38, 0.28),   # deep warm shadow — raw umber
            (0.82, 0.74, 0.68),   # cool reflected light — pearlescent under-chin bounce
            (0.38, 0.42, 0.52),   # cool deep shadow — blue-grey in the deepest recesses
            (0.70, 0.60, 0.44),   # mid-flesh unifier — neutral warm mid-tone
        ],
        ground_color=(0.72, 0.62, 0.48),    # warm cream ground — toned panel
        stroke_size=3,
        wet_blend=0.88,                      # near-maximum blending — seamless, no visible marks
        edge_softness=0.80,                  # very soft transitions — porcelain continuity
        jitter=0.008,                        # minimal jitter — controlled, deliberate pigment
        glazing=(0.76, 0.62, 0.42),          # warm golden glaze — Academic warmth over all flesh
        crackle=False,
        chromatic_split=False,
        technique=(
            "Academic smooth technique — flesh built through imperceptible layers of "
            "carefully graduated colour, each passage blended into its neighbour until "
            "no mark or boundary is visible. Bouguereau worked from a warm cream ground, "
            "establishing the shadow masses first in transparent warm umber, then building "
            "the lit passages in progressive lighter tones of warm ivory, blending each "
            "addition with a soft dry brush before the paint had begun to set. The cool "
            "reflected lights under the chin and in the deep recesses are added last as "
            "thin, transparent cooler passages that counterbalance the warm highlights. "
            "The result is a surface that appears almost fresco-like in its smoothness — "
            "the paint has no physical texture; the only relief is the gentle three-"
            "dimensional modelling of the form itself. Critics at the time described his "
            "flesh as looking like 'porcelain or wax' — a quality he achieved through "
            "patience, extremely fine brushes, and a willingness to work the same passage "
            "for days until every trace of the brush had been erased."
        ),
        famous_works=[
            ("The Birth of Venus", "1879"),
            ("Nymphs and Satyr", "1873"),
            ("Young Girl Defending Herself Against Eros", "1880"),
            ("La Vague (The Wave)", "1896"),
            ("The Knitting Girl", "1869"),
            ("Maternal Admiration", "1869"),
            ("Pietà", "1876"),
        ],
        inspiration=(
            "Use academic_skin_pass() as the primary figure-refining pass after build_form(): "
            "tiny strokes (2–4px) with very high wet_blend (0.85–0.92) applied in the "
            "skin zones, building up seamlessly smooth flesh through multiple thin passes. "
            "Each pass follows the surface curvature at a slightly different angle to erase "
            "any visible directionality.  Follow with glazed_panel_pass() at very low opacity "
            "(3–4 layers, glaze_opacity=0.025) to add the characteristic warm golden depth "
            "without disturbing the smooth surface.  The goal is zero visible brushwork — "
            "only the gentle tonal transitions of perfectly modelled form."
        ),
    ),

    # ── Mary Cassatt ──────────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Mary Stevenson Cassatt (1844–1926) was an American painter who spent most
    # of her career in Paris, becoming the only American — and one of only two
    # women — to join the core Impressionist circle.  Her lifelong association
    # with Degas shaped her cropped, asymmetric compositions, but her palette and
    # subject matter are distinctly her own.
    #
    # Her defining subject is the domestic interior: women reading, bathing
    # children, nursing infants, attending the theatre.  The scenes are always
    # lit by *north-window daylight* — cool, diffused, indirect — rather than
    # the outdoor sunlight that preoccupied Monet or Renoir.  This gives her
    # palette a characteristic quality: warm flesh illuminated by cool sky light,
    # with warm amber ambient bouncing back from walls and floors into shadow.
    #
    # Her sustained engagement with Japanese woodblock prints (ukiyo-e) from 1890
    # onward pushed her toward flatter zones, stronger contours, and cropped
    # viewpoints.  Her series of colour aquatints (1890–1891) — exhibited
    # alongside Hiroshige and Utamaro — are the most direct synthesis.  In her
    # paintings the influence is subtler but present: clear, unmodulated passages
    # of flat colour in garments and backgrounds contrast with the more carefully
    # modelled flesh.
    #
    # Cassatt was also a pre-eminent pastel artist.  Her pastels carry a fine
    # chalky granularity — the powdery surface of dry chalk on laid paper —
    # quite different from the oil impasto of her male colleagues.
    #
    # Pipeline key: north_light_diffusion_pass() — simulates the cool-light /
    # warm-shadow interplay of indoor north-window daylight.
    "mary_cassatt": ArtStyle(
        artist="Mary Stevenson Cassatt",
        movement="American Impressionism / Intimisme",
        nationality="American (expatriate French)",
        period="1872–1926",
        palette=[
            (0.92, 0.82, 0.68),   # warm ivory highlight — north-lit flesh
            (0.78, 0.64, 0.50),   # warm mid-flesh — ochre-cream
            (0.54, 0.62, 0.72),   # cool blue-grey — north-light shadow
            (0.68, 0.78, 0.65),   # sage green — foliage / wallpaper
            (0.82, 0.70, 0.82),   # dusty rose-mauve — fabric / bonnets
            (0.42, 0.52, 0.68),   # cool cerulean — armchair / dress
            (0.88, 0.76, 0.55),   # warm amber — bounced ground-plane light
        ],
        ground_color=(0.88, 0.84, 0.76),    # pale cream — north-lit interior ground
        stroke_size=9,
        wet_blend=0.38,                      # deliberate but not Impressionist-broken
        edge_softness=0.42,                  # soft edges from diffused north light
        jitter=0.035,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "North-window intimate Impressionism. Soft, cool, diffused daylight from one "
            "side creates gentle shadow transitions — no harsh chiaroscuro. Shadow areas "
            "receive warm amber reflected light from ground plane and walls rather than "
            "pure darkness. Figures cropped and asymmetrically placed, influenced by "
            "Japanese woodblock prints (ukiyo-e). Background objects — wallpaper patterns, "
            "striped fabrics, floral upholstery — treated as flat decorative zones that "
            "contrast with more carefully modelled flesh. Pastel work adds a chalky, "
            "granular surface quite different from oil impasto: powdery, directional, "
            "layer upon layer of fine chalk strokes. Dominant warm palette: cream, sage, "
            "dusty rose, with cool blue-grey shadow and warm amber reflected light."
        ),
        famous_works=[
            ("In the Loge", "1878"),
            ("Little Girl in a Blue Armchair", "1878"),
            ("The Child's Bath", "1893"),
            ("Mother and Child (The Oval Mirror)", "1899"),
            ("Young Woman Sewing in a Garden", "c. 1886"),
            ("The Boating Party", "1893–1894"),
        ],
        inspiration=(
            "Use north_light_diffusion_pass() as the primary atmospheric pass: "
            "cool blue-grey shift on the lit (window) side; warm amber reflected "
            "light in the shadow. Backgrounds: flat_plane_pass() for flat patterned "
            "fabric zones. Skin: academic_skin_pass() with moderate wet_blend (0.38) "
            "and cool-leaning flesh tones — north light desaturates warm highlights."
        ),
    ),

    # ── Pieter Bruegel the Elder ──────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Pieter Bruegel the Elder (c. 1525–1569) is the supreme master of the
    # Flemish panoramic landscape and the peasant genre scene.  He is remarkable
    # for inventing a new compositional format: the *high-horizon panorama* — the
    # viewer placed on an elevated vantage, looking out across a vast seasonal
    # landscape that fills three-quarters of the canvas.  His figures are small
    # relative to the land they inhabit, yet meticulously individualised: each
    # posture, each costume, each face is particularised within a densely
    # populated scene that reads as a whole before it resolves into its parts.
    #
    # Bruegel's technical innovations:
    #
    #   1. AERIAL PERSPECTIVE AS SYSTEM — he is the first Northern European
    #      painter to apply Leonardo's atmospheric recession theory rigorously
    #      and consistently.  Foreground: saturated warm earth tones.  Middle
    #      ground: cooler, less saturated, greens beginning to grey.  Far
    #      distance: desaturated cool blue-grey, edges lost in haze.  The
    #      transition is incremental and reads over the full depth range.
    #
    #   2. SEASONAL LIGHT — each of the six "Seasons" panels (*Hunters in the
    #      Snow*, *The Harvesters*, *Gloomy Day*, etc.) is lit by a precise
    #      seasonal light quality.  Winter: flat grey overcast, no shadows,
    #      palette reduced to near-monochrome black-grey-ochre.  Summer: warm
    #      golden harvest light from the upper left, long horizontal shadows.
    #      This is not generic landscape light but *meteorological* light.
    #
    #   3. HIGH-HORIZON COMPOSITION — the horizon line is typically in the upper
    #      quarter of the canvas, forcing the viewer's gaze to sweep across a
    #      vast panoramic terrain before reaching the sky.  Diagonal paths and
    #      rivers lead the eye from foreground corners into the deep distance.
    #
    #   4. EARTHY NATURALISM — the palette avoids Flemish jewel-tones (no
    #      lapis, no vermilion except sparingly).  Earth pigments dominate:
    #      raw umber, burnt sienna, yellow ochre, verdigris green, lead white,
    #      ivory black.  The effect is warm but fundamentally terrestrial —
    #      the colour of dirt, bark, snow, and stubble.
    #
    #   5. FLAT COLOUR ZONES FOR FIGURES — individual figures are rendered in
    #      relatively flat, posterised zones of colour with minimal tonal
    #      modelling.  The environment receives more tonal nuance than the
    #      figures; this reverses the Renaissance priority and is distinctly
    #      Northern.  Faces are ruddy, coarse, individualised.
    #
    # Pipeline key: bruegel_panorama_pass() — applies progressive aerial
    # perspective desaturation and blue-grey haze as a function of the
    # pixel's distance from the foreground base of the canvas, formalising
    # Bruegel's systematic atmospheric recession into a single composable pass.
    "bruegel": ArtStyle(
        artist="Pieter Bruegel the Elder",
        movement="Flemish Renaissance / Northern Panoramic Realism",
        nationality="Flemish (Netherlandish)",
        period="c. 1550–1569",
        palette=[
            (0.62, 0.48, 0.28),   # warm yellow-ochre — foreground earth, straw, skin
            (0.32, 0.38, 0.20),   # dark olive green — near-ground foliage and scrub
            (0.20, 0.16, 0.10),   # dark raw umber — tree trunks, deep shadow
            (0.48, 0.52, 0.40),   # mid-value grey-green — middle-distance field
            (0.62, 0.66, 0.72),   # cool blue-grey — far atmospheric haze
            (0.85, 0.88, 0.92),   # pale sky blue-white — zenith sky
            (0.78, 0.72, 0.55),   # warm pale buff — lit snow / harvest stubble
            (0.28, 0.22, 0.14),   # deep umber — darkest foreground shadow
        ],
        ground_color=(0.52, 0.44, 0.28),    # warm ochre-brown imprimatura
        stroke_size=6,
        wet_blend=0.28,                      # moderate — forms are clear, not blended
        edge_softness=0.50,                  # medium — figures are clear; distances dissolve
        jitter=0.03,
        glazing=(0.62, 0.55, 0.35),          # warm amber unifying glaze — binds earthy tones
        crackle=True,
        chromatic_split=False,
        technique=(
            "High-horizon panoramic composition with systematic aerial perspective. "
            "Foreground: warm saturated earth tones — ochre, burnt sienna, dark umber — "
            "with clear figure outlines and detailed individual characterisation. "
            "Middle ground: progressively cooler and less saturated; greens become grey-green; "
            "figures become silhouettes with minimal detail. "
            "Far distance: desaturated cool blue-grey; edges dissolve into atmospheric haze; "
            "only mass and horizon line remain legible. "
            "Seasonal light is precise and meteorological — not generic 'golden hour' but "
            "the specific quality of winter overcast or summer noon or autumn afternoon. "
            "Figure palette: flat earthy zones with ruddy flesh and minimal modelling — "
            "the land is more tonally nuanced than the peasants who inhabit it. "
            "Diagonal paths and rivers lead the eye from the foreground corners deep into "
            "the receding landscape, creating the sensation of vast inhabited space."
        ),
        famous_works=[
            ("Hunters in the Snow (Winter)", "1565"),
            ("The Harvesters (Summer)", "1565"),
            ("The Peasant Wedding", "c. 1567"),
            ("The Tower of Babel", "1563"),
            ("Landscape with the Fall of Icarus", "c. 1555"),
            ("The Blind Leading the Blind", "1568"),
            ("Gloomy Day (February)", "1565"),
        ],
        inspiration=(
            "Use bruegel_panorama_pass() as the primary depth-rendering pass: "
            "apply progressive desaturation and cool blue-grey haze as a function of "
            "vertical position (depth proxy) — full warm saturation at the canvas bottom "
            "fading to cool desaturated haze at the horizon line.  The foreground zone "
            "(bottom 25%) retains full palette chroma; mid-ground (25–60%) receives a "
            "cool temperature shift and -20% saturation; far-ground (60–100% up) receives "
            "full desaturation and blue-grey overlay at 40–60% opacity.  "
            "tone_ground() with warm ochre-brown.  Individual figures: flat_plane_pass() "
            "with earthy poster zones.  Winter scenes: reduce jitter to near-zero and "
            "shift palette to near-monochrome grey-white-black."
        ),
    ),


    # ── Anders Zorn ───────────────────────────────────────────────────────────
    "anders_zorn": ArtStyle(
        artist="Anders Zorn",
        movement="Nordic Impressionism",
        nationality="Swedish",
        period="1882–1920",
        palette=[
            (0.82, 0.62, 0.18),   # yellow ochre — the warm midtone anchor
            (0.10, 0.08, 0.06),   # ivory black — warm near-black, never cool grey
            (0.88, 0.24, 0.12),   # vermillion — accent warmth at lips/cheeks/ears
            (0.96, 0.92, 0.84),   # lead white — slightly warm, not brilliant blue-white
            (0.92, 0.76, 0.52),   # warm flesh light  (white + ochre + trace vermillion)
            (0.72, 0.54, 0.28),   # mid flesh (ochre dominant, no red)
            (0.38, 0.28, 0.14),   # warm shadow (ochre + ivory black)
        ],
        ground_color=(0.52, 0.46, 0.34),    # warm neutral grey-brown (toned canvas)
        stroke_size=8,
        wet_blend=0.62,                      # confident wet-into-wet; strokes stay readable
        edge_softness=0.42,                  # decisive edges softened by wet paint
        jitter=0.04,
        glazing=(0.82, 0.64, 0.36),          # warm amber unifier — ochre-tinted varnish
        crackle=True,
        chromatic_split=False,
        technique=(
            "Zorn worked with a famously restricted palette of only four pigments: "
            "yellow ochre, ivory black, vermillion, and lead white.  This 'Zorn palette' "
            "forces all flesh rendering through warm mixtures — there are no cool blues or "
            "greens in his skin, only ochres, warm greys, and accented vermillion. "
            "His mark-making is confident and calligraphic: large-format brushes loaded "
            "with paint, each stroke placed with deliberate economy.  He rarely reworked a "
            "passage — his instinct was to place a stroke correctly once and leave it alone. "
            "Water was his signature subject: wet reflections demanded he work quickly in "
            "wet-into-wet passages, pulling long ochre highlights across dark mirror surfaces. "
            "In portraiture he exploited the tonal range of ochre+black to create an "
            "extraordinary illusion of form with minimal means.  Highlights are pure white "
            "or white+ochre; midtones are ochre alone; shadows are ochre+black in varying "
            "proportions, never descending into cool grey.  The warmth of ivory black (as "
            "opposed to lamp black or blue-black) is essential: his shadows glow rather "
            "than recede."
        ),
        famous_works=[
            ("Omnibus", "1895"),
            ("Hugo Lindqvist", "1895"),
            ("Midsummer Dance", "1897"),
            ("Dagmar", "1911"),
            ("The Waltz", "1891"),
            ("My Model and My Boat", "1886"),
            ("In the Dardanelles", "1886"),
        ],
        inspiration=(
            "Use zorn_tricolor_pass() as the primary skin-rendering pass: "
            "shift all midtone flesh areas toward warm ochre (0.82, 0.62, 0.18); "
            "add a vermillion accent saturation boost to the warmest red/pink pixels "
            "(lips, cheekbones, ear helices); apply a warm brown cast to dark regions "
            "to replicate ivory black's warmth.  "
            "tone_ground() with warm neutral grey (0.52, 0.46, 0.34).  "
            "block_in() with large confident strokes (stroke_size_bg=32).  "
            "build_form() with the limited palette — sample from the ochre/black/white "
            "triplet rather than a full colour wheel.  "
            "place_lights() at high opacity — Zorn's specular highlights are decisive "
            "pure-white marks, not soft glow.  "
            "Final glaze: warm amber at opacity 0.06 to unify the warm palette."
        ),
    ),

    # ── Berthe Morisot ────────────────────────────────────────────────────────────
    # ── Edgar Degas ───────────────────────────────────────────────────────────
    # Pipeline key: degas_pastel_pass() — builds crosshatched pastel-over-monotype
    # texture; shifts dark areas toward blue-grey while warming the lights with orange-rose.
    "degas": ArtStyle(
        artist="Edgar Degas",
        movement="Post-Impressionism / Impressionism",
        nationality="French",
        period="1853–1917",
        palette=[
            (0.88, 0.72, 0.54),   # warm amber-orange — lit flesh highlight
            (0.74, 0.68, 0.78),   # cool blue-grey — shadow flesh / background tone
            (0.96, 0.88, 0.76),   # pale ivory — top highlight on skin
            (0.38, 0.62, 0.52),   # muted viridian — costume accents, background
            (0.86, 0.62, 0.66),   # warm dusty rose — fabric and soft shadows
            (0.30, 0.30, 0.42),   # deep blue-grey — deep shadow, near-black passages
            (0.72, 0.60, 0.42),   # raw sienna — monotype base warmth beneath pastels
        ],
        ground_color=(0.28, 0.26, 0.32),    # dark blue-grey toned monotype ground
        stroke_size=7,
        wet_blend=0.22,
        edge_softness=0.35,
        jitter=0.05,
        glazing=None,                        # pastel has no glazing layer
        crackle=False,
        chromatic_split=False,
        technique=(
            "Degas developed a hybrid technique combining oil-ink monotype with subsequent "
            "pastel reworking — a method that gave his surfaces an extraordinary tension "
            "between the fluid, spontaneous monotype ground and the precise, directional "
            "pastel marks layered on top.  His hatching was multidirectional: short strokes "
            "at varying angles build up colour optically rather than physically mixing.  "
            "The result is a shimmering, vibrating surface — adjacent complementary marks "
            "(warm orange against cool blue-grey) create simultaneous contrast that the eye "
            "resolves into a coherent, luminous whole only at reading distance.  "
            "His palette is cooler and more restrained than the garden Impressionists: "
            "shadow areas drift toward blue-grey and deep slate, while lights warm toward "
            "amber, dusty rose, and pale ivory.  He was deeply influenced by Japanese prints "
            "(strong diagonals, unusual cropping, flat pattern) and by classical masters "
            "including Ingres and Mantegna.  Despite founding the Impressionist exhibitions "
            "he rejected the label, insisting that spontaneity was overrated and that "
            "careful drawing lay beneath every vibrating surface he ever made."
        ),
        famous_works=[
            ("The Dance Class", "1874"),
            ("L'Absinthe", "1876"),
            ("Ballet Rehearsal", "1875"),
            ("Woman Bathing in a Shallow Tub", "1886"),
            ("At the Races", "1869"),
            ("The Millinery Shop", "1879"),
            ("Dancers in Blue", "1890"),
        ],
        inspiration=(
            "Use degas_pastel_pass() as the primary colouristic technique: "
            "build directional crosshatched strokes over a dark blue-grey ground, "
            "shift shadows toward cool blue-grey while warming lights toward amber-orange. "
            "tone_ground() with dark blue-grey (0.28, 0.26, 0.32) — a monotype-like base. "
            "block_in() and build_form() with fine marks (stroke_size_face=7). "
            "degas_pastel_pass() adds the characteristic cool-shadow / warm-light duality "
            "and simulates the optical colour-mixing of overlaid pastel hatching. "
            "No final glaze — pastels have no varnish layer.  Edge softness is moderate: "
            "structural drawing clarity must remain beneath the colouristic surface."
        ),
    ),

    # ── Piero della Francesca ─────────────────────────────────────────────────
    # Pipeline key: piero_crystalline_pass() — shifts shadows toward cool stone-grey,
    # cools highlights toward silver-white, and gently desaturates midtones to achieve
    # the mineral, fresco-like clarity of Piero's panel and fresco painting.
    "piero_della_francesca": ArtStyle(
        artist="Piero della Francesca",
        movement="Early Italian Renaissance",
        nationality="Italian",
        period="c. 1450–1492",
        palette=[
            (0.88, 0.82, 0.70),   # pale warm ivory — lit flesh in full light
            (0.56, 0.55, 0.52),   # cool stone-grey — shadow flesh and mid-ground
            (0.52, 0.66, 0.78),   # muted cerulean blue — sky, robes, distant forms
            (0.74, 0.68, 0.54),   # warm sand-buff — architectural elements, stone
            (0.50, 0.58, 0.46),   # muted green-grey — landscape foliage and hills
            (0.82, 0.80, 0.78),   # pale silver-cool — principal highlight tone
        ],
        ground_color=(0.72, 0.68, 0.58),    # warm neutral buff — lighter than Leonardo's ochre
        stroke_size=5,
        wet_blend=0.45,
        edge_softness=0.42,
        jitter=0.04,
        glazing=(0.70, 0.70, 0.66),          # pale cool-neutral glaze — not Leonardo's warm amber
        crackle=True,                         # panel paintings and frescoes age
        chromatic_split=False,
        technique=(
            "Piero della Francesca approached painting as a branch of applied geometry: "
            "every figure, drapery fold, and architectural element was governed by "
            "mathematical perspective and precise spatial logic.  His figures inhabit space "
            "with a monumental, crystalline clarity — forms are fully resolved rather than "
            "dissolved into sfumato, and the light that falls on them is diffuse, sourceless, "
            "and almost mineral in quality.  Unlike the warm amber light of Leonardo or the "
            "golden fire of Titian, Piero's illumination is cool and even — as if his subjects "
            "exist in the clear, shadowless air of an early-morning Italian hilltown.  "
            "His flesh palette is cool ivory; shadows drift toward pale stone-grey rather than "
            "warm umber; and his highlights are silver-white rather than the warm cream of the "
            "High Renaissance.  The result is a surface that reads as simultaneously luminous "
            "and austere — figures appear carved from light-transmitting stone.  "
            "Piero's technique on panel involved careful egg-tempera underpaint followed by "
            "transparent oil glazes, a hybrid method that produced the crystalline depth "
            "visible in works like the Flagellation.  His frescoes in Arezzo (Legend of the "
            "True Cross) demonstrate the same quality at monumental scale: the colours are "
            "muted, the edges resolved, and the spatial logic impeccable."
        ),
        famous_works=[
            ("The Flagellation of Christ", "c. 1455"),
            ("The Resurrection", "c. 1463"),
            ("The Baptism of Christ", "c. 1448"),
            ("Portrait of Federico da Montefeltro", "c. 1472"),
            ("Legend of the True Cross", "c. 1452–1466"),
            ("Madonna del Parto", "c. 1460"),
        ],
        inspiration=(
            "Use piero_crystalline_pass() as the defining colouristic technique: "
            "shift shadow areas toward cool stone-grey rather than warm umber, cool "
            "highlights toward silver-white rather than amber, and gently desaturate "
            "midtones to achieve the pale mineral quality of Piero's fresco and panel work.  "
            "tone_ground() with warm neutral buff (0.72, 0.68, 0.58) — lighter and cooler "
            "than Leonardo's ochre.  "
            "block_in() and build_form() with fine marks (stroke_size_face=5).  "
            "piero_crystalline_pass() after build_form() to impose the cool mineral palette.  "
            "sfumato_veil_pass() is inappropriate — Piero's edges are clear, not dissolved.  "
            "Final glaze: pale cool-neutral (0.70, 0.70, 0.66) at low opacity to unify "
            "without warming."
        ),
    ),

    # ── John William Waterhouse ───────────────────────────────────────────────
    # Pipeline key: waterhouse_jewel_pass() — lifts midtone saturation on a near-white
    # ground; cools shadows toward Pre-Raphaelite blue; reinforces jewel-tone pigments.
    "waterhouse": ArtStyle(
        artist="John William Waterhouse",
        movement="Pre-Raphaelitism / Academic Classicism",
        nationality="British",
        period="1874–1917",
        palette=[
            (0.22, 0.38, 0.68),   # deep sapphire blue — costume and water reflections
            (0.72, 0.12, 0.18),   # deep crimson — drapery and mythological garments
            (0.88, 0.78, 0.55),   # warm ivory flesh — lit skin on a white ground
            (0.18, 0.48, 0.32),   # rich viridian — foliage and landscape greens
            (0.92, 0.85, 0.72),   # pale golden cream — highlight skin and linen
            (0.58, 0.28, 0.62),   # dusty mauve-violet — shadow passages in drapery
            (0.30, 0.22, 0.14),   # warm dark umber — hair and deep shadow accents
        ],
        ground_color=(0.94, 0.93, 0.90),    # near-white — wet white ground priming (Pre-Raphaelite method)
        stroke_size=5,
        wet_blend=0.30,
        edge_softness=0.28,
        jitter=0.04,
        glazing=(0.78, 0.82, 0.90),          # cool blue-grey unifying glaze — Pre-Raphaelite atmosphere
        crackle=False,
        chromatic_split=False,
        technique=(
            "Waterhouse inherited the Pre-Raphaelite Brotherhood's wet white ground method: "
            "he applied each painting session directly onto a still-wet white lead priming, "
            "so every pigment retained maximum luminosity as it dried — there was no oil "
            "sinking into a dark absorbent ground to grey the colours.  The result is the "
            "characteristic jewel-quality of his palette: the sapphire blues, deep crimsons, "
            "and rich viridians that saturate his mythological subjects glow from within "
            "rather than sitting inertly on the surface.  His flesh tones are warm ivory on "
            "the lit side, cooling toward pale lavender in the halftone as the white ground "
            "shows through thin, wet paint — a quality only achievable on a white support.  "
            "He worked with exceptional Pre-Raphaelite precision in the rendering of textile "
            "detail, foliage, and facial features, using fine sable brushes in the focal "
            "areas and broader scumbled marks at the edges of the composition.  His "
            "backgrounds show careful atmospheric recession — the landscape behind Lady "
            "of Shalott or Hylas recedes through graduated aerial perspective rather than "
            "Impressionist dissolution — and are painted with the same high-key luminosity "
            "as the figure.  Despite the Victorian Academic setting, Waterhouse's colour is "
            "more Pre-Raphaelite than Academic in its intensity and chromatic precision."
        ),
        famous_works=[
            ("The Lady of Shalott", "1888"),
            ("Hylas and the Nymphs", "1896"),
            ("Ophelia", "1894"),
            ("Echo and Narcissus", "1903"),
            ("The Magic Circle", "1886"),
            ("Circe Invidiosa", "1892"),
            ("Miranda", "1916"),
        ],
        inspiration=(
            "Use waterhouse_jewel_pass() as the defining colouristic technique: "
            "it lifts midtone saturation (jewel zone: lum 0.20–0.62) to simulate the "
            "white-ground luminosity, cools shadows toward lavender-blue (the white ground "
            "visible through thin paint), and preserves highlight warmth. "
            "tone_ground() with near-white (0.94, 0.93, 0.90) — the defining Pre-Raphaelite choice. "
            "block_in() and build_form() with fine marks (stroke_size_face=5). "
            "waterhouse_jewel_pass() saturates the jewel zones and cools the shadows. "
            "place_lights() with warm ivory highlights (not brilliant white — the white "
            "ground is already doing the luminosity work). "
            "Cool blue-grey glazing (0.78, 0.82, 0.90) at opacity 0.05–0.07 unifies the "
            "atmospheric Pre-Raphaelite palette.  Light vignette; no crackle."
        ),
    ),

    "berthe_morisot": ArtStyle(
        artist="Berthe Morisot",
        movement="French Impressionism",
        nationality="French",
        period="1864–1895",
        palette=[
            (0.96, 0.93, 0.86),   # warm white — luminous, slightly cream highlight
            (0.78, 0.88, 0.95),   # pale sky blue — cool shadow of flesh in daylight
            (0.94, 0.82, 0.72),   # warm peach-flesh — highlighted skin
            (0.72, 0.80, 0.88),   # blue-grey — cool halftone shadow
            (0.82, 0.74, 0.88),   # lavender — colorful reflected shadow in flesh
            (0.64, 0.76, 0.62),   # muted sage — garden or outdoor backdrop element
            (0.90, 0.72, 0.54),   # warm amber flesh midtone
        ],
        ground_color=(0.88, 0.84, 0.78),    # pale luminous warm cream — much lighter than most
        stroke_size=9,
        wet_blend=0.35,
        edge_softness=0.25,
        jitter=0.06,
        glazing=None,                        # no unifying glaze — keep the surface fresh
        crackle=False,
        chromatic_split=False,
        technique=(
            "Morisot built her pictures on a pale, luminous ground with feathery, "
            "multi-directional brushstrokes applied wet-into-wet.  Her shadow passages "
            "are never dark or neutral — they are painted in blue-violet or lavender, "
            "enriched with chromatic color rather than mere value reduction.  She studied "
            "under Corot, then absorbed Manet's influence (she became his sister-in-law), "
            "but developed a distinctly intimate vocabulary: loose, gestural marks that "
            "suggest rather than define, interiors that dissolve into light, women and "
            "children captured in fleeting moments of domestic life.  Her palette is "
            "consistently high-key: highlights push toward warm cream, shadows toward "
            "cool lavender, midtones toward warm peach.  There is almost no darkness in "
            "her work — the tonal dynamic stays in the upper half of the scale, and even "
            "the most shadowed passages retain a luminous quality.  She frequently broke "
            "brushstroke direction to create a shimmering, woven surface texture — "
            "horizontal in one area, diagonal in the next — giving the painting a sense "
            "of captured movement and vibrating light."
        ),
        famous_works=[
            ("The Cradle", "1872"),
            ("Summer's Day", "1879"),
            ("Woman at Her Toilette", "1879"),
            ("The Harbor at Lorient", "1869"),
            ("Reading", "1873"),
            ("The Butterfly Hunt", "1874"),
            ("Girl Arranging Her Hair", "1893"),
        ],
        inspiration=(
            "Use morisot_plein_air_pass() as the primary atmosphere technique: "
            "convert dark/neutral shadow areas to blue-violet or lavender, boost overall "
            "luminosity so the tonal range stays high-key, and apply short multi-directional "
            "feather strokes.  "
            "tone_ground() with pale warm cream (0.88, 0.84, 0.78) — far lighter than most. "
            "block_in() and build_form() with medium marks (stroke_size_face=9). "
            "morisot_plein_air_pass() shifts shadow chroma toward cool lavender. "
            "place_lights() with warm cream highlights, not brilliant white. "
            "No final glaze — her surface should remain fresh and atmospheric."
        ),
    ),

    # ── Sandro Botticelli ─────────────────────────────────────────────────────
    # Florentine painter (1445–1510), the supreme master of sinuous linear grace
    # in the Early Italian Renaissance.  Botticelli worked almost exclusively in
    # egg tempera on gessoed poplar panels — a medium that dries in seconds,
    # permits no wet blending, and demands that form be built entirely through
    # transparent hatching layers rather than tonal fusion.  His two great
    # mythological panels — Primavera (c. 1477–82) and The Birth of Venus
    # (c. 1485) — are unmatched in Western painting for their combination of
    # breathtaking decorative beauty and profound melancholy.  Unlike his
    # contemporary Leonardo, Botticelli never pursued mass, volume, or shadow:
    # his figures are defined entirely by flowing contour lines of extraordinary
    # calligraphic sensitivity.  The sinuous S-curve of Venus's body in the
    # Primavera is drawn, not modelled; every fold of drapery, every strand of
    # golden hair, every petal in the floral carpet beneath the Graces is
    # individually rendered with the patience of a miniaturist and the nerve of
    # a master draughtsman.  His palette is clear and brilliant — no sfumato,
    # no atmospheric haze — built on the pale white gesso ground whose luminosity
    # shows through thin tempera washes and makes each colour appear lit from
    # within.  Gold is applied not as leaf but as fine chrysographic filaments
    # (parallel strokes of shell gold) in hair, drapery, and botanical detail.
    "botticelli": ArtStyle(
        artist     = "Sandro Botticelli",
        movement   = "Florentine Renaissance / Early Italian Renaissance",
        nationality= "Italian",
        period     = "1445–1510",
        palette    = [
            (0.95, 0.91, 0.83),   # pale ivory — the luminous gesso ground showing through
            (0.88, 0.72, 0.50),   # warm flesh — Botticelli's characteristic ochre midtone
            (0.30, 0.52, 0.60),   # cerulean blue — sky and ocean in Birth of Venus
            (0.72, 0.18, 0.16),   # vermilion — Mars and Venus, drapery accents
            (0.82, 0.68, 0.22),   # gold ochre — chrysographic filament highlights
            (0.22, 0.42, 0.28),   # forest green — dense botanical foliage in Primavera
            (0.88, 0.60, 0.62),   # rose-pink — drapery of the Graces
            (0.20, 0.16, 0.10),   # dark umber — deepest shadow (never truly black in tempera)
        ],
        ground_color  = (0.94, 0.91, 0.85),   # brilliant pale gesso — tempera on white panel
        stroke_size   = 4,                      # very fine — each mark a single hair of the brush
        wet_blend     = 0.06,                   # minimal — egg tempera dries in seconds
        edge_softness = 0.12,                   # very crisp — Gothic-linearity rules over mass
        jitter        = 0.05,                   # slight — hatching shows controlled colour variation
        glazing       = None,                   # no final glaze — tempera does not glaze like oil
        crackle       = True,                   # 500-year-old gessoed panels crack extensively
        chromatic_split = False,                # no optical mixing — tempera zones stay distinct
        technique=(
            "Botticelli's tempera technique is the antithesis of Leonardo's sfumato.  "
            "Every form is defined by an unbroken flowing contour line drawn with a small "
            "pointed brush loaded with slightly darker paint — the contour exists as a "
            "literal drawn line, not as the edge of a tonal gradient.  Form is then built "
            "inward from the contour using fine parallel hatching strokes (parallel to the "
            "edge and progressively lighter toward the lit centre), never blended — tempera "
            "dries before the brush can return for a second pass.  "
            "Color is applied in pure, brilliant zones: Botticelli never mixed colours on "
            "the panel — instead, he superimposed thin transparent washes of pure pigment "
            "to build the mid-tones, while the pale gesso ground provides the highlights "
            "automatically where paint is thinnest.  "
            "Gold in his work is chrysographic — applied as fine parallel filaments of "
            "shell gold (ground gold leaf) using a quill pen or very fine brush, rather "
            "than as applied gold leaf.  Hair, drapery highlights, and botanical elements "
            "all receive these fine gold filaments.  "
            "His figures have an impossible, floating weightlessness — they seem to stand "
            "on air rather than ground, their drapery blown by a wind that exists only in "
            "the painting.  This is achieved compositionally: he foreshortens feet and "
            "lowers the horizon line so figures appear to rise above the picture plane."
        ),
        famous_works=[
            ("Primavera",                          "c. 1477–82"),
            ("The Birth of Venus",                 "c. 1485"),
            ("Mars and Venus",                     "c. 1483"),
            ("Adoration of the Magi",              "c. 1476"),
            ("Portrait of a Young Man",            "c. 1480"),
            ("The Mystical Nativity",              "1500"),
            ("Pallas and the Centaur",             "c. 1482"),
            ("La Bella Simonetta (Simonetta Vespucci)", "c. 1476"),
        ],
        inspiration=(
            "Use botticelli_linear_grace_pass() as the defining surface technique: "
            "scatter fine parallel hatching marks along edge gradients (the tempera "
            "hatching that builds form in the absence of wet blending), scatter "
            "chrysographic gold filaments through upper-midtone zones (hair, fabric "
            "highlights, botanical details), and apply a mild overall luminosity lift "
            "that simulates the bright gesso ground glowing through thin tempera.  "
            "tone_ground() with pale cream (0.94, 0.91, 0.85) — not a dark imprimatura "
            "but the brilliant white gesso characteristic of tempera panel painting.  "
            "underpainting() and block_in() with very fine strokes.  "
            "build_form() with the smallest stroke_size — every mark is deliberate.  "
            "botticelli_linear_grace_pass() applies the sinuous contour enhancement and "
            "gold filament highlights.  "
            "No final glaze — tempera surfaces are matte, not varnished to a high oil sheen.  "
            "Crackle: prominent — 550-year-old gessoed panels show extensive craquelure."
        ),
    ),

    # ── Albrecht Dürer ────────────────────────────────────────────────────────
    # German painter, printmaker, and theorist (1471–1528) — the colossus of
    # the Northern Renaissance.  Dürer was the first artist north of the Alps
    # to fully absorb and systematize the Italian Renaissance discoveries of
    # perspective, proportion, and classical form, and the first Northern
    # European artist to achieve international celebrity in his own lifetime.
    # He was born in Nuremberg, the son of a goldsmith, and his earliest
    # training was in the precise, disciplined craft of metal engraving —
    # an influence that never left his oil painting.  His three self-portraits
    # (1484, 1498, 1500) are among the most technically ambitious portraits of
    # the entire Renaissance.  The Self-Portrait at 28 (1500, Alte Pinakothek)
    # is unique in the history of art: Dürer painted himself in a strict frontal
    # pose reserved exclusively for images of Christ, asserting his divinely
    # granted creative power with startling boldness.
    #
    # Dürer's oil technique is the opposite of Leonardo's sfumato and the
    # Venetian wet glaze.  He worked on a pale grey or white-silver ground
    # (often linden wood gessoed and then given a thin lead-white imprimatura),
    # built forms with the finest sable brushes, and finished individual hairs
    # and fabric fibres with a near-engraving precision that no other painter
    # of his era could match.  His shadows are cool and clearly structured —
    # thin semi-transparent grey washes that model form without the warmth of
    # Italian chiaroscuro.  Highlights are pure white or near-white, with no
    # warm amber shift.  The overall tonality is silvery, intellectual, and
    # exquisitely controlled.
    #
    # His palette is restrained but precise: warm ochre and raw sienna for
    # flesh, cool blue-grey for shadows and backgrounds, black for drawing-
    # style contour reinforcement, crimson for lips and fabric accents, and
    # a characteristic cool lead-white for the highest lights.  His fur
    # rendering (the famous fur collar in his 1500 Self-Portrait) is achieved
    # by painting every individual hair in a separate thin stroke with a
    # single-hair brush — a technique that reads as virtuosity at the edge
    # of human capability.
    #
    # Famous works: Self-Portrait at 28 (1500), Self-Portrait at 26 (1498),
    # Young Hare (1502), The Large Turf (1503), Praying Hands (1508),
    # Portrait of Hieronymus Holzschuher (1526), The Four Apostles (1526).
    "albrecht_durer": ArtStyle(
        artist     = "Albrecht Dürer",
        movement   = "Northern Renaissance",
        nationality= "German",
        period     = "1471–1528",
        palette    = [
            (0.84, 0.72, 0.56),   # warm flesh — ochre midtone, less orange than Italian
            (0.58, 0.46, 0.34),   # shadow flesh — cool umber half-tone
            (0.72, 0.70, 0.68),   # cool silver-grey — background and atmospheric shadow
            (0.92, 0.88, 0.82),   # pale lead-white — highest flesh highlight
            (0.62, 0.14, 0.10),   # crimson — lips, drapery accents, bonnet cord
            (0.22, 0.20, 0.18),   # near-black — engraving-style contour lines
            (0.36, 0.42, 0.50),   # cool blue-grey — background, shadow cool shift
            (0.52, 0.40, 0.22),   # raw sienna — hair, fur mid-tone
        ],
        ground_color  = (0.82, 0.80, 0.76),   # pale silver-white imprimatura on gessoed panel
        stroke_size   = 3,                      # extremely fine — each mark a single hair
        wet_blend     = 0.20,                   # thin transparent oil layers; some blending
        edge_softness = 0.18,                   # crisp engraving-influenced edges
        jitter        = 0.025,                  # very controlled — minimal colour variation
        glazing       = (0.70, 0.68, 0.64),    # very subtle cool silver unifier
        crackle       = True,                   # 500-year-old panel paintings crack extensively
        chromatic_split = False,                # no optical mixing — precise layered oil
        technique=(
            "Dürer's oil technique is rooted in the precision of metal engraving.  "
            "He worked on a pale lead-white or silver-grey ground applied over "
            "gessoed linden-wood or limewood panels, and built his forms with the "
            "finest available sable brushes — often single-hair strokes for fur, "
            "beard, and fabric detail.  His shadows are cool and transparent, built "
            "from thin grey or blue-grey washes layered without blending, creating "
            "a tonal structure that reads like an engraving translated into colour.  "
            "There is no sfumato, no warm atmospheric haze, no Venetian wet-into-wet "
            "colour mixing: each form is precisely drawn before it is painted, and "
            "the drawn underdrawing is often visible beneath the thin paint film.  "
            "Highlights are pure lead-white with the cool, hard quality of silverpoint "
            "rather than the warm ivory of Italian flesh lights.  "
            "His most virtuosic paintings — the 1500 Self-Portrait, the Holzschuher "
            "portrait — achieve a level of individual-hair-by-hair precision that "
            "remains astonishing five centuries later.  The fur collar in the 1500 "
            "Self-Portrait is painted hair by hair, each strand following the natural "
            "direction of the fur with a sensitivity and patience that no other "
            "Renaissance painter attempted at this scale.  "
            "His palette is deliberately restrained: warm ochre flesh, cool grey shadow, "
            "near-black contour reinforcement, and a single saturated accent (usually "
            "crimson or deep blue) for psychological emphasis.  There is no sweetness "
            "in his colour — it is intellectual, controlled, and exquisitely calibrated."
        ),
        famous_works=[
            ("Self-Portrait at 28",               "1500"),
            ("Self-Portrait at 26",               "1498"),
            ("Young Hare",                        "1502"),
            ("Praying Hands",                     "1508"),
            ("Portrait of Hieronymus Holzschuher","1526"),
            ("The Four Apostles",                 "1526"),
            ("The Large Turf",                    "1503"),
            ("Portrait of the Artist's Father",   "1490"),
        ],
        inspiration=(
            "Use durer_engraving_pass() as the defining surface technique: apply "
            "fine cross-hatching in shadow zones at ±45°, denser in deeper shadows, "
            "replicating the graphic, engraving-influenced quality of Dürer's shadow "
            "modelling in oil.  "
            "tone_ground() with pale silver-white (0.82, 0.80, 0.76) — the cool "
            "Flemish-style imprimatura that makes his flesh tones read as luminous "
            "and cool rather than warm and amber.  "
            "underpainting() and block_in() with very fine marks (stroke_size=3).  "
            "build_form() with the finest stroke_size — each mark deliberate.  "
            "durer_engraving_pass() applies the cross-hatching that defines his "
            "shadow structure.  "
            "selective_focus_pass() to keep the face razor-sharp while the "
            "background and clothing areas soften slightly.  "
            "place_lights() with cool lead-white highlights (0.92, 0.88, 0.82).  "
            "Very subtle cool silver final glaze (0.70, 0.68, 0.64).  "
            "Prominent crackle — 500-year-old gessoed panels show extensive craquelure."
        ),
    ),

    # ── Gustave Moreau ────────────────────────────────────────────────────────
    # French Symbolist painter (1826–1898).  Moreau is the founder of the
    # Symbolist movement in painting, and his mythological canvases are unlike
    # anything else in Western art: dense, jewelled surfaces that accumulate
    # layer upon layer of small, patient brushstrokes until the canvas resembles
    # a Byzantine reliquary rather than an oil painting.  His work bridges the
    # academic tradition (he was trained at the École des Beaux-Arts) with a
    # visionary personal mythology drawn from Greek legend, the Bible, and his
    # own obsessive interior world.  He was the teacher of Matisse, Rouault,
    # and Marquet, and his studio-turned-museum (the Musée Gustave Moreau in
    # Paris) preserves thousands of works in his characteristic layered style.
    #
    # Palette signature: deep crimson, burnished gold, emerald green, sapphire
    # blue, warm umber flesh — the palette of enamel and precious stone rather
    # than paint.  His grounds are dark warm umber-crimson, allowing the deep
    # base colour to glow through thin passages of glaze and giving his shadows
    # an internal fire absent from academic contemporaries.
    "gustave_moreau": ArtStyle(
        artist     = "Gustave Moreau",
        movement   = "Symbolism / Academic Idealism",
        nationality= "French",
        period     = "1826–1898",
        palette    = [
            (0.62, 0.14, 0.08),   # deep crimson — Moreau's defining shadow/accent hue
            (0.82, 0.62, 0.08),   # burnished gold — encrusted highlight fragments
            (0.10, 0.34, 0.28),   # deep emerald green — jewelled drapery and water
            (0.12, 0.22, 0.52),   # sapphire blue — mythological sky and water shadow
            (0.72, 0.52, 0.32),   # warm umber flesh — figure midtone
            (0.88, 0.74, 0.42),   # pale gold — upper highlight register
            (0.14, 0.08, 0.06),   # near-black umber — deep void background
        ],
        ground_color  = (0.18, 0.08, 0.05),   # dark warm crimson-umber ground
        stroke_size   = 4,                      # very fine — miniaturist precision
        wet_blend     = 0.25,                   # moderate: strokes stack, don't dissolve
        edge_softness = 0.20,                   # relatively crisp — draughtsman's precision
        jitter        = 0.04,                   # low jitter — controlled, patient marks
        glazing       = (0.62, 0.28, 0.10),    # deep warm crimson glaze — his warm unifier
        crackle       = True,                   # museum-aged large canvases crack prominently
        chromatic_split = False,                # no optical mixing — glazed accumulation
        technique=(
            "Moreau built his mythological paintings through obsessive accumulation: "
            "thousands of tiny, patient marks laid over a dark warm crimson-umber ground "
            "until the surface achieves the density and texture of encrusted enamel or "
            "Byzantine mosaic.  His technique fuses academic draughtsmanship (he drew "
            "incessantly — the Musée Moreau holds over ten thousand drawings) with a "
            "colourist approach drawn from Delacroix and the Venetian masters.  The dark "
            "warm ground is never fully covered: it glows through passages of thin glaze "
            "and becomes the shadow colour, giving his interiors a deep ruby warmth that "
            "academic contemporaries could not achieve with opaque darks.  Gold is "
            "literally scattered across his surfaces — tiny touches of yellow-gold paint "
            "applied as encrusted fragments, simulating the effect of gold leaf in "
            "medieval manuscript illumination.  His palette is the palette of precious "
            "stone: crimson, sapphire, emerald, burnished gold — never the pastel tints "
            "of the Impressionists.  Backgrounds dissolve into near-black mythological "
            "void from which architectural or natural details emerge like visions.  His "
            "great paintings include Salome Dancing Before Herod (1876), The Apparition "
            "(1876), Jupiter and Semele (1895), and Galatea (1880)."
        ),
        famous_works=[
            ("Salome Dancing Before Herod",      "1876"),
            ("The Apparition",                   "1876"),
            ("Jupiter and Semele",               "1895"),
            ("Galatea",                          "1880"),
            ("Oedipus and the Sphinx",           "1864"),
            ("The Unicorns",                     "1885"),
            ("Hercules and the Lernaean Hydra",  "1876"),
        ],
        inspiration=(
            "Use moreau_gilded_pass() as the primary surface technique: scatter "
            "burnished gold fragments across upper-midtone and highlight zones, "
            "and enrich deep shadows with a warm crimson glow that prevents "
            "the darks from reading as dead black.  "
            "tone_ground() with dark crimson-umber (0.18, 0.08, 0.05) — the warm "
            "underpinning that glows through all thin passages.  "
            "underpainting() and block_in() with moderate-to-fine marks.  "
            "venetian_glaze_pass() with warm amber-crimson (0.78, 0.38, 0.12) "
            "to unify the dark ground with the midtone passage.  "
            "moreau_gilded_pass() to apply stochastic gold-point fragments — "
            "the defining Moreau surface quality.  "
            "dark_void_pass() on background only to dissolve into mythological abyss.  "
            "place_lights() with warm amber-gold highlights (0.88, 0.74, 0.42).  "
            "Final glaze (0.62, 0.28, 0.10) crimson — his characteristic warm unifier.  "
            "Heavy crackle vignette — Moreau's large canvases are heavily museum-aged."
        ),
    ),

    # ── Hans Holbein the Younger ─────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Hans Holbein the Younger (c. 1497–1543) — German-Swiss master of the
    # Tudor court.  Working in Basel then London under Henry VIII, Holbein
    # brought the Northern panel tradition — superb draughtsmanship, silverpoint
    # underdrawings transferred by pouncing, thin oil-and-resin glazes over a
    # pale white ground — to a new plateau of objective fidelity.  His portraits
    # achieve an almost unsettling verisimilitude: the light falls without drama,
    # the surfaces are completely without visible brushwork, and every texture
    # (silk damask, ermine, gold chain) is rendered with equal, almost inhuman
    # attention.  Unlike his Italian contemporaries, who used warm amber varnishes
    # and sfumato to create atmospheric unity, Holbein kept each colour zone
    # independent — the crimson of a sleeve, the forest green of a gown, the
    # pale ivory of a face remain distinct, jewel-like, and saturated.  The
    # overall impression is that of a coloured miniature blown up to life scale.
    "holbein_the_younger": ArtStyle(
        artist="Hans Holbein the Younger",
        movement="Northern Renaissance / Tudor Court",
        nationality="German-Swiss",
        period="c. 1497–1543",
        palette=[
            (0.88, 0.78, 0.62),   # cool ivory flesh — pale, Flemish-influence skin
            (0.56, 0.40, 0.26),   # raw umber shadow — mid-tone shadow flesh
            (0.64, 0.08, 0.12),   # crimson lake — deep jewel red (madder)
            (0.18, 0.28, 0.60),   # azurite / smalt blue — cold, mineral blue
            (0.06, 0.22, 0.12),   # malachite / sap green — forest green
            (0.10, 0.10, 0.08),   # ivory black — deep neutral dark
            (0.84, 0.80, 0.68),   # lead-white highlight — warm but pale
            (0.72, 0.56, 0.18),   # gold-chain amber — burnished metal ornament
        ],
        ground_color=(0.88, 0.85, 0.78),    # near-white buff ground — all colours read independently
        stroke_size=4,
        wet_blend=0.12,                      # minimal blending — thin oil-glaze on dry ground
        edge_softness=0.18,                  # very crisp outline — no sfumato
        jitter=0.008,                        # near-photographic precision, minimal colour variation
        glazing=None,                        # no warm amber unifier — colours stay jewel-pure
        crackle=True,                        # aged oak-panel paintings crackle
        chromatic_split=False,               # no Seurat-style divisionism
        technique=(
            "Silverpoint underdrawing on sized paper, then transferred by pouncing "
            "to a pale white-ground panel (or vellum for miniatures).  Thin, resin-rich "
            "oil glazes applied over completely dry underlayers: no wet-into-wet blending. "
            "Each colour zone is built individually — crimson sleeve, green gown, ivory face "
            "— and kept distinct.  No warm amber varnish unifies the surface: each hue "
            "retains its full chromatic identity, producing the 'jewel' quality that "
            "distinguishes Holbein's palette from the warm, atmospheric unity of the Italian "
            "schools.  Skin modelling is extremely subtle — the light source is diffused "
            "and almost frontal, creating smooth tonal transitions without drama or chiaroscuro. "
            "Hands, fabrics, and accessories receive the same minute attention as the face."
        ),
        famous_works=[
            ("The Ambassadors",                  "1533"),
            ("Portrait of Henry VIII",            "c. 1536–1537"),
            ("Christina of Denmark",              "1538"),
            ("Portrait of Jane Seymour",          "c. 1536"),
            ("Portrait of Erasmus of Rotterdam",  "1523"),
            ("Portrait of Thomas More",           "1527"),
            ("Anne of Cleves",                    "c. 1539"),
        ],
        inspiration=(
            "Use pale buff ground (ground_color ≈ (0.88, 0.85, 0.78)).  "
            "holbein_jewel_glaze_pass() to boost mid-tone chroma and cool/warm the "
            "luminance extremes — the defining jewel-depth quality of his surfaces.  "
            "Low wet_blend and low edge_softness: colours and contours stay precise.  "
            "porcelain_skin_pass() for seamless, nearly-shadowless flesh rendering.  "
            "micro_detail_pass() for fabric textures and chain links.  "
            "No sfumato_veil_pass — Holbein's edges never dissolve into atmosphere.  "
            "Final glaze with near-neutral cool veil rather than warm amber."
        ),
    ),

    # ── Anthony van Dyck ──────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Anthony van Dyck (1599–1641) — Flemish Baroque court painter who defined
    # the language of aristocratic portraiture for a century.  Born in Antwerp,
    # a child prodigy who became Rubens's chief assistant before establishing
    # an independent career in Genoa and then London as court painter to Charles I.
    # His signature is the fusion of Rubens's physical confidence with a personal
    # psychological sensitivity: sitters look inward, melancholic, aware of their
    # own fragility despite the grandeur of their setting.  Technically his most
    # celebrated contribution is the rendering of silk — especially the shimmering
    # silver-grey English court silks that appear in virtually every late portrait.
    # Paint thin and fast over a warm reddish-brown imprimatura; lay the dark of
    # the background in swiftly; then model the face with patient small strokes
    # using lead white, naples yellow, and Van Dyck brown; finally, render the
    # silk with rapid, confident loaded strokes that follow the fabric's fall,
    # leaving light peaks and cool shadow valleys across the cloth.
    "anthony_van_dyck": ArtStyle(
        artist="Anthony van Dyck",
        movement="Flemish / English Baroque",
        nationality="Flemish",
        period="1617–1641",
        palette=[
            (0.88, 0.70, 0.52),   # warm flesh highlight — Naples yellow-red
            (0.65, 0.48, 0.30),   # mid-tone flesh — warm umber
            (0.28, 0.16, 0.08),   # Van Dyck brown — deep warm shadow
            (0.05, 0.05, 0.06),   # ivory black — near-black background / velvet
            (0.72, 0.74, 0.78),   # pearl-grey silk — highlight side
            (0.56, 0.58, 0.62),   # mid-grey silk — shadow side of silver drapery
            (0.62, 0.08, 0.12),   # crimson lake — warm red velvet
            (0.15, 0.22, 0.58),   # ultramarine — cool accessory blue
            (0.92, 0.88, 0.82),   # lead-white highlight — final brilliant touch
        ],
        ground_color=(0.35, 0.22, 0.10),    # warm reddish-brown imprimatura
        stroke_size=9,
        wet_blend=0.45,                      # fluid wet-into-wet; confident blending
        edge_softness=0.48,                  # present but yielding — no sfumato, no blade edge
        jitter=0.038,
        glazing=(0.48, 0.32, 0.10),          # warm amber-brown final varnish
        crackle=True,
        chromatic_split=False,
        technique=(
            "Warm reddish-brown imprimatura brushed over the panel or canvas ground "
            "— this toned ground gives the shadows their deep warm unity without "
            "extra glazes.  Background and costume laid in quickly and broadly, "
            "wet-into-wet, with large hog-hair brushes.  The face modelled with "
            "more patient small marks: flesh mid-tones blended softly, shadows built "
            "from Van Dyck brown (raw umber + ivory black + venetian red), highlights "
            "applied last with thick lead-white.  Silk drapery — van Dyck's most "
            "celebrated achievement — rendered with rapid loaded strokes following "
            "the fabric's fall, leaving bright ridges of thick pearl-grey paint "
            "alternating with cool shadow valleys; the shimmer of woven silk reproduced "
            "by varying stroke pressure and direction.  Hands and fingers 'van Dyck "
            "elongated' — tapered, aristocratic, rendered with individual care.  Final "
            "warm amber-brown glaze unifies the surface."
        ),
        famous_works=[
            ("Charles I at the Hunt",                          "c. 1635"),
            ("Equestrian Portrait of Charles I",               "c. 1637–1638"),
            ("Portrait of Marchesa Elena Grimaldi",            "1623"),
            ("The Balbi Children",                             "c. 1625–1627"),
            ("Portrait of Henrietta Maria with Sir Jeffrey Hudson", "1633"),
            ("Thomas Howard, 2nd Earl of Arundel",             "c. 1620–1621"),
            ("Self-Portrait with a Sunflower",                 "c. 1632–1633"),
        ],
        inspiration=(
            "Use warm reddish-brown imprimatura (ground_color ≈ (0.35, 0.22, 0.10)).  "
            "van_dyck_silver_drapery_pass() for the shimmering silver-grey silk: "
            "sinusoidal shimmer along fabric perpendicular, silver-cool shift, "
            "ivory specular push in brightest highlights.  moderate wet_blend and "
            "edge_softness: edges are present and readable but not harshly Northern.  "
            "Place Van Dyck brown shadows early; lead-white highlights late and thick.  "
            "Final warm amber-brown glaze (0.48, 0.32, 0.10) at low opacity to unify."
        ),
    ),

    # ── Fra Angelico ──────────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Fra Angelico (c. 1395–1455) — "Beato Angelico" — bridges the International
    # Gothic and Early Renaissance.  His tempera technique on white gesso panels
    # produces an unmatched luminous purity: mineral pigments (lapis lazuli,
    # vermilion, lead white) remain undimmed by the warm amber varnishes that
    # characterise later oil-based schools.  Gold leaf halos and sky-blue
    # mandorlas glow with a supernatural intensity.  Forms are outlined with
    # a confident, gentle contour; flesh is built up in thin, parallel
    # hatching strokes rather than blended wet-on-wet.  The result is at once
    # archaic (flat, icon-like gold zones) and surprisingly modern: the colour
    # relationships are radically pure and the serene, otherworldly mood
    # is achieved entirely through palette and composition.
    "fra_angelico": ArtStyle(
        artist="Fra Angelico (Guido di Pietro)",
        movement="International Gothic / Quattrocento",
        nationality="Italian",
        period="c. 1418–1455",
        palette=[
            (0.94, 0.88, 0.68),   # lead-white highlight — pure gesso luminosity
            (0.82, 0.65, 0.45),   # warm ivory flesh — tempera skin mid-tone
            (0.48, 0.36, 0.22),   # raw sienna — flesh shadow hatching
            (0.18, 0.38, 0.72),   # lapis lazuli blue — celestial robes / sky
            (0.88, 0.22, 0.18),   # vermilion red — angels / robes
            (0.85, 0.72, 0.12),   # gold leaf — halos / borders
            (0.38, 0.55, 0.32),   # verdigris green — secondary drapery
            (0.90, 0.85, 0.75),   # pale gesso ground — showing between strokes
        ],
        ground_color=(0.96, 0.94, 0.88),    # chalk-white gesso panel — brilliant, not warm
        stroke_size=4,
        wet_blend=0.05,                      # tempera dries almost instantly — no wet blending
        edge_softness=0.22,                  # gentle contour edges, no sfumato
        jitter=0.018,
        glazing=None,                        # no unifying amber glaze — colours stay pure
        crackle=True,                        # aged tempera panel crackle
        chromatic_split=False,
        technique=(
            "Egg-tempera on chalk-white gesso panel.  Forms built up by fine parallel "
            "hatching strokes (piani di colore) rather than wet blending.  Each stroke "
            "is dragged over a dry previous layer, building tonal depth through hatching "
            "density rather than impasto or sfumato.  Gold leaf applied on bole and "
            "burnished to a mirror finish for halos and architectural ornament.  Colour "
            "zones remain flat and pure — lapis remains deep blue without glaze warmth; "
            "vermilion remains chromatic and undimmed.  The pale gesso ground acts as "
            "its own source of light, glowing between the hatching strokes."
        ),
        famous_works=[
            ("Annunciation (San Marco fresco)", "c. 1438–1447"),
            ("Coronation of the Virgin (Uffizi)", "c. 1432"),
            ("The Last Judgement", "c. 1432–1435"),
            ("Madonna of Humility (Prado)", "c. 1433–1435"),
        ],
        inspiration=(
            "Use white gesso ground (ground_color near white).  hatching_pass() for "
            "building tonal form — fine parallel strokes at ~45° over dry layers.  "
            "Zero wet_blend.  Preserve colour purity: no amber glaze.  "
            "Gold highlight zones via place_lights() with (0.88, 0.72, 0.12) gold.  "
            "Gentle contour outlines via thin dark hatch lines at figure edges."
        ),
    ),

    # ── Peter Paul Rubens ──────────────────────────────────────────────────────
    # Randomly selected artist for this session's inspiration.
    # Peter Paul Rubens (1577–1640) — the supreme master of Flemish Baroque,
    # arguably the most technically accomplished and prolific painter of the
    # seventeenth century.  Born in Siegen, Westphalia, trained in Antwerp, and
    # deeply formed by a decade in Italy (1600–1608) studying Titian, Veronese,
    # and Caravaggio.  What makes Rubens unmistakable is not grand composition
    # alone but an almost uncanny ability to render living flesh — warm, rosy,
    # translucent, breathing.  He achieved this through a disciplined multi-layer
    # technique: a reddish-brown imprimatura (he called this the "preparation")
    # over which he blocked in dead-colour monochrome, then built flesh in three
    # to five glazed layers, each applied wet-on-wet before the previous fully
    # dried, so colours mingled without muddying.  The final touches — thick
    # lead-white impasto at cheekbones, forehead, and nose tip — were pressed on
    # with a palette knife, leaving a textural ridge that catches raking light.
    # Thin-skin zones (ears, nose, lips, knuckles) were treated with an extra
    # glaze of vermilion or rose madder, giving them a flushed, vascular warmth
    # entirely absent from his Northern contemporaries.  Shadows are never cool
    # or grey in Rubens — they glow with a deep brownish-red transmitted light,
    # as though the figure were lit from within.  This is the quality that
    # rubens_flesh_vitality_pass() approximates.
    # ── Nicolas Poussin ───────────────────────────────────────────────────────
    # Poussin is the supreme classicist of European painting.  Born in Normandy,
    # trained in Paris, he settled permanently in Rome in 1624 and devoted himself
    # to classical antiquity, Stoic philosophy, and the rational organisation of
    # pictorial space.  His paintings are argued compositions: every figure, every
    # gesture, every colour zone is placed with deliberate architectural intent.
    #
    # Poussin's technique differs from the warm Baroque tradition around him in
    # three crucial ways:
    #
    #   1. COOL SHADOWS — Unlike Rembrandt (warm brown), Rubens (brownish-red),
    #      or Caravaggio (near-black), Poussin's shadow areas have a silvery,
    #      blue-grey quality derived from his close study of classical marble
    #      sculpture in Rome.  Marble casts cool grey shadows, and his figures —
    #      conceived as living sculptures — reflect this quality.
    #
    #   2. RATIONAL COLOUR IDENTITY — Poussin dressed each figure in a distinct
    #      colour badge (his famous azure/vermilion/yellow triads) so that the
    #      composition could be read from across a gallery as a clear chromatic
    #      argument.  No two major figures share the same hue.
    #
    #   3. SATURATION DISCIPLINE — His palette is radiant but never garish.
    #      No colour dominates the whole surface; every hue is placed in a tonal
    #      context that gives it value without allowing it to overwhelm.
    #
    # poussin_classical_clarity_pass() approximates these three qualities.
    "nicolas_poussin": ArtStyle(
        artist="Nicolas Poussin",
        movement="French Classicism / Grand Manner",
        nationality="French",
        period="1624–1665",
        palette=[
            (0.80, 0.70, 0.56),   # warm ivory flesh highlight — cool lead white
            (0.60, 0.48, 0.34),   # warm flesh mid-tone
            (0.30, 0.18, 0.10),   # umber shadow flesh
            (0.22, 0.44, 0.72),   # Poussin azure blue — his signature garment hue
            (0.76, 0.24, 0.16),   # clear vermilion red — garment accent
            (0.72, 0.68, 0.22),   # acid yellow-gold — sunlit fabric / hair
            (0.28, 0.50, 0.30),   # classical forest green — landscape / drapery
            (0.58, 0.60, 0.64),   # cool silver-grey shadow — marble-cast quality
            (0.66, 0.62, 0.48),   # warm golden ochre — Arcadian landscape ground
        ],
        ground_color=(0.52, 0.48, 0.38),    # neutral warm ochre imprimatura — not the hot
                                             # reddish-brown of Rubens; Poussin's ground
                                             # is temperate and architectural
        stroke_size=7,
        wet_blend=0.38,                      # deliberate layering — not wet-on-wet alla prima;
                                             # each passage is considered before the next begins
        edge_softness=0.42,                  # clear, legible classical edges — no sfumato haze;
                                             # forms read as rational sculpture, not atmosphere
        jitter=0.022,
        glazing=(0.60, 0.62, 0.64),          # cool silver-neutral unifying glaze — slightly more
                                             # blue than red; the opposite of warm Baroque varnish
        crackle=True,
        chromatic_split=False,
        technique=(
            "Rational classical composition built on a moderate warm-ochre imprimatura.  "
            "Each figure is given a distinct chromatic identity (azure/vermilion/yellow "
            "triads) so the composition reads as a clear chromatic argument at distance.  "
            "Shadows are cool and silvery — derived from the marble sculpture Poussin studied "
            "in Rome — rather than the warm browns of the Baroque tradition.  "
            "Brushwork is deliberate and patient: thin oil layers, no impasto, no wet-on-wet "
            "alla prima; Poussin re-drew and re-painted passages until they satisfied his "
            "geometric and philosophical criteria.  The final surface is smooth and silvery, "
            "with a cool near-neutral glaze unifying the whole picture plane."
        ),
        famous_works=[
            ("Et in Arcadia Ego (The Arcadian Shepherds)", "c. 1637–1638"),
            ("The Rape of the Sabine Women",               "c. 1634–1635"),
            ("A Dance to the Music of Time",               "c. 1634–1636"),
            ("Landscape with Saint John on Patmos",        "1640"),
            ("The Holy Family on the Steps",               "1648"),
            ("Landscape with the Burial of Phocion",       "1648"),
        ],
        inspiration=(
            "Apply poussin_classical_clarity_pass() for cool silver shadows, "
            "rational mid-tone clarity, and saturation discipline.  "
            "Use the azure/vermilion/yellow palette triad for figure garments.  "
            "Cool silver-neutral glaze (0.60, 0.62, 0.64) at very low opacity "
            "unifies without warming.  Keep wet_blend moderate (0.38) — Poussin "
            "layers deliberately, not alla prima."
        ),
    ),

    "peter_paul_rubens": ArtStyle(
        artist="Peter Paul Rubens",
        movement="Flemish Baroque",
        nationality="Flemish",
        period="1600–1640",
        palette=[
            (0.95, 0.80, 0.64),   # warm cream flesh highlight — lead white + naples yellow
            (0.88, 0.65, 0.48),   # warm flesh mid-tone — naples yellow + vermilion
            (0.82, 0.50, 0.40),   # rosy blush — vermilion tint in thin-skin zones
            (0.64, 0.40, 0.24),   # warm umber flesh shadow
            (0.52, 0.28, 0.12),   # deep brownish-red transmitted shadow
            (0.26, 0.12, 0.05),   # near-black void — sparingly used
            (0.76, 0.22, 0.12),   # vermilion lake — fabric, lips, accent
            (0.12, 0.26, 0.58),   # ultramarine — cool sky and garment accent
        ],
        ground_color=(0.44, 0.28, 0.12),    # warm reddish-brown imprimatura
        stroke_size=10,
        wet_blend=0.62,                      # fluid alla prima; wet-on-wet layers
        edge_softness=0.42,                  # edges present and readable; no Northern crispness
        jitter=0.055,
        glazing=(0.55, 0.36, 0.14),          # warm amber-red unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Warm reddish-brown imprimatura over linen.  Dead-colour block-in in "
            "raw umber monochrome to establish masses.  Flesh built wet-on-wet "
            "through three to five layers, each modifying the last before fully "
            "drying: mid-tones of naples yellow, vermilion, and lead white; "
            "shadows of raw umber deepened with ivory black.  Thin-skin zones "
            "(ears, nose tip, lips, knuckles) receive an extra glaze of vermilion "
            "or rose madder — the blush that gives Rubens figures their living warmth.  "
            "Deep shadows glow with brownish-red transmitted light, never turning "
            "cold or grey.  Final highlights pressed on with thick lead-white "
            "impasto, leaving a raised ridge at cheekbones, forehead, and nose "
            "bridge.  A warm amber-red varnish glaze unifies the whole surface."
        ),
        famous_works=[
            ("The Descent from the Cross",                    "1612–1614"),
            ("The Rape of the Daughters of Leucippus",        "c. 1617–1618"),
            ("Samson and Delilah",                            "c. 1609–1610"),
            ("The Three Graces",                              "c. 1635"),
            ("Peace and War (Minerva Protects Pax from Mars)", "1629–1630"),
            ("The Garden of Love",                            "c. 1630–1635"),
            ("Self-Portrait",                                 "c. 1638–1640"),
        ],
        inspiration=(
            "Use warm reddish-brown imprimatura (ground_color ≈ (0.44, 0.28, 0.12)).  "
            "rubens_flesh_vitality_pass() for the hallmark warm, pink-vitality skin: "
            "rosy blush in mid-luminance thin-skin zones, creamy ivory push at "
            "highlight peaks, warm brownish-red undertone in deep shadows.  "
            "High wet_blend (0.62) for fluid wet-on-wet blending; moderate "
            "edge_softness (0.42) keeps forms readable.  Final warm amber-red glaze "
            "(0.55, 0.36, 0.14) at low opacity unifies the whole surface."
        ),
    ),

    # ── Thomas Gainsborough ────────────────────────────────────────────────────
    #
    # Thomas Gainsborough (1727–1788) was the supreme British portrait and
    # landscape painter of the 18th century.  He worked in direct competition
    # with Sir Joshua Reynolds — while Reynolds favoured grand classical
    # gravity and warm academic flesh tones, Gainsborough's answer was a
    # breathtaking lightness: silvery, feathery, alive with atmosphere.
    #
    # His technical signatures:
    #
    #   1. FEATHERY BRUSHWORK — Gainsborough used very long, flexible brushes
    #      (sometimes taped to sticks) to apply paint from a distance.  Each
    #      stroke ended in a fine, broken, tapered "feather" rather than a blunt
    #      edge.  This is most visible at the boundaries between flesh and
    #      background, and throughout drapery passages.  The effect is as if
    #      edges were combed outward in the direction of the brush.
    #
    #   2. COOL SILVER TONALITY — Unlike the warm ochre and umber tradition
    #      of the Old Masters, Gainsborough's highlights tend toward a cool,
    #      blue-white silver.  He admired Van Dyck's pearl-grey silk passages
    #      and translated that quality into flesh and landscape.  His shadows
    #      in drapery areas often carry a subtle blue-grey cast.
    #
    #   3. FLUID, LIQUID APPLICATION — He famously worked in a dim studio by
    #      candlelight (to soften tonal contrasts) and applied paint in very
    #      thin fluid layers — sometimes so liquid they would run if not caught
    #      with a broad brush immediately.  This produces a streaming, fluid
    #      quality in drapery and hair unlike any contemporary British painter.
    #
    #   4. FIGURE EMBEDDED IN LANDSCAPE — Uniquely for the era, Gainsborough
    #      always treated his sitter and their landscape as a single
    #      atmospheric whole.  The background atmospheric haze literally
    #      bleeds into the figure's silhouette, and the figure's costume often
    #      carries the same cool blue-grey as the sky.
    #
    # gainsborough_feathery_pass() approximates these qualities.
    "thomas_gainsborough": ArtStyle(
        artist="Thomas Gainsborough",
        movement="British Rococo / Grand Manner Portrait",
        nationality="British",
        period="1745–1788",
        palette=[
            (0.90, 0.86, 0.82),   # silver-white highlight — cool, not cream
            (0.76, 0.68, 0.60),   # warm pearl flesh mid-tone
            (0.58, 0.52, 0.46),   # cool grey-tan flesh shadow
            (0.38, 0.30, 0.22),   # warm umber deep shadow
            (0.64, 0.70, 0.78),   # cool blue-grey sky / background haze
            (0.30, 0.40, 0.52),   # deep blue-grey shadow in drapery
            (0.72, 0.64, 0.50),   # warm gold — satin or silk highlights
            (0.44, 0.54, 0.40),   # soft landscape green — foliage distance
            (0.56, 0.62, 0.68),   # atmospheric silver-blue — sky and far distance
        ],
        ground_color=(0.72, 0.68, 0.62),    # pale warm-grey ground — Gainsborough
                                             # often used a light grey or cream
                                             # preparation, far cooler than the warm
                                             # reddish imprimatura of the Baroque
        stroke_size=8,
        wet_blend=0.55,                      # moderate-high — fluid oil applied wet-
                                             # into-wet; each feathered stroke blends
                                             # at its tip into the previous layer
        edge_softness=0.68,                  # high — the feathery dissolution of edges
                                             # is Gainsborough's hallmark; forms melt
                                             # into background without hard seams
        jitter=0.040,
        glazing=(0.58, 0.64, 0.72),          # cool blue-silver unifying glaze —
                                             # even cooler than Poussin's silver;
                                             # Gainsborough unified his whole surface
                                             # with a cool atmospheric veil
        crackle=True,
        chromatic_split=False,
        technique=(
            "Feathery fluid oil on a pale grey-cream ground.  "
            "Applied with very long flexible brushes from a distance, "
            "each stroke ending in a tapered, broken 'feather' that "
            "dissolves into adjacent passages.  Cool silver-blue tonality "
            "throughout — highlights lean toward blue-white silver rather "
            "than warm ivory.  Thin, liquid paint layers applied wet-into-wet; "
            "the figure and landscape background share the same atmospheric "
            "cool haze, so the sitter appears to inhabit and breathe the "
            "same air as their landscape setting."
        ),
        famous_works=[
            ("The Blue Boy",                                        "c. 1770"),
            ("Mr and Mrs Andrews",                                  "c. 1750"),
            ("Portrait of Mrs. Richard Brinsley Sheridan",          "1785–1787"),
            ("The Morning Walk (Mr and Mrs William Hallett)",       "1785"),
            ("Portrait of Jonathan Buttall",                        "c. 1770"),
            ("Lady Innes",                                          "c. 1757"),
            ("The Painter's Daughters Chasing a Butterfly",        "c. 1756"),
        ],
        inspiration=(
            "Use gainsborough_feathery_pass() for the hallmark feathery "
            "edge dissolution, cool silver-blue highlights, and fluid midtone "
            "shimmer.  Pale grey-cream ground_color (0.72, 0.68, 0.62).  "
            "High edge_softness (0.68) — Gainsborough's figures fade into "
            "their backgrounds.  Cool blue-silver glaze (0.58, 0.64, 0.72) "
            "at very low opacity unifies figure and landscape into one atmosphere."
        ),
    ),

    # ── Winslow Homer ─────────────────────────────────────────────────────────
    # Homer was America's greatest marine and genre painter, self-taught in
    # Gloucester watercolour technique before translating the same chromatic
    # transparency to large-scale oil.  His mature work (1880–1910, Prouts Neck,
    # Maine) is characterised by:
    #   • Brilliant upper-left maritime light striking a lit foreground plane
    #   • Deep, transparent cool-blue shadows (Atlantic ocean / overcast sky)
    #   • High tonal contrast — he separated light from shadow decisively,
    #     with almost no halftone zone between them (influenced by Japanese prints)
    #   • A "wet-paper" watercolour quality even in oil: thin translucent paint
    #     over a white gessoed ground so the support glows through the pigment
    #   • Confident, unretouched brushwork — once placed, a stroke was not corrected
    #   • Horizontal compositional banding: sea / horizon / sky in thirds
    # homer_marine_clarity_pass() approximates these qualities.
    "winslow_homer": ArtStyle(
        artist="Winslow Homer",
        movement="American Realism / Marine Painting",
        nationality="American",
        period="1865–1910",
        palette=[
            (0.95, 0.92, 0.85),   # brilliant maritime white — sunlit foam / sail
            (0.82, 0.75, 0.58),   # warm ochre — weathered wood, rope, flesh
            (0.68, 0.58, 0.40),   # raw sienna — mid-tone flesh / hull timber
            (0.38, 0.28, 0.18),   # warm umber deep shadow — under decks, coat
            (0.26, 0.40, 0.58),   # slate-blue ocean shadow — Atlantic cold water
            (0.44, 0.58, 0.72),   # mid-ocean blue — lit wave surface
            (0.65, 0.75, 0.82),   # pale Atlantic sky — overcast silver-blue
            (0.18, 0.28, 0.42),   # deep Prussian storm sea — dark wave trough
            (0.72, 0.64, 0.52),   # warm sand / beach ochre
        ],
        ground_color=(0.96, 0.95, 0.93),    # near-white gessoed panel or paper —
                                             # Homer's most important tonal decision;
                                             # the white ground glows through every
                                             # transparent layer, giving his shadows
                                             # their luminous quality despite being dark
        stroke_size=9,
        wet_blend=0.30,                      # moderate — Homer placed strokes
                                             # decisively and rarely blended; wet-into-wet
                                             # in the sky and sea, dry-over-dry in detail
        edge_softness=0.35,                  # moderate — marine edges are present
                                             # (horizon is crisp), but atmospheric
                                             # perspective softens far distance;
                                             # figures have clear silhouette edges
        jitter=0.030,
        glazing=(0.44, 0.58, 0.72),          # cool Atlantic blue-grey unifying glaze —
                                             # binds sky, sea, and shadow into a
                                             # coherent cool atmosphere; opposite of
                                             # Leonardo's warm amber — this is cold salt air
        crackle=True,
        chromatic_split=False,
        technique=(
            "Transparent oil and watercolour over near-white gessoed panel or paper.  "
            "Brilliant maritime light from upper-left illuminates foreground figures "
            "and breaking wave crests in warm ochre-white.  Deep shadows are cool "
            "slate-blue and Prussian (the Atlantic in shadow is cold and deep).  "
            "High tonal contrast with minimal halftone — Homer learned from Japanese "
            "woodblock prints to separate light from dark decisively.  Confident, "
            "unretouched brushwork: each stroke placed once and left.  Thin paint "
            "over white ground glows with internal luminosity even in dark passages."
        ),
        famous_works=[
            ("The Life Line",                       "1884"),
            ("Fog Warning (Halibut Fishing)",        "1885"),
            ("Eight Bells",                         "1886"),
            ("Breezing Up (A Fair Wind)",            "1876"),
            ("The Blue Boat",                       "1892"),
            ("Sloop, Nassau",                       "1899"),
            ("Kissing the Moon",                    "1904"),
            ("The Winslow Homer Sponge Fishing",    "1885"),
        ],
        inspiration=(
            "Use homer_marine_clarity_pass() for the hallmark maritime tonal clarity: "
            "cool Prussian-blue shadows, brilliant near-white maritime highlights, "
            "and the transparent-wash luminosity of thin paint over white ground.  "
            "Near-white ground_color (0.96, 0.95, 0.93).  Moderate wet_blend (0.30) "
            "and edge_softness (0.35) — decisive, unretouched strokes with clear "
            "silhouette edges.  Cool blue-grey glaze (0.44, 0.58, 0.72) unifies the "
            "composition in Atlantic salt-air atmosphere."
        ),
    ),

    # ── Pierre-Auguste Renoir ─────────────────────────────────────────────────
    # Renoir was the supreme portraitist of French Impressionism — his canvases
    # glow with warm, saturated colour and a luminous, almost confection-like
    # quality of light.  His mature style (1870s–1880s) is defined by:
    #   • Rich chromatic saturation — every hue at maximum luminous intensity;
    #     reds are rose-warm, greens are spring-fresh, blues are sky-warm not cold
    #   • Warm, rosy flesh tones — Renoir's skin is peach-rose; never the cool
    #     ivory of Academic painting, never the umber warmth of Rembrandt
    #   • Dappled, broken light — outdoor and garden scenes with shifting pools
    #     of warm and cool light flickering across figures and foliage
    #   • Feathery, curving brushwork — strokes follow the surface, curving with
    #     the form; lively but not angular like Van Gogh's impasto
    #   • Warm peach-cream highlights — highlights bloom warm, never silvery-cold
    # renoir_luminous_warmth_pass() approximates these qualities.
    "pierre_auguste_renoir": ArtStyle(
        artist="Pierre-Auguste Renoir",
        movement="French Impressionism",
        nationality="French",
        period="1867–1919",
        palette=[
            (0.97, 0.91, 0.82),   # warm cream-white highlight — sunlit skin, lace
            (0.92, 0.72, 0.68),   # rose-peach flesh mid-tone — his signature warmth
            (0.80, 0.56, 0.50),   # warm peach shadow — deepening flesh tones
            (0.52, 0.32, 0.28),   # warm umber shadow — dark hair, deep shade
            (0.58, 0.74, 0.52),   # spring leaf green — garden foliage
            (0.68, 0.82, 0.88),   # warm sky blue — his skies are warm, not cold
            (0.86, 0.60, 0.70),   # rose-pink — ribbons, lips, warm drapery
            (0.94, 0.80, 0.52),   # warm golden sunlight — dappled afternoon
            (0.42, 0.56, 0.70),   # soft warm blue-grey — shadows in drapery
        ],
        ground_color=(0.94, 0.88, 0.80),    # warm pale ivory ground — Renoir prepared
                                            # his canvases with a warm cream-white; the
                                            # ground glows through thin paint and unifies
                                            # the whole surface in warm ambient light
        stroke_size=8,
        wet_blend=0.55,                      # moderate — Renoir worked wet-into-wet
                                            # throughout; strokes blend at their tips into
                                            # the preceding layer, but each mark retains
                                            # its identity — not the total dissolution
                                            # of Leonardo's sfumato
        edge_softness=0.48,                  # moderate-soft — edges are present and
                                            # readable (Renoir's figures are not dissolved
                                            # like Gainsborough's), but contours are
                                            # gently diffused, especially where foliage
                                            # or dappled light breaks up the boundary
        jitter=0.045,
        glazing=(0.90, 0.72, 0.62),          # warm peach-rose glaze — unifies the
                                            # whole surface in a rosy warmth; the
                                            # characteristic Renoir "glow" that
                                            # reads as warm afternoon garden light
        crackle=True,
        chromatic_split=False,
        technique=(
            "Rich, feathery oil on pale warm-ivory ground.  "
            "Strokes are curving and surface-following — each mark traces the form "
            "beneath it, giving the paint surface a living, breathing quality.  "
            "Flesh tones are warm rose-peach throughout; shadows deepen in warm umber "
            "with no cool blue intrusion — Renoir explicitly rejected the Impressionist "
            "convention of cool violet shadows.  Highlights bloom in warm cream-gold, "
            "not silver.  The palette is maximally chromatic — saturation runs high.  "
            "A warm peach-rose glaze over the whole surface unifies all colours into "
            "the characteristic Renoir warmth."
        ),
        famous_works=[
            ("Dance at Le Moulin de la Galette",    "1876"),
            ("Luncheon of the Boating Party",        "1880–1881"),
            ("Two Sisters (On the Terrace)",         "1881"),
            ("The Large Bathers",                    "1887"),
            ("Madame Georges Charpentier and Her Children", "1878"),
            ("La Loge (The Theatre Box)",            "1874"),
            ("Girl with a Watering Can",             "1876"),
        ],
        inspiration=(
            "Use renoir_luminous_warmth_pass() for the hallmark warm saturation boost, "
            "rose-peach flesh tone push, and luminous highlight bloom.  Warm pale-ivory "
            "ground_color (0.94, 0.88, 0.80).  Moderate wet_blend (0.55) and "
            "edge_softness (0.48) — feathery, curving marks with soft but readable edges.  "
            "Warm peach-rose glaze (0.90, 0.72, 0.62) unifies in garden-afternoon warmth.  "
            "No cool blue in shadows — Renoir's darks are warm umber throughout."
        ),
    ),

    # ── Artemisia Gentileschi ─────────────────────────────────────────────────
    # Artemisia Gentileschi (1593–1653) stands apart from Caravaggio's pure
    # tenebrism: where Caravaggio's flesh emerges cold from absolute void,
    # Gentileschi's subjects carry a warm candlelit humanity — flesh tones are
    # richer, more saturated, emotionally charged.  Her defining qualities:
    #   • Warm shadow zone — shadows are deep warm umber-brown, never the cold
    #     near-black of Caravaggio; the half-shadow carries a warm olive-amber cast
    #     that reads as firelight absorbed into the flesh rather than an absence of light
    #   • Theatrical single-source illumination — harsh directional light from upper-left;
    #     lit faces gleam with warm golden highlights while the far side falls to deep
    #     shadow in a steep, dramatic gradient
    #   • Deep crimson / burgundy drapery — rich saturated red contrasting against warm
    #     flesh and dark ground; her cloth has physical weight and sculptural folds
    #   • Confident, energetic brushwork in lit areas — not the patient sfumato of
    #     Leonardo; Gentileschi painted decisively, with thick impasto in the highlights
    #     and thinner, more transparent glazes in the shadows
    #   • Psychological intensity — her figures have an interiority lacking in many
    #     Baroque contemporaries; the face is always the emotional centre
    # gentileschi_dramatic_flesh_pass() approximates these qualities.
    "artemisia_gentileschi": ArtStyle(
        artist="Artemisia Gentileschi",
        movement="Italian Baroque / Tenebrism",
        nationality="Italian",
        period="1593–1653",
        palette=[
            (0.89, 0.70, 0.48),   # warm candlelit flesh highlight — golden amber warmth
            (0.72, 0.52, 0.34),   # rose-warm flesh midtone — the key flesh register
            (0.52, 0.36, 0.22),   # warm mid-shadow — the penumbra zone, olive warmth
            (0.32, 0.22, 0.12),   # deep warm umber shadow — not cold black, warm brown
            (0.08, 0.06, 0.04),   # near-black void background — not absolute; retains warmth
            (0.62, 0.10, 0.08),   # deep crimson drapery — her signature rich red
            (0.78, 0.60, 0.20),   # warm amber-gold accent — collar trim, jewel, candlelight
            (0.30, 0.36, 0.20),   # deep olive — shadow within cloth, distant fabric
        ],
        ground_color=(0.14, 0.10, 0.06),    # very dark warm brown ground — Gentileschi
                                            # prepared on a dark warm imprimatura; this
                                            # ground shows through shadow zones, warming
                                            # the darks from beneath and preventing the
                                            # cold void of Caravaggio's black grounds
        stroke_size=9,
        wet_blend=0.32,                      # deliberate but not dry — confident marks
                                            # that stay distinct in the shadow zone but
                                            # allow some wet-into-wet blending in the
                                            # highly-worked lit flesh areas
        edge_softness=0.42,                  # moderate — not sfumato (Leonardo), not
                                            # razor-sharp (Schiele); Gentileschi's edges
                                            # are legible and confident but not harsh
        jitter=0.040,
        glazing=(0.58, 0.38, 0.16),          # warm amber-umber glaze — enriches the
                                            # shadow zone with depth; applied thinly over
                                            # the dark ground to warm the entire canvas
                                            # in candlelit amber
        crackle=True,
        chromatic_split=False,
        technique=(
            "Baroque tenebrism with warm emotional flesh — Gentileschi took Caravaggio's "
            "dramatic chiaroscuro but suffused the shadows with warm umber rather than "
            "cold black void.  A dark warm-brown imprimatura shows through all shadow "
            "areas, preventing the cold nihilism of pure tenebrism.  Single-source "
            "directional lighting illuminates flesh in warm golden-amber highlights; "
            "the penumbra carries an olive-warm intermediate tone; the shadow zone "
            "deepens to warm umber-brown rather than absolute darkness.  Highlights are "
            "applied in thick, confident impasto — not sfumato; the brushwork is "
            "energetic and decisive in the lit areas.  Deep crimson drapery provides "
            "chromatic contrast against the warm flesh and dark ground.  The face is "
            "always the psychological centre: Gentileschi's protagonists meet the viewer "
            "with directness and psychological intensity rarely found in Baroque portraiture."
        ),
        famous_works=[
            ("Judith Slaying Holofernes",              "c. 1614–1620"),
            ("Self-Portrait as the Allegory of Painting", "c. 1638–1639"),
            ("Susanna and the Elders",                 "1610"),
            ("Judith and Her Maidservant",             "c. 1623–1625"),
            ("Mary Magdalene as Melancholy",           "c. 1621–1622"),
            ("Lucretia",                               "c. 1621"),
        ],
        inspiration=(
            "Use gentileschi_dramatic_flesh_pass() for the hallmark warm shadow zone, "
            "deep warm umber-brown darks, and golden candlelit highlight lift.  "
            "Dark warm brown ground_color (0.14, 0.10, 0.06) — shows through shadows "
            "and warms the entire canvas.  Moderate wet_blend (0.32) and edge_softness (0.42) "
            "— confident, legible marks in the Baroque tradition.  Warm amber-umber glaze "
            "(0.58, 0.38, 0.16) unifies in candlelit warmth.  Shadows stay warm umber — "
            "never the cold near-black of Caravaggio's pure tenebrism."
        ),
    ),

    # ── Jean-Honoré Fragonard ──────────────────────────────────────────────────
    # Fragonard was the supreme master of French Rococo painting — rapid, assured,
    # loaded-brush bravura that dazzles with its spontaneity.  His mature style
    # (1760s–1780s) is characterised by:
    #   • Bravura brushwork — a single loaded sweep covers a broad passage; Fragonard
    #     often completed a canvas in a single session, painting alla prima
    #   • Warm, airy palette — rose flesh, cream highlights, honey-amber shadows;
    #     no cold northern light, only the warm glow of French garden afternoons
    #   • Luminous cream-ivory highlights that bloom slightly at their tips into the
    #     surrounding warm midtone — not the silver-cool of Gainsborough or the
    #     Academic porcelain of Bouguereau
    #   • Spontaneous gesture — brushstrokes read as marks; Fragonard celebrated the
    #     stroke itself rather than hiding it behind glazing
    #   • Playful, lyrical subject matter — garden swings, lovers, bathers, reading girls
    # fragonard_bravura_pass() approximates these qualities.
    "jean_honore_fragonard": ArtStyle(
        artist="Jean-Honoré Fragonard",
        movement="French Rococo",
        nationality="French",
        period="1752–1806",
        palette=[
            (0.96, 0.88, 0.78),   # warm cream-white highlight — sunlit, not silver
            (0.88, 0.72, 0.62),   # warm rose flesh mid-tone
            (0.76, 0.58, 0.46),   # warm peach flesh shadow
            (0.55, 0.38, 0.28),   # warm umber deep shadow — no cool blue in shadows
            (0.84, 0.88, 0.68),   # chartreuse garden green — Fragonard's vivid foliage
            (0.64, 0.80, 0.90),   # soft sky blue — warm pastel, not cold
            (0.92, 0.80, 0.54),   # warm golden sunlight — his characteristic afternoon glow
            (0.72, 0.54, 0.70),   # soft lavender-pink drapery — ribbons, silks, petticoats
        ],
        ground_color=(0.90, 0.82, 0.70),    # warm cream-ivory ground — Fragonard toned his
                                            # canvases with a warm, honey-tinted preparation;
                                            # this warm underpaint glows through and unifies
                                            # the whole surface in garden-afternoon warmth
        stroke_size=12,
        wet_blend=0.62,                      # fluid, spontaneous — paint is worked wet-into-
                                            # wet throughout a single sitting; Fragonard rarely
                                            # returned to a dry passage to rework it
        edge_softness=0.52,                  # edges present but softened at stroke tips —
                                            # more spirited than Gainsborough (who dissolved
                                            # edges to mist); Fragonard's strokes have body
                                            # and direction with only the tip feathered
        jitter=0.055,
        glazing=(0.88, 0.78, 0.62),          # warm honey-amber glaze — peach-gold overtone
                                            # that bathes the whole surface in afternoon warmth;
                                            # the opposite of Gainsborough's cool silver glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Bravura alla-prima oil on warm cream-ivory ground.  "
            "A single loaded sweep of a broad, springy hog-bristle brush "
            "covers each passage; marks are confident and largely unretouched.  "
            "Warm rose flesh emerges from a peach-cream midtone ground rather "
            "than the cool Academic imprimatura.  Highlights are creamy warm "
            "(not silver), blooming slightly at their edges into the surrounding "
            "warm half-tone.  Shadows stay warm umber-brown — no cool blue intrudes.  "
            "The whole surface is unified by a warm honey-amber glaze that reads "
            "as afternoon garden light rather than northern studio illumination."
        ),
        famous_works=[
            ("The Swing",                   "1767"),
            ("The Bathers",                 "c. 1765"),
            ("The Progress of Love",        "1771–1772"),
            ("Young Girl Reading",          "c. 1776"),
            ("The Love Letter",             "c. 1770"),
            ("A Young Girl Playing with a Dog", "c. 1770"),
        ],
        inspiration=(
            "Use fragonard_bravura_pass() for the hallmark warm highlight bloom, "
            "rosy flesh-midtone warmth, and honey-amber shadow.  Warm cream-ivory "
            "ground_color (0.90, 0.82, 0.70).  High stroke_size (12) and wet_blend (0.62) "
            "— bravura, spontaneous, loaded-brush marks.  Warm honey glaze "
            "(0.88, 0.78, 0.62) unifies in afternoon warmth.  No cool blue in shadows."
        ),
    ),

    # ── Edvard Munch ──────────────────────────────────────────────────────────
    "munch": ArtStyle(
        artist      = "Edvard Munch",
        movement    = "Nordic Expressionism / Symbolism",
        nationality = "Norwegian",
        period      = "1880–1944",
        palette     = [
            (0.82, 0.28, 0.14),   # cadmium-red anxiety — the blood-red of The Scream sky
            (0.88, 0.62, 0.18),   # saffron-amber — warm undulating atmospheric tone
            (0.18, 0.32, 0.52),   # prussian-cobalt — cold fjord depth, existential shadow
            (0.42, 0.58, 0.38),   # muted verdigris — sickly landscape green, emotional unease
            (0.12, 0.10, 0.08),   # near-black umber — void, formlessness, encroaching dark
            (0.78, 0.72, 0.62),   # pale ivory — isolated flesh tones in the turbulence
            (0.62, 0.22, 0.35),   # crimson-violet — late-evening sky, psychic wound colour
        ],
        ground_color   = (0.18, 0.14, 0.10),   # dark warm umber — Munch primed on dark grounds
        stroke_size    = 10.0,                  # bold, loaded-brush curvilinear marks
        wet_blend      = 0.45,                  # moderate — strokes fuse at tips but stay directional
        edge_softness  = 0.38,                  # figure-ground boundary purposely dissolves
        jitter         = 0.06,                  # organic colour variation per stroke
        glazing        = (0.65, 0.30, 0.10),    # warm crimson-amber unifying glaze
        crackle        = True,                  # Munch's oils have aged surface craquelure
        chromatic_split = False,
        technique=(
            "Edvard Munch painted from psychological states rather than observed nature.  "
            "His defining technical hallmark is the sinuous, undulating brushstroke — long, "
            "curving marks that follow no fixed axis but instead spiral and eddy across the "
            "canvas surface, making the air itself feel charged and unstable.  He applied "
            "oil paint in sweeping directional arcs — the same rhythmic energy appears in "
            "both the figure and the landscape behind them, erasing the boundary between "
            "inner emotional state and outer world.  "
            "Munch worked on dark-toned grounds, usually a warm umber or raw sienna "
            "imprimatura, which unifies his palette in shadow and gives his lit zones their "
            "intensity by simultaneous contrast.  His palette is deliberately visceral: "
            "blood reds, saffron yellows, prussian blues and sickly greens are opposed "
            "without neutral mediation — the colour relationships carry anxiety directly.  "
            "Flesh in Munch's portraits is simplified and mask-like — oval, pale, almost "
            "featureless — while the background swirls with expressionist energy.  The "
            "figure is present but barely anchored; it could dissolve into the landscape "
            "at any moment.  "
            "His glazing practice involves thin, turbid colour washes that build atmospheric "
            "depth rather than form, unifying the whole surface in a sickly warmth reminiscent "
            "of fever light.  Edge_softness is deliberately elevated so that figure contours "
            "begin to merge with the swirling background — psychological dissolution made "
            "visible through paint."
        ),
        famous_works=[
            ("The Scream",                  "1893"),
            ("Madonna",                     "1894–1895"),
            ("The Kiss",                    "1897"),
            ("Anxiety",                     "1894"),
            ("Melancholy",                  "1894–1895"),
            ("The Sick Child",              "1885–1886"),
            ("Vampire",                     "1893–1894"),
            ("Dance of Life",               "1899–1900"),
            ("Self-Portrait with Cigarette","1895"),
            ("Girls on the Bridge",         "1901"),
        ],
        inspiration=(
            "Use munch_anxiety_swirl_pass() for the signature sinuous swirling background — "
            "long curvilinear strokes that spiral across the canvas generating psychological "
            "turbulence.  Dark warm umber ground_color (0.18, 0.14, 0.10) — light zones "
            "must earn their presence against the dark.  stroke_size=10, wet_blend=0.45 — "
            "bold marks that blend at their tips but retain directional energy.  Warm "
            "crimson-amber glaze (0.65, 0.30, 0.10) unifies in fever warmth.  High "
            "edge_softness (0.38) dissolves figure-ground boundary — the psychological "
            "key of the whole approach."
        ),
    ),

    # ── Frans Hals ─────────────────────────────────────────────────────────────
    "frans_hals": ArtStyle(
        artist="Frans Hals",
        movement="Dutch Golden Age",
        nationality="Dutch",
        period="c. 1610–1666",
        palette=[
            (0.92, 0.84, 0.70),   # warm ivory (lit flesh highlights)
            (0.72, 0.52, 0.32),   # raw sienna (mid-tone flesh)
            (0.50, 0.30, 0.18),   # burnt umber (shadow flesh)
            (0.14, 0.12, 0.10),   # ivory black (costume darks)
            (0.96, 0.94, 0.88),   # lead white (direct impasto highlights)
            (0.80, 0.42, 0.30),   # vermillion-sienna (warm blush accents)
            (0.38, 0.34, 0.28),   # warm grey (transitional half-tone)
        ],
        ground_color=(0.78, 0.70, 0.52),   # warm straw-buff priming ground
        stroke_size=8.0,
        wet_blend=0.14,
        edge_softness=0.18,
        jitter=0.048,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Frans Hals's revolutionary technique is built on alla prima bravura "
            "brushwork — each stroke placed directly, wet-on-wet in a single session, "
            "without subsequent reworking or glazing.  His marks are short, angled, and "
            "asymmetric; each stroke follows the local form direction approximately but "
            "deviates at a bold angle, creating the characteristic restless spontaneity "
            "of his surfaces that no other seventeenth-century painter approached.  "
            "Hals's defining innovation is 'broken tone': adjacent strokes of slightly "
            "different values are placed side-by-side rather than blended, so the "
            "flesh passages appear to vibrate with life when viewed from normal reading "
            "distance — the eye performs the tonal synthesis, not the brush.  This "
            "technique anticipates Impressionist divided colour by two centuries.  "
            "His palette is deliberately simple and direct: warm ivory and lead-white "
            "for the lit passages of flesh; raw sienna for mid-tones; burnt umber for "
            "the deepest shadow passages.  Vermillion accents animate lips and warm "
            "cheek passages.  Ivory black provides the decisive costume darks — Hals "
            "often left his black drapery areas as thin, single-layer washes rather "
            "than building them up, creating a thin translucency in the dark areas "
            "that contrasts vividly with the thick impasto highlights above.  "
            "The warm straw-buff ground (ground_color) is the key structural element: "
            "Hals allowed the priming to remain partially visible in the half-tone "
            "passages as the mid-value, relying on it rather than mixing a mid-tone "
            "pigment.  This creates the characteristic warm optical unity of his "
            "canvases without any unifying glaze.  Edges are crisp and directional — "
            "each stroke has a clear start and finish, never fading softly into the "
            "ground the way Leonardo's sfumato does.  The cumulative effect is "
            "spontaneous and psychologically alive, as if caught in the instant of "
            "perception rather than constructed over many sessions."
        ),
        famous_works=[
            ("The Laughing Cavalier",                       "1624"),
            ("Malle Babbe",                                 "c. 1633–1635"),
            ("Regents of the Old Men's Alms House",         "1664"),
            ("Regentesses of the Old Men's Alms House",     "1664"),
            ("Banquet of the Officers of the St George Militia", "1616"),
            ("Portrait of a Man",                           "c. 1660"),
            ("The Merry Drinker",                           "c. 1628–1630"),
        ],
        inspiration=(
            "Use hals_bravura_stroke_pass() for the defining alla prima broken-tone "
            "technique — short, multi-angled strokes with high per-stroke colour "
            "jitter placed directly on the canvas with low wet_blend.  "
            "Warm straw ground_color (0.78, 0.70, 0.52) must remain partially "
            "visible in the half-tone passages — it supplies the warm mid-tone "
            "that Hals relied on rather than mixing it into the paint.  "
            "stroke_size=8.0 is the primary figure mark; reduce to 5.0–6.0 for "
            "the fine face-detail pass.  wet_blend=0.14 keeps strokes crisp and "
            "alla prima — increasing this destroys the bravura character.  "
            "High jitter=0.048 ensures no two adjacent strokes are identical — "
            "the per-stroke colour variation IS the broken-tone technique, not a "
            "flaw.  glazing=None — Hals worked direct, no unifying glaze layers.  "
            "angle_jitter_deg=42 in hals_bravura_stroke_pass() simulates the bold "
            "deviation from the flow field that gives his marks their spontaneous "
            "energy; do not reduce below 35 or the surface becomes too regular."
        ),
    ),

    # ── Salvador Dali ──────────────────────────────────────────────────────────
    "salvador_dali": ArtStyle(
        artist       = "Salvador Dali",
        movement     = "Surrealism",
        nationality  = "Spanish",
        period       = "1929–1989",
        palette      = [
            (0.82, 0.62, 0.25),   # Catalan amber-gold (sunlit sand)
            (0.95, 0.78, 0.42),   # bright ochre (Empordà sunlight)
            (0.12, 0.14, 0.52),   # deep ultramarine (Dali's shadow depths)
            (0.30, 0.55, 0.82),   # cerulean sky blue (Catalan sky)
            (0.68, 0.28, 0.10),   # burnt sienna (sun-baked earth)
            (0.55, 0.35, 0.15),   # raw umber (flesh shadow)
            (0.92, 0.88, 0.75),   # warm ivory (lit flesh, hyper-realist)
            (0.35, 0.18, 0.08),   # deep warm brown (darkest darks)
            (0.72, 0.45, 0.20),   # golden amber (mid-tone)
            (0.18, 0.12, 0.38),   # violet-ultramarine (very deep shadow)
        ],
        ground_color  = (0.88, 0.82, 0.62),   # warm ivory-ochre (Catalan sunlight quality)
        stroke_size   = 4.0,                   # extremely fine, near-invisible marks
        wet_blend     = 0.05,                  # near-dry — hyper-controlled, no bleeding
        edge_softness = 0.08,                  # crisp foreground edges (anti-sfumato)
        jitter        = 0.02,                  # minimal — precise, almost photographic
        glazing       = (0.88, 0.78, 0.42),   # warm amber-gold glaze (Catalan sunlight)
        crackle       = False,
        chromatic_split = False,
        technique     = (
            "Dali employed an extreme hyper-realist technique he called the "
            "'hand-painted dream photograph' — objects rendered with almost obsessive "
            "photographic precision placed within physically impossible contexts.  "
            "Working on a white or ivory-toned ground, he built up extremely thin "
            "oil glazes with very fine brushes, creating a seamless enamel-like "
            "surface that paradoxically makes the impossible contents more convincing: "
            "the more realistic the technique, the more disturbing the subject.  "
            "His palette is dominated by the warm ochre-amber of the Catalonian "
            "landscape — particularly the Cap de Creus coastline near his home in "
            "Cadaqués — set against ultra-deep ultramarine shadows that reach toward "
            "violet at their darkest.  The sky zones are brilliant cerulean, and the "
            "overall tonality transitions sharply from warmly lit golden foreground "
            "to cool deep shadow — a dramatic chiaroscuro applied to dreamlike "
            "scenes rather than the religious subjects of Baroque predecessors.  "
            "His Paranoiac-Critical Method involved inducing paranoid states to "
            "discover hidden double images within compositions — two or more "
            "distinct subjects that occupy the same visual space, each perceptible "
            "depending on the viewer's mental frame.  A subtle chromatic prismatic "
            "aberration — a slight displacement of red and blue channels in "
            "peripheral and background areas — contributes to the dreamlike "
            "out-of-phase quality of his most photographically rendered works, "
            "suggesting the image is seen slightly through the lens of a dreaming "
            "mind rather than waking perception."
        ),
        famous_works  = [
            ("The Persistence of Memory",
             "1931"),
            ("Dream Caused by the Flight of a Bee Around a Pomegranate a Second Before Awakening",
             "1944"),
            ("The Elephants",
             "1948"),
            ("Metamorphosis of Narcissus",
             "1937"),
            ("Swans Reflecting Elephants",
             "1937"),
            ("The Temptation of Saint Anthony",
             "1946"),
            ("The Sacrament of the Last Supper",
             "1955"),
            ("Galatea of the Spheres",
             "1952"),
        ],
        inspiration   = (
            "Use dali_paranoiac_critical_pass() after block_in() and build_form() "
            "to introduce the chromatic prismatic aberration, ultramarine shadow "
            "deepening, and hyper-realist clarity that define Dali's surrealist "
            "canvases.  The pass applies a subtle RGB channel offset to background "
            "regions (chroma_shift=3) — creating the dreamlike out-of-phase quality "
            "of his hyper-realist surfaces — deepens shadows toward deep ultramarine "
            "(his Catalonian light signature), warms sunlit highlights toward Catalan "
            "amber-gold, and applies a controlled unsharp-mask sharpening pass over "
            "figure regions to achieve the 'hand-painted photograph' precision.  "
            "stroke_size=4.0 and wet_blend=0.05 are essential — Dali worked with "
            "extremely fine marks and near-zero wet blending.  The warm "
            "ivory-ochre ground_color must show through in the mid-tone passages.  "
            "Apply glazing=(0.88, 0.78, 0.42) as the final unifying warm amber "
            "layer to achieve the golden Catalan light quality."
        ),
    ),


    # ── Vilhelm Hammershøi ─────────────────────────────────────────────────────
    # ── John Constable ───────────────────────────────────────────────────────
    # Randomly selected artist for this session's naturalistic-landscape inspiration.
    # Constable is the founding voice of English plein air painting — his observation
    # of cloud, light, and the living English countryside shaped both the Barbizon
    # School and French Impressionism.  His technique is the polar opposite of Turner's
    # atmospheric dissolution: Constable's edges are PRESENT; his colour is broken but
    # READ; his sky is studied fact before it is feeling.
    "john_constable": ArtStyle(
        artist="John Constable",
        movement="Romanticism / English Naturalism",
        nationality="British",
        period="c. 1799–1837",
        palette=[
            (0.28, 0.52, 0.22),   # sap green — dense summer foliage (his dominant key)
            (0.48, 0.32, 0.15),   # warm earth brown — ploughed Suffolk field
            (0.55, 0.70, 0.82),   # cool cerulean sky — English overcast blue
            (0.92, 0.90, 0.85),   # silver white — cloud highlight (his famous "snow")
            (0.62, 0.64, 0.68),   # cool grey — storm-cloud underbelly
            (0.72, 0.62, 0.38),   # warm ochre — sunlit path and foreground mud
            (0.22, 0.28, 0.15),   # dark olive shadow — deep tree and hedge shadow
            (0.78, 0.82, 0.88),   # luminous pale sky — horizon glow near waterline
        ],
        ground_color=(0.52, 0.54, 0.42),   # warm greenish-grey — his Dedham Vale ground
        stroke_size=12.0,
        wet_blend=0.42,         # moderate — fresh plein air spontaneity, not over-blended
        edge_softness=0.35,     # moderate — atmospheric softness without Turner-like dissolution
        jitter=0.040,           # animated mark texture — sky and foliage alive
        glazing=(0.68, 0.72, 0.62),     # cool grey-green unifying veil — English damp air
        crackle=False,
        chromatic_split=False,
        technique=(
            "Constable's fundamental innovation was systematic sky observation: he "
            "painted hundreds of cloud studies from life, recording time, date, and "
            "wind direction on the verso, treating meteorology as pictorial fact. "
            "His canvases begin with a warm greenish ground that reads through the "
            "thin paint layers of the middle distance, warming the greens of the "
            "Stour Valley meadows.  Foliage is built from broken, directional dabs "
            "— never blended into a single tone — so the eye reads 'leaves' rather "
            "than 'green mass'.  His most celebrated technical device is the "
            "'Constable snow': tiny dagger-like touches of thick undiluted white "
            "impasto scattered across lit surfaces — water glints, cloud edges, wet "
            "leaf surfaces — that catch actual raking studio light and give the "
            "painting a real luminosity beyond tonal illusion alone.  Shadows are "
            "cool, often greenish; lit passages are warm cream-ochre; the sky is "
            "always the light source and the most carefully painted element.  He "
            "rejected the brown-varnish conventions of the 'Old Masters' as "
            "falsified nature: 'The sound of water escaping from mill-dams, willows, "
            "old rotten planks, slimy posts, and brickwork, I love such things.'  "
            "The technique requires three registers held simultaneously: the large "
            "enveloping sky tone, the middle-distance tonal silhouette, and the "
            "broken close-focus foreground detail."
        ),
        famous_works=[
            ("The Hay Wain",                              "1821"),
            ("Dedham Vale",                               "1802"),
            ("Salisbury Cathedral from the Meadows",      "1831"),
            ("Flatford Mill (Scene on a Navigable River)", "1817"),
            ("Weymouth Bay",                              "1816"),
            ("The White Horse",                           "1819"),
            ("Cloud Study",                               "1822"),
            ("Hampstead Heath with a Rainbow",            "1836"),
        ],
        inspiration=(
            "Use constable_cloud_sky_pass() as the defining stylistic pass — it "
            "builds luminous English skies with warm cream cloud-highlight edges, "
            "cool grey-blue shadow undersides, and Constable's characteristic "
            "'silver sparkle' impasto highlights scattered across lit cloud and "
            "water surfaces.  "
            "The ground_color (0.52, 0.54, 0.42) — warm greenish-grey — should "
            "remain visible in the mid-tone middle-distance passages; Constable's "
            "meadows are the ground showing through thin broken colour.  "
            "wet_blend=0.42 is deliberately moderate: DO NOT raise it; the freshness "
            "of plein air handling depends on NOT over-blending individual strokes.  "
            "jitter=0.040 animates the foliage and sky marks — essential for the "
            "sense of breeze and living light.  "
            "Apply constable_cloud_sky_pass() AFTER build_form() and BEFORE the "
            "final glaze.  Pair with atmospheric_depth_pass() for full recession."
        ),
    ),

    "vilhelm_hammershoi": ArtStyle(
        artist="Vilhelm Hammershøi",
        movement="Symbolism / Danish Intimisme",
        nationality="Danish",
        period="c. 1884–1916",
        palette=[
            (0.82, 0.80, 0.78),   # silver ash (primary tone — lit interior wall)
            (0.68, 0.67, 0.65),   # cool grey (dominant mid-tone — floors and shadow walls)
            (0.52, 0.50, 0.48),   # pewter shadow (darker room recesses)
            (0.35, 0.34, 0.33),   # charcoal grey (furniture silhouettes and deep shadow)
            (0.14, 0.13, 0.14),   # near-black (the deepest tonal anchor — door frames, curtain hems)
            (0.92, 0.91, 0.88),   # pale ivory (direct north window light — the brightest zone)
            (0.72, 0.71, 0.74),   # blue-grey (window glass reflection — slightly cooler than walls)
            (0.45, 0.44, 0.47),   # muted blue-grey shadow (wall in shadow — a ghost of colour)
        ],
        ground_color=(0.68, 0.67, 0.65),   # cool silver-ash priming ground
        stroke_size=4.0,
        wet_blend=0.75,
        edge_softness=0.72,
        jitter=0.008,
        glazing=(0.78, 0.77, 0.74),        # cool grey glaze — near-neutral, R≈G≈B with a whisper of blue
        crackle=False,
        chromatic_split=False,
        technique=(
            "Hammershøi's technique achieves near-total silence through a deliberate "
            "strategy of suppression.  His Copenhagen interiors are constructed from an "
            "extremely limited tonal range — essentially a single grey chord modulated "
            "across the canvas — with almost all colour saturation removed.  What little "
            "colour remains is the ghost of colour: a faint cool bias in the wall tones, "
            "a whisper of warm ivory in the lit window zone, a hint of blue-grey in the "
            "shadowed recesses.  The key decision is the palette: everything is built "
            "from a family of silvers and grey-ivories sharing the same hue family, so "
            "the eye perceives not colour contrast but pure tonal relationship.  "
            "His brushwork is invisible — the surface reads as seamless and continuous "
            "rather than built from marks.  This effect requires extremely high wet "
            "blending: every stroke dissolves immediately into its neighbour, and the "
            "resulting tonal transitions are gradual and smooth to the point of "
            "imperceptibility.  Edge_softness is also very high: even the figure-to-"
            "background boundary is a tone gradient, not a line.  Light enters from the "
            "north window — always from the left in his interiors — as a cool, diffuse "
            "glow that illuminates without casting harsh shadows.  The shadows themselves "
            "receive no warm bounce light; they are simply cooler and darker versions of "
            "the wall tone.  The total effect is of a held breath — the room exists in "
            "a suspension of time, drained of incident, waiting.  Hammershøi's restraint "
            "is itself the subject.  The near-absence of colour, the near-absence of "
            "visible facture, the near-absence of narrative: these absences accumulate "
            "into a profound positive quality — the quality of interior silence made "
            "palpable on canvas."
        ),
        famous_works=[
            ("Dust Motes Dancing in Sunrays",          "1900"),
            ("Interior with Young Woman from Behind",  "c. 1904"),
            ("The Four Rooms",                         "1914"),
            ("Interior, Strandgade 30",                "1901"),
            ("Ida Reading a Letter",                   "1899"),
            ("Interior with Turned Back Figure",       "c. 1913"),
            ("White Doors",                            "1905"),
            ("A Room in the Artist's Home in Strandgade", "1906"),
        ],
        inspiration=(
            "Use hammershoi_grey_silence_pass() as the defining stylistic pass — "
            "it applies systematic desaturation toward grey (leaving only a ghost of "
            "hue at rate 0.82) followed by differential window-light cooling in bright "
            "zones (B lift, R+G damp) and shadow cooling in dark zones.  This tripartite "
            "strategy — desaturate, cool the lights, cool the shadows — reproduces the "
            "characteristic near-monochrome silver-grey of Hammershøi's Copenhagen "
            "interiors without collapsing into pure greyscale.  "
            "Cool silver-ash ground_color (0.68, 0.67, 0.65) must remain visible in "
            "the mid-tone passages — Hammershøi's walls are the ground showing through "
            "thin paint rather than densely opaque coverage.  "
            "wet_blend=0.75 is the highest in the catalog — use it and do not reduce; "
            "the invisibility of brushwork IS the technique.  "
            "edge_softness=0.72 ensures all edges dissolve gradually — no hard "
            "outlines anywhere, not even at the figure boundary.  "
            "glazing=(0.78, 0.77, 0.74) applies the final cool unifying veil — "
            "a near-neutral grey with the faintest blue suggestion.  "
            "Apply hammershoi_grey_silence_pass() with desaturation=0.82 (default) "
            "after build_form() and before the final glaze."
        ),
    ),

    # ── Giovanni Bellini ───────────────────────────────────────────────────────
    "giovanni_bellini": ArtStyle(
        artist="Giovanni Bellini",
        movement="Early Venetian Renaissance",
        nationality="Italian",
        period="1470–1516",
        palette=[
            (0.92, 0.82, 0.65),   # luminous ivory flesh — sacred warmth
            (0.65, 0.50, 0.30),   # warm amber shadow — honey underpaint
            (0.28, 0.20, 0.10),   # deep umber dark — warm, not black
            (0.30, 0.42, 0.68),   # lapis lazuli — Virgin's robe deep blue
            (0.72, 0.60, 0.30),   # warm gold ochre — architectural ground
            (0.52, 0.65, 0.58),   # soft sage-green landscape — hazy recession
            (0.68, 0.28, 0.22),   # soft crimson — drapery warmth
            (0.85, 0.82, 0.75),   # silver-ivory highlight — lit stone and cloth
        ],
        ground_color=(0.62, 0.50, 0.32),    # warm amber-ochre imprimatura
        stroke_size=5,
        wet_blend=0.55,                      # moderate; thin glazes blend in halftones
        edge_softness=0.55,                  # soft but resolved — not sfumato
        jitter=0.018,
        glazing=(0.72, 0.58, 0.28),          # warm honey-amber unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Bellini's method is the first fully matured Venetian oil technique, "
            "adopted from the Flemish glazing system that Antonello da Messina "
            "brought to Venice around 1475.  He works on a warm amber imprimatura "
            "over gessoed panel, establishing the tonal structure in dilute raw "
            "umber, then builds colour through successive thin transparent oil glazes.  "
            "Each glaze layer dries before the next is applied, creating a luminous "
            "optical depth that cannot be achieved by mixing: light passes through "
            "the upper glaze layers and reflects back from the white gesso beneath, "
            "producing the characteristic crystalline inner glow of his Madonnas.  "
            "His flesh tones — ivory lit surfaces over warm umber shadows — have a "
            "quality of translucent warmth, as if skin were backlit from within by "
            "a divine source.  Edges are soft but architecturally resolved; unlike "
            "Leonardo's sfumato they maintain clear form, merely yielding gently at "
            "the periphery.  The sky passages in his altarpieces — cool dove-grey "
            "at the horizon lifting to deeper cerulean at the zenith — introduce the "
            "Venetian tradition of sky-as-atmosphere that Giorgione and Titian would "
            "later extend into full landscape poetry."
        ),
        famous_works=[
            ("San Zaccaria Altarpiece",               "1505"),
            ("Madonna of the Meadow",                  "c. 1500"),
            ("Doge Leonardo Loredan",                  "c. 1501"),
            ("Transfiguration of Christ",              "c. 1480"),
            ("Pietà",                                  "c. 1460"),
            ("St Francis in the Desert",               "c. 1480"),
            ("Madonna with Child Enthroned",           "c. 1488"),
            ("The Feast of the Gods",                  "1514"),
        ],
        inspiration=(
            "Use bellini_sacred_light_pass() after build_form() and sfumato_veil_pass() "
            "to apply the crystalline divine luminosity characteristic of his sacred works.  "
            "The pass applies a warm ivory lift to the upper light zone (simulating the "
            "honey-amber glaze over a warm imprimatura), a cool translucent blue push in the "
            "deep shadow zone (lapis lazuli glaze quality), and a subtle golden halo zone in "
            "the brightest highlight region.  "
            "wet_blend=0.55 balances Flemish glaze precision with Venetian atmospheric warmth.  "
            "edge_softness=0.55 keeps forms legible and architecturally sound — Bellini's forms "
            "are resolved, not dissolved.  "
            "glazing=(0.72, 0.58, 0.28) applies the final warm honey-amber unifying veil that "
            "gives his altarpieces their characteristic golden sacred warmth.  "
            "ground_color=(0.62, 0.50, 0.32) reproduces the warm amber imprimatura — this ground "
            "should remain visible in the thinner passages as a unifying undertone."
        ),
    ),

    # ── Session 53 — new artist: Rogier van der Weyden ────────────────────────
    # Randomly selected artist for session 53's inspiration.
    # Rogier van der Weyden (c. 1399/1400–1464) was the most influential painter
    # in Northern Europe after Jan van Eyck, and in many ways his emotional
    # opposite.  Where Van Eyck described the world with encyclopaedic patience —
    # every texture, every material, every reflection catalogued with devotion —
    # Weyden used oil paint as an instrument of intense psychological drama.
    # His great achievement was the transmission of interior emotional states
    # through purely pictorial means: the angle of a head, the tension of a hand,
    # the precise geometry of shadow across a tear-streaked face.
    #
    # Technically, Weyden's defining quality is the relationship between light and
    # shadow.  Unlike Leonardo's sfumato (which dissolves edges into a continuous
    # atmospheric haze), Weyden's shadows have clean, angular boundaries that
    # describe the geometry of folded cloth with almost architectural precision.
    # A mantle fold is modelled by a single sharp passage from warm lit surface
    # into a deep, cool shadow — the edge is found, not lost.  This gives his
    # drapery the quality of carved stone: the cloth looks as if it could support
    # its own weight.  His flesh is pale — often almost waxen — with cool, slightly
    # blue-tinged shadows.  The emotional charge lives not in warm luminous flesh
    # (Titian, Rubens) but in the precise rendering of grief: swollen eyelids,
    # tautened brows, hands clasped to white-knuckle tension.
    #
    # His palette is rich but controlled: brilliant reds (vermilion, red lake),
    # deep blues (lapis lazuli, azurite), warm gold (Naples yellow, lead white),
    # and the almost black shadows that define his forms.  Unlike Van Eyck's
    # landscapes, Weyden's backgrounds are often gold-leaf or plain architectural
    # settings that concentrate attention on the emotional geometry of the figures.
    "rogier_van_der_weyden": ArtStyle(
        artist="Rogier van der Weyden",
        movement="Early Netherlandish",
        nationality="Flemish",
        period="1430–1464",
        palette=[
            (0.88, 0.76, 0.54),   # warm ivory flesh — pale, slightly cool lit skin
            (0.58, 0.38, 0.28),   # warm umber mid-tone — flesh shadow
            (0.20, 0.14, 0.10),   # near-black shadow — drapery voids
            (0.82, 0.18, 0.14),   # vermilion — rich red mantle, Christ's robe
            (0.18, 0.28, 0.62),   # lapis blue — Virgin's robe, deep background
            (0.88, 0.76, 0.22),   # Naples gold — gilded background, halo
            (0.42, 0.30, 0.48),   # cool violet-shadow — pale flesh in shade
        ],
        ground_color=(0.48, 0.40, 0.28),    # warm ochre-brown oak panel ground
        stroke_size=4,
        wet_blend=0.12,                      # precise, dry marks — Flemish control
        edge_softness=0.18,                  # found edges: angular, geometric shadows
        jitter=0.018,                        # tight colour variation — controlled surface
        glazing=(0.68, 0.52, 0.30),          # warm amber final glaze over oak panel tone
        crackle=True,                        # 15th-century Flemish panel
        chromatic_split=False,
        technique=(
            "Weyden modelled form through angular, geometric shadow passages with "
            "clean found edges — unlike sfumato, each shadow boundary is precise. "
            "Pale flesh rendered with cool undertones; warm umber mid-tones model "
            "the form, then near-black recesses define folds with architectural clarity. "
            "Emotional charge conveyed through exact geometry: brow angles, hand tension. "
            "Vermilion and lapis anchor the composition; gilded or plain dark backgrounds "
            "concentrate all attention on figural expression and drapery geometry."
        ),
        famous_works=[
            ("Descent from the Cross", "c. 1435"),
            ("Beaune Altarpiece (Last Judgement)", "c. 1446–1452"),
            ("Portrait of a Lady", "c. 1460"),
            ("Seven Sacraments Altarpiece", "c. 1445–1450"),
            ("Entombment of Christ", "c. 1450"),
            ("St Luke Drawing the Virgin", "c. 1435–1440"),
        ],
        inspiration=(
            "Use weyden_angular_shadow_pass() to apply Weyden's signature sharp, "
            "geometric shadow boundaries: find each light-to-shadow transition and "
            "harden it into a precise angular edge (rather than blending it away). "
            "Shadow zones receive a slight cool-violet tint (damp, cloth-like shadow) "
            "rather than warm umber.  Flesh highlights push toward cool pale ivory. "
            "Follows well after build_form() and before glaze() — establishes the "
            "geometric clarity before any unifying warm layer is applied."
        ),
    ),

    # ── Session 54 — new artist: Hans Memling ────────────────────────────────
    # Randomly selected artist for session 54's inspiration.
    # Hans Memling (c. 1430/1440–1494) occupies a unique position in Early
    # Netherlandish painting.  He was almost certainly trained in Rogier van
    # der Weyden's Brussels workshop, and inherited that master's command of
    # psychological expression through pictorial geometry.  But where Weyden
    # cultivated drama — angular shadows, grief-stricken figures, the terrible
    # geometry of sorrow — Memling transformed the same technical inheritance
    # into something altogether different: a serene, luminous, jewel-like world
    # in which every surface glows with its own interior light.
    #
    # His defining quality is what might be called crystalline luminosity.
    # Unlike Leonardo's sfumato (edges dissolved into atmospheric smoke) or
    # Weyden's angular found-edge shadows, Memling's light has the quality of
    # polished enamel: bright passages are not just light, they are brilliant,
    # as if the colour itself were luminescent.  This comes from Memling's
    # mastery of oil glazing — he would build up the lit zones with multiple
    # thin transparent layers of lead white and pale ochre, each separately
    # dried, so the final highlight has a depth and translucency that simple
    # opaque painting cannot achieve.
    #
    # The most distinctive quality of his flesh is a blue-green coolness in
    # the shadow transitions — not the warm umber shadows of Italian painting,
    # not Rembrandt's golden pools of shadow, but a slight blue-green
    # undertone that reads as translucent skin with light passing partly
    # through it.  This is the Flemish subsurface quality: the paint surface
    # imitates the way light enters the skin, scatters slightly, and exits
    # cooled.  In Memling's portraits this gives the faces a quality of
    # gentle, living luminosity entirely unlike the warm opaque masks of the
    # Venetians.
    #
    # His palette is rich but kept at a controlled saturation: warm peachy
    # flesh tones, deep vermilion robes, brilliant azure blue, gold accents,
    # and richly detailed verdant backgrounds (often Flemish landscapes or
    # gardens through arched windows).  Nothing is strident; everything is
    # resolved into a jewel-like harmony.
    #
    "hans_memling": ArtStyle(
        artist="Hans Memling",
        movement="Early Netherlandish",
        nationality="Flemish",
        period="1465–1494",
        palette=[
            (0.92, 0.80, 0.62),   # cool pale ivory — lit flesh highlights
            (0.82, 0.62, 0.44),   # warm peachy mid-tone — main flesh area
            (0.52, 0.40, 0.34),   # warm umber shadow — flesh in shadow
            (0.40, 0.50, 0.48),   # blue-green shadow undertone — subsurface quality
            (0.82, 0.20, 0.18),   # brilliant vermilion — the red robes
            (0.22, 0.38, 0.72),   # azure blue — brilliant Flemish blue robes
            (0.82, 0.70, 0.22),   # Naples gold — gilded details, halos
            (0.28, 0.36, 0.28),   # deep Flemish green — landscape background
        ],
        ground_color=(0.72, 0.62, 0.42),    # warm pale ochre oak panel ground
        stroke_size=3,
        wet_blend=0.62,                      # smooth glazed surface — visible tool marks rare
        edge_softness=0.35,                  # precise Flemish edges, not sfumato
        jitter=0.012,                        # very tight colour variation — enamel control
        glazing=(0.80, 0.68, 0.42),          # warm golden glaze — clear, not smoky
        crackle=True,                        # 15th-century Flemish oak panel
        chromatic_split=False,
        technique=(
            "Memling built luminosity through stacked transparent oil glazes on a "
            "chalk-white gesso ground — each layer dried separately so light passes "
            "through, reflects from the ground, and exits with a jewel-like inner glow. "
            "Flesh is warm peachy ivory in the light, with a distinctive blue-green "
            "coolness in the shadow transitions that mimics translucent skin (subsurface "
            "scattering before the concept existed).  Bright highlights approach "
            "enamel-like luminosity — the surface looks polished rather than worked. "
            "Edges are precise and found (Early Netherlandish clarity) but softly blended "
            "without sfumato's atmospheric smoke.  His palette is richly saturated — "
            "brilliant vermilion, azure, and Naples gold — but always kept in jewel-like "
            "harmonic resolution rather than the dissonant tension of the Mannerists."
        ),
        famous_works=[
            ("Diptych of Maarten van Nieuwenhove",      "1487"),
            ("Portrait of a Man with a Roman Coin",     "c. 1480"),
            ("Triptych of Jan Floreins",                "1479"),
            ("Portrait of Maria Portinari",             "c. 1470"),
            ("Virgin and Child with St. Anne",          "c. 1470"),
            ("Last Judgement Triptych",                 "c. 1467–1471"),
            ("Portrait of a Young Man",                 "c. 1480"),
        ],
        inspiration=(
            "Use memling_jewel_light_pass() after build_form() to apply Memling's "
            "signature crystalline luminosity: brightest highlight zones receive a "
            "gentle white-push (cool ivory) making them read as enamel-bright; "
            "mid-shadow transitions receive a subtle blue-green subsurface tint "
            "replicating the Flemish translucent-skin quality.  "
            "ground_color=(0.72, 0.62, 0.42) uses a clear warm ochre — lighter than "
            "the darker grounds of Rembrandt or Caravaggio, allowing the transparent "
            "glaze layers to retain their luminosity rather than being absorbed.  "
            "wet_blend=0.62 produces the smooth, polished surface characteristic of "
            "Flemish oak panel — strokes are blended seamlessly without leaving visible "
            "marks.  edge_softness=0.35 keeps Flemish found-edge precision but avoids "
            "both sfumato's atmospheric loss and Weyden's angular rigour."
        ),
    ),

    # ── Session 56 ─────────────────────────────────────────────────────────────
    "bronzino": ArtStyle(
        artist="Agnolo Bronzino",
        movement="Florentine Mannerism",
        nationality="Italian",
        period="1530–1572",
        palette=[
            (0.94, 0.90, 0.84),   # cool pale ivory — enamel-bright lit flesh
            (0.84, 0.72, 0.58),   # warm ivory — primary mid-tone flesh
            (0.68, 0.58, 0.50),   # cool grey-rose — desaturated shadow flesh
            (0.30, 0.26, 0.34),   # cool blue-grey void — deep shadow (purple-cool)
            (0.18, 0.28, 0.62),   # deep ultramarine — sitter's ceremonial costume
            (0.10, 0.22, 0.14),   # dark Flemish green — court velvet garments
            (0.88, 0.78, 0.28),   # Naples gold — jewellery, gilt accessories
            (0.54, 0.50, 0.58),   # cool silver-violet — neutral background ground
        ],
        ground_color=(0.62, 0.58, 0.56),    # cool neutral pale ground — neither warm ochre nor cold lilac
        stroke_size=4,
        wet_blend=0.18,                      # very low — precise Florentine marks, no wet diffusion
        edge_softness=0.22,                  # Florentine drawing precision: found edges, no sfumato
        jitter=0.008,                        # minimal — court precision demands exact colour consistency
        glazing=(0.88, 0.86, 0.82),          # cool pale ivory glaze — lifts flesh toward enamel luminosity
        crackle=True,                        # aged Florentine panel/canvas painting
        chromatic_split=False,
        technique=(
            "Bronzino achieved his characteristic 'enamel flesh' through extreme surface "
            "refinement: multiple thin, carefully dried oil layers were sanded between "
            "applications so that the final surface had a smooth, almost polished quality — "
            "as if the flesh had been lacquered rather than painted.  This effect is "
            "inseparable from his Mannerist aesthetic: the sitter is cool, contained, and "
            "psychologically inaccessible, as if behind glass.  "
            "Unlike his teacher Pontormo's anxious dissonance, Bronzino's palette is "
            "restrained and aristocratic: cool ivory highlights that approach white, "
            "deeply desaturated shadow tones (no warm amber in the darks), and a "
            "characteristic cool silver-violet neutrality in the deepest shadow passages.  "
            "His light is diffuse and overhead rather than directional — there are "
            "no Rembrandt triangles or Caravaggio spotlights — and the modelling is "
            "minimal: the flesh of a Bronzino portrait reads almost flat in the "
            "midtones, with form suggested by very subtle tonal transitions rather "
            "than bold shadow masses.  "
            "He was court painter to Cosimo I de' Medici, and every brushstroke "
            "communicates the sitter's social distance from the viewer: serene, "
            "untouchable, perfect.  The Mannerist quality here is not Pontormo's "
            "psychological anguish but an aristocratic emotional control that is "
            "its own form of tension."
        ),
        famous_works=[
            ("Portrait of Eleanor of Toledo with Her Son Giovanni", "c. 1545"),
            ("Portrait of a Young Man",                              "c. 1530–1532"),
            ("Venus, Cupid, Folly and Time",                         "c. 1545"),
            ("Portrait of Cosimo I de' Medici",                      "c. 1543"),
            ("Portrait of Laura Battiferri",                          "c. 1555–1560"),
            ("Pygmalion and Galatea",                                  "c. 1529–1530"),
            ("Portrait of Ugolino Martelli",                          "c. 1536–1537"),
        ],
        inspiration=(
            "Use bronzino_enamel_skin_pass() after build_form() to apply Bronzino's "
            "signature enamel-smooth flesh quality: midtone texture is compressed "
            "toward a smooth seamless surface (suppressing the tonal texture that "
            "reads as visible brushwork), the brightest highlights are pushed toward "
            "cool pale ivory (B lifted, R reduced — the opposite of warm gold "
            "highlights), and shadow passages are desaturated to remove warm undertones "
            "(Bronzino's shadows are cool and chromatic, not amber).  "
            "ground_color=(0.62, 0.58, 0.56) uses a cool neutral pale ground — "
            "neither the warm ochre of the High Renaissance nor Pontormo's cold lilac: "
            "a restrained courtly neutrality.  "
            "wet_blend=0.18 keeps marks precise and non-diffused — Florentine "
            "drawing tradition demands clean, controlled edges.  "
            "edge_softness=0.22 preserves the found-edge quality of Florentine "
            "draughtsmanship without any sfumato dissolution.  "
            "glazing=(0.88, 0.86, 0.82) uses a cool pale ivory unifying glaze — "
            "not warm amber (Rembrandt) or deep golden (Leonardo) but a silvery "
            "coolness that lifts the whole surface toward the enamel register."
        ),
    ),

    # ── Session 53 ─────────────────────────────────────────────────────────────
    "tintoretto": ArtStyle(
        artist="Jacopo Tintoretto",
        movement="Venetian Late Renaissance / Mannerism",
        nationality="Italian",
        period="1539–1594",
        palette=[
            (0.90, 0.84, 0.72),   # cool silver-white — lightning highlight
            (0.78, 0.65, 0.46),   # warm mid-flesh — Venetian impasto
            (0.50, 0.38, 0.22),   # brown mid-shadow — raw umber
            (0.08, 0.06, 0.10),   # near-black void — very dark Venetian ground
            (0.22, 0.32, 0.60),   # Prussian blue — deep drapery shadow
            (0.68, 0.18, 0.12),   # Venetian crimson — accent, martyrdom
            (0.38, 0.48, 0.32),   # deep olive green — foliage / background
            (0.82, 0.72, 0.55),   # warm Naples yellow — impasto foreground
        ],
        ground_color=(0.10, 0.07, 0.05),    # near-black Venetian ground — maximum tonal drama
        stroke_size=10,
        wet_blend=0.35,                      # moderate — impasto marks stay visible but wet
        edge_softness=0.42,                  # readable edges, some Venetian atmospheric quality
        jitter=0.048,                        # bold, gestural variation per mark
        glazing=(0.48, 0.42, 0.18),          # deep amber Venetian varnish — rich depth
        crackle=True,
        chromatic_split=False,
        technique=(
            "Tintoretto — dubbed 'Il Furioso' by Aretino for the speed and violence "
            "of his paint application — combined Venetian colourism with a Michelangelesque "
            "command of dramatic anatomy and composition.  Where Titian built luminosity "
            "through patient transparent glazing, Tintoretto slashed silver-white impasto "
            "highlights directly onto near-black grounds: the light reads not as warm gold "
            "but as cool, electric silver, as if a bolt of lightning illuminates the scene "
            "from an oblique upper angle rather than a steady window.  "
            "His dark grounds are among the most extreme in Italian painting — in the "
            "Scuola Grande di San Rocco paintings the canvas absorbs light rather than "
            "reflecting it, with figures materialising from near-absolute darkness.  "
            "Compositionally, Tintoretto rejected the static triangular groupings of the "
            "High Renaissance in favour of violent diagonals: figures recede sharply into "
            "depth or lunge toward the viewer, foreshortened to near-impossibility.  "
            "His brushwork at close range is almost incomprehensible — loose, slashing, "
            "apparently careless marks — yet at viewing distance they resolve into urgent "
            "flesh and drapery with total conviction.  "
            "The silver highlight is his most distinctive single technique: a loaded filbert "
            "brush dragged rapidly across a dark surface, breaking at the edge of a form, "
            "leaving a bright trail that reads simultaneously as a ridge of impasto paint and "
            "a flash of divine light.  This is neither Rembrandt's single warm-amber glowing "
            "triangle nor Leonardo's smooth sfumato transition — it is abrupt, directional, "
            "and luminously cool, as if the form is struck by its own internal electricity."
        ),
        famous_works=[
            ("The Miracle of the Slave",               "1548"),
            ("Saint George and the Dragon",            "c. 1555–1558"),
            ("The Last Supper (San Giorgio Maggiore)", "1592–1594"),
            ("The Origin of the Milky Way",            "c. 1575"),
            ("Paradise (Doge's Palace)",               "1588–1592"),
            ("The Finding of the Body of Saint Mark",  "1562–1566"),
            ("Susanna and the Elders",                 "c. 1555"),
            ("Crucifixion (Scuola Grande di San Rocco)", "1565"),
        ],
        inspiration=(
            "Use tintoretto_dynamic_light_pass() after build_form() to model "
            "Tintoretto's signature silver lightning-highlight quality: extreme contrast "
            "amplification deepens the already-dark ground, while a silver-cool "
            "directional highlight push cuts across form boundaries — lifting the brightest "
            "impasto ridges toward silver-white rather than warm Naples yellow.  "
            "Shadow deepening pulls dark zones toward the near-black ground colour, "
            "widening the tonal gap between light and dark far beyond naturalistic range.  "
            "ground_color=(0.10, 0.07, 0.05) is the darkest in the Venetian catalog — "
            "even darker than Caravaggio's tenebrism (0.06, 0.04, 0.02 RG-biased) — "
            "distinguished by a slight cool-brown rather than pure black, reflecting "
            "Tintoretto's use of a brown-toned lead-white priming rather than Caravaggio's "
            "pure black bitumen ground.  "
            "wet_blend=0.35 keeps marks impasted and semi-wet — paint is worked, not dry, "
            "but not as fluid as Titian.  "
            "glazing=(0.48, 0.42, 0.18) applies a deep amber unifying varnish that "
            "warms the whole surface, uniting the silver highlights and dark shadows "
            "under a common amber tonality — the characteristic depth of old Venetian panels."
        ),
    ),

    # ── Session 52 ─────────────────────────────────────────────────────────────
    "giorgione": ArtStyle(
        artist="Giorgione (Giorgio Barbarelli da Castelfranco)",
        movement="Venetian High Renaissance",
        nationality="Italian",
        period="c. 1477–1510",
        palette=[
            (0.94, 0.88, 0.78),   # pale ivory — primary lit flesh
            (0.82, 0.68, 0.52),   # warm amber-peach — mid-tone flesh
            (0.58, 0.42, 0.28),   # raw sienna — shadow flesh, warmly earthen
            (0.18, 0.26, 0.44),   # deep Prussian blue — sky, storm-blue distance
            (0.28, 0.38, 0.26),   # muted blue-green — deep shadow, distant landscape
            (0.72, 0.52, 0.28),   # warm amber — glowing earth and warm dark tones
            (0.14, 0.10, 0.06),   # near-black brown — deepest shadow void
            (0.86, 0.80, 0.68),   # silver-warm grey — atmospheric haze, fading distance
        ],
        ground_color=(0.68, 0.56, 0.38),
        stroke_size=7,
        wet_blend=0.62,
        edge_softness=0.72,
        jitter=0.022,
        glazing=(0.76, 0.62, 0.32),
        crackle=True,
        chromatic_split=False,
        technique=(
            "Giorgione revolutionised Venetian painting by abandoning the primacy of "
            "drawing and designing compositions entirely through tone and colour — a method "
            "the Venetians called 'pittura di macchia' (painting in patches), later "
            "recognised as 'tonalismo.'  Where his teacher Giovanni Bellini still used "
            "linear underdrawing as structural armature, Giorgione built form directly from "
            "the prepared amber ground upward, placing dark tones first and coaxing light "
            "from the surface by transparent glaze accumulation.  His flesh is organised "
            "not by boundary lines but by tonal pools — areas of luminous midtone that "
            "catch the light and dissolve imperceptibly into either highlight or shadow.  "
            "The result is a form that appears to breathe from within, as if the skin "
            "itself generated light.  "
            "His characteristic edges are never the crisp Flemish edge of van Eyck nor the "
            "disembodied haze of Leonardo's pure sfumato: they occupy a middle position — "
            "soft enough that forms merge into landscape and atmosphere, firm enough that "
            "figure and space remain distinct.  He was the first major Venetian painter to "
            "treat landscape not as a backdrop but as a participant — atmospheric recession, "
            "wet riverbanks, and storm-lit trees share the emotional weight of the figure.  "
            "His palette is consistently warm in the lights and in the deep earth shadows, "
            "with cool blue-green infiltrating the middle-ground distances and occasionally "
            "the figure's peripheral shadows, creating a warm-cool oscillation that binds "
            "figure to landscape.  "
            "Only about six works are universally attributed to him — the mystery of his "
            "brief life (he died of plague at approximately 33) and the numerous works "
            "attributed and deattributed have made him one of the most debated artists in "
            "the Western canon.  Titian, who completed his Sleeping Venus after his death, "
            "absorbed and amplified every technique Giorgione invented."
        ),
        famous_works=[
            ("The Tempest",                   "c. 1508"),
            ("The Three Philosophers",         "c. 1508–09"),
            ("Sleeping Venus",                 "c. 1508–10"),
            ("Castelfranco Madonna",           "c. 1504"),
            ("Portrait of a Young Man",        "c. 1504–06"),
            ("Laura",                          "c. 1506"),
            ("Judith",                         "c. 1504"),
        ],
        inspiration=(
            "Use giorgione_tonal_poetry_pass() after build_form() to apply Giorgione's "
            "signature tonal luminosity — a soft inner glow lifted into the midtone range "
            "that gives flesh its mysterious pooled light.  The pass also applies a warm "
            "amber push to the shadow-midtone transition (Giorgione's earthen warmth in the "
            "deep half-tones) and, when a figure_mask is provided, a cool blue-green "
            "atmospheric bleed at the figure's peripheral edge — the landscape seeping into "
            "the figure's silhouette, one of his most distinctive spatial qualities.  "
            "ground_color=(0.68, 0.56, 0.38) is a warm honey-amber Venetian panel — warmer "
            "and lighter than Tintoretto's near-black, slightly darker and more amber than "
            "Titian's ochre-sienna.  This warm ground shows through in the shadows and "
            "contributes to the characteristic Giorgionesque warmth.  "
            "wet_blend=0.62 supports the tonal building method: colour is worked wet-into-wet "
            "in a liquid, blended manner, with each tone zone softly absorbed into its "
            "neighbour.  "
            "edge_softness=0.72 gives the distinctive soft-but-present Giorgione edge — not "
            "the crisp Flemish line, not the dissolved Leonardo sfumato, but a firm "
            "atmospheric suggestion that keeps forms luminous and readable.  "
            "glazing=(0.76, 0.62, 0.32) applies a deep amber honey unifying varnish in the "
            "final step, warming the entire surface and intensifying the characteristic "
            "tonal depth of the Venetian panel."
        ),
    ),

    # ── Session 59 ─────────────────────────────────────────────────────────────
    "veronese": ArtStyle(
        artist="Paolo Veronese (Paolo Caliari)",
        movement="Venetian Colorism",
        nationality="Italian",
        period="1528–1588",
        palette=[
            (0.94, 0.88, 0.74),   # warm ivory — primary lit flesh
            (0.84, 0.74, 0.58),   # warm peach — mid-tone flesh
            (0.60, 0.48, 0.34),   # warm umber — shadow flesh
            (0.74, 0.80, 0.88),   # cool silver-grey — stone architecture, columns
            (0.78, 0.28, 0.34),   # brilliant rose-crimson — his signature drapery colour
            (0.34, 0.52, 0.44),   # cool grey-green — second drapery, verdant shade
            (0.90, 0.82, 0.38),   # clear warm yellow-gold — brilliant festive fabric
            (0.10, 0.08, 0.08),   # near-black — deepest shadow, concentrated void
        ],
        ground_color=(0.62, 0.54, 0.36),
        stroke_size=9,
        wet_blend=0.48,
        edge_softness=0.40,
        jitter=0.030,
        glazing=(0.68, 0.60, 0.42),
        crackle=True,
        chromatic_split=False,
        technique=(
            "Paolo Veronese stands apart from his great Venetian contemporaries — "
            "Titian and Tintoretto — through a quality of luminous, airborne clarity.  "
            "Where Titian built surface through layered glazes that accumulate deep warmth, "
            "and Tintoretto plunged his canvases into near-black Venetian void, Veronese "
            "bathed his enormous compositions in an even, silvery-clear light that seems to "
            "belong to outdoor festivals and marble-colonnaded loggias.  His palette is the "
            "brightest of the three: rose-crimson, cool grey-green, warm yellow-gold, and "
            "pale ivory flesh — saturated colours placed with architectural confidence rather "
            "than atmospheric dissolution.  "
            "His paint surface has a fresh, decisive quality: colours are often applied in "
            "broad, confident wet-on-wet passages that retain visible direction without the "
            "violent urgency of Tintoretto's slash-and-drag.  Flesh is warm ivory in the lights "
            "with cool silver-grey highlights — unlike the warm gold of Titian — and umber in "
            "the shadows, but shadows remain relatively light-filled; his compositions rarely "
            "deploy the crushing near-black of Caravaggio or Tintoretto.  "
            "His architecture and fabric textures are rendered with a near-decorative richness: "
            "brocades, silks, and damasks are differentiated not through minute Flemish detail "
            "but through broad colour zones and directional light that imply luxurious material "
            "without slavish illusionism.  His handling of space is assured — figures move with "
            "ease through deep architectural settings, yet the surface always retains the "
            "brilliance and freshness of a painter in full command of his material.  "
            "The Inquisition summoned him in 1573 to justify the irreverent content of what "
            "he had titled The Last Supper — Veronese simply renamed it Feast in the House of "
            "Levi and kept painting exactly as he pleased.  The episode crystallises his "
            "temperament: exuberant, untroubled, luminously sensuous."
        ),
        famous_works=[
            ("The Wedding at Cana",                   "1563"),
            ("Feast in the House of Levi",             "1573"),
            ("Mars and Venus United by Love",          "c. 1578"),
            ("The Rape of Europa",                     "1580"),
            ("Triumph of Venice",                      "c. 1582"),
            ("Portrait of a Lady (La Bella Nani)",     "c. 1560"),
            ("Allegory of Love I–IV",                  "c. 1575–80"),
        ],
        inspiration=(
            "Use veronese_luminous_feast_pass() after build_form() to apply Veronese's "
            "signature luminous colour quality: a saturation boost in the mid-tone band that "
            "intensifies brilliant fabric and flesh colours without oversaturating highlights "
            "or muddying shadows.  The pass also applies a cool silver-ivory push to the "
            "brightest lit surfaces (Veronese's cool north-light highlights, distinct from "
            "Titian's warm gold) and a gentle shadow chroma preservation that keeps "
            "Veronese's shadows luminous and colour-filled rather than collapsing toward black.  "
            "ground_color=(0.62, 0.54, 0.36) is a warm ochre-light panel — lighter than "
            "Tintoretto's near-black, not as deeply amber as Giorgione's honey ground; it "
            "gives the painting a sunny, open base that supports the brilliant palette.  "
            "wet_blend=0.48 gives confident, fresh wet-into-wet marks without the tonal "
            "pooling of Giorgione (0.62) — colours blend at edges but retain directional "
            "clarity.  "
            "edge_softness=0.40 produces Veronese's characteristic confident, readable edges: "
            "figures stand clearly in light, not dissolved into atmosphere; architectural "
            "elements read with spatial clarity."
        ),
    ),

    # ── Bartolomé Esteban Murillo ─────────────────────────────────────────────
    "murillo": ArtStyle(
        artist="Bartolomé Esteban Murillo",
        movement="Spanish Baroque",
        nationality="Spanish",
        period="1630–1682",
        palette=[
            (0.92, 0.80, 0.62),   # warm ivory flesh — lit face
            (0.76, 0.58, 0.40),   # golden mid-tone flesh — Murillo's 'pearl' skin
            (0.54, 0.36, 0.22),   # warm shadow umber
            (0.72, 0.52, 0.62),   # rose-violet — characteristic shadow veil
            (0.88, 0.76, 0.52),   # amber-honey — warm ground glow
            (0.34, 0.26, 0.18),   # deep warm brown — rich dark void
            (0.62, 0.70, 0.80),   # cool silver-blue — sky and distant haze
            (0.92, 0.88, 0.82),   # near-white ivory — pearl highlight
        ],
        ground_color=(0.60, 0.48, 0.30),    # warm amber-ochre imprimatura
        stroke_size=6,
        wet_blend=0.65,                      # high blending — vaporous, no harsh boundaries
        edge_softness=0.72,                  # estilo vaporoso: edges dissolve in warm air
        jitter=0.022,
        glazing=(0.68, 0.50, 0.34),          # warm amber-rose unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Murillo's 'estilo vaporoso' (vaporous style) — the defining quality of his "
            "mature work — is a warm, diffused luminosity that makes his figures appear "
            "to glow from within, as if surrounded by a gentle, beatific haze. "
            "Unlike Caravaggio's cold, dramatic chiaroscuro or Zurbarán's razor-edged "
            "Spanish tenebrism, Murillo bathes his subjects — tender Madonnas, ragged "
            "street children, the Immaculate Conception floating on clouds — in a warm "
            "amber-rose light that reads as spiritual comfort made visible. "
            "The characteristic flesh tone is a warm ivory-pearl: luminous in the lights, "
            "transitioning through golden amber midtones into warm umber shadows that "
            "retain colour rather than collapsing to near-black. Edges are soft — not "
            "the sharp contour of Holbein, not the intellectual sfumato of Leonardo — "
            "but a tender dissolution, as if the figure is half-absorbed into the "
            "warm air around it. "
            "His palette is exceptional among Spanish Baroque painters for its warmth "
            "and sweetness: where Velázquez preferred cool silver and Zurbarán "
            "used near-black void, Murillo consistently chose amber, golden ochre, "
            "rose-violet, and honey tones. His shadows have a warm, rose-tinged quality "
            "that prevents the darkness from ever feeling oppressive. "
            "He excelled at depicting the vulnerable — children, beggars, the young "
            "Virgin — and his entire technique seems calibrated to make viewers feel "
            "tenderness rather than awe. The vaporous style was so distinctive that "
            "18th-century collectors called it 'vapory' to distinguish it from the "
            "harder, more theatrical work of his contemporaries. "
            "Technically, the estilo vaporoso is achieved through: (1) a warm "
            "amber-ochre ground that pre-warms every subsequent colour; (2) extensive "
            "wet-on-wet blending so that boundaries dissolve rather than assert; "
            "(3) multiple thin warm glazes over the completed work that unify all tones "
            "into a golden-amber harmony; (4) the deliberate avoidance of harsh shadow "
            "edges — shadow transitions are gradual and warm, not abrupt and cold."
        ),
        famous_works=[
            ("Immaculate Conception of Los Venerables",  "c. 1678"),
            ("The Young Beggar",                          "c. 1645–50"),
            ("Two Women at a Window",                     "c. 1655–60"),
            ("The Return of the Prodigal Son",            "c. 1667–70"),
            ("Virgin and Child",                          "c. 1655–60"),
            ("Boys Eating Grapes and a Melon",            "c. 1645–46"),
            ("St Thomas of Villanueva Distributing Alms", "c. 1665"),
            ("Adoration of the Magi",                     "1655–60"),
        ],
        inspiration=(
            "Use murillo_vapor_pass() after build_form() and before glaze() to apply "
            "Murillo's defining 'estilo vaporoso': a warm luminous bloom that radiates "
            "outward from highlighted areas, warm amber-rose shadow injection, and a "
            "gentle ivory pearl push on the brightest lit pixels. "
            "ground_color=(0.60, 0.48, 0.30) — warm amber-ochre imprimatura pre-warms "
            "every colour layer; Murillo's characteristic golden underpinning distinguishes "
            "his flesh from the cooler grounds of Velázquez and Zurbarán. "
            "wet_blend=0.65 produces Murillo's characteristic soft, vaporous boundaries: "
            "not Leonardesque sfumato (edges that vanish entirely) but a tender dissolution "
            "where form transitions are warm and gradual. "
            "glazing=(0.68, 0.50, 0.34) — warm amber-rose final glaze that shifts all "
            "tones toward Murillo's characteristic golden-warm harmony."
        ),
    ),

    "tiepolo": ArtStyle(
        artist="Giovanni Battista Tiepolo",
        movement="Venetian Rococo",
        nationality="Italian",
        period="1696–1770",
        palette=[
            (0.42, 0.68, 0.88),   # brilliant azure — the signature Tiepolo sky
            (0.98, 0.92, 0.72),   # Naples yellow — his defining warm light tone
            (0.96, 0.94, 0.90),   # pearl white — dazzling celestial highlight
            (0.88, 0.46, 0.34),   # coral vermilion — warm drapery accent
            (0.82, 0.70, 0.48),   # warm ochre — flesh mid-tone, imprimatura tone
            (0.72, 0.80, 0.90),   # pale sky blue — aerial distance
            (0.78, 0.62, 0.74),   # soft lavender-violet — drapery shadow
            (0.36, 0.26, 0.18),   # warm dark umber — deep shadow accent
        ],
        ground_color=(0.90, 0.86, 0.76),
        stroke_size=9,
        wet_blend=0.68,
        edge_softness=0.52,
        jitter=0.032,
        glazing=(0.94, 0.88, 0.72),
        crackle=True,
        chromatic_split=False,
        technique=(
            "Giovanni Battista Tiepolo was the supreme master of the Venetian Rococo "
            "and the last great fresco painter of the Western tradition.  Working across "
            "ceilings, altarpieces, and cabinet paintings from Venice to Würzburg to "
            "Madrid, he perfected a system of aerial luminosity that no subsequent painter "
            "has matched: figures seem to inhabit real sky, to float in brilliant "
            "atmosphere lit from directly overhead by an invisible celestial source.  "
            "His palette is the defining feature of the Venetian Rococo.  Where Titian "
            "built richness through warm amber glazing and Tintoretto through violent "
            "contrast, Tiepolo worked in a higher key: brilliant azure, Naples yellow, "
            "pearl white, coral vermilion — colours that appear to absorb and re-emit "
            "light rather than merely reflect it.  His skies are not blue smears but "
            "luminous atmospheric phenomena, differentiated through subtle gradations "
            "of azure, pale cerulean, and near-white zenith that give them a "
            "convincing three-dimensional depth.  "
            "The technique behind this aerial quality is rooted in the Venetian tradition "
            "of painting into a wet ground.  Tiepolo toned his plaster or canvas with "
            "a warm pale cream — not the dark grounds of Rembrandt or Caravaggio — so "
            "that every subsequent colour note reads lighter and more luminous than it "
            "would on a neutral or dark preparation.  Flesh tones are modelled from a "
            "warm Naples yellow base through coral rose midtones to brilliant pearl "
            "white highlights, with deep warm umber only in the most recessed shadows.  "
            "The characteristic effect — visible especially in the Würzburg Residenz "
            "ceiling (1750–53) and the Villa Valmarana 'Foresteria' frescoes (1757) — "
            "is a flesh that seems self-luminous: as if the figures have absorbed the "
            "celestial light and radiate it from within.  "
            "His brushwork is both confident and refined: large decisive strokes lay in "
            "the broad colour zones (the wet-into-wet Venetian tradition), while final "
            "touches of pure Naples yellow and pearl white, applied almost dry with a "
            "loaded fine brush, create the dazzling highlights on drapery folds, "
            "metallic armour, and upturned faces.  The transition from highlight to "
            "deep shadow is rapid by Renaissance standards — Tiepolo is a Rococo "
            "master and embraces theatrical contrast — but always mediated by a "
            "characteristic warm coral-rose midtone that prevents the drama from "
            "reading as Baroque gloom.  "
            "Technically the celestial-light effect depends on three decisions: "
            "(1) a pale warm imprimatura that pre-luminifies every subsequent layer; "
            "(2) overhead light direction — almost vertical — so that the tops of "
            "forms are maximally lit and the undersides recede into warm shadow "
            "(the opposite of candlelight or single-window studio lighting); "
            "(3) the restraint to leave the sky itself nearly unpainted — the palest "
            "azure washes over bare cream ground — so that the figures, despite "
            "their brilliant colours, read as darker than the air that surrounds them."
        ),
        famous_works=[
            ("Würzburg Residenz ceiling frescoes",          "1750–53"),
            ("Villa Valmarana — Foresteria frescoes",       "1757"),
            ("The Banquet of Cleopatra",                    "1743–44"),
            ("The Triumph of Zephyr and Flora",             "c. 1734–35"),
            ("Apotheosis of the Pisani Family",             "c. 1761–62"),
            ("Allegory of the Planets and Continents",     "1752"),
            ("The Investiture of Bishop Harold",            "1751–52"),
            ("St Thecla Liberating Este from the Plague",  "1759"),
        ],
        inspiration=(
            "Use tiepolo_celestial_light_pass() after build_form() and before glaze() "
            "to apply Tiepolo's defining overhead-celestial luminosity: a brilliant "
            "pearl-white bloom from above, an azure push into the upper canvas zone, "
            "and a warm Naples-yellow glow into the lit tops of figure forms.  "
            "ground_color=(0.90, 0.86, 0.76) is the pale warm cream imprimatura that "
            "pre-luminifies every colour layer — the foundation of the celestial light "
            "effect.  Without this warm pale ground the characteristic aerial luminosity "
            "cannot be achieved: every colour note reads lighter, more aerial, more "
            "self-luminous than it would on a neutral or dark preparation.  "
            "wet_blend=0.68 honours the Venetian wet-into-wet tradition: broad colour "
            "zones are worked into each other while the ground is still moist, producing "
            "the soft warm-to-cool transitions that give Tiepolo's flesh its three- "
            "dimensional roundness without sfumato-level dissolution.  "
            "glazing=(0.94, 0.88, 0.72) — warm Naples-pearl final glaze that shifts "
            "all tones toward the characteristic Tiepolo golden-white aerial harmony "
            "without the amber weight of Rembrandt's amber glazing."
        ),
    ),

    "zurbaran": ArtStyle(
        artist="Francisco de Zurbarán",
        movement="Spanish Baroque Tenebrism",
        nationality="Spanish",
        period="1598–1664",
        palette=[
            (0.95, 0.95, 0.93),   # pure cold white — the luminous monk's habit
            (0.82, 0.80, 0.78),   # warm-grey upper mid-light on white drapery
            (0.60, 0.60, 0.65),   # cool blue-grey — shadow on white fabric
            (0.72, 0.56, 0.32),   # warm ochre — flesh in clear northern light
            (0.42, 0.28, 0.18),   # dark burnt sienna — flesh receding into shadow
            (0.30, 0.22, 0.14),   # raw umber — deep mid-shadow on drapery folds
            (0.12, 0.09, 0.07),   # near-black cold void — the dominant dark
            (0.06, 0.04, 0.04),   # absolute black void — deepest recession
        ],
        ground_color=(0.08, 0.06, 0.05),
        stroke_size=5,
        wet_blend=0.18,
        edge_softness=0.22,
        jitter=0.010,
        glazing=None,
        crackle=True,
        chromatic_split=False,
        technique=(
            "Zurbarán is the supreme painter of austere devotion — known as 'the painter "
            "of monks' and 'the Spanish Caravaggio', though his light is contemplative "
            "rather than theatrical.  Where Caravaggio uses darkness as drama, Zurbarán "
            "uses it as silence.  His white habits are among the most astonishing passages "
            "in Western painting: rendered with cool, almost sculptural clarity, the fabric "
            "modelled purely in blue-grey shadows and near-pure cold-white highlights that "
            "read as marble or alabaster rather than cloth.  "
            "His tonal range is maximally polarised: forms leap from near-black ground "
            "directly to brilliant white with minimal midtone transition — a binary "
            "devotional clarity that has no warmth, no atmospheric haze, no sfumato.  "
            "Unlike Murillo (his contemporary), Zurbarán's shadows offer no warmth: "
            "the darkness is cold, absent, void.  Light does not glow or bloom — it "
            "simply falls, sharp and singular, as if through a high monastery window.  "
            "His still lifes (pottery jars, lambs, citrus) carry the same austere "
            "holiness as his saints — objects rendered with an almost sacred specificity.  "
            "He was the preferred painter of the Sevillian monasteries and the Spanish "
            "colonial trade, and his work shaped the visual identity of Counter-Reformation "
            "piety across two continents."
        ),
        famous_works=[
            ("Saint Francis in Meditation",            "c. 1635–40"),
            ("The Apotheosis of Saint Thomas Aquinas", "1631"),
            ("Still Life with Pottery Jars",            "c. 1636"),
            ("Christ on the Cross",                     "1627"),
            ("Agnus Dei (Lamb of God)",                 "c. 1635–40"),
            ("Saint Serapion",                          "1628"),
            ("The Battle of Christians and Moors at El Sotillo", "1638"),
            ("The Supper at Emmaus",                    "c. 1620"),
        ],
        inspiration=(
            "Use zurbaran_stark_devotion_pass() after build_form() and before glaze() "
            "to apply Zurbarán's defining tonal polarity: cold void deepening in the "
            "darkest shadows (desaturating and cooling toward near-black), brilliant "
            "cool-white crystalline push in the highest highlights (especially white "
            "drapery with blue-grey shadow modelling), and midtone compression that "
            "creates the stark binary contrast of his devotional work.  "
            "ground_color=(0.08, 0.06, 0.05) — the near-black imprimatura is essential: "
            "Zurbarán's forms emerge FROM the void, not against a warm ground.  "
            "wet_blend=0.18 — crisp, controlled, almost sculptural mark-making; "
            "the polar opposite of Murillo's vaporous wet-on-wet blending.  "
            "edge_softness=0.22 — hard, precise edges against the black ground define "
            "the devotional clarity: objects and figures in Zurbarán are absolutely present "
            "or absolutely absent, with no atmospheric ambiguity between them.  "
            "glazing=(0.68, 0.62, 0.50) at very low opacity (0.04) — a barely perceptible "
            "unifying amber applied only to warm the flesh passages; the white drapery "
            "must remain cold and pure."
        ),
    ),

    # ── Jean-Baptiste-Camille Corot ───────────────────────────────────────────
    "corot": ArtStyle(
        artist="Jean-Baptiste-Camille Corot",
        movement="Barbizon School / Proto-Impressionism",
        nationality="French",
        period="1820–1875",
        palette=[
            (0.72, 0.75, 0.62),   # silvery sage green — foliage in diffuse light
            (0.62, 0.66, 0.58),   # muted grey-green — mid-distance tree mass
            (0.80, 0.80, 0.74),   # pale silver-grey — sky and bright foliage highlight
            (0.52, 0.55, 0.50),   # cool grey-green — shadow zone under trees
            (0.70, 0.68, 0.55),   # warm ochre — sun-touched open ground
            (0.42, 0.45, 0.52),   # cool blue-grey — atmospheric distance
            (0.88, 0.86, 0.78),   # pearl white — brightest sky or water reflection
            (0.32, 0.34, 0.28),   # dark olive — deepest shadow in foliage mass
        ],
        ground_color=(0.62, 0.60, 0.50),    # warm ochre-grey imprimatura — Corot often
                                             # used a mid-toned warm ground for landscapes
        stroke_size=8,
        wet_blend=0.72,                      # high — blended transitions for atmospheric softness
        edge_softness=0.78,                  # very high — the silvery veil dissolves boundaries
        jitter=0.022,
        glazing=(0.76, 0.78, 0.70),          # pale cool silver glaze — the unifying veil
        crackle=True,
        chromatic_split=False,
        technique=(
            "Corot's signature is the 'silver veil' — an atmospheric dissolution "
            "of form and colour that anticipates Impressionism by two decades.  "
            "Working outdoors in the Barbizon forest, the Roman Campagna, and at "
            "Ville-d'Avray, he developed a systematic approach to atmospheric depth: "
            "forms in the distance lose not only detail but colour identity, shifting "
            "toward a unified cool silver-grey that reads as light itself suspended "
            "in air.  His greens are never the saturated greens of Constable or "
            "Gainsborough — they are muted, slightly grey, as if seen through a "
            "morning mist.  His skies and his foliage share the same tonal "
            "register — this deliberate tonal compression is what gives his "
            "landscapes their lyrical, dreamlike quality.  "
            "Unlike the Impressionists who followed him, Corot retained a "
            "structural firmness in his tree trunks and architecture — the "
            "dissolved quality is in the atmosphere, not in the drawing.  "
            "His brushwork in the foliage masses uses stippling and dabbing "
            "motions that create vibrating surface texture without the colour "
            "divisionism of Seurat — the surface shimmers but the palette "
            "remains tonal.  He was famous among younger painters (Pissarro, "
            "Morisot, Sisley all considered him a father figure) for his "
            "absolute control of tonal values — his ability to render the exact "
            "luminosity of open air without resorting to high key colour."
        ),
        famous_works=[
            ("The Bridge at Narni",                       "1826"),
            ("Souvenir de Mortefontaine",                 "1864"),
            ("The Church of Marissel",                    "1866"),
            ("Ville-d'Avray",                             "c. 1867"),
            ("Dance of the Nymphs",                       "c. 1850–1860"),
            ("Agostina",                                  "1866"),
            ("A Woman Reading",                           "c. 1869"),
        ],
        inspiration=(
            "Use corot_silver_veil_pass() after build_form() to apply the "
            "characteristic silvery atmospheric desaturation: all colours are "
            "pulled gently toward a cool silver-grey — saturated greens lose "
            "their assertiveness, warm tones are cooled by fractional amounts, "
            "and the whole canvas acquires the luminous tonal unity of open-air "
            "diffuse light.  "
            "ground_color=(0.62, 0.60, 0.50) — a warm ochre-grey imprimatura "
            "that reads as neither warm nor cool under the final pale glaze.  "
            "edge_softness=0.78 — the silver veil softens foliage boundaries "
            "against sky; tree edges are feathered, not crisp.  "
            "glazing=(0.76, 0.78, 0.70) at low opacity (0.05–0.08) — the "
            "unifying pale silver glaze applied at the very end to merge all "
            "tones into a single luminous atmosphere; this is the essential "
            "final operation that achieves the characteristic Corot unity.  "
            "Pairs naturally with atmospheric_depth_pass() for the landscape "
            "distance recession, and north_light_diffusion_pass() for the "
            "soft, directionless light quality of his studio figure paintings."
        ),
    ),

    # ── Session 62 addition: Parmigianino ────────────────────────────────────
    "parmigianino": ArtStyle(
        artist="Parmigianino (Girolamo Francesco Maria Mazzola)",
        movement="Parma / Florentine Mannerism",
        nationality="Italian",
        period="1503–1540",
        palette=[
            (0.96, 0.93, 0.86),   # cool porcelain ivory — the defining skin tone
            (0.88, 0.84, 0.79),   # warm pale buff — upper midlight on face
            (0.72, 0.68, 0.73),   # silvery cool grey — shadow on face / neck
            (0.82, 0.70, 0.75),   # dusty rose-mauve — drapery midlight
            (0.67, 0.62, 0.78),   # lavender-silver — cool shadow on pale drapery
            (0.48, 0.44, 0.54),   # violet-grey — deep drapery shadow
            (0.36, 0.30, 0.24),   # warm dark umber — minimal deep shadow anchor
            (0.12, 0.10, 0.16),   # blue-violet black — void shadow
        ],
        ground_color=(0.68, 0.65, 0.60),
        stroke_size=4,
        wet_blend=0.32,
        edge_softness=0.62,
        jitter=0.018,
        glazing=(0.88, 0.88, 0.90),
        crackle=True,
        chromatic_split=False,
        technique=(
            "Parmigianino — baptised Girolamo Francesco Maria Mazzola, born in Parma "
            "1503 — is the supreme poet of Mannerist elegance.  Where his Parma "
            "predecessor Correggio achieved softness through warm atmospheric blending, "
            "Parmigianino achieved it through refinement: an extreme attenuation of "
            "form, a near-total suppression of tactile texture in the skin, and a "
            "colour harmony that is simultaneously the palest and the most unusual "
            "in the Italian tradition.  "
            "His figures are famously elongated — the Madonna in 'Madonna with the "
            "Long Neck' (c.1535, Uffizi) has a neck that no anatomist could account "
            "for, fingers that extend beyond natural proportion, and a torso that "
            "reads as architectural.  Yet the distortion never reads as grotesque: "
            "it reads as ideal.  The elongation is a claim about what beauty IS, "
            "not a mistake about what bodies look like.  "
            "His skin is porcelain-cool: the usual Venetian warm amber subsurface "
            "glow is entirely absent; instead flesh reads as translucent ivory with "
            "cool silvery grey shadows.  This is partly a Parma stylistic preference "
            "and partly Parmigianino's own temperament — his figures exist in an "
            "atmosphere of cool, perfectly composed detachment.  "
            "His 'Self-Portrait in a Convex Mirror' (c.1524, Kunsthistorisches Museum) "
            "— painted to impress Pope Clement VII, on a convex wooden panel that "
            "reproduced the exact distortion of a circular mirror — is one of the "
            "most technically astonishing objects of the Italian Renaissance: the "
            "foreground hand is enormous, the background room curves impossibly, and "
            "the face at centre is small, perfectly smooth, and absolutely calm.  "
            "Drapery in his work moves with an autonomous grace: it swirls in arcs "
            "that serve the composition rather than anatomy.  The colours are dusty "
            "rose, lavender, silver, and a muted coral — the palette is almost "
            "pastel by the standards of the period.  "
            "He died at 37 — reportedly having become so obsessed with alchemy that "
            "he neglected his appearance and work — but his influence on the Fontainebleau "
            "School and Northern European Mannerism was vast."
        ),
        famous_works=[
            ("Madonna with the Long Neck",               "c. 1534–40"),
            ("Self-Portrait in a Convex Mirror",         "c. 1523–24"),
            ("Schiava Turca (The Turkish Slave)",         "c. 1530–32"),
            ("The Vision of Saint Jerome",               "1526–27"),
            ("Cupid Carving His Bow",                     "c. 1533–35"),
            ("Portrait of a Young Woman (Antea)",        "c. 1531–35"),
            ("Portrait of Galeazzo Sanvitale",           "1524"),
            ("The Virgin of the Rose",                   "c. 1529–30"),
        ],
        inspiration=(
            "Use parmigianino_serpentine_elegance_pass() after build_form() and before "
            "glaze() to apply Parmigianino's defining cool porcelain refinement: "
            "midlight skin zones shifted toward translucent cool ivory (suppressing "
            "the warm amber subsurface glow found in Venetian and Flemish portraits), "
            "shadow zones pushed toward silvery lavender-grey (his characteristic cool "
            "shadow colour, the polar opposite of Rembrandt's warm umber shadow), and "
            "highlight zones polished to a cool silver-white (not warm gold).  "
            "ground_color=(0.68, 0.65, 0.60) — a neutral warm-grey Parma ground that "
            "neither pre-warms (as warm ochre would) nor pre-cools (as a blue-grey "
            "would); it is deliberately mid-temperature so that the cool ivory palette "
            "reads as elegant refinement rather than coldness.  "
            "edge_softness=0.62 — Parmigianino's edges are softer than Florentine "
            "line-dominant painting but crisper than Leonardo's sfumato; his forms "
            "are recognisable at a glance but their transitions are imperceptible.  "
            "stroke_size=4 — fine, controlled marks throughout; no impasto.  "
            "glazing=(0.88, 0.88, 0.90) — a very pale, slightly cool silver-ivory unifying "
            "glaze that ties all tones together and gives the characteristic translucent "
            "'enamel' surface quality of his panel paintings; the slight B>R bias keeps "
            "the overall harmony cool rather than amber."
        ),
    ),

    "canaletto": ArtStyle(
        artist="Giovanni Antonio Canal (Canaletto)",
        movement="Venetian Vedutismo",
        nationality="Italian",
        period="1697–1768",
        palette=[
            (0.62, 0.78, 0.90),   # cerulean sky — the luminous Venetian sky, pure and clear
            (0.82, 0.72, 0.48),   # warm honey-stone — Venetian palazzo masonry in direct sun
            (0.52, 0.62, 0.70),   # cool canal silver — Canal Grande water reflections
            (0.90, 0.86, 0.68),   # pale sunlit plaster — sunlit façades, bleached white near zenith
            (0.28, 0.24, 0.18),   # dark warm umber — deep shadow under arcades, gondola hulls
            (0.68, 0.52, 0.30),   # warm sienna — terracotta rooftiles, sunlit stonework shadow face
            (0.76, 0.82, 0.86),   # silver-grey haze — atmospheric distance, receding architecture
            (0.14, 0.18, 0.28),   # deep indigo shadow — coolest canal shadow, under bridges
        ],
        ground_color=(0.72, 0.68, 0.52),   # warm pale ochre: Venetian afternoon light
        stroke_size=5,
        wet_blend=0.20,
        edge_softness=0.18,
        jitter=0.018,
        glazing=(0.88, 0.84, 0.64),        # warm pale ivory unifying glaze — afternoon sun
        crackle=True,
        chromatic_split=False,
        technique=(
            "Canaletto perfected the veduta — the topographically precise urban view — "
            "to a degree unequalled before or since.  His Venice is not the Venice of "
            "atmospheric impression (Turner's approach, a century later) but of lucid, "
            "crystalline fact: every stone course counted, every arcade measured, every "
            "gondola prow anatomised with the care of an architectural draughtsman.  "
            "He was trained as a theatrical scenographer, and that training is inseparable "
            "from his mature style: his compositions are staged with the precision of a "
            "set designer — viewpoints chosen for maximum spatial drama, foreground shadows "
            "framing a sunlit distance, the eye led back through layers of architecture into "
            "a pale, luminous sky.  "
            "His sky is one of the most immediately recognisable qualities of his work: "
            "a clear Venetian cerulean, often with small fleecy clouds, lit from above with "
            "an absolute directness.  Where Claude Lorrain's sky dissolves at the horizon "
            "into warm haze, Canaletto's remains a pure, saturated blue almost to the roofline.  "
            "The light in his paintings is high and direct — southern summer noon or early "
            "afternoon — casting short, crisp shadows and creating the extreme value contrast "
            "between sunlit stone and shadow arcade that is the structural skeleton of his "
            "compositions.  "
            "He used a camera obscura as a compositional aid, and the slightly wide-angle, "
            "slightly exaggerated perspective of his views reflects this: the Grand Canal "
            "widens, the Piazza San Marco deepens, everything is slightly more than real, "
            "more legible, more theatrical.  "
            "His palette is narrow but brilliantly deployed: warm honey-stone for sunlit "
            "masonry, cool silver for canal water, deep warm umber for shadow, and the "
            "ever-present cerulean sky.  The figures that populate his vedute are tiny, "
            "summary, gestural — not portraits but staffage, colour notes that confirm "
            "scale and animate the scene without competing with the architecture."
        ),
        famous_works=[
            ("The Grand Canal from Santa Croce to San Simeone Piccolo",  "c. 1738"),
            ("The Stonemason's Yard",                                     "c. 1725–30"),
            ("View of the Bacino di San Marco",                           "c. 1735"),
            ("Venice: The Piazza San Marco",                              "c. 1720s"),
            ("A Regatta on the Grand Canal",                              "c. 1735"),
            ("The Grand Canal from Palazzo Balbi",                        "c. 1724"),
            ("Eton College",                                              "1754"),
            ("The Thames and the City of London from Richmond House",     "1746"),
        ],
        inspiration=(
            "Use canaletto_luminous_veduta_pass() after build_form() and before glaze() "
            "to apply Canaletto's defining atmospheric clarity: the warm honey-stone "
            "sunlit façades are pushed toward bright warm ochre, canal-water zones are "
            "pulled toward cool silver-blue, and the sky zone receives a saturated cerulean "
            "lift — the three chromatic pillars of the Venetian veduta.  "
            "Optionally follow with old_master_varnish_pass() at very low opacity (0.15–0.20) "
            "to add the aged amber patina of a Canaletto panel viewed in a museum collection: "
            "this subtly warms the whole image and adds the slightly honeyed quality of "
            "three centuries of varnish oxidation without obscuring the architectural clarity.  "
            "ground_color=(0.72, 0.68, 0.52) — a warm pale ochre ground that pre-establishes "
            "the afternoon sunlight reading before any paint is applied; Canaletto's warm "
            "Venetian light is the dominant key.  "
            "stroke_size=5 — small and precise; Canaletto's fine architectural detail "
            "demands controlled marks, not broad gestural ones.  "
            "wet_blend=0.20, edge_softness=0.18 — his edges are crisp by the standards of "
            "oil painting; the hard light of the Venetian noon makes shadows sharp-edged, "
            "and his architectural precision requires legible stone courses and window "
            "openings, not sfumato dissolution.  "
            "glazing=(0.88, 0.84, 0.64) — a very pale warm ivory unifying glaze that gives "
            "the characteristic golden-afternoon quality of his finished works."
        ),
    ),

    # ── Élisabeth Louise Vigée Le Brun ────────────────────────────────────────
    # Élisabeth Louise Vigée Le Brun (1755–1842) was the most celebrated
    # portraitist of the ancien régime — court painter to Marie Antoinette,
    # sought after across Europe by royalty, nobility, and intelligentsia.
    # Her portraits are immediately recognisable by a quality difficult to name
    # precisely but instantly felt: the sitter appears to glow from within.
    # This is not the smoky inner light of Leonardo, nor the self-illuminating
    # warm amber glow of Raphael, nor even the pure pearl radiance of Bouguereau.
    # It is something more specifically feminine and 18th-century: a warm
    # rose-ivory iridescence — the colour of good skin in candlelight, or of
    # a complexion viewed through very fine muslin.
    #
    # The technical secret lies in her midtone handling.  Where academic
    # painters built flesh from dark to light (shadow → midtone → highlight),
    # Vigée Le Brun worked from the *midtone outward* — her typical portrait
    # session began with a warm, rosy middle tone laid in across the whole face,
    # and then darkened toward shadow and lightened toward highlight *from that
    # pink centre*.  The result is that even her deepest shadows retain a
    # rose-warm quality — they are not grey, not cold violet, but inhabited,
    # warm, living.  And her highlights, instead of pure white, reach toward a
    # cool pearl — the slight blue-cool shimmer of nacre, not the warm ivory of
    # a glazed Raphael.
    #
    # This combination — warm rose body with cool pearl highlights and warm
    # rose-violet shadows — is unique in 18th-century painting.  It gives her
    # female sitters in particular an air of radiant vitality that no
    # contemporary could quite match.  Her famous self-portraits (the one
    # with the straw hat, 1782; the one with her daughter, 1786) are the
    # most complete demonstrations of this quality.
    "vigee_le_brun": ArtStyle(
        artist="Élisabeth Louise Vigée Le Brun",
        movement="French Neoclassical / Late Rococo Portraiture",
        nationality="French",
        period="1778–1842",
        palette=[
            (0.96, 0.88, 0.76),   # luminous warm-ivory pearl — the lit highlight
            (0.90, 0.74, 0.60),   # warm rose-ivory midflesh — her signature skin tone
            (0.80, 0.60, 0.46),   # golden pink midtone — deeper lit flesh
            (0.60, 0.42, 0.30),   # warm raw umber shadow — transparent, rose-warm
            (0.38, 0.28, 0.42),   # cool violet-rose deep shadow — the coldest passage
            (0.78, 0.32, 0.30),   # deep vermillion — drapery accent, rose-red fabric
            (0.20, 0.22, 0.44),   # deep French ultramarine — dark portrait backdrop
            (0.94, 0.86, 0.80),   # pearl near-highlight — the nacre shimmer
        ],
        ground_color=(0.62, 0.50, 0.34),    # warm medium ochre imprimatura
        stroke_size=4,
        wet_blend=0.88,                      # near-seamless; no visible brushwork on flesh
        edge_softness=0.72,                  # soft but not sfumato — forms are legible
        jitter=0.015,
        glazing=(0.82, 0.62, 0.40),          # warm amber-rose unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "French Neoclassical / Late Rococo portraiture — the luminous pearlescent "
            "skin technique of the ancien régime's greatest portraitist.  Vigée Le Brun "
            "worked from the midtone outward: a warm rose-ivory foundation across the "
            "whole face, then darkened toward shadow and lightened toward highlight from "
            "that pink centre.  The characteristic result is that shadows are never "
            "grey or cold — they are warm rose-violet, inhabited, alive — while highlights "
            "reach toward a cool pearl iridescence (not warm ivory) in the brightest "
            "specular zone.  This combination of warm rose body, cool pearl surface, and "
            "warm rose-violet shadows is unique in 18th-century painting.  Drapery and "
            "costume are rendered with jewel-like saturated colour — deep French blues, "
            "vermillion reds, warm gold accents — set against a typically dark, almost "
            "tonally neutral backdrop.  Her edges are soft but not dissolved: each form "
            "is rounded through controlled gradients, not sfumato blur.  Unlike Leonardo "
            "or Raphael, she does not suppress individual features into atmospheric unity; "
            "instead each face retains its specific character within the warm, glowing key."
        ),
        famous_works=[
            ("Self-Portrait with Straw Hat",       "1782"),
            ("Self-Portrait with Her Daughter",    "1786"),
            ("Portrait of Marie Antoinette",        "1783"),
            ("Marie Antoinette with a Rose",        "1783"),
            ("La Paix ramenant l'Abondance",        "1780"),
            ("Portrait of Hubert Robert",           "1788"),
            ("Portrait of Lady Hamilton",           "1791–92"),
            ("Portrait of Anna Pitt as Hebe",       "1792"),
        ],
        inspiration=(
            "Use vigee_le_brun_pearlescent_grace_pass() after build_form() and before "
            "final glazing to apply her signature skin quality: warm rose bloom in the "
            "lit midtones (the dominant quality — not orange-warm like Old Masters but "
            "pink-rose like candlelit aristocratic skin), cool pearl shift in the very "
            "brightest highlights (B+ slight, R- slight — nacre not ivory), and warm "
            "rose-violet warmth injected into the deepest shadows.  "
            "Combine with subsurface_scatter_pass() at lower opacity (0.40–0.55) to "
            "add the physiologically accurate SSS red-orange bloom beneath the rose "
            "surface quality — the combination of SSS depth + pearlescent surface is "
            "the full Vigée Le Brun skin model.  "
            "ground_color=(0.62, 0.50, 0.34) — warm medium ochre; her grounds are warmer "
            "and more pink than Leonardo's cool imprimatura.  "
            "wet_blend=0.88, edge_softness=0.72 — highly blended but not sfumato: her "
            "edges are soft and rounded, but each form remains legible and specific.  "
            "glazing=(0.82, 0.62, 0.40) — a warm amber-rose glaze that unifies the whole "
            "portrait into a single warm, rose-tinted key.  Dark blue-ultramarine backdrop "
            "(ground_color contrast) makes the glowing warm flesh read as even more luminous."
        ),
    ),

    "pontormo": ArtStyle(
        artist="Jacopo Pontormo",
        movement="Florentine Mannerism",
        nationality="Italian",
        period="1494–1557",
        palette=[
            (0.78, 0.88, 0.30),   # acid chartreuse-yellow — the Deposition robes
            (0.90, 0.32, 0.52),   # shocking carmine-rose — swooping drapery pink
            (0.68, 0.80, 0.92),   # glacial pale blue — the Virgin's mantle
            (0.78, 0.62, 0.82),   # lavender-lilac — ambiguous intermediate
            (0.92, 0.50, 0.26),   # hot vermilion-orange — accent drapery
            (0.52, 0.68, 0.80),   # cerulean — cold middle-ground
            (0.94, 0.90, 0.54),   # lemon ice — acid pale yellow
            (0.06, 0.04, 0.14),   # purple-black void — deep shadow
        ],
        ground_color=(0.52, 0.50, 0.58),
        stroke_size=5,
        wet_blend=0.28,
        edge_softness=0.68,
        jitter=0.028,
        glazing=None,
        crackle=True,
        chromatic_split=False,
        technique=(
            "Pontormo abandoned the warm harmonic palettes of the High Renaissance "
            "for an entirely unprecedented system of colour — acid, dissonant, "
            "deliberately unnatural.  Where Leonardo sought harmony through sfumato "
            "and Raphael through luminous balance, Pontormo cultivated tension.  "
            "His Deposition from the Cross (c.1525–28, Capponi Chapel, Florence) "
            "is the supreme example: a composition built from chartreuse yellow, "
            "shocking carmine rose, glacial blue, and hot vermilion, none of which "
            "harmonise in the conventional sense — the effect is a sustained "
            "chromatic anxiety.  "
            "The shadows in his work are not warm umbers but cold, blue-tinged or "
            "violet-black — a deliberate inversion of the High Renaissance norm. "
            "Highlights push toward acid lemon-yellow rather than warm ivory.  "
            "His figures have a compressed, swirling quality: they occupy shallow "
            "space with no convincing recession — the composition feels crowded "
            "and airless, as if the figures cannot escape one another.  "
            "His flesh is pale, almost waxen, with a slightly clammy quality — "
            "lacking the warm subsurface glow of Venetian portraiture.  "
            "He was intensely introspective: his late diary records a life of "
            "anxious solitude, and this psychological state is inseparable from "
            "his work's quality of interior tension rendered as colour."
        ),
        famous_works=[
            ("Deposition from the Cross",        "c. 1525–28"),
            ("Visitation",                        "c. 1528–29"),
            ("Portrait of a Halberdier",          "c. 1528–30"),
            ("Joseph in Egypt",                   "c. 1515–18"),
            ("Vertumnus and Pomona",              "1519–21"),
            ("Portrait of a Young Man",           "c. 1530"),
            ("Supper at Emmaus",                  "1525"),
            ("Cosimo de' Medici the Elder",       "c. 1519"),
        ],
        inspiration=(
            "Use pontormo_dissonance_pass() after build_form() to apply Pontormo's "
            "signature dissonant colour vibration: acid chartreuse pushed into the "
            "highlights, cold violet-black deepened in the shadows, and a chromatic "
            "tension introduced in the midtones (alternating warm rose and cool "
            "chartreuse by spatial region) that reads as psychological unease rather "
            "than conventional colour harmony.  "
            "ground_color=(0.52, 0.50, 0.58) uses a cool grey-lilac imprimatura — "
            "unlike the warm ochre grounds of the High Renaissance, Pontormo's "
            "Mannerist palette demands a neutral-cool base so that the acid colours "
            "are not pre-warmed by the ground.  "
            "edge_softness=0.68 keeps form legible but not resolved — Pontormo's "
            "figure edges are not sfumato (imperceptible) but not Flemish either: "
            "a controlled softness that maintains the swirling compositional flow.  "
            "glazing=None — his colours are direct and opaque, not built through "
            "transparent layers: the shocking effect would be lost under glazing."
        ),
    ),

    # ── Lawrence Alma-Tadema ───────────────────────────────────────────────────
    "alma_tadema": ArtStyle(
        artist="Lawrence Alma-Tadema",
        movement="Academicism / Victorian Classical",
        nationality="Dutch-British",
        period="1870–1912",
        palette=[
            (0.96, 0.94, 0.88),   # crystalline marble white — Pentelic with warm cast
            (0.88, 0.80, 0.62),   # warm Giallo Antico stone — Roman golden marble
            (0.72, 0.85, 0.92),   # Mediterranean sky — Aegean blue over marble
            (0.94, 0.88, 0.70),   # alabaster warm cream — translucent stone glow
            (0.82, 0.60, 0.44),   # terracotta Roman tile — warm reddish-brown
            (0.56, 0.72, 0.58),   # laurel and olive — muted classical green
            (0.90, 0.82, 0.68),   # silk ivory — draped Classical costume
            (0.38, 0.52, 0.68),   # Aegean deep water — distant sea blue-grey
            (0.95, 0.90, 0.82),   # noon light on marble — bleached Mediterranean
        ],
        ground_color=(0.88, 0.82, 0.68),    # warm cream imprimatura — light marble ground
        stroke_size=3,
        wet_blend=0.30,          # primarily optical — not relying on wet blending
        edge_softness=0.22,      # very crisp edges — photographic precision
        jitter=0.008,            # extremely low jitter — near-photographic detail
        glazing=(0.92, 0.86, 0.68),   # warm golden glaze — Mediterranean noon
        crackle=False,           # Victorian oil on panel — typically well-preserved
        chromatic_split=False,
        technique=(
            "Photographic precision with an almost enamelled surface — Alma-Tadema "
            "built up thin, glazed layers over a smooth, light-coloured ground, "
            "achieving a luminosity in his marble that seems to glow from within.  "
            "His marble is not merely white: it is translucent, veined, and selectively "
            "warm — absorbing light in the depths and radiating it from the surface.  "
            "Specular highlights on polished marble are pure, concentrated, and sharply "
            "bounded — like reflections in glass, not the diffuse highlights of Impressionism.  "
            "Silk and linen draperies show fine, coherent folds — each crease a precise "
            "cast shadow with a clean penumbra.  Flesh tones are cool ivory — Roman marble "
            "light reflected back onto skin.  The overall palette is extremely high in "
            "key: his paintings read as bright, sun-flooded interiors where the dominant "
            "optical fact is light bouncing between marble surfaces."
        ),
        famous_works=[
            ("The Roses of Heliogabalus",         "1888"),
            ("Spring (A Coign of Vantage)",        "1895"),
            ("Tepidarium",                         "1881"),
            ("The Finding of Moses",               "1904"),
            ("A Favourite Custom",                 "1909"),
            ("In the Tepidarium",                  "1881"),
            ("Phidias and the Frieze of the Parthenon", "1868"),
        ],
        inspiration=(
            "Apply alma_tadema_marble_luminance_pass() to bright surfaces to introduce "
            "the characteristic crystalline specular quality of polished Roman marble — "
            "concentrated pure-white highlights with a subtle cool shift, surrounded by "
            "the warm cream glow of translucent stone lit from within.  "
            "Follow with crystalline_surface_pass() (session 65 artistic improvement) "
            "to sharpen and concentrate specular peaks across the whole image — this "
            "universal surface-quality improvement was inspired directly by Alma-Tadema's "
            "glass-like precision.  "
            "ground_color=(0.88, 0.82, 0.68) uses a very light, warm cream ground — "
            "Alma-Tadema often worked on panel or prepared a light ground so that the "
            "thin glazes would transmit maximum luminosity.  "
            "edge_softness=0.22 is the lowest in the catalog after Holbein — his edges "
            "are photographically crisp, a defining quality that separates his work from "
            "academic contemporaries like Bouguereau (soft-edged) or Ingres (sharp but "
            "not photographic)."
        ),
    ),

    # ── Joachim Patinir ────────────────────────────────────────────────────────
    "patinir": ArtStyle(
        artist="Joachim Patinir",
        movement="Flemish World Landscape (Weltlandschaft)",
        nationality="Flemish",
        period="c. 1480–1524",
        palette=[
            (0.72, 0.58, 0.32),   # warm sandy ochre foreground earth
            (0.50, 0.38, 0.22),   # mid brown warm earth / rocks
            (0.42, 0.52, 0.32),   # muted olive green middle-distance foliage
            (0.52, 0.58, 0.42),   # pale sage green far-middle terrain
            (0.55, 0.62, 0.72),   # dusty cool blue far distance
            (0.72, 0.76, 0.82),   # pale blue-grey sky and horizon haze
            (0.22, 0.16, 0.08),   # dark warm umber shadow rock
            (0.38, 0.52, 0.68),   # cool river-water silver-blue
        ],
        ground_color=(0.65, 0.55, 0.32),    # warm mid-ochre panel ground
        stroke_size=4,
        wet_blend=0.25,                      # relatively dry — precise gem-like detail
        edge_softness=0.30,                  # reasonably crisp edges for geological forms
        jitter=0.020,
        glazing=(0.70, 0.68, 0.52),          # warm amber-gold unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Weltlandschaft ('world landscape') — panoramic imaginary terrain viewed "
            "from a high, elevated vantage point.  The defining signature is a systematic "
            "three-zone atmospheric recession: (1) warm brown-ochre foreground with crisp "
            "geological rock detail; (2) muted olive-green middle distance with winding "
            "rivers, paths, and tiny figures; (3) cool blue-grey far distance dissolving "
            "into pale sky.  Patinir was the first Western painter to establish landscape "
            "as an independent genre — his figures are biblical pretexts for the vista.  "
            "Surfaces are gem-like and enamelled, painted on panel with fine brushwork."
        ),
        famous_works=[
            ("Landscape with Charon Crossing the Styx", "c. 1515–1524"),
            ("Rest on the Flight into Egypt",           "c. 1515"),
            ("Landscape with the Baptism of Christ",    "c. 1515"),
            ("Saint Jerome in a Rocky Landscape",       "c. 1515"),
        ],
        inspiration=(
            "Apply patinir_weltlandschaft_pass() to enforce the three-zone warm→green→cool "
            "atmospheric recession that defines Weltlandschaft painting.  The foreground is "
            "pushed toward warm sandy ochre, the middle distance toward muted olive-green, "
            "and the far distance toward pale cool blue-grey.  Use edge_softness=0.30 (not "
            "sfumato — Patinir's edges are precise, not dissolved) with a low wet_blend=0.25 "
            "to preserve the gem-like, enamel surface quality of Flemish panel painting.  "
            "The warm amber glaze unifies across all three recession zones."
        ),
    ),

    # ── Andrea Mantegna ───────────────────────────────────────────────────────
    # ── Claude Lorrain ────────────────────────────────────────────────────────
    "claude_lorrain": ArtStyle(
        artist="Claude Lorrain",
        movement="Classical Landscape Baroque",
        nationality="French (worked in Rome)",
        period="1600–1682",
        palette=[
            (0.95, 0.82, 0.48),   # warm golden-amber horizon glow — the signature Lorrain light
            (0.88, 0.72, 0.38),   # deep golden ochre — sunlit sky above horizon
            (0.62, 0.72, 0.85),   # cool cerulean upper sky — high atmospheric blue
            (0.78, 0.82, 0.90),   # pale blue-white zenith — cloud-lit sky
            (0.40, 0.35, 0.20),   # warm dark sienna — foreground shadow earth
            (0.25, 0.32, 0.18),   # deep cool green — dark foreground trees
            (0.52, 0.60, 0.42),   # muted sage — mid-distance foliage
            (0.70, 0.75, 0.80),   # silver-blue water / river light
            (0.82, 0.78, 0.62),   # warm cream limestone — classical ruins / architecture
        ],
        ground_color=(0.65, 0.58, 0.35),    # warm golden-ochre primed ground
        stroke_size=7,
        wet_blend=0.72,                      # high blending — luminous dissolved transitions
        edge_softness=0.75,                  # soft edges — atmosphere dissolves all forms at distance
        jitter=0.022,
        glazing=(0.88, 0.72, 0.35),          # deep golden amber glaze — the Lorrain golden unity
        crackle=True,
        chromatic_split=False,
        technique=(
            "Idealized classical landscape — the natural world reimagined as a serene, "
            "golden-lit Arcadia.  Claude Lorrain (born Claude Gellée) was the supreme master "
            "of landscape as mood: every element — ruined temples, dark repoussoir trees, "
            "shimmering water, tiny epic figures — serves the single purpose of conveying light. "
            "His signature achievement is the contre-jour sun on the horizon, flooding the lower "
            "sky and water with warm amber-gold while the upper sky recedes into cool cerulean. "
            "Foreground trees act as dark repoussoir flanking wings that frame the luminous "
            "distance beyond; the eye travels in from dark foreground warmth, through cool "
            "middle-distance haze, toward the incandescent golden horizon.  Forms dissolve in "
            "atmospheric haze as they recede — a proto-Impressionist aerial perspective that "
            "predates Monet by two centuries.  Claude made extensive open-air studies in chalk "
            "(Liber Veritatis) but always painted finished works in the studio, refining the "
            "golden hour from observation into ideal.  His influence on the English Romantic "
            "landscape — Turner, Constable — was profound and direct."
        ),
        famous_works=[
            ("Embarkation of the Queen of Sheba",    "1648"),
            ("Seaport at Sunset",                    "c. 1639"),
            ("The Mill",                             "1648"),
            ("Landscape with the Marriage of Isaac and Rebekah", "1648"),
            ("Pastoral Landscape with the Ponte Molle", "1645"),
        ],
        inspiration=(
            "Apply claude_lorrain_golden_light_pass() to flood the lower sky and "
            "horizon with warm amber-gold light while preserving the cool cerulean upper "
            "sky.  The pass creates the signature contre-jour gradient: maximum golden "
            "warmth at the horizon, cooling and darkening toward the zenith.  Use "
            "edge_softness=0.75 and wet_blend=0.72 so distant forms dissolve into the "
            "atmospheric haze — the entire landscape breathes with diffused golden light "
            "rather than crisp, individually readable elements."
        ),
    ),

    # ── Jacques-Louis David ───────────────────────────────────────────────────
    "jacques_louis_david": ArtStyle(
        artist="Jacques-Louis David",
        movement="French Neoclassicism",
        nationality="French",
        period="1748–1825",
        palette=[
            (0.85, 0.78, 0.65),   # warm ivory flesh — smooth, porcelain-luminous skin
            (0.70, 0.60, 0.45),   # mid-tone flesh — warm shadow on cheek and neck
            (0.45, 0.38, 0.28),   # deep warm-ochre shadow — under jaw, collar bone
            (0.72, 0.72, 0.70),   # cool stone-grey — classical architectural background
            (0.55, 0.55, 0.52),   # mid stone — mid-value column or draped fabric
            (0.30, 0.30, 0.28),   # dark stone-grey — deep architectural shadow
            (0.62, 0.42, 0.22),   # warm amber — Roman drapery, military uniform
            (0.22, 0.26, 0.38),   # Prussian blue-grey — military costume or sky
        ],
        ground_color=(0.65, 0.60, 0.48),    # warm grey-ochre imprimatura — classical preparation
        stroke_size=5,
        wet_blend=0.25,                      # moderate — smooth flesh without deep blending haze
        edge_softness=0.32,                  # moderate — crisp classical contour, not sfumato
        jitter=0.012,
        glazing=(0.68, 0.60, 0.42),          # warm amber unifying glaze — old-master warmth
        crackle=True,
        chromatic_split=False,
        technique=(
            "Heroic Neoclassical clarity — David subordinated every pictorial element "
            "to rational, sculptural legibility.  Trained under Vien in the French "
            "Academy, he absorbed the cool geometry of Poussin and the civic grandeur "
            "of Roman relief sculpture, then fused these with the direct observation "
            "of Caravaggio's dramatic lighting.  His flesh is luminously smooth — "
            "closer to polished marble than living skin — achieved through a warm "
            "imprimatura, careful layered lean-to-fat construction, and a final amber "
            "glaze that unifies the surface without obscuring the precise contour "
            "drawing beneath it.  Backgrounds are characteristically cool and "
            "architectural: grey stone columns, receding arches, dark curtains that "
            "frame the heroic figure without competing for attention.  The Death of "
            "Marat (1793) demonstrates his supreme mastery: a radical horizontal "
            "composition with a near-black upper void, the body lit by a raking upper-"
            "left source, with all sentimental detail excised for political power.  "
            "Napoleon Crossing the Alps (1800–1801) shows his command of heroic "
            "vertical scale — the figure painted five times for different patrons, "
            "each variant calibrated for a different court's taste.  David never "
            "confused drama with excess: his restraint is a political act."
        ),
        famous_works=[
            ("Oath of the Horatii",              "1784"),
            ("The Death of Marat",               "1793"),
            ("Napoleon Crossing the Alps",        "1801"),
            ("Coronation of Napoleon",            "1807"),
            ("The Intervention of the Sabine Women", "1799"),
            ("Madame Récamier",                   "1800"),
        ],
        inspiration=(
            "Apply david_neoclassical_clarity_pass() to reinforce David's heroic "
            "sculptural legibility: cool the background toward stone-grey, crisp the "
            "figure contours with a mild edge-enhancement, and add a subtle warm-"
            "amber glaze over the flesh to achieve the luminous but controlled "
            "surface that defines his portrait and history painting.  Use "
            "ground_tone_recession_pass() to push the background into deeper "
            "cool shadow, reinforcing the spatial separation between the lit heroic "
            "figure in the foreground and the architectural void behind it."
        ),
    ),

    # ── Andrea Mantegna ───────────────────────────────────────────────────────
    "andrea_mantegna": ArtStyle(
        artist="Andrea Mantegna",
        movement="Paduan Renaissance",
        nationality="Italian",
        period="1431–1506",
        palette=[
            (0.85, 0.82, 0.74),   # pale chalk-white highlight — stone lit in raking light
            (0.65, 0.62, 0.54),   # cool mid stone — the dominant Mantegna mineral tone
            (0.48, 0.45, 0.36),   # warm grey-ochre shadow on carved form
            (0.30, 0.27, 0.20),   # deep warm-umber shadow trough
            (0.14, 0.12, 0.08),   # near-black void — Mantegna's deepest shadows
            (0.72, 0.68, 0.58),   # parchment ground — warm cream-grey imprimatura
            (0.42, 0.52, 0.64),   # cool sky-blue distance — archaeological sky
            (0.35, 0.42, 0.30),   # dull muted green — rocky landscape vegetation
        ],
        ground_color=(0.72, 0.68, 0.55),    # warm cream-grey gesso ground
        stroke_size=4,
        wet_blend=0.12,                      # very dry — stone does not bleed; forms carved, not melted
        edge_softness=0.20,                  # crisp archaeological edges — opposite of Leonardo sfumato
        jitter=0.018,
        glazing=None,                        # no oil glazing — Mantegna used tempera on canvas or panel
        crackle=True,                        # aged Renaissance panel/canvas
        chromatic_split=False,
        technique=(
            "Sculptural grisaille precision — figures rendered as if carved from cold marble or "
            "cast in bronze.  Mantegna trained in the workshop of Francesco Squarcione, who "
            "immersed his pupils in Greco-Roman antiquity; every figure in Mantegna's work "
            "reads as a three-dimensional sculpture seen from a low, theatrical viewpoint.  "
            "His colour is characteristically cool and mineral: pale chalk-white highlights, "
            "cold grey-stone midtones, warm umber shadows.  The grisaille quality is most "
            "explicit in the Camera degli Sposi ceiling trompe-l'oeil and the series of "
            "canvases depicting the Triumphs of Caesar.  Edges are engraved-crisp — never "
            "sfumato — giving his forms the quality of relief sculpture.  Perspective "
            "is rigorously foreshortened: the Dead Christ experiments with extreme sotto in "
            "sù (from below) foreshortening that would influence every subsequent master "
            "of the figure, including Michelangelo."
        ),
        famous_works=[
            ("Camera degli Sposi (Bridal Chamber)", "1465–1474"),
            ("Lamentation over the Dead Christ",    "c. 1480"),
            ("Triumphs of Caesar",                  "1484–1492"),
            ("Saint Sebastian",                     "c. 1480"),
            ("Agony in the Garden",                 "c. 1455"),
        ],
        inspiration=(
            "Apply mantegna_sculptural_form_pass() to push the rendered figure toward the "
            "cold, engraved-stone quality that defines Mantegna.  The pass detects facial "
            "ridge-forms (brow bone, cheekbone, nose bridge, chin) using luminance gradients "
            "and adds a pale chalk-cool highlight on their lit surfaces while deepening the "
            "shadow troughs.  This gives the face the three-dimensional carved relief quality "
            "that separates Mantegna from Leonardo's melted-smoke approach.  Use edge_softness=0.20 "
            "and wet_blend=0.12 — the antithesis of sfumato — to preserve the archaeological "
            "crispness that makes his forms feel permanently solid."
        ),
    ),

    # ──────────────────────────────────────────────────────────────────────────
    # Guido Reni — session 70 addition
    # ──────────────────────────────────────────────────────────────────────────
    "guido_reni": ArtStyle(
        artist="Guido Reni",
        movement="Bolognese Baroque",
        nationality="Italian",
        period="1575–1642",
        palette=[
            (0.94, 0.90, 0.84),   # alabaster pearl-white — the defining Reni highlight
            (0.88, 0.78, 0.68),   # warm pale flesh — the lit midtone, peachy and soft
            (0.80, 0.66, 0.58),   # warm rose-ivory — upper midtone with gentle warmth
            (0.72, 0.56, 0.50),   # rose-peach midtone — characteristic warm shadow transition
            (0.48, 0.40, 0.54),   # cool lavender-grey shadow — distinctly violet, shadow side
            (0.34, 0.28, 0.42),   # deep violet-grey — Reni's deepest shadow, B>R for spiritual lightness
            (0.42, 0.56, 0.76),   # heavenly blue — sky and drapery, the divine register
            (0.82, 0.70, 0.30),   # warm amber-gold — gilded details and angelic accoutrements
        ],
        ground_color=(0.68, 0.60, 0.48),    # warm mid-ochre — Bolognese imprimatura
        stroke_size=5,
        wet_blend=0.62,                      # high — silken skin blending
        edge_softness=0.55,                  # moderate — softer than David, crisper than Leonardo
        jitter=0.015,
        glazing=(0.90, 0.82, 0.72),          # warm ivory-rose unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Reni is the supreme master of the Bolognese Baroque ideal: beauty as a vehicle "
            "for the divine.  Trained in Annibale Carracci's Accademia degli Incamminati, he "
            "developed a technique of exquisite softness — not Leonardo's smoky sfumato but a "
            "silken, high-key blending that gives his figures an otherworldly luminosity.  His "
            "skin is painted in thin, layered glazes over a warm ground, building from rose-ivory "
            "midtones to alabaster pearl highlights that seem to radiate from within.  Shadows are "
            "kept cool and violet-grey rather than brown-black, giving even the darkest passages a "
            "spiritual lightness.  His palette is high-key: pale ivory, warm peach, rose, and the "
            "heavenly blue of divine drapery.  Faces are idealised to the point of abstraction — "
            "oval, smooth-browed, with downcast or upcast eyes.  The Aurora ceiling fresco in "
            "the Casino Rospigliosi (1614) is the fullest demonstration: a triumphal procession "
            "of light across a cool dawn sky, every figure individually lit and yet unified by "
            "the warm-to-cool colour temperature sweep.  His portrait of Beatrice Cenci (attr.) "
            "captures a quality of inward spiritual suffering that the smooth, luminous skin makes "
            "all the more affecting by contrast."
        ),
        famous_works=[
            ("Atalanta and Hippomenes",       "c. 1612"),
            ("Archangel Michael",             "1635"),
            ("Aurora",                        "1614"),
            ("Beatrice Cenci (attr.)",        "c. 1599"),
            ("The Massacre of the Innocents", "1611"),
            ("Samson the Victor",             "1611"),
        ],
        inspiration=(
            "Apply guido_reni_angelic_grace_pass() to push the portrait toward Reni's "
            "characteristic alabaster luminosity: lift the highlight region toward a cool "
            "pearl-white, inject warm rose into the cheek/lip zone, and cool the deepest "
            "shadows toward violet-grey.  Follow with highlight_bloom_pass() — the session 70 "
            "artistic improvement — which adds a soft luminous glow around the brightest "
            "highlights, simulating the way Reni's glazed ivory skin appears to emit its own "
            "gentle light.  Use wet_blend=0.62 and edge_softness=0.55: silken blending without "
            "sfumato dissolution."
        ),
    ),

    "correggio": ArtStyle(
        artist="Antonio Allegri da Correggio",
        movement="Parma Renaissance / Proto-Baroque",
        nationality="Italian",
        period="1489–1534",
        palette=[
            (0.96, 0.88, 0.70),   # warm golden ivory — the lit highlight, honeyed and radiant
            (0.90, 0.78, 0.58),   # warm amber flesh — characteristic midtone, suffused with gold
            (0.82, 0.66, 0.46),   # golden ochre — upper shadow transition, warm and glowing
            (0.68, 0.52, 0.36),   # amber-brown shadow — deeper midtone, still warm, no cool lean
            (0.52, 0.40, 0.28),   # warm umber — shadow side, rich, honeyed, never cold
            (0.36, 0.28, 0.20),   # deep warm brown — deepest shadows, warm ground showing through
            (0.60, 0.72, 0.86),   # soft heavenly blue — drapery and sky, pale and dreaming
            (0.76, 0.62, 0.36),   # golden amber glaze — the unifying warm varnish tone
        ],
        ground_color=(0.64, 0.54, 0.36),    # warm amber-ochre ground — Correggesque imprimatura
        stroke_size=5,
        wet_blend=0.70,                      # very high — the signature melting, seamless transitions
        edge_softness=0.72,                  # very soft — proto-sfumato, almost no hard edges
        jitter=0.012,
        glazing=(0.86, 0.74, 0.46),          # warm golden honey glaze — the Correggesque unifier
        crackle=True,
        chromatic_split=False,
        technique=(
            "Correggio is the supreme master of golden, tender luminosity in the Italian "
            "Renaissance.  Working in Parma, largely independent of the Roman and Florentine "
            "academic traditions, he developed a technique of extraordinary softness — a proto-"
            "Baroque melting of form into light that anticipates Rubens, Reni, and the entire "
            "Flemish Baroque by a century.  His defining quality is 'Correggesque' tenderness: "
            "figures that appear suffused with warm, amber-gold light from within, their forms "
            "dissolving into each other without hard transitions.  Unlike Leonardo's cool, smoky "
            "sfumato, Correggio's is warm and honeyed — the shadows are amber-brown, never grey, "
            "and the highlights are warm ivory rather than cool pearl.  He painted the Assumption "
            "of the Virgin in Parma Cathedral (1526–30) lying on his back on scaffolding, creating "
            "a dizzying illusionistic vortex of foreshortened figures spiralling up into heavenly "
            "light — the first great illusionistic ceiling fresco of the Baroque tradition.  His "
            "Jupiter and Io (c. 1531) demonstrates the Correggesque ideal at its most intense: "
            "Io's flesh, emerging from a warm dark cloud, is rendered with a melting, amber-gold "
            "luminosity that makes the body appear to glow.  His figures smile — the 'Correggesque "
            "smile' is a warm, sensuous upturn of the lips quite unlike the enigmatic ambiguity of "
            "Leonardo or the spiritual detachment of Raphael.  Technically, he built up his flesh "
            "tones with warm amber glazes over an ochre imprimatura, never allowing the shadows to "
            "cool, creating an overall golden harmony that suffuses the entire canvas."
        ),
        famous_works=[
            ("Assumption of the Virgin",     "1526–1530"),
            ("Jupiter and Io",               "c. 1531"),
            ("Ganymede",                     "c. 1531"),
            ("Leda and the Swan",            "c. 1532"),
            ("The Holy Night",               "c. 1530"),
            ("Madonna of Saint Jerome",      "1528"),
            ("Adoration of the Magi",        "1516–1518"),
        ],
        inspiration=(
            "Apply correggio_golden_tenderness_pass() to push the portrait toward Correggio's "
            "characteristic warm-gold luminosity: shift the midtones toward amber-gold, warm the "
            "shadows toward rich umber (resisting any cool shift), and add a soft warm glow to "
            "the face and upper figure.  Follow with luminous_haze_pass() — the session 71 "
            "artistic improvement — which simulates the aged golden varnish and atmospheric warmth "
            "of old master oil paintings, adding a subtle global honey-tone haze that unifies the "
            "palette and softens the overall tonal contrast.  Use wet_blend=0.70 and "
            "edge_softness=0.72 for the Correggesque melting quality."
        ),
    ),

    # ── Antoine Watteau ───────────────────────────────────────────────────────
    "watteau": ArtStyle(
        artist="Jean-Antoine Watteau",
        movement="French Rococo / Fête Galante",
        nationality="French",
        period="1684–1721",
        palette=[
            (0.95, 0.91, 0.82),   # warm ivory highlight — autumnal, never brilliant
            (0.88, 0.78, 0.65),   # golden amber flesh — warm afternoon flesh tone
            (0.76, 0.65, 0.52),   # warm ochre midtone — the faded-silk quality
            (0.60, 0.50, 0.38),   # warm umber-sienna shadow — no cool blue, ever
            (0.42, 0.36, 0.26),   # deep warm brown — deepest shadow, still glowing
            (0.60, 0.64, 0.44),   # moss-olive green — Watteau's autumnal foliage
            (0.50, 0.58, 0.68),   # dusty blue-grey — theatrical backdrop distance
            (0.82, 0.74, 0.52),   # warm golden haze — the crepuscular unifying glow
        ],
        ground_color=(0.70, 0.60, 0.42),    # warm golden-sienna imprimatura — Watteau's
                                            # warm ground that glows through the thin paint
                                            # film, unifying the whole in autumnal warmth
        stroke_size=9,
        wet_blend=0.58,                      # moderate — fluid but with feathery edges
        edge_softness=0.60,                  # edges soften gently — a dreamlike dissolution
        jitter=0.032,                        # slight tonal variation per stroke — the
                                            # shimmer of silk and leaf in fading light
        glazing=(0.80, 0.70, 0.48),         # warm golden-amber glaze — crepuscular unifier
        crackle=True,
        chromatic_split=False,
        technique=(
            "Antoine Watteau (1684–1721) is one of the most elusive and poetic painters "
            "in the history of Western art — the founder of the fête galante, a genre he "
            "essentially invented and to which he gave its definitive form in 'The "
            "Embarkation for Cythera' (1717, Louvre).  Born in Valenciennes in French "
            "Flanders, he moved to Paris around 1702 and absorbed the influence of Rubens "
            "(the great Marie de' Medici cycle then hanging in the Luxembourg Palace), "
            "Veronese, and the sixteenth-century Flemish masters.  His technique is "
            "characterised by a warm golden-sienna imprimatura laid over a red bole ground; "
            "thin, flowing oil paint is worked wet-into-wet with a soft hog-hair brush in "
            "decisive but gentle strokes.  The defining quality of his surfaces is a "
            "crepuscular, autumnal warmth: every passage seems bathed in the golden haze "
            "of late afternoon fading into twilight.  His shadows are never cold — they "
            "retain the warm umber-sienna of the ground showing through — and his highlights "
            "are a warm ivory rather than cool silver.  His figures in silks and satins are "
            "rendered with extraordinary sensitivity to fabric shimmer: the silk catches the "
            "light in warm highlights while the folds recede into warm umber.  Watteau died "
            "of tuberculosis at thirty-six, leaving a body of work — including 'Gilles' "
            "(Louvre), 'The Music Lesson' (Wallace), and the 'Fêtes galantes' — that is "
            "poignant, ironic, and suffused with a melancholy that underlies even the most "
            "festive scenes.  The fête galante is always, in Watteau, already ending: the "
            "light is fading, the music is stopping, the figures are departing.  This "
            "twilight quality — the sense of beauty observed at the moment of its passing "
            "— is his greatest achievement, and it is encoded in his palette: warm, "
            "golden, autumnal, and already moving toward shadow."
        ),
        famous_works=[
            ("The Embarkation for Cythera",  "1717"),
            ("Gilles (Pierrot)",             "c. 1718–1719"),
            ("The Music Lesson",             "c. 1715–1716"),
            ("The Shepherds",                "c. 1717–1719"),
            ("Jupiter and Antiope",          "c. 1715"),
            ("The Scale of Love",            "c. 1715–1718"),
            ("Mezzetin",                     "c. 1718–1720"),
        ],
        inspiration=(
            "Apply watteau_crepuscular_reverie_pass() to introduce Watteau's autumnal "
            "twilight quality: a warm golden haze that shifts the palette toward "
            "amber-sienna, lifts the deep shadows slightly (the warm ground showing "
            "through), softens edges into the dreamlike dissolution of his fête galante "
            "backgrounds, and adds a gentle crepuscular gradient — brighter and warmer "
            "in the upper middle zone, fading to golden amber at the periphery.  Use "
            "wet_blend=0.58 and edge_softness=0.60 for the characteristic floating, "
            "poetic quality that distinguishes Watteau from Fragonard's bravura energy."
        ),
    ),

    # ── Sofonisba Anguissola ───────────────────────────────────────────────────
    "sofonisba_anguissola": ArtStyle(
        artist="Sofonisba Anguissola",
        movement="Lombard Renaissance",
        nationality="Italian",
        period="1550–1625",
        palette=[
            (0.86, 0.72, 0.56),   # warm ivory flesh — Lombard luminous skin tone
            (0.74, 0.58, 0.42),   # mid-tone flesh — warm amber-gold midtone
            (0.52, 0.38, 0.24),   # warm umber shadow — deeper flesh in shadow
            (0.30, 0.22, 0.14),   # deep brown shadow — darkest flesh recess
            (0.16, 0.20, 0.18),   # dark dress — dignified black, slightly warm
            (0.72, 0.64, 0.50),   # golden ambient — the warm Lombard light envelope
        ],
        ground_color=(0.58, 0.48, 0.32),    # warm ochre imprimatura — Lombard golden ground
        stroke_size=6,
        wet_blend=0.72,                      # high — seamless Lombard skin transitions
        edge_softness=0.68,                  # soft but not sfumato — Lombard warmth without
                                             # Leonardo's extreme atmospheric dissolution
        jitter=0.018,
        glazing=(0.68, 0.54, 0.34),          # warm golden amber glaze — Lombard unifier
        crackle=True,
        chromatic_split=False,
        technique=(
            "Sofonisba Anguissola (c. 1535–1625) is the first woman to achieve "
            "international recognition as a major portrait painter in Western art.  "
            "Born in Cremona in Lombardy to an enlightened nobleman who ensured all six "
            "of his daughters received a humanist education, she studied under Bernardino "
            "Campi and later corresponded with Michelangelo, who praised her drawings.  "
            "From 1559 to 1573 she served as court painter and lady-in-waiting to "
            "Queen Isabella of Valois and later Queen Anne of Austria at the Spanish "
            "court of Philip II in Madrid — an extraordinary position of cultural "
            "prominence for any artist, let alone a woman in the sixteenth century.  "
            "Her technique is characterised by the warm Lombard light she absorbed from "
            "Campi and from the tradition of Bernardino Luini, Leonardo's Lombard "
            "follower: the skin is rendered with a seamless, glowing warmth — not the "
            "cool analytical light of the Florentines nor the extreme sfumato dissolution "
            "of Leonardo, but a middle path of warm, luminous naturalism.  She was "
            "particularly celebrated for the psychological intimacy and directness of her "
            "portraits: sitters look out from her canvases with a specific, living "
            "quality that contemporaries found remarkable — a 'breathing' quality "
            "(Anthony van Dyck, who visited her in Palermo in 1624 when she was nearly "
            "ninety and still discussing painting, noted that he learned more about "
            "portraiture from her than from any painted work).  Her palette is centred "
            "on warm ivory flesh with golden midtones and amber shadows; her dress "
            "passages are typically dark — black or deep forest green — which concentrates "
            "the eye on the luminous face and hands.  She favoured the half-length "
            "three-quarter pose that Leonardo had established as the format for intimate "
            "portraiture, with hands visible in the lower register.  Her sitters include "
            "her own sisters in informal, psychologically vivid group compositions — "
            "uncharacteristic for the period — and multiple royal portraits that combine "
            "formal dignity with a quality of inner life.  Technically, anguissola_intimacy_pass() "
            "encodes her defining achievement: a focused sharpening of the eyes and lips "
            "— the psychological centres of a portrait — against a gently softened "
            "periphery, giving the face its characteristic quality of living presence "
            "while the surrounding flesh and drapery recede into warm Lombard atmospheric "
            "warmth."
        ),
        famous_works=[
            ("Portrait of the Artist's Sisters Playing Chess",  "1555"),
            ("Self-Portrait at the Easel",                      "c. 1556"),
            ("Portrait of Queen Isabella of Valois",            "c. 1565"),
            ("Portrait of a Young Nobleman",                    "c. 1558"),
            ("The Chess Game",                                  "1555"),
            ("Portrait of Philip II",                           "c. 1565"),
            ("Self-Portrait",                                   "c. 1610"),
        ],
        inspiration=(
            "Apply anguissola_intimacy_pass() — the session 73 artistic improvement — "
            "to achieve Sofonisba's defining portrait quality: a psychological focus "
            "that sharpens the eyes and lips (the emotional centres of the face) while "
            "allowing the peripheral flesh, hair, and drapery to soften into the warm "
            "Lombard ambient light.  This creates her characteristic 'breathing' quality "
            "— the sense that the sitter is specifically present rather than generically "
            "idealised.  Combine with wet_blend=0.72 for the seamless Lombard skin and "
            "edge_softness=0.68 for warmth without extreme sfumato dissolution."
        ),
    ),

    # ── Hieronymus Bosch ──────────────────────────────────────────────────────
    # Hieronymus Bosch (c. 1450–1516) is the most singular painter in Western
    # art — a Brabantine master whose teeming, nightmarish visions of hell, temptation,
    # and spiritual peril have no precedent and no real successor.  Born in 's-Hertogenbosch
    # (from which he took his name), he spent his entire career in this provincial Brabantine
    # town, yet his paintings became international sensations, collected by Philip II of Spain,
    # who acquired everything he could.  His technique is grounded in the solid Early
    # Netherlandish oil tradition — thin, transparent oil glazes over white chalk-gesso on oak
    # panel — but deployed in a visionary service utterly unlike his contemporaries.
    #
    # Bosch's palette is dominated by a dark, warm olive-brown ground from which figures and
    # creatures emerge lit from an indeterminate source.  His backgrounds are NOT the flat
    # dark void of Tenebrist painting — they are alive.  Every square centimetre of his
    # backgrounds contains something: a distant city burning, a creature devouring a soul,
    # a fish with human legs, a tree-man leaning on broken eggshell boats.  This density
    # of symbolic incident is the defining characteristic of his style: the eye can never
    # rest in a Bosch painting.
    #
    # Against this dark, living backdrop, Bosch deploys his secondary palette: intense,
    # saturated jewel accents — crimson, lapis lazuli blue, golden amber, pale silver flesh —
    # that make individual figures leap from the void.  These accents are not arbitrarily
    # placed; they encode symbolic meaning.  The flesh of damned souls is grey-white; the
    # flesh of saintly figures is warm pink-ivory; the creatures are often bilious green or
    # dung-brown.
    #
    # His paint application is meticulous — far more so than his subjects suggest.  Forms
    # are built in controlled transparent glazes with fine sable-tipped brushes, giving even
    # the most grotesque creature a precise, almost jeweller's finish.  The eeriness of his
    # work arises not from loose, frightened paint but from the opposite: calm, patient,
    # deliberate craftsmanship applied to delirious subject matter.
    #
    # bosch_phantasmagoria_pass() encodes his defining aesthetic achievement: scattering
    # intricate micro-detail marks across background regions to create the sense that every
    # inch of the canvas conceals symbolic incident, while jewel-tone accents make focal
    # figures read against the warm-dark void.
    "hieronymus_bosch": ArtStyle(
        artist="Hieronymus Bosch",
        movement="Early Netherlandish / Brabantine Fantastical",
        nationality="Dutch (Brabantine)",
        period="1470–1516",
        palette=[
            (0.82, 0.72, 0.56),   # warm ivory flesh — saintly figure skin
            (0.72, 0.52, 0.38),   # mid-tone warm sienna — creature bodies
            (0.22, 0.14, 0.08),   # deep warm olive-brown — the Brabantine dark ground
            (0.30, 0.22, 0.12),   # dark umber — shadow passages and creature silhouettes
            (0.75, 0.15, 0.10),   # intense crimson — blood, damned flesh, hell fire accents
            (0.15, 0.28, 0.62),   # lapis lazuli blue — celestial figures, heavenly accents
            (0.72, 0.58, 0.15),   # warm golden amber — symbolic jewel accents, halos
            (0.62, 0.72, 0.32),   # bilious olive-green — creature bodies, hellish vegetation
            (0.85, 0.84, 0.80),   # pale grey-white — the flesh of damned souls
        ],
        ground_color=(0.24, 0.18, 0.10),    # dark warm olive-brown Brabantine ground
        stroke_size=4,
        wet_blend=0.35,                      # moderate — controlled transparent oil glazes
        edge_softness=0.30,                  # moderate crispness — jewel clarity against void
        jitter=0.045,                        # moderate variation — creature forms vary in tone
        glazing=(0.28, 0.22, 0.10),          # dark warm amber unifying glaze — the Brabantine void tone
        crackle=True,
        chromatic_split=False,
        technique=(
            "Bosch worked in thin, precise transparent oil glazes over white chalk-gesso on oak "
            "panel — the standard Early Netherlandish technique, deployed in service of a wholly "
            "unprecedented visionary programme.  His backgrounds are never simple voids: they teem "
            "with micro-detail — distant burning cities, fantastical hybrid creatures, symbolic "
            "architecture — that rewards prolonged looking.  Against this densely populated dark "
            "ground, focal figures emerge lit in warm ivory flesh (saints) or grey-white deadened "
            "flesh (the damned), picked out with intense jewel-tone accents of crimson, lapis blue, "
            "and golden amber.  Paint application is calm, patient, and meticulous — the eeriness "
            "arises from deliberate craftsmanship applied to nightmarish content, not from loose "
            "or anxious marks.  Characteristic palette: warm olive-brown void, crimson blood accents, "
            "lapis azure celestial notes, bilious green creatures, pale ivory saints."
        ),
        famous_works=[
            ("The Garden of Earthly Delights",          "c. 1490–1510"),
            ("The Temptation of Saint Anthony",          "c. 1501"),
            ("The Last Judgment",                        "c. 1482"),
            ("The Haywain Triptych",                     "c. 1500–1502"),
            ("The Ship of Fools",                        "c. 1490–1500"),
            ("The Extraction of the Stone of Madness",   "c. 1494–1516"),
            ("Christ Carrying the Cross",                "c. 1510–1516"),
        ],
        inspiration=(
            "Use bosch_phantasmagoria_pass() to scatter intricate micro-detail marks across "
            "background regions — creating the teeming symbolic density that makes a Bosch painting "
            "feel alive with hidden meaning.  The pass seeds small dark marks with occasional intense "
            "jewel-tone accents (crimson, lapis blue, amber) across background areas, using the figure "
            "mask to avoid overpainting the focal figure.  tone_ground() with the dark olive-brown "
            "Brabantine ground is essential — the void must be warm and deep.  underpainting in dark "
            "umber establishes the symbolic weight.  block_in() with fine stroke_size (4px) to build "
            "the meticulous, patient figure modelling.  Final dark warm amber glaze unifies the "
            "Brabantine void tone.  cool_atmospheric_recession_pass() can add the characteristic "
            "distant blue-grey horizon haze visible in his panoramic landscapes."
        ),
    ),

    # ── Session 75: Pieter de Hooch ──────────────────────────────────────────
    "pieter_de_hooch": ArtStyle(
        artist      = "Pieter de Hooch",
        movement    = "Dutch Golden Age / Domestic Interior",
        nationality = "Dutch",
        period      = "1629–1684",
        palette     = [
            (0.72, 0.52, 0.24),   # warm amber floor light
            (0.58, 0.44, 0.28),   # ochre brick wall
            (0.82, 0.74, 0.58),   # cream plaster highlight
            (0.34, 0.44, 0.54),   # cool exterior daylight
            (0.48, 0.38, 0.26),   # dark oak woodwork
            (0.68, 0.32, 0.18),   # deep madder red costume
            (0.22, 0.30, 0.42),   # blue-grey shadow
            (0.86, 0.82, 0.72),   # pale linen light
            (0.30, 0.22, 0.14),   # near-black shadow accent
        ],
        ground_color   = (0.54, 0.44, 0.30),   # warm sienna-ochre imprimatura
        stroke_size    = 5,
        wet_blend      = 0.20,
        edge_softness  = 0.55,
        jitter         = 0.015,
        glazing        = (0.62, 0.48, 0.26),   # warm amber unifying glaze
        crackle        = True,
        chromatic_split = False,
        technique      = (
            "Pieter de Hooch worked in small panel and canvas formats on a warm sienna-ochre "
            "imprimatura.  His defining technical achievement is the threshold light effect: "
            "the depiction of warm amber interior light in sharp, luminous contrast against "
            "the cool silvery daylight entering from an open window or doorway.  This "
            "warm/cool threshold was built through careful layered glazing — the warm floor "
            "and wall areas received successive thin amber-ochre glazes while the doorway "
            "and sky passages were painted in cool grey-blue tones that read as exterior "
            "atmosphere by contrast.  De Hooch was systematic in his perspective: his tile "
            "floors and receding rooms follow strict geometric recession that creates a sense "
            "of inhabitable domestic space.  His figures are secondary to the architecture of "
            "light; they are painted with warm flesh tones that catch the interior amber "
            "light, modelled with deliberate, unhurried marks — closer to Vermeer's patience "
            "than Hals's bravura, but warmer and more golden than either.  The famous "
            "'light through the doorway' effect is achieved by reserving a strong, clean "
            "rectangle of cool exterior light that acts as a colour-temperature foil to the "
            "warm amber foreground — a compositional device de Hooch invented and deployed "
            "with extraordinary consistency across his entire body of work."
        ),
        famous_works   = [
            ("The Courtyard of a House in Delft",        "1658"),
            ("A Woman and Her Maid in a Courtyard",      "c. 1660–1661"),
            ("Interior with Women beside a Linen Chest", "1663"),
            ("The Card Players",                         "c. 1658"),
            ("A Boy Bringing Bread",                     "c. 1663"),
            ("Woman Drinking with Soldiers",             "c. 1658"),
        ],
        inspiration    = (
            "Use de_hooch_threshold_light_pass() to model the characteristic warm/cool light "
            "contrast of de Hooch's domestic interiors — warm amber light floods the foreground "
            "from a window off the left edge, creating an oblique illumination across floors and "
            "figures while a cooler, exterior daylight quality fills the receding background. "
            "tone_ground() with the warm sienna-ochre imprimatura establishes the amber interior "
            "atmosphere from the start.  block_in() with moderate stroke_size captures the "
            "geometric tiled-floor perspective and architectural masses.  build_form() models "
            "the figure in warm interior light against the cool background recession.  "
            "A final warm amber glaze unifies the interior warmth."
        ),
    ),

    # ── Jan Steen ─────────────────────────────────────────────────────────────
    "jan_steen": ArtStyle(
        artist="Jan Steen",
        movement="Dutch Golden Age / Genre Comedy",
        nationality="Dutch",
        period="1646–1679",
        palette=[
            (0.84, 0.68, 0.48),   # warm amber flesh highlight — imprimatura showing through
            (0.72, 0.52, 0.34),   # mid-tone flesh — rosy amber midground
            (0.50, 0.32, 0.18),   # warm shadow flesh — deep amber-brown
            (0.18, 0.12, 0.06),   # near-black deep shadow
            (0.78, 0.22, 0.12),   # vivid red costume accent (vermilion-scarlet)
            (0.82, 0.72, 0.28),   # warm golden-yellow ochre (costume/fabric)
            (0.28, 0.38, 0.22),   # muted olive-green (foliage, shadow fabric)
            (0.90, 0.85, 0.72),   # warm cream-white highlight (linen, tablecloth)
            (0.60, 0.46, 0.28),   # warm ochre mid-ground (floor, wood, earth)
        ],
        ground_color=(0.52, 0.42, 0.24),    # warm amber-ochre imprimatura — same family as
                                             # de Hooch but slightly darker and more saturated;
                                             # Steen's ground asserts itself through thin paint
        stroke_size=8,
        wet_blend=0.40,                      # moderate blending — lively but not dissolved;
                                             # Steen paints with energy, not sfumato patience
        edge_softness=0.45,
        jitter=0.040,                        # higher jitter = chromatic vitality; his flesh
                                             # is never uniformly flat — always slightly varied
        glazing=(0.60, 0.45, 0.18),          # warm amber-umber unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Genre comedy painting — lively impasto highlights on warm amber imprimatura. "
            "Figures have flushed, rosy warm flesh from vigorous alla prima working. "
            "Characteristic warm amber shadows (never cold); deep Vandyke-brown darks. "
            "Confident directional strokes in clothing; more careful modelling in faces. "
            "Rich chromatic variety: vermilion reds, golden ochres, muted olive greens "
            "create visual energy. Moral narrative embedded in gesture and expression."
        ),
        famous_works=[
            ("The Feast of Saint Nicholas",                "c. 1665–1668"),
            ("The Sick Woman",                             "c. 1663–1666"),
            ("Rhetoricians at a Window",                   "c. 1661–1666"),
            ("The Merry Family",                           "1668"),
            ("The Way You Hear It Is the Way You Sing It", "1665"),
            ("As the Old Sing, So Pipe the Young",         "c. 1668–1670"),
        ],
        inspiration=(
            "Use steen_warm_vitality_pass() to introduce Jan Steen's warm amber imprimatura "
            "glow — the defining quality that makes his flesh appear luminous and alive. "
            "tone_ground() with warm ochre-amber establishes the lively interior warmth. "
            "block_in() with moderate stroke_size captures his energetic compositional masses. "
            "build_form() models flesh in warm interior light with rosy midtone warmth. "
            "The pass lifts highlight amber, adds rose flush to face zones, and ensures "
            "all shadows are warm amber-brown rather than cold — Steen's hallmark."
        ),
    ),


    # ── Nicolas Poussin ────────────────────────────────────────────────────────
    "nicolas_poussin": ArtStyle(
        artist="Nicolas Poussin",
        movement="French Classical",
        nationality="French",
        period="1624–1665",
        palette=[
            (0.74, 0.61, 0.38),   # warm stone ochre — Poussin's classical flesh highlight
            (0.62, 0.48, 0.30),   # mid-tone flesh — warm but controlled
            (0.42, 0.42, 0.52),   # cool silver-grey shadow — the defining French Classical shadow hue
            (0.22, 0.38, 0.72),   # Poussin azure — deep ultramarine for heroic drapery
            (0.72, 0.28, 0.20),   # Roman vermilion — his characteristic warm-red drapery accent
            (0.35, 0.42, 0.28),   # muted Arcadian olive green — cool landscape distance
            (0.84, 0.78, 0.65),   # warm ivory highlight — pale stone light on architecture
        ],
        ground_color=(0.55, 0.52, 0.42),    # neutral warm-grey ground — Poussin's typical Roman
                                              # imprimatura: cooler and more controlled than Rubens'
                                              # warm amber, warmer than Dürer's silver-white
        stroke_size=7,
        wet_blend=0.38,                      # deliberate, patient layering — Poussin worked in
                                              # Rome on sized linen; each session dried before the
                                              # next was applied.  Neither sfumato nor alla prima.
        edge_softness=0.42,                  # classical clarity — forms read as rational sculpture;
                                              # present, considered edges, no sfumato haze
        jitter=0.025,
        glazing=(0.50, 0.52, 0.54),          # cool silver-neutral unifying glaze — the opposite of
                                              # Rubens' warm amber; unifies the composition with a
                                              # cool architectural dignity (B >= R, as classical theory demands)
        crackle=True,
        chromatic_split=False,
        technique=(
            "French Classical — deliberate, architecturally rational oil painting. "
            "Colour zones organised like a stage set: figures lit by a raking, even "
            "light from the upper left, shadows cool grey-silver (never the warm amber "
            "of Baroque).  Each passage dried before the next; no wet-on-wet alla prima. "
            "The palette is disciplined: ultramarine blue, Roman red, warm flesh ochre, "
            "cool shadow grey — always in service of narrative clarity and moral weight. "
            "Saturation is deliberately restrained; chromatic intensity signals importance, "
            "not decoration.  Poussin said: 'The first requirement of painting is that "
            "it should be legible to reason.'"
        ),
        famous_works=[
            ("Et in Arcadia Ego",                       "c. 1637–1638"),
            ("The Rape of the Sabine Women",             "c. 1634–1635"),
            ("The Plague of Ashdod",                     "1630"),
            ("The Holy Family on the Steps",             "1648"),
            ("Moses Striking Water from the Rock",       "1649"),
        ],
        inspiration=(
            "Use poussin_classical_clarity_pass() to impose Poussin's defining chromatic "
            "discipline: cool the shadows (blue-grey, never warm amber), lift midtone clarity "
            "to the rational architectural light he favoured, and cap saturation so no colour "
            "zone shouts louder than the narrative demands.  tone_ground() with a neutral "
            "warm-grey imprimatura establishes the sober Roman ground.  block_in() with "
            "moderate stroke_size and controlled wet_blend builds the colour zones cleanly. "
            "The cool silver glaze at the end unifies the surface with a French Classical "
            "tonality: cool, clear, and morally legible."
        ),
    ),


    # ── Hyacinthe Rigaud ──────────────────────────────────────────────────────
    "hyacinthe_rigaud": ArtStyle(
        artist="Hyacinthe Rigaud",
        movement="French Court Baroque",
        nationality="French",
        period="1681–1743",
        palette=[
            (0.72, 0.52, 0.32),   # warm chestnut flesh — Rigaud's sitters have a warm,
                                   # sun-touched or candlelit ivory-amber complexion
            (0.54, 0.38, 0.22),   # mid-tone flesh shadow — warm brown modelling under chin/neck
            (0.12, 0.08, 0.06),   # near-black velvet void — the defining deep shadow in velvet
                                   # drapery; almost impenetrable darkness with warm undertone
            (0.78, 0.76, 0.82),   # cool silk highlight — the brilliant silvery sheen on silk/satin,
                                   # the chromatic opposite to the warm flesh
            (0.92, 0.90, 0.88),   # ermine white — pure ivory for ermine trim and lace cuffs
            (0.48, 0.32, 0.14),   # warm chestnut mid-velvet — the mid-tone in velvet folds,
                                   # a rich warm brown between near-black void and reflected light
            (0.25, 0.20, 0.38),   # royal blue-purple drapery — the prestige colour of court
                                   # portraiture, often the background curtain or robe lining
            (0.70, 0.58, 0.20),   # gold braid — the metallic trim of court dress, warm and
                                   # slightly desaturated (not raw yellow — aged court gold)
            (0.82, 0.72, 0.60),   # warm ivory ground glow — the luminous background that
                                   # contrasts with dark velvet and architectural columns
        ],
        ground_color=(0.50, 0.42, 0.30),    # warm amber-brown imprimatura — Rigaud prepared his
                                              # canvases with a warm mid-tone ground, standard in
                                              # the French Academy tradition.  The warmth glows
                                              # through shadows in velvet and flesh alike.
        stroke_size=6,
        wet_blend=0.32,                      # controlled layering — Rigaud built his portraits in
                                              # distinct phases: drawing, dead colour, colour proper,
                                              # and glazes.  Flesh was modelled carefully; velvet
                                              # required distinct light/mid/dark passages.
        edge_softness=0.38,                  # moderate crispness — silk highlights have found
                                              # edges; velvet folds transition softly; face edges
                                              # are clean but not Tenebrist razor-sharp.
        jitter=0.020,
        glazing=(0.52, 0.44, 0.32),          # warm amber-brown final glaze — unifies the canvas
                                              # with a courtly, candlelit warmth; deepens the
                                              # velvet voids and gives flesh a golden luminosity
        crackle=True,
        chromatic_split=False,
        technique=(
            "French Court Baroque portraiture — sumptuous, architecturally composed, and deeply "
            "hierarchical.  Rigaud was the premier portraitist of the Versailles court and the "
            "dominant figure in French portrait painting for fifty years (1690–1740).  His most "
            "famous work, the 1701 portrait of Louis XIV, codified the French royal portrait type: "
            "the king in ermine-lined coronation robes, sceptre in hand, full-length against a "
            "column and billowing curtain, the very image of absolute monarchy. "
            "His technique rests on three pillars: (1) deep velvet darkness — Rigaud mastered the "
            "near-black voids of velvet by building up multiple thin dark glazes over a warm "
            "mid-tone ground, creating a depth that absorbs light and makes the silk highlights "
            "appear to float above; (2) cool silk luminosity — the highlights on silk and satin "
            "are painted with cool silvery whites, the chromatic opposite of the warm flesh and "
            "warm velvet, creating a visual shock that reads as lustrous materiality; (3) warm "
            "chestnut flesh modelling — faces and hands are built up in warm ivory-amber flesh "
            "tones, modelled smoothly with fine brushes, giving the sitters a courtly, composed "
            "gravitas rather than Rembrandt's psychological turbulence or Hals's energy. "
            "Backgrounds are stable and architectural: columns, draped curtains (usually dark "
            "red-purple), and distant landscape glimpses.  The compositions are formally "
            "hierarchical — the sitter dominates, the environment submits."
        ),
        famous_works=[
            ("Portrait of Louis XIV in Coronation Robes",    "1701"),
            ("Portrait of Cardinal Fleury",                   "1728"),
            ("Portrait of Philippe II, Duke of Orléans",      "1700"),
            ("Portrait of Samuel Bernard",                    "1726"),
            ("Self-Portrait",                                 "c. 1698"),
        ],
        inspiration=(
            "Use rigaud_velvet_drapery_pass() to introduce Rigaud's defining material quality: "
            "the deep, sumptuous velvet darkness with its warm chestnut mid-tone and cool silk "
            "highlight sheen.  The pass identifies dark fabric zones (non-flesh pixels below a "
            "luminance threshold) and in three operations — deepens their voids to near-black with "
            "a warm undertone, adds a directional specular sheen on the lit edge of fabric folds "
            "using a cool silvery highlight, and adds faint ermine-like texture at highlight peaks. "
            "tone_ground() with warm amber-brown establishes the courtly imprimatura.  block_in() "
            "builds the colour masses with controlled wet_blend.  The warm chestnut flesh is "
            "modelled in careful warm ivory-amber layers; velvet drapery follows with dark glaze "
            "layers over the warm ground.  The result is a portrait of material opulence: "
            "presence, rank, and the weight of power rendered in pigment."
        ),
    ),

    # ──────────────────────────────────────────────────────────────────────────
    # Lorenzo Lotto — session 79 addition
    # ──────────────────────────────────────────────────────────────────────────
    # ── Session 80 ─────────────────────────────────────────────────────────────
    # Andrea del Sarto — "The Faultless Painter", Florentine High Renaissance.
    # Warm golden sfumato: amber-ivory highlights, seamless midtone transitions,
    # colour-temperature harmony that Vasari called 'without error'.
    # ──────────────────────────────────────────────────────────────────────────
    "andrea_del_sarto": ArtStyle(
        artist="Andrea del Sarto",
        movement="Florentine High Renaissance",
        nationality="Italian",
        period="c. 1486–1530",
        palette=[
            (0.94, 0.87, 0.73),   # warm ivory highlight — the 'faultless' flesh light
            (0.82, 0.72, 0.55),   # golden mid-flesh — the signature amber warmth
            (0.64, 0.52, 0.36),   # warm umber midtone-shadow
            (0.36, 0.26, 0.16),   # deep warm brown shadow
            (0.50, 0.56, 0.42),   # soft sage-green landscape distance
            (0.42, 0.48, 0.56),   # cool atmospheric recession
            (0.70, 0.58, 0.36),   # sienna-gold drapery
            (0.86, 0.78, 0.62),   # creamy half-light (below the golden peak)
        ],
        ground_color=(0.62, 0.52, 0.34),   # warm amber-ochre imprimatura
        stroke_size=5,
        wet_blend=0.65,      # high — seamless Florentine tonal transitions
        edge_softness=0.62,  # Leonardo-adjacent sfumato, but warmer and more grounded
        jitter=0.018,
        glazing=(0.52, 0.44, 0.28),    # warm amber unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Andrea del Sarto (1486–1530), called 'il pittore sanza errori' — the "
            "faultless painter — by Giorgio Vasari, achieved a seamless synthesis of "
            "the two dominant Florentine traditions: Fra Bartolommeo's monumental "
            "architectural clarity and Leonardo da Vinci's atmospheric sfumato.  "
            "Where Leonardo's sfumato dissolved forms into a smoky continuum, del "
            "Sarto's version retained the underlying clarity of volume — a warm, "
            "golden haze rather than Leonardo's cool smoke.  His flesh tones are "
            "among the most admired in the Italian tradition: a warm amber-ivory in "
            "the lights deepening through golden midtones to warm umber shadows, "
            "with a harmonious unity of temperature that prevents cold-light / "
            "warm-shadow contrast.\n\n"
            "His working method began with a warm amber-ochre imprimatura over which "
            "he built volume in monochromatic underlayers before introducing colour "
            "in transparent oil glazes.  The finished surface has the depth of "
            "stacked coloured glass: each glaze layer contributes chromatic warmth "
            "that accumulates into the characteristic golden luminosity.  His "
            "transitions are so smooth that Vasari's phrase implies not merely "
            "technical correction but natural inevitability — the tonal shift from "
            "light to shadow reads as the substance of flesh itself rather than "
            "applied paint.\n\n"
            "Unlike Leonardo, who used sfumato to dissolve the boundary between "
            "figure and ground, del Sarto maintained compositional clarity — his "
            "figures are atmospherically soft but spatially anchored.  Background "
            "landscapes use aerial perspective with a warmer palette (more ochre and "
            "sienna, less cool grey) than Leonardo, giving his atmospheric depth a "
            "golden, habitable quality.  The Madonna of the Harpies (1517), the "
            "Pietà (c. 1524), and the Portrait of a Young Man (c. 1517) demonstrate "
            "this: controlled warmth, perfect transitions, nothing superfluous."
        ),
        famous_works=[
            ("Madonna of the Harpies",           "1517"),
            ("Portrait of a Young Man",           "c. 1517"),
            ("Holy Family with Saint Catherine",  "c. 1529"),
            ("Pietà",                             "c. 1524"),
            ("The Annunciation",                  "c. 1512"),
        ],
        inspiration=(
            "Apply andrea_del_sarto_golden_sfumato_pass() to inject the characteristic "
            "'faultless' Florentine quality in three stages: (1) golden midtone warmth "
            "— skin pixels in the midtone band [0.45–0.80] receive R↑ and G↑ in a "
            "warm amber ratio (R stronger, G modest), enriching the ivory-gold without "
            "adding orange; (2) sfumato edge feathering — transition zones detected via "
            "local luminance gradient magnitude receive an additional Gaussian softening "
            "pass, pulling hard edges toward del Sarto's Leonardo-adjacent atmospheric "
            "quality; (3) colour harmony pull — pixels whose saturation exceeds a cap "
            "(0.85) are mildly desaturated toward the warm centre of the palette, "
            "preventing individual preceding passes from leaving chromatic outliers.  "
            "Opacity around 0.42–0.52 — del Sarto's effect is present but never "
            "intrusive; the 'faultless' quality comes from accumulated subtlety."
        ),
    ),

    "lorenzo_lotto": ArtStyle(
        artist="Lorenzo Lotto",
        movement="Venetian Renaissance / Venetian Psychological",
        nationality="Italian",
        period="c. 1480–1556",
        palette=[
            (0.88, 0.82, 0.72),   # warm ivory highlight — the lit face, slightly cooler than Titian
            (0.76, 0.68, 0.56),   # mid-tone flesh — warm ochre-ivory with a slight grey tension
            (0.54, 0.46, 0.38),   # warm-cool shadow flesh — cooler than Venetian norm, a grey-amber
            (0.28, 0.22, 0.16),   # near-black deep shadow — rich and warm but not Baroque void
            (0.38, 0.52, 0.46),   # cool muted green — Lotto's characteristic cool-green background tone
            (0.28, 0.34, 0.52),   # cool slate-blue shadow — the cool register that unsettles warmth
            (0.64, 0.44, 0.30),   # warm sienna-amber mid-drapery — the Venetian warmth inheritance
            (0.82, 0.76, 0.62),   # parchment ground glow — warm cream ground visible in thin passages
        ],
        ground_color=(0.58, 0.50, 0.36),    # warm mid-ochre Venetian imprimatura — slightly greyer than Titian
        stroke_size=5,
        wet_blend=0.45,                      # moderate — Venetian oil blending but less dissolved than Titian
        edge_softness=0.48,                  # moderate-soft — psychological crispness; not full sfumato
        jitter=0.022,
        glazing=(0.44, 0.46, 0.50),          # cool-neutral grey glaze (B>R) — introduces the grey-cool register
                                              # that distinguishes Lotto from warm-glazing Venetians (Titian: warm amber)
        crackle=True,
        chromatic_split=False,
        technique=(
            "Lotto occupies a singular position in the Venetian Renaissance: trained in the same "
            "tradition as Titian and Giorgione, but temperamentally and chromatically apart from "
            "them.  Where Titian unified his canvases with warm amber glazes and dissolved, sensual "
            "surfaces, Lotto introduced a pervasive cool chromatic anxiety — a grey-blue undertone "
            "beneath the warm flesh, a muted cool-green in backgrounds, a slight formal restlessness "
            "that prevents his portraits from ever fully settling into the comfortable grandeur of "
            "high Venetian portraiture.  This quality has led modern critics to describe his work as "
            "proto-psychological — his sitters seem caught at a moment of interior tension, their "
            "composure slightly effortful.  His most famous portraits — the Portrait of a Young Man "
            "with a Book (c. 1526), the Andrea Odoni (1527), and the Triple Portrait of a Goldsmith "
            "(c. 1530) — all share this quality: the sitter gazes out, but something in the cool "
            "half-light suggests they would rather not be seen.  "
            "Technically, Lotto worked with all the Venetian oil-glazing vocabulary but used it "
            "differently: his shadows cool toward grey-blue rather than warming toward umber; his "
            "backgrounds introduce chromatic discord (an unexpected muted green, a cold grey-stone, "
            "a curtain of impure blue) that prevents the compositional harmony Titian always achieved. "
            "His brushwork in the face is more deliberate and analytical than Titian's fluid touch — "
            "each form has a slight psychological edge.  The result is technically accomplished but "
            "emotionally unsettled: the chromatic signature of introversion rendered in paint."
        ),
        famous_works=[
            ("Portrait of a Young Man with a Book",     "c. 1526"),
            ("Portrait of Andrea Odoni",                "1527"),
            ("Triple Portrait of a Goldsmith",          "c. 1530"),
            ("The Annunciation",                        "c. 1534"),
            ("Man with a Golden Paw",                   "c. 1527"),
            ("Saint Jerome in the Wilderness",          "1506"),
        ],
        inspiration=(
            "Apply lotto_chromatic_anxiety_pass() to introduce Lotto's defining quality: the cool "
            "chromatic undertone that disturbs Venetian warmth without destroying it.  The pass "
            "operates in three stages: (1) cool flesh midtone injection — pixels in the midtone "
            "flesh band (warm ochre register) receive a gentle B↑ and R↓ push, introducing a grey "
            "tension beneath the warm surface; (2) eye-region chromatic intensification — a small "
            "elliptical zone around each eye receives a local contrast boost and a slight cool-blue "
            "shadow shift, heightening the psychological gaze quality Lotto's portraits are known for; "
            "(3) background color dissonance — non-skin background pixels in the midtone range receive "
            "a G↑ push (the cool muted green register) and a slight B↑, introducing the chromatic "
            "discord that prevents compositional ease.  The pass is subtle — opacity around 0.40–0.55 "
            "— because Lotto's effect is not dramatic but accumulative: by the end of the canvas, "
            "the sum of small cool deviations produces a portrait that reads as psychologically "
            "distinct from a Titian of the same sitter."
        ),
    ),

    # ── Jean-Baptiste-Siméon Chardin ──────────────────────────────────────────
    "chardin": ArtStyle(
        artist="Jean-Baptiste-Siméon Chardin",
        movement="French Rococo / Intimism",
        nationality="French",
        period="1720–1779",
        palette=[
            (0.74, 0.70, 0.58),   # warm ivory — signature quiet highlight
            (0.58, 0.54, 0.44),   # muted ochre midtone
            (0.42, 0.39, 0.32),   # warm umber shadow — never cold
            (0.65, 0.62, 0.53),   # warm gray — the atmospheric 'breath'
            (0.36, 0.38, 0.32),   # muted olive shadow accent
            (0.82, 0.79, 0.68),   # soft ivory near-light
        ],
        ground_color=(0.60, 0.57, 0.47),    # warm mid-gray imprimatura — Chardin often
        #                                     started on a warm neutral ground that
        #                                     'breathes' through every passage
        stroke_size=5,
        wet_blend=0.25,                      # low — Chardin's granular dabs stay distinct
        #                                     from each other; optical mixing happens on the
        #                                     retina, not on the palette. Wet blending would
        #                                     destroy the granular texture that is his
        #                                     defining technique.
        edge_softness=0.58,                  # moderate-soft; form is always legible through
        #                                     the grain — not sfumato dissolution, but not crisp
        jitter=0.028,
        glazing=(0.70, 0.67, 0.55),          # warm gray-gold unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Granular optical intimacy — Chardin applied small, individual dabs of paint "
            "side by side, allowing them to mix optically on the retina rather than on the "
            "palette.  The result is a quiet atmospheric 'granularity': surfaces appear to "
            "breathe with a warm, dusty luminosity that is distinct from both the smooth "
            "blending of sfumato and the systematic dots of Pointillism.  His palette is "
            "deliberately muted — warm grays, ochres, muted greens — yet the paintings read "
            "as luminous because the granular texture creates microscopic light-dark variation "
            "that mimics the way eyes perceive texture in diffuse illumination.  No drama, no "
            "impasto showmanship: the power is in the accumulation of quiet touches."
        ),
        famous_works=[
            ("The Ray",                         "1728"),
            ("The Copper Drinking Fountain",    "c. 1734"),
            ("Grace Before the Meal",           "1740"),
            ("The Young Draughtsman",           "c. 1737"),
            ("Self-Portrait with Spectacles",   "1771"),
            ("The Brioche",                     "1763"),
        ],
        inspiration=(
            "Apply chardin_granular_intimacy_pass() to introduce Chardin's defining optical "
            "texture: small granular color dabs scattered across the surface for retinal optical "
            "mixing, atmospheric muting pull toward the warm-gray palette center, and gentle "
            "luminance cap to remove specular blazing.  For an aged surface effect, also apply "
            "dry_granulation_pass() at low opacity — its pigment-separation simulation produces "
            "the dusty, tactile quality visible on Chardin's mature canvases under raking light.  "
            "Use low opacity (0.30–0.45) on both passes — the effect accumulates like dust "
            "settling on a still surface.  Chardin's intimacy is not achieved by a single "
            "dramatic gesture but by the patient layering of small decisions."
        ),
    ),


    # ── Théodore Géricault ────────────────────────────────────────────────────
    # ── Fra Filippo Lippi ─────────────────────────────────────────────────────
    "fra_filippo_lippi": ArtStyle(
        artist="Fra Filippo Lippi",
        movement="Florentine Early Renaissance / Quattrocento",
        nationality="Italian",
        period="1406–1469",
        palette=[
            (0.92, 0.83, 0.68),   # warm ivory highlight — the Lippi glow on brow and cheek
            (0.84, 0.70, 0.52),   # rose-ivory midtone — the pinkish warmth unique to Lippi flesh
            (0.68, 0.52, 0.36),   # warm amber shadow — never grey; always ochre-orange
            (0.48, 0.36, 0.24),   # deep warm umber — form-defining darks
            (0.60, 0.72, 0.54),   # soft muted green — drapery, background foliage
            (0.54, 0.64, 0.76),   # warm sky blue — the Lippi heavenly blue (lapis-azurite)
            (0.82, 0.74, 0.56),   # warm parchment — the neutral ground that breathes through
        ],
        ground_color=(0.72, 0.65, 0.50),    # warm buff/parchment imprimatura — Lippi worked
        #                                     on light-toned grounds over gesso that kept the
        #                                     luminosity of panel painting
        stroke_size=5,
        wet_blend=0.22,                      # low — Lippi's early tempera-influenced technique
        #                                     uses careful, distinct small marks; the transition
        #                                     to oil brought more blending but retained the
        #                                     careful form-building of tempera
        edge_softness=0.52,                  # moderate — softer than his Quattrocento
        #                                     contemporaries (Masaccio's hard outlines), but
        #                                     not yet the full sfumato dissolution of Leonardo
        jitter=0.018,
        glazing=(0.82, 0.74, 0.56),          # warm parchment glaze — unifies the warm light
        crackle=True,
        chromatic_split=False,
        technique=(
            "Fra Filippo Lippi (c. 1406–1469) was the single most important bridge figure "
            "between Masaccio's austere sculptural realism and Leonardo's sfumato lyricism.  "
            "Trained in the Carmelite order alongside the influence of Masaccio's revolutionary "
            "work in the Brancacci Chapel, Lippi absorbed the new naturalism — the sense of "
            "weight, volume, and psychological presence — but transformed it through a "
            "temperament that was, at its core, tender rather than heroic.  Where Masaccio "
            "rendered the human body with the gravity of ancient sculpture, Lippi gave his "
            "figures an intimacy and gentleness — a quality contemporaries and later writers "
            "called 'tenerezza' — that made them feel like real, specific people rather than "
            "idealized archetypes.\n\n"
            "His technical signature is a warm, softly luminous rendering of flesh that "
            "anticipates Correggio and Leonardo.  Unlike the cool, silver-grey darks of some "
            "contemporaries, Lippi's shadows are always warm — ochre, amber, burnt sienna — "
            "and his highlights are a warm ivory that transitions through a distinctive "
            "rose-inflected midtone.  This pinkish-ivory warmth, especially in the faces of "
            "his Madonnas, is the quality that makes his figures appear to glow with an "
            "interior life.  It is not dramatic illumination; it is the quiet radiance of "
            "a face seen in warm afternoon light through a thin curtain.\n\n"
            "His use of line is also transitional.  Early Quattrocento painting treated the "
            "contour as a firm boundary — the edge of a form was drawn before it was filled.  "
            "Lippi began to soften this contour, allowing the form to dissolve slightly at "
            "the edge into the surrounding space, a proto-sfumato that his pupil Botticelli "
            "would stylise into decorative linearity, and his indirect pupil Leonardo would "
            "develop into full atmospheric dissolution.  Lippi's edges are soft without being "
            "lost — they read as the edge of a rounded form in gentle diffuse light, not as "
            "a drawn boundary.\n\n"
            "Key works: the Annunciation in San Lorenzo (Florence), the Coronation of the "
            "Virgin (Uffizi), the Barbadori Altarpiece, and above all the Madonna and Child "
            "with Angels (Uffizi, c. 1465), where the famous direct gaze of the Madonna and "
            "the mischievous naturalism of the angels demonstrate his unique fusion of "
            "spiritual subject matter and vivid human observation.  The story that the model "
            "for the Madonna was Lucrezia Buti, the nun with whom he had an affair (and who "
            "became the mother of Filippino Lippi), is almost certainly true — the faces in "
            "his late works have a specific, intimate quality that speaks of real looking at "
            "a real person.\n\n"
            "His influence ran directly to Botticelli (his pupil), to Filippino Lippi (his "
            "son), and, through the example of his handling of flesh and soft light, to "
            "Leonardo da Vinci, who must have studied his work closely in Florence.  The "
            "warm pinkish warmth of Leonardo's early flesh tones — the Benois Madonna, the "
            "Ginevra de' Benci — owes a debt to Lippi's tenerezza that is rarely acknowledged."
        ),
        famous_works=[
            ("Madonna and Child with Angels (Uffizi)",  "c. 1465"),
            ("Annunciation, San Lorenzo",               "c. 1443"),
            ("Coronation of the Virgin",                "1441–1447"),
            ("Barbadori Altarpiece",                    "c. 1437"),
            ("Frescoes, Prato Cathedral",               "1452–1466"),
            ("Adoration of the Magi (Uffizi)",          "c. 1496"),
        ],
        inspiration=(
            "Apply fra_filippo_lippi_tenerezza_pass() to introduce the Quattrocento master's "
            "defining quality: the warm, rose-ivory pinkish luminosity of flesh, the gentle "
            "interior glow that reads as an almost spiritual tenderness.  The pass warms the "
            "flesh midtones toward rose-ivory, adds a very soft internal luminous lift in the "
            "lightest skin passages, and gently quiets the background by slightly cooling and "
            "desaturating it — reinforcing the figure-ground separation that Lippi always "
            "maintained.  Use at low-to-moderate opacity (0.30–0.48): Lippi's tenerezza is "
            "a quality of feeling, not a dramatic effect.  It accumulates in repeated "
            "contemplation, not in a single forceful gesture."
        ),
    ),


    "perugino": ArtStyle(
        artist="Pietro Perugino",
        movement="Umbrian / High Renaissance (early)",
        nationality="Italian",
        period="c. 1446–1523",
        palette=[
            (0.91, 0.84, 0.70),   # warm ivory highlight — Perugino's luminous pale flesh
            (0.82, 0.70, 0.54),   # peach-ivory midtone — the serene warm register of his skin
            (0.62, 0.56, 0.50),   # cool silvery shadow — Perugino's shadows are cooler than
            #                       Leonardo's; the silver-grey that gives his faces their
            #                       serene idealized quality
            (0.38, 0.34, 0.30),   # cool warm mid-dark — figure ground transition
            (0.54, 0.68, 0.82),   # luminous cerulean sky — the Umbrian blue that defines
            #                       Perugino's landscapes: pale, high, almost bleached
            (0.72, 0.78, 0.72),   # soft blue-green midground — Umbrian hills receding
            (0.34, 0.46, 0.28),   # muted grass green — near-ground landscape
            (0.78, 0.68, 0.52),   # warm parchment neutral — the underlying ground tone
        ],
        ground_color=(0.78, 0.72, 0.58),    # warm buff-ivory imprimatura — Perugino worked
        #                                     on light, warm-toned grounds that contributed
        #                                     luminosity to his pale, high-key passages
        stroke_size=4,
        wet_blend=0.38,                      # moderate — Perugino's surfaces are smooth but
        #                                     not deeply blended; he achieved smoothness through
        #                                     careful layering rather than Leonardo's sfumato
        #                                     dissolution; his edges are soft without being lost
        edge_softness=0.55,                  # moderate — softer than Flemish contemporaries,
        #                                     less dissolved than Leonardo; the figure reads as
        #                                     clearly bounded but without hard contours
        jitter=0.014,
        glazing=(0.80, 0.76, 0.62),          # pale warm ivory glaze — unifies the light ground
        #                                     with the high-key flesh; reinforces the luminous,
        #                                     open quality of his surfaces
        crackle=True,
        chromatic_split=False,
        technique=(
            "Pietro Perugino (Pietro di Cristoforo Vannucci, c. 1446–1523) was for a "
            "decade and a half the most famous painter in Italy — the master Raphael chose "
            "as his teacher, the artist whose serene, spacious style defined what the Italian "
            "High Renaissance portrait should look and feel like.  He trained in Florence, "
            "almost certainly in the orbit of Verrocchio's workshop — the same environment "
            "that shaped Leonardo da Vinci — and the influence of that shared formation is "
            "visible in both painters' approach to flesh and soft light.\n\n"
            "Perugino's defining quality is serenity.  His faces have an expression that "
            "contemporaries called 'dolcezza' — sweetness — and that later critics, with "
            "less charity, called saccharine.  His Madonnas and saints look out from their "
            "pictures with an expression of quiet, inward composure that never quite resolves "
            "into a specific emotion.  This was not a failure of psychological observation; "
            "it was a deliberate aesthetic — the face of ideal humanity in a state of "
            "spiritual grace, beyond ordinary perturbation.  The 'Perugino face' — the smooth "
            "oval, the high forehead, the slightly downcast or gently forward gaze, the small "
            "closed lips with their faint upward curve — was so recognisable and so admired "
            "that it became a cultural type, copied and adapted across decades.\n\n"
            "His handling of landscape is equally distinctive.  Behind his figures, extending "
            "into great depth on either side, lies the Umbrian countryside as he imagined it "
            "should be: spacious, airy, and luminous.  The sky is always very pale — almost "
            "white at the horizon, deepening to a clear cerulean above — and the distant hills "
            "are rendered in the soft blue-grey of aerial perspective.  Trees are placed with "
            "careful spacing; paths wind into the distance; the whole scene has a quality of "
            "geometric order and gentle air that is quite different from the geological drama "
            "of Leonardo's backgrounds.  Perugino's landscape is paradise — organized, "
            "luminous, and inhabited only by the quiet of early morning.\n\n"
            "Technically, his flesh is among the smoothest of his generation.  He achieved "
            "this smoothness not through Leonardo's sfumato (the wet blending of edges and "
            "forms into one another) but through a careful, patient layering of thin paint "
            "over a warm light ground — building up the flesh by adding glazes and scumbles "
            "that kept the surface luminous rather than opaque.  His shadows are cooler and "
            "more silvery than Leonardo's warm umber darks: the shadow side of a Perugino "
            "face has a gentle grey-violet cast that reads as the cool side of warm diffuse "
            "light rather than the deep warm shadow of Leonardesque chiaroscuro.  This "
            "cool-shadow / warm-light system gives his figures their quality of being "
            "suffused by open, bounced, ambient light — the light of Umbria on a pale "
            "morning — rather than the directed drama of a single light source.\n\n"
            "His greatest works include the fresco of Christ Delivering the Keys to Saint "
            "Peter (Sistine Chapel, 1481–82), the Collegio del Cambio frescoes in Perugia "
            "(1499–1500), and numerous altarpieces and devotional Madonnas.  His most direct "
            "legacy is Raphael (Raffaello Sanzio), who entered his workshop in Città di "
            "Castello around 1501 and absorbed the Perugino facial type, spatial clarity, "
            "and serene idealism before transforming them into the deeper psychological "
            "engagement of his Roman masterpieces.  Perugino's influence is also visible in "
            "Leonardo's early Florentine work: the two men moved in the same world, and the "
            "Mona Lisa's landscape — its pale, receding aerial distance — owes something to "
            "the Umbrian convention of the open, luminous background that Perugino helped "
            "define and popularise."
        ),
        famous_works=[
            ("Christ Delivering the Keys to Saint Peter",  "1481–1482"),
            ("The Pietà",                                   "c. 1495"),
            ("Apollo and Marsyas",                          "c. 1495"),
            ("Collegio del Cambio Frescoes (Perugia)",      "1499–1500"),
            ("The Marriage of the Virgin (Sposalizio)",     "1499–1504"),
            ("The Combat of Love and Chastity",             "1505"),
        ],
        inspiration=(
            "Apply perugino_serene_grace_pass() to introduce Perugino's defining tonal "
            "and atmospheric qualities in three stages: (1) sky luminosity bleaching — lift "
            "and cool the upper background zone toward Perugino's characteristic pale "
            "cerulean-ivory sky, desaturating the upper background and nudging it toward a "
            "luminous blue-white; (2) cool silvery shadow harmonization — in dark-to-midtone "
            "passages of the figure, apply a very gentle grey-violet shift that replicates "
            "Perugino's cool-shadow convention, separating the figure's shadow side from the "
            "warm ground and giving the face the serene, ambient-light quality of Umbrian "
            "open-air illumination; (3) midtone serene smoothing — a very subtle Gaussian "
            "harmonization of the mid-luminance zone that evens out local contrast in the "
            "flesh midtones, producing Perugino's characteristic porcelain-smooth surfaces.  "
            "Use at low-to-moderate opacity (0.30–0.45): Perugino's serenity is quiet and "
            "accumulative, not dramatic."
        ),
    ),


    "gericault": ArtStyle(
        artist="Théodore Géricault",
        movement="French Romanticism",
        nationality="French",
        period="1791–1824",
        palette=[
            (0.82, 0.68, 0.46),   # warm ivory-ochre — the sudden heroic highlight
            (0.60, 0.44, 0.26),   # mid-flesh amber — raw, living skin in dramatic light
            (0.38, 0.26, 0.14),   # warm umber shadow — the deep warm dark that defines form
            (0.14, 0.10, 0.07),   # near-black ground — Géricault's void, warm not cool
            (0.48, 0.34, 0.20),   # mid-brown drapery — the turbulent fabric of history
            (0.72, 0.52, 0.30),   # amber highlight — caught on impasto ridges in storm light
            (0.26, 0.20, 0.14),   # dark warm shadow — the penumbra of Romantic chiaroscuro
            (0.88, 0.76, 0.54),   # brilliant highlight — the sudden light eruption on flesh
        ],
        ground_color=(0.18, 0.14, 0.09),    # dark warm near-black imprimatura — Géricault began
        #                                     on dark grounds (unlike the Baroque cool blacks);
        #                                     his darkness is always warm, organic, threatening
        stroke_size=10,
        wet_blend=0.68,                      # high — vigorous wet-on-wet impasto; Géricault
        #                                     worked alla prima with thick paint, letting forms
        #                                     merge where they meet in the shadow passages
        edge_softness=0.72,                  # moderate-high — turbulent dissolution: edges
        #                                     dissolve through movement and drama, not sfumato
        jitter=0.040,                        # high — Géricault's brushwork is visibly forceful;
        #                                     individual strokes carry directional energy
        glazing=(0.44, 0.32, 0.14),          # deep warm amber-umber glaze — unifies the dark
        #                                     ground with the impasto highlights; the glaze
        #                                     pools in the recesses, giving depth to shadows
        crackle=True,
        chromatic_split=False,
        technique=(
            "Théodore Géricault (1791–1824) was the founding figure of French Romanticism and "
            "one of the most technically audacious painters of his era.  Where Neoclassicism — the "
            "reigning style of David and his followers — sought cool rational clarity, heroic "
            "restraint, and polished academic surfaces, Géricault pursued raw turbulent power: "
            "the unbridled energy of horses, the visceral horror of real catastrophe, the psychological "
            "intensity of extreme human states.  He studied anatomy in the Paris morgue.  He "
            "interviewed survivors of the Raft of the Medusa disaster.  He painted portraits of "
            "patients in the Salpêtrière asylum not as curiosities but as full human beings with "
            "interior lives.  His art is the art of confrontation.\n\n"
            "His technique was as dramatic as his subjects.  He worked on dark warm grounds — "
            "not the cool black gesso of some contemporaries but a warm near-black composed of "
            "burnt umber, black, and a touch of raw sienna — that allowed the shadows to remain "
            "warm and organic rather than cold and dead.  Over this ground he applied paint in "
            "thick, vigorous impasto, building up the lit passages with confident directional "
            "marks that read as turbulent energy.  The transition from shadow to light is "
            "sudden, not gradual: Géricault's chiaroscuro has the theatrical drama of Caravaggio "
            "but with a Romantic violence and agitation that Caravaggio, for all his power, "
            "never pursued.  His darks are warm and deep; his lights erupt with almost shocking "
            "force.  Between them, the transition zone is not a soft sfumato passage but a "
            "turbulent, active boundary — the penumbra of storm light, where form is known but "
            "not settled.\n\n"
            "The Officer of the Imperial Guard Charging (1812), The Wounded Cuirassier (1814), "
            "The Raft of the Medusa (1818–19), and the Portraits of the Insane (1819–22) are "
            "the canonical works.  Each demonstrates the same technical signature: warm near-"
            "black void, sudden warm light, thick directional impasto, and an emotional urgency "
            "that makes every surface feel like it is in motion.  His palette is tightly "
            "constrained — predominantly warm earth tones (ochre, sienna, umber, ivory black) "
            "with the lights never cool and the darks never cold.  This palette restraint, "
            "combined with the turbulent application, is what gives Géricault's paintings their "
            "concentrated intensity: there is nowhere for the eye to rest, no decorative relief "
            "from the drama."
        ),
        famous_works=[
            ("Officer of the Imperial Guard Charging",  "1812"),
            ("The Wounded Cuirassier Leaving the Field", "1814"),
            ("The Raft of the Medusa",                  "1818–1819"),
            ("Portrait of a Kleptomaniac",              "c. 1820"),
            ("Portrait of a Man Suffering from Delusions of Military Command", "c. 1822"),
            ("The Derby at Epsom",                      "1821"),
        ],
        inspiration=(
            "Apply gericault_romantic_turbulence_pass() to introduce Géricault's defining "
            "chromatic and tonal signature in three stages: (1) shadow depth enrichment — push "
            "dark pixels (luminance < 0.32) toward warm near-black by reducing blue and green "
            "channels while preserving the warm red-umber register; Géricault's shadows are "
            "never cool grey, always warm dark; (2) turbulent highlight contrast — apply "
            "directional luminance variance in the mid-tone boundary zone (0.32–0.65 luminance) "
            "that creates the impression of impasto ridges catching storm light; this introduces "
            "the Romantic sense of surface energy without the sfumato tradition's dissolution; "
            "(3) dramatic contrast intensification — local contrast boost in the mid-range using "
            "a sigmoid tone curve, sharpening the division between the dark passages and the "
            "sudden warm lights.  The pass should be used at moderate opacity (0.38–0.52) — "
            "Géricault's drama is not subtle, but the portrait context requires that the existing "
            "tonal balance is not entirely overridden.  The warm shadow recovery is the most "
            "important single contribution: removing any residual cool-grey cast from shadow "
            "passages and replacing it with Géricault's characteristic warm umber void."
        ),
    ),

    "signorelli": ArtStyle(
        artist="Luca Signorelli",
        movement="Umbrian Renaissance",
        nationality="Italian",
        period="c. 1445–1523",
        palette=[
            (0.82, 0.65, 0.42),   # warm ochre flesh — Signorelli's lit figure surfaces
            (0.58, 0.40, 0.22),   # mid-tone umber — the strong modelled shadow on flesh
            (0.20, 0.15, 0.09),   # deep warm near-black — the structural shadow void
            (0.46, 0.58, 0.36),   # muted olive-green — drapery and foliage accents
            (0.62, 0.34, 0.22),   # burnt sienna — the vigorous drapery mid-tone
            (0.72, 0.80, 0.72),   # cool silver-sage — the pale sky and distant terrain
            (0.88, 0.78, 0.55),   # ivory highlight — brilliant lit ridge on muscle
            (0.36, 0.28, 0.18),   # dark warm umber — the penumbra of sculptural relief
        ],
        ground_color=(0.42, 0.32, 0.18),    # warm mid-tone sienna imprimatura —
        #                                     Signorelli worked on a mid-value warm ground
        #                                     that allowed him to model both upward into
        #                                     highlights and downward into shadow without
        #                                     losing surface unity; unlike Leonardo's
        #                                     warm-amber glaze or Géricault's near-black
        #                                     void, his ground is a moderate warm brown
        stroke_size=8,
        wet_blend=0.52,                      # moderate — Signorelli's surfaces are smooth
        #                                     but not sfumato-dissolved; he blended within
        #                                     each passage but kept contours legible and firm
        edge_softness=0.28,                  # low — Signorelli's defining quality is the
        #                                     clarity of his contours; where Leonardo
        #                                     dissolved edges into atmospheric haze,
        #                                     Signorelli drew them firmly in paint,
        #                                     giving figures a sculptural, bas-relief quality
        jitter=0.025,                        # moderate — visible brushwork energy without
        #                                     the chaos of Géricault or the Expressionists;
        #                                     his surfaces have directional muscle-following
        #                                     marks that read as anatomical authority
        glazing=(0.55, 0.40, 0.20),          # warm sienna-amber glaze — unifies flesh
        #                                     passages across the warm mid-tone ground;
        #                                     cooler than Leonardo's amber, more golden
        #                                     than Géricault's deep umber
        crackle=True,
        chromatic_split=False,
        technique=(
            "Luca Signorelli (c. 1445/50–1523) was one of the most audaciously original "
            "painters of the Italian fifteenth century — and one of the least celebrated in "
            "proportion to his actual influence.  He was a native of Cortona, trained almost "
            "certainly in the workshop of Piero della Francesca (whose cool mineral clarity and "
            "geometrical rigour he absorbed and then dramatically transformed), and subsequently "
            "active across Umbria, Tuscany, and Rome.  Vasari, who admired him enormously, called "
            "him 'the master of Michelangelo'; and while the precise relationship between the two "
            "men is contested by modern scholars, Signorelli's influence on the Sistine Chapel "
            "ceiling — its muscular, foreshortened nudes, its dynamic contour authority, its "
            "sense of the human body as an instrument of spiritual drama — is visible and direct.\n\n"
            "What distinguishes Signorelli from his Umbrian contemporaries — Perugino, Pinturicchio, "
            "the young Raphael — is his absolute commitment to the human body as the primary vehicle "
            "of meaning.  Where Perugino sought serene composure in the face and the landscape, "
            "Signorelli sought anatomical drama in the figure.  His bodies are muscular, torsional, "
            "and explicitly three-dimensional: they twist, strain, fall, and rise in ways that no "
            "Italian painter before him had attempted at such systematic scale.  The great frescoes "
            "of the Chapel of San Brizio in Orvieto Cathedral (1499–1504) — the Last Judgement "
            "cycle with its apocalyptic mass of naked, writhing, damned souls — are the culmination "
            "of this project: a vast experiment in depicting the human body under extreme physical "
            "and spiritual duress.\n\n"
            "Technically, Signorelli's most distinctive quality is the clarity of his contours.  "
            "He drew in paint — that is, he described form through firm, clear edges rather than "
            "the sfumato dissolve of Leonardo or the tonal merging of Giorgione.  His outlines are "
            "not calligraphic in the Botticelli manner (curved, lyrical, decorative) but structural: "
            "they follow the actual geometry of muscle, bone, and tendon, so that the edge of a "
            "Signorelli limb reads as the boundary between one anatomical plane and the next.  This "
            "makes his figures feel carved — solid, bas-relief objects existing in real space — "
            "rather than painted illusions.  His shadows are deep and warm (umber, sienna, near-black) "
            "and transition to the lights through a relatively compressed mid-tone range, giving "
            "his modelling a dramatic sculptural relief that contrasts sharply with Perugino's "
            "diffuse, ambient-light gentleness.\n\n"
            "His palette is characteristically Umbrian in its warm earth-tone foundation (ochre, "
            "sienna, umber) but distinguished by unusually vivid chromatic accents — the intense "
            "blue of a sky, the saturated red of a drapery, the sudden green of foliage — that give "
            "his compositions a jewel-like colour energy within a predominantly warm ground.  He "
            "applied his colour with directional, form-following strokes that read as both painterly "
            "and architectonic: each mark describes a surface plane, not just a local tone.\n\n"
            "Among his other significant works are the fresco of the Testament and Death of Moses "
            "(Sistine Chapel, c. 1482), the Holy Family Tondo (Uffizi, c. 1490–95), and numerous "
            "altarpieces for Umbrian and Tuscan patrons.  His portraits, though fewer in number than "
            "his narrative works, display the same sculptural authority and penetrating gaze-direction "
            "that characterise his figure style."
        ),
        famous_works=[
            ("Last Judgement Frescoes, Chapel of San Brizio, Orvieto",  "1499–1504"),
            ("The Damned Cast into Hell",                                "1499–1504"),
            ("The Resurrection of the Flesh",                           "1499–1504"),
            ("Holy Family Tondo (Medici Tondo)",                        "c. 1490–1495"),
            ("Testament and Death of Moses (Sistine Chapel)",           "c. 1482"),
            ("Portrait of a Lawyer",                                    "c. 1490–1500"),
        ],
        inspiration=(
            "Apply signorelli_sculptural_vigour_pass() to introduce Signorelli's defining "
            "anatomical and chromatic qualities in three stages: (1) contour clarification — "
            "a gentle unsharp-mask edge-sharpening pass targeted at mid-luminance boundaries, "
            "which replicates Signorelli's characteristic clear painted contour that gives his "
            "figures their sculptural, bas-relief quality; (2) shadow depth modelling — push "
            "mid-dark pixels (luminance 0.10–0.42) toward warm umber by enriching the red-brown "
            "register and reducing the blue channel, deepening the sculptural shadow relief that "
            "distinguishes Signorelli's modelling from Perugino's softer ambient-light approach; "
            "(3) chromatic accent lift — in saturated mid-tone regions (saturation > 0.25), apply "
            "a gentle Sigmoid-curve saturation boost that replicates the vivid colour energy of "
            "Signorelli's drapery and landscape accents against the warm earth-tone foundation.  "
            "Use at moderate opacity (0.35–0.50): Signorelli's vigour is muscular and direct, "
            "not accumulated gradually like Perugino's serenity."
        ),
    ),

    # ── Rosalba Carriera ───────────────────────────────────────────────────────
    "rosalba_carriera": ArtStyle(
        artist="Rosalba Carriera",
        movement="Venetian Rococo / Pastel Portraiture",
        nationality="Italian",
        period="1700–1757",
        palette=[
            (0.95, 0.85, 0.78),   # luminous ivory-pink flesh — Carriera's signature
            (0.88, 0.72, 0.68),   # warm rose mid-flesh — blushed cheek warmth
            (0.80, 0.82, 0.88),   # cool silver-lavender shadow — pastel cool shade
            (0.92, 0.88, 0.82),   # pearlescent warm white — highlight bloom
            (0.72, 0.78, 0.85),   # pale cerulean-grey — atmospheric cool distance
            (0.85, 0.70, 0.55),   # amber-peach — dress / costume warmth
            (0.60, 0.65, 0.72),   # muted steel-blue — background recess
        ],
        ground_color=(0.82, 0.78, 0.72),    # pale warm vellum — Carriera worked
        #                                     on prepared vellum or fine paper, giving
        #                                     her an inherently light, warm ground
        #                                     that interacts optically with the soft
        #                                     pastel layers above it
        stroke_size=4,
        wet_blend=0.88,                      # very high — pastel is pressed and blended
        #                                     with fingers, torchons, and soft leather
        #                                     stumps; the result is an almost seamless
        #                                     chromatic transition with no visible
        #                                     individual marks in the flesh zones
        edge_softness=0.90,                  # very high — Carriera's faces dissolve
        #                                     at their edges into soft vignette-like
        #                                     halos of tone; there are no hard outlines,
        #                                     only gradations so gentle they read as
        #                                     atmosphere rather than drawing
        jitter=0.012,                        # very low — the powdery medium creates
        #                                     an inherent optical softness; individual
        #                                     stroke jitter is subsumed into the overall
        #                                     chromatic fusion
        glazing=None,                        # pastel has no glaze layer — the optical
        #                                     luminosity comes from the ground reflecting
        #                                     through the translucent pigment dust;
        #                                     the equivalent effect is the pearlescent
        #                                     pale ground interacting with cool shadows
        crackle=False,                       # pastel does not crack — it is a dry
        #                                     medium; the aged-paper analogue is
        #                                     a very faint grain texture
        chromatic_split=False,
        technique=(
            "Rosalba Carriera (1673–1757) was the most celebrated pastellist of the eighteenth "
            "century and one of the decisive figures in the Rococo revolution in portraiture.  "
            "Born in Venice, she began her career producing miniature portraits on ivory — a "
            "practice she effectively invented, substituting ivory for the traditional vellum "
            "support to achieve a more luminous, warm-reflective ground — before discovering "
            "that the pastel medium offered a freedom of chromatic fusion and surface delicacy "
            "that no other portable medium could match.  By the 1700s she was the most sought-"
            "after portrait artist in Europe, receiving commissions from the courts of France, "
            "Austria, and Poland, and in 1720 she made a triumphant visit to Paris that "
            "introduced pastel portraiture to the French artistic world and influenced an entire "
            "generation of French Rococo painters — most decisively Quentin de La Tour and "
            "Jean-Baptiste Perronneau.  In 1720 she was elected to the Académie Royale de "
            "Peinture et de Sculpture in Paris, the first woman from outside France to receive "
            "that honour.\n\n"
            "Her technique is defined by an extraordinary control of the pastel medium's unique "
            "optical properties.  Pastel pigment sits on the tooth of the support as a fine "
            "dry powder; it scatters and reflects light in a manner unlike any other painting "
            "medium — not the deep, transmissive glow of oil glazes, nor the opaque matte of "
            "fresco or tempera, but a luminous, slightly hazy brilliance as if the colour itself "
            "were internally lit.  Carriera exploited this property with consummate skill.  "
            "Her flesh tones are built up through many thin, successive layers of gently "
            "blended pastel — warm ivory-pinks at the surface, with cool lavender-grey "
            "shadows pressed deep into the support so they read through the warm overstrokes "
            "as simultaneously present and recessed.  The result is a skin surface of "
            "extraordinary illusionistic delicacy: it appears soft, slightly translucent, "
            "and subtly alive in a way that oil paint cannot replicate without elaborate "
            "glazing sequences.\n\n"
            "Her highlights are pearlescent rather than specular.  Where Vermeer gave his "
            "subjects crisp diffused-light pearls and Rembrandt's impasto highlights read as "
            "physical paint ridges, Carriera's lights are feathered, powdery, and diffused "
            "across a slightly wider area — less a point of maximum reflection than a gentle "
            "bloom of brightness, as if the skin itself were softly luminous.  She avoided "
            "the dramatic chiaroscuro of the Baroque tradition entirely: her light sources "
            "are invariably soft, frontal, and slightly diffused, creating the impression of "
            "interior studio light rather than theatrical stage illumination.\n\n"
            "Her backgrounds are handled with supreme economy: typically a neutral cool-grey "
            "or warm-beige tone, slightly varied in density so as to suggest atmospheric depth "
            "without competing with the face.  She painted costumes and textiles with great "
            "virtuosity — the shimmer of silk, the softness of fur, the lightness of lace — "
            "but always subordinated them to the radiance of the face.  Her sitters appear to "
            "inhabit a slightly dreamy, stylised world: the Rococo ideal of feminised elegance "
            "and social grace made visible in light itself.\n\n"
            "Her principal works are distributed across the major European collections: the "
            "Gallerie dell'Accademia in Venice, the Gemäldegalerie in Dresden, the Uffizi "
            "in Florence, the Royal Collection in Windsor, and numerous private collections.  "
            "Her self-portraits — of which she produced several, in the Uffizi tradition of "
            "artists' self-portraiture — are remarkable for their unsentimental self-awareness "
            "combined with the same feathery luminosity she brought to every sitter."
        ),
        famous_works=[
            ("Self-Portrait as Winter", "c. 1731"),
            ("Portrait of a Young Lady", "c. 1720–1730"),
            ("Portrait of Antoine Watteau", "c. 1721"),
            ("Girl with a Dove", "c. 1710–1720"),
            ("Portrait of Charles of Austria as a Child", "c. 1730"),
            ("Self-Portrait with a Portrait of Her Sister", "c. 1715"),
        ],
        inspiration=(
            "Apply carriera_pastel_glow_pass() to introduce Rosalba Carriera's defining "
            "optical signature in three stages: (1) pearlescent skin brightening — a "
            "gentle luminance lift in the upper mid-tones (luminance 0.55–0.85) that "
            "replicates the pale, luminous bloom of pastel pigment on a warm vellum ground; "
            "warm pixels in this zone receive a slight pinkish-ivory brightening while cool "
            "pixels shift gently toward lavender-grey, mimicking the warm-cool layering "
            "sequence of real pastel flesh; (2) highlight diffusion — instead of Vermeer's "
            "crisp pearl dots or Rembrandt's impasto ridges, Carriera's highlights are soft "
            "halos; apply a gentle Gaussian bloom (sigma 2.5–4px) to the highest-luminance "
            "pixels (> 0.88), blending the specular peaks outward into a feathery radiance "
            "rather than a crisp point; (3) background vignette cooling — the background zone "
            "outside the figure mask receives a gentle shift toward cool blue-grey lavender, "
            "replicating Carriera's characteristic neutral cool-toned backgrounds that make "
            "the warm, luminous face advance.  Use at moderate opacity (0.28–0.42): Carriera's "
            "effect is cumulative and delicate; a heavy application would compromise the "
            "sfumato depth built up by earlier sessions."
        ),
    ),

    # ── James McNeill Whistler ─────────────────────────────────────────────────
    "whistler": ArtStyle(
        artist="James McNeill Whistler",
        movement="American Tonalism / Aestheticism",
        nationality="American-British",
        period="1855–1903",
        palette=[
            (0.56, 0.57, 0.62),   # cool silver-grey — dominant tonal key (nocturnes)
            (0.82, 0.80, 0.78),   # pale warm silver — lit figure surfaces
            (0.28, 0.30, 0.36),   # dark blue-grey — deep nocturne shadow
            (0.70, 0.68, 0.72),   # silver-lavender mid-tone — Whistler's characteristic
            (0.18, 0.22, 0.32),   # deep nocturne blue — the Thames at night
            (0.88, 0.82, 0.68),   # warm ivory — figure highlight (Arrangement paintings)
            (0.42, 0.44, 0.50),   # steel-blue mid-grey — cool tonal anchor
        ],
        ground_color=(0.58, 0.58, 0.62),    # cool silver-grey prepared board — Whistler
        #                                     primed his mahogany panels and canvases with
        #                                     a cool grey ground that unified the tonal key
        #                                     before a single stroke of colour was applied
        stroke_size=4,
        wet_blend=0.72,
        edge_softness=0.80,
        jitter=0.018,
        glazing=(0.55, 0.56, 0.60),          # cool neutral glaze — grey rather than amber
        crackle=True,
        chromatic_split=False,
        technique=(
            "James McNeill Whistler (1834–1903) occupies a singular position in the "
            "history of Western painting as the artist who most fully translated the "
            "philosophy of 'art for art's sake' — l'art pour l'art — into a working "
            "pictorial method.  Born in Lowell, Massachusetts, trained briefly at West "
            "Point and at the École des Beaux-Arts in Paris, he spent most of his "
            "productive life in London and Paris, where he moved between the realist "
            "circle of Courbet, the Impressionist orbit of Monet, and the Japoniste "
            "enthusiasm that swept the European avant-garde after the opening of "
            "Japan in the 1850s.  He was, in the fullest sense, an international "
            "artist who belonged to no single national tradition and refused to be "
            "confined by any single school.\n\n"
            "His defining theoretical contribution was the insistence that a painting "
            "should be experienced as a formal object — an arrangement of colour, tone, "
            "and line — rather than as a vehicle for narrative, moral instruction, or "
            "social commentary.  He named his paintings accordingly: not 'Seascape "
            "with Boats' but 'Harmony in Blue and Silver'; not 'Portrait of My Mother' "
            "but 'Arrangement in Grey and Black No. 1'.  The musical titles were not "
            "affectation but doctrine: he believed that painting, like music, could "
            "produce purely aesthetic emotion through the formal relationships of its "
            "materials, independent of what those materials happened to depict.\n\n"
            "His technical practice was equally distinctive.  He prepared his boards "
            "and canvases with a cool grey ground that unified the entire tonal key "
            "before a brushstroke was applied.  He then worked with a preparation he "
            "called the 'sauce' — oil paint diluted to extreme fluidity with "
            "turpentine — which allowed him to wipe away, layer, and restate the "
            "image many times without losing the atmospheric unity of the ground.  "
            "The result was a surface where values inhabit a narrow tonal range, "
            "graduated from the dominant grey key through carefully placed accents of "
            "darker and lighter tone.  Nothing was strident, nothing was forced; "
            "the whole surface breathed together as a tonal chord.\n\n"
            "The 'Nocturnes' — his night paintings of the Thames, Cremorne Gardens, "
            "and the Venice lagoon — take this tonal philosophy to its limit.  Working "
            "from memory after observing a scene, he laid a fluid dark ground, then "
            "floated lighter tonal accents across it with a wide decorator's brush.  "
            "The result is paintings where the pictorial information is barely "
            "sufficient to read — a dark horizontal band, a suggestion of reflected "
            "light in water, a distant burst of fireworks — yet which communicate an "
            "overwhelming atmosphere of night, stillness, and the dissolution of form "
            "in darkness.  Edges are not so much softened as eliminated: figures, "
            "bridges, and trees dissolve into their atmospheric ground as completely "
            "as any Leonardo sfumato, but through tonal key management rather than "
            "blended gradients.\n\n"
            "His portrait practice shows the same philosophy applied to the figure: "
            "the sitter's face and hands emerge from a near-monochromatic ground, "
            "with the surrounding costume and environment dissolved into the same "
            "tonal register as the background.  The radical tonal economy of "
            "'Arrangement in Grey and Black No. 1' — later universally called "
            "'Whistler's Mother' — represents perhaps the most disciplined "
            "application of tonal key in the history of formal portraiture.\n\n"
            "His deep engagement with Japanese woodblock prints (ukiyo-e) — he "
            "collected them avidly and incorporated motifs into his paintings and "
            "interior design — shaped his compositional instincts: asymmetry, the "
            "large emptiness of a cool tonal ground as a compositional element, the "
            "decorative handling of the picture edge, and the treatment of foreground "
            "figures as flat silhouettes against atmospheric distances.  These "
            "qualities infused all his mature work with an elegant, spare quality "
            "that anticipated the minimalism of the twentieth century."
        ),
        famous_works=[
            ("Arrangement in Grey and Black No.1 (Whistler's Mother)", "1871"),
            ("Symphony in White No.1: The White Girl", "1862"),
            ("Nocturne: Blue and Gold — Old Battersea Bridge", "c. 1872–75"),
            ("The Princess from the Land of Porcelain", "1863–65"),
            ("Nocturne in Black and Gold: The Falling Rocket", "c. 1875"),
            ("Arrangement in Grey: Self-Portrait", "c. 1872–75"),
        ],
        inspiration=(
            "Apply whistler_tonal_harmony_pass() to introduce Whistler's defining "
            "optical quality in three interlocking stages: (1) tonal key lock — "
            "compress all luminance values toward a target key center (default 0.48, "
            "mid-key), pulling extreme darks and lights toward the characteristic "
            "cool-grey tonal register of the Nocturnes; do not flatten the image "
            "but reduce the tonal range so that accents read as deliberate placements "
            "rather than uncontrolled contrasts; (2) cool silver monochromatic drift "
            "— nudge the palette toward Whistler's dominant cool silver-grey hue "
            "(R≈0.56, G≈0.57, B≈0.62) by pulling saturation inward; the effect is "
            "tonal harmony rather than desaturation — each colour is pulled slightly "
            "toward the dominant register while retaining its hue character; "
            "(3) peripheral edge dissolution — apply progressive Gaussian softening "
            "from the compositional periphery inward, dissolving edge detail into "
            "atmospheric suggestion in the manner of Japanese woodblock negative "
            "space and Whistler's intentionally 'lost' picture boundaries; the focal "
            "center retains full edge clarity while the periphery dissolves into haze.  "
            "Use at opacity 0.38–0.48: the effect accumulates quietly and should feel "
            "like a shift in atmosphere rather than a visible filter."
        ),
    ),


    # ── Léon Spilliaert ───────────────────────────────────────────────────────
    "leon_spilliaert": ArtStyle(
        artist="Léon Spilliaert",
        movement="Belgian Symbolism / Expressionism",
        nationality="Belgian",
        period="1900–1940",
        palette=[
            (0.06, 0.05, 0.07),   # near-black ink void — Spilliaert's Indian-ink ground
            (0.20, 0.20, 0.24),   # cold dark grey — penumbra of the void
            (0.75, 0.76, 0.80),   # cold pale grey-white — isolated figure tone
            (0.92, 0.93, 0.96),   # near-white ivory — the most exposed lit surface
            (0.82, 0.80, 0.30),   # acid chartreuse-yellow — eerie lamp-light accent
            (0.18, 0.30, 0.52),   # electric blue-grey — moonlit sea and sky
            (0.38, 0.34, 0.40),   # muted mauve-grey — transitional mid-tone
        ],
        ground_color=(0.08, 0.07, 0.10),   # deep blue-black — supports the noir ground
        stroke_size=3,
        wet_blend=0.22,
        edge_softness=0.18,                # near-crisp — Spilliaert's ink lines are precise
        jitter=0.008,
        glazing=(0.10, 0.10, 0.14),        # cool near-black glaze — deepens the void
        crackle=False,
        chromatic_split=False,
        technique=(
            "Léon Spilliaert (1881–1946) was the most solitary and least classified "
            "of all the Belgian Symbolists.  Where Ensor exploded into carnival masks "
            "and Khnopff retreated into aristocratic silence, Spilliaert simply walked "
            "alone on the beach at Ostend at night, and painted what he found there.  "
            "His work is dominated by vertiginous perspective — empty corridors "
            "receding into darkness, seafronts stretching toward a vanishing point, "
            "staircases descending into void.  The human figure, when it appears at "
            "all, is usually himself: a pale, narrow presence against an engulfing "
            "dark field, like a mark of punctuation in a sentence that has forgotten "
            "its own meaning.  Spilliaert worked primarily in Indian ink, watercolour, "
            "and pastel — often combined in the same work, each medium fighting the "
            "others.  The ink established the near-black scaffolding; the watercolour "
            "floated across it as cool grey washes; the pastel — rare, used sparingly "
            "— provided the occasional acid accent: a strip of pale yellow lamplight, "
            "an electric blue moonlit sea.  His palette is nearly monochromatic.  The "
            "blacks are cold — ink blacks, not oil-paint blacks, which carry no residual "
            "warmth.  The whites are exposed paper or very pale grey wash.  Between "
            "them, almost nothing.  The power of his work comes entirely from tonal "
            "contrast, geometric depth, and the specific quality of emptiness that "
            "fills the spaces between figure and frame.  His masterwork 'Dizziness' "
            "(also called 'Vertigo', 1908) shows a spiral staircase receding into "
            "a void so absolute that the viewer's sense of scale collapses — it is "
            "simultaneously a perfectly rendered architectural interior and a diagram "
            "of existential dissolution.  Apply spilliaert_vertiginous_void_pass() "
            "to encode his characteristic shadow compression and isolated-figure "
            "paleness — the near-black deep field against which pale forms emerge."
        ),
        famous_works=[
            ("Dizziness (Vertigo)", "1908"),
            ("Moonlit Shore", "1906"),
            ("Young Woman at the Window", "1908"),
            ("Self-Portrait", "1907"),
            ("The Seafront at Night", "1908"),
            ("Reflection", "1908"),
            ("The Promenade", "1907"),
            ("Woman Reading", "1920"),
        ],
        inspiration=(
            "Apply spilliaert_vertiginous_void_pass() to encode Spilliaert's "
            "characteristic near-monochrome tonal architecture.  Three operations: "
            "(1) shadow compression — push all dark pixels (lum < void_thresh ≈ 0.30) "
            "further toward near-black with a cold blue-grey undertone (Spilliaert's "
            "ink blacks are cool, carrying a faint blue-grey cast, not the warm brown "
            "of oil-paint darkness); (2) mid-tone isolation — pale areas in the "
            "upper luminance band (lum > pale_thresh ≈ 0.70) receive a very slight "
            "cool-grey lift, isolating them as pale islands against the dark field, "
            "the characteristic 'figure emerging from void' quality; (3) peripheral "
            "vignette deepening — the canvas perimeter darkens further toward absolute "
            "black, reinforcing the geometric vertiginous depth that pulls the eye "
            "toward the composition centre.  Use at opacity 0.30–0.40; the effect "
            "should feel like a shift from oil warmth toward ink austerity."
        ),
    ),


    # ── Odilon Redon ──────────────────────────────────────────────────────────
    "odilon_redon": ArtStyle(
        artist="Odilon Redon",
        movement="French Symbolism / Post-Impressionism",
        nationality="French",
        period="1875–1916",
        palette=[
            (0.12, 0.08, 0.20),   # deep violet-plum void — the noir ground (darkest)
            (0.18, 0.28, 0.68),   # jewel ultramarine blue — floating orbs, cyclops eye
            (0.82, 0.70, 0.22),   # luminous golden ochre — aureole light
            (0.92, 0.88, 0.80),   # luminous ivory cream — brilliant highlight
            (0.72, 0.20, 0.58),   # spectral rose-violet — Redon's magenta jewels
            (0.24, 0.68, 0.62),   # luminous turquoise-green — flower petals, unusual
            (0.88, 0.56, 0.28),   # warm amber — sunlit flower centres
            (0.68, 0.60, 0.82),   # pale lavender halo — atmospheric bloom around forms
        ],
        ground_color=(0.20, 0.16, 0.28),   # deep violet-plum void — supports noir and pastel
        stroke_size=4,
        wet_blend=0.65,
        edge_softness=0.75,
        jitter=0.016,
        glazing=(0.28, 0.22, 0.42),   # cool violet-dominant glaze — dark luminous depth
        crackle=False,
        chromatic_split=True,
        technique=(
            "Odilon Redon (1840–1916) pursued an entirely interior vision — a painting "
            "of what he called 'the logic of the visible in the service of the invisible.' "
            "His career divides into two almost paradoxically distinct phases.  The first, "
            "lasting until the 1890s, was dominated by the 'Noirs' — large charcoal "
            "drawings and lithographs of floating eyes, smiling spiders, winged heads, "
            "and cyclopean giants, all emerging from or dissolving back into dense "
            "velvety black voids.  The Noirs are among the most original graphic works "
            "of the nineteenth century: Redon understood that charcoal, like the "
            "imagination, operates at the boundary between substance and shadow.  His "
            "blacks are not flat — they have depth, warmth, and an almost organic "
            "density that absorbs the eye.  Luminous forms float within these voids "
            "with no rational explanation: they simply appear, as memories or dreams.  "
            "After 1890, and with increasing intensity from around 1900, Redon pivoted "
            "entirely into colour — pastels, oils, distemper — and produced some of the "
            "most jewel-like, spectral, and saturated surfaces in Western art.  His "
            "flowers are not botanical records but chromatic events: petals of impossible "
            "blue, violet, gold, and turquoise clustered in arrangements that have no "
            "naturalistic precedent.  His mythological heads — Orpheus, Apollo, Buddha "
            "— float in halos of luminous warm light.  His colour does not describe "
            "form; it emanates from it.  The two phases are not opposites but extensions "
            "of the same vision: in the Noirs, form is light rescued from darkness; in "
            "the pastels, darkness provides depth against which jewel colours glow.  "
            "Technique: Redon worked with extraordinary materials sensitivity — he "
            "preferred pastel because its dry pigment particles sit on the surface and "
            "catch light differently from oil, creating a bloom and luminosity that oil "
            "cannot replicate.  In oils he built up thin layers of transparent paint "
            "over dark grounds, allowing the ground to show through as the velvety void "
            "that underpins every luminous passage.  His colour relationships are "
            "symbolist not naturalist: complementary pairs (violet and gold, blue and "
            "orange) are exaggerated rather than muted; saturation is pushed to the "
            "maximum the medium allows while retaining harmony.  He was admired by "
            "Gauguin (who owned Redon drawings), influenced by Symbolist poetry "
            "(especially Mallarmé and Baudelaire), and was a touchstone for the "
            "Surrealists decades before Surrealism existed.  Apply "
            "redon_luminous_reverie_pass() for the velvety void / jewel-bloom quality."
        ),
        famous_works=[
            ("The Cyclops", "c.1898–1900"),
            ("The Eye Like a Strange Balloon Mounts toward Infinity", "1882"),
            ("Apollo's Chariot", "c.1905–1914"),
            ("Flower Clouds", "c.1903"),
            ("Orpheus", "c.1903–1910"),
            ("The Shell", "1912"),
            ("Smiling Spider", "1887"),
            ("Buddha", "1906"),
            ("Wildflowers", "c.1912"),
        ],
        inspiration=(
            "Apply redon_luminous_reverie_pass() to encode Redon's distinctive "
            "two-register visual world.  Three operations: (1) velvet void enrichment — "
            "push dark pixels (lum < void_thresh ≈ 0.28) toward a rich warm-violet "
            "near-black by lifting R and B while slightly damping G; produces the "
            "velvety, warm-dark depth of Redon's charcoal and dark oil grounds from "
            "which luminous forms emerge rather than the flat cold black of lesser "
            "painters; (2) spectral bloom aureole — detect the highest-chroma pixels "
            "(saturated jewel colours); apply per-channel Gaussian blur at sigma≈4.5 "
            "to produce a soft halo of scattered light; blend halo at bloom_strength "
            "weighted by local chroma; simulates the optical aureole that surrounds "
            "Redon's floating orbs, cyclops eye, and flower-burst pastels — the "
            "luminous bloom of dry pigment particles catching incident light; "
            "(3) jewel saturation lift — in mid-luminance, high-chroma zones push "
            "saturation further outward (each channel moved away from luminance by "
            "boost_amount); produces the jewel-like chromatic intensity of Redon's "
            "mature pastel and oil work.  Use at opacity 0.38–0.48; effect should "
            "feel like a shift from representational to dreamlike register."
        ),
    ),

    # ── Ferdinand Hodler ───────────────────────────────────────────────────────
    "ferdinand_hodler": ArtStyle(
        artist="Ferdinand Hodler",
        movement="Swiss Symbolism / Post-Impressionism",
        nationality="Swiss",
        period="1885–1918",
        palette=[
            (0.72, 0.58, 0.30),   # warm ochre — mountain earth, dominant landscape tone
            (0.20, 0.40, 0.65),   # Swiss cobalt blue — Alpine lakes and high sky
            (0.45, 0.30, 0.15),   # dark warm umber — figure outlines, tree trunks
            (0.90, 0.85, 0.72),   # warm ivory — flesh passages, bright sky margin
            (0.25, 0.45, 0.22),   # dark meadow green — mid-ground foliage
            (0.62, 0.22, 0.18),   # deep crimson umber — warm shadow accent, draped fabric
            (0.78, 0.70, 0.85),   # pale violet — atmospheric distant peaks
        ],
        ground_color=(0.55, 0.48, 0.28),   # warm ochre-grey — toned canvas for Alpine light
        stroke_size=6,
        wet_blend=0.42,
        edge_softness=0.22,
        jitter=0.022,
        glazing=(0.68, 0.58, 0.32),        # warm amber glaze — unifies the earth-tone palette
        crackle=False,
        chromatic_split=False,
        technique=(
            "Ferdinand Hodler (1853–1918) was the leading Swiss painter of the late "
            "nineteenth and early twentieth centuries and one of the pivotal figures in "
            "European Symbolism.  His mature work is governed by a principle he called "
            "Parallelism — a formal theory derived from his observation that nature "
            "organises itself into rhythmic, symmetrical, repeated structures: parallel "
            "rows of trees along a lakeshore, the parallel thrust of mountain ridges, "
            "the parallel extension of limbs in a procession of figures.  This was not "
            "mere decorative repetition; Hodler believed Parallelism revealed the "
            "underlying order of the universe, its fundamental harmony or Eurythmie.  "
            "In practice, Parallelism meant painting figures in closely mirrored poses "
            "side by side, trees as near-identical vertical accents across the canvas, "
            "and mountain ranges as stacked horizontal bands of simplified colour.  "
            "Hodler stripped away atmospheric haze, anecdotal detail, and casual "
            "incident, reducing landscape and figure to bold, geometrically clarified "
            "zones.  His canvases feel like diagrams of emotional states, not records "
            "of perception.  \n"
            "His early masterpieces — Night (1890), The Disappointed Souls (1892), "
            "Day (1900) — established him internationally and were exhibited at the "
            "Vienna Secession, where they deeply influenced Klimt, Schiele, and the "
            "Jugendstil movement.  Night in particular caused a scandal at its first "
            "Zurich exhibition: its naked, sleeping figures, confronting mysterious "
            "dark presences, seemed too modern, too naked, too psychologically "
            "disturbing for academic taste.  "
            "Palette and technique: Hodler used strong, largely unmixed pigments — "
            "earth ochres, cobalt blues, deep umbers, and warm ivories.  He avoided "
            "subtle atmospheric blending; instead he built up flat or lightly modelled "
            "planes separated by strong dark contour lines.  His canvases have a "
            "poster-like clarity of colour zone, each area reading as a distinct "
            "chromatic and tonal value.  In his Alpine landscapes — Thun, Geneva, "
            "Niesen — the lake is always a single flat zone of deep cobalt or grey-"
            "blue; the mountains are banded horizontal planes of ochre, green, and "
            "purple; the sky is a flat warm ivory or golden yellow.  This structural "
            "simplification — real objects reduced to their essential geometric "
            "chromatic identity — anticipates the language of Matisse, Mondrian, and "
            "twentieth-century abstract painting.  "
            "Apply hodler_parallelism_pass() to encode the characteristic Hodler "
            "surface: simplified tonal planes, strong dark contours, and chromatic "
            "clarity that reads across the full viewing distance."
        ),
        famous_works=[
            ("Night", "1890"),
            ("Day", "1900"),
            ("The Disappointed Souls", "1892"),
            ("The Chosen One", "1893–1894"),
            ("Eurythmie", "1895"),
            ("Lake Thun", "1905"),
            ("Autumn Evening", "1892"),
            ("Look into Infinity", "1913–1916"),
            ("The Battle of Murten", "1897"),
        ],
        inspiration=(
            "Apply hodler_parallelism_pass() to encode Hodler's signature visual "
            "language.  Three stages: (1) tonal band simplification — reduce the canvas "
            "luminance to a small number of discrete tonal bands via a smooth staircase "
            "function (n_bands ≈ 5–7); mid-tones collapse toward a dominant plane value "
            "rather than blending continuously; produces the flat, zone-based tonal "
            "quality of Hodler's simplified figure and landscape planes; (2) contour "
            "darkening — detect luminance edges using Sobel gradient; darken pixels in "
            "the edge zone by a configurable amount, effectively strengthening the dark "
            "contour lines that separate Hodler's tonal planes from one another and give "
            "his compositions their characteristic poster-bold clarity; (3) chromatic "
            "clarity — in mid-luminance, high-chroma zones slightly boost saturation "
            "toward the dominant hue, while very low-chroma (near-neutral) passages "
            "are left untouched; produces the effect of Hodler's largely unmixed "
            "pigments, where each colour zone reads as its essential identity rather "
            "than a complex mixture.  Use at opacity 0.32–0.45."
        ),
    ),

    # ── Gustave Caillebotte ───────────────────────────────────────────────────
    "gustave_caillebotte": ArtStyle(
        artist="Gustave Caillebotte",
        movement="Impressionism / Urban Realism",
        nationality="French",
        period="1870–1894",
        palette=[
            (0.58, 0.60, 0.62),   # cool grey — wet Parisian cobblestone
            (0.72, 0.68, 0.55),   # warm ochre-tan — overcoats and building façades
            (0.38, 0.40, 0.45),   # deep slate — cast shadows, receding distance
            (0.85, 0.84, 0.80),   # pale cream — building stone in diffuse sky light
            (0.30, 0.32, 0.35),   # dark charcoal — umbrella handles, ironwork, deep shadow
            (0.50, 0.55, 0.65),   # cool mist blue — overcast sky reflected in puddles
            (0.65, 0.52, 0.38),   # warm sienna — wood floors, wooden scraper handles
        ],
        ground_color=(0.52, 0.53, 0.55),   # cool mid-grey — overcast Parisian ambient
        stroke_size=5,
        wet_blend=0.18,
        edge_softness=0.25,
        jitter=0.018,
        glazing=None,
        crackle=False,
        chromatic_split=False,
        technique=(
            "Gustave Caillebotte (1848–1894) occupies an unusual position in the "
            "history of Impressionism: he was a founding exhibitor alongside Monet, "
            "Renoir, and Degas, yet his technique was far more precisely realist than "
            "theirs, his debt to photography more explicit, and his compositional "
            "ambitions more architectural.  Born into a wealthy Parisian family, he "
            "had the means to paint what he chose without commercial pressure, and "
            "what he chose was the spectacle of modern urban life — newly Haussmann-"
            "ized Paris with its broad swept boulevards, iron bridges, and gleaming "
            "rain-wet cobblestones.  \n"
            "His signature move is radical perspective foreshortening.  In 'Paris "
            "Street; Rainy Day' (1877) — his masterpiece — the foreground figures are "
            "cropped at the frame edge exactly as a camera would crop them, while the "
            "receding intersection stretches back to a single vanishing point with "
            "almost ruler-precise geometry.  This photographic cropping — cutting a "
            "figure in half at the left edge, letting a lamppost slice the composition "
            "into zones — was jarring to academic audiences accustomed to centred, "
            "complete compositions.  'Pont de l'Europe' (1876) uses the iron grid of "
            "the bridge to impose a geometric armature across the entire canvas, "
            "turning the painting into a study of perspective lines as much as a "
            "record of pedestrians.  \n"
            "Caillebotte's palette for outdoor Paris scenes is cool and muted: "
            "overcast sky grey, wet cobblestone reflections of that grey, warm ochre "
            "and tan overcoats contrasting with the cool ground, cream limestone "
            "building façades grading to shadow slate.  He avoided the bright "
            "unmixed colour of Monet or Renoir; his paint handling is controlled, "
            "his surfaces relatively smooth, his forms clearly delineated.  Light "
            "in his urban scenes is diffuse and even — Paris under a cloud-filtered "
            "sky — without the Monet sunburst or the Rembrandt spotlight.  "
            "His indoor scenes — notably 'The Floor Scrapers' (1875) and "
            "'Man at His Bath' (1884) — exploit extreme foreshortening of a "
            "different kind: the floor scrapers bent double fill the foreground, "
            "their muscular backs foreshortened by a high viewpoint, the bare "
            "parquet floor receding in strong perspective.  These figures are "
            "painted with almost photographic musculature and realism quite unlike "
            "the impressionistic smear of his contemporaries.  "
            "Apply caillebotte_perspective_pass() to encode Caillebotte's "
            "characteristic visual language: axis-aligned edge sharpening to "
            "reinforce receding geometric lines, cool cobblestone reflection "
            "brightening in dark low-saturation zones, and a subtle cool blue-"
            "channel lift that neutralizes warm mid-tones under Parisian overcast sky."
        ),
        famous_works=[
            ("Paris Street; Rainy Day", "1877"),
            ("The Floor Scrapers", "1875"),
            ("Pont de l'Europe", "1876"),
            ("Young Man at His Window", "1875"),
            ("Man at His Bath", "1884"),
            ("Le Déjeuner", "1876"),
            ("Skiffs on the Yerres", "1877"),
            ("Boating", "1877"),
            ("The Orange Trees", "1878"),
        ],
        inspiration=(
            "Apply caillebotte_perspective_pass() to encode Caillebotte's visual "
            "language.  Three stages: (1) axis-aligned edge sharpening — compute "
            "horizontal and vertical Sobel edge maps separately; apply unsharp "
            "masking along each axis independently at perspective_strength to "
            "reinforce the receding geometric lines (iron grids, cobblestone joints, "
            "building cornices) without halos on organic diagonal edges; (2) "
            "cobblestone reflection lift — in dark, low-saturation zones (luminance "
            "< 0.45, chroma < 0.10), apply a cool blue-channel brightening of "
            "cobblestone_boost, simulating the dull reflection of overcast sky in "
            "wet Parisian pavement; (3) cool ambient shift — in warm mid-tones "
            "(R > B, luminance in [0.30, 0.70]), nudge the blue channel up by "
            "cool_shift to pull the overall temperature toward the diffuse grey "
            "Parisian sky ambient light.  Use at opacity 0.30–0.40."
        ),
    ),

    # ── Franz Marc ─────────────────────────────────────────────────────────────
    "franz_marc": ArtStyle(
        artist="Franz Marc",
        movement="German Expressionism / Der Blaue Reiter",
        nationality="German",
        period="1880–1916",
        palette=[
            (0.12, 0.20, 0.72),   # ultramarine spiritual blue — the defining Marc hue; horses, deer, sky
            (0.92, 0.82, 0.10),   # cadmium yellow — feminine vitality; cows, meadows, sunlight
            (0.82, 0.22, 0.14),   # cadmium red — violence, matter, earth; accents on bodies and ground
            (0.18, 0.62, 0.28),   # emerald green — nature ground; landscape planes beneath animals
            (0.55, 0.30, 0.65),   # violet — spiritual transition between blue and red; shadow masses
            (0.08, 0.08, 0.12),   # warm near-black — deep shadow, outline boundary planes
            (0.92, 0.90, 0.88),   # warm ivory — highlight zones, sky margin, lightest flesh
        ],
        ground_color=(0.18, 0.28, 0.55),   # deep ultramarine-blue ground — the spiritual ground of existence
        stroke_size=6,
        wet_blend=0.28,
        edge_softness=0.32,
        jitter=0.018,
        glazing=(0.62, 0.55, 0.22),        # warm amber glaze — unifies the prismatic primaries across the canvas
        crackle=False,
        chromatic_split=False,
        technique=(
            "Franz Marc (1880–1916) was co-founder, with Wassily Kandinsky, of Der "
            "Blaue Reiter (The Blue Rider) — the Munich-based German Expressionist "
            "movement that sought to use colour as a direct vehicle of spiritual truth "
            "rather than a description of observed reality.  Marc's central conviction "
            "was that specific colours carried inherent symbolic meaning: blue for "
            "spirituality and the masculine principle, yellow for warmth, gentleness "
            "and the feminine, red for violence, matter, and the earthly.  These were "
            "not arbitrary assignments but beliefs derived from Goethe's colour theory "
            "and theosophical spiritualism that Marc studied intensively.  "
            "In practice this meant that Marc's animals — the blue horses, the yellow "
            "cow, the red deer — are not naturalistic descriptions but chromatic "
            "arguments: the horse painted ultramarine is a spiritual being; the same "
            "animal painted red would be earthy and violent; yellow would be gentle and "
            "feminine.  His canvases are therefore colour-philosophies as much as "
            "paintings.  "
            "Formally, Marc moved steadily toward abstraction.  His early animal works "
            "are recognisably figurative but rendered in pure unmixed primaries applied "
            "in clearly bounded planes with minimal atmospheric blending.  By 1912–1913 "
            "the planes begin to fragment into the angular, faceted geometry of Cubism "
            "(which Marc encountered in Paris in 1912 through Delaunay's Orphism) while "
            "retaining the prismatic colour symbolism.  Fate of the Animals (1913) is "
            "the culmination: a shattering cascade of prismatic shards implying "
            "apocalyptic destruction, with the symbolic colour system now embedded in "
            "a Cubist-shattered space.  Marc himself called it a premonition — he was "
            "killed at Verdun in 1916, aged 35.  "
            "Technique: Marc worked with a limited palette of pure primaries — "
            "ultramarine, cadmium yellow, cadmium red, emerald green — and avoided "
            "greys, browns, and earth tones wherever possible.  His canvases have an "
            "almost stained-glass luminosity: each colour plane glows independently "
            "rather than participating in a unified tonal system.  His grounds were "
            "often blue or violet — the spiritual colour — so that it could seep "
            "through the upper paint layers as a unifying undertone.  "
            "Apply franz_marc_prismatic_vitality_pass() to encode the characteristic "
            "Marc surface: symbolic colour intensification, prismatic clarity of "
            "individual colour planes, and the spiritual luminosity of pure unmixed "
            "primaries glowing against a deep blue ground."
        ),
        famous_works=[
            ("Blue Horse I", "1911"),
            ("The Large Blue Horses", "1911"),
            ("Yellow Cow", "1911"),
            ("The Tiger", "1912"),
            ("Deer in the Forest II", "1913"),
            ("Fate of the Animals", "1913"),
            ("Tower of Blue Horses", "1913"),
            ("The Foxes", "1913"),
            ("Fighting Forms", "1914"),
            ("Stables", "1913"),
        ],
        inspiration=(
            "Apply franz_marc_prismatic_vitality_pass() to encode Marc's symbolic "
            "colour language.  Three stages: (1) symbolic colour intensification — "
            "identify dominant hue of each pixel zone; pixels where blue dominates "
            "(B > R×1.15, B > G×1.10) receive a further push toward ultramarine "
            "(spiritual elevation); pixels where warm yellow dominates (R > B×1.15, "
            "G > B×1.10, high luminance > 0.70) receive a gentle golden warmth push; "
            "pixels with red-dominant mid-darks (R > B×1.20, lum in [0.25, 0.60]) "
            "receive a slight deepening into warm crimson; this simulates Marc's "
            "symbolic colour assignment in which each primary retains and amplifies "
            "its own emotional character; (2) prismatic form bloom — compute per-pixel "
            "chroma (max_rgb − min_rgb); at high-chroma boundaries (chroma > "
            "bloom_thresh) apply a per-channel Gaussian bloom (sigma=3.0) weighted "
            "by the excess chroma, producing the glowing luminous aureole around pure "
            "colour planes characteristic of Marc's stained-glass quality; (3) "
            "prismatic clarity lift — in mid-luminance zones (lum in [0.30, 0.75]) "
            "boost saturation by boost_amount × chroma_gate (chroma > sat_thresh), "
            "moving each channel further from the luminance mean; this maintains the "
            "unmixed-pigment vibrancy of Marc's pure primary palette and prevents "
            "any overall muddying of the colour zones.  Use at opacity 0.32–0.45."
        ),
    ),


    # ── Session 92 — new artist: Antonello da Messina ────────────────────────
    # Randomly selected artist for session 92's inspiration.
    # Antonello da Messina (c. 1430–1479) occupies a singular pivot-point in the
    # history of European painting.  He was a Sicilian, born in Messina, trained
    # partly in Naples at the workshop of Colantonio — an artist who had himself
    # studied Flemish painting under Alfonso V of Aragon's collection.  Through
    # this channel Antonello absorbed the Flemish oil-glazing technique that Jan
    # van Eyck had perfected: the method of building up colour in multiple thin,
    # transparent layers on a white-gesso ground, so that light passes through
    # the layers, reflects from the ground, and re-emerges with the jewel-like
    # inner luminosity that tempera and fresco could never achieve.
    #
    # When Antonello arrived in Venice in 1475–76 he transformed Italian
    # portraiture.  Italian painters — even great Florentines — had largely
    # painted in the three-quarter profile convention, avoiding the full-face
    # gaze as technically difficult and psychologically confrontational.  Flemish
    # portraitists like van Eyck and Memling had already mastered the frontal
    # gaze, and Antonello brought this directness south with him.  His portraits
    # look at you.  The sitter's eyes meet the viewer's with an immediacy that
    # has still not worn away after five and a half centuries.  Giovanni Bellini,
    # who met Antonello in Venice and was profoundly influenced by him, later
    # wrote that the Sicilian's technique was "as much a mystery as a revelation."
    #
    # The defining quality of Antonello's flesh is what may be called pellucid
    # clarity: the painted skin appears to have depth and translucency — not the
    # warm opaque mask of the Florentines, not the atmospheric dissolve of
    # Leonardo, but something closer to polished crystal: you feel the form
    # beneath the surface, the bone structure under the skin, the light moving
    # *through* rather than merely *across* the paint.  This comes from his
    # Flemish glazing method combined with a distinctly Italian warmth in the
    # midtone flesh: the lit zones are warm Naples yellow-ivory, but the
    # mid-shadow transitions carry a slight blue-green Flemish subsurface tint
    # that reads as skin through which light has penetrated and scatted.
    #
    # Unlike Memling, whose palette is richly saturated — brilliant vermilion,
    # azure, Naples gold — Antonello's palette is more restrained, more Italian:
    # warm siennas, raw umber, ivory-Naples yellow flesh, with backgrounds often
    # cool and architectural (pale blue sky, a stone niche, or an arched window
    # framing a Flemish-style landscape).  The contrast between the warm figure
    # and the cool, luminous background architecture is distinctively Antonello.
    #
    # His most famous work, the 'Portrait of a Man' (c. 1475, National Gallery,
    # London) — possibly a self-portrait — shows all of this: the direct gaze,
    # the pellucid warm-flesh-over-cool-shadow construction, the architectural
    # setting, and the sense of a specific individual encountered across time.
    #
    "antonello_da_messina": ArtStyle(
        artist="Antonello da Messina",
        movement="Sicilian Renaissance / Flemish-Italian Bridge",
        nationality="Italian (Sicilian)",
        period="1455–1479",
        palette=[
            (0.90, 0.82, 0.64),   # Naples yellow-ivory — lit flesh highlights; warmest Antonello tone
            (0.80, 0.65, 0.46),   # warm sienna flesh — primary midtone; Italian warmth over Flemish structure
            (0.60, 0.48, 0.36),   # raw umber shadow flesh — deep midtone transition
            (0.40, 0.46, 0.44),   # blue-green shadow undertone — Flemish subsurface tint in shadow transitions
            (0.20, 0.26, 0.42),   # cool architectural blue-grey — background niches, sky, stone vaulting
            (0.32, 0.28, 0.24),   # warm near-black — deep shadow; Antonello's voids are warm, not cold
            (0.76, 0.64, 0.38),   # golden amber — warm imprimatura glow; the Italian oil-glazing foundation
            (0.85, 0.88, 0.92),   # cool pale sky — luminous Flemish-style background atmosphere
        ],
        ground_color=(0.74, 0.64, 0.42),    # warm pale ochre — lighter than Rembrandt; allows Flemish glaze luminosity
        stroke_size=3,
        wet_blend=0.55,                      # moderate-high — smooth oil-glazing surface, invisible brushwork
        edge_softness=0.38,                  # found-edge Flemish clarity — neither sfumato nor hard contour
        jitter=0.014,                        # tight colour variation; Flemish control, not impressionist flicker
        glazing=(0.78, 0.66, 0.38),          # warm amber glaze — Italian warmth as final unifier
        crackle=True,                        # 15th-century panel; Sicilian oak or poplar ground
        chromatic_split=False,
        technique=(
            "Antonello da Messina (c. 1430–1479) built his technique from two sources: "
            "the Flemish oil-glazing method of Jan van Eyck (absorbed in Naples through "
            "Colantonio) and the Italian warm-flesh tradition of the South.  He worked on "
            "a white-gesso panel ground — like the Flemish masters — with a warm amber "
            "imprimatura as the first toning layer.  Over this he built flesh in multiple "
            "thin transparent glazes, starting with warm sienna midtones and pushing "
            "lighter with Naples yellow-ivory in the lit zones and darker with raw umber "
            "in the shadows.  "
            "The defining pellucid quality of his flesh comes from a slight blue-green "
            "coolness in the mid-shadow transitions — a Flemish subsurface tint that "
            "suggests light entering, scattering through the translucent oil layers, and "
            "re-emerging cooled.  Highlights approach warm Naples yellow-ivory but are "
            "kept crisp and small — enamel-like specular points rather than broad lit zones.  "
            "Unlike Leonardo (atmospheric sfumato) or Raphael (radiant idealism), "
            "Antonello's edges are Flemish found-edges: resolved with precision but not "
            "hardened; the boundary of the face is clear but breathing.  "
            "His backgrounds are typically cool and architectural — pale blue sky through "
            "an arched window, a stone niche, or a Flemish-style landscape — creating a "
            "strong warm-figure / cool-background contrast that reinforces the spatial "
            "presence of the sitter.  Apply antonello_pellucid_flesh_pass() after "
            "build_form() to add the characteristic pellucid shadow coolness and warm "
            "highlight clarity that distinguish him from all his Italian contemporaries."
        ),
        famous_works=[
            ("Portrait of a Man ('Il Condottiere')",     "c. 1475"),
            ("Portrait of a Man (National Gallery, London)", "c. 1475"),
            ("Saint Jerome in His Study",                "c. 1475"),
            ("Salvator Mundi",                           "c. 1465"),
            ("Virgin Annunciate",                        "c. 1476"),
            ("Portrait of a Young Man (Berlin)",         "c. 1478"),
            ("San Cassiano Altarpiece (fragments)",      "1475–1476"),
            ("Portrait of a Man (Turin)",                "c. 1476"),
        ],
        inspiration=(
            "Use antonello_pellucid_flesh_pass() after build_form() and before glaze() "
            "to encode Antonello's pellucid flesh quality.  Three stages: "
            "(1) Flemish shadow cooling — in mid-shadow transitions (lum 0.18–0.46), "
            "apply a slight blue-green subsurface tint (G + subtle, B + moderate, R – "
            "slight) replicating the Flemish translucent-skin quality that Antonello "
            "brought from van Eyck; this is not Memling's enamel brilliance but a quieter, "
            "more Italian restraint of the same phenomenon; (2) warm highlight clarification "
            "— in lit zones (lum > 0.74), push slightly toward Naples yellow-ivory "
            "(R + moderate, G + modest, B – slight), creating the small, crisp, warm "
            "specular quality of Antonello's oil-glazed highlights; (3) pellucid edge "
            "band — at the light-shadow transition zone (penumbra, lum 0.44–0.58), very "
            "slightly sharpen the tonal gradient to give the 'found-edge' quality that "
            "Flemish painters mastered — the boundary reads as resolved, not dissolved "
            "and not hardened.  "
            "ground_color=(0.74, 0.64, 0.42) uses a clear warm ochre ground that allows "
            "Flemish glaze layers to retain their luminosity.  "
            "edge_softness=0.38 gives Flemish found-edge precision without sfumato."
        ),
    ),

    # ── Hugo van der Goes (session 93) ─────────────────────────────────────
    "hugo_van_der_goes": ArtStyle(
        artist="Hugo van der Goes",
        movement="Early Netherlandish / Flemish Late Gothic",
        nationality="Flemish",
        period="c. 1467–1482",
        palette=[
            (0.84, 0.72, 0.52),   # warm ochre-ivory flesh — lit face midtone; earthy rather than idealized
            (0.72, 0.58, 0.38),   # golden amber — deep midtone flesh; warm brown that characterises van der Goes
            (0.52, 0.38, 0.24),   # raw sienna shadow — upper-shadow flesh transition; rich, not cold
            (0.30, 0.22, 0.14),   # warm near-black — deep shadow; velvet dark with amber undertone
            (0.14, 0.10, 0.07),   # void black — absolute background dark; van der Goes backgrounds recede to near-absence
            (0.60, 0.22, 0.14),   # crimson red — drapery accent; intense saturated cloth against earthy flesh
            (0.28, 0.38, 0.24),   # dark muted green — background foliage; subdued, not Spring-bright
            (0.90, 0.86, 0.80),   # cool pale ivory — maximum lit flesh; slightly cooler highlight than Antonello's warm Naples yellow
        ],
        ground_color=(0.62, 0.50, 0.32),    # warm amber-brown imprimatura — darker and richer than Antonello's
        stroke_size=3,
        wet_blend=0.42,                      # moderate — oil glazes, but less transparent stacking than van Eyck
        edge_softness=0.32,                  # Flemish found-edges — precise but not hardened; contours breathe
        jitter=0.018,                        # slight colour variation — Flemish control, but organic life
        glazing=(0.60, 0.42, 0.22),          # deep amber-brown glaze — warm unifying layer over the whole surface
        crackle=True,                        # 15th-century oak panel; extensive craquelure on originals
        chromatic_split=False,
        technique=(
            "Hugo van der Goes (c. 1440–1482) is the most psychologically intense of "
            "the Early Netherlandish masters — and arguably the most modern in his "
            "emotional register.  Working in Ghent at the height of the Flemish panel "
            "tradition (his contemporaries include Memling and Bouts), van der Goes "
            "shared their technical precision but departed radically from their serene "
            "idealism.  His figures carry weight — not only physical mass, but psychological "
            "burden — and his compositions have an unsettling, pre-Expressionist quality "
            "that sets him apart from every other painter of his century.  "
            "Technically, van der Goes worked on oak panel with a white chalk gesso ground, "
            "toned with a warm amber-brown imprimatura darker and richer than van Eyck's "
            "cool white.  Over this ground he built flesh in multiple oil-glaze layers, "
            "beginning with raw sienna and umber underpaint and progressing toward warm "
            "ochre-ivory in the lit zones.  His shadow transitions are deeper and warmer "
            "than Antonello's or Memling's — the darks approach a velvety near-black with "
            "amber undertones, and there is no Flemish blue-green subsurface tint: van der "
            "Goes' shadows are exclusively warm.  "
            "His most distinctive feature is the near-absence of background — compositions "
            "like the Portinari Altarpiece place figures against atmospheric near-black "
            "voids that anticipate Caravaggio by a century.  The background is not the "
            "rich Flemish landscape of van Eyck or Memling's carefully rendered rooms: "
            "it is darkness, weight, and psychological depth rendered as absence.  "
            "Colour-wise, van der Goes favoured intense saturated accents — crimson and "
            "deep scarlet drapery against earthy flesh — and subdued, low-key greens for "
            "any landscape elements.  His whites are cool and slightly ashy, quite different "
            "from the warm Naples yellow-ivory highlights of the Italian-trained Flemings.  "
            "Apply hugo_van_der_goes_expressive_depth_pass() after build_form() to add the "
            "characteristic warm-dark shadow enrichment, psychological weight through "
            "midtone earthing, and near-black void deepening that define van der Goes."
        ),
        famous_works=[
            ("Portinari Altarpiece",                    "c. 1475–1476"),
            ("Dormition of the Virgin",                 "c. 1480"),
            ("Adoration of the Shepherds (Uffizi)",     "c. 1480"),
            ("The Fall of Man and the Lamentation",     "c. 1470–1475"),
            ("Portrait of a Man (Praying)",             "c. 1475"),
            ("Monforte Altarpiece",                     "c. 1470"),
            ("Trinity Panels (Royal Collection)",       "c. 1478–1479"),
        ],
        inspiration=(
            "Use hugo_van_der_goes_expressive_depth_pass() after build_form() and "
            "before any glaze pass to encode van der Goes' three defining qualities:  "
            "(1) Warm shadow enrichment — in deep shadow zones (lum < 0.35), amplify "
            "warm amber undertones by boosting R slightly and damping B, reinforcing the "
            "velvety warmth of his near-black darks; avoid any blue-green subsurface tint "
            "(that is Antonello's quality, not van der Goes'); (2) Psychological weight "
            "through midtone earthing — in upper-midtone flesh (lum 0.45–0.68), apply a "
            "slight amber-brown pull (R + modest, G + slight, B − modest), making the "
            "flesh feel earthbound and weighty rather than idealized or radiant; this is "
            "the quality that separates van der Goes from Memling's serenity; (3) Near-"
            "black void deepening — in the absolute darks (lum < 0.12), push slightly "
            "further toward warm void black, increasing depth without going to cold neutral.  "
            "ground_color=(0.62, 0.50, 0.32) uses a rich amber-brown ground darker than "
            "Antonello's — it asserts itself in any passages of thin paint, unifying the "
            "surface with warm depth.  "
            "edge_softness=0.32 gives Flemish found-edge clarity — precise but not "
            "mechanical.  glazing=(0.60, 0.42, 0.22) applies a deep amber-brown unifier "
            "over the entire surface, replicating the aged amber varnish on van der Goes "
            "panels, which has darkened the originals significantly."
        ),
    ),

    # ── Gerrit Dou ────────────────────────────────────────────────────────────
    # ── Carel Fabritius ───────────────────────────────────────────────────────
    "carel_fabritius": ArtStyle(
        artist="Carel Fabritius",
        movement="Dutch Golden Age / Contre-Jour Portraiture",
        nationality="Dutch",
        period="1641–1654",
        palette=[
            (0.88, 0.84, 0.76),   # pale grey ground — the luminous wall/background his figures read against
            (0.78, 0.68, 0.52),   # warm ivory flesh — lit midtone; warmer than his pale ground
            (0.58, 0.50, 0.38),   # ochre mid-shadow — form transitions on the lit side
            (0.32, 0.26, 0.18),   # raw umber — shadow; leaning warmer than Rembrandt's cool voids
            (0.12, 0.10, 0.08),   # near-black — deepest darks, used sparingly against bright ground
            (0.94, 0.90, 0.82),   # cool bright ground — the atmospheric pale background that defines contre-jour
            (0.68, 0.60, 0.46),   # warm mid-flesh — confident impasto in lit areas
            (0.45, 0.40, 0.30),   # warm brown — drapery and shadow masses
        ],
        ground_color=(0.78, 0.74, 0.66),    # pale grey-warm ground — utterly unlike Rembrandt's dark imprimatura
        stroke_size=8,
        wet_blend=0.48,                      # moderate blending — visible brushwork, not fijnschilder smoothness
        edge_softness=0.42,                  # moderate — edges are present, not dissolved; the ground does the softening
        jitter=0.035,                        # slight colour variation per stroke — confident but not mechanical
        glazing=None,                        # no unifying glaze — the pale ground provides the unifying light
        crackle=True,                        # 17th-century panel; aged craquelure
        chromatic_split=False,
        technique=(
            "Carel Fabritius (1622–1654) was Rembrandt's most gifted pupil and the teacher "
            "of Johannes Vermeer — a crucial pivot in the Dutch Golden Age tradition.  "
            "His brief career (he died at 32 in the Delft gunpowder explosion of 1654, "
            "taking most of his work with him) produced a handful of paintings of extraordinary "
            "originality, most famous among them The Goldfinch (1654), now in the Mauritshuis.  "
            "Where Rembrandt worked on dark brown grounds, building light out of shadow, "
            "Fabritius invented the reverse: he painted on pale grey grounds, letting the "
            "bright background read through the thin glazes, so that his figures emerge as "
            "warm masses against a cool, luminous field.  This is the contre-jour principle "
            "— light against light — and it transforms the spatial language of Dutch painting: "
            "figures are not isolated spotlit forms in a void but atmospheric presences "
            "embedded in an ambient grey-white light.  "
            "His brushwork is confident and direct — broader and more impressionistic than "
            "Vermeer's patient glazing, warmer and more atmospheric than Rembrandt's dramatic "
            "chiaroscuro.  In The Goldfinch, individual brushstrokes of cream, yellow-ochre, "
            "and warm brown build the bird's plumage with remarkable economy: ten strokes "
            "where another painter might use fifty, each one placed with absolute assurance.  "
            "The background — that pale grey wall — is not empty space but active light, "
            "pushing forward against the dark body of the bird, creating the contre-jour "
            "silhouette that makes the image unforgettable.  "
            "Apply fabritius_contre_jour_pass() after the main painting passes to add the "
            "three defining qualities: pale ground luminosity, edge bloom where figures meet "
            "the bright background, and the cool atmospheric veil that Fabritius used instead "
            "of Rembrandt's warm imprimatura darkness."
        ),
        famous_works=[
            ("The Goldfinch",                "1654"),
            ("A View in Delft",              "1652"),
            ("Self-Portrait",                "c. 1645–49"),
            ("The Sentry",                   "1654"),
            ("Hagar and the Angel",          "c. 1645"),
            ("Mercury and Argus",            "1645"),
            ("Abraham de Potter",            "1649"),
            ("Young Man in a Fur Cap",       "c. 1654"),
        ],
        inspiration=(
            "Apply fabritius_contre_jour_pass() to encode Fabritius's contre-jour light: "
            "(1) Cool ground veil — in deep shadow zones (lum < shadow_threshold), add "
            "a gentle cool grey lift, simulating his pale ground luminosity showing through "
            "thin glazes; this is the opposite of Rembrandt's warm dark ground — the shadows "
            "here are cool and luminous, not warm and opaque; (2) Edge bloom — at significant "
            "luminance gradient boundaries (figure edges), add a soft halo on the brighter "
            "side, simulating the contre-jour glow where a figure reads against a bright "
            "background; (3) Atmospheric ground haze — apply a very gentle global cool "
            "tint in mid-tone regions, unifying the surface with the pale grey-white ground "
            "quality that defines Fabritius's spatial language."
        ),
    ),

    "judith_leyster": ArtStyle(
        artist="Judith Leyster",
        movement="Dutch Golden Age / Utrecht Caravaggist-influenced genre",
        nationality="Dutch (Haarlem)",
        period="1629–1660",
        palette=[
            (0.97, 0.89, 0.72),   # warm ivory highlight — candlelit peak; creamy amber warmth on lit flesh
            (0.90, 0.74, 0.52),   # warm ochre-peach — lit midtone; her flesh glows with amber incandescence
            (0.76, 0.58, 0.38),   # golden amber — upper shadow transition; warm brown imprimatura showing through
            (0.52, 0.36, 0.20),   # raw umber — mid-shadow; warm, never cold; her shadows stay alive
            (0.28, 0.18, 0.10),   # warm near-black — deep shadow; rich warm-brown void, not neutral black
            (0.84, 0.60, 0.30),   # amber-orange — candle highlight note; the warm point-source quality
            (0.62, 0.48, 0.34),   # warm stone — background neutrals; interior wall warmth in shadow
            (0.40, 0.28, 0.18),   # deep warm brown — drapery darks; the same imprimatura tone in full shadow
        ],
        ground_color=(0.60, 0.46, 0.28),    # warm brown imprimatura — Hals/Haarlem tradition, amber-ochre warmth
        stroke_size=9,
        wet_blend=0.38,                      # confident directness — blended enough for flesh warmth, not dissolved
        edge_softness=0.50,                  # moderate — figures read clearly against warm shadow ground
        jitter=0.025,                        # slight colour variation — lively, not mechanical
        glazing=(0.72, 0.54, 0.28),          # warm amber-brown unifying glaze — her characteristic warmth register
        crackle=True,                        # 17th-century canvas; aged craquelure in originals
        chromatic_split=False,
        technique=(
            "Judith Leyster (1609–1660) was one of the most gifted painters of the Dutch Golden "
            "Age — a contemporary, near-neighbour, and occasional rival of Frans Hals in Haarlem. "
            "In 1633 she became one of the very few women admitted to the Haarlem Guild of St. Luke, "
            "and shortly after ran her own independent workshop with multiple male apprentices, "
            "an extraordinary achievement for a woman in the seventeenth century.  "
            "Leyster's technique blends the bravura directness she absorbed from Hals — loaded-brush "
            "marks, confident all-prima working, strokes placed with economy and purpose — with a "
            "warmer, more intimate tonal register influenced by the Utrecht Caravaggists (Honthorst, "
            "Terbrugghen).  Unlike Hals's cooler, more extroverted portraiture, Leyster's genre scenes "
            "are suffused with amber warmth: a candle or lamp just off-stage tilts the illumination "
            "toward orange-amber, making flesh tones glow with incandescence against rich, warm-brown "
            "shadow grounds.  "
            "Her defining compositional mode is the single figure caught in a moment of private joy "
            "or domestic absorption — a fiddler caught mid-laugh, a seamstress working by candlelight, "
            "a child blowing a soap bubble.  The figure is typically close to the picture plane, often "
            "turning slightly toward the viewer with an expression of animated awareness.  Unlike the "
            "pure tenebrism of Caravaggio or La Tour, Leyster allows ambient warmth into the mid-tones: "
            "her shadows are luminous, not opaque, heated by the brown imprimatura showing through thin "
            "shadow glazes.  This gives her work a vitality that is peculiarly her own — joyful and "
            "alive, even in stillness.  "
            "Apply judith_leyster_joyful_light_pass() after main build_form() passes to encode the "
            "three defining qualities: incandescent highlight warmth, shadow vitality from the warm "
            "imprimatura, and a mid-tone chromatic ping that makes her transitional flesh zones glow "
            "with the characteristic amber animation of her candlelit interiors."
        ),
        famous_works=[
            ("The Joyful Toper",              "c. 1629"),
            ("The Serenade",                  "1629"),
            ("Self-Portrait",                 "c. 1633"),
            ("Two Children with a Cat",       "c. 1629–1631"),
            ("The Proposition",               "1631"),
            ("Young Flute Player",            "c. 1635"),
            ("Boy and Girl with a Cat",       "c. 1635"),
            ("Carousing Couple",              "1630"),
        ],
        inspiration=(
            "Apply judith_leyster_joyful_light_pass() to encode her defining tonal qualities: "
            "(1) Incandescent highlight warm-lift — in upper highlight zones (lum > 0.65), add "
            "a warm amber-peach shift (R+, G+ slightly, B-), simulating the incandescent orange-"
            "amber of her candlelit illumination; this is warmer than Dou's refined gold, more "
            "domestic than La Tour's flame, more joyful than Rembrandt's chiaroscuro; (2) Shadow "
            "vitality (warm imprimatura show-through) — in deep shadow zones (lum < 0.28), add a "
            "very slight warm brown lift (R+ slightly, G+ less, B minimal), simulating the warm "
            "ochre-brown imprimatura showing through thin shadow glazes; Leyster's shadows are never "
            "dead — they breathe with the warmth of the ground; (3) Mid-tone chromatic animation — "
            "in the transitional zone (lum 0.35–0.60), add a subtle warm amber ping that makes the "
            "transitional flesh zones glow; this is the zone where Leyster's figures feel most alive, "
            "caught between the deep warmth of shadow and the incandescence of direct light."
        ),
    ),

    # ── Frans Hals ────────────────────────────────────────────────────────────
    "frans_hals": ArtStyle(
        artist="Frans Hals",
        movement="Dutch Golden Age / Bravura Portrait",
        nationality="Dutch (Haarlem)",
        period="1610–1666",
        palette=[
            (0.92, 0.82, 0.66),   # warm ivory highlight — lit flesh peak; naples yellow warmth
            (0.76, 0.62, 0.44),   # amber-ochre mid-flesh — warm imprimatura showing through thin paint
            (0.52, 0.40, 0.26),   # raw sienna shadow — warm, earthy shadow transition
            (0.22, 0.16, 0.10),   # near-black ground — rich dark void; Hals let ground read in shadows
            (0.08, 0.06, 0.04),   # near-black void — deeply receding background passages
            (0.86, 0.72, 0.52),   # sunlit highlight — characteristic bright warm cream for lit faces
            (0.64, 0.52, 0.36),   # ochre middle — confident impasto on cheek and brow planes
            (0.38, 0.28, 0.18),   # warm umber — drapery and shadow; richer than neutral grey
        ],
        ground_color=(0.44, 0.34, 0.20),    # warm amber-brown imprimatura — standard Haarlem tradition
        stroke_size=10,                      # confident, bold taches — loaded brush, placed once
        wet_blend=0.14,                      # very low: alla prima means no layered blending
        edge_softness=0.22,                  # crisp directional edges — psychological vivacity not sfumato
        jitter=0.038,                        # significant variation per tache — spontaneous, not mechanical
        glazing=None,                        # no unifying glaze — alla prima; paint is applied once
        crackle=True,                        # 17th-century canvas; aged craquelure in originals
        chromatic_split=False,
        technique=(
            "Frans Hals (1582/3–1666) is the master of alla prima ('all at once') "
            "oil painting — a technique in which wet paint is applied in a single session "
            "without waiting for earlier passages to dry.  Where Gerrit Dou took hours "
            "over a single inch of canvas, Hals completed entire portraits in one energetic "
            "sitting.  The result is a surface alive with visible, directional brushmarks — "
            "called taches — that read from a distance as vivid, observed flesh but reveal, "
            "close up, as a sequence of astonishingly confident individual strokes.  "
            "Hals worked on a warm amber-brown imprimatura (standard Haarlem practice), "
            "building the dark background broadly first, then blocking in the major flesh "
            "masses with loaded brushwork, and finally placing the highlights in single "
            "definitive strokes — never overworked, never blended out.  The highlights "
            "arrive as pure cream-ivory taches that read as sunlight catching a brow or "
            "cheekbone.  His brushstrokes follow the form of the face — they are not random "
            "gestures but contour-following marks that describe volume through their direction "
            "as much as through their tone.  "
            "The result is the first great tradition of 'painterly painting' in Western art — "
            "a surface that acknowledges its own materiality.  Hals's influence on the "
            "Impressionists (particularly Manet) was profound: they saw in his taches the "
            "permission to let the mark show.  "
            "Psychologically, his portraits capture a vivacity no other old-master achieves: "
            "subjects laugh, grin, gesture, and look caught in mid-thought — an impression "
            "that is partly artistic skill and partly the inevitable result of alla prima "
            "speed: the paint's spontaneity mirrors the subject's spontaneity.  "
            "Apply hals_alla_prima_vivacity_pass() after build_form() to add the three "
            "defining qualities: directional tache energy (gradient-direction modulation), "
            "warm imprimatura vivacity in mid-tones, and psychological edge crispness in the "
            "focal area."
        ),
        famous_works=[
            ("The Laughing Cavalier",                   "1624"),
            ("Banquet of the Officers of the St George Militia", "1616"),
            ("Malle Babbe",                             "c. 1633"),
            ("The Gypsy Girl",                          "c. 1628–1630"),
            ("Regents of the Old Men's Almshouse",      "c. 1664"),
            ("Regentesses of the Old Men's Almshouse",  "c. 1664"),
            ("Portrait of Isaac Abrahamszoon Massa",     "1626"),
            ("Young Man with a Skull",                  "c. 1626–1628"),
        ],
        inspiration=(
            "Apply hals_bravura_stroke_pass() as the primary stroke layer encoding Hals's "
            "alla prima bravura: strokes placed once with absolute confidence, following "
            "the form contour flow field at angle_jitter_deg variation (±30° for Hals's "
            "energetic directional range); broken_tone=True activates per-stroke colour "
            "variation simulating wet-into-wet paint picking up slightly different pigment "
            "mixes at each tache; low wet_blend=0.12 keeps strokes distinct and unblended.  "
            "Additionally apply hals_alla_prima_vivacity_pass() after the stroke layer for "
            "three pixel-level refinements: (1) Directional tache energy via gradient "
            "direction field modulation — a spatially new concept in the pipeline; "
            "(2) Warm mid-tone imprimatura vivacity in the flesh zone; (3) Focal "
            "psychological crispness via unsharp mask in the face region."
        ),
    ),

    "gerrit_dou": ArtStyle(
        artist="Gerrit Dou",
        movement="Dutch Golden Age / Fijnschilder",
        nationality="Dutch (Leiden)",
        period="1620–1675",
        palette=[
            (0.96, 0.88, 0.72),   # warm ivory highlight — candlelit peak brightness; creamy Naples yellow warmth
            (0.88, 0.76, 0.56),   # golden amber flesh — lit midtone; Dou's skin glows with candle warmth
            (0.72, 0.58, 0.40),   # warm ochre — mid shadow transition; smooth glaze between light and dark
            (0.48, 0.35, 0.22),   # raw umber shadow — deep flesh shadow; smooth, never harsh
            (0.20, 0.14, 0.08),   # near-black void — niche/background darks; rich, warm near-absence
            (0.82, 0.62, 0.28),   # candle amber — the warm point-source colour; defines lit folds and edges
            (0.58, 0.48, 0.36),   # warm stone grey — niche arch colour; pale warm stone of his framing devices
            (0.30, 0.26, 0.20),   # warm dark brown — drapery shadow; deep without going cold
        ],
        ground_color=(0.62, 0.50, 0.32),    # warm amber imprimatura — shared Leiden tradition with Rembrandt
        stroke_size=2,                       # the finest in the catalog — Dou painted with a magnifying glass
        wet_blend=0.82,                      # extreme glazing: 30+ transparent layers, smooth as enamel
        edge_softness=0.28,                  # crisp, clear contours — his figures are sharply defined, not sfumato
        jitter=0.008,                        # near-zero jitter — his surfaces are glass-smooth
        glazing=(0.76, 0.60, 0.32),          # warm amber-gold candle glaze over the final surface
        crackle=True,                        # 17th-century oak panel; aged craquelure in originals
        chromatic_split=False,
        technique=(
            "Gerrit Dou (1613–1675) was Rembrandt's first and most famous pupil in Leiden, "
            "and the founder of the fijnschilder ('fine painter') tradition that would "
            "define Leiden art for the next century.  He represents the extreme of technical "
            "refinement in the Dutch Golden Age — a painter whose surfaces are as smooth "
            "and luminous as enamel, achieved through up to thirty or more translucent oil-"
            "glaze layers applied over a warm amber imprimatura.  Contemporaries reported "
            "that Dou used a magnifying glass while painting and spent hours allowing dust "
            "to settle before resuming work, to avoid contaminating his perfectly polished "
            "surfaces.  "
            "Dou's defining contribution is the 'niche' composition — a figure framed within "
            "a stone arch or window, caught in a moment of domestic or scholarly life.  The "
            "niche device serves multiple functions: it creates a recession of space, it "
            "frames the figure against a warm candlelit interior, and it gives the composition "
            "a theatrical, stage-like quality that anticipates the Dutch domestic genre "
            "tradition of de Hooch and Vermeer.  Unlike de Hooch's open thresholds, Dou's "
            "niches are enclosed and intimate — the figure is caught in a private moment, "
            "watched rather than encountered.  "
            "Technically, Dou's most distinctive quality is the warm candlelit illumination "
            "of his later works.  His candle scenes (The Night School, The Hermit, Woman "
            "Reading by Candlelight) achieve a warm amber-gold light quality — brighter and "
            "warmer than Rembrandt's chiaroscuro, more intimate than Georges de la Tour's "
            "pure tenebrism.  The candle is always a warm amber-orange, creating rich, "
            "smooth tonal gradients across flesh and drapery.  "
            "Apply gerrit_dou_fijnschilder_pass() after the main build_form() passes to "
            "achieve the enamel surface fineness, candle-warm highlight gold, and warm "
            "point-source gradient that define Dou's intimate interiors."
        ),
        famous_works=[
            ("The Night School",                    "c. 1660–1665"),
            ("Woman Reading by Candlelight",        "c. 1660"),
            ("Self-Portrait",                       "c. 1645"),
            ("The Leiden Baker",                    "c. 1646"),
            ("The Dropsical Woman",                 "c. 1663"),
            ("The Hermit",                          "c. 1670"),
            ("Girl at a Window",                    "c. 1645"),
            ("Young Mother",                        "c. 1658"),
        ],
        inspiration=(
            "Apply gerrit_dou_fijnschilder_pass() to add three defining qualities: "
            "(1) Enamel micro-smoothing — in bright skin zones (lum > 0.62), apply very "
            "gentle Gaussian smoothing at enamel_strength-controlled sigma (0.6–1.4) to "
            "create the glass-like surface polish of 30+ glaze layers, composited at low "
            "opacity to retain texture while adding luminous fineness; (2) Candle-warm "
            "highlight gold — in upper highlights (lum > 0.72), shift toward warm amber-"
            "gold (R+, G+ slightly, B neutral), replicating the warm candle illumination "
            "that characterises Dou's later interiors; (3) Point-source candle gradient — "
            "gerrit_dou_fijnschilder_candle_gradient_pass() applies a radial warm gradient "
            "from a simulated candle position (default: upper-right, x=0.72, y=0.15 in "
            "image-space), adding the warm directional quality of a side-candle to the "
            "overall surface register.  stroke_size=2 requires a fine build_form() pass "
            "before application.  wet_blend=0.82 produces smooth, glass-like blends in "
            "the underpainting and block_in passes.  "
            "edge_softness=0.28: Dou's edges are crisp and clear — no sfumato, no "
            "dissolution — but they are luminously smooth, not harsh.  The niche "
            "architecture creates its own spatial recession."
        ),
    ),
    "bernardino_luini": ArtStyle(
        artist="Bernardino Luini",
        movement="Milanese Renaissance / Leonardesque",
        nationality="Italian (Milanese)",
        period="1480–1532",
        palette=[
            (0.92, 0.84, 0.70),   # warm ivory highlight — peak flesh light; the luminous
                                   # lead-white ground reading through thin warm glaze
            (0.82, 0.70, 0.52),   # warm ochre mid-tone — transitional flesh; the core of
                                   # Luini's smooth Madonna-type skin register
            (0.62, 0.50, 0.36),   # amber-brown mid-shadow — the sfumato transition zone;
                                   # where form melts into shadow without hard edge
            (0.36, 0.28, 0.20),   # warm umber shadow — deep shadow; retains warmth from
                                   # the amber imprimatura reading through thin glazes
            (0.18, 0.16, 0.14),   # near-black void — pure Leonardo dark void; not cold
            (0.46, 0.52, 0.42),   # muted olive-grey — landscape and drapery ground tone;
                                   # the Milanese atmospheric haze of distant terrain
            (0.68, 0.62, 0.78),   # cool violet-grey — sky and distant background; Leonardo-
                                   # school ambient sky quality in the shadow passages
            (0.58, 0.44, 0.28),   # warm sienna drapery — mid-tone garment colour;
                                   # Luini's characteristic warm-toned robe fabric
        ],
        ground_color=(0.72, 0.60, 0.40),    # warm amber-ivory ground — Milanese tradition;
                                             # warmer and lighter than Florentine ochre
        stroke_size=4,                       # fine, polished strokes building seamless surfaces
        wet_blend=0.72,                      # high — Luini's surfaces are seamlessly blended
        edge_softness=0.78,                  # very soft sfumato — edges melt without hard lines
        jitter=0.010,                        # very low — smooth, controlled, no spontaneity
        glazing=(0.72, 0.58, 0.36),          # warm amber glaze — the multi-layer glazing unity
        crackle=True,                        # oil on panel; aged craquelure in originals
        chromatic_split=False,
        technique=(
            "Bernardino Luini (c. 1480/85–1532) was the most celebrated and prolific "
            "follower of Leonardo da Vinci in Milan.  Working in the immediate wake of "
            "Leonardo's Milanese period (1482–1499 and 1506–1513), Luini absorbed the "
            "master's sfumato technique so thoroughly that, until the nineteenth century, "
            "several of his works were attributed to Leonardo himself.  Giorgio Vasari "
            "described him as 'gracious and very sweet in colouring,' and the nineteenth-"
            "century critic John Ruskin considered his Madonnas among the most beautiful "
            "works ever painted.  "
            "Luini's defining contribution to the Milanese tradition was the distillation "
            "of Leonardo's sfumato into a sweet, accessible idiom.  Where Leonardo's own "
            "portraits carry an unresolvable psychological complexity (the Mona Lisa's "
            "ambiguous smile, the Lady with an Ermine's arrested glance), Luini's figures "
            "project serene, idealized beauty — the Madonna type raised to its highest "
            "formal perfection.  His flesh surfaces are among the smoothest in the entire "
            "Renaissance tradition, achieved through many thin glaze layers over a warm "
            "amber-ivory ground, with each layer imperceptible in itself.  "
            "Technically, Luini's most distinctive qualities are: (1) the warm-ivory "
            "highlight glow — his highest flesh lights have a creamy, lead-white quality "
            "that reads as luminous rather than bleached; (2) the cool-violet shadow "
            "delicacy — his deepest shadows carry a barely perceptible blue-violet "
            "atmosphere from ambient sky light (a Leonardo inheritance); and (3) the "
            "seamlessly polished flesh surface — even smoother than Leonardo's own, "
            "carrying the Leonardesque blend to a point of near-supernatural smoothness.  "
            "Apply luini_leonardesque_glow_pass() after the main sfumato passes to "
            "achieve the warm-ivory highlight glow, cool-violet shadow delicacy, and "
            "seamless flesh surface that define Luini's Milanese Madonna portraits."
        ),
        famous_works=[
            ("Susanna at the Bath",                         "c. 1520–1523"),
            ("Madonna delle Rose",                          "c. 1510–1515"),
            ("Christ Carrying the Cross",                   "c. 1513"),
            ("Virgin and Child with Saint Anne",            "c. 1515–1520"),
            ("Herodias with the Head of John the Baptist",  "c. 1525–1530"),
            ("Portrait of a Lady",                          "c. 1520–1525"),
            ("The Crivelli Madonna",                        "c. 1510–1515"),
            ("Salome",                                      "c. 1527–1531"),
        ],
        inspiration=(
            "Apply luini_leonardesque_glow_pass() to add three defining qualities: "
            "(1) Warm-ivory highlight clarification — in upper highlight zones "
            "(lum > highlight_lo=0.70), add a gentle warm-ivory push (R + ivory_r=0.028, "
            "G + ivory_g=0.016, B + ivory_b=0.006) that simulates the lead-white ground "
            "reading through thin warm glaze in Leonardo's school; the highest flesh lights "
            "glow with creamy luminosity rather than bleached whiteness; "
            "(2) Cool-violet shadow delicacy — in deep shadow zones (lum < shadow_hi=0.32), "
            "add a very faint cool-blue-violet lift (B + shadow_violet_b=0.018, "
            "G + shadow_violet_g=0.006, R − shadow_violet_r=0.004) simulating ambient sky "
            "reflection in the shadow passages — a Leonardo-school principle that Luini "
            "inherited and refined; "
            "(3) Sfumato flesh surface smoothing — in the transitional mid-tone zone "
            "[flesh_lo=0.40, flesh_hi=0.74], blend toward a Gaussian-smoothed version at "
            "smooth_strength=0.55 to create Luini's glass-smooth Madonna surface; "
            "for the sfumato_veil_pass() preceding this, use highlight_ivory_lift=0.06 "
            "(session 97 improvement) to pre-warm the highlights before the amber veils "
            "composite over them.  wet_blend=0.72 produces seamlessly blended glazes.  "
            "edge_softness=0.78: the softest in the warm-palette catalog — Luini's edges "
            "dissolve more gently even than Leonardo's own."
        ),
    ),
    # ──────────────────────────────────────────────────────────────────────────
    # Giovanni Antonio Boltraffio  (session 107)
    # ──────────────────────────────────────────────────────────────────────────
    "boltraffio": ArtStyle(
        artist="Giovanni Antonio Boltraffio",
        movement="Milanese High Renaissance / Leonardesque",
        nationality="Italian (Milanese)",
        period="1467–1516",
        palette=[
            (0.88, 0.90, 0.92),   # cool pearl highlight — the signature Boltraffio quality;
                                   # silver-white rather than warm ivory; lead-white ground
                                   # reading through cool pearl glazes, not warm amber;
                                   # B slightly exceeds R, giving a barely perceptible
                                   # cool-silver luminosity at the highlight peak
            (0.85, 0.76, 0.60),   # warm mid-tone flesh — the broad modelled register;
                                   # slightly cooler than Luini, retaining more neutral flesh
            (0.65, 0.54, 0.40),   # amber-grey transition — sfumato dissolution zone;
                                   # Boltraffio's transitions are crisper than Luini's but
                                   # still imperceptibly edged
            (0.38, 0.32, 0.28),   # cool umber mid-shadow — deeper and more neutral than
                                   # Luini's warm amber shadow; Boltraffio retains cool air
            (0.22, 0.22, 0.28),   # cool blue-grey deep shadow — the defining Boltraffio
                                   # shadow quality: distinctly cool-blue, not violet-grey;
                                   # suggests candle or north-light studio illumination
            (0.14, 0.14, 0.20),   # near-black void with blue undertone — shadow terminus;
                                   # preserves Leonardesque void depth but with cool quality
            (0.50, 0.55, 0.48),   # olive-green landscape — Milanese background distance;
                                   # the verdant Lombard plain seen in his Virgin and Child
            (0.72, 0.76, 0.84),   # cool lavender-grey sky — pale atmospheric sky quality;
                                   # cooler and more silvery than Luini's violet-grey
        ],
        ground_color=(0.68, 0.58, 0.42),    # warm amber panel ground — Milanese tradition;
                                             # slightly cooler and darker than Luini's ground
        stroke_size=5,                       # fine, controlled — more precise than Luini
        wet_blend=0.78,                      # high but less extreme than Luini; surfaces are
                                             # smooth but retain slight tonal precision
        edge_softness=0.82,                  # very high sfumato — edges dissolve thoroughly;
                                             # Boltraffio's sfumato is as extreme as Leonardo's
        jitter=0.012,                        # very low — controlled Milanese precision
        glazing=(0.64, 0.56, 0.40),          # cool-warm amber glaze — unifying but cooler than
                                             # Luini's; the pearl surface shows through
        crackle=True,                        # oil on panel; aged craquelure in originals
        chromatic_split=False,
        technique=(
            "Giovanni Antonio Boltraffio (1467–1516) was Leonardo da Vinci's most gifted and "
            "personally close Milanese pupil.  While Bernardino Luini distilled Leonardo's "
            "sfumato into warmth and sweetness — a Madonna-type idealism of amber ivory flesh "
            "and serene expression — Boltraffio refined the same technique into a crystalline, "
            "psychologically penetrating idiom that is in many ways closer to the master's own "
            "complex spirit.  Giorgio Vasari named him among Leonardo's best pupils, and Boltraffio "
            "was the only Milanese pupil to sign work jointly with Leonardo (the Louvre Narcissus).  "
            "The defining Boltraffio quality — the one that immediately distinguishes his work from "
            "Luini's — is the pearl highlight: where Luini's highest flesh lights glow with warm "
            "ivory luminosity (lead-white ground reading through amber glaze), Boltraffio's peak "
            "highlights have a cool, almost silver-white quality — pearl rather than ivory, "
            "cool-luminous rather than warm-glowing.  This is achieved through a slightly cooler "
            "glaze sequence and a tendency toward neutral-silver in the final highlight layer.  "
            "His shadow quality is equally distinctive: where Luini's shadows retain amber warmth "
            "throughout, Boltraffio's deepen into genuinely cool blue-grey in the deepest passages, "
            "suggesting ambient north light or reflected sky in the shadow.  The mid-flesh "
            "transitions are sfumato-dissolved but have a jewel-like tonal precision that makes "
            "his portraits appear almost crystalline — forms emerge from shadow with extraordinary "
            "clarity at the moment of emergence, then dissolve back into darkness with equal "
            "imperceptibility.  Technically, the Portrait of Ginevra Bentivenuti (Louvre) shows "
            "his mastery of the three-quarter pose, with an expression of cool, withdrawn "
            "psychological depth that influenced portraiture across the Milanese school.  "
            "Apply boltraffio_pearled_sfumato_pass() as the primary Boltraffio effect: this adds "
            "the pearl highlight clarification (cool-silver rather than warm-ivory), the deep "
            "cool-blue shadow atmosphere, and the mid-flesh crystalline clarity that distinguish "
            "Boltraffio from his warmer Milanese colleagues."
        ),
        famous_works=[
            ("Portrait of Ginevra Bentivenuti",    "c. 1490–1500"),
            ("Virgin and Child",                    "c. 1490–1495"),
            ("Narcissus",                           "c. 1490–1500"),
            ("Madonna of the Rose",                 "c. 1510"),
            ("Portrait of a Young Man",             "c. 1490"),
            ("Casio's Virgin",                      "c. 1500"),
            ("Polymnia (Muse)",                     "c. 1490–1500"),
        ],
        inspiration=(
            "Apply boltraffio_pearled_sfumato_pass() to add the three defining Boltraffio "
            "qualities that separate his sfumato from Luini's warmer variant: "
            "(1) Pearl highlight clarification — in upper highlight zones (lum > pearl_lo=0.72), "
            "add a cool-silver push (R + pearl_r=0.012, G + pearl_g=0.018, B + pearl_b=0.025) "
            "creating silver-pearl rather than warm-ivory; Boltraffio's peaks are neutrally "
            "bright, approaching silver-white on the forehead and cheekbone ridge; "
            "(2) Cool-blue deep shadow atmosphere — in deep shadow zones (lum < shadow_hi=0.30), "
            "add a distinctly cool-blue atmospheric lift "
            "(B + shadow_b=0.024, G + shadow_g=0.008, R - shadow_r=0.006) creating the ambient "
            "north-light or sky-reflection quality in Boltraffio's darkest passages — deeper and "
            "more distinctly blue than Luini's gentle violet-grey; "
            "(3) Mid-flesh crystalline clarity — in the mid-flesh zone (flesh_lo=0.38, "
            "flesh_hi=0.70), blend toward a very mildly sharpened version of the canvas "
            "(clarity_sigma=0.8, clarity_strength=0.18) to simulate the jewel-like tonal "
            "precision that makes Boltraffio's forms emerge from shadow with unusual clarity; "
            "use opacity=0.38.  Precede with sfumato_veil_pass() to establish the dissolved "
            "edge quality before adding the Boltraffio pearl clarification over it."
        ),
    ),
    # ──────────────────────────────────────────────────────────────────────────
    # Federico Barocci  (session 98)
    # ──────────────────────────────────────────────────────────────────────────
    "federico_barocci": ArtStyle(
        artist      = "Federico Barocci",
        movement    = "Umbrian Mannerism / proto-Baroque",
        nationality = "Italian (Marchigian / Urbino)",
        period      = "c. 1535–1612",
        palette     = [
            (0.92, 0.76, 0.62),   # warm rose-ivory highlight
            (0.86, 0.62, 0.50),   # peach-rose upper midtone
            (0.76, 0.50, 0.38),   # warm flesh penumbra (petal flush zone)
            (0.60, 0.36, 0.26),   # shadow flesh — warm sienna
            (0.44, 0.26, 0.18),   # deep shadow — warm burnt umber
            (0.36, 0.46, 0.62),   # cool blue-grey ambient veil
            (0.68, 0.56, 0.38),   # warm amber middle ground
            (0.30, 0.40, 0.54),   # distant cool blue landscape
        ],
        ground_color    = (0.84, 0.78, 0.66),   # warm ivory "bianca" ground
        stroke_size     = 5,
        wet_blend       = 0.68,
        edge_softness   = 0.72,
        jitter          = 0.018,
        glazing         = (0.60, 0.44, 0.28),   # amber-rose final glaze
        crackle         = True,
        chromatic_split = False,
        technique       = (
            "Federico Barocci (c. 1535–1612) was the supreme colorist of Umbrian "
            "Mannerism and the critical bridge between late-Renaissance tradition and "
            "the fully realised Baroque.  Born in Urbino in the Marche, he worked "
            "almost exclusively for the courts and churches of central Italy, refusing "
            "prestigious commissions from Rome that might have altered his singularly "
            "personal development.  His work was admired by Rubens (who owned several "
            "Barocci drawings), Annibale Carracci, and Bellori, all of whom recognised "
            "in him qualities that the Bolognese reform of painting would systematise "
            "a generation later.  "
            "Barocci's most distinctive technical achievement was his use of chalk "
            "pastel studies — 'pasteletti' — as full colour preparatory tools.  He was "
            "among the first Italian artists to employ pastels not merely for drawing "
            "but for exploring the exact colour relationships that would appear in the "
            "finished oil.  This practice fed directly into his oil technique: each "
            "finished surface was built from multiple warm-cool glaze layers over a "
            "luminous warm ground (the 'bianca'), creating a surface quality that "
            "appears almost pastellic — soft, powdery, translucent — while retaining "
            "the optical depth of oil glazing.  "
            "The defining quality of Barocci's flesh passages is his handling of the "
            "penumbra — the transitional zone between direct light and shadow (roughly "
            "lum 0.42–0.62).  Where Leonardo dissolved this boundary with grey sfumato "
            "and Rembrandt charged it with psychological weight, Barocci filled it with "
            "a warm rose-pink luminosity that is uniquely his own.  This 'petal flush' "
            "— soft, warm, slightly rosy — gives his flesh surfaces a quality closer "
            "to living skin than paint: the cheek facing away from the main light "
            "carries a warm rose breath, as if the body's internal warmth rises through "
            "the surface.  "
            "Three defining technical qualities: (1) The petal flush — in the penumbra "
            "zone [penumbra_lo=0.42, penumbra_hi=0.62], a warm rose-pink bloom (R+ "
            "rose_r=0.022, G+ rose_g=0.008, B- rose_b=0.010) deposited with organic "
            "softness; (2) The bianca ground luminosity — in upper mid-tones "
            "[bianca_lo=0.58, bianca_hi=0.82], a warm creamy lift (bianca_r=0.018, "
            "bianca_g=0.012, bianca_b=0.006) simulating the pale warm ground reading "
            "through thin glazes; (3) Warm perimeter dissolution — figure edges dissolve "
            "into warm ambient haze (edge_dissolve_strength=0.35) like Leonardo's sfumato "
            "but warmer and more colorful.  Apply barocci_petal_flush_pass() after all "
            "major sfumato and glaze passes."
        ),
        famous_works = [
            ("Annunciation (Vatican)",                  "1582–1584"),
            ("Madonna of the People (Uffizi)",          "1575–1579"),
            ("Rest on the Flight into Egypt (Vatican)", "1570–1573"),
            ("Entombment (Senigallia)",                 "1579–1582"),
            ("Portrait of Francesco II della Rovere",   "c. 1572"),
            ("Nativity (Prado)",                        "c. 1597"),
            ("Visitation (Santa Maria in Vallicella)",  "1583–1586"),
            ("Stigmatization of St Francis (Urbino)",   "c. 1594–1595"),
        ],
        inspiration = (
            "Apply barocci_petal_flush_pass() to encode three defining qualities of "
            "Barocci's Umbrian flesh technique: "
            "(1) Petal flush — in the penumbra zone [penumbra_lo=0.42, "
            "penumbra_hi=0.62], where Barocci's most characteristic rose-pink warmth "
            "lives, add a soft warm flush (R + rose_r=0.022, G + rose_g=0.008, "
            "B - rose_b=0.010).  This is the 'pasteletti' quality translated into oil: "
            "the transitional zone between light and shadow carries a living rose warmth "
            "rather than a grey or cool dissolution.  The flush is distributed with "
            "Gaussian feathering (blur_radius=4.0) so it appears organic and breathing "
            "rather than mechanically banded; "
            "(2) Bianca ground luminosity — in the upper mid-tone zone "
            "[bianca_lo=0.58, bianca_hi=0.82], add a warm creamy lift "
            "(R + bianca_r=0.018, G + bianca_g=0.012, B + bianca_b=0.006) simulating "
            "the pale warm 'bianca' ground reading through Barocci's multiple thin "
            "transparent glazes — the paper-white luminosity visible in the Madonna of "
            "the People and the Vatican Annunciation; "
            "(3) Warm perimeter dissolution — in the outer rim of the figure "
            "(distance > edge_dissolve_radius=0.72 from composition centre), add a "
            "gentle Gaussian blur (sigma=edge_dissolve_sigma=2.2) at "
            "edge_dissolve_strength=0.35, creating the warm ambient edge loss that "
            "Barocci borrowed from Leonardo but warmed and colourised.  "
            "wet_blend=0.68 produces the seamlessly blended glaze-on-glaze surface.  "
            "edge_softness=0.72: very soft Umbrian sfumato, warmer than Leonardo's.  "
            "Use opacity=0.38 to integrate naturally with the accumulated prior passes."
        ),
    ),

    # ── Pierre Bonnard ────────────────────────────────────────────────────────
    # Randomly selected artist for session 99's inspiration.
    # Pierre Bonnard (1867–1947) began as a founding member of the Nabis group —
    # young Post-Impressionists who admired Gauguin's flat colour zones and dark
    # cloisonné outlines — but his mature work departed radically from that early
    # aesthetic into something sui generis: a late style (c. 1920–1947, painted
    # largely at his villa Le Cannet near Cannes) of almost hallucinatory colour
    # saturation, where hot orange, cadmium yellow, and acid violet jostle in
    # domestic spaces bathed in Mediterranean light.  Bonnard's signature effect
    # is 'chromatic vibration': warm and cool notes placed in immediate proximity
    # so the eye reads them simultaneously as colour and as light — a perceptual
    # oscillation that makes his interiors pulse and breathe.
    "pierre_bonnard": ArtStyle(
        artist="Pierre Bonnard",
        movement="Post-Impressionism / Nabi / Chromatic Intimisme",
        nationality="French",
        period="1891–1947",
        palette=[
            (0.96, 0.72, 0.18),   # cadmium yellow — the dominant hot note
            (0.88, 0.45, 0.15),   # burnt orange — warm mid-tone anchor
            (0.55, 0.18, 0.52),   # warm violet — shadow complement to the yellows
            (0.30, 0.62, 0.42),   # muted sage green — garden / tablecloth
            (0.70, 0.82, 0.88),   # pale cerulean — cool window light
            (0.92, 0.85, 0.58),   # warm cream — sunlit interior surfaces
            (0.20, 0.14, 0.38),   # deep indigo — darkest shadow
        ],
        ground_color=(0.88, 0.78, 0.52),    # warm ochre-cream (sun-baked Cannet wall)
        stroke_size=9,
        wet_blend=0.35,                      # low: adjacent dabs remain distinct
        edge_softness=0.42,                  # moderate: forms readable but not crisp
        jitter=0.055,                        # high: each stroke varies — no flat zones
        glazing=(0.76, 0.62, 0.28),          # warm amber-ochre final glaze
        crackle=False,
        chromatic_split=False,               # not pointillist dots — organic warm/cool oscillation
        technique=(
            "Chromatic vibration — Bonnard's defining mature technique.  In the "
            "intimate interiors and garden scenes painted at Le Cannet (1920–1947), "
            "he placed warm (cadmium yellow, burnt orange) and cool (cerulean, "
            "muted violet) touches in immediate adjacency throughout every zone of "
            "the canvas: not just in the highlights or shadows, but pervasively in "
            "mid-tones and even in the deep shadows.  The eye, unable to resolve "
            "these near-complementary pairs into a single flat tone, reads them as "
            "light itself — a pulsing optical shimmer that transcends the actual "
            "luminance range of the pigments.  "
            "This is distinct from Seurat's pointillism (which is systematic and "
            "retinal-theory-driven) and from Impressionist broken colour (which "
            "pursues atmospheric naturalism).  Bonnard's oscillation is emotional "
            "and perceptual: the warm-cool pairs are calibrated to the mood of the "
            "room, the hour, the season.  His method was to pin a canvas to his "
            "studio wall and work on it intermittently over months or years, "
            "adjusting the colour temperature of each zone until the vibration felt "
            "right — an intuitive, atmospheric calibration rather than a system.  "
            "The palette is notoriously warm-dominant: cadmium yellow and burnt "
            "orange anchor most compositions, with cool violet and cerulean serving "
            "as the oscillating complement.  Shadows are never grey or black — they "
            "are deep indigo-violet, warm brown, or saturated green.  Lights are "
            "not white — they are the warmest possible yellow or cream.  "
            "Pipeline implementation: bonnard_chromatic_vibration_pass() injects "
            "warm/cool oscillation pairs across the mid-tone zone using a "
            "low-frequency sinusoidal spatial pattern seeded by Perlin noise, "
            "so the warm/cool beats appear organic rather than mechanical.  "
            "The oscillation amplitude is small (0.02–0.04 per channel) so it "
            "reads as texture and life rather than as visible colour change."
        ),
        famous_works=[
            ("The Dining Room in the Country",      "1913"),
            ("The Bowl of Milk",                    "c. 1919"),
            ("Nude in the Bath",                    "1936"),
            ("The Garden",                          "1936"),
            ("Table in Front of the Window",        "1934–1935"),
            ("Mimosa, Le Cannet",                   "1945"),
            ("The Studio with Mimosa",              "1939–1946"),
            ("Marthe at Her Toilette",              "1908"),
        ],
        inspiration=(
            "Apply bonnard_chromatic_vibration_pass() to inject the signature "
            "warm/cool oscillation throughout the mid-tone zone [lum 0.28–0.76].  "
            "The oscillation is spatially organic — driven by a low-frequency "
            "Perlin noise field — so warm and cool beats alternate in patches "
            "of 15–30 px rather than pixel-by-pixel.  "
            "Warm phase: +R warm_amp, -B warm_amp * 0.55 (orange-yellow push).  "
            "Cool phase: +B cool_amp, -R cool_amp * 0.45 (violet-cerulean push).  "
            "The pass is intentionally subtle (opacity 0.30–0.40): it should read "
            "as a warm quality of light in the flesh and costume zones rather than "
            "as visible colour manipulation.  "
            "wet_blend=0.35 keeps adjacent dabs distinct so the vibration is "
            "preserved in the final surface.  "
            "High jitter (0.055) ensures no flat zones — every mark varies."
        ),
    ),

    # ── Masaccio ───────────────────────────────────────────────────────────────
    "masaccio": ArtStyle(
        artist="Masaccio",
        movement="Proto-Renaissance / Early Florentine Renaissance",
        nationality="Italian",
        period="1422–1428",
        palette=[
            (0.76, 0.52, 0.22),   # warm burnt sienna — primary flesh and robe tone
            (0.55, 0.38, 0.16),   # raw umber mid-shadow — transition from lit to dark
            (0.24, 0.16, 0.08),   # deep shadow umber — deepest architectural void
            (0.82, 0.72, 0.48),   # warm ochre highlight — Masaccio's lit planes
            (0.46, 0.50, 0.42),   # cool neutral — distant landscape and architectural stone
            (0.68, 0.58, 0.38),   # golden imprimatura — warm Florentine panel ground
        ],
        ground_color=(0.58, 0.48, 0.28),    # warm ochre-umber panel ground
        stroke_size=8,
        wet_blend=0.42,                      # moderate: forms built in convincing tonal layers
        edge_softness=0.38,                  # crisp architectural edges — no sfumato dissolution
        jitter=0.025,                        # controlled: Masaccio's authority, not impressionistic scatter
        glazing=(0.62, 0.48, 0.22),          # warm amber unifying final glaze
        crackle=True,                        # fresco and early tempera surfaces show age
        chromatic_split=False,               # no chromatic splitting — volumetric tonal unity
        technique=(
            "Architectonic mass — Masaccio's defining achievement.  Between 1422 "
            "and his death at 27 in 1428, he transformed Italian painting by "
            "replacing the decorative flatness of the International Gothic with a "
            "rigorous, sculptural approach to form and light.  His figures — in the "
            "Brancacci Chapel frescoes (c. 1424–1427) and the Trinity at Santa Maria "
            "Novella (c. 1427) — have genuine physical weight; they stand on the "
            "ground, cast shadows, and occupy convincing three-dimensional space.  "
            "This revolution was accomplished through a single, radical insight: "
            "that natural light, applied consistently from a single source, builds "
            "believable form more effectively than any amount of linear description.  "
            "Masaccio's light is not the decorative modelling of his predecessors "
            "(Giotto's flat tonal zones, the Gothic masters' gold-leaf halos) but a "
            "genuinely directional, raking source that catches the high planes of "
            "face and drapery and drops deep, near-black shadows behind projecting "
            "forms.  The result is a technique often described as 'architectonic': "
            "forms read as masses of stone or clay modelled in space, not as flat "
            "silhouettes decorated with pattern.  "
            "His palette is austere by the standards of his era: burnt sienna, raw "
            "umber, warm ochre, with architectural stone grey in the backgrounds.  "
            "There is none of the lapis-lazuli blue or vermilion red that enriched "
            "the altarpieces of his contemporaries — Masaccio was after solidity, "
            "not splendour.  "
            "His shadow modelling is the key contribution to this pipeline: the "
            "penumbra zone (lum 0.28–0.52) receives a subtle contrast enhancement "
            "that makes the shadow-to-light transition read as a physical edge rather "
            "than a tonal gradient.  The highlight side receives a warm ochre lift "
            "that catches the upper-left light source described in the portrait.  "
            "Deep shadow zones are gently deepened to maintain the architectural "
            "void that gives Masaccio's forms their gravity.  "
            "Pipeline implementation: masaccio_architectonic_mass_pass() targets "
            "the penumbra transition zone with a localised contrast boost, deepens "
            "the deep-shadow void slightly, and adds a warm ochre glow to the lit "
            "side of the figure, restoring sculptural weight that the accumulated "
            "sfumato-heavy prior passes have softened."
        ),
        famous_works=[
            ("The Expulsion from the Garden of Eden (Brancacci Chapel)", "c. 1424–1427"),
            ("The Tribute Money (Brancacci Chapel)",                      "c. 1424–1427"),
            ("The Trinity, Santa Maria Novella",                          "c. 1427"),
            ("Madonna and Child with Angels (Pisa Altarpiece)",           "1426"),
            ("St Peter Healing with His Shadow (Brancacci Chapel)",       "c. 1424–1427"),
        ],
        inspiration=(
            "Apply masaccio_architectonic_mass_pass() to restore sculptural mass "
            "and architectural shadow weight to the accumulated soft-sfumato surface.  "
            "Target the penumbra zone [lum 0.28–0.52]: apply a gentle S-curve "
            "contrast boost in this band to sharpen the shadow/light boundary, "
            "giving forms the physicality Masaccio achieved through raking directional "
            "light.  "
            "Deep shadow zone [lum < 0.24]: deepen by a small multiplicative "
            "factor (shadow_deepen=0.04–0.08) to maintain the architectural void.  "
            "Lit zone [lum > 0.62]: add warm ochre lift (earth_r=0.018, "
            "earth_g=0.012) that echoes the burnt-sienna/ochre palette — the upper-"
            "left light source warms the high planes of face and drapery.  "
            "The pass respects the figure mask so the background landscape is "
            "unaffected — Masaccio's sculptural weight is a figure-zone quality.  "
            "opacity=0.28: this pass should add solidity, not reverse the sfumato; "
            "the cumulative effect should read as weight and presence beneath the "
            "atmospheric surface of the 99 prior sessions."
        ),
    ),

    # ── James Tissot (1836–1902) ──────────────────────────────────────────────────
    # Pipeline key: tissot_fashionable_gloss_pass() — enamel surface clarity,
    # specular sheen enhancement, chromatic richness in warm midtones, cool
    # crystalline highlights.
    "tissot": ArtStyle(
        artist      = "James Tissot",
        movement    = "Victorian Social Realism / Aesthetic Movement",
        nationality = "French-British",
        period      = "1860–1902",
        palette     = [
            (0.90, 0.86, 0.74),   # warm pale cream / ivory (fashionable dress highlights)
            (0.62, 0.50, 0.38),   # warm tan / buff (flesh mid-tone)
            (0.22, 0.26, 0.38),   # deep navy-blue (gentleman's coat / water shadows)
            (0.72, 0.36, 0.22),   # warm terracotta / rose (fashionable dress accents)
            (0.54, 0.60, 0.50),   # cool grey-green (Thames riverbank / garden foliage)
            (0.82, 0.70, 0.44),   # warm amber-gold (Thames light / afternoon sun)
        ],
        ground_color  = (0.78, 0.74, 0.62),   # warm pale ochre-cream canvas preparation
        stroke_size   = 5,
        wet_blend     = 0.80,
        edge_softness = 0.62,
        jitter        = 0.018,
        glazing       = (0.62, 0.50, 0.28),
        crackle       = False,
        chromatic_split = False,
        technique     = (
            "James Tissot occupies a distinctive position in Victorian painting — a "
            "Frenchman in London who combined the precise academic surface of the "
            "Beaux-Arts with an almost photographic eye for the visual detail of "
            "fashionable social life.  His technical method belongs firmly to the "
            "academic tradition of Ingres and Delaroche: oil paint applied in thin, "
            "controlled layers over a carefully prepared warm-toned ground, each "
            "surface built up through successive glazes until the result is a "
            "seamless, almost lacquered finish with no visible brushwork on the "
            "figure's skin or the principal fabrics.  "
            "His most distinctive quality is what might be called fashionable gloss: "
            "a combination of high local contrast in mid-tone passages, specular-like "
            "sheen in the brightest highlights of silk and satin, and a chromatic "
            "richness in the warm dress fabrics that makes his women appear almost "
            "to be lit from within.  This is not the warm impasto glow of Rembrandt "
            "or the atmospheric shimmer of Monet — it is the precision of a craftsman "
            "who has studied how woven silk reflects light, and who reproduces that "
            "observation with systematic fidelity.  "
            "The palette is warm in the foreground — cream-ivory, buff flesh tones, "
            "warm amber of afternoon Thames light — and cools progressively into the "
            "distance: the grey-green of riverside foliage, the deep navy of water "
            "in shadow, the pale cool sky.  This is not atmospheric sfumato (his "
            "edges are clear and purposeful) but atmospheric recession through colour "
            "temperature alone, a quality he shared with the Impressionists he knew "
            "in Paris but never fully joined.  "
            "His later career — after the death of his companion Kathleen Newton — "
            "turned entirely to biblical illustration (La Vie de Notre-Seigneur "
            "Jésus-Christ, 1886–1896), which required the same technical precision "
            "applied to Middle Eastern landscape and costume detail.  Both phases — "
            "fashionable Victorian and devotional biblical — share the same root "
            "quality: an almost uncomfortable clarity of observation, as if the "
            "painter trusts the eye more than any system of pictorial convention."
        ),
        famous_works  = [
            ("The Ball on Shipboard",               "c. 1874"),
            ("Too Early",                           "1873"),
            ("The Thames",                          "c. 1876"),
            ("October",                             "1877"),
            ("La Femme à Paris — L'Ambitieuse",     "1883–1885"),
            ("The Last Evening",                    "1873"),
            ("Hush!",                               "1875"),
            ("The Reception",                       "c. 1883–1885"),
        ],
        inspiration   = (
            "Apply tissot_fashionable_gloss_pass() as the primary stylistic pass for "
            "this artist.  The pass simulates four defining qualities of Tissot's "
            "Victorian academic surface:  "
            "(1) Enamel surface clarity — mild local contrast enhancement in the "
            "mid-tone range [lum 0.28–0.72] (clarity_str ≈ 0.10–0.14) that sharpens "
            "the perceived detail of fabric and skin without adding artificial "
            "HDR-style crunchiness.  Implemented as a mild unsharp-mask: "
            "canvas − gaussian_blur(canvas, σ≈4) * clarity_str.  "
            "(2) Specular surface sheen — in the brightest non-highlight zones "
            "(sheen_thresh ≈ 0.72) add a subtle luminance lift (sheen_strength ≈ "
            "0.06–0.10) that simulates the specular reflectance of fine silk and "
            "satin.  This is the micro-quality that makes Tissot's dress fabrics "
            "look physically present rather than painted.  "
            "(3) Chromatic richness — in the warm mid-tone zone, apply a modest "
            "saturation boost (chroma_boost ≈ 0.05–0.08) by pulling each channel "
            "away from luminance-grey in proportion to its existing deviation.  "
            "This replicates the vivid fabric quality of his fashionable interiors.  "
            "(4) Cool highlight crystallization — in the very brightest zones "
            "(lum > 0.85), apply a slight cool shift (highlight_cool ≈ 0.03–0.06, "
            "B↑ R↓) that turns hot-white highlights into the crisp, crystalline "
            "whites of silk and linen under English afternoon light, distinct from "
            "the warm ivory highlights of the sfumato tradition.  "
            "Use opacity ≈ 0.24–0.32 so the pass adds Tissot's precise fashionable "
            "surface without overriding the accumulated atmospheric depth of prior "
            "sessions.  The Mona Lisa should gain Tissot's clarity and presence "
            "while retaining Leonardo's atmospheric mystery."
        ),
    ),

    # ── Carlo Dolci (1616–1686) ───────────────────────────────────────────────────
    # Pipeline key: dolci_florentine_enamel_pass() — hyper-smooth devotional enamel
    # surface finish, deep walnut-brown shadow glazes, crystalline ivory highlights,
    # and an introspective psychological stillness inspired by his devotional panels.
    "carlo_dolci": ArtStyle(
        artist      = "Carlo Dolci",
        movement    = "Florentine Baroque / Devotional Realism",
        nationality = "Italian",
        period      = "1640–1686",
        palette     = [
            (0.90, 0.78, 0.62),   # warm ivory flesh highlight — naples-cream
            (0.72, 0.54, 0.36),   # mid-tone flesh — warm amber ochre
            (0.42, 0.28, 0.14),   # deep shadow — warm walnut-brown
            (0.14, 0.08, 0.04),   # absolute dark — near-black void
            (0.58, 0.44, 0.28),   # penumbra zone — amber-brown transition
            (0.82, 0.70, 0.50),   # highlight bloom — ivory over warm ground
        ],
        ground_color  = (0.38, 0.28, 0.16),   # warm walnut imprimatura (copper panels)
        stroke_size   = 4,
        wet_blend     = 0.88,
        edge_softness = 0.55,
        jitter        = 0.008,
        glazing       = (0.55, 0.40, 0.18),    # warm amber resin glaze
        crackle       = True,
        chromatic_split = False,
        technique     = (
            "Carlo Dolci was the most technically obsessive painter of the Florentine "
            "Baroque: a devotional artist who approached each painting as an act of "
            "spiritual discipline and who was capable of spending years — sometimes "
            "literally years — on a single figure.  His speed was negligible; his "
            "surface finish was extraordinary.  He worked primarily on copper panels "
            "and small-format wood, which provided the ideal non-absorbent ground for "
            "his technique of building form through dozens of thin, transparent oil-"
            "glaze layers, each dried before the next was applied, in the Flemish "
            "tradition transmitted through Florentine channels.  The result is a skin "
            "surface that approaches the quality of fine enamelware: seamless, warm, "
            "extraordinarily deep in its shadows, and crystalline in its highlights.  "
            "His shadows are among the richest in the tradition — built from repeated "
            "glazes of warm walnut-brown and raw umber over a warmly toned copper "
            "ground, the depth of darkness achieved not through a single opaque dark "
            "but through the accumulation of many transparent layers, each adding a "
            "fraction of absorption while retaining the translucency of the paint film.  "
            "The result is a shadow zone that appears to have interior depth — you seem "
            "to look into the shadow rather than at an opaque surface.  "
            "His highlights are the opposite: pure, almost glassy ivory touches over "
            "the smooth flesh surface, applied with the finest possible brush — "
            "crystalline and precise in a way that has more in common with a goldsmith's "
            "work than with the wet-into-wet oil traditions of his Venetian contemporaries.  "
            "The devotional stillness of his figures — heavy-lidded saints, weeping "
            "Madonnas, absorbed Magdalenes — is amplified by the surface quality: "
            "a portrait that feels as if it has been resolved to absolute completion, "
            "with no rough edge, no unresolved mark, no evidence of hesitation."
        ),
        famous_works  = [
            ("St. Cecilia at the Organ",               "c. 1671–1672"),
            ("The Virgin and Child with Saints",        "c. 1665"),
            ("Salome with the Head of St. John",        "c. 1670"),
            ("David in Prayer",                         "c. 1640"),
            ("The Penitent Magdalene",                  "c. 1660–1665"),
            ("Christ Carrying the Cross",               "c. 1646"),
            ("Portrait of Ainolfo de' Bardi",           "c. 1632–1635"),
        ],
        inspiration   = (
            "Apply dolci_florentine_enamel_pass() as the primary stylistic pass for "
            "this artist.  The pass simulates four defining qualities of Dolci's "
            "hyper-smooth devotional enamel surface:  "
            "(1) Enamel surface refinement — a bilateral-style local smoothing in the "
            "flesh and mid-tone zones, going beyond Tissot's unsharp-mask clarity to "
            "actively reduce micro-texture variation.  Applied with a narrow Gaussian "
            "blend (sigma ≈ 2.5–3.5) to merge adjacent tonal variations within skin "
            "zones — simulating the glass-smooth surface of paint glazed over copper.  "
            "(2) Shadow depth enrichment — in the deep shadow zone (lum < 0.32), apply "
            "warm walnut-brown glazes (R+ modest, G+ very slight, B dampened) that add "
            "interior depth without lifting the darks toward grey.  The key quality is "
            "warmth without brightness: the shadows should feel deep and amber-brown, "
            "not lifted.  Use shadow_depth_str ≈ 0.06–0.12.  "
            "(3) Crystal highlight clarification — in the very brightest zones "
            "(lum > 0.82), apply a subtle luminance lift (highlight_lift ≈ 0.04–0.08) "
            "that brings the very tip of the highlight to a near-white crystalline "
            "purity — the goldsmith's touch on the enamel surface.  Unlike Tissot's "
            "cool crystallization (B↑ R↓), Dolci's highlights remain warm ivory "
            "(R+ modest, neutral G, B neutral).  "
            "(4) Penumbra amber resonance — in the transition zone between light and "
            "shadow (lum 0.30–0.55), apply a very faint warm-amber glow (R+ slight, "
            "G+ very slight, B dampened) that simulates the amber radiance of his "
            "penumbra zones, built from many transparent layers of warm-coloured glaze.  "
            "Use opacity ≈ 0.28–0.38 so the pass adds Dolci's enamel depth and devotional "
            "stillness without overriding the accumulated sfumato atmosphere of prior sessions."
        ),
    ),

    # ── Henri de Toulouse-Lautrec (1864–1901) ────────────────────────────────────
    # Pipeline key: lautrec_essence_pass() — matte surface desaturation, spidery
    # diagonal hatching in mid-tones, warm-cool graphic separation.
    "toulouse_lautrec": ArtStyle(
        artist      = "Henri de Toulouse-Lautrec",
        movement    = "Post-Impressionism / Belle Époque",
        nationality = "French",
        period      = "1880–1901",
        palette     = [
            (0.78, 0.62, 0.18),   # warm mustard / cadmium yellow ochre
            (0.52, 0.12, 0.18),   # burgundy red / carmine
            (0.26, 0.36, 0.22),   # deep olive / sap green
            (0.20, 0.20, 0.28),   # charcoal blue-grey (shadow zone)
            (0.82, 0.68, 0.58),   # warm cream / cardboard ground tone
            (0.58, 0.32, 0.48),   # dusty rose-violet (mid flesh)
        ],
        ground_color  = (0.76, 0.66, 0.50),   # raw cardboard warm mid-tone
        stroke_size   = 6,
        wet_blend     = 0.08,
        edge_softness = 0.14,
        jitter        = 0.055,
        glazing       = None,
        crackle       = False,
        chromatic_split = False,
        technique     = (
            "Henri de Toulouse-Lautrec developed his signature technique, known as "
            "'peinture à l'essence', by thinning oil paint heavily with turpentine "
            "and applying it directly to raw cardboard rather than stretched canvas.  "
            "The absorbent cardboard surface immediately drew the oil binder out of "
            "the paint, leaving behind a layer of dry, chalky pigment with an almost "
            "matte, poster-like quality quite unlike the luminous oil surfaces of the "
            "Old Master tradition.  This was not a technical limitation but a deliberate "
            "aesthetic choice: Lautrec was drawn to the flat, graphic quality that the "
            "technique produced, which resonated with his deep engagement with Japanese "
            "ukiyo-e woodblock prints and their bold, unmodulated color zones separated "
            "by clear, purposeful contour lines.  "
            "His approach to form was that of a draughtsman who happened also to be a "
            "painter.  He drew constantly — in cafés, brothels, backstage at the Moulin "
            "Rouge — building an extraordinary vocabulary of expressive posture, gesture, "
            "and psychological character through line alone.  When he painted, this linear "
            "intelligence survived in the directional, spidery hatching that appears in his "
            "shadow zones and mid-tone passages: loose parallel strokes, each carrying both "
            "tonal and directional information simultaneously, a technique that recalls the "
            "engravers he admired and the lithographic process in which he worked in parallel "
            "to his paintings.  "
            "His palette for portraiture was warm and contrasted: the cardboard ground itself "
            "contributed an ochre warmth that read through any thinly applied layer; shadows "
            "were pushed toward cool charcoal or blue-grey; mid-tone flesh zones sat between "
            "these poles in a distinctive dusty rose-violet that was more graphic than "
            "naturalistic.  Highlights were spare — a warm cream or mustard-yellow touch "
            "rather than the white impasto highlight of academic painting.  "
            "The result is a surface that reads flat in reproduction (as his lithographic "
            "posters were designed to) but has an immediate, urgent psychological presence "
            "in the original: the figure seems seized and set down in a single visual "
            "decision, without the accumulative uncertainty of the academic painter who "
            "corrects, glazes, and revises toward perfection.  Lautrec's paintings feel "
            "known at a glance because they were painted by an artist who already knew "
            "exactly what he was looking for before he picked up the brush."
        ),
        famous_works  = [
            ("At the Moulin Rouge",                 "1892–1895"),
            ("La Goulue at the Moulin Rouge",        "1891"),
            ("Jane Avril Dancing",                   "1892"),
            ("The Laundress",                        "1889"),
            ("Divan Japonais (poster)",              "1892–1893"),
            ("Cha-U-Kao at the Moulin Rouge",        "1895"),
            ("The Clownesse Cha-U-Kao",              "1895"),
        ],
        inspiration   = (
            "Apply lautrec_essence_pass() as the primary stylistic pass for this "
            "artist.  The pass simulates the three defining qualities of Lautrec's "
            "peinture à l'essence technique:  "
            "(1) Matte surface desaturation — a mild, spatially uniform saturation "
            "reduction across the whole canvas (matte_str ≈ 0.10–0.14) that replaces "
            "the luminous, oil-rich surface of traditional glazing with the dry, "
            "chalky quality of turpentine-diluted paint soaked into cardboard.  "
            "(2) Spidery diagonal hatching — in the mid-tone and shadow zones "
            "[lum 0.22–0.62], apply sparse diagonal marks at approximately 45° "
            "(hatch_angle ≈ 42–48°) that darken slightly (hatch_darkness ≈ 0.06–0.10) "
            "and simulate the loose cross-hatching of his draughtsmanship.  The density "
            "should remain low (hatch_density ≈ 0.20–0.30) to read as texture rather "
            "than as a repeating pattern.  "
            "(3) Warm-cool graphic separation — push warm pixels (high R/G ratio) "
            "toward mustard-amber (warm_boost ≈ 0.05–0.08 in R channel) and cool "
            "pixels (high B ratio) toward blue-grey (cool_boost ≈ 0.04–0.06 in B "
            "channel), separating the warm cardboard-tone foreground from the cool "
            "shadow zones in the manner of his flat, Japonisme-influenced graphic "
            "language.  "
            "Use opacity ≈ 0.28–0.34 so the pass adds the matte, graphic character "
            "without fully destroying the underlying sfumato depth built by prior "
            "sessions.  The Mona Lisa should retain her atmospheric mystery while "
            "gaining Lautrec's dry, immediate, psychological presence."
        ),
    ),

    # ── Luca Giordano (1634–1705) ────────────────────────────────────────────────
    # Known as "Fa Presto" (does-it-quickly) for his astonishing speed.
    # Pipeline key: giordano_rapidita_luminosa_pass() — warm golden aureole
    # sweeping from upper-right, dynamic baroque radiance, Venetian colour richness.
    "luca_giordano": ArtStyle(
        artist      = "Luca Giordano",
        movement    = "Neapolitan Baroque",
        nationality = "Italian",
        period      = "1650–1705",
        palette     = [
            (0.92, 0.78, 0.42),   # warm golden aureole — sunlit ivory-gold
            (0.72, 0.52, 0.22),   # mid amber-gold — penumbra warmth
            (0.30, 0.18, 0.08),   # deep warm brown shadow — Baroque void
            (0.62, 0.74, 0.88),   # cool blue zenith — ceiling fresco sky
            (0.80, 0.60, 0.36),   # warm ochre flesh highlight
            (0.22, 0.28, 0.44),   # cool violet-blue deep shadow
        ],
        ground_color  = (0.42, 0.30, 0.14),   # warm walnut-brown imprimatura
        stroke_size   = 7,
        wet_blend     = 0.62,
        edge_softness = 0.48,
        jitter        = 0.040,
        glazing       = (0.68, 0.52, 0.22),    # warm golden resin glaze
        crackle       = True,
        chromatic_split = False,
        technique     = (
            "Luca Giordano was the most prodigiously prolific painter of the Italian "
            "Baroque and arguably the most technically versatile: a Neapolitan master "
            "who could absorb, synthesise, and deploy any prior style — Raphael, "
            "Titian, Veronese, Rubens, Rembrandt, Velázquez — with equal facility and "
            "then move on.  His nickname 'Fa Presto' (does-it-quickly) came from his "
            "father, who would drive him to work faster, but it captured a genuine "
            "quality of his genius: a speed that was not carelessness but concentrated "
            "intelligence, an ability to read a large composition whole and execute it "
            "in a single sustained arc of energy without losing coherence or luminosity.  "
            "He was reportedly able to paint ceiling frescoes of vast scope — the "
            "Palazzo Medici-Riccardi, the Escorial Library, the Certosa di San "
            "Martino — in weeks that other painters would spend months planning.  "
            "His technique was built on the Venetian tradition transmitted through "
            "Ribera (with whom he trained in Naples) and enriched by direct study of "
            "Titian, Veronese, and Rubens: a warm imprimatura of reddish-brown or "
            "walnut-brown, over which he built form rapidly in broad, confident wet-"
            "into-wet strokes, using a palette dominated by warm golden yellows, deep "
            "warm browns, and cool cerulean or lapis blue accents.  His light source "
            "was typically theatrical and upper-right, creating a warm golden aureole "
            "that swept diagonally across the composition — a celestial radiance "
            "characteristic of his altarpieces and ceiling frescoes.  "
            "Unlike the slow accretion of Dolci's enamel passes or the sfumato "
            "dissolution of Leonardo, Giordano's surfaces are built in a single "
            "confident day: visible directional brushwork, active edges, and a surface "
            "energy that reads as dynamic rather than perfected.  His shadows are warm "
            "and deep — rich Baroque voids with a residual amber warmth — and his "
            "highlights are warm golden-ivory rather than cool or crystalline.  "
            "The defining quality in the pipeline is the 'rapidità luminosa': a warm "
            "golden radiance that sweeps across the upper portion of the composition "
            "from the upper-right, brightening and warming the background sky zone "
            "and adding a subtle warm-gold rim to the lit edges of the figure — "
            "simulating the theatrical upper illumination that characterises his "
            "altarpieces and the grand narrative sweep of his ceiling paintings."
        ),
        famous_works  = [
            ("Triumph of Judith",                                "c. 1704"),
            ("The Rape of the Sabine Women",                     "c. 1680–1685"),
            ("Allegory of Human Life and the Medici (ceiling)",  "1682–1683"),
            ("Escorial Library ceiling frescoes",                "1692–1694"),
            ("Saint Michael Vanquishing Satan",                  "c. 1663"),
            ("The Fall of the Rebel Angels",                     "c. 1660–1665"),
            ("Certosa di San Martino Treasury frescoes",         "1704"),
        ],
        inspiration   = (
            "Apply giordano_rapidita_luminosa_pass() as the primary stylistic pass "
            "for this artist.  The pass simulates the defining quality of Giordano's "
            "large-scale Baroque illumination — the warm golden aureole that sweeps "
            "from the upper-right across the composition — in three stages:  "
            "(1) Upper-right golden aureole in background — in the upper-right "
            "quadrant of the background zone, apply a warm golden brightening "
            "(R+ strong, G+ moderate, B+ slight) that falls off with distance from "
            "the upper-right corner.  The aureole should feel like celestial light "
            "entering from above, not a spotlight: use aureole_r ≈ 0.04–0.07, "
            "aureole_g ≈ 0.02–0.04, aureole_b ≈ 0.005–0.012 with a large Gaussian "
            "radius (radius ≈ 0.65–0.80 of canvas width) so the effect is gradual "
            "and atmospheric, not concentrated.  "
            "(2) Warm golden rim on figure's lit edges — on the lit (upper-right) "
            "side of the figure silhouette, add a very faint warm-gold edge "
            "brightening (rim_strength ≈ 0.03–0.06) to simulate the way his figures "
            "are touched by the theatrical upper illumination.  "
            "(3) Shadow violet depth — in the deep shadow zone (lum < 0.30), add a "
            "very faint cool violet push (B+ very slight, R+ very slight warm "
            "recovery) simulating the Venetian-influenced shadow colour that "
            "Giordano absorbed from Titian and Ribera.  "
            "Use opacity ≈ 0.28–0.36 so the golden sweep adds luminous drama "
            "without overriding the accumulated sfumato and enamel depth."
        ),
    ),

    # ── Guercino (Giovanni Francesco Barbieri) ───────────────────────────────
    # Giovanni Francesco Barbieri — universally known as "il Guercino"
    # (the Squinter, from an eye condition) — was the supreme master of the
    # Emilian Baroque school, born in Cento near Bologna in 1591.  His early
    # works (c. 1617–1627) are characterised by a dramatic Caravaggesque
    # chiaroscuro suffused with warm amber-ochre light and astonishingly
    # expressive surfaces; his late works (after 1642, influenced by Guido
    # Reni's idealism) adopt a lighter, more classical palette but retain his
    # characteristic penumbra warmth and emotional intelligence.
    #
    # Defining qualities for the pipeline:
    #   • Penumbra amber: the transition zone from lit flesh to shadow is
    #     suffused with a golden ochre-amber warmth — a slow, concentrated
    #     golden surrender to shadow that is not found in Caravaggio's abrupt
    #     chiaroscuro or Leonardo's cool sfumato.
    #   • Upper-left directional light: unlike Giordano's theatrical upper-
    #     right, Guercino's light enters from the upper left, creating an
    #     intimate warm gradient across the figure.
    #   • Deep shadow warm retention: shadows stay warm umber-brown, never
    #     cold black — the dark ground shows through.
    #   • Drawing-informed mark-making: perhaps the greatest draughtsman of
    #     his century; pen-and-wash intelligence informs his painted surfaces.
    "guercino": ArtStyle(
        artist        = "Giovanni Francesco Barbieri (il Guercino)",
        movement      = "Italian Baroque / Emilian School",
        nationality   = "Italian",
        period        = "c. 1617–1666",
        palette       = [
            (0.90, 0.76, 0.54),   # warm ivory-gold flesh highlight
            (0.78, 0.60, 0.36),   # golden amber midtone flesh
            (0.60, 0.44, 0.24),   # warm ochre penumbra — the defining zone
            (0.38, 0.26, 0.14),   # warm umber transitional shadow
            (0.14, 0.10, 0.06),   # dark warm-brown shadow void
            (0.42, 0.18, 0.10),   # deep crimson-brown drapery accent
            (0.62, 0.58, 0.72),   # muted cerulean-lavender sky/distance
            (0.72, 0.62, 0.28),   # warm golden-ochre middle ground
        ],
        ground_color  = (0.18, 0.13, 0.07),    # warm dark brown — shows through
                                                # deep shadows, warming the voids
        stroke_size   = 9,
        wet_blend     = 0.28,
        edge_softness = 0.52,
        jitter        = 0.038,
        glazing       = (0.62, 0.44, 0.18),    # warm amber-umber glaze
        crackle       = True,
        chromatic_split = False,
        technique     = (
            "Guercino's technique is built on a dark warm-brown imprimatura that "
            "allows shadow zones to breathe with a residual amber warmth rather "
            "than falling to cold black.  His single-source directional light "
            "(typically upper-left) creates a warm Gaussian spotlight illuminating "
            "flesh in golden-amber highlights.  The penumbra zone — the transition "
            "band from lit flesh to deep shadow — glows with a concentrated ochre-"
            "amber warmth that is the hallmark of his flesh passages: not "
            "Caravaggio's hard chiaroscuro, not Leonardo's cool sfumato, but a "
            "warm confident gradient that spends time in the amber penumbra before "
            "surrendering to umber shadow.  His draughtsmanship informed his painted "
            "surfaces — marks are calligraphic and confident in mid-tones, softly "
            "blended in highlights.  His late-period palette lightens and idealises "
            "under Guido Reni's influence, but the amber penumbra warmth never leaves."
        ),
        famous_works  = [
            ("The Incredulity of Saint Thomas",    "1621"),
            ("Samson Captured by the Philistines", "1619"),
            ("Et in Arcadia ego",                  "c. 1618–1622"),
            ("The Dead Christ with Angels",        "1617–1618"),
            ("Aurora (Casino Ludovisi ceiling)",   "1621"),
            ("Jacob Blessing the Sons of Joseph",  "c. 1620"),
            ("Semiramis",                          "c. 1645"),
        ],
        inspiration   = (
            "Apply guercino_penumbra_warmth_pass() as the primary stylistic pass. "
            "Three stages: "
            "(1) Penumbra amber enrichment — in the luminance band from "
            "penumbra_lo (≈0.28) to penumbra_hi (≈0.62), apply a warm amber-ochre "
            "lift (R+ strong, G+ moderate, B- slight) via a Gaussian bell mask "
            "peaking at the midpoint of the penumbra range.  This is the defining "
            "quality of Guercino's flesh — a concentrated amber warmth in the "
            "transition zone that glows with emotional intensity. "
            "(2) Upper-left directional warmth — apply a gentle warm gradient "
            "falling off from the upper-left corner (light_cx≈0.18, light_cy≈0.08) "
            "with a large Gaussian radius (≈0.85 of canvas width), simulating "
            "Guercino's characteristic upper-left domestic light source. "
            "(3) Shadow warm retention — in the deepest shadow zone (lum < "
            "shadow_hi≈0.28), add a subtle warm-umber retention (R+ slight, G+ very "
            "slight) to prevent cold black voids — the dark ground warmth visible "
            "through the shadows.  "
            "Use opacity ≈ 0.25–0.32 so the amber penumbra enrichment adds "
            "emotional warmth without competing with the accumulated sfumato depth."
        ),
    ),

    # ── Jusepe de Ribera ──────────────────────────────────────────────────────
    # Jusepe de Ribera (1591–1652), known as "Lo Spagnoletto" (The Little
    # Spaniard), was born in Valencia but spent his entire mature career in
    # Naples — then a Spanish viceroyalty — where he fused the Spanish
    # tradition of austere naturalism with the most brutal form of Italian
    # Caravaggism.  His tenebrism is the most uncompromising in the history of
    # painting: near-black void shadows that consume forms completely, from which
    # lit passages emerge with almost shocking physical presence.
    #
    # What distinguishes Ribera from Caravaggio — the primary influence — is the
    # *texture* he brings to his shadows.  Caravaggio's dark passages are smooth,
    # pooling, and absolute; Ribera's are alive with gritty, almost granular
    # visible brushwork.  The physical substance of paint — its body and grain —
    # is particularly apparent in his shadow areas, as if the darkness itself is
    # made of rough, inhabited matter rather than an empty void.  His highlighted
    # passages, conversely, are warm amber-ivory, modelled with a confident
    # directness that feels sculptural: the light lands and the form is there,
    # without Leonardo's slow dissolution or Rubens' rosy flush.
    #
    # Ribera's subjects — aged philosophers, tortured martyrs, working-class
    # models with calloused hands — carry a dignity that comes from unflinching
    # observation.  He painted poverty, age, and suffering as subjects worthy of
    # the full weight of his technique.  His wrinkled skin, veined hands, and
    # coarse fabrics are rendered with the same loving precision Flemish masters
    # reserved for silk and precious metals.
    "ribera": ArtStyle(
        artist="Jusepe de Ribera",
        movement="Spanish-Neapolitan Baroque",
        nationality="Spanish (worked in Naples)",
        period="1610–1652",
        palette=[
            (0.72, 0.55, 0.35),   # warm amber highlight flesh
            (0.52, 0.40, 0.25),   # mid-tone warm sienna flesh
            (0.30, 0.22, 0.13),   # deep warm umber penumbra
            (0.12, 0.09, 0.06),   # near-black warm void shadow
            (0.65, 0.52, 0.32),   # ochre costume accent
            (0.18, 0.15, 0.10),   # dark warm-brown ground tone
        ],
        ground_color=(0.10, 0.07, 0.04),    # very dark warm-brown imprimatura
        stroke_size=8,
        wet_blend=0.32,                      # low blend — visible brushwork especially in shadows
        edge_softness=0.28,                  # mostly crisp found edges
        jitter=0.045,
        glazing=(0.55, 0.40, 0.22),         # dark warm umber unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Ribera's technique begins with an extremely dark warm-brown imprimatura "
            "that establishes the near-black void as the default state: the ground "
            "IS the shadow, and the painting is the act of retrieving form from "
            "darkness through selective illumination.  His light source is invariably "
            "single and directional — typically upper-left — creating a theatrical "
            "chiaroscuro even more extreme than Caravaggio's.  Where Caravaggio "
            "organised his darks into clean, pooling shapes, Ribera's shadow areas "
            "retain visible gritty brushwork: the marks are present even in the "
            "deepest darks, giving a granular textural quality to the voids.  His "
            "highlights on aged skin are warm amber-ivory, applied with sculptural "
            "directness over a warm sienna mid-tone.  Brushwork is legible "
            "throughout; his colourist range is narrow — warm earth tones, with "
            "occasional crimson or blue accents — making rare bright colours explode "
            "against the dominant warm-black tonality."
        ),
        famous_works=[
            ("The Martyrdom of Saint Philip",          "1639"),
            ("Jacob and Esau",                          "1637"),
            ("The Clubfoot",                            "1642"),
            ("Drunken Silenus",                         "1626"),
            ("Saint Jerome and the Angel of Judgment",  "1626"),
            ("The Sense of Touch (Blind Sculptor)",     "c. 1615–1616"),
            ("Saint Andrew",                            "1631"),
        ],
        inspiration=(
            "Apply ribera_gritty_tenebrism_pass() as the primary stylistic pass. "
            "Three stages: "
            "(1) Near-black void reinforcement — in the deepest shadow zone "
            "(lum < shadow_hi ≈ 0.22), strengthen near-black with warm umber "
            "ground grain (R+ tiny, G+ tiny) and gritty granular noise that "
            "simulates the dark brown imprimatura and Ribera's visible shadow "
            "brushwork, preventing flat digital black. "
            "(2) Upper-left directional amber spotlight — a Gaussian warmth from "
            "the upper left (light_cx ≈ 0.15, light_cy ≈ 0.08) that warms and "
            "lifts the lit zone; more dramatic and sharper than Guercino. "
            "(3) Gritty shadow penumbra texture — in the mid-dark zone "
            "(penumbra_lo ≈ 0.22 to penumbra_hi ≈ 0.45), overlay granular noise "
            "(grain_strength ≈ 0.025–0.040) creating Ribera's distinctive "
            "shadow grain — darkness as inhabited, textured matter.  "
            "Use opacity ≈ 0.35–0.45."
        ),
    ),

    # ── Giovanni Battista Moroni ───────────────────────────────────────────────
    # Randomly selected artist for session 108's inspiration.
    # Giovanni Battista Moroni (c. 1520–1579) was a Bergamasque painter whose
    # portraits are among the most psychologically direct works of the entire
    # Italian Renaissance.  He trained under Moretto da Brescia in Brescia — a
    # city whose painters emphasised naturalism over the idealism of Venice or
    # Florence — and spent most of his career in Bergamo serving middle-class
    # patrons: merchants, lawyers, clergy, and guild masters who wanted to be
    # seen as they were, not as gods.
    #
    # The quality that makes Moroni singular in the history of Western portraiture
    # is what might be called **silver presence**: an uncanny sense of physical
    # reality achieved not through micro-detail (Flemish) or glossy finish
    # (Bronzino) but through a startlingly accurate tonal structure.  His
    # highlights have a distinctive cool silver quality — where Raphael's
    # lights glow with warm ivory and Bronzino's are cold enamel, Moroni's
    # occupy a middle register: cool, restrained, almost metallic, yet still
    # warm enough to read as living flesh.  The effect is of a person caught in
    # real north-window light in a Bergamasque courtyard.
    #
    # His shadow passages are equally characteristic: warm amber-ochre recovery
    # prevents the darks from going grey or cold.  Unlike Ribera (who lets his
    # voids go near-black) or Leonardo (whose shadows dissolve into sfumato haze),
    # Moroni's shadows retain an earthy warmth that keeps the face readable in
    # three dimensions without theatrical drama.
    #
    # Moroni also has a remarkable ability to render textile — brocade, velvet,
    # lace — with precision that borders on trompe-l'oeil, while keeping the
    # face broadly painted and psychologically alive.  This contrast between
    # elaborate costume and direct face is the structural drama of his portraits.
    #
    # His most celebrated work, "Il Sarto" (The Tailor, c. 1570, National Gallery
    # London), captures his essence: a craftsman holding his shears, gazing
    # directly at the viewer with unnerving calm, his dark costume rendered in
    # precise detail while his face carries the entire psychological weight of
    # the picture.  The Louvre's Portrait of an Old Man with a Book and Brera's
    # various Bergamasque gentlemen show the full range of his cool, unhurried,
    # profoundly truthful portrait vision.
    # ── Session 109 — new artist: Bernardo Strozzi ────────────────────────────
    #
    # Bernardo Strozzi (1581–1644), called "Il Cappuccino" (having taken Capuchin
    # orders in 1597, though he later left and was briefly imprisoned) and "Il Prete
    # Genovese" (The Genoese Priest), occupies a pivotal position between the
    # Genoese and Venetian schools of the early seventeenth century.  Born in Genoa,
    # he trained under Pietro Sorri before immersing himself in the rich Genoese
    # painting culture that had been galvanised by Peter Paul Rubens's two extended
    # visits (1600–02 and 1607–08).  Rubens left Genoa transformed: the fluid alla
    # prima loading of the brush, the warm amber-chestnut shadows, the frank
    # vitality of flesh — all these qualities permeate Strozzi's mature Genoese work.
    #
    # Strozzi moved to Venice around 1631, where he remained until his death.  There
    # he absorbed the Venetian tradition — the warm glazing depth of Titian, the
    # theatrical chiaroscuro of Tintoretto, the luminous atmosphere of the lagoon —
    # and synthesised it with his Genoese Rubensian foundation to produce a bravura
    # oil style unlike any other in the seicento: rich, saturated, physically
    # present, and emotionally direct.
    #
    # His palette is one of the warmest in seventeenth-century painting.  The
    # shadows are not the near-black voids of Caravaggio or Ribera but warm
    # chestnut-amber darks, as if the darkness itself were suffused with candlelight.
    # His midtones glow with rose-peach warmth; his highlights are loaded and creamy,
    # applied with a confidence that suggests he rarely needed to rework a surface.
    # His famous "Old Woman at the Mirror" (c. 1615) encodes all of this: warm amber
    # darks, rosy flesh, impasto cream highlights, the whole surface singing with
    # physical and chromatic energy.
    #
    # Technically, Strozzi worked on a warm brown imprimatura — raw umber or burnt
    # sienna thinned to translucency — which glows through the paint layers and
    # unifies the image with a golden internal warmth.  Over this he built form
    # with fluid, loaded strokes, wet into wet, adjusting colour temperature as the
    # forms turned from light into shadow.  His brushwork is confident and visible,
    # especially in the shadows and backgrounds, where broad calligraphic marks
    # are left unreworked.  His flesh surfaces are more finished, but even there
    # the underlying energy of the loaded brush is perceptible.
    "strozzi": ArtStyle(
        artist="Bernardo Strozzi",
        movement="Genoese-Venetian Baroque",
        nationality="Italian",
        period="c. 1581–1644",
        palette=[
            (0.92, 0.80, 0.62),   # warm Naples-ivory highlight flesh — the cream of a loaded brush
            (0.78, 0.58, 0.42),   # warm rose-sienna mid-flesh — glowing with Genoese warmth
            (0.55, 0.36, 0.22),   # warm chestnut mid-shadow — amber heat in the turning flesh
            (0.35, 0.22, 0.14),   # warm umber deep shadow — not cold, not black; glowing amber dark
            (0.20, 0.14, 0.10),   # near-black warm void — Strozzi's darkest passages retain warmth
            (0.68, 0.45, 0.28),   # golden ochre accent — collar trim, fabric highlights
            (0.42, 0.28, 0.38),   # deep wine-violet drapery — rich Venetian costume depth
            (0.82, 0.62, 0.48),   # warm buff imprimatura tone — the ground showing through
        ],
        ground_color=(0.42, 0.30, 0.18),   # warm burnt-sienna-umber imprimatura ground
        stroke_size=7,
        wet_blend=0.50,
        edge_softness=0.38,
        jitter=0.028,              # moderate: Strozzi's loaded brush introduces organic variation
        glazing=(0.58, 0.42, 0.22),  # warm amber-chestnut unifying glaze
        crackle=True,              # oil on canvas — 17th-century aging appropriate
        chromatic_split=False,     # warm Baroque colorism, not divisionist splitting
        technique=(
            "Bravura warmth — Strozzi's defining quality.  His paintings are physically "
            "present in a way that pure chiaroscuro painters (Caravaggio, Ribera) never "
            "quite achieve: the warmth lives in the shadows as much as in the lights, "
            "unifying the entire tonal range in a golden amber-chestnut coherence.  "
            "His ground is warm — raw umber or burnt sienna — and it shows through, "
            "especially in the mid-tones and at the edges of forms, contributing an "
            "internal luminosity that cannot be faked by surface glazing alone.  "
            "Over this warm ground he built flesh with rose-peach mid-tones, loading "
            "the brush for the cream highlights and laying them in confident single "
            "strokes.  The shadows he resolved with broad amber-chestnut marks, "
            "warm enough to read as part of the same colour family as the lights.  "
            "This is the opposite of the Caravaggist approach: where Caravaggio uses "
            "near-black voids to intensify the drama of light, Strozzi keeps his "
            "shadows warm and accessible, maintaining the sitter's presence even in "
            "the darkest passages.  "
            "His handling of the loaded brush — the impasto highlight — is the most "
            "immediately distinctive quality.  Where Rembrandt reserves his thickest "
            "paint for the darkest shadows, Strozzi loads the brush for the lights, "
            "creating a physical relief on the canvas surface that catches raking "
            "illumination and gives the flesh an almost tactile luminosity.  "
            "The Venetian influence, absorbed after his move to Venice in 1631, "
            "added a deeper colour saturation and a greater range of atmospheric "
            "transitions — qualities he merged seamlessly with his Genoese Rubensian "
            "foundation, producing the richest, most chromatic Baroque portraits of "
            "northern Italy."
        ),
        famous_works=[
            ("Old Woman at the Mirror",          "c. 1615"),
            ("The Cook",                          "c. 1625"),
            ("Parable of the Talents",            "c. 1630"),
            ("Portrait of Antonio Grimani",       "c. 1635–40"),
            ("Saint Cecilia with Two Angels",     "c. 1620"),
            ("Allegory of Fame",                  "c. 1635–36"),
            ("Portrait of a Gentleman in Armour", "c. 1630"),
        ],
        inspiration=(
            "Apply strozzi_amber_impasto_pass() as the defining stylistic pass.  "
            "Three stages that encode Strozzi's warm Genoese-Venetian signature: "
            "(1) Amber shadow enrichment — in the shadow zone (lum < shadow_hi ≈ 0.38), "
            "shift decisively toward warm chestnut-amber: R + amber_r (strong), "
            "G + amber_g (moderate), B - amber_b (notable reduction — removes cold cast).  "
            "Strozzi's darks glow; they are never cold or grey.  This warms the deepest "
            "tonal zones and gives the shadow passages their characteristic candlelit quality.  "
            "(2) Impasto highlight bloom — in the upper highlight zone (lum > hi_lo ≈ 0.72), "
            "apply a warm creamy bloom: slight R + cream_r, slight G + cream_g, "
            "slight B - cream_b.  This is the loaded-brush quality: cream-warm, "
            "not cool-silver like Moroni, not pearl-blue like Boltraffio, but warm "
            "Naples-ivory loaded paint.  Also apply a subtle local luminance boost "
            "(multiply by hi_boost ≈ 1.04) to push the peak highlights slightly brighter, "
            "simulating the physical relief of impasto paint catching the light.  "
            "(3) Warm mid-tone vitality — in the mid-tone zone [mid_lo, mid_hi], "
            "apply a gentle warm-rose saturation tint: small R + rose_r, tiny B - rose_b.  "
            "Strozzi's flesh mid-tones are warm rose-sienna; this step adds the "
            "characteristic glowing vitality that distinguishes his flesh from the "
            "cooler mid-tones of the Venetians.  "
            "Use opacity ≈ 0.38–0.48."
        ),
    ),

    # ── Giovanni Battista Salvi da Sassoferrato ────────────────────────────────
    "sassoferrato": ArtStyle(
        artist="Giovanni Battista Salvi da Sassoferrato",
        movement="Roman Baroque / Devotional Classicism",
        nationality="Italian",
        period="1609–1685",
        palette=[
            (0.88, 0.76, 0.60),   # warm ivory skin highlight — purest flesh
            (0.72, 0.58, 0.42),   # warm sienna mid-tone flesh
            (0.12, 0.18, 0.68),   # pure ultramarine — the defining Sassoferrato blue
            (0.08, 0.10, 0.45),   # deep ultramarine shadow — lapislazuli depth
            (0.38, 0.30, 0.22),   # warm umber — earth undertone beneath drapery
            (0.92, 0.90, 0.88),   # cool pearl-white highlight — translucent skin peak
            (0.28, 0.24, 0.52),   # violet-blue midtone in drapery folds
        ],
        ground_color=(0.60, 0.52, 0.36),    # warm ochre imprimatura — Romanist ground
        stroke_size=5,
        wet_blend=0.82,                      # very blended — Sassoferrato's seamless glazing
        edge_softness=0.72,                  # soft devotional calm — edges present but never harsh
        jitter=0.012,                        # minimal: devotional precision, controlled surface
        glazing=(0.68, 0.60, 0.45),          # warm amber final unifying glaze
        crackle=True,                        # oil on canvas — 17th-century aging appropriate
        chromatic_split=False,               # pure devotional naturalism, no divisionism
        technique=(
            "Pure devotion — Sassoferrato's defining quality.  Born Giovanni Battista "
            "Salvi in the small Marche town of Sassoferrato, he worked in Rome throughout "
            "the seventeenth century producing an extraordinary corpus of devotional "
            "Madonnas and saints whose chromatic purity and technical refinement stand "
            "entirely apart from the theatricality of the Baroque mainstream.  "
            "His ultramarine is the most saturated blue in Western painting — not the "
            "purplish-blue of Flemish painters or the grey-blue of atmospheric distance, "
            "but a burning, concentrated lapis lazuli blue of almost impossible purity, "
            "built up through multiple glaze layers over a warm ochre ground so that "
            "the colour seems to glow with internal light rather than reflecting it.  "
            "This is the blue of the Virgin's mantle — theologically specific (lapis "
            "lazuli was reserved for the Madonna in medieval and Renaissance iconography) "
            "and technically consummate.  "
            "His flesh is the counterpart: ivory-warm in the lights, porcelain-smooth "
            "in surface, with a cool pearl quality at the highest highlight points that "
            "gives the impression of light passing through translucent skin rather than "
            "bouncing off opaque pigment.  Where Leonardo achieves this through sfumato "
            "(atmospheric dissolution), Sassoferrato achieves it through patient glazing: "
            "warm ochre imprimatura, warm flesh layers, cool pearl final glaze — the "
            "cumulative effect of transparent paint over a warm ground that shows through "
            "every layer.  "
            "His compositions are reduced to essentials: a face, hands, the blue mantle.  "
            "No landscape, no drama, no narrative.  The power comes from chromatic purity "
            "and the quality of psychological stillness — his Virgins appear not "
            "photographed but distilled: the concept of serene spiritual absorption "
            "made visible as paint."
        ),
        famous_works=[
            ("Virgin in Prayer",                  "c. 1640–1650"),
            ("The Virgin and Child",              "c. 1650"),
            ("Head of the Virgin",                "c. 1640"),
            ("Virgin and Child with Saint Anne",  "c. 1660"),
            ("Sleeping Child",                    "c. 1640"),
            ("The Virgin Mary",                   "c. 1654"),
        ],
        inspiration=(
            "Apply sassoferrato_pure_devotion_pass() as the defining stylistic pass.  "
            "Three stages encode Sassoferrato's chromatic signature: "
            "(1) Ultramarine purity — in blue-predominant zones (b0 > r0 + ultra_thresh "
            "and b0 > g0 + ultra_thresh), boost blue and damp red contamination, "
            "building the saturated lapis depth through a graduated mask.  "
            "(2) Porcelain skin glow — in the upper highlight zone (lum > pearl_lo ≈ 0.76), "
            "apply a subtle cool pearl shift: slight R reduction, slight B lift, giving "
            "the translucent quality of light through ivory skin rather than opaque "
            "white paint.  "
            "(3) Ultramarine shadow depth — in shadow zones where blue is dominant, "
            "deepen toward lapislazuli darkness with a controlled violet-blue enrichment.  "
            "Use opacity ≈ 0.28–0.38."
        ),
    ),

    # ── Orazio Gentileschi ────────────────────────────────────────────────────
    "orazio_gentileschi": ArtStyle(
        artist="Orazio Gentileschi",
        movement="Italian Baroque / Caravaggesque / Courtly Naturalism",
        nationality="Italian",
        period="c. 1590–1639",
        palette=[
            (0.90, 0.84, 0.70),   # cool ivory-silver highlight flesh — clear north light
            (0.72, 0.58, 0.42),   # warm mid-tone flesh — earthy sienna quality
            (0.42, 0.32, 0.20),   # warm umber shadow — never cold, never void-black
            (0.80, 0.74, 0.80),   # cool silver-grey highlight — characteristic courtly light
            (0.88, 0.70, 0.22),   # warm gold-ochre satin — his spectacular fabric colour
            (0.62, 0.34, 0.26),   # deep red damask — saturated but not theatrical
            (0.44, 0.52, 0.70),   # cool blue-grey atmospheric recession / sky
        ],
        ground_color=(0.50, 0.44, 0.30),    # warm neutral ground — Tuscan warmth under cool daylight
        stroke_size=6,
        wet_blend=0.52,                      # moderate — controlled, not dissolved; fabric edges hold
        edge_softness=0.48,                  # moderate — softer than Bronzino, crisper than sfumato
        jitter=0.018,                        # restrained — precise naturalism without scatter
        glazing=(0.70, 0.66, 0.52),          # cool-warm silver-buff final glaze
        crackle=True,                        # oil on canvas — appropriate for 17th-century aging
        chromatic_split=False,               # pure naturalism; no optical colour-splitting
        technique=(
            "Silver daylight — the defining quality of Orazio Gentileschi's mature "
            "Baroque naturalism.  Unlike his contemporary Caravaggio (whose single "
            "harsh light carves figures from near-black void) or the Flemish masters "
            "(whose light is warm amber-candlelight), Orazio works with cool, even, "
            "aristocratic north-facing daylight — the light of a London or Genoa "
            "studio in overcast winter, soft but precise, without drama or obscurity.  "
            "Trained in Caravaggio's circle in Rome around 1600, he absorbed the "
            "revolutionary naturalist programme but tempered it: his tenebrism is never "
            "brutal, his shadows are never void, his light is never theatrical.  Instead "
            "he achieved a serene, inhabited quality — figures who seem genuinely present "
            "in real space under real light.  "
            "His second signature is chromatic precision in fabrics.  Where Caravaggio's "
            "draperies are generalised vehicles of form, Orazio's are specific: shimmering "
            "gold satin, vivid red damask, cool blue silk — each rendered with a close "
            "observation that anticipates the 18th-century tradition of fabric painting.  "
            "His palette within a given work is often narrow in its range but exceptional "
            "in its precision: he achieves luminosity through chromatic accuracy rather "
            "than tonal contrast.  "
            "Technical analysis of his panels (he worked in both panel and canvas) "
            "suggests he used a warm ochre imprimatura ground, built his forms through "
            "a careful dead-colouring stage, then laid cool final lights in lead white "
            "with small quantities of smalt — giving his highlight flesh tones a cool, "
            "slightly blue-tinged silver that is entirely characteristic.  "
            "His career spanned Rome, Genoa, Paris (court of Marie de' Medici), and "
            "finally London (court of Charles I, 1626–1639), where he died.  Each move "
            "brought a new courtly audience with sophisticated visual expectations — "
            "which may explain the refined, elegant quality that distinguishes him from "
            "the rougher Caravaggisti of Naples and Sicily."
        ),
        famous_works=[
            ("Lute Player", "c. 1612–1620"),
            ("Rest on the Flight into Egypt", "1628"),
            ("Danaë", "c. 1621–1622"),
            ("Judith and Her Maidservant with the Head of Holofernes", "c. 1608–1609"),
            ("The Penitent Magdalene", "c. 1615–1621"),
            ("Saint Cecilia Playing a Lute", "c. 1617–1620"),
        ],
        inspiration=(
            "Apply orazio_silver_daylight_pass() as the defining stylistic pass.  "
            "Three stages encoding Orazio's cool daylight signature: "
            "(1) Silver highlight coolness — in the upper highlight zone (lum > hi_lo ≈ 0.68), "
            "apply a gentle cool shift: R - silver_r_damp (tiny), B + silver_b_lift (modest). "
            "This is the cool north-window daylight quality of Orazio's lead-white highlights "
            "— not the warm ivory of southern sun nor the cold blue of Mannerist artifice, "
            "but the honest silver of real overcast daylight.  "
            "(2) Midtone chroma lift — in the midtone band [mid_lo, mid_hi], apply a "
            "gentle saturation boost (chroma_lift ≈ 0.015–0.025) that enhances the chromatic "
            "identity of each colour zone.  This encodes Orazio's precision with fabric colour: "
            "his golds are more golden, his reds more vivid, without tipping into "
            "impressionistic scatter.  Implemented as a move toward the mean-hue direction "
            "from grey.  "
            "(3) Cool shadow control — in shadow zones (lum < shadow_hi), apply a very gentle "
            "cool-grey shift that prevents the darks from retaining the Strozzi amber or "
            "Guercino warm-penumbra warmth: slight R - cool_r_damp, slight B + cool_b_lift.  "
            "Orazio's shadows are cool and controlled — not the warm umber void of the Roman "
            "Caravaggisti but a restrained, atmospheric coolness.  "
            "Use opacity ≈ 0.28–0.38."
        ),
    ),

    # ── Jacob Jordaens ────────────────────────────────────────────────────────
    "jordaens": ArtStyle(
        artist="Jacob Jordaens",
        movement="Antwerp Baroque / Flemish Naturalism",
        nationality="Flemish",
        period="c. 1615–1678",
        palette=[
            (0.88, 0.74, 0.55),   # warm ivory-cream highlight flesh — Antwerp daylight quality
            (0.78, 0.58, 0.36),   # warm sienna mid-tone flesh — earthy, ruddy vitality
            (0.54, 0.36, 0.18),   # warm umber-brown shadow flesh — never cold, always grounded
            (0.68, 0.42, 0.22),   # deep ruddy shadow — warm chestnut, Jordaens' characteristic shadow colour
            (0.82, 0.68, 0.28),   # warm golden ochre — sunlit fabric and drapery highlight
            (0.58, 0.26, 0.16),   # deep red-brown — saturated shadow in warm fabric zones
            (0.44, 0.38, 0.28),   # warm olive-grey background — earthy neutral ground
        ],
        ground_color=(0.48, 0.36, 0.20),    # warm sienna-ochre imprimatura — Antwerp Baroque ground
        stroke_size=9,
        wet_blend=0.38,                      # moderate-low — alla prima vitality; not Rubens' fluid alla prima but vigorous impasto
        edge_softness=0.38,                  # moderate-crisp — naturalist found edges, more physical than Leonardo
        jitter=0.035,                        # moderate — earthy spontaneity, not impressionistic scatter
        glazing=(0.62, 0.48, 0.22),          # warm amber-ochre final glaze — unifying Antwerp warmth
        crackle=True,                        # oil on canvas — 17th-century aging appropriate
        chromatic_split=False,               # pure naturalism; no optical colour-splitting
        technique=(
            "Earthy vitality — the defining quality of Jacob Jordaens' Antwerp Baroque.  "
            "Where his contemporary Rubens was cosmopolitan, drawing on Italian grand manner "
            "and courtly elegance, Jordaens was resolutely Antwerp: earthy, robust, grounded "
            "in the Flemish artisan tradition.  He never left Antwerp for Italy, and his art "
            "reflects this: warmer, more ruddy, more physically present than Rubens' celestial "
            "grandeur, with a vitality that feels genuinely observed rather than idealised.  "
            "His flesh tones are characteristically warm and sienna-based — a ruddy, earthy quality "
            "that reflects real Flemish skin under warm indoor light, without the polish of court "
            "portraiture or the theatrical pallor of tenebrism.  His highlights are warm cream-ivory, "
            "built up in thick impasto on the lit sides of faces and drapery — physically present "
            "rather than glazed.  His shadows retain warmth even in the deepest passages: a warm "
            "umber-chestnut that prevents figures from sinking into cold void.  "
            "He was trained by Adam van Noort (also Rubens' teacher), absorbed the Flemish "
            "workshop tradition of warm imprimatura grounds, and built his technique on loaded-brush "
            "work with wet-into-wet blending — but his hand is heavier and more earthy than Rubens', "
            "and his figures are more physically grounded.  After Rubens' death in 1640 he became the "
            "leading master of Antwerp, executing large commissions and decorative schemes that "
            "demonstrate his command of scale without losing his characteristic earthy intimacy.  "
            "His palette is dominated by warm amber-ochre, sienna, and raw umber — the palette "
            "of the Flemish artisan tradition — with brilliant highlights of warm cream-ivory "
            "built in thick impasto on lit surfaces."
        ),
        famous_works=[
            ("The King Drinks (Le Roi Boit)", "c. 1638"),
            ("Satyr and Peasant", "c. 1620"),
            ("The Allegory of Fertility", "c. 1617–1618"),
            ("As the Old Sing, So the Young Pipe", "1638"),
            ("The Triumph of Prince Frederick Henry", "1652"),
            ("Portrait of a Young Married Couple", "c. 1620–1625"),
            ("The Holy Family with Saint Anne", "c. 1616"),
        ],
        inspiration=(
            "Apply jordaens_earthy_vitality_pass() as the defining stylistic pass.  "
            "Three stages encoding Jordaens' warm Antwerp naturalism: "
            "(1) Warm cream highlight lift — in the upper highlight zone (lum > hi_lo ≈ 0.72), "
            "apply a warm cream lift: R + cream_r (modest), G + cream_g_small.  This is "
            "Jordaens' impasto peak-light quality — warm cream-ivory, not cool silver — "
            "built up in loaded-brush strokes on forehead, nose bridge, cheekbone, and chin.  "
            "(2) Earthy sienna midtone warmth — in the mid-tone band [mid_lo, mid_hi], apply "
            "a warm earthy boost: R + ruddy_r, G + ruddy_g, B - ruddy_b_damp.  This encodes "
            "Jordaens' characteristic flesh quality — ruddy, warm, sienna-based — the quality "
            "of real Flemish skin under warm indoor-ambient light.  "
            "(3) Shadow amber retention — in shadow zones (lum < shadow_hi ≈ 0.38), add "
            "warm amber-ochre: R + ochre_r, G + ochre_g_small.  Jordaens' shadows never go "
            "cold or grey; they retain a warm chestnut-amber quality that keeps figures "
            "physically grounded and alive.  "
            "Use opacity ≈ 0.30–0.40."
        ),
    ),

    # ── Guido Cagnacci ────────────────────────────────────────────────────────
    "guido_cagnacci": ArtStyle(
        artist="Guido Cagnacci",
        movement="Emilian Baroque / Caravaggesque Idealism",
        nationality="Italian",
        period="c. 1620–1663",
        palette=[
            (0.92, 0.78, 0.68),   # rose-ivory highlight flesh — pinkish warmth at peak light
            (0.80, 0.58, 0.48),   # warm peach mid-tone flesh — the defining Cagnacci rose
            (0.52, 0.32, 0.24),   # warm umber-rose shadow — never cold, retains warmth
            (0.70, 0.44, 0.36),   # deep rose-amber penumbra — luminous shadow transition
            (0.38, 0.32, 0.48),   # cool violet-grey deep shadow (rare, sparingly used)
            (0.62, 0.56, 0.44),   # warm buff background — soft Emilian ground tone
        ],
        ground_color=(0.58, 0.46, 0.32),    # warm sienna-ochre ground — Bolognese warm imprimatura
        stroke_size=5,
        wet_blend=0.78,                      # smooth, glazed quality — no impasto scatter
        edge_softness=0.72,                  # softly diffused — forms melt but don't dissolve
        jitter=0.014,                        # low — controlled, dreamy quality
        glazing=(0.72, 0.52, 0.38),          # rose-amber unifying glaze — his warm luminosity
        crackle=True,
        chromatic_split=False,
        technique=(
            "Rose flesh — the defining quality of Guido Cagnacci's Emilian Baroque.  "
            "Born in Santarcangelo di Romagna in 1601, Cagnacci trained in Bologna "
            "within the orbit of Guido Reni — absorbing Reni's idealizing grace and "
            "perfectly smooth sfumato technique — before moving to Rome, Venice, and "
            "finally Vienna, where he died in 1663 as court painter to Emperor Leopold I.  "
            "What distinguishes Cagnacci from every other Baroque master is his "
            "treatment of female flesh: a warm, pinkish, dreamlike luminescence that "
            "goes beyond mere naturalism into something almost ethereal.  Where Reni's "
            "flesh is cool ivory-pearl and Guercino's is amber-warm, Cagnacci's is "
            "rose — a specific warm-pink quality in the mid-tone zone that reads like "
            "candlelight seen through thin skin.  "
            "Technical analysis suggests this arose from his layering practice: warm "
            "sienna imprimatura, cool dead-colouring, then multiple thin rose-pink "
            "glazes over the mid-tones before the final cool ivory highlights.  "
            "The result is flesh that seems to glow from within — translucent, "
            "saturated, and slightly idealized, carrying Reni's grace without "
            "his coldness.  "
            "His mature works — The Death of Cleopatra (three known versions), "
            "Repentant Magdalene, Martha Rebuking Mary for Her Vanity — share this "
            "quality: women in states of emotion or repose whose skin carries an "
            "almost impossible luminosity, warm and pink and soft, as if they are "
            "lit not by a candle but by an inner light."
        ),
        famous_works=[
            ("The Death of Cleopatra",                   "c. 1658–1659"),
            ("Repentant Magdalene",                       "c. 1660"),
            ("Martha Rebuking Mary for Her Vanity",       "c. 1660"),
            ("Cleopatra before Augustus",                 "c. 1655–1660"),
            ("Lucretia",                                  "c. 1645"),
        ],
        inspiration=(
            "Apply cagnacci_rose_flesh_pass() as the defining stylistic pass.  "
            "Three stages encoding Cagnacci's rose flesh signature: "
            "(1) Rose highlight warmth — in the upper highlight zone (lum > hi_lo ≈ 0.70), "
            "apply a gentle pinkish warmth: R + rose_r_lift (modest), B - rose_b_damp (tiny), "
            "giving the characteristic Cagnacci pinkish-ivory quality at peak flesh lights — "
            "warmer than Boltraffio's pearl, warmer still than Orazio's silver, yet not "
            "the warm gold of Rembrandt; a specific rose quality.  "
            "(2) Peach mid-tone glow — in the mid-tone band [mid_lo, mid_hi], apply a "
            "gentle rose-amber shift (R + peach_r, G + peach_g small, B - peach_b tiny) "
            "via a raised-cosine window.  This is the primary Cagnacci effect: the "
            "pinkish peach warmth in the mid-tone flesh zone that no other Baroque "
            "master achieves in quite this way.  "
            "(3) Warm shadow recovery — in shadow zones (lum < shadow_hi), apply a "
            "rose-amber recovery (R + warm_r, G + warm_g smaller) to prevent the "
            "accumulated cool corrections (Orazio, Sassoferrato) from rendering the "
            "shadows too cold.  Cagnacci's shadows stay warm — rose-amber rather than "
            "grey-cool.  "
            "Use opacity ≈ 0.28–0.36."
        ),
    ),

    "furini": ArtStyle(
        artist="Francesco Furini",
        movement="Florentine Melancholic Baroque / Naturalist Sfumato",
        nationality="Italian",
        period="c. 1625–1646",
        palette=[
            (0.95, 0.88, 0.76),   # evanescent ivory highlight flesh
            (0.82, 0.68, 0.54),   # warm buff mid-tone flesh
            (0.52, 0.42, 0.36),   # deep warm umber-brown shadow flesh
            (0.60, 0.58, 0.62),   # lavender-grey penumbra transition (his signature)
            (0.18, 0.14, 0.12),   # near-black warm void background ground
            (0.72, 0.62, 0.48),   # warm amber mid-shadow recovery
        ],
        ground_color=(0.22, 0.18, 0.14),    # very dark warm-brown void ground — figures emerge from darkness
        stroke_size=4,
        wet_blend=0.82,                      # the highest blending of any Baroque period; near-Leonardo continuity
        edge_softness=0.88,                  # extreme sfumato — forms dissolve at periphery without edge
        jitter=0.010,                        # very low — seamless, controlled, no visible mark variation
        glazing=(0.68, 0.52, 0.34),          # warm amber-ochre unifying glaze — holds the figure in warm space
        crackle=True,
        chromatic_split=False,
        technique=(
            "Evanescent sfumato — the defining quality of Francesco Furini's Florentine Baroque.  "
            "Born in Florence in 1603, Furini trained under Matteo Rosselli before spending "
            "the formative years of his career in Rome (c. 1619–1622), where he absorbed "
            "both the Caravaggist tradition of tenebrism and the continuing influence of "
            "Correggio's Parma sfumato.  He returned to Florence and remained there until "
            "his early death in 1646 — ordained a priest in 1633, yet continuing to paint "
            "mythological and biblical subjects of extraordinary sensuality throughout his "
            "priestly career.  "
            "What makes Furini unique among his Florentine contemporaries is his synthesis "
            "of deep Caravaggist darkness with soft Correggesque sfumato.  His technique "
            "was described by contemporary sources as 'di marmo' (like marble) — yet warm "
            "and alive.  The comparison to marble points to the key quality: an almost "
            "impossible surface continuity, as if the skin were not painted but grown, "
            "with no visible brushstroke, no transition, no edge anywhere on the face "
            "or torso.  "
            "His most distinctive technical signature is a cool lavender-grey quality "
            "at the penumbra — the transition zone between the illuminated flesh and "
            "the surrounding deep brown shadow.  Where Correggio uses warm amber at "
            "his penumbra edges and Guido Reni uses cool ivory, Furini uses a subtle "
            "grey-lavender that reads as Florentine ambient reflected light: the colour "
            "of a grey Renaissance sky seen through a high studio window, bouncing into "
            "the shadow-adjacent flesh.  This quality is almost invisible on casual "
            "inspection but is the source of the characteristic 'Furini ring' — a subtle "
            "tonal coolness that encircles illuminated forms at their shadow boundary, "
            "sharpening the sense of three-dimensionality without introducing any hard edge.  "
            "His palette is essentially bimodal: warm ivory flesh and near-black void, "
            "with very little chromatic activity between.  The rich Venetian and Emilian "
            "middle zone of warm amber and ochre is largely absent from his work.  Instead, "
            "the transition from light to dark is handled almost entirely by value, with "
            "the lavender penumbra serving as the only chromatic event in the transition."
        ),
        famous_works=[
            ("Hylas and the Nymphs",                         "c. 1630–1635"),
            ("Judith with the Head of Holofernes",            "c. 1630–1635"),
            ("Lot and his Daughters",                         "c. 1634"),
            ("Saint Agnes",                                   "c. 1630"),
            ("Venus and Adonis",                              "c. 1638–1640"),
            ("Adam and Eve",                                  "c. 1626"),
        ],
        inspiration=(
            "Apply furini_melancholic_sfumato_pass() as the defining stylistic pass.  "
            "Four stages encoding Furini's melancholic sfumato signature: "
            "(1) Ivory highlight bloom — in the upper highlight zone (lum > hi_lo ≈ 0.68), "
            "apply a gently warm ivory lift with heavy Gaussian blur (blur_radius * 1.8) "
            "to ensure the effect has no boundary — the highlight bleeds outward as "
            "a luminous bloom, replicating the evanescent quality of Furini's peak lights.  "
            "Warmer than Boltraffio's pearl (which is cool), warmer than Moroni's silver, "
            "but less warm than Rembrandt's gold — a specific warm ivory with no hard edge.  "
            "(2) Lavender penumbra — in the transition band [penumbra_lo, penumbra_hi] ≈ "
            "[0.28, 0.60], apply a cool lavender shift via raised-cosine window: "
            "B + lavender_b, R - lavender_r.  This encodes the 'Furini ring' — the cool "
            "grey-lavender quality at shadow edges that is his most distinctive signature.  "
            "The raised-cosine window ensures it peaks at the centre of the transition zone "
            "and fades smoothly toward both the light and dark extremes.  "
            "(3) Deep shadow cool — in the deepest shadow zone (lum < shadow_hi ≈ 0.26), "
            "a subtle atmospheric cool (B + shadow_b, R - shadow_r) that prevents the "
            "accumulated warm passes (Strozzi, Jordaens, Cagnacci) from making the void "
            "background too amber.  Furini's void is warm brown, not amber — there is a "
            "difference, and this adjustment maintains it.  "
            "(4) Ultra-smooth mid-tone surface — Gaussian blur at smooth_sigma ≈ 2.2 "
            "blended into the mid-tone zone [smooth_lo, smooth_hi] at smooth_str ≈ 0.45, "
            "creating artificial surface continuity that mimics his extreme glazing patience.  "
            "Use opacity ≈ 0.28–0.34."
        ),
    ),

    "lavinia_fontana": ArtStyle(
        artist="Lavinia Fontana",
        movement="Bolognese Mannerism / Post-Tridentine Portrait Realism",
        nationality="Italian",
        period="c. 1575–1614",
        palette=[
            (0.88, 0.74, 0.62),   # warm rose-ivory highlight flesh (Bolognese warmth)
            (0.74, 0.56, 0.44),   # warm peach mid-tone flesh
            (0.50, 0.32, 0.24),   # warm sienna shadow flesh
            (0.62, 0.16, 0.16),   # deep crimson costume (signature velvet richness)
            (0.14, 0.10, 0.08),   # near-black velvet costume shadow
            (0.78, 0.66, 0.26),   # warm gold jewellery and trim
            (0.54, 0.46, 0.36),   # warm buff architectural background
        ],
        ground_color=(0.46, 0.38, 0.28),    # warm ochre Bolognese ground
        stroke_size=5,
        wet_blend=0.62,                      # moderate-high — glazed finish, not full sfumato
        edge_softness=0.58,                  # moderate-soft — refined Bolognese edges
        jitter=0.016,                        # low: controlled portrait precision
        glazing=(0.68, 0.54, 0.38),          # warm amber-rose unifying glaze
        crackle=True,                        # oil on canvas — appropriate for period
        chromatic_split=False,               # pure tonal portraiture, no colour splitting
        technique=(
            "Lavinia Fontana (1552–1614) was the first woman in Western history to "
            "establish herself as a fully professional artist — not a court ornament or "
            "noble amateur, but a working painter who supported her household through "
            "commissions, employed her husband as studio assistant, and eventually "
            "received a papal invitation to Rome from Clement VIII.  Daughter of the "
            "Bolognese painter Prospero Fontana, she trained in one of the most "
            "technically rigorous workshops in northern Italy — the same Bolognese "
            "environment that would, within a generation, produce the Carracci academy "
            "and its reform of European painting.  "
            "Her technical inheritance is unmistakably Bolognese: a warm, amber-toned "
            "ground, smooth flesh modeling built up through careful glazed layers, and "
            "an approach to luminosity that owes more to Correggio's atmospheric warmth "
            "than to the cool silver precision of the Lombard portrait tradition.  "
            "Where Moroni observes his sitters under flat north light and records them "
            "with tonal accuracy, Fontana idealises slightly — lifting the flesh toward "
            "a rose-ivory warmth that flatters without falsifying.  "
            "Her defining technical signature, however, is the rendering of costume and "
            "jewellery.  No other Italian painter of the late sixteenth century matched "
            "her command of deep crimson velvet — the fabric of choice for Bolognese "
            "nobility — rendered with such material convincingness.  The darkness of the "
            "velvet is not the near-black void of a Caravaggio or the flat black of a "
            "Bronzino; it is a warm, rich darkness with crimson depth visible in the "
            "folds and highlights, a quality achieved through multiple translucent "
            "glazes of vermilion and lake over a warm umber underlayer.  Against this "
            "costume depth, gold jewellery — pearl necklaces, gold chains, gem-set "
            "brooches — reads with extraordinary vivacity because the warm gold is "
            "simultaneously a highlight against the dark velvet and a colour accent "
            "that ties the figure's costume palette together.  "
            "Her flesh handling in the face and hands is smooth and controlled — "
            "no visible brushwork, edges softened but not dissolved into sfumato.  "
            "The Bolognese glazing tradition gives her flesh a layered, luminous quality "
            "different from either the crisp enamel of Bronzino or the atmospheric "
            "dissolution of Leonardo: the forms are solid and present, but the surface "
            "is warm and softly translucent, as if lit from within rather than from "
            "above.  Her shadow handling retains the warm amber retention of the "
            "Bolognese tradition — never the cold grey of the north or the near-black "
            "void of the tenebristi.  Even in the deepest costume shadows, there is "
            "recoverable warmth."
        ),
        famous_works=[
            ("Self-Portrait at the Clavichord",          "1577"),
            ("Noli me tangere",                          "1581"),
            ("Portrait of the Gozzadini Family",         "c. 1584"),
            ("Portrait of a Noblewoman",                 "c. 1580"),
            ("Minerva Dressing",                         "1613"),
            ("Portrait of Costanza Alidosi",             "c. 1594"),
            ("Holy Family with Saints",                  "c. 1578"),
        ],
        inspiration=(
            "Apply fontana_jewel_costume_pass() as the defining stylistic pass.  "
            "Three stages encoding Fontana's Bolognese portrait signature: "
            "(1) Highlight warm brilliance — in the upper highlight zone (lum > hi_lo ≈ 0.70), "
            "apply a gentle warm ivory lift: R + ivory_r (≈0.012), G + ivory_g (≈0.007), "
            "B + ivory_b (≈0.002).  The Gaussian-blurred mask ensures the highlight "
            "blooms outward without a hard edge — Bolognese luminosity is warm and "
            "present, not cool silver (Moroni) or pearled (Boltraffio).  "
            "(2) Costume crimson depth — in the dark costume zone [costume_lo, costume_hi] "
            "≈ [0.18, 0.46], apply a raised-cosine warm crimson enrichment: "
            "R + crimson_r (≈0.020), G + crimson_g (≈0.003, tiny), B - crimson_b (≈0.007, "
            "reduces blue to avoid purple shift).  This replicates Fontana's signature "
            "deep crimson velvet quality — the warm, saturated darkness that gives her "
            "costume zones their material richness and depth, contrasting with the cold "
            "dark of a Bronzino or the void dark of a Caravaggio.  "
            "(3) Shadow amber warmth — in the deepest shadow zone (lum < shadow_hi ≈ 0.22), "
            "add warm amber retention: R + amber_r (≈0.014), G + amber_g (≈0.006).  "
            "Bolognese painters never let their shadows go cold or grey; even in the "
            "near-black void of the background, there is recoverable warm amber — the "
            "quality that makes Bolognese portraits feel inhabited and warm rather than "
            "theatrically dramatic.  "
            "Use opacity ≈ 0.26–0.34."
        ),
    ),

    "moroni": ArtStyle(
        artist="Giovanni Battista Moroni",
        movement="Bergamasque Portrait Realism / Lombard Renaissance",
        nationality="Italian",
        period="c. 1545–1579",
        palette=[
            (0.82, 0.72, 0.58),   # warm ivory-buff highlight flesh
            (0.65, 0.52, 0.38),   # warm sienna mid-tone flesh
            (0.42, 0.32, 0.22),   # warm umber shadow flesh
            (0.55, 0.58, 0.52),   # cool grey-green background stone
            (0.22, 0.20, 0.18),   # near-black costume (velvets, dark wool)
            (0.72, 0.68, 0.60),   # pale silver highlight (textiles and flesh peak)
            (0.48, 0.42, 0.32),   # mid warm-brown — shadow recovery anchor
        ],
        ground_color=(0.52, 0.48, 0.40),    # warm grey-buff ground — Bergamasque panel tone
        stroke_size=6,
        wet_blend=0.45,                      # moderate — smooth but not sfumato-dissolved
        edge_softness=0.40,                  # moderate-crisp — naturalist found edges
        jitter=0.020,                        # low: Moroni's precision, not impressionistic scatter
        glazing=(0.72, 0.68, 0.52),          # warm silver-buff final unifying glaze
        crackle=True,                        # oil on canvas — 16th-century aging appropriate
        chromatic_split=False,               # pure tonal naturalism, no colour splitting
        technique=(
            "Silver presence — Moroni's defining quality.  Unlike Leonardo's sfumato "
            "(which dematerialises form into atmospheric haze) or Bronzino's enamel "
            "(which crystallises form into cold perfection), Moroni achieves physical "
            "presence through tonal accuracy: the correct luminance value at every "
            "point of the face, as observed under real north-window light.  His "
            "highlights are cool silver-grey — not warm ivory — catching the flat "
            "Bergamasque daylight without the warm amber glaze of the Venetians.  "
            "His shadows are warm amber-ochre rather than cool grey or near-black "
            "void: they recover warmth in the darkest passages, keeping the face "
            "readable and grounded.  "
            "The mid-tone zone — where most of his sitters' faces live — is handled "
            "with extraordinary precision: gentle local contrast that makes forms "
            "emerge from one another without sfumato dissolution or theatrical drama.  "
            "The result is a sense of the sitter existing in real space and real light, "
            "observed without flattery or idealization.  "
            "Moroni's technique was likely influenced by Moretto da Brescia's "
            "naturalism and Savoldo's tonal approach — the Lombard tradition of "
            "careful, unhurried observation that predates and parallels (but does not "
            "descend from) Caravaggio's later naturalist revolution."
        ),
        famous_works=[
            ("Il Sarto (The Tailor)",              "c. 1570"),
            ("Portrait of a Gentleman (Il Cavaliere)",  "c. 1554"),
            ("Portrait of an Old Man with a Book",  "c. 1575"),
            ("Portrait of Gian Gerolamo Grumelli ('The Knight in Pink')", "1560"),
            ("The Poet Torquato Tasso",             "c. 1560"),
            ("Portrait of Count Pietro Secco Suardo", "1563"),
            ("Portrait of a Lady in White",         "c. 1556"),
        ],
        inspiration=(
            "Apply moroni_silver_presence_pass() as the defining stylistic pass.  "
            "Three stages that encode Moroni's tonal signature: "
            "(1) Cool silver highlight — in the upper highlight zone (lum > hi_lo ≈ 0.68), "
            "shift subtly toward cool silver: R - silver_r (tiny), "
            "G + silver_g (small), B + silver_b (moderate).  This replicates the "
            "cool north-window quality of Moroni's lit flesh — silver rather than ivory.  "
            "(2) Warm shadow recovery — in the shadow zone (lum < shadow_hi ≈ 0.35), "
            "add warm amber-ochre recovery: R + warm_r, G + warm_g (smaller), "
            "B - warm_b (tiny reduction).  Moroni's shadows never go cold or grey; "
            "they retain earthy warmth even in the deepest tones.  "
            "(3) Mid-tone presence enhancement — in the mid-tone zone [0.35, 0.68], "
            "apply a very mild luminance contrast boost (gamma_mid ≈ 0.92–0.96 in "
            "the lower half, 1.04–1.08 in the upper half) that slightly separates "
            "the mid-tone planes without visible sharpening artifacts.  This captures "
            "Moroni's characteristic tonal precision — the quality that makes his "
            "sitters seem physically present rather than painted.  "
            "Use opacity ≈ 0.32–0.42."
        ),
    ),

    "andrea_solario": ArtStyle(
        artist="Andrea Solario",
        movement="Lombard Leonardesque / Venetian-Influenced Milanese Renaissance",
        nationality="Italian",
        period="c. 1490–1524",
        palette=[
            (0.90, 0.78, 0.58),   # pellucid amber-honey highlight flesh (Lombard warmth)
            (0.76, 0.60, 0.42),   # warm amber mid-tone flesh
            (0.50, 0.36, 0.24),   # warm sienna shadow flesh
            (0.24, 0.22, 0.36),   # cool blue-violet deep shadow (Venetian influence)
            (0.16, 0.14, 0.12),   # near-black background void
            (0.72, 0.64, 0.42),   # warm honey-gold ambient (amber glaze quality)
            (0.44, 0.52, 0.48),   # cool blue-grey atmospheric recession (landscape)
        ],
        ground_color=(0.44, 0.36, 0.24),    # warm amber-ochre Lombard ground
        stroke_size=4,
        wet_blend=0.78,                      # high — very smooth, Leonardesque sfumato quality
        edge_softness=0.82,                  # near-sfumato — edges dissolve with Lombard warmth
        jitter=0.012,                        # very low: pellucid surface, no scatter
        glazing=(0.64, 0.52, 0.30),          # warm amber glazing — honey depth in accumulated layers
        crackle=True,                        # oil on panel — early 16th-century aging
        chromatic_split=False,               # tonal luminosity, not chromatic scattering
        technique=(
            "Andrea Solario (c. 1460–1524) is among the most refined and least "
            "celebrated painters of the Lombard Renaissance — a figure who absorbed "
            "Leonardo's sfumato technique with a depth perhaps exceeding any other "
            "painter in Leonardo's orbit save Bernardino Luini, and who combined "
            "this Leonardesque inheritance with a Venetian chromatic sensibility "
            "acquired during his probable visit to Venice in the early 1490s.  The "
            "result is a style of singular luminous quality: the sfumato is present, "
            "but it is warmer than Leonardo's — suffused with an amber-honey tone "
            "that gives his flesh the quality of light filtered through a thin amber "
            "panel rather than the cooler, more silvery atmospheric haze of the "
            "master himself.  "
            "His key technical signature is what might be called pellucid warmth — "
            "a quality of flesh that appears lit from within by warm amber light, "
            "as if the skin were itself slightly translucent.  This is not the "
            "cool pearl luminosity of Boltraffio (who was also in Leonardo's "
            "orbit), nor is it the ivory warmth of Furini's later Baroque sfumato.  "
            "It is specifically amber — a honey-gold quality in the upper highlight "
            "zone that suggests a physical depth to the paint surface: layers of "
            "thin amber-tinted glaze built up over a warm ground, each layer "
            "adding a fractional degree of warmth and depth.  "
            "The Venetian influence manifests most clearly in his shadow treatment.  "
            "Unlike the warm amber shadows of the Bolognese tradition or the warm "
            "umber darkness of the Lombard panel tradition, Solario's deepest shadows "
            "carry a slight cool blue-violet undertone — the characteristic Venetian "
            "shadow quality that one sees in Giorgione and early Titian, where the "
            "cool atmosphere of the lagoon seems to enter even the interior light of "
            "a portrait.  This chromatic arc — from warm amber highlights through "
            "neutral mid-tones to cool violet shadows — creates a subtle, continuously "
            "varying colour temperature across the face that gives his portraits an "
            "unusual sense of spatial depth and atmospheric presence.  "
            "His famous Madonna paintings (especially the Madonna with Green Cushion "
            "in the Louvre) demonstrate the full synthesis: sfumato-softened edges, "
            "amber-glowing flesh, cool-shadowed drapery, and a landscape background "
            "of Leonardesque geological fantasy that dissolves into pale blue-grey "
            "atmospheric haze in a manner almost indistinguishable from Leonardo's own.  "
            "His portrait of Cristoforo Longoni (c. 1505) is perhaps the closest any "
            "Lombard painter came to matching Leonardo's psychological presence "
            "in portraiture: the sitter exists in real atmospheric space, his skin "
            "warm and luminous, his eyes meeting the viewer with a calm directness "
            "that never tips into the theatrical."
        ),
        famous_works=[
            ("Madonna with Green Cushion",              "c. 1507–1510"),
            ("Salome with the Head of Saint John the Baptist", "c. 1507–1510"),
            ("Portrait of a Man (Cristoforo Longoni?)", "c. 1505"),
            ("Rest on the Flight into Egypt",           "c. 1515"),
            ("Head of Saint John the Baptist on a Platter", "c. 1507"),
            ("The Lamentation over the Dead Christ",    "c. 1505"),
            ("Madonna of the Veil",                     "c. 1508–1510"),
        ],
        inspiration=(
            "Apply solario_pellucid_amber_pass() as the defining stylistic pass.  "
            "Three stages encoding Solario's Lombard-Leonardesque signature: "
            "(1) Pellucid amber highlight — in the upper highlight zone (lum > hi_lo ≈ 0.62), "
            "apply a warm amber-honey lift: R + amber_r (≈0.018), G + amber_g (≈0.010), "
            "B - amber_b (≈0.004, reduces blue to avoid ivory drift).  The Gaussian-blurred "
            "mask ensures the amber warmth blooms outward without a hard edge — Solario's "
            "highlights are warm amber, not cool silver (Moroni), not pearl (Boltraffio), "
            "not ivory (Furini): specifically amber, as if light passes through warm honey glass.  "
            "(2) Cool violet shadow — in the deep shadow zone (lum < shadow_hi ≈ 0.32), "
            "apply a raised-cosine cool blue-violet undertone: B + violet_b (≈0.016), "
            "G + violet_g (≈0.004), R - violet_r (≈0.005, tiny desaturation).  This is "
            "Solario's Venetian inheritance: even in Lombard interiors, his shadows carry "
            "a slight atmospheric coolness — the blue-violet quality of Venetian shadow "
            "that never appears in purely Florentine or Bolognese painters.  "
            "(3) Chromatic arc mid-tone warmth — in the penumbra zone [arc_lo, arc_hi] "
            "≈ [0.32, 0.62], apply a sin-window warmth pulse: R + arc_r * sin_window, "
            "G + arc_g * sin_window (smaller).  This encodes the continuously-varying "
            "colour temperature across Solario's flesh — the transition from cool shadows "
            "through warm amber mid-tones and back to amber highlights creates a "
            "chromatic arc that gives the portrait its unusual depth and atmospheric "
            "presence.  The sin-window ensures the warmth peaks in the penumbra centre "
            "and fades toward both shadow and highlight.  "
            "Use opacity ≈ 0.28–0.36."
        ),
    ),

    "perugino": ArtStyle(
        artist="Pietro Perugino",
        movement="Umbrian Renaissance / Proto-Classical",
        nationality="Italian",
        period="c. 1472–1523",
        palette=[
            (0.94, 0.82, 0.64),   # luminous warm ivory highlight flesh (Umbrian light)
            (0.78, 0.62, 0.45),   # warm peach mid-tone flesh
            (0.54, 0.38, 0.26),   # warm amber-sienna shadow flesh
            (0.60, 0.70, 0.80),   # Umbrian sky blue (serene atmospheric distance)
            (0.38, 0.50, 0.35),   # soft sage-green landscape (harmonious, quiet)
            (0.82, 0.75, 0.58),   # warm golden ambient — Umbrian plain light
            (0.30, 0.24, 0.16),   # deep warm shadow — anchor (not cold)
        ],
        ground_color=(0.82, 0.72, 0.54),    # warm luminous buff-ivory ground (lum≈0.73) — Umbrian light ground
        stroke_size=5,
        wet_blend=0.42,                      # moderate — careful glazed layering, not deep sfumato blending
        edge_softness=0.65,                  # moderate-high — softened, serene, not sfumato extremes
        jitter=0.014,
        glazing=(0.70, 0.60, 0.38),          # warm amber-golden glaze — Umbrian luminosity
        crackle=True,                        # oil on panel — aging appropriate
        chromatic_split=False,               # pure tonal harmony, not chromatic scattering
        technique=(
            "Pietro Perugino (c. 1446–1523) stands as one of the most significant "
            "and underestimated painters of the Italian Renaissance — underestimated "
            "because his supreme pupil Raphael so completely surpassed and absorbed "
            "him that Perugino's own achievement has been obscured by the very school "
            "he founded.  Yet the Umbrian school that Perugino created and embodied "
            "is one of the most distinctive in Italian art: a tradition of serene, "
            "harmonious composition, soft atmospheric light, and an almost "
            "otherworldly quality of inner calm that no other regional tradition "
            "quite matches.  "
            "His defining technical quality might be called luminous ground warmth — "
            "a way of handling light that does not produce the theatrical drama of "
            "Caravaggio's chiaroscuro, nor the intellectual exactitude of Leonardo's "
            "sfumato, nor the warm vitality of the Venetian colorists, but something "
            "distinct: a diffuse, pervasive warmth that seems to emanate from the "
            "ground itself, as if the warm ochre imprimatura is glowing softly "
            "through every layer of paint.  The shadows in Perugino's paintings are "
            "never cold or theatrical; they are warm amber-shadow, retaining the "
            "gentle heat of the Umbrian plain even in the darkest passages.  The "
            "highlights are not brilliant white flashes but creamy ivory-gold, warm "
            "and unassuming — the light of an Umbrian afternoon rather than a "
            "Venetian lagoon or a Flemish studio window.  "
            "Perugino's landscapes are among the most characteristic elements of "
            "his style: open, luminous, with gently rolling hills dissolving into "
            "a soft blue-green atmospheric haze on the horizon.  This atmospheric "
            "treatment — a precursor to the High Renaissance's full deployment of "
            "aerial perspective — creates a sense of endless, peaceful recession "
            "that amplifies the psychological serenity of his figures.  "
            "His human figures embody this same quality: they are calm, composed, "
            "slightly idealised without being cold or classical in the Florentine "
            "sense.  His Madonna faces, in particular, have a quality of gentle "
            "rapture — eyes slightly downcast, mouths softly curved — that his "
            "pupil Raphael would refine into one of the most recognizable ideals "
            "of feminine beauty in Western art.  "
            "Perugino's key technical contribution to the subsequent tradition: "
            "the demonstration that a unified warm ground, allowing the imprimatura "
            "to glow through thin glazes, could create a quality of luminosity "
            "more harmonious and psychologically gentle than either the cool "
            "sfumato of Leonardo or the warm impasto of the Venetians.  This "
            "approach — which might be called glazed ground luminosity — would "
            "directly influence Raphael's handling of his early Umbrian-period "
            "paintings before Raphael moved toward the more saturated palette of "
            "the Roman school."
        ),
        famous_works=[
            ("The Delivery of the Keys",            "1481–1482"),
            ("Christ Giving the Keys to Saint Peter", "c. 1481"),
            ("Virgin and Child with Saints",         "c. 1493"),
            ("The Crucifixion with Saints",          "c. 1496"),
            ("Lamentation over the Dead Christ",     "c. 1495"),
            ("Apollo and Marsyas",                   "c. 1495"),
            ("Portrait of Francesco delle Opere",    "1494"),
            ("Assumption of the Virgin (Vallombrosa)", "1500"),
        ],
        inspiration=(
            "Apply perugino_serene_grace_pass() as the defining stylistic pass.  "
            "Three stages encoding Perugino's Umbrian-Renaissance signature: "
            "(1) Luminous ground warmth — a warm ambient lift applied throughout the "
            "mid-tone zone [ground_lo, ground_hi] ≈ [0.30, 0.75] via a smooth bell-window "
            "(sin²(π * t) where t = normalised position in the range).  "
            "R + ground_r (≈0.014), G + ground_g (≈0.007).  This encodes the defining "
            "Umbrian quality: the warm ochre imprimatura glowing through thin paint "
            "layers, suffusing every passage with a gentle inner warmth.  Unlike "
            "Guercino's penumbra_warmth (concentrated in the penumbra zone) or "
            "Jordaens's ruddy mid-tone (raw vitality), Perugino's warmth is "
            "diffuse and harmonious — it is the warmth of the ground itself rather "
            "than a local flesh-colour effect.  The sin² window (rather than a simple "
            "sin window) produces a peak that is broader and more gradual than a "
            "sine peak — more like a warm ambient field than a targeted warmth pulse.  "
            "(2) Ivory highlight serenity — in the upper highlight zone (lum > hi_lo ≈ 0.70), "
            "apply a warm ivory-gold lift: R + ivory_r (≈0.010), G + ivory_g (≈0.006), "
            "B - ivory_b (≈0.003, minor blue reduction to avoid drift).  Perugino's "
            "highlights are creamy ivory-gold rather than cool pearl (Boltraffio), "
            "silver (Moroni), or amber-pellucid (Solario): they are warm, unassuming, "
            "and harmonious — the serene Umbrian quality.  "
            "(3) Warm amber shadow — in the shadow zone (lum < shadow_hi ≈ 0.35), "
            "apply a gentle raised-cosine warm amber recovery: R + warm_r (≈0.014), "
            "G + warm_g (≈0.006).  Perugino's shadows never go cold — unlike the "
            "violet Venetian shadows of Solario, his dark passages retain the warm "
            "amber-sienna quality of the Umbrian earth.  "
            "Use opacity ≈ 0.28–0.36."
        ),
    ),

    # ── Giovanni Gerolamo Savoldo ──────────────────────────────────────────────
    "savoldo": ArtStyle(
        artist="Giovanni Gerolamo Savoldo",
        movement="Brescian Renaissance / Venetian-Lombard School",
        nationality="Italian (Brescian)",
        period="c. 1480/85–1548",
        palette=[
            (0.82, 0.78, 0.72),   # warm silver-ivory highlight — moonlit peak flesh
            (0.62, 0.60, 0.65),   # cool silver-grey — phosphorescent penumbra shimmer
            (0.48, 0.44, 0.40),   # warm mid-tone — Brescian amber under-glow
            (0.28, 0.24, 0.20),   # deep warm umber shadow — never cold black
            (0.55, 0.58, 0.68),   # cool blue-grey atmosphere — nocturnal distance haze
            (0.70, 0.65, 0.52),   # warm ochre-ivory — Venetian-Lombard ground warmth
        ],
        ground_color=(0.52, 0.46, 0.34),    # warm amber-ochre Venetian imprimatura
        stroke_size=5,
        wet_blend=0.70,                      # high blending — nocturnal surface seamlessness
        edge_softness=0.78,                  # high softness — silver moonveil dissolves edges
        jitter=0.018,
        glazing=(0.58, 0.54, 0.48),          # warm amber-grey unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Silver moonveil — a phosphorescent cool-silver shimmer concentrated "
            "at the penumbra boundary (the transitional zone between illuminated "
            "surface and shadow).  Savoldo places his most luminous grey-silver "
            "exactly at the midpoint of the light-to-shadow transition, creating "
            "the illusion of moonlight scattering through drapery and atmosphere.  "
            "Highlights are warm silver-ivory (not cold blue); shadows retain warm "
            "amber depth (never dead black); only the penumbra transition itself "
            "carries the characteristic cool silver cast.  "
            "Unlike Leonardo's sfumato (which dissolves all edges equally through "
            "atmospheric smoke) or Boltraffio's pearl (a cool-blue highlight quality), "
            "Savoldo's silver is concentrated, atmospheric, and location-specific — "
            "it belongs to the boundary between light and dark, not to the light "
            "itself.  His nocturnal scenes (Saint Mary Magdalen, Adoration of the "
            "Shepherds) demonstrate this quality most fully: drapery lit by moonlight "
            "reads as luminous silver-grey at the fold crests while the shadows "
            "below retain warm amber earth tones, and the transition between the "
            "two carries a distinctive phosphorescent shimmer."
        ),
        famous_works=[
            ("Saint Mary Magdalen Approaching the Sepulchre", "c. 1535–1540"),
            ("Portrait of a Knight",                           "c. 1525"),
            ("Tobias and the Angel",                           "c. 1527–1530"),
            ("Adoration of the Shepherds (Brescia)",           "c. 1540"),
            ("Portrait of a Man in Armour",                    "c. 1522"),
            ("Saint Matthew and the Angel",                    "c. 1534"),
        ],
        inspiration=(
            "Apply savoldo_silver_veil_pass() as the defining stylistic pass.  "
            "Three stages encoding Savoldo's Brescian-nocturnal signature: "
            "(1) Silver moonveil at the penumbra boundary — a Gaussian-peaked "
            "weight centred at the midpoint of [penumbra_lo, penumbra_hi] (default "
            "[0.28, 0.62]).  The Gaussian window (σ ≈ 0.20 of the range) concentrates "
            "the silver shimmer exactly at the light-shadow boundary: R - silver_r "
            "(≈0.010), G unchanged, B + silver_b (≈0.022).  This Gaussian-peaked "
            "penumbra window is the session 118 artistic improvement: a more "
            "physically accurate model of scattered moonlight than the sin-windowed "
            "penumbra arc (session 116) or sin²-windowed ground warmth (session 117) "
            "— a Gaussian naturally models the bell-shaped distribution of scattered "
            "light at a surface tangent to the illumination direction.  "
            "(2) Warm ivory highlight — in the upper highlight zone (lum > hi_lo ≈ 0.70), "
            "apply a warm ivory lift (R + ivory_r ≈ 0.012, G + ivory_g ≈ 0.007).  "
            "Savoldo's highlights are warm silver-ivory, not cold blue — the warmth "
            "of reflected moonlight against warm Venetian-ground flesh, not arctic "
            "silver.  "
            "(3) Warm shadow retention — in the shadow zone (lum < shadow_hi ≈ 0.32), "
            "a gentle raised-cosine warm recovery (R + warm_r ≈ 0.012, G + warm_g ≈ 0.005) "
            "prevents cold black voids — Savoldo's nocturnal shadows retain Brescian "
            "warmth and depth even in their deepest passages.  "
            "Use opacity ≈ 0.26–0.34."
        ),
    ),

    # ── Pompeo Batoni ─────────────────────────────────────────────────────────
    "batoni": ArtStyle(
        artist="Pompeo Batoni",
        movement="Roman Classicism / Rococo-Classicism",
        nationality="Italian",
        period="1740–1787",
        palette=[
            (0.88, 0.74, 0.56),   # warm cream flesh — Batoni's celebrated carnations
            (0.72, 0.56, 0.38),   # mid-tone ochre shadow
            (0.48, 0.32, 0.18),   # deep umber shadow
            (0.82, 0.68, 0.78),   # cool rose highlight — characteristic pink warmth
            (0.42, 0.55, 0.72),   # Prussian blue drapery
            (0.72, 0.35, 0.28),   # vermilion red — Grand Tour sitter coats
            (0.88, 0.82, 0.60),   # warm ivory silk sheen highlight
            (0.55, 0.62, 0.44),   # Roman verdaccio shadow green
        ],
        ground_color=(0.60, 0.50, 0.34),    # warm Roman imprimatura
        stroke_size=6,
        wet_blend=0.55,
        edge_softness=0.65,
        jitter=0.025,
        glazing=(0.78, 0.65, 0.42),          # warm amber varnish
        crackle=True,
        chromatic_split=False,
        technique=(
            "Polished Roman Classicism with Rococo elegance.  Batoni's flesh tones "
            "are warm, smooth, and luminous — a Roman refinement of Venetian colorism.  "
            "His defining specialty: the rendering of silk and satin drapery via thin "
            "anisotropic highlight streaks along the weave direction, creating a "
            "directional shimmer unlike the isotropic highlights of his contemporaries.  "
            "Glazed with warm amber to unify the palette; figures set against classical "
            "Roman architecture or antique statuary backgrounds.  "
            "Grand Tour portraiture: aristocratic sitters of impeccable finish."
        ),
        famous_works=[
            ("Portrait of a Young Man (Grand Tour sitter)", "c. 1760"),
            ("Thomas William Coke, later 1st Earl of Leicester", "1774"),
            ("Portrait of Francis Basset", "1778"),
            ("John Staples", "1773"),
        ],
        inspiration=(
            "Apply batoni_silk_sheen_pass() as the defining stylistic pass.  "
            "Batoni's silk rendering: directional anisotropic specular streaks along "
            "a set angle (default 45°), Gaussian-profiled across their width.  "
            "The session 119 artistic improvement is the anisotropic_silk_streak() "
            "kernel — physically models the elongated highlight lobe of woven silk "
            "(where the warp and weft threads reflect specular light preferentially "
            "along the weave direction).  Warm ivory streaks (R + streak_r ≈ 0.032, "
            "G + streak_g ≈ 0.022) applied only where luminance exceeds silk_lo ≈ 0.48.  "
            "Streak width ~ 3–7 px, spacing ~ 8–14 px, angle ~ 40–50°.  "
            "Use opacity ≈ 0.22–0.30."
        ),
    ),


    # ── Lorenzo Lotto ──────────────────────────────────────────────────────────
    "lotto": ArtStyle(
        artist="Lorenzo Lotto",
        movement="Venetian Renaissance / Bergamask Eccentric School",
        nationality="Italian (Venetian, later Bergamask)",
        period="c. 1480–1556/57",
        palette=[
            (0.86, 0.72, 0.54),   # warm cream flesh — luminous Lotto portraits
            (0.58, 0.72, 0.42),   # vivid grass-green — eccentric costume accent
            (0.75, 0.48, 0.38),   # warm rose-salmon — chromatic vitality in flesh
            (0.32, 0.30, 0.42),   # cool blue-grey shadow — Lotto's cold dark accents
            (0.68, 0.52, 0.22),   # warm golden ochre — Venetian ground warmth
            (0.52, 0.32, 0.22),   # deep warm umber — shadow depth
        ],
        ground_color=(0.52, 0.44, 0.30),    # warm Venetian ochre imprimatura
        stroke_size=5,
        wet_blend=0.45,                      # moderate — visible chromatic energy, not Titian's full blend
        edge_softness=0.52,                  # moderate — psychological acuity; clearer than sfumato masters
        jitter=0.035,                        # higher — chromatic restlessness
        glazing=(0.72, 0.58, 0.32),          # warm golden glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Eccentric Venetian portraiture with psychological intensity and "
            "chromatic restlessness.  Lotto's portraits are distinguished by three "
            "qualities: vivid, unexpected color contrasts (grass-green against mauve, "
            "cool grey against warm ochre); diagonal compositional energy that creates "
            "a sense of psychological instability or mid-thought alertness; and a "
            "chromatic vitality in flesh tones that results from the optical mixture "
            "of multiple thin glazes over a textured Venetian ground.  Unlike Titian's "
            "smooth seamless warm flesh, Lotto's surfaces carry a slight hum of warm "
            "and cool color — visible when examined at close range — that contemporary "
            "viewers described as a 'living quality.'  His portrait sitters appear "
            "caught mid-thought: the Portrait of Andrea Odoni (1527) is an almost "
            "disquieting study of a collector surrounded by antique fragments, his "
            "gaze turned inward.  Lotto moved restlessly between Venice, Bergamo, "
            "the Marche, and Treviso, never settling into a single courtly idiom, "
            "which may account for the psychological edge and formal eccentricity "
            "that distinguishes him from his more celebrated Venetian contemporaries."
        ),
        famous_works=[
            ("Portrait of Andrea Odoni",              "1527"),
            ("Portrait of a Young Man",               "c. 1505"),
            ("Venus and Cupid",                       "c. 1520–1525"),
            ("Triumph of Chastity",                   "c. 1529–1530"),
            ("Saint Jerome in the Wilderness",        "c. 1506"),
            ("Portrait of Lucina Brembati",           "c. 1520"),
            ("Annunciation (Recanati)",                "1527"),
            ("Portrait of a Man with a Golden Paw",  "c. 1527"),
        ],
        inspiration=(
            "Apply lotto_restless_vivacity_pass() as the defining stylistic pass.  "
            "Three stages encoding Lotto's eccentric Venetian signature: "
            "(1) Warm vivacity lift in highlights — above hi_lo (≈ 0.68), apply a "
            "warm rose-ivory lift: R + vivacity_r (≈ 0.014), G + vivacity_g (≈ 0.008), "
            "B - vivacity_b (≈ 0.004).  Lotto's highlights are warm and slightly "
            "saturated — neither the cool pearl of Boltraffio nor the neutral ivory "
            "of Raphael, but a rose-warm quality reflecting his Venetian-ground warmth.  "
            "(2) Cool eccentric shadow accent — below shadow_hi (≈ 0.36), apply a "
            "slight blue-grey shift: B + shadow_cool_b (≈ 0.012), G - shadow_warm_g "
            "(≈ 0.004).  Lotto's darks often carry unexpected cool accents — a quality "
            "that distinguishes his psychological intensity from the warm-dark tradition "
            "of Giorgione and early Titian.  "
            "(3) Multi-scale chromatic vibration field — the session 120 artistic "
            "improvement.  A noise field composed of Gaussian-smoothed random noise "
            "at three spatial scales (σ ≈ 0.32×, 1×, 2.4× noise_scale, default 25 px) "
            "is weighted and combined to produce a smooth, non-uniform modulation map.  "
            "Applied in the mid-tone zone (mid_lo–mid_hi) with amplitude vibration_str "
            "(≈ 0.010), it adds a spatially varying warm/cool shift to each pixel — "
            "some areas slightly warmer, others slightly cooler — modelling the optical "
            "complexity of Venetian multi-glaze technique.  Each spatial scale models "
            "one glaze layer: fine grain (σ × 0.32) captures stroke-level pigment "
            "variation; medium (σ × 1) models the glaze layer; coarse (σ × 2.4) "
            "models the atmospheric imprimatura breathing through.  Their weighted "
            "combination (0.50 fine + 0.35 medium + 0.15 coarse) creates the chromatic "
            "'singing quality' that Lotto's flesh is known for — the warm-cool "
            "variation that makes skin look alive rather than uniformly tinted.  "
            "Use opacity ≈ 0.26–0.34."
        ),
    ),

    # ── Giovanni Boldini ───────────────────────────────────────────────────────
    # Giovanni Boldini (1842–1931) — the Ferrarese-born 'Master of Swirl' and
    # supreme virtuoso of Belle Époque portraiture in Paris.  Trained in Florence
    # under Stefano Ussi and in London before settling permanently in Paris in
    # 1871, Boldini became the most fashionable and technically audacious portrait
    # painter of the late nineteenth and early twentieth century.  His defining
    # technique — the diagonal swirling brushstroke applied at two or more
    # overlapping angles — creates a visual energy unlike anything in academic
    # portraiture: the surface appears to be in motion even in still repose.
    # The face and hands emerge as resolved zones of luminous warmth against a
    # near-black background that dissolves into directional gestural energy.
    "boldini": ArtStyle(
        artist="Giovanni Boldini",
        movement="Italian Belle Époque / Parisian Portraiture",
        nationality="Italian (Ferrarese, later Parisian)",
        period="c. 1860–1931",
        palette=[
            (0.90, 0.78, 0.62),   # warm ivory flesh — luminous, slightly tawny
            (0.72, 0.55, 0.42),   # warm rose mid-flesh — characteristic carnation
            (0.15, 0.10, 0.07),   # near-black background void — deep dramatic ground
            (0.38, 0.28, 0.18),   # warm brown shadow — chestnut depth in darks
            (0.60, 0.50, 0.35),   # warm ochre transition — figure-to-background bridge
            (0.94, 0.88, 0.76),   # cream highlight — luminous peak, warm ivory crest
        ],
        ground_color=(0.28, 0.20, 0.13),    # dark warm chestnut — Boldini favoured
        #                                     near-black grounds from which the
        #                                     luminous figure emerges dramatically
        stroke_size=8,
        wet_blend=0.30,                      # low-moderate — loose directional strokes
        #                                     retain individual energy; not dissolved
        edge_softness=0.50,                  # moderate — figures emerge softly from
        #                                     dark backgrounds with luminous edge quality
        jitter=0.048,                        # high — gestural energy, varied stroke colour
        glazing=(0.40, 0.30, 0.15),          # warm amber-chestnut final glaze
        crackle=False,
        chromatic_split=False,
        technique=(
            "Giovanni Boldini (1842–1931) was the supreme virtuoso of Belle Époque portraiture "
            "— the Ferrarese-born, Parisian-adopted 'Master of Swirl' whose sitters appeared "
            "to be caught in a moment of animated movement even in still repose.  Trained in "
            "Florence and London before settling permanently in Paris in 1871, Boldini combined "
            "the tonal grandeur of Old Master practice (dark grounds, luminous figures emerging "
            "from deep shadow) with a new gestural freedom that anticipated twentieth-century "
            "Expressionism.  His defining technique is the diagonal swirling brushstroke: "
            "loaded with paint and drawn at two or three overlapping angles across the canvas, "
            "these marks create a visual vibration — a sense that the painted surface itself is "
            "in motion.  Fabric, hair, and background environment are almost dissolved into this "
            "directional energy; only the face and hands emerge as zones of resolution and focus, "
            "rendered with greater precision against the surrounding swirl.  "
            "Boldini's palette is organized around a warm tonal hierarchy: near-black grounds "
            "(raw umber + ivory black), deep warm shadows (Van Dyck brown register), warm "
            "mid-tones (rose-ochre carnations), and luminous ivory-cream highlights.  The flesh "
            "tones are warm rather than cool — a deliberate opposition to the silvery flesh of "
            "his contemporaries like Sargent.  Where Sargent's bravura is crisp and "
            "architectural, Boldini's is flowing and curvilinear: the strokes follow the "
            "movement of drapery folds and hair rather than the structure of underlying anatomy.  "
            "Famous sitters include the Marchesa Luisa Casati (1908), Madame Charles Max (1896), "
            "Consuelo Vanderbilt Duchess of Marlborough (1906), and Giovinetta Errazuriz (1892).  "
            "His late works — executed in his eighties with increasingly wild brushwork — "
            "anticipate the gestural abstraction of Abstract Expressionism by several decades."
        ),
        famous_works=[
            ("Portrait of the Marchesa Luisa Casati",       "1908"),
            ("Portrait of Madame Charles Max",               "1896"),
            ("Portrait of the Duchess of Marlborough",       "1906"),
            ("Portrait of Giovinetta Errazuriz",             "1892"),
            ("Portrait of James Abbott McNeill Whistler",    "1897"),
            ("Portrait of Count Robert de Montesquiou",      "1897"),
            ("Girl in White",                                "c. 1884"),
            ("Portrait of Mademoiselle Lantelme",            "1907"),
        ],
        inspiration=(
            "Apply boldini_swirl_bravura_pass() as the defining stylistic pass for session 121.  "
            "The pass encodes Boldini's signature in three stages:  "
            "(1) Dual-angle diagonal swirl field — the session 121 artistic improvement.  Two "
            "anisotropic streak fields are computed at primary angle ~45° and secondary angle "
            "~-28° (Boldini's strokes cross at roughly these competing angles in his most "
            "characteristic works — the Marchesa Casati 1908, Madame Max 1896).  Each streak "
            "field is built by rotating the luminance swirl mask, applying an anisotropic "
            "Gaussian (σ_along=14px >> σ_across=1.5px), then rotating back.  The two fields "
            "are combined: primary at full swirl_str (≈ 0.038), secondary at half (swirl_str "
            "× 0.50).  Applied to the upper mid-tone and highlight zone (lum > swirl_lo ≈ "
            "0.42) via a smooth ramp mask, the result is a warm ivory brightness modulation "
            "along two crossing axes — approximating the visual complexity of superimposed "
            "directional brushstrokes.  Unlike Batoni's single-angle silk sheen (session 119), "
            "the dual crossing angles produce Boldini's characteristic 'swirl' rather than a "
            "weave-direction shimmer.  "
            "(2) Warm flesh luminosity lift — in the upper mid-tone zone of the figure (lum "
            "range 0.50–0.85), lift R + flesh_r (≈ 0.016), G + flesh_g (≈ 0.009), slightly "
            "reduce B (-flesh_b ≈ 0.005).  Boldini's flesh has a warm, slightly tawny quality "
            "— ivory with a faint warm rose undertone — contrasting strongly with the cool "
            "near-black background.  "
            "(3) Background darkening — in the background zone (outside figure mask), multiply "
            "all channels by dark_factor (≈ 0.94) and add a faint warm R undertone (bg_warm_r "
            "≈ 0.005).  Boldini's backgrounds have a slightly warm dark quality — not pure "
            "neutral black but a deep chestnut-umber register.  "
            "Use at opacity ≈ 0.28–0.36."
        ),
    ),

    # ── Salvator Rosa ─────────────────────────────────────────────────────────
    # Randomly selected artist for session 123's inspiration.
    # Salvator Rosa (1615–1673) — Neapolitan/Roman Baroque painter, poet,
    # musician, and actor — was the most deliberately Romantic personality in
    # 17th-century European painting before Romanticism had a name.  Born in
    # Naples during the heyday of Ribera and Caravaggio's influence, Rosa
    # trained briefly under Francesco Fracanzano (Ribera's son-in-law) before
    # establishing himself in Rome as a ferocious critic of academic convention
    # and a champion of wild, unpeopled wilderness landscapes.
    #
    # His paintings resist categorisation: part Baroque tenebrism (the dark
    # grounds and dramatic light inherited from Ribera), part proto-Romantic
    # sublime (the wind-torn trees, stormy skies, and banditti lurking in
    # craggy ravines that made him a cult figure for later generations), and
    # part satirist (his *Satires* in verse skewered academic painters as
    # parasites).  He refused all court patronage, insisting on complete
    # artistic independence — a stance almost without parallel in his era.
    #
    # Technical signature: Rosa's most distinctive quality is *gestural
    # turbulence* — a restless, wind-blown energy that animates every surface.
    # His landscapes feel as if a storm has just passed or is about to break.
    # Technically this arises from his alla-prima bravura: broad, irregular
    # strokes that follow no single direction, leaving the surface in a state
    # of perpetual visual motion.  Deep, raw umber shadows pressed in from
    # every edge; only the central focus catches warm amber light.
    #
    # Pipeline key: salvator_rosa_wild_bravura_pass() — the session 123
    # artistic improvement: a multi-scale turbulent displacement field that
    # warps the canvas pixels via stochastic spatial offsets, creating the
    # impression of gestural energy and atmospheric turbulence.  This is the
    # first pass in the pipeline to use image-space warping (displacement)
    # rather than pure per-pixel colour modification.
    "salvator_rosa": ArtStyle(
        artist="Salvator Rosa",
        movement="Baroque / Proto-Romantic Landscape",
        nationality="Italian (Neapolitan/Roman)",
        period="c. 1635–1673",
        palette=[
            (0.55, 0.38, 0.20),   # warm raw umber — his characteristic dark warm shadow
            (0.24, 0.18, 0.10),   # deep Vandyke brown — near-black foliage and void
            (0.72, 0.58, 0.32),   # amber highlight — the sudden warm light in storm dark
            (0.35, 0.42, 0.28),   # stormy olive green — his landscape distance
            (0.62, 0.62, 0.70),   # cool grey-blue — storm sky and atmospheric haze
            (0.88, 0.72, 0.48),   # warm ochre flesh — figures in dramatic light
        ],
        ground_color=(0.18, 0.12, 0.07),    # near-black raw umber ground — Rosa
        #                                     almost always worked on a near-black
        #                                     ground, so the darks are the canvas
        #                                     itself showing through thin paint
        stroke_size=12,
        wet_blend=0.22,                      # low blending — the gestural brushwork
        #                                     is directional and energetic, not smoothed
        edge_softness=0.38,                  # moderate crispness — storm-charged forms
        #                                     have a tense, agitated edge quality
        jitter=0.055,                        # high jitter — irregular, turbulent stroke
        glazing=(0.28, 0.20, 0.10),          # deep umber varnish — unifying dark tonal glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Salvator Rosa (1615–1673) was the most deliberately unconventional personality "
            "in 17th-century European art — a Neapolitan painter, poet, musician, and actor "
            "who refused all court patronage and built a career on studied defiance of academic "
            "convention.  Trained briefly in Naples under the Ribera circle, he moved to Rome "
            "in 1639 and eventually settled there permanently in 1649, becoming the favourite "
            "painter of the *bamboccianti* intelligentsia and later a cult figure for the "
            "Romantics who saw in him a proto-Romantic hero a century before Romanticism existed.  "
            "His landscapes — vast, craggy, storm-charged wilderness scenes populated by "
            "armed banditti, hermit philosophers, and mythological wanderers — are the most "
            "dramatic natural environments in Baroque painting.  Where Claude Lorrain painted "
            "golden Mediterranean calm, Rosa painted the sublime terror of wilderness: "
            "wind-tortured trees, fractured rock faces, and skies bruised with threatening cloud.  "
            "His figure paintings include ambitious allegories (*L'Umana Fragilità*, c. 1656; "
            "*Fortune*, c. 1658–1659) and self-portraits of studied Romantic melancholy "
            "(*Self-Portrait as Democritus*, c. 1651–1655) — in which he presents himself as "
            "a brooding philosopher-artist, not a court craftsman.  "
            "Technical signature: Rosa's brushwork is deliberately turbulent — broad, irregular, "
            "direction-less strokes that leave the painted surface in perpetual visual motion.  "
            "He worked on near-black raw umber grounds so that shadows are simply the canvas "
            "visible through thin, transparent paint; only the focal areas of warm amber light "
            "receive opaque, loaded impasto.  The result is a chiaroscuro more extreme than "
            "Caravaggio's but less systematic — the darkness feels atmospheric and unpredictable "
            "rather than theatrical and controlled.  His edges are agitated: never crisp like "
            "Velázquez, never dissolved like Leonardo, but in a perpetual state of energetic "
            "tension between definition and dissolution."
        ),
        famous_works=[
            ("L'Umana Fragilità (Human Frailty)",         "c. 1656"),
            ("Self-Portrait as Democritus",                "c. 1651–1655"),
            ("Landscape with Soldiers and Hunters",        "c. 1670"),
            ("The Conspiracy of Catiline",                 "c. 1663–1664"),
            ("Witches at their Incantations",              "c. 1646"),
            ("Fortune",                                    "c. 1658–1659"),
            ("Landscape with Tobias and the Angel",        "c. 1660–1665"),
            ("Jason and the Dragon",                       "c. 1668–1670"),
        ],
        inspiration=(
            "Apply salvator_rosa_wild_bravura_pass() as the defining pass for session 123.  "
            "The pass encodes Rosa's gestural turbulence in three stages built around the "
            "session 123 artistic improvement: the multi-scale turbulent displacement field.  "
            "(1) Turbulent displacement field — the session 123 artistic improvement.  All "
            "previous passes in this pipeline modify pixel colour values in place (additive "
            "blends, temperature shifts, saturation adjustments).  This pass introduces a "
            "fundamentally different operation: spatial image warping via a stochastic "
            "displacement field.  The field is generated by summing N_OCTAVES octaves of "
            "Gaussian-filtered random noise at doubling spatial scales (sigma = 2, 4, 8, 16 px), "
            "each octave weighted by 1/(octave+1) following a 1/f pink-noise power spectrum.  "
            "The summed field is normalised, then split into two orthogonal displacement "
            "components (dx, dy) by rotating the field vector by 90°.  These are scaled by "
            "max_disp (≈ 1.5–2.5 px) and used to warp the canvas via scipy.ndimage.map_coordinates. "
            "Applied at low opacity (≈ 0.20–0.28), the result is a subtle but pervasive gestural "
            "turbulence — as if the canvas were viewed through gently disturbed air.  "
            "(2) Dark vignette deepening — multiply border pixels toward deep umber, pressing "
            "darkness in from all edges (Rosa's characteristic charged atmospheric borders).  "
            "(3) Warm shadow glow — add a faint raw umber warmth to the deep shadow zone "
            "(lum < shadow_hi), reflecting the warm dark canvas ground glowing through thin "
            "transparent paint.  "
            "Use at opacity ≈ 0.22–0.30."
        ),
    ),

    # ── Annibale Carracci ─────────────────────────────────────────────────────
    "annibale_carracci": ArtStyle(
        artist="Annibale Carracci",
        movement="Bolognese School / Early Baroque",
        nationality="Italian (Bolognese)",
        period="c. 1582–1609",
        palette=[
            (0.86, 0.71, 0.52),   # warm amber flesh — golden, naturalistic, directly observed
            (0.63, 0.49, 0.33),   # warm rose-brown mid-flesh — carnation with sienna depth
            (0.20, 0.14, 0.09),   # deep warm shadow — Vandyke brown, luminous depth
            (0.42, 0.52, 0.40),   # cool landscape green — atmospheric recession distance
            (0.66, 0.61, 0.50),   # warm ochre transition — penumbra temperature bridge
            (0.92, 0.84, 0.70),   # warm ivory highlight — naturalistic, not idealized
        ],
        ground_color=(0.42, 0.32, 0.20),    # warm sienna-brown imprimatura — the warm
        #                                     toned ground characteristic of Bolognese
        #                                     academic practice, allowing warmth to glow
        #                                     through glazed shadow zones
        stroke_size=7,
        wet_blend=0.55,                      # moderate blending — direct naturalistic
        #                                     painting; forms resolved without dissolving
        edge_softness=0.55,                  # moderate — clearly defined forms; Carracci
        #                                     rejected the artificial vagueness of late
        #                                     Mannerism in favour of direct observation
        jitter=0.028,                        # moderate — controlled naturalistic variation
        glazing=(0.60, 0.48, 0.28),          # warm amber-sienna unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Annibale Carracci (1560–1609) was the central figure of the Bolognese reform movement "
            "— the anti-Mannerist revolution that restored direct observation of nature as the "
            "foundation of painting after a generation of artificial elegance.  With his brother "
            "Agostino and cousin Ludovico, Annibale founded the Accademia degli Incamminati "
            "('Academy of the Progressives') in Bologna in 1582, the first formal teaching "
            "academy in European art, which trained a generation of Baroque masters including "
            "Guido Reni, Albani, and Domenichino.  "
            "Annibale's mature technique synthesises the warm flesh-tone tradition of Correggio "
            "(whom he studied carefully), the compositional clarity of Raphael, the coloristic "
            "richness of Titian, and the naturalistic directness of Flemish genre painting — a "
            "remarkable fusion of North and South Italian traditions.  His flesh tones are warm "
            "and golden, built on a sienna-toned ground that allows the warm imprimatura to glow "
            "through shadow glazes.  The defining characteristic of Bolognese naturalism is the "
            "directional tonal temperature field: lit surfaces receive warm amber-ochre warmth "
            "from the light source (typically upper-left in his portraits), while shadow faces "
            "develop a cool blue-violet tone from atmospheric and reflected light.  This "
            "warm-light / cool-shadow temperature contrast is physically motivated — it describes "
            "how a single warm light source modulates both colour temperature and luminance "
            "simultaneously — and creates an internal luminosity that distinguishes Bolognese "
            "work from both the uniform tonality of Venetian painting and the harsh tenebrism "
            "of the Caravaggisti.  "
            "His most celebrated works include the Farnese Gallery ceiling frescoes (1597–1602, "
            "Palazzo Farnese, Rome) — one of the most ambitious decorative programs of the "
            "Baroque era — and a series of intimate portraits including the *Self-Portrait on an "
            "Easel in a Workshop* (c. 1604) and the *Man with a Monkey* (c. 1591, Uffizi).  "
            "His genre scenes (*The Bean Eater*, c. 1580–1590) introduced a new dignity for "
            "humble subject matter that influenced Northern European genre painting for a century."
        ),
        famous_works=[
            ("Farnese Gallery ceiling frescoes",     "1597–1602"),
            ("Self-Portrait on an Easel in a Workshop", "c. 1604"),
            ("The Bean Eater",                       "c. 1580–1590"),
            ("Man with a Monkey",                    "c. 1591"),
            ("Pietà",                                "c. 1599–1600"),
            ("Assumption of the Virgin",             "1587"),
            ("The Butcher's Shop",                   "c. 1582–1583"),
            ("Flight into Egypt",                    "1604"),
        ],
        inspiration=(
            "Apply annibale_carracci_tonal_reform_pass() as the defining pass for session 122.  "
            "The pass encodes the Bolognese naturalistic reform in three stages built around the "
            "session 122 artistic improvement: the spatially-varying directional tonal temperature "
            "field.  "
            "(1) Directional temperature field — the session 122 artistic improvement.  Unlike "
            "prior passes that use only luminance value (a scalar) to drive color adjustments, "
            "this pass computes the luminance *gradient* (a 2-D vector via Sobel operators) to "
            "distinguish lit-face from shadow-face pixels.  The dot product between the normalised "
            "gradient direction and a user-specified light direction vector produces a signed "
            "field in [-1, 1]: positive values indicate that luminance rises toward the light "
            "(lit face); negative values indicate that luminance falls toward the light (shadow "
            "face).  Warm colour temperature shift (R+, G+, B-) is applied proportionally to "
            "the positive lobe; cool shift (R-, G+, B+) is applied proportionally to the "
            "negative lobe.  Both effects are restricted to the penumbra luminance zone "
            "(penumbra_lo...penumbra_hi) where temperature contrast is perceptually strongest, "
            "and smoothed with a Gaussian to create soft transitions between the two regions.  "
            "This is a physically motivated model of how a warm point light source (upper-left "
            "in Bolognese painting) generates simultaneous luminance and temperature gradients.  "
            "(2) Warm ground glow — in the deep shadow zone (lum < shadow_hi), add a faint warm "
            "amber undertone (R += shadow_warm_r, G += shadow_warm_g).  Carracci built on a "
            "warm sienna imprimatura that glows through transparent shadow glazes, giving his "
            "darks a warm luminous depth rather than neutral blackness.  "
            "(3) Highlight ivory lift — in the specular highlight zone (lum > hi_lo), add a "
            "slight warm ivory lift (R += hi_r, G += hi_g).  Carracci's lights are naturalistic "
            "warm ivory, not the cold blue-white of Northern European masters or the pearl-grey "
            "of Florentine Mannerism.  "
            "Use at opacity ≈ 0.28–0.36."
        ),
    ),

    # ── Massimo Stanzione ─────────────────────────────────────────────────────
    "massimo_stanzione": ArtStyle(
        artist="Massimo Stanzione",
        movement="Neapolitan Baroque Classicism",
        nationality="Italian (Neapolitan)",
        period="c. 1620–1656",
        palette=[
            (0.90, 0.80, 0.64),   # warm ivory highlight — Reni-derived luminous flesh bloom
            (0.76, 0.60, 0.40),   # golden mid-flesh — warm Bolognese carnation
            (0.54, 0.38, 0.22),   # amber penumbra — warm transition zone with golden depth
            (0.32, 0.24, 0.36),   # cool violet shadow — restrained Caravaggist shadow depth
            (0.68, 0.64, 0.78),   # lavender penumbra glow — cool reflected light from shadow
            (0.20, 0.14, 0.10),   # near-black umber — deep shadow ground (Neapolitan Baroque)
        ],
        ground_color=(0.46, 0.36, 0.22),    # warm amber-brown imprimatura — Bolognese-derived
        stroke_size=6,
        wet_blend=0.72,                      # smooth blending — classicist restraint; Reni-influenced
        edge_softness=0.68,                  # moderate sfumato — resolved forms, not dissolved
        jitter=0.022,                        # controlled variation — classical discipline
        glazing=(0.64, 0.52, 0.30),          # warm amber-sienna unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Massimo Stanzione (c. 1585–1656), known as 'il Cavalier Calabrese' (the Calabrian "
            "Knight), was the dominant figure of Neapolitan painting in the second quarter of the "
            "17th century — the master who mediated between the harsh tenebrism of Caravaggio and "
            "Ribera on one hand and the luminous classicism of Guido Reni on the other.  "
            "Stanzione trained in Naples under Giovan Battista Caracciolo and made extended visits "
            "to Rome (c. 1617–1618 and again c. 1625–1630), where prolonged study of Bolognese "
            "academic painting — especially Guido Reni, whose smooth idealized flesh quality he "
            "absorbed deeply — transformed his palette from the raw darkness of early Caravaggism "
            "toward a refined, luminous classicism perfectly suited to devotional altarpieces and "
            "aristocratic portraiture.  He is sometimes called the 'Neapolitan Guido Reni,' a "
            "designation that captures both his debt to Reni's alabaster skin quality and his "
            "independent achievement: Stanzione's flesh is warmer, more golden, more earthily "
            "Mediterranean than Reni's cool Bolognese pearl.  "
            "His defining technical quality is the reconciliation of two forces normally in "
            "opposition: the warm sculptural shadow depth inherited from the Caravaggist tradition "
            "(deep cast shadows, controlled tenebrism) and the smooth luminous flesh bloom derived "
            "from Reni (warm ivory highlights, seamlessly blended penumbra transitions, glazed "
            "inner-light quality).  The result is a flesh tone of unusual complexity: warm golden "
            "in the light, cooling through a lavender-violet penumbra zone into a deep amber-brown "
            "shadow that has just enough warmth to glow rather than simply go dark.  His edges are "
            "resolved — neither sfumato dissolution nor Flemish crispness, but the clear-eyed form "
            "definition of Bolognese academic training applied to the warmer, darker Neapolitan "
            "tradition.  "
            "Major works include the *Judith with the Head of Holofernes* (Prado, c. 1630s) — one "
            "of the most psychologically composed Judith treatments of the era — the *Pietà* (Prado), "
            "the *Baptism of Christ* (S. Giovanni dei Fiorentini, Naples, c. 1635), the extensive "
            "fresco cycles for S. Maria Donna Regina Nuova and S. Paolo Maggiore, and a group of "
            "refined aristocratic portraits combining Reni's smooth flesh with the psychological "
            "directness of the Caravaggist naturalist tradition."
        ),
        famous_works=[
            ("Judith with the Head of Holofernes",           "c. 1630s"),
            ("Pietà",                                         "c. 1637"),
            ("Baptism of Christ",                             "c. 1635"),
            ("Assumption of the Virgin",                      "c. 1638"),
            ("Allegory of Music",                             "c. 1634–1638"),
            ("Susanna and the Elders",                        "c. 1630"),
            ("Saint John the Baptist in the Desert",          "c. 1634"),
            ("Frescoes, S. Maria Donna Regina Nuova, Naples", "c. 1638–1646"),
        ],
        inspiration=(
            "Apply stanzione_noble_repose_pass() as the defining pass for session 124.  "
            "The pass encodes Stanzione's Neapolitan Baroque classicism in three stages built "
            "around the session 124 artistic improvement: the Laplacian pyramid multi-scale "
            "clarity pass.  "
            "(1) Laplacian pyramid multi-scale clarity — the session 124 artistic improvement.  "
            "All previous passes in this pipeline operate either in colour-space (additive blends, "
            "temperature shifts, luminance lifts) or in spatial domain (image warping via "
            "displacement fields).  This pass introduces a fundamentally different approach: "
            "frequency-band decomposition via a stationary Laplacian pyramid.  The canvas is "
            "decomposed into four frequency bands by subtracting progressively smoothed versions "
            "(sigma = 2, 4, 8 px Gaussian): L0 = fine detail (~2 px); L1 = mid-frequency facial "
            "structure (~4 px); L2 = coarse tonal form (~8 px); L3 = global tonal base.  The "
            "mid-frequency band L1 is selectively boosted (contrast enhancement of facial planes "
            "and structural form), while L0 is gently suppressed (fine noise reduction for "
            "sfumato-like surface smoothness).  The canvas is then reconstructed with the adjusted "
            "bands.  This replicates the perceptual effect of careful Bolognese glazing — where "
            "thin transparent layers built up over time enhance mid-frequency structural clarity "
            "while smoothing out surface irregularities at the finest scale.  "
            "(2) Warm ivory highlight lift — in the luminance highlight zone (lum > hi_lo), add a "
            "warm ivory tone (R += ivory_r, G += ivory_g).  Stanzione's lights are Reni-derived: "
            "warm golden-ivory, not the cool pearl of Northern masters or the blue-white of "
            "Florentine academic idealism.  "
            "(3) Cool violet shadow penumbra — in the mid-shadow zone (penumbra_lo...penumbra_hi), "
            "add a subtle cool violet shift (B += violet_b, R -= violet_r).  Stanzione's shadows "
            "retain Caravaggist depth but replace raw darkness with a cool lavender-violet tone "
            "from atmospheric and reflected light — the zone where warm Bolognese classicism "
            "meets Caravaggist shadow discipline.  "
            "Use at opacity ≈ 0.28–0.36."
        ),
    ),

    # ── Fra Bartolommeo ───────────────────────────────────────────────────────
    "fra_bartolommeo": ArtStyle(
        artist="Fra Bartolommeo",
        movement="Florentine Monumental Classicism",
        nationality="Italian (Florentine)",
        period="c. 1490–1517",
        palette=[
            (0.92, 0.82, 0.66),   # warm ivory flesh — lit face, rich Florentine warmth
            (0.80, 0.65, 0.50),   # rose-amber midtone — the characteristic warm penumbra
            (0.56, 0.42, 0.30),   # deep chestnut shadow — voluminous, Leonardesque depth
            (0.30, 0.22, 0.14),   # near-black shadow trough — deep architectural darkness
            (0.30, 0.42, 0.64),   # Dominican blue — sapphire drapery, spiritual register
            (0.62, 0.70, 0.46),   # sage-olive landscape — hills behind devotional figures
            (0.80, 0.72, 0.52),   # warm amber-gold — gilded highlights and divine light
            (0.72, 0.60, 0.44),   # warm ground tone — Florentine imprimatura warmth
        ],
        ground_color=(0.64, 0.52, 0.34),    # warm chestnut-amber imprimatura
        stroke_size=5,
        wet_blend=0.72,                      # high — smooth monumental surfaces
        edge_softness=0.58,                  # moderate — resolved but not crisp; soft Florentine sfumato
        jitter=0.016,
        glazing=(0.70, 0.58, 0.38),          # warm amber-chestnut unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Fra Bartolommeo (1472–1517) — born Baccio della Porta, later Frate Bartolommeo di "
            "San Marco — is the supreme master of Florentine monumental classicism in the High "
            "Renaissance.  Trained in Cosimo Rosselli's workshop alongside Piero di Cosimo and "
            "Albertinelli, he absorbed the Florentine draughtsmanship tradition, then underwent "
            "a profound spiritual crisis under Savonarola's influence: he burned his secular "
            "paintings in the Bonfire of the Vanities (1497) and entered the Dominican priory of "
            "San Marco (Michelangelo's Fra Angelico's house) where he painted nothing for four "
            "years.  When he returned to painting in 1504, his style had transformed entirely: "
            "the intimate quattrocento linearity replaced by a monumental, architectural grandeur "
            "synthesizing Leonardo's sfumato, Raphael's harmonious clarity, and Michelangelo's "
            "sculptural weight into the definitive Florentine High Renaissance figure idiom.  "
            "His most distinctive technical practice was the 'velo' ('veil') — a sheer cloth "
            "draped over posed lay figures or mannequins to study the behavior of light and shadow "
            "as they travel across complex three-dimensional forms.  The velo produced a specific "
            "visual quality: where the cloth stretched taut over a protruding form, it caught the "
            "light and marked the ridge precisely; where it fell into shadow on the receding "
            "surface, the shadow deepened in a graduated, precisely-bounded gradient.  This "
            "gave Fra Bartolommeo's painted forms — especially drapery and monumental architectural "
            "figures — an unusually clear tonal boundary between light and shadow zones: not "
            "Leonardo's smoky sfumato dissolution, but a more articulated, volumetrically "
            "decisive statement of where form turns away from the light source.  His palette "
            "is warm, saturated, and rich: deep chestnut-amber grounds, warm rose-ivory flesh, "
            "deep architectural shadows that never read as flat but retain volumetric warmth, "
            "and — when he painted devotional subjects — a luminous Dominican blue that gives "
            "his Madonnas a spiritual radiance distinct from the cold Flemish blue of Van Eyck "
            "or the cool Venetian blue of Titian.  He was the master who transmitted the grand "
            "Florentine synthesis to subsequent generations, influencing Raphael, Andrea del "
            "Sarto, and the whole Florentine Mannerist tradition."
        ),
        famous_works=[
            ("Mystical Marriage of St. Catherine",        "1511"),
            ("God the Father with Saints",                "c. 1509"),
            ("Salvator Mundi",                            "c. 1516"),
            ("Portrait of Savonarola",                    "c. 1498"),
            ("Madonna della Misericordia",                "1515"),
            ("St Mark Enthroned",                         "1514"),
            ("The Carondelet Diptych",                    "c. 1511–1512"),
            ("Great Last Judgement fresco (S. Marco)",    "c. 1499–1501"),
        ],
        inspiration=(
            "Apply fra_bartolommeo_velo_shadow_pass() as the defining pass for session 126.  "
            "The pass encodes Fra Bartolommeo's velo technique in three stages built around "
            "the session 126 artistic improvement: Sobel-gradient-driven form boundary modulation.  "
            "(1) Sobel-based form-ridge detection — the session 126 artistic improvement.  "
            "All previous passes in this pipeline operate in one of three modes: "
            "colour-space transforms (temperature shifts, luminance lifts), "
            "frequency-band decomposition (Laplacian pyramid, s124), or "
            "spatial-gradient fields (aerial perspective, s125).  "
            "This pass introduces a fourth, fundamentally different mode: "
            "EDGE-MAP-DRIVEN selective modulation.  A Gaussian-smoothed luminance map is "
            "processed through the Sobel operator (horizontal: axis=1, vertical: axis=0), "
            "yielding a gradient magnitude map that precisely locates the tonal boundary "
            "zones where light-side meets shadow-side on three-dimensional forms — exactly "
            "what Fra Bartolommeo studied using his velo.  This gradient mask is then used "
            "to apply selective color-temperature contrast only at detected form ridges.  "
            "(2) Warm thermal lift on lit side of form transitions — in zones where the "
            "luminance is above the penumbra midpoint AND the Sobel gradient is significant, "
            "add a warm R/G lift.  Fra Bartolommeo's lit form-ridges catch warm directional "
            "light and read as luminous amber-ivory against the shadowed trough.  "
            "(3) Cool shadow deepening on shadow side — in zones where the luminance is "
            "below the penumbra midpoint AND the Sobel gradient is significant, add a cool "
            "blue deepening.  Fra Bartolommeo's shadow troughs — especially in the velo "
            "drapery studies — have a precise, resolved quality: not Leonardo's smoky "
            "dissolution but a crisply-bounded volumetric statement.  "
            "Use at opacity ≈ 0.26–0.34."
        ),
    ),

    # ── Francesco Albani ──────────────────────────────────────────────────────
    "albani": ArtStyle(
        artist="Francesco Albani",
        movement="Bolognese Arcadian Classicism",
        nationality="Italian (Bolognese)",
        period="c. 1600–1660",
        palette=[
            (0.95, 0.88, 0.78),   # pearl ivory — the ambient light that bathes Albani's figures
            (0.88, 0.72, 0.64),   # rose-peach flesh — his characteristic warm, sweetly idealized skin
            (0.72, 0.58, 0.44),   # warm mid-shadow — amber penumbra, soft Carracci-derived transition
            (0.62, 0.70, 0.82),   # sky blue — the cool aerial blue that fills shadow zones in outdoor scenes
            (0.54, 0.65, 0.42),   # sage green — pastoral foliage, muted and harmonious, never harsh
            (0.84, 0.76, 0.52),   # warm gold — sunlit grass and distant ground planes, Arcadian warmth
        ],
        ground_color=(0.74, 0.64, 0.46),    # warm honey-amber imprimatura — Bolognese academic ground
        stroke_size=5,
        wet_blend=0.80,                      # very smooth blending — Albani's surfaces are silky, unified
        edge_softness=0.72,                  # soft but resolved — pastoral idealism, not sfumato dissolution
        jitter=0.018,                        # very low variation — sweet, harmonious, no raw stroke tension
        glazing=(0.78, 0.68, 0.50),          # warm amber-gold unifying glaze — Bolognese warmth
        crackle=True,
        chromatic_split=False,
        technique=(
            "Francesco Albani (1578–1660) was the Bolognese master of the Arcadian idyll — the painter "
            "who transformed the severe academic naturalism of his teacher Annibale Carracci into a "
            "world of sunlit pastoral grace, delicate mythological playfulness, and sweetly idealized "
            "figures bathed in soft, even ambient light.  He studied in the Carracci Academy alongside "
            "Guido Reni and Domenichino, absorbing the Bolognese reform of colour temperature and "
            "tonal discipline, but where Reni pursued transcendent spiritual luminosity and Domenichino "
            "pursued intellectual narrative clarity, Albani pursued the sensuous pleasure of "
            "harmonious pastoral beauty — the 'pittore delle Grazie' (painter of the Graces), as he "
            "was known to his contemporaries.  "
            "His palette is characteristic and immediately recognizable: pearl-ivory ambient light "
            "that fills the entire pictorial space, rose-peach flesh tones of exquisite sweetness, "
            "muted sage-green foliage that never competes with the figures, warm golden ground "
            "planes in sunlit outdoor scenes, and — his most distinctive technical touch — a "
            "delicate cool sky-blue that enters the shadow zones of outdoor figures, modeling the "
            "reflected light from an open sky rather than the warm reflected ground typical of "
            "interior Baroque chiaroscuro.  This cool sky-reflected shadow is the optical signature "
            "of painting figures en plein-air in classical Arcadian settings, and Albani deployed it "
            "with systematic consistency across his entire career.  "
            "His surfaces are among the smoothest in Bolognese painting — more seamless even than "
            "Reni in the flesh zones, with a silky, porcelain-adjacent quality that sets his figures "
            "apart from both the rougher realism of the Caravaggists and the harder idealism of "
            "later academic painters.  He built up surfaces with thin, patient oil glazes over a "
            "warm imprimatura, never allowing impasto texture to disrupt the lyrical softness of "
            "his pastoral world.  "
            "Major works include the four large *Albani Tondi* (Galleria Borghese, Rome), the "
            "*Diana and Actaeon* series, the *Venus with Putti* (Pinacoteca di Bologna), and "
            "numerous oval cabinet pictures of mythological scenes with landscapes — the format "
            "that became his signature: intimate, harmonious, suffused with outdoor light."
        ),
        famous_works=[
            ("Diana and Actaeon",                          "c. 1617"),
            ("The Four Seasons (Albani Tondi)",            "c. 1616–1617"),
            ("Venus with Putti",                           "c. 1621"),
            ("The Baptism of Christ",                      "c. 1640"),
            ("Toilet of Venus",                            "c. 1622–1623"),
            ("Landscape with Diana Hunting",               "c. 1635"),
            ("Galatea",                                    "c. 1625"),
        ],
        inspiration=(
            "Apply albani_arcadian_grace_pass() as the defining pass for session 125.  "
            "The pass encodes Albani's Bolognese Arcadian Classicism in three stages built "
            "around the session 125 artistic improvement: chromatic aerial perspective.  "
            "(1) Chromatic aerial perspective — the session 125 artistic improvement.  "
            "All previous colour-manipulation passes in this pipeline operate either as "
            "uniform tone shifts (temperature field, ivory lift, violet penumbra) or as "
            "frequency-band operations (Laplacian pyramid, s124).  This pass introduces "
            "a new spatial dimension: a vertical gradient that applies progressive blue-grey "
            "cooling and saturation reduction from the lower foreground to the upper "
            "atmospheric distance — modeling the physical scattering of short-wavelength "
            "blue light by intervening atmosphere along long sight lines.  This is "
            "Leonardo's sfumato dell'aria, Albani's pastoral sky-fill, and the "
            "foundation of classical landscape painting's depth illusion.  "
            "(2) Rose-peach skin bloom — in mid-tone zones, add a delicate rose-peach "
            "warmth.  Albani's flesh is idealized and sweetly warm — not the Reni cool-pearl "
            "or Stanzione's Mediterranean golden ochre, but a lighter, softer peach that "
            "reads as the embodiment of pastoral innocence.  "
            "(3) Cool sky-reflected shadow — in the shadow zone, add a delicate cool "
            "blue-lavender tint.  Albani's shadow zones in outdoor settings catch the "
            "ambient sky light — pale blue-grey fills the penumbra, replacing the warm "
            "amber of interior candlelight with the cool reflective light of open sky.  "
            "Use at opacity ≈ 0.26–0.34."
        ),
    ),

    # ── Simone Cantarini ──────────────────────────────────────────────────────
    "simone_cantarini": ArtStyle(
        artist="Simone Cantarini",
        movement="Bolognese Renesque Silver Classicism",
        nationality="Italian",
        period="1612–1648",
        palette=[
            (0.92, 0.84, 0.76),   # ivory-pearl — cool white flesh highlight
            (0.84, 0.72, 0.65),   # rose-ivory mid-tone — warm carnation blush
            (0.62, 0.52, 0.48),   # penumbra grey-rose — the 'pearl-fog' zone
            (0.38, 0.32, 0.30),   # shadow umber — deep but never harsh
            (0.70, 0.74, 0.80),   # cool blue-pearl — scattered short-wavelength haze
            (0.58, 0.50, 0.34),   # warm ground — Reni's Bolognese amber imprimatura
        ],
        ground_color=(0.60, 0.52, 0.36),    # warm Bolognese amber ground
        stroke_size=4,
        wet_blend=0.82,                      # extremely smooth — Cantarini's multi-glaze finish
        edge_softness=0.74,                  # very soft sfumato, pearl-foggy penumbra
        jitter=0.04,
        glazing=(0.88, 0.82, 0.72),          # pale ivory unifying glaze — Reni's silver tonality
        crackle=False,
        chromatic_split=False,
        technique=(
            "Multi-layer spectral glazing creating wavelength-selective translucency. "
            "Cantarini applies eight to twelve superimposed transparent films of lead white, "
            "smalt (cobalt-blue glass), and lake over a warm amber ground, building a physically "
            "layered medium in which short-wavelength blue light scatters laterally in the upper "
            "glaze layers while long-wavelength red light penetrates deeper before reflecting. "
            "The result is the 'pearl-fog' penumbra: the shadow zone glows with a cool blue-violet "
            "iridescence while the warm ground structure remains legible beneath it. "
            "Flesh tones are extremely pale and refined — Reni's silver-white palette inflected "
            "with a distinctly personal rose warmth in the carnation zone. "
            "Unlike Reni's cooler, more impersonal flesh, Cantarini's has a gentle sensuality."
        ),
        famous_works=[
            ("Rest on the Flight into Egypt", "c.1635–40"),
            ("Madonna and Child with the Young St. John", "c.1638"),
            ("St. Joseph with the Christ Child", "c.1640"),
            ("Portrait of Guido Reni", "c.1637"),
            ("Holy Family with St. Anne", "c.1642"),
        ],
        inspiration=(
            "Apply cantarini_pearl_fog_pass() as the defining pass for session 127.  "
            "The pass encodes Cantarini's Bolognese Renesque Silver Classicism through "
            "spectral channel-selective diffusion — the session 127 artistic improvement.  "
            "Previous colour-manipulation passes in this pipeline treat all three RGB channels "
            "identically in their blur operations.  This pass introduces the fifth distinct "
            "processing mode: wavelength-dependent per-channel Gaussian blur, where σ_B > σ_G > σ_R, "
            "simulating Rayleigh-type scatter in Cantarini's translucent glaze stack.  "
            "The blue channel receives maximum blur (σ_B ≈ 3.5) — simulating the way short-wavelength "
            "light diffuses laterally through superficial smalt/lead-white layers.  "
            "The red channel receives minimal blur (σ_R ≈ 1.2) — simulating the way long-wavelength "
            "light penetrates to the warm ground before reflecting with relative crispness.  "
            "Combined, these create the 'pearl-fog': a softly glowing penumbra zone with a cool "
            "blue iridescence over warm undertones.  "
            "The pass also adds a gentle rose warmth in the highlight zone (Cantarini's carnations) "
            "and an ivory specular lift to prevent accumulated coolness from greying the image.  "
            "Use at opacity ≈ 0.28–0.36."
        ),
    ),

    # ── Vittore Carpaccio ──────────────────────────────────────────────────────
    "carpaccio": ArtStyle(
        artist="Vittore Carpaccio",
        movement="Venetian Narrative Luminism",
        nationality="Italian (Venetian)",
        period="c. 1465–1526",
        palette=[
            (0.90, 0.82, 0.66),   # warm ivory highlight — Carpaccio's luminous Venetian daylight
            (0.82, 0.68, 0.50),   # warm amber midtone — sunlit architectural surfaces, golden stone
            (0.70, 0.56, 0.40),   # ochre-warm shadow — rich mid-shadow, warm earth undertone
            (0.58, 0.44, 0.30),   # deep warm shadow — Venetian deep tonal reserve
            (0.48, 0.58, 0.74),   # cool sky blue — his distinctive Venetian sky-light in shadows
            (0.62, 0.70, 0.82),   # cool blue-grey — distant architecture, aerial perspective
            (0.72, 0.62, 0.44),   # mid amber ground — Venetian panel ground, warm honey
        ],
        ground_color=(0.78, 0.68, 0.50),    # warm Venetian honey imprimatura
        stroke_size=6,
        wet_blend=0.62,                      # moderate blending — crisp but not harsh, clear Venetian precision
        edge_softness=0.48,                  # moderately crisp — not sfumato; Carpaccio's edges are resolved
        jitter=0.022,                        # moderate variation — narrative richness, not monotone
        glazing=(0.70, 0.60, 0.40),          # warm amber-honey final glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Vittore Carpaccio (c. 1465–1526) was the supreme Venetian narrative painter — the artist "
            "who created some of the most expansive, luminously detailed, and storytelling-rich "
            "paintings in the entire Venetian tradition.  Born in Venice (possibly of Dalmatian "
            "origin), he spent almost his entire career in the city, producing the great narrative "
            "cycles that define Venetian public painting in the late Quattrocento and early "
            "Cinquecento: the cycle of Saint Ursula (Accademia, Venice), the Scuola di San Giorgio "
            "degli Schiavoni cycle, and the Miracle of the Relic of the True Cross.  He was deeply "
            "influenced by Gentile Bellini's documentary realism and by the clear, crystalline "
            "Venetian light that entered workshops through canal-reflected northern windows.  "
            "His defining technical quality is a paradoxical clarity: his canvases are filled with "
            "almost overwhelming detail — architectural panoramas, costumed processions, heraldic "
            "devices, inscriptions, animals, boats, flags — yet they read with a fresh, crystalline "
            "luminosity rather than the density of northern Mannerism.  This clarity comes from his "
            "handling of light: warm golden highlights on architectural surfaces and costume details "
            "sit against remarkably luminous, cool blue-grey shadow zones that catch the reflected "
            "light of the Venetian sky and canal water.  His penumbra zones are never muddy or "
            "opaque — they are permeated with reflected cool ambient light in a way that no "
            "interior-lit Baroque painter would achieve.  "
            "His palette is characteristically warm-dominant in highlights (amber-ivory, warm gold, "
            "ochre) but distinctively cool in shadow (sky blue, canal-reflected blue-grey, distant "
            "atmospheric lavender) — a warm/cool separation driven by the Venetian outdoor "
            "environment rather than by candle or torch.  This makes his shadows feel 'open' and "
            "inhabited by reflected light, giving his paintings their unusual quality of expansive "
            "luminosity even in complex, detailed narrative contexts.  "
            "He painted with a careful, moderately-blended technique: not the full sfumato "
            "dissolution of Leonardo, not the raw alla prima immediacy of Titian, but a clean, "
            "patient layering that builds crisp forms with carefully modulated transitions.  "
            "The local variance in his paintings — from the fine detail of embroidered costume to "
            "the smooth, even sky passages — is among the widest in Venetian painting, and this "
            "spatial specificity is precisely what carpaccio_venetian_clarity_pass() models: "
            "detecting high-variance detail zones and low-variance smooth zones, then applying "
            "fundamentally different refinement to each.  "
            "Major cycles include: Life of Saint Ursula (1490–1498), Life of Saint George and "
            "Saint Jerome (Scuola di San Giorgio, 1502–1507), and the Miracle of the True Cross "
            "(1494–1501, shared cycle with Gentile Bellini).  Individual masterworks include "
            "Two Venetian Ladies (c. 1490–1510), Dream of Saint Ursula (1495), and "
            "Presentation of Jesus in the Temple (1510)."
        ),
        famous_works=[
            ("Dream of Saint Ursula",                   "1495"),
            ("Saint George and the Dragon",              "c. 1502"),
            ("Two Venetian Ladies",                      "c. 1490–1510"),
            ("Miracle of the True Cross at the Rialto Bridge", "1494"),
            ("Presentation of Jesus in the Temple",     "1510"),
            ("Young Knight in a Landscape",              "1510"),
            ("Saint Stephen Disputing with the Doctors", "c. 1514"),
        ],
        inspiration=(
            "Apply carpaccio_venetian_clarity_pass() as the defining pass for session 128.  "
            "The pass encodes Carpaccio's Venetian Narrative Luminism in three stages built "
            "around the session 128 artistic improvement: LOCAL VARIANCE MAP SPATIAL ADAPTATION.  "
            "(1) Local variance map — the session 128 artistic improvement.  "
            "All previous passes in this pipeline operate in one of five modes: "
            "RGB colour-space transforms (s122 Carracci temperature field), "
            "spatial displacement (s123 Rosa Perlin warp), "
            "frequency decomposition (s124 Stanzione Laplacian pyramid), "
            "spatial depth gradient (s125 Albani aerial perspective), or "
            "edge-map-driven selective modulation (s126 Bartolommeo Sobel magnitude).  "
            "This pass introduces a sixth, fundamentally different mode: "
            "LOCAL VARIANCE MAP SPATIAL ADAPTATION.  "
            "A per-pixel local luminance standard deviation is computed as: "
            "std = sqrt(max(GaussBlur(lum²) - GaussBlur(lum)², 0))  "
            "using the difference-of-blurred-squares identity.  "
            "The resulting std_norm map distinguishes: "
            "std_norm ≈ 0 → smooth zone (skin, background sky, flat fabric areas), "
            "std_norm ≈ 1 → detail zone (hair, costume pattern, architectural relief).  "
            "These two zones receive fundamentally different treatment:  "
            "Detail zones get a local contrast boost (push each channel away from its blurred "
            "value, scaled by std_norm) — sharpening optically rich costume and architecture "
            "passages without over-sharpening smooth skin.  "
            "Smooth zones get gentle spatial smoothing (blend toward GaussBlur at smooth_zone_sigma) "
            "— Carpaccio's skin and sky passages are seamless, fresh, with no rough texture.  "
            "(2) Warm golden highlights — in lum > hi_lo zones, apply warm amber R/G lift.  "
            "Carpaccio's highlights on architectural stone and costume gold are distinctively "
            "warm amber-ivory, never cool or silvery.  "
            "(3) Cool luminous shadows — in lum < shadow_hi zones, apply cool blue B lift and "
            "slight R damp.  Carpaccio's shadow zones are permeated with Venice-sky-reflected "
            "cool blue light — never muddy brown, always luminous and spatially open.  "
            "Use at opacity ≈ 0.26–0.34."
        ),
    ),

    # ── Giovanni Battista Piazzetta ───────────────────────────────────────────
    "piazzetta": ArtStyle(
        artist="Giovanni Battista Piazzetta",
        movement="Venetian Baroque Tenebrism",
        nationality="Italian",
        period="1682–1754",
        palette=[
            (0.18, 0.12, 0.08),   # warm near-black velvet shadow — Piazzetta's deep tenebrism ground
            (0.42, 0.28, 0.18),   # warm umber mid-shadow — the transitional warmth zone
            (0.62, 0.50, 0.34),   # golden mid-flesh — the quiet warm bridge
            (0.82, 0.68, 0.48),   # amber impasto highlight — glowing thick warm light
            (0.94, 0.84, 0.64),   # bright highlight crest — the peak warm ivory-amber
            (0.35, 0.24, 0.14),   # deep chestnut shadow — warm-brown penumbra zone
        ],
        ground_color=(0.25, 0.17, 0.10),   # very dark warm umber ground — Piazzetta's tenebrism foundation
        stroke_size=5,
        wet_blend=0.55,                     # moderate — smooth transitions with impasto body
        edge_softness=0.40,                 # moderate — forms emerging from dark, not sfumato-dissolved
        jitter=0.022,                       # modest variation — painterly impasto texture
        glazing=(0.40, 0.32, 0.20),        # warm amber-umber unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Giovanni Battista Piazzetta (1682–1754) was the great independent master of the "
            "Venetian Baroque who refused assimilation into the dominant tradition of either "
            "Tiepolo's airy luminosity or the Bolognese academic classicism that surrounded him.  "
            "Where Tiepolo — his contemporary, pupil in spirit, and eventual rival — dissolved "
            "everything into celestial light, Piazzetta worked in the opposite direction: into "
            "darkness, excavating warmth from a near-black tenebrism ground.  His style owes "
            "something to Caravaggio's legacy (mediated via Giuseppe Maria Crespi, his teacher) "
            "and something to the Northern chiaroscuro tradition, but the result is distinctly "
            "Venetian: a warm velvet darkness rather than the Roman cold-stone void.  "
            "The defining quality of Piazzetta's surface is the contrast between his deep, soft, "
            "WARM VELVET DARKS — where the shadow zones are rich umber-brown near-blacks, velvety "
            "in texture, warm rather than cool, deeply compressed rather than luminously open — "
            "and his IMPASTO AMBER HIGHLIGHTS — where thick, warm-ivory paint is applied with "
            "visible relief, catching the light to create a glow that seems to emerge physically "
            "from the ground.  This is not the pearl-white of Guido Reni nor the cerulean cool of "
            "Domenichino; it is a candlelight amber warmth specific to Piazzetta's intimate "
            "Venetian chiaroscuro.  "
            "His most celebrated works — *The Fortune Teller* (Accademia, Venice, c. 1740), "
            "*Idyll on the Shore* (Wallraf-Richartz-Museum, c. 1740), *Saint James Led to "
            "Martyrdom* (San Stae, Venice, 1717), *Rebecca at the Well* (Brera, c. 1735) — all "
            "share this polar structure: the lower half of the tonal range compressed into warm "
            "velvet darkness, the upper range lifted into warm impasto glow, with the midtone zone "
            "serving as a quiet bridge between these two worlds.  "
            "Unlike Rembrandt (whose tenebrism is cool and metallic in the highlights) or "
            "Caravaggio (whose darks are cold and abrupt), Piazzetta's whole tonal range is warm — "
            "even the deepest shadows retain a umber-brown warmth, as if the darkness itself is "
            "suffused with candlelight.  This gives his paintings a sense of interior intimacy and "
            "psychological proximity that his more theatrical contemporaries rarely achieved.  "
            "He was a slow, deliberate painter — Tiepolo was said to complete what Piazzetta spent "
            "months on in a day — and this deliberateness is visible in the surface: every tonal "
            "transition is considered, every highlight carefully placed for maximum luminous impact "
            "against the surrounding velvet dark."
        ),
        famous_works=[
            ("The Fortune Teller",                "c. 1740"),
            ("Idyll on the Shore",                "c. 1740"),
            ("Saint James Led to Martyrdom",      "1717"),
            ("Rebecca at the Well",               "c. 1735"),
            ("The Soothsayer",                    "c. 1740"),
            ("Elijah Fed by an Angel",            "c. 1730"),
            ("The Standard Bearer",               "c. 1740"),
        ],
        inspiration=(
            "Apply piazzetta_velvet_shadow_pass() as the defining pass for session 129.  "
            "The pass encodes Piazzetta's Venetian Baroque Tenebrism around the session 129 "
            "artistic improvement: PERCENTILE-ADAPTIVE TONAL SCULPTING.  "
            "All previous colour-manipulation passes in this pipeline use LOCAL SPATIAL analysis: "
            "s123 spatial displacement (flow warping), s124 frequency decomposition (Laplacian "
            "pyramid), s125 vertical gradient (depth perspective), s126 Sobel edge-map modulation, "
            "s127 local variance field (sliding window), s128 local variance std map.  "
            "Session 129 introduces a fundamentally different mode: GLOBAL HISTOGRAM PERCENTILE "
            "ANALYSIS — operating on the rank-order structure of the ENTIRE image's luminance "
            "distribution rather than any local neighbourhood.  "
            "(1) Compute the flat luminance array for the full canvas.  "
            "(2) Sort and rank to produce a percentile map: each pixel maps to its rank in [0,1] "
            "within the global distribution — this is the novelty, a rank-order spatial weight.  "
            "(3) Shadow zone (percentile < shadow_percentile): apply warm-umber compression — "
            "push R slightly up, B slightly down — deepening the darks toward warm near-black with "
            "Piazzetta's characteristic velvet warmth.  The compression is gentle (not clipping) "
            "to preserve the velvety gradation within the dark zone.  "
            "(4) Highlight zone (percentile > highlight_percentile): apply warm amber lift — "
            "R and G up — simulating the glowing impasto warmth of Piazzetta's painted light.  "
            "(5) Midtone zone: untouched — the quiet neutral bridge that makes the polar contrast "
            "of Piazzetta's style feel natural rather than forced.  "
            "Use at opacity ≈ 0.28–0.36."
        ),
    ),

    # ── Sebastiano del Piombo ──────────────────────────────────────────────────
    "sebastiano_del_piombo": ArtStyle(
        artist="Sebastiano del Piombo",
        movement="Venetian-Roman Synthesis",
        nationality="Italian (Venetian-Roman)",
        period="1485–1547",
        palette=[
            (0.82, 0.65, 0.46),   # warm Venetian flesh — honey-ivory highlight
            (0.62, 0.46, 0.30),   # mid flesh — rich warm sienna
            (0.38, 0.26, 0.14),   # deep umber shadow — Venetian warm dark
            (0.20, 0.16, 0.10),   # near-black depth — Roman gravity void
            (0.46, 0.40, 0.28),   # olive-ochre mid-ground — Roman earth
            (0.55, 0.52, 0.44),   # cool grey-stone — Roman architectural cool
            (0.62, 0.54, 0.38),   # warm amber-ochre — Venetian glazing unity
        ],
        ground_color=(0.40, 0.30, 0.16),    # rich warm umber-ochre imprimatura
        stroke_size=6,
        wet_blend=0.78,                      # strong Venetian blending — rich, fused surface
        edge_softness=0.68,                  # Venetian-school softness; forms emerge without hard edge
        jitter=0.016,
        glazing=(0.55, 0.42, 0.24),          # deep amber-umber unifying glaze — Roman grandeur
        crackle=True,
        chromatic_split=False,
        technique=(
            "Venetian-Roman synthesis: Giorgione-derived sfumato-adjacent blending "
            "and rich warm color fused with Michelangelesque sculptural weight and "
            "monumental form gravity.  Smooth, deeply blended surfaces give the figure "
            "three-dimensional solidity without visible brushwork.  Shadow zones are "
            "warm and deep; highlights are warm ivory rather than cool silver."
        ),
        famous_works=[
            ("Portrait of a Young Roman Woman",          "c. 1512"),
            ("The Raising of Lazarus",                   "1519"),
            ("Portrait of Pope Clement VII",             "c. 1526"),
            ("Portrait of Ferry Carondelet",             "c. 1512"),
            ("Portrait of a Man (attributed)",           "c. 1515"),
            ("Pietà (Viterbo)",                          "c. 1516"),
            ("Portrait of Christopher Columbus",         "1519"),
        ],
        inspiration=(
            "Apply sebastiano_sculptural_depth_pass() as the defining pass for "
            "session 130.  The pass encodes Sebastiano's Venetian-Roman synthesis "
            "through the session 130 artistic improvement: IMAGE STRUCTURE TENSOR "
            "COHERENCE-DRIVEN FORM SMOOTHING — the eighth distinct processing mode "
            "in this pipeline.  "
            "Prior modes: (1) s123 Rosa — spatial displacement/flow warping; "
            "(2) s124 Stanzione — Laplacian pyramid frequency decomposition; "
            "(3) s125 Albani — vertical spatial gradient; "
            "(4) s126 Bartolommeo — Sobel edge-map modulation; "
            "(5) s127 Cantarini — spectral channel-selective diffusion; "
            "(6) s128 Carpaccio — local variance std map spatial adaptation; "
            "(7) s129 Piazzetta — global histogram percentile tonal sculpting.  "
            "Session 130 mode: IMAGE STRUCTURE TENSOR ANALYSIS.  The 2×2 structure "
            "tensor J at each pixel is built from integration-sigma-smoothed outer "
            "products of the image gradient [Gx, Gy].  Its eigenvalues λ1 ≥ λ2 "
            "encode local anisotropy: λ1≫λ2 at directional edges; λ1≈λ2≈0 in flat "
            "interior planes.  The coherence index c = ((λ1−λ2)/(λ1+λ2+ε))^p "
            "maps this to [0,1] — high where structure is directional (edges), "
            "low where it is isotropic (flat form interiors).  "
            "Interpolation: result = original·c + Gaussian_smooth·(1−c).  "
            "Edge pixels keep their original value (crisp boundary preserved).  "
            "Interior pixels receive the smooth, deeply rounded form surface.  "
            "A gentle R-channel warm tint (warm_tint_r) on the smooth fraction "
            "adds Venetian amber warmth to the deepened interior planes.  "
            "Use integration_sigma≈2.5, smooth_sigma≈4.0, opacity≈0.28–0.34."
        ),
    ),


    # ── Rosso Fiorentino ───────────────────────────────────────────────────────
    "rosso_fiorentino": ArtStyle(
        artist="Rosso Fiorentino",
        movement="Florentine Mannerism",
        nationality="Italian (Florentine)",
        period="1495–1540",
        palette=[
            (0.92, 0.88, 0.62),   # acid lemon-yellow highlight — jaundiced, not ivory
            (0.76, 0.72, 0.54),   # pale ash-gold mid-flesh — bleached cadaverous undertone
            (0.50, 0.56, 0.40),   # poison green-grey — characteristic Rosso shadow dissonance
            (0.26, 0.22, 0.14),   # deep cold umber — tense dark ground
            (0.70, 0.38, 0.28),   # hot vermilion accent — shock chromatic punctuation
            (0.48, 0.52, 0.62),   # cold blue-grey — steel drapery cool
            (0.62, 0.68, 0.38),   # acid olive-chartreuse — the signature Rosso dissonant green
        ],
        ground_color=(0.42, 0.42, 0.36),    # cool grey-olive imprimatura — tension before the first stroke
        stroke_size=5,
        wet_blend=0.22,                      # low — dissonant palette stays unresolved, not blended away
        edge_softness=0.20,                  # sharp, angular edges — electrified Mannerist definition
        jitter=0.032,                        # high chromatic jitter — every stroke slightly wrong
        glazing=None,                        # no unifying glaze — Rosso refuses tonal harmony
        crackle=True,
        chromatic_split=False,
        technique=(
            "Extreme Florentine Mannerism: acidic, dissonant palette of jaundiced "
            "yellows, cold bleached flesh, and poisonous green-grey shadows — colors "
            "that read as emotionally disturbing rather than beautiful.  Angular, "
            "electrified compositions with figures under existential stress.  "
            "Deliberately un-natural color relationships that encode psychological "
            "tension; Rosso rejected the harmonious Florentine ideal in favor of "
            "chromatic dissonance as expressive violence."
        ),
        famous_works=[
            ("Deposition from the Cross (Volterra)",    "1521"),
            ("Moses Defending the Daughters of Jethro", "1523"),
            ("Pietà",                                   "c. 1537"),
            ("Marriage of the Virgin",                  "1523"),
            ("Dead Christ with Angels",                 "c. 1524–1527"),
            ("Portrait of a Young Man",                 "c. 1518"),
            ("Adoration of the Magi",                   "1521"),
        ],
        inspiration=(
            "Apply rosso_chromatic_dissonance_pass() as the defining pass for "
            "session 131.  The pass encodes Rosso Fiorentino's defining quality: "
            "HUE-SELECTIVE CHROMATIC TENSION MAPPING — the ninth distinct processing "
            "mode in this pipeline.  "
            "Prior modes: (1) s123 Rosa — spatial displacement/flow warping; "
            "(2) s124 Stanzione — Laplacian pyramid frequency decomposition; "
            "(3) s125 Albani — vertical spatial gradient; "
            "(4) s126 Bartolommeo — Sobel edge-map modulation; "
            "(5) s127 Cantarini — spectral channel-selective diffusion; "
            "(6) s128 Carpaccio — local variance std map spatial adaptation; "
            "(7) s129 Piazzetta — global histogram percentile tonal sculpting; "
            "(8) s130 Sebastiano — image structure tensor coherence-driven smoothing.  "
            "Session 131 mode: HUE-SELECTIVE CHROMATIC TENSION MAPPING.  "
            "Algorithm: Convert the RGB canvas to HSV colour space.  "
            "(1) FLESH HUE TENSION: Identify pixels with warm flesh-hue (H ∈ [10°, 38°]) "
            "and moderate saturation (S > 0.12).  Rotate these hues by -hue_shift_flesh "
            "(toward cooler lemon-yellow, away from orange warmth) and reduce saturation "
            "by flesh_desat_amount — producing Rosso's characteristic bleached, "
            "near-cadaverous skin tone, wrong in a way that is unforgettable.  "
            "(2) SHADOW GREEN INJECTION: Identify mid-to-dark regions (V < shadow_v_thresh) "
            "and rotate their hue by +hue_shift_shadow toward the acidic green zone; "
            "slightly boost saturation — injecting Rosso's signature poison-green "
            "shadow dissonance.  "
            "(3) HIGHLIGHT ACID SHIFT: Identify bright highlights (V > highlight_v_thresh, "
            "S > 0.08) and rotate hue toward the acid-yellow quadrant (+hue_shift_highlight) "
            "— making highlights read jaundiced rather than warm-ivory, the key signature "
            "of Florentine acidic Mannerism.  "
            "Unlike all prior modes, this pass operates exclusively in HSV hue-space — "
            "not in spatial coordinates, not in frequency bands, not in luminance rank, "
            "not in edge gradients, not in spectral channels, not in local variance.  "
            "It is the first pipeline mode to manipulate HUE ANGLE DIRECTLY as a "
            "spatially-selective, value-conditional chromatic shift.  "
            "Use at opacity ≈ 0.22–0.30."
        ),
    ),


    # ── Dosso Dossi ────────────────────────────────────────────────────────────
    # ── Jacopo Bassano ────────────────────────────────────────────────────────
    "jacopo_bassano": ArtStyle(
        artist="Jacopo Bassano",
        movement="Venetian Pastoral Luminism",
        nationality="Italian (Venetian)",
        period="c. 1510–1592",
        palette=[
            (0.90, 0.74, 0.52),   # warm candlelit flesh — primary lit face in firelight
            (0.66, 0.50, 0.30),   # ochre-amber shadow flesh — deep warm earth half-tone
            (0.22, 0.16, 0.08),   # near-black umber void — Bassano's deep darkness
            (0.86, 0.64, 0.32),   # copper-gold — warm firelight highlight zone
            (0.42, 0.48, 0.36),   # muted sage-green — pastoral foliage, earthy distance
            (0.70, 0.66, 0.56),   # warm grey haze — atmospheric recession in landscape
            (0.38, 0.28, 0.18),   # dark chocolate umber — warm impasto shadow mass
        ],
        ground_color=(0.38, 0.28, 0.16),    # deep warm umber-brown ground — Bassano's dark base
        stroke_size=9,
        wet_blend=0.38,                      # moderate — impasto quality in darks, some fusion in lights
        edge_softness=0.44,                  # medium — firm chiaroscuro edges, soft in mid-transition
        jitter=0.034,                        # higher — Bassano's rough, expressive impasto texture
        glazing=(0.80, 0.60, 0.28),          # warm amber-copper glaze — firelight unification
        crackle=True,
        chromatic_split=False,
        technique=(
            "Jacopo Bassano (Jacopo da Ponte, c.1510–1592) transformed Venetian painting "
            "by combining the high-color tradition of Titian with a completely original "
            "focus on rustic pastoral life, dramatic artificial light, and vigorous impasto "
            "handling.  Born in the small market town of Bassano del Grappa north of Venice, "
            "he spent nearly his entire career there — an unusual choice that gave him "
            "freedom to develop an intensely personal vision outside the demands of the "
            "Serenissima's official culture.  "
            "His palette builds from a deep warm umber ground: shadows are rich, dark, and "
            "warm (burnt umber, raw sienna), while lights are applied with loaded brushes "
            "in thick, creamy impasto — warm ivory, bright ochre, and copper-gold accents "
            "for the zones caught by torchlight or firelight.  The transition from shadow "
            "to light is often abrupt, reflecting a pre-Caravaggesque understanding of "
            "artificial light as it carves form from darkness.  "
            "His later works (1570s–1580s) develop an extraordinarily loose, almost "
            "proto-Impressionist surface: forms dissolve into energetic marks that are more "
            "calligraphic than descriptive, anticipating Tintoretto's lightning impasto and "
            "prefiguring the bravura of later centuries.  El Greco, who likely passed "
            "through his workshop, absorbed both the dramatic lighting and the expressive "
            "brushwork.  "
            "Characteristic pastoral subjects — farm animals, peasants, shepherds, Nativity "
            "scenes set in farmyards — are rendered with unflinching naturalism and "
            "occasional surprising dignity."
        ),
        famous_works=[
            ("Rest on the Flight into Egypt",     "c. 1540"),
            ("Lazarus and the Rich Man",           "c. 1554"),
            ("The Adoration of the Magi",          "c. 1542"),
            ("Portrait of a Bearded Man",          "c. 1550"),
            ("The Baptism of Christ",              "c. 1590"),
            ("Animals Entering Noah's Ark",        "c. 1570"),
            ("St. John the Baptist in the Desert", "c. 1558"),
        ],
        inspiration=(
            "Apply bassano_pastoral_glow_pass() to encode Jacopo's defining quality: "
            "the luminous warmth of firelight and torchlight emerging from deep warm "
            "darkness.  This is the eleventh distinct processing mode in the pipeline: "
            "ANISOTROPIC DIFFUSION (Perona-Malik filter).  "
            "Prior modes: (1) s123 Rosa — spatial displacement; (2) s124 Stanzione — "
            "Laplacian pyramid; (3) s125 Albani — vertical gradient; (4) s126 Bartolommeo — "
            "Sobel edge-map; (5) s127 Cantarini — channel-selective diffusion; "
            "(6) s128 Carpaccio — local variance adaptation; (7) s129 Piazzetta — "
            "histogram percentile sculpting; (8) s130 Sebastiano — structure tensor; "
            "(9) s131 Rosso — hue-selective chromatic tension; (10) s132 Dosso — "
            "illumination-reflectance decomposition.  "
            "Session 133 mode: ANISOTROPIC DIFFUSION.  "
            "Algorithm: Perona-Malik anisotropic diffusion iteratively smooths flat "
            "tonal areas while PRESERVING edges — the conductance function c(s) = "
            "exp(-(s/K)²) approaches zero at luminance edges (high gradient) and 1.0 "
            "in flat tonal zones.  This creates Bassano's 'tonal pools' — smooth, "
            "luminous, beautifully graduated light zones — bounded by firm chiaroscuro "
            "edges that the diffusion refuses to cross.  "
            "After diffusion: a FIRELIGHT WARMTH BOOST applies a warm copper-amber tint "
            "proportional to pixel luminance — brighter pixels receive more warmth, "
            "simulating the orange-amber quality of torch and candlelight that saturates "
            "Bassano's highlights.  "
            "Use at opacity ≈ 0.28–0.36."
        ),
    ),

    # ── Aelbert Cuyp ──────────────────────────────────────────────────────────
    "aelbert_cuyp": ArtStyle(
        artist="Aelbert Cuyp",
        movement="Dutch Golden Age Luminism",
        nationality="Dutch",
        period="c. 1639–1672",
        palette=[
            (0.96, 0.84, 0.52),   # blazing amber-gold — Cuyp's signature afternoon sky light
            (0.88, 0.72, 0.38),   # warm ochre-gold — sunlit cattle hide, lit meadow grass
            (0.72, 0.60, 0.38),   # golden-sienna — rich warm mid-tone ground
            (0.52, 0.46, 0.62),   # cool blue-violet — distance and shadow depths
            (0.38, 0.46, 0.58),   # atmospheric blue-grey — cool sky and river glints
            (0.28, 0.30, 0.22),   # dark warm-green — shadow foliage, riverbank depth
            (0.92, 0.88, 0.70),   # pale ivory-gold — lit cloud and water highlight
            (0.64, 0.52, 0.30),   # raw umber warmth — cattle shadow, earth mid-tone
        ],
        ground_color=(0.68, 0.58, 0.38),    # warm amber-gold priming — the "Dutch Claude" ground
        stroke_size=7,
        wet_blend=0.68,                      # high — golden light merges and dissolves surfaces
        edge_softness=0.55,                  # moderate-soft — forms clear but edges dissolve in luminosity
        jitter=0.022,
        glazing=(0.90, 0.78, 0.42),          # radiant amber-gold glaze — Cuyp's defining atmosphere
        crackle=True,
        chromatic_split=False,
        technique=(
            "Aelbert Cuyp (1620–1691) is the supreme master of golden-hour light in "
            "Dutch painting — the painter who brought the warm Mediterranean luminosity "
            "of Claude Lorrain's Italian campagna into the flat polders and river meadows "
            "of the Dordrecht countryside.  His defining quality, so distinctive that he "
            "was nicknamed 'the Dutch Claude,' is an extraordinary amber-gold atmospheric "
            "luminosity that seems to dissolve fine spatial detail in brightly lit zones "
            "into a radiant golden field — forms that in shadow retain their structure "
            "but in bright light appear to merge with the glowing air around them.  "
            "This is not a failure of observation but a precise record of how human vision "
            "actually responds to very bright afternoon light: at high background luminance "
            "levels, the visual system's sensitivity to high spatial frequencies (fine "
            "texture, sharp edge detail) falls dramatically — a phenomenon now quantified "
            "as the luminance-dependent Contrast Sensitivity Function.  Cuyp observed and "
            "encoded this perceptual truth two centuries before it was measured.  "
            "His palette is built around a family of warm amber-golds: the sky, the lit "
            "surfaces of cattle, the gleaming river water, and the long afternoon grass "
            "all share the same warm luminous register — they dissolve into one another "
            "as the eye moves from one lit zone to another.  Shadow zones receive "
            "cool blue-violet accents (the sky reflected in the darkness), creating "
            "a powerful warm/cool contrast that makes the lights burn all the more "
            "intensely.  The ground tone — a warm amber imprimatura — reads through "
            "all thin paint passages, giving the entire canvas a warm tonal unity.  "
            "His brushwork in lit zones is smooth and barely visible; in shadow "
            "zones it becomes firmer and more structural.  The total effect is of "
            "landscape bathed in late-afternoon warmth — golden, still, and profound."
        ),
        famous_works=[
            ("A Herdsman with Cows by a River",        "c. 1650–1655"),
            ("The Maas at Dordrecht",                   "c. 1650"),
            ("Horsemen and Herdsmen with Cattle",       "c. 1655–1660"),
            ("The Large Dort (Dordrecht)",              "c. 1650–1665"),
            ("River Scene with a View of Dordrecht",   "c. 1660"),
            ("Young Herdsman with Cows",                "c. 1655"),
            ("Ubbergen Castle",                         "c. 1655"),
            ("Riders and Herdsmen with Cattle",        "c. 1658"),
        ],
        inspiration=(
            "Apply cuyp_golden_hour_pass() to encode Cuyp's defining quality: "
            "the radiant amber-gold afternoon luminosity that dissolves fine detail "
            "in bright zones while preserving structure in shadow areas.  "
            "This is the TWELFTH distinct processing mode in the pipeline: "
            "LUMINANCE-ADAPTIVE SPATIAL FREQUENCY ATTENUATION "
            "(Contrast Sensitivity Function simulation).  "
            "Prior modes: (1) s123 Rosa — spatial displacement; (2) s124 Stanzione — "
            "Laplacian pyramid; (3) s125 Albani — vertical gradient; (4) s126 Bartolommeo — "
            "Sobel edge-map; (5) s127 Cantarini — channel-selective diffusion; "
            "(6) s128 Carpaccio — local variance adaptation; (7) s129 Piazzetta — "
            "histogram percentile sculpting; (8) s130 Sebastiano — structure tensor; "
            "(9) s131 Rosso — hue-selective chromatic tension; (10) s132 Dosso — "
            "illumination-reflectance decomposition; (11) s133 Bassano — anisotropic diffusion.  "
            "Session 134 mode: LUMINANCE-ADAPTIVE SPATIAL FREQUENCY ATTENUATION.  "
            "Algorithm: (1) LUMINANCE COMPUTATION: L = 0.299R + 0.587G + 0.114B.  "
            "(2) GOLDEN WARMTH: Compute a warm-shifted version of the image: R += "
            "gold_warm_r × L² (quadratic so only brightest pixels get full warmth); "
            "G += gold_warm_g × L²; B -= gold_cool_b × L² (slight blue depletion).  "
            "(3) LUMINANCE-ADAPTIVE BLUR: For each pixel, the effective Gaussian sigma "
            "is sigma_base + sigma_scale × L² — bright pixels get much larger sigma "
            "(detail dissolves into the golden atmosphere); dark pixels get near-zero "
            "additional blur (structure preserved).  This is a SPATIALLY VARYING BLUR "
            "implemented via a weighted sum of several pre-computed Gaussian blur levels "
            "at different sigma values, blended proportionally to L² — a computationally "
            "tractable approximation of the ideal spatially-variant PSF.  "
            "(4) COMPOSITE: Blend the spatially-blurred golden version with the "
            "original at `opacity`.  The result: bright zones glow and dissolve into "
            "the warm golden atmosphere; shadow zones retain their form and cool structure.  "
            "Use at opacity ≈ 0.28–0.40."
        ),
    ),

    "dosso_dossi": ArtStyle(
        artist="Dosso Dossi",
        movement="Ferrarese Colorist Poesia",
        nationality="Italian (Ferrarese)",
        period="c. 1490–1542",
        palette=[
            (0.88, 0.72, 0.38),   # warm amber-gold — Dosso's defining illumination hue
            (0.76, 0.54, 0.32),   # rich ochre-sienna — warm mid-tone flesh
            (0.34, 0.46, 0.62),   # deep lapis-blue — jewel drapery cool
            (0.62, 0.42, 0.24),   # burnt umber-copper — dark warm ground
            (0.52, 0.68, 0.42),   # sage forest-green — poetic landscape foliage
            (0.78, 0.64, 0.52),   # pearl rose-tan — luminous skin highlight
            (0.22, 0.18, 0.28),   # deep cool indigo-black — atmospheric shadow depth
        ],
        ground_color=(0.48, 0.38, 0.26),    # warm umber-amber imprimatura — Ferrarese gold ground
        stroke_size=6,
        wet_blend=0.82,                      # high — jewel-like fused surfaces, no visible brushwork
        edge_softness=0.65,                  # Giorgionesque soft sfumato emergence from shadow
        jitter=0.012,                        # low — smooth, polished surfaces; Dosso was a careful technician
        glazing=(0.82, 0.65, 0.38),          # warm amber glaze — Ferrarese golden inner luminosity
        crackle=True,
        chromatic_split=False,
        technique=(
            "Ferrarese court painter of exceptional coloristic poetry.  Dosso Dossi "
            "(born Giovanni di Niccolò de Lutteri) absorbed the Giorgionesque sfumato "
            "and chromatic vision of the Venetian school — especially Giorgione and "
            "the young Titian — and combined it with a Ferrarese taste for rich, "
            "jewel-like color intensity and poetic mythological subjects.  His "
            "palette has a distinctive inner luminosity: colors read as if lit "
            "from within rather than from an external source — warm amber-golds, "
            "saturated lapus-blues, and glowing ochre flesh tones that seem to "
            "emit their own light.  The landscapes behind his figures dissolve "
            "into cool atmospheric poetry, with dense forest greens and golden "
            "sky-lit distances.  Surfaces are deeply glazed and richly fused."
        ),
        famous_works=[
            ("Circe and Her Lovers in a Landscape",    "c. 1514–1516"),
            ("Melissa",                                "c. 1516–1520"),
            ("Jupiter Painting Butterflies",           "c. 1523–1524"),
            ("Portrait of a Warrior",                  "c. 1510"),
            ("Allegory of Hercules",                   "c. 1535"),
            ("Saints John the Baptist and Bartholomew","c. 1520"),
            ("Lamentation of Christ",                  "c. 1527–1530"),
        ],
        inspiration=(
            "Apply dosso_luminance_reflectance_pass() as the defining pass for "
            "session 132.  The pass encodes Dosso Dossi's defining quality: the "
            "INNER LUMINOSITY of his jewel-like color — surfaces that seem to glow "
            "from within rather than being merely lit from outside.  "
            "This is the tenth distinct processing mode in the pipeline: "
            "ILLUMINATION-REFLECTANCE DECOMPOSITION (Retinex-inspired).  "
            "Prior modes: (1) s123 Rosa — spatial displacement/flow warping; "
            "(2) s124 Stanzione — Laplacian pyramid frequency decomposition; "
            "(3) s125 Albani — vertical spatial gradient; "
            "(4) s126 Bartolommeo — Sobel edge-map modulation; "
            "(5) s127 Cantarini — spectral channel-selective diffusion; "
            "(6) s128 Carpaccio — local variance std map spatial adaptation; "
            "(7) s129 Piazzetta — global histogram percentile tonal sculpting; "
            "(8) s130 Sebastiano — image structure tensor coherence-driven smoothing; "
            "(9) s131 Rosso — hue-selective chromatic tension mapping.  "
            "Session 132 mode: ILLUMINATION-REFLECTANCE DECOMPOSITION.  "
            "Algorithm: Treat the RGB image as L = I × R (illumination × reflectance).  "
            "In log space: log(L) = log(I) + log(R).  "
            "(1) ILLUMINATION ESTIMATION: For each channel, estimate illumination I "
            "as a strong Gaussian blur of the log-image (sigma_illum ≈ 60px).  "
            "(2) REFLECTANCE EXTRACTION: R = L / (I + eps) — the fine-grained "
            "color-and-detail layer, freed from the slow illumination envelope.  "
            "(3) REFLECTANCE SATURATION BOOST: In the reflectance layer, convert "
            "to HSV and boost saturation by sat_boost — this produces the jewel-like "
            "richness of Dosso's local colors without affecting the overall tonal key.  "
            "(4) ILLUMINATION WARMTH TINT: Add a warm amber tint to the illumination "
            "layer (slight positive shift on R and G channels, proportional to "
            "illum_warm_r, illum_warm_g) — simulating the warm Ferrarese ground "
            "luminosity that permeates Dosso's canvas.  "
            "(5) RECONSTRUCTION: Multiply the tinted illumination by the saturation-"
            "boosted reflectance.  Clamp to [0, 1] and composite at opacity.  "
            "Unlike all prior modes, this pass operates in LOG-DOMAIN ILLUMINATION/"
            "REFLECTANCE SPACE — the first pipeline mode to decompose the image into "
            "its physical illumination and surface-color components and manipulate "
            "each independently.  "
            "Use at opacity ≈ 0.28–0.38."
        ),
    ),

    # ── Moretto da Brescia ────────────────────────────────────────────────────
    "moretto_da_brescia": ArtStyle(
        artist="Moretto da Brescia",
        movement="Lombard Silver Classicism",
        nationality="Italian (Brescian)",
        period="c. 1498–1554",
        palette=[
            (0.90, 0.87, 0.82),   # pearl ivory-white — Moretto's defining cool skin highlight
            (0.78, 0.72, 0.68),   # silver-grey flesh — lit face midtone, cool and luminous
            (0.54, 0.50, 0.56),   # cool blue-grey — penumbra and half-shadow flesh
            (0.38, 0.36, 0.42),   # cool violet-shadow — deep face shadow, cool and clean
            (0.28, 0.32, 0.38),   # steel blue-dark — background drapery depth
            (0.62, 0.56, 0.50),   # warm umber mid — dark garment and hair
            (0.82, 0.78, 0.72),   # pale cool silver — lit collar, white lace, linen
            (0.44, 0.46, 0.52),   # atmospheric grey-blue — landscape distance, sky shadow
        ],
        ground_color=(0.62, 0.64, 0.66),    # cool silver-grey imprimatura — Lombard cool ground (B > R)
        stroke_size=5,
        wet_blend=0.58,                      # moderate-high — tones merge softly; clear form but no hard Gothic edges
        edge_softness=0.46,                  # moderate — soft but not Venetian-dissolved; Lombard structural presence
        jitter=0.010,                        # low — refined, controlled surface; Moretto was a careful technician
        glazing=(0.72, 0.70, 0.74),          # cool silver-lavender glaze — Lombard diffused overcast atmosphere
        crackle=True,
        chromatic_split=False,
        technique=(
            "Moretto da Brescia (Alessandro Bonvicino, c. 1498–1554) is the supreme "
            "master of the Lombard 'silver light' — a cool, pearlescent, diffused "
            "tonality utterly unlike the warm amber luminosity of the Venetian school.  "
            "Where Titian bathes his subjects in Mediterranean gold and Giorgione wraps "
            "them in smoky dusk, Moretto illuminates his figures with an overcast Brescian "
            "light: cool, even, and shadowless in the lit zones, with deep cool-violet "
            "shadow accents.  The result is a quality of extraordinary dignity and "
            "introspective calm — Moretto's sitters appear to exist in a world of perfect "
            "tonal quiet.  His palette is built around a family of cool pearl-grey and "
            "ivory tones: skin does not glow amber-warm but reads as silver-white; "
            "shadows are cool blue-violet rather than warm umber; and the overall tonal "
            "key is high and even — no dramatic dark masses or Caravaggesque voids.  "
            "His technique shows the influence of Raphael's tonal discipline fused with "
            "the Venetian command of glazed oil surfaces: surfaces are built up in "
            "multiple thin layers over a cool grey ground, giving a depth and luminosity "
            "that pure opaque application cannot achieve.  The glazing final pass is "
            "silver-lavender rather than amber — a colour temperature no other major "
            "Renaissance master habitually used.  Moretto was also the direct teacher "
            "and foremost influence on Giovanni Battista Moroni, whose uncompromising "
            "portrait realism grew directly from Moretto's cool-light objectivity."
        ),
        famous_works=[
            ("Portrait of a Young Man",                "c. 1525–1530"),
            ("Portrait of Count Fortunato Martinengo", "c. 1543"),
            ("Madonna and Child with Saints",          "c. 1524"),
            ("The Supper in the House of Simon",       "c. 1544"),
            ("Pietà",                                  "c. 1554"),
            ("Saint Justina with the Unicorn",         "c. 1530"),
            ("Portrait of a Lady",                     "c. 1540"),
            ("Elijah in the Wilderness",               "c. 1520–1525"),
        ],
        inspiration=(
            "Apply moretto_silver_luminance_pass() as the defining pass for "
            "session 136.  The pass encodes Moretto's defining optical quality: "
            "the LOMBARD SILVER LIGHT — a cool, pearlescent diffused tonality "
            "achieved by sculpting the image in CIE L*a*b* perceptual colour space.  "
            "This is the FOURTEENTH distinct processing mode in the pipeline: "
            "PERCEPTUAL COLOR SPACE SCULPTING (CIE L*a*b*).  "
            "Prior modes: (1) s123 Rosa — spatial displacement; (2) s124 Stanzione — "
            "Laplacian pyramid; (3) s125 Albani — vertical gradient; (4) s126 Bartolommeo — "
            "Sobel edge-map; (5) s127 Cantarini — channel-selective diffusion; "
            "(6) s128 Carpaccio — local variance adaptation; (7) s129 Piazzetta — "
            "histogram percentile sculpting; (8) s130 Sebastiano — structure tensor; "
            "(9) s131 Rosso — hue-selective chromatic tension; (10) s132 Dosso — "
            "illumination-reflectance decomposition; (11) s133 Bassano — anisotropic "
            "diffusion; (12) s134 Cuyp — luminance-adaptive CSF attenuation; "
            "(13) s135 Cranach — chromaticity/luminance decomposition.  "
            "Session 136 mode: PERCEPTUAL COLOR SPACE SCULPTING (CIE Lab).  "
            "Algorithm: (1) sRGB -> linear -> XYZ (D65) -> L*a*b*.  "
            "(2) L* MIDTONE LIFT: Gaussian bell at L*=55 lifts midtones by l_lift "
            "(high-key Lombard airiness).  (3) b* SILVER NEUTRALISATION: "
            "b_new = b * (1 - b_silver * (L/100)^2) -- depletes yellow-warmth "
            "in bright zones proportionally to L^2, giving silver-neutral highlights.  "
            "(4) a* COOL HIGHLIGHT DRIFT: in zones where L* > 70, a small negative "
            "a* shift models sky-reflected cool glint from pale skin.  "
            "(5) Lab -> XYZ -> sRGB.  This is the first pipeline mode to operate in "
            "perceptual Lab space -- all prior modes used linear RGB, HSV, log-domain, "
            "or PDE-based operations.  "
            "Also apply pearlescent_sfumato_pass() (session 136 artistic improvement): "
            "a structure-sensitive opalescent shimmer that adds pearlescent luminous depth "
            "to smooth gradient zones, modelling the scattering of light through "
            "multiple thin glaze layers.  Use at opacity ~0.26-0.34."
        ),
    ),

    # ── Parmigianino ──────────────────────────────────────────────────────────
    "parmigianino": ArtStyle(
        artist="Francesco Mazzola (Parmigianino)",
        movement="Italian Mannerism / Parma School",
        nationality="Italian",
        period="16th century (1503–1540)",
        palette=[
            (0.92, 0.87, 0.78),   # pearl ivory — luminous skin base, high-key warm
            (0.88, 0.88, 0.92),   # cool silver highlight — B > R, defining Parmigianino touch
            (0.76, 0.76, 0.80),   # cool neutral half-tone — pale lavender-grey mid-flesh
            (0.38, 0.32, 0.52),   # cool blue-lavender shadow — B > R > G, lum < 0.55 ✓
            (0.30, 0.18, 0.08),   # deep warm umber — shadow anchor depth
            (0.68, 0.22, 0.28),   # cold crimson — draped silk, cool saturated red
            (0.16, 0.20, 0.28),   # deep blue-green — costume / background depth
        ],
        ground_color=(0.66, 0.63, 0.60),    # neutral warm-grey — Parma panel (R-B = 0.06 ≤ 0.15)
        stroke_size=4,
        wet_blend=0.85,                      # heavy blending — imperceptible transitions
        edge_softness=0.68,                  # soft but legible — [0.50, 0.75] range
        jitter=0.008,                        # minimal — controlled, refined mark
        glazing=(0.84, 0.83, 0.82),          # cool pale ivory glaze — B ≥ R-0.05 ✓
        crackle=True,                        # aged panel paintings show characteristic crackle
        chromatic_split=False,
        technique=(
            "Francesco Mazzola, known as Parmigianino (1503–1540), embodied Italian "
            "Mannerism at its most refined and psychologically sophisticated.  His "
            "painting technique represents an extreme of sfumato-adjacent surface "
            "perfection: flesh surfaces are rendered with such seamless transitions "
            "that they read as polished porcelain or cool pearl, with absolutely no "
            "visible brushwork.  Unlike Leonardo's warm amber sfumato, Parmigianino "
            "cools his half-tones toward silver-lavender, creating a distinctive "
            "'mercury-cool' quality in skin modelling.  This technique required "
            "building the flesh up from a warm umber underpainting through successive "
            "thin glazes, each slightly cooler and more silvery toward the lights.  "
            "His palette is restrained: warm umber-amber in deep shadows, transitioning "
            "through cool blue-lavender in the penumbra, to the brilliant pearl-ivory "
            "of the highlight zone.  His most famous works demonstrate extreme "
            "elongation of the figure -- the neck and fingers are stretched far beyond "
            "natural proportion to achieve ideal Mannerist grace (serpentina figura).  "
            "This elongation is psychologically unsettling yet formally beautiful, "
            "creating figures that inhabit a rarefied ideal space outside ordinary "
            "human physiology."
        ),
        famous_works=[
            ("Madonna with the Long Neck",              "c. 1534–1540"),
            ("Self-Portrait in a Convex Mirror",        "1524"),
            ("Antea (Portrait of a Young Woman)",       "c. 1531–1535"),
            ("Portrait of a Young Man",                 "c. 1527"),
            ("The Vision of Saint Jerome",              "1527"),
            ("Moses",                                   "c. 1531"),
            ("Portrait of Galeazzo Sanvitale",          "1524"),
        ],
        inspiration=(
            "Apply parmigianino_serpentine_elegance_pass() as the core pipeline pass "
            "for Parmigianino's cool porcelain refinement (session 62).  "
            "Session 137 adds parmigianino_pearl_refinement_pass() — the FIFTEENTH "
            "distinct processing mode: LUMINANCE-CHROMINANCE DECOUPLED FILTERING.  "
            "Algorithm: Luma = 0.299R + 0.587G + 0.114B (perceptual weighting, "
            "unlike Cranach mode's mean-grey (R+G+B)/3); chroma residuals "
            "Cr = R-Luma, Cg = G-Luma, Cb = B-Luma; apply Gaussian sigma_chroma "
            "to each chroma channel (smooth colour zones); apply USM with "
            "sigma_luma/usm_amount to Luma (sharpen tonal structure); optionally "
            "shift Cb by +cool_tint (nudge penumbra toward cool lavender-pearl); "
            "reconstruct R_out = Luma_sharp + Cr_smooth; composite at opacity.  "
            "Session 137 also adds penumbra_cool_tint_pass() — zone-targeted cool "
            "tint in the penumbra band (shadow_lo=0.15 to shadow_hi=0.52), encoding "
            "the warm/cool split: warm highlights + cool ambient-scattered half-tones.  "
            "Distinct from Mode 13 (Cranach) in: (a) perceptual vs mean-grey axis; "
            "(b) DUAL mode -- different filters on luma vs chroma; "
            "(c) optional directional cool-pearl chroma tint.  "
            "Use pearl_refinement at opacity 0.28--0.38."
        ),
    ),

    "lucas_cranach": ArtStyle(
        artist="Lucas Cranach the Elder",
        movement="German Renaissance / Protestant Reformation",
        nationality="German (Saxony)",
        period="16th century (1472–1553)",
        palette=[
            (0.82, 0.14, 0.08),   # vermilion — intense pure red, court robes, symbolic blood
            (0.10, 0.28, 0.12),   # deep forest green — Germanic woodland, hunting backgrounds
            (0.06, 0.06, 0.06),   # jet black — costume, Lutheran gravity, contour definition
            (0.92, 0.85, 0.68),   # pearl ivory flesh — luminous skin, Venus and noble subjects
            (0.80, 0.68, 0.22),   # warm gold — ornamentation, Saxon court opulence
            (0.72, 0.72, 0.74),   # cool silver-grey — metalwork, armour, architectural detail
            (0.45, 0.25, 0.12),   # warm umber — background foliage shadow depth
            (0.95, 0.94, 0.90),   # near-white — sheer gauze veils, translucent fabric
        ],
        ground_color=(0.86, 0.78, 0.62),    # warm honey-ochre — Saxon court panel warmth
        stroke_size=4,
        wet_blend=0.20,                      # low — flat-applied paint, little blending
        edge_softness=0.14,                  # very firm — Gothic linear clarity
        jitter=0.005,                        # minimal — controlled, definite marks
        glazing=(0.80, 0.62, 0.32),          # warm amber glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Lucas Cranach the Elder (1472-1553), German (Saxony), was court painter "
            "to the Saxon Electors and close friend and visual propagandist for Martin "
            "Luther.  His painting style synthesizes Gothic German linear clarity with "
            "Italian Renaissance figuration, creating a distinctly Northern idiom.  "
            "Cranach's surfaces are enamel-flat: each colour area is applied in a "
            "single uniform tone with minimal gradation, giving his panels the jewel-"
            "like intensity of stained glass or illuminated manuscript pages.  His "
            "palette is among the most vivid and saturated of the Renaissance: pure "
            "vermilion, jet black, and brilliant gold dominate his court portraits; "
            "deep forest green and warm umber structure his hunting and landscape "
            "backgrounds.  Flesh tones are pale ivory-pearl with little tonal "
            "modelling -- faces are almost mask-like in their smooth, even surface, "
            "emphasising the Gothic idealization of his subjects.  His famous Venus "
            "series demonstrates mastery of flat, lustrous skin rendering against "
            "deep dark backgrounds, with each decorative detail (necklace, hat, veil) "
            "rendered with heraldic precision.  Cranach's outlines are definite and "
            "unambiguous -- the boundary between figure and ground is sharp and "
            "authoritative, in contrast to Italian sfumato."
        ),
        famous_works=[
            ("Venus Standing in a Landscape",     "1529"),
            ("Portrait of Martin Luther",          "1529"),
            ("Adam and Eve",                       "1526"),
            ("Portrait of a Lady",                 "1526"),
            ("Cardinal Albrecht of Brandenburg",   "1526"),
            ("Judith with the Head of Holofernes", "1530"),
            ("The Golden Age",                     "c. 1530"),
            ("Resting Diana on the Hunt",          "c. 1525"),
        ],
        inspiration=(
            "Apply cranach_enamel_clarity_pass() as the defining pass for "
            "session 135.  The pass encodes Cranach's defining optical quality: "
            "the jewel-like, enamel-flat COLOR PURITY of his panel surfaces -- "
            "colours that read at maximum chroma for their luminance level, with "
            "no grey contamination from blending or atmospheric dissolution.  "
            "This is the THIRTEENTH distinct processing mode in the pipeline: "
            "CHROMATICITY/LUMINANCE DECOMPOSITION (mean-achromatic separation "
            "with chroma boost and spatial pooling).  "
            "Prior modes: (1) s123 Rosa -- spatial displacement/flow warping; "
            "(2) s124 Stanzione -- Laplacian pyramid frequency decomposition; "
            "(3) s125 Albani -- vertical spatial gradient; "
            "(4) s126 Bartolommeo -- Sobel edge-map modulation; "
            "(5) s127 Cantarini -- spectral channel-selective diffusion; "
            "(6) s128 Carpaccio -- local variance std map spatial adaptation; "
            "(7) s129 Piazzetta -- global histogram percentile tonal sculpting; "
            "(8) s130 Sebastiano -- image structure tensor coherence-driven smoothing; "
            "(9) s131 Rosso -- hue-selective chromatic tension mapping (HSV space); "
            "(10) s132 Dosso -- illumination-reflectance decomposition (Retinex/log); "
            "(11) s133 Bassano -- anisotropic diffusion (Perona-Malik); "
            "(12) s134 Cuyp -- luminance-adaptive spatial frequency attenuation (CSF).  "
            "Session 135 mode: CHROMATICITY/LUMINANCE DECOMPOSITION.  "
            "Algorithm: grey = (R+G+B)/3; chromatic deviation cr = R-grey (sum=0); "
            "boost cr by (1+chroma_boost); optionally pool chroma spatially with "
            "Gaussian sigma_pool; reconstruct R_out = grey + cr_final.  Unlike HSV "
            "saturation (Mode 9, max-channel), this uses MEAN-CHANNEL grey as the "
            "achromatic axis -- geometrically distinct.  Use at opacity 0.28--0.38."
        ),
    ),

    # ── Giorgione ──────────────────────────────────────────────────────────────
    "giorgione": ArtStyle(
        artist="Giorgione (Giorgio da Castelfranco)",
        movement="Venetian High Renaissance / Poetic Tonalism",
        nationality="Italian",
        period="c. 1477–1510",
        palette=[
            (0.85, 0.68, 0.44),   # warm amber-ochre — glowing central light
            (0.72, 0.52, 0.30),   # raw sienna — deep warm mid-tone
            (0.28, 0.22, 0.14),   # warm umber shadow — rich, not cold
            (0.54, 0.62, 0.46),   # mysterious olive-green — Giorgione's arcadian backgrounds
            (0.45, 0.55, 0.64),   # atmospheric blue-grey — distant mountains in sfumato haze
            (0.62, 0.50, 0.36),   # golden-brown — the warm focal radiance at compositional center
            (0.82, 0.74, 0.58),   # warm ivory flesh — luminous, lit from within
            (0.30, 0.38, 0.46),   # deep blue-slate — storm sky, The Tempest atmosphere
        ],
        ground_color=(0.60, 0.48, 0.30),    # warm amber-brown imprimatura — Venetian glowing ground
        stroke_size=6,
        wet_blend=0.65,                      # high — tonal pools blend freely; pittura di macchia demands liquid flow
        edge_softness=0.78,                  # high-soft — forms dissolve into warm atmosphere; softer than Flemish, firmer than Leonardo
        jitter=0.018,
        glazing=(0.68, 0.54, 0.30),          # warm amber-golden unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Giorgione (Giorgio da Castelfranco, c. 1477-1510) was the founding "
            "master of Venetian tonal painting and the originator of the 'poesia' — "
            "a mode of painterly poetry that subordinated narrative to atmospheric "
            "mood and mysterious psychological interiority.  His surfaces are built "
            "from warm amber-golden imprimatura over which successive glazes of oil "
            "create a luminous depth that appears to glow from within.  Unlike "
            "Leonardo's cooler, more analytical sfumato, Giorgione's tonal "
            "transitions are warmer and more sensuous — forms emerge from pools of "
            "golden ambient light rather than from cool grey shadow.  His most "
            "distinctive quality is the FOCAL WARMTH RADIANCE: the compositional "
            "center of each painting is bathed in warm amber-golden light that "
            "gradually cools and desaturates toward the picture margins, creating "
            "an effect of intimate illumination within a mysterious larger world.  "
            "The Tempest (c. 1508) shows this quality perfectly: the central figures "
            "glow with warm internal light while the surrounding storm landscape "
            "recedes into cool atmospheric haze.  Only about six paintings are "
            "definitively attributed to Giorgione; his brief life (died of plague "
            "c. 1510) and enormous influence make each work a concentrated distillation "
            "of Venetian tonalist aesthetics.  Titian completed several of his "
            "unfinished canvases, and the boundary between late Giorgione and early "
            "Titian remains one of art history's most debated questions."
        ),
        famous_works=[
            ("The Tempest",                       "c. 1508"),
            ("Sleeping Venus",                    "c. 1510 (completed by Titian)"),
            ("Three Philosophers",                "c. 1508–1509"),
            ("Judith with the Head of Holofernes","c. 1504"),
            ("Portrait of a Young Man (Berlin)",  "c. 1506"),
            ("Laura",                             "1506"),
        ],
        inspiration=(
            "Apply giorgione_tonal_poetry_pass() as the defining pass for session 138.  "
            "This pass encodes Giorgione's poesia through LUMINANCE-ZONED DUAL-"
            "TEMPERATURE SCULPTING — the SIXTEENTH distinct processing mode in the "
            "pipeline.  Three luminance-responsive zones: (1) MIDTONE FOCAL WARMTH "
            "LIFT in [midtone_low, midtone_high] — warm amber luminous_lift applied "
            "via smooth sigmoid gate, brightening the glowing core tones; "
            "(2) SHADOW WARM TRANSITION — warm_shadow_strength amber tint in the "
            "deep-to-mid shadow zone where umber ground shows through thin glazes; "
            "(3) SILHOUETTE COOL EDGE ACCENT — cool_edge_strength tint at the figure "
            "boundary (figure_mask gradient), encoding Giorgione's cool atmospheric "
            "edge melt.  Together these three zones model his signature quality: "
            "warm glowing focal interior, cool mysterious silhouette boundary, warm "
            "amber shadow depth.  Also use giorgione_focal_warmth_pass() for the "
            "elliptical Gaussian spatial warmth radiance from focal centre.  "
            "Use luminous_lift=0.08, warm_shadow_strength=0.04, opacity=0.30."
        ),
    ),


    # ── Session 139 ─────────────────────────────────────────────────────────────
    "palma_vecchio": ArtStyle(
        artist="Palma Vecchio",
        movement="Venetian High Renaissance",
        nationality="Italian (Bergamasque/Venetian)",
        period="c. 1480–1528",
        palette=[
            (0.86, 0.74, 0.52),   # warm golden ivory flesh — the defining Palma tone
            (0.72, 0.52, 0.28),   # amber-ochre shadow — rich warm depth
            (0.52, 0.36, 0.20),   # warm umber — deep shadow on dark ground
            (0.78, 0.62, 0.44),   # golden midtone — the "blonde luminance" zone
            (0.42, 0.56, 0.70),   # cool blue-grey landscape — distant atmosphere
            (0.62, 0.24, 0.18),   # rich crimson drapery — jewel-tone costume accent
            (0.30, 0.44, 0.28),   # deep Venetian green — foliage, costume
            (0.88, 0.80, 0.62),   # pale golden sky — warm Venetian horizon haze
        ],
        ground_color=(0.56, 0.42, 0.24),    # warm amber-sienna imprimatura — Venetian glowing ground
        stroke_size=7,
        wet_blend=0.60,                      # high — Venetian oil softness; between Titian (0.72) and Giorgione (0.65)
        edge_softness=0.62,                  # moderate-high — softer than Titian, firmer than Giorgione; naturalistic warmth
        jitter=0.022,
        glazing=(0.72, 0.56, 0.28),          # warm amber-golden unifying glaze — the Palma signature warmth
        crackle=True,
        chromatic_split=False,
        technique=(
            "Palma Vecchio (Jacopo Palma, c. 1480-1528) was among the most gifted "
            "of the Venetian High Renaissance painters working in the orbit of "
            "Titian and Giorgione.  Born in Serina near Bergamo, he arrived in Venice "
            "around 1500 and rapidly absorbed the new Venetian oil technique of warm "
            "amber imprimatura overlaid with successive glazes.  Palma is above all "
            "the painter of BLONDE LUMINANCE — his portraits and sacra conversazione "
            "altarpieces are saturated with a warm golden light that emanates from "
            "flesh, hair, and drapery alike.  Where Giorgione's tonalism is cool and "
            "mysterious, and Titian's colorism is rich and saturated, Palma's "
            "distinctive quality is a warm, golden, almost honeyed naturalism — a "
            "daylit warmth that makes his surfaces seem to glow with internal amber "
            "light.  His flesh tones build from a warm amber imprimatura through golden "
            "midtones to luminous ivory highlights, with almost no cool undertone — "
            "the entire scale is warm.  His most famous works are the half-length "
            "portraits of beautiful blonde women (La Bella, Violante, the various "
            "'Portrait of a Young Woman' canvases) where his golden luminance is "
            "most concentrated.  He died young (c. 48), leaving many works unfinished; "
            "Titian and others completed several of his final commissions.  His "
            "influence on Venetian portraiture was considerable, particularly in "
            "establishing the half-length beauty portrait as a distinct genre."
        ),
        famous_works=[
            ("Three Sisters (Three Graces)",      "c. 1520"),
            ("Sacra Conversazione",               "c. 1522"),
            ("Portrait of a Young Woman (Flora)", "c. 1520"),
            ("Violante",                          "c. 1514–1520 (attrib.)"),
            ("Adam and Eve",                      "c. 1510"),
            ("St Barbara",                        "1522–1524"),
        ],
        inspiration=(
            "Apply palma_blonde_luminance_pass() as the defining pass for session 139.  "
            "This pass encodes Palma Vecchio's GOLDEN BLONDE LUMINANCE through "
            "LUMINANCE-ZONED WARM BLOOM SCULPTING — the SEVENTEENTH distinct processing "
            "mode in the pipeline.  A Gaussian-shaped luminance gate centred on the "
            "warm midtone zone (centre≈0.60, sigma≈0.22) selectively applies warm "
            "golden tint (warm_r lift on red channel, warm_g lift on green channel) "
            "in the mid-to-high luminance zone where Palma's characteristic blonde "
            "luminance lives — the golden flesh, the luminous hair, the sun-touched "
            "drapery.  Deep shadows and near-white highlights are excluded by the "
            "Gaussian gate, preserving tonal structure.  The result is Palma's "
            "defining quality: a warm golden inner glow radiating from the luminous "
            "midtone zone, distinguishable from Giorgione's cooler atmospheric "
            "tonalism and from Titian's saturated colorism.  "
            "Use luminance_centre=0.60, luminance_sigma=0.22, warm_r=0.08, "
            "warm_g=0.04, opacity=0.32."
        ),
    ),

    # ── Francesco del Cossa ───────────────────────────────────────────────────
    "cossa": ArtStyle(
        artist="Francesco del Cossa",
        movement="Ferrarese Renaissance",
        nationality="Italian",
        period="c. 1436–1478",
        palette=[
            (0.88, 0.22, 0.12),   # vermilion red — bold Ferrarese drapery signature
            (0.22, 0.42, 0.78),   # brilliant azure — deep ultramarine sky and costume
            (0.86, 0.72, 0.20),   # gold ochre — gilded ornamental warmth
            (0.24, 0.58, 0.32),   # malachite emerald — cool drapery counterpoint
            (0.90, 0.83, 0.68),   # warm ivory flesh — pale, sculptural Ferrarese skin
            (0.52, 0.36, 0.16),   # warm umber — directional shadow modeling
            (0.76, 0.66, 0.50),   # amber mid-flesh — secondary skin tone
        ],
        ground_color=(0.72, 0.62, 0.44),    # warm amber-ochre imprimatura
        stroke_size=6,
        wet_blend=0.35,                      # relatively dry — crisp zone boundaries
        edge_softness=0.22,                  # hard Ferrarese contours; no sfumato
        jitter=0.025,
        glazing=None,                         # no unifying glaze — clean discrete zones
        crackle=True,
        chromatic_split=False,
        technique=(
            "Francesco del Cossa was the greatest painter of the Ferrarese school "
            "and one of the most distinctively individual voices of the entire "
            "Italian quattrocento.  Born in Ferrara around 1436, he reached maturity "
            "under the patronage of the Este court and produced his masterwork — the "
            "frescoes of the Sala dei Mesi (Hall of the Months) in the Palazzo "
            "Schifanoia (1469–70) — a panoramic allegory of courtly life, zodiac "
            "symbolism, and seasonal labour that stands as the supreme example of "
            "the Este courtly style.  "
            "Cossa's technique is immediately recognisable by what it refuses to do: "
            "there is no sfumato, no soft atmospheric haze, no blended edge that "
            "dissolves form into background.  Instead every figure is bounded by a "
            "firm, confident contour — the line of a trained draughtsman who thought "
            "in sculptural terms — and every colour zone is laid in with a clean, "
            "jewel-like application that appears to have been fired rather than "
            "painted.  This quality is often described as ENAMEL CLARITY: the "
            "surface of a Cossa painting glows with an almost mineral luminescence, "
            "as if the pigments were transparent stones — lapis lazuli blue, "
            "malachite green, vermilion red — set between firm contours of dark umber "
            "in the manner of a cloisonné enamel or illuminated manuscript.  "
            "His palette is one of the most distinctive in Renaissance painting: "
            "brilliant vermilion reds for drapery, saturated azure blues (Ferrarese "
            "painters had privileged access to high-quality ultramarine through Este "
            "trade connections), warm gold ochres, and the pale ivory flesh tones "
            "that give his figures their sculptural, almost stone-carved quality.  "
            "Shadows are modelled with warm umber in tight, controlled transitions — "
            "not the deep tenebrism of later Baroque masters but a quattrocento "
            "structural shading that reads as relief carving rather than atmospheric "
            "depth.  "
            "Cossa moved to Bologna in 1470, partly in response to what he felt was "
            "inadequate payment from Borso d'Este for the Schifanoia frescoes — a "
            "letter he wrote complaining about this survives as an extraordinary "
            "document of Renaissance artist self-assertion — and in Bologna produced "
            "his altarpieces, including the San Vincenzo Ferrer polyptych (1473), "
            "which show his mature style: more monumental than the frescoes, with "
            "figures that inhabit a fully three-dimensional pictorial space while "
            "retaining the hard chromatic clarity that distinguishes him from his "
            "more atmospheric contemporaries.  "
            "The enamel quality is achieved technically through a warm amber "
            "imprimatura, relatively dry paint application (little wet-on-wet blending), "
            "and careful restraint with edge softening — each colour is allowed to "
            "declare itself fully before the adjacent zone begins."
        ),
        famous_works=[
            ("Palazzo Schifanoia — Sala dei Mesi (March panel)", "1469–70"),
            ("Palazzo Schifanoia — Sala dei Mesi (April panel)",  "1469–70"),
            ("San Vincenzo Ferrer polyptych",                    "1473"),
            ("Griffin Altarpiece",                               "c. 1472–73"),
            ("St John the Baptist",                              "c. 1473"),
            ("Annunciation",                                     "c. 1470–72"),
        ],
        inspiration=(
            "Use cossa_enamel_structure_pass() after build_form() to apply Cossa's "
            "defining GEM-ENAMEL CLARITY: a chroma boost in the mid-luminance gem zone "
            "that intensifies colour zone purity, followed by an unsharp mask that "
            "reinforces structural contour clarity (the 'hard edge' of Ferrarese "
            "quattrocento painting).  "
            "edge_softness=0.22 enforces Cossa's crisp zone boundaries — the opposite "
            "of sfumato.  wet_blend=0.35 keeps colour zones distinct and prevents the "
            "soft wet-into-wet blending of Venetian contemporaries.  "
            "ground_color=(0.72, 0.62, 0.44) — warm amber-ochre imprimatura that "
            "gives the Ferrarese school its characteristic glowing warmth beneath "
            "the cool enamel surface colours.  "
            "Use chroma_boost=0.18, structure_strength=0.22, opacity=0.36."
        ),
    ),

    # ── Session 141 ───────────────────────────────────────────────────────────
    "crivelli": ArtStyle(
        artist      = "Carlo Crivelli",
        movement    = "Venetian Late Gothic / International Gothic",
        nationality = "Italian",
        period      = "c. 1430–1495",
        palette     = [
            (0.82, 0.64, 0.18),   # gold leaf — burnished gilt
            (0.72, 0.14, 0.18),   # vermilion — sharp crimson
            (0.18, 0.38, 0.72),   # lapis ultramarine — cool jewel blue
            (0.22, 0.52, 0.28),   # malachite green — translucent emerald
            (0.94, 0.88, 0.72),   # ivory — pale flesh, near-white highlights
            (0.44, 0.22, 0.12),   # warm umber — deep brown ground
            (0.88, 0.76, 0.44),   # amber gold — secondary gilt mid-tone
        ],
        ground_color  = (0.58, 0.48, 0.28),   # warm ochre-gold imprimatura
        stroke_size   = 5,
        wet_blend     = 0.20,     # very dry — crisp zone separation
        edge_softness = 0.10,     # hard Gothic contours — no sfumato whatsoever
        jitter        = 0.018,
        glazing       = None,     # clean zone separation, no unifying glaze
        crackle       = True,
        chromatic_split = False,
        technique     = (
            "Carlo Crivelli (c. 1430–1495) was a Venetian-trained painter who spent "
            "almost his entire career in the Marche region of Italy, producing devotional "
            "altarpieces of extraordinary decorative intensity. His style is among the "
            "most distinctive in all Italian art: a singular fusion of Byzantine "
            "gold-ground tradition, International Gothic linear precision, and nascent "
            "Renaissance spatial awareness.  "
            "Crivelli's forms are obsessively linear — every contour is a hard, crisp "
            "edge drawn with almost metallic clarity. There is absolutely no sfumato, no "
            "atmospheric dissolution, no soft transition between tones. The figures occupy "
            "architectural niches and landscape settings of nail-sharp precision, every "
            "stone and leaf in hard focus regardless of distance.  "
            "His most famous signature is the suspension of real objects — cucumbers, "
            "apples, pears, gourds, swags of fruit — in the picture space as if they "
            "could be physically plucked. These are rendered with an almost hallucinatory "
            "realism that contrasts violently with the gold-leaf backgrounds and hieratic "
            "figures, producing an effect that is simultaneously devotional and bizarre.  "
            "The palette is electrifying: vermilion of extraordinary sharpness, "
            "ultramarine of saturated depth, malachite green of translucent brilliance, "
            "and above all gold. Not merely golden paint, but actual burnished gold leaf "
            "applied to halos, brocade vestments, and architectural ornament. This gold "
            "catches light in a purely specular way — a hard, brilliant flash unlike any "
            "painted surface. The crivelli_gold_leaf_pass() captures this effect.  "
            "His flesh tones are cool and porcelain-pale, modelled with fine tempera "
            "hatching rather than wet blending. Drapery is treated as formal, almost "
            "abstract pattern — crisp ridges and valleys of cloth read as decorative "
            "geometry rather than naturalistic fabric. This is pure International Gothic "
            "stylisation elevated to an extreme of refinement.  "
            "Technically, Crivelli worked in egg tempera on gold-ground panel — a medium "
            "that enforces precision and penalises wet blending. edge_softness=0.10 "
            "encodes the absolute hardness of his Gothic contours. wet_blend=0.20 keeps "
            "colour zones perfectly discrete. The crivelli_gold_leaf_pass() simulates the "
            "specular highlight behaviour of burnished gold leaf: a hard power-curve spike "
            "in the brightest luminance zone only, leaving mid-tones and shadows "
            "untouched."
        ),
        famous_works = [
            ("The Annunciation with Saint Emidius",         "1486"),
            ("Pietà",                                        "c. 1470"),
            ("Virgin and Child Enthroned with Saints",       "c. 1476"),
            ("The Dead Christ Supported by Two Angels",      "c. 1470"),
            ("Demidoff Altarpiece",                          "1476"),
            ("Madonna della Rondine",                        "c. 1490–92"),
        ],
        inspiration   = (
            "Use crivelli_gold_leaf_pass() after build_form() to apply Crivelli's "
            "defining GILT SPECULAR BRILLIANCE: a power-curve highlight gilding that "
            "simulates the way burnished gold leaf fires a hard specular spike only in "
            "the top luminance percentile.  "
            "edge_softness=0.10 enforces Crivelli's absolute Gothic contour hardness — "
            "sharper even than Cossa's already-firm enamel edges. wet_blend=0.20 keeps "
            "colour zones perfectly discrete, honouring tempera panel tradition.  "
            "ground_color=(0.58, 0.48, 0.28) — warm ochre-gold imprimatura appropriate "
            "to the gold-ground panel tradition.  "
            "Use gilt_thresh=0.72, gilt_power=2.2, gold_r=0.22, gold_g=0.12, "
            "gold_b_damp=0.06, opacity=0.38."
        ),
    ),

    # ── Filippino Lippi ────────────────────────────────────────────────────────
    "filippino_lippi": ArtStyle(
        artist="Filippino Lippi",
        movement="Late Florentine Quattrocento",
        nationality="Italian",
        period="1457–1504",
        palette=[
            (0.82, 0.64, 0.52),   # warm rose flesh
            (0.82, 0.22, 0.12),   # hot vermilion drapery
            (0.68, 0.74, 0.28),   # acid yellow-green dissonance
            (0.32, 0.24, 0.45),   # cobalt-violet shadow
            (0.78, 0.65, 0.22),   # warm gold ochre
            (0.52, 0.55, 0.60),   # blue-grey aerial distance
            (0.88, 0.82, 0.68),   # pale ivory highlight
        ],
        ground_color=(0.55, 0.44, 0.32),
        stroke_size=5,
        wet_blend=0.40,
        edge_softness=0.32,
        jitter=0.028,
        glazing=None,
        crackle=True,
        chromatic_split=False,
        technique=(
            "Filippino Lippi (c. 1457–1504) occupies an extraordinary position in "
            "Florentine painting: son of Fra Filippo Lippi, pupil of Botticelli, and "
            "the artist who completed Masaccio's Brancacci Chapel frescoes.  In his "
            "mature work, beginning with the Strozzi Chapel frescoes at Santa Maria "
            "Novella (c. 1489–1502), he transforms the quattrocento inheritance "
            "into something unmistakably his own: a turbulent, nervous energy charged "
            "with anxious vitality.  His drapery does not fall in serene classical arcs "
            "but torques and billows in complex surfaces of light and shadow.  "
            "His palette uses COLOR AS TENSION: vivid vermilion against acid "
            "yellow-green, warm rose flesh against cool violet-blue shadow, gold ochre "
            "against stone-grey architecture.  Adjacent zones do not harmonise — "
            "they argue, push against each other with restless chromatic energy.  "
            "His devotion to antiquity shows in dense archaeological decoration: the "
            "Strozzi and Carafa Chapel frescoes are dense with antique trophies, "
            "candelabra, putti, and relief panels.  Technically his oil technique "
            "shares the warm imprimatura of Florentine practice but his paint "
            "application is more direct than Leonardo's — colour zones stay "
            "vivid rather than sfumato-dissolving, trembling with chromatic potential."
        ),
        famous_works=[
            ("Strozzi Chapel frescoes, Santa Maria Novella",       "c. 1489–1502"),
            ("Carafa Chapel frescoes, Santa Maria sopra Minerva",   "1488–1493"),
            ("Vision of St Bernard, Badia Fiorentina",             "c. 1485–1487"),
            ("Adoration of the Magi, Uffizi",                      "1496"),
            ("Brancacci Chapel — completion of Masaccio cycle", "c. 1481–1482"),
        ],
        inspiration=(
            "Use filippino_tension_pass() after build_form() to apply Filippino's "
            "SATURATION-GATED HUE ROTATION: in HSV space, the most chromatic pixels "
            "receive a gentle hue rotation, pushing vivid zones further apart and "
            "creating the subtle color-tension that makes adjacent zones argue rather "
            "than harmonise.  Saturation is also slightly boosted in those zones.  "
            "edge_softness=0.32 preserves Florentine disegno — firm contours — "
            "without Gothic hardness.  wet_blend=0.40 keeps zones distinct while "
            "allowing soft mid-tone transitions.  "
            "ground_color=(0.55, 0.44, 0.32) — warm terracotta imprimatura.  "
            "Use sat_thresh=0.25, sat_power=1.5, hue_shift=0.04, "
            "sat_boost=0.18, opacity=0.30."
        ),
    ),


    # ── Alessandro Magnasco (il Lissandrino) ───────────────────────────────────
    "magnasco": ArtStyle(
        artist="Alessandro Magnasco",
        movement="Genoese Dark Baroque",
        nationality="Italian (Genoese)",
        period="1667–1749",
        palette=[
            (0.08, 0.06, 0.04),   # near-black umber void
            (0.22, 0.15, 0.08),   # dark warm shadow
            (0.82, 0.68, 0.38),   # amber-golden impasto highlight
            (0.72, 0.56, 0.32),   # warm mid-tone flicker
            (0.35, 0.28, 0.18),   # dark ochre mid-shadow
            (0.58, 0.45, 0.25),   # warm sienna accent
            (0.88, 0.82, 0.65),   # pale silver-gold peak highlight
        ],
        ground_color=(0.10, 0.07, 0.04),    # near-black umber ground
        stroke_size=4,
        wet_blend=0.12,                      # dry rapid marks — not blended
        edge_softness=0.18,                  # firm edges — nervous, graphic
        jitter=0.07,                         # high per-stroke variation
        glazing=(0.40, 0.28, 0.10),          # dark amber unifying glaze
        crackle=True,
        chromatic_split=False,
        technique=(
            "Nervous flickering highlights on near-black umber grounds — rapid "
            "impasto marks placed with fierce gestural energy; figures and "
            "environments emerge from near-total darkness via scattered warm "
            "amber-gold highlight touches applied with a loaded, quickened brush. "
            "Magnasco's surfaces feel perpetually in motion: nothing rests, "
            "every mark vibrates with expressive urgency."
        ),
        famous_works=[
            ("The Last Supper",                          "c. 1720"),
            ("Refectory of the Monks",                   "c. 1730"),
            ("Massacre of the Innocents",                "c. 1700"),
            ("Landscape with Brigands",                  "c. 1725"),
            ("St John the Baptist Preaching",            "c. 1710"),
        ],
        inspiration=(
            "Use magnasco_nervous_brilliance_pass() after build_form() to apply "
            "Magnasco's SPATIAL-SCATTER HIGH-FREQUENCY LUMINANCE REVIVAL: "
            "extract bright high-frequency surface peaks via positive unsharp "
            "mask, then scatter multiple shifted copies of these highlight marks "
            "across the dark ground using controlled random roll offsets "
            "(±scatter_px px), gated by luminance so the effect concentrates in "
            "dark and mid-dark tonal zones (where Magnasco inserts his nervous "
            "amber-gold flickers).  Warm-tint the scattered peaks slightly "
            "(warm_tint ~0.05) for the candlelight quality of his impasto.  "
            "Parameters: hf_sigma=2.5, scatter_px=3, bright_thresh=0.04, "
            "dark_gate_lo=0.10, dark_gate_hi=0.65, warm_tint=0.05, opacity=0.30."
        ),
    ),

}


def get_style(key: str) -> ArtStyle:
    """
    Return an ArtStyle by artist key.

    >>> s = get_style("seurat")
    >>> s.chromatic_split
    True
    """
    k = key.lower().replace(" ", "_").replace("-", "_")
    if k not in CATALOG:
        available = ", ".join(sorted(CATALOG.keys()))
        raise KeyError(f"Unknown style key {key!r}. Available: {available}")
    return CATALOG[k]


def list_artists() -> List[str]:
    """Return all available artist keys."""
    return sorted(CATALOG.keys())


def palette_for(key: str) -> List[Color]:
    """Return the palette colours for a given artist key."""
    return get_style(key).palette
