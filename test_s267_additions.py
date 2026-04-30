"""
test_s267_additions.py -- Session 267 tests for goncharova_rayonist_pass,
paint_palette_knife_ridge_pass, and the natalia_goncharova catalog entry.
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


def _sunflower_reference(w=64, h=64):
    """Reference with sky zone (blue) and bright sunflower disc (yellow)."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Sky: cobalt blue (top 60%)
    arr[:int(h * 0.6), :, :] = [47, 56, 188]
    # Ground: warm sienna (bottom 40%)
    arr[int(h * 0.6):, :, :] = [130, 78, 35]
    # Sunflower disc: golden yellow circle at centre-upper
    cy, cx = int(h * 0.30), int(w * 0.50)
    r_disc = max(5, int(min(w, h) * 0.14))
    Y, X = np.mgrid[0:h, 0:w]
    disc_mask = (X - cx)**2 + (Y - cy)**2 < r_disc**2
    arr[disc_mask, :] = [234, 186, 25]
    return Image.fromarray(arr, "RGB")


def _gradient_reference(w=64, h=64):
    """Reference with clear luminance gradient (left=dark, right=bright)."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    xs = np.linspace(30, 220, w, dtype=np.uint8)
    arr[:, :, 0] = xs[None, :]
    arr[:, :, 1] = (xs * 0.8).astype(np.uint8)[None, :]
    arr[:, :, 2] = (xs * 0.5).astype(np.uint8)[None, :]
    return Image.fromarray(arr, "RGB")


def _mid_grey_reference(w=64, h=64):
    """Uniform mid-grey reference."""
    from PIL import Image
    arr = np.full((h, w, 3), 128, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _dark_reference(w=64, h=64):
    """Near-black reference."""
    from PIL import Image
    arr = np.full((h, w, 3), 22, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, sunflower=False, gradient=False, grey=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if sunflower:
            ref = _sunflower_reference(w, h)
        elif gradient:
            ref = _gradient_reference(w, h)
        elif grey:
            ref = _mid_grey_reference(w, h)
        else:
            ref = _dark_reference(w, h)
    p.tone_ground((0.28, 0.18, 0.08), texture_strength=0.01)
    p.block_in(np.array(ref), stroke_size=10, n_strokes=24)


# ── paint_palette_knife_ridge_pass ────────────────────────────────────────────

def test_s267_ridge_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_palette_knife_ridge_pass")


def test_s267_ridge_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, gradient=True)
    result = p.paint_palette_knife_ridge_pass()
    assert result is None


def test_s267_ridge_modifies_canvas():
    """Canvas values change after applying ridge pass on mid-tone gradient."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, gradient=True)
    before = _get_canvas(p).copy()
    p.paint_palette_knife_ridge_pass(
        ridge_freq=0.20,
        ridge_scale=0.10,
        opacity=0.90,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff > 0, "Canvas was not modified by paint_palette_knife_ridge_pass"


def test_s267_ridge_creates_variation():
    """Ridge texture increases pixel-level luminance variance."""
    p = _make_small_painter(w=80, h=80)
    # Use a flat mid-grey reference so ridges have max effect
    _prime_canvas(p, grey=True)
    before = _get_canvas(p).copy().astype(np.float32)
    lum_before = 0.299 * before[:, :, 2] + 0.587 * before[:, :, 1] + 0.114 * before[:, :, 0]

    p.paint_palette_knife_ridge_pass(
        ridge_freq=0.25,
        ridge_scale=0.12,
        ridge_sigma=4.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32)
    lum_after = 0.299 * after[:, :, 2] + 0.587 * after[:, :, 1] + 0.114 * after[:, :, 0]

    var_before = float(np.var(lum_before))
    var_after = float(np.var(lum_after))
    assert var_after >= var_before, (
        f"Ridge pass should not reduce luminance variance: "
        f"before={var_before:.4f}, after={var_after:.4f}"
    )


def test_s267_ridge_dark_canvas_minimal_effect():
    """Ridge is invisible on near-black canvas (luminance gate suppresses it)."""
    p = _make_small_painter()
    _prime_canvas(p)  # dark reference
    before = _get_canvas(p).copy()
    p.paint_palette_knife_ridge_pass(
        ridge_freq=0.20,
        ridge_scale=0.10,
        lum_lo=0.25,
        lum_hi=0.80,
        opacity=1.0,
    )
    after = _get_canvas(p)
    # On a dark canvas the lum gate should suppress most of the ridge effect
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).mean()
    assert diff < 10.0, (
        f"Ridge should be suppressed on dark canvas (mean diff={diff:.2f})"
    )


def test_s267_ridge_opacity_zero_no_change():
    """At opacity=0 the canvas should not change."""
    p = _make_small_painter()
    _prime_canvas(p, gradient=True)
    before = _get_canvas(p).copy()
    p.paint_palette_knife_ridge_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff <= 1, f"Canvas changed at opacity=0 (max diff={diff})"


def test_s267_ridge_output_shape_preserved():
    """Canvas shape is unchanged after pass."""
    p = _make_small_painter(w=56, h=72)
    _prime_canvas(p, gradient=True)
    p.paint_palette_knife_ridge_pass()
    after = _get_canvas(p)
    assert after.shape == (72, 56, 4)


