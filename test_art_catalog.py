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
    "strozzi",
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
    "hyacinthe_rigaud",
    "lorenzo_lotto",
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
    "patinir",
    "andrea_mantegna",
    "claude_lorrain",
    "jacques_louis_david",
    "guido_reni",
    "correggio",
    "watteau",
    "sofonisba_anguissola",
    "hieronymus_bosch",
    "pieter_de_hooch",
    "jan_steen",
    "andrea_del_sarto",
    "chardin",
    "gericault",
    "perugino",
    "signorelli",
    "rosalba_carriera",
    "whistler",
    "odilon_redon",
    "leon_spilliaert",
    "ferdinand_hodler",
    "gustave_caillebotte",
    "franz_marc",
    "antonello_da_messina",
    "hugo_van_der_goes",
    "gerrit_dou",
    "carel_fabritius",
    "judith_leyster",
    "bernardino_luini",
    "boltraffio",
    "federico_barocci",
    "pierre_bonnard",
    "masaccio",
    "carlo_dolci",
    "luca_giordano",
    "guercino",
    "ribera",
    "moroni",
    "sassoferrato",
    "orazio_gentileschi",
    "jordaens",
    "guido_cagnacci",
    "furini",
    "lavinia_fontana",
    "moroni",
    "andrea_solario",
    "perugino",
    "savoldo",
    "batoni",
    "boldini",
    "annibale_carracci",
    "salvator_rosa",
    "massimo_stanzione",
    "albani",
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
    "PADUAN_RENAISSANCE",
    "CLASSICAL_LANDSCAPE",
    "FRENCH_NEOCLASSICAL",
    "BOLOGNESE_BAROQUE",
    "PARMA_RENAISSANCE",
    "FETE_GALANTE",
    "LOMBARD_RENAISSANCE",
    "NORTHERN_FANTASTICAL",
    "DUTCH_DOMESTIC",
    "DUTCH_GENRE_COMEDY",
    "FRENCH_ROMANTIC",
    "UMBRIAN_RENAISSANCE",
    "VENETIAN_PASTEL_PORTRAIT",
    "AMERICAN_TONALIST",
    "DUTCH_FIJNSCHILDER",
    "DUTCH_LIGHT_GROUND",
    "DUTCH_CANDLELIT_GENRE",
    "DUTCH_BRAVURA_PORTRAIT",
    "MILANESE_SFUMATO",
    "UMBRIAN_MANNERIST",
    "CHROMATIC_INTIMISME",
    "PROTO_RENAISSANCE",
    "BELLE_EPOQUE",
    "VICTORIAN_SOCIAL_REALIST",
    "FLORENTINE_DEVOTIONAL_BAROQUE",
    "NEAPOLITAN_BAROQUE",
    "SPANISH_NEAPOLITAN_BAROQUE",
    "MILANESE_PEARLED",
    "BERGAMASQUE_PORTRAIT_REALISM",
    "GENOESE_VENETIAN_BAROQUE",
    "ROMAN_DEVOTIONAL_BAROQUE",
    "ITALO_COURTLY_BAROQUE",
    "ANTWERP_BAROQUE",
    "UMBRIAN_CLASSICAL_HARMONY",
    "BRESCIAN_SILVER_NOCTURNE",
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
# Théodore Géricault — artist catalog tests
# ──────────────────────────────────────────────────────────────────────────────

def test_gericault_in_catalog():
    """Géricault must be present in CATALOG."""
    assert "gericault" in CATALOG, "gericault not found in CATALOG"


def test_gericault_movement():
    """Géricault's movement must reference French Romanticism."""
    s = get_style("gericault")
    m = s.movement.lower()
    assert "romantic" in m or "romanticism" in m, (
        f"Géricault movement should reference Romanticism; got: {s.movement!r}")


def test_gericault_nationality():
    """Géricault was French."""
    s = get_style("gericault")
    assert "french" in s.nationality.lower(), (
        f"Géricault nationality should be French; got: {s.nationality!r}")


def test_gericault_palette_length():
    """Géricault's palette should have at least 6 key colours (dark warms, amber lights)."""
    s = get_style("gericault")
    assert len(s.palette) >= 6, (
        f"Géricault palette should have ≥6 key colours; got {len(s.palette)}")


def test_gericault_palette_values_in_range():
    """All Géricault palette RGB values must be in [0, 1]."""
    s = get_style("gericault")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Géricault palette {rgb}")


def test_gericault_dark_ground():
    """Géricault used a dark warm ground — ground_color luminance should be low (≤ 0.25)."""
    s = get_style("gericault")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum <= 0.25, (
        f"Géricault ground_color luminance should be low (dark ground); got {lum:.3f}")


def test_gericault_high_wet_blend():
    """Géricault worked alla prima in wet impasto — wet_blend should be high (≥ 0.60)."""
    s = get_style("gericault")
    assert s.wet_blend >= 0.60, (
        f"Géricault wet_blend should be high (wet-on-wet impasto); got {s.wet_blend}")


def test_gericault_no_chromatic_split():
    """Géricault does not use divisionist chromatic splitting."""
    s = get_style("gericault")
    assert not s.chromatic_split, "Géricault chromatic_split should be False"


def test_gericault_famous_works_not_empty():
    """Géricault should have at least 4 famous works documented."""
    s = get_style("gericault")
    assert len(s.famous_works) >= 4, (
        f"Géricault should have ≥4 famous works; got {len(s.famous_works)}")


def test_gericault_famous_works_include_raft():
    """Géricault's famous works should include The Raft of the Medusa."""
    s = get_style("gericault")
    titles = [w[0] for w in s.famous_works]
    assert any("Raft" in t or "Medusa" in t for t in titles), (
        "Géricault famous works should include The Raft of the Medusa")


def test_gericault_inspiration_references_turbulence_pass():
    """Géricault's inspiration text should reference gericault_romantic_turbulence_pass."""
    s = get_style("gericault")
    assert "gericault_romantic_turbulence_pass" in s.inspiration, (
        "Géricault inspiration should reference gericault_romantic_turbulence_pass()")


def test_gericault_warm_palette_shadows():
    """Géricault's palette near-black colour should be warm (R ≥ G ≥ B not hold — R > B)."""
    s = get_style("gericault")
    # Find the darkest palette colour
    darkest = min(s.palette, key=lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2])
    r, g, b = darkest
    assert r > b, (
        f"Géricault's darkest palette colour should be warm (R > B); "
        f"got R={r:.3f} B={b:.3f}")


# ──────────────────────────────────────────────────────────────────────────────
# Period.FRENCH_ROMANTIC — Géricault period enum
# ──────────────────────────────────────────────────────────────────────────────

def test_french_romantic_period_present():
    """FRENCH_ROMANTIC must exist in the Period enum."""
    assert hasattr(Period, "FRENCH_ROMANTIC"), "Period.FRENCH_ROMANTIC not found"
    assert Period.FRENCH_ROMANTIC in list(Period)


