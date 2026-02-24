import os
import json
from datetime import datetime

HISTORY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "history_trip.json",  # <-- matches what you expect
)


def _load_history_file() -> dict:
    if not os.path.exists(HISTORY_PATH):
        return {}
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_history_file(data: dict) -> None:
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _normalize_user_key(user_name: str) -> str:
    k = (user_name or "").strip()
    if not k:
        return "anonymous"
    k = " ".join(k.split())
    return k.lower()


def load_trip_history(user_name: str):
    data = _load_history_file()
    return data.get(_normalize_user_key(user_name), [])


def append_trip_history(user_name: str, city: str, start_date: str, days: int, short_notes: str):
    data = _load_history_file()
    key = _normalize_user_key(user_name)
    history = data.get(key, [])

    history.append(
        {
            "user_name": (user_name or "").strip() or "Anonymous",
            "city": city,
            "start_date": start_date,
            "days": days,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "short_notes": (short_notes or "")[:200],
        }
    )

    if len(history) > 20:
        history = history[-20:]

    data[key] = history
    _save_history_file(data)
