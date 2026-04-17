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
    "anthony_van_dyck",
    "artemisia_gentileschi",
    "berthe_morisot",
    "waterhouse",
    "botticelli",
    "bouguereau",
    "bruegel",
    "caravaggio", "caspar_david_friedrich", "cezanne",
    "chardin", "courbet",
    "degas",
    "delacroix",
    "egon_schiele",
    "el_greco", "fra_angelico", "frida_kahlo", "gauguin", "goya", "hilma_af_klint", "hokusai",
    "georges_de_la_tour",
    "holbein_the_younger",
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
    "albrecht_durer",
    "peter_paul_rubens",
    "nicolas_poussin",
    "thomas_gainsborough",
    "winslow_homer",
    "jean_honore_fragonard",
    "pierre_auguste_renoir",
    "munch",
    "frans_hals",
    "salvador_dali",
    "vilhelm_hammershoi",
    "john_constable",
    "giovanni_bellini",
    "pontormo",
    "rogier_van_der_weyden",
    "hans_memling",
    "bronzino",
    "tintoretto",
    "giorgione",
    "veronese",
    "murillo",
    "tiepolo",
    "corot",
    "parmigianino",
    "canaletto",
    "vigee_le_brun",
    "alma_tadema",
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
    "QUATTROCENTO",
    "FRENCH_ROCOCO",
    "EARLY_VENETIAN_RENAISSANCE",
    "FLORENTINE_MANNERIST",
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


def test_artemisia_gentileschi_inspiration_references_dramatic_flesh_pass():
    """Inspiration text must reference gentileschi_dramatic_flesh_pass."""
    s = get_style("artemisia_gentileschi")
    assert "gentileschi_dramatic_flesh" in s.inspiration.lower().replace(" ", "_"), (
        "Gentileschi inspiration should reference gentileschi_dramatic_flesh_pass() — "
        "the dedicated Baroque warm-shadow/candlelit-highlight pass for her style")


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


# ──────────────────────────────────────────────────────────────────────────────
# Albrecht Dürer / NORTHERN_RENAISSANCE — session 34 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_albrecht_durer_in_catalog():
    """albrecht_durer must be present in CATALOG after session 34."""
    assert "albrecht_durer" in CATALOG


def test_albrecht_durer_movement():
    s = get_style("albrecht_durer")
    assert "northern renaissance" in s.movement.lower() or "northern" in s.movement.lower(), (
        f"albrecht_durer movement should reference Northern Renaissance; got {s.movement!r}")


def test_albrecht_durer_nationality():
    s = get_style("albrecht_durer")
    assert s.nationality == "German", (
        f"albrecht_durer nationality should be 'German'; got {s.nationality!r}")


def test_albrecht_durer_palette_length():
    s = get_style("albrecht_durer")
    assert len(s.palette) >= 5, (
        f"albrecht_durer palette should have ≥ 5 colours; got {len(s.palette)}")


def test_albrecht_durer_palette_values_in_range():
    """All palette RGB values for albrecht_durer must be in [0, 1]."""
    s = get_style("albrecht_durer")
    for i, color in enumerate(s.palette):
        for j, channel in enumerate(color):
            assert 0.0 <= channel <= 1.0, (
                f"albrecht_durer palette[{i}][{j}] = {channel} is outside [0, 1]")


def test_albrecht_durer_ground_pale():
    """albrecht_durer ground_color should be pale — silver-white imprimatura on gessoed panel."""
    s = get_style("albrecht_durer")
    lum = 0.299 * s.ground_color[0] + 0.587 * s.ground_color[1] + 0.114 * s.ground_color[2]
    assert lum >= 0.70, (
        f"albrecht_durer ground_color should be pale (lum ≥ 0.70); got lum={lum:.3f}")


def test_albrecht_durer_palette_has_cool_grey():
    """albrecht_durer palette must contain a cool grey/silver tone (near-equal RGB, mid-high value)."""
    s = get_style("albrecht_durer")
    cool_grey = any(
        abs(r - g) < 0.10 and abs(g - b) < 0.10 and r > 0.55
        for r, g, b in s.palette
    )
    assert cool_grey, (
        "albrecht_durer palette must contain a cool grey/silver entry "
        "(Dürer's background and shadow tonality is cool silver-grey)")


def test_albrecht_durer_palette_has_warm_flesh():
    """albrecht_durer palette must contain a warm flesh tone (R dominant in midrange)."""
    s = get_style("albrecht_durer")
    warm_flesh = any(r > 0.70 and r > g and g > b and r < 0.95 for r, g, b in s.palette)
    assert warm_flesh, (
        "albrecht_durer palette must contain a warm ochre flesh entry (R dominant midrange)")


def test_albrecht_durer_has_crackle():
    """albrecht_durer crackle should be True — 500-year-old panel paintings crack extensively."""
    s = get_style("albrecht_durer")
    assert s.crackle, "albrecht_durer crackle should be True (500-year-old gessoed panels)"


def test_albrecht_durer_edge_softness_crisp():
    """albrecht_durer edge_softness should be very low — engraving-precision crisp edges."""
    s = get_style("albrecht_durer")
    assert s.edge_softness <= 0.25, (
        f"albrecht_durer edge_softness should be ≤ 0.25 (engraving-crisp); "
        f"got {s.edge_softness}")


def test_albrecht_durer_stroke_size_fine():
    """albrecht_durer stroke_size should be very fine — single-hair precision marks."""
    s = get_style("albrecht_durer")
    assert s.stroke_size <= 5, (
        f"albrecht_durer stroke_size should be ≤ 5 (single-hair engraving precision); "
        f"got {s.stroke_size}")


def test_albrecht_durer_wet_blend_moderate():
    """albrecht_durer wet_blend should be moderate — thin oil layers, some blending."""
    s = get_style("albrecht_durer")
    assert 0.10 <= s.wet_blend <= 0.40, (
        f"albrecht_durer wet_blend should be 0.10–0.40 (thin oil, not tempera dry nor wet sfumato); "
        f"got {s.wet_blend}")


def test_albrecht_durer_famous_works_not_empty():
    s = get_style("albrecht_durer")
    assert len(s.famous_works) >= 4, (
        f"albrecht_durer famous_works should have ≥ 4 entries; got {len(s.famous_works)}")


def test_albrecht_durer_self_portrait_referenced():
    """albrecht_durer famous_works must include a self-portrait — his most iconic works."""
    s = get_style("albrecht_durer")
    titles = [title for title, _ in s.famous_works]
    assert any("self-portrait" in t.lower() or "self portrait" in t.lower() for t in titles), (
        "albrecht_durer famous_works must include a Self-Portrait")


def test_albrecht_durer_inspiration_references_pass():
    """The Dürer catalog entry must reference durer_engraving_pass."""
    s = get_style("albrecht_durer")
    assert "durer_engraving_pass" in s.inspiration, (
        "albrecht_durer inspiration must reference durer_engraving_pass()")


def test_albrecht_durer_no_warm_glaze():
    """albrecht_durer glazing should be cool (B ≥ R) or very neutral — not Italian warm amber."""
    s = get_style("albrecht_durer")
    if s.glazing is not None:
        r, g, b = s.glazing
        # Cool or neutral: R should not strongly dominate (not >0.20 above B)
        assert r - b <= 0.20, (
            f"albrecht_durer glazing should be cool/neutral (not warm amber); "
            f"got R={r:.2f} G={g:.2f} B={b:.2f}")


# ── NORTHERN_RENAISSANCE period stroke_params ─────────────────────────────────

def test_northern_renaissance_period_in_enum():
    """NORTHERN_RENAISSANCE must be a valid Period enum member after session 34."""
    assert hasattr(Period, "NORTHERN_RENAISSANCE"), (
        "Period.NORTHERN_RENAISSANCE missing from scene_schema")
    assert isinstance(Period.NORTHERN_RENAISSANCE, Period)


