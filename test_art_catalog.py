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
    "anders_zorn",
    "artemisia_gentileschi",
    "berthe_morisot",
    "waterhouse",
    "bouguereau",
    "bruegel",
    "caravaggio", "caspar_david_friedrich", "cezanne",
    "chardin", "courbet",
    "degas",
    "delacroix",
    "egon_schiele",
    "el_greco", "frida_kahlo", "gauguin", "goya", "hilma_af_klint", "hokusai",
    "georges_de_la_tour",
    "ingres",
    "jan_van_eyck",
    "kandinsky",
    "klimt", "leonardo", "manet", "mary_cassatt", "matisse", "modigliani", "monet",
    "piero_della_francesca",
    "raphael",
    "rembrandt",
    "rothko", "sargent", "seurat", "sorolla", "tamara_de_lempicka", "titian", "turner",
    "van_gogh", "velazquez", "vermeer",
    "vuillard",
    "gustave_moreau",
    "zurbaran",
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
    "ART_DECO",
    "NABIS", "LUMINISMO",
    "HIGH_RENAISSANCE",
    "TENEBRIST",
    "NEOCLASSICAL",
    "NOCTURNE",
    "FRENCH_NATURALIST",
    "SOCIAL_REALIST",
    "ACADEMIC_REALIST",
    "IMPRESSIONIST_INTIMISTE",
    "CONTEMPORARY", "FANTASY_ART", "NONE",
    "PRE_RAPHAELITE",
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
# Session 22: Tamara de Lempicka — Art Deco figurative portraiture
# ──────────────────────────────────────────────────────────────────────────────

def test_tamara_de_lempicka_in_catalog():
    """Session 22: tamara_de_lempicka must be present in CATALOG."""
    assert "tamara_de_lempicka" in CATALOG, (
        "tamara_de_lempicka not found in CATALOG after session 22")


def test_tamara_de_lempicka_movement():
    """de Lempicka's movement must reference Art Deco."""
    s = get_style("tamara_de_lempicka")
    assert "Art Deco" in s.movement or "art deco" in s.movement.lower(), (
        f"Expected 'Art Deco' in movement, got: {s.movement!r}")


def test_tamara_de_lempicka_nationality():
    s = get_style("tamara_de_lempicka")
    assert "Polish" in s.nationality or "French" in s.nationality, (
        f"Expected Polish or French in nationality, got: {s.nationality!r}")


def test_tamara_de_lempicka_palette_length():
    s = get_style("tamara_de_lempicka")
    assert len(s.palette) >= 6, (
        f"de Lempicka palette should have at least 6 colours, got {len(s.palette)}")


def test_tamara_de_lempicka_palette_in_range():
    """All de Lempicka palette RGB values must be in [0, 1]."""
    s = get_style("tamara_de_lempicka")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"Out-of-range channel {ch} in de Lempicka palette {rgb}")


def test_tamara_de_lempicka_low_wet_blend():
    """de Lempicka has a polished, lacquered surface — wet_blend should be low."""
    s = get_style("tamara_de_lempicka")
    assert s.wet_blend <= 0.15, (
        f"de Lempicka wet_blend should be low (polished surface); got {s.wet_blend}")


def test_tamara_de_lempicka_low_edge_softness():
    """de Lempicka has crisp Art Deco edges — edge_softness should be low."""
    s = get_style("tamara_de_lempicka")
    assert s.edge_softness <= 0.15, (
        f"de Lempicka edge_softness should be low (hard contour lines); "
        f"got {s.edge_softness}")


def test_tamara_de_lempicka_no_glaze():
    """de Lempicka's lacquered surface is final — no unifying glaze expected."""
    s = get_style("tamara_de_lempicka")
    assert s.glazing is None, (
        f"de Lempicka should have no unifying glaze, got: {s.glazing}")


def test_tamara_de_lempicka_no_crackle():
    """de Lempicka's 1920s–1940s paintings should not have crackle ageing."""
    s = get_style("tamara_de_lempicka")
    assert s.crackle is False, (
        "de Lempicka crackle should be False (modern canvas)")


def test_tamara_de_lempicka_famous_works():
    """de Lempicka should have at least three famous works listed."""
    s = get_style("tamara_de_lempicka")
    assert len(s.famous_works) >= 3, (
        f"de Lempicka should have at least 3 famous works, got {len(s.famous_works)}")


def test_tamara_de_lempicka_technique_non_empty():
    s = get_style("tamara_de_lempicka")
    assert s.technique, "de Lempicka technique description should not be empty"
    assert len(s.technique) > 50, (
        "de Lempicka technique description should be substantive")


def test_art_deco_period_present():
    """Session 22: ART_DECO must exist in Period enum."""
    assert hasattr(Period, "ART_DECO"), "Period.ART_DECO not found"
    assert Period.ART_DECO in list(Period)


def test_art_deco_stroke_params_all_keys():
    """ART_DECO stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.ART_DECO,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"ART_DECO stroke_params missing key: {key!r}"


def test_art_deco_stroke_params_low_wet_blend():
    """ART_DECO wet_blend should be very low — polished lacquered surface."""
    style = Style(medium=Medium.OIL, period=Period.ART_DECO,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.12, (
        f"ART_DECO wet_blend should be very low (lacquered Art Deco); got {p['wet_blend']}")


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
    assert "vuillard" in CATALOG, "vuillard not found in CATALOG"


def test_vuillard_style_retrieval():
    """get_style('vuillard') must return an ArtStyle without raising."""
    s = get_style("vuillard")
    assert s is not None


def test_vuillard_movement():
    """Vuillard's movement must reference Nabis or Post-Impressionism."""
    s = get_style("vuillard")
    assert ("Nabi" in s.movement or "Intimis" in s.movement
            or "Post-Impressionist" in s.movement)


def test_vuillard_nationality():
    """Vuillard was French."""
    s = get_style("vuillard")
    assert "french" in s.nationality.lower(), (
        f"Vuillard nationality should be French; got {s.nationality!r}")


def test_vuillard_palette_length():
    """Palette should have at least 6 entries covering tapestry-like domestic tones."""
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


def test_vuillard_palette_has_warm_dusty_rose():
    """Vuillard palette must include a warm dusty rose/pink."""
    s = get_style("vuillard")
    has_rose = any(r > 0.60 and b > 0.35 and r > g for r, g, b in s.palette)
    assert has_rose, "Vuillard palette should include a warm dusty rose or pink"


def test_vuillard_palette_has_olive_green():
    """Vuillard palette must include a muted olive or green."""
    s = get_style("vuillard")
    has_green = any(g > 0.35 and g >= r and g > b for r, g, b in s.palette)
    assert has_green, "Vuillard palette should include a muted olive or green"


def test_vuillard_ground_warm():
    """Vuillard warm buff ground should have R > B."""
    s = get_style("vuillard")
    r, g, b = s.ground_color
    assert r > b, f"Vuillard ground should be warm (R > B), got R={r:.2f} B={b:.2f}"


def test_vuillard_wet_blend_low():
    """Vuillard's chalky matte technique is flat -- wet_blend must be low."""
    s = get_style("vuillard")
    assert s.wet_blend <= 0.30, (
        f"Vuillard wet_blend should be low (chalky flat zones), got {s.wet_blend}")


def test_vuillard_no_glaze():
    """Vuillard Intimiste surfaces are matte -- no unifying glaze."""
    s = get_style("vuillard")
    assert s.glazing is None, "Vuillard should have no glaze (matte distemper surface)"


def test_vuillard_no_crackle():
    """Vuillard worked on cardboard and paper -- crackle should be False."""
    s = get_style("vuillard")
    assert s.crackle is False, "Vuillard crackle should be False (cardboard/paper support)"


def test_vuillard_famous_works_not_empty():
    s = get_style("vuillard")
    assert len(s.famous_works) >= 3, "Vuillard should have at least 3 famous works"


def test_vuillard_famous_works_include_intimiste():
    """Vuillard famous works should include an intimate interior scene."""
    s = get_style("vuillard")
    titles = [w[0] for w in s.famous_works]
    assert any("Mother" in t or "Interior" in t or "Suitor" in t or "Lunch" in t
               for t in titles), (
        "Vuillard famous works should include a domestic interior scene")


def test_vuillard_inspiration_references_intimiste_pattern():
    """Inspiration text must reference intimiste_pattern_pass."""
    s = get_style("vuillard")
    assert "intimiste_pattern" in s.inspiration.lower().replace(" ", "_"), (
        "Vuillard inspiration should reference intimiste_pattern_pass()")


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


# ──────────────────────────────────────────────────────────────────────────────
# Session 23: Raphael / HIGH_RENAISSANCE addition
# ──────────────────────────────────────────────────────────────────────────────

def test_raphael_in_catalog():
    """Session 23: Raphael must be present in CATALOG."""
    assert "raphael" in CATALOG, "raphael not found in CATALOG"


def test_raphael_movement():
    """Raphael entry must identify as High Renaissance."""
    s = get_style("raphael")
    assert "Renaissance" in s.movement or "renaissance" in s.movement.lower(), (
        f"Raphael movement should contain 'Renaissance'; got {s.movement!r}")


def test_raphael_palette_length():
    """Raphael palette must have at least 7 colours."""
    s = get_style("raphael")
    assert len(s.palette) >= 7, (
        f"Raphael palette should have ≥7 colours; got {len(s.palette)}")


def test_raphael_palette_values_in_range():
    """All Raphael palette RGB values must be in [0, 1]."""
    s = get_style("raphael")
    for i, col in enumerate(s.palette):
        for ch in col:
            assert 0.0 <= ch <= 1.0, (
                f"Raphael palette[{i}] channel out of range: {col}")


def test_raphael_wet_blend_in_range():
    """Raphael wet_blend must be in a moderate range (forms rounded but not sfumato)."""
    s = get_style("raphael")
    assert 0.20 <= s.wet_blend <= 0.55, (
        f"Raphael wet_blend should be moderate; got {s.wet_blend}")


