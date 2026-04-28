"""Post session 223 painting to Discord #gustave channel."""

import requests
import os
import time

TOKEN = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"
HEADERS = {
    "Authorization": f"Bot {TOKEN}",
    "User-Agent": "DiscordBot (https://github.com/gr84x/painting-pipeline, 1.0)",
}

MSG1 = (
    '**Session 223 — "The Last Light of Winter"**\n'
    "*Helene Schjerfbeck (1862–1946) — 134th distinct mode: schjerfbeck_sparse_portrait_pass*\n\n"
    "**Subject & Composition:** A single elderly Finnish woman in close three-quarter portrait, "
    "viewed from slightly above and fractionally to the right. The composition is tight — barely "
    "any air above the white hair, the dark garment vanishing at the bottom edge. She is the only subject.\n\n"
    "**The Figure:** Age approximately eighty-five. Face in near-profile, tilted downward and to the left. "
    "Sparse white hair pulled back, a few strands at the temple. Eyes closed or cast far down — the "
    "emotional state is interior stillness, not grief or peace, but the specific quality of someone who "
    "has outlasted most of the things that once mattered. The skin has the translucence of advanced age: "
    "thin over the cheekbones, nearly papery at the temple."
)

MSG2 = (
    "**The Environment:** The background is almost nothing — a pale grey-white plane with the barest "
    "suggestion of a tall window at the upper right, bleeding cold diffuse winter light. The boundary between "
    "background and figure is deliberately unclear at the periphery. Only the central oval of the face is "
    "fully articulated. Hair, ears, collar dissolve toward the edges. No furniture is visible.\n\n"
    "**Technique & Palette:** Helene Schjerfbeck style — *schjerfbeck_sparse_portrait_pass* (134th mode). "
    "Peripheral dissolution blurs background outward from a central anchor; tonal flattening compresses the "
    "face into soft planes; a Nordic cool wash bleaches toward chalk-white; a thin veil lifts the dark tones "
    "slightly. *halation_glow_pass* (session 223 improvement) creates a warm luminous bloom from window light "
    "landing on her temple and brow.\n\n"
    "Palette: chalk-white flesh · warm ochre mid-tone · grey-brown shadow · deep charcoal "
    "· warm bone highlight · cool blue-grey dissolved periphery · raw umber structural accent"
)

MSG3 = (
    "**Mood & Intent:** About the quality of light at the end of a life — not dramatic, not sorrowful, "
    "simply present. The face reduced to its essential planes is not weakness; it is something distilled. "
    "The halation around her lit temple is the specific cold luminosity of Scandinavian winter: a light that "
    "reveals without warming, that shows a face as it is, as it always will have been. Walk away with the "
    "feeling of having stood in a very quiet room."
)


def post_msg(content):
    r = requests.post(
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        headers=HEADERS,
        json={"content": content},
    )
    msg_id = r.json().get("id", "error")
    print(f"  [{r.status_code}] message id: {msg_id}")
    time.sleep(0.7)
    return msg_id


def post_image(filepath):
    with open(filepath, "rb") as f:
        img_data = f.read()
    files = {"file": (os.path.basename(filepath), img_data, "image/png")}
    r = requests.post(
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        headers=HEADERS,
        files=files,
    )
    msg_id = r.json().get("id", "error")
    print(f"  [{r.status_code}] image id: {msg_id}")
    return msg_id


if __name__ == "__main__":
    print("Posting session 223 painting to Discord #gustave...")
    id1 = post_msg(MSG1)
    id2 = post_msg(MSG2)
    id3 = post_msg(MSG3)
    id4 = post_image("s223_last_light.png")
    print(f"\nDone. Message IDs: {id1} / {id2} / {id3} / {id4}")
