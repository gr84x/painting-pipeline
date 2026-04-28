"""
test_s230_additions.py -- Session 230 tests for hammershoi_grey_interior_pass,
chromatic_memory_pass, and the vilhelm_hammershoi catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64, rgb=(160, 155, 148)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)),
        "RGB")


# ─────────────────────────────────────────────────────────────────────────────
# Art catalog — vilhelm_hammershoi entry  (session 230)
# ─────────────────────────────────────────────────────────────────────────────

def test_s230_catalog_hammershoi_exists():
    """Session 230: CATALOG must contain 'vilhelm_hammershoi' key."""
    from art_catalog import CATALOG
    assert "vilhelm_hammershoi" in CATALOG, (
        "CATALOG is missing 'vilhelm_hammershoi' entry")


def test_s230_catalog_hammershoi_fields():
    """Session 230: vilhelm_hammershoi ArtStyle must have all required fields."""
    from art_catalog import CATALOG
    s = CATALOG["vilhelm_hammershoi"]
    assert s.artist == "Vilhelm Hammershøi"
    assert "Danish" in s.nationality
    assert len(s.palette) >= 5
    assert 0.0 <= s.wet_blend <= 1.0
    assert 0.0 <= s.edge_softness <= 1.0
    assert len(s.famous_works) >= 3
    assert "hammershoi_grey_interior_pass" in s.inspiration


def test_s230_catalog_hammershoi_get_style():
    """Session 230: get_style('vilhelm_hammershoi') must return the entry without error."""
    from art_catalog import get_style
    s = get_style("vilhelm_hammershoi")
    assert s.artist == "Vilhelm Hammershøi"


def test_s230_catalog_hammershoi_palette_is_grey():
    """Session 230: Hammershøi palette must be near-grey (low saturation)."""
    from art_catalog import CATALOG
    s = CATALOG["vilhelm_hammershoi"]
    for r, g, b in s.palette:
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        sat = (cmax - cmin) / (cmax + 1e-6) if cmax > 1e-6 else 0.0
        assert sat < 0.25, (
            f"Hammershøi palette colour ({r:.2f},{g:.2f},{b:.2f}) "
            f"has saturation {sat:.3f} > 0.25 — should be near-grey")


# ─────────────────────────────────────────────────────────────────────────────
# hammershoi_grey_interior_pass  (141st distinct mode, session 230)
# ─────────────────────────────────────────────────────────────────────────────

def test_s230_hammershoi_pass_exists():
    """Session 230: Painter must have hammershoi_grey_interior_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "hammershoi_grey_interior_pass"), (
        "Painter is missing hammershoi_grey_interior_pass")
    assert callable(getattr(Painter, "hammershoi_grey_interior_pass"))


def test_s230_hammershoi_pass_no_error():
    """Session 230: hammershoi_grey_interior_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.52, 0.51, 0.50), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.hammershoi_grey_interior_pass(
        grey_veil=0.55,
        window_lift=0.09,
        window_cool=0.06,
        stillness_sigma=1.6,
        stillness_str=0.40,
        opacity=0.70,
    )


def test_s230_hammershoi_pass_zero_opacity_no_change():
    """Session 230: hammershoi_grey_interior_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.52, 0.51, 0.50), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.hammershoi_grey_interior_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "hammershoi_grey_interior_pass at opacity=0.0 must not change any pixels")


def test_s230_hammershoi_pass_changes_canvas():
    """Session 230: hammershoi_grey_interior_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(160, 130, 90))
    p.tone_ground((0.52, 0.51, 0.50), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.hammershoi_grey_interior_pass(
        grey_veil=0.70,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "hammershoi_grey_interior_pass must change a non-uniform canvas"


def test_s230_hammershoi_grey_veil_desaturates():
    """Session 230: grey_veil must reduce saturation in midtone regions."""
    p = _make_small_painter(64, 64)
    # A saturated mid-luminance canvas: orange mid-grey
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :, 0] = 190   # R
    arr[:, :, 1] = 120   # G
    arr[:, :, 2] = 60    # B
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.60, 0.45, 0.25), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    # Measure saturation before
    buf_before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    r_b = buf_before[:, :, 2].astype(np.float32) / 255.0
    g_b = buf_before[:, :, 1].astype(np.float32) / 255.0
    b_b = buf_before[:, :, 0].astype(np.float32) / 255.0
    cmax_b = np.maximum(np.maximum(r_b, g_b), b_b)
    cmin_b = np.minimum(np.minimum(r_b, g_b), b_b)
    sat_before = np.mean((cmax_b - cmin_b) / (cmax_b + 1e-6))

    p.hammershoi_grey_interior_pass(grey_veil=0.80, opacity=1.0)

    buf_after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    r_a = buf_after[:, :, 2].astype(np.float32) / 255.0
    g_a = buf_after[:, :, 1].astype(np.float32) / 255.0
    b_a = buf_after[:, :, 0].astype(np.float32) / 255.0
    cmax_a = np.maximum(np.maximum(r_a, g_a), b_a)
    cmin_a = np.minimum(np.minimum(r_a, g_a), b_a)
    sat_after = np.mean((cmax_a - cmin_a) / (cmax_a + 1e-6))

    assert sat_after < sat_before, (
        f"hammershoi_grey_interior_pass must reduce saturation: "
        f"before={sat_before:.4f} after={sat_after:.4f}")


def test_s230_hammershoi_window_brightens_left():
    """Session 230: window_lift must brighten the left side more than the right side."""
    p = _make_small_painter(64, 64)
    # Uniform grey canvas
    arr = np.full((64, 64, 3), 128, dtype=np.uint8)
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    p.hammershoi_grey_interior_pass(
        grey_veil=0.0,
        window_lift=0.15,
        window_cool=0.0,
        stillness_str=0.0,
        opacity=1.0,
    )

    buf = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    lum_left  = buf[:, :16, 2].astype(np.float32).mean()   # R channel left column
    lum_right = buf[:, 48:, 2].astype(np.float32).mean()   # R channel right column
    assert lum_left > lum_right, (
        f"window_lift must produce brighter left than right: "
        f"left_lum={lum_left:.1f} right_lum={lum_right:.1f}")


def test_s230_hammershoi_pass_default_params():
    """Session 230: hammershoi_grey_interior_pass must run with all default parameters."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.52, 0.51, 0.50), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.hammershoi_grey_interior_pass()   # all defaults


