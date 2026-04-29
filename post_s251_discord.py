"""Post session 251 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s251_bacon_bull.png")
FILENAME   = "s251_bacon_bull.png"

TEXT_BLOCKS = [
    """\
**Bull at Rest** -- Session 251

*Warm linen ground, Francis Bacon Isolated Figure mode -- 162nd distinct mode*

**Image Description**

A bull viewed from below and to the left -- nearly head-on -- standing in absolute stillness at the centre of the canvas. The animal fills two-thirds of the canvas height. Its massive head is lowered, the broad muzzle pressing slightly forward as if scenting the air. The horns sweep outward at the same level as the top of the frame. The composition is axially symmetrical with a slight lean to the animal's left shoulder.

The bull's hide is a deep warm umber-ochre with thick flesh tones -- not a naturalistic hide, but the memory of a hide, smeared and pulled. The musculature of the neck and shoulder carries directional strokes running upper-left to lower-right, as if the painter had dragged a rag across the half-wet paint. The eye -- just one visible, at the left edge -- is a single dark globe with the quality of absolute impassivity. Emotional state: contained power, absolute patience, the vacancy of pure physical existence. The body is both specific and generic -- Bacon's intended flesh, not illustration.""",

    """\
**The Environment**

Raw cadmium orange flat field surrounds the figure, entirely flat and unarticulated -- no horizon, no room, no floor, no shadow -- just the intense ground pushing the figure outward into visibility. A faint elliptical boundary separates figure from ground, barely visible as a slight darkening at the edge of the flesh zone. The background is uniform and presses forward.

**Technique & Palette**

Francis Bacon (1909-1992) Isolated Figure mode -- session 251, 162nd distinct painting mode.

Stage 1, ELLIPTICAL ISOLATION VIGNETTE: Ellipse (rx=0.36, ry=0.45) concentrates visual energy on the figure. Exterior darkened by exterior_strength=0.65 toward near-black, with smooth cosine transition band width=0.09. Separates figure from the flat orange void with the spatial precision Bacon called an armature. NOVEL: FIRST PASS to use a configurable elliptical (not circular, not corner-based) spatial zone as primary spatial structure; vignette_pass uses corner-based quartic falloff; chroma_focus uses circular radial field for saturation -- no prior pass uses an explicit ellipse with configurable aspect ratio (rx != ry) as primary spatial mask.""",

    """\
Stage 2, DIRECTIONAL LINEAR SMEAR: smear_angle=42 degrees (upper-left to lower-right, along the shoulder slope), smear_length=16 pixels. Smear weight sw weighted by mid_luminance=0.46, smear_bandwidth=0.30: strongest in warm flesh mid-tones, weakest at highlights and near-blacks. The smeared pixels record the directional rag-scrub of Bacon working across wet paint in the hide passages. smear_opacity=0.72. NOVEL: FIRST PASS to apply a discrete linear motion-blur kernel (not Gaussian) as primary figure-zone treatment; prior blur passes (wet-bleed s250: Gaussian saturation-gated; edge-softness: Gaussian radial; guided filter: structure-guided) are all isotropic Gaussian forms; this pass uses a directional pixel-averaging line-kernel that simulates the directionality of Bacon's rag-scrub technique.

Stage 3, FLAT BACKGROUND TONE FIELD: flat_hue=0.08 (cadmium orange), flat_sat=0.80, exterior_blend=0.70. Converts exterior zone to a unified cadmium orange field -- the raw ground Bacon rolled with a house-painter's brush to achieve absolute colour uniformity. NOVEL: FIRST PASS to apply coordinated hue target + saturation target blending in the exterior isolation zone.""",

    """\
**Palette:** Warm ochre-umber (0.84/0.44/0.18) -- Raw sienna (0.62/0.28/0.08) -- Deep burnt umber (0.28/0.14/0.06) -- Cadmium orange ground (0.88/0.42/0.10) -- Near-black (0.08/0.06/0.04) -- Pale highlight (0.90/0.86/0.72) -- Cool grey (0.48/0.46/0.52)

Paint Warm-Cool Separation improvement (session 251): warm_boost=0.26 lifts warm ochre and sienna passages. cool_boost=0.22 deepens cool grey shadows. warm_lum_shift=0.03 follows Delacroix perceptual rule (warm=lighter), cool_lum_shift=0.025 (cool=heavier). NOVEL: (a) DUAL HUE-ZONE WARM-COOL CLASSIFICATION -- first improvement pass to build separate warm-zone and cool-zone cosine proximity weight maps modulated by saturation; (b) DUAL INDEPENDENT TEMPERATURE-ZONE SATURATION AMPLIFICATION; (c) TEMPERATURE-DEPENDENT LUMINOSITY ADJUSTMENT -- first improvement pass to adjust luminosity by warm/cool hue classification.""",

    """\
**Mood & Intent**

Francis Bacon said: "I want to record a person, but at the same time I want to make a kind of ghost of them." This painting intends the quality he called "the brutality of fact" -- not a symbolic bull, not a metaphorical bull, but the specific weight and presence of flesh. The cadmium orange void presses the figure out of any narrative context. The directional smear through the hide dissolves the animal into paint at the same moment it constitutes it. The elliptical isolation frame is the armature that holds the dissolution in place.

The viewer should feel something about the animal not as creature but as matter: the sensation of confronting a mass of living tissue with no mediation of sentiment or narrative. A weight. A fact. A temporary arrangement of flesh.

*New this session: Francis Bacon (Figurative Expressionism, Irish-British, 1909-1992) -- bacon_isolated_figure_pass (162nd distinct mode). ELLIPTICAL ISOLATION VIGNETTE: configurable ellipse with exterior darkening + DIRECTIONAL LINEAR SMEAR: discrete line-kernel motion blur weighted by mid-tone luminance + FLAT BACKGROUND TONE FIELD: hue/sat field unification in exterior zone. PAINT_WARM_COOL_SEPARATION_PASS: dual hue-zone classification + independent warm/cool saturation push + temperature-dependent luminosity adjustment.*

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
    time.sleep(0.5)

    print(f"\nAll message IDs: {all_msg_ids}")