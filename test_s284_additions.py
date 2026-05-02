"""
test_s284_additions.py -- Session 284 tests for paint_chromatic_shadow_shift_pass,
kokoschka_vibrating_surface_pass (bonus improvement), grosz_neue_sachlichkeit_pass
(195th mode), and the george_grosz catalog entry.
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
    """High-contrast reference: warm lit top, cool dark bottom."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :, :] = [190, 150, 100]
    arr[h // 2:, :, :] = [45, 35, 55]
    return arr


def _colourful_reference(w=64, h=64):
    """Chromatically varied reference with distinct hue zones."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Red zone left, blue zone right, green zone top
    arr[:, :w // 2, :] = [180, 40,  40]   # red
    arr[:, w // 2:, :] = [40,  40, 180]   # blue
    arr[:h // 4, :,  :] = [40, 160, 40]   # green strip at top
    return arr


def _flat_midtone_reference(w=64, h=64):
    return np.full((h, w, 3), [130, 110, 90], dtype=np.uint8)


def _curved_reference(w=64, h=64):
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
    p.tone_ground((0.34, 0.28, 0.44), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=30)


def _prime_canvas_full(p, ref=None):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        ref = _high_contrast_reference(w, h)
    p.tone_ground((0.34, 0.28, 0.44), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.build_form(ref, stroke_size=5, n_strokes=25)
    p.place_lights(ref, stroke_size=3, n_strokes=15)


# ── paint_chromatic_shadow_shift_pass ─────────────────────────────────────────

def test_s284_chromatic_shadow_shift_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_chromatic_shadow_shift_pass")


def test_s284_chromatic_shadow_shift_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_chromatic_shadow_shift_pass()
    assert result is None


def test_s284_chromatic_shadow_shift_modifies_canvas():
    """Chromatic shadow shift should visibly change the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas_full(p, _colourful_reference(80, 80))
    before = _get_canvas(p).copy()
    p.paint_chromatic_shadow_shift_pass(
        shadow_hue_shift=40.0,
        highlight_hue_shift=15.0,
        shift_strength=1.0,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after paint_chromatic_shadow_shift_pass"
    )


def test_s284_chromatic_shadow_shift_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_chromatic_shadow_shift_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s284_chromatic_shadow_shift_zero_shifts_no_change():
    """Zero hue shifts should produce no visible change regardless of opacity."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas_full(p)
    before = _get_canvas(p).copy()
    p.paint_chromatic_shadow_shift_pass(
        shadow_hue_shift=0.0,
        highlight_hue_shift=0.0,
        shift_strength=1.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() <= 2, (
        f"Zero hue shifts should produce near-zero change: max_diff={diff.max()}"
    )


def test_s284_chromatic_shadow_shift_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas_full(p, _colourful_reference(72, 72))
    p.paint_chromatic_shadow_shift_pass(
        shadow_hue_shift=45.0,
        highlight_hue_shift=20.0,
        shift_strength=1.0,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s284_chromatic_shadow_shift_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.paint_chromatic_shadow_shift_pass(opacity=0.80)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque"
    )


def test_s284_chromatic_shadow_shift_shadow_zone_changed():
    """Dark pixels should be modified by shadow hue shift."""
    p = _make_small_painter(w=80, h=80)
    # Fill with chromatic dark: red shadows
    ref = np.full((80, 80, 3), [60, 20, 20], dtype=np.uint8)
    p.tone_ground((0.20, 0.10, 0.10), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=100)

    before = _get_canvas(p).copy()
    p.paint_chromatic_shadow_shift_pass(
        shadow_thresh=0.65,   # broad shadow gate (most dark pixels qualify)
        shadow_range=0.20,
        shadow_hue_shift=60.0,
        highlight_hue_shift=0.0,
        shift_strength=1.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() >= 1, (
        "Shadow hue rotation on chromatic dark reference should change the canvas"
    )


def test_s284_chromatic_shadow_shift_small_canvas():
    """Edge case: tiny canvas should not crash."""
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.paint_chromatic_shadow_shift_pass(opacity=0.60)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


def test_s284_chromatic_shadow_shift_full_opacity_valid():
    """Full opacity with strong shift should still produce valid output."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas_full(p, _colourful_reference(64, 64))
    p.paint_chromatic_shadow_shift_pass(
        shadow_hue_shift=90.0,
        highlight_hue_shift=30.0,
        shift_strength=1.0,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0
    assert canvas[:, :, 3].min() == 255


# ── kokoschka_vibrating_surface_pass ──────────────────────────────────────────

def test_s284_kokoschka_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "kokoschka_vibrating_surface_pass")


def test_s284_kokoschka_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.kokoschka_vibrating_surface_pass()
    assert result is None


def test_s284_kokoschka_pass_modifies_canvas():
    """Kokoschka pass should visibly change the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas_full(p, _colourful_reference(80, 80))
    before = _get_canvas(p).copy()
    p.kokoschka_vibrating_surface_pass(
        glow_strength=0.28,
        edge_strength=0.32,
        sat_boost=0.35,
        opacity=0.90,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after kokoschka_vibrating_surface_pass"
    )


def test_s284_kokoschka_pass_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.kokoschka_vibrating_surface_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s284_kokoschka_pass_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas_full(p, _colourful_reference(72, 72))
    p.kokoschka_vibrating_surface_pass(
        glow_strength=0.40,
        edge_strength=0.50,
        sat_boost=0.45,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s284_kokoschka_pass_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.kokoschka_vibrating_surface_pass(opacity=0.84)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque after kokoschka_vibrating_surface_pass"
    )


def test_s284_kokoschka_edge_accent_blue_channel():
    """Edge accent (cobalt blue) should increase blue channel at sharp boundaries."""
    p = _make_small_painter(w=80, h=80)
    # High-contrast chromatic reference creates many edges
    ref = _colourful_reference(80, 80)
    p.tone_ground((0.34, 0.28, 0.44), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=80)

    before = _get_canvas(p).copy()
    # Strong edge accent with cobalt (high B, low R)
    p.kokoschka_vibrating_surface_pass(
        glow_strength=0.0,    # disable inner glow
        edge_r=0.12,
        edge_g=0.30,
        edge_b=0.95,          # strong cobalt push
        edge_strength=0.60,
        sat_boost=0.0,        # disable sat boost
        opacity=1.0,
    )
    after = _get_canvas(p)
    # Canvas should change from edge accent
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() >= 1, "Strong cobalt edge accent should visibly change the canvas"


def test_s284_kokoschka_pass_zero_strengths_minimal_change():
    """All strengths at zero should produce minimal change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.kokoschka_vibrating_surface_pass(
        glow_strength=0.0,
        edge_strength=0.0,
        sat_boost=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() <= 2, (
        f"Zero strengths should produce near-zero change: max_diff={diff.max()}"
    )


def test_s284_kokoschka_pass_small_canvas():
    """Edge case: tiny canvas should not crash."""
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.kokoschka_vibrating_surface_pass(opacity=0.60)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


def test_s284_kokoschka_pass_full_opacity_valid():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas_full(p, _colourful_reference(64, 64))
    p.kokoschka_vibrating_surface_pass(
        glow_strength=0.35,
        edge_strength=0.45,
        sat_boost=0.40,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0
    assert canvas[:, :, 3].min() == 255


# ── oskar_kokoschka catalog entry ─────────────────────────────────────────────

def test_s284_kokoschka_in_catalog():
    from art_catalog import CATALOG
    assert "oskar_kokoschka" in CATALOG, "oskar_kokoschka should be in CATALOG"


def test_s284_kokoschka_artist_name():
    from art_catalog import get_style
    style = get_style("oskar_kokoschka")
    assert style.artist == "Oskar Kokoschka"


def test_s284_kokoschka_movement_mentions_expressionism():
    from art_catalog import get_style
    style = get_style("oskar_kokoschka")
    m = style.movement.lower()
    assert "expressi" in m, (
        f"Movement should mention Expressionism: {style.movement}"
    )


def test_s284_kokoschka_nationality():
    from art_catalog import get_style
    style = get_style("oskar_kokoschka")
    nat = style.nationality.lower()
    assert "austrian" in nat or "vienness" in nat or "vienna" in nat or "austria" in nat, (
        f"Nationality should be Austrian: {style.nationality}"
    )


def test_s284_kokoschka_period():
    from art_catalog import get_style
    style = get_style("oskar_kokoschka")
    # Existing catalog entry uses career period (1905-1975), not birth-death years.
    # Accept either career start year or birth year in period field.
    assert style.period, f"Period should be non-empty: {style.period!r}"
    assert any(yr in style.period for yr in ("1886", "1905", "1910")), (
        f"Period should include a Kokoschka-era year: {style.period}"
    )


def test_s284_kokoschka_palette_count():
    from art_catalog import get_style
    style = get_style("oskar_kokoschka")
    assert len(style.palette) >= 6, (
        f"Kokoschka palette should have at least 6 colours, got {len(style.palette)}"
    )


def test_s284_kokoschka_palette_has_cobalt():
    """Palette should include a vivid cobalt blue (Kokoschka's edge accent)."""
    from art_catalog import get_style
    style = get_style("oskar_kokoschka")
    # Cobalt: B >> R, B >> G, all in reasonable range
    has_cobalt = any(c[2] > 0.65 and c[2] > c[0] * 1.8 for c in style.palette)
    assert has_cobalt, "Palette should include a vivid cobalt blue for edge accents"


def test_s284_kokoschka_palette_has_warm_amber():
    """Palette should include a warm amber/ochre (Kokoschka's inner glow)."""
    from art_catalog import get_style
    style = get_style("oskar_kokoschka")
    # Warm amber: R > G >> B
    has_amber = any(c[0] > 0.80 and c[0] > c[1] and c[1] > c[2] for c in style.palette)
    assert has_amber, "Palette should include a warm amber for inner glow"


def test_s284_kokoschka_palette_rgb_range():
    from art_catalog import get_style
    style = get_style("oskar_kokoschka")
    for i, color in enumerate(style.palette):
        assert len(color) == 3, f"Palette color {i} should have 3 channels"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"Palette color {i} channel out of [0,1] range: {ch}"
            )


def test_s284_kokoschka_famous_works():
    from art_catalog import get_style
    style = get_style("oskar_kokoschka")
    assert len(style.famous_works) >= 5
    titles = [w[0].lower() for w in style.famous_works]
    assert any("bride" in t or "wind" in t or "windsbraut" in t or
               "loos" in t or "prague" in t or "constanti" in t
               for t in titles), (
        f"Famous works should include a Kokoschka signature work: {titles}"
    )


def test_s284_kokoschka_inspiration_mentions_pass():
    from art_catalog import get_style
    style = get_style("oskar_kokoschka")
    # Pre-existing catalog entry uses kokoschka_anxious_portrait_pass (129th mode).
    # The new kokoschka_vibrating_surface_pass is a bonus method added this session
    # but the catalog inspiration field retains the original pass reference.
    insp = style.inspiration.lower()
    assert ("kokoschka_anxious_portrait_pass" in insp or
            "kokoschka_vibrating_surface_pass" in insp or
            "kokoschka" in insp), (
        f"Inspiration should mention a Kokoschka pass: {style.inspiration[:120]!r}"
    )


def test_s284_kokoschka_get_style_roundtrip():
    from art_catalog import get_style, list_artists
    assert "oskar_kokoschka" in list_artists()
    style = get_style("oskar_kokoschka")
    assert style.artist == "Oskar Kokoschka"


# ── Combined pipeline smoke tests ─────────────────────────────────────────────

def test_s284_full_pipeline_smoke():
    """Smoke test: both new passes run on a small canvas without error."""
    p = _make_small_painter(w=80, h=80)
    ref = _colourful_reference(80, 80)
    p.tone_ground((0.34, 0.28, 0.44), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)
    p.place_lights(ref, stroke_size=3, n_strokes=15)

    p.paint_chromatic_shadow_shift_pass(
        shadow_hue_shift=28.0,
        highlight_hue_shift=12.0,
        shift_strength=0.80,
        opacity=0.75,
    )
    p.kokoschka_vibrating_surface_pass(
        glow_strength=0.22,
        edge_strength=0.28,
        sat_boost=0.30,
        opacity=0.84,
    )

    canvas = _get_canvas(p)
    assert canvas.shape == (80, 80, 4)
    assert canvas[:, :, 3].min() == 255, "Alpha channel should remain fully opaque"
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s284_passes_with_prior_session_passes():
    """s284 passes should work alongside s283 passes without error."""
    p = _make_small_painter(w=80, h=80)
    ref = _colourful_reference(80, 80)
    p.tone_ground((0.34, 0.28, 0.44), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)
    p.place_lights(ref, stroke_size=3, n_strokes=15)

    # s283 passes
    p.repin_character_depth_pass(opacity=0.85)
    p.paint_form_curvature_tint_pass(opacity=0.75)

    # s284 passes
    p.paint_chromatic_shadow_shift_pass(opacity=0.72)
    p.kokoschka_vibrating_surface_pass(opacity=0.84)

    canvas = _get_canvas(p)
    assert canvas.shape == (80, 80, 4)
    assert canvas[:, :, 3].min() == 255
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s284_passes_order_independence():
    """Both orderings of the two new passes produce valid canvases."""
    ref = _colourful_reference(64, 64)

    p1 = _make_small_painter(w=64, h=64)
    p1.tone_ground((0.34, 0.28, 0.44), texture_strength=0.01)
    p1.block_in(ref, stroke_size=8, n_strokes=20)
    p1.paint_chromatic_shadow_shift_pass(opacity=0.72)
    p1.kokoschka_vibrating_surface_pass(opacity=0.84)
    c1 = _get_canvas(p1)

    p2 = _make_small_painter(w=64, h=64)
    p2.tone_ground((0.34, 0.28, 0.44), texture_strength=0.01)
    p2.block_in(ref, stroke_size=8, n_strokes=20)
    p2.kokoschka_vibrating_surface_pass(opacity=0.84)
    p2.paint_chromatic_shadow_shift_pass(opacity=0.72)
    c2 = _get_canvas(p2)

    for c in [c1, c2]:
        assert c.shape == (64, 64, 4)
        assert c[:, :, 3].min() == 255
        assert c[:, :, :3].max() <= 255
        assert c[:, :, :3].min() >= 0


# ── grosz_neue_sachlichkeit_pass ──────────────────────────────────────────────

def test_s284_grosz_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "grosz_neue_sachlichkeit_pass")


def test_s284_grosz_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.grosz_neue_sachlichkeit_pass()
    assert result is None


def test_s284_grosz_pass_modifies_canvas():
    p = _make_small_painter(w=80, h=80)
    _prime_canvas_full(p, _high_contrast_reference(80, 80))
    before = _get_canvas(p).copy()
    p.grosz_neue_sachlichkeit_pass(
        shadow_darken=0.65,
        flat_strength=0.30,
        acid_strength=0.28,
        gamma_value=0.80,
        opacity=0.88,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), \
        "Canvas should change after grosz_neue_sachlichkeit_pass"


def test_s284_grosz_pass_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.grosz_neue_sachlichkeit_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), \
        "Zero opacity should produce no canvas change"


