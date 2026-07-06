init python:
    FAST_TRAVEL_COLOR = "#FF1A1A"
    FAST_TRAVEL_HOVER_COLOR = "#FF6666"
    WORLD_MAP_LOCKED_COLOR = "#242424"
    WORLD_MAP_PLAYER_COLOR = "#FFFFFF"

    def get_fast_travel_options():
        return [
            zone_id for zone_id in ZONE_FAST_TRAVEL.keys()
            if store.unlocked_fast.get(zone_id, False)
            and zone_id != store.player_location
        ]

    def get_fast_travel_zone_at(row, col):
        for zone_id, pos in ZONE_FAST_TRAVEL.items():
            if pos == (row, col):
                return zone_id
        return None

    def is_unlocked_fast_travel_point(row, col):
        zone_id = get_fast_travel_zone_at(row, col)
        if not zone_id:
            return False
        return bool(store.unlocked_fast.get(zone_id, False))

    def fast_travel_map_color_at(row, col):
        zone_id = get_fast_travel_zone_at(row, col)

        if zone_id and store.unlocked_fast.get(zone_id, False):
            return FAST_TRAVEL_COLOR

        if row == store.player_grid_row and col == store.player_grid_col:
            return WORLD_MAP_PLAYER_COLOR

        if not is_minimap_cell_revealed(row, col):
            return WORLD_MAP_LOCKED_COLOR

        return get_minimap_color_at(row, col)

screen world_fast_travel_map():
    modal True

    default cell_size = 18

    $ _tooltip = GetTooltip()

    add Solid("#000000DD")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 22
        ypadding 22
        background Solid("#090909EE")

        vbox:
            spacing 14
            xalign 0.5

            text "Harta lumii" xalign 0.5 size 34 color "#E8D5A3"

            fixed:
                xsize GRID_COLS * cell_size
                ysize GRID_ROWS * cell_size

                for r in range(GRID_ROWS):
                    for c in range(GRID_COLS):
                        $ _zone_id = get_fast_travel_zone_at(r, c)
                        $ _is_ft = _zone_id and unlocked_fast.get(_zone_id, False)
                        $ _color = fast_travel_map_color_at(r, c)

                        if _is_ft:
                            button:
                                xpos c * cell_size
                                ypos r * cell_size
                                xsize cell_size
                                ysize cell_size
                                background Solid(_color)
                                hover_background Solid(FAST_TRAVEL_HOVER_COLOR)
                                action Return(("fast_travel", _zone_id))
                                tooltip location_name(_zone_id)
                        else:
                            add Solid(_color, xsize=cell_size, ysize=cell_size):
                                xpos c * cell_size
                                ypos r * cell_size

            if _tooltip:
                text _tooltip xalign 0.5 size 24 color "#FFD700"
            else:
                text "Click pe un punct roșu pentru fast travel. Esc sau M închide harta." xalign 0.5 size 20 color "#AAAAAA"

    key "K_ESCAPE" action Return(None)
    key "K_m" action Return(None)

label open_world_fast_travel_map:
    call screen world_fast_travel_map
    $ _map_result = _return

    if _map_result is None:
        return

    if _map_result[0] == "fast_travel":
        $ _choice = _map_result[1]

        if not unlocked_fast.get(_choice, False):
            return

        if _choice == player_location:
            return

        "[player_name] se deplasează rapid spre [location_name(_choice)]."

        $ player_location = _choice
        $ _pos = ZONE_FAST_TRAVEL.get(_choice, (29, 0))
        $ player_grid_row = _pos[0]
        $ player_grid_col = _pos[1]

        if renpy.has_label("enter_" + _choice):
            call expression "enter_" + _choice

        jump grid_map

    return