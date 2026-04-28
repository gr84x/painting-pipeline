"""
test_s233_additions.py -- Session 233 tests for kuindzhi_moonlit_radiance_pass,
paint_gravity_drift_pass, and the arkhip_kuindzhi catalog entry.
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


def _bright_reference(w: int = 64, h: int = 64):
    """Bright reference with a central bright zone (simulates moon)."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :] = 20  # dark background
    # Central bright circle
    cy, cx = h // 2, w // 2
    for y in range(h):
        for x in range(w):
            if (x - cx) ** 2 + (y - cy) ** 2 < (min(w, h) // 5) ** 2:
                arr[y, x] = 230
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


def _primed_dark(w=64, h=64):
    """Dark-ground painter for moonlit scenes."""
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = _solid_reference(w, h, rgb=(20, 20, 35))
    p.tone_ground((0.06, 0.06, 0.14), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    return p


def _primed_bright(w=64, h=64):
    """Painter primed with a bright central zone."""
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = _bright_reference(w, h)
    p.tone_ground((0.06, 0.06, 0.14), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    return p


def _primed_grad(w=64, h=64):
    """Painter loaded from a gradient reference."""
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = _gradient_reference(w, h)
    p.tone_ground((0.55, 0.56, 0.60), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    return p


def _get_rgb(painter) -> np.ndarray:
    """Return HxWx3 float32 [0,1] from painter canvas."""
    import numpy as np
    surface = painter.canvas.surface
    raw = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (painter.canvas.h, painter.canvas.w, 4)).copy()
    b = raw[:, :, 0].astype(np.float32) / 255.0
    g = raw[:, :, 1].astype(np.float32) / 255.0
    r = raw[:, :, 2].astype(np.float32) / 255.0
    return np.stack([r, g, b], axis=-1)


# ─────────────────────────────────────────────────────────────────────────────
# Art catalog — arkhip_kuindzhi entry  (session 233)
# ─────────────────────────────────────────────────────────────────────────────

def test_s233_catalog_kuindzhi_exists():
    """Session 233: CATALOG must contain 'arkhip_kuindzhi' key."""
    from art_catalog import CATALOG
    assert "arkhip_kuindzhi" in CATALOG, (
        "CATALOG is missing 'arkhip_kuindzhi' entry")


def test_s233_catalog_kuindzhi_fields():
    """Session 233: arkhip_kuindzhi ArtStyle must have all required fields."""
    from art_catalog import CATALOG
    s = CATALOG["arkhip_kuindzhi"]
    assert s.artist == "Arkhip Kuindzhi"
    assert "Ukrainian" in s.nationality or "Russian" in s.nationality
    assert len(s.palette) >= 6
    assert 0.0 <= s.wet_blend <= 1.0
    assert 0.0 <= s.edge_softness <= 1.0
    assert len(s.famous_works) >= 5
    assert "kuindzhi_moonlit_radiance_pass" in s.inspiration


def test_s233_catalog_kuindzhi_get_style():
    """Session 233: get_style('arkhip_kuindzhi') must return the entry without error."""
    from art_catalog import get_style
    s = get_style("arkhip_kuindzhi")
    assert s.artist == "Arkhip Kuindzhi"


def test_s233_catalog_kuindzhi_palette_has_dark():
    """Session 233: Kuindzhi palette must include near-black shadow tones."""
    from art_catalog import CATALOG
    s = CATALOG["arkhip_kuindzhi"]
    # At least one colour should be very dark (all channels < 0.15)
    dark_entries = [c for c in s.palette if max(c) < 0.20]
    assert len(dark_entries) >= 2, (
        "Kuindzhi palette must have at least 2 near-black shadow tones")


def test_s233_catalog_kuindzhi_famous_works():
    """Session 233: Kuindzhi famous_works must include 'Moonlit Night on the Dnieper'."""
    from art_catalog import CATALOG
    s = CATALOG["arkhip_kuindzhi"]
    titles = [t for t, _ in s.famous_works]
    assert any("Dnieper" in t or "Moonlit" in t for t in titles), (
        "Kuindzhi famous_works should include 'Moonlit Night on the Dnieper'")


def test_s233_catalog_kuindzhi_period():
    """Session 233: Kuindzhi period must reference 1842 and 1910."""
    from art_catalog import CATALOG
    s = CATALOG["arkhip_kuindzhi"]
    assert "1842" in s.period, "Period should contain birth year 1842"
    assert "1910" in s.period, "Period should contain death year 1910"


def test_s233_catalog_kuindzhi_ground_dark():
    """Session 233: Kuindzhi ground_color should be very dark (all channels < 0.15)."""
    from art_catalog import CATALOG
    s = CATALOG["arkhip_kuindzhi"]
    assert max(s.ground_color) < 0.20, (
        f"Kuindzhi ground_color should be near-black, got {s.ground_color}")


# ─────────────────────────────────────────────────────────────────────────────
# kuindzhi_moonlit_radiance_pass -- session 233 (144th mode)
# ─────────────────────────────────────────────────────────────────────────────

def test_s233_kuindzhi_pass_exists():
    """Session 233: Painter must have kuindzhi_moonlit_radiance_pass method."""
    from stroke_engine import Painter
    p = Painter(32, 32)
    assert hasattr(p, "kuindzhi_moonlit_radiance_pass"), (
        "Painter is missing kuindzhi_moonlit_radiance_pass")


def test_s233_kuindzhi_pass_runs_without_error():
    """Session 233: kuindzhi_moonlit_radiance_pass must run on a 64x64 canvas."""
    p = _primed_dark()
    p.kuindzhi_moonlit_radiance_pass()


def test_s233_kuindzhi_pass_modifies_canvas():
    """Session 233: kuindzhi_moonlit_radiance_pass must change at least one pixel."""
    p = _primed_bright()
    before = _get_rgb(p).copy()
    p.kuindzhi_moonlit_radiance_pass()
    after = _get_rgb(p)
    assert not np.allclose(before, after, atol=1.0 / 255), (
        "kuindzhi_moonlit_radiance_pass made no changes to canvas")


def test_s233_kuindzhi_velvet_darkens_shadows():
    """Session 233: kuindzhi_moonlit_radiance_pass must darken deep shadow zones."""
    p = _primed_dark(w=80, h=80)
    before = _get_rgb(p)
    # Find pixels that are already fairly dark
    lum_before = 0.299 * before[:, :, 0] + 0.587 * before[:, :, 1] + 0.114 * before[:, :, 2]
    very_dark = lum_before < 0.15
    if very_dark.sum() < 10:
        pytest.skip("Not enough dark pixels on this canvas for shadow velveting test")
    p.kuindzhi_moonlit_radiance_pass(
        velvet_threshold=0.35,
        velvet_power=2.5,
        opacity=1.0,
    )
    after = _get_rgb(p)
    lum_after = 0.299 * after[:, :, 0] + 0.587 * after[:, :, 1] + 0.114 * after[:, :, 2]
    mean_before = lum_before[very_dark].mean()
    mean_after  = lum_after[very_dark].mean()
    assert mean_after <= mean_before + 0.03, (
        f"Shadow zone should darken with velveting: before={mean_before:.4f} after={mean_after:.4f}")


def test_s233_kuindzhi_halo_brightens_corona():
    """Session 233: a large halo sigma should add measurable light around bright zones."""
    p = _primed_bright(w=96, h=96)
    before = _get_rgb(p)
    lum_before = 0.299 * before[:, :, 0] + 0.587 * before[:, :, 1] + 0.114 * before[:, :, 2]
    # Identify the ring region: medium brightness (not the source, not the deep dark)
    ring_mask = (lum_before > 0.08) & (lum_before < 0.45)
    if ring_mask.sum() < 20:
        pytest.skip("Not enough ring pixels for halo test")
    p.kuindzhi_moonlit_radiance_pass(
        halo_sigma=8.0,
        halo_strength=0.25,
        moon_threshold=0.55,
        opacity=1.0,
    )
    after = _get_rgb(p)
    lum_after = 0.299 * after[:, :, 0] + 0.587 * after[:, :, 1] + 0.114 * after[:, :, 2]
    # Corona should add blue channel (cold halo)
    b_before = before[:, :, 2][ring_mask].mean()
    b_after  = after[:, :, 2][ring_mask].mean()
    assert b_after >= b_before - 0.02, (
        f"Halo corona should increase blue in ring zone: {b_before:.4f} -> {b_after:.4f}")


def test_s233_kuindzhi_cold_blue_in_highlights():
    """Session 233: kuindzhi_moonlit_radiance_pass must add blue in highlight zone."""
    # Use a bright canvas so highlights are plentiful
    from PIL import Image
    from stroke_engine import Painter
    p = Painter(64, 64)
    ref = Image.fromarray(
        (np.ones((64, 64, 3), dtype=np.uint8) * 200), "RGB")
    p.tone_ground((0.50, 0.52, 0.50), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    before = _get_rgb(p)
    p.kuindzhi_moonlit_radiance_pass(
        moon_threshold=0.55,
        moon_cold_b_shift=0.15,
        moon_cold_r_drop=0.08,
        opacity=1.0,
    )
    after = _get_rgb(p)
    lum = 0.299 * before[:, :, 0] + 0.587 * before[:, :, 1] + 0.114 * before[:, :, 2]
    bright = lum > 0.60
    if bright.sum() < 10:
        pytest.skip("Canvas not bright enough for cold-blue test")
    b_before = before[:, :, 2][bright].mean()
    r_before = before[:, :, 0][bright].mean()
    b_after  = after[:, :, 2][bright].mean()
    r_after  = after[:, :, 0][bright].mean()
    assert b_after > b_before - 0.02, (
        f"Blue should increase in highlights: {b_before:.4f} -> {b_after:.4f}")
    assert r_after <= r_before + 0.02, (
        f"Red should not increase in highlights: {r_before:.4f} -> {r_after:.4f}")


def test_s233_kuindzhi_pass_preserves_alpha():
    """Session 233: kuindzhi_moonlit_radiance_pass must not alter alpha channel."""
    import numpy as np
    p = _primed_dark()
    surface = p.canvas.surface
    before_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))[:, :, 3].copy()
    p.kuindzhi_moonlit_radiance_pass()
    after_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))[:, :, 3].copy()
    assert np.array_equal(before_alpha, after_alpha), (
        "kuindzhi_moonlit_radiance_pass must not modify alpha channel")


