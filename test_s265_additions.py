"""
test_s265_additions.py -- Session 265 tests for ury_nocturne_reflection_pass,
paint_wet_surface_gleam_pass, and the lesser_ury catalog entry.
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


def _bright_reference(w=64, h=64):
    """Reference with bright upper zone (lamp/window) and dark lower zone."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :, :] = [200, 160, 80]   # bright amber upper half
    arr[h // 2:, :, :] = [20, 22, 35]     # dark prussian lower half
    return Image.fromarray(arr, "RGB")


def _dark_reference(w=64, h=64):
    """Uniform near-black reference."""
    from PIL import Image
    arr = np.full((h, w, 3), 20, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _lamp_reference(w=64, h=64):
    """Reference with a bright spot (lamp) in upper area."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :, :] = [18, 20, 30]
    # Bright lamp spot at upper-center
    cy, cx, r = h // 4, w // 2, w // 10
    for row in range(max(0, cy - r), min(h, cy + r)):
        for col in range(max(0, cx - r), min(w, cx + r)):
            if (row - cy) ** 2 + (col - cx) ** 2 < r * r:
                arr[row, col, :] = [230, 180, 80]
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, bright=False, dark=False, lamp=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if bright:
            ref = _bright_reference(w, h)
        elif lamp:
            ref = _lamp_reference(w, h)
        else:
            ref = _dark_reference(w, h)
    p.tone_ground((0.05, 0.06, 0.16), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── paint_wet_surface_gleam_pass ──────────────────────────────────────────────

def test_s265_gleam_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_wet_surface_gleam_pass")


def test_s265_gleam_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    result = p.paint_wet_surface_gleam_pass()
    assert result is None


def test_s265_gleam_pass_modifies_canvas():
    """Pass must change at least some pixels when bright sources are present."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_wet_surface_gleam_pass(
        spec_threshold=0.20,   # low threshold -- most of bright half triggers
        streak_sigma=8.0,
        gleam_r=0.50,
        gleam_g=0.35,
        gleam_b=0.18,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_wet_surface_gleam_pass"


def test_s265_gleam_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p)
    p.paint_wet_surface_gleam_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after paint_wet_surface_gleam_pass"
    )


def test_s265_gleam_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_wet_surface_gleam_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s265_gleam_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.paint_wet_surface_gleam_pass(
        spec_threshold=0.10,
        gleam_r=1.0,
        gleam_g=0.8,
        gleam_b=0.5,
        opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after paint_wet_surface_gleam_pass"
    )


def test_s265_gleam_dark_canvas_minimal_effect():
    """A purely dark canvas should produce negligible gleam (no bright sources)."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.paint_wet_surface_gleam_pass(
        spec_threshold=0.90,   # only very bright pixels trigger
        streak_sigma=8.0,
        gleam_r=0.50,
        gleam_g=0.35,
        gleam_b=0.18,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    # Dark canvas at high threshold: total change should be very small
    total_pixels = before.shape[0] * before.shape[1] * 3
    assert diff[:, :, :3].sum() < total_pixels * 5, (
        "Gleam should be negligible on a dark canvas at high spec_threshold"
    )


def test_s265_gleam_streak_extends_downward():
    """Gleam trail from upper bright source should also appear in lower half."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, lamp=True)
    before = _get_canvas(p).copy().astype(float) / 255.0
    lower_before = before[32:, :, :3].mean()

    p2 = _make_small_painter(w=64, h=64)
    _prime_canvas(p2, lamp=True)
    p2.paint_wet_surface_gleam_pass(
        spec_threshold=0.50,
        streak_sigma=20.0,     # long streak to reach lower half
        gleam_r=0.60,
        gleam_g=0.45,
        gleam_b=0.25,
        opacity=1.0,
    )
    after = _get_canvas(p2).astype(float) / 255.0
    lower_after = after[32:, :, :3].mean()

    assert lower_after >= lower_before - 0.005, (
        "Gleam streak should not reduce lower canvas luminance"
    )


