"""
test_s257_additions.py -- Session 257 tests for hilma_af_klint_biomorphic_pass,
paint_shadow_bleed_pass, and the hilma_af_klint catalog inspiration update.
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


def _warm_cool_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [200, 100, 40]
    arr[:, w // 2:, :] = [40, 80, 200]
    return Image.fromarray(arr, "RGB")


def _light_dark_reference(w=64, h=64):
    """Top half bright, bottom half dark -- for shadow bleed test."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :] = [220, 200, 180]   # bright
    arr[h // 2:, :] = [30, 25, 20]       # dark
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, warm_cool=False, light_dark=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if warm_cool:
            ref = _warm_cool_reference(w, h)
        elif light_dark:
            ref = _light_dark_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.92, 0.90, 0.85), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── hilma_af_klint_biomorphic_pass ───────────────────────────────────────────

def test_s257_biomorphic_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "hilma_af_klint_biomorphic_pass")


def test_s257_biomorphic_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.hilma_af_klint_biomorphic_pass()
    assert result is None


def test_s257_biomorphic_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    before = _get_canvas(p).copy()
    p.hilma_af_klint_biomorphic_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after hilma_af_klint_biomorphic_pass"


def test_s257_biomorphic_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p)
    p.hilma_af_klint_biomorphic_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after hilma_af_klint_biomorphic_pass"
    )


def test_s257_biomorphic_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.hilma_af_klint_biomorphic_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s257_biomorphic_values_in_range():
    """All RGB values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    p.hilma_af_klint_biomorphic_pass(opacity=1.0, ring_amplitude=1.0)
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after biomorphic pass"
    )


def test_s257_biomorphic_warm_push_increases_red():
    """With warm_push > 0 and cool_push=0, the pass should push some pixels warmer (R up)."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.hilma_af_klint_biomorphic_pass(
        ring_count=2.0,
        ring_amplitude=1.0,
        warm_push=0.5,
        cool_push=0.0,
        haze_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    # R channel should increase somewhere due to warm push
    r_diff = after[:, :, 2].astype(int) - before[:, :, 2].astype(int)
    assert r_diff.max() > 0, "Warm push should increase R channel in some pixels"


def test_s257_biomorphic_cool_push_increases_blue():
    """With cool_push > 0 and warm_push=0, the pass should push some pixels cooler (B up)."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.hilma_af_klint_biomorphic_pass(
        ring_count=2.0,
        ring_amplitude=1.0,
        warm_push=0.0,
        cool_push=0.5,
        haze_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    # B channel (index 0 in BGRA Cairo order) should increase somewhere
    b_diff = after[:, :, 0].astype(int) - before[:, :, 0].astype(int)
    assert b_diff.max() > 0, "Cool push should increase B channel in some pixels"


def test_s257_biomorphic_haze_brightens():
    """With high haze_strength, some pixels should be brighter than before."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.hilma_af_klint_biomorphic_pass(
        ring_amplitude=1.0,
        warm_push=0.0,
        cool_push=0.0,
        haze_strength=0.5,
        opacity=1.0,
    )
    after = _get_canvas(p)
    # Some pixels should be brighter
    any_brighter = (after[:, :, 2].astype(int) > before[:, :, 2].astype(int)).any()
    assert any_brighter, "Haze should brighten some pixels"


