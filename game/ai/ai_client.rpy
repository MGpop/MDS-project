# game/ai/ai_client.rpy

init python:
    import json
    import os
    import time
    import subprocess

    try:
        from urllib.request import Request, urlopen
        from urllib.error import URLError, HTTPError
    except ImportError:
        # Fallback pentru Python mai vechi, dacă ar fi cazul.
        from urllib2 import Request, urlopen, URLError, HTTPError


    AI_DEFAULT_TIMEOUT = 5

    _ai_server_process = None


    def ai_project_root():
        """
        Găsește folderul principal al proiectului:
        Order of the Dragon/
        """

        candidates = []

        try:
            candidates.append(config.basedir)
        except Exception:
            pass

        try:
            candidates.append(os.path.dirname(config.gamedir))
        except Exception:
            pass

        candidates.append(os.getcwd())

        seen = set()

        for candidate in candidates:
            if not candidate:
                continue

            root = os.path.abspath(candidate)

            if root in seen:
                continue

            seen.add(root)

            server_script = os.path.join(root, "ai", "server.py")
            python_exe = os.path.join(root, "runtime", "python311", "python.exe")

            if os.path.exists(server_script) and os.path.exists(python_exe):
                return root

        # fallback
        try:
            return os.path.abspath(config.basedir)
        except Exception:
            return os.getcwd()


    def ai_server_paths():
        root = ai_project_root()

        python_exe = os.path.join(root, "runtime", "python311", "python.exe")
        server_script = os.path.join(root, "ai", "server.py")

        return root, python_exe, server_script


    def ai_wait_for_server(max_seconds=None):
        """
        Așteaptă ca serverul AI să răspundă la /health.
        """

        if max_seconds is None:
            max_seconds = getattr(store, "ai_server_start_timeout", 15)

        deadline = time.time() + float(max_seconds)

        while time.time() < deadline:
            if ai_health_check(timeout=1):
                return True

            time.sleep(0.5)

        store.ai_server_start_error = "Serverul AI a fost pornit, dar nu a răspuns la timp."
        ai_set_error(store.ai_server_start_error)
        return False


    def ai_start_server():
        """
        Pornește serverul AI folosind Python-ul portabil inclus în proiect.
        """

        global _ai_server_process

        if not getattr(store, "ai_auto_start_server", True):
            ai_set_error("Auto-start AI server este dezactivat.")
            return False

        # Dacă serverul rulează deja, nu mai pornim altul.
        if ai_health_check(timeout=1):
            return True

        root, python_exe, server_script = ai_server_paths()

        if not os.path.exists(python_exe):
            store.ai_server_start_error = "Nu am găsit Python-ul inclus: " + python_exe
            ai_set_error(store.ai_server_start_error)
            return False

        if not os.path.exists(server_script):
            store.ai_server_start_error = "Nu am găsit server.py: " + server_script
            ai_set_error(store.ai_server_start_error)
            return False

        # Dacă noi am pornit deja un proces și încă merge, doar așteptăm health.
        try:
            if _ai_server_process is not None and _ai_server_process.poll() is None:
                return ai_wait_for_server()
        except Exception:
            _ai_server_process = None

        try:
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"
            env["ODD_AI_STARTED_BY_GAME"] = "1"

            popen_kwargs = {
                "cwd": root,
                "stdin": subprocess.DEVNULL,
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
                "env": env,
            }

            if os.name == "nt":
                popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

            _ai_server_process = subprocess.Popen(
                [python_exe, server_script],
                **popen_kwargs
            )

            store.ai_server_started_by_game = True
            store.ai_server_start_error = ""

            ai_log("Am pornit serverul AI din joc.")
            return ai_wait_for_server()

        except Exception as exc:
            store.ai_server_start_error = str(exc)
            ai_set_error(exc)
            return False


    def ai_ensure_server_running():
        """
        Verifică serverul AI; dacă nu merge, încearcă să îl pornească.
        """

        if ai_health_check(timeout=1):
            return True

        return ai_start_server()


    def ai_stop_server():
        """
        Oprește serverul AI doar dacă a fost pornit de joc.
        """

        global _ai_server_process

        try:
            if _ai_server_process is not None and _ai_server_process.poll() is None:
                _ai_server_process.terminate()
                _ai_server_process = None
                store.ai_server_started_by_game = False
                ai_log("Serverul AI a fost oprit.")
        except Exception:
            pass


    try:
        config.quit_callbacks.append(ai_stop_server)
    except Exception:
        pass


    def ai_log(message):
        """
        Scrie în log doar dacă debug mode este activ.
        """
        try:
            if getattr(store, "ai_debug_mode", False):
                renpy.log("[AI] " + str(message))
        except Exception:
            pass


    def ai_base_url():
        """
        Normalizează URL-ul serverului.
        """
        url = getattr(store, "ai_server_url", "http://127.0.0.1:8765")
        return url.rstrip("/")


    def ai_set_error(error_message):
        store.ai_available = False
        store.ai_last_error = str(error_message)
        ai_log("ERROR: " + str(error_message))


    def ai_clear_error():
        store.ai_last_error = ""


    def ai_json_request(method, endpoint, payload=None, timeout=AI_DEFAULT_TIMEOUT):
        """
        Trimite cerere JSON către serverul AI.

        Returnează:
        - dict, dacă merge
        - None, dacă serverul nu răspunde sau apare eroare
        """

        if not getattr(store, "ai_enabled", True):
            ai_set_error("AI disabled.")
            return None

        url = ai_base_url() + endpoint

        try:
            data = None
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            if payload is not None:
                data = json.dumps(payload).encode("utf-8")

            request = Request(
                url,
                data=data,
                headers=headers
            )

            # urllib decide metoda automat în funcție de data,
            # dar pentru claritate forțăm metoda.
            request.get_method = lambda: method

            response = urlopen(request, timeout=timeout)
            raw = response.read().decode("utf-8")

            if not raw:
                return {}

            result = json.loads(raw)

            store.ai_available = True
            ai_clear_error()

            return result

        except Exception as exc:
            ai_set_error(exc)
            return None


    def ai_get(endpoint, timeout=AI_DEFAULT_TIMEOUT):
        return ai_json_request("GET", endpoint, None, timeout)


    def ai_post(endpoint, payload, timeout=AI_DEFAULT_TIMEOUT):
        return ai_json_request("POST", endpoint, payload, timeout)


    def ai_health_check(timeout=2):
        """
        Verifică dacă serverul AI este pornit.
        """

        result = ai_get("/health", timeout=timeout)

        if result is None:
            return False

        status = result.get("status", "")

        if status == "ok":
            store.ai_available = True
            ai_clear_error()
            ai_log("Health check OK.")
            return True

        ai_set_error("Server AI returned invalid health response.")
        return False


    def ai_basic_context(extra_context=None):
        """
        Construiește contextul trimis către agenții AI.
        Folosim getattr ca să nu crape pe save-uri vechi sau variabile lipsă.
        """

        context = {
            "player_name": getattr(store, "player_name", "Mara"),
            "player_location": getattr(store, "player_location", ""),
            "player_grid_row": getattr(store, "player_grid_row", 0),
            "player_grid_col": getattr(store, "player_grid_col", 0),
            "current_chapter": getattr(store, "current_chapter", 1),

            "ai_world_tone": getattr(store, "ai_world_tone", "neutral"),
            "ai_spawn_modifier": getattr(store, "ai_spawn_modifier", "normal"),

            "honor": getattr(store, "ai_environment_state", {}).get("honor", 0),
            "cruelty": getattr(store, "ai_environment_state", {}).get("cruelty", 0),
            "suspicion": getattr(store, "ai_environment_state", {}).get("suspicion", 0),
            "commoner_trust": getattr(store, "ai_environment_state", {}).get("commoner_trust", 0),

            "got_city_seal": getattr(store, "got_city_seal", False),
            "boier_chest_returned": getattr(store, "boier_chest_returned", False),
            "wolf_tutorial_done": getattr(store, "wolf_tutorial_done", False),
        }

        if extra_context:
            context.update(extra_context)

        return context


    def ai_dialogue(npc_id, location="", player_message="", context=None, fallback=None):
        """
        Cere o replică de la Dialogue Agent.

        Returnează mereu un string.
        Dacă AI-ul nu merge, returnează fallback.
        """

        if fallback is None:
            fallback = "Nu știu ce să-ți spun acum, străine."

        if not ai_ensure_server_running():
            store.ai_last_reply = fallback
            return fallback

        payload = {
            "npc_id": npc_id,
            "location": location,
            "player_message": player_message,
            "context": ai_basic_context(context),
        }

        result = ai_post("/dialogue", payload, timeout=20)

        if result is None:
            store.ai_last_reply = fallback
            return fallback

        reply = result.get("reply", fallback)

        if not reply:
            reply = fallback

        store.ai_last_reply = reply

        # Dacă serverul întoarce și tonul Environment Director-ului, îl păstrăm.
        if "tone" in result:
            store.ai_world_tone = result.get("tone") or store.ai_world_tone

        return reply


    def ai_environment_event(event_type, data=None):
        """
        Trimite un eveniment către Environment Director Agent.

        Exemple event_type:
        - promise_kept
        - promise_broken
        - returned_valuable
        - civilian_killed
        - attacked_boyar
        """

        if data is None:
            data = {}

        if not ai_ensure_server_running():
            return None

        payload = {
            "event_type": event_type,
            "data": data,
        }

        result = ai_post("/environment/update", payload, timeout=5)

        if result is None:
            return None

        state = result.get("state", {})
        npc_tone = result.get("npc_tone", "neutral")
        spawn_modifier = result.get("spawn_modifier", "normal")

        store.ai_environment_state = state
        store.ai_world_tone = npc_tone
        store.ai_spawn_modifier = spawn_modifier

        ai_log("Environment updated: tone=%s spawn=%s" % (npc_tone, spawn_modifier))

        return result


    def ai_get_environment_state():
        """
        Cere starea curentă de la Environment Director Agent.
        """

        result = ai_get("/environment/state", timeout=5)

        if result is None:
            return None

        state = result.get("state", {})
        npc_tone = result.get("npc_tone", "neutral")
        spawn_modifier = result.get("spawn_modifier", "normal")

        store.ai_environment_state = state
        store.ai_world_tone = npc_tone
        store.ai_spawn_modifier = spawn_modifier

        return result


    def ai_combat_adapt(enemy_id, player_actions, player_hp=100, player_max_hp=100, enemy_hp=100, enemy_max_hp=100):
        """
        Cere Combat Adaptation Agent-ului o strategie.
        Momentan nu îl conectăm încă la combat_system.rpy, doar îl pregătim.
        """

        payload = {
            "enemy_id": enemy_id,
            "player_actions": player_actions,
            "player_hp": player_hp,
            "player_max_hp": player_max_hp,
            "enemy_hp": enemy_hp,
            "enemy_max_hp": enemy_max_hp,
        }

        result = ai_post("/combat/adapt", payload, timeout=5)

        if result is None:
            return {
                "enemy_id": enemy_id,
                "detected_pattern": "fallback",
                "strategy": "standard",
                "light_chance_bonus": 0,
                "heavy_chance_bonus": 0,
                "parry_chance_bonus": 0,
                "delay_modifier": 1.0,
                "explanation": "AI server unavailable.",
            }

        return result


    def ai_reward_evaluate(enemy_id, base_xp=10, base_coins=3, player_max_hp=100, player_hp_end=100,
                        damage_dealt=0, damage_taken=0, enemy_damage=0, turns=1, used_consumables=0):
        """
        Cere Reward Evaluator Agent-ului o recompensă.
        Îl vom conecta mai târziu la combat_victory.
        """

        payload = {
            "enemy_id": enemy_id,
            "base_xp": base_xp,
            "base_coins": base_coins,
            "player_max_hp": player_max_hp,
            "player_hp_end": player_hp_end,
            "damage_dealt": damage_dealt,
            "damage_taken": damage_taken,
            "enemy_damage": enemy_damage,
            "turns": turns,
            "used_consumables": used_consumables,
        }

        result = ai_post("/reward/evaluate", payload, timeout=5)

        if result is None:
            return {
                "enemy_id": enemy_id,
                "xp": base_xp,
                "coins": base_coins,
                "food": 0,
                "difficulty_score": 1.0,
                "explanation": "AI server unavailable.",
            }

        return result