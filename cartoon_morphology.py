"""
cartoon_morphology.py — Morphology parameters for stylized/cartoon head meshes.

CartoonMorphology is passed to build_head_code() to scale anatomical features
from realistic (all 1.0) to extreme cartoon/chibi (large values).
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CartoonMorphology:
    # ── Head shape ─────────────────────────────────────────────────────────────
    cranium_ratio: float = 1.0   # >1 expands skull above brow (anime big-head)
    face_flat:     float = 0.0   # 0=realistic depth, 1=flat anime face profile
    jaw_taper:     float = 0.0   # 0=normal, 1=very pointed/narrow chin

    # ── Eye region ─────────────────────────────────────────────────────────────
    eye_scale:     float = 1.0   # >1 = larger eye sockets (anime)
    eye_depth:     float = 1.0   # socket depth multiplier
    brow_ridge:    float = 1.0   # brow protrusion multiplier

    # ── Nose ───────────────────────────────────────────────────────────────────
    nose_size:     float = 1.0   # overall scale of nose displacements
    nose_tip:      float = 1.0   # tip prominence multiplier

    # ── Mouth / lips ───────────────────────────────────────────────────────────
    mouth_width:   float = 1.0   # widens mouth region
    lip_fullness:  float = 1.0   # lip volume multiplier

    # ── Presets ────────────────────────────────────────────────────────────────
    @classmethod
    def realistic(cls) -> CartoonMorphology:
        return cls()

    @classmethod
    def stylized(cls) -> CartoonMorphology:
        """Subtle exaggeration — still human but slightly more expressive."""
        return cls(cranium_ratio=1.15, eye_scale=1.20, eye_depth=1.30,
                   nose_size=0.80, lip_fullness=1.20, brow_ridge=1.10)

    @classmethod
    def cartoon(cls) -> CartoonMorphology:
        """Clear cartoon proportions — large eyes, small nose, round head."""
        return cls(cranium_ratio=1.35, face_flat=0.25,
                   eye_scale=1.60, eye_depth=1.50, brow_ridge=0.70,
                   nose_size=0.45, nose_tip=0.40,
                   lip_fullness=1.30, jaw_taper=0.20)

    @classmethod
    def chibi(cls) -> CartoonMorphology:
        """Extreme chibi: huge cranium, minimal face features, flat profile."""
        return cls(cranium_ratio=1.80, face_flat=0.55, jaw_taper=0.40,
                   eye_scale=2.20, eye_depth=1.80, brow_ridge=0.30,
                   nose_size=0.15, nose_tip=0.10,
                   lip_fullness=0.80, mouth_width=0.70)