def test_northern_renaissance_stroke_params_present():
    """NORTHERN_RENAISSANCE must have a stroke_params entry covering all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.NORTHERN_RENAISSANCE).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"NORTHERN_RENAISSANCE stroke_params missing key: {key!r}"


def test_northern_renaissance_stroke_size_face_fine():
    """NORTHERN_RENAISSANCE stroke_size_face should be very fine — engraving-precision marks."""
    sp = Style(medium=Medium.OIL, period=Period.NORTHERN_RENAISSANCE).stroke_params
    assert sp["stroke_size_face"] <= 5, (
        f"NORTHERN_RENAISSANCE stroke_size_face should be ≤ 5 (single-hair precision); "
        f"got {sp['stroke_size_face']}")


def test_northern_renaissance_edge_softness_crisp():
    """NORTHERN_RENAISSANCE edge_softness should be very low — crisp engraving-influenced edges."""
    sp = Style(medium=Medium.OIL, period=Period.NORTHERN_RENAISSANCE).stroke_params
    assert sp["edge_softness"] <= 0.25, (
        f"NORTHERN_RENAISSANCE edge_softness should be ≤ 0.25 (engraving-crisp); "
        f"got {sp['edge_softness']}")


def test_northern_renaissance_wet_blend_moderate():
    """NORTHERN_RENAISSANCE wet_blend should be moderate — thin oils, some blending."""
    sp = Style(medium=Medium.OIL, period=Period.NORTHERN_RENAISSANCE).stroke_params
    assert 0.10 <= sp["wet_blend"] <= 0.40, (
        f"NORTHERN_RENAISSANCE wet_blend should be 0.10–0.40; got {sp['wet_blend']:.3f}")


def test_northern_renaissance_crisper_than_venetian():
    """NORTHERN_RENAISSANCE edge_softness must be lower than VENETIAN_RENAISSANCE."""
    sp_north = Style(medium=Medium.OIL, period=Period.NORTHERN_RENAISSANCE).stroke_params
    sp_ven   = Style(medium=Medium.OIL, period=Period.VENETIAN_RENAISSANCE).stroke_params
    assert sp_north["edge_softness"] < sp_ven["edge_softness"], (
        "NORTHERN_RENAISSANCE edge_softness must be lower than VENETIAN_RENAISSANCE "
        "(Dürer's engraving-influenced precision is crisper than Titian's rich glazed softness)")


# ──────────────────────────────────────────────────────────────────────────────
# Fra Angelico (Quattrocento) — randomly selected artist for this session
# ──────────────────────────────────────────────────────────────────────────────

def test_fra_angelico_in_catalog():
    """Fra Angelico (this session's randomly selected artist) must appear in CATALOG."""
    assert "fra_angelico" in CATALOG, "fra_angelico missing from CATALOG"


def test_fra_angelico_movement():
    """Fra Angelico's movement must reference International Gothic or Quattrocento."""
    s = get_style("fra_angelico")
    assert ("Gothic" in s.movement or "Quattrocento" in s.movement
            or "Renaissance" in s.movement), (
        f"fra_angelico movement unexpected: {s.movement!r}")


def test_fra_angelico_nationality():
    s = get_style("fra_angelico")
    assert s.nationality == "Italian"


def test_fra_angelico_palette_length():
    s = get_style("fra_angelico")
    assert len(s.palette) >= 6, (
        "Fra Angelico palette should have ≥ 6 entries (lead white, flesh, "
        "sienna shadow, lapis blue, vermilion, gold leaf)")


def test_fra_angelico_palette_values_in_range():
    """All Fra Angelico palette RGB values must be in [0, 1]."""
    s = get_style("fra_angelico")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in fra_angelico palette {rgb}")


def test_fra_angelico_ground_color_pale():
    """Fra Angelico worked on chalk-white gesso — ground_color must be very pale."""
    s = get_style("fra_angelico")
    avg_brightness = sum(s.ground_color) / 3.0
    assert avg_brightness >= 0.80, (
        f"fra_angelico ground_color should be near-white (gesso panel); "
        f"average brightness = {avg_brightness:.3f}")


def test_fra_angelico_wet_blend_near_zero():
    """Egg tempera dries almost instantly — wet_blend must be very low."""
    s = get_style("fra_angelico")
    assert s.wet_blend <= 0.10, (
        f"fra_angelico wet_blend should be ≤ 0.10 (tempera dries instantly); "
        f"got {s.wet_blend}")


def test_fra_angelico_edge_softness_crisp():
    """Fra Angelico uses clear Gothic-influenced contour lines — edge_softness must be low."""
    s = get_style("fra_angelico")
    assert s.edge_softness <= 0.30, (
        f"fra_angelico edge_softness should be ≤ 0.30 (no sfumato, clear contour); "
        f"got {s.edge_softness}")


def test_fra_angelico_no_glazing():
    """Tempera technique predates warm amber oil glazing — glazing should be None."""
    s = get_style("fra_angelico")
    assert s.glazing is None, (
        f"fra_angelico glazing should be None (no unifying oil glaze); "
        f"got {s.glazing!r}")


def test_fra_angelico_crackle():
    """Aged tempera panels crackle — crackle should be True."""
    s = get_style("fra_angelico")
    assert s.crackle is True, "fra_angelico crackle should be True (aged panel)"


def test_fra_angelico_famous_works():
    s = get_style("fra_angelico")
    assert len(s.famous_works) >= 3, "Fra Angelico must have ≥ 3 famous works listed"
    titles = [w[0] for w in s.famous_works]
    assert any("Annunciation" in t or "annunciation" in t.lower()
               for t in titles), (
        "Fra Angelico's famous works must include the Annunciation "
        "(his most canonical work, San Marco c.1438)")


def test_fra_angelico_stroke_size_fine():
    """Tempera hatching uses the finest brush strokes — stroke_size must be very small."""
    s = get_style("fra_angelico")
    assert s.stroke_size <= 5, (
        f"fra_angelico stroke_size should be ≤ 5 (fine tempera hatch); "
        f"got {s.stroke_size}")


# ── QUATTROCENTO period ─────────────────────────────────────────────────────────

def test_quattrocento_period_in_enum():
    """QUATTROCENTO must be a valid Period enum member after this session."""
    assert hasattr(Period, "QUATTROCENTO"), (
        "Period.QUATTROCENTO missing from scene_schema")
    assert isinstance(Period.QUATTROCENTO, Period)


def test_quattrocento_stroke_params_present():
    """QUATTROCENTO must have stroke_params covering all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.QUATTROCENTO).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"QUATTROCENTO stroke_params missing key: {key!r}"


def test_quattrocento_wet_blend_near_zero():
    """QUATTROCENTO wet_blend must be very low — tempera dries instantly."""
    sp = Style(medium=Medium.OIL, period=Period.QUATTROCENTO).stroke_params
    assert sp["wet_blend"] <= 0.10, (
        f"QUATTROCENTO wet_blend should be ≤ 0.10; got {sp['wet_blend']:.3f}")


def test_quattrocento_edge_softness_crisp():
    """QUATTROCENTO edge_softness must be low — clear Gothic contour, no sfumato."""
    sp = Style(medium=Medium.OIL, period=Period.QUATTROCENTO).stroke_params
    assert sp["edge_softness"] <= 0.25, (
        f"QUATTROCENTO edge_softness should be ≤ 0.25; got {sp['edge_softness']:.3f}")


def test_quattrocento_stroke_size_face_fine():
    """QUATTROCENTO stroke_size_face must be very fine — single-hair tempera marks."""
    sp = Style(medium=Medium.OIL, period=Period.QUATTROCENTO).stroke_params
    assert sp["stroke_size_face"] <= 5, (
        f"QUATTROCENTO stroke_size_face should be ≤ 5 (hair-width tempera marks); "
        f"got {sp['stroke_size_face']}")


def test_quattrocento_crisper_than_high_renaissance():
    """QUATTROCENTO edge_softness must be lower than HIGH_RENAISSANCE (no sfumato at all)."""
    sp_quat = Style(medium=Medium.OIL, period=Period.QUATTROCENTO).stroke_params
    sp_high = Style(medium=Medium.OIL, period=Period.HIGH_RENAISSANCE).stroke_params
    assert sp_quat["edge_softness"] < sp_high["edge_softness"], (
        "QUATTROCENTO edge_softness must be crisper than HIGH_RENAISSANCE "
        "(Fra Angelico's contour lines precede the soft modelling of Raphael)")


# ── Hans Holbein the Younger (session 36 addition) ──────────────────────────

def test_holbein_the_younger_in_catalog():
    """holbein_the_younger must be present in CATALOG after this session."""
    assert "holbein_the_younger" in CATALOG, (
        "holbein_the_younger missing from CATALOG — expected after session 36")


def test_holbein_in_expected_artists():
    """EXPECTED_ARTISTS list must include holbein_the_younger."""
    assert "holbein_the_younger" in EXPECTED_ARTISTS, (
        "holbein_the_younger must appear in EXPECTED_ARTISTS for catalog completeness tests")


def test_holbein_movement():
    """Holbein's movement must reference Northern Renaissance."""
    s = get_style("holbein_the_younger")
    assert "Northern Renaissance" in s.movement or "northern renaissance" in s.movement.lower(), (
        f"holbein_the_younger movement should include 'Northern Renaissance'; got {s.movement!r}")


def test_holbein_nationality():
    """Holbein was German-Swiss."""
    s = get_style("holbein_the_younger")
    assert "German" in s.nationality or "Swiss" in s.nationality, (
        f"holbein_the_younger nationality should be German-Swiss; got {s.nationality!r}")


def test_holbein_palette_length():
    """Holbein palette must have at least 6 colours."""
    s = get_style("holbein_the_younger")
    assert len(s.palette) >= 6, (
        f"holbein_the_younger palette should have ≥ 6 colours; got {len(s.palette)}")


def test_holbein_palette_values_in_range():
    """All palette RGB components must be in [0, 1]."""
    s = get_style("holbein_the_younger")
    for i, col in enumerate(s.palette):
        for j, v in enumerate(col):
            assert 0.0 <= v <= 1.0, (
                f"holbein_the_younger palette[{i}][{j}]={v:.3f} out of [0,1]")


def test_holbein_low_wet_blend():
    """Holbein used thin dry glazes — wet_blend must be low (≤ 0.20)."""
    s = get_style("holbein_the_younger")
    assert s.wet_blend <= 0.20, (
        f"holbein_the_younger wet_blend should be ≤ 0.20 (thin glaze, no wet-into-wet); "
        f"got {s.wet_blend:.3f}")


def test_holbein_crisp_edges():
    """Holbein's portraits have extremely crisp outlines — edge_softness must be low (≤ 0.25)."""
    s = get_style("holbein_the_younger")
    assert s.edge_softness <= 0.25, (
        f"holbein_the_younger edge_softness should be ≤ 0.25 (no sfumato, precise contour); "
        f"got {s.edge_softness:.3f}")


def test_holbein_no_chromatic_split():
    """Holbein predates Seurat divisionism — chromatic_split must be False."""
    s = get_style("holbein_the_younger")
    assert s.chromatic_split is False, (
        "holbein_the_younger chromatic_split should be False (no Pointillist technique)")


def test_holbein_crackle():
    """Aged oak panel paintings crackle — crackle should be True."""
    s = get_style("holbein_the_younger")
    assert s.crackle is True, "holbein_the_younger crackle should be True (aged panel)"


def test_holbein_fine_stroke_size():
    """Holbein's technique requires very fine marks — stroke_size must be ≤ 6."""
    s = get_style("holbein_the_younger")
    assert s.stroke_size <= 6, (
        f"holbein_the_younger stroke_size should be ≤ 6 (precise panel technique); "
        f"got {s.stroke_size}")


def test_holbein_famous_works():
    """Holbein must have at least 5 famous works and include The Ambassadors."""
    s = get_style("holbein_the_younger")
    assert len(s.famous_works) >= 5, (
        f"holbein_the_younger should have ≥ 5 famous works; got {len(s.famous_works)}")
    titles = [w[0] for w in s.famous_works]
    assert any("Ambassadors" in t or "ambassadors" in t.lower() for t in titles), (
        "holbein_the_younger famous_works must include 'The Ambassadors' (1533 — his "
        "most celebrated work, now in the National Gallery, London)")


def test_holbein_crisper_than_leonardo():
    """Holbein's edge_softness must be lower than Leonardo's (no sfumato vs. maximum sfumato)."""
    s_holbein  = get_style("holbein_the_younger")
    s_leonardo = get_style("leonardo")
    assert s_holbein.edge_softness < s_leonardo.edge_softness, (
        "holbein_the_younger edge_softness must be crisper than leonardo "
        "(Holbein's precise Northern outlines vs. Leonardo's smoke-dissolved edges)")


def test_holbein_ground_paler_than_rembrandt():
    """Holbein's pale white ground must be lighter than Rembrandt's dark imprimatura."""
    s_holbein  = get_style("holbein_the_younger")
    s_rembrandt = get_style("rembrandt")
    # Ground luminance: 0.299R + 0.587G + 0.114B
    lum_h = (0.299 * s_holbein.ground_color[0]
             + 0.587 * s_holbein.ground_color[1]
             + 0.114 * s_holbein.ground_color[2])
    lum_r = (0.299 * s_rembrandt.ground_color[0]
             + 0.587 * s_rembrandt.ground_color[1]
             + 0.114 * s_rembrandt.ground_color[2])
    assert lum_h > lum_r, (
        f"holbein_the_younger ground ({lum_h:.3f}) should be lighter than "
        f"rembrandt ground ({lum_r:.3f})")


# ── Anthony van Dyck (session 37 addition) ───────────────────────────────────

def test_van_dyck_in_catalog():
    """anthony_van_dyck must be present in CATALOG after this session."""
    assert "anthony_van_dyck" in CATALOG, (
        "anthony_van_dyck missing from CATALOG — expected after session 37")


def test_van_dyck_in_expected_artists():
    """EXPECTED_ARTISTS list must include anthony_van_dyck."""
    assert "anthony_van_dyck" in EXPECTED_ARTISTS, (
        "anthony_van_dyck must appear in EXPECTED_ARTISTS for catalog completeness tests")


def test_van_dyck_movement():
    """Van Dyck's movement must reference Baroque."""
    s = get_style("anthony_van_dyck")
    assert "baroque" in s.movement.lower(), (
        f"anthony_van_dyck movement should include 'Baroque'; got {s.movement!r}")


def test_van_dyck_nationality():
    """Van Dyck was Flemish."""
    s = get_style("anthony_van_dyck")
    assert "Flemish" in s.nationality or "flemish" in s.nationality.lower(), (
        f"anthony_van_dyck nationality should be Flemish; got {s.nationality!r}")


def test_van_dyck_palette_length():
    """Van Dyck palette must have at least 6 colours (flesh, silk, Van Dyck brown, black, crimson, ultramarine)."""
    s = get_style("anthony_van_dyck")
    assert len(s.palette) >= 6, (
        f"anthony_van_dyck palette should have ≥ 6 colours; got {len(s.palette)}")


def test_van_dyck_palette_values_in_range():
    """All Van Dyck palette RGB components must be in [0, 1]."""
    s = get_style("anthony_van_dyck")
    for i, col in enumerate(s.palette):
        for j, v in enumerate(col):
            assert 0.0 <= v <= 1.0, (
                f"anthony_van_dyck palette[{i}][{j}]={v:.3f} out of [0,1]")


def test_van_dyck_moderate_wet_blend():
    """Van Dyck worked wet-into-wet but not as heavily as Titian — wet_blend between 0.30 and 0.65."""
    s = get_style("anthony_van_dyck")
    assert 0.30 <= s.wet_blend <= 0.65, (
        f"anthony_van_dyck wet_blend should be in [0.30, 0.65] (fluid Baroque blending); "
        f"got {s.wet_blend:.3f}")


def test_van_dyck_moderate_edge_softness():
    """Van Dyck's edges are present but yielding — edge_softness between 0.30 and 0.65."""
    s = get_style("anthony_van_dyck")
    assert 0.30 <= s.edge_softness <= 0.65, (
        f"anthony_van_dyck edge_softness should be in [0.30, 0.65] "
        f"(neither sfumato nor razor-crisp Northern edge); got {s.edge_softness:.3f}")


def test_van_dyck_has_glazing():
    """Van Dyck applied a warm amber-brown final varnish — glazing must not be None."""
    s = get_style("anthony_van_dyck")
    assert s.glazing is not None, (
        "anthony_van_dyck glazing should not be None — warm amber-brown final varnish")
    assert len(s.glazing) == 3
    for ch in s.glazing:
        assert 0.0 <= ch <= 1.0, f"anthony_van_dyck glazing channel {ch:.3f} out of [0,1]"


def test_van_dyck_crackle():
    """Aged canvas paintings crackle — crackle should be True."""
    s = get_style("anthony_van_dyck")
    assert s.crackle is True, "anthony_van_dyck crackle should be True (aged canvas)"


def test_van_dyck_no_chromatic_split():
    """Van Dyck predates Seurat divisionism — chromatic_split must be False."""
    s = get_style("anthony_van_dyck")
    assert s.chromatic_split is False, (
        "anthony_van_dyck chromatic_split should be False (no Pointillist technique)")


def test_van_dyck_famous_works():
    """Van Dyck must have at least 4 famous works and include Charles I."""
    s = get_style("anthony_van_dyck")
    assert len(s.famous_works) >= 4, (
        f"anthony_van_dyck should have ≥ 4 famous works; got {len(s.famous_works)}")
    titles = [w[0] for w in s.famous_works]
    assert any("Charles" in t for t in titles), (
        "anthony_van_dyck famous_works must include a portrait of Charles I "
        "(his most celebrated patron; multiple iconic works from the London period)")


def test_van_dyck_silk_palette_present():
    """Van Dyck's signature silver-grey silk colour must be in his palette."""
    s = get_style("anthony_van_dyck")
    # Silver-grey silk: R ≈ G ≈ B in the mid-to-high range; look for a near-neutral bright entry
    def _is_silver_grey(rgb):
        r, g, b = rgb
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        v   = max(r, g, b)
        c   = v - min(r, g, b)
        sat = c / (v + 1e-6) if v > 1e-6 else 0.0
        return lum >= 0.50 and sat <= 0.20   # bright, near-neutral grey
    assert any(_is_silver_grey(rgb) for rgb in s.palette), (
        "anthony_van_dyck palette must contain at least one silver-grey colour "
        "(his defining silk-drapery tone)")


def test_van_dyck_darker_ground_than_holbein():
    """Van Dyck's warm dark imprimatura must be darker than Holbein's near-white buff ground."""
    s_vd = get_style("anthony_van_dyck")
    s_hb = get_style("holbein_the_younger")
    lum_vd = (0.299 * s_vd.ground_color[0]
              + 0.587 * s_vd.ground_color[1]
              + 0.114 * s_vd.ground_color[2])
    lum_hb = (0.299 * s_hb.ground_color[0]
              + 0.587 * s_hb.ground_color[1]
              + 0.114 * s_hb.ground_color[2])
    assert lum_vd < lum_hb, (
        f"anthony_van_dyck ground ({lum_vd:.3f}) should be darker than "
        f"holbein_the_younger ground ({lum_hb:.3f}) — warm dark imprimatura vs. near-white buff")


# ═════════════════════════════════════════════════════════════════════════════
# Peter Paul Rubens — catalog tests
# ═════════════════════════════════════════════════════════════════════════════

def test_rubens_in_catalog():
    """peter_paul_rubens must be present in CATALOG."""
    assert "peter_paul_rubens" in CATALOG, (
        "peter_paul_rubens not found in CATALOG — add the ArtStyle entry")


def test_rubens_palette_valid():
    """Every colour in peter_paul_rubens palette must have RGB channels in [0, 1]."""
    s = get_style("peter_paul_rubens")
    for i, rgb in enumerate(s.palette):
        for j, v in enumerate(rgb):
            assert 0.0 <= v <= 1.0, (
                f"peter_paul_rubens palette[{i}][{j}]={v:.3f} out of [0, 1]")


def test_rubens_warm_ground():
    """peter_paul_rubens ground must be warm (R > B) — reddish-brown imprimatura."""
    s = get_style("peter_paul_rubens")
    r, g, b = s.ground_color
    assert r > b, (
        f"peter_paul_rubens ground_color R={r:.3f} should exceed B={b:.3f} "
        f"(warm reddish-brown imprimatura, not cold grey)")


def test_rubens_high_wet_blend():
    """peter_paul_rubens wet_blend should be >= 0.55 for fluid wet-on-wet alla prima."""
    s = get_style("peter_paul_rubens")
    assert s.wet_blend >= 0.55, (
        f"peter_paul_rubens wet_blend={s.wet_blend:.2f} should be >= 0.55 "
        "(Rubens worked wet-on-wet through multiple layers; fluid blending is essential)")


def test_rubens_moderate_edge_softness():
    """peter_paul_rubens edge_softness should be in [0.30, 0.60] — present but readable."""
    s = get_style("peter_paul_rubens")
    assert 0.30 <= s.edge_softness <= 0.60, (
        f"peter_paul_rubens edge_softness={s.edge_softness:.2f} should be in [0.30, 0.60] "
        "(Rubens' edges are soft but not sfumato — forms remain clearly bounded)")


def test_rubens_has_glazing():
    """peter_paul_rubens glazing must not be None — warm amber-red unifying glaze."""
    s = get_style("peter_paul_rubens")
    assert s.glazing is not None, (
        "peter_paul_rubens glazing should not be None — warm amber-red final varnish")
    for ch in s.glazing:
        assert 0.0 <= ch <= 1.0, (
            f"peter_paul_rubens glazing channel {ch:.3f} out of [0, 1]")


def test_rubens_warm_glazing():
    """peter_paul_rubens glazing must be warm (R > B) — amber-red, not cool."""
    s = get_style("peter_paul_rubens")
    r, g, b = s.glazing
    assert r > b, (
        f"peter_paul_rubens glazing R={r:.3f} should exceed B={b:.3f} "
        "(Rubens' unifying glaze is warm amber-red, never cool)")


def test_rubens_crackle():
    """peter_paul_rubens crackle should be True — large oil canvases age and crackle."""
    s = get_style("peter_paul_rubens")
    assert s.crackle is True, (
        "peter_paul_rubens crackle should be True (aged oil canvas on large panel/linen)")


def test_rubens_no_chromatic_split():
    """peter_paul_rubens chromatic_split should be False — no Pointillist technique."""
    s = get_style("peter_paul_rubens")
    assert s.chromatic_split is False, (
        "peter_paul_rubens chromatic_split should be False (no Seurat/divisionist dots)")


def test_rubens_famous_works():
    """peter_paul_rubens should have >= 5 famous works including The Descent from the Cross."""
    s = get_style("peter_paul_rubens")
    assert len(s.famous_works) >= 5, (
        f"peter_paul_rubens should have >= 5 famous works; got {len(s.famous_works)}")
    titles = [t for t, _ in s.famous_works]
    assert any("Descent" in t for t in titles), (
        "peter_paul_rubens famous_works must include 'The Descent from the Cross' "
        "— his most celebrated altarpiece in Antwerp Cathedral")


def test_rubens_palette_has_warm_flesh():
    """peter_paul_rubens palette must contain at least one warm cream flesh highlight."""
    s = get_style("peter_paul_rubens")

    def _is_warm_cream(rgb):
        r, g, b = rgb
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        return lum >= 0.60 and r > b and r > g * 0.85   # bright, warm-dominant

    assert any(_is_warm_cream(rgb) for rgb in s.palette), (
        "peter_paul_rubens palette must contain at least one warm cream flesh colour "
        "(lead white + naples yellow — his hallmark highlight tone)")


def test_rubens_palette_has_rosy_blush():
    """peter_paul_rubens palette must contain a reddish-pink blush tone."""
    s = get_style("peter_paul_rubens")

    def _is_rosy(rgb):
        r, g, b = rgb
        return r > 0.65 and r > g * 1.30 and r > b * 1.50   # clearly red-dominant blush

    assert any(_is_rosy(rgb) for rgb in s.palette), (
        "peter_paul_rubens palette must contain a reddish-pink blush tone "
        "(vermilion applied to thin-skin zones — cheeks, ears, lips, knuckles)")


def test_rubens_ground_similar_warmth_to_van_dyck():
    """
    Rubens and Van Dyck share warm imprimatura tradition;
    both grounds must be warm (R > B), though specific values may differ.
    """
    s_rb = get_style("peter_paul_rubens")
    s_vd = get_style("anthony_van_dyck")
    r_rb, _, b_rb = s_rb.ground_color
    r_vd, _, b_vd = s_vd.ground_color
    assert r_rb > b_rb, (
        f"peter_paul_rubens ground must be warm (R={r_rb:.3f} > B={b_rb:.3f})")
    assert r_vd > b_vd, (
        f"anthony_van_dyck ground must be warm (R={r_vd:.3f} > B={b_vd:.3f})")


# ═════════════════════════════════════════════════════════════════════════════
# Nicolas Poussin — catalog tests
# ═════════════════════════════════════════════════════════════════════════════

def test_nicolas_poussin_in_catalog():
    """nicolas_poussin must be present in CATALOG."""
    assert "nicolas_poussin" in CATALOG, (
        "nicolas_poussin not found in CATALOG — add the ArtStyle entry")


def test_nicolas_poussin_palette_valid():
    """Every colour in nicolas_poussin palette must have RGB channels in [0, 1]."""
    s = get_style("nicolas_poussin")
    for i, rgb in enumerate(s.palette):
        for j, v in enumerate(rgb):
            assert 0.0 <= v <= 1.0, (
                f"nicolas_poussin palette[{i}][{j}]={v:.3f} out of [0, 1]")


def test_nicolas_poussin_cool_glazing():
    """
    nicolas_poussin glazing must be cool or near-neutral (B >= R) — silver, not warm amber.
    Poussin's unifying glaze is cool-silvery, the opposite of the warm amber of Rubens/Rembrandt.
    """
    s = get_style("nicolas_poussin")
    assert s.glazing is not None, (
        "nicolas_poussin glazing should not be None — cool silver-neutral glaze")
    r, g, b = s.glazing
    assert b >= r, (
        f"nicolas_poussin glazing B={b:.3f} should be >= R={r:.3f} "
        "(cool-silver unifying glaze, NOT warm amber like Rubens/Rembrandt)")


def test_nicolas_poussin_moderate_wet_blend():
    """
    nicolas_poussin wet_blend should be in [0.25, 0.55] — deliberate layering,
    neither sfumato (>0.85) nor completely dry (< 0.15).
    """
    s = get_style("nicolas_poussin")
    assert 0.25 <= s.wet_blend <= 0.55, (
        f"nicolas_poussin wet_blend={s.wet_blend:.2f} should be in [0.25, 0.55] "
        "(Poussin layered deliberately — moderate blending, not wet-on-wet alla prima)")


def test_nicolas_poussin_clear_edges():
    """
    nicolas_poussin edge_softness should be in [0.30, 0.55] — classical clarity,
    neither sfumato haze (>0.85) nor razor-sharp Tenebrist (< 0.20).
    """
    s = get_style("nicolas_poussin")
    assert 0.30 <= s.edge_softness <= 0.55, (
        f"nicolas_poussin edge_softness={s.edge_softness:.2f} should be in [0.30, 0.55] "
        "(classical edges read as rational sculpture — present but not sfumato)")


def test_nicolas_poussin_crackle():
    """nicolas_poussin crackle should be True — old master oil on canvas/panel."""
    s = get_style("nicolas_poussin")
    assert s.crackle is True, (
        "nicolas_poussin crackle should be True (aged 17th-century oil on canvas)")


def test_nicolas_poussin_no_chromatic_split():
    """nicolas_poussin chromatic_split should be False — no Pointillist technique."""
    s = get_style("nicolas_poussin")
    assert s.chromatic_split is False, (
        "nicolas_poussin chromatic_split should be False (no Seurat/divisionist dots)")


def test_nicolas_poussin_famous_works():
    """nicolas_poussin should have >= 4 famous works including Et in Arcadia Ego."""
    s = get_style("nicolas_poussin")
    assert len(s.famous_works) >= 4, (
        f"nicolas_poussin should have >= 4 famous works; got {len(s.famous_works)}")
    titles = [t for t, _ in s.famous_works]
    assert any("Arcadia" in t for t in titles), (
        "nicolas_poussin famous_works must include 'Et in Arcadia Ego' "
        "— his most celebrated and philosophically resonant masterpiece")


def test_nicolas_poussin_palette_has_azure():
    """nicolas_poussin palette must contain at least one blue-dominant colour (the Poussin azure)."""
    s = get_style("nicolas_poussin")

    def _is_azure(rgb):
        r, g, b = rgb
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        return b > r * 1.40 and b > 0.35 and lum > 0.20

    assert any(_is_azure(rgb) for rgb in s.palette), (
        "nicolas_poussin palette must contain at least one azure blue colour "
        "(his signature garment hue — ultramarine or smalt blue)")


def test_nicolas_poussin_cooler_glaze_than_rubens():
    """
    nicolas_poussin glaze must be cooler (higher B/R ratio) than peter_paul_rubens glaze.
    This encodes the fundamental chromatic distinction between French Classicism and Flemish Baroque.
    """
    s_poussin = get_style("nicolas_poussin")
    s_rubens  = get_style("peter_paul_rubens")

    r_p, _, b_p = s_poussin.glazing
    r_r, _, b_r = s_rubens.glazing

    ratio_poussin = b_p / (r_p + 1e-6)
    ratio_rubens  = b_r / (r_r + 1e-6)

    assert ratio_poussin > ratio_rubens, (
        f"nicolas_poussin glaze B/R ratio ({ratio_poussin:.3f}) should exceed "
        f"peter_paul_rubens ratio ({ratio_rubens:.3f}) — "
        "Poussin's glaze is cool-silvery; Rubens' is warm amber")


# ═════════════════════════════════════════════════════════════════════════════
# Thomas Gainsborough — catalog tests
# ═════════════════════════════════════════════════════════════════════════════

def test_thomas_gainsborough_in_catalog():
    """thomas_gainsborough must be present in CATALOG."""
    assert "thomas_gainsborough" in CATALOG, (
        "thomas_gainsborough not found in CATALOG — add the ArtStyle entry")


def test_thomas_gainsborough_palette_valid():
    """Every colour in thomas_gainsborough palette must have RGB channels in [0, 1]."""
    s = get_style("thomas_gainsborough")
    for i, rgb in enumerate(s.palette):
        for j, v in enumerate(rgb):
            assert 0.0 <= v <= 1.0, (
                f"thomas_gainsborough palette[{i}][{j}]={v:.3f} out of [0, 1]")


def test_thomas_gainsborough_cool_glazing():
    """
    thomas_gainsborough glazing must be cool (B > R) — blue-silver, not warm amber.
    Gainsborough's unifying veil is even cooler than Poussin's; it carries the
    English atmospheric sky colour into the whole composition.
    """
    s = get_style("thomas_gainsborough")
    assert s.glazing is not None, (
        "thomas_gainsborough glazing should not be None — cool blue-silver glaze")
    r, g, b = s.glazing
    assert b > r, (
        f"thomas_gainsborough glazing B={b:.3f} should exceed R={r:.3f} "
        "(cool blue-silver atmospheric veil — English sky tonality)")


def test_thomas_gainsborough_cooler_glaze_than_poussin():
    """
    thomas_gainsborough glaze must be cooler (higher B/R ratio) than nicolas_poussin glaze.
    Gainsborough pushed even further toward cool blue-silver than Poussin's neutral-cool.
    """
    s_g = get_style("thomas_gainsborough")
    s_p = get_style("nicolas_poussin")

    r_g, _, b_g = s_g.glazing
    r_p, _, b_p = s_p.glazing

    ratio_g = b_g / (r_g + 1e-6)
    ratio_p = b_p / (r_p + 1e-6)

    assert ratio_g >= ratio_p, (
        f"thomas_gainsborough glaze B/R ratio ({ratio_g:.3f}) should be >= "
        f"nicolas_poussin ratio ({ratio_p:.3f}) — "
        "Gainsborough's glaze is English-sky cool; Poussin's is neutral-silver")


def test_thomas_gainsborough_high_edge_softness():
    """
    thomas_gainsborough edge_softness should be in [0.55, 0.85] — his feathery
    dissolution of figure into background is a defining quality.
    """
    s = get_style("thomas_gainsborough")
    assert 0.55 <= s.edge_softness <= 0.85, (
        f"thomas_gainsborough edge_softness={s.edge_softness:.2f} should be in [0.55, 0.85] "
        "(feathery dissolution of figure into background — Gainsborough's hallmark)")


def test_thomas_gainsborough_moderate_high_wet_blend():
    """
    thomas_gainsborough wet_blend should be in [0.40, 0.70] — fluid wet-into-wet
    application; each feathered mark blends at its tip into the previous layer.
    """
    s = get_style("thomas_gainsborough")
    assert 0.40 <= s.wet_blend <= 0.70, (
        f"thomas_gainsborough wet_blend={s.wet_blend:.2f} should be in [0.40, 0.70] "
        "(fluid wet-into-wet application — thin oil layers, feathery blending)")


def test_thomas_gainsborough_crackle():
    """thomas_gainsborough crackle should be True — aged 18th-century oil on canvas."""
    s = get_style("thomas_gainsborough")
    assert s.crackle is True, (
        "thomas_gainsborough crackle should be True (aged 18th-century oil on canvas)")


def test_thomas_gainsborough_no_chromatic_split():
    """thomas_gainsborough chromatic_split should be False — no Pointillist technique."""
    s = get_style("thomas_gainsborough")
    assert s.chromatic_split is False, (
        "thomas_gainsborough chromatic_split should be False (no divisionist dots)")


def test_thomas_gainsborough_famous_works():
    """thomas_gainsborough should have >= 4 famous works including The Blue Boy."""
    s = get_style("thomas_gainsborough")
    assert len(s.famous_works) >= 4, (
        f"thomas_gainsborough should have >= 4 famous works; got {len(s.famous_works)}")
    titles = [t for t, _ in s.famous_works]
    assert any("Blue Boy" in t for t in titles), (
        "thomas_gainsborough famous_works must include 'The Blue Boy' "
        "— his most iconic portrait (c. 1770, Huntington Library)")


def test_thomas_gainsborough_palette_has_silver_highlight():
    """thomas_gainsborough palette must contain at least one cool silver-white highlight."""
    s = get_style("thomas_gainsborough")

    def _is_silver_highlight(rgb):
        r, g, b = rgb
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        return lum >= 0.75 and b >= r * 0.90   # bright, and not strongly warm

    assert any(_is_silver_highlight(rgb) for rgb in s.palette), (
        "thomas_gainsborough palette must contain at least one cool silver-white highlight "
        "(B >= R*0.90 and lum >= 0.75) — his characteristic pearl-grey highlight tone")


def test_thomas_gainsborough_palette_has_atmospheric_blue():
    """thomas_gainsborough palette must contain at least one cool blue-grey (atmospheric haze)."""
    s = get_style("thomas_gainsborough")

    def _is_atmospheric_blue(rgb):
        r, g, b = rgb
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        return b > r * 1.15 and 0.30 <= lum <= 0.80   # blue-dominant mid-range

    assert any(_is_atmospheric_blue(rgb) for rgb in s.palette), (
        "thomas_gainsborough palette must contain at least one cool blue-grey atmospheric "
        "haze colour (sky, background, drapery cool accents)")


def test_thomas_gainsborough_ground_is_pale():
    """
    thomas_gainsborough ground must be pale (lum >= 0.55) — he used a light grey-cream
    preparation, much cooler and lighter than the warm Baroque reddish imprimatura.
    """
    s = get_style("thomas_gainsborough")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum >= 0.55, (
        f"thomas_gainsborough ground luminance={lum:.3f} should be >= 0.55 "
        "(pale grey-cream ground — far lighter than warm reddish Baroque imprimatura)")


def test_thomas_gainsborough_is_british_movement():
    """thomas_gainsborough movement should reference British style."""
    s = get_style("thomas_gainsborough")
    assert "British" in s.movement or "Rococo" in s.movement, (
        f"thomas_gainsborough movement={s.movement!r} should reference "
        "'British' or 'Rococo' (British Rococo / Grand Manner Portrait)")


# ═══════════════════════════════════════════════════════════════════════════
# ROCOCO_PORTRAIT period enum tests — Thomas Gainsborough (session 40)
# ═══════════════════════════════════════════════════════════════════════════

def test_rococo_portrait_period_in_enum():
    """Period.ROCOCO_PORTRAIT must be a valid member of the Period enum."""
    assert hasattr(Period, "ROCOCO_PORTRAIT"), (
        "Period enum is missing ROCOCO_PORTRAIT — add it to scene_schema.py")


def test_rococo_portrait_stroke_params_keys():
    """ROCOCO_PORTRAIT stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.ROCOCO_PORTRAIT).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"ROCOCO_PORTRAIT stroke_params missing key: {key!r}"


def test_rococo_portrait_stroke_params_ranges():
    """ROCOCO_PORTRAIT stroke_params values must be in valid ranges."""
    sp = Style(medium=Medium.OIL, period=Period.ROCOCO_PORTRAIT).stroke_params
    assert 3 <= sp["stroke_size_face"] <= 20, (
        f"ROCOCO_PORTRAIT stroke_size_face={sp['stroke_size_face']} should be in [3, 20]")
    assert 0.0 <= sp["wet_blend"] <= 1.0, (
        f"ROCOCO_PORTRAIT wet_blend={sp['wet_blend']} should be in [0, 1]")
    assert 0.0 <= sp["edge_softness"] <= 1.0, (
        f"ROCOCO_PORTRAIT edge_softness={sp['edge_softness']} should be in [0, 1]")


def test_rococo_portrait_high_edge_softness():
    """ROCOCO_PORTRAIT edge_softness should be >= 0.55 — feathery dissolution of edges."""
    sp = Style(medium=Medium.OIL, period=Period.ROCOCO_PORTRAIT).stroke_params
    assert sp["edge_softness"] >= 0.55, (
        f"ROCOCO_PORTRAIT edge_softness={sp['edge_softness']:.2f} should be >= 0.55 "
        "(Gainsborough's feathery edges require high softness)")


# ═══════════════════════════════════════════════════════════════════════════
# Winslow Homer — art catalog tests (session 41)
# ═══════════════════════════════════════════════════════════════════════════

def test_winslow_homer_in_catalog():
    """winslow_homer must be present in CATALOG (session 41 addition)."""
    assert "winslow_homer" in CATALOG, "winslow_homer not found in CATALOG"


def test_winslow_homer_in_expected_artists():
    """winslow_homer must appear in the EXPECTED_ARTISTS list used by test_all_expected_artists_present."""
    assert "winslow_homer" in EXPECTED_ARTISTS, (
        "winslow_homer missing from EXPECTED_ARTISTS — add it to the list")


def test_winslow_homer_movement_american():
    """winslow_homer movement must reference American painting."""
    s = get_style("winslow_homer")
    assert "American" in s.movement or "american" in s.movement.lower(), (
        f"winslow_homer movement={s.movement!r} should reference 'American'")


def test_winslow_homer_nationality():
    """winslow_homer was American."""
    s = get_style("winslow_homer")
    assert "American" in s.nationality, (
        f"winslow_homer nationality should be American; got: {s.nationality!r}")


def test_winslow_homer_palette_length():
    """winslow_homer palette should have at least 7 key colours."""
    s = get_style("winslow_homer")
    assert len(s.palette) >= 7, (
        f"winslow_homer palette should have >= 7 colours; got {len(s.palette)}")


def test_winslow_homer_palette_in_range():
    """All winslow_homer palette RGB values must be in [0, 1]."""
    s = get_style("winslow_homer")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in winslow_homer palette {rgb}")


def test_winslow_homer_pale_ground():
    """
    winslow_homer ground must be very pale (lum >= 0.88) — near-white gessoed
    panel or paper is the foundation of his transparent-wash technique.
    """
    s = get_style("winslow_homer")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum >= 0.88, (
        f"winslow_homer ground luminance={lum:.3f} should be >= 0.88 "
        "(near-white ground — Homer's transparent washes require a luminous support)")


def test_winslow_homer_palette_has_ocean_blue():
    """winslow_homer palette must include a dominant cool blue (Atlantic ocean shadow)."""
    s = get_style("winslow_homer")
    has_ocean_blue = any(
        b > 0.50 and b > r + 0.12
        for r, g, b in s.palette
    )
    assert has_ocean_blue, (
        "winslow_homer palette should include a cool blue for Atlantic ocean shadows "
        "(B > 0.50 and B > R + 0.12)")


def test_winslow_homer_famous_works_contain_breezing_up():
    """winslow_homer famous_works should include 'Breezing Up' — his most iconic oil."""
    s = get_style("winslow_homer")
    titles = [w[0] for w in s.famous_works]
    assert any("Breezing" in t for t in titles), (
        f"winslow_homer famous_works should include 'Breezing Up'; got: {titles}")


def test_winslow_homer_inspiration_references_homer_pass():
    """winslow_homer inspiration text should reference homer_marine_clarity_pass."""
    s = get_style("winslow_homer")
    assert "homer_marine_clarity_pass" in s.inspiration, (
        "winslow_homer inspiration should reference homer_marine_clarity_pass()")


def test_winslow_homer_moderate_wet_blend():
    """
    winslow_homer wet_blend must be in [0.20, 0.45] — decisive, unretouched
    strokes with limited wet-into-wet blending.
    """
    s = get_style("winslow_homer")
    assert 0.20 <= s.wet_blend <= 0.45, (
        f"winslow_homer wet_blend={s.wet_blend:.2f} should be in [0.20, 0.45] "
        "(decisive strokes — not overly blended like Academic, not dry like Flemish)")


def test_winslow_homer_moderate_edge_softness():
    """
    winslow_homer edge_softness should be in [0.22, 0.50] — marine silhouettes
    and horizon lines are crisp; only far atmospheric distance softens.
    """
    s = get_style("winslow_homer")
    assert 0.22 <= s.edge_softness <= 0.50, (
        f"winslow_homer edge_softness={s.edge_softness:.2f} should be in [0.22, 0.50] "
        "(clear silhouette edges — not sfumato-dissolved)")


# ═══════════════════════════════════════════════════════════════════════════
# AMERICAN_MARINE period enum tests — Winslow Homer (session 41)
# ═══════════════════════════════════════════════════════════════════════════

def test_american_marine_period_in_enum():
    """Period.AMERICAN_MARINE must be a valid member of the Period enum."""
    assert hasattr(Period, "AMERICAN_MARINE"), (
        "Period enum is missing AMERICAN_MARINE — add it to scene_schema.py")


def test_american_marine_stroke_params_keys():
    """AMERICAN_MARINE stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.AMERICAN_MARINE).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"AMERICAN_MARINE stroke_params missing key: {key!r}"


