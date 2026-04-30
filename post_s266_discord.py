"""Post session 266 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s266_birch_forest.png")
FILENAME   = "s266_birch_forest.png"

TEXT_BLOCKS = [
    """\
**Birch Forest at Dusk, Lake Ruovesi** -- Session 266

*Dark umber ground, Akseli Gallen-Kallela Enamel Cloisonne mode -- 177th distinct mode*

**Subject & Composition**

A Finnish birch forest stands in late October at the edge of Lake Ruovesi in Häme, Finland -- the same lake at whose shores Gallen-Kallela built his studio Kalela in 1895. Six birch trunks of varying heights occupy the lower two-thirds of the canvas as vertical white sentinels, evenly distributed across the width. The viewer stands at the lake's edge, looking into the forest interior; the lake is a narrow band of dark water in the middle distance, visible between and beneath the birch crowns. Above the treeline: a Finnish dusk sky -- deep cobalt at the zenith, graduating through raw ultramarine to a band of brilliant burnt orange above the horizon. The composition is landscape-oriented, emphasising the horizontal spread of the Finnish forest and the long flat horizon of Finnish lake country.""",

    """\
**The Subjects**

No human figure. The six birch trunks are the compositional figures -- tall, vertical, each one a distinct white form against the dark forest interior. The trees vary: the leftmost is the tallest and most massive, its base flaring slightly at the ground; two thinner saplings cluster near the left-centre; the central dominant trunk rises toward the top edge; two further birches frame the right half. Each trunk carries the characteristic dark oval node markings of Betula pendula -- small horizontal black lenticels scattered at irregular intervals up the white bark. The emotional state of the subject is ancient and indifferent: these trees predate memory, have stood through a hundred Finnish winters, and will stand through a hundred more. Their stillness is total.

**The Environment**

The Finnish forest interior at dusk: between the birch trunks lies a zone of deep shadow -- the spruce and pine understorey, almost impenetrable to the eye, painted as a flat deep forest-green / dark umber field. The forest floor is covered in leaf litter: fallen birch leaves in brilliant burnt ochre, golden yellow, and warm russet, gathered at the base of each trunk. The narrow lake band gleams in the middle distance -- deep blue-black, nearly opaque, with a single horizontal streak of reflected burnt orange from the dusk sky. Temperature: below freezing tonight for the first time this year. The air is absolutely still.""",

    """\
**Technique & Passes**

Akseli Gallen-Kallela Enamel Cloisonne mode -- session 266, 177th distinct mode.

Stage 1 (CIRCULAR-HUE ZONE FLATTENING, flat_sigma=5.0, zone_blend=0.60): Gaussian-weighted circular mean of hue (sin/cos encoding of hue angle with saturation weighting) resolves subtle within-zone hue variation into unified flat colour areas -- the birch trunks become pure cream-white, the sky cobalt becomes a single assertive hue. The Japanese woodblock flatness Gallen-Kallela absorbed in Paris, applied to the Finnish forest subject.

Stage 2 (BOLD CONTOUR DARKENING, contour_strength=0.75, contour_sigma=0.8): Sobel edge magnitude computed from the hue-FLATTENED canvas (not the original painted surface) detects boundaries between unified colour zones. Darkening at 0.75 produces bold partition-line outlines in the tradition of Gallen-Kallela's "Symposium" -- architectural, assertive contours rather than soft atmospheric edges.

Stage 3 (DECORATIVE PALETTE SATURATION PUNCH, sat_boost=0.25): Saturation-gated per-pixel chroma amplification from luminance pushes the cobalt sky toward pure lapis, the burnt orange leaves toward vivid crimson-ochre, and the forest green toward a deep jewel-tone. The result reads as landscape decoration rather than landscape painting -- the view through a Finnish stained-glass window.""",

    """\
**Technique (continued)**

Pipeline improvement s266 (HUE ZONE BOUNDARY): `paint_hue_zone_boundary_pass` is the first improvement to use CIRCULAR HUE STATISTICS for boundary detection. Prior boundary methods use luminance-based Sobel, which misses equal-luminance colour boundaries (e.g., blue-to-orange transition at same brightness). This pass computes circular variance of the hue angle (sin/cos encoding with saturation weighting, sigma=3.5): circular coherence R = |mean of saturation-weighted unit hue vectors|; hue_var = 1 - R. High variance = zone boundary; low variance = zone interior. Boundary darkening (boundary_dark=0.60) creates the cloison partition line. Interior chroma amplification (interior_chroma=0.20) enriches zone colours. Key: 69,021 boundary pixels found vs 1,441,240 interior pixels enriched.

Full pipeline: tone_ground (dark umber 0.20/0.14/0.08) → underpainting (×2) → block_in (×2) → build_form (×2) → place_lights (×2) → paint_hue_zone_boundary_pass → gallen_kallela_enamel_cloisonne_pass → paint_flat_zone_pass → paint_atmospheric_recession_pass → paint_granulation_pass""",

    """\
**Mood & Intent**

The painting aims for the quality Gallen-Kallela described as "Finnish gravitas" -- the particular weight of the Finnish forest landscape, its resistance to sentimentality, its refusal to be merely picturesque. The birch trees are not charming; they are ancient and vertical. The dusk sky is not romantic; it is a fact of the October latitude. The lake does not beckon; it reflects, and what it reflects is the fire of the dying day.

The viewer should leave with the sense of having looked through a window -- not into a painted fiction but into a real category of place: the Finnish lakeside forest at the end of October, which is neither tragic nor beautiful in the ordinary sense, but simply true.

*New this session: Akseli Gallen-Kallela (1865-1931, Finnish, National Romanticism / Symbolism) -- gallen_kallela_enamel_cloisonne_pass (177th distinct mode). THREE-STAGE ENAMEL CLOISONNE: (1) circular-hue zone flattening via Gaussian-weighted sin/cos hue average; (2) Sobel contour darkening on the flattened canvas (not original); (3) saturation-gated chroma amplification. Improvement: paint_hue_zone_boundary_pass -- first improvement using circular hue variance (not luminance Sobel) to detect colour zone boundaries and apply boundary darkening + interior chroma enrichment.*""",
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
    print(f"Posting Session 266 to Discord channel {CHANNEL_ID}...")
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
