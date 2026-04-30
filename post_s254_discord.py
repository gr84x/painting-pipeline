"""Post session 254 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s254_rego_kitchen_woman.png")
FILENAME   = "s254_rego_kitchen_woman.png"

TEXT_BLOCKS = [
    """\
**Woman at Kitchen Table** -- Session 254

*Warm earthy ground, Paula Rego Flat Figure mode -- 165th distinct mode*

**Image Description**

A stout woman seated squarely at a kitchen table, viewed from a slightly elevated angle as if the viewer stands while she is seated. She faces directly forward, head tilted slightly right, filling the lower two-thirds of the canvas. A large amber-eyed tabby cat sits on the table to her left -- both pairs of eyes, human and animal, look directly at the viewer. The composition is frontal, claustrophobic, pressing the figure against the picture plane. A white ceramic cup rests on the table between her hands. At the right edge of the canvas: an empty chair back, just visible.""",

    """\
**The Figure**

The woman is broad-shouldered, heavy-handed, in her fifties. She wears a dark green dress with a white collar. Her hands rest flat on the table -- right hand open, relaxed; left hand closed in a loose fist. Her face is broad, with high cheekbones and a set jaw; her expression is neither hostile nor welcoming -- it is watchful, deliberate, the face of someone who has absorbed the weight of many things and released none of them. Dark hair pulled back. Emotional state: contained power, patience worn to its exact edge, quiet authority. Not angry. Not sad. Fully present, waiting.

The cat is large, solidly built, with a round face and pale-gold eyes. It sits in the classic loaf position, paws tucked, tail curled. Its fur is warm ochre-brown with darker tabby stripes. Emotional state: total self-possession -- indifference and alertness simultaneously, as animals in Rego's paintings always are.

**The Environment**

The kitchen is stark and close. A flat dark-green painted wall fills the upper half of the canvas. A single high window at upper right admits cold grey exterior light that does not warm the room. The table surface is plain pale wood -- scrubbed, dry, slightly worn. No decorative objects. No softening. The space is real, ordinary, without romance. The boundary between wall and table is hard-edged, unblended -- flat planes described with the directness of a woodcut.""",

    """\
**Technique & Palette**

Paula Rego (1935--2022, Lisbon / London) Flat Figure mode -- session 254, 165th distinct painting mode. Figurative / Neo-Expressionism.

Stage 1, TONAL ZONE POSTERISATION: n_levels=7, zone_blend=0.68. Colours reduced to flat zones in the manner of Rego's pastel work -- large areas of a single unmodulated tone. zone_blend=0.68 preserves the organic warmth of hand-mixed pastel zones without digital harshness. NOVEL: FIRST PASS to combine per-channel uniform quantisation (round to n_levels) with per-zone local mean-colour blending as a two-step figurative colour flattening; distinct from global tone operations; no prior pass performs quantised zone identification followed by zone-mean colour replacement weighted by zone_blend.

Stage 2, WARM CONTOUR OUTLINING: contour_threshold=0.06, contour_strength=0.62, contour_px=2, outline_tone=(0.14, 0.09, 0.06). Finite-difference gradient edges dilated 2 pixels and blended toward a warm dark outline tone -- giving figures their characteristic heavy, slightly warm boundary. contour_pixels=350,203. NOVEL: FIRST PASS to apply warm-toned dark blending specifically at dilated gradient-edge pixels as a figurative contour simulation; no prior artist pass applies a warm-shifted dark tone to dilated edge pixels for contour darkening.

Stage 3, CHROMATIC ZONE TENSION: tension_warm=(0.68, 0.48, 0.28), tension_cool=(0.36, 0.46, 0.58), tension_strength=0.10. Canvas divided into 2x2 spatial grid: upper-right and lower-left (figure zones) pushed slightly warmer; upper-left and lower-right (ground zones) pushed slightly cooler. NOVEL: FIRST PASS to apply alternating warm/cool chromatic pushes indexed by spatial quadrant position as a figurative composition technique.""",

    """\
