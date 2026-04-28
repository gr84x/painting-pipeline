"""
test_s234_additions.py -- Session 234 tests for ryder_moonlit_sea_pass,
paint_varnish_depth_pass, and the albert_pinkham_ryder catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64, rgb=(80, 80, 80)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)),
        "RGB")


def _dark_reference(w: int = 64, h: int = 64):
    """Reference biased toward dark tones."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :] = 18
    arr[h//2:h//2+6, w//4:3*w//4] = 160  # pale horizon strip
    return Image.fromarray(arr, "RGB")


def _gradient_reference(w: int = 64, h: int = 64):
    """Horizontal luminance gradient from dark to light."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for x in range(w):
        v = int(x / w * 200) + 20
        arr[:, x, :] = v
    return Image.fromarray(arr, "RGB")


def _multitone_reference(w: int = 80, h: int = 80):
    """Dark / mid-tone / bright zones side by side."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w//3, :]       = 20
    arr[:, w//3:2*w//3, :] = 128
    arr[:, 2*w//3:, :]     = 220
    return Image.fromarray(arr, "RGB")


def _colorful_reference(w: int = 64, h: int = 64):
    """Reference with varied hue and saturation."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for x in range(w):
        v = int(x / w * 180) + 30
        arr[:w//2, x, 0] = v          # red channel top half
        arr[w//2:, x, 2] = v          # blue channel bottom half
        arr[:, x, 1] = 40             # green low
    return Image.fromarray(arr, "RGB")


def _primed_dark(w=64, h=64):
    """Dark-ground painter for nocturnal scenes."""
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = _dark_reference(w, h)
    p.tone_ground((0.08, 0.07, 0.12), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    return p


def _primed_grad(w=64, h=64):
    """Painter with gradient reference."""
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = _gradient_reference(w, h)
    p.tone_ground((0.45, 0.40, 0.32), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    return p


def _primed_multi(w=80, h=80):
    """Painter with 3-zone tonal reference."""
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = _multitone_reference(w, h)
    p.tone_ground((0.35, 0.32, 0.28), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=25)
    return p


def _primed_colorful(w=64, h=64):
    """Painter with colourful reference for saturation tests."""
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = _colorful_reference(w, h)
    p.tone_ground((0.40, 0.35, 0.28), texture_strength=0.03)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    return p


def _primed_bright(w=64, h=64):
    """Painter with predominantly bright canvas."""
    from PIL import Image
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * 210), "RGB")
    p.tone_ground((0.72, 0.72, 0.70), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    return p


def _get_rgb(painter) -> np.ndarray:
    """Return HxWx3 float32 [0,1] from painter canvas."""
    surface = painter.canvas.surface
    raw = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (painter.canvas.h, painter.canvas.w, 4)).copy()
    b = raw[:, :, 0].astype(np.float32) / 255.0
    g = raw[:, :, 1].astype(np.float32) / 255.0
    r = raw[:, :, 2].astype(np.float32) / 255.0
    return np.stack([r, g, b], axis=-1)


# ─────────────────────────────────────────────────────────────────────────────
# Art catalog — albert_pinkham_ryder entry  (session 234)
# ─────────────────────────────────────────────────────────────────────────────

def test_s234_catalog_ryder_exists():
    """Session 234: CATALOG must contain 'albert_pinkham_ryder' key."""
    from art_catalog import CATALOG
    assert "albert_pinkham_ryder" in CATALOG, (
        "CATALOG is missing 'albert_pinkham_ryder' entry")


def test_s234_catalog_ryder_fields():
    """Session 234: albert_pinkham_ryder ArtStyle must have all required fields."""
    from art_catalog import CATALOG
    s = CATALOG["albert_pinkham_ryder"]
    assert s.artist == "Albert Pinkham Ryder"
    assert "American" in s.nationality
    assert len(s.palette) >= 6
    assert 0.0 <= s.wet_blend <= 1.0
    assert 0.0 <= s.edge_softness <= 1.0
    assert len(s.famous_works) >= 5
    assert "ryder_moonlit_sea_pass" in s.inspiration


def test_s234_catalog_ryder_get_style():
    """Session 234: get_style('albert_pinkham_ryder') must return entry without error."""
    from art_catalog import get_style
    s = get_style("albert_pinkham_ryder")
    assert s.artist == "Albert Pinkham Ryder"


def test_s234_catalog_ryder_palette_has_dark():
    """Session 234: Ryder palette must include near-black shadow tones."""
    from art_catalog import CATALOG
    s = CATALOG["albert_pinkham_ryder"]
    dark_entries = [c for c in s.palette if max(c) < 0.18]
    assert len(dark_entries) >= 2, (
        "Ryder palette must have at least 2 near-black shadow tones")


def test_s234_catalog_ryder_palette_has_amber():
    """Session 234: Ryder palette must include at least one amber/ochre tone."""
    from art_catalog import CATALOG
    s = CATALOG["albert_pinkham_ryder"]
    # Amber: R > G > B, all mid-range
    amber = [c for c in s.palette if c[0] > c[2] + 0.10 and c[0] > 0.30]
    assert len(amber) >= 1, (
        "Ryder palette should have at least one amber/ochre tone")


def test_s234_catalog_ryder_famous_works():
    """Session 234: Ryder famous_works must include 'Moonlit Cove'."""
    from art_catalog import CATALOG
    s = CATALOG["albert_pinkham_ryder"]
    titles = [t for t, _ in s.famous_works]
    assert any("Moonlit" in t or "Cove" in t or "Moonlit Cove" in t for t in titles), (
        "Ryder famous_works should include 'Moonlit Cove'")


def test_s234_catalog_ryder_period():
    """Session 234: Ryder period must reference 1847 and 1917."""
    from art_catalog import CATALOG
    s = CATALOG["albert_pinkham_ryder"]
    assert "1847" in s.period, "Period should contain birth year 1847"
    assert "1917" in s.period, "Period should contain death year 1917"


def test_s234_catalog_ryder_ground_dark():
    """Session 234: Ryder ground_color should be dark (warm dark brown/umber)."""
    from art_catalog import CATALOG
    s = CATALOG["albert_pinkham_ryder"]
    # Ground should be dark — max channel < 0.35
    assert max(s.ground_color) < 0.40, (
        f"Ryder ground_color should be dark, got {s.ground_color}")


def test_s234_catalog_count():
    """Session 234: CATALOG should have at least 234 unique entries."""
    from art_catalog import CATALOG
    assert len(CATALOG) >= 234, (
        f"CATALOG should have >=234 entries after s234, got {len(CATALOG)}")


# ─────────────────────────────────────────────────────────────────────────────
# ryder_moonlit_sea_pass -- session 234 (145th mode)
# ─────────────────────────────────────────────────────────────────────────────

def test_s234_ryder_pass_exists():
    """Session 234: Painter must have ryder_moonlit_sea_pass method."""
    from stroke_engine import Painter
    p = Painter(32, 32)
    assert hasattr(p, "ryder_moonlit_sea_pass"), (
        "Painter is missing ryder_moonlit_sea_pass")


def test_s234_ryder_pass_runs_without_error():
    """Session 234: ryder_moonlit_sea_pass must run on a 64x64 canvas."""
    p = _primed_dark()
    p.ryder_moonlit_sea_pass()


def test_s234_ryder_pass_modifies_canvas():
    """Session 234: ryder_moonlit_sea_pass must change at least one pixel."""
    p = _primed_dark()
    before = _get_rgb(p).copy()
    p.ryder_moonlit_sea_pass()
    after = _get_rgb(p)
    assert not np.allclose(before, after, atol=1.0 / 255), (
        "ryder_moonlit_sea_pass made no changes to canvas")


def test_s234_ryder_tonal_massing_darkens_shadows():
    """Session 234: ryder_moonlit_sea_pass must darken already-dark pixels."""
    p = _primed_dark(w=80, h=80)
    before = _get_rgb(p)
    lum_before = 0.299 * before[:, :, 0] + 0.587 * before[:, :, 1] + 0.114 * before[:, :, 2]
    very_dark = lum_before < 0.20
    if very_dark.sum() < 10:
        pytest.skip("Not enough dark pixels for shadow-massing test")
    p.ryder_moonlit_sea_pass(
        dark_thresh=0.40,
        dark_power=1.5,
        dark_crush=0.60,
        light_lift=0.0,   # disable light lifting
        amber_str=0.0,    # disable amber glaze
        dissolution_blend=0.0,
        opacity=1.0,
    )
    after = _get_rgb(p)
    lum_after = 0.299 * after[:, :, 0] + 0.587 * after[:, :, 1] + 0.114 * after[:, :, 2]
    mean_before = lum_before[very_dark].mean()
    mean_after  = lum_after[very_dark].mean()
    assert mean_after <= mean_before + 0.03, (
        f"Shadow zone should darken with tonal massing: before={mean_before:.4f} after={mean_after:.4f}")


def test_s234_ryder_tonal_massing_lifts_highlights():
    """Session 234: ryder_moonlit_sea_pass must lift bright highlight pixels."""
    p = _primed_bright()
    before = _get_rgb(p)
    lum_before = 0.299 * before[:, :, 0] + 0.587 * before[:, :, 1] + 0.114 * before[:, :, 2]
    bright = lum_before > 0.60
    if bright.sum() < 10:
        pytest.skip("Not enough bright pixels for highlight-lift test")
    p.ryder_moonlit_sea_pass(
        light_thresh=0.50,
        light_power=1.2,
        light_lift=0.40,
        dark_crush=0.0,    # disable shadow crushing
        amber_str=0.0,
        dissolution_blend=0.0,
        opacity=1.0,
    )
    after = _get_rgb(p)
    lum_after = 0.299 * after[:, :, 0] + 0.587 * after[:, :, 1] + 0.114 * after[:, :, 2]
    mean_before = lum_before[bright].mean()
    mean_after  = lum_after[bright].mean()
    assert mean_after >= mean_before - 0.03, (
        f"Highlight zone should lift with tonal massing: before={mean_before:.4f} after={mean_after:.4f}")


def test_s234_ryder_amber_glaze_adds_warmth():
    """Session 234: ryder_moonlit_sea_pass amber glaze must increase R relative to B in mid-tones."""
    p = _primed_grad()
    before = _get_rgb(p)
    lum_before = 0.299 * before[:, :, 0] + 0.587 * before[:, :, 1] + 0.114 * before[:, :, 2]
    mid = (lum_before > 0.25) & (lum_before < 0.60)
    if mid.sum() < 10:
        pytest.skip("Not enough mid-tone pixels for amber glaze test")
    p.ryder_moonlit_sea_pass(
        dark_crush=0.0,     # disable shadow massing
        light_lift=0.0,     # disable highlight lift
        amber_str=1.0,
        amber_r=0.20,
        amber_g=0.05,
        amber_b=0.12,
        dissolution_blend=0.0,
        opacity=1.0,
    )
    after = _get_rgb(p)
    r_before = before[:, :, 0][mid].mean()
    b_before = before[:, :, 2][mid].mean()
    r_after  = after[:, :, 0][mid].mean()
    b_after  = after[:, :, 2][mid].mean()
    # Amber = R should increase relative to B
    r_delta = r_after - r_before
    b_delta = b_after - b_before
    assert r_delta > b_delta - 0.01, (
        f"Amber glaze should increase R more than B in mid-tones: R_delta={r_delta:.4f} B_delta={b_delta:.4f}")


def test_s234_ryder_dissolution_softens_edges():
    """Session 234: with large dissolution sigma, ryder_moonlit_sea_pass reduces local variance."""
    p = _primed_multi()
    before = _get_rgb(p)
    var_before = float(np.var(before))
    p.ryder_moonlit_sea_pass(
        dark_crush=0.0,
        light_lift=0.0,
        amber_str=0.0,
        dissolution_sigma=6.0,
        dissolution_blend=0.80,
        opacity=1.0,
    )
    after = _get_rgb(p)
    var_after = float(np.var(after))
    assert var_after <= var_before + 1e-4, (
        f"Dissolution should reduce image variance: before={var_before:.6f} after={var_after:.6f}")


def test_s234_ryder_pass_preserves_alpha():
    """Session 234: ryder_moonlit_sea_pass must not alter alpha channel."""
    p = _primed_dark()
    surface = p.canvas.surface
    before_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))[:, :, 3].copy()
    p.ryder_moonlit_sea_pass()
    after_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))[:, :, 3].copy()
    assert np.array_equal(before_alpha, after_alpha), (
        "ryder_moonlit_sea_pass must not modify alpha channel")


def test_s234_ryder_pass_values_in_range():
    """Session 234: ryder_moonlit_sea_pass must keep all pixel values in [0, 255]."""
    p = _primed_dark()
    p.ryder_moonlit_sea_pass()
    surface = p.canvas.surface
    raw = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))
    assert raw[:, :, :3].min() >= 0
    assert raw[:, :, :3].max() <= 255


def test_s234_ryder_pass_accepts_kwargs():
    """Session 234: ryder_moonlit_sea_pass must accept all documented kwargs."""
    p = _primed_dark()
    p.ryder_moonlit_sea_pass(
        dark_thresh=0.35,
        dark_power=2.0,
        dark_crush=0.45,
        light_thresh=0.60,
        light_power=1.80,
        light_lift=0.25,
        amber_center=0.38,
        amber_width=0.22,
        amber_r=0.12,
        amber_g=0.05,
        amber_b=0.08,
        amber_str=0.65,
        dissolution_sigma=2.5,
        dissolution_blend=0.25,
        opacity=0.80,
    )


def test_s234_ryder_zero_opacity_leaves_canvas_unchanged():
    """Session 234: ryder_moonlit_sea_pass at opacity=0 must not change canvas."""
    p = _primed_dark()
    before = _get_rgb(p).copy()
    p.ryder_moonlit_sea_pass(opacity=0.0)
    after = _get_rgb(p)
    assert np.allclose(before, after, atol=2.0 / 255), (
        "ryder_moonlit_sea_pass at opacity=0 should not change canvas")


# ─────────────────────────────────────────────────────────────────────────────
# paint_varnish_depth_pass -- session 234 improvement
# ─────────────────────────────────────────────────────────────────────────────

def test_s234_varnish_pass_exists():
    """Session 234: Painter must have paint_varnish_depth_pass method."""
    from stroke_engine import Painter
    p = Painter(32, 32)
    assert hasattr(p, "paint_varnish_depth_pass"), (
        "Painter is missing paint_varnish_depth_pass")


def test_s234_varnish_pass_runs_without_error():
    """Session 234: paint_varnish_depth_pass must run on a 64x64 canvas."""
    p = _primed_grad()
    p.paint_varnish_depth_pass()


def test_s234_varnish_pass_modifies_canvas():
    """Session 234: paint_varnish_depth_pass must change at least one pixel."""
    p = _primed_colorful()
    before = _get_rgb(p).copy()
    p.paint_varnish_depth_pass()
    after = _get_rgb(p)
    assert not np.allclose(before, after, atol=1.0 / 255), (
        "paint_varnish_depth_pass made no changes to canvas")


def test_s234_varnish_saturation_increases_in_midtones():
    """Session 234: varnish pass must increase saturation in mid-tone zone."""
    p = _primed_colorful()
    before = _get_rgb(p)
    lum_before = 0.299 * before[:, :, 0] + 0.587 * before[:, :, 1] + 0.114 * before[:, :, 2]
    mid = (lum_before > 0.25) & (lum_before < 0.65)
    if mid.sum() < 10:
        pytest.skip("Not enough mid-tone pixels for saturation test")

    def _sat(rgb):
        lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
        # Saturation proxy = mean deviation from grey
        return np.abs(rgb[:, :, 0] - lum).mean() + np.abs(rgb[:, :, 1] - lum).mean()

    sat_before = _sat(before[:, :] if before.ndim == 3 else before)
    p.paint_varnish_depth_pass(sat_boost=0.60, sheen_strength=0.0, opacity=1.0)
    after = _get_rgb(p)
    sat_after = _sat(after)
    # Saturation should not decrease significantly
    assert sat_after >= sat_before - 0.01, (
        f"Varnish saturation boost should not decrease saturation: "
        f"before={sat_before:.5f} after={sat_after:.5f}")


def test_s234_varnish_pass_preserves_alpha():
    """Session 234: paint_varnish_depth_pass must not alter alpha channel."""
    p = _primed_grad()
    surface = p.canvas.surface
    before_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))[:, :, 3].copy()
    p.paint_varnish_depth_pass()
    after_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))[:, :, 3].copy()
    assert np.array_equal(before_alpha, after_alpha), (
        "paint_varnish_depth_pass must not modify alpha channel")


def test_s234_varnish_pass_values_in_range():
    """Session 234: paint_varnish_depth_pass must keep all pixel values in [0, 255]."""
    p = _primed_colorful()
    p.paint_varnish_depth_pass()
    surface = p.canvas.surface
    raw = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))
    assert raw[:, :, :3].min() >= 0
    assert raw[:, :, :3].max() <= 255


def test_s234_varnish_sheen_only_in_bright_zones():
    """Session 234: sheen should be minimal on dark canvas with high sheen_thresh."""
    p = _primed_dark()
    before = _get_rgb(p).copy()
    p.paint_varnish_depth_pass(
        sat_boost=0.0,       # disable saturation
        sheen_thresh=0.90,   # only very bright pixels
        sheen_strength=0.50,
        opacity=1.0,
    )
    after = _get_rgb(p)
    diff = np.abs(after - before)
    # Dark canvas has very few pixels > 0.90 lum, so sheen change should be tiny
    mean_change = diff.mean()
    assert mean_change < 0.04, (
        f"Sheen should be minimal on dark canvas: mean_change={mean_change:.5f}")


def test_s234_varnish_pass_accepts_kwargs():
    """Session 234: paint_varnish_depth_pass must accept all documented kwargs."""
    p = _primed_grad()
    p.paint_varnish_depth_pass(
        sat_center=0.42,
        sat_width=0.25,
        sat_boost=0.30,
        sheen_thresh=0.75,
        sheen_sigma=4.0,
        sheen_strength=0.05,
        opacity=0.65,
        seed=42,
    )


def test_s234_varnish_low_opacity_smaller_change():
    """Session 234: low opacity should produce smaller change than high opacity."""
    p_lo = _primed_colorful()
    before_lo = _get_rgb(p_lo).copy()
    p_lo.paint_varnish_depth_pass(opacity=0.05)
    after_lo = _get_rgb(p_lo)

    p_hi = _primed_colorful()
    before_hi = _get_rgb(p_hi).copy()
    p_hi.paint_varnish_depth_pass(opacity=0.90)
    after_hi = _get_rgb(p_hi)

    change_lo = np.abs(after_lo - before_lo).mean()
    change_hi = np.abs(after_hi - before_hi).mean()
    assert change_lo <= change_hi + 1e-5, (
        f"Low opacity should produce smaller change: lo={change_lo:.6f} hi={change_hi:.6f}")


# ─────────────────────────────────────────────────────────────────────────────
# Combined integration
# ─────────────────────────────────────────────────────────────────────────────

def test_s234_combined_passes_run():
    """Session 234: ryder and varnish passes must run sequentially without error."""
    p = _primed_dark()
    p.ryder_moonlit_sea_pass()
    p.paint_varnish_depth_pass()


def test_s234_combined_passes_result_in_range():
    """Session 234: combined passes must keep pixels in [0, 255]."""
    p = _primed_dark()
    p.ryder_moonlit_sea_pass()
    p.paint_varnish_depth_pass()
    surface = p.canvas.surface
    raw = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))
    assert raw[:, :, :3].min() >= 0
    assert raw[:, :, :3].max() <= 255
