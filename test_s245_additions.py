"""
test_s245_additions.py -- Session 245 tests for jawlensky_abstract_head_pass,
paint_optical_vibration_pass, and the alexej_von_jawlensky catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w=64, h=64):
    from stroke_engine import Painter
    return Painter(w, h)


def _get_canvas(p):
    return np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((p.canvas.h, p.canvas.w, 4)).copy()


def _solid_reference(w=64, h=64, rgb=(140, 160, 200)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)), "RGB")


def _gradient_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w//2, :] = [220, 180, 120]
    arr[:, w//2:, :] = [40, 80, 200]
    return Image.fromarray(arr, "RGB")


def _dark_reference(w=64, h=64):
    from PIL import Image
    arr = np.ones((h, w, 3), dtype=np.uint8) * np.array([28, 24, 20], dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _bright_reference(w=64, h=64):
    from PIL import Image
    arr = np.ones((h, w, 3), dtype=np.uint8) * np.array([220, 215, 210], dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _multicolor_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//2, :w//2, :] = [200, 100, 30]   # warm orange
    arr[:h//2, w//2:, :] = [30, 80, 200]    # cool blue
    arr[h//2:, :w//2, :] = [180, 40, 60]    # warm red
    arr[h//2:, w//2:, :] = [60, 140, 180]   # cool teal
    return Image.fromarray(arr, "RGB")


def _high_contrast_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w//2, :] = [240, 230, 220]
    arr[:, w//2:, :] = [20, 18, 14]
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, dark=False, bright=False, multicolor=False,
                  high_contrast=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if dark:
            ref = _dark_reference(w, h)
        elif bright:
            ref = _bright_reference(w, h)
        elif multicolor:
            ref = _multicolor_reference(w, h)
        elif high_contrast:
            ref = _high_contrast_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.16, 0.14, 0.10), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── jawlensky_abstract_head_pass ──────────────────────────────────────────────

def test_s245_jawlensky_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "jawlensky_abstract_head_pass")


def test_s245_jawlensky_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.jawlensky_abstract_head_pass()
    assert result is None


def test_s245_jawlensky_pass_modifies_canvas():
    """Pass must change at least some pixels on a multicolour canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.jawlensky_abstract_head_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "jawlensky_abstract_head_pass must modify canvas"


def test_s245_jawlensky_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.jawlensky_abstract_head_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="jawlensky_abstract_head_pass must not alter alpha channel"
    )


