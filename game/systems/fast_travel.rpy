init python:
    def get_fast_travel_options():
        # Fast travel disponibil doar spre locații principale deja deblocate
        return [
            loc_id for loc_id, data in LOCATIONS.items()
            if data.get("type") == "main"
            and is_location_unlocked(loc_id)
            and loc_id != player_location
        ]

label fast_travel_menu:
    $ options = get_fast_travel_options()

    if not options:
        "Nu ai alte locații deblocate spre care să călătorești rapid."
        return

    "Unde vrei să mergi?"

    $ menu_items = [(location_name(d), d) for d in options]
    $ menu_items.append(("Anulează", None))

    $ choice = renpy.display_menu(menu_items, screen="choice")

    if choice is None:
        return

    "[player_name] se deplasează rapid spre [location_name(choice)]."
    $ player_location = choice
    call expression "enter_" + choice
    return
