"""Post session 250 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s250_mitchell_summer_flood.png")

FILENAME = "s250_mitchell_summer_flood.png"

TEXT_BLOCKS = [
    """\
**Summer Flood, Hudson Valley** -- Session 250

*Off-white linen ground, Joan Mitchell Gestural Arc mode -- 161st distinct mode*

**Image Description**

An all-over abstraction in landscape memory -- the physical sensation of standing at the Hudson Valley's edge in midsummer after rain, when the river has risen and the fields gone silver-green and the sky pressed low with water. No horizon line. No depth cue. The canvas is organised from lower-left to upper-right in a diagonal surge of energy, with a zone of relative stillness in the lower right and a dense knot of mark activity in the upper centre-left.

The marks themselves are the subject. Large circular arc sweeps in cobalt and deep violet in the upper field -- arm-arc gestures that follow the curve of the shoulder -- surging from lower right to upper left as if recording the upward drive of floodwater. Against them: short rapid yellow and cadmium marks that cut horizontally, the intensity of summer light broken into incident. A zone of viridian and sap green in the lower left sits heavily, like waterlogged fields pressed to the ground. Raw white strokes scattered through the centre: the silver glare of water surface.""",

    """\
**The Mark Field**

A single dark mass in the lower right -- dense near-black and burnt sienna -- anchors the composition against the surge: a stand of trees, a mud bank, the weight of earth against the flood. The marks have emotional states: the blue arcs are urgent, the green mass is patient and heavy, the white glare is indifferent, the black anchor is still.

**The Ground**

No environment outside the marks. The canvas ground is warm off-white linen. It shows through in the sparse zones as the breathing space Mitchell always preserved -- the lung of the composition. The background does not recede but holds the marks at the surface. All space is flat but all space is active: even the unpainted areas carry the memory of the marks around them.""",

    """\
**Technique & Palette**

Joan Mitchell (1925-1992) Gestural Arc mode -- session 250, 161st distinct painting mode.

Stage 1, LARGE CIRCULAR ARC GESTURAL MARKS: 30 arc marks scattered across the canvas, each a circular arc segment at random radius (0.18 to 0.52 * min_dim) and arc span (0.6 to 2.1 radians). Each mark rendered by computing minimum angular distance to the nearest arc point and applying brightness_shift within mark_width=4.5px. The result is a field of curved gestural marks tracing the arm-arc movement of the painter at full extension. NOVEL: FIRST PASS to rasterize gestural marks as curved circular arc segments defined by centre, radius, start angle, and arc span; Basquiat (s249) uses straight line-segment rasters; Kline (s119) uses calligraphic mega-strokes derived from gradient orientation -- neither parameterizes marks as curved arcs.

Stage 2, WET-SPREAD DIRECTIONAL COLOUR BLEED: High-saturation pixels (sat > 0.26) receive anisotropic Gaussian blur [sigma_lo=1.4, sigma_hi=3.2] simulating wet paint spreading laterally from mark into adjacent ground. Only the most intensely coloured pixels spread into neighbours, creating the soft boundary between cobalt arc and off-white ground. NOVEL: FIRST PASS with saturation-gated anisotropic colour bleed; no prior pass gates anisotropic bleed by per-pixel saturation value.""",

    """\
Stage 3, MARK DENSITY SATURATION RHYTHM: The arc density field drives saturation: dense zones +0.24, sparse zones -0.12. Creates the characteristic dense-sparse alternation of all-over composition. NOVEL: FIRST PASS to modulate saturation by a spatially derived arc mark density field.

**Palette:** Cobalt blue (0.14/0.36/0.72) -- Viridian-deep green (0.22/0.54/0.28) -- Cadmium yellow (0.92/0.84/0.18) -- Cadmium red-orange (0.82/0.26/0.18) -- Titanium white/off-linen (0.90/0.88/0.84) -- Near-black (0.14/0.12/0.10) -- Deep violet (0.68/0.30/0.64) -- Cerulean (0.62/0.80/0.88) -- Burnt sienna (0.72/0.38/0.22) -- Yellow-green (0.38/0.64/0.30)

Paint Chromatic Underdark improvement (session 250): Shadow zones enriched toward deep indigo-violet (dark_hue=0.70), weighted by existing per-pixel saturation via HSV hue rotation. Shadow clarity lift (clarity_amount=0.20) via shadow-masked unsharp mask preserves dark mark texture. NOVEL: (a) FIRST IMPROVEMENT PASS with configurable hue anchor shadow enrichment in HSV space, saturation-weighted; (b) FIRST IMPROVEMENT PASS to apply shadow-zone unsharp mask clarity.""",

    """\
**Mood & Intent**

Mitchell said: "I carry my landscapes around with me." This painting intends the quality of carried landscape -- not a view but a sensation, not a document but a physical residue. The surge of blue arcs from lower right to upper left is the body's memory of standing at the river's edge as the water rose. The green mass is the weight of saturated earth. The yellow cuts are the way summer light comes through rain.

The viewer should feel the physical sensation of being inside weather -- not watching it but standing inside it -- and the particular emotional state Mitchell sought in her paintings: the exhilaration of the body's response to natural scale and force.

*New this session: Joan Mitchell (Abstract Expressionism, American, 1925-1992) -- mitchell_gestural_arc_pass (161st distinct mode). CIRCULAR ARC SEGMENT GESTURAL MARKS: curved arc rasters by centre/radius/span + WET-SPREAD DIRECTIONAL COLOUR BLEED: saturation-gated anisotropic bleed + MARK DENSITY SATURATION RHYTHM: arc density modulated saturation. PAINT_CHROMATIC_UNDERDARK_PASS: HSV hue anchor shadow enrichment + shadow clarity lift.*

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
