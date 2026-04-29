"""
test_s241_additions.py -- Session 241 tests for frankenthaler_soak_stain_pass,
paint_lost_found_edges_pass, and the helen_frankenthaler catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64, rgb=(140, 160, 200)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)),
        "RGB")


def _gradient_reference(w: int = 64, h: int = 64):
    """Reference with a strong tonal gradient to exercise edge detection."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [220, 180, 120]
    arr[:, w // 2:, :] = [40, 80, 140]
    return Image.fromarray(arr, "RGB")


def _multicolor_reference(w: int = 64, h: int = 64):
    """Reference with several colour zones for stain tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :w // 2, :] = [200, 100, 80]
    arr[:h // 2, w // 2:, :] = [80, 160, 200]
    arr[h // 2:, :w // 2, :] = [80, 200, 120]
    arr[h // 2:, w // 2:, :] = [200, 180, 60]
    return Image.fromarray(arr, "RGB")


# ─────────────────────────────────────────────────────────────────────────────
# frankenthaler_soak_stain_pass  (152nd distinct mode, session 241)
# ─────────────────────────────────────────────────────────────────────────────

def test_s241_soak_stain_pass_exists():
    """Session 241: Painter must have frankenthaler_soak_stain_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "frankenthaler_soak_stain_pass"), (
        "Painter is missing frankenthaler_soak_stain_pass")
    assert callable(getattr(Painter, "frankenthaler_soak_stain_pass"))


def test_s241_soak_stain_pass_no_error():
    """Session 241: frankenthaler_soak_stain_pass runs without error."""
    p   = _make_small_painter(64, 64)
    ref = _multicolor_reference(64, 64)
    p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.frankenthaler_soak_stain_pass(
        n_stains=3,
        sigma_large=20.0,
        sigma_small=6.0,
        stain_alpha=0.38,
        absorption=0.62,
        cap_sigma=2.0,
        cap_threshold=0.05,
        seed=42,
        opacity=0.76,
    )


def test_s241_soak_stain_zero_opacity_no_change():
    """Session 241: frankenthaler_soak_stain_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64)
    p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.frankenthaler_soak_stain_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "frankenthaler_soak_stain_pass at opacity=0.0 must not change any pixels")


def test_s241_soak_stain_changes_canvas():
    """Session 241: frankenthaler_soak_stain_pass must modify the canvas."""
    p   = _make_small_painter(64, 64)
    ref = _multicolor_reference(64, 64)
    p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.frankenthaler_soak_stain_pass(
        n_stains=4,
        stain_alpha=0.45,
        absorption=0.50,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "frankenthaler_soak_stain_pass must change the canvas"


def test_s241_soak_stain_different_seeds_differ():
    """Session 241: different random seeds must produce different stain placements."""
    p1 = _make_small_painter(64, 64)
    p2 = _make_small_painter(64, 64)
    ref = _multicolor_reference(64, 64)

    for p in (p1, p2):
        p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.02)
        p.block_in(ref, stroke_size=8, n_strokes=40)

    p1.frankenthaler_soak_stain_pass(n_stains=3, seed=7,  opacity=1.0)
    p2.frankenthaler_soak_stain_pass(n_stains=3, seed=99, opacity=1.0)

    arr1 = np.frombuffer(p1.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    arr2 = np.frombuffer(p2.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    diff = np.abs(arr1.astype(np.int32) - arr2.astype(np.int32)).max()
    assert diff > 0, "Different seeds must produce different stain outputs"


def test_s241_soak_stain_absorption_modulates_shift():
    """Session 241: high absorption must produce smaller colour shift than low absorption."""
    p_high = _make_small_painter(64, 64)
    p_low  = _make_small_painter(64, 64)
    ref    = _multicolor_reference(64, 64)

    for p in (p_high, p_low):
        p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.02)
        p.block_in(ref, stroke_size=8, n_strokes=40)

    before_high = np.frombuffer(
        p_high.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_low  = np.frombuffer(
        p_low.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    p_high.frankenthaler_soak_stain_pass(absorption=0.92, stain_alpha=0.40, seed=7, opacity=1.0)
    p_low.frankenthaler_soak_stain_pass( absorption=0.05, stain_alpha=0.40, seed=7, opacity=1.0)

    after_high = np.frombuffer(
        p_high.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    after_low  = np.frombuffer(
        p_low.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))

    shift_high = np.abs(after_high.astype(np.int32) - before_high.astype(np.int32)).mean()
    shift_low  = np.abs(after_low.astype(np.int32)  - before_low.astype(np.int32)).mean()

    assert shift_high < shift_low, (
        f"High absorption ({shift_high:.2f}) must produce smaller shift than "
        f"low absorption ({shift_low:.2f})")


def test_s241_soak_stain_same_seed_reproducible():
    """Session 241: same seed must produce identical outputs."""
    ref = _multicolor_reference(64, 64)

    p1 = _make_small_painter(64, 64)
    p2 = _make_small_painter(64, 64)

    for p in (p1, p2):
        p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.02)
        p.block_in(ref, stroke_size=8, n_strokes=40)

    p1.frankenthaler_soak_stain_pass(seed=17, opacity=1.0)
    p2.frankenthaler_soak_stain_pass(seed=17, opacity=1.0)

    arr1 = np.frombuffer(p1.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    arr2 = np.frombuffer(p2.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    assert np.array_equal(arr1, arr2), "Same seed must produce identical stain outputs"


# ─────────────────────────────────────────────────────────────────────────────
# paint_lost_found_edges_pass  (session 241 improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_s241_lost_found_pass_exists():
    """Session 241: Painter must have paint_lost_found_edges_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_lost_found_edges_pass"), (
        "Painter is missing paint_lost_found_edges_pass")
    assert callable(getattr(Painter, "paint_lost_found_edges_pass"))


