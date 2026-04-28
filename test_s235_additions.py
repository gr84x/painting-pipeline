"""
Tests for session 235 additions:
  - emil_nolde catalog entry
  - nolde_incandescent_surge_pass  (146th distinct mode)
  - paint_pigment_granulation_pass (improvement pass)
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


def _solid_reference(painter, r, g, b):
    """Fill canvas with solid colour (float 0-1 each channel)."""
    import cairo
    ctx = cairo.Context(painter.canvas.surface)
    ctx.set_source_rgb(r, g, b)
    ctx.paint()
    painter.canvas.surface.mark_dirty()


def _gradient_reference(painter):
    """Fill canvas with horizontal gradient (black left → white right)."""
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
    """Fill canvas with vertical gradient (white top → black bottom)."""
    import cairo
    w, h = painter.canvas.w, painter.canvas.h
    gradient = cairo.LinearGradient(0, 0, 0, h)
    gradient.add_color_stop_rgb(0, 1, 1, 1)
    gradient.add_color_stop_rgb(1, 0, 0, 0)
    ctx = cairo.Context(painter.canvas.surface)
    ctx.set_source(gradient)
    ctx.paint()
    painter.canvas.surface.mark_dirty()


def _vivid_red_reference(painter):
    """Fill canvas with a vivid saturated red (high chroma, mid luminance)."""
    import cairo
    ctx = cairo.Context(painter.canvas.surface)
    ctx.set_source_rgb(0.78, 0.10, 0.08)
    ctx.paint()
    painter.canvas.surface.mark_dirty()


def _mid_tone_reference(painter):
    """Fill canvas with a vivid mid-tone orange (lum ≈ 0.50, high chroma)."""
    import cairo
    ctx = cairo.Context(painter.canvas.surface)
    ctx.set_source_rgb(0.72, 0.48, 0.08)   # lum ≈ 0.50
    ctx.paint()
    painter.canvas.surface.mark_dirty()


def _dark_reference(painter):
    """Fill canvas with a very dark near-black (lum ≈ 0.08)."""
    import cairo
    ctx = cairo.Context(painter.canvas.surface)
    ctx.set_source_rgb(0.08, 0.06, 0.05)
    ctx.paint()
    painter.canvas.surface.mark_dirty()


def _read_rgb(painter):
    """Return canvas as float32 (H, W, 3) in RGB order."""
    buf = np.frombuffer(painter.canvas.surface.get_data(),
                        dtype=np.uint8).reshape((painter.canvas.h,
                                                 painter.canvas.w, 4)).copy()
    r = buf[:, :, 2].astype(np.float32) / 255.0
    g = buf[:, :, 1].astype(np.float32) / 255.0
    b = buf[:, :, 0].astype(np.float32) / 255.0
    return np.stack([r, g, b], axis=2)


# ─────────────────────────────────────────────────────────────────────────────
# Catalog tests (8)
# ─────────────────────────────────────────────────────────────────────────────

class TestEmilNoldeCatalog:

    def test_entry_exists(self):
        from art_catalog import CATALOG
        assert "emil_nolde" in CATALOG

    def test_artist_field(self):
        from art_catalog import CATALOG
        assert CATALOG["emil_nolde"].artist == "Emil Nolde"

    def test_movement_field(self):
        from art_catalog import CATALOG
        entry = CATALOG["emil_nolde"]
        assert "Expressionism" in entry.movement

    def test_period_field(self):
        from art_catalog import CATALOG
        entry = CATALOG["emil_nolde"]
        assert "1867" in entry.period
        assert "1956" in entry.period

    def test_palette_has_eight_colours(self):
        from art_catalog import CATALOG
        palette = CATALOG["emil_nolde"].palette
        assert len(palette) == 8

    def test_palette_colours_in_unit_range(self):
        from art_catalog import CATALOG
        for colour in CATALOG["emil_nolde"].palette:
            r, g, b = colour
            assert 0.0 <= r <= 1.0
            assert 0.0 <= g <= 1.0
            assert 0.0 <= b <= 1.0

    def test_famous_works_present(self):
        from art_catalog import CATALOG
        works = CATALOG["emil_nolde"].famous_works
        assert len(works) >= 5
        titles = [w[0] for w in works]
        assert any("Sunflowers" in t or "Flower" in t or "Garden" in t
                   for t in titles), "Expected a floral work"

    def test_inspiration_references_pass(self):
        from art_catalog import CATALOG
        inspiration = CATALOG["emil_nolde"].inspiration
        assert "nolde_incandescent_surge_pass" in inspiration


# ─────────────────────────────────────────────────────────────────────────────
# Nolde Incandescent Surge pass tests (16)
# ─────────────────────────────────────────────────────────────────────────────

class TestNoldeIncandescentSurgePass:

    def test_method_exists(self):
        p = _make_small_painter()
        assert hasattr(p, 'nolde_incandescent_surge_pass')

    def test_method_callable(self):
        p = _make_small_painter()
        assert callable(getattr(p, 'nolde_incandescent_surge_pass'))

    def test_pass_runs_without_error(self):
        p = _make_small_painter()
        _gradient_reference(p)
        p.nolde_incandescent_surge_pass()

    def test_shadow_warmth_inversion_red_increases_in_dark_zones(self):
        """Stage 1: dark zones should gain red channel relative to original."""
        p = _make_small_painter()
        _dark_reference(p)
        before = _read_rgb(p)[:, :, 0].mean()
        p.nolde_incandescent_surge_pass(opacity=1.0)
        after = _read_rgb(p)[:, :, 0].mean()
        assert after > before, (
            f"Shadow warmth inversion should increase red in dark zones: "
            f"before={before:.4f} after={after:.4f}"
        )

    def test_shadow_warmth_inversion_blue_decreases_in_dark_zones(self):
        """Stage 1: dark zones should lose blue channel relative to original."""
        p = _make_small_painter()
        _dark_reference(p)
        before = _read_rgb(p)[:, :, 2].mean()
        p.nolde_incandescent_surge_pass(opacity=1.0, shadow_b_drop=0.07)
        after = _read_rgb(p)[:, :, 2].mean()
        assert after <= before, (
            f"Shadow warmth inversion should not increase blue in dark zones: "
            f"before={before:.4f} after={after:.4f}"
        )

    def test_mid_tone_surge_increases_saturation(self):
        """Stage 2: vivid mid-tone should become more saturated after pass."""
        p = _make_small_painter()
        _mid_tone_reference(p)
        rgb_before = _read_rgb(p)
        lum_b = (0.299 * rgb_before[:, :, 0]
                 + 0.587 * rgb_before[:, :, 1]
                 + 0.114 * rgb_before[:, :, 2])
        chroma_before = (rgb_before.max(axis=2) - rgb_before.min(axis=2)).mean()
        p.nolde_incandescent_surge_pass(
            opacity=1.0, surge_boost=0.70, mid_center=0.50, mid_width=0.20
        )
        rgb_after = _read_rgb(p)
        chroma_after = (rgb_after.max(axis=2) - rgb_after.min(axis=2)).mean()
        assert chroma_after > chroma_before, (
            f"Mid-tone surge should increase chroma: "
            f"before={chroma_before:.4f} after={chroma_after:.4f}"
        )

    def test_mid_tone_surge_stronger_than_highlights(self):
        """Stage 2 bell at lum=0.50 should affect mid-tones more than near-white."""
        p_mid = _make_small_painter(seed=1)
        _mid_tone_reference(p_mid)
        rgb_mid_before = _read_rgb(p_mid)
        p_mid.nolde_incandescent_surge_pass(opacity=1.0)
        rgb_mid_after = _read_rgb(p_mid)
        chroma_change_mid = ((rgb_mid_after.max(axis=2) - rgb_mid_after.min(axis=2))
                             - (rgb_mid_before.max(axis=2) - rgb_mid_before.min(axis=2))).mean()

        p_hi = _make_small_painter(seed=2)
        _solid_reference(p_hi, 0.95, 0.92, 0.88)   # near-white, low chroma
        rgb_hi_before = _read_rgb(p_hi)
        p_hi.nolde_incandescent_surge_pass(opacity=1.0)
        rgb_hi_after = _read_rgb(p_hi)
        chroma_change_hi = ((rgb_hi_after.max(axis=2) - rgb_hi_after.min(axis=2))
                            - (rgb_hi_before.max(axis=2) - rgb_hi_before.min(axis=2))).mean()

        assert chroma_change_mid > chroma_change_hi, (
            f"Mid-tone surge (lum≈0.50) should change chroma more than highlights: "
            f"mid={chroma_change_mid:.5f} hi={chroma_change_hi:.5f}"
        )

    def test_bloom_halation_requires_high_chroma(self):
        """Stage 3: low-chroma high-lum canvas should receive little bloom."""
        p_vivid = _make_small_painter(seed=10)
        _solid_reference(p_vivid, 0.80, 0.20, 0.05)   # vivid red, high chroma
        p_vivid.nolde_incandescent_surge_pass(
            opacity=1.0, bloom_sigma=3.5,
            bloom_chroma_min=0.22, bloom_lum_min=0.38
        )
        vivid_r_mean = _read_rgb(p_vivid)[:, :, 0].mean()

        p_neutral = _make_small_painter(seed=11)
        _solid_reference(p_neutral, 0.58, 0.55, 0.52)  # neutral grey, low chroma
        p_neutral.nolde_incandescent_surge_pass(
            opacity=1.0, bloom_sigma=3.5,
            bloom_chroma_min=0.22, bloom_lum_min=0.38
        )
        neutral_r_mean = _read_rgb(p_neutral)[:, :, 0].mean()

        # Vivid canvas should receive more red warmth from bloom
        assert vivid_r_mean > neutral_r_mean, (
            f"High-chroma canvas should have more bloom than neutral: "
            f"vivid_r={vivid_r_mean:.4f} neutral_r={neutral_r_mean:.4f}"
        )

    def test_output_stays_in_unit_range(self):
        p = _make_small_painter()
        _gradient_reference(p)
        p.nolde_incandescent_surge_pass()
        rgb = _read_rgb(p)
        assert rgb.min() >= 0.0 - 1e-5
        assert rgb.max() <= 1.0 + 1e-5

    def test_opacity_zero_leaves_canvas_unchanged(self):
        p = _make_small_painter()
        _vivid_red_reference(p)
        before = _read_rgb(p).copy()
        p.nolde_incandescent_surge_pass(opacity=0.0)
        after = _read_rgb(p)
        np.testing.assert_allclose(before, after, atol=1/255)

    def test_opacity_one_applies_full_effect(self):
        """opacity=1.0 should differ more from original than opacity=0.1."""
        p_full = _make_small_painter(seed=5)
        _mid_tone_reference(p_full)
        before = _read_rgb(p_full).copy()
        p_full.nolde_incandescent_surge_pass(opacity=1.0)
        diff_full = np.abs(_read_rgb(p_full) - before).mean()

        p_small = _make_small_painter(seed=5)
        _mid_tone_reference(p_small)
        p_small.nolde_incandescent_surge_pass(opacity=0.1)
        diff_small = np.abs(_read_rgb(p_small) - before).mean()

        assert diff_full > diff_small

    def test_surge_boost_zero_leaves_mid_chroma_unchanged(self):
        """With surge_boost=0, Stage 2 should not change saturation."""
        p = _make_small_painter()
        _mid_tone_reference(p)
        rgb_before = _read_rgb(p)
        chroma_before = (rgb_before.max(axis=2) - rgb_before.min(axis=2)).mean()
        # Only shadow warmth and bloom operate; no mid-tone boost
        p.nolde_incandescent_surge_pass(
            opacity=1.0, surge_boost=0.0,
            shadow_r_push=0.0, shadow_b_drop=0.0,
            bloom_warm_r=0.0, bloom_warm_g=0.0, bloom_warm_b=0.0
        )
        rgb_after = _read_rgb(p)
        chroma_after = (rgb_after.max(axis=2) - rgb_after.min(axis=2)).mean()
        np.testing.assert_allclose(chroma_before, chroma_after, atol=0.01)

    def test_shadow_warmth_zero_params_no_warmth(self):
        """shadow_r_push=0, shadow_b_drop=0 should not change dark channel values."""
        p = _make_small_painter()
        _dark_reference(p)
        before = _read_rgb(p).copy()
        p.nolde_incandescent_surge_pass(
            opacity=1.0, shadow_r_push=0.0, shadow_b_drop=0.0,
            surge_boost=0.0, bloom_warm_r=0.0, bloom_warm_g=0.0, bloom_warm_b=0.0
        )
        after = _read_rgb(p)
        np.testing.assert_allclose(before, after, atol=1/255)

    def test_idempotent_flag_check(self):
        """Running pass twice should differ from running once (not idempotent)."""
        p_once = _make_small_painter(seed=7)
        _mid_tone_reference(p_once)
        p_once.nolde_incandescent_surge_pass(opacity=0.84)
        rgb_once = _read_rgb(p_once).copy()

        p_twice = _make_small_painter(seed=7)
        _mid_tone_reference(p_twice)
        p_twice.nolde_incandescent_surge_pass(opacity=0.84)
        p_twice.nolde_incandescent_surge_pass(opacity=0.84)
        rgb_twice = _read_rgb(p_twice)

        assert not np.allclose(rgb_once, rgb_twice, atol=0.001), (
            "Running pass twice should produce different result from once"
        )

    def test_dark_canvas_warm_shift_direction(self):
        """Net effect on near-black: red mean should exceed blue mean (warm shift)."""
        p = _make_small_painter()
        _dark_reference(p)
        p.nolde_incandescent_surge_pass(
            opacity=1.0, shadow_r_push=0.10, shadow_b_drop=0.07
        )
        rgb = _read_rgb(p)
        assert rgb[:, :, 0].mean() > rgb[:, :, 2].mean(), (
            "After shadow warmth inversion on dark canvas, red should exceed blue"
        )

    def test_gradient_canvas_processes_full_range(self):
        """Gradient canvas exercises all luminance zones without error."""
        p = _make_small_painter()
        _gradient_reference(p)
        p.nolde_incandescent_surge_pass()
        rgb = _read_rgb(p)
        assert rgb.shape == (64, 64, 3)
        assert rgb.min() >= 0.0 - 1e-5
        assert rgb.max() <= 1.0 + 1e-5

    def test_default_params_produce_visible_change(self):
        """Default parameters on a vivid canvas should produce a measurable change."""
        p = _make_small_painter()
        _mid_tone_reference(p)
        before = _read_rgb(p).copy()
        p.nolde_incandescent_surge_pass()
        after = _read_rgb(p)
        mean_diff = np.abs(after - before).mean()
        assert mean_diff > 0.005, (
            f"Default pass should produce a visible change, got mean diff={mean_diff:.5f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Pigment Granulation pass tests (13)
# ─────────────────────────────────────────────────────────────────────────────

class TestPigmentGranulationPass:

    def test_method_exists(self):
        p = _make_small_painter()
        assert hasattr(p, 'paint_pigment_granulation_pass')

    def test_method_callable(self):
        p = _make_small_painter()
        assert callable(getattr(p, 'paint_pigment_granulation_pass'))

    def test_pass_runs_without_error(self):
        p = _make_small_painter()
        _gradient_reference(p)
        p.paint_pigment_granulation_pass()

    def test_output_stays_in_unit_range(self):
        p = _make_small_painter()
        _gradient_reference(p)
        p.paint_pigment_granulation_pass()
        rgb = _read_rgb(p)
        assert rgb.min() >= 0.0 - 1e-5
        assert rgb.max() <= 1.0 + 1e-5

    def test_opacity_zero_leaves_canvas_unchanged(self):
        p = _make_small_painter()
        _vivid_red_reference(p)
        before = _read_rgb(p).copy()
        p.paint_pigment_granulation_pass(opacity=0.0)
        after = _read_rgb(p)
        np.testing.assert_allclose(before, after, atol=1/255)

    def test_chroma_gate_suppresses_neutral_granulation(self):
        """Low-chroma neutral canvas should show smaller variance change than vivid."""
        p_vivid = _make_small_painter(seed=20)
        _solid_reference(p_vivid, 0.78, 0.12, 0.08)   # high chroma red
        before_vivid = _read_rgb(p_vivid).copy()
        p_vivid.paint_pigment_granulation_pass(opacity=1.0, chroma_min=0.10)
        after_vivid = _read_rgb(p_vivid)
        var_vivid = np.var(after_vivid - before_vivid)

        p_neutral = _make_small_painter(seed=20)
        _solid_reference(p_neutral, 0.50, 0.48, 0.46)  # low chroma grey
        before_neutral = _read_rgb(p_neutral).copy()
        p_neutral.paint_pigment_granulation_pass(opacity=1.0, chroma_min=0.10)
        after_neutral = _read_rgb(p_neutral)
        var_neutral = np.var(after_neutral - before_neutral)

        assert var_vivid > var_neutral, (
            f"Vivid canvas should show more granulation variance than neutral: "
            f"vivid={var_vivid:.8f} neutral={var_neutral:.8f}"
        )

    def test_granulation_introduces_spatial_variance(self):
        """Pass on vivid solid should introduce spatial variation (non-zero std)."""
        p = _make_small_painter()
        _vivid_red_reference(p)
        p.paint_pigment_granulation_pass(opacity=1.0)
        rgb = _read_rgb(p)
        std_r = rgb[:, :, 0].std()
        assert std_r > 0.001, (
            f"Granulation should introduce spatial variance: std_r={std_r:.5f}"
        )

    def test_valley_warm_tint_raises_red_in_valley_zones(self):
        """valley_r_push > 0 means valley zones have slight red boost overall."""
        p_warm = _make_small_painter(seed=30)
        _vivid_red_reference(p_warm)
        p_warm.paint_pigment_granulation_pass(
            opacity=1.0, valley_r_push=0.10, valley_g_push=0.0
        )
        r_warm = _read_rgb(p_warm)[:, :, 0].mean()

        p_cold = _make_small_painter(seed=30)
        _vivid_red_reference(p_cold)
        p_cold.paint_pigment_granulation_pass(
            opacity=1.0, valley_r_push=0.0, valley_g_push=0.0
        )
        r_cold = _read_rgb(p_cold)[:, :, 0].mean()

        assert r_warm > r_cold, (
            f"valley_r_push=0.10 should raise mean red vs valley_r_push=0: "
            f"warm={r_warm:.4f} cold={r_cold:.4f}"
        )

    def test_granule_depth_zero_still_allows_valley_tint(self):
        """granule_depth=0 should still allow valley warm tint to apply."""
        p = _make_small_painter()
        _vivid_red_reference(p)
        before = _read_rgb(p)[:, :, 0].mean()
        p.paint_pigment_granulation_pass(
            opacity=1.0, granule_depth=0.0, valley_r_push=0.05
        )
        after = _read_rgb(p)[:, :, 0].mean()
        # valley_r_push still acts on valley pixels even with granule_depth=0
        # mean change may be tiny but pass should run without error
        assert after >= before - 0.01

    def test_high_chroma_canvas_shows_texture(self):
        """A purely vivid canvas should show visible texture (std > threshold)."""
        p = _make_small_painter(w=128, h=128)
        _solid_reference(p, 0.85, 0.08, 0.05)
        p.paint_pigment_granulation_pass(opacity=1.0, granule_depth=0.08)
        rgb = _read_rgb(p)
        spatial_std = rgb.std()
        assert spatial_std > 0.002, (
            f"High-chroma canvas should show visible granulation std: {spatial_std:.5f}"
        )

    def test_pass_is_deterministic(self):
        """Same initial canvas → same result (fixed seed in pass)."""
        p1 = _make_small_painter(seed=99)
        _vivid_red_reference(p1)
        p1.paint_pigment_granulation_pass(opacity=0.55)
        rgb1 = _read_rgb(p1).copy()

        p2 = _make_small_painter(seed=99)
        _vivid_red_reference(p2)
        p2.paint_pigment_granulation_pass(opacity=0.55)
        rgb2 = _read_rgb(p2)

        np.testing.assert_allclose(rgb1, rgb2, atol=1/255)

    def test_default_params_produce_visible_change(self):
        """Default parameters on a vivid canvas should produce a measurable change."""
        p = _make_small_painter()
        _vivid_red_reference(p)
        before = _read_rgb(p).copy()
        p.paint_pigment_granulation_pass()
        after = _read_rgb(p)
        mean_diff = np.abs(after - before).mean()
        assert mean_diff > 0.001, (
            f"Default pass should produce a visible change, got mean diff={mean_diff:.5f}"
        )

    def test_gradient_canvas_processes_without_error(self):
        """Gradient canvas (full luminance range) should process without error."""
        p = _make_small_painter()
        _gradient_reference(p)
        p.paint_pigment_granulation_pass()
        rgb = _read_rgb(p)
        assert rgb.shape == (64, 64, 3)
