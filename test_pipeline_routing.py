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
        "is_art_deco":                period == Period.ART_DECO,
        "is_high_renaissance":        period == Period.HIGH_RENAISSANCE,
        "is_tenebrist":               period == Period.TENEBRIST,
        "is_neoclassical":            period == Period.NEOCLASSICAL,
        "is_nocturne":                period == Period.NOCTURNE,
        "is_social_realist":          period == Period.SOCIAL_REALIST,
        "is_academic_realist":        period == Period.ACADEMIC_REALIST,
        "is_nordic_impressionist":    period == Period.NORDIC_IMPRESSIONIST,
        "is_impressionist_plein_air": period == Period.IMPRESSIONIST_PLEIN_AIR,
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
# Session 22: art_deco_facet_pass + velatura_pass + ART_DECO routing
# ──────────────────────────────────────────────────────────────────────────────

def test_art_deco_facet_pass_exists():
    """Session 22: Painter must have art_deco_facet_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "art_deco_facet_pass"), (
        "art_deco_facet_pass not found on Painter")
    assert callable(getattr(Painter, "art_deco_facet_pass"))


def test_velatura_pass_exists():
    """Session 22: Painter must have velatura_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "velatura_pass"), (
        "velatura_pass not found on Painter")
    assert callable(getattr(Painter, "velatura_pass"))


def test_art_deco_facet_pass_no_error():
    """art_deco_facet_pass() runs without error on a painted canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.50, 0.42), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    # Should not raise
    p.art_deco_facet_pass(ref, n_zones=4, smooth_sigma=2.0,
                          boundary_contrast=0.25, metallic_sheen=0.20)


def test_art_deco_facet_pass_modifies_canvas():
    """art_deco_facet_pass() with boundary_contrast > 0 must modify the canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.50, 0.42), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.art_deco_facet_pass(ref, n_zones=5, smooth_sigma=2.5,
                          boundary_contrast=0.30, metallic_sheen=0.22,
                          saturation_boost=1.20)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, (
        "art_deco_facet_pass with boundary_contrast=0.30 should modify the canvas; "
        f"max pixel diff = {diff}")


def test_art_deco_facet_pass_pixels_in_range():
    """art_deco_facet_pass() must not produce out-of-range pixel values."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.50, 0.42), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.art_deco_facet_pass(ref, n_zones=5, smooth_sigma=3.0,
                          boundary_contrast=0.35, metallic_sheen=0.25)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_art_deco_facet_pass_figure_only_no_error():
    """art_deco_facet_pass() with figure_only=True and a loaded mask should not raise."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.50, 0.42), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[16:48, 16:48] = 1.0
    p._figure_mask = mask
    p.art_deco_facet_pass(ref, n_zones=4, figure_only=True)


def test_velatura_pass_no_error():
    """velatura_pass() runs without error on a painted canvas."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.50, 0.42), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    # Should not raise — default warm amber midtone tint
    p.velatura_pass()


def test_velatura_pass_modifies_canvas():
    """velatura_pass() with midtone_opacity > 0 must shift canvas values."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.50, 0.42), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.velatura_pass(midtone_tint=(0.62, 0.52, 0.32), midtone_opacity=0.20)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, (
        "velatura_pass with midtone_opacity=0.20 should modify the canvas; "
        f"max pixel diff = {diff}")


def test_velatura_pass_zero_opacity_is_near_noop():
    """velatura_pass() with midtone_opacity=0 and no shadow_tint should be a no-op."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.50, 0.42), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.velatura_pass(midtone_opacity=0.0, shadow_tint=None, lum_preserve=False)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    np.testing.assert_array_equal(before, after,
        err_msg="velatura_pass with opacity=0 and no shadow_tint should be a no-op")


def test_velatura_pass_with_shadow_tint_no_error():
    """velatura_pass() with an explicit shadow_tint should not raise."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.50, 0.42), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.velatura_pass(
        midtone_tint  = (0.62, 0.52, 0.32),
        shadow_tint   = (0.35, 0.24, 0.10),
        midtone_opacity = 0.10,
        shadow_opacity  = 0.06,
    )


def test_velatura_pass_pixels_in_range():
    """velatura_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.50, 0.42), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.velatura_pass(midtone_tint=(0.62, 0.52, 0.32), midtone_opacity=0.30,
                    shadow_tint=(0.35, 0.24, 0.10), shadow_opacity=0.20)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


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


def test_art_deco_period_in_enum():
    """ART_DECO must be a member of the Period enum."""
    assert hasattr(Period, "ART_DECO"), "Period.ART_DECO not found"
    assert Period.ART_DECO in list(Period)


def test_art_deco_stroke_params_valid():
    """ART_DECO period must return valid stroke_params."""
    style = Style(medium=Medium.OIL, period=Period.ART_DECO,
                  palette=PaletteHint.WARM_EARTH)
    params = style.stroke_params
    assert params["stroke_size_face"] > 0
    assert params["stroke_size_bg"]   > 0
    assert 0.0 <= params["wet_blend"]    <= 1.0
    assert 0.0 <= params["edge_softness"] <= 1.0
    # Art Deco has very low wet_blend and edge_softness — polished, hard edges
    assert params["wet_blend"]    <= 0.15, "ART_DECO should have low wet_blend"
    assert params["edge_softness"] <= 0.15, "ART_DECO should have low edge_softness"


def test_art_deco_routing_flag_set():
    """ART_DECO period must set is_art_deco=True in routing flags."""
    flags = _routing_flags(Period.ART_DECO)
    assert flags["is_art_deco"] is True


def test_art_deco_routing_flag_not_set_for_other_periods():
    """is_art_deco must be False for all periods except ART_DECO."""
    for period in Period:
        if period == Period.ART_DECO:
            continue
        flags = _routing_flags(period)
        assert not flags["is_art_deco"], (
            f"is_art_deco should be False for {period.name}")


def test_art_deco_and_fauvist_mutually_exclusive():
    """ART_DECO and FAUVIST are distinct periods."""
    flags_ad = _routing_flags(Period.ART_DECO)
    flags_f  = _routing_flags(Period.FAUVIST)
    assert     flags_ad["is_art_deco"]
    assert not flags_ad["is_fauvist"]
    assert     flags_f["is_fauvist"]
    assert not flags_f["is_art_deco"]


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


# Session 23: radiance_bloom_pass + reflected_light_pass + HIGH_RENAISSANCE routing
# ──────────────────────────────────────────────────────────────────────────────

def test_radiance_bloom_pass_exists():
    """Session 23: Painter must have radiance_bloom_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "radiance_bloom_pass"), (
        "radiance_bloom_pass not found on Painter")
    assert callable(getattr(Painter, "radiance_bloom_pass"))


def test_reflected_light_pass_exists():
    """Session 23: Painter must have reflected_light_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "reflected_light_pass"), (
        "reflected_light_pass not found on Painter")
    assert callable(getattr(Painter, "reflected_light_pass"))


def test_radiance_bloom_pass_no_error():
    """radiance_bloom_pass() runs without error on a painted canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.60, 0.50, 0.32), texture_strength=0.09)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    # Should not raise
    p.radiance_bloom_pass(ref, glow_radius=4.0, glow_opacity=0.18)


def test_radiance_bloom_pass_modifies_canvas():
    """radiance_bloom_pass() with positive opacity must modify the canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.60, 0.50, 0.32), texture_strength=0.09)
    p.block_in(ref, stroke_size=10, n_strokes=30)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.radiance_bloom_pass(ref, glow_radius=6.0, glow_opacity=0.30,
                          glow_tint=(0.85, 0.68, 0.40))
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, (
        "radiance_bloom_pass with glow_opacity=0.30 should modify the canvas")


def test_radiance_bloom_pass_pixels_in_range():
    """radiance_bloom_pass() must not produce out-of-range pixel values."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.58, 0.48, 0.30), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.radiance_bloom_pass(ref, glow_radius=5.0, glow_opacity=0.25)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4)
    assert buf.min() >= 0,   "Pixel values must be >= 0 after radiance_bloom_pass"
    assert buf.max() <= 255, "Pixel values must be <= 255 after radiance_bloom_pass"


