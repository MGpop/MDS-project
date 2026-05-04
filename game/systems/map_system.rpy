init python:
    def can_travel_to(dest_id):
        if not is_location_unlocked(dest_id):
            return False
        # Locațiile de legătură nu sunt destinații directe din meniu
        if LOCATIONS.get(dest_id, {}).get("type") == "connector":
            return False
        return dest_id in location_connections(player_location)

    def get_travel_destinations():
        return [
            loc_id for loc_id in location_connections(player_location)
            if is_location_unlocked(loc_id)
            and LOCATIONS.get(loc_id, {}).get("type") != "connector"
        ]

label map_menu:
    $ destinations = get_travel_destinations()

    if not destinations:
        "Nu ai unde să mergi de aici."
        return

    $ menu_items = [(location_name(d), d) for d in destinations]
    $ menu_items.append(("Rămân aici", None))

    $ choice = renpy.display_menu(menu_items, screen="choice")

    if choice is None:
        return

    call travel_to(choice)

label travel_to(dest_id):
    $ route_key = (player_location, dest_id)
    $ connector_id = TRAVEL_ROUTES.get(route_key)

    if connector_id:
        call expression "enter_" + connector_id

    call expression "enter_" + dest_id
    return
