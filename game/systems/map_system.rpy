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

    # Minimapă — dreapta sus. Zonele încă nedeblocate apar întunecate, ca să se
    # vadă că există, dar nu sunt accesibile încă.
    frame:
        xalign 1.0
        yalign 0.0
        xoffset -20
        yoffset 20
        xpadding 12
        ypadding 10
        background Solid("#000000CC")

        vbox:
            spacing 8

            text "Harta lumii" style "grid_zone_title" size 20

            vbox:
                spacing 1
                for r in range(GRID_ROWS):
                    hbox:
                        spacing 1
                        for c in range(GRID_COLS):
                            add Solid(minimap_cell_color(r, c, player_grid_row, player_grid_col), xsize=20, ysize=20)

            vbox:
                spacing 4
                for _legend_zone in MINIMAP_LEGEND:
                    hbox:
                        spacing 8
                        add Solid(minimap_legend_color(_legend_zone), xsize=14, ysize=14) yalign 0.5
                        text minimap_legend_label(_legend_zone) style "minimap_legend_text" yalign 0.5

    # Panou loialități — stânga jos. Face vizibil efectul alegerilor și al agenților.
    frame:
        xpos 20
        yalign 1.0
        yoffset -20
        xsize 300
        background Solid("#000000BB")
        xpadding 14
        ypadding 12

        vbox:
            spacing 4
            text "Loialități" style "grid_zone_title" size 20
            text "Vlad: [loyalty_vlad]" style "grid_loyalty_text"
            text "Boieri: [loyalty_boyars]" style "grid_loyalty_text"
            text "Otomani: [loyalty_ottomans]" style "grid_loyalty_text"
            text "Încredere Ordin: [dragon_order_trust]" style "grid_loyalty_text"
            text "Suspiciune Ordin: [order_suspicion]" style "grid_loyalty_text"

    # Bară de acțiuni — dreapta jos
    vbox:
        xalign 1.0
        yalign 1.0
        xoffset -20
        yoffset -20
        spacing 6

        textbutton "Inventar (I)" action Return("inventory") style "action_btn"
        textbutton "Jurnal (J)" action Return("journal") style "action_btn"
        textbutton "Fast-travel (T)" action Return("fasttravel") style "action_btn"
        textbutton "Agent AI (F9)" action ToggleVariable("ai_debug_visible") style "action_btn"

    key "K_i" action Return("inventory")
    key "K_j" action Return("journal")
    key "K_t" action Return("fasttravel")
    key "K_F9" action ToggleVariable("ai_debug_visible")

    # Ce a decis ultimul agent AI și de ce — vizibil doar când e cerut.
    if ai_debug_visible:
        use ai_debug_panel

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
                sensitive not is_grid_wall(player_grid_row - 1, player_grid_col)
                style "dpad_btn"

        hbox:
            spacing 4
            xalign 0.5
            textbutton "←":
                action Return("left")
                sensitive not is_grid_wall(player_grid_row, player_grid_col - 1)
                style "dpad_btn"
            textbutton "●":
                action Return("interact")
                style "dpad_center_btn"
            textbutton "→":
                action Return("right")
                sensitive not is_grid_wall(player_grid_row, player_grid_col + 1)
                style "dpad_btn"

        hbox:
            xalign 0.5
            textbutton "▼":
                action Return("down")
                sensitive not is_grid_wall(player_grid_row + 1, player_grid_col)
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
        $ _has_zone_action = bool(_z) and renpy.has_label("zone_actions_" + _z)

        if _has_zone_action:
            call expression "zone_actions_" + _z

        if npc_talkable_here():
            call npc_zone_menu
        elif not _has_zone_action:
            "Nu ai ce face acum. Continuă să explorezi."

        jump grid_map

    if _dir == "inventory":
        call screen inventory_screen
        jump grid_map

    if _dir == "journal":
        call screen quest_journal
        if _return == "ending":
            jump demo_ending
        jump grid_map

    if _dir == "fasttravel":
        call fast_travel_menu
        jump grid_map

    $ _delta = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}.get(_dir)
    if _delta is None:
        jump grid_map

    $ _nr = player_grid_row + _delta[0]
    $ _nc = player_grid_col + _delta[1]

    # Zidurile nu spun nimic — butonul lor e deja insensibil.
    if is_grid_wall(_nr, _nc):
        jump grid_map

    # Zonă reală, dar încă nedeblocată de poveste: explicăm, nu lăsăm butonul mort.
    $ _block_reason = grid_block_reason(_nr, _nc)
    if _block_reason:
        $ renpy.notify(_block_reason)
        jump grid_map

    $ player_grid_row = _nr
    $ player_grid_col = _nc

    # player_location urmărește și drumurile, nu doar zonele, ca fast-travel-ul
    # și agenții să știe mereu unde ești.
    $ _area = get_map_area_at(_nr, _nc)
    if _area:
        $ player_location = _area

    # Intrarea într-o zonă se declanșează o singură dată, la schimbarea zonei.
    # Fără garda asta, un pas pe drum și înapoi rula din nou enter_<zonă> — iar în
    # Han asta însemna o nouă aruncare de zar pentru soldatul otoman, la nesfârșit.
    $ _next_zone = get_zone_at(_nr, _nc)
    if _next_zone and _next_zone != last_entered_zone:
        $ last_entered_zone = _next_zone
        call expression "enter_" + _next_zone
        call environment_director_on_enter(_next_zone)

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

style grid_loyalty_text:
    font "fonts/Cormorant_Upright/CormorantUpright-Regular.ttf"
    size 18
    color "#D4C0A0"

style action_btn:
    xsize 220
    background Solid("#2A1A0A")
    hover_background Solid("#5A3A1A")
    xpadding 12
    ypadding 8

style action_btn_text:
    font "fonts/Cinzel/static/Cinzel-Regular.ttf"
    size 18
    color "#D4AF37"
    hover_color "#FFD700"
    xalign 0.5

style minimap_legend_text:
    font "fonts/Cormorant_Upright/CormorantUpright-Regular.ttf"
    size 16
    color "#C0A080"
