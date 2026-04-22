"""
scene_schema.py — Structured scene description.

This is the intermediate representation between a text prompt and any
renderer (Blender, pycairo, stroke engine). All builders consume Scene
objects; none of them parse text directly.

Design goals:
  - Blender-compatible: every concept maps to a Blender object/property
  - Renderer-agnostic: nothing cairo- or Blender-specific in this file
  - Composable: scenes can be assembled programmatically or from prompts
  - 3D-native: all positions/directions are Vec3; 2D is a projection choice

Usage:
  scene = Scene(
      subjects=[
          Character(
              archetype=Archetype.HUMAN,
              build=Build.AVERAGE,
              pose=Pose.SEATED,
              facing=Vec3(0, 0, 1),
              expression=Expression.NEUTRAL,
              costume=Costume(top="dark robe", palette=PaletteHint.DARK_EARTH),
          )
      ],
      camera=Camera(position=Vec3(0, 1.6, 3.5), target=Vec3(0, 1.2, 0), fov=35),
      lighting=LightRig.THREE_POINT_WARM,
      environment=Environment(type=EnvType.INTERIOR, atmosphere=0.0),
      style=Style(medium=Medium.OIL, period=Period.RENAISSANCE, palette=PaletteHint.WARM_EARTH),
  )
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple

from cartoon_morphology import CartoonMorphology


# ─────────────────────────────────────────────────────────────────────────────
# Primitives
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Vec3:
    """3D vector/point. All world positions and directions use this."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __add__(self, other: Vec3) -> Vec3:
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, s: float) -> Vec3:
        return Vec3(self.x * s, self.y * s, self.z * s)

    def normalized(self) -> Vec3:
        import math
        mag = math.sqrt(self.x**2 + self.y**2 + self.z**2) or 1e-9
        return Vec3(self.x / mag, self.y / mag, self.z / mag)


# RGB in [0, 1]
Color = Tuple[float, float, float]


def hex_color(h: str) -> Color:
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return r / 255.0, g / 255.0, b / 255.0


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class Archetype(Enum):
    """Subject type — drives anatomy system selection."""
    HUMAN       = auto()
    HUMANOID    = auto()   # elvish, orcish, etc. — human base with modifications
    QUADRUPED   = auto()   # horses, wolves, big cats
    BIRD        = auto()
    REPTILE     = auto()
    INSECT      = auto()
    FISH        = auto()
    FANTASY     = auto()   # dragons, centaurs — composite anatomy
    ABSTRACT    = auto()   # non-figurative subjects


class Build(Enum):
    """Body build / silhouette."""
    SLIGHT    = auto()
    AVERAGE   = auto()
    ATHLETIC  = auto()
    STOCKY    = auto()
    HEAVY     = auto()


class Sex(Enum):
    UNSPECIFIED = auto()
    FEMALE      = auto()
    MALE        = auto()
    ANDROGYNOUS = auto()


class AgeRange(Enum):
    CHILD    = auto()   # 4–12
    TEEN     = auto()   # 13–18
    YOUNG    = auto()   # 19–30
    ADULT    = auto()   # 31–55
    ELDER    = auto()   # 56+


class Pose(Enum):
    """Broad pose category; fine-tuned via PoseDetail."""
    STANDING       = auto()
    SEATED         = auto()
    CROUCHING      = auto()
    RECLINING      = auto()
    WALKING        = auto()
    RUNNING        = auto()
    FIGHTING       = auto()
    FLYING         = auto()
    CUSTOM         = auto()   # use PoseDetail.joints


class Expression(Enum):
    NEUTRAL    = auto()
    SMILING    = auto()
    ENIGMATIC  = auto()   # subtle, ambiguous
    PENSIVE    = auto()
    STERN      = auto()
    FEARFUL    = auto()
    JOYFUL     = auto()
    SORROWFUL  = auto()
    ANGRY      = auto()


class SkinTone(Enum):
    FAIR        = auto()
    LIGHT       = auto()
    MEDIUM      = auto()
    OLIVE       = auto()
    TAN         = auto()
    BROWN       = auto()
    DEEP        = auto()


class HairStyle(Enum):
    SHORT       = auto()
    MEDIUM      = auto()
    LONG        = auto()
    CURLY       = auto()
    BRAIDED     = auto()
    BALD        = auto()
    VEILED      = auto()


class EnvType(Enum):
    INTERIOR    = auto()
    EXTERIOR    = auto()
    LANDSCAPE   = auto()
    ABSTRACT    = auto()


class Medium(Enum):
    OIL         = auto()
    WATERCOLOR  = auto()
    INK_WASH    = auto()
    CHARCOAL    = auto()
    GOUACHE     = auto()
    DIGITAL     = auto()


class Period(Enum):
    RENAISSANCE   = auto()
    BAROQUE       = auto()
    IMPRESSIONIST = auto()
    EXPRESSIONIST = auto()
    POINTILLIST   = auto()   # Seurat / divisionism — dots, no wet blending
    ROMANTIC      = auto()   # Turner — luminous light vortex, dissolved edges
    ART_NOUVEAU   = auto()   # Klimt — gold leaf, flat ornament, symbolic colour
    UKIYO_E       = auto()   # Hokusai — flat colour, bokashi gradient, ink contours
    PROTO_EXPRESSIONIST = auto()  # Goya — black void, crude urgency, darkness as subject
    REALIST       = auto()   # Manet — flat value planes, bold black, cool silver half-tones
    VIENNESE_EXPRESSIONIST = auto()  # Schiele — angular contour, flat muted void, psychological rawness
    COLOR_FIELD   = auto()   # Rothko — luminous horizontal bands, optical vibration, absorbing void
    SYNTHETIST    = auto()   # Gauguin — flat colour zones, dark cloisonné contour lines, tropical palette
    MANNERIST     = auto()   # El Greco — elongated figures, jewel-tone palette, inner-lit silver flesh
    SURREALIST    = auto()   # Kahlo — flat folk-art zones, intense saturated palette, dark contour outlines
    ABSTRACT_EXPRESSIONIST = auto()  # Kandinsky — geometric resonance, synesthetic colour theory, floating primitives
    VENETIAN_RENAISSANCE = auto()  # Titian — rich colourism, warm glazing, gestural impasto, luminous depth
    VENETIAN_HIGH_RENAISSANCE = auto()  # Giorgione — tonal poetry, luminous midtone pooling, warm-cool atmospheric transition, proto-sfumato
    EARLY_VENETIAN_RENAISSANCE = auto()  # Bellini — crystalline sacred light, honey-amber glazing, serene divine luminosity
    FAUVIST       = auto()   # Matisse — maximum saturation, flat zones, complementary shadows, coloured outlines
    PRIMITIVIST   = auto()   # Modigliani — oval mask faces, almond eyes, elongated necks, warm ochre flesh
    EARLY_NETHERLANDISH = auto()  # Jan van Eyck — stacked transparent oil glazes, chalk-white gesso, Flemish micro-detail
    ART_DECO      = auto()   # Tamara de Lempicka — smooth cubist facets, metallic gloss, bold saturated palette
    NABIS         = auto()   # Vuillard / Bonnard — intimate pattern-ground fusion, flat muted zones, figures absorbed into patterned grounds
    LUMINISMO     = auto()   # Sorolla — maximum sunlight, warm/cool simultaneous contrast, dappled light pools
    HIGH_RENAISSANCE = auto()  # Raphael — luminous clarity, radiant warm midtones, idealized form, no heavy sfumato
    EARLY_ITALIAN_RENAISSANCE = auto()  # Piero della Francesca — cool mineral palette, geometric clarity, diffuse crystalline light
    TENEBRIST     = auto()   # Zurbarán — near-black void, hyper-real white fabric, razor-sharp found edges
    NEOCLASSICAL  = auto()   # Ingres — porcelain-smooth flesh, cool pearl highlights, precise classical line
    NOCTURNE      = auto()   # La Tour — single candle, warm amber radial glow, near-black void, simplified serene forms
    FRENCH_NATURALIST = auto()  # Chardin — granular powdery surface, warm grey palette, soft domestic intimacy
    SOCIAL_REALIST = auto()    # Courbet — palette knife planes, dark earthy ground, unidealized impasto
    ACADEMIC_REALIST = auto()  # Bouguereau — porcelain-smooth flesh, imperceptible blending, warm golden glazing
    IMPRESSIONIST_INTIMISTE = auto()  # Cassatt — north-window light, warm/cool shadow contrast, domestic intimacy
    FLEMISH_BAROQUE   = auto()        # Rubens — warm imprimatura, rosy flesh vitality, wet-on-wet alla prima, amber glaze
    FLEMISH_PANORAMIC = auto()        # Bruegel — high-horizon landscape, systematic aerial perspective, earthy palette
    NORDIC_IMPRESSIONIST = auto()     # Zorn — warm Zorn palette, confident calligraphic marks, wet-into-wet portraiture
    IMPRESSIONIST_PLEIN_AIR = auto()  # Morisot — feathery high-key brushwork, colorful violet shadows, luminous atmosphere
    POST_IMPRESSIONIST = auto()      # Degas — crosshatched pastel over monotype, blue-grey tonality, warm orange lights
    PRE_RAPHAELITE = auto()          # Waterhouse — jewel palette, wet white ground luminosity, fine Pre-Raphaelite detail
    SYMBOLIST     = auto()           # Moreau — encrusted gold highlights, Byzantine mosaic texture, deep crimson shadow richness
    FLORENTINE_RENAISSANCE = auto()  # Botticelli — pale gesso ground, sinuous linear grace, tempera hatching, chrysographic gold filaments
    FLORENTINE_MANNERIST = auto()   # Pontormo — acid dissonant palette, cool grey ground, psychological colour tension, compressed figures
    NORTHERN_RENAISSANCE = auto()    # Dürer — pale silver-white ground, cool engraving-precision, cross-hatch shadows, single-hair detail
    QUATTROCENTO  = auto()           # Fra Angelico — chalk-white gesso, tempera hatching, pure lapis/vermilion, gold-leaf halos
    FRENCH_CLASSICAL = auto()        # Poussin — cool architectural clarity, silver shadows, rational colour zones, saturation discipline
    FRENCH_COURT_BAROQUE = auto()    # Rigaud — sumptuous velvet darkness, cool silk highlights, ermine sheen, warm chestnut portraits of royal grandeur
    ROCOCO_PORTRAIT = auto()         # Gainsborough — feathery edge dissolution, cool silver-blue tonality, figure embedded in landscape
    AMERICAN_MARINE = auto()         # Homer — brilliant maritime light, cool Prussian shadows, transparent wash over white ground, decisive unretouched strokes
    FRENCH_ROCOCO = auto()           # Fragonard — bravura loaded-brush highlights, warm cream-peach palette, spontaneous gestural marks, warm amber-honey glaze
    FRENCH_IMPRESSIONIST = auto()    # Renoir — rich chromatic saturation, warm rose-peach flesh, dappled light, feathery curving brushwork, peach-rose glaze
    NORDIC_EXPRESSIONIST = auto()    # Munch — sinuous swirling lines, raw psychological color, existential anxiety rendered as landscape distortion
    DUTCH_GOLDEN_AGE  = auto()       # Frans Hals — bravura alla prima, broken tone, low wet-blend, crisp directional marks
    DANISH_INTIMISTE  = auto()       # Hammershøi — near-monochrome silver-grey, diffuse north window light, profound stillness, invisible blending
    VENETIAN_MANNERIST = auto()     # Tintoretto — near-black void ground, silver lightning highlights, violent diagonal composition, Venetian-cool impasto
    VENETIAN_COLORIST  = auto()     # Veronese — luminous clear palette, saturated brilliant colour, cool silver highlights, monumental architectural setting
    SPANISH_BAROQUE    = auto()     # Murillo — estilo vaporoso, warm amber-rose luminosity, soft dissolved edges, tender spiritual warmth
    VENETIAN_ROCOCO    = auto()     # Tiepolo — celestial overhead light, brilliant azure sky, Naples yellow flesh, pearl-white highlights, aerial luminosity
    BARBIZON      = auto()   # Corot — silvery atmospheric veil, soft cool greens, proto-Impressionist dissolved edges, lyrical landscape intimacy
    VEDUTISMO     = auto()   # Canaletto — crystal-clear Venetian light, precise architectural perspective, cool cerulean sky, warm honey-stone buildings, silver canal water
    PADUAN_RENAISSANCE = auto()  # Mantegna — cold stone-mineral palette, sculptural grisaille clarity, engraved archaeological precision, pale chalk highlights on ridge-forms
    CLASSICAL_LANDSCAPE = auto()  # Claude Lorrain — golden horizon contre-jour, warm amber glaze, soft atmospheric dissolution, dark repoussoir foreground trees
    FRENCH_NEOCLASSICAL = auto()  # David — heroic civic clarity, cool stone-grey backgrounds, smooth luminous flesh, crisp classical contours, restrained palette
    BOLOGNESE_BAROQUE = auto()   # Guido Reni — alabaster pearl skin, heavenly sfumato-adjacent softness, warm rose midflesh, cool lavender-grey shadows, radiant highlight bloom
    PARMA_RENAISSANCE = auto()   # Correggio — golden amber warmth, proto-Baroque softness, tender melting transitions, warm honeyed shadows, sensuous luminous flesh
    FETE_GALANTE  = auto()       # Watteau — crepuscular amber twilight, warm golden imprimatura glow, autumnal melancholy, dissolved midtone edges, peripheral amber vignette
    LOMBARD_RENAISSANCE = auto() # Anguissola — warm Lombard ivory skin, psychological gaze intimacy, sharp eye/lip focus against softened periphery, golden ambient warmth
    NORTHERN_FANTASTICAL = auto() # Bosch — near-black Brabantine void ground, jewel-tone symbolic accents, teeming micro-detail density, phantasmagoric creature texture
    DUTCH_DOMESTIC = auto()      # de Hooch — warm threshold light through doorways, warm/cool interior contrast, geometric tile floors, amber-lit foreground against cool daylight background
    DUTCH_GENRE_COMEDY = auto()  # Jan Steen — warm amber imprimatura glow, rosy flushed flesh, vivid costume accents, energetic alla prima brushwork, warm amber-brown shadows
    VENETIAN_PSYCHOLOGICAL = auto()  # Lotto — cool chromatic anxiety beneath Venetian warmth, psychological eye intensity, background color dissonance, restless chromatic undertone
    FLORENTINE_HIGH_RENAISSANCE = auto()  # Andrea del Sarto — warm golden sfumato, 'faultless' seamless Florentine transitions, amber-ivory flesh, harmonious colour temperature
    FRENCH_INTIMISTE = auto()  # Chardin — warm-gray granular optical texture, muted atmospheric palette, quiet luminosity without dramatism, patient accumulation of small touches
    FRENCH_ROMANTIC  = auto()  # Géricault — turbulent warm-dark chiaroscuro, thick impasto drama, raw emotional intensity, near-black shadows with sudden warm light eruptions
    UMBRIAN_RENAISSANCE = auto()  # Signorelli — muscular clear-contour authority, warm sienna ground, vivid chromatic accents, sculptural bas-relief modelling
    VENETIAN_PASTEL_PORTRAIT = auto()  # Rosalba Carriera — feathery luminous pastel glow, pearlescent skin bloom, cool lavender shadows, warm vellum ground
    AMERICAN_TONALIST = auto()  # Whistler — cool silver-grey tonal harmony, nocturne atmospheric dissolution, peripheral edge loss, minimal palette keyed to a single tonal register
    BELGIAN_SYMBOLIST = auto()  # Spilliaert — near-monochrome ink-black voids, vertiginous geometric perspective, pale isolated figures, cold blue-grey ink darkness, profound solitude
    PARISIAN_REALIST = auto()  # Caillebotte — radical perspective foreshortening, photographic cropping, cool grey urban palette, wet cobblestone reflections, geometric receding planes
    DER_BLAUE_REITER = auto()  # Franz Marc / Kandinsky — spiritual prismatic primaries, symbolic colour assignment, bold simplified animal/landscape forms, ultramarine grounds, unmixed pigment zones
    SICILIAN_RENAISSANCE = auto()  # Antonello da Messina — Flemish oil glazing precision grafted onto Italian warmth; pellucid crystalline flesh, crisp found edges, direct psychological gaze, warm ivory highlights over blue-green shadow transitions
    FLEMISH_LATE_GOTHIC  = auto()  # Hugo van der Goes — intense psychological realism, deep warm-brown shadows, earthy amber-ochre palette, velvety near-black voids, fine Flemish detail with weighty human presence
    DUTCH_FIJNSCHILDER   = auto()  # Gerrit Dou — extreme enamel-like surface fineness, 30+ glaze layers, candle-warm amber highlights, niche-framed compositions, glass-smooth skin, magnifying-glass precision
    DUTCH_LIGHT_GROUND   = auto()  # Carel Fabritius — contre-jour technique, pale grey ground, figures reading against bright background, confident impressionistic brushwork, atmospheric ambient light
    DUTCH_CANDLELIT_GENRE = auto()  # Judith Leyster — warm candlelit genre scenes, Hals-adjacent bravura, Utrecht Caravaggist amber warmth, joyful animated figures, warm brown imprimatura vitality
    DUTCH_BRAVURA_PORTRAIT = auto()  # Frans Hals — alla prima directional energy, confident tache brushwork, psychological vivacity, warm imprimatura with low wet-blend, crisp directional marks
    MILANESE_SFUMATO       = auto()  # Bernardino Luini — Leonardo-school Milanese sfumato, warm ivory highlights, cool-violet shadow delicacy, seamless flesh surfaces, sweet idealized expressions
    MILANESE_PEARLED       = auto()  # Giovanni Antonio Boltraffio — Leonardesque sfumato with cool pearl highlights, deep cool-blue shadows, crystalline mid-flesh precision, jewel-like psychological depth
    UMBRIAN_MANNERIST      = auto()  # Federico Barocci — petal-soft rose-pink penumbra flush, pasteletti bianca ground luminosity, proto-Baroque tenderness, warm perimeter dissolution
    CHROMATIC_INTIMISME    = auto()  # Pierre Bonnard — warm/cool chromatic oscillation in mid-tones, hallucinatory colour saturation, cadmium-yellow dominance, violet-shadow complements, domestic Mediterranean light
    PROTO_RENAISSANCE      = auto()  # Masaccio — architectonic mass modeling, deep directional shadow, warm ochre highlights, sculptural gravity, no sfumato
    BELLE_EPOQUE           = auto()  # Toulouse-Lautrec — peinture à l'essence matte surface, spidery diagonal hatching, warm-cool separation, bold flat-color zones, Japonisme-influenced graphic flatness
    VICTORIAN_SOCIAL_REALIST = auto()  # James Tissot — enamel surface clarity, specular fabric sheen, chromatic richness in warm midtones, cool crystalline highlights, precise atmospheric colour recession
    FLORENTINE_DEVOTIONAL_BAROQUE = auto()  # Carlo Dolci — hyper-smooth devotional enamel finish, deep walnut-brown shadow glazes, crystalline ivory highlights, introspective psychological stillness, obsessive surface polish
    NEAPOLITAN_BAROQUE = auto()  # Luca Giordano — warm golden-aureole illumination, sweeping Venetian colour, theatrical tenebrism, dynamic aerial grandeur, rapid luminous synthesis of all prior traditions
    SPANISH_NEAPOLITAN_BAROQUE = auto()  # Jusepe de Ribera — brutal tenebrism from near-black void, gritty visible shadow texture, warm amber highlights, raw psychological realism, Spanish naturalism grafted onto Caravaggism
    BERGAMASQUE_PORTRAIT_REALISM = auto()  # Giovanni Battista Moroni — cool silver highlights, warm shadow recovery, mid-tone presence; the most psychologically direct portrait realism in 16th-century Italy
    GENOESE_VENETIAN_BAROQUE = auto()  # Bernardo Strozzi — warm chestnut-amber shadows, bravura impasto highlights, saturated Venetian-Genoese colorism, loaded-brush vitality
    ROMAN_DEVOTIONAL_BAROQUE = auto()  # Sassoferrato — pure ultramarine glazing, porcelain skin translucency, devotional calm, seamless blending, psychological stillness
    ITALO_COURTLY_BAROQUE = auto()  # Orazio Gentileschi — cool silver north-window daylight, restrained Caravaggesque naturalism, chromatic fabric precision, courtly aristocratic elegance
    ANTWERP_BAROQUE = auto()        # Jacob Jordaens — warm sienna-ochre ground, earthy ruddy flesh vitality, warm cream impasto highlights, amber shadow retention, grounded Flemish naturalism
    EMILIAN_ROSY_BAROQUE = auto()  # Guido Cagnacci — dreamlike rose-flesh luminescence, pinkish peach mid-tone glow, smooth Reni-derived sfumato, warm shadow recovery, glazed inner-light quality
    FLORENTINE_MELANCHOLIC_BAROQUE = auto()  # Francesco Furini — evanescent ivory skin bloom, cool lavender penumbra at shadow edges, ultra-smooth Florentine sfumato, figures emerging from deep darkness with melancholic inwardness
    BOLOGNESE_MANNERIST_PORTRAITURE = auto()  # Lavinia Fontana — warm rose-ivory flesh brilliance, deep crimson costume richness, amber velvet shadow warmth, Bolognese glazed high finish
    LOMBARD_LEONARDESQUE = auto()  # Solario — pellucid amber-honey flesh, cool violet Venetian shadows, ultra-smooth Leonardesque sfumato, warm amber glazing depth
    UMBRIAN_CLASSICAL_HARMONY = auto()  # Perugino — luminous ground warmth diffusing through glazes, ivory-gold serene highlights, warm amber shadows, harmonious open landscapes, psychological serenity
    BRESCIAN_SILVER_NOCTURNE  = auto()  # Savoldo — cool silver moonveil at the penumbra boundary, phosphorescent drapery shimmer, warm ivory highlights, near-nocturnal atmospheric depth
    ROMAN_GRAND_TOUR_CLASSICISM = auto()  # Batoni — polished Roman-Classicist flesh with anisotropic silk-sheen streaks, warm Rococo carnations, amber-glazed finish
    VENETIAN_ECCENTRIC_PORTRAITURE = auto()  # Lotto — vivid eccentric color contrasts, multi-scale chromatic vibration field, warm rose-ivory highlights, cool shadow accents, psychological intensity
    ITALIAN_BELLE_EPOQUE_PORTRAITURE = auto()  # Boldini — dual-angle swirl bravura, luminous warm flesh emerging from near-black grounds, aristocratic vivacity
    BOLOGNESE_ACADEMIC_NATURALISM = auto()   # Annibale Carracci — warm-ground naturalism, directional tonal temperature field, lit-side warmth vs cool-shadow, Bolognese reformist clarity
    ROMAN_BAROQUE_LANDSCAPE = auto()  # Salvator Rosa — gestural turbulent displacement, near-black umber ground, storm-charged atmospheric borders, warm amber focal light from enveloping darkness
    NEAPOLITAN_BAROQUE_CLASSICISM = auto()  # Massimo Stanzione — warm Reni-derived ivory highlights, cool violet shadow penumbra, Laplacian pyramid mid-frequency clarity, golden Bolognese classicist flesh
    CONTEMPORARY  = auto()
    FANTASY_ART   = auto()
    NONE          = auto()


