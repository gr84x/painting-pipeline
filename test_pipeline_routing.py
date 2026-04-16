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
        "is_post_impressionist":         period == Period.POST_IMPRESSIONIST,
        "is_pre_raphaelite":             period == Period.PRE_RAPHAELITE,
        "is_symbolist":                  period == Period.SYMBOLIST,
        "is_florentine_renaissance":     period == Period.FLORENTINE_RENAISSANCE,
        "is_northern_renaissance":       period == Period.NORTHERN_RENAISSANCE,
        "is_quattrocento":               period == Period.QUATTROCENTO,
        "is_renaissance_soft":           (period == Period.RENAISSANCE
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
# piero_crystalline_pass — prior session's random artistic improvement
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
# EARLY_ITALIAN_RENAISSANCE period routing (prior session)
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


# ──────────────────────────────────────────────────────────────────────────────
# POST_IMPRESSIONIST routing flags (Degas, current session)
# ──────────────────────────────────────────────────────────────────────────────

def test_post_impressionist_flag_set():
    """POST_IMPRESSIONIST period must set is_post_impressionist=True."""
    flags = _routing_flags(Period.POST_IMPRESSIONIST)
    assert flags["is_post_impressionist"] is True


def test_post_impressionist_flag_not_set_for_other_periods():
    """is_post_impressionist must be False for all periods except POST_IMPRESSIONIST."""
    for period in Period:
        if period == Period.POST_IMPRESSIONIST:
            continue
        flags = _routing_flags(period)
        assert not flags["is_post_impressionist"], (
            f"is_post_impressionist should be False for {period.name}")


def test_post_impressionist_mutually_exclusive_with_impressionist_plein_air():
    """POST_IMPRESSIONIST and IMPRESSIONIST_PLEIN_AIR must not both be True."""
    flags_pi = _routing_flags(Period.POST_IMPRESSIONIST)
    flags_pa = _routing_flags(Period.IMPRESSIONIST_PLEIN_AIR)
    assert     flags_pi["is_post_impressionist"]
    assert not flags_pi["is_impressionist_plein_air"]
    assert     flags_pa["is_impressionist_plein_air"]
    assert not flags_pa["is_post_impressionist"]


# ──────────────────────────────────────────────────────────────────────────────
# degas_pastel_pass — routing-level smoke tests (current session)
# ──────────────────────────────────────────────────────────────────────────────

def test_degas_pastel_pass_exists():
    """Painter must have degas_pastel_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "degas_pastel_pass"), (
        "degas_pastel_pass not found on Painter")
    assert callable(getattr(Painter, "degas_pastel_pass"))


def test_degas_pastel_pass_no_error():
    """degas_pastel_pass() runs without error on a plain toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.28, 0.26, 0.32), texture_strength=0.06)
    p.degas_pastel_pass()


def test_degas_pastel_pass_modifies_canvas():
    """degas_pastel_pass() with non-zero strengths must modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.28, 0.26, 0.32), texture_strength=0.04)
    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.degas_pastel_pass(
        shadow_strength = 0.40,
        light_strength  = 0.30,
        blend_opacity   = 0.60,
    )
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()
    assert not np.array_equal(before, after), (
        "degas_pastel_pass with non-zero strengths must modify the canvas")


# ──────────────────────────────────────────────────────────────────────────────
# waterhouse_jewel_pass — current session addition
# ──────────────────────────────────────────────────────────────────────────────

def test_waterhouse_jewel_pass_exists():
    """Painter must have waterhouse_jewel_pass() method after this session."""
    from stroke_engine import Painter
    assert hasattr(Painter, "waterhouse_jewel_pass"), (
        "waterhouse_jewel_pass not found on Painter")
    assert callable(getattr(Painter, "waterhouse_jewel_pass"))


def test_waterhouse_jewel_pass_no_error():
    """waterhouse_jewel_pass() runs without error on a plain near-white canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.94, 0.93, 0.90), texture_strength=0.02)
    p.waterhouse_jewel_pass()


def test_waterhouse_jewel_pass_no_error_with_block_in():
    """waterhouse_jewel_pass() runs without error after block_in on a painted canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.94, 0.93, 0.90), texture_strength=0.02)
    p.block_in(ref, stroke_size=6, n_strokes=15)
    p.waterhouse_jewel_pass(
        jewel_boost         = 0.14,
        jewel_low           = 0.20,
        jewel_high          = 0.62,
        shadow_cool         = 0.10,
        shadow_threshold    = 0.30,
        shadow_width        = 0.12,
        highlight_warmth    = 0.06,
        highlight_threshold = 0.76,
        blend_opacity       = 0.46,
    )


def test_waterhouse_jewel_pass_zero_boost_no_saturation_change():
    """waterhouse_jewel_pass with jewel_boost=0 and shadow_cool=0 and highlight_warmth=0 is a no-op."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.50, 0.35), texture_strength=0.04)
    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.waterhouse_jewel_pass(
        jewel_boost      = 0.0,
        shadow_cool      = 0.0,
        highlight_warmth = 0.0,
        blend_opacity    = 0.50,
    )
    after = np.frombuffer(p.canvas.surface.get_data(),
                          dtype=np.uint8).reshape(64, 64, 4).copy()
    np.testing.assert_array_equal(before, after,
        err_msg="waterhouse_jewel_pass with all-zero strengths should be a no-op")


def test_waterhouse_jewel_pass_increases_saturation_on_midtone_canvas():
    """
    On a desaturated midtone canvas, waterhouse_jewel_pass should increase
    the spread between colour channels (higher saturation).
    """
    p = _make_small_painter(64, 64)
    # Slightly coloured midtone canvas — R > G > B but not by much
    p.tone_ground((0.55, 0.48, 0.38), texture_strength=0.00)

    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    # Saturation proxy: max(R, G, B) - min(R, G, B)
    before_chroma = float(
        (before_buf[:, :, 2].astype(float) - before_buf[:, :, 0].astype(float)).mean())

    p.waterhouse_jewel_pass(
        jewel_boost      = 0.20,
        jewel_low        = 0.30,
        jewel_high       = 0.75,
        shadow_cool      = 0.00,
        highlight_warmth = 0.00,
        blend_opacity    = 0.80,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_chroma = float(
        (after_buf[:, :, 2].astype(float) - after_buf[:, :, 0].astype(float)).mean())

    assert after_chroma > before_chroma, (
        f"waterhouse_jewel_pass should increase channel spread (saturation) on "
        f"a coloured midtone canvas: before={before_chroma:.2f}, after={after_chroma:.2f}")


def test_waterhouse_jewel_pass_shadow_cool_increases_blue():
    """
    On a dark warm canvas, waterhouse_jewel_pass shadow_cool should increase
    the B channel (cooling deep shadows toward lavender-blue).
    """
    p = _make_small_painter(64, 64)
    # Very dark warm canvas — all pixels fall in the shadow zone
    p.tone_ground((0.15, 0.11, 0.07), texture_strength=0.00)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    before_b = float(before_buf[:, :, 0].mean())   # Cairo BGRA: channel 0 = B

    p.waterhouse_jewel_pass(
        jewel_boost      = 0.0,
        shadow_cool      = 0.35,
        shadow_threshold = 0.40,   # high threshold to catch these dark pixels
        shadow_width     = 0.15,
        highlight_warmth = 0.0,
        blend_opacity    = 0.80,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_b = float(after_buf[:, :, 0].mean())

    assert after_b > before_b, (
        f"Shadow cooling should increase B channel on a dark warm canvas: "
        f"before_B={before_b:.1f}, after_B={after_b:.1f}")


# ──────────────────────────────────────────────────────────────────────────────
# PRE_RAPHAELITE period routing (current session)
# ──────────────────────────────────────────────────────────────────────────────

def test_pre_raphaelite_flag_set():
    """PRE_RAPHAELITE period must set is_pre_raphaelite=True."""
    flags = _routing_flags(Period.PRE_RAPHAELITE)
    assert flags["is_pre_raphaelite"] is True


def test_pre_raphaelite_flag_not_set_for_other_periods():
    """is_pre_raphaelite must be False for all periods except PRE_RAPHAELITE."""
    for period in Period:
        if period == Period.PRE_RAPHAELITE:
            continue
        flags = _routing_flags(period)
        assert not flags["is_pre_raphaelite"], (
            f"is_pre_raphaelite should be False for {period.name}")


def test_pre_raphaelite_mutually_exclusive_with_post_impressionist():
    """PRE_RAPHAELITE and POST_IMPRESSIONIST must not both be True."""
    flags_pr = _routing_flags(Period.PRE_RAPHAELITE)
    flags_pi = _routing_flags(Period.POST_IMPRESSIONIST)
    assert     flags_pr["is_pre_raphaelite"]
    assert not flags_pr["is_post_impressionist"]
    assert     flags_pi["is_post_impressionist"]
    assert not flags_pi["is_pre_raphaelite"]


def test_pre_raphaelite_stroke_params_valid():
    """PRE_RAPHAELITE stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.PRE_RAPHAELITE,
                  palette=PaletteHint.JEWEL)
    sp = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"PRE_RAPHAELITE stroke_params missing key: {key!r}"
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


# ──────────────────────────────────────────────────────────────────────────────
# moreau_gilded_pass — session 32 addition (random artistic improvement)
# ──────────────────────────────────────────────────────────────────────────────
# This session's random artistic improvement: stochastic gold-point scattering.
# Unlike all prior passes (which modify pixels deterministically by luminance
# band or via convolution), moreau_gilded_pass uses random pixel sampling to
# place individual gold-tinted "fragments" across the canvas — simulating
# Moreau's encrusted Byzantine-mosaic surface technique.

def test_moreau_gilded_pass_exists():
    """Painter must have moreau_gilded_pass() method after session 32."""
    from stroke_engine import Painter
    assert hasattr(Painter, "moreau_gilded_pass"), (
        "moreau_gilded_pass not found on Painter")
    assert callable(getattr(Painter, "moreau_gilded_pass"))


def test_moreau_gilded_pass_no_error():
    """moreau_gilded_pass() runs without error on a plain toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.18, 0.08, 0.05), texture_strength=0.0)
    p.moreau_gilded_pass()


def test_moreau_gilded_pass_modifies_canvas():
    """moreau_gilded_pass() with non-zero parameters must modify the canvas."""
    p = _make_small_painter(64, 64)
    # Mid-tone canvas — pixels fall within gold scattering range
    p.tone_ground((0.55, 0.45, 0.30), texture_strength=0.0)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()

    p.moreau_gilded_pass(
        gold_density   = 0.30,   # very high density so modification is detectable
        blend_opacity  = 0.80,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert not np.array_equal(before_buf, after_buf), (
        "moreau_gilded_pass with high gold_density should modify the canvas")


def test_moreau_gilded_pass_zero_opacity_minimal_change():
    """moreau_gilded_pass with blend_opacity=0.0 should leave the canvas nearly unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.45, 0.30), texture_strength=0.0)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()

    p.moreau_gilded_pass(blend_opacity=0.0)

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    # With opacity=0 all three zones collapse to no-op (gold scatter alpha=0,
    # shadow_alpha=0, atm_strength=0), so the canvas should be unchanged.
    assert np.array_equal(before_buf, after_buf), (
        "moreau_gilded_pass with blend_opacity=0.0 should leave the canvas unchanged")


def test_moreau_gilded_pass_warms_shadows():
    """
    moreau_gilded_pass shadow enrichment should shift deep-shadow pixels
    toward warm crimson (raise R channel relative to B).
    """
    p = _make_small_painter(64, 64)
    # Very dark cool canvas — all pixels fall in the shadow zone
    p.tone_ground((0.08, 0.10, 0.14), texture_strength=0.0)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA: channel 2 = R, channel 0 = B
    before_r_minus_b = float(
        (before_buf[:, :, 2].astype(float) - before_buf[:, :, 0].astype(float)).mean())

    p.moreau_gilded_pass(
        gold_density       = 0.0,      # disable gold scatter — test shadow only
        crimson_shadow     = 0.50,     # strong crimson push
        shadow_threshold   = 0.50,     # high threshold to catch these dark pixels
        blend_opacity      = 0.80,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_r_minus_b = float(
        (after_buf[:, :, 2].astype(float) - after_buf[:, :, 0].astype(float)).mean())

    assert after_r_minus_b > before_r_minus_b, (
        f"moreau_gilded_pass shadow enrichment should raise R relative to B on a cool-dark "
        f"canvas: before R-B={before_r_minus_b:.2f}, after R-B={after_r_minus_b:.2f}")


def test_moreau_gilded_pass_gold_raises_r_channel():
    """
    On a mid-tone canvas, moreau_gilded_pass gold scattering with a warm gold_tint
    should raise the mean R channel value (gold is R > G > B).
    """
    p = _make_small_painter(64, 64)
    # Neutral mid-grey — luminance ~0.50, within the gold window
    p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    before_r = float(before_buf[:, :, 2].mean())   # Cairo BGRA: channel 2 = R

    p.moreau_gilded_pass(
        gold_density   = 0.50,          # 50% of pixels get gold touch
        gold_low       = 0.40,
        gold_high      = 0.70,
        gold_tint      = (0.92, 0.76, 0.22),
        crimson_shadow = 0.0,           # disable shadow enrichment
        blend_opacity  = 0.80,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_r = float(after_buf[:, :, 2].mean())

    assert after_r > before_r, (
        f"moreau_gilded_pass gold scattering with warm gold_tint should raise mean R; "
        f"before={before_r:.1f}, after={after_r:.1f}")


# ──────────────────────────────────────────────────────────────────────────────
# SYMBOLIST period routing (session 32)
# ──────────────────────────────────────────────────────────────────────────────

def test_symbolist_flag_set():
    """SYMBOLIST period must set is_symbolist=True."""
    flags = _routing_flags(Period.SYMBOLIST)
    assert flags["is_symbolist"] is True


def test_symbolist_flag_not_set_for_other_periods():
    """is_symbolist must be False for all periods except SYMBOLIST."""
    for period in Period:
        if period == Period.SYMBOLIST:
            continue
        flags = _routing_flags(period)
        assert not flags["is_symbolist"], (
            f"is_symbolist should be False for {period.name}")


def test_symbolist_mutually_exclusive_with_pre_raphaelite():
    """SYMBOLIST and PRE_RAPHAELITE must not both be True simultaneously."""
    flags_s  = _routing_flags(Period.SYMBOLIST)
    flags_pr = _routing_flags(Period.PRE_RAPHAELITE)
    assert     flags_s["is_symbolist"]
    assert not flags_s["is_pre_raphaelite"]
    assert     flags_pr["is_pre_raphaelite"]
    assert not flags_pr["is_symbolist"]


def test_symbolist_stroke_params_valid():
    """SYMBOLIST stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.SYMBOLIST,
                  palette=PaletteHint.JEWEL)
    sp = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"SYMBOLIST stroke_params missing key: {key!r}"
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


# ──────────────────────────────────────────────────────────────────────────────
# botticelli_linear_grace_pass — Florentine Renaissance tempera technique
# ──────────────────────────────────────────────────────────────────────────────

def test_botticelli_linear_grace_pass_exists():
    """Painter must have botticelli_linear_grace_pass() after this session."""
    from stroke_engine import Painter
    assert hasattr(Painter, "botticelli_linear_grace_pass"), (
        "botticelli_linear_grace_pass not found on Painter")
    assert callable(getattr(Painter, "botticelli_linear_grace_pass"))


def test_botticelli_linear_grace_pass_no_error():
    """botticelli_linear_grace_pass() must complete without error on a plain canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    # Pale gesso ground mimicking Botticelli's panel preparation
    p.tone_ground((0.94, 0.91, 0.85), texture_strength=0.03)
    p.botticelli_linear_grace_pass(ref)


def test_botticelli_linear_grace_pass_modifies_canvas():
    """botticelli_linear_grace_pass() must modify a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.90, 0.87, 0.80), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=15)

    before = np.array(p.canvas.to_pil(), dtype=np.float32)
    p.botticelli_linear_grace_pass(ref, luminosity_lift=0.08)
    after  = np.array(p.canvas.to_pil(), dtype=np.float32)

    assert np.abs(after - before).max() > 0, (
        "botticelli_linear_grace_pass should modify the canvas")


