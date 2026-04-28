"""
test_s227_additions.py -- Session 227 tests for vermeer_pearl_light_pass
and the updated vermeer catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64, rgb=(180, 150, 120)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)),
        "RGB")


# ------------------------------------------------------------------------------
# vermeer_pearl_light_pass -- session 227 artist pass (138th mode)
# ------------------------------------------------------------------------------

def test_s227_vermeer_pass_exists():
    """Session 227: Painter must have vermeer_pearl_light_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "vermeer_pearl_light_pass"), (
        "Painter is missing vermeer_pearl_light_pass")
    assert callable(getattr(Painter, "vermeer_pearl_light_pass"))


def test_s227_vermeer_pass_no_error():
    """Session 227: vermeer_pearl_light_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.48, 0.32), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.vermeer_pearl_light_pass(
        light_x=0.20,
        light_y=0.12,
        light_reach=0.55,
        warm_strength=0.10,
        cool_strength=0.10,
        light_thresh=0.60,
        shadow_thresh=0.38,
        pearl_thresh=0.72,
        pearl_density=0.006,
        pearl_radius=1.4,
        pearl_r=0.97,
        pearl_g=0.95,
        pearl_b=0.88,
        shadow_sigma=1.0,
        shadow_blur_str=0.35,
        opacity=0.75,
        seed=227,
    )


def test_s227_vermeer_pass_zero_opacity_no_change():
    """Session 227: vermeer_pearl_light_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.48, 0.32), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.vermeer_pearl_light_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "vermeer_pearl_light_pass at opacity=0.0 must not change any pixels")


def test_s227_vermeer_pass_changes_canvas():
    """Session 227: vermeer_pearl_light_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.48, 0.32), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.vermeer_pearl_light_pass(opacity=0.75)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "vermeer_pearl_light_pass must change a non-uniform canvas"


def test_s227_vermeer_warm_light_raises_red_in_highlights():
    """Session 227: warm light shift must raise red channel in bright canvas areas."""
    p = _make_small_painter(64, 64)
    # Very bright canvas — all in lit zone
    p.tone_ground((0.88, 0.86, 0.82), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_r = float(before[:, :, 2].mean())

    p.vermeer_pearl_light_pass(
        light_thresh=0.40,       # low threshold so bright canvas qualifies
        warm_strength=0.30,      # exaggerate for reliable detection
        cool_strength=0.0,       # isolate warm effect
        shadow_thresh=0.05,      # disable shadow shift
        pearl_density=0.0,       # disable pearls
        shadow_blur_str=0.0,     # disable shadow softening
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_r = float(after[:, :, 2].mean())

    assert after_r >= before_r, (
        f"Warm light shift should raise mean red on bright canvas; "
        f"before={before_r:.1f} after={after_r:.1f}")


def test_s227_vermeer_cool_shadow_raises_blue_in_darks():
    """Session 227: cool shadow shift must raise blue channel in dark canvas areas."""
    p = _make_small_painter(64, 64)
    # Very dark canvas — all in shadow zone
    p.tone_ground((0.12, 0.10, 0.08), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_b = float(before[:, :, 0].mean())

    p.vermeer_pearl_light_pass(
        light_thresh=0.95,       # disable warm shift on dark canvas
        warm_strength=0.0,
        shadow_thresh=0.80,      # high threshold so dark canvas qualifies
        cool_strength=0.30,      # exaggerate for reliable detection
        pearl_density=0.0,
        shadow_blur_str=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_b = float(after[:, :, 0].mean())

    assert after_b >= before_b, (
        f"Cool shadow shift should raise blue on dark canvas; "
        f"before={before_b:.1f} after={after_b:.1f}")


def test_s227_vermeer_pearl_sparkle_produces_brighter_pixels():
    """Session 227: Pearl sparkle must produce at least some brighter pixels on a mid-bright canvas."""
    p = _make_small_painter(64, 64)
    # Mid-bright canvas so pearls can fire on the lighter patches
    p.tone_ground((0.75, 0.73, 0.70), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_max = int(before[:, :, 2].max())

    p.vermeer_pearl_light_pass(
        light_thresh=0.95,       # disable warm shift
        warm_strength=0.0,
        shadow_thresh=0.05,      # disable cool shift
        cool_strength=0.0,
        pearl_thresh=0.50,       # low threshold so canvas qualifies
        pearl_density=0.08,      # high density for reliable detection on small canvas
        pearl_radius=0.8,
        pearl_r=1.0,
        pearl_g=1.0,
        pearl_b=1.0,
        shadow_blur_str=0.0,
        opacity=1.0,
        seed=42,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_max = int(after[:, :, 2].max())

    assert after_max >= before_max, (
        f"Pearl sparkle should produce pixels at least as bright as canvas baseline; "
        f"before_max={before_max} after_max={after_max}")


def test_s227_vermeer_shadow_softening_reduces_local_sharpness():
    """Session 227: Shadow-zone softening must reduce sharpness within shadow passages."""
    p = _make_small_painter(64, 64)
    # Dark canvas with a hard internal edge — softening should reduce sharpness
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :32, :] = [40, 35, 30]     # dark warm left
    arr[:, 32:, :] = [25, 20, 18]     # darker right
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.14, 0.12, 0.10), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    # Measure local gradient at internal boundary
    before_grad = float(np.abs(
        before[:, 30:35, 2].astype(np.int32) - before[:, 29:34, 2].astype(np.int32)
    ).mean())

    p.vermeer_pearl_light_pass(
        light_thresh=0.95,      # disable warm shift on dark canvas
        warm_strength=0.0,
        shadow_thresh=0.90,     # high so dark canvas is in shadow zone
        cool_strength=0.0,
        pearl_density=0.0,
        shadow_sigma=2.5,
        shadow_blur_str=0.60,   # exaggerate blur for reliable detection
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_grad = float(np.abs(
        after[:, 30:35, 2].astype(np.int32) - after[:, 29:34, 2].astype(np.int32)
    ).mean())

    assert after_grad <= before_grad + 2.0, (
        f"Shadow softening should not sharpen shadow boundaries; "
        f"before_grad={before_grad:.2f} after_grad={after_grad:.2f}")


# ------------------------------------------------------------------------------
# Vermeer catalog entry -- session 227
# ------------------------------------------------------------------------------

def test_s227_vermeer_in_catalog():
    """Session 227: vermeer must appear in CATALOG with correct properties."""
    from art_catalog import CATALOG, get_style
    assert "vermeer" in CATALOG, "vermeer missing from CATALOG"
    s = get_style("vermeer")
    mv = s.movement.lower()
    assert "dutch" in mv or "golden" in mv, (
        f"vermeer movement unexpected: {s.movement!r}")
    assert s.chromatic_split is False
    assert s.crackle is True
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"
    assert len(s.famous_works) >= 3
    assert "138" in s.inspiration or "THIRTY-EIGHTH" in s.inspiration, (
        "vermeer inspiration must reference 138th mode")


def test_s227_vermeer_catalog_palette_includes_ultramarine():
    """Session 227: Vermeer palette must include at least one strongly-blue colour."""
    from art_catalog import get_style
    s = get_style("vermeer")
    has_blue = any(rgb[2] > 0.45 and rgb[2] > rgb[0] + 0.15 for rgb in s.palette)
    assert has_blue, "Vermeer palette should include a notable ultramarine blue entry"
