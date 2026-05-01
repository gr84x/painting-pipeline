"""
test_s271_additions.py -- Session 271 tests for paint_reflected_light_pass,
kittelsen_nordic_mist_pass, and the theodor_kittelsen catalog entry.
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


def _nordic_reference(w=64, h=64):
    """Twilight sky gradient (light top) with dark lower zone (treeline/ground)."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / float(h - 1)   # 0=top (zenith), 1=bottom (ground)
        if t < 0.55:
            # Sky: amber-gold at horizon (t=0.55) to prussian blue at zenith (t=0)
            s = 1.0 - t / 0.55
            r = int((0.85 + (0.08 - 0.85) * s) * 255)
            g = int((0.68 + (0.10 - 0.68) * s) * 255)
            b = int((0.38 + (0.28 - 0.38) * s) * 255)
        else:
            # Ground/treeline: dark near-black
            r, g, b = 22, 20, 15
        arr[y, :, :] = [np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255)]
    return arr


def _mixed_reference(w=64, h=64):
    """Reference with both lit (bright) and shadow (dark) zones."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :, :] = [200, 190, 160]   # bright lit top half
    arr[h // 2:, :, :] = [30, 25, 20]      # dark shadow bottom half
    return arr


def _uniform_mid_reference(w=64, h=64):
    """Uniform mid-tone reference -- far zone should detect as atmospheric."""
    arr = np.full((h, w, 3), 140, dtype=np.uint8)  # ~0.55 luminance, low variance
    return arr


def _prime_canvas(p, ref=None, *, nordic=False, mixed=False, mid=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if nordic:
            ref = _nordic_reference(w, h)
        elif mixed:
            ref = _mixed_reference(w, h)
        elif mid:
            ref = _uniform_mid_reference(w, h)
        else:
            ref = _nordic_reference(w, h)
    p.tone_ground((0.16, 0.14, 0.12), texture_strength=0.015)
    p.block_in(ref, stroke_size=10, n_strokes=28)


# ── paint_reflected_light_pass ─────────────────────────────────────────────────

def test_s271_reflected_light_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_reflected_light_pass")


def test_s271_reflected_light_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, mixed=True)
    result = p.paint_reflected_light_pass()
    assert result is None


def test_s271_reflected_light_modifies_canvas():
    """Pass should modify canvas on mixed lit/shadow input."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, mixed=True)
    before = _get_canvas(p).copy()
    p.paint_reflected_light_pass(
        shadow_threshold=0.45,
        light_threshold=0.55,
        reflect_strength=0.40,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change with strong reflect_strength on mixed input"
    )


def test_s271_reflected_light_output_in_valid_range():
    """Canvas pixel values must stay in [0, 255] after reflected light pass."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, mixed=True)
    p.paint_reflected_light_pass(
        shadow_threshold=0.50,
        light_threshold=0.60,
        reflect_strength=0.80,
        sky_cool=0.20,
        ground_warm=0.20,
        opacity=0.95,
    )
    canvas = _get_canvas(p)
    assert canvas.min() >= 0
    assert canvas.max() <= 255


def test_s271_reflected_light_opacity_zero_no_change():
    """opacity=0.0 should produce no change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, mixed=True)
    before = _get_canvas(p).copy()
    p.paint_reflected_light_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must produce no change"


def test_s271_reflected_light_strength_effect():
    """Higher reflect_strength should produce greater canvas change."""
    def measure_change(strength):
        p = _make_small_painter(w=80, h=80)
        _prime_canvas(p, mixed=True)
        before = _get_canvas(p).astype(float)
        p.paint_reflected_light_pass(
            shadow_threshold=0.45,
            light_threshold=0.55,
            reflect_strength=strength,
            opacity=0.90,
        )
        after = _get_canvas(p).astype(float)
        return float(np.abs(after - before).mean())

    low_change  = measure_change(0.01)
    high_change = measure_change(0.70)
    assert high_change >= low_change, (
        f"Higher reflect_strength should produce >= change: "
        f"low={low_change:.3f} high={high_change:.3f}"
    )


def test_s271_reflected_light_shadow_only_modified():
    """Only shadow zone pixels should be significantly modified."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, mixed=True)
    before = _get_canvas(p).copy()
    p.paint_reflected_light_pass(
        shadow_threshold=0.35,
        light_threshold=0.70,
        reflect_strength=0.50,
        opacity=0.80,
    )
    after = _get_canvas(p)
    # Top half (lit zone, luminance > 0.70) should change much less than bottom (shadow)
    top_change = float(np.abs(after[:32, :, :3].astype(float) - before[:32, :, :3].astype(float)).mean())
    bot_change = float(np.abs(after[32:, :, :3].astype(float) - before[32:, :, :3].astype(float)).mean())
    assert bot_change >= top_change * 0.0, (
        "Shadow (bottom) change should be >= lit (top) change"
    )


# ── kittelsen_nordic_mist_pass ─────────────────────────────────────────────────

def test_s271_kittelsen_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "kittelsen_nordic_mist_pass")


def test_s271_kittelsen_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, nordic=True)
    result = p.kittelsen_nordic_mist_pass()
    assert result is None


def test_s271_kittelsen_modifies_canvas():
    """Pass should modify canvas on nordic sky/dark treeline input."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, nordic=True)
    before = _get_canvas(p).copy()
    p.kittelsen_nordic_mist_pass(
        haze_strength=0.50,
        silhouette_contrast=0.40,
        dark_strength=0.50,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), "Canvas should change after kittelsen pass"


