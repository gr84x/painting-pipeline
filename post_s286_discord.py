"""Post session 286 Discord painting to #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s286_canal_dusk.png")
FILENAME   = "s286_canal_dusk.png"

TEXT_BLOCKS = [
    """\
**The Canal at Dusk** -- Session 286

*Oil on linen -- Eugene Carriere mode -- 197th distinct mode -- Smoky Reverie + Tonal Rebalance*

**Subject & Composition**

A solitary woman stands at the stone edge of a narrow urban canal at dusk, viewed from slightly behind and to her left. She holds a loose bunch of cut irises at her side -- a detail that rewards close looking. The canal runs horizontally across the middle of the frame, its dark water catching broken amber reflections from gas lamps and lit windows on the far bank. The far-bank buildings rise as dark irregular masses above, six to eight windows lit warm amber against the evening. Bare pollarded willows arc their branch tracery against the grey sky at left. The foreground is wet cobblestones, rain-slick, picking up the amber reflections of the single gas lamp at the upper right. The figure is positioned center-left, smaller than the architecture -- anonymous, chosen, still.""",

    """\
**The Figure & Environment**

The woman in the long dark coat has stopped here deliberately. Her posture is chosen stillness, not sadness -- she is looking at the water, pausing in the city's anonymous evening. Her felt hat brim curves slightly over her hair. The irises she carries are a private gesture: beauty chosen for no audience.

The canal water is near-black except where gas-lamp light creates a smear of amber -- broken by gentle movement into irregular comma-shapes of warm gold. The far-bank window reflections add wavering vertical columns that dissipate toward the near bank. The tenements on the far bank are dark warm umber-grey, their facades lit only by the warm amber rectangles of windows. Between the buildings: narrow dark passages. The building edges dissolve into the dusky sky -- rooflines barely distinguishable from the grey above.

**Technique & Palette -- Eugene Carriere (1849-1906)**

Carriere's smoky reverie technique. The palette is built entirely from warm bistre-brown tones: deep warm umber, amber-ochre, dark sienna, and lamp amber against near-dark. No cool tones anywhere -- even the canal's dark water carries warmth from its reflected lamp light.""",

    """\
**The New Pass -- carriere_smoky_reverie_pass (197th distinct mode)**

Four stages of novel warm-monochrome mathematics:

**(1) WARM SEPIA TINT:** L = luminance; R_s = L x sepia_r (0.58), G_s = L x sepia_g (0.44), B_s = L x sepia_b (0.28); blend at sepia_strength=0.72. First pass to apply luminance-scaled warm tint uniformly across all zones -- no luminance gating. Prior warm passes are zone-gated (repin midtone bell, grosz colour-dominance, s284 HSV hue rotation).

**(2) EXPONENTIAL SHADOW MERGE:** gate = exp(-L / tau) where tau=0.26. Push toward deep warm umber (0.12, 0.08, 0.05). First use of negative exponential exp(-L/tau) as a luminance zone gate. Prior shadow gates use hard threshold (repin), power law (grosz gamma L^0.80), or linear ramp (s281 shadow_temperature).

**(3) GRADIENT-MAGNITUDE SOFT EDGE DISSOLUTION:** weight = clip(sqrt(G_norm) x strength, 0, 1); output = canvas x (1-weight) + Gaussian(canvas) x weight. First pass to use G_norm as a blur WEIGHT (MORE blur at HIGH gradient zones). All prior edge passes sharpen at high G_norm -- this inverts that, dissolving the very edges.

**(4) PERIPHERAL EDGE FADE:** d_edge = min(x, W-1-x, y, H-1-y) / (min(W,H) x 0.5). First use of minimum-distance-to-canvas-boundary as zone gate (Chebyshev distance). Distinct from focal_vignette_pass (s278) which uses L2 radial distance from detected luminance centroid.""",

    """\
**Improvement -- paint_tonal_rebalance_pass**

Adaptive sigmoidal tone mapping with percentile auto-levels and luminance-ratio chromatic preservation. Four novel stages:

**(1) PERCENTILE AUTO-LEVELS:** Find P5 and P95 of luminance histogram. L_norm = clip((L - P5) / (P95 - P5), 0, 1). First per-image adaptive tonal range detection -- prior passes use fixed parameters, not per-image percentile measurement.

**(2) HYPERBOLIC TANGENT S-CURVE:** L_curve = 0.5 + 0.5 x tanh(k x (L_norm x 2 - 1)) / tanh(k), k=1.55. Passes through (0,0), (0.5,0.5), (1,1) exactly. First use of tanh() as a tone curve -- prior S-curves use polynomial zone masks or power-law gamma, not tanh.

**(3) LUMINANCE-RATIO CHROMATIC PRESERVATION:** scale = L_curve / max(L_norm, eps). R_out = clip(R x scale, 0, 1). Preserves R:G:B ratios (hue angle) exactly while remapping luminance. First multiplicative luminance ratio in engine -- prior adjustments are additive blends.

**(4) HIGHLIGHT SHOULDER:** soft clamp x/sqrt(1+x^2) above shoulder_start=0.88. First smooth soft-clipping knee in engine -- prior passes use hard clip(0,1).

**Mood & Intent**

Urban solitude at the hour when a life pauses in public space without demand or expectation. The canal becomes a mirror not of the buildings across it but of the woman's interior state -- dark, still, lit from within. The mist softens everything; the Carriere technique makes the familiar strange. The irises she carries: beauty for no audience.

*New this session: Eugene Carriere (1849-1906, French Symbolist) -- carriere_smoky_reverie_pass (197th distinct mode). Improvement: paint_tonal_rebalance_pass -- percentile auto-levels + tanh S-curve + luminance-ratio preservation + soft highlight shoulder.*""",
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
    for i, block in enumerate(TEXT_BLOCKS):
        if len(block) > 2000:
            print(f"ERROR: Block {i} is {len(block)} chars (limit 2000)")
            sys.exit(1)
        else:
            print(f"Block {i}: {len(block)} chars -- OK")

    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image not found at {IMAGE_PATH}")
        sys.exit(1)

    print(f"Posting s286 to channel {CHANNEL_ID}...")
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