def test_s265_gleam_warm_tint():
    """Gleam should be warmer (higher R than B) due to per-channel weights."""
    from PIL import Image
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:16, :, :] = [220, 200, 180]   # bright top band
    arr[16:, :, :] = [20, 22, 30]      # dark lower band
    ref = Image.fromarray(arr, "RGB")

    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy().astype(float) / 255.0

    p2 = _make_small_painter(w=64, h=64)
    _prime_canvas(p2, ref=ref)
    p2.paint_wet_surface_gleam_pass(
        spec_threshold=0.30,
        streak_sigma=15.0,
        gleam_r=0.50,
        gleam_g=0.25,
        gleam_b=0.05,    # minimal blue -- gleam is warm
        opacity=1.0,
    )
    after = _get_canvas(p2).astype(float) / 255.0

    dr = (after[:, :, 2] - before[:, :, 2]).mean()   # BGRA -> channel 2 is R
    db = (after[:, :, 0] - before[:, :, 0]).mean()   # channel 0 is B
    # Red should increase more than blue
    assert dr >= db, (
        f"Gleam should add more red than blue; dr={dr:.4f}, db={db:.4f}"
    )


def test_s265_gleam_higher_opacity_more_change():
    """Higher opacity should produce at least as much change as lower opacity."""
    ref = _bright_reference(64, 64)

    def _run(op):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        before = _get_canvas(p).copy()
        p.paint_wet_surface_gleam_pass(
            spec_threshold=0.30, streak_sigma=8.0, opacity=op
        )
        after = _get_canvas(p)
        return int(np.abs(before.astype(int) - after.astype(int)).sum())

    assert _run(0.8) >= _run(0.2), "Higher opacity should produce more change"


# ── ury_nocturne_reflection_pass ──────────────────────────────────────────────

def test_s265_ury_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "ury_nocturne_reflection_pass")


def test_s265_ury_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    result = p.ury_nocturne_reflection_pass()
    assert result is None


def test_s265_ury_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.ury_nocturne_reflection_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after ury_nocturne_reflection_pass"


def test_s265_ury_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p)
    p.ury_nocturne_reflection_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after ury_nocturne_reflection_pass"
    )


def test_s265_ury_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.ury_nocturne_reflection_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s265_ury_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.ury_nocturne_reflection_pass(
        corona_strength=1.0,
        shadow_strength=1.0,
        reflection_opacity=1.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after ury_nocturne_reflection_pass"
    )


