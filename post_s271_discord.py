"""Post session 271 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s271_nordic_fjord_dusk.png")
FILENAME   = "s271_nordic_fjord_dusk.png"

TEXT_BLOCKS = [
    """\
**Trolljegeren's Pond — Twilight Over a Norse Peat Bog** -- Session 271

*Dark peat-umber ground, Theodor Kittelsen Norwegian Romantic Realism mode -- 182nd distinct mode*

**Subject & Composition**

A small, near-circular peat bog pond set in open moorland at deep twilight. The canvas is wide landscape (1440 × 1040), framing a low horizon with the pond occupying the lower 40% as a perfect still mirror. The sky fills the upper 60%, transitioning from amber-gold just above the silhouetted treeline to cool steel blue in the mid-sky to deep prussian blue-violet at the zenith. A single bright evening star emerges in the upper-right sky. The composition is rigorously horizontal: treeline and pond edge both run parallel to the canvas edge, emphasizing the vast flatness of Norwegian moorland.""",

    """\
**The Subject**

The pond is the central subject: a perfectly still body of dark water that mirrors the twilight sky above it. The reflection inverts the sky gradient — amber at the water's far edge, steel blue in the pond center, deep violet near the near shore. The surface is absolutely still; there is not a ripple. A thin wispy band of mist rises from warm water into cooler air, hovering just above the pond surface, pale silver-white against the dark treeline.

Flanking the pond: silhouetted birch trees with pale trunks and dark branching crowns, their reflections mirrored in the water below. Silhouettes are sharply cut against the pale sky — the defining Kittelsen opposition. To the far right: a lone dead birch with bare upward-reaching branches. On the near shore: dark heather and sedge tufts pressing toward the viewer.

The emotional state of the scene is deep, listening stillness — the particular Norwegian quality of being utterly alone in the wilderness at the edge of night, when daylight is fully gone but darkness has not yet taken complete hold. There is a latent sense that the landscape is aware of you. Kittelsen placed his trolls and spirits into exactly these moments.""",

    """\
**Technique & Passes**

Theodor Kittelsen Norwegian Romantic Realism mode — session 271, 182nd distinct mode.

`kittelsen_nordic_mist_pass` — FOUR-STAGE ATMOSPHERIC TECHNIQUE inspired by Theodor Kittelsen (1857-1914):

Stage 1 (CONTENT-ADAPTIVE FAR ZONE DETECTION): Compute local luminance variance via gaussian(L²) - gaussian(L)² at variance_sigma. Detect far/mist zones as pixels with luminance in [far_lum_low, far_lum_high] AND local variance below 35th-percentile threshold. NOVEL: joint luminance-range AND variance condition to detect atmospheric zones without assuming depth follows vertical position — a fog bank can appear anywhere in the frame and is identified by its smoothness AND brightness.

Stage 2 (ATMOSPHERIC HAZE TINT IN FAR ZONES): Blend far zones toward a cool Prussian blue-grey. Tint strength is luminance-modulated within the detected zone — brighter far-zone pixels receive stronger haze, implementing the Kittelsen sky gradient from maximum haze at the bright horizon to minimum haze at the dark zenith.

Stage 3 (SILHOUETTE EDGE CONTRAST HARDENING): Compute gradient magnitude of the far-zone mask. At zone boundaries, darken the near (dark silhouette) side and lighten the far (sky/mist) side. NOVEL: zone-mask-gradient silhouette hardener — contrast derived from content-adaptive zone topology, not pixel-value edge detection.""",

    """\
**Technique (continued)**

Stage 4 (DEEP SHADOW BLUE-VIOLET UNDERLAYER): Detect deep shadow pixels (L < dark_threshold) and blend toward Prussian blue-violet, proportional to shadow depth. Recreates Kittelsen's characteristic cold blue-violet in dark forest, bog water, and peat shadow zones — never neutral black.

Session improvement s271 (`paint_reflected_light_pass`) — SECONDARY BOUNCE LIGHT INJECTION, physically motivated by the classical painting principle of \'luce riflessa\':

Stage 1 (SHADOW/LIGHT ZONE DETECTION): Binary zone segmentation of canvas into shadow (L < shadow_threshold) and lit zones (L ≥ light_threshold).

