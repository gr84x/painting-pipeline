"""Post session 257 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s257_afklint_elm_spring.png")
FILENAME   = "s257_afklint_elm_spring.png"

TEXT_BLOCKS = [
    """\
**Elm, First Light of Spring** -- Session 257

*Pale cerulean sky wash ground, Hilma af Klint Biomorphic mode -- 168th distinct mode*

**Image Description**

A single ancient elm tree fills the canvas from edge to edge, viewed from directly below and slightly to the right -- a worm's-eye perspective that makes the trunk feel massive and the sky a living presence between the branches. The trunk base anchors the lower-center of the composition, bifurcating at about one-third height into two main structural arms that reach across the upper two-thirds. Secondary branches radiate outward from these arms in natural asymmetric arcing gestures. The outermost terminal branches bear the first unfurling leaf clusters of early spring -- small, citron-yellow-green, lit from above.""",

    """\
**The Figure**

The elm is very old -- its trunk circumference suggests three or four centuries. The bark is deeply furrowed with long vertical fissures, the ridges grey-brown and slightly silvered where the light catches. At the bifurcation point there is a large pale callus where an old limb was lost decades ago. The trunk is backlit from above, so its silhouette edge catches a rim of warm amber afternoon light while its face is in soft cool blue-grey shadow. The branches thin rapidly as they radiate outward -- from wrist-thick at the first fork to twig-fine at the tips. At the branch ends, the first true leaves of the year are just emerging: tight clusters of five or six small leaves, still pleated and slightly translucent, colour somewhere between citron and yellow-green against the pale sky. The tree's emotional state is patient renewal: it has stood through many winters and does not rush its spring.

**The Environment**

The sky behind the tree is pale early-spring cerulean, lightening toward near-white directly above where the light is most intense. Near the lower frame edge the sky is warmer and slightly amber-tinted from the low sun angle. The bark texture in the foreground trunk has a rough three-dimensional quality -- ridges and fissures catching the light at different angles. In the upper corners, the small outer branch tips are slightly softer in the cool haze of the sky. The boundaries between bark and sky are sharp at the main trunk, soft and hazy at the delicate outer branches. Ground detail is not visible -- the viewer is lying on their back beneath the tree, looking straight up.""",

    """\
**Technique & Passes**

Hilma af Klint Biomorphic mode -- session 257, 168th distinct mode.

The af Klint biomorphic pass computes the luminance-weighted centroid of the composition (which falls near the trunk bifurcation -- the visual centre of gravity) and radiates concentric growth rings outward from this point. The ring count of 4.5 produces alternating warm/cool zones: inner zones (trunk, major branches) are pushed slightly warmer, outer zones (sky areas) slightly cooler, echoing af Klint's deliberate warm-inner / cool-outer colour pairing in her temple paintings. The haze boundary glow (sigma=22) creates luminosity at each ring transition, as if the tree's annual growth rings are broadcasting outward as a visible spiritual field.

Shadow Bleed improvement (session 257): Warm reflected light is injected into the shadow zone of the trunk's near face and the dark bark fissures. The reflected source field is derived from the sky and rim light areas, bouncing diffuse warm amber light back into the shadow side of the bark. The effect bleeds smoothly (bleed_sigma=10) into the deeper shadow zones, adding warmth without painting-on artificiality.

*Additional passes: Edge Temperature (s256) -- temperature contrast at bark/sky boundary; Tonal Key (s255) -- slight high-key push for spring light quality; Contour Weight (s254) -- variable-thickness bark edge contour.*""",

    """\
**Mood & Intent**

This painting is about the specific patience of trees. A tree does not experience winter as loss -- it waits. The first leaves do not appear as a celebration but as a quiet fact, like the return of something that left without ceremony. Viewed from below, the viewer is placed in the position of something small -- a child, an animal, a supplicant -- beneath a form that has been here far longer than they have and will remain after they leave.

The af Klint biomorphic pass adds to this the quality of invisible growth patterns made visible: the tree's annual rings (recorded inside the trunk, invisible from outside) are projected outward as a luminous field, as if the tree's history of growth is broadcasting into the surrounding air. Af Klint believed there were invisible forces structuring the visible world; this painting applies that belief to the most literal possible subject -- a tree whose internal rings are its complete autobiography.

*New this session: Hilma af Klint (1862--1944, Swedish Abstract / Spiritual / Proto-Abstract Expressionism) -- hilma_af_klint_biomorphic_pass (168th distinct mode). THREE-STAGE BIOMORPHIC ABSTRACTION: (1) luminance-weighted centroid as radial ring origin with sine-wave frequency ring field; (2) radial ring-distance-weighted chromatic warm/cool zone resonance; (3) gradient magnitude of ring field blurred into luminous boundary haze. Improvement: paint_shadow_bleed_pass -- shadow boundary proximity from blurred binary luminance-threshold mask; bright source proximity field; reflected warm light injection at shadow-bright proximity product zone.*""",
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
    print(f"Posting session 257 to Discord channel {CHANNEL_ID}...")

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
