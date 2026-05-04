label start:

    $ player_name = renpy.input("Cum te numești?")
    $ player_name = player_name.strip()

    if player_name == "":
        $ player_name = "Mara"

    jump main_quest_intro




label demo_ending:

    scene bg room

    if loyalty_vlad > loyalty_boyars and loyalty_vlad > loyalty_ottomans:
        n "Pentru moment, alegerea ta îl întărește pe Vlad."
        n "Dar Țara Românească va plăti prețul fricii."

    elif loyalty_boyars > loyalty_vlad and loyalty_boyars > loyalty_ottomans:
        n "Ai ales boierii."
        n "Poate ai salvat câteva vieți. Sau poate ai deschis poarta trădării."

    elif loyalty_ottomans > loyalty_vlad and loyalty_ottomans > loyalty_boyars:
        n "Ai ales umbra Imperiului Otoman."
        n "Pacea promisă miroase deja a lanțuri."

    else:
        n "Nu ai ales încă o tabără."
        n "Iar asta te face periculos pentru toate."

    if player_wounded:
        n "Ai supraviețuit, dar rana îți amintește că fiecare alegere are un cost."

    n "Sfârșitul demo-ului."

    return