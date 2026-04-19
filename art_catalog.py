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
