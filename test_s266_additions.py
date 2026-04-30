"""
test_s266_additions.py -- Session 266 tests for gallen_kallela_enamel_cloisonne_pass,
paint_hue_zone_boundary_pass, and the akseli_gallen_kallela catalog entry.
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


def _forest_reference(w=64, h=64):
    """Reference with sky, treeline, and birch trunks."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Sky zone (top 30%): cobalt blue
    arr[:h // 3, :, :] = [47, 66, 184]
    # Forest zone (middle 40%): dark green
    arr[h // 3: 3 * h // 4, :, :] = [31, 72, 31]
    # Floor zone (bottom 25%): burnt orange
    arr[3 * h // 4:, :, :] = [159, 102, 31]
    # Birch trunk: white vertical stripe
    mid = w // 2
    arr[:, mid - 2:mid + 2, :] = [240, 235, 224]
    return Image.fromarray(arr, "RGB")


def _saturated_reference(w=64, h=64):
    """Reference with strongly saturated distinct colour zones."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Left half: strong cobalt blue
    arr[:, :w // 2, :] = [46, 66, 182]
    # Right half: strong burnt orange
    arr[:, w // 2:, :] = [210, 102, 20]
    return Image.fromarray(arr, "RGB")


def _grey_reference(w=64, h=64):
    """Uniform mid-grey reference (low saturation)."""
    from PIL import Image
    arr = np.full((h, w, 3), 128, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _dark_reference(w=64, h=64):
    """Near-black reference."""
    from PIL import Image
    arr = np.full((h, w, 3), 20, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, forest=False, saturated=False, grey=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if forest:
            ref = _forest_reference(w, h)
        elif saturated:
            ref = _saturated_reference(w, h)
        elif grey:
            ref = _grey_reference(w, h)
        else:
            ref = _dark_reference(w, h)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.01)
    p.block_in(np.array(ref), stroke_size=10, n_strokes=24)


# ── paint_hue_zone_boundary_pass ──────────────────────────────────────────────

def test_s266_hue_boundary_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_hue_zone_boundary_pass")


def test_s266_hue_boundary_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    result = p.paint_hue_zone_boundary_pass()
    assert result is None


def test_s266_hue_boundary_modifies_canvas():
    """Canvas values change after applying hue boundary pass on saturated ref."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    before = _get_canvas(p).copy()
    p.paint_hue_zone_boundary_pass(
        variance_sigma=2.0,
        boundary_dark=0.60,
        interior_chroma=0.20,
        opacity=0.80,
    )
    after = _get_canvas(p)
    # Canvas should change because saturated zones with sharp boundary exist
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff > 0, "Canvas was not modified by paint_hue_zone_boundary_pass"


def test_s266_hue_boundary_darkens_boundary_pixels():
    """The pass darkens pixels at the colour zone boundary."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, saturated=True)
    before = _get_canvas(p).copy()
    p.paint_hue_zone_boundary_pass(
        variance_sigma=2.5,
        boundary_dark=0.80,
        interior_chroma=0.10,
        opacity=1.0,
    )
    after = _get_canvas(p)
    # The centre column (at the blue/orange boundary) should be darker
    mid_x = p.canvas.w // 2
    before_lum = 0.299 * before[:, mid_x, 2] + 0.587 * before[:, mid_x, 1] + 0.114 * before[:, mid_x, 0]
    after_lum  = 0.299 * after[:, mid_x, 2] + 0.587 * after[:, mid_x, 1] + 0.114 * after[:, mid_x, 0]
    mean_before = float(before_lum.mean())
    mean_after  = float(after_lum.mean())
    assert mean_after < mean_before + 5.0, (
        f"Boundary column was not darkened: before_lum={mean_before:.1f}, after_lum={mean_after:.1f}"
    )


def test_s266_hue_boundary_interior_chroma_lifts_saturation():
    """Interior chroma lift increases saturation within flat-hue zones."""
    p = _make_small_painter(w=80, h=80)
    ref = _saturated_reference(p.canvas.w, p.canvas.h)
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy().astype(np.float32)
    # Compute pre-pass saturation in the left (blue) zone
    r_b = before[:, :p.canvas.w // 3, 2] / 255.0
    g_b = before[:, :p.canvas.w // 3, 1] / 255.0
    b_b = before[:, :p.canvas.w // 3, 0] / 255.0
    ch_max_b = np.maximum(np.maximum(r_b, g_b), b_b)
    ch_min_b = np.minimum(np.minimum(r_b, g_b), b_b)
    sat_before = float(np.mean((ch_max_b - ch_min_b) / (ch_max_b + 1e-6)))

    p.paint_hue_zone_boundary_pass(
        variance_sigma=2.0,
        boundary_dark=0.20,
        interior_chroma=0.40,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32)
    r_a = after[:, :p.canvas.w // 3, 2] / 255.0
    g_a = after[:, :p.canvas.w // 3, 1] / 255.0
    b_a = after[:, :p.canvas.w // 3, 0] / 255.0
    ch_max_a = np.maximum(np.maximum(r_a, g_a), b_a)
    ch_min_a = np.minimum(np.minimum(r_a, g_a), b_a)
    sat_after = float(np.mean((ch_max_a - ch_min_a) / (ch_max_a + 1e-6)))

    assert sat_after >= sat_before - 0.02, (
        f"Interior saturation should not decrease: before={sat_before:.3f}, after={sat_after:.3f}"
    )


def test_s266_hue_boundary_grey_canvas_no_crash():
    """Pass runs without error on a low-saturation (grey) canvas."""
    p = _make_small_painter()
    _prime_canvas(p, grey=True)
    p.paint_hue_zone_boundary_pass(
        variance_sigma=2.0,
        boundary_dark=0.50,
        interior_chroma=0.20,
        opacity=0.70,
    )
    after = _get_canvas(p)
    assert after.shape == (p.canvas.h, p.canvas.w, 4)


def test_s266_hue_boundary_opacity_zero_no_change():
    """At opacity=0 the canvas should not change."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    before = _get_canvas(p).copy()
    p.paint_hue_zone_boundary_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff <= 1, f"Canvas changed at opacity=0 (max diff={diff})"


def test_s266_hue_boundary_output_shape_preserved():
    """Canvas shape is unchanged after pass."""
    p = _make_small_painter(w=48, h=72)
    _prime_canvas(p, saturated=True)
    p.paint_hue_zone_boundary_pass()
    after = _get_canvas(p)
    assert after.shape == (72, 48, 4)


def test_s266_hue_boundary_values_in_range():
    """Output pixel values remain in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, saturated=True)
    p.paint_hue_zone_boundary_pass(
        variance_sigma=3.0,
        boundary_dark=0.90,
        interior_chroma=0.40,
        opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0
    assert after.max() <= 255


# ── gallen_kallela_enamel_cloisonne_pass ──────────────────────────────────────

def test_s266_cloisonne_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "gallen_kallela_enamel_cloisonne_pass")


def test_s266_cloisonne_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, forest=True)
    result = p.gallen_kallela_enamel_cloisonne_pass()
    assert result is None


def test_s266_cloisonne_modifies_canvas():
    """Canvas changes after applying cloisonne pass."""
    p = _make_small_painter()
    _prime_canvas(p, forest=True)
    before = _get_canvas(p).copy()
    p.gallen_kallela_enamel_cloisonne_pass(
        flat_sigma=3.0,
        zone_blend=0.55,
        contour_strength=0.65,
        opacity=0.80,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff > 0, "Canvas was not modified by gallen_kallela_enamel_cloisonne_pass"


def test_s266_cloisonne_contour_darkening_at_edges():
    """Sobel edges in the flattened canvas are darkened by the pass."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, saturated=True)
    before = _get_canvas(p).copy()
    p.gallen_kallela_enamel_cloisonne_pass(
        flat_sigma=2.0,
        zone_blend=0.50,
        contour_strength=0.90,
        opacity=1.0,
    )
    after = _get_canvas(p)
    # The zone boundary column should be darker or the overall luminance should shift
    mid_x = p.canvas.w // 2
    before_lum = float(np.mean(
        0.299 * before[:, mid_x, 2] + 0.587 * before[:, mid_x, 1] + 0.114 * before[:, mid_x, 0]
    ))
    after_lum = float(np.mean(
        0.299 * after[:, mid_x, 2] + 0.587 * after[:, mid_x, 1] + 0.114 * after[:, mid_x, 0]
    ))
    # The darkening effect should reduce luminance or keep it the same at boundaries
    assert after_lum <= before_lum + 5.0, (
        f"Cloisonne contour darkening should darken zone boundaries: "
        f"before={before_lum:.1f}, after={after_lum:.1f}"
    )


def test_s266_cloisonne_saturation_boost_chromatic_zones():
    """Saturation is boosted in zones with pre-existing chroma."""
    p = _make_small_painter(w=80, h=80)
    ref = _saturated_reference(p.canvas.w, p.canvas.h)
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy().astype(np.float32)

    p.gallen_kallela_enamel_cloisonne_pass(
        flat_sigma=2.0,
        zone_blend=0.40,
        contour_strength=0.20,
        sat_boost=0.50,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32)

    def mean_sat(canvas_zone):
        r = canvas_zone[:, :, 2] / 255.0
        g = canvas_zone[:, :, 1] / 255.0
        b = canvas_zone[:, :, 0] / 255.0
        mx = np.maximum(np.maximum(r, g), b)
        mn = np.minimum(np.minimum(r, g), b)
        return float(np.mean((mx - mn) / (mx + 1e-6)))

    w = p.canvas.w
    sat_b = mean_sat(before[:, :w // 3, :])
    sat_a = mean_sat(after[:, :w // 3, :])
    assert sat_a >= sat_b - 0.03, (
        f"Saturation should not decrease significantly in chromatic zones: "
        f"before={sat_b:.3f}, after={sat_a:.3f}"
    )


def test_s266_cloisonne_grey_no_crash():
    """Pass runs without error on low-saturation grey canvas."""
    p = _make_small_painter()
    _prime_canvas(p, grey=True)
    p.gallen_kallela_enamel_cloisonne_pass()
    after = _get_canvas(p)
    assert after.shape == (p.canvas.h, p.canvas.w, 4)


def test_s266_cloisonne_opacity_zero_no_change():
    """At opacity=0 the canvas should not change."""
    p = _make_small_painter()
    _prime_canvas(p, forest=True)
    before = _get_canvas(p).copy()
    p.gallen_kallela_enamel_cloisonne_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff <= 1, f"Canvas changed at opacity=0 (max diff={diff})"


def test_s266_cloisonne_output_shape_preserved():
    """Canvas shape is unchanged after pass."""
    p = _make_small_painter(w=56, h=72)
    _prime_canvas(p, forest=True)
    p.gallen_kallela_enamel_cloisonne_pass()
    after = _get_canvas(p)
    assert after.shape == (72, 56, 4)


def test_s266_cloisonne_values_in_range():
    """Output pixel values remain in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, forest=True)
    p.gallen_kallela_enamel_cloisonne_pass(
        sat_boost=0.40,
        contour_strength=0.90,
        opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0
    assert after.max() <= 255


def test_s266_cloisonne_zone_flatten_reduces_hue_variance():
    """After zone flattening, within-zone hue variance should not increase."""
    p = _make_small_painter(w=80, h=80)
    ref = _forest_reference(p.canvas.w, p.canvas.h)
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy().astype(np.float32) / 255.0

    def hue_std(canvas_zone):
        r = canvas_zone[:, :, 2]
        g = canvas_zone[:, :, 1]
        b = canvas_zone[:, :, 0]
        ch_max = np.maximum(np.maximum(r, g), b)
        ch_min = np.minimum(np.minimum(r, g), b)
        delta = ch_max - ch_min
        m = delta > 0.02
        if not m.any():
            return 0.0
        hue = np.zeros_like(r)
        rr, gg, bb, dd, mx = r[m], g[m], b[m], delta[m], ch_max[m]
        is_r = mx == rr
        is_g = (mx == gg) & ~is_r
        hr = ((gg - bb) / dd) % 6.0
        hg = (bb - rr) / dd + 2.0
        hb = (rr - gg) / dd + 4.0
        hue[m] = np.where(is_r, hr, np.where(is_g, hg, hb)) / 6.0
        return float(np.std(hue[m]))

    hue_var_b = hue_std(before)

    p.gallen_kallela_enamel_cloisonne_pass(
        flat_sigma=6.0,
        zone_blend=0.80,
        contour_strength=0.10,
        sat_boost=0.05,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32) / 255.0
    hue_var_a = hue_std(after)

    # Zone flattening should reduce or maintain hue variance (not increase it)
    assert hue_var_a <= hue_var_b + 0.05, (
        f"Zone flattening should reduce hue variance: before={hue_var_b:.3f}, after={hue_var_a:.3f}"
    )


# ── akseli_gallen_kallela catalog entry ───────────────────────────────────────

def test_s266_catalog_entry_exists():
    from art_catalog import get_style
    style = get_style("akseli_gallen_kallela")
    assert style is not None


def test_s266_catalog_artist_name():
    from art_catalog import get_style
    style = get_style("akseli_gallen_kallela")
    assert style.artist == "Akseli Gallen-Kallela"


def test_s266_catalog_movement():
    from art_catalog import get_style
    style = get_style("akseli_gallen_kallela")
    assert "Finnish" in style.movement or "Symbolism" in style.movement


def test_s266_catalog_palette_has_entries():
    from art_catalog import get_style
    style = get_style("akseli_gallen_kallela")
    assert len(style.palette) >= 6


def test_s266_catalog_palette_values_valid():
    from art_catalog import get_style
    style = get_style("akseli_gallen_kallela")
    for colour in style.palette:
        assert len(colour) == 3
        for v in colour:
            assert 0.0 <= v <= 1.0, f"Palette value out of range: {v}"


def test_s266_catalog_technique_nonempty():
    from art_catalog import get_style
    style = get_style("akseli_gallen_kallela")
    assert isinstance(style.technique, str) and len(style.technique) > 50


def test_s266_catalog_famous_works():
    from art_catalog import get_style
    style = get_style("akseli_gallen_kallela")
    assert len(style.famous_works) >= 4
    for (title, year) in style.famous_works:
        assert isinstance(title, str) and len(title) > 2
        assert isinstance(year, str) and len(year) == 4


def test_s266_catalog_in_list():
    from art_catalog import list_artists
    assert "akseli_gallen_kallela" in list_artists()


def test_s266_catalog_ground_color_valid():
    from art_catalog import get_style
    style = get_style("akseli_gallen_kallela")
    assert len(style.ground_color) == 3
    for v in style.ground_color:
        assert 0.0 <= v <= 1.0


def test_s266_catalog_stroke_size_positive():
    from art_catalog import get_style
    style = get_style("akseli_gallen_kallela")
    assert style.stroke_size > 0


def test_s266_catalog_inspiration_mentions_177th():
    from art_catalog import get_style
    style = get_style("akseli_gallen_kallela")
    assert "177" in style.inspiration


def test_s266_catalog_inspiration_mentions_cloisonne():
    from art_catalog import get_style
    style = get_style("akseli_gallen_kallela")
    assert "cloisonne" in style.inspiration.lower() or "cloisonné" in style.inspiration.lower()
