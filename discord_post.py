"""Post painting to Discord #gustave channel via Red bot."""
import subprocess
import json
import sys
import base64

TOKEN  = ""  # set via DISCORD_TOKEN env var or fill in before running
CHANNEL = "1497780916418908341"
IMAGE_PATH = r"C:\Source\painting-pipeline\owl_gargoyle_watcher.png"

TEXT = (
    "**The Watcher** — Session 208\n\n"
    "*Oil on linen, expressionist nocturne*\n\n"
    "**Image Description**\n\n"
    "A great horned owl perches motionless on the weathered crown of a moss-covered "
    "stone gargoyle jutting from a gothic cathedral rooftop, viewed from a three-quarter "
    "angle below-left. The owl dominates the upper canvas — wings folded, body upright "
    "in absolute stillness, facing the viewer with burnished gold irises and jet-black "
    "pupils. An ancient, penetrating gaze.\n\n"
    "The owl's plumage: dense barred amber-gold and raw umber, the breast warm and "
    "striated, the dark mantle edged in silver moonlight along its upper-right silhouette. "
    "Throat disc: pale ivory. A rust-orange facial ring circles the eyes.\n\n"
    "The gargoyle and stone parapet are dark blue-grey, the upper edge brilliant where "
    "the full moon catches from the upper right. Sky descends from luminous silver-white "
    "near the moon through deep Prussian blue. Faint cirrus wisps. Below: the city far "
    "beneath is a warm amber haze of distant lights rising in fog around the cathedral's stone.\n\n"
    "**Technique:** Munch-influenced expressionist atmospheric · Rembrandt chiaroscuro\n"
    "**Palette:** Prussian blue · ivory black · raw umber · burnt sienna · naples yellow · moonlit silver\n"
    "**Mood:** Solitary nocturnal wisdom — patient, ageless, detached from the human world below\n"
    "**Passes:** underpainting → block_in → build_form → munch_anxiety_swirl_pass → place_lights → glaze\n\n"
    "*New this session: Franz Kline (Abstract Expressionism) — kline_gestural_slash_pass "
    "(119th distinct mode). DIRECTIONAL CALLIGRAPHIC SWEEP FIELD: structural image axes "
    "detected from luminance gradient orientation, swept as pressure-modulated mega-strokes "
    "with Gaussian edge bleed.*"
)

payload = json.dumps({"content": TEXT})

# Send text message
result = subprocess.run(
    [
        "curl", "-s", "-X", "POST",
        f"https://discord.com/api/v10/channels/{CHANNEL}/messages",
        "-H", f"Authorization: Bot {TOKEN}",
        "-H", "Content-Type: application/json",
        "-d", payload,
    ],
    capture_output=True, text=True
)
resp = json.loads(result.stdout)
print(f"Text message ID: {resp.get('id', 'ERROR: ' + str(resp))}")

# Send image as file attachment
result2 = subprocess.run(
    [
        "curl", "-s", "-X", "POST",
        f"https://discord.com/api/v10/channels/{CHANNEL}/messages",
        "-H", f"Authorization: Bot {TOKEN}",
        "-F", f"files[0]=@{IMAGE_PATH};filename=the_watcher.png",
        "-F", 'payload_json={"attachments": [{"id": 0, "filename": "the_watcher.png"}]}',
    ],
    capture_output=True, text=True
)
resp2 = json.loads(result2.stdout)
print(f"Image message ID: {resp2.get('id', 'ERROR: ' + str(resp2))}")
