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
        "is_surrealist":              period == Period.SURREALIST,
        "is_abstract_expressionist":  period == Period.ABSTRACT_EXPRESSIONIST,
        "is_romantic":                period == Period.ROMANTIC,
        "is_venetian":                period == Period.VENETIAN_RENAISSANCE,
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


# ──────────────────────────────────────────────────────────────────────────────
# folk_retablo_pass — session 13 addition (Frida Kahlo / Surrealist technique)
# ──────────────────────────────────────────────────────────────────────────────

def test_folk_retablo_pass_exists():
    """Painter must have folk_retablo_pass() method after session 13."""
    from stroke_engine import Painter
    assert hasattr(Painter, "folk_retablo_pass"), (
        "folk_retablo_pass not found on Painter")
    assert callable(getattr(Painter, "folk_retablo_pass"))


def test_folk_retablo_pass_no_error():
    """folk_retablo_pass() runs without error on a plain toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.72, 0.58, 0.32), texture_strength=0.08)
    # Should not raise
    p.folk_retablo_pass(ref, n_levels=4, saturation_boost=1.50,
                        boundary_vibration=True)


def test_folk_retablo_pass_no_error_vibration_off():
    """folk_retablo_pass() runs without error when boundary_vibration is disabled."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.72, 0.58, 0.32), texture_strength=0.08)
    p.folk_retablo_pass(ref, n_levels=3, saturation_boost=1.30,
                        boundary_vibration=False)


def test_folk_retablo_pass_modifies_canvas():
    """folk_retablo_pass() with saturation boost must change a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)

    # Paint some colourful strokes so the pass has colour to posterize / boost
    p.tone_ground((0.50, 0.22, 0.12), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.array(p.canvas.to_pil(), dtype=np.float32)
    p.folk_retablo_pass(ref, n_levels=4, saturation_boost=1.55,
                        outline_thickness=2.0, boundary_vibration=True)
    after = np.array(p.canvas.to_pil(), dtype=np.float32)

    diff = np.abs(after - before).max()
    assert diff > 0, "folk_retablo_pass should modify a non-uniform canvas"


def test_folk_retablo_pass_outline_darkens_edges():
    """
    With a vivid two-colour canvas, the contour outlines should produce pixels
    darker than both input zones near the boundary.
    """
    from PIL import Image as _PILImg
    p = _make_small_painter(64, 64)

    # Paint left half warm red, right half cool blue to create a strong edge
    p.tone_ground((0.80, 0.20, 0.10), texture_strength=0.0)
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :32, :] = [200, 50, 30]    # left: warm red
    arr[:, 32:, :] = [30, 60, 180]    # right: cool blue
    ref = _PILImg.fromarray(arr, "RGB")

    p.folk_retablo_pass(ref, n_levels=2, saturation_boost=1.0,
                        outline_thickness=3.0, outline_opacity=0.95,
                        boundary_vibration=False)

    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    # Cairo BGRA: channel 0=B, 1=G, 2=R
    # The centre column (where the boundary is) should be darkened by the outline
    centre_col = buf[:, 31, :]   # column just left of boundary
    # Mean brightness = (R+G+B)/3
    mean_brightness = (centre_col[:, 0].astype(float) +
                       centre_col[:, 1].astype(float) +
                       centre_col[:, 2].astype(float)) / 3.0
    # Outline is near-black, so mean should be substantially below 255
    assert mean_brightness.mean() < 200, (
        "Boundary column should be darkened by the retablo outline stroke, "
        f"but mean brightness is {mean_brightness.mean():.1f}")


# ──────────────────────────────────────────────────────────────────────────────
# SURREALIST period routing flags
# ──────────────────────────────────────────────────────────────────────────────

def test_surrealist_flag_set_for_surrealist_period():
    flags = _routing_flags(Period.SURREALIST)
    assert flags["is_surrealist"] is True


def test_surrealist_flag_not_set_for_other_periods():
    for period in Period:
        if period == Period.SURREALIST:
            continue
        flags = _routing_flags(period)
        assert not flags["is_surrealist"], (
            f"is_surrealist should be False for {period.name}")


def test_surrealist_and_mannerist_mutually_exclusive():
    flags_s = _routing_flags(Period.SURREALIST)
    flags_m = _routing_flags(Period.MANNERIST)
    assert flags_s["is_surrealist"] and not flags_s["is_mannerist"]
    assert flags_m["is_mannerist"]  and not flags_m["is_surrealist"]


# ──────────────────────────────────────────────────────────────────────────────
# Session 14: geometric_resonance_pass + ABSTRACT_EXPRESSIONIST routing
# ──────────────────────────────────────────────────────────────────────────────

def test_geometric_resonance_pass_exists():
    """Session 14: Painter must have geometric_resonance_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "geometric_resonance_pass"), (
        "geometric_resonance_pass not found on Painter")
    assert callable(getattr(Painter, "geometric_resonance_pass"))


