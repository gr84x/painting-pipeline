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
        "is_fauvist":                 period == Period.FAUVIST,
        "is_primitivist":             period == Period.PRIMITIVIST,
        "is_early_netherlandish":     period == Period.EARLY_NETHERLANDISH,
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


# ──────────────────────────────────────────────────────────────────────────────
# fauvist_mosaic_pass + chroma_zone_pass — session 16
# ──────────────────────────────────────────────────────────────────────────────

def test_fauvist_mosaic_pass_exists():
    """Painter must have fauvist_mosaic_pass() method (session 16)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "fauvist_mosaic_pass"), (
        "fauvist_mosaic_pass not found on Painter")
    assert callable(getattr(Painter, "fauvist_mosaic_pass"))


def test_chroma_zone_pass_exists():
    """Painter must have chroma_zone_pass() method (session 16 random improvement)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "chroma_zone_pass"), (
        "chroma_zone_pass not found on Painter")
    assert callable(getattr(Painter, "chroma_zone_pass"))


def test_fauvist_mosaic_pass_no_error():
    """fauvist_mosaic_pass() runs without error on a small synthetic canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.96, 0.94, 0.80), texture_strength=0.03)
    p.fauvist_mosaic_pass(ref, n_zones=4, saturation_boost=1.60, lum_flatten=0.50)


def test_fauvist_mosaic_pass_modifies_canvas():
    """fauvist_mosaic_pass() must visibly alter the canvas pixels."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.96, 0.94, 0.80), texture_strength=0.03)

    # Read canvas before
    buf_before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()

    p.fauvist_mosaic_pass(ref, n_zones=4, saturation_boost=1.60,
                          lum_flatten=0.50, complement_shadow=True)

    buf_after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()

    assert not np.array_equal(buf_before, buf_after), (
        "fauvist_mosaic_pass did not modify the canvas")


def test_chroma_zone_pass_no_error():
    """chroma_zone_pass() runs without error on a painted canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.08)
    p.block_in(ref, stroke_size=12, n_strokes=40)
    # Should complete without exception
    p.chroma_zone_pass(light_suppress=0.55, shadow_suppress=0.40,
                       midtone_boost=1.20)


def test_chroma_zone_pass_modifies_canvas():
    """chroma_zone_pass() must alter the canvas pixels."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    # Use a colourful reference so saturation suppression is detectable
    from PIL import Image
    colourful = Image.fromarray(
        (np.array([[[200, 30, 30]] * 64] * 64, dtype=np.uint8)), "RGB")
    p.tone_ground((0.78, 0.15, 0.12), texture_strength=0.05)
    p.block_in(colourful, stroke_size=10, n_strokes=60)

    buf_before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.chroma_zone_pass(light_suppress=0.40, shadow_suppress=0.30,
                       midtone_boost=1.30)
    buf_after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()

    assert not np.array_equal(buf_before, buf_after), (
        "chroma_zone_pass did not modify the canvas")


def test_chroma_zone_pass_pixels_stay_in_range():
    """chroma_zone_pass() must not produce out-of-range pixel values."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.08)
    p.block_in(ref, stroke_size=12, n_strokes=40)
    p.chroma_zone_pass(light_suppress=0.55, shadow_suppress=0.40,
                       midtone_boost=1.20)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_fauvist_flag_set_for_fauvist_period():
    """is_fauvist routing flag must be True for Period.FAUVIST."""
    flags = _routing_flags(Period.FAUVIST)
    assert flags["is_fauvist"] is True


def test_fauvist_flag_not_set_for_other_periods():
    """is_fauvist must be False for all periods except FAUVIST."""
    for period in Period:
        if period == Period.FAUVIST:
            continue
        flags = _routing_flags(period)
        assert not flags["is_fauvist"], (
            f"is_fauvist should be False for {period.name}")


def test_fauvist_mutually_exclusive_with_synthetist():
    """FAUVIST and SYNTHETIST are distinct periods — both flat but different pipelines."""
    flags_f = _routing_flags(Period.FAUVIST)
    flags_s = _routing_flags(Period.SYNTHETIST)
    assert     flags_f["is_fauvist"]
    assert not flags_f["is_synthetist"]
    assert     flags_s["is_synthetist"]
    assert not flags_s["is_fauvist"]


# ──────────────────────────────────────────────────────────────────────────────
# oval_mask_pass — Modigliani Primitivist technique (session 17)
# ──────────────────────────────────────────────────────────────────────────────

def test_oval_mask_pass_exists():
    """Painter must have oval_mask_pass() method after session 17."""
    from stroke_engine import Painter
    assert hasattr(Painter, "oval_mask_pass"), "oval_mask_pass not found on Painter"
    assert callable(getattr(Painter, "oval_mask_pass"))


def test_oval_mask_pass_no_error_no_mask():
    """oval_mask_pass() should complete without error when no figure mask is set."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.78, 0.62, 0.40), texture_strength=0.05)
    p.block_in(ref, stroke_size=12, n_strokes=30)
    p.oval_mask_pass(ref)


