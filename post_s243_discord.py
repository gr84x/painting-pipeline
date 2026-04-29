"""Post session 243 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s243_kirchner_cafe_woman.png")

FILENAME = "s243_kirchner_cafe_woman.png"

TEXT_BLOCKS = [
    """\
**Woman at the Cafe Corner, Berlin** — Session 243

*Dark olive-black ground, Kirchner Die Brucke Expressionist mode — 154th distinct mode*

**Image Description**

A seated young woman at a small round marble cafe table in the corner of a Berlin cafe interior, ca. 1913 — viewed from slightly below eye level, at three-quarter angle, her body turned to face the viewer directly. The composition is portrait-format, with the woman occupying the lower-centre to lower-right of the canvas: her head and upper body emergent from the dark olive-black of the interior, the acid-yellow of her dress the only bright vertical axis in an otherwise near-black environment. Behind her, partially visible in the deep shadow of the upper-right, the edge of a dark male figure in cobalt-blue leans at an oblique angle, suggesting the social world of which she is part and in which she is nonetheless entirely alone.""",

    """\
**The Figure**

She is in her mid-twenties. She sits compactly, every line of her posture held in tension — not the graceful repose of academic portraiture but a coiled, guarded stillness. Her left arm rests flat on the marble table; her right hand holds the white coffee cup lightly, slightly raised. Her dress is acid chrome yellow with bold dark diagonal stripes — a fierce visual claim in the dim interior. Hair: dark, cut bluntly below the ears with a straight fringe across the forehead. Skin: acid lime-green — Kirchner's psychologically charged flesh-substitute, the colour of pallor under artificial light. Eyes: large, dark, absolutely direct. She meets the viewer without expression, without invitation, without retreat. The mouth is a narrow compressed line of cadmium red. Emotional state: tense, psychologically exposed, confrontational — someone who expects to be misread and has stopped correcting it.""",

    """\
**The Environment**

A Berlin cafe interior — dark, close, lit by a single harsh yellow gaslight positioned upper-right. The lamp casts a cone of warm amber light downward-left: the table glows with amber-gold beneath the coffee cup. The wall shadow to the left is cold cobalt blue — a harsh tonal jump with no modelled transition. Walls: dark olive-black panelling, barely legible panel lines, a single chair-rail moulding. The floor is dark ochre board receding into near-blackness. The background male figure is built from cobalt-blue and deep violet: a dark presence, semi-abstract, defined more by the space he occupies than by any specific form — a social context, not a character.""",

    """\
**Technique & Palette**

Ernst Ludwig Kirchner (1880-1938) Die Brucke technique — 154th distinct painting mode: the Kirchner Die Brucke Expressionist pass (session 243).

Stage 1, CHROMATIC DISSONANCE AMPLIFICATION: Five Kirchner chromatic poles (vivid red 0 deg, acid yellow 50 deg, acid lime 110 deg, cobalt blue 225 deg, vivid magenta 300 deg). Per-pixel hue rotated toward nearest pole; saturation boosted proportionally. First pass to implement multi-pole hue attraction using an artist-specific vocabulary.

Stage 2, WOODCUT CONTOUR DARKENING: Sobel gradient magnitude drives multiplicative darkening toward pure black at high-gradient pixels — simulating Kirchner's bold Die Brucke woodcut contour lines, the grammar of the woodblock translated to oil on canvas.

Stage 3, FLAT PLANE VALUE POLARIZATION: Local luminance mean computed via box filter; above-mean pixels pushed brighter, below-mean pixels pushed darker. Creates the hard tonal jumps between slab-like colour planes that Kirchner substituted for academic modelling.

Paint Imprimatura Warmth improvement (session 243): luminance-gated warm amber ground glowing through shadow zones and at brushstroke edges — simulating Rembrandt and Titian's toned ground technique in a dark Kirchner key.""",

    """\
**Palette:** Acid chrome yellow · deep cobalt blue · cadmium red · olive black · acid lime green (flesh distortion) · vivid magenta-violet · zinc white · near-black umber (woodcut contour) · warm amber imprimatura · dark violet (dress shadow)

**Mood & Intent**

Psychological tension. Raw confrontation. The painting proposes that beauty and discomfort are not opposites but neighbours — that the most honest portrait is also the most unsettling, because honest people do not arrange themselves for our comfort.

Kirchner understood Berlin cafe culture as a space of performance and anonymity: everyone visible, no one seen. The woman at the cafe table is visible. She turns to look at us. She is not performing. The viewer is meant to leave with the feeling of having made eye contact with a stranger who held the gaze a beat too long — haunted by a face met briefly and not remembered clearly, but which measured them and found them ordinary.

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
