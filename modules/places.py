import os
import requests
from typing import Optional
from dotenv import load_dotenv
from modules.cache import cache_get, cache_set

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # /app
load_dotenv(os.path.join(BASE_DIR, "config", ".env"))

PLACES_KEY = os.getenv("PLACES_API_KEY")
TEXTSEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

def search_attractions(city: str, limit: int = 8, query: Optional[str] = None):
    if not PLACES_KEY:
        raise RuntimeError("PLACES_API_KEY not set in config/.env")

    if query is None:
        query = f"{city} top attractions"

    cache_key = f"places:textsearch:{query}:{limit}"
    cached = cache_get(cache_key, max_age_seconds=24 * 3600)
    if cached:
        return cached

    resp = requests.get(TEXTSEARCH_URL, params={"query": query, "key": PLACES_KEY}, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])[:limit]
    simplified = []
    for r in results:
        simplified.append({
            "name": r.get("name"),
            "rating": r.get("rating"),
            "address": r.get("formatted_address"),
            "place_id": r.get("place_id"),
            "photos": r.get("photos", []),
        })

    cache_set(cache_key, simplified)
    return simplified