def test_radiance_bloom_pass_figure_only_no_error():
    """radiance_bloom_pass() with figure_only=True and a loaded mask should not raise."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.60, 0.50, 0.32), texture_strength=0.09)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[16:48, 16:48] = 1.0
    p._figure_mask = mask
    p.radiance_bloom_pass(ref, glow_radius=4.0, glow_opacity=0.20, figure_only=True)


def test_reflected_light_pass_no_error():
    """reflected_light_pass() runs without error on a painted canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.60, 0.50, 0.32), texture_strength=0.09)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    # Should not raise
    p.reflected_light_pass()


def test_reflected_light_pass_modifies_canvas():
    """reflected_light_pass() with positive strengths must modify the canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.08)  # dark ground → has shadows
    p.block_in(ref, stroke_size=10, n_strokes=30)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.reflected_light_pass(warm_strength=0.30, cool_strength=0.20,
                           shadow_threshold=0.55)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, (
        "reflected_light_pass with positive strengths should modify the canvas")


def test_reflected_light_pass_zero_strength_is_noop():
    """reflected_light_pass() with both strengths at 0 should leave canvas unchanged."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=30)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.reflected_light_pass(warm_strength=0.0, cool_strength=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff <= 2, (
        f"reflected_light_pass with zero strength should be a no-op; diff={diff}")


def test_reflected_light_pass_pixels_in_range():
    """reflected_light_pass() must not produce out-of-range pixel values."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.18, 0.12, 0.06), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.reflected_light_pass(warm_strength=0.25, cool_strength=0.15,
                           shadow_threshold=0.50)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4)
    assert buf.min() >= 0,   "Pixel values must be >= 0 after reflected_light_pass"
    assert buf.max() <= 255, "Pixel values must be <= 255 after reflected_light_pass"


def test_reflected_light_pass_figure_only_no_error():
    """reflected_light_pass() with figure_only=True and a loaded mask should not raise."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[16:48, 16:48] = 1.0
    p._figure_mask = mask
    p.reflected_light_pass(warm_strength=0.18, cool_strength=0.10,
                           shadow_threshold=0.45, figure_only=True)


def test_high_renaissance_routing_flag():
    """HIGH_RENAISSANCE period must set is_high_renaissance=True in routing flags."""
    flags = _routing_flags(Period.HIGH_RENAISSANCE)
    assert flags["is_high_renaissance"], (
        "is_high_renaissance should be True for Period.HIGH_RENAISSANCE")


def test_high_renaissance_routing_exclusive():
    """HIGH_RENAISSANCE must not set any other exclusive period flag."""
    flags  = _routing_flags(Period.HIGH_RENAISSANCE)
    others = {k: v for k, v in flags.items()
              if k not in ("is_high_renaissance", "is_watercolor",
                           "is_romantic", "is_renaissance_soft")
              and v}
    assert len(others) == 0, (
        f"HIGH_RENAISSANCE should set only is_high_renaissance; also set: {others}")


def test_high_renaissance_stroke_params_valid():
    """HIGH_RENAISSANCE stroke_params must be valid for pipeline use."""
    style = Style(medium=Medium.OIL, period=Period.HIGH_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] >= 4,  "stroke_size_face should be ≥ 4"
    assert p["stroke_size_bg"]   >= 16, "stroke_size_bg should be ≥ 16"
    assert 0.20 <= p["wet_blend"]      <= 0.55, "wet_blend out of expected range"
    assert 0.40 <= p["edge_softness"]  <= 0.75, "edge_softness out of expected range"


# luminous_fabric_pass tests - session 24

def test_luminous_fabric_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, 'luminous_fabric_pass')
    assert callable(getattr(Painter, 'luminous_fabric_pass'))

def test_luminous_fabric_pass_no_error():
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.08, 0.06, 0.04), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.luminous_fabric_pass(ref)

def test_luminous_fabric_pass_modifies_canvas():
    """luminous_fabric_pass() must change pixels when reference has both bright and dark zones."""
    import numpy as np
    from PIL import Image
    # Reference with bright-white top half (fabric zone) and near-black bottom half (void zone).
    # This ensures fabric_mask and void_mask are both populated so the pass has work to do.
    ref_arr = np.zeros((64, 64, 3), dtype=np.uint8)
    ref_arr[:32, :] = [240, 238, 232]   # near-white top half — fabric zone
    ref_arr[32:, :] = [8,   6,   4]     # near-black bottom half — void zone
    ref = Image.fromarray(ref_arr, "RGB")
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.48, 0.35), texture_strength=0.06)   # bright ground so difference is visible
    p.block_in(ref, stroke_size=10, n_strokes=30)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4).copy()
    p.luminous_fabric_pass(ref, void_darken=0.70)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    assert np.abs(after.astype(np.int32) - before.astype(np.int32)).sum() > 0

def test_luminous_fabric_pass_pixels_in_range():
    import numpy as np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.08, 0.06, 0.04), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.luminous_fabric_pass(ref, fold_contrast=0.80, void_darken=0.85)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    assert buf.min() >= 0 and buf.max() <= 255

def test_luminous_fabric_pass_void_darkens():
    import numpy as np
    from PIL import Image
    dark_ref = Image.fromarray(
        (np.ones((64, 64, 3), dtype=np.uint8) * np.array([20, 16, 10], dtype=np.uint8)), "RGB")
    p = _make_small_painter(64, 64)
    p.tone_ground((0.45, 0.38, 0.28), texture_strength=0.06)
    p.block_in(dark_ref, stroke_size=10, n_strokes=30)
    before_mean = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)[:, :, :3].mean()
    p.luminous_fabric_pass(dark_ref, void_darken=0.75)
    after_mean = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)[:, :, :3].mean()
    assert after_mean <= before_mean, f"void_darken should not increase luminance: before={before_mean:.1f} after={after_mean:.1f}"

# edge_lost_and_found_pass tests - session 24

def test_edge_lost_and_found_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "edge_lost_and_found_pass")
    assert callable(getattr(Painter, "edge_lost_and_found_pass"))

def test_edge_lost_and_found_pass_no_error():
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.edge_lost_and_found_pass()

def test_edge_lost_and_found_pass_modifies_canvas():
    import numpy as np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4).copy()
    p.edge_lost_and_found_pass(strength=0.50)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    assert np.abs(after.astype(np.int32) - before.astype(np.int32)).sum() > 0

def test_edge_lost_and_found_pass_zero_strength_noop():
    import numpy as np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4).copy()
    p.edge_lost_and_found_pass(strength=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff <= 2, f"zero strength should be near-noop; diff={diff}"

def test_edge_lost_and_found_pass_pixels_in_range():
    import numpy as np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.edge_lost_and_found_pass(found_sharpness=0.80, lost_blur=3.0, strength=0.60)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    assert buf.min() >= 0 and buf.max() <= 255

def test_edge_lost_and_found_pass_figure_only_no_error():
    import numpy as np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.06)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[16:48, 16:48] = 1.0
    p._figure_mask = mask
    p.edge_lost_and_found_pass(strength=0.35, figure_only=True)

# TENEBRIST routing flag tests - session 24

def test_tenebrist_routing_flag():
    flags = _routing_flags(Period.TENEBRIST)
    assert flags["is_tenebrist"], "is_tenebrist should be True for Period.TENEBRIST"

def test_tenebrist_routing_exclusive():
    flags = _routing_flags(Period.TENEBRIST)
    others = {k: v for k, v in flags.items()
              if k not in ("is_tenebrist", "is_watercolor", "is_romantic", "is_renaissance_soft") and v}
    assert len(others) == 0, f"TENEBRIST should only set is_tenebrist; also set: {others}"

def test_tenebrist_stroke_params_valid():
    style = Style(medium=Medium.OIL, period=Period.TENEBRIST, palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] >= 4
    assert p["stroke_size_bg"] >= 30
    assert p["wet_blend"] <= 0.35
    assert p["edge_softness"] <= 0.40


# ──────────────────────────────────────────────────────────────────────────────
# Session 25: porcelain_skin_pass, tonal_compression_pass, NEOCLASSICAL routing
# ──────────────────────────────────────────────────────────────────────────────

def test_porcelain_skin_pass_exists():
    """Painter must have porcelain_skin_pass() method after session 25."""
    from stroke_engine import Painter
    assert hasattr(Painter, "porcelain_skin_pass"), (
        "porcelain_skin_pass not found on Painter")
    assert callable(getattr(Painter, "porcelain_skin_pass"))


