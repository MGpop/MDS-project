# Replici reutilizabile pentru NPC-uri minore sau situații generice

label npc_refuz_info:
    "Omul dă din cap și se uită în altă parte."
    "— Nu știu nimic. Și dacă aș ști, nu ți-aș spune."
    return

label npc_salut_targoviste:
    "Un trecător te privește cu suspiciune. Stranieri nu sunt bine-văzuți în aceste zile."
    return

label tranzitie_drum(origin, dest):
    $ route_key = (origin, dest)
    $ connector = TRAVEL_ROUTES.get(route_key)
    if connector == "drum_targoviste_curtea":
        "Mergi pe ulița principală spre Curtea Domnească. Soldații lui Vlad patrulează la fiecare colț."
    elif connector == "drum_targoviste_han":
        "Cobori spre marginea orașului. Hanul e vizibil de la distanță — singurul loc cu lumini la ora asta."
    elif connector == "camp_han_padure":
        "Câmpul e deschis și rece. În depărtare, marginea pădurii se profilează neagră pe cerul serii."
    elif connector == "drum_padure_tabara":
        "Urmezi un drum ascuns prin pădure. Tabăra otomană e bine camuflată, dar știi semnele."
    else:
        "Mergi în tăcere. Drumul e lung și nesigur."
    return
