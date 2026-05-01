"""Post session 280 Discord painting to #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s280_discord_flamenca.png")
FILENAME   = "s280_discord_flamenca.png"

TEXT_BLOCKS = [
    """\
**La Vuelta — The Flamenco Dancer at the Peak of Her Turn** — Session 280

*Oil on linen · Nicolai Fechin mode — 191st distinct mode · Fechin Gestural Impasto + Lost-and-Found Edges*

**Subject & Composition**

A Spanish flamenco dancer at the exact peak of a rapid vuelta (turn), viewed from a low three-quarter angle looking slightly upward. She fills the portrait canvas (1040 × 1440) from knee-height to the upper edge, spinning clockwise so we see primarily her left side and the beginning of her face turning back toward us in profile. Arms in arabesque: the left arm curved above her head reaching toward the upper right, the right arm sweeping out below at mid-height, gathering the dress hem. Her deep crimson dress billows in a wide arc behind her — a comet-tail of spinning silk, frozen at the moment of maximum extension.""",

    """\
**The Figure**

A woman in her early 50s: powerful, precise, absolute. Dark auburn hair pulled tightly into a bun, with a few wisps escaping at the temples. Brown skin glistening with the heat of exertion. Her spine is straight as a column; her bearing is architectural. A fitted black silk bodice with red embroidery at the collar. The deep crimson skirt with black ruffle has become a revolving plane of fabric — a kinetic object in its own right. Her left hand is open, fingers extended and slightly curved in the classic flamenco *mano*. Expression: contained, fierce, inward. The audience does not exist for her. She has disappeared entirely into the music and the movement.""",

    """\
**The Environment**

A small stone-vaulted *tablao* in Seville. The ceiling is a dark barrel vault of rough whitewashed brick, lit from below by thick beeswax candles in iron wall-holders. The walls are warm amber-plaster in the candle zones, cooling to shadow-gray at the vault. The floor: deep-worn chestnut floorboards that catch faint candle-gold. In the far background center, barely discernible in the darkness: the silhouette of a seated guitarist, head bowed over the instrument. Foreground: the dancer's shadow sprawls dramatically across the warm boards, longer than she is tall — a second dancer made of darkness.""",

    """\
**Technique & Palette — Nicolai Fechin (1881–1955)**

Fechin's three-way tension: (1) tight Repin-academic rendering at the face and hands; (2) loose, slashing gestural impasto in the dress and background; (3) palette knife scraping on the brightest crimson folds — horizontal bright streaks where the knife has dragged across the wet impasto, exposing the warm sienna ground beneath.

The new *fechin_gestural_impasto_pass* (191st distinct mode) applies a sinusoidal velocity field to create spatially varying directional brushwork energy, then scrapes the highlights with an anisotropic horizontal mean filter. Repin's academic sharpening is applied as a focal-proximity USM — tightest at the face, loosening toward the periphery. Warm raw sienna reinforces the midtones via a Gaussian-bell zone (not a threshold) peaking at L=0.42.

The new *paint_lost_found_edges_pass* (s280 improvement) simultaneously sharpens the found edges near the focal face and softens the lost edges in the peripheral background — the dress tail dissolves into atmosphere while the face contours sharpen.

Palette: deep crimson · near-black silk · amber candle-gold · burnt sienna ground · Payne gray-blue vault · raw sienna earth midtone""",

    """\
**Mood & Intent**

Contained passion. The paradox at the heart of flamenco: absolute emotional intensity made visible through absolute technical precision. The painting should communicate heat, weight, sound — and privacy. The viewer should feel the candle-heat on their face, hear the heels on the chestnut boards, and understand that they are witnessing something not meant to be witnessed: a private communion between a human being and their art.

Fechin painted the Taos Pueblo people with exactly this quality of attention — the belief that if you look long enough, and carefully enough, with full respect for what you are seeing, the canvas becomes an act of witness rather than representation. La Vuelta is that act of witness.

**Full Pipeline:** `tone_ground` (warm umber) → `underpainting` (×2) → `block_in` (×2) → `build_form` (×2) → `place_lights` → `fechin_gestural_impasto_pass` → `paint_lost_found_edges_pass` → `paint_surface_grain_pass`

*New this session: Nicolai Fechin (1881–1955, Russian-American, Taos School) — fechin_gestural_impasto_pass (191st distinct mode). FOUR-STAGE GESTURAL IMPASTO SYSTEM: (1) sinusoidal velocity field anisotropy — first pass to generate autonomous flow field from superposed sinusoids for directional brushwork; (2) palette knife scrape simulation via luminance-gated horizontal uniform filter; (3) Repin focal sharpening via distance-power USM; (4) Gaussian-bell midtone sienna reinforcement — first pass to use Gaussian bell for zone selection. Improvement: paint_lost_found_edges_pass — simultaneous found-edge USM sharpening + lost-edge peripheral softening, first pass to implement the painter's lost-and-found edge doctrine as a dual-threshold, focal-distance-weighted system.*""",
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
    print(f"Posting s280 Discord painting to channel {CHANNEL_ID}...")
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
