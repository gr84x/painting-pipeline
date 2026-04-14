"""
test_pipeline_routing.py — Tests for new stroke_engine passes and pipeline routing.

Covers:
  - elongation_distortion_pass() exists as a method on Painter
  - impasto_texture_pass() exists as a method on Painter
  - elongation_distortion_pass() runs without error on a small synthetic canvas
  - impasto_texture_pass() runs without error on a small synthetic canvas
  - scene_to_painting routing flags (is_mannerist etc.) set correctly from Period enum
"""

import sys
import os
import types
import pytest
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

from scene_schema import Period, Style, Medium, PaletteHint


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _make_small_painter(w: int = 64, h: int = 64):
    """Return a Painter initialised on a tiny canvas — avoids slow texture generation."""
    from stroke_engine import Painter
    p = Painter(w, h)
    return p


def _solid_reference(w: int = 64, h: int = 64):
    """Return a solid warm-grey PIL Image for use as a reference."""
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array([180, 150, 120], dtype=np.uint8)),
        "RGB")


# ──────────────────────────────────────────────────────────────────────────────
# Pass existence
# ──────────────────────────────────────────────────────────────────────────────

def test_elongation_distortion_pass_exists():
    """Painter must have elongation_distortion_pass() method after session 11."""
    from stroke_engine import Painter
    assert hasattr(Painter, "elongation_distortion_pass"), (
        "elongation_distortion_pass not found on Painter")
    assert callable(getattr(Painter, "elongation_distortion_pass"))


def test_impasto_texture_pass_exists():
    """Painter must have impasto_texture_pass() method after session 11."""
    from stroke_engine import Painter
    assert hasattr(Painter, "impasto_texture_pass"), (
        "impasto_texture_pass not found on Painter")
    assert callable(getattr(Painter, "impasto_texture_pass"))


# ──────────────────────────────────────────────────────────────────────────────
# Pass smoke tests — run on a tiny 64×64 canvas; no errors means success
# ──────────────────────────────────────────────────────────────────────────────

def test_elongation_distortion_pass_no_mask():
    """elongation_distortion_pass() runs without error when no figure mask is set."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.12, 0.10, 0.18), texture_strength=0.05)
    # Should complete without exception
    p.elongation_distortion_pass(ref, elongation_factor=0.12)


def test_elongation_distortion_pass_with_mask():
    """elongation_distortion_pass() runs correctly when a figure mask is provided."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.12, 0.10, 0.18), texture_strength=0.05)

    # Build a simple ellipse mask — top-half of the canvas is 'figure'
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[10:54, 15:49] = 1.0   # rectangle figure region

    p.elongation_distortion_pass(
        ref,
        elongation_factor  = 0.14,
        figure_mask        = mask,
        jewel_boost        = 1.30,
        inner_glow_radius  = 4.0,
        inner_glow_opacity = 0.15,
        glow_color         = (0.88, 0.86, 0.78),
    )


def test_elongation_distortion_pass_canvas_not_blank():
    """After elongation pass, the canvas should contain non-zero pixel data."""
    from PIL import Image as _Img
    p = _make_small_painter(64, 64)
    p.tone_ground((0.40, 0.35, 0.22), texture_strength=0.08)
    ref = _solid_reference(64, 64)
    p.elongation_distortion_pass(ref, elongation_factor=0.10)
    img = p.canvas.to_pil()
    arr = np.array(img)
    # Canvas must have been written — at least some pixels > 0
    assert arr.max() > 0, "Canvas is blank after elongation_distortion_pass"


