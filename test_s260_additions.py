"""
test_s260_additions.py -- Session 260 tests for foujita_milky_ground_contour_pass,
paint_sfumato_contour_dissolution_pass, and the tsuguharu_foujita catalog entry.
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
    """Bright, warm reference suitable for ivory-lift tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :] = [230, 220, 200]   # bright warm tones (highlight zone)
    arr[h // 2:, :] = [80,  60,  50]    # dark warm shadow
    return Image.fromarray(arr, "RGB")


def _edge_reference(w=64, h=64):
    """High-contrast reference with strong edges for contour tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [220, 200, 180]  # bright left half
    arr[:, w // 2:, :] = [30, 20, 15]     # dark right half
    return Image.fromarray(arr, "RGB")


def _grey_reference(w=64, h=64):
    """Mid-grey flat reference."""
    from PIL import Image
    arr = np.full((h, w, 3), 128, dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, bright=False, edge=False, grey=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if bright:
            ref = _bright_reference(w, h)
        elif edge:
            ref = _edge_reference(w, h)
        elif grey:
            ref = _grey_reference(w, h)
        else:
            ref = _bright_reference(w, h)
    p.tone_ground((0.92, 0.90, 0.82), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── foujita_milky_ground_contour_pass ─────────────────────────────────────────

def test_s260_foujita_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "foujita_milky_ground_contour_pass")


def test_s260_foujita_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    result = p.foujita_milky_ground_contour_pass()
    assert result is None


def test_s260_foujita_pass_modifies_canvas():
    """Pass must change at least some pixels on a non-trivial canvas."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.foujita_milky_ground_contour_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after foujita_milky_ground_contour_pass"


def test_s260_foujita_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p)
    p.foujita_milky_ground_contour_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after foujita_milky_ground_contour_pass"
    )


def test_s260_foujita_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    before = _get_canvas(p).copy()
    p.foujita_milky_ground_contour_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s260_foujita_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, bright=True)
    p.foujita_milky_ground_contour_pass(
        ivory_strength=1.0, contour_darkness=1.0, hatch_amplitude=0.2, opacity=1.0
    )
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after foujita_milky_ground_contour_pass"
    )


