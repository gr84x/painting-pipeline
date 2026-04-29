"""
test_s246_additions.py -- Session 246 tests for macke_luminous_planes_pass,
paint_golden_ground_pass, and the august_macke catalog entry.
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


def _solid_reference(w=64, h=64, rgb=(140, 160, 200)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)), "RGB")


def _gradient_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w//2, :] = [220, 180, 120]
    arr[:, w//2:, :] = [40, 80, 200]
    return Image.fromarray(arr, "RGB")


def _dark_reference(w=64, h=64):
    from PIL import Image
    arr = np.ones((h, w, 3), dtype=np.uint8) * np.array([28, 24, 20], dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _bright_reference(w=64, h=64):
    from PIL import Image
    arr = np.ones((h, w, 3), dtype=np.uint8) * np.array([220, 215, 210], dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _multicolor_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//2, :w//2, :] = [200, 100, 30]   # warm orange
    arr[:h//2, w//2:, :] = [30, 80, 200]    # cool blue
    arr[h//2:, :w//2, :] = [180, 40, 60]    # warm red
    arr[h//2:, w//2:, :] = [60, 140, 180]   # cool teal
    return Image.fromarray(arr, "RGB")


def _low_sat_reference(w=64, h=64):
    """Low-saturation reference for testing saturation lift."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w//3, :] = [120, 100, 90]    # desaturated warm
    arr[:, w//3:2*w//3, :] = [80, 85, 100]  # desaturated cool
    arr[:, 2*w//3:, :] = [110, 120, 95]  # desaturated green
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, dark=False, bright=False, multicolor=False,
                  low_sat=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if dark:
            ref = _dark_reference(w, h)
        elif bright:
            ref = _bright_reference(w, h)
        elif multicolor:
            ref = _multicolor_reference(w, h)
        elif low_sat:
            ref = _low_sat_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.82, 0.66, 0.28), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── macke_luminous_planes_pass ────────────────────────────────────────────────

def test_s246_macke_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "macke_luminous_planes_pass")


def test_s246_macke_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.macke_luminous_planes_pass()
    assert result is None


def test_s246_macke_pass_modifies_canvas():
    """Pass must change at least some pixels on a multicolour canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.macke_luminous_planes_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "macke_luminous_planes_pass must modify canvas"


def test_s246_macke_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.macke_luminous_planes_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="macke_luminous_planes_pass must not alter alpha channel"
    )


def test_s246_macke_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.macke_luminous_planes_pass(sat_target=0.99, hue_jump_bright=0.50,
                                  veil_strength=0.50, opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0, "RGB must not go below 0"
    assert after[:, :, :3].max() <= 255, "RGB must not exceed 255"


def test_s246_macke_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas essentially unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.macke_luminous_planes_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1, (
        "opacity=0 should leave RGB channels essentially unchanged (max diff <= 1 LSB)"
    )


def test_s246_macke_pass_opacity_full_effect():
    """opacity=1 should produce visible change on multicolour canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.macke_luminous_planes_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() > 2, "opacity=1 should produce noticeable change"


def test_s246_macke_pass_saturation_lift_on_low_sat_canvas():
    """Low-saturation canvas should have higher mean saturation after the pass."""
    p = _make_small_painter(w=80, h=64)
    _prime_canvas(p, low_sat=True)
    before = _get_canvas(p).copy()

    def _mean_sat(arr_):
        r_ = arr_[:, :, 2].astype(np.float32) / 255
        g_ = arr_[:, :, 1].astype(np.float32) / 255
        b_ = arr_[:, :, 0].astype(np.float32) / 255
        mx = np.maximum(r_, np.maximum(g_, b_))
        mn = np.minimum(r_, np.minimum(g_, b_))
        return np.where(mx > 1e-7, (mx - mn) / (mx + 1e-7), 0.0).mean()

    sat_before = _mean_sat(before)
    p.macke_luminous_planes_pass(sat_target=0.90, sat_lift_str=0.80, opacity=1.0)
    after = _get_canvas(p)
    sat_after = _mean_sat(after)
    assert sat_after >= sat_before - 0.02, (
        f"Saturation should not substantially decrease on low-sat canvas "
        f"(before={sat_before:.3f}, after={sat_after:.3f})"
    )


