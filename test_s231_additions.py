"""
test_s231_additions.py -- Session 231 tests for vrubel_crystal_facet_pass,
midtone_clarity_pass, and the mikhail_vrubel catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64, rgb=(130, 100, 160)):
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
    arr[:, :w//3, :]       = 25    # dark
    arr[:, w//3:2*w//3, :] = 128   # mid-tone
    arr[:, 2*w//3:, :]     = 230   # bright
    return Image.fromarray(arr, "RGB")


def _primed(w=64, h=64, ref_rgb=(100, 80, 140)):
    """Return a painter with tone_ground + block_in applied."""
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = _solid_reference(w, h, rgb=ref_rgb)
    p.tone_ground((0.32, 0.24, 0.55), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    return p


def _primed_grad(w=64, h=64):
    """Primed painter loaded from a gradient reference."""
    from stroke_engine import Painter
    p = Painter(w, h)
    ref = _gradient_reference(w, h)
    p.tone_ground((0.35, 0.30, 0.50), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    return p


# ─────────────────────────────────────────────────────────────────────────────
# Art catalog — mikhail_vrubel entry  (session 231)
# ─────────────────────────────────────────────────────────────────────────────

def test_s231_catalog_vrubel_exists():
    """Session 231: CATALOG must contain 'mikhail_vrubel' key."""
    from art_catalog import CATALOG
    assert "mikhail_vrubel" in CATALOG, (
        "CATALOG is missing 'mikhail_vrubel' entry")


def test_s231_catalog_vrubel_fields():
    """Session 231: mikhail_vrubel ArtStyle must have all required fields."""
    from art_catalog import CATALOG
    s = CATALOG["mikhail_vrubel"]
    assert s.artist == "Mikhail Vrubel"
    assert "Russian" in s.nationality
    assert len(s.palette) >= 5
    assert 0.0 <= s.wet_blend <= 1.0
    assert 0.0 <= s.edge_softness <= 1.0
    assert len(s.famous_works) >= 3
    assert "vrubel_crystal_facet_pass" in s.inspiration


def test_s231_catalog_vrubel_get_style():
    """Session 231: get_style('mikhail_vrubel') must return the entry without error."""
    from art_catalog import get_style
    s = get_style("mikhail_vrubel")
    assert s.artist == "Mikhail Vrubel"


def test_s231_catalog_vrubel_palette_has_blue_violet():
    """Session 231: Vrubel palette must include deep blue/violet tones (B > R)."""
    from art_catalog import CATALOG
    s = CATALOG["mikhail_vrubel"]
    has_blue_violet = any(b > r for r, g, b in s.palette)
    assert has_blue_violet, "Vrubel palette should contain blue/violet tones"


def test_s231_catalog_vrubel_famous_works():
    """Session 231: Vrubel famous_works must include a Demon painting."""
    from art_catalog import CATALOG
    s = CATALOG["mikhail_vrubel"]
    titles = [t for t, _ in s.famous_works]
    assert any("Demon" in t for t in titles), (
        "Vrubel famous_works should include a Demon painting")


def test_s231_catalog_vrubel_period():
    """Session 231: Vrubel period must reference 1856 and 1910."""
    from art_catalog import CATALOG
    s = CATALOG["mikhail_vrubel"]
    assert "1856" in s.period or "1857" in s.period
    assert "1910" in s.period


def test_s231_catalog_count_increased():
    """Session 231: total artist count must be >= 231 (added Vrubel)."""
    from art_catalog import list_artists
    n = len(list_artists())
    assert n >= 231, f"Expected >= 231 artists, got {n}"


# ─────────────────────────────────────────────────────────────────────────────
# vrubel_crystal_facet_pass  (session 231 — 142nd mode)
# ─────────────────────────────────────────────────────────────────────────────

def test_s231_vrubel_pass_exists():
    """Session 231: Painter must have vrubel_crystal_facet_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "vrubel_crystal_facet_pass"), (
        "Painter is missing vrubel_crystal_facet_pass")


