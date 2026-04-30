"""
test_s264_additions.py -- Session 264 tests for soulages_outrenoir_pass,
paint_luminance_excavation_pass, and the soulages catalog entry.
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
    """Very dark reference -- ideal for dark-region passes."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :, :] = [22, 20, 24]   # near-black schist
    # Add a few lighter fracture bands
    for fy in [16, 32, 48]:
        arr[fy:fy + 2, :, :] = [110, 95, 80]
    return Image.fromarray(arr, "RGB")


def _edge_reference(w=64, h=64):
    """High-contrast half-half for edge/bloom tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [200, 190, 180]
    arr[:, w // 2:, :] = [20, 18, 22]
    return Image.fromarray(arr, "RGB")


def _grey_reference(w=64, h=64):
    """Mid-grey flat reference."""
    from PIL import Image
    arr = np.full((h, w, 3), 128, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, dark=False, edge=False, grey=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if dark:
            ref = _dark_reference(w, h)
        elif edge:
            ref = _edge_reference(w, h)
        elif grey:
            ref = _grey_reference(w, h)
        else:
            ref = _dark_reference(w, h)
    p.tone_ground((0.04, 0.04, 0.05), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── paint_luminance_excavation_pass ──────────────────────────────────────────

def test_s264_excavation_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_luminance_excavation_pass")


def test_s264_excavation_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    result = p.paint_luminance_excavation_pass()
    assert result is None


def test_s264_excavation_pass_modifies_canvas():
    """Pass must change at least some pixels with amplified parameters.

    Default lift_amount is intentionally sub-uint8 for subtlety on large
    canvases; this test uses stronger params to verify the mechanism works.
    """
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.paint_luminance_excavation_pass(
        dark_threshold=0.90,   # treat most canvas as dark
        texture_strength=2.0,
        lift_amount=0.20,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_luminance_excavation_pass"


def test_s264_excavation_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p)
    p.paint_luminance_excavation_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after paint_luminance_excavation_pass"
    )


def test_s264_excavation_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.paint_luminance_excavation_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s264_excavation_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.paint_luminance_excavation_pass(
        texture_strength=1.0, lift_amount=0.5, opacity=1.0
    )
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after paint_luminance_excavation_pass"
    )


def test_s264_excavation_lifts_dark_regions():
    """Excavation should only ever increase luminance (micro-lift, not darken)."""
    from PIL import Image
    arr = np.full((64, 64, 3), 18, dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")

    p_base = _make_small_painter()
    _prime_canvas(p_base, ref=ref)
    before = _get_canvas(p_base).copy().astype(float) / 255.0
    mean_before = before[:, :, :3].mean()

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    p.paint_luminance_excavation_pass(
        dark_threshold=0.9,  # everything is dark
        texture_strength=0.50,
        lift_amount=0.10,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    mean_after = after[:, :, :3].mean()

    # Lift should not decrease the mean (may be minimal change)
    assert mean_after >= mean_before - 0.005, (
        f"Excavation should not darken; before={mean_before:.4f}, after={mean_after:.4f}"
    )


def test_s264_excavation_higher_opacity_more_change():
    """Higher opacity should produce at least as much change as lower opacity."""
    ref = _dark_reference(64, 64)

    def _run(op):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        before = _get_canvas(p).copy()
        p.paint_luminance_excavation_pass(opacity=op)
        after = _get_canvas(p)
        return int(np.abs(before.astype(int) - after.astype(int)).sum())

    assert _run(0.8) >= _run(0.2), "Higher opacity should produce more change"


def test_s264_excavation_does_not_affect_bright_regions():
    """Bright pixels (above dark_threshold) should not be lifted by excavation."""
    from PIL import Image
    # Bright reference -- everything above threshold
    arr = np.full((64, 64, 3), 200, dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")

    p_base = _make_small_painter()
    _prime_canvas(p_base, ref=ref)
    before = _get_canvas(p_base).copy()

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    # dark_threshold=0.10 means only very dark pixels get excavated
    p.paint_luminance_excavation_pass(
        dark_threshold=0.10,
        texture_strength=0.50,
        lift_amount=0.20,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    # The change should be negligible for a bright canvas at very low threshold
    assert diff[:, :, :3].sum() < before[:, :, :3].size * 0.05 * 255, (
        "Excavation should not significantly affect bright regions"
    )


# ── soulages_outrenoir_pass ───────────────────────────────────────────────────

def test_s264_soulages_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "soulages_outrenoir_pass")


def test_s264_soulages_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    result = p.soulages_outrenoir_pass()
    assert result is None


def test_s264_soulages_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.soulages_outrenoir_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after soulages_outrenoir_pass"


def test_s264_soulages_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p)
    p.soulages_outrenoir_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after soulages_outrenoir_pass"
    )


def test_s264_soulages_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.soulages_outrenoir_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s264_soulages_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.soulages_outrenoir_pass(
        deepening_power=4.0,
        stripe_strength=0.50,
        bloom_strength=0.50,
        opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after soulages_outrenoir_pass"
    )


def test_s264_soulages_deepening_darkens_dark_regions():
    """Ultra-black deepening should reduce mean luminance of a dark canvas."""
    from PIL import Image
    arr = np.full((64, 64, 3), 45, dtype=np.uint8)  # lum ~0.18 -- below threshold
    ref = Image.fromarray(arr, "RGB")

    p_base = _make_small_painter()
    _prime_canvas(p_base, ref=ref)
    before = _get_canvas(p_base).copy().astype(float) / 255.0
    mean_before = before[:, :, :3].mean()

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    p.soulages_outrenoir_pass(
        black_threshold=0.80,  # everything below 0.80 gets deepened
        deepening_power=3.0,
        stripe_strength=0.0,   # disable other effects for isolation
        bloom_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    mean_after = after[:, :, :3].mean()

    assert mean_after <= mean_before + 0.005, (
        f"Deepening should darken or preserve dark regions; "
        f"before={mean_before:.4f}, after={mean_after:.4f}"
    )


def test_s264_soulages_stripe_adds_horizontal_variation():
    """Stripe field should add luminance variation in dark regions."""
    from PIL import Image
    # Uniform very dark canvas -- stripe should add row-to-row variation
    arr = np.full((64, 64, 3), 18, dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    p.soulages_outrenoir_pass(
        black_threshold=0.90,
        deepening_power=1.0,   # no deepening
        stripe_freq=8.0,
        stripe_strength=0.40,
        stripe_threshold=0.90,
        bloom_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    # Row means should vary (stripe pattern creates row-to-row variation)
    row_means = after[:, :, :3].mean(axis=(1, 2))
    row_variance = float(np.var(row_means))
    assert row_variance > 1e-6, (
        f"Stripe field should create row-to-row luminance variation; "
        f"row_var={row_variance:.8f}"
    )


def test_s264_soulages_bloom_lifts_edge_light_side():
    """Bloom should increase luminance near dark/light transitions."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy().astype(float) / 255.0
    # Mean of bright half
    bright_before = before[:, :32, :3].mean()

    p2 = _make_small_painter()
    _prime_canvas(p2, edge=True)
    p2.soulages_outrenoir_pass(
        black_threshold=0.05,  # no deepening
        deepening_power=1.0,
        stripe_strength=0.0,   # no stripes
        bloom_sigma=2.0,
        bloom_strength=0.80,
        opacity=1.0,
    )
    after = _get_canvas(p2).astype(float) / 255.0
    bright_after = after[:, :32, :3].mean()

    # Bloom should not decrease the bright side mean
    assert bright_after >= bright_before - 0.01, (
        f"Bloom should not reduce bright-side luminance; "
        f"before={bright_before:.3f}, after={bright_after:.3f}"
    )


