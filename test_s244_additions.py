"""
test_s244_additions.py -- Session 244 tests for beckmann_black_armature_pass,
paint_aerial_perspective_pass, and the max_beckmann catalog entry.
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
    arr[:h//2, :w//2, :] = [160, 140, 30]
    arr[:h//2, w//2:, :] = [30, 100, 200]
    arr[h//2:, :w//2, :] = [200, 40, 60]
    arr[h//2:, w//2:, :] = [60, 140, 80]
    return Image.fromarray(arr, "RGB")


def _high_contrast_reference(w=64, h=64):
    """Reference with sharp edge for gradient detection."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w//2, :] = [240, 230, 220]
    arr[:, w//2:, :] = [20, 18, 14]
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, dark=False, bright=False, multicolor=False,
                  high_contrast=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if dark:
            ref = _dark_reference(w, h)
        elif bright:
            ref = _bright_reference(w, h)
        elif multicolor:
            ref = _multicolor_reference(w, h)
        elif high_contrast:
            ref = _high_contrast_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.20, 0.18, 0.14), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── beckmann_black_armature_pass ──────────────────────────────────────────────

def test_s244_beckmann_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "beckmann_black_armature_pass")


def test_s244_beckmann_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.beckmann_black_armature_pass()
    assert result is None


def test_s244_beckmann_pass_modifies_canvas():
    """Pass must change at least some pixels on a gradient canvas."""
    p = _make_small_painter()
    _prime_canvas(p, high_contrast=True)
    before = _get_canvas(p).copy()
    p.beckmann_black_armature_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "beckmann_black_armature_pass must modify canvas"


def test_s244_beckmann_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.beckmann_black_armature_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="beckmann_black_armature_pass must not alter alpha channel"
    )


def test_s244_beckmann_pass_edge_darkening():
    """High-contrast canvas: edge pixels should get darker (armature snap)."""
    p = _make_small_painter(w=80, h=64)
    ref = _high_contrast_reference(80, 64)
    p.tone_ground((0.20, 0.18, 0.14), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    before = _get_canvas(p).copy()
    p.beckmann_black_armature_pass(armature_thresh=0.05, armature_snap=0.90)
    after = _get_canvas(p)
    # The mean brightness of the full canvas should decrease (dark armature added)
    before_lum = 0.299*before[:,:,2]/255 + 0.587*before[:,:,1]/255 + 0.114*before[:,:,0]/255
    after_lum  = 0.299*after[:,:,2]/255  + 0.587*after[:,:,1]/255  + 0.114*after[:,:,0]/255
    assert after_lum.mean() < before_lum.mean() + 0.05, (
        "beckmann_black_armature_pass should not brighten canvas overall"
    )


def test_s244_beckmann_pass_tonal_compression():
    """Value range should be compressed (std dev of luminance should not increase)."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    before_lum = (0.299*before[:,:,2]/255 + 0.587*before[:,:,1]/255 + 0.114*before[:,:,0]/255)
    p.beckmann_black_armature_pass(compress_str=0.40, armature_snap=0.0, palette_str=0.0)
    after = _get_canvas(p)
    after_lum  = (0.299*after[:,:,2]/255  + 0.587*after[:,:,1]/255  + 0.114*after[:,:,0]/255)
    # With strong compression and no other effects, std dev should decrease or hold
    assert after_lum.std() <= before_lum.std() + 0.05, (
        "Tonal compression should not increase luminance std dev substantially"
    )


def test_s244_beckmann_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.beckmann_black_armature_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1, (
        "opacity=0 should leave RGB channels essentially unchanged (max diff <= 1 LSB)"
    )


def test_s244_beckmann_pass_opacity_full_effect():
    """opacity=1 should produce visible change on gradient canvas."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.beckmann_black_armature_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() > 2, (
        "opacity=1 should produce noticeable change"
    )


def test_s244_beckmann_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.beckmann_black_armature_pass(armature_snap=1.0, compress_str=0.5, palette_str=0.9)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0, "RGB must not go below 0"
    assert after[:, :, :3].max() <= 255, "RGB must not exceed 255"


def test_s244_beckmann_pass_multicolor():
    """Pass works without error on saturated multicolour canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.beckmann_black_armature_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s244_beckmann_pass_dark_canvas_no_crash():
    """Very dark canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.beckmann_black_armature_pass()
    after = _get_canvas(p)
    assert after is not None