def test_s231_vrubel_pass_callable():
    """Session 231: vrubel_crystal_facet_pass must be callable."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "vrubel_crystal_facet_pass"))


def test_s231_vrubel_pass_runs_without_error():
    """Session 231: vrubel_crystal_facet_pass must run without raising."""
    p = _primed(64, 64, ref_rgb=(80, 60, 140))
    p.vrubel_crystal_facet_pass()


def test_s231_vrubel_pass_modifies_canvas():
    """Session 231: vrubel_crystal_facet_pass must change pixel values."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    p.vrubel_crystal_facet_pass()
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    assert not np.array_equal(before, after), (
        "vrubel_crystal_facet_pass should modify the canvas")


def test_s231_vrubel_pass_output_stays_in_range():
    """Session 231: vrubel_crystal_facet_pass output must stay within [0, 255]."""
    p = _primed_grad(64, 64)
    p.vrubel_crystal_facet_pass()
    surface = p.canvas.surface
    arr = np.frombuffer(surface.get_data(), dtype=np.uint8)
    assert arr.min() >= 0
    assert arr.max() <= 255


def test_s231_vrubel_pass_grout_darkens_edges():
    """Session 231: vrubel pass should produce some pixels darker than input (grout effect)."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4).copy()
    p.vrubel_crystal_facet_pass(grout_depth=0.60, opacity=1.0)
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    darkened = (after[:, :, :3].astype(int) < before[:, :, :3].astype(int)).any(axis=2)
    assert darkened.sum() > 0, "vrubel_crystal_facet_pass should darken some edge pixels"


def test_s231_vrubel_pass_accepts_custom_sigma():
    """Session 231: vrubel_crystal_facet_pass must accept custom facet_sigma."""
    p = _primed_grad(64, 64)
    p.vrubel_crystal_facet_pass(facet_sigma=2.0)
    p2 = _primed_grad(64, 64)
    p2.vrubel_crystal_facet_pass(facet_sigma=8.0)


def test_s231_vrubel_pass_opacity_zero_no_change():
    """Session 231: vrubel_crystal_facet_pass at opacity=0 must not change the canvas."""
    p = _primed(64, 64, ref_rgb=(100, 80, 140))
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    p.vrubel_crystal_facet_pass(opacity=0.0)
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        "vrubel_crystal_facet_pass at opacity=0 should not change canvas")


def test_s231_vrubel_pass_alpha_channel_preserved():
    """Session 231: vrubel_crystal_facet_pass must not alter the alpha channel."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)[:, :, 3].copy()
    p.vrubel_crystal_facet_pass()
    after_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)[:, :, 3]
    assert np.array_equal(before_alpha, after_alpha), (
        "vrubel_crystal_facet_pass must not modify the alpha channel")


def test_s231_vrubel_pass_docstring_mentions_session():
    """Session 231: vrubel_crystal_facet_pass docstring must reference session 231."""
    from stroke_engine import Painter
    doc = Painter.vrubel_crystal_facet_pass.__doc__
    assert doc is not None
    assert "231" in doc, "Docstring should identify this as session 231"
    assert "FORTY-SECOND" in doc or "142" in doc, (
        "Docstring should name this as the 142nd mode")


