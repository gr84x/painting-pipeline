"""
test_s232_additions.py -- Session 232 tests for khnopff_frozen_reverie_pass,
warm_cool_zone_pass, and the fernand_khnopff catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64, rgb=(140, 140, 148)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)),
        "RGB")


def _gradient_reference(w: int = 64, h: int = 64):
    """Horizontal luminance gradient from dark to light."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for x in range(w):
        v = int(x / w * 200) + 30
        arr[:, x, :] = v
    return Image.fromarray(arr, "RGB")


def _multitone_reference(w: int = 80, h: int = 80):
    """Dark / mid-tone / bright zones side by side."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w//3, :]       = 25
    arr[:, w//3:2*w//3, :] = 128
    arr[:, 2*w//3:, :]     = 230
    return Image.fromarray(arr, "RGB")


def _primed(w=64, h=64, ref_rgb=(140, 140, 148)):
    """Return a painter with tone_ground + block_in applied."""
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = _solid_reference(w, h, rgb=ref_rgb)
    p.tone_ground((0.55, 0.56, 0.60), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    return p


def _primed_grad(w=64, h=64):
    """Primed painter loaded from a gradient reference."""
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = _gradient_reference(w, h)
    p.tone_ground((0.55, 0.56, 0.60), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    return p


# ─────────────────────────────────────────────────────────────────────────────
# Art catalog — fernand_khnopff entry  (session 232)
# ─────────────────────────────────────────────────────────────────────────────

def test_s232_catalog_khnopff_exists():
    """Session 232: CATALOG must contain 'fernand_khnopff' key."""
    from art_catalog import CATALOG
    assert "fernand_khnopff" in CATALOG, (
        "CATALOG is missing 'fernand_khnopff' entry")


def test_s232_catalog_khnopff_fields():
    """Session 232: fernand_khnopff ArtStyle must have all required fields."""
    from art_catalog import CATALOG
    s = CATALOG["fernand_khnopff"]
    assert s.artist == "Fernand Khnopff"
    assert "Belgian" in s.nationality
    assert len(s.palette) >= 5
    assert 0.0 <= s.wet_blend <= 1.0
    assert 0.0 <= s.edge_softness <= 1.0
    assert len(s.famous_works) >= 3
    assert "khnopff_frozen_reverie_pass" in s.inspiration


def test_s232_catalog_khnopff_get_style():
    """Session 232: get_style('fernand_khnopff') must return the entry without error."""
    from art_catalog import get_style
    s = get_style("fernand_khnopff")
    assert s.artist == "Fernand Khnopff"


def test_s232_catalog_khnopff_palette_is_cool():
    """Session 232: Khnopff palette must have predominantly cool tones (B >= R for most)."""
    from art_catalog import CATALOG
    s = CATALOG["fernand_khnopff"]
    cool_count = sum(1 for r, g, b in s.palette if b >= r)
    assert cool_count >= len(s.palette) // 2, (
        "Khnopff palette should have predominantly cool (B>=R) tones")


def test_s232_catalog_khnopff_famous_works():
    """Session 232: Khnopff famous_works must include 'I Lock My Door' or 'Caress'."""
    from art_catalog import CATALOG
    s = CATALOG["fernand_khnopff"]
    titles = [t for t, _ in s.famous_works]
    assert any("Lock" in t or "Caress" in t or "Memories" in t for t in titles), (
        "Khnopff famous_works should include a key Symbolist painting")


def test_s232_catalog_khnopff_period():
    """Session 232: Khnopff period must reference 1858 and 1921."""
    from art_catalog import CATALOG
    s = CATALOG["fernand_khnopff"]
    assert "1858" in s.period
    assert "1921" in s.period


def test_s232_catalog_count_increased():
    """Session 232: total artist count must be >= 232 (added Khnopff)."""
    from art_catalog import list_artists
    n = len(list_artists())
    assert n >= 232, f"Expected >= 232 artists, got {n}"


# ─────────────────────────────────────────────────────────────────────────────
# khnopff_frozen_reverie_pass  (session 232 — 143rd mode)
# ─────────────────────────────────────────────────────────────────────────────

def test_s232_khnopff_pass_exists():
    """Session 232: Painter must have khnopff_frozen_reverie_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "khnopff_frozen_reverie_pass"), (
        "Painter is missing khnopff_frozen_reverie_pass")


