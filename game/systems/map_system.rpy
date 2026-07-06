init python:
    GRID_DIRECTION_DELTAS = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
        "up_left": (-1, -1),
        "up_right": (-1, 1),
        "down_left": (1, -1),
        "down_right": (1, 1),
    }

    GRID_OPPOSITE_DIRECTIONS = {
        "up": "down",
        "down": "up",
        "left": "right",
        "right": "left",
    }

    HAN_ENTRANCE_CELL = (15, 9)
    HAN_DOOR_CELL = (14, 9)

    HAN_RESTRICTED_CELLS = {
        (14, 8),
        (14, 10),
        (13, 8),
        (13, 9),
        (13, 10),
    }

    CITY_ENTRY_PAIRS = {
        (10, 26): (11, 26),
        (16, 20): (16, 21),
        (22, 26): (21, 26),
    }

    CITY_EXIT_PAIRS = {
        (11, 26): (10, 26),
        (16, 21): (16, 20),
        (21, 26): (22, 26),
    }

    def player_has_city_seal():
        inventory = getattr(store, "inventory", {})
        return bool(getattr(store, "got_city_seal", False) or inventory.get("pecete_targoviste", 0) > 0)

    def is_city_entry_attempt(source, target):
        return CITY_ENTRY_PAIRS.get(source) == target

    def is_city_exit_attempt(source, target):
        return CITY_EXIT_PAIRS.get(source) == target

    def can_move_between_grid_cells(row, col, nr, nc):
        source = (row, col)
        target = (nr, nc)

        source_zone = get_zone_at(row, col)
        target_zone = get_zone_at(nr, nc)

        # Încercarea de intrare în Târgoviște trebuie să fie posibilă
        # ca butonul/tasta să funcționeze și soldatul să poată reacționa.
        if is_city_entry_attempt(source, target):
            return True

        # Odată intrat în cetate, poți ieși doar prin cele trei porți.
        if source_zone == "ztargoviste" and target_zone != "ztargoviste":
            return is_city_exit_attempt(source, target) and is_grid_passable(nr, nc)

        # Nu poți intra în Târgoviște prin alte margini ale zonei.
        if source_zone != "ztargoviste" and target_zone == "ztargoviste":
            return False

        if not is_grid_passable(nr, nc):
            return False

        # Poți intra pe celula ușii hanului doar din fața hanului
        # sau întorcându-te din interior.
        if target == HAN_DOOR_CELL:
            return source == HAN_ENTRANCE_CELL or source in HAN_RESTRICTED_CELLS

        # Celulele interioare ale hanului pot fi accesate doar din celula ușii.
        if target in HAN_RESTRICTED_CELLS:
            return store.han_entry_reached and source == HAN_DOOR_CELL

        # Dacă ești într-o celulă interioară, poți ieși doar înapoi pe ușă.
        if source in HAN_RESTRICTED_CELLS:
            return target == HAN_DOOR_CELL

        return True

    def combine_grid_directions(first_dir, second_dir):
        """
        Folosit doar pentru tastatură.
        Dacă a doua tastă formează o diagonală validă, întoarce diagonala.
        Dacă este opusă, aceeași direcție sau absentă, păstrează prima direcție.
        """
        if first_dir not in GRID_OPPOSITE_DIRECTIONS:
            return first_dir

        if second_dir not in GRID_OPPOSITE_DIRECTIONS:
            return first_dir

        if second_dir == first_dir:
            return first_dir

        if second_dir == GRID_OPPOSITE_DIRECTIONS[first_dir]:
            return first_dir

        vertical = first_dir if first_dir in ("up", "down") else second_dir
        horizontal = first_dir if first_dir in ("left", "right") else second_dir
        return vertical + "_" + horizontal

    def can_move_grid_direction(row, col, direction):
        delta = GRID_DIRECTION_DELTAS.get(direction)
        if not delta:
            return False

        nr = row + delta[0]
        nc = col + delta[1]
        return can_move_between_grid_cells(row, col, nr, nc)