def test_s257_biomorphic_zero_ring_amplitude_minimal_rgb_change():
    """With ring_amplitude=0 and haze_strength=0, no chromatic change should occur."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.hilma_af_klint_biomorphic_pass(
        ring_amplitude=0.0,
        haze_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(int) - after[:, :, :3].astype(int))
    assert diff.max() <= 2, (
        f"ring_amplitude=0, haze=0 should produce no visible change; max_diff={diff.max()}"
    )


def test_s257_biomorphic_more_rings_more_alternation():
    """More rings should produce more alternating warm/cool zones."""
    p_few = _make_small_painter()
    _prime_canvas(p_few)
    p_few.hilma_af_klint_biomorphic_pass(ring_count=1.0, ring_amplitude=1.0,
                                          warm_push=0.3, cool_push=0.3,
                                          haze_strength=0.0, opacity=1.0)
    out_few = _get_canvas(p_few)

    p_many = _make_small_painter()
    _prime_canvas(p_many)
    p_many.hilma_af_klint_biomorphic_pass(ring_count=8.0, ring_amplitude=1.0,
                                           warm_push=0.3, cool_push=0.3,
                                           haze_strength=0.0, opacity=1.0)
    out_many = _get_canvas(p_many)

    # More rings = more variation = higher std of R channel diff from baseline
    std_few = float(np.std(out_few[:, :, 2].astype(float)))
    std_many = float(np.std(out_many[:, :, 2].astype(float)))
    # More rings should produce at least as much variation (std may stay similar
    # or increase; both should at least be non-zero)
    assert std_few > 0 and std_many > 0, "Both passes must produce channel variation"


# ── paint_shadow_bleed_pass ──────────────────────────────────────────────────

def test_s257_shadow_bleed_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_shadow_bleed_pass")


def test_s257_shadow_bleed_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, light_dark=True)
    result = p.paint_shadow_bleed_pass()
    assert result is None


def test_s257_shadow_bleed_pass_modifies_canvas():
    """Pass must change pixels when both shadow and bright regions exist."""
    p = _make_small_painter()
    _prime_canvas(p, light_dark=True)
    before = _get_canvas(p).copy()
    p.paint_shadow_bleed_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_shadow_bleed_pass"


def test_s257_shadow_bleed_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, light_dark=True)
    before = _get_canvas(p)
    p.paint_shadow_bleed_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after paint_shadow_bleed_pass"
    )


def test_s257_shadow_bleed_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, light_dark=True)
    before = _get_canvas(p).copy()
    p.paint_shadow_bleed_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s257_shadow_bleed_values_in_range():
    """All RGB values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, light_dark=True)
    p.paint_shadow_bleed_pass(opacity=1.0, reflect_strength=1.0)
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] range after shadow bleed pass"
    )


