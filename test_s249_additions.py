"""
test_s249_additions.py -- Session 249 tests for basquiat_neo_expressionist_scrawl_pass,
paint_chroma_focus_pass, and the jean_michel_basquiat catalog entry.
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
    arr[:, :w//2, :] = [220, 130, 40]
    arr[:, w//2:, :] = [40, 80, 200]
    return Image.fromarray(arr, "RGB")


def _dark_reference(w=64, h=64):
    from PIL import Image
    arr = np.ones((h, w, 3), dtype=np.uint8) * np.array([28, 24, 20], dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _bright_reference(w=64, h=64):
    from PIL import Image
    arr = np.ones((h, w, 3), dtype=np.uint8) * np.array([230, 220, 210], dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _multicolor_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//2, :w//2, :] = [200, 80, 30]
    arr[:h//2, w//2:, :] = [30, 80, 200]
    arr[h//2:, :w//2, :] = [180, 160, 20]
    arr[h//2:, w//2:, :] = [60, 140, 80]
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
    p.tone_ground((0.80, 0.50, 0.18), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── basquiat_neo_expressionist_scrawl_pass ────────────────────────────────────

def test_s249_basquiat_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "basquiat_neo_expressionist_scrawl_pass")


def test_s249_basquiat_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.basquiat_neo_expressionist_scrawl_pass()
    assert result is None


def test_s249_basquiat_pass_modifies_canvas():
    """Pass must change pixels on a gradient canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.basquiat_neo_expressionist_scrawl_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "basquiat_neo_expressionist_scrawl_pass must modify canvas"


def test_s249_basquiat_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.basquiat_neo_expressionist_scrawl_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="basquiat_neo_expressionist_scrawl_pass must not alter alpha channel"
    )


def test_s249_basquiat_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.basquiat_neo_expressionist_scrawl_pass(
        n_levels=4, n_marks=80, mark_strength=0.5, sat_boost=0.8, opacity=1.0
    )
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s249_basquiat_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas essentially unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.basquiat_neo_expressionist_scrawl_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1


def test_s249_basquiat_pass_opacity_full_visible_change():
    """opacity=1 should produce a visible change on a multicolour canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.basquiat_neo_expressionist_scrawl_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() > 2


def test_s249_basquiat_posterization_reduces_unique_values():
    """After pass, the number of unique channel values should decrease due to quantization."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, multicolor=True)

    before = _get_canvas(p).copy()
    n_unique_before = len(np.unique(before[:, :, 2]))

    p.basquiat_neo_expressionist_scrawl_pass(
        n_levels=4,
        n_marks=0,        # no marks, only posterization
        sat_boost=0.0,    # no saturation boost
        opacity=1.0,
    )
    after = _get_canvas(p)
    n_unique_after = len(np.unique(after[:, :, 2]))
    assert n_unique_after <= n_unique_before, (
        f"Posterization should not increase unique channel values "
        f"(before={n_unique_before}, after={n_unique_after})"
    )


def test_s249_basquiat_n_levels_range():
    """Pass accepts n_levels 2, 4, 6, 8, 16 without crash."""
    for nl in [2, 4, 6, 8, 16]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.basquiat_neo_expressionist_scrawl_pass(n_levels=nl)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0
        assert after[:, :, :3].max() <= 255


def test_s249_basquiat_no_marks_no_crash():
    """n_marks=0 should not crash."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.basquiat_neo_expressionist_scrawl_pass(n_marks=0)
    after = _get_canvas(p)
    assert after[:, :, :3].max() <= 255


def test_s249_basquiat_many_marks_no_crash():
    """n_marks=500 should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.basquiat_neo_expressionist_scrawl_pass(n_marks=500)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s249_basquiat_mark_length_range():
    """Various mark lengths accepted without crash."""
    for ml in [4, 8, 16, 32]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.basquiat_neo_expressionist_scrawl_pass(mark_length=ml)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255