class PaletteHint(Enum):
    """Broad colour temperature / key for the style system."""
    WARM_EARTH   = auto()   # ochres, siennas, umbers
    COOL_GREY    = auto()   # silver, blue-grey, ash
    DARK_EARTH   = auto()   # near-blacks, deep browns
    JEWEL        = auto()   # saturated magentas, teals, golds
    MUTED        = auto()   # desaturated, painterly
    MONOCHROME   = auto()
    NATURAL      = auto()   # read from reference


# ─────────────────────────────────────────────────────────────────────────────
# Component dataclasses
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PoseDetail:
    """
    Fine-grained pose control.
    joints: dict mapping joint name → world-space Vec3 position.
    Blender maps these to armature bone head positions.
    Common joint names: head, neck, l_shoulder, r_shoulder,
    l_elbow, r_elbow, l_wrist, r_wrist, spine, l_hip, r_hip,
    l_knee, r_knee, l_ankle, r_ankle.
    """
    gesture_curve: Optional[List[Vec3]] = None   # line of action, spine to head
    joints: Optional[dict] = None
    head_tilt: float  = 0.0    # degrees, + = right ear to shoulder
    head_turn: float  = 0.0    # degrees, + = face turns right (viewer's left)
    head_nod:  float  = 0.0    # degrees, + = chin down


@dataclass
class Costume:
    """
    What the subject is wearing.
    Described loosely; Blender scripts interpret for cloth simulation.
    """
    top:        Optional[str]  = None   # "dark robe", "plate armour", "silk blouse"
    bottom:     Optional[str]  = None
    headwear:   Optional[str]  = None
    accessory:  Optional[str]  = None
    palette:    PaletteHint    = PaletteHint.NATURAL
    fabric_sim: bool           = True   # run Blender cloth sim if True


@dataclass
class Character:
    """
    A single subject in the scene.
    Multiple characters can coexist in one Scene.
    """
    archetype:   Archetype     = Archetype.HUMAN
    build:       Build         = Build.AVERAGE
    sex:         Sex           = Sex.UNSPECIFIED
    age:         AgeRange      = AgeRange.ADULT
    skin_tone:   SkinTone      = SkinTone.MEDIUM
    hair_style:  HairStyle     = HairStyle.LONG
    hair_color:  Color         = (0.22, 0.12, 0.05)   # dark auburn default

    pose:        Pose          = Pose.STANDING
    pose_detail: PoseDetail    = field(default_factory=PoseDetail)
    expression:  Expression    = Expression.NEUTRAL
    morphology:  Optional[CartoonMorphology] = None   # None = realistic defaults
    facing:      Vec3          = field(default_factory=lambda: Vec3(0, 0, 1))

    costume:     Costume       = field(default_factory=Costume)
    position:    Vec3          = field(default_factory=Vec3)   # world space
    scale:       float         = 1.0    # 1.0 = ~1.75m human

    # Creature-specific overrides (used when archetype != HUMAN)
    creature_desc: Optional[str] = None   # "dragon with iridescent scales"


@dataclass
class Camera:
    """
    Scene viewpoint.
    position / target are in Blender world space (Z-up, Y-back).
    fov: horizontal field of view in degrees.
    """
    position: Vec3  = field(default_factory=lambda: Vec3(0, -3.5, 1.6))
    target:   Vec3  = field(default_factory=lambda: Vec3(0,  0,   1.2))
    fov:      float = 35.0     # 35mm portrait lens
    # Depth of field
    dof_enabled:   bool  = False
    dof_aperture:  float = 2.8   # f-stop
    dof_focus_dist: float = 3.5  # metres


@dataclass
class Light:
    """A single light source."""
    position:  Vec3   = field(default_factory=lambda: Vec3(-2, -2, 3))
    color:     Color  = (1.0, 0.95, 0.85)   # warm white
    intensity: float  = 800.0   # Blender watts
    kind:      str    = "AREA"  # AREA | POINT | SUN | SPOT


@dataclass
class LightRig:
    """
    Named multi-light setups.
    Build custom rigs or use the class-level presets below.
    """
    lights: List[Light] = field(default_factory=list)
    ambient_color: Color  = (0.05, 0.05, 0.08)
    ambient_strength: float = 0.3

    # ── Named presets ─────────────────────────────────────────────────────────

    @classmethod
    def three_point_warm(cls) -> LightRig:
        """Classic three-point: warm key left, cool fill right, rim behind."""
        return cls(lights=[
            Light(Vec3(-2.5, -1.5, 3.0), (1.0, 0.92, 0.78), 120, "AREA"),   # key
            Light(Vec3( 2.0, -1.0, 2.0), (0.72, 0.82, 1.0),   30, "AREA"),   # fill
            Light(Vec3( 0.5,  2.5, 2.5), (1.0, 0.98, 0.92),   60, "AREA"),   # rim
        ], ambient_color=(0.08, 0.06, 0.04), ambient_strength=0.25)

    @classmethod
    def rembrandt(cls) -> LightRig:
        """Single strong key from upper-left; deep shadow side."""
        return cls(lights=[
            Light(Vec3(-2.0, -0.5, 3.5), (1.0, 0.90, 0.75), 180, "AREA"),
        ], ambient_color=(0.04, 0.03, 0.02), ambient_strength=0.15)

    @classmethod
    def overcast(cls) -> LightRig:
        """Soft wrap light simulating cloudy sky."""
        return cls(lights=[
            Light(Vec3(0, 0, 5), (0.85, 0.90, 1.0), 5, "SUN"),
        ], ambient_color=(0.60, 0.68, 0.80), ambient_strength=0.8)

    @classmethod
    def sunset(cls) -> LightRig:
        """Low warm key from right, cool blue fill from left."""
        return cls(lights=[
            Light(Vec3(3.0, -1.0, 0.8), (1.0, 0.65, 0.30), 8, "SUN"),
            Light(Vec3(-2.0, -1.0, 2.0), (0.45, 0.60, 1.0), 20, "AREA"),
        ], ambient_color=(0.15, 0.10, 0.20), ambient_strength=0.4)


