"""
generate_mona_lisa.py — Generate a Mona Lisa-style oil painting using Stable Diffusion.

Uses stabilityai/sdxl-turbo for fast, high-quality generation.
Saves result to mona_lisa_generated.png in the project directory.
"""

import logging
import sys
from pathlib import Path

import torch
from diffusers import AutoPipelineForText2Image
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ── Prompt ────────────────────────────────────────────────────────────────────

# SDXL has two CLIP text encoders. Each is limited to 77 tokens.
# prompt  → encoder 1 (ViT-L/14, more style/composition-focused)
# prompt_2 → encoder 2 (ViT-bigG/14, more semantic/content-focused)
# Splitting the description across both to maximize coverage.

# Encoder 1: style, technique, composition, pose
PROMPT = (
    "Leonardo da Vinci oil painting, sfumato, Renaissance portrait, "
    "half-length woman three-quarter pose body right head facing viewer, "
    "hands folded in lap, warm ivory skin, dark heavy-lidded eyes, "
    "enigmatic slight smile, soft diffused light upper left, "
    "old master glazing technique, warm ochres raw umbers, masterpiece"
)

# Encoder 2: facial details, clothing, background landscape
PROMPT_2 = (
    "oval face faint eyebrows dark calm gaze straight nose small lips, "
    "dark brown hair center-parted waves dark veil, "
    "dark forest-green dress gold neckline trim gauze shawl, "
    "rocky misty landscape background winding road left river middle distance, "
    "sfumato blue-grey atmospheric haze, cool background warm figure"
)

NEGATIVE_PROMPT = (
    "deformed, ugly, blurry, watermark, text, signature, cartoon, anime, "
    "3d render, photo, modern, smile teeth, harsh shadows, extra limbs, bad anatomy"
)

NEGATIVE_PROMPT_2 = NEGATIVE_PROMPT

OUTPUT_PATH = Path(__file__).parent / "mona_lisa_generated.png"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    # Resolve device
    if torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
        log.info("Using CUDA — GPU: %s (%.1f GB VRAM)",
                 torch.cuda.get_device_name(0),
                 torch.cuda.get_device_properties(0).total_memory / 1e9)
    else:
        device = "cpu"
        dtype = torch.float32
        log.warning("CUDA not available — using CPU (very slow)")

    # Load SDXL-Turbo
    model_id = "stabilityai/sdxl-turbo"
    log.info("Loading model: %s …", model_id)
    pipe = AutoPipelineForText2Image.from_pretrained(
        model_id,
        torch_dtype=dtype,
        variant="fp16" if dtype == torch.float16 else None,
    )
    pipe = pipe.to(device)

    # Enable attention slicing to reduce peak VRAM usage
    pipe.enable_attention_slicing()

    log.info("Generating portrait …")
    # SDXL-Turbo: guidance_scale=0.0 is optimal (distillation-based)
    # prompt_2 targets the second (larger) CLIP encoder for additional detail
    result = pipe(
        prompt=PROMPT,
        prompt_2=PROMPT_2,
        negative_prompt=NEGATIVE_PROMPT,
        negative_prompt_2=NEGATIVE_PROMPT_2,
        num_inference_steps=8,
        guidance_scale=0.0,   # Turbo uses distillation — guidance=0 is optimal
        width=768,
        height=960,           # Portrait aspect ratio (4:5)
        generator=torch.Generator(device=device).manual_seed(1452),  # Leonardo's birth year
    )

    image: Image.Image = result.images[0]
    image.save(OUTPUT_PATH)
    log.info("Saved to: %s", OUTPUT_PATH)
    print(f"\nImage saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