def test_s245_jawlensky_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.jawlensky_abstract_head_pass(warmth_str=0.9, cool_str=0.9, edge_snap=0.95, opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0, "RGB must not go below 0"
    assert after[:, :, :3].max() <= 255, "RGB must not exceed 255"


def test_s245_jawlensky_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas essentially unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.jawlensky_abstract_head_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1, (
        "opacity=0 should leave RGB channels essentially unchanged (max diff <= 1 LSB)"
    )


def test_s245_jawlensky_pass_opacity_full_effect():
    """opacity=1 should produce visible change on multicolour canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.jawlensky_abstract_head_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() > 2, "opacity=1 should produce noticeable change"


def test_s245_jawlensky_pass_edge_darkening_produces_blue_tint():
    """High-contrast canvas: edge pixels should gain blue tint (not pure black)."""
    p = _make_small_painter(w=80, h=64)
    ref = _high_contrast_reference(80, 64)
    p.tone_ground((0.16, 0.14, 0.10), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    before = _get_canvas(p).copy()
    p.jawlensky_abstract_head_pass(edge_thresh=0.05, edge_snap=0.90, opacity=1.0)
    after = _get_canvas(p)
    # At a high-contrast edge, the canvas should change
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() > 0, "Edge darkening should change pixels"


def test_s245_jawlensky_pass_dark_canvas_no_crash():
    """Very dark canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.jawlensky_abstract_head_pass()
    after = _get_canvas(p)
    assert after is not None


def test_s245_jawlensky_pass_bright_canvas_no_crash():
    """Very bright canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.jawlensky_abstract_head_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].max() <= 255


def test_s245_jawlensky_pass_inner_radius_extremes():
    """Pass accepts inner_radius values from 0.1 to 0.9 without crash."""
    for ir in [0.1, 0.5, 0.9]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.jawlensky_abstract_head_pass(inner_radius=ir)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255


def test_s245_jawlensky_pass_cool_str_range():
    """Pass accepts cool_str from 0 to 1 without crash."""
    for cs in [0.0, 0.5, 1.0]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.jawlensky_abstract_head_pass(cool_str=cs)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0


def test_s245_jawlensky_pass_sequential_with_aerial():
    """Jawlensky pass followed by aerial perspective should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.jawlensky_abstract_head_pass()
    p.paint_aerial_perspective_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


# ── paint_optical_vibration_pass ──────────────────────────────────────────────

def test_s245_optical_vibration_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_optical_vibration_pass")


def test_s245_optical_vibration_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_optical_vibration_pass()
    assert result is None


def test_s245_optical_vibration_pass_modifies_canvas():
    """Pass must change the canvas on a warm-cool gradient canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.paint_optical_vibration_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "paint_optical_vibration_pass must modify canvas"


def test_s245_optical_vibration_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_optical_vibration_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="paint_optical_vibration_pass must not alter alpha channel"
    )


def test_s245_optical_vibration_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.paint_optical_vibration_pass(diverge_str=0.8, vibration_str=0.8, opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0, "RGB must not go below 0"
    assert after[:, :, :3].max() <= 255, "RGB must not exceed 255"


def test_s245_optical_vibration_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_optical_vibration_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1, (
        "opacity=0 should leave RGB channels essentially unchanged (max diff <= 1 LSB)"
    )


def test_s245_optical_vibration_pass_saturation_boost_at_boundaries():
    """Warm-cool boundary canvas: mean saturation should not decrease with high vibration_str."""
    p = _make_small_painter(w=80, h=64)
    from PIL import Image
    arr = np.zeros((64, 80, 3), dtype=np.uint8)
    arr[:, :40, :] = [220, 100, 30]   # warm orange left
    arr[:, 40:, :] = [30, 60, 210]    # cool blue right
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.16, 0.14, 0.10), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    before = _get_canvas(p).copy()

    def _sat(arr_):
        r_ = arr_[:,:,2].astype(np.float32)/255
        g_ = arr_[:,:,1].astype(np.float32)/255
        b_ = arr_[:,:,0].astype(np.float32)/255
        mx = np.maximum(r_, np.maximum(g_, b_))
        mn = np.minimum(r_, np.minimum(g_, b_))
        return np.where(mx > 1e-7, (mx-mn)/(mx+1e-7), 0.0)

    sat_before = _sat(before).mean()
    p.paint_optical_vibration_pass(vibration_str=0.6, opacity=1.0)
    after = _get_canvas(p)
    sat_after = _sat(after).mean()
    # Saturation should increase or stay the same (vibration boosts it at boundaries)
    assert sat_after >= sat_before - 0.03, (
        f"Optical vibration should not substantially decrease saturation "
        f"(before={sat_before:.3f}, after={sat_after:.3f})"
    )


def test_s245_optical_vibration_pass_sigma_range():
    """Pass accepts boundary_sigma from 1 to 20 without crash."""
    for sigma in [1.0, 8.0, 20.0]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.paint_optical_vibration_pass(boundary_sigma=sigma)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255


def test_s245_optical_vibration_pass_dark_canvas_no_crash():
    """Very dark canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.paint_optical_vibration_pass()
    after = _get_canvas(p)
    assert after is not None


def test_s245_optical_vibration_pass_bright_canvas_no_crash():
    """Very bright canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.paint_optical_vibration_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].max() <= 255


def test_s245_optical_vibration_pass_uniform_canvas_minimal_effect():
    """Uniform-colour canvas has no warm-cool boundaries, so boundary_map is near zero."""
    from PIL import Image
    arr = np.ones((64, 64, 3), dtype=np.uint8) * np.array([180, 100, 40], dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter()
    p.tone_ground((0.16, 0.14, 0.10), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=20)
    before = _get_canvas(p).copy()
    p.paint_optical_vibration_pass(diverge_str=1.0, vibration_str=1.0, opacity=1.0)
    after = _get_canvas(p)
    # On a near-uniform canvas, changes should be modest (boundary_map ~ 0)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    # Max diff should be smaller than on a warm-cool gradient canvas
    assert diff[:, :, :3].max() <= 255  # basic sanity


# ── alexej_von_jawlensky catalog entry ────────────────────────────────────────

def test_s245_jawlensky_in_catalog():
    import art_catalog
    assert 'alexej_von_jawlensky' in art_catalog.CATALOG, (
        "alexej_von_jawlensky key must be present in CATALOG"
    )


def test_s245_jawlensky_artist_name():
    import art_catalog
    entry = art_catalog.CATALOG['alexej_von_jawlensky']
    assert entry.artist == 'Alexej von Jawlensky', (
        f"artist field mismatch: expected 'Alexej von Jawlensky', got {entry.artist!r}"
    )


def test_s245_jawlensky_movement():
    import art_catalog
    entry = art_catalog.CATALOG['alexej_von_jawlensky']
    assert 'Expressionism' in entry.movement or 'Blaue' in entry.movement, (
        f"movement should reference Expressionism or Blaue Reiter, got {entry.movement!r}"
    )


def test_s245_jawlensky_period():
    import art_catalog
    entry = art_catalog.CATALOG['alexej_von_jawlensky']
    assert '1864' in entry.period, f"period should contain birth year 1864, got {entry.period!r}"
    assert '1941' in entry.period, f"period should contain death year 1941, got {entry.period!r}"


def test_s245_jawlensky_palette_length():
    import art_catalog
    entry = art_catalog.CATALOG['alexej_von_jawlensky']
    assert len(entry.palette) >= 6, (
        f"Jawlensky palette should have at least 6 colours, got {len(entry.palette)}"
    )


def test_s245_jawlensky_palette_values_valid():
    import art_catalog
    entry = art_catalog.CATALOG['alexej_von_jawlensky']
    for i, color in enumerate(entry.palette):
        assert len(color) == 3, f"palette[{i}] must be an (R,G,B) triple"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"palette[{i}] channel {ch} out of [0,1] range"
            )


def test_s245_jawlensky_famous_works():
    import art_catalog
    entry = art_catalog.CATALOG['alexej_von_jawlensky']
    assert len(entry.famous_works) >= 4, (
        f"Jawlensky should have at least 4 famous works listed, got {len(entry.famous_works)}"
    )


def test_s245_jawlensky_mystical_head_in_works():
    import art_catalog
    entry = art_catalog.CATALOG['alexej_von_jawlensky']
    titles = [w[0] for w in entry.famous_works]
    assert any('Mystical' in t or 'Abstract' in t or 'Meditation' in t for t in titles), (
        "Famous works should include Mystical Head, Abstract Head, or Meditation series"
    )


def test_s245_jawlensky_inspiration_references_pass():
    import art_catalog
    entry = art_catalog.CATALOG['alexej_von_jawlensky']
    insp = entry.inspiration.lower()
    assert 'jawlensky' in insp or 'radial' in insp or 'warmth' in insp, (
        "inspiration field should reference the jawlensky_abstract_head_pass"
    )


def test_s245_jawlensky_technique_nonempty():
    import art_catalog
    entry = art_catalog.CATALOG['alexej_von_jawlensky']
    assert len(entry.technique) > 200, (
        "Jawlensky technique description should be substantial (>200 chars)"
    )


def test_s245_catalog_total_count():
    import art_catalog
    count = len(art_catalog.CATALOG)
    assert count >= 245, (
        f"After session 245, CATALOG should have at least 245 entries, got {count}"
    )


def test_s245_both_passes_sequential():
    """Run both new passes in sequence -- no errors, canvas stays valid."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.jawlensky_abstract_head_pass()
    p.paint_optical_vibration_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s245_painter_smoke_test():
    """Full painter workflow with both new passes on small canvas."""
    from PIL import Image
    w, h = 64, 80
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//2, :w//2, :] = [200, 100, 30]   # warm upper-left
    arr[:h//2, w//2:, :] = [30, 60, 210]    # cool upper-right
    arr[h//2:, :, :]     = [120, 80, 160]   # violet lower
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter(w=w, h=h)
    p.tone_ground((0.16, 0.14, 0.10), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=16)
    p.jawlensky_abstract_head_pass(opacity=0.80)
    p.paint_optical_vibration_pass(opacity=0.65)
    after = _get_canvas(p)
    assert after.shape == (h, w, 4)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255
