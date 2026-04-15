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
    FAUVIST       = auto()   # Matisse — maximum saturation, flat zones, complementary shadows, coloured outlines
    PRIMITIVIST   = auto()   # Modigliani — oval mask faces, almond eyes, elongated necks, warm ochre flesh
    EARLY_NETHERLANDISH = auto()  # Jan van Eyck — stacked transparent oil glazes, chalk-white gesso, Flemish micro-detail
    ART_DECO      = auto()   # Tamara de Lempicka — smooth cubist facets, metallic gloss, bold saturated palette
    NABIS         = auto()   # Vuillard / Bonnard — intimate pattern-ground fusion, flat muted zones, figures absorbed into patterned grounds
    LUMINISMO     = auto()   # Sorolla — maximum sunlight, warm/cool simultaneous contrast, dappled light pools
    HIGH_RENAISSANCE = auto()  # Raphael — luminous clarity, radiant warm midtones, idealized form, no heavy sfumato
    TENEBRIST     = auto()   # Zurbarán — near-black void, hyper-real white fabric, razor-sharp found edges
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