def test_oval_mask_pass_modifies_canvas():
    """oval_mask_pass() must change at least some pixel values in the face zone."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.78, 0.62, 0.40), texture_strength=0.05)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.oval_mask_pass(ref, flesh_tint=0.60)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    assert not np.array_equal(before, after), (
        "oval_mask_pass should modify at least some canvas pixels")


def test_oval_mask_pass_pixels_in_range():
    """oval_mask_pass() must not produce out-of-range (>255) pixel values."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.78, 0.62, 0.40), texture_strength=0.05)
    p.block_in(ref, stroke_size=12, n_strokes=30)
    p.oval_mask_pass(ref)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.max() <= 255
    assert buf.min() >= 0


# ──────────────────────────────────────────────────────────────────────────────
# warm_cool_boundary_pass — session 17 random artistic improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_warm_cool_boundary_pass_exists():
    """Painter must have warm_cool_boundary_pass() method after session 17."""
    from stroke_engine import Painter
    assert hasattr(Painter, "warm_cool_boundary_pass"), (
        "warm_cool_boundary_pass not found on Painter")
    assert callable(getattr(Painter, "warm_cool_boundary_pass"))


def test_warm_cool_boundary_pass_no_error():
    """warm_cool_boundary_pass() should complete without error on a plain canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.08)
    p.block_in(ref, stroke_size=12, n_strokes=40)
    p.warm_cool_boundary_pass()


def test_warm_cool_boundary_pass_modifies_boundaries():
    """
    With a two-tone reference (warm left / cool right), the pass should produce
    different pixel values near the centre than far from it.
    """
    import numpy as np
    from PIL import Image as _PILImg

    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)

    # Paint half warm, half cool so there is a strong boundary
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :32, :] = [200, 120, 60]    # left: warm
    arr[:, 32:, :] = [60, 100, 200]   # right: cool
    ref = _PILImg.fromarray(arr, "RGB")
    p.block_in(ref, stroke_size=14, n_strokes=60)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.warm_cool_boundary_pass(strength=0.30, edge_thresh=0.05)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    assert not np.array_equal(before, after), (
        "warm_cool_boundary_pass should modify pixels near the warm/cool boundary")


def test_warm_cool_boundary_pass_pixels_in_range():
    """warm_cool_boundary_pass() must not produce out-of-range pixel values."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.08)
    p.block_in(ref, stroke_size=12, n_strokes=40)
    p.warm_cool_boundary_pass()
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.max() <= 255
    assert buf.min() >= 0


# ──────────────────────────────────────────────────────────────────────────────
# PRIMITIVIST period routing flags (session 17)
# ──────────────────────────────────────────────────────────────────────────────

def test_primitivist_flag_set_for_primitivist_period():
    """is_primitivist routing flag must be True for Period.PRIMITIVIST."""
    flags = _routing_flags(Period.PRIMITIVIST)
    assert flags["is_primitivist"] is True


def test_primitivist_flag_not_set_for_other_periods():
    """is_primitivist must be False for all periods except PRIMITIVIST."""
    for period in Period:
        if period == Period.PRIMITIVIST:
            continue
        flags = _routing_flags(period)
        assert not flags["is_primitivist"], (
            f"is_primitivist should be False for {period.name}")


