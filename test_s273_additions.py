"""
test_s273_additions.py -- Session 273 tests for paint_transparent_glaze_pass,
klein_ib_field_pass, and the yves_klein catalog entry.
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


def _blue_reference(w=64, h=64):
    """IKB blue field with slight sky/sea gradient."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / float(h - 1)
        r = 0
        g = int((0.18 + t * 0.04) * 255)
        b = int((0.65 - t * 0.08) * 255)
        arr[y, :, :] = [np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255)]
    return arr


def _bright_reference(w=64, h=64):
    """Bright sky reference with luminous upper zone (for glaze test)."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :, :] = [180, 200, 240]   # bright blue-white sky
    arr[h // 2:, :, :] = [30,  50,  120]   # dark deep sea
    return arr


def _warm_reference(w=64, h=64):
    """Warm orange-yellow reference (for warm suppression test in IKB pass)."""
    arr = np.full((h, w, 3), [200, 140, 50], dtype=np.uint8)
    return arr


def _prime_canvas(p, ref=None, *, bright=False, warm=False, blue=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if bright:
            ref = _bright_reference(w, h)
        elif warm:
            ref = _warm_reference(w, h)
        else:
            ref = _blue_reference(w, h)
    p.tone_ground((0.02, 0.10, 0.52), texture_strength=0.015)
    p.block_in(ref, stroke_size=10, n_strokes=30)


# ── paint_transparent_glaze_pass ──────────────────────────────────────────────

def test_s273_transparent_glaze_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_transparent_glaze_pass")


def test_s273_transparent_glaze_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    result = p.paint_transparent_glaze_pass()
    assert result is None


def test_s273_transparent_glaze_modifies_canvas():
    """Glaze pass should change the canvas on a primed surface."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_transparent_glaze_pass(
        glaze_strength=0.50,
        coverage_density=0.90,
        opacity=0.85,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change with high glaze_strength and coverage_density"
    )


def test_s273_transparent_glaze_darkens_via_multiply():
    """A blue glaze over a bright non-blue surface must reduce red and green channels."""
    p = _make_small_painter(w=80, h=80)
    # Use a very bright, warm white-ish reference so the light zone is large
    ref = np.full((80, 80, 3), [220, 210, 180], dtype=np.uint8)
    p.tone_ground((0.02, 0.10, 0.52), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=200)

    before = _get_canvas(p).copy()
    mean_r_before = before[:, :, 2].astype(np.float32).mean()

    p.paint_transparent_glaze_pass(
        glaze_r=0.00,
        glaze_g=0.10,
        glaze_b=0.85,          # pure blue glaze -- suppresses red strongly
        light_threshold=0.20,  # low threshold so most of the bright canvas qualifies
        glaze_strength=0.55,
        coverage_density=0.90,
        opacity=0.90,
    )
    after = _get_canvas(p)
    mean_r_after = after[:, :, 2].astype(np.float32).mean()

    assert mean_r_after < mean_r_before, (
        f"Blue glaze multiply-blend should reduce red channel mean: "
        f"before={mean_r_before:.2f}, after={mean_r_after:.2f}"
    )


def test_s273_transparent_glaze_preserves_dark_pixels():
    """Pixels below light_threshold must not change -- glaze only touches lights."""
    p = _make_small_painter(w=80, h=80)
    ref = _bright_reference(80, 80)
    p.tone_ground((0.02, 0.10, 0.52), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=200)

    before = _get_canvas(p).copy()
    lum_before = (
        0.299 * before[:, :, 2].astype(np.float32) / 255.0 +
        0.587 * before[:, :, 1].astype(np.float32) / 255.0 +
        0.114 * before[:, :, 0].astype(np.float32) / 255.0
    )

    light_threshold = 0.50
    p.paint_transparent_glaze_pass(
        light_threshold=light_threshold,
        glaze_strength=0.50,
        coverage_density=0.90,
        opacity=0.90,
    )
    after = _get_canvas(p)

    # Pixels that were BELOW threshold should not change (dark zone is untouched)
    dark_mask = lum_before < light_threshold
    n_dark = int(dark_mask.sum())
    if n_dark > 0:
        diff = np.abs(
            before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32)
        )
        max_change_in_dark = int(diff[dark_mask].max())
        assert max_change_in_dark == 0, (
            f"Pixels below light_threshold should not change; "
            f"max change in dark pixels = {max_change_in_dark}"
        )