def test_american_marine_stroke_params_ranges():
    """AMERICAN_MARINE stroke_params values must be in valid numeric ranges."""
    sp = Style(medium=Medium.OIL, period=Period.AMERICAN_MARINE).stroke_params
    assert 3 <= sp["stroke_size_face"] <= 20, (
        f"AMERICAN_MARINE stroke_size_face={sp['stroke_size_face']} should be in [3, 20]")
    assert 0.0 <= sp["wet_blend"] <= 1.0, (
        f"AMERICAN_MARINE wet_blend={sp['wet_blend']} should be in [0, 1]")
    assert 0.0 <= sp["edge_softness"] <= 1.0, (
        f"AMERICAN_MARINE edge_softness={sp['edge_softness']} should be in [0, 1]")


def test_american_marine_moderate_edge_softness():
    """AMERICAN_MARINE edge_softness should be in [0.22, 0.50] — marine edges are present."""
    sp = Style(medium=Medium.OIL, period=Period.AMERICAN_MARINE).stroke_params
    assert 0.22 <= sp["edge_softness"] <= 0.50, (
        f"AMERICAN_MARINE edge_softness={sp['edge_softness']:.2f} should be in [0.22, 0.50] "
        "(Homer's silhouette edges are crisp — not dissolved like Gainsborough)")


def test_american_marine_moderate_wet_blend():
    """AMERICAN_MARINE wet_blend should be in [0.20, 0.45] — decisive brushwork."""
    sp = Style(medium=Medium.OIL, period=Period.AMERICAN_MARINE).stroke_params
    assert 0.20 <= sp["wet_blend"] <= 0.45, (
        f"AMERICAN_MARINE wet_blend={sp['wet_blend']:.2f} should be in [0.20, 0.45] "
        "(Homer placed strokes once and left them — no heavy wet-on-wet blending)")


# ═══════════════════════════════════════════════════════════════════════════
# Jean-Honoré Fragonard — art catalog tests (session 42)
# ═══════════════════════════════════════════════════════════════════════════

def test_jean_honore_fragonard_in_catalog():
    """jean_honore_fragonard must be present in CATALOG (session 42 addition)."""
    assert "jean_honore_fragonard" in CATALOG, "jean_honore_fragonard not found in CATALOG"


def test_jean_honore_fragonard_in_expected_artists():
    """jean_honore_fragonard must appear in the EXPECTED_ARTISTS list."""
    assert "jean_honore_fragonard" in EXPECTED_ARTISTS, (
        "jean_honore_fragonard missing from EXPECTED_ARTISTS — add it to the list")


def test_jean_honore_fragonard_movement_french_rococo():
    """jean_honore_fragonard movement must reference French Rococo."""
    s = get_style("jean_honore_fragonard")
    assert "Rococo" in s.movement or "rococo" in s.movement.lower(), (
        f"jean_honore_fragonard movement={s.movement!r} should reference 'Rococo'")


def test_jean_honore_fragonard_nationality():
    """jean_honore_fragonard was French."""
    s = get_style("jean_honore_fragonard")
    assert "French" in s.nationality, (
        f"jean_honore_fragonard nationality should be French; got: {s.nationality!r}")


def test_jean_honore_fragonard_palette_length():
    """jean_honore_fragonard palette should have at least 7 key colours."""
    s = get_style("jean_honore_fragonard")
    assert len(s.palette) >= 7, (
        f"jean_honore_fragonard palette should have >= 7 colours; got {len(s.palette)}")


def test_jean_honore_fragonard_palette_in_range():
    """All jean_honore_fragonard palette RGB values must be in [0, 1]."""
    s = get_style("jean_honore_fragonard")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in jean_honore_fragonard palette {rgb}")


def test_jean_honore_fragonard_warm_ground():
    """
    jean_honore_fragonard ground must be warm (R > B) and pale (lum >= 0.70) —
    the warm cream-ivory preparation that unifies his garden-afternoon palette.
    """
    s = get_style("jean_honore_fragonard")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert r > b, (
        f"jean_honore_fragonard ground_color R={r:.3f} should exceed B={b:.3f} "
        "(warm cream-ivory ground — not cool northern grey)")
    assert lum >= 0.70, (
        f"jean_honore_fragonard ground luminance={lum:.3f} should be >= 0.70 "
        "(pale warm ground — Fragonard's warmth glows through thin paint layers)")


def test_jean_honore_fragonard_warm_glazing():
    """jean_honore_fragonard glazing must be warm (R > B) — honey-amber afternoon glow."""
    s = get_style("jean_honore_fragonard")
    assert s.glazing is not None, (
        "jean_honore_fragonard glazing should not be None — warm honey-amber final varnish")
    r, g, b = s.glazing
    assert r > b, (
        f"jean_honore_fragonard glazing R={r:.3f} should exceed B={b:.3f} "
        "(warm honey-amber glaze — the opposite of Gainsborough's cool silver glaze)")


def test_jean_honore_fragonard_high_wet_blend():
    """jean_honore_fragonard wet_blend should be >= 0.55 — fluid bravura alla prima."""
    s = get_style("jean_honore_fragonard")
    assert s.wet_blend >= 0.55, (
        f"jean_honore_fragonard wet_blend={s.wet_blend:.2f} should be >= 0.55 "
        "(Fragonard painted alla prima, often completing a canvas wet-into-wet in one sitting)")


def test_jean_honore_fragonard_moderate_edge_softness():
    """jean_honore_fragonard edge_softness should be in [0.40, 0.65] — spirited but not dissolved."""
    s = get_style("jean_honore_fragonard")
    assert 0.40 <= s.edge_softness <= 0.65, (
        f"jean_honore_fragonard edge_softness={s.edge_softness:.2f} should be in [0.40, 0.65] "
        "(edges tapered at stroke tips but the stroke body is legible — not sfumato-dissolved)")


def test_jean_honore_fragonard_crackle():
    """jean_honore_fragonard crackle should be True — aged 18th-century oil on canvas."""
    s = get_style("jean_honore_fragonard")
    assert s.crackle is True, (
        "jean_honore_fragonard crackle should be True (aged 18th-century oil on canvas)")


def test_jean_honore_fragonard_famous_works_contain_swing():
    """jean_honore_fragonard famous_works should include 'The Swing' — his most iconic work."""
    s = get_style("jean_honore_fragonard")
    titles = [w[0] for w in s.famous_works]
    assert any("Swing" in t for t in titles), (
        f"jean_honore_fragonard famous_works should include 'The Swing'; got: {titles}")


def test_jean_honore_fragonard_inspiration_references_bravura_pass():
    """jean_honore_fragonard inspiration text should reference fragonard_bravura_pass."""
    s = get_style("jean_honore_fragonard")
    assert "fragonard_bravura_pass" in s.inspiration, (
        "jean_honore_fragonard inspiration should reference fragonard_bravura_pass()")


def test_jean_honore_fragonard_palette_has_warm_highlight():
    """jean_honore_fragonard palette must have a warm, bright highlight (R > B and lum >= 0.82)."""
    s = get_style("jean_honore_fragonard")

    def _is_warm_highlight(rgb):
        r, g, b = rgb
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        return lum >= 0.82 and r > b

    assert any(_is_warm_highlight(rgb) for rgb in s.palette), (
        "jean_honore_fragonard palette must contain a warm bright highlight "
        "(lum >= 0.82 and R > B) — Fragonard's cream-warm sunlit highlights")


def test_jean_honore_fragonard_palette_warmer_highlight_than_gainsborough():
    """
    jean_honore_fragonard highlight must be warmer than thomas_gainsborough highlight.
    Gainsborough uses cool silver-white; Fragonard uses warm cream-ivory.
    """
    s_f = get_style("jean_honore_fragonard")
    s_g = get_style("thomas_gainsborough")

    def _brightest_rgb(palette):
        """Return the RGB with highest luminance."""
        return max(palette, key=lambda rgb: 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2])

    hi_f = _brightest_rgb(s_f.palette)
    hi_g = _brightest_rgb(s_g.palette)

    # Fragonard's highlight R/B ratio should exceed Gainsborough's
    ratio_f = hi_f[0] / (hi_f[2] + 1e-6)
    ratio_g = hi_g[0] / (hi_g[2] + 1e-6)
    assert ratio_f >= ratio_g, (
        f"jean_honore_fragonard highlight R/B ratio ({ratio_f:.3f}) should be >= "
        f"thomas_gainsborough highlight R/B ratio ({ratio_g:.3f}) — "
        "Fragonard warm cream vs Gainsborough cool silver")


# ═══════════════════════════════════════════════════════════════════════════
# FRENCH_ROCOCO period enum tests — Jean-Honoré Fragonard (session 42)
# ═══════════════════════════════════════════════════════════════════════════

def test_french_rococo_period_in_enum():
    """Period.FRENCH_ROCOCO must be a valid member of the Period enum."""
    assert hasattr(Period, "FRENCH_ROCOCO"), (
        "Period enum is missing FRENCH_ROCOCO — add it to scene_schema.py")


def test_french_rococo_stroke_params_keys():
    """FRENCH_ROCOCO stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_ROCOCO).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"FRENCH_ROCOCO stroke_params missing key: {key!r}"


def test_french_rococo_stroke_params_ranges():
    """FRENCH_ROCOCO stroke_params values must be in valid ranges."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_ROCOCO).stroke_params
    assert 3 <= sp["stroke_size_face"] <= 20, (
        f"FRENCH_ROCOCO stroke_size_face={sp['stroke_size_face']} should be in [3, 20]")
    assert 0.0 <= sp["wet_blend"] <= 1.0, (
        f"FRENCH_ROCOCO wet_blend={sp['wet_blend']} should be in [0, 1]")
    assert 0.0 <= sp["edge_softness"] <= 1.0, (
        f"FRENCH_ROCOCO edge_softness={sp['edge_softness']} should be in [0, 1]")


def test_french_rococo_high_wet_blend():
    """FRENCH_ROCOCO wet_blend should be >= 0.55 — fluid bravura alla prima."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_ROCOCO).stroke_params
    assert sp["wet_blend"] >= 0.55, (
        f"FRENCH_ROCOCO wet_blend={sp['wet_blend']:.2f} should be >= 0.55 "
        "(Fragonard painted wet-into-wet in a single sitting — fluid, spontaneous)")


def test_french_rococo_moderate_edge_softness():
    """FRENCH_ROCOCO edge_softness should be in [0.40, 0.65] — spirited but readable strokes."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_ROCOCO).stroke_params
    assert 0.40 <= sp["edge_softness"] <= 0.65, (
        f"FRENCH_ROCOCO edge_softness={sp['edge_softness']:.2f} should be in [0.40, 0.65] "
        "(bravura strokes taper at tips but body remains legible — not sfumato-dissolved)")


def test_french_rococo_larger_stroke_than_rococo_portrait():
    """
    FRENCH_ROCOCO stroke_size_face should be >= ROCOCO_PORTRAIT stroke_size_face.
    Fragonard's bravura marks are bolder than Gainsborough's refined feathered strokes.
    """
    sp_fr = Style(medium=Medium.OIL, period=Period.FRENCH_ROCOCO).stroke_params
    sp_rp = Style(medium=Medium.OIL, period=Period.ROCOCO_PORTRAIT).stroke_params
    assert sp_fr["stroke_size_face"] >= sp_rp["stroke_size_face"], (
        f"FRENCH_ROCOCO stroke_size_face ({sp_fr['stroke_size_face']}) should be >= "
        f"ROCOCO_PORTRAIT stroke_size_face ({sp_rp['stroke_size_face']}) — "
        "Fragonard's bravura marks are larger and bolder than Gainsborough's refined touches")


# ═══════════════════════════════════════════════════════════════════════════
# Pierre-Auguste Renoir — art catalog tests
# ═══════════════════════════════════════════════════════════════════════════

def test_pierre_auguste_renoir_in_catalog():
    """pierre_auguste_renoir must be present in CATALOG."""
    assert "pierre_auguste_renoir" in CATALOG, (
        "pierre_auguste_renoir not found in CATALOG — add the ArtStyle entry")


def test_pierre_auguste_renoir_in_expected_artists():
    """pierre_auguste_renoir must appear in the EXPECTED_ARTISTS list."""
    assert "pierre_auguste_renoir" in EXPECTED_ARTISTS, (
        "pierre_auguste_renoir missing from EXPECTED_ARTISTS — add it to the list")


def test_pierre_auguste_renoir_movement_impressionist():
    """pierre_auguste_renoir movement must reference Impressionism."""
    s = get_style("pierre_auguste_renoir")
    assert "Impressi" in s.movement, (
        f"pierre_auguste_renoir movement={s.movement!r} should reference 'Impressionism'")


def test_pierre_auguste_renoir_nationality():
    """pierre_auguste_renoir was French."""
    s = get_style("pierre_auguste_renoir")
    assert "French" in s.nationality, (
        f"pierre_auguste_renoir nationality should be French; got: {s.nationality!r}")


def test_pierre_auguste_renoir_palette_length():
    """pierre_auguste_renoir palette should have at least 7 key colours."""
    s = get_style("pierre_auguste_renoir")
    assert len(s.palette) >= 7, (
        f"pierre_auguste_renoir palette should have >= 7 colours; got {len(s.palette)}")


def test_pierre_auguste_renoir_palette_in_range():
    """All pierre_auguste_renoir palette RGB values must be in [0, 1]."""
    s = get_style("pierre_auguste_renoir")
    for i, rgb in enumerate(s.palette):
        assert len(rgb) == 3
        for j, channel in enumerate(rgb):
            assert 0.0 <= channel <= 1.0, (
                f"pierre_auguste_renoir palette[{i}][{j}]={channel:.3f} out of [0, 1]")


def test_pierre_auguste_renoir_warm_ground():
    """
    pierre_auguste_renoir ground must be warm (R > B) and pale (lum >= 0.70) —
    the warm pale-ivory preparation that unifies his chromatic palette in warmth.
    """
    s = get_style("pierre_auguste_renoir")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert r > b, (
        f"pierre_auguste_renoir ground_color R={r:.3f} should exceed B={b:.3f} "
        "(warm pale-ivory ground — not cool northern grey)")
    assert lum >= 0.70, (
        f"pierre_auguste_renoir ground luminance={lum:.3f} should be >= 0.70 "
        "(pale warm ground glows through thin paint layers in typical Renoir warmth)")


def test_pierre_auguste_renoir_warm_glazing():
    """pierre_auguste_renoir glazing must be warm (R > B) — peach-rose afternoon glow."""
    s = get_style("pierre_auguste_renoir")
    assert s.glazing is not None, (
        "pierre_auguste_renoir glazing should not be None — warm peach-rose glaze")
    r, _, b = s.glazing
    assert r > b, (
        f"pierre_auguste_renoir glazing R={r:.3f} should exceed B={b:.3f} "
        "(warm peach-rose glaze — not cool northern silver)")


def test_pierre_auguste_renoir_crackle():
    """pierre_auguste_renoir crackle should be True — aged 19th-century oil on canvas."""
    s = get_style("pierre_auguste_renoir")
    assert s.crackle is True, (
        "pierre_auguste_renoir crackle should be True (aged 19th-century oil on canvas)")


def test_pierre_auguste_renoir_no_chromatic_split():
    """pierre_auguste_renoir chromatic_split should be False — not Pointillist."""
    s = get_style("pierre_auguste_renoir")
    assert s.chromatic_split is False, (
        "pierre_auguste_renoir chromatic_split should be False "
        "(Renoir used optical colour mixing via adjacent strokes, not Pointillist dots)")


def test_pierre_auguste_renoir_famous_works():
    """pierre_auguste_renoir should have >= 5 famous works including Moulin de la Galette."""
    s = get_style("pierre_auguste_renoir")
    assert len(s.famous_works) >= 5, (
        f"pierre_auguste_renoir should have >= 5 famous works; got {len(s.famous_works)}")
    titles = [t for t, _ in s.famous_works]
    assert any("Galette" in t or "Moulin" in t for t in titles), (
        "pierre_auguste_renoir famous_works must include 'Dance at Le Moulin de la Galette' "
        "— his most celebrated and technically representative work")


def test_pierre_auguste_renoir_palette_has_warm_flesh():
    """pierre_auguste_renoir palette must contain at least one warm rose-peach flesh tone."""
    s = get_style("pierre_auguste_renoir")
    found = any(
        r > 0.75 and r > g and g > b and (r - b) > 0.20
        for r, g, b in s.palette
    )
    assert found, (
        "pierre_auguste_renoir palette must contain at least one warm rose-peach flesh tone "
        "(R dominant, R > G > B pattern, r-b spread > 0.20) — his signature warm flesh")


def test_pierre_Auguste_renoir_palette_has_spring_green():
    """pierre_auguste_renoir palette must contain at least one fresh spring green."""
    s = get_style("pierre_auguste_renoir")
    found = any(g > r and g > b for r, g, b in s.palette)
    assert found, (
        "pierre_auguste_renoir palette must contain at least one spring green (G dominant) — "
        "his garden and outdoor scenes always include fresh foliage greens")


def test_pierre_auguste_renoir_moderate_wet_blend():
    """pierre_auguste_renoir wet_blend should be in [0.40, 0.70] — feathery, living paint."""
    s = get_style("pierre_auguste_renoir")
    assert 0.40 <= s.wet_blend <= 0.70, (
        f"pierre_auguste_renoir wet_blend={s.wet_blend:.2f} should be in [0.40, 0.70] "
        "(Renoir worked wet-into-wet throughout; each stroke blends at its tip into "
        "the preceding layer — more fluid than Homer, less blended than Leonardo)")


def test_pierre_auguste_renoir_moderate_edge_softness():
    """pierre_auguste_renoir edge_softness should be in [0.30, 0.65] — soft but readable."""
    s = get_style("pierre_auguste_renoir")
    assert 0.30 <= s.edge_softness <= 0.65, (
        f"pierre_auguste_renoir edge_softness={s.edge_softness:.2f} should be in [0.30, 0.65] "
        "(figures are readable and present, but contours gently diffuse — "
        "not dissolved like Leonardo, not crisp like Homer)")


# ═══════════════════════════════════════════════════════════════════════════
# FRENCH_IMPRESSIONIST Period — scene_schema tests
# ═══════════════════════════════════════════════════════════════════════════

def test_french_impressionist_period_exists():
    """Period enum must have FRENCH_IMPRESSIONIST member."""
    assert hasattr(Period, "FRENCH_IMPRESSIONIST"), (
        "Period enum is missing FRENCH_IMPRESSIONIST — add it to scene_schema.py")


def test_french_impressionist_stroke_params_keys():
    """FRENCH_IMPRESSIONIST stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_IMPRESSIONIST).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"FRENCH_IMPRESSIONIST stroke_params missing key: {key!r}"


def test_french_impressionist_stroke_params_ranges():
    """FRENCH_IMPRESSIONIST stroke_params values must be in valid numeric ranges."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_IMPRESSIONIST).stroke_params
    assert 3 <= sp["stroke_size_face"] <= 20, (
        f"FRENCH_IMPRESSIONIST stroke_size_face={sp['stroke_size_face']} should be in [3, 20]")
    assert 0.0 <= sp["wet_blend"] <= 1.0, (
        f"FRENCH_IMPRESSIONIST wet_blend={sp['wet_blend']} should be in [0, 1]")
    assert 0.0 <= sp["edge_softness"] <= 1.0, (
        f"FRENCH_IMPRESSIONIST edge_softness={sp['edge_softness']} should be in [0, 1]")


def test_french_impressionist_moderate_wet_blend():
    """FRENCH_IMPRESSIONIST wet_blend should be in [0.40, 0.70] — feathery wet-into-wet."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_IMPRESSIONIST).stroke_params
    assert 0.40 <= sp["wet_blend"] <= 0.70, (
        f"FRENCH_IMPRESSIONIST wet_blend={sp['wet_blend']:.2f} should be in [0.40, 0.70] "
        "(Renoir worked wet-into-wet; strokes blend at tips but retain identity)")


def test_french_impressionist_moderate_edge_softness():
    """FRENCH_IMPRESSIONIST edge_softness should be in [0.30, 0.60] — soft but readable."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_IMPRESSIONIST).stroke_params
    assert 0.30 <= sp["edge_softness"] <= 0.60, (
        f"FRENCH_IMPRESSIONIST edge_softness={sp['edge_softness']:.2f} should be in [0.30, 0.60] "
        "(Renoir's figures are readable — not dissolved; not crisp marine silhouettes)")


# ──────────────────────────────────────────────────────────────────────────────
# Edvard Munch — NORDIC_EXPRESSIONIST (current session addition)
# ──────────────────────────────────────────────────────────────────────────────

def test_munch_in_catalog():
    """Edvard Munch must be present in CATALOG under the key 'munch'."""
    assert "munch" in CATALOG, "munch not found in CATALOG"


def test_munch_style_retrieval():
    """get_style('munch') must return an ArtStyle without raising."""
    s = get_style("munch")
    assert s is not None


def test_munch_movement():
    """Movement must reference Expressionism or Symbolism."""
    s = get_style("munch")
    combined = s.movement.lower()

    assert "expressionism" in combined or "symbolism" in combined, (
        f"Expected Expressionism or Symbolism in movement, got {s.movement!r}")


def test_munch_nationality():
    """Munch was Norwegian."""
    s = get_style("munch")
    assert "norwegian" in s.nationality.lower(), (
        f"Expected Norwegian nationality, got {s.nationality!r}")


