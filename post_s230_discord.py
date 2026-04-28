"""Post session 230 painting to Discord #gustave channel."""
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
                          "s230_hammershoi_empty_chair.png")

IMAGE_DESCRIPTION = """**The Empty Chair** — Session 230

*Oil on linen, silvery grey imprimatura, Hammershøi Intimist interior*

**Image Description**

An empty rocking chair sits alone in the corner of a bare interior room, lit by a single tall north-facing window at upper-left. The chair faces slightly away from the viewer, three-quarter angle, its seat vacant. No figure occupies it — the absence is the subject.

The chair is dark oak, old and worn, its curved rockers resting on wide pine floorboards whose grain runs horizontally toward the light. The caning on the seat is faded, worn thin at the centre from years of use. The chair back rises in a gentle arch above five slender spindles, the outer uprights catching the soft window light on their left edges — a thin warm gleam against the grey. The curved rockers leave long, barely-visible shadows on the floor angled toward the lower right.

The room is almost empty. The left wall holds the window: tall, divided by a dark oak frame and single crossbar, its glass panes pouring diffused silver light in a column across the floor. That column of light — ivory-warm near its source, cooling to silver across the middle of the floor, fading before it reaches the far-right corner — is the painting's true subject. The back wall is bare plaster, a muted grey-ivory that holds the light with slight warmth near the window and retreats into cool shadow at right. High on the far wall, barely distinguishable from the plaster, hangs a small framed picture, its content entirely indistinct. A low skirting board runs along the floor junction. There is no other furniture, no decoration, no object. The ceiling corners are deep charcoal. The right-side wall is swallowed in shadow.

The floor: pale pine boards, wide-planked, the grain catching the window light. Near the window the boards are warm silver-cream; at mid-room they hold a cool silver-grey; in the right foreground they are almost dark.

Floating in the column of window light: eighteen barely-visible dust motes drift in slow suspension — tiny points of ivory light, the only motion in the room.

**Technique:** Vilhelm Hammershøi Grey Interior (141st distinct mode)
**Palette:** Silver-ivory window light · warm grey plaster · cool blue-grey shadow · dark oak chair · pale pine floor · near-charcoal corner
**Mood:** The weight of a recently vacated room — profound, poignant absence. Someone sat in that chair. Where are they now? The viewer should feel the heavy stillness of a house from which someone has gently departed.
**Passes:** tone_ground (grey imprimatura) → underpainting → block_in × 2 → build_form × 2 → place_lights → hammershoi_grey_interior_pass → chromatic_memory_pass → impasto_relief_pass → diffuse_boundary_pass → glaze (silver-grey) → vignette

*New this session: Vilhelm Hammershøi (1864-1916, Danish Intimism) — hammershoi_grey_interior_pass (141st distinct mode). THREE-STAGE SILVERY INTERIOR MODEL: (1) Midtone grey veil — bell-curve desaturation strongest at lum=0.55, with warm-highlight and cool-shadow preservation; (2) Unidirectional left-window gradient — horizontal brightening at left with warm lift + complementary cool-blue cast at right; (3) Stillness haze — midtone-gated Gaussian softening blurring interior contours while leaving lit and shadow extremes crisp. Improvement: chromatic_memory_pass — spatial colour memory via local-average pull gated by saturation threshold, harmonising low-saturation greys without touching saturated focal areas.*"""

FILENAME = "s230_hammershoi_empty_chair.png"


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

    print("Posting session 230 to Discord #gustave...")
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
