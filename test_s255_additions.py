"""
test_s255_additions.py -- Session 255 tests for wyeth_tempera_drybrush_pass,
paint_tonal_key_pass, and the andrew_wyeth catalog entry.
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


def _gradient_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [160, 80, 40]
    arr[:, w // 2:, :] = [40, 100, 160]
    return Image.fromarray(arr, "RGB")


def _midtone_reference(w=64, h=64):
    """Canvas dominated by midtone values -- for midtone contrast test."""
    from PIL import Image
    arr = np.full((h, w, 3), 128, dtype=np.uint8)
    arr[:h // 2, :] = 100
    arr[h // 2:, :] = 155
    return Image.fromarray(arr, "RGB")


def _dark_reference(w=64, h=64):
    """Mostly dark canvas for key correction test."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :, :] = 40
    arr[h // 4: 3 * h // 4, w // 4: 3 * w // 4, :] = 80
    return Image.fromarray(arr, "RGB")


def _bright_reference(w=64, h=64):
    """Mostly bright canvas for key correction test."""
    from PIL import Image
    arr = np.full((h, w, 3), 210, dtype=np.uint8)
    arr[h // 4: 3 * h // 4, w // 4: 3 * w // 4, :] = 180
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, midtone=False, dark=False, bright=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if midtone:
            ref = _midtone_reference(w, h)
        elif dark:
            ref = _dark_reference(w, h)
        elif bright:
            ref = _bright_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.72, 0.66, 0.52), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── wyeth_tempera_drybrush_pass ───────────────────────────────────────────────

def test_s255_wyeth_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "wyeth_tempera_drybrush_pass")


def test_s255_wyeth_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.wyeth_tempera_drybrush_pass()
    assert result is None


def test_s255_wyeth_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.wyeth_tempera_drybrush_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after wyeth_tempera_drybrush_pass"


def test_s255_wyeth_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p)
    p.wyeth_tempera_drybrush_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="Alpha channel modified by wyeth_tempera_drybrush_pass"
    )


def test_s255_wyeth_pass_zero_opacity_no_change():
    """opacity=0.0 must leave canvas nearly identical."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.wyeth_tempera_drybrush_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff[:, :, :3].max() <= 2, \
        "opacity=0 should produce negligible change"


def test_s255_wyeth_pass_pixel_values_in_range():
    """All RGB values must remain in [0, 255] after pass."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.wyeth_tempera_drybrush_pass(opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s255_wyeth_pass_chalk_adds_variation():
    """High chalk_amplitude should increase pixel-to-pixel variation."""
    p_low = _make_small_painter(w=128, h=128)
    _prime_canvas(p_low)
    # No chalk, no contrast, no fiber
    p_low.wyeth_tempera_drybrush_pass(
        chalk_amplitude=0.0,
        contrast_strength=0.0,
        fiber_density=0.0,
        opacity=1.0
    )
    after_low = _get_canvas(p_low)

    p_high = _make_small_painter(w=128, h=128)
    _prime_canvas(p_high)
    p_high.wyeth_tempera_drybrush_pass(
        chalk_amplitude=0.12,
        contrast_strength=0.0,
        fiber_density=0.0,
        opacity=1.0
    )
    after_high = _get_canvas(p_high)

    # Variation (std dev of luminance) should be higher with chalk
    lum_low  = after_low[:, :, :3].astype(float).mean(axis=2)
    lum_high = after_high[:, :, :3].astype(float).mean(axis=2)
    assert lum_high.std() >= lum_low.std() - 1.0, \
        "Higher chalk_amplitude should produce more pixel-to-pixel variation"


def test_s255_wyeth_pass_higher_opacity_larger_delta():
    """opacity=1.0 should produce larger pixel delta than opacity=0.2."""
    p_full = _make_small_painter()
    _prime_canvas(p_full)
    before_f = _get_canvas(p_full).copy()
    p_full.wyeth_tempera_drybrush_pass(opacity=1.0)
    after_f  = _get_canvas(p_full)
    delta_full = np.abs(before_f.astype(int) - after_f.astype(int)).sum()

    p_low = _make_small_painter()
    _prime_canvas(p_low)
    before_l = _get_canvas(p_low).copy()
    p_low.wyeth_tempera_drybrush_pass(opacity=0.2)
    after_l  = _get_canvas(p_low)
    delta_low = np.abs(before_l.astype(int) - after_l.astype(int)).sum()

    assert delta_full > delta_low, \
        "Higher opacity should produce larger pixel delta"


