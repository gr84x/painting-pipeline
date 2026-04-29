"""Post session 244 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s244_beckmann_tarot_reader.png")

FILENAME = "s244_beckmann_tarot_reader.png"

TEXT_BLOCKS = [
    """\
**The Tarot Reader** — Session 244

*Dark umber near-black ground, Max Beckmann Black Armature mode — 155th distinct mode*

**Image Description**

A middle-aged woman tarot reader seated at a low round table, seen from a three-quarter angle slightly above and to her right. She is the dominant figure; the table, spread cards, candlestick, and symbolic objects fill the lower half of a vertical canvas pressed tight with Beckmann's characteristic refusal of recession. A dark compressed background figure occupies the upper-left shadow. A thick rope descends from the upper-left corner into near-blackness. Everything is pushed toward the viewer — no air, no atmospheric distance, no escape from the encounter.""",

    """\
**The Figure**

She is in her mid-to-late forties. Heavyset, strong hands. She sits with her torso angled slightly toward the viewer, arms spread wide over the cards — left hand flat on the table surface, right hand raised in a gestural half-halt, fingers splayed. Her dress: deep teal with bold vertical black stripes, the Beckmann armature visible as dark bands between the stripes. Skin: acid yellow-green, Beckmann's psychologically charged flesh-substitute, the colour of pallor under candlelight filtered through a closed room. Hair: dark, cut bluntly.

Her face is turned directly to the viewer. Wide dark eyes — cold blue-violet irises, heavy near-black lids — meet the viewer without expression, without invitation, without retreat. The mouth is a compressed line of brick red. She has just finished reading the cards. Her emotional state is controlled concealment: the practiced stillness of someone who knows what the future holds and has decided how much to reveal. She is measuring us. We did not consent to be measured.""",

    """\
**The Environment**

A cramped, airless room. Near-black walls with barely legible panelling — forms pressed to the surface, no recession. Upper right: a brick-red curtain in broad vertical folds, three near-black shadow-bands between the folds. Lower left: a wooden plate bearing a large fish rendered in acid green — Beckmann's symbolic object, eye visible, more sign than anatomy, the fish as ambiguous moral prop, neither explained nor apologised for. The rope descending from the upper-left corner is similarly silent — a presence in the image as unexplained as fate itself.

The table is dark brown with a lit salmon-orange edge. Across the table, seven tarot cards are spread in a rough arc: ivory faces, cold blue-violet reverses visible on the turned ones. A single tall candlestick stands to the figure's right — dark umber shaft, warm yellow flame, casting a small hot pool of light that warms the right quarter of the scene. The left is given to cold shadow. At upper-left, barely distinguishable from the wall, a second figure exists only as dark umber mass — a presence, not a person; a social weight, not a character.""",

    """\
**Technique & Palette**

Max Beckmann (1884-1950) Black Armature Expressionist mode — session 244, 155th distinct painting mode.

Stage 1, GRADIENT-THRESHOLD SATURATION-STRIPPING SNAP TO BLACK: Sobel gradient detection identifies high-gradient edge pixels. Where the normalised gradient exceeds the armature threshold, saturation is simultaneously stripped and value snapped toward near-black with strength proportional to gradient magnitude. The result is Beckmann's decisive drawn-black armature — fully desaturated, structurally non-negotiable — bounding every form from within the canvas like a woodcut grid translated into oil. First pass to combine saturation removal with value snap at form boundaries.

Stage 2, BIDIRECTIONAL VALUE RANGE COMPRESSION TOWARD MIDTONE: The full tonal range is contracted symmetrically: V′ = mid + (V − mid) × (1 − compress_str). Both extremes are brought toward the mid-grey anchor. Shadows lift slightly, highlights lower. The result is the airless, claustrophobic tonal flatness characteristic of Beckmann's interiors — no deep shadow, no brilliant highlight, everything held in a compressed, suffocating mid-range. First pass to apply symmetric tonal contraction toward a configurable midtone anchor.

Stage 3, BECKMANN PALETTE ATTRACTION WITH PROPORTIONAL ANGULAR SNAP: Five hue poles — salmon-orange 15°, acid yellow-green 80°, deep teal 175°, cold blue-violet 220°, brick red 350°. Per-pixel hue is moved palette_str fraction of the remaining angular gap to the nearest in-radius pole. The snap is proportional to proximity — close hues jump decisively, far hues barely move — creating sudden non-naturalistic hue jumps characteristic of Beckmann's psychologically charged colour decisions.

Paint Aerial Perspective improvement (session 244): Difference-of-Gaussians spatial-frequency analysis estimates scene depth from image smoothness — smooth background regions are identified as distance, desaturated proportionally, and tinted with a cool haze colour. The far wall and curtain recede slightly while the dense foreground figure and candlelight remain sharp.""",

    """\
**Palette:** Salmon-orange · acid yellow-green (flesh distortion) · cold blue-violet · brick red · deep teal · near-black armature · zinc white · raw umber (shadow) · candle yellow · dark umber (figure masses)

**Mood & Intent**

Psychological entrapment. Existential confrontation without resolution.

The painting's central proposition is that we — the viewer — are not observers of the reading. We are its subject. The cards are spread. The reader has read them. She is now looking at us over the table. We cannot see the cards. We can only see her face, which has already processed what they say.

This is Beckmann's essential discovery: the figure in the painting is not the subject. The viewer is. The painting is a mirror that has a mind. The woman across the table has seen something in our future and chosen not to speak it plainly. We leave the room knowing that something was measured, and that the measurement was not flattering, and that we will not be told the result.

The rope in the corner was always there. We did not notice it until now.

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
