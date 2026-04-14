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
