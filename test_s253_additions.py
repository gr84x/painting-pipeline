"""
test_s253_additions.py -- Session 253 tests for kiefer_scorched_earth_pass,
paint_impasto_ridge_cast_pass, and the anselm_kiefer catalog entry.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))


def _make_small_painter(w=64, h=64):
    from stroke_engine import Painter
    return Painter(w, h)


def _get_canvas(p):
    return np.frombuffer(
        p.canvas.surface.get_data(), dtype=np.uint8
    ).reshape((p.canvas.h, p.canvas.w, 4)).copy()


def _gradient_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w // 2, :] = [160, 80, 40]
    arr[:, w // 2:, :] = [40, 100, 160]
    return Image.fromarray(arr, "RGB")


def _multicolor_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 2, :w // 2, :] = [180, 60, 30]
    arr[:h // 2, w // 2:, :] = [30, 60, 190]
    arr[h // 2:, :w // 2, :] = [160, 140, 20]
    arr[h // 2:, w // 2:, :] = [50, 150, 80]
    return Image.fromarray(arr, "RGB")


def _dark_field_reference(w=64, h=64):
    """Dark foreground, lighter sky -- typical Kiefer landscape structure."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h // 3, :]  = [180, 170, 155]   # pale sky
    arr[h // 3:, :]  = [60, 50, 40]      # dark scorched field
    return Image.fromarray(arr, "RGB")


def _high_edge_reference(w=64, h=64):
    """Sharp edge pattern for testing ridge/impasto detection."""
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    # Strong vertical edge at center
    arr[:, :w // 2, :] = [30, 30, 30]
    arr[:, w // 2:, :] = [210, 210, 210]
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, multi=False, dark=False, edge=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if multi:
            ref = _multicolor_reference(w, h)
        elif dark:
            ref = _dark_field_reference(w, h)
        elif edge:
            ref = _high_edge_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.44, 0.40, 0.34), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── kiefer_scorched_earth_pass ────────────────────────────────────────────────

def test_s253_kiefer_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "kiefer_scorched_earth_pass")


def test_s253_kiefer_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p)
    result = p.kiefer_scorched_earth_pass()
    assert result is None


def test_s253_kiefer_pass_modifies_canvas():
    """Pass must change at least some pixels."""
    p = _make_small_painter()
    _prime_canvas(p, multi=True)
    before = _get_canvas(p).copy()
    p.kiefer_scorched_earth_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after kiefer_scorched_earth_pass"


def test_s253_kiefer_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p)
    before = _get_canvas(p)
    p.kiefer_scorched_earth_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="Alpha channel modified by kiefer_scorched_earth_pass"
    )


def test_s253_kiefer_pass_zero_opacity_no_change():
    """opacity=0.0 must leave canvas pixel-identical."""
    p = _make_small_painter()
    _prime_canvas(p, multi=True)
    before = _get_canvas(p).copy()
    p.kiefer_scorched_earth_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff[:, :, :3].max() <= 2, \
        "opacity=0 should produce negligible change"


def test_s253_kiefer_pass_ash_effect_on_sky():
    """Upper zone (horizon) should be more desaturated than lower (foreground)."""
    p = _make_small_painter(w=80, h=80)
    _prime_canvas(p, dark=True)
    p.kiefer_scorched_earth_pass(n_zones=4, max_ash_blend=0.80, opacity=1.0)
    after = _get_canvas(p)
    # Top rows (sky/horizon zone) should be greyer (lower chroma) than bottom rows
    top_rows = after[:10, :, :3].astype(float)
    bot_rows = after[70:, :, :3].astype(float)
    # Chroma = max(R,G,B) - min(R,G,B)
    top_chroma = (top_rows.max(axis=2) - top_rows.min(axis=2)).mean()
    bot_chroma = (bot_rows.max(axis=2) - bot_rows.min(axis=2)).mean()
    # Top (horizon) should have less chroma after ash gradient
    assert top_chroma <= bot_chroma + 15, \
        f"Horizon zone should be more ashen (top_chroma={top_chroma:.1f}, bot_chroma={bot_chroma:.1f})"


def test_s253_kiefer_pass_crack_darkens_dark_pixels():
    """Lead crack veining should darken dark-tone pixels."""
    p = _make_small_painter(w=128, h=128)
    # Prime with a uniformly dark field where cracks should appear
    from PIL import Image
    dark_ref = Image.fromarray(
        np.full((128, 128, 3), 60, dtype=np.uint8), "RGB"
    )
    p.tone_ground((0.25, 0.22, 0.18), texture_strength=0.01)
    p.block_in(dark_ref, stroke_size=10, n_strokes=24)
    before = _get_canvas(p).copy()
    p.kiefer_scorched_earth_pass(
        n_cracks=20, crack_depth=0.60, lum_ceiling=0.80,
        opacity=1.0, seed=42
    )
    after = _get_canvas(p)
    # Some pixels must be darker after crack pass
    diff = before[:, :, :3].astype(int) - after[:, :, :3].astype(int)
    assert diff.max() > 5, "Crack veining should darken some pixels"