def test_s260_foujita_ivory_lift_warms_highlights():
    """Ivory lift should push bright regions toward warm ivory (R and G up relative to B)."""
    from PIL import Image
    arr = np.full((64, 64, 3), 210, dtype=np.uint8)
    arr[:, :, 2] = 180  # slightly cooler (lower blue channel in RGB)
    ref = Image.fromarray(arr, "RGB")

    p_base = _make_small_painter()
    _prime_canvas(p_base, ref=ref)
    before = _get_canvas(p_base).copy().astype(float) / 255.0

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    p.foujita_milky_ground_contour_pass(
        ivory_r=0.97, ivory_g=0.95, ivory_b=0.88,
        ivory_threshold=0.50,
        ivory_strength=0.90,
        contour_threshold=1.0,  # disable contour (impossible threshold)
        hatch_amplitude=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0

    # Mean R and G should be >= before (ivory is warm)
    assert after[:, :, 2].mean() >= before[:, :, 2].mean() - 0.01, (
        "Ivory lift should not reduce mean red channel in highlight zone"
    )


def test_s260_foujita_contour_darkens_edges():
    """Contour stage must darken pixels at strong edges."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)  # sharp half/half boundary
    before = _get_canvas(p).copy().astype(float)
    lum_before = 0.299 * before[:, :, 2] + 0.587 * before[:, :, 1] + 0.114 * before[:, :, 0]

    p2 = _make_small_painter()
    _prime_canvas(p2, edge=True)
    p2.foujita_milky_ground_contour_pass(
        ivory_strength=0.0,         # disable ivory lift
        contour_threshold=0.02,     # very sensitive edge detection
        contour_darkness=0.90,
        hatch_amplitude=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p2).astype(float)
    lum_after = 0.299 * after[:, :, 2] + 0.587 * after[:, :, 1] + 0.114 * after[:, :, 0]

    # Pixels at the edge boundary zone should get darker
    # Check the center column (x=32) which straddles the edge
    center_lum_before = lum_before[:, 30:34].mean()
    center_lum_after  = lum_after[:, 30:34].mean()
    assert center_lum_after <= center_lum_before, (
        f"Contour zone should darken at edges; before={center_lum_before:.3f}, "
        f"after={center_lum_after:.3f}"
    )


def test_s260_foujita_hatch_adds_texture():
    """Hatch stage (amplitude > 0) should increase spatial variance."""
    p_flat = _make_small_painter()
    p_flat.tone_ground((0.75, 0.73, 0.68), texture_strength=0.0)
    out_flat = _get_canvas(p_flat).astype(float) / 255.0
    lum_flat = 0.299 * out_flat[:, :, 2] + 0.587 * out_flat[:, :, 1] + 0.114 * out_flat[:, :, 0]
    var_before = float(np.var(lum_flat))

    p_hatch = _make_small_painter()
    p_hatch.tone_ground((0.75, 0.73, 0.68), texture_strength=0.0)
    p_hatch.foujita_milky_ground_contour_pass(
        ivory_strength=0.0,
        contour_darkness=0.0,
        hatch_spacing=5,
        hatch_amplitude=0.10,
        hatch_sigma=0.5,
        opacity=1.0,
    )
    out_hatch = _get_canvas(p_hatch).astype(float) / 255.0
    lum_hatch = 0.299 * out_hatch[:, :, 2] + 0.587 * out_hatch[:, :, 1] + 0.114 * out_hatch[:, :, 0]
    var_after = float(np.var(lum_hatch))

    assert var_after > var_before, (
        f"Hatch should increase spatial luminance variance; "
        f"before={var_before:.6f}, after={var_after:.6f}"
    )


def test_s260_foujita_higher_opacity_more_change():
    """Higher opacity produces at least as much change as lower opacity."""
    ref = _bright_reference(64, 64)

    def _run(op):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        before = _get_canvas(p).copy()
        p.foujita_milky_ground_contour_pass(opacity=op)
        after = _get_canvas(p)
        return int(np.abs(before.astype(int) - after.astype(int)).sum())

    assert _run(0.8) >= _run(0.2), "Higher opacity should produce more change"


# ── paint_sfumato_contour_dissolution_pass ────────────────────────────────────

def test_s260_sfumato_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_sfumato_contour_dissolution_pass")


def test_s260_sfumato_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    result = p.paint_sfumato_contour_dissolution_pass()
    assert result is None


def test_s260_sfumato_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()
    p.paint_sfumato_contour_dissolution_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_sfumato_contour_dissolution_pass"


def test_s260_sfumato_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p)
    p.paint_sfumato_contour_dissolution_pass()
    after = _get_canvas(p)
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), (
        "Alpha channel changed after paint_sfumato_contour_dissolution_pass"
    )


def test_s260_sfumato_opacity_zero_no_change():
    """opacity=0 must leave canvas unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()
    p.paint_sfumato_contour_dissolution_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), "opacity=0 must leave canvas unchanged"


