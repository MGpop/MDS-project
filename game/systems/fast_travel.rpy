init python:
    def get_fast_travel_options():
        return [
            loc_id for loc_id, data in LOCATIONS.items()
            if data.get("type") == "main"
            and is_location_unlocked(loc_id)
            and loc_id != player_location
        ]

label fast_travel_menu:
    $ _options = get_fast_travel_options()

    if not _options:
        "Nu ai alte locații deblocate spre care să călătorești rapid."
        return

    "Unde vrei să mergi?"

    $ _menu_items = [(location_name(d), d) for d in _options]
    # Valoarea nu are voie să fie None: renpy.display_menu ar afișa intrarea ca
    # titlu, nu ca buton apăsabil.
    $ _menu_items.append(("Anulează", "__anuleaza__"))

    $ _choice = renpy.display_menu(_menu_items, screen="choice")

    if _choice == "__anuleaza__" or _choice is None:
        return

    "[player_name] se deplasează rapid spre [location_name(_choice)]."
    $ player_location = _choice
    $ last_entered_zone = _choice
    $ _pos = ZONE_START_POS.get(_choice, (0, 0))
    $ player_grid_row = _pos[0]
    $ player_grid_col = _pos[1]
    call expression "enter_" + _choice
    call environment_director_on_enter(_choice)
    return
