"""
face_builder.py

Generates Blender Python code (as a string) that, when executed inside
Blender's headless Python interpreter, creates a mesh-based human face.

Public interface
----------------
    build_face_code(lm: dict, pose_detail) -> str

Parameters
----------
lm          : landmarks dict returned by compute_landmarks()
pose_detail : PoseDetail with attributes head_turn, head_nod, head_tilt (radians)

The generated code assumes `skin_mat` is already defined in the Blender scope.
All internal variable names are prefixed with `_fb_` to avoid collisions.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_face_code(lm: dict, pose_detail) -> str:
    """Return a self-contained Blender Python script string that builds the
    face mesh when exec()'d inside Blender's interpreter.

    Parameters
    ----------
    lm          : dict from compute_landmarks()
    pose_detail : object with head_turn, head_nod, head_tilt (float, radians)
    """
    # Extract scalar values from landmarks so they embed cleanly as literals.
    head_top  = lm["head_top"]   # (x, y, z) world position
    chin_pt   = lm["chin"]       # (x, y, z) world position
    head_ctr  = lm["head_ctr"]   # (x, y, z) world centre

    # Sphere radius derived from vertical span.
    import math
    r_val = max(0.118, (head_top[2] - chin_pt[2]) / 2.0)

    # Pose angles — PoseDetail stores degrees; rotation_euler needs radians.
    import math as _math
    turn_val  = _math.radians(float(getattr(pose_detail, "head_turn", 0.0)))
    nod_val   = _math.radians(float(getattr(pose_detail, "head_nod",  0.0)))
    tilt_val  = _math.radians(float(getattr(pose_detail, "head_tilt", 0.0)))

    # Position.
    cx, cy, cz = float(head_ctr[0]), float(head_ctr[1]), float(head_ctr[2])

    code = _render_template(r_val, cx, cy, cz, turn_val, nod_val, tilt_val)
    return code


# ---------------------------------------------------------------------------
# Internal: template renderer
# ---------------------------------------------------------------------------

def _render_template(r: float, cx: float, cy: float, cz: float,
                     turn: float, nod: float, tilt: float) -> str:
    """Produce the full Blender script as a string."""

    # We embed all floats as literals so the generated script is standalone.
    return f"""\
# ---- face_builder generated block ----------------------------------------
import bpy as _fb_bpy
import bmesh as _fb_bmesh
import math as _m
from mathutils import Vector as _fb_V, Matrix as _fb_M

# --- parameters (baked at generation time) ---------------------------------
_fb_r    = {r!r}
_fb_cx   = {cx!r}
_fb_cy   = {cy!r}
_fb_cz   = {cz!r}
_fb_turn = {turn!r}   # Z rotation (head turn)
_fb_tilt = {tilt!r}   # Y rotation (head tilt)
_fb_nod  = {nod!r}    # X rotation (head nod)

_fb_SEGS  = 64   # longitude segments (was 28 — too coarse for nose/eye Gaussians)
_fb_RINGS = 48   # latitude rings     (was 20 — σ_nose≈0.13rad needs ≥5 verts per σ)
_fb_NECK_R = 0.040  # neck radius (metres) for taper

# ---------------------------------------------------------------------------
# 1. Build UV-sphere vertices and faces via pure Python maths
#    Layout: index 0 = north pole, indices 1..(SEGS*RINGS) = ring vertices,
#            index SEGS*RINGS+1 = south pole
# ---------------------------------------------------------------------------

def _fb_build_sphere_data(r, segs, rings):
    \"\"\"Return (verts, faces) as lists of tuples ready for from_pydata.\"\"\"
    verts = []
    faces = []

    # North pole
    verts.append((0.0, 0.0, r))

    # Ring vertices: ring 0 = just below north pole, ring rings-1 = just above south pole
    for ring_i in range(rings):
        # polar angle phi: from pi/(rings+1) to pi*rings/(rings+1)
        phi = _m.pi * (ring_i + 1) / (rings + 1)
        sin_phi = _m.sin(phi)
        cos_phi = _m.cos(phi)
        for seg_i in range(segs):
            theta = 2.0 * _m.pi * seg_i / segs
            x = r * sin_phi * _m.cos(theta)
            y = r * sin_phi * _m.sin(theta)
            z = r * cos_phi
            verts.append((x, y, z))

    # South pole
    verts.append((0.0, 0.0, -r))

    south_idx = len(verts) - 1

    # --- Faces ---
    # North-pole cap: triangles connecting pole to first ring
    for s in range(segs):
        a = 1 + s
        b = 1 + (s + 1) % segs
        faces.append((0, a, b))

    # Quad bands between successive rings
    for ring_i in range(rings - 1):
        row_a = 1 + ring_i * segs
        row_b = 1 + (ring_i + 1) * segs
        for s in range(segs):
            a = row_a + s
            b = row_a + (s + 1) % segs
            c = row_b + (s + 1) % segs
            d = row_b + s
            faces.append((a, b, c, d))

    # South-pole cap: triangles connecting last ring to pole
    last_row = 1 + (rings - 1) * segs
    for s in range(segs):
        a = last_row + s
        b = last_row + (s + 1) % segs
        faces.append((b, a, south_idx))

    return verts, faces

