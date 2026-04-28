"""Post session 232 painting to Discord #gustave channel."""
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
                          "s232_khnopff_canal_reverie.png")

IMAGE_DESCRIPTION = """**The Canal Reverie** — Session 232

*Oil on linen, cool blue-grey imprimatura, Khnopff Frozen Reverie mode (143rd distinct mode)*

**Image Description**

A solitary young woman sits at the far end of a fog-shrouded canal jetty at the last hour before Belgian dawn. The viewer is positioned slightly above and to her right, looking down along the grey weathered planks toward her hunched, still form. She does not know she is observed. She is not waiting. She has simply stopped.

**The Figure**
The woman occupies the center and left of the composition, filling roughly the upper two-thirds. She is wrapped entirely in a heavy grey-blue wool shawl — the fabric drawn over her head and shoulders like a soft monastic hood, obscuring everything except a partial profile of her right cheek and jaw. Only the right side of her face is visible, pale as old porcelain: a high cheekbone, a closed or cast-down eye whose lashes barely register, parted lips that do not speak. Her pale hands rest loosely together in her lap, just visible below the shawl's hem — the only note of warmth in an otherwise cool composition.

Her emotional state: she is not sad. She has gone somewhere deep inside herself that ordinary emotion does not reach. She is suspended. The fog has entered her.

**The Environment**
The Belgian canal at pre-dawn. Fog of such density that the far bank — fifty meters distant — has dissolved into a flat smear of grey-green willow shadow, barely distinguishable from sky. The water surface is an absolute mirror of grey steel, perfectly still, reflecting the fog and the underside of the jetty planks in a long faint echo. The jetty itself runs horizontally through the lower third of the canvas: old weathered boards the color of old bone, darkened at their joints by moss and lichen, their edges blurred by damp. A thin darker line marks where water meets wood. The horizon glow — no sun, just a pale lightening of grey at fog-level — forms a soft luminous band across the middle distance, too vague to cast shadows.

Everything in the environment is multiple shades of grey. This is intentional.

**Technique & Palette**
Fernand Khnopff's frozen reverie atmosphere — cool silver desaturation pulling the entire image toward blue-grey, atmospheric mist blurring all but the pale face and hands, cool pearl tint in the brightest highlights to preserve the north-European grey-light quality rather than warm gold. Palette: cool silver-grey dominant · blue-grey shadow · warm ivory-pearl (face and hands, only) · slate blue (deep mid-shadow) · near-black blue-charcoal (deepest jetty shadows) · fog-white (horizon glow)

**Mood & Intent**
Absolute stillness. The image should make the viewer involuntarily slow their breathing. It conveys the quality of a moment so complete in its quietness that it has ceased to be a moment — it has become a condition. The woman is not waiting for anything. The fog is not clearing. The day may never come. And this is enough.

Viewers should carry away a strange, aching longing for this kind of silence — not melancholy, but the particular peace of having chosen solitude completely.

**Passes:** tone_ground (cool blue-grey) → block_in × 3 → midtone_clarity_pass → warm_cool_zone_pass → khnopff_frozen_reverie_pass → glaze (cool grey) → vignette

*New this session: Fernand Khnopff (1858-1921, Belgian Symbolism) — khnopff_frozen_reverie_pass (143rd distinct mode). THREE-STAGE REVERIE MODEL: (1) Cool silver veil — global desaturation toward blue-grey, strongest in shadows (cool_gate gated by 1-lum/0.65) with blue channel boost and red reduction; (2) Reverie mist blur — Gaussian atmospheric blur blended inversely to luminance so highlights stay crisp while shadows dissolve into fog; (3) Pearl highlight tint — B+ in lum>0.70 for characteristic cold-white north-European highlight quality (opposite of Moreau's warm gold). Improvement: warm_cool_zone_pass — standalone academic light-temperature separation: warm ramp in highlights (R+, B-) and cool ramp in shadows (B+, R-), mid-tones intentionally untouched.*"""

FILENAME = "s232_khnopff_canal_reverie.png"


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

    print("Posting session 232 to Discord #gustave...")
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
