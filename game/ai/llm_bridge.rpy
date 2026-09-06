# ai/llm_bridge.rpy
# Puntea dintre joc și modelul de limbaj local.
#
# Aici stau: configurația agenților, așteptarea neblocantă a răspunsului și
# panoul de debug care arată la prezentare ce a decis agentul și de ce.

init -5 python:
    import os as _ai_os
    import time as _ai_time

    import dragon_ai.runtime as ai_runtime
    from dragon_ai import schemas as ai_schemas
    from dragon_ai.config import MODELE_SUGERATE

    # Jurnalul apelurilor: materie primă pentru evals și pentru raportul AI.
    AI_LOG_PATH = _ai_os.path.join(config.basedir, "logs", "llm_calls.jsonl")

    # Cât așteptăm în joc înainte să trecem pe fallback.
    # Calibrate pe latențele măsurate în evals (p95: ~12s cronicar, ~8s dialog cu
    # qwen2.5:3b-instruct pe CPU). Cu o marjă peste, ca să nu aruncăm pe fallback
    # răspunsuri care oricum ar fi venit.
    AI_DIALOG_WAIT = 28.0
    AI_CHRONICLER_WAIT = 28.0

    # Câte schimburi are voie o conversație liberă, ca să nu se poată "farma" loialitate.
    AI_DIALOG_MAX_EXCHANGES = 5


# Preferințe salvate între sesiuni: se pot schimba din meniul de opțiuni.
default persistent.ai_enabled = True
default persistent.ai_model = MODELE_SUGERATE[0]

# Ultimul apel al unui agent, pentru panoul de debug. Doar șiruri și numere.
default ai_last_call = {}
default ai_debug_lines = []
default ai_debug_visible = False

# Evenimentele recente ale Cronicarului, ca să nu se repete.
default ai_recent_events = []


init python:
    def _ai_sigur(text):
        """Text venit de la model sau dintr-o excepție, făcut sigur pentru ecran."""
        if not text:
            return u""
        return text.replace("[", "[[").replace("{", "{{")

    def ai_apply_settings():
        """Reconstruiește agenții după preferințele curente ale jucătorului."""
        ai_runtime.configure(
            model=persistent.ai_model or MODELE_SUGERATE[0],
            enabled=bool(persistent.ai_enabled),
            log_path=AI_LOG_PATH,
        )

    def ai_status_text():
        """Ce scrie în meniul de opțiuni despre starea modelului local."""
        if not persistent.ai_enabled:
            return u"oprit — jocul folosește textele scrise de mână"
        if ai_runtime.is_available():
            return u"pornit — model local: %s" % persistent.ai_model
        return u"pornit, dar modelul local nu răspunde — se folosesc textele de rezervă"

    def ai_toggle_enabled():
        persistent.ai_enabled = not persistent.ai_enabled
        ai_apply_settings()

    def ai_set_model(nume):
        persistent.ai_model = nume
        ai_apply_settings()

    def ai_thinking_dots():
        return u"." * (int(_ai_time.time() * 2) % 4)

    def ai_deadline(timeout):
        return _ai_time.time() + timeout

    def ai_still_waiting(cutie, limita):
        return (not cutie["done"]) and _ai_time.time() < limita

    def ai_note_call(agent, rezultat):
        global ai_last_call, ai_debug_lines

        sursa = rezultat.get("sursa", u"?")
        linii = [
            ("ai_debug_text", u"Agent: %s   |   Model: %s" % (agent, persistent.ai_model)),
        ]
        if sursa == u"model":
            linii.append(("ai_debug_ok", u"Sursă: MODEL LOCAL   |   Latență: %.1fs"
                        % float(rezultat.get("latenta", 0.0))))
        else:
            linii.append(("ai_debug_warn", u"Sursă: FALLBACK — %s"
                        % _ai_sigur(rezultat.get("motiv_tehnic", u""))))

        motiv = _ai_sigur(rezultat.get("motiv", u""))
        if motiv:
            linii.append(("ai_debug_text", u"Motivul agentului: " + motiv))

        brut = _ai_sigur(rezultat.get("raw", u""))
        if brut:
            linii.append(("ai_debug_raw", u"JSON brut: " + brut))

        ai_debug_lines = linii
        ai_last_call = {"agent": agent, "sursa": sursa}

    def ai_remember_event(eveniment_id):
        global ai_recent_events
        if eveniment_id in ("nimic", ""):
            return
        ai_recent_events = ([eveniment_id] + list(ai_recent_events))[:3]

    def ai_player_can_fight():
        if in_combat:
            return False
        if "ambuscada" in ai_recent_events:
            return False
        return player_health >= player_max_health * 0.6

    def ai_inventory_names(limita=4):
        nume = [
            ITEMS.get(item_id, {}).get("name", item_id)
            for item_id in inventory.keys()
            if item_id != "monede" and inventory.get(item_id, 0) > 0
        ]
        return nume[:limita]

    def ai_loyalty_snapshot():
        return {
            u"Vlad": loyalty_vlad,
            u"boieri": loyalty_boyars,
            u"otomani": loyalty_ottomans,
            u"Ordin": dragon_order_trust,
        }