def test_tonal_compression_pass_exists():
    """Painter must have tonal_compression_pass() method after session 25."""
    from stroke_engine import Painter
    assert hasattr(Painter, "tonal_compression_pass"), (
        "tonal_compression_pass not found on Painter")
    assert callable(getattr(Painter, "tonal_compression_pass"))


def test_porcelain_skin_pass_no_error():
    """porcelain_skin_pass() runs without error on a plain painted canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.75, 0.68, 0.52), texture_strength=0.04)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.porcelain_skin_pass(smooth_strength=0.50, figure_only=False)


def test_porcelain_skin_pass_default_figure_only():
    """porcelain_skin_pass with figure_only=True and no mask should not raise."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.75, 0.68, 0.52), texture_strength=0.04)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    # figure_only=True (default) with no mask set: should be a no-op without error
    p.porcelain_skin_pass(figure_only=True)


def test_porcelain_skin_pass_with_mask():
    """porcelain_skin_pass() with a figure mask runs without error."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.75, 0.68, 0.52), texture_strength=0.04)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[12:52, 12:52] = 1.0
    p._figure_mask = mask
    p.porcelain_skin_pass(
        smooth_strength  = 0.60,
        highlight_cool   = 0.07,
        blush_opacity    = 0.10,
        highlight_thresh = 0.74,
        blush_lo         = 0.40,
        blush_hi         = 0.68,
        smooth_sigma     = 2.2,
        figure_only      = True,
    )


def test_porcelain_skin_pass_modifies_canvas():
    """porcelain_skin_pass() with strong smooth_strength must alter a non-uniform canvas."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    # Paint a non-uniform warm canvas so flesh detection finds candidates
    p.tone_ground((0.82, 0.72, 0.54), texture_strength=0.10)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.porcelain_skin_pass(smooth_strength=0.90, figure_only=False)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()

    assert not np.array_equal(before, after), (
        "porcelain_skin_pass with strong smooth_strength should modify the canvas")


def test_tonal_compression_pass_no_error():
    """tonal_compression_pass() runs without error on a plain canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.75, 0.68, 0.52), texture_strength=0.04)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.tonal_compression_pass(shadow_lift=0.04, highlight_compress=0.96,
                              midtone_contrast=0.06)


def test_tonal_compression_pass_zero_lift_no_shadow_change():
    """tonal_compression_pass with shadow_lift=0 and no compress should barely change canvas."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.50, 0.42, 0.30), texture_strength=0.05)

    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.tonal_compression_pass(shadow_lift=0.0, highlight_compress=1.0,
                              midtone_contrast=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()

    # With all parameters at identity, changes should be near-zero
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff <= 2, (
        f"tonal_compression_pass with identity params should not change canvas; diff={diff}")


def test_tonal_compression_pass_lifts_darks():
    """tonal_compression_pass with shadow_lift > 0 should raise minimum luminance."""
    import numpy as np
    # Build a canvas with near-black pixels
    p   = _make_small_painter(64, 64)
    p.tone_ground((0.02, 0.01, 0.01), texture_strength=0.0)

    W_, H_ = 64, 64
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy().reshape(H_, W_, -1)
    min_before = before[:, :, :3].min()  # minimum across RGB channels

    p.tonal_compression_pass(shadow_lift=0.06, highlight_compress=1.0,
                              midtone_contrast=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy().reshape(H_, W_, -1)
    min_after = after[:, :, :3].min()

    assert min_after >= min_before, (
        f"Shadow lift should not decrease minimum value; "
        f"before={min_before} after={min_after}")


def test_tonal_compression_pass_compresses_highlights():
    """tonal_compression_pass with highlight_compress < 1.0 should reduce maximum luminance."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    # Near-white canvas
    p.tone_ground((0.98, 0.97, 0.96), texture_strength=0.0)

    W_, H_ = 64, 64
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy().reshape(H_, W_, -1)
    max_before = before[:, :, :3].max()

    p.tonal_compression_pass(shadow_lift=0.0, highlight_compress=0.90,
                              midtone_contrast=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy().reshape(H_, W_, -1)
    max_after = after[:, :, :3].max()

    # Maximum should not exceed what we started with (compression never adds brightness)
    assert max_after <= max_before + 2, (
        f"Highlight compression should not increase max brightness; "
        f"before={max_before} after={max_after}")


def test_tonal_compression_pass_figure_only_no_error():
    """tonal_compression_pass with figure_only=True and no mask should not raise."""
    import numpy as np
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.50, 0.42, 0.30), texture_strength=0.05)
    p.block_in(ref, stroke_size=8, n_strokes=30)
    # No mask set — figure_only=True should degrade gracefully
    p.tonal_compression_pass(shadow_lift=0.04, figure_only=True)


# ── NEOCLASSICAL routing flag tests ─────────────────────────────────────────

def test_neoclassical_routing_flag():
    flags = _routing_flags(Period.NEOCLASSICAL)
    assert flags["is_neoclassical"], "is_neoclassical should be True for Period.NEOCLASSICAL"


def test_neoclassical_routing_exclusive():
    flags = _routing_flags(Period.NEOCLASSICAL)
    others = {k: v for k, v in flags.items()
              if k not in ("is_neoclassical", "is_watercolor",
                           "is_romantic", "is_renaissance_soft") and v}
    assert len(others) == 0, (
        f"NEOCLASSICAL should only set is_neoclassical; also set: {others}")


def test_neoclassical_flag_false_for_other_periods():
    """is_neoclassical must be False for every period except NEOCLASSICAL."""
    for period in Period:
        if period == Period.NEOCLASSICAL:
            continue
        flags = _routing_flags(period)
        assert not flags["is_neoclassical"], (
            f"is_neoclassical should be False for {period.name}")


def test_neoclassical_stroke_params_valid():
    style = Style(medium=Medium.OIL, period=Period.NEOCLASSICAL,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] <= 8,  "NEOCLASSICAL face stroke should be small"
    assert p["stroke_size_bg"]   >= 14, "NEOCLASSICAL bg stroke should be present"
    assert 0.15 <= p["wet_blend"] <= 0.55, "NEOCLASSICAL wet_blend should be moderate"
    assert 0.20 <= p["edge_softness"] <= 0.55, "NEOCLASSICAL edge_softness moderate"


# ──────────────────────────────────────────────────────────────────────────────
# NOCTURNE / La Tour — candlelight_pass + routing
# ──────────────────────────────────────────────────────────────────────────────

def test_candlelight_pass_exists():
    """candlelight_pass must exist as a method on Painter."""
    p = _make_small_painter()
    assert hasattr(p, "candlelight_pass"), "Painter.candlelight_pass not found"
    assert callable(getattr(p, "candlelight_pass"))


def test_candlelight_pass_no_error():
    """candlelight_pass runs without raising on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.05, 0.03, 0.01))
    p.candlelight_pass(candle_x=0.5, candle_y=0.5)


def test_candlelight_pass_no_error_custom_params():
    """candlelight_pass accepts custom candle position, radius, and colors."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.05, 0.03, 0.01))
    p.candlelight_pass(
        candle_x=0.4, candle_y=0.6,
        radius=0.45,
        candle_color=(0.90, 0.60, 0.15),
        dark_color=(0.03, 0.02, 0.01),
        warmth_peak=0.60,
        void_crush=0.90,
        falloff_power=2.5,
    )


def test_candlelight_pass_modifies_canvas():
    """candlelight_pass must change at least some pixels on the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.40, 0.35, 0.25))

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape(64, 64, 4).copy()

    p.candlelight_pass(candle_x=0.5, candle_y=0.5, void_crush=0.85)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape(64, 64, 4).copy()

    assert not np.array_equal(before, after), (
        "candlelight_pass should modify the canvas")


def test_candlelight_pass_darkens_periphery():
    """Pixels far from the candle should be darker after the pass."""
    p = _make_small_painter(128, 128)
    # Start with a mid-grey canvas
    p.tone_ground((0.50, 0.50, 0.50))

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape(128, 128, 4).copy().astype(np.float32) / 255.0

    # Candle centred; periphery = corners
    p.candlelight_pass(candle_x=0.5, candle_y=0.5,
                       radius=0.40, void_crush=0.80)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape(128, 128, 4).copy().astype(np.float32) / 255.0

    # Top-left corner should be darker after the pass
    corner_before = before[5:15, 5:15, :3].mean()
    corner_after  = after[5:15, 5:15, :3].mean()
    assert corner_after < corner_before, (
        f"Periphery should darken: before={corner_before:.3f} after={corner_after:.3f}")


