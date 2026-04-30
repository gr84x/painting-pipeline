"""Post session 263 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s263_vallotton_lamp_dinner.png")
FILENAME   = "s263_vallotton_lamp_dinner.png"

TEXT_BLOCKS = [
    """\
**Dinner, by Lamplight** -- Session 263

*Near-black ground, Félix Vallotton Dark Interior Chiaroscuro mode -- 174th distinct mode*

**Image Description**

A lamp-lit dining room in a bourgeois apartment, Lausanne or Paris, circa 1899. Three figures are seated at a round table in the lower half of the canvas. The composition is organised entirely around the kerosene lamp at centre-left of the upper half: it is the only light source, and its presence commands the picture. The room is otherwise consumed by near-black -- walls, floor, ceiling, and all objects beyond lamp-reach are crushed into darkness. The table surface is a warm amber ellipse; the three figures are partially dissolved into shadow, their upper torsos and faces caught in warm-lit passages and their lower portions extinguished. A white tablecloth anchors the composition, its broad warm-cream field the largest lit mass in the picture after the lamp itself.""",

    """\
**The Figures**

Three adults at table -- two women and one man, all in late middle age. The central woman (near side, three-quarter view) is lit most fully: her face and décolletage receive a concentrated warm amber, her dark dress vanishing into the shadow below the table. She holds her hands around a cup or glass just visible at the table edge. The second woman (far side, nearly silhouetted) is reduced to a dark form with a pale upper forehead catching a residual gleam of lamp light. The man (right side, in profile) is half-turned from the viewer -- his jacket fuses with the dark wall behind him; only his shirt-front and the near side of his face are legible.

None of the three figures look at each other or at the viewer. They are suspended in the private silence of a meal nearly concluded. Vallotton's psychological distance is absolute: the viewer watches through a door-frame at people who have no awareness of being watched.

**The Environment**

The room itself is barely present. A dark brownish-green wall absorbs the right half of the canvas. An unseen door or window is implied at far left by the absolute black of that corner. The floor is dark parquet. The lamp -- a kerosene fixture with a round white globe and a dark metal collar -- sits on a short column or bracket slightly off-centre and above the table. Its light radiates outward in a quadratic falloff: concentrated amber at the table surface, fading to ochre at the figures' faces, vanishing to near-black within half a metre. The lamp globe itself is the single white-hot element in the picture, a small fierce node of illumination in an otherwise consumed room.""",

    """\
**Technique & Passes**

Vallotton Dark Interior Chiaroscuro mode -- session 263, 174th distinct mode.

The vallotton_dark_interior_pass applies three stages after the scene is built up through standard structural passes.

Stage 1 (SHADOW CRUSH): A sigmoid-steepened compression curve is applied below the shadow_crush threshold (0.38). Pixels in the lower luminance range are remapped through a sigmoid function with a steepness of 8.0, then blended back toward a near-black target colour (0.055, 0.045, 0.035) proportional to how deeply below the threshold they fall. This crushes the vast mid-shadow passages of the room to near-black -- not pure black, but the particular near-black of Vallotton's oil paint on dark-imprimatura canvas. Approximately 1.3 million pixels affected.

Stage 2 (RADIAL LAMP WARMTH POOL): A quadratic falloff warm-amber field centred on the configured lamp position (lamp_cx=0.48, lamp_cy=0.25, lamp_radius=0.28) is blended additively into the canvas at lamp_strength=0.34. The blend colour is a concentrated warm amber (0.88, 0.65, 0.20). Pixels outside the lamp radius receive no warmth. This creates the characteristic Vallotton concentrated lamp pool -- a warm ellipse on the table and lower faces -- without globally brightening the canvas. Approximately 134,000 pixels in the pool zone.

Stage 3 (JAPANESE INK CONTOUR): Sobel x/y gradient magnitude is computed on the current canvas state, Gaussian anti-aliased (sigma=0.7), normalised, and used as a multiplicative darkening weight at contour_strength=0.35. The effect is strongest at tonal boundaries -- the lamp-dark wall transition, the figure silhouette edges, the tablecloth border -- producing the hard woodcut-quality ink outline that distinguishes Vallotton from all other Nabi painters. Approximately 140,000 contour pixels darkened.

Flat Zone pass improvement (session 263): The paint_flat_zone_pass applies spatial median filtering per channel across a radius-5 neighbourhood, producing the Nabis flat-colour-zone quality. Edge zones (above Sobel threshold 0.08) are preserved through a (1 - edge_weight * preserve_edges) composite, preventing the median from smearing figure boundaries. In low-saturation areas (below 0.12 threshold), the warm ground colour (0.58, 0.52, 0.44) is revealed at a 0.10 strength, recovering Vallotton's visible warm imprimatura in the dark passages.

Full pipeline: tone_ground (near-black, 0.18/0.15/0.12) → underpainting (×2) → block_in (×2) → build_form (×2) → place_lights → paint_flat_zone_pass → vallotton_dark_interior_pass → paint_triple_zone_glaze_pass → paint_shadow_bleed_pass""",

    """\
**Mood & Intent**

The painting is an exercise in the psychology of darkness-as-content. Vallotton does not use darkness to dramatise light, in the manner of Caravaggio or de la Tour -- darkness, for Vallotton, is the natural state of the domestic interior, and light is the intrusion. The lamp does not illuminate the room; it creates a small territory of warmth against a room that was always primarily dark.

The three figures at table are both present and absent. They are present physically -- flesh, cloth, hair, hands -- but their interior lives are sealed off. Vallotton refuses interiority: these are not people in a psychological moment, they are forms in a tonal study. The viewer is excluded from whatever conversation or silence exists among them. This is voyeurism without reward: you see, but you learn nothing.

The Japanese woodcut influence is structural, not decorative. Vallotton learned from Hiroshige and Hokusai that a picture can be organised entirely by zones of flat tone with ink boundaries, without atmospheric modelling, without brushstroke evidence, without impasto. The surface is as smooth as a lacquered panel. The emotional weight comes not from texture but from tonal architecture.

*New this session: Félix Vallotton (1865-1925, Swiss-French, Nabis / Post-Impressionist) -- vallotton_dark_interior_pass (174th distinct mode). THREE-STAGE STARK INTERIOR CHIAROSCURO: (1) sigmoid-steepened shadow crush below threshold pushes near-shadow pixels to near-black imprimatura tone; (2) quadratic-falloff warm-amber blend centred on configurable lamp position builds concentrated lamp pool without global brightening; (3) Sobel + Gaussian ink contour used as multiplicative darkening to add woodcut-quality hard outline at all tonal boundaries. Improvement: paint_flat_zone_pass -- spatial median zone flattening with Sobel edge preservation composite and saturation-gated warm ground reveal for Nabis flat-colour-zone quality.*""",
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
    print(f"Posting Session 263 to Discord channel {CHANNEL_ID}...")
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
