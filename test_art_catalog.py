"""
test_art_catalog.py — Unit tests for the art catalog and related schema.

Covers:
  - All expected artists are present in CATALOG
  - Each ArtStyle has structurally valid data (palette colours in [0, 1], etc.)
  - El Greco entry is correct (session 11 addition)
  - get_style() and list_artists() behave correctly
  - Period enum contains all expected values including MANNERIST (session 11)
  - Style.stroke_params returns valid dicts for every Period value
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(__file__))

from art_catalog import CATALOG, get_style, list_artists
from scene_schema import Period, Style, Medium, PaletteHint


# ──────────────────────────────────────────────────────────────────────────────
# Catalog presence
# ──────────────────────────────────────────────────────────────────────────────

EXPECTED_ARTISTS = [
    "caravaggio", "caspar_david_friedrich", "cezanne", "egon_schiele",
    "el_greco", "gauguin", "goya", "hilma_af_klint", "hokusai", "klimt",
    "leonardo", "manet", "monet", "rembrandt", "rothko", "sargent",
    "seurat", "turner", "van_gogh", "velazquez", "vermeer",
]


def test_all_expected_artists_present():
    """Every artist added across all sessions must appear in CATALOG."""
    for artist in EXPECTED_ARTISTS:
        assert artist in CATALOG, f"Missing artist: {artist!r}"


def test_el_greco_in_catalog():
    """El Greco (session 11) must be in the catalog."""
    assert "el_greco" in CATALOG


def test_el_greco_movement():
    s = get_style("el_greco")
    assert "Manner" in s.movement or "manner" in s.movement.lower()


def test_el_greco_palette_length():
    s = get_style("el_greco")
    assert len(s.palette) >= 5


def test_el_greco_palette_values_in_range():
    """All El Greco palette RGB values must be in [0, 1]."""
    s = get_style("el_greco")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in El Greco palette {rgb}")


def test_el_greco_ground_color_valid():
    s = get_style("el_greco")
    assert len(s.ground_color) == 3
    for ch in s.ground_color:
        assert 0.0 <= ch <= 1.0


# ──────────────────────────────────────────────────────────────────────────────
# Structural integrity of every catalog entry
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("key,style", list(CATALOG.items()))
def test_palette_colors_in_range(key, style):
    """Every palette colour channel must be in [0, 1]."""
    for rgb in style.palette:
        assert len(rgb) == 3, f"{key}: palette entry not 3-tuple"
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"{key}: palette channel {ch} out of [0,1]"


@pytest.mark.parametrize("key,style", list(CATALOG.items()))
def test_ground_color_in_range(key, style):
    assert len(style.ground_color) == 3, f"{key}: ground_color not 3-tuple"
    for ch in style.ground_color:
        assert 0.0 <= ch <= 1.0, f"{key}: ground_color channel {ch} out of [0,1]"


@pytest.mark.parametrize("key,style", list(CATALOG.items()))
def test_glazing_color_valid_if_present(key, style):
    if style.glazing is not None:
        assert len(style.glazing) == 3, f"{key}: glazing not 3-tuple"
        for ch in style.glazing:
            assert 0.0 <= ch <= 1.0, f"{key}: glazing channel {ch} out of [0,1]"


@pytest.mark.parametrize("key,style", list(CATALOG.items()))
def test_stroke_params_positive(key, style):
    assert style.stroke_size > 0, f"{key}: stroke_size must be > 0"
    assert 0.0 <= style.wet_blend <= 1.0, f"{key}: wet_blend out of [0,1]"
    assert 0.0 <= style.edge_softness <= 1.0, f"{key}: edge_softness out of [0,1]"
    assert 0.0 <= style.jitter <= 1.0, f"{key}: jitter out of [0,1]"


@pytest.mark.parametrize("key,style", list(CATALOG.items()))
def test_text_fields_non_empty(key, style):
    assert style.artist,    f"{key}: artist field is empty"
    assert style.movement,  f"{key}: movement field is empty"
    assert style.technique, f"{key}: technique field is empty"
    assert len(style.famous_works) >= 1, f"{key}: must have at least one famous work"


# ──────────────────────────────────────────────────────────────────────────────
# get_style / list_artists API
# ──────────────────────────────────────────────────────────────────────────────

def test_get_style_known_key():
    s = get_style("leonardo")
    assert s.artist == "Leonardo da Vinci"


def test_get_style_case_insensitive():
    s = get_style("EL_GRECO")
    assert "El Greco" in s.artist or "Greco" in s.artist


def test_get_style_unknown_key_raises():
    with pytest.raises(KeyError):
        get_style("nonexistent_painter_xyz")


def test_list_artists_returns_all_catalog_keys():
    artists = list_artists()
    assert set(artists) == set(CATALOG.keys())


def test_list_artists_is_sorted():
    artists = list_artists()
    assert artists == sorted(artists)


# ──────────────────────────────────────────────────────────────────────────────
# Period enum — all expected values present
# ──────────────────────────────────────────────────────────────────────────────

EXPECTED_PERIODS = [
    "RENAISSANCE", "BAROQUE", "IMPRESSIONIST", "EXPRESSIONIST",
    "POINTILLIST", "ROMANTIC", "ART_NOUVEAU", "UKIYO_E",
    "PROTO_EXPRESSIONIST", "REALIST", "VIENNESE_EXPRESSIONIST",
    "COLOR_FIELD", "SYNTHETIST", "MANNERIST",
    "CONTEMPORARY", "FANTASY_ART", "NONE",
]


def test_all_expected_periods_present():
    period_names = {p.name for p in Period}
    for name in EXPECTED_PERIODS:
        assert name in period_names, f"Missing Period: {name}"


def test_mannerist_period_present():
    """Session 11: MANNERIST must exist in Period enum."""
    assert hasattr(Period, "MANNERIST"), "Period.MANNERIST not found"
    assert Period.MANNERIST in list(Period)


# ──────────────────────────────────────────────────────────────────────────────
# Style.stroke_params — every Period must return a valid dict
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("period", list(Period))
def test_stroke_params_all_periods(period):
    """stroke_params must return a dict with the four required keys for every Period."""
    style = Style(medium=Medium.OIL, period=period, palette=PaletteHint.WARM_EARTH)
    params = style.stroke_params
    assert "stroke_size_face" in params
    assert "stroke_size_bg"   in params
    assert "wet_blend"        in params
    assert "edge_softness"    in params
    assert params["stroke_size_face"] > 0
    assert params["stroke_size_bg"]   > 0
    assert 0.0 <= params["wet_blend"]    <= 1.0
    assert 0.0 <= params["edge_softness"] <= 1.0


def test_mannerist_stroke_params_values():
    """MANNERIST should have low wet_blend (jewel-tone clarity) and moderate stroke_size."""
    style = Style(medium=Medium.OIL, period=Period.MANNERIST, palette=PaletteHint.JEWEL)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.30, "Mannerist wet_blend should be low for jewel-zone clarity"
    assert p["stroke_size_face"] >= 6


# ──────────────────────────────────────────────────────────────────────────────
# Caspar David Friedrich — session 12 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_caspar_david_friedrich_in_catalog():
    """Friedrich (session 12) must be present in CATALOG."""
    assert "caspar_david_friedrich" in CATALOG


def test_caspar_david_friedrich_movement():
    s = get_style("caspar_david_friedrich")
    assert "Romanti" in s.movement or "romanti" in s.movement.lower()


def test_caspar_david_friedrich_palette_length():
    s = get_style("caspar_david_friedrich")
    assert len(s.palette) >= 5, "Friedrich palette should have at least 5 key colours"


def test_caspar_david_friedrich_palette_values_in_range():
    """All Friedrich palette RGB values must be in [0, 1]."""
    s = get_style("caspar_david_friedrich")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Friedrich palette {rgb}")


def test_caspar_david_friedrich_famous_works_not_empty():
    s = get_style("caspar_david_friedrich")
    assert len(s.famous_works) >= 3, "Friedrich should have at least 3 famous works"
    # The Wanderer is the canonical entry
    titles = [w[0] for w in s.famous_works]
    assert any("Wanderer" in t for t in titles), (
        "Friedrich's famous works should include Wanderer above the Sea of Fog")
