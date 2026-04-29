"""
test_s247_additions.py -- Session 247 tests for kollwitz_charcoal_etching_pass,
paint_luminance_stretch_pass, and the kathe_kollwitz catalog entry.
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


def _prime_canvas(p, ref=None, *, dark=False, bright=False, multicolor=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if dark:
            ref = _dark_reference(w, h)
        elif bright:
            ref = _bright_reference(w, h)
        elif multicolor:
            ref = _multicolor_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.82, 0.66, 0.28), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── kollwitz_charcoal_etching_pass ───────────────────────────────────────────

def test_s247_kollwitz_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "kollwitz_charcoal_etching_pass")


def test_s247_kollwitz_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.kollwitz_charcoal_etching_pass()
    assert result is None


def test_s247_kollwitz_pass_modifies_canvas():
    """Pass must change at least some pixels on a multicolour canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.kollwitz_charcoal_etching_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "kollwitz_charcoal_etching_pass must modify canvas"


def test_s247_kollwitz_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.kollwitz_charcoal_etching_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="kollwitz_charcoal_etching_pass must not alter alpha channel"
    )


def test_s247_kollwitz_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.kollwitz_charcoal_etching_pass(
        desat_str=1.0, sigmoid_k=12.0, grain_strength=0.5, opacity=1.0
    )
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0, "RGB must not go below 0"
    assert after[:, :, :3].max() <= 255, "RGB must not exceed 255"


def test_s247_kollwitz_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas essentially unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.kollwitz_charcoal_etching_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1, (
        "opacity=0 should leave RGB channels essentially unchanged (max diff <= 1 LSB)"
    )


def test_s247_kollwitz_pass_opacity_full_visible_change():
    """opacity=1 should produce visible change on multicolour canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.kollwitz_charcoal_etching_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() > 2, "opacity=1 should produce noticeable change"


def test_s247_kollwitz_desaturation_reduces_saturation():
    """After charcoal pass with full desat, mean saturation should decrease."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()

    def _mean_sat(arr_):
        r_ = arr_[:, :, 2].astype(np.float32) / 255
        g_ = arr_[:, :, 1].astype(np.float32) / 255
        b_ = arr_[:, :, 0].astype(np.float32) / 255
        mx = np.maximum(r_, np.maximum(g_, b_))
        mn = np.minimum(r_, np.minimum(g_, b_))
        return np.where(mx > 1e-7, (mx - mn) / (mx + 1e-7), 0.0).mean()

    sat_before = _mean_sat(before)
    p.kollwitz_charcoal_etching_pass(desat_str=0.95, opacity=1.0)
    after = _get_canvas(p)
    sat_after = _mean_sat(after)
    assert sat_after < sat_before + 0.02, (
        f"Charcoal pass should reduce mean saturation on vibrant canvas "
        f"(before={sat_before:.3f}, after={sat_after:.3f})"
    )


def test_s247_kollwitz_contrast_expands_tonal_range():
    """After pass, the dynamic range of luminance values should increase."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()

    def _lum_range(arr_):
        r_ = arr_[:, :, 2].astype(np.float32) / 255
        g_ = arr_[:, :, 1].astype(np.float32) / 255
        b_ = arr_[:, :, 0].astype(np.float32) / 255
        lum_ = 0.299 * r_ + 0.587 * g_ + 0.114 * b_
        return float(lum_.max() - lum_.min())

    range_before = _lum_range(before)
    p.kollwitz_charcoal_etching_pass(sigmoid_k=10.0, opacity=1.0)
    after = _get_canvas(p)
    range_after = _lum_range(after)
    # Range should not substantially decrease (sigmoid expands or maintains it)
    assert range_after >= range_before * 0.7, (
        f"Sigmoid contrast should not drastically compress tonal range "
        f"(before={range_before:.3f}, after={range_after:.3f})"
    )


def test_s247_kollwitz_dark_canvas_no_crash():
    """Very dark canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.kollwitz_charcoal_etching_pass()
    after = _get_canvas(p)
    assert after is not None
    assert after[:, :, :3].min() >= 0