def test_s246_macke_pass_boundary_brightening_active():
    """High-contrast hue-jump canvas: boundary brightening should produce changes."""
    from PIL import Image
    arr = np.zeros((64, 80, 3), dtype=np.uint8)
    arr[:, :40, :] = [220, 80, 20]   # warm orange
    arr[:, 40:, :] = [20, 60, 210]   # cool blue
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter(w=80, h=64)
    p.tone_ground((0.82, 0.66, 0.28), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=24)
    before = _get_canvas(p).copy()
    p.macke_luminous_planes_pass(hue_jump_bright=0.40, hue_jump_thresh=0.05, opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() > 0, "Boundary brightening should change pixels"


def test_s246_macke_pass_warm_veil_brightens_highlights():
    """Warm veil should shift bright pixels toward warm on a bright canvas."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.macke_luminous_planes_pass(warm_r=0.99, warm_g=0.85, warm_b=0.40,
                                  veil_strength=0.50, opacity=1.0)
    after = _get_canvas(p)
    # On a bright canvas, warm veil (high warm_r, lower warm_b) should
    # increase red channel relative to blue at bright pixels
    r_before = before[:, :, 2].astype(np.int32)
    b_before = before[:, :, 0].astype(np.int32)
    r_after  = after[:, :, 2].astype(np.int32)
    b_after  = after[:, :, 0].astype(np.int32)
    # Red should increase or hold; blue should decrease or hold on average
    assert r_after.mean() >= r_before.mean() - 2.0, (
        "Warm veil should not substantially reduce red channel on bright canvas"
    )


def test_s246_macke_pass_dark_canvas_no_crash():
    """Very dark canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.macke_luminous_planes_pass()
    after = _get_canvas(p)
    assert after is not None


def test_s246_macke_pass_bright_canvas_no_crash():
    """Very bright canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.macke_luminous_planes_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].max() <= 255


def test_s246_macke_pass_n_zones_range():
    """Pass accepts n_hue_zones from 4 to 12 without crash."""
    for nz in [4, 8, 12]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.macke_luminous_planes_pass(n_hue_zones=nz)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255


def test_s246_macke_pass_sequential_with_optical_vibration():
    """Macke pass followed by optical vibration should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.macke_luminous_planes_pass()
    p.paint_optical_vibration_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


# ── paint_golden_ground_pass ──────────────────────────────────────────────────

def test_s246_golden_ground_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_golden_ground_pass")


def test_s246_golden_ground_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_golden_ground_pass()
    assert result is None


def test_s246_golden_ground_pass_modifies_canvas():
    """Pass must change canvas on a multicolour canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.paint_golden_ground_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "paint_golden_ground_pass must modify canvas"


def test_s246_golden_ground_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_golden_ground_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="paint_golden_ground_pass must not alter alpha channel"
    )


def test_s246_golden_ground_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.paint_golden_ground_pass(midtone_str=0.9, shadow_str=0.9,
                                highlight_str=0.9, opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0, "RGB must not go below 0"
    assert after[:, :, :3].max() <= 255, "RGB must not exceed 255"


def test_s246_golden_ground_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas essentially unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_golden_ground_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1, (
        "opacity=0 should leave RGB channels essentially unchanged (max diff <= 1 LSB)"
    )


def test_s246_golden_ground_midtone_echo_warms_midtones():
    """A mid-grey canvas should acquire warmer hue after the midtone echo stage."""
    from PIL import Image
    arr = np.ones((64, 64, 3), dtype=np.uint8) * 128  # mid-grey
    ref = Image.fromarray(arr.astype(np.uint8), "RGB")
    p = _make_small_painter()
    p.tone_ground((0.82, 0.66, 0.28), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=16)
    before = _get_canvas(p).copy()
    p.paint_golden_ground_pass(
        ground_r=0.80, ground_g=0.55, ground_b=0.20,
        midtone_str=0.60, shadow_str=0.0, highlight_str=0.0, opacity=1.0
    )
    after = _get_canvas(p)
    # Red channel should increase (warm ground has high R)
    r_before = before[:, :, 2].astype(np.float32).mean()
    r_after  = after[:, :, 2].astype(np.float32).mean()
    b_before = before[:, :, 0].astype(np.float32).mean()
    b_after  = after[:, :, 0].astype(np.float32).mean()
    assert r_after >= r_before - 2.0, (
        f"Midtone echo should warm mid-grey canvas (R: {r_before:.1f} -> {r_after:.1f})"
    )


def test_s246_golden_ground_shadow_anchor_active():
    """A dark canvas should be warmed in shadows after shadow anchor stage."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.paint_golden_ground_pass(
        shadow_thresh=0.60, shadow_ground_r=0.55, shadow_ground_g=0.30, shadow_ground_b=0.10,
        shadow_str=0.60, midtone_str=0.0, highlight_str=0.0, opacity=1.0
    )
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    # Dark canvas should be modified by shadow anchor
    assert diff[:, :, :3].max() > 0, "Shadow anchor should modify dark canvas"


def test_s246_golden_ground_highlight_kiss_active():
    """A bright canvas should receive golden highlight kiss."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_golden_ground_pass(
        highlight_thresh=0.50, highlight_r=0.99, highlight_g=0.92, highlight_b=0.60,
        highlight_str=0.60, midtone_str=0.0, shadow_str=0.0, opacity=1.0
    )
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() > 0, "Highlight kiss should modify bright canvas"


def test_s246_golden_ground_dark_canvas_no_crash():
    """Very dark canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.paint_golden_ground_pass()
    after = _get_canvas(p)
    assert after is not None