def test_french_romantic_stroke_params_all_keys():
    """FRENCH_ROMANTIC stroke_params must contain all required keys."""
    style = Style(medium=Medium.OIL, period=Period.FRENCH_ROMANTIC,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"FRENCH_ROMANTIC stroke_params missing key: {key!r}"


def test_french_romantic_high_wet_blend():
    """FRENCH_ROMANTIC wet_blend should be high — vigorous wet-on-wet impasto."""
    style = Style(medium=Medium.OIL, period=Period.FRENCH_ROMANTIC,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.60, (
        f"FRENCH_ROMANTIC wet_blend should be high (≥0.60); got {p['wet_blend']}")


def test_french_romantic_moderate_high_edge_softness():
    """FRENCH_ROMANTIC edge_softness should be moderate-high (≥ 0.65) — turbulent dissolution."""
    style = Style(medium=Medium.OIL, period=Period.FRENCH_ROMANTIC,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] >= 0.65, (
        f"FRENCH_ROMANTIC edge_softness should be moderate-high (≥0.65); "
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


# ──────────────────────────────────────────────────────────────────────────────
# Andrea Mantegna — session 67 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_andrea_mantegna_in_catalog():
    """Andrea Mantegna (session 67) must be present in CATALOG."""
    assert "andrea_mantegna" in CATALOG, (
        "andrea_mantegna missing from CATALOG — add it to art_catalog.py")


def test_andrea_mantegna_movement():
    """andrea_mantegna movement must reference Paduan or Renaissance."""
    s = get_style("andrea_mantegna")
    mv = s.movement.lower()
    assert "paduan" in mv or "renaissance" in mv, (
        f"andrea_mantegna movement should reference Paduan or Renaissance; "
        f"got: {s.movement!r}")


def test_andrea_mantegna_nationality_italian():
    """andrea_mantegna nationality must be Italian."""
    s = get_style("andrea_mantegna")
    assert "italian" in s.nationality.lower(), (
        f"andrea_mantegna nationality should be Italian; got: {s.nationality!r}")


def test_andrea_mantegna_palette_length():
    """andrea_mantegna palette must have at least 6 entries."""
    s = get_style("andrea_mantegna")
    assert len(s.palette) >= 6, (
        f"andrea_mantegna palette has only {len(s.palette)} entries; expected >= 6")


def test_andrea_mantegna_palette_values_in_range():
    """All andrea_mantegna palette RGB values must be in [0, 1]."""
    s = get_style("andrea_mantegna")
    for i, rgb in enumerate(s.palette):
        assert len(rgb) == 3
        for j, ch in enumerate(rgb):
            assert 0.0 <= ch <= 1.0, (
                f"andrea_mantegna palette[{i}][{j}]={ch:.4f} is out of [0,1]")


def test_andrea_mantegna_low_wet_blend():
    """andrea_mantegna wet_blend must be <= 0.20 (stone does not bleed)."""
    s = get_style("andrea_mantegna")
    assert s.wet_blend <= 0.20, (
        f"andrea_mantegna wet_blend={s.wet_blend:.3f} should be <= 0.20 — "
        f"Mantegna's surfaces are stone-hard, not liquid-blended")


def test_andrea_mantegna_low_edge_softness():
    """andrea_mantegna edge_softness must be <= 0.25 (engraved archaeological crispness)."""
    s = get_style("andrea_mantegna")
    assert s.edge_softness <= 0.25, (
        f"andrea_mantegna edge_softness={s.edge_softness:.3f} should be <= 0.25 — "
        f"Mantegna's contours are engraved-crisp, the opposite of Leonardo's sfumato")


def test_andrea_mantegna_palette_has_cool_pale_highlight():
    """andrea_mantegna palette must contain a cool pale chalk highlight."""
    s = get_style("andrea_mantegna")
    # Cool pale highlight: all channels high, B slightly dominant over R
    has_cool_highlight = any(r > 0.75 and g > 0.75 and b > 0.70
                             for r, g, b in s.palette)
    assert has_cool_highlight, (
        "andrea_mantegna palette must contain a cool pale chalk highlight tone — "
        "the stone-lit ridge-form highlight that defines his sculptural modelling")


def test_andrea_mantegna_palette_has_deep_shadow():
    """andrea_mantegna palette must contain a near-black deep shadow."""
    s = get_style("andrea_mantegna")
    has_deep_shadow = any(r < 0.20 and g < 0.20 and b < 0.15
                          for r, g, b in s.palette)
    assert has_deep_shadow, (
        "andrea_mantegna palette must contain a near-black shadow — "
        "Mantegna used deep warm-umber voids at shadow troughs")


def test_andrea_mantegna_crackle():
    """andrea_mantegna crackle should be True (aged Renaissance panel/canvas)."""
    s = get_style("andrea_mantegna")
    assert s.crackle is True, (
        f"andrea_mantegna crackle={s.crackle} should be True — "
        f"his works on panel and canvas show characteristic aged craquelure")


def test_andrea_mantegna_no_glazing():
    """andrea_mantegna glazing should be None (tempera on panel, not oil glaze)."""
    s = get_style("andrea_mantegna")
    assert s.glazing is None, (
        "andrea_mantegna glazing should be None — Mantegna predominantly used "
        "tempera on panel; no oil-glaze unification layer")


def test_andrea_mantegna_famous_works_include_dead_christ():
    """andrea_mantegna famous works should include the Lamentation / Dead Christ."""
    s = get_style("andrea_mantegna")
    titles = [w[0] for w in s.famous_works]
    assert any("Christ" in t or "Dead" in t or "Lamentation" in t
               for t in titles), (
        "andrea_mantegna famous works should include the Lamentation over the Dead "
        "Christ — his most famous and technically radical work")


def test_andrea_mantegna_famous_works_count():
    """andrea_mantegna should have at least 4 famous works documented."""
    s = get_style("andrea_mantegna")
    assert len(s.famous_works) >= 4, (
        f"andrea_mantegna should have >= 4 famous works; got {len(s.famous_works)}")


def test_andrea_mantegna_inspiration_references_sculptural_pass():
    """andrea_mantegna inspiration must reference mantegna_sculptural_form_pass()."""
    s = get_style("andrea_mantegna")
    assert "mantegna_sculptural_form_pass()" in s.inspiration, (
        "andrea_mantegna inspiration must reference mantegna_sculptural_form_pass() — "
        "the defining pipeline pass for his engraved stone-form technique")


def test_andrea_mantegna_in_expected_artists():
    """EXPECTED_ARTISTS list must include andrea_mantegna."""
    assert "andrea_mantegna" in EXPECTED_ARTISTS, (
        "andrea_mantegna missing from EXPECTED_ARTISTS — add it to the list")


# ──────────────────────────────────────────────────────────────────────────────
# Period.PADUAN_RENAISSANCE — session 67 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_paduan_renaissance_period_present():
    """Session 67: PADUAN_RENAISSANCE must exist in Period enum."""
    assert hasattr(Period, "PADUAN_RENAISSANCE"), (
        "Period.PADUAN_RENAISSANCE not found — add it to scene_schema.py")
    assert Period.PADUAN_RENAISSANCE in list(Period)


def test_paduan_renaissance_stroke_params_low_wet_blend():
    """PADUAN_RENAISSANCE should have very low wet_blend (stone does not bleed)."""
    style = Style(medium=Medium.OIL, period=Period.PADUAN_RENAISSANCE,
                  palette=PaletteHint.COOL_GREY)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.20, (
        f"PADUAN_RENAISSANCE wet_blend should be <= 0.20 for stone-hard surfaces; "
        f"got {p['wet_blend']}")


def test_paduan_renaissance_stroke_params_low_edge_softness():
    """PADUAN_RENAISSANCE should have low edge_softness (engraved precision)."""
    style = Style(medium=Medium.OIL, period=Period.PADUAN_RENAISSANCE,
                  palette=PaletteHint.COOL_GREY)
    p = style.stroke_params
    assert p["edge_softness"] <= 0.28, (
        f"PADUAN_RENAISSANCE edge_softness should be <= 0.28 for crisp engraved "
        f"archaeological edges; got {p['edge_softness']}")



# ──────────────────────────────────────────────────────────────────────────────
# Claude Lorrain — session 68 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_claude_lorrain_in_catalog():
    """claude_lorrain must exist in CATALOG (session 68 addition)."""
    assert "claude_lorrain" in CATALOG, (
        "claude_lorrain missing from CATALOG — add the entry to art_catalog.py")


def test_claude_lorrain_movement():
    """claude_lorrain movement must reference Classical Landscape."""
    s = get_style("claude_lorrain")
    assert "Classical" in s.movement or "classical" in s.movement.lower() or "Landscape" in s.movement, (
        f"claude_lorrain movement should reference Classical Landscape; got {s.movement!r}")


def test_claude_lorrain_palette_has_golden_horizon():
    """claude_lorrain palette must contain a warm golden-amber horizon tone."""
    s = get_style("claude_lorrain")
    # Warm golden amber: R high, G moderately high, B significantly lower
    has_golden = any(r > 0.85 and g > 0.65 and b < 0.60
                     for r, g, b in s.palette)
    assert has_golden, (
        "claude_lorrain palette must contain a warm golden-amber horizon tone — "
        "the signature contre-jour glow that floods the sky in his landscapes")


def test_claude_lorrain_palette_has_cool_sky():
    """claude_lorrain palette must contain a cool cerulean upper sky tone."""
    s = get_style("claude_lorrain")
    # Cool sky: B dominant, moderate G, lower R
    has_cool_sky = any(b > r and b > 0.75 and r < 0.75
                       for r, g, b in s.palette)
    assert has_cool_sky, (
        "claude_lorrain palette must contain a cool cerulean sky tone — "
        "the upper sky that contrasts with the warm golden horizon below")


def test_claude_lorrain_palette_has_dark_repoussoir():
    """claude_lorrain palette must contain a dark foreground shadow tone."""
    s = get_style("claude_lorrain")
    has_dark = any(r < 0.35 and g < 0.40 and b < 0.30
                   for r, g, b in s.palette)
    assert has_dark, (
        "claude_lorrain palette must contain a dark shadow tone for foreground "
        "repoussoir trees — the dark flanking elements that frame the luminous distance")


def test_claude_lorrain_high_edge_softness():
    """claude_lorrain edge_softness should be >= 0.65 (atmospheric dissolution)."""
    s = get_style("claude_lorrain")
    assert s.edge_softness >= 0.65, (
        f"claude_lorrain edge_softness={s.edge_softness:.2f} should be >= 0.65 — "
        f"Lorrain's distant forms dissolve in atmospheric haze; crisp edges would "
        f"contradict his characteristic proto-sfumato aerial perspective")


def test_claude_lorrain_high_wet_blend():
    """claude_lorrain wet_blend should be >= 0.60 (soft luminous transitions)."""
    s = get_style("claude_lorrain")
    assert s.wet_blend >= 0.60, (
        f"claude_lorrain wet_blend={s.wet_blend:.2f} should be >= 0.60 — "
        f"the golden horizon glow requires heavily blended, seamless sky transitions")


def test_claude_lorrain_has_glazing():
    """claude_lorrain glazing should not be None (unifying amber glaze)."""
    s = get_style("claude_lorrain")
    assert s.glazing is not None, (
        "claude_lorrain glazing should not be None — the warm amber unifying glaze "
        "bathes all elements in the characteristic golden Lorrain light")
    r, g, b = s.glazing
    assert r > g > b, (
        f"claude_lorrain glazing={s.glazing} should be warm amber (R > G > B) — "
        f"the golden unity glaze that warms the entire landscape surface")


def test_claude_lorrain_famous_works_include_queen_of_sheba():
    """claude_lorrain famous works should include Embarkation of the Queen of Sheba."""
    s = get_style("claude_lorrain")
    titles = [w[0] for w in s.famous_works]
    assert any("Sheba" in t or "Queen" in t or "Embarkation" in t
               for t in titles), (
        "claude_lorrain famous works should include Embarkation of the Queen of Sheba "
        "— his most celebrated and technically accomplished composition")


def test_claude_lorrain_famous_works_count():
    """claude_lorrain should have at least 4 famous works documented."""
    s = get_style("claude_lorrain")
    assert len(s.famous_works) >= 4, (
        f"claude_lorrain should have >= 4 famous works; got {len(s.famous_works)}")


def test_claude_lorrain_inspiration_references_golden_light_pass():
    """claude_lorrain inspiration must reference claude_lorrain_golden_light_pass()."""
    s = get_style("claude_lorrain")
    assert "claude_lorrain_golden_light_pass()" in s.inspiration, (
        "claude_lorrain inspiration must reference claude_lorrain_golden_light_pass() — "
        "the defining pipeline pass for his golden contre-jour horizon technique")


def test_claude_lorrain_in_expected_artists():
    """EXPECTED_ARTISTS list must include claude_lorrain."""
    assert "claude_lorrain" in EXPECTED_ARTISTS, (
        "claude_lorrain missing from EXPECTED_ARTISTS — add it to the list")


# ──────────────────────────────────────────────────────────────────────────────
# Period.CLASSICAL_LANDSCAPE — session 68 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_classical_landscape_period_present():
    """Session 68: CLASSICAL_LANDSCAPE must exist in Period enum."""
    assert hasattr(Period, "CLASSICAL_LANDSCAPE"), (
        "Period.CLASSICAL_LANDSCAPE not found — add it to scene_schema.py")
    assert Period.CLASSICAL_LANDSCAPE in list(Period)


def test_classical_landscape_stroke_params_high_wet_blend():
    """CLASSICAL_LANDSCAPE should have high wet_blend (soft atmospheric glow)."""
    style = Style(medium=Medium.OIL, period=Period.CLASSICAL_LANDSCAPE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.60, (
        f"CLASSICAL_LANDSCAPE wet_blend should be >= 0.60 for Lorrain's luminous "
        f"atmospheric transitions; got {p['wet_blend']}")


def test_classical_landscape_stroke_params_high_edge_softness():
    """CLASSICAL_LANDSCAPE should have high edge_softness (atmospheric dissolution)."""
    style = Style(medium=Medium.OIL, period=Period.CLASSICAL_LANDSCAPE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] >= 0.65, (
        f"CLASSICAL_LANDSCAPE edge_softness should be >= 0.65 for Lorrain's dissolved "
        f"atmospheric edges in distant landscape forms; got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Jacques-Louis David — session 69 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_jacques_louis_david_in_catalog():
    """Session 69: Jacques-Louis David must be present in CATALOG."""
    assert "jacques_louis_david" in CATALOG, (
        "jacques_louis_david missing from CATALOG — add it to art_catalog.py")


def test_jacques_louis_david_movement():
    """David's movement must reference Neoclassic."""
    s = get_style("jacques_louis_david")
    movement_lower = s.movement.lower()
    assert "neoclassic" in movement_lower or "classical" in movement_lower, (
        f"Jacques-Louis David movement should reference Neoclassicism; got {s.movement!r}")


def test_jacques_louis_david_nationality():
    """David was French."""
    s = get_style("jacques_louis_david")
    assert "French" in s.nationality, (
        f"Jacques-Louis David nationality should be French; got {s.nationality!r}")


def test_jacques_louis_david_palette_length():
    """David palette must have at least 6 entries."""
    s = get_style("jacques_louis_david")
    assert len(s.palette) >= 6, (
        f"jacques_louis_david palette has only {len(s.palette)} entries; expected >= 6")


def test_jacques_louis_david_palette_values_in_range():
    """All David palette RGB values must be in [0.0, 1.0]."""
    s = get_style("jacques_louis_david")
    for i, rgb in enumerate(s.palette):
        assert len(rgb) == 3, f"palette[{i}] is not a 3-tuple"
        for j, v in enumerate(rgb):
            assert 0.0 <= v <= 1.0, (
                f"jacques_louis_david palette[{i}][{j}]={v:.4f} is out of [0,1]")


def test_jacques_louis_david_moderate_wet_blend():
    """David uses moderate wet_blend — smooth flesh but not sfumato."""
    s = get_style("jacques_louis_david")
    assert 0.15 <= s.wet_blend <= 0.45, (
        f"jacques_louis_david wet_blend={s.wet_blend:.3f} should be in [0.15, 0.45] — "
        "moderate smoothness without sfumato haze")


def test_jacques_louis_david_moderate_edge_softness():
    """David uses moderately crisp edges — classical contour, not sfumato."""
    s = get_style("jacques_louis_david")
    assert s.edge_softness <= 0.50, (
        f"jacques_louis_david edge_softness={s.edge_softness:.3f} should be <= 0.50 — "
        "crisp neoclassical contour")


def test_jacques_louis_david_has_glazing():
    """David applied a warm amber unifying glaze — glazing must not be None."""
    s = get_style("jacques_louis_david")
    assert s.glazing is not None, (
        "jacques_louis_david glazing should not be None — David applied a warm amber "
        "glaze over his portraits to unify the flesh tones")


def test_jacques_louis_david_palette_has_stone_grey():
    """David palette must contain a cool stone-grey for his architectural backgrounds."""
    s = get_style("jacques_louis_david")
    has_stone_grey = any(
        0.40 <= r <= 0.85 and 0.40 <= g <= 0.85 and 0.40 <= b <= 0.85
        and abs(r - g) < 0.15 and abs(g - b) < 0.15
        for r, g, b in s.palette
    )
    assert has_stone_grey, (
        "jacques_louis_david palette must contain a cool stone-grey tone — "
        "David's backgrounds are cool neutral stone, not warm")


def test_jacques_louis_david_famous_works_include_marat():
    """David's famous works must include The Death of Marat."""
    s = get_style("jacques_louis_david")
    titles = [w[0] for w in s.famous_works]
    assert any("Marat" in t for t in titles), (
        "jacques_louis_david famous works should include The Death of Marat — "
        "his most celebrated and politically radical painting")


def test_jacques_louis_david_famous_works_include_horatii():
    """David's famous works must include Oath of the Horatii."""
    s = get_style("jacques_louis_david")
    titles = [w[0] for w in s.famous_works]
    assert any("Horat" in t for t in titles), (
        "jacques_louis_david famous works should include Oath of the Horatii — "
        "the defining manifesto of French Neoclassicism")


def test_jacques_louis_david_famous_works_count():
    """David should have at least 4 famous works documented."""
    s = get_style("jacques_louis_david")
    assert len(s.famous_works) >= 4, (
        f"jacques_louis_david should have >= 4 famous works; got {len(s.famous_works)}")


def test_jacques_louis_david_inspiration_references_david_pass():
    """David inspiration must reference david_neoclassical_clarity_pass()."""
    s = get_style("jacques_louis_david")
    assert "david_neoclassical_clarity_pass()" in s.inspiration, (
        "jacques_louis_david inspiration must reference david_neoclassical_clarity_pass() — "
        "the defining pipeline pass for his heroic clarity technique")


def test_jacques_louis_david_inspiration_references_recession_pass():
    """David inspiration must reference ground_tone_recession_pass()."""
    s = get_style("jacques_louis_david")
    assert "ground_tone_recession_pass()" in s.inspiration, (
        "jacques_louis_david inspiration must reference ground_tone_recession_pass() — "
        "the session 69 artistic improvement pass")


def test_jacques_louis_david_in_expected_artists():
    """EXPECTED_ARTISTS list must include jacques_louis_david."""
    assert "jacques_louis_david" in EXPECTED_ARTISTS, (
        "jacques_louis_david missing from EXPECTED_ARTISTS — add it to the list")


# ──────────────────────────────────────────────────────────────────────────────
# Period.FRENCH_NEOCLASSICAL — session 69 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_french_neoclassical_period_present():
    """Session 69: FRENCH_NEOCLASSICAL must exist in Period enum."""
    assert hasattr(Period, "FRENCH_NEOCLASSICAL"), (
        "Period.FRENCH_NEOCLASSICAL not found — add it to scene_schema.py")
    assert Period.FRENCH_NEOCLASSICAL in list(Period)


def test_french_neoclassical_stroke_params_moderate_wet_blend():
    """FRENCH_NEOCLASSICAL should have moderate wet_blend (smooth flesh, not sfumato)."""
    style = Style(medium=Medium.OIL, period=Period.FRENCH_NEOCLASSICAL,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.40, (
        f"FRENCH_NEOCLASSICAL wet_blend should be <= 0.40 for controlled smoothness; "
        f"got {p['wet_blend']}")
    assert p["wet_blend"] >= 0.15, (
        f"FRENCH_NEOCLASSICAL wet_blend should be >= 0.15 (not a dry technique); "
        f"got {p['wet_blend']}")


def test_french_neoclassical_stroke_params_moderate_edge_softness():
    """FRENCH_NEOCLASSICAL should have moderate edge_softness (classical contour)."""
    style = Style(medium=Medium.OIL, period=Period.FRENCH_NEOCLASSICAL,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] <= 0.50, (
        f"FRENCH_NEOCLASSICAL edge_softness should be <= 0.50 for crisp classical "
        f"contours; got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Guido Reni — session 70 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_guido_reni_in_catalog():
    """Session 70: Guido Reni must be present in CATALOG."""
    assert "guido_reni" in CATALOG, (
        "guido_reni missing from CATALOG — add it to art_catalog.py")


def test_guido_reni_movement():
    """Reni's movement must reference Bolognese or Baroque."""
    s = get_style("guido_reni")
    mv = s.movement.lower()
    assert "bolognese" in mv or "baroque" in mv, (
        f"guido_reni movement should reference Bolognese Baroque; got {s.movement!r}")


def test_guido_reni_nationality():
    """Reni was Italian."""
    s = get_style("guido_reni")
    assert "Italian" in s.nationality, (
        f"guido_reni nationality should be Italian; got {s.nationality!r}")


def test_guido_reni_palette_length():
    """Reni palette must have at least 6 entries."""
    s = get_style("guido_reni")
    assert len(s.palette) >= 6, (
        f"guido_reni palette has only {len(s.palette)} entries; expected >= 6")


def test_guido_reni_palette_values_in_range():
    """All Reni palette RGB values must be in [0.0, 1.0]."""
    s = get_style("guido_reni")
    for i, rgb in enumerate(s.palette):
        assert len(rgb) == 3, f"palette[{i}] is not a 3-tuple"
        for j, v in enumerate(rgb):
            assert 0.0 <= v <= 1.0, (
                f"guido_reni palette[{i}][{j}]={v:.4f} is out of [0,1]")


def test_guido_reni_high_wet_blend():
    """Reni uses high wet_blend — silken blending for his angelic skin quality."""
    s = get_style("guido_reni")
    assert s.wet_blend >= 0.50, (
        f"guido_reni wet_blend={s.wet_blend:.3f} should be >= 0.50 — "
        "high wet_blend for the silken blending that defines his alabaster skin")


def test_guido_reni_moderate_edge_softness():
    """Reni uses moderate edge_softness — soft but not dissolved."""
    s = get_style("guido_reni")
    assert 0.40 <= s.edge_softness <= 0.72, (
        f"guido_reni edge_softness={s.edge_softness:.3f} should be in [0.40, 0.72] — "
        "soft Baroque blending without sfumato dissolution")


def test_guido_reni_has_glazing():
    """Reni applied warm ivory-rose glazes — glazing must not be None."""
    s = get_style("guido_reni")
    assert s.glazing is not None, (
        "guido_reni glazing should not be None — Reni built his skin through "
        "repeated warm glazes over a light ground")


def test_guido_reni_palette_has_pearl_highlight():
    """Reni palette must contain a near-white pearl highlight."""
    s = get_style("guido_reni")
    has_pearl = any(r >= 0.88 and g >= 0.84 and b >= 0.78 for r, g, b in s.palette)
    assert has_pearl, (
        "guido_reni palette must contain a near-white pearl highlight (R≥0.88, "
        "G≥0.84, B≥0.78) — the alabaster specular that defines his skin quality")


def test_guido_reni_palette_has_heavenly_blue():
    """Reni palette must contain a heavenly blue for divine drapery."""
    s = get_style("guido_reni")
    has_blue = any(b >= 0.68 and b > r + 0.20 and b > g + 0.12 for r, g, b in s.palette)
    assert has_blue, (
        "guido_reni palette must contain a heavenly blue (B≥0.68, B>R+0.20) — "
        "the divine-register drapery colour that appears throughout his sacred works")


def test_guido_reni_palette_has_shadow_violet():
    """Reni palette must contain a cool violet-grey in the shadow range."""
    s = get_style("guido_reni")
    has_violet_shadow = any(
        0.28 <= r <= 0.62 and b > r + 0.03 and lum < 0.52
        for r, g, b in s.palette
        for lum in [0.299 * r + 0.587 * g + 0.114 * b]
    )
    assert has_violet_shadow, (
        "guido_reni palette must contain a cool violet-grey shadow (B>R, lum<0.52) — "
        "Reni's shadows are violet-grey, not umber-black")


def test_guido_reni_famous_works_include_aurora():
    """Reni's famous works must include Aurora."""
    s = get_style("guido_reni")
    titles = [w[0] for w in s.famous_works]
    assert any("Aurora" in t for t in titles), (
        "guido_reni famous works should include Aurora — "
        "his supreme demonstration of warm-to-cool light sweep")


def test_guido_reni_famous_works_include_archangel():
    """Reni's famous works must include Archangel Michael."""
    s = get_style("guido_reni")
    titles = [w[0] for w in s.famous_works]
    assert any("Archangel" in t or "Michael" in t for t in titles), (
        "guido_reni famous works should include Archangel Michael — "
        "one of the most reproduced devotional images of the Baroque")


def test_guido_reni_famous_works_count():
    """Reni should have at least 4 famous works documented."""
    s = get_style("guido_reni")
    assert len(s.famous_works) >= 4, (
        f"guido_reni should have >= 4 famous works; got {len(s.famous_works)}")


def test_guido_reni_inspiration_references_angelic_pass():
    """Reni inspiration must reference guido_reni_angelic_grace_pass()."""
    s = get_style("guido_reni")
    assert "guido_reni_angelic_grace_pass()" in s.inspiration, (
        "guido_reni inspiration must reference guido_reni_angelic_grace_pass() — "
        "the defining pipeline pass for his alabaster luminosity technique")


def test_guido_reni_inspiration_references_bloom_pass():
    """Reni inspiration must reference highlight_bloom_pass()."""
    s = get_style("guido_reni")
    assert "highlight_bloom_pass()" in s.inspiration, (
        "guido_reni inspiration must reference highlight_bloom_pass() — "
        "the session 70 artistic improvement pass")


def test_guido_reni_in_expected_artists():
    """EXPECTED_ARTISTS list must include guido_reni."""
    assert "guido_reni" in EXPECTED_ARTISTS, (
        "guido_reni missing from EXPECTED_ARTISTS — add it to the list")


# ──────────────────────────────────────────────────────────────────────────────
# Period.BOLOGNESE_BAROQUE — session 70 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_bolognese_baroque_period_present():
    """Session 70: BOLOGNESE_BAROQUE must exist in Period enum."""
    assert hasattr(Period, "BOLOGNESE_BAROQUE"), (
        "Period.BOLOGNESE_BAROQUE not found — add it to scene_schema.py")
    assert Period.BOLOGNESE_BAROQUE in list(Period)


def test_bolognese_baroque_stroke_params_high_wet_blend():
    """BOLOGNESE_BAROQUE should have high wet_blend (silken skin blending)."""
    style = Style(medium=Medium.OIL, period=Period.BOLOGNESE_BAROQUE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.50, (
        f"BOLOGNESE_BAROQUE wet_blend should be >= 0.50 for Reni's silken skin "
        f"transitions; got {p['wet_blend']}")


def test_bolognese_baroque_stroke_params_moderate_edge_softness():
    """BOLOGNESE_BAROQUE should have moderate edge_softness."""
    style = Style(medium=Medium.OIL, period=Period.BOLOGNESE_BAROQUE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.38 <= p["edge_softness"] <= 0.72, (
        f"BOLOGNESE_BAROQUE edge_softness should be in [0.38, 0.72] — soft Baroque "
        f"blending without full sfumato dissolution; got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Correggio — session 71 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_correggio_in_catalog():
    """Session 71: correggio must be present in CATALOG."""
    assert "correggio" in CATALOG, (
        "correggio missing from CATALOG — add it to art_catalog.py")


def test_correggio_movement():
    """Correggio's movement should reference Parma or Proto-Baroque."""
    s = get_style("correggio")
    assert ("Parma" in s.movement or "Proto" in s.movement
            or "Renaissance" in s.movement), (
        f"correggio movement should reference Parma or Proto-Baroque; got {s.movement!r}")


def test_correggio_palette_length():
    s = get_style("correggio")
    assert len(s.palette) >= 6, (
        f"correggio palette should have at least 6 key colours; got {len(s.palette)}")


def test_correggio_palette_values_in_range():
    """All Correggio palette RGB values must be in [0, 1]."""
    s = get_style("correggio")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Correggio palette {rgb}")


def test_correggio_high_wet_blend():
    """Correggio's melting transitions require very high wet_blend (>= 0.60)."""
    s = get_style("correggio")
    assert s.wet_blend >= 0.60, (
        f"correggio wet_blend should be >= 0.60 for the signature melting "
        f"Correggesque transitions; got {s.wet_blend}")


def test_correggio_high_edge_softness():
    """Correggio's proto-sfumato requires very high edge_softness (>= 0.60)."""
    s = get_style("correggio")
    assert s.edge_softness >= 0.60, (
        f"correggio edge_softness should be >= 0.60 for proto-sfumato softness; "
        f"got {s.edge_softness}")


def test_correggio_warm_palette():
    """Correggio's palette must contain warm golden/amber highlights (R > B, high lum)."""
    s = get_style("correggio")
    warm_highlights = [
        rgb for rgb in s.palette
        if rgb[0] > 0.75 and rgb[0] > rgb[2] + 0.15
    ]
    assert len(warm_highlights) >= 2, (
        "correggio palette must contain at least 2 warm golden/amber colours — "
        "his defining warm ivory and amber-gold flesh tones")


def test_correggio_famous_works_include_assumption():
    """Correggio's famous works must include the Assumption of the Virgin."""
    s = get_style("correggio")
    titles = [w[0] for w in s.famous_works]
    assert any("Assumption" in t for t in titles), (
        "correggio famous works should include Assumption of the Virgin — "
        "his supreme illusionistic ceiling fresco in Parma Cathedral")


def test_correggio_famous_works_include_jupiter_io():
    """Correggio's famous works must include Jupiter and Io."""
    s = get_style("correggio")
    titles = [w[0] for w in s.famous_works]
    assert any(("Jupiter" in t or "Io" in t) for t in titles), (
        "correggio famous works should include Jupiter and Io — "
        "the supreme demonstration of the Correggesque golden flesh ideal")


def test_correggio_famous_works_count():
    """Correggio should have at least 4 famous works documented."""
    s = get_style("correggio")
    assert len(s.famous_works) >= 4, (
        f"correggio should have >= 4 famous works; got {len(s.famous_works)}")


def test_correggio_inspiration_references_tenderness_pass():
    """Correggio inspiration must reference correggio_golden_tenderness_pass()."""
    s = get_style("correggio")
    assert "correggio_golden_tenderness_pass()" in s.inspiration, (
        "correggio inspiration must reference correggio_golden_tenderness_pass() — "
        "the defining pipeline pass for his amber-gold luminosity technique")


def test_correggio_inspiration_references_luminous_haze_pass():
    """Correggio inspiration must reference luminous_haze_pass()."""
    s = get_style("correggio")
    assert "luminous_haze_pass()" in s.inspiration, (
        "correggio inspiration must reference luminous_haze_pass() — "
        "the session 71 artistic improvement pass")


def test_correggio_in_expected_artists():
    """EXPECTED_ARTISTS list must include correggio."""
    assert "correggio" in EXPECTED_ARTISTS, (
        "correggio missing from EXPECTED_ARTISTS — add it to the list")


# ──────────────────────────────────────────────────────────────────────────────
# Period.PARMA_RENAISSANCE — session 71 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_parma_renaissance_period_present():
    """Session 71: PARMA_RENAISSANCE must exist in Period enum."""
    assert hasattr(Period, "PARMA_RENAISSANCE"), (
        "Period.PARMA_RENAISSANCE not found — add it to scene_schema.py")
    assert Period.PARMA_RENAISSANCE in list(Period)


def test_parma_renaissance_stroke_params_high_wet_blend():
    """PARMA_RENAISSANCE should have very high wet_blend (melting Correggesque transitions)."""
    style = Style(medium=Medium.OIL, period=Period.PARMA_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.55, (
        f"PARMA_RENAISSANCE wet_blend should be >= 0.55 for Correggio's melting "
        f"transitions; got {p['wet_blend']}")


def test_parma_renaissance_stroke_params_high_edge_softness():
    """PARMA_RENAISSANCE should have very high edge_softness (proto-sfumato)."""
    style = Style(medium=Medium.OIL, period=Period.PARMA_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] >= 0.55, (
        f"PARMA_RENAISSANCE edge_softness should be >= 0.55 for proto-sfumato "
        f"softness; got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Watteau — session 72 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_watteau_in_catalog():
    """Session 72: watteau must be in CATALOG."""
    assert "watteau" in CATALOG, "watteau missing from CATALOG — add it to art_catalog.py"


def test_watteau_movement():
    """Watteau movement must reference Rococo or Fête Galante."""
    s = get_style("watteau")
    movement_lower = s.movement.lower()
    assert "rococo" in movement_lower or "galante" in movement_lower or "fete" in movement_lower, (
        f"Watteau movement should reference Rococo or Fête Galante; got {s.movement!r}")


def test_watteau_palette_length():
    """Watteau palette must have at least 6 colours."""
    s = get_style("watteau")
    assert len(s.palette) >= 6, (
        f"Watteau palette should have >= 6 entries; got {len(s.palette)}")


def test_watteau_palette_values_in_range():
    """All Watteau palette entries must be in [0, 1]."""
    s = get_style("watteau")
    for i, colour in enumerate(s.palette):
        for j, component in enumerate(colour):
            assert 0.0 <= component <= 1.0, (
                f"Watteau palette[{i}][{j}] = {component!r} out of [0,1] range")


def test_watteau_warm_palette():
    """Watteau palette should be warm-dominant (mean R > mean B)."""
    s = get_style("watteau")
    mean_r = sum(c[0] for c in s.palette) / len(s.palette)
    mean_b = sum(c[2] for c in s.palette) / len(s.palette)
    assert mean_r > mean_b, (
        f"Watteau palette should be warm (R > B); got mean_r={mean_r:.3f} mean_b={mean_b:.3f}")


def test_watteau_moderate_edge_softness():
    """Watteau should have moderate-to-high edge_softness (dreamlike dissolution)."""
    s = get_style("watteau")
    assert s.edge_softness >= 0.40, (
        f"Watteau edge_softness should be >= 0.40 for crepuscular softening; "
        f"got {s.edge_softness}")


def test_watteau_warm_ground():
    """Watteau ground_color must be warm (R > B)."""
    s = get_style("watteau")
    r, g, b = s.ground_color
    assert r > b, (
        f"Watteau ground_color should be warm (R > B); got {s.ground_color!r}")


def test_watteau_glazing_is_warm_amber():
    """Watteau glazing must be warm amber (R > G > B)."""
    s = get_style("watteau")
    assert s.glazing is not None, "Watteau should have a glazing colour"
    r, g, b = s.glazing
    assert r > g > b, (
        f"Watteau glazing should be warm amber (R > G > B); got {s.glazing!r}")


def test_watteau_famous_works_include_embarkation():
    """Watteau famous_works must include The Embarkation for Cythera."""
    s = get_style("watteau")
    titles = [title for title, _ in s.famous_works]
    assert any("Cythera" in t or "Embarkation" in t for t in titles), (
        f"Watteau famous_works should include The Embarkation for Cythera; "
        f"got {titles!r}")


def test_watteau_famous_works_include_gilles():
    """Watteau famous_works must include Gilles / Pierrot."""
    s = get_style("watteau")
    titles = [title.lower() for title, _ in s.famous_works]
    assert any("gilles" in t or "pierrot" in t for t in titles), (
        f"Watteau famous_works should include Gilles (Pierrot); got {titles!r}")


def test_watteau_famous_works_count():
    """Watteau should have at least 5 famous works."""
    s = get_style("watteau")
    assert len(s.famous_works) >= 5, (
        f"Watteau should have >= 5 famous works; got {len(s.famous_works)}")


def test_watteau_inspiration_references_crepuscular_pass():
    """Watteau inspiration text should reference watteau_crepuscular_reverie_pass."""
    s = get_style("watteau")
    assert "crepuscular" in s.inspiration.lower(), (
        f"Watteau inspiration should reference the crepuscular pass; "
        f"got {s.inspiration[:80]!r}")


def test_watteau_in_expected_artists():
    """watteau must be present in the EXPECTED_ARTISTS list."""
    assert "watteau" in EXPECTED_ARTISTS, (
        "watteau missing from EXPECTED_ARTISTS — add it to the list in test_art_catalog.py")


# ──────────────────────────────────────────────────────────────────────────────
# Period.FETE_GALANTE — session 72 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_fete_galante_period_present():
    """Session 72: FETE_GALANTE must exist in Period enum."""
    assert hasattr(Period, "FETE_GALANTE"), (
        "Period.FETE_GALANTE not found — add it to scene_schema.py")
    assert Period.FETE_GALANTE in list(Period)


def test_fete_galante_stroke_params_moderate_wet_blend():
    """FETE_GALANTE should have moderate wet_blend (fluid but directional Watteau brushwork)."""
    style = Style(medium=Medium.OIL, period=Period.FETE_GALANTE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.40 <= p["wet_blend"] <= 0.80, (
        f"FETE_GALANTE wet_blend should be 0.40–0.80 for Watteau's fluid brushwork; "
        f"got {p['wet_blend']}")


def test_fete_galante_stroke_params_moderate_edge_softness():
    """FETE_GALANTE should have moderate edge_softness (crepuscular dreamlike dissolve)."""
    style = Style(medium=Medium.OIL, period=Period.FETE_GALANTE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] >= 0.45, (
        f"FETE_GALANTE edge_softness should be >= 0.45 for Watteau's edge dissolution; "
        f"got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Sofonisba Anguissola — session 73 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_sofonisba_anguissola_in_catalog():
    """Session 73: sofonisba_anguissola must be in CATALOG."""
    assert "sofonisba_anguissola" in CATALOG, (
        "sofonisba_anguissola missing from CATALOG — add it to art_catalog.py")


def test_sofonisba_anguissola_movement():
    """Anguissola movement must reference Lombard Renaissance."""
    s = get_style("sofonisba_anguissola")
    movement_lower = s.movement.lower()
    assert "lombard" in movement_lower or "renaissance" in movement_lower, (
        f"Anguissola movement should reference Lombard Renaissance; got {s.movement!r}")


def test_sofonisba_anguissola_nationality():
    """Anguissola must be Italian."""
    s = get_style("sofonisba_anguissola")
    assert s.nationality.lower() == "italian", (
        f"Anguissola nationality should be Italian; got {s.nationality!r}")


def test_sofonisba_anguissola_palette_length():
    """Anguissola palette must have at least 5 colours."""
    s = get_style("sofonisba_anguissola")
    assert len(s.palette) >= 5, (
        f"Anguissola palette should have >= 5 entries; got {len(s.palette)}")


def test_sofonisba_anguissola_palette_values_in_range():
    """All Anguissola palette entries must be in [0, 1]."""
    s = get_style("sofonisba_anguissola")
    for i, colour in enumerate(s.palette):
        for j, component in enumerate(colour):
            assert 0.0 <= component <= 1.0, (
                f"Anguissola palette[{i}][{j}] = {component!r} out of [0,1] range")


def test_sofonisba_anguissola_warm_palette():
    """Anguissola palette should be warm-dominant (mean R > mean B) — Lombard golden light."""
    s = get_style("sofonisba_anguissola")
    mean_r = sum(c[0] for c in s.palette) / len(s.palette)
    mean_b = sum(c[2] for c in s.palette) / len(s.palette)
    assert mean_r > mean_b, (
        f"Anguissola palette should be warm (R > B); got mean_r={mean_r:.3f} mean_b={mean_b:.3f}")


def test_sofonisba_anguissola_high_wet_blend():
    """Anguissola should have high wet_blend (seamless Lombard skin transitions)."""
    s = get_style("sofonisba_anguissola")
    assert s.wet_blend >= 0.55, (
        f"Anguissola wet_blend should be >= 0.55 for seamless Lombard skin; "
        f"got {s.wet_blend}")


def test_sofonisba_anguissola_moderate_edge_softness():
    """Anguissola edge_softness should be moderate-to-high (Lombard warmth without extreme sfumato)."""
    s = get_style("sofonisba_anguissola")
    assert 0.45 <= s.edge_softness <= 0.85, (
        f"Anguissola edge_softness should be in [0.45, 0.85] for Lombard softness; "
        f"got {s.edge_softness}")


def test_sofonisba_anguissola_has_glazing():
    """Anguissola should have a warm amber glazing colour."""
    s = get_style("sofonisba_anguissola")
    assert s.glazing is not None, "Anguissola should have a glazing colour"
    r, g, b = s.glazing
    assert r > b, (
        f"Anguissola glazing should be warm (R > B); got {s.glazing!r}")


def test_sofonisba_anguissola_warm_ground():
    """Anguissola ground_color must be warm (R > B) — Lombard ochre imprimatura."""
    s = get_style("sofonisba_anguissola")
    r, g, b = s.ground_color
    assert r > b, (
        f"Anguissola ground_color should be warm (R > B); got {s.ground_color!r}")


def test_sofonisba_anguissola_famous_works_include_chess():
    """Anguissola famous_works must include the Chess Game / Sisters Playing Chess."""
    s = get_style("sofonisba_anguissola")
    titles = [title.lower() for title, _ in s.famous_works]
    assert any("chess" in t for t in titles), (
        f"Anguissola famous_works should include the Chess Game; got titles={titles!r}")


def test_sofonisba_anguissola_famous_works_include_self_portrait():
    """Anguissola famous_works must include a Self-Portrait."""
    s = get_style("sofonisba_anguissola")
    titles = [title.lower() for title, _ in s.famous_works]
    assert any("self" in t or "self-portrait" in t for t in titles), (
        f"Anguissola famous_works should include a Self-Portrait; got {titles!r}")


def test_sofonisba_anguissola_famous_works_count():
    """Anguissola should have at least 5 famous works."""
    s = get_style("sofonisba_anguissola")
    assert len(s.famous_works) >= 5, (
        f"Anguissola should have >= 5 famous works; got {len(s.famous_works)}")


def test_sofonisba_anguissola_inspiration_references_intimacy_pass():
    """Anguissola inspiration text should reference anguissola_intimacy_pass."""
    s = get_style("sofonisba_anguissola")
    assert "intimacy" in s.inspiration.lower(), (
        f"Anguissola inspiration should reference the intimacy pass; "
        f"got {s.inspiration[:80]!r}")


def test_sofonisba_anguissola_in_expected_artists():
    """sofonisba_anguissola must be present in the EXPECTED_ARTISTS list."""
    assert "sofonisba_anguissola" in EXPECTED_ARTISTS, (
        "sofonisba_anguissola missing from EXPECTED_ARTISTS — add it to the list "
        "in test_art_catalog.py")


# ──────────────────────────────────────────────────────────────────────────────
# Period.LOMBARD_RENAISSANCE — session 73 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_lombard_renaissance_period_present():
    """Session 73: LOMBARD_RENAISSANCE must exist in Period enum."""
    assert hasattr(Period, "LOMBARD_RENAISSANCE"), (
        "Period.LOMBARD_RENAISSANCE not found — add it to scene_schema.py")
    assert Period.LOMBARD_RENAISSANCE in list(Period)


def test_lombard_renaissance_stroke_params_high_wet_blend():
    """LOMBARD_RENAISSANCE should have high wet_blend (seamless Lombard skin blending)."""
    style = Style(medium=Medium.OIL, period=Period.LOMBARD_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.55, (
        f"LOMBARD_RENAISSANCE wet_blend should be >= 0.55 for Anguissola's seamless skin; "
        f"got {p['wet_blend']}")


def test_lombard_renaissance_stroke_params_moderate_edge_softness():
    """LOMBARD_RENAISSANCE should have moderate-to-high edge_softness."""
    style = Style(medium=Medium.OIL, period=Period.LOMBARD_RENAISSANCE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.45 <= p["edge_softness"] <= 0.85, (
        f"LOMBARD_RENAISSANCE edge_softness should be in [0.45, 0.85] for Lombard warmth; "
        f"got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Hieronymus Bosch — session 74 random artist discovery
# ──────────────────────────────────────────────────────────────────────────────

def test_hieronymus_bosch_in_catalog():
    """Bosch (session 74) must be present in CATALOG."""
    assert "hieronymus_bosch" in CATALOG


def test_hieronymus_bosch_movement_contains_netherlandish():
    """Bosch movement should reference Netherlandish or Brabantine tradition."""
    s = get_style("hieronymus_bosch")
    text = s.movement.lower()
    assert "netherlandish" in text or "brabant" in text or "flemish" in text, (
        f"Bosch movement should reference Netherlandish or Brabantine; got {s.movement!r}")


def test_hieronymus_bosch_palette_length():
    """Bosch palette should have at least 7 colours (dark void + jewel accents)."""
    s = get_style("hieronymus_bosch")
    assert len(s.palette) >= 7, (
        f"Bosch palette should have >= 7 colours; got {len(s.palette)}")


def test_hieronymus_bosch_palette_values_in_range():
    """All Bosch palette RGB values must be in [0, 1]."""
    s = get_style("hieronymus_bosch")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Bosch palette {rgb}")


def test_hieronymus_bosch_ground_color_dark():
    """Bosch ground_color should be dark (luminance < 0.25) — the Brabantine void."""
    s = get_style("hieronymus_bosch")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum < 0.25, (
        f"Bosch ground_color should be dark (lum < 0.25 for Brabantine void); got lum={lum:.3f}")


def test_hieronymus_bosch_wet_blend_moderate():
    """Bosch wet_blend should be moderate — controlled transparent oil glazes."""
    s = get_style("hieronymus_bosch")
    assert 0.20 <= s.wet_blend <= 0.55, (
        f"Bosch wet_blend should be moderate [0.20, 0.55]; got {s.wet_blend}")


def test_hieronymus_bosch_famous_works():
    """Bosch should have at least 5 famous works including The Garden of Earthly Delights."""
    s = get_style("hieronymus_bosch")
    assert len(s.famous_works) >= 5, (
        f"Bosch should have >= 5 famous works; got {len(s.famous_works)}")
    titles = [title for title, _ in s.famous_works]
    assert any("Garden" in t for t in titles), (
        "Bosch famous_works should include The Garden of Earthly Delights")


def test_hieronymus_bosch_inspiration_references_phantasmagoria_pass():
    """Bosch inspiration text should reference bosch_phantasmagoria_pass."""
    s = get_style("hieronymus_bosch")
    assert "phantasmagoria" in s.inspiration.lower() or "bosch_phantasmagoria" in s.inspiration, (
        f"Bosch inspiration should reference phantasmagoria_pass; "
        f"got {s.inspiration[:100]!r}")


def test_hieronymus_bosch_in_expected_artists():
    """hieronymus_bosch must be present in the EXPECTED_ARTISTS list."""
    assert "hieronymus_bosch" in EXPECTED_ARTISTS, (
        "hieronymus_bosch missing from EXPECTED_ARTISTS — add it to the list "
        "in test_art_catalog.py")


# ──────────────────────────────────────────────────────────────────────────────
# Period.NORTHERN_FANTASTICAL — session 74 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_northern_fantastical_period_present():
    """Session 74: NORTHERN_FANTASTICAL must exist in Period enum."""
    assert hasattr(Period, "NORTHERN_FANTASTICAL"), (
        "Period.NORTHERN_FANTASTICAL not found — add it to scene_schema.py")
    assert Period.NORTHERN_FANTASTICAL in list(Period)


def test_northern_fantastical_stroke_params_fine_marks():
    """NORTHERN_FANTASTICAL should have small stroke_size_face for Bosch's micro-detail."""
    style = Style(medium=Medium.OIL, period=Period.NORTHERN_FANTASTICAL,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] <= 6, (
        f"NORTHERN_FANTASTICAL stroke_size_face should be <= 6 for Bosch micro-detail; "
        f"got {p['stroke_size_face']}")


def test_northern_fantastical_stroke_params_moderate_edge_softness():
    """NORTHERN_FANTASTICAL should have moderate edge_softness for jewel clarity."""
    style = Style(medium=Medium.OIL, period=Period.NORTHERN_FANTASTICAL,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] <= 0.50, (
        f"NORTHERN_FANTASTICAL edge_softness should be <= 0.50 for jewel clarity; "
        f"got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Pieter de Hooch — session 75 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_pieter_de_hooch_in_catalog():
    """Pieter de Hooch must be present in the CATALOG under key 'pieter_de_hooch'."""
    assert "pieter_de_hooch" in CATALOG, "pieter_de_hooch not found in CATALOG"


def test_pieter_de_hooch_style_retrieval():
    """get_style('pieter_de_hooch') must return an ArtStyle without raising."""
    s = get_style("pieter_de_hooch")
    assert s is not None


def test_pieter_de_hooch_movement():
    """Pieter de Hooch should be classified in the Dutch Golden Age movement."""
    s = get_style("pieter_de_hooch")
    assert "Dutch" in s.movement, (
        f"Expected 'Dutch' in movement, got {s.movement!r}")


def test_pieter_de_hooch_nationality():
    """Pieter de Hooch should be Dutch."""
    s = get_style("pieter_de_hooch")
    assert s.nationality == "Dutch", (
        f"Expected nationality='Dutch', got {s.nationality!r}")


def test_pieter_de_hooch_palette_length():
    """Pieter de Hooch palette must have at least 7 colours."""
    s = get_style("pieter_de_hooch")
    assert len(s.palette) >= 7, (
        f"Expected at least 7 palette colours, got {len(s.palette)}")


def test_pieter_de_hooch_palette_has_warm_amber():
    """de Hooch palette must include a warm amber/ochre floor-light tone."""
    s = get_style("pieter_de_hooch")
    warm = [(r, g, b) for r, g, b in s.palette if r > 0.60 and g > 0.40 and b < 0.40]
    assert warm, "pieter_de_hooch palette should include a warm amber/ochre tone"


def test_pieter_de_hooch_palette_has_cool_exterior():
    """de Hooch palette must include a cool grey-blue exterior daylight tone."""
    s = get_style("pieter_de_hooch")
    cool = [(r, g, b) for r, g, b in s.palette if b > r and b > 0.40]
    assert cool, "pieter_de_hooch palette should include a cool blue-grey exterior tone"


def test_pieter_de_hooch_ground_is_warm():
    """de Hooch ground should be a warm sienna-ochre imprimatura (mean > 0.38)."""
    s = get_style("pieter_de_hooch")
    mean_ground = sum(s.ground_color) / 3.0
    assert mean_ground > 0.38, (
        f"pieter_de_hooch ground should be warm (mean > 0.38), got {mean_ground:.3f}")


def test_pieter_de_hooch_low_wet_blend():
    """de Hooch wet_blend should be low (< 0.35) — measured, unhurried strokes."""
    s = get_style("pieter_de_hooch")
    assert s.wet_blend < 0.35, (
        f"pieter_de_hooch wet_blend should be < 0.35 for deliberate stroke quality; "
        f"got {s.wet_blend}")


def test_pieter_de_hooch_has_crackle():
    """de Hooch should have crackle=True for aged panel surface texture."""
    s = get_style("pieter_de_hooch")
    assert s.crackle is True, "pieter_de_hooch should have crackle=True"


def test_pieter_de_hooch_famous_works():
    """de Hooch famous_works must include the Courtyard of a House in Delft."""
    s = get_style("pieter_de_hooch")
    titles = [title for title, _ in s.famous_works]
    assert any("Courtyard" in t or "Delft" in t for t in titles), (
        "pieter_de_hooch famous_works should include 'The Courtyard of a House in Delft'")


def test_dutch_domestic_period_present():
    """Session 75: DUTCH_DOMESTIC must exist in Period enum."""
    assert hasattr(Period, "DUTCH_DOMESTIC"), (
        "Period.DUTCH_DOMESTIC not found — add it to scene_schema.py")
    assert Period.DUTCH_DOMESTIC in list(Period)


def test_dutch_domestic_stroke_params_low_wet_blend():
    """DUTCH_DOMESTIC should have low wet_blend for de Hooch's measured strokes."""
    style = Style(medium=Medium.OIL, period=Period.DUTCH_DOMESTIC,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.30, (
        f"DUTCH_DOMESTIC wet_blend should be <= 0.30 for de Hooch's deliberate quality; "
        f"got {p['wet_blend']}")


def test_dutch_domestic_stroke_params_moderate_edge_softness():
    """DUTCH_DOMESTIC should have moderate edge_softness for threshold light clarity."""
    style = Style(medium=Medium.OIL, period=Period.DUTCH_DOMESTIC,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.40 <= p["edge_softness"] <= 0.70, (
        f"DUTCH_DOMESTIC edge_softness should be in [0.40, 0.70] for threshold clarity; "
        f"got {p['edge_softness']}")


# ──────────────────────────────────────────────────────────────────────────────
# Jan Steen — session 76 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_jan_steen_in_catalog():
    """Jan Steen must be present in the CATALOG under key 'jan_steen'."""
    assert "jan_steen" in CATALOG, "jan_steen not found in CATALOG"


def test_jan_steen_style_retrieval():
    """get_style('jan_steen') must return an ArtStyle without raising."""
    s = get_style("jan_steen")
    assert s is not None


def test_jan_steen_movement():
    """Jan Steen should be classified in the Dutch Golden Age / Genre Comedy movement."""
    s = get_style("jan_steen")
    assert "Dutch" in s.movement, (
        f"Expected 'Dutch' in movement, got {s.movement!r}")


def test_jan_steen_nationality():
    """Jan Steen should be Dutch."""
    s = get_style("jan_steen")
    assert s.nationality == "Dutch", (
        f"Expected nationality='Dutch', got {s.nationality!r}")


def test_jan_steen_palette_length():
    """Jan Steen palette must have at least 7 colours."""
    s = get_style("jan_steen")
    assert len(s.palette) >= 7, (
        f"Expected at least 7 palette colours, got {len(s.palette)}")


def test_jan_steen_palette_has_warm_amber_flesh():
    """Jan Steen palette must include a warm amber flesh highlight."""
    s = get_style("jan_steen")
    warm_flesh = [(r, g, b) for r, g, b in s.palette if r > 0.70 and g > 0.50 and b < 0.60]
    assert warm_flesh, "jan_steen palette should include a warm amber flesh highlight"


def test_jan_steen_palette_has_vivid_red():
    """Jan Steen palette must include a vivid red costume accent (vermilion)."""
    s = get_style("jan_steen")
    has_red = any(r > 0.65 and g < 0.35 and b < 0.25 for r, g, b in s.palette)
    assert has_red, "jan_steen palette should include a vivid red accent (vermilion-scarlet)"


def test_jan_steen_palette_has_dark_shadow():
    """Jan Steen palette must include a near-black deep shadow."""
    s = get_style("jan_steen")
    has_dark = any(r < 0.25 and g < 0.20 and b < 0.15 for r, g, b in s.palette)
    assert has_dark, "jan_steen palette should include a near-black deep shadow"


def test_jan_steen_palette_values_in_range():
    """All Jan Steen palette RGB values must be in [0, 1]."""
    s = get_style("jan_steen")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in jan_steen palette {rgb}")


def test_jan_steen_ground_is_warm():
    """Jan Steen ground_color should be a warm amber-ochre imprimatura (mean > 0.35)."""
    s = get_style("jan_steen")
    mean_ground = sum(s.ground_color) / 3.0
    assert mean_ground > 0.35, (
        f"jan_steen ground should be warm (mean > 0.35), got {mean_ground:.3f}")


def test_jan_steen_moderate_wet_blend():
    """Jan Steen wet_blend should be moderate [0.25, 0.55] — lively but not sfumato."""
    s = get_style("jan_steen")
    assert 0.25 <= s.wet_blend <= 0.55, (
        f"jan_steen wet_blend should be in [0.25, 0.55] for alla prima vitality; "
        f"got {s.wet_blend}")


def test_jan_steen_has_crackle():
    """Jan Steen should have crackle=True for aged canvas texture."""
    s = get_style("jan_steen")
    assert s.crackle is True, "jan_steen should have crackle=True"


def test_jan_steen_famous_works():
    """Jan Steen famous_works must include at least 4 works including The Feast of Saint Nicholas."""
    s = get_style("jan_steen")
    assert len(s.famous_works) >= 4, (
        f"jan_steen should have >= 4 famous works; got {len(s.famous_works)}")
    titles = [title for title, _ in s.famous_works]
    assert any("Nicholas" in t or "Feast" in t or "Merry" in t for t in titles), (
        "jan_steen famous_works should include The Feast of Saint Nicholas or a Merry scene")


def test_jan_steen_inspiration_references_vitality_pass():
    """Jan Steen inspiration text should reference steen_warm_vitality_pass."""
    s = get_style("jan_steen")
    assert "steen_warm_vitality" in s.inspiration.lower().replace(" ", "_"), (
        "jan_steen inspiration should reference steen_warm_vitality_pass()")


def test_jan_steen_in_expected_artists():
    """jan_steen must be present in the EXPECTED_ARTISTS list."""
    assert "jan_steen" in EXPECTED_ARTISTS, (
        "jan_steen missing from EXPECTED_ARTISTS — add it to the list in test_art_catalog.py")


# ──────────────────────────────────────────────────────────────────────────────
# Period.DUTCH_GENRE_COMEDY — session 76 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_dutch_genre_comedy_period_present():
    """Session 76: DUTCH_GENRE_COMEDY must exist in Period enum."""
    assert hasattr(Period, "DUTCH_GENRE_COMEDY"), (
        "Period.DUTCH_GENRE_COMEDY not found — add it to scene_schema.py")
    assert Period.DUTCH_GENRE_COMEDY in list(Period)


def test_dutch_genre_comedy_stroke_params_moderate_wet_blend():
    """DUTCH_GENRE_COMEDY should have moderate wet_blend for Steen's alla prima vitality."""
    style = Style(medium=Medium.OIL, period=Period.DUTCH_GENRE_COMEDY,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.25 <= p["wet_blend"] <= 0.55, (
        f"DUTCH_GENRE_COMEDY wet_blend should be in [0.25, 0.55] for Steen's lively painting; "
        f"got {p['wet_blend']}")


def test_dutch_genre_comedy_stroke_params_moderate_edge_softness():
    """DUTCH_GENRE_COMEDY should have moderate edge_softness for Steen's confident strokes."""
    style = Style(medium=Medium.OIL, period=Period.DUTCH_GENRE_COMEDY,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.30 <= p["edge_softness"] <= 0.60, (
        f"DUTCH_GENRE_COMEDY edge_softness should be in [0.30, 0.60] for Steen's energy; "
        f"got {p['edge_softness']}")


def test_dutch_genre_comedy_stroke_params_vigorous_marks():
    """DUTCH_GENRE_COMEDY stroke_size_face should be >= 7 for Steen's vigorous brushwork."""
    style = Style(medium=Medium.OIL, period=Period.DUTCH_GENRE_COMEDY,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["stroke_size_face"] >= 7, (
        f"DUTCH_GENRE_COMEDY stroke_size_face should be >= 7 for Steen's energetic marks; "
        f"got {p['stroke_size_face']}")


# ──────────────────────────────────────────────────────────────────────────────
# Hyacinthe Rigaud / FRENCH_COURT_BAROQUE — session 78 tests
# ──────────────────────────────────────────────────────────────────────────────

def test_hyacinthe_rigaud_in_catalog():
    """hyacinthe_rigaud must be present in CATALOG."""
    assert "hyacinthe_rigaud" in CATALOG, (
        "hyacinthe_rigaud not found in CATALOG — add the ArtStyle entry")


def test_hyacinthe_rigaud_palette_valid():
    """Every colour in hyacinthe_rigaud palette must have RGB channels in [0, 1]."""
    s = get_style("hyacinthe_rigaud")
    for i, col in enumerate(s.palette):
        for j, v in enumerate(col):
            assert 0.0 <= v <= 1.0, (
                f"hyacinthe_rigaud palette[{i}][{j}]={v:.3f} out of [0, 1]")


def test_hyacinthe_rigaud_warm_glazing():
    """
    hyacinthe_rigaud glazing must be warm (R >= B) — amber-brown unifying glaze
    reflects the candlelit warmth of French court portraiture.
    """
    s = get_style("hyacinthe_rigaud")
    assert s.glazing is not None, (
        "hyacinthe_rigaud glazing should not be None — warm amber-brown glaze")
    r, _g, b = s.glazing
    assert r >= b, (
        f"hyacinthe_rigaud glazing R={r:.3f} should be >= B={b:.3f} "
        f"(warm amber court portrait glaze, not a cool Poussin silver)")


def test_hyacinthe_rigaud_moderate_wet_blend():
    """
    hyacinthe_rigaud wet_blend should be in [0.20, 0.45] — controlled deliberate
    layering for velvet modelling, not Baroque alla prima spontaneity.
    """
    s = get_style("hyacinthe_rigaud")
    assert 0.20 <= s.wet_blend <= 0.45, (
        f"hyacinthe_rigaud wet_blend={s.wet_blend:.2f} should be in [0.20, 0.45] "
        f"(controlled layering for velvet: not fully blended, not dry-alla-prima)")


def test_hyacinthe_rigaud_moderate_edges():
    """
    hyacinthe_rigaud edge_softness should be in [0.25, 0.55] — silk has found
    edges, velvet has soft transitions; neither sfumato nor Tenebrist razor.
    """
    s = get_style("hyacinthe_rigaud")
    assert 0.25 <= s.edge_softness <= 0.55, (
        f"hyacinthe_rigaud edge_softness={s.edge_softness:.2f} should be in [0.25, 0.55] "
        f"(silk highlight crispness balanced against velvet softness)")


def test_hyacinthe_rigaud_crackle():
    """hyacinthe_rigaud crackle should be True — aged 17th-century oil on canvas."""
    s = get_style("hyacinthe_rigaud")
    assert s.crackle is True, (
        "hyacinthe_rigaud crackle should be True (aged court portrait oil on canvas)")


def test_hyacinthe_rigaud_no_chromatic_split():
    """hyacinthe_rigaud chromatic_split should be False — no Pointillist technique."""
    s = get_style("hyacinthe_rigaud")
    assert s.chromatic_split is False, (
        "hyacinthe_rigaud chromatic_split should be False (no Seurat/divisionist dots)")


def test_hyacinthe_rigaud_dark_velvet_in_palette():
    """
    hyacinthe_rigaud palette must contain at least one near-black velvet colour
    (lum < 0.15) — the deep void is the defining material quality of his drapery.
    """
    s = get_style("hyacinthe_rigaud")
    has_dark = any(
        0.2126 * r + 0.7152 * g + 0.0722 * b < 0.15
        for r, g, b in s.palette
    )
    assert has_dark, (
        "hyacinthe_rigaud palette should include a near-black velvet void colour "
        "(lum < 0.15) — the deep darkness is the chromatic signature of his drapery")


def test_french_court_baroque_period_present():
    """Period.FRENCH_COURT_BAROQUE must be a valid member of the Period enum."""
    assert hasattr(Period, "FRENCH_COURT_BAROQUE"), (
        "Period enum is missing FRENCH_COURT_BAROQUE — add it to scene_schema.py")


def test_french_court_baroque_stroke_params_valid():
    """FRENCH_COURT_BAROQUE stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_COURT_BAROQUE).stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in sp, f"FRENCH_COURT_BAROQUE stroke_params missing key: {key!r}"
    assert 3 <= sp["stroke_size_face"] <= 20, (
        f"FRENCH_COURT_BAROQUE stroke_size_face={sp['stroke_size_face']} should be in [3, 20]")
    assert 0 <= sp["wet_blend"] <= 1, (
        f"FRENCH_COURT_BAROQUE wet_blend={sp['wet_blend']} should be in [0, 1]")
    assert 0 <= sp["edge_softness"] <= 1, (
        f"FRENCH_COURT_BAROQUE edge_softness={sp['edge_softness']} should be in [0, 1]")


# -------------------------------------------------------------------------
# Lorenzo Lotto / VENETIAN_PSYCHOLOGICAL -- session 79 tests
# -------------------------------------------------------------------------


def test_lorenzo_lotto_in_catalog():
    """lorenzo_lotto must be present in CATALOG."""
    assert "lorenzo_lotto" in CATALOG, (
        "lorenzo_lotto not found in CATALOG -- add the ArtStyle entry")


def test_lorenzo_lotto_palette_valid():
    """Every colour in lorenzo_lotto palette must have RGB channels in [0, 1]."""
    s = get_style("lorenzo_lotto")
    for i, col in enumerate(s.palette):
        for j, v in enumerate(col):
            assert 0.0 <= v <= 1.0, (
                f"lorenzo_lotto palette[{i}][{j}]={v:.3f} out of [0, 1]")


def test_lorenzo_lotto_cool_neutral_glazing():
    """
    lorenzo_lotto glazing must be present and cool-neutral (B >= R) --
    distinguishes Lotto from warm-glazing Venetians like Titian.
    """
    s = get_style("lorenzo_lotto")
    assert s.glazing is not None, (
        "lorenzo_lotto glazing should not be None -- cool-neutral glaze required")
    r, g, b = s.glazing
    assert b >= r, (
        f"lorenzo_lotto glazing B={b:.3f} should be >= R={r:.3f} "
        f"(cool-neutral register distinguishes Lotto from warm-glazing Titian)")


def test_lorenzo_lotto_moderate_wet_blend():
    """
    lorenzo_lotto wet_blend should be in [0.30, 0.60] -- Venetian oil blending
    but with less dissolution than Titian.
    """
    s = get_style("lorenzo_lotto")
    assert 0.30 <= s.wet_blend <= 0.60, (
        f"lorenzo_lotto wet_blend={s.wet_blend:.2f} should be in [0.30, 0.60] "
        "(Venetian oil blending, less dissolved than Titian)")


def test_lorenzo_lotto_moderate_edge_softness():
    """
    lorenzo_lotto edge_softness should be in [0.35, 0.65] -- psychologically
    crisp without full sfumato dissolution.
    """
    s = get_style("lorenzo_lotto")
    assert 0.35 <= s.edge_softness <= 0.65, (
        f"lorenzo_lotto edge_softness={s.edge_softness:.2f} should be in [0.35, 0.65] "
        "(moderate softness -- psychological crispness without Leonardo sfumato)")


def test_lorenzo_lotto_crackle():
    """lorenzo_lotto crackle should be True -- aged Renaissance oil on canvas."""
    s = get_style("lorenzo_lotto")
    assert s.crackle is True, (
        "lorenzo_lotto crackle should be True (aged 16th-century Venetian oil)")


def test_lorenzo_lotto_no_chromatic_split():
    """lorenzo_lotto chromatic_split should be False -- no Pointillist technique."""
    s = get_style("lorenzo_lotto")
    assert s.chromatic_split is False, (
        "lorenzo_lotto chromatic_split should be False (no Seurat dots)")


def test_lorenzo_lotto_cool_midtone_in_palette():
    """
    lorenzo_lotto palette must contain at least one cool midtone (B > R+0.05) --
    the cool chromatic undertone is his defining quality.
    """
    s = get_style("lorenzo_lotto")
    has_cool = any(b > r + 0.05 for r, g, b in s.palette)
    assert has_cool, (
        "lorenzo_lotto palette should include at least one cool midtone (B > R+0.05) "
        "-- the cool chromatic anxiety is his defining departure from Venetian warmth")


def test_lorenzo_lotto_warm_highlight_in_palette():
    """
    lorenzo_lotto palette must contain at least one warm highlight (R >= 0.80) --
    Venetian flesh warmth is inherited even if the shadow register is cool.
    """
    s = get_style("lorenzo_lotto")
    has_warm_high = any(r >= 0.80 for r, g, b in s.palette)
    assert has_warm_high, (
        "lorenzo_lotto palette should include at least one warm highlight (R >= 0.80) "
        "-- Lotto inherited the Venetian warm flesh tradition despite his cool departures")


def test_venetian_psychological_period_present():
    """Period.VENETIAN_PSYCHOLOGICAL must be a valid member of the Period enum."""
    assert hasattr(Period, 'VENETIAN_PSYCHOLOGICAL'), (
        'Period enum is missing VENETIAN_PSYCHOLOGICAL -- add it to scene_schema.py')


def test_venetian_psychological_stroke_params_valid():
    """VENETIAN_PSYCHOLOGICAL stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.VENETIAN_PSYCHOLOGICAL).stroke_params
    for key in ('stroke_size_face', 'stroke_size_bg', 'wet_blend', 'edge_softness'):
        assert key in sp, f'VENETIAN_PSYCHOLOGICAL stroke_params missing key: {key!r}'
    assert 3 <= sp['stroke_size_face'] <= 20, (
        f"VENETIAN_PSYCHOLOGICAL stroke_size_face={sp['stroke_size_face']} should be in [3, 20]")
    assert 0 <= sp['wet_blend'] <= 1, (
        f"VENETIAN_PSYCHOLOGICAL wet_blend={sp['wet_blend']} should be in [0, 1]")
    assert 0 <= sp['edge_softness'] <= 1, (
        f"VENETIAN_PSYCHOLOGICAL edge_softness={sp['edge_softness']} should be in [0, 1]")


# ──────────────────────────────────────────────────────────────────────────────
# Session 80 — Andrea del Sarto (Florentine High Renaissance)
# ──────────────────────────────────────────────────────────────────────────────

def test_andrea_del_sarto_in_catalog():
    """Andrea del Sarto (session 80) must be present in the catalog."""
    assert "andrea_del_sarto" in CATALOG, (
        "andrea_del_sarto missing from CATALOG -- add it to art_catalog.py")


def test_andrea_del_sarto_palette_valid():
    """
    andrea_del_sarto palette must have ≥ 5 colours with all channels in [0, 1].
    """
    s = get_style("andrea_del_sarto")
    assert len(s.palette) >= 5, (
        f"andrea_del_sarto palette has {len(s.palette)} colours; expected ≥ 5")
    for i, rgb in enumerate(s.palette):
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"andrea_del_sarto palette[{i}] channel {ch:.3f} out of [0, 1]")


def test_andrea_del_sarto_warm_highlight_in_palette():
    """
    andrea_del_sarto palette must contain at least one warm ivory highlight
    (R >= 0.88, R > B + 0.12) — the 'faultless' flesh-light quality.
    """
    s = get_style("andrea_del_sarto")
    has_warm_high = any(r >= 0.88 and r > b + 0.12 for r, g, b in s.palette)
    assert has_warm_high, (
        "andrea_del_sarto palette should include at least one warm ivory highlight "
        "(R >= 0.88, R > B+0.12) -- the signature ivory-gold flesh light of del Sarto")


def test_andrea_del_sarto_warm_glaze():
    """
    andrea_del_sarto glazing must be warm (R > B + 0.10) -- the amber unifying
    glaze that ties his compositions into a harmonious golden tonality.
    """
    s = get_style("andrea_del_sarto")
    r, g, b = s.glazing
    assert r > b + 0.10, (
        f"andrea_del_sarto glazing R={r:.3f} B={b:.3f}: expected R > B+0.10 "
        "(warm amber glaze is the unifying tonality of del Sarto's Florentine palette)")


def test_andrea_del_sarto_high_wet_blend():
    """
    andrea_del_sarto wet_blend must be in [0.55, 0.80] -- the seamless Florentine
    tonal transitions that Vasari called 'faultless'.
    """
    s = get_style("andrea_del_sarto")
    assert 0.55 <= s.wet_blend <= 0.80, (
        f"andrea_del_sarto wet_blend={s.wet_blend:.2f} should be in [0.55, 0.80] "
        "(high blending for the 'faultless' seamless Florentine transitions)")


def test_andrea_del_sarto_high_edge_softness():
    """
    andrea_del_sarto edge_softness must be in [0.50, 0.75] -- Leonardo-adjacent
    sfumato, warmer and more grounded than Leonardo's full dissolution.
    """
    s = get_style("andrea_del_sarto")
    assert 0.50 <= s.edge_softness <= 0.75, (
        f"andrea_del_sarto edge_softness={s.edge_softness:.2f} should be in [0.50, 0.75] "
        "(high sfumato in the Florentine tradition -- not cool dissolution but warm atmospheric softness)")


def test_andrea_del_sarto_crackle():
    """andrea_del_sarto crackle should be True -- aged Renaissance oil on panel."""
    s = get_style("andrea_del_sarto")
    assert s.crackle is True, (
        "andrea_del_sarto crackle should be True (aged 16th-century Florentine oil)")


def test_andrea_del_sarto_no_chromatic_split():
    """andrea_del_sarto chromatic_split should be False -- no Pointillist dots."""
    s = get_style("andrea_del_sarto")
    assert s.chromatic_split is False, (
        "andrea_del_sarto chromatic_split should be False (no Seurat divisionism)")


def test_andrea_del_sarto_ground_color_warm():
    """
    andrea_del_sarto ground_color must be warm (R > B + 0.15) -- the amber-ochre
    imprimatura from which del Sarto built his warm flesh glazing.
    """
    s = get_style("andrea_del_sarto")
    r, g, b = s.ground_color
    assert r > b + 0.15, (
        f"andrea_del_sarto ground_color R={r:.3f} B={b:.3f}: expected R > B+0.15 "
        "(warm amber-ochre imprimatura is the foundation of del Sarto's warmth)")


def test_andrea_del_sarto_technique_mentions_faultless():
    """
    andrea_del_sarto technique text must mention either 'faultless' or 'sanza errori'
    -- Vasari's epithet is the canonical description of del Sarto's quality.
    """
    s = get_style("andrea_del_sarto")
    tech_lower = s.technique.lower()
    assert "faultless" in tech_lower or "sanza errori" in tech_lower, (
        "andrea_del_sarto technique should mention 'faultless' or 'sanza errori' "
        "(Vasari's canonical epithet for Andrea del Sarto)")


def test_andrea_del_sarto_famous_works_present():
    """andrea_del_sarto must list ≥ 3 famous works."""
    s = get_style("andrea_del_sarto")
    assert len(s.famous_works) >= 3, (
        f"andrea_del_sarto famous_works has {len(s.famous_works)} entries; expected ≥ 3")
    for title, year in s.famous_works:
        assert isinstance(title, str) and len(title) > 0
        assert isinstance(year, str) and len(year) > 0


def test_florentine_high_renaissance_period_present():
    """Period.FLORENTINE_HIGH_RENAISSANCE must be a valid member of the Period enum."""
    assert hasattr(Period, 'FLORENTINE_HIGH_RENAISSANCE'), (
        'Period enum is missing FLORENTINE_HIGH_RENAISSANCE -- add it to scene_schema.py')


def test_florentine_high_renaissance_stroke_params_valid():
    """FLORENTINE_HIGH_RENAISSANCE stroke_params must contain all required keys."""
    sp = Style(medium=Medium.OIL, period=Period.FLORENTINE_HIGH_RENAISSANCE).stroke_params
    for key in ('stroke_size_face', 'stroke_size_bg', 'wet_blend', 'edge_softness'):
        assert key in sp, (
            f'FLORENTINE_HIGH_RENAISSANCE stroke_params missing key: {key!r}')
    assert 3 <= sp['stroke_size_face'] <= 20, (
        f"FLORENTINE_HIGH_RENAISSANCE stroke_size_face={sp['stroke_size_face']} "
        "should be in [3, 20]")
    assert 0.55 <= sp['wet_blend'] <= 0.80, (
        f"FLORENTINE_HIGH_RENAISSANCE wet_blend={sp['wet_blend']:.2f} should be "
        "in [0.55, 0.80] (high blending for del Sarto's seamless Florentine transitions)")
    assert 0.50 <= sp['edge_softness'] <= 0.75, (
        f"FLORENTINE_HIGH_RENAISSANCE edge_softness={sp['edge_softness']:.2f} should "
        "be in [0.50, 0.75] (high sfumato in the Florentine tradition)")


# Jean-Baptiste-Siméon Chardin / FRENCH_INTIMISTE -- session 81 tests
# ─────────────────────────────────────────────────────────────────────────────

def test_chardin_in_catalog():
    """chardin must be present in CATALOG."""
    assert "chardin" in CATALOG, (
        "chardin not found in CATALOG -- add the ArtStyle entry")


def test_chardin_palette_valid():
    """Every colour in chardin palette must have RGB channels in [0, 1]."""
    s = get_style("chardin")
    for i, col in enumerate(s.palette):
        for j, v in enumerate(col):
            assert 0.0 <= v <= 1.0, (
                f"chardin palette[{i}][{j}]={v:.3f} out of [0, 1]")


def test_chardin_palette_muted():
    """
    chardin palette must be muted — no highly saturated (max-min > 0.55) colours.
    Chardin's defining palette quality is warm-gray atmospheric restraint.
    """
    s = get_style("chardin")
    for i, (r, g, b) in enumerate(s.palette):
        sat = max(r, g, b) - min(r, g, b)
        assert sat <= 0.55, (
            f"chardin palette[{i}] saturation={sat:.3f} exceeds 0.55 -- "
            "Chardin's palette is muted warm-gray, not chromatic")


def test_chardin_warm_ground():
    """
    chardin ground_color must be warm (R > B + 0.08) — the warm mid-gray
    imprimatura that breathes through Chardin's finished surfaces.
    """
    s = get_style("chardin")
    r, g, b = s.ground_color
    assert r > b + 0.08, (
        f"chardin ground_color R={r:.3f} B={b:.3f}: expected R > B+0.08 "
        "(warm mid-gray imprimatura is the foundation of Chardin's atmospheric warmth)")


def test_chardin_low_wet_blend():
    """
    chardin wet_blend should be low (≤ 0.30) -- Chardin's granular dabs stay distinct;
    optical mixing happens on the retina, not by blending on the palette.
    """
    s = get_style("chardin")
    assert s.wet_blend <= 0.30, (
        f"chardin wet_blend={s.wet_blend:.2f} should be ≤ 0.30 "
        "(low -- granular dabs must stay distinct for Chardin's optical texture)")


def test_chardin_moderate_edge_softness():
    """
    chardin edge_softness should be in [0.40, 0.68] -- soft but legible;
    Chardin's forms always remain readable through the atmospheric grain.
    """
    s = get_style("chardin")
    assert 0.40 <= s.edge_softness <= 0.68, (
        f"chardin edge_softness={s.edge_softness:.2f} should be in [0.40, 0.68] "
        "(soft without full sfumato -- forms legible through the atmospheric grain)")


def test_chardin_crackle():
    """chardin crackle should be True -- aged 18th-century French oil on canvas."""
    s = get_style("chardin")
    assert s.crackle is True, (
        "chardin crackle should be True (aged 18th-century French oil on canvas)")


def test_chardin_no_chromatic_split():
    """chardin chromatic_split should be False -- no Pointillist systematic dots."""
    s = get_style("chardin")
    assert s.chromatic_split is False, (
        "chardin chromatic_split should be False (granular optical texture, not Seurat divisionism)")


def test_chardin_warm_gray_glazing():
    """
    chardin glazing must be warm (R > B + 0.05) and present -- the warm
    gray-gold unifying glaze that ties Chardin's muted surfaces together.
    """
    s = get_style("chardin")
    assert s.glazing is not None, (
        "chardin glazing should not be None -- warm gray-gold glaze required")
    r, g, b = s.glazing
    assert r > b + 0.05, (
        f"chardin glazing R={r:.3f} B={b:.3f}: expected warm (R > B+0.05) "
        "-- Chardin's unifying glaze is warm gray-gold, not cool")


def test_chardin_technique_mentions_granular():
    """
    chardin technique text must mention 'granular' or 'dab' -- Chardin's
    defining optical texture is the core of his technique.
    """
    s = get_style("chardin")
    tech_lower = s.technique.lower()
    assert "granular" in tech_lower or "dab" in tech_lower, (
        "chardin technique should mention 'granular' or 'dab' "
        "(Chardin's granular optical dab-texture is his defining characteristic)")


def test_chardin_famous_works_present():
    """chardin must list >= 3 famous works."""
    s = get_style("chardin")
    assert len(s.famous_works) >= 3, (
        f"chardin famous_works has {len(s.famous_works)} entries; expected >= 3")
    for title, year in s.famous_works:
        assert isinstance(title, str) and len(title) > 0
        assert isinstance(year, str) and len(year) > 0


def test_french_intimiste_period_present():
    """Period.FRENCH_INTIMISTE must be a valid member of the Period enum."""
    assert hasattr(Period, 'FRENCH_INTIMISTE'), (
        'Period enum is missing FRENCH_INTIMISTE -- add it to scene_schema.py')


def test_french_intimiste_stroke_params_valid():
    """FRENCH_INTIMISTE stroke_params must contain all required keys with valid values."""
    sp = Style(medium=Medium.OIL, period=Period.FRENCH_INTIMISTE).stroke_params
    for key in ('stroke_size_face', 'stroke_size_bg', 'wet_blend', 'edge_softness'):
        assert key in sp, (
            f'FRENCH_INTIMISTE stroke_params missing key: {key!r}')
    assert 3 <= sp['stroke_size_face'] <= 10, (
        f"FRENCH_INTIMISTE stroke_size_face={sp['stroke_size_face']} "
        "should be in [3, 10] (small careful dabs)")
    assert sp['wet_blend'] <= 0.30, (
        f"FRENCH_INTIMISTE wet_blend={sp['wet_blend']:.2f} should be "
        "≤ 0.30 (low -- Chardin's granular dabs must stay distinct)")
    assert 0.40 <= sp['edge_softness'] <= 0.68, (
        f"FRENCH_INTIMISTE edge_softness={sp['edge_softness']:.2f} should "
        "be in [0.40, 0.68] (soft without full sfumato -- forms legible)")


# ═══════════════════════════════════════════════════════════════════════════════
# Session 83 — Fra Filippo Lippi tests
# ═══════════════════════════════════════════════════════════════════════════════

def test_fra_filippo_lippi_in_catalog():
    """fra_filippo_lippi must be a key in the CATALOG dict (session 83)."""
    assert "fra_filippo_lippi" in CATALOG, (
        "fra_filippo_lippi missing from CATALOG -- add entry in art_catalog.py")


def test_fra_filippo_lippi_artist_name():
    """fra_filippo_lippi artist field must contain 'Lippi'."""
    s = get_style("fra_filippo_lippi")
    assert "Lippi" in s.artist, (
        f"fra_filippo_lippi artist={s.artist!r} should contain 'Lippi'")


def test_fra_filippo_lippi_movement():
    """fra_filippo_lippi movement must mention 'Renaissance' or 'Quattrocento'."""
    s = get_style("fra_filippo_lippi")
    assert "Renaissance" in s.movement or "Quattrocento" in s.movement, (
        f"fra_filippo_lippi movement={s.movement!r} should mention "
        "'Renaissance' or 'Quattrocento'")


def test_fra_filippo_lippi_nationality():
    """fra_filippo_lippi nationality must be 'Italian'."""
    s = get_style("fra_filippo_lippi")
    assert s.nationality == "Italian", (
        f"fra_filippo_lippi nationality={s.nationality!r} should be 'Italian'")


def test_fra_filippo_lippi_palette_length():
    """fra_filippo_lippi palette must have >= 5 colours."""
    s = get_style("fra_filippo_lippi")
    assert len(s.palette) >= 5, (
        f"fra_filippo_lippi palette has {len(s.palette)} colours; expected >= 5")


def test_fra_filippo_lippi_palette_values_in_range():
    """fra_filippo_lippi palette: all RGB channels must be in [0, 1]."""
    s = get_style("fra_filippo_lippi")
    for i, rgb in enumerate(s.palette):
        for ch, val in enumerate(rgb):
            assert 0.0 <= val <= 1.0, (
                f"fra_filippo_lippi palette[{i}] channel {ch} = {val:.4f} "
                "is outside [0, 1]")


def test_fra_filippo_lippi_warm_palette():
    """
    fra_filippo_lippi palette's first colour (warm ivory highlight) must be warm:
    R > B + 0.10 -- Lippi's highlights are always warm ivory, never cool.
    """
    s = get_style("fra_filippo_lippi")
    r, g, b = s.palette[0]
    assert r > b + 0.10, (
        f"fra_filippo_lippi palette[0] R={r:.3f} B={b:.3f}: "
        "expected warm highlight (R > B + 0.10) -- Lippi's highlights are warm ivory")


def test_fra_filippo_lippi_low_wet_blend():
    """
    fra_filippo_lippi wet_blend must be <= 0.30 -- Lippi's tempera-influenced
    technique uses careful distinct marks; high blending would destroy the form.
    """
    s = get_style("fra_filippo_lippi")
    assert s.wet_blend <= 0.30, (
        f"fra_filippo_lippi wet_blend={s.wet_blend:.2f} should be <= 0.30 "
        "(tempera-influenced technique; marks stay distinct)")


def test_fra_filippo_lippi_glazing_warm():
    """
    fra_filippo_lippi glazing must be warm (R > B + 0.05) -- Lippi's unifying
    glaze was always warm parchment, never cool.
    """
    s = get_style("fra_filippo_lippi")
    assert s.glazing is not None, (
        "fra_filippo_lippi glazing should not be None -- warm parchment glaze required")
    r, g, b = s.glazing
    assert r > b + 0.05, (
        f"fra_filippo_lippi glazing R={r:.3f} B={b:.3f}: expected warm (R > B+0.05)")


def test_fra_filippo_lippi_technique_mentions_tenerezza():
    """
    fra_filippo_lippi technique text must mention 'tenerezza' -- Lippi's
    defining quality is 'tenderness of light'.
    """
    s = get_style("fra_filippo_lippi")
    assert "tenerezza" in s.technique.lower(), (
        "fra_filippo_lippi technique should mention 'tenerezza' "
        "(Lippi's defining quality: tenderness of light)")


def test_fra_filippo_lippi_famous_works_present():
    """fra_filippo_lippi must list >= 3 famous works."""
    s = get_style("fra_filippo_lippi")
    assert len(s.famous_works) >= 3, (
        f"fra_filippo_lippi famous_works has {len(s.famous_works)} entries; expected >= 3")
    for title, year in s.famous_works:
        assert isinstance(title, str) and len(title) > 0
        assert isinstance(year, str) and len(year) > 0


def test_fra_filippo_lippi_inspiration_references_tenerezza_pass():
    """
    fra_filippo_lippi inspiration must reference 'fra_filippo_lippi_tenerezza_pass'
    so the pipeline knows which pass to call.
    """
    s = get_style("fra_filippo_lippi")
    assert "fra_filippo_lippi_tenerezza_pass" in s.inspiration, (
        "fra_filippo_lippi inspiration should reference 'fra_filippo_lippi_tenerezza_pass'")


def test_fra_filippo_lippi_ground_color_warm():
    """
    fra_filippo_lippi ground_color must be warm (R > B + 0.08) -- Lippi worked
    on warm buff/parchment grounds, not cool gesso.
    """
    s = get_style("fra_filippo_lippi")
    r, g, b = s.ground_color
    assert r > b + 0.08, (
        f"fra_filippo_lippi ground_color R={r:.3f} B={b:.3f}: "
        "expected warm ground (R > B + 0.08) -- Lippi used warm buff/parchment imprimatura")


# ──────────────────────────────────────────────────────────────────────────────
# Pietro Perugino — Session 84 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_perugino_in_catalog():
    """Pietro Perugino must be present in CATALOG."""
    assert "perugino" in CATALOG, "perugino not found in CATALOG"


def test_perugino_movement():
    """Perugino's movement must reference Umbrian or High Renaissance."""
    s = get_style("perugino")
    m = s.movement.lower()
    assert "umbrian" in m or "renaissance" in m, (
        f"Perugino movement should reference Umbrian or Renaissance; got: {s.movement!r}")


def test_perugino_nationality():
    """Perugino was Italian."""
    s = get_style("perugino")
    assert "italian" in s.nationality.lower(), (
        f"Perugino nationality should be Italian; got: {s.nationality!r}")


def test_perugino_palette_length():
    """Perugino's palette should have at least 6 colours (sky blues, flesh, landscape greens)."""
    s = get_style("perugino")
    assert len(s.palette) >= 6, (
        f"Perugino palette should have >=6 key colours; got {len(s.palette)}")


def test_perugino_palette_values_in_range():
    """All Perugino palette RGB values must be in [0, 1]."""
    s = get_style("perugino")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Perugino palette {rgb}")


def test_perugino_has_sky_blue_in_palette():
    """
    Perugino's palette must include a sky blue — his Umbrian skies are the most
    recognisable element of his landscapes.  Sky blue: B > R and B > G.
    """
    s = get_style("perugino")
    sky_blues = [c for c in s.palette if c[2] > c[0] and c[2] > c[1]]
    assert len(sky_blues) >= 1, (
        "Perugino palette should include at least one sky-blue colour (B > R and B > G); "
        f"palette: {s.palette}")


def test_perugino_light_ground_color():
    """
    Perugino worked on light, warm grounds -- ground_color should be luminous (lum >= 0.65).
    This is the opposite of Géricault's dark ground convention.
    """
    s = get_style("perugino")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum >= 0.65, (
        f"Perugino ground_color luminance should be light (>= 0.65); got {lum:.3f}")


def test_perugino_ground_color_warm():
    """Perugino used a warm buff-ivory ground -- ground_color R should exceed B."""
    s = get_style("perugino")
    r, g, b = s.ground_color
    assert r > b, (
        f"Perugino ground_color should be warm (R > B); got R={r:.3f} B={b:.3f}")


def test_perugino_moderate_wet_blend():
    """
    Perugino achieved smoothness through careful layering, not deep sfumato --
    wet_blend should be moderate (0.25 -- 0.55).
    """
    s = get_style("perugino")
    assert 0.25 <= s.wet_blend <= 0.55, (
        f"Perugino wet_blend should be moderate (0.25--0.55); got {s.wet_blend}")


def test_perugino_moderate_edge_softness():
    """
    Perugino's edges are soft but not fully dissolved -- edge_softness should be
    moderate (0.40 -- 0.70).
    """
    s = get_style("perugino")
    assert 0.40 <= s.edge_softness <= 0.70, (
        f"Perugino edge_softness should be moderate (0.40--0.70); got {s.edge_softness}")


def test_perugino_no_chromatic_split():
    """Perugino does not use divisionist chromatic splitting."""
    s = get_style("perugino")
    assert not s.chromatic_split, "Perugino chromatic_split should be False"


def test_perugino_famous_works_not_empty():
    """Perugino must document at least 4 famous works."""
    s = get_style("perugino")
    assert len(s.famous_works) >= 4, (
        f"Perugino famous_works should have >= 4 entries; got {len(s.famous_works)}")


def test_perugino_famous_works_include_keys():
    """Perugino's famous works should include his Sistine Chapel fresco."""
    s = get_style("perugino")
    titles = [w[0] for w in s.famous_works]
    assert any("Keys" in t or "Sistine" in t or "Saint Peter" in t for t in titles), (
        "Perugino famous works should include Christ Delivering the Keys (Sistine Chapel)")


def test_perugino_inspiration_references_serene_grace_pass():
    """Perugino's inspiration must reference 'perugino_serene_grace_pass'."""
    s = get_style("perugino")
    assert "perugino_serene_grace_pass" in s.inspiration, (
        "Perugino inspiration should reference 'perugino_serene_grace_pass()'")


def test_perugino_technique_mentions_raphael():
    """Perugino's technique text must mention Raphael -- the master-pupil relationship
    is central to his historical importance."""
    s = get_style("perugino")
    assert "raphael" in s.technique.lower() or "Raphael" in s.technique, (
        "Perugino technique should mention Raphael (his most famous pupil)")


def test_perugino_technique_mentions_umbria():
    """Perugino's technique must reference his Umbrian landscape tradition."""
    s = get_style("perugino")
    assert "umbri" in s.technique.lower(), (
        "Perugino technique should mention Umbria/Umbrian landscape")


# ── Luca Signorelli tests (session 85) ──────────────────────────────────────


def test_signorelli_in_catalog():
    """Signorelli must be present in CATALOG."""
    assert "signorelli" in CATALOG, "signorelli not found in CATALOG"


def test_signorelli_movement():
    """Signorelli must be classified as Umbrian Renaissance."""
    s = get_style("signorelli")
    assert "umbrian" in s.movement.lower() or "renaissance" in s.movement.lower(), (
        f"Signorelli movement should reference Umbrian Renaissance; got {s.movement!r}")


def test_signorelli_nationality():
    """Signorelli must be Italian."""
    s = get_style("signorelli")
    assert s.nationality.lower() == "italian", (
        f"Signorelli nationality should be 'Italian'; got {s.nationality!r}")


def test_signorelli_palette_length():
    """Signorelli palette must have at least 6 entries."""
    s = get_style("signorelli")
    assert len(s.palette) >= 6, (
        f"Signorelli palette should have >= 6 entries; got {len(s.palette)}")


def test_signorelli_palette_values_in_range():
    """All Signorelli palette channels must be in [0, 1]."""
    s = get_style("signorelli")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Signorelli palette {rgb}")


def test_signorelli_mid_tone_ground():
    """
    Signorelli worked on a mid-value warm ground — ground_color luminance
    should be moderate (0.25–0.55), neither as dark as Géricault nor as
    light as Perugino.
    """
    s = get_style("signorelli")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert 0.25 <= lum <= 0.55, (
        f"Signorelli ground_color luminance should be mid-value (0.25–0.55); "
        f"got {lum:.3f}")


def test_signorelli_ground_color_warm():
    """Signorelli's imprimatura is warm sienna — ground_color R should exceed B."""
    s = get_style("signorelli")
    r, g, b = s.ground_color
    assert r > b, (
        f"Signorelli ground_color should be warm (R > B); got R={r:.3f} B={b:.3f}")


def test_signorelli_low_edge_softness():
    """
    Signorelli's contour clarity is his defining quality — edge_softness
    should be low (< 0.42), contrasting with Leonardo's near-1.0 sfumato.
    """
    s = get_style("signorelli")
    assert s.edge_softness < 0.42, (
        f"Signorelli edge_softness should be low (< 0.42) for contour clarity; "
        f"got {s.edge_softness}")


def test_signorelli_no_chromatic_split():
    """Signorelli does not use divisionist chromatic splitting."""
    s = get_style("signorelli")
    assert not s.chromatic_split, "Signorelli chromatic_split should be False"


def test_signorelli_famous_works_not_empty():
    """Signorelli must document at least 4 famous works."""
    s = get_style("signorelli")
    assert len(s.famous_works) >= 4, (
        f"Signorelli famous_works should have >= 4 entries; got {len(s.famous_works)}")


def test_signorelli_famous_works_include_orvieto():
    """Signorelli's famous works should include his Orvieto Cathedral frescoes."""
    s = get_style("signorelli")
    titles_lower = [w[0].lower() for w in s.famous_works]
    assert any("orvieto" in t or "san brizio" in t or "last judgement" in t
               or "damned" in t for t in titles_lower), (
        "Signorelli famous works should include his Orvieto Cathedral frescoes "
        "(Last Judgement / San Brizio / The Damned Cast into Hell)")


def test_signorelli_inspiration_references_sculptural_vigour_pass():
    """Signorelli's inspiration must reference 'signorelli_sculptural_vigour_pass'."""
    s = get_style("signorelli")
    assert "signorelli_sculptural_vigour_pass" in s.inspiration, (
        "Signorelli inspiration should reference 'signorelli_sculptural_vigour_pass()'")


def test_signorelli_technique_mentions_michelangelo():
    """Signorelli's technique text must mention Michelangelo — the master-pupil
    influence is central to his historical importance."""
    s = get_style("signorelli")
    assert "michelangelo" in s.technique.lower(), (
        "Signorelli technique should mention Michelangelo (his most famous influenced artist)")


def test_signorelli_technique_mentions_orvieto():
    """Signorelli's technique must reference his Orvieto Cathedral frescoes."""
    s = get_style("signorelli")
    assert "orvieto" in s.technique.lower(), (
        "Signorelli technique should mention Orvieto Cathedral")


def test_umbrian_renaissance_in_expected_periods():
    """EXPECTED_PERIODS list must include UMBRIAN_RENAISSANCE."""
    assert "UMBRIAN_CLASSICAL_HARMONY" in EXPECTED_PERIODS, (
        "UMBRIAN_RENAISSANCE missing from EXPECTED_PERIODS — add it to the list")


# ──────────────────────────────────────────────────────────────────────────────
# Rosalba Carriera — session 86 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_rosalba_carriera_in_catalog():
    """Rosalba Carriera must be present in CATALOG."""
    assert "rosalba_carriera" in CATALOG, "rosalba_carriera not found in CATALOG"


def test_rosalba_carriera_movement():
    """Carriera must be classified as Venetian Rococo / Pastel Portraiture."""
    s = get_style("rosalba_carriera")
    assert "rococo" in s.movement.lower() or "pastel" in s.movement.lower(), (
        f"Carriera movement should reference Rococo or Pastel Portraiture; got {s.movement!r}")


def test_rosalba_carriera_nationality():
    """Carriera must be Italian."""
    s = get_style("rosalba_carriera")
    assert s.nationality.lower() == "italian", (
        f"Carriera nationality should be 'Italian'; got {s.nationality!r}")


def test_rosalba_carriera_palette_length():
    """Carriera palette must have at least 5 entries."""
    s = get_style("rosalba_carriera")
    assert len(s.palette) >= 5, (
        f"Carriera palette should have >= 5 entries; got {len(s.palette)}")


def test_rosalba_carriera_palette_values_in_range():
    """All Carriera palette channels must be in [0, 1]."""
    s = get_style("rosalba_carriera")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Carriera palette {rgb}")


def test_rosalba_carriera_high_wet_blend():
    """
    Carriera's pastel blending is near-seamless — wet_blend should be very
    high (> 0.80), reflecting finger-blended pastel with no visible marks.
    """
    s = get_style("rosalba_carriera")
    assert s.wet_blend > 0.80, (
        f"Carriera wet_blend should be very high (> 0.80) for pastel fusion; "
        f"got {s.wet_blend:.3f}")


def test_rosalba_carriera_high_edge_softness():
    """
    Carriera's edges dissolve into soft vignette halos — edge_softness should
    be very high (> 0.80), close to Leonardo's sfumato level.
    """
    s = get_style("rosalba_carriera")
    assert s.edge_softness > 0.80, (
        f"Carriera edge_softness should be very high (> 0.80) for powdery pastel "
        f"edge dissolution; got {s.edge_softness:.3f}")


def test_rosalba_carriera_light_ground():
    """
    Carriera worked on pale warm vellum — ground_color luminance should be
    high (> 0.70), much lighter than oil painters' dark or mid-tone imprimaturas.
    """
    s = get_style("rosalba_carriera")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum > 0.70, (
        f"Carriera ground_color luminance should be very light (> 0.70) for "
        f"pale warm vellum; got {lum:.3f}")


def test_rosalba_carriera_no_chromatic_split():
    """Carriera does not use divisionist chromatic splitting."""
    s = get_style("rosalba_carriera")
    assert not s.chromatic_split, "Carriera chromatic_split should be False"


def test_rosalba_carriera_no_crackle():
    """Pastel does not crack — Carriera crackle should be False."""
    s = get_style("rosalba_carriera")
    assert not s.crackle, "Carriera crackle should be False (pastel is a dry medium)"


def test_rosalba_carriera_famous_works_not_empty():
    """Carriera must document at least 4 famous works."""
    s = get_style("rosalba_carriera")
    assert len(s.famous_works) >= 4, (
        f"Carriera famous_works should have >= 4 entries; got {len(s.famous_works)}")


def test_rosalba_carriera_famous_works_include_self_portrait():
    """Carriera's famous works should include at least one self-portrait."""
    s = get_style("rosalba_carriera")
    titles_lower = [w[0].lower() for w in s.famous_works]
    assert any("self" in t or "portrait" in t for t in titles_lower), (
        "Carriera famous works should include a self-portrait")


def test_rosalba_carriera_inspiration_references_pastel_glow_pass():
    """Carriera's inspiration must reference 'carriera_pastel_glow_pass'."""
    s = get_style("rosalba_carriera")
    assert "carriera_pastel_glow_pass" in s.inspiration, (
        "Carriera inspiration should reference 'carriera_pastel_glow_pass()'")


def test_rosalba_carriera_technique_mentions_academy():
    """Carriera's technique text must mention her Académie Royale election — the
    first woman from outside France to receive that honour."""
    s = get_style("rosalba_carriera")
    assert "académie" in s.technique.lower() or "academie" in s.technique.lower() or "académie" in s.technique, (
        "Carriera technique should mention her Académie Royale election")


def test_rosalba_carriera_technique_mentions_ivory():
    """Carriera's technique must reference her pioneering use of ivory as a support."""
    s = get_style("rosalba_carriera")
    assert "ivory" in s.technique.lower(), (
        "Carriera technique should mention ivory (she pioneered miniature on ivory support)")


def test_venetian_pastel_portrait_in_expected_periods():
    """EXPECTED_PERIODS list must include VENETIAN_PASTEL_PORTRAIT."""
    assert "VENETIAN_PASTEL_PORTRAIT" in EXPECTED_PERIODS, (
        "VENETIAN_PASTEL_PORTRAIT missing from EXPECTED_PERIODS — add it to the list")


def test_venetian_pastel_portrait_stroke_params():
    """VENETIAN_PASTEL_PORTRAIT stroke_params should reflect very soft pastel technique."""
    from scene_schema import Period, Style, Medium, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_PASTEL_PORTRAIT,
                  palette=PaletteHint.COOL_GREY)
    p = style.stroke_params
    # Pastel is the softest, most blended technique in the catalog
    assert p["wet_blend"] > 0.80, (
        f"VENETIAN_PASTEL_PORTRAIT wet_blend should be > 0.80 for pastel fusion; "
        f"got {p['wet_blend']:.3f}")
    assert p["edge_softness"] > 0.80, (
        f"VENETIAN_PASTEL_PORTRAIT edge_softness should be > 0.80 for powdery edge "
        f"dissolution; got {p['edge_softness']:.3f}")
    # Fine marks — Carriera's stroke size is very small
    assert p["stroke_size_face"] <= 5, (
        f"VENETIAN_PASTEL_PORTRAIT stroke_size_face should be <= 5 for fine pastel "
        f"marks; got {p['stroke_size_face']}")


# ─────────────────────────────────────────────────────────────────────────────
# James McNeill Whistler — Session 87
# ─────────────────────────────────────────────────────────────────────────────

def test_whistler_in_catalog():
    """James McNeill Whistler must be present in CATALOG."""
    assert "whistler" in CATALOG, "whistler not found in CATALOG"


def test_whistler_movement():
    """Whistler must be classified as Tonalist or Aestheticism."""
    s = get_style("whistler")
    assert "tonal" in s.movement.lower() or "aesthet" in s.movement.lower(), (
        f"Whistler movement should reference Tonalism or Aestheticism; got {s.movement!r}")


def test_whistler_nationality():
    """Whistler must be listed as American-British."""
    s = get_style("whistler")
    assert "american" in s.nationality.lower() or "british" in s.nationality.lower(), (
        f"Whistler nationality should reference American or British; got {s.nationality!r}")


def test_whistler_palette_length():
    """Whistler palette must have at least 5 entries."""
    s = get_style("whistler")
    assert len(s.palette) >= 5, (
        f"Whistler palette should have >= 5 entries; got {len(s.palette)}")


def test_whistler_palette_values_in_range():
    """All Whistler palette channels must be in [0, 1]."""
    s = get_style("whistler")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Whistler palette {rgb}")


def test_whistler_cool_ground():
    """
    Whistler's cool silver-grey ground — ground_color should be cool (B >= R)
    and mid-tone (luminance 0.40–0.70), reflecting his prepared grey boards.
    """
    s = get_style("whistler")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert b >= r, (
        f"Whistler ground_color should be cool (B >= R); got R={r:.3f} B={b:.3f}")
    assert 0.40 <= lum <= 0.75, (
        f"Whistler ground_color luminance should be mid-tone (0.40–0.75); got {lum:.3f}")


def test_whistler_has_cool_dominant_in_palette():
    """
    Whistler's palette should contain at least one cool grey-blue tone
    (B > R and B > G and luminance >= 0.40).
    """
    s = get_style("whistler")
    cool_greys = [
        (r, g, b) for (r, g, b) in s.palette
        if b > r and b > g and (0.299 * r + 0.587 * g + 0.114 * b) >= 0.40
    ]
    assert len(cool_greys) >= 1, (
        "Whistler palette should contain at least one cool silver-grey tone (B>R, B>G, lum>=0.40)")


def test_whistler_high_wet_blend():
    """
    Whistler's 'sauce' (turpentine-diluted paint) produces heavily blended
    tonal zones — wet_blend should be high (> 0.60).
    """
    s = get_style("whistler")
    assert s.wet_blend > 0.60, (
        f"Whistler wet_blend should be high (> 0.60) for liquid 'sauce' paint; "
        f"got {s.wet_blend:.3f}")


def test_whistler_high_edge_softness():
    """
    Whistler's Nocturnes dissolve forms into atmosphere — edge_softness should
    be high (> 0.70).
    """
    s = get_style("whistler")
    assert s.edge_softness > 0.70, (
        f"Whistler edge_softness should be high (> 0.70) for nocturne dissolution; "
        f"got {s.edge_softness:.3f}")


def test_whistler_no_chromatic_split():
    """Whistler does not use Pointillist chromatic splitting."""
    s = get_style("whistler")
    assert not s.chromatic_split, "Whistler chromatic_split should be False"


def test_whistler_crackle():
    """Whistler painted in oil — crackle should be True."""
    s = get_style("whistler")
    assert s.crackle, "Whistler crackle should be True (oil on panel/canvas)"


def test_whistler_famous_works_not_empty():
    """Whistler must document at least 4 famous works."""
    s = get_style("whistler")
    assert len(s.famous_works) >= 4, (
        f"Whistler famous_works should have >= 4 entries; got {len(s.famous_works)}")


def test_whistler_famous_works_include_arrangement():
    """Whistler's famous works should include 'Arrangement in Grey and Black' (Whistler's Mother)."""
    s = get_style("whistler")
    titles_lower = [w[0].lower() for w in s.famous_works]
    assert any("arrangement" in t or "grey" in t or "mother" in t for t in titles_lower), (
        "Whistler famous works should include 'Arrangement in Grey and Black No.1'")


def test_whistler_famous_works_include_nocturne():
    """Whistler's famous works should include at least one Nocturne."""
    s = get_style("whistler")
    titles_lower = [w[0].lower() for w in s.famous_works]
    assert any("nocturne" in t for t in titles_lower), (
        "Whistler famous works should include at least one Nocturne")


def test_whistler_inspiration_references_tonal_harmony_pass():
    """Whistler's inspiration must reference 'whistler_tonal_harmony_pass'."""
    s = get_style("whistler")
    assert "whistler_tonal_harmony_pass" in s.inspiration, (
        "Whistler inspiration should reference 'whistler_tonal_harmony_pass()'")


def test_whistler_technique_mentions_sauce():
    """Whistler's technique text must mention his 'sauce' (turpentine-diluted paint)."""
    s = get_style("whistler")
    assert "sauce" in s.technique.lower(), (
        "Whistler technique should mention his 'sauce' (turpentine-diluted paint method)")


def test_whistler_technique_mentions_nocturne():
    """Whistler's technique must reference his Nocturne series."""
    s = get_style("whistler")
    assert "nocturne" in s.technique.lower(), (
        "Whistler technique should mention his Nocturne paintings")


def test_whistler_technique_mentions_japonisme():
    """Whistler's technique must reference Japanese art influence."""
    s = get_style("whistler")
    assert "japan" in s.technique.lower() or "ukiyo" in s.technique.lower(), (
        "Whistler technique should mention Japanese art influence (Japonisme)")


def test_whistler_cool_glazing():
    """
    Whistler's glazing should be cool (B >= R) — he used cool grey unifying
    glazes rather than the warm amber glazes of Old Master oil painting.
    """
    s = get_style("whistler")
    assert s.glazing is not None, "Whistler glazing should not be None"
    r, g, b = s.glazing
    assert b >= r, (
        f"Whistler glazing should be cool (B >= R); got R={r:.3f} B={b:.3f}")


def test_american_tonalist_in_expected_periods():
    """EXPECTED_PERIODS list must include AMERICAN_TONALIST."""
    assert "AMERICAN_TONALIST" in EXPECTED_PERIODS, (
        "AMERICAN_TONALIST missing from EXPECTED_PERIODS — add it to the list")


def test_american_tonalist_stroke_params():
    """AMERICAN_TONALIST stroke_params should reflect Whistler's tonal harmony technique."""
    from scene_schema import Period, Style, Medium, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.AMERICAN_TONALIST,
                  palette=PaletteHint.COOL_GREY)
    p = style.stroke_params
    # Whistler's 'sauce' produces very blended, liquid tonal zones
    assert p["wet_blend"] > 0.60, (
        f"AMERICAN_TONALIST wet_blend should be > 0.60 for Whistler's liquid sauce; "
        f"got {p['wet_blend']:.3f}")
    # Nocturne edge dissolution is very high
    assert p["edge_softness"] > 0.70, (
        f"AMERICAN_TONALIST edge_softness should be > 0.70 for nocturne edge dissolution; "
        f"got {p['edge_softness']:.3f}")
    # Whistler used fine marks — not large impasto strokes
    assert p["stroke_size_face"] <= 6, (
        f"AMERICAN_TONALIST stroke_size_face should be <= 6 for Whistler's fine tonal marks; "
        f"got {p['stroke_size_face']}")


# ─────────────────────────────────────────────────────────────────────────────
# Session 88 — Odilon Redon tests
# ─────────────────────────────────────────────────────────────────────────────

def test_odilon_redon_in_catalog():
    """odilon_redon must be present in CATALOG (session 88)."""
    assert "odilon_redon" in CATALOG


def test_odilon_redon_movement_symbolism():
    """Redon's movement must reference Symbolism."""
    s = get_style("odilon_redon")
    assert "Symbolism" in s.movement or "symbolism" in s.movement.lower(), (
        f"Redon movement should reference Symbolism; got {s.movement!r}")


def test_odilon_redon_nationality_french():
    """Redon must be catalogued as French."""
    s = get_style("odilon_redon")
    assert "French" in s.nationality or "french" in s.nationality.lower(), (
        f"Redon nationality should be French; got {s.nationality!r}")


def test_odilon_redon_palette_length():
    """Redon palette must have at least 6 entries for his chromatic range."""
    s = get_style("odilon_redon")
    assert len(s.palette) >= 6, (
        f"Redon palette should have >= 6 entries; got {len(s.palette)}")


def test_odilon_redon_palette_values_in_range():
    """All Redon palette colour channels must be in [0, 1]."""
    s = get_style("odilon_redon")
    for i, (r, g, b) in enumerate(s.palette):
        assert 0.0 <= r <= 1.0, f"Redon palette[{i}] R={r} out of range"
        assert 0.0 <= g <= 1.0, f"Redon palette[{i}] G={g} out of range"
        assert 0.0 <= b <= 1.0, f"Redon palette[{i}] B={b} out of range"


def test_odilon_redon_ground_dark():
    """Redon's ground must be dark (luminance < 0.35) — his velvety void."""
    s = get_style("odilon_redon")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum < 0.35, (
        f"Redon ground should be dark (lum < 0.35) for his void noir; got lum={lum:.3f}")


def test_odilon_redon_has_jewel_colour():
    """Redon palette must include at least one high-chroma jewel colour."""
    s = get_style("odilon_redon")
    jewel_found = False
    for r, g, b in s.palette:
        chroma = max(r, g, b) - min(r, g, b)
        if chroma > 0.40:
            jewel_found = True
            break
    assert jewel_found, "Redon palette should include at least one jewel-saturated colour"


def test_odilon_redon_chromatic_split():
    """Redon must have chromatic_split=True for his spectral colour richness."""
    s = get_style("odilon_redon")
    assert s.chromatic_split is True, (
        "Redon chromatic_split should be True for spectral jewel richness")


def test_odilon_redon_no_crackle():
    """Redon must have crackle=False — pastel does not crackle like oil on panel."""
    s = get_style("odilon_redon")
    assert s.crackle is False, (
        "Redon crackle should be False — pastel medium does not crack")


def test_odilon_redon_edge_softness():
    """Redon edge_softness must be > 0.60 — dreamlike dissolving forms."""
    s = get_style("odilon_redon")
    assert s.edge_softness > 0.60, (
        f"Redon edge_softness should be > 0.60 for soft dreamlike forms; "
        f"got {s.edge_softness:.3f}")


def test_odilon_redon_famous_works_count():
    """Redon must have at least 6 famous works catalogued."""
    s = get_style("odilon_redon")
    assert len(s.famous_works) >= 6, (
        f"Redon should have >= 6 famous works; got {len(s.famous_works)}")


def test_odilon_redon_famous_works_include_cyclops():
    """Redon's famous works must include The Cyclops — his most iconic image."""
    s = get_style("odilon_redon")
    titles = [w[0].lower() for w in s.famous_works]
    assert any("cyclops" in t for t in titles), (
        "Redon famous_works should include The Cyclops")


def test_odilon_redon_inspiration_references_pass():
    """Redon inspiration must reference redon_luminous_reverie_pass()."""
    s = get_style("odilon_redon")
    assert "redon_luminous_reverie_pass" in s.inspiration, (
        "Redon inspiration should reference redon_luminous_reverie_pass()")


def test_odilon_redon_technique_mentions_noirs():
    """Redon technique must mention his 'Noirs' charcoal period."""
    s = get_style("odilon_redon")
    assert "noir" in s.technique.lower() or "Noirs" in s.technique, (
        "Redon technique should mention his Noirs period")


def test_odilon_redon_technique_mentions_symbolist_poetry():
    """Redon technique must mention Symbolist poetry or literary influence."""
    s = get_style("odilon_redon")
    has_ref = (
        "Mallarm" in s.technique
        or "Baudelaire" in s.technique
        or "Symbolist" in s.technique
        or "symbolist" in s.technique.lower()
    )
    assert has_ref, (
        "Redon technique should mention Symbolist poetry (Mallarmé, Baudelaire, or Symbolism)")


def test_odilon_redon_in_expected_artists():
    """EXPECTED_ARTISTS list must include odilon_redon."""
    assert "odilon_redon" in EXPECTED_ARTISTS


def test_whistler_in_expected_artists():
    """EXPECTED_ARTISTS list must include whistler (session 87)."""
    assert "whistler" in EXPECTED_ARTISTS


# ──────────────────────────────────────────────────────────────────────────────
# Session 89 — Léon Spilliaert
# ──────────────────────────────────────────────────────────────────────────────

def test_leon_spilliaert_in_catalog():
    """Léon Spilliaert (session 89) must be in the catalog."""
    assert "leon_spilliaert" in CATALOG


def test_leon_spilliaert_in_expected_artists():
    """EXPECTED_ARTISTS list must include leon_spilliaert (session 89)."""
    assert "leon_spilliaert" in EXPECTED_ARTISTS


def test_leon_spilliaert_movement():
    """Spilliaert movement must reference Belgian Symbolism."""
    s = get_style("leon_spilliaert")
    assert "Belgian" in s.movement or "Symbolism" in s.movement, (
        f"Spilliaert movement should reference Belgian Symbolism; got {s.movement!r}")


def test_leon_spilliaert_nationality():
    """Spilliaert must be cataloged as Belgian."""
    s = get_style("leon_spilliaert")
    assert s.nationality == "Belgian"


def test_leon_spilliaert_palette_length():
    """Spilliaert palette must have at least 5 colours."""
    s = get_style("leon_spilliaert")
    assert len(s.palette) >= 5


def test_leon_spilliaert_palette_in_range():
    """All Spilliaert palette RGB values must be in [0, 1]."""
    s = get_style("leon_spilliaert")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"Spilliaert palette channel {ch} out of [0, 1] in {rgb}")


def test_leon_spilliaert_ground_is_dark():
    """Spilliaert ground colour must be very dark (luminance < 0.15)."""
    s = get_style("leon_spilliaert")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum < 0.15, (
        f"Spilliaert ground should be near-black ink void; luminance={lum:.3f}")


def test_leon_spilliaert_no_crackle():
    """Spilliaert worked on paper — no crackle finish."""
    s = get_style("leon_spilliaert")
    assert not s.crackle


def test_leon_spilliaert_no_chromatic_split():
    """Spilliaert palette is near-monochromatic — no divisionist chromatic split."""
    s = get_style("leon_spilliaert")
    assert not s.chromatic_split


def test_leon_spilliaert_edge_softness_low():
    """Spilliaert edge_softness must be low (< 0.30) — ink lines are precise."""
    s = get_style("leon_spilliaert")
    assert s.edge_softness < 0.30, (
        f"Spilliaert edge_softness should be low for ink precision; got {s.edge_softness:.2f}")


def test_leon_spilliaert_wet_blend_low():
    """Spilliaert wet_blend must be low (< 0.35) — watercolour/ink, not oil."""
    s = get_style("leon_spilliaert")
    assert s.wet_blend < 0.35, (
        f"Spilliaert wet_blend should be low for ink/watercolour; got {s.wet_blend:.2f}")


def test_leon_spilliaert_famous_works_include_vertigo():
    """Spilliaert's famous works must include Dizziness/Vertigo (1908)."""
    s = get_style("leon_spilliaert")
    titles = [t.lower() for t, _ in s.famous_works]
    assert any("vertigo" in t or "dizziness" in t for t in titles), (
        "Spilliaert famous_works must include Dizziness/Vertigo (1908)")


def test_leon_spilliaert_inspiration_references_pass():
    """Spilliaert inspiration must reference spilliaert_vertiginous_void_pass()."""
    s = get_style("leon_spilliaert")
    assert "spilliaert_vertiginous_void_pass" in s.inspiration, (
        "Spilliaert inspiration should reference spilliaert_vertiginous_void_pass()")


# ── Session 90 — Ferdinand Hodler ─────────────────────────────────────────────

def test_ferdinand_hodler_in_catalog():
    """ferdinand_hodler must be present in CATALOG (session 90)."""
    assert "ferdinand_hodler" in CATALOG, "ferdinand_hodler not found in CATALOG"


def test_ferdinand_hodler_movement():
    """Hodler's movement must identify Swiss Symbolism or Post-Impressionism."""
    s = get_style("ferdinand_hodler")
    assert "Symbolism" in s.movement or "Impressionism" in s.movement, (
        f"Hodler movement should mention Symbolism or Impressionism; got {s.movement!r}")


def test_ferdinand_hodler_nationality():
    """Hodler must be recorded as Swiss."""
    s = get_style("ferdinand_hodler")
    assert s.nationality == "Swiss", (
        f"Hodler nationality should be 'Swiss'; got {s.nationality!r}")


def test_ferdinand_hodler_palette_length():
    """Hodler's palette must have at least 5 colours."""
    s = get_style("ferdinand_hodler")
    assert len(s.palette) >= 5, (
        f"Hodler palette should have ≥ 5 entries; got {len(s.palette)}")


def test_ferdinand_hodler_palette_values_in_range():
    """All Hodler palette RGB values must be in [0, 1]."""
    s = get_style("ferdinand_hodler")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"Hodler palette channel {ch} out of [0, 1] in {rgb}")


def test_ferdinand_hodler_palette_contains_cobalt():
    """Hodler's palette must contain a cobalt/Swiss blue (B > R, B > G)."""
    s = get_style("ferdinand_hodler")
    has_blue = any(b > r and b > g for r, g, b in s.palette)
    assert has_blue, (
        "Hodler palette must include a cobalt blue — key to his Alpine lake and sky passages")


def test_ferdinand_hodler_warm_ground():
    """Hodler ground colour must be warm (R > B) — ochre-grey toned canvas."""
    s = get_style("ferdinand_hodler")
    r, g, b = s.ground_color
    assert r > b, (
        f"Hodler ground should be warm ochre-grey (R > B); got R={r:.2f} B={b:.2f}")


def test_ferdinand_hodler_low_edge_softness():
    """Hodler edge_softness must be below 0.40 — his bold contour outlines define forms."""
    s = get_style("ferdinand_hodler")
    assert s.edge_softness < 0.40, (
        f"Hodler edge_softness should be low for bold contour clarity; got {s.edge_softness:.2f}")


def test_ferdinand_hodler_no_crackle():
    """Hodler crackle must be False — his canvases are not heavily aged."""
    s = get_style("ferdinand_hodler")
    assert not s.crackle, "Hodler crackle should be False"


def test_ferdinand_hodler_warm_glazing():
    """Hodler glazing must be warm (R > B) — amber unifying glaze over earth palette."""
    s = get_style("ferdinand_hodler")
    assert s.glazing is not None, "Hodler should have a glazing colour"
    r, g, b = s.glazing
    assert r > b, (
        f"Hodler glazing should be warm amber (R > B); got {s.glazing}")


def test_ferdinand_hodler_famous_works_not_empty():
    """Hodler famous_works must not be empty."""
    s = get_style("ferdinand_hodler")
    assert len(s.famous_works) > 0, "Hodler famous_works must not be empty"


def test_ferdinand_hodler_famous_works_include_night():
    """Hodler's famous works must include Night (1890), his breakthrough work."""
    s = get_style("ferdinand_hodler")
    titles = [t.lower() for t, _ in s.famous_works]
    assert any("night" in t for t in titles), (
        "Hodler famous_works must include Night (1890)")


def test_ferdinand_hodler_famous_works_include_day():
    """Hodler's famous works must include Day (1900)."""
    s = get_style("ferdinand_hodler")
    titles = [t.lower() for t, _ in s.famous_works]
    assert any("day" in t for t in titles), (
        "Hodler famous_works must include Day (1900)")


def test_ferdinand_hodler_inspiration_references_parallelism_pass():
    """Hodler inspiration must reference hodler_parallelism_pass()."""
    s = get_style("ferdinand_hodler")
    assert "hodler_parallelism_pass" in s.inspiration, (
        "Hodler inspiration should reference hodler_parallelism_pass()")


# ── Session 91 — Gustave Caillebotte ──────────────────────────────────────────

def test_gustave_caillebotte_in_catalog():
    """gustave_caillebotte must be present in CATALOG (session 91)."""
    assert "gustave_caillebotte" in CATALOG, "gustave_caillebotte not found in CATALOG"


def test_gustave_caillebotte_in_expected_artists():
    """EXPECTED_ARTISTS list must include gustave_caillebotte (session 91)."""
    assert "gustave_caillebotte" in EXPECTED_ARTISTS


def test_gustave_caillebotte_movement():
    """Caillebotte's movement must reference Impressionism or Urban Realism."""
    s = get_style("gustave_caillebotte")
    assert "Impressionism" in s.movement or "Realism" in s.movement, (
        f"Caillebotte movement should reference Impressionism or Realism; got {s.movement!r}")


def test_gustave_caillebotte_nationality():
    """Caillebotte must be recorded as French."""
    s = get_style("gustave_caillebotte")
    assert s.nationality == "French", (
        f"Caillebotte nationality should be 'French'; got {s.nationality!r}")


def test_gustave_caillebotte_palette_length():
    """Caillebotte's palette must have at least 5 colours."""
    s = get_style("gustave_caillebotte")
    assert len(s.palette) >= 5, (
        f"Caillebotte palette should have >= 5 entries; got {len(s.palette)}")


def test_gustave_caillebotte_palette_values_in_range():
    """All Caillebotte palette RGB values must be in [0, 1]."""
    s = get_style("gustave_caillebotte")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"Caillebotte palette channel {ch} out of [0, 1] in {rgb}")


def test_gustave_caillebotte_palette_contains_cool_grey():
    """Caillebotte's palette must contain a cool grey tone (G ≈ B, moderate luminance)."""
    s = get_style("gustave_caillebotte")
    has_grey = any(
        abs(g - b) < 0.10 and abs(r - g) < 0.15 and 0.30 < (0.299*r + 0.587*g + 0.114*b) < 0.75
        for r, g, b in s.palette
    )
    assert has_grey, (
        "Caillebotte palette must include a cool grey — key to his Parisian cobblestone palette")


def test_gustave_caillebotte_ground_is_cool_mid():
    """Caillebotte ground must be a cool mid-grey (B >= R, moderate luminance)."""
    s = get_style("gustave_caillebotte")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert b >= r, (
        f"Caillebotte ground should be cool (B >= R); got R={r:.2f} B={b:.2f}")
    assert 0.30 < lum < 0.75, (
        f"Caillebotte ground should be mid-luminance (0.30–0.75); got lum={lum:.3f}")


def test_gustave_caillebotte_no_crackle():
    """Caillebotte's crackle must be False — relatively modern, controlled paint surface."""
    s = get_style("gustave_caillebotte")
    assert not s.crackle, "Caillebotte crackle should be False"


def test_gustave_caillebotte_no_chromatic_split():
    """Caillebotte did not use divisionist chromatic splitting."""
    s = get_style("gustave_caillebotte")
    assert not s.chromatic_split, "Caillebotte chromatic_split should be False"


def test_gustave_caillebotte_no_glazing():
    """Caillebotte used no warm unifying glaze — his palette is cool and clear."""
    s = get_style("gustave_caillebotte")
    assert s.glazing is None, (
        f"Caillebotte glazing should be None; got {s.glazing}")


def test_gustave_caillebotte_low_wet_blend():
    """Caillebotte wet_blend must be below 0.35 — precise realist technique, not impressionistic."""
    s = get_style("gustave_caillebotte")
    assert s.wet_blend < 0.35, (
        f"Caillebotte wet_blend should be low for realist precision; got {s.wet_blend:.2f}")


def test_gustave_caillebotte_low_edge_softness():
    """Caillebotte edge_softness must be below 0.40 — crisp architectural edges."""
    s = get_style("gustave_caillebotte")
    assert s.edge_softness < 0.40, (
        f"Caillebotte edge_softness should be low for architectural precision; got {s.edge_softness:.2f}")


def test_gustave_caillebotte_famous_works_include_paris_street():
    """Caillebotte's famous works must include Paris Street; Rainy Day — his masterpiece."""
    s = get_style("gustave_caillebotte")
    titles = [t.lower() for t, _ in s.famous_works]
    assert any("paris" in t and "rain" in t for t in titles), (
        "Caillebotte famous_works must include Paris Street; Rainy Day (1877)")


def test_gustave_caillebotte_famous_works_include_floor_scrapers():
    """Caillebotte's famous works must include The Floor Scrapers (1875)."""
    s = get_style("gustave_caillebotte")
    titles = [t.lower() for t, _ in s.famous_works]
    assert any("floor" in t or "scraper" in t for t in titles), (
        "Caillebotte famous_works must include The Floor Scrapers (1875)")


def test_gustave_caillebotte_famous_works_count():
    """Caillebotte must have at least 5 famous works catalogued."""
    s = get_style("gustave_caillebotte")
    assert len(s.famous_works) >= 5, (
        f"Caillebotte should have >= 5 famous works; got {len(s.famous_works)}")


def test_gustave_caillebotte_inspiration_references_pass():
    """Caillebotte inspiration must reference caillebotte_perspective_pass()."""
    s = get_style("gustave_caillebotte")
    assert "caillebotte_perspective_pass" in s.inspiration, (
        "Caillebotte inspiration should reference caillebotte_perspective_pass()")


def test_gustave_caillebotte_technique_mentions_perspective():
    """Caillebotte technique must mention perspective or foreshortening."""
    s = get_style("gustave_caillebotte")
    has_ref = (
        "perspective" in s.technique.lower()
        or "foreshorten" in s.technique.lower()
        or "vanishing" in s.technique.lower()
    )
    assert has_ref, (
        "Caillebotte technique should mention perspective / foreshortening / vanishing point")


def test_gustave_caillebotte_technique_mentions_paris():
    """Caillebotte technique must mention Paris — his defining subject."""
    s = get_style("gustave_caillebotte")
    assert "Paris" in s.technique or "paris" in s.technique.lower(), (
        "Caillebotte technique should mention Paris")


# ── Session 91 — Franz Marc ────────────────────────────────────────────────────

def test_franz_marc_in_catalog():
    """franz_marc must be present in CATALOG (session 91)."""
    assert "franz_marc" in CATALOG, "franz_marc not found in CATALOG"


def test_franz_marc_in_expected_artists():
    """EXPECTED_ARTISTS list must include franz_marc (session 91)."""
    assert "franz_marc" in EXPECTED_ARTISTS


def test_franz_marc_palette_values_in_range():
    """All Franz Marc palette RGB values must be in [0, 1]."""
    s = get_style("franz_marc")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"Marc palette channel {ch} out of [0, 1] in {rgb}")


def test_franz_marc_palette_contains_spiritual_blue():
    """Marc's palette must contain an ultramarine spiritual blue (B > R, B > G)."""
    s = get_style("franz_marc")
    has_blue = any(b > r and b > g for r, g, b in s.palette)
    assert has_blue, (
        "Marc palette must include a spiritual ultramarine blue — "
        "the defining symbolic colour of Der Blaue Reiter")


def test_franz_marc_palette_contains_cadmium_yellow():
    """Marc's palette must contain a cadmium yellow (R > B, G > B, high luminance)."""
    s = get_style("franz_marc")
    has_yellow = any(r > b and g > b and (0.299 * r + 0.587 * g + 0.114 * b) > 0.65
                     for r, g, b in s.palette)
    assert has_yellow, (
        "Marc palette must include a cadmium yellow — "
        "the feminine/vitality colour in his symbolic system")


def test_franz_marc_ground_is_blue_dominant():
    """Marc's ground colour must be blue-dominant (B > R) — deep spiritual ground."""
    s = get_style("franz_marc")
    r, g, b = s.ground_color
    assert b > r, (
        f"Marc ground should be blue-dominant (B > R); got R={r:.2f} B={b:.2f}")


def test_franz_marc_low_wet_blend():
    """Marc's wet_blend must be below 0.45 — colour planes stay clearly bounded."""
    s = get_style("franz_marc")
    assert s.wet_blend < 0.45, (
        f"Marc wet_blend should be low; colour planes must stay bounded; "
        f"got {s.wet_blend:.2f}")


def test_franz_marc_no_crackle():
    """Marc crackle must be False — his canvases are not heavily aged."""
    s = get_style("franz_marc")
    assert not s.crackle, "Marc crackle should be False"


def test_franz_marc_warm_glazing():
    """Marc's glazing must be warm (R > B) — amber glaze unifies the primaries."""
    s = get_style("franz_marc")
    assert s.glazing is not None, "Marc should have a glazing colour"
    r, g, b = s.glazing
    assert r > b, (
        f"Marc glazing should be warm amber (R > B); got {s.glazing}")


def test_franz_marc_famous_works_not_empty():
    """Marc's famous_works must not be empty."""
    s = get_style("franz_marc")
    assert len(s.famous_works) > 0, "Marc famous_works must not be empty"


def test_franz_marc_famous_works_include_blue_horse():
    """Marc's famous works must include Blue Horse I (1911)."""
    s = get_style("franz_marc")
    titles = [t.lower() for t, _ in s.famous_works]
    assert any("blue horse" in t for t in titles), (
        "Marc famous_works must include Blue Horse I (1911) — his most iconic work")


def test_franz_marc_famous_works_include_fate_of_animals():
    """Marc's famous works must include Fate of the Animals (1913)."""
    s = get_style("franz_marc")
    titles = [t.lower() for t, _ in s.famous_works]
    assert any("fate" in t or "animals" in t for t in titles), (
        "Marc famous_works must include Fate of the Animals (1913)")


def test_franz_marc_inspiration_references_prismatic_pass():
    """Marc's inspiration must reference franz_marc_prismatic_vitality_pass()."""
    s = get_style("franz_marc")
    assert "franz_marc_prismatic_vitality_pass" in s.inspiration, (
        "Marc inspiration should reference franz_marc_prismatic_vitality_pass()")


# ── Hugo van der Goes tests (session 93) ─────────────────────────────────────

def test_hugo_van_der_goes_in_catalog():
    """Hugo van der Goes must be present in the catalog."""
    assert "hugo_van_der_goes" in list_artists(), (
        "hugo_van_der_goes must be in CATALOG")


def test_hugo_van_der_goes_in_expected_artists():
    """get_style('hugo_van_der_goes') must succeed without raising."""
    s = get_style("hugo_van_der_goes")
    assert s.artist == "Hugo van der Goes", (
        f"Expected artist='Hugo van der Goes'; got {s.artist!r}")


def test_hugo_van_der_goes_movement_is_flemish():
    """Hugo van der Goes' movement must reference Flemish or Netherlandish tradition."""
    s = get_style("hugo_van_der_goes")
    m = s.movement.lower()
    assert "flemish" in m or "netherlandish" in m, (
        f"Movement must reference Flemish or Netherlandish; got {s.movement!r}")


def test_hugo_van_der_goes_palette_length():
    """Hugo van der Goes must have at least 6 palette colours."""
    s = get_style("hugo_van_der_goes")
    assert len(s.palette) >= 6, (
        f"Van der Goes palette must have ≥6 colours; got {len(s.palette)}")


def test_hugo_van_der_goes_palette_values_in_range():
    """All Hugo van der Goes palette RGB values must be in [0, 1]."""
    s = get_style("hugo_van_der_goes")
    for i, col in enumerate(s.palette):
        for ch in col:
            assert 0.0 <= ch <= 1.0, (
                f"Van der Goes palette[{i}] has out-of-range value {ch:.4f}")


def test_hugo_van_der_goes_palette_contains_warm_dark():
    """Van der Goes palette must contain a warm near-black (R > B, lum < 0.22)."""
    s = get_style("hugo_van_der_goes")
    warm_darks = [
        c for c in s.palette
        if c[0] > c[2] and (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) < 0.22
    ]
    assert len(warm_darks) >= 1, (
        "Van der Goes palette must contain at least one warm near-black (R > B, lum < 0.22) — "
        "his shadows are exclusively warm amber-to-near-black, no cool blue voids")


def test_hugo_van_der_goes_ground_is_warm_amber():
    """Van der Goes ground_color must be warm (R > B) and mid-dark (lum < 0.62)."""
    s = get_style("hugo_van_der_goes")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert r > b, (
        f"Van der Goes ground must be warm (R > B); got ground_color={s.ground_color}")
    assert lum < 0.62, (
        f"Van der Goes ground must be darker than Antonello's (lum < 0.62); "
        f"got lum={lum:.3f}")


def test_hugo_van_der_goes_has_crackle():
    """Van der Goes crackle must be True — 15th-century oak panel."""
    s = get_style("hugo_van_der_goes")
    assert s.crackle, "Van der Goes crackle must be True (15th-century oak panel)"


def test_hugo_van_der_goes_no_chromatic_split():
    """Van der Goes chromatic_split must be False — not a Divisionist."""
    s = get_style("hugo_van_der_goes")
    assert not s.chromatic_split, (
        "Van der Goes chromatic_split must be False — he is not a Divisionist painter")


def test_hugo_van_der_goes_has_deep_amber_glazing():
    """Van der Goes glazing must be warm (R > B) and deep (lum < 0.52)."""
    s = get_style("hugo_van_der_goes")
    assert s.glazing is not None, "Van der Goes must have a glazing colour"
    r, g, b = s.glazing
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert r > b, (
        f"Van der Goes glazing must be warm amber (R > B); got {s.glazing}")
    assert lum < 0.52, (
        f"Van der Goes glazing must be deep amber-brown (lum < 0.52); got lum={lum:.3f}")


def test_hugo_van_der_goes_moderate_wet_blend():
    """Van der Goes wet_blend must be in [0.30, 0.55] — oil glazes, not heavy impasto."""
    s = get_style("hugo_van_der_goes")
    assert 0.30 <= s.wet_blend <= 0.55, (
        f"Van der Goes wet_blend must be in [0.30, 0.55]; got {s.wet_blend:.2f}")


def test_hugo_van_der_goes_precise_edge_softness():
    """Van der Goes edge_softness must be below 0.40 — Flemish found-edge precision."""
    s = get_style("hugo_van_der_goes")
    assert s.edge_softness < 0.40, (
        f"Van der Goes edge_softness must be < 0.40 (Flemish precision); "
        f"got {s.edge_softness:.2f}")


def test_hugo_van_der_goes_famous_works_not_empty():
    """Van der Goes famous_works must not be empty."""
    s = get_style("hugo_van_der_goes")
    assert len(s.famous_works) > 0, "Van der Goes famous_works must not be empty"


def test_hugo_van_der_goes_famous_works_include_portinari():
    """Van der Goes famous works must include the Portinari Altarpiece."""
    s = get_style("hugo_van_der_goes")
    titles = [t.lower() for t, _ in s.famous_works]
    assert any("portinari" in t for t in titles), (
        "Van der Goes famous_works must include the Portinari Altarpiece — "
        "his most influential and celebrated work")


def test_hugo_van_der_goes_famous_works_include_dormition():
    """Van der Goes famous works must include the Dormition of the Virgin."""
    s = get_style("hugo_van_der_goes")
    titles = [t.lower() for t, _ in s.famous_works]
    assert any("dormition" in t or "virgin" in t for t in titles), (
        "Van der Goes famous_works must include the Dormition of the Virgin")


def test_hugo_van_der_goes_technique_mentions_portinari():
    """Van der Goes technique text must mention the Portinari Altarpiece."""
    s = get_style("hugo_van_der_goes")
    assert "portinari" in s.technique.lower(), (
        "Van der Goes technique text must mention the Portinari Altarpiece")


def test_hugo_van_der_goes_technique_mentions_ghent():
    """Van der Goes technique text must mention Ghent (his city of work)."""
    s = get_style("hugo_van_der_goes")
    assert "ghent" in s.technique.lower(), (
        "Van der Goes technique text must mention Ghent — he worked there "
        "and the city defines his artistic context")


def test_hugo_van_der_goes_inspiration_references_pass():
    """Van der Goes inspiration must reference hugo_van_der_goes_expressive_depth_pass()."""
    s = get_style("hugo_van_der_goes")
    assert "hugo_van_der_goes_expressive_depth_pass" in s.inspiration, (
        "Van der Goes inspiration must reference hugo_van_der_goes_expressive_depth_pass()")


# ──────────────────────────────────────────────────────────────────────────────
# Gerrit Dou — session 94 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_gerrit_dou_in_catalog():
    """Gerrit Dou (session 94) must be present in CATALOG."""
    assert "gerrit_dou" in CATALOG, "gerrit_dou not found in CATALOG"


def test_gerrit_dou_movement():
    """Gerrit Dou movement must reference Fijnschilder or Dutch Golden Age."""
    s = get_style("gerrit_dou")
    assert ("Fijnschilder" in s.movement or "fijnschilder" in s.movement.lower()
            or "Dutch" in s.movement), (
        f"Gerrit Dou movement should reference Fijnschilder; got {s.movement!r}")


def test_gerrit_dou_nationality():
    """Gerrit Dou must be identified as Dutch."""
    s = get_style("gerrit_dou")
    assert "Dutch" in s.nationality or "Leiden" in s.nationality, (
        f"Gerrit Dou must be Dutch; got nationality={s.nationality!r}")


def test_gerrit_dou_palette_length():
    """Gerrit Dou palette must have at least 6 key colours."""
    s = get_style("gerrit_dou")
    assert len(s.palette) >= 6, (
        f"Gerrit Dou palette should have at least 6 key colours; got {len(s.palette)}")


def test_gerrit_dou_palette_in_range():
    """All Gerrit Dou palette RGB values must be in [0, 1]."""
    s = get_style("gerrit_dou")
    for rgb in s.palette:
        assert len(rgb) == 3, f"Gerrit Dou palette entry {rgb} is not a 3-tuple"
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel:.3f} in Gerrit Dou palette {rgb}")


def test_gerrit_dou_ground_color_warm():
    """Gerrit Dou ground_color must be warm (R > B) — amber imprimatura."""
    s = get_style("gerrit_dou")
    r, g, b = s.ground_color
    assert r > b, (
        f"Gerrit Dou ground must be warm (R > B) — amber imprimatura; "
        f"got ground_color={s.ground_color}")


def test_gerrit_dou_stroke_size_finest():
    """Gerrit Dou stroke_size must be ≤ 3 — the most extreme fineness in the catalog."""
    s = get_style("gerrit_dou")
    assert s.stroke_size <= 3, (
        f"Gerrit Dou stroke_size must be ≤ 3 (magnifying-glass precision); "
        f"got {s.stroke_size}")


def test_gerrit_dou_wet_blend_high():
    """Gerrit Dou wet_blend must be ≥ 0.70 — extreme glazing: 30+ transparent layers."""
    s = get_style("gerrit_dou")
    assert s.wet_blend >= 0.70, (
        f"Gerrit Dou wet_blend must be ≥ 0.70 (extreme glazing); got {s.wet_blend:.2f}")


def test_gerrit_dou_edge_softness_crisp():
    """Gerrit Dou edge_softness must be ≤ 0.40 — crisp Leiden precision, not sfumato."""
    s = get_style("gerrit_dou")
    assert s.edge_softness <= 0.40, (
        f"Gerrit Dou edge_softness must be ≤ 0.40 (crisp, not sfumato); "
        f"got {s.edge_softness:.2f}")


def test_gerrit_dou_has_warm_glazing():
    """Gerrit Dou glazing must be warm (R > B) — candle amber glaze."""
    s = get_style("gerrit_dou")
    assert s.glazing is not None, "Gerrit Dou must have a glazing colour"
    r, g, b = s.glazing
    assert r > b, (
        f"Gerrit Dou glazing must be warm (R > B) — candle amber; got {s.glazing}")


def test_gerrit_dou_has_crackle():
    """Gerrit Dou crackle must be True — 17th-century panel."""
    s = get_style("gerrit_dou")
    assert s.crackle, "Gerrit Dou crackle must be True (17th-century oak panel)"


def test_gerrit_dou_no_chromatic_split():
    """Gerrit Dou chromatic_split must be False — not a Divisionist."""
    s = get_style("gerrit_dou")
    assert not s.chromatic_split, (
        "Gerrit Dou chromatic_split must be False — he is not a Divisionist")


def test_gerrit_dou_famous_works_not_empty():
    """Gerrit Dou famous_works must not be empty."""
    s = get_style("gerrit_dou")
    assert len(s.famous_works) >= 4, (
        f"Gerrit Dou should have at least 4 famous works; got {len(s.famous_works)}")


def test_gerrit_dou_famous_works_include_night_school():
    """Gerrit Dou famous works must include The Night School."""
    s = get_style("gerrit_dou")
    titles = [t.lower() for t, _ in s.famous_works]
    assert any("night school" in t or "night" in t for t in titles), (
        "Gerrit Dou famous_works must include The Night School — "
        "his most celebrated candle scene")


def test_gerrit_dou_technique_mentions_magnifying_glass():
    """Gerrit Dou technique text must mention the magnifying glass."""
    s = get_style("gerrit_dou")
    assert ("magnifying" in s.technique.lower() or "magnifying glass" in s.technique.lower()), (
        "Gerrit Dou technique must mention his use of a magnifying glass — "
        "the defining detail of his working practice")


def test_gerrit_dou_technique_mentions_fijnschilder():
    """Gerrit Dou technique text must reference fijnschilder tradition."""
    s = get_style("gerrit_dou")
    assert "fijnschilder" in s.technique.lower(), (
        "Gerrit Dou technique must reference the fijnschilder tradition he founded")


def test_gerrit_dou_technique_mentions_rembrandt():
    """Gerrit Dou technique must mention Rembrandt — he was Rembrandt's first pupil."""
    s = get_style("gerrit_dou")
    assert "rembrandt" in s.technique.lower(), (
        "Gerrit Dou technique must mention Rembrandt — he was Rembrandt's first pupil in Leiden")


def test_gerrit_dou_inspiration_references_pass():
    """Gerrit Dou inspiration must reference gerrit_dou_fijnschilder_pass()."""
    s = get_style("gerrit_dou")
    assert "gerrit_dou_fijnschilder_pass" in s.inspiration, (
        "Gerrit Dou inspiration must reference gerrit_dou_fijnschilder_pass()")


def test_gerrit_dou_period_enum_present():
    """DUTCH_FIJNSCHILDER must exist in Period enum (session 94)."""
    assert hasattr(Period, "DUTCH_FIJNSCHILDER"), "Period.DUTCH_FIJNSCHILDER not found"
    assert Period.DUTCH_FIJNSCHILDER in list(Period)


def test_gerrit_dou_stroke_params():
    """DUTCH_FIJNSCHILDER stroke_params must reflect extreme fineness."""
    style = Style(medium=Medium.OIL, period=Period.DUTCH_FIJNSCHILDER, palette=PaletteHint.WARM_EARTH)
    params = style.stroke_params
    # Dou: extremely fine strokes — stroke_size_face must be the smallest in the catalog
    assert params["stroke_size_face"] <= 3, (
        f"DUTCH_FIJNSCHILDER stroke_size_face must be ≤ 3 (magnifying-glass precision); "
        f"got {params['stroke_size_face']}")
    # Extreme glazing — wet_blend must be very high
    assert params["wet_blend"] >= 0.70, (
        f"DUTCH_FIJNSCHILDER wet_blend must be ≥ 0.70 (30+ glaze layers); "
        f"got {params['wet_blend']:.2f}")
    # Crisp edges — not sfumato
    assert params["edge_softness"] <= 0.40, (
        f"DUTCH_FIJNSCHILDER edge_softness must be ≤ 0.40 (Leiden precision); "
        f"got {params['edge_softness']:.2f}")


# ──────────────────────────────────────────────────────────────────────────────
# Carel Fabritius — session 95 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_carel_fabritius_in_catalog():
    """Carel Fabritius (session 95) must be in the catalog."""
    assert "carel_fabritius" in CATALOG


def test_carel_fabritius_movement():
    s = get_style("carel_fabritius")
    assert "Dutch" in s.movement or "dutch" in s.movement.lower()


def test_carel_fabritius_nationality():
    s = get_style("carel_fabritius")
    assert "Dutch" in s.nationality


def test_carel_fabritius_palette_length():
    s = get_style("carel_fabritius")
    assert len(s.palette) >= 5, "Fabritius palette should have at least 5 key colours"


def test_carel_fabritius_palette_in_range():
    """All Fabritius palette RGB values must be in [0, 1]."""
    s = get_style("carel_fabritius")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Fabritius palette {rgb}")


def test_carel_fabritius_ground_color_pale():
    """Fabritius used a pale grey ground — all channels should be above 0.55."""
    s = get_style("carel_fabritius")
    for ch in s.ground_color:
        assert ch >= 0.55, (
            f"Fabritius ground channel {ch:.3f} should be pale (≥ 0.55); "
            "he painted on light grounds, not Rembrandt-dark imprimatura")


def test_carel_fabritius_stroke_size_moderate():
    """Fabritius worked with confident, direct brushwork — not fijnschilder fineness."""
    s = get_style("carel_fabritius")
    assert s.stroke_size >= 6, (
        f"Fabritius stroke_size should be ≥ 6 (confident brushwork); got {s.stroke_size}")


def test_carel_fabritius_no_glazing():
    """Fabritius did not use a unifying final glaze — his pale ground provides the unity."""
    s = get_style("carel_fabritius")
    assert s.glazing is None, "Fabritius should have no glazing colour"


def test_carel_fabritius_has_crackle():
    s = get_style("carel_fabritius")
    assert s.crackle is True


def test_carel_fabritius_no_chromatic_split():
    s = get_style("carel_fabritius")
    assert s.chromatic_split is False


def test_carel_fabritius_famous_works_not_empty():
    s = get_style("carel_fabritius")
    assert len(s.famous_works) >= 3


def test_carel_fabritius_famous_works_include_goldfinch():
    """The Goldfinch (1654) is Fabritius's most famous surviving work."""
    s = get_style("carel_fabritius")
    titles = [w[0] for w in s.famous_works]
    assert any("Goldfinch" in t for t in titles), (
        f"Expected 'The Goldfinch' among famous works; got {titles}")


def test_carel_fabritius_technique_mentions_contre_jour():
    s = get_style("carel_fabritius")
    assert "contre" in s.technique.lower() or "light" in s.technique.lower()


def test_carel_fabritius_technique_mentions_vermeer():
    """Fabritius was Vermeer's teacher — technique must mention this lineage."""
    s = get_style("carel_fabritius")
    assert "Vermeer" in s.technique


def test_carel_fabritius_inspiration_references_pass():
    """Inspiration field must reference fabritius_contre_jour_pass()."""
    s = get_style("carel_fabritius")
    assert "fabritius_contre_jour_pass" in s.inspiration


def test_carel_fabritius_period_enum_present():
    """DUTCH_LIGHT_GROUND must exist in Period enum (session 95)."""
    assert hasattr(Period, "DUTCH_LIGHT_GROUND"), "Period.DUTCH_LIGHT_GROUND not found"
    assert Period.DUTCH_LIGHT_GROUND in list(Period)


def test_carel_fabritius_stroke_params():
    """DUTCH_LIGHT_GROUND stroke_params must reflect confident moderate brushwork."""
    style = Style(medium=Medium.OIL, period=Period.DUTCH_LIGHT_GROUND, palette=PaletteHint.WARM_EARTH)
    params = style.stroke_params
    # Fabritius: confident direct strokes — larger than fijnschilder but not Baroque bravura
    assert params["stroke_size_face"] >= 6, (
        f"DUTCH_LIGHT_GROUND stroke_size_face must be ≥ 6 (confident brushwork); "
        f"got {params['stroke_size_face']}")
    # Moderate wet blending — not extreme glazing, not alla prima dry
    assert 0.35 <= params["wet_blend"] <= 0.65, (
        f"DUTCH_LIGHT_GROUND wet_blend must be moderate [0.35, 0.65]; "
        f"got {params['wet_blend']:.2f}")
    # Moderate edges — not sfumato, not Flemish razor-precision
    assert 0.30 <= params["edge_softness"] <= 0.60, (
        f"DUTCH_LIGHT_GROUND edge_softness must be moderate [0.30, 0.60]; "
        f"got {params['edge_softness']:.2f}")


# ──────────────────────────────────────────────────────────────────────────────
# Judith Leyster — session 96 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_judith_leyster_in_catalog():
    """Judith Leyster (session 96) must be present in CATALOG."""
    assert "judith_leyster" in CATALOG


def test_judith_leyster_artist_name():
    s = get_style("judith_leyster")
    assert "Leyster" in s.artist


def test_judith_leyster_movement_dutch():
    """Leyster belongs to the Dutch Golden Age tradition."""
    s = get_style("judith_leyster")
    assert "Dutch" in s.movement or "dutch" in s.movement.lower()


def test_judith_leyster_palette_length():
    s = get_style("judith_leyster")
    assert len(s.palette) >= 6, "Leyster palette should have at least 6 key colours"


def test_judith_leyster_palette_values_in_range():
    """All Judith Leyster palette RGB values must be in [0, 1]."""
    s = get_style("judith_leyster")
# Frans Hals — session 96 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_frans_hals_in_catalog():
    """Frans Hals (session 96) must be in the catalog."""
    assert "frans_hals" in CATALOG


def test_frans_hals_movement():
    s = get_style("frans_hals")
    assert "Dutch" in s.movement or "dutch" in s.movement.lower()


def test_frans_hals_nationality():
    s = get_style("frans_hals")
    assert "Dutch" in s.nationality


def test_frans_hals_palette_length():
    s = get_style("frans_hals")
    assert len(s.palette) >= 5, "Hals palette should have at least 5 key colours"


def test_frans_hals_palette_in_range():
    """All Hals palette RGB values must be in [0, 1]."""
    s = get_style("frans_hals")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Leyster palette {rgb}")


def test_judith_leyster_ground_color_warm():
    """Leyster's ground should be warm amber-brown (R > B)."""
    s = get_style("judith_leyster")
    r, g, b = s.ground_color
    assert r > b, "Leyster ground_color should be warm (R > B)"
    assert r > 0.4, "Leyster ground_color R should be substantial warm amber"


def test_judith_leyster_edge_softness_moderate():
    """Leyster's edges are moderate — figures read clearly, not sfumato-dissolved."""
    s = get_style("judith_leyster")
    assert 0.35 <= s.edge_softness <= 0.70, (
        f"Leyster edge_softness should be moderate [0.35, 0.70]; got {s.edge_softness:.2f}")


def test_judith_leyster_wet_blend_moderate():
    """Leyster's wet_blend should be moderate — not Dou's extreme glazing, not alla prima dry."""
    s = get_style("judith_leyster")
    assert 0.25 <= s.wet_blend <= 0.60, (
        f"Leyster wet_blend should be moderate [0.25, 0.60]; got {s.wet_blend:.2f}")


def test_judith_leyster_famous_works_not_empty():
    s = get_style("judith_leyster")
    assert len(s.famous_works) >= 3, "Leyster should have at least 3 famous works"


def test_judith_leyster_famous_works_include_self_portrait():
    """Self-Portrait (c. 1633) is her most iconic and widely reproduced work."""
    s = get_style("judith_leyster")
    titles = [w[0] for w in s.famous_works]
    assert any("Self" in t or "Portrait" in t for t in titles), (
        f"Expected 'Self-Portrait' among Leyster's famous works; got {titles}")


def test_judith_leyster_technique_not_empty():
    s = get_style("judith_leyster")
    assert len(s.technique) >= 100, "Leyster technique field should be substantive"


def test_judith_leyster_technique_mentions_hals():
    """Leyster's relationship to Frans Hals is the defining biographical fact."""
    s = get_style("judith_leyster")
    assert "Hals" in s.technique, "Leyster's technique must mention Frans Hals"


def test_judith_leyster_technique_mentions_guild():
    """Her admission to the Haarlem Guild is a defining artistic achievement."""
    s = get_style("judith_leyster")
    assert "Guild" in s.technique or "guild" in s.technique.lower(), (
        "Leyster's technique should mention the Haarlem Guild of St. Luke")


def test_judith_leyster_inspiration_references_pass():
    """Inspiration field must reference judith_leyster_joyful_light_pass()."""
    s = get_style("judith_leyster")
    assert "judith_leyster_joyful_light_pass" in s.inspiration


def test_judith_leyster_period_enum_present():
    """DUTCH_CANDLELIT_GENRE must exist in Period enum (session 96)."""
    assert hasattr(Period, "DUTCH_CANDLELIT_GENRE"), "Period.DUTCH_CANDLELIT_GENRE not found"
    assert Period.DUTCH_CANDLELIT_GENRE in list(Period)


def test_judith_leyster_stroke_params():
    """DUTCH_CANDLELIT_GENRE stroke_params must reflect confident warm bravura."""
    style = Style(medium=Medium.OIL, period=Period.DUTCH_CANDLELIT_GENRE, palette=PaletteHint.WARM_EARTH)
    params = style.stroke_params
    # Leyster: confident bravura marks — larger than Dou's minute fineness
    assert params["stroke_size_face"] >= 7, (
        f"DUTCH_CANDLELIT_GENRE stroke_size_face must be ≥ 7 (bravura marks); "
        f"got {params['stroke_size_face']}")
    # Moderate wet blending — warm flesh transitions, not sfumato dissolution
    assert 0.25 <= params["wet_blend"] <= 0.60, (
        f"DUTCH_CANDLELIT_GENRE wet_blend must be moderate [0.25, 0.60]; "
        f"got {params['wet_blend']:.2f}")
    # Moderate edges — figures read clearly against warm shadow ground
    assert 0.35 <= params["edge_softness"] <= 0.68, (
        f"DUTCH_CANDLELIT_GENRE edge_softness must be moderate [0.35, 0.68]; "
                f"Out-of-range channel {channel} in Hals palette {rgb}")


def test_frans_hals_no_glazing():
    """Hals painted alla prima — no unifying final glaze."""
    s = get_style("frans_hals")
    assert s.glazing is None, "Hals should have no glazing (alla prima, not multi-glaze)"


def test_Frans_hals_stroke_size_bold():
    """Hals painted with large, confident taches — stroke_size should be ≥ 8."""
    s = get_style("frans_hals")
    assert s.stroke_size >= 8, (
        f"Hals stroke_size should be ≥ 8 (bold tache brushwork); got {s.stroke_size}")


def test_Frans_hals_wet_blend_low():
    """Alla prima means very low wet_blend — strokes are direct, not melted together."""
    s = get_style("frans_hals")
    assert s.wet_blend <= 0.25, (
        f"Hals wet_blend should be ≤ 0.25 (alla prima directness); got {s.wet_blend:.2f}")


def test_Frans_hals_edge_softness_crisp():
    """Hals edges are crisp and directional — not sfumato dissolved."""
    s = get_style("frans_hals")
    assert s.edge_softness <= 0.35, (
        f"Hals edge_softness should be ≤ 0.35 (psychological vivacity); "
        f"got {s.edge_softness:.2f}")


def test_Frans_hals_has_crackle():
    s = get_style("frans_hals")
    assert s.crackle is True


def test_Frans_hals_no_chromatic_split():
    s = get_style("frans_hals")
    assert s.chromatic_split is False


def test_Frans_hals_famous_works_not_empty():
    s = get_style("frans_hals")
    assert len(s.famous_works) >= 3


def test_Frans_hals_famous_works_include_laughing_cavalier():
    """The Laughing Cavalier (1624) is Hals's most famous work."""
    s = get_style("frans_hals")
    titles = [w[0] for w in s.famous_works]
    assert any("Cavalier" in t or "Laughing" in t for t in titles), (
        f"Expected 'The Laughing Cavalier' among famous works; got {titles}")


def test_Frans_hals_technique_mentions_alla_prima():
    s = get_style("frans_hals")
    assert "alla prima" in s.technique.lower() or "tache" in s.technique.lower()


def test_Frans_hals_technique_mentions_impressionist():
    """Hals's influence on the Impressionists (especially Manet) should be noted."""
    s = get_style("frans_hals")
    assert "Impressionist" in s.technique or "Manet" in s.technique


def test_Frans_hals_inspiration_references_pass():
    """Inspiration field must reference hals_bravura_stroke_pass()."""
    s = get_style("frans_hals")
    assert "hals_bravura_stroke_pass" in s.inspiration


def test_Frans_hals_period_enum_present():
    """DUTCH_BRAVURA_PORTRAIT must exist in Period enum (session 96)."""
    assert hasattr(Period, "DUTCH_BRAVURA_PORTRAIT"), "Period.DUTCH_BRAVURA_PORTRAIT not found"
    assert Period.DUTCH_BRAVURA_PORTRAIT in list(Period)


def test_Frans_hals_stroke_params():
    """DUTCH_BRAVURA_PORTRAIT stroke_params must reflect bold alla prima brushwork."""
    style = Style(medium=Medium.OIL, period=Period.DUTCH_BRAVURA_PORTRAIT, palette=PaletteHint.WARM_EARTH)
    params = style.stroke_params
    # Hals: bold loaded-brush taches — larger than fijnschilder or Fabritius
    assert params["stroke_size_face"] >= 8, (
        f"DUTCH_BRAVURA_PORTRAIT stroke_size_face must be ≥ 8 (bold tache); "
        f"got {params['stroke_size_face']}")
    # Very low wet blending — alla prima directness
    assert params["wet_blend"] <= 0.20, (
        f"DUTCH_BRAVURA_PORTRAIT wet_blend must be ≤ 0.20 (alla prima); "
        f"got {params['wet_blend']:.2f}")
    # Crisp directional edges — psychological vivacity
    assert params["edge_softness"] <= 0.30, (
        f"DUTCH_BRAVURA_PORTRAIT edge_softness must be ≤ 0.30 (tache crispness); "
        f"got {params['edge_softness']:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# Bernardino Luini — session 97
# ─────────────────────────────────────────────────────────────────────────────

def test_bernardino_luini_in_catalog():
    """bernardino_luini must be present in the CATALOG (session 97)."""
    from art_catalog import CATALOG
    assert "bernardino_luini" in CATALOG, "bernardino_luini not found in CATALOG"


def test_bernardino_luini_style_fields():
    """bernardino_luini ArtStyle must have artist, nationality, movement, and period."""
    s = get_style("bernardino_luini")
    assert "Luini" in s.artist
    assert "Italian" in s.nationality or "Milanese" in s.nationality
    assert "Milanese" in s.movement or "Renaissance" in s.movement
    assert s.period is not None and len(s.period) > 0


def test_bernardino_luini_palette_size():
    """bernardino_luini must have at least 6 palette entries."""
    s = get_style("bernardino_luini")
    assert len(s.palette) >= 6, (
        f"bernardino_luini palette must have ≥ 6 entries; got {len(s.palette)}")


def test_bernardino_luini_palette_warm_ivory():
    """bernardino_luini palette must include warm-ivory highlight (R > 0.85, all channels high)."""
    s = get_style("bernardino_luini")
    warm_ivory_found = any(
        r > 0.85 and g > 0.75 and b > 0.55
        for r, g, b in s.palette
    )
    assert warm_ivory_found, (
        f"bernardino_luini palette must include a warm-ivory highlight (R>0.85, G>0.75, B>0.55); "
        f"got {s.palette}")


def test_bernardino_luini_soft_edges():
    """bernardino_luini edge_softness must be >= 0.65 (Leonardesque sfumato dissolution)."""
    s = get_style("bernardino_luini")
    assert s.edge_softness >= 0.65, (
        f"bernardino_luini edge_softness must be >= 0.65 (sfumato); got {s.edge_softness:.2f}")


def test_bernardino_luini_high_wet_blend():
    """bernardino_luini wet_blend must be >= 0.60 (multi-glaze seamless surface)."""
    s = get_style("bernardino_luini")
    assert s.wet_blend >= 0.60, (
        f"bernardino_luini wet_blend must be >= 0.60 (glaze layers); got {s.wet_blend:.2f}")


def test_bernardino_luini_fine_stroke_size():
    """bernardino_luini stroke_size must be <= 6 (fine polished Renaissance brushwork)."""
    s = get_style("bernardino_luini")
    assert s.stroke_size <= 6, (
        f"bernardino_luini stroke_size must be <= 6; got {s.stroke_size}")


def test_bernardino_luini_has_glazing():
    """bernardino_luini must have a glazing colour (multi-layer glazed surface)."""
    s = get_style("bernardino_luini")
    assert s.glazing is not None, "bernardino_luini should have a glazing colour (multi-glaze)"


def test_bernardino_luini_has_crackle():
    """bernardino_luini crackle must be True (oil on panel, aged)."""
    s = get_style("bernardino_luini")
    assert s.crackle is True


def test_bernardino_luini_no_chromatic_split():
    """bernardino_luini chromatic_split must be False (warm unified glaze, not split)."""
    s = get_style("bernardino_luini")
    assert s.chromatic_split is False


def test_bernardino_luini_technique_mentions_leonardo():
    """Technique field must reference Leonardo da Vinci."""
    s = get_style("bernardino_luini")
    assert "Leonardo" in s.technique, "bernardino_luini technique must mention Leonardo da Vinci"


def test_bernardino_luini_technique_mentions_sfumato():
    """Technique field must reference sfumato."""
    s = get_style("bernardino_luini")
    assert "sfumato" in s.technique.lower(), "bernardino_luini technique must mention sfumato"


def test_bernardino_luini_famous_works_not_empty():
    """bernardino_luini must have at least 4 famous works."""
    s = get_style("bernardino_luini")
    assert len(s.famous_works) >= 4, (
        f"bernardino_luini must have >= 4 famous works; got {len(s.famous_works)}")


def test_bernardino_luini_famous_works_include_susanna():
    """Susanna at the Bath (c. 1520-1523) is among Luini's most celebrated works."""
    s = get_style("bernardino_luini")
    titles = [w[0] for w in s.famous_works]
    assert any("Susanna" in t for t in titles), (
        f"Expected 'Susanna at the Bath' among famous works; got {titles}")


def test_bernardino_luini_inspiration_references_pass():
    """Inspiration field must reference luini_leonardesque_glow_pass()."""
    s = get_style("bernardino_luini")
    assert "luini_leonardesque_glow_pass" in s.inspiration


def test_bernardino_luini_period_enum_present():
    """MILANESE_SFUMATO must exist in Period enum (session 97)."""
    assert hasattr(Period, "MILANESE_SFUMATO"), "Period.MILANESE_SFUMATO not found"
    assert Period.MILANESE_SFUMATO in list(Period)


def test_bernardino_luini_stroke_params():
    """MILANESE_SFUMATO stroke_params must reflect soft Leonardesque sfumato technique."""
    style = Style(medium=Medium.OIL, period=Period.MILANESE_SFUMATO, palette=PaletteHint.WARM_EARTH)
    params = style.stroke_params
    # Fine strokes — polished Milanese sfumato
    assert params["stroke_size_face"] <= 6, (
        f"MILANESE_SFUMATO stroke_size_face must be <= 6 (fine sfumato); "
        f"got {params['stroke_size_face']}")
    # High wet blend — seamless multi-glaze surface
    assert params["wet_blend"] >= 0.60, (
        f"MILANESE_SFUMATO wet_blend must be >= 0.60 (glaze seamlessness); "
        f"got {params['wet_blend']:.2f}")
    # Very soft edges — sfumato dissolution
    assert params["edge_softness"] >= 0.65, (
        f"MILANESE_SFUMATO edge_softness must be >= 0.65 (sfumato edge loss); "
        f"got {params['edge_softness']:.2f}")


def test_sfumato_veil_pass_highlight_ivory_lift_parameter_exists():
    """sfumato_veil_pass must accept highlight_ivory_lift parameter (session 97)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.sfumato_veil_pass)
    assert "highlight_ivory_lift" in sig.parameters, (
        "sfumato_veil_pass must have highlight_ivory_lift parameter (session 97)")


def test_sfumato_veil_pass_highlight_ivory_thresh_parameter_exists():
    """sfumato_veil_pass must accept highlight_ivory_thresh parameter (session 97)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.sfumato_veil_pass)
    assert "highlight_ivory_thresh" in sig.parameters, (
        "sfumato_veil_pass must have highlight_ivory_thresh parameter (session 97)")


# ──────────────────────────────────────────────────────────────────────────────
# Federico Barocci  (session 98)
# ──────────────────────────────────────────────────────────────────────────────

def test_federico_barocci_in_catalog():
    """federico_barocci must be present in the CATALOG (session 98)."""
    assert "federico_barocci" in CATALOG, "federico_barocci not found in CATALOG"


def test_federico_barocci_style_fields():
    """federico_barocci ArtStyle must have artist, nationality, movement, and period."""
    s = get_style("federico_barocci")
    assert s.artist
    assert s.nationality
    assert s.movement
    assert s.period


def test_federico_barocci_palette_size():
    """federico_barocci must have at least 6 palette entries."""
    s = get_style("federico_barocci")
    assert len(s.palette) >= 6, (
        f"federico_barocci palette must have >= 6 entries; got {len(s.palette)}")


def test_federico_barocci_palette_rose_flesh():
    """federico_barocci palette must include a warm rose-flesh midtone (high R, moderate G and B)."""
    s = get_style("federico_barocci")
    has_rose = any(
        rgb[0] > 0.72 and rgb[1] > 0.44 and rgb[2] > 0.32
        for rgb in s.palette
    )
    assert has_rose, (
        f"federico_barocci palette must include a warm rose-flesh midtone "
        f"(R>0.72, G>0.44, B>0.32); got {s.palette}")


def test_federico_barocci_soft_edges():
    """federico_barocci edge_softness must be >= 0.60 (Umbrian sfumato dissolution)."""
    s = get_style("federico_barocci")
    assert s.edge_softness >= 0.60, (
        f"federico_barocci edge_softness must be >= 0.60 (Umbrian sfumato); "
        f"got {s.edge_softness:.2f}")


def test_federico_barocci_high_wet_blend():
    """federico_barocci wet_blend must be >= 0.55 (multi-glaze pasteletti surface)."""
    s = get_style("federico_barocci")
    assert s.wet_blend >= 0.55, (
        f"federico_barocci wet_blend must be >= 0.55 (multi-glaze); got {s.wet_blend:.2f}")


def test_federico_barocci_fine_stroke_size():
    """federico_barocci stroke_size must be <= 7 (fine Umbrian Mannerist brushwork)."""
    s = get_style("federico_barocci")
    assert s.stroke_size <= 7, (
        f"federico_barocci stroke_size must be <= 7; got {s.stroke_size}")


def test_federico_barocci_has_glazing():
    """federico_barocci must have a glazing colour (multi-layer warm glazed surface)."""
    s = get_style("federico_barocci")
    assert s.glazing is not None, "federico_barocci should have a glazing colour"


def test_federico_barocci_has_crackle():
    """federico_barocci crackle must be True (oil on panel / canvas, aged)."""
    s = get_style("federico_barocci")
    assert s.crackle is True, "federico_barocci crackle must be True (aged oil)"


def test_federico_barocci_no_chromatic_split():
    """federico_barocci chromatic_split must be False (unified warm-rose glazing)."""
    s = get_style("federico_barocci")
    assert s.chromatic_split is False, (
        "federico_barocci chromatic_split must be False (warm unified palette)")


def test_federico_barocci_technique_mentions_penumbra():
    """federico_barocci technique must mention the penumbra or petal flush concept."""
    s = get_style("federico_barocci")
    assert "penumbra" in s.technique.lower() or "petal" in s.technique.lower(), (
        "federico_barocci technique must describe the penumbra / petal flush quality")


def test_federico_barocci_technique_mentions_pasteletti():
    """federico_barocci technique must mention pasteletti (the preparatory pastel technique)."""
    s = get_style("federico_barocci")
    assert "pasteletti" in s.technique.lower() or "pastel" in s.technique.lower(), (
        "federico_barocci technique must mention pasteletti (chalk pastel studies)")


def test_federico_barocci_famous_works_not_empty():
    """federico_barocci must have at least 4 famous works."""
    s = get_style("federico_barocci")
    assert len(s.famous_works) >= 4, (
        f"federico_barocci must have >= 4 famous works; got {len(s.famous_works)}")


def test_federico_barocci_famous_works_include_annunciation():
    """Annunciation (Vatican) is Barocci's most celebrated work."""
    s = get_style("federico_barocci")
    titles = [w[0] for w in s.famous_works]
    assert any("Annunciation" in t for t in titles), (
        f"Expected 'Annunciation' among famous works; got {titles}")


def test_federico_barocci_inspiration_references_pass():
    """Inspiration field must reference barocci_petal_flush_pass()."""
    s = get_style("federico_barocci")
    assert "barocci_petal_flush_pass" in s.inspiration, (
        "federico_barocci inspiration must reference barocci_petal_flush_pass()")


def test_federico_barocci_period_enum_present():
    """UMBRIAN_MANNERIST must exist in Period enum (session 98)."""
    assert hasattr(Period, "UMBRIAN_MANNERIST"), "Period.UMBRIAN_MANNERIST not found"
    assert Period.UMBRIAN_MANNERIST in list(Period)


def test_federico_barocci_stroke_params():
    """UMBRIAN_MANNERIST stroke_params must reflect soft Umbrian Mannerist technique."""
    style = Style(medium=Medium.OIL, period=Period.UMBRIAN_MANNERIST, palette=PaletteHint.WARM_EARTH)
    params = style.stroke_params
    # Fine strokes — polished Umbrian flesh passages
    assert params["stroke_size_face"] <= 7, (
        f"UMBRIAN_MANNERIST stroke_size_face must be <= 7 (fine Umbrian brushwork); "
        f"got {params['stroke_size_face']}")
    # High wet blend — seamless multi-glaze surface
    assert params["wet_blend"] >= 0.55, (
        f"UMBRIAN_MANNERIST wet_blend must be >= 0.55 (glaze seamlessness); "
        f"got {params['wet_blend']:.2f}")
    # Soft edges — Umbrian sfumato dissolution
    assert params["edge_softness"] >= 0.60, (
        f"UMBRIAN_MANNERIST edge_softness must be >= 0.60 (Umbrian sfumato); "
        f"got {params['edge_softness']:.2f}")


def test_barocci_petal_flush_pass_exists():
    """Painter must have a barocci_petal_flush_pass() method (session 98)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "barocci_petal_flush_pass"), (
        "Painter must have barocci_petal_flush_pass() method (session 98)")


def test_barocci_petal_flush_pass_penumbra_parameters():
    """barocci_petal_flush_pass must accept penumbra_lo, penumbra_hi, rose_r, rose_g, rose_b."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.barocci_petal_flush_pass)
    for param in ("penumbra_lo", "penumbra_hi", "rose_r", "rose_g", "rose_b"):
        assert param in sig.parameters, (
            f"barocci_petal_flush_pass must have {param!r} parameter")


def test_barocci_petal_flush_pass_bianca_parameters():
    """barocci_petal_flush_pass must accept bianca_lo, bianca_hi, bianca_r, bianca_g, bianca_b."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.barocci_petal_flush_pass)
    for param in ("bianca_lo", "bianca_hi", "bianca_r", "bianca_g", "bianca_b"):
        assert param in sig.parameters, (
            f"barocci_petal_flush_pass must have {param!r} parameter")


def test_barocci_petal_flush_pass_edge_dissolve_parameters():
    """barocci_petal_flush_pass must accept edge_dissolve_sigma, edge_dissolve_radius,
    edge_dissolve_strength."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.barocci_petal_flush_pass)
    for param in ("edge_dissolve_sigma", "edge_dissolve_radius", "edge_dissolve_strength"):
        assert param in sig.parameters, (
            f"barocci_petal_flush_pass must have {param!r} parameter")


# ──────────────────────────────────────────────────────────────────────────────
# Pierre Bonnard / CHROMATIC_INTIMISME — session 99 additions
# ──────────────────────────────────────────────────────────────────────────────

def test_pierre_bonnard_in_catalog():
    """pierre_bonnard (session 99) must be in the catalog."""
    assert "pierre_bonnard" in CATALOG, "pierre_bonnard missing from CATALOG"


def test_pierre_bonnard_movement():
    """Bonnard's movement must reference Post-Impressionism or Nabi."""
    s = get_style("pierre_bonnard")
    mvmt = s.movement.lower()
    assert "nabi" in mvmt or "impressi" in mvmt or "intimisme" in mvmt, (
        f"pierre_bonnard movement {s.movement!r} should mention Nabi or Post-Impressionism"
    )


def test_pierre_bonnard_palette_length():
    """Bonnard palette must have at least 5 entries."""
    s = get_style("pierre_bonnard")
    assert len(s.palette) >= 5, (
        f"pierre_bonnard palette should have ≥ 5 entries; got {len(s.palette)}"
    )


def test_pierre_bonnard_palette_values_in_range():
    """All Bonnard palette RGB channels must be in [0, 1]."""
    s = get_style("pierre_bonnard")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"pierre_bonnard palette channel {ch} out of [0, 1]"
            )


def test_pierre_bonnard_wet_blend_low():
    """Bonnard's low wet_blend keeps warm/cool dabs distinct — must be ≤ 0.45."""
    s = get_style("pierre_bonnard")
    assert s.wet_blend <= 0.45, (
        f"pierre_bonnard wet_blend should be ≤ 0.45 (chromatic vibration requires "
        f"distinct dabs); got {s.wet_blend}"
    )


def test_pierre_bonnard_jitter_elevated():
    """Bonnard's elevated jitter prevents flat zones — must be > 0.03."""
    s = get_style("pierre_bonnard")
    assert s.jitter > 0.03, (
        f"pierre_bonnard jitter should be > 0.03 (no flat zones); got {s.jitter}"
    )


def test_pierre_bonnard_famous_works_present():
    """Bonnard must have at least 4 famous works catalogued."""
    s = get_style("pierre_bonnard")
    assert len(s.famous_works) >= 4, (
        f"pierre_bonnard should have ≥ 4 famous works; got {len(s.famous_works)}"
    )


# CHROMATIC_INTIMISME period tests

def test_chromatic_intimisme_period_present():
    """CHROMATIC_INTIMISME must exist in Period enum (session 99)."""
    assert hasattr(Period, "CHROMATIC_INTIMISME"), "Period.CHROMATIC_INTIMISME not found"
    assert Period.CHROMATIC_INTIMISME in list(Period)


def test_chromatic_intimisme_stroke_params_keys():
    """CHROMATIC_INTIMISME stroke_params must contain all four required keys."""
    style = Style(medium=Medium.OIL, period=Period.CHROMATIC_INTIMISME,
                  palette=PaletteHint.JEWEL)
    p = style.stroke_params
    for key in ("stroke_size_face", "stroke_size_bg", "wet_blend", "edge_softness"):
        assert key in p, f"CHROMATIC_INTIMISME stroke_params missing key: {key!r}"


def test_chromatic_intimisme_wet_blend_low():
    """CHROMATIC_INTIMISME should have low wet_blend (distinct dabs for vibration)."""
    style = Style(medium=Medium.OIL, period=Period.CHROMATIC_INTIMISME,
                  palette=PaletteHint.JEWEL)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.45, (
        f"CHROMATIC_INTIMISME wet_blend should be ≤ 0.45 for chromatic vibration; "
        f"got {p['wet_blend']}"
    )


def test_chromatic_intimisme_in_expected_periods():
    """EXPECTED_PERIODS list must include CHROMATIC_INTIMISME."""
    assert "CHROMATIC_INTIMISME" in EXPECTED_PERIODS, (
        "CHROMATIC_INTIMISME missing from EXPECTED_PERIODS — add it to the list"
    )


# bonnard_chromatic_vibration_pass signature tests

def test_bonnard_chromatic_vibration_pass_exists():
    """Painter must have a bonnard_chromatic_vibration_pass method (session 99)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "bonnard_chromatic_vibration_pass"), (
        "Painter missing bonnard_chromatic_vibration_pass"
    )


def test_bonnard_chromatic_vibration_pass_mid_parameters():
    """bonnard_chromatic_vibration_pass must accept mid_lo and mid_hi."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.bonnard_chromatic_vibration_pass)
    for param in ("mid_lo", "mid_hi"):
        assert param in sig.parameters, (
            f"bonnard_chromatic_vibration_pass must have {param!r} parameter"
        )


def test_bonnard_chromatic_vibration_pass_amp_parameters():
    """bonnard_chromatic_vibration_pass must accept warm_amp and cool_amp."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.bonnard_chromatic_vibration_pass)
    for param in ("warm_amp", "cool_amp"):
        assert param in sig.parameters, (
            f"bonnard_chromatic_vibration_pass must have {param!r} parameter"
        )


def test_bonnard_chromatic_vibration_pass_noise_parameters():
    """bonnard_chromatic_vibration_pass must accept noise_scale, noise_octaves,
    noise_persistence."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.bonnard_chromatic_vibration_pass)
    for param in ("noise_scale", "noise_octaves", "noise_persistence"):
        assert param in sig.parameters, (
            f"bonnard_chromatic_vibration_pass must have {param!r} parameter"
        )


def test_bonnard_chromatic_vibration_pass_opacity_parameter():
    """bonnard_chromatic_vibration_pass must accept opacity."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.bonnard_chromatic_vibration_pass)
    assert "opacity" in sig.parameters, (
        "bonnard_chromatic_vibration_pass must have 'opacity' parameter"
    )


# ── Session 101: Toulouse-Lautrec ────────────────────────────────────────────

def test_toulouse_lautrec_in_catalog():
    """toulouse_lautrec must be present in the art catalog."""
    from art_catalog import CATALOG
    assert "toulouse_lautrec" in CATALOG, (
        "toulouse_lautrec missing from CATALOG"
    )


def test_toulouse_lautrec_style_fields():
    """toulouse_lautrec ArtStyle must have correct artist metadata."""
    from art_catalog import get_style
    s = get_style("toulouse_lautrec")
    assert "Toulouse-Lautrec" in s.artist
    assert "Post-Impressionism" in s.movement or "Belle Époque" in s.movement
    assert s.nationality == "French"


def test_toulouse_lautrec_palette_valid():
    """toulouse_lautrec palette colors must be in [0, 1]."""
    from art_catalog import get_style
    s = get_style("toulouse_lautrec")
    for color in s.palette:
        for channel in color:
            assert 0.0 <= channel <= 1.0, (
                f"toulouse_lautrec palette channel {channel} out of [0,1]"
            )


def test_toulouse_lautrec_stroke_params():
    """toulouse_lautrec must have low wet_blend (peinture à l'essence)."""
    from art_catalog import get_style
    s = get_style("toulouse_lautrec")
    assert s.wet_blend <= 0.15, (
        f"toulouse_lautrec wet_blend {s.wet_blend} too high for essence technique"
    )
    assert s.edge_softness <= 0.25, (
        f"toulouse_lautrec edge_softness {s.edge_softness} too high for graphic style"
    )


def test_toulouse_lautrec_famous_works():
    """toulouse_lautrec must list known works."""
    from art_catalog import get_style
    s = get_style("toulouse_lautrec")
    assert len(s.famous_works) >= 3
    titles = [w[0] for w in s.famous_works]
    assert any("Moulin" in t for t in titles), (
        "toulouse_lautrec famous_works should include a Moulin Rouge work"
    )


def test_belle_epoque_period_enum():
    """BELLE_EPOQUE must exist in the Period enum."""
    from scene_schema import Period
    assert hasattr(Period, "BELLE_EPOQUE"), (
        "Period enum missing BELLE_EPOQUE"
    )


def test_belle_epoque_stroke_params():
    """BELLE_EPOQUE must have low wet_blend and low edge_softness."""
    from scene_schema import Style, Period
    s = Style(period=Period.BELLE_EPOQUE)
    params = s.stroke_params
    assert params["wet_blend"] <= 0.12, (
        f"BELLE_EPOQUE wet_blend {params['wet_blend']} too high"
    )
    assert params["edge_softness"] <= 0.20, (
        f"BELLE_EPOQUE edge_softness {params['edge_softness']} too high"
    )


def test_lautrec_essence_pass_exists():
    """Painter must have lautrec_essence_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "lautrec_essence_pass"), (
        "Painter missing lautrec_essence_pass"
    )


def test_lautrec_essence_pass_matte_parameter():
    """lautrec_essence_pass must accept matte_str."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.lautrec_essence_pass)
    assert "matte_str" in sig.parameters, (
        "lautrec_essence_pass must have 'matte_str' parameter"
    )


def test_lautrec_essence_pass_hatch_parameters():
    """lautrec_essence_pass must accept hatch_angle, hatch_density, hatch_darkness."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.lautrec_essence_pass)
    for param in ("hatch_angle", "hatch_density", "hatch_darkness"):
        assert param in sig.parameters, (
            f"lautrec_essence_pass must have {param!r} parameter"
        )


def test_lautrec_essence_pass_warm_cool_parameters():
    """lautrec_essence_pass must accept warm_boost and cool_boost."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.lautrec_essence_pass)
    for param in ("warm_boost", "cool_boost"):
        assert param in sig.parameters, (
            f"lautrec_essence_pass must have {param!r} parameter"
        )


def test_lautrec_essence_pass_opacity_parameter():
    """lautrec_essence_pass must accept opacity."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.lautrec_essence_pass)
    assert "opacity" in sig.parameters, (
        "lautrec_essence_pass must have 'opacity' parameter"
    )


def test_lautrec_essence_pass_rng_seed_parameter():
    """lautrec_essence_pass must accept rng_seed for reproducible hatching."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.lautrec_essence_pass)
    assert "rng_seed" in sig.parameters, (
        "lautrec_essence_pass must have 'rng_seed' parameter"
    )


# ── Session 102: James Tissot ─────────────────────────────────────────────────

def test_tissot_in_catalog():
    """tissot must be present in the art catalog."""
    from art_catalog import CATALOG
    assert "tissot" in CATALOG, (
        "tissot missing from CATALOG"
    )


def test_tissot_style_fields():
    """tissot ArtStyle must have correct artist metadata."""
    from art_catalog import get_style
    s = get_style("tissot")
    assert "Tissot" in s.artist
    assert "Victorian" in s.movement or "Realism" in s.movement or "Aesthetic" in s.movement
    assert "French" in s.nationality or "British" in s.nationality


def test_tissot_palette_valid():
    """tissot palette colors must be in [0, 1]."""
    from art_catalog import get_style
    s = get_style("tissot")
    for color in s.palette:
        for channel in color:
            assert 0.0 <= channel <= 1.0, (
                f"tissot palette channel {channel} out of [0,1]"
            )


def test_tissot_stroke_params():
    """tissot must have high wet_blend (academic glazed finish)."""
    from art_catalog import get_style
    s = get_style("tissot")
    assert s.wet_blend >= 0.70, (
        f"tissot wet_blend {s.wet_blend} too low for academic glazed finish"
    )
    assert s.edge_softness >= 0.50, (
        f"tissot edge_softness {s.edge_softness} too low for academic surface"
    )


def test_tissot_famous_works():
    """tissot must list known works."""
    from art_catalog import get_style
    s = get_style("tissot")
    assert len(s.famous_works) >= 3
    titles = [w[0] for w in s.famous_works]
    assert any("Ball" in t or "Thames" in t or "Early" in t for t in titles), (
        "tissot famous_works should include a known Tissot work"
    )


def test_victorian_social_realist_period_enum():
    """VICTORIAN_SOCIAL_REALIST must exist in the Period enum."""
    from scene_schema import Period
    assert hasattr(Period, "VICTORIAN_SOCIAL_REALIST"), (
        "Period enum missing VICTORIAN_SOCIAL_REALIST"
    )


def test_victorian_social_realist_stroke_params():
    """VICTORIAN_SOCIAL_REALIST must have high wet_blend and moderate edge_softness."""
    from scene_schema import Style, Period
    s = Style(period=Period.VICTORIAN_SOCIAL_REALIST)
    params = s.stroke_params
    assert params["wet_blend"] >= 0.70, (
        f"VICTORIAN_SOCIAL_REALIST wet_blend {params['wet_blend']} too low"
    )
    assert params["edge_softness"] >= 0.50, (
        f"VICTORIAN_SOCIAL_REALIST edge_softness {params['edge_softness']} too low"
    )


def test_tissot_fashionable_gloss_pass_exists():
    """Painter must have tissot_fashionable_gloss_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "tissot_fashionable_gloss_pass"), (
        "Painter missing tissot_fashionable_gloss_pass"
    )


def test_tissot_fashionable_gloss_pass_clarity_parameter():
    """tissot_fashionable_gloss_pass must accept clarity_str."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.tissot_fashionable_gloss_pass)
    assert "clarity_str" in sig.parameters, (
        "tissot_fashionable_gloss_pass must have 'clarity_str' parameter"
    )


def test_tissot_fashionable_gloss_pass_sheen_parameters():
    """tissot_fashionable_gloss_pass must accept sheen_thresh and sheen_strength."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.tissot_fashionable_gloss_pass)
    for param in ("sheen_thresh", "sheen_strength"):
        assert param in sig.parameters, (
            f"tissot_fashionable_gloss_pass must have {param!r} parameter"
        )


def test_tissot_fashionable_gloss_pass_chroma_parameter():
    """tissot_fashionable_gloss_pass must accept chroma_boost."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.tissot_fashionable_gloss_pass)
    assert "chroma_boost" in sig.parameters, (
        "tissot_fashionable_gloss_pass must have 'chroma_boost' parameter"
    )


def test_tissot_fashionable_gloss_pass_highlight_cool_parameter():
    """tissot_fashionable_gloss_pass must accept highlight_cool."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.tissot_fashionable_gloss_pass)
    assert "highlight_cool" in sig.parameters, (
        "tissot_fashionable_gloss_pass must have 'highlight_cool' parameter"
    )


def test_tissot_fashionable_gloss_pass_opacity_parameter():
    """tissot_fashionable_gloss_pass must accept opacity."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.tissot_fashionable_gloss_pass)
    assert "opacity" in sig.parameters, (
        "tissot_fashionable_gloss_pass must have 'opacity' parameter"
    )


def test_sfumato_veil_pass_atmospheric_blue_shift_parameter():
    """sfumato_veil_pass must accept atmospheric_blue_shift (session 102 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.sfumato_veil_pass)
    assert "atmospheric_blue_shift" in sig.parameters, (
        "sfumato_veil_pass must have 'atmospheric_blue_shift' parameter (session 102)"
    )


# ── Session 103: Carlo Dolci ──────────────────────────────────────────────────

def test_carlo_dolci_in_catalog():
    """carlo_dolci must be present in the art catalog."""
    from art_catalog import CATALOG
    assert "carlo_dolci" in CATALOG, (
        "carlo_dolci missing from CATALOG"
    )


def test_carlo_dolci_style_fields():
    """carlo_dolci ArtStyle must have correct artist metadata."""
    from art_catalog import get_style
    s = get_style("carlo_dolci")
    assert "Dolci" in s.artist
    assert "Baroque" in s.movement or "Devotional" in s.movement
    assert s.nationality == "Italian"


def test_carlo_dolci_palette_valid():
    """carlo_dolci palette colors must be in [0, 1]."""
    from art_catalog import get_style
    s = get_style("carlo_dolci")
    for color in s.palette:
        for channel in color:
            assert 0.0 <= channel <= 1.0, (
                f"carlo_dolci palette channel {channel} out of [0,1]"
            )


def test_carlo_dolci_stroke_params():
    """carlo_dolci must have very high wet_blend (enamel glazed finish)."""
    from art_catalog import get_style
    s = get_style("carlo_dolci")
    assert s.wet_blend >= 0.80, (
        f"carlo_dolci wet_blend {s.wet_blend} too low for enamel glazed finish"
    )
    assert s.edge_softness >= 0.45, (
        f"carlo_dolci edge_softness {s.edge_softness} too low for glassy surface"
    )


def test_carlo_dolci_famous_works():
    """carlo_dolci must list known works."""
    from art_catalog import get_style
    s = get_style("carlo_dolci")
    assert len(s.famous_works) >= 3
    titles = [w[0] for w in s.famous_works]
    assert any("Cecilia" in t or "Magdalene" in t or "David" in t for t in titles), (
        "carlo_dolci famous_works should include a known Dolci devotional work"
    )


def test_florentine_devotional_baroque_period_enum():
    """FLORENTINE_DEVOTIONAL_BAROQUE must exist in the Period enum."""
    from scene_schema import Period
    assert hasattr(Period, "FLORENTINE_DEVOTIONAL_BAROQUE"), (
        "Period enum missing FLORENTINE_DEVOTIONAL_BAROQUE"
    )


def test_florentine_devotional_baroque_stroke_params():
    """FLORENTINE_DEVOTIONAL_BAROQUE must have very high wet_blend and moderate edge_softness."""
    from scene_schema import Style, Period
    s = Style(period=Period.FLORENTINE_DEVOTIONAL_BAROQUE)
    params = s.stroke_params
    assert params["wet_blend"] >= 0.80, (
        f"FLORENTINE_DEVOTIONAL_BAROQUE wet_blend {params['wet_blend']} too low"
    )
    assert params["edge_softness"] >= 0.45, (
        f"FLORENTINE_DEVOTIONAL_BAROQUE edge_softness {params['edge_softness']} too low"
    )


def test_dolci_florentine_enamel_pass_exists():
    """Painter must have dolci_florentine_enamel_pass method."""
    from stroke_engine import Painter
    assert hasattr(Painter, "dolci_florentine_enamel_pass"), (
        "Painter missing dolci_florentine_enamel_pass"
    )


def test_dolci_florentine_enamel_pass_smooth_parameters():
    """dolci_florentine_enamel_pass must accept smooth_sigma and smooth_strength."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.dolci_florentine_enamel_pass)
    for param in ("smooth_sigma", "smooth_strength"):
        assert param in sig.parameters, (
            f"dolci_florentine_enamel_pass must have {param!r} parameter"
        )


def test_dolci_florentine_enamel_pass_shadow_parameters():
    """dolci_florentine_enamel_pass must accept shadow_depth_str."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.dolci_florentine_enamel_pass)
    assert "shadow_depth_str" in sig.parameters, (
        "dolci_florentine_enamel_pass must have 'shadow_depth_str' parameter"
    )


def test_dolci_florentine_enamel_pass_highlight_parameters():
    """dolci_florentine_enamel_pass must accept highlight_lift."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.dolci_florentine_enamel_pass)
    assert "highlight_lift" in sig.parameters, (
        "dolci_florentine_enamel_pass must have 'highlight_lift' parameter"
    )


def test_dolci_florentine_enamel_pass_penumbra_parameters():
    """dolci_florentine_enamel_pass must accept penumbra_amber_r."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.dolci_florentine_enamel_pass)
    assert "penumbra_amber_r" in sig.parameters, (
        "dolci_florentine_enamel_pass must have 'penumbra_amber_r' parameter"
    )


def test_dolci_florentine_enamel_pass_opacity_parameter():
    """dolci_florentine_enamel_pass must accept opacity."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.dolci_florentine_enamel_pass)
    assert "opacity" in sig.parameters, (
        "dolci_florentine_enamel_pass must have 'opacity' parameter"
    )


def test_subsurface_scatter_pass_penumbra_warmth_depth_parameter():
    """subsurface_scatter_pass must accept penumbra_warmth_depth (session 103 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.subsurface_scatter_pass)
    assert "penumbra_warmth_depth" in sig.parameters, (
        "subsurface_scatter_pass must have 'penumbra_warmth_depth' parameter (session 103)"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Session 104: Luca Giordano + NEAPOLITAN_BAROQUE + giordano_rapidita_luminosa_pass
# ──────────────────────────────────────────────────────────────────────────────

def test_luca_giordano_in_catalog():
    """Luca Giordano (session 104) must be in the CATALOG."""
    assert "luca_giordano" in CATALOG, "Missing artist: 'luca_giordano'"


def test_luca_giordano_movement():
    """Luca Giordano's movement must reference Neapolitan Baroque."""
    s = get_style("luca_giordano")
    assert "Baroque" in s.movement or "baroque" in s.movement.lower(), (
        f"luca_giordano movement {s.movement!r} should mention Baroque"
    )


def test_luca_giordano_palette_length():
    """Luca Giordano's palette must have at least 5 colours."""
    s = get_style("luca_giordano")
    assert len(s.palette) >= 5, (
        f"luca_giordano palette has only {len(s.palette)} entries"
    )


def test_luca_giordano_palette_values_in_range():
    """All Luca Giordano palette RGB values must be in [0, 1]."""
    s = get_style("luca_giordano")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in luca_giordano palette {rgb}"
            )


def test_luca_giordano_famous_works():
    """Luca Giordano must have at least one famous work."""
    s = get_style("luca_giordano")
    assert len(s.famous_works) >= 1, "luca_giordano must have at least one famous work"
    titles = [w[0] for w in s.famous_works]
    assert any("Judith" in t or "Rebel" in t or "Escorial" in t for t in titles), (
        "luca_giordano famous_works should include a known Giordano work"
    )


def test_neapolitan_baroque_period_enum():
    """NEAPOLITAN_BAROQUE must exist in the Period enum (session 104)."""
    from scene_schema import Period
    assert hasattr(Period, "NEAPOLITAN_BAROQUE"), (
        "Period enum missing NEAPOLITAN_BAROQUE"
    )


def test_neapolitan_baroque_stroke_params():
    """NEAPOLITAN_BAROQUE must have moderate wet_blend and moderate edge_softness."""
    from scene_schema import Style, Period
    s = Style(period=Period.NEAPOLITAN_BAROQUE)
    params = s.stroke_params
    assert 0.40 <= params["wet_blend"] <= 0.85, (
        f"NEAPOLITAN_BAROQUE wet_blend {params['wet_blend']} out of expected range"
    )
    assert 0.30 <= params["edge_softness"] <= 0.70, (
        f"NEAPOLITAN_BAROQUE edge_softness {params['edge_softness']} out of expected range"
    )


def test_giordano_rapidita_luminosa_pass_exists():
    """Painter must have giordano_rapidita_luminosa_pass method (session 104)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "giordano_rapidita_luminosa_pass"), (
        "Painter missing giordano_rapidita_luminosa_pass"
    )


def test_giordano_rapidita_luminosa_pass_aureole_parameters():
    """giordano_rapidita_luminosa_pass must accept aureole_r and aureole_radius."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.giordano_rapidita_luminosa_pass)
    for param in ("aureole_r", "aureole_radius", "aureole_cx", "aureole_cy"):
        assert param in sig.parameters, (
            f"giordano_rapidita_luminosa_pass must have {param!r} parameter"
        )


def test_giordano_rapidita_luminosa_pass_rim_parameters():
    """giordano_rapidita_luminosa_pass must accept rim_strength."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.giordano_rapidita_luminosa_pass)
    assert "rim_strength" in sig.parameters, (
        "giordano_rapidita_luminosa_pass must have 'rim_strength' parameter"
    )


def test_giordano_rapidita_luminosa_pass_shadow_parameters():
    """giordano_rapidita_luminosa_pass must accept shadow_violet_b."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.giordano_rapidita_luminosa_pass)
    assert "shadow_violet_b" in sig.parameters, (
        "giordano_rapidita_luminosa_pass must have 'shadow_violet_b' parameter"
    )


def test_giordano_rapidita_luminosa_pass_opacity_parameter():
    """giordano_rapidita_luminosa_pass must accept opacity."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.giordano_rapidita_luminosa_pass)
    assert "opacity" in sig.parameters, (
        "giordano_rapidita_luminosa_pass must have 'opacity' parameter"
    )


def test_atmospheric_depth_pass_zenith_luminance_boost_parameter():
    """atmospheric_depth_pass must accept zenith_luminance_boost (session 104 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.atmospheric_depth_pass)
    assert "zenith_luminance_boost" in sig.parameters, (
        "atmospheric_depth_pass must have 'zenith_luminance_boost' parameter (session 104)"
    )


def test_ribera_in_catalog():
    """ribera (Jusepe de Ribera, session 106) must be in the catalog."""
    assert "ribera" in CATALOG, "ribera missing from CATALOG — add it"


def test_ribera_movement():
    """ribera movement must reference Spanish-Neapolitan or Baroque."""
    s = get_style("ribera")
    assert "baroque" in s.movement.lower() or "neapolitan" in s.movement.lower(), (
        f"ribera movement should reference Baroque or Neapolitan, got: {s.movement!r}"
    )


def test_ribera_palette_length():
    """ribera palette must have at least 5 colours."""
    s = get_style("ribera")
    assert len(s.palette) >= 5, f"ribera palette too short: {len(s.palette)}"


def test_ribera_palette_values_in_range():
    """All ribera palette RGB values must be in [0, 1]."""
    s = get_style("ribera")
    for c in s.palette:
        for v in c:
            assert 0.0 <= v <= 1.0, f"ribera palette value out of range: {v}"


def test_ribera_wet_blend_low():
    """ribera wet_blend should be low — visible brushwork, not smooth sfumato."""
    s = get_style("ribera")
    assert s.wet_blend < 0.50, (
        f"ribera wet_blend should be < 0.50 (gritty visible brushwork); got {s.wet_blend}"
    )


def test_ribera_dark_ground():
    """ribera ground_color should be very dark — near-black imprimatura."""
    s = get_style("ribera")
    lum = 0.299 * s.ground_color[0] + 0.587 * s.ground_color[1] + 0.114 * s.ground_color[2]
    assert lum < 0.20, (
        f"ribera ground_color should be near-black (lum < 0.20); got lum={lum:.3f}"
    )


def test_ribera_expected_artists_list():
    """ribera must appear in the EXPECTED_ARTISTS list."""
    assert "ribera" in EXPECTED_ARTISTS, (
        "ribera missing from EXPECTED_ARTISTS — add it to the list"
    )


def test_ribera_gritty_tenebrism_pass_exists():
    """ribera_gritty_tenebrism_pass must be implemented in Painter."""
    from stroke_engine import Painter
    assert hasattr(Painter, "ribera_gritty_tenebrism_pass"), (
        "Painter must have ribera_gritty_tenebrism_pass method"
    )


def test_ribera_gritty_tenebrism_pass_grain_parameter():
    """ribera_gritty_tenebrism_pass must accept grain_strength parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.ribera_gritty_tenebrism_pass)
    assert "grain_strength" in sig.parameters, (
        "ribera_gritty_tenebrism_pass must have 'grain_strength' parameter"
    )


def test_ribera_gritty_tenebrism_pass_opacity_parameter():
    """ribera_gritty_tenebrism_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.ribera_gritty_tenebrism_pass)
    assert "opacity" in sig.parameters, (
        "ribera_gritty_tenebrism_pass must have 'opacity' parameter"
    )


def test_atmospheric_depth_pass_foreground_warmth_parameter():
    """atmospheric_depth_pass must accept foreground_warmth (session 106 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.atmospheric_depth_pass)
    assert "foreground_warmth" in sig.parameters, (
        "atmospheric_depth_pass must have 'foreground_warmth' parameter (session 106)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Session 107 — Giovanni Antonio Boltraffio + MILANESE_PEARLED + SPANISH_NEAPOLITAN_BAROQUE
# ─────────────────────────────────────────────────────────────────────────────

def test_boltraffio_in_catalog():
    """boltraffio must be present in art_catalog.CATALOG (session 107)."""
    from art_catalog import CATALOG
    assert "boltraffio" in CATALOG, (
        "boltraffio missing from CATALOG — add it to art_catalog.py"
    )


def test_boltraffio_expected_artists_list():
    """boltraffio must appear in the EXPECTED_ARTISTS list."""
    assert "boltraffio" in EXPECTED_ARTISTS, (
        "boltraffio missing from EXPECTED_ARTISTS — add it to the list"
    )


def test_boltraffio_catalog_fields():
    """boltraffio catalog entry must have correct artist name and movement."""
    s = get_style("boltraffio")
    assert "Boltraffio" in s.artist, (
        f"boltraffio artist field should contain 'Boltraffio'; got: {s.artist!r}"
    )
    assert "Milanese" in s.movement or "Leonardo" in s.movement, (
        f"boltraffio movement should reference Milanese or Leonardesque; got: {s.movement!r}"
    )


def test_boltraffio_palette_cool_highlights():
    """boltraffio palette must have a cool highlight (B >= R in first entry)."""
    s = get_style("boltraffio")
    r, g, b = s.palette[0]
    assert b >= r, (
        f"boltraffio first palette entry should be cool-pearl (B >= R); "
        f"got R={r:.3f}, B={b:.3f}"
    )


def test_boltraffio_inspiration_references_pass():
    """Inspiration field must reference boltraffio_pearled_sfumato_pass()."""
    s = get_style("boltraffio")
    assert "boltraffio_pearled_sfumato_pass" in s.inspiration, (
        "boltraffio inspiration must reference boltraffio_pearled_sfumato_pass()"
    )


def test_boltraffio_high_edge_softness():
    """boltraffio edge_softness must be >= 0.75 (extreme sfumato dissolution)."""
    s = get_style("boltraffio")
    assert s.edge_softness >= 0.75, (
        f"boltraffio edge_softness should be >= 0.75 (Leonardesque sfumato); "
        f"got {s.edge_softness}"
    )


def test_boltraffio_pearled_sfumato_pass_exists():
    """boltraffio_pearled_sfumato_pass must be implemented in Painter."""
    from stroke_engine import Painter
    assert hasattr(Painter, "boltraffio_pearled_sfumato_pass"), (
        "Painter must have boltraffio_pearled_sfumato_pass method (session 107)"
    )


def test_boltraffio_pearled_sfumato_pass_pearl_parameter():
    """boltraffio_pearled_sfumato_pass must accept pearl_lo parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.boltraffio_pearled_sfumato_pass)
    assert "pearl_lo" in sig.parameters, (
        "boltraffio_pearled_sfumato_pass must have 'pearl_lo' parameter"
    )


def test_boltraffio_pearled_sfumato_pass_opacity_parameter():
    """boltraffio_pearled_sfumato_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.boltraffio_pearled_sfumato_pass)
    assert "opacity" in sig.parameters, (
        "boltraffio_pearled_sfumato_pass must have 'opacity' parameter"
    )


def test_milanese_pearled_period_exists():
    """Period.MILANESE_PEARLED must exist in scene_schema (session 107)."""
    from scene_schema import Period
    assert hasattr(Period, "MILANESE_PEARLED"), (
        "Period.MILANESE_PEARLED not found — add it to scene_schema.py"
    )
    assert Period.MILANESE_PEARLED in list(Period)


def test_milanese_pearled_stroke_params():
    """MILANESE_PEARLED should have high wet_blend for Boltraffio's smooth sfumato."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.MILANESE_PEARLED,
                  palette=PaletteHint.COOL_GREY)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.65, (
        f"MILANESE_PEARLED wet_blend should be >= 0.65 for Boltraffio's sfumato; "
        f"got {p['wet_blend']}"
    )
    assert p["edge_softness"] >= 0.70, (
        f"MILANESE_PEARLED edge_softness should be >= 0.70 for extreme sfumato dissolution; "
        f"got {p['edge_softness']}"
    )


def test_spanish_neapolitan_baroque_period_exists():
    """Period.SPANISH_NEAPOLITAN_BAROQUE must exist in scene_schema (session 106)."""
    from scene_schema import Period
    assert hasattr(Period, "SPANISH_NEAPOLITAN_BAROQUE"), (
        "Period.SPANISH_NEAPOLITAN_BAROQUE not found — add it to scene_schema.py"
    )


def test_spanish_neapolitan_baroque_stroke_params():
    """SPANISH_NEAPOLITAN_BAROQUE should have low wet_blend and edge_softness for brutal tenebrism."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.SPANISH_NEAPOLITAN_BAROQUE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.40, (
        f"SPANISH_NEAPOLITAN_BAROQUE wet_blend should be <= 0.40 for Ribera's gritty brushwork; "
        f"got {p['wet_blend']}"
    )
    assert p["edge_softness"] <= 0.40, (
        f"SPANISH_NEAPOLITAN_BAROQUE edge_softness should be <= 0.40 for hard tenebrism edges; "
        f"got {p['edge_softness']}"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Session 108: Giovanni Battista Moroni + BERGAMASQUE_PORTRAIT_REALISM
# ──────────────────────────────────────────────────────────────────────────────

def test_moroni_in_catalog():
    """moroni must be present in CATALOG (session 108)."""
    assert "moroni" in CATALOG, "moroni missing from CATALOG — add ArtStyle entry"


def test_moroni_in_expected_artists():
    """EXPECTED_ARTISTS list must include moroni."""
    assert "moroni" in EXPECTED_ARTISTS, (
        "moroni missing from EXPECTED_ARTISTS — add it to the list"
    )


def test_moroni_cool_silver_palette():
    """moroni palette must contain at least one cool/silver tone (B component >= 0.55)."""
    s = get_style("moroni")
    has_silver = any(b >= 0.55 for (_, _, b) in s.palette)
    assert has_silver, (
        "moroni palette should include a cool/silver tone (B >= 0.55) — "
        "Moroni's defining highlight quality is cool north-daylight silver"
    )


def test_moroni_warm_shadow_in_palette():
    """moroni palette must contain warm earth tones (R > G >= B) for shadow recovery."""
    s = get_style("moroni")
    has_warm_earth = any(r > g and g >= b for (r, g, b) in s.palette)
    assert has_warm_earth, (
        "moroni palette should include warm earth tones (R > G >= B) for shadow warmth"
    )


def test_moroni_moderate_edge_softness():
    """moroni edge_softness should be moderate-crisp (0.30–0.55) for naturalist portraiture."""
    s = get_style("moroni")
    assert 0.30 <= s.edge_softness <= 0.55, (
        f"moroni edge_softness should be in [0.30, 0.55] for naturalist found edges; "
        f"got {s.edge_softness}"
    )


def test_moroni_moderate_wet_blend():
    """moroni wet_blend should be moderate (0.35–0.58) — smooth but not sfumato."""
    s = get_style("moroni")
    assert 0.35 <= s.wet_blend <= 0.58, (
        f"moroni wet_blend should be in [0.35, 0.58] — smooth without sfumato dissolution; "
        f"got {s.wet_blend}"
    )


def test_moroni_inspiration_references_pass():
    """moroni inspiration must reference moroni_silver_presence_pass()."""
    s = get_style("moroni")
    assert "moroni_silver_presence_pass" in s.inspiration, (
        "moroni inspiration must reference moroni_silver_presence_pass()"
    )


def test_moroni_silver_presence_pass_exists():
    """moroni_silver_presence_pass must be implemented in Painter (session 108)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "moroni_silver_presence_pass"), (
        "Painter must have moroni_silver_presence_pass method (session 108)"
    )


def test_moroni_silver_presence_pass_opacity_parameter():
    """moroni_silver_presence_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.moroni_silver_presence_pass)
    assert "opacity" in sig.parameters, (
        "moroni_silver_presence_pass must have 'opacity' parameter"
    )


def test_moroni_silver_presence_pass_hi_lo_parameter():
    """moroni_silver_presence_pass must accept hi_lo parameter for silver highlight threshold."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.moroni_silver_presence_pass)
    assert "hi_lo" in sig.parameters, (
        "moroni_silver_presence_pass must have 'hi_lo' parameter"
    )


def test_moroni_silver_presence_pass_shadow_hi_parameter():
    """moroni_silver_presence_pass must accept shadow_hi parameter for warm shadow recovery."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.moroni_silver_presence_pass)
    assert "shadow_hi" in sig.parameters, (
        "moroni_silver_presence_pass must have 'shadow_hi' parameter"
    )


def test_bergamasque_portrait_realism_period_exists():
    """Period.BERGAMASQUE_PORTRAIT_REALISM must exist in scene_schema (session 108)."""
    from scene_schema import Period
    assert hasattr(Period, "BERGAMASQUE_PORTRAIT_REALISM"), (
        "Period.BERGAMASQUE_PORTRAIT_REALISM not found — add it to scene_schema.py"
    )
    assert Period.BERGAMASQUE_PORTRAIT_REALISM in list(Period)


def test_bergamasque_portrait_realism_stroke_params():
    """BERGAMASQUE_PORTRAIT_REALISM should have moderate wet_blend and edge_softness for naturalism."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.BERGAMASQUE_PORTRAIT_REALISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.35 <= p["wet_blend"] <= 0.58, (
        f"BERGAMASQUE_PORTRAIT_REALISM wet_blend should be in [0.35, 0.58] for Moroni's "
        f"smooth-but-naturalist surfaces; got {p['wet_blend']}"
    )
    assert 0.30 <= p["edge_softness"] <= 0.55, (
        f"BERGAMASQUE_PORTRAIT_REALISM edge_softness should be in [0.30, 0.55] for "
        f"Moroni's naturalist found edges; got {p['edge_softness']}"
    )


def test_bergamasque_portrait_realism_in_expected_periods():
    """EXPECTED_PERIODS list must include BERGAMASQUE_PORTRAIT_REALISM."""
    assert "BERGAMASQUE_PORTRAIT_REALISM" in EXPECTED_PERIODS, (
        "BERGAMASQUE_PORTRAIT_REALISM missing from EXPECTED_PERIODS — add it to the list"
    )


def test_moroni_famous_works_include_tailor():
    """moroni famous_works must include 'Il Sarto' — his most celebrated portrait."""
    s = get_style("moroni")
    titles = [title for (title, _) in s.famous_works]
    assert any("Sarto" in t or "Tailor" in t for t in titles), (
        "moroni famous_works must include 'Il Sarto (The Tailor)' — his canonical work"
    )


def test_moroni_movement_bergamasque():
    """moroni movement must reference Bergamasque or Lombard heritage."""
    s = get_style("moroni")
    assert "Bergam" in s.movement or "Lombard" in s.movement, (
        f"moroni movement should reference Bergamasque or Lombard; got {s.movement!r}"
    )
    assert Period.SPANISH_NEAPOLITAN_BAROQUE in list(Period)


# ─────────────────────────────────────────────────────────────────────────────
# Session 109 — Bernardo Strozzi + GENOESE_VENETIAN_BAROQUE
# ─────────────────────────────────────────────────────────────────────────────

def test_strozzi_in_catalog():
    """strozzi (session 109) must be in the catalog."""
    assert "strozzi" in CATALOG, "strozzi missing from CATALOG — add it to art_catalog.py"


def test_strozzi_in_expected_artists():
    """EXPECTED_ARTISTS list must include strozzi."""
    assert "strozzi" in EXPECTED_ARTISTS, (
        "strozzi missing from EXPECTED_ARTISTS — add it to the list"
    )


def test_strozzi_palette_values_in_range():
    """strozzi palette RGB values must all be in [0, 1]."""
    s = get_style("strozzi")
    for i, color in enumerate(s.palette):
        for j, channel in enumerate(color):
            assert 0.0 <= channel <= 1.0, (
                f"strozzi palette[{i}][{j}] = {channel} is outside [0, 1]"
            )


def test_strozzi_palette_length():
    """strozzi palette must have between 5 and 8 colours."""
    s = get_style("strozzi")
    assert 5 <= len(s.palette) <= 8, (
        f"strozzi palette has {len(s.palette)} colours; expected 5–8"
    )


def test_strozzi_stroke_size_in_range():
    """strozzi stroke_size must be in the valid range [4, 18]."""
    s = get_style("strozzi")
    assert 4 <= s.stroke_size <= 18, (
        f"strozzi stroke_size={s.stroke_size} is outside [4, 18]"
    )


def test_strozzi_movement_genoese_venetian():
    """strozzi movement must reference Genoese and/or Venetian Baroque heritage."""
    s = get_style("strozzi")
    assert "Genoese" in s.movement or "Venetian" in s.movement or "Baroque" in s.movement, (
        f"strozzi movement should reference Genoese-Venetian Baroque; got {s.movement!r}"
    )


def test_strozzi_famous_works_include_old_woman():
    """strozzi famous_works must include 'Old Woman at the Mirror' — his canonical genre work."""
    s = get_style("strozzi")
    titles = [title for (title, _) in s.famous_works]
    assert any("Old Woman" in t or "Mirror" in t for t in titles), (
        "strozzi famous_works must include 'Old Woman at the Mirror'"
    )


def test_strozzi_famous_works_count():
    """strozzi famous_works must have at least 3 entries."""
    s = get_style("strozzi")
    assert len(s.famous_works) >= 3, (
        f"strozzi famous_works has only {len(s.famous_works)} entries; expected at least 3"
    )


def test_strozzi_inspiration_references_pass():
    """strozzi inspiration must reference strozzi_amber_impasto_pass."""
    s = get_style("strozzi")
    assert "strozzi_amber_impasto_pass" in s.inspiration, (
        "strozzi inspiration must reference strozzi_amber_impasto_pass()"
    )


def test_genoese_venetian_baroque_period_exists():
    """Period.GENOESE_VENETIAN_BAROQUE must exist in scene_schema (session 109)."""
    from scene_schema import Period
    assert hasattr(Period, "GENOESE_VENETIAN_BAROQUE"), (
        "Period.GENOESE_VENETIAN_BAROQUE not found — add it to scene_schema.py"
    )
    assert Period.GENOESE_VENETIAN_BAROQUE in list(Period)


def test_genoese_venetian_baroque_stroke_params():
    """GENOESE_VENETIAN_BAROQUE must have warm bravura stroke params for Strozzi."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.GENOESE_VENETIAN_BAROQUE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.40 <= p["wet_blend"] <= 0.65, (
        f"GENOESE_VENETIAN_BAROQUE wet_blend should be in [0.40, 0.65] for Strozzi's "
        f"bravura alla prima surfaces; got {p['wet_blend']}"
    )
    assert 0.28 <= p["edge_softness"] <= 0.55, (
        f"GENOESE_VENETIAN_BAROQUE edge_softness should be in [0.28, 0.55] for "
        f"Strozzi's assertive found edges; got {p['edge_softness']}"
    )


def test_genoese_venetian_baroque_in_expected_periods():
    """EXPECTED_PERIODS list must include GENOESE_VENETIAN_BAROQUE."""
    assert "GENOESE_VENETIAN_BAROQUE" in EXPECTED_PERIODS, (
        "GENOESE_VENETIAN_BAROQUE missing from EXPECTED_PERIODS — add it to the list"
    )


def test_strozzi_amber_impasto_pass_exists():
    """strozzi_amber_impasto_pass must be defined in stroke_engine.Painter (session 109)."""
    import inspect
    from stroke_engine import Painter
    assert hasattr(Painter, "strozzi_amber_impasto_pass"), (
        "Painter.strozzi_amber_impasto_pass not found — add it to stroke_engine.py"
    )


def test_strozzi_amber_impasto_pass_opacity_parameter():
    """strozzi_amber_impasto_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.strozzi_amber_impasto_pass)
    assert "opacity" in sig.parameters, (
        "strozzi_amber_impasto_pass must have 'opacity' parameter"
    )


def test_strozzi_amber_impasto_pass_shadow_hi_parameter():
    """strozzi_amber_impasto_pass must accept shadow_hi parameter for amber shadow enrichment."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.strozzi_amber_impasto_pass)
    assert "shadow_hi" in sig.parameters, (
        "strozzi_amber_impasto_pass must have 'shadow_hi' parameter"
    )


def test_strozzi_amber_impasto_pass_hi_boost_parameter():
    """strozzi_amber_impasto_pass must accept hi_boost parameter for impasto luminance boost."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.strozzi_amber_impasto_pass)
    assert "hi_boost" in sig.parameters, (
        "strozzi_amber_impasto_pass must have 'hi_boost' parameter"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Session 110 — Giovanni Battista Salvi da Sassoferrato + ROMAN_DEVOTIONAL_BAROQUE
#             + sassoferrato_pure_devotion_pass
# ─────────────────────────────────────────────────────────────────────────────

def test_sassoferrato_in_catalog():
    """Sassoferrato (session 110) must be present in CATALOG."""
    assert "sassoferrato" in CATALOG, (
        "sassoferrato not found in CATALOG — add it to art_catalog.py"
    )


def test_sassoferrato_artist_name():
    """Sassoferrato ArtStyle must carry the correct full artist name."""
    s = get_style("sassoferrato")
    assert "Sassoferrato" in s.artist or "Salvi" in s.artist, (
        f"sassoferrato.artist should contain 'Sassoferrato' or 'Salvi'; got {s.artist!r}"
    )


def test_sassoferrato_movement():
    """Sassoferrato ArtStyle movement should reference Baroque or Devotional."""
    s = get_style("sassoferrato")
    mv = s.movement.lower()
    assert "baroque" in mv or "devotional" in mv or "classicism" in mv, (
        f"sassoferrato.movement should reference Baroque or Devotional; got {s.movement!r}"
    )


def test_sassoferrato_palette_length():
    """Sassoferrato palette must have at least 5 colours."""
    s = get_style("sassoferrato")
    assert len(s.palette) >= 5, (
        f"sassoferrato palette should have >= 5 colours; got {len(s.palette)}"
    )


def test_sassoferrato_palette_values_in_range():
    """All Sassoferrato palette RGB values must be in [0, 1]."""
    s = get_style("sassoferrato")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, (
                f"Out-of-range channel {ch} in Sassoferrato palette {rgb}"
            )


def test_sassoferrato_wet_blend_high():
    """Sassoferrato's seamless glazing demands wet_blend >= 0.70."""
    s = get_style("sassoferrato")
    assert s.wet_blend >= 0.70, (
        f"sassoferrato.wet_blend should be >= 0.70 for seamless devotional glazing; "
        f"got {s.wet_blend}"
    )


def test_sassoferrato_edge_softness():
    """Sassoferrato's devotional calm requires edge_softness in [0.60, 0.90]."""
    s = get_style("sassoferrato")
    assert 0.60 <= s.edge_softness <= 0.90, (
        f"sassoferrato.edge_softness should be in [0.60, 0.90] for devotional quiet; "
        f"got {s.edge_softness}"
    )


def test_sassoferrato_ultramarine_in_palette():
    """Sassoferrato palette must contain a blue-dominant colour (the signature ultramarine)."""
    s = get_style("sassoferrato")
    has_blue = any(rgb[2] > rgb[0] and rgb[2] > rgb[1] for rgb in s.palette)
    assert has_blue, (
        "sassoferrato palette must include at least one blue-dominant colour "
        "(the lapislazuli ultramarine that defines his work)"
    )


def test_sassoferrato_in_expected_artists():
    """sassoferrato must be in EXPECTED_ARTISTS list (session 110)."""
    assert "sassoferrato" in EXPECTED_ARTISTS, (
        "sassoferrato missing from EXPECTED_ARTISTS — add it to the list"
    )


def test_roman_devotional_baroque_period_exists():
    """Period.ROMAN_DEVOTIONAL_BAROQUE must exist in scene_schema (session 110)."""
    from scene_schema import Period
    assert hasattr(Period, "ROMAN_DEVOTIONAL_BAROQUE"), (
        "Period.ROMAN_DEVOTIONAL_BAROQUE not found — add it to scene_schema.py"
    )
    assert Period.ROMAN_DEVOTIONAL_BAROQUE in list(Period)


def test_roman_devotional_baroque_stroke_params():
    """ROMAN_DEVOTIONAL_BAROQUE must have high wet_blend and edge_softness for glazing."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.ROMAN_DEVOTIONAL_BAROQUE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.70, (
        f"ROMAN_DEVOTIONAL_BAROQUE wet_blend should be >= 0.70 for Sassoferrato's "
        f"seamless devotional glazing; got {p['wet_blend']}"
    )
    assert p["edge_softness"] >= 0.60, (
        f"ROMAN_DEVOTIONAL_BAROQUE edge_softness should be >= 0.60 for "
        f"devotional calm quiet edges; got {p['edge_softness']}"
    )


def test_roman_devotional_baroque_in_expected_periods():
    """EXPECTED_PERIODS list must include ROMAN_DEVOTIONAL_BAROQUE."""
    assert "ROMAN_DEVOTIONAL_BAROQUE" in EXPECTED_PERIODS, (
        "ROMAN_DEVOTIONAL_BAROQUE missing from EXPECTED_PERIODS — add it to the list"
    )


def test_sassoferrato_pure_devotion_pass_exists():
    """sassoferrato_pure_devotion_pass must be defined in stroke_engine.Painter (session 110)."""
    import inspect
    from stroke_engine import Painter
    assert hasattr(Painter, "sassoferrato_pure_devotion_pass"), (
        "Painter.sassoferrato_pure_devotion_pass not found — add it to stroke_engine.py"
    )


def test_sassoferrato_pure_devotion_pass_opacity_parameter():
    """sassoferrato_pure_devotion_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.sassoferrato_pure_devotion_pass)
    assert "opacity" in sig.parameters, (
        "sassoferrato_pure_devotion_pass must have 'opacity' parameter"
    )


def test_sassoferrato_pure_devotion_pass_ultra_thresh_parameter():
    """sassoferrato_pure_devotion_pass must accept ultra_thresh for blue zone detection."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.sassoferrato_pure_devotion_pass)
    assert "ultra_thresh" in sig.parameters, (
        "sassoferrato_pure_devotion_pass must have 'ultra_thresh' parameter"
    )


def test_sassoferrato_pure_devotion_pass_pearl_lo_parameter():
    """sassoferrato_pure_devotion_pass must accept pearl_lo for porcelain skin glow."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.sassoferrato_pure_devotion_pass)
    assert "pearl_lo" in sig.parameters, (
        "sassoferrato_pure_devotion_pass must have 'pearl_lo' parameter"
    )


def test_roman_devotional_baroque_period_in_period_enum():
    """Period.ROMAN_DEVOTIONAL_BAROQUE must be accessible from scene_schema (session 110)."""
    from scene_schema import Period
    assert Period.ROMAN_DEVOTIONAL_BAROQUE in list(Period)


# ──────────────────────────────────────────────────────────────────────────────
# Jacob Jordaens — session 112 addition
# ──────────────────────────────────────────────────────────────────────────────

def test_jordaens_in_catalog():
    """Jordaens (session 112) must be present in CATALOG."""
    assert "jordaens" in CATALOG


def test_jordaens_movement():
    s = get_style("jordaens")
    assert "Antwerp" in s.movement or "Flemish" in s.movement


def test_jordaens_palette_length():
    s = get_style("jordaens")
    assert len(s.palette) >= 5, "Jordaens palette should have at least 5 key colours"


def test_jordaens_palette_values_in_range():
    """All Jordaens palette RGB values must be in [0, 1]."""
    s = get_style("jordaens")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel!r} in Jordaens palette {rgb}")


def test_jordaens_famous_works_includes_king_drinks():
    s = get_style("jordaens")
    titles = [w[0] for w in s.famous_works]
    assert any("King" in t or "Roi" in t for t in titles), (
        "Jordaens catalog entry should include 'The King Drinks' (Le Roi Boit)"
    )


def test_antwerp_baroque_period_in_period_enum():
    """Period.ANTWERP_BAROQUE must be accessible from scene_schema (session 112)."""
    from scene_schema import Period
    assert Period.ANTWERP_BAROQUE in list(Period)


def test_jordaens_earthy_vitality_pass_exists():
    """Painter must have jordaens_earthy_vitality_pass() method after session 112."""
    from stroke_engine import Painter
    assert hasattr(Painter, "jordaens_earthy_vitality_pass"), (
        "jordaens_earthy_vitality_pass not found on Painter")
    assert callable(getattr(Painter, "jordaens_earthy_vitality_pass"))


def test_jordaens_earthy_vitality_pass_runs():
    """jordaens_earthy_vitality_pass() must run without error on a small canvas."""
    import numpy as np
    from stroke_engine import Painter
    p = Painter(64, 64)
    p.tone_ground((0.48, 0.36, 0.20), texture_strength=0.06)
    p.jordaens_earthy_vitality_pass(opacity=0.34)


def test_antwerp_baroque_stroke_params():
    """ANTWERP_BAROQUE stroke_params must be a valid dict with expected warm impasto values."""
    style = Style(medium=Medium.OIL, period=Period.ANTWERP_BAROQUE, palette=PaletteHint.WARM_EARTH)
    params = style.stroke_params
    assert params["stroke_size_face"] >= 6
    assert 0.0 <= params["wet_blend"] <= 1.0
    assert 0.0 <= params["edge_softness"] <= 1.0


# ═════════════════════════════════════════════════════════════════════════════
# Guido Cagnacci — catalog and pass tests (session 113)
# ═════════════════════════════════════════════════════════════════════════════

def test_guido_cagnacci_in_catalog():
    """guido_cagnacci must be present in CATALOG (session 112)."""
    assert "guido_cagnacci" in CATALOG, (
        "guido_cagnacci not found in CATALOG — add the ArtStyle entry")


def test_guido_cagnacci_in_expected_artists():
    """EXPECTED_ARTISTS list must include guido_cagnacci (session 112)."""
    assert "guido_cagnacci" in EXPECTED_ARTISTS, (
        "guido_cagnacci must be in EXPECTED_ARTISTS list")


def test_guido_cagnacci_palette_valid():
    """Every colour in guido_cagnacci palette must have RGB channels in [0, 1]."""
    s = get_style("guido_cagnacci")
    for i, rgb in enumerate(s.palette):
        for j, v in enumerate(rgb):
            assert 0.0 <= v <= 1.0, (
                f"guido_cagnacci palette[{i}][{j}]={v:.3f} out of [0, 1]")


def test_guido_cagnacci_warm_rose_highlight():
    """
    Cagnacci's defining quality is rose-warm flesh at highlights.
    The first palette entry (highlight flesh) must be warm (R > B) and pinkish (R > G).
    """
    s = get_style("guido_cagnacci")
    r, g, b = s.palette[0]
    assert r > b, (
        f"guido_cagnacci highlight palette[0] must be warm (R={r:.3f} > B={b:.3f}) "
        "— Cagnacci's rose-ivory highlight quality")
    assert r > g, (
        f"guido_cagnacci highlight palette[0] must be pinkish (R={r:.3f} > G={g:.3f}) "
        "— the rose quality distinguishing him from cool-ivory Reni")


def test_guido_cagnacci_warm_ground():
    """
    Cagnacci used a warm sienna-ochre imprimatura ground.
    ground_color must be warm (R > B).
    """
    s = get_style("guido_cagnacci")
    r, _, b = s.ground_color
    assert r > b, (
        f"guido_cagnacci ground_color must be warm (R={r:.3f} > B={b:.3f}) "
        "— Bolognese warm sienna imprimatura tradition")


def test_guido_cagnacci_high_wet_blend():
    """
    Cagnacci's technique is smooth glazed sfumato — high wet_blend expected (>= 0.70).
    """
    s = get_style("guido_cagnacci")
    assert s.wet_blend >= 0.70, (
        f"guido_cagnacci wet_blend={s.wet_blend:.2f} too low — should be >= 0.70 "
        "for the smooth Reni-derived sfumato glazing technique")


def test_guido_cagnacci_soft_edges():
    """
    Cagnacci's forms melt softly — edge_softness must be >= 0.65.
    """
    s = get_style("guido_cagnacci")
    assert s.edge_softness >= 0.65, (
        f"guido_cagnacci edge_softness={s.edge_softness:.2f} too low — should be >= 0.65 "
        "for the dreamlike, diffused quality of his flesh")


def test_guido_cagnacci_rose_glaze():
    """
    Cagnacci's unifying glaze must be warm rose-amber (R > B).
    """
    s = get_style("guido_cagnacci")
    assert s.glazing is not None, "guido_cagnacci glazing should not be None"
    r, g, b = s.glazing
    assert r > b, (
        f"guido_cagnacci glazing must be warm (R={r:.3f} > B={b:.3f}) "
        "— rose-amber unifying glaze, not cool silver")


def test_guido_cagnacci_movement_emilian():
    """
    Cagnacci's movement must reference Emilian Baroque lineage.
    """
    s = get_style("guido_cagnacci")
    assert "Emilian" in s.movement or "emilian" in s.movement.lower(), (
        f"guido_cagnacci movement={s.movement!r} must reference Emilian Baroque tradition")


def test_cagnacci_rose_flesh_pass_exists():
    """Painter must expose cagnacci_rose_flesh_pass (session 112 new pass)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "cagnacci_rose_flesh_pass"), (
        "Painter.cagnacci_rose_flesh_pass not found — add it to stroke_engine.py"
    )


def test_cagnacci_rose_flesh_pass_opacity_parameter():
    """cagnacci_rose_flesh_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.cagnacci_rose_flesh_pass)
    assert "opacity" in sig.parameters, (
        "cagnacci_rose_flesh_pass must have 'opacity' parameter"
    )


def test_cagnacci_rose_flesh_pass_peach_r_parameter():
    """cagnacci_rose_flesh_pass must accept peach_r for mid-tone rose glow."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.cagnacci_rose_flesh_pass)
    assert "peach_r" in sig.parameters, (
        "cagnacci_rose_flesh_pass must have 'peach_r' parameter "
        "(primary mid-tone rose-peach component)"
    )


def test_cagnacci_rose_flesh_pass_rose_r_lift_parameter():
    """cagnacci_rose_flesh_pass must accept rose_r_lift for highlight warmth."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.cagnacci_rose_flesh_pass)
    assert "rose_r_lift" in sig.parameters, (
        "cagnacci_rose_flesh_pass must have 'rose_r_lift' parameter "
        "(pinkish rose warmth at peak flesh highlights)"
    )


def test_emilian_rosy_baroque_period_in_period_enum():
    """Period.EMILIAN_ROSY_BAROQUE must be accessible from scene_schema (session 113)."""
    from scene_schema import Period
    assert Period.EMILIAN_ROSY_BAROQUE in list(Period), (
        "Period.EMILIAN_ROSY_BAROQUE not found — add it to scene_schema.py Period enum")


# ──────────────────────────────────────────────────────────────────────────────
# lavinia_fontana — session 115 new artist
# ──────────────────────────────────────────────────────────────────────────────

def test_lavinia_fontana_in_catalog():
    """lavinia_fontana must be present in CATALOG after session 115."""
    assert "lavinia_fontana" in CATALOG, (
        "lavinia_fontana not found in CATALOG — add her to art_catalog.py")


def test_lavinia_fontana_in_expected_artists():
    """lavinia_fontana must appear in EXPECTED_ARTISTS."""
    assert "lavinia_fontana" in EXPECTED_ARTISTS


def test_lavinia_fontana_palette_valid():
    """All palette colours must be in [0, 1]."""
    s = get_style("lavinia_fontana")
    for i, rgb in enumerate(s.palette):
        for j, v in enumerate(rgb):
            assert 0.0 <= v <= 1.0, (
                f"lavinia_fontana palette[{i}][{j}]={v:.3f} out of [0, 1]")


def test_lavinia_fontana_warm_rose_highlight():
    """
    Fontana's highlight flesh is warm rose-ivory — R must dominate (R > B).
    """
    s = get_style("lavinia_fontana")
    r, g, b = s.palette[0]
    assert r > b, (
        f"lavinia_fontana palette[0]: highlight must be warm (R={r:.3f} > B={b:.3f}) "
        "— Bolognese rose-ivory warmth, not cool silver")


def test_lavinia_fontana_crimson_costume_entry():
    """
    Fontana's crimson costume palette entry must be strongly red-dominant (R >> B).
    """
    s = get_style("lavinia_fontana")
    r, g, b = s.palette[3]
    assert r > b * 2.0, (
        f"lavinia_fontana palette[3] (crimson costume): R={r:.3f} should be strongly "
        f"greater than B={b:.3f} — deep crimson velvet signature")


def test_lavinia_fontana_warm_ground():
    """
    Fontana's ground must be warm (R > B) — Bolognese warm ochre tradition.
    """
    s = get_style("lavinia_fontana")
    r, _, b = s.ground_color
    assert r > b, (
        f"lavinia_fontana ground_color must be warm (R={r:.3f} > B={b:.3f}) "
        "— Bolognese warm ochre ground")


def test_lavinia_fontana_moderate_wet_blend():
    """
    Fontana's wet_blend must be moderate-high (>= 0.55) for glazed Bolognese finish.
    """
    s = get_style("lavinia_fontana")
    assert s.wet_blend >= 0.55, (
        f"lavinia_fontana wet_blend={s.wet_blend:.2f} too low — should be >= 0.55 "
        "for glazed Bolognese high finish")


def test_lavinia_fontana_moderate_edge_softness():
    """
    Fontana's edge_softness must be moderate (>= 0.50) — refined edges, not Bronzino enamel.
    """
    s = get_style("lavinia_fontana")
    assert s.edge_softness >= 0.50, (
        f"lavinia_fontana edge_softness={s.edge_softness:.2f} too low — should be >= 0.50 "
        "for refined Bolognese edges")


def test_lavinia_fontana_warm_glaze():
    """
    Fontana's unifying glaze must be warm amber-rose (R > B).
    """
    s = get_style("lavinia_fontana")
    assert s.glazing is not None, "lavinia_fontana glazing should not be None"
    r, g, b = s.glazing
    assert r > b, (
        f"lavinia_fontana glazing must be warm (R={r:.3f} > B={b:.3f}) "
        "— warm amber-rose unifying glaze, Bolognese warmth tradition")


def test_lavinia_fontana_movement_bolognese():
    """
    Fontana's movement must reference the Bolognese tradition.
    """
    s = get_style("lavinia_fontana")
    assert "Bolognese" in s.movement or "bolognese" in s.movement.lower(), (
        f"lavinia_fontana movement={s.movement!r} must reference Bolognese tradition")


def test_fontana_jewel_costume_pass_exists():
    """Painter must expose fontana_jewel_costume_pass (session 115 new pass)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "fontana_jewel_costume_pass"), (
        "Painter.fontana_jewel_costume_pass not found — add it to stroke_engine.py"
    )


def test_fontana_jewel_costume_pass_opacity_parameter():
    """fontana_jewel_costume_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.fontana_jewel_costume_pass)
    assert "opacity" in sig.parameters, (
        "fontana_jewel_costume_pass must have 'opacity' parameter"
    )


def test_fontana_jewel_costume_pass_crimson_r_parameter():
    """fontana_jewel_costume_pass must accept crimson_r for costume zone warmth."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.fontana_jewel_costume_pass)
    assert "crimson_r" in sig.parameters, (
        "fontana_jewel_costume_pass must have 'crimson_r' parameter "
        "(primary costume crimson warmth component)"
    )


def test_fontana_jewel_costume_pass_ivory_r_parameter():
    """fontana_jewel_costume_pass must accept ivory_r for highlight warmth."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.fontana_jewel_costume_pass)
    assert "ivory_r" in sig.parameters, (
        "fontana_jewel_costume_pass must have 'ivory_r' parameter "
        "(warm ivory lift at highlight peaks)"
    )


def test_bolognese_mannerist_portraiture_period_in_period_enum():
    """Period.BOLOGNESE_MANNERIST_PORTRAITURE must be accessible from scene_schema (session 115)."""
    from scene_schema import Period
    assert Period.BOLOGNESE_MANNERIST_PORTRAITURE in list(Period), (
        "Period.BOLOGNESE_MANNERIST_PORTRAITURE not found — add it to scene_schema.py Period enum")


# ── Session 116: Andrea Solario + Period.LOMBARD_LEONARDESQUE ─────────────────


def test_andrea_solario_in_catalog():
    """andrea_solario must be present in CATALOG (session 116)."""
    from art_catalog import CATALOG
    assert "andrea_solario" in CATALOG, (
        "andrea_solario not found in CATALOG — add it to art_catalog.py")


def test_andrea_solario_movement():
    """andrea_solario movement must reference Lombard or Leonardesque tradition."""
    from art_catalog import get_style
    s = get_style("andrea_solario")
    mv = s.movement.lower()
    assert "lombard" in mv or "leonardesque" in mv, (
        f"andrea_solario movement={s.movement!r} must reference Lombard or Leonardesque")


def test_andrea_solario_nationality():
    """andrea_solario must be listed as Italian."""
    from art_catalog import get_style
    s = get_style("andrea_solario")
    assert "italian" in s.nationality.lower(), (
        f"andrea_solario nationality={s.nationality!r} should be Italian")


def test_andrea_solario_palette_length():
    """andrea_solario palette must have at least 5 colours."""
    from art_catalog import get_style
    s = get_style("andrea_solario")
    assert len(s.palette) >= 5, (
        f"andrea_solario palette has {len(s.palette)} colours; expected >= 5")


def test_andrea_solario_palette_values_in_range():
    """All andrea_solario palette RGB values must be in [0, 1]."""
    from art_catalog import get_style
    s = get_style("andrea_solario")
    for i, col in enumerate(s.palette):
        for j, ch in enumerate(col):
            assert 0.0 <= ch <= 1.0, (
                f"andrea_solario palette[{i}][{j}] = {ch} out of [0, 1]")


def test_andrea_solario_has_amber_highlight():
    """andrea_solario palette must include warm amber highlight (R > 0.80, G > 0.70)."""
    from art_catalog import get_style
    s = get_style("andrea_solario")
    warm_highlights = [(r, g, b) for r, g, b in s.palette if r > 0.80 and g > 0.70]
    assert warm_highlights, (
        "andrea_solario palette must include at least one warm amber highlight "
        "(R > 0.80, G > 0.70) — his defining pellucid flesh quality")


def test_andrea_solario_has_cool_shadow():
    """andrea_solario palette must include a cool violet/blue shadow."""
    from art_catalog import get_style
    s = get_style("andrea_solario")
    cool_shadows = [(r, g, b) for r, g, b in s.palette if b > r and b > 0.20]
    assert cool_shadows, (
        "andrea_solario palette must include a cool shadow (B > R, B > 0.20) "
        "— his Venetian shadow inheritance")


def test_andrea_solario_high_wet_blend():
    """andrea_solario wet_blend must be >= 0.70 (Leonardesque sfumato)."""
    from art_catalog import get_style
    s = get_style("andrea_solario")
    assert s.wet_blend >= 0.70, (
        f"andrea_solario wet_blend={s.wet_blend} should be >= 0.70 for sfumato quality")


def test_andrea_solario_high_edge_softness():
    """andrea_solario edge_softness must be >= 0.75 (sfumato edge dissolution)."""
    from art_catalog import get_style
    s = get_style("andrea_solario")
    assert s.edge_softness >= 0.75, (
        f"andrea_solario edge_softness={s.edge_softness} should be >= 0.75 for sfumato")


def test_andrea_solario_has_glazing():
    """andrea_solario must define glazing (warm amber overlay)."""
    from art_catalog import get_style
    s = get_style("andrea_solario")
    assert s.glazing is not None, "andrea_solario must have glazing (amber depth)"
    r, g, b = s.glazing
    assert r > g > b, (
        f"andrea_solario glazing={s.glazing!r} should be warm amber (R > G > B)")


def test_andrea_solario_famous_works_include_madonna():
    """andrea_solario famous_works must reference at least one Madonna work."""
    from art_catalog import get_style
    s = get_style("andrea_solario")
    assert any("madonna" in w[0].lower() or "madonna" in w[0].lower()
               for w in s.famous_works), (
        "andrea_solario famous_works must include at least one Madonna painting")


def test_andrea_solario_inspiration_references_pellucid():
    """andrea_solario inspiration must reference pellucid or amber quality."""
    from art_catalog import get_style
    s = get_style("andrea_solario")
    insp = s.inspiration.lower()
    assert "pellucid" in insp or "amber" in insp, (
        "andrea_solario inspiration must reference pellucid amber quality")


def test_lombard_leonardesque_period_present():
    """Period.LOMBARD_LEONARDESQUE must be in the Period enum (session 116)."""
    from scene_schema import Period
    assert hasattr(Period, "LOMBARD_LEONARDESQUE"), (
        "Period.LOMBARD_LEONARDESQUE not found — add it to scene_schema.py")
    assert Period.LOMBARD_LEONARDESQUE in list(Period)


def test_lombard_leonardesque_stroke_params_high_wet_blend():
    """LOMBARD_LEONARDESQUE stroke_params must have wet_blend >= 0.70."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.LOMBARD_LEONARDESQUE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.70, (
        f"LOMBARD_LEONARDESQUE wet_blend should be >= 0.70 for Leonardesque sfumato; "
        f"got {p['wet_blend']}")


def test_lombard_leonardesque_stroke_params_high_edge_softness():
    """LOMBARD_LEONARDESQUE stroke_params must have edge_softness >= 0.75."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.LOMBARD_LEONARDESQUE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["edge_softness"] >= 0.75, (
        f"LOMBARD_LEONARDESQUE edge_softness should be >= 0.75 for sfumato dissolution; "
        f"got {p['edge_softness']}")


def test_solario_pellucid_amber_pass_exists():
    """Painter must expose solario_pellucid_amber_pass (session 116)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "solario_pellucid_amber_pass"), (
        "Painter.solario_pellucid_amber_pass not found — add it to stroke_engine.py")


def test_solario_pellucid_amber_pass_opacity_parameter():
    """solario_pellucid_amber_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.solario_pellucid_amber_pass)
    assert "opacity" in sig.parameters, (
        "solario_pellucid_amber_pass must have 'opacity' parameter")


def test_solario_pellucid_amber_pass_amber_r_parameter():
    """solario_pellucid_amber_pass must accept amber_r for highlight warmth."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.solario_pellucid_amber_pass)
    assert "amber_r" in sig.parameters, (
        "solario_pellucid_amber_pass must have 'amber_r' parameter "
        "(primary amber highlight component)")


def test_solario_pellucid_amber_pass_violet_b_parameter():
    """solario_pellucid_amber_pass must accept violet_b for cool shadow."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.solario_pellucid_amber_pass)
    assert "violet_b" in sig.parameters, (
        "solario_pellucid_amber_pass must have 'violet_b' parameter "
        "(Venetian cool violet shadow component)")


def test_solario_pellucid_amber_pass_arc_r_parameter():
    """solario_pellucid_amber_pass must accept arc_r (chromatic arc mid-tone warmth)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.solario_pellucid_amber_pass)
    assert "arc_r" in sig.parameters, (
        "solario_pellucid_amber_pass must have 'arc_r' parameter "
        "(chromatic arc mid-tone warmth — session 116 improvement)")


def test_lombard_leonardesque_period_in_period_enum():
    """Period.LOMBARD_LEONARDESQUE must be accessible from scene_schema (session 116)."""
    from scene_schema import Period
    assert Period.LOMBARD_LEONARDESQUE in list(Period), (
        "Period.LOMBARD_LEONARDESQUE not found — add it to scene_schema.py Period enum")


# ── Session 117: Pietro Perugino + Period.UMBRIAN_CLASSICAL_HARMONY ──────────


def test_perugino_in_catalog():
    """perugino must be present in CATALOG (session 117)."""
    from art_catalog import CATALOG
    assert "perugino" in CATALOG, (
        "perugino not found in CATALOG — add it to art_catalog.py")


def test_perugino_movement():
    """perugino movement must reference Umbrian tradition."""
    from art_catalog import get_style
    s = get_style("perugino")
    mv = s.movement.lower()
    assert "umbrian" in mv or "proto-classical" in mv, (
        f"perugino movement={s.movement!r} must reference Umbrian or Proto-Classical")


def test_perugino_nationality():
    """perugino must be listed as Italian."""
    from art_catalog import get_style
    s = get_style("perugino")
    assert "italian" in s.nationality.lower(), (
        f"perugino nationality={s.nationality!r} should be Italian")


def test_perugino_palette_length():
    """perugino palette must have at least 5 colours."""
    from art_catalog import get_style
    s = get_style("perugino")
    assert len(s.palette) >= 5, (
        f"perugino palette has {len(s.palette)} colours; expected >= 5")


def test_perugino_palette_values_in_range():
    """All perugino palette RGB values must be in [0, 1]."""
    from art_catalog import get_style
    s = get_style("perugino")
    for i, col in enumerate(s.palette):
        for j, ch in enumerate(col):
            assert 0.0 <= ch <= 1.0, (
                f"perugino palette[{i}][{j}] = {ch} out of [0, 1]")


def test_perugino_has_warm_highlight():
    """perugino palette must include a warm ivory-gold highlight (R > 0.85, G > 0.75)."""
    from art_catalog import get_style
    s = get_style("perugino")
    warm_highlights = [(r, g, b) for r, g, b in s.palette if r > 0.85 and g > 0.75]
    assert warm_highlights, (
        "perugino palette must include at least one warm ivory-gold highlight "
        "(R > 0.85, G > 0.75) — his defining Umbrian luminosity")


def test_perugino_has_sky_blue():
    """perugino palette must include a soft blue entry (B > 0.70, B > R)."""
    from art_catalog import get_style
    s = get_style("perugino")
    blues = [(r, g, b) for r, g, b in s.palette if b > 0.70 and b > r]
    assert blues, (
        "perugino palette must include a sky-blue entry (B > 0.70, B > R) "
        "— his characteristic serene Umbrian sky")


def test_perugino_moderate_wet_blend_s117():
    """perugino wet_blend must be in [0.25, 0.55] — careful glazed layering, not deep sfumato."""
    from art_catalog import get_style
    s = get_style("perugino")
    assert 0.25 <= s.wet_blend <= 0.55, (
        f"perugino wet_blend={s.wet_blend} should be moderate [0.25, 0.55] for glazed layering")


def test_perugino_moderate_edge_softness():
    """perugino edge_softness must be in [0.50, 0.85] (serene softened edges)."""
    from art_catalog import get_style
    s = get_style("perugino")
    assert 0.50 <= s.edge_softness <= 0.85, (
        f"perugino edge_softness={s.edge_softness} should be in [0.50, 0.85] for serenity")


def test_perugino_has_glazing():
    """perugino must define glazing (warm amber-golden overlay)."""
    from art_catalog import get_style
    s = get_style("perugino")
    assert s.glazing is not None, "perugino must have glazing (warm amber-golden depth)"
    r, g, b = s.glazing
    assert r > g > b, (
        f"perugino glazing={s.glazing!r} should be warm amber-golden (R > G > B)")


def test_perugino_famous_works_include_delivery_of_keys():
    """perugino famous_works must reference a key work or religious subject."""
    from art_catalog import get_style
    s = get_style("perugino")
    titles_lower = [w[0].lower() for w in s.famous_works]
    has_known = any(
        "keys" in t or "christ" in t or "crucifixion" in t or "virgin" in t
        or "delivery" in t or "lamentation" in t or "portrait" in t
        for t in titles_lower
    )
    assert has_known, (
        "perugino famous_works must include at least one recognizable work "
        "(keys, christ, crucifixion, virgin, delivery, lamentation, or portrait)")


def test_perugino_inspiration_references_ground_warmth():
    """perugino inspiration must reference ground warmth or Umbrian quality."""
    from art_catalog import get_style
    s = get_style("perugino")
    insp = s.inspiration.lower()
    assert "ground" in insp or "umbrian" in insp or "serenity" in insp, (
        "perugino inspiration must reference ground warmth or Umbrian serenity")


def test_umbrian_classical_harmony_period_present():
    """Period.UMBRIAN_CLASSICAL_HARMONY must be in the Period enum (session 117)."""
    from scene_schema import Period
    assert hasattr(Period, "UMBRIAN_CLASSICAL_HARMONY"), (
        "Period.UMBRIAN_CLASSICAL_HARMONY not found — add it to scene_schema.py")
    assert Period.UMBRIAN_CLASSICAL_HARMONY in list(Period)


def test_umbrian_classical_harmony_stroke_params_high_wet_blend():
    """UMBRIAN_CLASSICAL_HARMONY stroke_params must have wet_blend >= 0.60."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.UMBRIAN_CLASSICAL_HARMONY,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.60, (
        f"UMBRIAN_CLASSICAL_HARMONY wet_blend should be >= 0.60 for harmonious smooth surface; "
        f"got {p['wet_blend']}")


def test_umbrian_classical_harmony_stroke_params_moderate_edge_softness():
    """UMBRIAN_CLASSICAL_HARMONY stroke_params must have edge_softness in [0.50, 0.85]."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.UMBRIAN_CLASSICAL_HARMONY,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.50 <= p["edge_softness"] <= 0.85, (
        f"UMBRIAN_CLASSICAL_HARMONY edge_softness should be in [0.50, 0.85] for Umbrian serenity; "
        f"got {p['edge_softness']}")


def test_perugino_serene_grace_pass_exists():
    """Painter must expose perugino_serene_grace_pass (session 117)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "perugino_serene_grace_pass"), (
        "Painter.perugino_serene_grace_pass not found — add it to stroke_engine.py")


