"""
sd_bridge.py — Stable Diffusion optional aesthetic reference generator.

Wraps HuggingFace diffusers to provide two modes:
  - img2img: refines an existing Blender render at low strength (0.25–0.40),
    preserving pose/structure while injecting SD's aesthetic coherence.
  - text2img: generates a reference from scratch when no Blender render exists.

Graceful degradation: if torch or diffusers are not installed, or CUDA is not
available, all methods return the input image unchanged (or a placeholder array).

Lazy loading: the model is not loaded until first use — weights are large and
the pipeline must remain importable even in environments without GPU/diffusers.
"""

from __future__ import annotations
import logging
from typing import Optional, Tuple

import numpy as np

from scene_schema import Period, Medium

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Period → art-historical prompt descriptor
# ─────────────────────────────────────────────────────────────────────────────

_PERIOD_DESCRIPTORS: dict[Period, str] = {
    Period.RENAISSANCE:              "renaissance oil painting, sfumato, classical composition",
    Period.BAROQUE:                  "baroque oil painting, chiaroscuro, dramatic shadows",
    Period.IMPRESSIONIST:            "impressionist painting, visible brushwork, dappled light",
    Period.EXPRESSIONIST:            "expressionist painting, distorted forms, emotional intensity",
    Period.POINTILLIST:              "pointillist painting, tiny dots of pure color, optical mixing",
    Period.ROMANTIC:                 "romantic era painting, atmospheric, emotional, luminous",
    Period.ART_NOUVEAU:              "art nouveau painting, decorative gold leaf, ornamental",
    Period.UKIYO_E:                  "ukiyo-e woodblock print, flat color, bold outlines, Japanese",
    Period.PROTO_EXPRESSIONIST:      "dark expressionist painting, black void, crude urgent marks",
    Period.REALIST:                  "realist painting, flat value planes, bold black, objective",
    Period.VIENNESE_EXPRESSIONIST:   "viennese expressionist painting, angular contour, psychological",
    Period.COLOR_FIELD:              "color field painting, luminous horizontal bands, absorbing void",
    Period.SYNTHETIST:               "synthetist painting, flat color zones, cloisonne contour lines",
    Period.MANNERIST:                "mannerist painting, elongated figures, jewel-tone palette",
    Period.SURREALIST:               "surrealist painting, folk art zones, saturated palette",
    Period.ABSTRACT_EXPRESSIONIST:   "abstract expressionist painting, geometric resonance, synesthetic",
    Period.VENETIAN_RENAISSANCE:     "venetian renaissance oil painting, rich colourism, warm glazing",
    Period.FAUVIST:                  "fauvist painting, maximum saturation, flat zones, bold color",
    Period.PRIMITIVIST:              "primitivist painting, oval mask faces, elongated necks, ochre",
    Period.EARLY_NETHERLANDISH:      "early netherlandish oil painting, transparent glazes, flemish detail",
    Period.ART_DECO:                 "art deco painting, smooth cubist facets, metallic gloss",
    Period.NABIS:                    "nabis intimiste painting, pattern-ground fusion, flat muted zones",
    Period.LUMINISMO:                "luminismo painting, maximum sunlight, mediterranean brilliance",
    Period.HIGH_RENAISSANCE:         "high renaissance oil painting, luminous clarity, idealized form",
    Period.TENEBRIST:                "tenebrist painting, near-black void, hyper-real white fabric",
    Period.NEOCLASSICAL:             "neoclassical oil painting, smooth brushwork, idealized forms, porcelain",
    Period.NOCTURNE:                 "nocturne candlelight painting, single candle, warm amber glow, darkness",
    Period.CONTEMPORARY:             "contemporary fine art painting",
    Period.FANTASY_ART:              "fantasy illustration, detailed, dramatic lighting",
    Period.NONE:                     "fine art painting",
}

_MEDIUM_DESCRIPTORS: dict[Medium, str] = {
    Medium.OIL:       "oil on canvas",
    Medium.WATERCOLOR: "watercolor on paper",
    Medium.INK_WASH:  "ink wash on paper",
    Medium.CHARCOAL:  "charcoal on paper",
    Medium.GOUACHE:   "gouache on board",
    Medium.DIGITAL:   "digital painting",
}

_QUALITY_BOOSTERS = (
    "masterpiece, highly detailed, museum quality, dramatic lighting, "
    "professional art, old master technique"
)

_NEGATIVE_PROMPT = (
    "deformed, ugly, blurry, watermark, text, signature, cartoon, anime, "
    "3d render, plastic, overexposed, underexposed, noise, oversaturated"
)


# ─────────────────────────────────────────────────────────────────────────────
# SDRefGenerator
# ─────────────────────────────────────────────────────────────────────────────

