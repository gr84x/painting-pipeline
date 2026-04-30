"""
paint_s260_foujita_woman_cat.py -- Session 260

"Woman with Cat, Afternoon Window" -- in the manner of Tsuguharu Foujita

Image Description
-----------------
Subject & Composition
    A single young woman, three-quarter view from the front-left, seated in a
    low wooden chair in a small Parisian apartment room. She occupies the left
    two-thirds of the composition, from just below waist level to just above
    the top of her loosely-pinned dark hair. Her gaze is directed toward the
    upper right, toward a grey tabby cat sitting on a white-painted windowsill
    in the upper-right quadrant. The cat is smaller, occupying perhaps a sixth
    of the total canvas area -- present but subsidiary. The eye traces a gentle
    diagonal from the woman's loosely-held hands in the lower center to the
    cat's watchful amber eyes at the upper right. A round pedestal side table
    enters from the lower-right corner, bearing a small ceramic cup and a
    folded journal. The chair's curved wooden back is visible behind the figure.

The Figure
    The woman is in her late twenties. She wears a loose, slightly oversized
    white cotton blouse with a small stand collar and a fine stripe pattern
    barely visible in the fabric -- the kind of blouse that has been washed
    too many times and has a familiar softness. Her dark hair is loosely piled
    up, several strands escaped at her nape and temple. Her skin is the
    defining element: the characteristic Foujita milky ivory -- luminous,
    pearlescent, neither warm nor cool but both simultaneously, as if lit from
    within. Her hands rest loosely in her lap, fingers lightly laced, the knuckle
    geography precise but not tense. Her face is turned so the viewer sees her
    left cheek and the bridge of her nose in three-quarter profile; her eyes are
    directed toward the cat. Her emotional state is one of quiet, suspended
    attention -- the particular absorption of watching an animal do something
    unremarkable. There is no drama in her expression. There is only presence.

The Environment
    A Parisian apartment room, third arrondissement, early afternoon in March.
    The light comes from a single tall window with a white-painted wooden frame,
    positioned in the upper-right of the composition. The window glass is slightly
    dusty, softening the exterior light into a diffuse, cool-pale wash. On the
    windowsill sits the grey tabby cat -- compact, upright, facing the woman with
    amber-yellow eyes half-slitted in the afternoon light. The cat's fur is a
    warm dark grey with faint striping, its paws folded neatly beneath its chest.
    The walls are papered with a faded floral pattern in muted ochre and dusty
    rose on a cream ground -- the wallpaper has been there for thirty years and
    has faded unevenly, darker near the baseboard and the corners, lighter near
    the ceiling and the window. The floor is warm-brown parquet, partially
    obscured by the chair and the lower edge of the woman's skirt. The side table
    in the lower right has a small white tablecloth, a ceramic cup with the faint
    ring-stain of coffee, and a folded weekly journal, its printed text too small
    to read. The boundary between the wallpapered wall and the window is a gentle
    tonal shift, not a hard line -- the window brightens the wall around it and
    the edge dissolves in pale wash.

Technique & Palette
    Foujita Milky Ground Contour mode -- session 260, 171st distinct mode.

    Stage 1 MILKY IVORY GROUND LIFT is applied at ivory_threshold=0.65,
    ivory_strength=0.52: this concentrates the warm ivory warmth (0.97, 0.95, 0.88)
    in the woman's skin highlight passages, the cotton blouse, and the white
    windowsill, giving them the characteristic Foujita porcelain luminosity.
    The wallpaper, the floor, and the shadow zones are below threshold and remain
    relatively unchanged, preserving the tonal depth of the room.

    Stage 2 JAPANESE INK CONTOUR TRACING at contour_threshold=0.07,
    contour_darkness=0.65: the Sobel-based contour detection draws dark lines
    at all significant tonal transitions -- the shoulder of the blouse, the
    curve of the jaw, the profile of the hair mass, the window frame, the table
    edge, the cat's silhouette. These contours function as Foujita's sable-brush
    ink lines, giving the image its structural skeleton.

    Stage 3 DIRECTIONAL MICRO-TEXTURE HATCHING at hatch_spacing=4,
    hatch_amplitude=0.028: fine directional hatching appears across the pale zones
    of skin and blouse, following the local gradient orientation (i.e., parallel
    to the surface contours rather than perpendicular to them) -- this is the
    cat-fur and skin-surface micro-mark that characterizes Foujita's mature work.
    The hatching is subtle enough to read as texture, not as visible marks.

    Sfumato Contour Dissolution improvement (session 260): Applied at
    edge_sigma=1.0, blur_sigma=2.2, dissolve_strength=0.60, shadow_bias=0.22,
    opacity=0.55 -- the sfumato pass softens the transition zones at the window-
    wall boundary and at the hair-background transition, while the shadow_bias
    deepening slightly darkens the room's shadow zones at their edges, giving
    the background the quality of sfumato recession: forms emerge from warmth
    rather than being outlined against it.

    Stage-by-stage palette build:
    Ground: warm linen-ivory (0.94, 0.91, 0.82)
    Block-in: figure mass and room
    Build form: figure modelling and room tones
    Place lights: window highlights and skin lights
    Foujita Milky Ground Contour pass: ivory lift, contour lines, micro-texture
    Sfumato Contour Dissolution pass: window-wall softening, shadow deepening
    Tonal Key pass (s255): confirm overall mid-high key
    Atmospheric Recession pass (s259): subtle recession toward window

    Palette: ivory-skin (0.97/0.95/0.88) -- skin-warm-mid (0.88/0.72/0.56) --
    skin-shadow (0.74/0.60/0.46) -- blouse-white (0.94/0.92/0.84) --
    wall-ochre-pale (0.86/0.80/0.64) -- wall-rose (0.80/0.72/0.62) --
    window-light (0.92/0.92/0.90) -- cat-grey-warm (0.55/0.52/0.48) --
    cat-grey-shadow (0.38/0.36/0.34) -- hair-dark (0.22/0.18/0.14) --
    floor-warm (0.60/0.50/0.36) -- table-cloth (0.92/0.90/0.82) --
    contour-ink (0.14/0.12/0.10) -- wood-chair (0.52/0.42/0.30)

Mood & Intent
    The image carries the particular quality Foujita found in domestic Paris:
    a moment sealed in amber light, existing outside narrative time. The woman
    does not look at the viewer -- she is absorbed in watching her cat, which
    watches her back. This small circuit of attention, between two living
    creatures in a warm room, is the entire content of the picture. The milky
    ivory of her skin against the faded wallpaper creates a tonal argument about
    presence and memory: she glows while the room recedes. The contour lines,
    drawn with the precision and restraint of Japanese calligraphy, give the
    image its structural dignity -- nothing is vague, nothing is approximate,
    and yet nothing is harsh. The viewer is intended to leave the picture feeling
    that they have seen something actual: not a symbol or a statement, but the
    simple fact of an afternoon, a woman, and a cat.
"""

