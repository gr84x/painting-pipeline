"""
Insect anatomy — dragonfly, beetle, bee.

All variants are dorsal (top-down) view with body along the vertical axis.

Dragonfly: enormous compound eyes, four transparent veined wings, long
segmented abdomen. Eye weight is extreme — compound eyes cover most of the head.

Beetle: heavily armoured; elytra (fused wing-covers) are the dominant surface.
Surface texture (iridescence, puncture rows, ridges) is the painting challenge.

Bee / bumblebee: distinctive yellow-black banding on hairy abdomen; pollen
baskets on hind legs; wings partially folded; face and compound eyes visible.
"""
import math
from ..schema import Landmark, FeatureZone, FlowZone, SubjectAnatomy


# ── Dragonfly ─────────────────────────────────────────────────────────────────

DRAGONFLY = SubjectAnatomy(
    subject_id="dragonfly",
    display_name="Dragonfly (Dorsal)",
    landmarks=[
        Landmark("head_centre",      nx= 0.00, ny=-0.82),
        Landmark("left_compound_eye",nx=-0.22, ny=-0.84),
        Landmark("right_compound_eye",nx=+0.22,ny=-0.84),
        Landmark("thorax",           nx= 0.00, ny=-0.62),
        Landmark("abdomen_s1",       nx= 0.00, ny=-0.42),
        Landmark("abdomen_s4",       nx= 0.00, ny= 0.00),
        Landmark("abdomen_s7",       nx= 0.00, ny=+0.45),
        Landmark("abdomen_tip",      nx= 0.00, ny=+0.88),
        # Wings — four, arranged in two pairs
        Landmark("fw_left_tip",      nx=-0.92, ny=-0.60),
        Landmark("fw_right_tip",     nx=+0.92, ny=-0.60),
        Landmark("fw_left_base",     nx=-0.12, ny=-0.65),
        Landmark("fw_right_base",    nx=+0.12, ny=-0.65),
        Landmark("hw_left_tip",      nx=-0.88, ny=-0.32),
        Landmark("hw_right_tip",     nx=+0.88, ny=-0.32),
        Landmark("hw_left_base",     nx=-0.14, ny=-0.52),
        Landmark("hw_right_base",    nx=+0.14, ny=-0.52),
    ],
    feature_zones=[
        FeatureZone("left_eye",  "left_compound_eye",  radius_nx=0.26, radius_ny=0.14,
                    error_weight=9.0, stroke_size_scale=0.42, jitter_scale=0.46, wet_blend_scale=0.42),
        FeatureZone("right_eye", "right_compound_eye", radius_nx=0.26, radius_ny=0.14,
                    error_weight=9.0, stroke_size_scale=0.42, jitter_scale=0.46, wet_blend_scale=0.42),
        FeatureZone("wing_venation_fw", "fw_left_tip", radius_nx=0.45, radius_ny=0.20,
                    error_weight=4.5, stroke_size_scale=0.48),   # vein network
        FeatureZone("abdomen_segments","abdomen_s4",   radius_nx=0.18, radius_ny=0.55,
                    error_weight=3.5, stroke_size_scale=0.52),
        FeatureZone("thorax_pattern", "thorax",        radius_nx=0.22, radius_ny=0.22,
                    error_weight=3.0, stroke_size_scale=0.55),
    ],
    flow_zones=[
        FlowZone("left_eye", "orbital",
                 {"orbit_anchor": "left_compound_eye", "orbit_nx": -0.22, "orbit_ny": -0.84},
                 weight_sigma_nx=0.22, weight_sigma_ny=0.16),
        FlowZone("right_eye", "orbital",
                 {"orbit_anchor": "right_compound_eye", "orbit_nx": +0.22, "orbit_ny": -0.84},
                 weight_sigma_nx=0.22, weight_sigma_ny=0.16),
        # Forewings — veins radiate from base
        FlowZone("fw_left", "diagonal",
                 {"nx_factor": -0.82, "ny_factor": -0.30, "anchor_nx": -0.12, "anchor_ny": -0.63},
                 weight_sigma_nx=0.48, weight_sigma_ny=0.20),
        FlowZone("fw_right", "diagonal",
                 {"nx_factor": +0.82, "ny_factor": -0.30, "anchor_nx": +0.12, "anchor_ny": -0.63},
                 weight_sigma_nx=0.48, weight_sigma_ny=0.20),
        # Hindwings
        FlowZone("hw_left", "diagonal",
                 {"nx_factor": -0.80, "ny_factor": -0.15, "anchor_nx": -0.14, "anchor_ny": -0.50},
                 weight_sigma_nx=0.46, weight_sigma_ny=0.20),
        FlowZone("hw_right", "diagonal",
                 {"nx_factor": +0.80, "ny_factor": -0.15, "anchor_nx": +0.14, "anchor_ny": -0.50},
                 weight_sigma_nx=0.46, weight_sigma_ny=0.20),
        # Abdomen segments — horizontal rings
        FlowZone("abdomen", "fixed",
                 {"radians": 0.0, "anchor_nx": 0.00, "anchor_ny": +0.20},
                 weight_sigma_nx=0.18, weight_sigma_ny=0.55),
    ],
    proportions={"abdomen_length_fraction": 0.65, "wingspan_to_body": 2.5, "aspect_ratio": 0.55},
)


