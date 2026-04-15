"""
test_art_catalog.py — Unit tests for the art catalog and related schema.

Covers:
  - All expected artists are present in CATALOG
  - Each ArtStyle has structurally valid data (palette colours in [0, 1], etc.)
  - El Greco entry is correct (session 11 addition)
  - Kandinsky entry is correct (session 14 addition)
  - Matisse entry is correct (session 16 addition)
  - get_style() and list_artists() behave correctly
  - Period enum contains all expected values including FAUVIST (session 16)
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
    "artemisia_gentileschi",
    "caravaggio", "caspar_david_friedrich", "cezanne",
    "delacroix",
    "egon_schiele",
    "el_greco", "frida_kahlo", "gauguin", "goya", "hilma_af_klint", "hokusai",
    "jan_van_eyck",
    "kandinsky",
    "klimt", "leonardo", "manet", "matisse", "modigliani", "monet", "rembrandt",
    "rothko", "sargent", "seurat", "sorolla", "titian", "turner", "van_gogh",
    "velazquez", "vermeer",
    "vuillard",
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
    "COLOR_FIELD", "SYNTHETIST", "MANNERIST", "SURREALIST",
    "ABSTRACT_EXPRESSIONIST", "VENETIAN_RENAISSANCE",
    "FAUVIST", "PRIMITIVIST", "EARLY_NETHERLANDISH",
    "NABIS", "LUMINISMO",
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


# ──────────────────────────────────────────────────────────────────────────────
# Frida Kahlo — session 13 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_frida_kahlo_in_catalog():
    """Frida Kahlo (session 13) must be present in CATALOG."""
    assert "frida_kahlo" in CATALOG


def test_frida_kahlo_movement():
    s = get_style("frida_kahlo")
    # Movement should reference Mexican or Surrealist context
    assert ("Mexican" in s.movement or "Naïve" in s.movement
            or "Folk" in s.movement or "Surreal" in s.movement)


def test_frida_kahlo_palette_length():
    s = get_style("frida_kahlo")
    assert len(s.palette) >= 5, "Kahlo palette should have at least 5 key colours"


def test_frida_kahlo_palette_values_in_range():
    """All Kahlo palette RGB values must be in [0, 1]."""
    s = get_style("frida_kahlo")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Kahlo palette {rgb}")


def test_frida_kahlo_wet_blend_low():
    """Kahlo's retablo technique is flat — wet_blend must be very low."""
    s = get_style("frida_kahlo")
    assert s.wet_blend <= 0.15, (
        f"Kahlo wet_blend should be low (flat zones), got {s.wet_blend}")


def test_frida_kahlo_edge_softness_low():
    """Kahlo uses hard dark outlines — edge_softness must be very low."""
    s = get_style("frida_kahlo")
    assert s.edge_softness <= 0.20, (
        f"Kahlo edge_softness should be low (hard outlines), got {s.edge_softness}")


def test_frida_kahlo_no_crackle():
    """Kahlo worked on Masonite/metal — crackle should be False."""
    s = get_style("frida_kahlo")
    assert not s.crackle, "Kahlo panels do not crackle like oil on canvas"


def test_frida_kahlo_famous_works_not_empty():
    s = get_style("frida_kahlo")
    assert len(s.famous_works) >= 3, "Kahlo should have at least 3 famous works"
    titles = [w[0] for w in s.famous_works]
    assert any("Frida" in t or "Column" in t or "Thorn" in t
               for t in titles), (
        "Kahlo famous works should include at least one well-known self-portrait")


def test_surrealist_period_present():
    """Session 13: SURREALIST must exist in Period enum."""
    assert hasattr(Period, "SURREALIST"), "Period.SURREALIST not found"
    assert Period.SURREALIST in list(Period)


def test_surrealist_stroke_params_low_wet_blend():
    """SURREALIST should have very low wet_blend for flat retablo zones."""
    style = Style(medium=Medium.OIL, period=Period.SURREALIST,
                  palette=PaletteHint.JEWEL)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.15, (
        f"SURREALIST wet_blend should be very low, got {p['wet_blend']}")


# ──────────────────────────────────────────────────────────────────────────────
# Session 14: Wassily Kandinsky + Period.ABSTRACT_EXPRESSIONIST
# ──────────────────────────────────────────────────────────────────────────────

def test_kandinsky_in_catalog():
    """Session 14: Kandinsky must be present in CATALOG."""
    assert "kandinsky" in CATALOG, "kandinsky not found in CATALOG"


def test_kandinsky_movement():
    """Kandinsky's movement must reference Blaue Reiter or Abstract."""
    s = get_style("kandinsky")
    movement_lower = s.movement.lower()
    assert ("blaue" in movement_lower or "abstract" in movement_lower
            or "bauhaus" in movement_lower), (
        f"Kandinsky movement should reference Der Blaue Reiter, Bauhaus, or Abstract; "
        f"got: {s.movement!r}")


def test_kandinsky_nationality():
    """Kandinsky was Russian-German."""
    s = get_style("kandinsky")
    nat_lower = s.nationality.lower()
    assert "russian" in nat_lower or "german" in nat_lower, (
        f"Kandinsky nationality should contain Russian or German; got: {s.nationality!r}")


