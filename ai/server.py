from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import random
import re
import threading

from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from gpt4all import GPT4All
except Exception:
    GPT4All = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AI_DIR = PROJECT_ROOT / "ai"
DATA_DIR = AI_DIR / "data"
CONFIG_FILE = AI_DIR / "config.json"
RIDDLES_FILE = DATA_DIR / "riddles.json"
ENV_STATE_FILE = DATA_DIR / "environment_state.json"

DEFAULT_CONFIG = {
    "model_path": "ai/models/model.gguf",
    "server_host": "127.0.0.1",
    "server_port": 8765,
    "ai_dialogue_enabled": True,
    "riddle_evaluator_enabled": True,
    "max_tokens": 140,
    "temperature": 0.7,
}

FALLBACK_RIDDLE = {
    "id": "shadow",
    "question": "I follow you by day, but vanish at night. What am I?",
    "answer": "shadow",
    "accepted_answers": ["shadow", "a shadow", "my shadow", "your shadow"],
}

DEFAULT_ENV_STATE = {
    "honor": 0,
    "cruelty": 0,
    "suspicion": 0,
    "world_tension": 0,
    "commoner_trust": 0,
    "events_seen": 0,
    "last_event": None,
}

app = FastAPI(title="Order of the Dragon AI Server")
_model = None
_model_error: Optional[str] = None
_model_lock = threading.Lock()


def load_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    config = dict(DEFAULT_CONFIG)
    config.update(loaded)
    return config


def project_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def get_model():
    global _model, _model_error
    if _model is not None:
        return _model
    if GPT4All is None:
        _model_error = "gpt4all nu poate fi importat."
        return None

    config = load_config()
    path = project_path(config["model_path"])
    if not path.exists():
        _model_error = "Modelul local nu există: %s" % path
        return None

    try:
        _model = GPT4All(model_name=path.name, model_path=str(path.parent), allow_download=False)
        _model_error = None
        return _model
    except Exception as exc:
        _model_error = str(exc)
        return None


def clean_text(text: str) -> str:
    text = (text or "").strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "The wind has stolen my words."
    return " ".join(lines[:2])[:800]


def normalize_answer(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9 ]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except Exception:
        return None


