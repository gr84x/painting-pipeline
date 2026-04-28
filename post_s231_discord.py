"""Post session 231 painting to Discord #gustave channel."""
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
                          "s231_vrubel_demon_edge.png")

IMAGE_DESCRIPTION = """**The Demon at the Edge of the World** — Session 231

*Oil on linen, deep violet-indigo imprimatura, Vrubel Crystal Facet mode*

**Image Description**

A vast demon sits at the edge of a precipice, viewed from slightly below and to one side — the viewer looks upward into the figure's face and spread wings. The demon is enormous, occupying most of the canvas. It does not stand; it sits — or perhaps crouches — at the rim of a rocky escarpment, its body turned slightly inward, contemplative rather than threatening.

The figure: massive violet-blue torso, each plane of form a distinct angular facet of colour — one plane deep indigo, the adjacent plane violet-mauve, the next burnished amber where the distant light catches it. The surfaces catch and refract like a crystal or shattered mirror, each facet holding its own colour. The head is oval, the face warm terracotta-flesh, lit from the far distance — two burning gold eyes stare into middle distance, not at the viewer. A fragmented gold crown floats above: not a solid ring but scattered points of gilt light, like broken Byzantine mosaic tiles rearranged into a halo.

The wings spread wide to both edges of the canvas — dark angular shapes, nearly black with a deep indigo-violet under-glow, their leading edges faintly glinting malachite-green where they catch the horizon light. The wings do not suggest flight; they are simply part of the demon's form, spread in rest the way a resting bird holds its wings slightly open.

The hands reach downward and outward, large and pale, nearly resting on the rock edge. Between the demon's figure and the rocky base — robes, or what might be robes — cascade in faceted violet-purple folds, each fold holding its own plane of colour, like tilted mirror-fragments of purple and indigo.

The precipice below: dark irregular rock faces in angular planes, stone-grey and violet-brown, receding into near-shadow at the canvas edges. Between the rocks and the demon's base, scattered tiny flowers — lilacs or wildflowers — small round touches of lavender and pale mauve, the only soft round forms in a painting otherwise composed of angular crystal planes.

The sky behind: deep violet-indigo at the top, graduating through twilight blue to a horizon band of mauve-gold at the level of the demon's chest — a distant sunset that gives the figure's face its warm terracotta glow and the far wing-edges their malachite gleam. The horizon is the only warm zone in the palette; everything else inhabits the cool jewel-blue of dusk or deep night.

**Technique:** Mikhail Vrubel Crystal Facet (142nd distinct mode)
**Palette:** Deep lapis blue · violet-mauve · burnished gold-amber · malachite green · periwinkle crystal · near-black indigo · pale terracotta flesh · lavender
**Mood:** The great exhaustion of power — a figure who holds immense strength and feels it as burden rather than gift. The viewer should feel awe without fear, and beneath the awe, a faint sadness for something ancient and beautiful that cannot rest. Vrubel painted his Demon not as villain but as sufferer; the image should carry that weight.
**Passes:** tone_ground (deep violet-indigo) → underpainting → block_in × 2 → build_form × 2 → place_lights → vrubel_crystal_facet_pass → midtone_clarity_pass → impasto_relief_pass → glaze (cool violet) → vignette

*New this session: Mikhail Vrubel (1856-1910, Russian Symbolism / Art Nouveau) — vrubel_crystal_facet_pass (142nd distinct mode). CRYSTAL FACET SURFACE MODEL: (1) Pre-smoothed Sobel gradient edge detection at macro scale (facet_sigma=4.5px) — finds region-level colour plane boundaries, not pixel noise; (2) Grout darkening — darkens at detected edges to simulate dark lines between mosaic/crystal tiles; (3) Facet interior jewel boost — saturation enhancement in low-gradient interior zones for iridescent crystalline quality. Improvement: midtone_clarity_pass — luminance bell-curve gated unsharp mask strongest at lum=0.50, sharpening mid-tone form detail while preserving painterly softness in shadows and highlights (complement to hammershoi_grey_interior_pass stillness haze).*"""

FILENAME = "s231_vrubel_demon_edge.png"


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

    print("Posting session 231 to Discord #gustave...")
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
