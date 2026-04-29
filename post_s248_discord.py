"""Post session 248 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s248_stael_harbor_agrigento.png")

FILENAME = "s248_stael_harbor_agrigento.png"

TEXT_BLOCKS = [
    """\
**Harbor at Agrigento, Dusk** — Session 248

*Burnt sienna ground, Nicolas de Stael Palette Knife Mosaic mode — 159th distinct mode*

**Image Description**

Three fishing boats moored side by side at a Sicilian harbour quay, seen from dock level looking across the boats toward the open sea. The composition is wide and horizontal, divided into strong bands: a burning cobalt-to-orange sky above, a simplified ochre limestone quay wall in the middle, the dark sea-green harbour water below. The three boat hulls — burnt sienna-red, weathered steel-blue, warm ochre-yellow — are the dominant vertical forms, each a single bold rectangle of colour pressed against the horizontal bands. A single tall mast rises from the centre boat, the only vertical element that crosses from the water zone into the sky.""",

    """\
**The Boats**

Left boat: a broad low wooden hull of burnt sienna-red, heavy and rounded at the bow, sitting low in dark water. A short cream-white superstructure sits forward. Its own reflection stretches directly below it — a bold red band in the dark harbour.

Centre boat: slightly larger. A weathered steel-blue hull — pale cobalt-grey, the blue of Mediterranean shadow in the late afternoon. Its cream-white cabin is cube-like, decisive. From the cabin roof, a single tall slim mast reaches into the orange sky — dark navy, the only vertical ambition left in the frame. The centre boat is the compositional anchor.

Right boat: a warm ochre-yellow hull, the yellow of Sicilian limestone in late light. Lower and flatter. No cabin visible — just the broad plane of deck and hull.

Three coloured rectangles. That is all. That is everything.""",

    """\
**The Environment**

Sky: deep cobalt blue at the zenith, transitioning through indigo and rich violet to a burning band of cadmium orange at the horizon — the sky at the exact moment before the sun disappears, when the orange is at its most saturated. A faint amber blush where sky meets water.

Quay wall: a simple horizontal band of warm Sicilian limestone — ochre, slightly worn. The boundary between sky and water. Clean. Architectural.

Water: the inner harbour is dark sea-green, nearly still. It holds pale cobalt reflections of the sky and warm amber streaks of dusk light. The hull reflections — red, blue, ochre — run as bold vertical bands down from the waterline, shimmering only slightly in the near-still harbour.""",

    """\
**Technique & Palette**

Nicolas de Stael (1914-1955) Palette Knife Mosaic mode — session 248, 159th distinct painting mode.

Stage 1, RECTANGULAR TILE MEAN QUANTIZATION: The canvas is divided into a grid of rectangular tiles (24x32 pixels for the first pass, 12x16 for the second). For each tile, the arithmetic mean of all pixel colours is computed. Every pixel in that tile is replaced with this mean. The result is a mosaic of flat rectangular colour planes — the same reduction of a scene to its essential colour geometry that de Stael achieved with his palette knife, where each deposit of paint carries a single dominant hue and the scene is abstracted into blocks rather than rendered in continuous tones. First pass to apply rectangular spatial mean pooling as a primary colour processing stage.

Stage 2, INTRA-TILE DIRECTIONAL KNIFE GRADIENT at 12 degrees (first pass) and 168 degrees (second pass): Within each tile, a slight directional luminance gradient at knife_angle_deg simulates the palette-knife drag direction. The gradient is a tiled template applied consistently across all tiles, reproducing the consistent knife-stroke direction of a single passage. First pass to add a parametric directional ramp within quantized colour blocks using a shared tiled template.

Stage 3, TILE BOUNDARY GAP DARKENING: Pixels within 2 pixels of any tile boundary are darkened proportionally to their proximity to that boundary — simulating the slight trough where the knife lifts between adjacent paint deposits. First pass to darken pixels specifically based on distance to spatial quantization boundaries.""",

    """\
**Palette:** Burnt sienna-orange (sky band, red hull) — Cobalt blue (upper sky, blue hull, deep water) — Raw ochre-yellow (quay stone, yellow hull, sunlight) — Brick red (left boat hull) — Slate blue-grey (weathered hull, water shadow) — Cream-white (superstructure, bright sky band) — Amber gold (dusk water reflection) — Deep sea-green (harbour depth, water base)

Paint Halation improvement (session 248): Bright pixels (luminance > 0.72) generate a warm orange Gaussian bloom at sigma=18 that bleeds softly into surrounding cobalt and grey areas, simulating the halation effect of strong dusk light — the bleeding warmth that occurs in Mediterranean evenings when the orange is so intense it affects the colour of everything it neighbours. First improvement pass to create a brightness-gated, tinted, spatially-soft Gaussian glow.

**Mood & Intent**

This painting attempts what de Stael achieved in his Mediterranean harbour paintings of 1953 and 1954: the reduction of a specific, luminous scene to its essential colour geometry. Not the boats as boats — but the boats as three coloured rectangles standing against a burning sky.

The mood is the particular richness of a Mediterranean summer evening at the exact moment of dusk, when every surface has become more intensely itself — the red hull redder, the blue hull more deeply blue, the ochre stone more golden. The harbour is emptying. The day is done. The water is still.

De Stael was not a melancholy painter. He believed a single decisive colour block could contain everything that needed to be said. One decisive rectangle of burnt sienna. One of weathered cobalt. One of warm ochre. The sky burning above. The dark water holding everything below.

*New this session: Nicolas de Stael (Abstract Expressionism / Lyrical Abstraction, Russian-French, 1914-1955) — de_stael_palette_knife_mosaic_pass (159th distinct mode). TILE MEAN QUANTIZATION: rectangular mean pooling into colour planes + INTRA-TILE KNIFE GRADIENT at parametric angle + TILE BOUNDARY GAP DARKENING. PAINT_HALATION_PASS: brightness-gated Gaussian bloom with RGB tint.*

*Paint with patience and practice, like a true artist.*""",
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
        chunks.append(text[:split_at].rstrip())
        text = text[split_at:].lstrip()
    return chunks


if __name__ == "__main__":
    all_msg_ids = []

    for block in TEXT_BLOCKS:
        for chunk in split_text(block):
            mid = post_text(chunk)
            all_msg_ids.append(mid)
            time.sleep(1.2)

    img_id = post_image(IMAGE_PATH, FILENAME)
    all_msg_ids.append(img_id)

    print(f"\nAll message IDs: {all_msg_ids}")