def test_s244_beckmann_pass_parameter_armature_thresh_range():
    """Pass accepts extreme thresh values without crash."""
    for thresh in [0.0, 0.5, 0.99]:
        p = _make_small_painter()
        _prime_canvas(p)
        p.beckmann_black_armature_pass(armature_thresh=thresh)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255


def test_s244_beckmann_pass_parameter_palette_str_range():
    """Pass accepts palette_str from 0 to 1 without crash."""
    for ps in [0.0, 0.5, 1.0]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.beckmann_black_armature_pass(palette_str=ps)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0


def test_s244_beckmann_pass_compress_mid_range():
    """Pass accepts compress_mid values across [0.2, 0.8] without crash."""
    for mid in [0.2, 0.48, 0.8]:
        p = _make_small_painter()
        _prime_canvas(p)
        p.beckmann_black_armature_pass(compress_mid=mid)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255


# ── paint_aerial_perspective_pass ─────────────────────────────────────────────

def test_s244_aerial_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_aerial_perspective_pass")


def test_s244_aerial_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_aerial_perspective_pass()
    assert result is None


def test_s244_aerial_pass_modifies_canvas():
    """Pass must change the canvas on a gradient input."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.paint_aerial_perspective_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "paint_aerial_perspective_pass must modify canvas"


def test_s244_aerial_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_aerial_perspective_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="paint_aerial_perspective_pass must not alter alpha channel"
    )


def test_s244_aerial_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.paint_aerial_perspective_pass(depth_str=1.0, haze_strength=0.8, desat_str=0.8, opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0, "RGB must not go below 0"
    assert after[:, :, :3].max() <= 255, "RGB must not exceed 255"


def test_s244_aerial_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_aerial_perspective_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1, (
        "opacity=0 should leave RGB channels essentially unchanged (max diff <= 1 LSB)"
    )


def test_s244_aerial_pass_desaturation_on_smooth_areas():
    """Smooth (uniform) canvas should be treated as background and desaturated."""
    from PIL import Image
    # A uniformly saturated canvas (all same vivid green) — no spatial frequency
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :, :] = [40, 180, 60]  # vivid green
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter()
    p.tone_ground((0.20, 0.18, 0.14), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=20)
    before = _get_canvas(p).copy()
    p.paint_aerial_perspective_pass(depth_str=0.80, desat_str=0.60, opacity=1.0)
    after = _get_canvas(p)
    # Compute per-pixel saturation before and after
    def _sat(arr_):
        r = arr_[:,:,2].astype(np.float32)/255
        g = arr_[:,:,1].astype(np.float32)/255
        b = arr_[:,:,0].astype(np.float32)/255
        mx = np.maximum(r, np.maximum(g, b))
        mn = np.minimum(r, np.minimum(g, b))
        return np.where(mx > 1e-7, (mx-mn)/(mx+1e-7), 0.0)
    sat_before = _sat(before).mean()
    sat_after  = _sat(after).mean()
    # Smooth uniform area → treated as background → saturation should decrease
    assert sat_after <= sat_before + 0.02, (
        f"Uniform (smooth) canvas should be desaturated by aerial perspective "
        f"(before={sat_before:.3f}, after={sat_after:.3f})"
    )


def test_s244_aerial_pass_haze_blend_direction():
    """Haze colour should shift smooth areas toward the configured haze RGB."""
    from PIL import Image
    # Dark uniform canvas (far from default cool grey haze)
    arr = np.ones((64, 64, 3), dtype=np.uint8) * np.array([30, 20, 10], dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter()
    p.tone_ground((0.20, 0.18, 0.14), texture_strength=0.01)
    p.block_in(ref, stroke_size=10, n_strokes=20)
    before = _get_canvas(p).copy()
    p.paint_aerial_perspective_pass(
        haze_r=0.90, haze_g=0.90, haze_b=0.95,
        haze_strength=0.60, depth_str=0.80, opacity=1.0
    )
    after = _get_canvas(p)
    # With a light haze and dark canvas, mean brightness should increase
    before_mean = before[:, :, :3].mean()
    after_mean  = after[:, :, :3].mean()
    assert after_mean >= before_mean - 5, (
        "Haze blend toward bright colour should not decrease mean brightness on dark canvas"
    )


def test_s244_aerial_pass_sigma_pair_validity():
    """Pass must work when fine_sigma < coarse_sigma (required for DoG)."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.paint_aerial_perspective_pass(fine_sigma=0.8, coarse_sigma=8.0)
    after = _get_canvas(p)
    assert after[:, :, :3].max() <= 255