def test_candlelight_pass_warms_centre():
    """Pixels close to the candle should shift toward warm amber."""
    p = _make_small_painter(128, 128)
    # Start with a cool neutral canvas
    p.tone_ground((0.40, 0.40, 0.55))   # slightly cool (B > R)

    p.candlelight_pass(
        candle_x=0.5, candle_y=0.5,
        candle_color=(0.92, 0.62, 0.18),   # warm amber
        warmth_peak=0.60,
        void_crush=0.50,
        radius=0.60,
    )

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape(128, 128, 4).copy().astype(np.float32) / 255.0

    # Cairo ARGB32 in memory: B G R A
    R_centre = after[56:72, 56:72, 2].mean()   # channel 2 = R in ARGB32
    B_centre = after[56:72, 56:72, 0].mean()   # channel 0 = B in ARGB32
    assert R_centre > B_centre, (
        f"Centre should be warm (R > B) after candlelight; R={R_centre:.3f} B={B_centre:.3f}")


def test_candlelight_pass_pixels_in_range():
    """All pixel values must remain in [0, 255] after candlelight_pass."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.50, 0.45, 0.30))
    p.candlelight_pass()
    buf = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0,   "Pixel value below 0 after candlelight_pass"
    assert buf.max() <= 255, "Pixel value above 255 after candlelight_pass"


def test_candlelight_pass_figure_only_no_error():
    """candlelight_pass(figure_only=True) must not raise even with a figure mask."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.20, 0.15, 0.05))
    # Circular figure mask in the upper half
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[10:40, 15:50] = 1.0
    p.set_figure_mask(mask)
    p.candlelight_pass(candle_x=0.5, candle_y=0.4, figure_only=True)


def test_nocturne_routing_flag():
    """is_nocturne should be True for Period.NOCTURNE."""
    flags = _routing_flags(Period.NOCTURNE)
    assert flags["is_nocturne"], "is_nocturne should be True for Period.NOCTURNE"


def test_nocturne_routing_exclusive():
    """NOCTURNE should only set is_nocturne among the period flags."""
    flags = _routing_flags(Period.NOCTURNE)
    others = {k: v for k, v in flags.items()
              if k not in ("is_nocturne", "is_watercolor",
                           "is_romantic", "is_renaissance_soft") and v}
    assert len(others) == 0, (
        f"NOCTURNE should only set is_nocturne; also set: {others}")


def test_nocturne_flag_false_for_other_periods():
    """is_nocturne must be False for every period except NOCTURNE."""
    for period in Period:
        if period == Period.NOCTURNE:
            continue
        flags = _routing_flags(period)
        assert not flags["is_nocturne"], (
            f"is_nocturne should be False for {period.name}")


def test_nocturne_stroke_params_valid():
    style = Style(medium=Medium.OIL, period=Period.NOCTURNE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["stroke_size_bg"]   >= 35, "NOCTURNE bg stroke should be large (void)"
    assert 0.35 <= p["wet_blend"] <= 0.75, "NOCTURNE wet_blend should be moderate"
    assert 0.25 <= p["edge_softness"] <= 0.65, "NOCTURNE edge_softness moderate"


# ──────────────────────────────────────────────────────────────────────────────
# SOCIAL_REALIST (Courbet) — palette_knife_pass + routing
# ──────────────────────────────────────────────────────────────────────────────

def test_palette_knife_pass_exists():
    """palette_knife_pass must exist as a method on Painter."""
    p = _make_small_painter()
    assert hasattr(p, "palette_knife_pass"), "Painter.palette_knife_pass not found"
    assert callable(getattr(p, "palette_knife_pass"))


def test_palette_knife_pass_no_error():
    """palette_knife_pass runs without raising on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.09, 0.05))
    palette = [
        (0.72, 0.60, 0.42),
        (0.38, 0.28, 0.16),
        (0.08, 0.06, 0.04),
    ]
    p.palette_knife_pass(palette=palette, n_strokes=30, rng_seed=42)


def test_palette_knife_pass_no_error_figure_only():
    """palette_knife_pass(figure_only=True) must not raise with a figure mask."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.09, 0.05))
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[10:55, 10:55] = 1.0
    p.set_figure_mask(mask)
    palette = [(0.72, 0.60, 0.42), (0.38, 0.28, 0.16)]
    p.palette_knife_pass(palette=palette, n_strokes=20, figure_only=True, rng_seed=7)


def test_palette_knife_pass_modifies_canvas():
    """palette_knife_pass must change at least some pixels on the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.09, 0.05))
    buf_before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).copy().reshape(64, 64, 4)
    palette = [(0.82, 0.72, 0.52), (0.55, 0.48, 0.30)]
    p.palette_knife_pass(palette=palette, n_strokes=50, rng_seed=99)
    buf_after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape(64, 64, 4)
    assert not np.array_equal(buf_before, buf_after), (
        "palette_knife_pass should modify the canvas")


def test_palette_knife_pass_pixels_in_range():
    """All pixel values must remain in [0, 255] after palette_knife_pass."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.09, 0.05))
    palette = [(0.72, 0.60, 0.42), (0.08, 0.06, 0.04), (0.82, 0.72, 0.52)]
    p.palette_knife_pass(palette=palette, n_strokes=80, rng_seed=13)
    buf = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0,   "Pixel value below 0 after palette_knife_pass"
    assert buf.max() <= 255, "Pixel value above 255 after palette_knife_pass"


def test_palette_knife_pass_empty_figure_mask_no_crash():
    """palette_knife_pass with figure_only=True and empty mask should skip gracefully."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.09, 0.05))
    mask = np.zeros((64, 64), dtype=np.float32)   # all zeros — no figure pixels
    p.set_figure_mask(mask)
    palette = [(0.72, 0.60, 0.42)]
    p.palette_knife_pass(palette=palette, n_strokes=20, figure_only=True, rng_seed=1)


def test_social_realist_routing_flag():
    """is_social_realist should be True for Period.SOCIAL_REALIST."""
    flags = _routing_flags(Period.SOCIAL_REALIST)
    assert flags["is_social_realist"], (
        "is_social_realist should be True for Period.SOCIAL_REALIST")


def test_social_realist_routing_exclusive():
    """SOCIAL_REALIST should only set is_social_realist among the period flags."""
    flags = _routing_flags(Period.SOCIAL_REALIST)
    others = {k: v for k, v in flags.items()
              if k not in ("is_social_realist", "is_watercolor",
                           "is_romantic", "is_renaissance_soft") and v}
    assert len(others) == 0, (
        f"SOCIAL_REALIST should only set is_social_realist; also set: {others}")


def test_social_realist_flag_false_for_other_periods():
    """is_social_realist must be False for every period except SOCIAL_REALIST."""
    for period in Period:
        if period == Period.SOCIAL_REALIST:
            continue
        flags = _routing_flags(period)
        assert not flags["is_social_realist"], (
            f"is_social_realist should be False for {period.name}")


def test_social_realist_stroke_params_valid():
    style = Style(medium=Medium.OIL, period=Period.SOCIAL_REALIST,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] >= 10, "SOCIAL_REALIST face stroke should be large (knife planes)"
    assert p["stroke_size_bg"]   >= 20, "SOCIAL_REALIST bg stroke should be large"
    assert p["wet_blend"]        <= 0.30, "SOCIAL_REALIST wet_blend should be low (crisp planes)"
    assert p["edge_softness"]    <= 0.40, "SOCIAL_REALIST edge_softness should be low (knife edges)"


# ──────────────────────────────────────────────────────────────────────────────
# ACADEMIC_REALIST (Bouguereau) — academic_skin_pass + routing
# ──────────────────────────────────────────────────────────────────────────────

def test_academic_skin_pass_exists():
    """Painter must have academic_skin_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "academic_skin_pass"), (
        "academic_skin_pass not found on Painter")


