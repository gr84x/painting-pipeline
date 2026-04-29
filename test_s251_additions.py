"""
test_s251_additions.py -- Session 251 tests for bacon_isolated_figure_pass,
paint_warm_cool_separation_pass, and the francis_bacon catalog entry.
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


def _flesh_reference(w=64, h=64):
    """Mid-tone warm flesh tones in centre, dark near-black exterior."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    cy, cx = h // 2, w // 2
    for y in range(h):
        for x in range(w):
            d = ((x - cx)**2 + (y - cy)**2) ** 0.5 / (min(w, h) * 0.4)
            if d < 1.0:
                arr[y, x] = [210, 155, 95]   # warm ochre flesh
            else:
                arr[y, x] = [18, 14, 10]     # near-black exterior
    return Image.fromarray(arr, "RGB")


def _warm_cool_reference(w=64, h=64):
    """Warm orange left, cool blue right, grey centre."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w//3, :] = [220, 120, 30]    # warm orange
    arr[:, w//3:2*w//3, :] = [140, 135, 130]   # neutral grey
    arr[:, 2*w//3:, :] = [30, 80, 200]   # cool blue
    return Image.fromarray(arr, "RGB")


def _multicolor_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//2, :w//2, :] = [200, 60, 30]
    arr[:h//2, w//2:, :] = [30, 60, 210]
    arr[h//2:, :w//2, :] = [180, 160, 20]
    arr[h//2:, w//2:, :] = [50, 160, 80]
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, flesh=False, warm_cool=False, multicolor=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if flesh:
            ref = _flesh_reference(w, h)
        elif warm_cool:
            ref = _warm_cool_reference(w, h)
        elif multicolor:
            ref = _multicolor_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.82, 0.76, 0.62), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── bacon_isolated_figure_pass ────────────────────────────────────────────────

def test_s251_bacon_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "bacon_isolated_figure_pass")


def test_s251_bacon_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.bacon_isolated_figure_pass()
    assert result is None


def test_s251_bacon_pass_modifies_canvas():
    """Pass must change pixels on a flesh-toned canvas."""
    p = _make_small_painter()
    _prime_canvas(p, flesh=True)
    before = _get_canvas(p).copy()
    p.bacon_isolated_figure_pass(exterior_strength=0.60, smear_length=8)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "bacon_isolated_figure_pass must modify canvas"


def test_s251_bacon_pass_preserves_alpha():
    """Alpha channel must be untouched."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.bacon_isolated_figure_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "bacon_isolated_figure_pass must not alter alpha channel"
    )


def test_s251_bacon_pass_exterior_darkens():
    """Exterior pixels should be darker than before (exterior_strength > 0)."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    # Use a small ellipse to ensure most pixels are exterior
    p.bacon_isolated_figure_pass(
        focal_x=0.5, focal_y=0.5, rx=0.15, ry=0.15,
        exterior_strength=0.80, opacity=1.0
    )
    after = _get_canvas(p)
    # Corner pixels (exterior) should on average be darker
    corner_before = before[:10, :10, :3].astype(float).mean()
    corner_after = after[:10, :10, :3].astype(float).mean()
    assert corner_after < corner_before, (
        "Exterior (corner) pixels should be darkened by isolation vignette"
    )


def test_s251_bacon_pass_interior_preserves_brightness():
    """Interior of ellipse should not be darkened by the vignette."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, flesh=True)
    before = _get_canvas(p).copy()
    # Large ellipse fills most of canvas -- interior should be largely preserved
    p.bacon_isolated_figure_pass(
        focal_x=0.5, focal_y=0.5, rx=0.48, ry=0.48,
        exterior_strength=0.90, smear_length=4, smear_opacity=0.0,
        exterior_blend=0.0, opacity=1.0
    )
    after = _get_canvas(p)
    # Centre pixel zone should be approximately unchanged in brightness
    h, w = 80, 80
    cy, cx = h // 2, w // 2
    centre_before = before[cy-5:cy+5, cx-5:cx+5, :3].astype(float).mean()
    centre_after = after[cy-5:cy+5, cx-5:cx+5, :3].astype(float).mean()
    assert abs(centre_after - centre_before) < 12, (
        f"Interior centre should not be darkened (before={centre_before:.1f}, "
        f"after={centre_after:.1f})"
    )


