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

    def location_connections(loc_id):
        return LOCATIONS.get(loc_id, {}).get("connections", [])

    def is_location_unlocked(loc_id):
        return loc_id in unlocked_locations

    def unlock_location(loc_id):
        if loc_id not in unlocked_locations:
            unlocked_locations.append(loc_id)