**Contour Weight improvement (session 254):** contour_threshold=0.05, max_weight=0.50, weight_exponent=1.2, junction_boost=0.18, taper_strength=0.32. edge_pixels=236,851; junction_pixels=106,565.

THREE-STAGE VARIABLE-WEIGHT CONTOUR: (1) GRADIENT FIELD WITH DIRECTION MAP -- computes both magnitude AND direction of luminance gradient simultaneously, retaining both for junction detection and taper computation; NOVEL: first pass to retain gradient direction for use in variable contour weighting. (2) JUNCTION DETECTION via local angular variance of gradient direction in 3x3 window -- high variance = corner/junction; junction_boost applied additively to contour weight; NOVEL: first pass to use angular variance of gradient direction as a corner detector for modulating contour darkness. (3) POWER-LAW CONTOUR WEIGHT with neighbour-count taper -- final_weight = edge_weight^1.2 * 0.50; endpoint pixels (fewer than 2 edge neighbours in 3x3 window) receive weight * (1 - 0.32) to taper stroke ends; NOVEL: first pass to combine power-law contour weight with endpoint taper suppression for variable-thickness figurative contour simulation.

**Palette:** Wall dark green (0.22/0.38/0.22) -- Dress shadow (0.20/0.26/0.20) -- Dress mid (0.28/0.40/0.28) -- Flesh warm (0.74/0.54/0.40) -- Flesh shadow (0.52/0.34/0.24) -- Cat ochre (0.76/0.60/0.32) -- Cat stripe (0.40/0.30/0.18) -- Table pale (0.82/0.76/0.62) -- Cup white (0.90/0.88/0.84) -- Window cool (0.60/0.66/0.74) -- Deep shadow (0.18/0.14/0.12)""",

    """\
**Mood & Intent**

This is a painting in Rego's mode of domestic confrontation: the kitchen as a space of female power, endurance, and ambiguity. The woman is not threatening but she is not subordinate either. She has sat at this table a thousand times and will sit here a thousand more. The cat beside her doubles her quality of watchful self-possession -- in Rego, animals and humans share the same ontological weight, equally present, equally watchful.

The viewer feels observed, measured, found neither sufficient nor insufficient -- simply noted. The cold grey light from the window suggests a morning before warmth arrives, before the day's demands. The empty chair at the right edge suggests recent absence or anticipated arrival, but offers no narrative comfort. The painting is still. It does not explain itself. That is its authority.

*New this session: Paula Rego (1935--2022, Portuguese-British Figurative) -- rego_flat_figure_pass (165th distinct mode). THREE-STAGE FLAT FIGURE: tonal zone posterisation with zone-mean smoothing + warm contour outlining with edge dilation + quadrant-indexed warm/cool chromatic tension. Improvement: paint_contour_weight_pass -- angular-variance junction detection, power-law weight scaling, neighbour-count endpoint taper.*""",
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
            "-F", 'payload_json={"attachments": [{"id": 0}]}',
        ],
        capture_output=True, text=True
    )
    resp = json.loads(result.stdout)
    msg_id = resp.get("id", f"ERROR: {resp}")
    print(f"Image message ID: {msg_id}")
    return msg_id


if __name__ == "__main__":
    print(f"Posting session 254 to Discord channel {CHANNEL_ID}...")

    ids = []
    for i, block in enumerate(TEXT_BLOCKS):
        print(f"  Posting text block {i+1}/{len(TEXT_BLOCKS)}...")
        mid = post_text(block)
        ids.append(mid)
        time.sleep(1.2)

    print(f"  Posting image {IMAGE_PATH}...")
    img_id = post_image(IMAGE_PATH, FILENAME)
    ids.append(img_id)

    print(f"\nAll message IDs: {ids}")
    print("Done.")