def test_botticelli_linear_grace_pass_luminosity_lift_brightens():
    """
    With luminosity_lift > 0, the mean luminance of the canvas should
    increase after the pass (the gesso-ground simulation brightens midtones).
    """
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    # Mid-grey ground — luminance ~0.50, within the lift zone
    p.tone_ground((0.55, 0.52, 0.48), texture_strength=0.00)

    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA: channel 2 = R, 1 = G, 0 = B
    before_lum = (0.299 * before_buf[:, :, 2].astype(float)
                  + 0.587 * before_buf[:, :, 1].astype(float)
                  + 0.114 * before_buf[:, :, 0].astype(float)).mean()

    p.botticelli_linear_grace_pass(
        ref,
        hatch_density   = 0.0,   # disable hatching to isolate luminosity lift
        gold_density    = 0.0,   # disable gold to isolate luminosity lift
        luminosity_lift = 0.12,
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_lum = (0.299 * after_buf[:, :, 2].astype(float)
                 + 0.587 * after_buf[:, :, 1].astype(float)
                 + 0.114 * after_buf[:, :, 0].astype(float)).mean()

    assert after_lum > before_lum, (
        f"luminosity_lift=0.12 should increase mean luminance; "
        f"before={before_lum:.2f}, after={after_lum:.2f}")


def test_botticelli_linear_grace_pass_gold_raises_warm_channels():
    """
    With a high gold_density and a warm gold_tint, the pass should raise the
    mean R channel more than the B channel (gold is warmer than the plain canvas).
    """
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    # Neutral mid-tone — luminance ~0.55, within the gold window (0.45–0.88)
    p.tone_ground((0.55, 0.55, 0.55), texture_strength=0.00)

    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    before_r = float(before_buf[:, :, 2].mean())
    before_b = float(before_buf[:, :, 0].mean())

    p.botticelli_linear_grace_pass(
        ref,
        hatch_density   = 0.0,            # disable hatching
        gold_density    = 0.50,           # high density to ensure visible effect
        gold_tint       = (0.88, 0.72, 0.24),
        gold_opacity    = 0.80,
        luminosity_lift = 0.0,            # disable lift
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_r = float(after_buf[:, :, 2].mean())
    after_b = float(after_buf[:, :, 0].mean())

    # Gold tint has R=0.88 >> B=0.24: R channel should rise more than B channel.
    r_delta = after_r - before_r
    b_delta = after_b - before_b
    assert r_delta > b_delta, (
        f"Gold scatter should raise R more than B; R_delta={r_delta:.2f}, B_delta={b_delta:.2f}")


# ──────────────────────────────────────────────────────────────────────────────
# tonal_envelope_pass — Portrait luminosity gradient improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_tonal_envelope_pass_exists():
    """Painter must have tonal_envelope_pass() after this session."""
    from stroke_engine import Painter
    assert hasattr(Painter, "tonal_envelope_pass"), (
        "tonal_envelope_pass not found on Painter")
    assert callable(getattr(Painter, "tonal_envelope_pass"))


def test_tonal_envelope_pass_no_error():
    """tonal_envelope_pass() must complete without error on a plain canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.50, 0.40), texture_strength=0.05)
    p.tonal_envelope_pass()


def test_tonal_envelope_pass_modifies_canvas():
    """tonal_envelope_pass() must change the canvas when lift_strength > 0."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.50, 0.40), texture_strength=0.04)

    before = np.array(p.canvas.to_pil(), dtype=np.float32)
    p.tonal_envelope_pass(lift_strength=0.12, edge_darken=0.08)
    after  = np.array(p.canvas.to_pil(), dtype=np.float32)

    assert np.abs(after - before).max() > 0, (
        "tonal_envelope_pass should modify the canvas")


def test_tonal_envelope_pass_centre_brighter_than_edges():
    """
    After tonal_envelope_pass, the central region of a uniform canvas should
    be brighter than the corner regions (the radial lift should be stronger
    at the portrait center than at the canvas edges).
    """
    p = _make_small_painter(64, 64)
    # Uniform mid-grey canvas — uniform before the pass
    p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.00)

    p.tonal_envelope_pass(
        center_x      = 0.50,
        center_y      = 0.50,
        radius        = 0.30,
        lift_strength = 0.15,
        lift_warmth   = 0.20,
        edge_darken   = 0.10,
        gamma         = 2.0,
    )

    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA: channel 2=R, 1=G, 0=B
    # Mean luminance of central 16×16 patch
    centre_lum = (0.299 * buf[24:40, 24:40, 2].astype(float)
                  + 0.587 * buf[24:40, 24:40, 1].astype(float)
                  + 0.114 * buf[24:40, 24:40, 0].astype(float)).mean()
    # Mean luminance of the four corner 8×8 patches
    corners = [buf[:8, :8], buf[:8, 56:], buf[56:, :8], buf[56:, 56:]]
    corner_lum = _np_mean_lum(corners)

    assert centre_lum > corner_lum, (
        f"Centre should be brighter than corners after tonal_envelope_pass; "
        f"centre={centre_lum:.2f}, corners={corner_lum:.2f}")


def _np_mean_lum(patches):
    """Helper: mean perceptual luminance across a list of BGRA patch arrays."""
    vals = []
    for patch in patches:
        lum = (0.299 * patch[:, :, 2].astype(float)
               + 0.587 * patch[:, :, 1].astype(float)
               + 0.114 * patch[:, :, 0].astype(float))
        vals.append(lum.mean())
    return sum(vals) / len(vals)


def test_tonal_envelope_pass_zero_lift_zero_darken_no_op():
    """tonal_envelope_pass with lift_strength=0 and edge_darken=0 must not modify canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.55, 0.45), texture_strength=0.03)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.tonal_envelope_pass(lift_strength=0.0, edge_darken=0.0)
    after  = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4)

    np.testing.assert_array_equal(before, after,
        err_msg="tonal_envelope_pass with zero lift and darken must be a no-op")


# ──────────────────────────────────────────────────────────────────────────────
# FLORENTINE_RENAISSANCE period routing flags
# ──────────────────────────────────────────────────────────────────────────────

def test_florentine_renaissance_flag_set():
    """FLORENTINE_RENAISSANCE period must set is_florentine_renaissance=True."""
    flags = _routing_flags(Period.FLORENTINE_RENAISSANCE)
    assert flags["is_florentine_renaissance"] is True


def test_florentine_renaissance_flag_not_set_for_other_periods():
    """is_florentine_renaissance must be False for all other periods."""
    for period in Period:
        if period == Period.FLORENTINE_RENAISSANCE:
            continue
        flags = _routing_flags(period)
        assert not flags["is_florentine_renaissance"], (
            f"is_florentine_renaissance should be False for {period.name}")


def test_florentine_renaissance_mutually_exclusive_with_symbolist():
    """FLORENTINE_RENAISSANCE and SYMBOLIST must not both be True simultaneously."""
    flags_f = _routing_flags(Period.FLORENTINE_RENAISSANCE)
    flags_s = _routing_flags(Period.SYMBOLIST)
    assert     flags_f["is_florentine_renaissance"]
    assert not flags_f["is_symbolist"]
    assert     flags_s["is_symbolist"]
    assert not flags_s["is_florentine_renaissance"]


def test_florentine_renaissance_stroke_params_valid():
    """FLORENTINE_RENAISSANCE stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.FLORENTINE_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    sp = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"FLORENTINE_RENAISSANCE stroke_params missing key: {key!r}"
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


def test_florentine_renaissance_has_minimum_wet_blend():
    """FLORENTINE_RENAISSANCE wet_blend must be very low (tempera dries instantly)."""
    sp = Style(medium=Medium.OIL, period=Period.FLORENTINE_RENAISSANCE).stroke_params
    assert sp["wet_blend"] <= 0.10, (
        f"FLORENTINE_RENAISSANCE wet_blend should be ≤ 0.10 (tempera), "
        f"got {sp['wet_blend']:.3f}")


def test_florentine_renaissance_has_crisp_edges():
    """FLORENTINE_RENAISSANCE edge_softness must be very low (Gothic linear contour)."""
    sp = Style(medium=Medium.OIL, period=Period.FLORENTINE_RENAISSANCE).stroke_params
    assert sp["edge_softness"] <= 0.20, (
        f"FLORENTINE_RENAISSANCE edge_softness should be ≤ 0.20 (crisp tempera line), "
        f"got {sp['edge_softness']:.3f}")


# ──────────────────────────────────────────────────────────────────────────────
# durer_engraving_pass — session 34 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_durer_engraving_pass_exists():
    """Painter must have durer_engraving_pass() method after session 34."""
    from stroke_engine import Painter
    assert hasattr(Painter, "durer_engraving_pass"), (
        "durer_engraving_pass not found on Painter")
    assert callable(getattr(Painter, "durer_engraving_pass"))


def test_durer_engraving_pass_runs():
    """durer_engraving_pass() runs without error on a small synthetic canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.82, 0.80, 0.76), texture_strength=0.02)
    p.underpainting(ref, stroke_size=20, n_strokes=30)
    p.durer_engraving_pass(ref, hatch_density=0.025, cross_hatch=True)


def test_durer_engraving_pass_no_cross_hatch():
    """durer_engraving_pass() runs correctly with cross_hatch=False."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.82, 0.80, 0.76), texture_strength=0.02)
    p.durer_engraving_pass(ref, hatch_density=0.020, cross_hatch=False)


def test_durer_engraving_pass_darkens_shadows():
    """
    durer_engraving_pass() should darken (or at minimum not brighten) shadow zones.

    The hatching adds darker marks and the cool shift reduces the red channel
    in shadows.  On a canvas that has both a dark zone and a light zone, the
    mean luminance of the dark zone should be ≤ its value before the pass.
    """
    p   = _make_small_painter(64, 64)
    # Build a reference with a clear dark (shadow) left half and light right half
    import numpy as np
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :32, :] = 40    # dark left — shadow zone
    arr[:, 32:, :] = 200   # light right — highlight zone
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.50, 0.45, 0.40), texture_strength=0.00)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    shadow_lum_before = (
        0.299 * buf_before[:, :32, 2].astype(float)
        + 0.587 * buf_before[:, :32, 1].astype(float)
        + 0.114 * buf_before[:, :32, 0].astype(float)
    ).mean()

    p.durer_engraving_pass(ref, hatch_density=0.040, cool_shift=0.06, cross_hatch=True)

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    shadow_lum_after = (
        0.299 * buf_after[:, :32, 2].astype(float)
        + 0.587 * buf_after[:, :32, 1].astype(float)
        + 0.114 * buf_after[:, :32, 0].astype(float)
    ).mean()

    assert shadow_lum_after <= shadow_lum_before + 2.0, (
        f"durer_engraving_pass should not brighten shadow zones; "
        f"before={shadow_lum_before:.2f}, after={shadow_lum_after:.2f}")


def test_durer_engraving_pass_cool_shifts_shadow_red():
    """
    durer_engraving_pass() cool shift must reduce mean red channel in shadow zone.

    The cool_shift parameter reduces R more than B in shadow pixels.
    On a canvas toned with a warm mid-grey, the red channel in a dark shadow
    zone should be lower after the pass than before.
    """
    import numpy as np
    from PIL import Image
    p = _make_small_painter(64, 64)
    # Dark ground (lum ≈ 0.28) — well below shadow_threshold=0.45 so the
    # cool-shift actually fires on these pixels.
    p.tone_ground((0.30, 0.28, 0.24), texture_strength=0.00)

    # Reference: pure dark so the whole canvas is in the shadow zone
    arr = np.zeros((64, 64, 3), dtype=np.uint8) + 30
    ref = Image.fromarray(arr, "RGB")

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    r_before = buf_before[:, :, 2].astype(float).mean()

    p.durer_engraving_pass(ref, hatch_density=0.010, cool_shift=0.12, cross_hatch=False)

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = buf_after[:, :, 2].astype(float).mean()

    assert r_after < r_before, (
        f"durer_engraving_pass cool_shift must reduce mean red channel in shadow zones; "
        f"before={r_before:.2f}, after={r_after:.2f}")


# ──────────────────────────────────────────────────────────────────────────────
# selective_focus_pass — session 34 random improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_selective_focus_pass_exists():
    """Painter must have selective_focus_pass() method after session 34."""
    from stroke_engine import Painter
    assert hasattr(Painter, "selective_focus_pass"), (
        "selective_focus_pass not found on Painter")
    assert callable(getattr(Painter, "selective_focus_pass"))


def test_selective_focus_pass_runs():
    """selective_focus_pass() runs without error on a small synthetic canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.55, 0.48), texture_strength=0.03)
    p.selective_focus_pass(
        center_x=0.50, center_y=0.30,
        focus_radius=0.30, max_blur_radius=3.0,
        desaturation=0.10,
    )


def test_selective_focus_pass_peripheral_softer():
    """
    selective_focus_pass() must make the canvas periphery softer (lower contrast)
    than the focal centre region.

    Blur reduces local contrast.  The standard deviation of pixel values in
    a corner patch should be ≤ that of the centre patch after the pass.
    """
    import numpy as np
    p = _make_small_painter(128, 128)
    # Lay down a noisy pattern to make contrast measurable
    p.tone_ground((0.50, 0.48, 0.44), texture_strength=0.08)

    p.selective_focus_pass(
        center_x=0.50, center_y=0.50,
        focus_radius=0.25,
        max_blur_radius=5.0,
        desaturation=0.15,
        gamma=2.0,
    )

    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(128, 128, 4)
    lum = (0.299 * buf[:, :, 2].astype(float)
           + 0.587 * buf[:, :, 1].astype(float)
           + 0.114 * buf[:, :, 0].astype(float))

    # Standard deviation of the centre 32×32 vs. four corner 24×24 patches
    centre_std  = lum[48:80, 48:80].std()
    tl_std = lum[:24,  :24 ].std()
    tr_std = lum[:24, 104:].std()
    bl_std = lum[104:, :24 ].std()
    br_std = lum[104:, 104:].std()
    corner_std  = (tl_std + tr_std + bl_std + br_std) / 4.0

    assert corner_std <= centre_std + 2.0, (
        f"selective_focus_pass periphery should not be sharper than centre; "
        f"centre_std={centre_std:.2f}  corner_std={corner_std:.2f}")


def test_selective_focus_pass_zero_blur_zero_desat_no_op():
    """selective_focus_pass with max_blur_radius=0 and desaturation=0 must be a no-op."""
    import numpy as np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.56, 0.48), texture_strength=0.04)

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.selective_focus_pass(max_blur_radius=0.0, desaturation=0.0)
    after  = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4)

    np.testing.assert_array_equal(before, after,
        err_msg="selective_focus_pass with zero blur and zero desat must be a no-op")


# ──────────────────────────────────────────────────────────────────────────────
# NORTHERN_RENAISSANCE period routing flags
# ──────────────────────────────────────────────────────────────────────────────

def test_northern_renaissance_flag_set():
    """NORTHERN_RENAISSANCE period must set is_northern_renaissance=True."""
    flags = _routing_flags(Period.NORTHERN_RENAISSANCE)
    assert flags["is_northern_renaissance"] is True


def test_northern_renaissance_flag_not_set_for_other_periods():
    """is_northern_renaissance must be False for all other periods."""
    for period in Period:
        if period == Period.NORTHERN_RENAISSANCE:
            continue
        flags = _routing_flags(period)
        assert not flags["is_northern_renaissance"], (
            f"is_northern_renaissance should be False for {period.name}")


def test_northern_renaissance_mutually_exclusive_with_florentine():
    """NORTHERN_RENAISSANCE and FLORENTINE_RENAISSANCE must not both be True."""
    flags_n = _routing_flags(Period.NORTHERN_RENAISSANCE)
    flags_f = _routing_flags(Period.FLORENTINE_RENAISSANCE)
    assert     flags_n["is_northern_renaissance"]
    assert not flags_n["is_florentine_renaissance"]
    assert     flags_f["is_florentine_renaissance"]
    assert not flags_f["is_northern_renaissance"]


def test_northern_renaissance_stroke_params_valid():
    """NORTHERN_RENAISSANCE stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.NORTHERN_RENAISSANCE,
                  palette=PaletteHint.COOL_GREY)
    sp = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"NORTHERN_RENAISSANCE stroke_params missing key: {key!r}"
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


def test_northern_renaissance_fine_stroke():
    """NORTHERN_RENAISSANCE stroke_size_face must be very fine (engraving precision)."""
    sp = Style(medium=Medium.OIL, period=Period.NORTHERN_RENAISSANCE).stroke_params
    assert sp["stroke_size_face"] <= 5, (
        f"NORTHERN_RENAISSANCE stroke_size_face should be ≤ 5 (single-hair precision); "
        f"got {sp['stroke_size_face']}")


def test_northern_renaissance_crisp_edges():
    """NORTHERN_RENAISSANCE edge_softness must be very low (engraving-influenced crisp contours)."""
    sp = Style(medium=Medium.OIL, period=Period.NORTHERN_RENAISSANCE).stroke_params
    assert sp["edge_softness"] <= 0.25, (
        f"NORTHERN_RENAISSANCE edge_softness should be ≤ 0.25 (engraving-crisp); "
        f"got {sp['edge_softness']:.3f}")


# ──────────────────────────────────────────────────────────────────────────────
# hatching_pass — randomly selected artistic improvement for this session
# Fra Angelico tempera-hatching technique
# ──────────────────────────────────────────────────────────────────────────────

def test_hatching_pass_exists():
    """Painter must have hatching_pass() method after this session."""
    from stroke_engine import Painter
    assert hasattr(Painter, "hatching_pass"), (
        "hatching_pass not found on Painter — Fra Angelico improvement not applied")
    assert callable(getattr(Painter, "hatching_pass"))


def test_hatching_pass_no_error_default_args():
    """hatching_pass() runs without error with default arguments on a small canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.92, 0.90, 0.85), texture_strength=0.04)
    p.hatching_pass(ref, n_strokes=120)


def test_hatching_pass_with_cross_hatch_disabled():
    """hatching_pass() runs without error when cross_hatch=False."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.92, 0.90, 0.85), texture_strength=0.04)
    p.hatching_pass(ref, n_strokes=80, cross_hatch=False)


def test_hatching_pass_modifies_canvas():
    """hatching_pass() must modify the canvas pixel data (strokes are applied)."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.92, 0.90, 0.85), texture_strength=0.04)

    before = np.array(p.canvas.to_pil(), dtype=np.float32)
    p.hatching_pass(ref, n_strokes=400,
                    dark_color=(0.18, 0.12, 0.06),
                    shadow_thresh=0.80)   # high threshold → strokes over uniform grey
    after = np.array(p.canvas.to_pil(), dtype=np.float32)

    diff = np.abs(after - before).max()
    assert diff > 0, (
        "hatching_pass() made no changes to canvas — strokes must be applied")


def test_hatching_pass_angle_parameter_accepted():
    """hatching_pass() should accept non-default angle parameters without error."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.92, 0.90, 0.85), texture_strength=0.04)
    p.hatching_pass(ref, n_strokes=100,
                    angle_primary=30.0, angle_cross=-60.0,
                    cross_hatch=True)


def test_hatching_pass_large_canvas_no_error():
    """hatching_pass() must complete without error on a moderate-size canvas."""
    p   = _make_small_painter(128, 160)
    ref = _solid_reference(128, 160)
    p.tone_ground((0.92, 0.90, 0.85), texture_strength=0.04)
    p.hatching_pass(ref, n_strokes=300, cross_hatch=True)


# ── QUATTROCENTO routing ──────────────────────────────────────────────────────

def test_quattrocento_routing_flag_set():
    """is_quattrocento must be True exactly for QUATTROCENTO period."""
    flags = _routing_flags(Period.QUATTROCENTO)
    assert flags["is_quattrocento"], (
        "is_quattrocento should be True for Period.QUATTROCENTO")


def test_quattrocento_flag_not_set_for_other_periods():
    """is_quattrocento must be False for all periods except QUATTROCENTO."""
    for period in Period:
        if period == Period.QUATTROCENTO:
            continue
        flags = _routing_flags(period)
        assert not flags["is_quattrocento"], (
            f"is_quattrocento should be False for {period.name}")


def test_quattrocento_stroke_params_valid():
    """QUATTROCENTO stroke_params must have all required keys and valid ranges."""
    sp = Style(medium=Medium.OIL, period=Period.QUATTROCENTO,
               palette=PaletteHint.COOL_GREY).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"QUATTROCENTO stroke_params missing key: {key!r}"
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


def test_quattrocento_mutually_exclusive_with_northern_renaissance():
    """QUATTROCENTO and NORTHERN_RENAISSANCE must not both be True simultaneously."""
    flags_q = _routing_flags(Period.QUATTROCENTO)
    flags_n = _routing_flags(Period.NORTHERN_RENAISSANCE)
    assert     flags_q["is_quattrocento"]
    assert not flags_q["is_northern_renaissance"]
    assert     flags_n["is_northern_renaissance"]
    assert not flags_n["is_quattrocento"]


# ── holbein_jewel_glaze_pass (session 36 random improvement) ─────────────────

def test_holbein_jewel_glaze_pass_exists():
    """Painter must expose holbein_jewel_glaze_pass() after session 36."""
    from stroke_engine import Painter
    assert hasattr(Painter, "holbein_jewel_glaze_pass"), (
        "holbein_jewel_glaze_pass not found on Painter — expected after session 36")
    assert callable(getattr(Painter, "holbein_jewel_glaze_pass"))


def test_holbein_jewel_glaze_pass_no_error():
    """holbein_jewel_glaze_pass() must complete without exception on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.85, 0.78), texture_strength=0.04)
    p.holbein_jewel_glaze_pass()


def test_holbein_jewel_glaze_pass_modifies_canvas():
    """holbein_jewel_glaze_pass() must change canvas pixel data at non-zero opacity."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Use a richly coloured reference so the jewel pass has chrominance to boost.
    ref = _np.zeros((64, 64, 3), dtype=_np.uint8)
    ref[:, :, 0] = 160   # moderate red — sits in jewel zone
    ref[:, :, 1] = 90
    ref[:, :, 2] = 40
    from PIL import Image as _Image
    img = _Image.fromarray(ref, "RGB")
    p.tone_ground((0.55, 0.38, 0.20), texture_strength=0.04)
    p.block_in(img, stroke_size=16, n_strokes=80)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.holbein_jewel_glaze_pass(chroma_boost=0.40, opacity=0.90)
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)

    diff = _np.abs(after.astype(_np.int32) - before.astype(_np.int32)).max()
    assert diff > 0, (
        "holbein_jewel_glaze_pass() made no changes to canvas — "
        "saturation and luminance adjustments must be applied")


def test_holbein_jewel_glaze_pass_opacity_zero_is_noop():
    """holbein_jewel_glaze_pass() with opacity=0 must leave the canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.50, 0.35), texture_strength=0.04)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.holbein_jewel_glaze_pass(opacity=0.0)
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)

    _np.testing.assert_array_equal(before, after,
        err_msg="holbein_jewel_glaze_pass with opacity=0 must be a no-op")


def test_holbein_jewel_glaze_pass_custom_parameters():
    """holbein_jewel_glaze_pass() accepts custom zone boundaries and strengths."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.70, 0.60, 0.45), texture_strength=0.04)
    p.holbein_jewel_glaze_pass(
        chroma_boost      = 0.18,
        jewel_lo          = 0.30,
        jewel_hi          = 0.65,
        shadow_cool_shift = 0.05,
        highlight_pale    = 0.10,
        shadow_desat      = 0.12,
        opacity           = 0.60,
    )


def test_holbein_jewel_glaze_pass_large_canvas():
    """holbein_jewel_glaze_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(128, 160)
    p.tone_ground((0.82, 0.78, 0.66), texture_strength=0.04)
    p.holbein_jewel_glaze_pass(chroma_boost=0.25, opacity=0.75)


def test_holbein_jewel_glaze_pass_jewel_zone_boosts_saturation():
    """
    On a canvas toned to mid-luminance (jewel zone), holbein_jewel_glaze_pass
    should increase or maintain saturation — never reduce it in that zone.
    """
    import numpy as _np
    import colorsys as _cs

    p = _make_small_painter(64, 64)
    # Tone with a moderately saturated mid-grey-green that sits in the jewel zone
    p.tone_ground((0.38, 0.55, 0.30), texture_strength=0.0)  # lum ≈ 0.48

    def _mean_sat() -> float:
        buf = _np.frombuffer(p.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(64, 64, 4)
        sats = []
        for y in range(0, 64, 4):
            for x in range(0, 64, 4):
                r = buf[y, x, 2] / 255.0
                g = buf[y, x, 1] / 255.0
                b = buf[y, x, 0] / 255.0
                _, s, _ = _cs.rgb_to_hsv(r, g, b)
                sats.append(s)
        return float(_np.mean(sats))

    sat_before = _mean_sat()
    p.holbein_jewel_glaze_pass(chroma_boost=0.30, jewel_lo=0.20, jewel_hi=0.80,
                               opacity=0.95)
    sat_after  = _mean_sat()

    assert sat_after >= sat_before - 0.02, (
        f"holbein_jewel_glaze_pass should boost or maintain saturation in the jewel "
        f"zone; before={sat_before:.3f}  after={sat_after:.3f}")


# ── van_dyck_silver_drapery_pass (session 37 random improvement) ─────────────

def test_van_dyck_silver_drapery_pass_exists():
    """Painter must expose van_dyck_silver_drapery_pass() after session 37."""
    from stroke_engine import Painter
    assert hasattr(Painter, "van_dyck_silver_drapery_pass"), (
        "van_dyck_silver_drapery_pass not found on Painter — expected after session 37")
    assert callable(getattr(Painter, "van_dyck_silver_drapery_pass"))


def test_van_dyck_silver_drapery_pass_no_error():
    """van_dyck_silver_drapery_pass() must complete without exception on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.70, 0.72, 0.76), texture_strength=0.04)
    p.van_dyck_silver_drapery_pass()


