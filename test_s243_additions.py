"""
test_s243_additions.py -- Session 243 tests for kirchner_brucke_expressionist_pass,
paint_imprimatura_warmth_pass, and the ernst_ludwig_kirchner catalog entry.
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


def _solid_reference(w=64, h=64, rgb=(140, 160, 200)):
    from PIL import Image
    return Image.fromarray(
        (np.ones((h, w, 3), dtype=np.uint8) * np.array(rgb, dtype=np.uint8)), "RGB")


def _gradient_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :w//2, :] = [220, 180, 120]
    arr[:, w//2:, :] = [40, 80, 200]
    return Image.fromarray(arr, "RGB")


def _dark_reference(w=64, h=64):
    from PIL import Image
    arr = np.ones((h, w, 3), dtype=np.uint8) * np.array([28, 24, 20], dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _bright_reference(w=64, h=64):
    from PIL import Image
    arr = np.ones((h, w, 3), dtype=np.uint8) * np.array([220, 215, 210], dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _multicolor_reference(w=64, h=64):
    from PIL import Image
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:h//2, :w//2, :] = [160, 140, 30]
    arr[:h//2, w//2:, :] = [30, 100, 200]
    arr[h//2:, :w//2, :] = [200, 40, 60]
    arr[h//2:, w//2:, :] = [60, 140, 80]
    return Image.fromarray(arr, "RGB")


def _prime_canvas(p, ref=None, *, dark=False, bright=False, multicolor=False):
    w, h = p.canvas.w, p.canvas.h
    if ref is None:
        if dark:
            ref = _dark_reference(w, h)
        elif bright:
            ref = _bright_reference(w, h)
        elif multicolor:
            ref = _multicolor_reference(w, h)
        else:
            ref = _gradient_reference(w, h)
    p.tone_ground((0.18, 0.16, 0.12), texture_strength=0.02)
    p.block_in(ref, stroke_size=10, n_strokes=24)


# ── kirchner_brucke_expressionist_pass ────────────────────────────────────────

def test_s243_kirchner_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "kirchner_brucke_expressionist_pass")
    assert callable(getattr(Painter, "kirchner_brucke_expressionist_pass"))


def test_s243_kirchner_pass_no_error():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, multicolor=True)
    p.kirchner_brucke_expressionist_pass(
        hue_pull_str=0.55, contour_thresh=0.08, contour_dark=0.32,
        polarize_radius=7, polarize_str=0.28, opacity=0.80)


def test_s243_kirchner_zero_opacity_no_change():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p)
    p.kirchner_brucke_expressionist_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), \
        "kirchner_brucke_expressionist_pass at opacity=0.0 must not change any pixels"


def test_s243_kirchner_changes_canvas():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, multicolor=True)
    before = _get_canvas(p)
    p.kirchner_brucke_expressionist_pass(
        hue_pull_str=0.70, contour_thresh=0.06, contour_dark=0.20,
        polarize_radius=5, polarize_str=0.35, opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 2, f"Expected visible changes, got max diff={diff}"


def test_s243_kirchner_alpha_channel_preserved():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, multicolor=True)
    before_alpha = _get_canvas(p)[:, :, 3].copy()
    p.kirchner_brucke_expressionist_pass(opacity=0.85)
    after_alpha = _get_canvas(p)[:, :, 3]
    assert np.array_equal(before_alpha, after_alpha), \
        "Alpha channel must not be altered"


def test_s243_kirchner_contour_darkening_does_not_raise_mean():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, multicolor=True)
    before_mean = _get_canvas(p)[:, :, :3].astype(np.float32).mean()
    p.kirchner_brucke_expressionist_pass(
        hue_pull_str=0.0, contour_thresh=0.01, contour_dark=0.10,
        polarize_str=0.0, opacity=1.0)
    after_mean = _get_canvas(p)[:, :, :3].astype(np.float32).mean()
    assert after_mean <= before_mean + 5.0, \
        f"Strong contour darkening should not increase brightness: before={before_mean:.2f} after={after_mean:.2f}"


def test_s243_kirchner_hue_pull_does_not_crash_greyscale():
    from PIL import Image
    p = _make_small_painter(64, 64)
    grey_ref = Image.fromarray(
        np.ones((64, 64, 3), dtype=np.uint8) * 128, "RGB")
    p.tone_ground((0.5, 0.5, 0.5), texture_strength=0.01)
    p.block_in(grey_ref, stroke_size=10, n_strokes=20)
    p.kirchner_brucke_expressionist_pass(hue_pull_str=0.80, opacity=0.90)


def test_s243_kirchner_polarization_does_not_reduce_variance():
    p = _make_small_painter(64, 64)
    _prime_canvas(p)
    def _lum_std(canvas_arr):
        rgb = canvas_arr[:, :, :3].astype(np.float32) / 255.0
        lum = 0.299*rgb[:,:,0] + 0.587*rgb[:,:,1] + 0.114*rgb[:,:,2]
        return float(lum.std())
    before_std = _lum_std(_get_canvas(p))
    p.kirchner_brucke_expressionist_pass(
        hue_pull_str=0.0, contour_thresh=0.99, contour_dark=0.99,
        polarize_radius=8, polarize_str=0.50, opacity=1.0)
    after_std = _lum_std(_get_canvas(p))
    assert after_std >= before_std - 0.01, \
        f"Polarization should not reduce tonal variance: before={before_std:.4f} after={after_std:.4f}"


# ── paint_imprimatura_warmth_pass ─────────────────────────────────────────────

def test_s243_imprimatura_pass_exists():
    from stroke_engine import Painter
    assert hasattr(Painter, "paint_imprimatura_warmth_pass")
    assert callable(getattr(Painter, "paint_imprimatura_warmth_pass"))


def test_s243_imprimatura_pass_no_error():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, dark=True)
    p.paint_imprimatura_warmth_pass(
        warmth_gate=0.35, warmth_str=0.22,
        imprimatura_r=0.68, imprimatura_g=0.42, imprimatura_b=0.18,
        edge_warmth=0.12, edge_sigma=1.2, opacity=0.60)


def test_s243_imprimatura_zero_opacity_no_change():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, dark=True)
    before = _get_canvas(p)
    p.paint_imprimatura_warmth_pass(opacity=0.0)
    after = _get_canvas(p)
    assert np.array_equal(before, after), \
        "paint_imprimatura_warmth_pass at opacity=0.0 must not change any pixels"


def test_s243_imprimatura_changes_dark_canvas():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, dark=True)
    before = _get_canvas(p)
    p.paint_imprimatura_warmth_pass(warmth_gate=0.50, warmth_str=0.50, opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff > 2, f"Expected visible effect on dark canvas, got max diff={diff}"


def test_s243_imprimatura_alpha_channel_preserved():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, dark=True)
    before_alpha = _get_canvas(p)[:, :, 3].copy()
    p.paint_imprimatura_warmth_pass(opacity=0.80)
    after_alpha = _get_canvas(p)[:, :, 3]
    assert np.array_equal(before_alpha, after_alpha), "Alpha must not be altered"


def test_s243_imprimatura_warms_dark_zones():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, dark=True)
    before_r = _get_canvas(p)[:, :, 2].astype(np.float32).mean()
    p.paint_imprimatura_warmth_pass(
        warmth_gate=0.50, warmth_str=0.60,
        imprimatura_r=0.90, imprimatura_g=0.50, imprimatura_b=0.10,
        opacity=1.0)
    after_r = _get_canvas(p)[:, :, 2].astype(np.float32).mean()
    assert after_r >= before_r, \
        f"Warm amber imprimatura should increase mean red: before={before_r:.2f} after={after_r:.2f}"


def test_s243_imprimatura_minimal_on_bright_canvas():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, bright=True)
    before = _get_canvas(p)
    p.paint_imprimatura_warmth_pass(warmth_gate=0.20, warmth_str=0.50, opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).mean()
    assert diff < 15.0, \
        f"Low warmth_gate should barely affect bright canvas: mean diff={diff:.2f}"


def test_s243_imprimatura_zero_strength_no_change():
    p = _make_small_painter(64, 64)
    _prime_canvas(p, dark=True)
    before = _get_canvas(p)
    p.paint_imprimatura_warmth_pass(warmth_str=0.0, edge_warmth=0.0, opacity=1.0)
    after = _get_canvas(p)
    diff = np.abs(after.astype(np.int32) - before.astype(np.int32)).max()
    assert diff <= 1, \
        f"warmth_str=0 and edge_warmth=0 should produce no change, got max diff={diff}"


# ── ernst_ludwig_kirchner catalog entry ───────────────────────────────────────

def test_s243_kirchner_in_catalog():
    from art_catalog import CATALOG
    assert "ernst_ludwig_kirchner" in CATALOG


def test_s243_kirchner_catalog_artist_name():
    from art_catalog import CATALOG
    assert CATALOG["ernst_ludwig_kirchner"].artist == "Ernst Ludwig Kirchner"


def test_s243_kirchner_catalog_palette_valid():
    from art_catalog import CATALOG
    entry = CATALOG["ernst_ludwig_kirchner"]
    assert len(entry.palette) >= 5
    for col in entry.palette:
        assert len(col) == 3
        assert all(0.0 <= ch <= 1.0 for ch in col)


def test_s243_kirchner_catalog_movement():
    from art_catalog import CATALOG
    entry = CATALOG["ernst_ludwig_kirchner"]
    assert "Expressionism" in entry.movement or "Brücke" in entry.movement or "Brucke" in entry.movement


def test_s243_kirchner_catalog_inspiration_references_pass():
    from art_catalog import CATALOG
    assert "kirchner_brucke_expressionist_pass" in CATALOG["ernst_ludwig_kirchner"].inspiration


def test_s243_kirchner_catalog_inspiration_references_mode_number():
    from art_catalog import CATALOG
    insp = CATALOG["ernst_ludwig_kirchner"].inspiration
    assert "ONE HUNDRED AND FIFTY-FOURTH" in insp


def test_s243_kirchner_catalog_famous_works():
    from art_catalog import CATALOG
    entry = CATALOG["ernst_ludwig_kirchner"]
    assert len(entry.famous_works) >= 4
    for work in entry.famous_works:
        assert len(work) == 2


def test_s243_catalog_total_count():
    from art_catalog import CATALOG
    assert len(CATALOG) >= 243