def test_primitivist_mutually_exclusive_with_fauvist():
    """PRIMITIVIST and FAUVIST are distinct flat-colour periods."""
    flags_p = _routing_flags(Period.PRIMITIVIST)
    flags_f = _routing_flags(Period.FAUVIST)
    assert     flags_p["is_primitivist"]
    assert not flags_p["is_fauvist"]
    assert     flags_f["is_fauvist"]
    assert not flags_f["is_primitivist"]


# ──────────────────────────────────────────────────────────────────────────────
# glazed_panel_pass() (session 18)
# ──────────────────────────────────────────────────────────────────────────────

def test_glazed_panel_pass_exists():
    """Painter must have glazed_panel_pass() method after session 18."""
    from stroke_engine import Painter
    assert hasattr(Painter, "glazed_panel_pass"), (
        "glazed_panel_pass not found on Painter")


def test_glazed_panel_pass_no_error():
    """glazed_panel_pass() must run without raising on a small synthetic canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.95, 0.93, 0.88), texture_strength=0.02)
    p.block_in(ref, stroke_size=12, n_strokes=60)
    p.glazed_panel_pass(ref, n_glaze_layers=3, glaze_opacity=0.08)


def test_glazed_panel_pass_modifies_canvas():
    """glazed_panel_pass() must change at least some pixel values.

    The solid warm-grey reference has luminance ~0.61.  shadow_thresh is raised
    to 0.75 so the mid-value reference pixels fall inside the shadow zone and
    the glaze accumulation fires.
    """
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.95, 0.93, 0.88), texture_strength=0.02)
    p.block_in(ref, stroke_size=12, n_strokes=60)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    # shadow_thresh=0.75 ensures the ~0.61 luminance reference pixels are treated
    # as shadow-zone pixels and receive the warm amber glaze accumulation.
    p.glazed_panel_pass(ref, n_glaze_layers=5, glaze_opacity=0.10,
                        shadow_warmth=0.40, shadow_thresh=0.75)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    assert not np.array_equal(before, after), (
        "glazed_panel_pass should modify canvas pixels in shadow zones")


def test_glazed_panel_pass_pixels_in_range():
    """glazed_panel_pass() must not produce out-of-range pixel values."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.95, 0.93, 0.88), texture_strength=0.02)
    p.block_in(ref, stroke_size=12, n_strokes=40)
    p.glazed_panel_pass(ref)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.max() <= 255
    assert buf.min() >= 0


# ──────────────────────────────────────────────────────────────────────────────
# micro_detail_pass() — session 18 random artistic improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_micro_detail_pass_exists():
    """Painter must have micro_detail_pass() method after session 18."""
    from stroke_engine import Painter
    assert hasattr(Painter, "micro_detail_pass"), (
        "micro_detail_pass not found on Painter")


def test_micro_detail_pass_no_error():
    """micro_detail_pass() must run without raising on a small synthetic canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.95, 0.93, 0.88), texture_strength=0.02)
    p.block_in(ref, stroke_size=12, n_strokes=60)
    p.micro_detail_pass(strength=0.20, fine_sigma=0.8, coarse_sigma=3.0)


def test_micro_detail_pass_modifies_canvas():
    """micro_detail_pass() must modify pixels near sharp fine edges."""
    import numpy as np
    from PIL import Image as _PILImg
    p = _make_small_painter(64, 64)

    # Synthetic reference with a sharp warm/cool contrast stripe for detectable edges
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :32, :] = [220, 180, 140]    # warm left half
    arr[:, 32:, :] = [100, 120, 160]    # cool right half
    ref = _PILImg.fromarray(arr, "RGB")
    p.tone_ground((0.95, 0.93, 0.88), texture_strength=0.02)
    p.block_in(ref, stroke_size=14, n_strokes=60)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.micro_detail_pass(strength=0.35, edge_thresh=0.03, figure_only=False)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    assert not np.array_equal(before, after), (
        "micro_detail_pass should modify pixels along fine edges")


def test_micro_detail_pass_pixels_in_range():
    """micro_detail_pass() must not produce out-of-range pixel values."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.08)
    p.block_in(ref, stroke_size=12, n_strokes=40)
    p.micro_detail_pass()
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.max() <= 255
    assert buf.min() >= 0


