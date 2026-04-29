"""
test_s237_additions.py -- Session 237 tests for rouault_stained_glass_pass,
paint_scumble_pass, and the georges_rouault catalog entry.
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
# rouault_stained_glass_pass  (148th distinct mode, session 237)
# ─────────────────────────────────────────────────────────────────────────────

def test_s237_rouault_pass_exists():
    """Session 237: Painter must have rouault_stained_glass_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "rouault_stained_glass_pass"), (
        "Painter is missing rouault_stained_glass_pass")
    assert callable(getattr(Painter, "rouault_stained_glass_pass"))


def test_s237_rouault_pass_no_error():
    """Session 237: rouault_stained_glass_pass runs without error on a toned canvas."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.rouault_stained_glass_pass(
        contour_thresh=0.18,
        contour_depth=0.72,
        contour_power=1.8,
        lead_cool=0.08,
        jewel_boost=0.55,
        opacity=0.82,
    )


def test_s237_rouault_pass_modifies_canvas():
    """Session 237: rouault_stained_glass_pass changes canvas pixel values."""
    import cairo
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(60, 100, 40))
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4)).copy()

    p.rouault_stained_glass_pass(opacity=0.82)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))

    assert not np.array_equal(before, after), (
        "rouault_stained_glass_pass did not change any pixels")


def test_s237_rouault_pass_opacity_zero_noop():
    """Session 237: rouault_stained_glass_pass with opacity=0 leaves canvas unchanged."""
    import cairo
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(70, 110, 50))
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4)).copy()

    p.rouault_stained_glass_pass(opacity=0.0)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))

    assert np.array_equal(before, after), (
        "rouault_stained_glass_pass with opacity=0 should not modify canvas")


def test_s237_rouault_pass_default_params():
    """Session 237: rouault_stained_glass_pass accepts default parameters."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.rouault_stained_glass_pass()   # default parameters should work


def test_s237_rouault_pass_preserves_alpha():
    """Session 237: rouault_stained_glass_pass must not change the alpha channel."""
    import cairo
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    alpha_before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))[:, :, 3].copy()

    p.rouault_stained_glass_pass(opacity=0.82)

    alpha_after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))[:, :, 3]

    assert np.array_equal(alpha_before, alpha_after), (
        "rouault_stained_glass_pass must not alter the alpha channel")


def test_s237_rouault_148th_mode_docstring():
    """Session 237: rouault_stained_glass_pass docstring mentions 148th distinct mode."""
    from stroke_engine import Painter
    doc = Painter.rouault_stained_glass_pass.__doc__ or ""
    # Convention: ordinals are written out (e.g. "ONE HUNDRED AND FORTY-EIGHTH")
    assert "FORTY-EIGHTH" in doc, "Docstring must reference 148th distinct mode (written out)"
    assert "237" in doc, "Docstring must reference session 237"


# ─────────────────────────────────────────────────────────────────────────────
# paint_scumble_pass  (session 237 improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_s237_scumble_pass_exists():
    """Session 237: Painter must have paint_scumble_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_scumble_pass"), (
        "Painter is missing paint_scumble_pass")
    assert callable(getattr(Painter, "paint_scumble_pass"))


def test_s237_scumble_pass_no_error():
    """Session 237: paint_scumble_pass runs without error on a toned canvas."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.paint_scumble_pass(
        bristle_sigma=0.75,
        bristle_thresh=0.60,
        scumble_lift=0.13,
        cool_tint=0.055,
        lum_gate_low=0.25,
        lum_gate_high=0.85,
        opacity=0.46,
        seed=237,
    )


def test_s237_scumble_pass_modifies_canvas():
    """Session 237: paint_scumble_pass changes canvas pixel values."""
    import cairo
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(120, 140, 100))
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4)).copy()

    p.paint_scumble_pass(opacity=0.46, seed=237)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))

    assert not np.array_equal(before, after), (
        "paint_scumble_pass did not change any pixels")


def test_s237_scumble_pass_opacity_zero_noop():
    """Session 237: paint_scumble_pass with opacity=0 leaves canvas unchanged."""
    import cairo
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(100, 130, 90))
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4)).copy()

    p.paint_scumble_pass(opacity=0.0, seed=237)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))

    assert np.array_equal(before, after), (
        "paint_scumble_pass with opacity=0 should not modify canvas")


