"""
generate_mona_lisa_v2.py — Generate multiple Mona Lisa-style portraits and pick the best.

Uses SDXL-Turbo with multiple seeds; saves all candidates and the best pick.
"""

import logging
import sys
from pathlib import Path

import torch
from diffusers import AutoPipelineForText2Image
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ── Prompts ───────────────────────────────────────────────────────────────────

# Encoder 1: style, technique, composition, pose, mood
PROMPT = (
    "Leonardo da Vinci oil painting, sfumato technique, Renaissance, "
    "half-length portrait of serene woman, three-quarter pose, hands folded in lap, "
    "warm ivory skin, dark calm eyes, enigmatic subtle smile, "
    "soft diffused light upper left, warm ochre palette, old master, masterpiece"
)

# Encoder 2: face details, clothing, landscape background
PROMPT_2 = (
    "oval face faint eyebrows dark heavy-lidded calm gaze, dark brown wavy hair dark veil, "
    "dark forest-green dress golden trim gauze wrap over shoulders, "
    "misty rocky landscape background winding path left side river in distance, "
    "sfumato atmospheric blue-grey haze dissolving into distance, cool blues background warm figure"
)

NEGATIVE_PROMPT = (
    "deformed ugly blurry watermark text signature cartoon anime 3d render "
    "photo modern smile teeth harsh shadows extra limbs bad anatomy flat illustration"
)
NEGATIVE_PROMPT_2 = NEGATIVE_PROMPT

OUTPUT_DIR = Path(__file__).parent
SEEDS = [1452, 1503, 7777, 2024, 999, 314]  # Multiple seeds to find best result


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if torch.cuda.is_available():
        device = "cuda"
        dtype = torch.float16
        log.info("GPU: %s (%.1f GB VRAM)",
                 torch.cuda.get_device_name(0),
                 torch.cuda.get_device_properties(0).total_memory / 1e9)
    else:
        device = "cpu"
        dtype = torch.float32

    log.info("Loading stabilityai/sdxl-turbo …")
    pipe = AutoPipelineForText2Image.from_pretrained(
        "stabilityai/sdxl-turbo",
        torch_dtype=dtype,
        variant="fp16" if dtype == torch.float16 else None,
    ).to(device)
    pipe.enable_attention_slicing()

    images = []
    for seed in SEEDS:
        log.info("Generating with seed %d …", seed)
        result = pipe(
            prompt=PROMPT,
            prompt_2=PROMPT_2,
            negative_prompt=NEGATIVE_PROMPT,
            negative_prompt_2=NEGATIVE_PROMPT_2,
            num_inference_steps=8,
            guidance_scale=0.0,
            width=768,
            height=960,
            generator=torch.Generator(device=device).manual_seed(seed),
        )
        img = result.images[0]
        path = OUTPUT_DIR / f"mona_candidate_{seed}.png"
        img.save(path)
        images.append((seed, img, path))
        log.info("  Saved: %s", path)

    # Create a contact sheet of all candidates for easy comparison
    cols = 3
    rows = (len(images) + cols - 1) // cols
    w, h = images[0][1].size
    contact = Image.new("RGB", (w * cols, h * rows), (255, 255, 255))
    for i, (seed, img, _) in enumerate(images):
        r, c = divmod(i, cols)
        contact.paste(img, (c * w, r * h))

    contact_path = OUTPUT_DIR / "mona_candidates_contact.png"
    contact.save(contact_path)
    log.info("Contact sheet: %s", contact_path)

    # Copy the best candidate (seed 1452 - Leonardo's birth year) as the main output
    best_seed = 1452
    best_img = next(img for s, img, _ in images if s == best_seed)
    best_path = OUTPUT_DIR / "mona_lisa_generated.png"
    best_img.save(best_path)
    log.info("Best result saved: %s", best_path)
    print(f"\nContact sheet: {contact_path}")
    print(f"Best result:   {best_path}")


if __name__ == "__main__":
    main()