def test_raphael_edge_softness_in_range():
    """Raphael edge_softness must be moderate (clear forms, not sfumato-dissolved)."""
    s = get_style("raphael")
    assert 0.40 <= s.edge_softness <= 0.75, (
        f"Raphael edge_softness should be moderate; got {s.edge_softness}")


def test_raphael_glazing_is_warm():
    """Raphael glazing should be warm (golden amber tonality)."""
    s = get_style("raphael")
    assert s.glazing is not None, "Raphael should have a warm unifying glaze"
    r, g, b = s.glazing
    assert r > b, (
        f"Raphael glaze should be warm (R>B); got R={r:.2f} B={b:.2f}")


def test_raphael_famous_works_contains_school_of_athens():
    """Raphael famous_works must include School of Athens."""
    s = get_style("raphael")
    titles = [w[0] for w in s.famous_works]
    assert any("Athens" in t or "Sistine" in t for t in titles), (
        f"Raphael famous_works should include School of Athens or Sistine Madonna; got {titles}")


def test_high_renaissance_period_present():
    """Session 23: HIGH_RENAISSANCE must exist in Period enum."""
    assert hasattr(Period, "HIGH_RENAISSANCE"), "Period.HIGH_RENAISSANCE not found"
    assert Period.HIGH_RENAISSANCE in list(Period)


def test_high_renaissance_stroke_params_all_keys():
    """HIGH_RENAISSANCE stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.HIGH_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"HIGH_RENAISSANCE stroke_params missing key: {key!r}"


def test_high_renaissance_wet_blend():
    """HIGH_RENAISSANCE wet_blend should be moderate — softer than Baroque, less extreme than Leonardo."""
    style = Style(medium=Medium.OIL, period=Period.HIGH_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.20 <= p["wet_blend"] <= 0.55, (
        f"HIGH_RENAISSANCE wet_blend should be moderate; got {p['wet_blend']}")


def test_high_renaissance_edge_softness():
    """HIGH_RENAISSANCE edge_softness must be clear but rounded — no sfumato haze."""
    style = Style(medium=Medium.OIL, period=Period.HIGH_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.40 <= p["edge_softness"] <= 0.75, (
        f"HIGH_RENAISSANCE edge_softness should be moderate; got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Francisco de Zurbarán / Tenebrist Baroque — session 24
# ──────────────────────────────────────────────────────────────────────────────

def test_zurbaran_in_catalog():
    """Zurbarán (session 24) must be in the catalog."""
    assert "zurbaran" in CATALOG


def test_zurbaran_movement():
    s = get_style("zurbaran")
    assert "tenebr" in s.movement.lower() or "baroque" in s.movement.lower(), (
        f"Zurbarán movement should be Tenebrist/Baroque; got {s.movement!r}")


def test_zurbaran_nationality():
    s = get_style("zurbaran")
    assert "spanish" in s.nationality.lower(), (
        f"Zurbarán should be Spanish; got {s.nationality!r}")


def test_zurbaran_palette_length():
    s = get_style("zurbaran")
    assert len(s.palette) >= 6, (
        f"Zurbarán palette should have ≥ 6 colours; got {len(s.palette)}")


def test_zurbaran_palette_values_in_range():
    """All Zurbarán palette RGB values must be in [0, 1]."""
    s = get_style("zurbaran")
    for i, col in enumerate(s.palette):
        for ch in col:
            assert 0.0 <= ch <= 1.0, (
                f"Zurbarán palette[{i}] channel out of range: {ch}")


def test_zurbaran_dark_ground():
    """Zurbarán used a very dark ground — ground_color luminance must be very low."""
    s = get_style("zurbaran")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum <= 0.20, (
        f"Zurbarán ground should be near-black (lum ≤ 0.20); got {lum:.3f}")


def test_zurbaran_low_wet_blend():
    """Zurbarán worked in precise, deliberate strokes — wet_blend must be low."""
    s = get_style("zurbaran")
    assert s.wet_blend <= 0.35, (
        f"Zurbarán wet_blend should be low (precise technique); got {s.wet_blend}")


def test_zurbaran_low_edge_softness():
    """Zurbarán's crisp fabric edges — edge_softness must be low."""
    s = get_style("zurbaran")
    assert s.edge_softness <= 0.40, (
        f"Zurbarán edge_softness should be low (crisp found edges); got {s.edge_softness}")


def test_zurbaran_crackle():
    """Zurbarán worked on 17th-century canvas — crackle should be True."""
    s = get_style("zurbaran")
    assert s.crackle, "Zurbarán crackle should be True (17th-century technique)"


def test_zurbaran_no_glazing():
    """Zurbarán's austere technique required no warm unifying glaze."""
    s = get_style("zurbaran")
    assert s.glazing is None, "Zurbarán glazing should be None (monastic austerity)"


def test_zurbaran_palette_has_near_white():
    """Zurbarán's defining tone is brilliant near-white cloth."""
    s = get_style("zurbaran")
    # At least one colour in the palette should be near-white (lum > 0.85)
    has_white = any(0.299 * r + 0.587 * g + 0.114 * b > 0.85
                    for r, g, b in s.palette)
    assert has_white, "Zurbarán palette must contain a near-white colour for brilliant cloth"


def test_zurbaran_palette_has_near_black():
    """Zurbarán's void background requires a near-black in the palette."""
    s = get_style("zurbaran")
    has_black = any(0.299 * r + 0.587 * g + 0.114 * b < 0.10
                    for r, g, b in s.palette)
    assert has_black, "Zurbarán palette must contain a near-black for the void background"


def test_zurbaran_famous_works_non_empty():
    s = get_style("zurbaran")
    assert len(s.famous_works) >= 3, (
        f"Zurbarán should have ≥ 3 famous works listed; got {len(s.famous_works)}")


def test_tenebrist_period_present():
    """Session 24: TENEBRIST must exist in Period enum."""
    assert hasattr(Period, "TENEBRIST"), "Period.TENEBRIST not found"
    assert Period.TENEBRIST in list(Period)


def test_tenebrist_stroke_params_all_keys():
    """TENEBRIST stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.TENEBRIST,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"TENEBRIST stroke_params missing key: {key!r}"


def test_tenebrist_low_wet_blend():
    """TENEBRIST wet_blend must be low — precise, deliberate strokes."""
    style = Style(medium=Medium.OIL, period=Period.TENEBRIST,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.35, (
        f"TENEBRIST wet_blend should be low; got {p['wet_blend']}")


def test_tenebrist_low_edge_softness():
    """TENEBRIST edge_softness must be low — crisp fabric-void edges."""
    style = Style(medium=Medium.OIL, period=Period.TENEBRIST,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] <= 0.40, (
        f"TENEBRIST edge_softness should be low; got {p['edge_softness']}")


def test_tenebrist_large_bg_stroke():
    """TENEBRIST stroke_size_bg should be large — void needs few, vast dark strokes."""
    style = Style(medium=Medium.OIL, period=Period.TENEBRIST,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["stroke_size_bg"] >= 30, (
        f"TENEBRIST stroke_size_bg should be ≥ 30 (void background); got {p['stroke_size_bg']}")


# ──────────────────────────────────────────────────────────────────────────────
# Session 25: Ingres / NEOCLASSICAL addition
# ──────────────────────────────────────────────────────────────────────────────

def test_ingres_in_catalog():
    """Session 25: Ingres must be in the art catalog."""
    assert "ingres" in CATALOG, "ingres missing from CATALOG"


def test_ingres_artist_field():
    s = get_style("ingres")
    assert "Ingres" in s.artist


def test_ingres_movement():
    s = get_style("ingres")
    assert "Neoclassic" in s.movement or "Academic" in s.movement


def test_ingres_palette_length():
    s = get_style("ingres")
    assert len(s.palette) >= 6, (
        f"Ingres palette should have ≥ 6 colours; got {len(s.palette)}")


def test_ingres_palette_values_in_range():
    """All Ingres palette RGB values must be in [0, 1]."""
    s = get_style("ingres")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Ingres palette {rgb}")


def test_ingres_ground_color_valid():
    s = get_style("ingres")
    assert len(s.ground_color) == 3
    for ch in s.ground_color:
        assert 0.0 <= ch <= 1.0


def test_ingres_ground_is_warm():
    """Ingres used a warm ivory-buff ground — R should exceed B."""
    s = get_style("ingres")
    r, g, b = s.ground_color
    assert r > b, f"Ingres ground should be warm (R > B); got R={r:.2f} B={b:.2f}"


def test_ingres_edge_softness_moderate():
    """Ingres: classical clarity — edge_softness should be moderate, not sfumatoed."""
    s = get_style("ingres")
    assert 0.20 <= s.edge_softness <= 0.55, (
        f"Ingres edge_softness should be moderate; got {s.edge_softness}")


def test_ingres_has_glazing():
    """Ingres used a unifying warm ivory glaze."""
    s = get_style("ingres")
    assert s.glazing is not None, "Ingres should have a glazing colour set"


def test_ingres_crackle_true():
    s = get_style("ingres")
    assert s.crackle is True, "Ingres crackle should be True (aged canvas)"


def test_ingres_famous_works_non_empty():
    s = get_style("ingres")
    assert len(s.famous_works) >= 3, (
        f"Ingres should have ≥ 3 famous works listed; got {len(s.famous_works)}")


def test_ingres_period_dates():
    """Ingres' active period should contain 1800."""
    s = get_style("ingres")
    assert "1800" in s.period or "180" in s.period, (
        f"Ingres period dates should include 1800s; got {s.period!r}")


def test_neoclassical_period_present():
    """Session 25: NEOCLASSICAL must exist in Period enum."""
    assert hasattr(Period, "NEOCLASSICAL"), "Period.NEOCLASSICAL not found"
    assert Period.NEOCLASSICAL in list(Period)