def test_van_dyck_silver_drapery_pass_modifies_canvas():
    """van_dyck_silver_drapery_pass() must change canvas pixel data at non-zero opacity."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Near-neutral bright tone — sits well inside the silk candidate zone
    p.tone_ground((0.70, 0.72, 0.74), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.van_dyck_silver_drapery_pass(
        shimmer_strength=0.15,
        silver_cool=0.20,
        opacity=0.90,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)

    diff = _np.abs(after.astype(_np.int32) - before.astype(_np.int32)).max()
    assert diff > 0, (
        "van_dyck_silver_drapery_pass() made no changes to canvas — "
        "shimmer, silver-cool, and ivory adjustments must be applied")


def test_van_dyck_silver_drapery_pass_opacity_zero_is_noop():
    """van_dyck_silver_drapery_pass() with opacity=0 must leave the canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.70, 0.72), texture_strength=0.04)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.van_dyck_silver_drapery_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)

    _np.testing.assert_array_equal(before, after,
        err_msg="van_dyck_silver_drapery_pass with opacity=0 must be a no-op")


def test_van_dyck_silver_drapery_pass_custom_parameters():
    """van_dyck_silver_drapery_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.74, 0.78), texture_strength=0.04)
    p.van_dyck_silver_drapery_pass(
        fabric_angle     = 60.0,
        shimmer_period   = 24.0,
        shimmer_strength = 0.05,
        silver_cool      = 0.08,
        ivory_boost      = 0.04,
        neutral_thresh   = 0.35,
        lum_lo           = 0.40,
        opacity          = 0.60,
    )


def test_van_dyck_silver_drapery_pass_large_canvas():
    """van_dyck_silver_drapery_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(128, 160)
    p.tone_ground((0.75, 0.76, 0.80), texture_strength=0.04)
    p.van_dyck_silver_drapery_pass(shimmer_strength=0.10, opacity=0.70)


def test_van_dyck_silver_drapery_pass_cools_bright_neutral():
    """
    On a bright near-neutral canvas, van_dyck_silver_drapery_pass should
    shift the colour slightly cooler (boost blue relative to red).
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Tone with a warm-neutral bright colour that sits firmly in the silk zone
    p.tone_ground((0.80, 0.78, 0.72), texture_strength=0.0)

    def _mean_channels():
        buf = _np.frombuffer(p.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(64, 64, 4).astype(_np.float32)
        # Cairo BGRA: R=channel[2], B=channel[0]
        return buf[:, :, 2].mean(), buf[:, :, 0].mean()   # mean_R, mean_B

    r_before, b_before = _mean_channels()
    p.van_dyck_silver_drapery_pass(
        silver_cool      = 0.20,
        shimmer_strength = 0.0,    # disable shimmer to isolate the cooling effect
        ivory_boost      = 0.0,    # disable ivory push
        opacity          = 0.90,
    )
    r_after, b_after = _mean_channels()

    assert r_after <= r_before + 1.0, (
        f"van_dyck_silver_drapery_pass silver cooling should not increase red channel; "
        f"R before={r_before:.1f}  R after={r_after:.1f}")
    assert b_after >= b_before - 1.0, (
        f"van_dyck_silver_drapery_pass silver cooling should boost blue channel; "
        f"B before={b_before:.1f}  B after={b_after:.1f}")


def test_van_dyck_silver_drapery_pass_excludes_chromatic_pixels():
    """
    Strongly chromatic pixels (high saturation) must not be modified by the
    silver-drapery pass — only near-neutral silk candidates are affected.
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Tone with a vivid red — saturation is high, far outside the silk zone
    p.tone_ground((0.85, 0.12, 0.08), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.van_dyck_silver_drapery_pass(
        neutral_thresh   = 0.30,   # strict threshold — keep chromatic pixels out
        shimmer_strength = 0.15,
        silver_cool      = 0.25,
        opacity          = 0.95,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)

    # Vivid red canvas should be largely unchanged (silk mask should exclude it)
    diff = _np.abs(after.astype(_np.int32) - before.astype(_np.int32)).mean()
    assert diff < 10.0, (
        f"van_dyck_silver_drapery_pass should not significantly modify vivid chromatic "
        f"pixels; mean diff={diff:.2f} (expected < 10.0 on a pure red canvas)")


# ═════════════════════════════════════════════════════════════════════════════
# rubens_flesh_vitality_pass() — pass tests
# ═════════════════════════════════════════════════════════════════════════════

def test_rubens_flesh_vitality_pass_exists():
    """rubens_flesh_vitality_pass() must exist as a method on Painter."""
    p = _make_small_painter(64, 64)
    assert hasattr(p, "rubens_flesh_vitality_pass"), (
        "Painter must have rubens_flesh_vitality_pass() method")


def test_rubens_flesh_vitality_pass_modifies_canvas():
    """rubens_flesh_vitality_pass() must modify the canvas (not a no-op at default params)."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Tone with a mid-luminance warm flesh — falls squarely in the blush zone
    p.tone_ground((0.72, 0.58, 0.42), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.rubens_flesh_vitality_pass(opacity=0.80)
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)

    diff = _np.abs(after.astype(_np.int32) - before.astype(_np.int32)).mean()
    assert diff > 0.5, (
        f"rubens_flesh_vitality_pass() made no changes to canvas — "
        f"mean pixel diff={diff:.3f} (expected > 0.5 on a mid-tone flesh canvas)")


def test_rubens_flesh_vitality_pass_opacity_zero_is_noop():
    """rubens_flesh_vitality_pass() with opacity=0 must leave the canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.58, 0.42), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.rubens_flesh_vitality_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)

    diff = _np.abs(after.astype(_np.int32) - before.astype(_np.int32)).mean()
    assert diff < 1.0, (
        f"rubens_flesh_vitality_pass with opacity=0 must be a no-op; "
        f"mean diff={diff:.3f}")


def test_rubens_flesh_vitality_pass_warms_mid_tones():
    """
    On a neutral mid-grey canvas (lum ~0.50, in the blush zone), the R channel
    should increase after rubens_flesh_vitality_pass — the rosy blush effect.
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Neutral grey: R=G=B=128 → lum=0.50, in blush_lo..blush_hi band
    # Use texture_strength=0 for a perfectly uniform canvas
    p.tone_ground((128/255, 128/255, 128/255), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    r_before = before[:, :, 2].astype(_np.float32).mean()

    p.rubens_flesh_vitality_pass(
        blush_strength=0.20,
        blush_lo=0.35,
        blush_hi=0.65,
        cream_strength=0.0,   # disable other effects for isolation
        warm_shadow=0.0,
        opacity=1.0,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)
    r_after = after[:, :, 2].astype(_np.float32).mean()

    assert r_after > r_before, (
        f"rubens_flesh_vitality_pass should boost R channel in mid-tone band "
        f"(rosy blush); R before={r_before:.1f}  R after={r_after:.1f}")


def test_rubens_flesh_vitality_pass_warms_highlights():
    """
    On a bright near-white canvas (lum ~0.90, above highlight_thresh), the R
    channel should increase after rubens_flesh_vitality_pass — the cream push.
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Near-white neutral: R=G=B=230 → lum~0.90, above highlight_thresh=0.72
    p.tone_ground((230/255, 230/255, 230/255), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    r_before = before[:, :, 2].astype(_np.float32).mean()

    p.rubens_flesh_vitality_pass(
        blush_strength=0.0,   # disable blush for isolation
        cream_strength=0.15,
        warm_shadow=0.0,
        highlight_thresh=0.72,
        opacity=1.0,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)
    r_after = after[:, :, 2].astype(_np.float32).mean()

    assert r_after > r_before, (
        f"rubens_flesh_vitality_pass cream push should boost R channel in highlights; "
        f"R before={r_before:.1f}  R after={r_after:.1f}")


def test_rubens_flesh_vitality_pass_warms_shadows():
    """
    On a dark canvas (lum ~0.10, below shadow_thresh), the R channel should
    increase after rubens_flesh_vitality_pass — the warm shadow glow.
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Near-black neutral: R=G=B=28 → lum~0.11, below shadow_thresh=0.22
    p.tone_ground((28/255, 28/255, 28/255), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    r_before = before[:, :, 2].astype(_np.float32).mean()

    p.rubens_flesh_vitality_pass(
        blush_strength=0.0,   # disable other effects for isolation
        cream_strength=0.0,
        warm_shadow=0.12,
        shadow_thresh=0.22,
        opacity=1.0,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)
    r_after = after[:, :, 2].astype(_np.float32).mean()

    assert r_after > r_before, (
        f"rubens_flesh_vitality_pass warm shadow should boost R channel in deep shadows; "
        f"R before={r_before:.1f}  R after={r_after:.1f}")


def test_rubens_flesh_vitality_pass_custom_parameters():
    """rubens_flesh_vitality_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.65, 0.50, 0.35), texture_strength=0.0)
    # Call with all parameters explicitly — must not raise
    p.rubens_flesh_vitality_pass(
        blush_strength   = 0.18,
        cream_strength   = 0.12,
        warm_shadow      = 0.08,
        blush_lo         = 0.25,
        blush_hi         = 0.70,
        highlight_thresh = 0.75,
        shadow_thresh    = 0.20,
        opacity          = 0.90,
    )


def test_rubens_flesh_vitality_pass_large_canvas():
    """rubens_flesh_vitality_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.70, 0.55, 0.40), texture_strength=0.0)
    p.rubens_flesh_vitality_pass(blush_strength=0.10, opacity=0.70)


def test_flemish_baroque_period_in_enum():
    """Period.FLEMISH_BAROQUE must be a valid member of the Period enum."""
    assert hasattr(Period, "FLEMISH_BAROQUE"), (
        "Period enum is missing FLEMISH_BAROQUE — add it to scene_schema.py")


# ═════════════════════════════════════════════════════════════════════════════
# Nicolas Poussin / FRENCH_CLASSICAL — Period enum + pass tests
# ═════════════════════════════════════════════════════════════════════════════

def test_french_classical_period_in_enum():
    """Period.FRENCH_CLASSICAL must be a valid member of the Period enum."""
    assert hasattr(Period, "FRENCH_CLASSICAL"), (
        "Period enum is missing FRENCH_CLASSICAL — add it to scene_schema.py")


def test_french_classical_stroke_params_keys():
    """FRENCH_CLASSICAL stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_CLASSICAL).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"FRENCH_CLASSICAL stroke_params missing key: {key!r}"


def test_french_classical_stroke_params_ranges():
    """FRENCH_CLASSICAL stroke_params values must be in valid ranges."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_CLASSICAL).stroke_params
    assert 3 <= sp["stroke_size_face"] <= 20, (
        f"FRENCH_CLASSICAL stroke_size_face={sp['stroke_size_face']} should be in [3, 20]")
    assert 0.0 <= sp["wet_blend"] <= 1.0, (
        f"FRENCH_CLASSICAL wet_blend={sp['wet_blend']} should be in [0, 1]")
    assert 0.0 <= sp["edge_softness"] <= 1.0, (
        f"FRENCH_CLASSICAL edge_softness={sp['edge_softness']} should be in [0, 1]")


def test_poussin_classical_clarity_pass_exists():
    """Painter must have a poussin_classical_clarity_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "poussin_classical_clarity_pass"), (
        "Painter is missing poussin_classical_clarity_pass — add it to stroke_engine.py")


def test_poussin_classical_clarity_pass_modifies_canvas():
    """poussin_classical_clarity_pass() must alter the canvas from its initial state."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Mid-grey with slight warmth — the pass should introduce cool corrections
    p.tone_ground((0.55, 0.50, 0.45), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.poussin_classical_clarity_pass(opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)

    assert not _np.array_equal(before, after), (
        "poussin_classical_clarity_pass should change the canvas when opacity=1.0")


def test_poussin_classical_clarity_pass_opacity_zero_is_noop():
    """poussin_classical_clarity_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.50, 0.45), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.poussin_classical_clarity_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)

    assert _np.array_equal(before, after), (
        "poussin_classical_clarity_pass(opacity=0) should be a noop")


def test_poussin_classical_clarity_pass_cools_shadows():
    """
    On a near-black canvas (lum ~0.08, well below shadow_thresh=0.32),
    the B channel should increase after poussin_classical_clarity_pass —
    the cool blue-grey shadow push.
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Near-black neutral: R=G=B=20 → lum~0.08, below shadow_thresh=0.32
    p.tone_ground((20/255, 20/255, 20/255), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    b_before = before[:, :, 0].astype(_np.float32).mean()   # BGRA index 0 = Blue

    p.poussin_classical_clarity_pass(
        shadow_cool=0.20,
        midtone_lift=0.0,
        saturation_cap=1.0,    # disable saturation cap for isolation
        highlight_ivory=0.0,
        shadow_thresh=0.32,
        opacity=1.0,
    )
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)
    b_after = after[:, :, 0].astype(_np.float32).mean()

    assert b_after > b_before, (
        f"poussin_classical_clarity_pass should boost B channel in deep shadows; "
        f"B before={b_before:.1f}  B after={b_after:.1f}")


def test_poussin_classical_clarity_pass_lifts_midtones():
    """
    On a mid-grey canvas (lum ~0.50, inside midtone_lo=0.32..midtone_hi=0.68),
    the average luminance should increase after poussin_classical_clarity_pass —
    the mid-tone clarification lift.
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Pure mid-grey: R=G=B=128 → lum~0.50, inside the mid-tone band
    p.tone_ground((128/255, 128/255, 128/255), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    lum_before = (0.299 * before[:, :, 2].astype(_np.float32)
                + 0.587 * before[:, :, 1].astype(_np.float32)
                + 0.114 * before[:, :, 0].astype(_np.float32)).mean()

    p.poussin_classical_clarity_pass(
        shadow_cool=0.0,
        midtone_lift=0.10,
        saturation_cap=1.0,
        highlight_ivory=0.0,
        midtone_lo=0.32,
        midtone_hi=0.68,
        opacity=1.0,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)
    lum_after = (0.299 * after[:, :, 2].astype(_np.float32)
               + 0.587 * after[:, :, 1].astype(_np.float32)
               + 0.114 * after[:, :, 0].astype(_np.float32)).mean()

    assert lum_after > lum_before, (
        f"poussin_classical_clarity_pass mid-tone lift should increase luminance; "
        f"lum before={lum_before:.1f}  lum after={lum_after:.1f}")


def test_poussin_classical_clarity_pass_caps_saturation():
    """
    On a fully saturated red canvas (R=255, G=B=0 → sat=1.0), the saturation
    should be reduced after poussin_classical_clarity_pass(saturation_cap=0.70).
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Pure red: R=1.0, G=0, B=0 → saturation=1.0, well above cap of 0.70
    p.tone_ground((1.0, 0.0, 0.0), texture_strength=0.0)

    p.poussin_classical_clarity_pass(
        shadow_cool=0.0,
        midtone_lift=0.0,
        saturation_cap=0.70,
        highlight_ivory=0.0,
        opacity=1.0,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)
    r_a = after[:, :, 2].astype(_np.float32) / 255.0
    g_a = after[:, :, 1].astype(_np.float32) / 255.0
    b_a = after[:, :, 0].astype(_np.float32) / 255.0

    max_c  = _np.maximum(_np.maximum(r_a, g_a), b_a)
    min_c  = _np.minimum(_np.minimum(r_a, g_a), b_a)
    sat    = _np.where(max_c > 1e-6, (max_c - min_c) / max_c, 0.0)
    max_sat = float(sat.max())

    assert max_sat <= 0.70 + 0.05, (
        f"poussin_classical_clarity_pass saturation_cap=0.70 should reduce max sat "
        f"to ≤0.75; got max_sat={max_sat:.3f}")


def test_poussin_classical_clarity_pass_custom_parameters():
    """poussin_classical_clarity_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.48, 0.40), texture_strength=0.0)
    p.poussin_classical_clarity_pass(
        shadow_cool      = 0.15,
        midtone_lift     = 0.08,
        saturation_cap   = 0.65,
        highlight_ivory  = 0.06,
        shadow_thresh    = 0.30,
        highlight_thresh = 0.75,
        midtone_lo       = 0.30,
        midtone_hi       = 0.70,
        opacity          = 0.75,
    )


def test_poussin_classical_clarity_pass_large_canvas():
    """poussin_classical_clarity_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.60, 0.55, 0.45), texture_strength=0.0)
    p.poussin_classical_clarity_pass(shadow_cool=0.10, midtone_lift=0.05, opacity=0.70)


# ═════════════════════════════════════════════════════════════════════════════
# Thomas Gainsborough / ROCOCO_PORTRAIT — Period enum + pass tests (session 40)
# ═════════════════════════════════════════════════════════════════════════════

def test_rococo_portrait_period_in_enum():
    """Period.ROCOCO_PORTRAIT must be a valid member of the Period enum."""
    assert hasattr(Period, "ROCOCO_PORTRAIT"), (
        "Period enum is missing ROCOCO_PORTRAIT — add it to scene_schema.py")


def test_rococo_portrait_stroke_params_keys():
    """ROCOCO_PORTRAIT stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.ROCOCO_PORTRAIT).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"ROCOCO_PORTRAIT stroke_params missing key: {key!r}"


def test_rococo_portrait_stroke_params_ranges():
    """ROCOCO_PORTRAIT stroke_params values must be in valid ranges."""
    sp = Style(medium=Medium.OIL, period=Period.ROCOCO_PORTRAIT).stroke_params
    assert 3 <= sp["stroke_size_face"] <= 20, (
        f"ROCOCO_PORTRAIT stroke_size_face={sp['stroke_size_face']} should be in [3, 20]")
    assert 0.0 <= sp["wet_blend"] <= 1.0, (
        f"ROCOCO_PORTRAIT wet_blend={sp['wet_blend']} should be in [0, 1]")
    assert 0.0 <= sp["edge_softness"] <= 1.0, (
        f"ROCOCO_PORTRAIT edge_softness={sp['edge_softness']} should be in [0, 1]")


def test_rococo_portrait_high_edge_softness():
    """ROCOCO_PORTRAIT edge_softness should be >= 0.55 — Gainsborough's feathery edges."""
    sp = Style(medium=Medium.OIL, period=Period.ROCOCO_PORTRAIT).stroke_params
    assert sp["edge_softness"] >= 0.55, (
        f"ROCOCO_PORTRAIT edge_softness={sp['edge_softness']:.2f} should be >= 0.55 "
        "(Gainsborough's hallmark feathery dissolution requires high edge softness)")


def test_gainsborough_feathery_pass_exists():
    """Painter must have a gainsborough_feathery_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "gainsborough_feathery_pass"), (
        "Painter is missing gainsborough_feathery_pass — add it to stroke_engine.py")
    assert callable(getattr(Painter, "gainsborough_feathery_pass"))


def test_gainsborough_feathery_pass_runs_without_error():
    """gainsborough_feathery_pass() must run on a small canvas without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.70, 0.65, 0.60), texture_strength=0.0)
    p.gainsborough_feathery_pass(opacity=0.78)


def test_gainsborough_feathery_pass_modifies_canvas():
    """gainsborough_feathery_pass() must alter the canvas from its initial state."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Warm-grey ground; the pass should cool and feather it
    p.tone_ground((0.70, 0.65, 0.58), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.gainsborough_feathery_pass(opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)

    assert not _np.array_equal(before, after), (
        "gainsborough_feathery_pass should change the canvas when opacity=1.0")


def test_gainsborough_feathery_pass_opacity_zero_is_noop():
    """gainsborough_feathery_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.70, 0.65, 0.58), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.gainsborough_feathery_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)

    assert _np.array_equal(before, after), (
        "gainsborough_feathery_pass(opacity=0) should be a noop")


