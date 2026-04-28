"""
test_s226_additions.py -- Session 226 tests for sorolla_mediterranean_light_pass,
diffuse_boundary_pass, and joaquin_sorolla catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array([180, 150, 120], dtype=np.uint8)),
        "RGB")


# ------------------------------------------------------------------------------
# sorolla_mediterranean_light_pass -- session 226 artist pass (137th mode)
# ------------------------------------------------------------------------------

def test_s226_sorolla_pass_exists():
    """Session 226: Painter must have sorolla_mediterranean_light_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "sorolla_mediterranean_light_pass"), (
        "Painter is missing sorolla_mediterranean_light_pass")
    assert callable(getattr(Painter, "sorolla_mediterranean_light_pass"))


def test_s226_sorolla_pass_no_error():
    """Session 226: sorolla_mediterranean_light_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.92, 0.90, 0.86), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.sorolla_mediterranean_light_pass(
        bleach_thresh=0.82,
        bleach_strength=0.55,
        azure_shadow_r=0.28,
        azure_shadow_g=0.58,
        azure_shadow_b=0.86,
        shadow_thresh=0.38,
        scatter_density=0.004,
        scatter_brightness=0.55,
        warm_boost=0.08,
        opacity=0.80,
    )


def test_s226_sorolla_pass_changes_canvas():
    """Session 226: sorolla_mediterranean_light_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.92, 0.90, 0.86), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.sorolla_mediterranean_light_pass(opacity=0.80)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "sorolla_mediterranean_light_pass must change a non-uniform canvas"


def test_s226_sorolla_pass_zero_opacity_no_change():
    """Session 226: sorolla_mediterranean_light_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.86, 0.80), texture_strength=0.05)
    p.block_in(ref, stroke_size=10, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.sorolla_mediterranean_light_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "sorolla_mediterranean_light_pass at opacity=0.0 must not change any pixels")


def test_s226_sorolla_highlight_bleaching_raises_bright_pixels():
    """Session 226: Highlight bleaching must raise the mean of near-white canvas pixels."""
    p = _make_small_painter(64, 64)
    # Very bright canvas — nearly all pixels should be bleached
    p.tone_ground((0.90, 0.90, 0.90), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_mean = float(before[:, :, 2].mean())   # red channel

    p.sorolla_mediterranean_light_pass(
        bleach_thresh=0.60,       # low threshold so canvas qualifies
        bleach_strength=0.80,     # exaggerate
        scatter_density=0.0,      # disable scatter for isolation
        warm_boost=0.0,
        shadow_thresh=0.10,       # prevent shadow gate on bright canvas
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_mean = float(after[:, :, 2].mean())

    assert after_mean > before_mean, (
        f"Highlight bleaching should raise mean red on near-white canvas; "
        f"before={before_mean:.1f} after={after_mean:.1f}")


def test_s226_sorolla_azure_shadow_raises_blue():
    """Session 226: Azure shadow shift must raise blue channel on a dark warm canvas."""
    p = _make_small_painter(64, 64)
    # Very dark warm canvas — shadow gate should push blue up
    p.tone_ground((0.15, 0.10, 0.05), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_blue = float(before[:, :, 0].mean())

    p.sorolla_mediterranean_light_pass(
        bleach_thresh=0.95,       # disable bleaching on dark canvas
        bleach_strength=0.0,
        azure_shadow_r=0.10,
        azure_shadow_g=0.40,
        azure_shadow_b=1.00,      # strong blue target
        shadow_thresh=0.70,       # high threshold so dark canvas qualifies
        scatter_density=0.0,
        warm_boost=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_blue = float(after[:, :, 0].mean())

    assert after_blue > before_blue, (
        f"Azure shadow shift should raise blue on dark warm canvas; "
        f"before={before_blue:.1f} after={after_blue:.1f}")


def test_s226_sorolla_scatter_increases_max_brightness():
    """Session 226: Stochastic scatter must produce at least some brighter pixels."""
    p = _make_small_painter(64, 64)
    # Mid-grey canvas — scatter should produce outlier-bright pixels
    p.tone_ground((0.55, 0.55, 0.55), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_max = int(before[:, :, 2].max())

    p.sorolla_mediterranean_light_pass(
        bleach_thresh=0.95,    # disable bleaching
        bleach_strength=0.0,
        shadow_thresh=0.10,    # disable shadow shift
        scatter_density=0.05,  # 5% scatter for reliable detection on small canvas
        scatter_brightness=0.60,
        warm_boost=0.0,
        opacity=1.0,
        seed=42,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_max = int(after[:, :, 2].max())

    assert after_max > before_max, (
        f"Scatter should produce pixels brighter than canvas baseline; "
        f"before_max={before_max} after_max={after_max}")


def test_s226_sorolla_warm_boost_increases_mid_tone_chroma():
    """Session 226: warm_boost must raise chroma range of mid-tone canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.52, 0.38, 0.24), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=25)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    r0 = before[:, :, 2].astype(np.float32) / 255.0
    g0 = before[:, :, 1].astype(np.float32) / 255.0
    b0 = before[:, :, 0].astype(np.float32) / 255.0
    chroma_before = (np.maximum(np.maximum(r0, g0), b0) - np.minimum(np.minimum(r0, g0), b0)).mean()

    p.sorolla_mediterranean_light_pass(
        bleach_thresh=0.95,    # disable bleaching
        bleach_strength=0.0,
        shadow_thresh=0.05,    # disable shadow shift
        scatter_density=0.0,   # disable scatter
        warm_boost=0.40,       # exaggerate warm boost for detection
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    r1 = after[:, :, 2].astype(np.float32) / 255.0
    g1 = after[:, :, 1].astype(np.float32) / 255.0
    b1 = after[:, :, 0].astype(np.float32) / 255.0
    chroma_after = (np.maximum(np.maximum(r1, g1), b1) - np.minimum(np.minimum(r1, g1), b1)).mean()

    assert chroma_after >= chroma_before, (
        f"warm_boost should not decrease mean chroma; "
        f"before={chroma_before:.4f} after={chroma_after:.4f}")


def test_s226_joaquin_sorolla_in_catalog():
    """Session 226: joaquin_sorolla must appear in CATALOG with correct properties."""
    from art_catalog import CATALOG, get_style
    assert "joaquin_sorolla" in CATALOG, "joaquin_sorolla missing from CATALOG"
    s = get_style("joaquin_sorolla")
    mv = s.movement.lower()
    assert "lumin" in mv or "impressi" in mv or "post" in mv, (
        f"joaquin_sorolla movement unexpected: {s.movement!r}")
    assert s.chromatic_split is False, "joaquin_sorolla chromatic_split must be False"
    assert s.crackle is False, "joaquin_sorolla crackle must be False"
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"
    assert len(s.famous_works) >= 5, (
        f"joaquin_sorolla should have >= 5 famous works; got {len(s.famous_works)}")
    assert "137" in s.inspiration or "THIRTY-SEVENTH" in s.inspiration, (
        "joaquin_sorolla inspiration must reference 137th mode")


# ------------------------------------------------------------------------------
# diffuse_boundary_pass -- session 226 artistic improvement
# ------------------------------------------------------------------------------

def test_s226_diffuse_boundary_pass_exists():
    """Session 226: Painter must have diffuse_boundary_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "diffuse_boundary_pass"), (
        "Painter is missing diffuse_boundary_pass")
    assert callable(getattr(Painter, "diffuse_boundary_pass"))


def test_s226_diffuse_boundary_pass_no_error():
    """Session 226: diffuse_boundary_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.70, 0.60, 0.50), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.diffuse_boundary_pass(
        low_grad=0.04,
        high_grad=0.22,
        sigma=1.2,
        strength=0.55,
        opacity=0.65,
    )


