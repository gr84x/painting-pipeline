"""Post session 285 Discord painting to #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s285_collioure_harbor.png")
FILENAME   = "s285_collioure_harbor.png"

TEXT_BLOCKS = [
    """\
**Collioure au Midi** — Session 285

*Oil on linen · André Derain mode — 196th distinct mode · Fauve Intensity + Frequency Separation*

**Subject & Composition**

The fishing harbour of Collioure, France, seen from the stone quay at high noon in the summer of 1905 — the year André Derain and Henri Matisse discovered the village and invented Fauvism there. Three moored fishing boats dominate the foreground: one cadmium orange, one cobalt cerulean, one vivid vermillion. Their hulls are close and large, their masts pencil-thin against the sky. Behind them, the medieval harbour wall curves left toward the Tour du Château tower. Beyond the tower: the steep hillside of the town rises in tiers of whitewashed walls and orange tile roofs, punctuated by acid-green vegetation and deep violet shadow in the alleys. The sky is a single flat plane of electric cobalt blue. The horizon bisects the canvas at 52% height.""",

    """\
**The Environment**

The harbour water is not a naturalistic blue-green but a Fauve surface of competing colour zones: deep cobalt where the quay shadow falls, vivid cadmium-orange where the noon sun strikes directly, flashes of viridian where it catches the hillside vegetation, violet-grey in the interior shadow. The boat reflections are broken fragments of their hull colours, shimmering. The stone quay in the foreground is warm ochre with violet shadow pooling in the cracks — not grey. Nothing here is grey. The fortification tower at left is flat ochre-stone with a deep violet shadow on its right face. The hillside buildings glow in near-white noon light, their windows and doorways cut with vivid violet-purple voids. The sky is a declaration, not a description: pure cerulean blue, deep and flat, the way Derain called it "too blue to be real."

**Technique & Palette — André Derain (1880–1954)**

Fauvism, Collioure 1905. Palette built around three primary Fauve oppositions: cadmium orange vs. cobalt cerulean (the dominant boats), viridian vs. violet-crimson (hillside vs. shadows), cadmium yellow vs. deep navy (sky accent vs. harbour depth). Colours squeezed nearly unmixed. No neutral zones — shadows are vivid violet-blue, lights are vivid amber-orange.""",

    """\
**The New Pass — derain_fauve_intensity_pass (196th distinct mode)**

Four stages of novel Fauve mathematics:

**(1) HSV S-CHANNEL POWER CURVE:** RGB→HSV, S_new = S^sat_gamma (gamma=0.60, sub-unity). First pass to apply power-law transformation to the S (saturation) channel. Prior s284 pass rotated the H (hue) channel; no pass has operated on S directly. The sub-unity gamma expands all saturation toward maximum — weak colours gain the most.

**(2) SIX-SECTOR HUE COMMITMENT:** H divided into 6 spectral sectors (0–60°, 60–120°, 120–180°, 180–240°, 240–300°, 300–360°). Each sector pushed toward its canonical spectral hue, weighted by saturation. First pass with 6-sector hue classification and per-sector push targets. Prior passes push toward one fixed colour universally.

**(3) LOCAL COLOUR CONTRAST AMPLIFICATION:** For each channel: C_new = clip(C + (C − Gaussian(C, σ=14)) × amplify, 0, 1). First pass to amplify colour deviations from local neighbourhood mean uniformly across all channels without luminance gate. Models Chevreul's Simultaneous Contrast: adjacent complementary colours mutually intensify each other.

**(4) GRADIENT-ANGLE WARM/COOL PUSH:** dot = cos(atan2(Gy, Gx) − light_angle). First pass to use the full 2D gradient ANGLE (atan2) as a directional cosine zone gate. Light-facing pixels receive warm amber push; shadow-facing receive cool cobalt push. Prior passes use G_mag only, or fixed-axis Gx only.""",

    """\
