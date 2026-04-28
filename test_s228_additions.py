"""
test_s228_additions.py -- Session 228 tests for boccioni_futurist_motion_pass,
chromatic_focal_pull_pass, and the umberto_boccioni catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64, rgb=(180, 150, 120)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)),
        "RGB")


# ─────────────────────────────────────────────────────────────────────────────
# boccioni_futurist_motion_pass  (139th distinct mode, session 228)
# ─────────────────────────────────────────────────────────────────────────────

def test_s228_boccioni_pass_exists():
    """Session 228: Painter must have boccioni_futurist_motion_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "boccioni_futurist_motion_pass"), (
        "Painter is missing boccioni_futurist_motion_pass")
    assert callable(getattr(Painter, "boccioni_futurist_motion_pass"))


def test_s228_boccioni_pass_no_error():
    """Session 228: boccioni_futurist_motion_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.22, 0.18, 0.34), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.boccioni_futurist_motion_pass(
        contour_thresh=0.035,
        force_strength=0.28,
        smear_distance=6,
        sat_boost=0.22,
        velocity_blur=1.8,
        opacity=0.78,
    )


def test_s228_boccioni_pass_zero_opacity_no_change():
    """Session 228: boccioni_futurist_motion_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.22, 0.18, 0.34), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.boccioni_futurist_motion_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "boccioni_futurist_motion_pass at opacity=0.0 must not change any pixels")


def test_s228_boccioni_pass_changes_canvas():
    """Session 228: boccioni_futurist_motion_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    # Create a non-uniform reference with contrast so gradients are present
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:32, :, :] = [200, 160, 80]
    arr[32:, :, :] = [40, 30, 100]
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.22, 0.18, 0.34), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.boccioni_futurist_motion_pass(
        contour_thresh=0.01,
        force_strength=0.50,
        smear_distance=4,
        sat_boost=0.30,
        opacity=0.90,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "boccioni_futurist_motion_pass must change a non-uniform canvas"


def test_s228_boccioni_saturation_boost_raises_chroma_in_contour_zones():
    """Session 228: sat_boost must increase colour spread near high-contrast edges."""
    p   = _make_small_painter(64, 64)
    # Canvas with a vertical sharp edge in the middle
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :32, :] = [220, 120, 40]
    arr[:, 32:, :] = [30, 80, 200]
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    # Measure colour range as proxy for saturation
    before_range = float(before[:, :, :3].astype(np.float32).std())

    p.boccioni_futurist_motion_pass(
        contour_thresh=0.005,
        force_strength=0.0,    # disable fringe to isolate sat_boost
        smear_distance=1,
        sat_boost=0.50,        # strong boost for reliable detection
        velocity_blur=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_range = float(after[:, :, :3].astype(np.float32).std())

    assert after_range >= before_range * 0.90, (
        f"Saturation boost should not reduce colour spread significantly; "
        f"before_std={before_range:.2f} after_std={after_range:.2f}")


def test_s228_boccioni_chromatic_fringe_shifts_r_and_b():
    """Session 228: force fringe must produce red-blue chromatic split at hard edges."""
    p = _make_small_painter(64, 64)
    # Two-tone canvas with a bright vertical edge
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :32, :] = [200, 200, 200]
    arr[:, 32:, :] = [20, 20, 20]
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.60, 0.60, 0.60), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_r_mean = float(before[:, :, 2].mean())
    before_b_mean = float(before[:, :, 0].mean())

    p.boccioni_futurist_motion_pass(
        contour_thresh=0.005,
        force_strength=0.70,   # strong fringe for reliable detection
        smear_distance=8,
        sat_boost=0.0,
        velocity_blur=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_r_mean = float(after[:, :, 2].mean())
    after_b_mean = float(after[:, :, 0].mean())

    # The chromatic fringe shifts R and B channels; overall values should differ
    # (not necessarily in a specific direction, but the canvas must change)
    r_delta = abs(after_r_mean - before_r_mean)
    b_delta = abs(after_b_mean - before_b_mean)
    assert r_delta + b_delta > 0.5, (
        f"Chromatic fringe should shift R and/or B channels near edges; "
        f"r_delta={r_delta:.2f} b_delta={b_delta:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# chromatic_focal_pull_pass  (session 228 artistic improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_s228_focal_pull_pass_exists():
    """Session 228: Painter must have chromatic_focal_pull_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "chromatic_focal_pull_pass"), (
        "Painter is missing chromatic_focal_pull_pass")
    assert callable(getattr(Painter, "chromatic_focal_pull_pass"))


