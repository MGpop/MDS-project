init python:
    BACKGROUND_DIR = "images/backgrounds"
    BACKGROUND_FALLBACK = "#101010"

    CELL_BACKGROUNDS = {
        "G": BACKGROUND_DIR + "/camp.png",
        "#": BACKGROUND_DIR + "/campie.png",
        "L": BACKGROUND_DIR + "/luminis.png",
        "P": BACKGROUND_DIR + "/padure.png",
        "H": BACKGROUND_DIR + "/han.png",
        "O": BACKGROUND_DIR + "/tabara_otomana.png",
        "F": BACKGROUND_DIR + "/fantana.png",
        "C": BACKGROUND_DIR + "/curtea_domneasca.png",
    }

    ZONE_BACKGROUNDS = {
        "ztargoviste": BACKGROUND_DIR + "/targoviste.png",
        "zcurte": BACKGROUND_DIR + "/curtea_domneasca.png",
    }

    SPECIAL_CELL_BACKGROUNDS = {
        ("D", "zhan"): BACKGROUND_DIR + "/drum.png",
    }

    LOCATIONS = {
        "zsat": {
            "name":        "Satul de început",
            "description": "Un sat mic, ascuns între câmpuri și marginea pădurii. De aici începe drumul tău.",
            "type":        "main",
            "chapter_unlock": 1,
            "background":  BACKGROUND_DIR + "/sat.png",
        },
        "zhan": {
            "name":        "Hanul Corbului Negru",
            "description": "Drumul se deschide în fața hanului. Aici se aud zvonurile înainte să ajungă la curte.",
            "type":        "main",
            "chapter_unlock": 1,
            "background":  BACKGROUND_DIR + "/han.png",
        },
        "zpadure": {
            "name":        "Pădurea Vlăsiei",
            "description": "Întunecată, deasă, periculoasă. Potecile par să se schimbe după ce treci de ele.",
            "type":        "main",
            "chapter_unlock": 1,
            "background":  BACKGROUND_DIR + "/padure.png",
        },
        "ztargoviste": {
            "name":        "Târgoviște",
            "description": "Capitala Țării Românești. Străzi înguste, priviri suspicioase, mirosul fumului de la torțe.",
            "type":        "main",
            "chapter_unlock": 1,
            "background":  BACKGROUND_DIR + "/targoviste.png",
        },
        "zcurte": {
            "name":        "Curtea Domnească",
            "description": "Reședința lui Vlad. Soldați la fiecare intrare. Nimeni nu intră fără motiv.",
            "type":        "main",
            "chapter_unlock": 1,
            "background":  BACKGROUND_DIR + "/curtea_domneasca.png",
        },
        "zotomani": {
            "name":        "Tabăra otomană",
            "description": "Ascunsă dincolo de pădure. Oficial nu există. Toată lumea știe că există.",
            "type":        "main",
            "chapter_unlock": 2,
            "background":  BACKGROUND_DIR + "/tabara_otomana.png",
        },
    }

    def location_name(loc_id):
        return LOCATIONS.get(loc_id, {}).get("name", loc_id)

    def is_location_unlocked(loc_id):
        return bool(store.unlocked_zone.get(loc_id, False))

    def unlock_location(loc_id):
        unlock_zone(loc_id)

    def unlock_zone(zone_id, unlock_fast=False):
        if zone_id in LOCATIONS:
            store.unlocked_zone[zone_id] = True
            if zone_id not in store.unlocked_locations:
                store.unlocked_locations.append(zone_id)
            if unlock_fast:
                store.unlocked_fast[zone_id] = True

    def unlock_fast_travel(zone_id):
        if zone_id in ZONE_FAST_TRAVEL:
            store.unlocked_fast[zone_id] = True

    def unlock_cell(row, col):
        cell = (row, col)
        if cell not in store.unlocked_cells:
            store.unlocked_cells.append(cell)

    def unlock_cells(cells):
        for row, col in cells:
            unlock_cell(row, col)

    def get_zone_char_at(row, col):
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return MAP_ZONES[row][col]
        return None

    def get_map_area_at(row, col):
        return get_zone_at(row, col)

    def get_minimap_color_at(row, col):
        cell = get_cell_char(row, col)
        return MINIMAP_COLORS.get(cell, "#1A1A1A")

    def grid_background_path(row, col):
        cell = get_cell_char(row, col)
        zone_id = get_zone_at(row, col)

        special_key = (cell, zone_id)
        if special_key in SPECIAL_CELL_BACKGROUNDS:
            return SPECIAL_CELL_BACKGROUNDS[special_key]

        if cell in CELL_BACKGROUNDS:
            return CELL_BACKGROUNDS[cell]

        if zone_id in ZONE_BACKGROUNDS:
            return ZONE_BACKGROUNDS[zone_id]

        return location_background_path(zone_id)

    def grid_background_displayable(row, col):
        path = grid_background_path(row, col)

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


