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
from typing import Any, Dict, List, Optional

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
    """
    sb = spec.stroke_base
    passes: List[PassConfig] = [
        # Foundational passes — large brushes, loose structure
        PassConfig("underpainting", kwargs=dict(stroke_size=int(sb * 8), opacity=0.60)),
        PassConfig("block_in",      kwargs=dict(stroke_size=int(sb * 5), opacity=0.55)),
        PassConfig("build_form",    kwargs=dict(stroke_size=int(sb * 3), opacity=0.50)),
        PassConfig("place_lights",  kwargs=dict(stroke_size=int(sb * 2), opacity=0.45)),
        # Detail passes — fine marks, frequency-targeted
        PassConfig("meso_detail_pass",     kwargs=dict(opacity=0.35)),
        PassConfig("micro_detail_pass",    kwargs=dict(opacity=0.28)),
        PassConfig("edge_definition_pass", kwargs=dict(opacity=0.30)),
        # Surface material
        PassConfig(spec.surface, kind="material", kwargs=dict(opacity=0.35)),
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
        painter = Painter(canvas, reference, artist_data)
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