def test_s273_transparent_glaze_zero_strength_no_change():
    """Zero glaze_strength: multiply factor = 1 for all channels, no change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_transparent_glaze_pass(
        glaze_strength=0.0,
        coverage_density=0.90,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero glaze_strength (multiply factor=1) should produce no canvas change"
    )


def test_s273_transparent_glaze_zero_opacity_no_change():
    """Zero opacity should produce no visible change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_transparent_glaze_pass(
        glaze_strength=0.50,
        coverage_density=0.90,
        opacity=0.0,
    )
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


# ── klein_ib_field_pass ───────────────────────────────────────────────────────

def test_s273_klein_ib_field_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "klein_ib_field_pass")


def test_s273_klein_ib_field_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, blue=True)
    result = p.klein_ib_field_pass()
    assert result is None


def test_s273_klein_ib_field_modifies_canvas():
    """IKB field pass should modify the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, blue=True)
    before = _get_canvas(p).copy()
    p.klein_ib_field_pass(
        tint_strength=0.60,
        opacity=0.85,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change with high tint_strength and opacity"
    )


def test_s273_klein_ib_field_increases_blue():
    """IKB pass on a warm canvas should increase the mean blue channel."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, warm=True)
    before = _get_canvas(p).copy()
    mean_b_before = before[:, :, 0].astype(np.float32).mean()  # Cairo BGRA: channel 0 = B

    p.klein_ib_field_pass(
        ikb_r=0.00,
        ikb_g=0.18,
        ikb_b=0.65,
        tint_strength=0.60,
        warm_suppress=0.40,
        opacity=0.80,
    )
    after = _get_canvas(p)
    mean_b_after = after[:, :, 0].astype(np.float32).mean()

    assert mean_b_after > mean_b_before, (
        f"IKB pass should increase mean blue on warm canvas: "
        f"before={mean_b_before:.2f}, after={mean_b_after:.2f}"
    )


def test_s273_klein_ib_field_suppresses_warm():
    """On warm input, the red channel should decrease after warm suppression."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, warm=True)
    before = _get_canvas(p).copy()
    mean_r_before = before[:, :, 2].astype(np.float32).mean()  # Cairo BGRA: channel 2 = R

    p.klein_ib_field_pass(
        tint_strength=0.50,
        warm_suppress=0.60,
        opacity=0.80,
    )
    after = _get_canvas(p)
    mean_r_after = after[:, :, 2].astype(np.float32).mean()

    assert mean_r_after < mean_r_before, (
        f"Warm suppression should reduce mean red on warm canvas: "
        f"before={mean_r_before:.2f}, after={mean_r_after:.2f}"
    )


def test_s273_klein_ib_field_zero_opacity_no_change():
    """Zero opacity should produce no visible change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, blue=True)
    before = _get_canvas(p).copy()
    p.klein_ib_field_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s273_klein_ib_field_deterministic():
    """Same seed should produce identical results."""
    p1 = _make_small_painter(w=80, h=80)
    _prime_canvas(p1, blue=True)
    p1.klein_ib_field_pass(texture_seed=42, opacity=0.70)
    result1 = _get_canvas(p1).copy()

    p2 = _make_small_painter(w=80, h=80)
    _prime_canvas(p2, blue=True)
    p2.klein_ib_field_pass(texture_seed=42, opacity=0.70)
    result2 = _get_canvas(p2)

    assert np.array_equal(result1, result2), (
        "Same texture_seed should produce identical IKB micro-texture pattern"
    )


