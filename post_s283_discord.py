"""Post session 283 Discord painting to #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s283_volga_hauler.png")
FILENAME   = "s283_volga_hauler.png"

TEXT_BLOCKS = [
    """\
**The Hauler's Rest** — Session 283

*Oil on linen · Ilya Repin mode — 194th distinct mode · Character Depth + Form Curvature Tint*

**Subject & Composition**

A single Volga barge hauler rests on a sunbaked river bank, seated low on a weathered boulder, his broad hands folded over the knob of a gnarled walking staff planted between his feet. He is seen from slightly below eye level at a 3/4 angle — the viewer meets this man almost face to face, without hierarchy or distance. His head, turned just past three-quarters to confront us directly, anchors the upper portion of a tall portrait canvas. The rope harness is still looped across his chest, marking him as mid-rest rather than finished for the day. He is not performed. He simply is.""",

    """\
**The Figure**

Male, broad-shouldered, in his mid-40s but aged beyond his years. His skin is deeply weathered — raw sienna and burnt umber at the temples, lighter warm ochre across the brow and illuminated cheek. His face holds the specific psychology of Repin's burlaki: eyes neither angry nor despairing but watchful and measuring, carrying a patient, undefeated dignity that is the emotional center of the image. Dark brows, a wide jaw, a short beard that is slightly unkempt. His worn linen shirt — once white, now the color of dry grass and river silt — hangs open at the collar, revealing a neck corded with muscle.

Late afternoon light cuts across his left cheek and brow from a low angle, throwing the right side of his face into deep, transparent shadow. The lit zone is warm — cream, ochre, raw sienna. The shadow zone is cool and glazed — blue-violet, transparent grey.""",

    """\
**The Environment**

The Volga in late summer afternoon. The river bank in the immediate foreground is hard-packed clay and sand, scattered with round river stones, in warm ochre and raw sienna. The broad Volga surface stretches out behind the figure in silver-grey, moving slowly, catching the flat oblique light of a descending sun. The far bank is a low dark smudge of forest barely visible through summer haze. The sky is vast: pale cerulean overhead shading through warm ochre-gold at the horizon. A distant barge shape — barely legible — occupies the lower-right background. A coil of tarred rope and two iron spikes lie discarded on the bank near his feet.

Foreground warm (ochre and sienna clay), background cool (silver water, blue-grey sky): the figure exists at the temperature boundary between earth and air.""",

    """\
**Technique & Palette — Ilya Repin (1844–1930)**

Repin's alla prima realist oil technique: direct, confident, form-following brushwork. The lit zones (left cheek, brow, lit shoulder) carry warm umber-flesh — raw sienna with an ochre undertone. The shadow zones are cool, glazed with blue-violet and transparent grey. Earth and air are in tonal dialogue across the figure's body.

The new *repin_character_depth_pass* (194th distinct mode) builds psychological realism in four stages: (1) **Gradient-orientation form blur** — gradient magnitude gates a spatial blur weighted by local |∇L|, approximating direction-following brushwork; first pass to gate a form-smoothing step on gradient magnitude, linking spatial filtering to structural edge strength; (2) **Midtone warm umber accent** — bell-gate mask (0.30–0.62) pushes toward Repin's warm umber-flesh (0.70/0.50/0.32), his specific midtone palette identity; (3) **Cool transparent shadow deepening** — smooth falloff shadow mask pushes toward cool violet (0.28/0.28/0.48), fixed artist-specific target distinct from the adaptive shadow_temperature_pass; (4) **Structural edge crispening** — gradient-gated unsharp mask (σ=1.1, amount=0.50) recovers character-defining edges (jaw, brow, collar) as the psychological-edge finalizer.""",

    """\
**Improvement & Mood**

The new *paint_form_curvature_tint_pass* (s283 improvement) models convex-concave light temperature: the Laplacian (∑ ∂²L/∂x²+∂²L/∂y²) of the smoothed luminance estimates local 3D form curvature — positive Laplacian = convex surfaces (facing the key light, receiving warm cream-gold), negative Laplacian = concave surfaces (sheltered, receiving cool ambient sky). First pass to use the second spatial derivative as a gate, and the first to apply opposing temperature effects to zones defined by a signed mathematical quantity rather than a luminance threshold.

**Mood & Intent**

Monumental humility. The viewer meets this man directly — not from above, not sentimentally, but as one equal to another. The image intends the specific Repin emotion: an ordinary human being, caught at a real moment, neither romanticized nor pitied, simply witnessed. The weight of physical labor and the unbroken dignity of the person who performs it.

**Full Pipeline:** `tone_ground` → `underpainting` (×2) → `block_in` (×2) → `build_form` (×2) → `place_lights` (×2) → `repin_character_depth_pass` → `paint_form_curvature_tint_pass` → `paint_contre_jour_rim_pass` → `paint_shadow_temperature_pass`

*New this session: Ilya Repin (1844–1930, Ukrainian-Russian Realist/Peredvizhniki) — repin_character_depth_pass (194th distinct mode). Improvement: paint_form_curvature_tint_pass — Laplacian-of-Gaussian form curvature → warm convex / cool concave tint; first use of second spatial derivative (∇²L) as pass gate in this engine.*""",
]


def post_text(text: str) -> str:
    assert len(text) <= 2000, f"Text block too long: {len(text)} chars"
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
    # Validate block lengths
    for i, block in enumerate(TEXT_BLOCKS):
        if len(block) > 2000:
            print(f"WARNING: Block {i} is {len(block)} chars (limit 2000)")

    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image not found at {IMAGE_PATH}")
        return

    print(f"Posting s283 Discord painting to channel {CHANNEL_ID}...")
    ids = []
    for i, block in enumerate(TEXT_BLOCKS):
        print(f"Posting text block {i + 1}/{len(TEXT_BLOCKS)} ({len(block)} chars)...")
        mid = post_text(block)
        ids.append(mid)
        time.sleep(0.8)

    print("Posting image...")
    img_id = post_image(IMAGE_PATH, FILENAME)
    ids.append(img_id)
    print(f"Done. Message IDs: {ids}")
    return ids


if __name__ == "__main__":
    main()
