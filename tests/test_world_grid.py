# -*- coding: utf-8 -*-
"""Testele hărții lumii.

Harta a avut bug-uri exact de tipul ăsta: zone care se atingeau direct (se sărea
peste conector), drumuri fără nume, conectori definiți în date dar fără nicio
celulă pe grilă. Testele de mai jos sunt aceleași verificări pe care jocul le
rulează la pornire, ca o regresie să pice în CI, nu în fața profesorului.
"""

from dragon_world import grid


# Topologia pe care o cere povestea (Capitolul I -> V).
TOPOLOGIE_ASTEPTATA = {
    "drum_targoviste_curtea": {"targoviste", "curtea_domneasca"},
    "drum_targoviste_han":    {"targoviste", "han"},
    "camp_han_padure":        {"han", "padure"},
    "drum_padure_tabara":     {"padure", "tabara_otomana"},
}

CONEXIUNI_LOCATIONS = {
    "drum_targoviste_curtea": ["targoviste", "curtea_domneasca"],
    "drum_targoviste_han":    ["targoviste", "han"],
    "camp_han_padure":        ["han", "padure"],
    "drum_padure_tabara":     ["padure", "tabara_otomana"],
}


def test_harta_nu_are_nicio_problema():
    assert grid.validate_world_grid(CONEXIUNI_LOCATIONS) == []


def test_grila_are_dimensiunile_declarate():
    assert len(grid.WORLD_GRID) == grid.GRID_ROWS
    for rand in grid.WORLD_GRID:
        assert len(rand) == grid.GRID_COLS


def test_doua_zone_nu_se_ating_niciodata_direct():
    # Dacă se ating, jucătorul intră în tabăra otomană fără să treacă pe potecă.
    assert grid._validate_zone_separation() == []


def test_fiecare_drum_are_conector_si_nu_e_fundatura():
    assert grid._validate_roads() == []


def test_toate_zonele_sunt_accesibile_pe_jos():
    assert grid._validate_reachability() == []


def test_pozitiile_de_fast_travel_cad_pe_zona_lor():
    assert grid._validate_start_positions() == []


def test_coridoarele_leaga_exact_perechile_din_poveste():
    assert grid.connector_endpoints() == TOPOLOGIE_ASTEPTATA


def test_startul_jucatorului_e_in_targoviste():
    # game_state.rpy pornește jucătorul la (2, 1).
    assert grid.get_zone_at(2, 1) == "targoviste"


def test_celulele_din_afara_hartii_sunt_ziduri():
    assert grid.is_wall(-1, 0)
    assert grid.is_wall(0, grid.GRID_COLS)


def test_conectorul_e_raportat_ca_zona_curenta():
    # Pe un drum, get_zone_at e None, dar jucătorul trebuie să vadă numele drumului.
    assert grid.get_zone_at(1, 4) is None
    assert grid.get_map_area_at(1, 4) == "drum_targoviste_curtea"


def test_validatorul_prinde_o_harta_stricata():
    # Regresia reală din versiunea veche: Târgoviște lipit de Curtea Domnească.
    original = grid.WORLD_GRID[:]
    try:
        grid.WORLD_GRID[2] = "#TTTTTCCCCCC"
        probleme = grid.validate_world_grid(CONEXIUNI_LOCATIONS)
        assert any("se ating direct" in p for p in probleme)
    finally:
        grid.WORLD_GRID[:] = original
