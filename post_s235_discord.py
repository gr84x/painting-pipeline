"""Post session 235 painting to Discord #gustave channel."""
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
                          "s235_nolde_fox_dark_pines.png")

IMAGE_DESCRIPTION = """**Fox at the Edge of the Dark Pines** — Session 235

*Oil on raw umber imprimatura, Nolde Incandescent Surge*

**Image Description**

Late October, dusk, on the North Sea coast of Schleswig-Holstein. The wind is from the north. A solitary red fox sits motionless on a lichen-crusted granite boulder at the edge of the last coastal meadow before the dark pine forest begins. He occupies the centre of the world.

The fox is seen from a low three-quarter angle, slightly below and to the left, so that his figure rises against the broken sky. His thick winter coat burns orange-crimson — not the fox-fur of a fairytale but the violent, primordial orange of Nolde's chromatic imagination, the colour of burning heather and iron-ore. The white patch of his chest glows warmly at the lower body. His tail is curled around his feet, a ring of slightly paler amber at the tip. His ears are pricked straight upward, black-tipped, alert to something the viewer cannot hear. His amber-gold eyes look directly out — patient, still, neither afraid nor hostile. They carry the calm authority of an animal that belongs here.

The granite boulder is dark with age and wet with coastal air: grey-brown with patches of pale ochre lichen, mossy at its base where the meadow grass presses in. Dry yellow-ochre meadow grass bends in low wind around the boulder's base, tufts of it in the near-black foreground, the whole ground zone a saturated dark umber-earth.

Behind the fox: the pine forest. Jagged black silhouettes of wind-bent coastal pines rise against the sky in an irregular line — some tall and narrow, some wide-branching, all collapsed into near-black shapes. They press in from both edges, narrowing the visible sky to a band above the fox's head.

And the sky. At the top: near-black storm-purple, the colour of a bruise. Below it, the purple lightens to deep violet-grey, then the sky tears open at the horizon in a band of smoldering incandescent amber-orange — the sun has already set but left this blazing farewell behind the cloud layer. The amber band is vivid, almost violent, a slash of warm fire at the base of the storm. In the Nolde surge, the amber radiates a warm bloom into the surrounding air.

In the shadows — under the boulder, in the pine zone, in the foreground grass — the darkness glows warm. Nolde's shadows are not cool blue-grey (as academic painting demands) but warm: red-earth, ochre-umber, fire-dark. The shadow inversion gives the whole image an inner light, as if the ground itself retains warmth from a distant geological fire.

The painting means: the wild endures. The fox was here before the pines, before the dunes, before the names of things. He will be here when the amber horizon closes. He watches, and the painting watches with him.

**Technique:** Nolde Incandescent Surge (146th distinct mode)
**Palette:** Raw umber dark ground · savage crimson-red · incandescent orange · chrome yellow · deep cobalt sea-night · dark pine-green · deep violet-plum · warm bone-ash
**Mood:** Primordial solitude — the wild creature in its wild element, time suspended at the edge of darkness
**Passes:** tone_ground (raw umber imprimatura) → underpainting → block_in × 2 → build_form × 2 → nolde_incandescent_surge_pass → paint_pigment_granulation_pass → warm_cool_zone_pass → chromatic_vignette_pass → glaze (raw umber) → vignette

*New this session: Emil Nolde (1867–1956, German Expressionism / Die Brücke) — nolde_incandescent_surge_pass (146th distinct mode). THREE-STAGE CHROMATIC SURGE: (1) Shadow warmth inversion — dark zones pushed warm (R+, B-), the OPPOSITE of academic warm-light/cool-shadow; no prior pass inverts the conventional warm/cool temperature relationship; (2) Mid-tone chromatic surge — bell-curve at lum=0.50 drives mid-tones to full spectral intensity, distinct from Chagall's chroma-gate approach (s234) and Moreau's penumbra bell at lum=0.28 (s232); (3) Vivid bloom halation — dual chroma+lum gate radiates warm halo from intense colour zones, first bloom pass requiring BOTH high chroma AND luminance (prior blooms gate on lum alone). Improvement: paint_pigment_granulation_pass — mineral pigment granulation simulation using dual-frequency coherent noise (coarse_sigma=5.5px clusters + fine_sigma=1.1px granules), chroma-gated texture, valley warm tint for earth pigment quality.*"""

FILENAME = "s235_nolde_fox_dark_pines.png"


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

    print("Posting session 235 to Discord #gustave...")
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