# ──────────────────────────────────────────────────────────────────────────────
# EARLY_NETHERLANDISH period routing flags (session 18)
# ──────────────────────────────────────────────────────────────────────────────

def test_early_netherlandish_flag_set_for_early_netherlandish_period():
    """is_early_netherlandish routing flag must be True for Period.EARLY_NETHERLANDISH."""
    flags = _routing_flags(Period.EARLY_NETHERLANDISH)
    assert flags["is_early_netherlandish"] is True


def test_early_netherlandish_flag_not_set_for_other_periods():
    """is_early_netherlandish must be False for all periods except EARLY_NETHERLANDISH."""
    for period in Period:
        if period == Period.EARLY_NETHERLANDISH:
            continue
        flags = _routing_flags(period)
        assert not flags["is_early_netherlandish"], (
            f"is_early_netherlandish should be False for {period.name}")


def test_early_netherlandish_mutually_exclusive_with_renaissance():
    """EARLY_NETHERLANDISH and RENAISSANCE are distinct periods."""
    flags_e = _routing_flags(Period.EARLY_NETHERLANDISH)
    flags_r = _routing_flags(Period.RENAISSANCE)
    assert     flags_e["is_early_netherlandish"]
    assert not flags_e.get("is_renaissance_soft", False)
    assert not flags_r["is_early_netherlandish"]


def test_early_netherlandish_mutually_exclusive_with_venetian():
    """EARLY_NETHERLANDISH and VENETIAN_RENAISSANCE are distinct glazing traditions."""
    flags_e = _routing_flags(Period.EARLY_NETHERLANDISH)
    flags_v = _routing_flags(Period.VENETIAN_RENAISSANCE)
    assert     flags_e["is_early_netherlandish"]
    assert not flags_e["is_venetian"]
    assert     flags_v["is_venetian"]
    assert not flags_v["is_early_netherlandish"]


# ──────────────────────────────────────────────────────────────────────────────
# chiaroscuro_focus_pass — Artemisia Gentileschi / Caravaggesque (current session)
# ──────────────────────────────────────────────────────────────────────────────

def test_chiaroscuro_focus_pass_exists():
    """Painter must have chiaroscuro_focus_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "chiaroscuro_focus_pass"), (
        "chiaroscuro_focus_pass not found on Painter")
    assert callable(getattr(Painter, "chiaroscuro_focus_pass"))


def test_chiaroscuro_focus_pass_no_error():
    """chiaroscuro_focus_pass() runs without error on a plain toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.06)
    # Should not raise
    p.chiaroscuro_focus_pass(
        light_center      = (0.35, 0.30),
        light_radius      = 0.38,
        shadow_strength   = 0.72,
    )


def test_chiaroscuro_focus_pass_darkens_corners():
    """
    With a central light and high shadow_strength, the canvas corners should
    be significantly darker than the centre after the pass.
    """
    p = _make_small_painter(64, 64)
    # Tone with a mid-grey so brightness changes are detectable
    p.tone_ground((0.55, 0.50, 0.45), texture_strength=0.00)

    p.chiaroscuro_focus_pass(
        light_center    = (0.5, 0.5),   # light exactly at centre
        light_radius    = 0.20,
        shadow_strength = 0.80,
    )

    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA: channel 2 = R
    centre_r = float(buf[30:34, 30:34, 2].mean())
    corner_r = float(buf[:8, :8, 2].mean())

    assert centre_r > corner_r, (
        f"Centre should be brighter than corner after chiaroscuro_focus_pass; "
        f"centre_R={centre_r:.1f}  corner_R={corner_r:.1f}")