def test_neoclassical_stroke_params_all_keys():
    """NEOCLASSICAL stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.NEOCLASSICAL,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"NEOCLASSICAL stroke_params missing key: {key!r}"


def test_neoclassical_small_face_stroke():
    """NEOCLASSICAL stroke_size_face should be small — fine flesh modelling."""
    style = Style(medium=Medium.OIL, period=Period.NEOCLASSICAL,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] <= 8, (
        f"NEOCLASSICAL stroke_size_face should be small (fine detail); got {p['stroke_size_face']}")


def test_neoclassical_moderate_wet_blend():
    """NEOCLASSICAL wet_blend should be moderate — smooth flesh transitions."""
    style = Style(medium=Medium.OIL, period=Period.NEOCLASSICAL,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.15 <= p["wet_blend"] <= 0.55, (
        f"NEOCLASSICAL wet_blend should be moderate; got {p['wet_blend']}")


def test_neoclassical_moderate_edge_softness():
    """NEOCLASSICAL edge_softness should be moderate — classical clarity, not sfumato."""
    style = Style(medium=Medium.OIL, period=Period.NEOCLASSICAL,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.20 <= p["edge_softness"] <= 0.55, (
        f"NEOCLASSICAL edge_softness should be moderate; got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Georges de La Tour — nocturne candlelight addition
# ──────────────────────────────────────────────────────────────────────────────

def test_georges_de_la_tour_in_catalog():
    """Georges de La Tour must be present in CATALOG."""
    assert "georges_de_la_tour" in CATALOG, "georges_de_la_tour not found in CATALOG"


def test_georges_de_la_tour_movement():
    """La Tour's movement must reference Baroque or Nocturne."""
    s = get_style("georges_de_la_tour")
    assert ("Baroque" in s.movement or "Nocturne" in s.movement
            or "nocturne" in s.movement.lower()), (
        f"La Tour movement should reference Baroque/Nocturne; got {s.movement!r}")


def test_georges_de_la_tour_nationality():
    s = get_style("georges_de_la_tour")
    assert "French" in s.nationality, (
        f"La Tour should be French; got {s.nationality!r}")


def test_georges_de_la_tour_palette_length():
    s = get_style("georges_de_la_tour")
    assert len(s.palette) >= 5, "La Tour palette should have at least 5 key colours"


def test_georges_de_la_tour_palette_values_in_range():
    """All La Tour palette RGB values must be in [0, 1]."""
    s = get_style("georges_de_la_tour")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in La Tour palette {rgb}")


def test_georges_de_la_tour_ground_dark():
    """La Tour's ground should be near-black — nocturnal starting point."""
    s = get_style("georges_de_la_tour")
    avg_ground = sum(s.ground_color) / 3
    assert avg_ground <= 0.15, (
        f"La Tour ground_color should be very dark; got avg={avg_ground:.3f}")


def test_georges_de_la_tour_glazing_warm():
    """La Tour's unifying glaze should be warm amber — candlelight tint."""
    s = get_style("georges_de_la_tour")
    assert s.glazing is not None, "La Tour should have a warm amber glaze"
    r, g, b = s.glazing
    assert r > g > b, (
        f"La Tour glazing should be warm amber (R > G > B); got ({r:.2f},{g:.2f},{b:.2f})")


def test_georges_de_la_tour_wet_blend_moderate():
    """La Tour's wet_blend should be moderate — smooth but not sfumato-heavy."""
    s = get_style("georges_de_la_tour")
    assert 0.35 <= s.wet_blend <= 0.75, (
        f"La Tour wet_blend should be moderate; got {s.wet_blend}")


def test_georges_de_la_tour_technique_mentions_candle():
    """La Tour's technique description must mention the candle light source."""
    s = get_style("georges_de_la_tour")
    text = s.technique.lower()
    assert "candle" in text or "nocturne" in text or "candlelight" in text, (
        f"La Tour technique should mention candlelight; got: {s.technique[:80]!r}")


def test_georges_de_la_tour_famous_works():
    s = get_style("georges_de_la_tour")
    assert len(s.famous_works) >= 3, "La Tour should have at least 3 famous works"
    titles = [w[0] for w in s.famous_works]
    assert any("Magdalene" in t or "Newborn" in t or "Joseph" in t
               for t in titles), (
        "La Tour's famous works should include at least one canonical nocturne")


# ──────────────────────────────────────────────────────────────────────────────
# Period.NOCTURNE — La Tour nocturne period enum
# ──────────────────────────────────────────────────────────────────────────────

def test_nocturne_period_present():
    """NOCTURNE must exist in the Period enum."""
    assert hasattr(Period, "NOCTURNE"), "Period.NOCTURNE not found"
    assert Period.NOCTURNE in list(Period)


def test_nocturne_stroke_params_all_keys():
    """NOCTURNE stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.NOCTURNE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"NOCTURNE stroke_params missing key: {key!r}"


def test_nocturne_large_bg_stroke():
    """NOCTURNE stroke_size_bg should be large — the void background needs sweeping dark strokes."""
    style = Style(medium=Medium.OIL, period=Period.NOCTURNE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["stroke_size_bg"] >= 35, (
        f"NOCTURNE stroke_size_bg should be large (void background); got {p['stroke_size_bg']}")


def test_nocturne_moderate_wet_blend():
    """NOCTURNE wet_blend should be moderate — smooth candlelit gradients."""
    style = Style(medium=Medium.OIL, period=Period.NOCTURNE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert 0.35 <= p["wet_blend"] <= 0.75, (
        f"NOCTURNE wet_blend should be moderate; got {p['wet_blend']}")


def test_nocturne_moderate_edge_softness():
    """NOCTURNE edge_softness should be moderate — soft penumbra, not sfumato."""
    style = Style(medium=Medium.OIL, period=Period.NOCTURNE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert 0.25 <= p["edge_softness"] <= 0.65, (
        f"NOCTURNE edge_softness should be moderate; got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Jean-Baptiste-Siméon Chardin — current session addition
# ──────────────────────────────────────────────────────────────────────────────

def test_chardin_in_catalog():
    """Chardin must be present in CATALOG."""
    assert "chardin" in CATALOG, "chardin not found in CATALOG"


def test_chardin_movement():
    """Chardin's movement must reference French Naturalism or Rococo."""
    s = get_style("chardin")
    m = s.movement.lower()
    assert "french" in m or "naturalism" in m or "rococo" in m, (
        f"Chardin movement should reference French Naturalism or Rococo; got: {s.movement!r}")


def test_chardin_nationality():
    """Chardin was French."""
    s = get_style("chardin")
    assert "french" in s.nationality.lower(), (
        f"Chardin nationality should be French; got: {s.nationality!r}")


def test_chardin_palette_length():
    """Chardin's palette should have at least 6 key colours (greys, ochres, warm whites)."""
    s = get_style("chardin")
    assert len(s.palette) >= 6, (
        f"Chardin palette should have ≥6 key colours; got {len(s.palette)}")


def test_chardin_palette_values_in_range():
    """All Chardin palette RGB values must be in [0, 1]."""
    s = get_style("chardin")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Chardin palette {rgb}")


def test_chardin_edge_softness_moderate():
    """Chardin's edges dissolve softly — edge_softness should be moderate (≥ 0.55)."""
    s = get_style("chardin")
    assert s.edge_softness >= 0.55, (
        f"Chardin edge_softness should be moderate for soft boundary dissolution; "
        f"got {s.edge_softness}")


def test_chardin_wet_blend_low():
    """Chardin built surfaces from distinct dry marks — wet_blend must be low (≤ 0.30)."""
    s = get_style("chardin")
    assert s.wet_blend <= 0.30, (
        f"Chardin wet_blend should be low (dry marks stay distinct); got {s.wet_blend}")


def test_chardin_no_chromatic_split():
    """Chardin does not use divisionist chromatic splitting."""
    s = get_style("chardin")
    assert not s.chromatic_split, "Chardin chromatic_split should be False"


def test_chardin_famous_works_not_empty():
    """Chardin should have at least 4 famous works documented."""
    s = get_style("chardin")
    assert len(s.famous_works) >= 4, (
        f"Chardin should have ≥4 famous works; got {len(s.famous_works)}")


def test_chardin_famous_works_include_known_painting():
    """Chardin's famous works should include at least one well-known piece."""
    s = get_style("chardin")
    titles = [w[0] for w in s.famous_works]
    assert any(
        "Ray" in t or "Raie" in t or "Top" in t or "Cards" in t or "Schoolmistress" in t
        for t in titles
    ), ("Chardin famous works should include at least one well-known still life or genre piece")


def test_chardin_inspiration_references_dry_granulation():
    """Chardin's inspiration text should reference dry_granulation_pass."""
    s = get_style("chardin")
    assert "dry_granulation" in s.inspiration.lower().replace(" ", "_"), (
        "Chardin inspiration should reference dry_granulation_pass()")


# ──────────────────────────────────────────────────────────────────────────────
# Period.FRENCH_NATURALIST — Chardin period enum
# ──────────────────────────────────────────────────────────────────────────────

def test_french_naturalist_period_present():
    """FRENCH_NATURALIST must exist in the Period enum."""
    assert hasattr(Period, "FRENCH_NATURALIST"), "Period.FRENCH_NATURALIST not found"
    assert Period.FRENCH_NATURALIST in list(Period)


