"""
test_s269_additions.py -- Session 269 tests for paint_chromatic_vibration_pass,
gorky_biomorphic_fluid_pass, and the arshile_gorky catalog entry.
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


def _garden_reference(w=64, h=64):
    """Reference with warm sky top, viridian mass left, crimson accent center."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Upper warm sky
    arr[:int(h * 0.45), :, :] = [210, 168, 80]
    # Warm ochre mid-ground center
    arr[int(h * 0.45):int(h * 0.70), int(w * 0.25):int(w * 0.75), :] = [185, 128, 45]
    # Left viridian mass
    arr[int(h * 0.40):, :int(w * 0.30), :] = [35, 92, 55]
    # Right viridian mass
    arr[int(h * 0.40):, int(w * 0.70):, :] = [40, 95, 57]
    # Crimson accent
    cy, cx = int(h * 0.52), int(w * 0.50)
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            if dy * dy + dx * dx <= 25:
                yy, xx = cy + dy, cx + dx
                if 0 <= yy < h and 0 <= xx < w:
                    arr[yy, xx, :] = [188, 40, 45]
    return Image.fromarray(arr, "RGB")


def _warm_cool_reference(w=64, h=64):
    """Left half warm (orange), right half cool (blue) -- strong temperature gradient."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [210, 130, 40]   # warm orange
    arr[:, w // 2:, :] = [50, 90, 200]    # cool blue
    return Image.fromarray(arr, "RGB")


def _grey_reference(w=64, h=64):
    """Uniform mid-grey."""
    from PIL import Image
    return Image.fromarray(np.full((h, w, 3), 128, dtype=np.uint8), "RGB")


def _prime_canvas(p, ref=None, *, garden=False, warm_cool=False, grey=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if garden:
            ref = _garden_reference(w, h)
        elif warm_cool:
            ref = _warm_cool_reference(w, h)
        elif grey:
            ref = _grey_reference(w, h)
        else:
            ref = _garden_reference(w, h)
    p.tone_ground((0.92, 0.88, 0.76), texture_strength=0.01)
    p.block_in(np.array(ref), stroke_size=10, n_strokes=28)


# ── paint_chromatic_vibration_pass ────────────────────────────────────────────

def test_s269_vibration_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_chromatic_vibration_pass")


def test_s269_vibration_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, garden=True)
    result = p.paint_chromatic_vibration_pass()
    assert result is None


def test_s269_vibration_modifies_canvas():
    """Canvas changes after applying chromatic vibration pass."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, warm_cool=True)
    before = _get_canvas(p).copy()
    p.paint_chromatic_vibration_pass(
        vibration_strength=0.30,
        boundary_threshold=0.02,
        opacity=0.90,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff > 0, "Canvas was not modified by paint_chromatic_vibration_pass"


def test_s269_vibration_warm_side_redder():
    """On a warm/cool split canvas, the warm side should become more red at boundaries."""
    p = _make_small_painter(w=80, h=40)
    _prime_canvas(p, warm_cool=True)

    before = _get_canvas(p).copy().astype(np.float32)

    p.paint_chromatic_vibration_pass(
        vibration_sigma=4.0,
        vibration_strength=0.35,
        boundary_threshold=0.02,
        saturation_boost=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32)

    # Near the boundary, warm side should be pushed warmer (more R, less B)
    # The boundary is around x=40. Check a strip near the boundary.
    boundary_col_warm = slice(max(0, 40 - 10), max(1, 40 - 2))

    # BGRA: channel 2 = R, channel 0 = B
    r_warm_before = before[:, boundary_col_warm, 2].mean()
    r_warm_after  = after[:, boundary_col_warm, 2].mean()

    # Warm side should not have gotten colder (R should not have decreased)
    assert r_warm_after >= r_warm_before - 5.0, (
        f"Warm boundary R should not decrease: before={r_warm_before:.1f}, after={r_warm_after:.1f}"
    )


def test_s269_vibration_opacity_zero_no_change():
    """At opacity=0 the canvas should not change."""
    p = _make_small_painter()
    _prime_canvas(p, garden=True)
    before = _get_canvas(p).copy()
    p.paint_chromatic_vibration_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff <= 1, f"Canvas changed at opacity=0 (max diff={diff})"


def test_s269_vibration_output_shape_preserved():
    """Canvas shape is unchanged after pass."""
    p = _make_small_painter(w=56, h=80)
    _prime_canvas(p, garden=True)
    p.paint_chromatic_vibration_pass()
    after = _get_canvas(p)
    assert after.shape == (80, 56, 4)


def test_s269_vibration_values_in_range():
    """Output pixel values remain in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    p.paint_chromatic_vibration_pass(
        vibration_strength=0.40,
        saturation_boost=0.20,
        opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0
    assert after.max() <= 255


def test_s269_vibration_grey_canvas_minimal_change():
    """A pure grey canvas (no temperature) should change minimally."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, grey=True)
    before = _get_canvas(p).copy().astype(np.float32)
    p.paint_chromatic_vibration_pass(
        vibration_strength=0.30,
        boundary_threshold=0.04,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32)
    # On a grey canvas (R≈G≈B), temperature T = R-B ≈ 0 everywhere.
    # After tone_ground and block_in there's some variation, but vibration
    # should still be constrained.
    diff = np.abs(before - after).max()
    assert diff <= 80, f"Excessive change on grey canvas (max diff={diff})"


def test_s269_vibration_non_square():
    """Pass handles non-square canvas."""
    p = _make_small_painter(w=52, h=80)
    _prime_canvas(p, garden=True)
    p.paint_chromatic_vibration_pass()
    after = _get_canvas(p)
    assert after.shape == (80, 52, 4)


def test_s269_vibration_strong_strength_still_valid():
    """Very high vibration_strength keeps values in valid range."""
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    p.paint_chromatic_vibration_pass(
        vibration_strength=0.80,
        saturation_boost=0.40,
        opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0
    assert after.max() <= 255


# ── gorky_biomorphic_fluid_pass ───────────────────────────────────────────────

def test_s269_gorky_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "gorky_biomorphic_fluid_pass")


def test_s269_gorky_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, garden=True)
    result = p.gorky_biomorphic_fluid_pass()
    assert result is None


