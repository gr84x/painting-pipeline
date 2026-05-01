"""Post session 281 Discord painting to #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s281_pine_forest.png")
FILENAME   = "s281_pine_forest.png"

TEXT_BLOCKS = [
    """\
**Cathedral Pines — A Russian Forest Interior at Golden Hour** — Session 281

*Oil on linen · Ivan Shishkin mode — 192nd distinct mode · Forest Density + Shadow Temperature*

**Subject & Composition**

A dense Russian pine forest interior in Vyatka Province, late September, 4 PM. The viewer stands inside a cathedral of towering Scots pines — massive trunks, perhaps 30-40 meters tall, their plated amber-brown bark lit from the upper right by a shaft of low golden afternoon light that descends in a diagonal beam between two massive foreground trees. The composition is organized around this central light column: two dominant trunks frame it on either side, a receding colonnade of smaller trunks dissolves behind them into cool blue-green atmospheric haze. The eye travels from the warm-lit ochre forest floor through the dark mid-zone of bark-shadow to the glowing canopy beyond.""",

    """\
**The Forest**

Mature Scots pines (*Pinus sylvestris*), each a column of geological mass. The two foreground trunks are nearly a meter in diameter: their bark rendered in vertical ridges and horizontal shadow bands, warm amber on the sun-facing right side, cool gray-green lichen on the shadow left. Behind them, five or six trunks recede into the distance — each one grayer, cooler, less distinct, until the farthest are indistinguishable from the atmospheric haze itself. The canopy above is dense and shadowed, with a bright warm opening at the upper center where the light shaft originates. The forest floor is dry pine-needle sand: warm raw umber with scattered dapples of sunlight in irregular patches. A low undergrowth of scrubby bracken fills the lower corners. No human presence. The scale makes the space ancient, vast, and indifferent to the viewer's presence.""",

    """\
**The Environment**

Deep provincial Russian forest, far from any city or road. The air carries cool resinous moisture — the specific scent of a pine forest after a warm autumn afternoon, before the evening chill arrives. Light enters only through the canopy gaps; the primary shaft is warm and golden, throwing sharp-edged shadows of the foreground trunks across the needle-covered floor. The middle distance is in deep green shadow. The far background dissolves into a blue-gray atmospheric veil where the trunk colors have lost their specificity. The mood: majestic solitude. The silence of the deep forest — broken only by the distant percussion of a woodpecker. Shishkin painted this forest because it was *there*, specific and material, and because he wanted it to be known.""",

    """\
**Technique & Palette — Ivan Shishkin (1832–1898)**

Shishkin's method distilled: meticulous bark texture on the foreground trunks (vertical grain, horizontal bands, specific material weight), dappled canopy light as a mosaic of carefully differentiated values, warm raw umber and ochre on the forest floor, cool blue-green atmospheric recession in the background distance.

The new *shishkin_forest_density_pass* (192nd distinct mode) applies four stages: (1) **Vertical bark anisotropy** — a purely vertical uniform filter (22:2 height:width kernel) imparts vertical grain texture to all tree surfaces, the first pass to use a single extreme-aspect-ratio vertical kernel for directional material simulation; (2) **Canopy dappling** — local luminance variance (*E*[*L*²] − *E*[*L*]²) identifies light/shadow transition zones in the canopy, pushing high-variance pixels toward sunlit yellow-green, the first pass to use local variance as a dappled-light proxy rather than absolute luminance; (3) **Shadow floor warmth** — shadow zones pushed toward warm forest-earth ochre, encoding the specific reflection of sandy soil into base-of-shadow areas; (4) **Desaturation haze** — per-pixel chroma gates a cool blue-green distance push, identifying naturally desaturated distant trunks regardless of vertical position.

The new *paint_shadow_temperature_pass* (s281 improvement) measures the dominant light temperature from the highlight pixels (warm_bias = R̄ − B̄ in the top 15%) and applies the *opposing* temperature to shadow zones — warm golden-hour light yields cool violet shadows; cool northern light yields warm amber shadows. The first improvement pass where push direction is computed from image data, not hardcoded.

Palette: deep forest shadow green · sunlit canopy yellow-green · warm amber bark · dark umber bark shadow · golden afternoon column · raw umber forest floor · cool haze blue-gray · sandy warm path""",

    """\
**Mood & Intent**

The grandeur and solitude of the Russian forest. Shishkin wanted viewers to *know* the forest as he knew it — not as romantic backdrop or decorative motif, but as a specific, material, living reality with its own weight, its own light, its own claim on attention. He was the first Russian painter to treat the landscape as worthy of the same sustained, patient, respectful observation that the Old Masters brought to the human face. The painting should convey the physical sensation of standing inside a mature pine forest: the scale, the filtered light, the specific temperature of the resin-cooled air. The viewer should feel the age of the trees and the smallness of themselves.

**Full Pipeline:** `tone_ground` (forest earth ochre) → `underpainting` (×2) → `block_in` (×2) → `build_form` (×2) → `place_lights` → `shishkin_forest_density_pass` → `paint_shadow_temperature_pass` → `paint_depth_atmosphere_pass` → `paint_lost_found_edges_pass`

*New this session: Ivan Shishkin (1832–1898, Russian Realist/Peredvizhniki) — shishkin_forest_density_pass (192nd distinct mode). FOUR-STAGE FOREST INTERIOR SYSTEM: (1) purely vertical anisotropic bark grain; (2) local luminance variance dappling — first use of E[L²]-E[L]² as zone gate; (3) shadow-zone warm earth push; (4) desaturation-gated cool haze recession — first pass gated on per-pixel chroma rather than vertical position or luminance. Improvement: paint_shadow_temperature_pass — data-adaptive warm/cool opposition: measures dominant light temperature from highlights, applies opposing temperature to shadows, first improvement pass with image-data-driven push direction.*""",
]


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
    print(f"Posting s281 Discord painting to channel {CHANNEL_ID}...")
    ids = []
    for block in TEXT_BLOCKS:
        mid = post_text(block)
        ids.append(mid)
        time.sleep(0.8)
    img_id = post_image(IMAGE_PATH, FILENAME)
    ids.append(img_id)
    print(f"Done. Message IDs: {ids}")
    return ids


if __name__ == "__main__":
    main()
