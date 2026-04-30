"""Post session 256 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s256_kollwitz_grieving_mother.png")
FILENAME   = "s256_kollwitz_grieving_mother.png"

TEXT_BLOCKS = [
    """\
**Grieving Mother, Candlelight** -- Session 256

*Very dark warm-grey ground, Käthe Kollwitz Charcoal Compression mode -- 167th distinct mode*

**Image Description**

A single woman -- a grieving mother -- occupies the left three-quarters of the canvas, viewed from a three-quarter angle, slightly to her right. She is seated, hunched forward, her head bowed and turned away. Only the back of her head and left cheekbone are visible. Her hands are clasped tightly in her lap. The composition is deliberately compressed: the figure fills the frame from below the knees to just above the crown of her head, with only narrow dark margins. The background is pure charcoal darkness with no identifiable room. A single candle burns at the lower-left, throwing raking upward light onto the left side of her face and neck -- the only warm illumination.""",

    """\
**The Figure**

The woman is in her fifties -- working-class, heavy-set, dressed in coarse dark wool. Her hands are thick and rope-veined, the knuckles pale where they press together. The back of her neck is visible above the collar: creased, shadowed, carrying the weight of her posture. The single candle's raking upward light illuminates the lit cheekbone and jaw; the right side of her face is in total shadow. Her emotional state is one of silent, crushing grief -- not weeping, which is active; this is the stillness after weeping, the aftermath of loss held motionless in the body. The posture says everything: she has not moved in an hour.

**The Environment**

The background is pure charcoal darkness -- no specific room, no identifiable furniture. In the lower-left foreground is the faint circular glow of the candle halo, warm amber, slightly smeared by the charcoal medium. Immediately behind the figure's right shoulder, a vague darker mass suggests a wall or the back of a chair -- not defined, just present. The boundary between figure and ground is achieved by value contrast only: the lit side reads against the dark background; the shadow side disappears into it.""",

    """\
**Technique & Palette**

Käthe Kollwitz (1867--1945, German Expressionism / Social Realism) Charcoal Compression mode -- session 256, 167th distinct painting mode.

Stage 1, DARK TONAL COMPRESSION: dark_power=1.60. Power-law luminance compression (lum ** 1.60) pushes the entire tonal range toward the dark half of the scale, simulating charcoal's fundamental constraint that the paper provides the ceiling. median_lum=0.088, target_key=0.32. NOVEL: FIRST PASS to apply power-law exponent > 1 to the luminance field for directional dark-range compression simulating charcoal's inability to produce luminance above the paper value; distinct from paint_tonal_key_pass (s255) which applies sigmoid remapping.

Stage 2, DIRECTIONAL CHARCOAL SMEAR: smear_angle_deg=52°, smear_sigma_along=5.5, smear_sigma_across=0.55, smear_strength=0.60. Angle-parameterised anisotropic smear via paired image rotation: rotate canvas by -52°, apply asymmetric Gaussian blur sigma=(5.5, 0.55), rotate back by +52°, blend at 0.60. NOVEL: FIRST PASS to implement directional smear via paired forward/back rotation to align the smear axis with the filter's long axis; wyeth_tempera_drybrush_pass (s255) uses asymmetric sigma in a fixed orientation without rotation.

Stage 3, CHARCOAL HIGHLIGHT LIFT: lift_density=0.012, lift_radius=2.8, lift_strength=0.25. Sparse seeded random field (1.2% of pixels), blurred to radius 2.8, applied as additive brightening weighted by (1 - lum): lift_amount = 0.25 * lift_field * (1 - lum). NOVEL: FIRST PASS to apply darkness-weighted sparse Gaussian-blurred lift zones simulating kneaded-eraser charcoal removal; lift_zones=418803px.""",

    """\
**Edge Temperature improvement (session 256):** warm_hue_center=0.07 (orange-amber), cool_hue_center=0.62 (blue-grey), contrast_strength=0.12, gradient_zone_px=3.5. boundary_px=247658.

THREE-STAGE SIMULTANEOUS TEMPERATURE CONTRAST: (1) WARM/COOL HSV HUE MEMBERSHIP MASKS -- per-pixel warm and cool soft membership via wrapped Gaussian bell over hue distance weighted by saturation; NOVEL: first pass for saturation-weighted dual hue-membership masks for temperature contrast. (2) TEMPERATURE BOUNDARY GRADIENT ZONE -- gradient magnitude of (warm_mask - cool_mask) blurred to gradient_zone_px=3.5 pixels; NOVEL: first pass to locate warm/cool boundaries via gradient of the signed membership difference map. (3) BIDIRECTIONAL SIMULTANEOUS TEMPERATURE CONTRAST -- single signed R/B push: R += temp_signal*0.12, B -= temp_signal*0.08; warm-zone boundary pixels push warmer, cool-zone pixels push cooler simultaneously; NOVEL: first pass for bidirectional temperature push via (warm_mask - cool_mask) * boundary_zone.

**Palette:** charcoal black (0.08/0.07/0.06) -- compressed dark (0.22/0.18/0.15) -- graphite mid (0.38/0.32/0.27) -- warm mid (0.52/0.45/0.36) -- lifted grey (0.72/0.65/0.55) -- candle warm (0.82/0.58/0.22) -- lit flesh (0.76/0.62/0.48) -- near-white lift (0.88/0.83/0.76) -- warm shadow flesh (0.42/0.34/0.28)""",

    """\
**Mood & Intent**

This painting is about weight. Not the dramatic weight of an operatic grief, but the specific physical weight that enters the body when it has run out of movement -- when there is nothing left to do but sit. Kollwitz painted this category of stillness more than any other artist: the moment after the soldier is already dead, after the letter has been read, after all the protesting has been done and the situation has not changed.

The candle is the only specific thing in this darkness, and it illuminates only the back of a head that is turned away. The viewer is not permitted to see the face directly -- is kept outside of the grief, a witness rather than a participant. The intention is not to generate sympathy but recognition: the viewer knows this posture. They have sat in it themselves, or will.

*New this session: Käthe Kollwitz (1867--1945, German Expressionism / Social Realism) -- kollwitz_charcoal_compression_pass (167th distinct mode). THREE-STAGE CHARCOAL SIMULATION: (1) power-law dark tonal compression; (2) angle-parameterised anisotropic rotation-smear; (3) darkness-weighted sparse eraser-lift zones. Improvement: paint_edge_temperature_pass -- saturation-weighted HSV hue membership masks, warm/cool boundary gradient zone, bidirectional simultaneous temperature contrast.*""",
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
            "-F", 'payload_json={"attachments": [{"id": 0}]}',
        ],
        capture_output=True, text=True
    )
    resp = json.loads(result.stdout)
    msg_id = resp.get("id", f"ERROR: {resp}")
    print(f"Image message ID: {msg_id}")
    return msg_id


if __name__ == "__main__":
    print(f"Posting session 256 to Discord channel {CHANNEL_ID}...")

    ids = []
    for i, block in enumerate(TEXT_BLOCKS):
        print(f"  Posting text block {i+1}/{len(TEXT_BLOCKS)}...")
        mid = post_text(block)
        ids.append(mid)
        time.sleep(1.2)

    print(f"  Posting image {IMAGE_PATH}...")
    img_id = post_image(IMAGE_PATH, FILENAME)
    ids.append(img_id)

    print(f"\nAll message IDs: {ids}")
    print("Done.")