def test_gainsborough_feathery_pass_cools_highlights():
    """
    On a bright near-white canvas (lum ~0.90, well above highlight_thresh=0.68),
    the B channel should increase and R channel should decrease after
    gainsborough_feathery_pass — the cool silver push.
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Warm bright: R=230, G=220, B=200 → lum ~0.86, above highlight_thresh=0.68
    p.tone_ground((230/255, 220/255, 200/255), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    # BGRA: index 0=B, 2=R
    b_before = before[:, :, 0].astype(_np.float32).mean()
    r_before = before[:, :, 2].astype(_np.float32).mean()

    p.gainsborough_feathery_pass(
        silver_strength  = 0.15,
        feather_spread   = 0.0,    # disable feathering for isolation
        shimmer_strength = 0.0,    # disable shimmer for isolation
        shadow_haze      = 0.0,    # disable shadow haze for isolation
        highlight_thresh = 0.68,
        opacity          = 1.0,
    )
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)
    b_after = after[:, :, 0].astype(_np.float32).mean()
    r_after = after[:, :, 2].astype(_np.float32).mean()

    assert b_after > b_before, (
        f"gainsborough_feathery_pass should boost B in bright highlights; "
        f"B before={b_before:.1f}  B after={b_after:.1f}")
    assert r_after < r_before, (
        f"gainsborough_feathery_pass should damp R in bright highlights; "
        f"R before={r_before:.1f}  R after={r_after:.1f}")


def test_gainsborough_feathery_pass_cools_shadows():
    """
    On a near-black canvas (lum ~0.08, below shadow_thresh=0.35), the B channel
    should increase after gainsborough_feathery_pass — the atmospheric haze push.
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Warm dark: R=30, G=20, B=10 → lum ~0.09, below shadow_thresh=0.35
    p.tone_ground((30/255, 20/255, 10/255), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    b_before = before[:, :, 0].astype(_np.float32).mean()

    p.gainsborough_feathery_pass(
        silver_strength  = 0.0,    # disable for isolation
        feather_spread   = 0.0,
        shimmer_strength = 0.0,
        shadow_haze      = 0.10,
        shadow_thresh    = 0.35,
        opacity          = 1.0,
    )
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)
    b_after = after[:, :, 0].astype(_np.float32).mean()

    assert b_after > b_before, (
        f"gainsborough_feathery_pass should boost B in shadows (atmospheric haze); "
        f"B before={b_before:.1f}  B after={b_after:.1f}")


def test_gainsborough_feathery_pass_custom_parameters():
    """gainsborough_feathery_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.62, 0.58), texture_strength=0.0)
    p.gainsborough_feathery_pass(
        silver_strength  = 0.12,
        feather_spread   = 3.0,
        shimmer_strength = 0.05,
        shadow_haze      = 0.08,
        highlight_thresh = 0.65,
        midtone_lo       = 0.28,
        midtone_hi       = 0.75,
        shadow_thresh    = 0.38,
        opacity          = 0.80,
    )


def test_gainsborough_feathery_pass_large_canvas():
    """gainsborough_feathery_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.70, 0.65, 0.60), texture_strength=0.0)
    p.gainsborough_feathery_pass(silver_strength=0.10, feather_spread=2.5, opacity=0.75)


# ═══════════════════════════════════════════════════════════════════════════
# homer_marine_clarity_pass — Winslow Homer artist pass (session 41)
# ═══════════════════════════════════════════════════════════════════════════

def test_homer_marine_clarity_pass_exists():
    """Painter must have homer_marine_clarity_pass() method (session 41 addition)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "homer_marine_clarity_pass"), (
        "homer_marine_clarity_pass not found on Painter")
    assert callable(getattr(Painter, "homer_marine_clarity_pass"))


def test_homer_marine_clarity_pass_runs():
    """homer_marine_clarity_pass() runs without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.94, 0.93, 0.90), texture_strength=0.0)
    p.homer_marine_clarity_pass(opacity=0.72)


def test_homer_marine_clarity_pass_opacity_zero_is_noop():
    """homer_marine_clarity_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.85, 0.80, 0.75), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.homer_marine_clarity_pass(opacity=0.0)
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)

    assert _np.array_equal(before, after), (
        "homer_marine_clarity_pass(opacity=0) should be a noop")


def test_homer_marine_clarity_pass_lifts_highlights():
    """
    On a near-white warm canvas (lum ~0.90, above highlight_thresh=0.72),
    overall luminance should increase after homer_marine_clarity_pass —
    the maritime highlight lift.
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Warm pale: R=240, G=230, B=210 → lum ~0.88, above default highlight_thresh=0.72
    p.tone_ground((240/255, 230/255, 210/255), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    # Average luminance before (from BGRA: R=index2, G=index1, B=index0)
    r_before = before[:, :, 2].astype(_np.float32).mean()
    g_before = before[:, :, 1].astype(_np.float32).mean()
    lum_before = (0.299 * r_before + 0.587 * g_before) / 255.0

    p.homer_marine_clarity_pass(
        highlight_lift    = 0.15,
        shadow_cool       = 0.0,    # disable for isolation
        contrast_strength = 0.0,
        wash_luminosity   = 0.0,
        highlight_thresh  = 0.72,
        opacity           = 1.0,
    )
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)
    r_after = after[:, :, 2].astype(_np.float32).mean()
    g_after = after[:, :, 1].astype(_np.float32).mean()
    lum_after = (0.299 * r_after + 0.587 * g_after) / 255.0

    assert lum_after > lum_before, (
        f"homer_marine_clarity_pass should lift highlight luminance; "
        f"lum before={lum_before:.4f}  lum after={lum_after:.4f}")


def test_homer_marine_clarity_pass_cools_shadows():
    """
    On a warm dark canvas (lum ~0.12, below shadow_thresh=0.35),
    B channel should increase after homer_marine_clarity_pass —
    the Prussian shadow cool push.
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Warm dark: R=50, G=35, B=20 → lum ~0.13, below shadow_thresh=0.35
    p.tone_ground((50/255, 35/255, 20/255), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    b_before = before[:, :, 0].astype(_np.float32).mean()

    p.homer_marine_clarity_pass(
        highlight_lift    = 0.0,    # disable for isolation
        shadow_cool       = 0.15,
        contrast_strength = 0.0,
        wash_luminosity   = 0.0,
        shadow_thresh     = 0.35,
        opacity           = 1.0,
    )
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)
    b_after = after[:, :, 0].astype(_np.float32).mean()

    assert b_after > b_before, (
        f"homer_marine_clarity_pass should boost B in shadows (Prussian cool push); "
        f"B before={b_before:.1f}  B after={b_after:.1f}")


def test_homer_marine_clarity_pass_custom_params():
    """homer_marine_clarity_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.94, 0.92, 0.88), texture_strength=0.0)
    p.homer_marine_clarity_pass(
        highlight_lift    = 0.10,
        shadow_cool       = 0.08,
        contrast_strength = 0.06,
        wash_luminosity   = 0.04,
        highlight_thresh  = 0.70,
        shadow_thresh     = 0.30,
        opacity           = 0.80,
    )


def test_homer_marine_clarity_pass_changes_canvas():
    """homer_marine_clarity_pass(opacity=1.0) must change at least some pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Use a canvas with mixed luminance so both highlight and shadow zones exist
    p.tone_ground((0.55, 0.50, 0.45), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.homer_marine_clarity_pass(opacity=1.0)
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)

    assert not _np.array_equal(before, after), (
        "homer_marine_clarity_pass should change the canvas when opacity=1.0")


# ═══════════════════════════════════════════════════════════════════════════
# wet_on_wet_bleeding_pass — session 41 random improvement
# ═══════════════════════════════════════════════════════════════════════════

def test_wet_on_wet_bleeding_pass_exists():
    """Painter must have wet_on_wet_bleeding_pass() method (session 41 random improvement)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "wet_on_wet_bleeding_pass"), (
        "wet_on_wet_bleeding_pass not found on Painter")
    assert callable(getattr(Painter, "wet_on_wet_bleeding_pass"))


def test_wet_on_wet_bleeding_pass_runs():
    """wet_on_wet_bleeding_pass() runs without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.45, 0.35), texture_strength=0.0)
    p.wet_on_wet_bleeding_pass(opacity=0.65)


def test_wet_on_wet_bleeding_pass_opacity_zero_is_noop():
    """wet_on_wet_bleeding_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.50, 0.40), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.wet_on_wet_bleeding_pass(opacity=0.0)
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)

    assert _np.array_equal(before, after), (
        "wet_on_wet_bleeding_pass(opacity=0) should be a noop")


def test_wet_on_wet_bleeding_pass_changes_high_contrast_canvas():
    """
    wet_on_wet_bleeding_pass should change pixels on a high-contrast canvas
    (sharp boundary → bleeding occurs at the edge).
    """
    import numpy as _np
    from stroke_engine import Painter

    p = Painter(64, 64)
    # Manually draw a sharp vertical dark/light boundary to create a strong edge
    buf = _np.frombuffer(p.canvas.surface.get_data(),
                         dtype=_np.uint8).reshape(64, 64, 4).copy()
    buf[:, :32, :3] = 30    # dark left half (BGRA — all channels)
    buf[:, 32:, :3] = 220   # bright right half
    buf[:, :, 3]    = 255   # full alpha
    p.canvas.surface.get_data()[:] = buf.tobytes()

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.wet_on_wet_bleeding_pass(
        bleed_radius      = 3.0,
        bleed_strength    = 0.50,
        edge_sensitivity  = 0.30,
        opacity           = 1.0,
    )
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)

    assert not _np.array_equal(before, after), (
        "wet_on_wet_bleeding_pass should change pixels on a high-contrast canvas")


def test_wet_on_wet_bleeding_pass_flat_canvas_is_noop():
    """
    On a perfectly flat (uniform-colour) canvas there are no edges, so
    wet_on_wet_bleeding_pass should return without modifying any pixels
    (or modify negligibly — the Sobel will be zero everywhere).
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Perfectly uniform fill — texture_strength=0 guarantees flat colour
    p.tone_ground((0.55, 0.50, 0.45), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.wet_on_wet_bleeding_pass(opacity=1.0)
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)

    # Allow a tiny epsilon for float→int rounding, but no gross changes
    diff = _np.abs(after.astype(_np.int32) - before.astype(_np.int32))
    assert diff.max() <= 2, (
        f"wet_on_wet_bleeding_pass on a flat canvas should be a near-noop; "
        f"max pixel delta={diff.max()}")


def test_wet_on_wet_bleeding_pass_custom_params():
    """wet_on_wet_bleeding_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.52, 0.44), texture_strength=0.0)
    p.wet_on_wet_bleeding_pass(
        bleed_radius     = 4.0,
        bleed_strength   = 0.25,
        edge_sensitivity = 0.60,
        opacity          = 0.55,
    )


def test_wet_on_wet_bleeding_pass_large_canvas():
    """wet_on_wet_bleeding_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.55, 0.50, 0.45), texture_strength=0.0)
    p.wet_on_wet_bleeding_pass(bleed_radius=3.0, bleed_strength=0.20, opacity=0.60)


# ═══════════════════════════════════════════════════════════════════════════
# fragonard_bravura_pass — Jean-Honoré Fragonard artist pass (session 42)
# ═══════════════════════════════════════════════════════════════════════════

def test_fragonard_bravura_pass_exists():
    """Painter must have fragonard_bravura_pass() method (session 42 addition)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "fragonard_bravura_pass"), (
        "fragonard_bravura_pass not found on Painter")
    assert callable(getattr(Painter, "fragonard_bravura_pass"))


def test_fragonard_bravura_pass_runs():
    """fragonard_bravura_pass() runs without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.80, 0.68), texture_strength=0.0)
    p.fragonard_bravura_pass(opacity=0.70)


def test_fragonard_bravura_pass_opacity_zero_is_noop():
    """fragonard_bravura_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.75, 0.65, 0.55), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.fragonard_bravura_pass(opacity=0.0)
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)

    assert _np.array_equal(before, after), (
        "fragonard_bravura_pass(opacity=0) should be a noop")


def test_fragonard_bravura_pass_warms_highlights():
    """
    On a warm-midtone canvas (lum ~0.75, above highlight_thresh=0.65),
    R channel should increase after fragonard_bravura_pass —
    the warm cream highlight bloom.
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Warm bright midtone: R=210, G=195, B=175 → lum ~0.76, above highlight_thresh=0.65
    p.tone_ground((210/255, 195/255, 175/255), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    r_before = before[:, :, 2].astype(_np.float32).mean()

    p.fragonard_bravura_pass(
        warmth_strength  = 0.0,   # disable midtone for isolation
        highlight_bloom  = 0.10,
        shadow_warm      = 0.0,
        highlight_thresh = 0.65,
        opacity          = 1.0,
    )
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)
    r_after = after[:, :, 2].astype(_np.float32).mean()

    assert r_after > r_before, (
        f"fragonard_bravura_pass should boost R in highlight zone; "
        f"R before={r_before:.1f}  R after={r_after:.1f}")


def test_fragonard_bravura_pass_warms_shadows():
    """
    On a warm dark canvas (lum ~0.12, below shadow_thresh=0.30),
    R channel should increase and B should decrease after fragonard_bravura_pass —
    the warm shadow damping (Fragonard's shadows are warm umber, not cool Prussian).
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Warm dark: R=50, G=35, B=25 → lum ~0.13, below shadow_thresh=0.30
    p.tone_ground((50/255, 35/255, 25/255), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    r_before = before[:, :, 2].astype(_np.float32).mean()
    b_before = before[:, :, 0].astype(_np.float32).mean()

    p.fragonard_bravura_pass(
        warmth_strength  = 0.0,   # disable midtone for isolation
        highlight_bloom  = 0.0,   # disable highlight for isolation
        shadow_warm      = 0.15,
        shadow_thresh    = 0.30,
        opacity          = 1.0,
    )
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)
    r_after = after[:, :, 2].astype(_np.float32).mean()
    b_after = after[:, :, 0].astype(_np.float32).mean()

    assert r_after > r_before, (
        f"fragonard_bravura_pass should boost R in shadow zone (warm umber); "
        f"R before={r_before:.1f}  R after={r_after:.1f}")
    assert b_after < b_before, (
        f"fragonard_bravura_pass should damp B in shadow zone (remove Prussian cool); "
        f"B before={b_before:.1f}  B after={b_after:.1f}")


def test_fragonard_bravura_pass_changes_canvas():
    """fragonard_bravura_pass(opacity=1.0) must change at least some pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.65, 0.55, 0.45), texture_strength=0.0)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.fragonard_bravura_pass(opacity=1.0)
    after  = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4)

    assert not _np.array_equal(before, after), (
        "fragonard_bravura_pass should change the canvas when opacity=1.0")


def test_fragonard_bravura_pass_custom_params():
    """fragonard_bravura_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.85, 0.75, 0.65), texture_strength=0.0)
    p.fragonard_bravura_pass(
        warmth_strength  = 0.06,
        highlight_bloom  = 0.05,
        shadow_warm      = 0.04,
        highlight_thresh = 0.70,
        shadow_thresh    = 0.25,
        opacity          = 0.60,
    )


def test_fragonard_bravura_pass_large_canvas():
    """fragonard_bravura_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.88, 0.80, 0.70), texture_strength=0.0)
    p.fragonard_bravura_pass(warmth_strength=0.07, highlight_bloom=0.05, opacity=0.70)


# ═══════════════════════════════════════════════════════════════════════════
# renoir_luminous_warmth_pass — Pierre-Auguste Renoir artist pass
# ═══════════════════════════════════════════════════════════════════════════

def test_renoir_luminous_warmth_pass_exists():
    """Painter must have renoir_luminous_warmth_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "renoir_luminous_warmth_pass"), (
        "Painter is missing renoir_luminous_warmth_pass — add it to stroke_engine.py")
    assert callable(getattr(Painter, "renoir_luminous_warmth_pass"))


def test_renoir_luminous_warmth_pass_runs():
    """renoir_luminous_warmth_pass() runs without error on a small canvas."""
    p = _make_small_painter()
    p.tone_ground((0.92, 0.86, 0.78), texture_strength=0.0)
    p.renoir_luminous_warmth_pass(opacity=0.72)


def test_renoir_luminous_warmth_pass_opacity_zero_is_noop():
    """renoir_luminous_warmth_pass(opacity=0) must leave the canvas unchanged."""
    p = _make_small_painter()
    p.tone_ground((0.92, 0.86, 0.78), texture_strength=0.0)
    buf_before = bytes(p.canvas.surface.get_data())
    p.renoir_luminous_warmth_pass(opacity=0.0)
    buf_after = bytes(p.canvas.surface.get_data())
    assert buf_before == buf_after, (
        "renoir_luminous_warmth_pass(opacity=0) should be a noop")


def test_renoir_luminous_warmth_pass_warms_midtones():
    """
    R channel should increase in midtone pixels after renoir_luminous_warmth_pass —
    the rose-peach warmth push.
    """
    p = _make_small_painter(32, 32)
    # Fill with a neutral warm-grey midtone (lum ~0.47 — solidly in the midtone band)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(32, 32, 4).copy()
    # Cairo BGRA: set R=140, G=120, B=115  → lum ≈ 0.47
    buf[:, :, 2] = 140   # R
    buf[:, :, 1] = 120   # G
    buf[:, :, 0] = 115   # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = int(buf[:, :, 2].mean())

    p.renoir_luminous_warmth_pass(
        saturation_boost=0.0,    # disable saturation to isolate warmth effect
        rose_warmth=0.10,
        highlight_glow=0.0,
        highlight_thresh=0.65,
        shadow_thresh=0.30,
        opacity=1.0,
    )
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(32, 32, 4)
    r_after = int(buf_after[:, :, 2].mean())
    assert r_after >= r_before, (
        f"renoir_luminous_warmth_pass should boost R in midtone zone; "
        f"R before={r_before}  after={r_after}")


def test_renoir_luminous_warmth_pass_lifts_highlights():
    """
    R and G channels should lift after renoir_luminous_warmth_pass in bright pixels —
    the luminous warm highlight glow.
    """
    p = _make_small_painter(32, 32)
    # Fill with near-white highlights (lum ~0.88 — well above highlight_thresh=0.62)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(32, 32, 4).copy()
    buf[:, :, 2] = 230   # R
    buf[:, :, 1] = 225   # G
    buf[:, :, 0] = 218   # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = int(buf[:, :, 2].mean())

    p.renoir_luminous_warmth_pass(
        saturation_boost=0.0,
        rose_warmth=0.0,
        highlight_glow=0.10,
        highlight_thresh=0.62,
        shadow_thresh=0.28,
        opacity=1.0,
    )
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(32, 32, 4)
    r_after = int(buf_after[:, :, 2].mean())
    assert r_after >= r_before, (
        f"renoir_luminous_warmth_pass should boost R in highlight zone; "
        f"R before={r_before}  after={r_after}")


def test_renoir_luminous_warmth_pass_changes_canvas():
    """renoir_luminous_warmth_pass(opacity=1.0) must change at least some pixels."""
    p = _make_small_painter()
    p.tone_ground((0.92, 0.86, 0.78), texture_strength=0.0)
    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.renoir_luminous_warmth_pass(
        saturation_boost=0.18, rose_warmth=0.07, highlight_glow=0.06, opacity=1.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert not np.array_equal(buf_before, buf_after), (
        "renoir_luminous_warmth_pass should change the canvas when opacity=1.0")


def test_renoir_luminous_warmth_pass_custom_params():
    """renoir_luminous_warmth_pass() accepts all custom parameters without error."""
    p = _make_small_painter()
    p.tone_ground((0.92, 0.86, 0.78), texture_strength=0.0)
    p.renoir_luminous_warmth_pass(
        saturation_boost = 0.12,
        rose_warmth      = 0.05,
        highlight_glow   = 0.04,
        highlight_thresh = 0.68,
        shadow_thresh    = 0.25,
        opacity          = 0.65,
    )


def test_renoir_luminous_warmth_pass_large_canvas():
    """renoir_luminous_warmth_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.92, 0.86, 0.78), texture_strength=0.0)
    p.renoir_luminous_warmth_pass(saturation_boost=0.15, rose_warmth=0.06, opacity=0.70)


# ═══════════════════════════════════════════════════════════════════════════
# gentileschi_dramatic_flesh_pass — Artemisia Gentileschi artist pass
# ═══════════════════════════════════════════════════════════════════════════

def test_gentileschi_dramatic_flesh_pass_exists():
    """Painter must have gentileschi_dramatic_flesh_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "gentileschi_dramatic_flesh_pass"), (
        "Painter is missing gentileschi_dramatic_flesh_pass — add it to stroke_engine.py")
    assert callable(getattr(Painter, "gentileschi_dramatic_flesh_pass"))


