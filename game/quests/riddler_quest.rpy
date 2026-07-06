# game/quests/riddler_quest.rpy

init python:
    import random
    import time

    RIDDLER_FIRST_SPAWN_CHANCE = 1.0    # 0.10
    RIDDLER_REPEAT_SPAWN_CHANCE = 1.0   # 0.03
    RIDDLER_COOLDOWN_SECONDS = 1 * 10   # 5 * 60

    def riddler_now():
        return time.time()

    def riddler_remaining_cooldown():
        remaining = float(getattr(store, "riddler_cooldown_until", 0.0) or 0.0) - riddler_now()
        return max(0, int(remaining))

    def riddler_is_on_cooldown():
        return riddler_remaining_cooldown() > 0

    def riddler_spawn_chance():
        if not bool(getattr(store, "riddler_first_encounter_done", False)):
            return RIDDLER_FIRST_SPAWN_CHANCE
        return RIDDLER_REPEAT_SPAWN_CHANCE

    def riddler_is_here(row=None, col=None):
        if row is None:
            row = getattr(store, "player_grid_row", -1)
        if col is None:
            col = getattr(store, "player_grid_col", -1)

        return (
            bool(getattr(store, "riddler_active", False))
            and int(getattr(store, "riddler_row", -1)) == int(row)
            and int(getattr(store, "riddler_col", -1)) == int(col)
        )

    def riddler_can_spawn_on_cell(row, col):
        if bool(getattr(store, "riddler_active", False)):
            return False
        if riddler_is_on_cooldown():
            return False
        try:
            return get_cell_char(row, col) == "G" and is_grid_passable(row, col)
        except Exception:
            return False

    def riddler_try_spawn_on_current_cell():
        row = int(getattr(store, "player_grid_row", -1))
        col = int(getattr(store, "player_grid_col", -1))

        if not riddler_can_spawn_on_cell(row, col):
            return False

        if random.random() <= riddler_spawn_chance():
            store.riddler_active = True
            store.riddler_row = row
            store.riddler_col = col
            store.riddler_current_riddle = None
            store.riddler_last_result = None
            return True

        return False

    def riddler_despawn(start_cooldown=True):
        store.riddler_active = False
        store.riddler_row = -1
        store.riddler_col = -1
        store.riddler_current_riddle = None
        if start_cooldown:
            store.riddler_cooldown_until = riddler_now() + RIDDLER_COOLDOWN_SECONDS

    def riddler_debug_force_spawn_here():
        store.riddler_active = True
        store.riddler_row = int(getattr(store, "player_grid_row", -1))
        store.riddler_col = int(getattr(store, "player_grid_col", -1))
        store.riddler_current_riddle = None
        store.riddler_last_result = None


label zone_actions_riddler:
    scene expression grid_background_displayable(player_grid_row, player_grid_col) with dissolve
    show expression npc_displayable("ghicitor") as npc_ghicitor at actor_ghicitor

    if not riddler_first_encounter_done:
        "Printre spicele înalte apare un bătrân cu o privire prea limpede pentru chipul lui obosit."
        ghicitor "Nu cer aur sau jurăminte. Doar un răspuns."
        ghicitor "Dacă răspunsul tău are miez, primești merinde pentru drum."
        $ riddler_first_encounter_done = True
    else:
        "Ghicitorul apare dintre grâne de parcă ar fi stat acolo de la începutul lumii."
        ghicitor "Ai mai venit cu întrebări în tălpi. Să vedem dacă ai și răspuns în minte."

    python:
        _riddle_intro = ai_dialogue(
            "riddler",
            "wheat fields",
            "Give me a short mysterious introduction before asking a riddle.",
            {"riddler_event": True},
            fallback="The wheat bends, the road listens, and I ask only one thing."
        )

    ghicitor "[_riddle_intro]"

    $ _riddle = ai_get_riddle()
    $ riddler_current_riddle = _riddle
    $ _riddle_question = _riddle.get("question", "I follow you by day, but vanish at night. What am I?")

    ghicitor "[_riddle_question]"

    $ _answer = renpy.input("Your answer:", length=80).strip()

    if not _answer:
        $ _answer = ""

    python:
        _riddle_result = ai_evaluate_riddle(
            _riddle,
            _answer,
            {"npc": "riddler", "location": player_location}
        )

    $ riddler_last_result = _riddle_result
    $ _riddle_correct = bool(_riddle_result.get("correct", False))
    $ _farewell = _riddle_result.get("farewell", "The field has heard enough. Walk on, traveler.")

    if _riddle_correct:
        $ add_item("merinde", 1)
        ghicitor "[_farewell]"
        narrator "Ai primit 1 merinde."
        $ ai_environment_event("solved_riddle", {"riddle_id": _riddle.get("id", ""), "answer": _answer})
    else:
        ghicitor "[_farewell]"
        narrator "Nu ai primit nimic. Ghicitorul pare deja departe, deși încă stă în fața ta."
        $ ai_environment_event("failed_riddle", {"riddle_id": _riddle.get("id", ""), "answer": _answer})

    $ riddler_despawn(start_cooldown=True)
    hide npc_ghicitor
    return