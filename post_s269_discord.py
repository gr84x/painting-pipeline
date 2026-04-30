"""Post session 269 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s269_garden_sochi.png")
FILENAME   = "s269_garden_sochi.png"

TEXT_BLOCKS = [
    """\
**Garden at Sochi, Dusk** -- Session 269

*Warm cream-ochre ground, Arshile Gorky Biomorphic Abstraction mode -- 180th distinct mode*

**Subject & Composition**

A garden landscape at dusk, viewed from an oblique elevated angle -- a wide composition (1440 × 1040) inspired by Arshile Gorky's Garden in Sochi series (c.1940-41), his paintings derived from memories of his father's garden in the Van province of historic Armenia. The composition is divided into three biomorphic zones: a warm amber-gold sky occupying the upper half, deep viridian plant masses anchoring the lower-left and right, and a luminous ochre mid-ground where the late afternoon sun falls on the earth between masses. Scattered crimson and rose accent shapes -- abstracted poppy and flower memories -- pulse through the middle plane. No horizon is named. The forms are organic, rounded, and irregular, with boundaries that shift between hard contour and soft bleed.""",

    """\
**The Subject**

The subject is not a scene but a memory of abundant organic life: the feel of a Mediterranean garden in late afternoon heat, the weight of dark viridian vegetation against warm ochre earth, the flicker of red flower colour against green and gold. Three primary biomorphic masses dominate: a dense dark viridian form (lower-left) -- trees, hedgerow, old stone under root -- its interior deep and cool, its boundary luminous where the afternoon sun catches the leaf edges; a warm earth form in sienna and umber (center-lower), from which accent shapes emerge; and a lighter, more atmospheric mass (right) -- dappled, partly dissolved in the warm light.

The mood is warm, unhurried, and melancholic -- the garden holds the memory of childhood summer. No human presence, but the feeling of a place made by human hands over generations.

**The Environment**

Upper sky zone (top 45%): warm amber-gold fading toward pale luminous cream at the zenith. Mid-ground (40-65%): the richly painted zone -- warm ochre earth cut through by crimson/burgundy accent shapes (abstracted poppies). Deep lower zone (below 75%): dark earth, umber-to-sienna, where vegetation meets ground. The warm cream ground shows through every layer, giving the painting its luminous, breathing quality.""",

    """\
**Technique & Passes**

Gorky Biomorphic Abstraction mode -- session 269, 180th distinct mode.

`gorky_biomorphic_fluid_pass` -- FOUR-STAGE BIOMORPHIC OIL TECHNIQUE inspired by Arshile Gorky (1904-1948):

Stage 1 (SATURATION MAP AND FORM ZONE DETECTION): Compute per-pixel HSV saturation, smooth to get local saturation mean. Identify HIGH SATURATION ZONES (biomorphic forms: sat > mean × 1.10) and LOW SATURATION ZONES (air/ground: sat < mean × 0.70). First pass to use saturation DEVIATION from the local neighbourhood mean as a form detection signal -- sensitive to colour richness independent of lightness, detecting Gorky's characteristic richly-coloured forms against a pale, desaturated ground.

Stage 2 (FLUID WASH IN FORM ZONES): In high-saturation zones, enrich colour by pulling each channel away from local luminance: wash_R = R + (R - L) × wash_strength. Analogous to a transparent oil glaze -- deepens and enriches hue without changing its character. Confined to detected form zones only, preserving the pale luminous quality of ground zones.

Stage 3 (ORGANIC CONTOUR SYNTHESIS): Compute Sobel luminance gradient magnitude. Overlay dark umber contour lines (0.12/0.08/0.06) at detected gradient boundaries at contour_opacity. First pass to introduce a DRAWN CONTOUR LINE quality in a specific pigment colour at luminance gradient edges -- modelling Gorky's practice of combining oil paint and drawn contour in a single layer.""",

    """\
**Technique (continued)**

Stage 4 (WARM GROUND RE-EXPOSURE AND PAINT BLEED): In low-saturation ground zones, apply a small lift toward warm cream (0.92/0.82/0.62), simulating the luminous ground showing through thin paint. Then apply a bleed effect at contour boundaries via small Gaussian blur at low opacity -- simulating the slight bleed of thinned oil paint along the canvas grain at form/ground boundaries. Novel combination: warm-ground re-exposure (canvas luminosity showing through) + directional bleed at saturation boundaries.

Session improvement s269 (CHROMATIC VIBRATION): `paint_chromatic_vibration_pass` -- SIMULTANEOUS CONTRAST VIBRATION based on Chevreul's law (1839). Compute warm-cool temperature T = R - B per pixel. Find local mean temperature T_mean via Gaussian blur. Where |T - T_mean| > threshold (warm-cool boundary zones), push each pixel further from its neighbourhood mean: warm pixels get more R, cool pixels get more B. Also boost saturation in boundary zones. First pass to compute LOCAL COLOUR TEMPERATURE DEVIATION from neighbourhood mean and amplify it -- creating optical vibration at warm-cool boundaries without global colour adjustment.

Full pipeline: tone_ground (warm cream-ochre 0.92/0.88/0.76) → underpainting (×2) → block_in (×2) → build_form (×2) → place_lights → paint_chromatic_vibration_pass → gorky_biomorphic_fluid_pass → paint_shadow_bleed_pass → paint_granulation_pass""",

    """\
**Mood & Intent**

The image is intended to convey WARM ORGANIC ABUNDANCE and the melancholy sweetness of the remembered garden -- a place that no longer exists except in memory and paint. The biomorphic forms feel alive with organic energy while remaining fully abstract: the viewer senses plant, earth, light, and flower without being able to name any specific thing. The crimson accents pulse against the viridian masses like remembered flashes of colour. The warm cream ground shows through every layer, giving the painting its luminous, breathing quality.

The viewer should feel the weight of summer afternoon light -- unhurried, golden, and already tinged with the melancholy of impermanence. This is the feeling of Gorky's Garden in Sochi: a paradise of memory, painted with total technical control and total emotional freedom.

*New this session: Arshile Gorky (1904-1948, Armenian-American, Biomorphic Abstraction) -- gorky_biomorphic_fluid_pass (180th distinct mode). FOUR-STAGE BIOMORPHIC OIL: (1) saturation-relative form zone detection; (2) luminance-relative colour enrichment in form zones; (3) Sobel-gradient organic contour overlay in dark umber; (4) warm ground re-exposure + paint bleed at boundaries. Improvement: paint_chromatic_vibration_pass -- simultaneous contrast vibration via local colour temperature deviation amplification.*""",
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
    print(f"Text message ID: {msg_id}")
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
    print(f"Image message ID: {msg_id}")
    return msg_id


def main():
    print(f"Posting Session 269 to Discord channel {CHANNEL_ID}...")
    ids = []
    for block in TEXT_BLOCKS:
        mid = post_text(block)
        ids.append(mid)
        time.sleep(0.8)
    img_id = post_image(IMAGE_PATH, FILENAME)
    ids.append(img_id)
    print(f"Done. Message IDs: {ids}")
    return ids


if __name__ == "__main__":
    main()