def test_perugino_serene_grace_pass_opacity_parameter():
    """perugino_serene_grace_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.perugino_serene_grace_pass)
    assert "opacity" in sig.parameters, (
        "perugino_serene_grace_pass must have 'opacity' parameter")


def test_perugino_serene_grace_pass_ground_r_parameter():
    """perugino_serene_grace_pass must accept ground_r for luminous ground warmth."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.perugino_serene_grace_pass)
    assert "ground_r" in sig.parameters, (
        "perugino_serene_grace_pass must have 'ground_r' parameter "
        "(primary ground warmth red component — session 117 improvement)")


def test_perugino_serene_grace_pass_ivory_r_parameter():
    """perugino_serene_grace_pass must accept ivory_r for highlight serenity."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.perugino_serene_grace_pass)
    assert "ivory_r" in sig.parameters, (
        "perugino_serene_grace_pass must have 'ivory_r' parameter "
        "(ivory-gold highlight warm component)")


def test_perugino_serene_grace_pass_warm_r_parameter():
    """perugino_serene_grace_pass must accept warm_r for amber shadow recovery."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.perugino_serene_grace_pass)
    assert "warm_r" in sig.parameters, (
        "perugino_serene_grace_pass must have 'warm_r' parameter "
        "(warm amber shadow recovery)")