def test_munch_palette_length():
    """Palette should have at least 5 entries covering anxiety reds, blues, and flesh."""
    s = get_style("munch")
    assert len(s.palette) >= 5, (
        f"Munch palette should have at least 5 entries, got {len(s.palette)}")


def test_munch_palette_values_in_range():
    """All Munch palette RGB values must be in [0, 1]."""
    s = get_style("munch")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Munch palette {rgb}")


def test_munch_dark_ground():
    """Munch primed on dark warm umber grounds — ground_color mean must be < 0.35."""
    s = get_style("munch")
    mean_ground = sum(s.ground_color) / 3
    assert mean_ground < 0.35, (
        f"Munch ground should be dark (mean < 0.35), got {mean_ground:.3f}")


def test_munch_has_glazing():
    """Munch used warm crimson-amber glazes — glazing should not be None."""
    s = get_style("munch")
    assert s.glazing is not None, "Munch should have a warm crimson-amber glazing colour"


def test_munch_glazing_warm():
    """Munch glaze should be warm (R > B)."""
    s = get_style("munch")
    r, g, b = s.glazing
    assert r > b, (
        f"Munch glaze should be warm (R > B), got ({r:.2f},{g:.2f},{b:.2f})")


def test_munch_crackle_true():
    """Munch's aged oils — crackle must be True."""
    s = get_style("munch")
    assert s.crackle, "Munch's aged oil canvases should have crackle=True"


def test_munch_famous_works_include_scream():
    """The Scream must be in Munch's famous works."""
    s = get_style("munch")
    titles = [w[0] for w in s.famous_works]
    assert any("Scream" in t for t in titles), (
        "Munch famous works should include The Scream (1893)")


def test_munch_famous_works_count():
    """Munch should have at least 6 famous works documented."""
    s = get_style("munch")
    assert len(s.famous_works) >= 6, (
        f"Munch should have at least 6 famous works, got {len(s.famous_works)}")


def test_munch_inspiration_references_swirl_pass():
    """Inspiration text must reference munch_anxiety_swirl_pass."""
    s = get_style("munch")
    assert "munch_anxiety_swirl" in s.inspiration.lower().replace(" ", "_"), (
        "Munch inspiration should reference munch_anxiety_swirl_pass() — "
        "the dedicated Nordic Expressionist sinuous background turbulence pass")


def test_munch_moderate_wet_blend():
    """Munch's directional strokes require moderate wet_blend (not too dissolved)."""
    s = get_style("munch")
    assert 0.30 <= s.wet_blend <= 0.65, (
        f"Munch wet_blend should be moderate [0.30, 0.65]; got {s.wet_blend}")


def test_munch_moderate_edge_softness():
    """Figure-ground boundary dissolves — edge_softness should be moderate."""
    s = get_style("munch")
    assert 0.25 <= s.edge_softness <= 0.60, (
        f"Munch edge_softness should be moderate [0.25, 0.60]; got {s.edge_softness}")


# ── NORDIC_EXPRESSIONIST Period stroke params ──────────────────────────────

def test_nordic_expressionist_period_exists():
    """Period.NORDIC_EXPRESSIONIST must exist in the Period enum."""
    assert hasattr(Period, "NORDIC_EXPRESSIONIST"), (
        "Period.NORDIC_EXPRESSIONIST not found — add it to scene_schema.py")


def test_nordic_expressionist_stroke_params_keys():
    """NORDIC_EXPRESSIONIST stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.NORDIC_EXPRESSIONIST).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"NORDIC_EXPRESSIONIST stroke_params missing key: {key!r}"


def test_nordic_expressionist_stroke_params_ranges():
    """NORDIC_EXPRESSIONIST stroke_params values must be in valid numeric ranges."""
    sp = Style(medium=Medium.OIL, period=Period.NORDIC_EXPRESSIONIST).stroke_params
    assert 3 <= sp["stroke_size_face"] <= 20, (
        f"NORDIC_EXPRESSIONIST stroke_size_face={sp['stroke_size_face']} should be in [3, 20]")
    assert 0.0 <= sp["wet_blend"] <= 1.0, (
        f"NORDIC_EXPRESSIONIST wet_blend={sp['wet_blend']} should be in [0, 1]")
    assert 0.0 <= sp["edge_softness"] <= 1.0, (
        f"NORDIC_EXPRESSIONIST edge_softness={sp['edge_softness']} should be in [0, 1]")


def test_nordic_expressionist_moderate_wet_blend():
    """NORDIC_EXPRESSIONIST wet_blend should be in [0.30, 0.65] — directional but blended."""
    sp = Style(medium=Medium.OIL, period=Period.NORDIC_EXPRESSIONIST).stroke_params
    assert 0.30 <= sp["wet_blend"] <= 0.65, (
        f"NORDIC_EXPRESSIONIST wet_blend={sp['wet_blend']:.2f} should be in [0.30, 0.65]")


def test_nordic_expressionist_moderate_edge_softness():
    """NORDIC_EXPRESSIONIST edge_softness should be in [0.20, 0.55] — dissolving but present."""
    sp = Style(medium=Medium.OIL, period=Period.NORDIC_EXPRESSIONIST).stroke_params
    assert 0.20 <= sp["edge_softness"] <= 0.55, (
        f"NORDIC_EXPRESSIONIST edge_softness={sp['edge_softness']:.2f} should be in [0.20, 0.55]")


# ── Frans Hals catalog tests ───────────────────────────────────────────────────

def test_frans_hals_in_catalog():
    """Frans Hals must be present in CATALOG under the key 'frans_hals'."""
    assert "frans_hals" in CATALOG, "frans_hals not found in CATALOG"


def test_frans_hals_style_retrieval():
    """get_style('frans_hals') must return an ArtStyle without raising."""
    s = get_style("frans_hals")
    assert s is not None
    assert s.artist == "Frans Hals"


def test_frans_hals_movement():
    """Frans Hals must be catalogued under the Dutch Golden Age movement."""
    s = get_style("frans_hals")
    assert "Dutch Golden Age" in s.movement, (
        f"Expected 'Dutch Golden Age' in movement, got {s.movement!r}")


def test_frans_hals_nationality():
    """Frans Hals must be recorded as Dutch."""
    s = get_style("frans_hals")
    assert "Dutch" in s.nationality, (
        f"Expected 'Dutch' in nationality, got {s.nationality!r}")


def test_frans_hals_palette_length():
    """Frans Hals palette must have at least 5 colour entries."""
    s = get_style("frans_hals")
    assert len(s.palette) >= 5, (
        f"Frans Hals palette should have ≥5 colours; got {len(s.palette)}")


def test_frans_hals_palette_values_in_range():
    """All palette RGB values must be in [0.0, 1.0]."""
    s = get_style("frans_hals")
    for i, rgb in enumerate(s.palette):
        for c_idx, c in enumerate(rgb):
            assert 0.0 <= c <= 1.0, (
                f"Frans Hals palette[{i}][{c_idx}] = {c:.4f} out of [0, 1]")


def test_frans_hals_warm_ground():
    """Frans Hals's ground_color must be warm (R > B)."""
    s = get_style("frans_hals")
    r, g, b = s.ground_color
    assert r > b, (
        f"Frans Hals ground_color should be warm (R > B); got R={r:.2f} B={b:.2f}")
    assert 0.0 <= r <= 1.0 and 0.0 <= g <= 1.0 and 0.0 <= b <= 1.0, (
        "Frans Hals ground_color values must be in [0, 1]")


def test_frans_hals_no_glazing():
    """Frans Hals worked alla prima without a unifying glaze — glazing must be None."""
    s = get_style("frans_hals")
    assert s.glazing is None, (
        f"Frans Hals glazing should be None (no unifying glaze); got {s.glazing!r}")


def test_frans_hals_famous_works_include_laughing_cavalier():
    """The Laughing Cavalier must be in Frans Hals's famous works."""
    s = get_style("frans_hals")
    titles = [w[0] for w in s.famous_works]
    assert any("Laughing Cavalier" in t for t in titles), (
        "Frans Hals famous works should include The Laughing Cavalier (1624)")


def test_frans_hals_famous_works_count():
    """Frans Hals should have at least 5 famous works documented."""
    s = get_style("frans_hals")
    assert len(s.famous_works) >= 5, (
        f"Frans Hals should have ≥5 famous works; got {len(s.famous_works)}")


def test_Frans_hals_inspiration_references_bravura_pass():
    """Inspiration text must reference hals_bravura_stroke_pass."""
    s = get_style("frans_hals")
    assert "hals_bravura_stroke" in s.inspiration.lower().replace(" ", "_"), (
        "Frans Hals inspiration should reference hals_bravura_stroke_pass() — "
        "the dedicated alla prima broken-tone pass")


def test_Frans_hals_low_wet_blend():
    """Alla prima technique demands low wet_blend (no wet-into-wet fusion)."""
    s = get_style("frans_hals")
    assert s.wet_blend <= 0.25, (
        f"Frans Hals wet_blend should be low (≤0.25 for alla prima); got {s.wet_blend:.2f}")


def test_Frans_hals_low_edge_softness():
    """Crisp directional bravura marks demand low edge_softness (no sfumato)."""
    s = get_style("frans_hals")
    assert s.edge_softness <= 0.30, (
        f"Frans Hals edge_softness should be low (≤0.30 for crisp marks); got {s.edge_softness:.2f}")


# ── Salvador Dali catalog tests ────────────────────────────────────────────────

def test_salvador_dali_in_catalog():
    """Salvador Dali must be present in CATALOG under the key 'salvador_dali'."""
    assert "salvador_dali" in CATALOG, "salvador_dali not found in CATALOG"


def test_salvador_dali_style_retrieval():
    """get_style('salvador_dali') must return an ArtStyle without raising."""
    s = get_style("salvador_dali")
    assert s is not None
    assert s.artist == "Salvador Dali"


def test_salvador_dali_movement():
    """Salvador Dali must be catalogued under Surrealism."""
    s = get_style("salvador_dali")
    assert "Surreal" in s.movement, (
        f"Expected 'Surreal' in movement, got {s.movement!r}")


def test_salvador_dali_nationality():
    """Salvador Dali must be recorded as Spanish."""
    s = get_style("salvador_dali")
    assert "Spanish" in s.nationality, (
        f"Expected 'Spanish' in nationality, got {s.nationality!r}")


def test_salvador_dali_palette_length():
    """Salvador Dali palette must have at least 5 colour entries."""
    s = get_style("salvador_dali")
    assert len(s.palette) >= 5, (
        f"Salvador Dali palette should have ≥5 colours; got {len(s.palette)}")


def test_salvador_dali_palette_values_in_range():
    """All Salvador Dali palette RGB values must be in [0.0, 1.0]."""
    s = get_style("salvador_dali")
    for i, rgb in enumerate(s.palette):
        for c_idx, c in enumerate(rgb):
            assert 0.0 <= c <= 1.0, (
                f"Salvador Dali palette[{i}][{c_idx}] = {c:.4f} out of [0, 1]")


def test_salvador_dali_crisp_edges():
    """Dali's hyper-realist technique demands low edge_softness (crisp foreground)."""
    s = get_style("salvador_dali")
    assert s.edge_softness <= 0.20, (
        f"Salvador Dali edge_softness should be ≤0.20 for hyper-realist precision; "
        f"got {s.edge_softness:.2f}")


def test_salvador_dali_low_wet_blend():
    """Dali's hyper-controlled technique demands low wet_blend."""
    s = get_style("salvador_dali")
    assert s.wet_blend <= 0.10, (
        f"Salvador Dali wet_blend should be ≤0.10 for dry hyper-realist technique; "
        f"got {s.wet_blend:.2f}")


def test_salvador_dali_famous_works_include_persistence_of_memory():
    """The Persistence of Memory must be in Salvador Dali's famous works."""
    s = get_style("salvador_dali")
    titles = [w[0] for w in s.famous_works]
    assert any("Persistence of Memory" in t for t in titles), (
        "Salvador Dali famous works should include The Persistence of Memory (1931)")


def test_salvador_dali_famous_works_count():
    """Salvador Dali should have at least 5 famous works documented."""
    s = get_style("salvador_dali")
    assert len(s.famous_works) >= 5, (
        f"Salvador Dali should have ≥5 famous works; got {len(s.famous_works)}")


def test_salvador_dali_inspiration_references_dali_pass():
    """Inspiration text must reference dali_paranoiac_critical_pass."""
    s = get_style("salvador_dali")
    assert "dali_paranoiac_critical" in s.inspiration.lower().replace(" ", "_"), (
        "Salvador Dali inspiration should reference dali_paranoiac_critical_pass() — "
        "the dedicated chromatic aberration and ultramarine shadow pass")


def test_salvador_dali_in_expected_artists():
    """EXPECTED_ARTISTS list must include salvador_dali."""
    assert "salvador_dali" in EXPECTED_ARTISTS, (
        "salvador_dali missing from EXPECTED_ARTISTS — add it to the list")


def test_salvador_dali_ground_color_warm():
    """Salvador Dali's ground must be warm (R > B) — warm ivory-ochre Catalan light."""
    s = get_style("salvador_dali")
    r, g, b = s.ground_color
    assert r > b, (
        f"Salvador Dali ground_color should be warm (R > B); got R={r:.2f} B={b:.2f}")
    assert 0.0 <= r <= 1.0 and 0.0 <= g <= 1.0 and 0.0 <= b <= 1.0, (
        "Salvador Dali ground_color values must be in [0, 1]")


def test_salvador_dali_has_glazing():
    """Salvador Dali used a warm amber unifying glaze — glazing must not be None."""
    s = get_style("salvador_dali")
    assert s.glazing is not None, (
        "Salvador Dali glazing should be set to warm amber-gold; got None")
    r, g, b = s.glazing
    assert r > b, (
        f"Dali's unifying glaze should be warm (R > B); got R={r:.2f} B={b:.2f}")


def test_Frans_hals_high_jitter():
    """Broken-tone variation requires jitter > 0.03."""
    s = get_style("frans_hals")
    assert s.jitter > 0.03, (
        f"Frans Hals jitter should be > 0.03 (broken-tone variation); got {s.jitter:.3f}")


# ── DUTCH_GOLDEN_AGE Period stroke params ─────────────────────────────────────

def test_dutch_golden_age_period_exists():
    """Period.DUTCH_GOLDEN_AGE must exist in the Period enum."""
    assert hasattr(Period, "DUTCH_GOLDEN_AGE"), (
        "Period.DUTCH_GOLDEN_AGE not found — add it to scene_schema.py")


def test_dutch_golden_age_stroke_params_keys():
    """DUTCH_GOLDEN_AGE stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.DUTCH_GOLDEN_AGE).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"DUTCH_GOLDEN_AGE stroke_params missing key: {key!r}"


def test_dutch_golden_age_stroke_params_ranges():
    """DUTCH_GOLDEN_AGE stroke_params values must be in valid numeric ranges."""
    sp = Style(medium=Medium.OIL, period=Period.DUTCH_GOLDEN_AGE).stroke_params
    assert 3 <= sp["stroke_size_face"] <= 20, (
        f"DUTCH_GOLDEN_AGE stroke_size_face={sp['stroke_size_face']} should be in [3, 20]")
    assert 0.0 <= sp["wet_blend"] <= 1.0, (
        f"DUTCH_GOLDEN_AGE wet_blend={sp['wet_blend']} should be in [0, 1]")
    assert 0.0 <= sp["edge_softness"] <= 1.0, (
        f"DUTCH_GOLDEN_AGE edge_softness={sp['edge_softness']} should be in [0, 1]")


def test_dutch_golden_age_low_wet_blend():
    """DUTCH_GOLDEN_AGE wet_blend should be in [0.05, 0.25] — alla prima, minimal fusion."""
    sp = Style(medium=Medium.OIL, period=Period.DUTCH_GOLDEN_AGE).stroke_params
    assert 0.05 <= sp["wet_blend"] <= 0.25, (
        f"DUTCH_GOLDEN_AGE wet_blend={sp['wet_blend']:.2f} should be in [0.05, 0.25]")


def test_dutch_golden_age_low_edge_softness():
    """DUTCH_GOLDEN_AGE edge_softness should be in [0.05, 0.28] — crisp directional marks."""
    sp = Style(medium=Medium.OIL, period=Period.DUTCH_GOLDEN_AGE).stroke_params
    assert 0.05 <= sp["edge_softness"] <= 0.28, (
        f"DUTCH_GOLDEN_AGE edge_softness={sp['edge_softness']:.2f} should be in [0.05, 0.28]")


# ─────────────────────────────────────────────────────────────────────────────
# Vilhelm Hammershøi — session 49
# ─────────────────────────────────────────────────────────────────────────────

def test_vilhelm_hammershoi_in_catalog():
    """Vilhelm Hammershøi must be present in CATALOG."""
    assert "vilhelm_hammershoi" in CATALOG, (
        "vilhelm_hammershoi missing from CATALOG")


def test_vilhelm_hammershoi_get_style():
    """get_style('vilhelm_hammershoi') must return an ArtStyle with correct artist name."""
    s = get_style("vilhelm_hammershoi")
    assert s is not None
    assert s.artist == "Vilhelm Hammershøi"


def test_vilhelm_hammershoi_movement():
    """Hammershøi must be catalogued under Symbolism / Danish Intimisme."""
    s = get_style("vilhelm_hammershoi")
    assert "Symbolism" in s.movement or "Intimisme" in s.movement or "intimis" in s.movement.lower(), (
        f"Expected Symbolism or Intimisme in movement, got {s.movement!r}")


def test_vilhelm_hammershoi_nationality():
    """Hammershøi must be recorded as Danish."""
    s = get_style("vilhelm_hammershoi")
    assert "Danish" in s.nationality, (
        f"Expected 'Danish' in nationality, got {s.nationality!r}")


def test_vilhelm_hammershoi_palette_length():
    """Hammershøi palette must have at least 5 colour entries."""
    s = get_style("vilhelm_hammershoi")
    assert len(s.palette) >= 5, (
        f"Vilhelm Hammershøi palette should have ≥5 colours; got {len(s.palette)}")


def test_vilhelm_hammershoi_palette_values_in_range():
    """All Hammershøi palette RGB values must be in [0.0, 1.0]."""
    s = get_style("vilhelm_hammershoi")
    for i, rgb in enumerate(s.palette):
        for c_idx, c in enumerate(rgb):
            assert 0.0 <= c <= 1.0, (
                f"Hammershøi palette[{i}][{c_idx}] = {c:.4f} out of [0, 1]")


def test_vilhelm_hammershoi_high_wet_blend():
    """Hammershøi's invisible brushwork requires very high wet_blend (≥0.65)."""
    s = get_style("vilhelm_hammershoi")
    assert s.wet_blend >= 0.65, (
        f"Vilhelm Hammershøi wet_blend should be ≥0.65 (seamless blending); "
        f"got {s.wet_blend:.2f}")


def test_vilhelm_hammershoi_high_edge_softness():
    """Hammershøi's dissolved edges require high edge_softness (≥0.60)."""
    s = get_style("vilhelm_hammershoi")
    assert s.edge_softness >= 0.60, (
        f"Vilhelm Hammershøi edge_softness should be ≥0.60 (dissolved edges); "
        f"got {s.edge_softness:.2f}")


def test_vilhelm_hammershoi_near_zero_jitter():
    """Hammershøi's uniform tonal surface requires very low jitter (≤0.02)."""
    s = get_style("vilhelm_hammershoi")
    assert s.jitter <= 0.02, (
        f"Vilhelm Hammershøi jitter should be ≤0.02 (uniform grey surface); "
        f"got {s.jitter:.4f}")


def test_vilhelm_hammershoi_cool_ground():
    """Hammershøi's ground must be a near-neutral cool grey (R≈G≈B, all in [0.55, 0.80])."""
    s = get_style("vilhelm_hammershoi")
    r, g, b = s.ground_color
    # Near-neutral: no channel differs from another by more than 0.06
    assert abs(r - g) <= 0.06, (
        f"Hammershøi ground_color R and G should be near-equal; got R={r:.2f} G={g:.2f}")
    assert abs(r - b) <= 0.06, (
        f"Hammershøi ground_color R and B should be near-equal; got R={r:.2f} B={b:.2f}")
    for ch, name in zip((r, g, b), ("R", "G", "B")):
        assert 0.55 <= ch <= 0.82, (
            f"Hammershøi ground_color {name}={ch:.2f} should be in [0.55, 0.82] — cool silver-ash")


def test_vilhelm_hammershoi_cool_glazing():
    """Hammershøi must have a near-neutral cool glazing (not warm, not None)."""
    s = get_style("vilhelm_hammershoi")
    assert s.glazing is not None, (
        "Vilhelm Hammershøi glazing must not be None — cool grey unifying glaze required")
    r, g, b = s.glazing
    # Glazing must not be warm (R should not dominate strongly over B)
    assert r - b <= 0.08, (
        f"Hammershøi glazing should not be warm; got R={r:.2f} B={b:.2f} (R-B={r-b:.2f})")


def test_vilhelm_hammershoi_famous_works_include_dust_motes():
    """'Dust Motes Dancing in Sunrays' must be in Hammershøi's famous works."""
    s = get_style("vilhelm_hammershoi")
    titles = [w[0] for w in s.famous_works]
    assert any("Dust Motes" in t or "dust motes" in t.lower() for t in titles), (
        "Hammershøi famous works should include 'Dust Motes Dancing in Sunrays' (1900)")


def test_vilhelm_hammershoi_famous_works_count():
    """Hammershøi should have at least 5 famous works documented."""
    s = get_style("vilhelm_hammershoi")
    assert len(s.famous_works) >= 5, (
        f"Vilhelm Hammershøi should have ≥5 famous works; got {len(s.famous_works)}")


def test_vilhelm_hammershoi_inspiration_references_grey_silence_pass():
    """Inspiration text must reference hammershoi_grey_silence_pass."""
    s = get_style("vilhelm_hammershoi")
    assert "hammershoi_grey_silence" in s.inspiration.lower().replace(" ", "_"), (
        "Hammershøi inspiration should reference hammershoi_grey_silence_pass() — "
        "the near-monochrome desaturation pass")


def test_vilhelm_hammershoi_in_expected_artists():
    """EXPECTED_ARTISTS list must include vilhelm_hammershoi."""
    assert "vilhelm_hammershoi" in EXPECTED_ARTISTS, (
        "vilhelm_hammershoi missing from EXPECTED_ARTISTS — add it to the list")


# ── DANISH_INTIMISTE Period stroke params ──────────────────────────────────────

def test_danish_intimiste_period_exists():
    """Period.DANISH_INTIMISTE must exist in the Period enum."""
    assert hasattr(Period, "DANISH_INTIMISTE"), (
        "Period.DANISH_INTIMISTE not found — add it to scene_schema.py")


def test_danish_intimiste_stroke_params_keys():
    """DANISH_INTIMISTE stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.DANISH_INTIMISTE).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"DANISH_INTIMISTE stroke_params missing key: {key!r}"


def test_danish_intimiste_stroke_params_ranges():
    """DANISH_INTIMISTE stroke_params values must be in valid numeric ranges."""
    sp = Style(medium=Medium.OIL, period=Period.DANISH_INTIMISTE).stroke_params
    assert 2 <= sp["stroke_size_face"] <= 10, (
        f"DANISH_INTIMISTE stroke_size_face={sp['stroke_size_face']} should be in [2, 10]")
    assert 0.0 <= sp["wet_blend"] <= 1.0, (
        f"DANISH_INTIMISTE wet_blend={sp['wet_blend']} should be in [0, 1]")
    assert 0.0 <= sp["edge_softness"] <= 1.0, (
        f"DANISH_INTIMISTE edge_softness={sp['edge_softness']} should be in [0, 1]")


def test_danish_intimiste_high_wet_blend():
    """DANISH_INTIMISTE wet_blend should be ≥0.65 — seamless invisible blending."""
    sp = Style(medium=Medium.OIL, period=Period.DANISH_INTIMISTE).stroke_params
    assert sp["wet_blend"] >= 0.65, (
        f"DANISH_INTIMISTE wet_blend={sp['wet_blend']:.2f} should be ≥0.65")


def test_danish_intimiste_high_edge_softness():
    """DANISH_INTIMISTE edge_softness should be ≥0.60 — dissolved edges, no hard lines."""
    sp = Style(medium=Medium.OIL, period=Period.DANISH_INTIMISTE).stroke_params
    assert sp["edge_softness"] >= 0.60, (
        f"DANISH_INTIMISTE edge_softness={sp['edge_softness']:.2f} should be ≥0.60")


# ══════════════════════════════════════════════════════════════════════════════
# Session 50 — John Constable
# ══════════════════════════════════════════════════════════════════════════════

def test_john_constable_in_catalog():
    """John Constable must be in the CATALOG (session 50 addition)."""
    assert "john_constable" in CATALOG, (
        "john_constable missing from CATALOG — add it to art_catalog.py")


def test_john_constable_movement_contains_romanticism():
    """Constable's movement must reference Romanticism."""
    s = get_style("john_constable")
    assert "romantic" in s.movement.lower() or "naturalis" in s.movement.lower(), (
        f"Constable movement should mention Romanticism or Naturalism; got {s.movement!r}")


