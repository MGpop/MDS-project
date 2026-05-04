label start:
    call init_game_state

    scene black with fade

    "Anul 1456. Țara Românească."
    "Vlad Țepeș s-a întors la tron, hotărât să curețe țara de trădători și să reziste otomanilor."
    "Ordinul Dragonului te-a trimis în secret la Târgoviște — misiunea: investighezi zvonuri despre o conspirație împotriva lui Vlad."
    "Dar nimeni nu ți-a spus tot adevărul."

    $ player_name = renpy.input("Cum te numești, agent al Ordinului?", default="Mara", length=20).strip()
    if player_name == "":
        $ player_name = "Mara"

    "[player_name]. Acesta este numele tău. Poate ultimul lucru sigur din această misiune."

    jump chapter_1_start