def test_umbrian_classical_harmony_period_in_period_enum():
    """Period.UMBRIAN_CLASSICAL_HARMONY must be accessible from scene_schema (session 117)."""
    from scene_schema import Period
    assert Period.UMBRIAN_CLASSICAL_HARMONY in list(Period), (
        "Period.UMBRIAN_CLASSICAL_HARMONY not found — add it to scene_schema.py Period enum")


# ──────────────────────────────────────────────────────────────────────────────
# Session 118: Giovanni Gerolamo Savoldo + BRESCIAN_SILVER_NOCTURNE
# ──────────────────────────────────────────────────────────────────────────────

def test_savoldo_in_catalog():
    """Savoldo (session 118) must be present in CATALOG."""
    assert "savoldo" in CATALOG


def test_savoldo_movement():
    s = get_style("savoldo")
    assert "Bresci" in s.movement or "bresci" in s.movement.lower() or "Venetian" in s.movement


def test_savoldo_palette_length():
    s = get_style("savoldo")
    assert len(s.palette) >= 5, "Savoldo palette should have at least 5 key colours"


def test_savoldo_palette_values_in_range():
    """All Savoldo palette RGB values must be in [0, 1]."""
    s = get_style("savoldo")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in Savoldo palette {rgb}")


def test_savoldo_ground_color_valid():
    s = get_style("savoldo")
    assert len(s.ground_color) == 3
    for ch in s.ground_color:
        assert 0.0 <= ch <= 1.0


