"""
test_s259_additions.py -- Session 259 tests for rysselberghe_chromatic_dot_field_pass,
paint_atmospheric_recession_pass, and the theo_van_rysselberghe catalog entry.
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


def _saturated_reference(w=64, h=64):
    """High-saturation multi-hue reference for chromatic boost tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    third = w // 3
    arr[:, :third, :] = [220, 40, 20]          # saturated red
    arr[:, third:2*third, :] = [20, 180, 40]   # saturated green
    arr[:, 2*third:, :] = [20, 60, 210]         # saturated blue
    return Image.fromarray(arr, "RGB")


def _grey_reference(w=64, h=64):
    """Near-grey reference -- should show minimal spectral boost."""
    from PIL import Image
    arr = np.full((h, w, 3), 128, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _gradient_reference(w=64, h=64):
    """Vertical gradient from warm to cool for recession tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//2, :] = [180, 140, 80]     # warm foreground (bottom half)
    arr[h//2:, :] = [120, 130, 160]    # cooler background (top half)
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, saturated=False, grey=False, gradient=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if saturated:
            ref = _saturated_reference(w, h)
        elif grey:
            ref = _grey_reference(w, h)
        elif gradient:
            ref = _gradient_reference(w, h)
        else:
            ref = _saturated_reference(w, h)
    p.tone_ground((0.92, 0.90, 0.82), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── rysselberghe_chromatic_dot_field_pass ─────────────────────────────────────

def test_s259_rysselberghe_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "rysselberghe_chromatic_dot_field_pass")


def test_s259_rysselberghe_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    result = p.rysselberghe_chromatic_dot_field_pass()
    assert result is None


def test_s259_rysselberghe_pass_modifies_canvas():
    """Pass must change at least some pixels on a non-trivial canvas."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    before = _get_canvas(p).copy()
    p.rysselberghe_chromatic_dot_field_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after rysselberghe_chromatic_dot_field_pass"


def test_s259_rysselberghe_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p)
    p.rysselberghe_chromatic_dot_field_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after rysselberghe_chromatic_dot_field_pass"
    )


def test_s259_rysselberghe_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    before = _get_canvas(p).copy()
    p.rysselberghe_chromatic_dot_field_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s259_rysselberghe_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    p.rysselberghe_chromatic_dot_field_pass(
        spectral_boost=1.0, luminosity_gain=0.5, dot_amplitude=0.3, opacity=1.0
    )
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after rysselberghe_chromatic_dot_field_pass"
    )


def test_s259_rysselberghe_spectral_boost_increases_saturation():
    """High spectral_boost on saturated input should increase or maintain mean saturation."""
    p_base = _make_small_painter()
    _prime_canvas(p_base, saturated=True)
    before_arr = _get_canvas(p_base).copy().astype(float) / 255.0
    b0 = before_arr[:, :, 0]
    g0 = before_arr[:, :, 1]
    r0 = before_arr[:, :, 2]
    cmax_b = np.maximum(np.maximum(r0, g0), b0)
    cmin_b = np.minimum(np.minimum(r0, g0), b0)
    sat_before = np.where(cmax_b > 1e-6, (cmax_b - cmin_b) / (cmax_b + 1e-8), 0.0)

    p_high = _make_small_painter()
    _prime_canvas(p_high, saturated=True)
    p_high.rysselberghe_chromatic_dot_field_pass(
        spectral_boost=0.8,
        luminosity_gain=0.0,
        dot_amplitude=0.0,
        opacity=1.0,
    )
    after_arr = _get_canvas(p_high).astype(float) / 255.0
    b1 = after_arr[:, :, 0]
    g1 = after_arr[:, :, 1]
    r1 = after_arr[:, :, 2]
    cmax_a = np.maximum(np.maximum(r1, g1), b1)
    cmin_a = np.minimum(np.minimum(r1, g1), b1)
    sat_after = np.where(cmax_a > 1e-6, (cmax_a - cmin_a) / (cmax_a + 1e-8), 0.0)

    assert sat_after.mean() >= sat_before.mean() - 0.01, (
        f"High spectral_boost should not decrease mean saturation; "
        f"before={sat_before.mean():.4f}, after={sat_after.mean():.4f}"
    )


