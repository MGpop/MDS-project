# -*- coding: utf-8 -*-
"""Grila lumii și validarea ei.

Modul de Python pur: nu importă Ren'Py, deci poate fi rulat direct de pytest.
Ren'Py îl vede pentru că `game/python-packages/` intră automat în sys.path.

Regula de aur a hărții: două zone diferite nu se ating niciodată direct. Trecerea
dintr-o zonă în alta se face doar printr-un coridor de conector, exact cum descrie
`connections` din LOCATIONS. `validate_world_grid()` verifică asta la fiecare
pornire a jocului și în teste, ca harta să nu se mai poată strica în tăcere.
"""

GRID_ROWS = 12
GRID_COLS = 12

# T=Târgoviște  C=Curtea Domnească  H=Han  P=Pădure  O=Tabăra otomană
# _=drum traversabil (conector)  #=zid (inaccesibil)
WORLD_GRID = [
    "######CCCCCC",   # rând 0
    "#TTT__CCCCCC",   # rând 1  <- coridorul spre Curtea Domnească
    "#TTT##CCCCCC",   # rând 2  <- start jucător (2,1)
    "#TTT########",   # rând 3
    "##_#########",   # rând 4  <- drumul spre Han
    "##_#########",   # rând 5
    "HHH##PPPP###",   # rând 6
    "HHH__PPPP###",   # rând 7  <- câmpul dintre Han și Pădure
    "HHH##PPPP###",   # rând 8
    "#####PPPP###",   # rând 9
    "#######__OOO",   # rând 10 <- poteca spre tabăra otomană
    "#########OOO",   # rând 11
]

ZONE_CHARS = {
    "T": "targoviste",
    "C": "curtea_domneasca",
    "H": "han",
    "P": "padure",
    "O": "tabara_otomana",
}

CHAR_BY_ZONE = dict((zone, ch) for ch, zone in ZONE_CHARS.items())

# Celulele de drum, grupate pe coridoare. Fiecare coridor leagă exact două zone.
CONNECTOR_CELLS = {
    # Târgoviște <-> Curtea Domnească
    (1, 4):  "drum_targoviste_curtea",
    (1, 5):  "drum_targoviste_curtea",

    # Târgoviște <-> Han
    (4, 2):  "drum_targoviste_han",
    (5, 2):  "drum_targoviste_han",

    # Han <-> Pădure
    (7, 3):  "camp_han_padure",
    (7, 4):  "camp_han_padure",

    # Pădure <-> Tabăra otomană
    (10, 7): "drum_padure_tabara",
    (10, 8): "drum_padure_tabara",
}

# Unde apare jucătorul când ajunge într-o zonă prin fast-travel.
ZONE_START_POS = {
    "targoviste":       (2, 2),
    "curtea_domneasca": (1, 8),
    "han":              (7, 1),
    "padure":           (7, 6),
    "tabara_otomana":   (11, 10),
}

WALL = "#"
ROAD = "_"


def get_cell_char(row, col):
    if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
        return WORLD_GRID[row][col]
    return WALL


def get_zone_at(row, col):
    return ZONE_CHARS.get(get_cell_char(row, col))


def get_connector_at(row, col):
    return CONNECTOR_CELLS.get((row, col))


def get_map_area_at(row, col):
    """Zona sau conectorul de sub picioarele jucătorului."""
    return get_zone_at(row, col) or get_connector_at(row, col)


def is_wall(row, col):
    """Zid sau în afara hărții — nu se poate trece niciodată."""
    return get_cell_char(row, col) == WALL


def neighbours(row, col):
    return [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]


# --- Validare ---------------------------------------------------------------

def _validate_shape():
    problems = []
    if len(WORLD_GRID) != GRID_ROWS:
        problems.append("WORLD_GRID are %d rânduri, se așteptau %d" % (len(WORLD_GRID), GRID_ROWS))
    for r, row in enumerate(WORLD_GRID):
        if len(row) != GRID_COLS:
            problems.append("rândul %d are %d caractere, se așteptau %d" % (r, len(row), GRID_COLS))
        for c, ch in enumerate(row):
            if ch not in (WALL, ROAD) and ch not in ZONE_CHARS:
                problems.append("caracter necunoscut %r la (%d,%d)" % (ch, r, c))
    return problems


