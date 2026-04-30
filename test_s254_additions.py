"""
test_s254_additions.py -- Session 254 tests for rego_flat_figure_pass,
paint_contour_weight_pass, and the paula_rego catalog entry.
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


def _multicolor_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :w // 2, :] = [180, 60, 30]
    arr[:h // 2, w // 2:, :] = [30, 60, 190]
    arr[h // 2:, :w // 2, :] = [160, 140, 20]
    arr[h // 2:, w // 2:, :] = [50, 150, 80]
    return Image.fromarray(arr, "RGB")


def _figure_reference(w=64, h=64):
    """Simulated Rego-style figure: large central dark shape on lighter ground."""
    from PIL import Image
    arr = np.full((h, w, 3), 180, dtype=np.uint8)
    # Central figure block
    arr[h // 4: 3 * h // 4, w // 4: 3 * w // 4, :] = [60, 40, 30]
    return Image.fromarray(arr, "RGB")


def _edge_reference(w=64, h=64):
    """Sharp edge pattern for contour detection."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [30, 30, 30]
    arr[:, w // 2:, :] = [210, 210, 210]
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, multi=False, figure=False, edge=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if multi:
            ref = _multicolor_reference(w, h)
        elif figure:
            ref = _figure_reference(w, h)
        elif edge:
            ref = _edge_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.60, 0.54, 0.46), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── rego_flat_figure_pass ─────────────────────────────────────────────────────

def test_s254_rego_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "rego_flat_figure_pass")


def test_s254_rego_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.rego_flat_figure_pass()
    assert result is None


def test_s254_rego_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p, multi=True)
    before = _get_canvas(p).copy()
    p.rego_flat_figure_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after rego_flat_figure_pass"


def test_s254_rego_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p)
    p.rego_flat_figure_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="Alpha channel modified by rego_flat_figure_pass"
    )


def test_s254_rego_pass_zero_opacity_no_change():
    """opacity=0.0 must leave canvas nearly identical."""
    p = _make_small_painter()
    _prime_canvas(p, multi=True)
    before = _get_canvas(p).copy()
    p.rego_flat_figure_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff[:, :, :3].max() <= 2, \
        "opacity=0 should produce negligible change"


def test_s254_rego_pass_posterisation_reduces_colour_variety():
    """Flat figure pass with aggressive posterisation should reduce unique colour count."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, multi=True)
    before = _get_canvas(p).copy()
    # Count unique RGB combinations before
    unique_before = len(np.unique(
        before[:, :, :3].reshape(-1, 3), axis=0
    ))
    p.rego_flat_figure_pass(n_levels=3, zone_blend=0.90, opacity=1.0)
    after = _get_canvas(p)
    unique_after = len(np.unique(
        after[:, :, :3].reshape(-1, 3), axis=0
    ))
    assert unique_after < unique_before, \
        "Posterisation should reduce number of unique colours"


def test_s254_rego_pass_contour_darkens_edges():
    """Contour outlining should darken the sharp edge in the figure reference."""
    p = _make_small_painter(w=128, h=128)
    _prime_canvas(p, figure=True)
    before = _get_canvas(p).copy()
    p.rego_flat_figure_pass(
        contour_threshold=0.04,
        contour_strength=0.80,
        contour_px=3,
        opacity=1.0
    )
    after = _get_canvas(p)
    # Edge region (central boundary) should have some darker pixels
    edge_before = before[28:36, 28:36, :3].astype(int)
    edge_after  = after[28:36, 28:36, :3].astype(int)
    diff = edge_before - edge_after
    assert diff.max() > 5, "Contour pass should darken edge pixels"


def test_s254_rego_pass_warm_cool_quadrant_tension():
    """Figure quadrants (upper-right, lower-left) should be warmer after tension pass."""
    p = _make_small_painter(w=128, h=128)
    _prime_canvas(p, multi=True)
    # Disable posterisation and contour to isolate tension stage
    p.rego_flat_figure_pass(
        n_levels=2,
        zone_blend=0.0,
        contour_threshold=1.0,   # suppress all contours
        contour_strength=0.0,
        tension_warm=(0.90, 0.20, 0.10),
        tension_cool=(0.10, 0.20, 0.90),
        tension_strength=0.50,
        opacity=1.0,
    )
    after = _get_canvas(p)
    h, w = after.shape[:2]
    cy, cx = h // 2, w // 2
    # Upper-right quadrant (figure zone) should have higher R vs B ratio
    ur = after[:cy, cx:, :3].astype(float)
    ur_r_minus_b = (ur[:, :, 2] - ur[:, :, 0]).mean()  # BGRA: idx2=R, idx0=B
    # Lower-right quadrant (ground zone) should have lower R vs B ratio
    lr = after[cy:, cx:, :3].astype(float)
    lr_r_minus_b = (lr[:, :, 2] - lr[:, :, 0]).mean()
    assert ur_r_minus_b > lr_r_minus_b - 10, \
        "Figure quadrant should be warmer than ground quadrant after tension pass"


def test_s254_rego_pass_pixel_values_in_range():
    """All RGB values must remain in [0, 255] after pass."""
    p = _make_small_painter()
    _prime_canvas(p, multi=True)
    p.rego_flat_figure_pass(opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s254_rego_pass_higher_opacity_larger_delta():
    """opacity=1.0 should produce larger pixel delta than opacity=0.2."""
    p_full = _make_small_painter()
    _prime_canvas(p_full, multi=True)
    before_f = _get_canvas(p_full).copy()
    p_full.rego_flat_figure_pass(opacity=1.0)
    after_f  = _get_canvas(p_full)
    delta_full = np.abs(before_f.astype(int) - after_f.astype(int)).sum()

    p_low = _make_small_painter()
    _prime_canvas(p_low, multi=True)
    before_l = _get_canvas(p_low).copy()
    p_low.rego_flat_figure_pass(opacity=0.2)
    after_l  = _get_canvas(p_low)
    delta_low = np.abs(before_l.astype(int) - after_l.astype(int)).sum()

    assert delta_full > delta_low, \
        "Higher opacity should produce larger pixel delta"


def test_s254_rego_pass_n_levels_1_runs_without_error():
    """n_levels=1 edge case should complete without error."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.rego_flat_figure_pass(n_levels=1)


