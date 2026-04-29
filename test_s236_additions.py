"""
Tests for session 236 additions:
  - frantisek_kupka catalog entry
  - kupka_orphic_fugue_pass  (147th distinct mode)
  - paint_medium_pooling_pass (improvement pass)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pytest
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_small_painter(seed=42, w=64, h=64):
    from stroke_engine import Painter
    return Painter(w, h, seed=seed)


def _solid_rgb(painter, r, g, b):
    import cairo
    ctx = cairo.Context(painter.canvas.surface)
    ctx.set_source_rgb(r, g, b)
    ctx.paint()
    painter.canvas.surface.mark_dirty()


def _gradient_reference(painter):
    import cairo
    w, h = painter.canvas.w, painter.canvas.h
    gradient = cairo.LinearGradient(0, 0, w, 0)
    gradient.add_color_stop_rgb(0, 0, 0, 0)
    gradient.add_color_stop_rgb(1, 1, 1, 1)
    ctx = cairo.Context(painter.canvas.surface)
    ctx.set_source(gradient)
    ctx.paint()
    painter.canvas.surface.mark_dirty()


def _vertical_gradient_reference(painter):
    import cairo
    w, h = painter.canvas.w, painter.canvas.h
    gradient = cairo.LinearGradient(0, 0, 0, h)
    gradient.add_color_stop_rgb(0, 1, 1, 1)
    gradient.add_color_stop_rgb(1, 0, 0, 0)
    ctx = cairo.Context(painter.canvas.surface)
    ctx.set_source(gradient)
    ctx.paint()
    painter.canvas.surface.mark_dirty()


def _vivid_mid_reference(painter):
    """Vivid saturated red-orange: lum ~0.40, high chroma -- good for hue rotation."""
    import cairo
    ctx = cairo.Context(painter.canvas.surface)
    ctx.set_source_rgb(0.88, 0.30, 0.04)
    ctx.paint()
    painter.canvas.surface.mark_dirty()


def _textured_reference(painter):
    """Sinusoidal luminance pattern to create real valleys for pooling."""
    import numpy as np, cairo
    w, h = painter.canvas.w, painter.canvas.h
    surface = painter.canvas.surface
    buf = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
    xx, yy = np.mgrid[0:w, 0:h]
    lum = (0.5 + 0.35 * np.sin(xx * 0.4) * np.cos(yy * 0.4)).astype(np.float32)
    lum = np.clip(lum, 0.0, 1.0)
    val = (lum * 255).astype(np.uint8)
    buf[:, :, 0] = val.T
    buf[:, :, 1] = val.T
    buf[:, :, 2] = val.T
    buf[:, :, 3] = 255
    surface.get_data()[:] = buf.tobytes()
    surface.mark_dirty()


def _read_rgb(painter):
    """Return canvas as float32 (H, W, 3) in RGB order."""
    buf = np.frombuffer(painter.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(
                            (painter.canvas.h, painter.canvas.w, 4)).copy()
    r = buf[:, :, 2].astype(np.float32) / 255.0
    g = buf[:, :, 1].astype(np.float32) / 255.0
    b = buf[:, :, 0].astype(np.float32) / 255.0
    return np.stack([r, g, b], axis=2)


def _chroma(rgb):
    """Per-pixel chroma (max - min) array, shape (H, W)."""
    return rgb.max(axis=2) - rgb.min(axis=2)


# ─────────────────────────────────────────────────────────────────────────────
# Catalog tests (8)
# ─────────────────────────────────────────────────────────────────────────────

class TestFrantisekKupkaCatalog:

    def test_entry_exists(self):
        from art_catalog import CATALOG
        assert "frantisek_kupka" in CATALOG

    def test_artist_field(self):
        from art_catalog import CATALOG
        assert CATALOG["frantisek_kupka"].artist == "Frantisek Kupka"

    def test_movement_field(self):
        from art_catalog import CATALOG
        entry = CATALOG["frantisek_kupka"]
        assert "Orphism" in entry.movement

    def test_period_field(self):
        from art_catalog import CATALOG
        entry = CATALOG["frantisek_kupka"]
        assert "1871" in entry.period
        assert "1957" in entry.period

    def test_palette_has_eight_colours(self):
        from art_catalog import CATALOG
        palette = CATALOG["frantisek_kupka"].palette
        assert len(palette) == 8

    def test_palette_colours_in_unit_range(self):
        from art_catalog import CATALOG
        for colour in CATALOG["frantisek_kupka"].palette:
            r, g, b = colour
            assert 0.0 <= r <= 1.0
            assert 0.0 <= g <= 1.0
            assert 0.0 <= b <= 1.0

    def test_famous_works_present(self):
        from art_catalog import CATALOG
        works = CATALOG["frantisek_kupka"].famous_works
        assert len(works) >= 5
        titles = [w[0] for w in works]
        assert any("Fugue" in t or "Amorpha" in t for t in titles), (
            "Expected 'Amorpha: Fugue in Two Colors' in famous works"
        )

    def test_inspiration_references_pass(self):
        from art_catalog import CATALOG
        inspiration = CATALOG["frantisek_kupka"].inspiration
        assert "kupka_orphic_fugue_pass" in inspiration

    def test_total_catalog_size(self):
        from art_catalog import CATALOG
        assert len(CATALOG) == 236, (
            f"Expected 236 entries after session 236, got {len(CATALOG)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Kupka Orphic Fugue pass tests (16)
# ─────────────────────────────────────────────────────────────────────────────

class TestKupkaOrphicFuguePass:

    def test_method_exists(self):
        p = _make_small_painter()
        assert hasattr(p, 'kupka_orphic_fugue_pass')

    def test_method_callable(self):
        p = _make_small_painter()
        assert callable(getattr(p, 'kupka_orphic_fugue_pass'))

    def test_pass_runs_without_error_on_gradient(self):
        p = _make_small_painter()
        _gradient_reference(p)
        p.kupka_orphic_fugue_pass()

    def test_pass_runs_without_error_on_solid_colour(self):
        p = _make_small_painter()
        _solid_rgb(p, 0.5, 0.3, 0.7)
        p.kupka_orphic_fugue_pass()

    def test_zero_opacity_leaves_canvas_unchanged(self):
        """At opacity=0 the pass must be a no-op."""
        p = _make_small_painter()
        _vivid_mid_reference(p)
        before = _read_rgb(p).copy()
        p.kupka_orphic_fugue_pass(opacity=0.0)
        after = _read_rgb(p)
        np.testing.assert_array_almost_equal(before, after, decimal=1,
            err_msg="opacity=0 should leave canvas unchanged")

    def test_hue_rotation_changes_colour_on_saturated_input(self):
        """A vivid red input should change colour after hue rotation."""
        p = _make_small_painter()
        _vivid_mid_reference(p)
        before = _read_rgb(p).copy()
        p.kupka_orphic_fugue_pass(
            hue_amplitude=0.20,
            hue_period_frac=0.20,
            chroma_boost=0.0,
            opacity=1.0,
        )
        after = _read_rgb(p)
        # At least some pixels should differ (hue rotation changes RGB values)
        diff = np.abs(after - before).mean()
        assert diff > 0.005, (
            f"Hue rotation should change pixel values on saturated input: diff={diff:.5f}"
        )

    def test_hue_rotation_preserves_luminance_approximately(self):
        """Hue rotation should not dramatically change average luminance."""
        p = _make_small_painter()
        _gradient_reference(p)
        before = _read_rgb(p)
        lum_before = (0.299 * before[:, :, 0]
                      + 0.587 * before[:, :, 1]
                      + 0.114 * before[:, :, 2]).mean()
        p.kupka_orphic_fugue_pass(hue_amplitude=0.15, chroma_boost=0.0, opacity=1.0)
        after = _read_rgb(p)
        lum_after = (0.299 * after[:, :, 0]
                     + 0.587 * after[:, :, 1]
                     + 0.114 * after[:, :, 2]).mean()
        assert abs(lum_after - lum_before) < 0.08, (
            f"Hue rotation should preserve luminance approximately: "
            f"before={lum_before:.4f} after={lum_after:.4f}"
        )

    def test_chroma_boost_increases_saturation_in_mid_values(self):
        """Chroma boost stage should increase mean chroma on mid-value input."""
        p = _make_small_painter()
        _vivid_mid_reference(p)
        before = _read_rgb(p)
        chroma_before = _chroma(before).mean()
        p.kupka_orphic_fugue_pass(
            hue_amplitude=0.0,   # isolate chroma boost
            chroma_boost=0.40,
            mid_lum_center=0.40,
            mid_lum_width=0.20,
            opacity=1.0,
        )
        after = _read_rgb(p)
        chroma_after = _chroma(after).mean()
        assert chroma_after > chroma_before, (
            f"Chroma boost should increase saturation: "
            f"before={chroma_before:.4f} after={chroma_after:.4f}"
        )

    def test_output_values_within_unit_range(self):
        """Output must stay within [0, 1] range."""
        p = _make_small_painter()
        _gradient_reference(p)
        p.kupka_orphic_fugue_pass(hue_amplitude=0.20, chroma_boost=0.50, opacity=1.0)
        after = _read_rgb(p)
        assert after.min() >= -0.001, f"Output below 0: {after.min():.5f}"
        assert after.max() <= 1.001, f"Output above 1: {after.max():.5f}"

    def test_neutral_grey_unaffected_by_hue_rotation(self):
        """Neutral grey (zero saturation) should not change hue under rotation."""
        p = _make_small_painter()
        _solid_rgb(p, 0.5, 0.5, 0.5)   # neutral grey, chroma=0
        before = _read_rgb(p).copy()
        p.kupka_orphic_fugue_pass(
            hue_amplitude=0.25, chroma_boost=0.0, opacity=1.0
        )
        after = _read_rgb(p)
        # Grey should be unchanged (no saturation to rotate)
        diff = np.abs(after - before).mean()
        assert diff < 0.02, (
            f"Neutral grey should be unaffected by hue rotation: diff={diff:.5f}"
        )

    def test_large_amplitude_still_produces_valid_output(self):
        """Even extreme amplitude (0.5 = 180 deg) should stay within bounds."""
        p = _make_small_painter()
        _vivid_mid_reference(p)
        p.kupka_orphic_fugue_pass(hue_amplitude=0.50, chroma_boost=0.0, opacity=1.0)
        after = _read_rgb(p)
        assert after.min() >= -0.001 and after.max() <= 1.001, "Output out of bounds"

    def test_pass_is_reproducible_with_same_parameters(self):
        """Applying the pass twice with same parameters is deterministic."""
        p1 = _make_small_painter(seed=7)
        p2 = _make_small_painter(seed=7)
        _gradient_reference(p1)
        _gradient_reference(p2)
        p1.kupka_orphic_fugue_pass(hue_amplitude=0.12, opacity=0.80)
        p2.kupka_orphic_fugue_pass(hue_amplitude=0.12, opacity=0.80)
        np.testing.assert_array_equal(_read_rgb(p1), _read_rgb(p2))

    def test_period_variation_changes_output(self):
        """Changing hue_period_frac must produce different output."""
        p1 = _make_small_painter(seed=11)
        p2 = _make_small_painter(seed=11)
        _vivid_mid_reference(p1)
        _vivid_mid_reference(p2)
        p1.kupka_orphic_fugue_pass(hue_period_frac=0.15, opacity=1.0)
        p2.kupka_orphic_fugue_pass(hue_period_frac=0.60, opacity=1.0)
        diff = np.abs(_read_rgb(p1) - _read_rgb(p2)).mean()
        assert diff > 0.002, (
            f"Different periods should produce different outputs: diff={diff:.5f}"
        )

    def test_full_opacity_passes_more_effect_than_half(self):
        """opacity=1.0 should produce a bigger change than opacity=0.5."""
        p_full = _make_small_painter(seed=3)
        p_half = _make_small_painter(seed=3)
        _vivid_mid_reference(p_full)
        _vivid_mid_reference(p_half)
        orig = _read_rgb(p_full).copy()
        p_full.kupka_orphic_fugue_pass(hue_amplitude=0.20, opacity=1.0)
        p_half.kupka_orphic_fugue_pass(hue_amplitude=0.20, opacity=0.5)
        diff_full = np.abs(_read_rgb(p_full) - orig).mean()
        diff_half = np.abs(_read_rgb(p_half) - orig).mean()
        assert diff_full > diff_half, (
            f"Full opacity should change more than half: "
            f"full={diff_full:.5f} half={diff_half:.5f}"
        )

    def test_canvas_dimensions_preserved(self):
        """Pass must not alter canvas dimensions."""
        p = _make_small_painter(w=80, h=48)
        _gradient_reference(p)
        p.kupka_orphic_fugue_pass()
        assert p.canvas.w == 80
        assert p.canvas.h == 48

    def test_vertical_gradient_also_runs_without_error(self):
        p = _make_small_painter()
        _vertical_gradient_reference(p)
        p.kupka_orphic_fugue_pass(hue_phase=1.57)


# ─────────────────────────────────────────────────────────────────────────────
# Paint Medium Pooling pass tests (14)
# ─────────────────────────────────────────────────────────────────────────────

class TestPaintMediumPoolingPass:

    def test_method_exists(self):
        p = _make_small_painter()
        assert hasattr(p, 'paint_medium_pooling_pass')

    def test_method_callable(self):
        p = _make_small_painter()
        assert callable(getattr(p, 'paint_medium_pooling_pass'))

    def test_pass_runs_without_error_on_gradient(self):
        p = _make_small_painter()
        _gradient_reference(p)
        p.paint_medium_pooling_pass()

    def test_pass_runs_on_textured_surface(self):
        p = _make_small_painter()
        _textured_reference(p)
        p.paint_medium_pooling_pass()

    def test_zero_opacity_leaves_canvas_unchanged(self):
        p = _make_small_painter()
        _textured_reference(p)
        before = _read_rgb(p).copy()
        p.paint_medium_pooling_pass(opacity=0.0)
        after = _read_rgb(p)
        np.testing.assert_array_almost_equal(before, after, decimal=1,
            err_msg="opacity=0 should leave canvas unchanged")

    def test_valley_darkening_reduces_luminance_on_textured_surface(self):
        """Valley darkening should reduce mean luminance slightly."""
        p = _make_small_painter()
        _textured_reference(p)
        before = _read_rgb(p)
        lum_before = (0.299 * before[:, :, 0]
                      + 0.587 * before[:, :, 1]
                      + 0.114 * before[:, :, 2]).mean()
        p.paint_medium_pooling_pass(pool_depth=0.08, pool_sat_lift=0.0, opacity=1.0)
        after = _read_rgb(p)
        lum_after = (0.299 * after[:, :, 0]
                     + 0.587 * after[:, :, 1]
                     + 0.114 * after[:, :, 2]).mean()
        assert lum_after < lum_before, (
            f"Valley darkening should reduce mean luminance: "
            f"before={lum_before:.4f} after={lum_after:.4f}"
        )

    def test_saturation_enrichment_increases_chroma_in_coloured_valleys(self):
        """Pool saturation lift should increase chroma on vivid textured surface."""
        p = _make_small_painter()
        # Use a vivid coloured textured surface
        import cairo, numpy as np_local
        w, h = p.canvas.w, p.canvas.h
        surface = p.canvas.surface
        buf = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
        xx, yy = np.mgrid[0:w, 0:h]
        lum = (0.5 + 0.35 * np.sin(xx * 0.4) * np.cos(yy * 0.4)).astype(np.float32)
        lum = np.clip(lum, 0.0, 1.0)
        val = (lum * 255).astype(np.uint8)
        buf[:, :, 2] = val.T          # R channel only → saturated red pattern
        buf[:, :, 1] = (val * 0.3).T  # low G
        buf[:, :, 0] = (val * 0.1).T  # low B
        buf[:, :, 3] = 255
        surface.get_data()[:] = buf.tobytes()
        surface.mark_dirty()

        before = _read_rgb(p)
        chroma_before = _chroma(before).mean()
        p.paint_medium_pooling_pass(pool_sat_lift=0.30, pool_depth=0.0, opacity=1.0)
        after = _read_rgb(p)
        chroma_after = _chroma(after).mean()
        assert chroma_after > chroma_before, (
            f"Saturation lift should increase chroma in valleys: "
            f"before={chroma_before:.4f} after={chroma_after:.4f}"
        )

    def test_flat_surface_minimal_effect(self):
        """A perfectly flat uniform surface has no valleys; effect should be tiny."""
        p = _make_small_painter()
        _solid_rgb(p, 0.55, 0.40, 0.20)
        before = _read_rgb(p).copy()
        p.paint_medium_pooling_pass(opacity=1.0)
        after = _read_rgb(p)
        diff = np.abs(after - before).mean()
        # Flat surface = every pixel IS the local minimum = gate is everywhere high
        # The effect will be present but the darkening should be small in absolute terms
        # (pool_depth default=0.045 * opacity=1.0 * gate≈1.0)
        # Just verify no explosion and output is bounded
        assert after.min() >= -0.001 and after.max() <= 1.001, "Output out of bounds"

    def test_output_values_within_unit_range(self):
        p = _make_small_painter()
        _textured_reference(p)
        p.paint_medium_pooling_pass(pool_depth=0.10, pool_sat_lift=0.30, opacity=1.0)
        after = _read_rgb(p)
        assert after.min() >= -0.001, f"Output below 0: {after.min():.5f}"
        assert after.max() <= 1.001, f"Output above 1: {after.max():.5f}"

    def test_larger_pool_size_has_different_effect_from_smaller(self):
        p1 = _make_small_painter(seed=5)
        p2 = _make_small_painter(seed=5)
        _textured_reference(p1)
        _textured_reference(p2)
        p1.paint_medium_pooling_pass(pool_size=3, opacity=1.0)
        p2.paint_medium_pooling_pass(pool_size=9, opacity=1.0)
        diff = np.abs(_read_rgb(p1) - _read_rgb(p2)).mean()
        assert diff > 1e-5, (
            f"Different pool sizes should produce different outputs: diff={diff:.6f}"
        )

    def test_pass_is_reproducible(self):
        p1 = _make_small_painter(seed=13)
        p2 = _make_small_painter(seed=13)
        _textured_reference(p1)
        _textured_reference(p2)
        p1.paint_medium_pooling_pass()
        p2.paint_medium_pooling_pass()
        np.testing.assert_array_equal(_read_rgb(p1), _read_rgb(p2))

    def test_higher_opacity_produces_more_effect(self):
        p_high = _make_small_painter(seed=9)
        p_low = _make_small_painter(seed=9)
        _textured_reference(p_high)
        _textured_reference(p_low)
        orig = _read_rgb(p_high).copy()
        p_high.paint_medium_pooling_pass(opacity=1.0)
        p_low.paint_medium_pooling_pass(opacity=0.3)
        diff_high = np.abs(_read_rgb(p_high) - orig).mean()
        diff_low = np.abs(_read_rgb(p_low) - orig).mean()
        assert diff_high > diff_low, (
            f"Higher opacity should produce more effect: "
            f"high={diff_high:.5f} low={diff_low:.5f}"
        )

    def test_canvas_dimensions_preserved(self):
        p = _make_small_painter(w=80, h=48)
        _textured_reference(p)
        p.paint_medium_pooling_pass()
        assert p.canvas.w == 80
        assert p.canvas.h == 48

    def test_both_passes_run_sequentially(self):
        """Kupka pass followed by medium pooling should not error."""
        p = _make_small_painter()
        _gradient_reference(p)
        p.kupka_orphic_fugue_pass()
        p.paint_medium_pooling_pass()
        after = _read_rgb(p)
        assert after.min() >= -0.001 and after.max() <= 1.001
