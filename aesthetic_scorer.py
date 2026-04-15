"""
aesthetic_scorer.py — LAION Aesthetic Predictor v2 and feedback loop.

The LAION Aesthetic Predictor v2 is a small MLP (5 linear layers) trained on
top of CLIP ViT-L/14 embeddings to predict human aesthetic scores (1–10).
It is fast (~20 ms per image on CPU after CLIP encoding).

Graceful degradation: if torch or clip are not installed, AestheticScorer
returns 5.0 (neutral) for all images so the feedback loop logic can still
operate structurally.

Usage::

    scorer = AestheticScorer()
    score  = scorer.score(image_array)   # float in [0, 10]

    loop = AestheticFeedbackLoop(scorer, target_score=7.0)
    info = loop.checkpoint(painter, "block_in")
    if loop.should_apply_remediation():
        ...
"""

from __future__ import annotations
import logging
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# AestheticScorer
# ─────────────────────────────────────────────────────────────────────────────

class AestheticScorer:
    """
    LAION Aesthetic Predictor v2.

    Scores images on a 1–10 aesthetic quality scale using a small MLP
    on top of CLIP ViT-L/14 image embeddings.

    Requires: torch plus either openai/clip or transformers (CLIP).
    Falls back gracefully if unavailable — returns 5.0 (neutral) for all
    images so that :class:`AestheticFeedbackLoop` logic remains functional.

    Usage::

        scorer = AestheticScorer()
        score  = scorer.score(image_array)
    """

    # LAION Aesthetic Predictor v2 MLP architecture constants
    _MLP_DIMS = [(768, 1024), (1024, 128), (128, 64), (64, 16), (16, 1)]
    _DROPOUT   = [0.2, 0.2, 0.1, 0.0, 0.0]   # dropout before each linear layer

    def __init__(self, device: str = "auto") -> None:
        """
        Initialise the scorer (does NOT load the model).

        Args:
            device: ``"auto"`` selects CUDA → MPS → CPU. Override with
                    ``"cpu"``, ``"cuda"``, or ``"mps"`` as needed.
        """
        self.device = device
        self._available: Optional[bool] = None   # None = not checked yet
        self._clip_model  = None
        self._clip_preprocess = None
        self._mlp         = None
        self._clip_backend: Optional[str] = None  # "openai_clip" | "transformers"
        self._torch_device = None

    # ── Lazy loader ───────────────────────────────────────────────────────────

    def _load(self) -> None:
        """
        Lazily import torch and CLIP, then load both models.

        Tries openai/clip first, falls back to transformers CLIPModel.
        Sets ``self._available`` to False on any failure so subsequent
        calls short-circuit and return the 5.0 neutral sentinel.
        """
        if self._available is not None:
            return

        try:
            import torch
        except ImportError:
            logger.warning(
                "aesthetic_scorer: torch not installed — scoring disabled. "
                "Install with: pip install torch"
            )
            self._available = False
            return

        # Resolve device
        device_str = self.device
        if device_str == "auto":
            if torch.cuda.is_available():
                device_str = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device_str = "mps"
            else:
                device_str = "cpu"
        self._torch_device = torch.device(device_str)

        # Load CLIP — try openai/clip first, fall back to transformers
        clip_loaded = False
        try:
            import clip as openai_clip
            model, preprocess = openai_clip.load("ViT-L/14", device=device_str)
            self._clip_model      = model
            self._clip_preprocess = preprocess
            self._clip_backend    = "openai_clip"
            clip_loaded = True
            logger.info("aesthetic_scorer: loaded CLIP via openai/clip.")
        except ImportError:
            pass
        except Exception as exc:
            logger.warning("aesthetic_scorer: openai/clip load failed (%s).", exc)

        if not clip_loaded:
            try:
                from transformers import CLIPModel, CLIPProcessor
                clip_name = "openai/clip-vit-large-patch14"
                self._clip_model      = CLIPModel.from_pretrained(clip_name).to(device_str)
                self._clip_preprocess = CLIPProcessor.from_pretrained(clip_name)
                self._clip_backend    = "transformers"
                clip_loaded = True
                logger.info("aesthetic_scorer: loaded CLIP via transformers.")
            except ImportError:
                logger.warning(
                    "aesthetic_scorer: neither openai/clip nor transformers available. "
                    "Install with: pip install git+https://github.com/openai/CLIP.git "
                    "OR: pip install transformers"
                )
                self._available = False
                return
            except Exception as exc:
                logger.warning("aesthetic_scorer: transformers CLIP load failed (%s).", exc)
                self._available = False
                return

        # Build MLP
        self._mlp = self._build_mlp(torch)
        self._mlp = self._mlp.to(self._torch_device)
        self._mlp.eval()

        # Load pretrained aesthetic predictor weights
        self._load_mlp_weights(torch)

        self._available = True

    def _build_mlp(self, torch):
        """
        Build the LAION Aesthetic Predictor v2 MLP.

        Architecture (input: 768-dim CLIP ViT-L/14 embedding → scalar):
            Linear(768→1024) → Dropout(0.2) → Linear(1024→128) →
            Dropout(0.2) → Linear(128→64) → Dropout(0.1) →
            Linear(64→16) → Linear(16→1)
        """
        import torch.nn as nn
        layers = []
        for i, (in_dim, out_dim) in enumerate(self._MLP_DIMS):
            dropout_p = self._DROPOUT[i]
            if dropout_p > 0:
                layers.append(nn.Dropout(dropout_p))
            layers.append(nn.Linear(in_dim, out_dim))
            # No activation after the final layer — raw logit
            if i < len(self._MLP_DIMS) - 1:
                layers.append(nn.ReLU())
        return nn.Sequential(*layers)

    def _load_mlp_weights(self, torch) -> None:
        """
        Attempt to download pretrained aesthetic predictor weights.

        Tries the shunk031/aesthetics-predictor checkpoint from HuggingFace.
        If the download fails (offline, no hub access) falls back to random
        weights with a warning — scores won't be calibrated but the feedback
        loop structure remains fully functional.
        """
        try:
            from huggingface_hub import hf_hub_download
            weights_path = hf_hub_download(
                repo_id="shunk031/aesthetics-predictor",
                filename="sac+logos+ava1-l14-linearMSE.pth",
            )
            state = torch.load(weights_path, map_location=self._torch_device)
            self._mlp.load_state_dict(state, strict=False)
            logger.info("aesthetic_scorer: aesthetic predictor weights loaded.")
        except Exception as exc:
            logger.warning(
                "aesthetic_scorer: could not load pretrained weights (%s). "
                "Using random weights — scores are uncalibrated but the "
                "feedback loop logic still works structurally.",
                exc,
            )

    # ── Scoring ───────────────────────────────────────────────────────────────

    def score(self, image: np.ndarray) -> float:
        """
        Score an image on a 1–10 aesthetic quality scale.

        The image is CLIP-encoded and the 768-dim embedding passed through the
        LAION Aesthetic Predictor v2 MLP.  The raw scalar output is mapped to
        [0, 10] via sigmoid × 10.

        Args:
            image: H×W×3 numpy array (uint8 or float32 [0,1]).

        Returns:
            Aesthetic score as float in [0, 10].  Returns 5.0 (neutral) if
            CLIP/torch are not available.
        """
        self._load()
        if not self._available:
            return 5.0

        import torch

        embedding = self._clip_embed(image)        # (1, 768) tensor
        with torch.no_grad():
            raw = self._mlp(embedding)             # (1, 1)
            score_val = torch.sigmoid(raw) * 10.0  # map to [0, 10]
        return float(score_val.item())

    def score_canvas(self, painter) -> float:
        """
        Score the current state of a :class:`~stroke_engine.Painter` canvas.

        Reads pixel data from the painter's cairo surface, converts it to a
        numpy array, and calls :meth:`score`.

        Args:
            painter: A :class:`~stroke_engine.Painter` instance.

        Returns:
            Aesthetic score as float in [0, 10].
        """
        image = _painter_to_numpy(painter)
        return self.score(image)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _clip_embed(self, image: np.ndarray):
        """
        Compute CLIP ViT-L/14 image embedding for the given numpy array.

        Returns a (1, 768) torch tensor on ``self._torch_device``.
        """
        import torch
        from PIL import Image as PILImage

        pil_img = _numpy_to_pil(image)

        if self._clip_backend == "openai_clip":
            tensor = self._clip_preprocess(pil_img).unsqueeze(0).to(self._torch_device)
            with torch.no_grad():
                features = self._clip_model.encode_image(tensor)
            # Normalise to unit hypersphere (standard LAION predictor practice)
            features = features / features.norm(dim=-1, keepdim=True)
            return features.float()

        # transformers backend
        inputs = self._clip_preprocess(images=pil_img, return_tensors="pt")
        inputs = {k: v.to(self._torch_device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self._clip_model.get_image_features(**inputs)
        outputs = outputs / outputs.norm(dim=-1, keepdim=True)
        return outputs.float()


# ─────────────────────────────────────────────────────────────────────────────
# AestheticFeedbackLoop
# ─────────────────────────────────────────────────────────────────────────────

class AestheticFeedbackLoop:
    """
    Wraps :class:`AestheticScorer` to provide adaptive pass selection.

    Tracks score history across painting passes and makes decisions:

    - Gate passes that would degrade quality (via :meth:`checkpoint` ``ok`` flag).
    - Signal when additional remediation passes are needed
      (:meth:`should_apply_remediation`).
    - Decide when the painting is "good enough" to stop (:meth:`is_finished`).
    - Recommend additional passes based on score trajectory (:meth:`recommend_passes`).

    Usage::

        scorer = AestheticScorer()
        loop   = AestheticFeedbackLoop(scorer, target_score=7.0)

        info = loop.checkpoint(painter, "block_in")
        print(info)  # {"pass": "block_in", "score": 5.8, "delta": ..., "ok": True}

        if loop.should_apply_remediation():
            painter.glaze(...)

        if loop.is_finished():
            break

        print(loop.summary())
    """

    def __init__(
        self,
        scorer: AestheticScorer,
        baseline_score: Optional[float] = None,
        min_acceptable: float = 5.5,
        target_score: float = 7.0,
    ) -> None:
        """
        Args:
            scorer:          An :class:`AestheticScorer` instance.
            baseline_score:  Aesthetic score of the reference image being
                             painted from.  None if unknown.
            min_acceptable:  Minimum acceptable score; scores below this
                             trigger stronger remediation recommendations.
            target_score:    Score at which the painting is considered done.
        """
        self.scorer         = scorer
        self.baseline_score = baseline_score
        self.min_acceptable = min_acceptable
        self.target_score   = target_score

        # Each entry: (pass_name, score_float)
        self.history: List[Tuple[str, float]] = []

    # ── Checkpoint ────────────────────────────────────────────────────────────

    def checkpoint(self, painter, pass_name: str) -> dict:
        """
        Score the current canvas and record the checkpoint.

        Args:
            painter:   A :class:`~stroke_engine.Painter` instance.
            pass_name: Human-readable label for the current painting pass
                       (e.g. ``"block_in"``, ``"build_form"``).

        Returns:
            A dict with keys:

            - ``"pass"``:  The pass name.
            - ``"score"``: Current aesthetic score (float).
            - ``"delta"``: Score change from previous checkpoint (0.0 if first).
            - ``"ok"``:    True if score improved or degraded by less than 0.3.
        """
        current_score = self.scorer.score_canvas(painter)
        prev_score = self.history[-1][1] if self.history else current_score
        delta = current_score - prev_score
        ok = delta >= 0 or abs(delta) < 0.3

        self.history.append((pass_name, current_score))

        return {
            "pass":  pass_name,
            "score": current_score,
            "delta": delta,
            "ok":    ok,
        }

    # ── Remediation decision ──────────────────────────────────────────────────

    def should_apply_remediation(self) -> bool:
        """
        Return True if the last two checkpoints both showed a score decrease.

        When two consecutive passes degrade quality, the pipeline should apply
        a unifying glaze or tonal compression pass to recover cohesion.

        Returns:
            True if remediation is recommended.
        """
        if len(self.history) < 2:
            return False
        # Compare last two deltas
        scores = [s for _, s in self.history]
        return scores[-1] < scores[-2] and scores[-2] < scores[-3] if len(scores) >= 3 else (
            scores[-1] < scores[-2]
        )

    # ── Completion decision ───────────────────────────────────────────────────

    def is_finished(self) -> bool:
        """
        Return True when the painting is good enough to stop.

        Conditions (either is sufficient):
        - Current score >= ``target_score``.
        - Last three checkpoints are within 0.2 of each other (plateau).

        Returns:
            True if no further passes are recommended.
        """
        if not self.history:
            return False

        current_score = self.history[-1][1]
        if current_score >= self.target_score:
            return True

        # Plateau detection: last 3 scores all within 0.2 of each other
        if len(self.history) >= 3:
            recent = [s for _, s in self.history[-3:]]
            if max(recent) - min(recent) <= 0.2:
                return True

        return False

    # ── Pass recommendations ──────────────────────────────────────────────────

    def recommend_passes(self) -> List[str]:
        """
        Recommend additional passes based on score history trajectory.

        Returns a list of pass-name strings that the pipeline can act on:

        - ``["finish"]``            — score is at or above target.
        - ``["continue"]``          — score is low but trending upward.
        - ``["glaze", "tonal_compression"]`` — score low and flat/declining.
        - ``["rollback_hint"]``     — score degraded suddenly (signals pipeline).

        Returns:
            List of recommended pass name strings.
        """
        if not self.history:
            return ["continue"]

        current_score = self.history[-1][1]

        if current_score >= self.target_score:
            return ["finish"]

        if len(self.history) < 2:
            return ["continue"]

        scores = [s for _, s in self.history]
        recent_delta = scores[-1] - scores[-2]

        # Sudden degradation: drop of more than 0.5 in one pass
        if recent_delta < -0.5:
            return ["rollback_hint"]

        # Low score and trending upward
        if current_score < self.min_acceptable and recent_delta > 0:
            return ["continue"]

        # Low score and flat or declining
        if current_score < self.min_acceptable:
            return ["glaze", "tonal_compression"]

        # Score acceptable but not yet at target and trending up
        if recent_delta >= 0:
            return ["continue"]

        # Score acceptable but flat — consolidate
        return ["glaze"]

    # ── Summary ───────────────────────────────────────────────────────────────

    def summary(self) -> str:
        """
        Return a human-readable summary of score progression across passes.

        Returns:
            Multi-line string with per-pass scores, deltas, and a final
            verdict (finished / target / below-minimum).
        """
        if not self.history:
            return "AestheticFeedbackLoop: no checkpoints recorded."

        lines = ["Aesthetic score progression:"]
        prev = None
        for pass_name, score in self.history:
            if prev is None:
                delta_str = "      "
            else:
                d = score - prev
                delta_str = f"{d:+.2f}"
            lines.append(f"  {pass_name:<30s} {score:.2f}  {delta_str}")
            prev = score

        final = self.history[-1][1]
        if final >= self.target_score:
            verdict = f"FINISHED — target {self.target_score:.1f} reached."
        elif final >= self.min_acceptable:
            verdict = f"Acceptable ({self.min_acceptable:.1f}–{self.target_score:.1f}). More passes may help."
        else:
            verdict = f"Below minimum ({final:.2f} < {self.min_acceptable:.1f}). Remediation recommended."

        lines.append(verdict)
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _numpy_to_pil(arr: np.ndarray):
    """Convert H×W×3 numpy array (uint8 or float32 [0,1]) to PIL RGB Image."""
    from PIL import Image as PILImage
    if arr.dtype != np.uint8:
        arr = (np.clip(arr, 0.0, 1.0) * 255).astype(np.uint8)
    return PILImage.fromarray(arr, mode="RGB")


def _painter_to_numpy(painter) -> np.ndarray:
    """
    Extract pixel data from a cairo-backed Painter as an H×W×3 uint8 array.

    Reads the underlying cairo ImageSurface buffer via numpy.  Handles the
    cairo ARGB32 format (B G R A byte order on little-endian) by reordering
    channels to R G B.
    """
    import cairo
    surface = painter.surface   # cairo.ImageSurface expected
    width   = surface.get_width()
    height  = surface.get_height()

    # cairo stores ARGB32 in native byte order; on x86 this is BGRA
    buf  = surface.get_data()
    arr  = np.frombuffer(buf, dtype=np.uint8).reshape((height, width, 4))
    # Extract R, G, B channels (drop alpha; swap B↔R for cairo BGRA)
    rgb  = arr[:, :, [2, 1, 0]].copy()
    return rgb
