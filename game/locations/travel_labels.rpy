# Entry point-uri pentru fiecare locație.
# Apelate de grid_map când jucătorul intră într-o nouă zonă.
# Returnează după narațiune — grid_map continuă.

default han_otoman_defeated = False

label zone_actions_zsat:
    scene expression grid_background_displayable(player_grid_row, player_grid_col) with dissolve

    if player_grid_row != 26 or player_grid_col != 5:
        "Nu ai ce face aici acum."
        return

    if not talked_to_old_man:
        "Bătrânul satului stă lângă poartă, sprijinit în toiag."

        batran "Ai drum spre Târgoviște, nu-i așa?"
        batran "Nu vei intra acolo fără document de trecere."
        batran "Mergi pe drum până la fântână, apoi ține dreapta spre han."
        batran "La Hanul Corbului Negru găsești oameni care pot deschide uși. Sau le pot închide pentru totdeauna."

        $ talked_to_old_man = True
        $ road_to_wolf_unlocked = True

        $ unlock_cells([
            (26, 6),
            (25, 7),
            (24, 7),
            (23, 7),
            (22, 7),
        ])

        narrator "Drumul spre han a fost deblocat."

    else:
        "Bătrânul privește spre drum."
        batran "Ține minte: până la fântână, apoi la dreapta. Hanul nu-i departe."

    return





label enter_zhan:
    $ player_location = "zhan"
    scene expression grid_background_displayable(player_grid_row, player_grid_col) with dissolve
    "Lumea te așteaptă. Povestea ta începe acum."
    return

label zone_actions_zhan:
    scene expression grid_background_displayable(player_grid_row, player_grid_col) with dissolve

    if player_grid_row != 14 or player_grid_col != 9:
        "Hanul vuiește încet: pași, șoapte, lemn vechi și pahare trântite pe mese."
        "Nu pare să fie nimic important aici acum."
        return

    if boier_defeated:
        "Locul boierului este gol."
        "Pe masă au rămas doar urme de vin și o tăcere stânjenitoare."
        return

    if boier_chest_returned:
        boier "Ți-am dat pecetea. Nu mai avem nimic de împărțit."
        return

    if got_city_seal:
        if city_seal_method == "stolen_from_boier":
            "Boierul nu mai are ce să-ți dea."
        else:
            boier "Pecetea e la tine. Folosește-o cu grijă."
        return

    if not met_boier_han:
        "Un boier stă singur la o masă, cu mantia strânsă în jurul umerilor."
        "Are în față o cupă neatinsă și privește spre ușă de parcă așteaptă vești proaste."

        boier "Tu. Pari om de drum."
        boier "Niște haiduci mi-au furat un cufăr. Nu era al lor. Nu era nici treaba lor ce se află în el."
        boier "Adu-mi-l înapoi și îți dau o pecete de trecere."
        boier "Cu ea, porțile Târgoviștei se deschid mai ușor."

        $ met_boier_han = True
        $ boier_chest_quest_started = True
        $ forest_unlocked_by_boier = True
        $ unlock_zone("zpadure", unlock_fast=False)

        narrator "Pădurea Vlăsiei a fost deblocată."
        return

    if has_item("cufar_boier"):
        menu:
            "Ce faci cu cufărul?"
            "Îi dai cufărul boierului":
                $ remove_item("cufar_boier")
                $ add_item("pecete_targoviste")
                $ got_city_seal = True
                $ boier_chest_returned = True
                $ city_seal_method = "boier_reward"

                boier "Bine. Ai făcut ce ai promis."
                boier "Ia pecetea. Arat-o la poarta Târgoviștei și nu pomeni numele meu mai mult decât trebuie."

                narrator "Ai primit Pecetea de trecere."

            "Îl păstrezi deocamdată":
                boier "Nu mă face să regret că am vorbit cu tine."

        return

    if boier_fight_done:
        boier "Nu-ți mai încerca norocul cu mine."
        return

    menu:
        "Boierul te privește nerăbdător."

        "Îi spui că vei aduce cufărul":
            boier "Atunci nu pierde vremea aici. Haiducii nu așteaptă să fie găsiți."

        "Îl ataci și încerci să-i iei pecetea":
            $ boier_fight_done = True
            $ boier_attacked = True
            $ combat_last_result = None

            boier "Așa deci."
            boier "Să vedem dacă ai și braț pentru obrăznicia asta."

            call start_combat("boier_han", "grid_map")

        "Îl lași în pace":
            "Boierul își întoarce privirea spre cupa neatinsă."

    return




