"""Post session 233 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"
HEADERS    = {
    "Authorization": f"Bot {TOKEN}",
    "User-Agent": "DiscordBot (https://github.com/gr84x/painting-pipeline, 1.0)",
}

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s233_kuindzhi_moonlit_steppe.png")

IMAGE_DESCRIPTION = """**Moonlit Night on the Steppe** — Session 233

*Oil on near-black imprimatura, Kuindzhi Moonlit Radiance*

**Image Description**

A solitary ancient birch tree stands sentinel at the edge of a perfectly still Ukrainian river on a windless autumn night, seen from low ground looking across the water toward the open steppe. The composition is architecturally simple — the vast horizontal silence of sky, river, and earth — held together by the vertical axis of the birch and the moon's reflection burning in the water below.

The birch occupies the right-centre of the canvas, its white bark split between incandescence and absolute dark: the moonlit right side glows cream-ivory with cold blue overtones; the shadow side is near-charcoal, swallowed into the surrounding darkness. Three bare branches curve upward and left in silhouette — leafless, late autumn — each branch as black as the sky it interrupts. The crown dissolves into indigo. The root base merges with the obsidian earth of the far bank.

The environment: above the far-bank horizon, the night sky is tiered in Kuindzhi's severe palette — near-black at the crown of the canvas, deep indigo at mid-sky, then a cool silver-grey corona around the full moon, grading to pale amber at the horizon's edge. The moon itself is a small, incandescent, cold-white disc with a luminous halo that radiates pale light into the surrounding atmosphere — cold-white at the source, silver-grey at the ring, indigo-dark beyond. A scatter of faint stars occupies the upper corners. The far bank is a flat dark ribbon of earth: absolute, featureless, three brushstrokes wide.

The river is obsidian black at its edges — and then, running vertically through the centre of the canvas from the far bank to the near foreground, a single streak of cold silver-lunar light: the moon's reflection, oscillating with the faintest water ripple, its brightness fading by half as it reaches the near shore. This vertical column of reflected light is the painting's spine. The foreground bank: dark earth, dried autumn grass in near-silhouette, a cluster of reeds at the waterline, their heads small oval shapes barely distinguishable from darkness.

The emotional state of the scene: absolute stillness. No wind, no sound, no human presence — only the moon, the water, and the one pale tree standing in its light.

**Technique:** Kuindzhi Moonlit Radiance (144th distinct mode)
**Palette:** Near-black velvet · deep indigo · cold silver-white lunar · pale amber horizon · cream birch bark · obsidian water
**Mood:** Transcendent Ukrainian solitude — the vast emptiness of the steppe at night, the moon as the only voice, the birch as witness to an ancient silence
**Passes:** tone_ground (near-black nocturnal imprimatura) → underpainting → block_in × 2 → build_form × 2 → place_lights → kuindzhi_moonlit_radiance_pass → paint_gravity_drift_pass → diffuse_boundary_pass → glaze (cold indigo) → vignette

*New this session: Arkhip Kuindzhi (1842–1910, Ukrainian-Russian Tonalism) — kuindzhi_moonlit_radiance_pass (144th distinct mode). FOUR-STAGE THEATRICAL MOONLIGHT MODEL: (1) Luminous halo corona — Gaussian-expanded bright mask minus source creates cold light ring around the moon; (2) Shadow velveting — power-curve darkening of dark zones to near-black velvet; (3) Chromatic moonlight shift — cold blue-white in highlights (B+, R-), indigo push in deep shadows; (4) Lunar reflection streak — vertical luminance column from x-centre simulating moon-on-water. Improvement: paint_gravity_drift_pass (asymmetric causal 1D vertical kernel — downward > upward — gated by paint thickness proxy, first pass using gravity-direction asymmetric blur to simulate wet oil paint sag).*"""

FILENAME = "s233_kuindzhi_moonlit_steppe.png"


def post_text(text: str) -> str:
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
    print(f"  Text message ID: {msg_id}")
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
    print(f"  Image message ID: {msg_id}")
    return msg_id


def split_text(text: str, max_len: int = 1900) -> list:
    """Split text into Discord-friendly chunks."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        split_at = text.rfind("\n\n", 0, max_len)
        if split_at < 0:
            split_at = text.rfind("\n", 0, max_len)
        if split_at < 0:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image not found at {IMAGE_PATH}")
        sys.exit(1)

    print("Posting session 233 to Discord #gustave...")
    print(f"Channel: {CHANNEL_ID}")
    print(f"Image: {IMAGE_PATH}")

    chunks = split_text(IMAGE_DESCRIPTION)
    msg_ids = []
    for i, chunk in enumerate(chunks):
        print(f"Posting text chunk {i+1}/{len(chunks)}...")
        mid = post_text(chunk)
        msg_ids.append(mid)
        time.sleep(0.8)

    print("Posting image...")
    img_id = post_image(IMAGE_PATH, FILENAME)
    msg_ids.append(img_id)

    print(f"\nAll messages posted:")
    for mid in msg_ids:
        print(f"  {mid}")


if __name__ == "__main__":
    main()