def test_kandinsky_palette_has_primary_triad():
    """Kandinsky's palette must include a yellow, a blue, and a red (his core synesthetic triad)."""
    s = get_style("kandinsky")
    has_yellow = any(r > 0.70 and g > 0.60 and b < 0.40
                     for r, g, b in s.palette)
    has_blue   = any(b > 0.50 and r < 0.35 and g < 0.40
                     for r, g, b in s.palette)
    has_red    = any(r > 0.60 and g < 0.30 and b < 0.30
                     for r, g, b in s.palette)
    assert has_yellow, "Kandinsky palette missing yellow (advancing/trumpet colour)"
    assert has_blue,   "Kandinsky palette missing blue (receding/cello colour)"
    assert has_red,    "Kandinsky palette missing red (drumbeat colour)"


def test_kandinsky_low_wet_blend():
    """Kandinsky's geometric forms demand crisp edges; wet_blend must be low."""
    s = get_style("kandinsky")
    assert s.wet_blend <= 0.15, (
        f"Kandinsky wet_blend should be low for crisp geometry; got {s.wet_blend}")


def test_kandinsky_low_edge_softness():
    """Kandinsky: circles and triangles have hard edges; edge_softness must be low."""
    s = get_style("kandinsky")
    assert s.edge_softness <= 0.25, (
        f"Kandinsky edge_softness should be low; got {s.edge_softness}")


def test_kandinsky_no_crackle():
    """Kandinsky worked on modern canvas; no aged crackle finish."""
    s = get_style("kandinsky")
    assert not s.crackle, "Kandinsky crackle should be False (modern canvas)"


def test_kandinsky_famous_works_not_empty():
    """Kandinsky should have at least 4 famous works documented."""
    s = get_style("kandinsky")
    assert len(s.famous_works) >= 4, (
        f"Kandinsky should have ≥4 famous works; got {len(s.famous_works)}")
    titles = [w[0] for w in s.famous_works]
    assert any("Composition" in t for t in titles), (
        "Kandinsky famous works should include at least one Composition")


def test_kandinsky_inspiration_references_geometric_resonance():
    """Kandinsky inspiration text should reference geometric_resonance_pass."""
    s = get_style("kandinsky")
    assert "geometric_resonance" in s.inspiration.lower().replace(" ", "_"), (
        "Kandinsky inspiration should reference geometric_resonance_pass()")


def test_abstract_expressionist_period_present():
    """Session 14: ABSTRACT_EXPRESSIONIST must exist in Period enum."""
    assert hasattr(Period, "ABSTRACT_EXPRESSIONIST"), (
        "Period.ABSTRACT_EXPRESSIONIST not found")
    assert Period.ABSTRACT_EXPRESSIONIST in list(Period)


def test_abstract_expressionist_stroke_params_low_wet_blend():
    """ABSTRACT_EXPRESSIONIST should have low wet_blend for crisp geometric edges."""
    style = Style(medium=Medium.OIL, period=Period.ABSTRACT_EXPRESSIONIST,
                  palette=PaletteHint.JEWEL)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.15, (
        f"ABSTRACT_EXPRESSIONIST wet_blend should be low for crisp geometry; "
        f"got {p['wet_blend']}")