**Improvement — paint_frequency_separation_pass**

A Laplacian pyramid decomposition — first technique in this engine to separate the canvas into independent spatial-frequency components:

  low_freq = Gaussian(canvas, σ=16) — broad colour masses
  high_freq = canvas − low_freq — brushstroke detail residue
  canvas = low_freq + high_freq — exact reconstruction

Stage 2: Saturation boost applied to low_freq only (broad colour masses become purer). Stage 3: Contrast amplification applied to high_freq only (edge detail sharpens). Stage 4: Recombine at 70% weight.

Novel: first pass to decompose the entire canvas into low+high frequency components and apply different colour operations to each before recombining. Prior Gaussian uses in this engine (repin Stage 1, grosz Stage 2) apply Gaussian to the whole canvas, never decompose and recombine.

**Mood & Intent**

*Colour for colour's own sake.* The harbour is a pretext. The three boats are primary, secondary, tertiary — a colour exercise wearing the clothes of a scene. The intent is the specific Fauve quality Matisse described after seeing Derain's Collioure work: unironic, physical joy in pure pigment against ancient stone and bright water. Nothing in this image mourns, struggles, or doubts. The noon light is pitiless and generous at once.

**Full Pipeline:** `tone_ground` → `underpainting` → `block_in` (×2) → `build_form` (×2) → `place_lights` → `paint_frequency_separation_pass` → `derain_fauve_intensity_pass` → `paint_chromatic_shadow_shift_pass`

*New this session: André Derain (1880–1954, French Fauve) — derain_fauve_intensity_pass (196th distinct mode). Improvement: paint_frequency_separation_pass — Laplacian decomposition (low_freq/high_freq split; differential saturation/contrast treatment; first frequency-domain pass in engine).*""",
]


def post_text(text: str) -> str:
    assert len(text) <= 2000, f"Text block too long: {len(text)} chars"
    payload = json.dumps({"content": text})
    result = subprocess.run(
        [
            "curl", "-s", "-X", "POST",
            f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
            "-H", f"Authorization: Bot {TOKEN}",
            "-H", "Content-Type: application/json",
            "-d", payload,
        ],
        capture_output=True, text=True
    )
    resp = json.loads(result.stdout)
    msg_id = resp.get("id", f"ERROR: {resp}")
    print(f"Text message ID: {msg_id}")
    return msg_id


def post_image(image_path: str, filename: str) -> str:
    result = subprocess.run(
        [
            "curl", "-s", "-X", "POST",
            f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
            "-H", f"Authorization: Bot {TOKEN}",
            "-F", f"files[0]=@{image_path};filename={filename}",
            "-F", f'payload_json={{"attachments": [{{"id": 0, "filename": "{filename}"}}]}}',
        ],
        capture_output=True, text=True
    )
    resp = json.loads(result.stdout)
    msg_id = resp.get("id", f"ERROR: {resp}")
    print(f"Image message ID: {msg_id}")
    return msg_id


def main():
    # Validate block lengths
    for i, block in enumerate(TEXT_BLOCKS):
        if len(block) > 2000:
            print(f"ERROR: Block {i} is {len(block)} chars (limit 2000)")
            sys.exit(1)
        else:
            print(f"Block {i}: {len(block)} chars -- OK")

    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image not found at {IMAGE_PATH}")
        sys.exit(1)

    print(f"Posting s285 to channel {CHANNEL_ID}...")
    ids = []
    for i, block in enumerate(TEXT_BLOCKS):
        print(f"Posting text block {i + 1}/{len(TEXT_BLOCKS)} ({len(block)} chars)...")
        mid = post_text(block)
        ids.append(mid)
        time.sleep(0.8)

    print("Posting image...")
    img_id = post_image(IMAGE_PATH, FILENAME)
    ids.append(img_id)
    print(f"Done. Message IDs: {ids}")
    return ids


if __name__ == "__main__":
    main()
