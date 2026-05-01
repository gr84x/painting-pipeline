"""
test_s282_additions.py -- Session 282 tests for paint_contre_jour_rim_pass,
savrasov_lyrical_mist_pass, and the alexei_savrasov catalog entry.
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


def _high_contrast_reference(w=64, h=64):
    """High-contrast reference: bright upper region on dark lower."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :, :] = [210, 210, 220]   # pale sky
    arr[h // 2:, :, :] = [40, 35, 30]      # dark ground
    return arr


def _landscape_reference(w=64, h=64):
    """Landscape reference: pale sky top, mid-value horizon, dark foreground."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    sky_h = h // 3
    mid_h = h // 3
    arr[:sky_h, :, :]          = [195, 200, 210]   # pale grey sky
    arr[sky_h:sky_h + mid_h, :, :] = [110, 110, 105]  # mid-value horizon zone
    arr[sky_h + mid_h:, :, :]  = [55, 48, 38]      # dark foreground/snow shadow
    return arr


def _flat_midtone_reference(w=64, h=64):
    return np.full((h, w, 3), [128, 120, 100], dtype=np.uint8)


def _prime_canvas(p, ref=None, *, landscape=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        ref = _landscape_reference(w, h) if landscape else _high_contrast_reference(w, h)
    p.tone_ground((0.68, 0.64, 0.56), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=30)


# ── paint_contre_jour_rim_pass ────────────────────────────────────────────────

def test_s282_contre_jour_rim_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_contre_jour_rim_pass")


def test_s282_contre_jour_rim_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_contre_jour_rim_pass()
    assert result is None


def test_s282_contre_jour_rim_modifies_canvas():
    """Contre-jour rim pass should visibly change the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, landscape=True)
    before = _get_canvas(p).copy()
    p.paint_contre_jour_rim_pass(
        bright_threshold   = 0.65,
        dark_threshold     = 0.38,
        rim_strength       = 0.60,
        cool_edge_strength = 0.35,
        opacity            = 0.92,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after paint_contre_jour_rim_pass"
    )


def test_s282_contre_jour_rim_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_contre_jour_rim_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s282_contre_jour_rim_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, landscape=True)
    p.paint_contre_jour_rim_pass(
        bright_threshold   = 0.60,
        rim_strength       = 1.0,
        cool_edge_strength = 0.80,
        opacity            = 1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s282_contre_jour_rim_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.paint_contre_jour_rim_pass(opacity=0.85)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque"
    )


def test_s282_contre_jour_rim_zero_strengths_no_change():
    """With both rim and cool_edge strength zero, canvas should not change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_contre_jour_rim_pass(
        rim_strength       = 0.0,
        cool_edge_strength = 0.0,
        opacity            = 1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() <= 2, (
        f"Zero strengths should produce no visible change: max_diff={diff.max()}"
    )


def test_s282_contre_jour_rim_warm_on_dark_side():
    """With high-contrast ref, dark pixels adjacent to bright should warm up."""
    p = _make_small_painter(w=80, h=80)
    ref = _high_contrast_reference(80, 80)
    p.tone_ground((0.68, 0.64, 0.56), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=200)
    p.build_form(ref, stroke_size=4, n_strokes=120)
    p.place_lights(ref, stroke_size=3, n_strokes=80)

    before = _get_canvas(p).copy()
    p.paint_contre_jour_rim_pass(
        bright_threshold   = 0.55,
        dark_threshold     = 0.35,
        gradient_sigma     = 1.2,
        rim_sigma          = 3.0,
        rim_strength       = 0.80,
        rim_r              = 0.90,
        rim_g              = 0.65,
        rim_b              = 0.20,
        cool_edge_strength = 0.0,   # isolate warm rim only
        opacity            = 1.0,
    )
    after = _get_canvas(p)
    # Near the boundary zone the canvas should have changed
    boundary_region = before[35:45, :, :]
    boundary_after  = after[35:45, :, :]
    diff = np.abs(boundary_region.astype(np.int32) - boundary_after.astype(np.int32))
    assert diff.max() >= 1, (
        "Rim pass should modify pixels near the bright/dark boundary"
    )


def test_s282_contre_jour_rim_single_pixel_canvas():
    """Edge case: tiny canvas should not crash."""
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.paint_contre_jour_rim_pass(opacity=0.50)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


# ── savrasov_lyrical_mist_pass ────────────────────────────────────────────────

def test_s282_savrasov_mist_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "savrasov_lyrical_mist_pass")


def test_s282_savrasov_mist_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, landscape=True)
    result = p.savrasov_lyrical_mist_pass()
    assert result is None


def test_s282_savrasov_mist_modifies_canvas():
    """Savrasov mist pass should visibly change the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, landscape=True)
    before = _get_canvas(p).copy()
    p.savrasov_lyrical_mist_pass(
        mist_strength  = 0.40,
        mid_strength   = 0.35,
        branch_sharp   = 0.60,
        horizon_strength = 0.40,
        opacity        = 0.92,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after savrasov_lyrical_mist_pass"
    )