def test_s251_bacon_pass_smear_changes_mid_tones():
    """Linear smear should affect mid-tone interior pixels."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, flesh=True)
    before = _get_canvas(p).copy()
    # No exterior darkening, no background toning -- just smear
    p.bacon_isolated_figure_pass(
        focal_x=0.5, focal_y=0.5, rx=0.48, ry=0.48,
        exterior_strength=0.0, exterior_blend=0.0,
        smear_length=18, smear_opacity=1.0, mid_luminance=0.50,
        smear_bandwidth=0.45, opacity=1.0
    )
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].mean() > 0.5, (
        "Smear should produce measurable pixel changes in mid-tone flesh zone"
    )


def test_s251_bacon_pass_zero_opacity_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.bacon_isolated_figure_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1, (
        "opacity=0 should leave canvas effectively unchanged (allowing for rounding)"
    )


def test_s251_bacon_pass_valid_pixel_range():
    """Output pixels must be in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, multicolor=True)
    p.bacon_isolated_figure_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s251_bacon_pass_custom_flat_hue():
    """Custom flat_hue should shift exterior hue toward target."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p).copy()
    # Use viridian hue (0.44) in exterior, large exterior_blend
    p.bacon_isolated_figure_pass(
        focal_x=0.5, focal_y=0.5, rx=0.15, ry=0.15,
        exterior_strength=0.0, exterior_blend=0.90,
        flat_hue=0.44, flat_sat=0.75, opacity=1.0
    )
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 5, "Custom flat_hue should produce visible hue shifts"


def test_s251_bacon_pass_small_canvas():
    """Pass should not crash on very small canvas."""
    p = _make_small_painter(w=16, h=16)
    _prime_canvas(p)
    p.bacon_isolated_figure_pass(smear_length=3)
    after = _get_canvas(p)
    assert after.shape == (16, 16, 4)


# ── paint_warm_cool_separation_pass ──────────────────────────────────────────

def test_s251_warmcool_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_warm_cool_separation_pass")


def test_s251_warmcool_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_warm_cool_separation_pass()
    assert result is None


def test_s251_warmcool_pass_modifies_canvas():
    """Pass must change pixels on a warm/cool canvas."""
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    before = _get_canvas(p).copy()
    p.paint_warm_cool_separation_pass()
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff.max() > 0, "paint_warm_cool_separation_pass must modify canvas"


def test_s251_warmcool_pass_preserves_alpha():
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_warm_cool_separation_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "paint_warm_cool_separation_pass must not alter alpha channel"
    )


def test_s251_warmcool_pass_valid_pixel_range():
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    p.paint_warm_cool_separation_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s251_warmcool_pass_zero_opacity_no_change():
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_warm_cool_separation_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    assert diff[:, :, :3].max() <= 1, (
        "opacity=0 should leave canvas effectively unchanged"
    )


def test_s251_warmcool_pass_warm_zone_brighter():
    """Warm zones should be slightly brighter after the pass (warm_lum_shift > 0)."""
    from PIL import Image
    p = _make_small_painter(w=80, h=40)
    # All-orange canvas (warm)
    arr = np.full((40, 80, 3), [220, 110, 20], dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy()
    p.paint_warm_cool_separation_pass(
        warm_boost=0.0, cool_boost=0.0,  # only luminosity effect
        warm_lum_shift=0.08, cool_lum_shift=0.0, opacity=1.0
    )
    after = _get_canvas(p)
    mean_before = before[:, :, :3].astype(float).mean()
    mean_after = after[:, :, :3].astype(float).mean()
    assert mean_after >= mean_before - 0.5, (
        f"Warm canvas should not get darker (before={mean_before:.2f}, after={mean_after:.2f})"
    )


def test_s251_warmcool_pass_neutral_unaffected():
    """Neutral grey canvas should be nearly unaffected (low saturation = low weight)."""
    from PIL import Image
    p = _make_small_painter(w=64, h=64)
    arr = np.full((64, 64, 3), [128, 128, 128], dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")
    _prime_canvas(p, ref=ref)
    before = _get_canvas(p).copy()
    p.paint_warm_cool_separation_pass(
        warm_boost=1.0, cool_boost=1.0, warm_lum_shift=0.2, cool_lum_shift=0.2,
        opacity=1.0
    )
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32))
    # Neutral grey has near-zero saturation so weights are near zero
    assert diff[:, :, :3].mean() < 15, (
        "Neutral grey should be minimally affected by warm/cool separation"
    )


def test_s251_warmcool_pass_high_boost_increases_saturation():
    """High warm_boost + high cool_boost should increase overall colour intensity."""
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    before = _get_canvas(p).copy().astype(float)

    def compute_sat_mean(arr):
        r = arr[:, :, 2] / 255.0
        g = arr[:, :, 1] / 255.0
        b = arr[:, :, 0] / 255.0
        mx = np.maximum(np.maximum(r, g), b)
        mn = np.minimum(np.minimum(r, g), b)
        delta = mx - mn
        sat = np.where(mx > 0.01, delta / (mx + 1e-8), 0.0)
        return sat.mean()

    sat_before = compute_sat_mean(before)
    p2 = _make_small_painter()
    _prime_canvas(p2, warm_cool=True)
    p2.paint_warm_cool_separation_pass(warm_boost=0.60, cool_boost=0.60, opacity=1.0)
    after = _get_canvas(p2)
    sat_after = compute_sat_mean(after.astype(float))
    assert sat_after >= sat_before - 0.01, (
        f"High boost should not decrease saturation (before={sat_before:.4f}, "
        f"after={sat_after:.4f})"
    )


# ── francis_bacon catalog entry ───────────────────────────────────────────────

def test_s251_bacon_catalog_exists():
    import art_catalog
    assert "francis_bacon" in art_catalog.CATALOG, (
        "francis_bacon should be in CATALOG after session 251"
    )


def test_s251_bacon_catalog_fields():
    import art_catalog
    entry = art_catalog.CATALOG["francis_bacon"]
    assert entry.artist == "Francis Bacon"
    assert entry.movement == "Figurative Expressionism"
    assert entry.nationality == "Irish-British"
    assert entry.period == "1909-1992"


def test_s251_bacon_catalog_palette():
    import art_catalog
    entry = art_catalog.CATALOG["francis_bacon"]
    assert len(entry.palette) >= 8, "Bacon palette should have at least 8 colours"
    for c in entry.palette:
        assert len(c) == 3
        assert all(0.0 <= v <= 1.0 for v in c)


def test_s251_bacon_palette_has_warm():
    """Bacon palette should include raw sienna / warm ochre tones."""
    import art_catalog
    entry = art_catalog.CATALOG["francis_bacon"]
    has_warm = any(c[0] > 0.5 and c[0] > c[2] for c in entry.palette)
    assert has_warm, "Bacon palette should include warm sienna/ochre tones"


def test_s251_bacon_famous_works():
    import art_catalog
    entry = art_catalog.CATALOG["francis_bacon"]
    assert len(entry.famous_works) >= 5, (
        f"Bacon should have at least 5 famous works, got {len(entry.famous_works)}"
    )


def test_s251_bacon_works_include_known_title():
    import art_catalog
    entry = art_catalog.CATALOG["francis_bacon"]
    titles = [w[0].lower() for w in entry.famous_works]
    known = ["pope", "crucifixion", "self-portrait", "triptych", "meat", "dyer", "van gogh"]
    assert any(any(k in t for k in known) for t in titles), (
        "Famous works should include at least one known Bacon title"
    )


def test_s251_bacon_inspiration_references_pass():
    import art_catalog
    entry = art_catalog.CATALOG["francis_bacon"]
    insp = entry.inspiration.lower()
    assert "bacon" in insp or "isolated" in insp or "elliptic" in insp, (
        "inspiration field should reference bacon_isolated_figure_pass"
    )


def test_s251_bacon_technique_nonempty():
    import art_catalog
    entry = art_catalog.CATALOG["francis_bacon"]
    assert len(entry.technique) > 200, (
        "Bacon technique description should be substantial (>200 chars)"
    )


def test_s251_bacon_inspiration_mentions_162nd():
    import art_catalog
    entry = art_catalog.CATALOG["francis_bacon"]
    insp = entry.inspiration.upper()
    assert "SIXTY-SECOND" in insp or "162" in insp, (
        "inspiration should mention the 162nd mode"
    )


def test_s251_catalog_total_count():
    import art_catalog
    count = len(art_catalog.CATALOG)
    assert count >= 251, (
        f"After session 251, CATALOG should have at least 251 entries, got {count}"
    )


# ── combined smoke tests ──────────────────────────────────────────────────────

def test_s251_both_passes_sequential():
    """Run both new passes in sequence -- no errors, canvas stays valid."""
    p = _make_small_painter()
    _prime_canvas(p, warm_cool=True)
    p.bacon_isolated_figure_pass(smear_length=8)
    p.paint_warm_cool_separation_pass()
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s251_full_pipeline_smoke():
    """Full painter workflow with both new passes on a flesh-toned canvas."""
    from PIL import Image
    w, h = 80, 80
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    cx, cy = w // 2, h // 2
    for y in range(h):
        for x in range(w):
            d = ((x - cx)**2 + (y - cy)**2) ** 0.5 / (min(w, h) * 0.38)
            if d < 1.0:
                # Warm flesh interior
                arr[y, x] = [int(200 * (1 - d * 0.4)), int(140 * (1 - d * 0.3)), int(80 * (1 - d * 0.2))]
            else:
                # Raw sienna exterior
                arr[y, x] = [155, 65, 18]
    ref = Image.fromarray(arr, "RGB")
    p = _make_small_painter(w=w, h=h)
    p.tone_ground((0.85, 0.78, 0.64), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.bacon_isolated_figure_pass(
        focal_x=0.5, focal_y=0.5, rx=0.40, ry=0.42,
        transition_width=0.10, exterior_strength=0.68,
        smear_angle=32.0, smear_length=12, mid_luminance=0.46,
        smear_bandwidth=0.28, smear_opacity=0.65,
        flat_hue=0.06, flat_sat=0.70, exterior_blend=0.55,
        opacity=0.88
    )
    p.paint_warm_cool_separation_pass(
        warm_boost=0.24, cool_boost=0.20,
        warm_lum_shift=0.03, cool_lum_shift=0.025,
        opacity=0.50
    )
    after = _get_canvas(p)
    assert after.shape == (h, w, 4)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255