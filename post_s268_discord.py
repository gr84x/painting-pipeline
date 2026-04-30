"""Post session 268 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s268_gorge_at_dawn.png")
FILENAME   = "s268_gorge_at_dawn.png"

TEXT_BLOCKS = [
    """\
**Huangshan Gorge at Dawn** -- Session 268

*Deep warm indigo-black ground, Zao Wou-Ki Lyrical Abstraction mode -- 179th distinct mode*

**Subject & Composition**

A deep mountain gorge at the moment of first dawn light -- the Huangshan (Yellow Mountains) of Anhui Province, evoked rather than depicted, in portrait format (1040 × 1440). The composition is centred on a luminous core of warm gold and apricot light in the upper portion of the canvas: sunrise breaking through morning mist above the gorge. The light source is not a disc or orb -- it is a zone of concentrated brilliance, the mountain mist acting as a diffuser. Radiating outward from this core, the canvas darkens in every direction: downward into the gorge shadow, sideways into the canyon walls, upward into the pre-dawn sky above the mist line.""",

    """\
**The Subject**

The gorge exists as felt depth rather than depicted form. The canyon walls are present as dark blue-indigo zones at the left and right margins, their materiality established through dense calligraphic peripheral marks: long, ink-dark strokes that orbit the luminous center at oblique tangential angles -- the visual language of the Chinese brush tradition fused with Western gestural painting. In the lower half of the canvas, the gorge floor and cliff bases emerge from the deepest indigo-black: raw rock, the ink tradition's ground. The mood is one of CONCENTRATED STILLNESS: the gorge holds its breath at first light, vast and ancient.

**The Environment**

Foreground (lower third): deep blue-black and indigo void -- the gorge floor in pre-dawn shadow. Mid-field (central third): the transition zone -- warm amber-ochre on the sun-lit canyon wall, cool cerulean on the shadowed wall, with atmospheric mist between them. The colour temperature clash in this zone is extreme -- warm and cool meet at the canyon's axis. Background/Sky (upper portion): the luminous center zone. Warm gold and apricot dissolve outward into pale misty white, then cool grey-blue of pre-dawn atmosphere. No hard edge anywhere in this zone -- everything dissolves.""",

    """\
**Technique & Passes**

Zao Wou-Ki Lyrical Abstraction mode -- session 268, 179th distinct mode.

`zao_wou_ki_ink_atmosphere_pass` -- FOUR-STAGE LYRICAL ABSTRACTION inspired by Zao Wou-Ki (Zhao Wuji, 1920-2013):

Stage 1 (LUMINOUS CENTER DETECTION AND RADIAL GLOW): Locate the painted luminance peak via Gaussian-smoothed luminance argmax -- first pass to locate the ACTUAL light source in the painted image rather than imposing a fixed compositional center. Build a content-aligned radial glow field from that peak, amplifying brightness and warmth in the detected light zone.

Stage 2 (DARK PERIPHERAL VIGNETTE): Non-linear (power-1.5) peripheral darkening centered on the detected luminous peak toward deep blue-black (0.04/0.06/0.14). Creates the asymmetric dark surround of Zao's luminous-center compositions. First pass to center the vignette on the DETECTED LUMINOUS PEAK rather than the canvas center.

Stage 3 (DUAL THERMAL COLOR FIELD): Luminance-proportional hue shift toward gold in bright zones (lum > 0.55) and toward blue-indigo in dark zones (lum < 0.35), with shift magnitude proportional to tonal depth. First pass to apply OPPOSITE hue rotations simultaneously to bright and dark zones, scaled by luminance -- creating the characteristic warm center / cool periphery temperature gradient of Zao's work.""",

    """\
**Technique (continued)**

Stage 4 (INK CALLIGRAPHIC STREAK SYNTHESIS): Gestural ink marks placed specifically in the peripheral zone (beyond radial threshold from luminous center), oriented TANGENTIALLY to the radial field with angular noise, rendered as anti-aliased Gaussian line segments. First calligraphic pass to place marks in the PERIPHERAL ZONE and orient them tangentially -- generating the orbiting quality of Zao's peripheral marks that circle the luminous interior.

Session improvement s268 (AERIAL PERSPECTIVE): `paint_depth_atmosphere_pass` -- first pass to simulate AERIAL PERSPECTIVE (atmospheric recession) by computing a per-pixel depth map from two signals: (1) vertical position (top = sky = far) and (2) local contrast (low contrast = distant/smooth passage). Blend each pixel toward a cool blue-grey haze color proportional to estimated depth. Models Leonardo da Vinci's atmospheric perspective principle: distant objects appear lighter, cooler, and lower in contrast.

Full pipeline: tone_ground (deep indigo-black 0.08/0.06/0.18) → underpainting (×2) → block_in (×2) → build_form (×2) → place_lights → paint_depth_atmosphere_pass → zao_wou_ki_ink_atmosphere_pass → paint_granulation_pass → paint_sfumato_contour_dissolution_pass""",

    """\
**Mood & Intent**

The painting is intended to convey PRIMORDIAL DEPTH AND FIRST LIGHT -- the sensation of standing at the edge of a mountain gorge in the seconds before sunrise fully breaks, when the landscape is still mostly dark but a warm radiance is already present in the upper atmosphere. The viewer should feel both the weight of the darkness below and the pull of the light above -- the vertical tension of the gorge architecture, the horizontal dissolution of the mist.

The calligraphic peripheral marks carry the energy of the Chinese ink tradition: the understanding that a mark is not a representation but an event, a gesture of the hand in the presence of the world. The painting should leave the viewer with a feeling of quiet awe at geological time and the transience of any particular moment of light.

*New this session: Zao Wou-Ki (1920-2013, Chinese-French, Lyrical Abstraction) -- zao_wou_ki_ink_atmosphere_pass (179th distinct mode). FOUR-STAGE LYRICAL ABSTRACTION: (1) content-aligned luminous center detection + radial glow; (2) non-linear peripheral vignette toward deep blue-black; (3) dual thermal color field (warm gold in lights, cool indigo in darks); (4) tangential ink calligraphic strokes in peripheral zone. Improvement: paint_depth_atmosphere_pass -- multi-cue aerial perspective simulation.*""",
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
    print(f"Posting Session 268 to Discord channel {CHANNEL_ID}...")
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
