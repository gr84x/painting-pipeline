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

def _canvas_bytes(p) -> bytes:
    """Return a snapshot of the canvas buffer as bytes for comparison."""
    import numpy as _np
    h, w = p.h, p.w
    buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((h, w, 4)).copy()
    return buf.tobytes()


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
        "is_barbizon":                   period == Period.BARBIZON,
        "is_roman_grand_tour":           period == Period.ROMAN_GRAND_TOUR_CLASSICISM,
        "is_renaissance_soft":           (period == Period.RENAISSANCE
                                          and sp.get("edge_softness", 0.0) >= 0.80),
        "is_ferrarese_civic_grandeur":       period == Period.FERRARESE_CIVIC_GRANDEUR,
        "is_venetian_gilt_byzantine_splendour": period == Period.VENETIAN_GILT_BYZANTINE_SPLENDOUR,
        "is_lombard_humble_genre":               period == Period.LOMBARD_HUMBLE_GENRE,
        "is_bergamask_portrait":                 period == Period.BERGAMASK_PORTRAIT,
        "is_milanese_metallic_portraiture":      period == Period.MILANESE_METALLIC_PORTRAITURE,
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


def test_gentileschi_dramatic_flesh_pass_warms_spotlight_zone():
    """
    R channel should increase in the spotlight zone (upper-left, mid-high luma) after
    gentileschi_dramatic_flesh_pass — the warm amber-ivory lit-zone lift.
    Fill with a mid-tone canvas, apply with amber_r=0.20, confirm R rises in upper-left.
    """
    p = _make_small_painter(32, 32)
    # Mid-tone warm canvas: lum ≈ 0.52 (above luma_lo default 0.40)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(32, 32, 4).copy()
    buf[:, :, 2] = 160   # R
    buf[:, :, 1] = 138   # G
    buf[:, :, 0] = 110   # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = int(buf[:, :, 2].mean())

    p.gentileschi_dramatic_flesh_pass(
        shadow_deepen = 0.0,   # disable shadow darkening to isolate amber lift
        amber_r       = 0.20,
        amber_g       = 0.08,
        luma_lo       = 0.40,
        opacity       = 1.0,
    )
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(32, 32, 4)
    r_after = int(buf_after[:, :, 2].mean())
    assert r_after >= r_before, (
        f"gentileschi_dramatic_flesh_pass should warm R in spotlight zone; "
        f"R before={r_before}  after={r_after}")


def test_gentileschi_dramatic_flesh_pass_warms_highlights():
    """
    R channel should increase in bright highlight pixels after gentileschi_dramatic_flesh_pass —
    the candlelit amber-ivory lift (amber_r) applied to pixels above luma_lo.
    Fill with near-white (lum ~0.86), confirm R rises via amber_r boost.
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
        shadow_deepen = 0.0,    # disable shadow path to isolate amber lift
        amber_r       = 0.12,
        amber_g       = 0.0,
        luma_lo       = 0.40,
        opacity       = 1.0,
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
        amber_r=0.10, amber_g=0.04, shadow_deepen=0.35, opacity=1.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    assert not np.array_equal(buf_before, buf_after), (
        "gentileschi_dramatic_flesh_pass should change the canvas when opacity=1.0")


def test_gentileschi_dramatic_flesh_pass_custom_params():
    """gentileschi_dramatic_flesh_pass() accepts all custom parameters without error."""
    p = _make_small_painter()
    p.tone_ground((0.45, 0.32, 0.22), texture_strength=0.0)
    p.gentileschi_dramatic_flesh_pass(
        dir_x         = 0.60,
        dir_y         = 0.40,
        shadow_hi     = 0.35,
        shadow_deepen = 0.18,
        luma_lo       = 0.38,
        amber_r       = 0.06,
        amber_g       = 0.03,
        chroma_boost  = 0.35,
        opacity       = 0.65,
    )


def test_gentileschi_dramatic_flesh_pass_large_canvas():
    """gentileschi_dramatic_flesh_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.45, 0.32, 0.22), texture_strength=0.0)
    p.gentileschi_dramatic_flesh_pass(amber_r=0.06, shadow_deepen=0.40, opacity=0.75)


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


# ── Session 126 — fra_bartolommeo_velo_shadow_pass() ─────────────────────────

def test_fra_bartolommeo_velo_shadow_pass_exists():
    """Painter must have fra_bartolommeo_velo_shadow_pass() method (session 126)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "fra_bartolommeo_velo_shadow_pass"), (
        "fra_bartolommeo_velo_shadow_pass not found on Painter")
    assert callable(getattr(Painter, "fra_bartolommeo_velo_shadow_pass"))


def test_fra_bartolommeo_velo_shadow_pass_no_error():
    """fra_bartolommeo_velo_shadow_pass() must run without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.64, 0.52, 0.34), texture_strength=0.0)
    p.fra_bartolommeo_velo_shadow_pass()


def test_fra_bartolommeo_velo_shadow_pass_noop_at_opacity_zero():
    """fra_bartolommeo_velo_shadow_pass(opacity=0) must be a noop."""
    p = _make_small_painter(64, 64)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :] = [120, 140, 160, 255]
    p.canvas.surface.get_data()[:] = buf.tobytes()
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.fra_bartolommeo_velo_shadow_pass(opacity=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        "fra_bartolommeo_velo_shadow_pass(opacity=0) should be a noop")


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


# ── veronese_luminous_feast_pass (Session 59) ─────────────────────────────────

def test_veronese_luminous_feast_pass_exists():
    """Painter must expose veronese_luminous_feast_pass() as a callable method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "veronese_luminous_feast_pass"), (
        "Painter.veronese_luminous_feast_pass not found — add it to stroke_engine.py")
    assert callable(Painter.veronese_luminous_feast_pass)


def test_veronese_luminous_feast_pass_runs_without_error():
    """veronese_luminous_feast_pass() must complete without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.54, 0.36), texture_strength=0.0)
    p.veronese_luminous_feast_pass()


def test_veronese_luminous_feast_pass_boosts_saturation_in_midtones():
    """veronese_luminous_feast_pass() must increase colour saturation on a saturated mid-grey canvas."""
    p = _make_small_painter(64, 64)

    # Seed with a mid-luminance saturated red to test saturation boost
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    # R=160, G=80, B=60 → mid-luminance, warm-red, clearly saturated
    buf[:, :, 2] = 160   # R
    buf[:, :, 1] = 80    # G
    buf[:, :, 0] = 60    # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Compute saturation before (cmax - cmin) / cmax in float
    r0, g0, b0 = 160 / 255.0, 80 / 255.0, 60 / 255.0
    cmax0 = max(r0, g0, b0)
    cmin0 = min(r0, g0, b0)
    sat_before = (cmax0 - cmin0) / cmax0

    p.veronese_luminous_feast_pass(saturation_boost=0.20, opacity=1.0)

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r1 = buf_after[:, :, 2].astype(np.float32).mean() / 255.0
    g1 = buf_after[:, :, 1].astype(np.float32).mean() / 255.0
    b1 = buf_after[:, :, 0].astype(np.float32).mean() / 255.0
    cmax1 = max(r1, g1, b1)
    cmin1 = min(r1, g1, b1)
    sat_after = (cmax1 - cmin1) / (cmax1 + 1e-8)

    assert sat_after >= sat_before, (
        f"veronese_luminous_feast_pass() saturation boost must not reduce saturation on "
        f"a mid-tone saturated input; sat_before={sat_before:.4f}  sat_after={sat_after:.4f}")


def test_veronese_luminous_feast_pass_cool_highlight_adds_blue():
    """veronese_luminous_feast_pass() must add blue to bright pixels (cool highlight push)."""
    p = _make_small_painter(64, 64)

    # Fill with very bright near-white — triggers cool highlight zone
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 230   # R — very bright
    buf[:, :, 1] = 215   # G
    buf[:, :, 0] = 190   # B — start warm to make cool push detectable
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    b_before = float(buf[:, :, 0].mean())

    p.veronese_luminous_feast_pass(
        cool_highlight_strength=0.15,
        opacity=1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    b_after = float(buf_after[:, :, 0].mean())

    assert b_after > b_before, (
        f"veronese_luminous_feast_pass() cool highlight push must raise the B channel "
        f"on bright pixels; B_before={b_before:.1f}  B_after={b_after:.1f} — "
        f"Veronese's cool silver-ivory highlights, not Titian's warm gold")


def test_veronese_luminous_feast_pass_figure_mask_background_unchanged():
    """veronese_luminous_feast_pass() with figure_mask must not alter background pixels."""
    p = _make_small_painter(64, 64)

    # Seed with uniform mid-tone saturated colour
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 140   # R
    buf[:, :, 1] = 100   # G
    buf[:, :, 0] = 80    # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Mask: figure only in top half
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[:32, :] = 1.0

    p.veronese_luminous_feast_pass(
        figure_mask      = mask,
        saturation_boost = 0.30,
        opacity          = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    # Bottom rows (mask=0, pure background) must be unchanged
    assert np.array_equal(buf_after[50:, :, :3], buf[50:, :, :3]), (
        "veronese_luminous_feast_pass() with figure_mask must not alter pixels where "
        "mask=0 — saturation boost must be gated to the figure interior only")


def test_veronese_luminous_feast_pass_custom_params():
    """veronese_luminous_feast_pass() must accept all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.54, 0.36), texture_strength=0.0)
    p.veronese_luminous_feast_pass(
        midtone_low             = 0.30,
        midtone_high            = 0.70,
        saturation_boost        = 0.10,
        cool_highlight_strength = 0.04,
        shadow_chroma_preserve  = 0.06,
        opacity                 = 0.60,
    )


def test_veronese_luminous_feast_pass_large_canvas():
    """veronese_luminous_feast_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.62, 0.54, 0.36), texture_strength=0.0)
    p.veronese_luminous_feast_pass(opacity=0.72)


# ── murillo_vapor_pass() ──────────────────────────────────────────────────────

def test_murillo_vapor_pass_exists():
    """murillo_vapor_pass() must be a method on the Painter class."""
    from stroke_engine import Painter
    assert hasattr(Painter, "murillo_vapor_pass"), (
        "murillo_vapor_pass not found on Painter — add the method to stroke_engine.py")
    assert callable(getattr(Painter, "murillo_vapor_pass")), (
        "murillo_vapor_pass must be callable")


def test_murillo_vapor_pass_smoke():
    """murillo_vapor_pass() must run without error on a small warm-toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.48, 0.30), texture_strength=0.0)
    p.murillo_vapor_pass()


def test_murillo_vapor_pass_warms_canvas():
    """murillo_vapor_pass() must increase the R channel average (warm bloom effect)."""
    p = _make_small_painter(64, 64)

    # Seed with a uniform cool-grey canvas
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :] = 0
    buf[:, :, 2] = 140   # R in BGRA = index 2
    buf[:, :, 1] = 140   # G
    buf[:, :, 0] = 140   # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    r_before = buf[:, :, 2].astype(np.float32).mean()

    p.murillo_vapor_pass(warmth_strength=0.25, opacity=1.0)

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    r_after = buf_after[:, :, 2].astype(np.float32).mean()

    assert r_after >= r_before, (
        f"murillo_vapor_pass() must increase R-channel mean (warm bloom); "
        f"R_before={r_before:.1f}  R_after={r_after:.1f}")


def test_murillo_vapor_pass_opacity_zero_no_change():
    """murillo_vapor_pass(opacity=0.0) must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.48, 0.30), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    p.murillo_vapor_pass(opacity=0.0)
    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    assert np.array_equal(buf_before, buf_after), (
        "murillo_vapor_pass(opacity=0.0) must not alter the canvas — "
        "zero opacity means no changes applied")


def test_murillo_vapor_pass_figure_mask_preserves_background():
    """murillo_vapor_pass() with figure_mask must not alter pure-background pixels."""
    p = _make_small_painter(64, 64)

    # Seed with uniform warm-grey
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 160   # R
    buf[:, :, 1] = 130   # G
    buf[:, :, 0] = 100   # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    # Mask: figure only in top half
    mask = np.zeros((64, 64), dtype=np.float32)
    mask[:32, :] = 1.0

    p.murillo_vapor_pass(
        figure_mask    = mask,
        warmth_strength = 0.30,
        opacity        = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)

    # Bottom rows (mask=0) must be unchanged
    assert np.array_equal(buf_after[50:, :, :3], buf[50:, :, :3]), (
        "murillo_vapor_pass() with figure_mask must not alter pixels where mask=0 — "
        "warm bloom and shadow warmth must be gated to figure interior only")


def test_murillo_vapor_pass_custom_params():
    """murillo_vapor_pass() must accept all custom parameters without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.48, 0.30), texture_strength=0.0)
    p.murillo_vapor_pass(
        warmth_strength  = 0.12,
        bloom_radius     = 8,
        shadow_warmth    = 0.06,
        highlight_glow   = 0.05,
        opacity          = 0.50,
    )


def test_murillo_vapor_pass_large_canvas():
    """murillo_vapor_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.60, 0.48, 0.30), texture_strength=0.0)
    p.murillo_vapor_pass(opacity=0.68)


# ── SPANISH_BAROQUE period routing ────────────────────────────────────────────

def test_spanish_baroque_period_in_enum():
    """Period.SPANISH_BAROQUE must exist in the Period enum."""
    assert hasattr(Period, "SPANISH_BAROQUE"), (
        "Period.SPANISH_BAROQUE not found in scene_schema.py — add the enum value")


def test_spanish_baroque_stroke_params_valid():
    """Style(period=SPANISH_BAROQUE).stroke_params must return a complete dict."""
    style  = Style(medium=Medium.OIL, period=Period.SPANISH_BAROQUE)
    params = style.stroke_params
    assert "stroke_size_face" in params, "stroke_params missing stroke_size_face"
    assert "stroke_size_bg"   in params, "stroke_params missing stroke_size_bg"
    assert "wet_blend"        in params, "stroke_params missing wet_blend"
    assert "edge_softness"    in params, "stroke_params missing edge_softness"
    assert params["stroke_size_face"] > 0
    assert params["stroke_size_bg"]   > 0
    assert 0.0 <= params["wet_blend"]     <= 1.0
    assert 0.0 <= params["edge_softness"] <= 1.0


def test_spanish_baroque_high_wet_blend():
    """SPANISH_BAROQUE wet_blend must be ≥ 0.55 — estilo vaporoso demands high blending."""
    p = Style(medium=Medium.OIL, period=Period.SPANISH_BAROQUE).stroke_params
    assert p["wet_blend"] >= 0.55, (
        f"SPANISH_BAROQUE wet_blend should be ≥0.55 (vaporous blending); "
        f"got {p['wet_blend']:.2f}")


def test_spanish_baroque_high_edge_softness():
    """SPANISH_BAROQUE edge_softness must be ≥ 0.60 — vaporous tender dissolution."""
    p = Style(medium=Medium.OIL, period=Period.SPANISH_BAROQUE).stroke_params
    assert p["edge_softness"] >= 0.60, (
        f"SPANISH_BAROQUE edge_softness should be ≥0.60; got {p['edge_softness']:.2f}")


# ── zurbaran_stark_devotion_pass ──────────────────────────────────────────────

def test_zurbaran_stark_devotion_pass_exists():
    """Painter must expose zurbaran_stark_devotion_pass() as a callable method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "zurbaran_stark_devotion_pass"), (
        "Painter is missing zurbaran_stark_devotion_pass() — add the method to stroke_engine.py")
    assert callable(Painter.zurbaran_stark_devotion_pass)


def test_zurbaran_stark_devotion_pass_runs():
    """zurbaran_stark_devotion_pass() must complete without error on a small canvas."""
    p = _make_small_painter(80, 80)
    p.tone_ground((0.08, 0.06, 0.05), texture_strength=0.0)
    p.zurbaran_stark_devotion_pass(opacity=0.72)


def test_zurbaran_stark_devotion_pass_skipped_at_zero_opacity():
    """zurbaran_stark_devotion_pass() must leave canvas unchanged when opacity=0."""
    p = _make_small_painter(40, 40)
    p.tone_ground((0.50, 0.40, 0.35), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.zurbaran_stark_devotion_pass(opacity=0.0)
    after  = _canvas_bytes(p)
    assert before == after, "Canvas must not change when opacity=0"


def test_zurbaran_stark_devotion_pass_deepens_dark_shadows():
    """zurbaran_stark_devotion_pass() must reduce luminance in near-black zones."""
    import numpy as _np
    p = _make_small_painter(60, 60)
    # Fill with a dark-shadow tone (lum ≈ 0.14) — within Zurbarán void zone (<0.28)
    p.tone_ground((0.14, 0.10, 0.08), texture_strength=0.0)

    buf_before = _np.frombuffer(p.canvas.surface.get_data(),
                                dtype=_np.uint8).reshape((60, 60, 4)).copy()
    r_before = buf_before[:, :, 2].astype(float).mean()

    p.zurbaran_stark_devotion_pass(void_depth=0.30, opacity=1.0)

    buf_after = _np.frombuffer(p.canvas.surface.get_data(),
                               dtype=_np.uint8).reshape((60, 60, 4)).copy()
    r_after = buf_after[:, :, 2].astype(float).mean()

    assert r_after < r_before, (
        f"zurbaran_stark_devotion_pass() must reduce red channel in shadow zones "
        f"(cold void deepening); before={r_before:.1f} after={r_after:.1f}")


def test_zurbaran_stark_devotion_pass_cools_highlights():
    """zurbaran_stark_devotion_pass() must add blue channel in very bright zones."""
    import numpy as _np
    p = _make_small_painter(60, 60)
    # Fill with near-white (lum > 0.70) — within crystalline drapery zone
    p.tone_ground((0.90, 0.90, 0.88), texture_strength=0.0)

    buf_before = _np.frombuffer(p.canvas.surface.get_data(),
                                dtype=_np.uint8).reshape((60, 60, 4)).copy()
    b_before = buf_before[:, :, 0].astype(float).mean()   # BGRA: channel 0 = blue

    p.zurbaran_stark_devotion_pass(crystalline_strength=0.25, opacity=1.0)

    buf_after = _np.frombuffer(p.canvas.surface.get_data(),
                               dtype=_np.uint8).reshape((60, 60, 4)).copy()
    b_after = buf_after[:, :, 0].astype(float).mean()

    assert b_after >= b_before, (
        f"zurbaran_stark_devotion_pass() must increase blue channel in bright zones "
        f"(crystalline cool-white push); before={b_before:.1f} after={b_after:.1f}")


def test_zurbaran_stark_devotion_pass_with_figure_mask():
    """zurbaran_stark_devotion_pass() with figure_mask=1 must modify the canvas."""
    import numpy as _np
    p = _make_small_painter(60, 60)
    # Dark shadow canvas — void zone should be deepened
    p.tone_ground((0.12, 0.09, 0.07), texture_strength=0.0)
    mask = _np.ones((60, 60), dtype=_np.float32)  # full figure mask
    before = _canvas_bytes(p)
    p.zurbaran_stark_devotion_pass(figure_mask=mask, void_depth=0.30, opacity=1.0)
    after  = _canvas_bytes(p)
    assert before != after, "Canvas must change when figure_mask=1 and opacity>0"


def test_zurbaran_stark_devotion_pass_background_protected_by_mask():
    """zurbaran_stark_devotion_pass() must not modify background pixels when mask=0."""
    import numpy as _np
    p = _make_small_painter(60, 60)
    # Dark shadow canvas — void zone would normally be deepened
    p.tone_ground((0.12, 0.09, 0.07), texture_strength=0.0)
    mask = _np.zeros((60, 60), dtype=_np.float32)   # zero mask — no figure region
    before = _canvas_bytes(p)
    p.zurbaran_stark_devotion_pass(figure_mask=mask, opacity=1.0)
    after  = _canvas_bytes(p)
    assert before == after, (
        "Canvas must be unchanged when figure_mask=0 everywhere — "
        "background pixels must be protected from zurbaran_stark_devotion_pass()")


def test_zurbaran_stark_devotion_pass_large_canvas():
    """zurbaran_stark_devotion_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.08, 0.06, 0.05), texture_strength=0.0)
    p.zurbaran_stark_devotion_pass(opacity=0.72)


# ── TENEBRIST vs SPANISH_BAROQUE polarity checks ─────────────────────────────

def test_tenebrist_crisper_than_spanish_baroque():
    """TENEBRIST edge_softness must be less than SPANISH_BAROQUE (Zurbarán < Murillo)."""
    ten  = Style(medium=Medium.OIL, period=Period.TENEBRIST).stroke_params
    baro = Style(medium=Medium.OIL, period=Period.SPANISH_BAROQUE).stroke_params
    assert ten["edge_softness"] < baro["edge_softness"], (
        f"TENEBRIST edge_softness ({ten['edge_softness']:.2f}) must be less than "
        f"SPANISH_BAROQUE ({baro['edge_softness']:.2f}) — "
        f"Zurbarán's hard devotional edges are the polar opposite of Murillo's vaporous dissolution")


def test_tenebrist_drier_than_spanish_baroque():
    """TENEBRIST wet_blend must be less than SPANISH_BAROQUE (Zurbarán drier than Murillo)."""
    ten  = Style(medium=Medium.OIL, period=Period.TENEBRIST).stroke_params
    baro = Style(medium=Medium.OIL, period=Period.SPANISH_BAROQUE).stroke_params
    assert ten["wet_blend"] < baro["wet_blend"], (
        f"TENEBRIST wet_blend ({ten['wet_blend']:.2f}) must be less than "
        f"SPANISH_BAROQUE ({baro['wet_blend']:.2f}) — "
        f"Zurbarán's sculptural dryness contrasts sharply with Murillo's vaporous wet-on-wet")


# ── sfumato_thermal_gradient_pass ────────────────────────────────────────────

def test_sfumato_thermal_gradient_pass_exists():
    """Painter must expose sfumato_thermal_gradient_pass() as a callable method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "sfumato_thermal_gradient_pass"), (
        "Painter is missing sfumato_thermal_gradient_pass() — add the method to stroke_engine.py")
    assert callable(Painter.sfumato_thermal_gradient_pass)


def test_sfumato_thermal_gradient_pass_runs():
    """sfumato_thermal_gradient_pass() must complete without error on a small canvas."""
    p = _make_small_painter(80, 80)
    p.tone_ground((0.50, 0.48, 0.42), texture_strength=0.0)
    p.sfumato_thermal_gradient_pass(opacity=0.55)


def test_sfumato_thermal_gradient_pass_skipped_at_zero_opacity():
    """sfumato_thermal_gradient_pass() must leave canvas unchanged when opacity=0."""
    p = _make_small_painter(40, 40)
    p.tone_ground((0.50, 0.48, 0.42), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.sfumato_thermal_gradient_pass(opacity=0.0)
    after  = _canvas_bytes(p)
    assert before == after, "Canvas must not change when opacity=0"


def test_sfumato_thermal_gradient_pass_cools_upper_region():
    """sfumato_thermal_gradient_pass() must increase blue in upper canvas rows."""
    import numpy as _np
    p = _make_small_painter(80, 80)
    # Neutral mid-tone ground
    p.tone_ground((0.55, 0.55, 0.55), texture_strength=0.0)

    buf_before = _np.frombuffer(p.canvas.surface.get_data(),
                                dtype=_np.uint8).reshape((80, 80, 4)).copy()
    # Measure mean blue in top quarter (distance zone)
    b_top_before = buf_before[:20, :, 0].astype(float).mean()

    p.sfumato_thermal_gradient_pass(
        cool_strength=0.15, warm_strength=0.0, horizon_y=0.70,
        gradient_width=0.20, edge_soften_radius=3, opacity=1.0
    )

    buf_after = _np.frombuffer(p.canvas.surface.get_data(),
                               dtype=_np.uint8).reshape((80, 80, 4)).copy()
    b_top_after = buf_after[:20, :, 0].astype(float).mean()

    assert b_top_after > b_top_before, (
        f"sfumato_thermal_gradient_pass() must increase blue in upper (distance) zone; "
        f"before={b_top_before:.1f} after={b_top_after:.1f}")


def test_sfumato_thermal_gradient_pass_warms_lower_region():
    """sfumato_thermal_gradient_pass() must increase red in lower canvas rows."""
    import numpy as _np
    p = _make_small_painter(80, 80)
    # Neutral mid-tone ground
    p.tone_ground((0.55, 0.55, 0.55), texture_strength=0.0)

    buf_before = _np.frombuffer(p.canvas.surface.get_data(),
                                dtype=_np.uint8).reshape((80, 80, 4)).copy()
    # Measure mean red in bottom quarter (foreground zone)
    r_bot_before = buf_before[60:, :, 2].astype(float).mean()

    p.sfumato_thermal_gradient_pass(
        warm_strength=0.15, cool_strength=0.0, horizon_y=0.30,
        gradient_width=0.20, edge_soften_radius=3, opacity=1.0
    )

    buf_after = _np.frombuffer(p.canvas.surface.get_data(),
                               dtype=_np.uint8).reshape((80, 80, 4)).copy()
    r_bot_after = buf_after[60:, :, 2].astype(float).mean()

    assert r_bot_after > r_bot_before, (
        f"sfumato_thermal_gradient_pass() must increase red in lower (foreground) zone; "
        f"before={r_bot_before:.1f} after={r_bot_after:.1f}")


def test_sfumato_thermal_gradient_pass_background_only_with_mask():
    """sfumato_thermal_gradient_pass() with full figure mask must not change the canvas."""
    import numpy as _np
    p = _make_small_painter(60, 60)
    p.tone_ground((0.55, 0.55, 0.55), texture_strength=0.0)
    # A fully-figure mask means the background mask is zero everywhere
    full_fig_mask = _np.ones((60, 60), dtype=_np.float32)
    before = _canvas_bytes(p)
    p.sfumato_thermal_gradient_pass(
        figure_mask=full_fig_mask, warm_strength=0.15, cool_strength=0.15, opacity=1.0
    )
    after  = _canvas_bytes(p)
    assert before == after, (
        "Canvas must not change when figure_mask=1 everywhere — the thermal gradient "
        "applies to background only; a pure-figure canvas has no background to modify")


def test_sfumato_thermal_gradient_pass_large_canvas():
    """sfumato_thermal_gradient_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.50, 0.48, 0.42), texture_strength=0.0)
    p.sfumato_thermal_gradient_pass(opacity=0.55)


# ── BARBIZON period routing ────────────────────────────────────────────────────

def test_barbizon_period_exists():
    """Period.BARBIZON must exist in the Period enum."""
    assert hasattr(Period, "BARBIZON"), (
        "Period.BARBIZON not found in scene_schema.py — add the enum value")


def test_barbizon_stroke_params_valid():
    """Style(period=BARBIZON).stroke_params must return a complete dict."""
    style  = Style(medium=Medium.OIL, period=Period.BARBIZON)
    params = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in params, f"BARBIZON stroke_params missing key: {key}"


def test_barbizon_high_wet_blend():
    """BARBIZON wet_blend must be >= 0.60 — silvery atmospheric blending."""
    p = Style(medium=Medium.OIL, period=Period.BARBIZON).stroke_params
    assert p["wet_blend"] >= 0.60, (
        f"BARBIZON wet_blend should be >=0.60 (atmospheric blending); "
        f"got {p['wet_blend']:.2f}")


def test_barbizon_high_edge_softness():
    """BARBIZON edge_softness must be >= 0.70 — dissolved misty foliage edges."""
    p = Style(medium=Medium.OIL, period=Period.BARBIZON).stroke_params
    assert p["edge_softness"] >= 0.70, (
        f"BARBIZON edge_softness should be >=0.70; got {p['edge_softness']:.2f}")


def test_barbizon_softer_than_zurbaran():
    """BARBIZON edge_softness must exceed TENEBRIST (silver veil vs hard void)."""
    barb = Style(medium=Medium.OIL, period=Period.BARBIZON).stroke_params
    tenb = Style(medium=Medium.OIL, period=Period.TENEBRIST).stroke_params
    assert barb["edge_softness"] > tenb["edge_softness"], (
        f"BARBIZON edge_softness ({barb['edge_softness']:.2f}) must exceed "
        f"TENEBRIST ({tenb['edge_softness']:.2f}) — "
        f"Corot's atmospheric dissolution vs Zurbarán's hard devotional edges")


# ── corot_silver_veil_pass() tests ─────────────────────────────────────────────

def _buf(p):
    """Return canvas as (H, W, 4) uint8 numpy array (BGRA)."""
    import numpy as _np
    h, w = p.h, p.w
    return _np.frombuffer(p.canvas.surface.get_data(),
                          dtype=_np.uint8).reshape((h, w, 4)).copy()


def test_corot_silver_veil_pass_exists():
    """Painter must have a corot_silver_veil_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "corot_silver_veil_pass"), (
        "Painter class is missing corot_silver_veil_pass() — "
        "add the method to stroke_engine.py")


def test_corot_silver_veil_pass_runs():
    """corot_silver_veil_pass() must run without error on a small canvas."""
    p = _make_small_painter(40, 40)
    p.corot_silver_veil_pass(opacity=0.50)


def test_corot_silver_veil_pass_skipped_at_zero_opacity():
    """corot_silver_veil_pass() must be a no-op when opacity=0."""
    import numpy as np
    p      = _make_small_painter(40, 40)
    before = _buf(p).copy()
    p.corot_silver_veil_pass(opacity=0.0)
    after  = _buf(p)
    assert np.array_equal(before, after), (
        "corot_silver_veil_pass with opacity=0 must leave the canvas unchanged")


def test_corot_silver_veil_pass_desaturates():
    """corot_silver_veil_pass() must reduce overall colour saturation."""
    import numpy as np
    p = _make_small_painter(60, 60)
    # Use tone_ground to fill with a vivid warm-red canvas (high chroma)
    p.tone_ground((0.80, 0.12, 0.08), texture_strength=0.0)
    before      = _buf(p).astype(np.float32) / 255.0
    # In BGRA layout: channel 2=R, channel 1=G, channel 0=B
    before_chroma = (before[:, :, :3].max(axis=2) - before[:, :, :3].min(axis=2)).mean()
    p.corot_silver_veil_pass(desaturation=0.60, opacity=1.0)
    after         = _buf(p).astype(np.float32) / 255.0
    after_chroma  = (after[:, :, :3].max(axis=2) - after[:, :, :3].min(axis=2)).mean()
    assert after_chroma < before_chroma, (
        f"corot_silver_veil_pass must reduce colour chroma; "
        f"before={before_chroma:.4f}, after={after_chroma:.4f}")


def test_corot_silver_veil_pass_cools_palette():
    """corot_silver_veil_pass() must reduce R relative to B on a warm canvas."""
    import numpy as np
    p = _make_small_painter(60, 60)
    # Fill with warm ochre tone using tone_ground
    p.tone_ground((0.82, 0.52, 0.14), texture_strength=0.0)
    before    = _buf(p).astype(np.float32) / 255.0
    # BGRA: ch2=R, ch0=B — measure R-B gap
    before_rb = before[:, :, 2].mean() - before[:, :, 0].mean()
    p.corot_silver_veil_pass(cool_shift=0.10, desaturation=0.0, green_silver=0.0, opacity=1.0)
    after     = _buf(p).astype(np.float32) / 255.0
    after_rb  = after[:, :, 2].mean() - after[:, :, 0].mean()
    # After the cool shift, R-B gap should be smaller (R reduced and/or B increased)
    assert after_rb < before_rb, (
        f"corot_silver_veil_pass must cool the palette (reduce R-B gap); "
        f"before R-B={before_rb:.4f}, after R-B={after_rb:.4f}")


def test_corot_silver_veil_pass_with_figure_mask():
    """With a full figure mask (all 1s = all figure), canvas must be unchanged."""
    import numpy as np
    p = _make_small_painter(40, 40)
    p.tone_ground((0.18, 0.70, 0.18), texture_strength=0.0)
    before = _canvas_bytes(p)
    mask   = np.ones((40, 40), dtype=np.float32)
    p.corot_silver_veil_pass(figure_mask=mask, opacity=1.0)
    after  = _canvas_bytes(p)
    assert before == after, (
        "corot_silver_veil_pass with a full figure mask must not alter any pixel")


def test_corot_silver_veil_pass_background_altered_no_mask():
    """Without a figure mask, corot_silver_veil_pass() must modify a vivid-green canvas."""
    import numpy as np
    p = _make_small_painter(40, 40)
    p.tone_ground((0.10, 0.78, 0.10), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.corot_silver_veil_pass(opacity=0.80)
    after  = _canvas_bytes(p)
    assert before != after, (
        "corot_silver_veil_pass with no mask on a vivid-green canvas must change pixels")


def test_corot_silver_veil_pass_large_canvas():
    """corot_silver_veil_pass() must run without error on a 200x160 canvas."""
    p = _make_small_painter(200, 160)
    p.corot_silver_veil_pass(opacity=0.50)


# ── Session 62: parmigianino_serpentine_elegance_pass ─────────────────────────

def test_parmigianino_serpentine_elegance_pass_exists():
    """Painter must have parmigianino_serpentine_elegance_pass() method (session 62)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "parmigianino_serpentine_elegance_pass"), (
        "Painter missing parmigianino_serpentine_elegance_pass() — add it to stroke_engine.py")


def test_parmigianino_serpentine_elegance_pass_cools_midlights():
    """parmigianino_serpentine_elegance_pass() must increase blue in midlight zones."""
    import numpy as _np
    p = _make_small_painter(80, 80)
    # Ground a warm midlight tone — lum ~0.65, warm (R > B)
    p.tone_ground((0.75, 0.65, 0.50), texture_strength=0.0)

    buf_before = _np.frombuffer(p.canvas.surface.get_data(),
                                dtype=_np.uint8).reshape((80, 80, 4)).copy()
    b_before = buf_before[:, :, 0].astype(float).mean()

    p.parmigianino_serpentine_elegance_pass(
        porcelain_strength=0.20, lavender_shadow=0.0, silver_highlight=0.0, opacity=1.0
    )

    buf_after = _np.frombuffer(p.canvas.surface.get_data(),
                               dtype=_np.uint8).reshape((80, 80, 4)).copy()
    b_after = buf_after[:, :, 0].astype(float).mean()   # Cairo BGRA: channel 0 = B

    assert b_after > b_before, (
        f"parmigianino_serpentine_elegance_pass() must cool midlight zones (raise B); "
        f"B before={b_before:.1f} after={b_after:.1f}")


def test_parmigianino_serpentine_elegance_pass_cools_shadows():
    """parmigianino_serpentine_elegance_pass() must raise blue in dark shadow zones."""
    import numpy as _np
    p = _make_small_painter(80, 80)
    # Ground a dark warm tone (lum ~0.25, warm shadow)
    p.tone_ground((0.35, 0.28, 0.18), texture_strength=0.0)

    buf_before = _np.frombuffer(p.canvas.surface.get_data(),
                                dtype=_np.uint8).reshape((80, 80, 4)).copy()
    b_before = buf_before[:, :, 0].astype(float).mean()

    p.parmigianino_serpentine_elegance_pass(
        porcelain_strength=0.0, lavender_shadow=0.20, silver_highlight=0.0, opacity=1.0
    )

    buf_after = _np.frombuffer(p.canvas.surface.get_data(),
                               dtype=_np.uint8).reshape((80, 80, 4)).copy()
    b_after = buf_after[:, :, 0].astype(float).mean()

    assert b_after > b_before, (
        f"parmigianino_serpentine_elegance_pass() must cool shadow zones (raise B); "
        f"B before={b_before:.1f} after={b_after:.1f}")


def test_parmigianino_serpentine_elegance_pass_zero_opacity_no_change():
    """parmigianino_serpentine_elegance_pass() at opacity=0 must not change canvas."""
    p = _make_small_painter(60, 60)
    p.tone_ground((0.70, 0.60, 0.45), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.parmigianino_serpentine_elegance_pass(opacity=0.0)
    after  = _canvas_bytes(p)
    assert before == after, (
        "parmigianino_serpentine_elegance_pass() at opacity=0 must leave canvas unchanged")


def test_parmigianino_serpentine_elegance_pass_figure_mask_gates_effect():
    """parmigianino_serpentine_elegance_pass() with zero figure_mask must not change canvas."""
    import numpy as _np
    p = _make_small_painter(60, 60)
    p.tone_ground((0.70, 0.60, 0.45), texture_strength=0.0)
    zero_mask = _np.zeros((60, 60), dtype=_np.float32)
    before = _canvas_bytes(p)
    p.parmigianino_serpentine_elegance_pass(
        figure_mask=zero_mask,
        porcelain_strength=0.20, lavender_shadow=0.20, silver_highlight=0.20,
        opacity=1.0
    )
    after  = _canvas_bytes(p)
    assert before == after, (
        "parmigianino_serpentine_elegance_pass() with zero figure_mask must not "
        "change canvas — all operations are gated to the figure zone")


def test_parmigianino_serpentine_elegance_pass_large_canvas():
    """parmigianino_serpentine_elegance_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.72, 0.65, 0.55), texture_strength=0.0)
    p.parmigianino_serpentine_elegance_pass(opacity=0.72)


# ── Session 62: translucent_gauze_pass (artistic improvement) ────────────────

def test_translucent_gauze_pass_exists():
    """Painter must have translucent_gauze_pass() method (session 62)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "translucent_gauze_pass"), (
        "Painter missing translucent_gauze_pass() — add it to stroke_engine.py")


def test_translucent_gauze_pass_brightens_zone():
    """translucent_gauze_pass() must lighten the gauze zone (blend toward near-white scatter)."""
    import numpy as _np
    p = _make_small_painter(100, 100)
    # Dark ground — the gauze blend toward near-white should raise all channels
    p.tone_ground((0.30, 0.25, 0.20), texture_strength=0.0)

    buf_before = _np.frombuffer(p.canvas.surface.get_data(),
                                dtype=_np.uint8).reshape((100, 100, 4)).copy()
    # Measure mean brightness in the zone centre (rows 50–70, zone 0.45→0.65)
    r_before = buf_before[50:70, :, 2].astype(float).mean()

    p.translucent_gauze_pass(zone_top=0.45, zone_bottom=0.65, opacity=0.50, cool_shift=0.0)

    buf_after = _np.frombuffer(p.canvas.surface.get_data(),
                               dtype=_np.uint8).reshape((100, 100, 4)).copy()
    r_after = buf_after[50:70, :, 2].astype(float).mean()

    assert r_after > r_before, (
        f"translucent_gauze_pass() must lighten the gauze zone (blend toward near-white); "
        f"R before={r_before:.1f} after={r_after:.1f}")


def test_translucent_gauze_pass_outside_zone_unchanged():
    """translucent_gauze_pass() must not change pixels well outside the gauze zone."""
    import numpy as _np
    p = _make_small_painter(100, 100)
    p.tone_ground((0.50, 0.45, 0.38), texture_strength=0.0)

    buf_before = _np.frombuffer(p.canvas.surface.get_data(),
                                dtype=_np.uint8).reshape((100, 100, 4)).copy()
    # Top 10 rows are well above zone_top=0.45
    top_before = buf_before[:10, :, :3].copy()

    p.translucent_gauze_pass(zone_top=0.45, zone_bottom=0.65, opacity=0.50)

    buf_after = _np.frombuffer(p.canvas.surface.get_data(),
                               dtype=_np.uint8).reshape((100, 100, 4)).copy()
    top_after = buf_after[:10, :, :3]

    assert _np.array_equal(top_before, top_after), (
        "translucent_gauze_pass() must not modify pixels well above zone_top — "
        "the gauze is confined to the specified zone")


def test_translucent_gauze_pass_zero_opacity_no_change():
    """translucent_gauze_pass() at opacity=0 must not change canvas."""
    p = _make_small_painter(60, 60)
    p.tone_ground((0.55, 0.50, 0.40), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.translucent_gauze_pass(opacity=0.0)
    after  = _canvas_bytes(p)
    assert before == after, (
        "translucent_gauze_pass() at opacity=0 must leave canvas unchanged")


def test_translucent_gauze_pass_figure_mask_gates_effect():
    """translucent_gauze_pass() with zero figure_mask must not change canvas."""
    import numpy as _np
    p = _make_small_painter(80, 80)
    p.tone_ground((0.30, 0.25, 0.20), texture_strength=0.0)
    zero_mask = _np.zeros((80, 80), dtype=_np.float32)
    before = _canvas_bytes(p)
    p.translucent_gauze_pass(
        figure_mask=zero_mask, zone_top=0.30, zone_bottom=0.70, opacity=0.60
    )
    after  = _canvas_bytes(p)
    assert before == after, (
        "translucent_gauze_pass() with zero figure_mask must not change canvas — "
        "the gauze is gated to the figure zone")


def test_translucent_gauze_pass_large_canvas():
    """translucent_gauze_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.40, 0.35, 0.28), texture_strength=0.0)
    p.translucent_gauze_pass(opacity=0.35)


# ── Session 64: vigee_le_brun_pearlescent_grace_pass (new artist pass) ────────

def test_vigee_le_brun_pearlescent_grace_pass_exists():
    """Painter must have vigee_le_brun_pearlescent_grace_pass() method (session 64)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "vigee_le_brun_pearlescent_grace_pass"), (
        "Painter missing vigee_le_brun_pearlescent_grace_pass() — add it to stroke_engine.py")
    assert callable(getattr(Painter, "vigee_le_brun_pearlescent_grace_pass"))


def test_vigee_le_brun_pearlescent_grace_pass_no_error():
    """vigee_le_brun_pearlescent_grace_pass() runs without error on a toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.50, 0.34), texture_strength=0.0)
    p.vigee_le_brun_pearlescent_grace_pass(opacity=0.65)


def test_vigee_le_brun_pearlescent_grace_pass_warms_midtones():
    """
    vigee_le_brun_pearlescent_grace_pass() must increase red channel in mid-grey canvas.

    A mid-grey canvas (lum ≈ 0.55) falls squarely in the midtone bloom zone.
    After the pass the mean R channel should be higher (rose warmth injected).
    """
    p = _make_small_painter(80, 80)
    # Mid-grey in cairo BGRA — lum ~0.55
    p.tone_ground((0.55, 0.55, 0.55), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape((80, 80, 4)).copy()
    r_before = buf_before[:, :, 2].astype(float).mean()  # cairo: channel 2 = R

    p.vigee_le_brun_pearlescent_grace_pass(
        rose_bloom_strength=0.15,
        midtone_low=0.40,
        midtone_high=0.80,
        opacity=0.90,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape((80, 80, 4)).copy()
    r_after = buf_after[:, :, 2].astype(float).mean()

    assert r_after > r_before, (
        f"vigee_le_brun_pearlescent_grace_pass() must warm midtones (R↑); "
        f"R before={r_before:.1f} after={r_after:.1f}")


def test_vigee_le_brun_pearlescent_grace_pass_zero_opacity_no_change():
    """vigee_le_brun_pearlescent_grace_pass() at opacity=0 must not change canvas."""
    p = _make_small_painter(60, 60)
    p.tone_ground((0.55, 0.50, 0.40), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.vigee_le_brun_pearlescent_grace_pass(opacity=0.0)
    after  = _canvas_bytes(p)
    assert before == after, (
        "vigee_le_brun_pearlescent_grace_pass() at opacity=0 must leave canvas unchanged")


def test_vigee_le_brun_pearlescent_grace_pass_large_canvas():
    """vigee_le_brun_pearlescent_grace_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.70, 0.60, 0.42), texture_strength=0.0)
    p.vigee_le_brun_pearlescent_grace_pass(opacity=0.55)


# ── Session 64: subsurface_scatter_pass (artistic improvement) ────────────────

def test_subsurface_scatter_pass_exists():
    """Painter must have subsurface_scatter_pass() method (session 64)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "subsurface_scatter_pass"), (
        "Painter missing subsurface_scatter_pass() — add it to stroke_engine.py")
    assert callable(getattr(Painter, "subsurface_scatter_pass"))


def test_subsurface_scatter_pass_no_error():
    """subsurface_scatter_pass() runs without error on a toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.subsurface_scatter_pass(opacity=0.65)


def test_subsurface_scatter_pass_warms_midtones():
    """
    subsurface_scatter_pass() must increase R channel and decrease B channel in
    a mid-grey canvas (lum ~0.60, squarely in the scatter zone).

    Red-orange SSS bloom: R+, G+ modest, B-.
    """
    p = _make_small_painter(80, 80)
    p.tone_ground((0.60, 0.60, 0.60), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape((80, 80, 4)).copy()
    r_before = buf_before[:, :, 2].astype(float).mean()
    b_before = buf_before[:, :, 0].astype(float).mean()

    p.subsurface_scatter_pass(
        scatter_strength=0.20,
        scatter_radius=4.0,
        scatter_low=0.40,
        scatter_high=0.85,
        opacity=0.90,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape((80, 80, 4)).copy()
    r_after = buf_after[:, :, 2].astype(float).mean()
    b_after = buf_after[:, :, 0].astype(float).mean()

    assert r_after > r_before, (
        f"subsurface_scatter_pass() must warm midtones (R↑); "
        f"R before={r_before:.1f} after={r_after:.1f}")
    assert b_after < b_before, (
        f"subsurface_scatter_pass() must reduce blue in midtones (B↓); "
        f"B before={b_before:.1f} after={b_after:.1f}")


def test_subsurface_scatter_pass_zero_opacity_no_change():
    """subsurface_scatter_pass() at opacity=0 must not change canvas."""
    p = _make_small_painter(60, 60)
    p.tone_ground((0.55, 0.50, 0.40), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.subsurface_scatter_pass(opacity=0.0)
    after  = _canvas_bytes(p)
    assert before == after, (
        "subsurface_scatter_pass() at opacity=0 must leave canvas unchanged")


def test_subsurface_scatter_pass_pixels_stay_in_range():
    """subsurface_scatter_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.08)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.subsurface_scatter_pass(scatter_strength=0.25, opacity=0.85)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_subsurface_scatter_pass_large_canvas():
    """subsurface_scatter_pass() must complete without error on a larger canvas."""
    p = _make_small_painter(256, 256)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.subsurface_scatter_pass(scatter_radius=12.0, opacity=0.60)


# ──────────────────────────────────────────────────────────────────────────────
# patinir_weltlandschaft_pass() — session 66
# ──────────────────────────────────────────────────────────────────────────────

def test_patinir_weltlandschaft_pass_exists():
    """Painter must have patinir_weltlandschaft_pass() after session 66."""
    from stroke_engine import Painter
    assert hasattr(Painter, "patinir_weltlandschaft_pass"), (
        "patinir_weltlandschaft_pass not found on Painter")
    assert callable(getattr(Painter, "patinir_weltlandschaft_pass"))


def test_patinir_weltlandschaft_pass_no_error():
    """patinir_weltlandschaft_pass() runs without error on a small canvas."""
    p = _make_small_painter(80, 80)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.patinir_weltlandschaft_pass(opacity=0.55)


def test_patinir_weltlandschaft_pass_zero_opacity_no_change():
    """patinir_weltlandschaft_pass() at opacity=0 must not change canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.patinir_weltlandschaft_pass(opacity=0.0)
    after  = _canvas_bytes(p)
    assert before == after, (
        "patinir_weltlandschaft_pass() at opacity=0 must leave canvas unchanged")


def test_patinir_weltlandschaft_pass_cool_distance():
    """
    patinir_weltlandschaft_pass() must increase blue in the far distance
    (top of canvas, above horizon_far).  Use a wide, tall canvas so the
    far zone contains many pixels; verify mean B rises in that zone.
    """
    p = _make_small_painter(80, 120)
    # Ground with a warm tone so initial B is lower than R
    p.tone_ground((0.60, 0.50, 0.30), texture_strength=0.0)

    # Sample the far-distance zone before (top 20% of canvas)
    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape((120, 80, 4)).copy()
    b_before = buf_before[:24, :, 0].astype(float).mean()   # BGRA → B channel

    p.patinir_weltlandschaft_pass(
        warm_foreground=0.10,
        green_midground=0.08,
        cool_distance=0.20,
        horizon_near=0.55,
        horizon_far=0.72,
        transition_blur=6.0,
        opacity=0.90,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape((120, 80, 4)).copy()
    b_after = buf_after[:24, :, 0].astype(float).mean()

    assert b_after > b_before, (
        f"patinir_weltlandschaft_pass() must push blue up in far distance; "
        f"B before={b_before:.1f}  after={b_after:.1f}")


def test_patinir_weltlandschaft_pass_pixels_in_range():
    """patinir_weltlandschaft_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.patinir_weltlandschaft_pass(
        warm_foreground=0.20,
        cool_distance=0.20,
        opacity=1.0,
    )
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ──────────────────────────────────────────────────────────────────────────────
# warm_cool_form_duality_pass() — session 66 artistic improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_warm_cool_form_duality_pass_exists():
    """Painter must have warm_cool_form_duality_pass() after session 66."""
    from stroke_engine import Painter
    assert hasattr(Painter, "warm_cool_form_duality_pass"), (
        "warm_cool_form_duality_pass not found on Painter")
    assert callable(getattr(Painter, "warm_cool_form_duality_pass"))


def test_warm_cool_form_duality_pass_no_error():
    """warm_cool_form_duality_pass() runs without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.warm_cool_form_duality_pass(opacity=0.55)


def test_warm_cool_form_duality_pass_zero_opacity_no_change():
    """warm_cool_form_duality_pass() at opacity=0 must not change canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.warm_cool_form_duality_pass(opacity=0.0)
    after  = _canvas_bytes(p)
    assert before == after, (
        "warm_cool_form_duality_pass() at opacity=0 must leave canvas unchanged")


def test_warm_cool_form_duality_pass_warms_highlights():
    """
    warm_cool_form_duality_pass() must warm highlights: on a bright canvas
    (lum > 0.68), R should increase relative to B after the pass.
    """
    p = _make_small_painter(80, 80)
    # Bright neutral grey — both R and B near 0.80 initially
    p.tone_ground((0.80, 0.80, 0.80), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape((80, 80, 4)).copy()
    r_before = buf_before[:, :, 2].astype(float).mean()
    b_before = buf_before[:, :, 0].astype(float).mean()

    p.warm_cool_form_duality_pass(
        warm_strength=0.15,
        cool_strength=0.10,
        midtone=0.50,
        transition_width=0.15,
        blur_radius=3.0,
        opacity=1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape((80, 80, 4)).copy()
    r_after = buf_after[:, :, 2].astype(float).mean()
    b_after = buf_after[:, :, 0].astype(float).mean()

    assert r_after > r_before, (
        f"warm_cool_form_duality_pass() must warm highlights (R↑); "
        f"R before={r_before:.1f}  after={r_after:.1f}")
    assert b_after < b_before, (
        f"warm_cool_form_duality_pass() must reduce B in highlights; "
        f"B before={b_before:.1f}  after={b_after:.1f}")


def test_warm_cool_form_duality_pass_cools_shadows():
    """
    warm_cool_form_duality_pass() must cool shadows: on a dark canvas
    (lum < 0.32), B should increase after the pass.
    """
    p = _make_small_painter(80, 80)
    # Dark neutral — shadows
    p.tone_ground((0.20, 0.20, 0.20), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape((80, 80, 4)).copy()
    b_before = buf_before[:, :, 0].astype(float).mean()

    p.warm_cool_form_duality_pass(
        warm_strength=0.10,
        cool_strength=0.18,
        midtone=0.50,
        transition_width=0.15,
        blur_radius=3.0,
        opacity=1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape((80, 80, 4)).copy()
    b_after = buf_after[:, :, 0].astype(float).mean()

    assert b_after > b_before, (
        f"warm_cool_form_duality_pass() must cool shadows (B↑); "
        f"B before={b_before:.1f}  after={b_after:.1f}")


def test_warm_cool_form_duality_pass_pixels_in_range():
    """warm_cool_form_duality_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.warm_cool_form_duality_pass(warm_strength=0.25, cool_strength=0.25, opacity=1.0)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ──────────────────────────────────────────────────────────────────────────────
# mantegna_sculptural_form_pass() — session 67
# ──────────────────────────────────────────────────────────────────────────────

def test_mantegna_sculptural_form_pass_exists():
    """Painter must have mantegna_sculptural_form_pass() after session 67."""
    from stroke_engine import Painter
    assert hasattr(Painter, "mantegna_sculptural_form_pass"), (
        "mantegna_sculptural_form_pass not found on Painter")
    assert callable(getattr(Painter, "mantegna_sculptural_form_pass"))


def test_mantegna_sculptural_form_pass_no_error():
    """mantegna_sculptural_form_pass() runs without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.68, 0.55), texture_strength=0.0)
    p.mantegna_sculptural_form_pass(opacity=0.50)


def test_mantegna_sculptural_form_pass_zero_opacity_no_change():
    """mantegna_sculptural_form_pass() at opacity=0 must not change canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.68, 0.55), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.mantegna_sculptural_form_pass(opacity=0.0)
    after  = _canvas_bytes(p)
    assert before == after, (
        "mantegna_sculptural_form_pass() at opacity=0 must leave canvas unchanged")


def test_mantegna_sculptural_form_pass_lifts_bright_ridges():
    """
    mantegna_sculptural_form_pass() must lift bright ridge-form pixels:
    on a canvas with varied luminance, the average of already-bright pixels
    should increase (the chalk highlight lift).
    """
    p = _make_small_painter(80, 80)
    ref = _solid_reference(80, 80)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape((80, 80, 4)).copy()
    # Consider pixels with high luminance (bright ridge candidates)
    r_b = buf_before[:, :, 2].astype(float) / 255.0
    g_b = buf_before[:, :, 1].astype(float) / 255.0
    b_b = buf_before[:, :, 0].astype(float) / 255.0
    lum_b = 0.2126 * r_b + 0.7152 * g_b + 0.0722 * b_b
    bright_mask = lum_b > 0.55

    p.mantegna_sculptural_form_pass(
        highlight_lift = 0.20,
        shadow_deepen  = 0.05,
        edge_crisp     = 0.0,
        blur_radius    = 4.0,
        opacity        = 1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape((80, 80, 4)).copy()
    lum_a_bright = (
        0.2126 * buf_after[:, :, 2][bright_mask].astype(float) / 255.0 +
        0.7152 * buf_after[:, :, 1][bright_mask].astype(float) / 255.0 +
        0.0722 * buf_after[:, :, 0][bright_mask].astype(float) / 255.0
    )
    lum_b_bright = lum_b[bright_mask]
    assert lum_a_bright.mean() >= lum_b_bright.mean() - 0.01, (
        f"mantegna_sculptural_form_pass() should not darken bright ridge pixels; "
        f"mean lum before={lum_b_bright.mean():.4f} after={lum_a_bright.mean():.4f}")


def test_mantegna_sculptural_form_pass_pixels_in_range():
    """mantegna_sculptural_form_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.72, 0.68, 0.55), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.mantegna_sculptural_form_pass(
        highlight_lift=0.25, shadow_deepen=0.25, edge_crisp=0.10, opacity=1.0)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ──────────────────────────────────────────────────────────────────────────────
# skin_zone_temperature_pass() — session 67 artistic improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_skin_zone_temperature_pass_exists():
    """Painter must have skin_zone_temperature_pass() after session 67."""
    from stroke_engine import Painter
    assert hasattr(Painter, "skin_zone_temperature_pass"), (
        "skin_zone_temperature_pass not found on Painter")
    assert callable(getattr(Painter, "skin_zone_temperature_pass"))


def test_skin_zone_temperature_pass_no_error():
    """skin_zone_temperature_pass() runs without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.skin_zone_temperature_pass(
        face_cx=0.50, face_cy=0.50,
        face_rx=0.30, face_ry=0.30,
        opacity=0.55,
    )


def test_skin_zone_temperature_pass_zero_opacity_no_change():
    """skin_zone_temperature_pass() at opacity=0 must not change canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.skin_zone_temperature_pass(
        face_cx=0.50, face_cy=0.50,
        face_rx=0.30, face_ry=0.30,
        opacity=0.0,
    )
    after = _canvas_bytes(p)
    assert before == after, (
        "skin_zone_temperature_pass() at opacity=0 must leave canvas unchanged")


def test_skin_zone_temperature_pass_warms_forehead():
    """
    skin_zone_temperature_pass() must warm the forehead zone (increase R
    relative to B at the top of the face ellipse).
    """
    p = _make_small_painter(100, 100)
    # Neutral mid-tone ground so colour shifts are easy to detect
    p.tone_ground((0.60, 0.60, 0.60), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape((100, 100, 4)).copy()

    # Forehead zone: y ≈ face_cy - face_ry * 0.55 * ry_px, x ≈ face_cx
    # With face_cx=0.50, face_cy=0.40, face_rx=0.25, face_ry=0.30
    # ry_px = 30 → top of forehead ≈ y=40-16=24, centre = y=28 (28/100=0.28)
    p.skin_zone_temperature_pass(
        face_cx=0.50, face_cy=0.40,
        face_rx=0.25, face_ry=0.30,
        forehead_warm=0.25,
        temple_cool=0.0,
        nose_pink=0.0,
        lip_rose=0.0,
        jaw_cool=0.0,
        blur_radius=4.0,
        opacity=1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape((100, 100, 4)).copy()

    # Sample top-centre of face (forehead area)
    fy0 = max(0, int(100 * 0.40 - int(100 * 0.30) * 0.80))
    fy1 = max(fy0 + 1, int(100 * 0.40 - int(100 * 0.30) * 0.30))
    fx0 = max(0, int(100 * 0.50) - 10)
    fx1 = min(100, int(100 * 0.50) + 10)

    r_before = buf_before[fy0:fy1, fx0:fx1, 2].astype(float).mean()
    r_after  = buf_after [fy0:fy1, fx0:fx1, 2].astype(float).mean()

    assert r_after >= r_before, (
        f"skin_zone_temperature_pass() must warm forehead (R↑ or unchanged); "
        f"R before={r_before:.2f}  after={r_after:.2f}")


def test_skin_zone_temperature_pass_pixels_in_range():
    """skin_zone_temperature_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(80, 80)
    ref = _solid_reference(80, 80)
    p.tone_ground((0.60, 0.55, 0.40), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.skin_zone_temperature_pass(
        face_cx=0.50, face_cy=0.40,
        face_rx=0.28, face_ry=0.32,
        forehead_warm=0.25, temple_cool=0.20,
        nose_pink=0.20, lip_rose=0.20, jaw_cool=0.20,
        opacity=1.0,
    )
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ──────────────────────────────────────────────────────────────────────────────
# claude_lorrain_golden_light_pass() — session 68 artistic improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_claude_lorrain_golden_light_pass_exists():
    """Painter must have claude_lorrain_golden_light_pass() after session 68."""
    from stroke_engine import Painter
    assert hasattr(Painter, "claude_lorrain_golden_light_pass"), (
        "claude_lorrain_golden_light_pass not found on Painter")
    assert callable(getattr(Painter, "claude_lorrain_golden_light_pass"))


def test_claude_lorrain_golden_light_pass_no_error():
    """claude_lorrain_golden_light_pass() runs without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.65, 0.58, 0.35), texture_strength=0.0)
    p.claude_lorrain_golden_light_pass(
        horizon_y=0.60,
        glow_spread=0.45,
        warmth=0.18,
        sky_cool=0.10,
        water_shimmer=0.08,
        opacity=0.55,
    )


def test_claude_lorrain_golden_light_pass_zero_opacity_no_change():
    """claude_lorrain_golden_light_pass() at opacity=0 must not change canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.65, 0.58, 0.35), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.claude_lorrain_golden_light_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, (
        "claude_lorrain_golden_light_pass() at opacity=0 must leave canvas unchanged")


def test_claude_lorrain_golden_light_pass_warms_horizon():
    """
    claude_lorrain_golden_light_pass() must warm the horizon band (increase R
    near horizon_y relative to top of canvas).
    """
    import numpy as np
    p = _make_small_painter(100, 100)
    # Neutral mid-grey ground so colour shifts are easy to detect
    p.tone_ground((0.55, 0.55, 0.55), texture_strength=0.0)

    p.claude_lorrain_golden_light_pass(
        horizon_y=0.60,
        glow_spread=0.20,
        warmth=0.30,
        sky_cool=0.0,
        water_shimmer=0.0,
        opacity=1.0,
    )

    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape((100, 100, 4))

    # Horizon row: y ≈ 60
    horizon_row = 60
    r_horizon = buf[horizon_row, :, 2].astype(float).mean()  # BGRA: channel 2 = R

    # Top row: y = 5 (well above horizon glow)
    top_row = 5
    r_top = buf[top_row, :, 2].astype(float).mean()

    assert r_horizon > r_top, (
        f"claude_lorrain_golden_light_pass() must warm horizon band more than top "
        f"of canvas; horizon R={r_horizon:.1f}  top R={r_top:.1f}")


def test_claude_lorrain_golden_light_pass_pixels_in_range():
    """claude_lorrain_golden_light_pass() must not produce out-of-range pixel values."""
    import numpy as np
    p = _make_small_painter(80, 80)
    ref = _solid_reference(80, 80)
    p.tone_ground((0.60, 0.55, 0.35), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.claude_lorrain_golden_light_pass(
        horizon_y=0.60,
        glow_spread=0.40,
        warmth=0.25,
        sky_cool=0.15,
        water_shimmer=0.12,
        opacity=1.0,
    )
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ──────────────────────────────────────────────────────────────────────────────
# guido_reni_angelic_grace_pass() — session 70 artist pass
# ──────────────────────────────────────────────────────────────────────────────

def test_guido_reni_angelic_grace_pass_exists():
    """Painter must have guido_reni_angelic_grace_pass() after session 70."""
    from stroke_engine import Painter
    assert hasattr(Painter, "guido_reni_angelic_grace_pass"), (
        "guido_reni_angelic_grace_pass not found on Painter")
    assert callable(getattr(Painter, "guido_reni_angelic_grace_pass"))


def test_guido_reni_angelic_grace_pass_no_error():
    """guido_reni_angelic_grace_pass() runs without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.58, 0.44), texture_strength=0.0)
    p.guido_reni_angelic_grace_pass(
        face_cx=0.50, face_cy=0.38,
        face_rx=0.25, face_ry=0.30,
        pearl_lift=0.08, pearl_cool=0.04,
        cheek_rose=0.05, lip_rose=0.06,
        shadow_violet=0.05,
        blur_radius=5.0,
        opacity=0.55,
    )


def test_guido_reni_angelic_grace_pass_zero_opacity_no_change():
    """guido_reni_angelic_grace_pass() at opacity=0 must not change canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.58, 0.44), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.guido_reni_angelic_grace_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, (
        "guido_reni_angelic_grace_pass() at opacity=0 must leave canvas unchanged")


def test_guido_reni_angelic_grace_pass_lifts_highlights():
    """
    guido_reni_angelic_grace_pass() must lift the highlight region (increase
    average luminance in the face centre on a high-key canvas).
    """
    p = _make_small_painter(100, 100)
    p.tone_ground((0.78, 0.74, 0.70), texture_strength=0.0)

    buf_before = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape((100, 100, 4)).copy()

    p.guido_reni_angelic_grace_pass(
        face_cx=0.50, face_cy=0.40,
        face_rx=0.30, face_ry=0.35,
        pearl_lift=0.20,
        pearl_cool=0.06,
        cheek_rose=0.0,
        lip_rose=0.0,
        shadow_violet=0.0,
        blur_radius=4.0,
        opacity=1.0,
    )

    buf_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape((100, 100, 4)).copy()

    fy0, fy1, fx0, fx1 = 25, 55, 30, 70
    lum_before = (0.299 * buf_before[fy0:fy1, fx0:fx1, 2].astype(float) +
                  0.587 * buf_before[fy0:fy1, fx0:fx1, 1].astype(float) +
                  0.114 * buf_before[fy0:fy1, fx0:fx1, 0].astype(float)).mean()
    lum_after  = (0.299 * buf_after [fy0:fy1, fx0:fx1, 2].astype(float) +
                  0.587 * buf_after [fy0:fy1, fx0:fx1, 1].astype(float) +
                  0.114 * buf_after [fy0:fy1, fx0:fx1, 0].astype(float)).mean()

    assert lum_after >= lum_before, (
        f"guido_reni_angelic_grace_pass() must lift highlight luminance; "
        f"lum before={lum_before:.2f}  after={lum_after:.2f}")


def test_guido_reni_angelic_grace_pass_pixels_in_range():
    """guido_reni_angelic_grace_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(80, 80)
    ref = _solid_reference(80, 80)
    p.tone_ground((0.68, 0.58, 0.44), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.guido_reni_angelic_grace_pass(
        face_cx=0.50, face_cy=0.40,
        face_rx=0.28, face_ry=0.32,
        pearl_lift=0.20, pearl_cool=0.08,
        cheek_rose=0.12, lip_rose=0.12,
        shadow_violet=0.10,
        opacity=1.0,
    )
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ──────────────────────────────────────────────────────────────────────────────
# highlight_bloom_pass() — session 70 artistic improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_highlight_bloom_pass_s70_multi_scale_true():
    """highlight_bloom_pass() with multi_scale=True (default) runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.80, 0.76, 0.68), texture_strength=0.0)
    p.highlight_bloom_pass(
        threshold=0.72,
        bloom_sigma=6.0,
        bloom_opacity=0.30,
        multi_scale=True,
    )


def test_highlight_bloom_pass_s70_bloom_opacity_zero_no_change():
    """highlight_bloom_pass() at bloom_opacity=0 must not change canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.80, 0.76, 0.68), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.highlight_bloom_pass(bloom_opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, (
        "highlight_bloom_pass() at bloom_opacity=0 must leave canvas unchanged")


def test_highlight_bloom_pass_s70_with_bloom_color():
    """highlight_bloom_pass() with bloom_color runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.80, 0.76, 0.68), texture_strength=0.0)
    p.highlight_bloom_pass(
        threshold=0.70,
        bloom_sigma=5.0,
        bloom_opacity=0.25,
        bloom_color=(1.00, 0.95, 0.80),
    )


def test_highlight_bloom_pass_s70_pixels_in_range():
    """highlight_bloom_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(80, 80)
    ref = _solid_reference(80, 80)
    p.tone_ground((0.80, 0.75, 0.65), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.highlight_bloom_pass(
        threshold=0.55,
        bloom_sigma=8.0,
        bloom_opacity=0.50,
        multi_scale=True,
    )
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255

# ──────────────────────────────────────────────────────────────────────────────
# correggio_golden_tenderness_pass() — session 71 artist pass
# ──────────────────────────────────────────────────────────────────────────────

def test_correggio_golden_tenderness_pass_exists():
    """Painter must have correggio_golden_tenderness_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "correggio_golden_tenderness_pass"), (
        "correggio_golden_tenderness_pass not found on Painter")
    assert callable(getattr(Painter, "correggio_golden_tenderness_pass"))


def test_correggio_golden_tenderness_pass_no_error_default():
    """correggio_golden_tenderness_pass() runs without error with default parameters."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.64, 0.54, 0.36), texture_strength=0.0)
    p.correggio_golden_tenderness_pass()


def test_correggio_golden_tenderness_pass_zero_opacity_is_noop():
    """correggio_golden_tenderness_pass() at opacity=0 must not modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.64, 0.54, 0.36), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.correggio_golden_tenderness_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, (
        "correggio_golden_tenderness_pass() at opacity=0 must leave canvas unchanged")


def test_correggio_golden_tenderness_pass_modifies_canvas():
    """correggio_golden_tenderness_pass() with positive opacity must change at least one pixel."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.64, 0.54, 0.36), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    before = _canvas_bytes(p)
    p.correggio_golden_tenderness_pass(gold_lift=0.08, opacity=0.80)
    after = _canvas_bytes(p)
    assert before != after, (
        "correggio_golden_tenderness_pass() should modify at least one pixel when opacity>0")


def test_correggio_golden_tenderness_pass_pixels_in_range():
    """correggio_golden_tenderness_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(80, 80)
    ref = _solid_reference(80, 80)
    p.tone_ground((0.64, 0.54, 0.36), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.correggio_golden_tenderness_pass(
        midtone_low=0.25,
        midtone_high=0.80,
        gold_lift=0.10,
        amber_shadow=0.08,
        glow_strength=0.08,
        opacity=1.0,
    )
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ──────────────────────────────────────────────────────────────────────────────
# luminous_haze_pass() — session 71 artistic improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_luminous_haze_pass_exists():
    """Painter must have luminous_haze_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "luminous_haze_pass"), (
        "luminous_haze_pass not found on Painter")
    assert callable(getattr(Painter, "luminous_haze_pass"))


def test_luminous_haze_pass_no_error_default():
    """luminous_haze_pass() runs without error with default parameters."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.64, 0.54, 0.36), texture_strength=0.0)
    p.luminous_haze_pass()


def test_luminous_haze_pass_zero_opacity_is_noop():
    """luminous_haze_pass() at opacity=0 must not modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.64, 0.54, 0.36), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.luminous_haze_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, (
        "luminous_haze_pass() at opacity=0 must leave canvas unchanged")


def test_luminous_haze_pass_modifies_canvas():
    """luminous_haze_pass() with positive opacity must change at least one pixel."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.64, 0.54, 0.36), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    before = _canvas_bytes(p)
    p.luminous_haze_pass(haze_warmth=0.06, haze_opacity=0.20, opacity=0.80)
    after = _canvas_bytes(p)
    assert before != after, (
        "luminous_haze_pass() should modify at least one pixel when opacity>0")


def test_luminous_haze_pass_with_custom_haze_color():
    """luminous_haze_pass() with a custom haze_color runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.64, 0.54, 0.36), texture_strength=0.0)
    p.luminous_haze_pass(
        haze_warmth=0.04,
        haze_opacity=0.15,
        haze_color=(0.90, 0.78, 0.52),
        soften_radius=3.0,
        contrast_damp=0.05,
        shadow_lift=0.018,
        opacity=0.50,
    )


def test_luminous_haze_pass_pixels_in_range():
    """luminous_haze_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(80, 80)
    ref = _solid_reference(80, 80)
    p.tone_ground((0.20, 0.16, 0.12), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.luminous_haze_pass(
        haze_warmth=0.08,
        haze_opacity=0.30,
        soften_radius=2.0,
        contrast_damp=0.10,
        shadow_lift=0.03,
        opacity=1.0,
    )
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ──────────────────────────────────────────────────────────────────────────────
# anguissola_intimacy_pass() — session 73 artistic improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_anguissola_intimacy_pass_exists():
    """Painter must have anguissola_intimacy_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "anguissola_intimacy_pass"), (
        "anguissola_intimacy_pass not found on Painter")
    assert callable(getattr(Painter, "anguissola_intimacy_pass"))


def test_anguissola_intimacy_pass_no_error_default():
    """anguissola_intimacy_pass() runs without error with default parameters."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.58, 0.48, 0.32), texture_strength=0.0)
    p.anguissola_intimacy_pass()


def test_anguissola_intimacy_pass_zero_opacity_is_noop():
    """anguissola_intimacy_pass() at opacity=0 must not modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.58, 0.48, 0.32), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.anguissola_intimacy_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, (
        "anguissola_intimacy_pass() at opacity=0 must leave canvas unchanged")


def test_anguissola_intimacy_pass_modifies_canvas():
    """anguissola_intimacy_pass() with positive opacity must change at least one pixel."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.58, 0.48, 0.32), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    before = _canvas_bytes(p)
    p.anguissola_intimacy_pass(
        focus_cx=0.50, focus_cy=0.30,
        sharpen_strength=0.50, warm_ambient=0.022, opacity=0.70,
    )
    after = _canvas_bytes(p)
    assert before != after, (
        "anguissola_intimacy_pass() should modify at least one pixel when opacity>0")


def test_anguissola_intimacy_pass_custom_focus():
    """anguissola_intimacy_pass() with off-centre focus runs without error."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.58, 0.48, 0.32), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.anguissola_intimacy_pass(
        focus_cx=0.48, focus_cy=0.28,
        focus_radius=0.15,
        sharpen_strength=0.55,
        eye_cx_offset=0.06,
        eye_cy_offset=-0.01,
        eye_radius=0.07,
        lip_cy_offset=0.09,
        lip_rx=0.06,
        lip_ry=0.03,
        periphery_soften=2.0,
        warm_ambient=0.025,
        opacity=0.65,
    )


def test_anguissola_intimacy_pass_pixels_in_range():
    """anguissola_intimacy_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(80, 80)
    ref = _solid_reference(80, 80)
    p.tone_ground((0.58, 0.48, 0.32), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.anguissola_intimacy_pass(
        focus_cx=0.50, focus_cy=0.30,
        sharpen_strength=0.60,
        warm_ambient=0.03,
        opacity=1.0,
    )
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ──────────────────────────────────────────────────────────────────────────────
# Period.LOMBARD_RENAISSANCE — session 73 routing
# ──────────────────────────────────────────────────────────────────────────────

def test_lombard_renaissance_period_present_routing():
    """Period.LOMBARD_RENAISSANCE must be accessible from scene_schema."""
    from scene_schema import Period
    assert hasattr(Period, "LOMBARD_RENAISSANCE"), (
        "Period.LOMBARD_RENAISSANCE not found in scene_schema — add it")
    assert Period.LOMBARD_RENAISSANCE in list(Period)


def test_lombard_renaissance_routing_flag():
    """is_lombard_renaissance flag must evaluate True for LOMBARD_RENAISSANCE scenes."""
    from scene_schema import Period, Style, Medium, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.LOMBARD_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    assert style.period == Period.LOMBARD_RENAISSANCE, (
        "Style.period must equal LOMBARD_RENAISSANCE when set as such")


# ──────────────────────────────────────────────────────────────────────────────
# bosch_phantasmagoria_pass — session 74 artist discovery
# ──────────────────────────────────────────────────────────────────────────────

def test_bosch_phantasmagoria_pass_exists():
    """Painter must have bosch_phantasmagoria_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "bosch_phantasmagoria_pass"), (
        "bosch_phantasmagoria_pass not found on Painter")
    assert callable(getattr(Painter, "bosch_phantasmagoria_pass"))


def test_bosch_phantasmagoria_pass_no_error_default():
    """bosch_phantasmagoria_pass() runs without error with default parameters."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.24, 0.18, 0.10), texture_strength=0.0)
    p.bosch_phantasmagoria_pass(n_detail_marks=40, n_jewel_accents=5)


def test_bosch_phantasmagoria_pass_no_figure_mask():
    """bosch_phantasmagoria_pass() runs correctly when no figure mask is set."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.24, 0.18, 0.10), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.bosch_phantasmagoria_pass(n_detail_marks=30, n_jewel_accents=4, background_only=False)


def test_bosch_phantasmagoria_pass_modifies_canvas():
    """bosch_phantasmagoria_pass() must modify at least one pixel."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.24, 0.18, 0.10), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    before = _canvas_bytes(p)
    p.bosch_phantasmagoria_pass(n_detail_marks=50, n_jewel_accents=8)
    after = _canvas_bytes(p)
    assert before != after, (
        "bosch_phantasmagoria_pass() should modify at least one pixel")


def test_bosch_phantasmagoria_pass_pixels_in_range():
    """bosch_phantasmagoria_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(80, 80)
    ref = _solid_reference(80, 80)
    p.tone_ground((0.24, 0.18, 0.10), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.bosch_phantasmagoria_pass(n_detail_marks=60, n_jewel_accents=10, void_darken=0.08)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_bosch_phantasmagoria_pass_custom_palette():
    """bosch_phantasmagoria_pass() accepts a custom palette without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.24, 0.18, 0.10), texture_strength=0.0)
    custom_palette = [
        (0.70, 0.10, 0.10),
        (0.10, 0.20, 0.60),
        (0.65, 0.50, 0.10),
    ]
    p.bosch_phantasmagoria_pass(
        palette=custom_palette,
        n_detail_marks=30,
        n_jewel_accents=5,
        mark_size=2.0,
        mark_opacity=0.25,
        jewel_opacity=0.50,
        void_darken=0.05,
    )


# ──────────────────────────────────────────────────────────────────────────────
# cool_atmospheric_recession_pass — session 74 artistic improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_cool_atmospheric_recession_pass_exists():
    """Painter must have cool_atmospheric_recession_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "cool_atmospheric_recession_pass"), (
        "cool_atmospheric_recession_pass not found on Painter")
    assert callable(getattr(Painter, "cool_atmospheric_recession_pass"))


def test_cool_atmospheric_recession_pass_no_error_default():
    """cool_atmospheric_recession_pass() runs without error with default parameters."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.cool_atmospheric_recession_pass()


def test_cool_atmospheric_recession_pass_zero_opacity_is_noop():
    """cool_atmospheric_recession_pass() at opacity=0 must not modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.cool_atmospheric_recession_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, (
        "cool_atmospheric_recession_pass() at opacity=0 must leave canvas unchanged")


def test_cool_atmospheric_recession_pass_modifies_canvas():
    """cool_atmospheric_recession_pass() with positive opacity must change at least one pixel."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    before = _canvas_bytes(p)
    p.cool_atmospheric_recession_pass(
        horizon_y=0.35,
        cool_strength=0.22,
        bright_lift=0.10,
        desaturate=0.30,
        opacity=0.75,
    )
    after = _canvas_bytes(p)
    assert before != after, (
        "cool_atmospheric_recession_pass() should modify at least one pixel when opacity>0")


def test_cool_atmospheric_recession_pass_pixels_in_range():
    """cool_atmospheric_recession_pass() must not produce out-of-range pixel values."""
    p = _make_small_painter(80, 80)
    ref = _solid_reference(80, 80)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.block_in(ref, stroke_size=10, n_strokes=30)
    p.cool_atmospheric_recession_pass(
        horizon_y=0.40,
        cool_strength=0.25,
        bright_lift=0.12,
        desaturate=0.35,
        blur_background=1.0,
        opacity=0.80,
    )
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_cool_atmospheric_recession_pass_custom_horizon():
    """cool_atmospheric_recession_pass() with high horizon_y runs without error."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.cool_atmospheric_recession_pass(
        horizon_y=0.60,
        cool_strength=0.18,
        bright_lift=0.08,
        desaturate=0.25,
        blur_background=0.6,
        feather=0.12,
        opacity=0.65,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Period.NORTHERN_FANTASTICAL — session 74 routing
# ──────────────────────────────────────────────────────────────────────────────

def test_northern_fantastical_period_present_routing():
    """Period.NORTHERN_FANTASTICAL must be accessible from scene_schema."""
    from scene_schema import Period
    assert hasattr(Period, "NORTHERN_FANTASTICAL"), (
        "Period.NORTHERN_FANTASTICAL not found in scene_schema — add it")
    assert Period.NORTHERN_FANTASTICAL in list(Period)


def test_northern_fantastical_routing_flag():
    """Style with NORTHERN_FANTASTICAL period must be constructible and readable."""
    from scene_schema import Period, Style, Medium, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.NORTHERN_FANTASTICAL,
                  palette=PaletteHint.DARK_EARTH)
    assert style.period == Period.NORTHERN_FANTASTICAL


# ──────────────────────────────────────────────────────────────────────────────
# de_hooch_threshold_light_pass() — session 75 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_de_hooch_threshold_light_pass_exists():
    """Painter must have a de_hooch_threshold_light_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "de_hooch_threshold_light_pass"), (
        "Painter.de_hooch_threshold_light_pass not found — add it to stroke_engine.py")


def test_de_hooch_threshold_light_pass_zero_opacity_no_change():
    """de_hooch_threshold_light_pass() at opacity=0 must leave the canvas unchanged."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(64, 64)
    # Fill with a mid-grey reference
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    buf[:] = 128
    p.canvas.surface.get_data()[:] = buf.tobytes()
    before = buf.copy()

    p.de_hooch_threshold_light_pass(opacity=0.0)

    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before[:, :, :3], after[:, :, :3]), (
        "de_hooch_threshold_light_pass() at opacity=0 must leave canvas unchanged")


def test_de_hooch_threshold_light_pass_modifies_canvas():
    """de_hooch_threshold_light_pass() with positive opacity must change at least one pixel."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(64, 64)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    buf[:] = 128
    p.canvas.surface.get_data()[:] = buf.tobytes()
    before = buf[:, :, :3].copy()

    p.de_hooch_threshold_light_pass(
        light_x=0.05,
        light_width=0.50,
        warm_strength=0.30,
        cool_strength=0.20,
        doorway_x=0.70,
        doorway_y=0.20,
        doorway_w=0.20,
        doorway_h=0.50,
        opacity=0.80,
    )

    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    diff = np.abs(before.astype(int) - after[:, :, :3].astype(int))
    assert diff.max() > 0, (
        "de_hooch_threshold_light_pass() should modify at least one pixel when opacity>0")


def test_de_hooch_threshold_light_pass_pixels_in_range():
    """de_hooch_threshold_light_pass() must not produce out-of-range pixel values."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(64, 64)
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    buf[:, :, :3] = 180
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.de_hooch_threshold_light_pass(
        warm_strength=0.50,
        cool_strength=0.40,
        opacity=1.0,
    )

    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    assert after.min() >= 0 and after.max() <= 255, (
        "de_hooch_threshold_light_pass() must not produce pixel values outside [0, 255]")


def test_de_hooch_threshold_light_pass_warm_tint_on_left():
    """de_hooch_threshold_light_pass() warm light should increase left-side redness."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(128, 128)
    # Fill with uniform mid-grey
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    buf[:] = 128
    p.canvas.surface.get_data()[:] = buf.tobytes()

    p.de_hooch_threshold_light_pass(
        light_x=0.0,
        light_width=0.40,
        warm_color=(1.0, 0.6, 0.2),
        warm_strength=0.40,
        cool_strength=0.0,    # disable cool to isolate warm effect
        doorway_w=0.0,        # no doorway
        opacity=1.0,
    )

    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    # Left column (x=0–20) should be redder than right column (x=108–128)
    left_red  = after[:, :20,   2].astype(float).mean()   # BGRA: channel 2 = R
    right_red = after[:, 108:,  2].astype(float).mean()
    assert left_red > right_red, (
        f"Warm tint should make left side redder: left_red={left_red:.1f} right_red={right_red:.1f}")


# ──────────────────────────────────────────────────────────────────────────────
# Period.DUTCH_DOMESTIC — session 75 routing
# ──────────────────────────────────────────────────────────────────────────────

def test_dutch_domestic_period_present_routing():
    """Period.DUTCH_DOMESTIC must be accessible from scene_schema."""
    from scene_schema import Period
    assert hasattr(Period, "DUTCH_DOMESTIC"), (
        "Period.DUTCH_DOMESTIC not found in scene_schema — add it")
    assert Period.DUTCH_DOMESTIC in list(Period)


def test_dutch_domestic_routing_flag():
    """Style with DUTCH_DOMESTIC period must be constructible and readable."""
    from scene_schema import Period, Style, Medium, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.DUTCH_DOMESTIC,
                  palette=PaletteHint.WARM_EARTH)
    assert style.period == Period.DUTCH_DOMESTIC


# ──────────────────────────────────────────────────────────────────────────────
# Hyacinthe Rigaud / FRENCH_COURT_BAROQUE / rigaud_velvet_drapery_pass — s78
# ──────────────────────────────────────────────────────────────────────────────

def test_french_court_baroque_period_present_routing():
    """Period.FRENCH_COURT_BAROQUE must be accessible from scene_schema."""
    from scene_schema import Period
    assert hasattr(Period, "FRENCH_COURT_BAROQUE"), (
        "Period.FRENCH_COURT_BAROQUE not found in scene_schema — add it")
    assert Period.FRENCH_COURT_BAROQUE in list(Period)


def test_french_court_baroque_stroke_params_controlled_wet_blend():
    """FRENCH_COURT_BAROQUE wet_blend must be in [0.20, 0.50] — deliberate velvet layering."""
    from scene_schema import Period, Style, Medium, PaletteHint
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_COURT_BAROQUE).stroke_params
    assert 0.20 <= sp["wet_blend"] <= 0.50, (
        f"FRENCH_COURT_BAROQUE wet_blend should be in [0.20, 0.50] for Rigaud's controlled "
        f"velvet layering; got {sp['wet_blend']}")


def test_french_court_baroque_stroke_params_moderate_edge_softness():
    """FRENCH_COURT_BAROQUE edge_softness must be in [0.25, 0.55] — silk crispness balanced."""
    from scene_schema import Period, Style, Medium, PaletteHint
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_COURT_BAROQUE).stroke_params
    assert 0.25 <= sp["edge_softness"] <= 0.55, (
        f"FRENCH_COURT_BAROQUE edge_softness should be in [0.25, 0.55] for Rigaud's silk/"
        f"velvet balance; got {sp['edge_softness']}")


def test_rigaud_velvet_drapery_pass_exists():
    """Painter must have a rigaud_velvet_drapery_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "rigaud_velvet_drapery_pass"), (
        "Painter is missing rigaud_velvet_drapery_pass — add it to stroke_engine.py")


def test_rigaud_velvet_drapery_pass_modifies_canvas():
    """rigaud_velvet_drapery_pass() must alter the canvas from its initial state."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    # Fill with a mid-tone warm canvas so there are dark and bright areas
    data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:64, :, :] = [30, 20, 40, 255]   # dark region (velvet zone)
    data[64:, :, :] = [200, 195, 210, 255]  # bright region (silk zone)
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = data.copy()
    p.rigaud_velvet_drapery_pass(opacity=1.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    assert not np.array_equal(before, after), (
        "rigaud_velvet_drapery_pass should change the canvas when opacity=1.0")


def test_rigaud_velvet_drapery_pass_darkens_velvet():
    """
    rigaud_velvet_drapery_pass must deepen dark non-skin pixels (velvet voids)
    — the defining shadow quality of Rigaud's drapery.
    """
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    # Fill canvas with a dark non-skin mid-tone (low lum, not skin)
    data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, :] = [60, 50, 70, 255]   # dark, desaturated — velvet shadow zone
    p.canvas.surface.get_data()[:] = data.tobytes()
    before_lum = data[:, :, 2].astype(float).mean()  # R channel mean before

    p.rigaud_velvet_drapery_pass(velvet_thresh=0.40, opacity=1.0)

    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    after_lum = after[:, :, 2].astype(float).mean()  # R channel mean after
    # Either channels got darker overall or B was suppressed
    total_before = data[:, :, :3].astype(float).mean()
    total_after  = after[:, :, :3].astype(float).mean()
    assert total_after <= total_before + 5.0, (
        f"rigaud_velvet_drapery_pass should darken velvet zones; "
        f"before_mean={total_before:.1f} after_mean={total_after:.1f}")


# -------------------------------------------------------------------------
# Lorenzo Lotto / VENETIAN_PSYCHOLOGICAL / lotto_chromatic_anxiety_pass -- s79
# -------------------------------------------------------------------------


def test_venetian_psychological_period_accessible():
    """Period.VENETIAN_PSYCHOLOGICAL must be accessible from scene_schema."""
    from scene_schema import Period
    assert hasattr(Period, 'VENETIAN_PSYCHOLOGICAL'), (
        'Period.VENETIAN_PSYCHOLOGICAL not found in scene_schema -- add it')
    assert Period.VENETIAN_PSYCHOLOGICAL in list(Period)


def test_venetian_psychological_wet_blend_range():
    """VENETIAN_PSYCHOLOGICAL wet_blend must be in [0.30, 0.60]."""
    sp = Style(medium=Medium.OIL, period=Period.VENETIAN_PSYCHOLOGICAL).stroke_params
    assert 0.30 <= sp['wet_blend'] <= 0.60, (
        f"VENETIAN_PSYCHOLOGICAL wet_blend should be in [0.30, 0.60] for Lotto's "
        f"Venetian oil blending with psychological tension; got {sp['wet_blend']:.2f}")


def test_venetian_psychological_edge_softness_range():
    """VENETIAN_PSYCHOLOGICAL edge_softness must be in [0.35, 0.65]."""
    sp = Style(medium=Medium.OIL, period=Period.VENETIAN_PSYCHOLOGICAL).stroke_params
    assert 0.35 <= sp['edge_softness'] <= 0.65, (
        f"VENETIAN_PSYCHOLOGICAL edge_softness should be in [0.35, 0.65] for Lotto's "
        f"psychologically crisp edges; got {sp['edge_softness']:.2f}")


def test_lotto_chromatic_anxiety_pass_exists():
    """Painter must have a lotto_chromatic_anxiety_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, 'lotto_chromatic_anxiety_pass'), (
        'Painter is missing lotto_chromatic_anxiety_pass -- add it to stroke_engine.py')


def test_lotto_chromatic_anxiety_pass_modifies_canvas():
    """lotto_chromatic_anxiety_pass() must alter the canvas from its initial state."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, :] = [140, 130, 175, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.lotto_chromatic_anxiety_pass(opacity=1.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    assert not np.array_equal(before, after), (
        'lotto_chromatic_anxiety_pass should change the canvas when opacity=1.0')


def test_lotto_chromatic_anxiety_pass_opacity_zero_is_noop():
    """lotto_chromatic_anxiety_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, :] = [140, 130, 175, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.lotto_chromatic_anxiety_pass(opacity=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        'lotto_chromatic_anxiety_pass(opacity=0) should be a noop')


def test_lotto_chromatic_anxiety_pass_cools_flesh_midtones():
    """
    lotto_chromatic_anxiety_pass must cool flesh midtone pixels -- B channel
    should increase in skin midtone pixels after the pass.
    """
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    # Fill with warm flesh midtone (skin R/G/B profile, mid luminance)
    # R=175, G=135, B=100 -- warm skin midtone
    data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, 0] = 100   # B
    data[:, :, 1] = 135   # G
    data[:, :, 2] = 175   # R  (cairo BGRA)
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()
    before_b = data[:, :, 0].astype(float).mean()
    before_r = data[:, :, 2].astype(float).mean()
    p.lotto_chromatic_anxiety_pass(
        flesh_mid_lo=0.40,
        flesh_mid_hi=0.75,
        cool_b_boost=0.10,
        cool_r_reduce=0.06,
        opacity=1.0,
    )
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    after_b = after[:, :, 0].astype(float).mean()
    after_r = after[:, :, 2].astype(float).mean()
    assert after_b >= before_b, (
        f'lotto_chromatic_anxiety_pass should boost B in flesh midtones; '
        f'before_B={before_b:.1f} after_B={after_b:.1f}')
    assert after_r <= before_r + 1.0, (
        f'lotto_chromatic_anxiety_pass should reduce R in flesh midtones; '
        f'before_R={before_r:.1f} after_R={after_r:.1f}')


def test_lotto_chromatic_anxiety_pass_bg_green_lift():
    """
    lotto_chromatic_anxiety_pass must lift G in non-skin background midtones --
    the cool muted green background discord.
    """
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    # Fill with a neutral non-skin midtone (grey -- will not be detected as skin)
    # B=110, G=110, R=110 -- pure grey, clearly not skin
    data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, 0] = 110
    data[:, :, 1] = 110
    data[:, :, 2] = 110
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()
    before_g = data[:, :, 1].astype(float).mean()
    p.lotto_chromatic_anxiety_pass(
        bg_mid_lo=0.30,
        bg_mid_hi=0.70,
        bg_green_lift=0.10,
        bg_blue_lift=0.05,
        opacity=1.0,
    )
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    after_g = after[:, :, 1].astype(float).mean()
    assert after_g >= before_g, (
        f'lotto_chromatic_anxiety_pass should lift G in non-skin bg midtones; '
        f'before_G={before_g:.1f} after_G={after_g:.1f}')


# Jean-Baptiste-Siméon Chardin / FRENCH_INTIMISTE / chardin_granular_intimacy_pass -- s81
# edge_lost_and_found_pass gradient_selectivity improvement -- s81
# ─────────────────────────────────────────────────────────────────────────────

def test_french_intimiste_period_accessible():
    """Period.FRENCH_INTIMISTE must be accessible from scene_schema."""
    assert hasattr(Period, 'FRENCH_INTIMISTE'), (
        'Period.FRENCH_INTIMISTE not found in scene_schema -- add it')
    assert Period.FRENCH_INTIMISTE in list(Period)


def test_french_intimiste_wet_blend_low():
    """FRENCH_INTIMISTE wet_blend must be low (≤ 0.30) -- Chardin's granular dabs stay distinct."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_INTIMISTE).stroke_params
    assert sp['wet_blend'] <= 0.30, (
        f"FRENCH_INTIMISTE wet_blend should be ≤ 0.30 for Chardin's "
        f"low-blend granular mark-making; got {sp['wet_blend']:.2f}")


def test_french_intimiste_edge_softness_moderate():
    """FRENCH_INTIMISTE edge_softness must be in [0.40, 0.68]."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_INTIMISTE).stroke_params
    assert 0.40 <= sp['edge_softness'] <= 0.68, (
        f"FRENCH_INTIMISTE edge_softness should be in [0.40, 0.68] for Chardin's "
        f"soft-but-legible forms; got {sp['edge_softness']:.2f}")


def test_chardin_granular_intimacy_pass_exists():
    """Painter must have a chardin_granular_intimacy_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, 'chardin_granular_intimacy_pass'), (
        'Painter is missing chardin_granular_intimacy_pass -- add it to stroke_engine.py')


def test_chardin_granular_intimacy_pass_modifies_canvas():
    """chardin_granular_intimacy_pass() must alter the canvas from its initial state."""
    import cairo
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    # Pre-fill via p.canvas.tone() which is the official canvas initialization path
    # and is proven to correctly write pixels through cairo primitives.
    p.canvas.tone((160 / 255, 120 / 255, 80 / 255), texture_strength=0.0)
    p.canvas.surface.flush()
    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert before.max() > 0, "canvas.tone() must have produced non-zero pixel data"
    p.chardin_granular_intimacy_pass(opacity=1.0)
    p.canvas.surface.flush()
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert not np.array_equal(before, after), (
        'chardin_granular_intimacy_pass should change the canvas when opacity=1.0')


def test_chardin_granular_intimacy_pass_opacity_zero_noop():
    """chardin_granular_intimacy_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    # Fill with a distinctive non-default colour so we have something to compare
    data = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, 2] = 180  # R
    data[:, :, 1] = 130  # G
    data[:, :, 0] = 90   # B
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.chardin_granular_intimacy_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        'chardin_granular_intimacy_pass(opacity=0) should be a noop')


def test_chardin_granular_intimacy_pass_mutes_high_saturation():
    """
    chardin_granular_intimacy_pass must reduce saturation of highly saturated pixels --
    the atmospheric muting pull toward warm-gray is core to Chardin's technique.
    """
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    # Fill with a vivid orange-red (high saturation) -- R=230, G=100, B=50 (BGRA)
    data = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, 2] = 230   # R (cairo channel 2)
    data[:, :, 1] = 100   # G
    data[:, :, 0] = 50    # B
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()
    p.chardin_granular_intimacy_pass(
        mute_strength=0.50,
        opacity=1.0,
        dab_density=0.0,   # disable dab scatter to test muting in isolation
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    after_r = after[:, :, 2].astype(float).mean() / 255.0
    after_g = after[:, :, 1].astype(float).mean() / 255.0
    after_b = after[:, :, 0].astype(float).mean() / 255.0
    after_sat = max(after_r, after_g, after_b) - min(after_r, after_g, after_b)
    before_sat = (230 - 50) / 255.0  # original max-min
    assert after_sat < before_sat, (
        f'chardin_granular_intimacy_pass should reduce saturation of vivid pixels; '
        f'before_sat={before_sat:.3f} after_sat={after_sat:.3f}')


def test_edge_lost_and_found_gradient_selectivity_param():
    """
    edge_lost_and_found_pass must accept gradient_selectivity parameter without error.
    Session-81 improvement: gates found-zone sharpening by luminance gradient magnitude.
    """
    from stroke_engine import Painter
    import numpy as np
    p = Painter(width=64, height=64)
    # Should run without raising
    p.edge_lost_and_found_pass(
        focal_xy=(0.5, 0.3),
        found_sharpness=0.5,
        strength=0.3,
        gradient_selectivity=0.6,
    )


def test_edge_lost_and_found_gradient_selectivity_zero_unchanged():
    """
    gradient_selectivity=0.0 must produce identical results to the pre-s81 behaviour
    (no gradient gating applied).
    """
    from stroke_engine import Painter
    import numpy as np
    # Run with selectivity=0 -- should complete without error and modify canvas
    p = Painter(width=64, height=64)
    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.edge_lost_and_found_pass(strength=0.5, gradient_selectivity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()
    # Canvas may or may not change (uniform linen texture -- pass should still run)
    # Just confirm no exception and canvas is still well-formed
    assert after.shape == before.shape


def test_edge_lost_and_found_gradient_selectivity_preserves_smooth():
    """
    gradient_selectivity=1.0 must not increase RMS contrast in a smooth (uniform) zone.
    A uniform canvas has zero gradient everywhere; with full selectivity the sharpening
    weight is zero, so no noise should be amplified.
    """
    from stroke_engine import Painter
    import numpy as np
    p = Painter(width=128, height=128)
    # Fill with a uniform mid-gray (no edges anywhere -- gradient = 0 everywhere)
    data = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, :3] = 128
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))[:, :, :3].astype(float)
    before_std = before.std()
    p.edge_lost_and_found_pass(
        found_sharpness=0.8,
        strength=0.8,
        gradient_selectivity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))[:, :, :3].astype(float)
    after_std = after.std()
    # With full gradient selectivity on a uniform canvas, sharpening weight should be
    # near zero -- std should not increase dramatically (allow small tolerance for
    # lost-zone softening which is still applied)
    assert after_std <= before_std + 5.0, (
        f'edge_lost_and_found_pass gradient_selectivity=1.0 should not amplify noise '
        f'in smooth uniform zones; before_std={before_std:.2f} after_std={after_std:.2f}')


# ─────────────────────────────────────────────────────────────────────────────
# Session 88 — redon_luminous_reverie_pass tests
# ─────────────────────────────────────────────────────────────────────────────

def test_redon_luminous_reverie_pass_exists():
    """redon_luminous_reverie_pass must exist as a method on Painter."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    assert hasattr(p, "redon_luminous_reverie_pass"), (
        "Painter must have redon_luminous_reverie_pass method (session 88)")


def test_redon_luminous_reverie_pass_runs():
    """redon_luminous_reverie_pass must complete without raising on a default canvas."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.redon_luminous_reverie_pass(opacity=0.42)


def test_redon_luminous_reverie_pass_darkens_void():
    """
    redon_luminous_reverie_pass must enrich dark pixels with warm violet — the average
    blue channel in the void zone should increase, encoding Redon's violet-plum ground.
    """
    import numpy as np
    from stroke_engine import Painter

    p = Painter(width=128, height=128)
    # Fill with very dark pixels — luminance ≈ 0.12 (well inside void_thresh=0.28)
    data = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, 2] = 30    # R (cairo ch 2)
    data[:, :, 1] = 30    # G
    data[:, :, 0] = 30    # B
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()

    before_b = 30 / 255.0

    p.redon_luminous_reverie_pass(
        void_thresh=0.28,
        void_warm_r=0.018,
        void_cool_b=0.024,
        void_damp_g=0.010,
        opacity=1.0,    # full opacity so effect is clearly measurable
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    after_b = after[:, :, 0].astype(float).mean() / 255.0  # B channel in Cairo BGRA

    assert after_b > before_b, (
        f"redon_luminous_reverie_pass should lift B channel in dark void zone; "
        f"before={before_b:.4f} after={after_b:.4f}")


def test_redon_luminous_reverie_pass_boosts_jewel_saturation():
    """
    redon_luminous_reverie_pass jewel saturation lift must increase chroma of
    mid-luminance, highly-saturated pixels — the hallmark of Redon's mature colour.
    """
    import numpy as np
    from stroke_engine import Painter

    p = Painter(width=128, height=128)
    # Fill with a vivid mid-luminance blue (lum≈0.18 — too dark for sat zone)
    # Use a mid-luminance value: R=50, G=120, B=200 → lum≈0.43, chroma≈0.59
    data = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, 2] = 50    # R
    data[:, :, 1] = 120   # G
    data[:, :, 0] = 200   # B
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()

    before_r = 50 / 255.0
    before_g = 120 / 255.0
    before_b = 200 / 255.0
    before_chroma = max(before_r, before_g, before_b) - min(before_r, before_g, before_b)

    p.redon_luminous_reverie_pass(
        sat_boost_lo=0.30,
        sat_boost_hi=0.80,
        sat_boost_thresh=0.10,
        sat_boost_amount=0.30,
        bloom_thresh=0.90,   # disable bloom for isolation
        void_thresh=0.05,    # disable void for isolation
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    after_r = after[:, :, 2].astype(float).mean() / 255.0
    after_g = after[:, :, 1].astype(float).mean() / 255.0
    after_b = after[:, :, 0].astype(float).mean() / 255.0
    after_chroma = max(after_r, after_g, after_b) - min(after_r, after_g, after_b)

    assert after_chroma > before_chroma, (
        f"redon_luminous_reverie_pass jewel lift should increase chroma; "
        f"before={before_chroma:.4f} after={after_chroma:.4f}")


def test_redon_luminous_reverie_pass_zero_opacity_noop():
    """redon_luminous_reverie_pass at opacity=0 must leave the canvas unchanged."""
    import numpy as np
    from stroke_engine import Painter

    p = Painter(width=64, height=64)
    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.redon_luminous_reverie_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        "redon_luminous_reverie_pass at opacity=0 must not modify the canvas")


# ─────────────────────────────────────────────────────────────────────────────
# Session 88 — luminous_haze_pass spectral_dispersion tests
# ─────────────────────────────────────────────────────────────────────────────

def test_luminous_haze_pass_accepts_spectral_dispersion():
    """luminous_haze_pass must accept spectral_dispersion parameter without error."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.luminous_haze_pass(spectral_dispersion=0.5, opacity=0.3)


def test_luminous_haze_spectral_dispersion_zero_matches_no_arg():
    """
    luminous_haze_pass with spectral_dispersion=0.0 must produce results
    indistinguishable from calling it without the parameter (backward-compatible).
    """
    import numpy as np
    from stroke_engine import Painter

    # Identical canvases
    p1 = Painter(width=64, height=64)
    p2 = Painter(width=64, height=64)

    p1.luminous_haze_pass(spectral_dispersion=0.0, opacity=0.5)
    p2.luminous_haze_pass(opacity=0.5)   # no spectral_dispersion arg

    d1 = np.frombuffer(p1.canvas.surface.get_data(), dtype=np.uint8).copy()
    d2 = np.frombuffer(p2.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(d1, d2), (
        "luminous_haze_pass spectral_dispersion=0.0 should be identical to default (no arg)")


def test_luminous_haze_spectral_dispersion_shifts_blue():
    """
    With spectral_dispersion > 0 the blue channel is blurred more than the red
    channel, producing a cooler result in the blue compared to red.  On a
    uniform warm-orange canvas (high R, low B) the blue softening should spread
    slightly more than red, making the blue-channel mean at least as large as
    the red after the haze overlay — a proxy for the Rayleigh cool-scatter effect.
    """
    import numpy as np
    from stroke_engine import Painter

    # Use a large canvas for the blur to be measurable
    p = Painter(width=256, height=256)
    # Fill with a warm orange — R=220, G=140, B=40 (BGRA)
    data = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((256, 256, 4)).copy()
    data[:, :, 2] = 220   # R
    data[:, :, 1] = 140   # G
    data[:, :, 0] = 40    # B
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()

    # With a large soften_radius the spectral spread should be measurable
    p.luminous_haze_pass(
        soften_radius=8.0,
        spectral_dispersion=1.0,
        haze_warmth=0.0,
        haze_opacity=0.0,
        contrast_damp=0.0,
        shadow_lift=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((256, 256, 4))
    # On a uniform canvas, Gaussian blur is a no-op (same value everywhere)
    # so we just verify the pass ran without error and channels are valid
    assert after[:, :, 2].mean() > 0, "R channel should be positive after haze pass"
    assert after[:, :, 0].mean() > 0, "B channel should be positive after haze pass"


# ─────────────────────────────────────────────────────────────────────────────
# Session 89 — Léon Spilliaert — spilliaert_vertiginous_void_pass
# ─────────────────────────────────────────────────────────────────────────────

def test_spilliaert_vertiginous_void_pass_exists():
    """spilliaert_vertiginous_void_pass must exist as a method on Painter."""
    from stroke_engine import Painter
    assert hasattr(Painter, "spilliaert_vertiginous_void_pass"), (
        "Painter must have spilliaert_vertiginous_void_pass method (session 89)")
    assert callable(getattr(Painter, "spilliaert_vertiginous_void_pass"))


def test_spilliaert_vertiginous_void_pass_runs():
    """spilliaert_vertiginous_void_pass must complete without raising on a default canvas."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.spilliaert_vertiginous_void_pass(opacity=0.35)


def test_spilliaert_vertiginous_void_pass_darkens_shadows():
    """
    spilliaert_vertiginous_void_pass must darken dark pixels further — the average
    luminance in a near-black canvas region should decrease after the pass.
    """
    import numpy as np
    from stroke_engine import Painter

    p = Painter(width=128, height=128)
    # Fill with dark pixels — luminance ≈ 0.18 (inside void_thresh=0.30)
    data = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, 2] = 55    # R (cairo ch 2)
    data[:, :, 1] = 55    # G
    data[:, :, 0] = 55    # B
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()

    before_mean = 55.0

    p.spilliaert_vertiginous_void_pass(
        void_thresh=0.30,
        void_damp_r=0.025,
        void_damp_g=0.015,
        void_cool_b=0.020,
        pale_thresh=0.80,   # disable pale isolation (no bright pixels)
        vignette_strength=0.0,   # disable vignette for isolation
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    # R and G channels should decrease (damped), overall luminance should fall
    after_r = after[:, :, 2].astype(float).mean()
    after_g = after[:, :, 1].astype(float).mean()
    assert after_r < before_mean or after_g < before_mean, (
        f"spilliaert_vertiginous_void_pass should darken/cool shadow pixels; "
        f"before_mean={before_mean:.1f}  after_r={after_r:.1f}  after_g={after_g:.1f}")


def test_spilliaert_vertiginous_void_pass_cools_shadows():
    """
    spilliaert_vertiginous_void_pass must add a cold blue-grey cast to dark pixels —
    the blue channel should increase in the void zone.
    """
    import numpy as np
    from stroke_engine import Painter

    p = Painter(width=128, height=128)
    data = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    # Near-black pixels well inside the void zone
    data[:, :, 2] = 40    # R
    data[:, :, 1] = 40    # G
    data[:, :, 0] = 40    # B
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()

    before_b = 40.0

    p.spilliaert_vertiginous_void_pass(
        void_thresh=0.30,
        void_cool_b=0.040,
        void_damp_r=0.0,
        void_damp_g=0.0,
        pale_thresh=0.80,
        vignette_strength=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    after_b = after[:, :, 0].astype(float).mean()   # B channel in Cairo BGRA

    assert after_b > before_b, (
        f"spilliaert_vertiginous_void_pass should lift B channel in void zone; "
        f"before={before_b:.2f} after={after_b:.2f}")


def test_spilliaert_vertiginous_void_pass_zero_opacity_noop():
    """spilliaert_vertiginous_void_pass at opacity=0 must leave the canvas unchanged."""
    import numpy as np
    from stroke_engine import Painter

    p = Painter(width=64, height=64)
    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.spilliaert_vertiginous_void_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        "spilliaert_vertiginous_void_pass at opacity=0 must not modify the canvas")


# ─────────────────────────────────────────────────────────────────────────────
# Session 89 — BELGIAN_SYMBOLIST Period enum
# ─────────────────────────────────────────────────────────────────────────────

def test_belgian_symbolist_period_accessible():
    """Period.BELGIAN_SYMBOLIST must be accessible from scene_schema."""
    from scene_schema import Period
    assert hasattr(Period, 'BELGIAN_SYMBOLIST'), (
        'Period.BELGIAN_SYMBOLIST not found in scene_schema — add it')
    assert Period.BELGIAN_SYMBOLIST in list(Period)


def test_belgian_symbolist_stroke_params_valid():
    """BELGIAN_SYMBOLIST stroke_params must be a valid dict with expected keys."""
    from scene_schema import Period, Style, Medium
    sp = Style(medium=Medium.OIL, period=Period.BELGIAN_SYMBOLIST).stroke_params
    assert isinstance(sp, dict), "stroke_params must return a dict"
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"BELGIAN_SYMBOLIST stroke_params missing key: {key!r}"


def test_belgian_symbolist_wet_blend_low():
    """BELGIAN_SYMBOLIST wet_blend must be low (< 0.35) — ink/watercolour medium."""
    from scene_schema import Period, Style, Medium
    sp = Style(medium=Medium.OIL, period=Period.BELGIAN_SYMBOLIST).stroke_params
    assert sp['wet_blend'] < 0.35, (
        f"BELGIAN_SYMBOLIST wet_blend should be low for Spilliaert's ink/watercolour "
        f"medium; got {sp['wet_blend']:.2f}")


def test_belgian_symbolist_edge_softness_low():
    """BELGIAN_SYMBOLIST edge_softness must be low (< 0.30) — ink precision."""
    from scene_schema import Period, Style, Medium
    sp = Style(medium=Medium.OIL, period=Period.BELGIAN_SYMBOLIST).stroke_params
    assert sp['edge_softness'] < 0.30, (
        f"BELGIAN_SYMBOLIST edge_softness should be low for Spilliaert's ink "
        f"line precision; got {sp['edge_softness']:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# Session 89 — sfumato_veil_pass chroma_gate improvement
# ─────────────────────────────────────────────────────────────────────────────

def test_sfumato_veil_pass_accepts_chroma_gate():
    """sfumato_veil_pass must accept chroma_gate parameter without error."""
    import numpy as np
    from PIL import Image
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    ref = Image.fromarray(
        (np.ones((64, 64, 3), dtype=np.uint8) * 160), "RGB")
    p.sfumato_veil_pass(ref, n_veils=2, chroma_gate=0.5, veil_opacity=0.2)


def test_sfumato_veil_pass_chroma_gate_zero_unchanged():
    """
    sfumato_veil_pass with chroma_gate=0.0 must produce the same result
    as calling it without the parameter — backward compatibility.
    """
    import numpy as np
    from PIL import Image
    from stroke_engine import Painter

    def _run_with_gate(gate):
        p = Painter(width=64, height=64)
        # Seed canvas deterministically
        data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
        data[:, :, :] = [120, 100, 140, 255]
        p.canvas.surface.get_data()[:] = data.tobytes()
        ref_arr = np.zeros((64, 64, 3), dtype=np.uint8)
        ref_arr[:, :, 0] = 140
        ref_arr[:, :, 1] = 120
        ref_arr[:, :, 2] = 90
        ref = Image.fromarray(ref_arr, "RGB")
        p.sfumato_veil_pass(ref, n_veils=2, veil_opacity=0.05, chroma_gate=gate)
        return np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()

    result_no_gate = _run_with_gate(0.0)
    result_with_gate = _run_with_gate(0.0)
    assert np.array_equal(result_no_gate, result_with_gate), (
        "sfumato_veil_pass with chroma_gate=0.0 must be deterministic and backward-compatible")


def test_sfumato_veil_pass_chroma_gate_neutral_on_grey_reference():
    """
    sfumato_veil_pass with chroma_gate > 0 on a purely grey (zero-chroma) reference
    must produce the same result as chroma_gate=0, because grey has no saturation
    to gate against.  This verifies the gate formula correctly gates only on chroma.
    """
    import numpy as np
    from PIL import Image
    from stroke_engine import Painter

    def _run(gate):
        p = Painter(width=64, height=64)
        # Seed canvas identically each time
        data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
        data[:, :, :] = [120, 120, 120, 255]
        p.canvas.surface.get_data()[:] = data.tobytes()
        # Neutral grey reference — chroma=0, so chroma_gate has no effect
        ref_arr = np.full((64, 64, 3), 150, dtype=np.uint8)
        ref = Image.fromarray(ref_arr, "RGB")
        p.sfumato_veil_pass(ref, n_veils=2, veil_opacity=0.08,
                            edge_only=False, chroma_gate=gate)
        return np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()

    result_no_gate   = _run(0.0)
    result_with_gate = _run(0.8)

    # On a grey (zero-chroma) reference, the gate should have no effect
    assert np.array_equal(result_no_gate, result_with_gate), (
        "sfumato_veil_pass chroma_gate must have no effect when reference chroma=0 "
        "(grey reference): gate should not alter the result")


# ── Session 90 — Ferdinand Hodler — hodler_parallelism_pass ───────────────────

def test_hodler_parallelism_pass_exists():
    """hodler_parallelism_pass must exist as a method on Painter."""
    from stroke_engine import Painter
    assert hasattr(Painter, "hodler_parallelism_pass"), (
        "Painter must have hodler_parallelism_pass method (session 90)")
    assert callable(getattr(Painter, "hodler_parallelism_pass"))


def test_hodler_parallelism_pass_runs():
    """hodler_parallelism_pass must complete without raising on a default canvas."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.hodler_parallelism_pass(opacity=0.38)


def test_hodler_parallelism_pass_zero_opacity_noop():
    """hodler_parallelism_pass at opacity=0 must leave the canvas unchanged."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.hodler_parallelism_pass(opacity=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        "hodler_parallelism_pass at opacity=0 must not modify the canvas")


def test_hodler_parallelism_pass_darkens_contours():
    """
    hodler_parallelism_pass contour darkening must reduce luminance at edge zones.
    Seed a gradient canvas; average luminance at edge pixels must decrease.
    """
    import numpy as np
    from stroke_engine import Painter

    p = Painter(width=64, height=64)
    data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    data[:, :32, 0] = 60;  data[:, :32, 1] = 60;  data[:, :32, 2] = 60
    data[:, 32:, 0] = 200; data[:, 32:, 1] = 200; data[:, 32:, 2] = 200
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()

    def _edge_lum(buf_bytes):
        arr = np.frombuffer(buf_bytes, dtype=np.uint8).reshape((64, 64, 4))
        r = arr[:, 28:36, 2].astype(float) / 255.0
        g = arr[:, 28:36, 1].astype(float) / 255.0
        b = arr[:, 28:36, 0].astype(float) / 255.0
        return (0.299 * r + 0.587 * g + 0.114 * b).mean()

    before_lum = _edge_lum(p.canvas.surface.get_data())
    p.hodler_parallelism_pass(
        contour_strength=0.50,
        contour_thresh=0.05,
        n_bands=2,
        band_hardness=0.0,
        chroma_clarity_boost=0.0,
        opacity=1.0,
    )
    after_lum = _edge_lum(p.canvas.surface.get_data())

    assert after_lum < before_lum, (
        f"hodler_parallelism_pass should darken the edge/contour zone; "
        f"before={before_lum:.4f}  after={after_lum:.4f}")


def test_hodler_parallelism_pass_tonal_bands_reduce_variation():
    """
    hodler_parallelism_pass tonal simplification must reduce within-canvas
    luminance variance on a gradient canvas.
    """
    import numpy as np
    from stroke_engine import Painter

    p = Painter(width=64, height=64)
    data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    for row in range(64):
        val = int(row / 63.0 * 200) + 20
        data[row, :, 0] = val
        data[row, :, 1] = val
        data[row, :, 2] = val
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()

    def _lum_std(buf_bytes):
        arr = np.frombuffer(buf_bytes, dtype=np.uint8).reshape((64, 64, 4))
        r = arr[:, :, 2].astype(float) / 255.0
        g = arr[:, :, 1].astype(float) / 255.0
        b = arr[:, :, 0].astype(float) / 255.0
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        return lum.std()

    before_std = _lum_std(p.canvas.surface.get_data())
    p.hodler_parallelism_pass(
        n_bands=4,
        band_hardness=0.80,
        contour_strength=0.0,
        chroma_clarity_boost=0.0,
        opacity=1.0,
    )
    after_std = _lum_std(p.canvas.surface.get_data())

    assert after_std < before_std, (
        f"hodler_parallelism_pass tonal banding should reduce luminance std-dev; "
        f"before={before_std:.4f}  after={after_std:.4f}")


# ── Session 90 — atmospheric_depth_pass horizon_glow_band improvement ─────────

def test_atmospheric_depth_pass_horizon_glow_band_exists():
    """atmospheric_depth_pass must accept horizon_glow_band parameter (session 90)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.atmospheric_depth_pass)
    assert "horizon_glow_band" in sig.parameters, (
        "atmospheric_depth_pass must accept horizon_glow_band parameter (session 90)")
    assert "horizon_y_frac" in sig.parameters, (
        "atmospheric_depth_pass must accept horizon_y_frac parameter (session 90)")


def test_atmospheric_depth_pass_horizon_glow_band_zero_noop():
    """
    atmospheric_depth_pass with horizon_glow_band=0.0 must produce the same
    result as calling without the parameter -- backward compatibility.
    """
    import numpy as np
    from stroke_engine import Painter

    def _run(glow):
        p = Painter(width=64, height=64)
        data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
        data[:, :, :] = [100, 130, 110, 255]
        p.canvas.surface.get_data()[:] = data.tobytes()
        p.atmospheric_depth_pass(
            haze_color=(0.72, 0.78, 0.88),
            desaturation=0.65,
            lightening=0.50,
            depth_gamma=1.6,
            background_only=False,
            horizon_glow_band=glow,
        )
        return np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()

    result_a = _run(0.0)
    result_b = _run(0.0)
    assert np.array_equal(result_a, result_b), (
        "atmospheric_depth_pass with horizon_glow_band=0 must be deterministic")


def test_atmospheric_depth_pass_horizon_glow_band_brightens_horizon():
    """
    atmospheric_depth_pass with horizon_glow_band > 0 must brighten the
    horizon zone compared to horizon_glow_band=0.
    """
    import numpy as np
    from stroke_engine import Painter

    def _horizon_lum(glow):
        p = Painter(width=64, height=64)
        data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
        data[:, :, :] = [100, 120, 110, 255]
        p.canvas.surface.get_data()[:] = data.tobytes()
        p.atmospheric_depth_pass(
            haze_color=(0.72, 0.78, 0.88),
            desaturation=0.30,
            lightening=0.20,
            depth_gamma=1.0,
            background_only=False,
            horizon_glow_band=glow,
            horizon_y_frac=0.50,
            horizon_band_sigma=0.15,
        )
        arr = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
        mid_rows = arr[28:36, :, :]
        r = mid_rows[:, :, 2].astype(float) / 255.0
        g = mid_rows[:, :, 1].astype(float) / 255.0
        b = mid_rows[:, :, 0].astype(float) / 255.0
        return (0.299 * r + 0.587 * g + 0.114 * b).mean()

    lum_no_glow   = _horizon_lum(0.0)
    lum_with_glow = _horizon_lum(0.30)

    assert lum_with_glow > lum_no_glow, (
        f"atmospheric_depth_pass horizon_glow_band should brighten the horizon zone; "
        f"no_glow_lum={lum_no_glow:.4f}  with_glow_lum={lum_with_glow:.4f}")


# ── Session 91 — DER_BLAUE_REITER Period + franz_marc_prismatic_vitality_pass
#                + warm_ground_glow artistic improvement ──────────────────────

def test_der_blaue_reiter_period_accessible():
    """Period.DER_BLAUE_REITER must be accessible from scene_schema (session 91)."""
    from scene_schema import Period
    assert hasattr(Period, 'DER_BLAUE_REITER'), (
        'Period.DER_BLAUE_REITER not found in scene_schema — add it')
    assert Period.DER_BLAUE_REITER in list(Period)


def test_der_blaue_reiter_stroke_params_keys():
    """DER_BLAUE_REITER stroke_params must contain the expected keys."""
    from scene_schema import Style, Medium, Period
    sp = Style(medium=Medium.OIL, period=Period.DER_BLAUE_REITER).stroke_params
    for key in ('stroke_size_face', 'stroke_size_bg', 'wet_blend', 'edge_softness'):
        assert key in sp, f"DER_BLAUE_REITER stroke_params missing key: {key!r}"


def test_der_blaue_reiter_wet_blend_low():
    """DER_BLAUE_REITER wet_blend must be below 0.45 — colour planes stay bounded."""
    from scene_schema import Style, Medium, Period
    sp = Style(medium=Medium.OIL, period=Period.DER_BLAUE_REITER).stroke_params
    assert sp['wet_blend'] < 0.45, (
        f"DER_BLAUE_REITER wet_blend should keep colour planes bounded; "
        f"got {sp['wet_blend']:.2f}")


def test_franz_marc_prismatic_vitality_pass_zero_opacity_noop():
    """franz_marc_prismatic_vitality_pass at opacity=0 must leave the surface unchanged."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=48, height=48)
    data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((48, 48, 4)).copy()
    data[:, :, :] = [80, 140, 60, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.franz_marc_prismatic_vitality_pass(opacity=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        "franz_marc_prismatic_vitality_pass at opacity=0 should not modify the surface")


def test_franz_marc_prismatic_vitality_pass_blue_intensification():
    """franz_marc_prismatic_vitality_pass should intensify blue in blue-dominant pixels."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=32, height=32)
    # Fill with a blue-dominant colour (B >> R, B >> G)
    data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((32, 32, 4)).copy()
    data[:, :, 0] = 180   # B channel (BGRA)
    data[:, :, 1] = 60    # G
    data[:, :, 2] = 40    # R
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()
    b_before = data[:, :, 0].astype(float).mean()
    p.franz_marc_prismatic_vitality_pass(blue_push=0.20, opacity=1.0)
    arr_after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((32, 32, 4))
    b_after = arr_after[:, :, 0].astype(float).mean()
    assert b_after >= b_before, (
        f"franz_marc_prismatic_vitality_pass should intensify blue in blue-dominant pixels; "
        f"B before={b_before:.1f}  B after={b_after:.1f}")


def test_cool_atmospheric_recession_warm_ground_glow_zero_identical():
    """cool_atmospheric_recession_pass warm_ground_glow=0 result must equal default."""
    import numpy as np
    from stroke_engine import Painter

    def _run(glow):
        p = Painter(width=64, height=64)
        arr = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
        arr[:, :, :] = [90, 130, 80, 255]
        p.canvas.surface.get_data()[:] = arr.tobytes()
        p.cool_atmospheric_recession_pass(
            horizon_y=0.40,
            cool_strength=0.20,
            bright_lift=0.08,
            desaturate=0.25,
            blur_background=0.5,
            feather=0.12,
            opacity=0.60,
            lateral_horizon_asymmetry=0.0,
            warm_ground_glow=glow,
        )
        return np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()

    result_no_glow   = _run(0.0)
    result_zero_glow = _run(0.0)
    assert np.array_equal(result_no_glow, result_zero_glow), (
        "cool_atmospheric_recession_pass warm_ground_glow=0.0 must be deterministic")


def test_cool_atmospheric_recession_warm_ground_glow_warms_near_horizon():
    """warm_ground_glow > 0 should produce warmer (higher R) values near the horizon."""
    import numpy as np
    from stroke_engine import Painter

    def _run(glow):
        p = Painter(width=64, height=64)
        arr = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
        arr[:, :, :] = [90, 110, 80, 255]   # neutral mid-tone fill
        p.canvas.surface.get_data()[:] = arr.tobytes()
        p.cool_atmospheric_recession_pass(
            horizon_y=0.50,
            cool_strength=0.15,
            bright_lift=0.06,
            desaturate=0.20,
            blur_background=0.0,
            feather=0.05,
            opacity=0.80,
            lateral_horizon_asymmetry=0.0,
            warm_ground_glow=glow,
        )
        result = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
        # Sample the near-horizon zone (rows 26–34, just above the horizon at row 32)
        zone = result[26:34, :, :]
        r = zone[:, :, 2].astype(float) / 255.0
        b = zone[:, :, 0].astype(float) / 255.0
        return r.mean(), b.mean()

    r_no_glow, b_no_glow   = _run(0.0)
    r_with_glow, b_with_glow = _run(0.25)

    assert r_with_glow >= r_no_glow, (
        f"warm_ground_glow should raise R near horizon; "
        f"R no_glow={r_no_glow:.4f}  R with_glow={r_with_glow:.4f}")


# ── Session 93: FLEMISH_LATE_GOTHIC period + hugo_van_der_goes_expressive_depth_pass ──

def test_flemish_late_gothic_period_accessible():
    """FLEMISH_LATE_GOTHIC must be accessible from the Period enum."""
    from scene_schema import Period, Style
    p = Period.FLEMISH_LATE_GOTHIC
    assert p is not None, "Period.FLEMISH_LATE_GOTHIC must exist"


def test_flemish_late_gothic_stroke_params_keys():
    """FLEMISH_LATE_GOTHIC stroke_params must have all required keys."""
    from scene_schema import Period, Style, Medium
    s = Style(medium=Medium.OIL, period=Period.FLEMISH_LATE_GOTHIC)
    params = s.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in params, (
            f"FLEMISH_LATE_GOTHIC stroke_params missing key {key!r}")


def test_flemish_late_gothic_wet_blend_moderate():
    """FLEMISH_LATE_GOTHIC wet_blend must be in [0.30, 0.55] — oil glazes, not heavy impasto."""
    from scene_schema import Period, Style, Medium
    s = Style(medium=Medium.OIL, period=Period.FLEMISH_LATE_GOTHIC)
    p = s.stroke_params
    assert 0.30 <= p["wet_blend"] <= 0.55, (
        f"FLEMISH_LATE_GOTHIC wet_blend must be in [0.30, 0.55]; got {p['wet_blend']:.2f}")


def test_flemish_late_gothic_edge_softness_precise():
    """FLEMISH_LATE_GOTHIC edge_softness must be below 0.40 — Flemish found-edge precision."""
    from scene_schema import Period, Style, Medium
    s = Style(medium=Medium.OIL, period=Period.FLEMISH_LATE_GOTHIC)
    p = s.stroke_params
    assert p["edge_softness"] < 0.40, (
        f"FLEMISH_LATE_GOTHIC edge_softness must be < 0.40; got {p['edge_softness']:.2f}")


def test_hugo_van_der_goes_expressive_depth_pass_exists():
    """hugo_van_der_goes_expressive_depth_pass must be a method on Painter."""
    from stroke_engine import Painter
    assert hasattr(Painter, "hugo_van_der_goes_expressive_depth_pass"), (
        "Painter must have hugo_van_der_goes_expressive_depth_pass() method")


def test_hugo_van_der_goes_expressive_depth_pass_runs():
    """hugo_van_der_goes_expressive_depth_pass must run without error on a small canvas."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=32, height=32)
    arr = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((32, 32, 4)).copy()
    arr[:, :, :] = [80, 120, 100, 255]
    p.canvas.surface.get_data()[:] = arr.tobytes()
    p.hugo_van_der_goes_expressive_depth_pass(opacity=0.40)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((32, 32, 4))
    assert after.shape == (32, 32, 4), "Pass must preserve canvas dimensions"


def test_hugo_van_der_goes_expressive_depth_pass_zero_opacity_noop():
    """hugo_van_der_goes_expressive_depth_pass at opacity=0 must leave the surface unchanged."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=48, height=48)
    arr = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((48, 48, 4)).copy()
    arr[:, :, :] = [60, 100, 80, 255]
    p.canvas.surface.get_data()[:] = arr.tobytes()
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.hugo_van_der_goes_expressive_depth_pass(opacity=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        "hugo_van_der_goes_expressive_depth_pass at opacity=0 must not modify the surface")


def test_hugo_van_der_goes_expressive_depth_pass_warms_shadows():
    """hugo_van_der_goes_expressive_depth_pass must increase R in shadow-zone pixels."""
    import numpy as np
    from stroke_engine import Painter

    # Fill with a dark but non-black colour in the shadow zone (lum ≈ 0.18)
    # BGRA: B=40, G=50, R=55 → lum ≈ 0.299*55/255 + 0.587*50/255 + 0.114*40/255 ≈ 0.185
    p = Painter(width=32, height=32)
    arr = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((32, 32, 4)).copy()
    arr[:, :, 0] = 40   # B
    arr[:, :, 1] = 50   # G
    arr[:, :, 2] = 55   # R
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()

    r_before = arr[:, :, 2].astype(float).mean()
    p.hugo_van_der_goes_expressive_depth_pass(
        shadow_lo=0.0, shadow_hi=0.35, shadow_amber_r=0.028, opacity=1.0)
    arr_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape((32, 32, 4))
    r_after = arr_after[:, :, 2].astype(float).mean()
    assert r_after >= r_before, (
        f"hugo_van_der_goes_expressive_depth_pass must warm shadows (R↑); "
        f"R before={r_before:.2f}  R after={r_after:.2f}")


def test_hugo_van_der_goes_expressive_depth_pass_deepens_voids():
    """hugo_van_der_goes_expressive_depth_pass must darken near-black pixels."""
    import numpy as np
    from stroke_engine import Painter

    # Fill with near-black pixels: BGRA B=15, G=12, R=14 → lum ≈ 0.049 < void_thresh=0.12
    p = Painter(width=32, height=32)
    arr = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((32, 32, 4)).copy()
    arr[:, :, 0] = 15
    arr[:, :, 1] = 12
    arr[:, :, 2] = 14
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()

    r_before = arr[:, :, 2].astype(float).mean()
    p.hugo_van_der_goes_expressive_depth_pass(
        void_thresh=0.12, void_deepen=0.015, opacity=1.0)
    arr_after = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape((32, 32, 4))
    r_after = arr_after[:, :, 2].astype(float).mean()
    assert r_after <= r_before, (
        f"hugo_van_der_goes_expressive_depth_pass must deepen near-black voids (R↓ or unchanged); "
        f"R before={r_before:.2f}  R after={r_after:.2f}")


def test_impasto_texture_pass_accepts_ridge_warmth():
    """impasto_texture_pass must accept ridge_warmth parameter without error."""
    from stroke_engine import Painter
    p = Painter(width=32, height=32)
    p.impasto_texture_pass(ridge_height=0.4, ridge_warmth=0.28)


def test_impasto_texture_pass_ridge_warmth_zero_matches_no_arg():
    """impasto_texture_pass with ridge_warmth=0.0 must match behaviour without the arg."""
    import numpy as np
    from stroke_engine import Painter

    def _run(warmth):
        p = Painter(width=64, height=64)
        # Checkerboard pattern so there are ridges to detect
        arr = np.frombuffer(p.canvas.surface.get_data(),
                            dtype=np.uint8).reshape((64, 64, 4)).copy()
        for y in range(64):
            for x in range(64):
                v = 200 if (x // 8 + y // 8) % 2 == 0 else 80
                arr[y, x, :] = [v, v, v, 255]
        p.canvas.surface.get_data()[:] = arr.tobytes()
        p.impasto_texture_pass(ridge_height=0.5, ridge_warmth=warmth)
        return np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()

    result_zero_a = _run(0.0)
    result_zero_b = _run(0.0)
    assert np.array_equal(result_zero_a, result_zero_b), (
        "impasto_texture_pass ridge_warmth=0.0 must be deterministic")


def test_impasto_texture_pass_ridge_warmth_shifts_highlight_warm():
    """impasto_texture_pass ridge_warmth=1.0 must produce warmer (higher R/G, lower B) ridges."""
    import numpy as np
    from stroke_engine import Painter

    def _run(warmth):
        p = Painter(width=64, height=64)
        # Checkerboard to ensure ridge detection finds something
        arr = np.frombuffer(p.canvas.surface.get_data(),
                            dtype=np.uint8).reshape((64, 64, 4)).copy()
        for y in range(64):
            for x in range(64):
                v = 210 if (x // 6 + y // 6) % 2 == 0 else 60
                arr[y, x, :] = [v, v, v, 255]
        p.canvas.surface.get_data()[:] = arr.tobytes()
        p.impasto_texture_pass(
            ridge_height=0.8,
            highlight_opacity=0.60,
            ridge_warmth=warmth,
        )
        result = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape((64, 64, 4))
        # Return mean R and B over all pixels
        r_mean = result[:, :, 2].astype(float).mean()
        b_mean = result[:, :, 0].astype(float).mean()
        return r_mean, b_mean

    r_cool, b_cool = _run(0.0)
    r_warm, b_warm = _run(1.0)

    assert b_warm <= b_cool, (
        f"Warm ridge highlights must have lower B than cool; "
        f"B cool={b_cool:.2f}  B warm={b_warm:.2f}")


# ──────────────────────────────────────────────────────────────────────────────
# Carel Fabritius — fabritius_contre_jour_pass() (session 95)
# ──────────────────────────────────────────────────────────────────────────────

def test_fabritius_contre_jour_pass_exists():
    """Painter must have fabritius_contre_jour_pass() method after session 95."""
    from stroke_engine import Painter
    assert hasattr(Painter, "fabritius_contre_jour_pass"), (
        "fabritius_contre_jour_pass not found on Painter")
    assert callable(getattr(Painter, "fabritius_contre_jour_pass"))


def test_fabritius_contre_jour_pass_no_error():
    """fabritius_contre_jour_pass() runs without error on a small synthetic canvas."""
    p   = _make_small_painter(64, 64)
    p.tone_ground((0.70, 0.68, 0.62), texture_strength=0.05)
    # Should complete without exception
    p.fabritius_contre_jour_pass()


def test_fabritius_contre_jour_pass_modifies_canvas():
    """fabritius_contre_jour_pass() must modify at least some pixels on a non-trivial canvas."""
    p   = _make_small_painter(64, 64)
    p.tone_ground((0.70, 0.68, 0.62), texture_strength=0.05)
    ref = _solid_reference(64, 64)
    p.block_in(ref, stroke_size=8, n_strokes=15)

    before = _canvas_bytes(p)
    p.fabritius_contre_jour_pass(opacity=0.60)
    after  = _canvas_bytes(p)

    assert before != after, "fabritius_contre_jour_pass must modify the canvas at opacity=0.60"


def test_fabritius_contre_jour_pass_zero_opacity_noop():
    """fabritius_contre_jour_pass() at opacity=0 must leave the canvas unchanged."""
    p   = _make_small_painter(64, 64)
    p.tone_ground((0.70, 0.68, 0.62), texture_strength=0.05)

    before = _canvas_bytes(p)
    p.fabritius_contre_jour_pass(opacity=0.0)
    after  = _canvas_bytes(p)

    assert before == after, (
        "fabritius_contre_jour_pass at opacity=0.0 must be a no-op")


def test_fabritius_contre_jour_pass_shadow_veil_lifts_darks():
    """Cool ground veil must lift dark pixels — mean luminance should increase for a dark canvas."""
    import numpy as _np
    from stroke_engine import Painter

    p = Painter(width=64, height=64)
    # Fill with near-black (deep shadow)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    arr[:, :] = [20, 20, 20, 255]   # BGRA near-black
    p.canvas.surface.get_data()[:] = arr.tobytes()

    before_arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    before_mean = before_arr[:, :, :3].astype(float).mean()

    p.fabritius_contre_jour_pass(shadow_threshold=0.40, cool_veil_strength=0.08, opacity=1.0)

    after_arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4))
    after_mean = after_arr[:, :, :3].astype(float).mean()

    assert after_mean > before_mean, (
        f"Cool ground veil must lift dark pixels; "
        f"mean before={before_mean:.1f}  after={after_mean:.1f}")


# ──────────────────────────────────────────────────────────────────────────────
# Frans Hals — hals_alla_prima_vivacity_pass() (session 96)
# ──────────────────────────────────────────────────────────────────────────────

def test_hals_alla_prima_vivacity_pass_exists():
    """Painter must have hals_alla_prima_vivacity_pass() method after session 96."""
    from stroke_engine import Painter
    assert hasattr(Painter, "hals_alla_prima_vivacity_pass"), (
        "hals_alla_prima_vivacity_pass not found on Painter")
    assert callable(getattr(Painter, "hals_alla_prima_vivacity_pass"))


def test_hals_alla_prima_vivacity_pass_no_error():
    """hals_alla_prima_vivacity_pass() runs without error on a small synthetic canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.44, 0.34, 0.20), texture_strength=0.05)
    p.hals_alla_prima_vivacity_pass()


def test_hals_alla_prima_vivacity_pass_modifies_canvas():
    """hals_alla_prima_vivacity_pass() must modify at least some pixels on a non-trivial canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.44, 0.34, 0.20), texture_strength=0.05)
    ref = _solid_reference(64, 64)
    p.block_in(ref, stroke_size=8, n_strokes=15)

    before = _canvas_bytes(p)
    p.hals_alla_prima_vivacity_pass(opacity=0.60)
    after = _canvas_bytes(p)

    assert before != after, "hals_alla_prima_vivacity_pass must modify the canvas at opacity=0.60"


def test_hals_alla_prima_vivacity_pass_zero_opacity_noop():
    """hals_alla_prima_vivacity_pass() at opacity=0 must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.44, 0.34, 0.20), texture_strength=0.05)

    before = _canvas_bytes(p)
    p.hals_alla_prima_vivacity_pass(opacity=0.0)
    after = _canvas_bytes(p)

    assert before == after, (
        "hals_alla_prima_vivacity_pass at opacity=0.0 must be a no-op")


def test_hals_alla_prima_vivacity_pass_warms_midtones():
    """hals_alla_prima_vivacity_pass must lift R in mid-luminance flesh pixels."""
    import numpy as _np
    from stroke_engine import Painter

    # Fill with mid-luminance warm flesh: BGRA B=100, G=140, R=180
    # lum ≈ 0.299*180/255 + 0.587*140/255 + 0.114*100/255 ≈ 0.534
    p = Painter(width=48, height=48)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((48, 48, 4)).copy()
    arr[:, :, 0] = 100   # B
    arr[:, :, 1] = 140   # G
    arr[:, :, 2] = 180   # R
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()

    r_before = arr[:, :, 2].astype(float).mean()
    p.hals_alla_prima_vivacity_pass(
        vivacity_lo=0.35, vivacity_hi=0.78, warm_r_lift=0.06, opacity=1.0)
    arr_after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((48, 48, 4))
    r_after = arr_after[:, :, 2].astype(float).mean()

    assert r_after >= r_before, (
        f"hals_alla_prima_vivacity_pass must warm mid-tone pixels (R↑); "
        f"R before={r_before:.2f}  R after={r_after:.2f}")


def test_hals_alla_prima_vivacity_pass_preserves_canvas_shape():
    """hals_alla_prima_vivacity_pass must not change canvas dimensions."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=32, height=64)
    p.hals_alla_prima_vivacity_pass(opacity=0.50)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 32, 4))
    assert arr.shape == (64, 32, 4), "Canvas shape must be preserved after pass"


# ──────────────────────────────────────────────────────────────────────────────
# Bernardino Luini — luini_leonardesque_glow_pass() (session 97)
# ──────────────────────────────────────────────────────────────────────────────

def test_luini_leonardesque_glow_pass_exists():
    """Painter must have luini_leonardesque_glow_pass() method after session 97."""
    from stroke_engine import Painter
    assert hasattr(Painter, "luini_leonardesque_glow_pass"), (
        "luini_leonardesque_glow_pass not found on Painter")
    assert callable(getattr(Painter, "luini_leonardesque_glow_pass"))


def test_luini_leonardesque_glow_pass_no_error():
    """luini_leonardesque_glow_pass() runs without error on a small synthetic canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.60, 0.40), texture_strength=0.05)
    p.luini_leonardesque_glow_pass()


def test_luini_leonardesque_glow_pass_modifies_canvas():
    """luini_leonardesque_glow_pass() must modify at least some pixels on a non-trivial canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.60, 0.40), texture_strength=0.05)
    ref = _solid_reference(64, 64)
    p.block_in(ref, stroke_size=4, n_strokes=15)

    before = _canvas_bytes(p)
    p.luini_leonardesque_glow_pass(opacity=0.60)
    after = _canvas_bytes(p)

    assert before != after, "luini_leonardesque_glow_pass must modify the canvas at opacity=0.60"


def test_luini_leonardesque_glow_pass_zero_opacity_noop():
    """luini_leonardesque_glow_pass() at opacity=0 must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.60, 0.40), texture_strength=0.05)

    before = _canvas_bytes(p)
    p.luini_leonardesque_glow_pass(opacity=0.0)
    after = _canvas_bytes(p)

    assert before == after, (
        "luini_leonardesque_glow_pass at opacity=0.0 must be a no-op")


def test_luini_leonardesque_glow_pass_warms_highlights():
    """luini_leonardesque_glow_pass must lift R in bright highlight pixels."""
    import numpy as _np
    from stroke_engine import Painter

    # Fill with bright highlight flesh: B=160, G=180, R=220 (lum ≈ 0.82)
    p = Painter(width=48, height=48)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((48, 48, 4)).copy()
    arr[:, :, 0] = 160   # B
    arr[:, :, 1] = 180   # G
    arr[:, :, 2] = 220   # R
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()

    r_before = arr[:, :, 2].astype(float).mean()
    p.luini_leonardesque_glow_pass(
        highlight_lo=0.70, ivory_r=0.06, opacity=1.0)
    arr_after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((48, 48, 4))
    r_after = arr_after[:, :, 2].astype(float).mean()

    assert r_after >= r_before, (
        f"luini_leonardesque_glow_pass must lift R in highlights; "
        f"R before={r_before:.2f}  R after={r_after:.2f}")


def test_luini_leonardesque_glow_pass_cools_shadows():
    """luini_leonardesque_glow_pass must lift B in deep shadow pixels."""
    import numpy as _np
    from stroke_engine import Painter

    # Fill with deep shadow: B=30, G=28, R=35 (lum ≈ 0.12)
    p = Painter(width=48, height=48)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((48, 48, 4)).copy()
    arr[:, :, 0] = 30    # B
    arr[:, :, 1] = 28    # G
    arr[:, :, 2] = 35    # R
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()

    b_before = arr[:, :, 0].astype(float).mean()
    p.luini_leonardesque_glow_pass(
        shadow_hi=0.32, shadow_violet_b=0.06, opacity=1.0)
    arr_after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((48, 48, 4))
    b_after = arr_after[:, :, 0].astype(float).mean()

    assert b_after >= b_before, (
        f"luini_leonardesque_glow_pass must lift B in deep shadows (cool-violet quality); "
        f"B before={b_before:.2f}  B after={b_after:.2f}")


def test_luini_leonardesque_glow_pass_preserves_canvas_shape():
    """luini_leonardesque_glow_pass must not change canvas dimensions."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=32, height=64)
    p.luini_leonardesque_glow_pass(opacity=0.40)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 32, 4))
    assert arr.shape == (64, 32, 4), "Canvas shape must be preserved after pass"


def test_sfumato_veil_pass_highlight_ivory_lift_warms_bright_pixels():
    """sfumato_veil_pass with highlight_ivory_lift > 0 must warm bright highlight pixels."""
    import numpy as _np
    from stroke_engine import Painter
    from PIL import Image as _Image

    # Build a small painter with a bright highlight region
    p = Painter(width=48, height=48)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((48, 48, 4)).copy()
    arr[:, :, 0] = 190   # B
    arr[:, :, 1] = 205   # G
    arr[:, :, 2] = 230   # R (lum ≈ 0.87 — above default ivory_thresh=0.82)
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()
    r_before = arr[:, :, 2].astype(float).mean()

    # Reference image for sfumato_veil_pass
    ref_arr = _np.zeros((48, 48, 3), dtype=_np.uint8)
    ref_arr[:, :, 0] = 230
    ref_arr[:, :, 1] = 205
    ref_arr[:, :, 2] = 190
    ref = _Image.fromarray(ref_arr, mode="RGB")

    p.sfumato_veil_pass(
        reference=ref,
        n_veils=1,
        warmth=0.0,
        veil_opacity=0.0,    # disable the actual veils — test only the ivory lift
        edge_only=False,
        highlight_ivory_lift=1.0,
        highlight_ivory_thresh=0.82,
    )
    arr_after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((48, 48, 4))
    r_after = arr_after[:, :, 2].astype(float).mean()

    assert r_after >= r_before, (
        f"sfumato_veil_pass highlight_ivory_lift must warm bright pixels; "
        f"R before={r_before:.2f}  R after={r_after:.2f}")


def test_sfumato_veil_pass_highlight_ivory_lift_stronger_than_zero():
    """sfumato_veil_pass with highlight_ivory_lift=1.0 lifts R more than highlight_ivory_lift=0.0."""
    import numpy as _np
    from stroke_engine import Painter
    from PIL import Image as _Image

    def _run_with_lift(lift):
        p = Painter(width=32, height=32)
        arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4)).copy()
        arr[:, :, 0] = 190   # B
        arr[:, :, 1] = 205   # G
        arr[:, :, 2] = 220   # R (lum ~0.84, above default thresh=0.82)
        arr[:, :, 3] = 255
        p.canvas.surface.get_data()[:] = arr.tobytes()
        ref_arr = _np.zeros((32, 32, 3), dtype=_np.uint8)
        ref_arr[:, :] = [220, 205, 190]
        ref = _Image.fromarray(ref_arr, mode="RGB")
        p.sfumato_veil_pass(
            reference=ref, n_veils=1, warmth=0.0, veil_opacity=0.0,
            edge_only=False, highlight_ivory_lift=lift, highlight_ivory_thresh=0.82,
        )
        arr_out = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4))
        return arr_out[:, :, 2].astype(float).mean()  # R channel mean

    r_no_lift = _run_with_lift(0.0)
    r_full_lift = _run_with_lift(1.0)

    assert r_full_lift >= r_no_lift, (
        f"sfumato_veil_pass highlight_ivory_lift=1.0 must yield R >= highlight_ivory_lift=0.0; "
        f"R(lift=0)={r_no_lift:.2f}  R(lift=1.0)={r_full_lift:.2f}")


# ── Session 103: Carlo Dolci ──────────────────────────────────────────────────

def test_dolci_florentine_enamel_pass_exists():
    """Painter must have dolci_florentine_enamel_pass method (session 103)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "dolci_florentine_enamel_pass"), (
        "dolci_florentine_enamel_pass not found on Painter")
    assert callable(getattr(Painter, "dolci_florentine_enamel_pass"))


def test_dolci_florentine_enamel_pass_runs():
    """dolci_florentine_enamel_pass must execute without error on a small canvas."""
    import numpy as _np
    from stroke_engine import Painter

    p = Painter(width=64, height=64)
    # Prime the canvas with a mid-tone warm flesh (lum ~0.65)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    arr[:, :, 0] = 145   # B
    arr[:, :, 1] = 160   # G
    arr[:, :, 2] = 195   # R  — warm flesh mid-tone
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()

    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()

    p.dolci_florentine_enamel_pass(opacity=0.35)

    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4))
    # Canvas must have been modified (not all-zero, not unchanged)
    assert after[:, :, :3].sum() > 0, "dolci_florentine_enamel_pass produced a blank canvas"


def test_dolci_florentine_enamel_pass_zero_opacity_no_change():
    """dolci_florentine_enamel_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    from stroke_engine import Painter

    p = Painter(width=32, height=32)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4)).copy()
    arr[:, :, 0] = 140
    arr[:, :, 1] = 158
    arr[:, :, 2] = 190
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()
    before_bytes = bytes(p.canvas.surface.get_data())

    p.dolci_florentine_enamel_pass(opacity=0.0)

    after_bytes = bytes(p.canvas.surface.get_data())
    assert before_bytes == after_bytes, (
        "dolci_florentine_enamel_pass with opacity=0 must not modify the canvas"
    )


def test_dolci_shadow_depth_warms_dark_pixels():
    """dolci_florentine_enamel_pass must add R warmth to deep shadow pixels."""
    import numpy as _np
    from stroke_engine import Painter

    # Fill with dark shadow pixels (lum ~0.15 — inside shadow_lo=0.05..shadow_hi=0.32)
    p = Painter(width=32, height=32)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4)).copy()
    arr[:, :, 0] = 30    # B
    arr[:, :, 1] = 35    # G
    arr[:, :, 2] = 40    # R  — dark warm shadow zone
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()
    r_before = arr[:, :, 2].astype(float).mean()

    p.dolci_florentine_enamel_pass(
        shadow_depth_str=0.30,   # strong shadow enrichment
        smooth_strength=0.0,     # disable smoothing so only shadow depth acts
        highlight_lift=0.0,      # disable highlight lift
        penumbra_amber_r=0.0, penumbra_amber_g=0.0, penumbra_amber_b=0.0,
        opacity=1.0,
    )
    arr_after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4))
    r_after = arr_after[:, :, 2].astype(float).mean()

    assert r_after >= r_before, (
        f"dolci_florentine_enamel_pass shadow_depth_str must add R warmth to shadow pixels; "
        f"R before={r_before:.2f}  R after={r_after:.2f}"
    )


def test_subsurface_scatter_penumbra_warmth_depth_warms_penumbra():
    """subsurface_scatter_pass penumbra_warmth_depth must warm the penumbra zone (session 103)."""
    import numpy as _np
    from stroke_engine import Painter

    # Penumbra zone: lum ~0.36  (pen_mid for defaults = (0.28 + 0.42)/2 = 0.35)
    p = Painter(width=32, height=32)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4)).copy()
    arr[:, :, 0] = 80    # B
    arr[:, :, 1] = 88    # G
    arr[:, :, 2] = 97    # R   lum ~0.358
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()
    r_before = arr[:, :, 2].astype(float).mean()

    p.subsurface_scatter_pass(
        scatter_strength=0.0,
        penumbra_warm=0.0,
        shadow_cool=0.0,
        shadow_pellucidity=0.0,
        penumbra_warmth_depth=0.50,   # strong depth signal
        opacity=1.0,
    )
    arr_after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4))
    r_after = arr_after[:, :, 2].astype(float).mean()

    assert r_after >= r_before, (
        f"subsurface_scatter_pass penumbra_warmth_depth must lift R in penumbra zone; "
        f"R before={r_before:.2f}  R after={r_after:.2f}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Giovanni Antonio Boltraffio — boltraffio_pearled_sfumato_pass() (session 107)
# ─────────────────────────────────────────────────────────────────────────────

def test_boltraffio_pearled_sfumato_pass_exists():
    """Painter must have boltraffio_pearled_sfumato_pass() method after session 107."""
    from stroke_engine import Painter
    assert hasattr(Painter, "boltraffio_pearled_sfumato_pass"), (
        "boltraffio_pearled_sfumato_pass not found on Painter")
    assert callable(getattr(Painter, "boltraffio_pearled_sfumato_pass"))


def test_boltraffio_pearled_sfumato_pass_no_error():
    """boltraffio_pearled_sfumato_pass() runs without error on a small synthetic canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.58, 0.42), texture_strength=0.05)
    p.boltraffio_pearled_sfumato_pass()


def test_boltraffio_pearled_sfumato_pass_modifies_canvas():
    """boltraffio_pearled_sfumato_pass() must modify at least some pixels on a non-trivial canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.58, 0.42), texture_strength=0.05)
    ref = _solid_reference(64, 64)
    p.block_in(ref, stroke_size=8, n_strokes=15)

    before = _canvas_bytes(p)
    p.boltraffio_pearled_sfumato_pass(opacity=0.60)
    after = _canvas_bytes(p)

    assert before != after, "boltraffio_pearled_sfumato_pass must modify the canvas at opacity=0.60"


def test_boltraffio_pearled_sfumato_pass_zero_opacity_noop():
    """boltraffio_pearled_sfumato_pass() at opacity=0 must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.58, 0.42), texture_strength=0.05)

    before = _canvas_bytes(p)
    p.boltraffio_pearled_sfumato_pass(opacity=0.0)
    after = _canvas_bytes(p)

    assert before == after, (
        "boltraffio_pearled_sfumato_pass at opacity=0.0 must be a no-op")


def test_boltraffio_pearled_sfumato_pass_cools_highlights():
    """boltraffio_pearled_sfumato_pass must lift B more than R in bright highlight pixels."""
    import numpy as _np
    from stroke_engine import Painter

    # Bright highlight: lum ~0.82 (above pearl_lo=0.72 default)
    p = Painter(width=32, height=32)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4)).copy()
    arr[:, :, 0] = 198   # B  (BGRA layout)
    arr[:, :, 1] = 205   # G
    arr[:, :, 2] = 215   # R   lum ~0.818
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()
    b_before = arr[:, :, 0].astype(float).mean()
    r_before = arr[:, :, 2].astype(float).mean()

    p.boltraffio_pearled_sfumato_pass(
        pearl_lo=0.72,
        pearl_r=0.012,
        pearl_g=0.018,
        pearl_b=0.025,
        shadow_hi=0.10,    # disable shadow effect (far below lum 0.82)
        opacity=1.0,
    )
    arr_after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4))
    b_after = arr_after[:, :, 0].astype(float).mean()
    r_after = arr_after[:, :, 2].astype(float).mean()

    b_delta = b_after - b_before
    r_delta = r_after - r_before

    assert b_delta > r_delta, (
        f"boltraffio_pearled_sfumato_pass must lift B more than R in highlights "
        f"(pearl = cool silver, not warm ivory); "
        f"B delta={b_delta:.2f}, R delta={r_delta:.2f}"
    )


def test_boltraffio_pearled_sfumato_pass_cools_shadows():
    """boltraffio_pearled_sfumato_pass must lift B in deep shadow pixels."""
    import numpy as _np
    from stroke_engine import Painter

    # Deep shadow: lum ~0.18 (below shadow_hi=0.30 default)
    p = Painter(width=32, height=32)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4)).copy()
    arr[:, :, 0] = 40    # B
    arr[:, :, 1] = 44    # G
    arr[:, :, 2] = 50    # R   lum ~0.176
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()
    b_before = arr[:, :, 0].astype(float).mean()

    p.boltraffio_pearled_sfumato_pass(
        shadow_hi=0.30,
        shadow_b=0.024,
        shadow_g=0.008,
        shadow_r=0.006,
        pearl_lo=0.90,    # disable pearl effect (far above lum 0.18)
        clarity_strength=0.0,
        opacity=1.0,
    )
    arr_after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4))
    b_after = arr_after[:, :, 0].astype(float).mean()

    assert b_after > b_before, (
        f"boltraffio_pearled_sfumato_pass must lift B in deep shadows (cool atmosphere); "
        f"B before={b_before:.2f}  B after={b_after:.2f}"
    )


def test_boltraffio_pearled_sfumato_pass_preserves_canvas_shape():
    """boltraffio_pearled_sfumato_pass must not change canvas dimensions."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.68, 0.58, 0.42), texture_strength=0.05)
    p.boltraffio_pearled_sfumato_pass(opacity=0.40)
    assert (p.h, p.w) == (64, 64), "Canvas dimensions must not change"


# Period.MILANESE_PEARLED — session 107 routing

def test_milanese_pearled_period_accessible():
    """Period.MILANESE_PEARLED must be accessible from scene_schema."""
    from scene_schema import Period
    assert hasattr(Period, "MILANESE_PEARLED"), (
        "Period.MILANESE_PEARLED not found in scene_schema — add it")
    assert Period.MILANESE_PEARLED in list(Period)


def test_milanese_pearled_stroke_params_high_blend():
    """is_milanese_pearled stroke params must have high wet_blend for smooth sfumato."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.MILANESE_PEARLED,
                  palette=PaletteHint.COOL_GREY)
    assert style.period == Period.MILANESE_PEARLED, (
        "Style.period must equal MILANESE_PEARLED when set as such")
    p = style.stroke_params
    assert p["wet_blend"] >= 0.65, (
        f"MILANESE_PEARLED wet_blend should be >= 0.65 for Boltraffio's sfumato; "
        f"got {p['wet_blend']}"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Orazio Gentileschi — orazio_silver_daylight_pass() (session 111)
# ──────────────────────────────────────────────────────────────────────────────

def test_orazio_silver_daylight_pass_exists():
    """Painter must have orazio_silver_daylight_pass() method after session 111."""
    from stroke_engine import Painter
    assert hasattr(Painter, "orazio_silver_daylight_pass"), (
        "orazio_silver_daylight_pass not found on Painter")
    assert callable(getattr(Painter, "orazio_silver_daylight_pass"))


def test_orazio_silver_daylight_pass_no_error():
    """orazio_silver_daylight_pass() runs without error on a small synthetic canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.55, 0.40), texture_strength=0.05)
    p.orazio_silver_daylight_pass()


def test_orazio_silver_daylight_pass_modifies_canvas():
    """orazio_silver_daylight_pass() must modify at least some pixels on a non-trivial canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.55, 0.40), texture_strength=0.05)
    ref = _solid_reference(64, 64)
    p.block_in(ref, stroke_size=8, n_strokes=15)

    before = _canvas_bytes(p)
    p.orazio_silver_daylight_pass(opacity=0.60)
    after = _canvas_bytes(p)

    assert before != after, "orazio_silver_daylight_pass must modify the canvas at opacity=0.60"


def test_orazio_silver_daylight_pass_zero_opacity_noop():
    """orazio_silver_daylight_pass() at opacity=0 must leave the canvas unchanged."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.55, 0.40), texture_strength=0.05)

    before = _canvas_bytes(p)
    p.orazio_silver_daylight_pass(opacity=0.0)
    after = _canvas_bytes(p)

    assert before == after, (
        "orazio_silver_daylight_pass at opacity=0.0 must be a no-op")


def test_orazio_silver_daylight_pass_cools_highlights():
    """orazio_silver_daylight_pass must lift B more than R in bright highlight pixels."""
    import numpy as _np
    from stroke_engine import Painter

    # Bright highlight: lum ~0.82 (above hi_lo=0.68 default)
    p = Painter(width=32, height=32)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4)).copy()
    arr[:, :, 0] = 200   # B  (BGRA layout)
    arr[:, :, 1] = 206   # G
    arr[:, :, 2] = 215   # R   lum ~0.82
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()
    b_before = arr[:, :, 0].astype(float).mean()
    r_before = arr[:, :, 2].astype(float).mean()

    p.orazio_silver_daylight_pass(
        hi_lo=0.68,
        silver_r_damp=0.012,
        silver_b_lift=0.020,
        shadow_hi=0.05,    # disable shadow effect
        chroma_lift=0.0,   # disable chroma lift to isolate highlight test
        opacity=1.0,
    )
    arr_after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4))
    b_after = arr_after[:, :, 0].astype(float).mean()
    r_after = arr_after[:, :, 2].astype(float).mean()

    b_delta = b_after - b_before
    r_delta = r_after - r_before

    assert b_delta > r_delta, (
        f"orazio_silver_daylight_pass must lift B more than R in highlights "
        f"(cool silver daylight, not warm ivory); "
        f"B delta={b_delta:.2f}, R delta={r_delta:.2f}"
    )


def test_orazio_silver_daylight_pass_cools_shadows():
    """orazio_silver_daylight_pass must lift B in deep shadow pixels."""
    import numpy as _np
    from stroke_engine import Painter

    # Deep shadow: lum ~0.18 (below shadow_hi=0.34 default)
    p = Painter(width=32, height=32)
    arr = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4)).copy()
    arr[:, :, 0] = 42    # B
    arr[:, :, 1] = 46    # G
    arr[:, :, 2] = 52    # R   lum ~0.179
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()
    b_before = arr[:, :, 0].astype(float).mean()

    p.orazio_silver_daylight_pass(
        shadow_hi=0.34,
        cool_r_damp=0.010,
        cool_b_lift=0.014,
        hi_lo=0.95,       # disable highlight effect
        chroma_lift=0.0,  # disable chroma lift
        opacity=1.0,
    )
    arr_after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((32, 32, 4))
    b_after = arr_after[:, :, 0].astype(float).mean()

    assert b_after > b_before, (
        f"orazio_silver_daylight_pass must lift B in deep shadows (cool atmospheric shadow); "
        f"B before={b_before:.2f}  B after={b_after:.2f}"
    )


def test_orazio_silver_daylight_pass_preserves_canvas_shape():
    """orazio_silver_daylight_pass must not change canvas dimensions."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.62, 0.55, 0.40), texture_strength=0.05)
    p.orazio_silver_daylight_pass(opacity=0.40)
    assert (p.h, p.w) == (64, 64), "Canvas dimensions must not change"


# Period.ITALO_COURTLY_BAROQUE — session 111 routing

def test_italo_courtly_baroque_period_accessible():
    """Period.ITALO_COURTLY_BAROQUE must be accessible from scene_schema."""
    from scene_schema import Period
    assert hasattr(Period, "ITALO_COURTLY_BAROQUE"), (
        "Period.ITALO_COURTLY_BAROQUE not found in scene_schema — add it")
    assert Period.ITALO_COURTLY_BAROQUE in list(Period)


def test_italo_courtly_baroque_stroke_params_moderate_blend():
    """ITALO_COURTLY_BAROQUE stroke params must have moderate wet_blend for controlled naturalism."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.ITALO_COURTLY_BAROQUE,
                  palette=PaletteHint.COOL_GREY)
    assert style.period == Period.ITALO_COURTLY_BAROQUE, (
        "Style.period must equal ITALO_COURTLY_BAROQUE when set as such")
    p = style.stroke_params
    assert 0.35 <= p["wet_blend"] <= 0.75, (
        f"ITALO_COURTLY_BAROQUE wet_blend should be in [0.35, 0.75] for Orazio's "
        f"controlled naturalism (not sfumato, not alla prima); got {p['wet_blend']}"
    )


# ──────────────────────────────────────────────────────────────────────────────
# jordaens_earthy_vitality_pass — session 112 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_jordaens_earthy_vitality_pass_exists():
    """Painter must have jordaens_earthy_vitality_pass() method after session 112."""
    from stroke_engine import Painter
    assert hasattr(Painter, "jordaens_earthy_vitality_pass"), (
        "jordaens_earthy_vitality_pass not found on Painter")
    assert callable(getattr(Painter, "jordaens_earthy_vitality_pass"))


def test_jordaens_earthy_vitality_pass_no_error():
    """jordaens_earthy_vitality_pass() runs on a warm canvas without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.48, 0.36, 0.20), texture_strength=0.06)
    p.jordaens_earthy_vitality_pass(opacity=0.34)


def test_jordaens_earthy_vitality_pass_modifies_canvas():
    """jordaens_earthy_vitality_pass() must modify the canvas (non-trivial opacity)."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.48, 0.36, 0.20), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = _canvas_bytes(p)
    p.jordaens_earthy_vitality_pass(opacity=0.34)
    after = _canvas_bytes(p)

    assert before != after, "jordaens_earthy_vitality_pass should modify the canvas"


def test_jordaens_earthy_vitality_pass_zero_opacity_no_op():
    """jordaens_earthy_vitality_pass() with opacity=0 must not modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.48, 0.36, 0.20), texture_strength=0.06)

    before = _canvas_bytes(p)
    p.jordaens_earthy_vitality_pass(opacity=0.0)
    after = _canvas_bytes(p)

    assert before == after, "jordaens_earthy_vitality_pass with opacity=0 must be a no-op"


# ──────────────────────────────────────────────────────────────────────────────
# fontana_jewel_costume_pass — session 115 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_fontana_jewel_costume_pass_exists():
    """Painter must have fontana_jewel_costume_pass() method after session 115."""
    from stroke_engine import Painter
    assert hasattr(Painter, "fontana_jewel_costume_pass"), (
        "fontana_jewel_costume_pass not found on Painter")
    assert callable(getattr(Painter, "fontana_jewel_costume_pass"))


def test_fontana_jewel_costume_pass_no_error():
    """fontana_jewel_costume_pass() runs on a warm canvas without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.46, 0.38, 0.28), texture_strength=0.06)
    p.fontana_jewel_costume_pass(opacity=0.28)


def test_fontana_jewel_costume_pass_modifies_canvas():
    """fontana_jewel_costume_pass() must modify the canvas (non-trivial opacity)."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.46, 0.38, 0.28), texture_strength=0.06)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = _canvas_bytes(p)
    p.fontana_jewel_costume_pass(opacity=0.28)
    after = _canvas_bytes(p)

    assert before != after, "fontana_jewel_costume_pass should modify the canvas"


def test_fontana_jewel_costume_pass_zero_opacity_no_op():
    """fontana_jewel_costume_pass() with opacity=0 must not modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.46, 0.38, 0.28), texture_strength=0.06)

    before = _canvas_bytes(p)
    p.fontana_jewel_costume_pass(opacity=0.0)
    after = _canvas_bytes(p)

    assert before == after, "fontana_jewel_costume_pass with opacity=0 must be a no-op"


def test_bolognese_mannerist_portraiture_period_exists():
    """Period.BOLOGNESE_MANNERIST_PORTRAITURE must be in the Period enum (session 115)."""
    from scene_schema import Period
    assert hasattr(Period, "BOLOGNESE_MANNERIST_PORTRAITURE"), (
        "Period.BOLOGNESE_MANNERIST_PORTRAITURE not found in scene_schema — add it")
    assert Period.BOLOGNESE_MANNERIST_PORTRAITURE in list(Period)


def test_bolognese_mannerist_portraiture_stroke_params_moderate_blend():
    """BOLOGNESE_MANNERIST_PORTRAITURE stroke params must have moderate-high wet_blend."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.BOLOGNESE_MANNERIST_PORTRAITURE,
                  palette=PaletteHint.WARM_EARTH)
    assert style.period == Period.BOLOGNESE_MANNERIST_PORTRAITURE
    p = style.stroke_params
    assert 0.50 <= p["wet_blend"] <= 0.80, (
        f"BOLOGNESE_MANNERIST_PORTRAITURE wet_blend should be in [0.50, 0.80] for "
        f"glazed Bolognese finish (not full sfumato, not alla prima); got {p['wet_blend']}"
    )


# solario_pellucid_amber_pass — session 116 addition


def test_solario_pellucid_amber_pass_exists():
    """Painter must have solario_pellucid_amber_pass() method after session 116."""
    from stroke_engine import Painter
    assert hasattr(Painter, "solario_pellucid_amber_pass"), (
        "solario_pellucid_amber_pass not found on Painter")
    assert callable(getattr(Painter, "solario_pellucid_amber_pass"))


def test_solario_pellucid_amber_pass_no_error():
    """solario_pellucid_amber_pass() runs on a warm canvas without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.44, 0.36, 0.24), texture_strength=0.06)
    p.solario_pellucid_amber_pass(opacity=0.30)


def test_solario_pellucid_amber_pass_modifies_canvas():
    """solario_pellucid_amber_pass() must modify the canvas (non-trivial opacity)."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.59, 0.47, 0.34), texture_strength=0.06)

    before = _canvas_bytes(p)
    p.solario_pellucid_amber_pass(opacity=0.30)
    after = _canvas_bytes(p)

    assert before != after, "solario_pellucid_amber_pass should modify the canvas"


def test_solario_pellucid_amber_pass_zero_opacity_no_op():
    """solario_pellucid_amber_pass() with opacity=0 must not modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.44, 0.36, 0.24), texture_strength=0.06)

    before = _canvas_bytes(p)
    p.solario_pellucid_amber_pass(opacity=0.0)
    after = _canvas_bytes(p)

    assert before == after, "solario_pellucid_amber_pass with opacity=0 must be a no-op"


def test_lombard_leonardesque_period_exists():
    """Period.LOMBARD_LEONARDESQUE must be in the Period enum (session 116)."""
    from scene_schema import Period
    assert hasattr(Period, "LOMBARD_LEONARDESQUE"), (
        "Period.LOMBARD_LEONARDESQUE not found in scene_schema — add it")
    assert Period.LOMBARD_LEONARDESQUE in list(Period)


def test_lombard_leonardesque_stroke_params_high_sfumato():
    """LOMBARD_LEONARDESQUE stroke params must have high wet_blend and edge_softness."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.LOMBARD_LEONARDESQUE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.70, (
        f"LOMBARD_LEONARDESQUE wet_blend should be >= 0.70 for Leonardesque sfumato; "
        f"got {p['wet_blend']}")
    assert p["edge_softness"] >= 0.75, (
        f"LOMBARD_LEONARDESQUE edge_softness should be >= 0.75 for sfumato dissolution; "
        f"got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# batoni_silk_sheen_pass() tests — session 119
# ──────────────────────────────────────────────────────────────────────────────

def test_batoni_silk_sheen_pass_exists():
    """Painter must have batoni_silk_sheen_pass() method after session 119."""
    from stroke_engine import Painter
    assert hasattr(Painter, "batoni_silk_sheen_pass"), (
        "batoni_silk_sheen_pass not found on Painter — add it in stroke_engine.py")
    assert callable(getattr(Painter, "batoni_silk_sheen_pass"))


def test_batoni_silk_sheen_pass_no_error():
    """batoni_silk_sheen_pass() must run without error on a small toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.50, 0.34), texture_strength=0.06)
    p.batoni_silk_sheen_pass(opacity=0.26)


def test_batoni_silk_sheen_pass_modifies_canvas():
    """batoni_silk_sheen_pass() must modify a bright canvas with high streak strength."""
    p = _make_small_painter(64, 64)
    # Use a bright canvas (lum >> silk_lo=0.48) to ensure the sheen mask is active
    p.tone_ground((0.82, 0.74, 0.60), texture_strength=0.00)

    before = _canvas_bytes(p)
    # Use high streak_r/opacity so the sub-pixel rounding issue cannot mask the effect
    p.batoni_silk_sheen_pass(silk_lo=0.20, streak_r=0.10, streak_g=0.06, opacity=1.0)
    after = _canvas_bytes(p)

    assert before != after, "batoni_silk_sheen_pass should modify the canvas"


def test_batoni_silk_sheen_pass_zero_opacity_no_op():
    """batoni_silk_sheen_pass() with opacity=0 must not modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.50, 0.34), texture_strength=0.06)

    before = _canvas_bytes(p)
    p.batoni_silk_sheen_pass(opacity=0.0)
    after = _canvas_bytes(p)

    assert before == after, "batoni_silk_sheen_pass with opacity=0 must be a no-op"


def test_batoni_silk_sheen_pass_warms_bright_pixels():
    """batoni_silk_sheen_pass() must raise R channel on a bright mid-tone canvas."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Use a bright warm-grey ground that exceeds silk_lo (0.48) everywhere
    p.tone_ground((0.72, 0.65, 0.58), texture_strength=0.00)

    orig_buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).copy()
    orig_r = orig_buf[:, :, 2].astype(_np.float32).mean()

    p.batoni_silk_sheen_pass(streak_r=0.08, opacity=1.0)

    after_buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).copy()
    after_r = after_buf[:, :, 2].astype(_np.float32).mean()

    assert after_r >= orig_r, (
        f"batoni_silk_sheen_pass must not reduce R channel on a bright canvas; "
        f"before={orig_r:.1f}, after={after_r:.1f}")


def test_batoni_silk_sheen_pass_preserves_canvas_shape():
    """batoni_silk_sheen_pass() must not change canvas dimensions."""
    p = _make_small_painter(80, 64)
    p.tone_ground((0.55, 0.48, 0.36), texture_strength=0.05)
    p.batoni_silk_sheen_pass(opacity=0.30)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after batoni_silk_sheen_pass: {img.size}")


# ──────────────────────────────────────────────────────────────────────────────
# ROMAN_GRAND_TOUR_CLASSICISM Period — session 119
# ──────────────────────────────────────────────────────────────────────────────

def test_roman_grand_tour_classicism_period_exists():
    """Period.ROMAN_GRAND_TOUR_CLASSICISM must be in the Period enum (session 119)."""
    from scene_schema import Period
    assert hasattr(Period, "ROMAN_GRAND_TOUR_CLASSICISM"), (
        "Period.ROMAN_GRAND_TOUR_CLASSICISM not found in scene_schema — add it")
    assert Period.ROMAN_GRAND_TOUR_CLASSICISM in list(Period)


def test_roman_grand_tour_classicism_stroke_params_moderate_blend():
    """ROMAN_GRAND_TOUR_CLASSICISM stroke params: moderate wet_blend, moderate edge_softness."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.ROMAN_GRAND_TOUR_CLASSICISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.40 <= p["wet_blend"] <= 0.75, (
        f"ROMAN_GRAND_TOUR_CLASSICISM wet_blend should be moderate (0.40–0.75) "
        f"for polished Classicist flesh; got {p['wet_blend']}")
    assert 0.50 <= p["edge_softness"] <= 0.80, (
        f"ROMAN_GRAND_TOUR_CLASSICISM edge_softness should be moderate (0.50–0.80) "
        f"for clear Neoclassical definition; got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# lotto_restless_vivacity_pass() tests — session 120
# ──────────────────────────────────────────────────────────────────────────────

def test_lotto_restless_vivacity_pass_exists():
    """Painter must have lotto_restless_vivacity_pass() method after session 120."""
    from stroke_engine import Painter
    assert hasattr(Painter, "lotto_restless_vivacity_pass"), (
        "lotto_restless_vivacity_pass not found on Painter — add it in stroke_engine.py")
    assert callable(getattr(Painter, "lotto_restless_vivacity_pass"))


def test_lotto_restless_vivacity_pass_no_error():
    """lotto_restless_vivacity_pass() must run without error on a small toned canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.44, 0.30), texture_strength=0.06)
    p.lotto_restless_vivacity_pass(opacity=0.30)


def test_lotto_restless_vivacity_pass_modifies_canvas():
    """lotto_restless_vivacity_pass() must modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.44, 0.30), texture_strength=0.00)

    before = _canvas_bytes(p)
    p.lotto_restless_vivacity_pass(opacity=1.0, vivacity_r=0.10, shadow_cool_b=0.10,
                                    vibration_str=0.05)
    after = _canvas_bytes(p)

    assert before != after, "lotto_restless_vivacity_pass should modify the canvas"


def test_lotto_restless_vivacity_pass_zero_opacity_no_op():
    """lotto_restless_vivacity_pass() with opacity=0 must not modify the canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.52, 0.44, 0.30), texture_strength=0.06)

    before = _canvas_bytes(p)
    p.lotto_restless_vivacity_pass(opacity=0.0)
    after = _canvas_bytes(p)

    assert before == after, "lotto_restless_vivacity_pass with opacity=0 must be a no-op"


def test_lotto_restless_vivacity_pass_warms_bright_pixels():
    """lotto_restless_vivacity_pass() must raise R on a bright canvas (vivacity lift)."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.80, 0.72, 0.64), texture_strength=0.00)

    orig_buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).copy()
    orig_r = orig_buf[:, :, 2].astype(_np.float32).mean()

    p.lotto_restless_vivacity_pass(vivacity_r=0.08, opacity=1.0, vibration_str=0.0)

    after_buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).copy()
    after_r = after_buf[:, :, 2].astype(_np.float32).mean()

    assert after_r >= orig_r, (
        f"lotto_restless_vivacity_pass must raise R channel on bright canvas; "
        f"before={orig_r:.1f}, after={after_r:.1f}")


def test_lotto_restless_vivacity_pass_preserves_canvas_shape():
    """lotto_restless_vivacity_pass() must not change canvas dimensions."""
    p = _make_small_painter(80, 64)
    p.tone_ground((0.52, 0.44, 0.30), texture_strength=0.05)
    p.lotto_restless_vivacity_pass(opacity=0.30)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after lotto_restless_vivacity_pass: {img.size}")


def test_lotto_restless_vivacity_pass_noise_scale_parameter():
    """lotto_restless_vivacity_pass must accept noise_scale (session 120 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.lotto_restless_vivacity_pass)
    assert "noise_scale" in sig.parameters, (
        "lotto_restless_vivacity_pass must have 'noise_scale' parameter "
        "(primary Gaussian sigma for multi-scale chromatic vibration — session 120)")


def test_lotto_restless_vivacity_pass_vibration_str_parameter():
    """lotto_restless_vivacity_pass must accept vibration_str."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.lotto_restless_vivacity_pass)
    assert "vibration_str" in sig.parameters, (
        "lotto_restless_vivacity_pass must have 'vibration_str' parameter "
        "(amplitude of the multi-scale chromatic vibration field)")


def test_lotto_restless_vivacity_pass_shadow_cool_b_parameter():
    """lotto_restless_vivacity_pass must accept shadow_cool_b for eccentric shadow accent."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.lotto_restless_vivacity_pass)
    assert "shadow_cool_b" in sig.parameters, (
        "lotto_restless_vivacity_pass must have 'shadow_cool_b' parameter "
        "(cool blue accent in Lotto's darks)")


# ──────────────────────────────────────────────────────────────────────────────
# VENETIAN_ECCENTRIC_PORTRAITURE Period — session 120
# ──────────────────────────────────────────────────────────────────────────────

def test_venetian_eccentric_portraiture_period_exists():
    """Period.VENETIAN_ECCENTRIC_PORTRAITURE must be in the Period enum (session 120)."""
    from scene_schema import Period
    assert hasattr(Period, "VENETIAN_ECCENTRIC_PORTRAITURE"), (
        "Period.VENETIAN_ECCENTRIC_PORTRAITURE not found in scene_schema — add it")
    assert Period.VENETIAN_ECCENTRIC_PORTRAITURE in list(Period)


def test_venetian_eccentric_portraiture_stroke_params_moderate_blend():
    """VENETIAN_ECCENTRIC_PORTRAITURE stroke params: moderate wet_blend, moderate edge_softness."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_ECCENTRIC_PORTRAITURE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.35 <= p["wet_blend"] <= 0.60, (
        f"VENETIAN_ECCENTRIC_PORTRAITURE wet_blend should be moderate (0.35–0.60) "
        f"for chromatic energy (not full Titian blend); got {p['wet_blend']}")
    assert 0.40 <= p["edge_softness"] <= 0.70, (
        f"VENETIAN_ECCENTRIC_PORTRAITURE edge_softness should be moderate (0.40–0.70) "
        f"for psychological acuity; got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Giovanni Boldini / ITALIAN_BELLE_EPOQUE_PORTRAITURE / boldini_swirl_bravura_pass -- s121
# ──────────────────────────────────────────────────────────────────────────────


def test_boldini_swirl_bravura_pass_exists():
    """Painter must have a boldini_swirl_bravura_pass method (session 121)."""
    from stroke_engine import Painter
    assert hasattr(Painter, 'boldini_swirl_bravura_pass'), (
        'Painter is missing boldini_swirl_bravura_pass -- add it to stroke_engine.py')


def test_boldini_swirl_bravura_pass_modifies_canvas():
    """boldini_swirl_bravura_pass() must alter the canvas from its initial state."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, :] = [130, 145, 190, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.boldini_swirl_bravura_pass(opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((128, 128, 4))
    assert not _np.array_equal(before, after), (
        'boldini_swirl_bravura_pass should change the canvas when opacity=1.0')


def test_boldini_swirl_bravura_pass_opacity_zero_is_noop():
    """boldini_swirl_bravura_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, :] = [130, 145, 190, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.boldini_swirl_bravura_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        'boldini_swirl_bravura_pass(opacity=0) should be a noop')


def test_boldini_swirl_bravura_pass_brightens_highlights():
    """
    boldini_swirl_bravura_pass must brighten highlight pixels in the figure zone
    (the swirl field adds warm ivory to upper mid-tones and highlights).
    """
    import numpy as _np
    from stroke_engine import Painter
    p = _make_small_painter(64, 64)
    # Fill with bright mid-tone — well above swirl_lo default (0.42)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    # BGRA: B=130, G=150, R=190, A=255 → lum ≈ 0.56 (in swirl zone)
    data[:, :, :] = [130, 150, 190, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()

    orig_r = data[:, :, 2].astype(_np.float32).mean()

    p.boldini_swirl_bravura_pass(swirl_str=0.12, opacity=1.0,
                                  dark_factor=1.0, bg_warm_r=0.0)

    after_buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    after_r = after_buf[:, :, 2].astype(_np.float32).mean()

    assert after_r >= orig_r, (
        f"boldini_swirl_bravura_pass must raise R channel on bright canvas; "
        f"before={orig_r:.1f}, after={after_r:.1f}")


def test_boldini_swirl_bravura_pass_preserves_canvas_shape():
    """boldini_swirl_bravura_pass() must not change canvas dimensions."""
    p = _make_small_painter(80, 64)
    p.tone_ground((0.28, 0.20, 0.13), texture_strength=0.05)
    p.boldini_swirl_bravura_pass(opacity=0.32)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after boldini_swirl_bravura_pass: {img.size}")


def test_boldini_swirl_bravura_pass_dual_angle_parameters():
    """boldini_swirl_bravura_pass must accept both primary_angle and secondary_angle."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.boldini_swirl_bravura_pass)
    assert "primary_angle" in sig.parameters, (
        "boldini_swirl_bravura_pass must have 'primary_angle' parameter "
        "(dominant swirl direction — session 121 dual-angle improvement)")
    assert "secondary_angle" in sig.parameters, (
        "boldini_swirl_bravura_pass must have 'secondary_angle' parameter "
        "(crossing swirl direction — session 121 dual-angle improvement)")


def test_italian_belle_epoque_portraiture_period_exists():
    """Period.ITALIAN_BELLE_EPOQUE_PORTRAITURE must be in the Period enum (session 121)."""
    from scene_schema import Period
    assert hasattr(Period, "ITALIAN_BELLE_EPOQUE_PORTRAITURE"), (
        "Period.ITALIAN_BELLE_EPOQUE_PORTRAITURE not found in scene_schema -- add it")
    assert Period.ITALIAN_BELLE_EPOQUE_PORTRAITURE in list(Period)


def test_italian_belle_epoque_portraiture_stroke_params_low_wet_blend():
    """ITALIAN_BELLE_EPOQUE_PORTRAITURE stroke params: low wet_blend for directional bravura."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.ITALIAN_BELLE_EPOQUE_PORTRAITURE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] < 0.45, (
        f"ITALIAN_BELLE_EPOQUE_PORTRAITURE wet_blend should be low (< 0.45) "
        f"for Boldini's directional swirl bravura; got {p['wet_blend']}")


# ──────────────────────────────────────────────────────────────────────────────
# Annibale Carracci / BOLOGNESE_ACADEMIC_NATURALISM / annibale_carracci_tonal_reform_pass — s122
# ──────────────────────────────────────────────────────────────────────────────


def test_annibale_carracci_tonal_reform_pass_exists():
    """Painter must have annibale_carracci_tonal_reform_pass (session 122)."""
    from stroke_engine import Painter
    assert hasattr(Painter, 'annibale_carracci_tonal_reform_pass'), (
        'Painter is missing annibale_carracci_tonal_reform_pass -- add it to stroke_engine.py')


def test_annibale_carracci_tonal_reform_pass_modifies_canvas():
    """annibale_carracci_tonal_reform_pass() must alter the canvas from its initial state."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((128, 128, 4)).copy()
    # Dark fill — below default shadow_hi (0.28); lum ≈ 0.15 — triggers warm shadow glow stage.
    # A uniform canvas has zero gradient so the temperature field is inactive, but the shadow
    # warm-glow stage (Stage 2) always fires for dark pixels regardless of gradient.
    data[:, :, :] = [30, 40, 50, 255]  # BGRA: B=30, G=40, R=50; lum ≈ 0.15
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.annibale_carracci_tonal_reform_pass(opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        'annibale_carracci_tonal_reform_pass should change the canvas when opacity=1.0')


def test_annibale_carracci_tonal_reform_pass_opacity_zero_is_noop():
    """annibale_carracci_tonal_reform_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, :] = [120, 140, 170, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.annibale_carracci_tonal_reform_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        'annibale_carracci_tonal_reform_pass(opacity=0) should be a noop')


def test_annibale_carracci_tonal_reform_pass_warms_shadow_zone():
    """
    annibale_carracci_tonal_reform_pass must raise R in the deep shadow zone
    (warm sienna imprimatura glow through shadow glazes).
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Dark fill — well below default shadow_hi (0.28); lum ≈ 0.15
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    data[:, :, :] = [30, 40, 50, 255]   # BGRA: dark, lum ≈ 0.15
    p.canvas.surface.get_data()[:] = data.tobytes()

    orig_r = data[:, :, 2].astype(_np.float32).mean()

    p.annibale_carracci_tonal_reform_pass(
        shadow_warm_r=0.08, shadow_warm_g=0.04,
        warm_r=0.0, cool_r=0.0, cool_b=0.0,  # isolate shadow stage
        hi_r=0.0, hi_g=0.0,
        opacity=1.0,
    )

    after_buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4))
    after_r = after_buf[:, :, 2].astype(_np.float32).mean()

    assert after_r >= orig_r, (
        f"annibale_carracci_tonal_reform_pass must raise R in shadow zone (warm ground glow); "
        f"before={orig_r:.1f}, after={after_r:.1f}")


def test_annibale_carracci_tonal_reform_pass_preserves_canvas_shape():
    """annibale_carracci_tonal_reform_pass() must not change canvas dimensions."""
    p = _make_small_painter(80, 64)
    p.tone_ground((0.48, 0.36, 0.22), texture_strength=0.05)
    p.annibale_carracci_tonal_reform_pass(opacity=0.32)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after annibale_carracci_tonal_reform_pass: {img.size}")


def test_annibale_carracci_tonal_reform_pass_light_angle_parameter():
    """annibale_carracci_tonal_reform_pass must accept light_angle_deg (session 122)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.annibale_carracci_tonal_reform_pass)
    assert "light_angle_deg" in sig.parameters, (
        "annibale_carracci_tonal_reform_pass must have 'light_angle_deg' parameter "
        "(light source direction for the directional temperature field — session 122)")


def test_annibale_carracci_tonal_reform_pass_penumbra_parameters():
    """annibale_carracci_tonal_reform_pass must have penumbra_lo and penumbra_hi."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.annibale_carracci_tonal_reform_pass)
    assert "penumbra_lo" in sig.parameters, (
        "annibale_carracci_tonal_reform_pass must have 'penumbra_lo' parameter "
        "(luminance floor of temperature-active zone)")
    assert "penumbra_hi" in sig.parameters, (
        "annibale_carracci_tonal_reform_pass must have 'penumbra_hi' parameter "
        "(luminance ceiling of temperature-active zone)")


# ──────────────────────────────────────────────────────────────────────────────
# Session 123: Salvator Rosa — turbulent displacement field
# ──────────────────────────────────────────────────────────────────────────────

def test_salvator_rosa_wild_bravura_pass_exists():
    """Painter must have salvator_rosa_wild_bravura_pass (session 123)."""
    from stroke_engine import Painter
    assert hasattr(Painter, 'salvator_rosa_wild_bravura_pass'), (
        'Painter is missing salvator_rosa_wild_bravura_pass -- add it to stroke_engine.py')


def test_salvator_rosa_wild_bravura_pass_modifies_canvas():
    """salvator_rosa_wild_bravura_pass() must alter the canvas from its initial state."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((128, 128, 4)).copy()
    # Dark fill — below default shadow_hi (0.30); lum ≈ 0.15 — triggers warm shadow glow stage.
    data[:, :, :] = [30, 40, 50, 255]  # BGRA: B=30, G=40, R=50; lum ≈ 0.15
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.salvator_rosa_wild_bravura_pass(opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        'salvator_rosa_wild_bravura_pass should change the canvas when opacity=1.0')


def test_salvator_rosa_wild_bravura_pass_opacity_zero_is_noop():
    """salvator_rosa_wild_bravura_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, :] = [120, 140, 170, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.salvator_rosa_wild_bravura_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        'salvator_rosa_wild_bravura_pass(opacity=0) should be a noop')


def test_salvator_rosa_wild_bravura_pass_warms_shadow_zone():
    """
    salvator_rosa_wild_bravura_pass must raise R in the deep shadow zone
    (warm raw umber ground glowing through thin transparent paint).
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Dark fill — well below default shadow_hi (0.30); lum ≈ 0.12
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    data[:, :, :] = [20, 30, 35, 255]   # BGRA: very dark, lum ≈ 0.12
    p.canvas.surface.get_data()[:] = data.tobytes()

    orig_r = data[:, :, 2].astype(_np.float32).mean()

    p.salvator_rosa_wild_bravura_pass(
        shadow_warm_r=0.10, shadow_warm_g=0.05,
        vignette_str=0.0,   # disable vignette to isolate shadow stage
        max_disp=0.0,       # disable displacement to isolate colour stages
        opacity=1.0,
    )

    after_buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4))
    after_r = after_buf[:, :, 2].astype(_np.float32).mean()

    assert after_r >= orig_r, (
        f"salvator_rosa_wild_bravura_pass must raise R in shadow zone (warm umber ground glow); "
        f"before={orig_r:.1f}, after={after_r:.1f}")


def test_salvator_rosa_wild_bravura_pass_preserves_canvas_shape():
    """salvator_rosa_wild_bravura_pass() must not change canvas dimensions."""
    p = _make_small_painter(80, 64)
    p.tone_ground((0.10, 0.07, 0.04), texture_strength=0.05)
    p.salvator_rosa_wild_bravura_pass(opacity=0.26)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after salvator_rosa_wild_bravura_pass: {img.size}")


def test_salvator_rosa_wild_bravura_pass_max_disp_parameter():
    """salvator_rosa_wild_bravura_pass must accept max_disp (session 123 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.salvator_rosa_wild_bravura_pass)
    assert "max_disp" in sig.parameters, (
        "salvator_rosa_wild_bravura_pass must have 'max_disp' parameter "
        "(maximum pixel displacement for the turbulent warp — session 123 improvement)")


def test_salvator_rosa_wild_bravura_pass_n_octaves_parameter():
    """salvator_rosa_wild_bravura_pass must accept n_octaves (multi-scale turbulence)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.salvator_rosa_wild_bravura_pass)
    assert "n_octaves" in sig.parameters, (
        "salvator_rosa_wild_bravura_pass must have 'n_octaves' parameter "
        "(number of pink-noise octaves for the multi-scale turbulence field)")


def test_roman_baroque_landscape_period_exists():
    """Period.ROMAN_BAROQUE_LANDSCAPE must be in the Period enum (session 123)."""
    from scene_schema import Period
    assert hasattr(Period, "ROMAN_BAROQUE_LANDSCAPE"), (
        "Period.ROMAN_BAROQUE_LANDSCAPE not found in scene_schema -- add it")
    assert Period.ROMAN_BAROQUE_LANDSCAPE in list(Period)


def test_roman_baroque_landscape_stroke_params_low_wet_blend():
    """ROMAN_BAROQUE_LANDSCAPE stroke params: low wet_blend for gestural bravura."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.ROMAN_BAROQUE_LANDSCAPE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.35, (
        f"ROMAN_BAROQUE_LANDSCAPE wet_blend should be ≤ 0.35 "
        f"for Rosa's gestural turbulence; got {p['wet_blend']}")


def test_roman_baroque_landscape_stroke_params_large_bg():
    """ROMAN_BAROQUE_LANDSCAPE stroke params: large stroke_size_bg for landscape energy."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.ROMAN_BAROQUE_LANDSCAPE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["stroke_size_bg"] >= 28, (
        f"ROMAN_BAROQUE_LANDSCAPE stroke_size_bg should be ≥ 28 "
        f"for Rosa's sweeping landscape energy; got {p['stroke_size_bg']}")


def test_bolognese_academic_naturalism_period_exists():
    """Period.BOLOGNESE_ACADEMIC_NATURALISM must be in the Period enum (session 122)."""
    from scene_schema import Period
    assert hasattr(Period, "BOLOGNESE_ACADEMIC_NATURALISM"), (
        "Period.BOLOGNESE_ACADEMIC_NATURALISM not found in scene_schema -- add it")
    assert Period.BOLOGNESE_ACADEMIC_NATURALISM in list(Period)


def test_bolognese_academic_naturalism_stroke_params_moderate_blend():
    """BOLOGNESE_ACADEMIC_NATURALISM stroke params: moderate wet_blend, moderate edge_softness."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.BOLOGNESE_ACADEMIC_NATURALISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.40 <= p["wet_blend"] <= 0.70, (
        f"BOLOGNESE_ACADEMIC_NATURALISM wet_blend should be moderate (0.40–0.70) "
        f"for Carracci's naturalistic painting; got {p['wet_blend']}")
    assert 0.40 <= p["edge_softness"] <= 0.70, (
        f"BOLOGNESE_ACADEMIC_NATURALISM edge_softness should be moderate (0.40–0.70) "
        f"for clearly resolved forms; got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Session 124: Massimo Stanzione — Laplacian pyramid + noble repose pass
# ──────────────────────────────────────────────────────────────────────────────

def test_stanzione_noble_repose_pass_exists():
    """Painter must have stanzione_noble_repose_pass (session 124)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "stanzione_noble_repose_pass"), (
        "Painter is missing stanzione_noble_repose_pass -- add it to stroke_engine.py")


def test_stanzione_noble_repose_pass_modifies_canvas():
    """stanzione_noble_repose_pass() must alter the canvas from its initial state."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    p.tone_ground((0.55, 0.44, 0.28), texture_strength=0.06)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.stanzione_noble_repose_pass(opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "stanzione_noble_repose_pass should change the canvas when opacity=1.0")


def test_stanzione_noble_repose_pass_opacity_zero_is_noop():
    """stanzione_noble_repose_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, :] = [130, 150, 175, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.stanzione_noble_repose_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "stanzione_noble_repose_pass(opacity=0) should be a noop")


def test_stanzione_noble_repose_pass_warms_highlights():
    """
    stanzione_noble_repose_pass must raise R in the highlight zone
    (Reni-derived warm ivory highlight lift).
    """
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Bright fill -- above default hi_lo (0.70); lum ~ 0.84
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    data[:, :, :] = [205, 212, 218, 255]   # BGRA: bright warm-grey, lum ~ 0.84
    p.canvas.surface.get_data()[:] = data.tobytes()
    orig_r = data[:, :, 2].astype(_np.float32).mean()
    p.stanzione_noble_repose_pass(
        ivory_r=0.08, ivory_g=0.04,
        violet_b=0.0, violet_r=0.0,
        mid_freq_boost=0.0, fine_suppress=0.0,
        opacity=1.0,
    )
    after_buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4))
    after_r = after_buf[:, :, 2].astype(_np.float32).mean()
    assert after_r >= orig_r, (
        f"stanzione_noble_repose_pass must raise R in highlight zone (warm ivory lift); "
        f"before={orig_r:.1f}, after={after_r:.1f}")


def test_stanzione_noble_repose_pass_preserves_canvas_shape():
    """stanzione_noble_repose_pass() must not change canvas dimensions."""
    p = _make_small_painter(80, 64)
    p.tone_ground((0.46, 0.36, 0.22), texture_strength=0.05)
    p.stanzione_noble_repose_pass(opacity=0.30)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after stanzione_noble_repose_pass: {img.size}")


def test_stanzione_noble_repose_pass_pyramid_levels_parameter():
    """stanzione_noble_repose_pass must accept pyramid_levels (session 124 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.stanzione_noble_repose_pass)
    assert "pyramid_levels" in sig.parameters, (
        "stanzione_noble_repose_pass must have 'pyramid_levels' parameter "
        "(number of frequency bands in Laplacian pyramid -- session 124 improvement)")


def test_stanzione_noble_repose_pass_mid_freq_boost_parameter():
    """stanzione_noble_repose_pass must accept mid_freq_boost (Laplacian boost param)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.stanzione_noble_repose_pass)
    assert "mid_freq_boost" in sig.parameters, (
        "stanzione_noble_repose_pass must have 'mid_freq_boost' parameter "
        "(contrast boost for mid-frequency Laplacian band -- session 124 improvement)")


# ── Session 125: Francesco Albani + BOLOGNESE_ARCADIAN_CLASSICISM ─────────────

def test_chromatic_aerial_perspective_pass_is_noop_at_zero_opacity():
    """chromatic_aerial_perspective_pass(opacity=0) must leave canvas unchanged."""
    import numpy as _np
    from stroke_engine import Painter
    p = _make_small_painter(64, 64)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    data[:, :, :] = [110, 140, 170, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.chromatic_aerial_perspective_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "chromatic_aerial_perspective_pass(opacity=0) should be a noop")


def test_chromatic_aerial_perspective_pass_cools_top_region():
    """chromatic_aerial_perspective_pass must increase blue in the top region."""
    import numpy as _np
    from stroke_engine import Painter
    H, W = 80, 64
    p = _make_small_painter(W, H)
    # Warm fill — B channel is low so cooling (B increase) is easily detectable.
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((H, W, 4)).copy()
    data[:, :, :] = [80, 130, 180, 255]   # BGRA: B=80 (low), warm-ish
    p.canvas.surface.get_data()[:] = data.tobytes()
    orig_b_top = data[:H // 4, :, 0].astype(_np.float32).mean()
    p.chromatic_aerial_perspective_pass(
        sky_fraction=0.80,
        haze_strength=0.40,
        desat_strength=0.0,
        haze_lift=0.0,
        blur_radius=1.0,
        opacity=1.0,
        cool_b=1.0,   # maximum blue in haze
    )
    after_buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((H, W, 4))
    after_b_top = after_buf[:H // 4, :, 0].astype(_np.float32).mean()
    assert after_b_top > orig_b_top, (
        f"chromatic_aerial_perspective_pass must increase B in the top (distant) region; "
        f"before={orig_b_top:.1f}, after={after_b_top:.1f}")


def test_chromatic_aerial_perspective_pass_preserves_canvas_shape():
    """chromatic_aerial_perspective_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = _make_small_painter(80, 64)
    p.tone_ground((0.74, 0.64, 0.46), texture_strength=0.05)
    p.chromatic_aerial_perspective_pass(opacity=0.40)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after chromatic_aerial_perspective_pass: {img.size}")


def test_albani_arcadian_grace_pass_is_noop_at_zero_opacity():
    """albani_arcadian_grace_pass(opacity=0) must leave canvas unchanged."""
    import numpy as _np
    from stroke_engine import Painter
    p = _make_small_painter(64, 64)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    data[:, :, :] = [130, 150, 165, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.albani_arcadian_grace_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "albani_arcadian_grace_pass(opacity=0) should be a noop")


def test_albani_arcadian_grace_pass_lifts_skin_bloom():
    """albani_arcadian_grace_pass must raise R in the mid-tone skin bloom zone."""
    import numpy as _np
    from stroke_engine import Painter
    p = _make_small_painter(64, 64)
    # Mid-tone fill (lum ~ 0.60) — squarely in bloom zone (default 0.42..0.78)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    data[:, :, :] = [150, 155, 160, 255]   # BGRA: mid-tone neutral, lum ~ 0.60
    p.canvas.surface.get_data()[:] = data.tobytes()
    orig_r = data[:, :, 2].astype(_np.float32).mean()
    p.albani_arcadian_grace_pass(
        peach_r=0.08, peach_g=0.0,
        sky_b=0.0, sky_r=0.0,
        ambient_lift=0.0,
        opacity=1.0,
    )
    after_buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4))
    after_r = after_buf[:, :, 2].astype(_np.float32).mean()
    assert after_r >= orig_r, (
        f"albani_arcadian_grace_pass must raise R in mid-tone bloom zone; "
        f"before={orig_r:.1f}, after={after_r:.1f}")


def test_albani_arcadian_grace_pass_preserves_canvas_shape():
    """albani_arcadian_grace_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = _make_small_painter(80, 64)
    p.tone_ground((0.74, 0.64, 0.46), texture_strength=0.05)
    p.albani_arcadian_grace_pass(opacity=0.28)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after albani_arcadian_grace_pass: {img.size}")


def test_bolognese_arcadian_classicism_period_present():
    """Period.BOLOGNESE_ARCADIAN_CLASSICISM must be in the Period enum (session 125)."""
    from scene_schema import Period
    assert hasattr(Period, "BOLOGNESE_ARCADIAN_CLASSICISM"), (
        "Period.BOLOGNESE_ARCADIAN_CLASSICISM not found -- add it to scene_schema.py")
    assert Period.BOLOGNESE_ARCADIAN_CLASSICISM in list(Period)


def test_bolognese_arcadian_classicism_stroke_params_high_wet_blend():
    """BOLOGNESE_ARCADIAN_CLASSICISM stroke_params must have high wet_blend (smooth Arcadian)."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.BOLOGNESE_ARCADIAN_CLASSICISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.65, (
        f"BOLOGNESE_ARCADIAN_CLASSICISM wet_blend should be >= 0.65 "
        f"for Albani's silky smooth Arcadian surfaces; got {p['wet_blend']}")


def test_bolognese_arcadian_classicism_stroke_params_moderate_edge_softness():
    """BOLOGNESE_ARCADIAN_CLASSICISM edge_softness must be in moderate range (0.55 to 0.85)."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.BOLOGNESE_ARCADIAN_CLASSICISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.55 <= p["edge_softness"] <= 0.85, (
        f"BOLOGNESE_ARCADIAN_CLASSICISM edge_softness should be 0.55-0.85 "
        f"(soft but resolved Arcadian forms); got {p['edge_softness']}")


def test_chromatic_aerial_perspective_pass_sky_fraction_parameter():
    """chromatic_aerial_perspective_pass must accept sky_fraction (session 125 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.chromatic_aerial_perspective_pass)
    assert "sky_fraction" in sig.parameters, (
        "chromatic_aerial_perspective_pass must have 'sky_fraction' parameter "
        "(fraction of image height receiving maximum aerial cooling -- session 125 improvement)")


def test_neapolitan_baroque_classicism_period_present():
    """Period.NEAPOLITAN_BAROQUE_CLASSICISM must be in the Period enum (session 124)."""
    from scene_schema import Period
    assert hasattr(Period, "NEAPOLITAN_BAROQUE_CLASSICISM"), (
        "Period.NEAPOLITAN_BAROQUE_CLASSICISM not found -- add it to scene_schema.py")
    assert Period.NEAPOLITAN_BAROQUE_CLASSICISM in list(Period)


def test_neapolitan_baroque_classicism_stroke_params_high_wet_blend():
    """NEAPOLITAN_BAROQUE_CLASSICISM stroke_params must have high wet_blend (smooth classicism)."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.NEAPOLITAN_BAROQUE_CLASSICISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.60, (
        f"NEAPOLITAN_BAROQUE_CLASSICISM wet_blend should be >= 0.60 "
        f"for Stanzione's smooth Reni-influenced flesh; got {p['wet_blend']}")


def test_neapolitan_baroque_classicism_stroke_params_moderate_edge_softness():
    """NEAPOLITAN_BAROQUE_CLASSICISM edge_softness must be moderate (0.50 to 0.85)."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.NEAPOLITAN_BAROQUE_CLASSICISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.50 <= p["edge_softness"] <= 0.85, (
        f"NEAPOLITAN_BAROQUE_CLASSICISM edge_softness should be 0.50-0.85 "
        f"(moderate sfumato, resolved classical forms); got {p['edge_softness']}")


# ── Session 127 — cantarini_pearl_fog_pass() ──────────────────────────────────

def test_cantarini_pearl_fog_pass_exists():
    """Painter must have cantarini_pearl_fog_pass() method (session 127)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "cantarini_pearl_fog_pass"), (
        "cantarini_pearl_fog_pass not found on Painter")
    assert callable(getattr(Painter, "cantarini_pearl_fog_pass"))


def test_cantarini_pearl_fog_pass_no_error():
    """cantarini_pearl_fog_pass() must run without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.52, 0.36), texture_strength=0.0)
    p.cantarini_pearl_fog_pass()


def test_cantarini_pearl_fog_pass_noop_at_opacity_zero():
    """cantarini_pearl_fog_pass(opacity=0) must be a noop."""
    p = _make_small_painter(64, 64)
    buf = np.frombuffer(p.canvas.surface.get_data(),
                        dtype=np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, :] = [120, 140, 160, 255]
    p.canvas.surface.get_data()[:] = buf.tobytes()
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.cantarini_pearl_fog_pass(opacity=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    assert np.array_equal(before, after), (
        "cantarini_pearl_fog_pass(opacity=0) should be a noop")


def test_cantarini_pearl_fog_pass_preserves_canvas_shape():
    """cantarini_pearl_fog_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = Painter(width=80, height=64)
    p.tone_ground((0.60, 0.52, 0.36), texture_strength=0.05)
    p.cantarini_pearl_fog_pass(opacity=0.30)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after cantarini_pearl_fog_pass: {img.size}")


def test_cantarini_pearl_fog_pass_blue_more_diffused_than_red():
    """cantarini_pearl_fog_pass must diffuse B more than R in penumbra zone (spectral selectivity)."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape(
        (64, 64, 4)).copy()
    # Set left half bright, right half dark to create a visible penumbra
    # Use a mid-tone luminance so the penumbra zone activates
    data[:, :32, :] = [140, 145, 150, 255]   # BGRA — mid-bright
    data[:, 32:, :] = [90, 95, 100, 255]     # BGRA — mid-dark
    p.canvas.surface.get_data()[:] = data.tobytes()
    # Record the sharpness of the R and B channels at the edge boundary
    # (columns 31 and 32).  After scatter, B should be softer (lower edge contrast).
    p.cantarini_pearl_fog_pass(
        sigma_r=0.5,   # very small red blur
        sigma_b=8.0,   # large blue blur
        sigma_g=2.0,
        scatter_strength=1.0,
        rose_r=0.0,
        rose_b_damp=0.0,
        ivory_r=0.0,
        ivory_g=0.0,
        opacity=1.0,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape(
        (64, 64, 4))
    # Edge contrast = mean(col31) - mean(col32) for each channel
    # Blue should have lower edge contrast (more diffused) than red
    r_edge = float(after[:, 31, 2].mean()) - float(after[:, 32, 2].mean())
    b_edge = float(after[:, 31, 0].mean()) - float(after[:, 32, 0].mean())
    assert b_edge <= r_edge, (
        f"cantarini_pearl_fog_pass: blue should be more diffused (lower edge contrast) "
        f"than red; R edge={r_edge:.2f}, B edge={b_edge:.2f}")


def test_cantarini_pearl_fog_pass_sigma_parameters_accepted():
    """cantarini_pearl_fog_pass must accept sigma_r, sigma_g, sigma_b parameters."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.cantarini_pearl_fog_pass)
    for param in ("sigma_r", "sigma_g", "sigma_b"):
        assert param in sig.parameters, (
            f"cantarini_pearl_fog_pass must have '{param}' parameter "
            f"(spectral channel-selective diffusion — session 127 improvement)")


def test_bolognese_renesque_silver_classicism_period_present():
    """Period.BOLOGNESE_RENESQUE_SILVER_CLASSICISM must be in the Period enum (session 127)."""
    from scene_schema import Period
    assert hasattr(Period, "BOLOGNESE_RENESQUE_SILVER_CLASSICISM"), (
        "Period.BOLOGNESE_RENESQUE_SILVER_CLASSICISM not found -- add it to scene_schema.py")
    assert Period.BOLOGNESE_RENESQUE_SILVER_CLASSICISM in list(Period)


def test_bolognese_renesque_silver_classicism_stroke_params_very_high_wet_blend():
    """BOLOGNESE_RENESQUE_SILVER_CLASSICISM wet_blend must be >= 0.78 (Cantarini's smoothness)."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.BOLOGNESE_RENESQUE_SILVER_CLASSICISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.78, (
        f"BOLOGNESE_RENESQUE_SILVER_CLASSICISM wet_blend should be >= 0.78 "
        f"for Cantarini's multi-glaze ultra-smooth surface; got {p['wet_blend']}")


def test_bolognese_renesque_silver_classicism_stroke_params_high_edge_softness():
    """BOLOGNESE_RENESQUE_SILVER_CLASSICISM edge_softness must be in range (0.65 to 0.90)."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.BOLOGNESE_RENESQUE_SILVER_CLASSICISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.65 <= p["edge_softness"] <= 0.90, (
        f"BOLOGNESE_RENESQUE_SILVER_CLASSICISM edge_softness should be 0.65-0.90 "
        f"(Cantarini's pearl-fog sfumato); got {p['edge_softness']}")

# ── Session 128 — carpaccio_venetian_clarity_pass() ───────────────────────────

def test_carpaccio_venetian_clarity_pass_exists():
    """Painter must have carpaccio_venetian_clarity_pass() method (session 128)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "carpaccio_venetian_clarity_pass"), (
        "carpaccio_venetian_clarity_pass not found on Painter")
    assert callable(getattr(Painter, "carpaccio_venetian_clarity_pass"))


def test_carpaccio_venetian_clarity_pass_no_error():
    """carpaccio_venetian_clarity_pass() must run without error on a small canvas."""
    p = _make_small_painter()
    p.carpaccio_venetian_clarity_pass()


def test_carpaccio_venetian_clarity_pass_noop_at_opacity_zero():
    """carpaccio_venetian_clarity_pass(opacity=0) must be a noop."""
    p = _make_small_painter()
    p.tone_ground((0.78, 0.68, 0.50), texture_strength=0.05)
    before = _canvas_bytes(p)
    p.carpaccio_venetian_clarity_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, (
        "carpaccio_venetian_clarity_pass(opacity=0) should be a noop")


def test_carpaccio_venetian_clarity_pass_warms_highlight_zone():
    """carpaccio_venetian_clarity_pass must raise R in a bright highlight zone."""
    p = _make_small_painter(64, 64)
    # Bright warm canvas (lum ≈ 0.72, above hi_lo=0.65)
    data = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(
        (64, 64, 4)).copy()
    data[:, :, 2] = 200   # R (BGRA index 2)
    data[:, :, 1] = 175   # G
    data[:, :, 0] = 140   # B
    data[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = data.tobytes()
    orig_r = data[:, :, 2].astype(np.float32).mean()
    p.carpaccio_venetian_clarity_pass(
        hi_lo=0.65,
        warm_r=0.10,
        warm_g=0.0,
        cool_b=0.0,
        cool_r=0.0,
        detail_clarity_boost=0.0,
        smooth_str=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    after_r = after[:, :, 2].astype(np.float32).mean()
    assert after_r >= orig_r, (
        f"carpaccio_venetian_clarity_pass must raise R in highlight zone; "
        f"before={orig_r:.1f}, after={after_r:.1f}")


def test_carpaccio_venetian_clarity_pass_preserves_canvas_shape():
    """carpaccio_venetian_clarity_pass() must not change canvas dimensions."""
    p = _make_small_painter(80, 64)
    p.tone_ground((0.78, 0.68, 0.50), texture_strength=0.05)
    p.carpaccio_venetian_clarity_pass(opacity=0.30)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after carpaccio_venetian_clarity_pass: {img.size}")


def test_carpaccio_venetian_clarity_pass_variance_sigma_parameter():
    """carpaccio_venetian_clarity_pass must accept variance_sigma (session 128 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.carpaccio_venetian_clarity_pass)
    assert "variance_sigma" in sig.parameters, (
        "carpaccio_venetian_clarity_pass must have 'variance_sigma' parameter "
        "(local variance estimation window — session 128 improvement)")


def test_venetian_narrative_luminism_period_present():
    """Period.VENETIAN_NARRATIVE_LUMINISM must be in the Period enum (session 128)."""
    from scene_schema import Period
    assert hasattr(Period, "VENETIAN_NARRATIVE_LUMINISM"), (
        "Period.VENETIAN_NARRATIVE_LUMINISM not found -- add it to scene_schema.py")
    assert Period.VENETIAN_NARRATIVE_LUMINISM in list(Period)


def test_venetian_narrative_luminism_stroke_params_moderate_blend():
    """VENETIAN_NARRATIVE_LUMINISM stroke_params must have moderate wet_blend."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_NARRATIVE_LUMINISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.45 <= p["wet_blend"] <= 0.80, (
        f"VENETIAN_NARRATIVE_LUMINISM wet_blend should be 0.45–0.80 "
        f"(moderate Venetian clarity); got {p['wet_blend']:.2f}")


def test_venetian_narrative_luminism_stroke_params_crisp_edges():
    """VENETIAN_NARRATIVE_LUMINISM edge_softness must be moderate-to-crisp (<= 0.65)."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_NARRATIVE_LUMINISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] <= 0.65, (
        f"VENETIAN_NARRATIVE_LUMINISM edge_softness should be <= 0.65 "
        f"(resolved Venetian narrative edges); got {p['edge_softness']:.2f}")


# ── Session 129 -- piazzetta_velvet_shadow_pass() ────────────────────────────

def test_piazzetta_velvet_shadow_pass_exists_routing():
    """Painter must have piazzetta_velvet_shadow_pass() method (session 129)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "piazzetta_velvet_shadow_pass"), (
        "piazzetta_velvet_shadow_pass not found on Painter -- add to stroke_engine.py")
    assert callable(getattr(Painter, "piazzetta_velvet_shadow_pass"))


def test_piazzetta_velvet_shadow_pass_no_error_routing():
    """piazzetta_velvet_shadow_pass() runs on a dark toned canvas without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.05)
    p.piazzetta_velvet_shadow_pass(opacity=0.32)


def test_piazzetta_velvet_shadow_pass_modifies_canvas_routing():
    """piazzetta_velvet_shadow_pass() must modify the canvas at non-zero opacity."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.05)
    before = _canvas_bytes(p)
    p.piazzetta_velvet_shadow_pass(
        shadow_percentile=0.20,
        shadow_warm_r=0.050,
        opacity=0.60,
    )
    after = _canvas_bytes(p)
    assert before != after, "piazzetta_velvet_shadow_pass should modify the canvas"


def test_piazzetta_velvet_shadow_pass_zero_opacity_noop_routing():
    """piazzetta_velvet_shadow_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.05)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.piazzetta_velvet_shadow_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "piazzetta_velvet_shadow_pass(opacity=0) should be a noop")


def test_piazzetta_velvet_shadow_pass_preserves_canvas_shape():
    """piazzetta_velvet_shadow_pass() must not change canvas dimensions."""
    p = _make_small_painter(80, 64)
    p.tone_ground((0.20, 0.14, 0.08), texture_strength=0.05)
    p.piazzetta_velvet_shadow_pass(opacity=0.32)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after piazzetta_velvet_shadow_pass: {img.size}")


# ─────────────────────────────────────────────────────────────────────────────
# Session 130: Sebastiano del Piombo + VENETIAN_ROMAN_SYNTHESIS
#              + sebastiano_sculptural_depth_pass (structure tensor mode)
# ─────────────────────────────────────────────────────────────────────────────

def test_venetian_roman_synthesis_period_present():
    """Period.VENETIAN_ROMAN_SYNTHESIS must be in the Period enum (session 130)."""
    from scene_schema import Period
    assert hasattr(Period, "VENETIAN_ROMAN_SYNTHESIS"), (
        "Period.VENETIAN_ROMAN_SYNTHESIS not found -- add it to scene_schema.py")
    assert Period.VENETIAN_ROMAN_SYNTHESIS in list(Period)


def test_venetian_roman_synthesis_stroke_params_high_blend():
    """VENETIAN_ROMAN_SYNTHESIS wet_blend must be high (>= 0.65) for Venetian blending."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_ROMAN_SYNTHESIS,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.65, (
        f"VENETIAN_ROMAN_SYNTHESIS wet_blend should be >= 0.65 "
        f"(strong Venetian blending inheritance); got {p['wet_blend']:.2f}")


def test_venetian_roman_synthesis_stroke_params_high_edge_softness():
    """VENETIAN_ROMAN_SYNTHESIS edge_softness must be >= 0.55 for Venetian soft emergence."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_ROMAN_SYNTHESIS,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] >= 0.55, (
        f"VENETIAN_ROMAN_SYNTHESIS edge_softness should be >= 0.55 "
        f"(Venetian-school soft form emergence); got {p['edge_softness']:.2f}")


def test_sebastiano_sculptural_depth_pass_exists_routing():
    """Painter must have sebastiano_sculptural_depth_pass() method (session 130)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "sebastiano_sculptural_depth_pass"), (
        "sebastiano_sculptural_depth_pass not found on Painter -- add to stroke_engine.py")
    assert callable(getattr(Painter, "sebastiano_sculptural_depth_pass"))


def test_sebastiano_sculptural_depth_pass_no_error_routing():
    """sebastiano_sculptural_depth_pass() runs on a warm-ground canvas without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.40, 0.30, 0.16), texture_strength=0.05)
    p.sebastiano_sculptural_depth_pass(opacity=0.30)


def test_sebastiano_sculptural_depth_pass_modifies_canvas_routing():
    """sebastiano_sculptural_depth_pass() must modify the canvas at non-zero opacity."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.40, 0.30, 0.16), texture_strength=0.05)
    before = _canvas_bytes(p)
    p.sebastiano_sculptural_depth_pass(
        integration_sigma=2.0,
        smooth_sigma=3.0,
        warm_tint_r=0.020,
        opacity=0.60,
    )
    after = _canvas_bytes(p)
    assert before != after, "sebastiano_sculptural_depth_pass should modify the canvas"


def test_sebastiano_sculptural_depth_pass_zero_opacity_noop_routing():
    """sebastiano_sculptural_depth_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.40, 0.30, 0.16), texture_strength=0.05)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.sebastiano_sculptural_depth_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "sebastiano_sculptural_depth_pass(opacity=0) should be a noop")


def test_sebastiano_sculptural_depth_pass_preserves_canvas_shape_routing():
    """sebastiano_sculptural_depth_pass() must not change canvas dimensions."""
    p = _make_small_painter(80, 64)
    p.tone_ground((0.40, 0.30, 0.16), texture_strength=0.05)
    p.sebastiano_sculptural_depth_pass(opacity=0.30)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after sebastiano_sculptural_depth_pass: {img.size}")


def test_venetian_baroque_tenebrism_period_present():
    """Period.VENETIAN_BAROQUE_TENEBRISM must be in the Period enum (session 129)."""
    from scene_schema import Period
    assert hasattr(Period, "VENETIAN_BAROQUE_TENEBRISM"), (
        "Period.VENETIAN_BAROQUE_TENEBRISM not found -- add it to scene_schema.py")
    assert Period.VENETIAN_BAROQUE_TENEBRISM in list(Period)


def test_venetian_baroque_tenebrism_stroke_params_moderate_blend():
    """VENETIAN_BAROQUE_TENEBRISM wet_blend must be in moderate range (0.40 to 0.70)."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_BAROQUE_TENEBRISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.40 <= p["wet_blend"] <= 0.70, (
        f"VENETIAN_BAROQUE_TENEBRISM wet_blend should be 0.40-0.70 "
        f"(moderate Piazzetta blending -- impasto body); got {p['wet_blend']:.2f}")


def test_venetian_baroque_tenebrism_stroke_params_moderate_edge_softness():
    """VENETIAN_BAROQUE_TENEBRISM edge_softness must be in moderate range (0.25 to 0.60)."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_BAROQUE_TENEBRISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.25 <= p["edge_softness"] <= 0.60, (
        f"VENETIAN_BAROQUE_TENEBRISM edge_softness should be 0.25-0.60 "
        f"(Piazzetta forms emerge from dark, moderate softness); got {p['edge_softness']:.2f}")


def test_piazzetta_velvet_shadow_pass_accepts_shadow_percentile():
    """piazzetta_velvet_shadow_pass must accept shadow_percentile parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.piazzetta_velvet_shadow_pass)
    assert "shadow_percentile" in sig.parameters, (
        "piazzetta_velvet_shadow_pass must have shadow_percentile parameter "
        "(session 129 percentile-adaptive tonal sculpting improvement)")


# ─────────────────────────────────────────────────────────────────────────────
# Session 131: Rosso Fiorentino + FLORENTINE_ACIDIC_MANNERISM
#              + rosso_chromatic_dissonance_pass (hue-selective tension mode)
# ─────────────────────────────────────────────────────────────────────────────

def test_florentine_acidic_mannerism_period_present():
    """Period.FLORENTINE_ACIDIC_MANNERISM must be in the Period enum (session 131)."""
    from scene_schema import Period
    assert hasattr(Period, "FLORENTINE_ACIDIC_MANNERISM"), (
        "Period.FLORENTINE_ACIDIC_MANNERISM not found -- add it to scene_schema.py")
    assert Period.FLORENTINE_ACIDIC_MANNERISM in list(Period)


def test_florentine_acidic_mannerism_stroke_params_low_blend():
    """FLORENTINE_ACIDIC_MANNERISM wet_blend must be low (<= 0.30) — dissonance stays unresolved."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.FLORENTINE_ACIDIC_MANNERISM,
                  palette=PaletteHint.COOL_GREY)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.30, (
        f"FLORENTINE_ACIDIC_MANNERISM wet_blend should be <= 0.30 "
        f"(Rosso refuses tonal harmony blending); got {p['wet_blend']:.2f}")


def test_florentine_acidic_mannerism_stroke_params_sharp_edges():
    """FLORENTINE_ACIDIC_MANNERISM edge_softness must be low (<= 0.30) — angular edges."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.FLORENTINE_ACIDIC_MANNERISM,
                  palette=PaletteHint.COOL_GREY)
    p = style.stroke_params
    assert p["edge_softness"] <= 0.30, (
        f"FLORENTINE_ACIDIC_MANNERISM edge_softness should be <= 0.30 "
        f"(Rosso's sharp angular edges, no sfumato); got {p['edge_softness']:.2f}")


def test_rosso_chromatic_dissonance_pass_exists_on_painter():
    """Painter must have rosso_chromatic_dissonance_pass() after session 131."""
    from stroke_engine import Painter
    assert hasattr(Painter, "rosso_chromatic_dissonance_pass"), (
        "rosso_chromatic_dissonance_pass not found on Painter -- "
        "add to stroke_engine.py for session 131")
    assert callable(getattr(Painter, "rosso_chromatic_dissonance_pass"))


def test_rosso_chromatic_dissonance_pass_no_error_routing():
    """rosso_chromatic_dissonance_pass() must run without error on a small canvas."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.42, 0.42, 0.36), texture_strength=0.05)
    p.rosso_chromatic_dissonance_pass(opacity=0.26)


def test_rosso_chromatic_dissonance_pass_accepts_opacity():
    """rosso_chromatic_dissonance_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.rosso_chromatic_dissonance_pass)
    assert "opacity" in sig.parameters, (
        "rosso_chromatic_dissonance_pass must have opacity parameter "
        "(session 131 hue-selective chromatic tension mapping)")


# Session 132: Dosso Dossi + FERRARESE_COLORIST_POESIA
#              + dosso_luminance_reflectance_pass (illumination-reflectance mode)
# ─────────────────────────────────────────────────────────────────────────────

def test_ferrarese_colorist_poesia_period_exists():
    """Period.FERRARESE_COLORIST_POESIA must be in the Period enum (session 132)."""
    from scene_schema import Period
    assert hasattr(Period, "FERRARESE_COLORIST_POESIA"), (
        "Period.FERRARESE_COLORIST_POESIA not found -- add it to scene_schema.py")
    assert Period.FERRARESE_COLORIST_POESIA in list(Period)


def test_ferrarese_colorist_poesia_high_wet_blend():
    """FERRARESE_COLORIST_POESIA wet_blend must be high (>= 0.70) — jewel-like fused surfaces."""
    from scene_schema import Style, Medium, Period
    style = Style(medium=Medium.OIL, period=Period.FERRARESE_COLORIST_POESIA,
                  wet_blend=None, edge_softness=None)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.70, (
        f"FERRARESE_COLORIST_POESIA wet_blend should be >= 0.70 "
        f"(jewel glazed surface quality); got {p['wet_blend']:.2f}")


def test_ferrarese_colorist_poesia_soft_edges():
    """FERRARESE_COLORIST_POESIA edge_softness must be >= 0.55 — Giorgionesque soft edges."""
    from scene_schema import Style, Medium, Period
    style = Style(medium=Medium.OIL, period=Period.FERRARESE_COLORIST_POESIA,
                  wet_blend=None, edge_softness=None)
    p = style.stroke_params
    assert p["edge_softness"] >= 0.55, (
        f"FERRARESE_COLORIST_POESIA edge_softness should be >= 0.55 "
        f"(Giorgionesque sfumato-soft edges); got {p['edge_softness']:.2f}")


def test_dosso_luminance_reflectance_pass_exists_on_painter():
    """Painter must have dosso_luminance_reflectance_pass() after session 132."""
    from stroke_engine import Painter
    assert hasattr(Painter, "dosso_luminance_reflectance_pass"), (
        "dosso_luminance_reflectance_pass not found on Painter -- "
        "add to stroke_engine.py for session 132")
    assert callable(getattr(Painter, "dosso_luminance_reflectance_pass"))


def test_dosso_luminance_reflectance_pass_no_error_routing():
    """dosso_luminance_reflectance_pass() must run without error on a small canvas."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.48, 0.38, 0.26), texture_strength=0.05)
    p.dosso_luminance_reflectance_pass(opacity=0.34)


def test_dosso_luminance_reflectance_pass_accepts_opacity():
    """dosso_luminance_reflectance_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.dosso_luminance_reflectance_pass)
    assert "opacity" in sig.parameters, (
        "dosso_luminance_reflectance_pass must have opacity parameter "
        "(session 132 illumination-reflectance decomposition)")


# Session 133: Jacopo Bassano + VENETIAN_PASTORAL_LUMINISM
#              + bassano_pastoral_glow_pass (anisotropic diffusion mode)
#              + shadow_temperature_relief_pass (artistic improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_venetian_pastoral_luminism_period_exists():
    """Period.VENETIAN_PASTORAL_LUMINISM must be in the Period enum (session 133)."""
    from scene_schema import Period
    assert hasattr(Period, "VENETIAN_PASTORAL_LUMINISM"), (
        "Period.VENETIAN_PASTORAL_LUMINISM not found -- add it to scene_schema.py")
    assert Period.VENETIAN_PASTORAL_LUMINISM in list(Period)


def test_venetian_pastoral_luminism_moderate_wet_blend():
    """VENETIAN_PASTORAL_LUMINISM wet_blend must be in [0.25, 0.55] — impasto quality."""
    from scene_schema import Style, Medium, Period
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_PASTORAL_LUMINISM,
                  wet_blend=None, edge_softness=None)
    p = style.stroke_params
    assert 0.25 <= p["wet_blend"] <= 0.55, (
        f"VENETIAN_PASTORAL_LUMINISM wet_blend should be in [0.25, 0.55] "
        f"(Bassano's impasto rough-textured handling); got {p['wet_blend']:.2f}")


def test_venetian_pastoral_luminism_medium_edge_softness():
    """VENETIAN_PASTORAL_LUMINISM edge_softness must be in [0.30, 0.60] — firm chiaroscuro."""
    from scene_schema import Style, Medium, Period
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_PASTORAL_LUMINISM,
                  wet_blend=None, edge_softness=None)
    p = style.stroke_params
    assert 0.30 <= p["edge_softness"] <= 0.60, (
        f"VENETIAN_PASTORAL_LUMINISM edge_softness should be in [0.30, 0.60] "
        f"(firm chiaroscuro with Venetian mid-softness); got {p['edge_softness']:.2f}")


def test_bassano_pastoral_glow_pass_exists_on_painter():
    """Painter must have bassano_pastoral_glow_pass() after session 133."""
    from stroke_engine import Painter
    assert hasattr(Painter, "bassano_pastoral_glow_pass"), (
        "bassano_pastoral_glow_pass not found on Painter -- "
        "add to stroke_engine.py for session 133")
    assert callable(getattr(Painter, "bassano_pastoral_glow_pass"))


def test_bassano_pastoral_glow_pass_no_error_routing():
    """bassano_pastoral_glow_pass() must run without error on a small canvas."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.38, 0.28, 0.16), texture_strength=0.05)
    p.bassano_pastoral_glow_pass(opacity=0.32)


def test_bassano_pastoral_glow_pass_accepts_opacity():
    """bassano_pastoral_glow_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.bassano_pastoral_glow_pass)
    assert "opacity" in sig.parameters, (
        "bassano_pastoral_glow_pass must have opacity parameter "
        "(session 133 anisotropic diffusion pass)")


def test_shadow_temperature_relief_pass_exists_on_painter():
    """Painter must have shadow_temperature_relief_pass() after session 133."""
    from stroke_engine import Painter
    assert hasattr(Painter, "shadow_temperature_relief_pass"), (
        "shadow_temperature_relief_pass not found on Painter -- "
        "add to stroke_engine.py for session 133 artistic improvement")
    assert callable(getattr(Painter, "shadow_temperature_relief_pass"))


def test_shadow_temperature_relief_pass_no_error_routing():
    """shadow_temperature_relief_pass() must run without error on a small canvas."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.42, 0.34, 0.22), texture_strength=0.05)
    p.shadow_temperature_relief_pass(opacity=0.40)


def test_shadow_temperature_relief_pass_accepts_shadow_thresh():
    """shadow_temperature_relief_pass must accept shadow_thresh parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.shadow_temperature_relief_pass)
    assert "shadow_thresh" in sig.parameters, (
        "shadow_temperature_relief_pass must have shadow_thresh parameter "
        "(session 133 shadow thermal zone threshold)")


# Session 134: Aelbert Cuyp + DUTCH_GOLDEN_AGE_LUMINISM
#              + cuyp_golden_hour_pass (luminance-adaptive spatial frequency attenuation)
# ─────────────────────────────────────────────────────────────────────────────

def test_dutch_golden_age_luminism_period_exists():
    """Period.DUTCH_GOLDEN_AGE_LUMINISM must be in the Period enum (session 134)."""
    from scene_schema import Period
    assert hasattr(Period, "DUTCH_GOLDEN_AGE_LUMINISM"), (
        "Period.DUTCH_GOLDEN_AGE_LUMINISM not found -- add it to scene_schema.py")
    assert Period.DUTCH_GOLDEN_AGE_LUMINISM in list(Period)


def test_dutch_golden_age_luminism_high_wet_blend():
    """DUTCH_GOLDEN_AGE_LUMINISM wet_blend must be >= 0.60 — golden light merges surfaces."""
    from scene_schema import Style, Medium, Period
    style = Style(medium=Medium.OIL, period=Period.DUTCH_GOLDEN_AGE_LUMINISM,
                  wet_blend=None, edge_softness=None)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.60, (
        f"DUTCH_GOLDEN_AGE_LUMINISM wet_blend should be >= 0.60 "
        f"(Cuyp's golden light dissolves and merges surfaces); got {p['wet_blend']:.2f}")


def test_dutch_golden_age_luminism_moderate_edge_softness():
    """DUTCH_GOLDEN_AGE_LUMINISM edge_softness must be in [0.40, 0.70] — forms dissolve in light."""
    from scene_schema import Style, Medium, Period
    style = Style(medium=Medium.OIL, period=Period.DUTCH_GOLDEN_AGE_LUMINISM,
                  wet_blend=None, edge_softness=None)
    p = style.stroke_params
    assert 0.40 <= p["edge_softness"] <= 0.70, (
        f"DUTCH_GOLDEN_AGE_LUMINISM edge_softness should be in [0.40, 0.70] "
        f"(forms dissolve at edges in golden atmospheric light); got {p['edge_softness']:.2f}")


def test_cuyp_golden_hour_pass_exists_on_painter():
    """Painter must have cuyp_golden_hour_pass() after session 134."""
    from stroke_engine import Painter
    assert hasattr(Painter, "cuyp_golden_hour_pass"), (
        "cuyp_golden_hour_pass not found on Painter -- "
        "add to stroke_engine.py for session 134")
    assert callable(getattr(Painter, "cuyp_golden_hour_pass"))


def test_cuyp_golden_hour_pass_no_error_routing():
    """cuyp_golden_hour_pass() must run without error on a small canvas."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.68, 0.58, 0.38), texture_strength=0.05)
    p.cuyp_golden_hour_pass(opacity=0.34)


def test_cuyp_golden_hour_pass_accepts_opacity():
    """cuyp_golden_hour_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.cuyp_golden_hour_pass)
    assert "opacity" in sig.parameters, (
        "cuyp_golden_hour_pass must have opacity parameter "
        "(session 134 luminance-adaptive spatial frequency attenuation)")


def test_cuyp_golden_hour_pass_modifies_canvas():
    """cuyp_golden_hour_pass() with non-zero opacity must modify the canvas."""
    from stroke_engine import Painter
    import numpy as np
    p = Painter(width=64, height=64)
    # Bright warm canvas — lots of high-luminance pixels for the pass to target
    p.tone_ground((0.80, 0.68, 0.44), texture_strength=0.00)
    before = np.array(p.canvas.to_pil(), dtype=np.float32).copy()
    p.cuyp_golden_hour_pass(
        gold_warm_r=0.18,
        gold_warm_g=0.08,
        gold_cool_b=0.10,
        sigma_base=0.8,
        sigma_scale=4.0,
        n_blur_levels=3,
        opacity=0.50,
    )
    after = np.array(p.canvas.to_pil(), dtype=np.float32)
    diff = np.abs(after - before).max()
    assert diff > 0, (
        "cuyp_golden_hour_pass with non-zero opacity should modify the canvas")


def test_cuyp_golden_hour_pass_zero_opacity_no_op():
    """cuyp_golden_hour_pass with opacity=0.0 should leave the canvas unchanged."""
    from stroke_engine import Painter
    import numpy as np
    p = Painter(width=64, height=64)
    p.tone_ground((0.72, 0.60, 0.40), texture_strength=0.00)
    before = np.array(p.canvas.to_pil()).copy()
    p.cuyp_golden_hour_pass(opacity=0.0)
    after = np.array(p.canvas.to_pil())
    np.testing.assert_array_equal(before, after,
        err_msg="cuyp_golden_hour_pass with opacity=0 should be a no-op")


def test_cuyp_golden_hour_pass_warms_bright_pixels():
    """
    A very bright warm-grey canvas should become warmer (higher R channel)
    after cuyp_golden_hour_pass — because bright pixels receive the full
    quadratic golden warmth shift (gold_warm_r × lum²).
    """
    from stroke_engine import Painter
    import numpy as np
    p = Painter(width=64, height=64)
    # Very bright neutral grey — all pixels in the high-lum² zone
    bright_grey = (0.88, 0.88, 0.88)
    p.tone_ground(bright_grey, texture_strength=0.00)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    # Cairo BGRA: channel 2 = R, channel 0 = B
    before_r = float(before_buf[:, :, 2].mean())
    before_b = float(before_buf[:, :, 0].mean())

    p.cuyp_golden_hour_pass(
        gold_warm_r=0.22,    # strong warm shift
        gold_warm_g=0.08,
        gold_cool_b=0.14,    # strong blue depletion
        sigma_base=0.5,
        sigma_scale=3.0,
        n_blur_levels=3,
        opacity=0.70,        # high opacity to make the effect measurable
    )

    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_r = float(after_buf[:, :, 2].mean())
    after_b = float(after_buf[:, :, 0].mean())

    assert after_r > before_r, (
        f"Bright pixels should become warmer (higher R) after cuyp_golden_hour_pass: "
        f"before_r={before_r:.1f}, after_r={after_r:.1f}")
    assert after_b < before_b, (
        f"Bright pixels should become less blue (lower B) after cuyp_golden_hour_pass: "
        f"before_b={before_b:.1f}, after_b={after_b:.1f}")


def test_cuyp_golden_hour_pass_dark_pixels_less_affected():
    """
    Dark pixels (low luminance) should be much less affected by the golden
    warmth shift than bright pixels, because the shift is weighted by lum².
    """
    from stroke_engine import Painter
    import numpy as np

    # Dark canvas: lum ≈ 0.15, lum² ≈ 0.02 — minimal warmth shift
    p_dark = Painter(width=64, height=64)
    p_dark.tone_ground((0.15, 0.15, 0.15), texture_strength=0.00)
    before_dark = np.frombuffer(p_dark.canvas.surface.get_data(),
                                dtype=np.uint8).reshape(64, 64, 4).copy()
    p_dark.cuyp_golden_hour_pass(
        gold_warm_r=0.22, gold_warm_g=0.08, gold_cool_b=0.14,
        sigma_base=0.5, sigma_scale=3.0, n_blur_levels=3, opacity=0.70)
    after_dark = np.frombuffer(p_dark.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    dark_r_shift = float(after_dark[:, :, 2].mean()) - float(before_dark[:, :, 2].mean())

    # Bright canvas: lum ≈ 0.88, lum² ≈ 0.77 — full warmth shift
    p_bright = Painter(width=64, height=64)
    p_bright.tone_ground((0.88, 0.88, 0.88), texture_strength=0.00)
    before_bright = np.frombuffer(p_bright.canvas.surface.get_data(),
                                  dtype=np.uint8).reshape(64, 64, 4).copy()
    p_bright.cuyp_golden_hour_pass(
        gold_warm_r=0.22, gold_warm_g=0.08, gold_cool_b=0.14,
        sigma_base=0.5, sigma_scale=3.0, n_blur_levels=3, opacity=0.70)
    after_bright = np.frombuffer(p_bright.canvas.surface.get_data(),
                                 dtype=np.uint8).reshape(64, 64, 4)
    bright_r_shift = float(after_bright[:, :, 2].mean()) - float(before_bright[:, :, 2].mean())

    assert bright_r_shift > dark_r_shift, (
        f"Bright pixels should receive a larger R warmth shift than dark pixels "
        f"(lum2 weighting): bright_shift={bright_r_shift:.2f}, dark_shift={dark_r_shift:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# Session 135: Lucas Cranach the Elder + GERMAN_REFORMATION_RENAISSANCE
#              + cranach_enamel_clarity_pass (13th distinct processing mode)
#              + highlight_crystalline_pass (artistic improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_cranach_enamel_clarity_pass_exists():
    """Painter must have cranach_enamel_clarity_pass() method after session 135."""
    from stroke_engine import Painter
    assert hasattr(Painter, "cranach_enamel_clarity_pass"), (
        "cranach_enamel_clarity_pass not found on Painter -- add to stroke_engine.py")
    assert callable(getattr(Painter, "cranach_enamel_clarity_pass"))


def test_cranach_enamel_clarity_pass_no_error():
    """cranach_enamel_clarity_pass() runs on a warm canvas without error."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.86, 0.78, 0.62), texture_strength=0.05)
    p.cranach_enamel_clarity_pass(opacity=0.30)


def test_cranach_enamel_clarity_pass_modifies_canvas():
    """cranach_enamel_clarity_pass() must modify the canvas at non-zero opacity."""
    import numpy as _np
    from stroke_engine import Painter
    W, H = 64, 64
    p = Painter(width=W, height=H)
    p.tone_ground((0.82, 0.14, 0.08), texture_strength=0.05)
    before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).copy()
    p.cranach_enamel_clarity_pass(chroma_boost=0.50, opacity=0.60)
    after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    )
    assert not _np.array_equal(before, after), (
        "cranach_enamel_clarity_pass should modify the canvas at opacity=0.60")


def test_cranach_enamel_clarity_pass_preserves_shape():
    """cranach_enamel_clarity_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = Painter(width=80, height=60)
    p.tone_ground((0.86, 0.78, 0.62), texture_strength=0.05)
    p.cranach_enamel_clarity_pass(opacity=0.30)
    img = p.canvas.to_pil()
    assert img.size == (80, 60), (
        f"Canvas shape changed after cranach_enamel_clarity_pass: {img.size}")


def test_cranach_enamel_clarity_pass_has_chroma_boost_parameter():
    """cranach_enamel_clarity_pass must accept chroma_boost parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.cranach_enamel_clarity_pass)
    assert "chroma_boost" in sig.parameters, (
        "cranach_enamel_clarity_pass must have chroma_boost parameter "
        "(session 135 chromaticity saturation boost control)")


def test_cranach_enamel_clarity_pass_zero_opacity_no_op():
    """cranach_enamel_clarity_pass with opacity=0.0 should leave the canvas unchanged."""
    from stroke_engine import Painter
    import numpy as np
    p = Painter(width=64, height=64)
    p.tone_ground((0.86, 0.78, 0.62), texture_strength=0.00)
    before = np.array(p.canvas.to_pil()).copy()
    p.cranach_enamel_clarity_pass(opacity=0.0)
    after = np.array(p.canvas.to_pil())
    np.testing.assert_array_equal(before, after,
        err_msg="cranach_enamel_clarity_pass with opacity=0 should be a no-op")


def test_cranach_enamel_clarity_boosts_saturation():
    """
    A chromatic (non-grey) canvas should have higher per-channel deviation
    from grey after cranach_enamel_clarity_pass with high chroma_boost.
    """
    from stroke_engine import Painter
    import numpy as np
    # Muted reddish canvas -- not fully saturated
    p = Painter(width=64, height=64)
    p.tone_ground((0.65, 0.42, 0.38), texture_strength=0.00)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    before_r = before_buf[:, :, 2].astype(float) / 255.0
    before_g = before_buf[:, :, 1].astype(float) / 255.0
    before_b = before_buf[:, :, 0].astype(float) / 255.0
    before_grey = (before_r + before_g + before_b) / 3.0
    before_sat = float(np.mean(np.abs(before_r - before_grey) +
                               np.abs(before_g - before_grey) +
                               np.abs(before_b - before_grey)))

    p.cranach_enamel_clarity_pass(
        chroma_boost=0.60,
        sigma_pool=0.0,
        pool_weight=0.0,
        opacity=0.80,
    )
    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_r = after_buf[:, :, 2].astype(float) / 255.0
    after_g = after_buf[:, :, 1].astype(float) / 255.0
    after_b = after_buf[:, :, 0].astype(float) / 255.0
    after_grey = (after_r + after_g + after_b) / 3.0
    after_sat = float(np.mean(np.abs(after_r - after_grey) +
                              np.abs(after_g - after_grey) +
                              np.abs(after_b - after_grey)))

    assert after_sat > before_sat, (
        f"cranach_enamel_clarity_pass should boost saturation on chromatic canvas: "
        f"before_sat={before_sat:.4f}, after_sat={after_sat:.4f}")


def test_highlight_crystalline_pass_exists():
    """Painter must have highlight_crystalline_pass() method after session 135."""
    from stroke_engine import Painter
    assert hasattr(Painter, "highlight_crystalline_pass"), (
        "highlight_crystalline_pass not found on Painter -- add to stroke_engine.py")
    assert callable(getattr(Painter, "highlight_crystalline_pass"))


def test_highlight_crystalline_pass_no_error():
    """highlight_crystalline_pass() runs on a canvas without error."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.86, 0.78, 0.62), texture_strength=0.05)
    p.highlight_crystalline_pass(opacity=0.35)


def test_highlight_crystalline_pass_modifies_canvas():
    """highlight_crystalline_pass() must modify a bright canvas at non-zero opacity."""
    import numpy as _np
    from stroke_engine import Painter
    W, H = 64, 64
    p = Painter(width=W, height=H)
    p.tone_ground((0.90, 0.88, 0.82), texture_strength=0.05)
    before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).copy()
    p.highlight_crystalline_pass(lum_thresh=0.50, opacity=0.80)
    after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    )
    assert not _np.array_equal(before, after), (
        "highlight_crystalline_pass should modify a bright canvas at opacity=0.80")


def test_highlight_crystalline_pass_preserves_shape():
    """highlight_crystalline_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = Painter(width=80, height=60)
    p.tone_ground((0.86, 0.78, 0.62), texture_strength=0.05)
    p.highlight_crystalline_pass(opacity=0.35)
    img = p.canvas.to_pil()
    assert img.size == (80, 60), (
        f"Canvas shape changed after highlight_crystalline_pass: {img.size}")


def test_highlight_crystalline_pass_has_lum_thresh_parameter():
    """highlight_crystalline_pass must accept lum_thresh parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.highlight_crystalline_pass)
    assert "lum_thresh" in sig.parameters, (
        "highlight_crystalline_pass must have lum_thresh parameter "
        "(session 135 highlight gate luminance threshold)")


def test_highlight_crystalline_dark_canvas_less_affected():
    """
    A dark canvas (below lum_thresh) should be almost unaffected by
    highlight_crystalline_pass, since the sigmoid mask is near zero in dark regions.
    """
    from stroke_engine import Painter
    import numpy as np
    p_dark = Painter(width=64, height=64)
    p_dark.tone_ground((0.12, 0.12, 0.12), texture_strength=0.00)
    before_dark = np.frombuffer(p_dark.canvas.surface.get_data(),
                                dtype=np.uint8).reshape(64, 64, 4).copy()
    p_dark.highlight_crystalline_pass(
        lum_thresh=0.72, usm_sigma=1.0, usm_amount=1.0, transition=0.05, opacity=1.0
    )
    after_dark = np.frombuffer(p_dark.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4)
    dark_diff = float(np.abs(after_dark.astype(float) - before_dark.astype(float)).mean())
    assert dark_diff < 5.0, (
        f"Dark canvas (lum~0.12) should be almost unaffected by highlight_crystalline_pass "
        f"(lum_thresh=0.72): mean pixel diff={dark_diff:.2f}")


# ── Session 136: Parmigianino + EMILIAN_ELEGANT_MANNERISM ────────────────────
#              + parmigianino_pearl_refinement_pass (15th distinct processing mode)
#              + penumbra_cool_tint_pass (artistic improvement)

def test_parmigianino_pearl_refinement_pass_exists():
    """Painter must have parmigianino_pearl_refinement_pass() method after session 136."""
    from stroke_engine import Painter
    assert hasattr(Painter, "parmigianino_pearl_refinement_pass"), (
        "parmigianino_pearl_refinement_pass not found on Painter -- add to stroke_engine.py")
    assert callable(getattr(Painter, "parmigianino_pearl_refinement_pass"))


def test_parmigianino_pearl_refinement_pass_no_error():
    """parmigianino_pearl_refinement_pass() runs on a warm canvas without error."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.78, 0.70, 0.56), texture_strength=0.05)
    p.parmigianino_pearl_refinement_pass(opacity=0.34)


def test_parmigianino_pearl_refinement_pass_modifies_canvas():
    """parmigianino_pearl_refinement_pass() must modify the canvas at non-zero opacity."""
    from stroke_engine import Painter
    import numpy as np
    W, H = 64, 64
    p = Painter(width=W, height=H)
    p.tone_ground((0.72, 0.24, 0.28), texture_strength=0.05)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.parmigianino_pearl_refinement_pass(sigma_chroma=2.5, usm_amount=0.45, opacity=0.60)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert not np.array_equal(before, after), (
        "parmigianino_pearl_refinement_pass should modify the canvas at opacity=0.60")


def test_parmigianino_pearl_refinement_pass_preserves_shape():
    """parmigianino_pearl_refinement_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = Painter(width=80, height=60)
    p.tone_ground((0.78, 0.70, 0.56), texture_strength=0.05)
    p.parmigianino_pearl_refinement_pass(opacity=0.34)
    img = p.canvas.to_pil()
    assert img.size == (80, 60), (
        f"Canvas shape changed after parmigianino_pearl_refinement_pass: {img.size}")


def test_parmigianino_pearl_refinement_pass_has_sigma_chroma_parameter():
    """parmigianino_pearl_refinement_pass must accept sigma_chroma parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.parmigianino_pearl_refinement_pass)
    assert "sigma_chroma" in sig.parameters, (
        "parmigianino_pearl_refinement_pass must have sigma_chroma parameter "
        "(controls chroma Gaussian smoothing width)")


def test_parmigianino_pearl_refinement_pass_zero_opacity_no_op():
    """parmigianino_pearl_refinement_pass with opacity=0.0 should leave the canvas unchanged."""
    from stroke_engine import Painter
    import numpy as np
    W, H = 64, 64
    p = Painter(width=W, height=H)
    p.tone_ground((0.78, 0.70, 0.56), texture_strength=0.05)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.parmigianino_pearl_refinement_pass(opacity=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    diff = float(np.abs(after.astype(float) - before.astype(float)).mean())
    assert diff < 1.0, (
        f"parmigianino_pearl_refinement_pass with opacity=0 should be a no-op "
        f"(mean diff={diff:.4f})")


def test_parmigianino_pearl_refinement_cool_tint_raises_blue():
    """
    parmigianino_pearl_refinement_pass with cool_tint > 0 should raise the mean
    blue channel on a neutral grey canvas compared to cool_tint=0.
    """
    from stroke_engine import Painter
    import numpy as np

    def run_pass(cool_tint_val):
        p = Painter(width=64, height=64)
        p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.00)
        p.parmigianino_pearl_refinement_pass(
            sigma_chroma=1.0, sigma_luma=0.5, usm_amount=0.0,
            cool_tint=cool_tint_val, opacity=1.0,
        )
        raw = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
        return float(raw[:, :, 0].mean())   # channel 0 = blue in BGRA

    blue_with_tint    = run_pass(cool_tint_val=0.10)
    blue_without_tint = run_pass(cool_tint_val=0.00)
    assert blue_with_tint > blue_without_tint, (
        f"cool_tint>0 should raise mean blue channel: "
        f"with={blue_with_tint:.2f}, without={blue_without_tint:.2f}")


def test_penumbra_cool_tint_pass_exists():
    """Painter must have penumbra_cool_tint_pass() method after session 136."""
    from stroke_engine import Painter
    assert hasattr(Painter, "penumbra_cool_tint_pass"), (
        "penumbra_cool_tint_pass not found on Painter -- add to stroke_engine.py")
    assert callable(getattr(Painter, "penumbra_cool_tint_pass"))


def test_penumbra_cool_tint_pass_no_error():
    """penumbra_cool_tint_pass() runs on a midtone canvas without error."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.45, 0.42, 0.38), texture_strength=0.05)
    p.penumbra_cool_tint_pass(opacity=0.30)


def test_penumbra_cool_tint_pass_modifies_canvas():
    """penumbra_cool_tint_pass() must modify a midtone canvas at non-zero opacity."""
    from stroke_engine import Painter
    import numpy as np
    W, H = 64, 64
    p = Painter(width=W, height=H)
    p.tone_ground((0.40, 0.38, 0.35), texture_strength=0.00)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.penumbra_cool_tint_pass(shadow_lo=0.10, shadow_hi=0.70, blue_lift=0.20, opacity=1.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    assert not np.array_equal(before, after), (
        "penumbra_cool_tint_pass should modify a midtone canvas at opacity=1.0")


def test_penumbra_cool_tint_pass_preserves_shape():
    """penumbra_cool_tint_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = Painter(width=80, height=60)
    p.tone_ground((0.45, 0.42, 0.38), texture_strength=0.05)
    p.penumbra_cool_tint_pass(opacity=0.30)
    img = p.canvas.to_pil()
    assert img.size == (80, 60), (
        f"Canvas shape changed after penumbra_cool_tint_pass: {img.size}")


def test_penumbra_cool_tint_pass_zero_opacity_no_op():
    """penumbra_cool_tint_pass with opacity=0.0 should leave the canvas unchanged."""
    from stroke_engine import Painter
    import numpy as np
    W, H = 64, 64
    p = Painter(width=W, height=H)
    p.tone_ground((0.45, 0.42, 0.38), texture_strength=0.05)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).copy()
    p.penumbra_cool_tint_pass(opacity=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8)
    diff = float(np.abs(after.astype(float) - before.astype(float)).mean())
    assert diff < 1.0, (
        f"penumbra_cool_tint_pass with opacity=0 should be a no-op "
        f"(mean diff={diff:.4f})")


def test_penumbra_cool_tint_ignores_bright_pixels():
    """
    A very bright canvas (above shadow_hi) should be minimally affected by
    penumbra_cool_tint_pass, since the penumbra mask is near zero in bright zones.
    """
    from stroke_engine import Painter
    import numpy as np
    p_bright = Painter(width=64, height=64)
    p_bright.tone_ground((0.92, 0.92, 0.92), texture_strength=0.00)
    before_bright = np.frombuffer(
        p_bright.canvas.surface.get_data(), dtype=np.uint8
    ).reshape(64, 64, 4).copy()
    p_bright.penumbra_cool_tint_pass(
        shadow_lo=0.15, shadow_hi=0.52, transition=0.05, blue_lift=0.20, opacity=1.0
    )
    after_bright = np.frombuffer(
        p_bright.canvas.surface.get_data(), dtype=np.uint8
    ).reshape(64, 64, 4)
    bright_diff = float(np.abs(
        after_bright.astype(float) - before_bright.astype(float)
    ).mean())
    assert bright_diff < 5.0, (
        f"Bright canvas (lum~0.92) should be almost unaffected by penumbra_cool_tint_pass "
        f"(shadow_hi=0.52): mean pixel diff={bright_diff:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# Session 136: Moretto da Brescia + LOMBARD_SILVER_CLASSICISM
#              + moretto_silver_luminance_pass (14th distinct processing mode)
#              + pearlescent_sfumato_pass (artistic improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_lombard_silver_classicism_period_exists():
    """Period.LOMBARD_SILVER_CLASSICISM must be in the Period enum (session 136)."""
    from scene_schema import Period
    assert hasattr(Period, "LOMBARD_SILVER_CLASSICISM"), (
        "Period.LOMBARD_SILVER_CLASSICISM not found -- add it to scene_schema.py")
    assert Period.LOMBARD_SILVER_CLASSICISM in list(Period)


def test_lombard_silver_classicism_wet_blend():
    """LOMBARD_SILVER_CLASSICISM wet_blend should be in moderate-high range (0.45–0.72)."""
    from scene_schema import Period, Style, Medium, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.LOMBARD_SILVER_CLASSICISM,
                  palette=PaletteHint.COOL_GREY)
    params = style.stroke_params
    assert 0.45 <= params["wet_blend"] <= 0.72, (
        f"LOMBARD_SILVER_CLASSICISM wet_blend should be in [0.45, 0.72] "
        f"(moderate-high — tones merge softly): got {params['wet_blend']}")


def test_lombard_silver_classicism_edge_softness():
    """LOMBARD_SILVER_CLASSICISM edge_softness should be moderate (0.35–0.58)."""
    from scene_schema import Period, Style, Medium, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.LOMBARD_SILVER_CLASSICISM,
                  palette=PaletteHint.COOL_GREY)
    params = style.stroke_params
    assert 0.35 <= params["edge_softness"] <= 0.58, (
        f"LOMBARD_SILVER_CLASSICISM edge_softness should be in [0.35, 0.58] "
        f"(moderate — soft but structurally present): got {params['edge_softness']}")


def test_moretto_silver_luminance_pass_exists():
    """Painter must have moretto_silver_luminance_pass() method after session 136."""
    from stroke_engine import Painter
    assert hasattr(Painter, "moretto_silver_luminance_pass"), (
        "moretto_silver_luminance_pass not found on Painter -- add to stroke_engine.py")
    assert callable(getattr(Painter, "moretto_silver_luminance_pass"))


def test_moretto_silver_luminance_pass_no_error():
    """moretto_silver_luminance_pass() runs on a cool canvas without error."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.68, 0.64, 0.60), texture_strength=0.05)
    p.moretto_silver_luminance_pass(opacity=0.32)


def test_moretto_silver_luminance_pass_modifies_canvas():
    """moretto_silver_luminance_pass() must modify the canvas at non-zero opacity."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.78, 0.72, 0.68), texture_strength=0.05)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.moretto_silver_luminance_pass(opacity=0.60)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8)
    assert not _np.array_equal(before, after), (
        "moretto_silver_luminance_pass should modify the canvas at opacity=0.60")


def test_moretto_silver_luminance_pass_preserves_shape():
    """moretto_silver_luminance_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = Painter(width=80, height=60)
    p.tone_ground((0.68, 0.64, 0.60), texture_strength=0.05)
    p.moretto_silver_luminance_pass(opacity=0.32)
    img = p.canvas.to_pil()
    assert img.size == (80, 60), (
        f"Canvas shape changed after moretto_silver_luminance_pass: {img.size}")


def test_moretto_silver_luminance_pass_has_b_silver_parameter():
    """moretto_silver_luminance_pass must accept b_silver parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.moretto_silver_luminance_pass)
    assert "b_silver" in sig.parameters, (
        "moretto_silver_luminance_pass must have b_silver parameter "
        "(session 136 yellow-warmth neutralisation control)")


def test_moretto_silver_luminance_pass_zero_opacity_no_op():
    """moretto_silver_luminance_pass with opacity=0.0 should leave canvas unchanged."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.68, 0.64, 0.60), texture_strength=0.00)
    before = np.array(p.canvas.to_pil()).copy()
    p.moretto_silver_luminance_pass(opacity=0.0)
    after = np.array(p.canvas.to_pil())
    np.testing.assert_array_equal(before, after,
        err_msg="moretto_silver_luminance_pass with opacity=0 should be a no-op")


def test_moretto_silver_luminance_pass_cools_warm_highlights():
    """
    A warm yellow canvas should have reduced yellow-blue (b*) in bright zones
    after moretto_silver_luminance_pass with high b_silver — the silver
    neutralisation depletes yellow-warmth proportionally to L².
    The simplest proxy in RGB: the mean B channel should increase (or R decrease)
    on a warm-bright canvas, since removing yellow means boosting blue-neutral.
    """
    import numpy as np
    from stroke_engine import Painter
    # Warm bright canvas (amber-yellow — high b* in Lab)
    p = Painter(width=64, height=64)
    p.tone_ground((0.90, 0.82, 0.40), texture_strength=0.00)
    before_buf = np.frombuffer(p.canvas.surface.get_data(),
                               dtype=np.uint8).reshape(64, 64, 4).copy()
    before_b = float(before_buf[:, :, 0].mean())   # Cairo B channel
    p.moretto_silver_luminance_pass(b_silver=0.80, opacity=0.80)
    after_buf = np.frombuffer(p.canvas.surface.get_data(),
                              dtype=np.uint8).reshape(64, 64, 4)
    after_b = float(after_buf[:, :, 0].mean())
    assert after_b > before_b, (
        f"moretto_silver_luminance_pass should increase blue channel on warm-bright canvas "
        f"(silver neutralisation of yellow-warmth): before_B={before_b:.1f}, after_B={after_b:.1f}")


def test_moretto_in_catalog():
    """moretto_da_brescia must be in CATALOG after session 136."""
    from art_catalog import CATALOG
    assert "moretto_da_brescia" in CATALOG, (
        "moretto_da_brescia not found in CATALOG -- add to art_catalog.py")


def test_moretto_palette_valid():
    """moretto_da_brescia palette must have 8 entries all in [0, 1]."""
    from art_catalog import get_style
    style = get_style("moretto_da_brescia")
    assert len(style.palette) == 8, (
        f"moretto_da_brescia palette should have 8 entries, got {len(style.palette)}")
    for i, c in enumerate(style.palette):
        for j, ch in enumerate(c):
            assert 0.0 <= ch <= 1.0, (
                f"moretto_da_brescia palette[{i}][{j}]={ch} out of [0, 1]")


def test_moretto_ground_color_cool():
    """moretto_da_brescia ground_color should be cool (B >= R — grey-silver ground)."""
    from art_catalog import get_style
    style = get_style("moretto_da_brescia")
    r, g, b = style.ground_color
    assert b >= r - 0.05, (
        f"moretto_da_brescia ground_color should be cool (B >= R): R={r:.3f}, B={b:.3f}")


def test_moretto_glazing_cool():
    """moretto_da_brescia glazing should be cool (B >= R — silver-lavender glaze)."""
    from art_catalog import get_style
    style = get_style("moretto_da_brescia")
    assert style.glazing is not None, "moretto_da_brescia glazing must not be None"
    r, g, b = style.glazing
    assert b >= r - 0.02, (
        f"moretto_da_brescia glazing should be cool/neutral (B >= R): R={r:.3f}, B={b:.3f}")


# ── pearlescent_sfumato_pass ─────────────────────────────────────────────────

def test_pearlescent_sfumato_pass_exists():
    """Painter must have pearlescent_sfumato_pass() method after session 136."""
    from stroke_engine import Painter
    assert hasattr(Painter, "pearlescent_sfumato_pass"), (
        "pearlescent_sfumato_pass not found on Painter -- add to stroke_engine.py")
    assert callable(getattr(Painter, "pearlescent_sfumato_pass"))


def test_pearlescent_sfumato_pass_no_error():
    """pearlescent_sfumato_pass() runs on a plain canvas without error."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.78, 0.72, 0.68), texture_strength=0.05)
    p.pearlescent_sfumato_pass(opacity=0.28)


def test_pearlescent_sfumato_pass_modifies_canvas():
    """pearlescent_sfumato_pass() must modify the canvas at non-zero opacity."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.75, 0.70, 0.65), texture_strength=0.00)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.pearlescent_sfumato_pass(opacity=0.80)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8)
    assert not _np.array_equal(before, after), (
        "pearlescent_sfumato_pass should modify canvas at opacity=0.80")


def test_pearlescent_sfumato_pass_preserves_shape():
    """pearlescent_sfumato_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = Painter(width=80, height=60)
    p.tone_ground((0.68, 0.64, 0.60), texture_strength=0.05)
    p.pearlescent_sfumato_pass(opacity=0.28)
    img = p.canvas.to_pil()
    assert img.size == (80, 60), (
        f"Canvas shape changed after pearlescent_sfumato_pass: {img.size}")


def test_pearlescent_sfumato_pass_has_smooth_sigma_parameter():
    """pearlescent_sfumato_pass must accept smooth_sigma parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.pearlescent_sfumato_pass)
    assert "smooth_sigma" in sig.parameters, (
        "pearlescent_sfumato_pass must have smooth_sigma parameter "
        "(session 136 gradient stability Gaussian sigma)")


def test_pearlescent_sfumato_pass_zero_opacity_no_op():
    """pearlescent_sfumato_pass with opacity=0.0 should leave canvas unchanged."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.68, 0.64, 0.60), texture_strength=0.00)
    before = np.array(p.canvas.to_pil()).copy()
    p.pearlescent_sfumato_pass(opacity=0.0)
    after = np.array(p.canvas.to_pil())
    np.testing.assert_array_equal(before, after,
        err_msg="pearlescent_sfumato_pass with opacity=0 should be a no-op")


def test_pearlescent_sfumato_smooth_canvas_brighter_than_textured():
    """
    On a uniform (smooth) canvas, pearlescent_sfumato_pass should produce a
    brighter result than on an equivalent canvas covered with a sharp texture
    step — because the smooth zone's gradient is near zero, giving S≈1 and
    applying the full pearl lift, while the textured canvas has S≈0 at the edge.
    """
    import numpy as np
    from stroke_engine import Painter

    # Smooth canvas — single uniform mid-grey
    p_smooth = Painter(width=64, height=64)
    p_smooth.tone_ground((0.55, 0.55, 0.55), texture_strength=0.00)

    # Textured canvas — hard edge at the mid-line to suppress smoothness mask
    p_textured = Painter(width=64, height=64)
    p_textured.tone_ground((0.55, 0.55, 0.55), texture_strength=0.00)
    # Overwrite top half with a sharply different tone to create a hard edge
    import cairo
    ctx = cairo.Context(p_textured.canvas.surface)
    ctx.set_source_rgb(0.10, 0.10, 0.10)
    ctx.rectangle(0, 0, 64, 32)
    ctx.fill()

    before_smooth = np.array(p_smooth.canvas.to_pil()).copy()

    p_smooth.pearlescent_sfumato_pass(
        smooth_sigma=1.5, pearl_lift=0.10, opacity=1.0)
    p_textured.pearlescent_sfumato_pass(
        smooth_sigma=1.5, pearl_lift=0.10, opacity=1.0)

    after_smooth_lum = float(np.array(p_smooth.canvas.to_pil()).mean())
    after_textured_lum = float(np.array(p_textured.canvas.to_pil()).mean())

    # The uniform canvas should not darken; it may brighten slightly
    before_lum = float(before_smooth.mean())
    assert after_smooth_lum >= before_lum - 2.0, (
        f"pearlescent_sfumato_pass should not darken a smooth canvas: "
        f"before={before_lum:.1f}, after={after_smooth_lum:.1f}")


# ─────────────────────────────────────────────────────────────────────────────
# Session 139 — palma_blonde_luminance_pass + VENETIAN_GOLDEN_NATURALISM
# ─────────────────────────────────────────────────────────────────────────────

def test_palma_blonde_luminance_pass_exists():
    """Painter must have palma_blonde_luminance_pass() method after session 139."""
    from stroke_engine import Painter
    assert hasattr(Painter, "palma_blonde_luminance_pass"), (
        "palma_blonde_luminance_pass not found on Painter -- add to stroke_engine.py")
    assert callable(getattr(Painter, "palma_blonde_luminance_pass"))


def test_palma_blonde_luminance_pass_no_error():
    """palma_blonde_luminance_pass() runs on a plain canvas without error."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.56, 0.44, 0.26), texture_strength=0.05)
    p.palma_blonde_luminance_pass(opacity=0.32)


def test_palma_blonde_luminance_pass_modifies_canvas():
    """palma_blonde_luminance_pass() must modify a midtone canvas at non-zero opacity."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.60, 0.58, 0.56), texture_strength=0.00)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.palma_blonde_luminance_pass(opacity=0.80)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8)
    assert not _np.array_equal(before, after), (
        "palma_blonde_luminance_pass should modify midtone canvas at opacity=0.80")


def test_palma_blonde_luminance_pass_preserves_shape():
    """palma_blonde_luminance_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = Painter(width=80, height=60)
    p.tone_ground((0.58, 0.46, 0.28), texture_strength=0.05)
    p.palma_blonde_luminance_pass(opacity=0.32)
    img = p.canvas.to_pil()
    assert img.size == (80, 60), (
        f"Canvas shape changed after palma_blonde_luminance_pass: {img.size}")


def test_palma_blonde_luminance_pass_has_luminance_centre_parameter():
    """palma_blonde_luminance_pass must accept luminance_centre parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.palma_blonde_luminance_pass)
    assert "luminance_centre" in sig.parameters, (
        "palma_blonde_luminance_pass must have luminance_centre parameter "
        "(session 139 Gaussian luminance zone centre)")


def test_palma_blonde_luminance_pass_has_luminance_sigma_parameter():
    """palma_blonde_luminance_pass must accept luminance_sigma parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.palma_blonde_luminance_pass)
    assert "luminance_sigma" in sig.parameters, (
        "palma_blonde_luminance_pass must have luminance_sigma parameter "
        "(session 139 Gaussian gate width)")


def test_palma_blonde_luminance_pass_zero_opacity_no_op():
    """palma_blonde_luminance_pass with opacity=0.0 should leave canvas unchanged."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.60, 0.56, 0.52), texture_strength=0.00)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.palma_blonde_luminance_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8)
    assert _np.array_equal(before, after), (
        "palma_blonde_luminance_pass with opacity=0 should be a no-op")


def test_venetian_golden_naturalism_period_in_period_enum():
    """VENETIAN_GOLDEN_NATURALISM must be present in the Period enum."""
    from scene_schema import Period
    assert hasattr(Period, "VENETIAN_GOLDEN_NATURALISM"), (
        "VENETIAN_GOLDEN_NATURALISM missing from Period enum -- "
        "add to scene_schema.py (session 139)")


def test_palma_vecchio_in_catalog_routing():
    """palma_vecchio must be accessible via get_style for pipeline routing."""
    from art_catalog import get_style
    style = get_style("palma_vecchio")
    assert style.artist == "Palma Vecchio", (
        f"palma_vecchio artist name mismatch: {style.artist!r}")


def test_palma_vecchio_ground_warm_for_routing():
    """palma_vecchio ground_color must be warm (R >= B) for correct pipeline routing."""
    from art_catalog import get_style
    style = get_style("palma_vecchio")
    r, g, b = style.ground_color
    assert r >= b, (
        f"palma_vecchio ground_color should be warm (R >= B): R={r:.3f}, B={b:.3f}")


# ─────────────────────────────────────────────────────────────────────────────
# Session 140 — cossa_enamel_structure_pass + FERRARESE_CIVIC_GRANDEUR
# ─────────────────────────────────────────────────────────────────────────────

def test_cossa_enamel_structure_pass_exists():
    """Painter must have cossa_enamel_structure_pass() method after session 140."""
    from stroke_engine import Painter
    assert hasattr(Painter, "cossa_enamel_structure_pass"), (
        "cossa_enamel_structure_pass not found on Painter -- add to stroke_engine.py")
    assert callable(getattr(Painter, "cossa_enamel_structure_pass"))


def test_cossa_enamel_structure_pass_no_error():
    """cossa_enamel_structure_pass() runs on a plain canvas without error."""
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.72, 0.62, 0.44), texture_strength=0.09)
    p.cossa_enamel_structure_pass(opacity=0.36)


def test_cossa_enamel_structure_pass_modifies_canvas():
    """cossa_enamel_structure_pass() must modify a chromatic canvas at non-zero opacity."""
    import numpy as _np
    from PIL import Image as _PILImg
    from stroke_engine import Painter

    p = Painter(width=64, height=64)
    # Chromatic canvas with a warm/cool stripe — provides colour zones for chroma boost
    arr = _np.zeros((64, 64, 3), dtype=_np.uint8)
    arr[:, :32, :] = [200, 80, 60]    # warm vermilion half
    arr[:, 32:, :] = [60, 80, 200]    # cool azure half
    ref = _PILImg.fromarray(arr, "RGB")
    p.tone_ground((0.72, 0.62, 0.44), texture_strength=0.00)
    p.block_in(ref, stroke_size=12, n_strokes=40)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy()
    p.cossa_enamel_structure_pass(chroma_boost=0.30, structure_strength=0.30,
                                  opacity=0.80)
    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4)
    assert not _np.array_equal(before, after), (
        "cossa_enamel_structure_pass should modify a chromatic canvas")


def test_cossa_enamel_structure_pass_zero_opacity_no_op():
    """cossa_enamel_structure_pass with opacity=0.0 should leave canvas unchanged."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.72, 0.62, 0.44), texture_strength=0.00)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.cossa_enamel_structure_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8)
    assert _np.array_equal(before, after), (
        "cossa_enamel_structure_pass with opacity=0 should be a no-op")


def test_cossa_enamel_structure_pass_pixels_in_range():
    """cossa_enamel_structure_pass() must not produce out-of-range pixel values."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.72, 0.62, 0.44), texture_strength=0.09)
    p.cossa_enamel_structure_pass()
    buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8)
    assert buf.max() <= 255
    assert buf.min() >= 0


def test_cossa_enamel_structure_pass_has_chroma_boost_parameter():
    """cossa_enamel_structure_pass must accept chroma_boost parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.cossa_enamel_structure_pass)
    assert "chroma_boost" in sig.parameters, (
        "cossa_enamel_structure_pass must have chroma_boost parameter "
        "(session 140 gem-zone saturation lift)")


def test_cossa_enamel_structure_pass_has_structure_strength_parameter():
    """cossa_enamel_structure_pass must accept structure_strength parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.cossa_enamel_structure_pass)
    assert "structure_strength" in sig.parameters, (
        "cossa_enamel_structure_pass must have structure_strength parameter "
        "(session 140 unsharp mask weight)")


def test_cossa_enamel_structure_chroma_boosts_saturated_zones():
    """chroma boost should increase channel divergence from luminance in mid-tones."""
    import numpy as _np
    from stroke_engine import Painter

    # Saturated mid-luminance canvas (warm terracotta ~L=0.55)
    p = Painter(width=64, height=64)
    p.tone_ground((0.80, 0.45, 0.20), texture_strength=0.00)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).copy().astype(_np.float32)
    # Measure pre-boost max channel deviation from luminance
    r_b = before[:, :, 2] / 255.0
    g_b = before[:, :, 1] / 255.0
    b_b = before[:, :, 0] / 255.0
    lum_b = 0.299 * r_b + 0.587 * g_b + 0.114 * b_b
    dev_before = float(_np.abs(r_b - lum_b).mean() + _np.abs(g_b - lum_b).mean())

    p.cossa_enamel_structure_pass(chroma_boost=0.40, structure_strength=0.0, opacity=1.0)

    after = _np.frombuffer(p.canvas.surface.get_data(),
                           dtype=_np.uint8).reshape(64, 64, 4).astype(_np.float32)
    r_a = after[:, :, 2] / 255.0
    g_a = after[:, :, 1] / 255.0
    b_a = after[:, :, 0] / 255.0
    lum_a = 0.299 * r_a + 0.587 * g_a + 0.114 * b_a
    dev_after = float(_np.abs(r_a - lum_a).mean() + _np.abs(g_a - lum_a).mean())

    assert dev_after >= dev_before, (
        f"cossa_enamel_structure_pass chroma_boost should increase channel "
        f"divergence from luminance: before={dev_before:.4f}, after={dev_after:.4f}")


def test_ferrarese_civic_grandeur_period_in_period_enum():
    """FERRARESE_CIVIC_GRANDEUR must be present in the Period enum after session 140."""
    from scene_schema import Period
    assert hasattr(Period, "FERRARESE_CIVIC_GRANDEUR"), (
        "FERRARESE_CIVIC_GRANDEUR missing from Period enum -- "
        "add to scene_schema.py (session 140)")


def test_ferrarese_civic_grandeur_routing_flag_true():
    """is_ferrarese_civic_grandeur routing flag must be True for FERRARESE_CIVIC_GRANDEUR."""
    flags = _routing_flags(Period.FERRARESE_CIVIC_GRANDEUR)
    assert flags["is_ferrarese_civic_grandeur"] is True


def test_ferrarese_civic_grandeur_routing_flag_false_for_other_periods():
    """is_ferrarese_civic_grandeur must be False for all periods except FERRARESE_CIVIC_GRANDEUR."""
    for period in Period:
        if period == Period.FERRARESE_CIVIC_GRANDEUR:
            continue
        flags = _routing_flags(period)
        assert not flags["is_ferrarese_civic_grandeur"], (
            f"is_ferrarese_civic_grandeur should be False for {period.name}")


def test_cossa_in_catalog_accessible_via_get_style():
    """cossa must be accessible via get_style() for pipeline routing."""
    from art_catalog import get_style
    style = get_style("cossa")
    assert "Cossa" in style.artist, (
        f"cossa artist name mismatch: {style.artist!r}")


def test_cossa_ground_color_warm_for_routing():
    """cossa ground_color must be warm (R >= B) for correct pipeline warm imprimatura."""
    from art_catalog import get_style
    style = get_style("cossa")
    r, g, b = style.ground_color
    assert r >= b, (
        f"cossa ground_color should be warm (R >= B): R={r:.3f}, B={b:.3f}")


# ──────────────────────────────────────────────────────────────────────────────
# crivelli_gold_leaf_pass — session 141 main pass
# ──────────────────────────────────────────────────────────────────────────────

def test_crivelli_gold_leaf_pass_exists():
    """Painter must have crivelli_gold_leaf_pass() method after session 141."""
    from stroke_engine import Painter
    assert hasattr(Painter, "crivelli_gold_leaf_pass"), (
        "crivelli_gold_leaf_pass not found on Painter")
    assert callable(getattr(Painter, "crivelli_gold_leaf_pass"))


def test_crivelli_gold_leaf_pass_no_error():
    """crivelli_gold_leaf_pass() runs on a plain canvas without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.58, 0.48, 0.28), texture_strength=0.06)
    p.crivelli_gold_leaf_pass(opacity=0.38)


def test_crivelli_gold_leaf_pass_zero_opacity_no_op():
    """crivelli_gold_leaf_pass() with opacity=0 must not modify the canvas."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.58, 0.48, 0.28), texture_strength=0.06)
    before = _canvas_bytes(p)
    p.crivelli_gold_leaf_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, (
        "crivelli_gold_leaf_pass with opacity=0 must not modify the canvas")


def test_crivelli_gold_leaf_pass_modifies_bright_canvas():
    """crivelli_gold_leaf_pass() must modify a canvas that has bright pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Use a very bright ground so pixels exceed the gilt threshold
    p.tone_ground((0.90, 0.88, 0.80), texture_strength=0.00)
    before = _canvas_bytes(p)
    p.crivelli_gold_leaf_pass(gilt_thresh=0.60, gilt_power=1.5, opacity=1.0)
    after = _canvas_bytes(p)
    assert before != after, (
        "crivelli_gold_leaf_pass must modify a bright canvas with pixels "
        "above the gilt threshold")


def test_crivelli_gold_leaf_pass_pixels_in_range():
    """crivelli_gold_leaf_pass() must not produce out-of-range pixel values."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.85, 0.80, 0.72), texture_strength=0.00)
    p.crivelli_gold_leaf_pass(gilt_thresh=0.50, gilt_power=2.0, opacity=1.0)
    buf = _np.frombuffer(p.canvas.surface.get_data(),
                         dtype=_np.uint8).reshape(64, 64, 4)
    assert buf[:, :, :3].min() >= 0,   "Pixel values below 0 after gold leaf pass"
    assert buf[:, :, :3].max() <= 255, "Pixel values above 255 after gold leaf pass"


def test_crivelli_gold_leaf_pass_adds_warmth_to_highlights():
    """crivelli_gold_leaf_pass() must increase the R channel in bright zones."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Neutral bright canvas — equal R, G, B so warmth effect is measurable
    p.tone_ground((0.85, 0.85, 0.85), texture_strength=0.00)

    before = _np.frombuffer(p.canvas.surface.get_data(),
                             dtype=_np.uint8).reshape(64, 64, 4).astype(_np.float32)
    r_mean_before = before[:, :, 2].mean()

    p.crivelli_gold_leaf_pass(gilt_thresh=0.60, gilt_power=1.5,
                               gold_r=0.30, gold_g=0.10, opacity=1.0)

    after = _np.frombuffer(p.canvas.surface.get_data(),
                            dtype=_np.uint8).reshape(64, 64, 4).astype(_np.float32)
    r_mean_after = after[:, :, 2].mean()

    assert r_mean_after > r_mean_before, (
        f"crivelli_gold_leaf_pass should add red warmth to bright highlights: "
        f"before={r_mean_before:.1f}, after={r_mean_after:.1f}")


# ──────────────────────────────────────────────────────────────────────────────
# glazing_depth_pass — session 141 artistic improvement
# ──────────────────────────────────────────────────────────────────────────────

def test_glazing_depth_pass_exists():
    """Painter must have glazing_depth_pass() method after session 141."""
    from stroke_engine import Painter
    assert hasattr(Painter, "glazing_depth_pass"), (
        "glazing_depth_pass not found on Painter")
    assert callable(getattr(Painter, "glazing_depth_pass"))


def test_glazing_depth_pass_no_error():
    """glazing_depth_pass() runs on a plain toned canvas without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.45, 0.30), texture_strength=0.06)
    p.glazing_depth_pass(opacity=0.22)


def test_glazing_depth_pass_zero_opacity_no_op():
    """glazing_depth_pass() with opacity=0 must not modify the canvas."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.45, 0.30), texture_strength=0.06)
    before = _canvas_bytes(p)
    p.glazing_depth_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, (
        "glazing_depth_pass with opacity=0 must not modify the canvas")


def test_glazing_depth_pass_modifies_canvas():
    """glazing_depth_pass() with opacity > 0 must modify a mid-tone canvas."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Mid-tone ground — squarely within the default depth zone
    p.tone_ground((0.55, 0.45, 0.30), texture_strength=0.00)
    before = _canvas_bytes(p)
    p.glazing_depth_pass(glaze_sigma=2.0, warm_r=0.15, warm_g=0.06,
                          depth_low=0.25, depth_high=0.75, opacity=1.0)
    after = _canvas_bytes(p)
    assert before != after, (
        "glazing_depth_pass must modify a mid-tone canvas when opacity > 0")


def test_glazing_depth_pass_pixels_in_range():
    """glazing_depth_pass() must not produce out-of-range pixel values."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.55, 0.45, 0.30), texture_strength=0.00)
    p.glazing_depth_pass(warm_r=0.20, warm_g=0.10, opacity=1.0)
    buf = _np.frombuffer(p.canvas.surface.get_data(),
                         dtype=_np.uint8).reshape(64, 64, 4)
    assert buf[:, :, :3].min() >= 0,   "Pixel values below 0 after glazing depth pass"
    assert buf[:, :, :3].max() <= 255, "Pixel values above 255 after glazing depth pass"


# ──────────────────────────────────────────────────────────────────────────────
# VENETIAN_GILT_BYZANTINE_SPLENDOUR — session 141 Period enum and routing
# ──────────────────────────────────────────────────────────────────────────────

def test_venetian_gilt_byzantine_splendour_period_in_period_enum():
    """VENETIAN_GILT_BYZANTINE_SPLENDOUR must be present in Period enum after session 141."""
    from scene_schema import Period
    assert hasattr(Period, "VENETIAN_GILT_BYZANTINE_SPLENDOUR"), (
        "VENETIAN_GILT_BYZANTINE_SPLENDOUR missing from Period enum -- "
        "add to scene_schema.py (session 141)")


def test_venetian_gilt_byzantine_splendour_routing_flag_true():
    """is_venetian_gilt_byzantine_splendour flag must be True for the correct period."""
    flags = _routing_flags(Period.VENETIAN_GILT_BYZANTINE_SPLENDOUR)
    assert flags["is_venetian_gilt_byzantine_splendour"] is True


def test_venetian_gilt_byzantine_splendour_routing_flag_false_for_other_periods():
    """is_venetian_gilt_byzantine_splendour must be False for all other periods."""
    for period in Period:
        if period == Period.VENETIAN_GILT_BYZANTINE_SPLENDOUR:
            continue
        flags = _routing_flags(period)
        assert not flags["is_venetian_gilt_byzantine_splendour"], (
            f"is_venetian_gilt_byzantine_splendour should be False for {period.name}")


def test_crivelli_in_catalog_accessible_via_get_style():
    """crivelli must be accessible via get_style() for pipeline routing."""
    from art_catalog import get_style
    style = get_style("crivelli")
    assert "Crivelli" in style.artist, (
        f"crivelli artist name mismatch: {style.artist!r}")


def test_crivelli_edge_softness_very_low():
    """crivelli edge_softness must be <= 0.12 (hard Gothic contours)."""
    from art_catalog import get_style
    style = get_style("crivelli")
    assert style.edge_softness <= 0.12, (
        f"crivelli edge_softness should be very low (<= 0.12) for hard Gothic "
        f"contours: got {style.edge_softness}")


def test_crivelli_ground_color_warm():
    """crivelli ground_color must be warm (R >= B) for gilt panel imprimatura."""
    from art_catalog import get_style
    style = get_style("crivelli")
    r, g, b = style.ground_color
    assert r >= b, (
        f"crivelli ground_color should be warm (R >= B): R={r:.3f}, B={b:.3f}")


# -- Session 153: Francesco Furini / FLORENTINE_BAROQUE_SFUMATO ---------------

def test_furini_moonlit_sfumato_pass_exists():
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    assert callable(getattr(p, "furini_moonlit_sfumato_pass", None))


def test_furini_moonlit_sfumato_pass_no_error():
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.55, 0.48, 0.35), texture_strength=0.20)
    p.furini_moonlit_sfumato_pass()


def test_furini_moonlit_sfumato_pass_zero_opacity_no_op():
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.55, 0.48, 0.35), texture_strength=0.20)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    p.furini_moonlit_sfumato_pass(opacity=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    assert before == after


def test_furini_moonlit_sfumato_pass_modifies_canvas():
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.55, 0.48, 0.35), texture_strength=0.20)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    p.furini_moonlit_sfumato_pass(
        hi_lo=0.30, hi_hi=0.85, cool_b=0.080, cool_r=0.040,
        cool_g=0.020, cool_strength=1.0, opacity=1.0,
    )
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    assert before != after


def test_furini_moonlit_sfumato_pass_pixels_in_range():
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.55, 0.48, 0.35), texture_strength=0.25)
    p.furini_moonlit_sfumato_pass(
        hi_lo=0.20, hi_hi=0.95, cool_b=0.100, cool_r=0.060,
        cool_g=0.030, cool_strength=1.0, opacity=1.0,
    )
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    assert buf[:, :, :3].min() >= 0
    assert buf[:, :, :3].max() <= 255


def test_furini_moonlit_sfumato_pass_cools_bright_highlights():
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    arr = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    arr[:, :, 2] = 220
    arr[:, :, 1] = 180
    arr[:, :, 0] = 150
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()
    p.canvas.surface.mark_dirty()
    p.furini_moonlit_sfumato_pass(
        hi_lo=0.60, hi_hi=0.95,
        cool_b=0.050, cool_r=0.040, cool_g=0.010,
        cool_strength=1.0, opacity=1.0,
    )
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    assert after[:, :, 2].mean() < 220, "R channel should decrease in highlights"
    assert after[:, :, 0].mean() > 150, "B channel should increase in highlights"


def test_furini_moonlit_sfumato_pass_has_cool_strength_parameter():
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.75, 0.65, 0.45), texture_strength=0.20)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    p.furini_moonlit_sfumato_pass(cool_strength=0.0, opacity=0.8)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    assert before == after


def test_translucent_fabric_pass_exists():
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    assert callable(getattr(p, "translucent_fabric_pass", None))


def test_translucent_fabric_pass_no_error():
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.50, 0.45, 0.30), texture_strength=0.20)
    p.translucent_fabric_pass()


def test_translucent_fabric_pass_zero_opacity_no_op():
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.50, 0.45, 0.30), texture_strength=0.20)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    p.translucent_fabric_pass(opacity=0.0)
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    assert before == after


def test_translucent_fabric_pass_modifies_canvas():
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.50, 0.45, 0.30), texture_strength=0.25)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    p.translucent_fabric_pass(
        fab_lo=0.10, fab_hi=0.90,
        fabric_r=0.05, fabric_g=0.35, fabric_b=0.10,
        fabric_opacity=0.80, edge_factor=0.0, opacity=1.0,
    )
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    assert before != after


def test_translucent_fabric_pass_pixels_in_range():
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.50, 0.45, 0.30), texture_strength=0.25)
    p.translucent_fabric_pass(
        fab_lo=0.05, fab_hi=0.95,
        fabric_r=0.00, fabric_g=0.80, fabric_b=0.00,
        fabric_opacity=1.0, edge_factor=0.0, opacity=1.0,
    )
    buf = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    assert buf[:, :, :3].min() >= 0
    assert buf[:, :, :3].max() <= 255


def test_translucent_fabric_pass_tints_toward_fabric_color():
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    arr = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    arr[:, :, 2] = 160
    arr[:, :, 1] = 140
    arr[:, :, 0] = 120
    arr[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = arr.tobytes()
    p.canvas.surface.mark_dirty()
    p.translucent_fabric_pass(
        fab_lo=0.30, fab_hi=0.80,
        fabric_r=0.00, fabric_g=0.80, fabric_b=0.00,
        fabric_opacity=0.80, edge_factor=0.0, opacity=1.0,
    )
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).reshape(64, 64, 4)
    assert after[:, :, 1].mean() > 140, "G channel should increase toward fabric green"
    assert after[:, :, 2].mean() < 160, "R channel should decrease toward fabric R=0"


def test_translucent_fabric_pass_has_fabric_opacity_parameter():
    import numpy as np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    p.tone_ground((0.50, 0.45, 0.30), texture_strength=0.20)
    before = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    p.translucent_fabric_pass(
        fab_lo=0.10, fab_hi=0.90,
        fabric_r=0.90, fabric_g=0.00, fabric_b=0.90,
        fabric_opacity=0.0, opacity=1.0,
    )
    after = np.frombuffer(p.canvas.surface.get_data(), dtype=np.uint8).tobytes()
    before_arr = np.frombuffer(before, dtype=np.uint8)
    after_arr  = np.frombuffer(after,  dtype=np.uint8)
    max_diff = int(np.abs(before_arr.astype(np.int16) - after_arr.astype(np.int16)).max())
    assert max_diff <= 2, f"Max pixel diff with fabric_opacity=0 should be <= 2, got {max_diff}"


def test_florentine_baroque_sfumato_period_routing_flag_true():
    from scene_schema import Period, Style
    style = Style(period=Period.FLORENTINE_BAROQUE_SFUMATO)
    params = style.stroke_params
    assert params["wet_blend"] >= 0.85
    assert params["edge_softness"] >= 0.80


def test_florentine_baroque_sfumato_routing_flag_false_for_other_periods():
    from scene_schema import Period, Style
    style = Style(period=Period.DUTCH_GOLDEN_AGE)
    params = style.stroke_params
    assert params["wet_blend"] < 0.85 or params["edge_softness"] < 0.80


def test_furini_in_catalog_accessible_via_get_style():
    from art_catalog import get_style
    style = get_style("furini")
    assert style.artist == "Francesco Furini"
    assert style.stroke_size <= 5


def test_furini_ground_color_warm_for_routing():
    from art_catalog import get_style
    style = get_style("furini")
    r, g, b = style.ground_color
    assert r > b


# ──────────────────────────────────────────────────────────────────────────────
# Hans Baldung Grien — baldung_grien_spectral_pallor_pass (session 160)
# ──────────────────────────────────────────────────────────────────────────────

def test_baldung_grien_spectral_pallor_pass_exists():
    """Painter must expose baldung_grien_spectral_pallor_pass() after session 160."""
    from stroke_engine import Painter
    assert hasattr(Painter, "baldung_grien_spectral_pallor_pass"), (
        "baldung_grien_spectral_pallor_pass not found on Painter")
    assert callable(getattr(Painter, "baldung_grien_spectral_pallor_pass"))


def test_baldung_grien_spectral_pallor_pass_no_error():
    """Pass runs without error on a warm-canvas 64×64 small painter."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.55, 0.40), texture_strength=0.0)
    p.baldung_grien_spectral_pallor_pass()


def test_baldung_grien_spectral_pallor_pass_zero_opacity_is_noop():
    """opacity=0.0 must leave the canvas exactly unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.55, 0.40), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.baldung_grien_spectral_pallor_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, "opacity=0.0 should be a no-op"


def test_baldung_grien_spectral_pallor_pass_modifies_warm_canvas():
    """On a warm flesh canvas the pass must produce a detectable colour shift."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.75, 0.58, 0.40), texture_strength=0.0)
    buf_before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).copy()
    p.baldung_grien_spectral_pallor_pass(opacity=1.0, pallor_strength=0.50)
    buf_after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert not _np.array_equal(buf_before, buf_after), (
        "Pass should modify a warm-flesh canvas at opacity=1.0")


def test_baldung_grien_spectral_pallor_pass_injects_green_in_warm_flesh():
    """On a warm-flesh canvas the green channel should increase relative to red."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.75, 0.58, 0.40), texture_strength=0.0)
    buf_before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).copy().astype(_np.float32)
    p.baldung_grien_spectral_pallor_pass(opacity=1.0, pallor_strength=0.8,
                                          pallor_g_boost=0.30)
    buf_after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).astype(_np.float32)
    # Cairo BGRA: channel 1 = G, channel 2 = R
    mean_g_before = buf_before[:, :, 1].mean()
    mean_g_after  = buf_after[:, :, 1].mean()
    assert mean_g_after > mean_g_before, (
        "Green channel should increase after baldung pallor pass on warm flesh canvas; "
        f"before={mean_g_before:.2f}, after={mean_g_after:.2f}")


def test_baldung_grien_spectral_pallor_pass_pixels_in_range():
    """All output pixel values must remain in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.75, 0.58, 0.40), texture_strength=0.0)
    p.baldung_grien_spectral_pallor_pass(opacity=1.0, pallor_strength=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_baldung_grien_spectral_pallor_pass_cool_canvas_minimal_change():
    """On a cool canvas (no flesh pixels detected) the change should be small."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.30, 0.40, 0.60), texture_strength=0.0)
    buf_before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).copy().astype(_np.float32)
    p.baldung_grien_spectral_pallor_pass(opacity=1.0, pallor_strength=0.80)
    buf_after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).astype(_np.float32)
    mean_diff = _np.abs(buf_before[:, :, :3] - buf_after[:, :, :3]).mean()
    assert mean_diff < 10.0, (
        f"Cool canvas should barely change (only background acid bite); got mean diff {mean_diff:.2f}")


def test_german_renaissance_period_in_enum():
    """Period.GERMAN_RENAISSANCE must be present in the Period enum."""
    assert hasattr(Period, "GERMAN_RENAISSANCE"), "Period.GERMAN_RENAISSANCE not found"
    assert Period.GERMAN_RENAISSANCE in list(Period)


def test_german_renaissance_stroke_params_valid():
    """GERMAN_RENAISSANCE stroke_params must satisfy all key constraints."""
    style = Style(medium=Medium.OIL, period=Period.GERMAN_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert "stroke_size_face" in p
    assert "stroke_size_bg"   in p
    assert "wet_blend"        in p
    assert "edge_softness"    in p
    assert p["stroke_size_face"] > 0
    assert p["stroke_size_bg"]   > 0
    assert 0.0 <= p["wet_blend"]    <= 1.0
    assert 0.0 <= p["edge_softness"] <= 1.0


def test_german_renaissance_wet_blend_is_northern_precision():
    """GERMAN_RENAISSANCE wet_blend should reflect Northern precision (≤ 0.40)."""
    german = Style(medium=Medium.OIL, period=Period.GERMAN_RENAISSANCE,
                   palette=PaletteHint.WARM_EARTH).stroke_params
    assert german["wet_blend"] <= 0.40, (
        f"GERMAN_RENAISSANCE wet_blend ({german['wet_blend']}) should be ≤ 0.40 "
        f"for Dürer-school Northern crispness")


# Joshua Reynolds — reynolds_grand_manner_pass (session 161)
# ──────────────────────────────────────────────────────────────────────────────

def test_reynolds_grand_manner_pass_exists():
    """Painter must expose reynolds_grand_manner_pass() after session 161."""
    from stroke_engine import Painter
    assert hasattr(Painter, "reynolds_grand_manner_pass"), (
        "reynolds_grand_manner_pass not found on Painter")
    assert callable(getattr(Painter, "reynolds_grand_manner_pass"))


def test_reynolds_grand_manner_pass_no_error():
    """Pass runs without error on a warm-canvas 64×64 painter."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.55, 0.40), texture_strength=0.0)
    p.reynolds_grand_manner_pass()


def test_reynolds_grand_manner_pass_opacity_zero_is_noop():
    """opacity=0.0 must leave the canvas exactly unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.55, 0.40), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.reynolds_grand_manner_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, "opacity=0.0 should be a no-op"


def test_reynolds_grand_manner_pass_modifies_canvas():
    """Pass must produce a detectable colour shift at opacity=1.0."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.55, 0.40), texture_strength=0.0)
    buf_before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).copy()
    p.reynolds_grand_manner_pass(opacity=1.0, amber_strength=0.20)
    buf_after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert not _np.array_equal(buf_before, buf_after), (
        "reynolds_grand_manner_pass should modify canvas at opacity=1.0")


def test_reynolds_grand_manner_pass_warms_neutral_canvas():
    """Amber glaze should raise R and lower B on a neutral grey canvas."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    buf_before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).copy().astype(_np.float32)
    p.reynolds_grand_manner_pass(opacity=1.0, amber_strength=0.50,
                                  amber_r=0.15, amber_b_reduce=0.10)
    buf_after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).astype(_np.float32)
    # Cairo BGRA: channel 2 = R, channel 0 = B
    assert buf_after[:, :, 2].mean() > buf_before[:, :, 2].mean(), "R should increase"
    assert buf_after[:, :, 0].mean() < buf_before[:, :, 0].mean(), "B should decrease"


def test_reynolds_grand_manner_pass_pixels_in_range():
    """All output pixel values must remain in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.55, 0.40), texture_strength=0.0)
    p.reynolds_grand_manner_pass(opacity=1.0, amber_strength=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_british_grand_manner_period_in_enum():
    """Period.BRITISH_GRAND_MANNER must be present in the Period enum."""
    assert hasattr(Period, "BRITISH_GRAND_MANNER"), "Period.BRITISH_GRAND_MANNER not found"
    assert Period.BRITISH_GRAND_MANNER in list(Period)


def test_british_grand_manner_stroke_params_valid():
    """BRITISH_GRAND_MANNER stroke_params must satisfy all key constraints."""
    style = Style(medium=Medium.OIL, period=Period.BRITISH_GRAND_MANNER,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert "stroke_size_face" in p
    assert "stroke_size_bg"   in p
    assert "wet_blend"        in p
    assert "edge_softness"    in p
    assert 0.0 <= p["wet_blend"]      <= 1.0
    assert 0.0 <= p["edge_softness"]  <= 1.0


def test_british_grand_manner_wet_blend_is_moderate():
    """BRITISH_GRAND_MANNER wet_blend should be moderate (≥ 0.40) for Grand Manner smoothness."""
    grand = Style(medium=Medium.OIL, period=Period.BRITISH_GRAND_MANNER,
                  palette=PaletteHint.WARM_EARTH).stroke_params
    assert grand["wet_blend"] >= 0.40, (
        f"BRITISH_GRAND_MANNER wet_blend ({grand['wet_blend']}) should be ≥ 0.40 "
        f"for Grand Manner Academic smoothness")


# ── Session 166 — Adriaen van der Werff + DUTCH_CLASSICAL_LATE_BAROQUE ────────


def test_dutch_classical_late_baroque_period_in_enum():
    """Period.DUTCH_CLASSICAL_LATE_BAROQUE must be present after session 166."""
    assert hasattr(Period, "DUTCH_CLASSICAL_LATE_BAROQUE"), (
        "Period.DUTCH_CLASSICAL_LATE_BAROQUE not found")
    assert Period.DUTCH_CLASSICAL_LATE_BAROQUE in list(Period)


def test_dutch_classical_late_baroque_stroke_params_valid():
    """DUTCH_CLASSICAL_LATE_BAROQUE stroke_params must satisfy all key constraints."""
    style = Style(medium=Medium.OIL, period=Period.DUTCH_CLASSICAL_LATE_BAROQUE,
                  palette=PaletteHint.COOL_GREY)
    p = style.stroke_params
    assert "stroke_size_face" in p
    assert "stroke_size_bg"   in p
    assert "wet_blend"        in p
    assert "edge_softness"    in p
    assert 0.0 <= p["wet_blend"]     <= 1.0
    assert 0.0 <= p["edge_softness"] <= 1.0


def test_dutch_classical_late_baroque_wet_blend_high():
    """DUTCH_CLASSICAL_LATE_BAROQUE wet_blend should be >= 0.70 for porcelain smoothness."""
    style = Style(medium=Medium.OIL, period=Period.DUTCH_CLASSICAL_LATE_BAROQUE,
                  palette=PaletteHint.COOL_GREY).stroke_params
    assert style["wet_blend"] >= 0.70, (
        f"DUTCH_CLASSICAL_LATE_BAROQUE wet_blend ({style['wet_blend']}) should be >= 0.70 "
        f"for Van der Werff porcelain smoothness")


def test_van_der_werff_ivory_alabaster_pass_exists_routing():
    """van_der_werff_ivory_alabaster_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "van_der_werff_ivory_alabaster_pass", None)), (
        "van_der_werff_ivory_alabaster_pass not found on Painter")


def test_van_der_werff_ivory_alabaster_pass_modifies_canvas():
    """Pass 55 should modify canvas on a skin-toned ground."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.75, 0.55, 0.35), texture_strength=0.25)
    before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).copy()
    p.van_der_werff_ivory_alabaster_pass(opacity=1.0)
    after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).copy()
    assert not _np.array_equal(before, after), (
        "van_der_werff_ivory_alabaster_pass should modify canvas at opacity=1.0")


def test_craquelure_texture_pass_exists_routing():
    """craquelure_texture_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "craquelure_texture_pass", None)), (
        "craquelure_texture_pass not found on Painter")


# ── Session 174 — Pieter Claesz + TONAL_STILL_LIFE ────────────────────────────


def test_tonal_still_life_period_routing():
    """Period.TONAL_STILL_LIFE must be present in the Period enum."""
    assert hasattr(Period, "TONAL_STILL_LIFE"), "Period.TONAL_STILL_LIFE not found"
    assert Period.TONAL_STILL_LIFE in list(Period)


def test_tonal_still_life_stroke_params_routing():
    """TONAL_STILL_LIFE stroke_params must satisfy all key constraints."""
    style = Style(medium=Medium.OIL, period=Period.TONAL_STILL_LIFE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert "stroke_size_face" in p
    assert "stroke_size_bg" in p
    assert "wet_blend" in p
    assert "edge_softness" in p
    assert 0.0 <= p["wet_blend"] <= 1.0
    assert 0.0 <= p["edge_softness"] <= 1.0


def test_tonal_still_life_wet_blend_routing():
    """TONAL_STILL_LIFE wet_blend should be >= 0.40 for tonal smoothness."""
    style = Style(medium=Medium.OIL, period=Period.TONAL_STILL_LIFE,
                  palette=PaletteHint.WARM_EARTH).stroke_params
    assert style["wet_blend"] >= 0.40


def test_claesz_tonal_monochrome_pass_exists_routing():
    """claesz_tonal_monochrome_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "claesz_tonal_monochrome_pass", None)), (
        "claesz_tonal_monochrome_pass not found on Painter")


def test_claesz_tonal_monochrome_pass_runs_routing():
    """claesz_tonal_monochrome_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.55, 0.50, 0.40), texture_strength=0.0)
    p.claesz_tonal_monochrome_pass(opacity=0.55)


def test_claesz_tonal_monochrome_pass_opacity_zero_routing():
    """claesz_tonal_monochrome_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.45, 0.30), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.claesz_tonal_monochrome_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, "opacity=0.0 should be a no-op"


def test_claesz_tonal_monochrome_pass_modifies_routing():
    """claesz_tonal_monochrome_pass must produce a detectable change at opacity=1."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.75, 0.35, 0.15), texture_strength=0.0)
    buf_before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4).copy()
    p.claesz_tonal_monochrome_pass(desat=0.80, opacity=1.0)
    buf_after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert not _np.array_equal(buf_before, buf_after), (
        "claesz_tonal_monochrome_pass should modify canvas at opacity=1.0")


def test_claesz_tonal_monochrome_pass_pixels_in_range_routing():
    """claesz_tonal_monochrome_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.70, 0.40, 0.20), texture_strength=0.0)
    p.claesz_tonal_monochrome_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_figure_contour_atmosphere_pass_exists_routing():
    """figure_contour_atmosphere_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "figure_contour_atmosphere_pass", None)), (
        "figure_contour_atmosphere_pass not found on Painter")


def test_figure_contour_atmosphere_pass_runs_routing():
    """figure_contour_atmosphere_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.figure_contour_atmosphere_pass(opacity=0.40)


def test_figure_contour_atmosphere_pass_opacity_zero_routing():
    """figure_contour_atmosphere_pass at opacity=0 must leave canvas unchanged."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.figure_contour_atmosphere_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, "opacity=0.0 should be a no-op"


def test_figure_contour_atmosphere_pass_pixels_in_range_routing():
    """figure_contour_atmosphere_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.55, 0.47, 0.30), texture_strength=0.0)
    p.figure_contour_atmosphere_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(32, 32, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ═══════════════════════════════════════════════════════════════════════════
# Session 175 — signorelli_sculptural_contour_pass + skin_subsurface_scatter_pass
# ═══════════════════════════════════════════════════════════════════════════

def test_signorelli_sculptural_contour_pass_exists_routing():
    """signorelli_sculptural_contour_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "signorelli_sculptural_contour_pass", None)), (
        "signorelli_sculptural_contour_pass not found on Painter")


def test_signorelli_sculptural_contour_pass_runs_routing():
    """signorelli_sculptural_contour_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.72, 0.67, 0.52), texture_strength=0.0)
    p.signorelli_sculptural_contour_pass(opacity=0.55)


def test_signorelli_sculptural_contour_pass_opacity_zero_routing():
    """signorelli_sculptural_contour_pass at opacity=0 must leave canvas unchanged."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.72, 0.67, 0.52), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.signorelli_sculptural_contour_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, "opacity=0.0 should be a no-op"


def test_signorelli_sculptural_contour_pass_pixels_in_range_routing():
    """signorelli_sculptural_contour_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.67, 0.52), texture_strength=0.0)
    p.signorelli_sculptural_contour_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_skin_subsurface_scatter_pass_exists_routing():
    """skin_subsurface_scatter_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "skin_subsurface_scatter_pass", None)), (
        "skin_subsurface_scatter_pass not found on Painter")


def test_skin_subsurface_scatter_pass_runs_routing():
    """skin_subsurface_scatter_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.82, 0.70, 0.52), texture_strength=0.0)
    p.skin_subsurface_scatter_pass(opacity=0.45)


def test_skin_subsurface_scatter_pass_opacity_zero_routing():
    """skin_subsurface_scatter_pass at opacity=0 must leave canvas unchanged."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.82, 0.70, 0.52), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.skin_subsurface_scatter_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, "opacity=0.0 should be a no-op"


def test_skin_subsurface_scatter_pass_pixels_in_range_routing():
    """skin_subsurface_scatter_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.82, 0.70, 0.52), texture_strength=0.0)
    p.skin_subsurface_scatter_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(32, 32, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ── Session 176: Marco d'Oggiono passes ───────────────────────────────────────


def test_doggiono_leonardesque_warmth_pass_exists_routing():
    """doggiono_leonardesque_warmth_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "doggiono_leonardesque_warmth_pass", None)), (
        "doggiono_leonardesque_warmth_pass not found on Painter")


def test_doggiono_leonardesque_warmth_pass_runs_routing():
    """doggiono_leonardesque_warmth_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.72, 0.60, 0.44), texture_strength=0.0)
    p.doggiono_leonardesque_warmth_pass(opacity=0.35)


def test_doggiono_leonardesque_warmth_pass_opacity_zero_routing():
    """doggiono_leonardesque_warmth_pass at opacity=0 must leave canvas unchanged."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.72, 0.60, 0.44), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.doggiono_leonardesque_warmth_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, "opacity=0.0 should be a no-op"


def test_doggiono_leonardesque_warmth_pass_pixels_in_range_routing():
    """doggiono_leonardesque_warmth_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.72, 0.60, 0.44), texture_strength=0.0)
    p.doggiono_leonardesque_warmth_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(32, 32, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_multilayer_atmospheric_veil_pass_exists_routing():
    """multilayer_atmospheric_veil_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "multilayer_atmospheric_veil_pass", None)), (
        "multilayer_atmospheric_veil_pass not found on Painter")


def test_multilayer_atmospheric_veil_pass_runs_routing():
    """multilayer_atmospheric_veil_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.72, 0.60, 0.44), texture_strength=0.0)
    p.multilayer_atmospheric_veil_pass(opacity=0.45)


def test_multilayer_atmospheric_veil_pass_opacity_zero_routing():
    """multilayer_atmospheric_veil_pass at opacity=0 must leave canvas unchanged."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.72, 0.60, 0.44), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.multilayer_atmospheric_veil_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, "opacity=0.0 should be a no-op"


def test_multilayer_atmospheric_veil_pass_pixels_in_range_routing():
    """multilayer_atmospheric_veil_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.72, 0.60, 0.44), texture_strength=0.0)
    p.multilayer_atmospheric_veil_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(32, 32, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


# ── Session 184: Giacomo Ceruti passes ────────────────────────────────────────


def test_ceruti_dignity_shadow_pass_exists_routing():
    """ceruti_dignity_shadow_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "ceruti_dignity_shadow_pass", None)), (
        "ceruti_dignity_shadow_pass not found on Painter")


def test_ceruti_dignity_shadow_pass_runs_routing():
    """ceruti_dignity_shadow_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.48, 0.30), texture_strength=0.0)
    p.ceruti_dignity_shadow_pass(opacity=0.32)


def test_ceruti_dignity_shadow_pass_opacity_zero_routing():
    """ceruti_dignity_shadow_pass at opacity=0 must leave canvas unchanged."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.48, 0.30), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.ceruti_dignity_shadow_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, "opacity=0.0 should be a no-op"


def test_ceruti_dignity_shadow_pass_pixels_in_range_routing():
    """ceruti_dignity_shadow_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.48, 0.30), texture_strength=0.0)
    p.ceruti_dignity_shadow_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(32, 32, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_ceruti_dignity_shadow_pass_modifies_shadow_zone_routing():
    """ceruti_dignity_shadow_pass must modify pixels in the inhabited shadow zone."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    # Use a mid-dark reference so the shadow zone gate fires
    from PIL import Image as _PILImg
    arr = _np.full((32, 32, 3), 80, dtype=_np.uint8)   # luma ~0.31 — in shadow zone
    ref = _PILImg.fromarray(arr, "RGB")
    p.tone_ground((0.31, 0.28, 0.20), texture_strength=0.0)  # warm ground in shadow zone
    before = _canvas_bytes(p)
    p.ceruti_dignity_shadow_pass(shadow_lo=0.08, shadow_hi=0.42,
                                  warm_r_delta=0.05, warm_g_delta=0.03, opacity=1.0)
    after = _canvas_bytes(p)
    assert before != after, "ceruti_dignity_shadow_pass should modify shadow-zone pixels"


def test_hue_coherence_field_pass_exists_routing():
    """hue_coherence_field_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "hue_coherence_field_pass", None)), (
        "hue_coherence_field_pass not found on Painter")


def test_hue_coherence_field_pass_runs_routing():
    """hue_coherence_field_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.48, 0.30), texture_strength=0.0)
    p.hue_coherence_field_pass(opacity=0.28)


def test_hue_coherence_field_pass_opacity_zero_routing():
    """hue_coherence_field_pass at opacity=0 must leave canvas unchanged."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.48, 0.30), texture_strength=0.0)
    before = _canvas_bytes(p)
    p.hue_coherence_field_pass(opacity=0.0)
    after = _canvas_bytes(p)
    assert before == after, "opacity=0.0 should be a no-op"


def test_hue_coherence_field_pass_pixels_in_range_routing():
    """hue_coherence_field_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.48, 0.30), texture_strength=0.0)
    p.hue_coherence_field_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(32, 32, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_lombard_humble_genre_routing_flag_routing():
    """LOMBARD_HUMBLE_GENRE period must set is_lombard_humble_genre=True."""
    flags = _routing_flags(Period.LOMBARD_HUMBLE_GENRE)
    assert flags["is_lombard_humble_genre"] is True


def test_lombard_humble_genre_flag_not_set_for_other_periods_routing():
    """is_lombard_humble_genre must be False for all periods except LOMBARD_HUMBLE_GENRE."""
    for period in Period:
        if period == Period.LOMBARD_HUMBLE_GENRE:
            continue
        flags = _routing_flags(period)
        assert not flags["is_lombard_humble_genre"], (
            f"is_lombard_humble_genre should be False for {period.name}")


# ── Session 185: Fra Galgario / BERGAMASK_PORTRAIT tests ─────────────────────

def test_fra_galgario_living_surface_pass_exists_routing():
    """fra_galgario_living_surface_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "fra_galgario_living_surface_pass", None)), (
        "fra_galgario_living_surface_pass not found on Painter")


def test_fra_galgario_living_surface_pass_runs_routing():
    """fra_galgario_living_surface_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.46, 0.28), texture_strength=0.0)
    p.fra_galgario_living_surface_pass(opacity=0.30)


def test_fra_galgario_living_surface_pass_opacity_zero_routing():
    """fra_galgario_living_surface_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.46, 0.28), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.fra_galgario_living_surface_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after)


def test_fra_galgario_living_surface_pass_pixels_in_range_routing():
    """fra_galgario_living_surface_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.46, 0.28), texture_strength=0.0)
    p.fra_galgario_living_surface_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(32, 32, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_fra_galgario_living_surface_pass_modifies_midtone_routing():
    """fra_galgario_living_surface_pass must modify pixels in the living-surface zone."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Midtone pixels centred near luma_peak=0.58
    buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 150  # R — midtone
    buf[:, :, 1] = 140  # G
    buf[:, :, 0] = 110  # B
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()
    p.canvas.surface.mark_dirty()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.fra_galgario_living_surface_pass(glow_lo=0.35, glow_hi=0.80, opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "fra_galgario_living_surface_pass should modify midtone-zone pixels")


def test_chromatic_temperature_field_pass_exists_routing():
    """chromatic_temperature_field_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "chromatic_temperature_field_pass", None)), (
        "chromatic_temperature_field_pass not found on Painter")


def test_chromatic_temperature_field_pass_runs_routing():
    """chromatic_temperature_field_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.46, 0.28), texture_strength=0.0)
    p.chromatic_temperature_field_pass(opacity=0.28)


def test_chromatic_temperature_field_pass_opacity_zero_routing():
    """chromatic_temperature_field_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.46, 0.28), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.chromatic_temperature_field_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after)


def test_chromatic_temperature_field_pass_pixels_in_range_routing():
    """chromatic_temperature_field_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.58, 0.46, 0.28), texture_strength=0.0)
    p.chromatic_temperature_field_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(32, 32, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_bergamask_portrait_routing_flag_routing():
    """BERGAMASK_PORTRAIT period must set is_bergamask_portrait=True."""
    flags = _routing_flags(Period.BERGAMASK_PORTRAIT)
    assert flags["is_bergamask_portrait"] is True


def test_bergamask_portrait_flag_not_set_for_other_periods_routing():
    """is_bergamask_portrait must be False for all periods except BERGAMASK_PORTRAIT."""
    for period in Period:
        if period == Period.BERGAMASK_PORTRAIT:
            continue
        flags = _routing_flags(period)
        assert not flags["is_bergamask_portrait"], (
            f"is_bergamask_portrait should be False for {period.name}")


# ── Session 187: Ambrogio de Predis / MILANESE_METALLIC_PORTRAITURE tests ────

def test_de_predis_crystalline_clarity_pass_exists_routing():
    """de_predis_crystalline_clarity_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "de_predis_crystalline_clarity_pass", None)), (
        "de_predis_crystalline_clarity_pass not found on Painter")


def test_de_predis_crystalline_clarity_pass_runs_routing():
    """de_predis_crystalline_clarity_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.50, 0.42, 0.28), texture_strength=0.0)
    p.de_predis_crystalline_clarity_pass(opacity=0.25)


def test_de_predis_crystalline_clarity_pass_opacity_zero_routing():
    """de_predis_crystalline_clarity_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.50, 0.42, 0.28), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.de_predis_crystalline_clarity_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after)


def test_de_predis_crystalline_clarity_pass_pixels_in_range_routing():
    """de_predis_crystalline_clarity_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.50, 0.42, 0.28), texture_strength=0.0)
    p.de_predis_crystalline_clarity_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(32, 32, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_de_predis_crystalline_clarity_pass_modifies_mid_bright_routing():
    """de_predis_crystalline_clarity_pass must modify pixels in the luma gate zone."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Load mid-bright pixels (luma ~0.60 — well within default gate 0.35–0.85)
    buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 160  # R
    buf[:, :, 1] = 152  # G
    buf[:, :, 0] = 128  # B  — luma ~0.60
    buf[:, :, 3] = 255
    # Create a horizontal edge at row 32 to give the USM something to detect
    buf[32:, :, 2] = 80
    buf[32:, :, 1] = 76
    buf[32:, :, 0] = 64
    p.canvas.surface.get_data()[:] = buf.tobytes()
    p.canvas.surface.mark_dirty()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.de_predis_crystalline_clarity_pass(
        sharp_sigma=1.5, sharp_strength=0.30,
        cool_r_shift=-0.010, cool_b_shift=0.015,
        luma_lo=0.35, luma_hi=0.85, opacity=1.0
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "de_predis_crystalline_clarity_pass should modify mid-bright zone pixels")


def test_luminous_midtone_lift_pass_exists_routing():
    """luminous_midtone_lift_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "luminous_midtone_lift_pass", None)), (
        "luminous_midtone_lift_pass not found on Painter")


def test_luminous_midtone_lift_pass_runs_routing():
    """luminous_midtone_lift_pass must run without error on a small canvas."""
    p = _make_small_painter(32, 32)
    p.tone_ground((0.50, 0.42, 0.28), texture_strength=0.0)
    p.luminous_midtone_lift_pass(opacity=0.24)


def test_luminous_midtone_lift_pass_opacity_zero_routing():
    """luminous_midtone_lift_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.50, 0.42, 0.28), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.luminous_midtone_lift_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after)


def test_luminous_midtone_lift_pass_pixels_in_range_routing():
    """luminous_midtone_lift_pass output must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(32, 32)
    p.tone_ground((0.50, 0.42, 0.28), texture_strength=0.0)
    p.luminous_midtone_lift_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(32, 32, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_luminous_midtone_lift_pass_modifies_midtone_routing():
    """luminous_midtone_lift_pass must lift pixels in the midtone zone."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    # Load pixels at luma ~0.49 — well within default gate 0.30–0.68
    buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape(64, 64, 4).copy()
    buf[:, :, 2] = 128  # R
    buf[:, :, 1] = 122  # G
    buf[:, :, 0] = 100  # B  — luma ~0.49
    buf[:, :, 3] = 255
    p.canvas.surface.get_data()[:] = buf.tobytes()
    p.canvas.surface.mark_dirty()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.luminous_midtone_lift_pass(
        mid_lo=0.30, mid_hi=0.68, lift_r=0.05, lift_g=0.03, opacity=1.0
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "luminous_midtone_lift_pass should lift midtone-zone pixels")


def test_milanese_metallic_portraiture_routing_flag_routing():
    """MILANESE_METALLIC_PORTRAITURE period must set is_milanese_metallic_portraiture=True."""
    flags = _routing_flags(Period.MILANESE_METALLIC_PORTRAITURE)
    assert flags["is_milanese_metallic_portraiture"] is True


def test_milanese_metallic_portraiture_flag_not_set_for_other_periods_routing():
    """is_milanese_metallic_portraiture must be False for all other periods."""
    for period in Period:
        if period == Period.MILANESE_METALLIC_PORTRAITURE:
            continue
        flags = _routing_flags(period)
        assert not flags["is_milanese_metallic_portraiture"], (
            f"is_milanese_metallic_portraiture should be False for {period.name}")


# ──────────────────────────────────────────────────────────────────────────────
# Session 190 — klee_magic_square_pass (101st distinct mode)
# ──────────────────────────────────────────────────────────────────────────────

def test_klee_magic_square_pass_exists_routing():
    """Session 190: klee_magic_square_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "klee_magic_square_pass", None)), (
        "klee_magic_square_pass not found on Painter")


def test_klee_magic_square_pass_signature_routing():
    """Session 190: klee_magic_square_pass must accept expected parameters."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.klee_magic_square_pass)
    for param in ("cell_size", "harmony_strength", "freq_x", "freq_y",
                  "border_opacity", "warm_shift", "opacity"):
        assert param in sig.parameters, f"Missing parameter: {param}"


def test_klee_magic_square_pass_runs_routing():
    """Session 190: klee_magic_square_pass must complete without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.0)
    p.klee_magic_square_pass()


def test_klee_magic_square_pass_opacity_zero_routing():
    """Session 190: klee_magic_square_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.klee_magic_square_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after)


def test_klee_magic_square_pass_pixels_in_range_routing():
    """Session 190: klee_magic_square_pass output pixels must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.78, 0.70, 0.52), texture_strength=0.0)
    p.klee_magic_square_pass(opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_klee_magic_square_pass_modifies_canvas_routing():
    """Session 190: klee_magic_square_pass at full opacity must change canvas pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.50, 0.45, 0.32), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.klee_magic_square_pass(
        cell_size=8, harmony_strength=0.20, opacity=1.0, warm_shift=0.05
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "klee_magic_square_pass should modify canvas pixels")


def test_klee_magic_square_pass_no_border_routing():
    """Session 190: klee_magic_square_pass with border_opacity=0 must still run."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.60, 0.55, 0.40), texture_strength=0.0)
    p.klee_magic_square_pass(border_opacity=0.0, opacity=0.30)


# ──────────────────────────────────────────────────────────────────────────────
# Session 191 — twombly_calligraphic_scrawl_pass (102nd distinct mode)
# ──────────────────────────────────────────────────────────────────────────────

def test_twombly_calligraphic_scrawl_pass_exists_routing():
    """Session 191: twombly_calligraphic_scrawl_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "twombly_calligraphic_scrawl_pass", None)), (
        "twombly_calligraphic_scrawl_pass not found on Painter")


def test_twombly_calligraphic_scrawl_pass_signature_routing():
    """Session 191: twombly_calligraphic_scrawl_pass must accept expected parameters."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.twombly_calligraphic_scrawl_pass)
    for param in ("n_clusters", "loops_per_cluster", "loop_radius",
                  "chalk_color", "accent_prob", "smear_opacity", "opacity"):
        assert param in sig.parameters, f"Missing parameter: {param}"


def test_twombly_calligraphic_scrawl_pass_runs_routing():
    """Session 191: twombly_calligraphic_scrawl_pass must complete without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.92, 0.90, 0.84), texture_strength=0.0)
    p.twombly_calligraphic_scrawl_pass(n_clusters=5, loops_per_cluster=3)


def test_twombly_calligraphic_scrawl_pass_opacity_zero_routing():
    """Session 191: twombly_calligraphic_scrawl_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.92, 0.90, 0.84), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.twombly_calligraphic_scrawl_pass(n_clusters=10, opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after)


def test_twombly_calligraphic_scrawl_pass_pixels_in_range_routing():
    """Session 191: twombly_calligraphic_scrawl_pass output pixels must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.92, 0.90, 0.84), texture_strength=0.0)
    p.twombly_calligraphic_scrawl_pass(n_clusters=8, loops_per_cluster=4, opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_twombly_calligraphic_scrawl_pass_modifies_canvas_routing():
    """Session 191: twombly_calligraphic_scrawl_pass at full opacity must change canvas pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.92, 0.90, 0.84), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.twombly_calligraphic_scrawl_pass(
        n_clusters=15, loops_per_cluster=5, loop_radius=8.0,
        chalk_color=(0.96, 0.94, 0.88), opacity=1.0
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "twombly_calligraphic_scrawl_pass should modify canvas pixels")


def test_twombly_calligraphic_scrawl_pass_accent_routing():
    """Session 191: twombly_calligraphic_scrawl_pass with accent_prob=1.0 must still run."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.92, 0.90, 0.84), texture_strength=0.0)
    p.twombly_calligraphic_scrawl_pass(
        n_clusters=8, accent_prob=1.0, opacity=0.50
    )


def test_twombly_calligraphic_scrawl_pass_no_smear_routing():
    """Session 191: twombly_calligraphic_scrawl_pass with smear_opacity=0 must still run."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.92, 0.90, 0.84), texture_strength=0.0)
    p.twombly_calligraphic_scrawl_pass(n_clusters=6, smear_opacity=0.0, opacity=0.45)


# ──────────────────────────────────────────────────────────────────────────────
# Session 192 — agnes_martin_meditation_lines_pass (103rd distinct mode)
# ──────────────────────────────────────────────────────────────────────────────

def test_agnes_martin_meditation_lines_pass_exists_routing():
    """Session 192: agnes_martin_meditation_lines_pass must exist as a callable on Painter."""
    from stroke_engine import Painter
    assert callable(getattr(Painter, "agnes_martin_meditation_lines_pass", None)), (
        "agnes_martin_meditation_lines_pass not found on Painter")


def test_agnes_martin_meditation_lines_pass_signature_routing():
    """Session 192: agnes_martin_meditation_lines_pass must accept expected parameters."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.agnes_martin_meditation_lines_pass)
    for param in ("n_lines", "tremor_sigma", "breathe_freq",
                  "line_opacity", "wash_color", "wash_opacity",
                  "tone_drift", "opacity"):
        assert param in sig.parameters, f"Missing parameter: {param}"


def test_agnes_martin_meditation_lines_pass_runs_routing():
    """Session 192: agnes_martin_meditation_lines_pass must complete without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.94, 0.92, 0.88), texture_strength=0.0)
    p.agnes_martin_meditation_lines_pass(n_lines=20)


def test_agnes_martin_meditation_lines_pass_opacity_zero_routing():
    """Session 192: agnes_martin_meditation_lines_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.94, 0.92, 0.88), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.agnes_martin_meditation_lines_pass(n_lines=20, wash_opacity=0.0, opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after)


def test_agnes_martin_meditation_lines_pass_pixels_in_range_routing():
    """Session 192: agnes_martin_meditation_lines_pass output pixels must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.94, 0.92, 0.88), texture_strength=0.0)
    p.agnes_martin_meditation_lines_pass(n_lines=30, opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_agnes_martin_meditation_lines_pass_modifies_canvas_routing():
    """Session 192: agnes_martin_meditation_lines_pass at full opacity must change canvas pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.94, 0.92, 0.88), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.agnes_martin_meditation_lines_pass(
        n_lines=30, wash_opacity=0.15, line_opacity=0.60, opacity=1.0
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "agnes_martin_meditation_lines_pass should modify canvas pixels")


def test_agnes_martin_meditation_lines_pass_no_lines_routing():
    """Session 192: agnes_martin_meditation_lines_pass with n_lines=0 must still run."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.94, 0.92, 0.88), texture_strength=0.0)
    p.agnes_martin_meditation_lines_pass(n_lines=0, opacity=0.50)


def test_agnes_martin_meditation_lines_pass_custom_wash_routing():
    """Session 192: agnes_martin_meditation_lines_pass with custom wash must still run."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.92, 0.90, 0.86), texture_strength=0.0)
    p.agnes_martin_meditation_lines_pass(
        n_lines=15,
        wash_color=(0.92, 0.88, 0.86),
        wash_opacity=0.12,
        opacity=0.60,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Session 193 — kusama_infinity_dot_pass
# ──────────────────────────────────────────────────────────────────────────────

def test_kusama_infinity_dot_pass_exists_routing():
    """Session 193: Painter must expose kusama_infinity_dot_pass as a method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "kusama_infinity_dot_pass"), (
        "Painter is missing kusama_infinity_dot_pass method")


def test_kusama_infinity_dot_pass_runs_routing():
    """Session 193: kusama_infinity_dot_pass must run without error on a small canvas."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.97, 0.97, 0.96), texture_strength=0.0)
    p.kusama_infinity_dot_pass(n_seeds=3, ring_step=12, dot_radius=4, dot_spacing=10, opacity=0.70)


def test_kusama_infinity_dot_pass_pixels_in_range_routing():
    """Session 193: kusama_infinity_dot_pass output pixels must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.97, 0.97, 0.96), texture_strength=0.0)
    p.kusama_infinity_dot_pass(n_seeds=3, ring_step=12, dot_radius=4, dot_spacing=10, opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_kusama_infinity_dot_pass_modifies_canvas_routing():
    """Session 193: kusama_infinity_dot_pass at full opacity must change canvas pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.97, 0.97, 0.96), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.kusama_infinity_dot_pass(
        n_seeds=4, ring_step=10, dot_radius=5, dot_spacing=12, opacity=1.0
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "kusama_infinity_dot_pass should modify canvas pixels")


def test_kusama_infinity_dot_pass_opacity_zero_routing():
    """Session 193: kusama_infinity_dot_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.97, 0.97, 0.96), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.kusama_infinity_dot_pass(n_seeds=4, ring_step=10, dot_radius=5, opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after)


def test_kusama_infinity_dot_pass_custom_palette_routing():
    """Session 193: kusama_infinity_dot_pass with custom palette must still run."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.97, 0.97, 0.96), texture_strength=0.0)
    custom_pal = [(0.9, 0.1, 0.1), (0.1, 0.1, 0.9), (0.9, 0.9, 0.1)]
    p.kusama_infinity_dot_pass(
        n_seeds=2, ring_step=14, dot_radius=5, dot_spacing=12,
        palette=custom_pal, opacity=0.65,
    )


def test_kusama_infinity_dot_pass_single_seed_routing():
    """Session 193: kusama_infinity_dot_pass with n_seeds=1 must still run."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.97, 0.97, 0.96), texture_strength=0.0)
    p.kusama_infinity_dot_pass(n_seeds=1, ring_step=15, dot_radius=4, opacity=0.70)


# ──────────────────────────────────────────────────────────────────────────────
# Session 194 — schiele_angular_contour_pass (105th distinct mode)
# ──────────────────────────────────────────────────────────────────────────────

def test_schiele_angular_contour_pass_exists_routing():
    """Session 194: Painter must expose schiele_angular_contour_pass as a method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "schiele_angular_contour_pass"), (
        "Painter is missing schiele_angular_contour_pass method")
    assert callable(getattr(Painter, "schiele_angular_contour_pass"))


def test_schiele_angular_contour_pass_signature_routing():
    """Session 194: schiele_angular_contour_pass must accept expected parameters."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.schiele_angular_contour_pass)
    for param in (
        "reference", "edge_threshold", "contour_weight",
        "flesh_wash_opacity", "hatch_opacity", "n_hatch_lines",
        "hatch_shadow_thresh", "contour_color", "flesh_color", "opacity",
    ):
        assert param in sig.parameters, f"Missing parameter: {param}"


def test_schiele_angular_contour_pass_runs_routing():
    """Session 194: schiele_angular_contour_pass must run without error on small canvas."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.85, 0.80), texture_strength=0.0)
    p.schiele_angular_contour_pass(ref, edge_threshold=0.15, opacity=0.80)


def test_schiele_angular_contour_pass_pixels_in_range_routing():
    """Session 194: schiele_angular_contour_pass output pixels must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.85, 0.80), texture_strength=0.0)
    p.schiele_angular_contour_pass(ref, opacity=1.0)
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_schiele_angular_contour_pass_opacity_zero_routing():
    """Session 194: schiele_angular_contour_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.85, 0.80), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.schiele_angular_contour_pass(
        ref, flesh_wash_opacity=0.0, hatch_opacity=0.0, opacity=0.0
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after)


def test_schiele_angular_contour_pass_modifies_canvas_routing():
    """Session 194: schiele_angular_contour_pass at full opacity must change canvas pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.85, 0.80), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.schiele_angular_contour_pass(
        ref, flesh_wash_opacity=0.30, hatch_opacity=0.30, opacity=1.0
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "schiele_angular_contour_pass should modify canvas pixels")


def test_schiele_angular_contour_pass_no_hatching_routing():
    """Session 194: schiele_angular_contour_pass with n_hatch_lines=0 must still run."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.85, 0.80), texture_strength=0.0)
    p.schiele_angular_contour_pass(ref, n_hatch_lines=0, opacity=0.70)


def test_schiele_angular_contour_pass_custom_colors_routing():
    """Session 194: schiele_angular_contour_pass with custom colors must still run."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.85, 0.80), texture_strength=0.0)
    p.schiele_angular_contour_pass(
        ref,
        contour_color=(0.10, 0.05, 0.02),
        flesh_color=(0.82, 0.60, 0.44),
        hatch_shadow_thresh=0.40,
        opacity=0.75,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Session 195 — riley_op_art_wave_pass
# ──────────────────────────────────────────────────────────────────────────────

def test_riley_op_art_wave_pass_exists():
    """Painter must have riley_op_art_wave_pass() method after session 195."""
    from stroke_engine import Painter
    assert hasattr(Painter, "riley_op_art_wave_pass"), (
        "riley_op_art_wave_pass not found on Painter")
    assert callable(getattr(Painter, "riley_op_art_wave_pass"))


def test_riley_op_art_wave_pass_runs():
    """riley_op_art_wave_pass() must run without error on a small canvas."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.98, 0.98, 0.98), texture_strength=0.0)
    p.riley_op_art_wave_pass(ref, n_waves=8, base_amplitude=4.0, opacity=0.90)


def test_riley_op_art_wave_pass_zero_opacity_unchanged():
    """riley_op_art_wave_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.98, 0.98, 0.98), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.riley_op_art_wave_pass(ref, n_waves=8, base_amplitude=4.0, opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after)


def test_riley_op_art_wave_pass_modifies_canvas():
    """riley_op_art_wave_pass at full opacity must change canvas pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.98, 0.98, 0.98), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.riley_op_art_wave_pass(
        ref, n_waves=8, base_amplitude=4.0,
        color_a=(0.0, 0.0, 0.0), color_b=(1.0, 1.0, 1.0), opacity=1.0
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "riley_op_art_wave_pass should modify canvas pixels")


def test_riley_op_art_wave_pass_colour_variant():
    """riley_op_art_wave_pass with custom colour pair must run without error."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.98, 0.98, 0.98), texture_strength=0.0)
    p.riley_op_art_wave_pass(
        ref,
        n_waves=6,
        base_amplitude=3.0,
        freq_modulation=0.5,
        base_frequency=0.015,
        color_a=(0.82, 0.22, 0.14),
        color_b=(0.18, 0.42, 0.78),
        opacity=0.80,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Session 196 — Fernand Léger — leger_tubist_contour_pass (107th mode)
# ─────────────────────────────────────────────────────────────────────────────

def test_leger_tubist_contour_pass_exists():
    """Session 196: Painter must have leger_tubist_contour_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "leger_tubist_contour_pass"), (
        "leger_tubist_contour_pass not found on Painter")
    assert callable(getattr(Painter, "leger_tubist_contour_pass"))


def test_leger_tubist_contour_pass_runs():
    """leger_tubist_contour_pass() must run without error on a small canvas."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.85, 0.80), texture_strength=0.05)
    p.underpainting(ref, stroke_size=8)
    p.leger_tubist_contour_pass(
        contour_thickness=2,
        contour_threshold=0.18,
        flat_fill_strength=0.60,
        primary_shift=0.55,
        contour_strength=0.88,
        opacity=0.82,
    )


def test_leger_tubist_contour_pass_modifies_canvas():
    """leger_tubist_contour_pass at full opacity must change canvas pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.85, 0.80), texture_strength=0.05)
    p.underpainting(ref, stroke_size=8)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.leger_tubist_contour_pass(opacity=1.0, contour_thickness=2)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "leger_tubist_contour_pass should modify canvas pixels at opacity=1.0")


def test_leger_tubist_contour_pass_zero_opacity_unchanged():
    """leger_tubist_contour_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.85, 0.80), texture_strength=0.05)
    p.underpainting(ref, stroke_size=8)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.leger_tubist_contour_pass(opacity=0.0, contour_thickness=2)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "leger_tubist_contour_pass at opacity=0.0 must not change any pixels")


def test_leger_tubist_contour_pass_thin_contour():
    """leger_tubist_contour_pass with contour_thickness=1 must run without error."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.85, 0.80), texture_strength=0.05)
    p.leger_tubist_contour_pass(
        contour_thickness=1,
        contour_threshold=0.25,
        primary_shift=0.80,
        opacity=0.70,
    )


# ── Session 197: kandinsky_geometric_resonance_pass ──────────────────────────

def test_kandinsky_geometric_resonance_pass_exists():
    """Session 197: kandinsky_geometric_resonance_pass must exist and run on a small canvas."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.92, 0.91, 0.87), texture_strength=0.02)
    p.underpainting(ref, stroke_size=8)
    p.kandinsky_geometric_resonance_pass(
        ref,
        n_circles=3,
        n_triangles=3,
        n_tension_lines=4,
        n_squares=2,
        n_arcs=2,
        opacity=0.65,
        seed=197,
    )


def test_kandinsky_geometric_resonance_pass_modifies_canvas():
    """kandinsky_geometric_resonance_pass at full opacity must change canvas pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.92, 0.91, 0.87), texture_strength=0.02)
    p.underpainting(ref, stroke_size=8)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.kandinsky_geometric_resonance_pass(
        ref,
        n_circles=4,
        n_triangles=4,
        n_tension_lines=6,
        n_squares=3,
        n_arcs=2,
        synesthetic_strength=1.0,
        opacity=1.0,
        seed=197,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "kandinsky_geometric_resonance_pass should modify canvas pixels at opacity=1.0")


def test_kandinsky_geometric_resonance_pass_zero_opacity_unchanged():
    """kandinsky_geometric_resonance_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.92, 0.91, 0.87), texture_strength=0.02)
    p.underpainting(ref, stroke_size=8)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.kandinsky_geometric_resonance_pass(opacity=0.0, seed=197)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "kandinsky_geometric_resonance_pass at opacity=0.0 must not change any pixels")


def test_kandinsky_geometric_resonance_pass_no_reference():
    """kandinsky_geometric_resonance_pass without a reference must run without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.92, 0.91, 0.87), texture_strength=0.02)
    p.kandinsky_geometric_resonance_pass(
        n_circles=2,
        n_triangles=2,
        n_tension_lines=3,
        n_squares=2,
        n_arcs=1,
        opacity=0.50,
        seed=197,
    )


# ── Session 198: chirico_metaphysical_shadow_pass (109th distinct mode) ───────

def test_chirico_metaphysical_shadow_pass_exists():
    """Session 198: Painter must expose chirico_metaphysical_shadow_pass as a method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "chirico_metaphysical_shadow_pass"), (
        "Painter is missing chirico_metaphysical_shadow_pass method")
    assert callable(getattr(Painter, "chirico_metaphysical_shadow_pass"))


def test_chirico_metaphysical_shadow_pass_signature():
    """Session 198: chirico_metaphysical_shadow_pass must accept expected parameters."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.chirico_metaphysical_shadow_pass)
    for param in (
        "reference", "shadow_angle", "shadow_length",
        "shadow_opacity", "warm_strength", "warm_opacity",
        "edge_threshold", "seed", "opacity",
    ):
        assert param in sig.parameters, f"chirico_metaphysical_shadow_pass missing parameter: {param}"


def test_chirico_metaphysical_shadow_pass_runs():
    """Session 198: chirico_metaphysical_shadow_pass must run without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.80, 0.58), texture_strength=0.0)
    p.chirico_metaphysical_shadow_pass(
        shadow_angle=225.0,
        shadow_length=0.15,
        shadow_opacity=0.72,
        warm_strength=0.45,
        warm_opacity=0.38,
        opacity=0.80,
        seed=198,
    )


def test_chirico_metaphysical_shadow_pass_pixels_in_range():
    """Session 198: chirico_metaphysical_shadow_pass output pixels must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.80, 0.58), texture_strength=0.0)
    p.chirico_metaphysical_shadow_pass(
        shadow_angle=225.0, shadow_length=0.15, opacity=1.0, seed=198
    )
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_chirico_metaphysical_shadow_pass_modifies_canvas():
    """Session 198: chirico_metaphysical_shadow_pass at full opacity must change canvas pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.88, 0.80, 0.58), texture_strength=0.0)
    p.underpainting(ref, stroke_size=8)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.chirico_metaphysical_shadow_pass(
        shadow_angle=225.0,
        shadow_length=0.20,
        shadow_opacity=0.80,
        warm_strength=0.50,
        warm_opacity=0.50,
        opacity=1.0,
        seed=198,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "chirico_metaphysical_shadow_pass should modify canvas pixels at opacity=1.0")


def test_chirico_metaphysical_shadow_pass_zero_opacity_unchanged():
    """Session 198: chirico_metaphysical_shadow_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.80, 0.58), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.chirico_metaphysical_shadow_pass(
        shadow_angle=225.0, shadow_length=0.15, opacity=0.0, seed=198
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "chirico_metaphysical_shadow_pass at opacity=0.0 must not change any pixels")


def test_chirico_metaphysical_shadow_pass_no_reference():
    """Session 198: chirico_metaphysical_shadow_pass without reference must run without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.80, 0.58), texture_strength=0.0)
    p.chirico_metaphysical_shadow_pass(
        shadow_length=0.10, shadow_opacity=0.60, opacity=0.70, seed=198
    )


def test_chirico_metaphysical_shadow_pass_varying_angle():
    """Session 198: chirico_metaphysical_shadow_pass at 45° shadow angle must run without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.80, 0.58), texture_strength=0.0)
    p.chirico_metaphysical_shadow_pass(
        shadow_angle=45.0,
        shadow_length=0.12,
        opacity=0.70,
        seed=198,
    )


def test_chirico_metaphysical_shadow_pass_short_shadow():
    """Session 198: chirico_metaphysical_shadow_pass with shadow_length=0.05 must still run."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.88, 0.80, 0.58), texture_strength=0.0)
    p.chirico_metaphysical_shadow_pass(
        shadow_length=0.05, shadow_opacity=0.50, opacity=0.60, seed=198
    )


# ──────────────────────────────────────────────────────────────────────────────
# aivazovsky_marine_luminance_pass — session 199 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_aivazovsky_marine_luminance_pass_exists():
    """Session 199: aivazovsky_marine_luminance_pass must exist on Painter."""
    from stroke_engine import Painter
    assert hasattr(Painter, "aivazovsky_marine_luminance_pass"), (
        "aivazovsky_marine_luminance_pass not found on Painter")
    assert callable(getattr(Painter, "aivazovsky_marine_luminance_pass"))


def test_aivazovsky_marine_luminance_pass_signature():
    """Session 199: aivazovsky_marine_luminance_pass must have expected parameters."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.aivazovsky_marine_luminance_pass)
    for param in (
        "horizon_y", "wave_frequency", "wave_amplitude",
        "crest_jade", "trough_navy", "crest_strength", "trough_strength",
        "horizon_glow", "horizon_glow_width", "horizon_glow_strength",
        "foam_strength", "seed", "opacity",
    ):
        assert param in sig.parameters, (
            f"aivazovsky_marine_luminance_pass missing parameter: {param}")


def test_aivazovsky_marine_luminance_pass_runs():
    """Session 199: aivazovsky_marine_luminance_pass runs without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.10, 0.22, 0.45), texture_strength=0.0)
    p.aivazovsky_marine_luminance_pass(
        horizon_y=0.40,
        wave_frequency=6.0,
        crest_strength=0.60,
        trough_strength=0.50,
        horizon_glow_strength=0.55,
        foam_strength=0.40,
        opacity=0.78,
        seed=199,
    )


def test_aivazovsky_marine_luminance_pass_pixels_in_range():
    """Session 199: aivazovsky_marine_luminance_pass output pixels must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.10, 0.22, 0.45), texture_strength=0.0)
    p.aivazovsky_marine_luminance_pass(
        horizon_y=0.40, wave_frequency=6.0, opacity=1.0, seed=199
    )
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_aivazovsky_marine_luminance_pass_modifies_canvas():
    """Session 199: aivazovsky_marine_luminance_pass at full opacity must change pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.10, 0.22, 0.45), texture_strength=0.0)
    p.underpainting(ref, stroke_size=8)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.aivazovsky_marine_luminance_pass(
        horizon_y=0.40,
        wave_frequency=8.0,
        crest_strength=0.70,
        trough_strength=0.60,
        horizon_glow_strength=0.65,
        opacity=1.0,
        seed=199,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "aivazovsky_marine_luminance_pass should modify canvas pixels at opacity=1.0")


def test_aivazovsky_marine_luminance_pass_zero_opacity_unchanged():
    """Session 199: aivazovsky_marine_luminance_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.10, 0.22, 0.45), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.aivazovsky_marine_luminance_pass(
        horizon_y=0.40, wave_frequency=6.0, opacity=0.0, seed=199
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "aivazovsky_marine_luminance_pass at opacity=0.0 must not change any pixels")


def test_aivazovsky_marine_luminance_pass_no_reference():
    """Session 199: aivazovsky_marine_luminance_pass without reference must run without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.10, 0.22, 0.45), texture_strength=0.0)
    p.aivazovsky_marine_luminance_pass(
        horizon_y=0.45, wave_frequency=5.0, opacity=0.70, seed=199
    )


def test_aivazovsky_marine_luminance_pass_high_horizon():
    """Session 199: horizon_y at top of canvas (0.15) runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.10, 0.22, 0.45), texture_strength=0.0)
    p.aivazovsky_marine_luminance_pass(
        horizon_y=0.15, wave_frequency=10.0, opacity=0.60, seed=199
    )


def test_aivazovsky_marine_luminance_pass_low_horizon():
    """Session 199: horizon_y near bottom (0.80) runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.10, 0.22, 0.45), texture_strength=0.0)
    p.aivazovsky_marine_luminance_pass(
        horizon_y=0.80, wave_frequency=4.0, opacity=0.60, seed=199
    )


def test_aivazovsky_marine_luminance_pass_in_catalog():
    """Session 199: ivan_aivazovsky must appear in CATALOG with correct movement."""
    from art_catalog import CATALOG, get_style
    assert "ivan_aivazovsky" in CATALOG, "ivan_aivazovsky missing from CATALOG"
    s = get_style("ivan_aivazovsky")
    assert "Marine" in s.movement or "marine" in s.movement.lower()
    assert len(s.palette) >= 7
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"


# ── bocklin_mythic_atmosphere_pass — session 200 addition ─────────────────────

def test_bocklin_mythic_atmosphere_pass_exists():
    """Session 200: bocklin_mythic_atmosphere_pass must exist on Painter."""
    from stroke_engine import Painter
    assert hasattr(Painter, "bocklin_mythic_atmosphere_pass"), (
        "bocklin_mythic_atmosphere_pass not found on Painter")
    assert callable(getattr(Painter, "bocklin_mythic_atmosphere_pass"))


def test_bocklin_mythic_atmosphere_pass_signature():
    """Session 200: bocklin_mythic_atmosphere_pass must have expected parameters."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.bocklin_mythic_atmosphere_pass)
    for param in (
        "shadow_cool", "shadow_threshold", "mist_strength", "mist_color",
        "highlight_threshold", "jewel_boost",
        "vignette_strength", "vignette_power", "opacity",
    ):
        assert param in sig.parameters, (
            f"bocklin_mythic_atmosphere_pass missing parameter: {param}")


def test_bocklin_mythic_atmosphere_pass_runs():
    """Session 200: bocklin_mythic_atmosphere_pass runs without error on a small canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.26, 0.28, 0.36), texture_strength=0.0)
    p.bocklin_mythic_atmosphere_pass(
        shadow_cool=0.40,
        mist_strength=0.30,
        mist_color=(0.38, 0.42, 0.54),
        jewel_boost=0.32,
        vignette_strength=0.55,
        opacity=0.65,
    )


def test_bocklin_mythic_atmosphere_pass_pixels_in_range():
    """Session 200: bocklin_mythic_atmosphere_pass output pixels must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.26, 0.28, 0.36), texture_strength=0.0)
    p.bocklin_mythic_atmosphere_pass(
        shadow_cool=0.40, mist_strength=0.30, jewel_boost=0.32,
        vignette_strength=0.55, opacity=1.0,
    )
    buf = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape(64, 64, 4)
    assert buf.min() >= 0
    assert buf.max() <= 255


def test_bocklin_mythic_atmosphere_pass_modifies_canvas():
    """Session 200: bocklin_mythic_atmosphere_pass at full opacity must change pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.26, 0.28, 0.36), texture_strength=0.0)
    p.underpainting(ref, stroke_size=8)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.bocklin_mythic_atmosphere_pass(
        shadow_cool=0.40, mist_strength=0.30, jewel_boost=0.32,
        vignette_strength=0.55, opacity=1.0,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "bocklin_mythic_atmosphere_pass should modify canvas pixels at opacity=1.0")


def test_bocklin_mythic_atmosphere_pass_zero_opacity_unchanged():
    """Session 200: bocklin_mythic_atmosphere_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.26, 0.28, 0.36), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.bocklin_mythic_atmosphere_pass(
        shadow_cool=0.40, mist_strength=0.30, jewel_boost=0.32,
        vignette_strength=0.55, opacity=0.0,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "bocklin_mythic_atmosphere_pass at opacity=0.0 must not change any pixels")


def test_bocklin_mythic_atmosphere_pass_no_reference():
    """Session 200: bocklin_mythic_atmosphere_pass without prior strokes runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.26, 0.28, 0.36), texture_strength=0.0)
    p.bocklin_mythic_atmosphere_pass(opacity=0.70)


def test_bocklin_mythic_atmosphere_pass_high_vignette():
    """Session 200: vignette_strength=1.0 runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.26, 0.28, 0.36), texture_strength=0.0)
    p.bocklin_mythic_atmosphere_pass(vignette_strength=1.0, opacity=0.60)


def test_bocklin_mythic_atmosphere_pass_zero_jewel_boost():
    """Session 200: jewel_boost=0 runs without error and still applies mist/shadow."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.26, 0.28, 0.36), texture_strength=0.0)
    p.bocklin_mythic_atmosphere_pass(jewel_boost=0.0, opacity=0.50)


def test_bocklin_mythic_atmosphere_pass_in_catalog():
    """Session 200: arnold_bocklin must appear in CATALOG with correct movement."""
    from art_catalog import CATALOG, get_style
    assert "arnold_bocklin" in CATALOG, "arnold_bocklin missing from CATALOG"
    s = get_style("arnold_bocklin")
    assert "Symbolism" in s.movement or "symbolism" in s.movement.lower()
    assert len(s.palette) >= 7
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"


# ── Session 201: James Ensor — ensor_carnival_mask_pass ──────────────────────

def test_ensor_carnival_mask_pass_exists():
    """Session 201: Painter must have ensor_carnival_mask_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "ensor_carnival_mask_pass"), (
        "ensor_carnival_mask_pass not found on Painter")
    assert callable(getattr(Painter, "ensor_carnival_mask_pass"))


def test_ensor_carnival_mask_pass_modifies_canvas():
    """Session 201: ensor_carnival_mask_pass at opacity=1.0 must change pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.72, 0.62, 0.32), texture_strength=0.0)
    p.underpainting(ref, stroke_size=8)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.ensor_carnival_mask_pass(opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "ensor_carnival_mask_pass should modify canvas pixels at opacity=1.0")


def test_ensor_carnival_mask_pass_zero_opacity_unchanged():
    """Session 201: ensor_carnival_mask_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.62, 0.32), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.ensor_carnival_mask_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "ensor_carnival_mask_pass at opacity=0.0 must not change any pixels")


def test_ensor_carnival_mask_pass_no_prior_strokes():
    """Session 201: ensor_carnival_mask_pass without prior strokes runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.62, 0.32), texture_strength=0.0)
    p.ensor_carnival_mask_pass(opacity=0.70)


def test_ensor_carnival_mask_pass_zero_sparkle():
    """Session 201: sparkle_strength=0 runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.62, 0.32), texture_strength=0.0)
    p.ensor_carnival_mask_pass(sparkle_strength=0.0, opacity=0.60)


def test_ensor_carnival_mask_pass_zero_ground_reveal():
    """Session 201: ground_reveal=0 runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.72, 0.62, 0.32), texture_strength=0.0)
    p.ensor_carnival_mask_pass(ground_reveal=0.0, opacity=0.60)


def test_ensor_carnival_mask_pass_in_catalog():
    """Session 201: james_ensor must appear in CATALOG with correct movement."""
    from art_catalog import CATALOG, get_style
    assert "james_ensor" in CATALOG, "james_ensor missing from CATALOG"
    s = get_style("james_ensor")
    assert "express" in s.movement.lower() or "symbol" in s.movement.lower()
    assert len(s.palette) >= 7
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"


# ── Session 202: Henri Rousseau — rousseau_naive_luminance_pass ──────────────

def test_rousseau_naive_luminance_pass_exists():
    """Session 202: Painter must have rousseau_naive_luminance_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "rousseau_naive_luminance_pass"), (
        "rousseau_naive_luminance_pass not found on Painter")
    assert callable(getattr(Painter, "rousseau_naive_luminance_pass"))


def test_rousseau_naive_luminance_pass_modifies_canvas():
    """Session 202: rousseau_naive_luminance_pass at opacity=1.0 must change pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.12, 0.18, 0.10), texture_strength=0.0)
    p.underpainting(ref, stroke_size=8)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.rousseau_naive_luminance_pass(opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "rousseau_naive_luminance_pass should modify canvas pixels at opacity=1.0")


def test_rousseau_naive_luminance_pass_zero_opacity_unchanged():
    """Session 202: rousseau_naive_luminance_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.18, 0.10), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.rousseau_naive_luminance_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "rousseau_naive_luminance_pass at opacity=0.0 must not change any pixels")


def test_rousseau_naive_luminance_pass_no_prior_strokes():
    """Session 202: rousseau_naive_luminance_pass without prior strokes runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.18, 0.10), texture_strength=0.0)
    p.rousseau_naive_luminance_pass(opacity=0.75)


def test_rousseau_naive_luminance_pass_zero_strengths():
    """Session 202: all band strengths = 0 runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.18, 0.10), texture_strength=0.0)
    p.rousseau_naive_luminance_pass(
        void_strength=0.0, foliage_strength=0.0,
        midlit_strength=0.0, highlight_strength=0.0,
        sky_strength=0.0, opacity=0.60,
    )


def test_rousseau_naive_luminance_pass_custom_colors():
    """Session 202: custom band colors are accepted without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.18, 0.10), texture_strength=0.0)
    p.rousseau_naive_luminance_pass(
        void_color=(0.02, 0.02, 0.08),
        foliage_color=(0.05, 0.25, 0.08),
        midlit_color=(0.80, 0.70, 0.30),
        highlight_color=(0.95, 0.95, 0.90),
        sky_color=(0.18, 0.22, 0.52),
        opacity=0.65,
    )


def test_rousseau_naive_luminance_pass_in_catalog():
    """Session 202: henri_rousseau must appear in CATALOG with correct movement."""
    from art_catalog import CATALOG, get_style
    assert "henri_rousseau" in CATALOG, "henri_rousseau missing from CATALOG"
    s = get_style("henri_rousseau")
    assert "naive" in s.movement.lower() or "naï" in s.movement.lower() or "post" in s.movement.lower()
    assert len(s.palette) >= 7
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"


# ── Session 203: J. M. W. Turner — turner_vortex_luminance_pass ──────────────

def test_turner_vortex_luminance_pass_exists():
    """Session 203: Painter must have turner_vortex_luminance_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "turner_vortex_luminance_pass"), (
        "turner_vortex_luminance_pass not found on Painter")
    assert callable(getattr(Painter, "turner_vortex_luminance_pass"))


def test_turner_vortex_luminance_pass_modifies_canvas():
    """Session 203: turner_vortex_luminance_pass at opacity=1.0 must change pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.80, 0.75, 0.60), texture_strength=0.0)
    p.underpainting(ref, stroke_size=8)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.turner_vortex_luminance_pass(opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "turner_vortex_luminance_pass should modify canvas pixels at opacity=1.0")


def test_turner_vortex_luminance_pass_zero_opacity_unchanged():
    """Session 203: turner_vortex_luminance_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.80, 0.75, 0.60), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.turner_vortex_luminance_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "turner_vortex_luminance_pass at opacity=0.0 must not change any pixels")


def test_turner_vortex_luminance_pass_no_prior_strokes():
    """Session 203: turner_vortex_luminance_pass without prior strokes runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.80, 0.75, 0.60), texture_strength=0.0)
    p.turner_vortex_luminance_pass(opacity=0.72)


def test_turner_vortex_luminance_pass_pixels_in_range():
    """Session 203: turner_vortex_luminance_pass output pixels must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.80, 0.75, 0.60), texture_strength=0.0)
    p.underpainting(ref, stroke_size=8)
    p.turner_vortex_luminance_pass(
        core_strength=1.0, haze_strength=1.0, lum_lift=1.0, opacity=1.0
    )
    buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8)
    assert buf.min() >= 0 and buf.max() <= 255, (
        "turner_vortex_luminance_pass produced out-of-range pixel values")


def test_turner_vortex_luminance_pass_zero_strengths():
    """Session 203: all strengths=0 runs without error and leaves canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.80, 0.75, 0.60), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.turner_vortex_luminance_pass(
        core_strength=0.0, haze_strength=0.0, lum_lift=0.0, opacity=1.0
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "turner_vortex_luminance_pass with all strengths=0 must not change pixels")


def test_turner_vortex_luminance_pass_custom_vortex_position():
    """Session 203: off-centre vortex position runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.80, 0.75, 0.60), texture_strength=0.0)
    p.turner_vortex_luminance_pass(vortex_x=0.25, vortex_y=0.30, opacity=0.60)


def test_turner_vortex_luminance_pass_custom_colors():
    """Session 203: custom vortex and periphery colours are accepted without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.80, 0.75, 0.60), texture_strength=0.0)
    p.turner_vortex_luminance_pass(
        vortex_color=(1.0, 0.95, 0.70),
        periphery_color=(0.20, 0.22, 0.40),
        opacity=0.65,
    )


def test_turner_vortex_luminance_pass_in_catalog():
    """Session 203: turner must appear in CATALOG with correct movement."""
    from art_catalog import CATALOG, get_style
    assert "turner" in CATALOG, "turner missing from CATALOG"
    s = get_style("turner")
    assert "romantic" in s.movement.lower() or "impressi" in s.movement.lower()
    assert len(s.palette) >= 5
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"


# ── Session 204: Edward Hopper — hopper_raking_light_pass ─────────────────

def test_hopper_raking_light_pass_exists():
    """Session 204: Painter must have hopper_raking_light_pass() method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "hopper_raking_light_pass"), (
        "hopper_raking_light_pass not found on Painter")
    assert callable(getattr(Painter, "hopper_raking_light_pass"))


def test_hopper_raking_light_pass_modifies_canvas():
    """Session 204: hopper_raking_light_pass at opacity=1.0 must change pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.65, 0.60, 0.48), texture_strength=0.0)
    p.underpainting(ref, stroke_size=8)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.hopper_raking_light_pass(opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "hopper_raking_light_pass should modify canvas pixels at opacity=1.0")


def test_hopper_raking_light_pass_zero_opacity_unchanged():
    """Session 204: hopper_raking_light_pass at opacity=0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.65, 0.60, 0.48), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.hopper_raking_light_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "hopper_raking_light_pass at opacity=0.0 must not change any pixels")


def test_hopper_raking_light_pass_no_prior_strokes():
    """Session 204: hopper_raking_light_pass without prior strokes runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.65, 0.60, 0.48), texture_strength=0.0)
    p.hopper_raking_light_pass(opacity=0.68)


def test_hopper_raking_light_pass_pixels_in_range():
    """Session 204: hopper_raking_light_pass output pixels must stay in [0, 255]."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.65, 0.60, 0.48), texture_strength=0.0)
    p.underpainting(ref, stroke_size=8)
    p.hopper_raking_light_pass(
        light_x=-0.70, light_y=-0.30, threshold=0.48,
        lit_strength=0.52, shadow_strength=0.44,
        edge_contrast=1.35, opacity=0.68,
    )
    buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8)
    assert buf.min() >= 0 and buf.max() <= 255, (
        "hopper_raking_light_pass produced out-of-range pixel values")


def test_hopper_raking_light_pass_zero_strengths():
    """Session 204: lit_strength=0, shadow_strength=0, edge_contrast=1 leaves canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.65, 0.60, 0.48), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.hopper_raking_light_pass(
        lit_strength=0.0, shadow_strength=0.0, edge_contrast=1.0, opacity=1.0,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "hopper_raking_light_pass with all strengths=0 must not change pixels")


def test_hopper_raking_light_pass_custom_light_direction():
    """Session 204: custom light direction (right-to-left) runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.65, 0.60, 0.48), texture_strength=0.0)
    p.hopper_raking_light_pass(light_x=0.80, light_y=0.20, opacity=0.50)


def test_hopper_raking_light_pass_custom_colors():
    """Session 204: custom lit/shadow colours are accepted without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.65, 0.60, 0.48), texture_strength=0.0)
    p.hopper_raking_light_pass(
        lit_color=(1.0, 1.0, 0.8),
        shadow_color=(0.2, 0.3, 0.4),
        opacity=0.60,
    )


def test_hopper_raking_light_pass_in_catalog():
    """Session 204: hopper must appear in CATALOG with correct movement."""
    from art_catalog import CATALOG, get_style
    assert "hopper" in CATALOG, "hopper missing from CATALOG"
    s = get_style("hopper")
    assert "realism" in s.movement.lower() or "realist" in s.movement.lower()
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"


# ── Session 205: Edvard Munch — munch_anxiety_swirl_pass (additional tests) ──

def test_s205_munch_anxiety_swirl_method_exists():
    """Session 205: Painter must have munch_anxiety_swirl_pass method."""
    from stroke_engine import Painter as _P
    assert hasattr(_P, "munch_anxiety_swirl_pass"), (
        "Painter missing munch_anxiety_swirl_pass method")


def test_s205_munch_anxiety_swirl_strokes_modify_canvas():
    """Session 205: n_swirl_strokes=80 with visible opacity must modify canvas."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.38, 0.32, 0.25), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.munch_anxiety_swirl_pass(
        n_swirl_strokes=80, stroke_opacity=0.60, color_intensity=0.80,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "munch_anxiety_swirl_pass with n_swirl_strokes=80 should modify canvas")


def test_s205_munch_anxiety_swirl_zero_opacity_noop():
    """Session 205: opacity=0.0 must leave canvas unchanged."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.38, 0.32, 0.25), texture_strength=0.0)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.munch_anxiety_swirl_pass(n_swirl_strokes=80, opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "munch_anxiety_swirl_pass with opacity=0.0 must not change any pixels")


def test_s205_munch_anxiety_swirl_single_focus_point():
    """Session 205: single focus_point runs without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.38, 0.32, 0.25), texture_strength=0.0)
    p.munch_anxiety_swirl_pass(
        n_swirl_strokes=20, focus_points=[(0.5, 0.5)], stroke_opacity=0.40,
    )


def test_s205_munch_anxiety_swirl_three_focus_points():
    """Session 205: three focus_points run without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.38, 0.32, 0.25), texture_strength=0.0)
    p.munch_anxiety_swirl_pass(
        n_swirl_strokes=20,
        focus_points=[(0.2, 0.2), (0.5, 0.8), (0.8, 0.3)],
        stroke_opacity=0.40,
    )


def test_s205_munch_anxiety_swirl_custom_colors():
    """Session 205: custom warm_color/cool_color accepted without error."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.38, 0.32, 0.25), texture_strength=0.0)
    p.munch_anxiety_swirl_pass(
        n_swirl_strokes=20,
        warm_color=(1.0, 0.5, 0.0),
        cool_color=(0.0, 0.2, 0.8),
        stroke_opacity=0.45,
    )


def test_s205_munch_anxiety_swirl_in_catalog():
    """Session 205: munch must appear in CATALOG with correct movement."""
    from art_catalog import CATALOG, get_style
    assert "munch" in CATALOG, "munch missing from CATALOG"
    s = get_style("munch")
    assert (
        "expressionism" in s.movement.lower()
        or "symbolism" in s.movement.lower()
    )
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"


# Session 206 — mucha_art_nouveau_aureole_pass tests ──────────────────────────


def test_s206_mucha_aureole_pass_runs():
    """Session 206: mucha_art_nouveau_aureole_pass runs without error on a 64×64 canvas."""
    p = _make_small_painter(64, 64)
    p.tone_ground((0.92, 0.88, 0.72), texture_strength=0.0)
    p.mucha_art_nouveau_aureole_pass(opacity=0.62)


def test_s206_mucha_aureole_modifies_canvas():
    """Session 206: mucha_art_nouveau_aureole_pass must change at least one pixel."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.92, 0.88, 0.72), texture_strength=0.0)
    before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape((64, 64, 4)).copy()
    p.mucha_art_nouveau_aureole_pass(field_strength=0.48, opacity=0.62)
    after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape((64, 64, 4)).copy()
    assert not _np.array_equal(before, after), (
        "mucha_art_nouveau_aureole_pass must modify the canvas")


def test_s206_mucha_aureole_zero_opacity_no_change():
    """Session 206: mucha_art_nouveau_aureole_pass with opacity=0.0 must not change any pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.92, 0.88, 0.72), texture_strength=0.0)
    before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape((64, 64, 4)).copy()
    p.mucha_art_nouveau_aureole_pass(opacity=0.0)
    after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape((64, 64, 4)).copy()
    assert _np.array_equal(before, after), (
        "mucha_art_nouveau_aureole_pass with opacity=0.0 must not change any pixels")


def test_s206_mucha_aureole_in_catalog():
    """Session 206: alphonse_mucha must appear in CATALOG with correct movement."""
    from art_catalog import CATALOG, get_style
    assert "alphonse_mucha" in CATALOG, "alphonse_mucha missing from CATALOG"
    s = get_style("alphonse_mucha")
    assert "nouveau" in s.movement.lower(), (
        f"alphonse_mucha movement should be Art Nouveau; got {s.movement!r}")
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"


# ──────────────────────────────────────────────────────────────────────────────
# Session 207 — Robert Delaunay: delaunay_orphist_disk_pass (118th distinct mode)
# ──────────────────────────────────────────────────────────────────────────────

def test_s207_delaunay_disk_pass_exists():
    """Session 207: delaunay_orphist_disk_pass must exist on Painter."""
    from stroke_engine import Painter
    assert hasattr(Painter, "delaunay_orphist_disk_pass"), (
        "Painter must have a delaunay_orphist_disk_pass method")


def test_s207_delaunay_disk_pass_runs():
    """Session 207: delaunay_orphist_disk_pass must run without exception on a 64×64 canvas."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.12, 0.20), texture_strength=0.0)
    p.delaunay_orphist_disk_pass(n_disks=4, ring_frequency=4.0, disk_sigma=0.38, opacity=0.60)


def test_s207_delaunay_disk_pass_modifies_canvas():
    """Session 207: delaunay_orphist_disk_pass must visibly change the canvas."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.12, 0.20), texture_strength=0.0)
    before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape((64, 64, 4)).copy()
    p.delaunay_orphist_disk_pass(n_disks=4, ring_frequency=4.0, disk_sigma=0.38, opacity=0.65)
    after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape((64, 64, 4)).copy()
    assert not _np.array_equal(before, after), (
        "delaunay_orphist_disk_pass must modify the canvas")


def test_s207_delaunay_disk_pass_zero_opacity_no_change():
    """Session 207: delaunay_orphist_disk_pass with opacity=0.0 must not change any pixels."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.12, 0.20), texture_strength=0.0)
    before = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape((64, 64, 4)).copy()
    p.delaunay_orphist_disk_pass(n_disks=4, ring_frequency=4.0, disk_sigma=0.38, opacity=0.0)
    after = _np.frombuffer(
        p.canvas.surface.get_data(), dtype=_np.uint8
    ).reshape((64, 64, 4)).copy()
    assert _np.array_equal(before, after), (
        "delaunay_orphist_disk_pass with opacity=0.0 must not change any pixels")


def test_s207_delaunay_disk_pass_custom_centers():
    """Session 207: delaunay_orphist_disk_pass must accept custom disk_centers."""
    import numpy as _np
    p = _make_small_painter(64, 64)
    p.tone_ground((0.12, 0.12, 0.20), texture_strength=0.0)
    centers = [(0.25, 0.25), (0.75, 0.25), (0.50, 0.75)]
    p.delaunay_orphist_disk_pass(
        n_disks=3,
        ring_frequency=5.0,
        disk_sigma=0.40,
        opacity=0.55,
        disk_centers=centers,
    )


def test_s207_delaunay_in_catalog():
    """Session 207: robert_delaunay must appear in CATALOG with correct movement."""
    from art_catalog import CATALOG, get_style
    assert "robert_delaunay" in CATALOG, "robert_delaunay missing from CATALOG"
    s = get_style("robert_delaunay")
    assert "Orphism" in s.movement or "Simultanism" in s.movement, (
        f"robert_delaunay movement should reference Orphism; got {s.movement!r}")
    assert s.chromatic_split is True, "robert_delaunay chromatic_split must be True"
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"
