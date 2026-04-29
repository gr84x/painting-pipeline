"""Post session 247 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s247_kollwitz_weight_of_earth.png")

FILENAME = "s247_kollwitz_weight_of_earth.png"

TEXT_BLOCKS = [
    """\
**The Weight of the Earth** — Session 247

*Warm charcoal ground, Käthe Kollwitz Charcoal Etching mode — 158th distinct mode*

**Image Description**

A lone woman crouched on bare winter earth, seen from a slightly elevated three-quarter angle from her left. Her hunched mass fills the lower-centre two-thirds of the canvas, the vast pale sky pressing down from above. A single bare branch crosses the upper-left quadrant — dark, thin, angular. The composition pulls downward. Nothing offers relief.""",

    """\
**The Figure**

She is broad and heavy-set, her dark shawl pulled tight around shoulders curved in grief. Her back is entirely toward us — Kollwitz never needed a face to communicate what she needed to communicate. Only the top of grey hair is visible beneath the shawl's edge. Her left hand is pressed flat against the cold earth: large-knuckled, wide-palmed, the fingers spread as if trying to feel what is buried beneath. The right arm curves hidden across her body, inside the shawl. The black skirt fans out around her crouching form, fabric merging into the dark earth below.

Emotional state: absolute, wordless mourning. The grief that has moved past weeping into something older and heavier — the grief of the body pressing itself toward the ground.""",

    """\
**The Environment**

Bare winter earth — cold, flat, textured with frost and dead grass stubble. Dark grey-brown, unyielding. The horizon line sits low, at one-quarter up from the bottom of the canvas, leaving the figure pressed between the heavy earth and the vast pale sky above. The sky is the colour of old paper: warm grey-white, flat, not luminous, not hopeful — the colour of a surface that has received many marks and many years. A single bare deciduous branch enters from the upper left, its thin dark silhouette an angular counterpoint to the rounded, collapsed form below. No leaves. No growth. The branch does not bend toward the figure. It is simply there, as winter is simply there.""",

    """\
**Technique & Palette**

Käthe Kollwitz (1867-1945) Charcoal Etching mode — session 247, 158th distinct painting mode.

Stage 1, WARM CHARCOAL MONOCHROME CONVERSION: Each pixel is desaturated toward a two-endpoint warm charcoal ramp. At luminance = 0: the target is warm deep-black (R=0.12, G=0.09, B=0.06) — the sepia darkness of aged charcoal on tooth paper. At luminance = 1: the target is warm cream-white (R=0.93, G=0.88, B=0.78) — the colour of an old lithographic ground. All pixels are blended from their original colour toward this ramp with weight desat_str = 0.90. The result is not cold grey monochrome — it is the specific warm near-monochrome of Kollwitz's charcoal and lithographic work, where shadows have a sepia warmth and highlights have a paper warmth. First pass to parameterise desaturation using separate dual endpoints for shadow and highlight zones, interpolated by luminance.

Stage 2, SIGMOID TONAL CONTRAST EXPANSION (k=8): After desaturation, a symmetric logistic sigmoid is applied to the luminance values. lum_new = 1 / (1 + exp(−8 × (lum − 0.5))). The steep k=8 curve pushes near-dark values toward absolute black and near-light values toward peak brightness, replicating the extreme tonal contrast of Kollwitz's mature graphic work — the depth at which her shadows fall, the brightness at which her highlights stand. Channels are scaled proportionally so hue (such as it remains) is preserved.

Stage 3, DIRECTIONAL SHADOW GRAIN at 50° and 140° (cross-hatch): A 1D kernel of length 11 is constructed at 50° by accumulating sub-pixel Gaussian weight along the parametric line direction. The dark zone of the image (luminance < 0.36) is convolved with this kernel; the high-frequency residual (original minus blurred) is added back into those shadow pixels with weight proportional to their depth in shadow. A second pass at 140° (cross-hatch direction) with a smaller kernel reinforces the grain. The result is a visible directional mark texture in dark zones — the oriented hatching characteristic of Kollwitz's charcoal and etching surfaces. First pass to construct a parametric-angle directional grain kernel and apply it exclusively to pixels below a shadow luminance threshold.

Paint Luminance Stretch improvement (session 247): Percentile-anchored luminance normalisation stretches the tonal range from [p2, p98] to the full [0, 1] scale, ensuring the paper white is fully bright and the charcoal dark is fully deep. Hue-preserving: all channels scaled by the same luminance ratio.""",

    """\
**Palette:** Warm deep-black (charcoal shadow) · Sepia brown (mid-shadow, etching tone) · Warm grey (mid-tone, stone, worn fabric) · Ochre-grey (earth, skin, aged paper) · Pale cream-white (sky, paper ground, hair rim light) · Near-black (shawl, skirt, branch silhouette)

**Mood & Intent**

This painting is built from a single emotion: the weight of earth.

Kollwitz made this image many times. The crouching woman. The pressed hand. The absent face. She was not illustrating grief — she was recording its physical form: the way grief turns the body toward the ground, the way the hands press against the earth as if trying to reach what is buried. She knew this grief personally. Her son Peter died at Diksmuide in October 1914, aged eighteen, five weeks after she completed "Kathe and Peter," a drawing of mother and son. She spent the next eighteen years working on the memorial sculptures that now kneel at Vladslo Cemetery facing his grave.

The viewer is not meant to feel sorrow. They are meant to recognise weight — to feel, in their own body, the pull that the figure is feeling. No colour interferes with this. No light offers relief. The pale sky is not hope. It is simply the emptiness above a person who has lost everything they cared for.

The bare branch in the upper left does not bend toward the figure. The earth does not yield to her hand. The painting refuses comfort. It offers only witness.

*New this session: Käthe Kollwitz (German Expressionism/Social Realism) — kollwitz_charcoal_etching_pass (158th distinct mode). WARM CHARCOAL MONOCHROME: dual-endpoint warm charcoal ramp desaturation + sigmoid tonal contrast expansion (k=8) + directional shadow grain at parametric angle. PAINT_LUMINANCE_STRETCH_PASS: percentile-anchored luminance normalisation.*

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