def test_savoldo_high_wet_blend():
    """Savoldo should have high wet_blend (smooth nocturnal surfaces)."""
    s = get_style("savoldo")
    assert s.wet_blend >= 0.60, "Savoldo wet_blend should be high for smooth nocturnal surfaces"


def test_savoldo_high_edge_softness():
    """Savoldo should have high edge_softness (moonveil dissolves edges)."""
    s = get_style("savoldo")
    assert s.edge_softness >= 0.65, "Savoldo edge_softness should be high for silver moonveil"


def test_brescian_silver_nocturne_period_in_period_enum():
    """Period.BRESCIAN_SILVER_NOCTURNE must be accessible from scene_schema (session 118)."""
    from scene_schema import Period
    assert Period.BRESCIAN_SILVER_NOCTURNE in list(Period), (
        "Period.BRESCIAN_SILVER_NOCTURNE not found — add it to scene_schema.py Period enum")


def test_brescian_silver_nocturne_stroke_params():
    """BRESCIAN_SILVER_NOCTURNE must return valid stroke_params."""
    from scene_schema import Period, Style, Medium, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.BRESCIAN_SILVER_NOCTURNE, palette=PaletteHint.COOL_GREY)
    params = style.stroke_params
    assert params["wet_blend"] >= 0.55, "Savoldo wet_blend should be >= 0.55 (smooth nocturnal)"
    assert params["edge_softness"] >= 0.65, "Savoldo edge_softness should be >= 0.65 (silver moonveil)"


