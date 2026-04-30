"""
test_s258_additions.py -- Session 258 tests for morandi_dusty_vessel_pass,
paint_granulation_pass, and the giorgio_morandi catalog inspiration update.
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


def _gradient_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [160, 80, 40]
    arr[:, w // 2:, :] = [40, 100, 160]
    return Image.fromarray(arr, "RGB")


def _midtone_reference(w=64, h=64):
    """Moderately saturated mid-tones -- good for tonal compression tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 3, :] = [210, 195, 160]         # light area
    arr[h // 3:2 * h // 3, :] = [130, 115, 90]  # mid area
    arr[2 * h // 3:, :] = [55, 45, 35]          # dark area
    return Image.fromarray(arr, "RGB")


def _saturated_reference(w=64, h=64):
    """High-saturation reference for dust/desaturation tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :] = [220, 40, 20]    # saturated red
    arr[h // 2:, :] = [20, 60, 210]    # saturated blue
    return Image.fromarray(arr, "RGB")


def _bright_dark_reference(w=64, h=64):
    """Half bright, half dark -- for edge-frequency granulation tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [210, 195, 175]   # bright half
    arr[:, w // 2:, :] = [45, 38, 30]       # dark half
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, saturated=False, midtone=False, bright_dark=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if saturated:
            ref = _saturated_reference(w, h)
        elif midtone:
            ref = _midtone_reference(w, h)
        elif bright_dark:
            ref = _bright_dark_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.82, 0.79, 0.70), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── morandi_dusty_vessel_pass ─────────────────────────────────────────────────

def test_s258_morandi_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "morandi_dusty_vessel_pass")


def test_s258_morandi_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    result = p.morandi_dusty_vessel_pass()
    assert result is None


def test_s258_morandi_pass_modifies_canvas():
    """Pass must change at least some pixels on a non-trivial canvas."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    before = _get_canvas(p).copy()
    p.morandi_dusty_vessel_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after morandi_dusty_vessel_pass"


def test_s258_morandi_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p)
    p.morandi_dusty_vessel_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after morandi_dusty_vessel_pass"
    )


def test_s258_morandi_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    before = _get_canvas(p).copy()
    p.morandi_dusty_vessel_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s258_morandi_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    p.morandi_dusty_vessel_pass(opacity=1.0, dust_veil=1.0, compress_strength=0.8)
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after morandi_dusty_vessel_pass"
    )


def test_s258_morandi_dust_veil_reduces_saturation():
    """High dust_veil must reduce colour saturation in dark pixels."""
    from PIL import Image
    # Ensure low-luminance saturated colors exist
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:32, :] = [180, 20, 20]   # saturated dark red
    arr[32:, :] = [20, 20, 180]   # saturated dark blue
    ref = Image.fromarray(arr, "RGB")

    p_high = _make_small_painter()
    _prime_canvas(p_high, ref=ref)
    # Record saturation before
    before_h = _get_canvas(p_high).copy().astype(float) / 255.0
    b0 = before_h[:, :, 0]
    g0 = before_h[:, :, 1]
    r0 = before_h[:, :, 2]
    cmax = np.maximum(np.maximum(r0, g0), b0)
    cmin = np.minimum(np.minimum(r0, g0), b0)
    sat_before = np.where(cmax > 1e-6, (cmax - cmin) / (cmax + 1e-8), 0.0)

    p_high.morandi_dusty_vessel_pass(dust_veil=1.0, compress_strength=0.0,
                                     reveal_strength=0.0, opacity=1.0)
    after_h = _get_canvas(p_high).astype(float) / 255.0
    b1 = after_h[:, :, 0]
    g1 = after_h[:, :, 1]
    r1 = after_h[:, :, 2]
    cmax1 = np.maximum(np.maximum(r1, g1), b1)
    cmin1 = np.minimum(np.minimum(r1, g1), b1)
    sat_after = np.where(cmax1 > 1e-6, (cmax1 - cmin1) / (cmax1 + 1e-8), 0.0)

    assert sat_after.mean() <= sat_before.mean(), (
        "dust_veil=1.0 should reduce mean saturation"
    )


def test_s258_morandi_tonal_compression_narrows_range():
    """High compress_strength should reduce the luminance range (max-min)."""
    p_none = _make_small_painter()
    _prime_canvas(p_none, ref=_midtone_reference(64, 64))
    p_none.morandi_dusty_vessel_pass(compress_strength=0.0, dust_veil=0.0,
                                     reveal_strength=0.0, opacity=1.0)
    out_none = _get_canvas(p_none).astype(float) / 255.0
    lum_none = 0.299 * out_none[:, :, 2] + 0.587 * out_none[:, :, 1] + 0.114 * out_none[:, :, 0]

    p_high = _make_small_painter()
    _prime_canvas(p_high, ref=_midtone_reference(64, 64))
    p_high.morandi_dusty_vessel_pass(compress_strength=0.7, dust_veil=0.0,
                                     reveal_strength=0.0, opacity=1.0)
    out_high = _get_canvas(p_high).astype(float) / 255.0
    lum_high = 0.299 * out_high[:, :, 2] + 0.587 * out_high[:, :, 1] + 0.114 * out_high[:, :, 0]

    range_none = float(lum_none.max() - lum_none.min())
    range_high = float(lum_high.max() - lum_high.min())
    assert range_high < range_none, (
        f"compress_strength=0.7 should narrow tonal range; "
        f"no-compress={range_none:.4f}, high-compress={range_high:.4f}"
    )


def test_s258_morandi_ochre_reveal_warms_highlights():
    """reveal_strength > 0 should push brightest pixels toward warm ochre (R up)."""
    p = _make_small_painter()
    _prime_canvas(p, ref=_midtone_reference(64, 64))
    before = _get_canvas(p).copy()

    p.morandi_dusty_vessel_pass(
        dust_veil=0.0,
        compress_strength=0.0,
        reveal_threshold=0.50,   # low threshold to catch many pixels
        reveal_strength=0.6,
        ochre_r=0.90,            # strong warm
        ochre_g=0.75,
        ochre_b=0.30,            # low blue = warm
        opacity=1.0,
    )
    after = _get_canvas(p)
    # In bright-ish pixels, R should rise and B should fall
    bright_rows = slice(0, 64 // 3)   # top third = lightest in reference
    r_before = before[bright_rows, :, 2].astype(float)
    r_after  = after[bright_rows, :, 2].astype(float)
    b_before = before[bright_rows, :, 0].astype(float)
    b_after  = after[bright_rows, :, 0].astype(float)
    assert r_after.mean() >= r_before.mean() - 1.0, (
        "Ochre reveal should not decrease R in bright region"
    )
    assert b_after.mean() <= b_before.mean() + 1.0, (
        "Ochre reveal should not increase B in bright region (ochre is warm)"
    )


def test_s258_morandi_higher_opacity_more_change():
    """Higher opacity should produce at least as much change as lower opacity."""
    ref = _saturated_reference(64, 64)

    def _run(op):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        before = _get_canvas(p).copy()
        p.morandi_dusty_vessel_pass(opacity=op)
        after = _get_canvas(p)
        return int(np.abs(before.astype(int) - after.astype(int)).sum())

    assert _run(0.8) >= _run(0.2), "Higher opacity should produce more change"


# ── paint_granulation_pass ────────────────────────────────────────────────────

def test_s258_granulation_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_granulation_pass")


def test_s258_granulation_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, bright_dark=True)
    result = p.paint_granulation_pass()
    assert result is None


def test_s258_granulation_pass_modifies_canvas():
    """Pass must change at least some pixels on a textured canvas."""
    p = _make_small_painter()
    _prime_canvas(p, bright_dark=True)
    before = _get_canvas(p).copy()
    p.paint_granulation_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_granulation_pass"


def test_s258_granulation_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p)
    p.paint_granulation_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after paint_granulation_pass"
    )


def test_s258_granulation_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, bright_dark=True)
    before = _get_canvas(p).copy()
    p.paint_granulation_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s258_granulation_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, bright_dark=True)
    p.paint_granulation_pass(
        granule_scale=1.0, warm_shift=1.0, cool_shift=1.0,
        edge_sharpen=1.0, opacity=1.0
    )
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after paint_granulation_pass"
    )


def test_s258_granulation_warm_shift_affects_rb_channels():
    """With warm_shift > 0 and cool_shift=0, R and B channels should diverge."""
    p = _make_small_painter()
    _prime_canvas(p, bright_dark=True)
    before = _get_canvas(p).copy()
    p.paint_granulation_pass(
        granule_sigma=1.5,
        granule_scale=0.5,
        warm_shift=0.8,
        cool_shift=0.8,
        edge_sharpen=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    # Some R channel change expected at valley pixels
    r_diff = np.abs(after[:, :, 2].astype(int) - before[:, :, 2].astype(int))
    b_diff = np.abs(after[:, :, 0].astype(int) - before[:, :, 0].astype(int))
    assert r_diff.sum() > 0 or b_diff.sum() > 0, (
        "Granulation with non-zero warm/cool shift should change R or B channel"
    )


def test_s258_granulation_edge_sharpen_increases_edge_contrast():
    """High edge_sharpen should increase local contrast relative to no sharpen."""
    ref = _bright_dark_reference(64, 64)

    def _edge_variance(sharpen_val):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        p.paint_granulation_pass(
            granule_sigma=2.0,
            granule_scale=0.0,   # no chromatic change; only sharpen
            warm_shift=0.0,
            cool_shift=0.0,
            edge_sharpen=sharpen_val,
            opacity=1.0,
        )
        out = _get_canvas(p).astype(float) / 255.0
        lum = 0.299 * out[:, :, 2] + 0.587 * out[:, :, 1] + 0.114 * out[:, :, 0]
        return float(np.var(lum))

    var_none  = _edge_variance(0.0)
    var_sharp = _edge_variance(1.0)
    assert var_sharp >= var_none, (
        "edge_sharpen=1.0 should produce >= luminance variance vs no sharpen"
    )


def test_s258_granulation_flat_canvas_minimal_change():
    """On a perfectly flat canvas the detail layer is zero; minimal change expected."""
    from PIL import Image
    arr = np.full((64, 64, 3), 128, dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter()
    # Skip tone_ground to start truly flat; manually fill uniform gray
    p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    before = _get_canvas(p).copy()
    p.paint_granulation_pass(granule_scale=1.0, warm_shift=1.0, cool_shift=1.0,
                             edge_sharpen=1.0, opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(int) - after[:, :, :3].astype(int))
    assert diff.max() <= 5, (
        f"Flat canvas should see minimal granulation change; max_diff={diff.max()}"
    )


def test_s258_granulation_higher_sigma_softer_detail():
    """Larger granule_sigma should produce a smoother texture (less high-frequency)."""
    ref = _bright_dark_reference(64, 64)

    def _hf_energy(sigma_val):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        p.paint_granulation_pass(
            granule_sigma=sigma_val,
            granule_scale=0.3,
            warm_shift=0.3,
            cool_shift=0.3,
            edge_sharpen=0.0,
            opacity=1.0,
        )
        out = _get_canvas(p).astype(float) / 255.0
        lum = 0.299 * out[:, :, 2] + 0.587 * out[:, :, 1] + 0.114 * out[:, :, 0]
        # High-frequency energy = variance of (image - gaussian-blurred image)
        from scipy.ndimage import gaussian_filter
        smoothed = gaussian_filter(lum.astype(np.float32), sigma=2.0)
        hf = lum - smoothed
        return float(np.var(hf))

    hf_fine   = _hf_energy(0.5)
    hf_coarse = _hf_energy(8.0)
    # Coarser decomposition has larger patches -> less HF energy in output
    assert hf_coarse <= hf_fine + 1e-5, (
        "Larger sigma should produce <= high-frequency energy in the output"
    )


# ── giorgio_morandi catalog tests ─────────────────────────────────────────────

def test_s258_catalog_morandi_present():
    from art_catalog import CATALOG
    assert "giorgio_morandi" in CATALOG, "giorgio_morandi not found in CATALOG"


def test_s258_catalog_morandi_fields():
    from art_catalog import CATALOG
    s = CATALOG["giorgio_morandi"]
    assert "Morandi" in s.artist
    assert s.nationality.startswith("Italian")
    assert len(s.palette) >= 6
    assert len(s.famous_works) >= 3


def test_s258_catalog_morandi_inspiration_updated():
    """Inspiration must now reference morandi_dusty_vessel_pass and 169th mode."""
    from art_catalog import CATALOG
    s = CATALOG["giorgio_morandi"]
    assert "morandi_dusty_vessel_pass" in s.inspiration, (
        "morandi_dusty_vessel_pass not found in morandi inspiration"
    )
    assert "169" in s.inspiration, (
        "169th mode not referenced in morandi inspiration"
    )


def test_s258_catalog_morandi_ground_warm():
    """Morandi's ground should be warm off-white (high R, G >= 0.7)."""
    from art_catalog import CATALOG
    s = CATALOG["giorgio_morandi"]
    r, g, b = s.ground_color
    assert r > 0.70, f"Expected R > 0.70 for warm ground; got {r:.2f}"
    assert g > 0.60, f"Expected G > 0.60 for warm ground; got {g:.2f}"


def test_s258_catalog_count_unchanged():
    """CATALOG count must remain 255 (no new artist added this session)."""
    from art_catalog import CATALOG
    assert len(CATALOG) == 255, f"Expected 255 catalog entries, got {len(CATALOG)}"


def test_s258_catalog_get_style_morandi():
    """get_style() must retrieve morandi by key."""
    from art_catalog import get_style
    s = get_style("giorgio_morandi")
    assert "Morandi" in s.artist


# ── Integration: run both new passes together ─────────────────────────────────

def test_s258_full_pipeline_morandi_and_granulation():
    """Run both new passes in sequence; canvas should be modified and valid."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    before = _get_canvas(p).copy()

    p.morandi_dusty_vessel_pass(opacity=0.80)
    p.paint_granulation_pass(opacity=0.65)

    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Pipeline should modify canvas"
    assert after.min() >= 0 and after.max() <= 255, "Values must stay in [0, 255]"
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), "Alpha must be preserved"
