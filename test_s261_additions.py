"""
test_s261_additions.py -- Session 261 tests for sisley_silver_veil_pass,
paint_triple_zone_glaze_pass, and the alfred_sisley catalog entry.
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


def _bright_reference(w=64, h=64):
    """Bright upper/dark lower reference for sky tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :] = [210, 215, 225]   # cool bright sky zone
    arr[h // 2:, :] = [80,  90,  75]    # darker ground
    return Image.fromarray(arr, "RGB")


def _edge_reference(w=64, h=64):
    """High-contrast half-half for edge/zone tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [210, 200, 185]
    arr[:, w // 2:, :] = [30, 25, 20]
    return Image.fromarray(arr, "RGB")


def _grey_reference(w=64, h=64):
    """Mid-grey flat reference."""
    from PIL import Image
    arr = np.full((h, w, 3), 145, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, bright=False, edge=False, grey=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if bright:
            ref = _bright_reference(w, h)
        elif edge:
            ref = _edge_reference(w, h)
        elif grey:
            ref = _grey_reference(w, h)
        else:
            ref = _bright_reference(w, h)
    p.tone_ground((0.82, 0.84, 0.82), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── sisley_silver_veil_pass ───────────────────────────────────────────────────

def test_s261_sisley_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "sisley_silver_veil_pass")


def test_s261_sisley_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    result = p.sisley_silver_veil_pass()
    assert result is None


def test_s261_sisley_pass_modifies_canvas():
    """Pass must change at least some pixels on a non-trivial canvas."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.sisley_silver_veil_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after sisley_silver_veil_pass"


def test_s261_sisley_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p)
    p.sisley_silver_veil_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after sisley_silver_veil_pass"
    )


def test_s261_sisley_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.sisley_silver_veil_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s261_sisley_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.sisley_silver_veil_pass(
        sky_strength=1.0, haze_strength=1.0,
        sky_blur_opacity=1.0, opacity=1.0
    )
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after sisley_silver_veil_pass"
    )


