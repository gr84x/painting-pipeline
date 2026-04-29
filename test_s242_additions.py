"""
test_s242_additions.py -- Session 242 tests for signac_divisionist_mosaic_pass,
paint_color_bloom_pass, and the paul_signac catalog entry.
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
    """Reference with a strong tonal gradient."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [220, 180, 120]
    arr[:, w // 2:, :] = [40, 80, 200]
    return Image.fromarray(arr, "RGB")


def _multicolor_reference(w: int = 64, h: int = 64):
    """Reference with vivid complementary colour zones for mosaic tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :w // 2, :] = [30, 100, 200]   # strong blue
    arr[:h // 2, w // 2:, :] = [220, 80, 30]    # vivid orange (complement)
    arr[h // 2:, :w // 2, :] = [40, 180, 80]    # vivid green
    arr[h // 2:, w // 2:, :] = [200, 40, 180]   # vivid violet (complement)
    return Image.fromarray(arr, "RGB")


def _saturated_reference(w: int = 64, h: int = 64):
    """Reference containing highly saturated regions for bloom tests."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Upper-left: vivid red (high saturation)
    arr[:h // 2, :w // 2, :] = [230, 20, 20]
    # Upper-right: vivid blue (high saturation)
    arr[:h // 2, w // 2:, :] = [20, 20, 230]
    # Lower half: near-grey (low saturation)
    arr[h // 2:, :, :] = [140, 140, 140]
    return Image.fromarray(arr, "RGB")


# ─────────────────────────────────────────────────────────────────────────────
# signac_divisionist_mosaic_pass  (153rd distinct mode, session 242)
# ─────────────────────────────────────────────────────────────────────────────

def test_s242_signac_pass_exists():
    """Session 242: Painter must have signac_divisionist_mosaic_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "signac_divisionist_mosaic_pass"), (
        "Painter is missing signac_divisionist_mosaic_pass")
    assert callable(getattr(Painter, "signac_divisionist_mosaic_pass"))


def test_s242_signac_pass_no_error():
    """Session 242: signac_divisionist_mosaic_pass runs without error."""
    p   = _make_small_painter(64, 64)
    ref = _multicolor_reference(64, 64)
    p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.signac_divisionist_mosaic_pass(
        patch_size=6,
        comp_mix=0.35,
        sat_boost=0.22,
        hue_thresh=80.0,
        blend_sigma=0.8,
        opacity=0.72,
    )


def test_s242_signac_zero_opacity_no_change():
    """Session 242: signac_divisionist_mosaic_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _multicolor_reference(64, 64)
    p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.signac_divisionist_mosaic_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "signac_divisionist_mosaic_pass at opacity=0.0 must not change any pixels")


def test_s242_signac_changes_canvas():
    """Session 242: signac_divisionist_mosaic_pass must modify a colourful canvas."""
    p   = _make_small_painter(64, 64)
    ref = _multicolor_reference(64, 64)
    p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.signac_divisionist_mosaic_pass(
        patch_size=4,
        comp_mix=0.40,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "signac_divisionist_mosaic_pass must change a colourful canvas"


def test_s242_signac_larger_patch_produces_coarser_mosaic():
    """Session 242: larger patch_size should produce more spatially uniform blocks."""
    p_fine  = _make_small_painter(64, 64)
    p_coarse = _make_small_painter(64, 64)
    ref = _multicolor_reference(64, 64)

    for p in (p_fine, p_coarse):
        p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
        p.block_in(ref, stroke_size=8, n_strokes=40)

    p_fine.signac_divisionist_mosaic_pass(patch_size=2, comp_mix=0.35, blend_sigma=0.0, opacity=1.0)
    p_coarse.signac_divisionist_mosaic_pass(patch_size=12, comp_mix=0.35, blend_sigma=0.0, opacity=1.0)

    arr_fine   = np.frombuffer(p_fine.canvas.surface.get_data(),   dtype=np.uint8).reshape((64, 64, 4))
    arr_coarse = np.frombuffer(p_coarse.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))

    # Coarser mosaic should have lower pixel-to-pixel variance (large uniform blocks)
    var_fine   = float(arr_fine[:, :, :3].astype(np.float32).var())
    var_coarse = float(arr_coarse[:, :, :3].astype(np.float32).var())
    assert var_coarse <= var_fine + 200.0, (
        f"Larger patch_size should produce lower or equal variance "
        f"(fine_var={var_fine:.1f}, coarse_var={var_coarse:.1f})")


def test_s242_signac_higher_comp_mix_changes_output():
    """Session 242: comp_mix > 0 vs comp_mix = 0 must produce different outputs."""
    p0 = _make_small_painter(64, 64)
    p1 = _make_small_painter(64, 64)
    ref = _multicolor_reference(64, 64)

    for p in (p0, p1):
        p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
        p.block_in(ref, stroke_size=8, n_strokes=40)

    p0.signac_divisionist_mosaic_pass(comp_mix=0.0, blend_sigma=0.0, opacity=1.0)
    p1.signac_divisionist_mosaic_pass(comp_mix=0.50, blend_sigma=0.0, opacity=1.0)

    arr0 = np.frombuffer(p0.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    arr1 = np.frombuffer(p1.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    diff = np.abs(arr0.astype(np.int32) - arr1.astype(np.int32)).max()
    assert diff > 0, "comp_mix=0.5 vs comp_mix=0.0 must produce different outputs"


def test_s242_signac_patch_size_1_runs():
    """Session 242: patch_size=1 (degenerate case) must not crash."""
    p   = _make_small_painter(32, 32)
    ref = _gradient_reference(32, 32)
    p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
    p.block_in(ref, stroke_size=6, n_strokes=20)
    # patch_size=1 means each pixel is its own patch; should not crash
    p.signac_divisionist_mosaic_pass(patch_size=1, opacity=0.5)


def test_s242_signac_output_in_valid_range():
    """Session 242: signac_divisionist_mosaic_pass must keep all pixel values in [0,255]."""
    p   = _make_small_painter(64, 64)
    ref = _multicolor_reference(64, 64)
    p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=40)
    p.signac_divisionist_mosaic_pass(sat_boost=0.50, comp_mix=0.50, opacity=1.0)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    assert after.min() >= 0 and after.max() <= 255, (
        f"Pixel values out of range: min={after.min()} max={after.max()}")


# ─────────────────────────────────────────────────────────────────────────────
# paint_color_bloom_pass  (session 242 improvement)
# ─────────────────────────────────────────────────────────────────────────────

def test_s242_bloom_pass_exists():
    """Session 242: Painter must have paint_color_bloom_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_color_bloom_pass"), (
        "Painter is missing paint_color_bloom_pass")
    assert callable(getattr(Painter, "paint_color_bloom_pass"))


def test_s242_bloom_pass_no_error():
    """Session 242: paint_color_bloom_pass runs without error."""
    p   = _make_small_painter(64, 64)
    ref = _saturated_reference(64, 64)
    p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)
    p.paint_color_bloom_pass(
        bloom_threshold=0.52,
        bloom_sigma=3.0,
        bloom_strength=0.28,
        chroma_shift=0.015,
        opacity=0.65,
    )


def test_s242_bloom_zero_opacity_no_change():
    """Session 242: paint_color_bloom_pass at opacity=0.0 must not change pixels."""
    p   = _make_small_painter(64, 64)
    ref = _saturated_reference(64, 64)
    p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.paint_color_bloom_pass(opacity=0.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    assert np.array_equal(before, after), (
        "paint_color_bloom_pass at opacity=0.0 must not change any pixels")


def test_s242_bloom_changes_canvas_on_saturated_input():
    """Session 242: paint_color_bloom_pass must modify a canvas with saturated colours."""
    p   = _make_small_painter(64, 64)
    ref = _saturated_reference(64, 64)
    p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=40)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.paint_color_bloom_pass(
        bloom_threshold=0.40,
        bloom_sigma=4.0,
        bloom_strength=0.50,
        opacity=1.0,
    )
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 0, "paint_color_bloom_pass must change a canvas with saturated colours"


def test_s242_bloom_no_effect_on_greyscale():
    """Session 242: paint_color_bloom_pass with high threshold must not change a greyscale canvas."""
    p   = _make_small_painter(64, 64)
    ref = _solid_reference(64, 64, rgb=(140, 140, 140))   # neutral grey
    p.tone_ground((0.55, 0.55, 0.55), texture_strength=0.00)
    p.block_in(ref, stroke_size=10, n_strokes=30)

    before = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    p.paint_color_bloom_pass(bloom_threshold=0.95, bloom_strength=0.50, opacity=1.0)
    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    # With saturation near 0 and threshold=0.95, bloom mask ≈ 0 everywhere
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).mean()
    assert diff < 5.0, (
        f"paint_color_bloom_pass should have negligible effect on near-greyscale canvas "
        f"with high threshold; mean diff={diff:.2f}")


def test_s242_bloom_stronger_on_more_saturated():
    """Session 242: lower bloom_threshold triggers effect on lower-saturation colours."""
    p_low  = _make_small_painter(64, 64)
    p_high = _make_small_painter(64, 64)
    ref = _saturated_reference(64, 64)

    for p in (p_low, p_high):
        p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
        p.block_in(ref, stroke_size=8, n_strokes=40)

    before_low  = np.frombuffer(p_low.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()
    before_high = np.frombuffer(p_high.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4)).copy()

    p_low.paint_color_bloom_pass( bloom_threshold=0.20, bloom_strength=0.40, opacity=1.0)
    p_high.paint_color_bloom_pass(bloom_threshold=0.90, bloom_strength=0.40, opacity=1.0)

    after_low  = np.frombuffer(p_low.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    after_high = np.frombuffer(p_high.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))

    diff_low  = np.abs(after_low.astype(np.int32)  - before_low.astype(np.int32)).mean()
    diff_high = np.abs(after_high.astype(np.int32) - before_high.astype(np.int32)).mean()

    assert diff_low > diff_high, (
        f"Lower bloom_threshold ({diff_low:.2f}) must produce larger change than "
        f"higher threshold ({diff_high:.2f})")


def test_s242_bloom_output_in_valid_range():
    """Session 242: paint_color_bloom_pass must keep all pixel values in [0,255]."""
    p   = _make_small_painter(64, 64)
    ref = _saturated_reference(64, 64)
    p.tone_ground((0.96, 0.96, 0.92), texture_strength=0.02)
    p.block_in(ref, stroke_size=8, n_strokes=40)
    p.paint_color_bloom_pass(bloom_threshold=0.10, bloom_strength=1.0, chroma_shift=0.10, opacity=1.0)

    after = np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8).reshape((64, 64, 4))
    assert after.min() >= 0 and after.max() <= 255, (
        f"Pixel values out of range: min={after.min()} max={after.max()}")


# ─────────────────────────────────────────────────────────────────────────────
# paul_signac catalog entry  (session 242)
# ─────────────────────────────────────────────────────────────────────────────

def test_s242_signac_in_catalog():
    """Session 242: CATALOG must contain 'paul_signac' with correct basic properties."""
    import art_catalog
    assert "paul_signac" in art_catalog.CATALOG, (
        "art_catalog.CATALOG must contain 'paul_signac'")
    s = art_catalog.CATALOG["paul_signac"]
    assert s.artist == "Paul Signac", f"artist should be 'Paul Signac', got {s.artist!r}"
    movement_lower = s.movement.lower()
    assert "neo-impressi" in movement_lower or "divisioni" in movement_lower, (
        f"movement should reference Neo-Impressionism or Divisionism, got {s.movement!r}")


def test_s242_signac_catalog_palette_has_blue_and_orange():
    """Session 242: Signac palette must include a deep blue and a vivid orange/warm entry."""
    import art_catalog
    palette = art_catalog.CATALOG["paul_signac"].palette
    assert len(palette) >= 6, f"palette should have >=6 entries, got {len(palette)}"
    has_blue   = any(b > r + 0.25 and b > 0.55 for r, g, b in palette)
    has_orange = any(r > 0.65 and r > b + 0.30 for r, g, b in palette)
    assert has_blue,   f"Signac palette must include a deep blue; palette={palette}"
    assert has_orange, f"Signac palette must include a vivid orange/warm; palette={palette}"


def test_s242_signac_catalog_chromatic_split_enabled():
    """Session 242: Signac chromatic_split must be True (divisionist complementary dots)."""
    import art_catalog
    s = art_catalog.CATALOG["paul_signac"]
    assert s.chromatic_split is True, (
        f"Signac chromatic_split should be True; got {s.chromatic_split}")


def test_s242_signac_catalog_low_wet_blend():
    """Session 242: Signac wet_blend must be low — divisionism uses no wet blending."""
    import art_catalog
    s = art_catalog.CATALOG["paul_signac"]
    assert s.wet_blend <= 0.15, (
        f"Signac wet_blend should be <=0.15 (pure juxtaposed strokes); got {s.wet_blend}")


def test_s242_signac_catalog_has_famous_works():
    """Session 242: Signac famous_works must include harbour/coastal titles."""
    import art_catalog
    works = art_catalog.CATALOG["paul_signac"].famous_works
    assert len(works) >= 4, f"famous_works should have >= 4 entries, got {len(works)}"
    titles_lower = " ".join(t for t, _ in works).lower()
    assert ("tropez" in titles_lower or "port" in titles_lower
            or "harbour" in titles_lower or "harbor" in titles_lower
            or "gas" in titles_lower or "venice" in titles_lower
            or "rotterdam" in titles_lower or "pont" in titles_lower), (
        f"famous_works should reference known Signac titles; titles={titles_lower!r}")


def test_s242_signac_catalog_inspiration_mentions_mode():
    """Session 242: Signac inspiration must mention the 153rd mode."""
    import art_catalog
    insp = art_catalog.CATALOG["paul_signac"].inspiration.lower()
    assert "153" in insp or "fifty-third" in insp or "fifty third" in insp, (
        "Signac inspiration text must mention the 153rd distinct mode")


def test_s242_signac_catalog_ground_is_light():
    """Session 242: Signac ground_color must be light — high-key divisionist ground."""
    import art_catalog
    gc = art_catalog.CATALOG["paul_signac"].ground_color
    lum = 0.299 * gc[0] + 0.587 * gc[1] + 0.114 * gc[2]
    assert lum >= 0.85, (
        f"Signac ground_color should be light (lum>=0.85); got lum={lum:.3f}")


def test_s242_total_catalog_count():
    """Session 242: catalog must have at least 242 entries after adding Signac."""
    import art_catalog
    count = len(art_catalog.CATALOG)
    assert count >= 242, f"Expected >= 242 catalog entries, got {count}"
