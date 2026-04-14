"""
blender_bridge.py — Generates and executes Blender Python scripts from Scene objects.

Pipeline:
  Scene → blender_scene_script() → temp .py file
        → subprocess: blender --background --python scene.py -- --output ref.png
        → ref.png (reference for stroke engine)

Blender coordinate system: Z-up, Y points toward viewer (right-hand).
"""

from __future__ import annotations
import subprocess
import tempfile
import os
import sys
import textwrap
from pathlib import Path

# Adjust if Blender is installed elsewhere
BLENDER_PATHS = [
    r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender\blender.exe",
    "blender",   # if on PATH
]


def find_blender() -> str:
    """Locate the Blender executable."""
    for path in BLENDER_PATHS:
        if Path(path).exists():
            return path
    # Try PATH
    import shutil
    found = shutil.which("blender")
    if found:
        return found
    raise FileNotFoundError(
        "Blender not found. Install via: winget install BlenderFoundation.Blender"
    )


def blender_scene_script(scene) -> str:
    """
    Generate a complete Blender Python script from a Scene object.

    The script:
      1. Clears the default scene
      2. Adds a MakeHuman-compatible metarig via Rigify (or a simple mesh proxy)
      3. Sets pose, expression, costume
      4. Configures camera, lights, environment
      5. Renders to the output path passed via sys.argv
    """
    from scene_schema import (LightRig, Period, Medium, Archetype,
                               Pose, Expression, EnvType)

    # Collect values
    subj      = scene.subjects[0] if scene.subjects else None
    cam       = scene.camera
    env       = scene.environment
    style     = scene.style
    rig       = scene.lighting

    # Compute face center height so we can point area lights directly at the face.
    # Without Track To constraints, AREA lights default to facing -Z (down) and
    # illuminate the top of the skull instead of the face — producing a featureless
    # pale dome no matter how well-positioned the light is.
    from scene_schema import PoseDetail as _PD_lights
    if subj:
        from figure_builder import compute_landmarks as _clm_lights
        _lm_lights = _clm_lights(subj.pose.name,
                                  getattr(subj, "pose_detail", _PD_lights()))
        _face_z = _lm_lights["head_ctr"][2]
        _face_x = _lm_lights["head_ctr"][0]
        _face_y = _lm_lights["head_ctr"][1]
    else:
        _face_x, _face_y, _face_z = 0.0, 0.0, 1.2

    # Light definitions as Python literal
    lights_code = []
    for i, lt in enumerate(rig.lights):
        lights_code.append(
f"bpy.ops.object.light_add(type='{lt.kind}', location=({lt.position.x}, {lt.position.y}, {lt.position.z}))\n"
f"_lt = bpy.context.object\n"
f"_lt.name = 'Light_{i}'\n"
f"_lt.data.energy = {lt.intensity}\n"
f"_lt.data.color  = ({lt.color[0]}, {lt.color[1]}, {lt.color[2]})\n"
f"if '{lt.kind}' == 'AREA':\n"
f"    _lt.data.size = 2.0\n"
f"    # Track To: rotate light so it points directly at the figure's face.\n"
f"    # Without this, area lights face -Z (down) and only illuminate the top\n"
f"    # of the skull, giving a featureless pale dome instead of a lit face.\n"
f"    bpy.ops.object.empty_add(type='PLAIN_AXES', location=({_face_x:.4f}, {_face_y:.4f}, {_face_z:.4f}))\n"
f"    _lt_tgt_{i} = bpy.context.object\n"
f"    _lt_tgt_{i}.name = '_LTgt_{i}'\n"
f"    bpy.context.view_layer.objects.active = _lt\n"
f"    _lt.select_set(True)\n"
f"    _lt_track_{i} = _lt.constraints.new(type='TRACK_TO')\n"
f"    _lt_track_{i}.target     = _lt_tgt_{i}\n"
f"    _lt_track_{i}.track_axis = 'TRACK_NEGATIVE_Z'\n"
f"    _lt_track_{i}.up_axis    = 'UP_Y'\n"
        )
    lights_str = "\n".join(lights_code)

    # Subject figure — built by figure_builder using metaballs + correct proportions
    subject_code = ""
    if subj:
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).parent))
        from figure_builder import build_figure_code
        subject_code = build_figure_code(subj)

    # Environment / world
    atm = env.atmosphere
    gc  = env.ground_color
    amb = rig.ambient_color
    amb_s = rig.ambient_strength

    # Camera
    cx, cy, cz = cam.position.x, cam.position.y, cam.position.z
    tx, ty, tz = cam.target.x,   cam.target.y,   cam.target.z

    script = f"""
import bpy
import math
import sys

# ── Parse output path from args ───────────────────────────────────────────────
argv   = sys.argv
sep    = argv.index('--') if '--' in argv else len(argv)
output = argv[sep + 2] if len(argv) > sep + 2 else '/tmp/render.png'

# ── Clean default scene ───────────────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in bpy.data.meshes:
    bpy.data.meshes.remove(block)

# ── Render engine: Cycles (accurate lighting, low samples for speed) ──────────
scene = bpy.context.scene
scene.render.engine         = 'CYCLES'
scene.cycles.samples        = 128
scene.cycles.use_denoising  = True
scene.render.resolution_x   = {scene.width}
scene.render.resolution_y   = {scene.height}
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath       = output

# ── World / environment ───────────────────────────────────────────────────────
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new('World')
    scene.world = world
# Set flat dark ambient — no sky, no blue
world.use_nodes = True
_wnt = world.node_tree
_wbg = _wnt.nodes.get('Background') or _wnt.nodes.new('ShaderNodeBackground')
_wbg.inputs['Color'].default_value    = ({amb[0]}, {amb[1]}, {amb[2]}, 1.0)
_wbg.inputs['Strength'].default_value = {amb_s}
# Ensure Background is connected to output
_wout = _wnt.nodes.get('World Output') or _wnt.nodes.new('ShaderNodeOutputWorld')
if not _wout.inputs['Surface'].is_linked:
    _wnt.links.new(_wbg.outputs['Background'], _wout.inputs['Surface'])

# ── Ground plane ──────────────────────────────────────────────────────────────
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.object
ground.name = 'Ground'
gmat = bpy.data.materials.new('Ground')
gmat.use_nodes = True
_gnt   = gmat.node_tree
_gnt.nodes.clear()
_gout  = _gnt.nodes.new('ShaderNodeOutputMaterial')
_gbsdf = _gnt.nodes.new('ShaderNodeBsdfPrincipled')
_gbsdf.inputs['Base Color'].default_value = ({gc[0]}, {gc[1]}, {gc[2]}, 1.0)
_gnt.links.new(_gbsdf.outputs['BSDF'], _gout.inputs['Surface'])
ground.data.materials.clear()
ground.data.materials.append(gmat)

# ── Dark vertical backdrop ────────────────────────────────────────────────────
# Placed 1.5 m behind the figure at Y=+1.5, tall enough to fill the frame.
# Near-black matte material so the stroke engine sees only dark colour behind
# the subject — prevents warm ground reflections from polluting background strokes.
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 1.5, 1.2))
backdrop = bpy.context.object
backdrop.name = 'Backdrop'
backdrop.rotation_euler = (1.5708, 0, 0)   # rotate 90° around X → vertical
bkmat = bpy.data.materials.new('Backdrop')
bkmat.use_nodes = True
_bknt   = bkmat.node_tree
_bknt.nodes.clear()
_bkout  = _bknt.nodes.new('ShaderNodeOutputMaterial')
_bkbsdf = _bknt.nodes.new('ShaderNodeBsdfPrincipled')
_bkbsdf.inputs['Base Color'].default_value = (0.010, 0.008, 0.006, 1.0)
_bkbsdf.inputs['Roughness'].default_value  = 1.0
_bknt.links.new(_bkbsdf.outputs['BSDF'], _bkout.inputs['Surface'])
backdrop.data.materials.clear()
backdrop.data.materials.append(bkmat)

# ── Lights ────────────────────────────────────────────────────────────────────
{lights_str}

# ── Subject ───────────────────────────────────────────────────────────────────
{subject_code}

# ── Camera ────────────────────────────────────────────────────────────────────
bpy.ops.object.camera_add(location=({cx}, {cy}, {cz}))
cam_obj = bpy.context.object
cam_obj.name = 'Camera'
scene.camera = cam_obj

# Point camera at target using Track To constraint
bpy.ops.object.empty_add(type='PLAIN_AXES', location=({tx}, {ty}, {tz}))
target_empty = bpy.context.object
target_empty.name = 'CameraTarget'

track = cam_obj.constraints.new(type='TRACK_TO')
track.target     = target_empty
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis    = 'UP_Y'

cam_obj.data.lens_unit = 'FOV'
cam_obj.data.angle     = math.radians({cam.fov})

# ── Render ────────────────────────────────────────────────────────────────────
bpy.ops.render.render(write_still=True)
print(f'Rendered: {{output}}')

# ── Figure mask render ────────────────────────────────────────────────────────
# Quick 1-sample emission pass: figure objects = white, all else = black.
# Gives a clean binary silhouette mask for the stroke engine.
_FIGURE_NAMES = {{'Figure', 'Hair', 'Face', 'Dress'}}

# Save all current material lists keyed by object name
_saved_mats = {{}}
for _o in bpy.data.objects:
    _d = getattr(getattr(_o, 'data', None), 'materials', None)
    if _d is not None:
        _saved_mats[_o.name] = list(_d)

# White emission material for figure objects
_wem = bpy.data.materials.new('_MaskWhite')
_wem.use_nodes = True
_wem.node_tree.nodes.clear()
_wem_out = _wem.node_tree.nodes.new('ShaderNodeOutputMaterial')
_wem_em  = _wem.node_tree.nodes.new('ShaderNodeEmission')
_wem_em.inputs['Color'].default_value    = (1.0, 1.0, 1.0, 1.0)
_wem_em.inputs['Strength'].default_value = 1.0
_wem.node_tree.links.new(_wem_em.outputs['Emission'], _wem_out.inputs['Surface'])

# Black emission material for background objects
_bem = bpy.data.materials.new('_MaskBlack')
_bem.use_nodes = True
_bem.node_tree.nodes.clear()
_bem_out = _bem.node_tree.nodes.new('ShaderNodeOutputMaterial')
_bem_em  = _bem.node_tree.nodes.new('ShaderNodeEmission')
_bem_em.inputs['Color'].default_value    = (0.0, 0.0, 0.0, 1.0)
_bem_em.inputs['Strength'].default_value = 1.0
_bem.node_tree.links.new(_bem_em.outputs['Emission'], _bem_out.inputs['Surface'])

# Swap all object materials
for _o in bpy.data.objects:
    _d = getattr(getattr(_o, 'data', None), 'materials', None)
    if _d is None:
        continue
    _mat = _wem if _o.name in _FIGURE_NAMES else _bem
    _d.clear()
    _d.append(_mat)

# Kill world so background is pure black
_wbg.inputs['Color'].default_value    = (0.0, 0.0, 0.0, 1.0)
_wbg.inputs['Strength'].default_value = 0.0

# Render mask at 1 sample — almost instant
scene.cycles.samples       = 1
scene.cycles.use_denoising = False
_mask_path = output.replace('.png', '_mask.png')
scene.render.filepath = _mask_path
bpy.ops.render.render(write_still=True)
print(f'Mask: {{_mask_path}}')

# Restore all original materials
for _o in bpy.data.objects:
    _d = getattr(getattr(_o, 'data', None), 'materials', None)
    if _d is None:
        continue
    _d.clear()
    for _m in _saved_mats.get(_o.name, []):
        _d.append(_m)

# ── Normal map render ─────────────────────────────────────────────────────────
# Outputs per-pixel world-space normals encoded as (N+1)/2 → RGB.
# Used by the stroke engine for: toon contour detection, stroke direction,
# hard shadow boundary computation.
# 1 sample, no denoising, background = grey (0.5, 0.5, 0.5).

_nem = bpy.data.materials.new('_NormalEmit')
_nem.use_nodes = True
_nem.node_tree.nodes.clear()
_nem_out = _nem.node_tree.nodes.new('ShaderNodeOutputMaterial')
_nem_geo = _nem.node_tree.nodes.new('ShaderNodeNewGeometry')
_nem_map = _nem.node_tree.nodes.new('ShaderNodeVectorMath')
_nem_map.operation = 'MULTIPLY_ADD'
_nem_map.inputs[1].default_value = (0.5, 0.5, 0.5)
_nem_map.inputs[2].default_value = (0.5, 0.5, 0.5)
_nem.node_tree.links.new(_nem_geo.outputs['Normal'], _nem_map.inputs[0])
_nem_emit = _nem.node_tree.nodes.new('ShaderNodeEmission')
_nem.node_tree.links.new(_nem_map.outputs['Vector'], _nem_emit.inputs['Color'])
_nem.node_tree.links.new(_nem_emit.outputs['Emission'], _nem_out.inputs['Surface'])

# Background = (0.5, 0.5, 0.5) = neutral normal (no surface)
_wbg.inputs['Color'].default_value    = (0.5, 0.5, 0.5, 1.0)
_wbg.inputs['Strength'].default_value = 1.0

for _o in bpy.data.objects:
    _d = getattr(getattr(_o, 'data', None), 'materials', None)
    if _d is None: continue
    if _o.name in _FIGURE_NAMES:
        _d.clear(); _d.append(_nem)
    else:
        _d.clear(); _d.append(_bem)

scene.cycles.samples       = 1
scene.cycles.use_denoising = False
_normal_path = output.replace('.png', '_normals.png')
scene.render.filepath = _normal_path
bpy.ops.render.render(write_still=True)
print(f'Normals: {{_normal_path}}')

# Re-restore materials after normal map pass (we just cleared them again above)
for _o in bpy.data.objects:
    _d = getattr(getattr(_o, 'data', None), 'materials', None)
    if _d is None:
        continue
    _d.clear()
    for _m2 in _saved_mats.get(_o.name, []):
        _d.append(_m2)

# Restore world
_wbg.inputs['Color'].default_value    = ({amb[0]}, {amb[1]}, {amb[2]}, 1.0)
_wbg.inputs['Strength'].default_value = {amb_s}
"""
    return textwrap.dedent(script)


