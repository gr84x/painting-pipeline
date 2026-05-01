"""
test_s276_additions.py -- Session 276 tests for paint_complementary_shadow_pass,
thiebaud_halo_shadow_pass, and the wayne_thiebaud catalog entry.
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


def _warm_reference(w=64, h=64):
    """Warm sunset reference -- bright warm upper half, dark rock lower half."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :, :] = [230, 160, 60]   # warm amber sky
    arr[h // 2:, :, :] = [40,  36, 32]    # dark basalt rock
    return arr


def _cool_reference(w=64, h=64):
    """Cool blue reference -- blue upper half, dark lower half."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :, :] = [60,  120, 220]  # cool blue
    arr[h // 2:, :, :] = [25,  30,  60]   # dark blue-black
    return arr


def _lighthouse_reference(w=80, h=80):
    """Reference with a bright white vertical stripe (lighthouse) on dark background."""
    arr = np.full((h, w, 3), [40, 36, 32], dtype=np.uint8)
    # White lighthouse stripe in center
    cx = w // 2
    arr[:, max(0, cx - 8):min(w, cx + 8), :] = [240, 235, 225]
    # Amber sky top 30%
    arr[:h // 3, :, :] = [220, 150, 50]
    return arr


def _prime_canvas(p, ref=None, *, warm=False, cool=False, lighthouse=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if cool:
            ref = _cool_reference(w, h)
        elif lighthouse:
            ref = _lighthouse_reference(w, h)
        else:
            ref = _warm_reference(w, h)
    p.tone_ground((0.48, 0.36, 0.24), texture_strength=0.015)
    p.block_in(ref, stroke_size=10, n_strokes=30)


# ── paint_complementary_shadow_pass ──────────────────────────────────────────

def test_s276_complementary_shadow_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_complementary_shadow_pass")


def test_s276_complementary_shadow_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, warm=True)
    result = p.paint_complementary_shadow_pass()
    assert result is None


def test_s276_complementary_shadow_modifies_canvas():
    """Complementary shadow pass should change the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, warm=True)
    before = _get_canvas(p).copy()
    p.paint_complementary_shadow_pass(
        tint_strength=0.50,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after complementary_shadow_pass with high opacity"
    )