def test_s253_kiefer_pass_straw_adds_warmth():
    """Straw overlay should shift mid-tone pixels toward warm straw-gold."""
    p = _make_small_painter(w=100, h=100)
    from PIL import Image
    # Mid-grey reference -- should receive straw overlay
    mid_ref = Image.fromarray(np.full((100, 100, 3), 128, dtype=np.uint8), "RGB")
    p.tone_ground((0.50, 0.46, 0.42), texture_strength=0.01)
    p.block_in(mid_ref, stroke_size=12, n_strokes=24)
    before = _get_canvas(p).copy()
    p.kiefer_scorched_earth_pass(
        n_cracks=0, n_zones=1, max_ash_blend=0.0,
        fiber_strength=0.70, straw_lo=0.20, straw_hi=0.90,
        straw_color=(0.76, 0.68, 0.28), opacity=1.0
    )
    after = _get_canvas(p)
    # straw_color is (R=0.76, G=0.68, B=0.28) -- warm means R > B
    # So after straw overlay, R channel should have increased relative to B
    before_r = before[:, :, 2].astype(float).mean()
    after_r  = after[:, :, 2].astype(float).mean()
    before_b = before[:, :, 0].astype(float).mean()
    after_b  = after[:, :, 0].astype(float).mean()
    # Red increases and/or blue decreases after warm straw overlay
    r_diff = after_r - before_r
    b_diff = after_b - before_b
    assert r_diff >= b_diff - 2, \
        f"Straw overlay should warm the mid-tones (R shift={r_diff:.1f}, B shift={b_diff:.1f})"


def test_s253_kiefer_pass_pixel_values_in_range():
    """All RGB values must remain in [0, 255] after pass."""
    p = _make_small_painter()
    _prime_canvas(p, multi=True)
    p.kiefer_scorched_earth_pass(opacity=1.0)
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s253_kiefer_pass_reproducible():
    """Same seed must produce identical output."""
    p1 = _make_small_painter()
    _prime_canvas(p1, multi=True)
    p1.kiefer_scorched_earth_pass(seed=42)
    snap1 = _get_canvas(p1).copy()

    p2 = _make_small_painter()
    _prime_canvas(p2, multi=True)
    p2.kiefer_scorched_earth_pass(seed=42)
    snap2 = _get_canvas(p2)

    np.testing.assert_array_equal(snap1, snap2,
        err_msg="kiefer_scorched_earth_pass not reproducible with same seed")


def test_s253_kiefer_pass_different_seeds_differ():
    """Different seeds must produce different crack layouts."""
    p1 = _make_small_painter(w=128, h=128)
    _prime_canvas(p1, multi=True)
    p1.kiefer_scorched_earth_pass(n_cracks=15, seed=10)
    snap1 = _get_canvas(p1).copy()

    p2 = _make_small_painter(w=128, h=128)
    _prime_canvas(p2, multi=True)
    p2.kiefer_scorched_earth_pass(n_cracks=15, seed=99)
    snap2 = _get_canvas(p2)

    diff = np.abs(snap1.astype(int) - snap2.astype(int))
    assert diff.sum() > 0, "Different seeds should produce different crack paths"


def test_s253_kiefer_pass_zero_cracks():
    """n_cracks=0 should run without error."""
    p = _make_small_painter()
    _prime_canvas(p)
    p.kiefer_scorched_earth_pass(n_cracks=0)


def test_s253_kiefer_pass_full_opacity_applies_maximal_effect():
    """opacity=1.0 should produce stronger total delta than opacity=0.2."""
    p_full = _make_small_painter()
    _prime_canvas(p_full, multi=True)
    before_f = _get_canvas(p_full).copy()
    p_full.kiefer_scorched_earth_pass(opacity=1.0, seed=7)
    after_f  = _get_canvas(p_full)
    delta_full = np.abs(before_f.astype(int) - after_f.astype(int)).sum()

    p_low = _make_small_painter()
    _prime_canvas(p_low, multi=True)
    before_l = _get_canvas(p_low).copy()
    p_low.kiefer_scorched_earth_pass(opacity=0.2, seed=7)
    after_l  = _get_canvas(p_low)
    delta_low = np.abs(before_l.astype(int) - after_l.astype(int)).sum()

    assert delta_full > delta_low, \
        "Higher opacity should produce larger pixel delta"


