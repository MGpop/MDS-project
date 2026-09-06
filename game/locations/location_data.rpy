init python:
    BACKGROUND_DIR = "images/backgrounds"
    BACKGROUND_FALLBACK = "#101010"

    LOCATIONS = {
        # Locații principale
        "targoviste": {
            "name":        "Târgoviște",
            "description": "Capitala Țării Românești. Străzi înguste, priviri suspicioase, mirosul fumului de la torțe.",
            "type":        "main",
            "chapter_unlock": 1,
            "connections": ["curtea_domneasca", "han"],
            "background":  BACKGROUND_DIR + "/targoviste.png",
        },
        "curtea_domneasca": {
            "name":        "Curtea Domnească",
            "description": "Reședința lui Vlad. Soldați la fiecare intrare. Nimeni nu intră fără motiv.",
            "type":        "main",
            "chapter_unlock": 1,
            "connections": ["targoviste"],
            "background":  BACKGROUND_DIR + "/curtea_domneasca.png",
        },
        "han": {
            "name":        "Hanul Corbului Negru",
            "description": "Singurul loc unde poți auzi șoapte fără să riști capul. Deocamdată.",
            "type":        "main",
            "chapter_unlock": 1,
            "connections": ["targoviste", "padure"],
            "background":  BACKGROUND_DIR + "/han.png",
        },
        "padure": {
            "name":        "Pădurea Vlăsiei",
            "description": "Întunecată, deasă, periculoasă. Locul unde Vlad și-a construit primul rând de țepe.",
            "type":        "main",
            "chapter_unlock": 2,
            "connections": ["han", "tabara_otomana"],
            "background":  BACKGROUND_DIR + "/padure.png",
        },
        "tabara_otomana": {
            "name":        "Tabăra otomană",
            "description": "Ascunsă dincolo de pădure. Oficial nu există. Toată lumea știe că există.",
            "type":        "main",
            "chapter_unlock": 2,
            "connections": ["padure"],
            "background":  BACKGROUND_DIR + "/tabara_otomana.png",
        },

        # Drumuri / câmpuri — spații de legătură
        "drum_targoviste_curtea": {
            "name":        "Ulița spre Curtea Domnească",
            "description": "Drum pietruit, patrulat. Fiecare pas e văzut.",
            "type":        "connector",
            "chapter_unlock": 1,
            "connections": ["targoviste", "curtea_domneasca"],
            "background":  BACKGROUND_DIR + "/drum_oras.png",
        },
        "drum_targoviste_han": {
            "name":        "Drumul spre Han",
            "description": "Marginea orașului. Lumini rare, umbre multe.",
            "type":        "connector",
            "chapter_unlock": 1,
            "connections": ["targoviste", "han"],
            "background":  BACKGROUND_DIR + "/drum_oras.png",
        },
        "camp_han_padure": {
            "name":        "Câmpul deschis",
            "description": "Fără adăpost. Oricine te poate vedea de la jumătate de leghe.",
            "type":        "connector",
            "chapter_unlock": 2,
            "connections": ["han", "padure"],
            "background":  BACKGROUND_DIR + "/camp.png",
        },
        "drum_padure_tabara": {
            "name":        "Poteca ascunsă",
            "description": "Un drum știut doar de contrabandișți și spioni. Acum și de tine.",
            "type":        "connector",
            "chapter_unlock": 2,
            "connections": ["padure", "tabara_otomana"],
            "background":  BACKGROUND_DIR + "/poteca_padure.png",
        },
    }

    def location_name(loc_id):
        return LOCATIONS.get(loc_id, {}).get("name", loc_id)

    def is_location_unlocked(loc_id):
        return loc_id in store.unlocked_locations

    def unlock_location(loc_id):
        if loc_id not in store.unlocked_locations:
            store.unlocked_locations.append(loc_id)

    def location_background_path(loc_id):
        return LOCATIONS.get(loc_id, {}).get("background")

    def location_background_displayable(loc_id):
        path = location_background_path(loc_id)
        if path and renpy.loadable(path):
            return Transform(
                path,
                xysize=(config.screen_width, config.screen_height),
                fit="cover",
                xalign=0.5,
                yalign=0.5,
            )
        return Transform(
            Solid(BACKGROUND_FALLBACK),
            xysize=(config.screen_width, config.screen_height),
            xalign=0.5,
            yalign=0.5,
        )


