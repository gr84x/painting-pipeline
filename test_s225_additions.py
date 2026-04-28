"""
test_s225_additions.py -- Session 225 tests for segantini_stitch_weave_pass,
alpine_luminance_intensification_pass, and giovanni_segantini catalog entry.
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
# segantini_stitch_weave_pass -- session 225 artist pass (136th mode)
# ------------------------------------------------------------------------------

def test_s225_segantini_pass_exists():
    """Session 225: Painter must have segantini_stitch_weave_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "segantini_stitch_weave_pass"), (
        "Painter is missing segantini_stitch_weave_pass")
    assert callable(getattr(Painter, "segantini_stitch_weave_pass"))


def test_s225_segantini_pass_no_error():
    """Session 225: segantini_stitch_weave_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.90, 0.88, 0.82), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.segantini_stitch_weave_pass(
        stitch_density=12.0,
        weave_strength=0.14,
        warm_target_r=0.84,
        warm_target_g=0.70,
        warm_target_b=0.32,
        cool_target_r=0.52,
        cool_target_g=0.72,
        cool_target_b=0.90,
        saturation_boost=0.10,
        opacity=0.78,
    )


def test_s225_segantini_pass_changes_canvas():
    """Session 225: segantini_stitch_weave_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.90, 0.88, 0.82), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.segantini_stitch_weave_pass(opacity=0.78)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "segantini_stitch_weave_pass must change a non-uniform canvas"


def test_s225_segantini_pass_zero_opacity_no_change():
    """Session 225: segantini_stitch_weave_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.86, 0.80), texture_strength=0.05)
    p.block_in(ref, stroke_size=10, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.segantini_stitch_weave_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "segantini_stitch_weave_pass at opacity=0.0 must not change any pixels")


def test_s225_segantini_warm_target_shifts_red():
    """Session 225: Stitch weave must visibly change individual pixels on a uniform canvas."""
    p = _make_small_painter(64, 64)
    # Neutral mid-tone canvas — stitch pattern produces warm/cool pixel alternation
    p.tone_ground((0.55, 0.55, 0.55), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    p.segantini_stitch_weave_pass(
        stitch_density=8.0,
        weave_strength=0.50,          # exaggerate for detectability
        warm_target_r=1.00,
        warm_target_g=0.50,
        warm_target_b=0.10,
        cool_target_r=0.10,
        cool_target_g=0.50,
        cool_target_b=1.00,
        saturation_boost=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    # Warm (R=1.0) and cool (R=0.1) stripes cancel in mean but individual pixels differ;
    # max per-pixel difference on the red channel must be substantial (stitch stripes visible)
    max_diff = int(np.abs(after[:, :, 2].astype(np.int32) - before[:, :, 2].astype(np.int32)).max())
    assert max_diff > 10, (
        f"segantini_stitch_weave_pass weave_strength=0.50 must visibly shift individual pixels; "
        f"max_per_pixel_red_diff={max_diff}")


def test_s225_segantini_saturation_boost_increases_chroma():
    """Session 225: saturation_boost>0 must increase chroma range on a coloured canvas."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.52, 0.38, 0.24), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=25)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    r0 = before[:, :, 2].astype(np.float32) / 255.0
    g0 = before[:, :, 1].astype(np.float32) / 255.0
    b0 = before[:, :, 0].astype(np.float32) / 255.0
    # Chroma range = max - min across channels per pixel
    chroma_before = (np.maximum(np.maximum(r0, g0), b0) - np.minimum(np.minimum(r0, g0), b0)).mean()

    p.segantini_stitch_weave_pass(
        weave_strength=0.0,       # disable weave oscillation
        saturation_boost=0.40,    # exaggerate saturation lift
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    r1 = after[:, :, 2].astype(np.float32) / 255.0
    g1 = after[:, :, 1].astype(np.float32) / 255.0
    b1 = after[:, :, 0].astype(np.float32) / 255.0
    chroma_after = (np.maximum(np.maximum(r1, g1), b1) - np.minimum(np.minimum(r1, g1), b1)).mean()

    assert chroma_after >= chroma_before, (
        f"saturation_boost should not decrease mean chroma; "
        f"before={chroma_before:.4f} after={chroma_after:.4f}")


def test_s225_giovanni_segantini_in_catalog():
    """Session 225: giovanni_segantini must appear in CATALOG with correct properties."""
    from art_catalog import CATALOG, get_style
    assert "giovanni_segantini" in CATALOG, "giovanni_segantini missing from CATALOG"
    s = get_style("giovanni_segantini")
    mv = s.movement.lower()
    assert "alpin" in mv or "neo-impressi" in mv or "divisioni" in mv, (
        f"giovanni_segantini movement unexpected: {s.movement!r}")
    assert s.chromatic_split is True, "giovanni_segantini chromatic_split must be True"
    assert s.crackle is False, "giovanni_segantini crackle must be False"
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"
    assert len(s.famous_works) >= 5, (
        f"giovanni_segantini should have >= 5 famous works; got {len(s.famous_works)}")
    assert "136" in s.inspiration or "THIRTY-SIXTH" in s.inspiration, (
        "giovanni_segantini inspiration must reference 136th mode")


# ------------------------------------------------------------------------------
# alpine_luminance_intensification_pass -- session 225 artistic improvement
# ------------------------------------------------------------------------------

def test_s225_alpine_pass_exists():
    """Session 225: Painter must have alpine_luminance_intensification_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "alpine_luminance_intensification_pass"), (
        "Painter is missing alpine_luminance_intensification_pass")
    assert callable(getattr(Painter, "alpine_luminance_intensification_pass"))


def test_s225_alpine_pass_no_error():
    """Session 225: alpine_luminance_intensification_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.70, 0.80, 0.90), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.alpine_luminance_intensification_pass(
        shadow_thresh=0.32,
        highlight_boost=0.07,
        highlight_thresh=0.75,
        chroma_scale=1.18,
        opacity=0.72,
    )