def test_john_constable_british():
    """Constable must be listed as British."""
    s = get_style("john_constable")
    assert s.nationality.lower() == "british", (
        f"John Constable nationality should be 'British'; got {s.nationality!r}")


def test_john_constable_green_in_palette():
    """Constable's palette must include at least one distinctly green swatch."""
    s = get_style("john_constable")
    has_green = any(
        g > r + 0.12 and g > b + 0.08
        for r, g, b in s.palette
    )
    assert has_green, (
        "Constable's palette must include a green swatch — he is the Suffolk landscape painter")


def test_john_constable_moderate_wet_blend():
    """Constable wet_blend should be in [0.30, 0.60] — plein air freshness, not over-blended."""
    s = get_style("john_constable")
    assert 0.30 <= s.wet_blend <= 0.60, (
        f"Constable wet_blend={s.wet_blend:.2f} should be in [0.30, 0.60] "
        f"(plein air spontaneity — not Turner's atmospheric dissolution)")


def test_john_constable_moderate_edge_softness():
    """Constable edge_softness should be in [0.20, 0.55] — atmospheric softness without sfumato."""
    s = get_style("john_constable")
    assert 0.20 <= s.edge_softness <= 0.55, (
        f"Constable edge_softness={s.edge_softness:.2f} should be in [0.20, 0.55] "
        f"(landscape edges are soft but present — not Turner-level dissolution)")


def test_john_constable_warm_green_ground():
    """Constable's ground must have a greenish or warm bias (G channel dominant or equal)."""
    s = get_style("john_constable")
    r, g, b = s.ground_color
    # The typical greenish-grey ground: G should be close to or above R
    assert g >= r - 0.05, (
        f"Constable ground_color should have a greenish or neutral bias; "
        f"got R={r:.2f} G={g:.2f} B={b:.2f}")


def test_john_constable_famous_works_include_hay_wain():
    """The Hay Wain (1821) must be in Constable's famous works."""
    s = get_style("john_constable")
    titles = [w[0] for w in s.famous_works]
    assert any("hay wain" in t.lower() for t in titles), (
        "Constable famous works should include 'The Hay Wain' (1821) — his most celebrated work")


def test_john_constable_famous_works_count():
    """Constable should have at least 5 famous works documented."""
    s = get_style("john_constable")
    assert len(s.famous_works) >= 5, (
        f"John Constable should have ≥5 famous works; got {len(s.famous_works)}")


def test_john_constable_inspiration_references_constable_cloud_sky_pass():
    """Inspiration text must reference constable_cloud_sky_pass."""
    s = get_style("john_constable")
    assert "constable_cloud_sky" in s.inspiration.lower().replace(" ", "_"), (
        "Constable inspiration should reference constable_cloud_sky_pass() — "
        "the defining sky technique pass")


def test_john_constable_in_expected_artists():
    """EXPECTED_ARTISTS list must include john_constable."""
    assert "john_constable" in EXPECTED_ARTISTS, (
        "john_constable missing from EXPECTED_ARTISTS — add it to the list")


# ──────────────────────────────────────────────────────────────────────────────
# Giovanni Bellini — session 51 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_giovanni_bellini_in_catalog():
    """Bellini (session 51) must be present in CATALOG."""
    assert "giovanni_bellini" in CATALOG


def test_giovanni_bellini_movement():
    """Bellini must be classified as Early Venetian Renaissance."""
    s = get_style("giovanni_bellini")
    assert "venetian" in s.movement.lower() or "renaissance" in s.movement.lower(), (
        f"Bellini movement should reference Venetian Renaissance; got {s.movement!r}")


def test_giovanni_bellini_italian():
    """Bellini must be listed as Italian."""
    s = get_style("giovanni_bellini")
    assert s.nationality.lower() == "italian", (
        f"Giovanni Bellini nationality should be 'Italian'; got {s.nationality!r}")


def test_giovanni_bellini_palette_length():
    """Bellini palette should have at least 6 key colours."""
    s = get_style("giovanni_bellini")
    assert len(s.palette) >= 6, (
        f"Bellini palette should have ≥6 colours; got {len(s.palette)}")


def test_giovanni_bellini_lapis_in_palette():
    """Bellini's palette must include a blue swatch for the Virgin's lapis robe."""
    s = get_style("giovanni_bellini")
    has_blue = any(b > r + 0.12 and b > g for r, g, b in s.palette)
    assert has_blue, (
        "Bellini palette must include a lapis-blue swatch — lapis lazuli for the Virgin's robe")


def test_giovanni_bellini_warm_ground():
    """Bellini's imprimatura should be warm (R+G > B) — amber-ochre base."""
    s = get_style("giovanni_bellini")
    r, g, b = s.ground_color
    assert (r + g) / 2.0 > b + 0.10, (
        f"Bellini ground must be warm amber-ochre (R+G > B); got R={r:.2f} G={g:.2f} B={b:.2f}")


def test_giovanni_bellini_glazing_warm():
    """Bellini's glaze must be a warm honey-amber (R > B)."""
    s = get_style("giovanni_bellini")
    assert s.glazing is not None, "Bellini must have a glazing colour"
    r, g, b = s.glazing
    assert r > b + 0.20, (
        f"Bellini glazing must be warm amber (R >> B); got R={r:.2f} B={b:.2f}")


def test_giovanni_bellini_wet_blend_range():
    """Bellini wet_blend should be in [0.40, 0.70] — thin glazes blend in halftones."""
    s = get_style("giovanni_bellini")
    assert 0.40 <= s.wet_blend <= 0.70, (
        f"Bellini wet_blend={s.wet_blend:.2f} should be in [0.40, 0.70]")


def test_giovanni_bellini_edge_softness_range():
    """Bellini edge_softness should be in [0.40, 0.70] — soft but architecturally resolved."""
    s = get_style("giovanni_bellini")
    assert 0.40 <= s.edge_softness <= 0.70, (
        f"Bellini edge_softness={s.edge_softness:.2f} should be in [0.40, 0.70] "
        f"(soft but resolved — not sfumato)")


def test_giovanni_bellini_famous_works_include_san_zaccaria():
    """San Zaccaria Altarpiece (1505) must be in Bellini's famous works."""
    s = get_style("giovanni_bellini")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("zaccaria" in t or "altarpiece" in t for t in titles), (
        "Bellini famous works should include San Zaccaria Altarpiece — his greatest mature work")


def test_giovanni_bellini_famous_works_count():
    """Bellini should have at least 5 famous works documented."""
    s = get_style("giovanni_bellini")
    assert len(s.famous_works) >= 5, (
        f"Giovanni Bellini should have ≥5 famous works; got {len(s.famous_works)}")


def test_giovanni_bellini_inspiration_references_bellini_sacred_light_pass():
    """Inspiration text must reference bellini_sacred_light_pass."""
    s = get_style("giovanni_bellini")
    assert "bellini_sacred_light" in s.inspiration.lower().replace(" ", "_"), (
        "Bellini inspiration must reference bellini_sacred_light_pass() — "
        "the defining sacred luminosity technique pass")


def test_giovanni_bellini_in_expected_artists():
    """EXPECTED_ARTISTS list must include giovanni_bellini."""
    assert "giovanni_bellini" in EXPECTED_ARTISTS, (
        "giovanni_bellini missing from EXPECTED_ARTISTS — add it to the list")


# ──────────────────────────────────────────────────────────────────────────────
# EARLY_VENETIAN_RENAISSANCE period — session 51 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_early_venetian_renaissance_period_present():
    """Period.EARLY_VENETIAN_RENAISSANCE must exist (session 51)."""
    assert hasattr(Period, "EARLY_VENETIAN_RENAISSANCE"), (
        "Period.EARLY_VENETIAN_RENAISSANCE not found — add it to scene_schema.py")
    assert Period.EARLY_VENETIAN_RENAISSANCE in list(Period)


def test_early_venetian_renaissance_stroke_params_valid():
    """EARLY_VENETIAN_RENAISSANCE stroke_params must return valid defaults."""
    style = Style(
        medium=Medium.OIL,
        period=Period.EARLY_VENETIAN_RENAISSANCE,
        palette=PaletteHint.WARM_EARTH,
    )
    params = style.stroke_params
    assert "stroke_size_face" in params
    assert "stroke_size_bg"   in params
    assert "wet_blend"        in params
    assert "edge_softness"    in params
    assert params["stroke_size_face"] > 0
    assert params["stroke_size_bg"]   > 0
    assert 0.0 <= params["wet_blend"]     <= 1.0
    assert 0.0 <= params["edge_softness"] <= 1.0


def test_early_venetian_renaissance_in_expected_periods():
    """EXPECTED_PERIODS list must include EARLY_VENETIAN_RENAISSANCE."""
    assert "EARLY_VENETIAN_RENAISSANCE" in EXPECTED_PERIODS, (
        "EARLY_VENETIAN_RENAISSANCE missing from EXPECTED_PERIODS — add it to the list")


# ──────────────────────────────────────────────────────────────────────────────
# Pontormo — session 52 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_pontormo_in_catalog():
    """pontormo must be present in CATALOG (session 52)."""
    assert "pontormo" in CATALOG, (
        "pontormo missing from CATALOG — add it to art_catalog.py")


def test_pontormo_movement_is_mannerist():
    """Pontormo's movement must be Florentine Mannerism."""
    s = get_style("pontormo")
    assert "manner" in s.movement.lower() or "mannerist" in s.movement.lower(), (
        f"Pontormo movement should be Mannerism-related; got {s.movement!r}")


def test_pontormo_palette_acid_highlight():
    """Pontormo palette must contain at least one acid yellow-green (G > 0.75 and R > 0.60)."""
    s = get_style("pontormo")
    acid = [(r, g, b) for r, g, b in s.palette if g > 0.75 and r > 0.60]
    assert len(acid) >= 1, (
        "Pontormo palette should include at least one acid chartreuse-yellow colour "
        f"(G > 0.75 and R > 0.60); palette={s.palette}")


def test_pontormo_palette_cool_shadow():
    """Pontormo palette must contain at least one near-black cool shadow (all channels < 0.20)."""
    s = get_style("pontormo")
    dark = [(r, g, b) for r, g, b in s.palette
            if r < 0.20 and g < 0.20 and b < 0.20]
    assert len(dark) >= 1, (
        "Pontormo palette should include at least one deep purple-black shadow; "
        f"palette={s.palette}")


def test_pontormo_palette_shocking_rose():
    """Pontormo palette must contain a shocking rose/carmine (R > 0.75, B > 0.30, G < 0.60)."""
    s = get_style("pontormo")
    rose = [(r, g, b) for r, g, b in s.palette if r > 0.75 and b > 0.30 and g < 0.60]
    assert len(rose) >= 1, (
        "Pontormo palette should include at least one shocking rose-carmine colour; "
        f"palette={s.palette}")


def test_pontormo_glazing_is_none():
    """Pontormo must have glazing=None — his colours are direct, not glazed."""
    s = get_style("pontormo")
    assert s.glazing is None, (
        f"Pontormo.glazing should be None (colours are direct and opaque); got {s.glazing!r}")


def test_pontormo_crackle():
    """Pontormo must have crackle=True — aged Florentine panel paintings crackle."""
    s = get_style("pontormo")
    assert s.crackle is True, (
        "Pontormo.crackle should be True — aged Florentine panel surfaces crackle")


def test_pontormo_ground_color_cool():
    """Pontormo ground must be a cool grey (B >= R, not warm amber)."""
    s = get_style("pontormo")
    r, g, b = s.ground_color
    assert b >= r - 0.05, (
        f"Pontormo ground_color should be cool (B ≥ R); got R={r:.2f} B={b:.2f}.  "
        f"Use a cool grey-lilac imprimatura, not the warm ochre of the High Renaissance.")


def test_pontormo_famous_works_include_deposition():
    """Pontormo must list the Deposition from the Cross as a famous work."""
    s = get_style("pontormo")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("deposition" in t for t in titles), (
        "Pontormo famous works should include the Deposition from the Cross "
        "— his supreme Mannerist masterpiece")


def test_pontormo_famous_works_count():
    """Pontormo should have at least 5 famous works documented."""
    s = get_style("pontormo")
    assert len(s.famous_works) >= 5, (
        f"pontormo should have ≥5 famous works; got {len(s.famous_works)}")


def test_pontormo_inspiration_references_dissonance_pass():
    """Pontormo inspiration must reference pontormo_dissonance_pass."""
    s = get_style("pontormo")
    assert "pontormo_dissonance" in s.inspiration.lower().replace(" ", "_"), (
        "Pontormo inspiration must reference pontormo_dissonance_pass() — "
        "the defining chromatic dissonance technique pass")


def test_pontormo_in_expected_artists():
    """EXPECTED_ARTISTS list must include pontormo."""
    assert "pontormo" in EXPECTED_ARTISTS, (
        "pontormo missing from EXPECTED_ARTISTS — add it to the list")


def test_pontormo_wet_blend_range():
    """Pontormo wet_blend should be in [0.20, 0.40] — crisp zones, not wet-blended."""
    s = get_style("pontormo")
    assert 0.20 <= s.wet_blend <= 0.40, (
        f"Pontormo wet_blend={s.wet_blend:.2f} should be in [0.20, 0.40] "
        f"(dissonant colour zones must stay separated, not blended)")


def test_pontormo_palette_length():
    """Pontormo palette should have at least 6 colours."""
    s = get_style("pontormo")
    assert len(s.palette) >= 6, (
        f"Pontormo palette should have ≥6 colours; got {len(s.palette)}")


# ──────────────────────────────────────────────────────────────────────────────
# FLORENTINE_MANNERIST period — session 52 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_florentine_mannerist_period_present():
    """Period.FLORENTINE_MANNERIST must exist (session 52)."""
    assert hasattr(Period, "FLORENTINE_MANNERIST"), (
        "Period.FLORENTINE_MANNERIST not found — add it to scene_schema.py")
    assert Period.FLORENTINE_MANNERIST in list(Period)


def test_florentine_mannerist_stroke_params_valid():
    """FLORENTINE_MANNERIST stroke_params must return valid defaults."""
    style = Style(
        medium=Medium.OIL,
        period=Period.FLORENTINE_MANNERIST,
        palette=PaletteHint.WARM_EARTH,
    )
    params = style.stroke_params
    assert "stroke_size_face" in params
    assert "stroke_size_bg"   in params
    assert "wet_blend"        in params
    assert "edge_softness"    in params
    assert params["stroke_size_face"] > 0
    assert params["stroke_size_bg"]   > 0
    assert 0.0 <= params["wet_blend"]     <= 1.0
    assert 0.0 <= params["edge_softness"] <= 1.0


def test_florentine_mannerist_wet_blend_low():
    """FLORENTINE_MANNERIST wet_blend should be ≤ 0.40 — crisp dissonant zones."""
    style = Style(
        medium=Medium.OIL,
        period=Period.FLORENTINE_MANNERIST,
        palette=PaletteHint.WARM_EARTH,
    )
    params = style.stroke_params
    assert params["wet_blend"] <= 0.40, (
        f"FLORENTINE_MANNERIST wet_blend={params['wet_blend']:.2f} should be ≤ 0.40 "
        f"— dissonant colour zones must stay separated, not blended into harmony")


def test_florentine_mannerist_in_expected_periods():
    """EXPECTED_PERIODS list must include FLORENTINE_MANNERIST."""
    assert "FLORENTINE_MANNERIST" in EXPECTED_PERIODS, (
        "FLORENTINE_MANNERIST missing from EXPECTED_PERIODS — add it to the list")


# ──────────────────────────────────────────────────────────────────────────────
# Rogier van der Weyden — session 53 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_rogier_van_der_weyden_in_catalog():
    """Rogier van der Weyden (session 53) must be in the catalog."""
    assert "rogier_van_der_weyden" in CATALOG, (
        "rogier_van_der_weyden not found in CATALOG — add it to art_catalog.py")


def test_rogier_van_der_weyden_movement():
    """Weyden movement must reference Early Netherlandish."""
    s = get_style("rogier_van_der_weyden")
    assert "Netherlandish" in s.movement or "netherlandish" in s.movement.lower(), (
        f"Weyden movement should reference 'Netherlandish'; got {s.movement!r}")


def test_rogier_van_der_weyden_palette_length():
    """Weyden palette should have at least 6 colours."""
    s = get_style("rogier_van_der_weyden")
    assert len(s.palette) >= 6, (
        f"Weyden palette should have ≥6 colours; got {len(s.palette)}")


def test_rogier_van_der_weyden_palette_values_in_range():
    """All Weyden palette RGB values must be in [0, 1]."""
    s = get_style("rogier_van_der_weyden")
    for rgb in s.palette:
        assert len(rgb) == 3, f"Weyden palette entry not 3-tuple: {rgb}"
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Weyden palette {rgb}")


def test_rogier_van_der_weyden_edge_softness_low():
    """Weyden edge_softness should be ≤ 0.25 — angular found edges, not sfumato."""
    s = get_style("rogier_van_der_weyden")
    assert s.edge_softness <= 0.25, (
        f"Weyden edge_softness={s.edge_softness:.2f} should be ≤ 0.25 "
        f"(angular found edges characterise his shadow geometry)")


def test_rogier_van_der_weyden_wet_blend_low():
    """Weyden wet_blend should be ≤ 0.20 — precise Flemish dry marks."""
    s = get_style("rogier_van_der_weyden")
    assert s.wet_blend <= 0.20, (
        f"Weyden wet_blend={s.wet_blend:.2f} should be ≤ 0.20 "
        f"— Early Netherlandish panel precision demands dry, controlled marks")


def test_rogier_van_der_weyden_ground_color_valid():
    """Weyden ground_color must be a valid 3-tuple in [0, 1]."""
    s = get_style("rogier_van_der_weyden")
    assert len(s.ground_color) == 3, "Weyden ground_color not a 3-tuple"
    for ch in s.ground_color:
        assert 0.0 <= ch <= 1.0, (
            f"Weyden ground_color channel {ch} out of [0, 1]")


# ──────────────────────────────────────────────────────────────────────────────
# Hans Memling — session 54 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_hans_memling_in_catalog():
    """Hans Memling (session 54) must be in the catalog."""
    assert "hans_memling" in CATALOG, (
        "hans_memling not found in CATALOG — add it to art_catalog.py")


def test_hans_memling_movement():
    """Memling movement must reference Early Netherlandish."""
    s = get_style("hans_memling")
    assert "Netherlandish" in s.movement or "netherlandish" in s.movement.lower(), (
        f"Memling movement should reference 'Netherlandish'; got {s.movement!r}")


def test_hans_memling_palette_length():
    """Memling palette should have at least 6 colours."""
    s = get_style("hans_memling")
    assert len(s.palette) >= 6, (
        f"Memling palette should have ≥6 colours; got {len(s.palette)}")


def test_hans_memling_palette_values_in_range():
    """All Memling palette RGB values must be in [0, 1]."""
    s = get_style("hans_memling")
    for rgb in s.palette:
        assert len(rgb) == 3, f"Memling palette entry not 3-tuple: {rgb}"
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Memling palette {rgb}")


def test_hans_memling_wet_blend_moderate():
    """Memling wet_blend should be between 0.50 and 0.80 — smooth glazed surface."""
    s = get_style("hans_memling")
    assert 0.50 <= s.wet_blend <= 0.80, (
        f"Memling wet_blend={s.wet_blend:.2f} should be in [0.50, 0.80] "
        f"— smooth Flemish panel surface with stacked transparent glazes")


def test_hans_memling_edge_softness_moderate():
    """Memling edge_softness should be < 0.50 — found edges, not sfumato."""
    s = get_style("hans_memling")
    assert s.edge_softness < 0.50, (
        f"Memling edge_softness={s.edge_softness:.2f} should be < 0.50 "
        f"— Flemish found edges: precise, not dissolved into atmospheric haze")


def test_hans_memling_stroke_size_fine():
    """Memling stroke_size should be ≤ 5 — very fine, jewel-like mark-making."""
    s = get_style("hans_memling")
    assert s.stroke_size <= 5, (
        f"Memling stroke_size={s.stroke_size} should be ≤ 5 "
        f"— Flemish micro-detail demands fine, controlled marks")


def test_hans_memling_ground_color_valid():
    """Memling ground_color must be a valid 3-tuple in [0, 1]."""
    s = get_style("hans_memling")
    assert len(s.ground_color) == 3, "Memling ground_color not a 3-tuple"
    for ch in s.ground_color:
        assert 0.0 <= ch <= 1.0, (
            f"Memling ground_color channel {ch} out of [0, 1]")


def test_hans_memling_ground_color_warm_light():
    """Memling ground_color should be a warm, light ochre — allows glazes to retain luminosity."""
    s = get_style("hans_memling")
    r, g, b = s.ground_color
    # Should be a warm colour: R > B
    assert r > b, (
        f"Memling ground should be warm (R > B); got R={r:.2f}  B={b:.2f}")
    # Should be reasonably light — not Rembrandt's dark brown ground
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    assert lum >= 0.40, (
        f"Memling ground_color luminance={lum:.2f} should be ≥ 0.40 "
        f"— pale oak panel ground allows transparent glazes to glow")


def test_hans_memling_famous_works_nonempty():
    """Memling famous_works must contain at least three entries."""
    s = get_style("hans_memling")
    assert len(s.famous_works) >= 3, (
        f"Memling famous_works should have ≥3 entries; got {len(s.famous_works)}")


def test_hans_memling_subsurface_blue_green_in_palette():
    """Memling palette must include a blue-green entry for the subsurface flesh quality."""
    s = get_style("hans_memling")
    # Look for at least one palette entry where G and B together dominate R:
    # the characteristic blue-green shadow undertone of Flemish flesh.
    has_blue_green = any(
        (g + b) > (r * 1.5)
        for r, g, b in s.palette
    )
    assert has_blue_green, (
        "Memling palette should include a blue-green entry for the "
        "subsurface flesh shadow quality — no such entry found")


# ──────────────────────────────────────────────────────────────────────────────
# Bronzino — session 56 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_bronzino_in_catalog():
    """bronzino must be present in CATALOG (session 56)."""
    assert "bronzino" in CATALOG, (
        "bronzino missing from CATALOG — add it to art_catalog.py")


def test_bronzino_movement_is_mannerist():
    """Bronzino's movement must be Florentine Mannerism."""
    s = get_style("bronzino")
    assert "manner" in s.movement.lower() or "mannerist" in s.movement.lower(), (
        f"Bronzino movement should be Mannerism-related; got {s.movement!r}")


def test_bronzino_palette_cool_ivory_highlight():
    """Bronzino palette must contain a cool pale ivory highlight (all channels > 0.80)."""
    s = get_style("bronzino")
    pale = [(r, g, b) for r, g, b in s.palette if r > 0.80 and g > 0.80 and b > 0.75]
    assert len(pale) >= 1, (
        "Bronzino palette should include at least one cool pale ivory highlight "
        f"(R > 0.80, G > 0.80, B > 0.75); palette={s.palette}")


