"""
test_s252_additions.py -- Session 252 tests for richter_squeegee_drag_pass,
paint_surface_tooth_pass, and the gerhard_richter catalog entry.
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
    arr[:, :w // 2, :] = [180, 80, 40]
    arr[:, w // 2:, :] = [40, 100, 200]
    return Image.fromarray(arr, "RGB")


def _multicolor_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :w // 2, :] = [200, 60, 30]
    arr[:h // 2, w // 2:, :] = [30, 60, 210]
    arr[h // 2:, :w // 2, :] = [180, 160, 20]
    arr[h // 2:, w // 2:, :] = [50, 160, 80]
    return Image.fromarray(arr, "RGB")


def _saturated_stripe_reference(w=64, h=64):
    """Alternating saturated horizontal stripes for trail detection."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        if (y // 8) % 2 == 0:
            arr[y, :] = [220, 30, 20]   # saturated red
        else:
            arr[y, :] = [30, 20, 210]   # saturated blue
    return Image.fromarray(arr, "RGB")


def _neutral_grey_reference(w=64, h=64):
    """Uniform mid-grey -- good for tooth texture tests."""
    from PIL import Image
    arr = np.full((h, w, 3), 128, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, multi=False, stripes=False, grey=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if multi:
            ref = _multicolor_reference(w, h)
        elif stripes:
            ref = _saturated_stripe_reference(w, h)
        elif grey:
            ref = _neutral_grey_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.82, 0.76, 0.62), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── richter_squeegee_drag_pass ────────────────────────────────────────────────

def test_s252_richter_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "richter_squeegee_drag_pass")


def test_s252_richter_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.richter_squeegee_drag_pass()
    assert result is None


def test_s252_richter_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p, multi=True)
    before = _get_canvas(p).copy()
    p.richter_squeegee_drag_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after richter_squeegee_drag_pass"


def test_s252_richter_pass_preserves_alpha():
    """Alpha channel must remain fully opaque (255) after the pass."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.richter_squeegee_drag_pass()
    canvas = _get_canvas(p)
    assert (canvas[:, :, 3] == 255).all(), "Alpha channel corrupted"


def test_s252_richter_pass_zero_opacity_is_noop():
    """At opacity=0, canvas must be pixel-identical to before."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.richter_squeegee_drag_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 should leave canvas unchanged"


def test_s252_richter_pass_channels_in_range():
    """All RGB values must remain in [0, 255] after the pass."""
    p = _make_small_painter()
    _prime_canvas(p, multi=True)
    p.richter_squeegee_drag_pass(opacity=1.0)
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s252_richter_pass_drag_mixes_colors():
    """With high drag_fraction, colours should become more horizontally uniform."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, multi=True)
    before = _get_canvas(p).copy()
    # Measure horizontal colour variance before
    var_before = before[:, :, 2].astype(float).var(axis=1).mean()
    p.richter_squeegee_drag_pass(drag_fraction=0.95, n_bands=8, opacity=1.0)
    after = _get_canvas(p)
    var_after = after[:, :, 2].astype(float).var(axis=1).mean()
    # High drag should reduce horizontal variance
    assert var_after <= var_before * 1.1, (
        f"High drag_fraction should reduce horizontal variance: "
        f"before={var_before:.2f}, after={var_after:.2f}"
    )


def test_s252_richter_pass_residue_modulation_varies_luminance():
    """Band residue modulation should create non-zero per-row luminance variation."""
    p = _make_small_painter(w=64, h=128)
    _prime_canvas(p, grey=True)
    p.richter_squeegee_drag_pass(
        n_bands=4,
        band_min=20,
        band_max=32,
        drag_fraction=0.0,    # disable drag to isolate residue
        trail_strength=0.0,   # disable trails
        residue_amp=0.08,
        opacity=1.0,
        seed=1234,
    )
    canvas = _get_canvas(p)
    lum_by_row = canvas[:, :, 2].astype(float).mean(axis=1)
    lum_std = lum_by_row.std()
    assert lum_std > 0.5, (
        f"Residue modulation should introduce row luminance variation; std={lum_std:.3f}"
    )


def test_s252_richter_pass_reproducible_with_seed():
    """Same seed must produce identical output."""
    p1 = _make_small_painter()
    _prime_canvas(p1, multi=True)
    p1.richter_squeegee_drag_pass(seed=999)
    out1 = _get_canvas(p1).copy()

    p2 = _make_small_painter()
    _prime_canvas(p2, multi=True)
    p2.richter_squeegee_drag_pass(seed=999)
    out2 = _get_canvas(p2)

    assert np.array_equal(out1, out2), "Different outputs for same seed"


def test_s252_richter_pass_different_seeds_differ():
    """Different seeds must produce meaningfully different outputs."""
    p1 = _make_small_painter()
    _prime_canvas(p1, multi=True)
    p1.richter_squeegee_drag_pass(seed=100)
    out1 = _get_canvas(p1).copy()

    p2 = _make_small_painter()
    _prime_canvas(p2, multi=True)
    p2.richter_squeegee_drag_pass(seed=200)
    out2 = _get_canvas(p2)

    diff = np.abs(out1.astype(int) - out2.astype(int)).sum()
    assert diff > 0, "Different seeds should produce different outputs"


def test_s252_richter_pass_high_opacity_more_change():
    """Higher opacity should produce more change relative to low opacity."""
    p_lo = _make_small_painter()
    _prime_canvas(p_lo, multi=True)
    before_lo = _get_canvas(p_lo).copy()
    p_lo.richter_squeegee_drag_pass(opacity=0.1)
    diff_lo = np.abs(_get_canvas(p_lo).astype(int) - before_lo.astype(int)).sum()

    p_hi = _make_small_painter()
    _prime_canvas(p_hi, multi=True)
    before_hi = _get_canvas(p_hi).copy()
    p_hi.richter_squeegee_drag_pass(opacity=0.9)
    diff_hi = np.abs(_get_canvas(p_hi).astype(int) - before_hi.astype(int)).sum()

    assert diff_hi > diff_lo, "Higher opacity should produce more total change"


def test_s252_richter_pass_stripes_trigger_trails():
    """Saturated stripes should activate trail detection."""
    p = _make_small_painter()
    _prime_canvas(p, stripes=True)
    before = _get_canvas(p).copy()
    p.richter_squeegee_drag_pass(
        sat_threshold=0.10,
        trail_length=12,
        trail_strength=0.80,
        drag_fraction=0.0,
        residue_amp=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int)).sum()
    assert diff > 100, "Trail stage should produce visible change on saturated stripes"


def test_s252_richter_pass_minimal_bands_runs():
    """Should run without error with just 1 band."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.richter_squeegee_drag_pass(n_bands=1, band_min=64, band_max=64)


