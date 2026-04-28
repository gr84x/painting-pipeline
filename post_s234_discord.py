"""Post session 234 painting to Discord #gustave channel."""
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
                          "s234_ryder_fishermans_vigil.png")

IMAGE_DESCRIPTION = """**The Fisherman's Vigil** — Session 234

*Oil on warm umber imprimatura, Ryder Moonlit Sea*

**Image Description**

A lone wooden fishing vessel sits heavy and still on a dark, open sea at night. The world has been reduced to its essentials: near-black water below, an indigo sky above, a pale quarter-moon suspended in amber haze, and between them — barely discernible, absorbed into the surrounding dark — a solitary old fisherman standing at the bow.

The boat occupies the right half of the canvas, its hull a dense silhouette of absolute dark, low in the water as if weighted by years and salt. A bare mast rises from the hull toward the upper sky; a single horizontal boom crosses it midway; a furled sail bunched against the yard is the only mass above the deck. Nothing moves. The rigging is too dark to trace. The fisherman stands at the bow, facing away from the viewer — hunched slightly against a cold that exists in the stillness itself. His coat, his hat, his posture: a single dark shape that reads as a man through its attitude alone, not its detail.

The environment is one of Ryder's elemental compositions. The sea occupies the lower half — near-black, flat, with a dozen barely-visible rolling swells rendered as the faintest tonal difference from the void below them. Across the centre, a soft vertical column of amber-gold light runs from the moon down through the water: the reflection, rippling very slightly, dissolving into nothing before it reaches the near shore. The horizon is a thin, imprecise line where dark sea meets dark sky — in Ryder's manner, the edge dissolves more than it divides. Above it, the sky deepens through deep indigo at the lower register to near-black at the top, with three or four torn cloud fragments low in the sky, rendered as wisps of amber-ochre, warm and faint as tarnished gold.

The moon is small and high — a cream-amber disc no larger than a ship's lantern, surrounded by a diffuse warm glow that fades into the indigo sky. Unlike Kuindzhi's theatrical cold-white moon, this one glows like a lamp burning low, its light the colour of aged varnish. It illuminates nothing precisely; it simply fills the middle distance with its warmth.

The emotional state of the scene: solitary endurance. The fisherman is not noble in a heroic sense — he is simply there, as he has always been there, as the sea has always been there. The painting asks nothing from the viewer except to be still, and to notice the warmth of a small moon above a dark sea.

**Technique:** Ryder Moonlit Sea (145th distinct mode)
**Palette:** Near-black deep water · warm dark umber shadow · amber-ochre mid-tone · pale cream moon glow · tarnished gold cloud edge · indigo night sky
**Mood:** Solitary endurance — the fisherman's vigil, the patient dark, one small warm light above an indifferent sea
**Passes:** tone_ground (warm umber imprimatura) → underpainting → block_in × 2 → build_form × 2 → place_lights → ryder_moonlit_sea_pass → paint_varnish_depth_pass → diffuse_boundary_pass → glaze (amber-umber) → vignette

*New this session: Albert Pinkham Ryder (1847–1917, American Tonalism / Romantic Symbolism) — ryder_moonlit_sea_pass (145th distinct mode). THREE-STAGE VISIONARY TONALISM: (1) Tonal massing — zone-selective dual luminance pull: dark zones crushed toward near-black (dark_gate^dark_power * dark_crush multiplier), light zones lifted toward white (light_gate^light_power * light_lift), creates Ryder's 2-3 stark tonal masses; (2) Amber ochre glaze — bell-curve gate at lum=0.40 (shadow-mid boundary), R+, G+, B- shift — models aged bituminous medium tint; (3) Visionary dissolution — global isotropic Gaussian blur at dissolution_blend ratio, universal form softening. Improvement: paint_varnish_depth_pass (bell-curve sat boost peaked at lum=0.45 modeling varnish wetting dry pigment + coherent Gaussian noise micro-sheen in near-white zones only, first pass simulating physical optical depth of picture varnish).*"""

FILENAME = "s234_ryder_fishermans_vigil.png"


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

    print("Posting session 234 to Discord #gustave...")
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

# Discord message IDs posted 2026-04-28:
# 1498820928262508555 / 1498820932171726919 / 1498820937489842386 / 1498820943244427334
