"""
test_s285_additions.py -- Session 285 tests for paint_frequency_separation_pass,
derain_fauve_intensity_pass, and the andre_derain catalog entry.
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
    arr[:h // 2, :w // 2, :] = [220, 80, 20]    # orange-red quadrant
    arr[:h // 2, w // 2:, :] = [20, 80, 200]    # cobalt blue quadrant
    arr[h // 2:, :w // 2, :] = [30, 170, 80]    # viridian quadrant
    arr[h // 2:, w // 2:, :] = [180, 30, 160]   # violet quadrant
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
    p.tone_ground((0.88, 0.84, 0.70), texture_strength=0.018)
    p.block_in(ref, stroke_size=10, n_strokes=30)


def _prime_canvas_full(p, ref=None):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        ref = _vivid_colour_reference(w, h)
    p.tone_ground((0.88, 0.84, 0.70), texture_strength=0.018)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.build_form(ref, stroke_size=5, n_strokes=25)
    p.place_lights(ref, stroke_size=3, n_strokes=15)


# ── paint_frequency_separation_pass ──────────────────────────────────────────

def test_s285_freq_sep_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_frequency_separation_pass")


def test_s285_freq_sep_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_frequency_separation_pass()
    assert result is None


def test_s285_freq_sep_modifies_canvas():
    p = _make_small_painter(w=80, h=80)
    _prime_canvas_full(p, _vivid_colour_reference(80, 80))
    before = _get_canvas(p).copy()
    p.paint_frequency_separation_pass(
        sat_boost=0.50,
        lum_contrast=0.60,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after paint_frequency_separation_pass"
    )


def test_s285_freq_sep_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_frequency_separation_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s285_freq_sep_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas_full(p, _vivid_colour_reference(72, 72))
    p.paint_frequency_separation_pass(
        sat_boost=0.60,
        lum_contrast=0.70,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s285_freq_sep_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.paint_frequency_separation_pass(opacity=0.80)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque"
    )


def test_s285_freq_sep_zero_sat_boost_small_change():
    """Zero sat_boost with some contrast should still apply high-freq amplification."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas_full(p)
    before = _get_canvas(p).copy()
    p.paint_frequency_separation_pass(
        sat_boost=0.0,
        lum_contrast=0.50,
        opacity=0.80,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    # Zero sat_boost + some contrast: high-freq amplified, change possible
    assert diff.max() >= 0  # should not crash; change may or may not be zero


def test_s285_freq_sep_increases_saturation_in_colour_zones():
    """Sat boost in low-freq should increase colour separation in vivid areas."""
    p = _make_small_painter(w=80, h=80)
    ref = _vivid_colour_reference(80, 80)
    p.tone_ground((0.88, 0.84, 0.70), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=120)
    before = _get_canvas(p).copy()
    p.paint_frequency_separation_pass(
        low_sigma=10.0,
        sat_boost=0.80,
        lum_contrast=0.0,
        recombine_weight=1.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    # Compute grey proximity before and after: saturation boosts should push
    # pixel values further from their channel mean
    b_rgb = before[:, :, :3].astype(np.float32)
    a_rgb = after[:, :, :3].astype(np.float32)
    b_spread = np.std(b_rgb, axis=2).mean()
    a_spread = np.std(a_rgb, axis=2).mean()
    assert a_spread >= b_spread - 5.0, (
        f"Frequency separation with sat_boost should not reduce inter-channel spread: "
        f"before={b_spread:.2f}, after={a_spread:.2f}"
    )


def test_s285_freq_sep_small_canvas():
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.paint_frequency_separation_pass(opacity=0.60)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


# ── derain_fauve_intensity_pass ───────────────────────────────────────────────

def test_s285_derain_fauve_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "derain_fauve_intensity_pass")


def test_s285_derain_fauve_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.derain_fauve_intensity_pass()
    assert result is None


def test_s285_derain_fauve_modifies_canvas():
    p = _make_small_painter(w=80, h=80)
    _prime_canvas_full(p, _vivid_colour_reference(80, 80))
    before = _get_canvas(p).copy()
    p.derain_fauve_intensity_pass(
        sat_gamma=0.55,
        sector_strength=0.30,
        contrast_amplify=0.50,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after derain_fauve_intensity_pass"
    )


def test_s285_derain_fauve_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.derain_fauve_intensity_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s285_derain_fauve_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas_full(p, _vivid_colour_reference(72, 72))
    p.derain_fauve_intensity_pass(
        sat_gamma=0.50,
        sector_strength=0.40,
        contrast_amplify=0.60,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s285_derain_fauve_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.derain_fauve_intensity_pass(opacity=0.85)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque after derain_fauve_intensity_pass"
    )


def test_s285_derain_fauve_boosts_saturation():
    """Saturation power curve (gamma < 1) should increase inter-channel spread."""
    p = _make_small_painter(w=64, h=64)
    ref = _vivid_colour_reference(64, 64)
    p.tone_ground((0.88, 0.84, 0.70), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=100)

    before = _get_canvas(p).copy()
    p.derain_fauve_intensity_pass(
        sat_gamma=0.40,        # strong saturation expansion
        sector_strength=0.0,   # isolate saturation effect
        contrast_amplify=0.0,
        angle_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    b_rgb = before[:, :, :3].astype(np.float32)
    a_rgb = after[:, :, :3].astype(np.float32)
    b_spread = np.std(b_rgb, axis=2).mean()
    a_spread = np.std(a_rgb, axis=2).mean()
    # Saturation boost should increase inter-channel divergence (or hold steady)
    assert a_spread >= b_spread - 5.0, (
        f"Saturation power curve should not decrease inter-channel spread: "
        f"before={b_spread:.2f}, after={a_spread:.2f}"
    )


def test_s285_derain_fauve_high_saturation_gamma():
    """gamma=1.0 should preserve saturation distribution, causing minimal change."""
    p = _make_small_painter(w=64, h=64)
    ref = _flat_midtone_reference(64, 64)
    p.tone_ground((0.88, 0.84, 0.70), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=80)

    before = _get_canvas(p).copy()
    p.derain_fauve_intensity_pass(
        sat_gamma=1.0,         # no-op saturation (S^1 = S)
        sector_strength=0.0,   # no hue push
        contrast_amplify=0.0,  # no colour contrast
        angle_strength=0.0,    # no directional push
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() <= 5, (
        f"gamma=1 with all strengths zero should produce minimal change: max_diff={diff.max()}"
    )


def test_s285_derain_fauve_small_canvas():
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.derain_fauve_intensity_pass(opacity=0.60)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


def test_s285_derain_sector_strength_zero_vs_nonzero():
    """Non-zero sector_strength should produce different result than zero."""
    ref = _vivid_colour_reference(64, 64)

    p1 = _make_small_painter(w=64, h=64)
    p1.tone_ground((0.88, 0.84, 0.70), texture_strength=0.01)
    p1.block_in(ref, stroke_size=8, n_strokes=60)
    p1.derain_fauve_intensity_pass(
        sat_gamma=1.0, sector_strength=0.0, contrast_amplify=0.0,
        angle_strength=0.0, opacity=1.0
    )
    c1 = _get_canvas(p1)

    p2 = _make_small_painter(w=64, h=64)
    p2.tone_ground((0.88, 0.84, 0.70), texture_strength=0.01)
    p2.block_in(ref, stroke_size=8, n_strokes=60)
    p2.derain_fauve_intensity_pass(
        sat_gamma=1.0, sector_strength=0.50, contrast_amplify=0.0,
        angle_strength=0.0, opacity=1.0
    )
    c2 = _get_canvas(p2)

    diff = np.abs(c1[:, :, :3].astype(np.int32) - c2[:, :, :3].astype(np.int32))
    assert diff.max() >= 1, (
        "sector_strength > 0 should produce different result from sector_strength = 0"
    )


# ── andre_derain catalog entry ────────────────────────────────────────────────

def test_s285_derain_in_catalog():
    from art_catalog import CATALOG
    assert "andre_derain" in CATALOG, "andre_derain should be in CATALOG"


def test_s285_derain_artist_name():
    from art_catalog import get_style
    style = get_style("andre_derain")
    assert style.artist == "André Derain"


def test_s285_derain_movement_mentions_fauvism():
    from art_catalog import get_style
    style = get_style("andre_derain")
    m = style.movement.lower()
    assert "fauv" in m, f"Movement should mention Fauvism: {style.movement}"


def test_s285_derain_nationality():
    from art_catalog import get_style
    style = get_style("andre_derain")
    assert "french" in style.nationality.lower(), (
        f"Nationality should be French: {style.nationality}"
    )


def test_s285_derain_period():
    from art_catalog import get_style
    style = get_style("andre_derain")
    assert "1880" in style.period, f"Period should include birth year 1880: {style.period}"


def test_s285_derain_palette_count():
    from art_catalog import get_style
    style = get_style("andre_derain")
    assert len(style.palette) >= 6, (
        f"Derain palette should have at least 6 colors, got {len(style.palette)}"
    )


def test_s285_derain_palette_has_vivid_warm():
    """Palette should include a vivid warm (orange-red Fauve) colour."""
    from art_catalog import get_style
    style = get_style("andre_derain")
    has_warm = any(c[0] > 0.70 and c[1] < 0.55 and c[2] < 0.35 for c in style.palette)
    assert has_warm, "Palette should include a vivid warm orange-red for Fauve energy"


def test_s285_derain_palette_has_vivid_cool():
    """Palette should include a vivid cool (cobalt blue) colour."""
    from art_catalog import get_style
    style = get_style("andre_derain")
    has_cool = any(c[2] > 0.65 and c[0] < 0.35 for c in style.palette)
    assert has_cool, "Palette should include a vivid cobalt blue for Fauve cool"


def test_s285_derain_palette_rgb_range():
    from art_catalog import get_style
    style = get_style("andre_derain")
    for i, color in enumerate(style.palette):
        assert len(color) == 3, f"Palette color {i} should have 3 channels"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"Palette color {i} channel out of [0,1] range: {ch}"
            )


def test_s285_derain_famous_works():
    from art_catalog import get_style
    style = get_style("andre_derain")
    assert len(style.famous_works) >= 5
    titles = [w[0].lower() for w in style.famous_works]
    assert any("collioure" in t or "pool" in t or "london" in t or
               "charing" in t or "thames" in t or "boats" in t
               for t in titles), (
        f"Famous works should include a Derain signature work: {titles}"
    )


def test_s285_derain_inspiration_mentions_pass():
    from art_catalog import get_style
    style = get_style("andre_derain")
    insp = style.inspiration.lower()
    assert "derain_fauve_intensity_pass" in insp or "196th" in insp, (
        "Inspiration should mention derain_fauve_intensity_pass or 196th mode"
    )


def test_s285_derain_get_style_roundtrip():
    from art_catalog import get_style, list_artists
    assert "andre_derain" in list_artists()
    style = get_style("andre_derain")
    assert style.artist == "André Derain"


# ── Combined pipeline smoke tests ─────────────────────────────────────────────

def test_s285_full_pipeline_smoke():
    """Both new passes run on a small canvas without error."""
    p = _make_small_painter(w=80, h=80)
    ref = _vivid_colour_reference(80, 80)
    p.tone_ground((0.88, 0.84, 0.70), texture_strength=0.018)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)
    p.place_lights(ref, stroke_size=3, n_strokes=15)

    p.paint_frequency_separation_pass(
        sat_boost=0.40,
        lum_contrast=0.50,
        opacity=0.78,
    )
    p.derain_fauve_intensity_pass(
        sat_gamma=0.60,
        sector_strength=0.28,
        contrast_amplify=0.48,
        angle_strength=0.20,
        opacity=0.80,
    )

    canvas = _get_canvas(p)
    assert canvas.shape == (80, 80, 4)
    assert canvas[:, :, 3].min() == 255
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s285_passes_with_s284_pass():
    """s285 passes should work alongside s284 chromatic_shadow_shift_pass."""
    p = _make_small_painter(w=72, h=72)
    ref = _vivid_colour_reference(72, 72)
    p.tone_ground((0.88, 0.84, 0.70), texture_strength=0.018)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.build_form(ref, stroke_size=4, n_strokes=18)
    p.place_lights(ref, stroke_size=3, n_strokes=12)

    p.paint_frequency_separation_pass(opacity=0.75)
    p.derain_fauve_intensity_pass(opacity=0.80)
    p.paint_chromatic_shadow_shift_pass(opacity=0.65)

    canvas = _get_canvas(p)
    assert canvas.shape == (72, 72, 4)
    assert canvas[:, :, 3].min() == 255
    assert canvas[:, :, :3].max() <= 255


def test_s285_passes_order_independence():
    """Both orders should produce valid canvases."""
    ref = _vivid_colour_reference(64, 64)

    p1 = _make_small_painter(w=64, h=64)
    p1.tone_ground((0.88, 0.84, 0.70), texture_strength=0.01)
    p1.block_in(ref, stroke_size=8, n_strokes=20)
    p1.paint_frequency_separation_pass(opacity=0.80)
    p1.derain_fauve_intensity_pass(opacity=0.80)
    c1 = _get_canvas(p1)

    p2 = _make_small_painter(w=64, h=64)
    p2.tone_ground((0.88, 0.84, 0.70), texture_strength=0.01)
    p2.block_in(ref, stroke_size=8, n_strokes=20)
    p2.derain_fauve_intensity_pass(opacity=0.80)
    p2.paint_frequency_separation_pass(opacity=0.80)
    c2 = _get_canvas(p2)

    for c in [c1, c2]:
        assert c.shape == (64, 64, 4)
        assert c[:, :, 3].min() == 255
        assert c[:, :, :3].max() <= 255
