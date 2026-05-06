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

# luptă demo
label enter_han:
    scene bg han with dissolve

    $ han_has_ottoman = renpy.random.randint(1, 100) <= 50

    if han_has_ottoman:

        $ otoman_starts_fight = renpy.random.randint(1, 100) <= 50

        if otoman_starts_fight:
            show otoman_spotted at enemy_alert_pos with dissolve
            "Soldatul otoman te vede și pune mâna pe armă."

            hide otoman_spotted with dissolve
            call start_combat("soldat_otoman", "grid_map")
            return

        else:
            show otoman_default at enemy_idle_pos with dissolve
            "Un soldat otoman stă în han, dar nu pare interesat de tine."

            menu:
                "Ce faci?"
                "Îl ignor":
                    "Îți vezi de treabă."
                    return

                "Îl confrunt":
                    hide otoman_default with dissolve
                    call start_combat("soldat_otoman", "grid_map")
                    return

    "Hanul e liniștit."
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
