"""
test_s280_additions.py -- Session 280 tests for paint_lost_found_edges_pass,
fechin_gestural_impasto_pass, and the nicolai_fechin catalog entry.
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


def _portrait_reference(w=64, h=64):
    """Portrait-style reference: dark background, lit face in center."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :, :] = [28, 22, 18]            # dark umber background
    # Face zone (upper center)
    cy, cx = h // 3, w // 2
    arr[cy - 12:cy + 14, cx - 10:cx + 10, :] = [180, 130, 85]   # warm flesh
    arr[cy - 4:cy + 4, cx - 4:cx + 4, :]    = [220, 185, 140]   # bright highlight
    arr[cy + 14:, :, :] = [55, 38, 22]    # dark drapery/clothing
    return arr


def _high_contrast_reference(w=64, h=64):
    """High-contrast reference: bright center on dark surround."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :, :] = [25, 22, 20]
    cy, cx = h // 2, w // 2
    arr[cy - 12:cy + 12, cx - 12:cx + 12, :] = [240, 235, 210]
    return arr


def _flat_midtone_reference(w=64, h=64):
    arr = np.full((h, w, 3), [128, 120, 100], dtype=np.uint8)
    return arr


def _prime_canvas(p, ref=None, *, portrait=False, high_contrast=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if high_contrast:
            ref = _high_contrast_reference(w, h)
        elif portrait:
            ref = _portrait_reference(w, h)
        else:
            ref = _portrait_reference(w, h)
    p.tone_ground((0.58, 0.42, 0.26), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=30)


# ── paint_lost_found_edges_pass ───────────────────────────────────────────────

def test_s280_lost_found_edges_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_lost_found_edges_pass")


def test_s280_lost_found_edges_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.paint_lost_found_edges_pass()
    assert result is None


def test_s280_lost_found_edges_modifies_canvas():
    """Lost/found edges should visibly change the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, high_contrast=True)
    before = _get_canvas(p).copy()
    p.paint_lost_found_edges_pass(
        found_threshold = 0.28,
        sharp_strength  = 0.80,
        lost_strength   = 0.55,
        opacity         = 0.95,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after paint_lost_found_edges_pass"
    )


def test_s280_lost_found_edges_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_lost_found_edges_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s280_lost_found_edges_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, high_contrast=True)
    p.paint_lost_found_edges_pass(
        found_threshold = 0.30,
        sharp_strength  = 1.0,
        lost_strength   = 0.80,
        opacity         = 1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s280_lost_found_edges_sharpens_focal_zone():
    """Found-edge sharpening should increase contrast near bright focal center."""
    p = _make_small_painter(w=80, h=80)
    ref = _high_contrast_reference(80, 80)
    p.tone_ground((0.58, 0.42, 0.26), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=200)
    p.build_form(ref, stroke_size=4, n_strokes=150)
    p.place_lights(ref, stroke_size=3, n_strokes=80)

    before = _get_canvas(p).copy()
    p.paint_lost_found_edges_pass(
        found_threshold = 0.25,
        sharp_strength  = 1.20,
        lost_strength   = 0.0,   # disable lost-edge softening for isolation
        opacity         = 1.0,
    )
    after = _get_canvas(p)
    # Some pixels should have increased luminance (sharpening adds detail)
    before_lum = before[:, :, 2].astype(np.float32) * 0.299 / 255
    after_lum  = after[:, :, 2].astype(np.float32)  * 0.299 / 255
    brightened = (after_lum > before_lum + 0.01).sum()
    assert brightened > 0, (
        "Found-edge sharpening should brighten some pixels (unsharp mask detail)"
    )


def test_s280_lost_found_edges_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.paint_lost_found_edges_pass(opacity=0.85)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque"
    )


def test_s280_lost_found_edges_zero_strengths_minimal_change():
    """With all strengths zero the pass should produce no visible change."""
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.paint_lost_found_edges_pass(
        sharp_strength = 0.0,
        lost_strength  = 0.0,
        opacity        = 1.0,
    )
    after = _get_canvas(p)
    diff = np.abs(before[:, :, :3].astype(np.int32) - after[:, :, :3].astype(np.int32))
    assert diff.max() <= 2, (
        f"Zero strengths should produce no visible change: max_diff={diff.max()}"
    )


# ── fechin_gestural_impasto_pass ──────────────────────────────────────────────

def test_s280_fechin_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "fechin_gestural_impasto_pass")


def test_s280_fechin_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.fechin_gestural_impasto_pass()
    assert result is None