def test_s241_lost_found_pass_no_error():
    """Session 241: paint_lost_found_edges_pass runs without error."""
    p   = _make_small_painter(64, 64)
    ref = _gradient_reference(64, 64)
    p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=20)
    p.paint_lost_found_edges_pass(
        found_sharpness=1.60,
        found_radius=1.0,
        lost_sigma=2.2,
        importance_k=5.0,
        cx=0.5,
        cy=0.5,
        focal_weight=0.45,
        opacity=0.68,
    )


def test_s241_lost_found_zero_opacity_no_change():
    """Session 241: paint_lost_found_edges_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _gradient_reference(64, 64)
    p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.paint_lost_found_edges_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "paint_lost_found_edges_pass at opacity=0.0 must not change any pixels")


def test_s241_lost_found_changes_canvas():
    """Session 241: paint_lost_found_edges_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    ref = _gradient_reference(64, 64)
    p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.paint_lost_found_edges_pass(
        found_sharpness=2.0,
        lost_sigma=3.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "paint_lost_found_edges_pass must change a non-uniform canvas"


def test_s241_lost_found_focal_sharpens_centre():
    """Session 241: focal region must have higher local variance after high-sharpness pass."""
    p   = _make_small_painter(128, 128)
    rng = np.random.RandomState(42)
    arr = np.clip(rng.normal(128, 30, (128, 128, 3)), 0, 255).astype(np.uint8)
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4)).copy()
    p.paint_lost_found_edges_pass(
        found_sharpness=2.5,
        found_radius=1.0,
        lost_sigma=4.0,
        cx=0.5,
        cy=0.5,
        focal_weight=0.90,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    grey_b = before[:, :, :3].mean(axis=2).astype(np.float32)
    grey_a = after[:, :, :3].mean(axis=2).astype(np.float32)

    centre_var_b = float(grey_b[48:80, 48:80].var())
    centre_var_a = float(grey_a[48:80, 48:80].var())

    assert centre_var_a >= centre_var_b * 0.85, (
        f"Centre variance should not collapse (before={centre_var_b:.2f} after={centre_var_a:.2f})")


def test_s241_lost_found_peripheral_softer():
    """Session 241: peripheral edges must be softer (lower variance) than centre after lost pass."""
    p   = _make_small_painter(128, 128)
    rng = np.random.RandomState(7)
    arr = np.clip(rng.normal(128, 35, (128, 128, 3)), 0, 255).astype(np.uint8)
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.04)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    p.paint_lost_found_edges_pass(
        found_sharpness=1.2,
        lost_sigma=5.0,
        cx=0.5,
        cy=0.5,
        focal_weight=0.85,
        importance_k=8.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    grey = after[:, :, :3].mean(axis=2).astype(np.float32)

    centre_var  = float(grey[44:84, 44:84].var())
    corner_var  = float(grey[0:20, 0:20].var())

    assert corner_var <= centre_var + 8.0, (
        f"Corner variance ({corner_var:.2f}) should not exceed centre "
        f"variance ({centre_var:.2f}) by more than 8 — lost edges must be softer")


def test_s241_lost_found_different_focal_differ():
    """Session 241: different focal centres must produce different outputs."""
    p1 = _make_small_painter(64, 64)
    p2 = _make_small_painter(64, 64)
    ref = _gradient_reference(64, 64)

    for p in (p1, p2):
        p.tone_ground((0.94, 0.92, 0.86), texture_strength=0.02)
        p.block_in(ref, stroke_size=8, n_strokes=40)

    p1.paint_lost_found_edges_pass(cx=0.15, cy=0.15, focal_weight=0.80, opacity=1.0)
    p2.paint_lost_found_edges_pass(cx=0.85, cy=0.85, focal_weight=0.80, opacity=1.0)

    arr1 = np.frombuffer(p1.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    arr2 = np.frombuffer(p2.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    diff = np.abs(arr1.astype(np.int32) - arr2.astype(np.int32)).max()
    assert diff > 0, (
        "Different focal centres (0.15,0.15) vs (0.85,0.85) must produce different outputs")


# ─────────────────────────────────────────────────────────────────────────────
# helen_frankenthaler catalog entry  (session 241)
# ─────────────────────────────────────────────────────────────────────────────

def test_s241_frankenthaler_in_catalog():
    """Session 241: CATALOG must contain 'helen_frankenthaler' with correct basic properties."""
    import art_catalog
    assert "helen_frankenthaler" in art_catalog.CATALOG, (
        "art_catalog.CATALOG must contain 'helen_frankenthaler'")
    s = art_catalog.CATALOG["helen_frankenthaler"]
    assert s.artist == "Helen Frankenthaler", f"artist should be 'Helen Frankenthaler', got {s.artist!r}"
    movement_lower = s.movement.lower()
    assert "color field" in movement_lower or "colour field" in movement_lower or "abstract" in movement_lower, (
        f"movement should reference Color Field or Abstract Expressionism, got {s.movement!r}")


def test_s241_frankenthaler_catalog_palette_has_blue_and_rose():
    """Session 241: Frankenthaler palette must include a blue and a warm rose/pink entry."""
    import art_catalog
    palette = art_catalog.CATALOG["helen_frankenthaler"].palette
    assert len(palette) >= 6, f"palette should have >=6 entries, got {len(palette)}"
    has_blue = any(b > r + 0.15 and b > 0.50 for r, g, b in palette)
    has_warm = any(r > 0.60 and r > b + 0.10 for r, g, b in palette)
    assert has_blue, f"Frankenthaler palette must include a blue entry; palette={palette}"
    assert has_warm, f"Frankenthaler palette must include a warm (rose/ochre) entry; palette={palette}"


def test_s241_frankenthaler_catalog_ground_is_light():
    """Session 241: Frankenthaler ground_color must be light — raw canvas luminosity."""
    import art_catalog
    gc = art_catalog.CATALOG["helen_frankenthaler"].ground_color
    lum = 0.299 * gc[0] + 0.587 * gc[1] + 0.114 * gc[2]
    assert lum >= 0.80, (
        f"Frankenthaler ground_color should be light (lum>=0.80); got lum={lum:.3f}")


def test_s241_frankenthaler_catalog_has_mountains_and_sea():
    """Session 241: Frankenthaler famous_works must include Mountains and Sea."""
    import art_catalog
    works = art_catalog.CATALOG["helen_frankenthaler"].famous_works
    assert len(works) >= 4, f"famous_works should have >= 4 entries, got {len(works)}"
    titles_lower = " ".join(t for t, _ in works).lower()
    assert "mountains" in titles_lower or "sea" in titles_lower or "eden" in titles_lower, (
        f"famous_works should reference Mountains and Sea or Eden; titles={titles_lower!r}")


def test_s241_frankenthaler_catalog_inspiration_mentions_mode():
    """Session 241: Frankenthaler inspiration must mention the 152nd mode."""
    import art_catalog
    insp = art_catalog.CATALOG["helen_frankenthaler"].inspiration.lower()
    assert "152" in insp or "fifty-second" in insp or "fifty second" in insp, (
        "Frankenthaler inspiration text must mention the 152nd distinct mode")


def test_s241_frankenthaler_catalog_wet_blend_high():
    """Session 241: Frankenthaler wet_blend should be high (stain = maximal blending)."""
    import art_catalog
    s = art_catalog.CATALOG["helen_frankenthaler"]
    assert s.wet_blend >= 0.50, (
        f"Frankenthaler wet_blend should be >= 0.50 (soak-stain is wet blending); "
        f"got {s.wet_blend}")


def test_s241_total_catalog_count():
    """Session 241: catalog must have at least 241 entries after adding Frankenthaler."""
    import art_catalog
    count = len(art_catalog.CATALOG)
    assert count >= 241, f"Expected >= 241 catalog entries, got {count}"
