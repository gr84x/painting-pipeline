"""Post session 264 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s264_quarry_face_aveyron.png")
FILENAME   = "s264_quarry_face_aveyron.png"

TEXT_BLOCKS = [
    """\
**Quarry Face at Nightfall, Aveyron** -- Session 264

*Outrenoir black ground, Pierre Soulages Outrenoir mode -- 175th distinct mode*

**Image Description**

A vertical basalt and schist quarry face, Conques-en-Rouergue, Aveyron, France -- the region where Pierre Soulages was born and from which his darkest instincts came. The stone wall fills nearly the entire canvas. The face is cut into a hillside; the ancient fracture planes of the rock run nearly horizontal, interrupted by irregular vertical joints. The viewpoint is direct -- face to face with the stone, as if standing a few metres from it, looking straight at it. There is no horizon line, no sky to speak of (a narrow sliver of deep violet at the very top), no middleground. The stone is the subject. The stone is everything.""",

    """\
**The Subject**

The basalt is nearly total darkness. The mineral is matte in its depths, but at the horizontal fracture planes -- where the stone split along its ancient grain under geological pressure -- the polished inner faces catch the last raking light of dusk from the west. These fracture seams read as horizontal bands of warmth against the surrounding mineral dark: not bright, not dramatic, but present -- the way a single candle reads in a cathedral.

There are approximately fourteen to eighteen visible fracture bands across the stone face, varying in apparent width from a narrow seam to a broader shelf. The left side of each fracture is slightly brighter than the right, where shadow accumulates as the evening light departs. At the very top of the canvas -- barely 7% of the canvas height -- a narrow band of deep violet-indigo sky is visible above the quarry's cut rim. At the very bottom, a still pool of dark water mirrors the stone above: the fracture bands appear again, inverted, even fainter.

The stone surface between fractures carries micro-texture: fine parallel saw-marks from the original quarrying, natural inclusions of quartz catching occasional points of light, and at the finest scale, a grey lichen that registers only as the faintest variation in the near-black field. The rightmost 25% of the stone face falls more deeply into shadow.

**The Environment**

The environment IS the stone face. There is no landscape, no horizon, no architecture beyond the quarry cut. The sky is a sliver of violet-indigo at the top -- not sky as sky, but sky as reminder that something exists beyond the stone. The water at the base is the stone's reflection: the quarry sees itself in the pool below. The stone is not in an environment. The stone IS the environment.""",

    """\
**Technique & Passes**

Soulages Outrenoir mode -- session 264, 175th distinct mode.

The `soulages_outrenoir_pass` applies three stages to create the signature Outrenoir effect.

Stage 1 (ULTRA-BLACK DEEPENING): A power-law compression (lum/threshold)^(power-1) is applied to all pixels below the black_threshold (0.40), pushing sub-threshold luminance toward near-zero. The exponent (deepening_power=2.4) creates an aggressive compression of near-darks without touching mid-tones or highlights. This simulates the absorption depth of Soulages' industrial-grade matte black acrylic -- richer and darker than any conventional oil paint. Approximately 1.49 million pixels deepened on this 1040×1440 canvas.

Stage 2 (HORIZONTAL REFLECTIVE STRIPE FIELD): A sinusoidal luminance variation -- `(sin(y * stripe_freq * pi) + 1) / 2` -- is confined to dark zones via a quadratic dark-region mask. With stripe_freq=24.0 and stripe_strength=0.052, this creates approximately 24 horizontal bands of slightly varying reflectivity within the black field, simulating Soulages' horizontal squeegee-drag marks that catch ambient light at different angles across the canvas surface. These are not marks in the conventional sense -- they are brightness topology. Approximately 1.15 million pixels received stripe variation.

Stage 3 (DARK-SIDE EDGE BLOOM): Sobel gradient magnitude is weighted by dark-side proximity (1 - lum), then Gaussian-blurred (sigma=3.0) and used to lift adjacent light pixels at dark/light transitions by bloom_strength=0.065. This creates the Soulages effect he described himself: the deep black makes the seams of light appear brighter than they are. The eye compensates for a darkness it cannot fully process, and the compensation elevates the remaining light. Approximately 323,000 pixels in the bloom zone.

Pipeline improvement s264 (LUMINANCE EXCAVATION): The `paint_luminance_excavation_pass` uses a difference-of-Gaussians approach to extract micro-texture frequency content from dark zones and apply a very subtle lift (dark_threshold=0.34, variance_sigma=5.0, lift_amount=0.030). The DoG reveals existing stroke direction, canvas grain, and pigment pooling from prior structural passes, very slightly amplifying this latent variation within the near-black field -- the technique Soulages discovered when he turned off his studio lights and found his black canvases emanating light from within.

Full pipeline: tone_ground (outrenoir black, 0.04/0.04/0.05) → underpainting (×2) → block_in (×2) → build_form (×2) → place_lights (×2) → paint_luminance_excavation_pass → soulages_outrenoir_pass → paint_flat_zone_pass → paint_shadow_bleed_pass""",

    """\
**Mood & Intent**

The viewer stands face-to-face with darkness. Not darkness as absence -- darkness as material, as mineral, as geological time. The stone has been here for three hundred million years. The quarry face was cut within the last century. The fracture planes were opened two hundred million years ago by pressures the imagination cannot hold. Against this time scale, the painting is a meditation.

The viewer should feel the specific quality of confronting something that does not need them: the stone is complete without observation, without witness. The few bands of light within the dark face are not warmth or invitation -- they are geometry, the record of ancient pressure, the signature of deep time.

Soulages returned to Conques throughout his life. The abbey church of Sainte-Foy at Conques, with its twelfth-century stained glass that he designed in 1994, filters light the same way his canvases do: the stone wall holds the dark; the glass releases light from within. He understood darkness as the condition of light, not its opposite.

The intended emotional response is not awe but presence: the viewer and the stone in the same silence, in the same late light, in the same darkness that will outlast both.

*New this session: Pierre Soulages (1919-2022, French, Outrenoir / Abstract) -- soulages_outrenoir_pass (175th distinct mode). THREE-STAGE OUTRENOIR: (1) power-law ultra-black deepening below threshold pushes near-darks toward total absorption; (2) sinusoidal horizontal stripe field confined to dark-region mask simulates horizontal squeegee-drag reflectivity bands within the black; (3) dark-side-weighted edge bloom lifts light pixels at dark/light transitions, making extreme darkness amplify adjacent light. Improvement: paint_luminance_excavation_pass -- DoG micro-texture extraction from dark zones, dark-region-gated lift to excavate buried stroke variation from sub-threshold field.*""",
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
    print(f"Posting Session 264 to Discord channel {CHANNEL_ID}...")
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