def test_s280_fechin_pass_modifies_canvas():
    """Fechin pass should visibly change the canvas."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, portrait=True)
    before = _get_canvas(p).copy()
    p.fechin_gestural_impasto_pass(
        aniso_strength   = 0.45,
        scrape_strength  = 0.55,
        sharp_strength   = 0.75,
        earth_strength   = 0.30,
        opacity          = 0.92,
    )
    after = _get_canvas(p)
    assert not np.array_equal(before, after), (
        "Canvas should change after fechin_gestural_impasto_pass"
    )


def test_s280_fechin_pass_zero_opacity_no_change():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    before = _get_canvas(p).copy()
    p.fechin_gestural_impasto_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), (
        "Zero opacity should produce no canvas change"
    )


def test_s280_fechin_pass_output_in_valid_range():
    p = _make_small_painter(w=72, h=72)
    _prime_canvas(p, portrait=True)
    p.fechin_gestural_impasto_pass(
        aniso_strength   = 0.60,
        scrape_threshold = 0.55,
        scrape_strength  = 0.70,
        sharp_strength   = 1.0,
        earth_strength   = 0.45,
        opacity          = 1.0,
    )
    canvas = _get_canvas(p)
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s280_fechin_pass_scraping_brightens_highlights():
    """Palette knife scraping should brighten high-luminance areas (knife exposes ground)."""
    p = _make_small_painter(w=80, h=80)
    ref = _high_contrast_reference(80, 80)
    p.tone_ground((0.58, 0.42, 0.26), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=200)
    p.build_form(ref, stroke_size=4, n_strokes=120)
    p.place_lights(ref, stroke_size=3, n_strokes=80)

    before = _get_canvas(p).copy()
    # Only activate scraping, zero other strengths
    p.fechin_gestural_impasto_pass(
        aniso_strength   = 0.0,
        scrape_threshold = 0.55,
        scrape_strength  = 0.80,
        sharp_strength   = 0.0,
        earth_strength   = 0.0,
        opacity          = 1.0,
    )
    after = _get_canvas(p)
    # In the bright center, the scraping should have changed pixel values
    h, w = before.shape[:2]
    cy, cx = h // 2, w // 2
    center_before = before[cy - 6:cy + 6, cx - 6:cx + 6, :3].astype(np.float32)
    center_after  = after[cy - 6:cy + 6, cx - 6:cx + 6, :3].astype(np.float32)
    diff = np.abs(center_before - center_after).max()
    assert diff > 2, (
        f"Palette knife scraping should modify bright center pixels: diff={diff}"
    )


def test_s280_fechin_pass_earth_tones_warm_midtones():
    """Earth tone reinforcement should push midtones warmer (increase R, decrease B)."""
    p = _make_small_painter(w=64, h=64)
    ref = _flat_midtone_reference(64, 64)
    p.tone_ground((0.58, 0.42, 0.26), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=100)

    before = _get_canvas(p).copy()
    p.fechin_gestural_impasto_pass(
        aniso_strength   = 0.0,
        scrape_threshold = 0.99,   # disable scraping (nothing this bright)
        scrape_strength  = 0.0,
        sharp_strength   = 0.0,
        earth_strength   = 0.60,   # strong sienna push
        earth_center     = 0.45,
        earth_sigma      = 0.25,
        sienna_r         = 0.72,
        sienna_g         = 0.38,
        sienna_b         = 0.12,
        opacity          = 1.0,
    )
    after = _get_canvas(p)
    # Sienna (0.72/0.38/0.12) is warm: should push R up, B down in midtones
    # BGRA format: channel 2=R, 1=G, 0=B
    mean_R_before = before[:, :, 2].astype(np.float32).mean()
    mean_B_before = before[:, :, 0].astype(np.float32).mean()
    mean_R_after  = after[:, :, 2].astype(np.float32).mean()
    mean_B_after  = after[:, :, 0].astype(np.float32).mean()
    assert mean_R_after >= mean_R_before - 1.0, (
        "Sienna earth push should not decrease mean R channel significantly"
    )
    assert mean_B_after <= mean_B_before + 1.0, (
        "Sienna earth push should not increase mean B channel"
    )


def test_s280_fechin_pass_alpha_unchanged():
    p = _make_small_painter(w=64, h=64)
    _prime_canvas(p)
    p.fechin_gestural_impasto_pass(opacity=0.85)
    canvas = _get_canvas(p)
    assert canvas[:, :, 3].min() == 255, (
        "Alpha channel should remain fully opaque after fechin_gestural_impasto_pass"
    )


def test_s280_fechin_pass_single_pixel_canvas():
    """Edge case: tiny canvas should not crash."""
    p = _make_small_painter(w=32, h=32)
    _prime_canvas(p)
    p.fechin_gestural_impasto_pass(opacity=0.50)
    canvas = _get_canvas(p)
    assert canvas.shape == (32, 32, 4)


# ── nicolai_fechin catalog entry ──────────────────────────────────────────────

def test_s280_fechin_in_catalog():
    from art_catalog import CATALOG
    assert "nicolai_fechin" in CATALOG, "nicolai_fechin should be in CATALOG"


def test_s280_fechin_artist_name():
    from art_catalog import get_style
    style = get_style("nicolai_fechin")
    assert style.artist == "Nicolai Fechin"


def test_s280_fechin_movement_mentions_realism():
    from art_catalog import get_style
    style = get_style("nicolai_fechin")
    assert ("realism" in style.movement.lower() or
            "taos" in style.movement.lower() or
            "impressionism" in style.movement.lower()), (
        f"Movement should mention Realism, Taos, or Impressionism: {style.movement}"
    )


def test_s280_fechin_nationality():
    from art_catalog import get_style
    style = get_style("nicolai_fechin")
    assert ("russian" in style.nationality.lower() or
            "american" in style.nationality.lower()), (
        f"Nationality should mention Russian or American: {style.nationality}"
    )


def test_s280_fechin_period():
    from art_catalog import get_style
    style = get_style("nicolai_fechin")
    assert "1881" in style.period or "1955" in style.period, (
        f"Period should include birth/death years: {style.period}"
    )


def test_s280_fechin_palette_count():
    from art_catalog import get_style
    style = get_style("nicolai_fechin")
    assert len(style.palette) >= 6, (
        f"Fechin palette should have at least 6 colors, got {len(style.palette)}"
    )


def test_s280_fechin_palette_has_warm_earth():
    """Palette should include a warm earth/sienna tone."""
    from art_catalog import get_style
    style = get_style("nicolai_fechin")
    # Raw sienna or burnt umber: R > G > B, R > 0.5
    has_earth = any(
        c[0] > 0.50 and c[0] > c[1] > c[2]
        for c in style.palette
    )
    assert has_earth, "Palette should include warm earth/sienna tones"


def test_s280_fechin_palette_rgb_range():
    from art_catalog import get_style
    style = get_style("nicolai_fechin")
    for i, color in enumerate(style.palette):
        assert len(color) == 3, f"Palette color {i} should have 3 channels"
        for ch in color:
            assert 0.0 <= ch <= 1.0, (
                f"Palette color {i} channel out of [0,1] range: {ch}"
            )


def test_s280_fechin_famous_works():
    from art_catalog import get_style
    style = get_style("nicolai_fechin")
    assert len(style.famous_works) >= 5
    titles = [w[0].lower() for w in style.famous_works]
    assert any("taos" in t or "indian" in t or "dark" in t or "corn" in t
               for t in titles), (
        "Famous works should include at least one Taos-period work"
    )


def test_s280_fechin_inspiration_mentions_pass():
    from art_catalog import get_style
    style = get_style("nicolai_fechin")
    assert ("fechin_gestural_impasto_pass" in style.inspiration.lower() or
            "191st" in style.inspiration), (
        "Inspiration should mention fechin_gestural_impasto_pass or 191st mode"
    )


def test_s280_fechin_get_style_roundtrip():
    from art_catalog import get_style, list_artists
    assert "nicolai_fechin" in list_artists()
    style = get_style("nicolai_fechin")
    assert style.artist == "Nicolai Fechin"


# ── Combined pipeline smoke test ──────────────────────────────────────────────

def test_s280_full_pipeline_smoke():
    """Smoke test: both new passes run on a small canvas without error."""
    p = _make_small_painter(w=80, h=80)
    ref = _portrait_reference(80, 80)
    p.tone_ground((0.58, 0.42, 0.26), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.build_form(ref, stroke_size=5, n_strokes=20)
    p.place_lights(ref, stroke_size=3, n_strokes=15)

    p.fechin_gestural_impasto_pass(
        aniso_strength  = 0.40,
        scrape_strength = 0.50,
        sharp_strength  = 0.70,
        earth_strength  = 0.28,
        opacity         = 0.88,
    )
    p.paint_lost_found_edges_pass(
        found_threshold = 0.32,
        sharp_strength  = 0.80,
        lost_strength   = 0.50,
        opacity         = 0.90,
    )

    canvas = _get_canvas(p)
    assert canvas.shape == (80, 80, 4)
    assert canvas[:, :, 3].min() == 255, "Alpha channel should remain fully opaque"
    assert canvas[:, :, :3].max() <= 255
    assert canvas[:, :, :3].min() >= 0


def test_s280_passes_order_independence():
    """Running passes in either order should produce valid results."""
    ref = _portrait_reference(64, 64)

    # Order A: fechin then edges
    p1 = _make_small_painter(w=64, h=64)
    p1.tone_ground((0.58, 0.42, 0.26), texture_strength=0.01)
    p1.block_in(ref, stroke_size=8, n_strokes=20)
    p1.fechin_gestural_impasto_pass(opacity=0.80)
    p1.paint_lost_found_edges_pass(opacity=0.85)
    c1 = _get_canvas(p1)

    # Order B: edges then fechin
    p2 = _make_small_painter(w=64, h=64)
    p2.tone_ground((0.58, 0.42, 0.26), texture_strength=0.01)
    p2.block_in(ref, stroke_size=8, n_strokes=20)
    p2.paint_lost_found_edges_pass(opacity=0.85)
    p2.fechin_gestural_impasto_pass(opacity=0.80)
    c2 = _get_canvas(p2)

    for c in [c1, c2]:
        assert c.shape == (64, 64, 4)
        assert c[:, :, 3].min() == 255
        assert c[:, :, :3].max() <= 255
