"""
test_s239_additions.py -- Session 239 tests for dix_neue_sachlichkeit_pass,
paint_glaze_gradient_pass, and the otto_dix catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64, rgb=(150, 120, 90)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)),
        "RGB")


# ─────────────────────────────────────────────────────────────────────────────
# dix_neue_sachlichkeit_pass  (150th distinct mode, session 239)
# ─────────────────────────────────────────────────────────────────────────────

def test_s239_dix_pass_exists():
    """Session 239: Painter must have dix_neue_sachlichkeit_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "dix_neue_sachlichkeit_pass"), (
        "Painter is missing dix_neue_sachlichkeit_pass")
    assert callable(getattr(Painter, "dix_neue_sachlichkeit_pass"))


def test_s239_dix_pass_no_error():
    """Session 239: dix_neue_sachlichkeit_pass runs without error on a toned canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(150, 120, 90))
    p.tone_ground((0.78, 0.70, 0.58), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.dix_neue_sachlichkeit_pass(
        compress_strength=0.42,
        midtone_gamma=1.8,
        surge_lo=0.28,
        surge_hi=0.66,
        saturation_surge=0.36,
        hi_thresh=0.80,
        hi_power=1.6,
        hi_crispness=0.52,
        opacity=0.78,
    )


def test_s239_dix_pass_zero_opacity_no_change():
    """Session 239: dix_neue_sachlichkeit_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(150, 120, 90))
    p.tone_ground((0.78, 0.70, 0.58), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.dix_neue_sachlichkeit_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "dix_neue_sachlichkeit_pass at opacity=0.0 must not change any pixels")


def test_s239_dix_pass_changes_canvas():
    """Session 239: dix_neue_sachlichkeit_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:32, :, :] = [200, 160, 120]
    arr[32:, :, :] = [40, 30, 20]
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.60, 0.55, 0.45), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.dix_neue_sachlichkeit_pass(
        compress_strength=0.60,
        saturation_surge=0.50,
        hi_crispness=0.60,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "dix_neue_sachlichkeit_pass must change a non-uniform canvas"


def test_s239_dix_compress_pushes_light_up_dark_down():
    """Session 239: midtone compression must brighten light pixels and darken dark ones."""
    p = _make_small_painter(64, 64)
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:32, :, :] = [180, 144, 108]   # mid-light region (lum ~ 0.58)
    arr[32:, :, :] = [76, 60, 44]      # mid-dark region (lum ~ 0.24)
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.55, 0.50, 0.42), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_top = float(before[:32, :, :3].mean())
    before_bot = float(before[32:, :, :3].mean())

    p.dix_neue_sachlichkeit_pass(
        compress_strength=0.70,
        midtone_gamma=1.5,
        saturation_surge=0.0,
        hi_crispness=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_top = float(after[:32, :, :3].mean())
    after_bot = float(after[32:, :, :3].mean())

    assert after_top >= before_top, (
        f"Light midtones should be brighter after compression; "
        f"before={before_top:.1f} after={after_top:.1f}")
    assert after_bot <= before_bot, (
        f"Dark midtones should be darker after compression; "
        f"before={before_bot:.1f} after={after_bot:.1f}")


def test_s239_dix_highlight_crisping_brightens_highlights():
    """Session 239: hi_crispness must brighten the highest-luminance pixels."""
    p = _make_small_painter(64, 64)
    arr = np.full((64, 64, 3), 220, dtype=np.uint8)  # bright near-white canvas
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.85, 0.82, 0.78), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_mean = float(before[:, :, :3].mean())

    p.dix_neue_sachlichkeit_pass(
        compress_strength=0.0,
        saturation_surge=0.0,
        hi_thresh=0.70,
        hi_power=1.0,
        hi_crispness=0.70,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_mean = float(after[:, :, :3].mean())

    assert after_mean >= before_mean, (
        f"Highlight crisping must increase brightness on near-white canvas; "
        f"before={before_mean:.1f} after={after_mean:.1f}")


# ─────────────────────────────────────────────────────────────────────────────
# paint_glaze_gradient_pass  (session 239 artistic improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_s239_glaze_gradient_pass_exists():
    """Session 239: Painter must have paint_glaze_gradient_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_glaze_gradient_pass"), (
        "Painter is missing paint_glaze_gradient_pass")
    assert callable(getattr(Painter, "paint_glaze_gradient_pass"))


