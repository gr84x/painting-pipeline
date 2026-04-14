"""
head_builder.py — Parametric human/cartoon head mesh for Blender.

Public interface:
    build_head_code(lm, pose_detail, morphology=None) -> str

Replaces face_builder.py. Improvements:
  - CartoonMorphology: scale cranium, eyes, nose, lips independently
  - Head shape deformations: cranium expansion, jaw taper, face flatten
  - Sharper feature boundaries using plateau/sigmoid shapes
  - Subdivision Surface level=1 for smooth normals (needed by normal-map pass)
  - Variable prefix _hb_ to coexist with old face_builder during transition
"""
from __future__ import annotations
import math
from cartoon_morphology import CartoonMorphology


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_head_code(lm: dict, pose_detail, morphology: CartoonMorphology = None) -> str:
    """Return a self-contained Blender Python script string that builds the
    head mesh when exec()'d inside Blender's interpreter.

    Parameters
    ----------
    lm          : dict from compute_landmarks()
    pose_detail : object with head_turn, head_nod, head_tilt (float, radians)
    morphology  : CartoonMorphology instance, or None for realistic defaults
    """
    m = morphology or CartoonMorphology()

    # Extract scalar values from landmarks so they embed cleanly as literals.
    head_top = lm["head_top"]   # (x, y, z) world position
    chin_pt  = lm["chin"]       # (x, y, z) world position
    head_ctr = lm["head_ctr"]   # (x, y, z) world centre

    # Sphere radius derived from vertical span.
    r_val = max(0.118, (head_top[2] - chin_pt[2]) / 2.0)

    # Pose angles — PoseDetail stores degrees; rotation_euler needs radians.
    turn_val = math.radians(float(getattr(pose_detail, "head_turn", 0.0)))
    nod_val  = math.radians(float(getattr(pose_detail, "head_nod",  0.0)))
    tilt_val = math.radians(float(getattr(pose_detail, "head_tilt", 0.0)))

    # Position.
    cx = float(head_ctr[0])
    cy = float(head_ctr[1])
    cz = float(head_ctr[2])

    # Pre-compute all morphology-scaled feature parameters as Python literals.
    # All these are embedded into the generated script as plain floats — the
    # Blender interpreter never needs to know about CartoonMorphology.

    # Brow ridge
    brow_amp = 0.12 * m.brow_ridge

    # Eye sockets: lateral centre shifts outward with eye_scale, sigma widens
    eye_amp       = 0.12 * m.eye_depth
    eye_lat_base  = 0.36                              # base lateral offset
    eye_lat_delta = 0.04 * (m.eye_scale - 1.0)       # shift outward when >1
    eye_lat_l     = -(eye_lat_base + eye_lat_delta)   # left socket centre
    eye_lat_r     =  (eye_lat_base + eye_lat_delta)   # right socket centre
    eye_sigma_lat = 0.13 * math.sqrt(max(0.5, m.eye_scale))   # wider sigma
    eye_sigma_ht  = 0.09
    eye_sigma_fd  = 0.15

    # Cheekbones (unaffected by morphology — structural landmark)
    cheek_amp = 0.07

    # Nose bridge
    nose_bridge_amp = 0.10 * m.nose_size

    # Nose tip
    nose_tip_amp = 0.28 * m.nose_size * m.nose_tip

    # Nostrils
    nostril_amp = 0.04 * m.nose_size

    # Upper lip
    upper_lip_amp = 0.09 * m.lip_fullness

    # Lower lip
    lower_lip_amp = 0.11 * m.lip_fullness

    # Lip lateral sigma scaled by mouth_width
    lip_sigma_lat = 0.20 * m.mouth_width
    lower_lip_sigma_lat = 0.22 * m.mouth_width

    # Philtrum (subtle, slight mouth_width link)
    philtrum_amp = 0.04 * m.lip_fullness

    # Chin
    chin_amp = 0.07

    # Head shape deformation parameters (embedded as literals)
    cranium_ratio = float(m.cranium_ratio)
    face_flat     = float(m.face_flat)
    jaw_taper     = float(m.jaw_taper)

    params = dict(
        brow_amp=brow_amp,
        eye_amp=eye_amp,
        eye_lat_l=eye_lat_l,
        eye_lat_r=eye_lat_r,
        eye_sigma_lat=eye_sigma_lat,
        eye_sigma_ht=eye_sigma_ht,
        eye_sigma_fd=eye_sigma_fd,
        cheek_amp=cheek_amp,
        nose_bridge_amp=nose_bridge_amp,
        nose_tip_amp=nose_tip_amp,
        nostril_amp=nostril_amp,
        upper_lip_amp=upper_lip_amp,
        lower_lip_amp=lower_lip_amp,
        lip_sigma_lat=lip_sigma_lat,
        lower_lip_sigma_lat=lower_lip_sigma_lat,
        philtrum_amp=philtrum_amp,
        chin_amp=chin_amp,
        cranium_ratio=cranium_ratio,
        face_flat=face_flat,
        jaw_taper=jaw_taper,
    )

    return _render_head_template(r_val, cx, cy, cz, turn_val, nod_val, tilt_val, params)


