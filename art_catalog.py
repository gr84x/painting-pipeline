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