def test_s237_scumble_pass_default_params():
    """Session 237: paint_scumble_pass accepts default parameters."""
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)
    p.paint_scumble_pass()


def test_s237_scumble_pass_preserves_alpha():
    """Session 237: paint_scumble_pass must not change the alpha channel."""
    import cairo
    p = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=20)

    alpha_before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))[:, :, 3].copy()

    p.paint_scumble_pass(opacity=0.46, seed=237)

    alpha_after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((64, 64, 4))[:, :, 3]

    assert np.array_equal(alpha_before, alpha_after), (
        "paint_scumble_pass must not alter the alpha channel")


def test_s237_scumble_pass_seed_reproducibility():
    """Session 237: paint_scumble_pass produces identical results with the same seed."""
    import cairo
    results = []
    for _ in range(2):
        p = _make_small_painter(64, 64)
        ref = _solid_reference(64, 64, rgb=(100, 130, 90))
        p.tone_ground((0.08, 0.06, 0.08), texture_strength=0.04)
        p.block_in(ref, stroke_size=8, n_strokes=20)
        p.paint_scumble_pass(opacity=0.46, seed=42)
        arr = np.frombuffer(
            p.canvas.surface.get_data(), dtype=np.uint8
        ).reshape((64, 64, 4)).copy()
        results.append(arr)
    assert np.array_equal(results[0], results[1]), (
        "paint_scumble_pass must be deterministic with the same seed")


# ─────────────────────────────────────────────────────────────────────────────
# Art catalog: georges_rouault entry (session 237)
# ─────────────────────────────────────────────────────────────────────────────

def test_s237_rouault_catalog_entry_exists():
    """Session 237: art_catalog must contain the georges_rouault entry."""
    from art_catalog import CATALOG
    assert "georges_rouault" in CATALOG, (
        "CATALOG is missing the georges_rouault entry (session 237)")


def test_s237_rouault_catalog_artist_name():
    """Session 237: georges_rouault catalog entry must name Georges Rouault."""
    from art_catalog import CATALOG
    entry = CATALOG["georges_rouault"]
    assert "Rouault" in entry.artist, (
        f"Expected artist name containing 'Rouault', got: {entry.artist!r}")


def test_s237_rouault_catalog_movement():
    """Session 237: georges_rouault movement must reference Expressionism or Fauvism."""
    from art_catalog import CATALOG
    entry = CATALOG["georges_rouault"]
    movement = entry.movement
    assert any(m in movement for m in ("Expressionism", "Fauvism")), (
        f"Expected Expressionism or Fauvism in movement, got: {movement!r}")


def test_s237_rouault_catalog_palette_length():
    """Session 237: georges_rouault palette must have at least 6 colours."""
    from art_catalog import CATALOG
    entry = CATALOG["georges_rouault"]
    assert len(entry.palette) >= 6, (
        f"Expected >= 6 palette colours, got {len(entry.palette)}")


def test_s237_rouault_catalog_has_near_black():
    """Session 237: Rouault palette must include a near-black contour colour."""
    from art_catalog import CATALOG
    entry = CATALOG["georges_rouault"]
    # At least one palette entry should be near-black (all channels < 0.15)
    has_dark = any(all(c < 0.15 for c in col) for col in entry.palette)
    assert has_dark, "Rouault palette should include a near-black contour colour"


def test_s237_rouault_catalog_famous_works():
    """Session 237: georges_rouault catalog entry must list at least 5 famous works."""
    from art_catalog import CATALOG
    entry = CATALOG["georges_rouault"]
    assert len(entry.famous_works) >= 5, (
        f"Expected >= 5 famous works, got {len(entry.famous_works)}")


def test_s237_rouault_catalog_count_237():
    """Session 237: CATALOG should contain exactly 237 artists after this session."""
    from art_catalog import CATALOG
    assert len(CATALOG) == 237, (
        f"Expected 237 catalog entries after session 237, got {len(CATALOG)}")


def test_s237_rouault_catalog_inspiration_references_pass():
    """Session 237: rouault inspiration text should reference rouault_stained_glass_pass."""
    from art_catalog import CATALOG
    entry = CATALOG["georges_rouault"]
    assert "rouault_stained_glass_pass" in entry.inspiration, (
        "Rouault inspiration should reference rouault_stained_glass_pass")
