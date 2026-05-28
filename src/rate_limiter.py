import threading
import json
import os
from datetime import date

_lock = threading.Lock()
_STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "rate_limit_state.json")
DAILY_LIMIT = int(os.getenv("DAILY_REQUEST_LIMIT", "20"))


def _load() -> dict:
    try:
        with open(_STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(state: dict) -> None:
    with open(_STATE_FILE, "w") as f:
        json.dump(state, f)


def get_status() -> tuple[int, int]:
    """Returns (current_count, daily_limit) without consuming a slot."""
    today = str(date.today())
    with _lock:
        state = _load()
        count = state.get("count", 0) if state.get("date") == today else 0
        return count, DAILY_LIMIT


def consume_request() -> tuple[bool, int, int]:
    """Atomically check and increment. Returns (allowed, new_count, daily_limit)."""
    today = str(date.today())
    with _lock:
        state = _load()
        if state.get("date") != today:
            state = {"date": today, "count": 0}
        if state["count"] >= DAILY_LIMIT:
            return False, state["count"], DAILY_LIMIT
        state["count"] += 1
        _save(state)
        return True, state["count"], DAILY_LIMIT
