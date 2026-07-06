init python:
    # Inamicii sunt folosiți în combat_system (alegeri, nu mecanici de bătălie)
    ENEMIES = {
        "lup": {
            "name":       "Lup",
            "faction":    "wild",
            "difficulty": 1,
            "locations":  ["drum_sat_han"],
            "reward":     "nimic",

            "max_health": 60,
            "damage": 8,

            "default_sprite": "lup_default",
            "spotted_sprite": "lup_spotted",
            "fight_sprite": "lup_fight",
            "parry_sprite": "lup_parry",
            "light_sprite": "lup_light",
            "heavy_sprite": "lup_heavy",
        },
        "soldat_otoman": {
            "name":       "Soldat otoman",
            "faction":    "ottomans",
            "difficulty": 1,
            "locations":  ["tabara_otomana", "drum_padure_tabara"],
            "reward":     "monede",

            "max_health": 100,
            "damage": 10,

            "default_sprite": "otoman_default",
            "spotted_sprite": "otoman_spotted",
            "fight_sprite": "otoman_fight",
            "parry_sprite": "otoman_parry",
            "light_sprite": "otoman_light",
            "heavy_sprite": "otoman_heavy",
        },
        # "boier_garda": {
        #     "name":       "Gardă boierească",
        #     "faction":    "boyars",
        #     "difficulty": 1,
        #     "locations":  ["targoviste", "han"],
        #     "reward":     "monede",
        # },
        # "asasin_ordin": {
        #     "name":       "Asasin al Ordinului",
        #     "faction":    "order",
        #     "difficulty": 2,
        #     "locations":  ["drum_targoviste_curtea", "camp_han_padure"],
        #     "reward":     "sigiliu_ordin",
        # },
        # "soldat_vlad": {
        #     "name":       "Soldat al lui Vlad",
        #     "faction":    "vlad",
        #     "difficulty": 1,
        #     "locations":  ["curtea_domneasca", "drum_targoviste_curtea"],
        #     "reward":     "monede",
        # },
        # "haiduc": {
        #     "name":       "Haiduc",
        #     "faction":    "none",
        #     "difficulty": 1,
        #     "locations":  ["padure", "camp_han_padure", "drum_padure_tabara"],
        #     "reward":     "monede",
        # },
        "haiduc_cufar": {
            "name":       "Haiducul",
            "faction":    "haiduci",
            "difficulty": 1,
            "locations":  ["padure"],
            "reward":     "cufar_boier",

            "max_health": 80,
            "damage": 9,

            "default_sprite": "haiduc_default",
            "spotted_sprite": "haiduc_spotted",
            "fight_sprite": "haiduc_fight",
            "parry_sprite": "haiduc_parry",
            "light_sprite": "haiduc_light",
            "heavy_sprite": "haiduc_heavy",
        },
        "boier_han": {
            "name":       "Boierul",
            "faction":    "boyars",
            "difficulty": 1,
            "locations":  ["han"],
            "reward":     "pecete_targoviste",

            "max_health": 70,
            "damage": 8,

            "default_sprite": "boier_default",
            "spotted_sprite": "boier_spotted",
            "fight_sprite": "boier_fight",
            "parry_sprite": "boier_parry",
            "light_sprite": "boier_light",
            "heavy_sprite": "boier_heavy",
        },
    }
