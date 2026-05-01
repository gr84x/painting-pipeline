"""Post session 282 Discord painting to #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s282_frozen_river_dawn.png")
FILENAME   = "s282_frozen_river_dawn.png"

TEXT_BLOCKS = [
    """\
**The Thaw — A Frozen Russian River at Dawn** — Session 282

*Oil on linen · Alexei Savrasov mode — 193rd distinct mode · Lyrical Mist + Contre-Jour Rim*

**Subject & Composition**

A wide Russian river in late February, seen from the high left bank at first light. The river fills the lower two-thirds of the composition: a broad frozen expanse of blue-white ice, cracked by pressure ridges that run diagonally left to right, with a strip of open dark water visible at the far-left edge where the current has begun to undercut the ice. The opposite bank is pale and indistinct — a distant dark treeline of conifers punctuated by a single white church bell tower, its cross just visible against the overcast sky. Three or four bare willow trees lean from the near bank at the right, their intricate branch networks silhouetted black against the pale ice and the dawn sky. Several rooks circle silently above the far treeline, small dark crescents against the grey.""",

    """\
**The River**

The ice surface is the compositional heartland. It is not uniform: the center shows faint mottling and diagonal pressure cracks — the ice's memory of the river's current, pressing upward from below. Where the ice meets the near bank, it darkens under the shadow of the willow canopy; where it approaches the far-left channel, it grades into the deep greenish-black of open water. This open channel — the first sign of thaw — runs along the far bank and carries a faint mist at its surface, the warmer river water meeting the frozen air. The near bank is snow-covered: warm cream-yellow on the exposed ridge, cool blue-grey in the shadow beneath the willows. The church tower stands impossibly still across the ice, white against white, its vertical mass the only architectural accent in a landscape of horizontals.""",

    """\
**The Environment**

Central Russia, the Oka watershed, late February, 7 AM. Temperature just below freezing — the last degrees before the first sustained thaw. The air is still and damp; the light is diffuse, directionless, the sun still below the cloud layer but the eastern sky brightening imperceptibly toward the right. The willows are absolutely bare: not a bud, not a swelling — just the precise black calligraphy of their branches against the pale ice and sky. The silence of the Russian winter: the soft creak of ice settling, the distant call of rooks. The world is suspended between the last of winter and the first of spring, and the painting lives in that exact moment — the frozen river as metaphor for anticipation, for the holding of breath before the world thaws and begins again.""",

    """\
**Technique & Palette — Alexei Savrasov (1830–1897)**

Savrasov's method in full: horizontal atmospheric layering in the sky (the specific mist bands of a Russian overcast dawn), the precise cool-grey-violet that is his signature light, bare willow branches sharp and botanically specific against the pale ice, and the subtle warm straw-ochre of snow-covered fields in the lower zone.

The new *savrasov_lyrical_mist_pass* (193rd distinct mode) applies four stages: (1) **Horizontal atmospheric mist banding** — a horizontal uniform filter (42:2 width:height kernel ratio) creates layered atmospheric bands in the sky, the geometric complement of Shishkin's vertical bark filter from s281, and the first pass to use a horizontal-dominant kernel; (2) **Mid-luminance bell-gate cool-grey push** — a bell-shaped smooth gate (product of two opposing ramps) centers the effect in the midtone range (0.38–0.70), pushing toward Savrasov's cool blue-grey (0.62/0.67/0.76), the first pass to target mid-luminance specifically with a bell gate rather than a step threshold; (3) **Vertical gradient (Gy) branch sharpening** — the y-component of the Gaussian derivative detects horizontal edges (branch outlines against sky), applying unsharp mask only there, the first pass to decompose the gradient into directional components and use Gy specifically; (4) **Lower-zone × saturation warm ochre horizon** — combines a spatial lower-zone mask with a low-saturation gate, pushing toward warm straw-ochre, distinct from s281's saturation-only gate by adding the spatial constraint.

The new *paint_contre_jour_rim_pass* (s282 improvement) models the optical geometry of back-lit edges: dilating the bright-zone mask identifies dark pixels adjacent to bright zones (silhouette edges) and applies a warm golden rim; simultaneously, dilating the dark-zone mask identifies bright pixels adjacent to dark zones and applies a cool halation, creating a chromatic dialogue across both sides of every contre-jour boundary — warm rim on the dark side, cool shadow on the bright side.

Palette: Savrasov grey (cool blue-violet) · pale overcast sky · bare branch umber · warm straw ochre · dark bark shadow · high snow white · melting earth ochre · sky reflection blue-grey""",

    """\
**Mood & Intent**

*Vesna* — the Russian word for spring — carries an emotional weight that "spring" in English does not quite reach: it is also longing, hope, and the specific grief of winter's end, the knowledge that the stillness is about to break. Savrasov painted *vesna* more accurately than any Russian painter before or after him. His "The Rooks Have Come Back" (1871) was the painting that taught Russians what their own landscape looked like — not idealized, not Italian, not romantic: their landscape, seen with clear and loving eyes.

This painting tries to inhabit the same moment: the frozen river not yet thawed, the willow branches not yet budded, the rooks returned but still circling, not yet settled. The church tower across the ice is the only permanent thing in a landscape where everything else is in transition. The viewer should feel the cold, the silence, and in the silence, the first faint warmth of what is coming.

**Full Pipeline:** `tone_ground` (pale warm-grey) → `underpainting` (×2) → `block_in` (×2) → `build_form` (×2) → `place_lights` → `savrasov_lyrical_mist_pass` → `paint_contre_jour_rim_pass` → `paint_shadow_temperature_pass` → `paint_depth_atmosphere_pass` → `paint_lost_found_edges_pass`

*New this session: Alexei Savrasov (1830–1897, Russian Realist/Lyrical Landscape) — savrasov_lyrical_mist_pass (193rd distinct mode). FOUR-STAGE LYRICAL LANDSCAPE SYSTEM: (1) horizontal uniform filter (42:2 ratio) for atmospheric banding; (2) bell-gate mid-luminance cool-grey push — first use of product-of-ramps gate for mid-zone color; (3) Gy-component branch sharpening — first pass to decompose gradient into Gx/Gy and use y-component alone; (4) lower-zone × saturation warm horizon — first spatial+saturation combined gate. Improvement: paint_contre_jour_rim_pass — dual-side luminance boundary model: warm rim on dark side of bright/dark boundaries via bright-mask dilation, cool halation on bright side via dark-mask dilation, first improvement pass to model opposing effects on both sides of a luminance boundary simultaneously.*""",
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
    print(f"Posting s282 Discord painting to channel {CHANNEL_ID}...")
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