def test_s232_khnopff_pass_callable():
    """Session 232: khnopff_frozen_reverie_pass must be callable."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "khnopff_frozen_reverie_pass"))


def test_s232_khnopff_pass_runs_without_error():
    """Session 232: khnopff_frozen_reverie_pass must run without raising."""
    p = _primed(64, 64, ref_rgb=(140, 140, 148))
    p.khnopff_frozen_reverie_pass()


def test_s232_khnopff_pass_modifies_canvas():
    """Session 232: khnopff_frozen_reverie_pass must change pixel values."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    p.khnopff_frozen_reverie_pass()
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    assert not np.array_equal(before, after), (
        "khnopff_frozen_reverie_pass should modify the canvas")


def test_s232_khnopff_pass_output_stays_in_range():
    """Session 232: khnopff_frozen_reverie_pass output must stay within [0, 255]."""
    p = _primed_grad(64, 64)
    p.khnopff_frozen_reverie_pass()
    surface = p.canvas.surface
    arr = np.frombuffer(surface.get_data(), dtype=np.uint8)
    assert arr.min() >= 0
    assert arr.max() <= 255


def test_s232_khnopff_pass_desaturates_canvas():
    """Session 232: khnopff pass must reduce saturation (image becomes more grey)."""
    p = _primed(64, 64, ref_rgb=(200, 100, 50))
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4).copy()
    # Compute before-saturation as channel spread
    b_before = before[:, :, :3].astype(float)
    spread_before = (b_before.max(axis=2) - b_before.min(axis=2)).mean()
    p.khnopff_frozen_reverie_pass(desat_str=0.80, opacity=1.0)
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    b_after = after[:, :, :3].astype(float)
    spread_after = (b_after.max(axis=2) - b_after.min(axis=2)).mean()
    assert spread_after < spread_before, (
        "khnopff_frozen_reverie_pass should desaturate (reduce channel spread)")


def test_s232_khnopff_pass_opacity_zero_no_change():
    """Session 232: khnopff_frozen_reverie_pass at opacity=0 must not change canvas."""
    p = _primed(64, 64, ref_rgb=(140, 140, 148))
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    p.khnopff_frozen_reverie_pass(opacity=0.0)
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        "khnopff_frozen_reverie_pass at opacity=0 should not change canvas")


def test_s232_khnopff_pass_alpha_channel_preserved():
    """Session 232: khnopff_frozen_reverie_pass must not alter the alpha channel."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        64, 64, 4)[:, :, 3].copy()
    p.khnopff_frozen_reverie_pass()
    after_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        64, 64, 4)[:, :, 3]
    assert np.array_equal(before_alpha, after_alpha), (
        "khnopff_frozen_reverie_pass must not modify the alpha channel")


def test_s232_khnopff_pass_accepts_custom_params():
    """Session 232: khnopff_frozen_reverie_pass must accept all custom parameters."""
    p = _primed_grad(64, 64)
    p.khnopff_frozen_reverie_pass(
        desat_str=0.60,
        cool_shift=0.04,
        reverie_sigma=1.5,
        mist_str=0.40,
        bright_start=0.55,
        bright_range=0.20,
        pearl_b_boost=0.02,
        pearl_start=0.72,
        opacity=0.75,
    )


def test_s232_khnopff_pass_docstring_mentions_session():
    """Session 232: khnopff_frozen_reverie_pass docstring must reference session 232."""
    from stroke_engine import Painter
    doc = Painter.khnopff_frozen_reverie_pass.__doc__
    assert doc is not None
    assert "232" in doc, "Docstring should identify this as session 232"
    assert "FORTY-THIRD" in doc or "143" in doc, (
        "Docstring should name this as the 143rd mode")


def test_s232_khnopff_pass_full_pipeline_sequence():
    """Session 232: khnopff pass must work after tone_ground + block_in + glaze."""
    from stroke_engine import Painter
    p = Painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(140, 140, 148))
    p.tone_ground((0.55, 0.56, 0.60), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.khnopff_frozen_reverie_pass()
    p.glaze((0.60, 0.62, 0.68), opacity=0.12)


# ─────────────────────────────────────────────────────────────────────────────
# warm_cool_zone_pass  (session 232 improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_s232_warm_cool_pass_exists():
    """Session 232: Painter must have warm_cool_zone_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "warm_cool_zone_pass"), (
        "Painter is missing warm_cool_zone_pass")


def test_s232_warm_cool_pass_callable():
    """Session 232: warm_cool_zone_pass must be callable."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "warm_cool_zone_pass"))


def test_s232_warm_cool_pass_runs_without_error():
    """Session 232: warm_cool_zone_pass must run without raising."""
    p = _primed(64, 64, ref_rgb=(128, 120, 110))
    p.warm_cool_zone_pass()


def test_s232_warm_cool_pass_modifies_canvas():
    """Session 232: warm_cool_zone_pass must change pixel values."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    p.warm_cool_zone_pass()
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    assert not np.array_equal(before, after), (
        "warm_cool_zone_pass should modify the canvas")


