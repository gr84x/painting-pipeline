"""
test_s250_additions.py -- Session 250 tests for mitchell_gestural_arc_pass,
paint_chromatic_underdark_pass, and the joan_mitchell catalog entry.
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
    arr[:, :w//2, :] = [180, 80, 40]
    arr[:, w//2:, :] = [40, 100, 200]
    return Image.fromarray(arr, "RGB")


def _dark_reference(w=64, h=64):
    from PIL import Image
    arr = np.ones((h, w, 3), dtype=np.uint8) * np.array([22, 18, 14], dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _bright_reference(w=64, h=64):
    from PIL import Image
    arr = np.ones((h, w, 3), dtype=np.uint8) * np.array([230, 220, 210], dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _multicolor_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//2, :w//2, :] = [200, 60, 30]
    arr[:h//2, w//2:, :] = [30, 60, 210]
    arr[h//2:, :w//2, :] = [180, 160, 20]
    arr[h//2:, w//2:, :] = [50, 160, 80]
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, dark=False, bright=False, multicolor=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if dark:
            ref = _dark_reference(w, h)
        elif bright:
            ref = _bright_reference(w, h)
        elif multicolor:
            ref = _multicolor_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.80, 0.76, 0.60), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── mitchell_gestural_arc_pass ────────────────────────────────────────────────

def test_s250_mitchell_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "mitchell_gestural_arc_pass")


def test_s250_mitchell_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.mitchell_gestural_arc_pass()
    assert result is None


def test_s250_mitchell_pass_modifies_canvas():
    """Pass must change pixels on a gradient canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.mitchell_gestural_arc_pass(n_arcs=8, seed=42)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "mitchell_gestural_arc_pass must modify canvas"


def test_s250_mitchell_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.mitchell_gestural_arc_pass(n_arcs=8, seed=42)
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="mitchell_gestural_arc_pass must not alter alpha channel"
    )


def test_s250_mitchell_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.mitchell_gestural_arc_pass(
        n_arcs=20, brightness_shift=0.5, opacity=1.0, seed=1
    )
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s250_mitchell_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas essentially unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.mitchell_gestural_arc_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 2


def test_s250_mitchell_pass_opacity_full_visible_change():
    """opacity=1 on a multicolour canvas should produce visible change."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.mitchell_gestural_arc_pass(n_arcs=10, opacity=1.0, seed=77)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() > 2


def test_s250_mitchell_zero_arcs_no_crash():
    """n_arcs=0 should not crash."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.mitchell_gestural_arc_pass(n_arcs=0)
    after = _get_canvas(p)
    assert after[:, :, :3].max() <= 255


def test_s250_mitchell_many_arcs_no_crash():
    """n_arcs=80 should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.mitchell_gestural_arc_pass(n_arcs=80, seed=5)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s250_mitchell_seed_reproducibility():
    """Same seed produces same result."""
    p1 = _make_small_painter()
    _prime_canvas(p1, multicolor=True)
    p1.mitchell_gestural_arc_pass(n_arcs=12, seed=99)
    out1 = _get_canvas(p1)

    p2 = _make_small_painter()
    _prime_canvas(p2, multicolor=True)
    p2.mitchell_gestural_arc_pass(n_arcs=12, seed=99)
    out2 = _get_canvas(p2)

    np.testing.assert_array_equal(out1, out2, err_msg="Same seed must produce same output")


def test_s250_mitchell_different_seeds_differ():
    """Different seeds should produce different arc layouts."""
    p1 = _make_small_painter()
    _prime_canvas(p1, multicolor=True)
    p1.mitchell_gestural_arc_pass(n_arcs=12, seed=10)
    out1 = _get_canvas(p1)

    p2 = _make_small_painter()
    _prime_canvas(p2, multicolor=True)
    p2.mitchell_gestural_arc_pass(n_arcs=12, seed=20)
    out2 = _get_canvas(p2)

    diff = np.abs(out1.astype(np.int32) - out2.astype(np.int32))
    assert diff[:, :, :3].max() > 0, "Different seeds should produce different outputs"


def test_s250_mitchell_all_dark_arcs():
    """dark_frac=1.0 (all dark arcs) should not crash and should darken."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.mitchell_gestural_arc_pass(
        n_arcs=20, dark_frac=1.0, brightness_shift=0.25, opacity=1.0, seed=3
    )
    after = _get_canvas(p)
    diff = after[:, :, :3].astype(np.int32) - before[:, :, :3].astype(np.int32)
    assert diff.min() < 0, "All-dark arcs should darken some pixels"