@dataclass
class Environment:
    """
    Scene backdrop and atmosphere.
    hdri_path: path to an HDR image for environment lighting/background.
    """
    type:        EnvType = EnvType.EXTERIOR
    description: str     = ""        # "rolling hills with distant water"
    atmosphere:  float   = 0.0       # 0 = clear, 1 = heavy fog/haze
    hdri_path:   Optional[str] = None
    ground_color: Color  = (0.25, 0.22, 0.18)


@dataclass
class Style:
    """
    Rendering style that maps to stroke_engine parameters.
    The stroke engine reads this to configure its passes.
    """
    medium:  Medium      = Medium.OIL
    period:  Period      = Period.RENAISSANCE
    palette: PaletteHint = PaletteHint.WARM_EARTH

    # Stroke engine overrides (None = use period defaults)
    stroke_size_face:   Optional[float] = None
    stroke_size_bg:     Optional[float] = None
    wet_blend:          Optional[float] = None
    edge_softness:      Optional[float] = None   # 0 = hard edges, 1 = full sfumato

    @property
    def stroke_params(self) -> dict:
        """
        Returns a dict of stroke_engine parameters for this style.
        Callers merge these with their own overrides.
        """
        defaults = {
            Period.RENAISSANCE:   dict(stroke_size_face=6,  stroke_size_bg=30, wet_blend=0.08, edge_softness=0.85),
            Period.BAROQUE:       dict(stroke_size_face=7,  stroke_size_bg=32, wet_blend=0.10, edge_softness=0.70),
            Period.IMPRESSIONIST: dict(stroke_size_face=10, stroke_size_bg=22, wet_blend=0.28, edge_softness=0.30),
            Period.EXPRESSIONIST: dict(stroke_size_face=14, stroke_size_bg=28, wet_blend=0.35, edge_softness=0.15),
            # Pointillist: tiny dots, zero wet-blending, crisp optical colour mixing.
            # stroke_size_face/bg here describes dot radius for pointillist_pass().
            Period.POINTILLIST:   dict(stroke_size_face=4,  stroke_size_bg=5,  wet_blend=0.02, edge_softness=0.10),
            # Romantic (Turner): very high wet blending and edge softness so forms
            # dissolve into radiant atmospheric light.  luminous_glow_pass() is the
            # key post-processing step for this period.
            Period.ROMANTIC:      dict(stroke_size_face=14, stroke_size_bg=30, wet_blend=0.75, edge_softness=0.90),
            # Art Nouveau (Klimt): moderate strokes; low wet blend to keep colour
            # zones crisp; the decorative gold overlay is applied as a glaze pass.
            Period.ART_NOUVEAU:   dict(stroke_size_face=6,  stroke_size_bg=20, wet_blend=0.15, edge_softness=0.40),
            # Ukiyo-e (Hokusai): woodblock print aesthetic — flat colour regions,
            # Prussian blue bokashi gradient, bold ink contour keyblock lines.
            # stroke_size_face is the ink contour line width; stroke_size_bg is
            # the bokashi soft-brush pass size used for sky/background gradients.
            Period.UKIYO_E:       dict(stroke_size_face=3,  stroke_size_bg=12, wet_blend=0.04, edge_softness=0.08),
            # Proto-Expressionist (Goya Black Paintings): crude, urgent dark strokes.
            # stroke_size_face large — spatula-like marks; stroke_size_bg very large
            # (black void background needs few, vast, dark strokes).
            # Very low wet_blend and edge_softness — forms are barely resolved.
            Period.PROTO_EXPRESSIONIST: dict(stroke_size_face=14, stroke_size_bg=45, wet_blend=0.12, edge_softness=0.25),
            # Realist (Manet): flat value-plane technique — wide loaded strokes,
            # minimal wet blending (flat patches, not gradients), crisp plane boundaries.
            # stroke_size_face large — Manet laid paint on in broad decisive patches.
            # Low wet_blend = paint stays where placed (no bleed into neighbour).
            # Low edge_softness = plane boundaries are visible and intentional.
            Period.REALIST:       dict(stroke_size_face=11, stroke_size_bg=28, wet_blend=0.15, edge_softness=0.20),
            # Viennese Expressionist (Schiele): razor-sharp angular contour drawing.
            # stroke_size_face is the contour line thickness — very thin (2–4px).
            # stroke_size_bg is background flat-stroke size (the void requires few,
            # large strokes to stay flat and barely-coloured).
            # Nearly zero wet_blend and edge_softness — dry, brutal, no softening.
            Period.VIENNESE_EXPRESSIONIST: dict(stroke_size_face=3, stroke_size_bg=24, wet_blend=0.04, edge_softness=0.04),
            # Color Field (Rothko): immense wash strokes; very high wet blend and edge
            # softness so bands melt into each other.  stroke_size_face is the wash
            # brush width — extremely wide (40–60px).  stroke_size_bg matches: the
            # background absorbing void is painted with the same vast brush.
            Period.COLOR_FIELD:   dict(stroke_size_face=42, stroke_size_bg=55, wet_blend=0.72, edge_softness=0.90),
            # Synthetist / Cloisonnist (Gauguin): bold flat colour zones with hard edges.
            # stroke_size_face is the flat fill stroke width — moderately wide (8–12px)
            # so each zone is covered in a few broad loaded sweeps.  stroke_size_bg is the
            # zone-fill stroke in background areas — larger (18–22px) for expansive fields.
            # Very low wet_blend: Synthetism demands crisp, non-blended zones.
            # Very low edge_softness: the cloisonné line is hard, not sfumatoed.
            Period.SYNTHETIST:    dict(stroke_size_face=10, stroke_size_bg=20, wet_blend=0.06, edge_softness=0.10),
            # Mannerist (El Greco): moderate stroke size with decisive drapery marks.
            # stroke_size_face is the figure detail stroke — slightly larger than
            # Renaissance to match El Greco's bold, sculptural paint application.
            # stroke_size_bg is the dark void background stroke — very large (near-black
            # ground needs few strokes).  Low wet_blend: colour zones are distinct and
            # jewel-like, not blurred.  Low-moderate edge_softness: edges are present
            # but softened by the inner glow that characterises his flesh areas.
            Period.MANNERIST:     dict(stroke_size_face=8,  stroke_size_bg=35, wet_blend=0.18, edge_softness=0.30),
            # Surrealist / Naïve Folk (Kahlo): flat saturated zones with no blending.
            # stroke_size_face is the loaded-brush stroke width — moderate; covers forms
            # in the deliberate naive style.  stroke_size_bg is smaller — background
            # objects (foliage, symbolic flora) need tighter control than a void ground.
            # Near-zero wet_blend: Kahlo's zones do not bleed; paint is dry and flat.
            # Very low edge_softness: hard dark outlines, no sfumato.
            Period.SURREALIST:    dict(stroke_size_face=8,  stroke_size_bg=18, wet_blend=0.08, edge_softness=0.12),
            # Abstract Expressionist (Kandinsky): geometric forms demand crisp boundaries
            # and minimal blending.  stroke_size_face is the primary geometric primitive
            # size — medium (shapes are legible, not microscopic).  stroke_size_bg is
            # the background fill stroke — larger for broad colour-ground sweeps.
            # Very low wet_blend: geometric edges must stay hard.
            # Low edge_softness: no sfumato; circles and triangles have clean arcs.
            Period.ABSTRACT_EXPRESSIONIST: dict(stroke_size_face=10, stroke_size_bg=22, wet_blend=0.08, edge_softness=0.12),
            # Venetian Renaissance (Titian): rich warm impasto and transparent glazing.
            # stroke_size_face is the impasto highlight stroke width — bold (12px) to
            # match Titian's thick loaded-brush passages.  stroke_size_bg is the
            # background block-in stroke — moderate.  High wet_blend: Titian worked
            # wet-into-wet, pushing and pulling colours across a moist surface.
            # Moderate-high edge_softness: edges soften through glazing, but Titian
            # is firmer than Leonardo's pure sfumato — forms are readable.
            Period.VENETIAN_RENAISSANCE: dict(stroke_size_face=12, stroke_size_bg=30, wet_blend=0.72, edge_softness=0.62),
            # Early Venetian Renaissance (Bellini): the first great Venetian master worked in thin,
            # precise oil glazes on a warm amber imprimatura — a technique he adopted from Antonello
            # da Messina (who brought Flemish oil technique to Venice).  Forms are built with deliberate
            # patient layering rather than broad wet-on-wet passages.
            # stroke_size_face=5: fine, considered marks — Bellini's faces are constructed with careful,
            # overlapping semi-transparent oil touches, building tonal richness through accumulated depth.
            # stroke_size_bg=22: moderate — his altarpiece backgrounds (architectural niches, sky, distant
            # landscape) are carefully observed but not Flemish-level micro-detail.
            # wet_blend=0.55: moderate-high — thin oil glazing permits significant wet blending in flesh
            # halftones, particularly in the soft transitions around the eyes and mouth that give his
            # Madonnas their characteristic serenity.
            # edge_softness=0.55: moderate — Bellini's edges are softer than the Northern Renaissance
            # (Dürer) but firmer than Leonardo's sfumato; forms are clearly resolved and architecturally
            # sound, with a gentle atmospheric softening at peripheral edges.
            # Venetian High Renaissance (Giorgione): tonal building without linear armature.
            # stroke_size_face=7: larger than Bellini's precise marks, smaller than Titian's
            # gestural impasto — Giorgione built flesh in broad, blended tonal zones rather
            # than individual brushwork passages.
            # stroke_size_bg=24: moderate — his backgrounds are atmospheric and painterly,
            # not the micro-detail of Flemish technique nor the bold drama of Tintoretto.
            # wet_blend=0.62: high — tonal zones are worked wet-into-wet; the characteristic
            # 'pittura di macchia' technique requires colour to flow between zones freely.
            # edge_softness=0.72: soft-but-present — not Leonardo's dissolved sfumato, not
            # van Eyck's precision; forms merge gently into atmosphere while remaining legible.
            Period.VENETIAN_HIGH_RENAISSANCE: dict(stroke_size_face=7, stroke_size_bg=24, wet_blend=0.62, edge_softness=0.72),
            Period.EARLY_VENETIAN_RENAISSANCE: dict(stroke_size_face=5, stroke_size_bg=22, wet_blend=0.55, edge_softness=0.55),
            # Fauvist (Matisse): bold flat colour zones, zero modelling, maximum
            # saturation.  stroke_size_face is the loaded-brush zone fill width —
            # medium (colours are placed in decisive broad patches).  stroke_size_bg
            # is the background fill size — larger (backgrounds are as assertive as
            # the figure in Fauvist painting).  Very low wet_blend: zones do not bleed
            # into each other — flat is the point.  Very low edge_softness: coloured
            # contour lines separate zones cleanly, no sfumato.
            Period.FAUVIST:       dict(stroke_size_face=10, stroke_size_bg=22, wet_blend=0.05, edge_softness=0.08),
            # Primitivist (Modigliani): mask-like oval faces, minimal modelling.
            # stroke_size_face is the face zone fill stroke — medium (broad decisive
            # ochre passages over the face plane).  stroke_size_bg is the background
            # flat fill — large (single flat cobalt/viridian background plane).
            # Very low wet_blend: zones must stay flat, no blending across boundaries.
            # Low edge_softness: the oval contour outline is present and deliberate.
            Period.PRIMITIVIST:   dict(stroke_size_face=9,  stroke_size_bg=20, wet_blend=0.10, edge_softness=0.18),
            # Early Netherlandish (van Eyck): very fine brushwork, multiple transparent glaze layers.
            # stroke_size_face is very small — Flemish faces are built with tiny, precise marks.
            # stroke_size_bg is moderate — architectural and landscape details are also fine.
            # Moderate wet_blend: glazing requires careful wet-into-wet in highlight passages,
            # but each glaze layer must stay distinct.  Moderate edge_softness: Flemish edges
            # are present and precise, softened only by the outermost translucent glaze film.
            Period.EARLY_NETHERLANDISH: dict(stroke_size_face=4, stroke_size_bg=14, wet_blend=0.55, edge_softness=0.45),
            # Art Deco (de Lempicka): smooth, polished surfaces — low wet_blend keeps
            # colour zones hard-edged and metallic.  stroke_size_face is the smoothing
            # brush width — medium (facets are larger than Flemish micro-detail but
            # smaller than Impressionist dabs).  stroke_size_bg is the background fill.
            # Very low edge_softness: Art Deco has sharp, decisive contour lines.
            Period.ART_DECO:      dict(stroke_size_face=8,  stroke_size_bg=22, wet_blend=0.06, edge_softness=0.08),
            # Nabis / Intimisme (Vuillard): short dense marks cover every surface equally —
            # figures do not stand out from their background but dissolve into it.
            # stroke_size_face is small-medium (intimate surface requires close marks).
            # stroke_size_bg is also small — the patterned background receives the same
            # close-mark treatment as the figure.  Low wet_blend: muted chalky zones stay
            # flat.  Low-moderate edge_softness: edges softened by uniform mark density
            # rather than blending — forms lose definition in the pattern.
            Period.NABIS:         dict(stroke_size_face=7,  stroke_size_bg=9,  wet_blend=0.12, edge_softness=0.28),
            # Luminismo (Sorolla): bold outdoor Impressionism — maximum sunlight,
            # warm/cool simultaneous contrast.  stroke_size_face is moderate (loaded
            # decisive outdoor strokes).  stroke_size_bg is large (broad sky and sea
            # washes).  Moderate wet_blend: lively wet-into-wet but strokes stay
            # readable and energetic, not muddy.  Low-moderate edge_softness: forms
            # are clear in the brilliant Mediterranean light — no sfumato.
            Period.LUMINISMO:     dict(stroke_size_face=10, stroke_size_bg=24, wet_blend=0.38, edge_softness=0.42),
            # High Renaissance (Raphael): luminous clarity — forms rounded gently,
            # no sfumato haze, shadows transparent.  stroke_size_face is moderate
            # (7–9px: fine enough for idealized detail, broad enough for confident
            # form-building).  stroke_size_bg is moderate — balanced backgrounds.
            # wet_blend=0.35: softer than Baroque but far less blended than Leonardo.
            # edge_softness=0.58: clear, legible forms with soft penumbra (not sfumato).
            Period.HIGH_RENAISSANCE: dict(stroke_size_face=7, stroke_size_bg=26, wet_blend=0.35, edge_softness=0.58),
            # Tenebrist (Zurbarán): near-black void with hyper-real white fabric.
            # stroke_size_face is small — fabric folds and flesh require fine marks.
            # stroke_size_bg is large — the void background needs few, vast, dark strokes.
            # Low wet_blend: forms are precise and sculpted, not blended.
            # Low edge_softness: the razor-sharp fabric-to-void edge is the defining quality.
            Period.TENEBRIST:     dict(stroke_size_face=6,  stroke_size_bg=40, wet_blend=0.22, edge_softness=0.28),
            # Neoclassical (Ingres): precise classical clarity — smaller strokes for
            # the fine-detail flesh rendering that defines Ingres.  stroke_size_face
            # is very small (5px) to allow the micro-blending of flesh tones that
            # creates his porcelain surface.  stroke_size_bg moderate — architectural
            # backgrounds are precisely drawn, not impressionistic.
            # wet_blend=0.28: enough to blend flesh tones smoothly, not so much as
            # to lose the deliberate precision of his form edges.
            # edge_softness=0.35: classical edge quality — clear, legible, not sfumatoed.
            Period.NEOCLASSICAL:  dict(stroke_size_face=5,  stroke_size_bg=22, wet_blend=0.28, edge_softness=0.35),
            # Nocturne (La Tour): single candlelight source — forms are simplified and
            # smooth; the transition from warm light to absolute darkness is gradual.
            # stroke_size_face is medium-small (smooth geometric forms need careful
            # blending).  stroke_size_bg is very large — the void background is a flat
            # near-black wash requiring few, sweeping dark strokes.
            # wet_blend=0.55: enough for the tender gradients of candlelit flesh but
            # not so heavy as to lose the clarity of La Tour's simplified geometry.
            # edge_softness=0.45: soft penumbra around lit forms, but clear legible
            # geometry — neither sfumato haze nor Tenebrist knife-edge.
            Period.NOCTURNE:      dict(stroke_size_face=7,  stroke_size_bg=45, wet_blend=0.55, edge_softness=0.45),
            # French Naturalist (Chardin): granular powdery surface built from small
            # overlapping dry-brush marks.  stroke_size_face is small (5px) — each mark
            # is a careful directional stamp.  stroke_size_bg is moderate — domestic
            # backgrounds are as intimately worked as the subjects.
            # Low wet_blend: marks stay distinct, creating the optical granularity.
            # Moderate edge_softness: edges dissolve softly without sfumato haze.
            Period.FRENCH_NATURALIST: dict(stroke_size_face=5, stroke_size_bg=14, wet_blend=0.22, edge_softness=0.65),
            # Social Realist (Courbet): palette knife deposits flat planes with crisp edges.
            # Large stroke_size_face — the knife covers broad areas in a single pass.
            # Very low wet_blend: each plane stays separate, no gradient merging.
            # Low edge_softness: clean knife-drag boundaries between tonal planes.
            Period.SOCIAL_REALIST: dict(stroke_size_face=14, stroke_size_bg=35, wet_blend=0.18, edge_softness=0.25),
            # Academic Realist (Bouguereau): the opposite extreme from Courbet — almost
            # invisible brushwork, porcelain-smooth flesh achieved through imperceptible
            # micro-blending.  stroke_size_face is tiny (3px) — each mark is a single
            # carefully placed filbert-hair stroke that is immediately blended away.
            # stroke_size_bg is moderate — Academic painting has precise, well-resolved
            # backgrounds even if the figure steals all the attention.
            # Very high wet_blend (0.88): the defining quality — no stroke ever dries
            # before it is blended into its neighbour.  High edge_softness (0.82): edges
            # on the figure are as smooth as the flesh itself — no crisp Academic line
            # separates the figure from the background; the boundary dissolves gradually.
            Period.ACADEMIC_REALIST: dict(stroke_size_face=3, stroke_size_bg=18, wet_blend=0.88, edge_softness=0.82),
            # Impressionist Intimiste (Cassatt): north-window daylight — soft, cool, diffused.
            # stroke_size_face is moderate (9px) — deliberate but not broken-colour Impressionist.
            # stroke_size_bg is moderate (18px) — flat decorative backgrounds need fewer,
            # broader sweeps than an outdoor Impressionist landscape.
            # wet_blend=0.38: more deliberate than outdoor Impressionism; shadows blend
            # gently but retain their chromatic warmth rather than becoming opaque mud.
            # edge_softness=0.42: north light creates soft but present edges — no sfumato
            # haze, but no Baroque razor-edge either.  Edges read across the room.
            Period.IMPRESSIONIST_INTIMISTE: dict(stroke_size_face=9, stroke_size_bg=18, wet_blend=0.38, edge_softness=0.42),
            # Flemish Panoramic (Bruegel): high-horizon landscape with systematic aerial
            # perspective.  stroke_size_face is moderate — individual figure marks are
            # small relative to the broad landscape.  stroke_size_bg is large — vast
            # landscape areas are painted with broad sweeping strokes.
            # Moderate wet_blend (0.28): forms are clear and present, not blended into
            # atmospheric haze (bruegel_panorama_pass() adds the haze as a separate step).
            # Moderate edge_softness (0.50): foreground figures have clear edges; the
            # atmospheric haze is added as a composable pass, not baked into the stroke.
            Period.FLEMISH_PANORAMIC: dict(stroke_size_face=6, stroke_size_bg=28, wet_blend=0.28, edge_softness=0.50),
            # Nordic Impressionist (Zorn): confident large-brush portraiture on a toned ground.
            # stroke_size_face is medium-large (10px) — Zorn's calligraphic marks were decisive
            # and broader than finicking Academic or Renaissance touches.  stroke_size_bg is
            # large (28px) for the bold background washes typical of his portrait settings.
            # wet_blend=0.62: strong enough to blend flesh tones fluidly in wet-into-wet
            # passages without losing the individuality of each stroke — Zorn's marks dissolve
            # at their edges but remain legible at their centres.
            # edge_softness=0.42: decisive edges that have a natural wet-paint softness —
            # not the sfumato of Leonardo or the razor-edge of Tenebrist; the boundary is
            # present but yielding, as if the paint was still moist.
            # Early Italian Renaissance (Piero della Francesca): geometric precision, diffuse cool light.
            # stroke_size_face=5: fine deliberate marks — Piero built form with precision, never
            # broad gesture; his flesh tones emerge from patient layering rather than large wet passes.
            # stroke_size_bg=22: moderate — architectural and landscape backgrounds need crisp geometry
            # more than expressive sweep.
            # wet_blend=0.45: moderate — more blending than Flemish oil glazing but far less than
            # Leonardo's 0.92 sfumato; Piero's transitions are smooth but not smoke-dissolved.
            # edge_softness=0.42: clean, present edges — the geometric clarity of his figures and
            # architectural forms is a signature quality; edges are resolved, not dissolved.
            Period.EARLY_ITALIAN_RENAISSANCE: dict(stroke_size_face=5, stroke_size_bg=22, wet_blend=0.45, edge_softness=0.42),
            Period.NORDIC_IMPRESSIONIST: dict(stroke_size_face=10, stroke_size_bg=28, wet_blend=0.62, edge_softness=0.42),
            # Impressionist Plein Air (Morisot): airy, high-key portraiture on a pale ground.
            # stroke_size_face=9: medium marks — visible individual brushwork, not coarse.
            # stroke_size_bg=20: loose, open background washes that let the ground breathe.
            # wet_blend=0.35: enough blending to fuse colors softly without losing stroke identity.
            # edge_softness=0.25: crisp-ish — Morisot's strokes have legible direction and boundary,
            # unlike sfumato; edges are yielding but present.
            Period.IMPRESSIONIST_PLEIN_AIR: dict(stroke_size_face=9, stroke_size_bg=20, wet_blend=0.35, edge_softness=0.25),
            # Post-Impressionist (Degas): pastel-hatching over a dark monotype base.
            # stroke_size_face=7: fine directional marks — Degas' pastel hatching was precise
            # and calligraphic, not broad washes.  stroke_size_bg=18: moderate background marks;
            # his backgrounds are often dissolved into tonal washes that frame the figure.
            # wet_blend=0.22: pastel behaves drier than oil — marks sit alongside each other
            # rather than blending, producing optical colour mixing from a distance.
            # edge_softness=0.35: edges are softened by pastel layering but never fully lost;
            # Degas retained structural drawing clarity beneath the colouristic surface.
            Period.POST_IMPRESSIONIST: dict(stroke_size_face=7, stroke_size_bg=18, wet_blend=0.22, edge_softness=0.35),
            # Pre-Raphaelite (Waterhouse): the Brotherhood painted on a STILL-WET white ground,
            # so every colour reads at maximum luminosity — no oil sinking into a dark priming.
            # stroke_size_face=5: fine, detail-oriented marks (foliage, fabric, face textures
            # were all rendered with exceptional Pre-Raphaelite precision).  stroke_size_bg=16:
            # moderate — landscape and architectural backgrounds are carefully observed,
            # not loose Impressionist washes.  wet_blend=0.30: enough to fuse flesh tones
            # smoothly on the wet white ground without losing brushstroke identity.
            # edge_softness=0.28: edges are present and legible — Pre-Raphaelite precision —
            # but yielding at the focal periphery through the scumbling technique.
            Period.PRE_RAPHAELITE: dict(stroke_size_face=5, stroke_size_bg=16, wet_blend=0.30, edge_softness=0.28),
            # Symbolist (Moreau): Moreau built up his surfaces with extremely fine, patient
            # touches — many small strokes encrusting the canvas surface like jewels set in
            # a reliquary.  stroke_size_face=4: the smallest marks, because his mythological
            # figures are painted with near-miniaturist precision in faces and drapery.
            # stroke_size_bg=20: architectural and landscape backgrounds receive richer,
            # more gestural treatment — looming mythological architecture, dark abyssal spaces.
            # wet_blend=0.25: moderate blending, but Moreau preserved the identity of each
            # touch; paint does not fully melt together, it stacks and accumulates.
            # edge_softness=0.20: edges are relatively crisp and linear — Moreau was a
            # draughtsman first, and his forms have clear sculptural definition even through
            # the richness of surface.
            Period.SYMBOLIST:     dict(stroke_size_face=4,  stroke_size_bg=20, wet_blend=0.25, edge_softness=0.20),
            # Florentine Renaissance (Botticelli): egg tempera on white gessoed panel.
            # stroke_size_face=4: very fine marks — tempera hatching is built from
            # individual parallel hairs of the brush, finer than any oil technique.
            # stroke_size_bg=18: moderate — botanical and landscape backgrounds are
            # also painted with fine deliberate tempera marks, not loose washes.
            # wet_blend=0.06: near-zero — egg tempera dries in seconds; form is built
            # through transparent layering, never wet-on-wet blending.
            # edge_softness=0.12: very crisp — the flowing Gothic-influenced contour
            # line defines every figure; there is no sfumato, no atmospheric softening;
            # the edge is a drawn line, not the edge of a tonal gradient.
            Period.FLORENTINE_RENAISSANCE: dict(stroke_size_face=4, stroke_size_bg=18, wet_blend=0.06, edge_softness=0.12),
            # Florentine Mannerist (Pontormo): acid palette, psychological dissonance, compressed figures.
            # stroke_size_face=5: fine-medium marks — Pontormo built his faces with careful deliberate
            # strokes on a cool grey ground; not as fine as tempera hatching but more deliberate than
            # broad oil impasto.  stroke_size_bg=22: moderate background marks — his backgrounds are
            # shallow and compressed, not elaborately detailed deep landscapes.
            # wet_blend=0.28: moderate-low — the dissonant colours must stay separated and individually
            # vivid; too much blending would neutralise the chromatic tension that is the point of the style.
            # edge_softness=0.28: moderate-low — Pontormo's edges are present and readable; not Flemish
            # razor-precision but not sfumato haze either.  Each colour zone is self-contained.
            Period.FLORENTINE_MANNERIST: dict(stroke_size_face=5, stroke_size_bg=22, wet_blend=0.28, edge_softness=0.28),
            # Northern Renaissance (Dürer): engraving-precision oil on pale silver-white panel.
            # stroke_size_face=3: the finest possible marks — Dürer painted individual hairs
            # and fabric threads; each stroke is a deliberate, precise calligraphic touch.
            # stroke_size_bg=16: moderate fine marks — Dürer's backgrounds are carefully
            # observed dark neutral fields, not loose impressionistic washes.
            # wet_blend=0.20: thin transparent oil layers permit limited wet blending in
            # flesh halftones, but there is no wet-into-wet fusion — forms stay precise.
            # edge_softness=0.18: very crisp — Dürer's engraving background makes every
            # edge a drawn line, not the edge of a tonal gradient.  No sfumato haze.
            Period.NORTHERN_RENAISSANCE: dict(stroke_size_face=3, stroke_size_bg=16, wet_blend=0.20, edge_softness=0.18),
            # Quattrocento (Fra Angelico): egg-tempera on chalk-white gesso panel.
            # stroke_size_face=3: the finest hatching strokes — tempera requires the brush
            # to be nearly dry, so each mark is a precise calligraphic hair-width stroke.
            # Form is built by increasing hatch density, not by blending.
            # stroke_size_bg=14: moderate — architectural niches and celestial backgrounds
            # are also rendered with fine tempera marks, not loose washes; gold-leaf areas
            # bypass the stroke system entirely (applied as a glaze pass).
            # wet_blend=0.04: almost zero — egg tempera dries in seconds on gesso; each
            # hatch layer must dry before the next is applied.  Form emerges from layering,
            # never from wet-on-wet mixing.
            # edge_softness=0.15: crisp, present outlines — the Gothic-influenced contour
            # line defines every figure; no sfumato; edges are drawn, not tonal gradients.
            Period.QUATTROCENTO:  dict(stroke_size_face=3, stroke_size_bg=14, wet_blend=0.04, edge_softness=0.15),
            # French Classical (Poussin): deliberate, considered brushwork — no impasto, no alla prima.
            # stroke_size_face=7: precise medium marks — Poussin modelled his figures with patient,
            # controlled strokes rather than the broad confident passes of Baroque or Impressionist
            # painting.  stroke_size_bg=24: moderate background strokes — his Arcadian landscapes
            # are carefully constructed, not loosely indicated.
            # wet_blend=0.38: moderate — Poussin layered deliberately; each passage dried before the
            # next, giving a cool, sober surface rather than the fluid warmth of wet-on-wet Baroque.
            # edge_softness=0.42: clear, legible Classical boundaries — forms read as rational sculpture;
            # no sfumato haze, no razor Tenebrist knife-edge; edges are present and considered.
            Period.FRENCH_CLASSICAL: dict(stroke_size_face=7, stroke_size_bg=24, wet_blend=0.38, edge_softness=0.42),
            # French Court Baroque (Rigaud): sumptuous formal portraiture with deep velvet and silk.
            # stroke_size_face=6: precise, careful modelling — Rigaud built up faces with smooth
            # deliberate strokes that leave a porcelain-like finish beneath the courtly grandeur.
            # stroke_size_bg=22: architectural backgrounds (columns, curtains, distant vistas) were
            # painted with controlled, measured marks — formal and stable, not gestural.
            # wet_blend=0.32: moderate — Rigaud worked in careful layers; velvet requires distinct
            # passages of dark, mid, and highlight tones rather than wet-into-wet dissolution.
            # edge_softness=0.38: moderate crispness — silk shimmers with found edges; velvet and
            # ermine have softer transitions; drapery edges are more defined than Baroque sfumato.
            Period.FRENCH_COURT_BAROQUE: dict(stroke_size_face=6, stroke_size_bg=22, wet_blend=0.32, edge_softness=0.38),
            # Rococo Portrait (Gainsborough): feathery, fluid British portraiture on a pale grey ground.
            # stroke_size_face=8: medium-large marks — Gainsborough worked boldly and swiftly with long
            # flexible brushes, covering large areas in a single pass rather than building up with many
            # small strokes.  stroke_size_bg=28: the atmospheric landscape backgrounds are painted with
            # wide, sweeping washes of thin oil.
            # wet_blend=0.55: moderate-high — the defining feathery quality comes from wet-into-wet
            # blending at stroke tips; each feathered mark blends slightly into the preceding layer.
            # edge_softness=0.68: high — Gainsborough's figures dissolve into their backgrounds;
            # the edge of a shoulder or powdered wig merges with the sky in a cool atmospheric haze.
            Period.ROCOCO_PORTRAIT: dict(stroke_size_face=8,  stroke_size_bg=28, wet_blend=0.55, edge_softness=0.68),
            # American Marine (Homer): near-white gessoed ground with decisive confident
            # strokes.  stroke_size_face=9: medium marks — Homer's brushwork was
            # assured and moderately broad, not fussy Flemish micro-detail.
            # stroke_size_bg=26: broad sweeping passes for sea and sky (horizontal thirds).
            # wet_blend=0.30: moderate — strokes are placed and left; limited wet-into-wet
            # in the sea surface, more separate in the sky and foreground figures.
            # edge_softness=0.35: present, decisive edges — marine silhouettes and
            # the horizon line are crisp; only far atmospheric distance softens.
            Period.AMERICAN_MARINE: dict(stroke_size_face=9, stroke_size_bg=26, wet_blend=0.30, edge_softness=0.35),
            # French Rococo (Fragonard): bravura oil on a warm cream-ivory ground.
            # stroke_size_face=10: large, confident marks — Fragonard's swift loaded brush
            # covered broad areas in single sweeping passes, creating the gestural,
            # spontaneous surface that defines bravura painting.  stroke_size_bg=32: loose,
            # expressive garden and landscape backgrounds rendered with open, airy sweeps.
            # wet_blend=0.62: fluid, spontaneous application — paint stays workable; Fragonard
            # often worked alla prima in a single sitting, blending wet-into-wet throughout.
            # edge_softness=0.52: edges are present but softened at their tips — more spirited
            # and less dissolved than Gainsborough (0.68); the bravura stroke has a clear
            # direction and body, with feathering only at the tapered end.
            Period.FRENCH_ROCOCO: dict(stroke_size_face=10, stroke_size_bg=32, wet_blend=0.62, edge_softness=0.52),
            # French Impressionism (Renoir): warm pale-ivory ground with feathery curving strokes.
            # stroke_size_face=8: medium marks — Renoir's brushwork was lively and surface-following,
            # neither fussy Flemish micro-detail nor Fragonard's bold sweep.  stroke_size_bg=22: loose,
            # impressionistic garden/landscape backgrounds with open, dappled dabs.
            # wet_blend=0.55: moderate — strokes blend at their tips into the preceding wet layer;
            # Renoir built colour by laying warm strokes adjacent and slightly overlapping,
            # producing a vibrant optical mixture rather than physical paint mixing.
            # edge_softness=0.48: moderate — figures are readable (not dissolved), but contours
            # soften gently, especially where dappled garden light breaks up the boundary.
            Period.FRENCH_IMPRESSIONIST: dict(stroke_size_face=8, stroke_size_bg=22, wet_blend=0.55, edge_softness=0.48),
            # Nordic Expressionist (Munch): emotionally charged marks on a dark ground.
            # stroke_size_face=9: medium-large marks — Munch's portraiture used bold,
            # energetic strokes that follow form but dissolve into background anxiety.
            # stroke_size_bg=28: wide swirling background strokes carry the emotional
            # weight — the landscape churns with the same psychological energy as the figure.
            # wet_blend=0.45: moderate — paint blends enough for atmospheric continuity
            # but strokes remain visible and directional, carrying the sinuous Munch line.
            # edge_softness=0.38: moderate — figures are readable but edges dissolve into
            # the swirling background, figure and landscape sharing the same psychic turbulence.
            Period.NORDIC_EXPRESSIONIST: dict(stroke_size_face=9, stroke_size_bg=28, wet_blend=0.45, edge_softness=0.38),
            # Dutch Golden Age (Frans Hals): bravura alla prima portraiture on a warm straw ground.
            # stroke_size_face=8: medium-confident marks — Hals's primary figure stroke was broad
            # and decisive, placed in a single loaded application and left.  stroke_size_bg=24:
            # moderate background strokes; Hals's backgrounds are loosely indicated dark fields,
            # not sfumatoed or elaborately worked.
            # wet_blend=0.14: very low — this is the definitive alla prima setting; strokes are
            # set down and left without wet-into-wet fusion.  The broken tone comes from value
            # contrast between adjacent strokes, not from blending.
            # edge_softness=0.18: crisp, directional edges — each stroke has a clear start and
            # finish; no sfumato dissolving; the edge IS the stroke itself.
            Period.DUTCH_GOLDEN_AGE: dict(stroke_size_face=8, stroke_size_bg=24, wet_blend=0.14, edge_softness=0.18),
            # Danish Intimisme (Hammershøi): near-monochrome interiors on a cool silver-ash ground.
            # stroke_size_face=4: Hammershøi's faces are built from extraordinarily fine, seamless
            # strokes — the marks are invisible; the surface reads as a continuous tone, not individual
            # brushwork.  stroke_size_bg=18: backgrounds are equally smooth — no visible marks.
            # wet_blend=0.75: extremely high — the highest in the catalog.  Every stroke is immediately
            # blended into the wet surface beside it; this is the source of the seamless tonal unity.
            # edge_softness=0.72: very high — all edges dissolve softly; even the figure-background
            # boundary is a gradual tone transition, not a line.  The silence of the image lives here.
            Period.DANISH_INTIMISTE: dict(stroke_size_face=4, stroke_size_bg=18, wet_blend=0.75, edge_softness=0.72),
            # Venetian Mannerist (Tintoretto): furious impasto on a near-black Venetian ground.
            # stroke_size_face=10: bold, gestural face strokes — Tintoretto's alla prima impasto
            # is thick and rapid; marks are large and slashing, not fussy.  stroke_size_bg=35:
            # very large background strokes — the near-black void needs only a few vast sweeps;
            # detailed background work would contradict the urgent, dramatic character.
            # wet_blend=0.35: moderate — marks are semi-wet and worked into each other at edges
            # but the impasto ridges stay distinct and directional, not dissolved like Titian.
            # edge_softness=0.42: readable edges with some atmospheric quality — figures are
            # legible against the dark ground but not Flemish-crisp; a slight Venetian atmospheric
            # softness keeps the transition between figure and void dramatic rather than surgical.
            Period.VENETIAN_MANNERIST: dict(stroke_size_face=10, stroke_size_bg=35, wet_blend=0.35, edge_softness=0.42),
            # Venetian Colorism (Veronese): luminous, clear-toned palette with confident impasto
            # highlights and brilliant saturated mid-tones.  Unlike Tintoretto's dark drama or
            # Giorgione's tonal softness, Veronese bathed his canvases in even, bright light —
            # architectural settings and elaborate fabrics read with almost decorative clarity.
            # stroke_size_face=9: broad, confident marks — Veronese's flesh is built with assured
            # overlapping strokes, slightly larger than Giorgione's (7) but not Tintoretto's
            # violent impasto (10).  stroke_size_bg=28: moderate — his architectural backgrounds
            # require legible structure, not Tintoretto's gestural near-black void sweeps.
            # wet_blend=0.48: moderate — forms are built with some wet-into-wet blending but
            # edges remain clearer than Giorgione's (0.62) tonal pooling; Veronese's paint
            # surface has a decisive, fresh quality.
            # edge_softness=0.40: crisper than Giorgione (0.72) — Veronese's edges are confident
            # and defined; his figures stand in light rather than dissolving into atmosphere.
            Period.VENETIAN_COLORIST:  dict(stroke_size_face=9,  stroke_size_bg=28, wet_blend=0.48, edge_softness=0.40),
            # SPANISH_BAROQUE (Murillo) — estilo vaporoso: highly blended, vaporous soft edges.
            # stroke_size_face=6: moderate detail (not Northern micro-precision, not loose Impressionism)
            # wet_blend=0.65: high blending — Murillo's warm vaporous transitions require it
            # edge_softness=0.70: near-sfumato softness, but warmer and more tender than Leonardo's cool smoke
            Period.SPANISH_BAROQUE:    dict(stroke_size_face=6,  stroke_size_bg=28, wet_blend=0.65, edge_softness=0.74),
            # VENETIAN_ROCOCO (Tiepolo) — celestial overhead light, high aerial luminosity.
            # stroke_size_face=9: confident Venetian wet-into-wet broad marks — not as tight
            #   as Renaissance masters but more refined than Impressionist dabs.
            # stroke_size_bg=34: Tiepolo's vast ceiling skies need very large, sweeping strokes
            #   to achieve the atmospheric aerial depth that characterises his compositions.
            # wet_blend=0.68: high — the Venetian tradition of painting into a moist ground;
            #   colour zones flow into each other to create the warm-to-cool flesh transitions.
            # edge_softness=0.52: moderate — forms are clear and readable (unlike sfumato)
            #   but softened by the aerial luminosity that permeates his compositions.
            Period.VENETIAN_ROCOCO:    dict(stroke_size_face=9,  stroke_size_bg=34, wet_blend=0.68, edge_softness=0.52),
            # BARBIZON (Corot) — silvery atmospheric: high wet_blend for soft tonal transitions,
            # high edge_softness for the dissolved, misty quality of foliage against sky.
            # stroke_size_bg=36: large landscape strokes for the feathery silvery foliage masses.
            Period.BARBIZON:      dict(stroke_size_face=7,  stroke_size_bg=36, wet_blend=0.70, edge_softness=0.78),
            # VEDUTISMO (Canaletto) — crisp architectural precision: low wet_blend for clear-cut stone edges,
            # very low edge_softness for defined architectural forms, small stroke for fine detail
            Period.VEDUTISMO:     dict(stroke_size_face=4,  stroke_size_bg=14, wet_blend=0.20, edge_softness=0.18),
            # PADUAN_RENAISSANCE (Mantegna) — cold sculptural precision: very low wet_blend
            # for the engraved, stone-like clarity of his forms; low edge_softness for
            # the archaeological crispness that distinguishes him from Leonardo's sfumato.
            Period.PADUAN_RENAISSANCE: dict(stroke_size_face=4, stroke_size_bg=16, wet_blend=0.12, edge_softness=0.20),
            # CLASSICAL_LANDSCAPE (Claude Lorrain) — golden atmospheric dissolution:
            # high wet_blend for the soft contre-jour horizon glow that melts sky into water;
            # high edge_softness for the atmospheric haze that dissolves distant forms;
            # large stroke_size_bg for the broad luminous sweeps of sky and far landscape.
            Period.CLASSICAL_LANDSCAPE: dict(stroke_size_face=7, stroke_size_bg=32, wet_blend=0.72, edge_softness=0.75),
            # FRENCH_NEOCLASSICAL (David) — heroic civic clarity: moderate wet_blend for smooth
            # luminous flesh without heavy glazing; moderate edge_softness for crisp classical
            # contours that are clear but not as hard as engraving; large bg strokes for cool
            # architectural stone backgrounds.
            Period.FRENCH_NEOCLASSICAL: dict(stroke_size_face=5, stroke_size_bg=20, wet_blend=0.25, edge_softness=0.32),
            # BOLOGNESE_BAROQUE (Guido Reni) — alabaster pearl softness: high wet_blend for
            # the silken blending that gives Reni's skin its angelic, sculptural luminosity;
            # moderate edge_softness — softer than David's crisp line but crisper than Leonardo;
            # fine stroke_size_face for the meticulous attention to delicate facial modelling.
            Period.BOLOGNESE_BAROQUE: dict(stroke_size_face=5, stroke_size_bg=22, wet_blend=0.62, edge_softness=0.55),
            # PARMA_RENAISSANCE (Correggio) — golden proto-Baroque tenderness: the highest
            # wet_blend in the catalog (0.72) for the Correggesque melting transitions where
            # forms dissolve into each other without any visible boundary; very high
            # edge_softness (0.68) for the proto-sfumato that anticipates the Baroque tradition;
            # fine stroke_size_face to build the extraordinary delicacy of his flesh glazing.
            Period.PARMA_RENAISSANCE: dict(stroke_size_face=5, stroke_size_bg=22, wet_blend=0.72, edge_softness=0.68),
            # FETE_GALANTE (Watteau) — crepuscular autumnal reverie: moderate wet_blend for
            # Watteau's fluid but directional brushwork; higher edge_softness than Fragonard
            # for the dreamy midtone dissolution of his fête galante backgrounds; moderate
            # stroke_size_face to build the delicate, warm-ground flesh tone.
            Period.FETE_GALANTE:  dict(stroke_size_face=7, stroke_size_bg=28, wet_blend=0.58, edge_softness=0.60),
            # LOMBARD_RENAISSANCE (Anguissola) — warm Lombard psychological portraiture:
            # high wet_blend (0.72) for the seamless Lombard skin transitions and warm
            # ambient light that was her signature achievement; moderate-to-high edge_softness
            # (0.68) for Lombard warmth without Leonardo's extreme sfumato dissolution;
            # fine stroke_size_face for the meticulous Lombard observation of facial detail.
            Period.LOMBARD_RENAISSANCE: dict(stroke_size_face=6, stroke_size_bg=24, wet_blend=0.72, edge_softness=0.68),
            # NORTHERN_FANTASTICAL (Bosch) — dark Brabantine ground with intricate symbolic texture.
            # stroke_size_face=4: fine, detail-oriented marks — Bosch's figures are rendered with
            # extraordinary fine-mark density; flesh forms are built with precise, small touches over
            # dark oak panel gesso.  stroke_size_bg=12: small background marks — unlike the broad
            # sweeping background of a Baroque void, Bosch's backgrounds teem with minute symbolic
            # detail that demands fine brushwork even in far-field areas.
            # wet_blend=0.35: moderate blending — Bosch worked in transparent oil over white chalk
            # gesso; forms are blended enough to model volume but edges remain legible and crisp.
            # edge_softness=0.30: moderate crispness — forms are clearly delineated against the dark
            # ground; the jewel-toned accents need clean edges to read as separate symbolic objects.
            Period.NORTHERN_FANTASTICAL: dict(stroke_size_face=4, stroke_size_bg=12, wet_blend=0.35, edge_softness=0.30),
            # DUTCH_DOMESTIC (de Hooch) — precise domestic interior painting.
            # stroke_size_face=5: careful modelling of figures in warm interior light — more
            # deliberate than Hals's bravura alla prima but less fine than Van Eyck's panel work.
            # stroke_size_bg=18: architectural backgrounds (tiles, walls, doorframes) painted with
            # measured regularity — larger than face marks but still precise.
            # wet_blend=0.20: low wet-blend — de Hooch's surfaces are smooth but not fluid; forms
            # are clearly separated rather than melted together; each light zone has a clean identity.
            # edge_softness=0.55: moderate — the threshold between warm interior and cool exterior
            # light creates soft value transitions at doorways, but hard edges on architecture.
            Period.DUTCH_DOMESTIC: dict(stroke_size_face=5, stroke_size_bg=18, wet_blend=0.20, edge_softness=0.55),
            # DUTCH_GENRE_COMEDY (Jan Steen) — lively genre painting with warm imprimatura vitality.
            # stroke_size_face=8: confident directional strokes — more vigorous than de Hooch's precision;
            # Steen worked quickly and energetically, building flesh with assertive loaded-brush marks.
            # stroke_size_bg=28: broad energetic background coverage; genre scenes are crowded, so
            # background elements are painted efficiently with larger, expressive marks.
            # wet_blend=0.40: moderate wet-on-wet — enough to soften flesh edges but not dissolved;
            # Steen achieves warmth through color choice and ground, not through deep sfumato blending.
            # edge_softness=0.45: moderate edges — clothing and props are fairly crisp, faces are softer.
            Period.DUTCH_GENRE_COMEDY: dict(stroke_size_face=8, stroke_size_bg=28, wet_blend=0.40, edge_softness=0.45),
            # VENETIAN_PSYCHOLOGICAL (Lotto) — cool, psychologically tense portraiture.
            # stroke_size_face=5: careful, observational portrait marks — Lotto was meticulous
            # about facial expression and detail; smaller than genre but larger than van Eyck.
            # stroke_size_bg=20: Lotto's backgrounds range from plain dark to complex interiors;
            # medium mark size for the architectural/landscape elements.
            # wet_blend=0.45: moderate blending — smooth enough for Venetian flesh but with
            # less warm dissolution than Titian; keeps a slight edge tension in the face.
            # edge_softness=0.48: slightly more defined than classic sfumato — Lotto's edges
            # have a psychological crispness even when the overall tonality is atmospheric.
            Period.VENETIAN_PSYCHOLOGICAL: dict(stroke_size_face=5, stroke_size_bg=20, wet_blend=0.45, edge_softness=0.48),
            # FLORENTINE_HIGH_RENAISSANCE (del Sarto) — 'faultless' warm golden sfumato.
            # stroke_size_face=5: meticulous Florentine skin observation — fine marks that
            # build seamless tonal transitions in the Leonardo-adjacent tradition.
            # stroke_size_bg=22: moderate landscape strokes; del Sarto's backgrounds are
            # warmer and more defined than Leonardo's cool void but still atmospheric.
            # wet_blend=0.65: high — the hallmark seamless Florentine transitions where
            # form dissolves into form without visible seam; higher than Lotto's tension.
            # edge_softness=0.62: high sfumato, warmer and more grounded than Leonardo's
            # full dissolution (0.80+), but clearly in the Florentine sfumato tradition.
            Period.FLORENTINE_HIGH_RENAISSANCE: dict(stroke_size_face=5, stroke_size_bg=22, wet_blend=0.65, edge_softness=0.62),
            # FRENCH_INTIMISTE (Chardin) — granular optical texture, muted atmospheric warmth.
            # stroke_size_face=5: small, careful dabs; Chardin's intimacy lives in the mark scale.
            # stroke_size_bg=18: moderate backgrounds; quieter than Flemish panoramas.
            # wet_blend=0.22: low — Chardin's granular dabs stay distinct; optical mixing
            # happens on the retina, not by blending on the palette. This is the defining
            # difference from sfumato-tradition painters.
            # edge_softness=0.56: moderate-soft; form is legible through the grain but never harsh.
            Period.FRENCH_INTIMISTE: dict(stroke_size_face=5, stroke_size_bg=18, wet_blend=0.22, edge_softness=0.56),
            # FRENCH_ROMANTIC (Géricault) — turbulent impasto drama, warm near-black shadows.
            # stroke_size_face=10: Géricault worked with vigorous, directional marks; larger than
            # the intimate painters but smaller than Baroque panoramists.
            # stroke_size_bg=30: broad, turbulent background strokes — the storm and chaos of nature.
            # wet_blend=0.68: high — wet-on-wet impasto; forms merge at their edges in the dark
            # passages, then erupt into sudden sharp light (the Romantic chiaroscuro).
            # edge_softness=0.72: moderate-high — Géricault's transitions are not sfumato
            # (too slow, too gentle) but neither are they Baroque hard cuts; they are *turbulent*
            # — forms dissolve through dynamic motion rather than quiet atmospheric haze.
            Period.FRENCH_ROMANTIC: dict(stroke_size_face=10, stroke_size_bg=30, wet_blend=0.68, edge_softness=0.72),
            # UMBRIAN_RENAISSANCE (Signorelli) — muscular sculptural authority, clear contours.
            # stroke_size_face=7: precise, form-following marks — larger than the miniaturists
            # but tighter than the Baroque panoramists; each stroke describes a muscle plane.
            # stroke_size_bg=26: confident background strokes — the Umbrian landscape is not
            # Perugino's gentle aerial haze but a more substantial, geological terrain.
            # wet_blend=0.52: moderate blending within each plane, firm edges between planes —
            # Signorelli's surfaces are smooth but not sfumato-dissolved.
            # edge_softness=0.28: deliberately low — Signorelli's contour clarity is his
            # defining artistic quality; his edges describe anatomical planes, not atmospheric haze.
            Period.UMBRIAN_RENAISSANCE: dict(stroke_size_face=7, stroke_size_bg=26, wet_blend=0.52, edge_softness=0.28),
            # VENETIAN_PASTEL_PORTRAIT (Rosalba Carriera) — feathery luminous pastel glow.
            # stroke_size_face=4: very fine — pastel portraiture is built up in delicate,
            # almost imperceptible layers; each stroke is a whisper of colour rather than a
            # bold mark; the finest details of the face are resolved in tiny, powdery touches.
            # stroke_size_bg=18: intimate background — Carriera's backgrounds are simple, neutral
            # tones with no landscape complexity; the focus is entirely on the face.
            # wet_blend=0.88: very high — pastel blended with fingers and tortillons creates an
            # almost seamless chromatic fusion; no visible marks in the flesh zones.
            # edge_softness=0.90: very high — Carriera's faces dissolve at their edges into
            # soft vignette halos; the powdery medium erases all hard contours.
            Period.VENETIAN_PASTEL_PORTRAIT: dict(stroke_size_face=4, stroke_size_bg=18, wet_blend=0.88, edge_softness=0.90),
            # wet_blend=0.72: Whistler's "sauce" — heavily turpentine-diluted paint creates
            # liquid, blended tonal zones rather than visible marks.
            # edge_softness=0.80: very high — forms dissolve into atmosphericbackgrounds,
            # peripheral regions especially; the Nocturnes are almost edgeless.
            Period.AMERICAN_TONALIST: dict(stroke_size_face=4, stroke_size_bg=22, wet_blend=0.72, edge_softness=0.80),
            Period.BELGIAN_SYMBOLIST: dict(stroke_size_face=3, stroke_size_bg=18, wet_blend=0.22, edge_softness=0.18),
            # stroke_size_face=5: Caillebotte's controlled, precise mark-making — realistic flesh,
            # no impressionistic smear; stroke_size_bg=14: architectural precision in backgrounds.
            # wet_blend=0.18: moderate realism, not impressionistic blending.
            # edge_softness=0.25: crisp edges for architectural geometry and perspective lines.
            Period.PARISIAN_REALIST: dict(stroke_size_face=5, stroke_size_bg=14, wet_blend=0.18, edge_softness=0.25),
            # DER_BLAUE_REITER (Franz Marc / Kandinsky) — prismatic spiritual primaries, bold simplified forms.
            # stroke_size_face=6: confident, clean strokes — Marc's animal forms are bold, each mark
            # defines a clear bounded plane of pure colour rather than a subtle tonal transition.
            # stroke_size_bg=22: landscape resolved in strong planes — Alpine ridges and meadows are
            # geometric colour bands; no impressionist flicker, no sfumato dissolution.
            # wet_blend=0.28: low-moderate; adjacent colour planes retain their individual identity
            # rather than blending; the chromatic contrast between blue/yellow/red is the subject.
            # edge_softness=0.32: low-moderate; clear form boundaries with just enough softening at
            # the very edge to avoid woodcut harshness; the colour does the modelling, not the edge.
            Period.DER_BLAUE_REITER: dict(stroke_size_face=6, stroke_size_bg=22, wet_blend=0.28, edge_softness=0.32),
            # SICILIAN_RENAISSANCE (Antonello da Messina) — Flemish precision fused with Italian warmth.
            # stroke_size_face=3: Flemish micro-detail quality; Antonello's flesh is rendered with the
            # same meticulous oil-glazing patience as van Eyck, not the gestural alla prima of Titian.
            # stroke_size_bg=16: backgrounds are crisp and receding — Antonello's portraits often show
            # Flemish-style architectural niches or landscapes through arched windows, carefully defined.
            # wet_blend=0.55: moderate-high blending — oil glazing produces smooth transitions between
            # layers; no visible impasto, but the surface is not as seamlessly finished as Bouguereau.
            # edge_softness=0.38: found-edge Flemish precision — not sfumato's atmospheric smoke, but
            # edges are resolved rather than hardened; the contour of the face is clear but breathing.
            Period.SICILIAN_RENAISSANCE: dict(stroke_size_face=3, stroke_size_bg=16, wet_blend=0.55, edge_softness=0.38),
            # FLEMISH_LATE_GOTHIC (Hugo van der Goes) — fine Flemish precision with earthy weight.
            # stroke_size_face=3: micro-detail control; van der Goes rendered individual hairs and
            # pores with the same Flemish discipline as van Eyck.
            # stroke_size_bg=18: deep warm-brown backgrounds with atmospheric but clearly defined forms.
            # wet_blend=0.42: moderate oil blending — smooth flesh transitions, but less glazed
            # than van Eyck; Hugo's paint is richer and more opaque in the shadow zones.
            # edge_softness=0.32: Flemish precision edges — forms are clearly bounded but not
            # mechanically hard; the contour breathes slightly without dissolving into sfumato.
            Period.FLEMISH_LATE_GOTHIC: dict(stroke_size_face=3, stroke_size_bg=18, wet_blend=0.42, edge_softness=0.32),
            # DUTCH_FIJNSCHILDER (Gerrit Dou) — the most extreme surface fineness in the catalog.
            # stroke_size_face=2: Dou used a magnifying glass; the finest individual strokes of any
            # Dutch Golden Age painter — hair-thin glazes over polished ivory ground.
            # stroke_size_bg=14: niche background spaces are spatially compressed and detailed
            # (stone arch textures, candlelit interiors), requiring fine background strokes.
            # wet_blend=0.82: extreme glazing — 30+ translucent layers blend seamlessly.
            # edge_softness=0.28: edges are crisp and clear (no sfumato), but luminously smooth —
            # the contour of a Dou figure is resolved and precise, never harsh or mechanical.
            Period.DUTCH_FIJNSCHILDER: dict(stroke_size_face=2, stroke_size_bg=14, wet_blend=0.82, edge_softness=0.28),
            # DUTCH_LIGHT_GROUND (Carel Fabritius) — contre-jour on a pale grey ground.
            # stroke_size_face=8: confident, direct brushwork; Fabritius placed strokes
            # with assurance rather than Dou's magnifying-glass refinement or van Eyck's
            # minute layering.  stroke_size_bg=26: pale background sweeps cover large ground
            # areas efficiently — the luminous background is not laboured but open and airy.
            # wet_blend=0.48: moderate — enough for flesh transitions to flow naturally, not
            # so much as to dissolve the confident individual strokes that define his style.
            # edge_softness=0.42: moderate — edges are present and legible; the contre-jour
            # softening comes from the bright ground radiating around forms, not from sfumato
            # blending; the edge itself stays reasonably crisp so the silhouette reads.
            Period.DUTCH_LIGHT_GROUND: dict(stroke_size_face=8, stroke_size_bg=26, wet_blend=0.48, edge_softness=0.42),
            # DUTCH_CANDLELIT_GENRE (Judith Leyster) — lively, candlelit genre warmth.
            # stroke_size_face=9: confident loaded-brush marks; Leyster learned bravura
            # directness from Hals — not the minute fineness of van Eyck or Dou, but
            # assertive, living strokes that capture expression with economy.
            # stroke_size_bg=28: broad, energetic background; genre interiors are built
            # with swift coverage — the background serves the figure, not the other way.
            # wet_blend=0.38: moderate; enough for warm flesh transitions to feel alive,
            # not so much as to dissolve the energetic directness of her brushwork.
            # edge_softness=0.50: moderate — her figures read crisply against the warm
            # brown shadow ground, with soft transitions in the candlelit flesh zones.
            Period.DUTCH_CANDLELIT_GENRE: dict(stroke_size_face=9, stroke_size_bg=28, wet_blend=0.38, edge_softness=0.50),
            # DUTCH_BRAVURA_PORTRAIT (Frans Hals) — alla prima directional energy.
            # stroke_size_face=10: confident, loaded-brush taches — larger than fijnschilder precision;
            # each stroke is placed once, with absolute assurance, never overworked.
            # stroke_size_bg=28: bold background coverage; Hals's backgrounds are dark and broadly
            # handled so attention concentrates on the vivid face.
            # wet_blend=0.14: very low — alla prima means wet-on-wet within a stroke but no
            # deep blending across strokes; edges stay crisply distinct, forms are not melted.
            # edge_softness=0.22: crisp — psychological vivacity lives in clear, direct edges
            # and confident tonal transitions, not sfumato dissolution.
            Period.DUTCH_BRAVURA_PORTRAIT: dict(stroke_size_face=10, stroke_size_bg=28, wet_blend=0.14, edge_softness=0.22),
            # MILANESE_SFUMATO (Bernardino Luini) — Leonardo-school Milanese sfumato.
            # stroke_size_face=4: fine, polished strokes building up a seamless ivory-flesh
            # surface through many thin glazes; not the minute fineness of Dou, but clearly
            # in the Leonardesque tradition of small-scale refinement.
            # stroke_size_bg=20: backgrounds receive broader handling; often warm neutral or
            # landscape distance dissolved in sfumato haze.
            # wet_blend=0.72: high — Luini's surfaces are seamlessly blended, following
            # Leonardo's own multi-glaze sfumato; no visible brushwork on the face.
            # edge_softness=0.78: very soft — edges melt into one another without hard lines,
            # the defining quality of Leonardo's Milan school.
            Period.MILANESE_SFUMATO: dict(stroke_size_face=4, stroke_size_bg=20, wet_blend=0.72, edge_softness=0.78),
            # MILANESE_PEARLED (Giovanni Antonio Boltraffio) — cool pearl sfumato.
            # stroke_size_face=5: Boltraffio's marks are slightly more visible than Luini's
            # obsessive miniaturism — he retains a jewel-like tonal precision rather than
            # Luini's seamless enamel, so a slightly larger face stroke captures his quality.
            # stroke_size_bg=22: moderate-small backgrounds; Boltraffio's settings are
            # simple, often dark or landscape-simple, directing focus entirely to the figure.
            # wet_blend=0.78: high but less extreme than Luini (0.72); surfaces are smooth
            # and finely blended, but with slightly more tonal structure retained.
            # edge_softness=0.82: very high; Boltraffio's sfumato is as extreme as Leonardo's
            # own — edges are thoroughly dissolved into smoke-like transitions.
            Period.MILANESE_PEARLED: dict(stroke_size_face=5, stroke_size_bg=22, wet_blend=0.78, edge_softness=0.82),
            # UMBRIAN_MANNERIST (Federico Barocci) — petal-soft penumbra rose flush.
            # stroke_size_face=5: fine enough for delicate flesh passages (finer than most Italian
            # Mannerists) but not as extreme as Dou or Luini; Barocci's surface is painterly-smooth
            # rather than glass-polished.
            # stroke_size_bg=22: moderate — landscape backgrounds in Barocci are softly rendered but
            # not as atmospheric as Leonardo or Turner.
            # wet_blend=0.68: high — Barocci's multiple warm-cool glaze layers produce seamless
            # transitions, especially in the penumbra zone where his characteristic rose flush lives.
            # edge_softness=0.72: very soft — Barocci's edges dissolve warmly into ambient haze,
            # similar to Leonardo's sfumato but warmer and more colorful.
            Period.UMBRIAN_MANNERIST: dict(stroke_size_face=5, stroke_size_bg=22, wet_blend=0.68, edge_softness=0.72),
            # CHROMATIC_INTIMISME (Bonnard) — medium stroke, low wet-blend to keep
            # warm/cool dabs distinct, moderate edge softness for organic surface.
            Period.CHROMATIC_INTIMISME: dict(stroke_size_face=9, stroke_size_bg=28, wet_blend=0.35, edge_softness=0.42),
            # PROTO_RENAISSANCE (Masaccio) — architectonic directional light modeling.
            # stroke_size_face=8: confident, architectural marks — Masaccio built his
            # fresco forms with broad, assured strokes applied into wet intonaco plaster;
            # not the fine glazing of oil panel, but deliberate tonal planes that
            # describe structural mass.  stroke_size_bg=24: moderate background marks —
            # Masaccio's architectural niches and spare landscapes are painted with the
            # same economy of means as the figures.
            # wet_blend=0.42: moderate — fresco requires swift, decisive mark-making;
            # wet-on-wet blending occurs within each giornata (day's work) but not
            # across dried sections; forms are smooth but not sfumato-dissolved.
            # edge_softness=0.38: relatively crisp — Masaccio's edges are physically
            # present and describe mass; the shadow cast by a nose or chin-plane is
            # a found edge, not an atmospheric gradient.  This is the defining
            # contrast with his Florentine successor Leonardo (edge_softness=0.85).
            Period.PROTO_RENAISSANCE: dict(stroke_size_face=8, stroke_size_bg=24, wet_blend=0.42, edge_softness=0.38),
            # BELLE_EPOQUE (Toulouse-Lautrec) — peinture à l'essence on cardboard.
            # stroke_size_face=6: Lautrec's faces are resolved with confident, graphic marks —
            # not the fine glazing of the Old Masters but the deliberate, calligraphic touch of a
            # draughtsman painting: marks are visible, directional, and purposeful.
            # stroke_size_bg=20: flat-colour backgrounds — influenced by Japonisme, backgrounds
            # are resolved in simple tonal zones, not elaborate depth-recession landscapes.
            # wet_blend=0.08: very low — turpentine-diluted "essence" paint soaks into cardboard
            # and dries immediately; there is no wet-on-wet blending; colours sit beside each
            # other as graphic zones, never fusing into sfumato transitions.
            # edge_softness=0.14: crisp, graphic edges — Lautrec was a draughtsman first; his
            # contours are clear, bold, and specific, never dissolved into atmosphere.
            Period.BELLE_EPOQUE:  dict(stroke_size_face=6,  stroke_size_bg=20, wet_blend=0.08, edge_softness=0.14),
            # VICTORIAN_SOCIAL_REALIST (James Tissot) — academic glazed surface.
            # stroke_size_face=5: Tissot's academic surface finish requires fine,
            # controlled marks — the skin is built up in thin, imperceptible glazes
            # with no visible brushwork at the figure scale; marks are smaller and
            # more controlled than the bravura Baroque tradition.
            # stroke_size_bg=22: backgrounds are painted with moderate marks —
            # Tissot's Thames riverbanks and garden settings are carefully observed
            # but not laboured; the eye is guided firmly toward the figure.
            # wet_blend=0.80: very high — Tissot's academic method requires smooth,
            # seamless flesh transitions built up through multiple wet-on-wet layers;
            # the surface should read as porcelain-smooth in the face and neck.
            # edge_softness=0.62: moderate-high — edges are clear and purposeful
            # (not sfumato-dissolved) but not hard; Tissot's precise contours are
            # softened by the glazing process into found, atmospheric edges.
            Period.VICTORIAN_SOCIAL_REALIST: dict(stroke_size_face=5, stroke_size_bg=22, wet_blend=0.80, edge_softness=0.62),
            # FLORENTINE_DEVOTIONAL_BAROQUE (Carlo Dolci) — obsessively smooth enamel surface.
            # stroke_size_face=4: Dolci built his skin surfaces through dozens of
            # tiny, imperceptible strokes — the smallest face marks in the pipeline,
            # reflecting his infamous slowness (he could spend years on a single face).
            # stroke_size_bg=20: backgrounds are simple, architectural, or near-black —
            # Dolci's devotional panels often place the figure against a dark velvet
            # void or a plain stone setting; the eye should go nowhere else.
            # wet_blend=0.88: extremely high — Dolci's enamel finish requires total
            # wet-on-wet integration; the surface should have no visible mark-making.
            # edge_softness=0.55: moderate — Dolci's edges are soft but purposeful;
            # they are not sfumato-dissolved (Leonardo) nor sharply found (Antonello),
            # but have a glassy, smooth-glass quality: present but not hard.
            Period.FLORENTINE_DEVOTIONAL_BAROQUE: dict(stroke_size_face=4, stroke_size_bg=20, wet_blend=0.88, edge_softness=0.55),
            # NEAPOLITAN_BAROQUE (Luca Giordano) — "Fa Presto": fast, sweeping, dynamic.
            # stroke_size_face=7: Giordano painted rapidly with broad, confident marks —
            # not Dolci's obsessive miniaturism but energetic, large-scale brushwork.
            # stroke_size_bg=34: vast, theatrical background sweeps typical of ceiling frescoes.
            # wet_blend=0.62: moderate-high — his surfaces are rich and blended but retain
            # directional energy, unlike Dolci's seamless enamel.
            # edge_softness=0.48: moderate — Giordano's edges are purposeful and dramatic,
            # neither Caravaggio-hard nor Leonardo-dissolved.
            Period.NEAPOLITAN_BAROQUE: dict(stroke_size_face=7, stroke_size_bg=34, wet_blend=0.62, edge_softness=0.48),
            # SPANISH_NEAPOLITAN_BAROQUE (Jusepe de Ribera) — brutal tenebrism, gritty shadow texture.
            # stroke_size_face=8: Ribera's flesh is modelled with confident, sculptural marks —
            # larger than the Italian academic tradition, reflecting his directness and the
            # physical weight he brings to aged, working-class faces.
            # stroke_size_bg=26: Ribera's backgrounds are near-absolute dark voids, painted
            # with broad, efficient strokes that establish the shadow ground rather than
            # depicting space; they are the dark earth from which lit forms emerge.
            # wet_blend=0.30: low — Ribera's visible brushwork in the shadow zones is a
            # defining technical quality; his darks retain gritty mark energy rather than
            # smoothing into seamless enamel; wet blending is reserved for flesh transitions.
            # edge_softness=0.28: deliberately low — Ribera's chiaroscuro requires hard
            # found edges where light meets shadow; the dramatic silhouette of his lit forms
            # against near-black void depends on edge clarity, not atmospheric softening.
            Period.SPANISH_NEAPOLITAN_BAROQUE: dict(stroke_size_face=8, stroke_size_bg=26, wet_blend=0.30, edge_softness=0.28),
            # BERGAMASQUE_PORTRAIT_REALISM (Giovanni Battista Moroni) — direct naturalism.
            # stroke_size_face=5: Moroni's portraits are built with careful, observational
            # marks — more deliberate than Hals's bravura but less miniaturist than Van Eyck;
            # each stroke describes a specific tonal plane in the face with quiet precision.
            # stroke_size_bg=20: Moroni's backgrounds are simple grey-green architectural
            # surfaces or neutral grounds, painted efficiently to direct focus to the sitter.
            # wet_blend=0.45: moderate — Moroni's surfaces are smooth and convincing but
            # not sfumato-dissolved; each tonal zone is clearly defined, giving his sitters
            # their characteristic sense of physical presence and tactile reality.
            # edge_softness=0.40: moderate-crisp — Moroni's edges are present and descriptive;
            # he was a naturalist, not a sfumato painter; contours are found (as in Caravaggio)
            # rather than dissolved (as in Leonardo), giving his sitters their direct gaze quality.
            Period.BERGAMASQUE_PORTRAIT_REALISM: dict(stroke_size_face=5, stroke_size_bg=20, wet_blend=0.45, edge_softness=0.40),
            # GENOESE_VENETIAN_BAROQUE (Bernardo Strozzi) — bravura loaded-brush alla prima.
            # stroke_size_face=7: Strozzi painted with confidence and physical energy;
            # his strokes are larger than Moroni's careful marks, loaded with paint,
            # describing form through bold tonal jumps rather than patient blending.
            # stroke_size_bg=28: Strozzi's backgrounds are broadly handled — warm amber
            # or dark umber grounds that frame the figure without competing with it.
            # wet_blend=0.50: moderate — Strozzi blends where transitions require it,
            # but he is not a sfumato painter; edges are found and assertive, rooted
            # in the Caravaggist tradition he absorbed through Genoese patronage of Rubens.
            # edge_softness=0.38: moderately crisp — his portraits have psychological
            # directness encoded in clear, decisive found edges, especially around
            # the eyes and mouth; periphery may soften slightly but the focal face is sharp.
            Period.GENOESE_VENETIAN_BAROQUE: dict(stroke_size_face=7, stroke_size_bg=28, wet_blend=0.50, edge_softness=0.38),
            # ROMAN_DEVOTIONAL_BAROQUE (Sassoferrato) — patient glazing precision.
            # stroke_size_face=5: tiny careful marks built through repeated glazing passes;
            # Sassoferrato's seamless surface demands fine, controlled application.
            # stroke_size_bg=18: backgrounds are often dark and simple, reduced essentials.
            # wet_blend=0.82: very high — the smooth, seamless glazing of a devotional master
            # who spent days on a single passage to achieve porcelain-smooth skin.
            # edge_softness=0.72: high but not full sfumato — edges are soft and calm,
            # devotionally quiet, but the face outline and mantle boundary remain gently present.
            Period.ROMAN_DEVOTIONAL_BAROQUE: dict(stroke_size_face=5, stroke_size_bg=18, wet_blend=0.82, edge_softness=0.72),
            # ITALO_COURTLY_BAROQUE (Orazio Gentileschi) — cool clear daylight, controlled naturalism.
            # stroke_size_face=6: moderate precision — not the finest sfumato but careful observation.
            # stroke_size_bg=22: backgrounds are often simple dark curtains or open sky — moderate.
            # wet_blend=0.52: controlled blending — smooth enough for ivory flesh, crisp enough for fabric edges.
            # edge_softness=0.48: moderate — softer than Bronzino's enamel, crisper than Leonardo's sfumato.
            Period.ITALO_COURTLY_BAROQUE: dict(stroke_size_face=6, stroke_size_bg=22, wet_blend=0.52, edge_softness=0.48),
            # ANTWERP_BAROQUE (Jacob Jordaens) — earthy loaded-brush vitality, warm imprimatura.
            # stroke_size_face=8: robust brushwork — heavier than Moroni's precision, lighter than Hals' bravura.
            # stroke_size_bg=26: backgrounds are often warm curtains or domestic interiors — moderate-broad.
            # wet_blend=0.38: moderate — alla prima vitality; not Rubens' fluid blending, but vigorous impasto.
            # edge_softness=0.38: moderate-crisp — naturalist found edges, physically grounded.
            Period.ANTWERP_BAROQUE: dict(stroke_size_face=8, stroke_size_bg=26, wet_blend=0.38, edge_softness=0.38),
            # EMILIAN_ROSY_BAROQUE (Guido Cagnacci) — smooth glazed sfumato, dreamlike rose flesh quality.
            # stroke_size_face=5: fine, controlled — smooth Reni-derived sfumato with no visible brushwork.
            # stroke_size_bg=20: backgrounds are simple, unassertive — support the figure's glow.
            # wet_blend=0.78: high blending — glazed, seamless transitions; Reni lineage.
            # edge_softness=0.72: soft diffusion — forms glow and melt without hard boundaries.
            Period.EMILIAN_ROSY_BAROQUE: dict(stroke_size_face=5, stroke_size_bg=20, wet_blend=0.78, edge_softness=0.72),
            # FLORENTINE_MELANCHOLIC_BAROQUE (Francesco Furini) — the most extreme sfumato after Leonardo.
            # stroke_size_face=4: very fine — evanescent, seamless surfaces with no visible mark.
            # stroke_size_bg=18: backgrounds are dark voids; minimal mark required.
            # wet_blend=0.82: highest blending of any Baroque period — approaching Leonardo's sfumato in continuity.
            # edge_softness=0.88: near-full sfumato — forms dissolve into surrounding darkness without edge.
            Period.FLORENTINE_MELANCHOLIC_BAROQUE: dict(stroke_size_face=4, stroke_size_bg=18, wet_blend=0.82, edge_softness=0.88),
            # BOLOGNESE_MANNERIST_PORTRAITURE (Lavinia Fontana) — glazed Bolognese finish, warm costume richness.
            # stroke_size_face=5: fine, controlled — smooth glazed surface, no visible brushwork on flesh.
            # stroke_size_bg=22: backgrounds are warm stone or architecture — moderate mark.
            # wet_blend=0.62: moderate-high blending — glazed but not fully sfumato-dissolved.
            # edge_softness=0.58: moderate-soft — refined Bolognese edges, softer than Bronzino, crisper than Leonardo.
            Period.BOLOGNESE_MANNERIST_PORTRAITURE: dict(stroke_size_face=5, stroke_size_bg=22, wet_blend=0.62, edge_softness=0.58),
            # LOMBARD_LEONARDESQUE (Andrea Solario) — Leonardesque sfumato with Lombard amber warmth + Venetian cool shadows.
            # stroke_size_face=4: very fine marks — smooth pellucid surface, Leonardesque care on flesh.
            # stroke_size_bg=16: narrow background strokes — landscape detail with atmospheric recession.
            # wet_blend=0.78: high blending — very smooth, approaching full Leonardesque sfumato.
            # edge_softness=0.82: near-sfumato — edges dissolve without completely vanishing; Lombard warmth prevents full dissolution.
            Period.LOMBARD_LEONARDESQUE: dict(stroke_size_face=4, stroke_size_bg=16, wet_blend=0.78, edge_softness=0.82),
            # UMBRIAN_CLASSICAL_HARMONY (Pietro Perugino) — serene harmonious warmth, smooth glazed surface, open landscape.
            # stroke_size_face=5: fine marks — smooth but not sfumato-dissolved; Umbrian clarity and finish.
            # stroke_size_bg=20: medium landscape strokes — open, luminous Umbrian plains with gentle recession.
            # wet_blend=0.72: high blending — harmonious smooth surface, no broken-colour or rough impasto.
            # edge_softness=0.65: moderate-high — softened, serene edges, not the extreme of sfumato but clearly soft.
            Period.UMBRIAN_CLASSICAL_HARMONY: dict(stroke_size_face=5, stroke_size_bg=20, wet_blend=0.72, edge_softness=0.65),
            # BRESCIAN_SILVER_NOCTURNE (Giovanni Gerolamo Savoldo) — moonlit silver veil, nocturnal depth, soft atmospheric glow.
            # stroke_size_face=5: fine sfumato-adjacent marks — smooth nocturnal surface, no impasto roughness.
            # stroke_size_bg=18: medium landscape strokes — Venetian-Brescian atmospheric recession in near-darkness.
            # wet_blend=0.70: high blending — Savoldo's seamlessly blended nocturnal surfaces, no visible brushwork.
            # edge_softness=0.78: high — phosphorescent silver edges dissolve softly into darkness; nocturnal atmosphere.
            Period.BRESCIAN_SILVER_NOCTURNE: dict(stroke_size_face=5, stroke_size_bg=18, wet_blend=0.70, edge_softness=0.78),
            # ROMAN_GRAND_TOUR_CLASSICISM (Pompeo Batoni) — warm Classicist flesh, anisotropic silk-sheen streaks, polished Rococo finish.
            # stroke_size_face=5: fine strokes for smooth Roman-Classicist flesh, polished like porcelain.
            # stroke_size_bg=20: medium landscape strokes — classical ruins and antique statuary, precisely rendered.
            # wet_blend=0.55: moderate blending — Batoni's surfaces are polished but retain visible directional energy.
            # edge_softness=0.65: moderate — forms are clearly defined, unlike sfumato masters; clear Neoclassical line.
            Period.ROMAN_GRAND_TOUR_CLASSICISM: dict(stroke_size_face=5, stroke_size_bg=20, wet_blend=0.55, edge_softness=0.65),
            # VENETIAN_ECCENTRIC_PORTRAITURE (Lorenzo Lotto) — psychological intensity, vivid color contrasts, multi-scale chromatic vitality.
            # stroke_size_face=5: fine strokes — detailed psychological portraiture with visible brushwork energy.
            # stroke_size_bg=22: medium landscape/background strokes — Lotto's varied, often eccentric settings.
            # wet_blend=0.45: moderate — surfaces have chromatic energy, not fully blended like Titian.
            # edge_softness=0.52: moderate — psychological acuity; clearer than sfumato masters.
            Period.VENETIAN_ECCENTRIC_PORTRAITURE: dict(stroke_size_face=5, stroke_size_bg=22, wet_blend=0.45, edge_softness=0.52),
            # ITALIAN_BELLE_EPOQUE_PORTRAITURE (Giovanni Boldini) — dual-angle swirl bravura, dark grounds, luminous warm flesh.
            # stroke_size_face=6: medium-fine for flesh — face rendered with more precision than flowing, gestural surroundings.
            # stroke_size_bg=24: loose background strokes — Boldini's backgrounds dissolve into directional gestural energy.
            # wet_blend=0.28: low — loose directional marks, each stroke retaining individual energy; not heavily blended.
            # edge_softness=0.50: moderate — figures emerge softly from dark grounds with luminous edge quality.
            Period.ITALIAN_BELLE_EPOQUE_PORTRAITURE: dict(stroke_size_face=6, stroke_size_bg=24, wet_blend=0.28, edge_softness=0.50),
            # BOLOGNESE_ACADEMIC_NATURALISM (Annibale Carracci) — naturalistic reform, warm-ground clarity, directional temperature field.
            # stroke_size_face=6: moderately fine — direct observation, forms resolved with naturalistic clarity.
            # stroke_size_bg=20: medium background strokes — classical architecture and landscape, clearly rendered.
            # wet_blend=0.55: moderate — naturalistic painting, forms blended but not dissolved (anti-Mannerist clarity).
            # edge_softness=0.55: moderate — clearly defined forms; neither crisp Mannerist line nor sfumato dissolution.
            Period.BOLOGNESE_ACADEMIC_NATURALISM: dict(stroke_size_face=6, stroke_size_bg=20, wet_blend=0.55, edge_softness=0.55),
            # ROMAN_BAROQUE_LANDSCAPE (Salvator Rosa) — gestural turbulence, near-black grounds, storm-charged wilderness.
            # stroke_size_face=10: broad, energetic marks — Rosa's alla-prima bravura favours large,
            # directional strokes that follow the form's energy rather than its contour; no sfumato finesse.
            # stroke_size_bg=36: very large background strokes — vast storm-sky and craggy rock faces
            # painted with sweeping gestural economy; the landscape is always more energetically painted
            # than the figure.
            # wet_blend=0.22: low blending — direction-less gestural marks retain their individual
            # energy; heavy blending would destroy the turbulent surface quality Rosa cultivated.
            # edge_softness=0.38: moderate crispness — agitated, storm-charged edges; not sfumato
            # dissolution, not crisp Velázquez line, but a tense in-between quality.
            Period.ROMAN_BAROQUE_LANDSCAPE: dict(stroke_size_face=10, stroke_size_bg=36, wet_blend=0.22, edge_softness=0.38),
            # NEAPOLITAN_BAROQUE_CLASSICISM (Massimo Stanzione) — Reni-derived classicism grafted onto
            # Neapolitan Baroque. stroke_size_face=6: restrained, classicist mark-making; Bolognese
            # academic discipline applied to Neapolitan warmth. stroke_size_bg=22: moderate background
            # strokes — architectural and devotional settings painted with Reni-adjacent clarity.
            # wet_blend=0.72: smooth blending — Stanzione's flesh surfaces are seamlessly resolved,
            # Reni-influenced; no rough impasto or alla-prima energy. edge_softness=0.68: moderate
            # sfumato — forms clearly defined (anti-Mannerist classicism) but not sharp (sfumato
            # influence from Bolognese academic training via Reni).
            Period.NEAPOLITAN_BAROQUE_CLASSICISM: dict(stroke_size_face=6, stroke_size_bg=22, wet_blend=0.72, edge_softness=0.68),
            Period.CONTEMPORARY:  dict(stroke_size_face=8,  stroke_size_bg=24, wet_blend=0.15, edge_softness=0.50),
            Period.FANTASY_ART:   dict(stroke_size_face=7,  stroke_size_bg=26, wet_blend=0.12, edge_softness=0.55),
            Period.NONE:          dict(stroke_size_face=8,  stroke_size_bg=24, wet_blend=0.18, edge_softness=0.50),
        }
        p = defaults.get(self.period, defaults[Period.NONE]).copy()
        # Apply per-style overrides
        if self.stroke_size_face is not None:  p["stroke_size_face"]  = self.stroke_size_face
        if self.stroke_size_bg   is not None:  p["stroke_size_bg"]    = self.stroke_size_bg
        if self.wet_blend        is not None:  p["wet_blend"]         = self.wet_blend
        if self.edge_softness    is not None:  p["edge_softness"]     = self.edge_softness
        return p