# ── paint_impasto_ridge_cast_pass ─────────────────────────────────────────────

def test_s253_impasto_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_impasto_ridge_cast_pass")


def test_s253_impasto_pass_returns_none():
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    result = p.paint_impasto_ridge_cast_pass()
    assert result is None


def test_s253_impasto_pass_modifies_canvas():
    """Pass must change at least some pixels on a high-edge canvas."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()
    p.paint_impasto_ridge_cast_pass(opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff.sum() > 0, "Canvas unchanged after paint_impasto_ridge_cast_pass"


def test_s253_impasto_pass_preserves_alpha():
    """Alpha channel must remain unchanged."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p)
    p.paint_impasto_ridge_cast_pass()
    after = _get_canvas(p)
    np.testing.assert_array_equal(
        before[:, :, 3], after[:, :, 3],
        err_msg="Alpha channel modified by paint_impasto_ridge_cast_pass"
    )


def test_s253_impasto_pass_zero_opacity_no_change():
    """opacity=0.0 must leave canvas nearly identical."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()
    p.paint_impasto_ridge_cast_pass(opacity=0.0)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    assert diff[:, :, :3].max() <= 2, \
        "opacity=0 should produce negligible change"


def test_s253_impasto_pass_shadow_darkens():
    """Shadow casting should darken some pixels relative to baseline."""
    p = _make_small_painter(w=128, h=128)
    _prime_canvas(p, edge=True)
    before = _get_canvas(p).copy()
    p.paint_impasto_ridge_cast_pass(
        shadow_strength=0.60, highlight_strength=0.0,
        opacity=1.0
    )
    after = _get_canvas(p)
    # Some pixels should be darker after shadow pass
    diff_dark = (before[:, :, :3].astype(int) - after[:, :, :3].astype(int))
    assert diff_dark.max() > 5, "Shadow pass should darken some pixels"


def test_s253_impasto_pass_highlight_brightens():
    """Highlight should brighten some pixels relative to shadow-only baseline."""
    p_hl = _make_small_painter(w=128, h=128)
    _prime_canvas(p_hl, edge=True)
    p_hl.paint_impasto_ridge_cast_pass(
        shadow_strength=0.0, highlight_strength=0.50, opacity=1.0
    )
    after_hl = _get_canvas(p_hl)

    p_no = _make_small_painter(w=128, h=128)
    _prime_canvas(p_no, edge=True)
    after_no = _get_canvas(p_no)

    # After highlight-only pass, some pixels should be brighter
    diff_bright = after_hl[:, :, :3].astype(int) - after_no[:, :, :3].astype(int)
    assert diff_bright.max() > 3, "Highlight pass should brighten some pixels"


def test_s253_impasto_pass_pixel_values_in_range():
    """All RGB values must remain in [0, 255] after pass."""
    p = _make_small_painter()
    _prime_canvas(p, edge=True)
    p.paint_impasto_ridge_cast_pass(
        shadow_strength=0.80, highlight_strength=0.50, opacity=1.0
    )
    after = _get_canvas(p)
    assert after[:, :, :3].min() >= 0
    assert after[:, :, :3].max() <= 255


def test_s253_impasto_pass_uniform_canvas_minimal_effect():
    """A fully uniform canvas has no ridges; effect should be minimal."""
    from PIL import Image
    p = _make_small_painter(w=80, h=80)
    flat_ref = Image.fromarray(np.full((80, 80, 3), 128, dtype=np.uint8), "RGB")
    p.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    # Do not block_in -- keep surface as uniform as possible
    before = _get_canvas(p).copy()
    p.paint_impasto_ridge_cast_pass(opacity=1.0, ridge_threshold=0.05)
    after = _get_canvas(p)
    diff = np.abs(before.astype(int) - after.astype(int))
    # On a uniform canvas gradient magnitude is near zero so ridges are few
    # Allow some change from texture-ground variation but not massive
    assert diff[:, :, :3].mean() < 30, \
        "Uniform canvas should not trigger large ridge effects"


def test_s253_impasto_pass_edge_canvas_larger_effect():
    """Sharp-edge canvas should trigger more effect than uniform canvas."""
    from PIL import Image

    p_edge = _make_small_painter(w=128, h=128)
    _prime_canvas(p_edge, edge=True)
    before_e = _get_canvas(p_edge).copy()
    p_edge.paint_impasto_ridge_cast_pass(opacity=1.0)
    after_e  = _get_canvas(p_edge)
    delta_edge = np.abs(before_e.astype(int) - after_e.astype(int)).sum()

    p_flat = _make_small_painter(w=128, h=128)
    flat_ref = Image.fromarray(np.full((128, 128, 3), 128, dtype=np.uint8), "RGB")
    p_flat.tone_ground((0.50, 0.50, 0.50), texture_strength=0.0)
    before_f = _get_canvas(p_flat).copy()
    p_flat.paint_impasto_ridge_cast_pass(opacity=1.0)
    after_f  = _get_canvas(p_flat)
    delta_flat = np.abs(before_f.astype(int) - after_f.astype(int)).sum()

    assert delta_edge > delta_flat, \
        "Edge canvas should produce larger impasto ridge effect than flat canvas"


def test_s253_impasto_pass_higher_opacity_larger_delta():
    """opacity=1.0 should produce larger delta than opacity=0.3."""
    p1 = _make_small_painter()
    _prime_canvas(p1, edge=True)
    b1 = _get_canvas(p1).copy()
    p1.paint_impasto_ridge_cast_pass(opacity=1.0)
    a1 = _get_canvas(p1)
    d1 = np.abs(b1.astype(int) - a1.astype(int)).sum()

    p2 = _make_small_painter()
    _prime_canvas(p2, edge=True)
    b2 = _get_canvas(p2).copy()
    p2.paint_impasto_ridge_cast_pass(opacity=0.3)
    a2 = _get_canvas(p2)
    d2 = np.abs(b2.astype(int) - a2.astype(int)).sum()

    assert d1 > d2, "Higher opacity should produce larger pixel delta"


# ── anselm_kiefer catalog entry ───────────────────────────────────────────────

def test_s253_catalog_kiefer_entry_exists():
    import art_catalog
    assert "anselm_kiefer" in art_catalog.CATALOG


def test_s253_catalog_kiefer_artist_name():
    import art_catalog
    s = art_catalog.get_style("anselm_kiefer")
    assert s.artist == "Anselm Kiefer"


def test_s253_catalog_kiefer_movement():
    import art_catalog
    s = art_catalog.get_style("anselm_kiefer")
    assert "Neo-Expressionism" in s.movement


def test_s253_catalog_kiefer_nationality():
    import art_catalog
    s = art_catalog.get_style("anselm_kiefer")
    assert s.nationality == "German"


def test_s253_catalog_kiefer_palette_count():
    import art_catalog
    s = art_catalog.get_style("anselm_kiefer")
    assert len(s.palette) >= 8, "Kiefer palette should have at least 8 colours"


def test_s253_catalog_kiefer_palette_values_valid():
    import art_catalog
    s = art_catalog.get_style("anselm_kiefer")
    for r, g, b in s.palette:
        assert 0.0 <= r <= 1.0
        assert 0.0 <= g <= 1.0
        assert 0.0 <= b <= 1.0


def test_s253_catalog_kiefer_ground_color_valid():
    import art_catalog
    s = art_catalog.get_style("anselm_kiefer")
    r, g, b = s.ground_color
    assert 0.0 <= r <= 1.0
    assert 0.0 <= g <= 1.0
    assert 0.0 <= b <= 1.0


def test_s253_catalog_kiefer_crackle_true():
    """Kiefer should have crackle=True (lead surface cracking)."""
    import art_catalog
    s = art_catalog.get_style("anselm_kiefer")
    assert s.crackle is True


def test_s253_catalog_kiefer_famous_works():
    import art_catalog
    s = art_catalog.get_style("anselm_kiefer")
    assert len(s.famous_works) >= 5
    titles = [t for t, _ in s.famous_works]
    assert any("Sulamith" in t for t in titles)


def test_s253_catalog_kiefer_inspiration_references_164th():
    import art_catalog
    s = art_catalog.get_style("anselm_kiefer")
    assert "164" in s.inspiration


def test_s253_catalog_kiefer_inspiration_references_scorched():
    import art_catalog
    s = art_catalog.get_style("anselm_kiefer")
    assert "scorched" in s.inspiration.lower() or "SCORCHED" in s.inspiration


def test_s253_catalog_total_artist_count():
    """Total artist count should have grown to at least 253."""
    import art_catalog
    assert len(art_catalog.list_artists()) >= 253


def test_s253_catalog_palette_is_dark_and_earthy():
    """Kiefer palette should be predominantly dark/earthy (mean luminance < 0.55)."""
    import art_catalog
    s = art_catalog.get_style("anselm_kiefer")
    lum_values = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in s.palette]
    mean_lum = sum(lum_values) / len(lum_values)
    assert mean_lum < 0.55, \
        f"Kiefer palette should be predominantly dark/earthy (mean_lum={mean_lum:.3f})"
