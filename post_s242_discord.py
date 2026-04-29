"""Post session 242 painting to Discord #gustave channel.

Discord message IDs (posted 2026-04-29):
  Text 1: 1498948658463244429
  Text 2: 1498948662812868658
  Text 3: 1498948667225411624
  Text 4: 1498948671792873522
  Text 5: 1498948676578578454
  Text 6: 1498948681024409711
  Text 7: 1498948685734613032
  Image:  1498948691158106145
"""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s242_signac_lighthouse_saint_tropez.png")

IMAGE_DESCRIPTION = """**The Lighthouse at Port de Saint-Tropez** — Session 242

*High-key white-primed ground, Signac Divisionist Mosaic mode*

**Image Description**

A Mediterranean harbour at the height of a late afternoon in August, viewed from a slightly elevated position on the stone quay — the vantage of someone who has climbed the quayside steps and turned to look back at the harbour basin before the light changes. The composition is portrait-format, moderately wide, and pivots on a single vertical axis: a stone lighthouse standing slightly right of centre, its white tower rising from the quay into a cerulean sky, claiming the full height of the canvas from the lantern housing above to its base on the warm honey-coloured stone below.

The lighthouse is the spine of the image. The tower is warm cream-white stone, slightly tapered — fractionally narrower at the lantern housing than at the base — with a single horizontal stripe of vermilion marking the lighthouse's identity, as required by maritime navigation law. The lantern housing itself is a compact, bright gold-ochre structure: a small square room with windows on four sides, surmounted by a low dome. At this hour it is not yet lit; it catches the afternoon sun as a vivid warm accent against the deep cerulean behind it. A stone balcony-railing encircles the lantern at platform level, casting a thin horizontal shadow on the tower below.

The stone quay runs as a warm horizontal band across the lower quarter of the canvas — honey-yellow limestone, the same stone as the lighthouse tower, pitted and salt-worn, its surface broken by the joints between blocks. The quay sits above the harbour water and below the sky like a firm punctuation: the grammar of human order in a world of light and motion. Below the quay edge, the stone meets the water.

Three fishing boats are moored at the quay wall, their hulls below the quay level, their masts rising into the sky zone. The leftmost hull is vivid vermilion-red, broad and low; the central hull is deep cobalt blue, the largest of the three, its mast reaching highest; the rightmost hull is warm orange, small and round-bottomed. Each boat has a thin boom and a simple mast of dark timber-brown. Their hulls are reflected in the harbour water below — distorted, shorter, darker, absorbed into the shifting sea-green and cerulean of the shallow basin — but recognisably themselves, a trio of complementary colour notes: red, blue, orange, each paired with their complementary shadows in the water (sea-green, violet, deep indigo).

The water is the largest surface area in the painting. It is not one colour but a field of complementary relationships: sea-green in the upper, shallower zone near the quay where the light reaches the sandy bottom; deep cerulean further out toward the harbour mouth; and deep violet-blue in the lower canvas where the basin deepens and the afternoon sky is reflected in shadow. Across the surface run thirty or more horizontal bands of shimmer — pale harbour-light glints, lemon-yellow reflections from the sun, HARBOUR_LIGHT catching the ripple-crest of each small wave. The orange and gold of the lighthouse lantern and the afternoon sun cast broken, warm streaks across the upper harbour water.

Above the harbour, the hillside town of Saint-Tropez runs along the skyline. The visible portion is a compressed band of terracotta rooflines — warm burnt-sienna tiles, each slightly different in tone and age — and white or cream house walls, the whole settlement compressed into the middle-distance by the height of the viewpoint and the low Mediterranean light. Behind and beyond the rooflines, a mass of olive-green vegetation — hills or garden trees — provides a dark horizontal foil against which the pale rooftops register. The sky is the painting's dominant coolness: deep cerulean at the upper canvas, warming toward the horizon with a narrow band of chrome yellow and orange glow where the sun, off-canvas to the right, catches the haze above the sea. White cloud wisps occupy the upper sky, each cloud rounded and soft, the kind that forms over warm coastal water in August and carries no rain.

The total palette is the Mediterranean as Signac understood it: vivid cerulean blue in complementary dialogue with vivid orange; sea-green with violet-magenta; chrome yellow with deep violet. Every chromatic pair across the canvas is chosen to maximise simultaneous contrast — the law that two complementary colours placed adjacent will each appear more vivid than either would in isolation, as Michel-Eugène Chevreul first formulated in 1839. The lighthouse's warm stone glows more warmly for standing against a cerulean sky. The red hull burns more intensely for floating on a sea-green harbour. The lemon-yellow water glints vibrate more luminously for being surrounded by deep violet water.

The Signac Divisionist Mosaic pass (153rd distinct mode) is the structural logic of the surface. Rather than continuous tonal modelling — rather than the sfumato of smooth gradations or the impasto of loaded brushwork — the paint surface is divided into rectangular mosaic patches: each patch_size × patch_size block is quantized to its local mean colour, creating the flat-colour tessellation of Signac's mature style. Within each patch, a tile-level checkerboard assigns even tiles to the primary colour and odd tiles to the complementary (hue rotated 180°), interleaving the two hue-opposites within each small rectangular unit — precisely implementing Chevreul's simultaneous contrast at the intra-patch level, with comp_mix controlling the blend ratio. At boundaries between adjacent patches with opposing hues (hue difference > hue_thresh), saturation is boosted proportionally to the hue distance, reinforcing Chevreul's simultaneous contrast effect at inter-patch edges. A light integration blur (blend_sigma=0.7) simulates the optical mixing that occurs at gallery viewing distance, where the mosaic resolves into luminous vibrating passages rather than discrete tiles.

The Color Bloom improvement (session 242) adds the irradiation of highly saturated colour zones. In the physical painting, vivid reds and blues and yellows appear to glow or spread slightly beyond their paint boundary — a perceptual and optical phenomenon painters call irradiation or colour bloom. The bloom mask is saturation-gated: only pixels with saturation above bloom_threshold contribute to the bloom source, and the mask is graduated by excess saturation so that the most intensely saturated zones create the strongest halo. The bloom spreads outward by Gaussian diffusion, carrying the source colour into adjacent, less-saturated areas at a strength governed by the spread mask. Blue light blooms fractionally further than red (shorter wavelength, higher refractive index), creating a faint chromatic fringe at the outer annular zone of each bloom halo — the blue of the fishing hull halos bleeds fractionally further into the water than the red, exactly as it would through a glass lens.

**Technique:** Paul Signac Divisionist Mosaic (153rd distinct mode)
**Palette:** Deep cerulean · vivid orange · sea-green · violet-magenta · chrome yellow · warm stone · lemon shimmer · deep violet · red/blue/orange hulls
**Mood:** Joyous, dazzling, celebratory. The painting does not contemplate the harbour — it vibrates with it. The simultaneous contrast of complementary pairs makes every surface appear more vivid than it could in isolation: the lighthouse more luminous, the water more alive, the boats more intensely themselves. The viewer is asked not to look at the harbour from outside it but to feel the particular quality of Mediterranean afternoon light that Signac spent forty years chasing: not the record of a scene but the sensation of colour relationships held at maximum vibrancy, the eye mixing what the painter divided.
**Passes:** tone_ground (high-key white) → underpainting → block_in × 2 → build_form × 2 → place_lights → signac_divisionist_mosaic_pass → paint_color_bloom_pass → diffuse_boundary_pass → glaze (cerulean) → glaze (chrome yellow) → vignette

*New this session: Paul Signac (1863-1935, Neo-Impressionism / Divisionism) — signac_divisionist_mosaic_pass (153rd distinct mode). THREE-STAGE DIVISIONIST MOSAIC: (1) Patch quantization via vectorised block-reshape mean pooling — canvas subdivided into rectangular tiles, each quantized to local mean colour — FIRST pass to apply divisionist colour quantization via numpy reshape producing rectangular-patch mosaic distinct from pointillist_pass (circular dots) and fauvist_mosaic_pass (Voronoi zones); (2) Complementary interleaving — tile-level checkerboard assigns even tiles primary colour, odd tiles hue-rotated-180° complement at comp_mix blend ratio — FIRST pass to interleave primary and complementary hue within the same quantized patch using tile-index checkerboard, implementing Chevreul simultaneous contrast at intra-patch level; (3) Simultaneous contrast boundary boost — at inter-patch boundaries with |delta_hue| > hue_thresh, saturation boosted proportionally to hue distance — FIRST pass to apply Chevreul simultaneous contrast as a boundary-localised hue-distance-weighted saturation boost. Improvement: paint_color_bloom_pass — saturation-gated colour irradiation where highly-saturated pixels bloom into adjacent areas; blue channel blooms fractionally further (shorter wavelength diffraction) creating chromatic fringe at outer bloom annulus — FIRST pass to apply saturation-threshold-gated colour bloom with proportional spread strength and differential blue chromatic fringe.*"""

FILENAME = "s242_signac_lighthouse_saint_tropez.png"


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

    print("Posting session 242 to Discord #gustave...")
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

    return msg_ids


if __name__ == "__main__":
    main()