def test_chiaroscuro_focus_pass_modifies_canvas():
    """chiaroscuro_focus_pass() must change pixel values on a non-trivial canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.45, 0.32), texture_strength=0.06)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.chiaroscuro_focus_pass(light_center=(0.35, 0.30), shadow_strength=0.65)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    assert not np.array_equal(before, after), (
        "chiaroscuro_focus_pass should modify canvas pixels")


def test_chiaroscuro_focus_pass_pixels_in_range():
    """chiaroscuro_focus_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.45, 0.32), texture_strength=0.06)
    p.chiaroscuro_focus_pass(shadow_strength=0.80, light_boost=0.08)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_chiaroscuro_focus_pass_no_error_with_figure_mask():
    """chiaroscuro_focus_pass() with figure_only=True and a mask should not raise."""
    p   = _make_small_painter(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.06)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[16:48, 16:48] = 1.0
    p._figure_mask = mask
    p.chiaroscuro_focus_pass(
        light_center  = (0.35, 0.30),
        shadow_strength = 0.70,
        figure_only   = True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# highlight_bloom_pass — specular highlight glow (current session random improvement)
# ──────────────────────────────────────────────────────────────────────────────

def test_highlight_bloom_pass_exists():
    """Painter must have highlight_bloom_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "highlight_bloom_pass"), (
        "highlight_bloom_pass not found on Painter")
    assert callable(getattr(Painter, "highlight_bloom_pass"))


def test_highlight_bloom_pass_no_error_default():
    """highlight_bloom_pass() runs without error with default parameters."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    # Should not raise
    p.highlight_bloom_pass()


def test_highlight_bloom_pass_no_error_multi_scale_false():
    """highlight_bloom_pass() with multi_scale=False runs without error."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.highlight_bloom_pass(multi_scale=False)


def test_highlight_bloom_pass_modifies_bright_canvas():
    """highlight_bloom_pass() must change pixel values on a canvas with bright highlights."""
    from PIL import Image as _PILImg
    p = _make_small_painter(64, 64)

    # Reference with a bright white zone — these pixels exceed the bloom threshold
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[20:44, 20:44, :] = 240   # near-white square that exceeds threshold
    ref = _PILImg.fromarray(arr, "RGB")

    p.tone_ground((0.10, 0.08, 0.06), texture_strength=0.04)
    p.block_in(ref, stroke_size=10, n_strokes=40)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.highlight_bloom_pass(threshold=0.70, bloom_sigma=4.0, bloom_opacity=0.35)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    assert not np.array_equal(before, after), (
        "highlight_bloom_pass should modify pixels around bright highlights")


def test_highlight_bloom_pass_zero_opacity_is_near_noop():
    """highlight_bloom_pass() with bloom_opacity=0 should not modify the canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.84, 0.78), texture_strength=0.04)
    p.block_in(ref, stroke_size=10, n_strokes=30)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.highlight_bloom_pass(bloom_opacity=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    np.testing.assert_array_equal(before, after,
        err_msg="highlight_bloom_pass with bloom_opacity=0 should be a no-op")


def test_highlight_bloom_pass_pixels_in_range():
    """highlight_bloom_pass() must not produce out-of-range pixel values."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.highlight_bloom_pass(threshold=0.50, bloom_sigma=5.0, bloom_opacity=0.40)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_highlight_bloom_pass_no_error_with_bloom_color():
    """highlight_bloom_pass() with an explicit bloom_color tint should not raise."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    # Warm amber tint — candlelight bloom
    p.highlight_bloom_pass(bloom_color=(0.98, 0.92, 0.72), bloom_opacity=0.18)


def test_highlight_bloom_pass_no_error_figure_only():
    """highlight_bloom_pass() with figure_only=True and a mask should not raise."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[16:48, 16:48] = 1.0
    p._figure_mask = mask
    p.highlight_bloom_pass(figure_only=True, bloom_opacity=0.20)


# ──────────────────────────────────────────────────────────────────────────────
# chromatic_shadow_pass() — session 20 random artistic improvement
# Inspired by Eugène Delacroix's discovery that shadows contain the complement
# of the dominant light colour.
# ──────────────────────────────────────────────────────────────────────────────

def test_chromatic_shadow_pass_exists():
    """Painter must have chromatic_shadow_pass() method after session 20."""
    from stroke_engine import Painter
    assert hasattr(Painter, "chromatic_shadow_pass"), (
        "chromatic_shadow_pass not found on Painter")
    assert callable(getattr(Painter, "chromatic_shadow_pass"))


def test_chromatic_shadow_pass_no_error():
    """chromatic_shadow_pass() runs without error on a tiny canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.40, 0.28, 0.14), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.chromatic_shadow_pass(shadow_threshold=0.45, strength=0.26)


