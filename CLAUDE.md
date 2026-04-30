# CLAUDE.md — painting-pipeline

Procedural painting system. Each session describes a scene, renders a reference image, then repaints it with a multi-pass stroke engine that mimics oil painting technique. A new artist mode (painting pass) is added every session.

---

## How a Session Works

Every session produces four things, committed together on a `session/NNN-artist-name` branch:

| File | Purpose |
|---|---|
| `paint_sNNN_<title>.py` | Main script: builds reference → paints → saves PNG |
| `add_sNNN_passes.py` | Inserts the new pass method(s) into `stroke_engine.py` |
| `add_sNNN_catalog.py` | Inserts the new artist entry into `art_catalog.py` |
| `sNNN_<title>.png` | Final output (posted to Discord) |

Run `add_sNNN_passes.py` and `add_sNNN_catalog.py` once each before running the paint script. They modify `stroke_engine.py` and `art_catalog.py` in place.

---

## Reference Image — CRITICAL

**The stroke engine paints *over* a reference. The reference determines form. Without good form in the reference, the output will be formless regardless of how many passes run.**

### Figurative and animal subjects → use Blender

Any session with a human figure, portrait, animal, creature, or character **must** use `blender_bridge.scene_to_painting()` to generate the reference. Blender provides real 3D geometry, lighting, and depth — the stroke engine resolves that into painted form.

```python
from scene_schema import Scene, Character, Camera, LightRig, Style, Medium, Period, PaletteHint, Vec3, Pose, SkinTone, Expression, Environment, EnvType
from blender_bridge import scene_to_painting

scene = Scene(
    subjects=[Character(
        pose      = Pose.SEATED,
        skin_tone = SkinTone.LIGHT,
        expression= Expression.ENIGMATIC,
    )],
    camera  = Camera(position=Vec3(-0.12, -1.2, 1.0), target=Vec3(0, 0, 1.10), fov=22),
    lighting= LightRig.rembrandt(),
    environment=Environment(type=EnvType.INTERIOR),
    style   = Style(medium=Medium.OIL, period=Period.RENAISSANCE, palette=PaletteHint.WARM_EARTH),
    width=780, height=1080,
    title="session_title",
)

ref_path = scene_to_painting(scene, "output.png", verbose=True)
ref = np.array(Image.open(ref_path)).astype(np.float32) / 255.0
```

Blender is installed at `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`. `find_blender()` locates it automatically.

### Anatomy weight maps — use for all figurative subjects

After obtaining a Blender reference, build an anatomy weight map and assign it to the painter. This concentrates strokes on anatomically significant features (eyes, beak, mane, etc.).

```python
from anatomy import subjects, PlacedAnatomy, build_combined_weight_map

# Match cx/cy/rx/ry to where the subject's head/body sits in the render
placed = [PlacedAnatomy(anatomy=subjects.get("human_portrait"), cx=390, cy=400, rx=160, ry=200)]
weight_map = build_combined_weight_map(placed, canvas_w=W, canvas_h=H)
if weight_map is not None:
    p._comp_map = weight_map
```

Available subjects: `subjects.list_subjects()` — 42 entries covering human portrait, mammals, birds, reptiles, insects, aquatic, and hybrid creatures. Use `anatomy.hybrid` to blend or modify anatomies for non-standard subjects.

### Landscape, abstract, and still-life subjects → procedural Python

When there is no figurative subject, build the reference image with numpy/PIL directly in a `build_reference()` function. No Blender needed.

---

## Adding a New Session

1. **Choose the artist and subject.** Check `art_catalog.py` — the artist must not already exist.
2. **Check `art_catalog.py`** for the current session number and the most recent improvement added.
3. **Design the scene.** For figurative subjects, compose a `Scene` object. For landscapes/abstracts, write `build_reference()`.
4. **Write `add_sNNN_passes.py`** — inserts one new artist pass method into `stroke_engine.py` (and optionally one pipeline improvement method). The pass name is `paint_<artist>_<style>_pass()` or similar.
5. **Write `add_sNNN_catalog.py`** — inserts the artist's `ArtStyle` entry into `CATALOG` in `art_catalog.py`.
6. **Write `paint_sNNN_<title>.py`** — assembles the full pipeline: reference → painter → passes → save.
7. **Run in order:** `add_passes` → `add_catalog` → `paint` script.
8. **Commit** on a `session/NNN-artist-name` branch, then open a PR to merge to main.

---

## Stroke Engine Basics

`Painter(W, H, seed=NNN)` — canvas in float32 RGB.

**Standard pass order** (matches real oil painting practice):

```python
p = Painter(W, H, seed=NNN)
p.tone_ground(color, texture_strength=0.02)   # toned linen ground
p.underpainting(ref, ...)                      # monochrome structure
p.block_in(ref, stroke_size=28, n_strokes=320) # broad masses
p.build_form(ref, stroke_size=14, n_strokes=280) # modelling
p.place_lights(ref, stroke_size=6, n_strokes=160) # lights and accents
# ... artist-specific passes ...
p.save("output.png")
```

**Stroke counts:** Use at least 280–400 for `block_in`, 240–320 for `build_form`, 140–200 for `place_lights` on a standard canvas. Sparse strokes leave the ground showing through — increase counts if coverage looks thin.

**Canvas sizes:** 760×900 to 1040×1440 depending on subject. Portraits and animals benefit from larger canvases (1040×1440) for feature resolution.

**`p._comp_map`** — assign a float32 `(H, W)` weight map to bias stroke placement toward features. Values >1 attract more strokes. Built by `build_combined_weight_map()` from the anatomy module.

---

## Key Files

| File | Purpose |
|---|---|
| `stroke_engine.py` | The painter — 170+ pass methods, ~63k lines |
| `art_catalog.py` | Artist entries: palette, technique, inspiration |
| `scene_schema.py` | Scene dataclasses: Character, Camera, LightRig, Style, etc. |
| `blender_bridge.py` | Generates Blender scripts, runs renders, returns reference path |
| `head_builder.py` | Parametric head mesh generation (used by blender_bridge) |
| `anatomy/` | Anatomy database — 42 subjects, weight map builder, flow field builder |
| `anatomy/hybrid.py` | Blend, graft, mirror, scale anatomy definitions |
| `examples/` | Full working example scripts (Rembrandt, Sorolla, Kusama, etc.) |

---

## NEVER

- Build a purely procedural reference for a figurative or animal subject — use Blender
- Skip the anatomy weight map for any session that has a figure or animal in frame
- Add an artist who already exists in `art_catalog.py`
- Commit large PNG output files without checking `.gitignore`
- Call Blender directly with `bpy` — always go through `blender_bridge.py`
- Run `add_passes` or `add_catalog` scripts more than once (they modify files in place)

## ALWAYS

- Check `art_catalog.py` for the current session number before starting
- Verify Blender is reachable: `from blender_bridge import find_blender; find_blender()`
- Write the image description in the session script docstring (subject, composition, technique, palette, mood)
- Match the `PlacedAnatomy` bounding ellipse to where the subject actually sits in the Blender render
- Use the most recent pipeline improvement from the previous session as a baseline