def test_s252_richter_pass_large_drag_offset_clips():
    """Large drag_offset beyond canvas should not raise an error."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.richter_squeegee_drag_pass(drag_offset=500)


# ── paint_surface_tooth_pass ──────────────────────────────────────────────────

def test_s252_tooth_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_surface_tooth_pass")


def test_s252_tooth_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_surface_tooth_pass()
    assert result is None


def test_s252_tooth_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p, grey=True)
    before = _get_canvas(p).copy()
    p.paint_surface_tooth_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_surface_tooth_pass"


def test_s252_tooth_pass_preserves_alpha():
    p = _make_small_painter()
    _prime_canvas(p)
    p.paint_surface_tooth_pass()
    assert (_get_canvas(p)[:, :, 3] == 255).all()


def test_s252_tooth_pass_zero_opacity_is_noop():
    p = _make_small_painter()
    _prime_canvas(p, grey=True)
    before = _get_canvas(p).copy()
    p.paint_surface_tooth_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 should leave canvas unchanged"


def test_s252_tooth_pass_channels_in_range():
    p = _make_small_painter()
    _prime_canvas(p, multi=True)
    p.paint_surface_tooth_pass(opacity=1.0)
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s252_tooth_pass_introduces_spatial_variation():
    """On a uniform grey canvas, tooth pass should introduce per-pixel variation."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, grey=True)
    before = _get_canvas(p).copy()
    # Before should be quite uniform
    before_std = before[:, :, :3].astype(float).std()
    p.paint_surface_tooth_pass(
        fiber_amplitude=0.06,
        cross_boost=0.04,
        ridge_strength=0.04,
        opacity=1.0,
        seed=11,
    )
    after = _get_canvas(p)
    after_std = after[:, :, :3].astype(float).std()
    assert after_std > before_std, (
        f"Tooth pass should add spatial variation: before_std={before_std:.3f}, "
        f"after_std={after_std:.3f}"
    )


def test_s252_tooth_pass_larger_amplitude_more_effect():
    """Higher fiber_amplitude should produce more total pixel change."""
    p_lo = _make_small_painter(w=64, h=64)
    _prime_canvas(p_lo, grey=True)
    before_lo = _get_canvas(p_lo).copy()
    p_lo.paint_surface_tooth_pass(fiber_amplitude=0.005, cross_boost=0.0, ridge_strength=0.0, opacity=1.0, seed=42)
    diff_lo = np.abs(_get_canvas(p_lo).astype(int) - before_lo.astype(int)).sum()

    p_hi = _make_small_painter(w=64, h=64)
    _prime_canvas(p_hi, grey=True)
    before_hi = _get_canvas(p_hi).copy()
    p_hi.paint_surface_tooth_pass(fiber_amplitude=0.06, cross_boost=0.0, ridge_strength=0.0, opacity=1.0, seed=42)
    diff_hi = np.abs(_get_canvas(p_hi).astype(int) - before_hi.astype(int)).sum()

    assert diff_hi > diff_lo, "Higher fiber_amplitude should produce more pixel change"