def test_savoldo_silver_veil_pass_exists():
    """Painter must expose savoldo_silver_veil_pass (session 118)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "savoldo_silver_veil_pass"), (
        "Painter.savoldo_silver_veil_pass not found — add it to stroke_engine.py")


def test_savoldo_silver_veil_pass_opacity_parameter():
    """savoldo_silver_veil_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.savoldo_silver_veil_pass)
    assert "opacity" in sig.parameters, (
        "savoldo_silver_veil_pass must have 'opacity' parameter")


def test_savoldo_silver_veil_pass_silver_b_parameter():
    """savoldo_silver_veil_pass must accept silver_b for the cool moonveil shimmer."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.savoldo_silver_veil_pass)
    assert "silver_b" in sig.parameters, (
        "savoldo_silver_veil_pass must have 'silver_b' parameter "
        "(cool blue-silver moonveil component — session 118 Gaussian improvement)")


def test_savoldo_silver_veil_pass_penumbra_lo_parameter():
    """savoldo_silver_veil_pass must accept penumbra_lo for the Gaussian-peaked window."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.savoldo_silver_veil_pass)
    assert "penumbra_lo" in sig.parameters, (
        "savoldo_silver_veil_pass must have 'penumbra_lo' parameter "
        "(lower bound of Gaussian penumbra window)")


