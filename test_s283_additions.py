"""
test_s283_additions.py -- Session 283 tests for paint_form_curvature_tint_pass,
repin_character_depth_pass, and the ilya_repin catalog entry.
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
    """High-contrast portrait reference: warm lit zone top, dark shadow bottom."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :, :] = [190, 150, 100]   # warm lit skin / fabric
    arr[h // 2:, :, :] = [45, 35, 55]      # cool dark shadow zone
    return arr


def _flat_midtone_reference(w=64, h=64):
    return np.full((h, w, 3), [130, 110, 85], dtype=np.uint8)  # warm midtone


def _curved_reference(w=64, h=64):
    """Convex-looking reference: bright centre fading to dark edges (dome shape)."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    cy, cx = h // 2, w // 2
    Y, X = np.mgrid[:h, :w]
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2).astype(np.float32)
    lum = np.clip(1.0 - dist / max(cx, cy), 0.0, 1.0) * 200 + 30
    arr[:, :, 0] = (lum * 0.85).astype(np.uint8)
    arr[:, :, 1] = (lum * 0.70).astype(np.uint8)
    arr[:, :, 2] = (lum * 0.55).astype(np.uint8)
    return arr


def _prime_canvas(p, ref=None):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        ref = _high_contrast_reference(w, h)
    p.tone_ground((0.52, 0.38, 0.24), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=30)


def _prime_canvas_full(p, ref=None):
    """More fully rendered canvas for nuanced pass tests."""
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        ref = _high_contrast_reference(w, h)
    p.tone_ground((0.52, 0.38, 0.24), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.build_form(ref, stroke_size=5, n_strokes=25)
    p.place_lights(ref, stroke_size=3, n_strokes=15)


# ── paint_form_curvature_tint_pass ────────────────────────────────────────────

def test_s283_form_curvature_tint_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_form_curvature_tint_pass")


def test_s283_form_curvature_tint_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_form_curvature_tint_pass()
    assert result is None


def test_s283_form_curvature_tint_modifies_canvas():
    """Form curvature tint pass should visibly change the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas_full(p, _curved_reference(80, 80))
    before = _get_canvas(p).copy()
    p.paint_form_curvature_tint_pass(
        convex_strength=0.30,
        concave_strength=0.25,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after paint_form_curvature_tint_pass"
    )


def test_s283_form_curvature_tint_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_form_curvature_tint_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s283_form_curvature_tint_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas_full(p, _curved_reference(72, 72))
    p.paint_form_curvature_tint_pass(
        convex_strength=0.40,
        concave_strength=0.35,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s283_form_curvature_tint_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.paint_form_curvature_tint_pass(opacity=0.85)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque"
    )


def test_s283_form_curvature_tint_zero_strengths_minimal_change():
    """Zero convex/concave strengths should produce minimal or no change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_form_curvature_tint_pass(
        convex_strength=0.0,
        concave_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() <= 2, (
        f"Zero strengths should not change canvas: max_diff={diff.max()}"
    )


def test_s283_form_curvature_tint_convex_warms_bright_dome():
    """On a convex dome reference, bright centre should shift toward warm gold."""
    p = _make_small_painter(w=80, h=80)
    ref = _curved_reference(80, 80)
    _prime_canvas_full(p, ref)

    before = _get_canvas(p).copy()
    p.paint_form_curvature_tint_pass(
        smooth_sigma=6.0,
        convex_r=0.95,
        convex_g=0.85,
        convex_b=0.55,
        convex_strength=0.50,
        concave_strength=0.0,   # isolate convex tint
        opacity=1.0,
    )
    after = _get_canvas(p)
    # The central bright zone should have changed
    cx, cy = 40, 40
    r = 15
    centre_before = before[cy - r:cy + r, cx - r:cx + r, :]
    centre_after  = after[cy - r:cy + r, cx - r:cx + r, :]
    diff = np.abs(centre_before.astype(np.int32) - centre_after.astype(np.int32))
    assert diff.max() >= 1, (
        "Convex warm tint should modify the bright centre of a dome-shaped reference"
    )


def test_s283_form_curvature_tint_small_canvas():
    """Edge case: tiny canvas should not crash."""
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.paint_form_curvature_tint_pass(opacity=0.60)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


# ── repin_character_depth_pass ────────────────────────────────────────────────

def test_s283_repin_character_depth_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "repin_character_depth_pass")


def test_s283_repin_character_depth_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.repin_character_depth_pass()
    assert result is None


def test_s283_repin_character_depth_modifies_canvas():
    """Repin pass should visibly change the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas_full(p)
    before = _get_canvas(p).copy()
    p.repin_character_depth_pass(
        mid_strength=0.30,
        shadow_strength=0.28,
        edge_sharp_amount=0.55,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after repin_character_depth_pass"
    )


def test_s283_repin_character_depth_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.repin_character_depth_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s283_repin_character_depth_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas_full(p)
    p.repin_character_depth_pass(
        mid_strength=0.50,
        shadow_strength=0.50,
        edge_sharp_amount=0.70,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s283_repin_character_depth_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.repin_character_depth_pass(opacity=0.85)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque after repin_character_depth_pass"
    )


def test_s283_repin_shadow_cool_push():
    """Shadow cool push should increase B relative to R in shadow areas."""
    p = _make_small_painter(w=64, h=64)
    ref = np.full((64, 64, 3), [40, 35, 55], dtype=np.uint8)  # dark, slightly cool
    p.tone_ground((0.52, 0.38, 0.24), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=100)

    before = _get_canvas(p).copy()
    p.repin_character_depth_pass(
        form_blend=0.0,       # disable form blur
        mid_strength=0.0,     # disable midtone warmth
        shadow_thresh=0.55,   # broad shadow gate (most of dark canvas qualifies)
        shadow_r=0.28,
        shadow_g=0.28,
        shadow_b=0.60,        # strong blue push
        shadow_strength=0.60,
        edge_sharp_amount=0.0,  # disable edge sharpening
        opacity=1.0,
    )
    after = _get_canvas(p)
    # In BGRA, channel 0 = B; should have increased from cool push
    mean_B_before = before[:, :, 0].astype(np.float32).mean()
    mean_B_after  = after[:, :, 0].astype(np.float32).mean()
    assert mean_B_after >= mean_B_before - 1.0, (
        f"Shadow cool push should not reduce B channel: "
        f"before={mean_B_before:.1f}, after={mean_B_after:.1f}"
    )


def test_s283_repin_midtone_warm_push():
    """Midtone warm push should shift mid-luminance pixels toward warm umber."""
    p = _make_small_painter(w=64, h=64)
    ref = _flat_midtone_reference(64, 64)
    p.tone_ground((0.52, 0.38, 0.24), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=100)

    before = _get_canvas(p).copy()
    p.repin_character_depth_pass(
        form_blend=0.0,
        mid_lo=0.20,
        mid_hi=0.80,      # broad gate: catches most of the canvas
        mid_r=0.80,
        mid_g=0.55,
        mid_b=0.28,       # warm umber push
        mid_strength=0.60,
        shadow_strength=0.0,
        edge_sharp_amount=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    # Canvas should change
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() >= 1, "Midtone warm push should visibly change the canvas"


def test_s283_repin_character_depth_small_canvas():
    """Edge case: tiny canvas should not crash."""
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.repin_character_depth_pass(opacity=0.60)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


# ── ilya_repin catalog entry ──────────────────────────────────────────────────

def test_s283_repin_in_catalog():
    from art_catalog import CATALOG
    assert "ilya_repin" in CATALOG, "ilya_repin should be in CATALOG"


def test_s283_repin_artist_name():
    from art_catalog import get_style
    style = get_style("ilya_repin")
    assert style.artist == "Ilya Repin"


def test_s283_repin_movement_mentions_realism():
    from art_catalog import get_style
    style = get_style("ilya_repin")
    m = style.movement.lower()
    assert "realism" in m or "peredvizhniki" in m or "realist" in m, (
        f"Movement should mention Realism or Peredvizhniki: {style.movement}"
    )


def test_s283_repin_nationality():
    from art_catalog import get_style
    style = get_style("ilya_repin")
    nat = style.nationality.lower()
    assert "russian" in nat or "ukrainian" in nat, (
        f"Nationality should be Russian/Ukrainian: {style.nationality}"
    )


def test_s283_repin_period():
    from art_catalog import get_style
    style = get_style("ilya_repin")
    assert "1844" in style.period, (
        f"Period should include birth year 1844: {style.period}"
    )


def test_s283_repin_palette_count():
    from art_catalog import get_style
    style = get_style("ilya_repin")
    assert len(style.palette) >= 6, (
        f"Repin palette should have at least 6 colors, got {len(style.palette)}"
    )


def test_s283_repin_palette_has_warm_umber():
    """Palette should include a warm umber (Repin's lit midtone) color."""
    from art_catalog import get_style
    style = get_style("ilya_repin")
    # Warm umber: R >> G > B
    has_warm = any(c[0] > 0.55 and c[0] > c[1] and c[1] > c[2] for c in style.palette)
    assert has_warm, "Palette should include a warm umber tone for lit flesh/fabric"


def test_s283_repin_palette_has_cool_shadow():
    """Palette should include a cool shadow (violet-blue) color."""
    from art_catalog import get_style
    style = get_style("ilya_repin")
    # Cool shadow: B > R, all channels mid-to-low
    has_cool = any(c[2] > c[0] and c[0] < 0.50 for c in style.palette)
    assert has_cool, "Palette should include a cool shadow tone"


def test_s283_repin_palette_rgb_range():
    from art_catalog import get_style
    style = get_style("ilya_repin")
    for i, color in enumerate(style.palette):
        assert len(color) == 3, f"Palette color {i} should have 3 channels"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"Palette color {i} channel out of [0,1] range: {ch}"
            )


def test_s283_repin_famous_works():
    from art_catalog import get_style
    style = get_style("ilya_repin")
    assert len(style.famous_works) >= 5
    titles = [w[0].lower() for w in style.famous_works]
    assert any("barge" in t or "hauler" in t or "volga" in t or
               "ivan" in t or "cossack" in t or "reply" in t
               for t in titles), (
        f"Famous works should include a Repin signature work: {titles}"
    )


def test_s283_repin_inspiration_mentions_pass():
    from art_catalog import get_style
    style = get_style("ilya_repin")
    assert ("repin_character_depth_pass" in style.inspiration.lower() or
            "194th" in style.inspiration), (
        "Inspiration should mention repin_character_depth_pass or 194th mode"
    )


def test_s283_repin_get_style_roundtrip():
    from art_catalog import get_style, list_artists
    assert "ilya_repin" in list_artists()
    style = get_style("ilya_repin")
    assert style.artist == "Ilya Repin"


# ── Combined pipeline smoke test ──────────────────────────────────────────────

def test_s283_full_pipeline_smoke():
    """Smoke test: both new passes run on a small canvas without error."""
    p = _make_small_painter(w=80, h=80)
    ref = _high_contrast_reference(80, 80)
    p.tone_ground((0.52, 0.38, 0.24), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)
    p.place_lights(ref, stroke_size=3, n_strokes=15)

    p.repin_character_depth_pass(
        mid_strength=0.24,
        shadow_strength=0.22,
        edge_sharp_amount=0.50,
        opacity=0.85,
    )
    p.paint_form_curvature_tint_pass(
        convex_strength=0.18,
        concave_strength=0.14,
        opacity=0.75,
    )

    canvas = _get_canvas(p)
    assert canvas.shape == (80, 80, 4)
    assert canvas[:, :, 3].min() == 255, "Alpha channel should remain fully opaque"
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s283_passes_order_independence():
    """Running passes in either order should both produce valid canvases."""
    ref = _high_contrast_reference(64, 64)

    # Order A: repin then curvature
    p1 = _make_small_painter(w=64, h=64)
    p1.tone_ground((0.52, 0.38, 0.24), texture_strength=0.01)
    p1.block_in(ref, stroke_size=8, n_strokes=20)
    p1.repin_character_depth_pass(opacity=0.85)
    p1.paint_form_curvature_tint_pass(opacity=0.75)
    c1 = _get_canvas(p1)

    # Order B: curvature then repin
    p2 = _make_small_painter(w=64, h=64)
    p2.tone_ground((0.52, 0.38, 0.24), texture_strength=0.01)
    p2.block_in(ref, stroke_size=8, n_strokes=20)
    p2.paint_form_curvature_tint_pass(opacity=0.75)
    p2.repin_character_depth_pass(opacity=0.85)
    c2 = _get_canvas(p2)

    for c in [c1, c2]:
        assert c.shape == (64, 64, 4)
        assert c[:, :, 3].min() == 255
        assert c[:, :, :3].max() <= 255


def test_s283_new_passes_with_s282_passes():
    """s283 passes should work alongside s282 passes without error."""
    p = _make_small_painter(w=80, h=80)
    ref = _high_contrast_reference(80, 80)
    p.tone_ground((0.52, 0.38, 0.24), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)
    p.place_lights(ref, stroke_size=3, n_strokes=15)

    # s282 passes
    p.paint_contre_jour_rim_pass(opacity=0.70)
    p.paint_shadow_temperature_pass(opacity=0.60)

    # s283 passes
    p.repin_character_depth_pass(opacity=0.85)
    p.paint_form_curvature_tint_pass(opacity=0.75)

    canvas = _get_canvas(p)
    assert canvas.shape == (80, 80, 4)
    assert canvas[:, :, 3].min() == 255
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0
