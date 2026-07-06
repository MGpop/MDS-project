label start:
    call init_game_state
    $ player_name = renpy.input("Cum te numești?", default="Mara", length=20).strip()
    if player_name == "":
        $ player_name = "Mara"
    jump grid_map