def test_bronzino_palette_deep_shadow():
    """Bronzino palette must contain a deep cool shadow (all channels < 0.45)."""
    s = get_style("bronzino")
    dark = [(r, g, b) for r, g, b in s.palette if r < 0.45 and g < 0.45 and b < 0.45]
    assert len(dark) >= 1, (
        "Bronzino palette should include at least one deep shadow colour; "
        f"palette={s.palette}")


def test_bronzino_wet_blend_low():
    """Bronzino wet_blend must be ≤ 0.25 — precise Florentine court marks."""
    s = get_style("bronzino")
    assert s.wet_blend <= 0.25, (
        f"Bronzino wet_blend={s.wet_blend:.2f} should be ≤ 0.25 "
        f"— court precision demands dry, controlled marks without wet diffusion")


def test_bronzino_edge_softness_precise():
    """Bronzino edge_softness must be ≤ 0.30 — Florentine draughtsmanship, not sfumato."""
    s = get_style("bronzino")
    assert s.edge_softness <= 0.30, (
        f"Bronzino edge_softness={s.edge_softness:.2f} should be ≤ 0.30 "
        f"— Florentine drawing tradition: found edges, no sfumato dissolution")


def test_bronzino_famous_works_include_eleanor():
    """Bronzino must list the Portrait of Eleanor of Toledo as a famous work."""
    s = get_style("bronzino")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("eleanor" in t or "toledo" in t for t in titles), (
        "Bronzino famous works should include the Portrait of Eleanor of Toledo "
        "— his most celebrated and technically refined surviving work")


def test_bronzino_famous_works_count():
    """Bronzino should have at least 5 famous works documented."""
    s = get_style("bronzino")
    assert len(s.famous_works) >= 5, (
        f"Bronzino should have ≥5 famous works; got {len(s.famous_works)}")


def test_bronzino_inspiration_references_enamel_pass():
    """Bronzino inspiration must reference bronzino_enamel_skin_pass."""
    s = get_style("bronzino")
    assert "bronzino_enamel" in s.inspiration.lower().replace(" ", "_"), (
        "Bronzino inspiration must reference bronzino_enamel_skin_pass() — "
        "the defining enamel-smooth flesh technique pass")


def test_bronzino_in_expected_artists():
    """EXPECTED_ARTISTS list must include bronzino."""
    assert "bronzino" in EXPECTED_ARTISTS, (
        "bronzino missing from EXPECTED_ARTISTS — add it to the list")


def test_bronzino_palette_length():
    """Bronzino palette should have at least 6 colours."""
    s = get_style("bronzino")
    assert len(s.palette) >= 6, (
        f"Bronzino palette should have ≥6 colours; got {len(s.palette)}")


def test_bronzino_palette_values_in_range():
    """All Bronzino palette RGB values must be in [0, 1]."""
    s = get_style("bronzino")
    for rgb in s.palette:
        assert len(rgb) == 3, f"Bronzino palette entry not 3-tuple: {rgb}"
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Bronzino palette {rgb}")


def test_bronzino_ground_color_cool_neutral():
    """Bronzino ground_color must be a cool neutral (B not far below R)."""
    s = get_style("bronzino")
    r, g, b = s.ground_color
    # Cool neutral: B should be within 0.12 of R (not a warm amber like Rembrandt)
    assert abs(r - b) <= 0.12, (
        f"Bronzino ground_color should be cool-neutral (|R-B| ≤ 0.12); "
        f"got R={r:.2f}  B={b:.2f} — use a pale restrained neutral, not warm ochre")


def test_bronzino_ground_color_pale():
    """Bronzino ground_color should be relatively pale (luminance ≥ 0.40)."""
    s = get_style("bronzino")
    r, g, b = s.ground_color
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    assert lum >= 0.40, (
        f"Bronzino ground_color luminance={lum:.2f} should be ≥ 0.40 "
        f"— pale panel ground allows transparent layers to retain luminosity")


def test_bronzino_glazing_cool():
    """Bronzino glazing must be cool (B ≥ R − 0.08) — silvery ivory, not warm amber."""
    s = get_style("bronzino")
    assert s.glazing is not None, (
        "Bronzino.glazing should not be None — he used a cool pale ivory unifying glaze")
    r, g, b = s.glazing
    assert b >= r - 0.08, (
        f"Bronzino glazing should be cool-toned (B ≥ R−0.08); "
        f"got R={r:.2f}  B={b:.2f} — glazing should be silvery ivory, not warm amber")


# ──────────────────────────────────────────────────────────────────────────────
# Tintoretto (session 53)
# ──────────────────────────────────────────────────────────────────────────────

def test_tintoretto_in_catalog():
    """Tintoretto (session 53) must be present in CATALOG."""
    assert "tintoretto" in CATALOG


def test_tintoretto_in_expected_artists():
    """EXPECTED_ARTISTS list must include tintoretto."""
    assert "tintoretto" in EXPECTED_ARTISTS, (
        "tintoretto missing from EXPECTED_ARTISTS — add it to the list")


def test_tintoretto_movement():
    """Tintoretto movement must reference Venetian and Mannerism."""
    s = get_style("tintoretto")
    movement_lower = s.movement.lower()
    assert "venetian" in movement_lower or "mannerist" in movement_lower.replace("mannerism", "mannerist"), (
        f"Tintoretto movement should reference Venetian or Mannerism; got: {s.movement!r}")


def test_tintoretto_palette_length():
    """Tintoretto palette should have at least 6 colours."""
    s = get_style("tintoretto")
    assert len(s.palette) >= 6, (
        f"Tintoretto palette should have ≥6 colours; got {len(s.palette)}")


def test_tintoretto_palette_values_in_range():
    """All Tintoretto palette RGB values must be in [0, 1]."""
    s = get_style("tintoretto")
    for rgb in s.palette:
        assert len(rgb) == 3, f"Tintoretto palette entry not 3-tuple: {rgb}"
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Tintoretto palette {rgb}")


def test_tintoretto_ground_very_dark():
    """Tintoretto ground_color must be very dark (luminance ≤ 0.12) — near-black Venetian void."""
    s = get_style("tintoretto")
    r, g, b = s.ground_color
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    assert lum <= 0.12, (
        f"Tintoretto ground_color luminance={lum:.3f} should be ≤ 0.12 "
        f"— near-black Venetian void ground is the defining technical condition "
        f"for his dramatic silver highlights to read against")


def test_tintoretto_wet_blend_moderate():
    """Tintoretto wet_blend must be in 0.25–0.50 — impasted marks, semi-wet but not Titian fluid."""
    s = get_style("tintoretto")
    assert 0.25 <= s.wet_blend <= 0.50, (
        f"Tintoretto wet_blend={s.wet_blend:.2f} should be 0.25–0.50 "
        f"— impasted, semi-wet marks that stay directional but allow slight blending")


def test_tintoretto_famous_works_count():
    """Tintoretto should have at least 5 famous works documented."""
    s = get_style("tintoretto")
    assert len(s.famous_works) >= 5, (
        f"Tintoretto should have ≥5 famous works; got {len(s.famous_works)}")


def test_tintoretto_famous_works_include_miracle():
    """Tintoretto must list The Miracle of the Slave as a famous work."""
    s = get_style("tintoretto")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("miracle" in t or "slave" in t for t in titles), (
        "Tintoretto famous works should include The Miracle of the Slave (1548) "
        "— his career-making public masterwork")


def test_tintoretto_inspiration_references_dynamic_light_pass():
    """Tintoretto inspiration must reference tintoretto_dynamic_light_pass."""
    s = get_style("tintoretto")
    assert "tintoretto_dynamic_light" in s.inspiration.lower().replace(" ", "_"), (
        "Tintoretto inspiration must reference tintoretto_dynamic_light_pass() — "
        "the defining silver lightning-highlight technique pass")


def test_tintoretto_glazing_amber():
    """Tintoretto glazing must be warm amber (R ≥ B + 0.15) — deep Venetian varnish."""
    s = get_style("tintoretto")
    assert s.glazing is not None, (
        "Tintoretto.glazing should not be None — he used a deep amber Venetian varnish")
    r, g, b = s.glazing
    assert r >= b + 0.15, (
        f"Tintoretto glazing should be warm amber (R ≥ B+0.15); "
        f"got R={r:.2f}  B={b:.2f} — glazing must be deep amber, not silver-cool")


# ── Giorgione ────────────────────────────────────────────────────────────────

def test_giorgione_in_catalog():
    """Giorgione must be present in the CATALOG."""
    assert "giorgione" in CATALOG, (
        "'giorgione' key not found in CATALOG — add the Giorgione entry to art_catalog.py")


def test_giorgione_artist_name():
    """Giorgione entry must carry the full birth name."""
    s = get_style("giorgione")
    assert "Giorgione" in s.artist, (
        f"Giorgione artist field should include 'Giorgione'; got {s.artist!r}")
    assert "Castelfranco" in s.artist, (
        f"Giorgione artist field should include 'Castelfranco'; got {s.artist!r}")


def test_giorgione_movement_venetian_high_renaissance():
    """Giorgione movement must be Venetian High Renaissance."""
    s = get_style("giorgione")
    assert "Venetian High Renaissance" in s.movement, (
        f"Giorgione movement should be 'Venetian High Renaissance'; got {s.movement!r}")


def test_giorgione_nationality_italian():
    """Giorgione must be recorded as Italian."""
    s = get_style("giorgione")
    assert s.nationality.lower() == "italian", (
        f"Giorgione nationality should be 'Italian'; got {s.nationality!r}")


def test_giorgione_palette_count():
    """Giorgione must have 6–8 palette colours."""
    s = get_style("giorgione")
    assert 6 <= len(s.palette) <= 8, (
        f"Giorgione palette should have 6–8 colours; got {len(s.palette)}")


def test_giorgione_palette_warm_light():
    """Giorgione's lightest palette colour must be warm (R ≥ B + 0.08) — pale ivory lit flesh."""
    s = get_style("giorgione")
    lightest = max(s.palette, key=lambda c: 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2])
    r, g, b = lightest
    assert r >= b + 0.08, (
        f"Giorgione lightest colour should be warm (R ≥ B+0.08 for ivory flesh); "
        f"got R={r:.2f}  B={b:.2f} — Giorgione's lit flesh is warm pale ivory, not silver-cool")


def test_giorgione_palette_has_cool_blue():
    """Giorgione palette must contain at least one cool blue (B ≥ R + 0.10) for sky/distance."""
    s = get_style("giorgione")
    cool_blues = [(r, g, b) for r, g, b in s.palette if b >= r + 0.10]
    assert len(cool_blues) >= 1, (
        "Giorgione palette should contain at least one cool blue (B ≥ R+0.10) — "
        "his Prussian-blue sky and atmospheric distances are characteristic")


def test_giorgione_ground_warm_amber():
    """Giorgione ground must be warm amber (R ≥ B + 0.20) — Venetian honey-panel preparation."""
    s = get_style("giorgione")
    r, g, b = s.ground_color
    assert r >= b + 0.20, (
        f"Giorgione ground_color should be warm amber (R ≥ B+0.20); "
        f"got R={r:.2f}  B={b:.2f} — his warm honey-panel is lighter and warmer than Tintoretto")


def test_giorgione_ground_lighter_than_tintoretto():
    """Giorgione ground luminance must exceed Tintoretto's near-black ground."""
    g_style = get_style("giorgione")
    t_style = get_style("tintoretto")
    def lum(c): return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]
    assert lum(g_style.ground_color) > lum(t_style.ground_color), (
        "Giorgione ground must be lighter than Tintoretto's near-black ground — "
        "Giorgione used a warm amber panel, not Tintoretto's void black priming")


def test_giorgione_stroke_size_moderate():
    """Giorgione stroke_size must be 5–9 — broader than Bellini, smaller than Titian's impasto."""
    s = get_style("giorgione")
    assert 5 <= s.stroke_size <= 9, (
        f"Giorgione stroke_size={s.stroke_size} should be 5–9 "
        f"— broader than Bellini's micro-detail (3) but finer than Titian's gestural impasto (12)")


def test_giorgione_wet_blend_high():
    """Giorgione wet_blend must be 0.55–0.70 — tonal building requires liquid wet-into-wet."""
    s = get_style("giorgione")
    assert 0.55 <= s.wet_blend <= 0.70, (
        f"Giorgione wet_blend={s.wet_blend:.2f} should be 0.55–0.70 "
        f"— 'pittura di macchia' demands colour to flow freely between tonal zones")


def test_giorgione_edge_softness_high():
    """Giorgione edge_softness must be 0.60–0.82 — soft-but-present, not crisp Flemish nor dissolved sfumato."""
    s = get_style("giorgione")
    assert 0.60 <= s.edge_softness <= 0.82, (
        f"Giorgione edge_softness={s.edge_softness:.2f} should be 0.60–0.82 "
        f"— his edges are softer than Flemish precision but firmer than Leonardo's sfumato")


def test_giorgione_glazing_warm_amber():
    """Giorgione glazing must be warm amber (R ≥ B + 0.30) — honey Venetian varnish."""
    s = get_style("giorgione")
    assert s.glazing is not None, (
        "Giorgione.glazing should not be None — he used a deep honey-amber Venetian varnish")
    r, g, b = s.glazing
    assert r >= b + 0.30, (
        f"Giorgione glazing should be warm amber (R ≥ B+0.30); "
        f"got R={r:.2f}  B={b:.2f} — the honey varnish is warmer than Tintoretto's amber")


def test_giorgione_crackle():
    """Giorgione crackle must be True — old Venetian panel paintings age with craquelure."""
    s = get_style("giorgione")
    assert s.crackle is True, (
        "Giorgione.crackle should be True — Venetian panel paintings develop pronounced "
        "craquelure over 500+ years")


def test_giorgione_chromatic_split_false():
    """Giorgione chromatic_split must be False — tonal Venetian painting, not Seuratian divisionism."""
    s = get_style("giorgione")
    assert s.chromatic_split is False, (
        "Giorgione.chromatic_split should be False — his tonalismo is the antithesis of "
        "Seurat's divisionist dot separation; chromatic splitting would destroy the tonal fusion")


def test_giorgione_famous_works_count():
    """Giorgione must have at least 5 famous works documented."""
    s = get_style("giorgione")
    assert len(s.famous_works) >= 5, (
        f"Giorgione should have ≥5 famous works; got {len(s.famous_works)}")


def test_giorgione_famous_works_include_tempest():
    """Giorgione must list The Tempest as a famous work."""
    s = get_style("giorgione")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("tempest" in t for t in titles), (
        "Giorgione famous works should include The Tempest (c.1508) — "
        "his most celebrated and studied surviving work")


def test_giorgione_famous_works_include_sleeping_venus():
    """Giorgione must list Sleeping Venus as a famous work."""
    s = get_style("giorgione")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("sleeping" in t or "venus" in t for t in titles), (
        "Giorgione famous works should include Sleeping Venus — "
        "the reclining nude he left unfinished, completed by Titian")


def test_giorgione_technique_mentions_tonalismo():
    """Giorgione technique description must reference tonal painting / tonalismo."""
    s = get_style("giorgione")
    lower = s.technique.lower()
    assert "tonal" in lower or "tonalismo" in lower or "macchia" in lower, (
        "Giorgione technique must describe tonalismo / pittura di macchia — "
        "his defining innovation of composition through tone rather than line")


def test_giorgione_inspiration_references_tonal_poetry_pass():
    """Giorgione inspiration must reference giorgione_tonal_poetry_pass()."""
    s = get_style("giorgione")
    assert "giorgione_tonal_poetry_pass()" in s.inspiration, (
        "Giorgione inspiration must reference giorgione_tonal_poetry_pass() — "
        "see Tintoretto or Bronzino for the expected format")


def test_venetian_high_renaissance_period_in_enum():
    """Period.VENETIAN_HIGH_RENAISSANCE must exist in the Period enum."""
    assert hasattr(Period, "VENETIAN_HIGH_RENAISSANCE"), (
        "Period.VENETIAN_HIGH_RENAISSANCE not found — add it to the Period enum in scene_schema.py")


def test_venetian_high_renaissance_stroke_params():
    """Style with Period.VENETIAN_HIGH_RENAISSANCE must return valid stroke_params."""
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_HIGH_RENAISSANCE)
    params = style.stroke_params
    assert "stroke_size_face" in params
    assert "wet_blend" in params
    assert "edge_softness" in params
    # Giorgione: moderate face strokes (5–9), not Bellini's micro-detail nor Titian's impasto
    assert 5 <= params["stroke_size_face"] <= 9, (
        f"VENETIAN_HIGH_RENAISSANCE stroke_size_face should be 5–9; "
        f"got {params['stroke_size_face']}")
    # High wet_blend: tonal building demands wet-into-wet liquid blending
    assert params["wet_blend"] >= 0.55, (
        f"VENETIAN_HIGH_RENAISSANCE wet_blend should be ≥0.55 for tonalismo; "
        f"got {params['wet_blend']:.2f}")
    # High edge_softness: soft-but-present atmospheric Giorgione edge
    assert params["edge_softness"] >= 0.60, (
        f"VENETIAN_HIGH_RENAISSANCE edge_softness should be ≥0.60; "
        f"got {params['edge_softness']:.2f}")


# ── Venetian Mannerist ────────────────────────────────────────────────────────

def test_venetian_mannerist_period_in_enum():
    """Period.VENETIAN_MANNERIST must exist in the Period enum."""
    assert hasattr(Period, "VENETIAN_MANNERIST"), (
        "Period.VENETIAN_MANNERIST not found — add it to the Period enum in scene_schema.py")


def test_venetian_mannerist_stroke_params():
    """Style with Period.VENETIAN_MANNERIST must return valid stroke_params."""
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_MANNERIST)
    params = style.stroke_params
    assert "stroke_size_face" in params
    assert "wet_blend" in params
    assert "edge_softness" in params
    # Tintoretto: bold face strokes (≥8), high drama
    assert params["stroke_size_face"] >= 8, (
        f"VENETIAN_MANNERIST stroke_size_face should be ≥8 for bold impasto; "
        f"got {params['stroke_size_face']}")
    # Venetian Mannerist: moderate wet_blend (semi-impasted)
    assert 0.20 <= params["wet_blend"] <= 0.55, (
        f"VENETIAN_MANNERIST wet_blend should be 0.20–0.55; got {params['wet_blend']:.2f}")


# ── Veronese (Session 59) ─────────────────────────────────────────────────────

def test_veronese_in_catalog():
    """Veronese must be present in CATALOG."""
    assert "veronese" in CATALOG, (
        "veronese not found in CATALOG — add the entry to art_catalog.py")


def test_veronese_artist_name():
    """Veronese artist name must include Paolo Caliari or Paolo Veronese."""
    s = get_style("veronese")
    assert "Paolo" in s.artist and ("Veronese" in s.artist or "Caliari" in s.artist), (
        f"Veronese artist name incorrect: {s.artist!r} — "
        f"should reference Paolo Caliari / Paolo Veronese")


def test_veronese_ground_color_warm_ochre():
    """Veronese ground_color must be warm (R > B) — warm ochre-light panel."""
    s = get_style("veronese")
    r, g, b = s.ground_color
    assert r > b + 0.20, (
        f"Veronese ground must be warm ochre; got R={r:.2f} B={b:.2f} — "
        f"not as dark as Tintoretto, lighter than Giorgione's honey amber")


def test_veronese_stroke_size_moderate():
    """Veronese stroke_size should be 7–11 — confident marks, not micro-detail."""
    s = get_style("veronese")
    assert 7 <= s.stroke_size <= 11, (
        f"Veronese stroke_size should be 7–11 for confident Venetian impasto; "
        f"got {s.stroke_size}")


def test_veronese_wet_blend_moderate():
    """Veronese wet_blend must be in 0.35–0.62 — decisive wet-on-wet, not full tonal pooling."""
    s = get_style("veronese")
    assert 0.35 <= s.wet_blend <= 0.62, (
        f"Veronese wet_blend should be 0.35–0.62; got {s.wet_blend:.2f} — "
        f"confident fresh marks, less dissolved than Giorgione (0.62)")


def test_veronese_edge_softness_crisp():
    """Veronese edge_softness must be ≤ 0.55 — figures stand in clear light, not dissolved."""
    s = get_style("veronese")
    assert s.edge_softness <= 0.55, (
        f"Veronese edge_softness should be ≤0.55; got {s.edge_softness:.2f} — "
        f"Veronese's clear architecture and confident forms demand readable edges")


def test_veronese_chromatic_split_false():
    """Veronese chromatic_split must be False — Venetian colourism, not Seuratian divisionism."""
    s = get_style("veronese")
    assert s.chromatic_split is False, (
        "Veronese chromatic_split should be False — his brilliant palette is achieved "
        "through direct colour zones, not complementary-dot splitting")


def test_veronese_crackle():
    """Veronese crackle must be True — old Venetian canvas paintings show craquelure."""
    s = get_style("veronese")
    assert s.crackle is True, (
        "Veronese.crackle should be True — 16th-century Venetian canvases develop "
        "craquelure over centuries")


def test_veronese_famous_works_count():
    """Veronese must have at least 5 famous works documented."""
    s = get_style("veronese")
    assert len(s.famous_works) >= 5, (
        f"Veronese should have ≥5 famous works; got {len(s.famous_works)}")


def test_veronese_famous_works_include_wedding_at_cana():
    """Veronese must list The Wedding at Cana as a famous work."""
    s = get_style("veronese")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("cana" in t or "wedding" in t for t in titles), (
        "Veronese famous works should include The Wedding at Cana (1563) — "
        "his largest canvas and most celebrated feast scene")


def test_veronese_technique_mentions_colour_or_luminous():
    """Veronese technique description must reference his luminous colour quality."""
    s = get_style("veronese")
    lower = s.technique.lower()
    assert any(kw in lower for kw in ("luminous", "colour", "color", "palette", "saturated")), (
        "Veronese technique must describe his luminous colour quality — "
        "the defining characteristic that distinguishes him from Titian and Tintoretto")


def test_veronese_inspiration_references_luminous_feast_pass():
    """Veronese inspiration must reference veronese_luminous_feast_pass()."""
    s = get_style("veronese")
    assert "veronese_luminous_feast_pass()" in s.inspiration, (
        "Veronese inspiration must reference veronese_luminous_feast_pass() — "
        "see Giorgione or Tintoretto for the expected format")


# ── Venetian Colorist period ──────────────────────────────────────────────────

def test_venetian_colorist_period_in_enum():
    """Period.VENETIAN_COLORIST must exist in the Period enum."""
    assert hasattr(Period, "VENETIAN_COLORIST"), (
        "Period.VENETIAN_COLORIST not found — add it to the Period enum in scene_schema.py")


def test_venetian_colorist_stroke_params():
    """Style with Period.VENETIAN_COLORIST must return valid stroke_params."""
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_COLORIST)
    params = style.stroke_params
    assert "stroke_size_face" in params
    assert "wet_blend" in params
    assert "edge_softness" in params
    # Veronese: confident face strokes (7–11), clear architectural quality
    assert 7 <= params["stroke_size_face"] <= 11, (
        f"VENETIAN_COLORIST stroke_size_face should be 7–11; "
        f"got {params['stroke_size_face']}")
    # Moderate wet_blend: decisive wet-on-wet but not tonal pooling
    assert 0.35 <= params["wet_blend"] <= 0.62, (
        f"VENETIAN_COLORIST wet_blend should be 0.35–0.62; got {params['wet_blend']:.2f}")
    # Crisper edges than Giorgione: figures stand clearly in light
    assert params["edge_softness"] <= 0.55, (
        f"VENETIAN_COLORIST edge_softness should be ≤0.55 for Veronese's "
        f"clear confident forms; got {params['edge_softness']:.2f}")


# ── Bartolomé Esteban Murillo (estilo vaporoso) ───────────────────────────────

def test_murillo_in_catalog():
    """murillo must be present in CATALOG after this session."""
    assert "murillo" in CATALOG, (
        "'murillo' key not found in CATALOG — add the Murillo entry to art_catalog.py")


def test_murillo_in_expected_artists():
    """EXPECTED_ARTISTS list must include murillo."""
    assert "murillo" in EXPECTED_ARTISTS, (
        "murillo must appear in EXPECTED_ARTISTS for catalog completeness tests")