_fb_raw_verts, _fb_raw_faces = _fb_build_sphere_data(_fb_r, _fb_SEGS, _fb_RINGS)

# ---------------------------------------------------------------------------
# 2. Gaussian helper (inline for generated scope)
# ---------------------------------------------------------------------------

def _fb_gauss(x, mu, sigma):
    return _m.exp(-0.5 * ((x - mu) / sigma) ** 2)

# ---------------------------------------------------------------------------
# 3. Displace vertices to shape facial anatomy
# ---------------------------------------------------------------------------

def _fb_displace(verts, r):
    \"\"\"Return new list of displaced (x, y, z) tuples.\"\"\"
    result = []
    neck_r = _fb_NECK_R

    for (vx, vy, vz) in verts:
        # Normalised coordinates relative to sphere centre.
        # The sphere is centred at origin in local space; -Y faces camera.
        nx = vx / r
        ny = vy / r
        nz = vz / r

        # face_dot: 1 = dead centre facing -Y camera, -1 = back of head.
        # Because -Y is towards the camera, face_dot = -ny.
        face_dot  =  -ny
        lateral_t =   nx
        height_t  =   nz

        # Overall front-face weight — features only on the front hemisphere.
        if face_dot > 0.20:
            face_weight = (face_dot - 0.20) / 0.80
        else:
            face_weight = 0.0

        delta = 0.0

        if face_weight > 0.0:
            g = _fb_gauss  # shorthand

            # Brow ridge — protrudes ~14mm; wider Gaussian so it reads clearly
            lat_clamp = lateral_t / 0.80
            delta += face_weight * 0.12 * r * g(height_t, 0.38, 0.10) * g(face_dot, 0.75, 0.18) * max(0.0, 1.0 - lat_clamp * lat_clamp)

            # Eye sockets — deep indent ~14mm; punched in hard so shadow forms clearly
            delta -= face_weight * 0.12 * r * g(lateral_t, -0.36, 0.13) * g(height_t, 0.22, 0.09) * g(face_dot, 0.75, 0.15)
            delta -= face_weight * 0.12 * r * g(lateral_t,  0.36, 0.13) * g(height_t, 0.22, 0.09) * g(face_dot, 0.75, 0.15)

            # Cheekbones — gentle lateral protrusion ~8mm
            delta += face_weight * 0.07 * r * g(lateral_t, -0.56, 0.14) * g(height_t, 0.04, 0.11) * g(face_dot, 0.68, 0.18)
            delta += face_weight * 0.07 * r * g(lateral_t,  0.56, 0.14) * g(height_t, 0.04, 0.11) * g(face_dot, 0.68, 0.18)

            # Nose bridge — narrow ridge ~11mm
            delta += face_weight * 0.10 * r * g(lateral_t, 0.0, 0.08) * g(height_t, 0.12, 0.10) * g(face_dot, 0.82, 0.12)

            # Nose tip — prominent: protrudes ~21mm (anatomically correct)
            # σ_lateral=0.13 spans ~5 verts at 64 segs; clearly representable
            delta += face_weight * 0.28 * r * g(lateral_t, 0.0, 0.13) * g(height_t, -0.12, 0.09) * g(face_dot, 0.90, 0.10)

            # Nostrils (concave) — ~5mm indent each side
            delta -= face_weight * 0.04 * r * g(lateral_t, -0.14, 0.07) * g(height_t, -0.20, 0.06) * g(face_dot, 0.82, 0.10)
            delta -= face_weight * 0.04 * r * g(lateral_t,  0.14, 0.07) * g(height_t, -0.20, 0.06) * g(face_dot, 0.82, 0.10)

            # Upper lip boss — ~10mm protrusion with cupid's bow width
            delta += face_weight * 0.09 * r * g(lateral_t, 0.0, 0.20) * g(height_t, -0.34, 0.06) * g(face_dot, 0.82, 0.12)

            # Lower lip boss — slightly fuller, ~13mm protrusion
            delta += face_weight * 0.11 * r * g(lateral_t, 0.0, 0.22) * g(height_t, -0.46, 0.07) * g(face_dot, 0.80, 0.12)

            # Philtrum groove — narrow concave channel ~4mm
            delta -= face_weight * 0.04 * r * g(lateral_t, 0.0, 0.06) * g(height_t, -0.28, 0.06) * g(face_dot, 0.83, 0.10)

            # Chin knob — gentle protrusion ~8mm
            delta += face_weight * 0.07 * r * g(lateral_t, 0.0, 0.18) * g(height_t, -0.60, 0.09) * g(face_dot, 0.72, 0.16)

        # Displace radially (along the unit normal = the normalised position
        # vector on a sphere).
        ux, uy, uz = nx, ny, nz  # unit radial direction
        new_x = vx + ux * delta
        new_y = vy + uy * delta
        new_z = vz + uz * delta

        # -----------------------------------------------------------------
        # Neck taper: squeeze XY of southern vertices toward neck_r.
        # nz is the *original* normalised Z; use it for the taper test.
        # -----------------------------------------------------------------
        nz_norm = nz  # normalised z before any displacement
        if nz_norm < -0.80:
            taper_t = min(1.0, (-nz_norm - 0.80) / 0.20)
            xy_r = _m.sqrt(new_x * new_x + new_y * new_y)
            if xy_r > neck_r and xy_r > 1e-9:
                scale = 1.0 - taper_t * (1.0 - neck_r / xy_r)
                new_x *= scale
                new_y *= scale

        result.append((new_x, new_y, new_z))

    return result

