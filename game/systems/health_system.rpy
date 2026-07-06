init python:
    MERINDE_ITEM_ID = "merinde"
    MERINDE_HEAL_AMOUNT = 15

    def ensure_inventory_state():
        if not hasattr(store, "inventory") or store.inventory is None:
            store.inventory = {}

    def inventory_count(item_id):
        ensure_inventory_state()
        return int(store.inventory.get(item_id, 0) or 0)

    def merinde_count():
        return inventory_count(MERINDE_ITEM_ID)

    def health_missing():
        max_health = int(getattr(store, "player_max_health", 100) or 100)
        current_health = int(getattr(store, "player_health", max_health) or max_health)
        return max(0, max_health - current_health)

    def can_use_merinde():
        return merinde_count() > 0 and health_missing() > 0

    def consume_inventory_item(item_id, count=1):
        ensure_inventory_state()

        current_count = int(store.inventory.get(item_id, 0) or 0)
        if current_count <= 0:
            return False

        new_count = max(0, current_count - int(count))

        if new_count <= 0:
            if item_id in store.inventory:
                del store.inventory[item_id]
        else:
            store.inventory[item_id] = new_count

        return True

    def use_merinde():
        """
        Consumă o merinde și vindecă playerul cu maximum 15 HP.

        Returnează un dict cu:
        - used: True/False
        - healed: câte puncte de sănătate au fost refăcute
        - message: text afișabil în joc
        """

        ensure_inventory_state()

        max_health = int(getattr(store, "player_max_health", 100) or 100)
        current_health = int(getattr(store, "player_health", max_health) or max_health)

        if current_health >= max_health:
            store.player_health = max_health
            return {
                "used": False,
                "healed": 0,
                "message": "Ai deja sănătatea maximă.",
            }

        if merinde_count() <= 0:
            return {
                "used": False,
                "healed": 0,
                "message": "Nu ai merinde.",
            }

        healed = min(MERINDE_HEAL_AMOUNT, max_health - current_health)
        store.player_health = min(max_health, current_health + healed)
        consume_inventory_item(MERINDE_ITEM_ID, 1)

        try:
            renpy.restart_interaction()
        except Exception:
            pass

        return {
            "used": True,
            "healed": healed,
            "message": "Mănânci câteva merinde și îți refaci %s puncte de sănătate." % healed,
        }


label use_merinde_from_map:
    $ _merinde_result = use_merinde()
    $ _merinde_message = _merinde_result.get("message", "")
    "[_merinde_message]"
    return
