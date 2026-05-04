# Entry point-uri pentru fiecare locație.
# Apelate de map_system după tranziția pe drum/câmp.

label enter_targoviste:
    $ player_location = "targoviste"
    "Ești în Târgoviște. Zgomotul orașului te înconjoară."
    jump map_menu

label enter_curtea_domneasca:
    $ player_location = "curtea_domneasca"
    "Porțile Curții Domnești se deschid în fața ta. Soldații te urmăresc cu privirea."
    jump map_menu

label enter_han:
    $ player_location = "han"
    "Hanul Corbului Negru. Fum, voce joasă, cineva care nu vrea să fie văzut în colț."
    jump map_menu

label enter_padure:
    $ player_location = "padure"
    "Pădurea te înghite. Lumina dispare imediat ce intri sub coroanele copacilor."
    jump map_menu

label enter_tabara_otomana:
    $ player_location = "tabara_otomana"
    "Dai semnalul convenit. Un soldat otoman apare din umbră și te conduce înăuntru."
    jump map_menu

# Intrări în locații de legătură — scurte, fără map_menu
label enter_drum_targoviste_curtea:
    $ player_location = "drum_targoviste_curtea"
    call tranzitie_drum("targoviste", "curtea_domneasca")
    return

label enter_drum_targoviste_han:
    $ player_location = "drum_targoviste_han"
    call tranzitie_drum("targoviste", "han")
    return

label enter_camp_han_padure:
    $ player_location = "camp_han_padure"
    call tranzitie_drum("han", "padure")
    return

label enter_drum_padure_tabara:
    $ player_location = "drum_padure_tabara"
    call tranzitie_drum("padure", "tabara_otomana")
    return