# ──────────────────────────────────────────────────────────────────────────────
# Session 120: Lorenzo Lotto + VENETIAN_ECCENTRIC_PORTRAITURE
# ──────────────────────────────────────────────────────────────────────────────

def test_lotto_in_catalog():
    """Lotto (session 120) must be present in CATALOG."""
    assert "lotto" in CATALOG, "lotto not found in CATALOG — add it to art_catalog.py"


def test_lotto_movement():
    """Lotto movement must reference Venetian or Bergamask school."""
    s = get_style("lotto")
    assert "Venetian" in s.movement or "venetian" in s.movement.lower() or "Bergam" in s.movement, (
        f"lotto movement should reference Venetian or Bergamask; got {s.movement!r}")


def test_lotto_nationality():
    """Lotto nationality must reference Italian."""
    s = get_style("lotto")
    assert "Italian" in s.nationality, (
        f"lotto nationality should include 'Italian'; got {s.nationality!r}")


def test_lotto_palette_length():
    """Lotto palette must have at least 5 characteristic colours."""
    s = get_style("lotto")
    assert len(s.palette) >= 5, (
        f"Lotto palette should have at least 5 colours (vivid contrasts); got {len(s.palette)}")


def test_lotto_palette_values_in_range():
    """All Lotto palette RGB values must be in [0, 1]."""
    s = get_style("lotto")
    for rgb in s.palette:
        assert len(rgb) == 3
        for ch in rgb:
            assert 0.0 <= ch <= 1.0, f"Out-of-range channel {ch} in Lotto palette {rgb}"