def load_riddles() -> List[Dict[str, Any]]:
    if RIDDLES_FILE.exists():
        try:
            with open(RIDDLES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data
        except Exception:
            pass
    return [dict(FALLBACK_RIDDLE)]


def find_riddle(riddle_id: str) -> Dict[str, Any]:
    for riddle in load_riddles():
        if riddle.get("id") == riddle_id:
            return riddle
    return dict(FALLBACK_RIDDLE)


def direct_match(riddle: Dict[str, Any], player_answer: str) -> bool:
    answer = normalize_answer(player_answer)
    accepted = [normalize_answer(x) for x in riddle.get("accepted_answers", [])]
    accepted.append(normalize_answer(riddle.get("answer", "")))
    return answer in [x for x in accepted if x]


def clamp(value: int, minimum: int = -100, maximum: int = 100) -> int:
    return max(minimum, min(maximum, int(value)))


def load_environment_state() -> Dict[str, Any]:
    if ENV_STATE_FILE.exists():
        try:
            with open(ENV_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            state = {}
    else:
        state = {}

    merged = dict(DEFAULT_ENV_STATE)
    merged.update(state)
    return merged


def save_environment_state(state: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ENV_STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def environment_tone(state: Dict[str, Any]) -> str:
    if state.get("cruelty", 0) >= 50:
        return "frightened"
    if state.get("suspicion", 0) >= 45:
        return "suspicious"
    if state.get("honor", 0) >= 35 and state.get("commoner_trust", 0) >= 25:
        return "respectful"
    return "neutral"


def spawn_modifier(state: Dict[str, Any]) -> str:
    if state.get("world_tension", 0) >= 55 or state.get("cruelty", 0) >= 55:
        return "more_guards"
    if state.get("world_tension", 0) <= -20:
        return "calmer_roads"
    return "normal"


class DialogueRequest(BaseModel):
    npc_id: str
    location: str = ""
    player_message: str = ""
    context: Dict[str, Any] = Field(default_factory=dict)


class RiddleEvaluateRequest(BaseModel):
    riddle_id: str
    question: str = ""
    answer: str = ""
    accepted_answers: List[str] = Field(default_factory=list)
    player_answer: str
    context: Dict[str, Any] = Field(default_factory=dict)


class EnvironmentEventRequest(BaseModel):
    event_type: str
    data: Dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health():
    config = load_config()
    path = project_path(config["model_path"])
    return {
        "status": "ok",
        "service": "order_of_the_dragon_ai",
        "model_path": str(path),
        "model_exists": path.exists(),
        "gpt4all_imported": GPT4All is not None,
        "model_loaded": _model is not None,
        "model_error": _model_error,
    }


@app.post("/dialogue")
def dialogue(request: DialogueRequest):
    model = get_model()
    if model is None:
        return {"npc_id": request.npc_id, "reply": "The fields keep their secrets, traveler.", "used_model": False, "error": _model_error}

    prompt = (
        "You are a secondary NPC in a historical fantasy game. "
        "Answer in the same language as the player's message. Keep it short. "
        "Do not invent rewards, items, locations, or quests.\n\n"
        f"NPC: {request.npc_id}\nLocation: {request.location}\n"
        f"Context: {json.dumps(request.context, ensure_ascii=False)}\n"
        f"Player: {request.player_message}\nNPC:"
    )
    try:
        with _model_lock:
            raw = model.generate(prompt, max_tokens=int(load_config().get("max_tokens", 140)), temp=float(load_config().get("temperature", 0.7)))
        return {"npc_id": request.npc_id, "reply": clean_text(raw), "used_model": True}
    except Exception as exc:
        return {"npc_id": request.npc_id, "reply": "The fields keep their secrets, traveler.", "used_model": False, "error": str(exc)}


@app.get("/riddle/random")
def riddle_random():
    riddle = random.choice(load_riddles())
    return {
        "id": riddle.get("id"),
        "question": riddle.get("question"),
        "answer": riddle.get("answer"),
        "accepted_answers": riddle.get("accepted_answers", []),
    }


@app.post("/riddle/evaluate")
def riddle_evaluate(request: RiddleEvaluateRequest):
    riddle = find_riddle(request.riddle_id)
    if request.question:
        riddle["question"] = request.question
    if request.answer:
        riddle["answer"] = request.answer
    if request.accepted_answers:
        riddle["accepted_answers"] = request.accepted_answers

    direct = direct_match(riddle, request.player_answer)
    used_model = False
    model_correct = False
    farewell = "The field has heard enough. Walk on, traveler."
    error = None

    model = get_model()
    if model is not None and load_config().get("riddle_evaluator_enabled", True):
        prompt = (
            "You evaluate a riddle answer. Return ONLY JSON with keys correct and farewell. "
            "correct must be true or false. farewell must be one short mysterious English sentence.\n\n"
            f"Riddle: {riddle.get('question')}\n"
            f"Correct answer: {riddle.get('answer')}\n"
            f"Accepted answers: {riddle.get('accepted_answers', [])}\n"
            f"Player answer: {request.player_answer}\n"
            "JSON:"
        )
        try:
            with _model_lock:
                raw = model.generate(prompt, max_tokens=100, temp=0.2)
            parsed = extract_json(raw)
            if parsed:
                used_model = True
                model_correct = bool(parsed.get("correct", False))
                farewell = clean_text(str(parsed.get("farewell") or farewell))
        except Exception as exc:
            error = str(exc)
    else:
        error = _model_error

    correct = bool(direct or model_correct)
    if correct and farewell == "The field has heard enough. Walk on, traveler.":
        farewell = "A clear answer cuts through fog; take what the road offers."
    if not correct and farewell == "The field has heard enough. Walk on, traveler.":
        farewell = "Not every seed grows into truth; perhaps another road will teach you."

    return {
        "riddle_id": riddle.get("id"),
        "correct": correct,
        "farewell": farewell,
        "used_model": used_model,
        "direct_match": direct,
        "error": error,
    }


@app.post("/environment/update")
def environment_update(request: EnvironmentEventRequest):
    state = load_environment_state()

    def add(key: str, amount: int):
        state[key] = clamp(state.get(key, 0) + amount)

    if request.event_type == "solved_riddle":
        add("honor", 4)
        add("commoner_trust", 3)
    elif request.event_type == "failed_riddle":
        add("suspicion", 1)
    elif request.event_type == "returned_valuable":
        add("honor", 18)
        add("commoner_trust", 15)
        add("world_tension", -3)
    elif request.event_type == "promise_kept":
        add("honor", 15)
        add("commoner_trust", 10)
    elif request.event_type == "promise_broken":
        add("honor", -20)
        add("suspicion", 15)
        add("commoner_trust", -12)
    else:
        add("suspicion", 1)

    state["events_seen"] = int(state.get("events_seen", 0)) + 1
    state["last_event"] = {"type": request.event_type, "data": request.data}
    save_environment_state(state)

    return {
        "state": state,
        "npc_tone": environment_tone(state),
        "spawn_modifier": spawn_modifier(state),
        "explanation": "Environment Director processed event: %s" % request.event_type,
    }


@app.get("/environment/state")
def environment_state():
    state = load_environment_state()
    return {"state": state, "npc_tone": environment_tone(state), "spawn_modifier": spawn_modifier(state)}


if __name__ == "__main__":
    import uvicorn
    cfg = load_config()
    uvicorn.run(app, host=cfg.get("server_host", "127.0.0.1"), port=int(cfg.get("server_port", 8765)))