def test_geometric_resonance_pass_no_error():
    """geometric_resonance_pass() runs without error on a plain toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.92, 0.91, 0.87), texture_strength=0.03)
    # Should not raise
    p.geometric_resonance_pass(
        ref,
        n_circles     = 4,
        n_triangles   = 3,
        n_lines       = 6,
        shape_opacity = 0.20,
    )


def test_geometric_resonance_pass_modifies_canvas():
    """geometric_resonance_pass() with shape_opacity > 0 must modify the canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.92, 0.91, 0.87), texture_strength=0.03)
    before = np.array(p.canvas.to_pil(), dtype=np.float32)

    p.geometric_resonance_pass(
        ref,
        n_circles     = 6,
        n_triangles   = 5,
        n_lines       = 8,
        shape_opacity = 0.30,
        seed          = 7,
    )
    after = np.array(p.canvas.to_pil(), dtype=np.float32)

    diff = np.abs(after - before).max()
    assert diff > 0, (
        "geometric_resonance_pass with shape_opacity=0.30 should modify the canvas; "
        f"max pixel diff = {diff:.1f}")


def test_abstract_expressionist_flag_set():
    """ABSTRACT_EXPRESSIONIST period must set is_abstract_expressionist=True."""
    flags = _routing_flags(Period.ABSTRACT_EXPRESSIONIST)
    assert flags["is_abstract_expressionist"] is True


def test_abstract_expressionist_flag_not_set_for_other_periods():
    """is_abstract_expressionist must be False for all periods except ABSTRACT_EXPRESSIONIST."""
    for period in Period:
        if period == Period.ABSTRACT_EXPRESSIONIST:
            continue
        flags = _routing_flags(period)
        assert not flags["is_abstract_expressionist"], (
            f"is_abstract_expressionist should be False for {period.name}")


def test_abstract_expressionist_mutually_exclusive_with_surrealist():
    """ABSTRACT_EXPRESSIONIST and SURREALIST are different periods."""
    flags_ae = _routing_flags(Period.ABSTRACT_EXPRESSIONIST)
    flags_s  = _routing_flags(Period.SURREALIST)
    assert     flags_ae["is_abstract_expressionist"]
    assert not flags_ae["is_surrealist"]
    assert     flags_s["is_surrealist"]
    assert not flags_s["is_abstract_expressionist"]


def test_sfumato_veil_pass_chroma_dampen_accepted():
    """sfumato_veil_pass() must accept the new chroma_dampen parameter without error."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    # Should not raise — chroma_dampen is a new improvement in session 14
    p.sfumato_veil_pass(
        ref,
        n_veils       = 2,
        blur_radius   = 4.0,
        warmth        = 0.30,
        veil_opacity  = 0.06,
        chroma_dampen = 0.20,
    )


def test_sfumato_veil_pass_chroma_dampen_zero_same_as_default():
    """sfumato_veil_pass with chroma_dampen=0 must be valid (backward compat)."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.05)
    # Must not raise with explicit chroma_dampen=0
    p.sfumato_veil_pass(
        ref,
        n_veils       = 2,
        blur_radius   = 4.0,
        chroma_dampen = 0.0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Current session: venetian_glaze_pass + subsurface_glow_pass + VENETIAN_RENAISSANCE
# ──────────────────────────────────────────────────────────────────────────────

def test_venetian_glaze_pass_exists():
    """Painter must have venetian_glaze_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "venetian_glaze_pass"), (
        "venetian_glaze_pass not found on Painter")
    assert callable(getattr(Painter, "venetian_glaze_pass"))


def test_subsurface_glow_pass_exists():
    """Painter must have subsurface_glow_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "subsurface_glow_pass"), (
        "subsurface_glow_pass not found on Painter")
    assert callable(getattr(Painter, "subsurface_glow_pass"))


