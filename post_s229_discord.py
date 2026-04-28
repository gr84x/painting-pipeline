"""Post session 229 painting to Discord #gustave channel."""
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
                          "s229_redon_fox_kit.png")

IMAGE_DESCRIPTION = """**The Fox Kit at the Forest Edge** — Session 229

*Pastel and oil on indigo-violet ground, Symbolist reverie*

**Image Description**

A young fox kit sits motionless at the boundary of a twilight forest, body turned three-quarters toward the viewer while its amber eyes gaze sideways toward a luminous clearing — a violet mist glowing between the dark trunks with an otherworldly, phosphorescent radiance.

The fox kit occupies the lower-centre of the composition, seated on damp moss with front paws tucked neatly beneath a compact body. The coat is a warm burnt-orange with ochre lit-side, the chest dissolving into a cream-ivory bib. The tail curls fully around the haunches, white-tipped, a loose brushstroke of amber-gold that anchors the figure. Alert, triangular ears frame a narrow face; the whiskers are silver threads caught in the clearing's glow. The eyes carry a deep amber iris with a round violet-black pupil — and in the centre of each, the faintest white spark reflects the mist beyond.

The environment: a dense twilight forest with deep indigo-black tree trunks rising vertically at left and right, their forms swallowed into the violet darkness above. Between them at mid-ground, a luminous violet clearing glows as if the air itself is phosphorescent. The forest floor is mossy dark green-grey, scattered with small leaves and grass stems that catch the clearing's radiance. Foreground wildflowers bloom in impossible Redon colours — magenta, deep violet, rose-pink, indigo-blue, amber-gold, sage-green — each petal seeming to emit light from within rather than reflect it.

Floating through the mid-air of the clearing: luminous spore-motes or dream-particles drift in slow suspension, tiny points of violet-white light hovering like a Redon dreamscape made visible.

**Technique:** Odilon Redon Luminous Reverie (140th distinct mode)
**Palette:** Deep indigo-violet · burnt-orange fox · phosphorescent magenta · cerulean blue · amber-gold · cream-ivory
**Mood:** Threshold of dream — the fox kit pauses at the edge of the rational world, drawn toward luminous mystery beyond the trees
**Passes:** tone_ground (violet imprimatura) → underpainting → block_in × 2 → build_form × 2 → place_lights → redon_luminous_reverie_pass → impasto_relief_pass → diffuse_boundary_pass → glaze (violet-rose) → vignette

*New this session: Odilon Redon (1840-1916, Symbolism) — redon_luminous_reverie_pass (140th distinct mode). FOUR-STAGE SYMBOLIST LUMINOSITY MODEL: (1) Violet shadow lift — spectral indigo hue shift in dark zones; (2) Phosphorescent midtone bloom — bell-curve saturation gate peaked at lum=0.50; (3) Dream-haze shadow softening — Gaussian blur in shadow zones only; (4) Highlight shimmer — near-white bloom additive. Improvement: impasto_relief_pass (3D paint surface topography under directional raking light).*"""

FILENAME = "s229_redon_fox_kit.png"


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

    print("Posting session 229 to Discord #gustave...")
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
