"""
test_s268_additions.py -- Session 268 tests for paint_depth_atmosphere_pass,
zao_wou_ki_ink_atmosphere_pass, and the zao_wou_ki catalog entry.
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


def _gorge_reference(w=64, h=64):
    """Reference with warm upper zone and dark lower zone (gorge layout)."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Upper zone: warm gold/sky
    arr[:int(h * 0.40), :, :] = [240, 210, 90]
    # Mid zone: mist white/amber
    arr[int(h * 0.40):int(h * 0.60), :, :] = [220, 200, 160]
    # Lower zone: deep blue-black gorge
    arr[int(h * 0.60):, :, :] = [20, 18, 40]
    # Add a bright center spot in upper zone
    cy, cx = int(h * 0.25), int(w * 0.50)
    for dy in range(-6, 7):
        for dx in range(-6, 7):
            if dy*dy + dx*dx <= 36:
                yy, xx = cy + dy, cx + dx
                if 0 <= yy < h and 0 <= xx < w:
                    arr[yy, xx, :] = [250, 230, 120]
    return Image.fromarray(arr, "RGB")


def _gradient_reference(w=64, h=64):
    """Horizontal luminance gradient (left=dark, right=bright)."""
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
    return Image.fromarray(np.full((h, w, 3), 128, dtype=np.uint8), "RGB")


def _prime_canvas(p, ref=None, *, gorge=False, gradient=False, grey=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if gorge:
            ref = _gorge_reference(w, h)
        elif gradient:
            ref = _gradient_reference(w, h)
        elif grey:
            ref = _mid_grey_reference(w, h)
        else:
            ref = _gorge_reference(w, h)
    p.tone_ground((0.08, 0.06, 0.18), texture_strength=0.01)
    p.block_in(np.array(ref), stroke_size=10, n_strokes=28)


# ── paint_depth_atmosphere_pass ───────────────────────────────────────────────

def test_s268_depth_atm_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_depth_atmosphere_pass")


def test_s268_depth_atm_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, gorge=True)
    result = p.paint_depth_atmosphere_pass()
    assert result is None


def test_s268_depth_atm_modifies_canvas():
    """Canvas changes after applying depth atmosphere pass."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, gorge=True)
    before = _get_canvas(p).copy()
    p.paint_depth_atmosphere_pass(
        max_haze=0.40,
        opacity=0.90,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff > 0, "Canvas was not modified by paint_depth_atmosphere_pass"


def test_s268_depth_atm_top_less_hazed_than_vertical_middle():
    """
    Vertical depth signal: higher in canvas (lower y index) = more distant.
    With vertical_weight > 0, the upper half of the canvas should receive
    more haze than the very bottom row (which is 'near' foreground).
    """
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, grey=True)

    before = _get_canvas(p).copy().astype(np.float32)
    b_bottom = before[-4:, :, 2].mean()   # bottom strip blue channel before

    p.paint_depth_atmosphere_pass(
        haze_color=(0.1, 0.1, 0.9),    # strongly blue haze -- easy to detect
        depth_sigma=4.0,
        max_haze=0.55,
        vertical_weight=1.0,
        contrast_weight=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32)
    # Upper rows should have moved toward haze_blue more than bottom rows
    blue_top = after[:4, :, 2].mean()    # BGRA: channel 2 is red (in BGRA), 0 is blue
    blue_bottom = after[-4:, :, 2].mean()
    # Because haze_color is strongly blue, top (distant) should have MORE blue
    # channel 0 is B in BGRA, channel 2 is R
    # haze_color=(0.1, 0.1, 0.9) means r=0.1, g=0.1, b=0.9
    # In BGRA: buf[:,:,0] = blue, buf[:,:,1] = green, buf[:,:,2] = red
    blue_channel_top = after[:4, :, 0].mean()
    blue_channel_bottom = after[-4:, :, 0].mean()
    # Top rows should be bluer (more haze) than bottom rows on a grey canvas
    # with vertical_weight=1.0
    assert blue_channel_top >= blue_channel_bottom - 3.0, (
        f"Upper canvas should have more blue haze than bottom: "
        f"top_blue={blue_channel_top:.1f}, bot_blue={blue_channel_bottom:.1f}"
    )


def test_s268_depth_atm_opacity_zero_no_change():
    """At opacity=0 the canvas should not change."""
    p = _make_small_painter()
    _prime_canvas(p, gorge=True)
    before = _get_canvas(p).copy()
    p.paint_depth_atmosphere_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff <= 1, f"Canvas changed at opacity=0 (max diff={diff})"


def test_s268_depth_atm_output_shape_preserved():
    """Canvas shape is unchanged after pass."""
    p = _make_small_painter(w=56, h=80)
    _prime_canvas(p, gorge=True)
    p.paint_depth_atmosphere_pass()
    after = _get_canvas(p)
    assert after.shape == (80, 56, 4)


def test_s268_depth_atm_values_in_range():
    """Output pixel values remain in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, gorge=True)
    p.paint_depth_atmosphere_pass(max_haze=0.50, opacity=1.0)
    after = _get_canvas(p)
    assert after.min() >= 0
    assert after.max() <= 255