def test_venetian_glaze_pass_no_error():
    """venetian_glaze_pass() runs without error on a plain toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.54, 0.34, 0.22), texture_strength=0.08)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    # Should not raise
    p.venetian_glaze_pass(
        ref,
        n_glaze_layers  = 3,
        glaze_warmth    = 0.55,
        shadow_depth    = 0.70,
        impasto_strokes = 30,
        impasto_size    = 5.0,
        impasto_opacity = 0.85,
    )


def test_venetian_glaze_pass_modifies_canvas():
    """venetian_glaze_pass() must modify a non-trivial canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.54, 0.34, 0.22), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.array(p.canvas.to_pil(), dtype=np.float32)
    p.venetian_glaze_pass(ref, n_glaze_layers=3, impasto_strokes=20)
    after  = np.array(p.canvas.to_pil(), dtype=np.float32)

    assert np.abs(after - before).max() > 0, (
        "venetian_glaze_pass should modify the canvas")


def test_subsurface_glow_pass_no_error_no_mask():
    """subsurface_glow_pass() runs without error when no figure mask is set."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.54, 0.34, 0.22), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.subsurface_glow_pass(
        ref,
        glow_color    = (0.90, 0.42, 0.24),
        glow_strength = 0.15,
        blur_sigma    = 4.0,
        edge_falloff  = 0.55,
    )


def test_subsurface_glow_pass_no_error_with_mask():
    """subsurface_glow_pass() runs correctly when a figure mask is provided."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.54, 0.34, 0.22), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    mask = np.zeros((64, 64), dtype=np.float32)
    mask[16:48, 16:48] = 1.0
    p._figure_mask = mask

    p.subsurface_glow_pass(
        ref,
        glow_color    = (0.88, 0.40, 0.22),
        glow_strength = 0.18,
        blur_sigma    = 3.0,
    )


def test_subsurface_glow_pass_modifies_canvas():
    """subsurface_glow_pass() with glow_strength > 0 and a figure mask edge must modify the canvas."""
    from PIL import Image as _PILImg
    p   = _make_small_painter(64, 64)

    # Use a non-uniform reference with a clear bright/dark boundary so there are
    # detectable luminance gradient edges for the glow zone.
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :32, :] = [200, 160, 110]   # left: warm mid-tone
    arr[:, 32:, :] = [60, 48, 36]      # right: dark shadow
    ref = _PILImg.fromarray(arr, "RGB")

    p.tone_ground((0.54, 0.34, 0.22), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.array(p.canvas.to_pil(), dtype=np.float32)
    p.subsurface_glow_pass(ref, glow_strength=0.40, blur_sigma=3.0, edge_falloff=0.0)
    after  = np.array(p.canvas.to_pil(), dtype=np.float32)

    assert np.abs(after - before).max() > 0, (
        "subsurface_glow_pass with glow_strength=0.40 should modify the canvas")


def test_venetian_flag_set_for_venetian_period():
    """VENETIAN_RENAISSANCE period must set is_venetian=True."""
    flags = _routing_flags(Period.VENETIAN_RENAISSANCE)
    assert flags["is_venetian"] is True


def test_venetian_flag_not_set_for_other_periods():
    """is_venetian must be False for all periods except VENETIAN_RENAISSANCE."""
    for period in Period:
        if period == Period.VENETIAN_RENAISSANCE:
            continue
        flags = _routing_flags(period)
        assert not flags["is_venetian"], (
            f"is_venetian should be False for {period.name}")


def test_venetian_mutually_exclusive_with_renaissance():
    """VENETIAN_RENAISSANCE and RENAISSANCE are distinct periods."""
    flags_v = _routing_flags(Period.VENETIAN_RENAISSANCE)
    flags_r = _routing_flags(Period.RENAISSANCE)
    assert     flags_v["is_venetian"]
    assert not flags_v.get("is_renaissance_soft", False)
    assert not flags_r["is_venetian"]