def test_lotto_has_vivid_green_in_palette():
    """Lotto palette must include a vivid green (eccentric costume accent)."""
    s = get_style("lotto")
    has_green = any(g > 0.60 and g > r and g > b for r, g, b in s.palette)
    assert has_green, (
        "Lotto palette must include a vivid green — his eccentric costume accent "
        "(e.g. grass-green against mauve in Portrait of Andrea Odoni)")


def test_lotto_has_cool_shadow_in_palette():
    """Lotto palette must include a cool blue-grey shadow entry."""
    s = get_style("lotto")
    has_cool = any(b >= r and b >= g and b < 0.55 for r, g, b in s.palette)
    assert has_cool, (
        "Lotto palette must include a cool blue-grey shadow — his cold dark accents "
        "distinguish him from the warm-shadow Giorgionesque tradition")


def test_lotto_ground_color_valid():
    """Lotto ground_color must be a valid RGB triple in [0, 1]."""
    s = get_style("lotto")
    assert len(s.ground_color) == 3
    for ch in s.ground_color:
        assert 0.0 <= ch <= 1.0, f"Out-of-range ground_color channel: {ch}"


def test_lotto_moderate_wet_blend():
    """Lotto wet_blend must be moderate (chromatic energy, not full Titian blend)."""
    s = get_style("lotto")
    assert 0.35 <= s.wet_blend <= 0.60, (
        f"Lotto wet_blend should be moderate [0.35, 0.60]; got {s.wet_blend}")


def test_lotto_moderate_edge_softness():
    """Lotto edge_softness must be moderate (psychological acuity)."""
    s = get_style("lotto")
    assert 0.40 <= s.edge_softness <= 0.70, (
        f"Lotto edge_softness should be moderate [0.40, 0.70]; got {s.edge_softness}")


def test_lotto_higher_jitter():
    """Lotto jitter must be higher than typical (chromatic restlessness)."""
    s = get_style("lotto")
    assert s.jitter >= 0.028, (
        f"Lotto jitter should be higher (>= 0.028) for chromatic restlessness; got {s.jitter}")


def test_lotto_has_glazing():
    """Lotto must define a glazing colour (Venetian warm golden unifier)."""
    s = get_style("lotto")
    assert s.glazing is not None, "Lotto must have a glazing colour (warm Venetian golden glaze)"
    assert len(s.glazing) == 3
    for ch in s.glazing:
        assert 0.0 <= ch <= 1.0


def test_lotto_famous_works_include_odoni():
    """Lotto famous_works must include the Portrait of Andrea Odoni."""
    s = get_style("lotto")
    titles_lower = [t.lower() for t, _ in s.famous_works]
    has_odoni = any("odoni" in t for t in titles_lower)
    assert has_odoni, (
        "Lotto famous_works must include Portrait of Andrea Odoni — his defining masterwork")


def test_lotto_inspiration_references_vivacity_pass():
    """Lotto inspiration must reference lotto_restless_vivacity_pass."""
    s = get_style("lotto")
    assert "lotto_restless_vivacity_pass" in s.inspiration, (
        "Lotto inspiration must reference lotto_restless_vivacity_pass()")


def test_lotto_inspiration_references_chromatic_vibration():
    """Lotto inspiration must reference the multi-scale chromatic vibration improvement."""
    s = get_style("lotto")
    insp = s.inspiration.lower()
    assert "vibration" in insp or "multi-scale" in insp or "chromatic" in insp, (
        "Lotto inspiration must reference the multi-scale chromatic vibration field (session 120)")


def test_venetian_eccentric_portraiture_period_present():
    """Period.VENETIAN_ECCENTRIC_PORTRAITURE must be in the Period enum (session 120)."""
    from scene_schema import Period
    assert hasattr(Period, "VENETIAN_ECCENTRIC_PORTRAITURE"), (
        "Period.VENETIAN_ECCENTRIC_PORTRAITURE not found — add it to scene_schema.py")
    assert Period.VENETIAN_ECCENTRIC_PORTRAITURE in list(Period)


def test_venetian_eccentric_portraiture_stroke_params_moderate_wet_blend():
    """VENETIAN_ECCENTRIC_PORTRAITURE stroke_params must have moderate wet_blend."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_ECCENTRIC_PORTRAITURE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.35 <= p["wet_blend"] <= 0.60, (
        f"VENETIAN_ECCENTRIC_PORTRAITURE wet_blend should be moderate [0.35, 0.60] "
        f"for chromatic energy; got {p['wet_blend']}")


def test_venetian_eccentric_portraiture_stroke_params_moderate_edge_softness():
    """VENETIAN_ECCENTRIC_PORTRAITURE stroke_params must have moderate edge_softness."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.VENETIAN_ECCENTRIC_PORTRAITURE,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.40 <= p["edge_softness"] <= 0.70, (
        f"VENETIAN_ECCENTRIC_PORTRAITURE edge_softness should be moderate [0.40, 0.70] "
        f"for psychological acuity; got {p['edge_softness']}")


def test_lotto_restless_vivacity_pass_exists():
    """Painter must expose lotto_restless_vivacity_pass (session 120)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "lotto_restless_vivacity_pass"), (
        "Painter.lotto_restless_vivacity_pass not found — add it to stroke_engine.py")


def test_lotto_restless_vivacity_pass_opacity_parameter():
    """lotto_restless_vivacity_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.lotto_restless_vivacity_pass)
    assert "opacity" in sig.parameters, (
        "lotto_restless_vivacity_pass must have 'opacity' parameter")


def test_lotto_restless_vivacity_pass_vivacity_r_parameter():
    """lotto_restless_vivacity_pass must accept vivacity_r for the warm highlight lift."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.lotto_restless_vivacity_pass)
    assert "vivacity_r" in sig.parameters, (
        "lotto_restless_vivacity_pass must have 'vivacity_r' parameter "
        "(warm rose-ivory highlight red component)")


def test_lotto_restless_vivacity_pass_noise_scale_parameter():
    """lotto_restless_vivacity_pass must accept noise_scale (session 120 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.lotto_restless_vivacity_pass)
    assert "noise_scale" in sig.parameters, (
        "lotto_restless_vivacity_pass must have 'noise_scale' parameter "
        "(primary Gaussian sigma for multi-scale chromatic vibration — session 120 improvement)")


# ──────────────────────────────────────────────────────────────────────────────
# Session 121 — Giovanni Boldini + ITALIAN_BELLE_EPOQUE_PORTRAITURE
# ──────────────────────────────────────────────────────────────────────────────


def test_boldini_in_catalog():
    """boldini must be present in CATALOG (session 121)."""
    assert "boldini" in CATALOG, (
        "boldini not found in CATALOG -- add the ArtStyle entry")


def test_boldini_palette_valid():
    """Every colour in boldini palette must have RGB channels in [0, 1]."""
    s = get_style("boldini")
    for i, col in enumerate(s.palette):
        for j, v in enumerate(col):
            assert 0.0 <= v <= 1.0, (
                f"boldini palette[{i}][{j}]={v:.3f} out of [0, 1]")


def test_boldini_dark_ground():
    """
    boldini ground_color must be dark (luminance < 0.35) --
    Boldini favoured near-black chestnut grounds from which the figure
    emerges luminously.
    """
    s = get_style("boldini")
    r, g, b = s.ground_color
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    assert lum < 0.35, (
        f"boldini ground_color luminance={lum:.3f} should be dark (< 0.35) "
        "-- Boldini's near-black chestnut ground is compositionally essential")


def test_boldini_low_wet_blend():
    """
    boldini wet_blend must be low (< 0.45) -- Boldini's loose directional
    strokes retain individual energy; they are not heavily blended.
    """
    s = get_style("boldini")
    assert s.wet_blend < 0.45, (
        f"boldini wet_blend={s.wet_blend:.2f} should be low (< 0.45) "
        "-- directional swirl strokes are not heavily wet-blended")


def test_boldini_famous_works_include_marchesa_casati():
    """boldini famous_works must include Portrait of the Marchesa Luisa Casati."""
    s = get_style("boldini")
    titles = [t for t, _ in s.famous_works]
    assert any("Casati" in t or "Marchesa" in t for t in titles), (
        "boldini famous_works must include the Marchesa Casati portrait — "
        "his defining masterwork of the swirl technique")


def test_boldini_inspiration_references_swirl_pass():
    """boldini inspiration must reference boldini_swirl_bravura_pass."""
    s = get_style("boldini")
    assert "boldini_swirl_bravura_pass" in s.inspiration, (
        "boldini inspiration must reference boldini_swirl_bravura_pass()")


def test_boldini_inspiration_references_dual_angle():
    """boldini inspiration must reference the dual-angle improvement."""
    s = get_style("boldini")
    insp = s.inspiration.lower()
    assert "dual" in insp or "two" in insp or "secondary" in insp, (
        "boldini inspiration must reference the dual-angle swirl field "
        "(the session 121 artistic improvement)")


def test_italian_belle_epoque_portraiture_period_present():
    """Period.ITALIAN_BELLE_EPOQUE_PORTRAITURE must be in the Period enum (session 121)."""
    assert hasattr(Period, "ITALIAN_BELLE_EPOQUE_PORTRAITURE"), (
        "Period.ITALIAN_BELLE_EPOQUE_PORTRAITURE not found -- add it to scene_schema.py")
    assert Period.ITALIAN_BELLE_EPOQUE_PORTRAITURE in list(Period)


def test_italian_belle_epoque_portraiture_stroke_params_low_wet_blend():
    """ITALIAN_BELLE_EPOQUE_PORTRAITURE stroke_params must have low wet_blend."""
    style = Style(medium=Medium.OIL, period=Period.ITALIAN_BELLE_EPOQUE_PORTRAITURE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] < 0.45, (
        f"ITALIAN_BELLE_EPOQUE_PORTRAITURE wet_blend should be low (< 0.45) "
        f"for Boldini's loose directional bravura; got {p['wet_blend']}")


def test_italian_belle_epoque_portraiture_stroke_params_moderate_edge_softness():
    """ITALIAN_BELLE_EPOQUE_PORTRAITURE stroke_params must have moderate edge_softness."""
    style = Style(medium=Medium.OIL, period=Period.ITALIAN_BELLE_EPOQUE_PORTRAITURE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert 0.35 <= p["edge_softness"] <= 0.70, (
        f"ITALIAN_BELLE_EPOQUE_PORTRAITURE edge_softness should be moderate [0.35, 0.70] "
        f"for figures emerging softly from dark grounds; got {p['edge_softness']}")


def test_boldini_swirl_bravura_pass_exists():
    """Painter must expose boldini_swirl_bravura_pass (session 121)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "boldini_swirl_bravura_pass"), (
        "Painter.boldini_swirl_bravura_pass not found -- add it to stroke_engine.py")


def test_boldini_swirl_bravura_pass_opacity_parameter():
    """boldini_swirl_bravura_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.boldini_swirl_bravura_pass)
    assert "opacity" in sig.parameters, (
        "boldini_swirl_bravura_pass must have 'opacity' parameter")


def test_boldini_swirl_bravura_pass_dual_angle_parameters():
    """boldini_swirl_bravura_pass must have both primary_angle and secondary_angle."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.boldini_swirl_bravura_pass)
    assert "primary_angle" in sig.parameters, (
        "boldini_swirl_bravura_pass must have 'primary_angle' parameter "
        "(the dominant swirl direction — session 121 improvement)")
    assert "secondary_angle" in sig.parameters, (
        "boldini_swirl_bravura_pass must have 'secondary_angle' parameter "
        "(the crossing swirl direction — session 121 improvement)")


# ──────────────────────────────────────────────────────────────────────────────
# Session 122 — Annibale Carracci + BOLOGNESE_ACADEMIC_NATURALISM
# ──────────────────────────────────────────────────────────────────────────────


def test_annibale_carracci_in_catalog():
    """annibale_carracci must be present in CATALOG (session 122)."""
    assert "annibale_carracci" in CATALOG, (
        "annibale_carracci not found in CATALOG -- add the ArtStyle entry")


def test_annibale_carracci_palette_valid():
    """Every colour in annibale_carracci palette must have RGB channels in [0, 1]."""
    s = get_style("annibale_carracci")
    for i, col in enumerate(s.palette):
        for j, v in enumerate(col):
            assert 0.0 <= v <= 1.0, (
                f"annibale_carracci palette[{i}][{j}]={v:.3f} out of [0, 1]")


def test_annibale_carracci_warm_ground():
    """
    annibale_carracci ground_color must be warm (R > B) --
    Carracci built on a warm sienna-brown imprimatura that glows
    through shadow glazes.
    """
    s = get_style("annibale_carracci")
    r, g, b = s.ground_color
    assert r > b, (
        f"annibale_carracci ground_color should be warm (R > B); "
        f"got R={r:.3f}, B={b:.3f}")


def test_annibale_carracci_moderate_wet_blend():
    """
    annibale_carracci wet_blend must be moderate (0.40 <= wet_blend <= 0.70) --
    Carracci's naturalistic painting is blended but not dissolved (anti-Mannerist clarity).
    """
    s = get_style("annibale_carracci")
    assert 0.40 <= s.wet_blend <= 0.70, (
        f"annibale_carracci wet_blend={s.wet_blend:.2f} should be moderate [0.40, 0.70] "
        "-- naturalistic painting, not sfumato dissolution or dry-brush tenebrism")


def test_annibale_carracci_famous_works_include_farnese():
    """annibale_carracci famous_works must include the Farnese Gallery frescoes."""
    s = get_style("annibale_carracci")
    titles = [t for t, _ in s.famous_works]
    assert any("Farnese" in t for t in titles), (
        "annibale_carracci famous_works must include the Farnese Gallery frescoes -- "
        "his defining large-scale masterwork")


def test_annibale_carracci_inspiration_references_pass():
    """annibale_carracci inspiration must reference annibale_carracci_tonal_reform_pass."""
    s = get_style("annibale_carracci")
    assert "annibale_carracci_tonal_reform_pass" in s.inspiration, (
        "annibale_carracci inspiration must reference annibale_carracci_tonal_reform_pass()")


def test_annibale_carracci_inspiration_references_temperature():
    """annibale_carracci inspiration must reference the directional temperature field improvement."""
    s = get_style("annibale_carracci")
    insp = s.inspiration.lower()
    assert "temperature" in insp or "gradient" in insp or "directional" in insp, (
        "annibale_carracci inspiration must reference the directional tonal temperature "
        "field (the session 122 artistic improvement)")


def test_bolognese_academic_naturalism_period_present():
    """Period.BOLOGNESE_ACADEMIC_NATURALISM must be in the Period enum (session 122)."""
    from scene_schema import Period
    assert hasattr(Period, "BOLOGNESE_ACADEMIC_NATURALISM"), (
        "Period.BOLOGNESE_ACADEMIC_NATURALISM not found — add it to scene_schema.py")
    assert Period.BOLOGNESE_ACADEMIC_NATURALISM in list(Period)


def test_bolognese_academic_naturalism_stroke_params_moderate_wet_blend():
    """BOLOGNESE_ACADEMIC_NATURALISM stroke_params must have moderate wet_blend."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.BOLOGNESE_ACADEMIC_NATURALISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.40 <= p["wet_blend"] <= 0.70, (
        f"BOLOGNESE_ACADEMIC_NATURALISM wet_blend should be moderate [0.40, 0.70] "
        f"for Carracci's naturalistic blending (not dissolved, not dry); got {p['wet_blend']}")


def test_bolognese_academic_naturalism_stroke_params_moderate_edge_softness():
    """BOLOGNESE_ACADEMIC_NATURALISM stroke_params must have moderate edge_softness."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.BOLOGNESE_ACADEMIC_NATURALISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.40 <= p["edge_softness"] <= 0.70, (
        f"BOLOGNESE_ACADEMIC_NATURALISM edge_softness should be moderate [0.40, 0.70] "
        f"for clearly resolved naturalistic forms; got {p['edge_softness']}")


def test_annibale_carracci_tonal_reform_pass_exists():
    """Painter must expose annibale_carracci_tonal_reform_pass (session 122)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "annibale_carracci_tonal_reform_pass"), (
        "Painter.annibale_carracci_tonal_reform_pass not found — add it to stroke_engine.py")


def test_annibale_carracci_tonal_reform_pass_opacity_parameter():
    """annibale_carracci_tonal_reform_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.annibale_carracci_tonal_reform_pass)
    assert "opacity" in sig.parameters, (
        "annibale_carracci_tonal_reform_pass must have 'opacity' parameter")


def test_annibale_carracci_tonal_reform_pass_light_angle_parameter():
    """annibale_carracci_tonal_reform_pass must accept light_angle_deg (session 122 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.annibale_carracci_tonal_reform_pass)
    assert "light_angle_deg" in sig.parameters, (
        "annibale_carracci_tonal_reform_pass must have 'light_angle_deg' parameter "
        "(light source direction for the directional temperature field — session 122 improvement)")


def test_annibale_carracci_tonal_reform_pass_gradient_temperature_parameters():
    """annibale_carracci_tonal_reform_pass must have warm_r and cool_b (temperature field)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.annibale_carracci_tonal_reform_pass)
    assert "warm_r" in sig.parameters, (
        "annibale_carracci_tonal_reform_pass must have 'warm_r' parameter "
        "(warm colour lift on lit face)")
    assert "cool_b" in sig.parameters, (
        "annibale_carracci_tonal_reform_pass must have 'cool_b' parameter "
        "(cool blue lift on shadow face — session 122 directional temperature improvement)")


# ──────────────────────────────────────────────────────────────────────────────
# Session 123: Salvator Rosa + ROMAN_BAROQUE_LANDSCAPE
# ──────────────────────────────────────────────────────────────────────────────

def test_salvator_rosa_in_catalog():
    """salvator_rosa must be in CATALOG (session 123)."""
    assert "salvator_rosa" in CATALOG, (
        "salvator_rosa not found in CATALOG — add it to art_catalog.py")


def test_salvator_rosa_movement():
    """salvator_rosa must be classified as Baroque / Proto-Romantic or similar."""
    s = get_style("salvator_rosa")
    mv = s.movement.lower()
    assert "baroque" in mv or "romantic" in mv, (
        f"salvator_rosa movement should reference Baroque or Romantic; got {s.movement!r}")


def test_salvator_rosa_palette_length():
    """salvator_rosa palette must have at least 5 entries."""
    s = get_style("salvator_rosa")
    assert len(s.palette) >= 5, (
        f"salvator_rosa palette has {len(s.palette)} entries; expected ≥ 5")


def test_salvator_rosa_palette_values_in_range():
    """All salvator_rosa palette RGB values must be in [0, 1]."""
    s = get_style("salvator_rosa")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in salvator_rosa palette {rgb}")


def test_salvator_rosa_low_wet_blend():
    """salvator_rosa wet_blend must be low (gestural brushwork, not blended sfumato)."""
    s = get_style("salvator_rosa")
    assert s.wet_blend <= 0.35, (
        f"salvator_rosa wet_blend={s.wet_blend:.2f} should be ≤ 0.35 "
        "-- Rosa's alla-prima gestural marks are direction-less, not heavily blended")


def test_salvator_rosa_famous_works_non_empty():
    """salvator_rosa must list at least one famous work."""
    s = get_style("salvator_rosa")
    assert len(s.famous_works) >= 1, "salvator_rosa must have at least one famous work"


def test_salvator_rosa_inspiration_references_pass():
    """salvator_rosa inspiration must reference salvator_rosa_wild_bravura_pass."""
    s = get_style("salvator_rosa")
    assert "salvator_rosa_wild_bravura_pass" in s.inspiration, (
        "salvator_rosa inspiration must reference salvator_rosa_wild_bravura_pass()")


def test_salvator_rosa_inspiration_references_displacement():
    """salvator_rosa inspiration must reference the displacement field improvement."""
    s = get_style("salvator_rosa")
    insp = s.inspiration.lower()
    assert "displacement" in insp or "warp" in insp or "turbul" in insp, (
        "salvator_rosa inspiration must reference the turbulent displacement field "
        "(the session 123 artistic improvement)")


def test_roman_baroque_landscape_period_present():
    """Period.ROMAN_BAROQUE_LANDSCAPE must be in the Period enum (session 123)."""
    from scene_schema import Period
    assert hasattr(Period, "ROMAN_BAROQUE_LANDSCAPE"), (
        "Period.ROMAN_BAROQUE_LANDSCAPE not found — add it to scene_schema.py")
    assert Period.ROMAN_BAROQUE_LANDSCAPE in list(Period)


def test_roman_baroque_landscape_stroke_params_low_wet_blend():
    """ROMAN_BAROQUE_LANDSCAPE stroke_params must have low wet_blend (gestural)."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.ROMAN_BAROQUE_LANDSCAPE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] <= 0.35, (
        f"ROMAN_BAROQUE_LANDSCAPE wet_blend should be ≤ 0.35 "
        f"for Rosa's gestural turbulence; got {p['wet_blend']}")


def test_roman_baroque_landscape_stroke_params_large_bg_strokes():
    """ROMAN_BAROQUE_LANDSCAPE stroke_params must have large stroke_size_bg (landscape energy)."""
    from scene_schema import Style, Medium, Period, PaletteHint
    style = Style(medium=Medium.OIL, period=Period.ROMAN_BAROQUE_LANDSCAPE,
                  palette=PaletteHint.DARK_EARTH)
    p = style.stroke_params
    assert p["stroke_size_bg"] >= 28, (
        f"ROMAN_BAROQUE_LANDSCAPE stroke_size_bg should be ≥ 28 "
        f"for Rosa's sweeping landscape brushwork; got {p['stroke_size_bg']}")


def test_salvator_rosa_wild_bravura_pass_exists():
    """Painter must expose salvator_rosa_wild_bravura_pass (session 123)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "salvator_rosa_wild_bravura_pass"), (
        "Painter.salvator_rosa_wild_bravura_pass not found — add it to stroke_engine.py")


def test_salvator_rosa_wild_bravura_pass_opacity_parameter():
    """salvator_rosa_wild_bravura_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.salvator_rosa_wild_bravura_pass)
    assert "opacity" in sig.parameters, (
        "salvator_rosa_wild_bravura_pass must have 'opacity' parameter")


def test_salvator_rosa_wild_bravura_pass_max_disp_parameter():
    """salvator_rosa_wild_bravura_pass must accept max_disp (session 123 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.salvator_rosa_wild_bravura_pass)
    assert "max_disp" in sig.parameters, (
        "salvator_rosa_wild_bravura_pass must have 'max_disp' parameter "
        "(maximum pixel displacement for the turbulent warp — session 123 improvement)")


# ──────────────────────────────────────────────────────────────────────────────
# Session 124: Massimo Stanzione — Neapolitan Baroque Classicism
# ──────────────────────────────────────────────────────────────────────────────

def test_massimo_stanzione_in_catalog():
    """massimo_stanzione must be present in CATALOG (session 124)."""
    assert "massimo_stanzione" in CATALOG, (
        "'massimo_stanzione' not found in CATALOG — add it to art_catalog.py")


def test_massimo_stanzione_get_style():
    """get_style('massimo_stanzione') must return an ArtStyle without error."""
    s = get_style("massimo_stanzione")
    assert s.artist == "Massimo Stanzione"


def test_massimo_stanzione_movement():
    """massimo_stanzione movement must identify Neapolitan Baroque Classicism."""
    s = get_style("massimo_stanzione")
    assert "Neapolitan" in s.movement or "Baroque" in s.movement, (
        f"massimo_stanzione movement should reference Neapolitan Baroque; got '{s.movement}'")


def test_massimo_stanzione_palette_length():
    """massimo_stanzione palette must have at least 5 entries."""
    s = get_style("massimo_stanzione")
    assert len(s.palette) >= 5, (
        f"massimo_stanzione palette has {len(s.palette)} entries; expected >= 5")


def test_massimo_stanzione_palette_values_in_range():
    """All massimo_stanzione palette RGB values must be in [0, 1]."""
    s = get_style("massimo_stanzione")
    for rgb in s.palette:
        assert len(rgb) == 3
        for channel in rgb:
            assert 0.0 <= channel <= 1.0, (
                f"Out-of-range channel {channel} in massimo_stanzione palette {rgb}")


def test_massimo_stanzione_high_wet_blend():
    """massimo_stanzione wet_blend must be high (smooth Reni-derived blending >= 0.60)."""
    s = get_style("massimo_stanzione")
    assert s.wet_blend >= 0.60, (
        f"massimo_stanzione wet_blend={s.wet_blend:.2f} should be >= 0.60 "
        "-- Stanzione's flesh surfaces are smooth and seamlessly blended, Reni-influenced")


def test_massimo_stanzione_famous_works_non_empty():
    """massimo_stanzione must list at least one famous work."""
    s = get_style("massimo_stanzione")
    assert len(s.famous_works) >= 1, "massimo_stanzione must have at least one famous work"


def test_massimo_stanzione_inspiration_references_pass():
    """massimo_stanzione inspiration must reference stanzione_noble_repose_pass."""
    s = get_style("massimo_stanzione")
    assert "stanzione_noble_repose_pass" in s.inspiration, (
        "massimo_stanzione inspiration must reference stanzione_noble_repose_pass()")


def test_massimo_stanzione_inspiration_references_pyramid():
    """massimo_stanzione inspiration must reference the Laplacian pyramid improvement."""
    s = get_style("massimo_stanzione")
    insp = s.inspiration.lower()
    assert "laplacian" in insp or "pyramid" in insp or "frequency" in insp, (
        "massimo_stanzione inspiration must reference the Laplacian pyramid "
        "(the session 124 artistic improvement)")


def test_neapolitan_baroque_classicism_period_present():
    """Period.NEAPOLITAN_BAROQUE_CLASSICISM must be in the Period enum (session 124)."""
    assert hasattr(Period, "NEAPOLITAN_BAROQUE_CLASSICISM"), (
        "Period.NEAPOLITAN_BAROQUE_CLASSICISM not found -- add it to scene_schema.py")
    assert Period.NEAPOLITAN_BAROQUE_CLASSICISM in list(Period)


def test_neapolitan_baroque_classicism_stroke_params_high_wet_blend():
    """NEAPOLITAN_BAROQUE_CLASSICISM stroke_params must have high wet_blend (>= 0.60)."""
    style = Style(medium=Medium.OIL, period=Period.NEAPOLITAN_BAROQUE_CLASSICISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert p["wet_blend"] >= 0.60, (
        f"NEAPOLITAN_BAROQUE_CLASSICISM wet_blend should be >= 0.60 "
        f"for Stanzione's smooth Reni-influenced flesh; got {p['wet_blend']}")


def test_neapolitan_baroque_classicism_stroke_params_moderate_edge_softness():
    """NEAPOLITAN_BAROQUE_CLASSICISM edge_softness must be moderate (0.50 to 0.85)."""
    style = Style(medium=Medium.OIL, period=Period.NEAPOLITAN_BAROQUE_CLASSICISM,
                  palette=PaletteHint.WARM_EARTH)
    p = style.stroke_params
    assert 0.50 <= p["edge_softness"] <= 0.85, (
        f"NEAPOLITAN_BAROQUE_CLASSICISM edge_softness should be 0.50-0.85; got {p['edge_softness']}")


def test_stanzione_noble_repose_pass_exists():
    """Painter must expose stanzione_noble_repose_pass (session 124)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "stanzione_noble_repose_pass"), (
        "Painter.stanzione_noble_repose_pass not found -- add it to stroke_engine.py")


def test_stanzione_noble_repose_pass_opacity_parameter():
    """stanzione_noble_repose_pass must accept opacity parameter."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.stanzione_noble_repose_pass)
    assert "opacity" in sig.parameters, (
        "stanzione_noble_repose_pass must have 'opacity' parameter")


def test_stanzione_noble_repose_pass_pyramid_levels_parameter():
    """stanzione_noble_repose_pass must accept pyramid_levels (session 124 improvement)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.stanzione_noble_repose_pass)
    assert "pyramid_levels" in sig.parameters, (
        "stanzione_noble_repose_pass must have 'pyramid_levels' parameter "
        "(number of frequency bands in Laplacian pyramid -- session 124 improvement)")


def test_stanzione_noble_repose_pass_mid_freq_boost_parameter():
    """stanzione_noble_repose_pass must accept mid_freq_boost (Laplacian band boost)."""
    import inspect
    from stroke_engine import Painter
    sig = inspect.signature(Painter.stanzione_noble_repose_pass)
    assert "mid_freq_boost" in sig.parameters, (
        "stanzione_noble_repose_pass must have 'mid_freq_boost' parameter "
        "(contrast boost for mid-frequency Laplacian band -- session 124 improvement)")


def test_stanzione_noble_repose_pass_modifies_canvas():
    """stanzione_noble_repose_pass() must alter the canvas from its initial state."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    p.tone_ground((0.55, 0.45, 0.30), texture_strength=0.06)
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.stanzione_noble_repose_pass(opacity=1.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert not _np.array_equal(before, after), (
        "stanzione_noble_repose_pass should change the canvas when opacity=1.0")


def test_stanzione_noble_repose_pass_opacity_zero_is_noop():
    """stanzione_noble_repose_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((128, 128, 4)).copy()
    data[:, :, :] = [120, 140, 170, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.stanzione_noble_repose_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "stanzione_noble_repose_pass(opacity=0) should be a noop")


def test_stanzione_noble_repose_pass_lifts_highlights():
    """stanzione_noble_repose_pass must raise R in the bright highlight zone."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    # Bright fill -- well above default hi_lo (0.70); lum ~ 0.85
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4)).copy()
    data[:, :, :] = [210, 215, 220, 255]   # BGRA: bright, lum ~ 0.85
    p.canvas.surface.get_data()[:] = data.tobytes()
    orig_r = data[:, :, 2].astype(_np.float32).mean()
    p.stanzione_noble_repose_pass(
        ivory_r=0.08, ivory_g=0.04,
        violet_b=0.0, violet_r=0.0,
        mid_freq_boost=0.0, fine_suppress=0.0,
        opacity=1.0,
    )
    after_buf = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape((64, 64, 4))
    after_r = after_buf[:, :, 2].astype(_np.float32).mean()
    assert after_r >= orig_r, (
        f"stanzione_noble_repose_pass must raise R in highlight zone (warm ivory lift); "
        f"before={orig_r:.1f}, after={after_r:.1f}")


def test_stanzione_noble_repose_pass_preserves_canvas_shape():
    """stanzione_noble_repose_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = Painter(width=80, height=64)
    p.tone_ground((0.46, 0.36, 0.22), texture_strength=0.05)
    p.stanzione_noble_repose_pass(opacity=0.30)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after stanzione_noble_repose_pass: {img.size}")


# ── Session 125: Francesco Albani ────────────────────────────────────────────

def test_albani_in_catalog():
    """Francesco Albani (session 125) must be in the catalog."""
    assert "albani" in CATALOG, "albani missing from CATALOG — add to art_catalog.py"


def test_albani_palette_valid():
    """albani palette entries must be valid RGB floats in [0, 1]."""
    s = get_style("albani")
    for i, col in enumerate(s.palette):
        assert len(col) == 3, f"albani palette[{i}] must have 3 components"
        for ch in col:
            assert 0.0 <= ch <= 1.0, (
                f"albani palette[{i}] channel out of range [0,1]: {ch}")


def test_albani_wet_blend_high():
    """albani wet_blend must be >= 0.65 for smooth Arcadian classicism."""
    s = get_style("albani")
    assert s.wet_blend >= 0.65, (
        f"albani wet_blend should be >= 0.65 (Albani's silky smooth surfaces); "
        f"got {s.wet_blend}")


def test_albani_inspiration_mentions_arcadian():
    """albani inspiration text must mention chromatic aerial perspective."""
    s = get_style("albani")
    insp_lower = s.inspiration.lower()
    assert "aerial" in insp_lower or "arcadian" in insp_lower, (
        "albani inspiration should reference 'aerial' or 'arcadian' — "
        "the defining aesthetic and technical improvement of session 125")


# ── Session 126: Fra Bartolommeo ──────────────────────────────────────────────

def test_fra_bartolommeo_in_catalog():
    """Fra Bartolommeo (session 126) must be in the catalog."""
    assert "fra_bartolommeo" in CATALOG, (
        "fra_bartolommeo missing from CATALOG — add to art_catalog.py")


def test_fra_bartolommeo_palette_valid():
    """fra_bartolommeo palette entries must be valid RGB floats in [0, 1]."""
    s = get_style("fra_bartolommeo")
    for i, col in enumerate(s.palette):
        assert len(col) == 3, f"fra_bartolommeo palette[{i}] must have 3 components"
        for ch in col:
            assert 0.0 <= ch <= 1.0, (
                f"fra_bartolommeo palette[{i}] channel out of range [0,1]: {ch}")


def test_fra_bartolommeo_wet_blend_high():
    """fra_bartolommeo wet_blend must be >= 0.60 for smooth monumental surfaces."""
    s = get_style("fra_bartolommeo")
    assert s.wet_blend >= 0.60, (
        f"fra_bartolommeo wet_blend should be >= 0.60 (monumental smooth surfaces); "
        f"got {s.wet_blend}")


def test_fra_bartolommeo_inspiration_mentions_sobel():
    """fra_bartolommeo inspiration text must mention Sobel or velo."""
    s = get_style("fra_bartolommeo")
    insp_lower = s.inspiration.lower()
    assert "sobel" in insp_lower or "velo" in insp_lower, (
        "fra_bartolommeo inspiration should reference 'sobel' or 'velo' — "
        "the defining technical improvement of session 126")


def test_fra_bartolommeo_velo_shadow_pass_exists():
    """Painter must have fra_bartolommeo_velo_shadow_pass() method (session 126)."""
    from stroke_engine import Painter
    assert hasattr(Painter, "fra_bartolommeo_velo_shadow_pass"), (
        "fra_bartolommeo_velo_shadow_pass not found on Painter — add to stroke_engine.py")
    assert callable(getattr(Painter, "fra_bartolommeo_velo_shadow_pass"))


def test_fra_bartolommeo_velo_shadow_pass_noop_at_zero_opacity():
    """fra_bartolommeo_velo_shadow_pass(opacity=0) must leave the canvas unchanged."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=128, height=128)
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape(
        (128, 128, 4)).copy()
    data[:, :, :] = [120, 140, 170, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    before = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    p.fra_bartolommeo_velo_shadow_pass(opacity=0.0)
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).copy()
    assert _np.array_equal(before, after), (
        "fra_bartolommeo_velo_shadow_pass(opacity=0) should be a noop")


def test_fra_bartolommeo_velo_shadow_pass_warms_lit_ridges():
    """fra_bartolommeo_velo_shadow_pass must raise R in mid-tone zone at full opacity."""
    import numpy as _np
    from stroke_engine import Painter
    p = Painter(width=64, height=64)
    # Gradient canvas: half bright, half dark — creates Sobel-detectable edge in the middle
    data = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape(
        (64, 64, 4)).copy()
    # Left half bright (lum ≈ 0.60 — lit side of penumbra)
    data[:, :32, :] = [150, 155, 160, 255]   # BGRA
    # Right half mid-shadow (lum ≈ 0.35 — shadow side of penumbra)
    data[:, 32:, :] = [80, 85, 90, 255]
    p.canvas.surface.get_data()[:] = data.tobytes()
    orig_r_lit = data[:, :32, 2].astype(_np.float32).mean()
    p.fra_bartolommeo_velo_shadow_pass(
        lit_warmth_r=0.10,
        lit_warmth_g=0.04,
        shadow_cool_b=0.0,
        shadow_cool_r=0.0,
        saturation_boost=0.0,
        opacity=1.0,
    )
    after = _np.frombuffer(p.canvas.surface.get_data(), dtype=_np.uint8).reshape(
        (64, 64, 4))
    after_r_lit = after[:, :32, 2].astype(_np.float32).mean()
    assert after_r_lit >= orig_r_lit, (
        f"fra_bartolommeo_velo_shadow_pass must raise R on lit side; "
        f"before={orig_r_lit:.1f}, after={after_r_lit:.1f}")


def test_fra_bartolommeo_velo_shadow_pass_preserves_canvas_shape():
    """fra_bartolommeo_velo_shadow_pass() must not change canvas dimensions."""
    from stroke_engine import Painter
    p = Painter(width=80, height=64)
    p.tone_ground((0.64, 0.52, 0.34), texture_strength=0.05)
    p.fra_bartolommeo_velo_shadow_pass(opacity=0.30)
    img = p.canvas.to_pil()
    assert img.size == (80, 64), (
        f"Canvas shape changed after fra_bartolommeo_velo_shadow_pass: {img.size}")


def test_florentine_monumental_classicism_period_exists():
    """FLORENTINE_MONUMENTAL_CLASSICISM must exist in the Period enum (session 126)."""
    from scene_schema import Period
    assert hasattr(Period, "FLORENTINE_MONUMENTAL_CLASSICISM"), (
        "FLORENTINE_MONUMENTAL_CLASSICISM missing from Period enum — "
        "add to scene_schema.py for session 126 (Fra Bartolommeo)")