class SDRefGenerator:
    """
    Optional Stable Diffusion reference image generator/refiner.

    Uses img2img to refine Blender renders aesthetically while preserving
    structural information (pose, proportions, lighting direction).
    Falls back gracefully if diffusers/torch not available.

    Usage::

        gen = SDRefGenerator()
        prompt, neg = gen.build_prompt(scene)
        refined = gen.refine(blender_render_array, prompt, neg, strength=0.30)
    """

    def __init__(
        self,
        model_id: str = "stabilityai/stable-diffusion-xl-base-1.0",
        device: str = "auto",
    ) -> None:
        """
        Initialise the generator (does NOT load the model).

        Args:
            model_id: HuggingFace model identifier for the SD checkpoint.
            device:   ``"auto"`` selects CUDA → MPS → CPU in that order.
                      Pass ``"cpu"``, ``"cuda"``, or ``"mps"`` to override.
        """
        self.model_id = model_id
        self.device = device
        self._available: Optional[bool] = None   # None = not checked yet
        self._i2i_pipe = None
        self._t2i_pipe = None

    # ── Lazy loader ───────────────────────────────────────────────────────────

    def _load(self) -> None:
        """
        Lazily import diffusers/torch and load both pipelines.

        Sets ``self._available`` to True on success, False on any import or
        load failure so subsequent calls short-circuit immediately.
        """
        if self._available is not None:
            return

        try:
            import torch
            from diffusers import AutoPipelineForImage2Image, AutoPipelineForText2Image
        except ImportError:
            logger.warning(
                "sd_bridge: diffusers or torch not installed. "
                "SD refinement unavailable — install with: "
                "pip install diffusers accelerate"
            )
            self._available = False
            return

        # Resolve device
        device = self.device
        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
                logger.warning(
                    "sd_bridge: CUDA unavailable — using CPU. "
                    "Inference will be very slow (~5–30 min per image)."
                )

        dtype = torch.float16 if device in ("cuda", "mps") else torch.float32

        try:
            logger.info("sd_bridge: loading %s on %s …", self.model_id, device)
            self._i2i_pipe = AutoPipelineForImage2Image.from_pretrained(
                self.model_id, torch_dtype=dtype
            ).to(device)
            self._i2i_pipe.enable_model_cpu_offload()

            self._t2i_pipe = AutoPipelineForText2Image.from_pretrained(
                self.model_id, torch_dtype=dtype
            ).to(device)
            self._t2i_pipe.enable_model_cpu_offload()

            self._available = True
            logger.info("sd_bridge: model loaded successfully.")
        except Exception as exc:
            logger.warning("sd_bridge: model load failed (%s) — SD unavailable.", exc)
            self._available = False

    # ── Prompt builder ────────────────────────────────────────────────────────

    def build_prompt(self, scene) -> Tuple[str, str]:
        """
        Convert a :class:`~scene_schema.Scene` to a (prompt, negative_prompt) pair.

        The prompt encodes:
        - Art-historical period descriptor
        - Paint medium
        - Subject description (age, sex, skin tone, expression, costume)
        - Key light color and intensity hint
        - Quality booster tokens

        Args:
            scene: A :class:`~scene_schema.Scene` instance.

        Returns:
            Tuple of ``(prompt, negative_prompt)`` strings.
        """
        style  = scene.style
        period = style.period
        medium = style.medium

        # Period and medium descriptors
        period_desc = _PERIOD_DESCRIPTORS.get(period, "fine art painting")
        medium_desc = _MEDIUM_DESCRIPTORS.get(medium, "oil on canvas")

        # Subject descriptors
        subject_parts = []
        for subj in scene.subjects:
            parts = []
            parts.append(subj.age.name.lower().replace("_", " ") + " person")
            if subj.sex.name != "UNSPECIFIED":
                parts[0] = subj.age.name.lower() + " " + subj.sex.name.lower()
            parts.append(subj.skin_tone.name.lower().replace("_", " ") + " skin tone")
            parts.append(subj.expression.name.lower().replace("_", " ") + " expression")
            if subj.hair_style.name != "BALD":
                parts.append(subj.hair_style.name.lower().replace("_", " ") + " hair")
            if subj.costume.top:
                parts.append(subj.costume.top)
            subject_parts.append(", ".join(parts))

        subject_desc = "; ".join(subject_parts) if subject_parts else "portrait subject"

        # Lighting hint from key light (first light in rig, or default)
        lighting_hint = ""
        if scene.lighting.lights:
            key = scene.lighting.lights[0]
            r, g, b = key.color
            if r > g and r > b:
                lighting_hint = "warm golden light"
            elif b > r and b > g:
                lighting_hint = "cool blue-tinted light"
            else:
                lighting_hint = "neutral white light"
            if key.intensity > 150:
                lighting_hint += ", dramatic contrast"

        prompt_parts = [
            period_desc,
            medium_desc,
            subject_desc,
        ]
        if lighting_hint:
            prompt_parts.append(lighting_hint)
        prompt_parts.append(_QUALITY_BOOSTERS)

        prompt = ", ".join(prompt_parts)
        return prompt, _NEGATIVE_PROMPT

    # ── img2img ───────────────────────────────────────────────────────────────

    def refine(
        self,
        image: np.ndarray,
        prompt: str,
        negative_prompt: str = "",
        strength: float = 0.30,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 30,
        seed: Optional[int] = None,
    ) -> np.ndarray:
        """
        Refine a Blender render with SD img2img at low strength.

        At the default strength of 0.30 the pose and proportions from the
        Blender render are preserved almost entirely; SD contributes aesthetic
        coherence (brushwork impression, colour temperature, tonal richness).

        Falls back to returning ``image`` unchanged if SD is unavailable.

        Args:
            image:              H×W×3 numpy array (uint8 or float32 [0,1]).
            prompt:             Positive text prompt.
            negative_prompt:    Negative text prompt.
            strength:           How much SD changes the image (0 = none, 1 = full).
                                Keep in [0.25, 0.40] to preserve structure.
            guidance_scale:     Classifier-free guidance scale.
            num_inference_steps: Denoising steps. 20–30 is usually sufficient.
            seed:               Random seed for reproducibility. None = random.

        Returns:
            Refined H×W×3 uint8 numpy array, or the original if SD unavailable.
        """
        self._load()
        if not self._available:
            return _ensure_uint8(image)

        import torch
        from PIL import Image as PILImage

        pil_img = _numpy_to_pil(image)

        generator = torch.Generator().manual_seed(seed) if seed is not None else None

        result = self._i2i_pipe(
            prompt=prompt,
            negative_prompt=negative_prompt or _NEGATIVE_PROMPT,
            image=pil_img,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            generator=generator,
        ).images[0]

        return _pil_to_numpy(result)

    # ── text2img ──────────────────────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 30,
        seed: Optional[int] = None,
    ) -> np.ndarray:
        """
        Generate a reference image from text when no Blender render is available.

        Args:
            prompt:             Positive text prompt.
            negative_prompt:    Negative text prompt.
            width:              Output width in pixels (must be divisible by 8).
            height:             Output height in pixels (must be divisible by 8).
            guidance_scale:     Classifier-free guidance scale.
            num_inference_steps: Denoising steps.
            seed:               Random seed for reproducibility. None = random.

        Returns:
            H×W×3 uint8 numpy array, or a black placeholder if SD unavailable.
        """
        self._load()
        if not self._available:
            logger.warning("sd_bridge: SD unavailable — returning black placeholder.")
            return np.zeros((height, width, 3), dtype=np.uint8)

        import torch

        generator = torch.Generator().manual_seed(seed) if seed is not None else None

        result = self._t2i_pipe(
            prompt=prompt,
            negative_prompt=negative_prompt or _NEGATIVE_PROMPT,
            width=width,
            height=height,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            generator=generator,
        ).images[0]

        return _pil_to_numpy(result)