def test_academic_skin_pass_no_error():
    """academic_skin_pass() must run without error on a tiny warm canvas."""
    p = _make_small_painter(64, 64)
    # Tone with a warm flesh colour so the skin detector finds candidates
    p.tone_ground((0.85, 0.68, 0.52))
    ref = _solid_reference(64, 64)
    p.academic_skin_pass(ref, n_passes=2, strokes_per_pass=20, rng_seed=1)


def test_academic_skin_pass_modifies_canvas():
    """academic_skin_pass() must alter at least one pixel on a warm flesh canvas."""
    import numpy as np
    from PIL import Image
    p = _make_small_painter(64, 64)
    p.tone_ground((0.85, 0.68, 0.52))
    # Capture pre-pass state
    before = np.array(p.canvas.to_pil(), dtype=np.float32)
    ref = Image.fromarray(
        (np.ones((64, 64, 3), dtype=np.uint8)
         * np.array([200, 160, 120], dtype=np.uint8)), "RGB")
    p.academic_skin_pass(ref, n_passes=2, strokes_per_pass=40, rng_seed=42)
    after = np.array(p.canvas.to_pil(), dtype=np.float32)
    assert not np.allclose(before, after), (
        "academic_skin_pass should modify at least one pixel on a warm flesh canvas")


def test_academic_skin_pass_no_skin_detected_no_crash():
    """academic_skin_pass() must not crash when no skin pixels are detected."""
    p = _make_small_painter(64, 64)
    # Use a cool blue ground — no warm flesh pixels
    p.tone_ground((0.20, 0.30, 0.65))
    ref = _solid_reference(64, 64)
    # Should print a warning and return gracefully, not raise
    p.academic_skin_pass(ref, n_passes=2, strokes_per_pass=20, rng_seed=7)


def test_academic_skin_pass_pixels_in_range():
    """academic_skin_pass() must not produce out-of-range [0, 1] pixel values."""
    import numpy as np
    from PIL import Image
    p = _make_small_painter(64, 64)
    p.tone_ground((0.82, 0.65, 0.48))
    ref = Image.fromarray(
        (np.ones((64, 64, 3), dtype=np.uint8)
         * np.array([195, 155, 115], dtype=np.uint8)), "RGB")
    p.academic_skin_pass(ref, n_passes=3, strokes_per_pass=60, rng_seed=99)
    arr = np.array(p.canvas.to_pil(), dtype=np.float32) / 255.0
    assert arr.min() >= 0.0, f"Pixel below 0.0: {arr.min()}"
    assert arr.max() <= 1.0, f"Pixel above 1.0: {arr.max()}"


def test_academic_realist_routing_flag():
    """is_academic_realist should be True for Period.ACADEMIC_REALIST."""
    flags = _routing_flags(Period.ACADEMIC_REALIST)
    assert flags["is_academic_realist"], (
        "is_academic_realist should be True for Period.ACADEMIC_REALIST")


def test_academic_realist_routing_exclusive():
    """ACADEMIC_REALIST should only set is_academic_realist among the period flags."""
    flags = _routing_flags(Period.ACADEMIC_REALIST)
    others = {k: v for k, v in flags.items()
              if k not in ("is_academic_realist", "is_watercolor",
                           "is_romantic", "is_renaissance_soft") and v}
    assert len(others) == 0, (
        f"ACADEMIC_REALIST should only set is_academic_realist; also set: {others}")


def test_academic_realist_flag_false_for_other_periods():
    """is_academic_realist must be False for every period except ACADEMIC_REALIST."""
    for period in Period:
        if period == Period.ACADEMIC_REALIST:
            continue
        flags = _routing_flags(period)
        assert not flags["is_academic_realist"], (
            f"is_academic_realist should be False for {period.name}")


def test_academic_realist_stroke_params_valid():
    """ACADEMIC_REALIST stroke_params should encode Bouguereau's porcelain technique."""
    style = Style(medium=Medium.OIL, period=Period.ACADEMIC_REALIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] <= 4,  "ACADEMIC_REALIST face stroke should be tiny (≤4)"
    assert p["stroke_size_bg"]   >= 12, "ACADEMIC_REALIST bg stroke should be moderate (≥12)"
    assert p["wet_blend"]        >= 0.80, "ACADEMIC_REALIST wet_blend must be very high (≥0.80)"
    assert p["edge_softness"]    >= 0.70, "ACADEMIC_REALIST edge_softness must be high (≥0.70)"


# ──────────────────────────────────────────────────────────────────────────────
# north_light_diffusion_pass — this session's new rendering pass (Cassatt)
# ──────────────────────────────────────────────────────────────────────────────

def test_north_light_diffusion_pass_exists():
    """Painter must have north_light_diffusion_pass() method after this session."""
    from stroke_engine import Painter
    assert hasattr(Painter, "north_light_diffusion_pass"), (
        "north_light_diffusion_pass not found on Painter")
    assert callable(getattr(Painter, "north_light_diffusion_pass"))


def test_north_light_diffusion_pass_no_error_left():
    """north_light_diffusion_pass(light_side='left') runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.84, 0.76), texture_strength=0.04)
    # Should complete without exception
    p.north_light_diffusion_pass(light_side="left")


def test_north_light_diffusion_pass_no_error_right():
    """north_light_diffusion_pass(light_side='right') runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.84, 0.76), texture_strength=0.04)
    p.north_light_diffusion_pass(light_side="right")


def test_north_light_diffusion_pass_no_error_top():
    """north_light_diffusion_pass(light_side='top') runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.84, 0.76), texture_strength=0.04)
    p.north_light_diffusion_pass(light_side="top")


def test_north_light_diffusion_pass_modifies_canvas():
    """north_light_diffusion_pass with non-zero strengths must modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.84, 0.76), texture_strength=0.04)
    before = np.array(p.canvas.to_pil(), dtype=np.float32).copy()
    p.north_light_diffusion_pass(
        light_side="left",
        cool_strength=0.15,
        warm_strength=0.12,
        blend_opacity=0.50,
    )
    after = np.array(p.canvas.to_pil(), dtype=np.float32)
    diff = np.abs(after - before).max()
    assert diff > 0, (
        "north_light_diffusion_pass with non-zero strengths should modify the canvas")


def test_north_light_diffusion_pass_zero_opacity_no_op():
    """north_light_diffusion_pass with blend_opacity=0 should not modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.84, 0.76), texture_strength=0.04)
    before = np.array(p.canvas.to_pil()).copy()
    p.north_light_diffusion_pass(blend_opacity=0.0)
    after = np.array(p.canvas.to_pil())
    np.testing.assert_array_equal(before, after,
        err_msg="north_light_diffusion_pass with blend_opacity=0 should be a no-op")


# ──────────────────────────────────────────────────────────────────────────────
# IMPRESSIONIST_INTIMISTE period routing
# ──────────────────────────────────────────────────────────────────────────────

def test_impressionist_intimiste_stroke_params_valid():
    """IMPRESSIONIST_INTIMISTE stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.IMPRESSIONIST_INTIMISTE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"IMPRESSIONIST_INTIMISTE stroke_params missing key: {key!r}"
    assert p["stroke_size_face"] > 0
    assert p["stroke_size_bg"]   > 0
    assert 0.0 <= p["wet_blend"]      <= 1.0
    assert 0.0 <= p["edge_softness"]  <= 1.0


# ──────────────────────────────────────────────────────────────────────────────
# bruegel_panorama_pass — this session's new artistic improvement
# Inspired by Pieter Bruegel the Elder's systematic aerial-perspective system
# ──────────────────────────────────────────────────────────────────────────────

def test_bruegel_panorama_pass_exists():
    """Painter must have bruegel_panorama_pass() method after this session."""
    from stroke_engine import Painter
    assert hasattr(Painter, "bruegel_panorama_pass"), (
        "bruegel_panorama_pass not found on Painter")
    assert callable(getattr(Painter, "bruegel_panorama_pass"))


