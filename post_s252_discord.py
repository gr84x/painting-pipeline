"""Post session 252 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s252_richter_motorway.png")
FILENAME   = "s252_richter_motorway.png"

TEXT_BLOCKS = [
    """\
**Motorway in Rain** -- Session 252

*Cool grey-beige ground, Gerhard Richter Squeegee Drag mode -- 163rd distinct mode*

**Image Description**

A section of wet German motorway viewed from directly above at a shallow diagonal -- the road surface occupies the full canvas, filling it edge to edge. Two lanes of tarmac recede in a tight perspective from the lower right to upper left, the white lane markings pulled into blurred streaks by motion and rain. No sky is visible. No horizon. The road is everything. Two dark vehicular smears at mid-left suggest cars that have dissolved into their own velocity. The composition is horizontal, nearly abstract, with the asphalt surface as both ground and subject.

The cars -- two of them, side by side -- exist as dark rectangular masses dragged horizontally across the wet tarmac, their outlines completely dissolved into the surrounding wet surface. They have the density of shadows without the precision of objects. No windows, no wheels, no chrome -- only the pressure of mass moving through wet paint. Emotional state: velocity as erasure, the modern landscape as surface without interiority, objects subsumed into weather.""",

    """\
**The Environment**

The tarmac is a complex chromatic neutral -- not grey but a layered field of cool blue-grey, warm ash, and cold near-black. The wet surface holds light: horizontal bands of pale silver-white reflection from overhead strip lighting dissolve and smear across the dark ground. The lane markings are white -- or were white -- now drawn out into long trailing smears by the squeegee and the implied rain. The road edges at left and right dissolve into near-black. Foreground detail is high: every water channel, every tarmac ridge articulated. Toward the upper-left the entire surface dissolves into a uniform near-grey, as if the road disappears into its own distance.

**Technique & Palette**

Gerhard Richter (born 1932, Dresden) Squeegee Drag mode -- session 252, 163rd distinct painting mode.

Stage 1, HORIZONTAL DRAG BAND DECOMPOSITION: n_bands=28 horizontal strips of randomly varied height (18--65 pixels). drag_fraction=0.72 mixes the dark asphalt tones laterally across each band, sampling 10 rows above and below (drag_offset=10). NOVEL: FIRST PASS to apply spatially partitioned horizontal drag band averaging that mixes colour between adjacent bands rather than a uniform global blur; no prior directional pass decomposes the canvas into random-height horizontal drag bands with cross-band colour averaging as its primary colour stage.""",

    """\
Stage 2, LATERAL PIGMENT CHANNEL TRAILS: sat_threshold=0.18 (low -- the palette is largely desaturated); trail_length=60, trail_strength=0.62. At each inter-band boundary, pixels above sat_threshold receive a 60-pixel horizontal trail blur, creating the concentrated colour ridges Richter called "pigment rivers." NOVEL: FIRST PASS to detect saturation-gated pigment concentrations at drag-band boundary rows and apply directional trail blur along the drag axis as a distinct secondary stage.

Stage 3, DRAG RESIDUE LUMINANCE MODULATION: residue_amp=0.042. Sinusoidal brightness variation across each band height: brightening at the leading edge (blade thinning paint) and darkening at trailing edge (paint accumulating before blade). NOVEL: FIRST PASS to apply band-coordinated sinusoidal luminance modulation parameterised by fractional position within each drag band.

**Improvement Pass -- Surface Tooth** (session 252): grain_size=8, fiber_amplitude=0.022, cross_boost=0.014, ridge_strength=0.018, light_angle=38°. Warp-and-weft sinusoidal fiber grid with fiber crossing micro-contrast and directional ridge catch-light. NOVEL: FIRST PASS to generate a dual-direction warp-and-weft periodic fiber product texture with peak-gated micro-contrast at fiber crossings and anisotropic ridge catch-light.""",

    """\
**Palette**

Cool blue-grey tarmac (0.42/0.44/0.46) -- Warm ash mid-grey (0.62/0.60/0.56) -- Wet silver reflection (0.84/0.84/0.82) -- Near-black asphalt depth (0.12/0.12/0.14) -- Cadmium warm trace (0.72/0.52/0.28) -- Cold blue-violet distance (0.34/0.38/0.52) -- White lane marking (0.94/0.94/0.92)

**Mood & Intent**

The image intends the quality Richter identified in his photo-paintings: the blurring as epistemology -- what painting can claim to know about an image is always already compromised by the act of painting it. The motorway is both specific (post-war German modernity, wet winter, fluorescent strip-light) and universal (the road as the modern sublime, infrastructure as landscape). The viewer should feel the speed and the cold and the particular quality of attention that photographs allow -- a world seen without a body.

*Gerhard Richter (born 1932) -- 252nd artist in catalog | 163rd distinct mode | 35 tests passing*""",
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
    time.sleep(0.5)

    print(f"\nAll message IDs: {all_msg_ids}")