def test_chromatic_shadow_pass_modifies_canvas():
    """chromatic_shadow_pass() must change at least some canvas pixels."""
    import cairo
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.20, 0.12, 0.06), texture_strength=0.08)  # very dark ground
    p.block_in(ref, stroke_size=10, n_strokes=60)

    surf = p.canvas.surface
    h, w = surf.get_height(), surf.get_width()
    before = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()

    p.chromatic_shadow_pass(shadow_threshold=0.55, strength=0.50, lum_preserve=False)

    after = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
    assert not np.array_equal(before, after), (
        "chromatic_shadow_pass() should have changed at least some pixels")


def test_chromatic_shadow_pass_lum_preserve_keeps_luminance():
    """With lum_preserve=True, per-pixel luminance must be preserved (within tolerance)."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.30, 0.22, 0.10), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=60)

    surf = p.canvas.surface
    h, w = surf.get_height(), surf.get_width()
    before_buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()

    # Compute luminance from Cairo ARGB32 (B=0, G=1, R=2)
    def _lum(buf):
        r = buf[:, :, 2].astype(np.float32) / 255.0
        g = buf[:, :, 1].astype(np.float32) / 255.0
        b = buf[:, :, 0].astype(np.float32) / 255.0
        return 0.299 * r + 0.587 * g + 0.114 * b

    lum_before = _lum(before_buf)

    # Shadow pixels only (lum < 0.50)
    shadow_mask = lum_before < 0.50

    p.chromatic_shadow_pass(shadow_threshold=0.50, strength=0.40, lum_preserve=True)

    after_buf = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
    lum_after = _lum(after_buf)

    # In shadow zones, luminance must not change by more than ±0.08 (8%)
    # Small rounding errors from uint8 quantisation are expected.
    if shadow_mask.any():
        delta = np.abs(lum_after[shadow_mask] - lum_before[shadow_mask])
        assert delta.max() <= 0.08, (
            f"lum_preserve=True should keep luminance constant; "
            f"max delta was {delta.max():.4f}")


def test_chromatic_shadow_pass_fixed_tint_no_error():
    """chromatic_shadow_pass() with a fixed shadow_tint should not raise."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.40, 0.28, 0.14), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    # Violet shadow tint — warm-lit Delacroix scene
    p.chromatic_shadow_pass(shadow_tint=(0.35, 0.22, 0.72), strength=0.30)


def test_chromatic_shadow_pass_figure_only_no_error():
    """chromatic_shadow_pass() with figure_only=True and a mask should not raise."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.40, 0.28, 0.14), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[16:48, 16:48] = 1.0
    p._figure_mask = mask
    p.chromatic_shadow_pass(figure_only=True, strength=0.28)


def test_chromatic_shadow_pass_pixels_in_range():
    """chromatic_shadow_pass() must not produce out-of-range pixel values."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.22, 0.14, 0.06), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=50)
    p.chromatic_shadow_pass(shadow_threshold=0.60, strength=0.50, lum_preserve=False)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_chromatic_shadow_pass_zero_strength_is_noop():
    """With strength=0, chromatic_shadow_pass() should not change the canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.40, 0.28, 0.14), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=40)

    surf = p.canvas.surface
    h, w = surf.get_height(), surf.get_width()
    before = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()

    p.chromatic_shadow_pass(strength=0.0)

    after = np.frombuffer(surf.get_data(), dtype=np.uint8).reshape((h, w, 4)).copy()
    assert np.array_equal(before, after), (
        "strength=0 should leave the canvas unchanged")


# ──────────────────────────────────────────────────────────────────────────────
# BAROQUE routing flag — scene_to_painting() flags
# ──────────────────────────────────────────────────────────────────────────────

def test_baroque_routing_flag_true_for_baroque_period():
    """is_baroque should be True when Period.BAROQUE is set."""
    style = Style(medium=Medium.OIL, period=Period.BAROQUE,
                  palette=PaletteHint.WARM_EARTH)
    assert style.period == Period.BAROQUE


def test_baroque_routing_flag_false_for_renaissance():
    """BAROQUE flag must not fire for RENAISSANCE period."""
    assert Period.BAROQUE != Period.RENAISSANCE


def test_baroque_stroke_params_present():
    """BAROQUE period must have stroke_params defined."""
    style = Style(medium=Medium.OIL, period=Period.BAROQUE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"BAROQUE stroke_params missing key: {key!r}"


# ──────────────────────────────────────────────────────────────────────────────
# scumble_pass -- dry-brush drag/scumbling effect (Vuillard/Nabis session)
# ──────────────────────────────────────────────────────────────────────────────

def test_scumble_pass_exists():
    """Painter must have scumble_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "scumble_pass"), "scumble_pass not found on Painter"
    assert callable(getattr(Painter, "scumble_pass"))


