"""
pipeline.py — General painting pipeline orchestrator.

PaintingSession assembles an ordered list of passes from the stroke engine,
reference builder, and material passes into a complete painting workflow.

Design principles
-----------------
- Decoupled from any specific subject (Mona Lisa, owl, portrait, creature)
- PipelineSpec drives all sizing via subject_frac + canvas dimensions
- sfumato_level is a dial (0 = none, 1 = full) — not a default
- two_pass (background + subject) is opt-in via two_pass=True
- Material passes plug in via the material_passes registry
- MarkMakers plug in via the mark_makers registry

Usage
-----
    from pipeline import PaintingSession, PipelineSpec
    spec = PipelineSpec(
        canvas_width=780, canvas_height=1080,
        subject_frac=0.65,
        artist_key="lovis_corinth",
        surface="skin",
        sfumato_level=0.0,
    )
    session = PaintingSession(spec)
    session.paint("output.png")
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Pass configuration
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PassConfig:
    """One entry in a PaintingSession pass list."""
    name:    str                  # method name or material/mark name
    kind:    str = "stroke_engine"  # "stroke_engine" | "material" | "mark_maker"
    kwargs:  Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


# ─────────────────────────────────────────────────────────────────────────────
# PipelineSpec
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PipelineSpec:
    """
    Top-level painting specification.

    All adaptive stroke sizing derives from canvas dimensions + subject_frac,
    so a single pass list works correctly at any composition scale.
    """
    canvas_width:  int   = 780
    canvas_height: int   = 1080
    subject_frac:  float = 0.65   # fraction of short axis the subject occupies
    dpi:           int   = 96

    # Style
    sfumato_level: float = 0.0    # 0 = no sfumato, 1 = heavy sfumato
    two_pass:      bool  = False   # True = bg wash before subject passes
    artist_key:    str   = ""      # CATALOG key (e.g. "lovis_corinth")

    # Surface material for MaterialPass
    surface:       str   = "skin"  # "skin" | "feather" | "fur" | "scales" | "fabric"

    # ── Improvement #5: reproducibility & exploration ─────────────────────────
    # Change seed to generate a different but equally valid painting from the
    # same reference.  Drives Painter.__init__ so all passes share one stream.
    seed:          int   = 7

    # ── Improvement #2: stroke size variation ────────────────────────────────
    # Lognormal σ for per-stroke size.  0 = old uniform belt.  0.40 is a good
    # default; higher values (0.6+) produce a more expressive size range.
    stroke_size_sigma: float = 0.40

    # ── Improvement #9: composition map focal pull ────────────────────────────
    # 0 = pure error-driven placement; 1 = pure composition-map bias.
    focal_pull:    float = 0.40

    # ── Improvement #4: scene light source ───────────────────────────────────
    # Normalised (x, y) in [0, 1].  None = no light-coherent color shift.
    light_pos:     Optional[Tuple[float, float]] = None

    # ── Improvement #7: imprimatura reveal ───────────────────────────────────
    # Fraction of strokes skipped to let toned ground show through [0, 0.20].
    imprimatura_reveal: float = 0.0

    # ── Improvement #11: palette harmony ─────────────────────────────────────
    # Colour-wheel scheme applied to the artist palette to constrain sampling.
    # '' = off.  Options: 'complementary', 'analogous', 'triadic',
    # 'split_complementary', 'tetradic', 'double_split'.
    harmony_mode:  str   = ""
    # Snap strength [0, 1]: how hard to push strokes toward harmony colours.
    # 0.30 gives subtle cohesion; 0.60+ becomes visibly palette-constrained.
    harmony_snap:  float = 0.30

    # Ordered pass list (populated by default_passes() if left empty)
    passes:        List[PassConfig] = field(default_factory=list)

    @property
    def subject_px(self) -> float:
        """Pixel diameter of the primary subject."""
        return min(self.canvas_width, self.canvas_height) * self.subject_frac

    @property
    def stroke_base(self) -> float:
        """Baseline stroke width (subject_px / 200)."""
        return max(1.0, self.subject_px / 200.0)

    def stroke_for_scale(self, scale: float) -> float:
        """Return a stroke width for the given pass scale factor."""
        return max(1.0, self.stroke_base * scale)


# ─────────────────────────────────────────────────────────────────────────────
# Default pass list
# ─────────────────────────────────────────────────────────────────────────────

def default_passes(spec: PipelineSpec) -> List[PassConfig]:
    """
    Sensible default pass list for a portrait or creature painting.

    Sfumato and material passes are included only when requested.
    Adaptive stroke sizes derive from spec.stroke_base so the list is
    valid at any subject_frac / canvas size.

    Improvement #10 — non-linear drying curve: early passes (underpainting,
    block-in) dry quickly so bold marks have a firm base; later passes
    (build-form) dry more slowly so colour blends naturally.  Drying amounts
    are computed via Painter._drying_curve() with the stroke passes as the
    sequence (detail/finishing passes don't call canvas.dry).
    """
    sb = spec.stroke_base

    # Stroke passes that call canvas.dry() — compute non-linear drying amounts.
    # Index order matches the sequence: underpainting=0, block_in=1, build_form=2.
    # Total = 3 so the curve spans the foundational layer sequence.
    def dry(i: int, total: int = 3) -> float:
        """Cosine ease: 0.90 at i=0, ~0.65 at i=1, ~0.48 at i=2."""
        t    = i / max(total - 1, 1)
        ease = 0.5 * (1.0 - __import__("math").cos(__import__("math").pi * t))
        return round(0.90 + (0.42 - 0.90) * ease, 3)

    passes: List[PassConfig] = [
        # Foundational passes — large brushes, loose structure
        PassConfig("underpainting", kwargs=dict(
            stroke_size=int(sb * 8), opacity=0.60,
            dry_amount=dry(0),
        )),
        PassConfig("block_in", kwargs=dict(
            stroke_size=int(sb * 5), opacity=0.55,
            dry_amount=dry(1),
        )),
        PassConfig("build_form", kwargs=dict(
            stroke_size=int(sb * 3), opacity=0.50,
            dry_amount=dry(2),
        )),
        PassConfig("place_lights",  kwargs=dict(stroke_size=int(sb * 2), opacity=0.45)),
        # Refinement passes — fine strokes before filter-based detail
        PassConfig("build_form", kwargs=dict(
            stroke_size=max(1, int(sb * 1.5)), opacity=0.45,
        )),
        PassConfig("place_lights", kwargs=dict(stroke_size=max(1, int(sb * 1)), opacity=0.40)),
        # Detail passes — fine marks, frequency-targeted
        PassConfig("meso_detail_pass",     kwargs=dict(opacity=0.35)),
        PassConfig("micro_detail_pass",    kwargs=dict(opacity=0.28)),
        PassConfig("edge_definition_pass", kwargs=dict(opacity=0.30)),
        # Focal sharpening with peripheral softness — classical lost-and-found edges
        PassConfig("edge_lost_and_found_pass", kwargs=dict(strength=0.35, figure_only=True)),
        # Surface material
        PassConfig(spec.surface, kind="material", kwargs=dict(opacity=0.35)),
        # Dry-brush scumble — deposits on texture peaks, breaks up dissolved look
        PassConfig("scumble_pass", kwargs=dict(opacity=0.18, figure_only=True)),
    ]

    # Sfumato — only when the artist or user requests it
    if spec.sfumato_level > 0.0:
        passes.append(PassConfig(
            "sfumato_pass",
            kwargs=dict(opacity=float(spec.sfumato_level) * 0.40),
        ))

    # Tonal unification / finishing
    passes += [
        PassConfig("glazing_pass",             kwargs=dict(opacity=0.25)),
        PassConfig("chromatic_aberration_pass", kwargs=dict(opacity=0.12)),
        PassConfig("vignette_pass",            kwargs=dict(opacity=0.30)),
    ]

    return passes


# ─────────────────────────────────────────────────────────────────────────────
# PaintingSession
# ─────────────────────────────────────────────────────────────────────────────

class PaintingSession:
    """
    Orchestrates a complete painting from reference through final PNG export.

    Parameters
    ----------
    spec : PipelineSpec driving all sizing, style, and pass selection
    """

    def __init__(self, spec: PipelineSpec):
        self.spec = spec
        if not spec.passes:
            spec.passes = default_passes(spec)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_reference(
        self,
        ref_spec=None,
        reference: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        from reference_builder import ReferenceBuilder, ReferenceSpec
        if reference is not None:
            return reference
        rs = ref_spec or ReferenceSpec(
            H=self.spec.canvas_height,
            W=self.spec.canvas_width,
            subject_frac=self.spec.subject_frac,
        )
        return ReferenceBuilder(rs).build_portrait()

    def _build_painter(self, reference: np.ndarray):
        from art_utils import ArtCanvas
        from stroke_engine import Painter
        from art_catalog import CATALOG

        W, H = self.spec.canvas_width, self.spec.canvas_height
        artist_data = (CATALOG.get(self.spec.artist_key, {})
                       if self.spec.artist_key else {})
        canvas  = ArtCanvas(W, H)
        # Improvement #5: forward spec seed so all passes share one RNG stream.
        painter = Painter(W, H, seed=self.spec.seed)
        return painter

    def _apply_pass(
        self,
        painter,
        pass_cfg: PassConfig,
        subject_mask: Optional[np.ndarray],
        direction_field: Optional[np.ndarray],
    ) -> None:
        if not pass_cfg.enabled:
            return
        kw   = dict(pass_cfg.kwargs)
        name = pass_cfg.name
        kind = pass_cfg.kind
        print(f"  [{kind}] {name} ...")

        if kind == "stroke_engine":
            fn = getattr(painter, name, None)
            if fn is None:
                print(f"    WARNING: Painter has no method '{name}', skipping.")
                return
            fn(**kw)

        elif kind == "material":
            from material_passes import get_material_pass, MaterialParams
            mp = get_material_pass(
                name,
                params=MaterialParams(
                    opacity=kw.pop("opacity", 0.35),
                    subject_mask=subject_mask,
                    direction_field=direction_field,
                ),
                **kw,
            )
            mp.apply(painter.canvas.surface)

        elif kind == "mark_maker":
            # Mark-maker passes are called externally; session loop is a stub.
            print(f"    INFO: mark_maker passes must be called via MarkMaker.mark() "
                  f"directly — skipping session-level dispatch.")

        else:
            print(f"    WARNING: unknown pass kind '{kind}', skipping.")

    def _two_pass_background(self, painter) -> None:
        """Lightweight background wash before the main subject pass list."""
        sb = self.spec.stroke_base
        if hasattr(painter, "underpainting"):
            painter.underpainting(stroke_size=int(sb * 10), opacity=0.45)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def paint(
        self,
        output_path: str = "output.png",
        ref_spec=None,
        reference: Optional[np.ndarray] = None,
    ) -> str:
        """
        Execute the full painting pipeline and save to output_path.

        Parameters
        ----------
        output_path : destination PNG path
        ref_spec    : ReferenceSpec for building the synthetic reference
        reference   : pre-built H×W×3 float32 reference (overrides ref_spec)

        Returns output_path on success.
        """
        from reference_builder import ReferenceBuilder

        print(
            f"PaintingSession | "
            f"{self.spec.canvas_width}×{self.spec.canvas_height} | "
            f"artist={self.spec.artist_key or 'generic'} | "
            f"surface={self.spec.surface} | "
            f"sfumato={self.spec.sfumato_level:.2f} | "
            f"two_pass={self.spec.two_pass}"
        )

        ref = self._build_reference(ref_spec=ref_spec, reference=reference)

        rb              = ReferenceBuilder()
        subject_mask    = rb.build_subject_mask(ref)
        direction_field = rb.build_direction_field(ref)

        painter = self._build_painter(ref)

        if self.spec.two_pass:
            print("  [two-pass] background wash ...")
            self._two_pass_background(painter)

        for pass_cfg in self.spec.passes:
            self._apply_pass(painter, pass_cfg, subject_mask, direction_field)

        painter.canvas.save(output_path)
        print(f"  Saved → {output_path}")
        return output_path