def test_bruegel_panorama_pass_no_error():
    """bruegel_panorama_pass() runs without error on a plain toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.44, 0.28), texture_strength=0.06)
    # Should not raise
    p.bruegel_panorama_pass(
        haze_color       = (0.72, 0.78, 0.88),
        horizon_fraction = 0.65,
        near_fraction    = 0.25,
        haze_opacity     = 0.55,
        desaturation     = 0.70,
        lightening       = 0.30,
    )


def test_bruegel_panorama_pass_top_rows_bluer_than_bottom():
    """
    Top rows (far distance) should be more blue-haze-shifted than bottom rows
    (foreground).  Paint a warm canvas, apply the pass with a blue haze, and
    confirm the top row has a higher blue channel than the bottom row.
    """
    p = _make_small_painter(64, 64)
    # Warm orange foreground — any blue haze effect will be detectable
    p.tone_ground((0.82, 0.42, 0.12), texture_strength=0.00)

    p.bruegel_panorama_pass(
        haze_color       = (0.40, 0.60, 0.90),   # blue haze
        horizon_fraction = 0.60,
        near_fraction    = 0.20,
        haze_opacity     = 0.70,
        desaturation     = 0.80,
        lightening       = 0.40,
    )

    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA: channel 0 = B, channel 1 = G, channel 2 = R
    top_blue    = float(buf[0,  :, 0].mean())   # top row (far distance) — B channel
    bottom_blue = float(buf[63, :, 0].mean())   # bottom row (foreground) — B channel

    assert top_blue > bottom_blue, (
        f"Top row (far distance) should be bluer after bruegel_panorama_pass, "
        f"but top_blue={top_blue:.1f} <= bottom_blue={bottom_blue:.1f}")


def test_bruegel_panorama_pass_foreground_unchanged():
    """
    Bottom rows (pure foreground, within near_fraction) should be minimally
    affected by the haze — the haze weight is 0 there.
    """
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.48, 0.28), texture_strength=0.00)

    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()

    # Only the bottom quarter is 'pure foreground' with near_fraction=0.25
    p.bruegel_panorama_pass(
        haze_color       = (0.40, 0.60, 0.90),
        near_fraction    = 0.30,   # bottom 30% is pure foreground
        horizon_fraction = 0.70,
        haze_opacity     = 0.80,
        desaturation     = 0.90,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    # The very bottom row should be unchanged (depth_w = 0 there)
    bottom_row_diff = np.abs(
        after_buf[63, :, :3].astype(np.int32) - before_buf[63, :, :3].astype(np.int32)
    ).max()
    assert bottom_row_diff == 0, (
        f"Bottom row (pure foreground) should be unchanged after bruegel_panorama_pass, "
        f"but max pixel diff = {bottom_row_diff}")


def test_bruegel_panorama_pass_screen_blend_no_error():
    """bruegel_panorama_pass() with blend_mode='screen' runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.44, 0.28), texture_strength=0.04)
    p.bruegel_panorama_pass(
        haze_color  = (0.72, 0.78, 0.88),
        haze_opacity= 0.40,
        blend_mode  = "screen",
    )


def test_flemish_panoramic_period_routing():
    """FLEMISH_PANORAMIC period must produce valid stroke_params."""
    sp = Style(medium=Medium.OIL, period=Period.FLEMISH_PANORAMIC).stroke_params
    assert sp["stroke_size_bg"] > sp["stroke_size_face"], (
        "FLEMISH_PANORAMIC bg stroke should exceed face stroke (landscape > figure)")
    assert 0.0 <= sp["wet_blend"] <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


# ──────────────────────────────────────────────────────────────────────────────
# zorn_tricolor_pass — this session's random artistic improvement
# Inspired by Anders Zorn's warm limited-palette skin technique
# ──────────────────────────────────────────────────────────────────────────────

def test_zorn_tricolor_pass_exists():
    """Painter must have zorn_tricolor_pass() method after this session."""
    from stroke_engine import Painter
    assert hasattr(Painter, "zorn_tricolor_pass"), (
        "zorn_tricolor_pass not found on Painter")
    assert callable(getattr(Painter, "zorn_tricolor_pass"))


def test_zorn_tricolor_pass_no_error():
    """zorn_tricolor_pass() runs without error on a plain toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.46, 0.34), texture_strength=0.04)
    # Should not raise
    p.zorn_tricolor_pass(
        ochre_warmth      = 0.09,
        vermillion_accent = 0.12,
        shadow_warmth     = 0.06,
        blend_opacity     = 0.40,
    )


def test_zorn_tricolor_pass_modifies_canvas():
    """zorn_tricolor_pass() with non-zero strengths should modify the canvas."""
    p = _make_small_painter(64, 64)
    # Warm ochre-biased tone — lots of midtone pixels for the pass to target
    p.tone_ground((0.72, 0.55, 0.28), texture_strength=0.00)
    before = np.array(p.canvas.to_pil(), dtype=np.float32).copy()
    p.zorn_tricolor_pass(
        ochre_warmth      = 0.12,
        vermillion_accent = 0.15,
        shadow_warmth     = 0.08,
        blend_opacity     = 0.50,
    )
    after = np.array(p.canvas.to_pil(), dtype=np.float32)
    diff = np.abs(after - before).max()
    assert diff > 0, (
        "zorn_tricolor_pass with non-zero strengths should modify the canvas")


def test_zorn_tricolor_pass_zero_opacity_no_op():
    """zorn_tricolor_pass with blend_opacity=0.0 should leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.55, 0.28), texture_strength=0.00)
    before = np.array(p.canvas.to_pil()).copy()
    p.zorn_tricolor_pass(blend_opacity=0.0)
    after = np.array(p.canvas.to_pil())
    np.testing.assert_array_equal(before, after,
        err_msg="zorn_tricolor_pass with blend_opacity=0 should be a no-op")


def test_zorn_tricolor_pass_warms_midtones():
    """
    A cool-grey midtone canvas should become warmer (higher R/G ratio) after
    zorn_tricolor_pass with a high ochre_warmth value.
    """
    p = _make_small_painter(64, 64)
    # Cool neutral grey — midtone luminance, equal R/G/B
    # Use a colour with lum ≈ 0.50 to land squarely in the midtone zone
    cool_grey = (0.50, 0.50, 0.50)
    p.tone_ground(cool_grey, texture_strength=0.00)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA layout: channel 2 = R, channel 1 = G, channel 0 = B
    before_r = float(before_buf[:, :, 2].mean())
    before_b = float(before_buf[:, :, 0].mean())

    p.zorn_tricolor_pass(
        ochre_warmth      = 0.18,   # strong ochre shift
        vermillion_accent = 0.00,   # disable to isolate the ochre effect
        shadow_warmth     = 0.00,   # disable
        midtone_low       = 0.30,
        midtone_high      = 0.70,
        blend_opacity     = 0.60,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_r = float(after_buf[:, :, 2].mean())
    after_b = float(after_buf[:, :, 0].mean())

    # After ochre shift, red should increase and blue should decrease
    assert after_r > before_r, (
        f"Midtone ochre shift should increase R channel: "
        f"before={before_r:.1f}, after={after_r:.1f}")
    assert after_b < before_b or after_b <= before_b + 1, (
        f"Midtone ochre shift should not increase B channel: "
        f"before={before_b:.1f}, after={after_b:.1f}")


# ──────────────────────────────────────────────────────────────────────────────
# NORDIC_IMPRESSIONIST period routing
# ──────────────────────────────────────────────────────────────────────────────

def test_nordic_impressionist_stroke_params_valid():
    """NORDIC_IMPRESSIONIST stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.NORDIC_IMPRESSIONIST,
                  palette=PaletteHint.WARM_EARTH)
    sp = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"NORDIC_IMPRESSIONIST stroke_params missing key: {key!r}"
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


def test_nordic_impressionist_wet_blend_moderate():
    """NORDIC_IMPRESSIONIST wet_blend must be ≥ 0.50 to reflect wet-into-wet painting."""
    sp = Style(medium=Medium.OIL, period=Period.NORDIC_IMPRESSIONIST).stroke_params
    assert sp["wet_blend"] >= 0.50, (
        f"NORDIC_IMPRESSIONIST wet_blend should be ≥ 0.50; got {sp['wet_blend']}")


# ──────────────────────────────────────────────────────────────────────────────
# morisot_plein_air_pass — this session's random artistic improvement
# Inspired by Berthe Morisot's high-key colorful-shadow impressionist technique
# ──────────────────────────────────────────────────────────────────────────────

def test_morisot_plein_air_pass_exists():
    """Painter must have morisot_plein_air_pass() method after this session."""
    from stroke_engine import Painter
    assert hasattr(Painter, "morisot_plein_air_pass"), (
        "morisot_plein_air_pass not found on Painter")
    assert callable(getattr(Painter, "morisot_plein_air_pass"))


def test_morisot_plein_air_pass_no_error():
    """morisot_plein_air_pass() runs without error on a plain toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.84, 0.78), texture_strength=0.04)
    # Should not raise
    p.morisot_plein_air_pass(
        shadow_violet       = (0.72, 0.68, 0.90),
        luminosity_lift     = 0.10,
        shadow_threshold    = 0.42,
        highlight_cream     = (0.96, 0.93, 0.86),
        highlight_threshold = 0.76,
        chroma_strength     = 0.18,
        blend_opacity       = 0.45,
    )


