"""Post session 288 Discord painting to #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s288_peles_fury.png")
FILENAME   = "s288_peles_fury.png"

TEXT_BLOCKS = [
    """\
**Pele's Fury — Kīlauea at Midnight** -- Session 288

*Oil on linen -- Camille Pissarro mode -- 199th distinct mode -- Divisionist Shimmer + Structure Tensor*

**Subject & Composition**

A Hawaiian volcanic eruption viewed from a low vantage point on the lava field, looking directly toward the active caldera of Kīlauea. The volcanic cone dominates the canvas: a broad dark shield rising from the bottom edge to roughly one-third height. The composition divides into three registers -- foreground lava field (black, glowing cracks), the volcanic cone with channeled flows, and the midnight sky (deep indigo shot through by orange-crimson glow). The caldera mouth at the apex is the brightest point -- the source of all warmth and light.

Three lava flow channels cross the cone: one runs straight down from the caldera; two fork diagonally left and right like a delta dividing. Each flow is a river of orange-crimson light against dark rock -- white-yellow at the center where lava is hottest, cooling to rust-red at the margins. Stars pierce the indigo sky above; smoke plumes rise from the caldera and drift northeast. The foreground is cooled aa lava -- rough, dark, crossed by a network of glowing cracks where the crust has fractured and the molten interior is visible.""",

    """\
**The Environment**

SKY: Deep midnight indigo at the zenith -- the color of Hawaii at 2am, far from urban light. Moving toward the cone, the sky transitions through navy to deep crimson-purple. Approximately 200 stars pierce the indigo where the glow has not reached. No moon. Smoke and ash plumes drift northeast.

VOLCANIC CONE: A broad, gently sloping shield -- Kīlauea is not the steep stratovolcano of popular imagination. Dark volcanic basalt: deep blue-green-black, the color of fresh basalt by firelight. Surface featureless except where lava flows interrupt it.

CALDERA: Small circular incandescence at the summit -- white-yellow at its absolute center, immediately transitioning to orange, then crimson, then deep red-black of still-hot cooling lava. Warm amber glow radiates from the reflected heat.

FOREGROUND LAVA FIELD: Cooled aa lava -- rough, jagged, clinker-like. Near-black surface crossed by irregular glowing cracks. Larger fractures near the bottom edge show pools of deep orange-red molten lava.

SEA: Pacific Ocean occupies narrow strips on either side and at the base -- very dark, near-black, with faint orange reflections of the eruption in horizontal ripple bands.

**No human figure.** The volcano is the protagonist. Pele herself -- neither malevolent nor benevolent, simply creative and destructive in equal measure. The caldera glow is her eye; the lava flows are her reaching fingers.""",

    """\
**Technique & Palette -- Camille Pissarro (1830-1903)**

Pissarro was the Dean of the Impressionists -- the only artist to exhibit in all eight Impressionist exhibitions (1874-1886), patriarch who mentored Cézanne, Gauguin, Seurat, and Signac. Born in the Danish West Indies to a Sephardic Jewish father and Creole mother; lifelong anarchist. His Neo-Impressionist period (1885-1891) perfected divisionist optical mixing: discrete touches of pure pigment placed side-by-side, letting the eye blend them. Unlike Seurat's mechanical dot, Pissarro's touches retained organic tremor -- the surface shimmers rather than buzzes.

**The New Pass -- pissarro_divisionist_shimmer_pass (199th distinct mode)**

**(1) STOCHASTIC CHROMATIC NEIGHBOR BLEND:** K=6 random displacement vectors (dy, dx) within dot_radius. For each: sample shifted canvas via np.roll; color distance cdist = sqrt(sum(dC^2)); w = exp(-cdist/sigma); accumulated weighted average blended at shimmer_strength. **FIRST STOCHASTIC spatial sampling in engine** -- all 198 prior passes use deterministic kernels (Gaussian, median, Sobel).

**(2) COOL SAGE-GREEN SHADOW:** Cubic Hermite gate; push toward (0.36, 0.52, 0.38). Pissarro's characteristic shadow, distinct from Monet's violet or Hammershoi's blue-grey.

**(3) WARM AMBER HIGHLIGHT:** Push toward (0.94, 0.86, 0.58) warm straw-gold in high-lum zones.

**(4) SECTOR-MEDIAN HUE COHERENCE:** 12 hue sectors; compute median H per sector; pull H toward sector median weighted by saturation. **FIRST data-driven per-sector hue normalization** -- creates Pissarro's organic hue families within each zone.""",

    """\
**Improvement -- paint_structure_tensor_pass**

The structure tensor: first 2×2 gradient covariance matrix in the engine. J = [[G(Ix·Ix), G(Ix·Iy)], [G(Ix·Iy), G(Iy·Iy)]] where Ix, Iy are Gaussian gradient components.

**(1) STRUCTURE TENSOR:** Jxx = G_outer(Ix*Ix), Jxy = G_outer(Ix*Iy), Jyy = G_outer(Iy*Iy). **FIRST use of structure tensor** -- all prior passes use scalar G_norm or atan2 direction.

**(2) EIGENVALUE DECOMPOSITION:** lambda1, lambda2 from closed-form 2x2 symmetric formula. **FIRST eigenvalue analysis in engine.** coherence = ((L1-L2)/(L1+L2))^2 -- near 1 at consistent edges, near 0 at flat regions and isotropic noise.

**(3) COHERENCE-GATED USM:** Standard unsharp mask gated by coherence map as per-pixel opacity. **FIRST sharpening pass to gate on eigenvalue-derived coherence** -- genuine edges sharpen fully; flat areas and noise zones receive zero effect automatically.

**Mood & Intent**

Kīlauea has been erupting continuously since 1983 -- adding new coastline to Hawaii. This is not a disaster. It is creation. Pissarro's divisionist patience applied to volcanic fire: the same optical attention he brought to a peasant field in Normandy brought to a field of fire in the Pacific. Every dark mass carries the cool blue-green of basalt or the warm orange of reflected fire. Never pure black.

*New this session: Camille Pissarro (1830-1903) -- pissarro_divisionist_shimmer_pass (199th mode). Improvement: paint_structure_tensor_pass.*""",
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

    print(f"Posting s288 to channel {CHANNEL_ID}...")
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