def test_s250_mitchell_all_bright_arcs():
    """dark_frac=0.0 (all light arcs) should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.mitchell_gestural_arc_pass(n_arcs=20, dark_frac=0.0, opacity=1.0, seed=4)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s250_mitchell_arc_radius_range():
    """Various arc radius ranges accepted without crash."""
    for rlo, rhi in [(0.05, 0.20), (0.25, 0.50), (0.40, 0.80)]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.mitchell_gestural_arc_pass(n_arcs=8, arc_radius_lo=rlo, arc_radius_hi=rhi, seed=7)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255


def test_s250_mitchell_small_canvas():
    """Pass works on very small canvas."""
    p = _make_small_painter(w=16, h=16)
    _prime_canvas(p, multicolor=True)
    p.mitchell_gestural_arc_pass(n_arcs=6, seed=8)
    after = _get_canvas(p)
    assert after.shape == (16, 16, 4)
    assert after[:, :, :3].max() <= 255


def test_s250_mitchell_wet_strength_zero_no_blend():
    """wet_strength=0 should not crash and should produce valid output."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.mitchell_gestural_arc_pass(n_arcs=10, wet_strength=0.0, seed=11)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s250_mitchell_sequential_with_basquiat():
    """Mitchell followed by Basquiat pass should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.mitchell_gestural_arc_pass(n_arcs=8, seed=12)
    p.basquiat_neo_expressionist_scrawl_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


# ── paint_chromatic_underdark_pass ────────────────────────────────────────────

def test_s250_underdark_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_chromatic_underdark_pass")


def test_s250_underdark_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_chromatic_underdark_pass()
    assert result is None


def test_s250_underdark_pass_modifies_canvas():
    """Pass must change pixels on a canvas with shadow zones."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.paint_chromatic_underdark_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "paint_chromatic_underdark_pass must modify canvas on dark canvas"


def test_s250_underdark_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.paint_chromatic_underdark_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="paint_chromatic_underdark_pass must not alter alpha channel"
    )


def test_s250_underdark_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.paint_chromatic_underdark_pass(
        dark_strength=1.0, clarity_amount=0.8, opacity=1.0
    )
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s250_underdark_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas essentially unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.paint_chromatic_underdark_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1


def test_s250_underdark_high_threshold_affects_more():
    """Higher shadow_thresh should affect a larger fraction of the canvas."""
    p_lo = _make_small_painter()
    _prime_canvas(p_lo, multicolor=True)
    before_lo = _get_canvas(p_lo).copy()
    p_lo.paint_chromatic_underdark_pass(shadow_thresh=0.10, opacity=1.0)
    diff_lo = np.abs(_get_canvas(p_lo).astype(np.int32) - before_lo.astype(np.int32))

    p_hi = _make_small_painter()
    _prime_canvas(p_hi, multicolor=True)
    before_hi = _get_canvas(p_hi).copy()
    p_hi.paint_chromatic_underdark_pass(shadow_thresh=0.80, opacity=1.0)
    diff_hi = np.abs(_get_canvas(p_hi).astype(np.int32) - before_hi.astype(np.int32))

    # Higher threshold should affect more pixels
    assert diff_hi[:, :, :3].sum() >= diff_lo[:, :, :3].sum(), (
        "Higher shadow_thresh should affect at least as many pixels"
    )


def test_s250_underdark_dark_strength_zero_minimal_change():
    """dark_strength=0 and clarity_amount=0 should produce minimal change."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.paint_chromatic_underdark_pass(
        dark_strength=0.0, clarity_amount=0.0, opacity=1.0
    )
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 3, (
        "With dark_strength=0 and clarity_amount=0, change should be minimal"
    )


def test_s250_underdark_bright_canvas_minimal_effect():
    """On a very bright canvas, shadow pass should have almost no effect."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_chromatic_underdark_pass(shadow_thresh=0.10, opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    # On a very bright canvas, shadow mask should be nearly zero
    assert diff[:, :, :3].sum() < before[:, :, :3].sum() * 0.01, (
        "Bright canvas should be nearly unaffected by shadow_thresh=0.10"
    )


def test_s250_underdark_various_dark_hues():
    """Various dark_hue values accepted without crash."""
    for dh in [0.0, 0.25, 0.50, 0.72, 1.0]:
        p = _make_small_painter()
        _prime_canvas(p, dark=True)
        p.paint_chromatic_underdark_pass(dark_hue=dh)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0
        assert after[:, :, :3].max() <= 255


def test_s250_underdark_small_canvas():
    """Pass works on very small canvas."""
    p = _make_small_painter(w=16, h=16)
    _prime_canvas(p, dark=True)
    p.paint_chromatic_underdark_pass()
    after = _get_canvas(p)
    assert after.shape == (16, 16, 4)
    assert after[:, :, :3].max() <= 255