init python:
    GRID_ROWS = 30
    GRID_COLS = 40

    WORLD_GRID = [
        "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPDDDDDOOOOO",   # rând 0
        "PPLLLPPPPPPPDDDDDDDDDDDDPPPPPDPPRRPOOOOO",   # rând 1
        "PLLLLLPPPDDDPPPPPPPPPPPPDPPPDPPPRRPPOOOO",   # rând 2
        "PLLLLLDDDPPPPPPPPPPPPPPPPDPDPPPPRRPPPOOO",   # rând 3
        "PLLLLLPPPPPPPPPPPPPPPPPPPPDPPPPPRRPPPPDO",   # rând 4
        "PPLLLPPPPPPPPPPPPPPPPPPPPPDPPPPPRRPPPPDP",   # rând 5
        "PPPDPPPPPPPPPPPPPPPPPPPPPPDPPPPPRRPPPPDP",   # rând 6
        "PPPDPPPPPPPPPPPPPPPPPPPPPPDPPPPPRRPPPPDP",   # rând 7
        "PPPDPPPPPPPPPPPPPPPPPPPPPPDPPPPPRRPPPPDP",   # rând 8
        "PPPDPPPPPPPPP######PPPPPPPDPPPPPRRPPPPDP",   # rând 9
        "PPPDPPPPPPP##########DDDDDDPPPPPRRPPPPDP",   # rând 10
        "PPPDPPPPP###########DGGGTTDTTPPPRRPPPPDP",   # rând 11
        "PPPDPPP############DGGGTTQDQTTPPRRPPPPDP",   # rând 12
        "PPPPDP##HHH#######DGGGTTQDTDQTTPRRPPPPDP",   # rând 13
        "PPPPPDDDHHH######DGGGTTQDTTTDQTTRRPPPPDP",   # rând 14
        "PPPPPPPPDDD#####DGGGGTQDTTCTTDQTRRPPPPDP",   # rând 15
        "DDDPPPPPPPDDDDDDDDDDDDDDDCCCTDQTRRPPPPDP",   # rând 16
        "###DDPPPPPD#####DGGGGTQDTTCTTDQTRRPPPPDP",   # rând 17
        "GG###DDFDD##GGG##DGGGTTQDTTTDQTTRRPPPPDP",   # rând 18
        "GGGG###D###GGGGG##DGGGTTQDTDQTT#RRPPPDPP",   # rând 19
        "GGGGGG#D#GGGGGGGG##DGGGTTQDQTT##RRPPDPPP",   # rând 20
        "GGGGGG#D#GGGGGGGGG##DGGGTTDTT###RRPDPDPP",   # rând 21
        "GGGGGG#D#GGGGGGGGGG##DDDDDDDDDDDDDDPPPDP",   # rând 22
        "GGGGGG#D#GGGGGGGGGGG######D#####RRPPPPDP",   # rând 23
        "GGGGG##D#GGGGGGGGGGGGG####D#####RRPPPPDP",   # rând 24
        "#######D#GGGGGGGGGGGGGGG##D#####RRPPPPDP",   # rând 25
        "SSSSSDD##GGGGGGGGGGGGGGGG#D#####RRPPPPDP",   # rând 26
        "SSSDDS###GGGGGGGGGGGGGGGG#D#####RRPLLLDP",   # rând 27
        "SDDSSS###GGGGGGGGGGGGGGGG#D#####RRPLLLLP",   # rând 28
        "DSSSSS###GGGGGGGGGGGGGGGG#D#####RRPPPPPP",   # rând 29
    ]

    MAP_ZONES = [
        "2222222222222222222222222222222225555555",   # rând 0
        "22222222222222222222222222222222__555555",   # rând 1
        "22222222222222222222222222222222__555555",   # rând 2
        "22222222222222222222222222222222__555555",   # rând 3
        "22222222222222222222222222222222__555555",   # rând 4
        "22222222222222222222222222222222__555555",   # rând 5
        "22222222222222222222222222222222__555555",   # rând 6
        "22222222222222222222222222222222__555555",   # rând 7
        "22222222222222222222222222222222__555555",   # rând 8
        "22222222222221111112222222222222__555555",   # rând 9
        "22222222222111111111111111122222__555555",   # rând 10
        "22222222211111111111111133333222__555555",   # rând 11
        "22222221111111111111111333333322__555555",   # rând 12
        "22222211111111111111113333333332__555555",   # rând 13
        "22222211111111111111133333333333__555555",   # rând 14
        "22222222111111111111133333433333__555555",   # rând 15
        "11122222221111111111133334443333__555555",   # rând 16
        "11111222221111111111133333433333__555555",   # rând 17
        "11111111111111111111133333333333__555555",   # rând 18
        "11111111111111111111113333333331__555555",   # rând 19
        "11111111111111111111111333333311__555555",   # rând 20
        "11111111111111111111111133333111__555555",   # rând 21
        "1111111111111111111111111111111115555555",   # rând 22
        "11111111111111111111111111111111__555555",   # rând 23
        "11111111111111111111111111111111__555555",   # rând 24
        "11111111111111111111111111111111__555555",   # rând 25
        "00000011111111111111111111111111__555555",   # rând 26
        "00000011111111111111111111111111__555555",   # rând 27
        "00000011111111111111111111111111__555555",   # rând 28
        "00000011111111111111111111111111__555555",   # rând 29
    ]

    ZONE_CHARS = {
        'T': 'targoviste',
        'C': 'curtea_domneasca',
        'H': 'han',
        'P': 'padure',
        'O': 'tabara_otomana',
        'S': 'sat',
        'D': 'drum',
        'L': 'luminis',
        'R': 'parau',
        '#': 'iarba',
        'G': 'grau',
        'F': 'fantana',
        'Q': 'case_targoviste'
    }
    
    MINIMAP_COLORS = {
        'T': "#6e311a",
        'C': "#240d05",
        'H': "#533f37",
        'P': "#0a570a",
        'O': "#520101",
        'S': "#6d5748",
        'D': "#a49386",
        'L': "#159c15",
        'R': "#2e96eb",
        '#': "#a9eca6",
        'G': "#f1d275",
        'F': "#002fb9",
        'Q': "#3a1709",
    }

    ZONE_NAMES = {
        '0': 'zsat',
        '1': 'zhan',
        '2': 'zpadure',
        '3': 'ztargoviste',
        '4': 'zcurte',
        '5': 'zotomani',
        '_': 'zparau',
    }

    # Pozițiile sunt în ordinea internă a grilei: (row, col).
    # zsat corespunde punctului vizual (x=0, y=29).
    ZONE_FAST_TRAVEL = {
        'zsat': (29, 0),
        'zhan': (15, 9),
        'zpadure': (3, 3),
        'ztargoviste': (16, 23),
        'zcurte': (16, 26),
        'zotomani': (1, 38),
    }

    ZONE_START_POS = ZONE_FAST_TRAVEL

    def get_cell_char(row, col):
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return WORLD_GRID[row][col]
        return '#'

    def get_zone_at(row, col):
        zone_char = get_zone_char_at(row, col)
        return ZONE_NAMES.get(zone_char)

    def is_grid_passable(row, col):
        if not (0 <= row < GRID_ROWS and 0 <= col < GRID_COLS):
            return False

        zone_id = get_zone_at(row, col)

        if zone_id is None or zone_id == "zparau":
            return False

        if (row, col) in store.unlocked_cells:
            return True

        return is_location_unlocked(zone_id)
