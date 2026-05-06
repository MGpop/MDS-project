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

    CONNECTOR_CELLS = {
        (2, 4):  "drum_targoviste_han",
        (2, 5):  "drum_targoviste_han",
        (3, 3):  "drum_targoviste_han",
        (3, 4):  "drum_targoviste_han",
        (4, 0):  "drum_targoviste_han",
        (4, 2):  "drum_targoviste_han",
        (4, 3):  "drum_targoviste_han",
        (5, 0):  "drum_targoviste_han",
        (5, 3):  "drum_targoviste_han",
        (6, 0):  "drum_targoviste_han",

        (5, 4):  "camp_han_padure",
        (6, 3):  "camp_han_padure",
        (7, 2):  "camp_han_padure",
        (7, 3):  "camp_han_padure",
        (8, 3):  "camp_han_padure",
        (8, 4):  "camp_han_padure",

        (9, 4):  "drum_padure_tabara",
        (9, 5):  "drum_padure_tabara",
        (10, 5): "drum_padure_tabara",
        (11, 6): "drum_padure_tabara",
    }

    def get_connector_at(row, col):
        return CONNECTOR_CELLS.get((row, col))

    def get_map_area_at(row, col):
        zone = get_zone_at(row, col)
        if zone:
            return zone
        return get_connector_at(row, col)

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
    # Grila lumii: 12 rânduri × 12 coloane
    # T=Târgoviște  C=Curtea Domnească  H=Han  P=Pădure  O=Tabăra otomană
    # _=drum traversabil  #=zid (inaccesibil)
    GRID_ROWS = 12
    GRID_COLS = 12

    WORLD_GRID = [
        "##CCCC######",   # rând 0
        "#TTCC#######",   # rând 1
        "TTTT__######",   # rând 2  ← start jucător (2,1)
        "TTT__#######",   # rând 3
        "_T__########",   # rând 4
        "_HH__#######",   # rând 5
        "_HH_PPP#####",   # rând 6
        "##__PPPP####",   # rând 7
        "###__PPPPOO#",   # rând 8
        "####__PPOOO#",   # rând 9
        "#####__OOO##",   # rând 10
        "######_#OO##",   # rând 11
    ]

    ZONE_CHARS = {
        'T': 'targoviste',
        'C': 'curtea_domneasca',
        'H': 'han',
        'P': 'padure',
        'O': 'tabara_otomana',
    }

    # Poziția de spawn pe grilă pentru fiecare locație
    ZONE_START_POS = {
        'targoviste':       (2, 1),
        'curtea_domneasca': (0, 3),
        'han':              (5, 2),
        'padure':           (7, 5),
        'tabara_otomana':   (9, 9),
    }

    # Culori minimapă
    MINIMAP_COLORS = {
        'T': "#8B7355",
        'C': "#696969",
        'H': "#CD853F",
        'P': "#228B22",
        'O': "#B8860B",
        '_': "#A0A0A0",
        '#': "#1A1A1A",
    }

    def get_cell_char(row, col):
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return WORLD_GRID[row][col]
        return '#'

    def get_zone_at(row, col):
        return ZONE_CHARS.get(get_cell_char(row, col))

    def is_grid_passable(row, col):
        c = get_cell_char(row, col)
        if c == '#':
            return False
        zone = ZONE_CHARS.get(c)
        if zone:
            return is_location_unlocked(zone)
        return True  # celulele '_' (drum) sunt mereu accesibile
