"""Subject anatomy registry."""
from .human_portrait import HUMAN_PORTRAIT
from .fox import FOX
from .dog import DOG
from .cat import CAT
from .wolf import WOLF
from .horse import HORSE
from .deer import DEER
from .rabbit import RABBIT
from .bear import BEAR
from .owl import OWL
from .songbird import SONGBIRD
from .raptor import RAPTOR
from .parrot import PARROT
from .heron import HERON
from .raven import RAVEN
from .waterfowl import WATERFOWL
from .falcon_eagle import FALCON, EAGLE
from .fish import FISH_TROPICAL, FISH_ELONGATED
from .octopus import OCTOPUS, SQUID
from .dolphin import DOLPHIN
from .sea_turtle import SEA_TURTLE
from .butterfly import BUTTERFLY, MOTH
from .insects import DRAGONFLY, BEETLE, BEE
from .reptiles import LIZARD, CHAMELEON, SNAKE, CROCODILE
from .large_mammals import LION, GIRAFFE, CHIMPANZEE, BEAVER, PIG
from .hybrid_creatures import GRIFFIN, DRAGON, KITSUNE, KIRIN

REGISTRY: dict = {s.subject_id: s for s in [
    HUMAN_PORTRAIT,
    FOX,
    DOG,
    CAT,
    WOLF,
    HORSE,
    DEER,
    RABBIT,
    BEAR,
    OWL,
    SONGBIRD,
    RAPTOR,
    PARROT,
    HERON,
    RAVEN,
    WATERFOWL,
    FALCON,
    EAGLE,
    FISH_TROPICAL,
    FISH_ELONGATED,
    OCTOPUS,
    SQUID,
    DOLPHIN,
    SEA_TURTLE,
    BUTTERFLY,
    MOTH,
    DRAGONFLY,
    BEETLE,
    BEE,
    LIZARD,
    CHAMELEON,
    SNAKE,
    CROCODILE,
    LION,
    GIRAFFE,
    CHIMPANZEE,
    BEAVER,
    PIG,
    GRIFFIN,
    DRAGON,
    KITSUNE,
    KIRIN,
]}


def get(subject_id: str):
    """Look up a SubjectAnatomy by ID. Raises KeyError if not found."""
    if subject_id not in REGISTRY:
        raise KeyError(
            f"Unknown subject_id {subject_id!r}. "
            f"Available: {sorted(REGISTRY.keys())}"
        )
    return REGISTRY[subject_id]


def list_subjects() -> list[str]:
    """Return all registered subject IDs."""
    return sorted(REGISTRY.keys())