def test_s255_wyeth_pass_contrast_enhances_midtones():
    """Midtone-heavy canvas should show larger delta when contrast_strength is high."""
    p_hi = _make_small_painter(w=128, h=128)
    _prime_canvas(p_hi, midtone=True)
    before_hi = _get_canvas(p_hi).copy()
    p_hi.wyeth_tempera_drybrush_pass(
        chalk_amplitude=0.0,
        contrast_strength=0.80,
        fiber_density=0.0,
        opacity=1.0,
    )
    after_hi = _get_canvas(p_hi)
    delta_hi = np.abs(before_hi.astype(int) - after_hi.astype(int)).sum()

    p_lo = _make_small_painter(w=128, h=128)
    _prime_canvas(p_lo, midtone=True)
    before_lo = _get_canvas(p_lo).copy()
    p_lo.wyeth_tempera_drybrush_pass(
        chalk_amplitude=0.0,
        contrast_strength=0.0,
        fiber_density=0.0,
        opacity=1.0,
    )
    after_lo = _get_canvas(p_lo)
    delta_lo = np.abs(before_lo.astype(int) - after_lo.astype(int)).sum()

    assert delta_hi > delta_lo, \
        "Higher contrast_strength should produce larger delta on midtone canvas"


def test_s255_wyeth_pass_fiber_brightens_transition_zone():
    """Fiber pass should introduce brighter pixels in dark-to-mid zone."""
    p_fiber = _make_small_painter(w=128, h=128)
    _prime_canvas(p_fiber, dark=True)
    before = _get_canvas(p_fiber).copy()
    p_fiber.wyeth_tempera_drybrush_pass(
        chalk_amplitude=0.0,
        contrast_strength=0.0,
        fiber_low_lum=0.05,
        fiber_high_lum=0.60,
        fiber_density=0.30,
        fiber_brightness=0.30,
        opacity=1.0,
    )
    after = _get_canvas(p_fiber)
    # Some pixels should be brighter
    diff = after.astype(int) - before.astype(int)
    assert diff[:, :, :3].max() > 5, \
        "Fiber pass should brighten some pixels in the transition zone"


def test_s255_wyeth_pass_seed_reproducibility():
    """Same seed should produce identical results."""
    p1 = _make_small_painter()
    _prime_canvas(p1)
    p1.wyeth_tempera_drybrush_pass(seed=42, opacity=1.0)
    r1 = _get_canvas(p1).copy()

    p2 = _make_small_painter()
    _prime_canvas(p2)
    p2.wyeth_tempera_drybrush_pass(seed=42, opacity=1.0)
    r2 = _get_canvas(p2).copy()

    np.testing.assert_array_equal(r1, r2, err_msg="Same seed must give same result")


def test_s255_wyeth_pass_different_seeds_differ():
    """Different seeds should give different chalk noise patterns."""
    p1 = _make_small_painter(w=128, h=128)
    _prime_canvas(p1)
    p1.wyeth_tempera_drybrush_pass(seed=11, chalk_amplitude=0.08, opacity=1.0)
    r1 = _get_canvas(p1)

    p2 = _make_small_painter(w=128, h=128)
    _prime_canvas(p2)
    p2.wyeth_tempera_drybrush_pass(seed=22, chalk_amplitude=0.08, opacity=1.0)
    r2 = _get_canvas(p2)

    diff = np.abs(r1.astype(int) - r2.astype(int))
    assert diff.sum() > 0, "Different seeds should produce different noise patterns"


# ── paint_tonal_key_pass ──────────────────────────────────────────────────────

def test_s255_tonal_key_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_tonal_key_pass")


def test_s255_tonal_key_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_tonal_key_pass()
    assert result is None


def test_s255_tonal_key_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_tonal_key_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_tonal_key_pass"


def test_s255_tonal_key_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p)
    p.paint_tonal_key_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="Alpha channel modified by paint_tonal_key_pass"
    )


def test_s255_tonal_key_pass_zero_opacity_no_change():
    """opacity=0.0 must leave canvas nearly identical."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_tonal_key_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff[:, :, :3].max() <= 2, \
        "opacity=0 should produce negligible change"


def test_s255_tonal_key_pass_pixel_values_in_range():
    """All RGB values must remain in [0, 255] after pass."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.paint_tonal_key_pass(opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s255_tonal_key_pass_high_key_brightens_dark_canvas():
    """target_key=0.9 should raise the median luminance of a dark canvas."""
    p = _make_small_painter(w=128, h=128)
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    before_lum = before[:, :, :3].astype(float).mean()

    p.paint_tonal_key_pass(target_key=0.9, key_strength=6.0, opacity=1.0)
    after = _get_canvas(p)
    after_lum = after[:, :, :3].astype(float).mean()

    assert after_lum > before_lum, \
        "High target_key should raise average luminance of a dark canvas"


