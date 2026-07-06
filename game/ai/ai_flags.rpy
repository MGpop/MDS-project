# game/ai/ai_flags.rpy

# Dacă este False, jocul nu mai încearcă să contacteze serverul AI.
default ai_enabled = True

# Serverul local FastAPI.
default ai_server_url = "http://127.0.0.1:8765"

# Stare runtime.
default ai_available = False
default ai_last_error = ""
default ai_last_reply = ""

# Starea primită de la Environment Director Agent.
default ai_world_tone = "neutral"
default ai_spawn_modifier = "normal"
default ai_environment_state = {}

# Pentru debugging rapid în joc.
default ai_debug_mode = True

# Pornește automat serverul AI dacă nu este deja pornit.
default ai_auto_start_server = True

# Câte secunde așteaptă jocul ca serverul AI să pornească.
default ai_server_start_timeout = 15

# Debug/runtime.
default ai_server_started_by_game = False
default ai_server_start_error = ""