# ─────────────────────────────────────────────────────────────────────────────
# Top-level Scene
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Scene:
    """
    Complete description of a painting to render.

    This object is the contract between:
      - the prompt interpreter (Claude, writing code that assembles a Scene)
      - the Blender scene builder  (consumes Scene → .blend / render)
      - the stroke engine          (consumes Style → painterly pass)

    Nothing in this class is renderer-specific.
    """
    subjects:    List[Character]  = field(default_factory=list)
    camera:      Camera           = field(default_factory=Camera)
    lighting:    LightRig         = field(default_factory=LightRig.three_point_warm)
    environment: Environment      = field(default_factory=Environment)
    style:       Style            = field(default_factory=Style)

    # Output
    width:  int = 780
    height: int = 1080
    title:  str = "untitled"

    def add_subject(self, character: Character) -> Scene:
        self.subjects.append(character)
        return self


# ─────────────────────────────────────────────────────────────────────────────
# Convenience constructors
# ─────────────────────────────────────────────────────────────────────────────

def portrait_scene(
        description: str = "",
        skin_tone: SkinTone = SkinTone.MEDIUM,
        expression: Expression = Expression.NEUTRAL,
        lighting: str = "three_point_warm",
        style: Period = Period.RENAISSANCE,
) -> Scene:
    """Quick constructor for a single-subject portrait."""
    rig_map = {
        "three_point_warm": LightRig.three_point_warm(),
        "rembrandt":        LightRig.rembrandt(),
        "overcast":         LightRig.overcast(),
        "sunset":           LightRig.sunset(),
    }
    return Scene(
        subjects=[Character(
            skin_tone  = skin_tone,
            expression = expression,
            pose       = Pose.SEATED,
            pose_detail= PoseDetail(head_turn=-15.0),   # classic 3/4 turn
        )],
        camera   = Camera(position=Vec3(0, -3.0, 1.55), fov=35),
        lighting = rig_map.get(lighting, LightRig.three_point_warm()),
        environment = Environment(
            type        = EnvType.EXTERIOR,
            description = description or "misty landscape with distant hills",
            atmosphere  = 0.15,
        ),
        style = Style(medium=Medium.OIL, period=style,
                      palette=PaletteHint.WARM_EARTH),
        title = "portrait",
    )