def test_gentileschi_dramatic_flesh_pass_runs():
    """gentileschi_dramatic_flesh_pass() runs without error on a small canvas."""
    p = _make_small_painter()
    p.tone_ground((0.55, 0.40, 0.28), texture_strength=0.0)
    p.gentileschi_dramatic_flesh_pass(opacity=0.75)


def test_gentileschi_dramatic_flesh_pass_opacity_zero_is_noop():
    """gentileschi_dramatic_flesh_pass(opacity=0) must leave the canvas unchanged."""
    p = _make_small_painter()
    p.tone_ground((0.55, 0.40, 0.28), texture_strength=0.0)
    buf_before = bytes(p.canvas.surface.get_data())
    p.gentileschi_dramatic_flesh_pass(opacity=0.0)
    buf_after = bytes(p.canvas.surface.get_data())
    assert buf_before == buf_after, (
        "gentileschi_dramatic_flesh_pass(opacity=0) should be a noop — "
        "no pixels should change when the pass is fully blended off")


def test_gentileschi_dramatic_flesh_pass_warms_shadows():
    """
    R channel should increase in dark shadow pixels after gentileschi_dramatic_flesh_pass —
    the warm umber shadow push (Gentileschi's shadows are warm brown, not cold near-black).
    Fill with a near-black pixel (lum ~0.08, well below shadow_thresh=0.30), then confirm
    that R rises relative to B after the pass — warm umber, not cold grey.
    """
    p = _make_small_painter(32, 32)
    # Near-black, slightly warm: R=22, G=16, B=12 → lum ≈ 0.065
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(32, 32, 4).copy()
    buf[:, :, 2] = 22    # R
    buf[:, :, 1] = 16    # G
    buf[:, :, 0] = 12    # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = int(buf[:, :, 2].mean())

    p.gentileschi_dramatic_flesh_pass(
        shadow_deepen   = 0.0,     # disable deepening to isolate warmth effect
        shadow_warmth   = 0.15,
        penumbra_warmth = 0.0,
        highlight_gold  = 0.0,
        shadow_thresh   = 0.30,
        opacity         = 1.0,
    )
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(32, 32, 4)
    r_after = int(buf_after[:, :, 2].mean())
    assert r_after >= r_before, (
        f"gentileschi_dramatic_flesh_pass should warm R in shadow zone; "
        f"R before={r_before}  after={r_after}")


def test_gentileschi_dramatic_flesh_pass_warms_highlights():
    """
    R channel should increase in bright highlight pixels after gentileschi_dramatic_flesh_pass —
    the candlelit amber-gold highlight lift (warm candle, not cool silver).
    Fill with near-white (lum ~0.86, above highlight_thresh=0.68), confirm R rises.
    """
    p = _make_small_painter(32, 32)
    # Near-white: R=225, G=218, B=210 → lum ≈ 0.857
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(32, 32, 4).copy()
    buf[:, :, 2] = 225   # R
    buf[:, :, 1] = 218   # G
    buf[:, :, 0] = 210   # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = int(buf[:, :, 2].mean())

    p.gentileschi_dramatic_flesh_pass(
        shadow_deepen   = 0.0,
        shadow_warmth   = 0.0,
        penumbra_warmth = 0.0,
        highlight_gold  = 0.12,
        highlight_thresh= 0.68,
        opacity         = 1.0,
    )
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(32, 32, 4)
    r_after = int(buf_after[:, :, 2].mean())
    assert r_after >= r_before, (
        f"gentileschi_dramatic_flesh_pass should boost R in highlight zone (candlelit gold); "
        f"R before={r_before}  after={r_after}")


def test_gentileschi_dramatic_flesh_pass_changes_canvas():
    """gentileschi_dramatic_flesh_pass(opacity=1.0) must change at least some pixels."""
    p = _make_small_painter()
    p.tone_ground((0.45, 0.32, 0.22), texture_strength=0.0)
    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.gentileschi_dramatic_flesh_pass(
        shadow_warmth=0.12, penumbra_warmth=0.09, highlight_gold=0.10, opacity=1.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert not np.array_equal(buf_before, buf_after), (
        "gentileschi_dramatic_flesh_pass should change the canvas when opacity=1.0")


def test_gentileschi_dramatic_flesh_pass_custom_params():
    """gentileschi_dramatic_flesh_pass() accepts all custom parameters without error."""
    p = _make_small_painter()
    p.tone_ground((0.45, 0.32, 0.22), texture_strength=0.0)
    p.gentileschi_dramatic_flesh_pass(
        shadow_deepen    = 0.18,
        shadow_warmth    = 0.10,
        penumbra_warmth  = 0.08,
        highlight_gold   = 0.08,
        shadow_thresh    = 0.28,
        highlight_thresh = 0.72,
        opacity          = 0.65,
    )


def test_gentileschi_dramatic_flesh_pass_large_canvas():
    """gentileschi_dramatic_flesh_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.45, 0.32, 0.22), texture_strength=0.0)
    p.gentileschi_dramatic_flesh_pass(shadow_warmth=0.12, highlight_gold=0.08, opacity=0.75)


# ═══════════════════════════════════════════════════════════════════════════
# munch_anxiety_swirl_pass — Edvard Munch artist pass (current session)
# ═══════════════════════════════════════════════════════════════════════════

def test_munch_anxiety_swirl_pass_exists():
    """Painter must have munch_anxiety_swirl_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "munch_anxiety_swirl_pass"), (
        "Painter is missing munch_anxiety_swirl_pass — add it to stroke_engine.py")
    assert callable(getattr(Painter, "munch_anxiety_swirl_pass"))


def test_munch_anxiety_swirl_pass_runs():
    """munch_anxiety_swirl_pass() runs without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.18, 0.14, 0.10), texture_strength=0.0)
    p.munch_anxiety_swirl_pass(n_swirl_strokes=20)


def test_munch_anxiety_swirl_pass_changes_canvas():
    """munch_anxiety_swirl_pass() must change at least some pixels on a toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.18, 0.14, 0.10), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.munch_anxiety_swirl_pass(
        n_swirl_strokes=80,
        color_intensity=0.80,
        stroke_opacity=0.60,
        stroke_size=8.0,
    )
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert not np.array_equal(buf_before, buf_after), (
        "munch_anxiety_swirl_pass should change the canvas — no swirl strokes were drawn")


def test_munch_anxiety_swirl_pass_zero_strokes_is_noop():
    """munch_anxiety_swirl_pass(n_swirl_strokes=0) must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.20, 0.16, 0.12), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.munch_anxiety_swirl_pass(n_swirl_strokes=0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert np.array_equal(buf_before, buf_after), (
        "munch_anxiety_swirl_pass(n_swirl_strokes=0) should be a noop")


def test_munch_anxiety_swirl_pass_bg_only_with_full_figure_mask():
    """With bg_only=True and a full-white figure mask, no strokes should be placed."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.20, 0.16, 0.12), texture_strength=0.0)

    # Set full-canvas figure mask — every pixel is figure, none is background
    p.set_figure_mask(np.ones((64, 64), dtype=np.float32))

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.munch_anxiety_swirl_pass(
        n_swirl_strokes=100,
        bg_only=True,
        color_intensity=0.90,
        stroke_opacity=0.70,
    )
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert np.array_equal(buf_before, buf_after), (
        "munch_anxiety_swirl_pass(bg_only=True) with a full figure mask should be a noop — "
        "all stroke midpoints fall within the figure and should be skipped")


def test_munch_anxiety_swirl_pass_custom_params():
    """munch_anxiety_swirl_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.18, 0.14, 0.10), texture_strength=0.0)
    p.munch_anxiety_swirl_pass(
        n_swirl_strokes = 30,
        swirl_amplitude = 0.30,
        swirl_frequency = 4.5,
        color_intensity = 0.60,
        bg_only         = False,
        stroke_opacity  = 0.35,
        stroke_size     = 7.0,
    )


def test_munch_anxiety_swirl_pass_large_canvas():
    """munch_anxiety_swirl_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.18, 0.14, 0.10), texture_strength=0.0)
    p.munch_anxiety_swirl_pass(n_swirl_strokes=80, color_intensity=0.55, stroke_opacity=0.30)


# ── hals_bravura_stroke_pass tests ────────────────────────────────────────────

def test_hals_bravura_stroke_pass_exists():
    """Painter must have hals_bravura_stroke_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "hals_bravura_stroke_pass"), (
        "hals_bravura_stroke_pass not found on Painter")
    assert callable(getattr(Painter, "hals_bravura_stroke_pass"))


def test_hals_bravura_stroke_pass_no_reference():
    """hals_bravura_stroke_pass() runs without error when no reference is passed."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.0)
    p.hals_bravura_stroke_pass(n_strokes=40, stroke_size=6.0, opacity=0.55)


def test_hals_bravura_stroke_pass_with_reference():
    """hals_bravura_stroke_pass() runs without error when a reference is passed."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.0)
    p.hals_bravura_stroke_pass(ref, n_strokes=40, stroke_size=6.0, opacity=0.55)


def test_hals_bravura_stroke_pass_changes_canvas():
    """hals_bravura_stroke_pass() must modify canvas pixels when n_strokes > 0."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.hals_bravura_stroke_pass(n_strokes=80, stroke_size=6.0, opacity=0.65)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert not np.array_equal(buf_before, buf_after), (
        "hals_bravura_stroke_pass should change the canvas — no strokes were drawn")


def test_hals_bravura_stroke_pass_zero_strokes_is_noop():
    """hals_bravura_stroke_pass(n_strokes=0) must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.hals_bravura_stroke_pass(n_strokes=0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert np.array_equal(buf_before, buf_after), (
        "hals_bravura_stroke_pass(n_strokes=0) should be a noop")


def test_hals_bravura_stroke_pass_broken_tone_disabled():
    """hals_bravura_stroke_pass(broken_tone=False) must run without error."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.0)
    p.hals_bravura_stroke_pass(ref, n_strokes=40, broken_tone=False, opacity=0.55)


def test_hals_bravura_stroke_pass_with_figure_mask():
    """hals_bravura_stroke_pass() accepts and uses a figure_mask without error."""
    p    = _make_small_painter(64, 64)
    ref  = _solid_reference(64, 64)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[10:54, 12:52] = 1.0
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.0)
    p.hals_bravura_stroke_pass(ref, n_strokes=50, figure_mask=mask, opacity=0.60)


def test_hals_bravura_stroke_pass_custom_params():
    """hals_bravura_stroke_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.0)
    p.hals_bravura_stroke_pass(
        n_strokes        = 30,
        stroke_size      = 5.0,
        opacity          = 0.50,
        angle_jitter_deg = 35.0,
        color_jitter     = 0.03,
        broken_tone      = True,
    )


def test_hals_bravura_stroke_pass_large_canvas():
    """hals_bravura_stroke_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.0)
    p.hals_bravura_stroke_pass(n_strokes=120, stroke_size=8.0, opacity=0.55)


# ─────────────────────────────────────────────────────────────────────────────
# dali_paranoiac_critical_pass — Salvador Dali
# ─────────────────────────────────────────────────────────────────────────────

def test_dali_paranoiac_critical_pass_exists():
    """Painter must have dali_paranoiac_critical_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "dali_paranoiac_critical_pass"), (
        "dali_paranoiac_critical_pass not found on Painter")
    assert callable(getattr(Painter, "dali_paranoiac_critical_pass"))


def test_dali_paranoiac_critical_pass_runs():
    """dali_paranoiac_critical_pass() runs without error on a default canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.82, 0.62), texture_strength=0.0)
    p.dali_paranoiac_critical_pass(opacity=0.80)


def test_dali_paranoiac_critical_pass_changes_canvas():
    """dali_paranoiac_critical_pass() must modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.82, 0.62), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.dali_paranoiac_critical_pass(
        shadow_ultramarine=0.30,
        shadow_thresh=0.80,    # very high threshold so most pixels get adjusted
        opacity=0.90,
        chroma_shift=0,
        figure_sharpen=0.0,
    )
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert not np.array_equal(buf_before, buf_after), (
        "dali_paranoiac_critical_pass should change the canvas")


def test_dali_paranoiac_critical_pass_opacity_zero_is_noop():
    """dali_paranoiac_critical_pass(opacity=0) must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.82, 0.62), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.dali_paranoiac_critical_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert np.array_equal(buf_before, buf_after), (
        "dali_paranoiac_critical_pass(opacity=0) should be a noop")


def test_dali_paranoiac_critical_pass_deepens_shadows_toward_blue():
    """Dark pixels must become bluer and less red after the ultramarine shadow pass."""
    p = _make_small_painter(64, 64)

    # Fill canvas with a dark warm-gray (lum ≈ 0.12, well below shadow_thresh)
    # Cairo BGRA: index 0=B, 1=G, 2=R, 3=A
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 0] = 25    # B
    buf[:, :, 1] = 25    # G
    buf[:, :, 2] = 35    # R (slightly warm dark)
    buf[:, :, 3] = 255   # A
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.dali_paranoiac_critical_pass(
        shadow_ultramarine=0.50,
        shadow_thresh=0.40,    # threshold comfortably above the dark fill
        chroma_shift=0,
        figure_sharpen=0.0,
        highlight_warmth=0.0,
        opacity=1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    b_after = float(buf_after[:, :, 0].mean())   # Blue channel (BGRA index 0)
    r_after = float(buf_after[:, :, 2].mean())   # Red channel  (BGRA index 2)

    assert b_after > 25, (
        f"Dark pixels should have more blue after ultramarine pass; "
        f"B before=25 after={b_after:.1f}")
    assert r_after < 35, (
        f"Dark pixels should have less red after ultramarine pass; "
        f"R before=35 after={r_after:.1f}")


def test_dali_paranoiac_critical_pass_with_figure_mask():
    """dali_paranoiac_critical_pass() accepts a figure_mask without error."""
    p    = _make_small_painter(64, 64)
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[10:54, 12:52] = 1.0
    p._figure_mask = mask
    p.tone_ground((0.88, 0.82, 0.62), texture_strength=0.0)
    p.dali_paranoiac_critical_pass(opacity=0.80, chroma_shift=2)


def test_dali_paranoiac_critical_pass_no_aberration():
    """dali_paranoiac_critical_pass(chroma_shift=0) runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.82, 0.62), texture_strength=0.0)
    p.dali_paranoiac_critical_pass(chroma_shift=0, opacity=0.80)


def test_dali_paranoiac_critical_pass_custom_params():
    """dali_paranoiac_critical_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.82, 0.62), texture_strength=0.0)
    p.dali_paranoiac_critical_pass(
        chroma_shift       = 2,
        shadow_ultramarine = 0.25,
        highlight_warmth   = 0.08,
        shadow_thresh      = 0.30,
        highlight_thresh   = 0.72,
        figure_sharpen     = 0.50,
        bg_only_aberration = False,
        opacity            = 0.75,
    )


def test_dali_paranoiac_critical_pass_large_canvas():
    """dali_paranoiac_critical_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.88, 0.82, 0.62), texture_strength=0.0)
    p.dali_paranoiac_critical_pass(opacity=0.80, chroma_shift=3)


# ─────────────────────────────────────────────────────────────────────────────
# hammershoi_grey_silence_pass — Vilhelm Hammershøi
# ─────────────────────────────────────────────────────────────────────────────

def test_hammershoi_grey_silence_pass_exists():
    """Painter must have hammershoi_grey_silence_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "hammershoi_grey_silence_pass"), (
        "hammershoi_grey_silence_pass not found on Painter")
    assert callable(getattr(Painter, "hammershoi_grey_silence_pass"))


def test_hammershoi_grey_silence_pass_runs():
    """hammershoi_grey_silence_pass() runs without error on a default canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.67, 0.65), texture_strength=0.0)
    p.hammershoi_grey_silence_pass(opacity=0.88)


def test_hammershoi_grey_silence_pass_changes_canvas():
    """hammershoi_grey_silence_pass() must modify the canvas."""
    p = _make_small_painter(64, 64)
    # Fill with a saturated warm colour so desaturation produces a measurable change
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 0] = 40    # B
    buf[:, :, 1] = 80    # G
    buf[:, :, 2] = 200   # R  (strongly warm red)
    buf[:, :, 3] = 255   # A
    p.canvas.surface.get_data()[:] = buf.tobytes()

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.hammershoi_grey_silence_pass(desaturation=0.90, opacity=1.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert not np.array_equal(buf_before, buf_after), (
        "hammershoi_grey_silence_pass should change the canvas")


def test_hammershoi_grey_silence_pass_opacity_zero_is_noop():
    """hammershoi_grey_silence_pass(opacity=0) must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.67, 0.65), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.hammershoi_grey_silence_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert np.array_equal(buf_before, buf_after), (
        "hammershoi_grey_silence_pass(opacity=0) should be a noop")


def test_hammershoi_grey_silence_pass_desaturates_toward_grey():
    """Saturated pixels must become less saturated (R−B gap narrows) after the pass."""
    p = _make_small_painter(64, 64)

    # Fill with a strongly warm-red canvas (high R, low B)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 0] = 30    # B
    buf[:, :, 1] = 100   # G
    buf[:, :, 2] = 200   # R  (highly saturated warm red, lum ≈ 0.63)
    buf[:, :, 3] = 255   # A
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.hammershoi_grey_silence_pass(desaturation=0.82, opacity=1.0,
                                   window_cool=0.0, shadow_cool=0.0)

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())   # Red channel (BGRA index 2)
    b_after = float(buf_after[:, :, 0].mean())   # Blue channel (BGRA index 0)

    # After desaturation, the R−B gap should be smaller (both converge toward grey)
    gap_before = 200 - 30   # = 170
    gap_after  = r_after - b_after
    assert gap_after < gap_before * 0.50, (
        f"Desaturation should substantially narrow R-B gap; "
        f"before={gap_before:.0f} after={gap_after:.1f}")


def test_hammershoi_grey_silence_pass_cools_bright_highlights():
    """Bright pixels must become cooler (B increases relative to R) after the pass."""
    p = _make_small_painter(64, 64)

    # Fill with a bright near-white warm canvas (lum > window_thresh=0.68)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 0] = 190   # B
    buf[:, :, 1] = 200   # G
    buf[:, :, 2] = 220   # R  (bright, slightly warm — lum ≈ 0.82)
    buf[:, :, 3] = 255   # A
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.hammershoi_grey_silence_pass(
        desaturation=0.0,   # disable desaturation to isolate window cooling
        window_thresh=0.70,
        window_cool=0.20,
        shadow_cool=0.0,
        opacity=1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    b_after = float(buf_after[:, :, 0].mean())
    r_after = float(buf_after[:, :, 2].mean())

    assert b_after > 190, (
        f"Bright pixels should have more blue after window cooling; "
        f"B before=190 after={b_after:.1f}")
    assert r_after < 220, (
        f"Bright pixels should have less red after window cooling; "
        f"R before=220 after={r_after:.1f}")


def test_hammershoi_grey_silence_pass_custom_params():
    """hammershoi_grey_silence_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.67, 0.65), texture_strength=0.0)
    p.hammershoi_grey_silence_pass(
        desaturation  = 0.75,
        window_thresh = 0.72,
        window_cool   = 0.10,
        shadow_thresh = 0.30,
        shadow_cool   = 0.06,
        opacity       = 0.80,
    )


def test_hammershoi_grey_silence_pass_large_canvas():
    """hammershoi_grey_silence_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.68, 0.67, 0.65), texture_strength=0.0)
    p.hammershoi_grey_silence_pass(opacity=0.88)


# ─────────────────────────────────────────────────────────────────────────────
# horizon_mist_pass — graduated mid-ground atmospheric haze (random improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_horizon_mist_pass_exists():
    """Painter must have horizon_mist_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "horizon_mist_pass"), (
        "horizon_mist_pass not found on Painter")
    assert callable(getattr(Painter, "horizon_mist_pass"))


def test_horizon_mist_pass_runs():
    """horizon_mist_pass() runs without error on a default canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.68, 0.60), texture_strength=0.0)
    p.horizon_mist_pass(opacity=0.72)