def test_abstract_expressionist_stroke_params_low_edge_softness():
    """ABSTRACT_EXPRESSIONIST should have low edge_softness (geometric precision)."""
    style = Style(medium=Medium.OIL, period=Period.ABSTRACT_EXPRESSIONIST,
                  palette=PaletteHint.JEWEL)
    p = style.stroke_params
    assert p["edge_softness"] <= 0.20, (
        f"ABSTRACT_EXPRESSIONIST edge_softness should be low; got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Titian + Period.VENETIAN_RENAISSANCE — current session addition
# ──────────────────────────────────────────────────────────────────────────────

def test_titian_in_catalog():
    """Titian must be present in CATALOG."""
    assert "titian" in CATALOG, "titian not found in CATALOG"


def test_titian_movement():
    """Titian's movement must reference Venetian."""
    s = get_style("titian")
    assert "Venetian" in s.movement or "venetian" in s.movement.lower(), (
        f"Titian movement should reference Venetian; got: {s.movement!r}")


def test_titian_nationality():
    """Titian was Italian (Venetian)."""
    s = get_style("titian")
    assert "Italian" in s.nationality, (
        f"Titian nationality should contain Italian; got: {s.nationality!r}")


def test_titian_palette_length():
    s = get_style("titian")
    assert len(s.palette) >= 5, "Titian palette should have at least 5 key colours"


def test_titian_palette_values_in_range():
    """All Titian palette RGB values must be in [0, 1]."""
    s = get_style("titian")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Titian palette {rgb}")


def test_titian_palette_has_warm_red():
    """Titian's palette must include a dominant warm red (vermilion)."""
    s = get_style("titian")
    has_warm_red = any(r > 0.65 and g < 0.45 and b < 0.35
                       for r, g, b in s.palette)
    assert has_warm_red, "Titian palette should include warm vermilion-red"


def test_titian_high_wet_blend():
    """Titian worked wet-into-wet — wet_blend must be high."""
    s = get_style("titian")
    assert s.wet_blend >= 0.70, (
        f"Titian wet_blend should be high (wet-into-wet technique); got {s.wet_blend}")


def test_titian_crackle():
    """Titian worked on 16th-century Venetian canvas — crackle should be True."""
    s = get_style("titian")
    assert s.crackle, "Titian crackle should be True (aged Venetian canvas)"


def test_titian_has_glazing():
    """Titian used a warm red-amber unifying glaze — glazing must not be None."""
    s = get_style("titian")
    assert s.glazing is not None, "Titian glazing should be set (warm Venetian glaze)"
    for ch in s.glazing:
        assert 0.0 <= ch <= 1.0, f"Titian glazing channel out of range: {ch}"


def test_titian_famous_works_include_venus():
    """Titian's famous works should include Venus of Urbino."""
    s = get_style("titian")
    titles = [w[0] for w in s.famous_works]
    assert any("Venus" in t for t in titles), (
        "Titian famous works should include Venus of Urbino")


def test_titian_inspiration_references_venetian_glaze():
    """Titian inspiration text should reference venetian_glaze_pass."""
    s = get_style("titian")
    assert "venetian_glaze" in s.inspiration.lower().replace(" ", "_"), (
        "Titian inspiration should reference venetian_glaze_pass()")


def test_venetian_renaissance_period_present():
    """VENETIAN_RENAISSANCE must exist in Period enum."""
    assert hasattr(Period, "VENETIAN_RENAISSANCE"), (
        "Period.VENETIAN_RENAISSANCE not found")
    assert Period.VENETIAN_RENAISSANCE in list(Period)


def test_venetian_renaissance_stroke_params_high_wet_blend():
    """VENETIAN_RENAISSANCE should have high wet_blend for Titian's wet-into-wet technique."""
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.60, (
        f"VENETIAN_RENAISSANCE wet_blend should be high; got {p['wet_blend']}")


def test_venetian_renaissance_stroke_params_moderate_edge_softness():
    """VENETIAN_RENAISSANCE edge_softness should be between sfumato and Baroque."""
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.45 <= p["edge_softness"] <= 0.80, (
        f"VENETIAN_RENAISSANCE edge_softness should be moderate (0.45–0.80); "
        f"got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Henri Matisse / Fauvism — session 16
# ──────────────────────────────────────────────────────────────────────────────

def test_matisse_in_catalog():
    """Matisse (session 16) must be in the catalog."""
    assert "matisse" in CATALOG


def test_matisse_movement():
    s = get_style("matisse")
    assert "fauv" in s.movement.lower() or "fauvist" in s.movement.lower() or "Fauv" in s.movement


def test_matisse_nationality():
    s = get_style("matisse")
    assert "french" in s.nationality.lower()


def test_matisse_palette_length():
    s = get_style("matisse")
    assert len(s.palette) >= 6


def test_matisse_palette_values_in_range():
    """All Matisse palette RGB values must be in [0, 1]."""
    s = get_style("matisse")
    for i, col in enumerate(s.palette):
        for ch in col:
            assert 0.0 <= ch <= 1.0, (
                f"Matisse palette colour {i} channel out of range: {ch}")


def test_matisse_low_wet_blend():
    """Matisse worked in flat, direct strokes — wet_blend must be very low."""
    s = get_style("matisse")
    assert s.wet_blend <= 0.12, (
        f"Matisse wet_blend should be very low (flat Fauvist technique); "
        f"got {s.wet_blend}")


def test_matisse_low_edge_softness():
    """Matisse used bold coloured outlines — edge_softness must be very low."""
    s = get_style("matisse")
    assert s.edge_softness <= 0.20, (
        f"Matisse edge_softness should be very low (bold outlines); "
        f"got {s.edge_softness}")


def test_matisse_no_crackle():
    """Matisse worked on modern canvas — crackle should be False."""
    s = get_style("matisse")
    assert not s.crackle, "Matisse crackle should be False (modern canvas)"


def test_matisse_no_glazing():
    """Matisse applied colour directly without oil glazes — glazing should be None."""
    s = get_style("matisse")
    assert s.glazing is None, "Matisse glazing should be None (no oil glazing in Fauvism)"


def test_matisse_ground_is_pale():
    """Matisse ground should be pale cream — he let the canvas read through."""
    s = get_style("matisse")
    avg = sum(s.ground_color) / 3.0
    assert avg >= 0.70, (
        f"Matisse ground should be pale cream (avg channel ≥ 0.70); got {avg:.2f}")


def test_matisse_famous_works_include_dance():
    """Matisse's famous works should include The Dance."""
    s = get_style("matisse")
    titles = [w[0] for w in s.famous_works]
    assert any("Dance" in t or "dance" in t for t in titles), (
        "Matisse famous works should include The Dance")


def test_matisse_inspiration_references_fauvist_mosaic():
    """Matisse inspiration text should reference fauvist_mosaic_pass."""
    s = get_style("matisse")
    assert "fauvist_mosaic" in s.inspiration.lower().replace(" ", "_"), (
        "Matisse inspiration should reference fauvist_mosaic_pass()")


def test_fauvist_period_present():
    """FAUVIST must exist in Period enum (session 16)."""
    assert hasattr(Period, "FAUVIST"), "Period.FAUVIST not found"
    assert Period.FAUVIST in list(Period)


def test_fauvist_stroke_params_low_wet_blend():
    """FAUVIST should have very low wet_blend — flat zones, no colour bleed."""
    style = Style(medium=Medium.OIL, period=Period.FAUVIST,
                  palette=PaletteHint.JEWEL)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.10, (
        f"FAUVIST wet_blend should be very low; got {p['wet_blend']}")


def test_fauvist_stroke_params_low_edge_softness():
    """FAUVIST should have very low edge_softness — coloured contour lines, no sfumato."""
    style = Style(medium=Medium.OIL, period=Period.FAUVIST,
                  palette=PaletteHint.JEWEL)
    p = style.stroke_params
    assert p["edge_softness"] <= 0.15, (
        f"FAUVIST edge_softness should be very low; got {p['edge_softness']}")


def test_fauvist_stroke_params_all_keys_present():
    """FAUVIST stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.FAUVIST,
                  palette=PaletteHint.JEWEL)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"FAUVIST stroke_params missing key: {key!r}"


# ──────────────────────────────────────────────────────────────────────────────
# Modigliani catalog entry (session 17)
# ──────────────────────────────────────────────────────────────────────────────

def test_modigliani_in_catalog():
    """Modigliani (session 17) must be in the catalog."""
    assert "modigliani" in CATALOG


def test_modigliani_movement():
    s = get_style("modigliani")
    movement_lower = s.movement.lower()
    assert ("paris" in movement_lower or "primitivis" in movement_lower
            or "école" in movement_lower or "post" in movement_lower), (
        f"Modigliani movement should reference École de Paris or Primitivism; got {s.movement!r}")


def test_modigliani_palette_length():
    s = get_style("modigliani")
    assert len(s.palette) >= 5, "Modigliani palette should have at least 5 key colours"


def test_modigliani_palette_values_in_range():
    """All Modigliani palette RGB values must be in [0, 1]."""
    s = get_style("modigliani")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Modigliani palette {rgb}")


def test_modigliani_ground_warm():
    """Modigliani's warm ochre ground: R channel must dominate B."""
    s = get_style("modigliani")
    r, g, b = s.ground_color
    assert r > b, (
        f"Modigliani ground should be warm (R > B), got R={r:.2f} B={b:.2f}")


def test_modigliani_wet_blend_low():
    """Modigliani's flat zone technique: wet_blend must be very low."""
    s = get_style("modigliani")
    assert s.wet_blend <= 0.20, (
        f"Modigliani wet_blend should be low (flat zones), got {s.wet_blend}")


def test_modigliani_edge_softness_low():
    """Modigliani uses hard oval contour outlines — edge_softness must be low."""
    s = get_style("modigliani")
    assert s.edge_softness <= 0.25, (
        f"Modigliani edge_softness should be low (hard oval contour), got {s.edge_softness}")


def test_modigliani_no_crackle():
    """Modigliani worked in the early 20th century — crackle should be False."""
    s = get_style("modigliani")
    assert not s.crackle, "Modigliani's modern canvas does not crackle"


def test_modigliani_famous_works_not_empty():
    s = get_style("modigliani")
    assert len(s.famous_works) >= 3, "Modigliani should have at least 3 famous works"


def test_modigliani_famous_works_include_known_painting():
    s = get_style("modigliani")
    titles = [w[0] for w in s.famous_works]
    assert any("Nu" in t or "Portrait" in t or "Jeanne" in t for t in titles), (
        "Modigliani famous works should include a known nude or portrait")


def test_modigliani_inspiration_references_oval_mask():
    """Modigliani inspiration text should reference oval_mask_pass."""
    s = get_style("modigliani")
    assert "oval_mask" in s.inspiration.lower().replace(" ", "_"), (
        "Modigliani inspiration should reference oval_mask_pass()")


# ──────────────────────────────────────────────────────────────────────────────
# PRIMITIVIST period (session 17)
# ──────────────────────────────────────────────────────────────────────────────

def test_primitivist_period_present():
    """PRIMITIVIST must exist in Period enum (session 17)."""
    assert hasattr(Period, "PRIMITIVIST"), "Period.PRIMITIVIST not found"
    assert Period.PRIMITIVIST in list(Period)


def test_primitivist_stroke_params_low_wet_blend():
    """PRIMITIVIST should have low wet_blend — flat zones, no colour bleed."""
    style = Style(medium=Medium.OIL, period=Period.PRIMITIVIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.20, (
        f"PRIMITIVIST wet_blend should be low (flat zones), got {p['wet_blend']}")


def test_primitivist_stroke_params_low_edge_softness():
    """PRIMITIVIST should have low edge_softness — oval contour present, no sfumato."""
    style = Style(medium=Medium.OIL, period=Period.PRIMITIVIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] <= 0.30, (
        f"PRIMITIVIST edge_softness should be low; got {p['edge_softness']}")


def test_primitivist_stroke_params_all_keys_present():
    """PRIMITIVIST stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.PRIMITIVIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"PRIMITIVIST stroke_params missing key: {key!r}"


# ──────────────────────────────────────────────────────────────────────────────
# Jan van Eyck — Early Netherlandish (session 18)
# ──────────────────────────────────────────────────────────────────────────────

def test_jan_van_eyck_in_catalog():
    """Jan van Eyck must be present in the CATALOG under key 'jan_van_eyck'."""
    assert "jan_van_eyck" in CATALOG, "jan_van_eyck not found in CATALOG"


def test_jan_van_eyck_style_retrieval():
    """get_style('jan_van_eyck') must return an ArtStyle without raising."""
    s = get_style("jan_van_eyck")
    assert s is not None


def test_jan_van_eyck_movement():
    """Jan van Eyck movement must be 'Early Netherlandish'."""
    s = get_style("jan_van_eyck")
    assert "netherlandish" in s.movement.lower(), (
        f"Expected 'Early Netherlandish' movement, got {s.movement!r}")


def test_jan_van_eyck_nationality():
    """Jan van Eyck must be listed as Flemish."""
    s = get_style("jan_van_eyck")
    assert s.nationality.lower() == "flemish", (
        f"Expected nationality 'Flemish', got {s.nationality!r}")


def test_jan_van_eyck_palette_has_lapis_blue():
    """Palette must include a deep lapis-like blue (B channel dominant, not too bright)."""
    s = get_style("jan_van_eyck")
    has_deep_blue = any(
        b > 0.45 and b > r and b > g and (r + g + b) / 3 < 0.65
        for r, g, b in s.palette
    )
    assert has_deep_blue, (
        "jan_van_eyck palette should include a deep lapis lazuli blue")


def test_jan_van_eyck_palette_has_chalk_white_highlight():
    """Palette must include a near-white chalk highlight colour."""
    s = get_style("jan_van_eyck")
    has_white = any(r > 0.85 and g > 0.80 and b > 0.70 for r, g, b in s.palette)
    assert has_white, (
        "jan_van_eyck palette should include a chalk-white gesso highlight")


def test_jan_van_eyck_ground_is_very_light():
    """Ground colour must be nearly white — chalk gesso panel."""
    s = get_style("jan_van_eyck")
    mean_ground = sum(s.ground_color) / 3
    assert mean_ground > 0.85, (
        f"jan_van_eyck ground should be chalk-white (mean > 0.85), got {mean_ground:.3f}")


def test_jan_van_eyck_has_glazing():
    """Van Eyck used a warm amber oil glaze — glazing should not be None."""
    s = get_style("jan_van_eyck")
    assert s.glazing is not None, "jan_van_eyck should have a warm amber glazing colour"
    r, g, b = s.glazing
    assert r > g > b, (
        f"Van Eyck glaze should be warm-amber (R>G>B), got ({r:.2f},{g:.2f},{b:.2f})")


def test_jan_van_eyck_crackle_true():
    """15th-century oak panel — crackle must be True."""
    s = get_style("jan_van_eyck")
    assert s.crackle, "jan_van_eyck's oak panel should have crackle=True"


def test_jan_van_eyck_palette_has_seven_colours():
    """Palette should have exactly 7 key pigment entries."""
    s = get_style("jan_van_eyck")
    assert len(s.palette) == 7, (
        f"jan_van_eyck palette should have 7 entries, got {len(s.palette)}")


def test_jan_van_eyck_wet_blend_moderate():
    """Van Eyck's glazing technique requires moderate wet_blend (0.40–0.70)."""
    s = get_style("jan_van_eyck")
    assert 0.40 <= s.wet_blend <= 0.70, (
        f"jan_van_eyck wet_blend should be moderate (glazing), got {s.wet_blend}")


def test_jan_van_eyck_famous_works_not_empty():
    s = get_style("jan_van_eyck")
    assert len(s.famous_works) >= 3, "jan_van_eyck should have at least 3 famous works"


def test_jan_van_eyck_famous_works_include_arnolfini():
    """Arnolfini Portrait must be in jan_van_eyck famous works."""
    s = get_style("jan_van_eyck")
    titles = [w[0] for w in s.famous_works]
    assert any("Arnolfini" in t for t in titles), (
        "jan_van_eyck famous works should include The Arnolfini Portrait")


def test_jan_van_eyck_inspiration_references_glazed_panel():
    """Inspiration text must reference glazed_panel_pass."""
    s = get_style("jan_van_eyck")
    assert "glazed_panel" in s.inspiration.lower().replace(" ", "_"), (
        "jan_van_eyck inspiration should reference glazed_panel_pass()")


# ──────────────────────────────────────────────────────────────────────────────
# Artemisia Gentileschi — current session addition
# ──────────────────────────────────────────────────────────────────────────────

def test_artemisia_gentileschi_in_catalog():
    """Artemisia Gentileschi must be present in CATALOG."""
    assert "artemisia_gentileschi" in CATALOG, (
        "artemisia_gentileschi not found in CATALOG")


def test_artemisia_gentileschi_style_retrieval():
    """get_style('artemisia_gentileschi') must return an ArtStyle without raising."""
    s = get_style("artemisia_gentileschi")
    assert s is not None


def test_artemisia_gentileschi_movement():
    """Movement must reference Baroque."""
    s = get_style("artemisia_gentileschi")
    assert "baroque" in s.movement.lower() or "Baroque" in s.movement, (
        f"Expected Baroque in movement, got {s.movement!r}")


def test_artemisia_gentileschi_nationality():
    """Gentileschi was Italian."""
    s = get_style("artemisia_gentileschi")
    assert "italian" in s.nationality.lower(), (
        f"Expected Italian nationality, got {s.nationality!r}")


def test_artemisia_gentileschi_palette_length():
    """Palette should have at least 6 entries covering flesh, shadow, and drapery."""
    s = get_style("artemisia_gentileschi")
    assert len(s.palette) >= 6, (
        f"Gentileschi palette should have at least 6 entries, got {len(s.palette)}")


def test_artemisia_gentileschi_palette_values_in_range():
    """All Gentileschi palette RGB values must be in [0, 1]."""
    s = get_style("artemisia_gentileschi")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Gentileschi palette {rgb}")


def test_artemisia_gentileschi_dark_ground():
    """Gentileschi worked alla prima on a dark warm brown ground."""
    s = get_style("artemisia_gentileschi")
    mean_ground = sum(s.ground_color) / 3
    assert mean_ground < 0.35, (
        f"Gentileschi ground should be dark (mean < 0.35), got {mean_ground:.3f}")


def test_artemisia_gentileschi_has_glazing():
    """Gentileschi used warm amber oil glazes — glazing should not be None."""
    s = get_style("artemisia_gentileschi")
    assert s.glazing is not None, "Gentileschi should have a warm glazing colour"


def test_artemisia_gentileschi_glazing_warm():
    """Glazing should be warm amber (R > G > B)."""
    s = get_style("artemisia_gentileschi")
    r, g, b = s.glazing
    assert r >= g, (
        f"Gentileschi glaze should be warm (R ≥ G), got ({r:.2f},{g:.2f},{b:.2f})")


def test_artemisia_gentileschi_crackle_true():
    """17th-century oil on canvas — crackle must be True."""
    s = get_style("artemisia_gentileschi")
    assert s.crackle, "Gentileschi's aged canvas should have crackle=True"


def test_artemisia_gentileschi_famous_works_include_judith():
    """Judith Slaying Holofernes must be in Gentileschi's famous works."""
    s = get_style("artemisia_gentileschi")
    titles = [w[0] for w in s.famous_works]
    assert any("Judith" in t for t in titles), (
        "Gentileschi famous works should include Judith Slaying Holofernes")


def test_artemisia_gentileschi_famous_works_count():
    """Gentileschi should have at least 4 famous works documented."""
    s = get_style("artemisia_gentileschi")
    assert len(s.famous_works) >= 4, (
        f"Gentileschi should have at least 4 famous works, got {len(s.famous_works)}")


def test_artemisia_gentileschi_inspiration_references_chiaroscuro_focus():
    """Inspiration text must reference chiaroscuro_focus_pass."""
    s = get_style("artemisia_gentileschi")
    assert "chiaroscuro_focus" in s.inspiration.lower().replace(" ", "_"), (
        "Gentileschi inspiration should reference chiaroscuro_focus_pass()")


def test_artemisia_gentileschi_moderate_wet_blend():
    """Gentileschi's smooth flesh requires moderate wet_blend (not too high, not zero)."""
    s = get_style("artemisia_gentileschi")
    assert 0.10 <= s.wet_blend <= 0.40, (
        f"Gentileschi wet_blend should be moderate; got {s.wet_blend}")


def test_artemisia_gentileschi_moderate_edge_softness():
    """Light melts into shadow — edge_softness should be moderate (0.40–0.75)."""
    s = get_style("artemisia_gentileschi")
    assert 0.40 <= s.edge_softness <= 0.75, (
        f"Gentileschi edge_softness should be moderate; got {s.edge_softness}")


def test_jan_van_eyck_inspiration_references_micro_detail():
    """Inspiration text must reference micro_detail_pass."""
    s = get_style("jan_van_eyck")
    assert "micro_detail" in s.inspiration.lower().replace(" ", "_"), (
        "jan_van_eyck inspiration should reference micro_detail_pass()")


# ──────────────────────────────────────────────────────────────────────────────
# EARLY_NETHERLANDISH period (session 18)
# ──────────────────────────────────────────────────────────────────────────────

def test_early_netherlandish_period_present():
    """EARLY_NETHERLANDISH must exist in Period enum (session 18)."""
    assert hasattr(Period, "EARLY_NETHERLANDISH"), "Period.EARLY_NETHERLANDISH not found"
    assert Period.EARLY_NETHERLANDISH in list(Period)


def test_early_netherlandish_stroke_params_moderate_wet_blend():
    """EARLY_NETHERLANDISH wet_blend should be moderate (glazing requires blending)."""
    style = Style(medium=Medium.OIL, period=Period.EARLY_NETHERLANDISH,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.35 <= p["wet_blend"] <= 0.75, (
        f"EARLY_NETHERLANDISH wet_blend should be moderate, got {p['wet_blend']}")


def test_early_netherlandish_stroke_params_moderate_edge_softness():
    """EARLY_NETHERLANDISH edge_softness should be moderate (glazed but not sfumato)."""
    style = Style(medium=Medium.OIL, period=Period.EARLY_NETHERLANDISH,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.30 <= p["edge_softness"] <= 0.65, (
        f"EARLY_NETHERLANDISH edge_softness should be moderate; got {p['edge_softness']}")


def test_early_netherlandish_stroke_params_small_face_stroke():
    """EARLY_NETHERLANDISH stroke_size_face should be very small — Flemish micro-detail."""
    style = Style(medium=Medium.OIL, period=Period.EARLY_NETHERLANDISH,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] <= 6, (
        f"EARLY_NETHERLANDISH stroke_size_face should be small (fine Flemish detail), "
        f"got {p['stroke_size_face']}")


def test_early_netherlandish_stroke_params_all_keys_present():
    """EARLY_NETHERLANDISH stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.EARLY_NETHERLANDISH,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"EARLY_NETHERLANDISH stroke_params missing key: {key!r}"


# ──────────────────────────────────────────────────────────────────────────────
# Eugène Delacroix — session 20 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_delacroix_in_catalog():
    """Delacroix (session 20) must be present in CATALOG."""
    assert "delacroix" in CATALOG


def test_delacroix_artist_name():
    s = get_style("delacroix")
    assert "Delacroix" in s.artist


def test_delacroix_movement_contains_romanticism():
    """Delacroix's movement must reference French Romanticism or Colorism."""
    s = get_style("delacroix")
    movement_lower = s.movement.lower()
    assert "romant" in movement_lower or "coloris" in movement_lower or "colour" in movement_lower


def test_delacroix_palette_length():
    """Delacroix catalog entry must have at least 6 palette colours."""
    s = get_style("delacroix")
    assert len(s.palette) >= 6


def test_delacroix_palette_values_in_range():
    """All Delacroix palette RGB values must be in [0, 1]."""
    s = get_style("delacroix")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Delacroix palette {rgb}")


def test_delacroix_ground_color_valid():
    s = get_style("delacroix")
    assert len(s.ground_color) == 3
    for ch in s.ground_color:
        assert 0.0 <= ch <= 1.0


def test_delacroix_ground_color_is_dark_warm():
    """Delacroix painted on a warm dark umber ground."""
    s = get_style("delacroix")
    r, g, b = s.ground_color
    # Warm: red channel dominates over blue
    assert r > b, "Delacroix ground should be warmer (R > B)"
    # Dark: luminance below 0.60
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum < 0.60, f"Delacroix ground should be relatively dark; lum={lum:.3f}"


def test_delacroix_wet_blend_moderate():
    """Delacroix's alla prima wet_blend should be moderate (vigorous wet-into-wet)."""
    s = get_style("delacroix")
    assert 0.20 <= s.wet_blend <= 0.55, (
        f"Delacroix wet_blend expected moderate; got {s.wet_blend}")


def test_delacroix_has_glazing():
    """Delacroix used a warm amber final glaze to unify the surface."""
    s = get_style("delacroix")
    assert s.glazing is not None
    assert len(s.glazing) == 3
    for ch in s.glazing:
        assert 0.0 <= ch <= 1.0


def test_delacroix_crackle_true():
    """Delacroix's 19th-century oil canvases show craquelure — crackle should be True."""
    s = get_style("delacroix")
    assert s.crackle is True


def test_delacroix_famous_works_present():
    """Delacroix catalog entry must include his major paintings."""
    s = get_style("delacroix")
    titles = [title for title, _ in s.famous_works]
    assert any("Liberty" in t for t in titles), "Missing 'Liberty Leading the People'"
    assert any("Sardanapalus" in t or "Sardanapale" in t for t in titles), (
        "Missing 'Death of Sardanapalus'")


def test_delacroix_in_expected_artists_list():
    """EXPECTED_ARTISTS list must include delacroix."""
    assert "delacroix" in EXPECTED_ARTISTS


# ──────────────────────────────────────────────────────────────────────────────
# Edouard Vuillard — Nabis / Intimiste addition
# ──────────────────────────────────────────────────────────────────────────────

def test_vuillard_in_catalog():
    """Vuillard must be present in CATALOG."""
    assert "vuillard" in CATALOG


def test_vuillard_movement():
    s = get_style("vuillard")
    assert ("Nabi" in s.movement or "Intimis" in s.movement
            or "Post-Impressionist" in s.movement)


def test_vuillard_palette_length():
    s = get_style("vuillard")
    assert len(s.palette) >= 6, "Vuillard palette should have at least 6 key colours"


def test_vuillard_palette_values_in_range():
    """All Vuillard palette RGB values must be in [0, 1]."""
    s = get_style("vuillard")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Vuillard palette {rgb}")


def test_vuillard_wet_blend_low():
    """Vuillard's chalky matte technique is flat -- wet_blend must be low."""
    s = get_style("vuillard")
    assert s.wet_blend <= 0.20, (
        f"Vuillard wet_blend should be low (chalky flat zones), got {s.wet_blend}")


def test_vuillard_no_glaze():
    """Vuillard's Intimiste surfaces are matte -- no unifying glaze."""
    s = get_style("vuillard")
    assert s.glazing is None, "Vuillard should have no glaze (matte distemper surface)"


def test_vuillard_no_crackle():
    """Vuillard worked on cardboard and paper -- crackle should be False."""
    s = get_style("vuillard")
    assert s.crackle is False, "Vuillard crackle should be False (cardboard/paper support)"


def test_vuillard_famous_works_not_empty():
    s = get_style("vuillard")
    assert len(s.famous_works) >= 3, "Vuillard should have at least 3 famous works"


# ──────────────────────────────────────────────────────────────────────────────
# NABIS period -- stroke_params coverage
# ──────────────────────────────────────────────────────────────────────────────

def test_nabis_period_present():
    """NABIS must exist in Period enum."""
    assert hasattr(Period, "NABIS"), "Period.NABIS not found"
    assert Period.NABIS in list(Period)


def test_nabis_stroke_params_all_keys_present():
    """NABIS stroke_params must contain all four required keys."""
    style = Style(medium=Medium.OIL, period=Period.NABIS, palette=PaletteHint.MUTED)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"NABIS stroke_params missing key: {key!r}"


def test_nabis_stroke_params_values():
    """NABIS should have low wet_blend (chalky flat zones) and equal face/bg strokes."""
    style = Style(medium=Medium.OIL, period=Period.NABIS, palette=PaletteHint.MUTED)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.20, (
        f"NABIS wet_blend should be low for chalky flat zones; got {p['wet_blend']}")
    # Face and background strokes should be similar (Intimisme dissolves figure into ground)
    assert abs(p["stroke_size_face"] - p["stroke_size_bg"]) <= 4, (
        f"NABIS face and bg stroke sizes should be close; "
        f"face={p['stroke_size_face']} bg={p['stroke_size_bg']}")


# ──────────────────────────────────────────────────────────────────────────────
# Sorolla / LUMINISMO — Luminismo addition
# ──────────────────────────────────────────────────────────────────────────────

def test_sorolla_in_catalog():
    """Sorolla must be present in CATALOG."""
    assert "sorolla" in CATALOG


def test_sorolla_movement():
    s = get_style("sorolla")
    assert "Luminismo" in s.movement or "luminismo" in s.movement.lower()


def test_sorolla_palette_length():
    s = get_style("sorolla")
    assert len(s.palette) >= 6, "Sorolla palette must include at least 6 colours"


def test_sorolla_palette_values_in_range():
    """All Sorolla palette RGB values must be in [0, 1]."""
    s = get_style("sorolla")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Sorolla palette {rgb}")


def test_sorolla_ground_color_valid():
    s = get_style("sorolla")
    assert len(s.ground_color) == 3
    for ch in s.ground_color:
        assert 0.0 <= ch <= 1.0


def test_sorolla_has_no_glazing():
    """Sorolla uses no unifying glaze — brilliance is the point."""
    s = get_style("sorolla")
    assert s.glazing is None, "Sorolla should have no unifying glaze"


def test_sorolla_famous_works_not_empty():
    s = get_style("sorolla")
    assert len(s.famous_works) >= 3, "Sorolla should have at least 3 famous works"


def test_sorolla_high_jitter():
    """Sorolla's vibrant optical mix requires higher jitter than most styles."""
    s = get_style("sorolla")
    assert s.jitter >= 0.04, (
        f"Sorolla jitter should be >= 0.04 for vibrant optical mixing; got {s.jitter}")


def test_sorolla_get_style_by_key():
    s = get_style("sorolla")
    assert "Sorolla" in s.artist


def test_luminismo_period_present():
    """LUMINISMO must exist in Period enum."""
    assert hasattr(Period, "LUMINISMO"), "Period.LUMINISMO not found"
    assert Period.LUMINISMO in list(Period)


def test_luminismo_stroke_params_values():
    """LUMINISMO should have moderate wet_blend (lively but not muddy) and moderate edge_softness."""
    style = Style(medium=Medium.OIL, period=Period.LUMINISMO,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    # Moderate wet_blend: outdoor strokes are fluid but not muddied
    assert 0.25 <= p["wet_blend"] <= 0.55, (
        f"LUMINISMO wet_blend should be moderate; got {p['wet_blend']}")
    # Moderate edge_softness: Mediterranean forms are clear, not sfumatoed
    assert 0.25 <= p["edge_softness"] <= 0.65, (
        f"LUMINISMO edge_softness should be moderate; got {p['edge_softness']}")


def test_luminismo_stroke_params_all_keys_present():
    """LUMINISMO stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.LUMINISMO,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"LUMINISMO stroke_params missing key: {key!r}"
