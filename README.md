# Painting Pipeline

A procedural portrait painting system. Describe a scene in Python; get back a painted image.

The pipeline builds a parametric 3D figure in Blender (head mesh, hair, costume), renders it into a reference image + normal map, then repaints it with a stroke engine that mimics oil painting technique — broad washes first, then focused detail passes around facial features.

## How it works

```
Scene (Python) → blender_bridge → Blender renders (beauty + mask + normals)
                                ↓
                         stroke_engine → painting output (.png)
```

Three render passes per scene:
1. **Beauty pass** — full Cycles render; becomes the reference image
2. **Figure mask** — flat white silhouette; used to prevent strokes bleeding into background
3. **Normal map** — world normals encoded as RGB; enables toon/cel-shading mode

## Requirements

- [Blender 4.x or 5.x](https://www.blender.org/) — must be on `PATH` as `blender`
- Python 3.10+
- `numpy`, `Pillow`

```bash
pip install numpy Pillow
```

## Quick Start

```bash
cd examples
python run_v21.py          # realistic oil portrait (best result)
python run_cartoon_v1.py   # cartoon morphology preset
```

Output images are written to the project root.

## Core Modules

| Module | Purpose |
|--------|---------|
| `scene_schema.py` | Dataclasses: `Scene`, `Character`, `Camera`, `LightRig`, `Style`, … |
| `blender_bridge.py` | Generates and executes Blender Python scripts; handles all three render passes |
| `figure_builder.py` | Assembles figure mesh (head + hair + costume) as a Blender script string |
| `head_builder.py` | Parametric head: UV sphere + Gaussian feature displacements + morphology deformations |
| `face_builder.py` | Legacy head builder (kept for reference) |
| `cartoon_morphology.py` | `CartoonMorphology` dataclass with presets: `realistic`, `stylized`, `cartoon`, `chibi` |
| `costume_builder.py` | Dress / outfit mesh generation |
| `stroke_engine.py` | Multi-pass stroke painter: block_in → focused_pass → detail passes; toon_paint for cel-shading |
| `art_utils.py` | Colour utilities shared across modules |

## CartoonMorphology Presets

```python
from cartoon_morphology import CartoonMorphology

CartoonMorphology.realistic()   # all 1.0 — no exaggeration
CartoonMorphology.stylized()    # subtle: bigger eyes, smaller nose
CartoonMorphology.cartoon()     # clear toon: large cranium + eyes, tiny nose
CartoonMorphology.chibi()       # extreme: huge head, minimal face features
```

Pass a morphology instance to `Character`:

```python
from scene_schema import Character
from cartoon_morphology import CartoonMorphology

char = Character(
    morphology = CartoonMorphology.cartoon(),
    ...
)
```

## Lighting

All run scripts use a single Rembrandt key light (`LightRig.rembrandt()`).
Maintaining an 8:1 key:fill ratio is critical — any fill light placed in the
wrong position will illuminate the shadow cheek more than the key illuminates
the lit side, collapsing the Rembrandt effect.

## Examples

| Script | What it shows |
|--------|--------------|
| `examples/run_v20.py` | Single-key Rembrandt, close camera (-22° head turn) |
| `examples/run_v21.py` | v20 + tight face ellipse, figure mask intersection, selective highlights |
| `examples/run_cartoon_v1.py` | Cartoon morphology through the same pipeline |

## Architecture Notes

- **head_builder** pre-computes all morphology-scaled parameters as Python literals before
  generating the Blender script. The Blender interpreter never imports `CartoonMorphology`.
- **focused_pass** intersects the face ellipse with the figure mask to prevent bright strokes
  appearing in the background behind the hair.
- **place_lights** uses `lum^4.5` weighting so only true specular highlights receive detail
  strokes — not moderately-lit hair.
- **Normal map** is encoded with `VectorMath MULTIPLY_ADD (×0.5+0.5)` in Blender and decoded
  in the stroke engine as `pixel*2-1 → [-1,1]` world normals.
