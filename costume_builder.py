"""
costume_builder.py

Generates Blender Python code (as a string) that creates a dark Renaissance
dress/robe mesh when executed inside Blender's headless Python interpreter.

Module interface
----------------
    build_costume_code(lm: dict, costume=None, pose_name: str = "SEATED") -> str
"""

from __future__ import annotations

import math
import textwrap
from typing import Any


# ---------------------------------------------------------------------------
# Ring profile: (z, radius) — floor-to-shoulder
# ---------------------------------------------------------------------------
_RINGS: list[tuple[float, float]] = [
    (0.06, 0.370),   # floor-level skirt hem
    (0.15, 0.340),
    (0.25, 0.310),
    (0.35, 0.285),
    (0.46, 0.230),   # waist (seated hip)
    (0.56, 0.200),   # lower bodice
    (0.66, 0.180),   # mid bodice
    (0.76, 0.170),   # upper bodice — wider than torso (r=0.130) for visibility
    (0.86, 0.200),   # chest
    (0.95, 0.240),   # upper chest / bust
    (1.03, 0.285),   # shoulder / neckline — clearly wider than neck metaballs
]

_SEGMENTS: int = 24

# Skirt fold parameters (applied where z < 0.55)
_FOLD_Z_THRESHOLD: float = 0.55
_FOLD_Z_BASE: float = 0.49          # denominator in the weight formula
_FOLD_AMPLITUDE: float = 0.022
_FOLD_FREQ: int = 7
_FOLD_PHASE: float = 0.3

# Object centre offset — Y=0 centres the dress on the figure origin;
# slight +Y was causing the dress to sit behind the forward-seated body.
_CENTRE_OFFSET: tuple[float, float, float] = (0.0, 0.0, 0.0)

# Material properties
_MAT_NAME: str = "Dress"
_MAT_BASE_COLOR: tuple[float, float, float, float] = (0.018, 0.014, 0.010, 1.0)
_MAT_ROUGHNESS: float = 0.72
_MAT_SHEEN_WEIGHT: float = 0.15
_MAT_SHEEN_TINT: float = 0.40
_MAT_SPECULAR_IOR: float = 0.08


# ---------------------------------------------------------------------------
# Geometry helpers (Python-side, used to bake literal vertex/face data)
# ---------------------------------------------------------------------------

def _build_geometry() -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    """
    Compute dress vertices and faces in Python so the generated Blender
    script contains literal data rather than runtime loops.

    Returns
    -------
    verts : list of (x, y, z) tuples — fold displacement already applied
    faces : list of index tuples  — quads for the body, triangles for the bottom cap
    """
    num_rings = len(_RINGS)
    raw_verts: list[tuple[float, float, float]] = []

    # Build raw ring vertices (no displacement yet)
    for z, r in _RINGS:
        for seg in range(_SEGMENTS):
            angle = 2.0 * math.pi * seg / _SEGMENTS
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            raw_verts.append((x, y, z))

    # Apply fold displacement to skirt vertices (z < _FOLD_Z_THRESHOLD)
    verts: list[tuple[float, float, float]] = []
    for x, y, z in raw_verts:
        if z < _FOLD_Z_THRESHOLD:
            phi = math.atan2(y, x)
            r_cur = math.sqrt(x * x + y * y)
            weight = max(0.0, (_FOLD_Z_THRESHOLD - z) / _FOLD_Z_BASE)
            fold = _FOLD_AMPLITUDE * math.sin(_FOLD_FREQ * phi + _FOLD_PHASE) * weight
            if r_cur > 1e-9:
                dx = x / r_cur
                dy = y / r_cur
            else:
                dx, dy = 1.0, 0.0
            x += dx * fold
            y += dy * fold
        verts.append((x, y, z))

    # Quad faces between consecutive rings
    faces: list[tuple[int, ...]] = []
    for ring in range(num_rings - 1):
        base_bot = ring * _SEGMENTS
        base_top = (ring + 1) * _SEGMENTS
        for seg in range(_SEGMENTS):
            next_seg = (seg + 1) % _SEGMENTS
            bl = base_bot + seg
            br = base_bot + next_seg
            tr = base_top + next_seg
            tl = base_top + seg
            faces.append((bl, br, tr, tl))

    # Bottom triangle fan — cap the floor ring
    num_body_verts = num_rings * _SEGMENTS
    centre_idx = num_body_verts
    bot_ring_z, bot_ring_r = _RINGS[0]
    # Centre point of the bottom cap (slight average radius = 0 for a true centre)
    verts.append((0.0, 0.0, bot_ring_z))

    for seg in range(_SEGMENTS):
        next_seg = (seg + 1) % _SEGMENTS
        v0 = seg                      # bottom ring, current seg
        v1 = next_seg                 # bottom ring, next seg
        # Wind so the face normal points downward (outward from the bottom)
        faces.append((centre_idx, v1, v0))

    # Top is left OPEN — no cap added.

    return verts, faces


# ---------------------------------------------------------------------------
# Code-generation utilities
# ---------------------------------------------------------------------------

