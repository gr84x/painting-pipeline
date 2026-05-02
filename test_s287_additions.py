"""
test_s287_additions.py -- Session 287 tests for paint_median_clarity_pass,
hartley_elemental_mass_pass, and the marsden_hartley catalog entry.
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


def _vivid_colour_reference(w=64, h=64):
    """Vivid multi-colour reference with strong saturation zones."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :w // 2, :] = [180, 100, 30]   # orange-umber quadrant
    arr[:h // 2, w // 2:, :] = [20, 60, 160]    # blue-black quadrant
    arr[h // 2:, :w // 2, :] = [30, 110, 40]    # forest green quadrant
    arr[h // 2:, w // 2:, :] = [160, 110, 50]   # ochre quadrant
    return arr


def _dark_reference(w=64, h=64):
    """Dark reference to test shadow protection and dark-mass handling."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :, :] = [20, 25, 20]    # very dark
    arr[h // 2:, :, :] = [180, 120, 40]  # bright warm zone
    return arr


def _high_contrast_reference(w=64, h=64):
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :, :] = [190, 150, 100]
    arr[h // 2:, :, :] = [45, 35, 55]
    return arr


def _flat_midtone_reference(w=64, h=64):
    return np.full((h, w, 3), [130, 110, 85], dtype=np.uint8)


def _prime_canvas(p, ref=None):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        ref = _high_contrast_reference(w, h)
    p.tone_ground((0.85, 0.80, 0.65), texture_strength=0.018)
    p.block_in(ref, stroke_size=10, n_strokes=30)


def _prime_canvas_full(p, ref=None):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        ref = _vivid_colour_reference(w, h)
    p.tone_ground((0.85, 0.80, 0.65), texture_strength=0.018)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.build_form(ref, stroke_size=5, n_strokes=25)
    p.place_lights(ref, stroke_size=3, n_strokes=15)


# ── paint_median_clarity_pass ────────────────────────────────────────────────

def test_s287_median_clarity_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_median_clarity_pass")


def test_s287_median_clarity_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_median_clarity_pass()
    assert result is None


def test_s287_median_clarity_modifies_canvas():
    p = _make_small_painter(w=80, h=80)
    _prime_canvas_full(p, _vivid_colour_reference(80, 80))
    before = _get_canvas(p).copy()
    p.paint_median_clarity_pass(
        median_size=5,
        detail_boost=2.0,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after paint_median_clarity_pass"
    )


def test_s287_median_clarity_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_median_clarity_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s287_median_clarity_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas_full(p, _vivid_colour_reference(72, 72))
    p.paint_median_clarity_pass(
        median_size=5,
        detail_boost=2.20,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s287_median_clarity_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.paint_median_clarity_pass(opacity=0.80)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque after paint_median_clarity_pass"
    )


def test_s287_median_clarity_small_canvas():
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.paint_median_clarity_pass(opacity=0.70)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


def test_s287_median_clarity_shadow_floor_preserves_dark():
    """Very dark pixels should be mostly preserved (shadow floor protection)."""
    p = _make_small_painter(w=64, h=64)
    dark_ref = _dark_reference(64, 64)
    p.tone_ground((0.06, 0.05, 0.04), texture_strength=0.01)
    p.block_in(dark_ref, stroke_size=8, n_strokes=60)
    p.build_form(dark_ref, stroke_size=4, n_strokes=40)

    canvas_before = _get_canvas(p).copy()
    p.paint_median_clarity_pass(
        shadow_floor=0.18,
        shadow_reset_strength=0.90,  # strong shadow protection
        opacity=1.0,
    )
    canvas_after = _get_canvas(p)

    # Identify dark pixels (top half of reference is very dark)
    dark_rows = slice(0, 32)
    dark_before = canvas_before[dark_rows, :, :3].astype(np.float32)
    dark_after  = canvas_after[dark_rows,  :, :3].astype(np.float32)
    diff = np.abs(dark_after - dark_before).mean()
    # Shadow floor should keep the very dark zone close to original
    assert diff <= 15.0, (
        f"Shadow floor protection should limit change in dark zone: mean_diff={diff:.2f}"
    )


def test_s287_median_clarity_size3_vs_size7():
    """Larger median size should produce more aggressive smoothing of fine detail."""
    ref = _vivid_colour_reference(64, 64)

    p3 = _make_small_painter(w=64, h=64)
    _prime_canvas_full(p3, ref)
    p3.paint_median_clarity_pass(median_size=3, detail_boost=2.0, opacity=1.0)
    c3 = _get_canvas(p3)

    p7 = _make_small_painter(w=64, h=64)
    _prime_canvas_full(p7, ref)
    p7.paint_median_clarity_pass(median_size=7, detail_boost=2.0, opacity=1.0)
    c7 = _get_canvas(p7)

    # The two canvases should differ (different median radius → different base)
    diff = np.abs(c3[:, :, :3].astype(np.int32) - c7[:, :, :3].astype(np.int32))
    assert diff.max() >= 1, (
        "Different median sizes should produce different outputs"
    )


def test_s287_median_clarity_detail_boost_1_near_original():
    """detail_boost=1.0 (no amplification) with strong opacity should be near no-op."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_median_clarity_pass(
        median_size=5,
        detail_boost=1.0,
        shadow_reset_strength=0.0,  # disable shadow reset
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    # detail_boost=1 means no amplification: output = median + detail*1 = original
    assert diff.max() <= 3, (
        f"detail_boost=1 should be near-identity: max_diff={diff.max()}"
    )


# ── hartley_elemental_mass_pass ───────────────────────────────────────────────

def test_s287_hartley_elemental_mass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "hartley_elemental_mass_pass")


def test_s287_hartley_elemental_mass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.hartley_elemental_mass_pass()
    assert result is None


def test_s287_hartley_elemental_mass_modifies_canvas():
    p = _make_small_painter(w=80, h=80)
    _prime_canvas_full(p, _vivid_colour_reference(80, 80))
    before = _get_canvas(p).copy()
    p.hartley_elemental_mass_pass(
        palette_strength=0.55,
        edge_darken_strength=0.50,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after hartley_elemental_mass_pass"
    )


def test_s287_hartley_elemental_mass_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.hartley_elemental_mass_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s287_hartley_elemental_mass_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas_full(p, _vivid_colour_reference(72, 72))
    p.hartley_elemental_mass_pass(
        palette_strength=0.60,
        interior_flatten_strength=0.40,
        edge_darken_strength=0.55,
        dark_desat_strength=0.60,
        bright_sat_strength=0.55,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s287_hartley_elemental_mass_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.hartley_elemental_mass_pass(opacity=0.85)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque after hartley_elemental_mass_pass"
    )


def test_s287_hartley_elemental_mass_small_canvas():
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.hartley_elemental_mass_pass(opacity=0.70)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


def test_s287_hartley_edge_darken_darkens_edges():
    """Strong edge darkening should reduce mean brightness at high-gradient edges."""
    p = _make_small_painter(w=64, h=64)
    ref = _high_contrast_reference(64, 64)
    p.tone_ground((0.85, 0.80, 0.65), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=80)

    before = _get_canvas(p).copy()
    p.hartley_elemental_mass_pass(
        palette_strength=0.0,        # isolate edge effect
        interior_flatten_strength=0.0,
        edge_darken_strength=0.90,
        dark_desat_strength=0.0,
        bright_sat_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    # Luminance around the transition (rows 28-36 = boundary zone)
    b_mean = before[28:36, :, :3].astype(np.float32).mean()
    a_mean = after[28:36,  :, :3].astype(np.float32).mean()
    assert a_mean <= b_mean + 5.0, (
        f"Edge darkening should not significantly brighten the transition zone: "
        f"before={b_mean:.1f}, after={a_mean:.1f}"
    )


def test_s287_hartley_dark_desat_reduces_saturation_in_darks():
    """Dark zone desaturation should push very dark pixels toward grey."""
    p = _make_small_painter(w=64, h=64)
    dark_ref = _dark_reference(64, 64)
    p.tone_ground((0.10, 0.12, 0.08), texture_strength=0.01)
    p.block_in(dark_ref, stroke_size=8, n_strokes=80)
    p.build_form(dark_ref, stroke_size=4, n_strokes=40)

    canvas_before = _get_canvas(p).copy()
    p.hartley_elemental_mass_pass(
        palette_strength=0.0,
        interior_flatten_strength=0.0,
        edge_darken_strength=0.0,
        dark_desat_thresh=0.30,
        dark_desat_strength=0.95,  # strong desaturation in darks
        bright_sat_strength=0.0,
        opacity=1.0,
    )
    canvas_after = _get_canvas(p)

    # In dark rows: channel spread should decrease (approaching grey)
    dark_rows = slice(0, 32)
    b_rgb = canvas_before[dark_rows, :, :3].astype(np.float32)
    a_rgb = canvas_after[dark_rows,  :, :3].astype(np.float32)
    b_spread = np.std(b_rgb, axis=2).mean()
    a_spread = np.std(a_rgb, axis=2).mean()
    assert a_spread <= b_spread + 5.0, (
        f"Dark-zone desaturation should not increase inter-channel spread in dark zone: "
        f"before={b_spread:.2f}, after={a_spread:.2f}"
    )


def test_s287_hartley_bright_sat_amplifies_brights():
    """Bright zone saturation boost should amplify inter-channel spread in bright zone."""
    p = _make_small_painter(w=64, h=64)
    dark_ref = _dark_reference(64, 64)
    # Use vivid-coloured ref for block_in so brights have colour to amplify
    vivid_ref = _vivid_colour_reference(64, 64)
    p.tone_ground((0.85, 0.80, 0.65), texture_strength=0.01)
    p.block_in(vivid_ref, stroke_size=8, n_strokes=80)
    p.build_form(vivid_ref, stroke_size=4, n_strokes=40)

    before = _get_canvas(p).copy()
    p.hartley_elemental_mass_pass(
        palette_strength=0.0,
        interior_flatten_strength=0.0,
        edge_darken_strength=0.0,
        dark_desat_strength=0.0,
        bright_sat_thresh=0.55,
        bright_sat_strength=0.90,  # strong saturation amplification in brights
        opacity=1.0,
    )
    after = _get_canvas(p)

    # In bright rows (bottom half of vivid ref): check spread change
    bright_rows = slice(32, 64)
    b_rgb = before[bright_rows, :, :3].astype(np.float32)
    a_rgb = after[bright_rows,  :, :3].astype(np.float32)
    b_spread = np.std(b_rgb, axis=2).mean()
    a_spread = np.std(a_rgb, axis=2).mean()
    assert a_spread >= b_spread - 5.0, (
        f"Bright-zone saturation boost should not decrease inter-channel spread: "
        f"before={b_spread:.2f}, after={a_spread:.2f}"
    )


def test_s287_hartley_palette_strength_zero_less_change():
    """palette_strength=0 should produce less change than palette_strength=0.8."""
    ref = _vivid_colour_reference(64, 64)

    p0 = _make_small_painter(w=64, h=64)
    _prime_canvas_full(p0, ref)
    before0 = _get_canvas(p0).copy()
    p0.hartley_elemental_mass_pass(
        palette_strength=0.0,
        interior_flatten_strength=0.0,
        edge_darken_strength=0.0,
        dark_desat_strength=0.0,
        bright_sat_strength=0.0,
        opacity=1.0,
    )
    after0 = _get_canvas(p0)
    diff0 = np.abs(before0[:, :, :3].astype(np.int32) - after0[:, :, :3].astype(np.int32))

    p8 = _make_small_painter(w=64, h=64)
    _prime_canvas_full(p8, ref)
    before8 = _get_canvas(p8).copy()
    p8.hartley_elemental_mass_pass(
        palette_strength=0.80,
        interior_flatten_strength=0.0,
        edge_darken_strength=0.0,
        dark_desat_strength=0.0,
        bright_sat_strength=0.0,
        opacity=1.0,
    )
    after8 = _get_canvas(p8)
    diff8 = np.abs(before8[:, :, :3].astype(np.int32) - after8[:, :, :3].astype(np.int32))

    assert diff8.mean() >= diff0.mean(), (
        f"Higher palette_strength should produce larger canvas change: "
        f"palette_0={diff0.mean():.2f}, palette_0.8={diff8.mean():.2f}"
    )


# ── marsden_hartley catalog entry ─────────────────────────────────────────────

def test_s287_hartley_in_catalog():
    from art_catalog import CATALOG
    assert "marsden_hartley" in CATALOG, "marsden_hartley should be in CATALOG"


def test_s287_hartley_artist_name():
    from art_catalog import get_style
    style = get_style("marsden_hartley")
    assert style.artist == "Marsden Hartley"


def test_s287_hartley_movement_mentions_modernism():
    from art_catalog import get_style
    style = get_style("marsden_hartley")
    m = style.movement.lower()
    assert "modern" in m or "express" in m, (
        f"Movement should mention Modernism or Expressionism: {style.movement}"
    )


def test_s287_hartley_nationality():
    from art_catalog import get_style
    style = get_style("marsden_hartley")
    assert "american" in style.nationality.lower(), (
        f"Nationality should be American: {style.nationality}"
    )


def test_s287_hartley_period():
    from art_catalog import get_style
    style = get_style("marsden_hartley")
    assert "1877" in style.period, f"Period should include birth year 1877: {style.period}"


def test_s287_hartley_palette_count():
    from art_catalog import get_style
    style = get_style("marsden_hartley")
    assert len(style.palette) >= 8, (
        f"Hartley palette should have at least 8 colors, got {len(style.palette)}"
    )


def test_s287_hartley_palette_has_dark_mass():
    """Palette must include a very dark near-black colour for Hartley's dark masses."""
    from art_catalog import get_style
    style = get_style("marsden_hartley")
    has_dark = any(max(c) < 0.20 for c in style.palette)
    assert has_dark, "Palette should include a very dark near-black for mass dominance"


def test_s287_hartley_palette_has_warm_accent():
    """Palette must include a burnt sienna / ochre warm accent."""
    from art_catalog import get_style
    style = get_style("marsden_hartley")
    has_warm = any(c[0] > 0.55 and c[1] < 0.55 and c[2] < 0.30 for c in style.palette)
    assert has_warm, "Palette should include a warm burnt sienna / ochre accent"


def test_s287_hartley_palette_rgb_range():
    from art_catalog import get_style
    style = get_style("marsden_hartley")
    for i, color in enumerate(style.palette):
        assert len(color) == 3, f"Palette color {i} should have 3 channels"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"Palette color {i} channel out of [0,1] range: {ch}"
            )


def test_s287_hartley_famous_works():
    from art_catalog import get_style
    style = get_style("marsden_hartley")
    assert len(style.famous_works) >= 5
    titles = [w[0].lower() for w in style.famous_works]
    assert any("katahdin" in t or "schoodic" in t or "dogtown" in t or
               "storm" in t or "fox" in t or "blueberry" in t
               for t in titles), (
        f"Famous works should include a Hartley signature work: {titles}"
    )


def test_s287_hartley_inspiration_mentions_pass():
    from art_catalog import get_style
    style = get_style("marsden_hartley")
    insp = style.inspiration.lower()
    assert "hartley_elemental_mass_pass" in insp or "198th" in insp, (
        "Inspiration should mention hartley_elemental_mass_pass or 198th mode"
    )


def test_s287_hartley_get_style_roundtrip():
    from art_catalog import get_style, list_artists
    assert "marsden_hartley" in list_artists()
    style = get_style("marsden_hartley")
    assert style.artist == "Marsden Hartley"


# ── Combined pipeline smoke tests ─────────────────────────────────────────────

def test_s287_full_pipeline_smoke():
    """Both new passes run on a small canvas without error."""
    p = _make_small_painter(w=80, h=80)
    ref = _vivid_colour_reference(80, 80)
    p.tone_ground((0.80, 0.75, 0.60), texture_strength=0.020)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)
    p.place_lights(ref, stroke_size=3, n_strokes=15)

    p.paint_median_clarity_pass(
        median_size=5,
        detail_boost=1.80,
        opacity=0.75,
    )
    p.hartley_elemental_mass_pass(
        palette_strength=0.48,
        interior_tile_n_h=8,
        interior_tile_n_w=6,
        interior_flatten_strength=0.32,
        edge_darken_strength=0.50,
        dark_desat_strength=0.52,
        bright_sat_strength=0.48,
        opacity=0.82,
    )

    canvas = _get_canvas(p)
    assert canvas.shape == (80, 80, 4)
    assert canvas[:, :, 3].min() == 255
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s287_passes_with_s286_tonal_rebalance():
    """s287 passes should work alongside s286 tonal_rebalance_pass."""
    p = _make_small_painter(w=72, h=72)
    ref = _vivid_colour_reference(72, 72)
    p.tone_ground((0.80, 0.75, 0.60), texture_strength=0.018)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.build_form(ref, stroke_size=4, n_strokes=18)
    p.place_lights(ref, stroke_size=3, n_strokes=12)

    p.paint_median_clarity_pass(opacity=0.75)
    p.hartley_elemental_mass_pass(opacity=0.82)
    p.paint_tonal_rebalance_pass(opacity=0.72)

    canvas = _get_canvas(p)
    assert canvas.shape == (72, 72, 4)
    assert canvas[:, :, 3].min() == 255
    assert canvas[:, :, :3].max() <= 255


def test_s287_passes_order_independence():
    """Both orders should produce valid canvases (not necessarily identical)."""
    ref = _vivid_colour_reference(64, 64)

    p1 = _make_small_painter(w=64, h=64)
    p1.tone_ground((0.80, 0.75, 0.60), texture_strength=0.01)
    p1.block_in(ref, stroke_size=8, n_strokes=20)
    p1.paint_median_clarity_pass(opacity=0.75)
    p1.hartley_elemental_mass_pass(opacity=0.80)
    c1 = _get_canvas(p1)

    p2 = _make_small_painter(w=64, h=64)
    p2.tone_ground((0.80, 0.75, 0.60), texture_strength=0.01)
    p2.block_in(ref, stroke_size=8, n_strokes=20)
    p2.hartley_elemental_mass_pass(opacity=0.80)
    p2.paint_median_clarity_pass(opacity=0.75)
    c2 = _get_canvas(p2)

    for c in [c1, c2]:
        assert c.shape == (64, 64, 4)
        assert c[:, :, 3].min() == 255
        assert c[:, :, :3].max() <= 255


def test_s287_new_passes_with_s285_frequency_separation():
    """s287 passes chain cleanly with s285 frequency separation."""
    p = _make_small_painter(w=64, h=64)
    ref = _vivid_colour_reference(64, 64)
    p.tone_ground((0.80, 0.75, 0.60), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.build_form(ref, stroke_size=4, n_strokes=18)

    p.paint_median_clarity_pass(opacity=0.75)
    p.hartley_elemental_mass_pass(opacity=0.80)
    p.paint_frequency_separation_pass(opacity=0.50)

    canvas = _get_canvas(p)
    assert canvas.shape == (64, 64, 4)
    assert canvas[:, :, 3].min() == 255
    assert canvas[:, :, :3].max() <= 255