label enter_zpadure:
    $ player_location = "zpadure"
    scene expression grid_background_displayable(player_grid_row, player_grid_col) with dissolve
    "Pădurea Vlăsiei te înghite. Lumina dispare imediat ce intri sub coroanele copacilor. Ceva scârțâie în ramuri."
    return

label zone_actions_zpadure:
    scene expression grid_background_displayable(player_grid_row, player_grid_col) with dissolve

    if player_grid_row != 3 or player_grid_col != 3:
        "Pădurea foșnește în jurul tău."
        "Nu pare să fie nimeni aici."
        return

    if not boier_chest_quest_started:
        "Un bărbat cu haine ponosite stă rezemat de un copac."
        "Te măsoară din priviri, dar nu pare să aibă motiv să-ți vorbească."
        return

    if boier_chest_returned:
        "Locul haiducului e gol."
        "Povestea cufărului s-a încheiat deja."
        return

    if has_item("cufar_boier"):
        "Cufărul boierului este deja la tine."
        "Nu mai ai ce să cauți aici acum."
        return

    if haiduc_cufar_defeated:
        "Haiducul zace învins, iar cufărul nu mai este aici."
        return

    if not met_haiduc_cufar:
        "Un haiduc iese dintre copaci, fără grabă."
        "Nu pare surprins că l-ai găsit."

        haiduc "Te-a trimis boierul, nu-i așa?"
        haiduc "Se vede pe fața ta. Numai oamenii trimiși de boieri vin în pădure cu atâta dreptate în glas."

        $ met_haiduc_cufar = True

    menu:
        "Ce faci?"

        "Îl acuzi că a furat cufărul boierului":
            $ haiduc_cufar_accused = True

            player "Ai furat cufărul boierului."
            player "Îl vreau înapoi."

            haiduc "Furat?"
            haiduc "Așa ți-a spus el?"
            haiduc "Bine. Dacă ai venit să judeci, judecă-mă cu fierul în mână."

            menu:
                "Cum răspunzi?"

                "Îl confrunți":
                    $ haiduc_cufar_fight_done = True
                    $ combat_last_result = None

                    haiduc "Atunci vino."

                    call start_combat("haiduc_cufar", "grid_map")

                "Îl lași în pace momentan":
                    haiduc "Înțelept. Sau doar nehotărât."
                    haiduc "Când te hotărăști, mă găsești aici."

        "Îl lași în pace momentan":
            haiduc "Pădurea e destul de mare pentru amândoi, câtă vreme nu calci unde nu trebuie."

    return





label enter_ztargoviste:
    $ player_location = "ztargoviste"
    scene expression grid_background_displayable(player_grid_row, player_grid_col) with dissolve
    "Târgoviște. Zgomotul orașului te înconjoară — roți pe pietre, strigăte de negustori, și priviri care nu te privesc direct."
    return





label enter_zcurte:
    $ player_location = "zcurte"
    scene expression grid_background_displayable(player_grid_row, player_grid_col) with dissolve
    "Porțile Curții Domnești se deschid în fața ta. Soldații te urmăresc cu privirea. Fiecare pas e numărat."
    return





label enter_zotomani:
    $ player_location = "zotomani"
    scene expression grid_background_displayable(player_grid_row, player_grid_col) with dissolve
    "Dai semnalul convenit. Un soldat otoman apare din umbră și te conduce înăuntru, fără un cuvânt."
    return