def test_murillo_artist_name():
    """murillo artist name must be the full Spanish Baroque name."""
    s = get_style("murillo")
    assert "Murillo" in s.artist, (
        f"murillo artist name should include 'Murillo'; got {s.artist!r}")


def test_murillo_movement_spanish_baroque():
    """Murillo's movement must reference Spanish Baroque."""
    s = get_style("murillo")
    lower = s.movement.lower()
    assert "baroque" in lower or "spanish" in lower, (
        f"murillo movement should include 'Baroque' or 'Spanish'; got {s.movement!r}")


def test_murillo_nationality_spanish():
    """Murillo was Spanish."""
    s = get_style("murillo")
    assert "Spanish" in s.nationality or "spanish" in s.nationality.lower(), (
        f"murillo nationality should be Spanish; got {s.nationality!r}")


def test_murillo_palette_count():
    """Murillo palette must have at least 6 colours."""
    s = get_style("murillo")
    assert len(s.palette) >= 6, (
        f"murillo palette should have ≥6 colours (warm flesh, shadow, etc.); got {len(s.palette)}")


def test_murillo_palette_values_in_range():
    """All Murillo palette RGB values must be in [0, 1]."""
    s = get_style("murillo")
    for i, col in enumerate(s.palette):
        for j, v in enumerate(col):
            assert 0.0 <= v <= 1.0, (
                f"murillo palette[{i}][{j}]={v:.3f} out of [0,1]")


def test_murillo_ground_warm():
    """Murillo's ground_color must be warm (R channel dominates G and B)."""
    s = get_style("murillo")
    r, g, b = s.ground_color
    assert r >= g, (
        f"murillo ground_color must be warm (R≥G); got R={r:.2f} G={g:.2f} B={b:.2f} — "
        f"Murillo's amber-ochre imprimatura pre-warms every colour layer")


def test_murillo_high_wet_blend():
    """Murillo's estilo vaporoso demands high blending — wet_blend must be ≥ 0.55."""
    s = get_style("murillo")
    assert s.wet_blend >= 0.55, (
        f"murillo wet_blend should be ≥0.55 (vaporous blending); got {s.wet_blend:.3f} — "
        f"the estilo vaporoso requires extensive wet-on-wet to dissolve boundaries")


def test_murillo_high_edge_softness():
    """Murillo's vaporous style demands soft edges — edge_softness must be ≥ 0.60."""
    s = get_style("murillo")
    assert s.edge_softness >= 0.60, (
        f"murillo edge_softness should be ≥0.60 (tender edge dissolution); "
        f"got {s.edge_softness:.3f}")


def test_murillo_glazing_warm():
    """Murillo's final glaze must be warm (R channel dominant)."""
    s = get_style("murillo")
    assert s.glazing is not None, "murillo should have a warm unifying glaze"
    r, g, b = s.glazing
    assert r > b, (
        f"murillo glazing should be warm (R>B); got R={r:.2f} B={b:.2f} — "
        f"warm amber-rose final glaze is the capstone of the estilo vaporoso")


def test_murillo_crackle():
    """Murillo's 17th-century oil paintings show craquelure — crackle should be True."""
    s = get_style("murillo")
    assert s.crackle is True, "murillo crackle should be True (aged Spanish Baroque canvas)"


def test_murillo_no_chromatic_split():
    """Murillo predates Seurat — chromatic_split must be False."""
    s = get_style("murillo")
    assert s.chromatic_split is False, (
        "murillo chromatic_split should be False (no Pointillist technique)")


def test_murillo_famous_works_count():
    """Murillo must have at least 5 famous works documented."""
    s = get_style("murillo")
    assert len(s.famous_works) >= 5, (
        f"murillo should have ≥5 famous works; got {len(s.famous_works)}")


def test_murillo_famous_works_include_immaculate_conception():
    """Murillo's most celebrated religious work must appear in famous_works."""
    s = get_style("murillo")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("immaculate" in t or "concepcion" in t or "conception" in t for t in titles), (
        "murillo famous_works must include the Immaculate Conception — "
        "his most celebrated and technically defining work")


def test_murillo_technique_mentions_vaporoso():
    """Murillo technique description must reference his defining 'estilo vaporoso'."""
    s = get_style("murillo")
    lower = s.technique.lower()
    assert any(kw in lower for kw in ("vaporoso", "vaporous", "warm", "glow", "luminous")), (
        "murillo technique must describe the estilo vaporoso (warm luminous diffusion) — "
        "his defining technical and spiritual quality")


def test_murillo_inspiration_references_murillo_vapor_pass():
    """Murillo inspiration must reference murillo_vapor_pass()."""
    s = get_style("murillo")
    assert "murillo_vapor_pass()" in s.inspiration, (
        "murillo inspiration must reference murillo_vapor_pass() — "
        "the dedicated pass implementing the estilo vaporoso")


def test_murillo_warmer_edges_than_holbein():
    """Murillo's edge_softness must be higher than Holbein's (vaporous vs. crisp Northern)."""
    murillo = get_style("murillo")
    holbein = get_style("holbein_the_younger")
    assert murillo.edge_softness > holbein.edge_softness, (
        f"murillo edge_softness ({murillo.edge_softness:.2f}) must exceed "
        f"holbein_the_younger ({holbein.edge_softness:.2f}) — "
        f"Murillo's vaporous tender edges are the opposite of Holbein's precise Northern contour")


def test_murillo_more_blended_than_velazquez():
    """Murillo's wet_blend must be higher than Velázquez's (vaporous vs. cool precision)."""
    murillo   = get_style("murillo")
    velazquez = get_style("velazquez")
    assert murillo.wet_blend > velazquez.wet_blend, (
        f"murillo wet_blend ({murillo.wet_blend:.2f}) must exceed "
        f"velazquez ({velazquez.wet_blend:.2f}) — "
        f"Murillo's estilo vaporoso requires higher blending than Velázquez's cool precision")


# ── SPANISH_BAROQUE period ────────────────────────────────────────────────────

def test_spanish_baroque_period_in_enum():
    """Period.SPANISH_BAROQUE must exist in the Period enum."""
    assert hasattr(Period, "SPANISH_BAROQUE"), (
        "Period.SPANISH_BAROQUE not found — add it to the Period enum in scene_schema.py")


def test_spanish_baroque_stroke_params():
    """Style with Period.SPANISH_BAROQUE must return valid stroke_params."""
    style  = Style(medium=Medium.OIL, period=Period.SPANISH_BAROQUE)
    params = style.stroke_params
    assert "stroke_size_face" in params
    assert "wet_blend" in params
    assert "edge_softness" in params
    # Murillo: moderate face strokes (not Northern micro-detail, not loose Impressionism)
    assert 4 <= params["stroke_size_face"] <= 9, (
        f"SPANISH_BAROQUE stroke_size_face should be 4–9; got {params['stroke_size_face']}")
    # High wet_blend: Murillo's vaporous style requires extensive blending
    assert params["wet_blend"] >= 0.55, (
        f"SPANISH_BAROQUE wet_blend should be ≥0.55 (estilo vaporoso); "
        f"got {params['wet_blend']:.2f}")
    # Soft edges: vaporous quality demands high edge_softness
    assert params["edge_softness"] >= 0.60, (
        f"SPANISH_BAROQUE edge_softness should be ≥0.60 (tender vaporous dissolution); "
        f"got {params['edge_softness']:.2f}")


def test_spanish_baroque_softer_than_baroque():
    """SPANISH_BAROQUE edge_softness must exceed generic BAROQUE (Murillo > Caravaggio)."""
    sp_bq = Style(medium=Medium.OIL, period=Period.SPANISH_BAROQUE).stroke_params
    bq    = Style(medium=Medium.OIL, period=Period.BAROQUE).stroke_params
    assert sp_bq["edge_softness"] > bq["edge_softness"], (
        f"SPANISH_BAROQUE edge_softness ({sp_bq['edge_softness']:.2f}) must exceed "
        f"BAROQUE ({bq['edge_softness']:.2f}) — "
        f"Murillo's vaporous softness is definitionally greater than Baroque's theatrical hard edges")


def test_spanish_baroque_more_blended_than_baroque():
    """SPANISH_BAROQUE wet_blend must exceed generic BAROQUE (Murillo's vapour > chiaroscuro)."""
    sp_bq = Style(medium=Medium.OIL, period=Period.SPANISH_BAROQUE).stroke_params
    bq    = Style(medium=Medium.OIL, period=Period.BAROQUE).stroke_params
    assert sp_bq["wet_blend"] > bq["wet_blend"], (
        f"SPANISH_BAROQUE wet_blend ({sp_bq['wet_blend']:.2f}) must exceed "
        f"BAROQUE ({bq['wet_blend']:.2f}) — "
        f"the estilo vaporoso is built on extensive wet blending, not Baroque's dry drama")


# ── TIEPOLO ────────────────────────────────────────────────────────────────────

def test_tiepolo_in_catalog():
    """Tiepolo must be present in the art catalog (session 59 addition)."""
    assert "tiepolo" in CATALOG, "tiepolo not found in CATALOG"


def test_tiepolo_movement():
    """Tiepolo's movement must identify him as Venetian Rococo."""
    s = get_style("tiepolo")
    lower = s.movement.lower()
    assert "venetian" in lower or "rococo" in lower, (
        f"tiepolo movement should mention 'Venetian' or 'Rococo'; got {s.movement!r}")


def test_tiepolo_palette_includes_azure():
    """Tiepolo's palette must contain a brilliant azure (high B, moderate G, low R)."""
    s = get_style("tiepolo")
    # Azure: B > 0.75, B > R by a significant margin
    has_azure = any(b > 0.75 and b > r + 0.35 for r, g, b in s.palette)
    assert has_azure, (
        "tiepolo palette must include a brilliant azure swatch — "
        "the azure sky is his most distinctive chromatic signature")


def test_tiepolo_palette_includes_naples_yellow():
    """Tiepolo's palette must contain a Naples yellow (high R and G, low B)."""
    s = get_style("tiepolo")
    has_naples = any(r > 0.85 and g > 0.80 and b < 0.80 for r, g, b in s.palette)
    assert has_naples, (
        "tiepolo palette must include Naples yellow — "
        "his defining warm flesh-light tone that gives figures their self-luminous quality")


def test_tiepolo_famous_works_count():
    """Tiepolo must have at least 5 famous works documented."""
    s = get_style("tiepolo")
    assert len(s.famous_works) >= 5, (
        f"tiepolo should have ≥5 famous works; got {len(s.famous_works)}")


def test_tiepolo_famous_works_include_wurzburg():
    """Tiepolo's most celebrated commission (Würzburg frescoes) must appear in famous_works."""
    s = get_style("tiepolo")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("w" in t and ("rzburg" in t or "urzburg" in t or "rzb" in t) for t in titles), (
        "tiepolo famous_works must include the Würzburg Residenz frescoes — "
        "his greatest and most technically ambitious commission")


def test_tiepolo_technique_mentions_celestial():
    """Tiepolo technique description must reference his defining aerial/celestial light quality."""
    s = get_style("tiepolo")
    lower = s.technique.lower()
    assert any(kw in lower for kw in ("celestial", "aerial", "luminous", "azure", "naples")), (
        "tiepolo technique must describe his celestial light system — "
        "the overhead luminosity and azure sky that define his Rococo fresco style")


def test_tiepolo_inspiration_references_tiepolo_celestial_light_pass():
    """Tiepolo inspiration must reference tiepolo_celestial_light_pass()."""
    s = get_style("tiepolo")
    assert "tiepolo_celestial_light_pass()" in s.inspiration, (
        "tiepolo inspiration must reference tiepolo_celestial_light_pass() — "
        "the dedicated pass implementing his celestial overhead luminosity")


def test_tiepolo_lighter_ground_than_tintoretto():
    """Tiepolo's ground must be much lighter than Tintoretto's (pale luminous vs. near-black void)."""
    tiepolo   = get_style("tiepolo")
    tintoretto = get_style("tintoretto")
    tiepolo_lum   = sum(tiepolo.ground_color) / 3
    tintoretto_lum = sum(tintoretto.ground_color) / 3
    assert tiepolo_lum > tintoretto_lum + 0.5, (
        f"tiepolo ground ({tiepolo_lum:.2f}) must be substantially lighter than "
        f"tintoretto ({tintoretto_lum:.2f}) — "
        f"Tiepolo's pale cream imprimatura is the foundation of his aerial luminosity; "
        f"Tintoretto used a near-black void ground for opposite dramatic effect")


def test_tiepolo_higher_wet_blend_than_bronzino():
    """Tiepolo's wet_blend must exceed Bronzino's (Venetian blending vs. Mannerist enamel precision)."""
    tiepolo  = get_style("tiepolo")
    bronzino = get_style("bronzino")
    assert tiepolo.wet_blend > bronzino.wet_blend, (
        f"tiepolo wet_blend ({tiepolo.wet_blend:.2f}) must exceed "
        f"bronzino ({bronzino.wet_blend:.2f}) — "
        f"Tiepolo's Venetian wet-into-wet tradition requires high blending; "
        f"Bronzino's enamel-smooth Mannerist surface demands very low blending")


# ── VENETIAN_ROCOCO period ─────────────────────────────────────────────────────

def test_venetian_rococo_period_in_enum():
    """Period.VENETIAN_ROCOCO must exist in the Period enum."""
    assert hasattr(Period, "VENETIAN_ROCOCO"), (
        "Period.VENETIAN_ROCOCO not found — add it to the Period enum in scene_schema.py")


def test_venetian_rococo_stroke_params():
    """Style with Period.VENETIAN_ROCOCO must return valid stroke_params."""
    style  = Style(medium=Medium.OIL, period=Period.VENETIAN_ROCOCO)
    params = style.stroke_params
    assert "stroke_size_face" in params
    assert "wet_blend" in params
    assert "edge_softness" in params
    # Tiepolo: confident broad marks (not Northern micro-detail, not loose Impressionism)
    assert 7 <= params["stroke_size_face"] <= 12, (
        f"VENETIAN_ROCOCO stroke_size_face should be 7–12; got {params['stroke_size_face']}")
    # High wet_blend: Tiepolo's Venetian wet-into-wet tradition requires it
    assert params["wet_blend"] >= 0.60, (
        f"VENETIAN_ROCOCO wet_blend should be ≥0.60 (Venetian wet-into-wet); "
        f"got {params['wet_blend']:.2f}")
    # Moderate edge_softness: forms clear but aerial
    assert 0.40 <= params["edge_softness"] <= 0.70, (
        f"VENETIAN_ROCOCO edge_softness should be 0.40–0.70 (aerial but resolved); "
        f"got {params['edge_softness']:.2f}")


def test_venetian_rococo_broader_bg_than_venetian_renaissance():
    """VENETIAN_ROCOCO stroke_size_bg must exceed VENETIAN_RENAISSANCE (vast sky vs. portrait bg)."""
    rococo     = Style(medium=Medium.OIL, period=Period.VENETIAN_ROCOCO).stroke_params
    renaissance = Style(medium=Medium.OIL, period=Period.VENETIAN_RENAISSANCE).stroke_params
    assert rococo["stroke_size_bg"] >= renaissance["stroke_size_bg"], (
        f"VENETIAN_ROCOCO stroke_size_bg ({rococo['stroke_size_bg']}) must be ≥ "
        f"VENETIAN_RENAISSANCE ({renaissance['stroke_size_bg']}) — "
        f"Tiepolo's vast ceiling frescoes need much larger background strokes than Titian's portraits")


# ── aerial_perspective_pass improvement (session 59) ──────────────────────────

def test_aerial_perspective_warm_foreground_push_parameter_exists():
    """aerial_perspective_pass must accept a warm_foreground_push keyword parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.aerial_perspective_pass)
    assert "warm_foreground_push" in sig.parameters, (
        "aerial_perspective_pass missing warm_foreground_push parameter — "
        "session 59 adds warm foreground complementary push to complete atmospheric perspective")


def test_aerial_perspective_fg_band_parameter_exists():
    """aerial_perspective_pass must accept a fg_band keyword parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.aerial_perspective_pass)
    assert "fg_band" in sig.parameters, (
        "aerial_perspective_pass missing fg_band parameter — "
        "controls the lower canvas zone for warm foreground push")


def test_aerial_perspective_warm_foreground_push_defaults_zero():
    """warm_foreground_push must default to 0.0 for full backwards compatibility."""
    import inspect
    from stroke_engine import Painter
    sig   = inspect.signature(Painter.aerial_perspective_pass)
    param = sig.parameters["warm_foreground_push"]
    assert param.default == 0.0, (
        f"warm_foreground_push default should be 0.0 (backwards compatible); "
        f"got {param.default!r}")
# ── Francisco de Zurbarán ──────────────────────────────────────────────────────

def test_zurbaran_in_catalog():
    """CATALOG must contain 'zurbaran' as a valid artist key."""
    assert "zurbaran" in CATALOG, (
        "'zurbaran' not found in CATALOG — add Francisco de Zurbarán to art_catalog.py")


def test_zurbaran_fields_complete():
    """Zurbarán ArtStyle must have all required fields populated."""
    s = get_style("zurbaran")
    assert s.artist,      "zurbaran.artist must be a non-empty string"
    assert s.movement,    "zurbaran.movement must be a non-empty string"
    assert s.nationality, "zurbaran.nationality must be a non-empty string"
    assert s.period,      "zurbaran.period must be a non-empty string"
    assert s.technique,   "zurbaran.technique must be a non-empty string"
    assert s.inspiration, "zurbaran.inspiration must be a non-empty string"
    assert len(s.palette) >= 6, (
        f"zurbaran palette must have ≥6 colours; got {len(s.palette)}")
    assert len(s.famous_works) >= 4, (
        f"zurbaran.famous_works must list ≥4 works; got {len(s.famous_works)}")


def test_zurbaran_palette_in_range():
    """All Zurbarán palette colours must have R, G, B values in [0, 1]."""
    s = get_style("zurbaran")
    for i, (r, g, b) in enumerate(s.palette):
        assert 0.0 <= r <= 1.0, f"zurbaran palette[{i}] R={r:.3f} out of [0, 1]"
        assert 0.0 <= g <= 1.0, f"zurbaran palette[{i}] G={g:.3f} out of [0, 1]"
        assert 0.0 <= b <= 1.0, f"zurbaran palette[{i}] B={b:.3f} out of [0, 1]"


def test_zurbaran_dark_ground():
    """Zurbarán ground_color must be very dark (luminance < 0.12) — the cold void imprimatura."""
    s   = get_style("zurbaran")
    r, g, b = s.ground_color
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    assert lum < 0.12, (
        f"zurbaran ground_color luminance={lum:.3f} must be <0.12 — "
        f"the near-black cold void is the defining ground for Zurbarán's devotional work")


def test_zurbaran_low_wet_blend():
    """Zurbarán wet_blend must be ≤ 0.30 — dry, sculptural mark-making."""
    s = get_style("zurbaran")
    assert s.wet_blend <= 0.30, (
        f"zurbaran wet_blend={s.wet_blend:.2f} must be ≤0.30 — "
        f"Zurbarán's marks are crisp and dry, not vaporous; "
        f"he is the polar opposite of Murillo's estilo vaporoso")


def test_zurbaran_low_edge_softness():
    """Zurbarán edge_softness must be ≤ 0.30 — hard devotional clarity."""
    s = get_style("zurbaran")
    assert s.edge_softness <= 0.30, (
        f"zurbaran edge_softness={s.edge_softness:.2f} must be ≤0.30 — "
        f"Zurbarán's forms emerge from the void with hard, precise edges; "
        f"no sfumato, no atmospheric ambiguity")


def test_zurbaran_inspiration_references_zurbaran_stark_devotion_pass():
    """Zurbarán inspiration must reference zurbaran_stark_devotion_pass()."""
    s = get_style("zurbaran")
    assert "zurbaran_stark_devotion_pass()" in s.inspiration, (
        "Zurbarán inspiration must reference zurbaran_stark_devotion_pass() — "
        "this is the defining pipeline pass for his cold void tonal polarity")


def test_zurbaran_palette_includes_near_black():
    """Zurbarán palette must include at least one near-black colour (luminance < 0.10)."""
    s = get_style("zurbaran")
    near_blacks = [
        (r, g, b) for (r, g, b) in s.palette
        if (0.2126 * r + 0.7152 * g + 0.0722 * b) < 0.10
    ]
    assert len(near_blacks) >= 1, (
        "Zurbarán palette must include at least one near-black colour (lum < 0.10) — "
        "the cold void is the defining feature of his tonal world")


def test_zurbaran_palette_includes_near_white():
    """Zurbarán palette must include at least one near-white colour (luminance > 0.80)."""
    s = get_style("zurbaran")
    near_whites = [
        (r, g, b) for (r, g, b) in s.palette
        if (0.2126 * r + 0.7152 * g + 0.0722 * b) > 0.80
    ]
    assert len(near_whites) >= 1, (
        "Zurbarán palette must include at least one near-white colour (lum > 0.80) — "
        "the crystalline white habit is the signature subject of his career")


def test_zurbaran_drier_than_murillo():
    """Zurbarán wet_blend must be less than Murillo's (austerity vs tenderness)."""
    zb = get_style("zurbaran")
    mu = get_style("murillo")
    assert zb.wet_blend < mu.wet_blend, (
        f"Zurbarán wet_blend ({zb.wet_blend:.2f}) must be less than "
        f"Murillo's ({mu.wet_blend:.2f}) — "
        f"Zurbarán's sculptural dryness is the polar opposite of Murillo's estilo vaporoso")


def test_zurbaran_crisper_than_murillo():
    """Zurbarán edge_softness must be less than Murillo's (hard void vs vaporous dissolution)."""
    zb = get_style("zurbaran")
    mu = get_style("murillo")
    assert zb.edge_softness < mu.edge_softness, (
        f"Zurbarán edge_softness ({zb.edge_softness:.2f}) must be less than "
        f"Murillo's ({mu.edge_softness:.2f}) — "
        f"hard devotional edges vs vaporous soft dissolution")


# ── TENEBRIST vs SPANISH_BAROQUE polarity ─────────────────────────────────────

def test_tenebrist_crisper_than_spanish_baroque():
    """TENEBRIST edge_softness must be less than SPANISH_BAROQUE (Zurbarán < Murillo)."""
    ten  = Style(medium=Medium.OIL, period=Period.TENEBRIST).stroke_params
    baro = Style(medium=Medium.OIL, period=Period.SPANISH_BAROQUE).stroke_params
    assert ten["edge_softness"] < baro["edge_softness"], (
        f"TENEBRIST edge_softness ({ten['edge_softness']:.2f}) must be less than "
        f"SPANISH_BAROQUE ({baro['edge_softness']:.2f}) — "
        f"Zurbarán's hard devotional precision is the polar opposite of Murillo's vaporous softness")




# ── Jean-Baptiste-Camille Corot ───────────────────────────────────────────────

def test_corot_in_catalog():
    """corot must exist as a key in the CATALOG."""
    assert "corot" in CATALOG, "CATALOG must contain a 'corot' entry"


def test_corot_get_style():
    """get_style('corot') must return an ArtStyle with the correct artist name."""
    s = get_style("corot")
    assert "Corot" in s.artist, f"Expected 'Corot' in artist name, got: {s.artist}"


def test_corot_movement_barbizon():
    """Corot movement must reference Barbizon or Proto-Impressionism."""
    s = get_style("corot")
    lower = s.movement.lower()
    assert "barbizon" in lower or "proto" in lower or "impressionism" in lower.replace("-", ""), (
        f"Corot movement should reference Barbizon or Proto-Impressionism; got: {s.movement}")


def test_corot_palette_in_range():
    """All Corot palette colours must have R, G, B values in [0, 1]."""
    s = get_style("corot")
    for i, (r, g, b) in enumerate(s.palette):
        assert 0.0 <= r <= 1.0, f"corot palette[{i}] R={r:.3f} out of [0, 1]"
        assert 0.0 <= g <= 1.0, f"corot palette[{i}] G={g:.3f} out of [0, 1]"
        assert 0.0 <= b <= 1.0, f"corot palette[{i}] B={b:.3f} out of [0, 1]"