def test_s255_tonal_key_pass_low_key_darkens_bright_canvas():
    """target_key=0.1 should lower the median luminance of a bright canvas."""
    p = _make_small_painter(w=128, h=128)
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    before_lum = before[:, :, :3].astype(float).mean()

    p.paint_tonal_key_pass(target_key=0.1, key_strength=6.0, opacity=1.0)
    after = _get_canvas(p)
    after_lum = after[:, :, :3].astype(float).mean()

    assert after_lum < before_lum, \
        "Low target_key should lower average luminance of a bright canvas"


def test_s255_tonal_key_pass_higher_opacity_larger_delta():
    """opacity=1.0 should produce larger delta than opacity=0.3."""
    p1 = _make_small_painter(w=128, h=128)
    _prime_canvas(p1, dark=True)
    b1 = _get_canvas(p1).copy()
    p1.paint_tonal_key_pass(target_key=0.8, opacity=1.0)
    a1 = _get_canvas(p1)
    d1 = np.abs(b1.astype(int) - a1.astype(int)).sum()

    p2 = _make_small_painter(w=128, h=128)
    _prime_canvas(p2, dark=True)
    b2 = _get_canvas(p2).copy()
    p2.paint_tonal_key_pass(target_key=0.8, opacity=0.3)
    a2 = _get_canvas(p2)
    d2 = np.abs(b2.astype(int) - a2.astype(int)).sum()

    assert d1 > d2, "Higher opacity should produce larger pixel delta"


def test_s255_tonal_key_pass_bayer_dither_creates_microvariation():
    """High dither_amplitude should produce more inter-pixel variation."""
    p_hi = _make_small_painter(w=128, h=128)
    _prime_canvas(p_hi)
    p_hi.paint_tonal_key_pass(
        target_key=0.5, key_strength=0.1,
        dither_amplitude=0.12, opacity=1.0
    )
    after_hi = _get_canvas(p_hi)
    lum_hi = after_hi[:, :, :3].astype(float).mean(axis=2)

    p_lo = _make_small_painter(w=128, h=128)
    _prime_canvas(p_lo)
    p_lo.paint_tonal_key_pass(
        target_key=0.5, key_strength=0.1,
        dither_amplitude=0.0, opacity=1.0
    )
    after_lo = _get_canvas(p_lo)
    lum_lo = after_lo[:, :, :3].astype(float).mean(axis=2)

    assert lum_hi.std() >= lum_lo.std() - 1.0, \
        "Higher dither_amplitude should not reduce pixel variation"


# ── andrew_wyeth catalog entry ────────────────────────────────────────────────

def test_s255_catalog_wyeth_entry_exists():
    import art_catalog
    assert "andrew_wyeth" in art_catalog.CATALOG


def test_s255_catalog_wyeth_artist_name():
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    assert s.artist == "Andrew Wyeth"


def test_s255_catalog_wyeth_movement():
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    assert "Realism" in s.movement or "Regionalism" in s.movement


def test_s255_catalog_wyeth_nationality():
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    assert "American" in s.nationality


def test_s255_catalog_wyeth_palette_count():
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    assert len(s.palette) >= 8, "Wyeth palette should have at least 8 colours"


def test_s255_catalog_wyeth_palette_values_valid():
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    for r, g, b in s.palette:
        assert 0.0 <= r <= 1.0
        assert 0.0 <= g <= 1.0
        assert 0.0 <= b <= 1.0


def test_s255_catalog_wyeth_ground_color_valid():
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    r, g, b = s.ground_color
    assert 0.0 <= r <= 1.0
    assert 0.0 <= g <= 1.0
    assert 0.0 <= b <= 1.0


def test_s255_catalog_wyeth_very_dry():
    """Wyeth egg tempera is very dry -- wet_blend should be low."""
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    assert s.wet_blend < 0.40, "Wyeth tempera should have low wet_blend"


def test_s255_catalog_wyeth_no_glazing():
    """Egg tempera does not use oil glazes."""
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    assert s.glazing is None, "Wyeth should have no glazing (tempera medium)"


def test_s255_catalog_wyeth_crackle_false():
    """Wyeth panels are modern -- no lead-based crackle."""
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    assert s.crackle is False


def test_s255_catalog_wyeth_famous_works():
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    assert len(s.famous_works) >= 5
    titles = [t for t, _ in s.famous_works]
    assert any("Christina" in t or "Winter" in t or "Wind" in t for t in titles)


def test_s255_catalog_wyeth_inspiration_references_166th():
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    assert "166" in s.inspiration


def test_s255_catalog_wyeth_inspiration_references_drybrush():
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    assert "dry" in s.inspiration.lower() or "fiber" in s.inspiration.lower()


def test_s255_catalog_wyeth_technique_mentions_tempera():
    import art_catalog
    s = art_catalog.get_style("andrew_wyeth")
    assert "tempera" in s.technique.lower()


def test_s255_catalog_total_artist_count():
    """Total artist count should have grown to at least 255."""
    import art_catalog
    assert len(art_catalog.list_artists()) >= 255