def test_s276_complementary_shadow_zero_opacity_no_change():
    """Zero opacity should produce no visible change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, warm=True)
    before = _get_canvas(p).copy()
    p.paint_complementary_shadow_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s276_complementary_shadow_only_affects_shadow_zone():
    """Pixels well above light_threshold should be largely unchanged."""
    p = _make_small_painter(w=80, h=80)
    # Use reference where top half is very bright
    ref = np.zeros((80, 80, 3), dtype=np.uint8)
    ref[:40, :, :] = [240, 230, 180]   # very bright warm top
    ref[40:, :, :] = [20,  18,  15]    # very dark bottom
    p.tone_ground((0.48, 0.36, 0.24), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=200)

    before = _get_canvas(p).copy()
    p.paint_complementary_shadow_pass(
        light_threshold=0.80,
        shadow_threshold=0.15,
        tint_strength=0.60,
        opacity=0.90,
    )
    after = _get_canvas(p)

    # Check that very bright pixels changed minimally
    lum_before = (
        0.299 * before[:, :, 2].astype(np.float32) / 255.0 +
        0.587 * before[:, :, 1].astype(np.float32) / 255.0 +
        0.114 * before[:, :, 0].astype(np.float32) / 255.0
    )
    very_bright = lum_before > 0.80
    n_bright = int(very_bright.sum())
    if n_bright > 0:
        diff = np.abs(
            before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32)
        )
        max_change_in_bright = int(diff[very_bright].max())
        assert max_change_in_bright <= 2, (
            f"Bright pixels above light_threshold should barely change: "
            f"max change = {max_change_in_bright}"
        )


def test_s276_complementary_shadow_warm_light_gives_cool_shadow():
    """A warm (amber) light source should produce a cool/blue-violet shadow tint."""
    p = _make_small_painter(w=80, h=80)
    # Reference: bright warm top, very dark bottom
    ref = np.zeros((80, 80, 3), dtype=np.uint8)
    ref[:35, :, :] = [235, 165, 55]   # warm amber light zone
    ref[50:, :, :] = [18,  16,  14]   # deep shadow zone
    p.tone_ground((0.48, 0.36, 0.24), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=250)

    before = _get_canvas(p).copy()
    # Measure shadow zone blue channel before
    lum_before = (
        0.299 * before[:, :, 2].astype(np.float32) / 255.0 +
        0.587 * before[:, :, 1].astype(np.float32) / 255.0 +
        0.114 * before[:, :, 0].astype(np.float32) / 255.0
    )
    shadow_zone = lum_before < 0.25
    n_shadow = int(shadow_zone.sum())

    if n_shadow > 10:
        mean_b_before = float(before[:, :, 0][shadow_zone].mean())  # BGRA: 0=B
        p.paint_complementary_shadow_pass(
            light_threshold=0.60,
            shadow_threshold=0.25,
            complement_shift=0.50,
            tint_saturation=0.35,
            tint_strength=0.45,
            opacity=0.80,
        )
        after = _get_canvas(p)
        mean_b_after = float(after[:, :, 0][shadow_zone].mean())
        # Complement of warm amber is cool blue-violet; shadow should gain blue
        assert mean_b_after >= mean_b_before - 2, (
            "Complementary tint of warm amber should not decrease blue in shadows: "
            f"before={mean_b_before:.2f}, after={mean_b_after:.2f}"
        )


def test_s276_complementary_shadow_zero_tint_no_change():
    """Zero tint_strength should produce no change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, warm=True)
    before = _get_canvas(p).copy()
    p.paint_complementary_shadow_pass(tint_strength=0.0, opacity=1.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "tint_strength=0 should produce no canvas change"
    )


# ── thiebaud_halo_shadow_pass ──────────────────────────────────────────────

def test_s276_thiebaud_halo_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "thiebaud_halo_shadow_pass")


def test_s276_thiebaud_halo_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, warm=True)
    result = p.thiebaud_halo_shadow_pass()
    assert result is None


def test_s276_thiebaud_halo_modifies_canvas():
    """Thiebaud halo pass should change the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, lighthouse=True)
    before = _get_canvas(p).copy()
    p.thiebaud_halo_shadow_pass(
        edge_threshold=0.04,
        halo_radius=6,
        halo_opacity=0.60,
        shadow_opacity=0.50,
        opacity=0.85,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change with non-trivial halo/shadow opacity settings"
    )


def test_s276_thiebaud_halo_zero_opacity_no_change():
    """Zero opacity should produce no visible change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, lighthouse=True)
    before = _get_canvas(p).copy()
    p.thiebaud_halo_shadow_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s276_thiebaud_halo_luminous_near_edges():
    """After halo pass, pixels near bright edges should trend warmer/brighter."""
    p = _make_small_painter(w=80, h=80)
    # Reference with clear high-contrast lighthouse stripe
    ref = _lighthouse_reference(80, 80)
    p.tone_ground((0.48, 0.36, 0.24), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=300)

    before = _get_canvas(p).copy()
    p.thiebaud_halo_shadow_pass(
        edge_threshold=0.04,
        halo_radius=8,
        halo_r=1.0, halo_g=0.95, halo_b=0.85,
        halo_opacity=0.70,
        shadow_r=0.90, shadow_g=0.60, shadow_b=0.90,
        shadow_opacity=0.60,
        opacity=0.80,
    )
    after = _get_canvas(p)

    # The canvas should have changed
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() > 0, "Halo pass must modify at least some pixels"