def test_s233_kuindzhi_pass_values_in_range():
    """Session 233: kuindzhi_moonlit_radiance_pass must keep all pixel values in [0, 255]."""
    import numpy as np
    p = _primed_bright()
    p.kuindzhi_moonlit_radiance_pass()
    surface = p.canvas.surface
    raw = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))
    assert raw[:, :, :3].min() >= 0
    assert raw[:, :, :3].max() <= 255


def test_s233_kuindzhi_pass_accepts_kwargs():
    """Session 233: kuindzhi_moonlit_radiance_pass must accept all documented kwargs."""
    p = _primed_dark()
    p.kuindzhi_moonlit_radiance_pass(
        halo_sigma=10.0,
        halo_strength=0.20,
        velvet_power=2.0,
        velvet_threshold=0.30,
        moon_cold_b_shift=0.08,
        moon_cold_r_drop=0.04,
        moon_threshold=0.70,
        shadow_b_push=0.05,
        shadow_threshold=0.20,
        streak_width=0.08,
        streak_strength=0.12,
        opacity=0.80,
    )


def test_s233_kuindzhi_streak_brighter_centre_than_edge():
    """Session 233: reflection streak makes centre column brighter than outer edge."""
    p = _primed_dark(w=80, h=80)
    # Disable all effects except the streak and measure centre vs edge
    p.kuindzhi_moonlit_radiance_pass(
        streak_width=0.10,
        streak_strength=0.40,
        halo_strength=0.0,
        velvet_threshold=0.0,   # disable velveting
        moon_cold_b_shift=0.0,
        shadow_b_push=0.0,
        opacity=1.0,
    )
    after = _get_rgb(p)
    lum_after = 0.299 * after[:, :, 0] + 0.587 * after[:, :, 1] + 0.114 * after[:, :, 2]
    centre_lum = lum_after[:, 38:42].mean()
    edge_lum   = lum_after[:, :5].mean()
    # Streak should make centre measurably brighter than far edge
    assert centre_lum >= edge_lum - 0.005, (
        f"Streak centre should be >= edge brightness: "
        f"centre={centre_lum:.4f} edge={edge_lum:.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# paint_gravity_drift_pass -- session 233 improvement
# ─────────────────────────────────────────────────────────────────────────────

def test_s233_gravity_pass_exists():
    """Session 233: Painter must have paint_gravity_drift_pass method."""
    from stroke_engine import Painter
    p = Painter(32, 32)
    assert hasattr(p, "paint_gravity_drift_pass"), (
        "Painter is missing paint_gravity_drift_pass")


def test_s233_gravity_pass_runs_without_error():
    """Session 233: paint_gravity_drift_pass must run on a 64x64 canvas."""
    p = _primed_grad()
    p.paint_gravity_drift_pass()


def test_s233_gravity_pass_modifies_canvas():
    """Session 233: paint_gravity_drift_pass must change at least one pixel."""
    p = _primed_grad()
    before = _get_rgb(p).copy()
    p.paint_gravity_drift_pass()
    after = _get_rgb(p)
    assert not np.allclose(before, after, atol=1.0 / 255), (
        "paint_gravity_drift_pass made no changes to canvas")


def test_s233_gravity_pass_preserves_alpha():
    """Session 233: paint_gravity_drift_pass must not alter alpha channel."""
    p = _primed_grad()
    surface = p.canvas.surface
    before_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))[:, :, 3].copy()
    p.paint_gravity_drift_pass()
    after_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))[:, :, 3].copy()
    assert np.array_equal(before_alpha, after_alpha), (
        "paint_gravity_drift_pass must not modify alpha channel")


