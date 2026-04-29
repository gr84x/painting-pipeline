"""Post session 246 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s246_macke_marche_a_tunis.png")

FILENAME = "s246_macke_marche_a_tunis.png"

TEXT_BLOCKS = [
    """\
**Marché à Tunis** — Session 246

*Warm golden ochre ground, August Macke Luminous Planes mode — 157th distinct mode*

**Image Description**

A lone woman in a flowing white-blue djellaba viewed from behind, standing at a sunlit market stall in a narrow Tunisian souk lane at high noon. The scene compresses into pure colour: cobalt-blue shadow wall pressing in from the left; blazing warm-white wall catching full sun to the right; above, an awning of cobalt-blue and burnt-orange stripes cuts the sky into horizontal bands of pure hue. The woman is the still point around which all the colour turns.""",

    """\
**The Figure**

She stands slightly left of centre, her back entirely toward us — a compositional choice Macke uses to refuse the sentimental. We are not given her face, her expression, her interiority. We are given instead the pure silhouette of a woman in noon light: the flat near-white plane of her djellaba catching the Tunisian sun on its back surface so completely it reads as almost achromatic white. On her left side, where the shadow falls, the fabric shifts to a flat cobalt blue — a completely distinct, equally saturated colour, not a darkened version of the white, placed in direct adjacency. Her dark hair shows beneath a terracotta headscarf. She cradles a large terracotta water jar against her right hip, the jar a deep rounded mass of warm burnt sienna, its rim in deep violet shadow. Her right arm extends to carry it, exposing warm ochre skin at the wrist. Her emotional state: absorbed, unhurried, entirely present to the market — her attention elsewhere and therefore fully herself.""",

    """\
**The Environment**

The lane is narrow, the walls pressing close. The left wall exists only as cobalt-blue shadow — no architecture, no detail, just flat chromatic zone. The right wall blazes ivory-warm. Between them the golden sand floor runs to a stone arch at the far end of the lane, through which desert light bleeds in as near-white luminosity — the arch is a brightness, a portal, not a structure.

Above: the awning hangs in alternating cobalt-blue and burnt-orange stripes, and below it, from hooks and cords, hang bolts of vermilion fabric, acid-yellow-green silk, and shorter lengths of deep orange cloth. The vertical cascade of hanging goods — red, green, orange against the warm wall — is the painting's richest chromatic moment, where Macke's colour syntax operates at full pitch: pure hue next to pure hue, boundaries bright rather than dark.

To the right foreground, a market table holds terracotta jars, a copper bowl whose concave interior catches cadmium-yellow reflected light, and folded cloth in deep violet and burnt orange. The sand floor in the extreme foreground is flat warm gold, interrupted by the crisp shadow stripes the awning casts across it.""",

    """\
**Technique & Palette**

August Macke (1887-1914) Luminous Planes mode — session 246, 157th distinct painting mode.

Stage 1, HUE-ZONE SATURATION NORMALISATION: The hue wheel is divided into 8 equal sectors (45° each). For each sector, the 80th-percentile saturation of pixels in that sector is measured. If that percentile falls below sat_target (0.84), a per-sector scale factor is computed as sat_target / p80, clamped to [1, 2.5]. All pixels in the sector have their saturation lifted: s_new = clip(s × (1 + (scale − 1) × sat_lift_str), 0, 1). The effect is that colour zones which have lost saturation through the stroke passes are independently restored, sector by sector, to Macke's characteristic chromatic intensity. First pass to apply per-hue-sector percentile-referenced saturation normalisation; no prior pass uses zone-local percentile statistics as the lift reference.

Stage 2, CIRCULAR HUE GRADIENT BOUNDARY BRIGHTENING: The hue angle is decomposed into sin(hue) and cos(hue). Sobel gradient operators are applied to both components. The combined circular gradient magnitude identifies boundaries between colour planes — specifically boundaries defined by large hue change rather than luminance change. Pixels at high hue-jump boundaries receive a brightness increase (value += boundary_map × 0.22). The colour-plane boundary glows. This is the stained-glass phenomenon: the interface between two saturated colour fields appears to emit light. First pass to detect boundaries via circular hue gradient (not luminance gradient) and to brighten (not darken) at those interfaces.

Stage 3, LUMINANCE-PROPORTIONAL WARM GOLDEN VEIL: Each pixel is blended toward a warm golden colour (R=0.96, G=0.82, B=0.40) with a weight proportional to existing luminance: weight = luminance × 0.18. Brighter pixels absorb more of the warm veil; shadow zones absorb almost none. This simulates the effect of Macke's warm golden-tan ground showing through the paint layer in lit zones, unifying the palette with a common warm undertone. First pass to scale a warm-colour blend by current pixel luminance.

Paint Golden Ground improvement (session 246): Three-stage value-zone ground echo. Stage 1 MIDTONE GROUND ECHO: midtone proximity = max(0, 1 − 2|lum − 0.5|) drives a blend toward warm ochre ground colour — pixels nearest 50% luminance are pulled most strongly toward the ground tone; first pass to use midtone proximity as blend weight. Stage 2 SHADOW WARMTH ANCHOR: shadow pixels (lum < 0.30) are additionally blended toward a deeper, richer burnt-umber ground tone — first pass to apply a second, distinct darker ground blend specifically in the shadow zone. Stage 3 GOLDEN HIGHLIGHT KISS: highlight pixels (lum > 0.78) receive a subtle warm near-white golden tint — first pass to apply a third, distinct golden tint in the highlight zone separately from mid-tone and shadow handling.""",

    """\
**Palette:** Cadmium yellow (noon sun, sand) · Cobalt blue (shadow wall, djellaba shadow) · Vermilion-orange (hanging fabric, awning) · Cerulean (sky arch glow) · Warm ivory-white (sunlit wall, djellaba lit face) · Terracotta-burnt sienna (architecture, water jar) · Acid yellow-green (market silk) · Deep violet (doorway depth, pot rims)

**Mood & Intent**

This painting is made in the key of joy. Not the mild pleasantness of a park scene, but the specific, almost unbearable chromatic joy of Macke's Tunisian works — the joy of someone who has found, in the colours of North Africa under direct noon sun, exactly the visual language he had been searching for, and who has perhaps three months left to live.

April 1914: Macke travels to Tunisia for two weeks with Paul Klee and Louis Moilliet. They paint furiously in Tunis, Saint-Germain, Hammamet, Kairouan. The watercolours they produce are among the most purely joyful images in German art. In September, five months later, Macke is killed at the Battle of Perthes-lès-Hurlus, aged twenty-seven.

The woman's turned back refuses sentiment. The cobalt shadow wall and blazing white wall refuse chiaroscuro. The vermilion fabric and acid-green silk against the terracotta architecture refuse muted colour. The glowing arch at the end of the lane refuses enclosure. What remains is the thing itself: noon light, colour, a market, a woman, a jar. Pure chromatic declaration. Paint with patience and practice, like a true artist.

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

# POSTED MESSAGE IDS: 1499062066626170991/1499062072598728814/1499062078479138817/1499062084837576956/1499062090940551231/1499062097344987206/1499062104836276325
