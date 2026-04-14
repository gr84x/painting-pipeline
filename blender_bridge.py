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
                               flow_field, anatomy_flow_field)
    from figure_builder import compute_landmarks
    from scene_schema import PoseDetail, Period, Medium, Style
    from art_catalog import CATALOG as _ART_CATALOG

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

    is_pointillist       = (scene.style.period == Period.POINTILLIST)
    is_ukiyo_e           = (scene.style.period == Period.UKIYO_E)
    is_watercolor        = (scene.style.medium == Medium.WATERCOLOR)
    is_proto_expressionist = (scene.style.period == Period.PROTO_EXPRESSIONIST)
    is_realist           = (scene.style.period == Period.REALIST)
    is_viennese_expressionist = (scene.style.period == Period.VIENNESE_EXPRESSIONIST)
    is_color_field       = (scene.style.period == Period.COLOR_FIELD)
    is_synthetist        = (scene.style.period == Period.SYNTHETIST)
    is_mannerist         = (scene.style.period == Period.MANNERIST)
    is_surrealist        = (scene.style.period == Period.SURREALIST)
    is_abstract_expressionist = (scene.style.period == Period.ABSTRACT_EXPRESSIONIST)
    is_romantic          = (scene.style.period == Period.ROMANTIC)
    is_venetian          = (scene.style.period == Period.VENETIAN_RENAISSANCE)
    is_fauvist           = (scene.style.period == Period.FAUVIST)
    is_primitivist       = (scene.style.period == Period.PRIMITIVIST)
    is_early_netherlandish = (scene.style.period == Period.EARLY_NETHERLANDISH)
    # Renaissance with high edge_softness triggers the improved sfumato veil pass
    is_renaissance_soft  = (scene.style.period == Period.RENAISSANCE
                             and sp.get("edge_softness", 0.0) >= 0.80)

    if is_proto_expressionist:
        # ── Proto-Expressionist pipeline (Goya Black Paintings technique) ────
        # Near-black ground; figures consumed by void; crude spatula-like marks.
        # Goya's palette is predominantly void — there is almost no paint, only
        # the darkness that surrounds and dissolves what little light exists.
        goya_style = _ART_CATALOG.get("goya")
        ground_col = goya_style.ground_color if goya_style else (0.04, 0.03, 0.02)
        flesh_col  = (0.68, 0.55, 0.35)   # ashen ochre
        accent_col = (0.72, 0.18, 0.08)   # blood red

        # Black-ground tone — extremely dark, almost nothing visible on canvas
        p.tone_ground(ground_col, texture_strength=0.12)

        # No underpainting — Goya worked directly and crudely onto the dark ground.
        # A single coarse block-in to establish figure masses before the void pass.
        p.block_in(ref, stroke_size=int(sp["stroke_size_bg"]), n_strokes=120)

        # Dark void pass: voids background, adds crude figure strokes, void encroachment
        p.dark_void_pass(
            ref,
            void_darkness = 0.94,
            n_strokes     = 600,
            stroke_size   = float(sp["stroke_size_face"]),
            flesh_color   = flesh_col,
            accent_color  = accent_col,
            accent_prob   = 0.07,
            void_depth    = 0.75,
        )

        # A single final very dark glaze — Goya's world is never quite black,
        # it is a dark warm amber-brown at the deepest shadows.
        p.glaze((0.18, 0.10, 0.04), opacity=0.12)
        # Heavy vignette crushes edges further into void; no crackle — plaster not canvas.
        p.finish(vignette=0.75, crackle=False)

    elif is_color_field:
        # ── Color Field pipeline (Mark Rothko technique) ──────────────────────
        # Rothko painted on unprimed or lightly sized raw canvas.  He used
        # rabbit-skin glue sizing to control how paint absorbed into the surface,
        # and worked in acrylic from the mid-1960s — but the visual language is
        # identical: vast horizontal bands of colour built up from many thin
        # semi-transparent washes over a very dark absorbing ground.
        #
        # Pipeline:
        #   1. Very dark warm ground — the absorbing void that makes light bands
        #      appear self-luminous by simultaneous contrast.
        #   2. Standard oil underpainting + block_in so a figure reading persists
        #      beneath the color field washes.
        #   3. color_field_pass() — the signature Rothko technique: horizontal
        #      bands analysed from reference, each built with many transparent
        #      washes with chromatic vibration at the boundaries.  figure_preserve
        #      blends the underpainting back so the figure is sensed but not named.
        #   4. Minimal finish — no crackle (modern canvas sizing), very light
        #      vignette.
        rothko_style = _ART_CATALOG.get("rothko")
        ground_col   = rothko_style.ground_color if rothko_style else (0.12, 0.06, 0.04)

        # Dark absorbing void ground — this is what makes Rothko's light bands
        # seem to glow.  Very low texture_strength: raw canvas has minimal tooth.
        p.tone_ground(ground_col, texture_strength=0.04)

        # Underpainting and block_in preserve the figure anatomy beneath the
        # color field so the form reads as "a warmth within the field."
        p.underpainting(ref, stroke_size=int(sp["stroke_size_bg"] * 1.5), n_strokes=140)
        p.block_in(ref,     stroke_size=int(sp["stroke_size_bg"]),         n_strokes=260)

        # Core Rothko technique: luminous horizontal bands with optical depth
        p.color_field_pass(
            ref,
            n_bands              = 3,
            n_washes             = 15,
            wash_opacity         = float(sp["wet_blend"]) * 0.26,
            edge_blur_sigma      = H * 0.04,   # ~4% of canvas height
            figure_preserve      = 0.62,
            chromatic_vibration  = 0.04,
            band_hue_drift       = 0.016,
        )

        # Place lights last — in Rothko's paintings the brightest zone emerges
        # from the upper band where it catches the studio's skylight.
        p.place_lights(ref, stroke_size=sp["stroke_size_bg"], n_strokes=200)

        # No glaze (Rothko did not varnish — the raw color surface IS the work).
        # Very gentle vignette: the absorbing dark ground already edges the canvas.
        p.finish(vignette=0.22, crackle=False)

    elif is_watercolor:
        # ── Watercolour pipeline (Sargent technique) ─────────────────────────
        # Cold-press watercolor paper ground — replaces the default linen
        # texture with authentic cold-press paper tooth: irregular grain,
        # horizontal laid lines, and chain lines.  Highlight areas left as
        # bare paper show through realistically.
        p.set_substrate("cold_press")
        p.tone_ground((0.96, 0.94, 0.90), texture_strength=0.022)

        # Three-stage watercolour process:
        # 1. Wet-into-wet washes (broad, diluted, soft edges)
        # 2. Sargent drag (dry-brush sparkle on sunlit surfaces)
        # 3. Dark accent strokes (crisp loaded-brush darks placed last)
        # Paper-threshold: leave anything brighter than 0.80 lum as bare paper.
        p.watercolor_wash_pass(
            ref,
            n_washes         = 8,
            wash_opacity     = float(sp["wet_blend"]) * 0.45,
            drag_strokes     = 200,
            drag_size        = float(sp["stroke_size_bg"]),
            dark_strokes     = 400,
            dark_opacity     = 0.72,
            paper_threshold  = 0.80,
            bloom_prob       = 0.22,
        )

        # Pigment granulation pass — physically-based paper-tooth modulation.
        # Certain watercolour pigments (ultramarine, burnt sienna, cobalt) have
        # large particles that settle into paper hollows as the wash dries,
        # creating a speckled, tactile granular texture.  Applied AFTER the
        # washes so it reads as a property of dried pigment, not a paint layer.
        # Cold-press paper has pronounced tooth that makes this effect vivid.
        p.pigment_granulation_pass(
            strength  = 0.44,
            lum_lo    = 0.08,
            lum_hi    = 0.80,
            tex_mean  = 0.84,   # midpoint of cold-press texture [0.68, 1.0]
        )

        # No oil glaze or crackle — watercolours don't varnish.
        # Light vignette only to frame the paper edges.
        p.finish(vignette=0.18, crackle=False)

    elif is_ukiyo_e:
        # ── Ukiyo-e / woodblock print pipeline (Hokusai technique) ───────────
        # Rice paper ground — pale cream, almost no texture (ukiyo-e used
        # smooth washi paper, not woven linen).
        p.tone_ground((0.90, 0.88, 0.80), texture_strength=0.02)

        # Three-stage woodblock process:
        # 1. Flat colour quantisation (colour blocks)
        # 2. Bokashi Prussian-blue gradient (background atmosphere)
        # 3. Ink keyblock contour lines
        p.woodblock_pass(
            ref,
            n_colors          = 8,            # typical ukiyo-e palette is 6–10 colours
            bokashi_color     = (0.15, 0.38, 0.72),   # Prussian blue (Bokashi)
            bokashi_strength  = 0.42,
            bokashi_vertical  = True,
            contour_weight    = 0.35,
            contour_thickness = float(sp["stroke_size_face"]),
            ink_color         = (0.06, 0.04, 0.10),
        )

        # No glaze — ukiyo-e pigment is transparent watercolour; the cream
        # paper reads through flat colour areas.
        # Very gentle vignette only; no crackle (prints don't age like oil varnish).
        p.finish(vignette=0.12, crackle=False)

    elif is_realist:
        # ── Realist / flat-plane pipeline (Manet technique) ──────────────────
        # Manet laid paint in a small number of discrete tonal planes.  He
        # rejected the academic convention of smoothly graduated chiaroscuro
        # and replaced it with bold flat patches separated by visible (but not
        # hard-outline) boundaries.  A cool mid-tone silver ground, warm cream
        # lights, and rich black used as a positive colour.
        #
        # Pipeline:
        #   1. Mid-tone cool grey ground — not the warm brown of Old Masters.
        #   2. Light block_in to establish composition masses.
        #   3. flat_plane_pass() — the signature Manet technique: quantized
        #      value bands, flat loaded-brush strokes, dark border marks.
        #   4. place_lights() for the brightest impasto highlights.
        #   5. Cool amber glaze (minimal) to unify.
        manet_style  = _ART_CATALOG.get("manet")
        ground_col   = manet_style.ground_color if manet_style else (0.52, 0.50, 0.48)

        # Cool silver-grey ground (not warm sienna — Manet's modernity)
        p.tone_ground(ground_col, texture_strength=0.06)

        # Light composition pass to establish masses before flat planes
        p.block_in(ref, stroke_size=int(sp["stroke_size_bg"]), n_strokes=180)

        # Core Manet technique: flat tonal planes + dark boundary strokes
        p.flat_plane_pass(
            ref,
            n_planes          = 5,
            strokes_per_plane = 600,
            stroke_size       = float(sp["stroke_size_face"]),
            plane_opacity     = 0.82,
            border_strokes    = 350,
            border_size       = float(sp["stroke_size_face"]) * 0.38,
            border_opacity    = 0.88,
            black_color       = (0.06, 0.05, 0.06),
            wet_blend         = sp["wet_blend"],
        )

        # Impasto light placement — Manet's highest highlights are loaded and direct
        p.place_lights(ref, stroke_size=sp["stroke_size_face"], n_strokes=350)

        # Very subtle warm glaze — Manet did not varnish elaborately
        p.glaze((0.55, 0.50, 0.38), opacity=0.04)
        # Moderate vignette; no crackle (modern technique)
        p.finish(vignette=0.35, crackle=False)

    elif is_viennese_expressionist:
        # ── Viennese Expressionist pipeline (Egon Schiele technique) ─────────
        # Schiele worked on paper, not oil canvas.  His figures exist in near-void,
        # painted with flat, barely-modelled pallid flesh against blank paper.
        # The contour line is the primary instrument; colour is secondary.
        #
        # Pipeline:
        #   1. Off-white paper ground — no texture (smooth paper, not linen).
        #   2. angular_contour_pass() — flat interior fill (desaturated, greenish
        #      flesh) + fractured angular contour lines + sparse blood-red accent.
        #   3. Minimal finish: very light vignette to preserve the paper void;
        #      no glaze, no crackle.
        schiele_style = _ART_CATALOG.get("egon_schiele")
        ground_col    = schiele_style.ground_color if schiele_style else (0.94, 0.91, 0.85)

        # Off-white paper ground — very fine texture, almost none
        p.tone_ground(ground_col, texture_strength=0.012)

        # angular_contour_pass() handles the entire figure rendering in one step.
        p.angular_contour_pass(
            ref,
            n_flat_strokes     = 900,
            flat_stroke_size   = float(sp["stroke_size_face"]) * 3.5,
            n_contour_strokes  = 1800,
            contour_thickness  = float(sp["stroke_size_face"]),
            contour_color      = (0.12, 0.07, 0.04),
            flesh_desaturation = 0.38,
            flesh_green_shift  = 0.10,
            accent_color       = (0.70, 0.12, 0.04),
            accent_prob        = 0.06,
        )

        # No glaze, no crackle — Schiele's works on paper do not have oil varnish.
        # Very light vignette to evoke the feel of a paper sheet edge.
        p.finish(vignette=0.12, crackle=False)

    elif is_mannerist:
        # ── Mannerist pipeline (El Greco technique) ───────────────────────────
        # El Greco worked on a dark ground, building form in dense layers before
        # applying his extraordinary jewel palette in final opaque passages.
        # His figures are elongated to express spiritual rather than bodily truth;
        # his flesh is a cool silver-grey that seems to emit its own inner light.
        #
        # Pipeline:
        #   1. Deep violet-black ground — the spiritual void from which figures
        #      emerge.  Very dark, very low texture (primed Italian canvas).
        #   2. Underpainting + block_in to establish figure masses.
        #   3. build_form + place_lights for jewel-zone highlights.
        #   4. elongation_distortion_pass() — the signature El Greco technique:
        #      (a) vertical figure stretch, (b) jewel saturation boost,
        #      (c) inner-glow on pale flesh zones.
        #   5. Sfumato veil pass for edge softening (El Greco studied in Venice
        #      under Titian; soft edge haze persists in his mid-period work).
        #   6. Cool violet glaze + moderate crackle (old Spanish canvas).
        el_greco_style = _ART_CATALOG.get("el_greco")
        ground_col     = el_greco_style.ground_color if el_greco_style else (0.12, 0.10, 0.20)

        # Deep violet-black ground — very dark, almost no texture showing through
        p.tone_ground(ground_col, texture_strength=0.05)

        # Dense underpainting and block_in to build the figure before
        # the dramatic jewel passages are applied.
        p.underpainting(ref, stroke_size=int(sp["stroke_size_bg"] * 1.5), n_strokes=160)
        p.block_in(ref,     stroke_size=int(sp["stroke_size_bg"]),         n_strokes=300)
        p.build_form(ref,   stroke_size=int(sp["stroke_size_bg"] * 0.5),   n_strokes=700)
        p.place_lights(ref, stroke_size=sp["stroke_size_face"],             n_strokes=450)

        # Core El Greco technique: elongation + jewel boost + inner glow
        fig_mask = p._figure_mask   # may be None if no mask was loaded
        p.elongation_distortion_pass(
            ref,
            elongation_factor  = 0.14,       # 14%: El Greco's typical vertical stretch
            figure_mask        = fig_mask,
            jewel_boost        = 1.28,        # jewel-tone saturation boost
            inner_glow_radius  = 16.0,        # glow spread in pixels
            inner_glow_opacity = 0.20,        # subtle — it is an inner quality, not a halo
            glow_color         = (0.88, 0.86, 0.78),   # silver-grey warm
        )

        # Soft sfumato veil over edge zones — El Greco's Venetian training
        # kept gentle sfumato on face edges even in his most extreme late work.
        p.sfumato_veil_pass(
            ref,
            n_veils      = 5,
            blur_radius  = float(sp["stroke_size_face"]) * 0.70,
            warmth       = 0.12,
            veil_opacity = 0.04,
            edge_only    = True,
        )

        # Cool violet unifying glaze — his flesh shadows always have a blue-violet
        # quality from the Venice / Byzantine influence
        p.glaze((0.25, 0.18, 0.45), opacity=0.08)
        # Moderate crackle — 16th-century Spanish oil on canvas
        p.finish(vignette=0.55, crackle=True)

    elif is_surrealist:
        # ── Surrealist / Folk Retablo pipeline (Frida Kahlo technique) ─────────
        # Kahlo's paintings are rooted in the Mexican retablo/ex-voto tradition:
        # flat zones of intense saturated colour separated by heavy dark contour
        # outlines.  No chiaroscuro, no sfumato — the retablo craftsman paints
        # objects as symbolic inventory, not as volumetric forms in space.
        #
        # Pipeline:
        #   1. Warm ochre-amber ground — Kahlo worked on Masonite or metal sheet
        #      prepared with a warm ground that glows through flat colour areas.
        #   2. Standard underpainting + block_in to establish figure masses.
        #   3. build_form (minimal — retablo figures are lightly modelled at most
        #      3 tonal values).
        #   4. folk_retablo_pass() — the signature Kahlo technique:
        #      (a) posterize canvas to flat colour zones,
        #      (b) boost saturation toward volcanic-earth palette,
        #      (c) boundary_vibration: apply simultaneous warm/cool contrast at
        #          zone edges — the perceptual 'hum' of her figure-ground,
        #      (d) draw heavy dark contour outlines at all zone boundaries.
        #   5. impasto_texture_pass() — Kahlo used visible loaded-brush strokes
        #      (not spatula) in foliage and costume areas; the impasto pass gives
        #      surface relief.
        #   6. Minimal warm glaze; no crackle (panel support does not crackle).
        kahlo_style = _ART_CATALOG.get("frida_kahlo")
        ground_col  = kahlo_style.ground_color if kahlo_style else (0.72, 0.58, 0.32)

        # Warm ochre-amber ground — the colour Kahlo prepared her Masonite panels
        p.tone_ground(ground_col, texture_strength=0.08)

        # Establish form masses before the flat zone pass flattens everything
        p.underpainting(ref, stroke_size=int(sp["stroke_size_bg"] * 1.4), n_strokes=130)
        p.block_in(ref,     stroke_size=int(sp["stroke_size_bg"]),         n_strokes=250)
        p.build_form(ref,   stroke_size=int(sp["stroke_size_bg"] * 0.55),  n_strokes=500)

        # Core Kahlo/retablo technique: flat zones + saturation boost +
        # boundary vibration + dark contour lines
        p.folk_retablo_pass(
            ref,
            n_levels           = 4,
            saturation_boost   = 1.55,
            outline_thickness  = max(2.0, float(sp["stroke_size_face"]) * 0.35),
            outline_color      = (0.05, 0.03, 0.02),
            outline_opacity    = 0.88,
            boundary_vibration = True,
            vibration_width    = 1.8,
            vibration_opacity  = 0.28,
        )

        # Impasto texture pass — visible loaded-brush ridges in foliage/drapery
        p.impasto_texture_pass(
            light_angle      = 315.0,   # upper-left light (Kahlo's standard)
            ridge_height     = 0.40,
            highlight_opacity= 0.30,
            shadow_opacity   = 0.22,
        )

        # Minimal warm earth glaze — the warm ground tones the overall palette
        p.glaze((0.68, 0.48, 0.18), opacity=0.05)
        # No crackle — Masonite/metal panel; light vignette to frame the picture
        p.finish(vignette=0.25, crackle=False)

    elif is_abstract_expressionist:
        # ── Abstract Expressionist pipeline (Kandinsky technique) ────────────
        # Kandinsky worked on off-white grounds so that colour could radiate
        # from the surface without the warming or darkening influence of a
        # toned preparation.  His Bauhaus compositions have an almost enamel
        # surface quality — controlled, flat-bodied paint with geometric
        # precision.  The geometric_resonance_pass() is the signature technique:
        # floating circles, triangles, and radiating tension lines overlay the
        # composition with Kandinsky's synesthetic colour-form vocabulary.
        #
        # Pipeline:
        #   1. Off-white ground — colour radiates cleanly; minimal texture.
        #   2. Light underpainting + block_in to establish form reading beneath
        #      the abstract geometric layer.
        #   3. build_form() at medium stroke — forms are present but not
        #      heavily modelled (pure abstraction suppresses chiaroscuro).
        #   4. geometric_resonance_pass() — the Kandinsky signature: scatter
        #      floating geometric primitives coloured by synesthetic theory.
        #      Circles (blue resonance), triangles (yellow/warm), tension lines.
        #   5. No glaze — Kandinsky did not varnish; colour surface is final.
        #   6. Minimal vignette; no crackle (modern canvas).
        kandinsky_style = _ART_CATALOG.get("kandinsky")
        ground_col      = kandinsky_style.ground_color if kandinsky_style else (0.92, 0.91, 0.87)

        # Off-white ground — Kandinsky's clean radiating surface
        p.tone_ground(ground_col, texture_strength=0.03)

        # Establish compositional masses — necessary so the resonance pass has
        # meaningful colour regions to sample and respond to
        p.underpainting(ref, stroke_size=int(sp["stroke_size_bg"] * 1.3), n_strokes=120)
        p.block_in(ref,     stroke_size=int(sp["stroke_size_bg"]),         n_strokes=240)
        p.build_form(ref,   stroke_size=int(sp["stroke_size_bg"] * 0.55),  n_strokes=380)

        # Core Kandinsky technique: geometric resonance overlay
        # Kandinsky's Bauhaus phase (1922–1933) used precise, controlled geometry;
        # his lyrical phase used organic swirling forms.  The pass unifies both
        # by scattering primitives that respond to the underlying colour regions.
        p.geometric_resonance_pass(
            ref,
            n_circles      = 14,
            n_triangles    = 10,
            n_lines        = 22,
            shape_opacity  = 0.20,
            min_radius     = 0.03,
            max_radius     = 0.16,
            line_thickness = max(1.5, float(sp["stroke_size_face"]) * 0.18),
        )

        # No glaze — Kandinsky's colour is direct and unmediated by varnish.
        # Very light vignette only; no crackle.
        p.finish(vignette=0.15, crackle=False)

    elif is_venetian:
        # ── Venetian Renaissance pipeline (Titian technique) ─────────────────
        # Titian built paintings through layered warm glazes over a red-earth
        # imprimatura.  The pipeline approximates his three-stage method:
        #   1. Warm red-earth ground (imprimatura glows through thin zones)
        #   2. Standard oil underpainting + block-in to establish masses
        #   3. venetian_glaze_pass() — warm shadow glazes + mid-tone strokes
        #      + loaded impasto highlights
        #   4. subsurface_glow_pass() — warm SSS glow at figure edges and
        #      thin-skin zones (simulates Titian's red-lake glaze effect)
        #   5. Warm Venetian red-amber glaze to unify the surface
        titian_style  = _ART_CATALOG.get("titian")
        ground_col    = titian_style.ground_color if titian_style else (0.54, 0.34, 0.22)

        # Warm red-earth imprimatura — Titian's ground colour glows through
        # thin transparent colour zones throughout the painting
        p.tone_ground(ground_col, texture_strength=0.08)

        # Standard layered oil build-up before the characteristic Venetian
        # glazing stages begin
        p.underpainting(ref, stroke_size=int(sp["stroke_size_bg"] * 1.3), n_strokes=180)
        p.block_in(ref,     stroke_size=int(sp["stroke_size_bg"]),         n_strokes=360)
        p.build_form(ref,   stroke_size=int(sp["stroke_size_bg"] * 0.55),  n_strokes=700)

        # Core Venetian technique: warm shadow glazing + gestural mid-tones
        # + loaded impasto highlights
        p.venetian_glaze_pass(
            ref,
            n_glaze_layers  = 7,
            glaze_warmth    = 0.58,
            shadow_depth    = 0.74,
            impasto_strokes = 450,
            impasto_size    = float(sp["stroke_size_face"]) * 0.90,
            impasto_opacity = 0.88,
        )

        # Subsurface scattering glow — simulates Titian's red-lake translucency
        # at figure edges and thin skin areas
        p.subsurface_glow_pass(
            ref,
            glow_color    = (0.90, 0.40, 0.22),
            glow_strength = 0.16,
            blur_sigma    = max(6.0, float(sp["stroke_size_face"]) * 0.75),
            edge_falloff  = 0.60,
        )

        # Warm Venetian red-amber unifying glaze
        p.glaze((0.72, 0.38, 0.18), opacity=0.07)
        # Strong vignette (Titian often used dark edges), aged crackle appropriate
        p.finish(vignette=0.50, crackle=True)

    elif is_fauvist:
        # ── Fauvist pipeline (Henri Matisse / Les Fauves technique) ──────────
        # Matisse worked on pale-primed or unprimed canvas, letting the cream
        # ground show through flat colour zones.  The defining visual strategy
        # is the complete rejection of chiaroscuro: forms are described by HUE
        # contrast, not by light-to-shadow gradients.  Shadows receive a
        # complementary hot colour (orange shadow for blue zones, purple for
        # yellow) — never a grey or darkened version of the local hue.
        # Coloured outlines (ultramarine, vermilion, viridian) replace neutral
        # black contours.
        #
        # Pipeline:
        #   1. Pale cream ground — lets colour radiate; very low texture.
        #   2. Light underpainting only — enough to orient composition before
        #      the flat zones obliterate all modelling.
        #   3. fauvist_mosaic_pass() — the signature Matisse technique:
        #      (a) hue quantization + Fauvist palette snap,
        #      (b) luminance suppression toward mid-value,
        #      (c) complementary shadow hues,
        #      (d) coloured (ultramarine) contour outlines.
        #   4. chroma_zone_pass() — applied at reduced strength; even within
        #      Fauvism the highest lights lose colour and shadows cool slightly.
        #   5. No glaze — colour is raw, direct, final.
        #   6. Very light vignette; no crackle (modern canvas).
        matisse_style = _ART_CATALOG.get("matisse")
        ground_col    = matisse_style.ground_color if matisse_style else (0.96, 0.94, 0.80)

        # Pale cream ground — Matisse's luminous starting surface
        p.tone_ground(ground_col, texture_strength=0.03)

        # Minimal underpainting: just enough to establish compositional masses
        # before the flat colour zones take over
        p.underpainting(ref, stroke_size=int(sp["stroke_size_bg"] * 1.8), n_strokes=90)

        # Core Matisse technique: hue liberation + flat zones + coloured contours
        p.fauvist_mosaic_pass(
            ref,
            n_zones           = 9,
            saturation_boost  = 1.75,
            lum_flatten       = 0.52,
            contour_thickness = max(2.0, float(sp["stroke_size_face"]) * 0.28),
            contour_opacity   = 0.92,
            complement_shadow = True,
            shadow_threshold  = 0.36,
        )

        # Chroma zone pass at reduced strength — even Fauvism has residual
        # tonal structure: lights are cooler-white, deep darks go near-neutral
        p.chroma_zone_pass(
            light_suppress  = 0.68,   # gentler suppression — Fauvist lights stay vivid
            shadow_suppress = 0.50,
            midtone_boost   = 1.15,
            light_thresh    = 0.78,
            shadow_thresh   = 0.24,
        )

        # No glaze — Matisse's colour is direct and final, not mediated by varnish.
        # Very light vignette; no crackle (modern canvas).
        p.finish(vignette=0.12, crackle=False)

    elif is_primitivist:
        # ── Primitivist pipeline (Amedeo Modigliani technique) ───────────────
        # Modigliani painted on warm sand-ochre grounds, often unprepared canvas.
        # His figure painting is a process of geometric abstraction: he distilled
        # each sitter into a mask archetype — oval face, elongated neck, almond
        # eyes, minimal shadow.  He worked rapidly; many portraits were finished
        # in a single session.  The background is a single flat plane of cool
        # cobalt or viridian that contrasts sharply with the warm flesh tones,
        # creating the strong figure-ground boundary that defines his compositions.
        #
        # Pipeline:
        #   1. Warm sand-ochre ground — the ground colour reads through in the
        #      thinnest flesh zones and through the canvas weave.
        #   2. Standard underpainting + block_in to establish figure masses.
        #   3. build_form (minimal) — just enough to know where the shadow edge
        #      lies before the oval mask flattens everything else.
        #   4. oval_mask_pass() — the signature Modigliani technique:
        #      (a) flatten luminance modelling in face zone toward a single warm
        #          ochre mid-value (suppress chiaroscuro),
        #      (b) tint face zone toward warm ochre flesh colour,
        #      (c) draw smooth oval face contour + elongated neck column in
        #          near-black, giving the mask-like silhouette.
        #   5. warm_cool_boundary_pass() — session 17 artistic improvement:
        #      micro-push warm/cool temperature at all colour boundaries so the
        #      face-to-background edge vibrates with simultaneous contrast.
        #   6. No formal glaze — Modigliani did not varnish; paint surface is final.
        #   7. Light vignette; no crackle (modern early-20th-century canvas).
        modi_style = _ART_CATALOG.get("modigliani")
        ground_col = modi_style.ground_color if modi_style else (0.78, 0.62, 0.40)

        # Warm sand-ochre ground — Modigliani's warm foundation
        p.tone_ground(ground_col, texture_strength=0.05)

        # Standard layered build: underpainting to know the figure, block_in to
        # establish masses, minimal build_form for shadow placement
        p.underpainting(ref, stroke_size=int(sp["stroke_size_bg"] * 1.5), n_strokes=120)
        p.block_in(ref,     stroke_size=int(sp["stroke_size_bg"]),         n_strokes=240)
        p.build_form(ref,   stroke_size=int(sp["stroke_size_bg"] * 0.55),  n_strokes=350)

        # Core Modigliani technique: mask face, elongate neck, draw oval contour
        p.oval_mask_pass(
            ref,
            flesh_color       = (0.84, 0.62, 0.38),   # warm ochre flesh
            shadow_color      = (0.68, 0.44, 0.24),   # raw sienna chin shadow
            outline_color     = (0.10, 0.07, 0.06),   # near-black contour
            outline_thickness = max(2.0, float(sp["stroke_size_face"]) * 0.28),
            outline_opacity   = 0.90,
            neck_elongation   = 0.22,
            flesh_flatten     = 0.58,
            flesh_tint        = 0.32,
        )

        # Warm-cool boundary vibration — makes the face/background edge alive
        p.warm_cool_boundary_pass(
            strength    = 0.14,
            edge_thresh = 0.08,
            blur_sigma  = 1.8,
        )

        # No formal glaze — Modigliani's colour is direct and final.
        # Light vignette; no crackle (early 20th century, no extreme ageing yet).
        p.finish(vignette=0.20, crackle=False)

    elif is_early_netherlandish:
        # ── Early Netherlandish pipeline (Jan van Eyck technique) ─────────────
        # Van Eyck's revolutionary contribution was the systematic perfection of
        # oil paint as a glazing medium.  He worked on seasoned oak panels prepared
        # with multiple chalk-white gesso layers sanded to glass smoothness —
        # a near-perfect reflective surface.  Paint was built in multiple thin,
        # transparent oil glazes using walnut or linseed oil as the medium.
        # Each layer dried completely before the next, allowing light to travel
        # through the stacked transparent films and reflect from the white ground
        # beneath — creating luminosity that tempera could not achieve.
        #
        # Pipeline:
        #   1. Chalk-white gesso ground — very pale, high luminosity base.
        #      Minimal texture_strength: a gesso panel is glass-smooth.
        #   2. Underpainting + block_in + build_form to establish full figure
        #      volumes.  Van Eyck's underdrawings (visible under infrared
        #      reflectography) are extremely detailed and precise.
        #   3. place_lights() for impasto highlights — though van Eyck rarely
        #      used truly thick paint, his highlights are brighter than anything
        #      else on the panel, loaded with lead white.
        #   4. glazed_panel_pass() — the signature van Eyck technique:
        #      (a) accumulate thin warm amber-umber shadow glazes (n layers),
        #      (b) apply faint cool-neutral tint to highlights (white ground showing),
        #      (c) panel bloom diffusion at brightest highlight peaks.
        #   5. micro_detail_pass() — session 18 random artistic improvement:
        #      enhance fine-scale edge contrast to replicate van Eyck's
        #      hyper-precise rendering of individual hairs, fabric weave,
        #      and gem reflections.
        #   6. Warm amber final glaze (linseed/walnut oil top varnish layer).
        #   7. Moderate vignette; crackle=True — 15th-century oak panel ageing.
        van_eyck_style = _ART_CATALOG.get("jan_van_eyck")
        ground_col     = van_eyck_style.ground_color if van_eyck_style else (0.95, 0.93, 0.88)

        # Chalk-white gesso panel ground — glass-smooth, near-white, minimal tooth
        p.tone_ground(ground_col, texture_strength=0.018)

        # Detailed underdrawing fidelity: full underpainting + block_in + build_form.
        # Van Eyck's build-up was meticulous — forms were fully modelled before glazing.
        p.underpainting(ref, stroke_size=int(sp["stroke_size_bg"] * 1.8), n_strokes=180)
        p.block_in(ref,     stroke_size=int(sp["stroke_size_bg"]),         n_strokes=340)
        p.build_form(ref,   stroke_size=int(sp["stroke_size_bg"] * 0.5),   n_strokes=820)
        p.place_lights(ref, stroke_size=sp["stroke_size_face"],             n_strokes=550)

        # Core van Eyck technique: transparent oil glaze layers on white gesso
        p.glazed_panel_pass(
            ref,
            n_glaze_layers   = 9,
            glaze_opacity    = 0.07,
            shadow_warmth    = 0.28,
            highlight_cool   = 0.12,
            shadow_thresh    = 0.38,
            highlight_thresh = 0.72,
            panel_bloom      = 0.08,
        )

        # Session 18 random artistic improvement: Flemish micro-detail enhancement
        # Brightens fine edge light-sides, deepens shadow-sides → hyper-crisp detail
        p.micro_detail_pass(
            strength      = 0.22,
            fine_sigma    = 0.8,
            coarse_sigma  = 3.5,
            edge_thresh   = 0.06,
            light_boost   = 0.18,
            shadow_deepen = 0.14,
            figure_only   = True,
        )

        # Warm amber final varnish glaze — linseed + walnut oil yellow naturally
        # over time; even fresh van Eyck panels had a warm amber tonality
        van_eyck_glaze = van_eyck_style.glazing if van_eyck_style else (0.75, 0.58, 0.28)
        p.glaze(van_eyck_glaze, opacity=0.06)

        # Moderate vignette; crackle=True — 15th-century oak panel craquelure
        p.finish(vignette=0.35, crackle=True)

    elif is_synthetist:
        # ── Synthetist / Cloisonnist pipeline (Paul Gauguin technique) ───────
        # Gauguin's Cloisonnism reduces the world to flat zones of saturated,
        # anti-naturalistic colour enclosed in thick dark contour lines — named
        # after cloisonné enamel jewellery where metallic 'cloisons' separate
        # vivid glass fields.  No chiaroscuro, no sfumato — bold zones and the
        # leading line are the entire pictorial vocabulary.
        #
        # Pipeline:
        #   1. Warm cream-ochre ground (Gauguin worked on raw or lightly primed
        #      canvas; the warm ground glows through thin colour areas).
        #   2. Light underpainting to establish figure masses — very brief;
        #      Cloisonnism suppresses modelling so this pass stays thin.
        #   3. cloisonne_pass() — quantize reference to N flat colour zones,
        #      boost saturation toward Tahitian register, fill each zone with
        #      flat loaded-brush strokes, draw thick Prussian-dark contour lines
        #      at all zone boundaries.
        #   4. Minimal finish — very light vignette; no glaze (raw colour is the
        #      point), no aged crackle (Gauguin's canvas is modern).
        gauguin_style = _ART_CATALOG.get("gauguin")
        ground_col    = gauguin_style.ground_color if gauguin_style else (0.88, 0.80, 0.60)

        # Warm cream-ochre ground — Gauguin's ground colour glows through the
        # thin flat colour zones, unifying the picture with warmth
        p.tone_ground(ground_col, texture_strength=0.06)

        # Very brief underpainting: just enough to know where the figure is
        # before the flat colour zones take over completely
        p.underpainting(ref, stroke_size=int(sp["stroke_size_bg"] * 1.6), n_strokes=100)

        # Core Gauguin technique: flat colour zones + cloisonné leading
        p.cloisonne_pass(
            ref,
            n_colors          = 8,
            contour_thickness = float(sp["stroke_size_face"]) * 0.55,
            contour_color     = (0.06, 0.04, 0.10),   # near-black Prussian blue
            saturation_boost  = 1.40,
            hue_exotic_shift  = 0.03,
            zone_opacity      = 0.92,
            contour_opacity   = 0.94,
            n_zone_strokes    = int(W * H / 520),      # scale with canvas size
        )

        # No glaze (raw colour is the work), no crackle.
        # Very light vignette to frame the canvas edge — Gauguin's pictures
        # are often edge-to-edge with colour, so keep this gentle.
        p.finish(vignette=0.20, crackle=False)

    elif is_pointillist:
        # ── Pointillist / divisionist pipeline (Seurat technique) ────────────
        # Pale canvas ground — dots are sparse enough that the ground shows
        # through in highlight areas, creating the luminous haze of La Grande Jatte.
        p.tone_ground((0.88, 0.84, 0.70), texture_strength=0.04)

        # Light value underpainting to establish composition before dots are placed.
        p.underpainting(ref, stroke_size=int(sp["stroke_size_bg"] * 2.0), n_strokes=80)

        # Primary divisionist pass — fine dots with chromatic complement pairs.
        p.pointillist_pass(
            ref,
            n_dots          = 8000,
            dot_size        = float(sp["stroke_size_face"]),
            chromatic_split = True,
            split_ratio     = 0.32,
            split_radius    = 2.2,
        )
        # Second pass at slightly larger dot size adds tonal variety —
        # Seurat varied dot size in different zones.
        p.pointillist_pass(
            ref,
            n_dots          = 4000,
            dot_size        = float(sp["stroke_size_bg"]),
            chromatic_split = True,
            split_ratio     = 0.28,
            split_radius    = 2.0,
        )

        # Impasto highlight dots last — just as in conventional oil painting.
        p.place_lights(ref, stroke_size=sp["stroke_size_face"], n_strokes=300)
        # No amber glaze — Seurat worked on fresh bright canvas.
        # Gentle vignette only; no aged crackle.
        p.finish(vignette=0.30, crackle=False)

    else:
        # ── Standard oil painting pipeline ───────────────────────────────────
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

            # anatomy_flow_field() encodes the major anatomical planes of the face:
            # horizontal forehead strokes, orbital curves around the eye sockets,
            # vertical nasal planes, diagonal cheekbone strokes, etc.  This gives
            # brushwork that reads more naturally than a generic spherical_flow()
            # because it mirrors how trained portrait painters actually work.
            # spherical_flow is passed as gradient_fallback so strokes outside
            # the face ellipse still follow the surface curvature.
            sphere_flow = spherical_flow(W, H, cx, cy, rx, ry)
            face_flow   = anatomy_flow_field(W, H, cx, cy, rx, ry,
                                             gradient_fallback=sphere_flow)

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

        # ── Sfumato veil pass for Leonardo-style Renaissance rendering ────────
        # Activated when edge_softness is high (≥0.80) — the sfumato_veil_pass
        # replaces crude edge_softness approximation with physically motivated
        # multi-layer warm glaze accumulation, as Leonardo applied ~30 layers
        # of imperceptibly thin glaze to the mouth and eye corners of the Mona Lisa.
        if is_renaissance_soft:
            p.sfumato_veil_pass(
                ref,
                n_veils      = 9,
                blur_radius  = max(6.0, float(sp["stroke_size_face"]) * 0.8),
                warmth       = 0.30,
                veil_opacity = 0.06,
                edge_only    = True,
            )

        # ── Luminous glow pass for Romantic / Turner atmospheric light ────────
        # Turner dissolved all solid form into radiant light — his late works are
        # nearly abstract vortices of warm yellow at the light centre fading to
        # cool blue-violet at the periphery.  luminous_glow_pass() locates the
        # brightest point in the reference and overlays concentric warm-to-cool
        # radial glaze rings — the defining quality of his work that cannot be
        # achieved through ordinary stroke painting alone.
        if is_romantic:
            p.luminous_glow_pass(
                ref,
                n_rings      = 11,
                max_radius   = 0.58,
                core_color   = (0.98, 0.94, 0.72),   # incandescent sun core
                haze_color   = (0.48, 0.60, 0.80),   # cool atmospheric periphery
                core_opacity = 0.24,
                haze_opacity = 0.10,
            )

        p.glaze((0.60, 0.42, 0.14), opacity=0.07)
        p.finish(vignette=0.50, crackle=True)

    p.save(output_path)

    return output_path
