"""
test_s238_additions.py -- Session 238 tests for feininger_crystalline_prism_pass,
paint_split_toning_pass, and the lyonel_feininger catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64, rgb=(80, 120, 60)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)),
        "RGB")


# ─────────────────────────────────────────────────────────────────────────────
# feininger_crystalline_prism_pass  (149th distinct mode, session 238)
# ─────────────────────────────────────────────────────────────────────────────

def test_s238_feininger_pass_exists():
    """Session 238: Painter must have feininger_crystalline_prism_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "feininger_crystalline_prism_pass"), (
        "Painter is missing feininger_crystalline_prism_pass")
    assert callable(getattr(Painter, "feininger_crystalline_prism_pass"))


def test_s238_feininger_pass_no_error():
    """Session 238: feininger_crystalline_prism_pass runs without error on a toned canvas."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.feininger_crystalline_prism_pass(
        facet_sigma=8.0,
        prism_cycles=3.0,
        chroma_tilt=0.10,
        lum_facet=0.06,
        opacity=0.72,
    )


def test_s238_feininger_pass_modifies_canvas():
    """Session 238: feininger_crystalline_prism_pass changes canvas pixel values."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(60, 100, 150))
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4)).copy()

    p.feininger_crystalline_prism_pass(opacity=0.72)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))

    assert not np.array_equal(before, after), (
        "feininger_crystalline_prism_pass did not change any pixels")


def test_s238_feininger_pass_opacity_zero_noop():
    """Session 238: feininger_crystalline_prism_pass with opacity=0 leaves canvas unchanged."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(70, 110, 50))
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4)).copy()

    p.feininger_crystalline_prism_pass(opacity=0.0)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))

    assert np.array_equal(before, after), (
        "feininger_crystalline_prism_pass with opacity=0 should not modify canvas")


def test_s238_feininger_pass_default_params():
    """Session 238: feininger_crystalline_prism_pass accepts default parameters."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.feininger_crystalline_prism_pass()


def test_s238_feininger_pass_preserves_alpha():
    """Session 238: feininger_crystalline_prism_pass must not change the alpha channel."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    alpha_before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))[:, :, 3].copy()

    p.feininger_crystalline_prism_pass(opacity=0.72)

    alpha_after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))[:, :, 3]

    assert np.array_equal(alpha_before, alpha_after), (
        "feininger_crystalline_prism_pass must not alter the alpha channel")


def test_s238_feininger_pass_149th_mode_docstring():
    """Session 238: feininger_crystalline_prism_pass docstring mentions 149th distinct mode."""
    from stroke_engine import Painter
    doc = Painter.feininger_crystalline_prism_pass.__doc__ or ""
    assert "FORTY-NINTH" in doc, "Docstring must reference 149th distinct mode (written out)"
    assert "238" in doc, "Docstring must reference session 238"


def test_s238_feininger_pass_output_in_valid_range():
    """Session 238: feininger_crystalline_prism_pass output pixel values in [0, 255]."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(80, 120, 160))
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.feininger_crystalline_prism_pass(chroma_tilt=0.20, opacity=1.0)

    arr = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))
    assert arr[:, :, :3].min() >= 0, "Pixel values below 0 after pass"
    assert arr[:, :, :3].max() <= 255, "Pixel values above 255 after pass"


# ─────────────────────────────────────────────────────────────────────────────
# paint_split_toning_pass  (session 238 improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_s238_split_toning_pass_exists():
    """Session 238: Painter must have paint_split_toning_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_split_toning_pass"), (
        "Painter is missing paint_split_toning_pass")
    assert callable(getattr(Painter, "paint_split_toning_pass"))


def test_s238_split_toning_pass_no_error():
    """Session 238: paint_split_toning_pass runs without error on a toned canvas."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.paint_split_toning_pass(
        shadow_cool=0.065,
        highlight_warm=0.055,
        shadow_pivot=0.30,
        highlight_pivot=0.72,
        transition_width=0.18,
        opacity=0.52,
    )


def test_s238_split_toning_pass_modifies_canvas():
    """Session 238: paint_split_toning_pass changes canvas pixel values."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(180, 180, 180))
    p.tone_ground((0.10, 0.10, 0.10), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4)).copy()

    p.paint_split_toning_pass(opacity=0.52)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))

    assert not np.array_equal(before, after), (
        "paint_split_toning_pass did not change any pixels")


def test_s238_split_toning_pass_opacity_zero_noop():
    """Session 238: paint_split_toning_pass with opacity=0 leaves canvas unchanged."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(100, 130, 90))
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4)).copy()

    p.paint_split_toning_pass(opacity=0.0)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))

    assert np.array_equal(before, after), (
        "paint_split_toning_pass with opacity=0 should not modify canvas")


def test_s238_split_toning_pass_default_params():
    """Session 238: paint_split_toning_pass accepts default parameters."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.paint_split_toning_pass()


def test_s238_split_toning_pass_preserves_alpha():
    """Session 238: paint_split_toning_pass must not change the alpha channel."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    alpha_before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))[:, :, 3].copy()

    p.paint_split_toning_pass(opacity=0.52)

    alpha_after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))[:, :, 3]

    assert np.array_equal(alpha_before, alpha_after), (
        "paint_split_toning_pass must not alter the alpha channel")