def test_s252_tooth_pass_reproducible():
    p1 = _make_small_painter(w=48, h=48)
    _prime_canvas(p1, grey=True)
    p1.paint_surface_tooth_pass(seed=77)
    out1 = _get_canvas(p1).copy()

    p2 = _make_small_painter(w=48, h=48)
    _prime_canvas(p2, grey=True)
    p2.paint_surface_tooth_pass(seed=77)
    out2 = _get_canvas(p2)

    assert np.array_equal(out1, out2)


def test_s252_tooth_pass_grain_size_affects_pattern():
    """Different grain sizes should produce different spatial patterns."""
    p_fine = _make_small_painter(w=64, h=64)
    _prime_canvas(p_fine, grey=True)
    p_fine.paint_surface_tooth_pass(grain_size=4, opacity=1.0, seed=99)
    out_fine = _get_canvas(p_fine).copy()

    p_coarse = _make_small_painter(w=64, h=64)
    _prime_canvas(p_coarse, grey=True)
    p_coarse.paint_surface_tooth_pass(grain_size=20, opacity=1.0, seed=99)
    out_coarse = _get_canvas(p_coarse)

    diff = np.abs(out_fine.astype(int) - out_coarse.astype(int)).sum()
    assert diff > 0, "Fine and coarse grain should produce different patterns"


def test_s252_tooth_pass_small_grain_size():
    """grain_size=2 (minimum) should not raise an error."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.paint_surface_tooth_pass(grain_size=2)


def test_s252_tooth_pass_full_pipeline():
    """Tooth pass should work cleanly after richter_squeegee_drag_pass."""
    p = _make_small_painter()
    _prime_canvas(p, multi=True)
    p.richter_squeegee_drag_pass()
    p.paint_surface_tooth_pass()
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0
    assert (canvas[:, :, 3] == 255).all()


# ── art_catalog: gerhard_richter entry ───────────────────────────────────────

def test_s252_catalog_richter_entry_exists():
    from art_catalog import CATALOG
    assert "gerhard_richter" in CATALOG, "gerhard_richter not found in CATALOG"


def test_s252_catalog_richter_has_required_fields():
    from art_catalog import CATALOG, ArtStyle
    s = CATALOG["gerhard_richter"]
    assert isinstance(s, ArtStyle)
    assert s.artist == "Gerhard Richter"
    assert "1932" in s.period
    assert len(s.palette) >= 8
    assert len(s.famous_works) >= 6
    assert s.stroke_size > 0
    assert 0.0 <= s.wet_blend <= 1.0
    assert 0.0 <= s.edge_softness <= 1.0
    assert 0.0 <= s.jitter <= 1.0


def test_s252_catalog_richter_palette_rgb_range():
    from art_catalog import CATALOG
    for c in CATALOG["gerhard_richter"].palette:
        assert len(c) == 3, "Each palette colour must be an (R, G, B) triple"
        for channel in c:
            assert 0.0 <= channel <= 1.0, f"Palette channel out of [0, 1]: {channel}"


def test_s252_catalog_richter_famous_works_format():
    from art_catalog import CATALOG
    for title, year in CATALOG["gerhard_richter"].famous_works:
        assert isinstance(title, str) and len(title) > 0
        assert isinstance(year, str) and len(year) >= 4


def test_s252_catalog_richter_inspiration_mentions_mode():
    from art_catalog import CATALOG
    insp = CATALOG["gerhard_richter"].inspiration
    assert "163" in insp, "Inspiration must reference 163rd mode"
    assert "squeegee" in insp.lower(), "Inspiration must mention squeegee technique"


def test_s252_catalog_total_count():
    from art_catalog import CATALOG
    assert len(CATALOG) >= 252, f"Expected at least 252 catalog entries, got {len(CATALOG)}"


def test_s252_catalog_get_style_richter():
    from art_catalog import get_style
    s = get_style("gerhard_richter")
    assert s is not None
    assert s.artist == "Gerhard Richter"


# ── Combined pipeline tests ───────────────────────────────────────────────────

def test_s252_full_pipeline_no_exceptions():
    """Full s252 pipeline (ground → block_in → squeegee → tooth) must complete."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, multi=True)
    p.richter_squeegee_drag_pass(n_bands=6, opacity=0.75)
    p.paint_surface_tooth_pass(opacity=0.6)
    canvas = _get_canvas(p)
    assert canvas.shape == (80, 80, 4)


def test_s252_squeegee_before_tooth_vs_reversed():
    """Order should matter: squeegee then tooth vs tooth then squeegee differ."""
    p1 = _make_small_painter()
    _prime_canvas(p1, multi=True)
    p1.richter_squeegee_drag_pass(seed=5)
    p1.paint_surface_tooth_pass(seed=5)
    out1 = _get_canvas(p1).copy()

    p2 = _make_small_painter()
    _prime_canvas(p2, multi=True)
    p2.paint_surface_tooth_pass(seed=5)
    p2.richter_squeegee_drag_pass(seed=5)
    out2 = _get_canvas(p2)

    diff = np.abs(out1.astype(int) - out2.astype(int)).sum()
    assert diff > 0, "Pass order should affect output"
