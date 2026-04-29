"""Post session 240 painting to Discord #gustave channel.

Discord message IDs (posted 2026-04-29):
  Text 1: 1498930877961470093
  Text 2: 1498930883103817790
  Text 3: 1498930887415300219
  Text 4: 1498930892041883648
  Image:  1498930897473507409
"""
import os
import sys
import json
import subprocess
import time

TOKEN      = os.environ["DISCORD_BOT_TOKEN_RED"]
CHANNEL_ID = "1497780916418908341"

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "s240_dufy_deauville_regatta.png")

IMAGE_DESCRIPTION = """**The Regatta at Deauville** — Session 240

*Near-white primed canvas, Dufy Chromatic Dissociation mode*

**Image Description**

Three racing sailboats run before a fresh southwest breeze on the brilliant Mediterranean blue off Deauville, seen from the promenade in a slightly elevated, open three-quarter view toward the sea. The horizon sits just above mid-canvas — sky above, sea below, beach and promenade filling the warm foreground — a composition built on clear horizontal bands of colour that Dufy would have laid in rapid washes before drawing a single line.

The boats are strung across the middle sea zone in a shallow diagonal recession from left-front to right-back. The closest, at left-centre, carries a red hull — a flat vermillion stroke — and a pair of sails (mainsail and jib) that catch the full afternoon sun. The colour of those sails is near-white with a faint Naples-yellow warmth; the rigging lines that define them, drawn after the wash, are rapid dark strokes that do not quite follow the edge of the white mass — the sail's luminous area bleeds a few centimetres beyond the ink mark. This is Dufy's central technique: the drawing and the colour are separate conversations happening simultaneously on the same surface.

The second boat, at centre, flies a cobalt-blue hull and runs slightly higher in the picture plane — further away, smaller. The third, far right, is green, and is little more than a hull-shape, a mast, and two white triangles. Above each mast a small pennant snaps: vermillion on the first, gold on the second, vermillion again on the third. A festive string of triangular pennants in red, gold, cerulean, and viridian runs across the full width of the sea zone, looping loosely between imaginary stanchions like bunting strung before a regatta start.

The sea is cerulean blue in its upper register, deepening to cobalt shadow in the foreground band. Horizontal wave-shimmer marks — short broken strokes of near-white — cross the sea surface at intervals, not defining waves so much as asserting the dance of light on moving water. The sky above grades from deep cerulean at the top to a hazy pale blue-white at the horizon, where the coastline of distant cliffs appears at the far right in soft ochre-grey, barely distinguished from the sky haze.

In the foreground, a wide sandy beach and promenade occupy the lower third of the canvas in warm sand ochre and Naples yellow. Eight spectator figures — silhouettes in dark, vermillion, cobalt, and viridian — stand or sit along the promenade watching the regatta, each rendered as a rapid ellipse-body with a small oval head, some with a hat or parasol. To the left, a tall palm tree leans slightly away from the viewer, its trunk a warm umber stroke and its fronds viridian arcs — drawn with the same relaxed calligraphic confidence that Dufy applied to all vegetation. A second palm peeks in at the far right edge. Two café parasols, one vermillion and one Naples yellow, stand at lower right, their circular canopies flat and bright, their single pole-strokes vertical and decisive.

The Dufy Chromatic Dissociation pass (151st mode) structures the entire surface. In Stage 1, Sobel-edge detection identifies the drawing lines — the mast lines, the hull boundaries, the edge of every sail — and darkens these zones toward near-black, converting the underlying paint structure into rapid ink-like outlines. In Stage 2, the chrominance of every pixel is shifted ten pixels right and seven pixels down relative to the luminance structure: the blue of the sea washes slightly beyond its drawn outline; the red of the hull drifts past the dark edge that defines it; the white of the sails spills into the adjacent sky. This spatial mis-registration between colour and form is the optical engine of all Dufy's work — it is not carelessness but a deliberate, joyful declaration that colour and drawing are independent energies. In Stage 3, a Fauvist saturation lift of 30% brings every hue to near-full chroma, giving the surface the transparent, light-drenched luminosity of Dufy's watercolours on white paper. The Sfumato Focus improvement softly blurs and desaturates the far periphery (distant coastline, corner sky, foreground sand edges) while leaving the primary sailboat and the sea zone sharp — a gentle radial focus gradient that concentrates attention on the regatta without any visible edge or boundary, just the natural recession of focus toward the periphery, as Leonardo modelled light and air dissolving form at a distance.

**Technique:** Raoul Dufy Chromatic Dissociation (151st distinct mode)
**Palette:** Cerulean blue · deep cobalt · Naples yellow · vermillion-red · viridian green · near-white sails · violet shadow · ochre sand · burnished gold pennants
**Mood:** The pure, uncomplicated joy of a summer regatta — wind, sun, speed, and the festive display of coloured hulls and pennants against Mediterranean blue. The viewer should feel light, warmth, and the holiday energy of a crowd gathered to watch beautiful boats race.
**Passes:** tone_ground (near-white) → underpainting → block_in × 2 → build_form × 2 → place_lights → dufy_chromatic_dissociation_pass → paint_sfumato_focus_pass → diffuse_boundary_pass → glaze (cerulean) → vignette

*New this session: Raoul Dufy (1877-1953, Fauvism / Post-Impressionism) — dufy_chromatic_dissociation_pass (151st distinct mode). THREE-STAGE CHROMATIC DISSOCIATION: (1) Outline extraction and darkening via Sobel-edge gate pushed toward near-black — FIRST pass to model ink-outline occlusion rather than edge contrast-sharpening; (2) Chrominance spatial dissociation: cb_ch = ch − lum, shifted by (dx, dy) pixels while luminance stays fixed — FIRST pass to spatially translate colour independently of form, producing intentional colour-line mis-registration; (3) Fauvist saturation lift. Improvement: paint_sfumato_focus_pass — radial progressive blur with sigmoid gate and simultaneous saturation falloff from a focal centre — FIRST pass to apply spatially varying Gaussian blur from a (cx, cy) focal point with dual radial focus and saturation gradient.*"""

FILENAME = "s240_dufy_deauville_regatta.png"


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

    print("Posting session 240 to Discord #gustave...")
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
