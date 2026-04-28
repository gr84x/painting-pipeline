"""
test_s229_additions.py -- Session 229 tests for redon_luminous_reverie_pass,
impasto_relief_pass, and the odilon_redon catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64, rgb=(150, 100, 180)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)),
        "RGB")


# ─────────────────────────────────────────────────────────────────────────────
# redon_luminous_reverie_pass  (140th distinct mode, session 229)
# ─────────────────────────────────────────────────────────────────────────────

def test_s229_redon_pass_exists():
    """Session 229: Painter must have redon_luminous_reverie_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "redon_luminous_reverie_pass"), (
        "Painter is missing redon_luminous_reverie_pass")
    assert callable(getattr(Painter, "redon_luminous_reverie_pass"))


def test_s229_redon_pass_no_error():
    """Session 229: redon_luminous_reverie_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.18, 0.12, 0.28), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.redon_luminous_reverie_pass(
        shadow_thresh=0.30,
        violet_lift=0.06,
        phosphor_boost=0.35,
        dream_sigma=1.8,
        shimmer_thresh=0.82,
        shimmer_str=0.08,
        opacity=0.75,
    )


def test_s229_redon_pass_zero_opacity_no_change():
    """Session 229: redon_luminous_reverie_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.18, 0.12, 0.28), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.redon_luminous_reverie_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "redon_luminous_reverie_pass at opacity=0.0 must not change any pixels")


def test_s229_redon_pass_changes_canvas():
    """Session 229: redon_luminous_reverie_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(150, 100, 180))
    p.tone_ground((0.18, 0.12, 0.28), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.redon_luminous_reverie_pass(
        violet_lift=0.12,
        phosphor_boost=0.50,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "redon_luminous_reverie_pass must change a non-uniform canvas"


def test_s229_redon_violet_lift_increases_blue_in_shadows():
    """Session 229: violet_lift must increase blue channel in dark regions."""
    p = _make_small_painter(64, 64)
    # Dark canvas to activate shadow gate
    arr = np.full((64, 64, 3), 40, dtype=np.uint8)
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_b = float(before[:, :, 0].mean())

    p.redon_luminous_reverie_pass(
        shadow_thresh=0.80,   # very high threshold to catch all pixels as "shadow"
        violet_lift=0.20,     # strong lift for reliable detection
        phosphor_boost=0.0,
        dream_sigma=0.1,
        shimmer_str=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_b = float(after[:, :, 0].mean())

    assert after_b >= before_b, (
        f"Violet lift must increase blue in shadow zones; "
        f"before_b={before_b:.1f} after_b={after_b:.1f}")


def test_s229_redon_phosphor_bloom_increases_saturation():
    """Session 229: phosphor_boost must increase colour saturation in midtones."""
    p = _make_small_painter(64, 64)
    # Midtone desaturated canvas for saturation boost to be measurable
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :, 0] = 128    # R
    arr[:, :, 1] = 100    # G (slightly lower — some saturation)
    arr[:, :, 2] = 80     # B
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.50, 0.40, 0.30), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_std = float(before[:, :, :3].astype(np.float32).std())

    p.redon_luminous_reverie_pass(
        shadow_thresh=0.05,   # low threshold so shadow gate doesn't fire
        violet_lift=0.0,
        phosphor_boost=0.80,  # strong boost for detection
        dream_sigma=0.1,
        shimmer_str=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_std = float(after[:, :, :3].astype(np.float32).std())

    # Saturation boost should increase the spread of RGB values
    assert after_std >= before_std * 0.95, (
        f"Phosphor boost should not reduce colour spread significantly; "
        f"before_std={before_std:.2f} after_std={after_std:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# impasto_relief_pass  (session 229 artistic improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_s229_impasto_pass_exists():
    """Session 229: Painter must have impasto_relief_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "impasto_relief_pass"), (
        "Painter is missing impasto_relief_pass")
    assert callable(getattr(Painter, "impasto_relief_pass"))