def test_s239_glaze_gradient_pass_no_error():
    """Session 239: paint_glaze_gradient_pass runs without error."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(180, 150, 110))
    p.tone_ground((0.65, 0.60, 0.50), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.paint_glaze_gradient_pass(
        color=(0.58, 0.32, 0.08),
        axis='y',
        opacity_near=0.0,
        opacity_far=0.12,
        gamma=1.5,
        reverse=True,
        blend_mode='multiply',
    )


def test_s239_glaze_gradient_zero_opacity_no_change():
    """Session 239: paint_glaze_gradient_pass at opacity_far=0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(180, 150, 110))
    p.tone_ground((0.65, 0.60, 0.50), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.paint_glaze_gradient_pass(opacity_near=0.0, opacity_far=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "paint_glaze_gradient_pass with opacity_far=0.0 must not change pixels")


def test_s239_glaze_gradient_changes_canvas():
    """Session 239: paint_glaze_gradient_pass must modify a non-trivial canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(200, 180, 140))
    p.tone_ground((0.70, 0.65, 0.55), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.paint_glaze_gradient_pass(
        color=(0.10, 0.40, 0.80),
        opacity_near=0.0,
        opacity_far=0.35,
        gamma=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "paint_glaze_gradient_pass must change the canvas"


def test_s239_glaze_gradient_y_axis_builds_toward_bottom():
    """Session 239: y-axis glaze must affect bottom rows more than top rows."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(220, 200, 160))
    p.tone_ground((0.80, 0.75, 0.62), texture_strength=0.0)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_top = before[:10, :, :3].astype(np.float32)
    before_bot = before[54:, :, :3].astype(np.float32)

    p.paint_glaze_gradient_pass(
        color=(0.10, 0.05, 0.80),   # strong blue glaze
        axis='y',
        opacity_near=0.0,
        opacity_far=0.50,
        gamma=1.0,
        reverse=False,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    after_top = after[:10,  :, :3].astype(np.float32)
    after_bot = after[54:,  :, :3].astype(np.float32)

    change_top = float(np.abs(after_top - before_top).mean())
    change_bot = float(np.abs(after_bot - before_bot).mean())

    assert change_bot > change_top, (
        f"y-axis glaze (reverse=False) must change bottom more than top; "
        f"change_top={change_top:.2f} change_bot={change_bot:.2f}")


def test_s239_glaze_gradient_reverse_flips_direction():
    """Session 239: reverse=True must flip which end of the canvas gets stronger glaze."""
    from PIL import Image
    arr = np.full((64, 64, 3), 200, dtype=np.uint8)
    ref = Image.fromarray(arr, "RGB")

    p1 = _make_small_painter(64, 64)
    p1.tone_ground((0.75, 0.70, 0.60))
    p1.block_in(ref, stroke_size=8, n_strokes=40)
    p1.paint_glaze_gradient_pass(color=(0.20, 0.60, 0.20), opacity_near=0.0,
                                  opacity_far=0.40, gamma=1.0, reverse=False)
    res_fwd = np.frombuffer(
        p1.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))[:, :, :3].copy()

    p2 = _make_small_painter(64, 64)
    p2.tone_ground((0.75, 0.70, 0.60))
    p2.block_in(ref, stroke_size=8, n_strokes=40)
    p2.paint_glaze_gradient_pass(color=(0.20, 0.60, 0.20), opacity_near=0.0,
                                  opacity_far=0.40, gamma=1.0, reverse=True)
    res_rev = np.frombuffer(
        p2.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))[:, :, :3].copy()

    change_fwd_top = float(np.abs(res_fwd[:10].astype(np.int32) - 200).mean())
    change_rev_top = float(np.abs(res_rev[:10].astype(np.int32) - 200).mean())
    assert change_rev_top > change_fwd_top, (
        "reverse=True should produce stronger glaze at top than reverse=False; "
        f"rev_top={change_rev_top:.2f} fwd_top={change_fwd_top:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# otto_dix catalog entry  (session 239)
# ─────────────────────────────────────────────────────────────────────────────

def test_s239_dix_in_catalog():
    """Session 239: otto_dix must appear in CATALOG with correct properties."""
    from art_catalog import CATALOG, get_style
    assert "otto_dix" in CATALOG, "otto_dix missing from CATALOG"
    s = get_style("otto_dix")
    mv = s.movement.lower()
    assert "objectiv" in mv or "express" in mv, (
        f"Dix movement unexpected: {s.movement!r}")
    assert s.chromatic_split is False
    assert s.crackle is False
    assert len(s.palette) >= 6
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range palette value: {ch}"
    assert len(s.famous_works) >= 4
    has_150 = "FIFTIETH" in s.inspiration or "150" in s.inspiration
    assert has_150, "otto_dix inspiration must reference 150th mode"


def test_s239_dix_catalog_palette_includes_dark_contour():
    """Session 239: Dix palette must include at least one near-black entry."""
    from art_catalog import get_style
    s = get_style("otto_dix")
    has_dark = any(max(rgb) < 0.22 for rgb in s.palette)
    assert has_dark, "Dix palette should include a near-black entry (max channel < 0.22)"


def test_s239_dix_catalog_includes_war_work():
    """Session 239: Dix famous_works must include Der Krieg or The War."""
    from art_catalog import get_style
    s = get_style("otto_dix")
    titles = [t.lower() for t, _ in s.famous_works]
    has_war = any("krieg" in t or "war" in t or "trench" in t for t in titles)
    assert has_war, "Dix famous_works should include Der Krieg, The War, or The Trench"


def test_s239_dix_catalog_ground_is_warm():
    """Session 239: Dix ground_color should be a warm mid-tone (plaster quality)."""
    from art_catalog import get_style
    s = get_style("otto_dix")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert 0.50 < lum < 0.90, f"Dix ground should be a warm mid-tone; lum={lum:.3f}"
    assert r > b, f"Dix ground should be warm (R > B); R={r:.2f} B={b:.2f}"
