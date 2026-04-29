"""Post session 245 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s245_jawlensky_mystic_at_prayer.png")

FILENAME = "s245_jawlensky_mystic_at_prayer.png"

TEXT_BLOCKS = [
    """\
**The Mystic at Prayer** — Session 245

*Deep violet-umber ground, Alexej von Jawlensky Abstract Head mode — 156th distinct mode*

**Image Description**

A solitary elderly man's face fills the canvas in near-total frontality — the iconic, devotional composition Jawlensky made his life's work. The head tilts infinitesimally downward and leftward, as if in the act of internal listening rather than external gaze. He occupies nearly 70% of the canvas height; the upper fifth shows only the warm gold dome of his cranium and the indigo-violet void above. There is no room, no window, no horizon. The environment is colour itself.""",

    """\
**The Figure**

The man is of indeterminate age between sixty and ancient — a peasant or a saint, a face worn smooth by decades of inner weather. His eyes are closed. Not sleeping: closed with deliberate weight, the heaviness of chosen inward sight. Deep eyelid arcs in near-ultramarine create the horizontal grammar of the face. The nose descends as a warm vertical ridge, its base flanked by deep blue-tinted nostrils. His mouth is barely parted — two faint horizontal lines of rose-violet and dark, between them a silence that feels held.

A flowing beard continues the warm amber and rose tones of the face downward, fading at its lower edge into the cool violet ground. The emotional state: profound inner absorption, bordering on ecstasy or grief — but controlled, turned inward, not displayed for the viewer's benefit. He is elsewhere. He is entirely present.""",

    """\
**The Environment**

Concentric radiating fields of pure hue emanate from the face's centre. At the face's heart: hot amber and saffron glowing like a lantern seen through oiled paper. Moving outward: deep orange, then rose-violet at the cheeks and brow. Beyond the face's edge, the air shifts to acid olive green, then deep cobalt blue, then an outer field of deep violet verging on near-black.

These are not shadows. They are zones of spiritual temperature. The warm inner core is the soul's light; the cool outer darkness is the world it inhabits. The hair on both sides is painted as flat cobalt-blue masses — not hair rendered but hair as pure chromatic zone, as Byzantine gold ground translated into blue. The shoulders dissolve at canvas edge into the same deep cobalt field, giving the figure a quality of emergence from the void rather than placement within a space.""",

    """\
**Technique & Palette**

Alexej von Jawlensky (1864-1941) Abstract Head mode — session 245, 156th distinct painting mode.

Stage 1, RADIAL WARMTH GRADIENT: Normalised radial distance from the image centroid drives a per-pixel hue attraction toward amber/saffron (~35°) in inner zones. The strength falls off linearly with distance: full warmth at the centroid, zero at inner_radius. This encodes Jawlensky's spiritual warmth radiating from the face's centre — inner zones hot amber, saffron, rose — as a spatial quantity rather than a painterly gesture. First pass to apply inward-warm/outward-cool hue shift weighted purely by centroid-radial distance.

Stage 2, COOL PERIPHERAL PUSH: Pixels beyond outer_radius receive hue attraction toward blue-violet (~230°) with strength proportional to peripheral distance. Simultaneously, saturation is boosted and value is lifted in the outer zone, creating the luminous cool-halo framing Jawlensky's central forms. First pass to apply cool-hue shift + saturation boost + value lift together in the image periphery only, gated by radial distance from centroid.

Stage 3, ULTRAMARINE EDGE TINT: Sobel gradient magnitude detects form boundaries. Edge pixels are blended toward deep ultramarine-dark (R=0.08, G=0.10, B=0.38) rather than pure black. Unlike Beckmann's achromatic armature or Kirchner's multiplicative darkening, this introduces chromatic blue in the contour lines — the signature of Jawlensky's thick painted outlines in his Abstract Heads series. First edge pass to use a configurable blue-dark rather than achromatic black.

Paint Optical Vibration improvement (session 245): Pixels classified as warm (hue 0–90° or 320–360°) and cool (90–270°) form two competing fields. A Gaussian blur of the warm/cool classification map, followed by gradient magnitude extraction, identifies warm-cool boundary zones. Warm pixels at boundaries are pushed toward orange (~30°); cool pixels toward blue-green (~210°). Saturation is boosted at boundary zones proportionally to boundary strength. The result is the optical oscillation Albers described in Interaction of Color (1963) — the visual vibration at warm-cool interfaces that Jawlensky and the Expressionists exploited to make colour feel alive.""",

    """\
**Palette:** Hot amber · saffron · rose-violet (cheeks/brow) · deep cobalt blue (outer zone/hair) · acid olive green (peripheral accent) · near-ultramarine dark (contour lines) · warm ivory (inner highlight) · deep violet (outer shadow field)

**Mood & Intent**

This is a devotional object — an icon stripped of narrative, gold ground, and specific divinity, but not of spiritual intensity.

The warm-to-cool radial gradient makes a single statement: something burns here, at the centre. The closed eyes say: it does not burn outward for your approval. The ultramarine contours say: this form was *drawn* before it was *painted* — the structure beneath precedes the light above.

Jawlensky spent the last years of his life painting over 1,200 tiny Meditations — works small enough to hold in a fist, as his arthritis had reduced his hand to a near-claw. He continued until death. This is what that kind of practice looks like, translated to a larger scale: the face reduced to its essential architecture, the colour reduced to its essential temperature, nothing remaining that is not necessary.

The viewer should leave with the sensation of having been briefly in the presence of a face that has learned to carry its interior without protest — old amber at the core, cold violet at the edge, nothing wasted.

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