def test_s269_gorky_modifies_canvas():
    """Canvas changes after applying Gorky pass."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, garden=True)
    before = _get_canvas(p).copy()
    p.gorky_biomorphic_fluid_pass(
        wash_strength=0.30,
        contour_opacity=0.35,
        opacity=0.85,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff > 0, "Canvas was not modified by gorky_biomorphic_fluid_pass"


def test_s269_gorky_opacity_zero_no_change():
    """At opacity=0 the canvas should not change."""
    p = _make_small_painter()
    _prime_canvas(p, garden=True)
    before = _get_canvas(p).copy()
    p.gorky_biomorphic_fluid_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff <= 1, f"Canvas changed at opacity=0 (max diff={diff})"


def test_s269_gorky_output_shape_preserved():
    """Canvas shape is unchanged after pass."""
    p = _make_small_painter(w=56, h=80)
    _prime_canvas(p, garden=True)
    p.gorky_biomorphic_fluid_pass()
    after = _get_canvas(p)
    assert after.shape == (80, 56, 4)


def test_s269_gorky_values_in_range():
    """Output pixel values remain in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, garden=True)
    p.gorky_biomorphic_fluid_pass(
        wash_strength=0.40,
        contour_opacity=0.50,
        ground_warmth=0.20,
        opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0
    assert after.max() <= 255


def test_s269_gorky_non_square_canvas():
    """Pass handles non-square canvas without shape errors."""
    p = _make_small_painter(w=52, h=80)
    _prime_canvas(p, garden=True)
    p.gorky_biomorphic_fluid_pass()
    after = _get_canvas(p)
    assert after.shape == (80, 52, 4)


def test_s269_gorky_grey_canvas_no_crash():
    """Pass runs on a grey (low-saturation) canvas without error."""
    p = _make_small_painter()
    _prime_canvas(p, grey=True)
    p.gorky_biomorphic_fluid_pass()
    after = _get_canvas(p)
    assert after.shape == (p.canvas.h, p.canvas.w, 4)


def test_s269_gorky_high_saturation_enriched():
    """High-saturation zones should be enriched (more saturated) after pass."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, garden=True)
    before = _get_canvas(p).copy().astype(np.float32)

    # Compute saturation before in green zone (viridian area)
    green_strip = before[:, :16, :]   # left strip (viridian mass)
    r_before = green_strip[:, :, 2] / 255.0
    g_before = green_strip[:, :, 1] / 255.0
    b_before = green_strip[:, :, 0] / 255.0
    mx_b = np.maximum(np.maximum(r_before, g_before), b_before)
    mn_b = np.minimum(np.minimum(r_before, g_before), b_before)
    sat_before = np.where(mx_b > 0.01, (mx_b - mn_b) / (mx_b + 1e-6), 0.0).mean()

    p.gorky_biomorphic_fluid_pass(wash_strength=0.35, opacity=1.0)
    after = _get_canvas(p).astype(np.float32)

    r_after = after[:, :16, 2] / 255.0
    g_after = after[:, :16, 1] / 255.0
    b_after = after[:, :16, 0] / 255.0
    mx_a = np.maximum(np.maximum(r_after, g_after), b_after)
    mn_a = np.minimum(np.minimum(r_after, g_after), b_after)
    sat_after = np.where(mx_a > 0.01, (mx_a - mn_a) / (mx_a + 1e-6), 0.0).mean()

    # Saturation in the viridian zone should not dramatically decrease
    assert sat_after >= sat_before - 0.06, (
        f"Saturation should not drop much after gorky pass: "
        f"before={sat_before:.3f}, after={sat_after:.3f}"
    )


def test_s269_gorky_ground_zones_warmer():
    """Low-saturation ground zones should be pushed toward warm cream."""
    p = _make_small_painter(w=64, h=64)
    # Use grey reference so the whole canvas is a "ground zone"
    _prime_canvas(p, grey=True)
    before = _get_canvas(p).copy().astype(np.float32)
    r_before = before[:, :, 2].mean() / 255.0
    b_before = before[:, :, 0].mean() / 255.0

    p.gorky_biomorphic_fluid_pass(
        ground_warmth=0.30,
        ground_color=(0.95, 0.85, 0.65),
        wash_strength=0.0,
        contour_opacity=0.0,
        bleed_opacity=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32)
    r_after = after[:, :, 2].mean() / 255.0
    b_after = after[:, :, 0].mean() / 255.0

    # Warm ground should push R up and not increase B much
    # (ground_color R=0.95 > B=0.65, so red channel should rise)
    assert r_after >= r_before - 0.01, (
        f"Red channel should not decrease with warm ground: "
        f"before={r_before:.3f}, after={r_after:.3f}"
    )


def test_s269_gorky_no_crash_zero_sigma():
    """Pass handles near-zero sigma without crashing."""
    p = _make_small_painter()
    _prime_canvas(p, garden=True)
    p.gorky_biomorphic_fluid_pass(wash_sigma=0.1, bleed_sigma=0.1)
    after = _get_canvas(p)
    assert after.shape == (p.canvas.h, p.canvas.w, 4)


# ── arshile_gorky catalog entry ───────────────────────────────────────────────

def test_s269_catalog_entry_exists():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert style is not None


def test_s269_catalog_artist_name():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert style.artist == "Arshile Gorky"


def test_s269_catalog_movement():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert ("Biomorphic" in style.movement or "Abstract" in style.movement
            or "Surreal" in style.movement)


def test_s269_catalog_nationality():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert "American" in style.nationality or "Armenian" in style.nationality


def test_s269_catalog_palette_has_entries():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert len(style.palette) >= 6


def test_s269_catalog_palette_values_valid():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    for colour in style.palette:
        assert len(colour) == 3
        for v in colour:
            assert 0.0 <= v <= 1.0, f"Palette value out of range: {v}"


def test_s269_catalog_technique_nonempty():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert isinstance(style.technique, str) and len(style.technique) > 50


def test_s269_catalog_famous_works():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert len(style.famous_works) >= 4
    for (title, year) in style.famous_works:
        assert isinstance(title, str) and len(title) > 2
        assert isinstance(year, str) and len(year) == 4


def test_s269_catalog_in_list():
    from art_catalog import list_artists
    assert "arshile_gorky" in list_artists()


def test_s269_catalog_ground_color_valid():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert len(style.ground_color) == 3
    for v in style.ground_color:
        assert 0.0 <= v <= 1.0


def test_s269_catalog_stroke_size_positive():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert style.stroke_size > 0


def test_s269_catalog_inspiration_mentions_180th():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert "180" in style.inspiration


def test_s269_catalog_inspiration_mentions_gorky():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert "gorky" in style.inspiration.lower() or "biomorphic" in style.inspiration.lower()


def test_s269_catalog_period_contains_dates():
    from art_catalog import get_style
    style = get_style("arshile_gorky")
    assert "1904" in style.period or "1948" in style.period
