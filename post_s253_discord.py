"""Post session 253 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s253_kiefer_burning_rye.png")
FILENAME   = "s253_kiefer_burning_rye.png"

TEXT_BLOCKS = [
    """\
**Burning Rye Field, Margarete** -- Session 253

*Warm ashen ground, Anselm Kiefer Scorched Earth mode -- 164th distinct mode*

**Image Description**

A vast scorched rye field at ground level, looking straight toward a distant horizon that cuts the canvas at 38% from the top. The field dominates the lower two-thirds in deep converging perspective -- ploughed furrows radiating from a central vanishing point, each ridge alternating warm straw-gold with dark charred umber. Above the horizon: dense stratified ash sky descending from near-black at the crown to pale flax-white at the line of earth. A single charred post rises at left-center, vertical in the horizontal severity of the composition -- charcoal-grey, cracked with lead-sheet veining, standing at rest with the stillness of something that has survived by not resisting.""",

    """\
**The Figure**

The charred wooden post -- perhaps the remnant of a boundary stake, perhaps a crucifix reduced to matter -- is approximately two-thirds the canvas height, slightly left of center. Its surface is very dark: raw umber-black with traces of rust iron-oxide at the base where the grain of the original wood is still legible through the char. The lead crack veining runs across its mass in sinusoidal trajectories, the crackle lines of a surface that has been through fire and cooling. It stands with the absolute stillness of a monument. Emotional state: endurance, weight, the dignity of survival without redemption.

**The Environment**

The rye field is a complex layered surface. Deep foreground: near-black scorched earth where the furrow trenches are darkest, the ashen desaturation gradient pushing these lower zones toward charcoal. Mid-ground: ash-grey field with straw-fiber warm overlay at 14 degrees from horizontal -- the tilted sinusoidal texture activating across mid-luminance pixels to suggest dried stalks still holding the ghost of summer gold. Background: pale ashen horizon where the burned field dissolves into sky. The sky: horizontal bands of stratified grey, the lowest layers pale as dried bone, the highest layers dense grey-black as if still holding the weight of ash unsettled by the fire.""",

    """\
**Technique & Palette**

Anselm Kiefer (born 1945, Donaueschingen, Germany) Scorched Earth mode -- session 253, 164th distinct painting mode. Neo-Expressionism / Conceptual Art.

Stage 1, ASHEN FIELD DESATURATION GRADIENT: n_zones=10 horizontal depth strips from foreground to horizon. zone_frac = (zone_index / (n_zones-1)) * max_ash_blend (0.72) with luminance gating: dark pixels (lum < 0.35) receive extra darkening push of 0.18 toward charcoal; mid-tones (0.35--0.65) receive full zone-fraction ash blend; lights (lum ≥ 0.65) receive half blend. NOVEL: FIRST PASS to apply zone-partitioned luminance-gated simultaneous desaturation and darkening in a foreground-to-horizon depth gradient; no prior pass applies zone-indexed horizontal strip desaturation with differential treatment of dark/mid/light pixels simultaneously.

Stage 2, LEAD SHEET CRACK VEINING: 28 sinusoidal crack trajectories with random amplitude (4--28 px), frequency (0.005--0.020 cycles/px), phase, and y-origin. Pixels within crack_width=3 of each trajectory darkened at crack_depth=0.42 toward near-black (0.10, 0.09, 0.08), gated on lum < 0.55. NOVEL: FIRST PASS to generate directional vein-path cracks as sinusoidal trajectories with luminance-threshold discontinuity; prior crackle passes use isotropic Voronoi noise -- none draw structured sinusoidal directional vein paths.""",

    """\
Stage 3, STRAW FIBER WARM OVERLAY: Rotated sinusoidal fiber texture at straw_angle=14°. For each pixel: u = x·cos(14°) + y·sin(14°); fiber = 0.5 + 0.5·sin(2π·u/8). Applied at fiber peaks (fiber > 0.55) where straw_lo=0.28 ≤ lum ≤ straw_hi=0.62, blending straw_gold (0.76, 0.68, 0.28) at fiber_strength=0.42. NOVEL: FIRST PASS to apply a tilted (non-orthogonal) single-direction chromatic sinusoidal fiber grid with warm straw-gold coloring gated on mid-luminance; s252 surface tooth uses orthogonal H×V for achromatic canvas texture -- no prior pass uses a rotated axis with chromatic hue blending.

**Impasto Ridge Cast improvement (session 253):** Sobel-derived gradient magnitude identifies thick impasto ridges. Shadow cast at light_angle=145° (upper-left source): shadow_offset=5 pixels, shadow_strength=0.30. Catch-light highlight on light-facing ridge edge at highlight_strength=0.14. ridge_pixels=179,210; shadow_coverage=19.5%. NOVEL: FIRST PASS to synthesize directional cast-shadows from a ridge map AND paired catch-light highlights as three-stage impasto depth simulation.

**Palette:** Near-black char (0.14/0.12/0.10) -- Scorched umber (0.26/0.22/0.18) -- Ash grey (0.52/0.48/0.44) -- Pale ashen horizon (0.82/0.78/0.70) -- Straw warm gold (0.76/0.68/0.28) -- Lead grey (0.44/0.42/0.40) -- Rust iron trace (0.58/0.32/0.16) -- Cold sky white (0.88/0.86/0.82)""",

    """\
**Mood & Intent**

"Your golden hair, Margarete / your ashen hair, Shulamit" -- Paul Celan, *Death Fugue*. The rye field is the hair of the dead woman, the burning both literal (a field after harvest fire) and historical (a culture consuming itself, a war consuming a landscape, an atrocity consuming its own record). Kiefer assigned specific weight to German landscape that refuses pastoral comfort: beautiful and terrible simultaneously, scorched by history that cannot be undone, the field as agricultural fact and wound.

The viewer should feel the specific quality of cold after fire -- not warmth, not comfort, but the residual warmth of still-hot ash and the incoming cold of the grey sky pressing down. The post is not a symbol of hope. It is a symbol of having survived without that meaning anything beyond the bare fact of standing. Grief without sentimentality. Endurance without redemption. The painting does not console.

*New this session: Anselm Kiefer (1945–, German Neo-Expressionism) -- kiefer_scorched_earth_pass (164th distinct mode). THREE-STAGE SCORCHED FIELD: zone-partitioned luminance-gated ash gradient + sinusoidal lead-crack vein network + tilted straw-fiber warm chromatic overlay. Improvement: paint_impasto_ridge_cast_pass -- Sobel ridge detection, directional cast-shadow displacement, catch-light on light-facing ridge edge.*""",
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
    print(f"Posting session 253 to Discord channel {CHANNEL_ID}...")

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