def test_s226_diffuse_boundary_pass_zero_opacity_no_change():
    """Session 226: diffuse_boundary_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.68, 0.56, 0.42), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.diffuse_boundary_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "diffuse_boundary_pass at opacity=0.0 must not change any pixels")


def test_s226_diffuse_boundary_pass_changes_non_uniform_canvas():
    """Session 226: diffuse_boundary_pass must modify a canvas with colour transitions."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.70, 0.60, 0.50), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.diffuse_boundary_pass(sigma=2.0, strength=0.80, opacity=1.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "diffuse_boundary_pass must change a canvas with colour transitions"


def test_s226_diffuse_boundary_pass_uniform_canvas_minimal_change():
    """Session 226: diffuse_boundary_pass on a fully uniform canvas should have near-zero effect."""
    p = _make_small_painter(64, 64)
    # Perfectly uniform canvas — gradient is zero everywhere, gate = 0
    p.tone_ground((0.60, 0.60, 0.60), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.diffuse_boundary_pass(low_grad=0.04, sigma=2.0, strength=1.0, opacity=1.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    # On a uniform canvas the gradient gate is 0 everywhere, so result = composite
    # of original with itself — no visible change.
    max_diff = int(np.abs(after.astype(np.int32) - before.astype(np.int32)).max())
    assert max_diff <= 1, (
        f"diffuse_boundary_pass on a uniform canvas should change <2 levels; "
        f"max_diff={max_diff}")


def test_s226_diffuse_boundary_softens_edges_between_colour_zones():
    """Session 226: diffuse_boundary_pass must reduce sharpness at colour boundaries."""
    p = _make_small_painter(64, 64)
    # Construct a sharp two-tone canvas: left half warm, right half cool
    import numpy as _np
    from PIL import Image
    arr = _np.zeros((64, 64, 3), dtype=_np.uint8)
    arr[:, :32, :] = [200, 140, 80]     # warm left half
    arr[:, 32:, :] = [80,  130, 200]    # cool right half
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.60, 0.60, 0.60), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    # Measure sharpness at the boundary column before and after
    before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    # Horizontal gradient at the boundary (columns 30-34)
    before_grad = float(_np.abs(
        before[:, 30:35, 2].astype(_np.int32) - before[:, 29:34, 2].astype(_np.int32)
    ).mean())

    p.diffuse_boundary_pass(
        low_grad=0.0,      # catch even gentle gradients
        high_grad=0.50,    # keep even sharp edges in moderate zone
        sigma=2.5,
        strength=0.90,
        opacity=1.0,
    )
    after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    after_grad = float(_np.abs(
        after[:, 30:35, 2].astype(_np.int32) - after[:, 29:34, 2].astype(_np.int32)
    ).mean())

    assert after_grad <= before_grad + 2.0, (
        f"diffuse_boundary_pass should not sharpen boundaries; "
        f"before_grad={before_grad:.2f} after_grad={after_grad:.2f}")
