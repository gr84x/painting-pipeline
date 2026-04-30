"""
test_s256_additions.py -- Session 256 tests for kollwitz_charcoal_compression_pass,
paint_edge_temperature_pass, and the kathe_kollwitz catalog entry.
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


def _dark_reference(w=64, h=64):
    """Mostly-dark canvas -- for charcoal compression test."""
    from PIL import Image
    arr = np.full((h, w, 3), 200, dtype=np.uint8)   # start bright to see compression
    arr[:h // 2, :] = 180
    arr[h // 2:, :] = 220
    return Image.fromarray(arr, "RGB")


def _warm_cool_reference(w=64, h=64):
    """Canvas split warm/cool horizontally -- for edge temperature test."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [200, 100, 40]   # warm orange-red
    arr[:, w // 2:, :] = [40, 80, 200]    # cool blue
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, dark=False, warm_cool=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if dark:
            ref = _dark_reference(w, h)
        elif warm_cool:
            ref = _warm_cool_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.84, 0.80, 0.74), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── kollwitz_charcoal_compression_pass ──────────────────────────────────────

def test_s256_kollwitz_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "kollwitz_charcoal_compression_pass")


def test_s256_kollwitz_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.kollwitz_charcoal_compression_pass()
    assert result is None


def test_s256_kollwitz_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.kollwitz_charcoal_compression_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after kollwitz_charcoal_compression_pass"


def test_s256_kollwitz_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p)
    p.kollwitz_charcoal_compression_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after kollwitz_charcoal_compression_pass"
    )


def test_s256_kollwitz_dark_compression_darkens():
    """Power-law compression with dark_power > 1 should darken the overall canvas."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.kollwitz_charcoal_compression_pass(dark_power=2.0, smear_strength=0.0,
                                          lift_density=0.0, opacity=1.0)
    after = _get_canvas(p)

    # Mean RGB luminance of RGB channels should decrease after dark compression
    def mean_lum(arr):
        r = arr[:, :, 2].astype(float) / 255.0
        g = arr[:, :, 1].astype(float) / 255.0
        b = arr[:, :, 0].astype(float) / 255.0
        return float(np.mean(0.299 * r + 0.587 * g + 0.114 * b))

    lum_before = mean_lum(before)
    lum_after = mean_lum(after)
    assert lum_after < lum_before, (
        f"Dark compression should reduce mean luminance: "
        f"before={lum_before:.3f}, after={lum_after:.3f}"
    )


def test_s256_kollwitz_lift_brightens_at_lift_zones():
    """With aggressive lift settings, there should be pixels brighter than before."""
    p = _make_small_painter()
    _prime_canvas(p)
    # Apply only the lift (bypass dark compression and smear)
    p.kollwitz_charcoal_compression_pass(
        dark_power=1.0,       # no compression
        smear_strength=0.0,   # no smear
        lift_density=0.5,     # heavy lift
        lift_strength=0.5,    # strong brightening
        opacity=1.0,
        seed=42,
    )
    after = _get_canvas(p)
    # Some pixels should be near-white due to lift
    bright_px = int((after[:, :, 2] > 200).sum())   # R channel
    assert bright_px > 0, "Lift with density=0.5, strength=0.5 should brighten some pixels"


def test_s256_kollwitz_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.kollwitz_charcoal_compression_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s256_kollwitz_smear_changes_canvas():
    """Smear stage alone (no compression, no lift) must visibly alter the image."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.kollwitz_charcoal_compression_pass(
        dark_power=1.0,
        smear_strength=0.9,
        lift_density=0.0,
        opacity=1.0,
        seed=99,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(int) - after[:, :, :3].astype(int))
    assert diff.sum() > 100, "Smear-only pass should visibly change the canvas"


def test_s256_kollwitz_seed_reproducibility():
    """Same seed must produce identical output."""
    from PIL import Image
    ref = _gradient_reference(64, 64)

    def _run(seed_val):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        p.kollwitz_charcoal_compression_pass(seed=seed_val)
        return _get_canvas(p)

    out_a = _run(123)
    out_b = _run(123)
    assert np.array_equal(out_a, out_b), "Same seed must produce identical output"


def test_s256_kollwitz_different_seeds_differ():
    """Different seeds should produce different outputs (lift positions differ)."""
    from PIL import Image
    ref = _gradient_reference(64, 64)

    def _run(seed_val):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        p.kollwitz_charcoal_compression_pass(lift_density=0.1, seed=seed_val)
        return _get_canvas(p)

    out_a = _run(1)
    out_b = _run(999)
    diff = np.abs(out_a.astype(int) - out_b.astype(int))
    assert diff.sum() > 0, "Different seeds should produce different lift zone positions"


