"""Post session 259 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s259_rysselberghe_regatta.png")
FILENAME   = "s259_rysselberghe_regatta.png"

TEXT_BLOCKS = [
    """\
**Regatta at Nieuwpoort, Flood Tide** -- Session 259

*Warm linen canvas, Théo van Rysselberghe Chromatic Dot Field mode -- 170th distinct mode*

**Image Description**

Seven sailing dinghies mid-race on the Belgian North Sea, viewed from a low angle at water level, slightly elevated port-side. The boats spread in a loose diagonal cluster from lower-left to upper-right -- the nearest boat fills the lower-left quarter, large and immediate; the farthest are small shapes dissolving into light near the upper-right horizon. Belgian North Sea coast near Nieuwpoort, late morning flood tide, midsummer.""",

    """\
**The Figure**

The nearest boat: a small wooden racing dinghy with a white mainsail and red jib, heeled well over, crew of two -- one hiking out hard over the windward rail (silhouette, male, strain in shoulders and arms), one at the tiller. The sails are taut. Behind it, six more boats at varying distances -- progressively smaller, sails lightening and fragmenting into pure colour-point values as they recede. The farthest read as three white triangles and two coloured triangles against the sky.

**The Environment**

Sky: intense cobalt blue overhead, paling through cerulean to a warm luminous yellow-white at the horizon, where summer haze blurs sea and sky. The sea: chopped into short wavelets in the foreground -- deep viridian-cobalt in the troughs, cadmium-yellow highlights on wave crests. Middle distance: pure cobalt. Far distance: silvery blue-white, barely distinguishable from the hazy sky. A grey-ochre breakwater strip sits at the horizon.""",

    """\
**Technique & Passes**

Rysselberghe Chromatic Dot Field mode -- session 259, 170th distinct mode.

The rysselberghe_chromatic_dot_field_pass applies three stages after the regatta scene is blocked in. Stage 1 (Spectral Hue Saturation Boost): for each pixel, its angular distance to the nearest spectral primary (red/yellow/green/cyan/blue/violet) is computed; saturation is boosted proportionally -- pixels near a spectral primary receive the strongest push, pixels mid-way between primaries receive none. The viridian sea becomes more purely viridian; the cobalt sky more purely cobalt; the cadmium sails more purely yellow. This models van Rysselberghe's practice of selecting pure unmixed pigment for each dot unit. Stage 2 (Optical Luminosity Enhancement): highly saturated pixels -- the pure chromatic dot zones -- receive a saturation-gated luminance lift, approximating the higher apparent luminosity of optical colour mixing versus physical pigment blending. Stage 3 (Dot Field Texture): a jittered grid of Gaussian-profile luminance bumps with alternating checkerboard sign stamps the characteristic micro-modulation of discrete hand-applied paint marks onto the canvas surface.

Atmospheric Recession improvement (session 259): the new paint_atmospheric_recession_pass applies three physically-motivated aerial perspective cues along the top-to-horizon recession axis -- luminance haze lift, HSV saturation reduction, and Rayleigh-scatter cool RGB shift -- each proportional to a linear depth-weight field. The boat fleet dissolves from full chromatic intensity in the foreground to pale spectral ghosts at the horizon.""",

    """\
**Mood & Intent**

Speed, light, chromatic exuberance. Van Rysselberghe saw the Belgian coastal regattas as a supreme colour problem: the sails as pure colour-units in an all-encompassing field of spectral light; the water as the most complex chromatic phenomenon in painting, shifting from viridian to cobalt to silver in the span of a few metres.

The viewer should walk away saturated with light -- from above, reflected from below, thrown by the sails -- and with the mild dizziness of following the fleet into the haze. The diagonal composition pulls the eye relentlessly toward the horizon, where the last two boats have almost dissolved. To see them is to understand what van Rysselberghe understood: at a certain distance, a painting becomes pure colour and light, and the object that once carried it vanishes.

*New this session: Théo van Rysselberghe (1862-1926, Belgian Neo-Impressionist/Divisionist) -- rysselberghe_chromatic_dot_field_pass (170th distinct mode). THREE-STAGE NEO-IMPRESSIONIST POINTILLIST CHROMATIC FIELD: (1) hue-angle-dependent spectral-primary proximity saturation boost (pure pigment selection model); (2) saturation-gated luminance lift (optical mixing luminosity gain); (3) jittered Gaussian-profile dot grid with alternating checkerboard sign (paint mark discretisation). Improvement: paint_atmospheric_recession_pass -- linear depth-weight field driving luminance haze lift + HSV saturation reduction + Rayleigh-scatter cool RGB shift as three-stage aerial perspective simulation.*""",
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
    print(f"Posting Session 259 to Discord channel {CHANNEL_ID}...")
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