import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from PIL import Image
from stroke_engine import Painter

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "s260_foujita_woman_cat.png")

W, H = 760, 900
RNG = random.Random(260)

# ── Colour palette ─────────────────────────────────────────────────────────────

IVORY_SKIN        = (0.97, 0.95, 0.88)
SKIN_WARM_MID     = (0.88, 0.72, 0.56)
SKIN_SHADOW       = (0.74, 0.60, 0.46)
SKIN_DEEP         = (0.58, 0.45, 0.33)
BLOUSE_WHITE      = (0.94, 0.92, 0.84)
BLOUSE_SHADOW     = (0.78, 0.76, 0.68)
WALL_OCHRE        = (0.86, 0.80, 0.64)
WALL_ROSE         = (0.80, 0.72, 0.62)
WALL_SHADOW       = (0.70, 0.64, 0.52)
WINDOW_LIGHT      = (0.94, 0.94, 0.92)
WINDOW_FRAME      = (0.88, 0.87, 0.82)
CAT_GREY_WARM     = (0.56, 0.52, 0.48)
CAT_GREY_DARK     = (0.38, 0.36, 0.34)
CAT_HIGHLIGHT     = (0.72, 0.70, 0.66)
HAIR_DARK         = (0.22, 0.18, 0.14)
HAIR_LIGHT        = (0.38, 0.32, 0.25)
FLOOR_WARM        = (0.62, 0.52, 0.38)
FLOOR_SHADOW      = (0.46, 0.38, 0.28)
TABLE_CLOTH       = (0.92, 0.90, 0.82)
CHAIR_WOOD        = (0.52, 0.42, 0.30)
INK_CONTOUR       = (0.14, 0.12, 0.10)
SILL_WHITE        = (0.90, 0.89, 0.84)
CUP_CERAMIC       = (0.82, 0.78, 0.70)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(a[i] * (1.0 - t) + b[i] * t for i in range(len(a)))