screen grid_movement():
    $ _area      = get_map_area_at(player_grid_row, player_grid_col)
    $ _bg        = grid_background_displayable(player_grid_row, player_grid_col)
    $ _zone_name = location_name(_area) if _area else "Drum"
    $ _zone_desc = (LOCATIONS.get(_area, {}).get("description", "") if _area else "") or "Un drum prăfuit, fără semne de viață."
    $ _grid_actor = grid_actor_at(player_grid_row, player_grid_col)
    $ _health_text = "HP: %s/%s" % (player_health, player_max_health)
    $ _merinde_count = merinde_count()

    add _bg

    # Actor vizual pe celula curentă — apare peste background, sub UI.
    if _grid_actor == "batran":
        add npc_displayable("batran") at actor_batran

    elif _grid_actor == "boier":
        add npc_displayable("boier") at actor_boier

    elif _grid_actor == "haiduc":
        add npc_displayable("haiduc") at actor_haiduc

    elif _grid_actor == "lup":
        add npc_displayable("lup") at actor_lup

    # Panou informații locație — stânga sus
    frame:
        xpos 20
        ypos 20
        xsize 440
        background Solid("#000000BB")
        xpadding 14
        ypadding 12

        vbox:
            spacing 8
            text _zone_name style "grid_zone_title"
            text _zone_desc style "grid_zone_desc"

    # Butoane rapide — stânga sus, sub panoul locației
    hbox:
        xpos 20
        ypos 148
        spacing 8

        text _health_text:
            yalign 0.5
            style "hud_status_text"

        textbutton ("Merinde x%s (H)" % _merinde_count):
            action Return("use_merinde")
            style "hud_btn"

        textbutton "Inventar (I)":
            action Return("open_inventory")
            style "hud_btn"

        textbutton "Arme (P)":
            action Return("open_arms")
            style "hud_btn"

    # Minimapă — dreapta sus
    button:
        xalign 1.0
        yalign 0.0
        xoffset -12
        yoffset 12
        xpadding 0
        ypadding 0
        background None
        hover_background Solid("#FFFFFF22")
        action Return("open_map")

        frame:
            xpadding 4
            ypadding 4
            background Solid("#000000CC")

            vbox:
                spacing 0
                for r in range(GRID_ROWS):
                    hbox:
                        spacing 0
                        for c in range(GRID_COLS):
                            $ _mc = get_minimap_display_color_at(r, c)
                            add Solid(_mc, xsize=7, ysize=7)

    # D-pad — 8 direcții pentru mouse
    vbox:
        xalign 0.5
        yalign 1.0
        yoffset -25
        spacing 4

        hbox:
            spacing 4
            xalign 0.5
            textbutton "↖":
                action Return("move_up_left")
                sensitive can_move_grid_direction(player_grid_row, player_grid_col, "up_left")
                style "dpad_btn"
            textbutton "▲":
                action Return("move_up")
                sensitive can_move_grid_direction(player_grid_row, player_grid_col, "up")
                style "dpad_btn"
            textbutton "↗":
                action Return("move_up_right")
                sensitive can_move_grid_direction(player_grid_row, player_grid_col, "up_right")
                style "dpad_btn"

        hbox:
            spacing 4
            xalign 0.5
            textbutton "←":
                action Return("move_left")
                sensitive can_move_grid_direction(player_grid_row, player_grid_col, "left")
                style "dpad_btn"
            textbutton "●":
                action Return("interact")
                style "dpad_center_btn"
            textbutton "→":
                action Return("move_right")
                sensitive can_move_grid_direction(player_grid_row, player_grid_col, "right")
                style "dpad_btn"

        hbox:
            spacing 4
            xalign 0.5
            textbutton "↙":
                action Return("move_down_left")
                sensitive can_move_grid_direction(player_grid_row, player_grid_col, "down_left")
                style "dpad_btn"
            textbutton "▼":
                action Return("move_down")
                sensitive can_move_grid_direction(player_grid_row, player_grid_col, "down")
                style "dpad_btn"
            textbutton "↘":
                action Return("move_down_right")
                sensitive can_move_grid_direction(player_grid_row, player_grid_col, "down_right")
                style "dpad_btn"

    # Prima tastă: nu mișcă imediat personajul.
    # Label-ul așteaptă apoi foarte scurt o a doua tastă pentru diagonală.
    key "K_UP"       action Return("key_up")
    key "K_DOWN"     action Return("key_down")
    key "K_LEFT"     action Return("key_left")
    key "K_RIGHT"    action Return("key_right")
    key "K_w"        action Return("key_up")
    key "K_s"        action Return("key_down")
    key "K_a"        action Return("key_left")
    key "K_d"        action Return("key_right")
    key "K_RETURN"   action Return("interact")
    key "K_KP_ENTER" action Return("interact")
    key "K_SPACE"    action Return("interact")
    key "K_m"        action Return("open_map")
    key "K_i"        action Return("open_inventory")
    key "K_p"        action Return("open_arms")
    key "K_h"        action Return("use_merinde")


screen grid_second_direction(first_dir):
    # Buffer scurt pentru diagonale pe tastatură.
    # Dacă nu vine nicio tastă în interval, rămâne direcția inițială.
    modal True

    timer 0.15 action Return(None)

    key "K_UP"       action Return("up")
    key "K_DOWN"     action Return("down")
    key "K_LEFT"     action Return("left")
    key "K_RIGHT"    action Return("right")
    key "K_w"        action Return("up")
    key "K_s"        action Return("down")
    key "K_a"        action Return("left")
    key "K_d"        action Return("right")