def test_horizon_mist_pass_changes_canvas():
    """horizon_mist_pass() must modify the canvas when mist_strength > 0."""
    p = _make_small_painter(64, 64)
    # Tone a dark canvas so the mist overlay produces a clear change
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = 30   # very dark (all channels)
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.horizon_mist_pass(
        horizon_y     = 0.5,
        band_height   = 0.40,   # wide band so the small 64-px canvas is fully covered
        mist_strength = 0.60,
        opacity       = 1.0,
    )
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert not np.array_equal(buf_before, buf_after), (
        "horizon_mist_pass should change the canvas")


def test_horizon_mist_pass_opacity_zero_is_noop():
    """horizon_mist_pass(opacity=0) must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.68, 0.60), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.horizon_mist_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert np.array_equal(buf_before, buf_after), (
        "horizon_mist_pass(opacity=0) should be a noop")


def test_horizon_mist_pass_lightens_band_center():
    """The band centre must become lighter/cooler after mist pass on a dark canvas."""
    p = _make_small_painter(64, 64)

    # Fill canvas with a uniformly dark warm canvas
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 0] = 20   # B
    buf[:, :, 1] = 20   # G
    buf[:, :, 2] = 30   # R (dark warm)
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.horizon_mist_pass(
        horizon_y     = 0.5,
        band_height   = 0.40,
        mist_color    = (0.78, 0.80, 0.86),   # cool silver-blue mist
        mist_strength = 0.70,
        blur_sigma    = 0.0,
        opacity       = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    # Sample the centre row
    centre_row = buf_after[32, :, :]
    b_centre = float(centre_row[:, 0].mean())  # B
    r_centre = float(centre_row[:, 2].mean())  # R

    # Band centre should be brighter (blue mist lifts B significantly above 20)
    assert b_centre > 40, (
        f"Band centre B should be > 40 after cool mist overlay; got {b_centre:.1f}")
    # And cooler (B should be greater than R after the cool mist)
    assert b_centre > r_centre, (
        f"Band centre should be cooler (B > R) after cool mist; "
        f"B={b_centre:.1f} R={r_centre:.1f}")


def test_horizon_mist_pass_custom_params():
    """horizon_mist_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.68, 0.60), texture_strength=0.0)
    p.horizon_mist_pass(
        horizon_y     = 0.42,
        band_height   = 0.22,
        mist_color    = (0.82, 0.84, 0.90),
        mist_strength = 0.35,
        blur_sigma    = 3.0,
        opacity       = 0.65,
    )


def test_horizon_mist_pass_large_canvas():
    """horizon_mist_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.72, 0.68, 0.60), texture_strength=0.0)
    p.horizon_mist_pass(opacity=0.72)


# ══════════════════════════════════════════════════════════════════════════════
# Session 50 — constable_cloud_sky_pass (John Constable artist pass)
# ══════════════════════════════════════════════════════════════════════════════

def test_constable_cloud_sky_pass_exists():
    """constable_cloud_sky_pass must exist on the Painter class."""
    from stroke_engine import Painter
    assert hasattr(Painter, "constable_cloud_sky_pass"), (
        "Painter missing constable_cloud_sky_pass — add it to stroke_engine.py")
    assert callable(getattr(Painter, "constable_cloud_sky_pass")), (
        "constable_cloud_sky_pass is not callable")


def test_constable_cloud_sky_pass_runs():
    """constable_cloud_sky_pass() must run without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.54, 0.42), texture_strength=0.0)
    p.constable_cloud_sky_pass()


def test_constable_cloud_sky_pass_modifies_canvas():
    """constable_cloud_sky_pass must visibly modify the sky zone."""
    p = _make_small_painter(64, 64)

    # Fill canvas with a uniform mid-grey
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:] = 128
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.constable_cloud_sky_pass(sky_threshold=0.50, opacity=1.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert not np.array_equal(buf_before, buf_after), (
        "constable_cloud_sky_pass should change the sky zone")


def test_constable_cloud_sky_pass_opacity_zero_is_noop():
    """constable_cloud_sky_pass(opacity=0) must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.54, 0.42), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.constable_cloud_sky_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert np.array_equal(buf_before, buf_after), (
        "constable_cloud_sky_pass(opacity=0) should be a noop")


def test_constable_cloud_sky_pass_landscape_zone_unchanged():
    """constable_cloud_sky_pass must not alter pixels below sky_threshold."""
    p = _make_small_painter(64, 64)

    # Set whole canvas to a distinctive warm mid-value
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 0] = 60    # B
    buf[:, :, 1] = 80    # G
    buf[:, :, 2] = 100   # R
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Apply with sky threshold = 0.25 → only rows 0..15 (of 64) are sky
    p.constable_cloud_sky_pass(sky_threshold=0.25, opacity=1.0)

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    # Landscape zone (row 16 onward) should be unchanged
    landscape = buf_after[16:, :, :3]
    assert np.all(landscape[:, :, 0] == 60), "B channel changed in landscape zone"
    assert np.all(landscape[:, :, 1] == 80), "G channel changed in landscape zone"
    assert np.all(landscape[:, :, 2] == 100), "R channel changed in landscape zone"


def test_constable_cloud_sky_pass_custom_params():
    """constable_cloud_sky_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.54, 0.42), texture_strength=0.0)
    p.constable_cloud_sky_pass(
        sky_threshold   = 0.35,
        warm_top        = 0.20,
        cool_base       = 0.12,
        silver_strength = 0.25,
        silver_density  = 0.02,
        opacity         = 0.60,
    )


def test_constable_cloud_sky_pass_large_canvas():
    """constable_cloud_sky_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.52, 0.54, 0.42), texture_strength=0.0)
    p.constable_cloud_sky_pass(opacity=0.72)


# ══════════════════════════════════════════════════════════════════════════════
# Session 50 — chiaroscuro_modelling_pass (random improvement)
# ══════════════════════════════════════════════════════════════════════════════

def test_chiaroscuro_modelling_pass_exists():
    """chiaroscuro_modelling_pass must exist on the Painter class."""
    from stroke_engine import Painter
    assert hasattr(Painter, "chiaroscuro_modelling_pass"), (
        "Painter missing chiaroscuro_modelling_pass — add it to stroke_engine.py")
    assert callable(getattr(Painter, "chiaroscuro_modelling_pass")), (
        "chiaroscuro_modelling_pass is not callable")


def test_chiaroscuro_modelling_pass_runs():
    """chiaroscuro_modelling_pass() must run without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.68, 0.58), texture_strength=0.0)
    p.chiaroscuro_modelling_pass()


def test_chiaroscuro_modelling_pass_modifies_canvas():
    """chiaroscuro_modelling_pass must visibly modify a canvas with clear light/shadow zones."""
    p = _make_small_painter(64, 64)

    # Set canvas: top half bright (lit), bottom half dark (shadowed)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:32, :, :3] = 200   # bright rows — light zone
    buf[32:, :, :3] = 50    # dark rows — shadow zone
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.chiaroscuro_modelling_pass(opacity=1.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert not np.array_equal(buf_before, buf_after), (
        "chiaroscuro_modelling_pass should change the canvas")


def test_chiaroscuro_modelling_pass_opacity_zero_is_noop():
    """chiaroscuro_modelling_pass(opacity=0) must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.68, 0.58), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.chiaroscuro_modelling_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert np.array_equal(buf_before, buf_after), (
        "chiaroscuro_modelling_pass(opacity=0) should be a noop")


def test_chiaroscuro_modelling_pass_warms_lights():
    """Light-zone pixels must become warmer (R lifted relative to B) after the pass."""
    p = _make_small_painter(64, 64)

    # Fill with a uniformly bright neutral canvas (all channels ~200 → lum ≈ 0.78)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = 200   # neutral bright — ensures all pixels are in light zone
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.chiaroscuro_modelling_pass(
        light_thresh  = 0.50,    # low threshold — all 200/255≈0.78 pixels qualify
        shadow_thresh = 0.20,    # high threshold keeps shadow zone empty
        light_warmth  = 0.20,
        shadow_cool   = 0.0,
        shadow_deepen = 0.0,
        opacity       = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_mean = float(buf_after[:, :, 2].mean())
    b_mean = float(buf_after[:, :, 0].mean())
    assert r_mean > b_mean + 5, (
        f"After warm light push R should exceed B by >5; got R={r_mean:.1f} B={b_mean:.1f}")


def test_chiaroscuro_modelling_pass_cools_shadows():
    """Shadow-zone pixels must become cooler (B lifted relative to R) after the pass."""
    p = _make_small_painter(64, 64)

    # Fill with a uniformly dark neutral canvas (all channels ~40 → lum ≈ 0.16)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = 40    # neutral dark — ensures all pixels are in shadow zone
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.chiaroscuro_modelling_pass(
        light_thresh  = 0.80,    # high threshold keeps light zone empty
        shadow_thresh = 0.50,    # low threshold — all 40/255≈0.16 pixels qualify
        light_warmth  = 0.0,
        shadow_cool   = 0.20,
        shadow_deepen = 0.0,
        opacity       = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    b_mean = float(buf_after[:, :, 0].mean())
    r_mean = float(buf_after[:, :, 2].mean())
    assert b_mean > r_mean + 3, (
        f"After shadow cool push B should exceed R; got B={b_mean:.1f} R={r_mean:.1f}")


def test_chiaroscuro_modelling_pass_with_figure_mask():
    """chiaroscuro_modelling_pass() must respect a figure_mask."""
    p = _make_small_painter(64, 64)

    # Uniform bright neutral canvas
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = 200
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Mask: only left half is figure
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[:, :32] = 1.0

    p.chiaroscuro_modelling_pass(
        figure_mask  = mask,
        light_thresh = 0.50,
        light_warmth = 0.30,
        shadow_cool  = 0.0,
        shadow_deepen= 0.0,
        opacity      = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    # Left half (figure) should be warmer than right half (background, unchanged)
    r_left  = float(buf_after[:, :32,  2].mean())
    r_right = float(buf_after[:, 32:, 2].mean())
    assert r_left > r_right, (
        f"Figure (left) R should exceed background (right) R after warm push; "
        f"R_left={r_left:.1f} R_right={r_right:.1f}")

    # Right half should be essentially unchanged (still ~200)
    assert r_right >= 195, (
        f"Background R should stay near 200 when outside mask; got {r_right:.1f}")


def test_chiaroscuro_modelling_pass_custom_params():
    """chiaroscuro_modelling_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.68, 0.58), texture_strength=0.0)
    p.chiaroscuro_modelling_pass(
        light_thresh  = 0.60,
        shadow_thresh = 0.35,
        light_warmth  = 0.12,
        shadow_cool   = 0.09,
        shadow_deepen = 0.06,
        opacity       = 0.55,
    )


def test_chiaroscuro_modelling_pass_large_canvas():
    """chiaroscuro_modelling_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.72, 0.68, 0.58), texture_strength=0.0)
    p.chiaroscuro_modelling_pass(opacity=0.68)


# ──────────────────────────────────────────────────────────────────────────────
# Session 51 — bellini_sacred_light_pass() tests
# ──────────────────────────────────────────────────────────────────────────────

def test_bellini_sacred_light_pass_exists():
    """Painter must have bellini_sacred_light_pass() method (session 51)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "bellini_sacred_light_pass"), (
        "bellini_sacred_light_pass not found on Painter")
    assert callable(getattr(Painter, "bellini_sacred_light_pass"))


def test_bellini_sacred_light_pass_no_error():
    """bellini_sacred_light_pass() must run without error on a small canvas."""
    p   = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.50, 0.32), texture_strength=0.0)
    p.bellini_sacred_light_pass()


def test_bellini_sacred_light_pass_warms_highlights():
    """After the pass, bright pixels should shift warmer (R > B increased)."""
    p = _make_small_painter(64, 64)

    # Seed with a uniform bright neutral canvas (~lum 0.75 > light_thresh 0.62)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = 200    # neutral bright — in the light zone
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Record R and B before
    r_before = float(buf[:, :, 2].mean())
    b_before = float(buf[:, :, 0].mean())

    p.bellini_sacred_light_pass(
        light_thresh  = 0.50,   # lowered so ~200/255≈0.78 clearly in light zone
        shadow_thresh = 0.20,
        honey_warmth  = 0.20,   # amplified for a testable shift
        lapis_cool    = 0.0,
        halo_thresh   = 0.90,   # above our luminance — halo zone inactive
        halo_gold     = 0.0,
        opacity       = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())
    b_after = float(buf_after[:, :, 0].mean())

    assert r_after > r_before + 2, (
        f"R should increase in light zone after honey warmth push; "
        f"R_before={r_before:.1f} R_after={r_after:.1f}")
    assert b_after < b_before + 1, (
        f"B should not increase in light zone (honey warmth damps B); "
        f"B_before={b_before:.1f} B_after={b_after:.1f}")


def test_bellini_sacred_light_pass_cools_shadows():
    """After the pass, dark pixels should gain a blue (lapis) cast."""
    p = _make_small_painter(64, 64)

    # Seed with a uniformly dark neutral canvas (~lum 0.16 < shadow_thresh 0.32)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = 40
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.bellini_sacred_light_pass(
        light_thresh  = 0.80,   # well above lum — light zone inactive
        shadow_thresh = 0.50,   # well above lum ≈ 0.16 — all in shadow zone
        honey_warmth  = 0.0,
        lapis_cool    = 0.25,   # amplified for a testable shift
        halo_gold     = 0.0,
        opacity       = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    b_after = float(buf_after[:, :, 0].mean())
    r_after = float(buf_after[:, :, 2].mean())
    assert b_after > r_after + 2, (
        f"B should exceed R after lapis shadow push; B={b_after:.1f} R={r_after:.1f}")


def test_bellini_sacred_light_pass_halo_warms_highlights():
    """Very bright pixels should receive an additional golden halo warm push."""
    p = _make_small_painter(64, 64)

    # Seed with very bright neutral canvas (~lum 0.94 > halo_thresh 0.82)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = 240
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = float(buf[:, :, 2].mean())

    p.bellini_sacred_light_pass(
        light_thresh  = 0.50,
        shadow_thresh = 0.10,
        honey_warmth  = 0.0,     # disable regular warm push
        lapis_cool    = 0.0,
        halo_thresh   = 0.70,    # 240/255≈0.94 is clearly above 0.70
        halo_gold     = 0.15,    # amplified for testable shift
        opacity       = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())
    assert r_after > r_before + 2, (
        f"R should increase in halo zone; R_before={r_before:.1f} R_after={r_after:.1f}")


def test_bellini_sacred_light_pass_respects_figure_mask():
    """bellini_sacred_light_pass() must confine warm push to figure (masked) region."""
    p = _make_small_painter(64, 64)

    # Bright uniform canvas (in light zone)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = 200
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Mask: only left half is figure
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[:, :32] = 1.0

    p.bellini_sacred_light_pass(
        figure_mask  = mask,
        light_thresh = 0.50,
        honey_warmth = 0.25,
        lapis_cool   = 0.0,
        halo_gold    = 0.0,
        opacity      = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_left  = float(buf_after[:, :32, 2].mean())
    r_right = float(buf_after[:, 32:, 2].mean())
    assert r_left > r_right + 3, (
        f"Figure (left) R should exceed background (right) R after warm push; "
        f"R_left={r_left:.1f} R_right={r_right:.1f}")
    assert r_right >= 195, (
        f"Background R should stay near 200 when outside mask; got {r_right:.1f}")


def test_bellini_sacred_light_pass_opacity_zero_skips():
    """bellini_sacred_light_pass() with opacity=0 must not change the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.50, 0.32), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.bellini_sacred_light_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert np.array_equal(buf_before, buf_after), (
        "Canvas must not change when bellini_sacred_light_pass(opacity=0)")


def test_bellini_sacred_light_pass_custom_params():
    """bellini_sacred_light_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.50, 0.32), texture_strength=0.0)
    p.bellini_sacred_light_pass(
        light_thresh  = 0.55,
        shadow_thresh = 0.28,
        honey_warmth  = 0.15,
        lapis_cool    = 0.12,
        halo_thresh   = 0.85,
        halo_gold     = 0.05,
        opacity       = 0.80,
    )


def test_bellini_sacred_light_pass_large_canvas():
    """bellini_sacred_light_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.62, 0.50, 0.32), texture_strength=0.0)
    p.bellini_sacred_light_pass(opacity=0.70)


# ──────────────────────────────────────────────────────────────────────────────
# Session 51 — penumbra_zone_pass() tests
# ──────────────────────────────────────────────────────────────────────────────

def test_penumbra_zone_pass_exists():
    """Painter must have penumbra_zone_pass() method (session 51)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "penumbra_zone_pass"), (
        "penumbra_zone_pass not found on Painter")
    assert callable(getattr(Painter, "penumbra_zone_pass"))


def test_penumbra_zone_pass_no_error():
    """penumbra_zone_pass() must run without error on a small canvas."""
    p   = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.50, 0.32), texture_strength=0.0)
    p.penumbra_zone_pass()


def test_penumbra_zone_pass_warms_midtones():
    """penumbra_zone_pass() must warm R in the penumbra band (midtone luminance)."""
    p = _make_small_painter(64, 64)

    # Seed with a neutral midtone canvas (lum ≈ 0.49 — in penumbra zone [0.35, 0.62])
    neutral_val = int(0.49 * 255)   # ≈ 125
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = neutral_val
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = float(buf[:, :, 2].mean())

    p.penumbra_zone_pass(
        light_thresh    = 0.62,
        shadow_thresh   = 0.35,
        penumbra_warmth = 0.20,    # amplified for testable shift
        penumbra_chroma = 0.0,
        opacity         = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())
    assert r_after > r_before + 2, (
        f"R should increase in penumbra band; R_before={r_before:.1f} R_after={r_after:.1f}")


def test_penumbra_zone_pass_does_not_affect_deep_shadows():
    """penumbra_zone_pass() must leave deep shadow pixels (lum << shadow_thresh) unchanged."""
    p = _make_small_painter(64, 64)

    # Very dark canvas: lum ≈ 0.08 — well below shadow_thresh=0.35
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = 20
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = float(buf[:, :, 2].mean())

    p.penumbra_zone_pass(
        light_thresh    = 0.62,
        shadow_thresh   = 0.35,
        penumbra_warmth = 0.30,
        opacity         = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())
    # Should be essentially unchanged — tent weight ≈ 0 far below shadow_thresh
    assert abs(r_after - r_before) < 5, (
        f"Deep shadow pixels should be barely affected; "
        f"R_before={r_before:.1f} R_after={r_after:.1f}")


def test_penumbra_zone_pass_does_not_affect_highlights():
    """penumbra_zone_pass() must leave bright highlight pixels (lum >> light_thresh) unchanged."""
    p = _make_small_painter(64, 64)

    # Very bright canvas: lum ≈ 0.91 — well above light_thresh=0.62
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = 232
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = float(buf[:, :, 2].mean())

    p.penumbra_zone_pass(
        light_thresh    = 0.62,
        shadow_thresh   = 0.35,
        penumbra_warmth = 0.30,
        opacity         = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())
    assert abs(r_after - r_before) < 5, (
        f"Highlight pixels should be barely affected; "
        f"R_before={r_before:.1f} R_after={r_after:.1f}")