def test_s232_warm_cool_pass_output_in_range():
    """Session 232: warm_cool_zone_pass output must stay within [0, 255]."""
    from stroke_engine import Painter
    p = Painter(80, 80)
    ref = _multitone_reference(80, 80)
    p.tone_ground((0.45, 0.36, 0.22), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.warm_cool_zone_pass()
    surface = p.canvas.surface
    arr = np.frombuffer(surface.get_data(), dtype=np.uint8)
    assert arr.min() >= 0
    assert arr.max() <= 255


def test_s232_warm_cool_pass_warms_bright_zone():
    """Session 232: warm_cool_zone_pass should increase red in bright pixels."""
    p = _primed(64, 64, ref_rgb=(230, 220, 215))
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4).copy()
    p.warm_cool_zone_pass(warm_r_lift=0.08, warm_threshold=0.30, opacity=1.0)
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    warmed = (after[:, :, 2].astype(int) > before[:, :, 2].astype(int))
    assert warmed.sum() > 0, (
        "warm_cool_zone_pass should warm (increase red) highlight pixels")


def test_s232_warm_cool_pass_cools_dark_zone():
    """Session 232: warm_cool_zone_pass should increase blue in dark pixels."""
    p = _primed(64, 64, ref_rgb=(25, 22, 20))
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4).copy()
    p.warm_cool_zone_pass(cool_b_lift=0.08, cool_threshold=0.60, opacity=1.0)
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    cooled = (after[:, :, 0].astype(int) > before[:, :, 0].astype(int))
    assert cooled.sum() > 0, (
        "warm_cool_zone_pass should cool (increase blue) shadow pixels")


def test_s232_warm_cool_pass_opacity_zero_no_change():
    """Session 232: warm_cool_zone_pass at opacity=0 must not change canvas."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    p.warm_cool_zone_pass(opacity=0.0)
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        "warm_cool_zone_pass at opacity=0 should not change canvas")


def test_s232_warm_cool_pass_alpha_channel_preserved():
    """Session 232: warm_cool_zone_pass must not alter the alpha channel."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        64, 64, 4)[:, :, 3].copy()
    p.warm_cool_zone_pass()
    after_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        64, 64, 4)[:, :, 3]
    assert np.array_equal(before_alpha, after_alpha), (
        "warm_cool_zone_pass must not modify alpha channel")


def test_s232_warm_cool_pass_accepts_custom_params():
    """Session 232: warm_cool_zone_pass must accept all custom parameters."""
    p = _primed_grad(64, 64)
    p.warm_cool_zone_pass(
        warm_threshold=0.55,
        warm_ramp=0.15,
        warm_r_lift=0.05,
        warm_b_drop=0.03,
        cool_threshold=0.30,
        cool_ramp=0.15,
        cool_b_lift=0.05,
        cool_r_drop=0.025,
        cool_g_drop=0.010,
        opacity=0.60,
    )


def test_s232_warm_cool_pass_docstring_mentions_session():
    """Session 232: warm_cool_zone_pass docstring must mention session 232."""
    from stroke_engine import Painter
    doc = Painter.warm_cool_zone_pass.__doc__
    assert doc is not None
    assert "232" in doc, "Docstring should reference session 232"


def test_s232_warm_cool_pass_after_khnopff_pass():
    """Session 232: warm_cool_zone_pass must work after khnopff_frozen_reverie_pass."""
    p = _primed(64, 64, ref_rgb=(140, 140, 148))
    p.khnopff_frozen_reverie_pass()
    p.warm_cool_zone_pass()


# ─────────────────────────────────────────────────────────────────────────────
# Combined pipeline tests
# ─────────────────────────────────────────────────────────────────────────────

def test_s232_combined_khnopff_warm_cool_sequence():
    """Session 232: khnopff + warm_cool passes must run in sequence without error."""
    from stroke_engine import Painter
    p = Painter(80, 80)
    ref = _solid_reference(80, 80, rgb=(140, 140, 148))
    p.tone_ground((0.55, 0.56, 0.60), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.khnopff_frozen_reverie_pass()
    p.warm_cool_zone_pass()
    p.glaze((0.60, 0.62, 0.68), opacity=0.12)


def test_s232_full_pass_count():
    """Session 232: stroke_engine should have at least 333 pass methods."""
    from stroke_engine import Painter
    passes = [m for m in dir(Painter) if m.endswith('_pass')]
    assert len(passes) >= 332, (
        f"Expected >= 332 passes after session 232, found {len(passes)}")