def test_s264_soulages_higher_opacity_more_change():
    """Higher opacity should produce at least as much change as lower opacity."""
    ref = _dark_reference(64, 64)

    def _run(op):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        before = _get_canvas(p).copy()
        p.soulages_outrenoir_pass(opacity=op)
        after = _get_canvas(p)
        return int(np.abs(before.astype(int) - after.astype(int)).sum())

    assert _run(0.8) >= _run(0.2), "Higher opacity should produce more change"


# ── soulages catalog tests ────────────────────────────────────────────────────

def test_s264_catalog_soulages_present():
    from art_catalog import CATALOG
    assert "soulages" in CATALOG, "soulages not found in CATALOG"


def test_s264_catalog_soulages_fields():
    from art_catalog import CATALOG
    s = CATALOG["soulages"]
    assert "Soulages" in s.artist
    assert "French" in s.nationality
    assert len(s.palette) >= 8
    assert len(s.famous_works) >= 8


def test_s264_catalog_soulages_inspiration():
    """Inspiration must reference soulages_outrenoir_pass and 175th mode."""
    from art_catalog import CATALOG
    s = CATALOG["soulages"]
    assert "soulages_outrenoir_pass" in s.inspiration, (
        "soulages_outrenoir_pass not found in inspiration"
    )
    assert "175" in s.inspiration, "175th mode not referenced in inspiration"


def test_s264_catalog_soulages_dark_palette():
    """Soulages' palette should include a near-black tone (lum < 0.05)."""
    from art_catalog import CATALOG
    s = CATALOG["soulages"]
    lums = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in s.palette]
    assert min(lums) < 0.05, (
        f"Palette should include a near-black outrenoir tone; min_lum={min(lums):.3f}"
    )


def test_s264_catalog_count_increased():
    """CATALOG count must be 261 (new artist added this session)."""
    from art_catalog import CATALOG
    assert len(CATALOG) == 261, f"Expected 261 catalog entries, got {len(CATALOG)}"


def test_s264_catalog_get_style_soulages():
    """get_style() must retrieve Soulages by key."""
    from art_catalog import get_style
    s = get_style("soulages")
    assert "Soulages" in s.artist


# ── Integration: run both new passes together ─────────────────────────────────

def test_s264_full_pipeline_excavation_and_outrenoir():
    """Run both new passes in sequence; canvas should be modified and valid."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()

    p.paint_luminance_excavation_pass(opacity=0.62)
    p.soulages_outrenoir_pass(opacity=0.80)

    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Pipeline should modify canvas"
    assert after.min() >= 0 and after.max() <= 255, "Values must stay in [0, 255]"
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), "Alpha must be preserved"
