label test_ai_client:

    "Testez conexiunea cu serverul AI..."

    $ _ai_ok = ai_ensure_server_running()

    if _ai_ok:
        "Serverul AI răspunde."
    else:
        "Serverul AI nu răspunde. Eroare: [ai_last_error]"
        return

    "Testez Dialogue Agent..."

    $ _reply = ai_dialogue(
        "ghicitor",
        "lanuri de grâu",
        "Who are you?",
        {
            "language": "en",
            "test": True
        },
        fallback="The riddler remains silent."
    )

    "Răspuns AI:"
    "[_reply]"

    "Testez Environment Director Agent..."

    $ _env = ai_environment_event(
        "promise_kept",
        {
            "quest": "test_ai_client",
            "npc": "ghicitor"
        }
    )

    if _env:
        "Environment Director a răspuns."
        "Ton NPC: [ai_world_tone]"
        "Spawn modifier: [ai_spawn_modifier]"
    else:
        "Environment Director nu a răspuns. Eroare: [ai_last_error]"

    return