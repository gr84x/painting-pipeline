"""Post session 273 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s273_klein_blue_harbor.png")
FILENAME   = "s273_klein_blue_harbor.png"

TEXT_BLOCKS = [
    """\
**The Harbor at Nice at Dusk — Into the Blue Void** — Session 273

*Deep IKB cobalt ground, Yves Klein Nouveau Réalisme / Monochromism mode — 184th distinct mode*

**Subject & Composition**

A harbor view from a balcony in Nice, France, at the precise moment of late dusk when the Mediterranean sea and the cobalt sky above dissolve into International Klein Blue — the same blue Klein grew up beneath and later registered as his own. Canvas format: landscape (1440 x 1040). Four horizontal bands: sky (upper 52%), a thin luminous horizon seam (52–56%), sea (56–88%), and a dark iron-railed balcony ledge (lower 12%). A single slender sailboat mast rises vertically at x≈62%, barely perceptible against the void. The dark terracotta silhouette of the old harbor wall curves across the far left 15%. The primary subject is the BLUE ITSELF.""",

    """\
**The Subject & Environment**

SKY (upper 52%): Not a gradient of conventional colors but a deep, uniform IKB field that grades from deeper navy at the zenith to slightly lighter electric ultramarine at the horizon. The entire sky reads as one continuous blue field. The quality is the quality of Klein's monochromes: color freed from incident, from event, from subject.

HORIZON (52–56%): A narrow band of slightly lighter, more luminous pale cerulean — the last refraction of visible light at dusk. Barely distinguishable from the sky and sea on either side; its function is spatial orientation, not drama.

SEA (56–88%): Deep IKB, slightly darker than sky, very faint horizontal chop texture. A subtle oval reflection of the pale horizon visible in the center. The color family is identical to the sky — the horizon seam is the only spatial clue.

HARBOR WALL (left 15%): Dark terracotta-umber silhouette curving gently into depth, getting darker and cooler as it recedes. Ochre top edge catches the last ambient light.

BALCONY: Single thin iron railing at the extreme bottom, near-black horizontal, anchoring the viewer's elevated position.""",

    """\
**Technique & Passes**

Yves Klein Nouveau Réalisme / Monochromism mode — session 273, 184th distinct mode.

`klein_ib_field_pass()` — THREE-STAGE IKB CHROMATIC FIELD inspired by Yves Klein (1928-1962):

**Stage 1 (CHROMATIC RESONANCE-WEIGHTED IKB TINTING):** Compute the dot-product alignment between each pixel's RGB vector and the IKB color vector (R=0.00, G=0.18, B=0.65). Blue-family pixels receive full tint_strength; warm/complementary pixels receive reduced tinting, scaled by resonance_weight. First pass to modulate tinting strength by existing hue AFFINITY for the target color — prior tint passes apply uniform strength regardless of existing pixel hue.

**Stage 2 (MATTE PIGMENT MICRO-TEXTURE):** Add isochromatic Gaussian noise at σ=0.8 pixels (sub-pixel, below canvas-weave scale) to all three channels simultaneously. Simulates pure PB29 ultramarine crystal scattering at the matte Rhodopas surface. First pass to apply sub-pixel-sigma ISOCHROMATIC noise.

**Stage 3 (WARM SUPPRESSION):** Reduce red excess (warmth = max(R−B, 0)) proportionally to each pixel's measured warmth value. Warm pixels shift toward cool blue-neutral; cool pixels unchanged. First pass to suppress warmth content-adaptively by measured warmth value rather than by fixed zone or uniform color shift.""",

    """\
**Session Improvement s273**

`paint_transparent_glaze_pass()` — CLASSICAL OIL GLAZING SIMULATION (BEER-LAMBERT THIN-FILM MODEL):

Glazing is one of the oldest indirect oil painting techniques, used by Van Eyck, Titian, Rubens, Rembrandt, and Vermeer. A thin layer of transparent pigment-in-medium is applied over dried lighter passages. Light passes through the glaze TWICE (in and out), absorbing complementary wavelengths each time — the mathematical model is MULTIPLICATIVE BLENDING:

`out_c = original_c × (1 − glaze_strength × (1 − glaze_c))`

A pure blue glaze (0.00, 0.12, 0.72) suppresses red and green by `(1 − glaze_strength)`, passes blue nearly intact. This is the Beer-Lambert thin-film model — the only physically accurate model of transparent-filter light transmission. **First improvement pass to use multiplicative (multiply-mode) compositing** — all prior passes use linear interpolation.

Applies only to **light zones** (L > light_threshold) — the opposite luminance zone from scumbling (s272, which applies only to dark zones). Together, glazing and scumbling cover the full tonal range of classical indirect oil painting technique.""",

    """\
**Mood & Intent**

The painting intends THE VOID OF PURE COLOR. Yves Klein (1928–1962, Nice) spent the last six years of his life pursuing one idea: that a sufficiently pure, sufficiently saturated color, applied with sufficient conviction to a sufficiently large surface, stops being a representation of anything and becomes a PRESENCE — a direct, unmediated sensory encounter between the viewer's perceptual field and the color itself, freed from subject, composition, and narrative.

Klein said: *"The sky is my first work of art."* This painting is the literal image that preceded that idea: standing on a balcony in Nice at dusk, watching the sea and sky dissolve into each other, recognizing in that dissolution the possibility of a painting that is nothing but blue.

International Klein Blue (IKB 79) is PB29 ultramarine pigment in Rhodopas M60A polymer resin — registered May 19, 1960. The resin binds without coating, leaving air-facing crystal surfaces free to scatter light independently. The result is a blue that appears to have no surface — as if the canvas were an opening into infinite blue space.

The viewer should feel not calm but something more acute: the slight vertigo of color that has no edge, no subject, no story — only the endless, unflinching fact of its own blueness.""",

    """\
**Full Pipeline**

`tone_ground` (IKB cobalt 0.02/0.10/0.52) → `underpainting` (×2, stroke_size 54/38) → `block_in` (×2, stroke_size 30/18) → `build_form` (×2, stroke_size 12/6) → `place_lights` (stroke_size 4) → `paint_transparent_glaze_pass` (IKB blue glaze 0.00/0.12/0.72, glaze_strength=0.32, light_threshold=0.25) → `klein_ib_field_pass` (ikb=0.00/0.18/0.65, resonance_weight=0.72, tint_strength=0.44, warm_suppress=0.32) → `paint_aerial_perspective_pass` → `paint_chromatic_underdark_pass`

*New this session: Yves Klein (1928–1962, French, Nouveau Réalisme / Monochromism) — klein_ib_field_pass (184th distinct mode). THREE-STAGE IKB FIELD: (1) chromatic resonance-weighted tinting (blue-affinity modulates strength via dot-product alignment); (2) matte pigment micro-texture (sub-pixel isochromatic σ=0.8 noise); (3) warm suppression (content-adaptive R-excess reduction). Improvement: paint_transparent_glaze_pass — Beer-Lambert multiplicative thin-film compositing over light zones, first improvement to use multiply-mode blend. Together with paint_scumbling_veil_pass (s272), now covers both light and dark zones of classical oil indirect technique.*""",
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
    print(f"Posting Session 273 to Discord channel {CHANNEL_ID}...")
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
