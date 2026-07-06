from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import threading

from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from gpt4all import GPT4All
except Exception:
    GPT4All = None


# ---------------------------------------------------------------------
# Paths / config
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AI_DIR = PROJECT_ROOT / "ai"
CONFIG_FILE = AI_DIR / "config.json"
DATA_DIR = AI_DIR / "data"
LOGS_DIR = AI_DIR / "logs"
ENV_STATE_FILE = DATA_DIR / "environment_state.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


DEFAULT_CONFIG = {
    "model_backend": "gpt4all",
    "model_path": "ai/models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
    "server_host": "127.0.0.1",
    "server_port": 8765,
    "ai_dialogue_enabled": True,
    "environment_director_enabled": True,
    "combat_adaptation_enabled": True,
    "reward_evaluator_enabled": True,
    "max_tokens": 140,
    "temperature": 0.8
}


def load_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return dict(DEFAULT_CONFIG)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    merged = dict(DEFAULT_CONFIG)
    merged.update(config)
    return merged


def resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def clamp(value: int, minimum: int = -100, maximum: int = 100) -> int:
    return max(minimum, min(maximum, int(value)))


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------

app = FastAPI(title="Order of the Dragon AI Server")


# ---------------------------------------------------------------------
# Dialogue model state
# ---------------------------------------------------------------------

_dialogue_model = None
_dialogue_model_error: Optional[str] = None
_dialogue_lock = threading.Lock()


def get_dialogue_model():
    """
    Încarcă modelul GGUF doar când este folosit prima dată.
    Astfel serverul poate porni chiar dacă modelul are o problemă.
    """

    global _dialogue_model, _dialogue_model_error

    if _dialogue_model is not None:
        return _dialogue_model

    if GPT4All is None:
        _dialogue_model_error = "Pachetul gpt4all nu este instalat sau nu poate fi importat."
        return None

    config = load_config()
    model_path = resolve_project_path(config["model_path"])

    if not model_path.exists():
        _dialogue_model_error = f"Modelul GGUF nu există: {model_path}"
        return None

    try:
        _dialogue_model = GPT4All(
            model_name=model_path.name,
            model_path=str(model_path.parent),
            allow_download=False
        )
        _dialogue_model_error = None
        return _dialogue_model

    except Exception as exc:
        _dialogue_model_error = str(exc)
        return None


def clean_model_reply(text: str) -> str:
    text = text.strip()

    unwanted_prefixes = [
        "NPC:",
        "Răspuns:",
        "Replica:",
        "Ghicitorul:",
        "Personajul:",
    ]

    changed = True
    while changed:
        changed = False
        for prefix in unwanted_prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                changed = True

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return "Hm... vântul mi-a furat vorbele. Mai întreabă-mă o dată."

    # Luăm doar primele 2 replici ca să nu țină monologuri lungi.
    return " ".join(lines[:2])[:800]


def fallback_dialogue(npc_id: str, player_message: str, context: Dict[str, Any]) -> str:
    if npc_id == "ghicitor":
        return "He-he... pământul ascunde multe răspunsuri, dar nu le dă pe toate celui grăbit."

    if npc_id == "soldat_fantana":
        return "Vorbește repede, drumețule. Nu-mi place liniștea asta din jurul fântânii."

    if npc_id == "negustor":
        return "Marfă puțină, vremuri grele. Dar pentru omul potrivit se găsește mereu ceva."

    return "Nu știu ce să-ți spun acum, străine."


# ---------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------

class DialogueRequest(BaseModel):
    npc_id: str
    location: str = ""
    player_message: str
    context: Dict[str, Any] = Field(default_factory=dict)


class DialogueResponse(BaseModel):
    npc_id: str
    reply: str
    tone: str = "neutral"
    emotion: str = "calm"
    used_model: bool
    error: Optional[str] = None


class EnvironmentEventRequest(BaseModel):
    event_type: str
    data: Dict[str, Any] = Field(default_factory=dict)


class EnvironmentStateResponse(BaseModel):
    state: Dict[str, Any]
    npc_tone: str
    spawn_modifier: str
    explanation: str


class CombatAdaptRequest(BaseModel):
    enemy_id: str
    player_actions: List[str] = Field(default_factory=list)
    player_hp: int = 100
    player_max_hp: int = 100
    enemy_hp: int = 100
    enemy_max_hp: int = 100


class CombatAdaptResponse(BaseModel):
    enemy_id: str
    detected_pattern: str
    strategy: str
    light_chance_bonus: int
    heavy_chance_bonus: int
    parry_chance_bonus: int
    delay_modifier: float
    explanation: str


class RewardEvaluateRequest(BaseModel):
    enemy_id: str
    base_xp: int = 10
    base_coins: int = 3
    player_max_hp: int = 100
    player_hp_end: int = 100
    damage_dealt: int = 0
    damage_taken: int = 0
    enemy_damage: int = 0
    turns: int = 1
    used_consumables: int = 0


