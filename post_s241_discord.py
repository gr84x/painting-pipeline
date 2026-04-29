"""Post session 241 painting to Discord #gustave channel.

Discord message IDs (posted 2026-04-29):
  Text 1: 1498933931062595634
  Text 2: 1498933936238231682
  Text 3: 1498933940839387248
  Text 4: 1498933944970776619
  Text 5: 1498933949555277884
  Text 6: 1498933953875148880
  Image:  1498933959331938364
"""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s241_frankenthaler_egret_dusk.png")

IMAGE_DESCRIPTION = """**The Egret at Dusk** — Session 241

*Off-white raw canvas ground, Frankenthaler Soak-Stain mode*

**Image Description**

A solitary great egret (Ardea alba) stands at the edge of tidal shallows in the final minutes of civil twilight, viewed from slightly below eye level in a portrait-format composition, the bird positioned just left of centre. It is mid-stride — right leg raised with knee bent forward, left leg planted in still, shallow water — its neck held in a relaxed S-curve, the long amber-yellow beak angled downward as though tracking some subtle movement below the surface. The bird is alert but entirely unhurried. It has the concentrated patience of a hunter who has learned that stillness is the most effective technique.

The egret occupies roughly two-thirds of the canvas height. Its plumage is a near-warm white — not pure white but the white of something that has absorbed light over a long, still afternoon — with soft lavender shadows pooling along its right flank where the cooling dusk light no longer reaches. From its lower back, breeding aigrette plumes trail in fine, weightless wisps, curving slightly as though moved by a breath of air too gentle to feel. The yellow lore — that bare patch of skin between eye and bill — catches the last horizontal light with vivid warmth. The beak is burnished amber-gold, deepening to near-black at its sharp, decisive tip.

The setting is a tidal marsh at low water, at the last minutes before dark. Sky occupies the upper forty percent of the canvas: luminous pale cerulean at the top, graduating down through rose-gold and warm ochre toward the horizon, where the most saturated colour exists — a narrow band of rose-gold glow, the memory of a sun that set behind the reeds moments before. At the horizon, sky and water meet without a drawn line; the two zones dissolve into each other through a shared warmth of colour. The lower sixty percent of the canvas is still water — the marsh at low tide, shallow enough that the egret's grey-green legs disappear into it only to the knee. The water mirrors the sky but deepens continuously toward deep indigo at the canvas bottom, as though the sea beneath the shallow surface is a different, older world. Horizontal bands of water-shimmer cross the mid-water zone — glassy, pale, ephemeral. In the far right of the canvas, above the horizon line, a loose mass of marsh reeds and sedge grasses rises in soft sage green; their tops dissolve into atmospheric haze, their bases already indistinguishable from the water they grow in.

Below the egret, just barely: its reflection — distorted, wider, paler, already half-absorbed into the indigo water. And from the planted left foot, slow rings of ripple spread outward, crossing the rose-gold reflection in the water, marking the one point of contact between the bird's patience and the world's movement.

The Frankenthaler Soak-Stain pass (152nd mode) is the structural logic of the image. Rather than painting sky and water as surfaces — rather than applying colour that sits on the canvas as a film — the soak-stain technique models paint absorbed INTO the canvas itself, wicking into the fibres of the raw cotton duck. Five independent stain pours are laid across the surface: each is a broad, organic shape generated from multi-scale noise fields at two spatial frequencies (sigma 55 for the broad swept-pour and sigma 16 for finer capillary detail), weighted toward mid-luminance zones where unprimed canvas absorbs most. The colours of each stain are sampled from the underlying canvas in that region, so each pour amplifies and transforms what is already there rather than overriding it. An absorption coefficient of 0.60 models sixty percent of each pour wicked into the fibres, leaving only forty percent at the surface — producing the transparent, filmless quality of Frankenthaler's actual stain paintings. At each stain's boundary, a capillary diffusion step applies an additional Gaussian blur precisely at the perimeter of the stain mask (where its gradient exceeds threshold), simulating the capillary fringe where paint wicks outward along individual canvas fibres beyond the main pool. The result: sky and water as pure, absorbed light; colour that is part of the material rather than applied to it.

The Lost-Found Edges improvement (session 241) structures the visual hierarchy. Every edge in the composition is classified on a continuous spectrum from fully found (hard, sharp, attended) to fully lost (soft, dissolved, peripheral) based on a combined importance score: local edge contrast multiplied by local standard deviation, weighted against radial proximity to the focal centre at the egret's body. Found edges — the beak, the eye, the bright line where plumage meets shadow, the egret's left leg entering water — are sharpened via unsharp masking at their scored weight. Lost edges — the horizon line, the distant reeds, the water shimmer at the canvas edges, the egret's reflection — are softened by Gaussian blur at their scored weight. No prior pass in the project applies both sharpening and softening simultaneously in a single pass governed by the same importance metric: this is the first time the full found/lost doctrine is implemented as a continuous differential edge treatment.

**Technique:** Helen Frankenthaler Soak-Stain (152nd distinct mode)
**Palette:** Off-white raw canvas ground · cerulean blue · rose-gold · warm ochre · deep indigo · sage green · near-white plumage · lavender shadow · beak amber
**Mood:** Stillness, patience, and the particular quality of light that exists for twenty minutes at day's end — when the sky still holds colour but the land has already entered evening. The painting asks the viewer to inhabit the egret's state: perfectly alert, completely unhurried, in that moment before the strike or the move that never quite arrives. The sky and water dissolve into each other as absorbed light; the egret alone holds its edge, found among lost things.
**Passes:** tone_ground (raw canvas) → underpainting → block_in × 2 → build_form × 2 → place_lights → frankenthaler_soak_stain_pass → paint_lost_found_edges_pass → diffuse_boundary_pass → glaze (cerulean) → glaze (rose-gold) → vignette

*New this session: Helen Frankenthaler (1928-2011, Color Field / Abstract Expressionism) — frankenthaler_soak_stain_pass (152nd distinct mode). THREE-STAGE SOAK-STAIN: (1) Organic stain region generation via multi-scale noise composition at sigma_large=55 and sigma_small=16, luminance-biased toward mid-tone zones — FIRST pass to build region masks from two-sigma random field composition with luminance weighting; (2) Paint absorption simulation: delta = stain_alpha × (1-absorption) × (stain_color - ch), modelling sixty percent absorption into canvas fibres vs. surface film — FIRST pass to separate surface opacity from substrate absorption coefficient; (3) Capillary edge diffusion: extra Gaussian blur applied selectively at stain boundary zones (|nabla mask| > threshold) — FIRST pass to apply boundary-localised capillary blur at the gradient-detected perimeter of generated region masks. Improvement: paint_lost_found_edges_pass — simultaneous found-edge sharpening (unsharp mask) and lost-edge softening (Gaussian) governed by a combined local-contrast × radial-proximity importance score — FIRST pass to implement differential edge treatment (sharpening found, softening lost) in a single unified pass.*"""

FILENAME = "s241_frankenthaler_egret_dusk.png"


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

    print("Posting session 241 to Discord #gustave...")
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

    return msg_ids


if __name__ == "__main__":
    main()