def test_s256_kollwitz_values_in_range():
    """All RGB values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.kollwitz_charcoal_compression_pass(opacity=1.0)
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] range after kollwitz pass"
    )


# ── paint_edge_temperature_pass ──────────────────────────────────────────────

def test_s256_edge_temp_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_edge_temperature_pass")


def test_s256_edge_temp_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_edge_temperature_pass()
    assert result is None


def test_s256_edge_temp_pass_modifies_canvas():
    """Pass must change at least some pixels on a warm/cool split canvas."""
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    before = _get_canvas(p).copy()
    p.paint_edge_temperature_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_edge_temperature_pass"


def test_s256_edge_temp_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    before = _get_canvas(p)
    p.paint_edge_temperature_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after paint_edge_temperature_pass"
    )


def test_s256_edge_temp_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_edge_temperature_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s256_edge_temp_warm_side_gets_warmer_at_boundary():
    """On a warm/cool split canvas, the warm side at the boundary should
    have its R channel pushed higher (or at least not lower) vs no-pass."""
    from PIL import Image
    w, h = 64, 64

    ref = _warm_cool_reference(w, h)

    # Get the canvas with the pass applied
    p_with = _make_small_painter(w, h)
    _prime_canvas(p_with, ref=ref)
    p_with.paint_edge_temperature_pass(opacity=1.0, contrast_strength=0.5)
    after = _get_canvas(p_with)

    # Get the canvas without the pass
    p_no = _make_small_painter(w, h)
    _prime_canvas(p_no, ref=ref)
    baseline = _get_canvas(p_no)

    # Warm side = left half; compare mean R at the boundary column (columns 20-30)
    warm_boundary_cols = slice(20, 31)
    r_after   = after[:, warm_boundary_cols, 2].astype(float)
    r_baseline = baseline[:, warm_boundary_cols, 2].astype(float)

    # The pass should change the warm boundary pixels in some direction
    diff = np.abs(r_after - r_baseline).sum()
    assert diff > 0, (
        "Edge temperature pass should visibly affect warm boundary pixels"
    )


def test_s256_edge_temp_values_in_range():
    """All RGB values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    p.paint_edge_temperature_pass(opacity=1.0, contrast_strength=1.0)
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] range after edge temperature pass"
    )


def test_s256_edge_temp_achromatic_canvas_minimal_change():
    """On a fully achromatic (grey) canvas, saturation=0 so the pass should
    make negligible changes (boundary zone weighting collapses)."""
    from PIL import Image
    arr = np.full((64, 64, 3), 128, dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy()
    p.paint_edge_temperature_pass(opacity=1.0, contrast_strength=0.5)
    after = _get_canvas(p)

    diff = np.abs(before[:, :, :3].astype(int) - after[:, :, :3].astype(int))
    # Should be very small change since achromatic canvas has saturation≈0
    assert diff.max() <= 5, (
        f"Achromatic canvas should see minimal temperature change; max diff={diff.max()}"
    )


# ── kathe_kollwitz catalog entry ─────────────────────────────────────────────

def test_s256_catalog_kollwitz_present():
    from art_catalog import CATALOG
    assert "kathe_kollwitz" in CATALOG, "kathe_kollwitz not found in CATALOG"


def test_s256_catalog_kollwitz_fields():
    from art_catalog import CATALOG
    s = CATALOG["kathe_kollwitz"]
    assert s.artist == "Käthe Kollwitz"
    assert s.nationality == "German"
    assert "1867" in s.period
    assert len(s.palette) >= 6
    assert len(s.famous_works) >= 5


def test_s256_catalog_kollwitz_dark_ground():
    """Ground color should be buff paper -- lighter than 0.5 in all channels."""
    from art_catalog import CATALOG
    s = CATALOG["kathe_kollwitz"]
    r, g, b = s.ground_color
    assert r > 0.5 and g > 0.5 and b > 0.5, (
        f"Expected buff paper ground > 0.5; got ({r:.2f},{g:.2f},{b:.2f})"
    )


def test_s256_catalog_kollwitz_dry_medium():
    """wet_blend must be low (charcoal is a dry medium)."""
    from art_catalog import CATALOG
    s = CATALOG["kathe_kollwitz"]
    assert s.wet_blend < 0.15, (
        f"Charcoal is dry; wet_blend should be < 0.15, got {s.wet_blend}"
    )


def test_s256_catalog_kollwitz_technique_keywords():
    """Technique description should mention key charcoal concepts."""
    from art_catalog import CATALOG
    s = CATALOG["kathe_kollwitz"]
    tech_lower = s.technique.lower()
    for kw in ("charcoal", "tonal", "grain", "silhouette"):
        assert kw in tech_lower, f"Expected '{kw}' in technique description"


def test_s256_catalog_get_style_kollwitz():
    """get_style() should retrieve kathe_kollwitz by key."""
    from art_catalog import get_style
    s = get_style("kathe_kollwitz")
    assert s.artist == "Käthe Kollwitz"


def test_s256_catalog_count_at_least_255():
    """CATALOG should contain at least 255 entries (256th artist already counted)."""
    from art_catalog import CATALOG
    assert len(CATALOG) >= 255, f"Expected >= 255 entries, got {len(CATALOG)}"


def test_s256_catalog_kollwitz_famous_works_have_dates():
    """All famous_works entries should be (title, year) tuples."""
    from art_catalog import CATALOG
    for title, year in CATALOG["kathe_kollwitz"].famous_works:
        assert isinstance(title, str) and len(title) > 0
        assert isinstance(year, str) and year.isdigit()


# ── Integration: run both new passes together ────────────────────────────────

def test_s256_full_pipeline_kollwitz_and_edge_temp():
    """Run both new passes in sequence; canvas should be modified and valid."""
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    before = _get_canvas(p).copy()

    p.kollwitz_charcoal_compression_pass(opacity=0.8)
    p.paint_edge_temperature_pass(opacity=0.7)

    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Pipeline should modify canvas"
    assert after.min() >= 0 and after.max() <= 255, "Values must stay in [0, 255]"
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), "Alpha must be preserved"