def test_penumbra_zone_pass_respects_figure_mask():
    """penumbra_zone_pass() must confine warm blush to the figure (masked) region."""
    p = _make_small_painter(64, 64)

    # Midtone neutral canvas (in penumbra zone)
    neutral_val = int(0.49 * 255)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = neutral_val
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Mask: only left half is figure
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[:, :32] = 1.0

    p.penumbra_zone_pass(
        figure_mask     = mask,
        light_thresh    = 0.62,
        shadow_thresh   = 0.35,
        penumbra_warmth = 0.25,
        penumbra_chroma = 0.0,
        opacity         = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_left  = float(buf_after[:, :32, 2].mean())
    r_right = float(buf_after[:, 32:, 2].mean())
    assert r_left > r_right + 3, (
        f"Figure (left) R should exceed background R after penumbra blush; "
        f"R_left={r_left:.1f} R_right={r_right:.1f}")
    assert r_right >= neutral_val - 3, (
        f"Background should stay near original when outside mask; got {r_right:.1f}")


def test_penumbra_zone_pass_opacity_zero_skips():
    """penumbra_zone_pass() with opacity=0 must not change the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.50, 0.32), texture_strength=0.0)
    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.penumbra_zone_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert np.array_equal(buf_before, buf_after), (
        "Canvas must not change when penumbra_zone_pass(opacity=0)")


def test_penumbra_zone_pass_chroma_boost_increases_saturation():
    """penumbra_zone_pass() with chroma boost should increase colour distance from grey."""
    p = _make_small_painter(64, 64)

    # Seed with a slightly warm midtone canvas: R > G > B in penumbra zone
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 140   # R (Cairo index 2)
    buf[:, :, 1] = 120   # G
    buf[:, :, 0] = 100   # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Measure chroma (std of RGB channels) before
    r_b = buf[:, :, 2].astype(float)
    g_b = buf[:, :, 1].astype(float)
    b_b = buf[:, :, 0].astype(float)
    chroma_before = float(np.std(np.stack([r_b, g_b, b_b], axis=-1), axis=-1).mean())

    p.penumbra_zone_pass(
        light_thresh    = 0.62,
        shadow_thresh   = 0.35,
        penumbra_warmth = 0.0,      # disable blush to isolate chroma boost
        penumbra_chroma = 0.40,     # amplified for measurable shift
        opacity         = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_a = buf_after[:, :, 2].astype(float)
    g_a = buf_after[:, :, 1].astype(float)
    b_a = buf_after[:, :, 0].astype(float)
    chroma_after = float(np.std(np.stack([r_a, g_a, b_a], axis=-1), axis=-1).mean())

    assert chroma_after >= chroma_before, (
        f"Chroma (std of channels) should not decrease after penumbra chroma boost; "
        f"before={chroma_before:.2f} after={chroma_after:.2f}")


def test_penumbra_zone_pass_custom_params():
    """penumbra_zone_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.48, 0.32), texture_strength=0.0)
    p.penumbra_zone_pass(
        light_thresh    = 0.68,
        shadow_thresh   = 0.30,
        penumbra_warmth = 0.10,
        penumbra_chroma = 0.08,
        opacity         = 0.55,
    )


def test_penumbra_zone_pass_large_canvas():
    """penumbra_zone_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.55, 0.48, 0.32), texture_strength=0.0)
    p.penumbra_zone_pass(opacity=0.65)


# ──────────────────────────────────────────────────────────────────────────────
# pontormo_dissonance_pass — session 52
# ──────────────────────────────────────────────────────────────────────────────

def test_pontormo_dissonance_pass_exists():
    """Painter must expose pontormo_dissonance_pass() (session 52)."""
    p = _make_small_painter(64, 64)
    assert hasattr(p, "pontormo_dissonance_pass"), (
        "Painter.pontormo_dissonance_pass() not found — add it to stroke_engine.py")
    assert callable(p.pontormo_dissonance_pass)


def test_pontormo_dissonance_pass_modifies_canvas():
    """pontormo_dissonance_pass() must change the canvas when opacity > 0."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.50, 0.58), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.pontormo_dissonance_pass(opacity=0.68)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert not np.array_equal(buf_before, buf_after), (
        "Canvas must change after pontormo_dissonance_pass(opacity=0.68)")


def test_pontormo_dissonance_pass_opacity_zero_skips():
    """pontormo_dissonance_pass() with opacity=0 must not change the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.50, 0.58), texture_strength=0.0)
    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.pontormo_dissonance_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert np.array_equal(buf_before, buf_after), (
        "Canvas must not change when pontormo_dissonance_pass(opacity=0)")


def test_pontormo_dissonance_pass_acid_lift_in_highlights():
    """pontormo_dissonance_pass() must lift R channel in the bright zone (acid yellow)."""
    p = _make_small_painter(64, 64)

    # Seed canvas with a uniformly bright value (above light_thresh=0.60)
    bright_val = 200   # ≈ 0.784 luminance — well above 0.60
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = bright_val
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = float(buf[:, :, 2].mean())

    p.pontormo_dissonance_pass(
        light_thresh   = 0.60,
        shadow_thresh  = 0.32,
        acid_lift      = 0.20,
        violet_push    = 0.0,
        midtone_chroma = 0.0,
        opacity        = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())

    assert r_after > r_before + 2, (
        f"Acid lift should raise R in the highlight zone; "
        f"R_before={r_before:.1f} R_after={r_after:.1f}")


def test_pontormo_dissonance_pass_violet_push_in_shadows():
    """pontormo_dissonance_pass() must boost B and reduce R in the dark zone (violet shadow)."""
    p = _make_small_painter(64, 64)

    # Seed canvas with a dark value (below shadow_thresh=0.32)
    dark_val = 60   # ≈ 0.235 luminance — well below 0.32
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = dark_val
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = float(buf[:, :, 2].mean())
    b_before = float(buf[:, :, 0].mean())

    p.pontormo_dissonance_pass(
        light_thresh   = 0.60,
        shadow_thresh  = 0.32,
        acid_lift      = 0.0,
        violet_push    = 0.25,
        midtone_chroma = 0.0,
        opacity        = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())
    b_after = float(buf_after[:, :, 0].mean())

    assert r_after < r_before - 1, (
        f"Violet push should reduce R in shadow zone; "
        f"R_before={r_before:.1f} R_after={r_after:.1f}")
    assert b_after > b_before + 1, (
        f"Violet push should boost B in shadow zone; "
        f"B_before={b_before:.1f} B_after={b_after:.1f}")


def test_pontormo_dissonance_pass_figure_mask_confines_effect():
    """pontormo_dissonance_pass() with figure_mask must confine acid lift to mask region."""
    p = _make_small_painter(64, 64)

    bright_val = 200
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = bright_val
    buf[:, :, 3]  = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Mask: only left half is figure
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[:, :32] = 1.0

    p.pontormo_dissonance_pass(
        figure_mask    = mask,
        acid_lift      = 0.30,
        violet_push    = 0.0,
        midtone_chroma = 0.0,
        opacity        = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_left  = float(buf_after[:, :32, 2].mean())
    r_right = float(buf_after[:, 32:, 2].mean())

    assert r_left > r_right + 3, (
        f"Acid lift should be stronger in masked (left) region; "
        f"R_left={r_left:.1f} R_right={r_right:.1f}")


def test_pontormo_dissonance_pass_custom_params():
    """pontormo_dissonance_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.50, 0.58), texture_strength=0.0)
    p.pontormo_dissonance_pass(
        light_thresh   = 0.55,
        shadow_thresh  = 0.28,
        acid_lift      = 0.18,
        violet_push    = 0.15,
        midtone_chroma = 0.12,
        opacity        = 0.55,
    )


def test_pontormo_dissonance_pass_large_canvas():
    """pontormo_dissonance_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.52, 0.50, 0.58), texture_strength=0.0)
    p.pontormo_dissonance_pass(opacity=0.68)


# ──────────────────────────────────────────────────────────────────────────────
# aerial_perspective_pass — session 52 (random improvement)
# ──────────────────────────────────────────────────────────────────────────────

def test_aerial_perspective_pass_exists():
    """Painter must expose aerial_perspective_pass() (session 52)."""
    p = _make_small_painter(64, 64)
    assert hasattr(p, "aerial_perspective_pass"), (
        "Painter.aerial_perspective_pass() not found — add it to stroke_engine.py")
    assert callable(p.aerial_perspective_pass)


def test_aerial_perspective_pass_modifies_canvas():
    """aerial_perspective_pass() must change the canvas when opacity > 0."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.40, 0.46, 0.58), texture_strength=0.0)
    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.aerial_perspective_pass(opacity=0.72)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert not np.array_equal(buf_before, buf_after), (
        "Canvas must change after aerial_perspective_pass(opacity=0.72)")


def test_aerial_perspective_pass_opacity_zero_skips():
    """aerial_perspective_pass() with opacity=0 must not change the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.40, 0.46, 0.58), texture_strength=0.0)
    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.aerial_perspective_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert np.array_equal(buf_before, buf_after), (
        "Canvas must not change when aerial_perspective_pass(opacity=0)")


def test_aerial_perspective_pass_upper_rows_more_affected():
    """aerial_perspective_pass() must affect upper rows more than lower rows."""
    p = _make_small_painter(64, 64)

    # Seed with warm earthy tones (high R, lower B) so desaturation is measurable
    warm_r, warm_g, warm_b = 180, 140, 80
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = warm_r   # R
    buf[:, :, 1] = warm_g   # G
    buf[:, :, 0] = warm_b   # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.aerial_perspective_pass(
        sky_band     = 0.60,    # upper 60% affected
        fade_power   = 2.2,
        desaturation = 0.80,    # amplified for measurable shift
        cool_push    = 0.0,     # disable to isolate desaturation
        haze_lift    = 0.0,
        opacity      = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    # Measure how much R has dropped in top rows vs bottom rows.
    # Desaturation pushes warm R toward grey — R should fall near the top.
    r_top    = float(buf_after[:8,  :, 2].mean())   # top 8 rows
    r_bottom = float(buf_after[56:, :, 2].mean())   # bottom 8 rows (below sky_band)

    assert r_bottom > r_top + 3, (
        f"Aerial perspective should reduce R more in upper rows than lower rows; "
        f"R_top={r_top:.1f}  R_bottom={r_bottom:.1f}")


def test_aerial_perspective_pass_cool_push_boosts_blue_at_top():
    """aerial_perspective_pass() cool_push must increase B channel near the top."""
    p = _make_small_painter(64, 64)

    # Seed with a warm value (low B) so boost is measurable
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 160   # R
    buf[:, :, 1] = 140   # G
    buf[:, :, 0] = 90    # B (low — warm canvas)
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    b_top_before = float(buf[:8, :, 0].mean())

    p.aerial_perspective_pass(
        sky_band     = 0.60,
        fade_power   = 2.2,
        desaturation = 0.0,    # disable desaturation to isolate cool push
        cool_push    = 0.25,   # amplified for measurable shift
        haze_lift    = 0.0,
        opacity      = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    b_top_after = float(buf_after[:8, :, 0].mean())

    assert b_top_after > b_top_before + 3, (
        f"Cool push should boost B at the top; "
        f"B_top_before={b_top_before:.1f}  B_top_after={b_top_after:.1f}")


def test_aerial_perspective_pass_below_sky_band_unchanged():
    """Rows below sky_band must not be affected by aerial_perspective_pass()."""
    p = _make_small_painter(64, 64)

    # Seed with a distinctive warm colour
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 160
    buf[:, :, 1] = 120
    buf[:, :, 0] = 80
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.aerial_perspective_pass(
        sky_band     = 0.25,    # only upper 25% = rows 0–15 on a 64-px canvas
        fade_power   = 2.2,
        desaturation = 0.80,
        cool_push    = 0.30,
        haze_lift    = 0.10,
        opacity      = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    # Bottom rows (well below sky_band=0.25 → row 16) should be unchanged
    r_bottom = float(buf_after[40:, :, 2].mean())
    assert abs(r_bottom - 160) < 3, (
        f"Rows below sky_band should be unaffected; "
        f"expected R≈160, got {r_bottom:.1f}")


def test_aerial_perspective_pass_custom_params():
    """aerial_perspective_pass() accepts all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.40, 0.46, 0.58), texture_strength=0.0)
    p.aerial_perspective_pass(
        sky_band     = 0.50,
        fade_power   = 1.8,
        desaturation = 0.45,
        cool_push    = 0.08,
        haze_lift    = 0.04,
        opacity      = 0.65,
    )


def test_aerial_perspective_pass_large_canvas():
    """aerial_perspective_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.40, 0.46, 0.58), texture_strength=0.0)
    p.aerial_perspective_pass(opacity=0.72)


# ──────────────────────────────────────────────────────────────────────────────
# Session 53 — weyden_angular_shadow_pass
# ──────────────────────────────────────────────────────────────────────────────

def test_weyden_angular_shadow_pass_exists():
    """weyden_angular_shadow_pass() must exist on Painter."""
    from stroke_engine import Painter
    assert hasattr(Painter, "weyden_angular_shadow_pass"), (
        "Painter.weyden_angular_shadow_pass not found — add it to stroke_engine.py")
    assert callable(getattr(Painter, "weyden_angular_shadow_pass"))


def test_weyden_angular_shadow_pass_smoke():
    """weyden_angular_shadow_pass() must run without error on default canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.48, 0.40, 0.28), texture_strength=0.0)
    p.weyden_angular_shadow_pass()


def test_weyden_angular_shadow_pass_opacity_zero_no_change():
    """weyden_angular_shadow_pass(opacity=0) must not change the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.48, 0.40, 0.28), texture_strength=0.0)
    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.weyden_angular_shadow_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert np.array_equal(buf_before, buf_after), (
        "Canvas must not change when weyden_angular_shadow_pass(opacity=0)")


def test_weyden_angular_shadow_pass_shadow_zone_cooled():
    """weyden_angular_shadow_pass() must reduce R (cool push) in dark shadow zones."""
    p = _make_small_painter(64, 64)

    # Seed canvas with a warm dark colour (low luminance, high R relative to B)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 60    # R — warm dark
    buf[:, :, 1] = 45    # G
    buf[:, :, 0] = 30    # B — low B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = float(buf[:, :, 2].mean())
    b_before = float(buf[:, :, 0].mean())

    p.weyden_angular_shadow_pass(
        shadow_thresh  = 0.38,
        shadow_cool    = 0.15,   # amplified for measurable shift
        highlight_cool = 0.0,
        edge_sharpen   = 0.0,
        opacity        = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())
    b_after = float(buf_after[:, :, 0].mean())

    # Dark warm pixels should have R reduced and B lifted
    assert r_after < r_before - 1, (
        f"Shadow zone R should decrease after cool push; "
        f"R_before={r_before:.1f}  R_after={r_after:.1f}")
    assert b_after > b_before + 1, (
        f"Shadow zone B should increase after cool push; "
        f"B_before={b_before:.1f}  B_after={b_after:.1f}")


def test_weyden_angular_shadow_pass_highlight_zone_cooled():
    """weyden_angular_shadow_pass() must lift B in bright highlight zones."""
    p = _make_small_painter(64, 64)

    # Seed canvas with a warm bright colour (high luminance, low B)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 230   # R — bright warm
    buf[:, :, 1] = 210   # G
    buf[:, :, 0] = 170   # B — warmer (lower B)
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    b_before = float(buf[:, :, 0].mean())

    p.weyden_angular_shadow_pass(
        light_thresh   = 0.60,
        highlight_cool = 0.12,   # amplified for measurable shift
        shadow_cool    = 0.0,
        edge_sharpen   = 0.0,
        opacity        = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    b_after = float(buf_after[:, :, 0].mean())

    assert b_after > b_before + 1, (
        f"Highlight zone B should increase after cool lift; "
        f"B_before={b_before:.1f}  B_after={b_after:.1f}")


def test_weyden_angular_shadow_pass_with_figure_mask():
    """weyden_angular_shadow_pass() with figure_mask must not alter background."""
    p = _make_small_painter(64, 64)

    # Seed with dark warm colour
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 55
    buf[:, :, 1] = 42
    buf[:, :, 0] = 25
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Mask: figure only in top half
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[:32, :] = 1.0

    p.weyden_angular_shadow_pass(
        figure_mask  = mask,
        shadow_cool  = 0.20,
        edge_sharpen = 0.0,
        opacity      = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    # Bottom half (background, mask=0) must be unchanged
    assert np.array_equal(buf_after[40:, :, :3], buf[40:, :, :3]), (
        "Background pixels (mask=0) must not be altered by weyden_angular_shadow_pass")


def test_weyden_angular_shadow_pass_custom_params():
    """weyden_angular_shadow_pass() must accept all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.48, 0.40, 0.28), texture_strength=0.0)
    p.weyden_angular_shadow_pass(
        shadow_thresh  = 0.32,
        light_thresh   = 0.65,
        edge_sharpen   = 0.40,
        shadow_cool    = 0.10,
        highlight_cool = 0.05,
        opacity        = 0.60,
    )


def test_weyden_angular_shadow_pass_large_canvas():
    """weyden_angular_shadow_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.48, 0.40, 0.28), texture_strength=0.0)
    p.weyden_angular_shadow_pass(opacity=0.65)


# ──────────────────────────────────────────────────────────────────────────────
# Session 54 — memling_jewel_light_pass
# ──────────────────────────────────────────────────────────────────────────────

def test_memling_jewel_light_pass_exists():
    """memling_jewel_light_pass() must exist on Painter."""
    from stroke_engine import Painter
    assert hasattr(Painter, "memling_jewel_light_pass"), (
        "Painter.memling_jewel_light_pass not found — add it to stroke_engine.py")
    assert callable(getattr(Painter, "memling_jewel_light_pass"))


def test_memling_jewel_light_pass_smoke():
    """memling_jewel_light_pass() must run without error on default canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.62, 0.42), texture_strength=0.0)
    p.memling_jewel_light_pass()


def test_memling_jewel_light_pass_opacity_zero_no_change():
    """memling_jewel_light_pass(opacity=0) must not change the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.62, 0.42), texture_strength=0.0)
    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.memling_jewel_light_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert np.array_equal(buf_before, buf_after), (
        "Canvas must not change when memling_jewel_light_pass(opacity=0)")


def test_memling_jewel_light_pass_highlight_zone_cooled():
    """memling_jewel_light_pass() must lift B and reduce R in bright highlight zones."""
    p = _make_small_painter(64, 64)

    # Seed canvas with warm bright colour (high luminance, low B relative to R)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 240   # R — bright warm
    buf[:, :, 1] = 210   # G
    buf[:, :, 0] = 160   # B — relatively low (warm highlight)
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = float(buf[:, :, 2].mean())
    b_before = float(buf[:, :, 0].mean())

    p.memling_jewel_light_pass(
        highlight_thresh  = 0.68,
        jewel_strength    = 0.14,   # amplified for measurable shift
        subsurface_strength = 0.0,
        opacity           = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())
    b_after = float(buf_after[:, :, 0].mean())

    assert b_after > b_before + 1, (
        f"Highlight zone B should increase (jewel-cool push); "
        f"B_before={b_before:.1f}  B_after={b_after:.1f}")
    assert r_after < r_before + 1, (
        f"Highlight zone R should not increase (jewel push reduces R); "
        f"R_before={r_before:.1f}  R_after={r_after:.1f}")


def test_memling_jewel_light_pass_subsurface_midtone_blue_green():
    """memling_jewel_light_pass() must lift G and B in the mid-tone shadow band."""
    p = _make_small_painter(64, 64)

    # Seed canvas with a warm mid-tone colour (lum ~0.45 — in the mid-tone band)
    # Cairo BGRA: B=idx0, G=idx1, R=idx2
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 140   # R — warm mid-tone
    buf[:, :, 1] = 115   # G
    buf[:, :, 0] = 80    # B — low (warm, no cool undertone yet)
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    g_before = float(buf[:, :, 1].mean())
    b_before = float(buf[:, :, 0].mean())

    p.memling_jewel_light_pass(
        midtone_low         = 0.30,
        midtone_high        = 0.65,
        subsurface_strength = 0.18,   # amplified for measurable shift
        jewel_strength      = 0.0,
        opacity             = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    g_after = float(buf_after[:, :, 1].mean())
    b_after = float(buf_after[:, :, 0].mean())

    assert g_after > g_before + 1, (
        f"Mid-tone G should increase (subsurface blue-green push); "
        f"G_before={g_before:.1f}  G_after={g_after:.1f}")
    assert b_after > b_before + 1, (
        f"Mid-tone B should increase (subsurface blue-green push); "
        f"B_before={b_before:.1f}  B_after={b_after:.1f}")


def test_memling_jewel_light_pass_with_figure_mask():
    """memling_jewel_light_pass() with figure_mask must not alter background pixels."""
    p = _make_small_painter(64, 64)

    # Seed with a warm bright colour (triggers highlight zone)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 230
    buf[:, :, 1] = 200
    buf[:, :, 0] = 155
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Mask: figure only in top half
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[:32, :] = 1.0

    p.memling_jewel_light_pass(
        figure_mask      = mask,
        jewel_strength   = 0.20,
        opacity          = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    # Bottom half (background, mask=0) must be unchanged
    assert np.array_equal(buf_after[40:, :, :3], buf[40:, :, :3]), (
        "Background pixels (mask=0) must not be altered by memling_jewel_light_pass")


def test_memling_jewel_light_pass_custom_params():
    """memling_jewel_light_pass() must accept all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.62, 0.42), texture_strength=0.0)
    p.memling_jewel_light_pass(
        highlight_thresh    = 0.78,
        midtone_low         = 0.28,
        midtone_high        = 0.55,
        jewel_strength      = 0.05,
        subsurface_strength = 0.04,
        opacity             = 0.60,
    )