# ---------------------------------------------------------------------------
# Internal: template renderer
# ---------------------------------------------------------------------------

def _render_head_template(r: float, cx: float, cy: float, cz: float,
                          turn: float, nod: float, tilt: float,
                          params: dict) -> str:
    """Produce the full Blender script as a string.

    All feature parameters are pre-computed literals embedded directly into
    the script — no CartoonMorphology import needed in Blender's interpreter.
    """
    # Unpack params for f-string embedding (repr for exact float literals).
    brow_amp             = repr(params["brow_amp"])
    eye_amp              = repr(params["eye_amp"])
    eye_lat_l            = repr(params["eye_lat_l"])
    eye_lat_r            = repr(params["eye_lat_r"])
    eye_sigma_lat        = repr(params["eye_sigma_lat"])
    eye_sigma_ht         = repr(params["eye_sigma_ht"])
    eye_sigma_fd         = repr(params["eye_sigma_fd"])
    cheek_amp            = repr(params["cheek_amp"])
    nose_bridge_amp      = repr(params["nose_bridge_amp"])
    nose_tip_amp         = repr(params["nose_tip_amp"])
    nostril_amp          = repr(params["nostril_amp"])
    upper_lip_amp        = repr(params["upper_lip_amp"])
    lower_lip_amp        = repr(params["lower_lip_amp"])
    lip_sigma_lat        = repr(params["lip_sigma_lat"])
    lower_lip_sigma_lat  = repr(params["lower_lip_sigma_lat"])
    philtrum_amp         = repr(params["philtrum_amp"])
    chin_amp             = repr(params["chin_amp"])
    cranium_ratio        = repr(params["cranium_ratio"])
    face_flat            = repr(params["face_flat"])
    jaw_taper            = repr(params["jaw_taper"])

    return f"""\
# ---- head_builder generated block ----------------------------------------
import bpy as _hb_bpy
import bmesh as _hb_bmesh
import math as _m
from mathutils import Vector as _hb_V, Matrix as _hb_M

# --- parameters (baked at generation time) ---------------------------------
_hb_r    = {r!r}
_hb_cx   = {cx!r}
_hb_cy   = {cy!r}
_hb_cz   = {cz!r}
_hb_turn = {turn!r}   # Z rotation (head turn)
_hb_tilt = {tilt!r}   # Y rotation (head tilt)
_hb_nod  = {nod!r}    # X rotation (head nod)

_hb_SEGS  = 64   # longitude segments
_hb_RINGS = 48   # latitude rings
_hb_NECK_R = 0.040  # neck radius (metres) for taper

# --- morphology-scaled feature amplitudes (pre-computed in Python) ---------
# These are exact literals embedded at script-generation time; no
# CartoonMorphology class is needed inside the Blender interpreter.
_hb_brow_amp            = {brow_amp}
_hb_eye_amp             = {eye_amp}
_hb_eye_lat_l           = {eye_lat_l}
_hb_eye_lat_r           = {eye_lat_r}
_hb_eye_sigma_lat       = {eye_sigma_lat}
_hb_eye_sigma_ht        = {eye_sigma_ht}
_hb_eye_sigma_fd        = {eye_sigma_fd}
_hb_cheek_amp           = {cheek_amp}
_hb_nose_bridge_amp     = {nose_bridge_amp}
_hb_nose_tip_amp        = {nose_tip_amp}
_hb_nostril_amp         = {nostril_amp}
_hb_upper_lip_amp       = {upper_lip_amp}
_hb_lower_lip_amp       = {lower_lip_amp}
_hb_lip_sigma_lat       = {lip_sigma_lat}
_hb_lower_lip_sigma_lat = {lower_lip_sigma_lat}
_hb_philtrum_amp        = {philtrum_amp}
_hb_chin_amp            = {chin_amp}
# head shape deformation parameters
_hb_cranium_ratio = {cranium_ratio}   # cranium expansion (>1 = anime big-head)
_hb_face_flat     = {face_flat}       # 0=realistic, 1=flat anime face
_hb_jaw_taper     = {jaw_taper}       # 0=normal, 1=very pointed chin

# ---------------------------------------------------------------------------
# 1. Build UV-sphere vertices and faces via pure Python maths
#    Layout: index 0 = north pole, indices 1..(SEGS*RINGS) = ring vertices,
#            index SEGS*RINGS+1 = south pole
# ---------------------------------------------------------------------------

def _hb_build_sphere_data(r, segs, rings):
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

_hb_raw_verts, _hb_raw_faces = _hb_build_sphere_data(_hb_r, _hb_SEGS, _hb_RINGS)

# ---------------------------------------------------------------------------
# 2. Gaussian helper (inline for generated scope)
# ---------------------------------------------------------------------------

def _hb_gauss(x, mu, sigma):
    return _m.exp(-0.5 * ((x - mu) / sigma) ** 2)

# ---------------------------------------------------------------------------
# 3. Displace vertices to shape head anatomy + cartoon deformations
# ---------------------------------------------------------------------------

def _hb_displace(verts, r):
    \"\"\"Return new list of displaced (x, y, z) tuples.

    Three stages per vertex:
      A. Gaussian facial features (amplitudes pre-scaled by morphology)
      B. Radial displacement applied
      C. Head shape deformations: cranium expansion, jaw taper, face flatten
      D. Neck taper (southern hemisphere)
    \"\"\"
    result = []
    neck_r = _hb_NECK_R

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
            g = _hb_gauss  # shorthand

            # Brow ridge — protrudes; wider Gaussian so it reads clearly.
            # Amplitude pre-scaled by brow_ridge morphology parameter.
            lat_clamp = lateral_t / 0.80
            delta += face_weight * _hb_brow_amp * r * g(height_t, 0.38, 0.10) * g(face_dot, 0.75, 0.18) * max(0.0, 1.0 - lat_clamp * lat_clamp)

            # Eye sockets — deep indent; lateral position and sigma scaled by eye_scale.
            # Amplitude pre-scaled by eye_depth morphology parameter.
            delta -= face_weight * _hb_eye_amp * r * g(lateral_t, _hb_eye_lat_l, _hb_eye_sigma_lat) * g(height_t, 0.22, _hb_eye_sigma_ht) * g(face_dot, 0.75, _hb_eye_sigma_fd)
            delta -= face_weight * _hb_eye_amp * r * g(lateral_t, _hb_eye_lat_r, _hb_eye_sigma_lat) * g(height_t, 0.22, _hb_eye_sigma_ht) * g(face_dot, 0.75, _hb_eye_sigma_fd)

            # Cheekbones — gentle lateral protrusion (unaffected by morphology).
            delta += face_weight * _hb_cheek_amp * r * g(lateral_t, -0.56, 0.14) * g(height_t, 0.04, 0.11) * g(face_dot, 0.68, 0.18)
            delta += face_weight * _hb_cheek_amp * r * g(lateral_t,  0.56, 0.14) * g(height_t, 0.04, 0.11) * g(face_dot, 0.68, 0.18)

            # Nose bridge — narrow ridge; amplitude scaled by nose_size.
            delta += face_weight * _hb_nose_bridge_amp * r * g(lateral_t, 0.0, 0.08) * g(height_t, 0.12, 0.10) * g(face_dot, 0.82, 0.12)

            # Nose tip — prominent protrusion; amplitude scaled by nose_size * nose_tip.
            delta += face_weight * _hb_nose_tip_amp * r * g(lateral_t, 0.0, 0.13) * g(height_t, -0.12, 0.09) * g(face_dot, 0.90, 0.10)

            # Nostrils (concave) — scaled by nose_size.
            delta -= face_weight * _hb_nostril_amp * r * g(lateral_t, -0.14, 0.07) * g(height_t, -0.20, 0.06) * g(face_dot, 0.82, 0.10)
            delta -= face_weight * _hb_nostril_amp * r * g(lateral_t,  0.14, 0.07) * g(height_t, -0.20, 0.06) * g(face_dot, 0.82, 0.10)

            # Upper lip boss — amplitude scaled by lip_fullness; sigma scaled by mouth_width.
            delta += face_weight * _hb_upper_lip_amp * r * g(lateral_t, 0.0, _hb_lip_sigma_lat) * g(height_t, -0.34, 0.06) * g(face_dot, 0.82, 0.12)

            # Lower lip boss — slightly fuller; scaled similarly.
            delta += face_weight * _hb_lower_lip_amp * r * g(lateral_t, 0.0, _hb_lower_lip_sigma_lat) * g(height_t, -0.46, 0.07) * g(face_dot, 0.80, 0.12)

            # Philtrum groove — narrow concave channel; slight lip_fullness link.
            delta -= face_weight * _hb_philtrum_amp * r * g(lateral_t, 0.0, 0.06) * g(height_t, -0.28, 0.06) * g(face_dot, 0.83, 0.10)

            # Chin knob — gentle protrusion (unaffected by morphology).
            delta += face_weight * _hb_chin_amp * r * g(lateral_t, 0.0, 0.18) * g(height_t, -0.60, 0.09) * g(face_dot, 0.72, 0.16)

        # Displace radially (along the unit normal = the normalised position
        # vector on a sphere).
        ux, uy, uz = nx, ny, nz  # unit radial direction
        new_x = vx + ux * delta
        new_y = vy + uy * delta
        new_z = vz + uz * delta

        # -----------------------------------------------------------------
        # Head shape deformation block — runs AFTER Gaussian features.
        # Uses original normalised coordinates (nx, ny, nz) for thresholds
        # to avoid feedback with the already-displaced position.
        # -----------------------------------------------------------------
        nz_orig = nz   # original normalised Z (before displacement)

        # A. Cranium expansion: enlarge skull above the brow line.
        #    nz > 0.35 corresponds roughly to the supraorbital ridge.
        #    Scales the displaced vertex outward from the local origin.
        if nz_orig > 0.35 and _hb_cranium_ratio != 1.0:
            # Blend from 0 at threshold to full ratio at top of head.
            t = min(1.0, (nz_orig - 0.35) / 0.65)
            expand = 1.0 + (_hb_cranium_ratio - 1.0) * t
            new_x *= expand
            new_y *= expand
            new_z *= expand

        # B. Jaw tapering: squeeze XY of lower face toward the vertical axis.
        #    nz < -0.55 is below the cheekbone/jaw region.
        if nz_orig < -0.55 and _hb_jaw_taper != 0.0:
            t = min(1.0, (-nz_orig - 0.55) / 0.45)
            squeeze = 1.0 - _hb_jaw_taper * t * 0.6
            new_x *= squeeze
            new_y *= squeeze

        # C. Face flattening: reduce the Y extent of the front face.
        #    face_dot > 0 means this vertex faces the camera.
        #    Pushes front-face vertices toward Y=0 (flattens nose/lip protrusion).
        if face_dot > 0.0 and _hb_face_flat != 0.0:
            flatten = _hb_face_flat * max(0.0, face_dot) * 0.5
            new_y *= (1.0 - flatten)

        # -----------------------------------------------------------------
        # Neck taper: squeeze XY of southern vertices toward neck_r.
        # nz_orig is used for the taper test (consistent with face_builder).
        # -----------------------------------------------------------------
        if nz_orig < -0.80:
            taper_t = min(1.0, (-nz_orig - 0.80) / 0.20)
            xy_r = _m.sqrt(new_x * new_x + new_y * new_y)
            if xy_r > neck_r and xy_r > 1e-9:
                scale = 1.0 - taper_t * (1.0 - neck_r / xy_r)
                new_x *= scale
                new_y *= scale

        result.append((new_x, new_y, new_z))

    return result

_hb_disp_verts = _hb_displace(_hb_raw_verts, _hb_r)

# ---------------------------------------------------------------------------
# 4. Create Blender mesh from displaced vertices
# ---------------------------------------------------------------------------

_hb_mesh = _hb_bpy.data.meshes.new("FaceMesh")
_hb_mesh.from_pydata(_hb_disp_verts, [], _hb_raw_faces)
_hb_mesh.update()

# Transfer into a bmesh to ensure clean normals, then write back.
_hb_bm = _hb_bmesh.new()
_hb_bm.from_mesh(_hb_mesh)
_hb_bmesh.ops.recalc_face_normals(_hb_bm, faces=_hb_bm.faces)
_hb_bm.to_mesh(_hb_mesh)
_hb_bm.free()
del _hb_bm

# ---------------------------------------------------------------------------
# 5. Create object, assign material, set smooth shading
# ---------------------------------------------------------------------------

_hb_obj = _hb_bpy.data.objects.new("Face", _hb_mesh)
_hb_bpy.context.collection.objects.link(_hb_obj)

# Assign the pre-existing skin material (defined in outer scope).
if _hb_mesh.materials:
    _hb_mesh.materials[0] = skin_mat  # noqa: F821  (defined in caller scope)
else:
    _hb_mesh.materials.append(skin_mat)  # noqa: F821

# Smooth shading on all polygons.
for _hb_poly in _hb_mesh.polygons:
    _hb_poly.use_smooth = True

# ---------------------------------------------------------------------------
# 6. Subdivision Surface modifier (Catmull-Clark, level=1)
#    Level 1 preserves anatomy while smoothing facets — needed for clean
#    normals in the normal-map render pass.  use_limit_surface=False for speed.
# ---------------------------------------------------------------------------

_hb_mod = _hb_obj.modifiers.new("Subd", "SUBSURF")
_hb_mod.subdivision_type = 'CATMULL_CLARK'
_hb_mod.levels = 1
_hb_mod.render_levels = 1
_hb_mod.use_limit_surface = False

# ---------------------------------------------------------------------------
# 7. Position and rotation
#    Rotation order: Z (turn) → Y (tilt) → X (nod) applied as Euler ZYX.
# ---------------------------------------------------------------------------

_hb_obj.location = (_hb_cx, _hb_cy, _hb_cz)
_hb_obj.rotation_mode  = "ZYX"
_hb_obj.rotation_euler = (_hb_nod, _hb_tilt, _hb_turn)

# Select and make active for any downstream operations.
_hb_bpy.context.view_layer.objects.active = _hb_obj
_hb_obj.select_set(True)

# Tidy up module-level names that callers should not reuse.
del _hb_disp_verts, _hb_raw_verts, _hb_raw_faces
# ---- end head_builder block -----------------------------------------------
"""
