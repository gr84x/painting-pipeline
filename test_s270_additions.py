"""
test_s270_additions.py -- Session 270 tests for paint_translucency_bloom_pass,
okeeffe_organic_form_pass, and the georgia_okeeffe catalog entry.
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


def _flower_reference(w=64, h=64):
    """Reference with near-white petal centre, crimson throat, indigo corners."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Indigo sky background
    arr[:, :, :] = [26, 31, 77]
    cx, cy = w // 2, h // 2
    # White-peach petal zone (circle)
    for y in range(h):
        for x in range(w):
            r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            petal_r = min(w, h) * 0.44
            if r < petal_r:
                depth = r / petal_r
                # Gradient from crimson (center) to near-white (outer)
                rr = int(184 + (249 - 184) * depth)
                gg = int(77  + (245 - 77)  * depth)
                bb = int(71  + (235 - 71)  * depth)
                arr[y, x, :] = [rr, gg, bb]
    return arr


def _warm_reference(w=64, h=64):
    """Warm mid-tone reference with smooth gradients."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            arr[y, x, :] = [200, 160, 130]
    return arr


def _high_luminance_low_sat_reference(w=64, h=64):
    """High-luminance, near-neutral reference for translucency bloom detection."""
    arr = np.full((h, w, 3), 200, dtype=np.uint8)   # near-white neutral
    return arr


def _prime_canvas(p, ref=None, *, flower=False, warm=False, bright=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if flower:
            ref = _flower_reference(w, h)
        elif warm:
            ref = _warm_reference(w, h)
        elif bright:
            ref = _high_luminance_low_sat_reference(w, h)
        else:
            ref = _flower_reference(w, h)
    p.tone_ground((0.94, 0.90, 0.84), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=28)


# ── paint_translucency_bloom_pass ─────────────────────────────────────────────

def test_s270_bloom_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_translucency_bloom_pass")


def test_s270_bloom_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, flower=True)
    result = p.paint_translucency_bloom_pass()
    assert result is None


def test_s270_bloom_modifies_canvas_on_bright_neutral():
    """Bloom should modify a near-white neutral canvas (high lum, low sat)."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_translucency_bloom_pass(
        lum_low=0.40,
        lum_high=0.95,
        sat_threshold=0.20,
        bloom_strength=0.40,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change on bright-neutral input with high bloom_strength"
    )


def test_s270_bloom_preserves_dark_zones():
    """Bloom should leave deep-indigo zones largely unchanged."""
    p = _make_small_painter(w=72, h=72)
    # Use flower ref: dark indigo in corners
    _prime_canvas(p, flower=True)
    before = _get_canvas(p).copy()

    p.paint_translucency_bloom_pass(
        lum_low=0.60,   # only affects bright zones
        lum_high=0.95,
        sat_threshold=0.08,
        bloom_strength=0.30,
        opacity=0.80,
    )
    after = _get_canvas(p)
    # Corners (indigo sky) should be little-changed
    corner_before = before[:16, :16, :3].astype(float).mean()
    corner_after  = after[:16, :16, :3].astype(float).mean()
    assert abs(corner_after - corner_before) < 30, (
        f"Dark corners changed too much: {corner_before:.1f} -> {corner_after:.1f}"
    )


def test_s270_bloom_opacity_zero_no_change():
    """opacity=0.0 should produce no change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_translucency_bloom_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must produce no change"


def test_s270_bloom_output_in_valid_range():
    """Canvas pixel values must stay in [0, 255] after bloom pass."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, bright=True)
    p.paint_translucency_bloom_pass(
        bloom_warmth=0.50,
        bloom_strength=0.80,
        halo_opacity=0.50,
        opacity=0.90,
    )
    canvas = _get_canvas(p)
    assert canvas.min() >= 0
    assert canvas.max() <= 255


def test_s270_bloom_halo_opacity_effect():
    """Higher halo_opacity should produce a more significant canvas change."""
    def measure_change(halo_op):
        p = _make_small_painter(w=80, h=80)
        _prime_canvas(p, flower=True)
        before = _get_canvas(p).astype(float)
        p.paint_translucency_bloom_pass(
            lum_low=0.35,
            lum_high=0.92,
            sat_threshold=0.15,
            halo_opacity=halo_op,
            bloom_strength=0.25,
            opacity=0.85,
        )
        after = _get_canvas(p).astype(float)
        return float(np.abs(after - before).mean())

    low_change  = measure_change(0.01)
    high_change = measure_change(0.60)
    assert high_change >= low_change, (
        f"Higher halo_opacity should produce >= change: low={low_change:.3f} high={high_change:.3f}"
    )


# ── okeeffe_organic_form_pass ─────────────────────────────────────────────────

def test_s270_okeeffe_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "okeeffe_organic_form_pass")


def test_s270_okeeffe_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, flower=True)
    result = p.okeeffe_organic_form_pass()
    assert result is None


