"""Post session 258 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s258_morandi_vessels.png")
FILENAME   = "s258_morandi_vessels.png"

TEXT_BLOCKS = [
    """\
**Five Vessels, Morning Light** -- Session 258

*Warm linen-grey ground, Giorgio Morandi Dusty Vessel mode -- 169th distinct mode*

**Image Description**

Five ceramic vessels arranged on a narrow shelf at strict eye level -- the viewer seated, eye plane exactly at the shelf surface. From left to right: a tall narrow bottle with a cylindrical neck; a medium-height vase with a widening body; a squat round jar with a flat lid; a second tall bottle positioned slightly behind, its shoulder breaking the horizon of the shelf; and a shallow oval bowl at the far right, its interior nearly parallel to the viewer's eye. The arrangement is asymmetric and generates five distinct negative-space intervals between the forms. Each interval is as carefully weighted as the vessels themselves.""",

    """\
**The Figure**

The vessels are described as a collective, not individually. All are ceramic, all in slightly different shades of the same grey-ochre-dust family. The tall left bottle is warm ash-grey with a slight blue undertone on its shaded flank. The vase is the warmest object, dusty ochre on its lit face. The squat jar is the most neutral, a flat cool grey. The second bottle, set back, is in more shadow -- a quiet blue-grey. The oval bowl is the palest -- its interior near-vellum, slightly yellowish white. Each form is rendered as a simplified ellipse of revolution. Highlights are not specular points but broad soft zones of slightly warmer, slightly paler tone. Shadows are not dark -- they are merely less pale. The vessels sit on the shelf without cast shadows beneath them.

**The Environment**

The background is a pale warm grey shifting barely perceptibly lighter toward the upper right where diffuse morning light enters from outside the frame. This is a studio interior: Via Fondazza, Bologna. The shelf surface is warm off-white, visible beneath the vessels as a narrow horizontal band. There is a faint horizon line between wall and shelf -- not a hard edge but a tonal transition. There are no other objects, no tablecloth, no window detail. The space is reduced to its essence: vessel, ground, wall, light. Edges are gently resolved throughout -- never harsh, never fully lost.""",

    """\
**Technique & Passes**

Morandi Dusty Vessel mode -- session 258, 169th distinct mode.

The morandi_dusty_vessel_pass applies three stages after the vessel forms are blocked in and modelled. Stage 1 (Dusty Desaturation Veil): luminance-weighted HSV saturation reduction -- dark pixels lose their chromatic identity most; every colour in shadow becomes a version of warm grey-dust. Stage 2 (Tonal Compression): all pixel luminance is pushed toward a target mid-tone of 0.54, narrowing the tonal range to the roughly 0.35-to-0.82 window Morandi actually used -- no true blacks, no true whites. Stage 3 (Ochre Ground Reveal): in the lightest passages (luminance above 0.68) the warm ochre imprimatura bleeds through, tinting the near-vellum highlights with a faint gold warmth, as if the warm linen primer shows through thin final glazes.

Granulation improvement (session 258): The paint_granulation_pass adds Morandi's characteristic sanded surface texture -- frequency decomposition separates the canvas into mass and detail layers; warm pigment settles into the texture valleys, cool light reflects off the ridges; a paired unsharp mask restores gentle edge definition after the granulation softening.

*Additional passes: Edge Temperature (s256) -- very gentle warm/cool contrast at vessel edges; Tonal Key (s255) -- slight high-key push for morning light; Shadow Bleed (s257) -- faint warm bounce light in shadow zones.*""",

    """\
**Mood & Intent**

The intent is the radical intimacy of Morandi's project: the discovery that a small group of ordinary vessels, painted in a small room over half a century, contains as much content as any history painting or landscape. What does it mean to look at the same five objects every morning for forty years? The vessels accumulate time. They are not symbols of anything -- they refuse allegory. They are simply what they are: containers, surfaces, light, form.

The mood is pre-verbal quiet. Not melancholy -- nothing has been lost here. Just the particular silence of a room before the day has begun its demands. The ochre glow in the lightest passages is the only warmth: the morning light, arriving slowly, as it always does.

*New this session: Giorgio Morandi (1890-1964, Italian Metaphysical/Post-Impressionist still life) -- morandi_dusty_vessel_pass (169th distinct mode). THREE-STAGE DUSTY STILL-LIFE EFFECT: (1) luminance-weighted HSV saturation reduction as dusty atmospheric veil in shadows; (2) pixel-wise luminance lerp toward mid-tone for tonal range compression; (3) luminance-gated ochre ground-colour bleed in near-highlight regions. Improvement: paint_granulation_pass -- Gaussian frequency decomposition of canvas luminance; signed peak/valley chromatic granulation (warm-in-valley, cool-on-ridge); paired unsharp mask from same residual field for edge clarity.*""",
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
    print(f"Posting Session 258 to Discord channel {CHANNEL_ID}...")
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
