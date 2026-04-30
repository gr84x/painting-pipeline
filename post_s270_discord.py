"""Post session 270 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s270_jimson_weed.png")
FILENAME   = "s270_jimson_weed.png"

TEXT_BLOCKS = [
    """\
**White Jimson Weed, Desert Night** -- Session 270

*Warm cream ground, Georgia O'Keeffe Organic Abstraction mode -- 181st distinct mode*

**Subject & Composition**

A single large jimson weed (Datura wrightii) flower viewed from slightly below and in front, the enormous white trumpet blossom filling the portrait canvas (1040 × 1440). The flower is centred and monumental -- five fused petals form a deep funnel that opens toward the viewer, the interior of the tube dropping into deep crimson shadow at the base, the outer petals curling and spreading into near-white luminosity at the tips. The composition references O'Keeffe's "Jimson Weed/White Flower No. 1" (1932) -- in which a single datura bloom is enlarged to canvas scale, stripped of all botanical illustration, and made purely architectural: the curve of one petal as grand as the face of a cliff, the shadow at the throat as deep as a canyon. No stem, no leaf, no context beyond the flower itself and the deep indigo sky behind it.""",

    """\
**The Subject**

The flower occupies approximately 80% of the canvas. Five petals radiate from a central trumpet throat: the petals are pure white in the highlights, shading through warm peach and salmon in the mid-tones, then through deep rose and crimson as they curve into the throat shadow. Each petal carries a faint midrib crease -- the fold at the centre of each corolla section -- visible as a warm luminous ridge in the near-white outer zone and as a slightly warmer tone in the peach mid-zone.

The emotional state of the subject is NOCTURNAL RADIANCE: the flower blooms at night, its white petals acting as a reflector and light-emitter in the darkness. The datura is toxic, beautiful, and night-blooming -- a quality of both serenity and strangeness.

**The Environment**

Background: deep indigo-blue-violet night sky (0.10/0.12/0.30), occupying the corners and upper edge of the canvas. The sky is slightly lighter at the upper centre -- a hint of moonlight -- and deeper and cooler at the corners. The transition from flower edge to sky is sharp and clean, as in all O'Keeffe paintings. The foreground below the flower throat: a dark warm umber depth in the very lowest portion of canvas where the stem would be.""",

    """\
**Technique & Passes**

Georgia O'Keeffe Organic Abstraction mode -- session 270, 181st distinct mode.

`okeeffe_organic_form_pass` -- FOUR-STAGE ORGANIC FORM REFINEMENT inspired by Georgia O'Keeffe (1887-1986):

Stage 1 (LOCAL LUMINANCE VARIANCE ZONE DETECTION): Compute per-pixel local luminance variance via gaussian(L²) - gaussian(L)² at variance_sigma. Identify SMOOTH INTERIOR zones (var ≤ 25th-percentile of nonzero variance) and EDGE zones (var > edge_threshold). First pass to use joint topology of smooth vs edge zones as opposing targets for two complementary operations -- smoothing and sharpening.

Stage 2 (VARIANCE-GATED INTERIOR SMOOTHING): Blend Gaussian-blurred canvas toward current canvas at smooth_strength, BUT ONLY in smooth interior zones -- zero effect at edge zones. First pass to gate Gaussian smoothing specifically to low-variance form interior regions, concentrating the O'Keeffe silky surface quality in the correct zone (the form interior) without softening edges.

Stage 3 (FORM-TURNING ZONE SATURATION LIFT): Detect pixels in mid-luminance range [0.28, 0.68] AND low local variance (below mid_variance_cap) -- the "form-turning zone" where a surface curves away from the light. Apply saturation lift by pulling each channel away from luminance. First pass to use joint luminance-range AND variance conditions to locate the tonal transition zone for targeted saturation intensification.""",

    """\
**Technique (continued)**

Stage 4 (EDGE-GATED UNSHARP MASKING): In high-variance edge zones, apply unsharp masking: canvas + amount × (canvas - blur). Leaving smooth interior zones completely untouched. First pass to gate USM sharpening to variance-detected edge zones only -- creating O'Keeffe's clean crisp boundary between adjacent colour masses while preserving the silky smooth interior of each form.

Session improvement s270 (`paint_translucency_bloom_pass`) -- TRANSMITTED LIGHT GLOW inspired by O'Keeffe's backlighted petals and Jan van Huysum's thin glazes:

Stage 1 (TRANSLUCENT ZONE DETECTION): Detect pixels that are simultaneously high-luminance [0.52, 0.88] AND low-saturation (< threshold) -- the physical signature of thin translucent material where light passes through. First pass to use joint luminance-and-low-saturation as a proxy for thin-material translucency.

Stage 2 (WARM INNER BLOOM): Accumulate a warm glow field (warm R lift, suppressed B) from detected translucent zone pixels; blur at sigma=bloom_sigma; blend back at bloom_strength. Creates the characteristic interior warm glow of backlighted thin material -- petals that appear lit from within.

Stage 3 (EDGE LUMINOUS HALO): Dilate the translucent zone mask, subtract original to get boundary ring, apply luminous warm-white halo. Simulates the brightness at the petal edge where reflected AND transmitted light add together -- the thin bright outline characteristic of a sunlit petal edge.

Full pipeline: tone_ground (warm cream 0.94/0.90/0.84) → underpainting (×2) → block_in (×2) → build_form (×2) → place_lights → paint_translucency_bloom_pass → okeeffe_organic_form_pass → paint_lost_found_edges_pass → paint_granulation_pass""",

    """\
**Mood & Intent**

The image intends NOCTURNAL RADIANCE and MONUMENTAL QUIETUDE. The viewer is confronted with the flower as architecture -- a structure as large and ordered as any built thing, but made of living tissue and open only in darkness. The white of the petals is not innocent or gentle; it is the white of something that glows in the dark by internal necessity. The deep indigo sky presses against the petals; the flower holds.

The emotion is a kind of reverent strangeness -- the datura does not bloom for human eyes, and observing it at this scale, this close, feels like a trespass.

*Georgia O'Keeffe (1887-1986) -- American Modernist, founding figure of American abstraction and the most celebrated woman artist in the history of American painting. Her close-up flower series of the 1920s-30s remains among the most recognisable images in American art.*

Session 270 | Georgia O'Keeffe (267th artist) | 181st distinct pass mode | 1040 × 1440""",
]


