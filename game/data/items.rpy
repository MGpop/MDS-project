init python:
    ITEMS = {
        # "sigiliu_ordin": {
        #     "name":        "Sigiliul Ordinului",
        #     "description": "Sigiliul de ceară al Ordinului Dragonului. Deschide uși și guri.",
        #     "type":        "key",
        #     "stackable":   False,
        # },
        # "scrisoare_secreta": {
        #     "name":        "Scrisoare secretă",
        #     "description": "O scrisoare codificată. Nu știi încă de la cine.",
        #     "type":        "document",
        #     "stackable":   False,
        # },
        # "pumnal": {
        #     "name":        "Pumnal",
        #     "description": "Un pumnal scurt cu lama înnegrită. Discret și eficient.",
        #     "type":        "weapon",
        #     "stackable":   False,
        # },
        # "document_boieri": {
        #     "name":        "Document boieresc",
        #     "description": "Dovedește o înțelegere secretă între boieri și otomani.",
        #     "type":        "document",
        #     "stackable":   False,
        # },
        # "relicva_ordin": {
        #     "name":        "Relicvă a Ordinului",
        #     "description": "Un obiect vechi cu simbolul dragonului. Aparținea părintelui tău.",
        #     "type":        "relic",
        #     "stackable":   False,
        # },
        "monede": {
            "name":        "Monede",
            "description": "Bani pentru mită sau cumpărături.",
            "type":        "currency",
            "stackable":   True,
        },

        "cufar_boier": {
            "name":        "Cufărul boierului",
            "description": "Un cufăr greu, întărit cu fier. Boierul spune că i-a fost furat de haiduci.",
            "type":        "quest",
            "stackable":   False,
        },

        "pecete_targoviste": {
            "name":        "Pecete de trecere",
            "description": "O pecete boierească ce îți poate permite intrarea în Târgoviște.",
            "type":        "key",
            "stackable":   False,
        },

        "merinde": {
            "name":        "Merinde",
            "description": "Provizii. Foloseștele pentru a te vindeca.",
            "type":        "health",
            "stackable":   True,
        },

        "cupa_fantana": {
            "name":        "Cupa de aur din legende",
            "description": "Nimeni nu îndrăznește să fure de sub nasul lui Țepeș. Această cupă își are locul la fântână.",
            "type":        "side-quest",
            "stackable":   False,
        },
    }

    def add_item(item_id, count=1):
        if item_id not in inventory:
            inventory[item_id] = 0
        inventory[item_id] += count

    def remove_item(item_id, count=1):
        if item_id in inventory:
            inventory[item_id] = max(0, inventory[item_id] - count)
            if inventory[item_id] == 0:
                del inventory[item_id]

    def has_item(item_id):
        return inventory.get(item_id, 0) > 0