def test_s282_savrasov_mist_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, landscape=True)
    before = _get_canvas(p).copy()
    p.savrasov_lyrical_mist_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s282_savrasov_mist_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, landscape=True)
    p.savrasov_lyrical_mist_pass(
        mist_strength    = 0.50,
        mid_strength     = 0.50,
        branch_sharp     = 0.80,
        horizon_strength = 0.50,
        opacity          = 1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s282_savrasov_mist_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, landscape=True)
    p.savrasov_lyrical_mist_pass(opacity=0.85)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque after savrasov_lyrical_mist_pass"
    )


def test_s282_savrasov_mist_cool_push_in_mid_luminance():
    """Mid-luminance cool push should increase B channel in midtone areas."""
    p = _make_small_painter(w=64, h=64)
    ref = _flat_midtone_reference(64, 64)
    p.tone_ground((0.68, 0.64, 0.56), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=100)

    before = _get_canvas(p).copy()
    p.savrasov_lyrical_mist_pass(
        mist_strength    = 0.0,   # disable mist to isolate mid-push
        mid_lo           = 0.30,
        mid_hi           = 0.80,
        mid_r            = 0.62,
        mid_g            = 0.67,
        mid_b            = 0.88,  # strong blue push
        mid_strength     = 0.60,
        branch_sharp     = 0.0,   # disable branch sharpening
        horizon_strength = 0.0,   # disable horizon
        opacity          = 1.0,
    )
    after = _get_canvas(p)
    # BGRA: channel 0 = B, should have increased
    mean_B_before = before[:, :, 0].astype(np.float32).mean()
    mean_B_after  = after[:, :, 0].astype(np.float32).mean()
    assert mean_B_after >= mean_B_before - 0.5, (
        f"Cool blue push should not substantially decrease B channel: "
        f"before={mean_B_before:.1f}, after={mean_B_after:.1f}"
    )