def curl(args):
    cmd = ["curl", "-sS"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print(f"curl error: {result.stderr[:400]}")
    return result.stdout


def send_message(text: str) -> str:
    payload = json.dumps({"content": text})
    out = curl([
        "-X", "POST",
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        "-H", f"Authorization: Bot {TOKEN}",
        "-H", "Content-Type: application/json",
        "-d", payload,
    ])
    try:
        data = json.loads(out)
        msg_id = data.get("id", "?")
        print(f"  Message sent: {msg_id}")
        return msg_id
    except Exception as e:
        print(f"  Parse error: {e} | raw: {out[:200]}")
        return "?"


def send_image(image_path: str, filename: str, caption: str = "") -> str:
    out = curl([
        "-X", "POST",
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        "-H", f"Authorization: Bot {TOKEN}",
        "-F", f"file=@{image_path};filename={filename}",
        "-F", f"payload_json={{\"content\": \"{caption}\"}}",
    ])
    try:
        data = json.loads(out)
        msg_id = data.get("id", "?")
        print(f"  Image sent: {msg_id}")
        return msg_id
    except Exception as e:
        print(f"  Parse error: {e} | raw: {out[:200]}")
        return "?"


def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: image not found at {IMAGE_PATH}")
        print("Run paint_s270_jimson_weed.py first.")
        return

    print(f"Posting session 270 to Discord channel {CHANNEL_ID}...")
    ids = []

    # Post the image first
    print("Uploading image...")
    img_id = send_image(IMAGE_PATH, FILENAME)
    ids.append(img_id)
    time.sleep(1.2)

    # Post text blocks
    for i, block in enumerate(TEXT_BLOCKS):
        print(f"Sending text block {i + 1}/{len(TEXT_BLOCKS)}...")
        msg_id = send_message(block)
        ids.append(msg_id)
        time.sleep(1.2)

    print(f"\nDone. Message IDs: {'/'.join(ids)}")


if __name__ == "__main__":
    main()