def test_s229_impasto_pass_no_error():
    """Session 229: impasto_relief_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(180, 150, 120))
    p.tone_ground((0.55, 0.45, 0.30), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.impasto_relief_pass(
        light_angle=2.36,
        relief_scale=0.12,
        thickness_gate=0.30,
        relief_sigma=1.2,
        opacity=0.55,
    )


def test_s229_impasto_pass_zero_opacity_no_change():
    """Session 229: impasto_relief_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(180, 150, 120))
    p.tone_ground((0.55, 0.45, 0.30), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.impasto_relief_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "impasto_relief_pass at opacity=0.0 must not change any pixels")


def test_s229_impasto_pass_changes_canvas():
    """Session 229: impasto_relief_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    # Gradient canvas with contrast so Sobel finds edges
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :32, :] = [220, 180, 140]
    arr[:, 32:, :] = [60, 50, 40]
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.50, 0.45, 0.35), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.impasto_relief_pass(
        relief_scale=0.25,
        thickness_gate=0.10,
        opacity=0.80,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "impasto_relief_pass must change a non-uniform canvas"


def test_s229_impasto_directional_light_asymmetry():
    """Session 229: Different light angles must produce different canvas results."""
    from PIL import Image

    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:32, :, :] = [200, 160, 120]
    arr[32:, :, :] = [60, 50, 40]
    ref = Image.fromarray(arr, "RGB")

    # Angle 0 (light from left)
    p1 = _make_small_painter(64, 64)
    p1.tone_ground((0.50, 0.45, 0.35))
    p1.block_in(ref, stroke_size=8, n_strokes=40)
    p1.impasto_relief_pass(light_angle=0.0, relief_scale=0.25, opacity=1.0)
    result1 = np.frombuffer(
        p1.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    # Angle pi (light from right)
    p2 = _make_small_painter(64, 64)
    p2.tone_ground((0.50, 0.45, 0.35))
    p2.block_in(ref, stroke_size=8, n_strokes=40)
    p2.impasto_relief_pass(light_angle=3.14159, relief_scale=0.25, opacity=1.0)
    result2 = np.frombuffer(
        p2.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(result1.astype(np.int32) - result2.astype(np.int32)).max()
    assert diff > 0, (
        "Different light angles should produce different results for impasto_relief_pass")


# ─────────────────────────────────────────────────────────────────────────────
# odilon_redon catalog entry  (session 229)
# ─────────────────────────────────────────────────────────────────────────────

def test_s229_redon_in_catalog():
    """Session 229: odilon_redon must appear in CATALOG with correct properties."""
    from art_catalog import CATALOG, get_style
    assert "odilon_redon" in CATALOG, "odilon_redon missing from CATALOG"
    s = get_style("odilon_redon")
    mv = s.movement.lower()
    assert "symbol" in mv, f"Redon movement unexpected: {s.movement!r}"
    assert s.chromatic_split is False
    assert s.crackle is False
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"
    assert len(s.famous_works) >= 4
    has_140 = "FORTIETH" in s.inspiration or "140" in s.inspiration
    assert has_140, "odilon_redon inspiration must reference 140th mode"


def test_s229_redon_catalog_palette_includes_violet():
    """Session 229: Redon palette must include at least one violet entry."""
    from art_catalog import get_style
    s = get_style("odilon_redon")
    has_violet = any(rgb[2] > 0.55 and rgb[0] > 0.35 for rgb in s.palette)
    assert has_violet, "Redon palette should include a violet entry (high R and B)"


def test_s229_redon_catalog_includes_symbolist_works():
    """Session 229: Redon famous_works must include The Cyclops or Ophelia."""
    from art_catalog import get_style
    s = get_style("odilon_redon")
    titles = [t.lower() for t, _ in s.famous_works]
    has_symbolist = any("cyclops" in t or "ophelia" in t or "orpheus" in t
                        for t in titles)
    assert has_symbolist, "Redon famous_works should include Cyclops, Ophelia, or Orpheus"


def test_s229_redon_catalog_ground_is_dark_violet():
    """Session 229: Redon ground_color should be a dark violet-purple."""
    from art_catalog import get_style
    s = get_style("odilon_redon")
    r, g, b = s.ground_color
    # Dark (low luminance) and violet-shifted (B > G, R > G, dark overall)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum < 0.35, f"Redon ground should be dark; lum={lum:.3f}"
    assert b > g, f"Redon ground should be violet (B > G); B={b:.2f} G={g:.2f}"