def test_corot_high_wet_blend():
    """Corot wet_blend must be >= 0.60 — silvery atmospheric blending."""
    s = get_style("corot")
    assert s.wet_blend >= 0.60, (
        f"corot wet_blend={s.wet_blend:.2f} must be >=0.60 — "
        f"the silver veil requires highly blended tonal transitions")


def test_corot_high_edge_softness():
    """Corot edge_softness must be >= 0.70 — dissolved misty edges."""
    s = get_style("corot")
    assert s.edge_softness >= 0.70, (
        f"corot edge_softness={s.edge_softness:.2f} must be >=0.70 — "
        f"foliage and sky boundaries dissolve in Corot's atmospheric veil")


def test_corot_palette_includes_silvery_tone():
    """Corot palette must include at least one silvery-grey tone (low chroma, mid-high lum)."""
    s = get_style("corot")
    silvery = []
    for (r, g, b) in s.palette:
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        chroma = max(r, g, b) - min(r, g, b)
        if lum > 0.45 and chroma < 0.20:
            silvery.append((r, g, b))
    assert len(silvery) >= 1, (
        "Corot palette must include at least one silvery-grey mid-to-high luminance tone "
        "(lum > 0.45, chroma < 0.20) — the silver veil is the defining quality")


def test_corot_palette_includes_muted_green():
    """Corot palette must include at least one muted green (green dominant, low chroma)."""
    s = get_style("corot")
    muted_greens = [
        (r, g, b) for (r, g, b) in s.palette
        if g > r and g > b and (max(r, g, b) - min(r, g, b)) < 0.30
    ]
    assert len(muted_greens) >= 1, (
        "Corot palette must include at least one muted green (green dominant, chroma <0.30) — "
        "his foliage greens are characteristically desaturated and silvery")


def test_corot_inspiration_references_corot_silver_veil_pass():
    """Corot inspiration must reference corot_silver_veil_pass()."""
    s = get_style("corot")
    assert "corot_silver_veil_pass()" in s.inspiration, (
        "Corot inspiration must reference corot_silver_veil_pass() — "
        "this is the defining pipeline pass for his atmospheric silvery veil")


def test_corot_famous_works_not_empty():
    """Corot must have at least three famous works listed."""
    s = get_style("corot")
    assert len(s.famous_works) >= 3, (
        f"Corot should have at least 3 famous works; got {len(s.famous_works)}")


def test_corot_softer_than_zurbaran():
    """Corot edge_softness must be greater than Zurbarán's (atmospheric veil vs hard devotional void)."""
    co = get_style("corot")
    zu = get_style("zurbaran")
    assert co.edge_softness > zu.edge_softness, (
        f"Corot edge_softness ({co.edge_softness:.2f}) must be greater than "
        f"Zurbarán's ({zu.edge_softness:.2f}) — "
        f"atmospheric silver veil vs hard devotional precision")


def test_corot_more_blended_than_hals():
    """Corot wet_blend must be greater than Frans Hals (atmospheric softness vs bravura dryness)."""
    co = get_style("corot")
    ha = get_style("frans_hals")
    assert co.wet_blend > ha.wet_blend, (
        f"Corot wet_blend ({co.wet_blend:.2f}) must be greater than "
        f"Hals ({ha.wet_blend:.2f}) — "
        f"silvery atmospheric blending vs bravura alla prima dryness")


# ── Session 62: Parmigianino ──────────────────────────────────────────────────

def test_parmigianino_in_catalog():
    """parmigianino must be present in CATALOG (session 62)."""
    assert "parmigianino" in CATALOG, (
        "parmigianino missing from CATALOG — add it to art_catalog.py")


def test_parmigianino_movement_is_mannerist():
    """Parmigianino's movement must be Mannerist."""
    s = get_style("parmigianino")
    assert "manner" in s.movement.lower() or "mannerist" in s.movement.lower(), (
        f"Parmigianino movement should be Mannerism-related; got {s.movement!r}")


def test_parmigianino_nationality_italian():
    """Parmigianino must be Italian."""
    s = get_style("parmigianino")
    assert s.nationality.lower() == "italian", (
        f"Parmigianino nationality should be 'Italian'; got {s.nationality!r}")


def test_parmigianino_palette_length():
    """Parmigianino palette must have at least 7 colours."""
    s = get_style("parmigianino")
    assert len(s.palette) >= 7, (
        f"Parmigianino palette must have ≥7 colours; got {len(s.palette)}")


def test_parmigianino_palette_in_range():
    """All Parmigianino palette colours must have R, G, B values in [0, 1]."""
    s = get_style("parmigianino")
    for i, (r, g, b) in enumerate(s.palette):
        assert 0.0 <= r <= 1.0, f"parmigianino palette[{i}] R={r:.3f} out of [0,1]"
        assert 0.0 <= g <= 1.0, f"parmigianino palette[{i}] G={g:.3f} out of [0,1]"
        assert 0.0 <= b <= 1.0, f"parmigianino palette[{i}] B={b:.3f} out of [0,1]"


def test_parmigianino_palette_has_porcelain_ivory():
    """Parmigianino palette must include at least one high-key cool ivory tone (lum > 0.80)."""
    s = get_style("parmigianino")
    pale = [
        (r, g, b) for r, g, b in s.palette
        if (0.2126 * r + 0.7152 * g + 0.0722 * b) > 0.80
    ]
    assert len(pale) >= 1, (
        "Parmigianino palette must include at least one porcelain ivory tone (lum > 0.80) — "
        "his skin is the palest and coolest of any Italian Mannerist painter")


def test_parmigianino_palette_has_lavender_shadow():
    """Parmigianino palette must include a cool shadow (B > R and B > G, lum < 0.55)."""
    s = get_style("parmigianino")
    lavender = [
        (r, g, b) for r, g, b in s.palette
        if b > r and b > g and (0.2126 * r + 0.7152 * g + 0.0722 * b) < 0.55
    ]
    assert len(lavender) >= 1, (
        "Parmigianino palette must include at least one cool lavender/silver shadow colour "
        "(B > R and B > G, lum < 0.55) — his shadows are silvery lavender, not warm umber")


def test_parmigianino_cool_ground():
    """Parmigianino ground_color must be relatively neutral (not a warm amber ground)."""
    s = get_style("parmigianino")
    r, g, b = s.ground_color
    # The Parma ground is a neutral warm-grey — R should not be >> B
    assert r - b <= 0.15, (
        f"Parmigianino ground_color is too warm: R={r:.2f} B={b:.2f} diff={r - b:.2f} > 0.15.  "
        f"Use a neutral warm-grey Parma ground, not a hot amber imprimatura.")


def test_parmigianino_fine_stroke():
    """Parmigianino stroke_size must be ≤ 5 — fine, controlled marks."""
    s = get_style("parmigianino")
    assert s.stroke_size <= 5, (
        f"Parmigianino stroke_size={s.stroke_size} must be ≤5 — "
        f"Parmigianino used fine, deliberate marks; no impasto or broad brushwork")


def test_parmigianino_has_glazing():
    """Parmigianino must have a non-None glazing tuple — his enamel surface requires glazing."""
    s = get_style("parmigianino")
    assert s.glazing is not None, (
        "Parmigianino.glazing should not be None — he built the characteristic enamel "
        "surface quality through pale cool ivory glazes")


def test_parmigianino_glazing_is_cool():
    """Parmigianino glazing must be cool ivory (B >= R - 0.05)."""
    s = get_style("parmigianino")
    assert s.glazing is not None, "Parmigianino must have glazing set"
    r, g, b = s.glazing
    assert b >= r - 0.05, (
        f"Parmigianino glazing should be cool ivory (B ≥ R - 0.05); "
        f"got R={r:.2f} B={b:.2f} — warm amber glazing would contradict his porcelain aesthetic")


def test_parmigianino_crackle():
    """Parmigianino must have crackle=True — aged panel paintings crackle."""
    s = get_style("parmigianino")
    assert s.crackle is True, (
        "Parmigianino.crackle should be True — his works are panel paintings "
        "that show typical age-crackle patterns")


def test_parmigianino_famous_works_non_empty():
    """Parmigianino must list at least 5 famous works."""
    s = get_style("parmigianino")
    assert len(s.famous_works) >= 5, (
        f"parmigianino should have ≥5 famous works; got {len(s.famous_works)}")


def test_parmigianino_famous_works_include_madonna_long_neck():
    """Parmigianino famous works must include 'Madonna with the Long Neck'."""
    s = get_style("parmigianino")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("long neck" in t or "madonna" in t for t in titles), (
        "Parmigianino famous works should include 'Madonna with the Long Neck' — "
        "his supreme masterpiece of Mannerist elongation")


def test_parmigianino_famous_works_include_convex_mirror():
    """Parmigianino famous works must include the Self-Portrait in a Convex Mirror."""
    s = get_style("parmigianino")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("convex" in t or "mirror" in t for t in titles), (
        "Parmigianino famous works should include 'Self-Portrait in a Convex Mirror' — "
        "one of the most technically astonishing objects of the Italian Renaissance")


def test_parmigianino_inspiration_references_serpentine_pass():
    """Parmigianino inspiration must reference parmigianino_serpentine_elegance_pass()."""
    s = get_style("parmigianino")
    assert "parmigianino_serpentine_elegance_pass()" in s.inspiration, (
        "Parmigianino inspiration must reference parmigianino_serpentine_elegance_pass() — "
        "the defining pipeline pass for his cool porcelain refinement")


def test_parmigianino_in_expected_artists():
    """EXPECTED_ARTISTS list must include parmigianino."""
    assert "parmigianino" in EXPECTED_ARTISTS, (
        "parmigianino missing from EXPECTED_ARTISTS — add it to the list")


def test_parmigianino_edge_softness_in_range():
    """Parmigianino edge_softness should be in [0.50, 0.75] — soft but legible forms."""
    s = get_style("parmigianino")
    assert 0.50 <= s.edge_softness <= 0.75, (
        f"Parmigianino edge_softness={s.edge_softness:.2f} should be in [0.50, 0.75] — "
        f"his forms are softer than Florentine linearity but crisper than Leonardo's sfumato")


def test_parmigianino_cooler_skin_than_titian():
    """Parmigianino skin palette must average cooler than Titian's (B ≥ R in pale tones)."""
    par = get_style("parmigianino")
    tit = get_style("titian")
    # Extract pale (high-lum) colours from each palette as proxy for skin tones
    par_pale = [(r, g, b) for r, g, b in par.palette
                if (0.2126 * r + 0.7152 * g + 0.0722 * b) > 0.60]
    tit_pale = [(r, g, b) for r, g, b in tit.palette
                if (0.2126 * r + 0.7152 * g + 0.0722 * b) > 0.60]
    if par_pale and tit_pale:
        par_avg_rb = sum(b - r for r, g, b in par_pale) / len(par_pale)
        tit_avg_rb = sum(b - r for r, g, b in tit_pale) / len(tit_pale)
        assert par_avg_rb >= tit_avg_rb - 0.05, (
            f"Parmigianino pale tones should be at least as cool as Titian's — "
            f"par B-R avg={par_avg_rb:.3f} vs titian B-R avg={tit_avg_rb:.3f}.  "
            f"Parmigianino's porcelain skin is cooler than Titian's warm amber colorito.")


# ─────────────────────────────────────────────────────────────────────────────
# Session 63 — Canaletto (Giovanni Antonio Canal, 1697–1768)
# Venetian vedutismo: crystal-clear cerulean sky, warm honey-stone masonry,
# cool canal-silver water, crisp architectural precision.
# ─────────────────────────────────────────────────────────────────────────────

def test_canaletto_in_catalog():
    """canaletto must be in CATALOG."""
    assert "canaletto" in CATALOG, (
        "canaletto missing from CATALOG — add the ArtStyle entry for "
        "Giovanni Antonio Canal (1697–1768)")


def test_canaletto_artist_name():
    """canaletto artist name must include 'Canaletto' or 'Canal'."""
    s = get_style("canaletto")
    assert "canal" in s.artist.lower(), (
        f"canaletto artist={s.artist!r} should include 'Canal' — "
        f"his canonical name is Giovanni Antonio Canal (Canaletto)")


def test_canaletto_movement():
    """canaletto movement must reference vedutismo or veduta."""
    s = get_style("canaletto")
    assert "vedut" in s.movement.lower(), (
        f"canaletto movement={s.movement!r} should reference 'Vedutismo' or 'Veduta' — "
        f"the topographically precise urban-view genre he perfected")


def test_canaletto_nationality():
    """canaletto nationality must be Italian."""
    s = get_style("canaletto")
    assert s.nationality.lower() == "italian", (
        f"canaletto nationality={s.nationality!r} should be 'Italian' — "
        f"he was born in Venice and spent most of his career there")


def test_canaletto_palette_has_cerulean():
    """canaletto palette must contain a strong cerulean-blue sky colour (B > 0.75, B > R+0.15)."""
    s = get_style("canaletto")
    cerulean = [(r, g, b) for r, g, b in s.palette if b > 0.75 and b > r + 0.15]
    assert cerulean, (
        "canaletto palette must include a cerulean-blue sky colour — "
        "his skies are the clearest and most saturated in the Western landscape tradition")


def test_canaletto_palette_has_warm_stone():
    """canaletto palette must contain a warm honey-stone colour (R > 0.65, R > B + 0.25)."""
    s = get_style("canaletto")
    stone = [(r, g, b) for r, g, b in s.palette if r > 0.65 and r > b + 0.25]
    assert stone, (
        "canaletto palette must include a warm honey-stone colour — "
        "the sunlit Venetian palazzo masonry that fills the centre of every veduta")


def test_canaletto_low_wet_blend():
    """canaletto wet_blend should be <= 0.30 — crisp architectural edges, not sfumato."""
    s = get_style("canaletto")
    assert s.wet_blend <= 0.30, (
        f"canaletto wet_blend={s.wet_blend:.2f} should be ≤ 0.30 — "
        f"his direct Venetian noon light creates crisp shadow edges, "
        f"the opposite of Leonardo's sfumato dissolution")


def test_canaletto_low_edge_softness():
    """canaletto edge_softness should be <= 0.25 — precise stone courses, not dissolved forms."""
    s = get_style("canaletto")
    assert s.edge_softness <= 0.25, (
        f"canaletto edge_softness={s.edge_softness:.2f} should be ≤ 0.25 — "
        f"architectural precision demands legible stone courses and window openings")


def test_canaletto_famous_works_include_stonemasons_yard():
    """canaletto famous works must include 'The Stonemason's Yard'."""
    s = get_style("canaletto")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("stonemason" in t or "mason" in t for t in titles), (
        "canaletto famous works must include 'The Stonemason's Yard' — "
        "his most celebrated painting for its unidealized documentary realism")


def test_canaletto_famous_works_include_grand_canal():
    """canaletto famous works must include a Grand Canal painting."""
    s = get_style("canaletto")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("grand canal" in t or "canal grande" in t for t in titles), (
        "canaletto famous works must include a Grand Canal view — "
        "the Grand Canal was the defining subject of his career")


def test_canaletto_inspiration_references_veduta_pass():
    """canaletto inspiration must reference canaletto_luminous_veduta_pass()."""
    s = get_style("canaletto")
    assert "canaletto_luminous_veduta_pass()" in s.inspiration, (
        "canaletto inspiration must reference canaletto_luminous_veduta_pass() — "
        "the defining pipeline pass for his cerulean sky, warm stone, and canal-silver palette")


def test_canaletto_inspiration_references_varnish_pass():
    """canaletto inspiration must reference old_master_varnish_pass()."""
    s = get_style("canaletto")
    assert "old_master_varnish_pass()" in s.inspiration, (
        "canaletto inspiration must reference old_master_varnish_pass() — "
        "the aged amber varnish patina pass introduced in session 63")


def test_canaletto_in_expected_artists():
    """EXPECTED_ARTISTS list must include canaletto."""
    assert "canaletto" in EXPECTED_ARTISTS, (
        "canaletto missing from EXPECTED_ARTISTS — add it to the list")


def test_canaletto_crackle():
    """canaletto crackle should be True — aged panel/canvas surface."""
    s = get_style("canaletto")
    assert s.crackle is True, (
        f"canaletto crackle={s.crackle} should be True — "
        f"his works are on aged canvases with characteristic craquelure")


def test_canaletto_warmer_than_corot():
    """canaletto palette must average warmer than corot's (R > B in dominant tones)."""
    can = get_style("canaletto")
    cor = get_style("corot")
    # Average R-B across full palettes as warmth proxy
    can_warmth = sum(r - b for r, g, b in can.palette) / len(can.palette)
    cor_warmth = sum(r - b for r, g, b in cor.palette) / len(cor.palette)
    assert can_warmth >= cor_warmth - 0.05, (
        f"canaletto palette should be at least as warm as corot's — "
        f"Venetian noon sun vs Barbizon silver haze: "
        f"canaletto R-B avg={can_warmth:.3f} vs corot R-B avg={cor_warmth:.3f}")


# ──────────────────────────────────────────────────────────────────────────────
# Vigée Le Brun — session 64 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_vigee_le_brun_in_catalog():
    """Vigée Le Brun (session 64) must be present in CATALOG."""
    assert "vigee_le_brun" in CATALOG, (
        "vigee_le_brun missing from CATALOG — add it to art_catalog.py")


def test_vigee_le_brun_movement():
    """vigee_le_brun movement must reference Neoclassical or Rococo portraiture."""
    s = get_style("vigee_le_brun")
    mv = s.movement.lower()
    assert "neoclassical" in mv or "rococo" in mv, (
        f"vigee_le_brun movement should reference Neoclassical or Rococo; "
        f"got: {s.movement!r}")


def test_vigee_le_brun_nationality_french():
    """vigee_le_brun nationality must be French."""
    s = get_style("vigee_le_brun")
    assert "french" in s.nationality.lower(), (
        f"vigee_le_brun nationality should be French; got: {s.nationality!r}")


def test_vigee_le_brun_palette_length():
    """vigee_le_brun palette must have at least 6 entries."""
    s = get_style("vigee_le_brun")
    assert len(s.palette) >= 6, (
        f"vigee_le_brun palette has only {len(s.palette)} entries; expected >= 6")


def test_vigee_le_brun_palette_values_in_range():
    """All vigee_le_brun palette RGB values must be in [0, 1]."""
    s = get_style("vigee_le_brun")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"Out-of-range channel {ch} in vigee_le_brun palette {rgb}")


def test_vigee_le_brun_high_wet_blend():
    """vigee_le_brun wet_blend should be high (>= 0.80) — near-seamless skin blending."""
    s = get_style("vigee_le_brun")
    assert s.wet_blend >= 0.80, (
        f"vigee_le_brun wet_blend={s.wet_blend:.2f} should be >= 0.80 — "
        f"her portraits have near-invisible brushwork on the flesh")


def test_vigee_le_brun_has_warm_highlight():
    """vigee_le_brun palette must contain a warm-ivory near-white highlight."""
    s = get_style("vigee_le_brun")
    has_warm_highlight = any(r > 0.88 and g > 0.78 and b > 0.68
                             for r, g, b in s.palette)
    assert has_warm_highlight, (
        "vigee_le_brun palette must contain a warm-ivory highlight tone — "
        "her luminous pearl highlights are a defining characteristic")


def test_vigee_le_brun_inspiration_references_pass():
    """vigee_le_brun inspiration must reference vigee_le_brun_pearlescent_grace_pass()."""
    s = get_style("vigee_le_brun")
    assert "vigee_le_brun_pearlescent_grace_pass()" in s.inspiration, (
        "vigee_le_brun inspiration must reference vigee_le_brun_pearlescent_grace_pass() — "
        "the defining pipeline pass for her pearlescent skin technique")


def test_vigee_le_brun_inspiration_references_subsurface_scatter():
    """vigee_le_brun inspiration must reference subsurface_scatter_pass()."""
    s = get_style("vigee_le_brun")
    assert "subsurface_scatter_pass()" in s.inspiration, (
        "vigee_le_brun inspiration must reference subsurface_scatter_pass() — "
        "the SSS artistic improvement introduced in session 64")


def test_vigee_le_brun_in_expected_artists():
    """EXPECTED_ARTISTS list must include vigee_le_brun."""
    assert "vigee_le_brun" in EXPECTED_ARTISTS, (
        "vigee_le_brun missing from EXPECTED_ARTISTS — add it to the list")


# ──────────────────────────────────────────────────────────────────────────────
# Alma-Tadema — session 65 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_alma_tadema_in_catalog():
    """Alma-Tadema (session 65) must be present in CATALOG."""
    assert "alma_tadema" in CATALOG, (
        "alma_tadema missing from CATALOG — add it to art_catalog.py")


def test_alma_tadema_movement():
    """alma_tadema movement must reference Academicism or Victorian."""
    s = get_style("alma_tadema")
    mv = s.movement.lower()
    assert "academ" in mv or "victorian" in mv or "classical" in mv, (
        f"alma_tadema movement should reference Academicism, Victorian, or Classical; "
        f"got: {s.movement!r}")


def test_alma_tadema_nationality_dutch_british():
    """alma_tadema nationality must reference Dutch or British."""
    s = get_style("alma_tadema")
    nat = s.nationality.lower()
    assert "dutch" in nat or "british" in nat, (
        f"alma_tadema nationality should reference Dutch or British (was Dutch-born, "
        f"naturalised British); got: {s.nationality!r}")


def test_alma_tadema_palette_length():
    """alma_tadema palette must have at least 6 entries."""
    s = get_style("alma_tadema")
    assert len(s.palette) >= 6, (
        f"alma_tadema palette has only {len(s.palette)} entries; expected >= 6")


def test_alma_tadema_palette_values_in_range():
    """alma_tadema palette values must all be in [0.0, 1.0]."""
    s = get_style("alma_tadema")
    for i, color in enumerate(s.palette):
        for j, v in enumerate(color):
            assert 0.0 <= v <= 1.0, (
                f"alma_tadema palette[{i}][{j}]={v:.4f} is out of [0,1]")


def test_alma_tadema_edge_softness_crisp():
    """alma_tadema edge_softness must be <= 0.35 (photographic crispness)."""
    s = get_style("alma_tadema")
    assert s.edge_softness <= 0.35, (
        f"alma_tadema edge_softness={s.edge_softness:.3f} should be <= 0.35 — "
        f"his marble edges are photographically crisp, the defining quality "
        f"that distinguishes his surfaces from Impressionist or sfumato softness")


def test_alma_tadema_high_key_palette():
    """alma_tadema palette average luminance must be > 0.60 (high-key)."""
    s = get_style("alma_tadema")
    avg_lum = sum(
        0.2126 * r + 0.7152 * g + 0.0722 * b
        for r, g, b in s.palette
    ) / len(s.palette)
    assert avg_lum > 0.60, (
        f"alma_tadema palette avg luminance={avg_lum:.3f} should be > 0.60 — "
        f"his paintings are extremely high-key: marble, noon light, pale silk, "
        f"and Mediterranean sky dominate the palette")


def test_alma_tadema_inspiration_references_marble_pass():
    """alma_tadema inspiration must reference alma_tadema_marble_luminance_pass()."""
    s = get_style("alma_tadema")
    assert "alma_tadema_marble_luminance_pass()" in s.inspiration, (
        "alma_tadema inspiration must reference alma_tadema_marble_luminance_pass() — "
        "the defining pipeline pass for his crystalline marble technique")


def test_alma_tadema_inspiration_references_crystalline_pass():
    """alma_tadema inspiration must reference crystalline_surface_pass()."""
    s = get_style("alma_tadema")
    assert "crystalline_surface_pass()" in s.inspiration, (
        "alma_tadema inspiration must reference crystalline_surface_pass() — "
        "the session 65 artistic improvement inspired by his glass-like precision")


def test_alma_tadema_in_expected_artists():
    """EXPECTED_ARTISTS list must include alma_tadema."""
    assert "alma_tadema" in EXPECTED_ARTISTS, (
        "alma_tadema missing from EXPECTED_ARTISTS — add it to the list")