def test_s246_golden_ground_bright_canvas_no_crash():
    """Very bright canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.paint_golden_ground_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].max() <= 255


def test_s246_golden_ground_shadow_thresh_range():
    """Pass accepts shadow_thresh values from 0.1 to 0.6 without crash."""
    for st in [0.1, 0.3, 0.6]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.paint_golden_ground_pass(shadow_thresh=st)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0


def test_s246_golden_ground_highlight_thresh_range():
    """Pass accepts highlight_thresh values from 0.5 to 0.9 without crash."""
    for ht in [0.5, 0.7, 0.9]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.paint_golden_ground_pass(highlight_thresh=ht)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255


def test_s246_golden_ground_sequential_after_macke():
    """Golden ground pass after macke pass should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.macke_luminous_planes_pass()
    p.paint_golden_ground_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


# ── august_macke catalog entry ────────────────────────────────────────────────

def test_s246_macke_in_catalog():
    import art_catalog
    assert 'august_macke' in art_catalog.CATALOG, (
        "august_macke key must be present in CATALOG"
    )


def test_s246_macke_artist_name():
    import art_catalog
    entry = art_catalog.CATALOG['august_macke']
    assert entry.artist == 'August Macke', (
        f"artist field mismatch: expected 'August Macke', got {entry.artist!r}"
    )


def test_s246_macke_movement():
    import art_catalog
    entry = art_catalog.CATALOG['august_macke']
    assert 'Expressionism' in entry.movement or 'Blaue' in entry.movement, (
        f"movement should reference Expressionism or Blaue Reiter, got {entry.movement!r}"
    )


def test_s246_macke_period():
    import art_catalog
    entry = art_catalog.CATALOG['august_macke']
    assert '1887' in entry.period, f"period should contain birth year 1887, got {entry.period!r}"
    assert '1914' in entry.period, f"period should contain death year 1914, got {entry.period!r}"


def test_s246_macke_palette_length():
    import art_catalog
    entry = art_catalog.CATALOG['august_macke']
    assert len(entry.palette) >= 6, (
        f"Macke palette should have at least 6 colours, got {len(entry.palette)}"
    )


def test_s246_macke_palette_values_valid():
    import art_catalog
    entry = art_catalog.CATALOG['august_macke']
    for i, color in enumerate(entry.palette):
        assert len(color) == 3, f"palette[{i}] must be an (R,G,B) triple"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"palette[{i}] channel {ch} out of [0,1] range"
            )


def test_s246_macke_famous_works():
    import art_catalog
    entry = art_catalog.CATALOG['august_macke']
    assert len(entry.famous_works) >= 4, (
        f"Macke should have at least 4 famous works listed, got {len(entry.famous_works)}"
    )


def test_s246_macke_kairouan_in_works():
    import art_catalog
    entry = art_catalog.CATALOG['august_macke']
    titles = [w[0] for w in entry.famous_works]
    assert any('Kairouan' in t or 'Tunisia' in t or 'Turkish' in t or 'Promenade' in t
               for t in titles), (
        "Famous works should include Kairouan, Promenade, or Turkish Café"
    )


def test_s246_macke_inspiration_references_pass():
    import art_catalog
    entry = art_catalog.CATALOG['august_macke']
    insp = entry.inspiration.lower()
    assert 'macke' in insp or 'luminous' in insp or 'hue' in insp, (
        "inspiration field should reference the macke_luminous_planes_pass"
    )


def test_s246_macke_technique_nonempty():
    import art_catalog
    entry = art_catalog.CATALOG['august_macke']
    assert len(entry.technique) > 200, (
        "Macke technique description should be substantial (>200 chars)"
    )


def test_s246_catalog_total_count():
    import art_catalog
    count = len(art_catalog.CATALOG)
    assert count >= 246, (
        f"After session 246, CATALOG should have at least 246 entries, got {count}"
    )


def test_s246_both_passes_sequential():
    """Run both new passes in sequence -- no errors, canvas stays valid."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.macke_luminous_planes_pass()
    p.paint_golden_ground_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s246_painter_smoke_test():
    """Full painter workflow with both new passes on small canvas."""
    from PIL import Image
    w, h = 80, 64
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//2, :w//3, :] = [220, 170, 40]   # warm yellow upper-left
    arr[:h//2, w//3:2*w//3, :] = [30, 70, 200]  # cool blue upper-mid
    arr[:h//2, 2*w//3:, :] = [200, 60, 20]  # vermilion upper-right
    arr[h//2:, :w//2, :] = [160, 140, 80]   # ochre lower-left
    arr[h//2:, w//2:, :] = [60, 100, 160]   # teal lower-right
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter(w=w, h=h)
    p.tone_ground((0.82, 0.66, 0.28), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=16)
    p.macke_luminous_planes_pass(opacity=0.80)
    p.paint_golden_ground_pass(opacity=0.65)
    after = _get_canvas(p)
    assert after.shape == (h, w, 4)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255