def test_s268_depth_atm_haze_lightens_dark_upper_canvas():
    """Upper dark pixels should become lighter (toward haze color) after pass."""
    p = _make_small_painter(w=64, h=80)
    # Build a canvas that is dark in the upper zone
    from PIL import Image
    dark_arr = np.zeros((80, 64, 3), dtype=np.uint8)
    dark_arr[:30, :, :] = [18, 16, 22]   # dark upper
    dark_arr[30:, :, :] = [200, 180, 90]  # bright lower
    _prime_canvas(p, ref=Image.fromarray(dark_arr, "RGB"))
    before = _get_canvas(p).copy().astype(np.float32)
    lum_top_before = before[:12, :, :3].mean()

    p.paint_depth_atmosphere_pass(
        haze_color=(0.76, 0.82, 0.92),
        max_haze=0.42,
        vertical_weight=1.0,
        contrast_weight=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32)
    lum_top_after = after[:12, :, :3].mean()
    assert lum_top_after >= lum_top_before - 2.0, (
        f"Upper dark pixels should be lightened by haze: "
        f"before={lum_top_before:.1f}, after={lum_top_after:.1f}"
    )


def test_s268_depth_atm_non_square():
    """Pass handles non-square canvas."""
    p = _make_small_painter(w=52, h=80)
    _prime_canvas(p, gorge=True)
    p.paint_depth_atmosphere_pass()
    after = _get_canvas(p)
    assert after.shape == (80, 52, 4)


# ── zao_wou_ki_ink_atmosphere_pass ────────────────────────────────────────────

def test_s268_zao_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "zao_wou_ki_ink_atmosphere_pass")


def test_s268_zao_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, gorge=True)
    result = p.zao_wou_ki_ink_atmosphere_pass()
    assert result is None


def test_s268_zao_modifies_canvas():
    """Canvas changes after applying Zao Wou-Ki pass."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, gorge=True)
    before = _get_canvas(p).copy()
    p.zao_wou_ki_ink_atmosphere_pass(
        glow_strength=0.30,
        vignette_strength=0.40,
        opacity=0.85,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff > 0, "Canvas was not modified by zao_wou_ki_ink_atmosphere_pass"


def test_s268_zao_luminous_center_brightened():
    """The brightest region of the canvas should become brighter after pass."""
    p = _make_small_painter(w=80, h=80)
    ref = _gorge_reference(p.canvas.w, p.canvas.h)
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy().astype(np.float32)

    # Locate the brightest region (upper center of the gorge reference)
    lum_before = (0.299 * before[:, :, 2] +
                  0.587 * before[:, :, 1] +
                  0.114 * before[:, :, 0])
    peak_idx = int(np.argmax(lum_before))
    cy_pk = peak_idx // p.canvas.w
    cx_pk = peak_idx % p.canvas.w

    # Sample a region around the peak
    r0 = max(0, cy_pk - 8)
    r1 = min(p.canvas.h, cy_pk + 9)
    c0 = max(0, cx_pk - 8)
    c1 = min(p.canvas.w, cx_pk + 9)
    lum_peak_before = float(lum_before[r0:r1, c0:c1].mean())

    p.zao_wou_ki_ink_atmosphere_pass(
        glow_sigma=0.22,
        glow_strength=0.35,
        vignette_strength=0.38,
        ink_n_strokes=12,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32)
    lum_after = (0.299 * after[:, :, 2] +
                 0.587 * after[:, :, 1] +
                 0.114 * after[:, :, 0])
    lum_peak_after = float(lum_after[r0:r1, c0:c1].mean())

    assert lum_peak_after >= lum_peak_before - 5.0, (
        f"Luminous center should not darken after glow pass: "
        f"before={lum_peak_before:.1f}, after={lum_peak_after:.1f}"
    )


def test_s268_zao_corners_darkened():
    """Corners of the canvas should be darker than the canvas center after pass."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, grey=True)  # uniform grey so any change is from pass
    p.zao_wou_ki_ink_atmosphere_pass(
        glow_strength=0.05,          # low glow to isolate vignette effect
        vignette_strength=0.55,
        vignette_color=(0.02, 0.03, 0.08),
        ink_n_strokes=0,             # no strokes
        opacity=1.0,
    )
    after = _get_canvas(p).astype(np.float32)
    lum_after = (0.299 * after[:, :, 2] +
                 0.587 * after[:, :, 1] +
                 0.114 * after[:, :, 0])
    # Corner mean vs center mean
    h, w = p.canvas.h, p.canvas.w
    corner_size = max(8, w // 8)
    corner_lum = np.mean([
        lum_after[:corner_size, :corner_size].mean(),
        lum_after[:corner_size, -corner_size:].mean(),
        lum_after[-corner_size:, :corner_size].mean(),
        lum_after[-corner_size:, -corner_size:].mean(),
    ])
    center_margin = corner_size
    center_lum = lum_after[
        h//2 - center_margin : h//2 + center_margin,
        w//2 - center_margin : w//2 + center_margin
    ].mean()
    assert corner_lum < center_lum + 8.0, (
        f"Corners should be darker than center after vignette: "
        f"corner_lum={corner_lum:.1f}, center_lum={center_lum:.1f}"
    )


def test_s268_zao_opacity_zero_no_change():
    """At opacity=0 the canvas should not change."""
    p = _make_small_painter()
    _prime_canvas(p, gorge=True)
    before = _get_canvas(p).copy()
    p.zao_wou_ki_ink_atmosphere_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(np.int32) - after.astype(np.int32)).max()
    assert diff <= 1, f"Canvas changed at opacity=0 (max diff={diff})"