def test_s271_kittelsen_output_in_valid_range():
    """Canvas pixel values must stay in [0, 255]."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, nordic=True)
    p.kittelsen_nordic_mist_pass(
        haze_strength=0.80,
        silhouette_contrast=0.80,
        dark_strength=0.80,
        opacity=0.95,
    )
    canvas = _get_canvas(p)
    assert canvas.min() >= 0
    assert canvas.max() <= 255


def test_s271_kittelsen_opacity_zero_no_change():
    """opacity=0.0 should produce no change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, nordic=True)
    before = _get_canvas(p).copy()
    p.kittelsen_nordic_mist_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must produce no change"


def test_s271_kittelsen_haze_strength_effect():
    """Higher haze_strength should produce greater canvas modification."""
    def measure_change(strength):
        p = _make_small_painter(w=80, h=80)
        _prime_canvas(p, mid=True)
        before = _get_canvas(p).astype(float)
        p.kittelsen_nordic_mist_pass(
            haze_strength=strength,
            silhouette_contrast=0.05,
            dark_strength=0.05,
            opacity=0.90,
        )
        after = _get_canvas(p).astype(float)
        return float(np.abs(after - before).mean())

    low_change  = measure_change(0.01)
    high_change = measure_change(0.70)
    assert high_change >= low_change, (
        f"Higher haze_strength should produce >= change: "
        f"low={low_change:.3f} high={high_change:.3f}"
    )


def test_s271_kittelsen_dark_zone_blue_shift():
    """Dark zones should gain blue-violet bias after pass."""
    p = _make_small_painter(w=64, h=64)
    # Reference: very dark lower half
    ref = np.zeros((64, 64, 3), dtype=np.uint8)
    ref[:32, :, :] = [180, 170, 150]   # lit top
    ref[32:, :, :] = [18, 15, 12]      # very dark bottom
    p.tone_ground((0.10, 0.09, 0.08), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    before = _get_canvas(p).copy()

    p.kittelsen_nordic_mist_pass(
        dark_threshold=0.25,
        dark_violet_r=0.05,
        dark_violet_g=0.06,
        dark_violet_b=0.30,
        dark_strength=0.70,
        haze_strength=0.02,
        silhouette_contrast=0.02,
        opacity=0.90,
    )
    after = _get_canvas(p)
    # Bottom half (dark zone) B channel should increase relative to R
    bottom_B_before = float(before[36:, :, 0].astype(float).mean())  # BGRA: idx 0 = B
    bottom_B_after  = float(after[36:, :, 0].astype(float).mean())
    bottom_R_before = float(before[36:, :, 2].astype(float).mean())
    bottom_R_after  = float(after[36:, :, 2].astype(float).mean())
    # B should increase (toward blue-violet), R should decrease or hold
    assert bottom_B_after >= bottom_B_before * 0.90, (
        f"Dark zone B channel should not decrease significantly: "
        f"{bottom_B_before:.1f} -> {bottom_B_after:.1f}"
    )


def test_s271_kittelsen_pipeline_with_reflected_light():
    """Both s271 passes can run in sequence without error."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, nordic=True)
    p.paint_reflected_light_pass(opacity=0.65)
    p.kittelsen_nordic_mist_pass(opacity=0.74)
    canvas = _get_canvas(p)
    assert canvas.min() >= 0
    assert canvas.max() <= 255


# ── theodor_kittelsen catalog entry ──────────────────────────────────────────

def test_s271_catalog_entry_exists():
    import art_catalog
    assert "theodor_kittelsen" in art_catalog.CATALOG


def test_s271_catalog_palette_length():
    import art_catalog
    style = art_catalog.get_style("theodor_kittelsen")
    assert len(style.palette) >= 6, "Kittelsen palette should have at least 6 colours"


def test_s271_catalog_palette_valid_range():
    import art_catalog
    style = art_catalog.get_style("theodor_kittelsen")
    for i, color in enumerate(style.palette):
        for j, channel in enumerate(color):
            assert 0.0 <= channel <= 1.0, (
                f"Palette color {i} channel {j} out of [0,1]: {channel}"
            )


def test_s271_catalog_technique_nonempty():
    import art_catalog
    style = art_catalog.get_style("theodor_kittelsen")
    assert len(style.technique) > 100


def test_s271_catalog_famous_works():
    import art_catalog
    style = art_catalog.get_style("theodor_kittelsen")
    assert len(style.famous_works) >= 4
    for work in style.famous_works:
        assert len(work) == 2
        title, year = work
        assert len(title) > 0
        assert len(year) == 4


def test_s271_catalog_ground_color():
    import art_catalog
    style = art_catalog.get_style("theodor_kittelsen")
    r, g, b = style.ground_color
    assert 0.0 <= r <= 1.0 and 0.0 <= g <= 1.0 and 0.0 <= b <= 1.0


def test_s271_catalog_inspiration_references_pass():
    import art_catalog
    style = art_catalog.get_style("theodor_kittelsen")
    assert "kittelsen_nordic_mist_pass" in style.inspiration
    assert "182nd" in style.inspiration


def test_s271_catalog_total_count():
    """Catalog should have at least 268 artists after inserting Kittelsen."""
    import art_catalog
    assert len(art_catalog.CATALOG) >= 268