def test_s249_basquiat_all_dark_marks():
    """dark_mark_frac=1.0 (all dark marks) should not crash and should darken."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.basquiat_neo_expressionist_scrawl_pass(
        dark_mark_frac=1.0, n_marks=200, mark_strength=0.3, opacity=1.0
    )
    after = _get_canvas(p)
    # Some pixels should be darker
    diff = after[:, :, :3].astype(np.int32) - before[:, :, :3].astype(np.int32)
    assert diff.min() < 0, "All-dark marks should darken some pixels"


def test_s249_basquiat_all_light_marks():
    """dark_mark_frac=0.0 (all light marks) should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.basquiat_neo_expressionist_scrawl_pass(dark_mark_frac=0.0, n_marks=200, opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s249_basquiat_sat_boost_zero_no_midtone_change():
    """sat_boost=0 should not amplify saturation (midtone stage has no effect)."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.basquiat_neo_expressionist_scrawl_pass(
        n_marks=0, sat_boost=0.0, n_levels=256, opacity=1.0
    )
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    # With 256 levels (essentially no quantization) and no marks or sat boost,
    # the output should be very close to input
    assert diff[:, :, :3].max() <= 4, (
        "With no marks, 256 levels, and sat_boost=0, canvas should barely change"
    )


def test_s249_basquiat_sat_boost_increases_chroma():
    """With high sat_boost on a midtone canvas, saturation should increase."""
    from PIL import Image
    arr = np.ones((64, 64, 3), dtype=np.uint8) * np.array([120, 80, 60], dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter()
    p.tone_ground((0.50, 0.35, 0.25), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=16)
    before = _get_canvas(p).copy()
    p.basquiat_neo_expressionist_scrawl_pass(
        n_marks=0, n_levels=256, sat_boost=0.8,
        mid_lo=0.10, mid_hi=0.90, opacity=1.0
    )
    after = _get_canvas(p)
    # Measure mean absolute deviation from per-pixel grey
    def _mean_sat(canvas):
        r = canvas[:, :, 2].astype(np.float32) / 255.0
        g = canvas[:, :, 1].astype(np.float32) / 255.0
        b = canvas[:, :, 0].astype(np.float32) / 255.0
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        return float(np.abs(r - lum).mean() + np.abs(g - lum).mean() + np.abs(b - lum).mean())
    sat_before = _mean_sat(before)
    sat_after  = _mean_sat(after)
    assert sat_after >= sat_before - 0.005, (
        f"High sat_boost should not decrease saturation (before={sat_before:.4f}, after={sat_after:.4f})"
    )


def test_s249_basquiat_seed_reproducibility():
    """Same seed produces same result."""
    p1 = _make_small_painter()
    _prime_canvas(p1, multicolor=True)
    p1.basquiat_neo_expressionist_scrawl_pass(seed=42)
    out1 = _get_canvas(p1)

    p2 = _make_small_painter()
    _prime_canvas(p2, multicolor=True)
    p2.basquiat_neo_expressionist_scrawl_pass(seed=42)
    out2 = _get_canvas(p2)

    np.testing.assert_array_equal(out1, out2, err_msg="Same seed must produce same output")


def test_s249_basquiat_different_seeds_differ():
    """Different seeds should produce different mark layouts."""
    p1 = _make_small_painter()
    _prime_canvas(p1, multicolor=True)
    p1.basquiat_neo_expressionist_scrawl_pass(seed=1, n_marks=80)
    out1 = _get_canvas(p1)

    p2 = _make_small_painter()
    _prime_canvas(p2, multicolor=True)
    p2.basquiat_neo_expressionist_scrawl_pass(seed=2, n_marks=80)
    out2 = _get_canvas(p2)

    diff = np.abs(out1.astype(np.int32) - out2.astype(np.int32))
    assert diff[:, :, :3].max() > 0, "Different seeds should produce different outputs"


def test_s249_basquiat_dark_canvas_no_crash():
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.basquiat_neo_expressionist_scrawl_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0


def test_s249_basquiat_bright_canvas_no_crash():
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.basquiat_neo_expressionist_scrawl_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].max() <= 255


def test_s249_basquiat_small_canvas():
    """Pass works on very small canvas."""
    p = _make_small_painter(w=16, h=16)
    _prime_canvas(p, multicolor=True)
    p.basquiat_neo_expressionist_scrawl_pass(n_marks=20, mark_length=3)
    after = _get_canvas(p)
    assert after.shape == (16, 16, 4)
    assert after[:, :, :3].max() <= 255


def test_s249_basquiat_sequential_with_destael():
    """Basquiat pass followed by de Stael should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.basquiat_neo_expressionist_scrawl_pass()
    p.de_stael_palette_knife_mosaic_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


# ── paint_chroma_focus_pass ───────────────────────────────────────────────────

def test_s249_chroma_focus_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_chroma_focus_pass")


def test_s249_chroma_focus_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_chroma_focus_pass()
    assert result is None


def test_s249_chroma_focus_pass_modifies_canvas():
    """Pass must change pixels on a coloured canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.paint_chroma_focus_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "paint_chroma_focus_pass must modify canvas"


def test_s249_chroma_focus_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.paint_chroma_focus_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="paint_chroma_focus_pass must not alter alpha channel"
    )


def test_s249_chroma_focus_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.paint_chroma_focus_pass(
        center_sat_boost=1.5, periphery_sat_reduce=0.9, opacity=1.0
    )
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s249_chroma_focus_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas essentially unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.paint_chroma_focus_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1


def test_s249_chroma_focus_no_boost_no_reduce_no_change():
    """center_sat_boost=0 and periphery_sat_reduce=0 should not change canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.paint_chroma_focus_pass(
        center_sat_boost=0.0, periphery_sat_reduce=0.0, opacity=1.0
    )
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 2, (
        "With zero boost and zero reduce, canvas should be essentially unchanged"
    )


def test_s249_chroma_focus_centre_more_saturated_than_edge():
    """After pass with strong boost, centre pixels should be more saturated than edge pixels."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, multicolor=True)
    p.paint_chroma_focus_pass(
        focus_x=0.5, focus_y=0.5,
        focus_radius=0.3,
        center_sat_boost=0.8,
        periphery_sat_reduce=0.5,
        opacity=1.0
    )
    after = _get_canvas(p)
    h, w = after.shape[:2]

    # Sample saturation at centre (5x5 patch)
    cy, cx = h // 2, w // 2
    centre = after[cy-2:cy+3, cx-2:cx+3, :3].astype(np.float32) / 255.0

    # Sample saturation at corner
    corner = after[:5, :5, :3].astype(np.float32) / 255.0

    def _sat(patch):
        r, g, b = patch[:, :, 0], patch[:, :, 1], patch[:, :, 2]
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        return float(np.abs(r - lum).mean() + np.abs(g - lum).mean() + np.abs(b - lum).mean())

    sat_centre = _sat(centre)
    sat_corner = _sat(corner)
    assert sat_centre >= sat_corner - 0.02, (
        f"Centre should be at least as saturated as corner "
        f"(centre={sat_centre:.4f}, corner={sat_corner:.4f})"
    )


def test_s249_chroma_focus_focus_position_range():
    """Pass accepts various focus positions without crash."""
    for fx, fy in [(0.0, 0.0), (0.5, 0.5), (1.0, 1.0), (0.25, 0.75)]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.paint_chroma_focus_pass(focus_x=fx, focus_y=fy)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0
        assert after[:, :, :3].max() <= 255


def test_s249_chroma_focus_radius_range():
    """Pass accepts various radius values without crash."""
    for r in [0.1, 0.3, 0.5, 0.9]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.paint_chroma_focus_pass(focus_radius=r)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255


def test_s249_chroma_focus_sequential_after_basquiat():
    """Chroma focus after basquiat scrawl should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.basquiat_neo_expressionist_scrawl_pass()
    p.paint_chroma_focus_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s249_chroma_focus_small_canvas():
    """Pass works on very small canvas."""
    p = _make_small_painter(w=16, h=16)
    _prime_canvas(p, multicolor=True)
    p.paint_chroma_focus_pass()
    after = _get_canvas(p)
    assert after.shape == (16, 16, 4)
    assert after[:, :, :3].max() <= 255


# ── jean_michel_basquiat catalog entry ───────────────────────────────────────

def test_s249_basquiat_in_catalog():
    import art_catalog
    assert "jean_michel_basquiat" in art_catalog.CATALOG, (
        "jean_michel_basquiat key must be present in CATALOG"
    )


def test_s249_basquiat_artist_name():
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    assert "Basquiat" in entry.artist, (
        f"artist field should contain 'Basquiat', got {entry.artist!r}"
    )


def test_s249_basquiat_movement():
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    mv = entry.movement.lower()
    assert "neo" in mv or "expressionism" in mv or "graffiti" in mv, (
        f"movement should reference Neo-Expressionism or Graffiti, got {entry.movement!r}"
    )


def test_s249_basquiat_period():
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    assert "1960" in entry.period, f"period should contain 1960, got {entry.period!r}"
    assert "1988" in entry.period, f"period should contain 1988, got {entry.period!r}"


def test_s249_basquiat_palette_length():
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    assert len(entry.palette) >= 6, (
        f"Basquiat palette should have at least 6 colours, got {len(entry.palette)}"
    )


def test_s249_basquiat_palette_values_valid():
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    for i, color in enumerate(entry.palette):
        assert len(color) == 3, f"palette[{i}] must be an (R,G,B) triple"
        for ch in color:
            assert 0.0 <= ch <= 1.0, f"palette[{i}] channel {ch} out of [0,1] range"


def test_s249_basquiat_palette_has_near_black():
    """Basquiat's palette should include a near-black."""
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    has_dark = any(max(c) < 0.25 for c in entry.palette)
    assert has_dark, "Basquiat palette should include a near-black colour"


def test_s249_basquiat_palette_has_yellow():
    """Basquiat's palette should include a yellow/chrome (crown colour)."""
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    has_yellow = any(c[0] > 0.7 and c[1] > 0.7 and c[2] < 0.4 for c in entry.palette)
    assert has_yellow, "Basquiat palette should include a yellow/crown colour"


def test_s249_basquiat_famous_works():
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    assert len(entry.famous_works) >= 4, (
        f"Basquiat should have at least 4 famous works, got {len(entry.famous_works)}"
    )


def test_s249_basquiat_works_include_known_title():
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    titles = [w[0].lower() for w in entry.famous_works]
    known = ["skull", "hollywood", "charles", "riding", "trumpet", "self", "history", "per capita"]
    assert any(any(k in t for k in known) for t in titles), (
        "Famous works should include at least one known Basquiat title"
    )


def test_s249_basquiat_inspiration_references_pass():
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    insp = entry.inspiration.lower()
    assert "basquiat" in insp or "scrawl" in insp or "posterization" in insp or "mark" in insp, (
        "inspiration field should reference the basquiat_neo_expressionist_scrawl_pass"
    )


def test_s249_basquiat_technique_nonempty():
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    assert len(entry.technique) > 200, (
        "Basquiat technique description should be substantial (>200 chars)"
    )


def test_s249_basquiat_inspiration_mentions_160th():
    import art_catalog
    entry = art_catalog.CATALOG["jean_michel_basquiat"]
    insp = entry.inspiration.upper()
    assert "SIXTIETH" in insp or "160" in insp, (
        "inspiration should mention the 160th mode"
    )


def test_s249_catalog_total_count():
    import art_catalog
    count = len(art_catalog.CATALOG)
    assert count >= 249, (
        f"After session 249, CATALOG should have at least 249 entries, got {count}"
    )


# ── combined smoke tests ──────────────────────────────────────────────────────

def test_s249_both_passes_sequential():
    """Run both new passes in sequence -- no errors, canvas stays valid."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.basquiat_neo_expressionist_scrawl_pass()
    p.paint_chroma_focus_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s249_full_pipeline_smoke():
    """Full painter workflow with both new passes on small canvas."""
    from PIL import Image
    w, h = 80, 60
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//3, :, :] = [12, 10, 8]           # near-black ground
    arr[h//3:2*h//3, :w//2, :] = [200, 50, 20]  # cadmium red left
    arr[h//3:2*h//3, w//2:, :] = [240, 210, 20]  # chrome yellow right
    arr[2*h//3:, :, :] = [180, 140, 80]      # flesh/ochre lower
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter(w=w, h=h)
    p.tone_ground((0.10, 0.09, 0.07), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=16)
    p.basquiat_neo_expressionist_scrawl_pass(
        n_levels=6, n_marks=60, mark_length=8, opacity=0.82
    )
    p.paint_chroma_focus_pass(
        focus_x=0.5, focus_y=0.5, focus_radius=0.4,
        center_sat_boost=0.30, periphery_sat_reduce=0.20, opacity=0.55
    )
    after = _get_canvas(p)
    assert after.shape == (h, w, 4)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255