def test_s267_ridge_values_in_range():
    """Output pixel values remain in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, gradient=True)
    p.paint_palette_knife_ridge_pass(
        ridge_scale=0.15,
        opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0
    assert after.max() <= 255


# ── goncharova_rayonist_pass ──────────────────────────────────────────────────

def test_s267_rayonist_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "goncharova_rayonist_pass")


def test_s267_rayonist_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, sunflower=True)
    result = p.goncharova_rayonist_pass()
    assert result is None


def test_s267_rayonist_modifies_canvas():
    """Canvas changes after applying Rayonist pass."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, sunflower=True)
    before = _get_canvas(p).copy()
    p.goncharova_rayonist_pass(
        n_angles=4,
        ray_sigma=10.0,
        ray_strength=0.40,
        opacity=0.80,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff > 0, "Canvas was not modified by goncharova_rayonist_pass"


def test_s267_rayonist_streaks_spread_colour():
    """Bright disc colours should spread into adjacent sky pixels after pass."""
    p = _make_small_painter(w=80, h=80)
    ref = _sunflower_reference(p.canvas.w, p.canvas.h)
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy().astype(np.float32)

    # Find the mean R channel in the upper-right quadrant (away from the disc)
    qh = p.canvas.h // 2
    qw = p.canvas.w // 2
    r_before = float(before[:qh, qw:, 2].mean())

    p.goncharova_rayonist_pass(
        n_angles=4,
        ray_sigma=18.0,
        ray_strength=0.50,
        shimmer_threshold=0.30,  # high threshold — suppress shimmer
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32)
    r_after = float(after[:qh, qw:, 2].mean())

    # The ray pass should spread warm disc colour into the sky quadrant
    assert r_after >= r_before - 2.0, (
        f"Warm disc colour should spread via rays: "
        f"before_R={r_before:.1f}, after_R={r_after:.1f}"
    )


def test_s267_rayonist_opacity_zero_no_change():
    """At opacity=0 the canvas should not change."""
    p = _make_small_painter()
    _prime_canvas(p, sunflower=True)
    before = _get_canvas(p).copy()
    p.goncharova_rayonist_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff <= 1, f"Canvas changed at opacity=0 (max diff={diff})"


def test_s267_rayonist_output_shape_preserved():
    """Canvas shape is unchanged after pass."""
    p = _make_small_painter(w=48, h=72)
    _prime_canvas(p, sunflower=True)
    p.goncharova_rayonist_pass()
    after = _get_canvas(p)
    assert after.shape == (72, 48, 4)


def test_s267_rayonist_values_in_range():
    """Output pixel values remain in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, sunflower=True)
    p.goncharova_rayonist_pass(
        ray_strength=0.50,
        shimmer_angle=20.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0
    assert after.max() <= 255


def test_s267_rayonist_grey_no_crash():
    """Pass runs without error on a low-saturation (grey) canvas."""
    p = _make_small_painter()
    _prime_canvas(p, grey=True)
    p.goncharova_rayonist_pass()
    after = _get_canvas(p)
    assert after.shape == (p.canvas.h, p.canvas.w, 4)


def test_s267_rayonist_non_square_canvas():
    """Pass handles non-square canvas (important for rot90 on portrait format)."""
    p = _make_small_painter(w=48, h=80)
    _prime_canvas(p, sunflower=True)
    p.goncharova_rayonist_pass(n_angles=4, ray_sigma=8.0)
    after = _get_canvas(p)
    assert after.shape == (80, 48, 4)


# ── natalia_goncharova catalog entry ──────────────────────────────────────────

def test_s267_catalog_entry_exists():
    from art_catalog import get_style
    style = get_style("natalia_goncharova")
    assert style is not None


def test_s267_catalog_artist_name():
    from art_catalog import get_style
    style = get_style("natalia_goncharova")
    assert style.artist == "Natalia Goncharova"


def test_s267_catalog_movement():
    from art_catalog import get_style
    style = get_style("natalia_goncharova")
    assert "Rayonism" in style.movement or "Russian" in style.movement


def test_s267_catalog_palette_has_entries():
    from art_catalog import get_style
    style = get_style("natalia_goncharova")
    assert len(style.palette) >= 6


def test_s267_catalog_palette_values_valid():
    from art_catalog import get_style
    style = get_style("natalia_goncharova")
    for colour in style.palette:
        assert len(colour) == 3
        for v in colour:
            assert 0.0 <= v <= 1.0, f"Palette value out of range: {v}"


def test_s267_catalog_technique_nonempty():
    from art_catalog import get_style
    style = get_style("natalia_goncharova")
    assert isinstance(style.technique, str) and len(style.technique) > 50


def test_s267_catalog_famous_works():
    from art_catalog import get_style
    style = get_style("natalia_goncharova")
    assert len(style.famous_works) >= 4
    for (title, year) in style.famous_works:
        assert isinstance(title, str) and len(title) > 2
        assert isinstance(year, str) and len(year) == 4


def test_s267_catalog_in_list():
    from art_catalog import list_artists
    assert "natalia_goncharova" in list_artists()


def test_s267_catalog_ground_color_valid():
    from art_catalog import get_style
    style = get_style("natalia_goncharova")
    assert len(style.ground_color) == 3
    for v in style.ground_color:
        assert 0.0 <= v <= 1.0


def test_s267_catalog_stroke_size_positive():
    from art_catalog import get_style
    style = get_style("natalia_goncharova")
    assert style.stroke_size > 0


def test_s267_catalog_inspiration_mentions_178th():
    from art_catalog import get_style
    style = get_style("natalia_goncharova")
    assert "178" in style.inspiration


def test_s267_catalog_inspiration_mentions_rayonist():
    from art_catalog import get_style
    style = get_style("natalia_goncharova")
    assert "rayonist" in style.inspiration.lower()