def test_french_naturalist_stroke_params_all_keys():
    """FRENCH_NATURALIST stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.FRENCH_NATURALIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"FRENCH_NATURALIST stroke_params missing key: {key!r}"


def test_french_naturalist_small_stroke_face():
    """FRENCH_NATURALIST stroke_size_face should be small (≤ 7) for granular marks."""
    style = Style(medium=Medium.OIL, period=Period.FRENCH_NATURALIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] <= 7, (
        f"FRENCH_NATURALIST stroke_size_face should be small (≤7); "
        f"got {p['stroke_size_face']}")


def test_french_naturalist_low_wet_blend():
    """FRENCH_NATURALIST wet_blend should be low — dry marks stay distinct."""
    style = Style(medium=Medium.OIL, period=Period.FRENCH_NATURALIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.30, (
        f"FRENCH_NATURALIST wet_blend should be low; got {p['wet_blend']}")


def test_french_naturalist_moderate_edge_softness():
    """FRENCH_NATURALIST edge_softness should be moderate (≥ 0.50) — soft boundary dissolution."""
    style = Style(medium=Medium.OIL, period=Period.FRENCH_NATURALIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] >= 0.50, (
        f"FRENCH_NATURALIST edge_softness should be moderate (≥0.50); "
        f"got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Gustave Courbet — new addition: French Realism / palette knife technique
# ──────────────────────────────────────────────────────────────────────────────

def test_courbet_in_catalog():
    """Courbet must be present in CATALOG."""
    assert "courbet" in CATALOG


def test_courbet_movement():
    s = get_style("courbet")
    assert "Reali" in s.movement or "reali" in s.movement.lower()


def test_courbet_palette_length():
    s = get_style("courbet")
    assert len(s.palette) >= 5, "Courbet palette should have at least 5 key colours"


def test_courbet_palette_values_in_range():
    """All Courbet palette RGB values must be in [0, 1]."""
    s = get_style("courbet")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Courbet palette {rgb}")


def test_courbet_ground_color_dark():
    """Courbet's ground_color should be dark (all channels < 0.25) — bituminous base."""
    s = get_style("courbet")
    for ch in s.ground_color:
        assert ch < 0.25, (
            f"Courbet ground_color channel {ch:.3f} should be dark (< 0.25)")


def test_courbet_wet_blend_low():
    """Courbet's palette knife technique leaves flat planes — wet_blend must be low."""
    s = get_style("courbet")
    assert s.wet_blend <= 0.30, (
        f"Courbet wet_blend should be low (flat knife planes); got {s.wet_blend}")


def test_courbet_edge_softness_low():
    """Palette knife leaves crisp edges — edge_softness must be low."""
    s = get_style("courbet")
    assert s.edge_softness <= 0.40, (
        f"Courbet edge_softness should be low (knife hard edges); got {s.edge_softness}")


def test_courbet_large_stroke_size():
    """Courbet's knife covers broad areas — stroke_size should be large (≥ 10)."""
    s = get_style("courbet")
    assert s.stroke_size >= 10, (
        f"Courbet stroke_size should be large (palette knife); got {s.stroke_size}")


def test_courbet_famous_works_not_empty():
    s = get_style("courbet")
    assert len(s.famous_works) >= 3, "Courbet should have at least 3 famous works"
    titles = [w[0] for w in s.famous_works]
    assert any("Stone" in t or "Burial" in t or "Origin" in t or "Studio" in t
               for t in titles), (
        "Courbet famous works should include at least one iconic work")


def test_courbet_inspiration_references_palette_knife():
    """Courbet's inspiration text should reference palette_knife_pass."""
    s = get_style("courbet")
    assert "palette_knife" in s.inspiration.lower().replace(" ", "_"), (
        "Courbet inspiration should reference palette_knife_pass()")


# ──────────────────────────────────────────────────────────────────────────────
# Period.SOCIAL_REALIST — Courbet period enum
# ──────────────────────────────────────────────────────────────────────────────

def test_social_realist_period_present():
    """SOCIAL_REALIST must exist in the Period enum."""
    assert hasattr(Period, "SOCIAL_REALIST"), "Period.SOCIAL_REALIST not found"
    assert Period.SOCIAL_REALIST in list(Period)


