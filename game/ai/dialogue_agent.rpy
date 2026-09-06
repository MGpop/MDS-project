# ai/dialogue_agent.rpy
# AGENT AI (2 din 2) — Dialogul liber cu NPC-urile.
#
# Jucătorul scrie ce vrea, iar NPC-ul răspunde în caracter, cu starea jocului în
# context, printr-un model de limbaj mic rulat local. Modelul întoarce JSON:
#
#     {"replica": "...", "efect": "...", "motiv": "..."}
#
# Efectul e ales dintr-o listă albă și e aplicat de joc, nu de model — deci
# dialogul liber chiar schimbă starea (loialități, indicii, chiar și o luptă),
# dar nu poate rupe progresul poveștii.
#
# Limite, ca discuția să nu devină o vacă de muls:
#   - cel mult AI_DIALOG_MAX_EXCHANGES schimburi pe conversație;
#   - cel mult o modificare de loialitate pe conversație;
#   - un singur indiciu per NPC, pentru toată partida.

default ai_dialog_hints_used = []


init python:
    def ai_dialog_state(npc_id):
        persona = npc_persona(npc_id) or {}
        camp = FACTIUNE_LOIALITATE.get(persona.get("factiune"))

        fapte = []
        if has_secret_letter:
            fapte.append(u"a găsit o scrisoare secretă cu sigiliu boieresc")
        if vlad_knows_player:
            fapte.append(u"Vlad îl cunoaște personal")
        if ottoman_contact_made:
            fapte.append(u"a luat legătura cu otomanii")
        if knows_order_truth:
            fapte.append(u"știe că Ordinul e dezbinat")

        return {
            "player_name": player_name,
            "capitol": current_chapter,
            "locatie": location_name(player_location),
            "loialitati": ai_loyalty_snapshot(),
            "obiecte": ai_inventory_names(),
            "relatie": getattr(store, camp) if camp else None,
            "fapte": fapte,
        }

    def ai_dialog_allowed_effects(npc_id, loialitate_folosita, indiciu_folosit):
        permise = [ai_schemas.EFECT_NIMIC]

        if not loialitate_folosita:
            permise.append(ai_schemas.EFECT_INCREDERE_PLUS)
            permise.append(ai_schemas.EFECT_INCREDERE_MINUS)

        persona = npc_persona(npc_id) or {}
        if persona.get("indiciu") and not indiciu_folosit and npc_id not in ai_dialog_hints_used:
            permise.append(ai_schemas.EFECT_INDICIU)

        # Ostilitatea are voie doar dacă există un inamic potrivit și lupta e corectă.
        if persona.get("enemy_id") and ai_player_can_fight():
            permise.append(ai_schemas.EFECT_OSTIL)

        return permise

    def ai_dialog_apply_effect(npc_id, efect):
        """Aplică efectul ales. Întoarce (text_narațiune, pornește_luptă)."""
        global ai_dialog_hints_used

        persona = npc_persona(npc_id) or {}
        camp = FACTIUNE_LOIALITATE.get(persona.get("factiune"))

        if efect == ai_schemas.EFECT_INCREDERE_PLUS and camp:
            setattr(store, camp, getattr(store, camp) + 1)
            return (u"L-ai câștigat puțin. (%s +1)" % persona.get("nume", npc_id), False)

        if efect == ai_schemas.EFECT_INCREDERE_MINUS and camp:
            setattr(store, camp, getattr(store, camp) - 1)
            return (u"Ai spus ce nu trebuia. (%s −1)" % persona.get("nume", npc_id), False)

        if efect == ai_schemas.EFECT_INDICIU:
            if npc_id not in ai_dialog_hints_used:
                ai_dialog_hints_used = list(ai_dialog_hints_used) + [npc_id]
            return (None, False)

        if efect == ai_schemas.EFECT_OSTIL:
            return (u"Ai împins prea departe.", True)

        return (None, False)

    def ai_dialog_say(npc_id, text):
        """Pune replica în gura personajului potrivit."""
        vorbitor = NPC_CHARACTERS.get(npc_id)
        if vorbitor is not None:
            renpy.say(vorbitor, text)
        else:
            renpy.say(None, text)


label npc_free_talk(npc_id):
    python:
        _talk_npc = npc_id
        _talk_persona = npc_persona(npc_id) or {}
        _talk_nume = _talk_persona.get("nume", u"Necunoscut")
        _talk_istoric = []
        _talk_exchanges = 0
        _talk_loyalty_used = False
        _talk_hint_used = False

    if not _talk_persona:
        return

    narrator "Poți să-i spui orice îți trece prin cap. Lasă câmpul gol ca să te retragi."
    jump npc_free_talk_loop


label npc_free_talk_loop:
    if _talk_exchanges >= AI_DIALOG_MAX_EXCHANGES:
        narrator "[_talk_nume] îți întoarce spatele. Discuția s-a terminat."
        return

    $ _talk_input = renpy.input(
        u"Ce îi spui lui %s?" % _talk_nume,
        length=200,
    ).strip()

    if _talk_input == "":
        narrator "Te retragi fără să mai spui nimic."
        return

    python:
        _talk_box = ai_runtime.run_async(
            ai_runtime.dialogue().respond,
            _talk_persona,
            ai_dialog_state(_talk_npc),
            _talk_input,
            list(_talk_istoric),
            ai_dialog_allowed_effects(_talk_npc, _talk_loyalty_used, _talk_hint_used),
        )

    call ai_wait_screen(_talk_box, AI_DIALOG_WAIT, _talk_nume + u" se gândește…")

    python:
        _talk_res = _talk_box.get("value")
        if _talk_res is None:
            from dragon_ai import fallbacks as _talk_fb
            _talk_res = {
                "replica": _talk_fb.dialog_reply(_talk_persona.get("factiune"), _talk_exchanges),
                "efect": ai_schemas.EFECT_NIMIC,
                "motiv": u"Replică de rezervă.",
                "sursa": u"fallback",
                "motiv_tehnic": _talk_box.get("error") or u"modelul nu a răspuns în timp util",
                "latenta": AI_DIALOG_WAIT,
                "raw": u"",
            }

        ai_note_call(u"Dialog liber", _talk_res)

        _talk_istoric.append(("player", _talk_input))
        _talk_istoric.append(("npc", _talk_res["replica"]))
        _talk_exchanges += 1

        _talk_efect = _talk_res.get("efect", ai_schemas.EFECT_NIMIC)
        if _talk_efect in (ai_schemas.EFECT_INCREDERE_PLUS, ai_schemas.EFECT_INCREDERE_MINUS):
            _talk_loyalty_used = True
        if _talk_efect == ai_schemas.EFECT_INDICIU:
            _talk_hint_used = True

        _talk_nota, _talk_fight = ai_dialog_apply_effect(_talk_npc, _talk_efect)

    $ ai_dialog_say(_talk_npc, _talk_res["replica"])

    if _talk_efect == ai_schemas.EFECT_INDICIU and _talk_persona.get("indiciu"):
        $ ai_dialog_say(_talk_npc, _talk_persona["indiciu"])
        narrator "{i}Ai aflat ceva ce nu se spune oricui.{/i}"

    if _talk_nota:
        narrator "{i}[_talk_nota]{/i}"

    if _talk_fight:
        $ _talk_enemy = _talk_persona.get("enemy_id", "haiduc")
        call start_combat(_talk_enemy, "grid_map")
        return

    menu:
        "Continui discuția?"
        "Mai spun ceva":
            jump npc_free_talk_loop
        "Îmi iau rămas bun":
            narrator "Te retragi."
            return
