init python:
    # Fiecare NPC are: faction, location, available (dacă e vizibil în acel moment al jocului)
    NPC_REGISTRY = {
        "vlad_tepes": {
            "name":     "Vlad Țepeș",
            "faction":  "vlad",
            "location": "curtea_domneasca",
            "chapter_from": 1,
        },
        "mircea_boier": {
            "name":     "Mircea Bălan",
            "faction":  "boyars",
            "location": "han",
            "chapter_from": 1,
        },
        "radu_boier": {
            "name":     "Radu din Craiova",
            "faction":  "boyars",
            "location": "targoviste",
            "chapter_from": 2,
        },
        "kemal_otoman": {
            "name":     "Kemal Pașa",
            "faction":  "ottomans",
            "location": "tabara_otomana",
            "chapter_from": 2,
        },
        "calin_ordin": {
            "name":     "Călin",
            "faction":  "order",
            "location": "targoviste",
            "chapter_from": 1,
        },
    }

    def npc_available(npc_id):
        npc = NPC_REGISTRY.get(npc_id)
        if npc is None:
            return False
        return current_chapter >= npc["chapter_from"]

    def npc_at_location(location_id):
        return [
            npc_id for npc_id, data in NPC_REGISTRY.items()
            if data["location"] == location_id and npc_available(npc_id)
        ]
