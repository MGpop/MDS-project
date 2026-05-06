screen grid_movement():
    $ _area      = get_map_area_at(player_grid_row, player_grid_col)
    $ _bg        = location_background_displayable(_area) if _area else Solid(BACKGROUND_FALLBACK)
    $ _zone_name = location_name(_area) if _area else "Drum"
    $ _zone_desc = (LOCATIONS.get(_area, {}).get("description", "") if _area else "") or "Un drum prăfuit, fără semne de viață."

    add _bg

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

    # Minimapă — dreapta sus (vbox/hbox pentru poziționare corectă)
    frame:
        xalign 1.0
        yalign 0.0
        xoffset -20
        yoffset 20
        xpadding 5
        ypadding 5
        background Solid("#000000CC")

        vbox:
            spacing 0
            for r in range(GRID_ROWS):
                hbox:
                    spacing 0
                    for c in range(GRID_COLS):
                        $ _mc = "#FFFFFF" if (r == player_grid_row and c == player_grid_col) else MINIMAP_COLORS.get(get_cell_char(r, c), "#1A1A1A")
                        add Solid(_mc, xsize=11, ysize=11)

    # D-pad — centru jos (vbox direct la nivel de ecran, yalign 1.0 ancorează jos)
    vbox:
        xalign 0.5
        yalign 1.0
        yoffset -25
        spacing 4

        hbox:
            xalign 0.5
            textbutton "▲":
                action Return("up")
                sensitive is_grid_passable(player_grid_row - 1, player_grid_col)
                style "dpad_btn"

        hbox:
            spacing 4
            xalign 0.5
            textbutton "←":
                action Return("left")
                sensitive is_grid_passable(player_grid_row, player_grid_col - 1)
                style "dpad_btn"
            textbutton "●":
                action Return("interact")
                style "dpad_center_btn"
            textbutton "→":
                action Return("right")
                sensitive is_grid_passable(player_grid_row, player_grid_col + 1)
                style "dpad_btn"

        hbox:
            xalign 0.5
            textbutton "▼":
                action Return("down")
                sensitive is_grid_passable(player_grid_row + 1, player_grid_col)
                style "dpad_btn"

    # Scurtături tastatură
    key "K_UP"       action Return("up")
    key "K_DOWN"     action Return("down")
    key "K_LEFT"     action Return("left")
    key "K_RIGHT"    action Return("right")
    key "K_w"        action Return("up")
    key "K_s"        action Return("down")
    key "K_a"        action Return("left")
    key "K_d"        action Return("right")
    key "K_RETURN"   action Return("interact")
    key "K_KP_ENTER" action Return("interact")
    key "K_SPACE"    action Return("interact")


label grid_map:
    call screen grid_movement
    $ _dir = _return

    if _dir == "interact":
        $ _z = get_zone_at(player_grid_row, player_grid_col)
        if _z and renpy.has_label("zone_actions_" + _z):
            call expression "zone_actions_" + _z
        else:
            "Nu ai ce face acum. Continuă să explorezi."
        jump grid_map

    $ _delta = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}.get(_dir, (0, 0))
    $ _nr = player_grid_row + _delta[0]
    $ _nc = player_grid_col + _delta[1]

    if is_grid_passable(_nr, _nc):
        $ _prev_zone = get_zone_at(player_grid_row, player_grid_col)
        $ player_grid_row = _nr
        $ player_grid_col = _nc
        $ _next_zone = get_zone_at(_nr, _nc)
        if _next_zone and _next_zone != _prev_zone:
            $ player_location = _next_zone
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