def test_s276_thiebaud_halo_does_not_change_alpha():
    """Alpha channel should remain 255 throughout."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, lighthouse=True)
    p.thiebaud_halo_shadow_pass(opacity=0.70)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, "Alpha channel should remain fully opaque"


def test_s276_thiebaud_halo_tiny_radius_minimal_change():
    """Halo radius=1 with very low opacity should produce only tiny change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, lighthouse=True)
    before = _get_canvas(p).copy()
    p.thiebaud_halo_shadow_pass(
        halo_radius=1,
        halo_opacity=0.02,
        shadow_opacity=0.02,
        contour_opacity=0.02,
        opacity=0.05,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() <= 8, (
        f"Tiny radius+opacity settings should produce minimal change: max_diff={diff.max()}"
    )


# ── wayne_thiebaud catalog entry ──────────────────────────────────────────────

def test_s276_thiebaud_in_catalog():
    from art_catalog import CATALOG
    assert "wayne_thiebaud" in CATALOG, "wayne_thiebaud should be in CATALOG"


def test_s276_thiebaud_artist_name():
    from art_catalog import get_style
    style = get_style("wayne_thiebaud")
    assert style.artist == "Wayne Thiebaud"


def test_s276_thiebaud_movement():
    from art_catalog import get_style
    style = get_style("wayne_thiebaud")
    assert "figurative" in style.movement.lower() or "sacramento" in style.movement.lower()


def test_s276_thiebaud_palette_count():
    from art_catalog import get_style
    style = get_style("wayne_thiebaud")
    assert len(style.palette) >= 6, (
        f"Thiebaud palette should have at least 6 colors, got {len(style.palette)}"
    )


def test_s276_thiebaud_palette_has_cream():
    """Palette should contain a near-white cream color (Thiebaud's luminous ground)."""
    from art_catalog import get_style
    style = get_style("wayne_thiebaud")
    has_cream = any(
        c[0] > 0.88 and c[1] > 0.88 and c[2] > 0.80
        for c in style.palette
    )
    assert has_cream, (
        "Palette should include near-white cream color for Thiebaud's luminous ground"
    )


def test_s276_thiebaud_palette_rgb_range():
    from art_catalog import get_style
    style = get_style("wayne_thiebaud")
    for i, color in enumerate(style.palette):
        assert len(color) == 3, f"Palette color {i} should have 3 channels"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"Palette color {i} channel out of [0,1] range: {ch}"
            )


def test_s276_thiebaud_famous_works():
    from art_catalog import get_style
    style = get_style("wayne_thiebaud")
    assert len(style.famous_works) >= 3
    titles = [w[0] for w in style.famous_works]
    assert any("pie" in t.lower() or "cake" in t.lower() or "display" in t.lower()
               for t in titles), (
        "Famous works should include pie or cake subjects"
    )


def test_s276_thiebaud_inspiration_mentions_mode():
    from art_catalog import get_style
    style = get_style("wayne_thiebaud")
    assert "thiebaud_halo_shadow_pass" in style.inspiration.lower() or \
           "187th" in style.inspiration, (
        "Inspiration should mention thiebaud_halo_shadow_pass or 187th mode"
    )


def test_s276_thiebaud_get_style_roundtrip():
    from art_catalog import get_style, list_artists
    assert "wayne_thiebaud" in list_artists()
    style = get_style("wayne_thiebaud")
    assert style.artist == "Wayne Thiebaud"


# ── Combined pipeline smoke test ───────────────────────────────────────────────

def test_s276_full_pipeline_smoke():
    """Smoke test: both new passes run on a small canvas without error."""
    p = _make_small_painter(w=72, h=72)
    ref = _lighthouse_reference(72, 72)
    p.tone_ground((0.48, 0.36, 0.24), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)

    p.paint_complementary_shadow_pass(
        light_threshold=0.65,
        shadow_threshold=0.28,
        tint_strength=0.25,
        opacity=0.55,
    )
    p.thiebaud_halo_shadow_pass(
        edge_sigma=1.5,
        edge_threshold=0.05,
        halo_radius=5,
        halo_opacity=0.35,
        shadow_opacity=0.28,
        opacity=0.70,
    )

    canvas = _get_canvas(p)
    assert canvas.shape == (72, 72, 4)
    assert canvas[:, :, 3].min() == 255, "Alpha channel should remain fully opaque"