def test_s273_klein_ib_field_different_seeds():
    """Different seeds should produce different micro-textures."""
    p1 = _make_small_painter(w=80, h=80)
    _prime_canvas(p1, blue=True)
    p1.klein_ib_field_pass(texture_seed=100, opacity=0.70, tint_strength=0.50)
    result1 = _get_canvas(p1).copy()

    p2 = _make_small_painter(w=80, h=80)
    _prime_canvas(p2, blue=True)
    p2.klein_ib_field_pass(texture_seed=999, opacity=0.70, tint_strength=0.50)
    result2 = _get_canvas(p2)

    assert not np.array_equal(result1, result2), (
        "Different texture_seed values should produce different micro-texture patterns"
    )


# ── yves_klein catalog entry ───────────────────────────────────────────────────

def test_s273_yves_klein_in_catalog():
    from art_catalog import CATALOG
    assert "yves_klein" in CATALOG, "yves_klein should be in CATALOG"


def test_s273_yves_klein_artist_name():
    from art_catalog import get_style
    style = get_style("yves_klein")
    assert style.artist == "Yves Klein"


def test_s273_yves_klein_movement():
    from art_catalog import get_style
    style = get_style("yves_klein")
    assert "Réalisme" in style.movement or "Monochromism" in style.movement


def test_s273_yves_klein_palette_count():
    from art_catalog import get_style
    style = get_style("yves_klein")
    assert len(style.palette) >= 6, (
        f"Yves Klein palette should have at least 6 colors, got {len(style.palette)}"
    )


def test_s273_yves_klein_palette_has_ikb():
    """Palette should contain a color with high blue and low red (IKB)."""
    from art_catalog import get_style
    style = get_style("yves_klein")
    has_ikb = any(
        c[2] > 0.50 and c[0] < 0.10
        for c in style.palette
    )
    assert has_ikb, "Palette should include a color with high blue (>0.5) and low red (<0.1) -- IKB"


def test_s273_yves_klein_palette_rgb_range():
    from art_catalog import get_style
    style = get_style("yves_klein")
    for i, color in enumerate(style.palette):
        assert len(color) == 3, f"Palette color {i} should have 3 channels"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"Palette color {i} channel out of [0,1] range: {ch}"
            )


def test_s273_yves_klein_famous_works():
    from art_catalog import get_style
    style = get_style("yves_klein")
    assert len(style.famous_works) >= 3
    titles = [w[0] for w in style.famous_works]
    assert any("IKB" in t or "Blue" in t or "Void" in t for t in titles), (
        "Famous works should include IKB or Void works"
    )


def test_s273_yves_klein_inspiration_mentions_mode():
    from art_catalog import get_style
    style = get_style("yves_klein")
    assert "klein_ib_field_pass" in style.inspiration.lower() or \
           "184th" in style.inspiration, (
        "Inspiration should mention klein_ib_field_pass or 184th mode"
    )


def test_s273_yves_klein_get_style_roundtrip():
    from art_catalog import get_style, list_artists
    assert "yves_klein" in list_artists()
    style = get_style("yves_klein")
    assert style.artist == "Yves Klein"


# ── Combined pipeline smoke test ───────────────────────────────────────────────

def test_s273_full_pipeline_smoke():
    """Smoke test: both new passes run on a small canvas without error."""
    p = _make_small_painter(w=72, h=72)
    ref = _blue_reference(72, 72)
    p.tone_ground((0.02, 0.10, 0.52), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)

    p.paint_transparent_glaze_pass(
        glaze_r=0.00,
        glaze_g=0.12,
        glaze_b=0.72,
        light_threshold=0.25,
        glaze_strength=0.30,
        coverage_density=0.65,
        opacity=0.60,
    )
    p.klein_ib_field_pass(
        ikb_r=0.00,
        ikb_g=0.18,
        ikb_b=0.65,
        tint_strength=0.40,
        warm_suppress=0.28,
        opacity=0.70,
    )

    canvas = _get_canvas(p)
    assert canvas.shape == (72, 72, 4)
    assert canvas[:, :, 3].min() == 255, "Alpha channel should remain fully opaque"
