# ai/environment_director.rpy
# AGENT AI (1 din 2) — «Cronicarul», regizorul de evenimente.
#
# La fiecare intrare într-o zonă, agentul primește starea comprimată a jocului
# (zonă, capitol, loialități, suspiciunea Ordinului, ce are în desagă) și decide
# ce se întâmplă: alege un eveniment dintr-o listă albă și scrie narațiunea pe loc,
# cu un model de limbaj mic rulat local.
#
# Modelul alege și scrie; consecința mecanică e legată determinist de id-ul
# evenimentului (vezi dragon_ai/schemas.py). Așa, un model care halucinează poate
# cel mult alege prost evenimentul — nu poate strica starea jocului.
#
# Dacă modelul e oprit, lent sau întoarce gunoi, se folosește euristica scrisă de
# mână din dragon_ai/fallbacks.py și jocul merge identic mai departe.

init -5 python:
    from dragon_ai import fallbacks as dragon_ai_fallbacks


init python:
    def ai_chronicler_state(zone):
        """Starea jocului, comprimată pentru prompt. Rulează pe firul principal."""
        return {
            "zona": zone,
            "zona_nume": location_name(zone),
            "capitol": current_chapter,
            "loialitati": ai_loyalty_snapshot(),
            "suspiciune": order_suspicion,
            "obiecte": ai_inventory_names(),
        }

    def ai_fallback_event(zone):
        """Evenimentul determinist, folosit când modelul nu răspunde la timp."""
        return dragon_ai_fallbacks.chronicler_event(
            zone, loyalty_vlad, loyalty_boyars, loyalty_ottomans,
            order_suspicion, current_chapter, renpy.random.randint(0, 99),
        )

    def ai_chronicler_ambush_enemy(zone):
        """Cine te atacă într-o ambuscadă, potrivit cu locul."""
        candidati = [
            enemy_id for enemy_id, date in ENEMIES.items()
            if zone in date.get("locations", [])
        ]
        if not candidati:
            return "haiduc"
        return candidati[renpy.random.randint(0, len(candidati) - 1)]

    def ai_chronicler_apply(rezultat):
        """Aplică efectul legat de evenimentul ales. Întoarce True dacă urmează o luptă."""
        global order_suspicion, dragon_order_trust

        efect = ai_schemas.efect_eveniment(rezultat.get("eveniment"))

        if efect == "suspiciune_plus":
            order_suspicion += 1
        elif efect == "incredere_ordin_plus":
            dragon_order_trust += 1
        elif efect == "lupta":
            return True

        return False


label environment_director_on_enter(zone):
    python:
        _chr_zone = zone
        _chr_state = ai_chronicler_state(zone)
        _chr_box = ai_runtime.run_async(
            ai_runtime.chronicler().pick_event,
            _chr_state,
            renpy.random.randint(0, 99),
            list(ai_recent_events),
            ai_player_can_fight(),
        )

    call ai_wait_screen(_chr_box, AI_CHRONICLER_WAIT, u"Cronicarul cântărește locul…")

    python:
        _chr_result = _chr_box.get("value")
        if _chr_result is None:
            # Firul a murit sau a expirat timpul: euristica scrisă de mână preia.
            _chr_result = dict(ai_fallback_event(_chr_zone))
            _chr_result["sursa"] = u"fallback"
            _chr_result["motiv_tehnic"] = _chr_box.get("error") or u"modelul nu a răspuns în timp util"
            _chr_result["latenta"] = AI_CHRONICLER_WAIT
            _chr_result["raw"] = u""

        ai_note_call(u"Cronicarul", _chr_result)
        ai_remember_event(_chr_result.get("eveniment", ""))
        _chr_fight = ai_chronicler_apply(_chr_result)
        _chr_text = _chr_result.get("text", u"")

    if _chr_text:
        narrator "{i}(Cronicarul){/i} [_chr_text]"

    if _chr_fight:
        $ _chr_enemy = ai_chronicler_ambush_enemy(_chr_zone)
        call start_combat(_chr_enemy, "grid_map")

    return
