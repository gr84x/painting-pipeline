"""Post session 237 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s237_rouault_raven.png")

IMAGE_DESCRIPTION = """**The Raven's Vigil** — Session 237

*Oil on near-black imprimatura, Rouault Stained Glass mode*

**Image Description**

A single raven perches on the crumbling top edge of a medieval stone wall, caught in the act of turning its head back toward the viewer. The low camera angle looks slightly upward at the bird, which occupies the upper-centre of the composition with sovereign authority.

The raven is large, its feathers painted in deep near-black with veins of cobalt-blue and blue-green iridescence where the cold winter sky light catches the quills — the right wing raised slightly, its primary feathers fanning apart to reveal their individual sheening darkness. The amber-gold eye is startling and wide, the iris a jewel-like burnt orange with a round near-black pupil and a cold specular highlight reflecting the pale sky. The beak is powerful and curved, dark grey with an ivory cutting edge, slightly parted as if the bird has just stopped calling. The talons grip the stone with practiced authority.

The environment: a crumbling stone wall built of rough ashlar courses stretches horizontally across the lower-centre of the canvas, its surface mottled with emerald lichen patches and pale golden-ochre moss, the mortar joints dark grey lines dividing the wall into weighty blocks. The wall top edge is dusted with dry snow in scattered patches, cold ivory-white against the raw umber stone. Behind and above: a turbulent prussian blue-grey winter sky, torn cloud masses pressing low and heavy, with a band of cold crimson-amber light breaking at the horizon to the left — the only warmth in an otherwise arctic scene. At the far horizon, bare tree silhouettes stand against this cold glow, black verticals with thin branching arms. The foreground below the wall is dark, cold ground with scattered snow patches and dead winter grasses — ochre stems bent and broken, their tips catching the pale sky light.

The Rouault Stained Glass pass (148th mode) does its defining work: thick near-black Sobel-detected contour lines encircle the raven's body, wing joints, beak, and eye — the heavy lead lines of medieval glass. Within these boundaries, the cobalt blue of the sky deepens to pure jewel intensity; the amber eye burns; the emerald lichen sings against the grey stone.

**Technique:** Georges Rouault Stained Glass (148th distinct mode)
**Palette:** Near-black contour · deep cobalt blue · cold crimson horizon · emerald lichen · raw umber stone · amber-gold eye · bone-white snow
**Mood:** Austere winter sovereignty — the viewer should feel the cold, the absolute stillness of a held breath, and the raven's complete indifference to human presence
**Passes:** tone_ground (near-black imprimatura) → underpainting → block_in × 2 → build_form × 2 → place_lights → rouault_stained_glass_pass → paint_scumble_pass → diffuse_boundary_pass → glaze (prussian blue-grey) → vignette

*New this session: Georges Rouault (1871-1958, Expressionism/Fauvism) — rouault_stained_glass_pass (148th distinct mode). THREE-STAGE STAINED GLASS SIMULATION: (1) Sobel gradient magnitude detects colour-zone boundaries — FIRST pass in project to use a spatial derivative operator as primary tool; (2) Contour darkening + lead-line cool tint drives high-gradient pixels toward near-black with blue-grey shift; (3) Inverse gradient gate pumps jewel saturation in enclosed interior zones. Improvement: paint_scumble_pass — sparse thresholded binary noise mask simulates dry-brush bristle contact zones, with luminance-gated cool asymmetric channel lift (first binary/near-binary noise mask in project).*"""

FILENAME = "s237_rouault_raven.png"


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

    print("Posting session 237 to Discord #gustave...")
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