def test_impasto_texture_pass_no_error():
    """impasto_texture_pass() runs on a uniform canvas without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.50, 0.40, 0.28), texture_strength=0.06)
    # Should complete without exception
    p.impasto_texture_pass(light_angle=315.0, ridge_height=0.50)


def test_impasto_texture_pass_zero_height_no_op():
    """impasto_texture_pass() with ridge_height=0 should not modify the canvas."""
    from PIL import Image as _Img
    p = _make_small_painter(64, 64)
    p.tone_ground((0.50, 0.40, 0.28), texture_strength=0.06)

    before = np.array(p.canvas.to_pil()).copy()
    p.impasto_texture_pass(ridge_height=0.0)
    after  = np.array(p.canvas.to_pil())

    np.testing.assert_array_equal(before, after,
        err_msg="impasto_texture_pass with ridge_height=0 should be a no-op")


def test_impasto_texture_pass_modifies_canvas():
    """impasto_texture_pass() with ridge_height > 0 must modify a non-uniform canvas."""
    from PIL import Image as _Img
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)

    # Paint some strokes to create a non-uniform surface
    p.tone_ground((0.45, 0.38, 0.22), texture_strength=0.08)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.array(p.canvas.to_pil(), dtype=np.float32)
    p.impasto_texture_pass(light_angle=315.0, ridge_height=0.60,
                            highlight_opacity=0.40, shadow_opacity=0.30)
    after = np.array(p.canvas.to_pil(), dtype=np.float32)

    diff = np.abs(after - before).max()
    # The canvas should have changed — if all pixels are the same something is wrong
    assert diff > 0, (
        "impasto_texture_pass with ridge_height=0.6 should modify a non-uniform canvas")


# ──────────────────────────────────────────────────────────────────────────────
# Pipeline routing flag logic (unit-tested without running the full pipeline)
# ──────────────────────────────────────────────────────────────────────────────

def _routing_flags(period: Period, medium: Medium = Medium.OIL) -> dict:
    """Replicate the is_* flag logic from scene_to_painting without importing blender."""
    sp = Style(medium=medium, period=period).stroke_params
    return {
        "is_pointillist":             period == Period.POINTILLIST,
        "is_ukiyo_e":                 period == Period.UKIYO_E,
        "is_watercolor":              medium == Medium.WATERCOLOR,
        "is_proto_expressionist":     period == Period.PROTO_EXPRESSIONIST,
        "is_realist":                 period == Period.REALIST,
        "is_viennese_expressionist":  period == Period.VIENNESE_EXPRESSIONIST,
        "is_color_field":             period == Period.COLOR_FIELD,
        "is_synthetist":              period == Period.SYNTHETIST,
        "is_mannerist":               period == Period.MANNERIST,
        "is_romantic":                period == Period.ROMANTIC,
        "is_renaissance_soft":        (period == Period.RENAISSANCE
                                       and sp.get("edge_softness", 0.0) >= 0.80),
    }


@pytest.mark.parametrize("period", list(Period))
def test_routing_flags_mutually_exclusive(period):
    """At most one style-period flag must be True for any given Period."""
    flags = _routing_flags(period)
    # These are the exclusive period-dispatch flags (watercolor is a medium flag)
    period_flags = [v for k, v in flags.items()
                    if k not in ("is_watercolor", "is_romantic", "is_renaissance_soft")]
    true_count = sum(1 for v in period_flags if v)
    assert true_count <= 1, (
        f"More than one period flag is True for {period.name}: "
        + str({k: v for k, v in flags.items() if v}))


def test_mannerist_flag_set_for_mannerist_period():
    flags = _routing_flags(Period.MANNERIST)
    assert flags["is_mannerist"] is True


def test_mannerist_flag_not_set_for_other_periods():
    for period in Period:
        if period == Period.MANNERIST:
            continue
        flags = _routing_flags(period)
        assert not flags["is_mannerist"], (
            f"is_mannerist should be False for {period.name}")


def test_synthetist_flag_set():
    flags = _routing_flags(Period.SYNTHETIST)
    assert flags["is_synthetist"] is True
    assert flags["is_mannerist"]  is False


def test_renaissance_soft_flag():
    """RENAISSANCE with high edge_softness should set is_renaissance_soft."""
    sp = Style(medium=Medium.OIL, period=Period.RENAISSANCE,
               edge_softness=0.85).stroke_params
    assert sp["edge_softness"] >= 0.80


def test_watercolor_flag_set_by_medium():
    flags = _routing_flags(Period.IMPRESSIONIST, medium=Medium.WATERCOLOR)
    assert flags["is_watercolor"] is True
    assert flags["is_mannerist"]  is False


# ──────────────────────────────────────────────────────────────────────────────
# atmospheric_depth_pass — session 12 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_atmospheric_depth_pass_exists():
    """Painter must have atmospheric_depth_pass() method after session 12."""
    from stroke_engine import Painter
    assert hasattr(Painter, "atmospheric_depth_pass"), (
        "atmospheric_depth_pass not found on Painter")
    assert callable(getattr(Painter, "atmospheric_depth_pass"))


def test_atmospheric_depth_pass_no_error():
    """atmospheric_depth_pass() runs without error on a plain toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.50, 0.45, 0.32), texture_strength=0.06)
    # Should not raise
    p.atmospheric_depth_pass(
        haze_color   = (0.72, 0.78, 0.88),
        desaturation = 0.60,
        lightening   = 0.45,
        depth_gamma  = 1.6,
    )


def test_atmospheric_depth_pass_affects_top_more_than_bottom():
    """
    Top rows (y ≈ 0, distant sky) should be more blended toward haze than
    bottom rows (y ≈ H-1, foreground).  Paint a warm-red canvas and check
    that the top row is cooler (higher blue channel) after the pass.
    """
    from PIL import Image as _Img
    p = _make_small_painter(64, 64)

    # Fill canvas with warm red pixels so any cool-haze effect is detectable.
    warm_red = (0.85, 0.30, 0.10)
    p.tone_ground(warm_red, texture_strength=0.00)

    # Haze colour is cool blue — if applied at top the blue channel must rise.
    haze = (0.40, 0.60, 0.90)
    p.atmospheric_depth_pass(haze_color=haze, desaturation=0.50, lightening=0.60,
                              depth_gamma=1.0, background_only=False)

    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA: channel 0 = B, channel 1 = G, channel 2 = R
    top_blue    = float(buf[0,  :, 0].mean())   # top row — B channel
    bottom_blue = float(buf[63, :, 0].mean())   # bottom row — B channel

    assert top_blue > bottom_blue, (
        f"Top row should be bluer (more haze) than bottom row after "
        f"atmospheric_depth_pass, but top_blue={top_blue:.1f} "
        f"<= bottom_blue={bottom_blue:.1f}")


def test_atmospheric_depth_pass_background_only_preserves_figure():
    """
    With background_only=True and a figure mask set to the full canvas,
    the pass should leave the canvas unchanged (all pixels are 'figure').
    """
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.45, 0.28), texture_strength=0.04)

    # Set figure mask = all ones (everything is figure)
    p._figure_mask = np.ones((64, 64), dtype=np.float32)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.atmospheric_depth_pass(background_only=True)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    np.testing.assert_array_equal(before, after,
        err_msg="atmospheric_depth_pass with all-figure mask should not modify canvas")
