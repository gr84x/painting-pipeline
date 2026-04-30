"""Update giorgio_morandi catalog inspiration to reference morandi_dusty_vessel_pass
(session 258, 169th mode).

Run once to modify art_catalog.py; preserved as a change record afterward.
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.abspath(__file__))
catalog_path = os.path.join(REPO, "art_catalog.py")

with open(catalog_path, "r", encoding="utf-8") as f:
    src = f.read()

if "morandi_dusty_vessel_pass" in src:
    print("giorgio_morandi inspiration already updated -- nothing to do.")
    sys.exit(0)

# Locate the exact inspiration block in the morandi entry
ANCHOR = '"giorgio_morandi"'
morandi_idx = src.find(ANCHOR)
if morandi_idx == -1:
    print("ERROR: could not find giorgio_morandi in catalog", file=sys.stderr)
    sys.exit(1)

chunk = src[morandi_idx:morandi_idx + 6000]
INSP_OPEN = 'inspiration=(\n'
insp_offset = chunk.find(INSP_OPEN)
if insp_offset == -1:
    print("ERROR: could not find inspiration=( in morandi block", file=sys.stderr)
    sys.exit(1)

# Find the matching close paren
depth = 0
start = insp_offset
for j, ch in enumerate(chunk[start:]):
    if ch == '(':
        depth += 1
    elif ch == ')':
        depth -= 1
        if depth == 0:
            end = start + j + 1
            break

old_inspiration = chunk[start:end]
old_abs_start = morandi_idx + start
old_abs_end   = morandi_idx + end

NEW_INSPIRATION = (
    'inspiration=(\n'
    '            "morandi_tonal_unity_pass() is the NINETY-SIXTH DISTINCT MODE "\n'
    '            "(CIELAB chrominance-only spatial convergence). "\n'
    '            "palette_proximity_pull_pass() is the NINETY-SEVENTH DISTINCT MODE "\n'
    '            "(soft palette nearest-neighbour gravity). "\n'
    '            "morandi_dusty_vessel_pass(): ONE HUNDRED AND SIXTY-NINTH "\n'
    '            "(169th) distinct mode -- three-stage dusty still-life effect -- "\n'
    '            "(1) DUSTY DESATURATION VEIL: luminance-weighted HSV saturation reduction "\n'
    '            "(dark pixels lose colour most; shadow zones go grey-dust); "\n'
    '            "first pass for luminance-weighted saturation clamp as dusty atmospheric veil; "\n'
    '            "(2) TONAL COMPRESSION: push all pixel luminance toward target_mid via lerp "\n'
    '            "then scale RGB proportionally to preserve hue; Morandi narrow tonal window; "\n'
    '            "first pass for pixel-wise luminance lerp toward user-defined mid-tone; "\n'
    '            "(3) OCHRE GROUND REVEAL: blend near-highlight pixels toward warm ochre "\n'
    '            "ground colour proportional to excess luminance above reveal_threshold; "\n'
    '            "first pass for luminance-gated ground-colour bleed in near-highlight regions."\n'
    '        )'
)

src = src[:old_abs_start] + NEW_INSPIRATION + src[old_abs_end:]

with open(catalog_path, "w", encoding="utf-8") as f:
    f.write(src)

print("Updated giorgio_morandi inspiration in art_catalog.py.")