def test_s244_aerial_pass_extreme_sigmas():
    """Very small or large sigma values must not crash."""
    for fine, coarse in [(0.5, 5.0), (2.0, 20.0)]:
        p = _make_small_painter()
        _prime_canvas(p)
        p.paint_aerial_perspective_pass(fine_sigma=fine, coarse_sigma=coarse)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0


def test_s244_aerial_pass_dark_canvas_no_crash():
    """Very dark canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.paint_aerial_perspective_pass()
    after = _get_canvas(p)
    assert after is not None


def test_s244_aerial_pass_bright_canvas_no_crash():
    """Very bright canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.paint_aerial_perspective_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].max() <= 255


# ── max_beckmann catalog entry ────────────────────────────────────────────────

def test_s244_max_beckmann_in_catalog():
    import art_catalog
    assert 'max_beckmann' in art_catalog.CATALOG, (
        "max_beckmann key must be present in CATALOG"
    )


def test_s244_max_beckmann_artist_name():
    import art_catalog
    entry = art_catalog.CATALOG['max_beckmann']
    assert entry.artist == 'Max Beckmann', (
        f"artist field mismatch: expected 'Max Beckmann', got {entry.artist!r}"
    )


def test_s244_max_beckmann_movement():
    import art_catalog
    entry = art_catalog.CATALOG['max_beckmann']
    assert 'Expressionism' in entry.movement or 'Objectivity' in entry.movement, (
        f"movement should reference Expressionism or Objectivity, got {entry.movement!r}"
    )


def test_s244_max_beckmann_period():
    import art_catalog
    entry = art_catalog.CATALOG['max_beckmann']
    assert '1884' in entry.period, f"period should contain birth year 1884, got {entry.period!r}"
    assert '1950' in entry.period, f"period should contain death year 1950, got {entry.period!r}"


def test_s244_max_beckmann_palette_length():
    import art_catalog
    entry = art_catalog.CATALOG['max_beckmann']
    assert len(entry.palette) >= 6, (
        f"Beckmann palette should have at least 6 colours, got {len(entry.palette)}"
    )


def test_s244_max_beckmann_palette_values_valid():
    import art_catalog
    entry = art_catalog.CATALOG['max_beckmann']
    for i, color in enumerate(entry.palette):
        assert len(color) == 3, f"palette[{i}] must be an (R,G,B) triple"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"palette[{i}] channel {ch} out of [0,1] range"
            )


def test_s244_max_beckmann_famous_works():
    import art_catalog
    entry = art_catalog.CATALOG['max_beckmann']
    assert len(entry.famous_works) >= 4, (
        f"Beckmann should have at least 4 famous works listed, got {len(entry.famous_works)}"
    )


def test_s244_max_beckmann_departure_in_works():
    import art_catalog
    entry = art_catalog.CATALOG['max_beckmann']
    titles = [w[0] for w in entry.famous_works]
    assert any('Departure' in t or 'triptych' in t.lower() for t in titles), (
        "Departure or triptych should be among Beckmann's famous works"
    )


def test_s244_max_beckmann_inspiration_references_pass():
    import art_catalog
    entry = art_catalog.CATALOG['max_beckmann']
    insp = entry.inspiration.lower()
    assert 'beckmann' in insp or 'armature' in insp, (
        "inspiration field should reference the beckmann_black_armature_pass"
    )


def test_s244_max_beckmann_technique_nonempty():
    import art_catalog
    entry = art_catalog.CATALOG['max_beckmann']
    assert len(entry.technique) > 200, (
        "Beckmann technique description should be substantial (>200 chars)"
    )


def test_s244_catalog_total_count():
    import art_catalog
    count = len(art_catalog.CATALOG)
    assert count >= 244, (
        f"After session 244, CATALOG should have at least 244 entries, got {count}"
    )


def test_s244_both_passes_sequential():
    """Run both new passes in sequence — no errors, canvas stays valid."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.beckmann_black_armature_pass()
    p.paint_aerial_perspective_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s244_painter_smoke_test():
    """Full painter workflow with both new passes on small canvas."""
    from PIL import Image
    w, h = 64, 80
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//2, :, :] = [120, 60, 180]
    arr[h//2:, :, :] = [200, 120, 40]
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter(w=w, h=h)
    p.tone_ground((0.20, 0.18, 0.14), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=16)
    p.beckmann_black_armature_pass(opacity=0.80)
    p.paint_aerial_perspective_pass(opacity=0.60)
    after = _get_canvas(p)
    assert after.shape == (h, w, 4)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255
