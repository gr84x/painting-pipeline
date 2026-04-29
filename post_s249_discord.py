"""Post session 249 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s249_basquiat_crown_bearer.png")

FILENAME = "s249_basquiat_crown_bearer.png"

TEXT_BLOCKS = [
    """\
**The Crown Bearer** -- Session 249

*Near-black ground, Jean-Michel Basquiat Neo-Expressionist Scrawl mode -- 160th distinct mode*

**Image Description**

A single standing young man seen frontally, his figure filling the portrait canvas from crown to thigh. He faces directly forward: confrontational and calm simultaneously. The composition is centred, near-symmetric, almost hieratic -- like an icon. The background is raw near-black ground with scattered bright graffiti fragments.

The figure is a young Black man in his twenties. His head is a warm brown oval, slightly squarer at the jaw -- schematic rather than observed, a signifier of a face rather than a portrait of one. Two small dark oval eyes, direct and unafraid. His hair is a close-cropped afro, very dark, merging almost imperceptibly with the near-black background at its edges. His neck is broad, his shoulders wide. He wears a plain off-white t-shirt -- flat, almost the white of unprimed canvas. His arms hang at his sides in loose fists.""",

    """\
**The Crown**

Chrome yellow. Three triangular points, slightly irregular, slightly wobbling -- this is a hand-drawn crown, not a manufactured one. It floats centred above the head, a gap of dark air between its base and his hair.

The floating says: this crown did not arrive by inheritance. It arrived and is permanent.

**The Environment**

Near-black ground -- the dark of Lower Manhattan at 3 AM, the dark of raw unprimed canvas, the dark of everything that has tried to erase this figure. Scattered across the dark background: small red marks, yellow dots, a blue fragment, white sparks -- graffiti residue, evidence that this wall has been written on before and will be again. No ground plane, no sky, no architecture. Just the dark field and the figure within it.""",

    """\
**Technique & Palette**

Jean-Michel Basquiat (1960-1988) Neo-Expressionist Scrawl mode -- session 249, 160th distinct painting mode.

Stage 1, PER-PIXEL CHANNEL DISCRETE POSTERIZATION (n_levels=5): Each R, G, B channel is independently rounded down to the nearest of 5 discrete steps using floor(channel * 5) / 5. The result flattens continuous tonal gradients into discrete flat-colour zones: the chrome yellow crown becomes a single bright plane; the off-white shirt becomes one flat zone; the warm brown flesh steps into distinct flat tones. This is the graphic, sign-painter directness of Basquiat flat primary-colour zones, where colour is a single unambiguous decision. FIRST PASS to apply global per-pixel per-channel discrete floor-rounding as its primary colour stage.

Stage 2, RANDOM DIRECTIONAL CRUDE MARK OVERLAY (n_marks=220): 220 random short oriented marks scattered across the canvas, each rasterized as a line segment at a random angle and position. Dark marks (62%) and light marks (38%) create the energetic mark-field that covers every Basquiat surface -- evidence of gesture, urgency, process. FIRST PASS to generate a parametric random field of individually positioned and oriented discrete segment raster marks.""",

    """\
Stage 3, MIDTONE SATURATION AMPLIFICATION (sat_boost=0.45): Pixels in the midtone luminance window [0.22, 0.72] -- the warm flesh tones, the off-white shirt, the mid-value mark fragments -- are pushed further from grey toward maximum chromatic presence. FIRST PASS to selectively amplify saturation within a bounded midtone luminance window while leaving very dark shadows and very bright highlights at their natural saturation.

**Palette:** Near-black (background, hair) -- Chrome yellow (crown, 0.94/0.82/0.06) -- Cadmium red (graffiti marks) -- Warm brown (flesh, 0.66/0.44/0.22) -- Off-white (t-shirt, 0.90/0.88/0.82) -- Cobalt-ultramarine (background fragment) -- Orange-amber (skin highlight)

Paint Chroma Focus improvement (session 249): The focus point is placed at the face/crown centre (x=0.50, y=0.22). The central zone receives a saturation boost of 0.30; the peripheral zone receives a saturation reduction of 0.20. The face and crown become the most vivid area of the canvas; the lower torso and corners become quieter. FIRST IMPROVEMENT PASS to simultaneously boost saturation in a central radial zone and reduce it in the peripheral zone using a geometric radial distance field from a configurable focal point.""",

    """\
**Mood & Intent**

This painting tries to do what Basquiat did with his crown figures: to anoint. To say that this person is royalty. That this body has dignity and grace. That the crude marks do not diminish the figure -- they assert the terms of its existence.

The directness of the gaze says: I am here. The crown says: and I have always been here.

The viewer should feel the power of a direct gaze from a figure who has claimed his own space. The crude marks are not signs of degradation but signs of presence -- evidence that this person was here, is here, and will remain here. That is what Basquiat's crown means. That is what this painting intends.

*New this session: Jean-Michel Basquiat (Neo-Expressionism / Street Art / Graffiti, American, 1960-1988) -- basquiat_neo_expressionist_scrawl_pass (160th distinct mode). PER-PIXEL CHANNEL DISCRETE POSTERIZATION: global floor-rounding to n discrete levels per channel + RANDOM DIRECTIONAL CRUDE MARK OVERLAY: parametric random field of short oriented line-segment raster marks + MIDTONE SATURATION AMPLIFICATION: saturation boost within bounded luminance window. PAINT_CHROMA_FOCUS_PASS: radial differential saturation (centre boost / periphery reduce).*

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