class RewardEvaluateResponse(BaseModel):
    enemy_id: str
    xp: int
    coins: int
    food: int
    difficulty_score: float
    explanation: str


# ---------------------------------------------------------------------
# Environment Director Agent
# ---------------------------------------------------------------------

DEFAULT_ENV_STATE = {
    "honor": 0,
    "cruelty": 0,
    "mercy": 0,
    "greed": 0,
    "suspicion": 0,
    "world_tension": 0,
    "commoner_trust": 0,
    "roman_support": 0,
    "bandit_respect": 0,
    "boyar_fear": 0,
    "events_seen": 0,
    "last_event": None,
    "updated_at": None
}


def load_environment_state() -> Dict[str, Any]:
    if not ENV_STATE_FILE.exists():
        save_environment_state(DEFAULT_ENV_STATE)
        return dict(DEFAULT_ENV_STATE)

    try:
        with open(ENV_STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = dict(DEFAULT_ENV_STATE)

    merged = dict(DEFAULT_ENV_STATE)
    merged.update(state)
    return merged


def save_environment_state(state: Dict[str, Any]) -> None:
    ENV_STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def apply_environment_event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    state = load_environment_state()

    def add(key: str, amount: int):
        state[key] = clamp(state.get(key, 0) + amount)

    if event_type == "promise_kept":
        add("honor", 15)
        add("commoner_trust", 10)
        add("world_tension", -4)

    elif event_type == "promise_broken":
        add("honor", -20)
        add("suspicion", 15)
        add("commoner_trust", -12)
        add("world_tension", 8)

    elif event_type == "helped_commoner":
        add("honor", 8)
        add("mercy", 8)
        add("commoner_trust", 12)

    elif event_type == "stole_item":
        add("greed", 12)
        add("suspicion", 12)
        add("honor", -8)
        add("world_tension", 4)

    elif event_type == "returned_valuable":
        add("honor", 18)
        add("commoner_trust", 15)
        add("greed", -5)
        add("world_tension", -3)

    elif event_type == "civilian_killed":
        add("cruelty", 25)
        add("suspicion", 20)
        add("world_tension", 20)
        add("commoner_trust", -25)
        add("honor", -20)

    elif event_type == "enemy_spared":
        add("mercy", 12)
        add("honor", 6)
        add("cruelty", -5)

    elif event_type == "enemy_executed":
        add("cruelty", 10)
        add("world_tension", 5)
        add("mercy", -8)

    elif event_type == "helped_bandits":
        add("bandit_respect", 16)
        add("roman_support", -8)
        add("suspicion", 10)

    elif event_type == "attacked_boyar":
        add("boyar_fear", 15)
        add("roman_support", -10)
        add("world_tension", 15)
        add("suspicion", 12)

    else:
        # Eveniment necunoscut: îl înregistrăm, dar nu stricăm nimic.
        add("suspicion", 1)

    state["events_seen"] = int(state.get("events_seen", 0)) + 1
    state["last_event"] = {
        "type": event_type,
        "data": data
    }
    state["updated_at"] = now_iso()

    save_environment_state(state)
    return state


def evaluate_npc_tone(state: Dict[str, Any]) -> str:
    cruelty = state.get("cruelty", 0)
    suspicion = state.get("suspicion", 0)
    honor = state.get("honor", 0)
    trust = state.get("commoner_trust", 0)
    greed = state.get("greed", 0)

    if cruelty >= 50:
        return "frightened"

    if suspicion >= 45:
        return "suspicious"

    if honor >= 35 and trust >= 25:
        return "respectful"

    if greed >= 40:
        return "guarded"

    if trust <= -30:
        return "cold"

    return "neutral"


def evaluate_spawn_modifier(state: Dict[str, Any]) -> str:
    tension = state.get("world_tension", 0)
    cruelty = state.get("cruelty", 0)
    suspicion = state.get("suspicion", 0)
    bandit_respect = state.get("bandit_respect", 0)
    roman_support = state.get("roman_support", 0)

    if tension >= 55 or cruelty >= 55 or suspicion >= 60:
        return "more_guards"

    if bandit_respect >= 35 and roman_support <= -15:
        return "more_bandits"

    if tension <= -20:
        return "calmer_roads"

    return "normal"


# ---------------------------------------------------------------------
# Combat Adaptation Agent
# ---------------------------------------------------------------------

def adapt_combat_strategy(
    enemy_id: str,
    actions: List[str],
    player_hp: int,
    player_max_hp: int,
    enemy_hp: int,
    enemy_max_hp: int
) -> Dict[str, Any]:

    recent = [a.lower() for a in actions[-8:]]

    light_count = recent.count("light")
    heavy_count = recent.count("heavy")
    parry_count = recent.count("parry")

    hp_ratio = player_hp / max(1, player_max_hp)

    pattern = "balanced"
    strategy = "standard"
    light_bonus = 0
    heavy_bonus = 0
    parry_bonus = 0
    delay_modifier = 1.0
    explanation = "Jucătorul nu are încă un pattern clar."

    if len(recent) < 3:
        pattern = "unknown"
        strategy = "observe"
        explanation = "Prea puține acțiuni observate. Inamicul joacă prudent."

    elif light_count >= 5:
        pattern = "light_spam"
        strategy = "anti_fast_attacks"
        parry_bonus = 20
        heavy_bonus = 5
        delay_modifier = 0.95
        explanation = "Jucătorul folosește multe atacuri rapide. Inamicul încearcă să pareze mai des."

    elif heavy_count >= 4:
        pattern = "heavy_spam"
        strategy = "interrupt_heavy"
        light_bonus = 20
        delay_modifier = 0.85
        explanation = "Jucătorul folosește atacuri grele. Inamicul răspunde cu atacuri mai rapide."

    elif parry_count >= 4:
        pattern = "defensive_parry"
        strategy = "bait_parry"
        heavy_bonus = 15
        delay_modifier = 1.15
        explanation = "Jucătorul parează des. Inamicul atacă mai rar, dar mai apăsat."

    elif hp_ratio <= 0.3:
        pattern = "low_hp_player"
        strategy = "pressure_player"
        light_bonus = 10
        heavy_bonus = 10
        delay_modifier = 0.9
        explanation = "Jucătorul are viață scăzută. Inamicul devine mai agresiv."

    return {
        "enemy_id": enemy_id,
        "detected_pattern": pattern,
        "strategy": strategy,
        "light_chance_bonus": light_bonus,
        "heavy_chance_bonus": heavy_bonus,
        "parry_chance_bonus": parry_bonus,
        "delay_modifier": delay_modifier,
        "explanation": explanation
    }


# ---------------------------------------------------------------------
# Reward Evaluator Agent
# ---------------------------------------------------------------------

def evaluate_reward(req: RewardEvaluateRequest) -> Dict[str, Any]:
    hp_lost_ratio = req.damage_taken / max(1, req.player_max_hp)
    hp_end_ratio = req.player_hp_end / max(1, req.player_max_hp)
    combat_length_factor = min(1.5, max(0.7, req.turns / 6))
    enemy_threat = req.enemy_damage / 10 if req.enemy_damage else 1.0

    difficulty_score = (
        1.0
        + hp_lost_ratio
        + (1.0 - hp_end_ratio) * 0.8
        + enemy_threat * 0.25
        + req.used_consumables * 0.15
    )

    difficulty_score *= combat_length_factor
    difficulty_score = max(0.5, min(3.0, difficulty_score))

    xp = int(req.base_xp * difficulty_score)
    coins = int(req.base_coins * min(2.2, difficulty_score))

    food = 0
    if difficulty_score >= 1.8:
        food = 1
    if difficulty_score >= 2.5:
        food = 2

    explanation = (
        f"Scor dificultate {difficulty_score:.2f}. "
        f"Damage primit: {req.damage_taken}, HP final: {req.player_hp_end}/{req.player_max_hp}, "
        f"ture: {req.turns}."
    )

    return {
        "enemy_id": req.enemy_id,
        "xp": max(1, xp),
        "coins": max(0, coins),
        "food": food,
        "difficulty_score": round(difficulty_score, 2),
        "explanation": explanation
    }


# ---------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------

@app.get("/health")
def health():
    config = load_config()
    model_path = resolve_project_path(config["model_path"])

    return {
        "status": "ok",
        "service": "order_of_the_dragon_ai",
        "config_file": str(CONFIG_FILE),
        "model_backend": config.get("model_backend"),
        "model_path": str(model_path),
        "model_exists": model_path.exists(),
        "gpt4all_imported": GPT4All is not None,
        "dialogue_model_loaded": _dialogue_model is not None,
        "dialogue_model_error": _dialogue_model_error
    }


@app.post("/dialogue", response_model=DialogueResponse)
def dialogue(request: DialogueRequest):
    config = load_config()

    if not config.get("ai_dialogue_enabled", True):
        return DialogueResponse(
            npc_id=request.npc_id,
            reply=fallback_dialogue(request.npc_id, request.player_message, request.context),
            used_model=False,
            error="Dialogue AI disabled in config."
        )

    model = get_dialogue_model()

    if model is None:
        return DialogueResponse(
            npc_id=request.npc_id,
            reply=fallback_dialogue(request.npc_id, request.player_message, request.context),
            used_model=False,
            error=_dialogue_model_error
        )

    env_state = load_environment_state()
    npc_tone = evaluate_npc_tone(env_state)

    system_prompt = (
        "You are a secondary NPC in a historical-fantasy game set during the time of Vlad the Impaler. "
        "Answer in the same language as the player's message. "
        "Keep the answer short, maximum 2 sentences. "
        "Do not invent items, rewards, locations, or new quests. "
        "Do not say you are an AI. "
        "Do not change the game state. "
        "Only generate the NPC's spoken line."
    )

    user_prompt = f"""
Context pentru personaj:

NPC ID: {request.npc_id}
Locație: {request.location}
Ton social sugerat de Environment Director: {npc_tone}

Context joc:
{json.dumps(request.context, ensure_ascii=False)}

Mesajul jucătorului:
{request.player_message}

Replica NPC-ului:
""".strip()

    full_prompt = system_prompt + "\n\n" + user_prompt

    try:
        with _dialogue_lock:
            raw_reply = model.generate(
                full_prompt,
                max_tokens=int(config.get("max_tokens", 140)),
                temp=float(config.get("temperature", 0.8))
            )

        reply = clean_model_reply(raw_reply)

        log_line = {
            "time": now_iso(),
            "npc_id": request.npc_id,
            "location": request.location,
            "player_message": request.player_message,
            "reply": reply,
            "used_model": True
        }

        with open(LOGS_DIR / "dialogue.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_line, ensure_ascii=False) + "\n")

        return DialogueResponse(
            npc_id=request.npc_id,
            reply=reply,
            tone=npc_tone,
            emotion="calm",
            used_model=True
        )

    except Exception as exc:
        return DialogueResponse(
            npc_id=request.npc_id,
            reply=fallback_dialogue(request.npc_id, request.player_message, request.context),
            tone=npc_tone,
            emotion="uncertain",
            used_model=False,
            error=str(exc)
        )


@app.post("/environment/update", response_model=EnvironmentStateResponse)
def environment_update(request: EnvironmentEventRequest):
    config = load_config()

    if not config.get("environment_director_enabled", True):
        state = load_environment_state()
        return EnvironmentStateResponse(
            state=state,
            npc_tone="neutral",
            spawn_modifier="normal",
            explanation="Environment Director este dezactivat în config."
        )

    state = apply_environment_event(request.event_type, request.data)
    tone = evaluate_npc_tone(state)
    spawn_modifier = evaluate_spawn_modifier(state)

    explanation = (
        f"Environment Director a procesat evenimentul '{request.event_type}'. "
        f"Ton NPC: {tone}. Spawn modifier: {spawn_modifier}."
    )

    return EnvironmentStateResponse(
        state=state,
        npc_tone=tone,
        spawn_modifier=spawn_modifier,
        explanation=explanation
    )


@app.get("/environment/state")
def environment_state():
    state = load_environment_state()
    return {
        "state": state,
        "npc_tone": evaluate_npc_tone(state),
        "spawn_modifier": evaluate_spawn_modifier(state)
    }


@app.post("/combat/adapt", response_model=CombatAdaptResponse)
def combat_adapt(request: CombatAdaptRequest):
    config = load_config()

    if not config.get("combat_adaptation_enabled", True):
        return CombatAdaptResponse(
            enemy_id=request.enemy_id,
            detected_pattern="disabled",
            strategy="standard",
            light_chance_bonus=0,
            heavy_chance_bonus=0,
            parry_chance_bonus=0,
            delay_modifier=1.0,
            explanation="Combat Adaptation Agent este dezactivat în config."
        )

    result = adapt_combat_strategy(
        enemy_id=request.enemy_id,
        actions=request.player_actions,
        player_hp=request.player_hp,
        player_max_hp=request.player_max_hp,
        enemy_hp=request.enemy_hp,
        enemy_max_hp=request.enemy_max_hp
    )

    return CombatAdaptResponse(**result)


@app.post("/reward/evaluate", response_model=RewardEvaluateResponse)
def reward_evaluate(request: RewardEvaluateRequest):
    config = load_config()

    if not config.get("reward_evaluator_enabled", True):
        return RewardEvaluateResponse(
            enemy_id=request.enemy_id,
            xp=request.base_xp,
            coins=request.base_coins,
            food=0,
            difficulty_score=1.0,
            explanation="Reward Evaluator Agent este dezactivat în config."
        )

    result = evaluate_reward(request)
    return RewardEvaluateResponse(**result)


# ---------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    cfg = load_config()

    host = cfg.get("server_host", "127.0.0.1")
    port = int(cfg.get("server_port", 8765))

    print("=== Order of the Dragon AI Server ===")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Config: {CONFIG_FILE}")
    print(f"Server: http://{host}:{port}")
    print()

    uvicorn.run(app, host=host, port=port)