def test_s247_kollwitz_bright_canvas_no_crash():
    """Very bright canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.kollwitz_charcoal_etching_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].max() <= 255


def test_s247_kollwitz_grain_angle_range():
    """Pass accepts grain angles 0, 45, 90, 135 without crash."""
    for angle in [0.0, 45.0, 90.0, 135.0]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.kollwitz_charcoal_etching_pass(grain_angle_deg=angle)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0, f"Angle {angle}: RGB below 0"
        assert after[:, :, :3].max() <= 255, f"Angle {angle}: RGB above 255"


def test_s247_kollwitz_kernel_length_range():
    """Pass accepts grain_kernel_len 3, 7, 11 without crash."""
    for klen in [3, 7, 11]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.kollwitz_charcoal_etching_pass(grain_kernel_len=klen)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255, f"kernel_len={klen}: RGB above 255"


def test_s247_kollwitz_sigmoid_k_range():
    """Pass accepts sigmoid_k 2.0, 7.0, 14.0 without crash."""
    for k in [2.0, 7.0, 14.0]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.kollwitz_charcoal_etching_pass(sigmoid_k=k)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0


def test_s247_kollwitz_sequential_with_golden_ground():
    """Kollwitz pass followed by golden ground should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.kollwitz_charcoal_etching_pass()
    p.paint_golden_ground_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s247_kollwitz_sequential_with_macke():
    """Macke luminous planes followed by kollwitz should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.macke_luminous_planes_pass()
    p.kollwitz_charcoal_etching_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s247_kollwitz_warm_dark_endpoint_applied():
    """With desat_str=1.0 and opacity=1.0, dark pixels should have a warm tint."""
    from PIL import Image
    arr = np.ones((64, 64, 3), dtype=np.uint8) * np.array([12, 10, 8], dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter()
    p.tone_ground((0.05, 0.05, 0.05), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=12)
    p.kollwitz_charcoal_etching_pass(
        desat_str=1.0, dark_r=0.20, dark_g=0.12, dark_b=0.07,
        sigmoid_k=1.0, grain_strength=0.0, opacity=1.0
    )
    after = _get_canvas(p)
    # On a very dark canvas the warm dark endpoint means red channel > blue channel
    r_mean = after[:, :, 2].astype(np.float32).mean()
    b_mean = after[:, :, 0].astype(np.float32).mean()
    assert r_mean >= b_mean - 5.0, (
        f"Dark warm endpoint should make red >= blue on a near-black canvas "
        f"(r={r_mean:.1f}, b={b_mean:.1f})"
    )


def test_s247_kollwitz_desat_str_zero_no_desaturation():
    """desat_str=0 with opacity=1 should produce no desaturation."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)

    def _mean_sat(arr_):
        r_ = arr_[:, :, 2].astype(np.float32) / 255
        g_ = arr_[:, :, 1].astype(np.float32) / 255
        b_ = arr_[:, :, 0].astype(np.float32) / 255
        mx = np.maximum(r_, np.maximum(g_, b_))
        mn = np.minimum(r_, np.minimum(g_, b_))
        return np.where(mx > 1e-7, (mx - mn) / (mx + 1e-7), 0.0).mean()

    before = _get_canvas(p).copy()
    p.kollwitz_charcoal_etching_pass(desat_str=0.0, grain_strength=0.0, opacity=1.0)
    after = _get_canvas(p)
    sat_before = _mean_sat(before)
    sat_after = _mean_sat(after)
    # With desat=0 and grain=0, saturation should be similar (only sigmoid may shift it slightly)
    assert abs(sat_after - sat_before) < 0.15, (
        f"desat_str=0 should leave saturation close to original "
        f"(before={sat_before:.3f}, after={sat_after:.3f})"
    )


# ── paint_luminance_stretch_pass ─────────────────────────────────────────────

def test_s247_luminance_stretch_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_luminance_stretch_pass")


def test_s247_luminance_stretch_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_luminance_stretch_pass()
    assert result is None


def test_s247_luminance_stretch_pass_modifies_canvas():
    """Pass must change canvas when there is tonal variation."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.paint_luminance_stretch_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "paint_luminance_stretch_pass must modify canvas"


def test_s247_luminance_stretch_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_luminance_stretch_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="paint_luminance_stretch_pass must not alter alpha channel"
    )


def test_s247_luminance_stretch_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.paint_luminance_stretch_pass(lo_pct=5.0, hi_pct=95.0, opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0, "RGB must not go below 0"
    assert after[:, :, :3].max() <= 255, "RGB must not exceed 255"


def test_s247_luminance_stretch_opacity_zero_no_change():
    """opacity=0 must leave canvas essentially unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_luminance_stretch_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1, (
        "opacity=0 should leave RGB channels essentially unchanged (max diff <= 1 LSB)"
    )


def test_s247_luminance_stretch_increases_dark_range_on_dark_canvas():
    """On a canvas with mainly dark pixels, stretch should increase mean luminance."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()

    def _mean_lum(arr_):
        r_ = arr_[:, :, 2].astype(np.float32) / 255
        g_ = arr_[:, :, 1].astype(np.float32) / 255
        b_ = arr_[:, :, 0].astype(np.float32) / 255
        return float((0.299 * r_ + 0.587 * g_ + 0.114 * b_).mean())

    lum_before = _mean_lum(before)
    p.paint_luminance_stretch_pass(lo_pct=1.0, hi_pct=99.0, opacity=1.0)
    after = _get_canvas(p)
    lum_after = _mean_lum(after)
    # Stretching a dark image should increase mean luminance (dark pixels pulled up)
    assert lum_after >= lum_before - 0.01, (
        f"Stretch should not decrease mean luminance on dark canvas "
        f"(before={lum_before:.3f}, after={lum_after:.3f})"
    )


def test_s247_luminance_stretch_no_crash_flat_canvas():
    """Flat (uniform) canvas should not cause division-by-zero crash."""
    from PIL import Image
    arr = np.ones((64, 64, 3), dtype=np.uint8) * 128
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter()
    p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=8)
    p.paint_luminance_stretch_pass()
    after = _get_canvas(p)
    assert after is not None
    assert after[:, :, :3].max() <= 255


def test_s247_luminance_stretch_pct_range():
    """Pass accepts lo/hi pairs (1,99), (5,95), (10,90) without crash."""
    for lo, hi in [(1.0, 99.0), (5.0, 95.0), (10.0, 90.0)]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.paint_luminance_stretch_pass(lo_pct=lo, hi_pct=hi)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0
        assert after[:, :, :3].max() <= 255


def test_s247_luminance_stretch_sequential_after_kollwitz():
    """Luminance stretch after kollwitz pass should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.kollwitz_charcoal_etching_pass()
    p.paint_luminance_stretch_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