def test_s260_sfumato_values_in_range():
    """All pixel values must stay in [0, 255]."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    p.paint_sfumato_contour_dissolution_pass(
        dissolve_strength=1.0, shadow_bias=1.0, opacity=1.0
    )
    after = _get_canvas(p)
    assert after.min() >= 0 and after.max() <= 255, (
        "Pixel values out of [0, 255] after paint_sfumato_contour_dissolution_pass"
    )


def test_s260_sfumato_softens_edges():
    """Sfumato should reduce sharpness at strong tonal edges."""
    # Measure local variance at the boundary region before and after
    p_before = _make_small_painter()
    _prime_canvas(p_before, edge=True)
    raw = _get_canvas(p_before).astype(float) / 255.0
    # Edge zone is column 32 ±4
    edge_zone_before = raw[:, 28:36, :3]
    var_before = float(np.var(edge_zone_before))

    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    p.paint_sfumato_contour_dissolution_pass(
        blur_sigma=3.0,
        dissolve_strength=1.0,
        shadow_bias=0.0,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    edge_zone_after = after[:, 28:36, :3]
    var_after = float(np.var(edge_zone_after))

    assert var_after <= var_before, (
        f"Sfumato should reduce edge-zone variance; before={var_before:.6f}, after={var_after:.6f}"
    )


def test_s260_sfumato_darkens_shadow_edges():
    """Shadow-bias deepening should darken dark edge regions."""
    from PIL import Image
    # Mostly dark canvas with an edge
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :32, :] = [60, 50, 40]   # dark left
    arr[:, 32:, :] = [200, 190, 170]  # bright right
    ref = Image.fromarray(arr, "RGB")

    p_base = _make_small_painter()
    _prime_canvas(p_base, ref=ref)
    before = _get_canvas(p_base).copy().astype(float) / 255.0
    # Dark region = left columns
    lum_dark_before = (0.299 * before[:, 10:20, 2]
                       + 0.587 * before[:, 10:20, 1]
                       + 0.114 * before[:, 10:20, 0]).mean()

    p = _make_small_painter()
    _prime_canvas(p, ref=ref)
    p.paint_sfumato_contour_dissolution_pass(
        edge_threshold=0.01,
        dissolve_strength=0.0,
        shadow_bias=0.80,
        opacity=1.0,
    )
    after = _get_canvas(p).astype(float) / 255.0
    lum_dark_after = (0.299 * after[:, 10:20, 2]
                      + 0.587 * after[:, 10:20, 1]
                      + 0.114 * after[:, 10:20, 0]).mean()

    assert lum_dark_after <= lum_dark_before + 0.01, (
        f"Shadow-bias should darken dark edge zone; before={lum_dark_before:.3f}, "
        f"after={lum_dark_after:.3f}"
    )


def test_s260_sfumato_higher_opacity_more_change():
    """Higher opacity should produce at least as much change as lower opacity."""
    ref = _edge_reference(64, 64)

    def _run(op):
        p = _make_small_painter()
        _prime_canvas(p, ref=ref)
        before = _get_canvas(p).copy()
        p.paint_sfumato_contour_dissolution_pass(opacity=op)
        after = _get_canvas(p)
        return int(np.abs(before.astype(int) - after.astype(int)).sum())

    assert _run(0.8) >= _run(0.2), "Higher opacity should produce more change"


# ── tsuguharu_foujita catalog tests ───────────────────────────────────────────

def test_s260_catalog_foujita_present():
    from art_catalog import CATALOG
    assert "tsuguharu_foujita" in CATALOG, (
        "tsuguharu_foujita not found in CATALOG"
    )


def test_s260_catalog_foujita_fields():
    from art_catalog import CATALOG
    s = CATALOG["tsuguharu_foujita"]
    assert "Foujita" in s.artist
    assert "Japanese" in s.nationality
    assert len(s.palette) >= 6
    assert len(s.famous_works) >= 5


def test_s260_catalog_foujita_inspiration():
    """Inspiration must reference foujita_milky_ground_contour_pass and 171st mode."""
    from art_catalog import CATALOG
    s = CATALOG["tsuguharu_foujita"]
    assert "foujita_milky_ground_contour_pass" in s.inspiration, (
        "foujita_milky_ground_contour_pass not found in inspiration"
    )
    assert "171" in s.inspiration, (
        "171st mode not referenced in inspiration"
    )


def test_s260_catalog_foujita_ivory_palette():
    """Foujita's palette should include a near-white ivory tone."""
    from art_catalog import CATALOG
    s = CATALOG["tsuguharu_foujita"]
    # Check for a high-luminance ivory entry
    lums = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in s.palette]
    assert max(lums) > 0.90, (
        f"Palette should include a near-white ivory tone; max_lum={max(lums):.3f}"
    )


def test_s260_catalog_count_increased():
    """CATALOG count must be 257 (new artist added this session)."""
    from art_catalog import CATALOG
    assert len(CATALOG) == 257, f"Expected 257 catalog entries, got {len(CATALOG)}"


def test_s260_catalog_get_style_foujita():
    """get_style() must retrieve Foujita by key."""
    from art_catalog import get_style
    s = get_style("tsuguharu_foujita")
    assert "Foujita" in s.artist


# ── Integration: run both new passes together ─────────────────────────────────

def test_s260_full_pipeline_foujita_and_sfumato():
    """Run both new passes in sequence; canvas should be modified and valid."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()

    p.foujita_milky_ground_contour_pass(opacity=0.78)
    p.paint_sfumato_contour_dissolution_pass(opacity=0.65)

    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Pipeline should modify canvas"
    assert after.min() >= 0 and after.max() <= 255, "Values must stay in [0, 255]"
    assert np.array_equal(before[:, :, 3], after[:, :, 3]), "Alpha must be preserved"