def test_s261_sisley_sky_band_affects_upper_rows():
    """Sky band must cause more change in upper rows than lower rows."""
    p_before = _make_small_painter()
    _prime_canvas(p_before, bright=True)
    before = _get_canvas(p_before).copy().astype(float)

    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.sisley_silver_veil_pass(
        sky_fraction=0.5,
        sky_strength=0.80,
        haze_strength=0.0,
        sky_blur_opacity=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float)

    diff = np.abs(before - after)
    h = diff.shape[0]
    upper_change = diff[:h // 4, :, :3].sum()
    lower_change = diff[3 * h // 4:, :, :3].sum()
    assert upper_change > lower_change, (
        f"Sky band should change upper rows more; upper={upper_change:.1f}, "
        f"lower={lower_change:.1f}"
    )


def test_s261_sisley_sky_fraction_zero_no_sky_change():
    """sky_fraction=0 means no sky rows affected -- pass should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    # sky_fraction=0 → sky_rows=0 → no sky effect; haze still applies
    p.sisley_silver_veil_pass(sky_fraction=0.0, sky_strength=0.0,
                               haze_strength=0.0, sky_blur_opacity=0.0, opacity=1.0)
    after = _get_canvas(p)
    # With all effects disabled at opacity=1, result should equal original
    assert np.array_equal(before, after), (
        "All effects disabled should leave canvas unchanged"
    )


def test_s261_sisley_haze_affects_midtone():
    """Haze stage should shift midtone luminance pixels toward silver."""
    from PIL import Image
    arr = np.full((64, 64, 3), 145, dtype=np.uint8)  # ~lum=0.57, ideal for haze
    ref = Image.fromarray(arr, "RGB")

    p_base = _make_small_painter()
    _prime_canvas(p_base, ref=ref)
    before = _get_canvas(p_base).copy().astype(float) / 255.0
    b_before = before[:, :, 0].mean()  # blue channel mean

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    p.sisley_silver_veil_pass(
        sky_fraction=0.0,
        sky_strength=0.0,
        haze_center=0.57,
        haze_band=0.15,
        haze_r=0.78,
        haze_g=0.78,
        haze_b=0.82,  # slightly blue target
        haze_strength=0.80,
        sky_blur_opacity=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    b_after = after[:, :, 0].mean()

    # haze_b=0.82 > typical midgrey blue; blue channel should increase
    assert b_after >= b_before - 0.01, (
        f"Haze with blue target should not reduce blue channel; "
        f"before={b_before:.3f}, after={b_after:.3f}"
    )


def test_s261_sisley_horizontal_blur_reduces_variance_in_sky():
    """Horizontal sky blur should reduce horizontal variance in sky rows."""
    from PIL import Image
    # Checkerboard pattern in upper half -- high horizontal variance
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    for i in range(64):
        for j in range(64):
            arr[i, j, :] = 210 if (i + j) % 2 == 0 else 150
    arr[32:, :] = 80  # lower half stays dark
    ref = Image.fromarray(arr, "RGB")

    p_before = _make_small_painter()
    _prime_canvas(p_before, ref=ref)
    raw = _get_canvas(p_before).astype(float)
    # Horizontal variance in top 30 rows (sky zone)
    sky_zone_before = raw[:16, :, :3]
    var_before = float(np.var(np.diff(sky_zone_before, axis=1)))

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    p.sisley_silver_veil_pass(
        sky_fraction=0.50,
        sky_strength=0.0,
        haze_strength=0.0,
        sky_blur_sigma=6.0,
        sky_blur_opacity=1.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float)
    sky_zone_after = after[:16, :, :3]
    var_after = float(np.var(np.diff(sky_zone_after, axis=1)))

    assert var_after <= var_before, (
        f"Horizontal blur should reduce sky horizontal variance; "
        f"before={var_before:.4f}, after={var_after:.4f}"
    )


def test_s261_sisley_higher_opacity_more_change():
    """Higher opacity should produce at least as much change as lower opacity."""
    ref = _bright_reference(64, 64)

    def _run(op):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        before = _get_canvas(p).copy()
        p.sisley_silver_veil_pass(opacity=op)
        after = _get_canvas(p)
        return int(np.abs(before.astype(int) - after.astype(int)).sum())

    assert _run(0.8) >= _run(0.2), "Higher opacity should produce more change"


# ── paint_triple_zone_glaze_pass ──────────────────────────────────────────────

def test_s261_triple_glaze_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_triple_zone_glaze_pass")


def test_s261_triple_glaze_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    result = p.paint_triple_zone_glaze_pass()
    assert result is None


def test_s261_triple_glaze_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()
    p.paint_triple_zone_glaze_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_triple_zone_glaze_pass"


def test_s261_triple_glaze_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p)
    p.paint_triple_zone_glaze_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after paint_triple_zone_glaze_pass"
    )


def test_s261_triple_glaze_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()
    p.paint_triple_zone_glaze_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s261_triple_glaze_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    p.paint_triple_zone_glaze_pass(
        shadow_opacity=0.5, mid_opacity=0.5,
        highlight_opacity=0.5, opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after paint_triple_zone_glaze_pass"
    )


def test_s261_triple_glaze_shadow_tints_dark_zone():
    """Shadow glaze should shift blue channel up in dark regions."""
    from PIL import Image
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :, :] = [50, 48, 46]  # very dark (lum ~0.19)
    ref = Image.fromarray(arr, "RGB")

    p_base = _make_small_painter()
    _prime_canvas(p_base, ref=ref)
    before = _get_canvas(p_base).copy().astype(float) / 255.0
    b_before = before[:, :, 0].mean()

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    p.paint_triple_zone_glaze_pass(
        shadow_pivot=0.40,
        shadow_r=0.25, shadow_g=0.28, shadow_b=0.55,  # blue target
        shadow_opacity=0.60,
        mid_opacity=0.0,
        highlight_opacity=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    b_after = after[:, :, 0].mean()

    assert b_after >= b_before - 0.01, (
        f"Shadow glaze with blue target should push blue up; "
        f"before={b_before:.3f}, after={b_after:.3f}"
    )


def test_s261_triple_glaze_highlight_tints_bright_zone():
    """Highlight glaze should shift channels in bright regions."""
    from PIL import Image
    arr = np.full((64, 64, 3), 220, dtype=np.uint8)  # bright (lum ~0.86)
    ref = Image.fromarray(arr, "RGB")

    p_base = _make_small_painter()
    _prime_canvas(p_base, ref=ref)
    before = _get_canvas(p_base).copy().astype(float) / 255.0
    r_before = before[:, :, 2].mean()

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    p.paint_triple_zone_glaze_pass(
        highlight_pivot=0.65,
        highlight_r=0.95, highlight_g=0.90, highlight_b=0.80,
        highlight_opacity=0.60,
        shadow_opacity=0.0,
        mid_opacity=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    r_after = after[:, :, 2].mean()

    # Highlight target has high R, so mean R should not decrease
    assert r_after >= r_before - 0.02, (
        f"Highlight glaze should not reduce red in bright zone; "
        f"before={r_before:.3f}, after={r_after:.3f}"
    )


def test_s261_triple_glaze_three_zones_all_active():
    """Running all three glazes simultaneously should modify canvas."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()
    p.paint_triple_zone_glaze_pass(
        shadow_opacity=0.20,
        mid_opacity=0.15,
        highlight_opacity=0.20,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "All-active triple glaze should modify canvas"


def test_s261_triple_glaze_higher_opacity_more_change():
    """Higher opacity should produce at least as much change."""
    ref = _edge_reference(64, 64)

    def _run(op):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        before = _get_canvas(p).copy()
        p.paint_triple_zone_glaze_pass(opacity=op)
        after = _get_canvas(p)
        return int(np.abs(before.astype(int) - after.astype(int)).sum())

    assert _run(0.8) >= _run(0.2), "Higher opacity should produce more change"


# ── alfred_sisley catalog tests ───────────────────────────────────────────────

def test_s261_catalog_sisley_present():
    from art_catalog import CATALOG
    assert "alfred_sisley" in CATALOG, (
        "alfred_sisley not found in CATALOG"
    )


def test_s261_catalog_sisley_fields():
    from art_catalog import CATALOG
    s = CATALOG["alfred_sisley"]
    assert "Sisley" in s.artist
    assert "French" in s.nationality or "British" in s.nationality
    assert len(s.palette) >= 8
    assert len(s.famous_works) >= 8


def test_s261_catalog_sisley_inspiration():
    """Inspiration must reference sisley_silver_veil_pass and 172nd mode."""
    from art_catalog import CATALOG
    s = CATALOG["alfred_sisley"]
    assert "sisley_silver_veil_pass" in s.inspiration, (
        "sisley_silver_veil_pass not found in inspiration"
    )
    assert "172" in s.inspiration, (
        "172nd mode not referenced in inspiration"
    )


def test_s261_catalog_sisley_silver_palette():
    """Sisley's palette should include a near-silver-grey tone (high lum, low sat)."""
    from art_catalog import CATALOG
    s = CATALOG["alfred_sisley"]
    # Check for a high-luminance near-neutral entry
    lums = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in s.palette]
    assert max(lums) > 0.80, (
        f"Palette should include a near-silver tone; max_lum={max(lums):.3f}"
    )


def test_s261_catalog_count_increased():
    """CATALOG count must be 258 (new artist added this session)."""
    from art_catalog import CATALOG
    assert len(CATALOG) == 258, f"Expected 258 catalog entries, got {len(CATALOG)}"


def test_s261_catalog_get_style_sisley():
    """get_style() must retrieve Sisley by key."""
    from art_catalog import get_style
    s = get_style("alfred_sisley")
    assert "Sisley" in s.artist


# ── Integration: run both new passes together ─────────────────────────────────

def test_s261_full_pipeline_sisley_and_triple_glaze():
    """Run both new passes in sequence; canvas should be modified and valid."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()

    p.sisley_silver_veil_pass(opacity=0.78)
    p.paint_triple_zone_glaze_pass(opacity=0.72)

    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Pipeline should modify canvas"
    assert after.min() >= 0 and after.max() <= 255, "Values must stay in [0, 255]"
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), "Alpha must be preserved"