# ── Beetle ────────────────────────────────────────────────────────────────────

BEETLE = SubjectAnatomy(
    subject_id="beetle",
    display_name="Beetle (Dorsal)",
    landmarks=[
        Landmark("head",              nx= 0.00, ny=-0.72),
        Landmark("left_compound_eye", nx=-0.18, ny=-0.74),
        Landmark("right_compound_eye",nx=+0.18, ny=-0.74),
        Landmark("left_mandible",     nx=-0.14, ny=-0.82),
        Landmark("right_mandible",    nx=+0.14, ny=-0.82),
        Landmark("pronotum",          nx= 0.00, ny=-0.52),   # thorax shield
        Landmark("pronotum_left",     nx=-0.32, ny=-0.52),
        Landmark("pronotum_right",    nx=+0.32, ny=-0.52),
        Landmark("scutellum",         nx= 0.00, ny=-0.35),   # small triangle between elytra
        Landmark("elytron_left",      nx=-0.30, ny= 0.00),   # left wing cover
        Landmark("elytron_right",     nx=+0.30, ny= 0.00),
        Landmark("elytron_suture",    nx= 0.00, ny= 0.10),   # centreline between elytra
        Landmark("elytron_tip_left",  nx=-0.22, ny=+0.68),
        Landmark("elytron_tip_right", nx=+0.22, ny=+0.68),
        Landmark("abdomen_tip",       nx= 0.00, ny=+0.78),
    ],
    feature_zones=[
        FeatureZone("left_eye",   "left_compound_eye",  radius_nx=0.16, radius_ny=0.12,
                    error_weight=8.0, stroke_size_scale=0.44, jitter_scale=0.50, wet_blend_scale=0.44),
        FeatureZone("right_eye",  "right_compound_eye", radius_nx=0.16, radius_ny=0.12,
                    error_weight=8.0, stroke_size_scale=0.44, jitter_scale=0.50, wet_blend_scale=0.44),
        FeatureZone("mandibles",  "left_mandible",      radius_nx=0.22, radius_ny=0.12,
                    error_weight=5.0, stroke_size_scale=0.48),
        # Elytra surface — iridescence, puncture rows, ridges are everything
        FeatureZone("elytra_left",  "elytron_left",   radius_nx=0.35, radius_ny=0.60,
                    error_weight=4.0, stroke_size_scale=0.55),
        FeatureZone("elytra_right", "elytron_right",  radius_nx=0.35, radius_ny=0.60,
                    error_weight=4.0, stroke_size_scale=0.55),
        FeatureZone("elytra_suture","elytron_suture", radius_nx=0.10, radius_ny=0.55,
                    error_weight=3.0, stroke_size_scale=0.48),   # centreline detail
        FeatureZone("pronotum",     "pronotum",       radius_nx=0.40, radius_ny=0.22,
                    error_weight=3.5, stroke_size_scale=0.55),
    ],
    flow_zones=[
        FlowZone("left_eye", "orbital",
                 {"orbit_anchor": "left_compound_eye", "orbit_nx": -0.18, "orbit_ny": -0.74},
                 weight_sigma_nx=0.16, weight_sigma_ny=0.13),
        FlowZone("right_eye", "orbital",
                 {"orbit_anchor": "right_compound_eye", "orbit_nx": +0.18, "orbit_ny": -0.74},
                 weight_sigma_nx=0.16, weight_sigma_ny=0.13),
        # Pronotum — dome-shaped; strokes follow curved surface
        FlowZone("pronotum", "orbital",
                 {"orbit_anchor": "pronotum", "orbit_nx": 0.00, "orbit_ny": -0.52},
                 weight_sigma_nx=0.38, weight_sigma_ny=0.22),
        # Elytra — strokes follow the longitudinal puncture rows
        FlowZone("elytra_left_rows", "diagonal",
                 {"nx_factor": -0.08, "ny_factor": 0.96, "anchor_nx": -0.28, "anchor_ny": +0.12},
                 weight_sigma_nx=0.32, weight_sigma_ny=0.60),
        FlowZone("elytra_right_rows", "diagonal",
                 {"nx_factor": +0.08, "ny_factor": 0.96, "anchor_nx": +0.28, "anchor_ny": +0.12},
                 weight_sigma_nx=0.32, weight_sigma_ny=0.60),
    ],
    proportions={"elytra_fraction": 0.55, "pronotum_width_fraction": 0.65, "aspect_ratio": 0.68},
)


