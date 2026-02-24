import os
import json
import time
from typing import Any

CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache.json")

def _load() -> dict:
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save(data: dict) -> None:
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cache_get(key: str, max_age_seconds: int) -> Any | None:
    data = _load()
    item = data.get(key)
    if not item:
        return None
    ts = item.get("ts", 0)
    if time.time() - ts > max_age_seconds:
        return None
    return item.get("value")

def cache_set(key: str, value: Any) -> None:
    data = _load()
    data[key] = {"ts": time.time(), "value": value}
    _save(data)