def smooth_step(t):
    return t * t * (3.0 - 2.0 * t)


def build_reference(w: int, h: int) -> Image.Image:
    """Build the procedural reference image for Woman with Cat, Afternoon Window."""
    arr = np.zeros((h, w, 3), dtype=np.float32)

    # Key layout proportions
    wall_top_y    = 0                      # wall starts at top
    window_left   = int(w * 0.62)          # window starts here
    window_right  = int(w * 0.95)
    window_top    = int(h * 0.04)
    window_bot    = int(h * 0.44)
    sill_y        = window_bot
    sill_bot      = int(h * 0.50)
    floor_y       = int(h * 0.82)          # floor starts here

    figure_cx     = int(w * 0.35)          # figure center x
    figure_top    = int(h * 0.04)          # top of hair
    figure_bot    = int(h * 0.85)          # bottom of figure
    shoulder_y    = int(h * 0.28)
    neck_bot      = int(h * 0.24)
    neck_top      = int(h * 0.18)
    head_cy       = int(h * 0.14)
    head_rx       = int(w * 0.095)
    head_ry       = int(h * 0.110)

    # ── Background wall ────────────────────────────────────────────────────────
    for row in range(floor_y):
        fy = row / floor_y
        for col in range(w):
            fx = col / w
            # Faded wallpaper: ochre-rose pattern, lighter near window
            window_proximity = max(0.0, (col - window_left + 60) / 80.0) if col > window_left - 60 else 0.0
            window_proximity = min(1.0, window_proximity)
            base = lerp(WALL_OCHRE, WALL_ROSE, 0.5 + 0.4 * math.sin(fx * 12.0 + fy * 8.0))
            # Fade corners darker
            corner_fade = max(0.0, 1.0 - 3.0 * (1.0 - fx) * (1.0 - fy))
            base = lerp(WALL_SHADOW, base, 0.55 + 0.45 * corner_fade)
            # Window brightens adjacent wall
            base = lerp(base, WINDOW_LIGHT, window_proximity * 0.35)
            arr[row, col, :] = base

    # ── Window opening ─────────────────────────────────────────────────────────
    for row in range(window_top, window_bot):
        for col in range(window_left, window_right):
            fy = (row - window_top) / max(1, window_bot - window_top)
            fx = (col - window_left) / max(1, window_right - window_left)
            # Window light: cool near-white, slightly warmer at bottom
            light_warm = fy * 0.08
            arr[row, col, :] = lerp(WINDOW_LIGHT, (0.88, 0.82, 0.68), light_warm)

    # ── Window frame ──────────────────────────────────────────────────────────
    frame_w = max(3, int(w * 0.008))
    # Left frame
    for row in range(window_top - frame_w, window_bot + frame_w):
        for col in range(max(0, window_left - frame_w), min(w, window_left + 1)):
            if 0 <= row < h:
                arr[row, col, :] = WINDOW_FRAME
    # Right frame
    for row in range(window_top - frame_w, window_bot + frame_w):
        for col in range(window_right, min(w, window_right + frame_w)):
            if 0 <= row < h:
                arr[row, col, :] = WINDOW_FRAME
    # Top frame
    for row in range(max(0, window_top - frame_w), window_top + 1):
        for col in range(window_left - frame_w, window_right + frame_w):
            if 0 <= col < w:
                arr[row, col, :] = WINDOW_FRAME
    # Bottom frame / sill top
    for row in range(window_bot, window_bot + frame_w + 2):
        for col in range(window_left - frame_w, window_right + frame_w):
            if 0 <= row < h and 0 <= col < w:
                arr[row, col, :] = WINDOW_FRAME

    # ── Windowsill surface ────────────────────────────────────────────────────
    for row in range(window_bot + frame_w, sill_bot):
        for col in range(max(0, window_left - int(w * 0.015)), min(w, window_right + int(w * 0.015))):
            fy = (row - window_bot) / max(1, sill_bot - window_bot)
            arr[row, col, :] = lerp(SILL_WHITE, WINDOW_FRAME, fy * 0.35)

    # ── Floor ─────────────────────────────────────────────────────────────────
    for row in range(floor_y, h):
        fy = (row - floor_y) / max(1, h - floor_y)
        for col in range(w):
            fx = col / w
            # Parquet: warm brown with subtle plank grain
            plank_grain = math.sin(fx * 30.0) * 0.03
            arr[row, col, :] = lerp(
                FLOOR_WARM,
                FLOOR_SHADOW,
                fy * 0.45 + plank_grain + fx * 0.10,
            )

    # ── Floor-wall transition ─────────────────────────────────────────────────
    for row in range(max(0, floor_y - 5), min(h, floor_y + 5)):
        for col in range(w):
            t = abs(row - floor_y) / 5.0
            arr[row, col, :] = lerp(lerp(WALL_SHADOW, FLOOR_SHADOW, 0.5), arr[row, col, :], t)

    # ── Hair mass ─────────────────────────────────────────────────────────────
    hair_top = figure_top
    hair_bot = int(h * 0.20)
    hair_lx  = int(figure_cx - head_rx * 1.15)
    hair_rx  = int(figure_cx + head_rx * 0.80)  # 3/4 view: less visible right side

    for row in range(hair_top, hair_bot):
        fy = (row - hair_top) / max(1, hair_bot - hair_top)
        hw = int((head_rx * 1.1) * math.sqrt(1.0 - (1.0 - fy) ** 2) + 2)
        left  = max(0, figure_cx - hw)
        right = min(w, figure_cx + int(hw * 0.7))  # 3/4 view
        for col in range(left, right):
            fx = (col - left) / max(1, right - left)
            light_t = (1.0 - fy) * 0.30 + (1.0 - fx) * 0.20
            arr[row, col, :] = lerp(HAIR_DARK, HAIR_LIGHT, light_t * 0.55)

    # ── Face / head ───────────────────────────────────────────────────────────
    for row in range(max(0, head_cy - head_ry), min(h, head_cy + head_ry)):
        dy = (row - head_cy) / head_ry
        hw = int(head_rx * math.sqrt(max(0.0, 1.0 - dy ** 2)))
        face_left  = max(0, figure_cx - hw)
        face_right = min(w, figure_cx + int(hw * 0.82))  # 3/4 view

        for col in range(face_left, face_right):
            fx = (col - face_left) / max(1, face_right - face_left)
            # Light from window (upper right) -- face lit slightly on right side
            lit_t   = fx * 0.45 + (1.0 - abs(dy)) * 0.25
            shade_t = (1.0 - fx) * 0.40
            skin = lerp(SKIN_WARM_MID, IVORY_SKIN, lit_t)
            skin = lerp(SKIN_SHADOW, skin, 1.0 - shade_t * 0.5)
            arr[row, col, :] = skin

    # ── Neck ─────────────────────────────────────────────────────────────────
    neck_hw = int(w * 0.032)
    for row in range(neck_top, neck_bot):
        for col in range(max(0, figure_cx - neck_hw), min(w, figure_cx + int(neck_hw * 0.9))):
            fx = (col - (figure_cx - neck_hw)) / max(1, 2 * neck_hw)
            skin = lerp(SKIN_SHADOW, SKIN_WARM_MID, fx * 0.7 + 0.2)
            arr[row, col, :] = skin

    # ── Body: torso in blouse ─────────────────────────────────────────────────
    torso_top   = shoulder_y
    torso_bot   = int(h * 0.78)
    torso_left  = int(figure_cx - w * 0.175)
    torso_right = int(figure_cx + w * 0.155)

    for row in range(torso_top, min(h, torso_bot)):
        fy = (row - torso_top) / max(1, torso_bot - torso_top)
        # Torso narrows slightly at waist, widens at hip
        t_half = int(w * (0.130 + fy * 0.040))
        left  = max(0, figure_cx - t_half - int(w * 0.015))
        right = min(w, figure_cx + t_half - int(w * 0.020))
        for col in range(left, right):
            fx = (col - left) / max(1, right - left)
            # Window light from right -- blouse right flank brighter
            lit_t = fx * 0.50 + (1.0 - fy) * 0.15
            blouse = lerp(BLOUSE_SHADOW, BLOUSE_WHITE, lit_t * 0.85 + 0.10)
            # Subtle floral stripe pattern
            stripe = math.sin((row + col * 0.6) * 0.35) * 0.012
            blouse = lerp(blouse, WALL_OCHRE, abs(stripe))
            arr[row, col, :] = blouse

    # ── Shoulder transition (skin to blouse) ─────────────────────────────────
    for row in range(max(0, neck_bot), shoulder_y + int(h * 0.025)):
        fy = (row - neck_bot) / max(1, shoulder_y - neck_bot + int(h * 0.025))
        hw = int(w * (0.055 + fy * 0.08))
        for col in range(max(0, figure_cx - hw - int(w * 0.015)),
                         min(w, figure_cx + int(hw * 0.80))):
            fx = (col - (figure_cx - hw)) / max(1, 2 * hw)
            skin = lerp(SKIN_SHADOW, SKIN_WARM_MID, fx * 0.6)
            arr[row, col, :] = skin

    # ── Hands in lap ─────────────────────────────────────────────────────────
    lap_y   = int(h * 0.72)
    lap_h   = int(h * 0.065)
    lap_cx  = int(figure_cx + w * 0.020)
    lap_hw  = int(w * 0.080)
    for row in range(lap_y, min(h, lap_y + lap_h)):
        fy = (row - lap_y) / max(1, lap_h)
        hw = int(lap_hw * (1.0 - fy * 0.30))
        for col in range(max(0, lap_cx - hw), min(w, lap_cx + hw)):
            fx = (col - (lap_cx - hw)) / max(1, 2 * hw)
            skin = lerp(SKIN_SHADOW, IVORY_SKIN, fx * 0.55 + 0.25)
            arr[row, col, :] = skin

    # ── Chair back (wooden arc) ───────────────────────────────────────────────
    chair_arc_top = int(h * 0.28)
    chair_arc_bot = int(h * 0.60)
    chair_right   = int(figure_cx + w * 0.220)
    chair_left    = int(figure_cx - w * 0.205)
    chair_w       = max(4, int(w * 0.012))

    # Left vertical of chair back
    for row in range(chair_arc_top, chair_arc_bot):
        for col in range(max(0, chair_left), min(w, chair_left + chair_w)):
            arr[row, col, :] = CHAIR_WOOD

    # Right vertical of chair back
    for row in range(chair_arc_top, chair_arc_bot):
        for col in range(max(0, chair_right - chair_w), min(w, chair_right)):
            arr[row, col, :] = CHAIR_WOOD

    # Top horizontal bar of chair back
    bar_h = max(3, int(h * 0.018))
    for row in range(chair_arc_top, chair_arc_top + bar_h):
        for col in range(max(0, chair_left - chair_w // 2), min(w, chair_right + chair_w // 2)):
            arr[row, col, :] = CHAIR_WOOD

    # ── Cat on windowsill ─────────────────────────────────────────────────────
    cat_cx  = int(w * 0.77)
    cat_cy  = int(h * 0.35)
    cat_rx  = int(w * 0.065)
    cat_ry  = int(h * 0.085)
    # Cat body (compact oval)
    for row in range(max(0, cat_cy - cat_ry), min(h, cat_cy + cat_ry)):
        dy = (row - cat_cy) / cat_ry
        hw = int(cat_rx * math.sqrt(max(0.0, 1.0 - dy ** 2)))
        for col in range(max(0, cat_cx - hw), min(w, cat_cx + hw)):
            fx = (col - (cat_cx - hw)) / max(1, 2 * hw)
            # Light from window (above-right)
            lit_t = fx * 0.35 + (1.0 - abs(dy)) * 0.30
            cat_col = lerp(CAT_GREY_DARK, CAT_GREY_WARM, lit_t)
            cat_col = lerp(cat_col, CAT_HIGHLIGHT, (1.0 - abs(dy)) * 0.20)
            arr[row, col, :] = cat_col

    # Cat head (slightly above body)
    cat_head_cy = cat_cy - int(cat_ry * 0.75)
    cat_head_rx = int(cat_rx * 0.68)
    cat_head_ry = int(cat_ry * 0.60)
    for row in range(max(0, cat_head_cy - cat_head_ry), min(h, cat_head_cy + cat_head_ry)):
        dy = (row - cat_head_cy) / cat_head_ry
        hw = int(cat_head_rx * math.sqrt(max(0.0, 1.0 - dy ** 2)))
        for col in range(max(0, cat_cx - hw), min(w, cat_cx + hw)):
            fx = (col - (cat_cx - hw)) / max(1, 2 * hw)
            lit_t = fx * 0.40 + (1.0 - abs(dy)) * 0.20
            cat_col = lerp(CAT_GREY_DARK, CAT_GREY_WARM, lit_t * 0.7 + 0.1)
            arr[row, col, :] = cat_col

    # Cat ears (two small triangular patches)
    for ear_cx in [cat_cx - int(cat_head_rx * 0.50), cat_cx + int(cat_head_rx * 0.45)]:
        ear_top  = cat_head_cy - cat_head_ry - int(h * 0.025)
        ear_bot  = cat_head_cy - cat_head_ry + int(h * 0.010)
        ear_hw   = max(2, int(cat_head_rx * 0.28))
        for row in range(max(0, ear_top), min(h, ear_bot)):
            fy = (row - ear_top) / max(1, ear_bot - ear_top)
            hw = max(1, int(ear_hw * (1.0 - (1.0 - fy) * 0.8)))
            for col in range(max(0, ear_cx - hw), min(w, ear_cx + hw)):
                arr[row, col, :] = CAT_GREY_DARK

    # ── Side table lower-right ────────────────────────────────────────────────
    table_cx  = int(w * 0.82)
    table_top = int(h * 0.68)
    table_bot = int(h * 0.76)
    table_hw  = int(w * 0.090)
    cloth_lift = int(h * 0.008)

    # Tablecloth surface
    for row in range(table_top, table_bot):
        fy = (row - table_top) / max(1, table_bot - table_top)
        for col in range(max(0, table_cx - table_hw), min(w, table_cx + table_hw)):
            arr[row, col, :] = lerp(TABLE_CLOTH, BLOUSE_SHADOW, fy * 0.25)

    # Table pedestal (thin vertical column below cloth)
    ped_hw = max(3, int(w * 0.010))
    for row in range(table_bot, min(h, floor_y + int(h * 0.04))):
        for col in range(max(0, table_cx - ped_hw), min(w, table_cx + ped_hw)):
            arr[row, col, :] = CHAIR_WOOD

    # Cup on table
    cup_cx  = int(table_cx - table_hw * 0.30)
    cup_cy  = int(table_top - int(h * 0.012))
    cup_rx  = int(w * 0.018)
    cup_ry  = int(h * 0.022)
    for row in range(max(0, cup_cy - cup_ry), min(h, cup_cy + cup_ry)):
        dy = (row - cup_cy) / cup_ry
        hw = int(cup_rx * math.sqrt(max(0.0, 1.0 - dy ** 2)))
        for col in range(max(0, cup_cx - hw), min(w, cup_cx + hw)):
            arr[row, col, :] = CUP_CERAMIC

    arr = np.clip(arr, 0.0, 1.0)
    arr_uint8 = (arr * 255).astype(np.uint8)
    return Image.fromarray(arr_uint8, "RGB")


def main():
    print("Session 260 -- Woman with Cat, Afternoon Window (after Tsuguharu Foujita)")
    print(f"Canvas: {W}x{H}")
    print()

    ref = build_reference(W, H)
    print("Reference built.")

    p = Painter(W, H)

    # Ground: warm linen-ivory imprimatura
    print("Toning ground...")
    p.tone_ground((0.94, 0.91, 0.82), texture_strength=0.018)

    # Block in: figure and room masses
    print("Blocking in masses...")
    p.block_in(ref, stroke_size=32, n_strokes=180)

    # Build form: modelling on figure
    print("Building form...")
    p.build_form(ref, stroke_size=14, n_strokes=140)

    # Place lights: window highlights and skin lights
    print("Placing lights...")
    p.place_lights(ref, stroke_size=5, n_strokes=90)

    # ── Foujita Milky Ground Contour pass (171st mode) ────────────────────────
    print("Applying Foujita Milky Ground Contour pass...")
    p.foujita_milky_ground_contour_pass(
        ivory_r=0.97,
        ivory_g=0.95,
        ivory_b=0.88,
        ivory_threshold=0.65,
        ivory_strength=0.52,
        contour_threshold=0.07,
        contour_width=1,
        contour_darkness=0.65,
        hatch_spacing=4,
        hatch_amplitude=0.028,
        hatch_sigma=0.9,
        noise_seed=260,
        opacity=0.80,
    )

    # ── Sfumato Contour Dissolution pass (improvement) ────────────────────────
    print("Applying Sfumato Contour Dissolution pass...")
    p.paint_sfumato_contour_dissolution_pass(
        edge_sigma=1.0,
        edge_threshold=0.05,
        blur_sigma=2.2,
        dissolve_strength=0.60,
        shadow_bias=0.22,
        noise_seed=260,
        opacity=0.55,
    )

    # ── Atmospheric Recession pass (s259) ─────────────────────────────────────
    print("Applying Atmospheric Recession pass...")
    p.paint_atmospheric_recession_pass(
        recession_direction="top",
        haze_lift=0.04,
        desaturation=0.08,
        cool_shift_r=0.02,
        cool_shift_g=0.01,
        cool_shift_b=0.02,
        near_fraction=0.20,
        far_fraction=0.80,
        opacity=0.42,
    )

    # ── Tonal Key pass (s255) ─────────────────────────────────────────────────
    print("Applying Tonal Key pass...")
    p.paint_tonal_key_pass(
        target_key=0.64,
        key_strength=1.8,
        dither_amplitude=0.003,
        opacity=0.32,
    )

    # ── Edge Temperature pass (s256) ─────────────────────────────────────────
    print("Applying Edge Temperature pass...")
    p.paint_edge_temperature_pass(
        warm_hue_center=0.08,
        warm_hue_width=0.18,
        cool_hue_center=0.58,
        cool_hue_width=0.20,
        gradient_zone_px=2.5,
        contrast_strength=0.06,
        opacity=0.48,
    )

    # ── Shadow Bleed pass (s257) ──────────────────────────────────────────────
    print("Applying Shadow Bleed pass...")
    p.paint_shadow_bleed_pass(
        shadow_threshold=0.40,
        bright_threshold=0.70,
        bleed_sigma=14.0,
        reflect_strength=0.10,
        warm_r=0.92,
        warm_g=0.84,
        warm_b=0.58,
        opacity=0.45,
    )

    # Save
    print(f"Saving to {OUTPUT_PATH}...")
    p.save(OUTPUT_PATH)
    print(f"Saved: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
