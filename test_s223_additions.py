"""
test_s223_additions.py — Session 223 tests for schjerfbeck_sparse_portrait_pass,
halation_glow_pass, and helene_schjerfbeck catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array([180, 150, 120], dtype=np.uint8)),
        "RGB")


# ──────────────────────────────────────────────────────────────────────────────
# schjerfbeck_sparse_portrait_pass — session 223 artist pass (134th mode)
# ──────────────────────────────────────────────────────────────────────────────

def test_s223_schjerfbeck_pass_exists():
    """Session 223: Painter must have schjerfbeck_sparse_portrait_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "schjerfbeck_sparse_portrait_pass"), (
        "Painter is missing schjerfbeck_sparse_portrait_pass")
    assert callable(getattr(Painter, "schjerfbeck_sparse_portrait_pass"))


def test_s223_schjerfbeck_pass_no_error():
    """Session 223: schjerfbeck_sparse_portrait_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.80, 0.77, 0.72), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.schjerfbeck_sparse_portrait_pass(
        dissolution_radius=0.40,
        dissolution_strength=0.70,
        flatten_sigma=3.0,
        flatten_strength=0.45,
        cool_shift=0.12,
        veil_opacity=0.08,
        opacity=0.78,
    )


def test_s223_schjerfbeck_pass_changes_canvas():
    """Session 223: schjerfbeck_sparse_portrait_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.80, 0.77, 0.72), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.schjerfbeck_sparse_portrait_pass(opacity=0.78)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "schjerfbeck_sparse_portrait_pass must change a non-uniform canvas"


def test_s223_schjerfbeck_pass_zero_opacity_no_change():
    """Session 223: schjerfbeck_sparse_portrait_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.78, 0.74, 0.68), texture_strength=0.05)
    p.block_in(ref, stroke_size=10, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.schjerfbeck_sparse_portrait_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "schjerfbeck_sparse_portrait_pass at opacity=0.0 must not change any pixels")


def test_s223_schjerfbeck_cool_wash_cools_bright_pixels():
    """Session 223: cool_shift must raise blue channel in bright regions."""
    p = _make_small_painter(64, 64)
    # Warm bright canvas so cool wash is detectable
    p.tone_ground((0.85, 0.80, 0.65), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    # BGRA: blue=channel 0, green=1, red=2
    before_blue = float(before[:, :, 0].mean())

    p.schjerfbeck_sparse_portrait_pass(
        cool_shift=0.40,           # exaggerate for detectability
        dissolution_strength=0.0,  # disable dissolution
        flatten_strength=0.0,      # disable flattening
        veil_opacity=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_blue = float(after[:, :, 0].mean())

    assert after_blue > before_blue, (
        f"cool_shift should raise blue channel on warm bright canvas; "
        f"before={before_blue:.1f} after={after_blue:.1f}")


def test_s223_helene_schjerfbeck_in_catalog():
    """Session 223: helene_schjerfbeck must appear in CATALOG with correct properties."""
    from art_catalog import CATALOG, get_style
    assert "helene_schjerfbeck" in CATALOG, "helene_schjerfbeck missing from CATALOG"
    s = get_style("helene_schjerfbeck")
    mv = s.movement.lower()
    assert "symbolism" in mv or "modernism" in mv or "finnish" in mv, (
        f"helene_schjerfbeck movement unexpected: {s.movement!r}")
    assert s.glazing is None, "helene_schjerfbeck glazing must be None"
    assert s.crackle is False, "helene_schjerfbeck crackle must be False"
    assert s.chromatic_split is False, "helene_schjerfbeck chromatic_split must be False"
    assert s.edge_softness >= 0.30, (
        f"helene_schjerfbeck edge_softness should be >= 0.30; got {s.edge_softness}")
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"
    assert len(s.famous_works) >= 5, (
        f"helene_schjerfbeck should have >= 5 famous works; got {len(s.famous_works)}")
    assert "134" in s.inspiration or "THIRTY-FOURTH" in s.inspiration, (
        "helene_schjerfbeck inspiration must reference 134th mode")


# ──────────────────────────────────────────────────────────────────────────────
# halation_glow_pass — session 223 artistic improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_s223_halation_glow_pass_exists():
    """Session 223: Painter must have halation_glow_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "halation_glow_pass"), (
        "Painter is missing halation_glow_pass")
    assert callable(getattr(Painter, "halation_glow_pass"))


def test_s223_halation_glow_pass_no_error():
    """Session 223: halation_glow_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.60, 0.55, 0.40), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.halation_glow_pass(
        threshold=0.75,
        bloom_sigma=0.04,
        bloom_intensity=0.35,
        opacity=0.65,
    )


def test_s223_halation_glow_pass_does_not_darken():
    """Session 223: halation_glow_pass must not darken any pixel (only adds bloom)."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.60, 0.55, 0.40), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.halation_glow_pass(threshold=0.50, bloom_sigma=0.06, bloom_intensity=0.40, opacity=1.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    # Bloom only adds; result must be >= original (allow tiny float rounding)
    diff = after[:, :, :3].astype(np.int32) - before[:, :, :3].astype(np.int32)
    assert diff.min() >= -2, (
        f"halation_glow_pass should not significantly darken any pixel; "
        f"min delta={diff.min()}")


def test_s223_halation_glow_pass_zero_opacity_no_change():
    """Session 223: halation_glow_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.70, 0.65, 0.50), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.halation_glow_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "halation_glow_pass at opacity=0.0 must not change any pixels")
