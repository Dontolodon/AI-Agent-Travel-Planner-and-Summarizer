import os
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # /app
load_dotenv(os.path.join(BASE_DIR, "config", ".env"))

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

DEFAULT_OPTIONS = {
    "temperature": 0.35,
    "top_p": 0.9,
    "num_predict": 420,
    "num_ctx": 4096,
}

def call_llm(system_prompt: str, user_prompt: str, *, num_predict: int | None = None) -> str:
    url = f"{OLLAMA_HOST}/api/chat"
    options = dict(DEFAULT_OPTIONS)
    if num_predict is not None:
        options["num_predict"] = int(num_predict)

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": options,
    }

    try:
        resp = requests.post(url, json=payload, timeout=(10, 1200))  # 20 min read timeout
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "") or ""
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Cannot reach Ollama at {OLLAMA_HOST}. "
            f"Check podman network + ollama container name. Original: {e}"
        )
