init python:
    LOCATIONS = {
        # Locații principale
        "targoviste": {
            "name":        "Târgoviște",
            "description": "Capitala Țării Românești. Străzi înguste, priviri suspicioase, mirosul fumului de la torțe.",
            "type":        "main",
            "chapter_unlock": 1,
            "connections": ["curtea_domneasca", "han"],
            "background":  "bg_targoviste",
        },
        "curtea_domneasca": {
            "name":        "Curtea Domnească",
            "description": "Reședința lui Vlad. Soldați la fiecare intrare. Nimeni nu intră fără motiv.",
            "type":        "main",
            "chapter_unlock": 1,
            "connections": ["targoviste"],
            "background":  "bg_curtea_domneasca",
        },
        "han": {
            "name":        "Hanul Corbului Negru",
            "description": "Singurul loc unde poți auzi șoapte fără să riști capul. Deocamdată.",
            "type":        "main",
            "chapter_unlock": 1,
            "connections": ["targoviste", "padure"],
            "background":  "bg_han",
        },
        "padure": {
            "name":        "Pădurea Vlăsiei",
            "description": "Întunecată, deasă, periculoasă. Locul unde Vlad și-a construit primul rând de țepe.",
            "type":        "main",
            "chapter_unlock": 2,
            "connections": ["han", "tabara_otomana"],
            "background":  "bg_padure",
        },
        "tabara_otomana": {
            "name":        "Tabăra otomană",
            "description": "Ascunsă dincolo de pădure. Oficial nu există. Toată lumea știe că există.",
            "type":        "main",
            "chapter_unlock": 2,
            "connections": ["padure"],
            "background":  "bg_tabara_otomana",
        },

        # Drumuri / câmpuri — spații de legătură
        "drum_targoviste_curtea": {
            "name":        "Ulița spre Curtea Domnească",
            "description": "Drum pietruit, patrulat. Fiecare pas e văzut.",
            "type":        "connector",
            "chapter_unlock": 1,
            "connections": ["targoviste", "curtea_domneasca"],
            "background":  "bg_drum_oras",
        },
        "drum_targoviste_han": {
            "name":        "Drumul spre Han",
            "description": "Marginea orașului. Lumini rare, umbre multe.",
            "type":        "connector",
            "chapter_unlock": 1,
            "connections": ["targoviste", "han"],
            "background":  "bg_drum_oras",
        },
        "camp_han_padure": {
            "name":        "Câmpul deschis",
            "description": "Fără adăpost. Oricine te poate vedea de la jumătate de leghe.",
            "type":        "connector",
            "chapter_unlock": 2,
            "connections": ["han", "padure"],
            "background":  "bg_camp",
        },
        "drum_padure_tabara": {
            "name":        "Poteca ascunsă",
            "description": "Un drum știut doar de contrabandișți și spioni. Acum și de tine.",
            "type":        "connector",
            "chapter_unlock": 2,
            "connections": ["padure", "tabara_otomana"],
            "background":  "bg_padure",
        },
    }

    def location_name(loc_id):
        return LOCATIONS.get(loc_id, {}).get("name", loc_id)

    def is_location_unlocked(loc_id):
        return loc_id in store.unlocked_locations

    def unlock_location(loc_id):
        if loc_id not in store.unlocked_locations:
            store.unlocked_locations.append(loc_id)

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
