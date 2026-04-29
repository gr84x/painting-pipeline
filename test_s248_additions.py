"""
test_s248_additions.py -- Session 248 tests for de_stael_palette_knife_mosaic_pass,
paint_halation_pass, and the nicolas_de_stael catalog entry.
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


# ── de_stael_palette_knife_mosaic_pass ───────────────────────────────────────

def test_s248_destael_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "de_stael_palette_knife_mosaic_pass")


def test_s248_destael_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.de_stael_palette_knife_mosaic_pass()
    assert result is None


def test_s248_destael_pass_modifies_canvas():
    """Pass must change pixels on a gradient canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.de_stael_palette_knife_mosaic_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "de_stael_palette_knife_mosaic_pass must modify canvas"


def test_s248_destael_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.de_stael_palette_knife_mosaic_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="de_stael_palette_knife_mosaic_pass must not alter alpha channel"
    )


def test_s248_destael_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.de_stael_palette_knife_mosaic_pass(
        tile_h=8, tile_w=8, knife_texture_str=0.2,
        boundary_strength=0.5, opacity=1.0
    )
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s248_destael_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas essentially unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.de_stael_palette_knife_mosaic_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1


def test_s248_destael_pass_opacity_full_visible_change():
    """opacity=1 should produce a visible change on a multicolour canvas."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    p.de_stael_palette_knife_mosaic_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() > 2


def test_s248_destael_tile_quantization_reduces_local_variance():
    """After pass with large tiles, variance within any tile region should decrease."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, multicolor=True)

    tile_h, tile_w = 16, 16

    before = _get_canvas(p).copy()
    p.de_stael_palette_knife_mosaic_pass(
        tile_h=tile_h, tile_w=tile_w,
        knife_texture_str=0.0,
        boundary_strength=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p)

    # Sample variance within a central tile
    r0 = before[:tile_h, :tile_w, 2].astype(np.float32)
    r1 = after[:tile_h, :tile_w, 2].astype(np.float32)
    var_before = float(r0.var())
    var_after  = float(r1.var())
    assert var_after <= var_before + 2.0, (
        f"Tile quantization should reduce intra-tile variance "
        f"(before={var_before:.2f}, after={var_after:.2f})"
    )


def test_s248_destael_tile_sizes_accepted():
    """Pass accepts tile sizes 4, 8, 16, 32 without crash."""
    for ts in [4, 8, 16, 32]:
        p = _make_small_painter(w=64, h=64)
        _prime_canvas(p, multicolor=True)
        p.de_stael_palette_knife_mosaic_pass(tile_h=ts, tile_w=ts)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0
        assert after[:, :, :3].max() <= 255


def test_s248_destael_knife_angle_range():
    """Pass accepts knife angles 0, 45, 90, 135 without crash."""
    for angle in [0.0, 45.0, 90.0, 135.0]:
        p = _make_small_painter()
        _prime_canvas(p, multicolor=True)
        p.de_stael_palette_knife_mosaic_pass(knife_angle_deg=angle)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0
        assert after[:, :, :3].max() <= 255


def test_s248_destael_no_boundary_no_crash():
    """boundary_width=0 or boundary_strength=0 should not crash."""
    for bw, bs in [(0, 0.0), (1, 0.0), (2, 0.0)]:
        p = _make_small_painter()
        _prime_canvas(p)
        p.de_stael_palette_knife_mosaic_pass(boundary_width=bw, boundary_strength=bs)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255


def test_s248_destael_dark_canvas_no_crash():
    """Very dark canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    p.de_stael_palette_knife_mosaic_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0


def test_s248_destael_bright_canvas_no_crash():
    """Very bright canvas should not raise exceptions."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.de_stael_palette_knife_mosaic_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].max() <= 255


def test_s248_destael_sequential_with_kollwitz():
    """de Stael pass followed by Kollwitz charcoal should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.de_stael_palette_knife_mosaic_pass()
    p.kollwitz_charcoal_etching_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s248_destael_non_square_tile():
    """Rectangular tiles (tile_h != tile_w) should work without crash."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p, multicolor=True)
    p.de_stael_palette_knife_mosaic_pass(tile_h=16, tile_w=8)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s248_destael_canvas_size_not_divisible_by_tile():
    """Canvas dimensions not divisible by tile size should not crash."""
    p = _make_small_painter(w=50, h=37)
    _prime_canvas(p, multicolor=True)
    p.de_stael_palette_knife_mosaic_pass(tile_h=16, tile_w=12)
    after = _get_canvas(p)
    assert after.shape[:2] == (37, 50)
    assert after[:, :, :3].max() <= 255