def test_s225_alpine_pass_zero_opacity_no_change():
    """Session 225: alpine_luminance_intensification_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.75, 0.82, 0.88), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.alpine_luminance_intensification_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "alpine_luminance_intensification_pass at opacity=0.0 must not change any pixels")


def test_s225_alpine_pass_shadow_violet_raises_blue():
    """Session 225: shadow violet shift must raise blue channel on a dark warm canvas."""
    p = _make_small_painter(64, 64)
    # Very dark warm canvas — shadow violet should push blue up
    p.tone_ground((0.18, 0.12, 0.06), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_blue = float(before[:, :, 0].mean())

    p.alpine_luminance_intensification_pass(
        shadow_violet_r=0.40,
        shadow_violet_g=0.40,
        shadow_violet_b=1.00,     # strong blue target
        shadow_thresh=0.60,       # raise threshold so dark canvas qualifies
        highlight_boost=0.0,
        chroma_scale=1.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_blue = float(after[:, :, 0].mean())

    assert after_blue > before_blue, (
        f"shadow violet shift should raise blue channel on dark warm canvas; "
        f"before={before_blue:.1f} after={after_blue:.1f}")


def test_s225_alpine_pass_highlight_boost_raises_brightness():
    """Session 225: highlight_boost must raise brightness of near-white pixels."""
    p = _make_small_painter(64, 64)
    # Bright neutral canvas — highlight boost should raise all channels
    p.tone_ground((0.88, 0.88, 0.88), texture_strength=0.0)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_mean = float(before[:, :, 2].mean())

    p.alpine_luminance_intensification_pass(
        shadow_thresh=0.10,       # lower so bright canvas doesn't get shadow violet
        highlight_boost=0.20,     # exaggerate boost
        highlight_thresh=0.60,    # lower threshold so bright canvas qualifies
        chroma_scale=1.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_mean = float(after[:, :, 2].mean())

    assert after_mean > before_mean, (
        f"highlight_boost should raise red channel on bright canvas; "
        f"before={before_mean:.1f} after={after_mean:.1f}")


def test_s225_alpine_pass_changes_canvas():
    """Session 225: alpine_luminance_intensification_pass must visibly change a mixed canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.65, 0.80), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.alpine_luminance_intensification_pass(chroma_scale=1.30, opacity=1.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "alpine_luminance_intensification_pass must change a non-uniform canvas"
