"""
Large mammal anatomy — lion, giraffe, ape/chimpanzee, beaver, pig.

All subjects: head / face in the most natural portrait orientation for each.
  Lion:       3/4 frontal — massive mane defines the silhouette
  Giraffe:    side profile — very long neck, ossicones, distinctive pattern
  Chimpanzee: frontal — expressive, human-like face, dark skin, bare face
  Beaver:     3/4 frontal — broad flat head, prominent incisors, small eyes
  Pig:        frontal — round snout disc, wide-set eyes, floppy or pricked ears
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy


# ── Lion (3/4 frontal) ────────────────────────────────────────────────────────

LION = SubjectAnatomy(
    subject_id="lion",
    display_name="Lion (3/4 Frontal, Male)",
    landmarks=[
        Landmark("near_eye",       nx=-0.22, ny=-0.12),
        Landmark("far_eye",        nx=+0.14, ny=-0.14),
        Landmark("nose_pad",       nx=-0.10, ny=+0.22),
        Landmark("left_nostril",   nx=-0.16, ny=+0.18),
        Landmark("right_nostril",  nx=-0.02, ny=+0.18),
        Landmark("upper_lip",      nx=-0.05, ny=+0.38),
        Landmark("mouth_corner",   nx=-0.24, ny=+0.36),
        Landmark("chin",           nx=-0.08, ny=+0.68),
        Landmark("forehead",       nx=+0.02, ny=-0.30),
        Landmark("mane_top",       nx=+0.05, ny=-0.85),     # mane extends far above skull
        Landmark("mane_left",      nx=-0.90, ny=+0.00),     # mane extends wide
        Landmark("mane_right",     nx=+0.80, ny=+0.00),
        Landmark("mane_bottom",    nx=-0.05, ny=+0.88),
        Landmark("near_ear",       nx=-0.38, ny=-0.60),
        Landmark("far_ear",        nx=+0.32, ny=-0.58),
        Landmark("whisker_pad",    nx=-0.26, ny=+0.28),
    ],
    feature_zones=[
        FeatureZone("near_eye",    "near_eye",    radius_nx=0.20, radius_ny=0.14,
                    error_weight=7.5, stroke_size_scale=0.52, jitter_scale=0.56, wet_blend_scale=0.52),
        FeatureZone("far_eye",     "far_eye",     radius_nx=0.16, radius_ny=0.11,
                    error_weight=6.0, stroke_size_scale=0.56, jitter_scale=0.60, wet_blend_scale=0.56),
        FeatureZone("nose",        "nose_pad",    radius_nx=0.22, radius_ny=0.18,
                    error_weight=5.5, stroke_size_scale=0.54, jitter_scale=0.60),
        FeatureZone("mouth",       "upper_lip",   radius_nx=0.32, radius_ny=0.18,
                    error_weight=4.0, stroke_size_scale=0.60),
        FeatureZone("whisker_pad", "whisker_pad", radius_nx=0.25, radius_ny=0.18,
                    error_weight=3.0, stroke_size_scale=0.62),
        # The mane is the lion's most distinctive visual feature
        FeatureZone("mane",        "mane_left",   radius_nx=0.55, radius_ny=0.75,
                    error_weight=3.5, stroke_size_scale=0.65),
        FeatureZone("near_ear",    "near_ear",    radius_nx=0.16, radius_ny=0.14,
                    error_weight=2.5, stroke_size_scale=0.68),
    ],
    flow_zones=[
        FlowZone("near_eye_socket", "orbital",
                 {"orbit_anchor": "near_eye", "orbit_nx": -0.22, "orbit_ny": -0.12},
                 weight_sigma_nx=0.20, weight_sigma_ny=0.16),
        FlowZone("far_eye_socket", "orbital",
                 {"orbit_anchor": "far_eye", "orbit_nx": +0.14, "orbit_ny": -0.14},
                 weight_sigma_nx=0.16, weight_sigma_ny=0.13),
        FlowZone("muzzle", "diagonal",
                 {"nx_factor": -0.08, "ny_factor": 0.96, "anchor_nx": -0.08, "anchor_ny": +0.28},
                 weight_sigma_nx=0.32, weight_sigma_ny=0.30),
        FlowZone("cheek", "diagonal",
                 {"nx_factor": -0.35, "ny_factor": 0.88, "anchor_nx": -0.18, "anchor_ny": +0.10},
                 weight_sigma_nx=0.38, weight_sigma_ny=0.35),
        FlowZone("forehead", "diagonal",
                 {"nx_factor": 0.10, "ny_factor": 1.0, "anchor_nx": +0.02, "anchor_ny": -0.28},
                 weight_sigma_nx=0.50, weight_sigma_ny=0.22),
        # Mane — fur radiates outward from face in all directions
        FlowZone("mane_left", "diagonal",
                 {"nx_factor": -0.88, "ny_factor": 0.30, "anchor_nx": -0.60, "anchor_ny": +0.05},
                 weight_sigma_nx=0.30, weight_sigma_ny=0.60),
        FlowZone("mane_right", "diagonal",
                 {"nx_factor": +0.72, "ny_factor": 0.40, "anchor_nx": +0.55, "anchor_ny": +0.05},
                 weight_sigma_nx=0.25, weight_sigma_ny=0.60),
        FlowZone("mane_top", "diagonal",
                 {"nx_factor": 0.08, "ny_factor": -0.92, "anchor_nx": +0.04, "anchor_ny": -0.62},
                 weight_sigma_nx=0.45, weight_sigma_ny=0.22),
        FlowZone("mane_bottom", "diagonal",
                 {"nx_factor": 0.10, "ny_factor": 0.92, "anchor_nx": -0.05, "anchor_ny": +0.72},
                 weight_sigma_nx=0.45, weight_sigma_ny=0.18),
    ],
    proportions={"mane_radius_fraction": 0.85, "eye_diameter_fraction": 0.14,
                 "nose_pad_fraction": 0.22, "aspect_ratio": 1.10},
)


# ── Giraffe (side profile) ────────────────────────────────────────────────────

GIRAFFE = SubjectAnatomy(
    subject_id="giraffe",
    display_name="Giraffe (Side Profile)",
    landmarks=[
        Landmark("eye",              nx=-0.12, ny=-0.25),
        Landmark("ossicone_main",    nx=+0.05, ny=-0.82),   # the horn-like ossicones
        Landmark("ossicone_secondary",nx=+0.20,ny=-0.75),
        Landmark("nostril",          nx=-0.80, ny=+0.12),
        Landmark("mouth_upper",      nx=-0.82, ny=+0.25),
        Landmark("mouth_lower",      nx=-0.80, ny=+0.35),
        Landmark("tongue",           nx=-0.88, ny=+0.30),   # prehensile tongue often visible
        Landmark("mouth_corner",     nx=-0.55, ny=+0.32),
        Landmark("forehead",         nx=+0.05, ny=-0.42),
        Landmark("nape",             nx=+0.40, ny=-0.55),
        Landmark("mane_top",         nx=+0.22, ny=-0.68),
        Landmark("chin",             nx=-0.62, ny=+0.45),
        Landmark("neck_pattern",     nx=+0.28, ny=+0.08),   # reticulated patch zone
        Landmark("cheek",            nx=-0.05, ny=+0.08),
        Landmark("ear",              nx=+0.30, ny=-0.38),
    ],
    feature_zones=[
        FeatureZone("eye",       "eye",         radius_nx=0.16, radius_ny=0.13,
                    error_weight=9.0, stroke_size_scale=0.46, jitter_scale=0.50, wet_blend_scale=0.46),
        FeatureZone("ossicones", "ossicone_main",radius_nx=0.22,radius_ny=0.28,
                    error_weight=4.5, stroke_size_scale=0.54),
        FeatureZone("nostril",   "nostril",     radius_nx=0.14, radius_ny=0.12,
                    error_weight=4.0, stroke_size_scale=0.50),
        FeatureZone("tongue",    "tongue",      radius_nx=0.18, radius_ny=0.14,
                    error_weight=5.0, stroke_size_scale=0.48),    # dark prehensile tongue
        FeatureZone("mouth",     "mouth_upper", radius_nx=0.22, radius_ny=0.16,
                    error_weight=3.5, stroke_size_scale=0.55),
        # Reticulated pattern — the signature coat pattern
        FeatureZone("coat_pattern","neck_pattern",radius_nx=0.55,radius_ny=0.55,
                    error_weight=4.0, stroke_size_scale=0.58),
        FeatureZone("ear",       "ear",         radius_nx=0.18, radius_ny=0.22,
                    error_weight=2.5, stroke_size_scale=0.65),
    ],
    flow_zones=[
        FlowZone("eye_socket", "orbital",
                 {"orbit_anchor": "eye", "orbit_nx": -0.12, "orbit_ny": -0.25},
                 weight_sigma_nx=0.16, weight_sigma_ny=0.14),
        FlowZone("snout", "fixed",
                 {"radians": 0.04, "anchor_nx": -0.55, "anchor_ny": +0.20},
                 weight_sigma_nx=0.32, weight_sigma_ny=0.22),
        FlowZone("cheek_short_fur", "diagonal",
                 {"nx_factor": 0.55, "ny_factor": 0.20, "anchor_nx": 0.00, "anchor_ny": 0.00},
                 weight_sigma_nx=0.42, weight_sigma_ny=0.38),
        # Reticulated patches — strokes follow patch interior
        FlowZone("coat_patches", "orbital",
                 {"orbit_anchor": "neck_pattern", "orbit_nx": +0.28, "orbit_ny": +0.08},
                 weight_sigma_nx=0.55, weight_sigma_ny=0.55),
        FlowZone("mane", "fixed",
                 {"radians": math.pi * 0.52, "anchor_nx": +0.22, "anchor_ny": -0.65},
                 weight_sigma_nx=0.14, weight_sigma_ny=0.20),
        FlowZone("ossicones", "fixed",
                 {"radians": math.pi * 0.50, "anchor_nx": +0.12, "anchor_ny": -0.78},
                 weight_sigma_nx=0.16, weight_sigma_ny=0.20),
    ],
    proportions={"snout_length_fraction": 0.50, "neck_length_multiplier": 3.5,
                 "eye_diameter_fraction": 0.14, "aspect_ratio": 1.60},
)


# ── Chimpanzee / Ape (frontal) ────────────────────────────────────────────────

CHIMPANZEE = SubjectAnatomy(
    subject_id="chimpanzee",
    display_name="Chimpanzee / Great Ape (Frontal)",
    landmarks=[
        Landmark("left_eye",          nx=-0.28, ny=-0.10),
        Landmark("right_eye",         nx=+0.28, ny=-0.10),
        Landmark("left_brow_ridge",   nx=-0.30, ny=-0.25),  # prominent supraorbital torus
        Landmark("right_brow_ridge",  nx=+0.30, ny=-0.25),
        Landmark("nose_bridge",       nx= 0.00, ny=+0.05),  # flat, wide nose
        Landmark("left_nostril",      nx=-0.14, ny=+0.22),
        Landmark("right_nostril",     nx=+0.14, ny=+0.22),
        Landmark("nose_tip",          nx= 0.00, ny=+0.22),
        Landmark("upper_lip",         nx= 0.00, ny=+0.40),
        Landmark("lower_lip",         nx= 0.00, ny=+0.52),
        Landmark("mouth_corner_left", nx=-0.24, ny=+0.46),
        Landmark("mouth_corner_right",nx=+0.24, ny=+0.46),
        Landmark("chin",              nx= 0.00, ny=+0.72),
        Landmark("forehead",          nx= 0.00, ny=-0.42),
        Landmark("left_ear",          nx=-0.82, ny=+0.05),
        Landmark("right_ear",         nx=+0.82, ny=+0.05),
        Landmark("left_cheek",        nx=-0.55, ny=+0.20),
        Landmark("right_cheek",       nx=+0.55, ny=+0.20),
    ],
    feature_zones=[
        FeatureZone("left_eye",        "left_eye",         radius_nx=0.22, radius_ny=0.14,
                    error_weight=8.0, stroke_size_scale=0.52, jitter_scale=0.56, wet_blend_scale=0.52),
        FeatureZone("right_eye",       "right_eye",        radius_nx=0.22, radius_ny=0.14,
                    error_weight=8.0, stroke_size_scale=0.52, jitter_scale=0.56, wet_blend_scale=0.52),
        # Supraorbital torus — the brow ridge is a major likeness feature
        FeatureZone("brow_ridge",      "left_brow_ridge",  radius_nx=0.55, radius_ny=0.10,
                    error_weight=5.5, stroke_size_scale=0.55),
        FeatureZone("nose",            "nose_tip",         radius_nx=0.25, radius_ny=0.20,
                    error_weight=4.5, stroke_size_scale=0.58),
        # Lips — highly expressive; chimps have protruding, mobile lips
        FeatureZone("mouth",           "upper_lip",        radius_nx=0.38, radius_ny=0.20,
                    error_weight=5.5, stroke_size_scale=0.52, jitter_scale=0.58, wet_blend_scale=0.55),
        FeatureZone("left_ear",        "left_ear",         radius_nx=0.22, radius_ny=0.28,
                    error_weight=2.5, stroke_size_scale=0.68),
        FeatureZone("right_ear",       "right_ear",        radius_nx=0.22, radius_ny=0.28,
                    error_weight=2.5, stroke_size_scale=0.68),
    ],
    flow_zones=[
        FlowZone("left_eye_socket", "orbital",
                 {"orbit_anchor": "left_eye", "orbit_nx": -0.28, "orbit_ny": -0.10},
                 weight_sigma_nx=0.22, weight_sigma_ny=0.16),
        FlowZone("right_eye_socket", "orbital",
                 {"orbit_anchor": "right_eye", "orbit_nx": +0.28, "orbit_ny": -0.10},
                 weight_sigma_nx=0.22, weight_sigma_ny=0.16),
        # Brow ridge — strokes follow the horizontal ridge
        FlowZone("brow_ridge", "fixed",
                 {"radians": 0.0, "anchor_nx": 0.00, "anchor_ny": -0.25},
                 weight_sigma_nx=0.58, weight_sigma_ny=0.10),
        FlowZone("left_cheek", "diagonal",
                 {"nx_factor": -0.40, "ny_factor": 0.88, "anchor_nx": -0.48, "anchor_ny": +0.18},
                 weight_sigma_nx=0.32, weight_sigma_ny=0.30),
        FlowZone("right_cheek", "diagonal",
                 {"nx_factor": +0.40, "ny_factor": 0.88, "anchor_nx": +0.48, "anchor_ny": +0.18},
                 weight_sigma_nx=0.32, weight_sigma_ny=0.30),
        FlowZone("forehead", "diagonal",
                 {"nx_factor": 0.10, "ny_factor": 1.0, "anchor_nx": 0.00, "anchor_ny": -0.40},
                 weight_sigma_nx=0.52, weight_sigma_ny=0.20),
        FlowZone("muzzle_lip", "diagonal",
                 {"nx_factor": 0.04, "ny_factor": 0.96, "anchor_nx": 0.00, "anchor_ny": +0.45},
                 weight_sigma_nx=0.38, weight_sigma_ny=0.18),
    ],
    proportions={"brow_ridge_prominence": 0.55, "muzzle_protrusion": 0.45,
                 "interocular_distance_nx": 0.56, "aspect_ratio": 0.92},
)


# ── Beaver (3/4 frontal) ──────────────────────────────────────────────────────

BEAVER = SubjectAnatomy(
    subject_id="beaver",
    display_name="Beaver (3/4 Frontal)",
    landmarks=[
        Landmark("near_eye",        nx=-0.20, ny=-0.18),   # small eyes, set wide and high
        Landmark("far_eye",         nx=+0.16, ny=-0.20),
        Landmark("nose_pad",        nx=-0.05, ny=+0.15),   # broad flat nose
        Landmark("left_nostril",    nx=-0.10, ny=+0.12),
        Landmark("right_nostril",   nx= 0.00, ny=+0.12),
        Landmark("upper_incisor",   nx=-0.06, ny=+0.28),   # the prominent orange teeth
        Landmark("lower_incisor",   nx=-0.06, ny=+0.42),
        Landmark("mouth_corner",    nx=-0.20, ny=+0.35),
        Landmark("chin",            nx=-0.04, ny=+0.68),
        Landmark("forehead",        nx=+0.04, ny=-0.40),
        Landmark("near_ear",        nx=-0.40, ny=-0.50),   # small, round ears
        Landmark("far_ear",         nx=+0.30, ny=-0.48),
        Landmark("whisker_pad",     nx=-0.18, ny=+0.22),
        Landmark("cheek",           nx=-0.32, ny=+0.08),
    ],
    feature_zones=[
        FeatureZone("near_eye",     "near_eye",      radius_nx=0.16, radius_ny=0.12,
                    error_weight=7.5, stroke_size_scale=0.50, jitter_scale=0.56, wet_blend_scale=0.50),
        FeatureZone("far_eye",      "far_eye",       radius_nx=0.13, radius_ny=0.10,
                    error_weight=6.0, stroke_size_scale=0.54, jitter_scale=0.60),
        # Incisors — the most distinctive beaver feature; bright orange enamel
        FeatureZone("incisors",     "upper_incisor", radius_nx=0.18, radius_ny=0.22,
                    error_weight=7.0, stroke_size_scale=0.46, jitter_scale=0.50, wet_blend_scale=0.46),
        FeatureZone("nose",         "nose_pad",      radius_nx=0.18, radius_ny=0.12,
                    error_weight=5.0, stroke_size_scale=0.52),
        FeatureZone("whisker_pad",  "whisker_pad",   radius_nx=0.20, radius_ny=0.16,
                    error_weight=3.0, stroke_size_scale=0.60),
        FeatureZone("near_ear",     "near_ear",      radius_nx=0.16, radius_ny=0.16,
                    error_weight=2.5, stroke_size_scale=0.65),
    ],
    flow_zones=[
        FlowZone("near_eye_socket", "orbital",
                 {"orbit_anchor": "near_eye", "orbit_nx": -0.20, "orbit_ny": -0.18},
                 weight_sigma_nx=0.16, weight_sigma_ny=0.13),
        FlowZone("far_eye_socket", "orbital",
                 {"orbit_anchor": "far_eye", "orbit_nx": +0.16, "orbit_ny": -0.20},
                 weight_sigma_nx=0.13, weight_sigma_ny=0.11),
        FlowZone("cheek_fur", "diagonal",
                 {"nx_factor": -0.38, "ny_factor": 0.88, "anchor_nx": -0.28, "anchor_ny": +0.10},
                 weight_sigma_nx=0.35, weight_sigma_ny=0.32),
        FlowZone("muzzle_fur", "diagonal",
                 {"nx_factor": -0.06, "ny_factor": 0.96, "anchor_nx": -0.06, "anchor_ny": +0.24},
                 weight_sigma_nx=0.24, weight_sigma_ny=0.28),
        FlowZone("forehead_fur", "diagonal",
                 {"nx_factor": 0.08, "ny_factor": 1.0, "anchor_nx": +0.04, "anchor_ny": -0.38},
                 weight_sigma_nx=0.46, weight_sigma_ny=0.20),
    ],
    proportions={"incisor_height_fraction": 0.24, "eye_diameter_fraction": 0.12,
                 "nose_width_fraction": 0.22, "aspect_ratio": 0.90},
)


# ── Pig (frontal) ─────────────────────────────────────────────────────────────

PIG = SubjectAnatomy(
    subject_id="pig",
    display_name="Pig (Frontal)",
    landmarks=[
        Landmark("left_eye",         nx=-0.32, ny=-0.08),
        Landmark("right_eye",        nx=+0.32, ny=-0.08),
        Landmark("snout_disc",       nx= 0.00, ny=+0.30),   # the round snout plate
        Landmark("left_nostril",     nx=-0.12, ny=+0.28),
        Landmark("right_nostril",    nx=+0.12, ny=+0.28),
        Landmark("snout_edge",       nx= 0.00, ny=+0.38),
        Landmark("upper_lip",        nx= 0.00, ny=+0.46),
        Landmark("mouth_corner",     nx=-0.22, ny=+0.45),
        Landmark("chin",             nx= 0.00, ny=+0.70),
        Landmark("forehead",         nx= 0.00, ny=-0.38),
        Landmark("left_ear_base",    nx=-0.38, ny=-0.35),
        Landmark("left_ear_tip",     nx=-0.44, ny=-0.72),   # floppy (adjust for pricked ears)
        Landmark("right_ear_base",   nx=+0.38, ny=-0.35),
        Landmark("right_ear_tip",    nx=+0.44, ny=-0.72),
        Landmark("jowl_left",        nx=-0.52, ny=+0.28),
        Landmark("jowl_right",       nx=+0.52, ny=+0.28),
    ],
    feature_zones=[
        FeatureZone("left_eye",  "left_eye",   radius_nx=0.20, radius_ny=0.14,
                    error_weight=7.0, stroke_size_scale=0.54, jitter_scale=0.58, wet_blend_scale=0.54),
        FeatureZone("right_eye", "right_eye",  radius_nx=0.20, radius_ny=0.14,
                    error_weight=7.0, stroke_size_scale=0.54, jitter_scale=0.58, wet_blend_scale=0.54),
        # The snout disc is the pig's most characteristic feature
        FeatureZone("snout",     "snout_disc",  radius_nx=0.30, radius_ny=0.24,
                    error_weight=6.5, stroke_size_scale=0.50, jitter_scale=0.55, wet_blend_scale=0.50),
        FeatureZone("nostrils",  "left_nostril",radius_nx=0.18, radius_ny=0.14,
                    error_weight=5.0, stroke_size_scale=0.48),
        FeatureZone("mouth",     "upper_lip",   radius_nx=0.32, radius_ny=0.16,
                    error_weight=3.5, stroke_size_scale=0.60),
        FeatureZone("left_ear",  "left_ear_tip",radius_nx=0.18, radius_ny=0.28,
                    error_weight=2.5, stroke_size_scale=0.68),
        FeatureZone("right_ear", "right_ear_tip",radius_nx=0.18, radius_ny=0.28,
                    error_weight=2.5, stroke_size_scale=0.68),
        FeatureZone("jowls",     "jowl_left",   radius_nx=0.28, radius_ny=0.38,
                    error_weight=2.0, stroke_size_scale=0.72),
    ],
    flow_zones=[
        FlowZone("left_eye_socket", "orbital",
                 {"orbit_anchor": "left_eye", "orbit_nx": -0.32, "orbit_ny": -0.08},
                 weight_sigma_nx=0.20, weight_sigma_ny=0.16),
        FlowZone("right_eye_socket", "orbital",
                 {"orbit_anchor": "right_eye", "orbit_nx": +0.32, "orbit_ny": -0.08},
                 weight_sigma_nx=0.20, weight_sigma_ny=0.16),
        # Snout disc — orbital strokes following the round disc
        FlowZone("snout_disc", "orbital",
                 {"orbit_anchor": "snout_disc", "orbit_nx": 0.00, "orbit_ny": +0.30},
                 weight_sigma_nx=0.28, weight_sigma_ny=0.24),
        FlowZone("left_cheek", "diagonal",
                 {"nx_factor": -0.42, "ny_factor": 0.86, "anchor_nx": -0.45, "anchor_ny": +0.22},
                 weight_sigma_nx=0.32, weight_sigma_ny=0.35),
        FlowZone("right_cheek", "diagonal",
                 {"nx_factor": +0.42, "ny_factor": 0.86, "anchor_nx": +0.45, "anchor_ny": +0.22},
                 weight_sigma_nx=0.32, weight_sigma_ny=0.35),
        FlowZone("forehead", "diagonal",
                 {"nx_factor": 0.08, "ny_factor": 1.0, "anchor_nx": 0.00, "anchor_ny": -0.35},
                 weight_sigma_nx=0.52, weight_sigma_ny=0.20),
        FlowZone("left_ear", "fixed",
                 {"radians": math.pi * 0.55, "anchor_nx": -0.41, "anchor_ny": -0.52},
                 weight_sigma_nx=0.18, weight_sigma_ny=0.26),
        FlowZone("right_ear", "fixed",
                 {"radians": math.pi * 0.45, "anchor_nx": +0.41, "anchor_ny": -0.52},
                 weight_sigma_nx=0.18, weight_sigma_ny=0.26),
    ],
    proportions={"snout_disc_fraction": 0.35, "eye_diameter_fraction": 0.14,
                 "interocular_distance_nx": 0.64, "aspect_ratio": 0.88},
)
