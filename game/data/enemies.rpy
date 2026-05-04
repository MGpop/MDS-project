init python:
    # Inamicii sunt folosiți în combat_system (alegeri, nu mecanici de bătălie)
    ENEMIES = {
        "soldat_otoman": {
            "name":       "Soldat otoman",
            "faction":    "ottomans",
            "difficulty": 1,
            "locations":  ["tabara_otomana", "drum_padure_tabara"],
            "reward":     "monede",
        },
        "boier_garda": {
            "name":       "Gardă boierească",
            "faction":    "boyars",
            "difficulty": 1,
            "locations":  ["targoviste", "han"],
            "reward":     "monede",
        },
        "asasin_ordin": {
            "name":       "Asasin al Ordinului",
            "faction":    "order",
            "difficulty": 2,
            "locations":  ["drum_targoviste_curtea", "camp_han_padure"],
            "reward":     "sigiliu_ordin",
        },
        "soldat_vlad": {
            "name":       "Soldat al lui Vlad",
            "faction":    "vlad",
            "difficulty": 1,
            "locations":  ["curtea_domneasca", "drum_targoviste_curtea"],
            "reward":     "monede",
        },
        "haiduc": {
            "name":       "Haiduc",
            "faction":    "none",
            "difficulty": 1,
            "locations":  ["padure", "camp_han_padure", "drum_padure_tabara"],
            "reward":     "monede",
        },
    }
