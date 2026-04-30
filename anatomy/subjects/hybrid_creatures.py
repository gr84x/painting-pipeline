"""
Pre-built hybrid creature anatomies.

Each creature is composed from real animal subjects using the hybrid toolkit.
These are ready to use directly from the registry:

    from anatomy import subjects
    griffin = subjects.get("griffin")

Creatures defined here
----------------------
griffin    — Eagle head/beak/wings + lion mane and feline mass
dragon     — Komodo lizard base + crocodile armour + eagle beak/brow + snake neck
kitsune    — Fox base with owl-large eyes and multiple tails (ear count boosted)
kirin      — Deer base with horse proportions + dragon horns + giraffe coat pattern
"""
from ..hybrid import blend_anatomies, graft_feature_zones, scale_feature_weights, add_landmarks
from ..schema import Landmark, FeatureZone, FlowZone
from . import (
    EAGLE, FALCON, LION, FOX, OWL, DEER, HORSE,
    LIZARD, CROCODILE, SNAKE, GIRAFFE,
)


# ── Griffin (eagle head + lion body) ─────────────────────────────────────────
# Eagle contributes beak, supraorbital, eyes, crown/nape flow.
# Lion contributes mane zone, facial mass, feline cheek flow.

GRIFFIN = blend_anatomies(
    [(EAGLE, 0.65), (LION, 0.35)],
    subject_id="griffin",
    display_name="Griffin (Eagle + Lion)",
)

# Emphasise the eagle beak and supraorbital (the most griffin-like features)
GRIFFIN = scale_feature_weights(GRIFFIN, {
    "beak":         1.5,
    "supraorbital": 1.4,
    "mane":         1.3,   # lion mane zone carries through
})


# ── Dragon (lizard + crocodile armour + eagle beak + snake neck) ──────────────
# Lizard provides the overall reptile body shape and dewlap.
# Crocodile contributes neck scutes and tooth row.
# Eagle contributes the heavy beak and supraorbital.
# Snake adds neck scale flow and the sinuous neck landmarks.

_dragon_base = blend_anatomies(
    [(LIZARD, 0.45), (CROCODILE, 0.35), (EAGLE, 0.20)],
    subject_id="_dragon_base",
    display_name="Dragon Base",
)

DRAGON = blend_anatomies(
    [(_dragon_base, 0.80), (SNAKE, 0.20)],
    subject_id="dragon",
    display_name="Dragon",
)

# Dragon's most important features: eye (reptile slit pupil), armour scutes, beak/horn
DRAGON = scale_feature_weights(DRAGON, {
    "eye":           1.4,
    "neck_scutes":   1.6,
    "beak":          1.3,
    "supraorbital":  1.3,
    "teeth":         1.4,
    "scales":        1.3,
})

# Add dragon-specific landmarks: horn tips and wing root
DRAGON = add_landmarks(DRAGON, [
    Landmark("horn_left",       nx=-0.28, ny=-0.82),
    Landmark("horn_right",      nx=+0.28, ny=-0.82),
    Landmark("wing_root_left",  nx=-0.55, ny=-0.30),
    Landmark("wing_root_right", nx=+0.55, ny=-0.30),
    Landmark("frill_peak",      nx= 0.00, ny=-1.00),   # dorsal frill if present
])

# Boost horn area with a feature zone
DRAGON = graft_feature_zones(DRAGON, additions=[
    FeatureZone("horns", "horn_left",
                radius_nx=0.32, radius_ny=0.26,
                error_weight=4.5, stroke_size_scale=0.50, jitter_scale=0.54),
])


# ── Kitsune (fox + owl eyes + multi-tail suggestion) ──────────────────────────
# Fox provides the overall facial structure, muzzle, ears.
# Owl provides enormous forward-facing eyes and facial-disc flow.
# Eyes are then further scaled up for the supernatural aesthetic.

KITSUNE = blend_anatomies(
    [(FOX, 0.68), (OWL, 0.32)],
    subject_id="kitsune",
    display_name="Kitsune (Fox Spirit)",
)

# Kitsune has supernaturally large eyes and ears
KITSUNE = scale_feature_weights(KITSUNE, {
    "near_eye": 1.6,
    "far_eye":  1.4,
    "ears":     1.3,
    "nose_pad": 0.8,   # soften nose emphasis — spirit foxes look more ethereal
})

# Extra tails suggested via landmark hints (painting interprets as flowing forms)
KITSUNE = add_landmarks(KITSUNE, [
    Landmark("tail_tip_1", nx=+0.88, ny=+0.55),
    Landmark("tail_tip_2", nx=+0.72, ny=+0.72),
    Landmark("tail_tip_3", nx=+0.55, ny=+0.85),
    Landmark("tail_base",  nx=+0.55, ny=+0.30),
])

KITSUNE = graft_feature_zones(KITSUNE, additions=[
    FeatureZone("tails", "tail_base",
                radius_nx=0.55, radius_ny=0.65,
                error_weight=2.5, stroke_size_scale=0.65, jitter_scale=0.70),
])


# ── Kirin / Qilin (deer + horse + giraffe pattern + dragon horns) ─────────────
# Deer contributes the elegant head shape, large eyes, and facial proportions.
# Horse provides the elongated muzzle and strong neck.
# Giraffe contributes the ossicone horns and coat pattern zone.

KIRIN = blend_anatomies(
    [(DEER, 0.50), (HORSE, 0.30), (GIRAFFE, 0.20)],
    subject_id="kirin",
    display_name="Kirin / Qilin",
)

# The kirin's most distinctive painted features: large eyes, pattern, horn
KIRIN = scale_feature_weights(KIRIN, {
    "near_eye":    1.3,
    "far_eye":     1.2,
    "coat_pattern": 1.4,   # giraffe reticulation zone
    "ossicones":   1.5,    # horn stumps
    "muzzle":      0.9,
})

# Add a longer horn suggestion as a landmark
KIRIN = add_landmarks(KIRIN, [
    Landmark("kirin_horn_tip",  nx=+0.08, ny=-1.00),
    Landmark("kirin_horn_base", nx=+0.08, ny=-0.62),
    Landmark("mane_peak",       nx=+0.30, ny=-0.70),
])

KIRIN = graft_feature_zones(KIRIN, additions=[
    FeatureZone("kirin_horn", "kirin_horn_base",
                radius_nx=0.18, radius_ny=0.42,
                error_weight=4.0, stroke_size_scale=0.50, jitter_scale=0.52),
    FeatureZone("kirin_mane", "mane_peak",
                radius_nx=0.35, radius_ny=0.45,
                error_weight=3.0, stroke_size_scale=0.60, jitter_scale=0.65),
])


# ── Registry entries (imported by subjects/__init__.py) ───────────────────────
ALL_HYBRID = [GRIFFIN, DRAGON, KITSUNE, KIRIN]