def _validate_zone_separation():
    """Două zone diferite nu au voie să se atingă: altfel se sare peste conector."""
    problems = []
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            zone = get_zone_at(r, c)
            if zone is None:
                continue
            for dr, dc in ((0, 1), (1, 0)):
                other = get_zone_at(r + dr, c + dc)
                if other is not None and other != zone:
                    problems.append(
                        "zonele %s și %s se ating direct la (%d,%d)-(%d,%d)"
                        % (zone, other, r, c, r + dr, c + dc)
                    )
    return problems


def _validate_roads():
    """Fiecare celulă de drum are un nume și duce undeva — nicio fundătură."""
    problems = []
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if get_cell_char(r, c) != ROAD:
                continue
            if get_connector_at(r, c) is None:
                problems.append("celula de drum (%d,%d) nu are intrare în CONNECTOR_CELLS" % (r, c))
            deschise = [n for n in neighbours(r, c) if not is_wall(n[0], n[1])]
            if len(deschise) < 2:
                problems.append("celula de drum (%d,%d) e fundătură" % (r, c))

    for (r, c), conn in CONNECTOR_CELLS.items():
        if get_cell_char(r, c) != ROAD:
            problems.append("conectorul %s indică (%d,%d), care nu e celulă de drum" % (conn, r, c))
    return problems


def _validate_start_positions():
    problems = []
    for zone, (r, c) in ZONE_START_POS.items():
        if get_zone_at(r, c) != zone:
            problems.append("ZONE_START_POS[%s]=(%d,%d) nu cade pe zona %s" % (zone, r, c, zone))
    for zone in ZONE_CHARS.values():
        if zone not in ZONE_START_POS:
            problems.append("zona %s nu are poziție de spawn pentru fast-travel" % zone)
    return problems


def reachable_cells(start=None):
    """Flood fill peste tot ce nu e zid, ignorând deblocările de poveste."""
    if start is None:
        start = ZONE_START_POS["targoviste"]
    seen = set()
    stack = [start]
    while stack:
        cell = stack.pop()
        if cell in seen or is_wall(cell[0], cell[1]):
            continue
        seen.add(cell)
        stack.extend(neighbours(cell[0], cell[1]))
    return seen


def _validate_reachability():
    gasite = set(get_zone_at(r, c) for (r, c) in reachable_cells())
    return [
        "zona %s nu e accesibilă pe jos din Târgoviște" % zone
        for zone in ZONE_CHARS.values() if zone not in gasite
    ]


def connector_endpoints():
    """Ce zone leagă efectiv fiecare coridor, citit de pe grilă."""
    real = {}
    for (r, c), conn in CONNECTOR_CELLS.items():
        for nr, nc in neighbours(r, c):
            zone = get_zone_at(nr, nc)
            if zone is not None:
                real.setdefault(conn, set()).add(zone)
    return real


def _validate_declared_connections(location_connections):
    """Graful desenat pe grilă trebuie să coincidă cu `connections` din LOCATIONS."""
    if not location_connections:
        return []

    problems = []
    real = connector_endpoints()

    for conn, zones in real.items():
        declarate = set(location_connections.get(conn, []))
        if zones != declarate:
            problems.append(
                "conectorul %s leagă pe hartă %s, dar în LOCATIONS scrie %s"
                % (conn, sorted(zones), sorted(declarate))
            )

    for loc_id in location_connections:
        if loc_id.startswith(("drum_", "camp_")) and loc_id not in real:
            problems.append("conectorul %s e definit în LOCATIONS, dar nu are nicio celulă pe hartă" % loc_id)

    return problems


def validate_world_grid(location_connections=None):
    """Întoarce lista problemelor găsite. Listă goală = harta e coerentă."""
    problems = []
    problems.extend(_validate_shape())
    problems.extend(_validate_zone_separation())
    problems.extend(_validate_roads())
    problems.extend(_validate_start_positions())
    problems.extend(_validate_reachability())
    problems.extend(_validate_declared_connections(location_connections))
    return problems