def _fmt_verts(verts: list[tuple[float, float, float]]) -> str:
    """Format vertex list as a compact multi-line Python literal."""
    lines = ["    ["]
    for v in verts:
        lines.append(f"        ({v[0]:.6f}, {v[1]:.6f}, {v[2]:.6f}),")
    lines.append("    ]")
    return "\n".join(lines)


def _fmt_faces(faces: list[tuple[int, ...]]) -> str:
    """Format face list as a compact multi-line Python literal."""
    lines = ["    ["]
    for f in faces:
        inner = ", ".join(str(i) for i in f)
        lines.append(f"        ({inner}),")
    lines.append("    ]")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_costume_code(
    lm: dict,
    costume: Any = None,
    pose_name: str = "SEATED",
) -> str:
    """
    Generate Blender Python source code that creates a dark Renaissance
    dress/robe mesh when executed inside a Blender headless session.

    Parameters
    ----------
    lm : dict
        Layout metadata passed in by the caller (reserved for future use;
        not currently used but kept for API compatibility).
    costume : any, optional
        Optional costume descriptor (reserved; not currently used).
    pose_name : str, optional
        Current pose name (e.g. "SEATED", "STANDING").  Currently informational
        only; may be used in future versions to adjust hem geometry.

    Returns
    -------
    str
        A self-contained Blender Python script string.
    """
    verts, faces = _build_geometry()

    verts_literal = _fmt_verts(verts)
    faces_literal = _fmt_faces(faces)

    cx, cy, cz = _CENTRE_OFFSET
    br, bg, bb, ba = _MAT_BASE_COLOR

    # NOTE: no textwrap.dedent — the template must start at column 0 so that
    # Blender's interpreter sees top-level (non-indented) statements.
    code = (
        "# --- costume_builder: Dark Renaissance Dress (pose=" + repr(pose_name) + ") ---\n"
        "import bpy\n"
        "import math\n"
        "\n"
        "# Vertex data (fold displacement baked in)\n"
        "_cb_verts = \\\n"
        + verts_literal + "\n\n"
        "# Face data\n"
        "_cb_faces = \\\n"
        + faces_literal + "\n\n"
        "_cb_mesh = bpy.data.meshes.new('DressMesh')\n"
        "_cb_mesh.from_pydata(_cb_verts, [], _cb_faces)\n"
        "_cb_mesh.update()\n"
        "\n"
        "for _cb_poly in _cb_mesh.polygons:\n"
        "    _cb_poly.use_smooth = True\n"
        "\n"
        "_cb_obj = bpy.data.objects.new('Dress', _cb_mesh)\n"
        f"_cb_obj.location = ({cx}, {cy}, {cz})\n"
        "bpy.context.collection.objects.link(_cb_obj)\n"
        "\n"
        "# --- Material: rebuild node tree from scratch for version safety ---\n"
        "_cb_mat = bpy.data.materials.new(name='DressMaterial')\n"
        "_cb_mat.use_nodes = True\n"
        "_cb_nt   = _cb_mat.node_tree\n"
        "_cb_nt.nodes.clear()\n"
        "_cb_out  = _cb_nt.nodes.new('ShaderNodeOutputMaterial')\n"
        "_cb_bsdf = _cb_nt.nodes.new('ShaderNodeBsdfPrincipled')\n"
        "_cb_out.location  = (300, 0)\n"
        "_cb_bsdf.location = (0, 0)\n"
        f"_cb_bsdf.inputs['Base Color'].default_value = ({br}, {bg}, {bb}, {ba})\n"
        f"_cb_bsdf.inputs['Roughness'].default_value = {_MAT_ROUGHNESS}\n"
        "for _cb_spec_k in ('Specular IOR Level', 'Specular'):\n"
        "    if _cb_spec_k in _cb_bsdf.inputs:\n"
        f"        _cb_bsdf.inputs[_cb_spec_k].default_value = {_MAT_SPECULAR_IOR}\n"
        "        break\n"
        "for _cb_sk in ('Sheen Weight', 'Sheen'):\n"
        "    if _cb_sk in _cb_bsdf.inputs:\n"
        f"        _cb_bsdf.inputs[_cb_sk].default_value = {_MAT_SHEEN_WEIGHT}\n"
        "        break\n"
        "# Sheen Tint is a Color socket in Blender 4+/5+; skip to avoid TypeError\n"
        "_cb_nt.links.new(_cb_bsdf.outputs['BSDF'], _cb_out.inputs['Surface'])\n"
        "print(f'[costume_builder] Base Color set to: {_cb_bsdf.inputs[\"Base Color\"].default_value[:]}')\n"
        "\n"
        "_cb_mesh.materials.clear()\n"
        "_cb_mesh.materials.append(_cb_mat)\n"
        "# --- end costume_builder ---\n"
    )

    return code


# ---------------------------------------------------------------------------
# Quick self-test (python costume_builder.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_lm: dict = {}
    result = build_costume_code(sample_lm, pose_name="SEATED")
    print(result)
    # Basic sanity checks
    assert "_cb_verts" in result
    assert "_cb_faces" in result
    assert "from_pydata" in result
    assert "use_smooth" in result
    assert "Dress" in result
    print(f"\n[OK] Generated {len(result)} characters of Blender code.")