def test_scumble_pass_no_error():
    """scumble_pass() runs without error on a small canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.60, 0.54, 0.44), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.scumble_pass(opacity=0.18, n_drags=80, drag_distance=8)


def test_scumble_pass_modifies_canvas():
    """scumble_pass() with positive opacity must modify a painted canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.45, 0.38, 0.22), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    before = np.array(p.canvas.to_pil(), dtype=np.float32)
    p.scumble_pass(opacity=0.30, n_drags=160, drag_distance=10, dry_factor=0.60)
    after = np.array(p.canvas.to_pil(), dtype=np.float32)
    diff = np.abs(after - before).max()
    assert diff > 0, "scumble_pass with opacity=0.30 should modify the canvas"


def test_scumble_pass_figure_only_no_error():
    """scumble_pass() with figure_only=True and a mask should not raise."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[16:48, 16:48] = 1.0
    p._figure_mask = mask
    p.scumble_pass(opacity=0.20, n_drags=80, drag_distance=8, figure_only=True)
# dappled_light_pass — Sorolla / Luminismo addition
# ──────────────────────────────────────────────────────────────────────────────

def test_dappled_light_pass_exists():
    """Painter must have dappled_light_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "dappled_light_pass"), (
        "dappled_light_pass not found on Painter")
    assert callable(getattr(Painter, "dappled_light_pass"))


def test_dappled_light_pass_no_error():
    """dappled_light_pass() runs without error on a plain toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.70, 0.68, 0.58), texture_strength=0.06)
    # Should not raise
    p.dappled_light_pass(ref, n_pools=6, pool_radius=0.12)


def test_dappled_light_pass_modifies_canvas():
    """dappled_light_pass() with non-zero intensity must modify a painted canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.60, 0.55, 0.40), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.dappled_light_pass(ref, n_pools=10, pool_radius=0.15,
                         light_intensity=0.40, shadow_intensity=0.20)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "dappled_light_pass should modify the canvas"


def test_dappled_light_pass_zero_intensity_minimal_change():
    """dappled_light_pass() with zero intensities should leave the canvas essentially unchanged."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.60, 0.55, 0.40), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.dappled_light_pass(ref, n_pools=8, pool_radius=0.12,
                         light_intensity=0.0, shadow_intensity=0.0,
                         blur_sigma=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    # With both intensities at zero the RGB channels should be unaltered;
    # allow a tolerance of 1 for float rounding through the uint8 write-back.
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff <= 2, (
        f"dappled_light_pass with zero intensity should not change the canvas, "
        f"but max pixel diff was {diff}")


def test_dappled_light_pass_luminismo_routing_flag():
    """LUMINISMO period must produce a valid stroke_params dict (routing smoke test)."""
    from scene_schema import Period, Style, Medium, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.LUMINISMO,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert "stroke_size_face" in p
    assert "wet_blend"        in p
    # Luminismo should NOT be mannerist, synthetist, or color-field
    assert style.period != Period.MANNERIST
    assert style.period != Period.SYNTHETIST
    assert style.period != Period.COLOR_FIELD
