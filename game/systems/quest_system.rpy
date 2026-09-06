# systems/quest_system.rpy
# Urmărirea quest-urilor: nume lizibile, helperi de start/finalizare și un
# jurnal vizibil în joc. Logica narativă rămâne în travel_labels/quests; aici
# sunt doar utilitarele și UI-ul.

init python:
    # Nume + descrieri scurte pentru afișare în jurnal.
    QUEST_INFO = {
        "q01_investigatie": {
            "name": u"Investighează Hanul",
            "desc": u"Ordinul te-a trimis să cauți dovezi despre o conspirație împotriva lui Vlad.",
        },
        "q02_tradarea_boierilor": {
            "name": u"Trădarea boierilor",
            "desc": u"Un grup de boieri pregătește o alianță secretă cu otomanii.",
        },
        "q03_padurea_tepelor": {
            "name": u"Pădurea Țepelor",
            "desc": u"Vezi cu ochii tăi prețul metodelor lui Vlad.",
        },
        "q04_ordinul_se_rupe": {
            "name": u"Ordinul se rupe",
            "desc": u"Ordinul Dragonului se împarte în două facțiuni rivale.",
        },
        "q05_alegerea_finala": {
            "name": u"Alegerea finală",
            "desc": u"Loialitățile tale decid soarta Țării Românești.",
        },
    }

    def quest_name(quest_id):
        return QUEST_INFO.get(quest_id, {}).get("name", quest_id)

    def quest_desc(quest_id):
        return QUEST_INFO.get(quest_id, {}).get("desc", "")

    def is_quest_active(quest_id):
        return quest_id in active_quests

    def is_quest_done(quest_id):
        return quest_id in completed_quests

    def start_quest(quest_id):
        if quest_id not in active_quests and quest_id not in completed_quests:
            active_quests.append(quest_id)

    def complete_quest(quest_id, give_reward=True):
        if quest_id in active_quests:
            active_quests.remove(quest_id)
        if quest_id not in completed_quests:
            completed_quests.append(quest_id)
        if give_reward:
            give_quest_reward(quest_id)


screen quest_journal():
    modal True
    zorder 250
    add Solid("#000000DD")

    frame:
        align (0.5, 0.5)
        xsize 900
        ysize 620
        background Solid("#150D06EE")
        padding (30, 26)

        vbox:
            spacing 16

            text "Jurnal de misiuni" style "grid_zone_title" size 36

            text "În desfășurare:" size 24 color "#cca35a"
            if active_quests:
                for q in active_quests:
                    vbox:
                        spacing 2
                        text "• [quest_name(q)]" size 22 color "#e8d5a3"
                        text "   [quest_desc(q)]" size 17 color "#9a8260"
            else:
                text "   (nicio misiune activă)" size 18 color "#7a6a50"

            null height 8

            text "Finalizate:" size 24 color "#7faf7f"
            if completed_quests:
                for q in completed_quests:
                    text "» [quest_name(q)]" size 20 color "#9ac79a"
            else:
                text "   (încă niciuna)" size 18 color "#7a6a50"

            null height 10
            hbox:
                xalign 1.0
                spacing 16
                if "q01_investigatie" in completed_quests:
                    textbutton "Vezi finalul (demo)" action Return("ending")
                textbutton "Închide (J)" action Return()

    key "K_j" action Return()
    key "K_ESCAPE" action Return()