_fb_disp_verts = _fb_displace(_fb_raw_verts, _fb_r)

# ---------------------------------------------------------------------------
# 4. Create Blender mesh from displaced vertices
# ---------------------------------------------------------------------------

_fb_mesh = _fb_bpy.data.meshes.new("FaceMesh")
_fb_mesh.from_pydata(_fb_disp_verts, [], _fb_raw_faces)
_fb_mesh.update()

# Transfer into a bmesh to ensure clean normals, then write back.
_fb_bm = _fb_bmesh.new()
_fb_bm.from_mesh(_fb_mesh)
_fb_bmesh.ops.recalc_face_normals(_fb_bm, faces=_fb_bm.faces)
_fb_bm.to_mesh(_fb_mesh)
_fb_bm.free()
del _fb_bm

# ---------------------------------------------------------------------------
# 5. Create object, assign material, set smooth shading
# ---------------------------------------------------------------------------

_fb_obj = _fb_bpy.data.objects.new("Face", _fb_mesh)
_fb_bpy.context.collection.objects.link(_fb_obj)

# Assign the pre-existing skin material (defined in outer scope).
if _fb_mesh.materials:
    _fb_mesh.materials[0] = skin_mat  # noqa: F821  (defined in caller scope)
else:
    _fb_mesh.materials.append(skin_mat)  # noqa: F821

# Smooth shading on all polygons.
for _fb_poly in _fb_mesh.polygons:
    _fb_poly.use_smooth = True

# ---------------------------------------------------------------------------
# 6. SubSurf modifier (Catmull–Clark, levels=2)
# ---------------------------------------------------------------------------

# No SubSurf: the displacement is pre-baked into vertex positions.
# Smooth shading on the dense UV sphere (28×20 rings) gives a good result
# without a subdivision modifier that would erase the sculpted features.

# ---------------------------------------------------------------------------
# 7. Position and rotation
#    Rotation order: Z (turn) → Y (tilt) → X (nod) applied as Euler ZYX.
# ---------------------------------------------------------------------------

_fb_obj.location = (_fb_cx, _fb_cy, _fb_cz)
_fb_obj.rotation_mode  = "ZYX"
_fb_obj.rotation_euler = (_fb_nod, _fb_tilt, _fb_turn)

# Select and make active for any downstream operations.
_fb_bpy.context.view_layer.objects.active = _fb_obj
_fb_obj.select_set(True)

# Tidy up module-level names that callers should not reuse.
del _fb_disp_verts, _fb_raw_verts, _fb_raw_faces
# ---- end face_builder block -----------------------------------------------
"""