def test_s259_rysselberghe_luminosity_lifts_bright_saturated_pixels():
    """luminosity_gain > 0 should brighten high-saturation pixels."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    before = _get_canvas(p).copy().astype(float)
    lum_before = 0.299 * before[:, :, 2] + 0.587 * before[:, :, 1] + 0.114 * before[:, :, 0]

    p2 = _make_small_painter()
    _prime_canvas(p2, saturated=True)
    p2.rysselberghe_chromatic_dot_field_pass(
        spectral_boost=0.0,
        luminosity_gain=0.5,
        luminosity_threshold=0.0,
        dot_amplitude=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p2).astype(float)
    lum_after = 0.299 * after[:, :, 2] + 0.587 * after[:, :, 1] + 0.114 * after[:, :, 0]
    assert lum_after.mean() >= lum_before.mean(), (
        "luminosity_gain=0.5 should not decrease mean luminance"
    )


def test_s259_rysselberghe_dot_field_changes_texture():
    """Dot field stamp (dot_amplitude > 0) should introduce spatial variation."""
    p_nodot = _make_small_painter()
    p_nodot.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    out_nodot = _get_canvas(p_nodot).astype(float) / 255.0
    lum_nodot = 0.299 * out_nodot[:, :, 2] + 0.587 * out_nodot[:, :, 1] + 0.114 * out_nodot[:, :, 0]
    var_before = float(np.var(lum_nodot))

    p_dot = _make_small_painter()
    p_dot.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    p_dot.rysselberghe_chromatic_dot_field_pass(
        spectral_boost=0.0,
        luminosity_gain=0.0,
        dot_spacing=6,
        dot_amplitude=0.12,
        dot_sigma=1.5,
        opacity=1.0,
    )
    out_dot = _get_canvas(p_dot).astype(float) / 255.0
    lum_dot = 0.299 * out_dot[:, :, 2] + 0.587 * out_dot[:, :, 1] + 0.114 * out_dot[:, :, 0]
    var_after = float(np.var(lum_dot))

    assert var_after > var_before, (
        f"Dot field should increase spatial luminance variance; "
        f"before={var_before:.6f}, after={var_after:.6f}"
    )


def test_s259_rysselberghe_higher_opacity_more_change():
    """Higher opacity should produce at least as much change as lower opacity."""
    ref = _saturated_reference(64, 64)

    def _run(op):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        before = _get_canvas(p).copy()
        p.rysselberghe_chromatic_dot_field_pass(opacity=op)
        after = _get_canvas(p)
        return int(np.abs(before.astype(int) - after.astype(int)).sum())

    assert _run(0.8) >= _run(0.2), "Higher opacity should produce more change"


# ── paint_atmospheric_recession_pass ─────────────────────────────────────────

def test_s259_recession_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_atmospheric_recession_pass")


def test_s259_recession_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, gradient=True)
    result = p.paint_atmospheric_recession_pass()
    assert result is None


def test_s259_recession_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p, gradient=True)
    before = _get_canvas(p).copy()
    p.paint_atmospheric_recession_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_atmospheric_recession_pass"


def test_s259_recession_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p)
    p.paint_atmospheric_recession_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after paint_atmospheric_recession_pass"
    )


def test_s259_recession_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, gradient=True)
    before = _get_canvas(p).copy()
    p.paint_atmospheric_recession_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s259_recession_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    p.paint_atmospheric_recession_pass(
        haze_lift=0.5, desaturation=1.0, cool_shift_b=0.5, opacity=1.0
    )
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after paint_atmospheric_recession_pass"
    )


def test_s259_recession_top_brightens_top_rows():
    """recession_direction='top' should lift luminance at top rows more than bottom."""
    from PIL import Image
    arr = np.full((64, 64, 3), 100, dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy().astype(float) / 255.0
    lum_before_top = (0.299 * before[:16, :, 2] + 0.587 * before[:16, :, 1]
                      + 0.114 * before[:16, :, 0]).mean()
    lum_before_bot = (0.299 * before[48:, :, 2] + 0.587 * before[48:, :, 1]
                      + 0.114 * before[48:, :, 0]).mean()

    p.paint_atmospheric_recession_pass(
        recession_direction="top",
        haze_lift=0.20,
        desaturation=0.0,
        cool_shift_r=0.0,
        cool_shift_g=0.0,
        cool_shift_b=0.0,
        near_fraction=0.0,
        far_fraction=1.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    lum_after_top = (0.299 * after[:16, :, 2] + 0.587 * after[:16, :, 1]
                     + 0.114 * after[:16, :, 0]).mean()
    lum_after_bot = (0.299 * after[48:, :, 2] + 0.587 * after[48:, :, 1]
                     + 0.114 * after[48:, :, 0]).mean()

    lift_top = lum_after_top - lum_before_top
    lift_bot = lum_after_bot - lum_before_bot
    assert lift_top > lift_bot, (
        f"Top-direction should lift top rows more than bottom rows; "
        f"top_lift={lift_top:.4f}, bot_lift={lift_bot:.4f}"
    )


def test_s259_recession_desaturation_reduces_far_saturation():
    """High desaturation should reduce saturation more in the far region."""
    from PIL import Image
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:] = [200, 30, 30]   # saturated red everywhere
    ref = Image.fromarray(arr, "RGB")

    def _get_sat_band(direction, rows_slice):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        p.paint_atmospheric_recession_pass(
            recession_direction=direction,
            haze_lift=0.0,
            desaturation=0.80,
            cool_shift_r=0.0,
            cool_shift_g=0.0,
            cool_shift_b=0.0,
            near_fraction=0.0,
            far_fraction=1.0,
            opacity=1.0,
        )
        after = _get_canvas(p).astype(float) / 255.0
        r = after[rows_slice, :, 2]
        g = after[rows_slice, :, 1]
        b = after[rows_slice, :, 0]
        cmax = np.maximum(np.maximum(r, g), b)
        cmin = np.minimum(np.minimum(r, g), b)
        return float(np.where(cmax > 1e-6, (cmax - cmin) / (cmax + 1e-8), 0.0).mean())

    sat_near = _get_sat_band("top", slice(48, 64))   # bottom = near for top recession
    sat_far  = _get_sat_band("top", slice(0, 16))    # top = far for top recession
    assert sat_far < sat_near, (
        f"Far region should have less saturation than near; far={sat_far:.4f}, near={sat_near:.4f}"
    )


def test_s259_recession_cool_shift_increases_blue_far():
    """Cool shift should increase blue channel more in the far region."""
    from PIL import Image
    arr = np.full((64, 64, 3), 150, dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy().astype(float)

    p.paint_atmospheric_recession_pass(
        recession_direction="top",
        haze_lift=0.0,
        desaturation=0.0,
        cool_shift_r=0.0,
        cool_shift_g=0.0,
        cool_shift_b=0.30,
        near_fraction=0.0,
        far_fraction=1.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float)

    # Top rows (far) should gain more blue than bottom rows (near)
    b_gain_top = (after[:16, :, 0] - before[:16, :, 0]).mean()
    b_gain_bot = (after[48:, :, 0] - before[48:, :, 0]).mean()
    assert b_gain_top >= b_gain_bot, (
        f"Top (far) rows should gain more blue channel; top={b_gain_top:.2f}, bot={b_gain_bot:.2f}"
    )


def test_s259_recession_directions_differ():
    """Top and bottom recession directions should produce different results."""
    ref = _gradient_reference(64, 64)

    def _run(direction):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        p.paint_atmospheric_recession_pass(
            recession_direction=direction,
            haze_lift=0.15,
            desaturation=0.30,
            opacity=0.8,
        )
        return _get_canvas(p).astype(int)

    top_out = _run("top")
    bot_out = _run("bottom")
    assert not np.array_equal(top_out, bot_out), (
        "Top and bottom recession directions should produce different outputs"
    )


# ── theo_van_rysselberghe catalog tests ───────────────────────────────────────

def test_s259_catalog_rysselberghe_present():
    from art_catalog import CATALOG
    assert "theo_van_rysselberghe" in CATALOG, (
        "theo_van_rysselberghe not found in CATALOG"
    )


def test_s259_catalog_rysselberghe_fields():
    from art_catalog import CATALOG
    s = CATALOG["theo_van_rysselberghe"]
    assert "Rysselberghe" in s.artist
    assert s.nationality.startswith("Belgian")
    assert len(s.palette) >= 6
    assert len(s.famous_works) >= 5


def test_s259_catalog_rysselberghe_inspiration():
    """Inspiration must reference rysselberghe_chromatic_dot_field_pass and 170th mode."""
    from art_catalog import CATALOG
    s = CATALOG["theo_van_rysselberghe"]
    assert "rysselberghe_chromatic_dot_field_pass" in s.inspiration, (
        "rysselberghe_chromatic_dot_field_pass not found in inspiration"
    )
    assert "170" in s.inspiration, (
        "170th mode not referenced in inspiration"
    )


def test_s259_catalog_rysselberghe_bright_palette():
    """Rysselberghe's palette should include high-luminance Mediterranean tones."""
    from art_catalog import CATALOG
    s = CATALOG["theo_van_rysselberghe"]
    lums = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in s.palette]
    assert max(lums) > 0.70, (
        f"Palette should include a bright Mediterranean tone; max_lum={max(lums):.3f}"
    )


def test_s259_catalog_count_increased():
    """CATALOG count must be 256 (new artist added this session)."""
    from art_catalog import CATALOG
    assert len(CATALOG) == 256, f"Expected 256 catalog entries, got {len(CATALOG)}"


def test_s259_catalog_get_style_rysselberghe():
    """get_style() must retrieve van Rysselberghe by key."""
    from art_catalog import get_style
    s = get_style("theo_van_rysselberghe")
    assert "Rysselberghe" in s.artist


# ── Integration: run both new passes together ─────────────────────────────────

def test_s259_full_pipeline_rysselberghe_and_recession():
    """Run both new passes in sequence; canvas should be modified and valid."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    before = _get_canvas(p).copy()

    p.rysselberghe_chromatic_dot_field_pass(opacity=0.72)
    p.paint_atmospheric_recession_pass(opacity=0.65)

    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Pipeline should modify canvas"
    assert after.min() >= 0 and after.max() <= 255, "Values must stay in [0, 255]"
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), "Alpha must be preserved"
