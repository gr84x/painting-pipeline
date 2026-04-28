# CLAUDE.md — painting-pipeline

Procedural portrait painting system. Describes a scene in Python → generates a 3D figure in Blender → renders reference + normal maps → repaints with a multi-pass stroke engine mimicking oil painting.

---

## NEVER

- Call Blender directly with `bpy` inside the main Python process — always go through `blender_bridge.py` which spawns Blender as a subprocess
- Save output images inside `src/` — outputs go to the configured output directory (default: project root or `examples/output/`)
- Change `scene_schema.py` dataclass field names without updating all callers — these are the contract between scene description and rendering
- Commit large PNG output files to git

## ALWAYS

- Ensure Blender 4.x+ is on PATH before running any pipeline step
- Use the `CartoonMorphology` presets in `cartoon_morphology.py` as the starting point for new character styles
- Run existing tests before adding new pipeline stages: `python -m pytest test_art_catalog.py test_pipeline_routing.py -v`
- Add a new example script under `examples/` for any new scene type or feature

---

## Key Locations

| What | Where |
|---|---|
| Scene dataclasses | `scene_schema.py` |
| Blender bridge | `blender_bridge.py` |
| Head/face/figure mesh | `head_builder.py`, `face_builder.py`, `figure_builder.py` |
| Morphology presets | `cartoon_morphology.py` |
| Costume generation | `costume_builder.py` |
| Stroke painting engine | `stroke_engine.py` |
| Color utilities | `art_utils.py` |
| Example entry points | `examples/run_v20.py`, `examples/run_v21.py`, `examples/run_cartoon_v1.py` |
| Tests | `test_art_catalog.py`, `test_pipeline_routing.py` |

## Dev Quick Reference

```bash
# Verify Blender is available
blender --version

# Run an example
python examples/run_cartoon_v1.py

# Run tests
python -m pytest test_art_catalog.py test_pipeline_routing.py -v
```

## Gotchas

- Blender subprocess calls are slow (seconds per render) — batch renders when possible
- The stroke engine does broad wash passes first, then detail passes; changing pass order significantly alters output style
- `sd_bridge.py` integrates with a local Stable Diffusion server — set `SD_API_URL` if using that path
