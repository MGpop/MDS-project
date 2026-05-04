label combat_demo:

    $ quest_stage = 2

    soldat "Stai pe loc. Dă-mi scrisoarea."

    menu:
        "Ataci direct":
            if loyalty_vlad >= 1:
                n "Ai ezitare puțină, dar lovești primul. Soldatul cade."
                $ player_wounded = False
            else:
                n "Ataci prea repede. Soldatul te rănește înainte să scapi."
                $ player_wounded = True

        "Încerci să-l păcălești":
            n "Îi spui că scrisoarea este deja la curte. Soldatul ezită."
            $ player_wounded = False

        "Îi dai scrisoarea":
            n "Soldatul ia scrisoarea și dispare în întuneric."
            $ has_secret_letter = False
            $ loyalty_ottomans += 1

    jump demo_ending