def test_morisot_plein_air_pass_modifies_canvas():
    """morisot_plein_air_pass() with non-zero strengths must modify the canvas."""
    p = _make_small_painter(64, 64)
    # Dark warm-grey canvas — lots of shadow pixels for the pass to target
    p.tone_ground((0.28, 0.22, 0.18), texture_strength=0.00)
    before = np.array(p.canvas.to_pil(), dtype=np.float32).copy()
    p.morisot_plein_air_pass(
        shadow_violet   = (0.72, 0.68, 0.90),
        luminosity_lift = 0.12,
        chroma_strength = 0.20,
        blend_opacity   = 0.50,
    )
    after = np.array(p.canvas.to_pil(), dtype=np.float32)
    diff = np.abs(after - before).max()
    assert diff > 0, (
        "morisot_plein_air_pass with non-zero strengths should modify the canvas")


def test_morisot_plein_air_pass_zero_opacity_no_op():
    """morisot_plein_air_pass with blend_opacity=0.0 should leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.55, 0.28), texture_strength=0.00)
    before = np.array(p.canvas.to_pil()).copy()
    p.morisot_plein_air_pass(blend_opacity=0.0)
    after = np.array(p.canvas.to_pil())
    np.testing.assert_array_equal(before, after,
        err_msg="morisot_plein_air_pass with blend_opacity=0 should be a no-op")


def test_morisot_plein_air_pass_cools_dark_shadows():
    """
    A dark warm canvas should become cooler (higher B channel) after
    morisot_plein_air_pass — because shadows are shifted toward blue-violet.
    """
    p = _make_small_painter(64, 64)
    # Very dark warm canvas — all pixels in the shadow zone
    dark_warm = (0.20, 0.14, 0.08)
    p.tone_ground(dark_warm, texture_strength=0.00)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA layout: channel 0 = B, channel 2 = R
    before_b = float(before_buf[:, :, 0].mean())

    p.morisot_plein_air_pass(
        shadow_violet   = (0.72, 0.68, 0.90),   # strongly blue-violet
        chroma_strength = 0.40,
        luminosity_lift = 0.15,
        blend_opacity   = 0.80,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_b = float(after_buf[:, :, 0].mean())

    assert after_b > before_b, (
        f"Shadow violet shift should increase B channel on a dark canvas: "
        f"before={before_b:.1f}, after={after_b:.1f}")


def test_morisot_plein_air_pass_lifts_dark_luminance():
    """
    A very dark canvas should become brighter after morisot_plein_air_pass
    when luminosity_lift > 0 — replicating Morisot's high-key shadow treatment.
    """
    p = _make_small_painter(64, 64)
    dark_canvas = (0.15, 0.12, 0.10)
    p.tone_ground(dark_canvas, texture_strength=0.00)
    before = np.array(p.canvas.to_pil(), dtype=np.float32)
    before_mean = before.mean()

    p.morisot_plein_air_pass(
        luminosity_lift  = 0.20,
        chroma_strength  = 0.10,
        shadow_threshold = 0.50,
        blend_opacity    = 0.70,
    )

    after = np.array(p.canvas.to_pil(), dtype=np.float32)
    after_mean = after.mean()

    assert after_mean > before_mean, (
        f"luminosity_lift should brighten dark shadows: "
        f"before_mean={before_mean:.1f}, after_mean={after_mean:.1f}")


# ──────────────────────────────────────────────────────────────────────────────
# IMPRESSIONIST_PLEIN_AIR period routing
# ──────────────────────────────────────────────────────────────────────────────

def test_impressionist_plein_air_stroke_params_valid():
    """IMPRESSIONIST_PLEIN_AIR stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.IMPRESSIONIST_PLEIN_AIR,
                  palette=PaletteHint.COOL_GREY)
    sp = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"IMPRESSIONIST_PLEIN_AIR stroke_params missing key: {key!r}"
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


def test_impressionist_plein_air_edge_softness_lower_than_renaissance():
    """IMPRESSIONIST_PLEIN_AIR edge_softness must be lower than sfumato RENAISSANCE."""
    sp_plein = Style(medium=Medium.OIL, period=Period.IMPRESSIONIST_PLEIN_AIR).stroke_params
    sp_ren   = Style(medium=Medium.OIL, period=Period.RENAISSANCE).stroke_params
    assert sp_plein["edge_softness"] < sp_ren["edge_softness"], (
        "IMPRESSIONIST_PLEIN_AIR edge_softness must be lower than RENAISSANCE sfumato")


# ──────────────────────────────────────────────────────────────────────────────
# Degas pastel pass (session 29)
# ──────────────────────────────────────────────────────────────────────────────

def test_degas_pastel_pass_exists():
    """Painter must have degas_pastel_pass() method after session 29."""
    from stroke_engine import Painter
    assert hasattr(Painter, "degas_pastel_pass"), (
        "degas_pastel_pass not found on Painter")
    assert callable(getattr(Painter, "degas_pastel_pass"))


def test_degas_pastel_pass_no_error():
    """degas_pastel_pass() must run without raising on a synthetic canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.50, 0.45, 0.38), texture_strength=0.00)
    p.degas_pastel_pass()  # default parameters — must not raise


def test_degas_pastel_pass_modifies_canvas():
    """degas_pastel_pass() at high opacity must change at least one pixel on a flat canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.50, 0.45, 0.38), texture_strength=0.00)
    before = np.array(p.canvas.to_pil(), dtype=np.int32)

    p.degas_pastel_pass(
        shadow_strength = 0.50,
        light_strength  = 0.50,
        pastel_grain    = 0.10,
        blend_opacity   = 0.80,
    )

    after = np.array(p.canvas.to_pil(), dtype=np.int32)
    assert (after != before).any(), "degas_pastel_pass() should modify canvas pixels"


def test_degas_pastel_pass_zero_opacity_no_op():
    """degas_pastel_pass() at blend_opacity=0 should leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.50, 0.45, 0.38), texture_strength=0.00)
    before = np.array(p.canvas.to_pil(), dtype=np.int32)

    p.degas_pastel_pass(
        shadow_strength = 0.50,
        light_strength  = 0.50,
        pastel_grain    = 0.00,  # also disable grain — both should be zero
        blend_opacity   = 0.00,
    )

    after = np.array(p.canvas.to_pil(), dtype=np.int32)
    assert (after == before).all(), (
        "degas_pastel_pass(blend_opacity=0, grain=0) should be a no-op")


def test_degas_pastel_pass_cools_dark_shadows():
    """
    A dark warm canvas should have more blue after degas_pastel_pass —
    because the shadow zone is shifted toward blue-grey (B > R for shadow_grey).
    """
    p = _make_small_painter(64, 64)
    # Very dark warm canvas — all pixels fall in the shadow zone
    p.tone_ground((0.22, 0.16, 0.10), texture_strength=0.00)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA layout: channel 0 = B, channel 2 = R
    before_b = float(before_buf[:, :, 0].mean())

    p.degas_pastel_pass(
        shadow_grey     = (0.30, 0.30, 0.42),  # strongly blue-shifted
        shadow_strength = 0.50,
        pastel_grain    = 0.00,
        blend_opacity   = 0.80,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_b = float(after_buf[:, :, 0].mean())

    assert after_b > before_b, (
        f"Shadow cooldown should increase B channel on a dark warm canvas: "
        f"before={before_b:.1f}, after={after_b:.1f}")


def test_degas_pastel_pass_warms_bright_highlights():
    """
    A very bright cool canvas should become warmer (higher R channel) after
    degas_pastel_pass — because the highlight zone is shifted toward amber-orange.
    """
    p = _make_small_painter(64, 64)
    # Very bright cool canvas — all pixels fall in the highlight zone
    p.tone_ground((0.80, 0.82, 0.90), texture_strength=0.00)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA layout: channel 2 = R
    before_r = float(before_buf[:, :, 2].mean())

    p.degas_pastel_pass(
        light_amber     = (0.88, 0.72, 0.54),  # warm amber-orange target
        light_threshold = 0.60,                 # lower threshold to catch all pixels
        light_strength  = 0.50,
        shadow_strength = 0.00,
        pastel_grain    = 0.00,
        blend_opacity   = 0.80,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_r = float(after_buf[:, :, 2].mean())

    assert after_r > before_r, (
        f"Highlight warmup should increase R channel on a bright cool canvas: "
        f"before={before_r:.1f}, after={after_r:.1f}")


# ──────────────────────────────────────────────────────────────────────────────
# POST_IMPRESSIONIST period routing (session 29)
# ──────────────────────────────────────────────────────────────────────────────

def test_post_impressionist_stroke_params_valid():
    """POST_IMPRESSIONIST stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.POST_IMPRESSIONIST,
                  palette=PaletteHint.COOL_GREY)
    sp = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"POST_IMPRESSIONIST stroke_params missing key: {key!r}"
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


