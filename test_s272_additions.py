"""
test_s272_additions.py -- Session 272 tests for paint_scumbling_veil_pass,
ernst_decalcomania_pass, and the max_ernst catalog entry.
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


def _dark_reference(w=64, h=64):
    """Dark lower zone (shadow) with bright upper zone (sky) -- for scumbling test."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :, :] = [200, 180, 140]   # bright sky top half
    arr[h // 2:, :, :] = [35, 25, 15]      # dark ground bottom half
    return arr


def _desert_reference(w=64, h=64):
    """Desert gradient: violet-indigo top, amber horizon, dark umber ground."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / float(h - 1)
        if t < 0.50:
            # Sky gradient
            s = t / 0.50
            r = int((0.06 + (0.86 - 0.06) * s) * 255)
            g = int((0.08 + (0.70 - 0.08) * s) * 255)
            b = int((0.28 + (0.36 - 0.28) * s) * 255)
        else:
            # Ground
            r, g, b = 50, 38, 22
        arr[y, :, :] = [np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255)]
    return arr


def _prime_canvas(p, ref=None, *, dark=False, desert=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if dark:
            ref = _dark_reference(w, h)
        else:
            ref = _desert_reference(w, h)
    p.tone_ground((0.20, 0.16, 0.10), texture_strength=0.015)
    p.block_in(ref, stroke_size=10, n_strokes=28)


# ── paint_scumbling_veil_pass ──────────────────────────────────────────────────

def test_s272_scumbling_veil_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_scumbling_veil_pass")


def test_s272_scumbling_veil_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    result = p.paint_scumbling_veil_pass()
    assert result is None


def test_s272_scumbling_veil_modifies_canvas():
    """Scumbling veil should lighten dark zones -- canvas must change."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.paint_scumbling_veil_pass(
        dark_threshold=0.50,
        veil_lightness=0.30,
        coverage_density=0.90,
        opacity=0.85,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change with high coverage_density and opacity on dark input"
    )


def test_s272_scumbling_veil_lightens_dark_zone():
    """Scumbling veil should increase mean luminance in the dark zone."""
    p = _make_small_painter(w=80, h=80)
    ref = _dark_reference(80, 80)
    p.tone_ground((0.20, 0.16, 0.10), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = _get_canvas(p).copy()
    # Compute mean R+G+B in bottom half (dark zone)
    dark_before = before[40:, :, :3].astype(np.float32).mean()

    p.paint_scumbling_veil_pass(
        dark_threshold=0.55,
        veil_lightness=0.28,
        coverage_density=0.88,
        opacity=0.80,
    )
    after = _get_canvas(p)
    dark_after = after[40:, :, :3].astype(np.float32).mean()

    assert dark_after > dark_before, (
        f"Dark zone mean should increase after scumbling veil: "
        f"before={dark_before:.2f}, after={dark_after:.2f}"
    )


def test_s272_scumbling_veil_preserves_bright_pixels():
    """Pixels above dark_threshold must not change -- scumbling only touches darks."""
    p = _make_small_painter(w=80, h=80)
    ref = _dark_reference(80, 80)
    p.tone_ground((0.20, 0.16, 0.10), texture_strength=0.01)
    # Use many strokes to ensure the bright top zone is well-covered
    p.block_in(ref, stroke_size=8, n_strokes=200)

    before = _get_canvas(p).copy()
    lum_before = (
        0.299 * before[:, :, 2].astype(np.float32) / 255.0 +
        0.587 * before[:, :, 1].astype(np.float32) / 255.0 +
        0.114 * before[:, :, 0].astype(np.float32) / 255.0
    )

    dark_threshold = 0.35
    p.paint_scumbling_veil_pass(
        dark_threshold=dark_threshold,
        veil_lightness=0.25,
        coverage_density=0.85,
        opacity=0.80,
    )
    after = _get_canvas(p)

    # Pixels that were above threshold before should be unchanged
    bright_mask = lum_before >= dark_threshold
    n_bright = int(bright_mask.sum())
    if n_bright > 0:
        diff = np.abs(
            before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32)
        )
        max_change_in_bright = int(diff[bright_mask].max())
        assert max_change_in_bright == 0, (
            f"Pixels above dark_threshold should not change; "
            f"max change in bright pixels = {max_change_in_bright}"
        )


def test_s272_scumbling_veil_zero_coverage_no_change():
    """Zero coverage_density should produce no change (no pixels receive veil)."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.paint_scumbling_veil_pass(
        coverage_density=0.0,   # no coverage -- nothing applied
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero coverage_density should produce no canvas change"
    )


def test_s272_scumbling_veil_zero_opacity_no_change():
    """Zero opacity should produce no visible change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.paint_scumbling_veil_pass(
        coverage_density=0.90,
        opacity=0.0,
    )
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


# ── ernst_decalcomania_pass ────────────────────────────────────────────────────

def test_s272_ernst_decalcomania_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "ernst_decalcomania_pass")


def test_s272_ernst_decalcomania_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.ernst_decalcomania_pass()
    assert result is None