# Agenții se construiesc o dată, la pornire, iar modelul se încarcă în RAM în
# fundal — altfel primul apel din joc ar dura zeci de secunde, cât citește Ollama
# gigabytele de pe disc.
init 100 python:
    ai_apply_settings()

label after_load:
    $ ai_apply_settings()
    return

label splashscreen:
    python:
        if persistent.ai_enabled:
            ai_runtime.warmup_async()
    return


# --- Ecranul de așteptare -----------------------------------------------------
# Se vede cât lucrează modelul. Fără el, jocul ar părea înghețat câteva secunde.

screen ai_thinking(mesaj):
    modal True
    zorder 250

    # Timerul ecranului e cel care ține bucla de așteptare în mișcare.
    # ATENȚIE: nu înlocui asta cu `pause` într-un while, cu ecranul afișat prin
    # `show screen`. Sub un ecran `modal True`, `pause` nu se mai termină
    # niciodată, iar jocul rămâne blocat pe „se gândește" la infinit.
    # Același tipar e folosit și de screen-ul combat_wait.
    timer 0.15 action Return()

    frame:
        xalign 0.5
        yalign 0.82
        xpadding 30
        ypadding 20
        background Solid("#000000DD")

        hbox:
            spacing 14
            add Solid("#D4AF37", xsize=10, ysize=10) yalign 0.5
            text (mesaj + ai_thinking_dots()) style "ai_thinking_text" yalign 0.5


label ai_wait_screen(cutie, timeout, mesaj):
    # Cât lucrează modelul pe alt fir, arătăm ecranul de așteptare și îl lăsăm să
    # se întoarcă singur la fiecare 0.15s. Bucla verifică între timp dacă a venit
    # răspunsul. Dacă expiră timpul, ieșim oricum — apelantul are un fallback.
    $ _ai_limita = ai_deadline(timeout)
    while ai_still_waiting(cutie, _ai_limita):
        call screen ai_thinking(mesaj)
    return


# --- Panoul de debug ----------------------------------------------------------
# Comutabil cu F9. Fără el, la prezentare nu se vede că în spate chiar rulează
# un model: aici apar decizia, motivul, latența și JSON-ul brut.

screen ai_debug_panel():
    zorder 180

    frame:
        xalign 0.5
        yalign 0.02
        xsize 900
        xpadding 16
        ypadding 12
        background Solid("#000000E0")

        vbox:
            spacing 4

            text "Agent AI — ultimul apel" style "grid_zone_title" size 20

            if not ai_debug_lines:
                text "Niciun apel încă. Intră într-o zonă sau vorbește liber cu un NPC." style "ai_debug_text"
            else:
                for _stil, _linie in ai_debug_lines:
                    text _linie style _stil


style ai_thinking_text:
    font "fonts/Cormorant_Upright/CormorantUpright-Regular.ttf"
    size 24
    color "#D4AF37"

style ai_debug_text:
    font "DejaVuSans.ttf"
    size 15
    color "#C0C0C0"

style ai_debug_ok:
    font "DejaVuSans.ttf"
    size 15
    color "#7FD17F"

style ai_debug_warn:
    font "DejaVuSans.ttf"
    size 15
    color "#E0A050"

style ai_debug_raw:
    font "DejaVuSans.ttf"
    size 13
    color "#7A7A7A"
