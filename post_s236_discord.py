"""Post session 236 painting to Discord #gustave channel."""
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
                          "s236_kupka_lighthouse.png")

IMAGE_DESCRIPTION = """**The Lighthouse at the Threshold** — Session 236

*Oil on near-black prussian imprimatura, Kupka Orphic Fugue*

**Image Description**

True dusk on a volcanic promontory somewhere on the North Atlantic — the moment between the last amber sliver of sunset and the full arrival of night. The lighthouse lamp has just been lit. It is the first and only warm light in an increasingly cold world.

The lighthouse stands right of centre, a tall white cylindrical tower rising from dark basalt rock. It is viewed from below and slightly to the left, so the tower rises against the full depth of the dusk sky. The light side of the tower catches the last warmth from the amber horizon — cream and ivory, gently golden where the lamp's own corona washes it. The shadow side falls into blue-violet: not dark as absence but dark as presence, the shadow side has its own colour, a cool cerulean-indigo that belongs to the sky behind it.

The lantern room glows. Warm gold-amber light burns within the dark metal housing of the lamp gallery. A corona — a warm halo — radiates outward from the lamp in rings, the innermost hot amber, cooling to pale golden cream at its edges. From the lamp, a diagonal beam cuts toward the upper left through the sky: pale amber-cream, narrow at the source, broadening as it sweeps into the dark cerulean above.

The sky is Kupka's domain. Five pure colour planes stack vertically above the sea in the manner of his *Vertical Planes in Blue and Red* (1913): near-black midnight at the top, prussian blue, cerulean, cadmium red at the horizon, chrome amber glow just above the waterline. But the Orphic Fugue has been applied: sinusoidal hue waves radiate concentrically from the lamp as their focal point, cycling warm → cool → warm in repeating rings outward across all five planes. The sky does not merely contain colour — it oscillates, breathes, rotates in a slow chromatic fugue around the lighthouse as its fixed axis. Warm hues cycle through cool and back again at a spatial period of roughly a quarter of the image width, so the sky shows approximately two full hue oscillation cycles between lamp and canvas edge.

The sea below the horizon is dark prussian blue — calmer than the sky, a mirror that refuses to fully reflect. A vertical reflection streak from the lamp descends straight down into the water: amber at its origin, widening and dimming as it reaches the foreground, until it merges with the near-black wetness of the volcanic foreground rocks. The orphic colour rings are faintly visible in the sea too — the hue waves do not stop at the waterline.

The foreground is dark volcanic basalt, wet with tidal spray: near-black boulders of various sizes, rounded and smoothed by centuries of wave action. Scattered across their wet surfaces are small bright glints — amber and gold where the sky's reflection strikes a tilted face of rock, blue-grey where the shadow side of sky meets a north-facing surface. Distant sea-rocks silhouette the horizon just above the water line.

Stars are just becoming visible in the upper third of the sky: small, cool-white, appearing through gaps in the near-black midnight band at the top.

Painted with patience and practice, like a true artist. The medium pooling pass has deepened the valleys between brush strokes — the shadows between rock faces and the recesses of the masonry are slightly darker and richer than the surrounding surfaces, as oil medium pools in the lows of the textured paint surface during drying.

**Technique:** Kupka Orphic Fugue (147th distinct mode)
**Palette:** Prussian blue · cadmium red · chrome yellow · emerald · cerulean · magenta-violet · ivory white · near-black
**Mood:** Transcendent solitude — the lighthouse as fixed axis of a rotating chromatic universe; the ancient human impulse to make light in darkness; colour freed from representation, freed even from sky and sea, orbiting a single warm point
**Passes:** tone_ground (prussian black) → underpainting → block_in × 2 → build_form × 2 → place_lights → kupka_orphic_fugue_pass → paint_medium_pooling_pass → diffuse_boundary_pass → glaze (prussian blue) → vignette

*New this session: Frantisek Kupka (1871–1957, Czech-French, Orphism) — kupka_orphic_fugue_pass (147th distinct mode). TWO-STAGE ORPHIC TRANSFORMATION: (1) Radial hue fugue — luminance-weighted centroid anchors a sinusoidal hue rotation field; Δhue = amplitude × sin(2π × r/period + phase) applied in HSV space; FIRST pass to rotate HSV hue as primary operation — prior passes add/subtract RGB offsets, this rotates the colour wheel; (2) Bell-curve chromatic surge at V=0.52 drives mid-tones to full spectral intensity. Improvement: paint_medium_pooling_pass — morphological erosion valley detection (grey_erosion, FIRST pass to use morphological operators); valley_gate = 1 − valley_depth/threshold; simultaneous darkening + saturation boost in valley zones models pooled oil medium.*"""

FILENAME = "s236_kupka_lighthouse.png"


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


if __name__ == "__main__":
    assert os.path.exists(IMAGE_PATH), f"Image not found: {IMAGE_PATH}"

    print("Splitting description into Discord-safe chunks...")
    MAX_LEN = 1900
    desc = IMAGE_DESCRIPTION
    chunks = []
    while len(desc) > MAX_LEN:
        split_at = desc.rfind("\n\n", 0, MAX_LEN)
        if split_at == -1:
            split_at = desc.rfind("\n", 0, MAX_LEN)
        if split_at == -1:
            split_at = MAX_LEN
        chunks.append(desc[:split_at])
        desc = desc[split_at:].lstrip()
    if desc:
        chunks.append(desc)
    print(f"  {len(chunks)} text chunk(s)")

    ids = []
    for i, chunk in enumerate(chunks):
        print(f"  Posting text chunk {i+1}/{len(chunks)}...")
        ids.append(post_text(chunk))
        if i < len(chunks) - 1:
            time.sleep(1)

    time.sleep(1)
    print("  Posting image...")
    ids.append(post_image(IMAGE_PATH, FILENAME))

    print("Done. Message IDs:", ids)
