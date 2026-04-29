"""
test_s240_additions.py -- Session 240 tests for dufy_chromatic_dissociation_pass,
paint_sfumato_focus_pass, and the raoul_dufy catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w: int = 64, h: int = 64):
    from stroke_engine import Painter
    return Painter(w, h)


def _solid_reference(w: int = 64, h: int = 64, rgb=(120, 160, 200)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)),
        "RGB")


def _gradient_reference(w: int = 64, h: int = 64):
    """Reference with a strong tonal gradient to exercise edge detection."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [220, 180, 120]   # warm left half
    arr[:, w // 2:, :] = [40, 80, 140]     # cool right half
    return Image.fromarray(arr, "RGB")


# ─────────────────────────────────────────────────────────────────────────────
# dufy_chromatic_dissociation_pass  (151st distinct mode, session 240)
# ─────────────────────────────────────────────────────────────────────────────

def test_s240_dufy_pass_exists():
    """Session 240: Painter must have dufy_chromatic_dissociation_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "dufy_chromatic_dissociation_pass"), (
        "Painter is missing dufy_chromatic_dissociation_pass")
    assert callable(getattr(Painter, "dufy_chromatic_dissociation_pass"))


def test_s240_dufy_pass_no_error():
    """Session 240: dufy_chromatic_dissociation_pass runs without error."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(120, 180, 220))
    p.tone_ground((0.92, 0.92, 0.90), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.dufy_chromatic_dissociation_pass(
        outline_sigma=1.2,
        outline_threshold=0.18,
        outline_darkness=0.70,
        chroma_dx=7,
        chroma_dy=5,
        saturation_lift=0.26,
        opacity=0.80,
    )


def test_s240_dufy_pass_zero_opacity_no_change():
    """Session 240: dufy_chromatic_dissociation_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(120, 180, 220))
    p.tone_ground((0.92, 0.92, 0.90), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.dufy_chromatic_dissociation_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "dufy_chromatic_dissociation_pass at opacity=0.0 must not change any pixels")


def test_s240_dufy_pass_changes_canvas():
    """Session 240: dufy_chromatic_dissociation_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    ref = _gradient_reference(64, 64)
    p.tone_ground((0.92, 0.92, 0.90), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.dufy_chromatic_dissociation_pass(
        outline_sigma=1.0,
        outline_darkness=0.80,
        chroma_dx=8,
        chroma_dy=6,
        saturation_lift=0.30,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "dufy_chromatic_dissociation_pass must change a non-uniform canvas"


def test_s240_dufy_outline_darkens_edges():
    """Session 240: outline stage must darken high-contrast edge pixels."""
    p   = _make_small_painter(64, 64)
    ref = _gradient_reference(64, 64)  # strong edge at x=32
    p.tone_ground((0.92, 0.92, 0.90), texture_strength=0.00)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    # Run with high darkness and zero chroma shift / saturation so only stage 1 acts
    p.dufy_chromatic_dissociation_pass(
        outline_sigma=0.8,
        outline_threshold=0.05,
        outline_darkness=0.90,
        chroma_dx=0,
        chroma_dy=0,
        saturation_lift=0.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    # Edge column (around x=32) should be darker after the pass
    before_edge_lum = before[:, 30:34, :3].mean()
    after_edge_lum  = after[:, 30:34, :3].mean()
    assert after_edge_lum < before_edge_lum, (
        "Outline darkening must reduce luminance at strong gradient edges "
        f"(before={before_edge_lum:.1f} after={after_edge_lum:.1f})")


def test_s240_dufy_chroma_shift_displaces_color():
    """Session 240: chrominance shift must produce different result from zero-shift."""
    p1 = _make_small_painter(64, 64)
    p2 = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(60, 150, 220))

    p1.tone_ground((0.92, 0.92, 0.90), texture_strength=0.00)
    p1.block_in(ref, stroke_size=8, n_strokes=30)
    p2.tone_ground((0.92, 0.92, 0.90), texture_strength=0.00)
    p2.block_in(ref, stroke_size=8, n_strokes=30)

    p1.dufy_chromatic_dissociation_pass(chroma_dx=0, chroma_dy=0, outline_darkness=0.0,
                                         saturation_lift=0.0, opacity=1.0)
    p2.dufy_chromatic_dissociation_pass(chroma_dx=10, chroma_dy=8, outline_darkness=0.0,
                                         saturation_lift=0.0, opacity=1.0)

    arr1 = np.frombuffer(p1.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    arr2 = np.frombuffer(p2.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    diff = np.abs(arr1.astype(np.int32) - arr2.astype(np.int32)).max()
    assert diff > 0, (
        "Chrominance shift (chroma_dx=10, chroma_dy=8) must produce "
        "a different result than zero shift")


def test_s240_dufy_saturation_lift_increases_saturation():
    """Session 240: saturation_lift > 0 must increase overall colour deviation from grey."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(80, 140, 200))
    p.tone_ground((0.92, 0.92, 0.90), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    bf = before[:, :, :3].astype(np.float32)
    lum_b = (0.299 * bf[:, :, 2] + 0.587 * bf[:, :, 1] + 0.114 * bf[:, :, 0])
    sat_before = np.abs(bf[:, :, 2] - lum_b).mean() + np.abs(bf[:, :, 1] - lum_b).mean()

    p.dufy_chromatic_dissociation_pass(
        outline_darkness=0.0,
        chroma_dx=0,
        chroma_dy=0,
        saturation_lift=0.50,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    af = after[:, :, :3].astype(np.float32)
    lum_a = (0.299 * af[:, :, 2] + 0.587 * af[:, :, 1] + 0.114 * af[:, :, 0])
    sat_after = np.abs(af[:, :, 2] - lum_a).mean() + np.abs(af[:, :, 1] - lum_a).mean()

    assert sat_after >= sat_before, (
        f"saturation_lift=0.5 must not decrease saturation "
        f"(before={sat_before:.3f} after={sat_after:.3f})")


# ─────────────────────────────────────────────────────────────────────────────
# paint_sfumato_focus_pass  (session 240 improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_s240_sfumato_pass_exists():
    """Session 240: Painter must have paint_sfumato_focus_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_sfumato_focus_pass"), (
        "Painter is missing paint_sfumato_focus_pass")
    assert callable(getattr(Painter, "paint_sfumato_focus_pass"))


def test_s240_sfumato_pass_no_error():
    """Session 240: paint_sfumato_focus_pass runs without error."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(140, 180, 220))
    p.tone_ground((0.92, 0.92, 0.90), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=20)
    p.paint_sfumato_focus_pass(
        cx=0.5, cy=0.5,
        focus_radius=0.22,
        max_sigma=4.0,
        sat_falloff=0.30,
        transition_k=6.0,
        opacity=0.70,
    )


def test_s240_sfumato_pass_zero_opacity_no_change():
    """Session 240: paint_sfumato_focus_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(140, 180, 220))
    p.tone_ground((0.92, 0.92, 0.90), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=20)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.paint_sfumato_focus_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "paint_sfumato_focus_pass at opacity=0.0 must not change any pixels")


def test_s240_sfumato_pass_changes_canvas():
    """Session 240: paint_sfumato_focus_pass must modify a non-uniform canvas."""
    p   = _make_small_painter(64, 64)
    ref = _gradient_reference(64, 64)
    p.tone_ground((0.92, 0.92, 0.90), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.paint_sfumato_focus_pass(
        cx=0.5, cy=0.5,
        focus_radius=0.10,
        max_sigma=6.0,
        sat_falloff=0.40,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "paint_sfumato_focus_pass must change a non-uniform canvas"


def test_s240_sfumato_periphery_softer_than_centre():
    """Session 240: periphery must be softer (lower local variance) than centre after sfumato."""
    p   = _make_small_painter(128, 128)
    # Use a reference with noise so variance is measurable
    rng = np.random.RandomState(42)
    arr = np.clip(rng.normal(128, 40, (128, 128, 3)), 0, 255).astype(np.uint8)
    from PIL import Image
    ref = Image.fromarray(arr, "RGB")
    p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.08)
    p.block_in(ref, stroke_size=8, n_strokes=60)

    p.paint_sfumato_focus_pass(
        cx=0.5, cy=0.5,
        focus_radius=0.12,
        max_sigma=8.0,
        sat_falloff=0.20,
        transition_k=8.0,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((128, 128, 4))
    grey = after[:, :, :3].mean(axis=2).astype(np.float32)

    # Centre 20x20 patch
    centre_var = float(grey[54:74, 54:74].var())
    # Corner patch (periphery)
    corner_var = float(grey[0:20, 0:20].var())

    assert corner_var <= centre_var + 5.0, (
        f"Periphery variance ({corner_var:.2f}) should not exceed centre "
        f"variance ({centre_var:.2f}) significantly — sfumato must soften periphery")


def test_s240_sfumato_different_focal_points_differ():
    """Session 240: different focal centres must produce different results."""
    p1 = _make_small_painter(64, 64)
    p2 = _make_small_painter(64, 64)
    ref = _gradient_reference(64, 64)

    for p in (p1, p2):
        p.tone_ground((0.92, 0.92, 0.90), texture_strength=0.02)
        p.block_in(ref, stroke_size=8, n_strokes=40)

    p1.paint_sfumato_focus_pass(cx=0.2, cy=0.2, focus_radius=0.15, max_sigma=5.0, opacity=1.0)
    p2.paint_sfumato_focus_pass(cx=0.8, cy=0.8, focus_radius=0.15, max_sigma=5.0, opacity=1.0)

    arr1 = np.frombuffer(p1.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    arr2 = np.frombuffer(p2.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    diff = np.abs(arr1.astype(np.int32) - arr2.astype(np.int32)).max()
    assert diff > 0, (
        "Different focal centres (0.2,0.2) vs (0.8,0.8) must produce different outputs")


# ─────────────────────────────────────────────────────────────────────────────
# raoul_dufy catalog entry  (session 240)
# ─────────────────────────────────────────────────────────────────────────────

def test_s240_dufy_in_catalog():
    """Session 240: CATALOG must contain 'raoul_dufy' with correct basic properties."""
    import art_catalog
    assert "raoul_dufy" in art_catalog.CATALOG, (
        "art_catalog.CATALOG must contain 'raoul_dufy'")
    s = art_catalog.CATALOG["raoul_dufy"]
    assert s.artist == "Raoul Dufy", f"artist should be 'Raoul Dufy', got {s.artist!r}"
    movement_lower = s.movement.lower()
    assert "fauv" in movement_lower or "post" in movement_lower, (
        f"movement should reference Fauvism or Post-Impressionism, got {s.movement!r}")


def test_s240_dufy_catalog_palette_has_blue():
    """Session 240: Dufy palette must include a distinctly blue entry (Mediterranean sea)."""
    import art_catalog
    palette = art_catalog.CATALOG["raoul_dufy"].palette
    assert len(palette) >= 6, f"palette should have >=6 entries, got {len(palette)}"
    # At least one entry should be distinctly blue: B > R + 0.20 and B > G - 0.10
    has_blue = any(
        (b > r + 0.20) and (b > g - 0.15)
        for r, g, b in palette
    )
    assert has_blue, (
        f"Dufy palette must include a blue entry; palette={palette}")


def test_s240_dufy_catalog_ground_is_light():
    """Session 240: Dufy ground_color must be light (near-white) — paper/canvas ground."""
    import art_catalog
    gc = art_catalog.CATALOG["raoul_dufy"].ground_color
    lum = 0.299 * gc[0] + 0.587 * gc[1] + 0.114 * gc[2]
    assert lum >= 0.80, (
        f"Dufy ground_color should be light (lum>=0.80 for near-white); got lum={lum:.3f}")


def test_s240_dufy_catalog_has_regatta_work():
    """Session 240: Dufy famous_works must include a regatta or Nice reference."""
    import art_catalog
    works = art_catalog.CATALOG["raoul_dufy"].famous_works
    assert len(works) >= 4, f"famous_works should have >= 4 entries, got {len(works)}"
    titles_lower = " ".join(t for t, _ in works).lower()
    assert "regatta" in titles_lower or "nice" in titles_lower or "cowes" in titles_lower, (
        f"famous_works should reference Regatta, Nice, or Cowes; titles={titles_lower!r}")


def test_s240_dufy_catalog_chromatic_split():
    """Session 240: Dufy catalog entry should have chromatic_split True (colour-line separation)."""
    import art_catalog
    s = art_catalog.CATALOG["raoul_dufy"]
    assert s.chromatic_split is True, (
        f"Dufy chromatic_split should be True (colour and line are dissociated); "
        f"got {s.chromatic_split!r}")


def test_s240_dufy_catalog_inspiration_mentions_mode():
    """Session 240: Dufy inspiration must mention the 151st mode."""
    import art_catalog
    insp = art_catalog.CATALOG["raoul_dufy"].inspiration.lower()
    assert "151" in insp or "fifty-first" in insp or "fifty first" in insp, (
        "Dufy inspiration text must mention the 151st distinct mode")