def render_scene(scene, output_path: str, verbose: bool = False) -> str:
    """
    Render a Scene to a PNG via Blender headless.

    Returns the path to the rendered PNG.
    """
    blender = find_blender()

    # Write the generated script to a temp file
    with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", prefix="blender_scene_",
            delete=False, encoding="utf-8") as f:
        f.write(blender_scene_script(scene))
        script_path = f.name

    try:
        cmd = [
            blender,
            "--background",
            "--python", script_path,
            "--",
            "--output", output_path,
        ]
        print(f"Running Blender: {' '.join(cmd[:4])} ... --output {output_path}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if verbose:
            print(result.stdout[-2000:] if result.stdout else "")
        if result.returncode != 0:
            err = result.stderr[-2000:] if result.stderr else "(no stderr)"
            raise RuntimeError(f"Blender exited {result.returncode}:\n{err}")
    finally:
        os.unlink(script_path)

    return output_path


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: scene → painting in one call
# ─────────────────────────────────────────────────────────────────────────────

def _project_to_image(world_pt, cam_pos, cam_target, fov_deg, W, H):
    """
    Project a world-space point onto image pixel coordinates.
    Returns (u, v) pixel position, or (W//2, H//2) as fallback.
    """
    import math
    # Camera basis vectors
    def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
    def dot(a, b): return sum(a[i]*b[i] for i in range(3))
    def cross(a, b):
        return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    def norm(v):
        m = math.sqrt(dot(v, v)) or 1e-9
        return (v[0]/m, v[1]/m, v[2]/m)

    cam = (cam_pos.x, cam_pos.y, cam_pos.z)
    tgt = (cam_target.x, cam_target.y, cam_target.z)
    wp  = world_pt

    fwd   = norm(sub(tgt, cam))
    up    = (0, 0, 1)
    right = norm(cross(fwd, up))
    if dot(right, right) < 1e-6:
        up = (0, 1, 0)
        right = norm(cross(fwd, up))
    up_c  = norm(cross(right, fwd))

    d = sub(wp, cam)
    pz = dot(d, fwd)
    if pz < 1e-4:
        return W // 2, H // 2

    px = dot(d, right)
    py = dot(d, up_c)

    tan_h = math.tan(math.radians(fov_deg / 2))
    ndcx  =  px / (pz * tan_h)
    aspect = H / W
    ndcy  = -py / (pz * tan_h * aspect)  # image Y flipped

    u = int((ndcx + 1) / 2 * W)
    v = int((ndcy + 1) / 2 * H)
    return max(0, min(W-1, u)), max(0, min(H-1, v))


def scene_to_painting(scene, output_path: str, verbose: bool = False) -> str:
    """
    Full pipeline: Scene → Blender render → stroke engine → painting PNG.
    Returns path to the final painting.
    """
    sys.path.insert(0, str(Path(__file__).parent))
    from PIL import Image
    from stroke_engine import (Painter, ellipse_mask, spherical_flow,
                               flow_field, ellipse_mask)
    from figure_builder import compute_landmarks
    from scene_schema import PoseDetail

    # Step 1: Blender reference render (also writes _mask.png and _normals.png alongside)
    ref_path     = output_path.replace(".png", "_ref.png")
    mask_path    = output_path.replace(".png", "_ref_mask.png")
    normals_path = output_path.replace(".png", "_ref_normals.png")
    render_scene(scene, ref_path, verbose=verbose)

    # Step 2: Stroke engine pass
    sp = scene.style.stroke_params
    ref = Image.open(ref_path).convert("RGB")
    W, H = ref.size

    p = Painter(W, H)

    # Load figure mask if the Blender mask pass was written
    if Path(normals_path).exists():
        p.set_normal_map(normals_path)

    if Path(mask_path).exists():
        p.set_figure_mask(mask_path)
        # Seal background first — copies reference bg pixels to canvas so no
        # figure stroke can ever contaminate the dark background area
        p.seal_background(ref)
        # A few large atmospheric strokes in background region for texture
        p.background_pass(ref, n_strokes=50, stroke_size=60)
    else:
        if verbose:
            print("  [warn] No figure mask found — painting without region separation")

    p.tone_ground((0.22, 0.17, 0.10), texture_strength=0.10)
    p.underpainting(ref, stroke_size=int(sp["stroke_size_bg"] * 1.4), n_strokes=180)
    p.block_in(ref,     stroke_size=int(sp["stroke_size_bg"]),         n_strokes=320)
    p.build_form(ref,   stroke_size=int(sp["stroke_size_bg"] * 0.5),   n_strokes=800)

    # Face-focused passes: project the face center through the camera to get
    # the correct pixel position for each scene configuration.
    if scene.subjects:
        subj = scene.subjects[0]
        lm   = compute_landmarks(subj.pose.name,
                                 getattr(subj, "pose_detail", PoseDetail()))
        face_world = lm["head_ctr"]       # (x, y, z) in world space
        # Vec3 wrapper for projection
        class _P:
            def __init__(self, t): self.x, self.y, self.z = t
        face_pt = _P(face_world)

        cx, cy = _project_to_image(
            (face_world[0], face_world[1], face_world[2]),
            scene.camera.position,
            scene.camera.target,
            scene.camera.fov,
            W, H,
        )

        # Head radius in pixels: project a point offset by HR in world X
        from figure_builder import R as RADII
        HR = RADII["head"]
        edge_x, _ = _project_to_image(
            (face_world[0] + HR, face_world[1], face_world[2]),
            scene.camera.position, scene.camera.target, scene.camera.fov, W, H,
        )
        rx = max(30, abs(edge_x - cx))
        ry = int(rx * 1.35)   # heads are taller than wide

        print(f"  Face projected to ({cx}, {cy}), rx={rx}, ry={ry}")

        # Tighter face ellipse: was rx*1.25, ry*1.20 — that extended into hair.
        # Now rx*1.0, ry*0.95 keeps the mask within the face geometry.
        face_mask  = ellipse_mask(W, H, cx, cy, rx * 1.00, ry * 0.95, feather=0.28)
        face_flow  = spherical_flow(W, H, cx, cy, rx, ry)
        eyes_mask  = ellipse_mask(W, H, cx, cy - ry//4, rx * 0.80, ry * 0.50, feather=0.22)
        lips_mask  = ellipse_mask(W, H, cx, cy + ry//2, rx * 0.50, ry * 0.28, feather=0.28)

        p.focused_pass(ref, face_mask,  stroke_size=int(sp["stroke_size_face"]*1.8),
                       n_strokes=1200, opacity=0.80, wet_blend=sp["wet_blend"],
                       form_angles=face_flow)
        p.focused_pass(ref, eyes_mask,  stroke_size=sp["stroke_size_face"],
                       n_strokes=800,  opacity=0.82, wet_blend=sp["wet_blend"]*0.6,
                       form_angles=face_flow)
        p.focused_pass(ref, lips_mask,  stroke_size=max(3, sp["stroke_size_face"]-2),
                       n_strokes=500,  opacity=0.84, wet_blend=sp["wet_blend"]*0.6,
                       form_angles=face_flow)

    p.place_lights(ref, stroke_size=sp["stroke_size_face"], n_strokes=500)
    p.glaze((0.60, 0.42, 0.14), opacity=0.07)
    p.finish(vignette=0.50, crackle=True)
    p.save(output_path)

    return output_path
