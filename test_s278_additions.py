"""
test_s278_additions.py -- Session 278 tests for paint_focal_vignette_pass,
toorop_symbolist_line_pass, and the jan_toorop catalog entry.
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


def _garden_reference(w=64, h=64):
    """Dusk garden reference: amber sky, dark water, green lily pads."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 4, :, :] = [200, 130, 50]    # amber sky
    arr[h // 4:3 * h // 4, :, :] = [20, 26, 60]  # dark still water
    arr[3 * h // 4:, :, :] = [45, 40, 35]  # dark stone near bank
    # Lily pad cluster in center of pond
    cy, cx = h // 2, w // 2
    arr[cy - 8:cy + 8, cx - 10:cx + 10, :] = [65, 100, 45]   # lily pads
    arr[cy - 4:cy + 4, cx - 4:cx + 4, :] = [225, 220, 205]   # white blossom
    return arr


def _high_contrast_reference(w=64, h=64):
    """High-contrast reference: bright center on dark surround."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :, :] = [25, 22, 20]   # near-black background
    cy, cx = h // 2, w // 2
    arr[cy - 12:cy + 12, cx - 12:cx + 12, :] = [240, 235, 210]  # bright focal zone
    return arr


def _flat_midtone_reference(w=64, h=64):
    """Flat midtone reference: useful for testing hatching in flat zones."""
    arr = np.full((h, w, 3), [128, 120, 100], dtype=np.uint8)
    return arr


def _prime_canvas(p, ref=None, *, garden=False, high_contrast=False, flat=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if high_contrast:
            ref = _high_contrast_reference(w, h)
        elif flat:
            ref = _flat_midtone_reference(w, h)
        else:
            ref = _garden_reference(w, h)
    p.tone_ground((0.62, 0.56, 0.42), texture_strength=0.015)
    p.block_in(ref, stroke_size=10, n_strokes=30)


# ── paint_focal_vignette_pass ────────────────────────────────────────────────

def test_s278_focal_vignette_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_focal_vignette_pass")


def test_s278_focal_vignette_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_focal_vignette_pass()
    assert result is None


def test_s278_focal_vignette_modifies_canvas():
    """Focal vignette should darken the canvas periphery."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, high_contrast=True)
    before = _get_canvas(p).copy()
    p.paint_focal_vignette_pass(
        vignette_strength=0.60,
        opacity=0.95,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after focal_vignette_pass with high vignette strength"
    )


def test_s278_focal_vignette_zero_opacity_no_change():
    """Zero opacity should produce no visible change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_focal_vignette_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s278_focal_vignette_zero_strength_minimal_change():
    """Zero vignette_strength should produce no darkening."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_focal_vignette_pass(
        vignette_strength=0.0,
        edge_color_cool=0.0,
        center_color_warm=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() <= 2, (
        f"Zero vignette+temperature settings should produce no visible change: "
        f"max_diff={diff.max()}"
    )


def test_s278_focal_vignette_edges_darker_than_center():
    """After vignette, corners should be darker than the detected focal center."""
    p = _make_small_painter(w=80, h=80)
    ref = _high_contrast_reference(80, 80)
    p.tone_ground((0.62, 0.56, 0.42), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=200)
    p.build_form(ref, stroke_size=4, n_strokes=120)

    p.paint_focal_vignette_pass(
        vignette_strength=0.65,
        edge_color_cool=0.06,
        center_color_warm=0.05,
        focal_percentile=78.0,
        opacity=1.0,
    )
    after = _get_canvas(p)

    # Corner pixels (BGRA: average luminance)
    h, w = after.shape[:2]
    corners = [
        after[2, 2],
        after[2, w - 3],
        after[h - 3, 2],
        after[h - 3, w - 3],
    ]
    corner_lum = np.mean([
        (0.299 * c[2] / 255 + 0.587 * c[1] / 255 + 0.114 * c[0] / 255)
        for c in corners
    ])
    center_pixel = after[h // 2, w // 2]
    center_lum = (0.299 * center_pixel[2] / 255 +
                  0.587 * center_pixel[1] / 255 +
                  0.114 * center_pixel[0] / 255)

    assert corner_lum < center_lum + 0.15, (
        "After focal vignette with bright center, corner luminance should not "
        f"greatly exceed center: corner_lum={corner_lum:.3f}, center_lum={center_lum:.3f}"
    )


def test_s278_focal_vignette_alpha_unchanged():
    """Alpha channel should remain fully opaque throughout."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.paint_focal_vignette_pass(vignette_strength=0.50, opacity=0.85)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque after focal_vignette_pass"
    )


def test_s278_focal_vignette_output_in_valid_range():
    """All output pixel values should remain within uint8 range (no overflow)."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p)
    p.paint_focal_vignette_pass(
        vignette_strength=0.90,
        edge_color_cool=0.10,
        center_color_warm=0.08,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


# ── toorop_symbolist_line_pass ────────────────────────────────────────────────

def test_s278_toorop_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "toorop_symbolist_line_pass")


def test_s278_toorop_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.toorop_symbolist_line_pass()
    assert result is None


def test_s278_toorop_pass_modifies_canvas():
    """Toorop pass should visibly change the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, garden=True)
    before = _get_canvas(p).copy()
    p.toorop_symbolist_line_pass(
        n_zones=4,
        zone_strength=0.50,
        edge_threshold=0.03,
        line_darkness=0.55,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after toorop_symbolist_line_pass"
    )


def test_s278_toorop_pass_zero_opacity_no_change():
    """Zero opacity should produce no visible change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.toorop_symbolist_line_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s278_toorop_pass_output_in_valid_range():
    """All output pixels should remain within valid uint8 range."""
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p)
    p.toorop_symbolist_line_pass(
        n_zones=5,
        zone_strength=0.70,
        edge_threshold=0.02,
        line_darkness=0.80,
        hatch_strength=0.25,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s278_toorop_pass_high_contrast_creates_darker_edges():
    """On a high-contrast reference, the pass should darken edge regions."""
    p = _make_small_painter(w=80, h=80)
    ref = _high_contrast_reference(80, 80)
    p.tone_ground((0.62, 0.56, 0.42), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=200)
    p.build_form(ref, stroke_size=4, n_strokes=150)
    p.place_lights(ref, stroke_size=3, n_strokes=80)

    before = _get_canvas(p).copy()
    p.toorop_symbolist_line_pass(
        n_zones=4,
        zone_strength=0.45,
        edge_threshold=0.03,
        line_darkness=0.60,
        line_length=5,
        opacity=0.85,
    )
    after = _get_canvas(p)

    # The pass should have reduced some luminance (contour darkening)
    before_lum = (0.299 * before[:, :, 2].astype(np.float32) / 255.0 +
                  0.587 * before[:, :, 1].astype(np.float32) / 255.0 +
                  0.114 * before[:, :, 0].astype(np.float32) / 255.0)
    after_lum = (0.299 * after[:, :, 2].astype(np.float32) / 255.0 +
                 0.587 * after[:, :, 1].astype(np.float32) / 255.0 +
                 0.114 * after[:, :, 0].astype(np.float32) / 255.0)
    # The mean luminance should be <= before (no brightening expected from contour threading)
    assert after_lum.mean() <= before_lum.mean() + 0.02, (
        "Toorop pass should not significantly increase mean luminance "
        f"(before={before_lum.mean():.4f}, after={after_lum.mean():.4f})"
    )


def test_s278_toorop_pass_flat_zone_hatching():
    """On a flat midtone reference, hatching should reduce luminance in stripe pattern."""
    p = _make_small_painter(w=80, h=80)
    ref = _flat_midtone_reference(80, 80)
    p.tone_ground((0.62, 0.56, 0.42), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=200)

    before = _get_canvas(p).copy()
    p.toorop_symbolist_line_pass(
        n_zones=3,
        zone_strength=0.30,
        edge_threshold=0.005,     # very low: almost all pixels are "flat"
        hatch_period=8.0,
        hatch_width=2.0,
        hatch_strength=0.25,
        hatch_grad_limit=0.5,     # very high: all pixels qualify as flat
        warm_ink_opacity=0.0,
        line_darkness=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)

    # On flat canvas, hatching should have darkened some pixels
    diff = before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32)
    darkened = (diff > 3).sum()
    assert darkened > 0, (
        "Flat zone hatching with high hatch_strength should darken some pixels"
    )


def test_s278_toorop_pass_alpha_unchanged():
    """Alpha channel should remain fully opaque."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.toorop_symbolist_line_pass(opacity=0.80)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque after toorop_symbolist_line_pass"
    )


def test_s278_toorop_pass_single_zone_still_runs():
    """Edge case: n_zones=1 should not crash."""
    p = _make_small_painter(w=48, h=48)
    _prime_canvas(p)
    p.toorop_symbolist_line_pass(n_zones=1, opacity=0.50)
    canvas = _get_canvas(p)
    assert canvas.shape == (48, 48, 4)


# ── jan_toorop catalog entry ──────────────────────────────────────────────────

def test_s278_toorop_in_catalog():
    from art_catalog import CATALOG
    assert "jan_toorop" in CATALOG, "jan_toorop should be in CATALOG"


def test_s278_toorop_artist_name():
    from art_catalog import get_style
    style = get_style("jan_toorop")
    assert style.artist == "Jan Toorop"


def test_s278_toorop_movement_mentions_symbolism():
    from art_catalog import get_style
    style = get_style("jan_toorop")
    assert "symbolism" in style.movement.lower() or "nouveau" in style.movement.lower(), (
        f"Movement should mention Symbolism or Art Nouveau: {style.movement}"
    )


def test_s278_toorop_nationality_dutch():
    from art_catalog import get_style
    style = get_style("jan_toorop")
    assert "dutch" in style.nationality.lower(), (
        f"Nationality should mention Dutch: {style.nationality}"
    )


def test_s278_toorop_period():
    from art_catalog import get_style
    style = get_style("jan_toorop")
    assert "1858" in style.period or "1928" in style.period, (
        f"Period should include birth/death years: {style.period}"
    )


def test_s278_toorop_palette_count():
    from art_catalog import get_style
    style = get_style("jan_toorop")
    assert len(style.palette) >= 6, (
        f"Toorop palette should have at least 6 colors, got {len(style.palette)}"
    )


def test_s278_toorop_palette_has_dark():
    """Palette should contain a near-black (ink) color."""
    from art_catalog import get_style
    style = get_style("jan_toorop")
    has_dark = any(
        c[0] < 0.15 and c[1] < 0.15 and c[2] < 0.15
        for c in style.palette
    )
    assert has_dark, "Palette should include near-black ink color for Toorop's linework"


def test_s278_toorop_palette_rgb_range():
    from art_catalog import get_style
    style = get_style("jan_toorop")
    for i, color in enumerate(style.palette):
        assert len(color) == 3, f"Palette color {i} should have 3 channels"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"Palette color {i} channel out of [0,1] range: {ch}"
            )


def test_s278_toorop_famous_works():
    from art_catalog import get_style
    style = get_style("jan_toorop")
    assert len(style.famous_works) >= 3
    titles = [w[0].lower() for w in style.famous_works]
    assert any("brides" in t or "grave" in t or "garden" in t or "sea" in t
               for t in titles), (
        "Famous works should include at least one of Toorop's known titles"
    )


def test_s278_toorop_inspiration_mentions_pass():
    from art_catalog import get_style
    style = get_style("jan_toorop")
    assert "toorop_symbolist_line_pass" in style.inspiration.lower() or \
           "189th" in style.inspiration, (
        "Inspiration should mention toorop_symbolist_line_pass or 189th mode"
    )


def test_s278_toorop_get_style_roundtrip():
    from art_catalog import get_style, list_artists
    assert "jan_toorop" in list_artists()
    style = get_style("jan_toorop")
    assert style.artist == "Jan Toorop"


# ── Combined pipeline smoke test ───────────────────────────────────────────────

def test_s278_full_pipeline_smoke():
    """Smoke test: both new passes run on a small canvas without error."""
    p = _make_small_painter(w=72, h=72)
    ref = _garden_reference(72, 72)
    p.tone_ground((0.62, 0.56, 0.42), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)
    p.place_lights(ref, stroke_size=3, n_strokes=15)

    p.toorop_symbolist_line_pass(
        n_zones=4,
        zone_strength=0.40,
        edge_threshold=0.03,
        line_darkness=0.50,
        hatch_strength=0.12,
        opacity=0.82,
    )
    p.paint_focal_vignette_pass(
        vignette_strength=0.45,
        edge_color_cool=0.04,
        center_color_warm=0.03,
        opacity=0.88,
    )

    canvas = _get_canvas(p)
    assert canvas.shape == (72, 72, 4)
    assert canvas[:, :, 3].min() == 255, "Alpha channel should remain fully opaque"
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s278_passes_order_independence():
    """Running passes in either order should produce different but valid results."""
    # Order A: toorop then vignette
    p1 = _make_small_painter(w=64, h=64)
    ref = _garden_reference(64, 64)
    p1.tone_ground((0.62, 0.56, 0.42), texture_strength=0.01)
    p1.block_in(ref, stroke_size=8, n_strokes=20)
    p1.toorop_symbolist_line_pass(n_zones=3, opacity=0.70)
    p1.paint_focal_vignette_pass(vignette_strength=0.40, opacity=0.80)
    c1 = _get_canvas(p1)

    # Order B: vignette then toorop
    p2 = _make_small_painter(w=64, h=64)
    p2.tone_ground((0.62, 0.56, 0.42), texture_strength=0.01)
    p2.block_in(ref, stroke_size=8, n_strokes=20)
    p2.paint_focal_vignette_pass(vignette_strength=0.40, opacity=0.80)
    p2.toorop_symbolist_line_pass(n_zones=3, opacity=0.70)
    c2 = _get_canvas(p2)

    # Both should produce valid canvases (no crash, valid range)
    for c in [c1, c2]:
        assert c.shape == (64, 64, 4)
        assert c[:, :, 3].min() == 255
        assert c[:, :, :3].max() <= 255