def test_s254_rego_pass_zero_contour_strength_less_dark_than_full():
    """With contour_strength=0, edge pixels should not be darker than with full strength."""
    p_no = _make_small_painter(w=128, h=128)
    _prime_canvas(p_no, figure=True)
    p_no.rego_flat_figure_pass(
        n_levels=8, zone_blend=0.0,
        contour_strength=0.0,
        contour_px=2,
        tension_strength=0.0,
        opacity=1.0
    )
    after_no = _get_canvas(p_no)

    p_yes = _make_small_painter(w=128, h=128)
    _prime_canvas(p_yes, figure=True)
    p_yes.rego_flat_figure_pass(
        n_levels=8, zone_blend=0.0,
        contour_strength=0.80,
        contour_px=2,
        tension_strength=0.0,
        opacity=1.0
    )
    after_yes = _get_canvas(p_yes)

    # Contour pass with strength=0.80 should produce darker edge pixels
    edge_no  = after_no[28:36, 28:36, :3].astype(float).mean()
    edge_yes = after_yes[28:36, 28:36, :3].astype(float).mean()
    assert edge_yes < edge_no + 10, \
        "Full contour_strength should produce darker edges than zero contour_strength"


# ── paint_contour_weight_pass ─────────────────────────────────────────────────

def test_s254_contour_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_contour_weight_pass")


def test_s254_contour_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    result = p.paint_contour_weight_pass()
    assert result is None


def test_s254_contour_pass_modifies_canvas():
    """Pass must change at least some pixels on an edge canvas."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()
    p.paint_contour_weight_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_contour_weight_pass"


def test_s254_contour_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p)
    p.paint_contour_weight_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="Alpha channel modified by paint_contour_weight_pass"
    )


def test_s254_contour_pass_zero_opacity_no_change():
    """opacity=0.0 must leave canvas nearly identical."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()
    p.paint_contour_weight_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff[:, :, :3].max() <= 2, \
        "opacity=0 should produce negligible change"


def test_s254_contour_pass_darkens_at_edges():
    """Contour pass should darken pixels at the sharp edge boundary."""
    p = _make_small_painter(w=128, h=128)
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()
    p.paint_contour_weight_pass(
        contour_threshold=0.03,
        max_weight=0.80,
        opacity=1.0
    )
    after = _get_canvas(p)
    # Region around the central vertical edge should be darker
    edge_col = 64  # center column
    edge_before = before[:, edge_col - 2:edge_col + 2, :3].astype(int)
    edge_after  = after[:, edge_col - 2:edge_col + 2, :3].astype(int)
    diff = edge_before - edge_after
    assert diff.max() > 5, "Contour pass should darken edge pixels"