Stage 2 (PROXIMITY-WEIGHTED LIT COLOUR SAMPLING): For each pixel position, Gaussian-blur the lit-zone pixel colours at sigma=search_radius/2. The blur implements inverse-distance weighting: nearby lit pixels contribute more to the local average than distant ones. NOVEL: first improvement pass to derive injected shadow colour from actual nearby lit-zone pixel values — prior passes use preset warm/cool biases.

Stage 3 (EDGE-BIASED INJECTION): Inject the blurred lit colour into shadow zones at strength modulated by shadow-edge proximity (stronger near shadow boundary, weaker deep in shadow) and nearby lit surface availability.

Stage 4 (VERTICAL SKY/GROUND BIAS): Upper shadow pixels receive a cool-blue sky bounce; lower shadow pixels receive a warm-gold ground bounce.

Full pipeline: tone_ground → underpainting (×2) → block_in (×2) → build_form (×2) → place_lights → paint_reflected_light_pass → kittelsen_nordic_mist_pass → paint_depth_atmosphere_pass → paint_lost_found_edges_pass → paint_chromatic_vibration_pass""",

    """\
**Mood & Intent**

The image intends NORDIC STILLNESS and THE WEIGHT OF DUSK. Kittelsen painted the Norwegian landscape at the moment when the rational world recedes and the folk world — trolls, nisse, spirits of the bog and forest — becomes plausible. This is that moment. The still water is too perfect, the silence too complete. The viewer is invited to pause at the edge of the pond and listen. The single evening star names the moment precisely: day has ended; night has not yet arrived; anything might walk out of the dark treeline.

*Theodor Kittelsen (1857-1914) — Norwegian Romantic Realist, illustrator, and the definitive visual interpreter of Norse folklore. His paintings of trolls, nisse, and Norse spirits remain the canonical image of the Norwegian folk imagination. His landscape paintings — particularly the bog and birch twilight series from Snøasen — represent some of the most atmospheric Norwegian landscape painting of the 19th century.*

Session 271 | Theodor Kittelsen (268th artist) | 182nd distinct pass mode | 1440 × 1040""",
]


def curl(args):
    cmd = ["curl", "-sS"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print(f"curl error: {result.stderr[:400]}")
    return result.stdout


def send_message(text: str) -> str:
    payload = json.dumps({"content": text})
    out = curl([
        "-X", "POST",
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        "-H", f"Authorization: Bot {TOKEN}",
        "-H", "Content-Type: application/json",
        "-d", payload,
    ])
    try:
        data = json.loads(out)
        msg_id = data.get("id", "?")
        print(f"  Message sent: {msg_id}")
        return msg_id
    except Exception as e:
        print(f"  Parse error: {e} | raw: {out[:200]}")
        return "?"


def send_image(image_path: str, filename: str, caption: str = "") -> str:
    out = curl([
        "-X", "POST",
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        "-H", f"Authorization: Bot {TOKEN}",
        "-F", f"file=@{image_path};filename={filename}",
        "-F", f"payload_json={{\"content\": \"{caption}\"}}",
    ])
    try:
        data = json.loads(out)
        msg_id = data.get("id", "?")
        print(f"  Image sent: {msg_id}")
        return msg_id
    except Exception as e:
        print(f"  Parse error: {e} | raw: {out[:200]}")
        return "?"


def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: image not found at {IMAGE_PATH}")
        print("Run paint_s271_nordic_fjord_dusk.py first.")
        return

    print(f"Posting session 271 to Discord channel {CHANNEL_ID}...")
    ids = []

    # Post the image first
    print("Uploading image...")
    img_id = send_image(IMAGE_PATH, FILENAME)
    ids.append(img_id)
    time.sleep(1.2)

    # Post text blocks
    for i, block in enumerate(TEXT_BLOCKS):
        print(f"Sending text block {i + 1}/{len(TEXT_BLOCKS)}...")
        msg_id = send_message(block)
        ids.append(msg_id)
        time.sleep(1.2)

    print(f"\nDone. Message IDs: {'/'.join(ids)}")


if __name__ == "__main__":
    main()