init -1 python:
    # Datele și validarea hărții stau în game/python-packages/dragon_world/grid.py,
    # ca Python pur — un singur loc adevărat pentru grilă, importabil și de pytest.
    from dragon_world.grid import (
        GRID_ROWS, GRID_COLS, WORLD_GRID, ZONE_CHARS, CHAR_BY_ZONE,
        CONNECTOR_CELLS, ZONE_START_POS,
        get_cell_char, get_zone_at, get_connector_at, get_map_area_at,
        is_wall as is_grid_wall,
        validate_world_grid,
    )


init python:
    # --- Accesibilitate: zid, blocat de poveste, sau liber ---------------------
    # Un zid nu se deschide niciodată; o zonă blocată se deschide pe măsura poveștii.
    # Jocul le tratează diferit: zidul e buton mort, zona blocată dă un mesaj.

    def is_grid_locked(row, col):
        zone = get_zone_at(row, col)
        return zone is not None and not is_location_unlocked(zone)

    def is_grid_passable(row, col):
        if is_grid_wall(row, col):
            return False
        return not is_grid_locked(row, col)

    def grid_block_reason(row, col):
        # Mesajul arătat jucătorului când celula există, dar e închisă.
        # None = ori se poate trece, ori e zid (zidurile nu explică nimic).
        zone = get_zone_at(row, col)
        if zone is not None and not is_location_unlocked(zone):
            return u"Drumul spre %s e închis deocamdată." % location_name(zone)
        return None


    # --- Minimapă --------------------------------------------------------------
    MINIMAP_COLORS = {
        'T': "#B08D57",   # Târgoviște
        'C': "#8C8CA0",   # Curtea Domnească
        'H': "#CD853F",   # Han
        'P': "#2E8B57",   # Pădure
        'O': "#B8860B",   # Tabăra otomană
        '_': "#7A6A55",   # drum
        '#': "#141414",   # zid
    }
    MINIMAP_LOCKED_COLOR = "#2A2620"   # zonă existentă, dar încă nedeblocată
    MINIMAP_PLAYER_COLOR = "#FFF3D0"

    # Zonele din legendă, în ordinea poveștii.
    MINIMAP_LEGEND = [
        'targoviste', 'curtea_domneasca', 'han', 'padure', 'tabara_otomana',
    ]

    def minimap_cell_color(row, col, player_row, player_col):
        if row == player_row and col == player_col:
            return MINIMAP_PLAYER_COLOR
        if is_grid_locked(row, col):
            return MINIMAP_LOCKED_COLOR
        return MINIMAP_COLORS.get(get_cell_char(row, col), "#141414")

    def minimap_legend_color(zone):
        if not is_location_unlocked(zone):
            return MINIMAP_LOCKED_COLOR
        return MINIMAP_COLORS.get(CHAR_BY_ZONE.get(zone), "#141414")

    def minimap_legend_label(zone):
        if not is_location_unlocked(zone):
            return location_name(zone) + u" — blocat"
        return location_name(zone)


    # --- Verificarea hărții la pornire -----------------------------------------
    # Orice inconsistență ajunge în consolă și în log.txt, fără să oprească jocul.
    def _report_grid_problems():
        connections = dict(
            (loc_id, data.get("connections", []))
            for loc_id, data in LOCATIONS.items()
        )
        problems = validate_world_grid(connections)
        for problem in problems:
            print(u"[hartă] PROBLEMĂ: " + problem)
        return problems

    _report_grid_problems()