# ── Bee / Bumblebee ───────────────────────────────────────────────────────────

BEE = SubjectAnatomy(
    subject_id="bee",
    display_name="Bee / Bumblebee (Dorsal / 3/4)",
    landmarks=[
        Landmark("head",              nx= 0.00, ny=-0.78),
        Landmark("left_compound_eye", nx=-0.24, ny=-0.80),
        Landmark("right_compound_eye",nx=+0.24, ny=-0.80),
        Landmark("left_antenna",      nx=-0.16, ny=-0.90),
        Landmark("right_antenna",     nx=+0.16, ny=-0.90),
        Landmark("face_centre",       nx= 0.00, ny=-0.78),
        Landmark("thorax",            nx= 0.00, ny=-0.52),
        Landmark("wing_left_base",    nx=-0.14, ny=-0.55),
        Landmark("wing_right_base",   nx=+0.14, ny=-0.55),
        Landmark("wing_left_tip",     nx=-0.75, ny=-0.45),
        Landmark("wing_right_tip",    nx=+0.75, ny=-0.45),
        Landmark("abdomen_band_1",    nx= 0.00, ny=-0.22),   # first colour band
        Landmark("abdomen_band_2",    nx= 0.00, ny= 0.00),
        Landmark("abdomen_band_3",    nx= 0.00, ny=+0.22),
        Landmark("abdomen_tip",       nx= 0.00, ny=+0.62),
        Landmark("pollen_basket_left",nx=-0.28, ny=+0.05),   # corbiculae on hind legs
        Landmark("pollen_basket_right",nx=+0.28,ny=+0.05),
    ],
    feature_zones=[
        FeatureZone("left_eye",   "left_compound_eye",  radius_nx=0.24, radius_ny=0.16,
                    error_weight=8.5, stroke_size_scale=0.44, jitter_scale=0.48, wet_blend_scale=0.44),
        FeatureZone("right_eye",  "right_compound_eye", radius_nx=0.24, radius_ny=0.16,
                    error_weight=8.5, stroke_size_scale=0.44, jitter_scale=0.48, wet_blend_scale=0.44),
        FeatureZone("face",       "face_centre",         radius_nx=0.35, radius_ny=0.18,
                    error_weight=5.0, stroke_size_scale=0.50),
        # Colour banding — the defining feature of bee identity
        FeatureZone("abdomen_bands","abdomen_band_2",   radius_nx=0.38, radius_ny=0.55,
                    error_weight=4.5, stroke_size_scale=0.52),
        FeatureZone("pollen_baskets","pollen_basket_left",radius_nx=0.18,radius_ny=0.28,
                    error_weight=3.5, stroke_size_scale=0.50),   # bright yellow pollen
        FeatureZone("wings",      "wing_left_tip",       radius_nx=0.40, radius_ny=0.22,
                    error_weight=2.5, stroke_size_scale=0.58),
    ],
    flow_zones=[
        FlowZone("left_eye", "orbital",
                 {"orbit_anchor": "left_compound_eye", "orbit_nx": -0.24, "orbit_ny": -0.80},
                 weight_sigma_nx=0.22, weight_sigma_ny=0.18),
        FlowZone("right_eye", "orbital",
                 {"orbit_anchor": "right_compound_eye", "orbit_nx": +0.24, "orbit_ny": -0.80},
                 weight_sigma_nx=0.22, weight_sigma_ny=0.18),
        # Thorax — hair on thorax runs in all directions; use orbital around centre
        FlowZone("thorax", "orbital",
                 {"orbit_anchor": "thorax", "orbit_nx": 0.00, "orbit_ny": -0.52},
                 weight_sigma_nx=0.28, weight_sigma_ny=0.24),
        # Abdomen — horizontal stripes across each segment
        FlowZone("abdomen_stripes", "fixed",
                 {"radians": 0.0, "anchor_nx": 0.00, "anchor_ny": +0.10},
                 weight_sigma_nx=0.38, weight_sigma_ny=0.52),
        # Wings — veins radiate from base
        FlowZone("wings_left", "diagonal",
                 {"nx_factor": -0.78, "ny_factor": -0.18, "anchor_nx": -0.14, "anchor_ny": -0.53},
                 weight_sigma_nx=0.38, weight_sigma_ny=0.18),
        FlowZone("wings_right", "diagonal",
                 {"nx_factor": +0.78, "ny_factor": -0.18, "anchor_nx": +0.14, "anchor_ny": -0.53},
                 weight_sigma_nx=0.38, weight_sigma_ny=0.18),
    ],
    proportions={"abdomen_band_count": 3, "wing_length_fraction": 0.80, "aspect_ratio": 0.62},
)