def test_s268_zao_output_shape_preserved():
    """Canvas shape is unchanged after pass."""
    p = _make_small_painter(w=56, h=80)
    _prime_canvas(p, gorge=True)
    p.zao_wou_ki_ink_atmosphere_pass()
    after = _get_canvas(p)
    assert after.shape == (80, 56, 4)


def test_s268_zao_values_in_range():
    """Output pixel values remain in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, gorge=True)
    p.zao_wou_ki_ink_atmosphere_pass(
        glow_strength=0.40,
        vignette_strength=0.55,
        ink_n_strokes=20,
        opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0
    assert after.max() <= 255


def test_s268_zao_non_square_canvas():
    """Pass handles non-square canvas without shape errors."""
    p = _make_small_painter(w=52, h=80)
    _prime_canvas(p, gorge=True)
    p.zao_wou_ki_ink_atmosphere_pass()
    after = _get_canvas(p)
    assert after.shape == (80, 52, 4)


def test_s268_zao_no_ink_strokes_runs():
    """Pass with ink_n_strokes=0 completes without error."""
    p = _make_small_painter()
    _prime_canvas(p, gorge=True)
    p.zao_wou_ki_ink_atmosphere_pass(ink_n_strokes=0)
    after = _get_canvas(p)
    assert after.shape == (p.canvas.h, p.canvas.w, 4)


def test_s268_zao_grey_canvas_no_crash():
    """Pass runs on a grey (low-saturation) canvas without error."""
    p = _make_small_painter()
    _prime_canvas(p, grey=True)
    p.zao_wou_ki_ink_atmosphere_pass()
    after = _get_canvas(p)
    assert after.shape == (p.canvas.h, p.canvas.w, 4)


# ── zao_wou_ki catalog entry ──────────────────────────────────────────────────

def test_s268_catalog_entry_exists():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    assert style is not None


def test_s268_catalog_artist_name():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    assert style.artist == "Zao Wou-Ki"


def test_s268_catalog_movement():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    assert ("Lyrical" in style.movement or "Abstract" in style.movement
            or "Chinese" in style.movement)


def test_s268_catalog_nationality():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    assert "French" in style.nationality or "Chinese" in style.nationality


def test_s268_catalog_palette_has_entries():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    assert len(style.palette) >= 6


def test_s268_catalog_palette_values_valid():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    for colour in style.palette:
        assert len(colour) == 3
        for v in colour:
            assert 0.0 <= v <= 1.0, f"Palette value out of range: {v}"


def test_s268_catalog_technique_nonempty():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    assert isinstance(style.technique, str) and len(style.technique) > 50


def test_s268_catalog_famous_works():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    assert len(style.famous_works) >= 4
    for (title, year) in style.famous_works:
        assert isinstance(title, str) and len(title) > 2
        assert isinstance(year, str) and len(year) == 4


def test_s268_catalog_in_list():
    from art_catalog import list_artists
    assert "zao_wou_ki" in list_artists()


def test_s268_catalog_ground_color_valid():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    assert len(style.ground_color) == 3
    for v in style.ground_color:
        assert 0.0 <= v <= 1.0


def test_s268_catalog_stroke_size_positive():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    assert style.stroke_size > 0


def test_s268_catalog_inspiration_mentions_179th():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    assert "179" in style.inspiration


def test_s268_catalog_inspiration_mentions_zao():
    from art_catalog import get_style
    style = get_style("zao_wou_ki")
    assert "zao_wou_ki" in style.inspiration.lower() or "ink" in style.inspiration.lower()