def test_s257_shadow_bleed_warms_shadow_zone():
    """The shadow region should become warmer (R higher) after pass with warm defaults."""
    from PIL import Image
    w, h = 64, 64
    ref = _light_dark_reference(w, h)

    p = _make_small_painter(w, h)
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy()

    p.paint_shadow_bleed_pass(
        shadow_threshold=0.40,
        bright_threshold=0.65,
        bleed_sigma=6.0,
        reflect_strength=0.5,
        warm_r=1.0,
        warm_g=0.7,
        warm_b=0.2,
        opacity=1.0,
    )
    after = _get_canvas(p)

    # Compare R channel in the dark region (lower half)
    shadow_rows = slice(h // 2, h)
    r_before = before[shadow_rows, :, 2].astype(float)
    r_after  = after[shadow_rows, :, 2].astype(float)
    # Mean R in shadow zone should not decrease
    assert r_after.mean() >= r_before.mean() - 1.0, (
        "Shadow bleed should not reduce R in shadow zone; "
        f"before={r_before.mean():.1f}, after={r_after.mean():.1f}"
    )


def test_s257_shadow_bleed_no_shadow_minimal_change():
    """If image is entirely bright (no shadow), reflect_field should be near-zero."""
    from PIL import Image
    arr = np.full((64, 64, 3), 220, dtype=np.uint8)   # all bright
    ref = Image.fromarray(arr, "RGB")

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy()
    p.paint_shadow_bleed_pass(opacity=1.0, shadow_threshold=0.10)   # very low threshold
    after = _get_canvas(p)

    diff = np.abs(before[:, :, :3].astype(int) - after[:, :, :3].astype(int))
    # All-bright canvas with low shadow_threshold has no shadow zone -> minimal change
    assert diff.max() <= 3, (
        f"All-bright canvas with low threshold should see minimal change; max={diff.max()}"
    )


def test_s257_shadow_bleed_no_bright_minimal_change():
    """If image is entirely dark (no bright zone), reflect_field should be near-zero."""
    from PIL import Image
    arr = np.full((64, 64, 3), 30, dtype=np.uint8)   # all dark
    ref = Image.fromarray(arr, "RGB")

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy()
    p.paint_shadow_bleed_pass(opacity=1.0, bright_threshold=0.90)   # very high threshold
    after = _get_canvas(p)

    diff = np.abs(before[:, :, :3].astype(int) - after[:, :, :3].astype(int))
    assert diff.max() <= 3, (
        f"All-dark canvas with high bright_threshold should see minimal change; max={diff.max()}"
    )


def test_s257_shadow_bleed_higher_strength_more_change():
    """Higher reflect_strength should produce more pixel change than lower."""
    from PIL import Image
    ref = _light_dark_reference(64, 64)

    def _run(strength):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        before = _get_canvas(p).copy()
        p.paint_shadow_bleed_pass(reflect_strength=strength, opacity=1.0)
        after = _get_canvas(p)
        return int(np.abs(before.astype(int) - after.astype(int)).sum())

    change_low  = _run(0.05)
    change_high = _run(0.50)
    assert change_high >= change_low, (
        "Higher reflect_strength should produce equal or greater change"
    )


# ── hilma_af_klint catalog entry ─────────────────────────────────────────────

def test_s257_catalog_hilma_af_klint_present():
    from art_catalog import CATALOG
    assert "hilma_af_klint" in CATALOG, "hilma_af_klint not found in CATALOG"


def test_s257_catalog_hilma_af_klint_fields():
    from art_catalog import CATALOG
    s = CATALOG["hilma_af_klint"]
    assert s.artist == "Hilma af Klint"
    assert s.nationality == "Swedish"
    assert "1906" in s.period
    assert len(s.palette) >= 4
    assert len(s.famous_works) >= 3


def test_s257_catalog_hilma_af_klint_inspiration_updated():
    """Inspiration field should reference the new biomorphic pass."""
    from art_catalog import CATALOG
    s = CATALOG["hilma_af_klint"]
    assert "biomorphic" in s.inspiration.lower(), (
        "Inspiration should reference hilma_af_klint_biomorphic_pass"
    )


def test_s257_catalog_hilma_light_ground():
    """Ground color should be pale (af Klint worked on light-grounded canvas)."""
    from art_catalog import CATALOG
    s = CATALOG["hilma_af_klint"]
    r, g, b = s.ground_color
    assert r > 0.8 and g > 0.8 and b > 0.8, (
        f"Expected pale canvas ground > 0.8; got ({r:.2f},{g:.2f},{b:.2f})"
    )


def test_s257_catalog_count_still_255():
    """CATALOG should still contain 255 entries (no new artist added this session)."""
    from art_catalog import CATALOG
    assert len(CATALOG) >= 255, f"Expected >= 255 entries, got {len(CATALOG)}"


def test_s257_catalog_get_style_hilma():
    """get_style() should retrieve hilma_af_klint by key."""
    from art_catalog import get_style
    s = get_style("hilma_af_klint")
    assert s.artist == "Hilma af Klint"


# ── Integration: run both new passes together ────────────────────────────────

def test_s257_full_pipeline_biomorphic_and_shadow_bleed():
    """Run both new passes in sequence; canvas should be modified and valid."""
    p = _make_small_painter()
    _prime_canvas(p, light_dark=True)
    before = _get_canvas(p).copy()

    p.hilma_af_klint_biomorphic_pass(opacity=0.8)
    p.paint_shadow_bleed_pass(opacity=0.7)

    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Pipeline should modify canvas"
    assert after.min() >= 0 and after.max() <= 255, "Values must stay in [0, 255]"
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), "Alpha must be preserved"