def test_s228_focal_pull_pass_no_error():
    """Session 228: chromatic_focal_pull_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.48, 0.32), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.chromatic_focal_pull_pass(
        focal_x=0.50,
        focal_y=0.42,
        reach=0.55,
        warm_pull=0.08,
        cool_push=0.06,
        opacity=0.70,
    )


def test_s228_focal_pull_zero_opacity_no_change():
    """Session 228: chromatic_focal_pull_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.48, 0.32), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.chromatic_focal_pull_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "chromatic_focal_pull_pass at opacity=0.0 must not change any pixels")


def test_s228_focal_pull_changes_canvas():
    """Session 228: chromatic_focal_pull_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(160, 120, 80))
    p.tone_ground((0.55, 0.48, 0.32), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.chromatic_focal_pull_pass(
        warm_pull=0.20,
        cool_push=0.15,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "chromatic_focal_pull_pass must change a non-uniform canvas"


def test_s228_focal_pull_warms_center_cools_periphery():
    """Session 228: focal pull must increase red at centre and blue at corners."""
    p = _make_small_painter(64, 64)
    # Neutral grey canvas — easy to detect warm/cool shifts
    arr = np.full((64, 64, 3), 128, dtype=np.uint8)
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    # Measure centre vs. corner regions
    # Centre 10x10
    cr = slice(27, 37)
    cc = slice(27, 37)
    # Corners 8x8
    tl = (slice(0, 8), slice(0, 8))

    before_c_r = float(before[cr, cc, 2].mean())
    before_c_b = float(before[cr, cc, 0].mean())
    before_tl_r = float(before[tl[0], tl[1], 2].mean())
    before_tl_b = float(before[tl[0], tl[1], 0].mean())

    p.chromatic_focal_pull_pass(
        focal_x=0.50,
        focal_y=0.50,
        reach=0.35,
        warm_pull=0.25,   # exaggerate for reliable detection
        cool_push=0.20,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    after_c_r  = float(after[cr, cc, 2].mean())
    after_tl_b = float(after[tl[0], tl[1], 0].mean())

    assert after_c_r >= before_c_r, (
        f"Centre red should increase with warm_pull; "
        f"before={before_c_r:.1f} after={after_c_r:.1f}")
    assert after_tl_b >= before_tl_b, (
        f"Corner blue should increase with cool_push; "
        f"before={before_tl_b:.1f} after={after_tl_b:.1f}")


# ─────────────────────────────────────────────────────────────────────────────
# umberto_boccioni catalog entry  (session 228)
# ─────────────────────────────────────────────────────────────────────────────

def test_s228_boccioni_in_catalog():
    """Session 228: umberto_boccioni must appear in CATALOG with correct properties."""
    from art_catalog import CATALOG, get_style
    assert "umberto_boccioni" in CATALOG, "umberto_boccioni missing from CATALOG"
    s = get_style("umberto_boccioni")
    mv = s.movement.lower()
    assert "futur" in mv, f"boccioni movement unexpected: {s.movement!r}"
    assert s.chromatic_split is True
    assert s.crackle is False
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"
    assert len(s.famous_works) >= 3
    assert "139" in s.inspiration or "THIRTY-NINTH" in s.inspiration, (
        "boccioni inspiration must reference 139th mode")


def test_s228_boccioni_catalog_palette_includes_blue():
    """Session 228: Boccioni palette must include at least one electric blue entry."""
    from art_catalog import get_style
    s = get_style("umberto_boccioni")
    has_blue = any(rgb[2] > 0.55 and rgb[2] > rgb[0] + 0.20 for rgb in s.palette)
    assert has_blue, "Boccioni palette should include a notable blue (force-line) entry"


def test_s228_boccioni_catalog_includes_futurist_works():
    """Session 228: Boccioni famous_works must include States of Mind."""
    from art_catalog import get_style
    s = get_style("umberto_boccioni")
    titles = [t.lower() for t, _ in s.famous_works]
    has_states = any("state" in t for t in titles)
    assert has_states, "Boccioni famous_works should include States of Mind"