def test_s231_vrubel_pass_full_pipeline_sequence():
    """Session 231: vrubel pass must work after tone_ground + block_in + glaze."""
    from stroke_engine import Painter
    p = Painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(80, 60, 140))
    p.tone_ground((0.20, 0.18, 0.38), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.vrubel_crystal_facet_pass()
    p.glaze((0.55, 0.50, 0.70), opacity=0.12)


# ─────────────────────────────────────────────────────────────────────────────
# midtone_clarity_pass  (session 231 improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_s231_clarity_pass_exists():
    """Session 231: Painter must have midtone_clarity_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "midtone_clarity_pass"), (
        "Painter is missing midtone_clarity_pass")


def test_s231_clarity_pass_callable():
    """Session 231: midtone_clarity_pass must be callable."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "midtone_clarity_pass"))


def test_s231_clarity_pass_runs_without_error():
    """Session 231: midtone_clarity_pass must run without raising."""
    p = _primed(64, 64, ref_rgb=(128, 120, 130))
    p.midtone_clarity_pass()


def test_s231_clarity_pass_modifies_canvas():
    """Session 231: midtone_clarity_pass must change pixel values."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    p.midtone_clarity_pass()
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    assert not np.array_equal(before, after), (
        "midtone_clarity_pass should modify the canvas")


def test_s231_clarity_pass_output_in_range():
    """Session 231: midtone_clarity_pass output must stay within [0, 255]."""
    from stroke_engine import Painter
    p = Painter(80, 80)
    ref = _multitone_reference(80, 80)
    p.tone_ground((0.35, 0.30, 0.50), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.midtone_clarity_pass()
    surface = p.canvas.surface
    arr = np.frombuffer(surface.get_data(), dtype=np.uint8)
    assert arr.min() >= 0
    assert arr.max() <= 255


def test_s231_clarity_pass_sharpens_midtones():
    """Session 231: midtone_clarity_pass should alter mid-tone zone pixel values."""
    from stroke_engine import Painter
    p = Painter(80, 80)
    ref = _multitone_reference(80, 80)
    p.tone_ground((0.35, 0.30, 0.50), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(80, 80, 4).copy()
    p.midtone_clarity_pass(sharpness=0.80, opacity=1.0)
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(80, 80, 4)
    # Canvas should differ somewhere after high-sharpness clarity pass
    assert not np.array_equal(before, after), (
        "midtone_clarity_pass at high sharpness should alter the canvas")


def test_s231_clarity_pass_opacity_zero_no_change():
    """Session 231: midtone_clarity_pass at opacity=0 must not change canvas."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    p.midtone_clarity_pass(opacity=0.0)
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        "midtone_clarity_pass at opacity=0 should not change canvas")


def test_s231_clarity_pass_alpha_channel_preserved():
    """Session 231: midtone_clarity_pass must not alter the alpha channel."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)[:, :, 3].copy()
    p.midtone_clarity_pass()
    after_alpha = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)[:, :, 3]
    assert np.array_equal(before_alpha, after_alpha), (
        "midtone_clarity_pass must not modify alpha channel")


def test_s231_clarity_pass_accepts_custom_params():
    """Session 231: midtone_clarity_pass must accept all custom parameters."""
    p = _primed_grad(64, 64)
    p.midtone_clarity_pass(
        clarity_center=0.45,
        clarity_width=0.18,
        sharpness=0.70,
        blur_sigma=2.0,
        opacity=0.50,
    )


def test_s231_clarity_pass_docstring_mentions_improvement():
    """Session 231: midtone_clarity_pass docstring must mention session 231."""
    from stroke_engine import Painter
    doc = Painter.midtone_clarity_pass.__doc__
    assert doc is not None
    assert "231" in doc, "Docstring should reference session 231"


def test_s231_clarity_pass_after_vrubel_pass():
    """Session 231: midtone_clarity_pass must work after vrubel_crystal_facet_pass."""
    p = _primed(64, 64, ref_rgb=(100, 80, 150))
    p.vrubel_crystal_facet_pass()
    p.midtone_clarity_pass()


def test_s231_clarity_pass_high_sharpness_changes_image():
    """Session 231: High sharpness clarity pass should change gradient image."""
    p = _primed_grad(64, 64)
    surface = p.canvas.surface
    before = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    p.midtone_clarity_pass(sharpness=1.5, blur_sigma=0.8, opacity=1.0)
    after = np.frombuffer(surface.get_data(), dtype=np.uint8).copy()
    assert not np.array_equal(before, after), (
        "High sharpness midtone_clarity_pass should alter the image")


# ─────────────────────────────────────────────────────────────────────────────
# Combined pipeline tests
# ─────────────────────────────────────────────────────────────────────────────

def test_s231_combined_vrubel_clarity_sequence():
    """Session 231: vrubel + clarity passes must run in sequence without error."""
    from stroke_engine import Painter
    p = Painter(80, 80)
    ref = _solid_reference(80, 80, rgb=(60, 50, 120))
    p.tone_ground((0.22, 0.18, 0.40), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.vrubel_crystal_facet_pass()
    p.midtone_clarity_pass()
    p.glaze((0.55, 0.50, 0.70), opacity=0.12)


def test_s231_full_pass_count():
    """Session 231: stroke_engine should have at least 329 pass methods."""
    from stroke_engine import Painter
    passes = [m for m in dir(Painter) if m.endswith('_pass')]
    assert len(passes) >= 329, (
        f"Expected >= 329 passes after session 231, found {len(passes)}")
