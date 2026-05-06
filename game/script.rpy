init python:
    def opening_background(filename):
        return Transform(
            "images/backgrounds/" + filename,
            xysize=(config.screen_width, config.screen_height),
            fit="cover",
            xalign=0.5,
            yalign=0.5,
        )

label start:
    call init_game_state
    # jump test_branch2

    scene expression opening_background("opening_targoviste.png") with fade

    "Anul 1456. Țara Românească."
    "Vlad Țepeș s-a întors la tron, hotărât să curețe țara de trădători și să reziste otomanilor."

    scene expression opening_background("opening_ordinul.png") with dissolve

    "Ordinul Dragonului te-a trimis în secret la Târgoviște — misiunea: investighezi zvonuri despre o conspirație împotriva lui Vlad."

    scene expression opening_background("opening_black_dragon_symbol.png") with dissolve

    "Dar nimeni nu ți-a spus tot adevărul."

    scene expression location_background_displayable("targoviste") with fade

    $ player_name = renpy.input("Cum te numești, agent al Ordinului?", default="Mara", length=20).strip()
    if player_name == "":
        $ player_name = "Mara"

    "[player_name]. Acesta este numele tău. Poate ultimul lucru sigur din această misiune."

    jump grid_map
    #jump chapter_1_start