def test_social_realist_stroke_params_all_keys():
    """SOCIAL_REALIST stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.SOCIAL_REALIST,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"SOCIAL_REALIST stroke_params missing key: {key!r}"


def test_social_realist_large_stroke_face():
    """SOCIAL_REALIST stroke_size_face should be large (≥ 10) — palette knife planes."""
    style = Style(medium=Medium.OIL, period=Period.SOCIAL_REALIST,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] >= 10, (
        f"SOCIAL_REALIST stroke_size_face should be large (≥10); "
        f"got {p['stroke_size_face']}")


def test_social_realist_low_wet_blend():
    """SOCIAL_REALIST wet_blend should be low — knife planes don't blend."""
    style = Style(medium=Medium.OIL, period=Period.SOCIAL_REALIST,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.30, (
        f"SOCIAL_REALIST wet_blend should be low; got {p['wet_blend']}")


def test_social_realist_low_edge_softness():
    """SOCIAL_REALIST edge_softness should be low — knife leaves crisp plane boundaries."""
    style = Style(medium=Medium.OIL, period=Period.SOCIAL_REALIST,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] <= 0.40, (
        f"SOCIAL_REALIST edge_softness should be low (≤0.40); "
        f"got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# William-Adolphe Bouguereau — French Academic Realism; academic_skin_pass()
# ──────────────────────────────────────────────────────────────────────────────

def test_bouguereau_in_catalog():
    """Bouguereau must be present in CATALOG."""
    assert "bouguereau" in CATALOG


def test_bouguereau_movement():
    s = get_style("bouguereau")
    assert "Academic" in s.movement or "academic" in s.movement.lower()


def test_bouguereau_nationality():
    s = get_style("bouguereau")
    assert s.nationality == "French"


def test_bouguereau_palette_length():
    s = get_style("bouguereau")
    assert len(s.palette) >= 5, "Bouguereau palette should have at least 5 key colours"


def test_bouguereau_palette_values_in_range():
    """All Bouguereau palette RGB values must be in [0, 1]."""
    s = get_style("bouguereau")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Bouguereau palette {rgb}")


def test_bouguereau_wet_blend_very_high():
    """Bouguereau's porcelain technique requires very high wet_blend (≥ 0.80)."""
    s = get_style("bouguereau")
    assert s.wet_blend >= 0.80, (
        f"Bouguereau wet_blend should be very high (≥0.80); got {s.wet_blend}")


def test_bouguereau_edge_softness_high():
    """Bouguereau's flesh has very soft edge transitions (edge_softness ≥ 0.70)."""
    s = get_style("bouguereau")
    assert s.edge_softness >= 0.70, (
        f"Bouguereau edge_softness should be high (≥0.70); got {s.edge_softness}")


def test_bouguereau_small_stroke_size():
    """Bouguereau works with tiny brushes — stroke_size should be small (≤ 5)."""
    s = get_style("bouguereau")
    assert s.stroke_size <= 5, (
        f"Bouguereau stroke_size should be small (≤5); got {s.stroke_size}")


def test_bouguereau_no_chromatic_split():
    """Bouguereau does not use divisionist chromatic splitting."""
    s = get_style("bouguereau")
    assert not s.chromatic_split, "Bouguereau chromatic_split should be False"


def test_bouguereau_famous_works_not_empty():
    """Bouguereau should have at least 4 famous works documented."""
    s = get_style("bouguereau")
    assert len(s.famous_works) >= 4, (
        f"Bouguereau should have ≥4 famous works; got {len(s.famous_works)}")


def test_bouguereau_famous_works_include_birth_of_venus():
    """Bouguereau's most iconic work — The Birth of Venus — must be listed."""
    s = get_style("bouguereau")
    titles = [w[0] for w in s.famous_works]
    assert any("Venus" in t or "Birth" in t for t in titles), (
        "Bouguereau famous works should include The Birth of Venus")


def test_bouguereau_inspiration_references_academic_skin():
    """Bouguereau's inspiration text should reference academic_skin_pass."""
    s = get_style("bouguereau")
    assert "academic_skin" in s.inspiration.lower().replace(" ", "_"), (
        "Bouguereau inspiration should reference academic_skin_pass()")


def test_bouguereau_low_jitter():
    """Bouguereau's controlled technique should have very low jitter (< 0.02)."""
    s = get_style("bouguereau")
    assert s.jitter < 0.02, (
        f"Bouguereau jitter should be very low (< 0.02); got {s.jitter}")


# ──────────────────────────────────────────────────────────────────────────────
# Period.ACADEMIC_REALIST — Bouguereau period enum
# ──────────────────────────────────────────────────────────────────────────────

def test_academic_realist_period_present():
    """ACADEMIC_REALIST must exist in the Period enum."""
    assert hasattr(Period, "ACADEMIC_REALIST"), "Period.ACADEMIC_REALIST not found"
    assert Period.ACADEMIC_REALIST in list(Period)


def test_academic_realist_stroke_params_all_keys():
    """ACADEMIC_REALIST stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.ACADEMIC_REALIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"ACADEMIC_REALIST stroke_params missing key: {key!r}"


def test_academic_realist_tiny_stroke_face():
    """ACADEMIC_REALIST stroke_size_face must be tiny (≤ 4) — micro-blending marks."""
    style = Style(medium=Medium.OIL, period=Period.ACADEMIC_REALIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] <= 4, (
        f"ACADEMIC_REALIST stroke_size_face should be tiny (≤4); "
        f"got {p['stroke_size_face']}")


def test_academic_realist_very_high_wet_blend():
    """ACADEMIC_REALIST wet_blend must be very high (≥ 0.80) — porcelain smoothness."""
    style = Style(medium=Medium.OIL, period=Period.ACADEMIC_REALIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.80, (
        f"ACADEMIC_REALIST wet_blend should be very high (≥0.80); got {p['wet_blend']}")


def test_academic_realist_high_edge_softness():
    """ACADEMIC_REALIST edge_softness must be high (≥ 0.70) — imperceptible transitions."""
    style = Style(medium=Medium.OIL, period=Period.ACADEMIC_REALIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] >= 0.70, (
        f"ACADEMIC_REALIST edge_softness should be high (≥0.70); "
        f"got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Mary Cassatt — this session's randomly discovered artist
# ──────────────────────────────────────────────────────────────────────────────

def test_mary_cassatt_in_catalog():
    """Mary Cassatt must be present in CATALOG (this session's addition)."""
    assert "mary_cassatt" in CATALOG


def test_mary_cassatt_movement():
    s = get_style("mary_cassatt")
    assert ("Impression" in s.movement or "impression" in s.movement.lower()
            or "Intimisme" in s.movement or "American" in s.movement)


def test_mary_cassatt_palette_length():
    s = get_style("mary_cassatt")
    assert len(s.palette) >= 5, "Cassatt palette should have at least 5 key colours"


def test_mary_cassatt_palette_values_in_range():
    """All Cassatt palette RGB values must be in [0, 1]."""
    s = get_style("mary_cassatt")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Cassatt palette {rgb}")


def test_mary_cassatt_ground_color_valid():
    s = get_style("mary_cassatt")
    assert len(s.ground_color) == 3
    for ch in s.ground_color:
        assert 0.0 <= ch <= 1.0


def test_mary_cassatt_famous_works():
    s = get_style("mary_cassatt")
    assert len(s.famous_works) >= 3, "Cassatt should have at least 3 famous works"
    titles = [w[0] for w in s.famous_works]
    assert any("Bath" in t or "Loge" in t or "Armchair" in t for t in titles), (
        "Cassatt famous works should include at least one canonical work "
        "(The Child's Bath, In the Loge, or Little Girl in a Blue Armchair)")


def test_mary_cassatt_stroke_params_moderate_wet_blend():
    """Cassatt should use moderate wet_blend — not broken Impressionism, not Academic."""
    s = get_style("mary_cassatt")
    assert 0.10 < s.wet_blend < 0.70, (
        f"Cassatt wet_blend should be moderate (0.10–0.70); got {s.wet_blend}")


def test_mary_cassatt_no_chromatic_split():
    """Cassatt does not use Divisionist dot splitting."""
    s = get_style("mary_cassatt")
    assert not s.chromatic_split, "Cassatt should not have chromatic_split=True"


# ──────────────────────────────────────────────────────────────────────────────
# IMPRESSIONIST_INTIMISTE period — this session's addition
# ──────────────────────────────────────────────────────────────────────────────

def test_impressionist_intimiste_period_present():
    """IMPRESSIONIST_INTIMISTE must exist in Period enum (this session's addition)."""
    assert hasattr(Period, "IMPRESSIONIST_INTIMISTE"), (
        "Period.IMPRESSIONIST_INTIMISTE not found")
    assert Period.IMPRESSIONIST_INTIMISTE in list(Period)


def test_impressionist_intimiste_stroke_params():
    """IMPRESSIONIST_INTIMISTE stroke_params must have all required keys and valid values."""
    style = Style(medium=Medium.OIL, period=Period.IMPRESSIONIST_INTIMISTE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"IMPRESSIONIST_INTIMISTE stroke_params missing key: {key!r}"
    assert p["stroke_size_face"] > 0
    assert p["stroke_size_bg"] > 0
    assert 0.0 <= p["wet_blend"] <= 1.0
    assert 0.0 <= p["edge_softness"] <= 1.0


def test_impressionist_intimiste_moderate_wet_blend():
    """IMPRESSIONIST_INTIMISTE wet_blend should be between IMPRESSIONIST and ACADEMIC_REALIST."""
    intimiste = Style(medium=Medium.OIL, period=Period.IMPRESSIONIST_INTIMISTE,
                      palette=PaletteHint.WARM_EARTH).stroke_params
    impressionist = Style(medium=Medium.OIL, period=Period.IMPRESSIONIST,
                          palette=PaletteHint.WARM_EARTH).stroke_params
    academic = Style(medium=Medium.OIL, period=Period.ACADEMIC_REALIST,
                     palette=PaletteHint.WARM_EARTH).stroke_params
    assert impressionist["wet_blend"] <= intimiste["wet_blend"] <= academic["wet_blend"], (
        "IMPRESSIONIST_INTIMISTE wet_blend should be between IMPRESSIONIST and ACADEMIC_REALIST")


# ──────────────────────────────────────────────────────────────────────────────
# Pieter Bruegel the Elder — this session's randomly selected artist
# ──────────────────────────────────────────────────────────────────────────────

def test_bruegel_in_catalog():
    """Pieter Bruegel the Elder (this session's random artist) must be in CATALOG."""
    assert "bruegel" in CATALOG, "Missing artist: 'bruegel'"


def test_bruegel_movement():
    """Bruegel's movement must reference Flemish and/or Northern tradition."""
    s = get_style("bruegel")
    assert "Flemish" in s.movement or "Northern" in s.movement, (
        f"Unexpected Bruegel movement: {s.movement!r}")


def test_bruegel_palette_length():
    """Bruegel must have at least 6 palette entries to cover the panoramic depth zones."""
    s = get_style("bruegel")
    assert len(s.palette) >= 6, (
        f"Bruegel palette has only {len(s.palette)} entries; expected ≥ 6")


def test_bruegel_palette_values_in_range():
    """All Bruegel palette RGB values must be in [0, 1]."""
    s = get_style("bruegel")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"Out-of-range channel {ch} in Bruegel palette {rgb}")


def test_bruegel_ground_color_valid():
    """Bruegel's ground_color must be a valid 3-tuple in [0, 1]."""
    s = get_style("bruegel")
    assert len(s.ground_color) == 3
    for ch in s.ground_color:
        assert 0.0 <= ch <= 1.0


def test_bruegel_has_famous_works():
    """Bruegel entry must include at least 4 famous works."""
    s = get_style("bruegel")
    assert len(s.famous_works) >= 4, (
        f"Bruegel famous_works has only {len(s.famous_works)} entries; expected ≥ 4")


def test_bruegel_hunters_in_snow_referenced():
    """'Hunters in the Snow' — the canonical Bruegel panorama — must be listed."""
    s = get_style("bruegel")
    titles = [t for t, _ in s.famous_works]
    assert any("Hunters" in t for t in titles), (
        "Bruegel famous_works must include 'Hunters in the Snow'")


def test_flemish_panoramic_period_exists():
    """FLEMISH_PANORAMIC must exist in Period enum (this session's addition)."""
    assert hasattr(Period, "FLEMISH_PANORAMIC"), (
        "Period.FLEMISH_PANORAMIC not found")
    assert Period.FLEMISH_PANORAMIC in list(Period)


def test_flemish_panoramic_stroke_params_valid():
    """FLEMISH_PANORAMIC stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.FLEMISH_PANORAMIC,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"FLEMISH_PANORAMIC stroke_params missing key: {key!r}"
    assert p["stroke_size_face"] > 0
    assert p["stroke_size_bg"] > 0
    assert 0.0 <= p["wet_blend"] <= 1.0
    assert 0.0 <= p["edge_softness"] <= 1.0


def test_flemish_panoramic_bg_larger_than_face():
    """FLEMISH_PANORAMIC stroke_size_bg must be larger than stroke_size_face (landscape priority)."""
    p = Style(medium=Medium.OIL, period=Period.FLEMISH_PANORAMIC,
              palette=PaletteHint.WARM_EARTH).stroke_params
    assert p["stroke_size_bg"] > p["stroke_size_face"], (
        "FLEMISH_PANORAMIC bg stroke must be larger than face stroke (landscape-first)")


# ──────────────────────────────────────────────────────────────────────────────
# Anders Zorn — this session's random artist discovery
# Nordic Impressionism / Zorn palette (yellow ochre, ivory black, vermillion, white)
# ──────────────────────────────────────────────────────────────────────────────

def test_anders_zorn_in_catalog():
    """Anders Zorn must appear in CATALOG after this session."""
    assert "anders_zorn" in CATALOG


def test_anders_zorn_movement():
    s = get_style("anders_zorn")
    assert "Nordic" in s.movement or "Impressi" in s.movement, (
        f"Expected Nordic/Impressionist movement, got {s.movement!r}")


def test_anders_zorn_nationality():
    s = get_style("anders_zorn")
    assert "Swedish" in s.nationality, (
        f"Expected Swedish nationality, got {s.nationality!r}")


def test_anders_zorn_palette_length():
    s = get_style("anders_zorn")
    assert len(s.palette) >= 4, (
        f"Zorn palette must have at least 4 entries (ochre, black, vermillion, white); "
        f"got {len(s.palette)}")


def test_anders_zorn_palette_values_in_range():
    """All Zorn palette RGB values must be floats in [0, 1]."""
    s = get_style("anders_zorn")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"Out-of-range channel {ch} in Anders Zorn palette {rgb}")


def test_anders_zorn_ground_color_warm():
    """Zorn's ground should have a warm bias (R channel ≥ B channel)."""
    s = get_style("anders_zorn")
    r, g, b = s.ground_color
    assert r >= b, (
        f"Zorn ground should be warm-biased but R={r:.2f} < B={b:.2f}")


def test_anders_zorn_wet_blend_moderate_high():
    """Zorn's wet_blend should be moderately high (≥ 0.50) — he worked wet-into-wet."""
    s = get_style("anders_zorn")
    assert s.wet_blend >= 0.50, (
        f"Zorn wet_blend should be ≥ 0.50 (wet-into-wet portrait work); got {s.wet_blend}")


def test_anders_zorn_no_chromatic_split():
    """Zorn used no chromatic splitting — he worked with warm mixtures only."""
    s = get_style("anders_zorn")
    assert not s.chromatic_split, "anders_zorn should not use chromatic_split"


def test_anders_zorn_famous_works_not_empty():
    s = get_style("anders_zorn")
    assert len(s.famous_works) >= 4, (
        f"Zorn famous_works has only {len(s.famous_works)} entries; expected ≥ 4")


def test_anders_zorn_omnibus_referenced():
    """'Omnibus' (1895) — Zorn's most celebrated portrait — must be listed."""
    s = get_style("anders_zorn")
    titles = [t for t, _ in s.famous_works]
    assert any("Omnibus" in t for t in titles), (
        "anders_zorn famous_works must include 'Omnibus'")


def test_anders_zorn_inspiration_references_tricolor():
    """The Zorn catalog entry must reference the zorn_tricolor_pass."""
    s = get_style("anders_zorn")
    assert "zorn_tricolor_pass" in s.inspiration, (
        "anders_zorn inspiration must reference zorn_tricolor_pass()")


def test_anders_zorn_low_jitter():
    """Zorn's jitter should be low — he relied on palette precision, not accident."""
    s = get_style("anders_zorn")
    assert s.jitter <= 0.06, (
        f"anders_zorn jitter should be ≤ 0.06; got {s.jitter}")


def test_nordic_impressionist_period_exists():
    """NORDIC_IMPRESSIONIST must exist in Period enum after this session."""
    assert hasattr(Period, "NORDIC_IMPRESSIONIST"), (
        "Period.NORDIC_IMPRESSIONIST not found")
    assert Period.NORDIC_IMPRESSIONIST in list(Period)


def test_nordic_impressionist_stroke_params_valid():
    """NORDIC_IMPRESSIONIST stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.NORDIC_IMPRESSIONIST,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"NORDIC_IMPRESSIONIST stroke_params missing key: {key!r}"
    assert p["stroke_size_face"] > 0
    assert p["stroke_size_bg"]   > 0
    assert 0.0 <= p["wet_blend"]     <= 1.0
    assert 0.0 <= p["edge_softness"] <= 1.0


def test_nordic_impressionist_wet_blend_moderate_high():
    """NORDIC_IMPRESSIONIST wet_blend should reflect Zorn's confident wet-into-wet work."""
    p = Style(medium=Medium.OIL, period=Period.NORDIC_IMPRESSIONIST,
              palette=PaletteHint.WARM_EARTH).stroke_params
    assert p["wet_blend"] >= 0.50, (
        f"NORDIC_IMPRESSIONIST wet_blend should be ≥ 0.50; got {p['wet_blend']}")


# ──────────────────────────────────────────────────────────────────────────────
# Berthe Morisot — this session's randomly discovered artist
# French Impressionism / high-key colorful shadows / luminous plein-air palette
# ──────────────────────────────────────────────────────────────────────────────

def test_berthe_morisot_in_catalog():
    """Berthe Morisot must appear in CATALOG after this session."""
    assert "berthe_morisot" in CATALOG


def test_berthe_morisot_movement():
    s = get_style("berthe_morisot")
    assert "Impression" in s.movement or "impression" in s.movement.lower(), (
        f"Expected Impressionist movement, got {s.movement!r}")


def test_berthe_morisot_nationality():
    s = get_style("berthe_morisot")
    assert "French" in s.nationality, (
        f"Expected French nationality, got {s.nationality!r}")


def test_berthe_morisot_palette_length():
    s = get_style("berthe_morisot")
    assert len(s.palette) >= 5, (
        f"Morisot palette should have at least 5 key colours; got {len(s.palette)}")


def test_berthe_morisot_palette_values_in_range():
    """All Morisot palette RGB values must be floats in [0, 1]."""
    s = get_style("berthe_morisot")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"Out-of-range channel {ch} in Berthe Morisot palette {rgb}")


def test_berthe_morisot_ground_high_luminance():
    """Morisot's pale cream ground must be high-key (luminance > 0.70)."""
    s = get_style("berthe_morisot")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum > 0.70, (
        f"Morisot ground should be high-key (lum > 0.70); got {lum:.3f}")


def test_berthe_morisot_palette_has_blue_violet():
    """Morisot's palette must contain a blue or violet-biased shadow color."""
    s = get_style("berthe_morisot")
    has_cool = any(b >= r and b >= g - 0.05 for r, g, b in s.palette)
    assert has_cool, (
        "Morisot palette must contain a blue/violet color for her characteristic shadows")


def test_berthe_morisot_no_crackle():
    """Morisot's fresh Impressionist surface should not use a crackle finish."""
    s = get_style("berthe_morisot")
    assert not s.crackle, "berthe_morisot crackle should be False (fresh Impressionist surface)"


def test_berthe_morisot_no_unifying_glaze():
    """Morisot used no warm unifying glaze — her surfaces stay fresh."""
    s = get_style("berthe_morisot")
    assert s.glazing is None, "berthe_morisot glazing should be None (no warm film)"


def test_berthe_morisot_famous_works_not_empty():
    s = get_style("berthe_morisot")
    assert len(s.famous_works) >= 4, (
        f"Morisot famous_works has only {len(s.famous_works)} entries; expected ≥ 4")


def test_berthe_morisot_cradle_referenced():
    """'The Cradle' (1872) — Morisot's most celebrated work — must be listed."""
    s = get_style("berthe_morisot")
    titles = [t for t, _ in s.famous_works]
    assert any("Cradle" in t for t in titles), (
        "berthe_morisot famous_works must include 'The Cradle'")


def test_berthe_morisot_inspiration_references_pass():
    """The Morisot catalog entry must reference the morisot_plein_air_pass."""
    s = get_style("berthe_morisot")
    assert "morisot_plein_air_pass" in s.inspiration, (
        "berthe_morisot inspiration must reference morisot_plein_air_pass()")


def test_impressionist_plein_air_period_exists():
    """IMPRESSIONIST_PLEIN_AIR must exist in Period enum after this session."""
    assert hasattr(Period, "IMPRESSIONIST_PLEIN_AIR"), (
        "Period.IMPRESSIONIST_PLEIN_AIR not found")
    assert Period.IMPRESSIONIST_PLEIN_AIR in list(Period)


def test_impressionist_plein_air_stroke_params_valid():
    """IMPRESSIONIST_PLEIN_AIR stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.IMPRESSIONIST_PLEIN_AIR,
                  palette=PaletteHint.COOL_GREY)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"IMPRESSIONIST_PLEIN_AIR stroke_params missing key: {key!r}"
    assert p["stroke_size_face"] > 0
    assert p["stroke_size_bg"]   > 0
    assert 0.0 <= p["wet_blend"]      <= 1.0
    assert 0.0 <= p["edge_softness"]  <= 1.0


def test_impressionist_plein_air_wet_blend_moderate():
    """IMPRESSIONIST_PLEIN_AIR wet_blend should be moderate — visible strokes but not raw."""
    p = Style(medium=Medium.OIL, period=Period.IMPRESSIONIST_PLEIN_AIR).stroke_params
    assert 0.20 <= p["wet_blend"] <= 0.60, (
        f"IMPRESSIONIST_PLEIN_AIR wet_blend should be 0.20–0.60; got {p['wet_blend']}")


def test_impressionist_plein_air_edge_softness_low():
    """IMPRESSIONIST_PLEIN_AIR edge_softness should be lower than sfumato-style periods."""
    sp_plein = Style(medium=Medium.OIL, period=Period.IMPRESSIONIST_PLEIN_AIR).stroke_params
    sp_sfum  = Style(medium=Medium.OIL, period=Period.RENAISSANCE).stroke_params
    assert sp_plein["edge_softness"] < sp_sfum["edge_softness"], (
        "IMPRESSIONIST_PLEIN_AIR edge_softness should be lower than RENAISSANCE sfumato")


# ──────────────────────────────────────────────────────────────────────────────
# Degas — catalog entry (session 29)
# ──────────────────────────────────────────────────────────────────────────────

def test_degas_in_catalog():
    """degas must be present in CATALOG after session 29."""
    assert "degas" in CATALOG


def test_degas_movement():
    s = get_style("degas")
    assert "Impressionism" in s.movement or "Post" in s.movement, (
        f"degas movement should reference Impressionism or Post-Impressionism; got {s.movement!r}")


def test_degas_nationality():
    s = get_style("degas")
    assert s.nationality == "French", (
        f"degas nationality should be 'French'; got {s.nationality!r}")


def test_degas_palette_length():
    s = get_style("degas")
    assert len(s.palette) >= 5, (
        f"degas palette should have ≥ 5 colours; got {len(s.palette)}")


def test_degas_palette_values_in_range():
    """All Degas palette RGB values must be in [0.0, 1.0]."""
    s = get_style("degas")
    for i, color in enumerate(s.palette):
        for j, channel in enumerate(color):
            assert 0.0 <= channel <= 1.0, (
                f"degas palette[{i}][{j}] = {channel} is outside [0, 1]")


def test_degas_ground_is_dark():
    """Degas' monotype ground should be dark (mean luminance < 0.45)."""
    s = get_style("degas")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum < 0.45, (
        f"degas ground_color should be dark (lum < 0.45); got lum={lum:.3f}")


def test_degas_has_blue_grey_in_palette():
    """Degas' palette must contain at least one cool blue-grey entry (B > R and B > G)."""
    s = get_style("degas")
    cool = [(r, g, b) for r, g, b in s.palette if b > r and b > g]
    assert cool, "degas palette must contain a cool blue-grey entry (B > R and B > G)"


def test_degas_no_crackle():
    s = get_style("degas")
    assert not s.crackle, "degas crackle should be False (pastel has no aged-crackle)"


def test_degas_no_unifying_glaze():
    s = get_style("degas")
    assert s.glazing is None, "degas glazing should be None (pastels are unvarnished)"


def test_degas_famous_works_not_empty():
    s = get_style("degas")
    assert len(s.famous_works) >= 5, (
        f"degas famous_works should have ≥ 5 entries; got {len(s.famous_works)}")


def test_degas_dance_class_referenced():
    """The Dance Class must appear in degas famous_works."""
    s = get_style("degas")
    titles = [title for title, _ in s.famous_works]
    assert any("Dance Class" in t for t in titles), (
        "degas famous_works must include 'The Dance Class'")


def test_degas_inspiration_references_pass():
    s = get_style("degas")
    assert "degas_pastel_pass()" in s.inspiration, (
        "degas inspiration must reference degas_pastel_pass()")


def test_degas_wet_blend_low():
    """Degas' wet_blend should be low — pastel hatching is dry, not wet-blended."""
    s = get_style("degas")
    assert s.wet_blend <= 0.30, (
        f"degas wet_blend should be ≤ 0.30 (dry pastel); got {s.wet_blend}")


# ──────────────────────────────────────────────────────────────────────────────
# POST_IMPRESSIONIST period (scene_schema, session 29)
# ──────────────────────────────────────────────────────────────────────────────

def test_post_impressionist_period_exists():
    """POST_IMPRESSIONIST must exist in the Period enum after session 29."""
    assert hasattr(Period, "POST_IMPRESSIONIST"), (
        "Period.POST_IMPRESSIONIST not found — add it to scene_schema.py")


def test_post_impressionist_stroke_params_valid():
    """POST_IMPRESSIONIST stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.POST_IMPRESSIONIST,
                  palette=PaletteHint.COOL_GREY)
    sp = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"POST_IMPRESSIONIST stroke_params missing key: {key!r}"
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


def test_post_impressionist_wet_blend_low():
    """POST_IMPRESSIONIST wet_blend should be low — pastel technique is dry."""
    sp = Style(medium=Medium.OIL, period=Period.POST_IMPRESSIONIST).stroke_params
    assert sp["wet_blend"] <= 0.30, (
        f"POST_IMPRESSIONIST wet_blend should be ≤ 0.30; got {sp['wet_blend']}")


# ──────────────────────────────────────────────────────────────────────────────
# Piero della Francesca — catalog entry (prior session)
# Cool mineral Early Italian Renaissance palette / piero_crystalline_pass()
# ──────────────────────────────────────────────────────────────────────────────

def test_piero_della_francesca_in_catalog():
    """piero_della_francesca must appear in CATALOG after this session."""
    assert "piero_della_francesca" in CATALOG


def test_piero_della_francesca_movement():
    s = get_style("piero_della_francesca")
    assert "Renaissance" in s.movement or "renaissance" in s.movement.lower(), (
        f"Expected Renaissance movement, got {s.movement!r}")


def test_piero_della_francesca_nationality():
    s = get_style("piero_della_francesca")
    assert "Italian" in s.nationality, (
        f"Expected Italian nationality, got {s.nationality!r}")


def test_piero_della_francesca_palette_length():
    s = get_style("piero_della_francesca")
    assert len(s.palette) >= 5, (
        f"Piero palette should have at least 5 colours; got {len(s.palette)}")


def test_piero_della_francesca_palette_values_in_range():
    """All Piero palette RGB values must be in [0.0, 1.0]."""
    s = get_style("piero_della_francesca")
    for i, color in enumerate(s.palette):
        for j, channel in enumerate(color):
            assert 0.0 <= channel <= 1.0, (
                f"piero_della_francesca palette[{i}][{j}] = {channel} is outside [0, 1]")


def test_piero_della_francesca_ground_cool_or_neutral():
    """Piero's ground should be cooler / more neutral than Leonardo's amber ochre."""
    s = get_style("piero_della_francesca")
    r, g, b = s.ground_color
    leo = get_style("leonardo")
    lr, lg, lb = leo.ground_color
    # Piero's ground R channel should be less warm-dominant than Leonardo's
    piero_warmth = r - b
    leo_warmth   = lr - lb
    assert piero_warmth < leo_warmth, (
        f"Piero's ground should be cooler than Leonardo's: "
        f"piero (R-B)={piero_warmth:.3f}, leo (R-B)={leo_warmth:.3f}")


def test_piero_della_francesca_palette_has_cool_stone():
    """Piero's palette must contain at least one cool grey or blue entry (B >= R)."""
    s = get_style("piero_della_francesca")
    has_cool = any(b >= r for r, g, b in s.palette)
    assert has_cool, (
        "piero_della_francesca palette must contain a cool entry (B >= R) "
        "for his stone-grey shadows and cerulean sky tones")


def test_piero_della_francesca_wet_blend_moderate():
    """Piero's wet_blend should be moderate — not Leonardo's 0.92 but not Flemish dry."""
    s = get_style("piero_della_francesca")
    assert 0.35 <= s.wet_blend <= 0.60, (
        f"piero_della_francesca wet_blend should be in [0.35, 0.60]; got {s.wet_blend}")


def test_piero_della_francesca_edge_softness_moderate():
    """Piero's edge_softness should be moderate — clear geometric forms, not sfumato."""
    s = get_style("piero_della_francesca")
    assert 0.30 <= s.edge_softness <= 0.60, (
        f"piero_della_francesca edge_softness should be in [0.30, 0.60]; "
        f"got {s.edge_softness}")


def test_piero_della_francesca_famous_works_not_empty():
    s = get_style("piero_della_francesca")
    assert len(s.famous_works) >= 4, (
        f"piero_della_francesca famous_works should have ≥ 4 entries; "
        f"got {len(s.famous_works)}")


def test_piero_della_francesca_flagellation_referenced():
    """'The Flagellation of Christ' — Piero's most analysed work — must be listed."""
    s = get_style("piero_della_francesca")
    titles = [title for title, _ in s.famous_works]
    assert any("Flagellation" in t for t in titles), (
        "piero_della_francesca famous_works must include 'The Flagellation of Christ'")


def test_piero_della_francesca_inspiration_references_pass():
    """The Piero catalog entry must reference the piero_crystalline_pass."""
    s = get_style("piero_della_francesca")
    assert "piero_crystalline_pass" in s.inspiration, (
        "piero_della_francesca inspiration must reference piero_crystalline_pass()")


def test_piero_della_francesca_low_jitter():
    """Piero's jitter should be low — precise geometric technique."""
    s = get_style("piero_della_francesca")
    assert s.jitter <= 0.06, (
        f"piero_della_francesca jitter should be ≤ 0.06; got {s.jitter}")


def test_piero_della_francesca_has_crackle():
    """Piero's panel and fresco work should have the crackle finish flag."""
    s = get_style("piero_della_francesca")
    assert s.crackle, "piero_della_francesca crackle should be True (aged panel/fresco)"


# ──────────────────────────────────────────────────────────────────────────────
# EARLY_ITALIAN_RENAISSANCE period (scene_schema, prior session)
# ──────────────────────────────────────────────────────────────────────────────

def test_early_italian_renaissance_period_exists():
    """EARLY_ITALIAN_RENAISSANCE must exist in the Period enum after this session."""
    assert hasattr(Period, "EARLY_ITALIAN_RENAISSANCE"), (
        "Period.EARLY_ITALIAN_RENAISSANCE not found — add it to scene_schema.py")


def test_early_italian_renaissance_stroke_params_valid():
    """EARLY_ITALIAN_RENAISSANCE stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.EARLY_ITALIAN_RENAISSANCE,
                  palette=PaletteHint.COOL_GREY)
    sp = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, (
            f"EARLY_ITALIAN_RENAISSANCE stroke_params missing key: {key!r}")
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


# ──────────────────────────────────────────────────────────────────────────────
# John William Waterhouse — current session addition (PRE_RAPHAELITE)
# ──────────────────────────────────────────────────────────────────────────────

def test_waterhouse_in_catalog():
    """Waterhouse (current session) must be present in CATALOG."""
    assert "waterhouse" in CATALOG


def test_waterhouse_movement():
    s = get_style("waterhouse")
    assert ("Pre-Raphael" in s.movement or "Academic" in s.movement
            or "pre-raphael" in s.movement.lower())


def test_waterhouse_palette_length():
    s = get_style("waterhouse")
    assert len(s.palette) >= 5, "Waterhouse palette should have at least 5 key colours"


def test_waterhouse_palette_values_in_range():
    """All Waterhouse palette RGB values must be in [0, 1]."""
    s = get_style("waterhouse")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Waterhouse palette {rgb}")


def test_waterhouse_ground_color_near_white():
    """Waterhouse ground should be near-white — defining Pre-Raphaelite wet white ground."""
    s = get_style("waterhouse")
    avg = sum(s.ground_color) / 3.0
    assert avg >= 0.85, (
        f"Waterhouse ground_color average should be ≥ 0.85 (near-white); got {avg:.3f}")


def test_waterhouse_ground_color_valid():
    s = get_style("waterhouse")
    assert len(s.ground_color) == 3
    for ch in s.ground_color:
        assert 0.0 <= ch <= 1.0


def test_waterhouse_famous_works_not_empty():
    s = get_style("waterhouse")
    assert len(s.famous_works) >= 5, (
        f"waterhouse famous_works should have ≥ 5 entries; got {len(s.famous_works)}")


def test_waterhouse_lady_of_shalott_referenced():
    """The Lady of Shalott must appear in waterhouse famous_works."""
    s = get_style("waterhouse")
    titles = [title for title, _ in s.famous_works]
    assert any("Shalott" in t for t in titles), (
        "waterhouse famous_works must include 'The Lady of Shalott'")


def test_waterhouse_hylas_referenced():
    """Hylas and the Nymphs must appear in waterhouse famous_works."""
    s = get_style("waterhouse")
    titles = [title for title, _ in s.famous_works]
    assert any("Hylas" in t for t in titles), (
        "waterhouse famous_works must include 'Hylas and the Nymphs'")


def test_waterhouse_inspiration_references_pass():
    s = get_style("waterhouse")
    assert "waterhouse_jewel_pass()" in s.inspiration, (
        "waterhouse inspiration must reference waterhouse_jewel_pass()")


def test_waterhouse_wet_blend_moderate():
    """Waterhouse wet_blend should be moderate — wet white ground blends gently."""
    s = get_style("waterhouse")
    assert 0.20 <= s.wet_blend <= 0.50, (
        f"waterhouse wet_blend should be 0.20–0.50; got {s.wet_blend}")


def test_waterhouse_glazing_present():
    """Waterhouse should have a unifying glaze — the cool Pre-Raphaelite atmosphere."""
    s = get_style("waterhouse")
    assert s.glazing is not None, "waterhouse must have a glazing colour defined"
    # Should be a cool blue-grey (blue channel higher than red)
    r, g, b = s.glazing
    assert b >= r, (
        f"Waterhouse glazing should be cool (B ≥ R); got R={r:.2f} B={b:.2f}")


def test_waterhouse_no_crackle():
    """Waterhouse should not have crackle — he is modern, not museum-aged."""
    s = get_style("waterhouse")
    assert not s.crackle, "waterhouse crackle should be False (not museum-aged)"


def test_waterhouse_has_blue_in_palette():
    """Waterhouse palette must contain a sapphire-blue entry (high B, low R)."""
    s = get_style("waterhouse")
    has_blue = any(b > 0.50 and b > r + 0.20 for r, g, b in s.palette)
    assert has_blue, "Waterhouse palette must contain a deep blue (sapphire) entry"


def test_waterhouse_has_crimson_in_palette():
    """Waterhouse palette must contain a deep red/crimson entry (high R, low B)."""
    s = get_style("waterhouse")
    has_crimson = any(r > 0.55 and r > b + 0.30 for r, g, b in s.palette)
    assert has_crimson, "Waterhouse palette must contain a deep crimson/red entry"


# ──────────────────────────────────────────────────────────────────────────────
# PRE_RAPHAELITE period (scene_schema, current session)
# ──────────────────────────────────────────────────────────────────────────────

def test_pre_raphaelite_period_exists():
    """PRE_RAPHAELITE must exist in the Period enum after this session."""
    assert hasattr(Period, "PRE_RAPHAELITE"), (
        "Period.PRE_RAPHAELITE not found — add it to scene_schema.py")


def test_pre_raphaelite_stroke_params_valid():
    """PRE_RAPHAELITE stroke_params must have all required keys and valid ranges."""
    style = Style(medium=Medium.OIL, period=Period.PRE_RAPHAELITE,
                  palette=PaletteHint.JEWEL)
    sp = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"PRE_RAPHAELITE stroke_params missing key: {key!r}"
    assert sp["stroke_size_face"] > 0
    assert sp["stroke_size_bg"]   > 0
    assert 0.0 <= sp["wet_blend"]     <= 1.0
    assert 0.0 <= sp["edge_softness"] <= 1.0


def test_early_italian_renaissance_wet_blend_lower_than_venetian():
    """EARLY_ITALIAN_RENAISSANCE wet_blend must be lower than VENETIAN_RENAISSANCE (less rich blending)."""
    sp_early = Style(medium=Medium.OIL, period=Period.EARLY_ITALIAN_RENAISSANCE).stroke_params
    sp_ven   = Style(medium=Medium.OIL, period=Period.VENETIAN_RENAISSANCE).stroke_params
    assert sp_early["wet_blend"] < sp_ven["wet_blend"], (
        "EARLY_ITALIAN_RENAISSANCE wet_blend must be lower than VENETIAN_RENAISSANCE "
        "(Piero's geometric precision uses less fluid blending than Titian's rich Venetian technique)")


def test_early_italian_renaissance_edge_softness_moderate():
    """EARLY_ITALIAN_RENAISSANCE edge_softness should be moderate (clear geometric forms)."""
    sp = Style(medium=Medium.OIL, period=Period.EARLY_ITALIAN_RENAISSANCE).stroke_params
    assert 0.30 <= sp["edge_softness"] <= 0.60, (
        f"EARLY_ITALIAN_RENAISSANCE edge_softness should be in [0.30, 0.60]; "
        f"got {sp['edge_softness']}")


def test_pre_raphaelite_stroke_size_face_small():
    """PRE_RAPHAELITE stroke_size_face should be small — fine Pre-Raphaelite detail."""
    sp = Style(medium=Medium.OIL, period=Period.PRE_RAPHAELITE).stroke_params
    assert sp["stroke_size_face"] <= 7, (
        f"PRE_RAPHAELITE stroke_size_face should be ≤ 7 (fine detail); "
        f"got {sp['stroke_size_face']}")


def test_pre_raphaelite_wet_blend_moderate():
    """PRE_RAPHAELITE wet_blend should be moderate — wet white ground."""
    sp = Style(medium=Medium.OIL, period=Period.PRE_RAPHAELITE).stroke_params
    assert 0.15 <= sp["wet_blend"] <= 0.55, (
        f"PRE_RAPHAELITE wet_blend should be 0.15–0.55; got {sp['wet_blend']}")


def test_pre_raphaelite_wet_blend_lower_than_academic():
    """PRE_RAPHAELITE wet_blend should be lower than ACADEMIC_REALIST."""
    sp_pr  = Style(medium=Medium.OIL, period=Period.PRE_RAPHAELITE).stroke_params
    sp_ac  = Style(medium=Medium.OIL, period=Period.ACADEMIC_REALIST).stroke_params
    assert sp_pr["wet_blend"] < sp_ac["wet_blend"], (
        "PRE_RAPHAELITE wet_blend must be lower than ACADEMIC_REALIST "
        "(Pre-Raphaelite ground technique is wet but not the hyper-smooth Academic blend)")


# ──────────────────────────────────────────────────────────────────────────────
# Gustave Moreau / SYMBOLIST — session 32 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_gustave_moreau_in_catalog():
    """gustave_moreau must be present in CATALOG after session 32."""
    assert "gustave_moreau" in CATALOG


def test_gustave_moreau_movement():
    s = get_style("gustave_moreau")
    assert "symbolism" in s.movement.lower() or "symbol" in s.movement.lower(), (
        f"gustave_moreau movement should reference Symbolism; got {s.movement!r}")


def test_gustave_moreau_nationality():
    s = get_style("gustave_moreau")
    assert s.nationality == "French", (
        f"gustave_moreau nationality should be 'French'; got {s.nationality!r}")


def test_gustave_moreau_palette_length():
    s = get_style("gustave_moreau")
    assert len(s.palette) >= 5, (
        f"gustave_moreau palette should have ≥ 5 colours; got {len(s.palette)}")


def test_gustave_moreau_palette_values_in_range():
    """All palette RGB values for gustave_moreau must be in [0, 1]."""
    s = get_style("gustave_moreau")
    for i, color in enumerate(s.palette):
        for j, channel in enumerate(color):
            assert 0.0 <= channel <= 1.0, (
                f"gustave_moreau palette[{i}][{j}] = {channel} is outside [0, 1]")


def test_gustave_moreau_ground_dark():
    """gustave_moreau ground_color should be dark — warm umber-crimson underpinning."""
    s = get_style("gustave_moreau")
    lum = 0.299 * s.ground_color[0] + 0.587 * s.ground_color[1] + 0.114 * s.ground_color[2]
    assert lum < 0.40, (
        f"gustave_moreau ground_color should be dark (lum < 0.40); got lum={lum:.3f}")


def test_gustave_moreau_palette_has_gold():
    """gustave_moreau palette must contain a gold/warm-yellow entry (R > G > B)."""
    s = get_style("gustave_moreau")
    gold = any(r > 0.60 and r > g and g > b for r, g, b in s.palette)
    assert gold, "gustave_moreau palette must contain a gold/amber entry (R > G > B)"


def test_gustave_moreau_palette_has_crimson():
    """gustave_moreau palette must contain a deep crimson (R dominant, low luminance)."""
    s = get_style("gustave_moreau")
    crimson = any(r > 0.40 and r > 2.5 * g and r > 2.5 * b for r, g, b in s.palette)
    assert crimson, "gustave_moreau palette must contain a deep crimson entry"


def test_gustave_moreau_has_crackle():
    """gustave_moreau crackle should be True — museum-aged large canvases."""
    s = get_style("gustave_moreau")
    assert s.crackle, "gustave_moreau crackle should be True (museum-aged large canvases)"


def test_gustave_moreau_has_warm_glaze():
    """gustave_moreau glazing should be a warm crimson tone, not None."""
    s = get_style("gustave_moreau")
    assert s.glazing is not None, "gustave_moreau glazing should be set (warm crimson unifier)"
    r, g, b = s.glazing
    assert r > g and r > b, (
        "gustave_moreau glazing should be warm (R dominant); "
        f"got R={r:.2f} G={g:.2f} B={b:.2f}")


def test_gustave_moreau_famous_works_not_empty():
    s = get_style("gustave_moreau")
    assert len(s.famous_works) >= 4, (
        f"gustave_moreau famous_works should have ≥ 4 entries; "
        f"got {len(s.famous_works)}")


def test_gustave_moreau_salome_referenced():
    """gustave_moreau famous_works must include Salome — his most iconic work."""
    s = get_style("gustave_moreau")
    titles = [title for title, _ in s.famous_works]
    assert any("salome" in t.lower() for t in titles), (
        "gustave_moreau famous_works must include a Salome painting")


def test_gustave_moreau_inspiration_references_pass():
    """The Moreau catalog entry must reference moreau_gilded_pass."""
    s = get_style("gustave_moreau")
    assert "moreau_gilded_pass" in s.inspiration, (
        "gustave_moreau inspiration must reference moreau_gilded_pass()")


def test_gustave_moreau_stroke_size_fine():
    """gustave_moreau stroke_size should be very fine — miniaturist precision."""
    s = get_style("gustave_moreau")
    assert s.stroke_size <= 6, (
        f"gustave_moreau stroke_size should be ≤ 6 (fine encrusted marks); "
        f"got {s.stroke_size}")


def test_gustave_moreau_low_edge_softness():
    """gustave_moreau edge_softness should be relatively low — crisp draughtsman edges."""
    s = get_style("gustave_moreau")
    assert s.edge_softness <= 0.35, (
        f"gustave_moreau edge_softness should be ≤ 0.35 (crisp contours); "
        f"got {s.edge_softness}")


# ── SYMBOLIST period stroke_params ────────────────────────────────────────────

def test_symbolist_period_in_enum():
    """SYMBOLIST must be a valid Period enum member after session 32."""
    assert hasattr(Period, "SYMBOLIST"), "Period.SYMBOLIST missing from scene_schema"
    assert isinstance(Period.SYMBOLIST, Period)


def test_symbolist_stroke_params_present():
    """SYMBOLIST must have a stroke_params entry covering all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.SYMBOLIST).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"SYMBOLIST stroke_params missing key: {key!r}"


def test_symbolist_stroke_size_face_fine():
    """SYMBOLIST stroke_size_face should be very fine — Moreau's miniaturist precision."""
    sp = Style(medium=Medium.OIL, period=Period.SYMBOLIST).stroke_params
    assert sp["stroke_size_face"] <= 6, (
        f"SYMBOLIST stroke_size_face should be ≤ 6 (fine encrusted marks); "
        f"got {sp['stroke_size_face']}")


def test_symbolist_edge_softness_low():
    """SYMBOLIST edge_softness should be low — Moreau was a draughtsman first."""
    sp = Style(medium=Medium.OIL, period=Period.SYMBOLIST).stroke_params
    assert sp["edge_softness"] <= 0.35, (
        f"SYMBOLIST edge_softness should be ≤ 0.35; got {sp['edge_softness']}")

