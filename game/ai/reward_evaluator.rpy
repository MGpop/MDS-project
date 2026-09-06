# ai/reward_evaluator.rpy
# Evaluator de recompense — euristică deterministă, FĂRĂ model de limbaj.
# (Cei doi agenți AI cu model local sunt Cronicarul din environment_director.rpy
#  și Dialogul liber din dialogue_agent.rpy.)
# După fiecare luptă sau quest, agentul cântărește dificultatea, performanța
# jucătorului (HP rămas, durata luptei) și alegerile/loialitățile, apoi decide
# cât XP, câte monede și ce bonusuri primește. Euristică pură, deterministă.

default last_reward_message = ""   # ultimul verdict, afișat în joc

init python:
    # Cât XP e nevoie pentru fiecare nivel (creștere simplă).
    XP_PER_LEVEL = 50

    def reward_apply_xp(amount):
        # Adaugă XP și ridică nivelul când se atinge pragul. Întoarce nr. de niveluri câștigate.
        global player_xp, player_level
        player_xp += amount
        levels_gained = 0
        while player_xp >= XP_PER_LEVEL:
            player_xp -= XP_PER_LEVEL
            player_level += 1
            levels_gained += 1
        return levels_gained

    # --- Nucleul agentului: funcție PURĂ (testabilă) --------------------------
    # Întoarce dict: {xp, gold, grade, perf, notes}.
    def reward_evaluate_combat(difficulty, player_hp_ratio, combat_time):
        base_xp = 8 + difficulty * 6
        base_gold = 5 + difficulty * 5

        perf = 1.0
        notes = []

        if player_hp_ratio >= 0.7:
            perf += 0.4
            notes.append(u"HP ridicat")
        elif player_hp_ratio <= 0.3:
            perf -= 0.25
            notes.append(u"abia ai supraviețuit")

        if combat_time <= 12.0:
            perf += 0.3
            notes.append(u"victorie rapidă")
        elif combat_time >= 30.0:
            perf -= 0.15
            notes.append(u"luptă lungă")

        perf = max(0.5, perf)

        if perf >= 1.5:
            grade = u"excelentă"
        elif perf >= 1.0:
            grade = u"bună"
        else:
            grade = u"slabă"

        return {
            "xp": int(round(base_xp * perf)),
            "gold": int(round(base_gold * perf)),
            "grade": grade,
            "perf": round(perf, 2),
            "notes": notes,
        }

    # --- Wrapper: evaluează lupta curentă, aplică efectele, setează mesajul ----
    def reward_grant_combat():
        global last_reward_message

        player_hp_ratio = player_health / float(max(1, player_max_health))
        result = reward_evaluate_combat(
            combat_enemy_difficulty,
            player_hp_ratio,
            combat_time,
        )

        add_item("monede", result["gold"])
        levels = reward_apply_xp(result["xp"])

        notes_txt = (u" (" + u", ".join(result["notes"]) + u")") if result["notes"] else u""
        msg = u"Evaluator recompense — performanță %s%s -> +%d XP, +%d monede." % (
            result["grade"], notes_txt, result["xp"], result["gold"]
        )
        if levels > 0:
            msg += u" Ai avansat la nivelul %d!" % player_level

        last_reward_message = msg
        return result

    # --- Recompensă de quest, scalată după capitol -----------------------------
    def reward_grant_quest(quest_id):
        global last_reward_message

        reward = QUEST_REWARDS.get(quest_id)
        if reward is None:
            return None

        for item_id in reward.get("items", []):
            add_item(item_id)

        xp = reward.get("xp", 0)
        levels = reward_apply_xp(xp)

        item_names = [ITEMS.get(i, {}).get("name", i) for i in reward.get("items", [])]
        items_txt = (u" Iteme: " + u", ".join(item_names) + u".") if item_names else u""
        msg = u"Evaluator recompense (quest) — +%d XP.%s" % (xp, items_txt)
        if levels > 0:
            msg += u" Nivel nou: %d!" % player_level

        last_reward_message = msg
        return reward
