"""Post session 255 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s255_wyeth_winter_oak.png")
FILENAME   = "s255_wyeth_winter_oak.png"

TEXT_BLOCKS = [
    """\
**Winter Oak, Brandywine** -- Session 255

*Dry warm ochre gesso ground, Andrew Wyeth Tempera Dry-Brush mode -- 166th distinct mode*

**Image Description**

A solitary leafless oak tree stands at the crest of a low rise, slightly right of canvas center. Viewed from below and to the left, the tree occupies the central two-thirds of the canvas height. The composition is asymmetric: the main trunk leans slightly, and a long heavy branch extends far to the left before rising. No other trees are visible. The sky fills the upper 60% of the canvas. A weathered split-rail fence descends diagonally from the upper left across the foreground slope. The winter light is diffuse and sourceless -- the flat, even illumination of an overcast Pennsylvania January.""",

    """\
**The Figure (the tree)**

The oak is old and gnarled, with dark warm umber bark, deeply fissured. The trunk is approximately 20 inches in diameter at the base, tapering as it divides near the top third into three major branches. These divide again and again until the finest twigs are single marks against the pale sky. The bark is dark with the diffuse overhead light catching the ridges very slightly on the upper-left surfaces. The tree's silhouette is irregular, worn, asymmetric -- not the romantic symmetrical oak of Victorian painting, but the specific, individual character of a tree that has endured two hundred winters.

**The Environment**

The sky is pale and nearly white at the upper left, warming to a faint ochre-grey at the horizon. No sun is visible. The ground is frozen dark umber-brown with sparse patches of dried amber grass at the lower right. The hill crests just below the tree's root line and descends gently rightward. The far distance is a pale grey-ochre suggesting a frozen farm field. The split-rail fence runs diagonally: three weathered grey rails with dark posts. The boundaries between sky, hill, and ground are softly but distinctly present -- tempera's quality of values that nearly merge without dissolving.""",

    """\
**Technique & Palette**

Andrew Wyeth (1917--2009, Chadds Ford, Pennsylvania) Tempera Dry-Brush mode -- session 255, 166th distinct painting mode. American Realism / Regionalism.

Stage 1, DRY CHALK SURFACE: chalk_amplitude=0.022. Seeded random noise blurred with asymmetric Gaussian sigma=(y=3.0, x=0.5) creates horizontally-biased grain -- applied uniformly to all channels to preserve hue. NOVEL: FIRST PASS to apply directional asymmetric-blur luminance-domain noise to simulate the dry horizontal grain of egg tempera on gessoed panel; distinct from paint_surface_tooth_pass (s252) which uses a different mechanism; no prior pass generates horizontal-grain directional noise using asymmetric Gaussian blur sigma for tempera surface simulation.

Stage 2, MIDTONE PRECISION BAND CONTRAST: midtone_low=0.20, midtone_high=0.80, contrast_strength=0.45. Unsharp-mask residual (canvas - Gaussian_blur_sigma8) gated by a soft luminance band mask [0.20, 0.80] with 0.15 lum ramps at each edge. NOVEL: FIRST PASS to apply unsharp-mask contrast gated by a soft luminance band mask targeting only the midtone zone; fiber_pixels=4342.

Stage 3, DRY-BRUSH FIBER TRACES: fiber_low_lum=0.15, fiber_high_lum=0.48, fiber_density=0.05, fiber_brightness=0.09. Sparse activation field (5% of pixels) blurred horizontally only (sigma=(0, 1.5)), applied as additive brightness in tonal transition zones. NOVEL: FIRST PASS to generate a sparse-then-horizontal-blur noise field applied as fiber-trace brightening in tonal transition zones.""",

    """\
**Tonal Key improvement (session 255):** target_key=0.42 (slightly low-key -- winter, somber), key_strength=4.5, dither_amplitude=0.006. median_lum=0.656.

THREE-STAGE TONAL KEY MANAGEMENT: (1) LUMINANCE MEDIAN ANALYSIS -- numpy.median(lum) as the tonal center of mass; NOVEL: first pass to compute luminance median to drive key correction. (2) SIGMOID KEY CORRECTION -- per-pixel: sigmoid_input = (lum - median) * key_strength + (target_key - 0.5) * key_strength; new_lum = 1/(1+exp(-sigmoid_input)); scale = new_lum/(lum+eps) clamped to [0.05, 20]; NOVEL: first pass to apply sigmoid function to per-pixel luminance deviation from computed median to push tonal distribution toward user-specified key. (3) MICRO-TONAL DITHERING -- 4x4 Bayer matrix normalised to [-0.5, 0.5] scaled by dither_amplitude=0.006, tiled to canvas size, applied uniformly to all channels; NOVEL: first pass to apply Bayer matrix ordered dithering to prevent posterisation banding in compressed tonal zones.

**Palette:** Winter sky pale (0.86/0.84/0.78) -- Sky horizon warm (0.80/0.76/0.66) -- Bark dark umber (0.28/0.22/0.16) -- Bark mid (0.48/0.38/0.28) -- Bark warm light (0.60/0.50/0.38) -- Ground frozen dark (0.36/0.30/0.22) -- Ground ochre (0.62/0.52/0.36) -- Dry grass amber (0.72/0.62/0.40) -- Fence weathered grey (0.60/0.58/0.52) -- Far distance pale (0.72/0.68/0.58)""",

    """\
**Mood & Intent**

This is a painting of endurance and particularity. Wyeth painted what he knew with exactitude -- not a generic oak but THIS oak, in THIS field, in THIS light. The bare branches against the winter sky capture both the vulnerability and the permanence of the living world. The tree stands where it has always stood. The frozen ground will give slightly in spring; the bark does not change.

This is a painting about time that does not become a painting about nostalgia -- it is too precise, too specific, too cold for sentiment. The viewer feels the temperature of the air, the hardness of the frozen soil underfoot, the faint warmth at the horizon that is not yet spring but promises it. There is no human figure. There is no narrative. There is only the tree and the field, which are sufficient.

*New this session: Andrew Wyeth (1917--2009, American Realism) -- wyeth_tempera_drybrush_pass (166th distinct mode). THREE-STAGE TEMPERA SURFACE: (1) horizontally-biased asymmetric-blur luminance-domain chalk noise; (2) luminance-band-gated unsharp-mask midtone contrast; (3) sparse horizontal-blur fiber traces in tonal transition zones. Improvement: paint_tonal_key_pass -- luminance median analysis, sigmoid key remapping, Bayer-matrix micro-tonal dithering.*""",
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
    print(f"Posting session 255 to Discord channel {CHANNEL_ID}...")

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
