# Entry point-uri pentru fiecare locație.
# Apelate de grid_map când jucătorul intră într-o nouă zonă.
# Returnează după narațiune — grid_map continuă.

label enter_targoviste:
    $ player_location = "targoviste"
    scene expression location_background_displayable("targoviste") with dissolve
    "Târgoviște. Zgomotul orașului te înconjoară — roți pe pietre, strigăte de negustori, și priviri care nu te privesc direct."
    return

label enter_curtea_domneasca:
    $ player_location = "curtea_domneasca"
    scene expression location_background_displayable("curtea_domneasca") with dissolve
    "Porțile Curții Domnești se deschid în fața ta. Soldații te urmăresc cu privirea. Fiecare pas e numărat."
    return

label enter_han:
    $ player_location = "han"
    scene expression location_background_displayable("han") with dissolve
    "Hanul Corbului Negru. Fum gros, voci joase. Cineva dintr-un colț întunecat nu vrea să fie văzut."
    return

label enter_padure:
    $ player_location = "padure"
    scene expression location_background_displayable("padure") with dissolve
    "Pădurea Vlăsiei te înghite. Lumina dispare imediat ce intri sub coroanele copacilor. Ceva scârțâie în ramuri."
    return

label enter_tabara_otomana:
    $ player_location = "tabara_otomana"
    scene expression location_background_displayable("tabara_otomana") with dissolve
    "Dai semnalul convenit. Un soldat otoman apare din umbră și te conduce înăuntru, fără un cuvânt."
    return