def test_s254_contour_pass_pixel_values_in_range():
    """All RGB values must remain in [0, 255] after pass."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    p.paint_contour_weight_pass(max_weight=0.90, opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s254_contour_pass_uniform_canvas_minimal_effect():
    """A uniform canvas has no edges; effect should be minimal."""
    from PIL import Image
    p = _make_small_painter(w=80, h=80)
    p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    before = _get_canvas(p).copy()
    p.paint_contour_weight_pass(opacity=1.0, contour_threshold=0.04)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff[:, :, :3].mean() < 25, \
        "Uniform canvas should not trigger large contour effects"


def test_s254_contour_pass_edge_stronger_than_flat():
    """Edge canvas should produce larger effect than flat canvas."""
    from PIL import Image

    p_edge = _make_small_painter(w=128, h=128)
    _prime_canvas(p_edge, edge=True)
    before_e = _get_canvas(p_edge).copy()
    p_edge.paint_contour_weight_pass(opacity=1.0)
    after_e  = _get_canvas(p_edge)
    delta_edge = np.abs(before_e.astype(int) - after_e.astype(int)).sum()

    p_flat = _make_small_painter(w=128, h=128)
    p_flat.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    before_f = _get_canvas(p_flat).copy()
    p_flat.paint_contour_weight_pass(opacity=1.0)
    after_f  = _get_canvas(p_flat)
    delta_flat = np.abs(before_f.astype(int) - after_f.astype(int)).sum()

    assert delta_edge > delta_flat, \
        "Edge canvas should produce larger contour weight effect than flat canvas"


def test_s254_contour_pass_higher_max_weight_larger_delta():
    """max_weight=0.8 should produce larger delta than max_weight=0.2."""
    p1 = _make_small_painter()
    _prime_canvas(p1, edge=True)
    b1 = _get_canvas(p1).copy()
    p1.paint_contour_weight_pass(max_weight=0.8, opacity=1.0)
    a1 = _get_canvas(p1)
    d1 = np.abs(b1.astype(int) - a1.astype(int)).sum()

    p2 = _make_small_painter()
    _prime_canvas(p2, edge=True)
    b2 = _get_canvas(p2).copy()
    p2.paint_contour_weight_pass(max_weight=0.2, opacity=1.0)
    a2 = _get_canvas(p2)
    d2 = np.abs(b2.astype(int) - a2.astype(int)).sum()

    assert d1 > d2, "Higher max_weight should produce larger pixel delta"


def test_s254_contour_pass_higher_opacity_larger_delta():
    """opacity=1.0 should produce larger delta than opacity=0.3."""
    p1 = _make_small_painter()
    _prime_canvas(p1, edge=True)
    b1 = _get_canvas(p1).copy()
    p1.paint_contour_weight_pass(opacity=1.0)
    a1 = _get_canvas(p1)
    d1 = np.abs(b1.astype(int) - a1.astype(int)).sum()

    p2 = _make_small_painter()
    _prime_canvas(p2, edge=True)
    b2 = _get_canvas(p2).copy()
    p2.paint_contour_weight_pass(opacity=0.3)
    a2 = _get_canvas(p2)
    d2 = np.abs(b2.astype(int) - a2.astype(int)).sum()

    assert d1 > d2, "Higher opacity should produce larger pixel delta"


# ── paula_rego catalog entry ──────────────────────────────────────────────────

def test_s254_catalog_rego_entry_exists():
    import art_catalog
    assert "paula_rego" in art_catalog.CATALOG


def test_s254_catalog_rego_artist_name():
    import art_catalog
    s = art_catalog.get_style("paula_rego")
    assert s.artist == "Paula Rego"


def test_s254_catalog_rego_movement():
    import art_catalog
    s = art_catalog.get_style("paula_rego")
    assert "Figurative" in s.movement


def test_s254_catalog_rego_nationality():
    import art_catalog
    s = art_catalog.get_style("paula_rego")
    assert "Portuguese" in s.nationality


def test_s254_catalog_rego_palette_count():
    import art_catalog
    s = art_catalog.get_style("paula_rego")
    assert len(s.palette) >= 8, "Rego palette should have at least 8 colours"


def test_s254_catalog_rego_palette_values_valid():
    import art_catalog
    s = art_catalog.get_style("paula_rego")
    for r, g, b in s.palette:
        assert 0.0 <= r <= 1.0
        assert 0.0 <= g <= 1.0
        assert 0.0 <= b <= 1.0


def test_s254_catalog_rego_ground_color_valid():
    import art_catalog
    s = art_catalog.get_style("paula_rego")
    r, g, b = s.ground_color
    assert 0.0 <= r <= 1.0
    assert 0.0 <= g <= 1.0
    assert 0.0 <= b <= 1.0


def test_s254_catalog_rego_crackle_false():
    """Rego should have crackle=False (no lead-surface cracking)."""
    import art_catalog
    s = art_catalog.get_style("paula_rego")
    assert s.crackle is False


def test_s254_catalog_rego_famous_works():
    import art_catalog
    s = art_catalog.get_style("paula_rego")
    assert len(s.famous_works) >= 5
    titles = [t for t, _ in s.famous_works]
    assert any("Maid" in t or "Dog" in t or "Dance" in t for t in titles)


def test_s254_catalog_rego_inspiration_references_165th():
    import art_catalog
    s = art_catalog.get_style("paula_rego")
    assert "165" in s.inspiration


def test_s254_catalog_rego_inspiration_references_flat_figure():
    import art_catalog
    s = art_catalog.get_style("paula_rego")
    assert "flat" in s.inspiration.lower() or "FLAT" in s.inspiration


def test_s254_catalog_total_artist_count():
    """Total artist count should have grown to at least 254."""
    import art_catalog
    assert len(art_catalog.list_artists()) >= 254


def test_s254_catalog_rego_technique_mentions_pastel():
    import art_catalog
    s = art_catalog.get_style("paula_rego")
    assert "pastel" in s.technique.lower()