def test_s270_okeeffe_modifies_canvas():
    """Canvas should change after okeeffe pass."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, flower=True)
    before = _get_canvas(p).copy()
    p.okeeffe_organic_form_pass(
        smooth_strength=0.50,
        sat_lift=0.20,
        edge_sharpen_amount=0.60,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after)


def test_s270_okeeffe_output_in_valid_range():
    """Canvas pixel values must stay in [0, 255]."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, warm=True)
    p.okeeffe_organic_form_pass(
        smooth_strength=0.60,
        sat_lift=0.30,
        edge_sharpen_amount=0.80,
        opacity=0.95,
    )
    canvas = _get_canvas(p)
    assert canvas.min() >= 0
    assert canvas.max() <= 255


def test_s270_okeeffe_opacity_zero_no_change():
    """opacity=0.0 should produce no change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, flower=True)
    before = _get_canvas(p).copy()
    p.okeeffe_organic_form_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must produce no change"


def test_s270_okeeffe_smooth_strength_effect():
    """Higher smooth_strength should produce greater canvas modification."""
    def measure_change(strength):
        p = _make_small_painter(w=80, h=80)
        _prime_canvas(p, flower=True)
        before = _get_canvas(p).astype(float)
        p.okeeffe_organic_form_pass(
            smooth_strength=strength,
            sat_lift=0.05,
            edge_sharpen_amount=0.1,
            opacity=0.90,
        )
        after = _get_canvas(p).astype(float)
        return float(np.abs(after - before).mean())

    low_change  = measure_change(0.05)
    high_change = measure_change(0.80)
    assert high_change >= low_change, (
        f"Higher smooth_strength should produce >= change: low={low_change:.3f} high={high_change:.3f}"
    )


def test_s270_okeeffe_edge_sharpen_effect():
    """Higher edge_sharpen_amount should produce greater canvas modification."""
    def measure_change(amount):
        p = _make_small_painter(w=80, h=80)
        _prime_canvas(p, flower=True)
        before = _get_canvas(p).astype(float)
        p.okeeffe_organic_form_pass(
            smooth_strength=0.1,
            sat_lift=0.05,
            edge_sharpen_amount=amount,
            edge_threshold=0.005,   # low threshold: more pixels treated as edges
            opacity=0.90,
        )
        after = _get_canvas(p).astype(float)
        return float(np.abs(after - before).mean())

    low_change  = measure_change(0.01)
    high_change = measure_change(0.90)
    assert high_change >= low_change, (
        f"Higher edge_sharpen_amount should produce >= change: low={low_change:.3f} high={high_change:.3f}"
    )


def test_s270_okeeffe_pipeline_with_bloom():
    """Both passes can be run in sequence without error."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, flower=True)
    p.paint_translucency_bloom_pass(opacity=0.70)
    p.okeeffe_organic_form_pass(opacity=0.78)
    canvas = _get_canvas(p)
    assert canvas.min() >= 0
    assert canvas.max() <= 255


# ── georgia_okeeffe catalog entry ────────────────────────────────────────────

def test_s270_catalog_entry_exists():
    import art_catalog
    assert "georgia_okeeffe" in art_catalog.CATALOG


def test_s270_catalog_palette_length():
    import art_catalog
    style = art_catalog.get_style("georgia_okeeffe")
    assert len(style.palette) >= 6, "O'Keeffe palette should have at least 6 colours"


def test_s270_catalog_palette_valid_range():
    import art_catalog
    style = art_catalog.get_style("georgia_okeeffe")
    for i, color in enumerate(style.palette):
        for j, channel in enumerate(color):
            assert 0.0 <= channel <= 1.0, (
                f"Palette color {i} channel {j} out of [0,1]: {channel}"
            )


def test_s270_catalog_technique_nonempty():
    import art_catalog
    style = art_catalog.get_style("georgia_okeeffe")
    assert len(style.technique) > 100


def test_s270_catalog_famous_works():
    import art_catalog
    style = art_catalog.get_style("georgia_okeeffe")
    assert len(style.famous_works) >= 4
    for work in style.famous_works:
        assert len(work) == 2
        title, year = work
        assert len(title) > 0
        assert len(year) == 4


def test_s270_catalog_ground_color():
    import art_catalog
    style = art_catalog.get_style("georgia_okeeffe")
    r, g, b = style.ground_color
    assert 0.0 <= r <= 1.0 and 0.0 <= g <= 1.0 and 0.0 <= b <= 1.0


def test_s270_catalog_inspiration_references_pass():
    import art_catalog
    style = art_catalog.get_style("georgia_okeeffe")
    assert "okeeffe_organic_form_pass" in style.inspiration
    assert "181st" in style.inspiration


def test_s270_catalog_total_count():
    """Catalog should have at least 267 artists after inserting O'Keeffe."""
    import art_catalog
    assert len(art_catalog.CATALOG) >= 267