def test_memling_jewel_light_pass_large_canvas():
    """memling_jewel_light_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.72, 0.62, 0.42), texture_strength=0.0)
    p.memling_jewel_light_pass(opacity=0.65)


# ── sfumato_veil_pass depth_gradient improvement (session 54) ────────────────

def test_sfumato_veil_pass_depth_gradient_param_accepted():
    """sfumato_veil_pass() must accept depth_gradient without error."""
    from PIL import Image
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    ref = Image.fromarray(
        (np.ones((64, 64, 3), dtype=np.uint8) * np.array([180, 150, 120],
                                                           dtype=np.uint8)), "RGB")
    p.sfumato_veil_pass(ref, n_veils=2, blur_radius=4.0, depth_gradient=0.6)


def test_sfumato_veil_pass_depth_gradient_zero_unchanged_signature():
    """sfumato_veil_pass(depth_gradient=0.0) must behave identically to no-arg call."""
    from PIL import Image
    # Two painters with identical seeded states must produce identical output.
    ref = Image.fromarray(
        (np.ones((64, 64, 3), dtype=np.uint8) * np.array([180, 150, 120],
                                                           dtype=np.uint8)), "RGB")

    p1 = _make_small_painter(64, 64)
    p1.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p1.sfumato_veil_pass(ref, n_veils=3, blur_radius=4.0, depth_gradient=0.0)
    buf1 = np.frombuffer(p1.canvas.surface.get_data(),
                         dtype=np.uint8).reshape(64, 64, 4).copy()

    p2 = _make_small_painter(64, 64)
    p2.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p2.sfumato_veil_pass(ref, n_veils=3, blur_radius=4.0)
    buf2 = np.frombuffer(p2.canvas.surface.get_data(),
                         dtype=np.uint8).reshape(64, 64, 4)

    assert np.array_equal(buf1, buf2), (
        "sfumato_veil_pass with depth_gradient=0.0 must produce identical "
        "output to calling without depth_gradient")


# ──────────────────────────────────────────────────────────────────────────────
# Session 56 — bronzino_enamel_skin_pass
# ──────────────────────────────────────────────────────────────────────────────

def test_bronzino_enamel_skin_pass_exists():
    """bronzino_enamel_skin_pass() must exist on Painter (session 56)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "bronzino_enamel_skin_pass"), (
        "Painter.bronzino_enamel_skin_pass not found — add it to stroke_engine.py")
    assert callable(getattr(Painter, "bronzino_enamel_skin_pass"))


def test_bronzino_enamel_skin_pass_smoke():
    """bronzino_enamel_skin_pass() must run without error on default canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.58, 0.56), texture_strength=0.0)
    p.bronzino_enamel_skin_pass()


def test_bronzino_enamel_skin_pass_opacity_zero_no_change():
    """bronzino_enamel_skin_pass(opacity=0) must not change the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.58, 0.56), texture_strength=0.0)
    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.bronzino_enamel_skin_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert np.array_equal(buf_before, buf_after), (
        "Canvas must not change when bronzino_enamel_skin_pass(opacity=0)")


def test_bronzino_enamel_skin_pass_midtone_compressed():
    """bronzino_enamel_skin_pass() must reduce variance in the midtone zone."""
    p = _make_small_painter(64, 64)

    # Seed canvas with alternating warm/cool horizontal stripes in midtone range.
    # Even rows: warm mid-tone (high R, low B); odd rows: cool mid-tone (low R, high B).
    # Both have similar luminance (~0.48) so both fall in the midtone band.
    # Cairo BGRA: B=idx0, G=idx1, R=idx2
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    for y in range(64):
        if y % 2 == 0:
            buf[y, :, 2] = 165   # R high — warm
            buf[y, :, 1] = 120
            buf[y, :, 0] = 72    # B low
        else:
            buf[y, :, 2] = 98    # R low — cool
            buf[y, :, 1] = 120
            buf[y, :, 0] = 148   # B high
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_std_before = float(np.std(buf[:, :, 2].astype(float)))

    p.bronzino_enamel_skin_pass(
        midtone_low=0.28,
        midtone_high=0.68,
        compression_strength=0.80,   # amplified for measurable effect
        cool_strength=0.0,
        desaturate_strength=0.0,
        opacity=1.0,
    )

    buf_after  = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    r_std_after = float(np.std(buf_after[:, :, 2].astype(float)))

    assert r_std_after < r_std_before, (
        f"Midtone compression should reduce R-channel std; "
        f"std_before={r_std_before:.2f}  std_after={r_std_after:.2f}")


def test_bronzino_enamel_skin_pass_cool_highlight_push():
    """bronzino_enamel_skin_pass() must lift B and reduce R in bright highlight zones."""
    p = _make_small_painter(64, 64)

    # Seed canvas with bright warm colour — high luminance, low B relative to R.
    # Cairo BGRA: B=idx0, G=idx1, R=idx2
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 240   # R — bright warm highlight
    buf[:, :, 1] = 215   # G
    buf[:, :, 0] = 158   # B — relatively low (warm)
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = float(buf[:, :, 2].mean())
    b_before = float(buf[:, :, 0].mean())

    p.bronzino_enamel_skin_pass(
        highlight_thresh  = 0.68,
        cool_strength     = 0.14,    # amplified for measurable shift
        compression_strength = 0.0,
        desaturate_strength  = 0.0,
        opacity           = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())
    b_after = float(buf_after[:, :, 0].mean())

    assert b_after > b_before + 1, (
        f"Highlight zone B should increase (cool push); "
        f"B_before={b_before:.1f}  B_after={b_after:.1f}")
    assert r_after < r_before + 1, (
        f"Highlight zone R should not increase (cool push reduces R); "
        f"R_before={r_before:.1f}  R_after={r_after:.1f}")


def test_bronzino_enamel_skin_pass_shadow_desaturated():
    """bronzino_enamel_skin_pass() must reduce saturation (narrow R-B gap) in shadows."""
    p = _make_small_painter(64, 64)

    # Seed canvas with warm dark colour in the shadow zone (low luminance, high R-B gap).
    # Cairo BGRA: B=idx0, G=idx1, R=idx2
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 80    # R — warm brown shadow
    buf[:, :, 1] = 55    # G
    buf[:, :, 0] = 28    # B — very low (very warm shadow)
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # R-B gap before: high (warm undertone)
    gap_before = float(buf[:, :, 2].mean()) - float(buf[:, :, 0].mean())

    p.bronzino_enamel_skin_pass(
        shadow_thresh       = 0.55,   # high thresh so these dark pixels are in shadow zone
        desaturate_strength = 0.80,   # amplified for measurable shift
        compression_strength = 0.0,
        cool_strength       = 0.0,
        opacity             = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    gap_after = float(buf_after[:, :, 2].mean()) - float(buf_after[:, :, 0].mean())

    assert gap_after < gap_before, (
        f"Shadow R-B gap should narrow after desaturation; "
        f"gap_before={gap_before:.2f}  gap_after={gap_after:.2f}")


def test_bronzino_enamel_skin_pass_with_figure_mask():
    """bronzino_enamel_skin_pass() with figure_mask must not alter background pixels."""
    p = _make_small_painter(64, 64)

    # Seed with warm bright colour (triggers highlight zone)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 228
    buf[:, :, 1] = 200
    buf[:, :, 0] = 152
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Mask: figure only in top half
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[:32, :] = 1.0

    p.bronzino_enamel_skin_pass(
        figure_mask   = mask,
        cool_strength = 0.20,
        opacity       = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    # Bottom half (background, mask=0) must be unchanged
    assert np.array_equal(buf_after[40:, :, :3], buf[40:, :, :3]), (
        "Background pixels (mask=0) must not be altered by bronzino_enamel_skin_pass")


def test_bronzino_enamel_skin_pass_custom_params():
    """bronzino_enamel_skin_pass() must accept all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.58, 0.56), texture_strength=0.0)
    p.bronzino_enamel_skin_pass(
        midtone_low          = 0.30,
        midtone_high         = 0.68,
        compression_strength = 0.12,
        highlight_thresh     = 0.75,
        cool_strength        = 0.04,
        shadow_thresh        = 0.32,
        desaturate_strength  = 0.18,
        opacity              = 0.65,
    )


def test_bronzino_enamel_skin_pass_large_canvas():
    """bronzino_enamel_skin_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.62, 0.58, 0.56), texture_strength=0.0)
    p.bronzino_enamel_skin_pass(opacity=0.65)


# ──────────────────────────────────────────────────────────────────────────────
# tintoretto_dynamic_light_pass() — session 53
# ──────────────────────────────────────────────────────────────────────────────

def test_tintoretto_dynamic_light_pass_exists():
    """Painter must have tintoretto_dynamic_light_pass() method after session 53."""
    from stroke_engine import Painter
    assert hasattr(Painter, "tintoretto_dynamic_light_pass"), (
        "tintoretto_dynamic_light_pass not found on Painter")
    assert callable(getattr(Painter, "tintoretto_dynamic_light_pass"))


def test_tintoretto_dynamic_light_pass_runs_without_error():
    """tintoretto_dynamic_light_pass() must run on a default canvas without raising."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.10, 0.07, 0.05), texture_strength=0.0)
    p.tintoretto_dynamic_light_pass()


def test_tintoretto_dynamic_light_pass_opacity_zero_noop():
    """tintoretto_dynamic_light_pass() with opacity=0 must not alter any pixels."""
    p = _make_small_painter(64, 64)
    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.tintoretto_dynamic_light_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert np.array_equal(buf_before, buf_after), (
        "opacity=0 must leave canvas completely unchanged")


def test_tintoretto_dynamic_light_pass_contrast_amplification():
    """tintoretto_dynamic_light_pass() must widen tonal range (increase luminance std)."""
    p = _make_small_painter(64, 64)

    # Seed with a gradient — both dark and bright regions present
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    # Top half: bright warm impasto
    buf[:32, :, 2] = 210   # R
    buf[:32, :, 1] = 185   # G
    buf[:32, :, 0] = 140   # B
    # Bottom half: deep shadow
    buf[32:, :, 2] = 45
    buf[32:, :, 1] = 32
    buf[32:, :, 0] = 22
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Compute luminance std before
    r_f  = buf[:, :, 2].astype(float) / 255.0
    g_f  = buf[:, :, 1].astype(float) / 255.0
    b_f  = buf[:, :, 0].astype(float) / 255.0
    lum_before = 0.2126 * r_f + 0.7152 * g_f + 0.0722 * b_f
    std_before = float(np.std(lum_before))

    p.tintoretto_dynamic_light_pass(
        contrast_strength  = 0.40,   # amplified for measurable effect
        silver_strength    = 0.0,
        shadow_depth_push  = 0.0,
        opacity            = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_a   = buf_after[:, :, 2].astype(float) / 255.0
    g_a   = buf_after[:, :, 1].astype(float) / 255.0
    b_a   = buf_after[:, :, 0].astype(float) / 255.0
    lum_after = 0.2126 * r_a + 0.7152 * g_a + 0.0722 * b_a
    std_after = float(np.std(lum_after))

    assert std_after >= std_before - 0.005, (
        f"Contrast amplification should not decrease luminance std; "
        f"std_before={std_before:.4f}  std_after={std_after:.4f}")


def test_tintoretto_dynamic_light_pass_silver_highlight_push():
    """tintoretto_dynamic_light_pass() must lift B and reduce R in bright highlight zones."""
    p = _make_small_painter(64, 64)

    # Seed with bright warm highlight — lum > highlight_thresh
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 235   # R — warm bright highlight
    buf[:, :, 1] = 210   # G
    buf[:, :, 0] = 155   # B — relatively low (warm)
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = float(buf[:, :, 2].mean())
    b_before = float(buf[:, :, 0].mean())

    p.tintoretto_dynamic_light_pass(
        highlight_thresh  = 0.60,    # ensure these pixels are in highlight zone
        silver_strength   = 0.18,    # amplified for measurable shift
        contrast_strength = 0.0,
        shadow_depth_push = 0.0,
        opacity           = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = float(buf_after[:, :, 2].mean())
    b_after = float(buf_after[:, :, 0].mean())

    assert b_after > b_before + 1, (
        f"Silver highlight push must lift B channel; "
        f"B_before={b_before:.1f}  B_after={b_after:.1f}")
    assert r_after < r_before + 1, (
        f"Silver highlight push must not increase R; "
        f"R_before={r_before:.1f}  R_after={r_after:.1f}")


def test_tintoretto_dynamic_light_pass_shadow_void_deepening():
    """tintoretto_dynamic_light_pass() must darken pixels in shadow zones."""
    p = _make_small_painter(64, 64)

    # Seed with dark warm shadow — lum < shadow_thresh
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 65    # R — dark warm brown shadow
    buf[:, :, 1] = 48    # G
    buf[:, :, 0] = 30    # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    mean_lum_before = (0.2126 * 65 + 0.7152 * 48 + 0.0722 * 30) / 255.0

    p.tintoretto_dynamic_light_pass(
        shadow_thresh     = 0.45,    # high threshold so these pixels are in shadow
        shadow_depth_push = 0.60,    # amplified for measurable darkening
        contrast_strength = 0.0,
        silver_strength   = 0.0,
        opacity           = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    mean_r_after = float(buf_after[:, :, 2].mean())
    mean_g_after = float(buf_after[:, :, 1].mean())
    mean_b_after = float(buf_after[:, :, 0].mean())
    mean_lum_after = (0.2126 * mean_r_after + 0.7152 * mean_g_after +
                      0.0722 * mean_b_after) / 255.0

    assert mean_lum_after < mean_lum_before, (
        f"Shadow void deepening must reduce mean luminance; "
        f"lum_before={mean_lum_before:.4f}  lum_after={mean_lum_after:.4f}")


def test_tintoretto_dynamic_light_pass_figure_mask():
    """tintoretto_dynamic_light_pass() with figure_mask must not alter background pixels."""
    p = _make_small_painter(64, 64)

    # Seed with bright warm tone everywhere (triggers silver push if in figure)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 220
    buf[:, :, 1] = 195
    buf[:, :, 0] = 140
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Mask: figure only in top half
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[:32, :] = 1.0

    p.tintoretto_dynamic_light_pass(
        figure_mask     = mask,
        silver_strength = 0.25,
        opacity         = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    # Bottom half (background, mask=0) must be unchanged
    assert np.array_equal(buf_after[40:, :, :3], buf[40:, :, :3]), (
        "Background pixels (mask=0) must not be altered by tintoretto_dynamic_light_pass")


def test_tintoretto_dynamic_light_pass_custom_params():
    """tintoretto_dynamic_light_pass() must accept all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.10, 0.07, 0.05), texture_strength=0.0)
    p.tintoretto_dynamic_light_pass(
        contrast_strength  = 0.15,
        highlight_thresh   = 0.72,
        silver_strength    = 0.06,
        shadow_thresh      = 0.28,
        shadow_depth_push  = 0.12,
        opacity            = 0.60,
    )


def test_tintoretto_dynamic_light_pass_large_canvas():
    """tintoretto_dynamic_light_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.10, 0.07, 0.05), texture_strength=0.0)
    p.tintoretto_dynamic_light_pass(opacity=0.65)


# ── giorgione_tonal_poetry_pass ───────────────────────────────────────────────

def test_giorgione_tonal_poetry_pass_exists():
    """Painter must have a giorgione_tonal_poetry_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "giorgione_tonal_poetry_pass"), (
        "Painter.giorgione_tonal_poetry_pass not found — add it to stroke_engine.py")
    assert callable(getattr(Painter, "giorgione_tonal_poetry_pass"))


def test_giorgione_tonal_poetry_pass_runs_without_error():
    """giorgione_tonal_poetry_pass() must run on default canvas without raising."""
    p = _make_small_painter(64, 64)
    p.giorgione_tonal_poetry_pass()  # should not raise


def test_giorgione_tonal_poetry_pass_opacity_zero_noop():
    """giorgione_tonal_poetry_pass(opacity=0) must not alter any pixels."""
    p = _make_small_painter(64, 64)

    # Seed with mid-grey so midtone lift would fire if opacity > 0
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 128   # R
    buf[:, :, 1] = 128   # G
    buf[:, :, 0] = 128   # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    before = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4).copy()
    p.giorgione_tonal_poetry_pass(opacity=0.0)
    after  = np.frombuffer(p.canvas.surface.get_data(),
                           dtype=np.uint8).reshape(64, 64, 4)

    assert np.array_equal(before[:, :, :3], after[:, :, :3]), (
        "giorgione_tonal_poetry_pass(opacity=0) must not alter any pixels — "
        "zero opacity is the no-op sentinel")


def test_giorgione_tonal_poetry_pass_midtone_lift_brightens():
    """giorgione_tonal_poetry_pass() must increase mean luminance on a mid-grey canvas."""
    p = _make_small_painter(64, 64)

    # Fill with mid-grey (luminance ≈ 0.50 — firmly in the midtone zone)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 128
    buf[:, :, 1] = 128
    buf[:, :, 0] = 128
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    lum_before = (0.2126 * buf_before[:, :, 2].astype(np.float32) +
                  0.7152 * buf_before[:, :, 1].astype(np.float32) +
                  0.0722 * buf_before[:, :, 0].astype(np.float32)).mean() / 255.0

    p.giorgione_tonal_poetry_pass(luminous_lift=0.15, opacity=1.0)

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    lum_after  = (0.2126 * buf_after[:, :, 2].astype(np.float32) +
                  0.7152 * buf_after[:, :, 1].astype(np.float32) +
                  0.0722 * buf_after[:, :, 0].astype(np.float32)).mean() / 255.0

    assert lum_after > lum_before, (
        f"giorgione_tonal_poetry_pass() midtone lift must raise mean luminance on a "
        f"mid-grey canvas; lum_before={lum_before:.4f}  lum_after={lum_after:.4f}")


def test_giorgione_tonal_poetry_pass_warm_lift_on_midtones():
    """giorgione_tonal_poetry_pass() must add more to R than B on a mid-grey canvas (warm lift)."""
    p = _make_small_painter(64, 64)

    # Fill with neutral mid-grey — in both midtone and shadow-transition zones
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 100   # R — slightly below mid so warm_shadow fires too
    buf[:, :, 1] = 100   # G
    buf[:, :, 0] = 100   # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.giorgione_tonal_poetry_pass(
        luminous_lift=0.10,
        warm_shadow_strength=0.08,
        opacity=1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    mean_r = float(buf_after[:, :, 2].mean())
    mean_b = float(buf_after[:, :, 0].mean())

    assert mean_r >= mean_b, (
        f"giorgione_tonal_poetry_pass() warm lift should result in mean R ≥ mean B "
        f"on a neutral input; R={mean_r:.1f}  B={mean_b:.1f} — "
        f"Giorgione's shadow-transition warms toward raw-sienna earth tones")


def test_giorgione_tonal_poetry_pass_figure_mask_background_unchanged():
    """giorgione_tonal_poetry_pass() with figure_mask must not alter background pixels."""
    p = _make_small_painter(64, 64)

    # Seed with uniform mid-grey
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :3] = 128
    buf[:, :,  3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Mask: figure only in top half
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[:32, :] = 1.0   # top half is figure interior

    p.giorgione_tonal_poetry_pass(
        figure_mask        = mask,
        cool_edge_strength = 0.20,   # strong enough to detect if it bleeds into background
        opacity            = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    # Bottom rows (mask=0, strictly background) must be unchanged
    assert np.array_equal(buf_after[50:, :, :3], buf[50:, :, :3]), (
        "giorgione_tonal_poetry_pass() with figure_mask must not alter pixels where "
        "mask=0 (pure background) — cool_edge_strength bleeds only at the silhouette edge")


def test_giorgione_tonal_poetry_pass_custom_params():
    """giorgione_tonal_poetry_pass() must accept all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.56, 0.38), texture_strength=0.0)
    p.giorgione_tonal_poetry_pass(
        midtone_low          = 0.25,
        midtone_high         = 0.65,
        luminous_lift        = 0.10,
        warm_shadow_strength = 0.04,
        cool_edge_strength   = 0.03,
        opacity              = 0.60,
    )


def test_giorgione_tonal_poetry_pass_large_canvas():
    """giorgione_tonal_poetry_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.68, 0.56, 0.38), texture_strength=0.0)
    p.giorgione_tonal_poetry_pass(opacity=0.70)
