"""
test_s224_additions.py -- Session 224 tests for serov_sunlit_portrait_pass,
color_temperature_oscillation_pass, and valentin_serov catalog entry.
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


# ------------------------------------------------------------------------------
# serov_sunlit_portrait_pass -- session 224 artist pass (135th mode)
# ------------------------------------------------------------------------------

def test_s224_serov_pass_exists():
    """Session 224: Painter must have serov_sunlit_portrait_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "serov_sunlit_portrait_pass"), (
        "Painter is missing serov_sunlit_portrait_pass")
    assert callable(getattr(Painter, "serov_sunlit_portrait_pass"))


def test_s224_serov_pass_no_error():
    """Session 224: serov_sunlit_portrait_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.84, 0.80, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.serov_sunlit_portrait_pass(
        warm_shift=0.22,
        cool_shift=0.18,
        highlight_thresh=0.65,
        shadow_thresh=0.40,
        luminosity_lift=0.06,
        vibration_strength=0.04,
        opacity=0.80,
    )


def test_s224_serov_pass_changes_canvas():
    """Session 224: serov_sunlit_portrait_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.84, 0.80, 0.70), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.serov_sunlit_portrait_pass(opacity=0.80)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "serov_sunlit_portrait_pass must change a non-uniform canvas"


def test_s224_serov_pass_zero_opacity_no_change():
    """Session 224: serov_sunlit_portrait_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.78, 0.74, 0.68), texture_strength=0.05)
    p.block_in(ref, stroke_size=10, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.serov_sunlit_portrait_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "serov_sunlit_portrait_pass at opacity=0.0 must not change any pixels")


def test_s224_serov_warm_shift_warms_highlights():
    """Session 224: warm_shift must shift bright pixels toward warm peach-amber (raise red)."""
    p = _make_small_painter(64, 64)
    # Cool-neutral bright canvas so warming is detectable
    p.tone_ground((0.78, 0.78, 0.78), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    # BGRA: blue=ch0, green=ch1, red=ch2
    before_red = float(before[:, :, 2].mean())

    p.serov_sunlit_portrait_pass(
        warm_shift=0.50,          # exaggerate for detectability
        cool_shift=0.0,           # disable shadow cooling
        highlight_thresh=0.50,    # lower threshold so uniform canvas qualifies
        luminosity_lift=0.0,
        vibration_strength=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_red = float(after[:, :, 2].mean())

    assert after_red > before_red, (
        f"warm_shift should raise red channel on bright neutral canvas; "
        f"before={before_red:.1f} after={after_red:.1f}")


def test_s224_serov_cool_shift_cools_shadows():
    """Session 224: cool_shift must shift dark pixels toward blue-violet (raise blue channel)."""
    p = _make_small_painter(64, 64)
    # Warm dark canvas so cool shadow shift is detectable
    p.tone_ground((0.22, 0.16, 0.08), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_blue = float(before[:, :, 0].mean())

    p.serov_sunlit_portrait_pass(
        warm_shift=0.0,
        cool_shift=0.50,          # exaggerate
        shadow_thresh=0.60,       # raise threshold so dark canvas qualifies
        luminosity_lift=0.0,
        vibration_strength=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_blue = float(after[:, :, 0].mean())

    assert after_blue > before_blue, (
        f"cool_shift should raise blue channel on dark warm canvas; "
        f"before={before_blue:.1f} after={after_blue:.1f}")


def test_s224_valentin_serov_in_catalog():
    """Session 224: valentin_serov must appear in CATALOG with correct properties."""
    from art_catalog import CATALOG, get_style
    assert "valentin_serov" in CATALOG, "valentin_serov missing from CATALOG"
    s = get_style("valentin_serov")
    mv = s.movement.lower()
    assert "russian" in mv or "impressionism" in mv, (
        f"valentin_serov movement unexpected: {s.movement!r}")
    assert s.glazing is None, "valentin_serov glazing must be None"
    assert s.crackle is False, "valentin_serov crackle must be False"
    assert s.chromatic_split is False, "valentin_serov chromatic_split must be False"
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"
    assert len(s.famous_works) >= 5, (
        f"valentin_serov should have >= 5 famous works; got {len(s.famous_works)}")
    assert "135" in s.inspiration or "THIRTY-FIFTH" in s.inspiration, (
        "valentin_serov inspiration must reference 135th mode")


# ------------------------------------------------------------------------------
# color_temperature_oscillation_pass -- session 224 artistic improvement
# ------------------------------------------------------------------------------

def test_s224_color_temp_oscillation_pass_exists():
    """Session 224: Painter must have color_temperature_oscillation_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "color_temperature_oscillation_pass"), (
        "Painter is missing color_temperature_oscillation_pass")
    assert callable(getattr(Painter, "color_temperature_oscillation_pass"))


def test_s224_color_temp_oscillation_pass_no_error():
    """Session 224: color_temperature_oscillation_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.65, 0.58, 0.42), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.color_temperature_oscillation_pass(
        highlight_gate=0.72,
        shadow_gate=0.35,
        strength=0.18,
        opacity=0.75,
    )


def test_s224_color_temp_oscillation_zero_opacity_no_change():
    """Session 224: color_temperature_oscillation_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.70, 0.65, 0.50), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.color_temperature_oscillation_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "color_temperature_oscillation_pass at opacity=0.0 must not change any pixels")


def test_s224_color_temp_oscillation_warms_highlights():
    """Session 224: oscillation pass must increase red channel on a very bright canvas."""
    p = _make_small_painter(64, 64)
    # Neutral-cool very bright canvas
    p.tone_ground((0.88, 0.88, 0.92), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_red = float(before[:, :, 2].mean())

    p.color_temperature_oscillation_pass(
        warm_highlight_r=1.00,
        warm_highlight_g=0.70,
        warm_highlight_b=0.50,   # very warm target for detectability
        highlight_gate=0.60,     # lower gate so bright canvas qualifies
        shadow_gate=0.20,
        strength=0.50,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_red = float(after[:, :, 2].mean())

    assert after_red > before_red, (
        f"oscillation pass should raise red on bright canvas for warm highlight zone; "
        f"before={before_red:.1f} after={after_red:.1f}")


def test_s224_color_temp_oscillation_changes_canvas():
    """Session 224: color_temperature_oscillation_pass must visibly change canvas with strength>0."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.60, 0.55, 0.40), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.color_temperature_oscillation_pass(strength=0.50, opacity=1.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "color_temperature_oscillation_pass must change a non-uniform canvas"
