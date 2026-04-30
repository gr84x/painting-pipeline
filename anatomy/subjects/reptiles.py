"""
Reptile anatomy — lizard, chameleon, snake, crocodile.

All side profile unless noted. The key painting challenges differ by species:
  Lizard:     scale texture, dewlap colour, long tail taper
  Chameleon:  granular texture, casque silhouette, independently rotating eyes
  Snake:      scale rows, colour pattern bands, triangular head shape
  Crocodile:  armoured scutes, tooth-studded jaw line, high-set eyes
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy


# ── Lizard (side profile) ─────────────────────────────────────────────────────

LIZARD = SubjectAnatomy(
    subject_id="lizard",
    display_name="Lizard (Side Profile)",
    landmarks=[
        Landmark("eye",             nx=-0.15, ny=-0.20),
        Landmark("pupil",           nx=-0.15, ny=-0.20),
        Landmark("mouth_corner",    nx=-0.65, ny=+0.10),
        Landmark("snout_tip",       nx=-0.80, ny=-0.02),
        Landmark("nostril",         nx=-0.60, ny=-0.10),
        Landmark("upper_jaw",       nx=-0.48, ny=-0.05),
        Landmark("lower_jaw",       nx=-0.45, ny=+0.15),
        Landmark("tympanum",        nx=+0.12, ny=-0.05),   # ear drum
        Landmark("dewlap_base",     nx=-0.20, ny=+0.45),   # throat fan
        Landmark("dewlap_tip",      nx=-0.05, ny=+0.78),
        Landmark("crown",           nx=+0.05, ny=-0.50),
        Landmark("nape",            nx=+0.42, ny=-0.28),
        Landmark("dorsal_crest",    nx=+0.20, ny=-0.62),   # if present
        Landmark("neck_base",       nx=+0.55, ny=+0.10),
    ],
    feature_zones=[
        FeatureZone("eye",      "eye",          radius_nx=0.16, radius_ny=0.14,
                    error_weight=9.0, stroke_size_scale=0.44, jitter_scale=0.48, wet_blend_scale=0.44),
        FeatureZone("mouth",    "mouth_corner", radius_nx=0.42, radius_ny=0.14,
                    error_weight=4.5, stroke_size_scale=0.52),
        FeatureZone("dewlap",   "dewlap_base",  radius_nx=0.28, radius_ny=0.38,
                    error_weight=4.0, stroke_size_scale=0.55),
        FeatureZone("tympanum", "tympanum",     radius_nx=0.16, radius_ny=0.14,
                    error_weight=3.0, stroke_size_scale=0.52),
        FeatureZone("scales",   "upper_jaw",    radius_nx=0.55, radius_ny=0.55,
                    error_weight=2.5, stroke_size_scale=0.58),
    ],
    flow_zones=[
        FlowZone("eye_socket", "orbital",
                 {"orbit_anchor": "eye", "orbit_nx": -0.15, "orbit_ny": -0.20},
                 weight_sigma_nx=0.16, weight_sigma_ny=0.14),
        FlowZone("jaw", "fixed", {"radians": 0.04, "anchor_nx": -0.45, "anchor_ny": 0.04},
                 weight_sigma_nx=0.38, weight_sigma_ny=0.16),
        FlowZone("body_scales", "diagonal",
                 {"nx_factor": 0.65, "ny_factor": 0.28, "anchor_nx": +0.25, "anchor_ny": 0.00},
                 weight_sigma_nx=0.45, weight_sigma_ny=0.48),
        FlowZone("dewlap", "diagonal",
                 {"nx_factor": -0.10, "ny_factor": 0.95, "anchor_nx": -0.12, "anchor_ny": +0.58},
                 weight_sigma_nx=0.24, weight_sigma_ny=0.38),
        FlowZone("crown", "diagonal",
                 {"nx_factor": 0.45, "ny_factor": -0.20, "anchor_nx": +0.08, "anchor_ny": -0.45},
                 weight_sigma_nx=0.35, weight_sigma_ny=0.22),
    ],
    proportions={"snout_length_fraction": 0.48, "eye_diameter_fraction": 0.14, "aspect_ratio": 1.40},
)


# ── Chameleon (side profile) ──────────────────────────────────────────────────

CHAMELEON = SubjectAnatomy(
    subject_id="chameleon",
    display_name="Chameleon (Side Profile)",
    landmarks=[
        Landmark("eye",             nx=-0.08, ny=-0.15),    # cone-shaped, rotates independently
        Landmark("casque_tip",      nx=+0.45, ny=-0.65),    # the helmet crest
        Landmark("casque_base",     nx=+0.30, ny=-0.48),
        Landmark("snout_tip",       nx=-0.72, ny=-0.08),
        Landmark("rostral_horn",    nx=-0.62, ny=-0.18),    # if present
        Landmark("mouth_corner",    nx=-0.40, ny=+0.12),
        Landmark("nostril",         nx=-0.55, ny=-0.12),
        Landmark("throat",          nx=+0.02, ny=+0.38),
        Landmark("dorsal_crest_peak",nx=+0.05,ny=-0.72),
        Landmark("body_centre",     nx=+0.20, ny= 0.00),
        Landmark("foot",            nx=+0.02, ny=+0.58),    # zygodactyl grip
        Landmark("tail_base",       nx=+0.55, ny=+0.18),
    ],
    feature_zones=[
        # The chameleon eye is extraordinary — bulging conical turret, tiny pupil
        FeatureZone("eye",        "eye",          radius_nx=0.22, radius_ny=0.20,
                    error_weight=10.0, stroke_size_scale=0.40, jitter_scale=0.44, wet_blend_scale=0.40),
        FeatureZone("casque",     "casque_tip",   radius_nx=0.30, radius_ny=0.32,
                    error_weight=4.5, stroke_size_scale=0.52),
        FeatureZone("mouth",      "mouth_corner", radius_nx=0.30, radius_ny=0.14,
                    error_weight=4.0, stroke_size_scale=0.55),
        FeatureZone("dorsal_crest","dorsal_crest_peak",radius_nx=0.20,radius_ny=0.30,
                    error_weight=3.5, stroke_size_scale=0.52),
        # Colour patches — chameleons show bold colour zones under emotional states
        FeatureZone("body_colour","body_centre",  radius_nx=0.55, radius_ny=0.55,
                    error_weight=3.0, stroke_size_scale=0.60),
        FeatureZone("foot",       "foot",         radius_nx=0.22, radius_ny=0.18,
                    error_weight=3.0, stroke_size_scale=0.48),
    ],
    flow_zones=[
        FlowZone("eye_socket", "orbital",
                 {"orbit_anchor": "eye", "orbit_nx": -0.08, "orbit_ny": -0.15},
                 weight_sigma_nx=0.20, weight_sigma_ny=0.18),
        FlowZone("casque", "diagonal",
                 {"nx_factor": 0.35, "ny_factor": -0.85, "anchor_nx": +0.38, "anchor_ny": -0.55},
                 weight_sigma_nx=0.28, weight_sigma_ny=0.30),
        FlowZone("body_granules", "orbital",
                 {"orbit_anchor": "body_centre", "orbit_nx": +0.20, "orbit_ny": 0.00},
                 weight_sigma_nx=0.55, weight_sigma_ny=0.55),
        FlowZone("jaw", "fixed",
                 {"radians": 0.06, "anchor_nx": -0.38, "anchor_ny": +0.08},
                 weight_sigma_nx=0.32, weight_sigma_ny=0.14),
    ],
    proportions={"casque_height_fraction": 0.48, "eye_diameter_fraction": 0.20, "aspect_ratio": 1.30},
)


# ── Snake (head + coiled body) ────────────────────────────────────────────────

SNAKE = SubjectAnatomy(
    subject_id="snake",
    display_name="Snake (Head — Side / 3/4)",
    landmarks=[
        # Head (the bounding ellipse covers the triangular head)
        Landmark("eye",             nx=-0.18, ny=-0.18),
        Landmark("pupil",           nx=-0.18, ny=-0.18),
        Landmark("pit_organ",       nx=-0.52, ny=-0.05),    # heat pit (vipers)
        Landmark("nostril",         nx=-0.68, ny=-0.08),
        Landmark("snout_tip",       nx=-0.82, ny= 0.00),
        Landmark("upper_jaw_front", nx=-0.70, ny=+0.08),
        Landmark("mouth_corner",    nx=-0.12, ny=+0.22),    # rear of jaw
        Landmark("fang",            nx=-0.60, ny=+0.16),    # if viper
        Landmark("lower_jaw",       nx=-0.40, ny=+0.28),
        Landmark("supraocular",     nx=-0.18, ny=-0.30),    # brow scale — gives stern look
        Landmark("parietal",        nx=+0.12, ny=-0.20),    # top head plate
        Landmark("neck_scale_front",nx=+0.40, ny=-0.05),
        Landmark("neck_scale_rear", nx=+0.72, ny=+0.08),
    ],
    feature_zones=[
        FeatureZone("eye",          "eye",          radius_nx=0.18, radius_ny=0.16,
                    error_weight=9.0, stroke_size_scale=0.42, jitter_scale=0.46, wet_blend_scale=0.42),
        FeatureZone("pit_organ",    "pit_organ",    radius_nx=0.14, radius_ny=0.12,
                    error_weight=6.0, stroke_size_scale=0.44),    # distinctive heat pit
        FeatureZone("supraocular",  "supraocular",  radius_nx=0.18, radius_ny=0.10,
                    error_weight=4.5, stroke_size_scale=0.48),    # the brow that looks angry
        FeatureZone("fang",         "fang",         radius_nx=0.16, radius_ny=0.14,
                    error_weight=5.5, stroke_size_scale=0.44),
        FeatureZone("head_scales",  "parietal",     radius_nx=0.55, radius_ny=0.45,
                    error_weight=3.5, stroke_size_scale=0.52),
        FeatureZone("neck_pattern", "neck_scale_mid" if False else "neck_scale_front",
                    radius_nx=0.30, radius_ny=0.35, error_weight=3.0, stroke_size_scale=0.55),
    ],
    flow_zones=[
        FlowZone("eye_socket", "orbital",
                 {"orbit_anchor": "eye", "orbit_nx": -0.18, "orbit_ny": -0.18},
                 weight_sigma_nx=0.18, weight_sigma_ny=0.16),
        FlowZone("jaw_line", "fixed",
                 {"radians": 0.06, "anchor_nx": -0.40, "anchor_ny": +0.16},
                 weight_sigma_nx=0.38, weight_sigma_ny=0.16),
        # Head scales — run roughly horizontal, slightly arched
        FlowZone("head_scales", "diagonal",
                 {"nx_factor": 0.55, "ny_factor": 0.05, "anchor_nx": +0.10, "anchor_ny": -0.10},
                 weight_sigma_nx=0.50, weight_sigma_ny=0.40),
        # Neck scales — slightly diagonal (scales overlap posteriorly)
        FlowZone("neck_scales", "diagonal",
                 {"nx_factor": 0.72, "ny_factor": 0.12, "anchor_nx": +0.55, "anchor_ny": 0.00},
                 weight_sigma_nx=0.28, weight_sigma_ny=0.35),
    ],
    proportions={"head_width_fraction": 0.55, "eye_diameter_fraction": 0.16, "aspect_ratio": 1.60},
)


# ── Crocodile (side / slight 3/4) ────────────────────────────────────────────

CROCODILE = SubjectAnatomy(
    subject_id="crocodile",
    display_name="Crocodile / Alligator (Side Profile)",
    landmarks=[
        Landmark("eye",              nx=-0.08, ny=-0.35),   # set very high on skull
        Landmark("pupil",            nx=-0.08, ny=-0.35),
        Landmark("nostril",          nx=-0.82, ny=-0.25),   # at snout tip, elevated
        Landmark("snout_tip",        nx=-0.90, ny=-0.12),
        Landmark("upper_jaw_mid",    nx=-0.50, ny=-0.08),
        Landmark("tooth_row_upper",  nx=-0.45, ny=+0.05),   # teeth visible below jaw
        Landmark("tooth_row_lower",  nx=-0.40, ny=+0.15),
        Landmark("mouth_corner",     nx=-0.02, ny=+0.18),
        Landmark("mandible_rear",    nx=+0.22, ny=+0.12),
        Landmark("scute_neck_1",     nx=+0.30, ny=-0.30),   # first neck scute
        Landmark("scute_neck_2",     nx=+0.52, ny=-0.35),
        Landmark("ear_pit",          nx=+0.18, ny=-0.25),   # ear opening behind eye
        Landmark("skull_top",        nx=+0.05, ny=-0.48),
    ],
    feature_zones=[
        # Eyes with vertical pupil — set very high, almost on top of head
        FeatureZone("eye",          "eye",          radius_nx=0.16, radius_ny=0.14,
                    error_weight=9.0, stroke_size_scale=0.44, jitter_scale=0.48, wet_blend_scale=0.44),
        FeatureZone("nostril",      "nostril",      radius_nx=0.12, radius_ny=0.10,
                    error_weight=5.5, stroke_size_scale=0.46),
        # Tooth row — the visible teeth define character
        FeatureZone("teeth",        "tooth_row_upper", radius_nx=0.48, radius_ny=0.12,
                    error_weight=5.0, stroke_size_scale=0.46, jitter_scale=0.52),
        # Armoured scutes — osteoderms on neck/back
        FeatureZone("neck_scutes",  "scute_neck_1",   radius_nx=0.40, radius_ny=0.22,
                    error_weight=4.0, stroke_size_scale=0.52),
        FeatureZone("snout",        "upper_jaw_mid",  radius_nx=0.50, radius_ny=0.22,
                    error_weight=3.5, stroke_size_scale=0.55),
        FeatureZone("ear_pit",      "ear_pit",        radius_nx=0.14, radius_ny=0.12,
                    error_weight=3.0, stroke_size_scale=0.50),
    ],
    flow_zones=[
        FlowZone("eye_socket", "orbital",
                 {"orbit_anchor": "eye", "orbit_nx": -0.08, "orbit_ny": -0.35},
                 weight_sigma_nx=0.16, weight_sigma_ny=0.14),
        # Snout — long horizontal strokes along the jaw
        FlowZone("snout", "fixed",
                 {"radians": 0.02, "anchor_nx": -0.50, "anchor_ny": -0.08},
                 weight_sigma_nx=0.48, weight_sigma_ny=0.20),
        # Scutes — brickwork pattern; strokes run horizontally across each scute
        FlowZone("scutes", "fixed",
                 {"radians": 0.0, "anchor_nx": +0.38, "anchor_ny": -0.30},
                 weight_sigma_nx=0.30, weight_sigma_ny=0.35),
        # Jaw line — strokes run along the tooth row
        FlowZone("jaw_line", "fixed",
                 {"radians": 0.05, "anchor_nx": -0.35, "anchor_ny": +0.10},
                 weight_sigma_nx=0.50, weight_sigma_ny=0.14),
    ],
    proportions={"snout_length_fraction": 0.62, "eye_position_ny": -0.35, "aspect_ratio": 2.40},
)
