"""Post session 265 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s265_berlin_rain.png")
FILENAME   = "s265_berlin_rain.png"

TEXT_BLOCKS = [
    """\
**Berliner Strassenszene im Regen** -- Session 265

*Prussian dark ground, Lesser Ury Nocturne mode -- 176th distinct mode*

**Image Description**

A solitary woman stands at the threshold of a Berlin cafe awning on a wet November evening, 1900. She occupies the lower-left third of the canvas, silhouetted in three-quarter profile against the warm amber glow of the cafe's street-level windows. The viewpoint is at street level, slightly below the figure's eye-line, as if the painter stands a few paces away on the opposite pavement. A wrought-iron gas lamp post rises vertically in the left quarter of the canvas, its globe casting the nearest amber halo. The upper 40% of the canvas is the deep prussian-blue night sky and dark building silhouettes. The lower 35% is wet cobblestone pavement, the stones' dark surfaces reading as a fractured mirror.""",

    """\
**The Figure**

A young woman, perhaps 26, in a dark charcoal-green evening coat that reaches her ankles. A small dark hat. Her face is turned three-quarters away from the viewer -- we see the line of her jaw, the pale column of her neck, the suggestion of her profile. Her right hand, gloved, is raised slightly at her side -- not hailing, not gesturing, simply present. Her posture is upright, undefeated by the rain and cold. Her emotional state: a specific urban solitude -- the state of being alone in public, surrounded by warmth you are not quite inside. She does not want rescue. She is simply here, at the edge of the light, waiting for something unnamed. Her silhouette is the darkest element in the composition; the cafe light behind her creates a faint warm rim along her left shoulder and hat brim.

**The Environment**

A Berlin street in the Mitte district, a rainy November night. Behind the figure: two tall rectangular cafe windows, their amber interiors visible as warm diffuse glow. The facade is prussian dark stone; a horizontal awning runs just above. To the left: the gas lamp post, a slim dark vertical line topped by the amber globe and its halo of warm dispersed light. The right half recedes deeper into prussian shadow -- the street curves away, a second lamp barely visible at mid-distance, smaller, cooler, implying recession.

The foreground cobblestones: each stone slightly different in its degree of wet-sheen. The amber lamp reflection in the pavement directly below the post: a bright oval of warm reflected light that breaks and elongates downward. The cafe window reflections in the pavement: two dim amber rectangles, distorted and elongated horizontally by the water film.""",

    """\
**Technique & Passes**

Lesser Ury Nocturne mode -- session 265, 176th distinct mode.

Stage 1 (WET PAVEMENT VERTICAL MIRROR REFLECTION): The upper 42% of the canvas is flipped vertically and composited into the lower 38% (pavement zone). Key novelty: asymmetric 2D Gaussian blur (H-sigma=20.0, V-sigma=4.0) elongates warm lamp glow and window rectangles into horizontal rain-streaked reflections. Attenuated to 35% of source luminance (wet stone absorbs ~65%). Composited at 0.65 opacity.

Stage 2 (GAS-LAMP AMBER CORONA): Pixels above lum 0.60 receive warm-amber hue shift (R+0.16, G+0.05, B-0.14 × lamp_mask). The warm excess is Gaussian-blurred (sigma=24.0) to simulate gaslight spreading into atmospheric haze -- the Ury amber halo extending 80-120px around each source. ~25,769 lamp pixels.

Stage 3 (PRUSSIAN BLUE NIGHT-SHADOW COOLER): Pixels below lum 0.30 receive differential per-channel scaling: R×0.72, G×0.80, B+0.025 -- shifting shadows toward prussian blue / indigo. The characteristic Ury contrast: warm amber against cold dark. ~1,068,204 shadow pixels.""",

    """\
**Technique (continued)**

Pipeline improvement s265 (WET SURFACE GLEAM): `paint_wet_surface_gleam_pass` extracts a luminance-threshold specular mask (spec_threshold=0.68), applies 1D Gaussian blur along the vertical axis (axis=0, sigma=22.0) to elongate bright sources into downward trails, then composites a warm per-channel gleam lift (R×0.30, G×0.22, B×0.12). This places warm, vertically-elongated gleam streaks from the lamp globe and window highlights -- the physical specular reflection on rain-wet cobblestones.

Full pipeline: tone_ground (prussian 0.05/0.06/0.16) → underpainting (×2) → block_in (×2) → build_form (×2) → place_lights (×2) → paint_wet_surface_gleam_pass → ury_nocturne_reflection_pass → paint_atmospheric_recession_pass → paint_shadow_bleed_pass → paint_granulation_pass""",

    """\
**Mood & Intent**

The painting carries the particular quality Ury found in the new Berlin: the modern city as a space of beautiful, chosen aloneness. The woman is not lost -- she is at the edge of the light, which is where interesting things happen. The amber warmth of the cafe is behind her, real and present, but she faces the prussian dark of the street.

The wet pavement mirrors everything above it, making the street both more complex and more melancholy -- every lamp doubled, every figure duplicated in distortion below their feet. The viewer should feel the specific quality of November rain in a city at night: not cold despair but alert solitude, the city's beauty visible precisely because the weather has emptied the street of the comfortable and the incurious.

*New this session: Lesser Ury (1861-1931, German, Impressionism) -- ury_nocturne_reflection_pass (176th distinct mode). THREE-STAGE BERLIN NOCTURNE: (1) upper-canvas vertical flip + asymmetric Gaussian blur (H=20, V=4) + attenuation composited into lower pavement zone to simulate wet cobblestone mirror reflections; (2) luminance-gated warm-amber hue shift diffused via Gaussian corona simulating gaslight atmospheric halos; (3) differential per-channel shadow scaling (R×0.72, G×0.80, B+0.025) to cool darks toward prussian blue. Improvement: paint_wet_surface_gleam_pass -- 1D vertical Gaussian streak from specular mask + warm per-channel gleam simulating rain-wet surface light trails.*""",
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
    print(f"Posting Session 265 to Discord channel {CHANNEL_ID}...")
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