label grid_map:
    $ sync_combat_move_stats()
    call screen grid_movement
    $ _dir = _return

    if _dir == "open_map":
        call open_world_fast_travel_map
        jump grid_map

    if _dir == "open_inventory":
        call open_inventory
        jump grid_map

    if _dir == "open_arms":
        call open_arms
        jump grid_map

    if _dir == "use_merinde":
        call use_merinde_from_map
        jump grid_map

    if _dir == "interact":
        $ _z = get_zone_at(player_grid_row, player_grid_col)
        if _z == "zcurte" and renpy.has_label("zone_actions_zcurte_open"):
            call zone_actions_zcurte_open
        elif _z and renpy.has_label("zone_actions_" + _z):
            call expression "zone_actions_" + _z
        else:
            "Nu ai ce face acum. Continuă să explorezi."
        jump grid_map

    if _dir and _dir.startswith("key_"):
        $ _first_dir = _dir.replace("key_", "", 1)
        call screen grid_second_direction(_first_dir)
        $ _second_dir = _return
        $ _dir = combine_grid_directions(_first_dir, _second_dir)
    elif _dir and _dir.startswith("move_"):
        $ _dir = _dir.replace("move_", "", 1)

    $ _delta = GRID_DIRECTION_DELTAS.get(_dir, (0, 0))
    $ _nr = player_grid_row + _delta[0]
    $ _nc = player_grid_col + _delta[1]

    $ _source_cell = (player_grid_row, player_grid_col)
    $ _target_cell = (_nr, _nc)

    if is_city_entry_attempt(_source_cell, _target_cell) and not player_has_city_seal():
        "Soldatul român îți blochează drumul cu sulița."
        soldat_roman "Fără pecete nu intri în Târgoviște."
        jump grid_map

    if is_city_entry_attempt(_source_cell, _target_cell) and player_has_city_seal():
        $ unlock_zone("ztargoviste", unlock_fast=False)

    if can_move_between_grid_cells(player_grid_row, player_grid_col, _nr, _nc):
        $ _prev_zone = get_zone_at(player_grid_row, player_grid_col)
        $ player_grid_row = _nr
        $ player_grid_col = _nc

        if player_grid_row == 15 and player_grid_col == 9 and not han_entry_reached:
            $ han_entry_reached = True
        
        if player_grid_row == 22 and player_grid_col == 7 and not wolf_tutorial_done:
            $ wolf_tutorial_active = True

            scene expression grid_background_displayable(player_grid_row, player_grid_col) with dissolve
            show expression npc_displayable("lup") as npc_lup at actor_lup

            "Un mârâit se aude din iarba înaltă."
            "Un lup îți taie calea."

            hide npc_lup
            $ wolf_tutorial_done = True

            call start_combat("lup", "grid_map")

        $ _next_zone = get_zone_at(_nr, _nc)
        if _next_zone and _next_zone != _prev_zone:
            $ player_location = _next_zone
            $ unlock_fast_travel(_next_zone)
            if renpy.has_label("enter_" + _next_zone):
                call expression "enter_" + _next_zone

    jump grid_map


style dpad_btn:
    xsize 72
    ysize 72
    xpadding 16
    ypadding 16
    background Solid("#2A1A0A")
    hover_background Solid("#5A3A1A")
    insensitive_background Solid("#111111")

style dpad_btn_text:
    font "DejaVuSans.ttf"
    xalign 0.5
    yalign 0.5
    size 30
    color "#D4AF37"
    hover_color "#FFD700"
    insensitive_color "#333333"

style dpad_center_btn:
    xsize 72
    ysize 72
    xpadding 16
    ypadding 16
    background Solid("#1A3A2A")
    hover_background Solid("#2A6A4A")

style dpad_center_btn_text:
    font "DejaVuSans.ttf"
    xalign 0.5
    yalign 0.5
    size 30
    color "#88CCAA"
    hover_color "#AAFFCC"

style hud_btn:
    xpadding 14
    ypadding 8
    background Solid("#000000CC")
    hover_background Solid("#3A2712DD")

style hud_btn_text:
    color "#E8D5A3"
    hover_color "#FFD700"
    size 18
    outlines [(1, "#000000", 1, 1)]

style hud_status_text:
    color "#E8D5A3"
    size 18
    outlines [(1, "#000000", 1, 1)]

style grid_zone_title:
    font "fonts/Cinzel/static/Cinzel-SemiBold.ttf"
    size 26
    color "#D4AF37"
    outlines [(1, "#000000", 1, 1)]

style grid_zone_desc:
    font "fonts/Cormorant_Upright/CormorantUpright-Regular.ttf"
    size 18
    color "#C0A080"
    line_leading 4