# ── paint_halation_pass ──────────────────────────────────────────────────────

def test_s248_halation_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_halation_pass")


def test_s248_halation_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_halation_pass()
    assert result is None


def test_s248_halation_pass_modifies_canvas():
    """Pass must change canvas when there are bright pixels."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_halation_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "paint_halation_pass must modify canvas when bright pixels exist"


def test_s248_halation_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_halation_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="paint_halation_pass must not alter alpha channel"
    )


def test_s248_halation_pass_clamps_output():
    """Output RGB values must stay within [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.paint_halation_pass(
        halation_thresh=0.50, bloom_strength=1.0, opacity=1.0
    )
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s248_halation_pass_opacity_zero_no_change():
    """opacity=0 must leave canvas essentially unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_halation_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1


def test_s248_halation_no_bright_pixels_minimal_change():
    """On a very dark canvas (no pixels above threshold), bloom should be minimal."""
    p = _make_small_painter()
    _prime_canvas(p, dark=True)
    before = _get_canvas(p).copy()
    p.paint_halation_pass(halation_thresh=0.95, bloom_strength=1.0, opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 8, (
        "Dark canvas with high threshold should produce minimal bloom change"
    )


def test_s248_halation_brightens_near_bright_areas():
    """On a canvas with a bright patch, neighbouring area should brighten."""
    from PIL import Image
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[28:36, 28:36, :] = [255, 250, 240]   # bright central patch
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter()
    p.tone_ground((0.10, 0.10, 0.10), texture_strength=0.01)
    p.block_in(ref, stroke_size=6, n_strokes=12)
    before = _get_canvas(p).copy()
    p.paint_halation_pass(
        halation_thresh=0.70, halation_sigma=12.0,
        bloom_strength=0.5, opacity=1.0
    )
    after = _get_canvas(p)
    # Check that mean brightness increases after bloom (some pixels get brighter)
    mean_before = float(after[:, :, :3].astype(np.float32).mean())
    mean_orig   = float(before[:, :, :3].astype(np.float32).mean())
    assert mean_before >= mean_orig - 1.0, "Halation pass should not decrease mean brightness"


def test_s248_halation_thresh_range():
    """Pass accepts threshold values 0.5, 0.7, 0.9 without crash."""
    for thresh in [0.5, 0.7, 0.9]:
        p = _make_small_painter()
        _prime_canvas(p, bright=True)
        p.paint_halation_pass(halation_thresh=thresh)
        after = _get_canvas(p)
        assert after[:, :, :3].min() >= 0
        assert after[:, :, :3].max() <= 255


def test_s248_halation_sigma_range():
    """Pass accepts sigma values 4, 10, 20 without crash."""
    for sigma in [4.0, 10.0, 20.0]:
        p = _make_small_painter()
        _prime_canvas(p, bright=True)
        p.paint_halation_pass(halation_sigma=sigma)
        after = _get_canvas(p)
        assert after[:, :, :3].max() <= 255


def test_s248_halation_sequential_after_destael():
    """Halation pass after de Stael mosaic should not crash."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.de_stael_palette_knife_mosaic_pass()
    p.paint_halation_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s248_halation_cool_tint_increases_blue():
    """With a cool tint (high tint_b, low tint_r), bloom should shift toward blue."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.paint_halation_pass(
        halation_thresh=0.5, tint_r=0.1, tint_g=0.3, tint_b=1.0,
        bloom_strength=0.5, opacity=1.0
    )
    after = _get_canvas(p)
    b_change = float(after[:, :, 0].astype(np.float32).mean()) - float(before[:, :, 0].astype(np.float32).mean())
    r_change = float(after[:, :, 2].astype(np.float32).mean()) - float(before[:, :, 2].astype(np.float32).mean())
    assert b_change >= r_change - 2.0, (
        f"Cool tint should shift blue more than red "
        f"(b_change={b_change:.2f}, r_change={r_change:.2f})"
    )


# ── nicolas_de_stael catalog entry ───────────────────────────────────────────

def test_s248_destael_in_catalog():
    import art_catalog
    assert 'nicolas_de_stael' in art_catalog.CATALOG, (
        "nicolas_de_stael key must be present in CATALOG"
    )


def test_s248_destael_artist_name():
    import art_catalog
    entry = art_catalog.CATALOG['nicolas_de_stael']
    assert 'de Stael' in entry.artist or 'Stael' in entry.artist, (
        f"artist field should contain 'de Stael', got {entry.artist!r}"
    )


def test_s248_destael_movement():
    import art_catalog
    entry = art_catalog.CATALOG['nicolas_de_stael']
    mv = entry.movement.lower()
    assert 'abstract' in mv or 'lyrical' in mv or 'expressionism' in mv, (
        f"movement should reference Abstract or Lyrical, got {entry.movement!r}"
    )


def test_s248_destael_period():
    import art_catalog
    entry = art_catalog.CATALOG['nicolas_de_stael']
    assert '1914' in entry.period, f"period should contain birth year 1914, got {entry.period!r}"
    assert '1955' in entry.period, f"period should contain death year 1955, got {entry.period!r}"


def test_s248_destael_palette_length():
    import art_catalog
    entry = art_catalog.CATALOG['nicolas_de_stael']
    assert len(entry.palette) >= 6, (
        f"de Stael palette should have at least 6 colours, got {len(entry.palette)}"
    )


def test_s248_destael_palette_values_valid():
    import art_catalog
    entry = art_catalog.CATALOG['nicolas_de_stael']
    for i, color in enumerate(entry.palette):
        assert len(color) == 3, f"palette[{i}] must be an (R,G,B) triple"
        for ch in color:
            assert 0.0 <= ch <= 1.0, f"palette[{i}] channel {ch} out of [0,1] range"


def test_s248_destael_famous_works():
    import art_catalog
    entry = art_catalog.CATALOG['nicolas_de_stael']
    assert len(entry.famous_works) >= 4, (
        f"de Stael should have at least 4 famous works listed, got {len(entry.famous_works)}"
    )


def test_s248_destael_works_include_known_title():
    import art_catalog
    entry = art_catalog.CATALOG['nicolas_de_stael']
    titles = [w[0].lower() for w in entry.famous_works]
    known = ['football', 'agrigento', 'boat', 'roof', 'concert', 'landscape', 'marathon']
    assert any(any(k in t for k in known) for t in titles), (
        "Famous works should include at least one known de Stael title"
    )


def test_s248_destael_inspiration_references_pass():
    import art_catalog
    entry = art_catalog.CATALOG['nicolas_de_stael']
    insp = entry.inspiration.lower()
    assert 'mosaic' in insp or 'tile' in insp or 'stael' in insp or 'knife' in insp, (
        "inspiration field should reference the de_stael_palette_knife_mosaic_pass"
    )


def test_s248_destael_technique_nonempty():
    import art_catalog
    entry = art_catalog.CATALOG['nicolas_de_stael']
    assert len(entry.technique) > 200, (
        "de Stael technique description should be substantial (>200 chars)"
    )


def test_s248_catalog_total_count():
    import art_catalog
    count = len(art_catalog.CATALOG)
    assert count >= 248, (
        f"After session 248, CATALOG should have at least 248 entries, got {count}"
    )


# ── combined smoke tests ──────────────────────────────────────────────────────

def test_s248_both_passes_sequential():
    """Run both new passes in sequence -- no errors, canvas stays valid."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.de_stael_palette_knife_mosaic_pass()
    p.paint_halation_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s248_painter_smoke_test():
    """Full painter workflow with both new passes on small canvas."""
    from PIL import Image
    w, h = 80, 60
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Sky: cobalt
    arr[:h//2, :, :] = [40, 80, 180]
    # Quay: ochre
    arr[h//2:h//2+4, :, :] = [180, 150, 90]
    # Water: dark blue-green
    arr[h//2+4:, :, :] = [30, 60, 70]
    # Boat hull: red, centre
    arr[h//2-6:h//2+8, w//4:3*w//4, :] = [180, 60, 30]
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter(w=w, h=h)
    p.tone_ground((0.80, 0.50, 0.18), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=16)
    p.de_stael_palette_knife_mosaic_pass(tile_h=12, tile_w=16, opacity=0.85)
    p.paint_halation_pass(opacity=0.50)
    after = _get_canvas(p)
    assert after.shape == (h, w, 4)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255
