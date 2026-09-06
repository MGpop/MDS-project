# ai/combat_adaptation.rpy
# Adaptare de combat — euristică deterministă, FĂRĂ model de limbaj.
# (Cei doi agenți AI cu model local sunt Cronicarul din environment_director.rpy
#  și Dialogul liber din dialogue_agent.rpy.)
# Inamicul NU mai urmează un pattern fix, ci își alege următoarea mișcare în
# funcție de cum se comportă jucătorul în lupta curentă (câte parări face, cât
# damage a încasat, raportul de HP). Logica de decizie este o euristică pură,
# deterministă (fără LLM) — sigură pentru demo live și ușor de testat.

# Contoare de performanță pentru lupta curentă. Resetate la fiecare start_combat.
default combat_adapt_player_parries = 0      # de câte ori a parat jucătorul
default combat_adapt_player_attacks = 0      # câte atacuri a lansat jucătorul
default combat_adapt_player_hits_taken = 0   # de câte ori a fost lovit jucătorul
default combat_adapt_last_tactic = None      # ultima tactică aleasă de agent
default combat_adapt_message = ""            # explicația afișată în HUD

init python:
    import random
    def combat_adaptation_reset():
        global combat_adapt_player_parries, combat_adapt_player_attacks
        global combat_adapt_player_hits_taken, combat_adapt_last_tactic, combat_adapt_message
        combat_adapt_player_parries = 0
        combat_adapt_player_attacks = 0
        combat_adapt_player_hits_taken = 0
        combat_adapt_last_tactic = None
        combat_adapt_message = ""

    def combat_adaptation_note_player_parry():
        global combat_adapt_player_parries
        combat_adapt_player_parries += 1

    def combat_adaptation_note_player_attack():
        global combat_adapt_player_attacks
        combat_adapt_player_attacks += 1

    def combat_adaptation_note_player_hit():
        global combat_adapt_player_hits_taken
        combat_adapt_player_hits_taken += 1

    # --- Nucleul agentului: funcție PURĂ (testabilă, fără globale) -------------
    # Întoarce (move_id, tactic, message). move_id in {"light","heavy","parry"}.
    def combat_decide_enemy_move(enemy_hp_ratio, player_hp_ratio, parries, attacks, hits_taken, fallback_index):
        total_actions = max(1, parries + attacks)
        parry_rate = parries / float(total_actions)

        # 1) Inamic rănit grav -> devine defensiv, ridică garda mai des.
        if enemy_hp_ratio <= 0.3:
            parry_chance = random.random()
            return ("parry" if parry_chance < 0.7 else "light", "defensiv", u"Inamicul e rănit și se retrage în defensivă — ridică garda.")

        # 2) Jucătorul parează mult -> inamicul îl pedepsește cu lovituri grele
        #    (parările lungi te lasă expus după ce se termină fereastra).
        if parries >= 2 and parry_rate >= 0.4:
            return ("heavy", "punish_parry", u"Inamicul a observat că parezi des — trece pe lovituri grele.")

        # 3) Jucătorul e slăbit -> inamicul forțează cu lovituri rapide, în serie.
        if player_hp_ratio <= 0.35:
            return ("light", "press_low_hp", u"Te vede slăbit — presează agresiv cu lovituri rapide.")

        # 4) Jucătorul a încasat mult -> inamicul își păstrează agresivitatea.
        if hits_taken >= 3:
            return ("heavy", "stay_aggressive", u"Simte că domină lupta — continuă să lovească tare.")

        # 5) Altfel: ciclu neutru, ca să nu fie previzibil.
        neutral_cycle = ["light", "parry", "heavy"]
        move = neutral_cycle[fallback_index % len(neutral_cycle)]
        return (move, "neutral", u"Inamicul te studiază, căutând o deschidere.")

    # --- Wrapper folosit de combat_system: citește starea curentă -------------
    def combat_adaptation_next_move():
        global combat_enemy_pattern_index, combat_adapt_last_tactic, combat_adapt_message

        enemy_hp_ratio = combat_enemy_health / float(max(1, combat_enemy_max_health))
        player_hp_ratio = player_health / float(max(1, player_max_health))

        move, tactic, message = combat_decide_enemy_move(
            enemy_hp_ratio,
            player_hp_ratio,
            combat_adapt_player_parries,
            combat_adapt_player_attacks,
            combat_adapt_player_hits_taken,
            combat_enemy_pattern_index,
        )

        combat_enemy_pattern_index += 1

        # Afișăm mesajul doar când tactica se schimbă, ca să nu spamăm HUD-ul.
        if tactic != combat_adapt_last_tactic:
            combat_adapt_message = message
            combat_adapt_last_tactic = tactic

        return move
