# game/ai/ai_client.rpy

init python:
    import json
    import os
    import time
    import subprocess

    try:
        from urllib.request import Request, urlopen
    except ImportError:
        from urllib2 import Request, urlopen

    AI_DEFAULT_TIMEOUT = 5
    _ai_server_process = None

    def ai_log(message):
        try:
            if getattr(store, "ai_debug_mode", False):
                renpy.log("[AI] " + str(message))
        except Exception:
            pass

    def ai_base_url():
        return getattr(store, "ai_server_url", "http://127.0.0.1:8765").rstrip("/")

    def ai_set_error(error_message):
        store.ai_available = False
        store.ai_last_error = str(error_message)
        ai_log("ERROR: " + str(error_message))

    def ai_clear_error():
        store.ai_last_error = ""

    def ai_json_request(method, endpoint, payload=None, timeout=AI_DEFAULT_TIMEOUT):
        if not getattr(store, "ai_enabled", True):
            ai_set_error("AI disabled.")
            return None

        try:
            data = None
            if payload is not None:
                data = json.dumps(payload).encode("utf-8")

            request = Request(
                ai_base_url() + endpoint,
                data=data,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
            request.get_method = lambda: method

            response = urlopen(request, timeout=timeout)
            raw = response.read().decode("utf-8")
            result = json.loads(raw) if raw else {}
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

    def ai_project_root():
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

            if os.path.exists(os.path.join(root, "ai", "server.py")) and os.path.exists(os.path.join(root, "runtime", "python311", "python.exe")):
                return root

        try:
            return os.path.abspath(config.basedir)
        except Exception:
            return os.getcwd()

    def ai_server_paths():
        root = ai_project_root()
        return (
            root,
            os.path.join(root, "runtime", "python311", "python.exe"),
            os.path.join(root, "ai", "server.py"),
        )

    def ai_health_check(timeout=2):
        result = ai_get("/health", timeout=timeout)
        if result and result.get("status") == "ok":
            store.ai_available = True
            ai_clear_error()
            return True
        return False

    def ai_wait_for_server(max_seconds=None):
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
        global _ai_server_process

        if not getattr(store, "ai_auto_start_server", True):
            ai_set_error("Auto-start AI server este dezactivat.")
            return False

        if ai_health_check(timeout=1):
            return True

        root, python_exe, server_script = ai_server_paths()

        if not os.path.exists(python_exe):
            ai_set_error("Nu am găsit Python-ul inclus: " + python_exe)
            return False

        if not os.path.exists(server_script):
            ai_set_error("Nu am găsit server.py: " + server_script)
            return False

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

            _ai_server_process = subprocess.Popen([python_exe, server_script], **popen_kwargs)
            store.ai_server_started_by_game = True
            store.ai_server_start_error = ""
            ai_log("Am pornit serverul AI din joc.")
            return ai_wait_for_server()

        except Exception as exc:
            store.ai_server_start_error = str(exc)
            ai_set_error(exc)
            return False

    def ai_ensure_server_running():
        if ai_health_check(timeout=1):
            return True
        return ai_start_server()

    def ai_stop_server():
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

    def ai_basic_context(extra_context=None):
        env_state = getattr(store, "ai_environment_state", {}) or {}
        context = {
            "player_name": getattr(store, "player_name", "Mara"),
            "player_location": getattr(store, "player_location", ""),
            "player_grid_row": getattr(store, "player_grid_row", 0),
            "player_grid_col": getattr(store, "player_grid_col", 0),
            "current_chapter": getattr(store, "current_chapter", 1),
            "ai_world_tone": getattr(store, "ai_world_tone", "neutral"),
            "ai_spawn_modifier": getattr(store, "ai_spawn_modifier", "normal"),
            "honor": env_state.get("honor", 0),
            "cruelty": env_state.get("cruelty", 0),
            "suspicion": env_state.get("suspicion", 0),
            "commoner_trust": env_state.get("commoner_trust", 0),
        }
        if extra_context:
            context.update(extra_context)
        return context

    def ai_dialogue(npc_id, location="", player_message="", context=None, fallback=None):
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

        reply = result.get("reply", fallback) or fallback
        store.ai_last_reply = reply
        return reply

    def ai_get_riddle():
        fallback = {
            "id": "shadow",
            "question": "I follow you by day, but vanish at night. What am I?",
            "answer": "shadow",
            "accepted_answers": ["shadow", "a shadow", "my shadow", "your shadow"],
        }

        if not ai_ensure_server_running():
            return fallback

        result = ai_get("/riddle/random", timeout=5)
        if not result:
            return fallback

        return {
            "id": result.get("id", fallback["id"]),
            "question": result.get("question", fallback["question"]),
            "answer": result.get("answer", fallback["answer"]),
            "accepted_answers": result.get("accepted_answers", fallback["accepted_answers"]),
        }

    def ai_direct_riddle_match(riddle, player_answer):
        import re
        answer = (player_answer or "").lower().strip()
        answer = re.sub(r"[^a-z0-9 ]+", "", answer)
        answer = re.sub(r"\s+", " ", answer).strip()

        accepted = list(riddle.get("accepted_answers", []))
        accepted.append(riddle.get("answer", ""))

        normalized = []
        for value in accepted:
            value = (value or "").lower().strip()
            value = re.sub(r"[^a-z0-9 ]+", "", value)
            value = re.sub(r"\s+", " ", value).strip()
            if value:
                normalized.append(value)

        return answer in normalized

    def ai_evaluate_riddle(riddle, player_answer, context=None):
        fallback_correct = ai_direct_riddle_match(riddle, player_answer)
        fallback = {
            "riddle_id": riddle.get("id", "fallback"),
            "correct": fallback_correct,
            "farewell": "A clear answer cuts through fog; take what the road offers." if fallback_correct else "Not every seed grows into truth; perhaps another road will teach you.",
            "used_model": False,
            "direct_match": fallback_correct,
        }

        if not ai_ensure_server_running():
            return fallback

        payload = {
            "riddle_id": riddle.get("id", ""),
            "question": riddle.get("question", ""),
            "answer": riddle.get("answer", ""),
            "accepted_answers": riddle.get("accepted_answers", []),
            "player_answer": player_answer,
            "context": ai_basic_context(context),
        }

        result = ai_post("/riddle/evaluate", payload, timeout=25)
        if not result:
            return fallback

        if fallback_correct:
            result["correct"] = True

        return result

    def ai_environment_event(event_type, data=None):
        if data is None:
            data = {}
        if not ai_ensure_server_running():
            return None
        result = ai_post("/environment/update", {"event_type": event_type, "data": data}, timeout=5)
        if result:
            store.ai_environment_state = result.get("state", {})
            store.ai_world_tone = result.get("npc_tone", "neutral")
            store.ai_spawn_modifier = result.get("spawn_modifier", "normal")
        return result