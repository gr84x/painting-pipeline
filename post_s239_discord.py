"""Post session 239 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s239_dix_foundry_night.png")

IMAGE_DESCRIPTION = """**The Foundry Night** — Session 239

*Warm plaster imprimatura, Dix Neue Sachlichkeit mode*

**Image Description**

A lone foundry worker stands in the cavernous darkness of an industrial forge, seen in three-quarter front-left view from slightly above. He occupies the center of the composition — a compact, solidly built man in a rough canvas jacket and heavy work trousers, a flat cloth cap pulled low over his brow, his right arm extended toward the furnace as if feeling the heat. The light source is the furnace itself: a roaring amber-orange opening in the lower-right of the canvas, its core blazing white-yellow where the fire peaks and bleeding outward into warm cadmium tones across the foundry floor.

The figure is described with the surgical directness of Dix's portrait practice. The furnace light falls from below and to the right, carving the left side of his face into harsh shadow while the right cheekbone, jaw, and extended hand catch the full amber blaze. His face is weathered and specific — deep-set eyes under the brow shadow, a prominent nose with a sharp highlight on its tip, a tight-set jaw that registers neither complaint nor sentiment, only the focused attention of a man who has done this work for twenty years. The skin is raw sienna and ochre in the light, dark umber and near-black in shadow. No softness, no flattery.

The background is foundry dark: near-black industrial space traversed by diagonal steel beams receding toward an upper-left vanishing point, a horizontal cross-beam at one-third height, and a single massive pillar left of frame. Smoke and heat haze build in the upper third — dark grey particulate matter drifting in loose irregular masses, each one rendered with a brief smear of tone rather than a sharp edge. A scatter of embers drifts visible against the dark air to the right of the figure, their paths caught mid-drift.

The ground level is concrete, its surface carrying the faint amber reflection of the furnace glow that reaches even here, across the foundry floor, and the dark scrawl of cracks and grime marks that document years of heavy work. The composition is stark and frontal, without atmospheric softening or tonal ambiguity: light zones are defined with finality, shadow zones with equal conviction.

The Dix Neue Sachlichkeit pass (150th mode) structures the tonal language throughout: midtone compression pushes ambiguous grey values decisively toward their nearest extreme — the mid-lit regions of the face flatten into specific zones of light and shadow; the boundary saturation surge brings out the reddish warmth at the precise edge between the jacket's shadow and the furnace-lit torso, the zone Dix consistently used to define his figures' contour with colour as well as value. The forensic highlight crisping drives the furnace core and the brightest skin surfaces to near-white, giving the image the hard enamel surface quality of Dix's oil-over-tempera technique. The glaze gradient improvement layers a descending warm ochre wash that builds from translucency at the top to a gentle amber tint at the bottom, reinforcing the foundry's heat-stained air.

**Technique:** Otto Dix Neue Sachlichkeit (150th distinct mode)
**Palette:** Near-black coal shadow · raw sienna and ochre skin · amber-orange furnace glow · yellow-grey highlight · dark umber jacket · warm plaster ground
**Mood:** The dignity of industrial labor without sentimentality — the viewer should feel the weight of the work, the heat of the furnace, and the unsentimental directness of a man examined honestly under raking light.
**Passes:** tone_ground (warm plaster) → underpainting → block_in × 2 → build_form × 2 → place_lights → dix_neue_sachlichkeit_pass → paint_glaze_gradient_pass → diffuse_boundary_pass → glaze (warm umber) → vignette

*New this session: Otto Dix (1891-1969, Expressionism / Neue Sachlichkeit) — dix_neue_sachlichkeit_pass (150th distinct mode). THREE-STAGE NEW OBJECTIVITY SIMULATION: (1) Midtone tonal compression via luminance-distance-from-neutral gate t=|lum-0.5|/0.5 — FIRST pass where tonal shift inverts sign at lum=0.5, pushing light midtones up and dark midtones down; (2) Boundary saturation surge via joint edge-and-zone gate (sobel_mag × zone_bell) — FIRST pass to boost saturation only where high gradient AND mid-tone luminance coincide; (3) Forensic highlight crisping. Improvement: paint_glaze_gradient_pass — spatially varying axial gradient glaze with gamma-curved ramp and dual blend modes — FIRST pass to apply a directionally building transparent color wash.*"""

FILENAME = "s239_dix_foundry_night.png"


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

    print("Posting session 239 to Discord #gustave...")
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