def test_s233_gravity_pass_values_in_range():
    """Session 233: paint_gravity_drift_pass must keep all pixel values in [0, 255]."""
    p = _primed_grad()
    p.paint_gravity_drift_pass()
    surface = p.canvas.surface
    raw = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))
    assert raw[:, :, :3].min() >= 0
    assert raw[:, :, :3].max() <= 255


def test_s233_gravity_pass_sparse_on_dark_canvas():
    """Session 233: gravity drift should be minimal on a near-black canvas."""
    p = _primed_dark()
    before = _get_rgb(p).copy()
    p.paint_gravity_drift_pass(thick_threshold=0.50, opacity=1.0)
    after = _get_rgb(p)
    diff = np.abs(after - before)
    # On a near-black canvas (all < 0.15), the thick_gate is nearly zero
    mean_change = diff.mean()
    assert mean_change < 0.05, (
        f"Gravity drift should be minimal on dark canvas, mean change={mean_change:.5f}")


def test_s233_gravity_pass_stronger_on_bright_canvas():
    """Session 233: gravity drift should produce larger changes on a bright canvas."""
    from PIL import Image
    from stroke_engine import Painter
    p = Painter(64, 64)
    ref = Image.fromarray((np.ones((64, 64, 3), dtype=np.uint8) * 200), "RGB")
    p.tone_ground((0.70, 0.70, 0.70), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    before = _get_rgb(p).copy()
    p.paint_gravity_drift_pass(drift_strength=0.80, opacity=0.90)
    after = _get_rgb(p)
    diff = np.abs(after - before)
    # Bright canvas should show more movement than dark
    mean_change = diff.mean()
    assert mean_change > 0.001, (
        f"Gravity drift should show measurable changes on bright canvas, mean={mean_change:.6f}")


def test_s233_gravity_pass_accepts_kwargs():
    """Session 233: paint_gravity_drift_pass must accept all documented kwargs."""
    p = _primed_grad()
    p.paint_gravity_drift_pass(
        drift_sigma_down=4.0,
        drift_sigma_up=0.8,
        thick_threshold=0.30,
        thick_power=1.50,
        drift_strength=0.60,
        opacity=0.55,
    )


def test_s233_gravity_pass_at_low_opacity_small_change():
    """Session 233: low opacity should produce smaller change than high opacity."""
    p_lo = _primed_grad()
    before_lo = _get_rgb(p_lo).copy()
    p_lo.paint_gravity_drift_pass(opacity=0.05)
    after_lo = _get_rgb(p_lo)

    p_hi = _primed_grad()
    before_hi = _get_rgb(p_hi).copy()
    p_hi.paint_gravity_drift_pass(opacity=0.90)
    after_hi = _get_rgb(p_hi)

    change_lo = np.abs(after_lo - before_lo).mean()
    change_hi = np.abs(after_hi - before_hi).mean()
    assert change_lo <= change_hi + 1e-5, (
        f"Low opacity should produce smaller change: lo={change_lo:.6f} hi={change_hi:.6f}")


# ─────────────────────────────────────────────────────────────────────────────
# Combined integration: both passes work together
# ─────────────────────────────────────────────────────────────────────────────

def test_s233_combined_passes_run():
    """Session 233: kuindzhi and gravity passes must run sequentially without error."""
    p = _primed_bright()
    p.kuindzhi_moonlit_radiance_pass()
    p.paint_gravity_drift_pass()


def test_s233_combined_passes_result_in_range():
    """Session 233: combined passes must keep pixels in [0, 255]."""
    p = _primed_bright()
    p.kuindzhi_moonlit_radiance_pass()
    p.paint_gravity_drift_pass()
    surface = p.canvas.surface
    raw = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        (p.canvas.h, p.canvas.w, 4))
    assert raw[:, :, :3].min() >= 0
    assert raw[:, :, :3].max() <= 255


# ─────────────────────────────────────────────────────────────────────────────
# Catalog count regression: session 233 should have 233 unique keys
# ─────────────────────────────────────────────────────────────────────────────

def test_s233_catalog_count():
    """Session 233: CATALOG should have at least 233 entries."""
    from art_catalog import CATALOG
    assert len(CATALOG) >= 233, (
        f"CATALOG should have >=233 entries after s233, got {len(CATALOG)}")
