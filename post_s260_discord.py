"""Post session 260 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

sys.stdout.reconfigure(encoding="utf-8")

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s260_foujita_woman_cat.png")
FILENAME   = "s260_foujita_woman_cat.png"

TEXT_BLOCKS = [
    """\
**Woman with Cat, Afternoon Window** -- Session 260

*Warm linen-ivory canvas, Tsuguharu Foujita Milky Ground Contour mode -- 171st distinct mode*

**Image Description**

A single young woman, three-quarter view from the front-left, seated in a low wooden chair in a small Parisian apartment room. She occupies the left two-thirds of the composition, from just below waist level to just above her loosely-pinned dark hair. Her gaze is directed toward a grey tabby cat sitting on a white-painted windowsill in the upper-right quadrant. The cat is smaller, occupying perhaps a sixth of the total canvas area -- present but subsidiary. The eye traces a gentle diagonal from the woman's loosely-held hands in the lower center to the cat's watchful amber eyes at the upper right. A round pedestal side table enters from the lower-right corner, bearing a small ceramic cup and a folded journal.""",

    """\
**The Figure**

The woman is in her late twenties. She wears a loose, slightly oversized white cotton blouse with a small stand collar and a fine stripe pattern barely visible in the fabric -- the kind of blouse that has been washed too many times and has a familiar softness. Her dark hair is loosely piled up, several strands escaped at her nape and temple. Her skin is the defining element: the characteristic Foujita milky ivory -- luminous, pearlescent, neither warm nor cool but both simultaneously, as if lit from within. Her hands rest loosely in her lap, fingers lightly laced. Her face is turned so the viewer sees her left cheek and the bridge of her nose in three-quarter profile; her eyes are directed toward the cat. Her emotional state is one of quiet, suspended attention -- the particular absorption of watching an animal do something unremarkable.

**The Environment**

A Parisian apartment room, third arrondissement, early afternoon in March. The light comes from a single tall window with a white-painted wooden frame, positioned in the upper-right of the composition. The window glass is slightly dusty, softening the exterior light into a diffuse, cool-pale wash. On the windowsill sits the grey tabby cat -- compact, upright, facing the woman with amber-yellow eyes half-slitted in the afternoon light. The walls are papered with a faded floral pattern in muted ochre and dusty rose on a cream ground -- the wallpaper has faded unevenly, darker near the corners, lighter near the ceiling and window. The floor is warm-brown parquet. A round side table in the lower right bears a small ceramic cup and a folded journal.""",

    """\
**Technique & Passes**

Foujita Milky Ground Contour mode -- session 260, 171st distinct mode.

The foujita_milky_ground_contour_pass applies three stages after the scene is blocked in. Stage 1 (Milky Ivory Ground Lift): pixels above an ivory_threshold of 0.65 are blended toward the target ivory color (0.97, 0.95, 0.88) with a weight proportional to how far their luminance exceeds the threshold. This concentrates the warm ivory warmth in the woman's skin highlight passages, the cotton blouse, and the white windowsill, giving them the characteristic Foujita porcelain luminosity. Stage 2 (Japanese Ink Contour Tracing): a Sobel-based gradient magnitude is computed, normalized, and any pixel above contour_threshold=0.07 is darkened toward near-black by contour_darkness=0.65 -- producing hair-thin dark contours at all significant tonal transitions, modeling Foujita's sable-brush ink lines. Stage 3 (Directional Micro-Texture Hatching): local Sobel gradient orientation (atan2(gy, gx)) is used to compute per-pixel hatch phase via (-sin(angle)*x + cos(angle)*y), creating sinusoidal micro-texture marks parallel to iso-luminance contours across a bell-function pale-zone mask centered at lum=0.75. This produces the cat-fur and skin-surface fine mark field of Foujita's mature work.

Sfumato Contour Dissolution improvement (session 260): The paint_sfumato_contour_dissolution_pass softens detected edge zones using a Gaussian-pre-smoothed Sobel edge map as a spatially-selective blur mask. Edge zones receive a blend toward a Gaussian-blurred version (blur_sigma=2.2, dissolve_strength=0.60); shadow-side edges are additionally deepened by a sfumato_zone * shadow_bias * (1-lum) weight. Applied at opacity=0.55, it dissolves the window-wall boundary and the hair-background transition, giving the background Leonardo's sfumato quality of emergence rather than definition.""",

    """\
**Mood & Intent**

The image carries the particular quality Foujita found in domestic Paris: a moment sealed in amber light, existing outside narrative time. The woman does not look at the viewer -- she is absorbed in watching her cat, which watches her back. This small circuit of attention, between two living creatures in a warm room, is the entire content of the picture. The milky ivory of her skin against the faded wallpaper creates a tonal argument about presence and memory: she glows while the room recedes. The contour lines, drawn with the precision and restraint of Japanese calligraphy, give the image its structural dignity -- nothing is vague, nothing is approximate, and yet nothing is harsh. The viewer is intended to leave the picture feeling that they have seen something actual: not a symbol or a statement, but the simple fact of an afternoon, a woman, and a cat.

*New this session: Tsuguharu Foujita (1886-1968, Japanese-French, École de Paris) -- foujita_milky_ground_contour_pass (171st distinct mode). THREE-STAGE JAPANESE-FRENCH MILKY IVORY TECHNIQUE: (1) highlight-targeted warm ivory tone drift proportional to luminance above threshold (Foujita milky ground lift); (2) Sobel-gradient contour map darkened as Japanese-ink sable line simulation (structural ink contour); (3) orientation-aligned sinusoidal hatching in pale zones derived from local Sobel gradient angle (directional micro-texture). Improvement: paint_sfumato_contour_dissolution_pass -- Gaussian-pre-smoothed Sobel edge map driving spatially-selective per-pixel blur (sfumato edge dissolution) with sfumato-zone-gated luminance-inverse shadow deepening (Leonardo shadow recession model).*""",
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
    print(f"Posting Session 260 to Discord channel {CHANNEL_ID}...")
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