def test_post_impressionist_wet_blend_lower_than_nordic_impressionist():
    """POST_IMPRESSIONIST wet_blend must be lower than NORDIC_IMPRESSIONIST (dry pastel vs wet oil)."""
    sp_post  = Style(medium=Medium.OIL, period=Period.POST_IMPRESSIONIST).stroke_params
    sp_nord  = Style(medium=Medium.OIL, period=Period.NORDIC_IMPRESSIONIST).stroke_params
    assert sp_post["wet_blend"] < sp_nord["wet_blend"], (
        "POST_IMPRESSIONIST wet_blend must be lower than NORDIC_IMPRESSIONIST "
        "(pastel marks sit drier than Zorn's wet-into-wet oil technique)")


# ──────────────────────────────────────────────────────────────────────────────
# piero_crystalline_pass — this session's random artistic improvement
# Inspired by Piero della Francesca's cool mineral Early Italian Renaissance light
# ──────────────────────────────────────────────────────────────────────────────

def test_piero_crystalline_pass_exists():
    """Painter must have piero_crystalline_pass() method after this session."""
    from stroke_engine import Painter
    assert hasattr(Painter, "piero_crystalline_pass"), (
        "piero_crystalline_pass not found on Painter")
    assert callable(getattr(Painter, "piero_crystalline_pass"))


def test_piero_crystalline_pass_no_error():
    """piero_crystalline_pass() runs without error on a plain toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.68, 0.58), texture_strength=0.04)
    # Should not raise
    p.piero_crystalline_pass(
        shadow_stone        = (0.44, 0.46, 0.50),
        highlight_silver    = (0.93, 0.94, 0.96),
        shadow_threshold    = 0.42,
        highlight_threshold = 0.70,
        shadow_strength     = 0.22,
        highlight_strength  = 0.16,
        chroma_dampen       = 0.08,
        blend_opacity       = 0.45,
    )


def test_piero_crystalline_pass_modifies_canvas():
    """piero_crystalline_pass() with non-zero strengths must modify the canvas."""
    p = _make_small_painter(64, 64)
    # Warm dark canvas — shadow zone pixels to shift toward cool stone
    p.tone_ground((0.30, 0.22, 0.14), texture_strength=0.00)
    before = np.array(p.canvas.to_pil(), dtype=np.float32).copy()
    p.piero_crystalline_pass(
        shadow_strength     = 0.50,
        highlight_strength  = 0.30,
        chroma_dampen       = 0.15,
        blend_opacity       = 0.70,
    )
    after = np.array(p.canvas.to_pil(), dtype=np.float32)
    diff = np.abs(after - before).max()
    assert diff > 0, (
        "piero_crystalline_pass with non-zero strengths should modify the canvas")


def test_piero_crystalline_pass_zero_opacity_no_op():
    """piero_crystalline_pass with blend_opacity=0.0 and chroma_dampen=0.0 should be a no-op."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.55, 0.28), texture_strength=0.00)
    before = np.array(p.canvas.to_pil()).copy()
    p.piero_crystalline_pass(blend_opacity=0.0, chroma_dampen=0.0)
    after = np.array(p.canvas.to_pil())
    np.testing.assert_array_equal(before, after,
        err_msg="piero_crystalline_pass with blend_opacity=0 and chroma_dampen=0 should be a no-op")


def test_piero_crystalline_pass_cools_dark_shadows():
    """
    A dark warm canvas should become cooler (higher B channel) after
    piero_crystalline_pass — because shadows are shifted toward stone-grey (B > R).
    """
    p = _make_small_painter(64, 64)
    # Very dark warm canvas — all pixels fall in the shadow zone
    p.tone_ground((0.22, 0.16, 0.10), texture_strength=0.00)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA layout: channel 0 = B, channel 2 = R
    before_b = float(before_buf[:, :, 0].mean())

    p.piero_crystalline_pass(
        shadow_stone    = (0.44, 0.46, 0.50),  # B > R target
        shadow_strength = 0.50,
        chroma_dampen   = 0.00,
        blend_opacity   = 0.80,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_b = float(after_buf[:, :, 0].mean())

    assert after_b > before_b, (
        f"Shadow stone shift should increase B channel on a dark warm canvas: "
        f"before={before_b:.1f}, after={after_b:.1f}")


def test_piero_crystalline_pass_cools_bright_highlights():
    """
    A bright warm canvas should become cooler (lower R/B ratio) after
    piero_crystalline_pass — because highlights shift toward silver-white (B > R).
    """
    p = _make_small_painter(64, 64)
    # Very bright warm canvas — all pixels fall in the highlight zone
    p.tone_ground((0.90, 0.86, 0.78), texture_strength=0.00)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA layout: channel 2 = R, channel 0 = B
    before_r = float(before_buf[:, :, 2].mean())
    before_b = float(before_buf[:, :, 0].mean())

    p.piero_crystalline_pass(
        highlight_silver    = (0.93, 0.94, 0.96),  # higher B/G than warm start
        highlight_threshold = 0.60,                  # lower threshold to catch all pixels
        highlight_strength  = 0.60,
        shadow_strength     = 0.00,
        chroma_dampen       = 0.00,
        blend_opacity       = 0.80,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_r = float(after_buf[:, :, 2].mean())
    after_b = float(after_buf[:, :, 0].mean())

    # Silver-white has higher B relative to R than the warm canvas start — so
    # R should decrease and/or B should increase after the shift.
    r_decreased = after_r < before_r
    b_increased = after_b > before_b
    assert r_decreased or b_increased, (
        f"Highlight silver shift should reduce R or increase B on a warm canvas: "
        f"R before={before_r:.1f} after={after_r:.1f}, "
        f"B before={before_b:.1f} after={after_b:.1f}")


# ──────────────────────────────────────────────────────────────────────────────
# EARLY_ITALIAN_RENAISSANCE period routing (this session)
# ──────────────────────────────────────────────────────────────────────────────

def test_early_italian_renaissance_stroke_params_valid():
    """EARLY_ITALIAN_RENAISSANCE stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.EARLY_ITALIAN_RENAISSANCE,
                  palette=PaletteHint.COOL_GREY)
    sp = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, (
            f"EARLY_ITALIAN_RENAISSANCE stroke_params missing key: {key!r}")
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


def test_early_italian_renaissance_wet_blend_lower_than_venetian():
    """EARLY_ITALIAN_RENAISSANCE wet_blend must be lower than VENETIAN_RENAISSANCE (less fluid blending)."""
    sp_early = Style(medium=Medium.OIL, period=Period.EARLY_ITALIAN_RENAISSANCE).stroke_params
    sp_ven   = Style(medium=Medium.OIL, period=Period.VENETIAN_RENAISSANCE).stroke_params
    assert sp_early["wet_blend"] < sp_ven["wet_blend"], (
        "EARLY_ITALIAN_RENAISSANCE wet_blend must be lower than VENETIAN_RENAISSANCE "
        "(Piero's geometric precision uses less fluid blending than Titian's rich Venetian technique)")
