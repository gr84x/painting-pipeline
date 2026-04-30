"""Post session 267 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s267_sunflower_rays.png")
FILENAME   = "s267_sunflower_rays.png"

TEXT_BLOCKS = [
    """\
**Three Sunflowers, Evening Sky** -- Session 267

*Warm sienna-brown ground, Natalia Goncharova Rayonist mode -- 178th distinct mode*

**Subject & Composition**

Three giant sunflower heads stand against a deep cobalt-to-golden evening sky in a portrait-format composition. The tallest sunflower occupies the centre-upper canvas, its face turned directly toward the viewer. Two flanking sunflowers at slightly lower heights frame the central one -- the left flower faces three-quarters left, the right faces three-quarters right, as though in active dialogue. The stems drive hard vertical lines from the base of the canvas upward, anchoring the composition against the dynamism of the Rayonist sky. The viewer stands close, looking slightly upward at the central disc.""",

    """\
**The Subject**

Each sunflower disc is rendered as a bold flat brown-black mass -- a large circular coin of compressed pigment at the head of each stem. Around each disc, 16-18 petals radiate outward as flat amber-gold lozenges, broad and blunt-tipped in the manner of Goncharova's bold Neo-Primitivist mark. The central sunflower carries 18 petals; the flanking pair 16 each. The petals are in full summer abundance -- heavy and full-faced, catching the warm evening light on their upper surfaces with vivid amber-gold, fading to ochre at the petal base. Each stem carries two pairs of broad elliptical leaves -- dark, assertive, the flat-cut leaf mass of folk embroidery.

**The Environment**

The sky occupies the upper half of the canvas and the negative space between the sunflower heads -- deep cobalt at the zenith, warming through violet-blue to amber-gold near the horizon. The Rayonist pass fractures this sky into crossing beams of directional light: golden sunflower disc-light streaks diagonally across the cooler sky zones; cool blue-violet rays cross the warm amber horizon light; and at every crossing, a zone of chromatic interference where warm and cool rays mix in a spatially alternating shimmer. The ground zone is warm olive-sienna -- a summer garden floor from which the thick stems rise.""",

    """\
**Technique & Passes**

Natalia Goncharova Rayonist mode -- session 267, 178th distinct mode.

Stage 1 (MULTI-ANGLE DIRECTIONAL STREAK SYNTHESIS, n_angles=4, ray_sigma=26px): The canvas colour is stretched simultaneously in 4 directions (0°, 45°, 90°, 135°) using 1D Gaussian blurs after rotation. The mean of all 4 directional blurs synthesises a multi-directional ray field. Each bright area (sunflower disc, petal highlight, sky glow) emits crossing rays in the Rayonist tradition. First mode pass to apply elongating directional blurs at 4+ distinct angles and composite them.

Stage 2 (LUMINANCE-WEIGHTED STREAK OVERLAY, ray_strength=0.30): Bright areas generate stronger ray contributions -- normalised luminance modulates the blend factor at each pixel. The golden discs produce full-strength rays; the dark leaf masses produce minimal ray extension. Models the Rayonist principle that light-source intensity governs ray emission strength.

Stage 3 (CHROMATIC HUE SHIMMER, shimmer_angle=16°, shimmer_freq=0.05): In crossing-ray interference zones (where the rayonist composite diverges from the original above threshold=0.10), a spatially alternating hue rotation of ±16° creates the chromatic vibration of Goncharova's prismatic colour placement along ray paths.""",

    """\
**Technique (continued)**

Pipeline improvement s267 (PALETTE KNIFE RIDGE TEXTURE): `paint_palette_knife_ridge_pass` -- first improvement to generate per-pixel ridge texture that adapts to the LOCAL GRADIENT DIRECTION (rather than fixed axes or isotropic noise). Stage 1: Sobel gradient direction field, smoothed by vectorial Gaussian (sin/cos circular mean, sigma=9px) to get the dominant paint-application direction. Stage 2: Ridge direction = gradient direction + 90° (perpendicular). Ridge phase = X*cos(perp) + Y*sin(perp); ridge_tex = sin(phase * ridge_freq * 2π). Ridges run transversely across petals (perpendicular to petal-axis gradient), authentically following the painted forms as a palette knife would. Stage 3: Luminance bell-gate (4 * ramp_lo * ramp_hi, peaks at mid-tone) ensures ridges are prominent in mid-tones, invisible in deep shadows and pure highlights.

Full pipeline: tone_ground (warm sienna 0.28/0.18/0.10) → underpainting (×2) → block_in (×2) → build_form (×2) → place_lights (×2) → paint_palette_knife_ridge_pass → goncharova_rayonist_pass → paint_hue_zone_boundary_pass → paint_granulation_pass""",

    """\
**Mood & Intent**

The painting embodies Goncharova's Rayonist conviction that painting should render not objects but the LIGHT BETWEEN objects -- the dynamic electromagnetic exchange between illuminated surface and viewing eye. The sunflowers are not static botanical specimens but active emitters of golden evening light. Their warm disc faces and glowing petals generate crossing ray fields that fracture the cobalt sky into planes of warm and cool interference.

The mood is vitalistic and declarative: the sunflowers radiate into the viewer's space with the same assertive frontality as the peasant icons and embroideries Goncharova drew from in her Neo-Primitivist period. The viewer should leave with the sense of having perceived not three sunflowers but the LIGHT of three sunflowers -- the rays, not the objects.

*New this session: Natalia Goncharova (1881-1962, Russian, Rayonism/Neo-Primitivism) -- goncharova_rayonist_pass (178th distinct mode). THREE-STAGE RAYONIST LIGHT FRACTURE: (1) multi-angle 1D Gaussian streak synthesis (0°/45°/90°/135°); (2) luminance-weighted streak overlay; (3) chromatic hue shimmer at ray interference zones. Improvement: paint_palette_knife_ridge_pass -- first improvement generating per-pixel ridge texture following the local gradient direction, with luminance bell-gate for mid-tone gating.*""",
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
    print(f"Posting Session 267 to Discord channel {CHANNEL_ID}...")
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