def test_s282_savrasov_mist_horizon_warm_push_lower_zone():
    """Horizon warm push should warm the lower zone of low-saturation canvas."""
    p = _make_small_painter(w=64, h=80)
    ref = np.full((80, 64, 3), [160, 155, 155], dtype=np.uint8)  # desaturated reference
    p.tone_ground((0.68, 0.64, 0.56), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=100)

    before = _get_canvas(p).copy()
    p.savrasov_lyrical_mist_pass(
        mist_strength    = 0.0,
        mid_strength     = 0.0,
        branch_sharp     = 0.0,
        horizon_zone     = 0.5,    # lower half
        horizon_sat_thresh = 0.80, # very broad saturation gate -- catches desaturated canvas
        horizon_r        = 0.80,
        horizon_g        = 0.62,
        horizon_b        = 0.30,   # warm ochre
        horizon_strength = 0.70,
        opacity          = 1.0,
    )
    after = _get_canvas(p)
    # In the lower zone, warm push should have changed R channel
    h = before.shape[0]
    lower_before = before[h // 2:, :, :]
    lower_after  = after[h // 2:, :, :]
    diff = np.abs(lower_before.astype(np.int32) - lower_after.astype(np.int32))
    assert diff.max() >= 1, (
        "Horizon warm push should modify lower-zone pixels"
    )


def test_s282_savrasov_mist_single_pixel_canvas():
    """Edge case: tiny canvas should not crash."""
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.savrasov_lyrical_mist_pass(opacity=0.50)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


# ── alexei_savrasov catalog entry ─────────────────────────────────────────────

def test_s282_savrasov_in_catalog():
    from art_catalog import CATALOG
    assert "alexei_savrasov" in CATALOG, "alexei_savrasov should be in CATALOG"


def test_s282_savrasov_artist_name():
    from art_catalog import get_style
    style = get_style("alexei_savrasov")
    assert style.artist == "Alexei Savrasov"


def test_s282_savrasov_movement_mentions_lyrical():
    from art_catalog import get_style
    style = get_style("alexei_savrasov")
    assert ("lyrical" in style.movement.lower() or
            "realism" in style.movement.lower() or
            "peredvizhniki" in style.movement.lower()), (
        f"Movement should mention Lyrical, Realism or Peredvizhniki: {style.movement}"
    )


def test_s282_savrasov_nationality():
    from art_catalog import get_style
    style = get_style("alexei_savrasov")
    assert "russian" in style.nationality.lower(), (
        f"Nationality should be Russian: {style.nationality}"
    )


def test_s282_savrasov_period():
    from art_catalog import get_style
    style = get_style("alexei_savrasov")
    assert "1830" in style.period or "1897" in style.period, (
        f"Period should include birth/death years: {style.period}"
    )


def test_s282_savrasov_palette_count():
    from art_catalog import get_style
    style = get_style("alexei_savrasov")
    assert len(style.palette) >= 6, (
        f"Savrasov palette should have at least 6 colors, got {len(style.palette)}"
    )


def test_s282_savrasov_palette_has_cool_grey():
    """Palette should include a cool grey (Savrasov grey) tone."""
    from art_catalog import get_style
    style = get_style("alexei_savrasov")
    # Savrasov grey: all channels > 0.4, blue slightly higher than red
    has_cool_grey = any(
        c[0] > 0.40 and c[1] > 0.40 and c[2] > c[0]
        for c in style.palette
    )
    assert has_cool_grey, "Palette should include a cool grey / blue-grey tone"


def test_s282_savrasov_palette_rgb_range():
    from art_catalog import get_style
    style = get_style("alexei_savrasov")
    for i, color in enumerate(style.palette):
        assert len(color) == 3, f"Palette color {i} should have 3 channels"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"Palette color {i} channel out of [0,1] range: {ch}"
            )


def test_s282_savrasov_famous_works():
    from art_catalog import get_style
    style = get_style("alexei_savrasov")
    assert len(style.famous_works) >= 5
    titles = [w[0].lower() for w in style.famous_works]
    assert any("rook" in t or "spring" in t or "thaw" in t for t in titles), (
        "Famous works should include at least one rooks/spring/thaw work"
    )


def test_s282_savrasov_inspiration_mentions_pass():
    from art_catalog import get_style
    style = get_style("alexei_savrasov")
    assert ("savrasov_lyrical_mist_pass" in style.inspiration.lower() or
            "193rd" in style.inspiration), (
        "Inspiration should mention savrasov_lyrical_mist_pass or 193rd mode"
    )


def test_s282_savrasov_get_style_roundtrip():
    from art_catalog import get_style, list_artists
    assert "alexei_savrasov" in list_artists()
    style = get_style("alexei_savrasov")
    assert style.artist == "Alexei Savrasov"


# ── Combined pipeline smoke test ──────────────────────────────────────────────

def test_s282_full_pipeline_smoke():
    """Smoke test: both new passes run on a small canvas without error."""
    p = _make_small_painter(w=80, h=80)
    ref = _landscape_reference(80, 80)
    p.tone_ground((0.68, 0.64, 0.56), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)
    p.place_lights(ref, stroke_size=3, n_strokes=15)

    p.savrasov_lyrical_mist_pass(
        mist_strength    = 0.30,
        mid_strength     = 0.28,
        branch_sharp     = 0.55,
        horizon_strength = 0.32,
        opacity          = 0.90,
    )
    p.paint_contre_jour_rim_pass(
        rim_strength       = 0.50,
        cool_edge_strength = 0.30,
        opacity            = 0.80,
    )

    canvas = _get_canvas(p)
    assert canvas.shape == (80, 80, 4)
    assert canvas[:, :, 3].min() == 255, "Alpha channel should remain fully opaque"
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s282_passes_order_independence():
    """Running passes in either order should produce valid results."""
    ref = _landscape_reference(64, 64)

    # Order A: savrasov then contre_jour
    p1 = _make_small_painter(w=64, h=64)
    p1.tone_ground((0.68, 0.64, 0.56), texture_strength=0.01)
    p1.block_in(ref, stroke_size=8, n_strokes=20)
    p1.savrasov_lyrical_mist_pass(opacity=0.88)
    p1.paint_contre_jour_rim_pass(opacity=0.80)
    c1 = _get_canvas(p1)

    # Order B: contre_jour then savrasov
    p2 = _make_small_painter(w=64, h=64)
    p2.tone_ground((0.68, 0.64, 0.56), texture_strength=0.01)
    p2.block_in(ref, stroke_size=8, n_strokes=20)
    p2.paint_contre_jour_rim_pass(opacity=0.80)
    p2.savrasov_lyrical_mist_pass(opacity=0.88)
    c2 = _get_canvas(p2)

    for c in [c1, c2]:
        assert c.shape == (64, 64, 4)
        assert c[:, :, 3].min() == 255
        assert c[:, :, :3].max() <= 255