# ─────────────────────────────────────────────────────────────────────────────
# Module-level convenience
# ─────────────────────────────────────────────────────────────────────────────

# Module-level singleton — created on first use
_default_generator: Optional[SDRefGenerator] = None


def sd_refine_reference(
    image: np.ndarray,
    scene,
    strength: float = 0.30,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    One-call interface: build a prompt from ``scene``, then refine ``image``.

    Uses a module-level :class:`SDRefGenerator` singleton so the model is only
    loaded once per process.  Returns ``image`` unchanged if SD is unavailable.

    Args:
        image:    H×W×3 numpy array (the Blender render to refine).
        scene:    A :class:`~scene_schema.Scene` instance for prompt building.
        strength: img2img denoising strength (0.25–0.40 recommended).
        seed:     Random seed for reproducibility. None = random.

    Returns:
        Refined H×W×3 uint8 numpy array.
    """
    global _default_generator
    if _default_generator is None:
        _default_generator = SDRefGenerator()

    prompt, neg = _default_generator.build_prompt(scene)
    return _default_generator.refine(image, prompt, neg, strength=strength, seed=seed)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_uint8(arr: np.ndarray) -> np.ndarray:
    """Convert float32 [0,1] array to uint8 [0,255], or pass uint8 through."""
    if arr.dtype == np.uint8:
        return arr
    return (np.clip(arr, 0.0, 1.0) * 255).astype(np.uint8)


def _numpy_to_pil(arr: np.ndarray):
    """Convert H×W×3 numpy array (uint8 or float32) to PIL Image (RGB)."""
    from PIL import Image as PILImage
    uint8 = _ensure_uint8(arr)
    return PILImage.fromarray(uint8, mode="RGB")


def _pil_to_numpy(pil_img) -> np.ndarray:
    """Convert a PIL Image to H×W×3 uint8 numpy array."""
    import numpy as _np
    return _np.array(pil_img.convert("RGB"), dtype=_np.uint8)