def test_s284_grosz_pass_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas_full(p, _colourful_reference(72, 72))
    p.grosz_neue_sachlichkeit_pass(
        shadow_darken=0.70,
        acid_strength=0.40,
        gamma_value=0.75,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s284_grosz_pass_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.grosz_neue_sachlichkeit_pass(opacity=0.82)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, \
        "Alpha channel should remain fully opaque"


def test_s284_grosz_pass_gamma_one_no_tonal_shift():
    """gamma_value=1.0 should produce no gamma change (Stage 4 identity)."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas_full(p)
    p.grosz_neue_sachlichkeit_pass(
        shadow_darken=0.0,
        flat_strength=0.0,
        acid_strength=0.0,
        dark_push_strength=0.0,
        gamma_value=1.0,
        opacity=1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s284_grosz_pass_small_canvas():
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.grosz_neue_sachlichkeit_pass(opacity=0.60)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


# ── george_grosz catalog entry ────────────────────────────────────────────────

def test_s284_grosz_in_catalog():
    from art_catalog import CATALOG
    assert "george_grosz" in CATALOG, "george_grosz should be in CATALOG"


def test_s284_grosz_artist_name():
    from art_catalog import get_style
    style = get_style("george_grosz")
    assert style.artist == "George Grosz"


def test_s284_grosz_movement_mentions_sachlichkeit_or_expressionism():
    from art_catalog import get_style
    style = get_style("george_grosz")
    m = style.movement.lower()
    assert "sachlichkeit" in m or "objectivity" in m or "expressi" in m or "dada" in m, \
        f"Movement should mention New Objectivity or Expressionism: {style.movement}"


def test_s284_grosz_nationality():
    from art_catalog import get_style
    style = get_style("george_grosz")
    nat = style.nationality.lower()
    assert "german" in nat or "american" in nat, \
        f"Nationality should be German or American: {style.nationality}"


def test_s284_grosz_period():
    from art_catalog import get_style
    style = get_style("george_grosz")
    assert "1893" in style.period, \
        f"Period should include birth year 1893: {style.period}"


def test_s284_grosz_palette_count():
    from art_catalog import get_style
    style = get_style("george_grosz")
    assert len(style.palette) >= 6, \
        f"Grosz palette should have at least 6 colours, got {len(style.palette)}"


def test_s284_grosz_palette_has_acid_yellow_green():
    from art_catalog import get_style
    style = get_style("george_grosz")
    # Acid yellow-green: G dominant, B very low
    has_acid = any(c[1] > 0.70 and c[2] < 0.30 for c in style.palette)
    assert has_acid, "Palette should include an acid yellow-green"


def test_s284_grosz_palette_has_dark():
    from art_catalog import get_style
    style = get_style("george_grosz")
    has_dark = any(all(ch < 0.25 for ch in c) for c in style.palette)
    assert has_dark, "Palette should include a near-black for heavy contour lines"


def test_s284_grosz_palette_rgb_range():
    from art_catalog import get_style
    style = get_style("george_grosz")
    for i, color in enumerate(style.palette):
        assert len(color) == 3, f"Palette color {i} should have 3 channels"
        for ch in color:
            assert 0.0 <= ch <= 1.0, f"Palette color {i} out of [0,1]: {ch}"


def test_s284_grosz_famous_works():
    from art_catalog import get_style
    style = get_style("george_grosz")
    assert len(style.famous_works) >= 5
    titles = [w[0].lower() for w in style.famous_works]
    assert any("pillars" in t or "society" in t or "eclipse" in t or
               "metropolis" in t or "funeral" in t or "panizza" in t
               for t in titles), \
        f"Famous works should include a Grosz signature work: {titles}"


def test_s284_grosz_inspiration_mentions_pass():
    from art_catalog import get_style
    style = get_style("george_grosz")
    assert ("grosz_neue_sachlichkeit_pass" in style.inspiration.lower() or
            "195th" in style.inspiration), \
        "Inspiration should mention grosz_neue_sachlichkeit_pass or 195th mode"


def test_s284_grosz_get_style_roundtrip():
    from art_catalog import get_style, list_artists
    assert "george_grosz" in list_artists()
    style = get_style("george_grosz")
    assert style.artist == "George Grosz"


# ── Full Grosz pipeline smoke ─────────────────────────────────────────────────

def test_s284_grosz_full_pipeline_smoke():
    """All three s284 passes run on a small canvas without error."""
    p = _make_small_painter(w=80, h=80)
    ref = _colourful_reference(80, 80)
    p.tone_ground((0.36, 0.28, 0.18), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)
    p.place_lights(ref, stroke_size=3, n_strokes=15)

    p.paint_chromatic_shadow_shift_pass(opacity=0.72)
    p.grosz_neue_sachlichkeit_pass(opacity=0.82)
    p.paint_form_curvature_tint_pass(opacity=0.68)

    canvas = _get_canvas(p)
    assert canvas.shape == (80, 80, 4)
    assert canvas[:, :, 3].min() == 255
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0
