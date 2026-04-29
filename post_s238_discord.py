"""Post session 238 painting to Discord #gustave channel."""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s238_feininger_harbor.png")

IMAGE_DESCRIPTION = """**The Crystalline Harbor** — Session 238

*Misty slate imprimatura, Feininger Crystalline Prism mode*

**Image Description**

A small gaff-rigged sloop sits anchored on a calm pewter harbor at early dawn, seen in three-quarter view from slightly above. The boat is centered in the composition: a warm ochre-cream hull with weathered planking, a tall dark mast with a slight aft rake, the mainsail and gaff sail furled tightly on their spars, thin stays and shrouds forming delicate geometric rigging against the sky. The boom extends aft; the cabin deckhouse is a small ochre rectangle midship. The hull reflects in the still water below — slightly cooler and more desaturated than the hull itself, the mast's dark line extending briefly into the mirror surface.

The sky occupies the upper half of the canvas: deep prussian cobalt at the top softening to cool slate-blue in the middle, then warming to amber-ochre at the horizon — the classic Feininger progression from cool atmospheric depth to warm earthbound light. Across this sky, crystalline angular cloud planes are layered in overlapping diagonal slabs of slate violet and cool grey, each plane with a slightly different hue, each edge sharp where it meets the adjacent tone. The cloud architecture has the angular precision of crystal faces: no soft cumulus rounding, only planar geometric volumes of atmospheric colour. Two small distant sails appear as dark triangular silhouettes on the horizon, their masts hairline verticals against the amber glow.

The water — lower half — is pewter grey-green, flat as glass. Angular faceted planes of reflected colour tile the surface: cool slate-blue panels alternate with warm amber-ochre panels, each panel a slightly different geometric zone of the horizon's light. Near the horizon the water glows warmest; toward the foreground it deepens to cold steel. A thin band of luminous mist softens the exact point where sky meets water. Eight foreground ripple lines mark the water surface in gentle sinusoidal waves, alternating cool and warm in Feininger's signature rhythmic geometry.

The Feininger Crystalline Prism pass (149th mode) does its defining work across the entire canvas: gradient direction angles are coherently blurred via circular Gaussian averaging (atan2 of blurred cosine/sine), then mapped through a cyclic warm/cool chromatic function. Each coherent angular zone of the image — a cloud plane, a sky gradient zone, a water facet, the hull's lit and shadow faces — receives a prismatic chromatic tilt that reinforces the angular planar structure. Cloud faces angled toward the horizon pick up amber warmth; faces angled skyward receive cobalt coolness. The water facets alternate warm and cool in the same angular logic. The split toning improvement deepens the shadow-cool/highlight-warm contrast structure throughout.

**Technique:** Lyonel Feininger Crystalline Prism (149th distinct mode)
**Palette:** Prussian cobalt blue · amber ochre gold · pewter grey-green · slate violet · warm ochre hull · ivory cream sails · near-black mast · misty horizon
**Mood:** Pre-dawn harbor stillness — the viewer should feel the cold, lucid air before wind, the crystalline geometric clarity of water at rest, and the meditative geometry of a vessel waiting for the day. A Bauhaus quiet, everything reduced to its essential planar form.
**Passes:** tone_ground (misty slate) → underpainting → block_in × 2 → build_form × 2 → place_lights → feininger_crystalline_prism_pass → paint_split_toning_pass → diffuse_boundary_pass → glaze (cobalt wash) → vignette

*New this session: Lyonel Feininger (1871-1956, Expressionism/Cubism/Bauhaus) — feininger_crystalline_prism_pass (149th distinct mode). TWO-STAGE CRYSTALLINE FACET SIMULATION: (1) Coherent angle map via circular Gaussian averaging — gradient direction atan2(sy,sx) averaged through cos/sin decomposition — FIRST pass in project to use gradient DIRECTION (not magnitude) as primary variable; FIRST circular/angular spatial average; (2) Prismatic cyclic warm/cool chromatic mapping: warm_cool=cos(angle×cycles) — FIRST direction-angle cyclic chromatic modulation. Improvement: paint_split_toning_pass — simultaneous opposing dual-zone tinting (shadows cool B+/R−, highlights warm R+/B−) — FIRST pass to apply two opposing colour shifts to two distinct luminance zones simultaneously.*"""

FILENAME = "s238_feininger_harbor.png"


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
    print(f"  Text message ID: {msg_id}")
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
    print(f"  Image message ID: {msg_id}")
    return msg_id


def split_text(text: str, max_len: int = 1900) -> list:
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        split_at = text.rfind("\n\n", 0, max_len)
        if split_at < 0:
            split_at = text.rfind("\n", 0, max_len)
        if split_at < 0:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"ERROR: Image not found at {IMAGE_PATH}")
        sys.exit(1)

    print("Posting session 238 to Discord #gustave...")
    print(f"Channel: {CHANNEL_ID}")
    print(f"Image: {IMAGE_PATH}")

    chunks = split_text(IMAGE_DESCRIPTION)
    msg_ids = []
    for i, chunk in enumerate(chunks):
        print(f"Posting text chunk {i+1}/{len(chunks)}...")
        mid = post_text(chunk)
        msg_ids.append(mid)
        time.sleep(0.8)

    print("Posting image...")
    img_id = post_image(IMAGE_PATH, FILENAME)
    msg_ids.append(img_id)

    print(f"\nAll messages posted:")
    for mid in msg_ids:
        print(f"  {mid}")


if __name__ == "__main__":
    main()