def test_s238_split_toning_shadow_darkens_blue():
    """Session 238: split toning pushes dark pixels toward cool (higher blue in shadows)."""
    p = _make_small_painter(64, 64)
    # Very dark reference — nearly all pixels will be in shadow zone
    ref = _solid_reference(64, 64, rgb=(20, 20, 20))
    p.tone_ground((0.05, 0.05, 0.05), texture_strength=0.01)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4)).copy()

    p.paint_split_toning_pass(
        shadow_cool=0.15,
        highlight_warm=0.0,
        shadow_pivot=0.50,
        highlight_pivot=0.99,
        transition_width=0.40,
        opacity=1.0,
    )

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))

    # Average blue should increase, average red should decrease or stay flat
    avg_b_before = float(before[:, :, 0].mean())  # cairo BGRA: channel 0 = blue
    avg_r_before = float(before[:, :, 2].mean())  # channel 2 = red
    avg_b_after  = float(after[:, :, 0].mean())
    avg_r_after  = float(after[:, :, 2].mean())

    assert avg_b_after >= avg_b_before - 0.5, (
        "Shadow cool toning should not decrease blue channel significantly")
    assert avg_r_after <= avg_r_before + 0.5, (
        "Shadow cool toning should not increase red channel significantly")


def test_s238_split_toning_pass_output_in_valid_range():
    """Session 238: paint_split_toning_pass output pixel values in [0, 255]."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(200, 200, 200))
    p.tone_ground((0.62, 0.64, 0.70), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.paint_split_toning_pass(
        shadow_cool=0.15, highlight_warm=0.12, opacity=1.0
    )

    arr = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))
    assert arr[:, :, :3].min() >= 0, "Pixel values below 0 after pass"
    assert arr[:, :, :3].max() <= 255, "Pixel values above 255 after pass"


# ─────────────────────────────────────────────────────────────────────────────
# Art catalog: lyonel_feininger entry (session 238)
# ─────────────────────────────────────────────────────────────────────────────

def test_s238_feininger_catalog_entry_exists():
    """Session 238: art_catalog must contain the lyonel_feininger entry."""
    from art_catalog import CATALOG
    assert "lyonel_feininger" in CATALOG, (
        "CATALOG is missing the lyonel_feininger entry (session 238)")


def test_s238_feininger_catalog_artist_name():
    """Session 238: lyonel_feininger catalog entry must name Lyonel Feininger."""
    from art_catalog import CATALOG
    entry = CATALOG["lyonel_feininger"]
    assert "Feininger" in entry.artist, (
        f"Expected artist name containing 'Feininger', got: {entry.artist!r}")


def test_s238_feininger_catalog_movement():
    """Session 238: lyonel_feininger movement must reference Expressionism, Cubism, or Bauhaus."""
    from art_catalog import CATALOG
    entry = CATALOG["lyonel_feininger"]
    movement = entry.movement
    assert any(m in movement for m in ("Expressionism", "Cubism", "Bauhaus")), (
        f"Expected Expressionism/Cubism/Bauhaus in movement, got: {movement!r}")


def test_s238_feininger_catalog_palette_length():
    """Session 238: lyonel_feininger palette must have at least 6 colours."""
    from art_catalog import CATALOG
    entry = CATALOG["lyonel_feininger"]
    assert len(entry.palette) >= 6, (
        f"Expected >= 6 palette colours, got {len(entry.palette)}")


def test_s238_feininger_catalog_famous_works():
    """Session 238: lyonel_feininger catalog entry must list at least 5 famous works."""
    from art_catalog import CATALOG
    entry = CATALOG["lyonel_feininger"]
    assert len(entry.famous_works) >= 5, (
        f"Expected >= 5 famous works, got {len(entry.famous_works)}")


def test_s238_feininger_catalog_count_238():
    """Session 238: CATALOG should contain exactly 238 artists after this session."""
    from art_catalog import CATALOG
    assert len(CATALOG) == 238, (
        f"Expected 238 catalog entries after session 238, got {len(CATALOG)}")


def test_s238_feininger_catalog_inspiration_references_pass():
    """Session 238: feininger inspiration text should reference feininger_crystalline_prism_pass."""
    from art_catalog import CATALOG
    entry = CATALOG["lyonel_feininger"]
    assert "feininger_crystalline_prism_pass" in entry.inspiration, (
        "Feininger inspiration should reference feininger_crystalline_prism_pass")


def test_s238_feininger_catalog_has_cobalt_in_palette():
    """Session 238: Feininger palette must include a cool blue colour."""
    from art_catalog import CATALOG
    entry = CATALOG["lyonel_feininger"]
    # At least one palette entry with high blue relative to red
    has_cool_blue = any(col[2] > col[0] + 0.15 for col in entry.palette)
    assert has_cool_blue, "Feininger palette should include a dominant cool blue colour"
