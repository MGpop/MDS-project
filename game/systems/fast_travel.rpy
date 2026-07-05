init python:
    def get_fast_travel_options():
        return [
            zone_id for zone_id in ZONE_FAST_TRAVEL.keys()
            if store.unlocked_fast.get(zone_id, False)
            and zone_id != store.player_location
        ]

label fast_travel_menu:
    $ _options = get_fast_travel_options()

    if not _options:
        "Nu ai alte zone deblocate spre care să călătorești rapid."
        return

    "Unde vrei să mergi?"

    $ _menu_items = [(location_name(d), d) for d in _options]
    $ _menu_items.append(("Anulează", None))

    $ _choice = renpy.display_menu(_menu_items, screen="choice")

    if _choice is None:
        return

    "[player_name] se deplasează rapid spre [location_name(_choice)]."
    $ player_location = _choice
    $ _pos = ZONE_FAST_TRAVEL.get(_choice, (29, 0))
    $ player_grid_row = _pos[0]
    $ player_grid_col = _pos[1]

    if renpy.has_label("enter_" + _choice):
        call expression "enter_" + _choice

    jump grid_map