def test_s272_ernst_decalcomania_modifies_canvas():
    """Decalcomania pass should modify the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.ernst_decalcomania_pass(
        transfer_strength=0.50,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change with high transfer_strength on primed canvas"
    )


def test_s272_ernst_decalcomania_zero_opacity_no_change():
    """Zero opacity should produce no visible change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.ernst_decalcomania_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s272_ernst_decalcomania_zero_transfer_minimal_change():
    """Zero transfer_strength: only vein darkening applies (minimal change)."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.ernst_decalcomania_pass(
        transfer_strength=0.0,
        vein_strength=0.0,
        opacity=0.90,
    )
    after = _get_canvas(p)
    # With both transfer and vein at zero and opacity blending toward original,
    # the result should be identical to the original
    assert np.array_equal(before, after), (
        "Zero transfer_strength and vein_strength should produce no change"
    )


def test_s272_ernst_decalcomania_deterministic():
    """Same seed should produce identical results."""
    p1 = _make_small_painter(w=80, h=80)
    _prime_canvas(p1)
    p1.ernst_decalcomania_pass(noise_seed=42, opacity=0.70)
    result1 = _get_canvas(p1).copy()

    p2 = _make_small_painter(w=80, h=80)
    _prime_canvas(p2)
    p2.ernst_decalcomania_pass(noise_seed=42, opacity=0.70)
    result2 = _get_canvas(p2)

    assert np.array_equal(result1, result2), (
        "Same noise_seed should produce identical decalcomania pattern"
    )


def test_s272_ernst_decalcomania_different_seeds():
    """Different seeds should produce different results."""
    p1 = _make_small_painter(w=80, h=80)
    _prime_canvas(p1)
    p1.ernst_decalcomania_pass(noise_seed=100, opacity=0.70, transfer_strength=0.40)
    result1 = _get_canvas(p1).copy()

    p2 = _make_small_painter(w=80, h=80)
    _prime_canvas(p2)
    p2.ernst_decalcomania_pass(noise_seed=999, opacity=0.70, transfer_strength=0.40)
    result2 = _get_canvas(p2)

    assert not np.array_equal(result1, result2), (
        "Different noise_seed values should produce different decalcomania patterns"
    )


# ── max_ernst catalog entry ────────────────────────────────────────────────────

def test_s272_max_ernst_in_catalog():
    from art_catalog import CATALOG
    assert "max_ernst" in CATALOG, "max_ernst should be in CATALOG"


def test_s272_max_ernst_artist_name():
    from art_catalog import get_style
    style = get_style("max_ernst")
    assert style.artist == "Max Ernst"


def test_s272_max_ernst_movement():
    from art_catalog import get_style
    style = get_style("max_ernst")
    assert "Surrealism" in style.movement or "Dada" in style.movement


def test_s272_max_ernst_palette_count():
    from art_catalog import get_style
    style = get_style("max_ernst")
    assert len(style.palette) >= 6, (
        f"Max Ernst palette should have at least 6 colors, got {len(style.palette)}"
    )


def test_s272_max_ernst_palette_rgb_range():
    from art_catalog import get_style
    style = get_style("max_ernst")
    for i, color in enumerate(style.palette):
        assert len(color) == 3, f"Palette color {i} should have 3 channels"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"Palette color {i} channel out of [0,1] range: {ch}"
            )


def test_s272_max_ernst_famous_works():
    from art_catalog import get_style
    style = get_style("max_ernst")
    assert len(style.famous_works) >= 3
    titles = [w[0] for w in style.famous_works]
    assert any("Europe" in t or "Rain" in t for t in titles), (
        "Famous works should include 'Europe After the Rain'"
    )


def test_s272_max_ernst_inspiration_mentions_decalcomania():
    from art_catalog import get_style
    style = get_style("max_ernst")
    assert "decalcomania" in style.inspiration.lower(), (
        "Inspiration should mention ernst_decalcomania_pass"
    )


def test_s272_max_ernst_get_style_roundtrip():
    from art_catalog import get_style, list_artists
    assert "max_ernst" in list_artists()
    style = get_style("max_ernst")
    assert style.artist == "Max Ernst"


# ── Combined pipeline smoke test ───────────────────────────────────────────────

def test_s272_full_pipeline_smoke():
    """Smoke test: both new passes run on a small canvas without error."""
    p = _make_small_painter(w=72, h=72)
    ref = _desert_reference(72, 72)
    p.tone_ground((0.20, 0.16, 0.10), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)

    p.paint_scumbling_veil_pass(
        dark_threshold=0.40,
        veil_lightness=0.20,
        coverage_density=0.60,
        opacity=0.50,
    )
    p.ernst_decalcomania_pass(
        pressure_scale=0.05,
        pressure_octaves=4,
        transfer_strength=0.25,
        opacity=0.65,
    )

    canvas = _get_canvas(p)
    assert canvas.shape == (72, 72, 4)
    assert canvas[:, :, 3].min() == 255, "Alpha channel should remain fully opaque"