def test_s250_underdark_sequential_after_mitchell():
    """Underdark after Mitchell arc should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.mitchell_gestural_arc_pass(n_arcs=8, seed=50)
    p.paint_chromatic_underdark_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


# ── joan_mitchell catalog entry ───────────────────────────────────────────────

def test_s250_mitchell_in_catalog():
    import art_catalog
    assert "joan_mitchell" in art_catalog.CATALOG, (
        "joan_mitchell key must be present in CATALOG"
    )


def test_s250_mitchell_artist_name():
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    assert "Mitchell" in entry.artist, (
        f"artist field should contain 'Mitchell', got {entry.artist!r}"
    )


def test_s250_mitchell_movement():
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    mv = entry.movement.lower()
    assert "abstract" in mv or "expressionism" in mv, (
        f"movement should reference Abstract Expressionism, got {entry.movement!r}"
    )


def test_s250_mitchell_period():
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    assert "1925" in entry.period, f"period should contain 1925, got {entry.period!r}"
    assert "1992" in entry.period, f"period should contain 1992, got {entry.period!r}"


def test_s250_mitchell_palette_length():
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    assert len(entry.palette) >= 6, (
        f"Mitchell palette should have at least 6 colours, got {len(entry.palette)}"
    )


def test_s250_mitchell_palette_values_valid():
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    for i, color in enumerate(entry.palette):
        assert len(color) == 3, f"palette[{i}] must be an (R,G,B) triple"
        for ch in color:
            assert 0.0 <= ch <= 1.0, f"palette[{i}] channel {ch} out of [0,1] range"


def test_s250_mitchell_palette_has_blue():
    """Mitchell's palette should include a blue."""
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    has_blue = any(c[2] > 0.5 and c[2] > c[0] and c[2] > c[1] for c in entry.palette)
    assert has_blue, "Mitchell palette should include a blue colour"


def test_s250_mitchell_palette_has_green():
    """Mitchell's palette should include a green."""
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    has_green = any(c[1] > 0.4 and c[1] > c[0] and c[1] > c[2] for c in entry.palette)
    assert has_green, "Mitchell palette should include a green colour"


def test_s250_mitchell_famous_works():
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    assert len(entry.famous_works) >= 4, (
        f"Mitchell should have at least 4 famous works, got {len(entry.famous_works)}"
    )


def test_s250_mitchell_works_include_known_title():
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    titles = [w[0].lower() for w in entry.famous_works]
    known = ["ladybug", "george", "city", "sunflower", "grande", "ici", "chasse"]
    assert any(any(k in t for k in known) for t in titles), (
        "Famous works should include at least one known Mitchell title"
    )


def test_s250_mitchell_inspiration_references_pass():
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    insp = entry.inspiration.lower()
    assert "mitchell" in insp or "gestural" in insp or "arc" in insp, (
        "inspiration field should reference mitchell_gestural_arc_pass"
    )


def test_s250_mitchell_technique_nonempty():
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    assert len(entry.technique) > 200, (
        "Mitchell technique description should be substantial (>200 chars)"
    )


def test_s250_mitchell_inspiration_mentions_161st():
    import art_catalog
    entry = art_catalog.CATALOG["joan_mitchell"]
    insp = entry.inspiration.upper()
    assert "SIXTY-FIRST" in insp or "161" in insp, (
        "inspiration should mention the 161st mode"
    )


def test_s250_catalog_total_count():
    import art_catalog
    count = len(art_catalog.CATALOG)
    assert count >= 250, (
        f"After session 250, CATALOG should have at least 250 entries, got {count}"
    )


# ── combined smoke tests ──────────────────────────────────────────────────────

def test_s250_both_passes_sequential():
    """Run both new passes in sequence -- no errors, canvas stays valid."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.mitchell_gestural_arc_pass(n_arcs=8, seed=42)
    p.paint_chromatic_underdark_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s250_full_pipeline_smoke():
    """Full painter workflow with both new passes on small canvas."""
    from PIL import Image
    w, h = 80, 60
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//3, :, :]        = [18, 36, 160]    # cobalt blue upper
    arr[h//3:2*h//3, :w//2, :] = [200, 180, 20]  # yellow left
    arr[h//3:2*h//3, w//2:, :] = [30, 140, 60]   # green right
    arr[2*h//3:, :, :]      = [18, 14, 12]     # near-black lower
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter(w=w, h=h)
    p.tone_ground((0.88, 0.84, 0.64), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=16)
    p.mitchell_gestural_arc_pass(
        n_arcs=12, arc_radius_lo=0.15, arc_radius_hi=0.45,
        brightness_shift=0.18, opacity=0.80, seed=250
    )
    p.paint_chromatic_underdark_pass(
        shadow_thresh=0.30, dark_hue=0.70, dark_strength=0.38,
        clarity_amount=0.20, opacity=0.48
    )
    after = _get_canvas(p)
    assert after.shape == (h, w, 4)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255