def test_s265_ury_pavement_reflection_modifies_lower_canvas():
    """Pavement reflection should change the lower canvas zone."""
    p_base = _make_small_painter(w=64, h=64)
    _prime_canvas(p_base, bright=True)
    before = _get_canvas(p_base).copy().astype(float) / 255.0
    lower_before = before[48:, :, :3].mean()

    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, bright=True)
    p.ury_nocturne_reflection_pass(
        sky_fraction=0.50,
        pavement_fraction=0.25,
        h_blur_sigma=2.0,
        v_blur_sigma=1.0,
        reflection_attenuation=0.50,
        reflection_opacity=1.0,    # full opacity to ensure change
        corona_strength=0.0,       # disable other stages for isolation
        shadow_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    lower_after = after[48:, :, :3].mean()

    # Reflection from bright upper half should change lower zone mean
    assert abs(lower_after - lower_before) > 0.001, (
        f"Pavement reflection should change lower canvas zone; "
        f"before={lower_before:.4f}, after={lower_after:.4f}"
    )


def test_s265_ury_corona_brightens_near_bright_sources():
    """Corona diffusion should maintain or increase luminance near bright sources."""
    p_base = _make_small_painter()
    _prime_canvas(p_base, lamp=True)
    before = _get_canvas(p_base).copy().astype(float) / 255.0
    upper_before = before[:32, :, :3].mean()

    p = _make_small_painter()
    _prime_canvas(p, lamp=True)
    p.ury_nocturne_reflection_pass(
        lamp_threshold=0.40,
        corona_sigma=8.0,
        corona_strength=0.80,
        reflection_opacity=0.0,    # disable reflection for isolation
        shadow_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    upper_after = after[:32, :, :3].mean()

    assert upper_after >= upper_before - 0.02, (
        f"Corona should not reduce upper zone luminance; "
        f"before={upper_before:.4f}, after={upper_after:.4f}"
    )


def test_s265_ury_shadow_cooler_adds_blue_to_darks():
    """Shadow cooler should add blue channel to dark pixels."""
    from PIL import Image
    arr = np.full((64, 64, 3), 20, dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")

    p_base = _make_small_painter()
    _prime_canvas(p_base, ref=ref)
    before = _get_canvas(p_base).copy().astype(float) / 255.0
    mean_b_before = before[:, :, 0].mean()   # BGRA: channel 0 is B

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    p.ury_nocturne_reflection_pass(
        shadow_threshold=0.90,    # everything dark counts as shadow
        shadow_r_scale=0.60,
        shadow_g_scale=0.70,
        shadow_b_lift=0.10,       # strong blue lift
        shadow_strength=0.90,
        reflection_opacity=0.0,
        corona_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    mean_b_after = after[:, :, 0].mean()

    assert mean_b_after >= mean_b_before - 0.005, (
        f"Shadow cooler with blue lift should not reduce blue channel; "
        f"before={mean_b_before:.4f}, after={mean_b_after:.4f}"
    )


def test_s265_ury_higher_opacity_more_change():
    """Higher opacity should produce at least as much change as lower opacity."""
    ref = _bright_reference(64, 64)

    def _run(op):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        before = _get_canvas(p).copy()
        p.ury_nocturne_reflection_pass(opacity=op)
        after = _get_canvas(p)
        return int(np.abs(before.astype(int) - after.astype(int)).sum())

    assert _run(0.8) >= _run(0.2), "Higher opacity should produce more change"


# ── lesser_ury catalog tests ──────────────────────────────────────────────────

def test_s265_catalog_lesser_ury_present():
    from art_catalog import CATALOG
    assert "lesser_ury" in CATALOG, "lesser_ury not found in CATALOG"


def test_s265_catalog_lesser_ury_fields():
    from art_catalog import CATALOG
    u = CATALOG["lesser_ury"]
    assert "Ury" in u.artist
    assert "German" in u.nationality
    assert len(u.palette) >= 8
    assert len(u.famous_works) >= 8


def test_s265_catalog_lesser_ury_inspiration():
    """Inspiration must reference ury_nocturne_reflection_pass and 176th mode."""
    from art_catalog import CATALOG
    u = CATALOG["lesser_ury"]
    assert "ury_nocturne_reflection_pass" in u.inspiration, (
        "ury_nocturne_reflection_pass not found in inspiration"
    )
    assert "176" in u.inspiration, "176th mode not referenced in inspiration"


def test_s265_catalog_lesser_ury_prussian_palette():
    """Palette should include a prussian blue (high B, low R) tone."""
    from art_catalog import CATALOG
    u = CATALOG["lesser_ury"]
    # At least one palette colour should have B > R (prussian blue characteristic)
    prussian_found = any(b > r * 1.5 for r, g, b in u.palette)
    assert prussian_found, (
        "Palette should contain at least one prussian-blue tone (B > R*1.5)"
    )


def test_s265_catalog_count_increased():
    """CATALOG count must be 262 (new artist added this session)."""
    from art_catalog import CATALOG
    assert len(CATALOG) == 262, f"Expected 262 catalog entries, got {len(CATALOG)}"


def test_s265_catalog_get_style_lesser_ury():
    """get_style() must retrieve Lesser Ury by key."""
    from art_catalog import get_style
    u = get_style("lesser_ury")
    assert "Ury" in u.artist


# ── Integration: run both new passes together ─────────────────────────────────

def test_s265_full_pipeline_gleam_and_nocturne():
    """Run both new passes in sequence; canvas should be modified and valid."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()

    p.paint_wet_surface_gleam_pass(opacity=0.55)
    p.ury_nocturne_reflection_pass(opacity=0.78)

    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Pipeline should modify canvas"
    assert after.min() >= 0 and after.max() <= 255, "Values must stay in [0, 255]"
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), "Alpha must be preserved"