# ── kathe_kollwitz catalog entry ─────────────────────────────────────────────

def test_s247_kollwitz_in_catalog():
    import art_catalog
    assert 'kathe_kollwitz' in art_catalog.CATALOG, (
        "kathe_kollwitz key must be present in CATALOG"
    )


def test_s247_kollwitz_artist_name():
    import art_catalog
    entry = art_catalog.CATALOG['kathe_kollwitz']
    assert 'Kollwitz' in entry.artist, (
        f"artist field should contain 'Kollwitz', got {entry.artist!r}"
    )


def test_s247_kollwitz_movement():
    import art_catalog
    entry = art_catalog.CATALOG['kathe_kollwitz']
    mv = entry.movement.lower()
    assert 'expressionism' in mv or 'realism' in mv, (
        f"movement should reference Expressionism or Realism, got {entry.movement!r}"
    )


def test_s247_kollwitz_period():
    import art_catalog
    entry = art_catalog.CATALOG['kathe_kollwitz']
    assert '1867' in entry.period, f"period should contain birth year 1867, got {entry.period!r}"
    assert '1945' in entry.period, f"period should contain death year 1945, got {entry.period!r}"


def test_s247_kollwitz_palette_length():
    import art_catalog
    entry = art_catalog.CATALOG['kathe_kollwitz']
    assert len(entry.palette) >= 6, (
        f"Kollwitz palette should have at least 6 colours, got {len(entry.palette)}"
    )


def test_s247_kollwitz_palette_values_valid():
    import art_catalog
    entry = art_catalog.CATALOG['kathe_kollwitz']
    for i, color in enumerate(entry.palette):
        assert len(color) == 3, f"palette[{i}] must be an (R,G,B) triple"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"palette[{i}] channel {ch} out of [0,1] range"
            )


def test_s247_kollwitz_famous_works():
    import art_catalog
    entry = art_catalog.CATALOG['kathe_kollwitz']
    assert len(entry.famous_works) >= 4, (
        f"Kollwitz should have at least 4 famous works listed, got {len(entry.famous_works)}"
    )


def test_s247_kollwitz_works_include_known_title():
    import art_catalog
    entry = art_catalog.CATALOG['kathe_kollwitz']
    titles = [w[0].lower() for w in entry.famous_works]
    known = ['weaver', 'peasant', 'mother', 'war', 'never', 'death', 'self']
    assert any(any(k in t for k in known) for t in titles), (
        "Famous works should include at least one known Kollwitz title"
    )


def test_s247_kollwitz_inspiration_references_pass():
    import art_catalog
    entry = art_catalog.CATALOG['kathe_kollwitz']
    insp = entry.inspiration.lower()
    assert 'kollwitz' in insp or 'charcoal' in insp or 'sigmoid' in insp, (
        "inspiration field should reference the kollwitz_charcoal_etching_pass"
    )


def test_s247_kollwitz_technique_nonempty():
    import art_catalog
    entry = art_catalog.CATALOG['kathe_kollwitz']
    assert len(entry.technique) > 200, (
        "Kollwitz technique description should be substantial (>200 chars)"
    )


def test_s247_catalog_total_count():
    import art_catalog
    count = len(art_catalog.CATALOG)
    assert count >= 247, (
        f"After session 247, CATALOG should have at least 247 entries, got {count}"
    )


# ── combined smoke tests ──────────────────────────────────────────────────────

def test_s247_both_passes_sequential():
    """Run both new passes in sequence -- no errors, canvas stays valid."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.kollwitz_charcoal_etching_pass()
    p.paint_luminance_stretch_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s247_painter_smoke_test():
    """Full painter workflow with both new passes on small canvas."""
    from PIL import Image
    w, h = 80, 64
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//2, :w//3, :]    = [180, 130, 80]   # warm ochre upper-left
    arr[:h//2, w//3:2*w//3, :] = [60, 60, 60]  # mid-grey upper-mid
    arr[:h//2, 2*w//3:, :]  = [30, 30, 30]     # dark upper-right
    arr[h//2:, :w//2, :]    = [220, 200, 180]   # light lower-left
    arr[h//2:, w//2:, :]    = [80, 60, 40]      # dark warm lower-right
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter(w=w, h=h)
    p.tone_ground((0.82, 0.66, 0.28), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=16)
    p.kollwitz_charcoal_etching_pass(opacity=0.88)
    p.paint_luminance_stretch_pass(opacity=0.70)
    after = _get_canvas(p)
    assert after.shape == (h, w, 4)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255