def test_s230_hammershoi_pass_extreme_grey_veil():
    """Session 230: grey_veil=1.0 must yield a near-monochromatic result."""
    p = _make_small_painter(64, 64)
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :, 0] = 200
    arr[:, :, 1] = 100
    arr[:, :, 2] = 40
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.65, 0.38, 0.15), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    p.hammershoi_grey_interior_pass(
        grey_veil=1.0,
        window_lift=0.0,
        window_cool=0.0,
        stillness_str=0.0,
        opacity=1.0,
    )

    buf = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    r_a = buf[:, :, 2].astype(np.float32) / 255.0
    g_a = buf[:, :, 1].astype(np.float32) / 255.0
    b_a = buf[:, :, 0].astype(np.float32) / 255.0
    cmax_a = np.maximum(np.maximum(r_a, g_a), b_a)
    cmin_a = np.minimum(np.minimum(r_a, g_a), b_a)
    sat_after = np.mean((cmax_a - cmin_a) / (cmax_a + 1e-6))
    assert sat_after < 0.15, (
        f"grey_veil=1.0 should yield near-monochrome; mean_sat={sat_after:.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# chromatic_memory_pass  (session 230 artistic improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_s230_chromatic_memory_pass_exists():
    """Session 230: Painter must have chromatic_memory_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "chromatic_memory_pass"), (
        "Painter is missing chromatic_memory_pass")
    assert callable(getattr(Painter, "chromatic_memory_pass"))


def test_s230_chromatic_memory_pass_no_error():
    """Session 230: chromatic_memory_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.52, 0.51, 0.50), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.chromatic_memory_pass(
        memory_radius=9,
        memory_pull=0.22,
        sat_threshold=0.18,
        opacity=0.60,
    )


def test_s230_chromatic_memory_pass_zero_opacity_no_change():
    """Session 230: chromatic_memory_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.52, 0.51, 0.50), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.chromatic_memory_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "chromatic_memory_pass at opacity=0.0 must not change any pixels")


def test_s230_chromatic_memory_pass_changes_canvas():
    """Session 230: chromatic_memory_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    # Build a canvas with varied low-saturation tones
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:32, :, :] = [180, 170, 160]
    arr[32:, :, :] = [140, 145, 150]
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.60, 0.58, 0.55), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.chromatic_memory_pass(
        memory_radius=9,
        memory_pull=0.40,
        sat_threshold=0.30,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "chromatic_memory_pass must change a non-uniform canvas"


def test_s230_chromatic_memory_skips_saturated_pixels():
    """Session 230: chromatic_memory_pass must leave highly saturated pixels unchanged."""
    p = _make_small_painter(64, 64)
    # Fully saturated red canvas — sat >> sat_threshold
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :, 0] = 220   # R very high
    arr[:, :, 1] = 10    # G very low
    arr[:, :, 2] = 10    # B very low
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.86, 0.04, 0.04), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.chromatic_memory_pass(
        memory_pull=1.0,
        sat_threshold=0.05,   # very low threshold; saturated red well above it
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    # Saturated pixels should be nearly unchanged
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).mean()
    assert diff < 8.0, (
        f"chromatic_memory_pass should leave highly saturated pixels near-unchanged; "
        f"mean_diff={diff:.2f}")


def test_s230_chromatic_memory_pull_reduces_boundary_contrast():
    """Session 230: memory_pull must reduce the contrast at a hard colour boundary."""
    p = _make_small_painter(64, 64)
    # Two halves: warm grey left, cool grey right — both low saturation
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :32, :] = [175, 168, 158]   # warm grey
    arr[:, 32:, :] = [155, 160, 170]   # cool grey
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.60, 0.60, 0.60), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    # Contrast at boundary before
    buf_b = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    contrast_before = np.abs(
        buf_b[:, 30, 2].astype(np.float32) - buf_b[:, 34, 2].astype(np.float32)
    ).mean()

    p.chromatic_memory_pass(
        memory_radius=12,
        memory_pull=0.50,
        sat_threshold=0.25,
        opacity=1.0,
    )

    buf_a = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    contrast_after = np.abs(
        buf_a[:, 30, 2].astype(np.float32) - buf_a[:, 34, 2].astype(np.float32)
    ).mean()

    assert contrast_after <= contrast_before + 1.0, (
        f"chromatic_memory_pass should not increase boundary contrast: "
        f"before={contrast_before:.2f} after={contrast_after:.2f}")


def test_s230_chromatic_memory_default_params():
    """Session 230: chromatic_memory_pass must run with all default parameters."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.52, 0.51, 0.50), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.chromatic_memory_pass()   # all defaults
